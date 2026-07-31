from __future__ import annotations

import pathlib
import sys

from PIL import Image

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import confirmed_reference_matcher as crm
import hybrid_reference_matcher as hm


def _row(
    asset_id: str,
    *,
    shape_family: str,
    layout_family: str,
    offer_structure: str,
    proof_mode: str,
    scene_role: str,
    density: str,
    composition_skeleton: str = "centered_symmetry",
    template_candidate_score: int = 80,
    source_kind: str = "ozon_seed16",
    source_path: str | None = None,
    direct_match_ready: bool = True,
    template_match_ready: bool = True,
    match_lane: str = "direct_and_template",
    fingerprint: dict | None = None,
) -> dict:
    row = {
        "asset_id": asset_id,
        "library_path": f"/tmp/{asset_id}.jpg",
        "source_path": source_path or f"/tmp/{asset_id}.jpg",
        "source_kind": source_kind,
        "shape_family": shape_family,
        "layout_family": layout_family,
        "composition_skeleton": composition_skeleton,
        "offer_structure": offer_structure,
        "proof_mode": proof_mode,
        "scene_role": scene_role,
        "density": density,
        "template_candidate_score": template_candidate_score,
        "direct_match_ready": direct_match_ready,
        "template_match_ready": template_match_ready,
        "match_lane": match_lane,
        "match_keywords": [asset_id, shape_family, layout_family, offer_structure, proof_mode, scene_role],
    }
    if fingerprint is not None:
        row["_fingerprint"] = fingerprint
    return row


def _fp(seed: int) -> dict:
    """A deterministic synthetic fingerprint that varies with seed."""
    bits = "".join("1" if (seed >> (i % 8)) & 1 else "0" for i in range(64))
    color = [0.0] * 512
    color[seed % 512] = 1.0
    edge = [0.0] * 16
    edge[seed % 16] = 1.0
    return {"dhash": bits, "color": color, "edge": edge}


QUERY = {
    "query_id": "q1",
    "title": "Vacuum sealer machine with food bags",
    "category": "home appliance",
    "keywords": ["vacuum", "sealer"],
    "offer_hint": "single_product",
    "shape_hint": "wide_low",
    "scene_hint": "result_or_food_scene",
    "skeleton_hint": "wide_low_banner",
}


def test_scheme_A_ranking_matches_baseline_overall():
    """Scheme A (structure-only) should rank identically to confirmed_reference_matcher overall."""
    rows = [
        _row("good", shape_family="wide_low", layout_family="wide_low_banner",
             offer_structure="single_product", proof_mode="numeric_banner",
             scene_role="graphic_or_shallow_scene", density="low", template_candidate_score=88),
        _row("bad", shape_family="installed", layout_family="installed_relation_layout",
             offer_structure="installed_relation", proof_mode="installation_relation",
             scene_role="mounted_host_scene", density="medium", template_candidate_score=85),
    ]
    # baseline
    base = crm.match_query(QUERY, rows, top_n=2)
    base_order = [r["asset_id"] for r in base["top_overall"]]
    # scheme A
    res = hm.match_query(QUERY, rows, scheme="A", top_n=2)
    a_order = [r["asset_id"] for r in res["top"]]
    assert a_order == base_order


def test_scheme_A_layer_detail_present():
    rows = [_row("only", shape_family="wide_low", layout_family="wide_low_banner",
                 offer_structure="single_product", proof_mode="numeric_banner",
                 scene_role="graphic_or_shallow_scene", density="low")]
    res = hm.match_query(QUERY, rows, scheme="A", top_n=1)
    item = res["top"][0]
    assert "layers" in item
    assert set(item["layers"]) >= {"offer", "shape", "scene", "layout", "overall"}
    assert "visual" not in item["layers"]
    assert "skeleton" not in item["layers"]


def test_scheme_B_uses_visual_recall_to_break_tie():
    """Two structurally identical rows: the one closer to the query image wins under scheme B."""
    query_fp = _fp(0)
    close = _fp(0)   # identical fingerprint -> distance 0
    far = _fp(7)     # very different fingerprint
    rows = [
        _row("close", shape_family="wide_low", layout_family="wide_low_banner",
             offer_structure="single_product", proof_mode="numeric_banner",
             scene_role="result_or_food_scene", density="low", fingerprint=close),
        _row("far", shape_family="wide_low", layout_family="wide_low_banner",
             offer_structure="single_product", proof_mode="numeric_banner",
             scene_role="result_or_food_scene", density="low", fingerprint=far),
    ]
    res = hm.match_query(QUERY, rows, scheme="B", top_n=2, query_fingerprint=query_fp)
    assert res["top"][0]["asset_id"] == "close"
    assert "visual" in res["top"][0]["layers"]


def test_scheme_C_uses_skeleton_recall():
    """A row whose composition_skeleton matches the query skeleton_hint scores higher."""
    rows = [
        _row("skel-match", shape_family="wide_low", layout_family="wide_low_banner",
             offer_structure="single_product", proof_mode="numeric_banner",
             scene_role="result_or_food_scene", density="low",
             composition_skeleton="wide_low_banner"),
        _row("skel-miss", shape_family="wide_low", layout_family="wide_low_banner",
             offer_structure="single_product", proof_mode="numeric_banner",
             scene_role="result_or_food_scene", density="low",
             composition_skeleton="centered_symmetry"),
    ]
    res = hm.match_query(QUERY, rows, scheme="C", top_n=2)
    assert res["top"][0]["asset_id"] == "skel-match"
    assert "skeleton" in res["top"][0]["layers"]


def test_scheme_D_supports_weight_presets():
    rows = [_row("only", shape_family="wide_low", layout_family="wide_low_banner",
                 offer_structure="single_product", proof_mode="numeric_banner",
                 scene_role="result_or_food_scene", density="low",
                 composition_skeleton="wide_low_banner", fingerprint=_fp(0))]
    query_fp = _fp(0)
    for preset in ("struct_heavy", "balanced", "image_heavy"):
        res = hm.match_query(QUERY, rows, scheme="D", top_n=1,
                             preset=preset, query_fingerprint=query_fp)
        assert res["top"][0]["asset_id"] == "only"
        assert res["scheme"] == "D"
        assert res["weights"]["__preset__"] == preset


def test_visual_similarity_one_for_identical_fingerprints():
    a = _fp(3)
    assert hm.visual_similarity(a, a) == 1.0


def test_match_query_returns_lane_per_candidate():
    rows = [
        _row("direct", shape_family="wide_low", layout_family="wide_low_banner",
             offer_structure="single_product", proof_mode="numeric_banner",
             scene_role="result_or_food_scene", density="low",
             direct_match_ready=True, match_lane="direct_and_template"),
        _row("tmpl", shape_family="wide_low", layout_family="wide_low_banner",
             offer_structure="single_product", proof_mode="numeric_banner",
             scene_role="result_or_food_scene", density="low",
             direct_match_ready=False, template_match_ready=True, match_lane="template_only",
             source_kind="xhs_notes_deep_images"),
    ]
    res = hm.match_query(QUERY, rows, scheme="A", top_n=2)
    lanes = {r["asset_id"]: r["lane"] for r in res["top"]}
    assert lanes["direct"] == "direct"
    assert lanes["tmpl"] == "pattern"


def test_reasons_explain_promoted_candidate():
    rows = [_row("only", shape_family="wide_low", layout_family="wide_low_banner",
                 offer_structure="single_product", proof_mode="numeric_banner",
                 scene_role="result_or_food_scene", density="low")]
    res = hm.match_query(QUERY, rows, scheme="A", top_n=1)
    assert isinstance(res["top"][0]["reasons"], list)


def test_diversity_caps_per_note_repetition():
    """A single xhs note with many pages must not monopolise the Top-N.

    With 8 near-identical pages from one note and no diversification, all 8
    would occupy the top of the ranking. With the per-note cap (2) plus a
    refill that still respects a relaxed cap, at most a few of those pages
    survive into Top-N and the distinct direct candidate must surface.
    """
    rows = []
    for i in range(8):
        rows.append(_row(
            f"xhs_04-abc123456789_{i:03d}",
            shape_family="wide_low", layout_family="wide_low_banner",
            offer_structure="single_product", proof_mode="numeric_banner",
            scene_role="result_or_food_scene", density="low",
            direct_match_ready=False, template_match_ready=True,
            match_lane="template_only", source_kind="xhs_notes_deep_images",
            template_candidate_score=90,
        ))
    # one direct candidate that ranks below the 8 pages on raw score
    rows.append(_row("direct1", shape_family="wide_low", layout_family="wide_low_banner",
                     offer_structure="single_product", proof_mode="numeric_banner",
                     scene_role="result_or_food_scene", density="low",
                     template_candidate_score=70))
    res = hm.match_query(QUERY, rows, scheme="A", top_n=5)
    assets = [r["asset_id"] for r in res["top"]]
    note_members = [a for a in assets if a.startswith("xhs_04-abc123456789")]
    # Cap is 2 strict, up to 3 with relaxed refill -> never the full 8
    assert len(note_members) <= 4, f"per-note cap violated: {note_members}"
    assert len(note_members) < 8, "note monopoly not broken"
    assert "direct1" in assets, "direct candidate should surface once notes are capped"
