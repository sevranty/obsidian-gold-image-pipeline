#!/usr/bin/env python3
"""OGP#37: optional, offline Presento v1 adapter for an accepted OGP raster.

No Presento import, network request, paid generation, or credential lookup.
The caller explicitly supplies an already accepted OGP manifest and PNG asset.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from PIL import Image, UnidentifiedImageError

REQUEST_ID = "presento.asset-provider.request.v1"
RESULT_ID = "presento.asset-provider.result.v1"
VERSION = "1.0.0"
PROJECT_ID = "OBSIDIAN_GOLD_IMAGE_PIPELINE"


class AdapterError(ValueError):
    """Stable, machine-readable refusal reason."""

    def __init__(self, code: str, detail: str):
        self.code = code
        super().__init__(f"{code}: {detail}")


def _require_request(request: dict[str, Any]) -> None:
    required = {
        "schema_version", "request_id", "provider_id", "asset_kind",
        "prompt_profile", "requirements", "config",
    }
    if not isinstance(request, dict) or set(request) != required:
        raise AdapterError("invalid_request", "request fields differ from Presento v1")
    if request["schema_version"] != VERSION:
        raise AdapterError("unsupported_version", "expected 1.0.0")
    if request["provider_id"] != "ogp" or request["asset_kind"] != "raster-image":
        raise AdapterError("unsupported_capability", "only ogp/raster-image is supported")
    if not isinstance(request["request_id"], str) or not request["request_id"].strip():
        raise AdapterError("invalid_request", "request_id must be non-empty")
    if request["prompt_profile"] is not None and not isinstance(request["prompt_profile"], str):
        raise AdapterError("invalid_request", "prompt_profile must be string or null")
    if not isinstance(request["requirements"], dict) or not isinstance(request["config"], dict):
        raise AdapterError("invalid_request", "requirements and config must be objects")


def _accepted_bytes(manifest_path: Path, asset_path: Path) -> tuple[bytes, dict[str, int]]:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise AdapterError("invalid_manifest", "OGP manifest cannot be read") from exc
    if not isinstance(manifest, dict):
        raise AdapterError("invalid_manifest", "OGP manifest must be an object")
    qa_result = manifest.get("qa_result")
    if not isinstance(qa_result, dict) or qa_result.get("verdict") != "ACCEPT":
        raise AdapterError("not_accepted", "OGP QA verdict is not ACCEPT")
    if manifest.get("selected_output") != asset_path.name:
        raise AdapterError("asset_mismatch", "asset does not match selected_output")
    expected = manifest.get("selected_output_sha256")
    if not isinstance(expected, str) or len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
        raise AdapterError("missing_asset_provenance", "manifest has no valid selected_output_sha256")
    try:
        payload = asset_path.read_bytes()
    except OSError as exc:
        raise AdapterError("missing_asset", "accepted raster cannot be read") from exc
    if not payload or hashlib.sha256(payload).hexdigest() != expected:
        raise AdapterError("asset_checksum_mismatch", "raster bytes differ from accepted manifest")
    try:
        with Image.open(asset_path) as image:
            if image.format != "PNG":
                raise AdapterError("unsupported_mime", "only accepted PNG raster is supported")
            dimensions = {"width_px": image.width, "height_px": image.height}
            image.verify()
    except (OSError, UnidentifiedImageError) as exc:
        raise AdapterError("invalid_asset", "raster cannot be decoded") from exc
    declared = manifest.get("output_dimensions")
    if not isinstance(declared, dict) or (
        declared.get("width"), declared.get("height")
    ) != (dimensions["width_px"], dimensions["height_px"]):
        raise AdapterError("dimensions_mismatch", "manifest dimensions differ from raster")
    return payload, dimensions


def make_executor(
    manifest_path: Path, asset_path: Path
) -> Callable[[dict[str, Any], Path], tuple[bytes, str, dict[str, int]]]:
    """Return the explicit Presento executor for an already accepted OGP asset.

    The output directory is owned by Presento; this function never writes to it.
    """
    def execute(request: dict[str, Any], output_dir: Path) -> tuple[bytes, str, dict[str, int]]:
        _require_request(request)
        payload, dimensions = _accepted_bytes(manifest_path, asset_path)
        return payload, "image/png", dimensions

    return execute


def result_from_accepted_asset(
    request: dict[str, Any],
    *,
    manifest_path: Path,
    asset_path: Path,
    provider_revision: str,
) -> dict[str, Any]:
    """Return Presento result v1 without materializing or changing the source asset."""
    _require_request(request)
    if not isinstance(provider_revision, str) or not provider_revision.strip():
        raise AdapterError("missing_provider_revision", "exact OGP revision is required")
    payload, dimensions = _accepted_bytes(manifest_path, asset_path)
    config_bytes = json.dumps(
        request["config"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {
        "schema_version": VERSION,
        "request_id": request["request_id"],
        "provider_id": "ogp",
        "provider_project_id": PROJECT_ID,
        "provider_revision": provider_revision,
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "asset_kind": "raster-image",
        "materialization": "local-file",
        "mime_type": "image/png",
        "path": asset_path.as_posix(),
        "checksum": hashlib.sha256(payload).hexdigest(),
        "dimensions": dimensions,
        "diagnostics": [],
    }
