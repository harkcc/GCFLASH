#!/usr/bin/env python3
"""Deterministic compilation of the frozen inputs (SPEC §5.1, §4.1 gates).

Where the target-language copy comes from
----------------------------------------
The upstream ``truth_pack.json`` holds ``operator_confirmed.title`` and
``operator_confirmed.facts`` -- free text, usually the marketplace listing title,
deliberately NOT structured into marketing slots.

Turning that into the handful of lines an image actually carries is real work:
choosing what to leave off, deciding which line earns the largest type, and
phrasing it in the target language. In the validated 2026-07-11 run the model
did exactly that unprompted -- the operator supplied only the listing title plus
"don't put everything on, it's a main image" and "output in Romanian". So it is
a fourth LLM node (``describers.compile_copy_slots``), not a human chore.

This module stays deterministic and does two jobs around that node:

- GATE the job on the truth pack (§4.1);
- VERIFY every figure in the resulting copy against the operator's product
  information (``verify_numbers_traceable``) before anything is frozen.

No LLM is involved here. Nothing in this module invents a claim.
"""
from __future__ import annotations

import json
import pathlib
import re

from . import contracts as C

# Slots that carry the three "core parameters" §4.1 gates on.
SLOT_BRAND = "brand"
SLOT_HEADLINE = "headline"
CORE_SPEC_SLOTS = ("spec_primary", "spec_secondary")

# A primary spec looks like a number plus a unit, e.g. "75 kPa", "120 W", "30 cm".
SPEC_PATTERN = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*(?:kpa|pa|bar|w|kw|v|mah|ah|ml|l|kg|g|mm|cm|m|db|rpm|"
    r"°c|hz|inch|\")\b", re.IGNORECASE)


NUMBER_PATTERN = re.compile(r"\d+(?:[.,]\d+)?")


def _normalise_for_lookup(text: str) -> str:
    """Lowercase and strip separators so '75 kPa' matches '75kpa'."""
    return re.sub(r"[\s ._\-–—/×x]+", "", (text or "").lower())


def truth_blob(truth: dict) -> str:
    """Everything the operator actually stated about the product, concatenated."""
    oc = truth.get("operator_confirmed") or {}
    parts = [truth_title(truth), str(oc.get("raw_product_info") or "")]
    parts += truth_facts(truth)
    obs = truth.get("source_visible_observations") or {}
    for key in ("visible_identity_text", "primary_product_accessories"):
        vals = obs.get(key)
        if isinstance(vals, list):
            parts += [str(v) for v in vals]
    return " ".join(parts)


def verify_numbers_traceable(slots: list[dict], truth: dict) -> list[dict]:
    """Every figure in the copy must appear in the operator's product info.

    This is the mechanical guard against the single most damaging error in the
    pipeline. The 2026-07-11 run put a wrong "70 kPa" on the image (the product
    is 75 kPa) because a human typed it into a follow-up instruction, and it took
    an explicit fact-defence line to undo. Once the fact list is frozen it is
    repeated verbatim on every subsequent round (R3), so a wrong number does not
    spoil one image, it spoils all of them.

    Returns a list of untraceable findings; empty means every number checks out.
    """
    blob = _normalise_for_lookup(truth_blob(truth))
    findings: list[dict] = []
    for slot in slots or []:
        text = (slot.get("text") or "").strip()
        for match in NUMBER_PATTERN.finditer(text):
            number = match.group(0)
            if _normalise_for_lookup(number) not in blob:
                findings.append({
                    "slot": slot.get("slot"),
                    "text": text,
                    "number": number,
                    "why": "this figure does not appear in the product information",
                })
    return findings


class IncompleteTruth(ValueError):
    """truth_pack is missing a core parameter -> terminal state (§4.1)."""

    def __init__(self, missing: list[str]):
        self.missing = missing
        super().__init__(
            "truth_pack is missing core parameter(s): " + ", ".join(missing) +
            f" -> terminal state {C.S_INCOMPLETE_TRUTH} (§4.1)")


def load_json(path: str | pathlib.Path) -> dict:
    p = pathlib.Path(path).expanduser()
    if not p.is_file():
        raise FileNotFoundError(f"required input not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# truth pack readers (tolerant: the shape has drifted across the repo)
# --------------------------------------------------------------------------- #

def truth_title(truth: dict) -> str:
    for path in (("operator_confirmed", "title"), ("title",),
                 ("product", "title"), ("operator_confirmed", "raw_product_info")):
        cur: object = truth
        for key in path:
            if not isinstance(cur, dict):
                cur = None
                break
            cur = cur.get(key)
        if isinstance(cur, str) and cur.strip():
            return cur.strip()
    return ""


def truth_facts(truth: dict) -> list[str]:
    oc = truth.get("operator_confirmed") or {}
    facts = oc.get("facts")
    if isinstance(facts, list):
        return [str(f).strip() for f in facts if str(f).strip()]
    if isinstance(truth.get("facts"), list):
        return [str(f).strip() for f in truth["facts"] if str(f).strip()]
    return []


def truth_expected_offer(truth: dict) -> str:
    oc = truth.get("operator_confirmed") or {}
    return str(oc.get("expected_offer") or truth.get("expected_offer") or
               "single_product")


def truth_native_text(truth: dict) -> list[str]:
    obs = truth.get("source_visible_observations") or {}
    vals = obs.get("visible_identity_text")
    return [str(v).strip() for v in vals if str(v).strip()] if isinstance(vals, list) else []


# --------------------------------------------------------------------------- #
# §4.1 gate
# --------------------------------------------------------------------------- #

def check_core_parameters(truth: dict, request_slots: list[dict] | None) -> None:
    """Raise IncompleteTruth if brand / product name / primary spec is missing.

    A value counts as present if the request supplies it OR the truth pack
    evidences it. We never accept a claim that appears in neither.
    """
    by_slot = {(s.get("slot") or "").strip(): (s.get("text") or "").strip()
               for s in (request_slots or [])}
    title = truth_title(truth)
    facts_blob = " ".join(truth_facts(truth)) + " " + title

    missing: list[str] = []
    if not by_slot.get(SLOT_BRAND) and not title:
        missing.append("brand")
    if not by_slot.get(SLOT_HEADLINE) and not title:
        missing.append("product_name")
    has_spec = any(by_slot.get(s) for s in CORE_SPEC_SLOTS) or \
        bool(SPEC_PATTERN.search(facts_blob))
    if not has_spec:
        missing.append("primary_spec")
    if missing:
        raise IncompleteTruth(missing)


def accessories_evidence_available(product_images: list[dict]) -> bool:
    roles = {(im.get("role") or "") for im in product_images}
    return bool(roles & {C.ROLE_ACCESSORIES_EVIDENCE, C.ROLE_NATIVE_TEXT_EVIDENCE})


def require_accessories_evidence(truth: dict, product_images: list[dict]) -> None:
    """§4.1: a complete_accessories repair may never let the model invent accessories.

    Called by the runner when that repair is selected, not at intake -- §4.1 lets
    the job start without the evidence image and only blocks the repair round.
    """
    if truth_expected_offer(truth) != "host_with_accessories":
        return
    if not accessories_evidence_available(product_images):
        raise NeedsUserInput(
            "expected_offer=host_with_accessories but no accessories_evidence or "
            "native_text_evidence image was supplied; a complete_accessories "
            "repair would have to invent the accessories, which is forbidden "
            "(§4.1). Supply an evidence image and retry this round.")


class NeedsUserInput(RuntimeError):
    """The job cannot proceed without another input from the operator."""


class UntraceableNumber(ValueError):
    """Copy carries a figure that is not in the operator's product information."""


# --------------------------------------------------------------------------- #
# §5.1 locked_fact_list
# --------------------------------------------------------------------------- #

def compile_locked_fact_list(*, truth: dict, intent: dict,
                             request_slots: list[dict] | None = None,
                             reference_metadata: dict | None = None,
                             native_product_text: list[str] | None = None) -> dict:
    """Compile once, allow one human revision, then freeze (R3)."""
    check_core_parameters(truth, request_slots)
    language = (intent.get("language") or "").strip()
    if not language:
        raise ValueError("intent.language is required to compile the fact list")

    needs_revision = False
    slots: list[dict] = []
    if request_slots:
        for s in request_slots:
            slot, text = (s.get("slot") or "").strip(), (s.get("text") or "").strip()
            if not slot or not text:
                raise ValueError(f"copy slot needs both slot and text: {s}")
            slots.append({"slot": slot, "text": text})
    else:
        # Draft only. Deliberately thin: a human must fill in target-language copy
        # before the job starts. We do not translate and we do not invent.
        title = truth_title(truth)
        if title:
            slots.append({"slot": SLOT_HEADLINE, "text": title})
        for match in SPEC_PATTERN.finditer(" ".join(truth_facts(truth))):
            spec = match.group(0).strip()
            if spec and not any(s["text"] == spec for s in slots):
                slots.append({"slot": f"spec_{len(slots)}", "text": spec})
        needs_revision = True

    native = list(native_product_text or []) or truth_native_text(truth)
    must_replace: list[str] = []
    if reference_metadata:
        warnings = reference_metadata.get("claim_warnings") or []
        for w in warnings:
            if isinstance(w, str) and w.strip():
                must_replace.append(w.strip())
            elif isinstance(w, dict):
                txt = (w.get("text") or w.get("claim") or w.get("warning") or "")
                if str(txt).strip():
                    must_replace.append(str(txt).strip())

    unverified = verify_numbers_traceable(slots, truth)
    if unverified:
        # Never auto-freeze copy carrying a figure we cannot trace (see
        # verify_numbers_traceable). A human must fix or explicitly accept it.
        needs_revision = True

    return {
        "language": language,
        "copy_slots": slots,
        "native_product_text": native,
        "must_replace_from_reference": must_replace,
        "needs_human_revision": needs_revision,
        "unverified_numbers": unverified,
        "frozen": False,
        "provenance": {
            "source": "request.copy_slots" if request_slots else "drafted_from_truth_pack",
            "truth_title": truth_title(truth),
            "expected_offer": truth_expected_offer(truth),
        },
    }


def freeze_fact_list(facts: dict, *, accept_unverified: bool = False) -> dict:
    """Mark the fact list frozen. After this, R3 forbids edits for the whole job.

    Refuses to freeze copy containing an untraceable figure unless a human
    explicitly accepts it, because freezing propagates the error to every round.
    """
    out = dict(facts)
    if not out.get("copy_slots"):
        raise ValueError("cannot freeze an empty copy_slots list")
    unverified = out.get("unverified_numbers") or []
    if unverified and not accept_unverified:
        detail = "; ".join(
            f"{u.get('slot')}={u.get('text')!r} (figure {u.get('number')})"
            for u in unverified)
        raise UntraceableNumber(
            f"refusing to freeze copy with untraceable figure(s): {detail}. "
            f"Fix the copy, or pass accept_unverified=True to override.")
    out["needs_human_revision"] = False
    out["frozen"] = True
    return out


# --------------------------------------------------------------------------- #
# §4.2 negative_constraints.json (R6 fixed content + donor specialisation)
# --------------------------------------------------------------------------- #

def compile_negative_constraints(brief: dict | None = None) -> dict:
    brief = brief or {}
    donor_brand = (brief.get("donor_brand") or "").strip()
    donor_lang = (brief.get("donor_language") or "").strip()
    specialised = []
    if donor_brand:
        specialised.append(f'no "{donor_brand}" branding')
    if donor_lang:
        specialised.append(f"no {donor_lang} text")
    return {
        "fixed_items": list(C.NEGATIVE_CONSTRAINT_ITEMS),
        "donor_specialised": specialised,
        "rendered_sentence": C.NEGATIVE_CONSTRAINTS_SENTENCE,
        "must_replace_note": (
            "Every claim visible on the reference image is unverified for this "
            "product and must be replaced or dropped."),
    }
