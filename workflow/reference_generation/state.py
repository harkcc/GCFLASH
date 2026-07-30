#!/usr/bin/env python3
"""State machine and immutable round ledger for the G1 workflow (SPEC §3, §4.2).

Artifact layout (R12 -- one directory per round, never overwritten)::

    generation_runs/<job_id>/<product_id>/
      request/generation_request.json
      compiled/{locked_fact_list,immutable_traits,reference_design_brief,
                negative_constraints}.json
      round_00_initial/        prompt.md inputs.json candidate.png candidate_meta.json
      round_01_recompose/      ...
      round_NN_<repair_type>/  ... judge_decision.json human_decision.json
      anchor/anchor.png anchor/anchor_meta.json
      style_transfers/<ref_id>/...
      state.json

Budget accounting (interpretation of R9, recorded here because the SPEC's
wording admits two readings): R9 says the default 8 rounds exclude round_00.
§3 places the optional recompose round inside the ``generating_initial`` state
rather than the repair loop, and the "budget 8" annotation sits on the
``repairing`` loop. So the budget is consumed by REPAIR rounds only. Rounds that
do not count, and why:

- ``round_00_initial`` / ``round_01_recompose`` -- initial generation, not repair;
- a round the backend failed to produce (``backend_error``) -- §6 says explicitly
  it does not consume budget;
- a forced product-integrity restore (§7, ``product_integrity_ok=false``) --
  §7 says "本轮不算修补".
"""
from __future__ import annotations

import copy
import dataclasses
import json
import pathlib
import time

from . import contracts as C


class StateError(RuntimeError):
    """Illegal state transition or budget violation."""


ROUND_KIND_INITIAL = "initial"
ROUND_KIND_RECOMPOSE = "recompose"
ROUND_KIND_REPAIR = "repair"
ROUND_KINDS = frozenset({ROUND_KIND_INITIAL, ROUND_KIND_RECOMPOSE, ROUND_KIND_REPAIR})


@dataclasses.dataclass
class RoundRecord:
    index: int
    kind: str
    dirname: str
    repair_type: str | None = None
    consumed_budget: bool = False
    backend_error: bool = False
    integrity_restore: bool = False
    candidate: str | None = None
    prompt_sha256: str | None = None
    created_at: str = dataclasses.field(
        default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S%z"))
    judge_decision: dict | None = None
    human_decision: dict | None = None

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> RoundRecord:
        known = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in known})


class JobState:
    """Reads/writes ``state.json`` and owns every state transition."""

    FILENAME = "state.json"

    def __init__(self, root: pathlib.Path, data: dict):
        self.root = pathlib.Path(root)
        self._data = data

    # -- lifecycle ---------------------------------------------------------- #

    @classmethod
    def create(cls, root: pathlib.Path, *, product_id: str, job_id: str,
               round_budget: int = C.DEFAULT_ROUND_BUDGET,
               review_mode: str = "required",
               intent: dict | None = None) -> JobState:
        root = pathlib.Path(root)
        if (root / cls.FILENAME).exists():
            raise StateError(
                f"{root / cls.FILENAME} already exists; a rerun must use a new "
                f"directory (R12)")
        if review_mode != "required":
            # R10: V1 has no automatic mode. Refuse rather than silently degrade.
            raise StateError(
                f"review_mode={review_mode!r} is not allowed in V1; only "
                f"'required' (R10)")
        root.mkdir(parents=True, exist_ok=True)
        data = {
            "job_id": job_id,
            "product_id": product_id,
            "state": C.S_QUEUED,
            "round_budget": int(round_budget),
            "review_mode": review_mode,
            "intent": intent or {},
            "rounds": [],
            "approved_modules": [],
            "style_transfers": [],
            "anchor": None,
            "history": [],
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        st = cls(root, data)
        st._log(None, C.S_QUEUED, "job created")
        st.save()
        return st

    @classmethod
    def load(cls, root: pathlib.Path) -> JobState:
        path = pathlib.Path(root) / cls.FILENAME
        if not path.is_file():
            raise StateError(f"no state.json under {root}")
        return cls(pathlib.Path(root), json.loads(path.read_text(encoding="utf-8")))

    def save(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / self.FILENAME).write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")

    # -- accessors ---------------------------------------------------------- #

    @property
    def state(self) -> str:
        return self._data["state"]

    @property
    def data(self) -> dict:
        return copy.deepcopy(self._data)

    @property
    def rounds(self) -> list[RoundRecord]:
        return [RoundRecord.from_dict(r) for r in self._data["rounds"]]

    @property
    def approved_modules(self) -> list[str]:
        return list(self._data["approved_modules"])

    @property
    def round_budget(self) -> int:
        return int(self._data["round_budget"])

    @property
    def repairs_used(self) -> int:
        return sum(1 for r in self._data["rounds"] if r.get("consumed_budget"))

    @property
    def budget_remaining(self) -> int:
        return max(0, self.round_budget - self.repairs_used)

    @property
    def budget_exhausted(self) -> bool:
        return self.budget_remaining <= 0

    def latest_candidate(self) -> pathlib.Path | None:
        """The current canvas: newest round that actually produced an image (R4)."""
        for r in reversed(self._data["rounds"]):
            if r.get("candidate") and not r.get("backend_error"):
                return pathlib.Path(r["candidate"])
        return None

    # -- transitions -------------------------------------------------------- #

    def transition(self, new_state: str, note: str = "") -> None:
        current = self.state
        allowed = C.TRANSITIONS.get(current, frozenset())
        if new_state == current:
            return
        if new_state not in allowed:
            raise StateError(
                f"illegal transition {current} -> {new_state}; allowed from "
                f"{current}: {sorted(allowed) or 'none (terminal)'}")
        self._data["state"] = new_state
        self._log(current, new_state, note)
        self.save()

    def _log(self, old: str | None, new: str, note: str) -> None:
        self._data.setdefault("history", []).append({
            "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "from": old, "to": new, "note": note,
        })

    # -- round allocation --------------------------------------------------- #

    def allocate_round(self, kind: str, *, repair_type: str | None = None,
                       integrity_restore: bool = False) -> RoundRecord:
        """Create the next round directory and ledger entry.

        Raises StateError when the budget is exhausted, so a caller cannot
        quietly keep generating rounds past R9.
        """
        if kind not in ROUND_KINDS:
            raise StateError(f"unknown round kind {kind!r}")
        if kind == ROUND_KIND_REPAIR:
            if repair_type not in C.REPAIR_MENU:
                raise StateError(
                    f"repair_type {repair_type!r} is not in the repair menu (R8)")
            # An integrity restore is free (§7); a real repair costs budget (R9).
            costs_budget = not integrity_restore
            if costs_budget and self.budget_exhausted:
                raise StateError(
                    f"round budget exhausted ({self.repairs_used}/"
                    f"{self.round_budget}); job must go to {C.S_NEEDS_MANUAL} (R9)")
        else:
            costs_budget = False

        index = len(self._data["rounds"])
        if kind == ROUND_KIND_INITIAL:
            dirname = f"round_{index:02d}_initial"
        elif kind == ROUND_KIND_RECOMPOSE:
            dirname = f"round_{index:02d}_recompose"
        else:
            suffix = "integrity_restore" if integrity_restore else repair_type
            dirname = f"round_{index:02d}_{suffix}"

        rd = self.root / dirname
        if rd.exists():
            raise StateError(f"round directory {rd} already exists (R12)")
        rd.mkdir(parents=True)

        rec = RoundRecord(index=index, kind=kind, dirname=dirname,
                          repair_type=repair_type, consumed_budget=costs_budget,
                          integrity_restore=integrity_restore)
        self._data["rounds"].append(rec.to_dict())
        self.save()
        return rec

    def round_dir(self, rec: RoundRecord) -> pathlib.Path:
        return self.root / rec.dirname

    def update_round(self, index: int, **fields) -> None:
        if not 0 <= index < len(self._data["rounds"]):
            raise StateError(f"no round at index {index}")
        rec = self._data["rounds"][index]
        known = {f.name for f in dataclasses.fields(RoundRecord)}
        unknown = set(fields) - known
        if unknown:
            raise StateError(f"unknown round fields: {sorted(unknown)}")
        rec.update(fields)
        # §6: a round the backend failed on must not consume budget.
        if fields.get("backend_error"):
            rec["consumed_budget"] = False
        self.save()

    # -- approved modules (§5.6 mechanism 4) -------------------------------- #

    def approve_modules(self, modules: list[str]) -> None:
        cur = self._data["approved_modules"]
        for m in modules:
            m = (m or "").strip()
            if m and m not in cur:
                cur.append(m)
        self.save()

    # -- anchor / style transfer -------------------------------------------- #

    def set_anchor(self, anchor_png: pathlib.Path, source_round: int) -> None:
        self._data["anchor"] = {
            "path": str(anchor_png), "source_round": source_round,
            "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        self.save()

    @property
    def anchor(self) -> dict | None:
        return self._data.get("anchor")

    def record_transfer(self, ref_id: str, attempt: int, candidate: str,
                        decision: dict | None = None) -> None:
        self._data.setdefault("style_transfers", []).append({
            "ref_id": ref_id, "attempt": attempt, "candidate": candidate,
            "decision": decision,
            "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        })
        self.save()

    def transfer_attempts(self, ref_id: str) -> int:
        return sum(1 for t in self._data.get("style_transfers", [])
                   if t.get("ref_id") == ref_id)

    # -- reporting ---------------------------------------------------------- #

    def summary(self) -> dict:
        return {
            "job_id": self._data["job_id"],
            "product_id": self._data["product_id"],
            "state": self.state,
            "rounds_total": len(self._data["rounds"]),
            "repairs_used": self.repairs_used,
            "round_budget": self.round_budget,
            "budget_remaining": self.budget_remaining,
            "approved_modules": self.approved_modules,
            "anchor": self._data.get("anchor"),
            "latest_candidate": (str(self.latest_candidate())
                                 if self.latest_candidate() else None),
        }
