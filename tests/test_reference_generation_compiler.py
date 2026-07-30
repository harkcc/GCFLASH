"""Offline tests for the G1 prompt compiler + Codex adapter.

Covers SPEC `tasks/G1_reference_generation_workflow_v1.md` §9 items 1-6 and 10.
Items 7/8/9 (truth_pack gate, round budget, state machine) live with the state
machine and are not asserted here.

The real backend is NEVER called: one generation is ~220 s of paid inference
(§6), so `subprocess.run` is monkeypatched and `CODEX_HOME` is redirected into
tmp_path.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import subprocess
import sys
import types

import pytest
from PIL import Image

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import imagegen_codex_adapter as adapter  # noqa: E402
from workflow.reference_generation import contracts as C  # noqa: E402
from workflow.reference_generation import templates as T  # noqa: E402

PHASES = ("INIT", "RECOMPOSE", "REPAIR", "STYLE_TRANSFER")


# --------------------------------------------------------------------------- #
# fixtures: the SPEC's own vacuum-sealer example (§5.1)
# --------------------------------------------------------------------------- #

@pytest.fixture
def facts() -> dict:
    """locked_fact_list.json verbatim from §5.1 — Romanian copy with diacritics."""
    return {
        "language": "ro",
        "copy_slots": [
            {"slot": "brand", "text": "EXCITAT"},
            {"slot": "headline", "text": "APARAT DE VIDAT"},
            {"slot": "badge", "text": "6 ÎN 1"},
            {"slot": "supporting_line", "text": "PENTRU PRODUSE USCATE ȘI UMEDE"},
            {"slot": "spec_primary", "text": "75 kPa"},
            {"slot": "spec_secondary", "text": "120 W"},
            {"slot": "offer", "text": "100 DE PUNGI INCLUSE"},
            {"slot": "feature", "text": "BARĂ DE SIGILARE DE 30 cm"},
            {"slot": "feature_optional", "text": "CUTTER ÎNCORPORAT • STERILIZARE UV"},
        ],
        "native_product_text": ["VACUUM SEALER", "PULSE", "SEAL", "VAC"],
        "must_replace_from_reference": ["70 kPa badge", "Bellwell warranty line"],
    }


@pytest.fixture
def traits() -> dict:
    """immutable_traits.json verbatim from §5.1."""
    return {
        "product_visual_traits": [
            "black-and-silver body", "rounded rectangular shape",
            "top control panel with touch buttons", "black locking bar",
            "realistic proportions",
        ],
        "accessories": [
            "stack of clear vacuum sealer bags",
            "external vacuum hose with connector",
        ],
    }


@pytest.fixture
def brief() -> dict:
    """reference_design_brief.json verbatim from §5.1."""
    return {
        "aspect_ratio": "3:4",
        "layout_skeleton": ("vertical hero: headline top-left, product lower half "
                            "on wooden counter, person upper-right"),
        "modules": [
            {"module": "headline_block", "position": "upper-left", "keep": True},
            {"module": "spec_badges", "position": "mid-left", "keep": True},
            {"module": "person", "position": "upper-right", "keep": True},
            {"module": "product_stage", "position": "lower half", "keep": True,
             "replace_content": True},
        ],
        "color_mood": "warm premium kitchen, brown/orange, soft blur",
        "composition_notes": ("product angled in perspective; sealed bag emerging "
                              "from machine"),
        "donor_brand": "Bellwell",
        "donor_language": "Russian/Cyrillic",
        "visible_claims_on_reference": ["70 kPa", "2 ГОДА ГАРАНТИИ"],
    }


@pytest.fixture
def make_png(tmp_path):
    """Synthesise test images locally — tests must not depend on repo-external files."""
    def _make(name: str, size: tuple[int, int] = (64, 64),
              color: tuple[int, int, int] = (180, 90, 30)) -> pathlib.Path:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", size, color).save(path)
        return path
    return _make


@pytest.fixture
def imgs(make_png) -> types.SimpleNamespace:
    """One InputImage per role the four phases can legitimately receive."""
    def _im(role: str, name: str) -> T.InputImage:
        return T.InputImage(role=role, path=str(make_png(name)))

    return types.SimpleNamespace(
        design_master=_im(C.ROLE_DESIGN_MASTER, "r2-warm-chef.png"),
        design_master_new=_im(C.ROLE_DESIGN_MASTER, "r1-purple-info.png"),
        anchor=_im(C.ROLE_APPEARANCE_ANCHOR, "host_white_bg.png"),
        anchor_alt=_im(C.ROLE_APPEARANCE_ANCHOR, "host_white_bg_2.png"),
        accessories=_im(C.ROLE_ACCESSORIES_EVIDENCE, "accessories_white_bg.png"),
        native_text=_im(C.ROLE_NATIVE_TEXT_EVIDENCE, "original_poster.png"),
        module_ref=_im(C.ROLE_MODULE_INSPIRATION, "module_inspiration.png"),
        module_ref_2=_im(C.ROLE_MODULE_INSPIRATION, "module_inspiration_2.png"),
        previous=_im(C.ROLE_PREVIOUS_CANVAS, "round_01_candidate.png"),
        style_anchor=_im(C.ROLE_STYLE_ANCHOR, "anchor.png"),
    )


@pytest.fixture
def compiled(facts, traits, brief, imgs) -> dict[str, T.CompiledPrompt]:
    """One compiled prompt per phase, all from the same job's frozen artefacts."""
    init = T.compile_init(
        images=[imgs.design_master, imgs.anchor, imgs.accessories],
        facts=facts, traits=traits, brief=brief, canvas="1:1",
        brand="EXCITAT", product_short_name="vacuum sealer")
    recompose = T.compile_recompose(
        previous=imgs.previous, facts=facts, traits=traits, brief=brief,
        canvas="1:1")
    repair = T.compile_repair(
        previous=imgs.previous, repair="amplify_spec_impact",
        prompt_delta="Make the 75 kPa value the second-strongest element.",
        facts=facts, traits=traits, brief=brief, canvas="1:1")
    transfer = T.compile_style_transfer(
        images=[imgs.design_master_new, imgs.style_anchor, imgs.anchor],
        facts=facts, traits=traits, brief=brief, canvas="1:1",
        brand="EXCITAT", product_short_name="vacuum sealer")
    return {"INIT": init, "RECOMPOSE": recompose, "REPAIR": repair,
            "STYLE_TRANSFER": transfer}


# --------------------------------------------------------------------------- #
# §9.1 locked fact list + negative constraints, verbatim, EVERY phase (R3/R6)
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("phase", PHASES)
def test_locked_facts_appear_verbatim_in_every_phase(compiled, facts, phase):
    text = compiled[phase].text
    for slot in facts["copy_slots"]:
        assert slot["text"] in text, f"{phase} dropped locked fact {slot['text']!r} (R3)"


@pytest.mark.parametrize("phase", PHASES)
def test_diacritics_survive_compilation(compiled, phase):
    # R3 is only worth anything if the non-ASCII glyphs come through untouched.
    for fragment in ("6 ÎN 1", "BARĂ DE SIGILARE DE 30 cm",
                     "CUTTER ÎNCORPORAT • STERILIZARE UV",
                     "PENTRU PRODUSE USCATE ȘI UMEDE"):
        assert fragment in compiled[phase].text


@pytest.mark.parametrize("phase", PHASES)
def test_negative_constraints_appear_verbatim_in_every_phase(compiled, phase):
    assert C.NEGATIVE_CONSTRAINTS_SENTENCE in compiled[phase].text


def test_locked_fact_section_is_the_same_string_in_all_phases(compiled, facts, brief):
    # The mechanical guarantee: one rendered section spliced into every round,
    # not four hand-maintained copies that can drift apart.
    section = T.render_locked_facts_section(facts, brief["donor_language"])
    for phase in PHASES:
        assert section in compiled[phase].text


@pytest.mark.parametrize("phase", PHASES)
def test_language_and_donor_language_declared(compiled, phase):
    text = compiled[phase].text
    assert "Use Romanian text only" in text
    assert "no Russian/Cyrillic" in text


@pytest.mark.parametrize("phase", PHASES)
def test_audit_prompt_passes_for_every_phase(compiled, facts, phase):
    T.audit_prompt(compiled[phase], facts)  # runner's pre-flight gate


def test_audit_prompt_detects_a_missing_fact(compiled, facts):
    # Guards against a vacuous audit: a fact the prompt does not contain must fail.
    facts["copy_slots"].append({"slot": "extra", "text": "GARANȚIE 5 ANI"})
    with pytest.raises(T.PromptCompileError, match="missing from INIT prompt"):
        T.audit_prompt(compiled["INIT"], facts)


def test_audit_prompt_detects_a_missing_negative_section(compiled, facts):
    stripped = compiled["INIT"].text.replace(C.NEGATIVE_CONSTRAINTS_SENTENCE, "")
    mutated = T.CompiledPrompt(text=stripped, images=compiled["INIT"].images,
                               phase="INIT")
    with pytest.raises(T.PromptCompileError, match="negative constraints"):
        T.audit_prompt(mutated, facts)


def test_empty_copy_slots_is_rejected(facts, traits, brief, imgs):
    facts["copy_slots"] = []
    with pytest.raises(T.PromptCompileError, match="copy_slots is empty"):
        T.compile_init(images=[imgs.design_master, imgs.anchor], facts=facts,
                       traits=traits, brief=brief, canvas="1:1", brand="EXCITAT",
                       product_short_name="vacuum sealer")


# --------------------------------------------------------------------------- #
# §9.2 one role-declaration clause per input image (R1)
# --------------------------------------------------------------------------- #

_DECLARATION_RE = re.compile(r"Use the (FIRST|SECOND|THIRD|FOURTH|FIFTH) reference image")


def assert_every_image_declared(prompt: T.CompiledPrompt) -> None:
    """R1: every input image is addressed by its own ordinal, exactly once.

    The previous round's canvas is exempt: R4 addresses it as "this existing
    image", which is what makes it the canvas rather than a reference.
    """
    declared = _DECLARATION_RE.findall(prompt.text)
    expected = [C.ordinal(i) for i, im in enumerate(prompt.images)
                if im.role != C.ROLE_PREVIOUS_CANVAS]
    assert sorted(declared) == sorted(expected), (
        f"{prompt.phase}: declared={declared} expected={expected} for roles "
        f"{[im.role for im in prompt.images]} (R1)")


@pytest.mark.parametrize("phase", PHASES)
def test_every_input_image_has_a_role_declaration(compiled, phase):
    assert_every_image_declared(compiled[phase])


def test_init_declares_the_optional_native_text_evidence_image(
        facts, traits, brief, imgs):
    # §4.1 permits a third product image with role native_text_evidence; R1 says
    # it still needs a declared authority, otherwise it is an undeclared visual input.
    prompt = T.compile_init(
        images=[imgs.design_master, imgs.anchor, imgs.accessories, imgs.native_text],
        facts=facts, traits=traits, brief=brief, canvas="1:1", brand="EXCITAT",
        product_short_name="vacuum sealer")
    assert_every_image_declared(prompt)
    assert "natively printed markings" in prompt.text  # R7 exemption evidence


def test_role_declarations_name_the_authority_of_each_image(compiled):
    text = compiled["INIT"].text
    assert "as the design master" in text
    assert "authoritative source for the product appearance" in text
    assert "evidence for the included accessories" in text
    # R1 also forbids leaning on order to carry meaning, so the donor bans are
    # attached to the design-master clause itself.
    assert 'Do not use its product, its "Bellwell" branding, or any Russian/Cyrillic text.' in text


def test_missing_appearance_anchor_is_rejected(facts, traits, brief, imgs):
    with pytest.raises(T.PromptCompileError, match=r"product_appearance_anchor required"):
        T.compile_init(images=[imgs.design_master, imgs.accessories], facts=facts,
                       traits=traits, brief=brief, canvas="1:1", brand="EXCITAT",
                       product_short_name="vacuum sealer")


def test_duplicate_appearance_anchor_is_rejected(facts, traits, brief, imgs):
    with pytest.raises(T.PromptCompileError, match=r"product_appearance_anchor required"):
        T.compile_init(images=[imgs.design_master, imgs.anchor, imgs.anchor_alt],
                       facts=facts, traits=traits, brief=brief, canvas="1:1",
                       brand="EXCITAT", product_short_name="vacuum sealer")


def test_missing_design_master_is_rejected(facts, traits, brief, imgs):
    with pytest.raises(T.PromptCompileError, match=r"design_master required"):
        T.compile_init(images=[imgs.anchor], facts=facts, traits=traits,
                       brief=brief, canvas="1:1", brand="EXCITAT",
                       product_short_name="vacuum sealer")


def test_style_transfer_requires_the_converged_anchor(facts, traits, brief, imgs):
    # R11: appearance authority for a transfer is the converged anchor, not a
    # fresh convergence from the new reference.
    with pytest.raises(T.PromptCompileError, match="style_anchor"):
        T.compile_style_transfer(
            images=[imgs.design_master_new, imgs.anchor], facts=facts,
            traits=traits, brief=brief, canvas="1:1", brand="EXCITAT",
            product_short_name="vacuum sealer")


def test_style_transfer_points_appearance_authority_at_the_anchor(compiled):
    text = compiled["STYLE_TRANSFER"].text
    anchor_ord = C.ordinal(1)  # design_master, style_anchor, appearance_anchor
    assert (f"Use the {anchor_ord} reference image as the authoritative source for "
            f"the product appearance and finished styling") in text


def test_unknown_role_is_rejected():
    with pytest.raises(T.PromptCompileError, match="unknown image role"):
        T.InputImage(role="mood_board", path="/tmp/x.png")


def test_duplicate_image_paths_are_rejected(facts, traits, brief, imgs):
    twin = T.InputImage(role=C.ROLE_ACCESSORIES_EVIDENCE, path=imgs.anchor.path)
    with pytest.raises(T.PromptCompileError, match="duplicate image paths"):
        T.compile_init(images=[imgs.design_master, imgs.anchor, twin], facts=facts,
                       traits=traits, brief=brief, canvas="1:1", brand="EXCITAT",
                       product_short_name="vacuum sealer")


def test_repeated_role_is_rejected_rather_than_silently_undeclared(
        facts, traits, brief, imgs, make_png):
    # Two images sharing a role would collapse into one clause, leaving the
    # second an undeclared visual input (R1).
    twin = T.InputImage(role=C.ROLE_ACCESSORIES_EVIDENCE,
                        path=str(make_png("accessories_white_bg_2.png")))
    with pytest.raises(T.PromptCompileError, match="appear more than once"):
        T.compile_init(images=[imgs.design_master, imgs.anchor, imgs.accessories, twin],
                       facts=facts, traits=traits, brief=brief, canvas="1:1",
                       brand="EXCITAT", product_short_name="vacuum sealer")


def test_inputs_manifest_records_role_ordinal_and_existence(compiled):
    manifest = compiled["INIT"].inputs_manifest()
    assert [row["ordinal"] for row in manifest] == ["FIRST", "SECOND", "THIRD"]
    assert [row["role"] for row in manifest] == [
        C.ROLE_DESIGN_MASTER, C.ROLE_APPEARANCE_ANCHOR, C.ROLE_ACCESSORIES_EVIDENCE]
    assert all(row["exists"] for row in manifest)


# --------------------------------------------------------------------------- #
# §9.3 REPAIR edits the previous canvas; nothing but INIT may "Create" (R4)
# --------------------------------------------------------------------------- #

def test_repair_starts_with_edit_this_existing(compiled):
    assert compiled["REPAIR"].text.startswith("Edit this existing 1:1 image.")


def test_repair_takes_the_previous_output_as_its_first_image(compiled, imgs):
    images = compiled["REPAIR"].images
    assert images[0].role == C.ROLE_PREVIOUS_CANVAS
    assert images[0].path == imgs.previous.path
    assert compiled["REPAIR"].image_paths[0] == imgs.previous.path


def test_repair_with_extra_image_still_puts_the_canvas_first(
        facts, traits, brief, imgs):
    prompt = T.compile_repair(
        previous=imgs.previous, repair="redesign_spec_module",
        prompt_delta="Rebuild the spec module using a cleaner badge treatment.",
        facts=facts, traits=traits, brief=brief, canvas="1:1",
        extra_images=[imgs.module_ref])
    assert prompt.images[0].role == C.ROLE_PREVIOUS_CANVAS
    assert prompt.image_paths[1] == imgs.module_ref.path
    assert "Use the SECOND reference image as inspiration" in prompt.text


def test_repair_rejects_an_image_set_without_the_previous_canvas(
        facts, traits, brief, imgs):
    with pytest.raises(T.PromptCompileError, match="previous_canvas"):
        T.compile_repair(
            previous=imgs.anchor, repair="amplify_spec_impact",
            prompt_delta="Enlarge the 75 kPa badge.", facts=facts, traits=traits,
            brief=brief, canvas="1:1")


def test_repair_rejects_a_second_canvas(facts, traits, brief, imgs):
    # R4: exactly one canvas per round, otherwise the single-canvas chain breaks.
    second = T.InputImage(role=C.ROLE_PREVIOUS_CANVAS, path=imgs.anchor.path)
    with pytest.raises(T.PromptCompileError, match="previous_canvas"):
        T.compile_repair(
            previous=imgs.previous, repair="complete_accessories",
            prompt_delta="Add the bags as included items.", facts=facts,
            traits=traits, brief=brief, canvas="1:1", extra_images=[second])


def test_recompose_accepts_only_the_previous_output(facts, traits, brief, imgs):
    with pytest.raises(T.PromptCompileError, match="previous_canvas"):
        T.compile_recompose(previous=imgs.anchor, facts=facts, traits=traits,
                            brief=brief, canvas="1:1")


@pytest.mark.parametrize("phase", ["RECOMPOSE", "REPAIR"])
def test_no_create_in_edit_phases(compiled, phase):
    assert "Create" not in compiled[phase].text


def test_init_and_transfer_do_create(compiled):
    # The complement of the rule above: only the two from-scratch phases say it.
    for phase in ("INIT", "STYLE_TRANSFER"):
        assert compiled[phase].text.startswith(
            "Create a polished e-commerce main product image in 1:1 format")


def test_audit_catches_create_smuggled_in_by_the_judge(facts, traits, brief, imgs):
    # R8 lets the judge write prose; R4 still forbids "Create" in a repair round,
    # so the audit -- not the judge -- is the enforcement point.
    prompt = T.compile_repair(
        previous=imgs.previous, repair="reduce_clutter",
        prompt_delta="Create a new cleaner layout from scratch.", facts=facts,
        traits=traits, brief=brief, canvas="1:1")
    with pytest.raises(T.PromptCompileError, match="must not contain 'Create'"):
        T.audit_prompt(prompt, facts)


def test_repair_requires_a_prompt_delta(facts, traits, brief, imgs):
    with pytest.raises(T.PromptCompileError, match="prompt_delta"):
        T.compile_repair(previous=imgs.previous, repair="add_breathing_room",
                         prompt_delta="   ", facts=facts, traits=traits,
                         brief=brief, canvas="1:1")


def test_recompose_forbids_cropping(compiled):
    # R5: aspect correction is a re-layout, never a crop.
    text = compiled["RECOMPOSE"].text
    assert "Re-layout the elements so no important text or product is cropped." in text
    assert "crop" not in text.replace("cropped", "")


@pytest.mark.parametrize("phase", ["INIT", "REPAIR", "RECOMPOSE", "STYLE_TRANSFER"])
def test_product_traits_are_repeated_every_round(compiled, traits, phase):
    # §5.6 mechanism 1: enumerated traits beat a vague "keep the product".
    text = compiled[phase].text
    for trait in traits["product_visual_traits"]:
        assert trait in text, f"{phase} dropped trait {trait!r}"


@pytest.mark.parametrize("phase", ["INIT", "STYLE_TRANSFER"])
def test_fixed_product_prohibition_present(compiled, phase):
    # §5.6 mechanism 2: fixed sentence, never reworded per round.
    assert "Do not redesign the product and do not crop its ends." in compiled[phase].text


# --------------------------------------------------------------------------- #
# §9.4 approved-module retention list (§5.6 mechanism 4)
# --------------------------------------------------------------------------- #

def test_retention_clause_appears_for_each_approved_module(
        facts, traits, brief, imgs):
    prompt = T.compile_repair(
        previous=imgs.previous, repair="amplify_spec_impact",
        prompt_delta="Increase the contrast of the 75 kPa badge.", facts=facts,
        traits=traits, brief=brief, canvas="1:1",
        approved_modules=["accessory module", "headline block"])
    assert ("The accessory module is already approved and must remain essentially "
            "unchanged.") in prompt.text
    assert ("The headline block is already approved and must remain essentially "
            "unchanged.") in prompt.text
    # Must still be section 1, i.e. before the repair delta.
    assert prompt.text.index("already approved") < prompt.text.index("Increase the contrast")


def test_no_retention_clause_before_anything_is_approved(compiled):
    assert "already approved" not in compiled["REPAIR"].text


def test_blank_approved_modules_are_ignored(facts, traits, brief, imgs):
    prompt = T.compile_repair(
        previous=imgs.previous, repair="fix_text_error",
        prompt_delta="Fix the spelling of PUNGI.", facts=facts, traits=traits,
        brief=brief, canvas="1:1", approved_modules=["", "  "])
    assert "already approved" not in prompt.text


# --------------------------------------------------------------------------- #
# §9.5 fact defence sentence shape (§5.6 mechanism 5)
# --------------------------------------------------------------------------- #

def test_fact_violations_render_the_exact_sentence_shape(facts, traits, brief, imgs):
    prompt = T.compile_repair(
        previous=imgs.previous, repair="replace_claim_text",
        prompt_delta="Replace the leftover donor claim text.", facts=facts,
        traits=traits, brief=brief, canvas="1:1",
        fact_violations=[{"wrong_value": "70 kPa", "correct_value": "75 kPa"},
                         {"wrong_value": "110 W", "correct_value": "120 W"}])
    assert "Do not use 70 kPa: the authoritative source says 75 kPa." in prompt.text
    assert "Do not use 110 W: the authoritative source says 120 W." in prompt.text
    # Section 3 sits between the delta and the locked fact list (§5.4).
    assert (prompt.text.index("Replace the leftover")
            < prompt.text.index("Do not use 70 kPa")
            < prompt.text.index("Use Romanian text only"))


def test_no_fact_defence_section_when_no_violations(compiled):
    assert "the authoritative source says" not in compiled["REPAIR"].text


@pytest.mark.parametrize("violation", [
    {"wrong_value": "70 kPa", "correct_value": ""},
    {"wrong_value": "", "correct_value": "75 kPa"},
    {"correct_value": "75 kPa"},
])
def test_half_filled_fact_violation_is_rejected(facts, traits, brief, imgs, violation):
    with pytest.raises(T.PromptCompileError, match="fact_violation needs both"):
        T.compile_repair(
            previous=imgs.previous, repair="fix_text_error",
            prompt_delta="Correct the spec value.", facts=facts, traits=traits,
            brief=brief, canvas="1:1", fact_violations=[violation])


# --------------------------------------------------------------------------- #
# §9.6 repair menu is closed; extra images obey the §7 column (R8)
# --------------------------------------------------------------------------- #

def test_repair_menu_matches_the_spec_table():
    # §7 lists exactly ten repair types; a new one is a SPEC change, not a code change.
    assert set(C.REPAIR_MENU) == {
        "recompose_aspect", "complete_accessories", "increase_product_dominance",
        "amplify_spec_impact", "redesign_accessory_module", "redesign_spec_module",
        "add_breathing_room", "fix_text_error", "replace_claim_text",
        "reduce_clutter",
    }


@pytest.mark.parametrize("repair", ["make_it_pop", "recompose", "", "RECOMPOSE_ASPECT"])
def test_repair_outside_the_menu_is_rejected(facts, traits, brief, imgs, repair):
    with pytest.raises(T.PromptCompileError, match="not in the repair menu"):
        T.compile_repair(previous=imgs.previous, repair=repair,
                         prompt_delta="Do the thing.", facts=facts, traits=traits,
                         brief=brief, canvas="1:1")


@pytest.mark.parametrize("repair", sorted(
    r for r, allowed in C.REPAIR_MENU.items() if not allowed))
def test_repairs_with_an_empty_column_accept_no_extra_image(
        facts, traits, brief, imgs, repair):
    # §7 "允许附加图: 无" -- attaching anything here would add a second visual
    # authority (R13) on a round that is supposed to be single-variable (R4).
    with pytest.raises(T.PromptCompileError, match="may not attach role"):
        T.compile_repair(previous=imgs.previous, repair=repair,
                         prompt_delta="Adjust the one thing.", facts=facts,
                         traits=traits, brief=brief, canvas="1:1",
                         extra_images=[imgs.module_ref])
    # ...and compiles cleanly with none.
    prompt = T.compile_repair(previous=imgs.previous, repair=repair,
                              prompt_delta="Adjust the one thing.", facts=facts,
                              traits=traits, brief=brief, canvas="1:1")
    assert len(prompt.images) == 1


@pytest.mark.parametrize("repair", ["redesign_accessory_module", "redesign_spec_module"])
def test_module_repairs_take_exactly_one_inspiration_image(
        facts, traits, brief, imgs, repair):
    ok = T.compile_repair(
        previous=imgs.previous, repair=repair,
        prompt_delta="Restyle this module only.", facts=facts, traits=traits,
        brief=brief, canvas="1:1", extra_images=[imgs.module_ref])
    assert len(ok.images) == 2
    assert "inspiration for this one module's treatment only" in ok.text

    with pytest.raises(T.PromptCompileError, match="at most 1 extra image"):
        T.compile_repair(
            previous=imgs.previous, repair=repair,
            prompt_delta="Restyle this module only.", facts=facts, traits=traits,
            brief=brief, canvas="1:1",
            extra_images=[imgs.module_ref, imgs.module_ref_2])


@pytest.mark.parametrize("repair", ["redesign_accessory_module", "redesign_spec_module"])
def test_module_repairs_reject_a_role_outside_their_column(
        facts, traits, brief, imgs, repair):
    with pytest.raises(T.PromptCompileError, match="may not attach role"):
        T.compile_repair(previous=imgs.previous, repair=repair,
                         prompt_delta="Restyle this module only.", facts=facts,
                         traits=traits, brief=brief, canvas="1:1",
                         extra_images=[imgs.accessories])


@pytest.mark.parametrize("extra_name", ["accessories", "native_text"])
def test_complete_accessories_accepts_either_allowed_role(
        facts, traits, brief, imgs, extra_name):
    extra = getattr(imgs, extra_name)
    prompt = T.compile_repair(
        previous=imgs.previous, repair="complete_accessories",
        prompt_delta="Show the bags and hose as included items.", facts=facts,
        traits=traits, brief=brief, canvas="1:1", extra_images=[extra])
    assert prompt.images[1].role == extra.role
    assert "Use the SECOND reference image only as evidence" in prompt.text
    assert_every_image_declared(prompt)


def test_complete_accessories_accepts_both_allowed_roles_together(
        facts, traits, brief, imgs):
    prompt = T.compile_repair(
        previous=imgs.previous, repair="complete_accessories",
        prompt_delta="Show the bags and hose as included items.", facts=facts,
        traits=traits, brief=brief, canvas="1:1",
        extra_images=[imgs.accessories, imgs.native_text])
    assert [im.role for im in prompt.images] == [
        C.ROLE_PREVIOUS_CANVAS, C.ROLE_ACCESSORIES_EVIDENCE,
        C.ROLE_NATIVE_TEXT_EVIDENCE]
    assert_every_image_declared(prompt)


def test_complete_accessories_rejects_a_module_inspiration_image(
        facts, traits, brief, imgs):
    with pytest.raises(T.PromptCompileError, match="may not attach role"):
        T.compile_repair(previous=imgs.previous, repair="complete_accessories",
                         prompt_delta="Show the included bags.", facts=facts,
                         traits=traits, brief=brief, canvas="1:1",
                         extra_images=[imgs.module_ref])


# --------------------------------------------------------------------------- #
# §9.10 adapter: resample bookkeeping and byte-level input integrity (R2)
# --------------------------------------------------------------------------- #

def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def fake_backend(monkeypatch, tmp_path):
    """Stand in for `codex exec`.

    The adapter finds its output by reading the `thread.started` event and then
    scanning `$CODEX_HOME/generated_images/<thread_id>/` for the newest PNG
    (§6: the filename is not stable), so the fake reproduces exactly that.
    CODEX_HOME is read into module globals at import time, so the globals are
    what must be patched -- never the real ~/.codex, and never the real backend
    (~220 s of paid inference per call).
    """
    generated_root = tmp_path / "codex_home" / "generated_images"
    generated_root.mkdir(parents=True)
    monkeypatch.setattr(adapter, "CODEX_HOME", tmp_path / "codex_home")
    monkeypatch.setattr(adapter, "GENERATED_ROOT", generated_root)

    state = types.SimpleNamespace(
        thread_id="019fb317-7c88-72b0-8144-362b97641d8b",
        size=(1024, 1024),
        calls=[],
        generated_root=generated_root,
    )

    def fake_run(cmd, *args, **kwargs):
        if list(cmd[:2]) == ["codex", "--version"]:
            return subprocess.CompletedProcess(cmd, 0, "codex-cli 0.144.4\n", "")
        state.calls.append({"cmd": list(cmd), "input": kwargs.get("input"),
                            "timeout": kwargs.get("timeout")})
        thread_dir = generated_root / state.thread_id
        thread_dir.mkdir(parents=True, exist_ok=True)
        # Deliberately an unstable-looking filename: the adapter must not match on it.
        Image.new("RGB", state.size, (210, 140, 60)).save(
            thread_dir / f"exec-{len(state.calls)}-a6cdfb99.png")
        event = json.dumps({"type": "thread.started", "thread_id": state.thread_id})
        return subprocess.CompletedProcess(cmd, 0, event + "\n", "")

    monkeypatch.setattr(adapter.subprocess, "run", fake_run)
    return state


@pytest.fixture
def backend_inputs(make_png) -> list[pathlib.Path]:
    """Two non-identical input images, as a real round would attach."""
    return [make_png("in_host.png", (720, 720), (255, 255, 255)),
            make_png("in_reference.png", (736, 982), (40, 80, 160))]


def _generate(tmp_path, backend_inputs, **kwargs) -> dict:
    out = tmp_path / "round_00_initial" / "candidate.png"
    return adapter.generate("PROMPT BODY", [str(p) for p in backend_inputs],
                            str(out), timeout_s=5, workdir=str(tmp_path), **kwargs)


def test_resample_records_backend_and_final_size(fake_backend, tmp_path,
                                                 backend_inputs):
    fake_backend.size = (1024, 1024)
    meta = _generate(tmp_path, backend_inputs, output_px=1600)

    assert meta["backend_size"] == [1024, 1024]
    assert meta["final_size"] == [1600, 1600]
    assert meta["resampled"] is True
    assert meta["requested_output_px"] == 1600
    with Image.open(meta["candidate_png"]) as im:
        assert im.size == (1600, 1600)

    # Both sizes must survive into candidate_meta.json on disk (§4.2).
    on_disk = json.loads(pathlib.Path(meta["meta_path"]).read_text(encoding="utf-8"))
    assert on_disk["backend_size"] == [1024, 1024]
    assert on_disk["final_size"] == [1600, 1600]
    assert pathlib.Path(meta["meta_path"]).name == "candidate_meta.json"


def test_no_resample_when_the_backend_already_matches(fake_backend, tmp_path,
                                                      backend_inputs):
    fake_backend.size = (1600, 1600)
    meta = _generate(tmp_path, backend_inputs, output_px=1600)

    assert meta["resampled"] is False
    assert meta["backend_size"] == meta["final_size"] == [1600, 1600]
    # Untouched means byte-identical, not merely same-sized.
    assert _sha256(pathlib.Path(meta["candidate_png"])) == \
        _sha256(pathlib.Path(meta["source_png"]))


def test_output_px_zero_keeps_backend_resolution(fake_backend, tmp_path,
                                                 backend_inputs):
    # §6: output_px=0 means "keep whatever the backend returned".
    fake_backend.size = (1024, 1280)
    meta = _generate(tmp_path, backend_inputs, output_px=0)
    assert meta["resampled"] is False
    assert meta["final_size"] == [1024, 1280]


def test_resample_preserves_aspect_ratio_and_never_crops(fake_backend, tmp_path,
                                                         backend_inputs):
    # R2/R5: the long edge is scaled to output_px; a mismatched aspect is the
    # RECOMPOSE round's problem, never the adapter's to crop away.
    fake_backend.size = (1200, 1500)  # 4:5, deliberately non-square
    meta = _generate(tmp_path, backend_inputs, output_px=800)

    assert meta["backend_size"] == [1200, 1500]
    assert meta["final_size"] == [640, 800]
    assert max(meta["final_size"]) == 800
    bw, bh = meta["backend_size"]
    fw, fh = meta["final_size"]
    assert fw / fh == pytest.approx(bw / bh, rel=1e-6)
    assert meta["aspect_ratio"] == pytest.approx(0.8, rel=1e-6)
    # Same scale on both axes == nothing was clipped off either edge.
    assert fw / bw == pytest.approx(fh / bh, rel=1e-6)
    with Image.open(meta["candidate_png"]) as im:
        assert im.size == (640, 800)


def test_downscale_of_a_landscape_backend_image(fake_backend, tmp_path,
                                                backend_inputs):
    fake_backend.size = (1500, 1200)
    meta = _generate(tmp_path, backend_inputs, output_px=1000)
    assert meta["final_size"] == [1000, 800]
    assert meta["aspect_ratio"] == pytest.approx(1.25, rel=1e-6)


def test_input_images_are_hashed_and_left_byte_identical(fake_backend, tmp_path,
                                                         backend_inputs):
    # R2: the adapter is not allowed to touch the inputs at all -- no crop, no
    # mask, no re-encode. The recorded hash is the audit trail for that.
    before = {p: p.read_bytes() for p in backend_inputs}
    meta = _generate(tmp_path, backend_inputs, output_px=1600)

    recorded = {row["path"]: row["sha256"] for row in meta["input_images"]}
    assert len(recorded) == len(backend_inputs)
    for path in backend_inputs:
        resolved = str(path.resolve())
        assert resolved in recorded, f"{path} missing from candidate_meta.input_images"
        assert recorded[resolved] == hashlib.sha256(before[path]).hexdigest()
        assert path.read_bytes() == before[path], f"{path} was modified (R2)"

    sizes = {row["path"]: tuple(row["size"]) for row in meta["input_images"]}
    assert sizes[str(backend_inputs[0].resolve())] == (720, 720)
    assert sizes[str(backend_inputs[1].resolve())] == (736, 982)


def test_missing_input_image_fails_before_any_backend_call(fake_backend, tmp_path,
                                                           backend_inputs):
    with pytest.raises(FileNotFoundError):
        _generate(tmp_path, backend_inputs + [tmp_path / "nope.png"], output_px=1600)
    assert fake_backend.calls == []


def test_backend_receives_the_images_in_prompt_ordinal_order(fake_backend, tmp_path,
                                                             backend_inputs):
    # §6.5: `-i` order and the paths listed in the wrapper must agree, because
    # the prompt's FIRST/SECOND ordinals index into that order.
    _generate(tmp_path, backend_inputs, output_px=1600)
    cmd = fake_backend.calls[0]["cmd"]
    flagged = [cmd[i + 1] for i, tok in enumerate(cmd) if tok == "-i"]
    assert flagged == [str(p.resolve()) for p in backend_inputs]
    wrapper_lines = [line for line in fake_backend.calls[0]["input"].splitlines()
                     if re.match(r"^\d+\. /", line)]
    assert wrapper_lines == [f"{i}. {p.resolve()}"
                            for i, p in enumerate(backend_inputs, 1)]
    assert "--skip-git-repo-check" in cmd
    assert fake_backend.calls[0]["timeout"] == 5  # macOS has no `timeout(1)` (§6.7)


def test_retry_then_success_does_not_lose_the_attempt_log(monkeypatch, fake_backend,
                                                          tmp_path, backend_inputs):
    # §6: at most 2 extra attempts with identical parameters.
    real_run = adapter.subprocess.run
    calls = {"n": 0}

    def flaky(cmd, *args, **kwargs):
        if list(cmd[:2]) == ["codex", "--version"]:
            return real_run(cmd, *args, **kwargs)
        calls["n"] += 1
        if calls["n"] == 1:
            fake_backend.calls.append({"cmd": list(cmd), "input": kwargs.get("input"),
                                       "timeout": kwargs.get("timeout")})
            return subprocess.CompletedProcess(cmd, 1, "", "transport error")
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(adapter.subprocess, "run", flaky)
    meta = _generate(tmp_path, backend_inputs, output_px=1600)
    assert [a["attempt"] for a in meta["attempts"]] == [1, 2]
    assert meta["attempts"][0]["source_png"] is None
    assert meta["attempts"][1]["source_png"] == meta["source_png"]


def test_no_png_after_all_attempts_raises(monkeypatch, fake_backend, tmp_path,
                                           backend_inputs):
    def silent(cmd, *args, **kwargs):
        if list(cmd[:2]) == ["codex", "--version"]:
            return subprocess.CompletedProcess(cmd, 0, "codex-cli 0.144.4\n", "")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(adapter.subprocess, "run", silent)
    with pytest.raises(RuntimeError, match="produced no PNG after 3 attempt"):
        _generate(tmp_path, backend_inputs, output_px=1600)


# --------------------------------------------------------------------------- #
# R13: the wrapper is plumbing only -- all visual authority comes from the
# six-section prompt (§6.5). Not in §9, but it is the load-bearing invariant.
# --------------------------------------------------------------------------- #

# Vocabulary that can only be there to steer what the image looks like.
ART_DIRECTION_WORDS = (
    "lighting", "light", "premium", "composition", "compose", "style", "styling",
    "background", "backdrop", "photography", "photographic", "photo", "color",
    "colour", "realistic", "photorealistic", "hero", "aesthetic", "cinematic",
    "typography", "font", "layout", "palette", "contrast", "shadow", "texture",
    "vibrant", "luxury", "minimalist", "sharp", "crisp", "bokeh", "angle",
    "lens", "mood", "beautiful", "professional", "product", "brand", "scene",
    "highlight", "glossy", "studio", "resolution", "quality",
)


def _art_direction_hits(text: str) -> list[str]:
    return sorted({w for w in ART_DIRECTION_WORDS
                   if re.search(rf"\b{w}\b", text, re.IGNORECASE)})


def test_wrapper_template_contains_zero_art_direction():
    # R13: multiple visual authorities is what broke the three earlier attempts.
    # If this fails, someone put art direction in the plumbing -- move it into
    # the compiled six-section prompt or delete it. Do not extend the allowlist.
    skeleton = adapter.WRAPPER_TEMPLATE.replace("{prompt}", "").replace(
        "{image_path_lines}", "")
    hits = _art_direction_hits(skeleton)
    assert hits == [], (
        f"WRAPPER_TEMPLATE must be pure plumbing (R13) but mentions {hits}; "
        f"visual authority may only come from the compiled six-section prompt")


def test_wrapper_only_ever_says_pass_the_prompt_through_unchanged(compiled):
    wrapped = adapter.WRAPPER_TEMPLATE.format(
        image_path_lines="1. /abs/a.png", prompt=compiled["INIT"].text)
    marker = wrapped.index("=== IMAGE PROMPT (verbatim) ===")

    # Every art-direction word in the wrapped payload must sit inside the
    # verbatim block, i.e. it came from the compiled prompt, not the wrapper.
    for word in ART_DIRECTION_WORDS:
        for match in re.finditer(rf"\b{word}\b", wrapped, re.IGNORECASE):
            assert match.start() > marker, (
                f"{word!r} appears in the wrapper preamble; only the compiled "
                f"prompt may carry visual instruction (R13)")
    assert compiled["INIT"].text in wrapped  # passed through byte-for-byte


def test_compiled_prompt_reaches_the_backend_verbatim(fake_backend, tmp_path,
                                                      backend_inputs, compiled):
    out = tmp_path / "round_00_initial" / "candidate.png"
    prompt = compiled["INIT"].text
    meta = adapter.generate(prompt, [str(p) for p in backend_inputs], str(out),
                            timeout_s=5, workdir=str(tmp_path), output_px=1600)
    sent = fake_backend.calls[0]["input"]
    assert prompt in sent, "the adapter must not rewrite the compiled prompt (R13)"
    assert sent.startswith("Generate exactly one image using your image generation tool.")
    assert meta["prompt_sha256"] == hashlib.sha256(prompt.encode()).hexdigest()


# --------------------------------------------------------------------------- #
# Scene-section copy containment.
#
# Regression for the 2026-07-30 end-to-end run: round_00 grew an invented
# Romanian tagline ("PĂSTREAZĂ PROSPEȚIMEA, SAVUREAZĂ CALITATEA") that was in no
# copy slot. Root cause was section 3 rendering the brief's `tagline_block` as
# "replace its content with our product", which invites new wording and makes
# section 3 a second copy authority competing with section 4 (R3/R13).
# --------------------------------------------------------------------------- #

def _brief_with_modules(brief: dict, modules: list[dict]) -> dict:
    out = dict(brief)
    out["modules"] = modules
    return out


def _init_with_modules(facts, traits, brief, imgs, modules) -> str:
    return T.compile_init(
        images=[imgs.design_master, imgs.anchor], facts=facts, traits=traits,
        brief=_brief_with_modules(brief, modules), canvas="1:1", brand="EXCITAT",
        product_short_name="vacuum sealer").text


class TestSceneSectionDoesNotInviteNewCopy:
    def test_text_module_is_not_told_to_replace_its_content(
            self, facts, traits, brief, imgs):
        text = _init_with_modules(facts, traits, brief, imgs, [
            {"module": "tagline_block", "position": "upper-center",
             "keep": True, "replace_content": True, "carries_text": True}])
        assert "tagline_block at upper-center" in text
        # The invitation to invent must be gone...
        assert "tagline_block at upper-center (replace its content" not in text
        # ...and replaced by a pointer back to the one copy authority.
        assert "using only the approved claims listed below, no other wording" in text

    def test_imagery_module_still_gets_replace_content(
            self, facts, traits, brief, imgs):
        text = _init_with_modules(facts, traits, brief, imgs, [
            {"module": "product_stage", "position": "lower half", "keep": True,
             "replace_content": True, "carries_text": False}])
        assert "product_stage at lower half (replace its content with our product)" \
            in text

    @pytest.mark.parametrize("banned", [
        "warranty_badge", "certification_row", "testimonial_block",
        "price_tag", "gift_block", "discount_badge", "promo_ribbon",
    ])
    def test_r6_banned_donor_modules_are_dropped_not_merely_suppressed(
            self, facts, traits, brief, imgs, banned):
        text = _init_with_modules(facts, traits, brief, imgs, [
            {"module": banned, "position": "mid-center", "keep": True,
             "replace_content": True, "carries_text": True},
            {"module": "product_stage", "position": "lower half", "keep": True,
             "replace_content": True, "carries_text": False}])
        # R6: do not keep the slot and hope the negative constraints hold it down.
        assert f"{banned} at mid-center" not in text
        assert f"Do not reproduce the reference's {banned} block(s)" in text
        # The legitimate module survives.
        assert "product_stage at lower half" in text

    def test_dropped_modules_are_listed_together(
            self, facts, traits, brief, imgs):
        text = _init_with_modules(facts, traits, brief, imgs, [
            {"module": "warranty_badge", "position": "mid-center", "keep": True,
             "replace_content": False, "carries_text": True},
            {"module": "gift_block", "position": "mid-left", "keep": True,
             "replace_content": False, "carries_text": True}])
        assert "Do not reproduce the reference's warranty_badge, gift_block block(s)" \
            in text

    def test_keep_false_modules_are_omitted(self, facts, traits, brief, imgs):
        text = _init_with_modules(facts, traits, brief, imgs, [
            {"module": "person", "position": "upper-right", "keep": False,
             "replace_content": False, "carries_text": False},
            {"module": "product_stage", "position": "lower half", "keep": True,
             "replace_content": True, "carries_text": False}])
        assert "person at upper-right" not in text
        assert "product_stage at lower half" in text

    def test_real_world_brief_from_the_e2e_run_is_contained(
            self, facts, traits, brief, imgs):
        """The exact module list the describer returned on 2026-07-30."""
        text = _init_with_modules(facts, traits, brief, imgs, [
            {"module": "identity_block", "position": "upper-left", "keep": True,
             "replace_content": True, "carries_text": True},
            {"module": "tagline_block", "position": "upper-center", "keep": True,
             "replace_content": True, "carries_text": True},
            {"module": "headline_block", "position": "upper-left", "keep": True,
             "replace_content": True, "carries_text": True},
            {"module": "primary_spec_badge", "position": "mid-left", "keep": True,
             "replace_content": True, "carries_text": True},
            {"module": "warranty_badge", "position": "mid-center", "keep": True,
             "replace_content": True, "carries_text": True},
            {"module": "offer_block", "position": "mid-left", "keep": True,
             "replace_content": True, "carries_text": True},
            {"module": "person", "position": "upper-right", "keep": True,
             "replace_content": False, "carries_text": False},
            {"module": "product_stage", "position": "lower half", "keep": True,
             "replace_content": True, "carries_text": False},
        ])
        # Every text module keeps its structural slot but is pointed back at the
        # approved claim list instead of being told to invent content.
        for mod, pos in (("identity_block", "upper-left"),
                         ("tagline_block", "upper-center"),
                         ("headline_block", "upper-left"),
                         ("primary_spec_badge", "mid-left"),
                         ("offer_block", "mid-left")):
            assert f"{mod} at {pos} (using only the approved claims" in text
            assert f"{mod} at {pos} (replace its content" not in text
        # Exactly one module -- the product stage -- may be re-contented.
        assert text.count("(replace its content with our product)") == 1
        assert "product_stage at lower half (replace its content" in text
        # The banned donor slot appears only inside the explicit refusal.
        assert "warranty_badge" not in text.split("Do not reproduce")[0]


class TestUnfilledTextModulesHaveALegalAction:
    """Regression for the 2026-07-30 style transfer.

    A `process_strip` module carried the containment clause and STILL produced an
    invented Romanian mode list ("1 PULSE / 2 SIGILARE / 3 VAC / 4 UMED /
    5 AUTOMAT / 6 STOP"). Forbidding new wording without offering an alternative
    leaves the model no legal way to satisfy the structural instruction.
    """

    ESCAPE = ("If a text module has no approved claim to carry, leave that area "
              "as clean empty space; do not invent copy, step lists, mode names, "
              "or numbered sequences to fill it.")

    def test_escape_hatch_present_when_text_modules_exist(
            self, facts, traits, brief, imgs):
        text = _init_with_modules(facts, traits, brief, imgs, [
            {"module": "process_strip", "position": "top edge", "keep": True,
             "replace_content": False, "carries_text": True}])
        assert self.ESCAPE in text

    def test_absent_when_no_text_module(self, facts, traits, brief, imgs):
        text = _init_with_modules(facts, traits, brief, imgs, [
            {"module": "product_stage", "position": "lower half", "keep": True,
             "replace_content": True, "carries_text": False}])
        assert self.ESCAPE not in text

    def test_absent_when_only_banned_text_modules(self, facts, traits, brief, imgs):
        # The banned module is dropped, so there is no text slot left to guard.
        text = _init_with_modules(facts, traits, brief, imgs, [
            {"module": "warranty_badge", "position": "mid", "keep": True,
             "replace_content": False, "carries_text": True},
            {"module": "product_stage", "position": "lower half", "keep": True,
             "replace_content": True, "carries_text": False}])
        assert self.ESCAPE not in text

    def test_absent_when_text_module_not_kept(self, facts, traits, brief, imgs):
        text = _init_with_modules(facts, traits, brief, imgs, [
            {"module": "process_strip", "position": "top", "keep": False,
             "replace_content": False, "carries_text": True},
            {"module": "product_stage", "position": "lower half", "keep": True,
             "replace_content": True, "carries_text": False}])
        assert self.ESCAPE not in text

    def test_real_purple_transfer_brief_gets_the_escape_hatch(
            self, facts, traits, brief, imgs):
        """The exact module list the describer returned for r1-purple-info."""
        text = _init_with_modules(facts, traits, brief, imgs, [
            {"module": "process_strip", "position": "top edge", "keep": True,
             "replace_content": False, "carries_text": True},
            {"module": "headline_block", "position": "upper-left", "keep": True,
             "replace_content": False, "carries_text": True},
            {"module": "warranty_badge", "position": "mid-left", "keep": True,
             "replace_content": False, "carries_text": True},
            {"module": "product_stage", "position": "center", "keep": True,
             "replace_content": True, "carries_text": False},
        ])
        assert self.ESCAPE in text
        assert "process_strip at top edge (using only the approved claims" in text
        assert "warranty_badge at" not in text
