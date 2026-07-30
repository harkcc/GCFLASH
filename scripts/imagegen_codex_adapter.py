#!/usr/bin/env python3
"""Codex image-generation backend adapter for the G1 reference-generation workflow.

Contract (SPEC G1 §6)::

    generate(prompt, image_paths, out_png, timeout_s=300) -> dict  # candidate_meta

Wiring, verified on this host 2026-07-30 with codex-cli 0.144.4:

- ``codex exec --json --skip-git-repo-check -C <workdir> -i <img>... `` with the
  prompt on stdin. Image generation requires ``[features] image_generation =
  true`` in ``$CODEX_HOME/config.toml`` (already set here).
- The first JSONL event is ``{"type":"thread.started","thread_id":"<uuid>"}``.
  The generated PNG lands in ``$CODEX_HOME/generated_images/<thread_id>/``.
  The FILENAME IS NOT STABLE: both ``call_<call_id>.png`` and
  ``exec-<uuid>.png`` were observed on 2026-07-30, minutes apart. Never match
  on filename — scan the thread directory and take the newest PNG.
- The image-generation tool call does NOT surface as an ``item.*`` event, so the
  output is located by scanning the thread directory, not by parsing events.

Adapter responsibilities and nothing else (R2 — no cropping, masking, or
compositing ever): invoke the backend, retrieve the PNG, whole-image resample to
the requested long edge, record before/after sizes, write ``candidate_meta.json``.

Aspect-ratio note: resampling preserves aspect ratio (long edge -> ``output_px``).
A backend image whose aspect does not match the requested canvas is NOT squeezed
or cropped into it; that is what the RECOMPOSE round exists for (R5). The meta
reports the measured aspect so the runner can decide.

Standalone use (P0 replication smoke, SPEC §10.1)::

    python scripts/imagegen_codex_adapter.py \
        --prompt-file /tmp/a1_prompt.txt \
        --image /abs/vacuum-sealer-product-source.jpg \
        --image /abs/r2-warm-chef.jpg \
        --out artifacts/g1_p0_smoke/candidate.png \
        --output-px 0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

from PIL import Image

CODEX_HOME = pathlib.Path(os.environ.get("CODEX_HOME") or (pathlib.Path.home() / ".codex"))
GENERATED_ROOT = CODEX_HOME / "generated_images"

# Mechanical wrapper around the compiled design prompt.
#
# INVARIANT (asserted by tests): this wrapper carries ZERO visual instruction.
# It only tells the agent which tool to call and forbids it from paraphrasing.
# Every word that can influence what the image looks like must come from the
# compiled six-section prompt (R13). Do not add art direction here.
WRAPPER_TEMPLATE = """Generate exactly one image using your image generation tool.

Pass these reference image paths to the tool, in this order:
{image_path_lines}

Use the instruction block below as the image prompt verbatim. Do not edit,
shorten, extend, rephrase, or reinterpret it, and do not add any detail of your
own. Do not write or run code, do not look for skills or documentation, and do
not copy, move, rename, or post-process the result. Call the tool once, then
stop and reply with the absolute path of the generated file.

=== IMAGE PROMPT (verbatim) ===
{prompt}
=== END IMAGE PROMPT ==="""


def _sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _image_size(path: pathlib.Path) -> list[int]:
    # Context-managed: a bare Image.open(...).size leaks one descriptor per input
    # image per round, and a job is 9 rounds x up to 4 images.
    with Image.open(path) as im:
        return list(im.size)


def _backend_id() -> str:
    try:
        out = subprocess.run(["codex", "--version"], capture_output=True, text=True,
                             timeout=30)
        return out.stdout.strip() or "codex-cli(unknown)"
    except Exception:
        return "codex-cli(unavailable)"


def _thread_id_from_events(stdout: str) -> str | None:
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "thread.started" and ev.get("thread_id"):
            return str(ev["thread_id"])
    return None


def _agent_errors(stdout: str) -> list[str]:
    msgs = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = ev.get("item") or {}
        if item.get("type") == "error" and item.get("message"):
            msgs.append(str(item["message"]))
    return msgs


def _find_generated_png(thread_id: str | None, started_at: float) -> pathlib.Path | None:
    """Locate the PNG the backend just produced.

    Primary: the thread's own directory. Fallback: any PNG under
    generated_images created after the call started (covers a backend that
    changes its directory convention).
    """
    candidates: list[pathlib.Path] = []
    if thread_id:
        thread_dir = GENERATED_ROOT / thread_id
        if thread_dir.is_dir():
            candidates = sorted(thread_dir.glob("*.png"),
                                key=lambda p: p.stat().st_mtime)
    if not candidates and GENERATED_ROOT.is_dir():
        candidates = sorted(
            (p for p in GENERATED_ROOT.glob("*/*.png")
             if p.stat().st_mtime >= started_at - 1),
            key=lambda p: p.stat().st_mtime,
        )
    return candidates[-1] if candidates else None


def _resample(src: pathlib.Path, out_png: pathlib.Path, output_px: int) -> dict:
    """Whole-image resample only. Never crops, never changes aspect ratio."""
    out_png.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        src_w, src_h = im.size
        long_edge = max(src_w, src_h)
        if output_px and long_edge != output_px:
            scale = output_px / long_edge
            new_size = (max(1, round(src_w * scale)), max(1, round(src_h * scale)))
            im = im.convert("RGB") if im.mode not in ("RGB", "RGBA") else im
            im = im.resize(new_size, Image.LANCZOS)
            im.save(out_png, "PNG")
            resampled = True
        else:
            shutil.copy2(src, out_png)
            new_size = (src_w, src_h)
            resampled = False
    return {
        "backend_size": [src_w, src_h],
        "final_size": list(new_size),
        "resampled": resampled,
        "aspect_ratio": round(new_size[0] / new_size[1], 4),
    }


def generate(prompt: str, image_paths: list[str], out_png: str,
             timeout_s: int = 300, *, output_px: int = 1600,
             workdir: str | None = None, model: str | None = None,
             retries: int = 2, meta_path: str | None = None) -> dict:
    """Generate one image. Returns candidate_meta; raises RuntimeError on failure.

    ``retries`` is the number of ADDITIONAL attempts after the first (SPEC §6:
    "same parameters, at most 2 retries").
    """
    out = pathlib.Path(out_png).resolve()
    imgs = [pathlib.Path(p).resolve() for p in image_paths]
    missing = [str(p) for p in imgs if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"input image(s) not found: {missing}")

    wrapped = WRAPPER_TEMPLATE.format(
        image_path_lines="\n".join(f"{i}. {p}" for i, p in enumerate(imgs, 1)),
        prompt=prompt,
    )
    cwd = workdir or str(out.parent if out.parent.exists() else pathlib.Path.cwd())
    pathlib.Path(cwd).mkdir(parents=True, exist_ok=True)

    cmd = ["codex", "exec", "--json", "--skip-git-repo-check", "-C", cwd]
    if model:
        cmd += ["-m", model]
    for p in imgs:
        cmd += ["-i", str(p)]

    attempts: list[dict] = []
    for attempt in range(retries + 1):
        started = time.time()
        try:
            proc = subprocess.run(cmd, input=wrapped, capture_output=True,
                                  text=True, timeout=timeout_s)
            rc, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            rc, timed_out = -1, True
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        elapsed = round(time.time() - started, 2)

        thread_id = _thread_id_from_events(stdout)
        src = _find_generated_png(thread_id, started) if not timed_out else None
        record = {
            "attempt": attempt + 1,
            "returncode": rc,
            "timed_out": timed_out,
            "elapsed_s": elapsed,
            "thread_id": thread_id,
            "source_png": str(src) if src else None,
            "agent_errors": _agent_errors(stdout),
            "stderr_tail": stderr[-1500:] if stderr else "",
        }
        attempts.append(record)

        if src is not None:
            size_meta = _resample(src, out, output_px)
            meta = {
                "backend": "codex_exec_imagegen",
                "backend_id": _backend_id(),
                "model": model or "config_default",
                "thread_id": thread_id,
                "source_png": str(src),
                "candidate_png": str(out),
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "prompt_chars": len(prompt),
                "input_images": [
                    {"path": str(p), "sha256": _sha256(p),
                     "size": _image_size(p)} for p in imgs
                ],
                "requested_output_px": output_px,
                "elapsed_s": elapsed,
                "attempts": attempts,
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                **size_meta,
            }
            mp = pathlib.Path(meta_path) if meta_path else out.parent / "candidate_meta.json"
            mp.parent.mkdir(parents=True, exist_ok=True)
            mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
            meta["meta_path"] = str(mp)
            return meta

        if attempt < retries:
            print(f"  [imagegen] attempt {attempt + 1} produced no image; retrying...",
                  file=sys.stderr, flush=True)

    raise RuntimeError(
        "codex imagegen produced no PNG after "
        f"{retries + 1} attempt(s):\n{json.dumps(attempts, ensure_ascii=False, indent=2)}"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Codex image-generation adapter (G1 §6)")
    ap.add_argument("--prompt-file", required=True, type=pathlib.Path)
    ap.add_argument("--image", action="append", default=[], metavar="PATH",
                    help="reference image, repeatable; order matches prompt ordinals")
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--output-px", type=int, default=1600,
                    help="long-edge target; 0 = keep backend resolution")
    ap.add_argument("--timeout-s", type=int, default=600)
    ap.add_argument("--model", default=None)
    ap.add_argument("--retries", type=int, default=2)
    args = ap.parse_args()

    if not args.image:
        ap.error("at least one --image is required")

    prompt = args.prompt_file.read_text(encoding="utf-8")
    meta = generate(prompt, args.image, str(args.out), timeout_s=args.timeout_s,
                    output_px=args.output_px, model=args.model, retries=args.retries)
    print(json.dumps({k: v for k, v in meta.items() if k != "attempts"},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
