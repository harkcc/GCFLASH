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

# Ratios a marketplace image is ever actually expressed in.
COMMON_RATIOS = ((1, 1), (3, 4), (4, 3), (4, 5), (5, 4), (2, 3), (3, 2),
                 (9, 16), (16, 9), (5, 7), (7, 5))


def measure_aspect_ratio(image_path: str | pathlib.Path) -> str:
    """Measure a reference's aspect ratio from the file, as a clean ratio string.

    Deterministic on purpose. Asked for it, the design briefer returned "32:41"
    for a 736x982 image -- a literal pixel reduction that no one designs to. The
    ratio drives the layout-adaptation instruction, so it must be measured, not
    described.
    """
    from PIL import Image
    with Image.open(image_path) as im:
        w, h = im.size
    value = w / h
    best = min(COMMON_RATIOS, key=lambda r: abs(r[0] / r[1] - value))
    # Only snap when the real ratio is genuinely close to a designed one.
    if abs(best[0] / best[1] - value) <= 0.03:
        return f"{best[0]}:{best[1]}"
    from fractions import Fraction
    frac = Fraction(value).limit_denominator(20)
    return f"{frac.numerator}:{frac.denominator}"


def _normalise_for_lookup(text: str) -> str:
    """Lowercase and strip separators so '75 kPa' matches '75kpa'."""
    return re.sub(r"[\s ._\-–—/×x]+", "", (text or "").lower())


# A figure with its unit: "75kpa", "75 kPa", "1,000 W", "17x20 cm". Unit optional.
# The boundary excludes a preceding DIGIT, not a preceding word character: with
# \w the "20cm" in "17x20cm" was swallowed (the "17x" match consumed the x, and
# the lookbehind then blocked 20), so the product's own bag width was untraceable
# and legitimate copy saying "20 cm" was rejected.
_QUANTITY = re.compile(
    r"(?<![\d.,])(\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d+)?)\s*([a-zA-Z\u00b5\u03bc\u00b0]{1,6})?")

# Spellings of the same unit. Copy is written for humans and the listing title
# for a search engine, so the same figure legitimately appears as "120W" and
# "120 Watt". Different UNITS are still different claims -- no conversion here.
_UNIT_ALIASES = {
    "watt": "w", "watts": "w", "wat": "w", "vati": "w", "vat": "w",
    "kilowatt": "kw", "kilowatts": "kw",
    "kpa": "kpa", "kilopascal": "kpa", "kilopascali": "kpa",
    "centimetri": "cm", "centimetru": "cm", "cm": "cm",
    "milimetri": "mm", "milimetru": "mm",
    "metri": "m", "metru": "m",
    "kilograme": "kg", "kilogram": "kg", "grame": "g", "gram": "g",
    "litri": "l", "litru": "l", "mililitri": "ml",
    "volti": "v", "volt": "v", "volts": "v",
    "ore": "h", "ora": "h", "hours": "h", "hour": "h",
    "minute": "min", "minutes": "min",
}


def _canonical_unit(unit: str) -> str:
    u = (unit or "").lower()
    return _UNIT_ALIASES.get(u, u)


# Short words that may follow a number without being its unit.
_NON_UNIT_WORDS = frozenset({
    "de", "in", "si", "la", "cu", "and", "or", "the", "buc", "pcs", "x",
    "ani", "luni", "zile", "din", "pe", "st", "nd", "rd", "th",
})


def _parse_number(raw: str) -> float | None:
    """'1,000' -> 1000.0, '7.5' -> 7.5, '7,5' -> 7.5.

    A dot or comma followed by exactly three digits (with digits before it) is a
    thousands separator; anything else is a decimal separator. That covers both
    "1,000 W" and Romanian/German "1.000 W" without mistaking the decimal "7,5"
    for a thousands group.
    """
    raw = raw.strip()
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", raw):
        return float(re.sub(r"[.,]", "", raw))
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        return None


def _quantities(text: str) -> list[tuple[float, str, str]]:
    """Extract (value, lowercased unit, original span) triples.

    The original span is kept so an error message can quote the copy exactly as
    written -- reporting "70 kpa" for text that says "70 kPa" makes the operator
    hunt for a defect that is not there.
    """
    out: list[tuple[float, str, str]] = []
    for m in _QUANTITY.finditer(text or ""):
        value = _parse_number(m.group(1))
        if value is None:
            continue
        raw_unit = (m.group(2) or "").lower()
        if raw_unit in _NON_UNIT_WORDS:
            unit, span = "", m.group(1)
        else:
            unit, span = _canonical_unit(raw_unit), m.group(0).strip()
        out.append((value, unit, span))
    return out


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
    """Every figure in the copy must be evidenced by the operator's product info.

    Compares (value, unit) pairs, not substrings. The substring version passed
    several real errors: "7.5 W" matched a truth pack containing only "75 kPa"
    (the separator was stripped), "75 W" matched SKU "X7500", and "75 W" matched
    "75 kPa" because the unit was ignored -- while "1000 W" was wrongly rejected
    against "1,000 W".

    A figure carrying a unit must match both value and unit. A bare count
    ("100 DE PUNGI") only has to match a value, since the noun carries the
    meaning.

    This is the mechanical guard against the most damaging error in the
    pipeline: the 2026-07-11 run printed "70 kPa" for a 75 kPa product because a
    human typed it. Frozen copy is repeated verbatim on every round (R3), so a
    wrong figure spoils the job rather than one image.

    Returns a list of untraceable findings; empty means everything checks out.
    """
    known = _quantities(truth_blob(truth))
    known_values = {v for v, _, _ in known}
    known_pairs = {(v, u) for v, u, _ in known if u}

    findings: list[dict] = []
    for slot in slots or []:
        text = str(slot.get("text") or "").strip()
        for value, unit, span in _quantities(text):
            if unit:
                # No "the value exists somewhere unitless, so any unit is fine"
                # escape hatch: "6-In-1" in the title must not license "6 W".
                ok = (value, unit) in known_pairs
            else:
                ok = value in known_values
            if not ok:
                shown = span
                findings.append({
                    "slot": slot.get("slot"),
                    "text": text,
                    "number": shown,
                    "why": ("this value with this unit does not appear in the "
                            "product information" if unit else
                            "this figure does not appear in the product information"),
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
