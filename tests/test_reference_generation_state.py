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
