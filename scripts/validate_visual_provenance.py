#!/usr/bin/env python3
"""Validate per-file provenance and checksums for OGP#8 visual assets."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

RIGHTS_STATUS = "self_authored_cc0_like_project_fixture"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    inventory = json.loads(
        (root / "docs/evidence/ogp8-inventory.json").read_text(encoding="utf-8")
    )
    records: list[dict[str, Any]] = []
    records.extend(inventory.get("coverage_cases", []))
    records.extend(inventory.get("runtime_anchors", []))
    records.extend(inventory.get("documentation_assets", []))
    for verdict in ("accepted", "repairable", "rejected"):
        payload = json.loads(
            (root / f"examples/{verdict}/index.json").read_text(encoding="utf-8")
        )
        records.extend(payload.get("cases", []))

    checked_paths: set[str] = set()
    for record in records:
        if record.get("rights_status") != RIGHTS_STATUS:
            errors.append(f"{record.get('id', record.get('path'))}: rights status mismatch")
        if not str(record.get("source_type", "")).startswith("programmatic_"):
            errors.append(f"{record.get('id', record.get('path'))}: source type mismatch")
        candidates: list[tuple[str, str]] = []
        if "file" in record:
            candidates.append((record["file"], record.get("sha256", "")))
        if "path" in record:
            candidates.append((record["path"], record.get("sha256", "")))
        for path_field, hash_field in (
            ("image", "image_sha256"),
            ("preview_64", "preview_sha256"),
            ("eval_output", "eval_output_sha256"),
        ):
            if path_field in record:
                candidates.append((record[path_field], record.get(hash_field, "")))
        for relative, expected in candidates:
            checked_paths.add(relative)
            path = root / relative
            if not path.exists():
                errors.append(f"Missing visual asset: {relative}")
            elif sha256(path) != expected:
                errors.append(f"Checksum mismatch: {relative}")

    expected_count = 10 + 3 + 1 + (15 * 3)
    if len(checked_paths) != expected_count:
        errors.append(
            f"Expected {expected_count} unique visual paths, got {len(checked_paths)}"
        )

    return {
        "schema_version": "1.0.0",
        "task": "OGP#8",
        "tool": "validate_visual_provenance.py",
        "status": "pass" if not errors else "fail",
        "records": len(records),
        "unique_visual_paths": len(checked_paths),
        "rights_status": RIGHTS_STATUS,
        "errors": errors,
        "limitations": [
            "The rights status identifies self-authored project fixtures; the public repository license is finalized in OGP#10."
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
