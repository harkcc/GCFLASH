from __future__ import annotations

import json
import pathlib
import sys

import pytest
from PIL import Image

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pil_fingerprints as fp


def _make_image(path: pathlib.Path, mode: str, color, size=(64, 64)) -> None:
    Image.new(mode, size, color).save(path)


def test_dhash_identical_images_zero_distance(tmp_path):
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    _make_image(a, "RGB", (120, 30, 200))
    _make_image(b, "RGB", (120, 30, 200))
    ha = fp.dhash(a)
    hb = fp.dhash(b)
    assert ha == hb
    assert fp.hamming(ha, hb) == 0


def test_dhash_different_images_nonzero_distance(tmp_path):
    solid = tmp_path / "solid.png"
    half = tmp_path / "half.png"
    _make_image(solid, "RGB", (200, 200, 200))
    # Split image: left half dark, right half light -> different dHash
    img = Image.new("RGB", (64, 64), (10, 10, 10))
    right = Image.new("RGB", (32, 64), (240, 240, 240))
    img.paste(right, (32, 0))
    img.save(half)
    assert fp.hamming(fp.dhash(solid), fp.dhash(half)) > 0


def test_color_hist_stable_and_512_length(tmp_path):
    p = tmp_path / "c.png"
    _make_image(p, "RGB", (255, 0, 0))
    hist1 = fp.color_hist(p)
    hist2 = fp.color_hist(p)
    assert len(hist1) == 512  # 8 bins * 8 bins * 8 bins joint cube
    assert hist1 == hist2
    # Pure red lands entirely in the (r=7, g=0, b=0) joint bin -> index 7*64 = 448
    assert hist1[7 * 64] == 1.0
    assert sum(hist1) == pytest.approx(1.0)


def test_color_hist_intersection_identical(tmp_path):
    p = tmp_path / "c.png"
    _make_image(p, "RGB", (10, 20, 30))
    h = fp.color_hist(p)
    # intersection distance of identical histograms == 0
    assert fp.hist_distance(h, h) == 0.0


def test_edge_grid_returns_16_values_and_normalized(tmp_path):
    p = tmp_path / "e.png"
    _make_image(p, "RGB", (255, 255, 255))
    grid = fp.edge_grid(p)
    assert len(grid) == 16
    # Grid is a distribution that sums to 1.0 (or 0 if totally empty)
    assert sum(grid) == pytest.approx(1.0) or sum(grid) == 0.0


def test_fingerprint_combines_all_three(tmp_path):
    p = tmp_path / "f.png"
    _make_image(p, "RGB", (50, 100, 150))
    fingerprint = fp.fingerprint(p)
    assert set(fingerprint.keys()) == {"dhash", "color", "edge"}
    assert len(fingerprint["color"]) == 512
    assert len(fingerprint["edge"]) == 16
    assert isinstance(fingerprint["dhash"], str) and len(fingerprint["dhash"]) == 64


def test_fp_distance_zero_for_identical(tmp_path):
    p = tmp_path / "f.png"
    _make_image(p, "RGB", (50, 100, 150))
    f = fp.fingerprint(p)
    assert fp.fp_distance(f, f) == 0.0


def test_fp_distance_positive_and_normalized(tmp_path):
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    _make_image(a, "RGB", (255, 255, 255))
    img = Image.new("RGB", (64, 64), (10, 10, 10))
    right = Image.new("RGB", (32, 64), (240, 240, 240))
    img.paste(right, (32, 0))
    img.save(b)
    fa = fp.fingerprint(a)
    fb = fp.fingerprint(b)
    d = fp.fp_distance(fa, fb)
    assert 0.0 < d <= 1.0


def test_visual_similarity_one_for_identical(tmp_path):
    p = tmp_path / "f.png"
    _make_image(p, "RGB", (50, 100, 150))
    f = fp.fingerprint(p)
    assert fp.visual_similarity(f, f) == 1.0


def test_build_cache_writes_and_is_idempotent(tmp_path):
    img = tmp_path / "x.png"
    _make_image(img, "RGB", (30, 60, 90))
    rows = [{"asset_id": "r1", "library_path": str(img)}]
    out = tmp_path / "cache.json"
    fp.build_cache(rows, out)
    cache = json.loads(out.read_text(encoding="utf-8"))
    assert "r1" in cache
    assert set(cache["r1"].keys()) == {"dhash", "color", "edge"}
    # Re-running must not change content (idempotent) and skips existing
    fp.build_cache(rows, out)
    cache2 = json.loads(out.read_text(encoding="utf-8"))
    assert cache2 == cache


def test_build_cache_normalizes_fingerprint_to_jsonable(tmp_path):
    """Cache must be JSON-serializable: dhash stored as a hex string or list of ints."""
    img = tmp_path / "x.png"
    _make_image(img, "RGB", (30, 60, 90))
    out = tmp_path / "cache.json"
    fp.build_cache([{"asset_id": "r1", "library_path": str(img)}], out)
    cache = json.loads(out.read_text(encoding="utf-8"))
    # Reload the stored fingerprint and reuse it in distance without a raw image
    loaded = fp.load_fingerprint(cache["r1"])
    assert fp.visual_similarity(loaded, loaded) == 1.0
