#!/usr/bin/env python3
"""G1 reference-generation workflow runner (SPEC §3, §8 phase P2-P4).

A workflow state machine with a bounded convergence loop -- not a free agent.
Serial execution, artifacts are the audit record, every round gets its own
immutable directory (R12).

Subcommands::

    run             compile + round_00 (+ round_01 recompose if needed)
    status          print the state ledger
    review          run the repair judge on the current candidate (prefill only)
    repair          execute one repair round (human-confirmed)
    approve         accept the current candidate -> converged, store the anchor
    abort           give up -> needs_manual
    style-transfer  single-step transfer of a new reference onto the anchor

Every human decision is written to disk (R10) because those decisions are the
labels a future automatic judge will be calibrated against.

Typical session::

    python scripts/run_reference_generation.py run --request req.json
    python scripts/run_reference_generation.py review --job <job_dir>
    python scripts/run_reference_generation.py repair --job <job_dir> --from-judge
    python scripts/run_reference_generation.py approve --job <job_dir> \
        --module "accessory module"
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import pathlib
import shutil
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from PIL import Image  # noqa: E402

from workflow.reference_generation import compile as G1C  # noqa: E402
from workflow.reference_generation import contracts as C  # noqa: E402
from workflow.reference_generation import describers, templates  # noqa: E402
from workflow.reference_generation.state import (  # noqa: E402
    ROUND_KIND_INITIAL, ROUND_KIND_RECOMPOSE, ROUND_KIND_REPAIR, JobState,
    StateError,
)

sys.path.insert(0, str(REPO / "scripts"))
import imagegen_codex_adapter as backend  # noqa: E402

ASPECT_TOLERANCE = 0.03
COPY_DRAFT_ATTEMPTS = 3  # redraft on an untraceable figure instead of stopping


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def _canvas_ratio(canvas: str) -> float | None:
    """'1:1' -> 1.0, '4:5' -> 0.8. None when unparseable."""
    try:
        w, h = (canvas or "").split(":")
        return float(w) / float(h)
    except (ValueError, ZeroDivisionError):
        return None


def _write_json(path: pathlib.Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _images_from_request(req: dict) -> list[dict]:
    imgs = req.get("product_images") or []
    if not 1 <= len(imgs) <= 3:
        raise ValueError(f"product_images must hold 1-3 entries, got {len(imgs)} (§4.1)")
    for im in imgs:
        role = im.get("role")
        if role not in C.REQUEST_PRODUCT_IMAGE_ROLES:
            raise ValueError(
                f"product_images role {role!r} invalid; allowed: "
                f"{sorted(C.REQUEST_PRODUCT_IMAGE_ROLES)} (§4.1)")
        if not pathlib.Path(im["path"]).is_file():
            raise FileNotFoundError(f"product image missing: {im['path']}")
    n_anchor = sum(1 for im in imgs if im["role"] == C.ROLE_APPEARANCE_ANCHOR)
    if n_anchor != 1:
        raise ValueError(
            f"exactly 1 product_appearance_anchor required, got {n_anchor} (§4.1)")
    return imgs


def _generate_round(st: JobState, rec, prompt: templates.CompiledPrompt,
                    facts: dict, intent: dict, *, timeout_s: int,
                    model: str | None) -> dict | None:
    """Render the prompt, call the backend, persist everything for one round.

    Returns candidate_meta, or None when the backend failed (which does not
    consume budget, §6).
    """
    rd = st.round_dir(rec)
    # Fail loudly on a template regression rather than degrade output silently.
    templates.audit_prompt(prompt, facts)
    (rd / "prompt.md").write_text(prompt.text + "\n", encoding="utf-8")
    _write_json(rd / "inputs.json", {
        "phase": prompt.phase,
        "images": prompt.inputs_manifest(),
        "prompt_sha256": hashlib.sha256(prompt.text.encode()).hexdigest(),
    })

    print(f"  [{rec.dirname}] {prompt.phase}, {len(prompt.images)} image(s), "
          f"calling backend (this takes minutes)...", flush=True)
    try:
        meta = backend.generate(
            prompt.text, prompt.image_paths, str(rd / "candidate.png"),
            timeout_s=timeout_s, output_px=int(intent.get("output_px") or 1600),
            model=model, meta_path=str(rd / "candidate_meta.json"))
    except Exception as exc:  # backend_error: round is free, state unchanged
        _write_json(rd / "backend_error.json",
                    {"error": str(exc)[:4000], "at": _now()})
        st.update_round(rec.index, backend_error=True)
        print(f"  [{rec.dirname}] backend error: {exc}", file=sys.stderr)
        return None

    st.update_round(rec.index, candidate=str(rd / "candidate.png"),
                    prompt_sha256=hashlib.sha256(prompt.text.encode()).hexdigest())
    print(f"  [{rec.dirname}] ok: {meta['final_size']} "
          f"aspect={meta['aspect_ratio']} in {meta['elapsed_s']}s")
    return meta


def _load_compiled(job: pathlib.Path) -> tuple[dict, dict, dict]:
    c = job / "compiled"
    return (G1C.load_json(c / "locked_fact_list.json"),
            G1C.load_json(c / "immutable_traits.json"),
            G1C.load_json(c / "reference_design_brief.json"))


def _brand_and_name(facts: dict, req: dict) -> tuple[str, str]:
    by_slot = {s["slot"]: s["text"] for s in facts.get("copy_slots") or []}
    brand = by_slot.get("brand") or req.get("brand") or ""
    name = (req.get("product_short_name") or by_slot.get("headline") or "product")
    return brand, name


def _record_human(rd: pathlib.Path, decision: str, *, decided_by: str = "human",
                  st: JobState | None = None, round_index: int | None = None,
                  **extra) -> None:
    """R10: every human decision is a label for future judge calibration.

    ``decided_by`` is recorded because those labels are only worth anything if
    they are honestly attributed. A decision made by an operator running an
    acceptance script is not a product owner's taste judgement, and mixing the
    two would quietly poison the calibration set.

    The decision goes to BOTH the round directory and the state ledger; writing
    only the file leaves ``status`` reporting "human=-" for rounds a human
    actually ruled on.
    """
    payload = {"decision": decision, "decided_by": decided_by, "at": _now(),
               **extra}
    _write_json(rd / "human_decision.json", payload)
    if st is not None and round_index is not None:
        st.update_round(round_index, human_decision=payload)


# --------------------------------------------------------------------------- #
# run
# --------------------------------------------------------------------------- #

def cmd_run(args: argparse.Namespace) -> int:
    req = G1C.load_json(args.request)
    intent = req.get("intent") or {}
    canvas = intent.get("canvas") or "1:1"
    product_id = req.get("product_id") or "unknown_product"
    job_id = args.job_id or _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    root = pathlib.Path(args.out_root).expanduser().resolve() / job_id / product_id

    sel = req.get("selected_reference") or {}
    ref_image = sel.get("image")
    if not ref_image or not pathlib.Path(ref_image).is_file():
        raise FileNotFoundError(f"selected_reference.image missing: {ref_image}")
    ref_meta = (G1C.load_json(sel["metadata"])
                if sel.get("metadata") and pathlib.Path(sel["metadata"]).is_file()
                else {})
    product_images = _images_from_request(req)
    truth = G1C.load_json(req["product_truth"])

    st = JobState.create(root, product_id=product_id, job_id=job_id,
                         round_budget=int(req.get("round_budget")
                                          or C.DEFAULT_ROUND_BUDGET),
                         review_mode=req.get("review_mode") or "required",
                         intent=intent)
    _write_json(root / "request" / "generation_request.json", req)
    print(f"job: {root}")

    # ---- compile ---------------------------------------------------------- #
    st.transition(C.S_COMPILING, "compiling frozen inputs")

    # Copy compiler (LLM node). Skipped when the request already carries copy the
    # operator authored or approved.
    request_slots = req.get("copy_slots")
    copy_draft = None
    if not request_slots:
        product_info = (G1C.truth_title(truth) + "\n" + str(
            (truth.get("operator_confirmed") or {}).get("raw_product_info") or ""))
        feedback, attempts = "", []
        # No human gate here: an untraceable figure is a defect the model can fix
        # when told exactly what is wrong, so re-draft instead of stopping.
        for attempt in range(COPY_DRAFT_ATTEMPTS):
            print(f"  compiling target-language copy (LLM node 1/3"
                  f"{f', retry {attempt}' if attempt else ''})...", flush=True)
            copy_draft = describers.compile_copy_slots(
                product_info=product_info, facts=G1C.truth_facts(truth),
                language=intent.get("language") or "", feedback=feedback,
                provider=args.provider, timeout_s=args.describe_timeout,
                model=args.describe_model)
            bad = G1C.verify_numbers_traceable(copy_draft["copy_slots"], truth)
            attempts.append({"attempt": attempt + 1,
                             "slots": copy_draft["copy_slots"],
                             "untraceable": bad})
            if not bad:
                break
            feedback = ("These figures do not appear anywhere in the product "
                        "information, so they cannot be printed. Remove or "
                        "correct the lines carrying them:\n" + "\n".join(
                            f"- {b['slot']}: {b['text']!r} contains {b['number']}"
                            for b in bad))
            print(f"    rejected: untraceable figure(s) "
                  f"{[b['number'] for b in bad]}; redrafting", flush=True)
        else:
            # Still bad after every retry: drop the offending lines rather than
            # blocking the run or printing an unverifiable number.
            bad_slots = {b["slot"] for b in
                         G1C.verify_numbers_traceable(copy_draft["copy_slots"], truth)}
            copy_draft["copy_slots"] = [s for s in copy_draft["copy_slots"]
                                        if s["slot"] not in bad_slots]
            copy_draft.setdefault("dropped", []).extend(
                f"{s} (untraceable figure)" for s in sorted(bad_slots))
            print(f"    dropped unverifiable slot(s): {sorted(bad_slots)}",
                  file=sys.stderr)
        copy_draft["attempts"] = attempts
        request_slots = copy_draft["copy_slots"]
        _write_json(root / "compiled" / "copy_draft.json", copy_draft)
        if not request_slots:
            # Falling through with an empty list would hand compile_locked_fact_list
            # a falsy value, which it reads as "nothing supplied" and answers with
            # the deterministic regex draft -- the raw truth title as headline, in
            # the SOURCE language. Silently freezing a Chinese headline onto a
            # Romanian image is worse than stopping.
            st.transition(C.S_NEEDS_USER_INPUT, "copy compiler produced no usable copy")
            print("STOP: the copy compiler produced no usable copy after "
                  f"{COPY_DRAFT_ATTEMPTS} attempts (see "
                  f"{root / 'compiled' / 'copy_draft.json'}). Supply copy_slots in "
                  f"the request, or fix the product information.", file=sys.stderr)
            return 3

    try:
        facts = G1C.compile_locked_fact_list(
            truth=truth, intent=intent, request_slots=request_slots,
            reference_metadata=ref_meta)
    except G1C.IncompleteTruth as exc:
        _write_json(root / "compiled" / "incomplete_truth.json",
                    {"missing": exc.missing, "at": _now()})
        st.transition(C.S_INCOMPLETE_TRUTH, str(exc))
        print(f"STOP: {exc}", file=sys.stderr)
        return 2

    if copy_draft is not None:
        print("\n  --- drafted copy ---")
        for slot in facts["copy_slots"]:
            print(f"    {slot['slot']:<18} {slot['text']}")
        if copy_draft.get("dropped"):
            print(f"    (left off: {', '.join(copy_draft['dropped'])})")
        if copy_draft.get("notes"):
            print(f"    note: {copy_draft['notes']}")
        print()

    # An untraceable figure is the one failure mode that must never pass
    # silently: once frozen, the copy is repeated verbatim on every round (R3),
    # so a wrong number spoils the whole job rather than one image.
    # Operator-supplied copy is the operator's business; we only refuse to freeze
    # a figure we cannot trace when WE drafted it (handled above). If the request
    # itself carries one, say so loudly and stop -- that is a data error upstream.
    unverified = facts.get("unverified_numbers") or []
    if unverified:
        _write_json(root / "compiled" / "locked_fact_list.draft.json", facts)
        st.transition(C.S_NEEDS_USER_INPUT, "request copy carries untraceable figure(s)")
        print("STOP: copy_slots supplied in the request carry figure(s) absent "
              "from the product information:", file=sys.stderr)
        for u in unverified:
            print(f"  - {u['slot']}: {u['text']!r} -> {u['number']}", file=sys.stderr)
        print("  fix the request or the product information, then rerun.",
              file=sys.stderr)
        return 3

    if args.confirm_copy:
        _write_json(root / "compiled" / "locked_fact_list.draft.json", facts)
        st.transition(C.S_NEEDS_USER_INPUT, "--confirm-copy requested")
        print("STOP (--confirm-copy): review the copy above, then put it in the "
              "request's copy_slots and start a new run.", file=sys.stderr)
        return 3

    anchor_img = next(im for im in product_images
                      if im["role"] == C.ROLE_APPEARANCE_ANCHOR)
    describe_paths = [im["path"] for im in product_images
                      if im["role"] != C.ROLE_NATIVE_TEXT_EVIDENCE]
    print("  compiling immutable traits (LLM node 2/3)...", flush=True)
    traits = describers.describe_immutable_traits(
        describe_paths, context=G1C.truth_title(truth), provider=args.provider,
        timeout_s=args.describe_timeout, model=args.describe_model)
    print("  compiling reference design brief (LLM node 3/3)...", flush=True)
    brief = describers.describe_reference_design(
        ref_image, context=G1C.truth_title(truth), provider=args.provider,
        timeout_s=args.describe_timeout, model=args.describe_model)
    # Measured, not described: the briefer once reported "32:41" for a 736x982
    # reference. This ratio drives the layout-adaptation instruction.
    brief["aspect_ratio"] = G1C.measure_aspect_ratio(ref_image)

    if traits.get("native_product_text") and not facts.get("native_product_text"):
        facts["native_product_text"] = traits["native_product_text"]  # R7
    for claim in brief.get("visible_claims_on_reference") or []:
        if claim not in facts["must_replace_from_reference"]:
            facts["must_replace_from_reference"].append(claim)
    facts = G1C.freeze_fact_list(facts)

    _write_json(root / "compiled" / "locked_fact_list.json", facts)
    _write_json(root / "compiled" / "immutable_traits.json", traits)
    _write_json(root / "compiled" / "reference_design_brief.json", brief)
    _write_json(root / "compiled" / "negative_constraints.json",
                G1C.compile_negative_constraints(brief))

    # ---- round_00 --------------------------------------------------------- #
    st.transition(C.S_GENERATING_INITIAL, "round_00 initial generation")
    brand, short_name = _brand_and_name(facts, req)
    images = [templates.InputImage(C.ROLE_DESIGN_MASTER, ref_image),
              templates.InputImage(C.ROLE_APPEARANCE_ANCHOR, anchor_img["path"])]
    # Attach every remaining request image. §4.1 allows accessories_evidence AND
    # native_text_evidence; dropping either would leave a supplied input unused
    # (and the compiler declares a role clause for each, per R1).
    for im in product_images:
        if im["role"] in (C.ROLE_ACCESSORIES_EVIDENCE, C.ROLE_NATIVE_TEXT_EVIDENCE):
            images.append(templates.InputImage(im["role"], im["path"]))
    prompt = templates.compile_init(images=images, facts=facts, traits=traits,
                                    brief=brief, canvas=canvas, brand=brand,
                                    product_short_name=short_name)
    rec = st.allocate_round(ROUND_KIND_INITIAL)
    meta = _generate_round(st, rec, prompt, facts, intent,
                           timeout_s=args.timeout, model=args.model)
    if meta is None:
        st.transition(C.S_AWAITING_ROUND_REVIEW, "backend error on round_00")
        return 4

    # ---- optional recompose ----------------------------------------------- #
    want = _canvas_ratio(canvas)
    if want and abs(meta["aspect_ratio"] - want) > ASPECT_TOLERANCE:
        print(f"  aspect {meta['aspect_ratio']} != target {want:.4f}; "
              f"adding a recompose round (R5: re-layout, never crop)")
        prev = templates.InputImage(C.ROLE_PREVIOUS_CANVAS,
                                    str(st.latest_candidate()))
        rprompt = templates.compile_recompose(previous=prev, facts=facts,
                                              traits=traits, brief=brief,
                                              canvas=canvas)
        rrec = st.allocate_round(ROUND_KIND_RECOMPOSE)
        _generate_round(st, rrec, rprompt, facts, intent,
                        timeout_s=args.timeout, model=args.model)

    st.transition(C.S_AWAITING_ROUND_REVIEW, "initial generation done")
    print(json.dumps(st.summary(), ensure_ascii=False, indent=2))
    print(f"\nnext: review --job {root}")
    return 0


# --------------------------------------------------------------------------- #
# review (judge prefill)
# --------------------------------------------------------------------------- #

def cmd_review(args: argparse.Namespace) -> int:
    job = pathlib.Path(args.job).expanduser().resolve()
    st = JobState.load(job)
    if st.state != C.S_AWAITING_ROUND_REVIEW:
        print(f"job is in state {st.state}; review expects "
              f"{C.S_AWAITING_ROUND_REVIEW}", file=sys.stderr)
        return 1
    facts, traits, brief = _load_compiled(job)
    req = G1C.load_json(job / "request" / "generation_request.json")
    ref_image = (req.get("selected_reference") or {}).get("image")
    candidate = st.latest_candidate()
    if not candidate or not candidate.is_file():
        print("no candidate image to review", file=sys.stderr)
        return 1

    canvas = (req.get("intent") or {}).get("canvas") or "1:1"
    with Image.open(candidate) as _im:
        cand_ratio = _im.width / _im.height
    measured = f"{cand_ratio:.3f} ({_im.width}x{_im.height})"
    want = _canvas_ratio(canvas)
    on_canvas = want is not None and abs(cand_ratio - want) <= ASPECT_TOLERANCE

    print(f"judging {candidate} ...", flush=True)
    try:
        decision = describers.judge_candidate(
            str(candidate), ref_image, facts=facts, traits=traits,
            canvas=canvas, measured_aspect=measured,
            donor_claims=facts.get("must_replace_from_reference") or [],
            repairs_used=st.repairs_used, round_budget=st.round_budget,
            provider=args.provider, timeout_s=args.describe_timeout,
            model=args.describe_model)
    except describers.SchemaFailure as exc:
        _write_json(job / "judge_schema_failure.json",
                    {"node": exc.node, "samples": exc.samples, "at": _now()})
        print(f"STOP (SPEC §11 condition 3): {exc}", file=sys.stderr)
        return 5

    # R5 is a contract, not a preference: the target canvas is independent of the
    # reference's shape. A judge that has just been shown a 3:4 reference will
    # otherwise propose reshaping a correct 1:1 candidate to match it, which both
    # breaks the contract and burns a repair round.
    contradiction = None
    if decision.get("repair") == "recompose_aspect" and on_canvas:
        contradiction = (
            f"the candidate already measures {measured} and the target canvas is "
            f"{canvas}; recompose_aspect would move it OFF contract (R5)")
        decision["_runner_warning"] = contradiction

    rec = st.rounds[-1]
    _write_json(st.round_dir(rec) / "judge_decision.json", decision)
    st.update_round(rec.index, judge_decision=decision)

    print(json.dumps(decision, ensure_ascii=False, indent=2))
    if contradiction:
        print(f"\nWARNING: {contradiction}.\n"
              f"  Do not run this repair as prefilled. Pick another repair, or "
              f"approve.", file=sys.stderr)
    print(f"\nbudget: {st.repairs_used}/{st.round_budget} used, "
          f"{st.budget_remaining} left")
    print("The judge only PREFILLS (R10). You decide:\n"
          f"  accept  : approve --job {job}\n"
          f"  repair  : repair --job {job} --from-judge\n"
          f"  override: repair --job {job} --repair <type> --delta '<text>'\n"
          f"  give up : abort --job {job}")
    return 0


# --------------------------------------------------------------------------- #
# repair
# --------------------------------------------------------------------------- #

INTEGRITY_DELTA = (
    "Restore the product to its exact authoritative appearance: {traits}. The "
    "body shape, colour, control panel, and hardware must match those traits "
    "exactly, and neither end of the product may be cropped. Change nothing "
    "else about the image.")


def cmd_repair(args: argparse.Namespace) -> int:
    job = pathlib.Path(args.job).expanduser().resolve()
    st = JobState.load(job)
    if st.state != C.S_AWAITING_ROUND_REVIEW:
        print(f"job is in state {st.state}; repair expects "
              f"{C.S_AWAITING_ROUND_REVIEW}", file=sys.stderr)
        return 1
    facts, traits, brief = _load_compiled(job)
    req = G1C.load_json(job / "request" / "generation_request.json")
    intent = req.get("intent") or {}
    canvas = intent.get("canvas") or "1:1"
    truth = G1C.load_json(req["product_truth"])

    last = st.rounds[-1]
    judge = last.judge_decision or {}
    repair = args.repair or judge.get("repair")
    delta = args.delta or judge.get("prompt_delta")
    overrode = bool(args.repair and judge.get("repair")
                    and args.repair != judge.get("repair"))

    # §7: a product-integrity failure outranks whatever repair was chosen, and
    # the round is free.
    integrity = judge.get("product_integrity_ok", True) is False
    if integrity and not args.ignore_integrity:
        repair = "increase_product_dominance"  # menu slot; delta is the fixed text
        delta = INTEGRITY_DELTA.format(
            traits=", ".join(traits.get("product_visual_traits") or []))
        print("judge reported product_integrity_ok=false -> forced integrity "
              "restore round, which does not consume budget (§7)")

    if not repair:
        print("no repair selected: pass --repair/--delta or run review first",
              file=sys.stderr)
        return 1
    if not delta:
        print(f"repair {repair!r} needs a --delta (the judge supplied none)",
              file=sys.stderr)
        return 1

    extra: list[templates.InputImage] = []
    for spec in args.extra_image or []:
        if "=" not in spec:
            print(f"--extra-image needs role=path, got {spec!r}", file=sys.stderr)
            return 1
        role, _, path = spec.partition("=")
        extra.append(templates.InputImage(role.strip(), str(
            pathlib.Path(path).expanduser().resolve())))

    if repair == "complete_accessories" and not extra:
        try:
            G1C.require_accessories_evidence(truth, req.get("product_images") or [])
        except G1C.NeedsUserInput as exc:
            st.transition(C.S_NEEDS_USER_INPUT, str(exc))
            print(f"STOP: {exc}", file=sys.stderr)
            return 6
        for im in req.get("product_images") or []:
            if im["role"] in (C.ROLE_ACCESSORIES_EVIDENCE,
                              C.ROLE_NATIVE_TEXT_EVIDENCE):
                extra.append(templates.InputImage(im["role"], im["path"]))
                break

    if st.budget_exhausted and not integrity:
        st.transition(C.S_NEEDS_MANUAL,
                      f"budget exhausted at {st.repairs_used}/{st.round_budget}")
        print(f"STOP: round budget exhausted ({st.repairs_used}/"
              f"{st.round_budget}); state -> {C.S_NEEDS_MANUAL} (R9). "
              f"Standards are not relaxed to force a result.", file=sys.stderr)
        return 7

    st.transition(C.S_REPAIRING, f"repair {repair}")
    prev = templates.InputImage(C.ROLE_PREVIOUS_CANVAS, str(st.latest_candidate()))
    try:
        prompt = templates.compile_repair(
            previous=prev, repair=repair, prompt_delta=delta, facts=facts,
            traits=traits, brief=brief, canvas=canvas,
            approved_modules=st.approved_modules,
            fact_violations=judge.get("fact_violations") or [],
            extra_images=extra)
    except templates.PromptCompileError as exc:
        st.transition(C.S_AWAITING_ROUND_REVIEW, f"repair rejected: {exc}")
        print(f"rejected: {exc}", file=sys.stderr)
        return 1

    try:
        rec = st.allocate_round(ROUND_KIND_REPAIR, repair_type=repair,
                                integrity_restore=integrity)
    except StateError as exc:
        st.transition(C.S_NEEDS_MANUAL, str(exc))
        print(f"STOP: {exc}", file=sys.stderr)
        return 7

    _record_human(st.round_dir(rec), "repair", decided_by=args.decided_by,
                  st=st, round_index=rec.index,
                  repair=repair, judge_repair=judge.get("repair"),
                  overrode_judge=overrode, integrity_restore=integrity,
                  delta_source="human" if args.delta else "judge")
    meta = _generate_round(st, rec, prompt, facts, intent,
                           timeout_s=args.timeout, model=args.model)
    st.transition(C.S_AWAITING_ROUND_REVIEW,
                  "repair done" if meta else "backend error")
    print(json.dumps(st.summary(), ensure_ascii=False, indent=2))
    return 0 if meta else 4


# --------------------------------------------------------------------------- #
# approve / abort
# --------------------------------------------------------------------------- #

def cmd_approve(args: argparse.Namespace) -> int:
    job = pathlib.Path(args.job).expanduser().resolve()
    st = JobState.load(job)
    if st.state != C.S_AWAITING_ROUND_REVIEW:
        print(f"job is in state {st.state}; approve expects "
              f"{C.S_AWAITING_ROUND_REVIEW}", file=sys.stderr)
        return 1
    candidate = st.latest_candidate()
    if not candidate or not candidate.is_file():
        print("nothing to approve", file=sys.stderr)
        return 1

    if args.module:
        st.approve_modules(list(args.module))
    rec = st.rounds[-1]
    _record_human(st.round_dir(rec), "approve", decided_by=args.decided_by,
                  st=st, round_index=rec.index,
                  approved_modules=st.approved_modules,
                  candidate=str(candidate))

    if args.modules_only:
        # Approve modules but keep iterating: retention list grows, loop continues.
        print(f"approved modules: {st.approved_modules} (still in review)")
        return 0

    anchor_dir = job / "anchor"
    anchor_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidate, anchor_dir / "anchor.png")
    meta_src = st.round_dir(rec) / "candidate_meta.json"
    anchor_meta = G1C.load_json(meta_src) if meta_src.is_file() else {}
    anchor_meta.update({"source_round": rec.dirname, "approved_at": _now(),
                        "approved_modules": st.approved_modules})
    _write_json(anchor_dir / "anchor_meta.json", anchor_meta)
    st.set_anchor(anchor_dir / "anchor.png", rec.index)
    st.transition(C.S_CONVERGED, f"human approved {rec.dirname}")

    print(f"converged. anchor: {anchor_dir / 'anchor.png'}")
    print(json.dumps(st.summary(), ensure_ascii=False, indent=2))
    return 0


def cmd_abort(args: argparse.Namespace) -> int:
    job = pathlib.Path(args.job).expanduser().resolve()
    st = JobState.load(job)
    if st.rounds:
        _record_human(st.round_dir(st.rounds[-1]), "abort",
                      decided_by=args.decided_by, st=st,
                      round_index=st.rounds[-1].index,
                      reason=args.reason or "")
    st.transition(C.S_NEEDS_MANUAL, f"human abort: {args.reason or ''}")
    print(f"state -> {C.S_NEEDS_MANUAL}")
    return 0


# --------------------------------------------------------------------------- #
# style transfer (§5.5)
# --------------------------------------------------------------------------- #

def cmd_style_transfer(args: argparse.Namespace) -> int:
    job = pathlib.Path(args.job).expanduser().resolve()
    st = JobState.load(job)
    anchor = st.anchor
    if not anchor:
        print("no anchor: style transfer requires a converged job (R11)",
              file=sys.stderr)
        return 1
    if st.state not in (C.S_CONVERGED, C.S_TRANSFER_DONE,
                        C.S_AWAITING_TRANSFER_REVIEW):
        print(f"job is in state {st.state}; style transfer needs a converged job",
              file=sys.stderr)
        return 1

    new_ref = str(pathlib.Path(args.reference).expanduser().resolve())
    if not pathlib.Path(new_ref).is_file():
        print(f"reference not found: {new_ref}", file=sys.stderr)
        return 1
    ref_id = args.ref_id or pathlib.Path(new_ref).stem

    attempts = st.transfer_attempts(ref_id)
    if attempts > C.MAX_TRANSFER_RETRIES:
        print(f"ref {ref_id!r} already had {attempts} attempts "
              f"(max {C.MAX_TRANSFER_RETRIES + 1} incl. first) (§5.5)",
              file=sys.stderr)
        return 7

    facts, traits, _ = _load_compiled(job)
    req = G1C.load_json(job / "request" / "generation_request.json")
    intent = req.get("intent") or {}
    canvas = intent.get("canvas") or "1:1"
    anchor_img = next(im for im in (req.get("product_images") or [])
                      if im["role"] == C.ROLE_APPEARANCE_ANCHOR)

    print(f"briefing new reference {ref_id} ...", flush=True)
    new_brief = describers.describe_reference_design(
        new_ref, context=G1C.truth_title(G1C.load_json(req["product_truth"])),
        provider=args.provider, timeout_s=args.describe_timeout,
        model=args.describe_model)
    new_brief["aspect_ratio"] = G1C.measure_aspect_ratio(new_ref)

    brand, short_name = _brand_and_name(facts, req)
    images = [templates.InputImage(C.ROLE_DESIGN_MASTER, new_ref),
              templates.InputImage(C.ROLE_STYLE_ANCHOR, anchor["path"]),
              templates.InputImage(C.ROLE_APPEARANCE_ANCHOR, anchor_img["path"])]
    prompt = templates.compile_style_transfer(
        images=images, facts=facts, traits=traits, brief=new_brief, canvas=canvas,
        brand=brand, product_short_name=short_name)
    templates.audit_prompt(prompt, facts)

    out_dir = job / "style_transfers" / ref_id / f"attempt_{attempts:02d}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "prompt.md").write_text(prompt.text + "\n", encoding="utf-8")
    _write_json(out_dir / "inputs.json",
                {"phase": prompt.phase, "images": prompt.inputs_manifest()})
    _write_json(out_dir / "reference_design_brief.json", new_brief)

    st.transition(C.S_AWAITING_TRANSFER_REVIEW, f"style transfer {ref_id}")
    print(f"  generating (attempt {attempts + 1}/"
          f"{C.MAX_TRANSFER_RETRIES + 1})...", flush=True)
    try:
        meta = backend.generate(
            prompt.text, prompt.image_paths, str(out_dir / "candidate.png"),
            timeout_s=args.timeout, output_px=int(intent.get("output_px") or 1600),
            model=args.model, meta_path=str(out_dir / "candidate_meta.json"))
    except Exception as exc:
        _write_json(out_dir / "backend_error.json", {"error": str(exc)[:4000]})
        print(f"backend error: {exc}", file=sys.stderr)
        return 4

    st.record_transfer(ref_id, attempts, str(out_dir / "candidate.png"))
    print(f"  ok: {meta['final_size']} in {meta['elapsed_s']}s -> "
          f"{out_dir / 'candidate.png'}")
    print(f"\nreview it, then:\n"
          f"  accept : transfer-accept --job {job} --ref-id {ref_id}\n"
          f"  retry  : style-transfer --job {job} --reference {new_ref} "
          f"--ref-id {ref_id}")
    return 0


def cmd_transfer_accept(args: argparse.Namespace) -> int:
    job = pathlib.Path(args.job).expanduser().resolve()
    st = JobState.load(job)
    if st.state != C.S_AWAITING_TRANSFER_REVIEW:
        print(f"job is in state {st.state}; expects "
              f"{C.S_AWAITING_TRANSFER_REVIEW}", file=sys.stderr)
        return 1
    ref_id = args.ref_id
    transfers = [t for t in st.data.get("style_transfers", [])
                 if t["ref_id"] == ref_id]
    if not transfers:
        print(f"no transfer recorded for ref_id {ref_id!r}", file=sys.stderr)
        return 1
    latest = transfers[-1]
    out_dir = pathlib.Path(latest["candidate"]).parent
    _record_human(out_dir, "approve", decided_by=args.decided_by, ref_id=ref_id,
                  attempt=latest["attempt"], candidate=latest["candidate"])
    st.transition(C.S_TRANSFER_DONE, f"human approved transfer {ref_id}")
    print(f"transfer {ref_id} accepted: {latest['candidate']}")
    return 0


# --------------------------------------------------------------------------- #
# status
# --------------------------------------------------------------------------- #

def cmd_status(args: argparse.Namespace) -> int:
    st = JobState.load(pathlib.Path(args.job).expanduser().resolve())
    print(json.dumps(st.summary(), ensure_ascii=False, indent=2))
    print("\nrounds:")
    for r in st.rounds:
        flags = [f for f, on in (("budget", r.consumed_budget),
                                 ("backend_error", r.backend_error),
                                 ("integrity_restore", r.integrity_restore)) if on]
        judged = (r.judge_decision or {}).get("repair", "-")
        human = (r.human_decision or {}).get("decision", "-")
        size = ""
        if r.candidate and pathlib.Path(r.candidate).is_file():
            with Image.open(r.candidate) as im:
                size = f"{im.width}x{im.height}"
        print(f"  {r.dirname:<34} {size:<11} judge={judged:<28} "
              f"human={human:<8} {','.join(flags)}")
    return 0


# --------------------------------------------------------------------------- #
# cli
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_decider_arg(p: argparse.ArgumentParser) -> None:
        p.add_argument("--decided-by", default="human",
                       help="who made this call; recorded verbatim so the R10 "
                            "calibration labels stay honestly attributed")

    def add_backend_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--timeout", type=int, default=900,
                       help="image generation timeout (a call takes ~220s)")
        p.add_argument("--model", default=None, help="image backend model override")
        p.add_argument("--provider", default="codex", choices=["codex", "claude"])
        p.add_argument("--describe-timeout", type=int, default=300)
        p.add_argument("--describe-model", default=None)

    p = sub.add_parser("run", help="compile + initial generation")
    p.add_argument("--request", required=True, type=pathlib.Path)
    p.add_argument("--out-root", default="generation_runs")
    p.add_argument("--job-id", default=None)
    p.add_argument("--confirm-copy", action="store_true",
                   help="stop after drafting the copy so a human can review it "
                        "before anything is generated")
    add_backend_args(p)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("status", help="print state ledger")
    p.add_argument("--job", required=True)
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("review", help="judge prefill for the current candidate")
    p.add_argument("--job", required=True)
    add_backend_args(p)
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("repair", help="execute one human-confirmed repair round")
    p.add_argument("--job", required=True)
    p.add_argument("--from-judge", action="store_true",
                   help="use the judge's prefilled repair and delta as-is")
    p.add_argument("--repair", default=None, help="override the repair type")
    p.add_argument("--delta", default=None, help="override the repair instruction")
    p.add_argument("--extra-image", action="append", metavar="ROLE=PATH")
    p.add_argument("--ignore-integrity", action="store_true",
                   help="do not force an integrity restore round")
    add_backend_args(p)
    add_decider_arg(p)
    p.set_defaults(func=cmd_repair)

    p = sub.add_parser("approve", help="accept the candidate -> converged")
    p.add_argument("--job", required=True)
    p.add_argument("--module", action="append",
                   help="module name to add to the retention list, repeatable")
    p.add_argument("--modules-only", action="store_true",
                   help="record approved modules but keep iterating")
    add_decider_arg(p)
    p.set_defaults(func=cmd_approve)

    p = sub.add_parser("abort", help="give up -> needs_manual")
    p.add_argument("--job", required=True)
    p.add_argument("--reason", default="")
    add_decider_arg(p)
    p.set_defaults(func=cmd_abort)

    p = sub.add_parser("style-transfer", help="single-step transfer onto the anchor")
    p.add_argument("--job", required=True)
    p.add_argument("--reference", required=True)
    p.add_argument("--ref-id", default=None)
    add_backend_args(p)
    p.set_defaults(func=cmd_style_transfer)

    p = sub.add_parser("transfer-accept", help="accept a style transfer result")
    p.add_argument("--job", required=True)
    p.add_argument("--ref-id", required=True)
    add_decider_arg(p)
    p.set_defaults(func=cmd_transfer_accept)

    return ap


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except (StateError, templates.PromptCompileError, G1C.NeedsUserInput) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
