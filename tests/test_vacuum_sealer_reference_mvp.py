import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
CHECKED_IN_MANIFEST = REPO / "workflow/ozon_visual_reference/mvp/vacuum_sealer_reference_mvp.json"
sys.path.insert(0, str(REPO / "scripts"))

import ozon_visual_reference_mvp_lib as mvp


import base64


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn0sGQAAAAASUVORK5CYII="
)


def _write_png(path: pathlib.Path) -> None:
    path.write_bytes(PNG_1X1)


def _write_manifest(tmp_path: pathlib.Path, *, direct_local_path: str | None = None) -> pathlib.Path:
    if direct_local_path is None:
        direct_local_path = str(tmp_path / "direct.webp")
    library = tmp_path / "library.jsonl"
    library.write_text(
        "\n".join(
            [
                json.dumps({
                    "reference_id": "d0d6d81112d4",
                    "role": "direct_reference",
                    "card_id": "wide_low_device",
                    "local_path": direct_local_path,
                    "title": "vacuum sealer direct",
                    "source": "ozon_curated",
                }),
                json.dumps({
                    "reference_id": "e1c49e0e97f5",
                    "role": "structure_pattern",
                    "card_id": "wide_low_device",
                    "local_path": str(tmp_path / "pattern.webp"),
                    "title": "vacuum sealer pattern",
                    "source": "ozon_curated",
                }),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for name in ["direct.webp", "pattern.webp", "product.png", "atoms.json", "cards.json", "proof.json", "bank.json"]:
        (tmp_path / name).write_bytes(b"x")
    manifest = {
        "product": {
            "title": "Vacuum sealer machine with cutter and 10 bags",
            "facts": "75 kPa suction; built-in cutter; dry and moist modes; includes 10 bags",
            "image": str(tmp_path / "product.png"),
        },
        "structure": {
            "card_id": "wide_low_device",
            "atoms_source": str(tmp_path / "atoms.json"),
            "cards_source": str(tmp_path / "cards.json"),
            "proof_source": str(tmp_path / "proof.json"),
            "prompt_bank_source": str(tmp_path / "bank.json"),
        },
        "references": {
            "library": str(library),
            "direct_reference_id": "d0d6d81112d4",
            "structure_prompt_id": "e1c49e0e97f5",
        },
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path


def test_build_branch_specs_pins_known_reference_ids(tmp_path):
    manifest_path = _write_manifest(tmp_path)
    manifest = mvp.load_manifest(manifest_path)
    branches = mvp.build_branch_specs(manifest)

    assert [branch.name for branch in branches] == ["direct_reference", "reference_prompt"]

    direct_branch = branches[0]
    assert direct_branch.route_mode == "direct_reference"
    assert direct_branch.card_id == "wide_low_device"
    assert direct_branch.primary_reference_id == "d0d6d81112d4"
    assert direct_branch.primary_reference_path.endswith("direct.webp")

    prompt_branch = branches[1]
    assert prompt_branch.route_mode == "reference_prompt"
    assert prompt_branch.primary_reference_id is None
    assert prompt_branch.prompt_reference_id == "e1c49e0e97f5"


def test_load_manifest_normalizes_repo_relative_paths_for_checked_in_manifest(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    manifest = mvp.load_manifest(CHECKED_IN_MANIFEST)

    for section, key in [
        ("product", "image"),
        ("structure", "atoms_source"),
        ("structure", "cards_source"),
        ("structure", "proof_source"),
        ("structure", "prompt_bank_source"),
        ("references", "library"),
    ]:
        resolved = pathlib.Path(manifest[section][key])
        assert resolved.is_absolute()
        assert resolved.exists()


def test_checked_in_manifest_builds_expected_branch_specs_from_any_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    manifest = mvp.load_manifest(CHECKED_IN_MANIFEST)
    branches = mvp.build_branch_specs(manifest)

    assert [branch.name for branch in branches] == ["direct_reference", "reference_prompt"]

    direct_branch = branches[0]
    assert direct_branch.primary_reference_id == "d0d6d81112d4"
    assert pathlib.Path(direct_branch.primary_reference_path).is_absolute()
    assert pathlib.Path(direct_branch.primary_reference_path).exists()

    prompt_branch = branches[1]
    assert prompt_branch.prompt_reference_id == "e1c49e0e97f5"
    assert pathlib.Path(prompt_branch.prompt_reference_path).is_absolute()
    assert pathlib.Path(prompt_branch.prompt_reference_path).exists()


def test_manifest_only_calls_do_not_import_runner_helper():
    script = f"""
import pathlib
import sys

repo = pathlib.Path({str(REPO)!r})
sys.path.insert(0, str((repo / "scripts").resolve()))

import ozon_visual_reference_mvp_lib as mvp

manifest = mvp.load_manifest({str(CHECKED_IN_MANIFEST)!r})
branches = mvp.build_branch_specs(manifest)
print("RUNNER_LOADED", "run_ozon_visual_reference_generation" in sys.modules)
print("BRANCHES", [branch.name for branch in branches])
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "RUNNER_LOADED False" in result.stdout
    assert "BRANCHES ['direct_reference', 'reference_prompt']" in result.stdout


def test_direct_reference_payload_includes_product_then_reference(tmp_path):
    manifest_path = _write_manifest(tmp_path)
    _write_png(tmp_path / "product.png")
    _write_png(tmp_path / "direct.webp")
    _write_png(tmp_path / "pattern.webp")
    branch = mvp.build_branch_specs(mvp.load_manifest(manifest_path))[0]

    parts, payload_manifest = mvp.build_branch_payload(branch)

    assert payload_manifest["input_images_in_order"][0]["role"] == "product_truth"
    assert payload_manifest["input_images_in_order"][1]["role"] == "primary_reference_anchor"
    assert payload_manifest["input_images_in_order"][1]["path"].endswith("direct.webp")
    assert len(parts) == 3


def test_reference_prompt_payload_omits_reference_image(tmp_path):
    manifest_path = _write_manifest(tmp_path)
    _write_png(tmp_path / "product.png")
    _write_png(tmp_path / "pattern.webp")
    branch = mvp.build_branch_specs(mvp.load_manifest(manifest_path))[1]

    parts, payload_manifest = mvp.build_branch_payload(branch)

    assert payload_manifest["input_images_in_order"] == [
        {"role": "product_truth", "path": branch.product_image}
    ]
    assert "ONE IMAGE IS PROVIDED" in parts[0]["text"]
    assert "TWO IMAGES ARE PROVIDED" not in parts[0]["text"]
    assert len(parts) == 2


def test_run_experiment_prompt_only_writes_expected_artifact_layout(tmp_path):
    manifest_path = _write_manifest(tmp_path)
    _write_png(tmp_path / "product.png")
    _write_png(tmp_path / "direct.webp")
    _write_png(tmp_path / "pattern.webp")

    run_dir = mvp.run_experiment(
        manifest_path=manifest_path,
        out_root=tmp_path / "artifacts",
        run_id="smoke-case",
        prompt_only=True,
        google_key=None,
    )

    assert (run_dir / "manifest.json").exists()
    assert (run_dir / "direct_reference" / "generation_prompt.md").exists()
    assert (run_dir / "direct_reference" / "reference_selection.json").exists()
    assert (run_dir / "direct_reference" / "imagegen_payload_manifest.json").exists()
    assert (run_dir / "reference_prompt" / "generation_prompt.md").exists()
    assert (run_dir / "reference_prompt" / "reference_selection.json").exists()
    assert (run_dir / "reference_prompt" / "imagegen_payload_manifest.json").exists()
    assert (run_dir / "evaluation_summary.json").exists()
    assert (run_dir / "evaluation_summary.md").exists()
    assert (run_dir / "scaling_notes.md").exists()

    direct_payload = json.loads(
        (run_dir / "direct_reference" / "imagegen_payload_manifest.json").read_text(encoding="utf-8")
    )
    prompt_payload = json.loads(
        (run_dir / "reference_prompt" / "imagegen_payload_manifest.json").read_text(encoding="utf-8")
    )

    assert [item["role"] for item in direct_payload["input_images_in_order"]] == [
        "product_truth",
        "primary_reference_anchor",
    ]
    assert [item["role"] for item in prompt_payload["input_images_in_order"]] == [
        "product_truth"
    ]


def test_run_experiment_prompt_only_rejects_empty_direct_reference_path(tmp_path):
    manifest_path = _write_manifest(tmp_path, direct_local_path="")
    _write_png(tmp_path / "product.png")
    _write_png(tmp_path / "pattern.webp")

    with pytest.raises(ValueError, match="direct_reference.*local_path"):
        mvp.run_experiment(
            manifest_path=manifest_path,
            out_root=tmp_path / "artifacts",
            run_id="broken-direct-reference",
            prompt_only=True,
            google_key=None,
        )


def test_validate_direct_reference_transfer_rejects_missing_anchor(tmp_path):
    payload_path = tmp_path / "imagegen_payload_manifest.json"
    payload_path.write_text(
        json.dumps({
            "input_images_in_order": [{"role": "product_truth", "path": "product.png"}]
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="did not transmit expected direct reference"):
        mvp.validate_direct_reference_transfer(payload_path, "direct.webp")


def test_validate_direct_reference_transfer_rejects_same_basename_different_path(tmp_path):
    expected_dir = tmp_path / "expected"
    actual_dir = tmp_path / "actual"
    expected_dir.mkdir()
    actual_dir.mkdir()

    payload_path = tmp_path / "imagegen_payload_manifest.json"
    payload_path.write_text(
        json.dumps({
            "input_images_in_order": [
                {"role": "product_truth", "path": str(tmp_path / "product.png")},
                {
                    "role": "primary_reference_anchor",
                    "path": str(actual_dir / "direct.webp"),
                    "reference_id": "wrong-anchor",
                },
            ]
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="did not transmit expected direct reference"):
        mvp.validate_direct_reference_transfer(payload_path, expected_dir / "direct.webp")


def test_validate_direct_reference_transfer_locates_primary_anchor_by_role(tmp_path):
    anchor_path = tmp_path / "direct.webp"
    payload_path = tmp_path / "imagegen_payload_manifest.json"
    payload_path.write_text(
        json.dumps({
            "input_images_in_order": [
                {"role": "product_truth", "path": str(tmp_path / "product.png")},
                {"role": "secondary_reference", "path": str(tmp_path / "secondary.webp")},
                {
                    "role": "primary_reference_anchor",
                    "path": str(anchor_path),
                    "reference_id": "d0d6d81112d4",
                },
            ]
        }),
        encoding="utf-8",
    )

    mvp.validate_direct_reference_transfer(payload_path, anchor_path)
