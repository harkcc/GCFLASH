#!/usr/bin/env python3
"""Frozen vocabulary for the G1 reference-generation workflow.

Everything here encodes a SPEC clause. Changing a value here changes a frozen
decision (SPEC §2) and must not be done to "make something pass".
"""
from __future__ import annotations

# --- image roles (R1) -------------------------------------------------------
ROLE_DESIGN_MASTER = "design_master"
ROLE_APPEARANCE_ANCHOR = "product_appearance_anchor"
ROLE_ACCESSORIES_EVIDENCE = "accessories_evidence"
ROLE_NATIVE_TEXT_EVIDENCE = "native_text_evidence"
ROLE_MODULE_INSPIRATION = "module_inspiration"
ROLE_PREVIOUS_CANVAS = "previous_canvas"
ROLE_STYLE_ANCHOR = "style_anchor"

VALID_ROLES = frozenset({
    ROLE_DESIGN_MASTER, ROLE_APPEARANCE_ANCHOR, ROLE_ACCESSORIES_EVIDENCE,
    ROLE_NATIVE_TEXT_EVIDENCE, ROLE_MODULE_INSPIRATION, ROLE_PREVIOUS_CANVAS,
    ROLE_STYLE_ANCHOR,
})

# Roles the caller may supply in generation_request.product_images (§4.1).
REQUEST_PRODUCT_IMAGE_ROLES = frozenset({
    ROLE_APPEARANCE_ANCHOR, ROLE_ACCESSORIES_EVIDENCE, ROLE_NATIVE_TEXT_EVIDENCE,
})

# --- repair menu (§7) -------------------------------------------------------
# repair_type -> extra image roles that repair is allowed to attach.
# The previous round's output is always attached and is not listed here (R4).
REPAIR_MENU: dict[str, frozenset[str]] = {
    "recompose_aspect": frozenset(),
    "complete_accessories": frozenset({ROLE_ACCESSORIES_EVIDENCE,
                                       ROLE_NATIVE_TEXT_EVIDENCE}),
    "increase_product_dominance": frozenset(),
    "amplify_spec_impact": frozenset(),
    "redesign_accessory_module": frozenset({ROLE_MODULE_INSPIRATION}),
    "redesign_spec_module": frozenset({ROLE_MODULE_INSPIRATION}),
    "add_breathing_room": frozenset(),
    "fix_text_error": frozenset(),
    "replace_claim_text": frozenset(),
    "reduce_clutter": frozenset(),
}

# repair types that may attach at most ONE extra image (§7: "1 张模块级灵感图")
SINGLE_EXTRA_IMAGE_REPAIRS = frozenset({
    "redesign_accessory_module", "redesign_spec_module",
})

# --- negative constraints (R6) ---------------------------------------------
# Rendered verbatim into every prompt of every round. Do not reword per round.
NEGATIVE_CONSTRAINTS_SENTENCE = (
    "Do not add warranty, certifications, testimonials, prices, fake logos, or "
    "unsupported claims. Do not add any text not listed above, except text that "
    "is natively printed on the product body itself. No watermark."
)

# The individual bans R6 enumerates, kept machine-readable for audit/tests.
NEGATIVE_CONSTRAINT_ITEMS = (
    "no donor brand", "no donor language script", "no warranty", "no price",
    "no certifications", "no testimonials", "no fake logos",
    "no unsupported claims", "no watermark",
)

# --- states (§3) ------------------------------------------------------------
S_QUEUED = "queued"
S_COMPILING = "compiling"
S_GENERATING_INITIAL = "generating_initial"
S_AWAITING_ROUND_REVIEW = "awaiting_round_review"
S_REPAIRING = "repairing"
S_CONVERGED = "converged"
S_NEEDS_MANUAL = "needs_manual"
S_INCOMPLETE_TRUTH = "incomplete_truth"
S_NEEDS_USER_INPUT = "needs_user_input"
S_AWAITING_TRANSFER_REVIEW = "awaiting_transfer_review"
S_TRANSFER_DONE = "transfer_done"

TERMINAL_STATES = frozenset({S_CONVERGED, S_NEEDS_MANUAL, S_INCOMPLETE_TRUTH,
                             S_TRANSFER_DONE})

# Legal transitions. Anything not listed is rejected (§9 test 9).
TRANSITIONS: dict[str, frozenset[str]] = {
    S_QUEUED: frozenset({S_COMPILING, S_INCOMPLETE_TRUTH}),
    S_COMPILING: frozenset({S_GENERATING_INITIAL, S_INCOMPLETE_TRUTH,
                            S_NEEDS_USER_INPUT}),
    S_GENERATING_INITIAL: frozenset({S_AWAITING_ROUND_REVIEW, S_NEEDS_MANUAL}),
    S_AWAITING_ROUND_REVIEW: frozenset({S_REPAIRING, S_CONVERGED, S_NEEDS_MANUAL,
                                        S_NEEDS_USER_INPUT}),
    S_REPAIRING: frozenset({S_AWAITING_ROUND_REVIEW, S_NEEDS_MANUAL,
                            S_NEEDS_USER_INPUT}),
    S_NEEDS_USER_INPUT: frozenset({S_REPAIRING, S_AWAITING_ROUND_REVIEW,
                                   S_NEEDS_MANUAL}),
    # converged is terminal for the loop, but style transfer may run repeatedly
    S_CONVERGED: frozenset({S_AWAITING_TRANSFER_REVIEW}),
    S_AWAITING_TRANSFER_REVIEW: frozenset({S_TRANSFER_DONE, S_CONVERGED,
                                           S_NEEDS_MANUAL}),
    S_TRANSFER_DONE: frozenset({S_AWAITING_TRANSFER_REVIEW, S_CONVERGED}),
    S_NEEDS_MANUAL: frozenset(),
    S_INCOMPLETE_TRUTH: frozenset(),
}

# --- misc -------------------------------------------------------------------
DEFAULT_ROUND_BUDGET = 8  # R9, excludes round_00
MAX_TRANSFER_RETRIES = 2  # §5.5

LANGUAGE_NAMES = {
    "ro": "Romanian", "ru": "Russian", "en": "English", "de": "German",
    "pl": "Polish", "es": "Spanish", "fr": "French", "it": "Italian",
    "hu": "Hungarian", "cs": "Czech", "bg": "Bulgarian", "uk": "Ukrainian",
    "kk": "Kazakh", "zh": "Chinese",
}

ORDINALS = ("FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH")


def language_name(code: str) -> str:
    """Human-readable language name for prompt text."""
    return LANGUAGE_NAMES.get((code or "").lower(), (code or "").upper())


def ordinal(index: int) -> str:
    """0-based index -> FIRST/SECOND/... for image role declarations."""
    if 0 <= index < len(ORDINALS):
        return ORDINALS[index]
    return f"#{index + 1}"
