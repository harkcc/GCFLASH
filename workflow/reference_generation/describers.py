#!/usr/bin/env python3
"""The three -- and only three -- LLM nodes of the G1 workflow (SPEC §3).

| node                 | produces                        |
|----------------------|---------------------------------|
| design briefer       | reference_design_brief.json     |
| appearance describer | immutable_traits.json           |
| repair judge         | judge_decision.json             |

Every node is a single call with a JSON Schema pinned via ``--output-schema``.
No node may loop, call tools, or emit prose. Everything else in the workflow is
deterministic code.

Provider seam (SPEC §6: "codex exec 多模态调用（或 Claude API，二选一，实现处
留 provider 参数）"): ``provider="codex"`` is implemented; ``provider="claude"``
raises until someone wires it, rather than silently falling back.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import tempfile

SCHEMA_DIR = pathlib.Path(__file__).resolve().parent / "schemas"
SCHEMA_TRAITS = SCHEMA_DIR / "immutable_traits.schema.json"
SCHEMA_BRIEF = SCHEMA_DIR / "reference_design_brief.schema.json"
SCHEMA_JUDGE = SCHEMA_DIR / "judge_decision.schema.json"

# SPEC §11 stop condition 3.
MAX_SCHEMA_FAILURES = 3


class SchemaFailure(RuntimeError):
    """The node could not produce schema-valid JSON within the allowed attempts.

    Carries the raw samples so the stop-condition report can quote them.
    """

    def __init__(self, node: str, samples: list[str]):
        self.node = node
        self.samples = samples
        preview = "\n---\n".join(s[:800] for s in samples)
        super().__init__(
            f"{node}: no schema-valid JSON in {len(samples)} attempt(s) "
            f"(SPEC §11 stop condition 3). Raw samples:\n{preview}")


def _extract_json(text: str) -> dict:
    """Parse the model's last message, tolerating a ```json fence."""
    text = (text or "").strip()
    if not text:
        raise ValueError("empty response")
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise


def _codex_json(prompt: str, image_paths: list[str], schema: pathlib.Path,
                *, timeout_s: int, model: str | None,
                reasoning_effort: str | None, node: str) -> dict:
    """One schema-constrained multimodal codex call, retried on schema failure."""
    samples: list[str] = []
    for _ in range(MAX_SCHEMA_FAILURES):
        with tempfile.TemporaryDirectory() as td:
            last = pathlib.Path(td) / "last.txt"
            cmd = ["codex", "exec", "--skip-git-repo-check",
                   "--output-schema", str(schema), "-o", str(last), "-C", td]
            if model:
                cmd += ["-m", model]
            if reasoning_effort:
                cmd += ["-c", f"model_reasoning_effort={reasoning_effort}"]
            for p in image_paths:
                cmd += ["-i", str(p)]
            try:
                proc = subprocess.run(cmd, input=prompt, capture_output=True,
                                      text=True, timeout=timeout_s)
            except subprocess.TimeoutExpired:
                samples.append(f"<timeout after {timeout_s}s>")
                continue
            raw = last.read_text(encoding="utf-8") if last.is_file() else proc.stdout
            if raw.strip():
                samples.append(raw)
            else:
                # An empty last-message is almost always the API rejecting the
                # schema (e.g. strict mode requires every property in
                # 'required'). That reason only appears on stderr/stdout, so
                # record it -- otherwise the failure looks like an empty sample
                # and is undiagnosable.
                samples.append(
                    f"<no last message; rc={proc.returncode}>\n"
                    f"STDERR:\n{(proc.stderr or '')[-2000:]}\n"
                    f"STDOUT:\n{(proc.stdout or '')[-2000:]}")
                continue
            try:
                return _extract_json(raw)
            except (ValueError, json.JSONDecodeError):
                continue
    raise SchemaFailure(node, samples)


def _call(prompt: str, image_paths: list[str], schema: pathlib.Path, *,
          provider: str, timeout_s: int, model: str | None,
          reasoning_effort: str | None, node: str) -> dict:
    if provider == "codex":
        return _codex_json(prompt, image_paths, schema, timeout_s=timeout_s,
                           model=model, reasoning_effort=reasoning_effort, node=node)
    if provider == "claude":
        raise NotImplementedError(
            "provider='claude' is a declared seam (SPEC §6) but is not wired yet; "
            "use provider='codex' or implement the Claude path explicitly")
    raise ValueError(f"unknown provider {provider!r}; expected 'codex' or 'claude'")


# --------------------------------------------------------------------------- #
# node 1: appearance describer
# --------------------------------------------------------------------------- #

TRAITS_PROMPT = """You are extracting the IMMUTABLE APPEARANCE of one product from the attached image(s), so that a downstream image generator can be forbidden from redesigning it.

The attached image(s) show the real product{multi_note}.

Produce short, concrete visual phrases naming what must never change: body colour and material, silhouette, control panel and its controls, distinctive hardware, and overall proportions. The downstream prompt will literally say "keep the exact <your phrases>", so each phrase must read naturally in that sentence.

Rules:
- Describe ONLY the product itself. No background, no scene, no lighting, no marketing language.
- Do not state any performance number, capability, or claim, even if printed on the image.
- List accessories only if they are actually visible. Never guess at accessories.
- For native_product_text, transcribe only markings you can actually read on the product body.

Product context (operator-supplied, may be in another language): {context}

Output JSON matching the schema exactly, with no extra commentary."""


def describe_immutable_traits(product_images: list[str], *, context: str = "",
                             provider: str = "codex", timeout_s: int = 300,
                             model: str | None = None,
                             reasoning_effort: str | None = None) -> dict:
    """§5.1 immutable_traits.json -- the first product-stability mechanism."""
    if not product_images:
        raise ValueError("describe_immutable_traits needs at least one image")
    multi = (" from several angles or with its accessories"
             if len(product_images) > 1 else "")
    prompt = TRAITS_PROMPT.format(multi_note=multi, context=context.strip() or "(none)")
    out = _call(prompt, product_images, SCHEMA_TRAITS, provider=provider,
                timeout_s=timeout_s, model=model, reasoning_effort=reasoning_effort,
                node="appearance_describer")
    out.setdefault("accessories", [])
    out.setdefault("native_product_text", [])
    return out


# --------------------------------------------------------------------------- #
# node 2: design briefer
# --------------------------------------------------------------------------- #

BRIEF_PROMPT = """You are decomposing a competitor's e-commerce main image so its DESIGN GRAMMAR can be reused for a different product and a different brand.

The attached image is the design reference. We will copy its structure, hierarchy, and mood. We will NOT copy its product, its brand, its language, or any of its claims.

Two jobs, both required:

1. Describe the reusable design: aspect ratio, layout skeleton, functional modules and where they sit, colour mood, and the compositional/photographic mechanics worth reproducing. Name modules by FUNCTION (headline_block, spec_badges, offer_block, product_stage, person), never by donor content. Keep the donor's brand name and donor-language text OUT of these fields -- they are wired straight into our generation prompt.

2. Transcribe, into visible_claims_on_reference, every marketing claim legible on the reference: warranty periods, gift/bonus offers, percentages, certifications, spec numbers. These are unverified for our product and the pipeline must strip or replace all of them. Missing one means it can leak into our image.

Also report donor_brand and donor_language so they can be explicitly banned.

Our product, for context only -- do not describe it, and do not let it influence the layout you report: {context}

Output JSON matching the schema exactly, with no extra commentary."""


def describe_reference_design(reference_image: str, *, context: str = "",
                              provider: str = "codex", timeout_s: int = 300,
                              model: str | None = None,
                              reasoning_effort: str | None = None) -> dict:
    """§5.1 reference_design_brief.json -- half of "how to borrow the reference".

    The other half is attaching the reference image itself as design master: text
    alone loses the design detail, the image alone leaves "imitate what?"
    unconstrained. Both are required.
    """
    prompt = BRIEF_PROMPT.format(context=context.strip() or "(not supplied)")
    out = _call(prompt, [reference_image], SCHEMA_BRIEF, provider=provider,
                timeout_s=timeout_s, model=model, reasoning_effort=reasoning_effort,
                node="design_briefer")
    for key in ("donor_brand", "donor_language"):
        out.setdefault(key, "")
    out.setdefault("visible_claims_on_reference", [])
    out.setdefault("modules", [])
    return out


# --------------------------------------------------------------------------- #
# node 3: repair judge
# --------------------------------------------------------------------------- #

JUDGE_PROMPT = """You are reviewing one round of an e-commerce main-image generation loop and choosing the single next repair.

Attached images: (1) the CURRENT CANDIDATE under review, (2) the DESIGN REFERENCE it should resemble structurally.

The locked fact list -- the only marketing copy allowed in the image:
{facts}

Text printed on the product body itself is exempt from that list and must NOT be
reported as an error: {native_text}

The product's immutable appearance traits:
{traits}

Rounds used: {used} of {budget}.

Repair menu -- choose EXACTLY ONE:
{menu}

How to choose: name the single biggest thing standing between this candidate and a
high-converting marketplace main image. One variable per round; do not bundle fixes.
If the candidate is already good enough that another round risks harming it, still
choose the least-harmful repair but set stop_recommended to true.

Constraints on your output:
- prompt_delta describes ONLY your chosen repair, as an instruction to an image
  editor. The pipeline appends the copy whitelist, the negative constraints, and
  the product traits itself -- do not repeat them, and never write a full prompt.
- Do not propose any new visual reference or extra image.
- Do not restate or edit the locked fact list.
- Report a fact_violation only where the candidate's text contradicts the locked
  fact list above.
- product_integrity_ok is about the product's own shape/colour/panel/hardware or
  cropping only -- not about layout, scene, or typography.

Output JSON matching the schema exactly, with no extra commentary."""


def judge_candidate(candidate_png: str, reference_image: str, *, facts: dict,
                    traits: dict, repairs_used: int, round_budget: int,
                    provider: str = "codex", timeout_s: int = 300,
                    model: str | None = None,
                    reasoning_effort: str | None = None) -> dict:
    """§7 repair judge. V1 uses this as a PREFILL only -- a human confirms (R10)."""
    from . import contracts as C

    facts_lines = "\n".join(
        f"- {s.get('slot')}: {s.get('text')}" for s in facts.get("copy_slots") or [])
    native = ", ".join(facts.get("native_product_text") or []) or "(none recorded)"
    traits_lines = ", ".join(traits.get("product_visual_traits") or [])
    menu_lines = "\n".join(f"- {k}" for k in C.REPAIR_MENU)

    prompt = JUDGE_PROMPT.format(
        facts=facts_lines, native_text=native, traits=traits_lines,
        used=repairs_used, budget=round_budget, menu=menu_lines)
    out = _call(prompt, [candidate_png, reference_image], SCHEMA_JUDGE,
                provider=provider, timeout_s=timeout_s, model=model,
                reasoning_effort=reasoning_effort, node="repair_judge")

    # R8: the judge is constrained by code, not just by prompt wording.
    if out.get("repair") not in C.REPAIR_MENU:
        raise SchemaFailure("repair_judge",
                            [json.dumps(out, ensure_ascii=False)])
    out.setdefault("fact_violations", [])
    out.setdefault("product_integrity_ok", True)
    out.setdefault("stop_recommended", False)
    return out
