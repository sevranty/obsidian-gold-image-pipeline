#!/usr/bin/env python3
"""Build a deterministic Obsidian Gold asset manifest from validated JSON input."""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError

try:
    from ._common import (
        EXIT_OPERATIONAL,
        EXIT_OK,
        TOOL_VERSION,
        ToolError,
        atomic_write_bytes,
        canonical_json_bytes,
        diagnostic,
        emit_report,
        ensure_distinct_paths,
        operational_failure,
        read_json,
        sha256_bytes,
        sha256_file,
    )
except ImportError:
    from _common import (
        EXIT_OPERATIONAL,
        EXIT_OK,
        TOOL_VERSION,
        ToolError,
        atomic_write_bytes,
        canonical_json_bytes,
        diagnostic,
        emit_report,
        ensure_distinct_paths,
        operational_failure,
        read_json,
        sha256_bytes,
        sha256_file,
    )

TOOL_NAME = "build_manifest"
MANIFEST_SCHEMA_VERSION = "1.0.0"

REQUIRED_FIELDS: dict[str, type | tuple[type, ...]] = {
    "asset_id": str,
    "created_at": str,
    "skill_version": str,
    "style_core_version": str,
    "prompt_schema_version": str,
    "qa_schema_version": str,
    "reference_files": list,
    "reference_roles": (list, dict),
    "transformation_mode": str,
    "scene_specification": dict,
    "final_prompt": str,
    "negative_constraints": list,
    "iterations": list,
    "diagnostic_codes": list,
    "selected_output": str,
    "output_dimensions": dict,
    "output_format": str,
    "qa_result": dict,
    "known_limitations": list,
}

SCENE_REQUIRED_FIELDS: tuple[str, ...] = (
    "mode",
    "asset_type",
    "primary_subject",
    "semantic_meaning",
    "recognition_features",
    "silhouette",
    "pose_or_orientation",
    "camera",
    "geometry",
    "materials",
    "obsidian_finish",
    "gold_placement",
    "gold_ratio",
    "lighting",
    "background",
    "composition",
    "negative_space",
    "subject_fidelity",
    "silhouette_fidelity",
    "composition_fidelity",
    "must_preserve",
    "must_remove",
    "must_not_add",
    "output_ratio",
    "output_usage",
    "input_image_roles",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate and canonicalize an Obsidian Gold manifest specification. "
            "The input must supply created_at; the tool never inserts the current time, "
            "so identical inputs and selected-output bytes produce identical manifests."
        )
    )
    parser.add_argument("spec", type=Path, help="Input JSON manifest specification.")
    parser.add_argument(
        "--selected-output",
        type=Path,
        help=(
            "Optional raster path used to verify selected_output and add its SHA-256. "
            "Defaults to the selected_output path in the specification, resolved relative "
            "to the specification directory."
        ),
    )
    parser.add_argument("--output", type=Path, required=True, help="Manifest JSON output.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing manifest output; never changes source inputs.",
    )
    return parser


def _validate_string_list(
    value: Any, field: str, diagnostics: list[dict[str, Any]]
) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        diagnostics.append(
            diagnostic(
                "MANIFEST_FIELD_TYPE",
                "error",
                f"{field} must be a list of strings.",
                field=field,
            )
        )


def _validate_created_at(value: Any, diagnostics: list[dict[str, Any]]) -> None:
    if not isinstance(value, str) or not value.strip():
        return
    candidate = value.replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(candidate)
    except ValueError:
        diagnostics.append(
            diagnostic(
                "MANIFEST_CREATED_AT_INVALID",
                "error",
                "created_at must be an RFC 3339 timestamp.",
                field="created_at",
            )
        )
        return
    if parsed.tzinfo is None:
        diagnostics.append(
            diagnostic(
                "MANIFEST_CREATED_AT_TIMEZONE_MISSING",
                "error",
                "created_at must include Z or an explicit UTC offset.",
                field="created_at",
            )
        )


def _validate_reference_roles(
    reference_files: Any,
    reference_roles: Any,
    diagnostics: list[dict[str, Any]],
) -> None:
    if not isinstance(reference_files, list) or not all(
        isinstance(item, str) and item for item in reference_files
    ):
        return
    declared: set[str] = set()
    if isinstance(reference_roles, list):
        for index, item in enumerate(reference_roles):
            if not isinstance(item, dict):
                diagnostics.append(
                    diagnostic(
                        "REFERENCE_ROLE_INVALID",
                        "error",
                        "Each reference_roles list item must be an object.",
                        field=f"reference_roles.{index}",
                    )
                )
                continue
            file_name = item.get("file")
            role = item.get("role")
            if not isinstance(file_name, str) or not file_name:
                diagnostics.append(
                    diagnostic(
                        "REFERENCE_ROLE_FILE_INVALID",
                        "error",
                        "Reference role file must be a non-empty string.",
                        field=f"reference_roles.{index}.file",
                    )
                )
            else:
                declared.add(file_name)
            if not isinstance(role, str) or not role:
                diagnostics.append(
                    diagnostic(
                        "REFERENCE_ROLE_VALUE_INVALID",
                        "error",
                        "Reference role must be a non-empty string.",
                        field=f"reference_roles.{index}.role",
                    )
                )
    elif isinstance(reference_roles, dict):
        for file_name, role in reference_roles.items():
            if (
                not isinstance(file_name, str)
                or not file_name
                or not isinstance(role, str)
                or not role
            ):
                diagnostics.append(
                    diagnostic(
                        "REFERENCE_ROLE_INVALID",
                        "error",
                        "reference_roles object keys and values must be non-empty strings.",
                        field="reference_roles",
                    )
                )
            else:
                declared.add(file_name)
    else:
        return

    missing = sorted(set(reference_files) - declared)
    if missing:
        diagnostics.append(
            diagnostic(
                "REFERENCE_ROLE_MISSING",
                "error",
                "Every reference_files item must have a declared role.",
                evidence=", ".join(missing),
                field="reference_roles",
            )
        )


def _validate_iterations(value: Any, diagnostics: list[dict[str, Any]]) -> None:
    if not isinstance(value, list):
        return
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            diagnostics.append(
                diagnostic(
                    "ITERATION_INVALID",
                    "error",
                    "Each iteration must be an object.",
                    field=f"iterations.{index}",
                )
            )
            continue
        if not isinstance(item.get("index"), int) or item["index"] < 1:
            diagnostics.append(
                diagnostic(
                    "ITERATION_INDEX_INVALID",
                    "error",
                    "Iteration index must be a positive integer.",
                    field=f"iterations.{index}.index",
                )
            )
        if not isinstance(item.get("action"), str) or not item["action"]:
            diagnostics.append(
                diagnostic(
                    "ITERATION_ACTION_INVALID",
                    "error",
                    "Iteration action must be a non-empty string.",
                    field=f"iterations.{index}.action",
                )
            )
        codes = item.get("diagnostic_codes")
        if not isinstance(codes, list) or not all(
            isinstance(code, str) for code in codes
        ):
            diagnostics.append(
                diagnostic(
                    "ITERATION_DIAGNOSTICS_INVALID",
                    "error",
                    "Iteration diagnostic_codes must be a string list.",
                    field=f"iterations.{index}.diagnostic_codes",
                )
            )


def _validate_spec(payload: Any) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    if not isinstance(payload, dict):
        return [
            diagnostic(
                "MANIFEST_ROOT_TYPE",
                "error",
                "Manifest specification must be a JSON object.",
            )
        ]

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in payload:
            diagnostics.append(
                diagnostic(
                    "MANIFEST_FIELD_MISSING",
                    "error",
                    f"Required manifest field is missing: {field}",
                    field=field,
                )
            )
            continue
        if not isinstance(payload[field], expected_type):
            diagnostics.append(
                diagnostic(
                    "MANIFEST_FIELD_TYPE",
                    "error",
                    f"Manifest field has invalid type: {field}",
                    field=field,
                )
            )

    for field in (
        "reference_files",
        "negative_constraints",
        "diagnostic_codes",
        "known_limitations",
    ):
        if field in payload:
            _validate_string_list(payload[field], field, diagnostics)

    if "asset_id" in payload and isinstance(payload["asset_id"], str):
        if not payload["asset_id"].strip():
            diagnostics.append(
                diagnostic(
                    "MANIFEST_FIELD_EMPTY",
                    "error",
                    "asset_id must not be empty.",
                    field="asset_id",
                )
            )

    if "created_at" in payload and isinstance(payload["created_at"], str):
        if not payload["created_at"].strip():
            diagnostics.append(
                diagnostic(
                    "MANIFEST_FIELD_EMPTY",
                    "error",
                    "created_at must be explicitly supplied and non-empty.",
                    field="created_at",
                )
            )

    _validate_created_at(payload.get("created_at"), diagnostics)
    _validate_reference_roles(
        payload.get("reference_files"),
        payload.get("reference_roles"),
        diagnostics,
    )
    _validate_iterations(payload.get("iterations"), diagnostics)

    if "transformation_mode" in payload and payload["transformation_mode"] not in (
        "generate",
        "edit",
    ):
        diagnostics.append(
            diagnostic(
                "MANIFEST_MODE_INVALID",
                "error",
                "transformation_mode must be generate or edit.",
                field="transformation_mode",
            )
        )

    dimensions = payload.get("output_dimensions")
    if isinstance(dimensions, dict):
        for field in ("width", "height"):
            if not isinstance(dimensions.get(field), int) or dimensions[field] <= 0:
                diagnostics.append(
                    diagnostic(
                        "MANIFEST_DIMENSION_INVALID",
                        "error",
                        f"output_dimensions.{field} must be a positive integer.",
                        field=f"output_dimensions.{field}",
                    )
                )

    scene = payload.get("scene_specification")
    if isinstance(scene, dict):
        for field in SCENE_REQUIRED_FIELDS:
            if field not in scene:
                diagnostics.append(
                    diagnostic(
                        "SCENE_FIELD_MISSING",
                        "error",
                        f"Required Scene Specification field is missing: {field}",
                        field=f"scene_specification.{field}",
                    )
                )

    qa_result = payload.get("qa_result")
    if isinstance(qa_result, dict):
        for field in (
            "verdict",
            "score_total",
            "category_scores",
            "critical_defects",
            "diagnostic_codes",
            "repairable",
            "recommended_action",
            "repair_scope",
            "known_limitations",
        ):
            if field not in qa_result:
                diagnostics.append(
                    diagnostic(
                        "QA_FIELD_MISSING",
                        "error",
                        f"Required qa_result field is missing: {field}",
                        field=f"qa_result.{field}",
                    )
                )
        score_total = qa_result.get("score_total")
        if (
            not isinstance(score_total, (int, float))
            or isinstance(score_total, bool)
            or not 0 <= score_total <= 100
        ):
            diagnostics.append(
                diagnostic(
                    "QA_SCORE_INVALID",
                    "error",
                    "qa_result.score_total must be a number from 0 to 100.",
                    field="qa_result.score_total",
                )
            )
        category_scores = qa_result.get("category_scores")
        if not isinstance(category_scores, dict) or not all(
            isinstance(score, (int, float))
            and not isinstance(score, bool)
            and score >= 0
            for score in category_scores.values()
        ):
            diagnostics.append(
                diagnostic(
                    "QA_CATEGORY_SCORES_INVALID",
                    "error",
                    "qa_result.category_scores must contain non-negative numeric values.",
                    field="qa_result.category_scores",
                )
            )

    return diagnostics


def _resolve_selected_output(
    spec_path: Path, payload: dict[str, Any], explicit: Path | None
) -> Path:
    if explicit is not None:
        return explicit.resolve(strict=True)
    declared = Path(str(payload["selected_output"]))
    if not declared.is_absolute():
        declared = spec_path.parent / declared
    return declared.resolve(strict=True)


def build_manifest(
    spec_path: Path,
    selected_output: Path | None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = read_json(spec_path)
    diagnostics = _validate_spec(payload)
    if diagnostics:
        return {}, diagnostics
    assert isinstance(payload, dict)

    raster = _resolve_selected_output(spec_path, payload, selected_output)
    declared = Path(str(payload["selected_output"]))
    if declared.name != raster.name:
        diagnostics.append(
            diagnostic(
                "SELECTED_OUTPUT_MISMATCH",
                "error",
                "selected_output filename does not match the verified raster.",
                evidence=f"{declared.name} != {raster.name}",
                field="selected_output",
            )
        )
        return {}, diagnostics

    try:
        with Image.open(raster) as opened:
            opened.load()
            actual_width, actual_height = opened.size
            actual_format = opened.format or "UNKNOWN"
    except (UnidentifiedImageError, OSError) as exc:
        diagnostics.append(
            diagnostic(
                "SELECTED_OUTPUT_DECODE_FAILED",
                "error",
                f"Cannot decode selected output: {exc}",
                field="selected_output",
            )
        )
        return {}, diagnostics

    declared_dimensions = payload["output_dimensions"]
    if (
        declared_dimensions.get("width") != actual_width
        or declared_dimensions.get("height") != actual_height
    ):
        diagnostics.append(
            diagnostic(
                "OUTPUT_DIMENSIONS_MISMATCH",
                "error",
                "Declared output dimensions do not match the selected raster.",
                evidence=(
                    f"declared={declared_dimensions.get('width')}x"
                    f"{declared_dimensions.get('height')}; "
                    f"actual={actual_width}x{actual_height}"
                ),
                field="output_dimensions",
            )
        )
    if str(payload["output_format"]).upper() != actual_format.upper():
        diagnostics.append(
            diagnostic(
                "OUTPUT_FORMAT_MISMATCH",
                "error",
                "Declared output format does not match the selected raster.",
                evidence=f"declared={payload['output_format']}; actual={actual_format}",
                field="output_format",
            )
        )
    if diagnostics:
        return {}, diagnostics

    manifest = dict(payload)
    manifest["manifest_schema_version"] = MANIFEST_SCHEMA_VERSION
    manifest["selected_output"] = raster.name
    manifest["selected_output_sha256"] = sha256_file(raster)
    manifest["selected_output_size_bytes"] = raster.stat().st_size
    manifest["reference_files"] = sorted(manifest["reference_files"])
    manifest["diagnostic_codes"] = sorted(set(manifest["diagnostic_codes"]))
    manifest["negative_constraints"] = list(manifest["negative_constraints"])
    manifest["known_limitations"] = list(manifest["known_limitations"])
    return manifest, diagnostics


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        ensure_distinct_paths(args.output, [args.spec])
        if args.selected_output is not None:
            ensure_distinct_paths(args.output, [args.selected_output])

        manifest, diagnostics = build_manifest(args.spec, args.selected_output)
        if diagnostics:
            report = {
                "tool": TOOL_NAME,
                "tool_version": TOOL_VERSION,
                "status": "fail",
                "valid": False,
                "diagnostics": diagnostics,
                "exit_code": 2,
            }
            emit_report(report)
            return 2

        payload = canonical_json_bytes(manifest)
        atomic_write_bytes(args.output, payload, force=args.force)
        report = {
            "tool": TOOL_NAME,
            "tool_version": TOOL_VERSION,
            "status": "pass",
            "valid": True,
            "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
            "output": str(args.output.resolve(strict=False)),
            "manifest_sha256": sha256_bytes(payload),
            "selected_output_sha256": manifest["selected_output_sha256"],
            "deterministic": True,
            "diagnostics": [],
            "exit_code": EXIT_OK,
        }
        emit_report(report)
        return EXIT_OK
    except (ToolError, FileNotFoundError) as exc:
        report = operational_failure(TOOL_NAME, str(exc))
        emit_report(report, stream=sys.stderr)
        return EXIT_OPERATIONAL
    except OSError as exc:
        report = operational_failure(TOOL_NAME, str(exc))
        emit_report(report, stream=sys.stderr)
        return EXIT_OPERATIONAL


if __name__ == "__main__":
    raise SystemExit(main())
