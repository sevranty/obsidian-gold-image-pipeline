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

NON_EMPTY_STRING_FIELDS = (
    "asset_id",
    "created_at",
    "skill_version",
    "style_core_version",
    "prompt_schema_version",
    "qa_schema_version",
    "transformation_mode",
    "final_prompt",
    "selected_output",
    "output_format",
)

SCENE_REQUIRED_FIELDS = (
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

QA_CATEGORY_LIMITS = {
    "meaning_and_subject": 25,
    "silhouette_and_geometry": 20,
    "material_and_gold": 20,
    "background_and_composition": 15,
    "lighting": 10,
    "technical_and_artifact": 10,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate and canonicalize an Obsidian Gold manifest specification. "
            "The input must supply created_at; the tool never inserts the current time. "
            "Exit 0 means valid; exit 2 means validation failure; exit 3 means an "
            "operational error."
        )
    )
    parser.add_argument("spec", type=Path, help="Input JSON manifest specification.")
    parser.add_argument(
        "--selected-output",
        type=Path,
        help=(
            "Raster used to verify selected_output and add SHA-256. Defaults to the "
            "selected_output path in the specification, relative to the spec directory."
        ),
    )
    parser.add_argument("--output", type=Path, required=True, help="Manifest JSON output.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing manifest output; never changes source inputs.",
    )
    return parser


def _add(
    diagnostics: list[dict[str, Any]],
    code: str,
    message: str,
    field: str | None = None,
    evidence: str | None = None,
) -> None:
    diagnostics.append(
        diagnostic(code, "error", message, field=field, evidence=evidence)
    )


def _string_list(value: Any, field: str, diagnostics: list[dict[str, Any]]) -> bool:
    valid = isinstance(value, list) and all(isinstance(item, str) for item in value)
    if not valid:
        _add(
            diagnostics,
            "MANIFEST_FIELD_TYPE",
            f"{field} must be a list of strings.",
            field,
        )
    return valid


def _validate_created_at(value: str, diagnostics: list[dict[str, Any]]) -> None:
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _add(
            diagnostics,
            "MANIFEST_CREATED_AT_INVALID",
            "created_at must be an RFC 3339 timestamp.",
            "created_at",
        )
        return
    if parsed.tzinfo is None:
        _add(
            diagnostics,
            "MANIFEST_CREATED_AT_TIMEZONE_MISSING",
            "created_at must include Z or an explicit UTC offset.",
            "created_at",
        )


def _validate_roles(payload: dict[str, Any], diagnostics: list[dict[str, Any]]) -> None:
    files = payload.get("reference_files")
    roles = payload.get("reference_roles")
    if not isinstance(files, list) or not all(
        isinstance(item, str) and item for item in files
    ):
        return
    if not files:
        _add(
            diagnostics,
            "REFERENCE_FILES_EMPTY",
            "reference_files must contain at least one reference.",
            "reference_files",
        )
        return

    declared: set[str] = set()
    if isinstance(roles, dict):
        for file_name, role in roles.items():
            if (
                not isinstance(file_name, str)
                or not file_name
                or not isinstance(role, str)
                or not role
            ):
                _add(
                    diagnostics,
                    "REFERENCE_ROLE_INVALID",
                    "reference_roles keys and values must be non-empty strings.",
                    "reference_roles",
                )
            else:
                declared.add(file_name)
    elif isinstance(roles, list):
        for index, item in enumerate(roles):
            if not isinstance(item, dict):
                _add(
                    diagnostics,
                    "REFERENCE_ROLE_INVALID",
                    "Each reference_roles list item must be an object.",
                    f"reference_roles.{index}",
                )
                continue
            file_name, role = item.get("file"), item.get("role")
            if not isinstance(file_name, str) or not file_name:
                _add(
                    diagnostics,
                    "REFERENCE_ROLE_FILE_INVALID",
                    "Reference role file must be a non-empty string.",
                    f"reference_roles.{index}.file",
                )
            else:
                declared.add(file_name)
            if not isinstance(role, str) or not role:
                _add(
                    diagnostics,
                    "REFERENCE_ROLE_VALUE_INVALID",
                    "Reference role must be a non-empty string.",
                    f"reference_roles.{index}.role",
                )

    missing = sorted(set(files) - declared)
    if missing:
        _add(
            diagnostics,
            "REFERENCE_ROLE_MISSING",
            "Every reference_files item must have a declared role.",
            "reference_roles",
            ", ".join(missing),
        )


def _validate_iterations(value: Any, diagnostics: list[dict[str, Any]]) -> None:
    if not isinstance(value, list):
        return
    for index, item in enumerate(value):
        prefix = f"iterations.{index}"
        if not isinstance(item, dict):
            _add(
                diagnostics,
                "ITERATION_INVALID",
                "Each iteration must be an object.",
                prefix,
            )
            continue
        if (
            not isinstance(item.get("index"), int)
            or isinstance(item.get("index"), bool)
            or item["index"] < 1
        ):
            _add(
                diagnostics,
                "ITERATION_INDEX_INVALID",
                "Iteration index must be a positive integer.",
                f"{prefix}.index",
            )
        if not isinstance(item.get("action"), str) or not item["action"].strip():
            _add(
                diagnostics,
                "ITERATION_ACTION_INVALID",
                "Iteration action must be a non-empty string.",
                f"{prefix}.action",
            )
        if not isinstance(item.get("diagnostic_codes"), list) or not all(
            isinstance(code, str) for code in item.get("diagnostic_codes", [])
        ):
            _add(
                diagnostics,
                "ITERATION_DIAGNOSTICS_INVALID",
                "Iteration diagnostic_codes must be a string list.",
                f"{prefix}.diagnostic_codes",
            )


def _validate_scene(payload: dict[str, Any], diagnostics: list[dict[str, Any]]) -> None:
    scene = payload.get("scene_specification")
    if not isinstance(scene, dict):
        return
    for field in SCENE_REQUIRED_FIELDS:
        if field not in scene:
            _add(
                diagnostics,
                "SCENE_FIELD_MISSING",
                f"Required Scene Specification field is missing: {field}",
                f"scene_specification.{field}",
            )
    if scene.get("mode") != payload.get("transformation_mode"):
        _add(
            diagnostics,
            "SCENE_MODE_MISMATCH",
            "scene_specification.mode must match transformation_mode.",
            "scene_specification.mode",
        )


def _validate_qa(qa: Any, diagnostics: list[dict[str, Any]]) -> None:
    if not isinstance(qa, dict):
        return
    required = (
        "verdict",
        "score_total",
        "category_scores",
        "critical_defects",
        "diagnostic_codes",
        "repairable",
        "recommended_action",
        "repair_scope",
        "known_limitations",
    )
    for field in required:
        if field not in qa:
            _add(
                diagnostics,
                "QA_FIELD_MISSING",
                f"Required qa_result field is missing: {field}",
                f"qa_result.{field}",
            )

    score_total = qa.get("score_total")
    score_valid = (
        isinstance(score_total, (int, float))
        and not isinstance(score_total, bool)
        and 0 <= score_total <= 100
    )
    if not score_valid:
        _add(
            diagnostics,
            "QA_SCORE_INVALID",
            "qa_result.score_total must be a number from 0 to 100.",
            "qa_result.score_total",
        )

    scores = qa.get("category_scores")
    if not isinstance(scores, dict):
        _add(
            diagnostics,
            "QA_CATEGORY_SCORES_INVALID",
            "qa_result.category_scores must be an object.",
            "qa_result.category_scores",
        )
    else:
        missing = sorted(set(QA_CATEGORY_LIMITS) - set(scores))
        extra = sorted(set(scores) - set(QA_CATEGORY_LIMITS))
        for category in missing:
            _add(
                diagnostics,
                "QA_CATEGORY_MISSING",
                f"Required QA category is missing: {category}",
                f"qa_result.category_scores.{category}",
            )
        for category in extra:
            _add(
                diagnostics,
                "QA_CATEGORY_UNKNOWN",
                f"Unknown QA category: {category}",
                f"qa_result.category_scores.{category}",
            )
        values_valid = True
        for category, maximum in QA_CATEGORY_LIMITS.items():
            value = scores.get(category)
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not 0 <= value <= maximum
            ):
                values_valid = False
                _add(
                    diagnostics,
                    "QA_CATEGORY_SCORE_INVALID",
                    f"{category} must be a number from 0 to {maximum}.",
                    f"qa_result.category_scores.{category}",
                )
        if score_valid and values_valid and not missing and not extra:
            category_total = sum(float(scores[key]) for key in QA_CATEGORY_LIMITS)
            if abs(category_total - float(score_total)) > 1e-9:
                _add(
                    diagnostics,
                    "QA_SCORE_TOTAL_MISMATCH",
                    "qa_result.score_total must equal the category score sum.",
                    "qa_result.score_total",
                    f"categories={category_total:g}; total={float(score_total):g}",
                )

    for field in ("critical_defects", "diagnostic_codes", "known_limitations"):
        value = qa.get(field)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            _add(
                diagnostics,
                "QA_FIELD_TYPE_INVALID",
                f"qa_result.{field} must be a list of strings.",
                f"qa_result.{field}",
            )
    if not isinstance(qa.get("repairable"), bool):
        _add(
            diagnostics,
            "QA_FIELD_TYPE_INVALID",
            "qa_result.repairable must be boolean.",
            "qa_result.repairable",
        )
    for field in ("verdict", "recommended_action"):
        value = qa.get(field)
        if not isinstance(value, str) or not value.strip():
            _add(
                diagnostics,
                "QA_FIELD_TYPE_INVALID",
                f"qa_result.{field} must be a non-empty string.",
                f"qa_result.{field}",
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
            _add(
                diagnostics,
                "MANIFEST_FIELD_MISSING",
                f"Required manifest field is missing: {field}",
                field,
            )
        elif not isinstance(payload[field], expected_type):
            _add(
                diagnostics,
                "MANIFEST_FIELD_TYPE",
                f"Manifest field has invalid type: {field}",
                field,
            )

    for field in NON_EMPTY_STRING_FIELDS:
        value = payload.get(field)
        if isinstance(value, str) and not value.strip():
            _add(
                diagnostics,
                "MANIFEST_FIELD_EMPTY",
                f"{field} must be non-empty.",
                field,
            )

    for field in (
        "reference_files",
        "negative_constraints",
        "diagnostic_codes",
        "known_limitations",
    ):
        if field in payload:
            _string_list(payload[field], field, diagnostics)

    created_at = payload.get("created_at")
    if isinstance(created_at, str) and created_at.strip():
        _validate_created_at(created_at, diagnostics)

    if payload.get("transformation_mode") not in ("generate", "edit"):
        _add(
            diagnostics,
            "MANIFEST_MODE_INVALID",
            "transformation_mode must be generate or edit.",
            "transformation_mode",
        )

    dimensions = payload.get("output_dimensions")
    if isinstance(dimensions, dict):
        for field in ("width", "height"):
            value = dimensions.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                _add(
                    diagnostics,
                    "MANIFEST_DIMENSION_INVALID",
                    f"output_dimensions.{field} must be a positive integer.",
                    f"output_dimensions.{field}",
                )

    _validate_roles(payload, diagnostics)
    _validate_iterations(payload.get("iterations"), diagnostics)
    _validate_scene(payload, diagnostics)
    _validate_qa(payload.get("qa_result"), diagnostics)
    return diagnostics


def _selected_output(
    spec_path: Path, payload: dict[str, Any], explicit: Path | None
) -> Path:
    if explicit is not None:
        return explicit.resolve(strict=True)
    declared = Path(payload["selected_output"])
    return (
        declared if declared.is_absolute() else spec_path.parent / declared
    ).resolve(strict=True)


def build_manifest(
    spec_path: Path, selected_output: Path | None
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = read_json(spec_path)
    diagnostics = _validate_spec(payload)
    if diagnostics:
        return {}, diagnostics
    assert isinstance(payload, dict)

    raster = _selected_output(spec_path, payload, selected_output)
    declared_name = Path(payload["selected_output"]).name
    if declared_name != raster.name:
        _add(
            diagnostics,
            "SELECTED_OUTPUT_MISMATCH",
            "selected_output filename does not match the verified raster.",
            "selected_output",
            f"{declared_name} != {raster.name}",
        )
        return {}, diagnostics

    try:
        with Image.open(raster) as opened:
            opened.load()
            width, height = opened.size
            actual_format = opened.format or "UNKNOWN"
    except (UnidentifiedImageError, OSError) as exc:
        _add(
            diagnostics,
            "SELECTED_OUTPUT_DECODE_FAILED",
            f"Cannot decode selected output: {exc}",
            "selected_output",
        )
        return {}, diagnostics

    declared_dimensions = payload["output_dimensions"]
    if declared_dimensions != {"width": width, "height": height}:
        _add(
            diagnostics,
            "OUTPUT_DIMENSIONS_MISMATCH",
            "Declared output dimensions do not match the selected raster.",
            "output_dimensions",
            f"declared={declared_dimensions}; actual={width}x{height}",
        )
    if payload["output_format"].upper() != actual_format.upper():
        _add(
            diagnostics,
            "OUTPUT_FORMAT_MISMATCH",
            "Declared output format does not match the selected raster.",
            "output_format",
            f"declared={payload['output_format']}; actual={actual_format}",
        )
    if diagnostics:
        return {}, diagnostics

    manifest = dict(payload)
    manifest.update(
        {
            "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
            "selected_output": raster.name,
            "selected_output_sha256": sha256_file(raster),
            "selected_output_size_bytes": raster.stat().st_size,
            "reference_files": sorted(payload["reference_files"]),
            "diagnostic_codes": sorted(set(payload["diagnostic_codes"])),
            "negative_constraints": list(payload["negative_constraints"]),
            "known_limitations": list(payload["known_limitations"]),
        }
    )
    return manifest, []


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        ensure_distinct_paths(args.output, [args.spec])
        if args.selected_output is not None:
            ensure_distinct_paths(args.output, [args.selected_output])

        manifest, diagnostics = build_manifest(args.spec, args.selected_output)
        if diagnostics:
            emit_report(
                {
                    "tool": TOOL_NAME,
                    "tool_version": TOOL_VERSION,
                    "status": "fail",
                    "valid": False,
                    "diagnostics": diagnostics,
                    "exit_code": 2,
                }
            )
            return 2

        payload = canonical_json_bytes(manifest)
        atomic_write_bytes(args.output, payload, force=args.force)
        emit_report(
            {
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
        )
        return EXIT_OK
    except (ToolError, FileNotFoundError) as exc:
        emit_report(operational_failure(TOOL_NAME, str(exc)), stream=sys.stderr)
        return EXIT_OPERATIONAL
    except OSError as exc:
        emit_report(operational_failure(TOOL_NAME, str(exc)), stream=sys.stderr)
        return EXIT_OPERATIONAL


if __name__ == "__main__":
    raise SystemExit(main())
