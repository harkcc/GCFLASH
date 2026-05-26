#!/usr/bin/env python3
"""Lightweight validation for eMAG detail product-input and section-plan artifacts."""

from __future__ import annotations

import argparse
import json
import pathlib


REQUIRED_PRODUCT_KEYS = {
    "product_id",
    "brand",
    "language",
    "product_title",
    "product_type",
    "core_features",
    "specs",
    "compatibility",
    "package_contents",
}

REQUIRED_SECTION_KEYS = {
    "section_id",
    "section_type",
    "buyer_question",
    "title",
    "body_points",
    "proof_mode",
    "compliance_notes",
}

ALLOWED_FAMILIES = {"minimal_clean", "dense_feature", "spec_first"}
ALLOWED_SECTION_TYPES = {
    "hero",
    "benefit",
    "feature_proof",
    "scenario",
    "specs",
    "compatibility",
    "package_contents",
    "safety_or_usage",
    "closing",
}


def load_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text())


def validate_product(product: dict) -> list[dict]:
    findings = []
    missing = sorted(REQUIRED_PRODUCT_KEYS - set(product.keys()))
    if missing:
      findings.append({"level": "error", "code": "missing_product_keys", "message": ", ".join(missing)})
    if len(product.get("core_features", [])) < 3:
        findings.append({"level": "error", "code": "core_features_too_short", "message": "Need at least 3 core features"})
    if len(product.get("specs", [])) < 3:
        findings.append({"level": "error", "code": "specs_too_short", "message": "Need at least 3 specs"})
    if not product.get("package_contents"):
        findings.append({"level": "error", "code": "package_contents_empty", "message": "Package contents missing"})
    return findings


def validate_plan(plan: dict) -> list[dict]:
    findings = []
    families = set(plan.get("template_families", []))
    if not families:
        findings.append({"level": "error", "code": "template_families_missing", "message": "No template families declared"})
    invalid_families = sorted(families - ALLOWED_FAMILIES)
    if invalid_families:
        findings.append({"level": "error", "code": "invalid_template_families", "message": ", ".join(invalid_families)})

    sections = plan.get("sections", [])
    if len(sections) < 4:
        findings.append({"level": "error", "code": "too_few_sections", "message": "Need at least 4 sections"})
    for idx, section in enumerate(sections):
        missing = sorted(REQUIRED_SECTION_KEYS - set(section.keys()))
        if missing:
            findings.append(
                {
                    "level": "error",
                    "code": "missing_section_keys",
                    "message": f"section[{idx}] missing: {', '.join(missing)}",
                }
            )
        if section.get("section_type") not in ALLOWED_SECTION_TYPES:
            findings.append(
                {
                    "level": "error",
                    "code": "invalid_section_type",
                    "message": f"section[{idx}] invalid type: {section.get('section_type')}",
                }
            )
        if not section.get("body_points"):
            findings.append(
                {
                    "level": "error",
                    "code": "empty_body_points",
                    "message": f"section[{idx}] body_points is empty",
                }
            )
    return findings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", type=pathlib.Path, required=True)
    parser.add_argument("--plan", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, default=None)
    args = parser.parse_args()

    product = load_json(args.product)
    plan = load_json(args.plan)
    findings = validate_product(product) + validate_plan(plan)
    report = {
        "product_path": str(args.product),
        "plan_path": str(args.plan),
        "status": "pass" if not findings else "fail",
        "findings": findings,
    }
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(payload + "\n")
    print(payload)


if __name__ == "__main__":
    main()
