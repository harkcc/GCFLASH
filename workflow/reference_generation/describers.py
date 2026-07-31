#!/usr/bin/env python3
"""The four LLM nodes of the G1 workflow (SPEC §3).

| node                 | produces                        | sees images |
|----------------------|---------------------------------|-------------|
| design briefer       | reference_design_brief.json     | reference   |
| appearance describer | immutable_traits.json           | product     |
| copy compiler        | locked_fact_list draft          | none        |
| repair judge         | judge_decision.json             | candidate   |

The copy compiler is deliberately BLIND: it never sees the reference image, so
it cannot copy the donor's claims. Its only source is the operator's product
information.

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
SCHEMA_COPY = SCHEMA_DIR / "copy_slots.schema.json"

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
# node 4: copy compiler
# --------------------------------------------------------------------------- #

COPY_PROMPT = """You are writing the marketing copy for ONE e-commerce main product image.

Product information supplied by the operator (this is the only source of truth
about the product; it is usually the marketplace listing title plus notes):

{product_info}

Additional confirmed facts:
{facts}

Target language: {language}

Your job, in order:

1. DECIDE WHAT GOES ON. A main image must NOT carry every fact. Pick the few
   lines that make someone stop scrolling and understand the product. Everything
   you leave off, list in "dropped" so a human can overrule you.
2. THE HEADLINE NAMES THE PRODUCT. A shopper scanning a results grid must
   recognise WHAT THIS IS before anything else, so the headline is the product's
   category name in the target language. Do not spend the headline on a
   specification, and never repeat there a figure that already has its own slot.
3. ASSIGN VISUAL WEIGHT. The slot you choose IS the type size and position:
   headline is the biggest words on the image, badge is the small highlighted
   chip, spec_primary/spec_secondary are the two numeric callouts, offer is the
   included-items block, feature/feature_optional are small bottom lines. Put the
   single most compelling thing in headline.
4. WRITE IT IN {language}. Correct spelling, correct diacritics. Marketplace
   headline style: short, punchy, works in uppercase, no sentence punctuation.

Hard rules:

- Every line must trace to the product information above. Quote the source for
  each one. If you cannot trace it, do not write it.
- NEVER invent or adjust a number. Every figure you print must appear in the
  product information exactly as given. Do not round, convert, or "improve" a
  specification. A wrong number is the single most damaging error you can make
  here, because this list is then frozen and repeated on every subsequent round.
- DO normalise how a figure is typeset, without changing its value. Listing
  titles are written carelessly; printed copy must not be. Restore the
  conventional spacing and capitalisation of the unit: "75kpa" is printed as
  "75 kPa", "120W" as "120 W", "17x20cm" as "17x20 cm". The digits stay
  identical -- you are fixing typography, not the specification.
- Lead with the specification that actually differentiates this product in its
  category, not merely the first one listed. For a vacuum sealer that is the
  suction pressure; for a battery device, capacity; for a lamp, brightness. Put
  the weaker figure in spec_secondary.
- Do not write warranty periods, certifications, testimonials, prices, ratings,
  delivery promises, or any superlative claim that is not stated above.
- Use each slot at most once, and omit any slot you have nothing truthful for.

Output JSON matching the schema exactly, with no extra commentary."""


def compile_copy_slots(*, product_info: str, facts: list[str], language: str,
                       feedback: str = "", provider: str = "codex",
                       timeout_s: int = 300, model: str | None = None,
                       reasoning_effort: str | None = None) -> dict:
    """§5.1 locked_fact_list drafting -- the copy the image will carry.

    Evidence for this node existing at all: in the validated 2026-07-11 run the
    operator supplied only the raw listing title plus "don't put everything on,
    it's a main image" and "output in Romanian". The model itself produced the
    nine-slot Romanian copy list that ended up on the accepted image. Making a
    human author those nine lines by hand was re-doing work the model already
    did well.

    The output is still a DRAFT: a human confirms before it is frozen (R3), and
    ``compile.verify_numbers_traceable`` mechanically checks every figure
    against the truth pack first -- the 2026-07-11 run shipped a wrong "70 kPa"
    into the image because a human typed it, so human authorship is not itself a
    correctness guarantee.
    """
    lang = language.strip()
    if not lang:
        raise ValueError("compile_copy_slots needs a target language")
    fact_lines = "\n".join(f"- {f}" for f in facts if str(f).strip()) or "(none)"
    prompt = COPY_PROMPT.format(
        product_info=(product_info or "").strip() or "(none supplied)",
        facts=fact_lines, language=lang)
    if feedback.strip():
        # Re-draft with the specific defect named, rather than stopping and
        # asking a human to fix what the model can fix itself.
        prompt += ("\n\nYOUR PREVIOUS ATTEMPT WAS REJECTED. Fix exactly this and "
                   "keep everything else:\n" + feedback.strip())
    out = _call(prompt, [], SCHEMA_COPY, provider=provider, timeout_s=timeout_s,
                model=model, reasoning_effort=reasoning_effort,
                node="copy_compiler")
    out.setdefault("copy_slots", [])
    out.setdefault("dropped", [])
    out.setdefault("notes", "")

    seen = set()
    deduped = []
    for s in out["copy_slots"]:
        slot = (s.get("slot") or "").strip()
        if slot and slot not in seen and (s.get("text") or "").strip():
            seen.add(slot)
            deduped.append({"slot": slot, "text": s["text"].strip(),
                            "source": (s.get("source") or "").strip()})
    out["copy_slots"] = deduped
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

These claims are visible on the DESIGN REFERENCE and are unverified for our
product. None may appear on our image in any language. If you see any of them
reproduced, that is a replace_claim_text repair and it outranks cosmetic issues:
{donor_claims}

The target canvas is {canvas}, and the current candidate measures {measured}.
The canvas is fixed by the job contract and is INDEPENDENT of the reference's own
shape (R5). The reference being a different shape is not a defect: our layout is
supposed to be re-distributed into {canvas}. Only choose recompose_aspect if the
candidate itself is NOT {canvas}.

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
                    canvas: str = "1:1", measured_aspect: str = "unknown",
                    donor_claims: list[str] | None = None,
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

    donor = "\n".join(f"- {c}" for c in (donor_claims or [])) or "(none recorded)"
    prompt = JUDGE_PROMPT.format(
        facts=facts_lines, native_text=native, traits=traits_lines,
        used=repairs_used, budget=round_budget, menu=menu_lines,
        canvas=canvas, measured=measured_aspect, donor_claims=donor)
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
