#!/usr/bin/env python3
"""Validate OGP#8 manual weighted QA scorecards against verdict indexes."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

EXPECTED_MAXIMA = {
    "meaning_and_subject": 25,
    "silhouette_and_geometry": 20,
    "material_and_gold": 20,
    "background_and_composition": 15,
    "lighting": 10,
    "technical_and_artifact": 10,
}


def validate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    outputs: dict[str, dict[str, Any]] = {}
    for verdict in ("accepted", "repairable", "rejected"):
        path = root / f"examples/{verdict}/index.json"
        if not path.exists():
            errors.append(f"Missing verdict index: {path.relative_to(root)}")
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for item in payload.get("cases", []):
            outputs[item.get("id", "")] = item

    review_path = root / "reports/ogp8-manual-review.json"
    if not review_path.exists():
        errors.append("Missing manual review report")
        review: dict[str, Any] = {}
    else:
        review = json.loads(review_path.read_text(encoding="utf-8"))

    if review.get("automated_aesthetic_claim") is not False:
        errors.append("Manual review must explicitly disable automated aesthetic claims")
    if review.get("category_maxima") != EXPECTED_MAXIMA:
        errors.append("Category maxima do not match the canonical 100-point QA rubric")

    reviewed = {item.get("id", ""): item for item in review.get("cases", [])}
    if set(reviewed) != set(outputs):
        errors.append("Manual review case set does not match verdict indexes")

    for case_id, item in reviewed.items():
        indexed = outputs.get(case_id, {})
        scores = item.get("category_scores")
        if not isinstance(scores, dict) or set(scores) != set(EXPECTED_MAXIMA):
            errors.append(f"{case_id}: incomplete category scorecard")
            continue
        for category, maximum in EXPECTED_MAXIMA.items():
            score = scores.get(category)
            if (
                not isinstance(score, (int, float))
                or isinstance(score, bool)
                or not 0 <= score <= maximum
            ):
                errors.append(f"{case_id}: invalid score for {category}")
        if sum(scores.values()) != item.get("score_total"):
            errors.append(f"{case_id}: score_total does not equal category sum")
        if item.get("verdict") != indexed.get("verdict"):
            errors.append(f"{case_id}: verdict mismatch")
        if item.get("diagnostic_codes") != indexed.get("failure_codes"):
            errors.append(f"{case_id}: diagnostic code mismatch")
        expected_repairable = indexed.get("verdict") == "repairable"
        if item.get("repairable") is not expected_repairable:
            errors.append(f"{case_id}: repairable flag mismatch")
        expected_action = {
            "accepted": "ACCEPT",
            "repairable": "TARGETED_REPAIR",
            "rejected": "REGENERATE",
        }.get(indexed.get("verdict"))
        if item.get("recommended_action") != expected_action:
            errors.append(f"{case_id}: recommended action mismatch")

    return {
        "schema_version": "1.0.0",
        "task": "OGP#8",
        "tool": "validate_manual_review.py",
        "status": "pass" if not errors else "fail",
        "reviewed_cases": len(reviewed),
        "indexed_cases": len(outputs),
        "category_count": len(EXPECTED_MAXIMA),
        "maximum_score": sum(EXPECTED_MAXIMA.values()),
        "errors": errors,
        "limitations": [
            "This validator checks scorecard integrity, not whether a human visual judgment is aesthetically correct."
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args(argv)
    report = validate(args.root.resolve())
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
