#!/usr/bin/env python3
"""Prompt compiler for the G1 reference-generation workflow (SPEC §5).

Four templates: INIT (§5.2), RECOMPOSE (§5.3), REPAIR (§5.4),
STYLE_TRANSFER (§5.5). All of them are assembled from a fixed list of sections;
nothing outside those sections is ever emitted (R13).

The two sections that carry the frozen content -- the locked fact list (R3) and
the negative constraints (R6) -- are rendered ONCE per job by
``render_locked_facts_section`` / ``render_negative_section`` and the resulting
strings are spliced into every round unchanged. That is what makes "repeated
verbatim every round" a mechanical property of the code rather than a habit.
"""
from __future__ import annotations

import dataclasses
import pathlib

from . import contracts as C


class PromptCompileError(ValueError):
    """Raised when a prompt cannot be compiled without violating a frozen rule."""


# --------------------------------------------------------------------------- #
# data carriers
# --------------------------------------------------------------------------- #

@dataclasses.dataclass(frozen=True)
class InputImage:
    role: str
    path: str

    def __post_init__(self) -> None:
        if self.role not in C.VALID_ROLES:
            raise PromptCompileError(
                f"unknown image role {self.role!r}; valid: {sorted(C.VALID_ROLES)}")


@dataclasses.dataclass(frozen=True)
class CompiledPrompt:
    """A rendered prompt plus the exact ordered image list it refers to."""
    text: str
    images: tuple[InputImage, ...]
    phase: str

    @property
    def image_paths(self) -> list[str]:
        return [im.path for im in self.images]

    def inputs_manifest(self) -> list[dict]:
        """What gets written to the round's inputs.json (§4.2)."""
        return [{"ordinal": C.ordinal(i), "role": im.role, "path": im.path,
                 "exists": pathlib.Path(im.path).is_file()}
                for i, im in enumerate(self.images)]


# --------------------------------------------------------------------------- #
# frozen sections (rendered once, reused verbatim -- R3 / R6)
# --------------------------------------------------------------------------- #

def render_locked_facts_section(facts: dict, donor_language: str | None) -> str:
    """Section 4. Identical string in every round of the job."""
    slots = facts.get("copy_slots") or []
    if not slots:
        raise PromptCompileError("locked_fact_list.copy_slots is empty")
    lang = C.language_name(facts.get("language", ""))
    no_donor = f", no {donor_language}" if donor_language else ""
    lines = [
        f"Use {lang} text only, correctly spelled with correct diacritics"
        f"{no_donor}. Use exactly these concise product claims:"
    ]
    for slot in slots:
        text = (slot.get("text") or "").strip()
        if not text:
            raise PromptCompileError(f"copy slot {slot.get('slot')!r} has empty text")
        lines.append(f"- {slot.get('slot')}: {text}")
    return "\n".join(lines)


def render_negative_section() -> str:
    """Section 5. Fixed text (R6)."""
    return C.NEGATIVE_CONSTRAINTS_SENTENCE


# --------------------------------------------------------------------------- #
# image-set validation (R1)
# --------------------------------------------------------------------------- #

def validate_images(images: list[InputImage], phase: str) -> None:
    roles = [im.role for im in images]
    if not images:
        raise PromptCompileError(f"{phase}: no input images")

    if phase in ("INIT", "STYLE_TRANSFER"):
        n_anchor = roles.count(C.ROLE_APPEARANCE_ANCHOR)
        if n_anchor != 1:
            raise PromptCompileError(
                f"{phase}: exactly 1 {C.ROLE_APPEARANCE_ANCHOR} required, got "
                f"{n_anchor} (R1)")
        if roles.count(C.ROLE_DESIGN_MASTER) != 1:
            raise PromptCompileError(
                f"{phase}: exactly 1 {C.ROLE_DESIGN_MASTER} required, got "
                f"{roles.count(C.ROLE_DESIGN_MASTER)} (R1)")
    if phase == "STYLE_TRANSFER" and roles.count(C.ROLE_STYLE_ANCHOR) != 1:
        raise PromptCompileError(
            f"STYLE_TRANSFER: exactly 1 {C.ROLE_STYLE_ANCHOR} required (R11)")

    if phase in ("RECOMPOSE", "REPAIR"):
        if roles.count(C.ROLE_PREVIOUS_CANVAS) != 1:
            raise PromptCompileError(
                f"{phase}: the previous round's output must be attached exactly "
                f"once as {C.ROLE_PREVIOUS_CANVAS} (R4)")
        if roles[0] != C.ROLE_PREVIOUS_CANVAS:
            raise PromptCompileError(
                f"{phase}: {C.ROLE_PREVIOUS_CANVAS} must be the first image so it "
                f"is the canvas being edited (R4)")
    if phase == "RECOMPOSE" and len(images) != 1:
        raise PromptCompileError(
            "RECOMPOSE: the previous output is the only allowed input (§5.3)")

    if len(set(im.path for im in images)) != len(images):
        raise PromptCompileError(f"{phase}: duplicate image paths in input set")

    # R1: each role gets exactly one declaration clause, so a repeated role would
    # leave the second image silently undeclared. No legal phase needs a repeat.
    dupes = sorted({r for r in roles if roles.count(r) > 1})
    if dupes:
        raise PromptCompileError(
            f"{phase}: role(s) {dupes} appear more than once; every input image "
            f"needs its own declared role (R1)")


def validate_repair_images(repair: str, extra: list[InputImage]) -> None:
    """§7: a repair may only attach the extra image roles its row allows (R8)."""
    if repair not in C.REPAIR_MENU:
        raise PromptCompileError(
            f"repair {repair!r} is not in the repair menu; valid: "
            f"{sorted(C.REPAIR_MENU)} (R8)")
    allowed = C.REPAIR_MENU[repair]
    for im in extra:
        if im.role not in allowed:
            raise PromptCompileError(
                f"repair {repair!r} may not attach role {im.role!r}; "
                f"allowed: {sorted(allowed) or 'none'} (R8/§7)")
    if repair in C.SINGLE_EXTRA_IMAGE_REPAIRS and len(extra) > 1:
        raise PromptCompileError(
            f"repair {repair!r} allows at most 1 extra image, got {len(extra)} (§7)")


# --------------------------------------------------------------------------- #
# section builders
# --------------------------------------------------------------------------- #

def _role_index(images: list[InputImage], role: str) -> int:
    for i, im in enumerate(images):
        if im.role == role:
            return i
    raise PromptCompileError(f"required role {role!r} missing from image set")


# Module-name tokens naming a claim class R6 bans outright. A donor slot for one
# of these must not be reproduced even with our own content in it.
BANNED_MODULE_TOKENS = (
    "warranty", "guarantee", "certification", "certificate", "certified",
    "testimonial", "review", "rating", "price", "discount", "sale", "gift",
    "bonus", "free_", "promo",
)


def _is_banned_module(name: str) -> bool:
    return any(tok in name.lower() for tok in BANNED_MODULE_TOKENS)


def _join_traits(traits: list[str]) -> str:
    cleaned = [t.strip() for t in traits if (t or "").strip()]
    if not cleaned:
        raise PromptCompileError("immutable_traits.product_visual_traits is empty")
    return ", ".join(cleaned)


def _design_master_clause(images: list[InputImage], brief: dict) -> str:
    idx = _role_index(images, C.ROLE_DESIGN_MASTER)
    skeleton = (brief.get("layout_skeleton") or "").strip()
    if not skeleton:
        raise PromptCompileError("reference_design_brief.layout_skeleton is empty")
    donor_brand = (brief.get("donor_brand") or "").strip()
    donor_lang = (brief.get("donor_language") or "").strip()
    out = [
        f"Use the {C.ordinal(idx)} reference image as the design master: follow "
        f"its {skeleton}, visual hierarchy, and commercial advertising style."
    ]
    banned = ["its product"]
    if donor_brand:
        banned.append(f'its "{donor_brand}" branding')
    if donor_lang:
        banned.append(f"any {donor_lang} text")
    if len(banned) == 1:
        banned_text = banned[0]
    else:
        banned_text = ", ".join(banned[:-1]) + ", or " + banned[-1]
    out.append(f"Do not use {banned_text}.")
    return " ".join(out)


def _appearance_clause(images: list[InputImage], traits: dict,
                       anchor_role: str = C.ROLE_APPEARANCE_ANCHOR,
                       extra_role: str | None = None) -> str:
    idx = _role_index(images, anchor_role)
    trait_text = _join_traits(traits.get("product_visual_traits") or [])
    label = ("authoritative source for the product appearance"
             if anchor_role == C.ROLE_APPEARANCE_ANCHOR else
             "authoritative source for the product appearance and finished styling")
    out = [
        f"Use the {C.ordinal(idx)} reference image as the {label}: keep the exact "
        f"{trait_text}.",
        # SPEC §5.6 mechanism 2 -- fixed prohibition, never reworded.
        "Do not redesign the product and do not crop its ends.",
    ]
    if extra_role:
        try:
            eidx = _role_index(images, extra_role)
        except PromptCompileError:
            eidx = None
        if eidx is not None:
            out.insert(1, f"Use the {C.ordinal(eidx)} reference image as "
                          f"corroborating evidence for the same product's real "
                          f"appearance and its natively printed markings.")
    return " ".join(out)


def _accessories_clause(images: list[InputImage], traits: dict) -> str | None:
    try:
        idx = _role_index(images, C.ROLE_ACCESSORIES_EVIDENCE)
    except PromptCompileError:
        return None
    acc = [a.strip() for a in (traits.get("accessories") or []) if (a or "").strip()]
    if not acc:
        return None
    return (f"Use the {C.ordinal(idx)} reference image as evidence for the "
            f"included accessories: {', '.join(acc)}. The accessories must look "
            f"like included items, not random props.")


def _aspect_adaptation_clause(brief: dict, canvas: str) -> str | None:
    """Say out loud when the reference's shape differs from our target canvas.

    In production this is the normal case, not the exception: the upstream
    exporter emits ~750x1000 (3:4 portrait) references and the marketplace main
    image is 1:1. A square is a third wider relative to its height, so a vertical
    hero layout has to be genuinely re-distributed. Left unsaid, the model is
    free to letterbox, crop, or squeeze the borrowed layout into the square --
    and cropping is exactly what R5 forbids.
    """
    ref = (brief.get("aspect_ratio") or "").strip()
    if not ref or not canvas:
        return None
    ref_r, canvas_r = _ratio_value(ref), _ratio_value(canvas)
    if ref_r is None or canvas_r is None or abs(ref_r - canvas_r) <= 0.02:
        return None
    direction = ("wider and shorter" if canvas_r > ref_r else
                 "taller and narrower")
    return (
        f"Note that the design reference is {ref} while our canvas is {canvas}, "
        f"which is {direction}. Re-distribute the reference's layout to fill our "
        f"canvas naturally: spread the modules into the space the new proportions "
        f"give you, and resize the product to suit. Do not crop the reference's "
        f"composition, do not letterbox it, and do not squeeze it to fit.")


def _ratio_value(ratio: str) -> float | None:
    """'3:4' -> 0.75. None when unparseable."""
    try:
        w, h = str(ratio).split(":")
        return float(w) / float(h)
    except (ValueError, ZeroDivisionError, AttributeError):
        return None


def _scene_section(brief: dict, facts: dict | None = None) -> str:
    """Section 3, compiled from the design brief.

    Two guards learned from the 2026-07-30 end-to-end run, where round_00 grew an
    invented Romanian tagline that was in no copy slot:

    1. A module whose content is words must NOT be rendered as "replace its
       content", because that instruction invites the model to write new copy and
       turns section 3 into a second copy authority, competing with the locked
       fact list in section 4 (R3, and R13's single-authority principle).
    2. Donor promo slots that R6 bans outright -- warranty, certification,
       testimonial, price, gift -- are dropped from the layout entirely. Keeping
       the slot and hoping the negative constraints suppress its content is a
       needless bet against ourselves.
    """
    mood = (brief.get("color_mood") or "").strip().rstrip(".")
    notes = (brief.get("composition_notes") or "").strip().rstrip(".")
    if not mood:
        raise PromptCompileError("reference_design_brief.color_mood is empty")
    parts = [f"Scene and composition: {mood}."]
    if notes:
        parts.append(f"{notes[0].upper()}{notes[1:]}.")

    module_bits, dropped = [], []
    for mod in brief.get("modules") or []:
        if not mod.get("keep", True):
            continue
        name = (mod.get("module") or "").strip()
        if not name:
            continue
        if _is_banned_module(name):
            dropped.append(name)
            continue
        pos = (mod.get("position") or "").strip()
        bit = f"{name} at {pos}" if pos else name
        if mod.get("carries_text"):
            bit += " (using only the approved claims listed below, no other wording)"
        elif mod.get("replace_content"):
            bit += " (replace its content with our product)"
        module_bits.append(bit)

    if module_bits:
        parts.append("Keep this module layout: " + "; ".join(module_bits) + ".")
    if any(m.get("carries_text") and m.get("keep", True) and
           not _is_banned_module((m.get("module") or ""))
           for m in brief.get("modules") or []):
        # Guard 3, from the 2026-07-30 style transfer: telling the model to use
        # only approved claims is necessary but not sufficient. A module whose
        # FUNCTION is a list -- process_strip, step row, mode strip -- still gets
        # populated, because forbidding new wording leaves it no legal way to
        # honour the structural instruction. So give it one explicitly.
        parts.append("If a text module has no approved claim to carry, leave that "
                     "area as clean empty space; do not invent copy, step lists, "
                     "mode names, or numbered sequences to fill it.")
    if dropped:
        # Say it out loud: the donor had these blocks and we are refusing them.
        parts.append(f"Do not reproduce the reference's "
                     f"{', '.join(dropped)} block(s) in any form.")
    parts.append("Keep the product itself as the largest sharp foreground object, "
                 "with enough negative space for readable copy.")
    return " ".join(parts)


def _quality_section(canvas: str) -> str:
    return (f"Final output: a single finished {canvas} e-commerce advertising "
            f"image, high resolution, realistic product photography, premium "
            f"lighting, crisp legible typography, clean high-conversion "
            f"marketplace hero layout.")


def _fact_defence_section(fact_violations: list[dict]) -> str | None:
    """§5.6 mechanism 5. The 2026-07-11 chain used exactly this sentence shape."""
    if not fact_violations:
        return None
    lines = []
    for fv in fact_violations:
        wrong = (fv.get("wrong_value") or "").strip()
        right = (fv.get("correct_value") or "").strip()
        if not wrong or not right:
            raise PromptCompileError(
                f"fact_violation needs both wrong_value and correct_value: {fv}")
        lines.append(f"Do not use {wrong}: the authoritative source says {right}.")
    return " ".join(lines)


def _retention_clause(approved_modules: list[str]) -> str | None:
    """§5.6 mechanism 4 -- accumulated approved-module retention list."""
    mods = [m.strip() for m in (approved_modules or []) if (m or "").strip()]
    if not mods:
        return None
    return " ".join(
        f"The {m} is already approved and must remain essentially unchanged."
        for m in mods)


def _assemble(sections: list[str | None]) -> str:
    return "\n\n".join(s.strip() for s in sections if s and s.strip())


# --------------------------------------------------------------------------- #
# the four templates
# --------------------------------------------------------------------------- #

def compile_init(*, images: list[InputImage], facts: dict, traits: dict,
                 brief: dict, canvas: str, brand: str,
                 product_short_name: str) -> CompiledPrompt:
    """§5.2 INIT, round_00."""
    validate_images(images, "INIT")
    donor_lang = (brief.get("donor_language") or "").strip() or None

    s1 = (f"Create a polished e-commerce main product image in {canvas} format "
          f"for the {brand} {product_short_name}.")
    s2 = _assemble([
        _design_master_clause(images, brief),
        # §4.1 allows an optional native_text_evidence image; R1 requires it to be
        # declared too, or it is an undeclared visual input.
        _appearance_clause(images, traits, extra_role=C.ROLE_NATIVE_TEXT_EVIDENCE),
        _accessories_clause(images, traits),
    ])
    text = _assemble([
        s1, s2, _scene_section(brief),
        _aspect_adaptation_clause(brief, canvas),
        render_locked_facts_section(facts, donor_lang),
        render_negative_section(), _quality_section(canvas),
    ])
    return CompiledPrompt(text=text, images=tuple(images), phase="INIT")


def compile_recompose(*, previous: InputImage, facts: dict, traits: dict,
                      brief: dict, canvas: str) -> CompiledPrompt:
    """§5.3 RECOMPOSE. Re-layout, never crop (R5)."""
    images = [previous]
    validate_images(images, "RECOMPOSE")
    donor_lang = (brief.get("donor_language") or "").strip() or None
    lang = C.language_name(facts.get("language", ""))
    traits_text = _join_traits(traits.get("product_visual_traits") or [])

    s1 = (f"Recompose this exact finished e-commerce image into a true {canvas} "
          f"format. Preserve the same product ({traits_text}), scene, style, and "
          f"all existing {lang} text. Do not change the product or invent new "
          f"claims. Re-layout the elements so no important text or product is "
          f"cropped.")
    s6 = (f"Balanced {canvas} composition for a marketplace main image, "
          f"high-resolution realistic commercial photography, no watermark.")
    text = _assemble([s1, render_locked_facts_section(facts, donor_lang),
                      render_negative_section(), s6])
    return CompiledPrompt(text=text, images=tuple(images), phase="RECOMPOSE")


def compile_repair(*, previous: InputImage, repair: str, prompt_delta: str,
                   facts: dict, traits: dict, brief: dict, canvas: str,
                   approved_modules: list[str] | None = None,
                   fact_violations: list[dict] | None = None,
                   extra_images: list[InputImage] | None = None) -> CompiledPrompt:
    """§5.4 REPAIR, round_02..N. ``prompt_delta`` is the only per-round variable."""
    extra = list(extra_images or [])
    validate_repair_images(repair, extra)
    images = [previous, *extra]
    validate_images(images, "REPAIR")

    delta = (prompt_delta or "").strip()
    if not delta:
        raise PromptCompileError("repair round needs a non-empty prompt_delta")

    donor_lang = (brief.get("donor_language") or "").strip() or None
    lang = C.language_name(facts.get("language", ""))
    traits_text = _join_traits(traits.get("product_visual_traits") or [])

    # R4: repair rounds always edit, never create.
    s1_bits = [f"Edit this existing {canvas} image."]
    retention = _retention_clause(approved_modules or [])
    if retention:
        s1_bits.append(retention)
    s1_bits.append(f"Preserve the exact product ({traits_text}), the overall "
                   f"layout, and all existing {lang} text except as instructed "
                   f"below.")
    if extra:
        for im in extra:
            idx = _role_index(images, im.role)
            if im.role == C.ROLE_MODULE_INSPIRATION:
                s1_bits.append(
                    f"Use the {C.ordinal(idx)} reference image as inspiration for "
                    f"this one module's treatment only; do not take its product, "
                    f"branding, or text.")
            else:
                s1_bits.append(
                    f"Use the {C.ordinal(idx)} reference image only as evidence "
                    f"for what the included accessories really look like.")

    text = _assemble([
        " ".join(s1_bits), delta,
        _fact_defence_section(fact_violations or []),
        render_locked_facts_section(facts, donor_lang),
        render_negative_section(),
        f"Keep {canvas} format, crisp typography, no watermark, no element cropped.",
    ])
    return CompiledPrompt(text=text, images=tuple(images), phase="REPAIR")


def compile_style_transfer(*, images: list[InputImage], facts: dict, traits: dict,
                           brief: dict, canvas: str, brand: str,
                           product_short_name: str) -> CompiledPrompt:
    """§5.5 STYLE_TRANSFER. INIT's six sections, but appearance authority is the
    converged anchor (R11) and the scene section comes from the NEW reference."""
    validate_images(images, "STYLE_TRANSFER")
    donor_lang = (brief.get("donor_language") or "").strip() or None

    s1 = (f"Create a polished e-commerce main product image in {canvas} format "
          f"for the {brand} {product_short_name}.")
    s2 = _assemble([
        _design_master_clause(images, brief),
        _appearance_clause(images, traits, anchor_role=C.ROLE_STYLE_ANCHOR,
                           extra_role=C.ROLE_APPEARANCE_ANCHOR),
    ])
    text = _assemble([
        s1, s2, _scene_section(brief),
        _aspect_adaptation_clause(brief, canvas),
        render_locked_facts_section(facts, donor_lang),
        render_negative_section(), _quality_section(canvas),
    ])
    return CompiledPrompt(text=text, images=tuple(images), phase="STYLE_TRANSFER")


# --------------------------------------------------------------------------- #
# post-compile audit (the mechanical guarantee behind R3/R6/R4)
# --------------------------------------------------------------------------- #

def audit_prompt(prompt: CompiledPrompt, facts: dict) -> None:
    """Assert the invariants that made the 2026-07-11 chain work.

    Called by the runner before every backend call, so a template regression
    fails loudly instead of silently degrading output quality.
    """
    text = prompt.text
    for slot in facts.get("copy_slots") or []:
        t = (slot.get("text") or "").strip()
        if t and t not in text:
            raise PromptCompileError(
                f"locked fact {t!r} missing from {prompt.phase} prompt (R3)")
    if C.NEGATIVE_CONSTRAINTS_SENTENCE not in text:
        raise PromptCompileError(
            f"negative constraints section missing from {prompt.phase} prompt (R6)")
    if prompt.phase in ("RECOMPOSE", "REPAIR") and "Create" in text:
        raise PromptCompileError(
            f"{prompt.phase} prompt must not contain 'Create' (R4)")
    if prompt.phase == "REPAIR" and not text.startswith("Edit this existing"):
        raise PromptCompileError(
            "REPAIR prompt must start with 'Edit this existing' (R4)")
