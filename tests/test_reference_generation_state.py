#!/usr/bin/env python3
"""SPEC §9 items 7-9: truth gate, round budget, state-machine legality.

Offline only -- no backend calls. Items 1-6 and 10 (prompt compiler + adapter)
live in ``test_reference_generation_compiler.py``.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from workflow.reference_generation import compile as G1C  # noqa: E402
from workflow.reference_generation import contracts as C  # noqa: E402
from workflow.reference_generation import templates as T  # noqa: E402
from workflow.reference_generation.state import (  # noqa: E402
    ROUND_KIND_INITIAL, ROUND_KIND_REPAIR, JobState, StateError,
)


def make_truth(*, title: str = "Excitat aparat de vidat 75 kPa 120 W",
               facts: list[str] | None = None,
               expected_offer: str = "single_product") -> dict:
    return {
        "operator_confirmed": {
            "title": title,
            "raw_product_info": "",
            "facts": facts if facts is not None else ["75 kPa", "120 W"],
            "expected_offer": expected_offer,
        },
        "source_visible_observations": {
            "visible_identity_text": ["VACUUM SEALER", "PULSE"],
            "visible_marketing_claims": [],
        },
    }


def new_job(tmp_path: pathlib.Path, *, budget: int = 8) -> JobState:
    return JobState.create(tmp_path / "job", product_id="p-1", job_id="j-1",
                           round_budget=budget, intent={"canvas": "1:1"})


# --------------------------------------------------------------------------- #
# §9.7 truth pack gate
# --------------------------------------------------------------------------- #

class TestTruthGate:
    def test_complete_truth_compiles(self):
        facts = G1C.compile_locked_fact_list(
            truth=make_truth(), intent={"language": "ro"},
            request_slots=[{"slot": "brand", "text": "EXCITAT"},
                           {"slot": "headline", "text": "APARAT DE VIDAT"},
                           {"slot": "spec_primary", "text": "75 kPa"}])
        assert facts["language"] == "ro"
        assert len(facts["copy_slots"]) == 3

    def test_missing_primary_spec_is_incomplete_truth(self):
        # No number+unit anywhere and no spec slot supplied -> §4.1 terminal state.
        truth = make_truth(title="Excitat vacuum sealer", facts=["negru"])
        with pytest.raises(G1C.IncompleteTruth) as exc:
            G1C.compile_locked_fact_list(
                truth=truth, intent={"language": "ro"},
                request_slots=[{"slot": "brand", "text": "EXCITAT"},
                               {"slot": "headline", "text": "APARAT DE VIDAT"}])
        assert "primary_spec" in exc.value.missing

    def test_missing_brand_and_name_is_incomplete_truth(self):
        truth = make_truth(title="", facts=["75 kPa"])
        with pytest.raises(G1C.IncompleteTruth) as exc:
            G1C.compile_locked_fact_list(truth=truth, intent={"language": "ro"},
                                         request_slots=[])
        assert "brand" in exc.value.missing
        assert "product_name" in exc.value.missing

    def test_spec_present_in_truth_pack_satisfies_gate(self):
        # The gate accepts evidence from the truth pack even with no spec slot.
        facts = G1C.compile_locked_fact_list(
            truth=make_truth(), intent={"language": "ro"},
            request_slots=[{"slot": "brand", "text": "EXCITAT"},
                           {"slot": "headline", "text": "APARAT DE VIDAT"}])
        assert facts["copy_slots"][0]["text"] == "EXCITAT"

    def test_draft_without_request_slots_flags_human_revision(self):
        facts = G1C.compile_locked_fact_list(truth=make_truth(),
                                            intent={"language": "ro"})
        # §5.1: compile once, human revises once, then freeze. Never auto-freeze
        # copy the operator never approved.
        assert facts["needs_human_revision"] is True
        assert facts["frozen"] is False

    def test_freeze_rejects_empty_slots(self):
        with pytest.raises(ValueError):
            G1C.freeze_fact_list({"copy_slots": []})

    def test_accessories_gate_blocks_invention(self):
        truth = make_truth(expected_offer="host_with_accessories")
        # No evidence image -> a complete_accessories repair must not proceed (§4.1).
        with pytest.raises(G1C.NeedsUserInput):
            G1C.require_accessories_evidence(
                truth, [{"role": C.ROLE_APPEARANCE_ANCHOR, "path": "/tmp/a.png"}])
        # With evidence it passes.
        G1C.require_accessories_evidence(
            truth, [{"role": C.ROLE_APPEARANCE_ANCHOR, "path": "/tmp/a.png"},
                    {"role": C.ROLE_ACCESSORIES_EVIDENCE, "path": "/tmp/b.png"}])

    def test_single_product_offer_needs_no_evidence(self):
        G1C.require_accessories_evidence(
            make_truth(), [{"role": C.ROLE_APPEARANCE_ANCHOR, "path": "/tmp/a.png"}])

    def test_reference_claim_warnings_become_must_replace(self):
        facts = G1C.compile_locked_fact_list(
            truth=make_truth(), intent={"language": "ro"},
            request_slots=[{"slot": "brand", "text": "EXCITAT"}],
            reference_metadata={"claim_warnings": [
                "12 месяцев гарантия", {"text": "Пакеты в подарок"}]})
        assert "12 месяцев гарантия" in facts["must_replace_from_reference"]
        assert "Пакеты в подарок" in facts["must_replace_from_reference"]


# --------------------------------------------------------------------------- #
# §9.8 round budget (R9)
# --------------------------------------------------------------------------- #

class TestRoundBudget:
    def test_initial_round_does_not_consume_budget(self, tmp_path):
        st = new_job(tmp_path, budget=2)
        st.allocate_round(ROUND_KIND_INITIAL)
        assert st.repairs_used == 0
        assert st.budget_remaining == 2

    def test_budget_exhaustion_blocks_new_rounds(self, tmp_path):
        st = new_job(tmp_path, budget=2)
        st.allocate_round(ROUND_KIND_INITIAL)
        st.allocate_round(ROUND_KIND_REPAIR, repair_type="add_breathing_room")
        st.allocate_round(ROUND_KIND_REPAIR, repair_type="reduce_clutter")
        assert st.budget_exhausted

        dirs_before = sorted(p.name for p in st.root.iterdir() if p.is_dir())
        with pytest.raises(StateError, match="budget exhausted"):
            st.allocate_round(ROUND_KIND_REPAIR, repair_type="fix_text_error")
        # R9: no new round directory may appear once the budget is gone.
        assert sorted(p.name for p in st.root.iterdir() if p.is_dir()) == dirs_before

    def test_integrity_restore_is_free(self, tmp_path):
        st = new_job(tmp_path, budget=1)
        st.allocate_round(ROUND_KIND_INITIAL)
        st.allocate_round(ROUND_KIND_REPAIR, repair_type="amplify_spec_impact")
        assert st.budget_exhausted
        # §7: an integrity restore is not a repair, so it still gets through.
        rec = st.allocate_round(ROUND_KIND_REPAIR,
                                repair_type="increase_product_dominance",
                                integrity_restore=True)
        assert rec.consumed_budget is False
        assert "integrity_restore" in rec.dirname

    def test_backend_error_refunds_budget(self, tmp_path):
        st = new_job(tmp_path, budget=1)
        st.allocate_round(ROUND_KIND_INITIAL)
        rec = st.allocate_round(ROUND_KIND_REPAIR, repair_type="fix_text_error")
        assert st.repairs_used == 1
        st.update_round(rec.index, backend_error=True)  # §6
        assert st.repairs_used == 0
        assert not st.budget_exhausted

    def test_repair_type_outside_menu_rejected(self, tmp_path):
        st = new_job(tmp_path)
        with pytest.raises(StateError, match="repair menu"):
            st.allocate_round(ROUND_KIND_REPAIR, repair_type="make_it_pop")

    def test_round_dirs_are_never_reused(self, tmp_path):
        st = new_job(tmp_path)
        r0 = st.allocate_round(ROUND_KIND_INITIAL)
        r1 = st.allocate_round(ROUND_KIND_REPAIR, repair_type="reduce_clutter")
        assert r0.dirname != r1.dirname
        assert r0.dirname.startswith("round_00")
        assert r1.dirname.startswith("round_01")

    def test_create_refuses_to_overwrite_existing_job(self, tmp_path):
        new_job(tmp_path)
        with pytest.raises(StateError, match="already exists"):
            new_job(tmp_path)  # R12: a rerun must use a fresh directory

    def test_auto_review_mode_refused(self, tmp_path):
        with pytest.raises(StateError, match="review_mode"):
            JobState.create(tmp_path / "j2", product_id="p", job_id="j",
                            review_mode="auto")  # R10 / §13


# --------------------------------------------------------------------------- #
# §9.9 state machine legality
# --------------------------------------------------------------------------- #

class TestStateMachine:
    def test_happy_path(self, tmp_path):
        st = new_job(tmp_path)
        for s in (C.S_COMPILING, C.S_GENERATING_INITIAL,
                  C.S_AWAITING_ROUND_REVIEW, C.S_REPAIRING,
                  C.S_AWAITING_ROUND_REVIEW, C.S_CONVERGED):
            st.transition(s)
        assert st.state == C.S_CONVERGED

    def test_repair_after_converged_rejected(self, tmp_path):
        st = new_job(tmp_path)
        for s in (C.S_COMPILING, C.S_GENERATING_INITIAL,
                  C.S_AWAITING_ROUND_REVIEW, C.S_CONVERGED):
            st.transition(s)
        with pytest.raises(StateError, match="illegal transition"):
            st.transition(C.S_REPAIRING)

    def test_cannot_skip_straight_to_converged(self, tmp_path):
        st = new_job(tmp_path)
        with pytest.raises(StateError, match="illegal transition"):
            st.transition(C.S_CONVERGED)

    def test_needs_manual_is_terminal(self, tmp_path):
        st = new_job(tmp_path)
        st.transition(C.S_COMPILING)
        st.transition(C.S_GENERATING_INITIAL)
        st.transition(C.S_AWAITING_ROUND_REVIEW)
        st.transition(C.S_NEEDS_MANUAL)
        for target in (C.S_REPAIRING, C.S_CONVERGED, C.S_AWAITING_ROUND_REVIEW):
            with pytest.raises(StateError):
                st.transition(target)

    def test_incomplete_truth_is_terminal(self, tmp_path):
        st = new_job(tmp_path)
        st.transition(C.S_INCOMPLETE_TRUTH)
        with pytest.raises(StateError):
            st.transition(C.S_COMPILING)

    def test_style_transfer_only_after_converged(self, tmp_path):
        st = new_job(tmp_path)
        st.transition(C.S_COMPILING)
        with pytest.raises(StateError):
            st.transition(C.S_AWAITING_TRANSFER_REVIEW)

    def test_transfer_can_repeat_from_transfer_done(self, tmp_path):
        st = new_job(tmp_path)
        for s in (C.S_COMPILING, C.S_GENERATING_INITIAL,
                  C.S_AWAITING_ROUND_REVIEW, C.S_CONVERGED,
                  C.S_AWAITING_TRANSFER_REVIEW, C.S_TRANSFER_DONE):
            st.transition(s)
        # R11: the anchor is reusable for many references.
        st.transition(C.S_AWAITING_TRANSFER_REVIEW)
        assert st.state == C.S_AWAITING_TRANSFER_REVIEW

    def test_same_state_transition_is_noop(self, tmp_path):
        st = new_job(tmp_path)
        st.transition(C.S_QUEUED)
        assert st.state == C.S_QUEUED

    def test_state_survives_reload(self, tmp_path):
        st = new_job(tmp_path)
        st.transition(C.S_COMPILING)
        st.approve_modules(["accessory module"])
        again = JobState.load(st.root)
        assert again.state == C.S_COMPILING
        assert again.approved_modules == ["accessory module"]

    def test_approved_modules_accumulate_without_duplicates(self, tmp_path):
        st = new_job(tmp_path)
        st.approve_modules(["accessory module"])
        st.approve_modules(["accessory module", "spec module"])
        assert st.approved_modules == ["accessory module", "spec module"]

    def test_transfer_attempt_counting(self, tmp_path):
        st = new_job(tmp_path)
        assert st.transfer_attempts("purple") == 0
        st.record_transfer("purple", 0, "/tmp/a.png")
        st.record_transfer("purple", 1, "/tmp/b.png")
        st.record_transfer("blue", 0, "/tmp/c.png")
        assert st.transfer_attempts("purple") == 2
        assert st.transfer_attempts("blue") == 1

    def test_latest_candidate_skips_backend_errors(self, tmp_path):
        st = new_job(tmp_path)
        r0 = st.allocate_round(ROUND_KIND_INITIAL)
        st.update_round(r0.index, candidate="/tmp/good.png")
        r1 = st.allocate_round(ROUND_KIND_REPAIR, repair_type="fix_text_error")
        st.update_round(r1.index, candidate=None, backend_error=True)
        # R4: the canvas for the next round is the last real image.
        assert str(st.latest_candidate()) == "/tmp/good.png"

    def test_update_round_rejects_unknown_field(self, tmp_path):
        st = new_job(tmp_path)
        rec = st.allocate_round(ROUND_KIND_INITIAL)
        with pytest.raises(StateError, match="unknown round fields"):
            st.update_round(rec.index, quality_score=9)


# --------------------------------------------------------------------------- #
# copy compiler (LLM node 4) + the number-traceability guard
#
# The guard exists because of a real incident: the validated 2026-07-11 run put
# "70 kPa" on the image when the product is 75 kPa, because the operator typed
# it into a follow-up instruction. Frozen copy is repeated verbatim on every
# round (R3), so a wrong figure spoils the whole job, not one image.
# --------------------------------------------------------------------------- #

REAL_LISTING = ("Aparat de Vidat si Sigilat Alimente, Excitat®, 120W, 75kpa, "
                "6-In-1, Functii Uscat/Umed/Vid Moale, cu 100 Pungi 17x20cm, "
                "30 cm bara de lipire, Cutter Incorporat, Sterilizare UV, "
                "Panou Control Tactil, Gri")


def listing_truth() -> dict:
    """The operator's real 2026-07-11 input: a marketplace listing title."""
    return {
        "operator_confirmed": {
            "title": REAL_LISTING, "raw_product_info": REAL_LISTING,
            "facts": [], "expected_offer": "host_with_accessories",
        },
        "source_visible_observations": {"visible_identity_text": []},
    }


class TestNumberTraceability:
    def test_the_2026_07_11_typo_is_caught(self):
        # The exact historical error.
        found = G1C.verify_numbers_traceable(
            [{"slot": "spec_primary", "text": "70 kPa"}], listing_truth())
        assert len(found) == 1
        # Reported with its unit, so the message names the actual defect.
        assert found[0]["number"] == "70 kPa"

    def test_every_real_slot_traces_to_the_listing_title(self):
        # The nine slots the model actually produced, against the title it saw.
        slots = [
            {"slot": "brand", "text": "EXCITAT"},
            {"slot": "headline", "text": "APARAT DE VIDAT"},
            {"slot": "badge", "text": "6 ÎN 1"},
            {"slot": "supporting_line", "text": "PENTRU PRODUSE USCATE ȘI UMEDE"},
            {"slot": "spec_primary", "text": "75 kPa"},
            {"slot": "spec_secondary", "text": "120 W"},
            {"slot": "offer", "text": "100 DE PUNGI INCLUSE"},
            {"slot": "feature", "text": "BARĂ DE SIGILARE DE 30 cm"},
            {"slot": "feature_optional", "text": "CUTTER ÎNCORPORAT • STERILIZARE UV"},
        ]
        assert G1C.verify_numbers_traceable(slots, listing_truth()) == []

    def test_spacing_and_case_do_not_defeat_the_match(self):
        # The title says "75kpa" and "120W"; the copy says "75 kPa" / "120 W".
        assert G1C.verify_numbers_traceable(
            [{"slot": "spec_primary", "text": "75 kPa"},
             {"slot": "spec_secondary", "text": "120 W"}], listing_truth()) == []

    def test_inflated_spec_is_caught(self):
        found = G1C.verify_numbers_traceable(
            [{"slot": "offer", "text": "200 DE PUNGI INCLUSE"}], listing_truth())
        assert found and found[0]["number"] == "200"  # bare count, no unit

    def test_invented_warranty_period_is_caught(self):
        found = G1C.verify_numbers_traceable(
            [{"slot": "feature", "text": "24 LUNI GARANTIE"}], listing_truth())
        assert found and found[0]["number"] == "24"  # LUNI is prose, not a unit

    def test_multiple_findings_are_all_reported(self):
        found = G1C.verify_numbers_traceable(
            [{"slot": "spec_primary", "text": "70 kPa"},
             {"slot": "spec_secondary", "text": "150 W"}], listing_truth())
        assert {f["number"] for f in found} == {"70 kPa", "150 W"}

    def test_non_numeric_copy_is_never_flagged(self):
        assert G1C.verify_numbers_traceable(
            [{"slot": "headline", "text": "APARAT DE VIDAT"}], listing_truth()) == []


class TestFreezeRefusesUntraceableCopy:
    def test_freeze_blocked_when_a_figure_is_untraceable(self):
        facts = G1C.compile_locked_fact_list(
            truth=listing_truth(), intent={"language": "ro"},
            request_slots=[{"slot": "brand", "text": "EXCITAT"},
                           {"slot": "headline", "text": "APARAT DE VIDAT"},
                           {"slot": "spec_primary", "text": "70 kPa"}])
        assert facts["unverified_numbers"]
        assert facts["needs_human_revision"] is True
        with pytest.raises(G1C.UntraceableNumber, match="70"):
            G1C.freeze_fact_list(facts)

    def test_human_can_explicitly_override(self):
        facts = G1C.compile_locked_fact_list(
            truth=listing_truth(), intent={"language": "ro"},
            request_slots=[{"slot": "brand", "text": "EXCITAT"},
                           {"slot": "headline", "text": "APARAT DE VIDAT"},
                           {"slot": "spec_primary", "text": "70 kPa"}])
        frozen = G1C.freeze_fact_list(facts, accept_unverified=True)
        assert frozen["frozen"] is True

    def test_clean_copy_freezes_without_ceremony(self):
        facts = G1C.compile_locked_fact_list(
            truth=listing_truth(), intent={"language": "ro"},
            request_slots=[{"slot": "brand", "text": "EXCITAT"},
                           {"slot": "headline", "text": "APARAT DE VIDAT"},
                           {"slot": "spec_primary", "text": "75 kPa"}])
        assert facts["unverified_numbers"] == []
        assert G1C.freeze_fact_list(facts)["frozen"] is True


class TestCopyCompilerNode:
    def test_dedupes_repeated_slots_and_drops_empties(self, monkeypatch):
        from workflow.reference_generation import describers

        def fake_call(prompt, images, schema, **kw):
            assert images == []  # the copy compiler must never see an image
            return {"copy_slots": [
                {"slot": "headline", "text": "APARAT DE VIDAT", "source": "title"},
                {"slot": "headline", "text": "ALTCEVA", "source": "title"},
                {"slot": "badge", "text": "   ", "source": ""},
                {"slot": "spec_primary", "text": "75 kPa", "source": "75kpa"},
            ], "dropped": ["Panou Control Tactil"], "notes": "led with the category"}

        monkeypatch.setattr(describers, "_call", fake_call)
        out = describers.compile_copy_slots(
            product_info=REAL_LISTING, facts=[], language="ro")
        slots = [s["slot"] for s in out["copy_slots"]]
        assert slots == ["headline", "spec_primary"]  # dedup + empty dropped
        assert out["dropped"] == ["Panou Control Tactil"]

    def test_requires_a_target_language(self):
        from workflow.reference_generation import describers
        with pytest.raises(ValueError, match="language"):
            describers.compile_copy_slots(product_info="x", facts=[], language="  ")

    def test_prompt_forbids_inventing_numbers(self):
        from workflow.reference_generation import describers
        # The strongest instruction in that prompt must not be softened away.
        assert "NEVER invent or adjust a number" in describers.COPY_PROMPT
        assert "do not put everything" in describers.COPY_PROMPT.lower() or \
               "must NOT carry every fact" in describers.COPY_PROMPT


class TestMeasuredAspectRatio:
    """The briefer once reported '32:41' for a 736x982 reference. Measure it."""

    def test_real_reference_shape_snaps_to_3_4(self, tmp_path):
        from PIL import Image
        p = tmp_path / "ref.jpg"
        Image.new("RGB", (736, 982)).save(p)          # the real export size
        assert G1C.measure_aspect_ratio(p) == "3:4"

    def test_square_is_reported_as_square(self, tmp_path):
        from PIL import Image
        p = tmp_path / "sq.png"
        Image.new("RGB", (1600, 1600)).save(p)
        assert G1C.measure_aspect_ratio(p) == "1:1"

    def test_four_five_is_not_confused_with_three_four(self, tmp_path):
        from PIL import Image
        p = tmp_path / "p.png"
        Image.new("RGB", (1080, 1350)).save(p)
        assert G1C.measure_aspect_ratio(p) == "4:5"

    def test_odd_shape_does_not_snap_to_a_designed_ratio(self, tmp_path):
        from PIL import Image
        p = tmp_path / "odd.png"
        Image.new("RGB", (1000, 300)).save(p)
        assert G1C.measure_aspect_ratio(p) not in {"1:1", "3:4", "4:3", "4:5"}


class TestAspectAdaptationClause:
    """3:4 reference -> 1:1 canvas is the PRODUCTION NORM, not an edge case:
    upstream exports ~750x1000 and the marketplace main image is square."""

    def test_the_production_case_gets_an_explicit_instruction(self):
        clause = T._aspect_adaptation_clause({"aspect_ratio": "3:4"}, "1:1")
        assert clause is not None
        assert "3:4" in clause and "1:1" in clause
        assert "wider and shorter" in clause
        # R5: adapting must never become cropping.
        assert "Do not crop" in clause
        assert "squeeze" in clause

    def test_no_clause_when_shapes_already_agree(self):
        assert T._aspect_adaptation_clause({"aspect_ratio": "1:1"}, "1:1") is None

    def test_taller_target_is_described_the_other_way(self):
        clause = T._aspect_adaptation_clause({"aspect_ratio": "1:1"}, "3:4")
        assert "taller and narrower" in clause

    def test_unparseable_ratio_is_skipped_not_crashed(self):
        assert T._aspect_adaptation_clause({"aspect_ratio": "wide-ish"}, "1:1") is None
        assert T._aspect_adaptation_clause({}, "1:1") is None

    def test_clause_reaches_the_init_prompt(self):
        facts = {"language": "ro", "copy_slots": [
            {"slot": "headline", "text": "APARAT DE VIDAT"}]}
        traits = {"product_visual_traits": ["black-and-silver body"]}
        brief = {"aspect_ratio": "3:4", "layout_skeleton": "vertical hero",
                 "color_mood": "warm kitchen", "composition_notes": "",
                 "modules": [], "donor_brand": "", "donor_language": ""}
        prompt = T.compile_init(
            images=[T.InputImage(C.ROLE_DESIGN_MASTER, "/tmp/a.jpg"),
                    T.InputImage(C.ROLE_APPEARANCE_ANCHOR, "/tmp/b.png")],
            facts=facts, traits=traits, brief=brief, canvas="1:1",
            brand="EXCITAT", product_short_name="vacuum sealer")
        assert "the design reference is 3:4 while our canvas is 1:1" in prompt.text


class TestNumberVerifierRegressions:
    """Every case an independent review found the substring version passing."""

    def _flag(self, copy: str, truth_text: str) -> bool:
        truth = {"operator_confirmed": {"title": truth_text,
                                        "raw_product_info": "", "facts": []}}
        return bool(G1C.verify_numbers_traceable([{"slot": "s", "text": copy}], truth))

    def test_decimal_is_not_flattened_into_a_different_number(self):
        # "7.5" once normalised to "75" and matched a truth pack with only 75 kPa.
        assert self._flag("7.5 W", "75 kPa")

    def test_thousands_separator_is_not_a_false_positive(self):
        assert not self._flag("1000 W", "1,000 W")
        assert not self._flag("1000 W", "1.000 W")   # ro/de grouping

    def test_a_figure_inside_a_longer_number_does_not_count(self):
        # "75" is a substring of SKU "X7500" but is not that value.
        assert self._flag("75 W", "model X7500")

    def test_right_value_wrong_unit_is_caught(self):
        assert self._flag("75 W", "75 kPa and 120 W is wrong pairing")

    def test_bare_count_matches_on_value_alone(self):
        # "100 DE PUNGI" -- the noun carries the meaning, not a unit.
        assert not self._flag("100 DE PUNGI INCLUSE", "cu 100 Pungi 17x20cm")

    def test_dimension_pair_survives(self):
        assert not self._flag("100 PUNGI 17x20 cm INCLUSE", "cu 100 Pungi 17x20cm")

    def test_the_whole_real_copy_set_passes(self):
        real = ("Aparat de Vidat si Sigilat Alimente, Excitat®, 120W, 75kpa, "
                "6-In-1, cu 100 Pungi 17x20cm, 30 cm bara de lipire")
        for line in ("75 kPa", "120 W", "6-ÎN-1", "BARĂ DE LIPIRE 30 cm",
                     "100 PUNGI 17x20 cm INCLUSE"):
            assert not self._flag(line, real), line


class TestNumberVerifierSecondReviewRegressions:
    """Cases a second independent review found after the first round of fixes."""

    REAL = ("Aparat de Vidat, Excitat®, 120W, 75kpa, 6-In-1, "
            "cu 100 Pungi 17x20cm, 30 cm bara de lipire")

    def _flag(self, copy: str) -> bool:
        truth = {"operator_confirmed": {"title": self.REAL,
                                        "raw_product_info": "", "facts": []}}
        return bool(G1C.verify_numbers_traceable([{"slot": "s", "text": copy}], truth))

    def test_dimension_after_x_is_extracted_from_the_truth(self):
        # With a \w boundary the "20cm" in "17x20cm" was swallowed, so the
        # product's own bag width could not be quoted.
        assert (20.0, "cm") in {(v, u) for v, u, _ in G1C._quantities(self.REAL)}
        assert not self._flag("PUNGI DE 20 cm")

    def test_a_bare_value_does_not_license_an_arbitrary_unit(self):
        # "6-In-1" puts a bare 6 in the truth pack. That must not make "6 W" --
        # a tenfold understatement of the real 120 W -- traceable.
        assert self._flag("DOAR 6 W CONSUM")
        assert self._flag("17 cm LATIME")
        assert self._flag("1 AN GARANTIE")

    def test_unit_spelled_out_is_the_same_unit(self):
        # The listing writes "120W"; printed copy may reasonably say "120 Watt".
        assert not self._flag("PUTERE 120 Watt")
        assert not self._flag("PUTERE 120 W")

    def test_a_different_unit_is_still_a_different_claim(self):
        # Alias folding must not become unit conversion.
        assert self._flag("75 W")
        assert self._flag("120 kPa")

    def test_unit_conversion_is_rejected_by_design(self):
        # 0.12 kW is arithmetically 120 W, but the copy compiler is told never to
        # convert: a converted figure is a different printed claim, and the
        # operator's own wording is what we can defend.
        assert self._flag("0.12 kW")

    def test_non_string_text_does_not_crash_the_verifier(self):
        truth = {"operator_confirmed": {"title": self.REAL}}
        assert G1C.verify_numbers_traceable([{"slot": "s", "text": 75}], truth) == []
        assert G1C.verify_numbers_traceable([{"slot": "s", "text": None}], truth) == []


class TestJudgeKnowsTheCanvasContract:
    """Regression from the 2026-07-30 v2 run.

    Shown a 3:4 reference and a correct 1:1 candidate, the judge chose
    recompose_aspect and asked to reshape the square into a portrait "to follow
    the reference's vertical flow". It had never been told the target canvas, so
    the only shape it could compare against was the reference's. R5 says the
    target canvas is a first-class parameter, independent of the reference.
    """

    def test_prompt_states_the_canvas_is_independent_of_the_reference(self):
        from workflow.reference_generation import describers
        p = describers.JUDGE_PROMPT
        assert "{canvas}" in p and "{measured}" in p
        assert "INDEPENDENT of the reference" in p
        assert "is not a defect" in p

    def test_judge_forwards_canvas_and_measurement(self, monkeypatch):
        from workflow.reference_generation import describers
        seen = {}

        def fake_call(prompt, images, schema, **kw):
            seen["prompt"] = prompt
            return {"repair": "add_breathing_room", "prompt_delta": "x" * 250,
                    "fact_violations": [], "product_integrity_ok": True,
                    "stop_recommended": False, "reason": "r"}

        monkeypatch.setattr(describers, "_call", fake_call)
        describers.judge_candidate(
            "/tmp/c.png", "/tmp/r.jpg",
            facts={"copy_slots": [{"slot": "brand", "text": "EXCITAT"}]},
            traits={"product_visual_traits": ["black body"]},
            repairs_used=0, round_budget=8,
            canvas="1:1", measured_aspect="1.000 (1600x1600)")
        # The prompt is hard-wrapped, so compare on normalised whitespace.
        flat = " ".join(seen["prompt"].split())
        assert "The target canvas is 1:1" in flat
        assert "1.000 (1600x1600)" in flat
        assert "Only choose recompose_aspect if the candidate itself is NOT 1:1" \
            in flat

    def test_donor_claims_reach_the_judge(self, monkeypatch):
        from workflow.reference_generation import describers
        seen = {}

        def fake_call(prompt, images, schema, **kw):
            seen["prompt"] = prompt
            return {"repair": "reduce_clutter", "prompt_delta": "x" * 250,
                    "fact_violations": [], "product_integrity_ok": True,
                    "stop_recommended": False, "reason": "r"}

        monkeypatch.setattr(describers, "_call", fake_call)
        describers.judge_candidate(
            "/tmp/c.png", "/tmp/r.jpg",
            facts={"copy_slots": [{"slot": "brand", "text": "EXCITAT"}]},
            traits={"product_visual_traits": ["black body"]},
            repairs_used=0, round_budget=8,
            donor_claims=["1 год гарантии", "20 пакетов в подарок"])
        # The judge is the only place that can see a donor claim reproduced in
        # the render, so it has to know what they were.
        assert "1 год гарантии" in seen["prompt"]
        assert "20 пакетов в подарок" in seen["prompt"]
