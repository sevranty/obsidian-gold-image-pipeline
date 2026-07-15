#!/usr/bin/env python3
"""Build a non-destructive production package for an accepted raster asset."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps, UnidentifiedImageError

try:
    from ._common import (
        EXIT_OPERATIONAL,
        EXIT_OK,
        TOOL_VERSION,
        ToolError,
        atomic_write_bytes,
        canonical_json_bytes,
        emit_report,
        operational_failure,
        read_json,
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
        emit_report,
        operational_failure,
        read_json,
        sha256_file,
    )

TOOL_NAME = "package_asset"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Copy an accepted image, 64x64 preview, and manifest into a new production "
            "directory. Optionally export WebP. Existing source files are never modified "
            "and an existing output directory is never replaced."
        )
    )
    parser.add_argument("image", type=Path, help="Accepted final raster image.")
    parser.add_argument("manifest", type=Path, help="Validated manifest JSON.")
    parser.add_argument(
        "--preview",
        type=Path,
        help="Existing 64x64 PNG preview; generated from the image when omitted.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="New package directory.",
    )
    parser.add_argument(
        "--include-webp",
        action="store_true",
        help="Add a WebP export without replacing the final source image.",
    )
    parser.add_argument(
        "--webp-quality",
        type=int,
        default=90,
        choices=range(1, 101),
        metavar="1..100",
        help="WebP quality used with --include-webp.",
    )
    return parser


def _load_image(path: Path) -> tuple[Image.Image, str]:
    try:
        with Image.open(path) as opened:
            opened.load()
            return opened.copy(), opened.format or "UNKNOWN"
    except (UnidentifiedImageError, OSError) as exc:
        raise ToolError(f"Cannot decode raster image {path}: {exc}") from exc


def _save_preview(image: Image.Image, output: Path) -> None:
    source = image.convert("RGBA")
    contained = ImageOps.contain(source, (64, 64), method=Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 255))
    offset = ((64 - contained.width) // 2, (64 - contained.height) // 2)
    canvas.alpha_composite(contained, dest=offset)
    canvas.convert("RGB").save(output, format="PNG", optimize=False)


def _validate_preview(path: Path) -> None:
    try:
        with Image.open(path) as preview:
            preview.load()
            if preview.size != (64, 64):
                raise ToolError(
                    f"Preview must be exactly 64x64 pixels: {path} is {preview.size}"
                )
            if preview.format != "PNG":
                raise ToolError(f"Preview must be PNG: {path} is {preview.format}")
    except (UnidentifiedImageError, OSError) as exc:
        raise ToolError(f"Cannot decode preview {path}: {exc}") from exc


def _record(path: Path, role: str) -> dict[str, Any]:
    return {
        "role": role,
        "filename": path.name,
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def package(
    image_path: Path,
    manifest_path: Path,
    *,
    preview_path: Path | None,
    output_dir: Path,
    include_webp: bool,
    webp_quality: int,
) -> dict[str, Any]:
    image_path = image_path.resolve(strict=True)
    manifest_path = manifest_path.resolve(strict=True)
    preview_resolved = (
        preview_path.resolve(strict=True) if preview_path is not None else None
    )
    output_dir = output_dir.resolve(strict=False)

    if output_dir.exists():
        raise ToolError(f"Output directory already exists: {output_dir}")
    if output_dir == image_path.parent or output_dir == manifest_path.parent:
        raise ToolError("Output directory must be separate from source directories.")

    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict):
        raise ToolError("Manifest root must be a JSON object.")
    for field in ("asset_id", "created_at", "selected_output", "selected_output_sha256"):
        if field not in manifest:
            raise ToolError(f"Manifest is missing required packaging field: {field}")

    source_hashes_before = {
        "image": sha256_file(image_path),
        "manifest": sha256_file(manifest_path),
    }
    if preview_resolved is not None:
        source_hashes_before["preview"] = sha256_file(preview_resolved)

    if Path(str(manifest["selected_output"])).name != image_path.name:
        raise ToolError(
            "Manifest selected_output filename does not match the supplied final image."
        )
    if manifest["selected_output_sha256"] != source_hashes_before["image"]:
        raise ToolError(
            "Manifest selected_output_sha256 does not match the supplied final image."
        )

    image, image_format = _load_image(image_path)
    if preview_resolved is not None:
        _validate_preview(preview_resolved)

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=output_dir.parent)
    )
    files: list[dict[str, Any]] = []
    try:
        final_copy = temporary / image_path.name
        reserved_names = {"manifest.json", "preview-64.png", "package-index.json"}
        if final_copy.name in reserved_names:
            raise ToolError(
                f"Selected output filename is reserved by the package contract: {final_copy.name}"
            )
        shutil.copy2(image_path, final_copy)
        files.append(_record(final_copy, "final_image"))

        manifest_copy = temporary / "manifest.json"
        shutil.copy2(manifest_path, manifest_copy)
        files.append(_record(manifest_copy, "manifest"))

        preview_copy = temporary / "preview-64.png"
        if preview_resolved is not None:
            shutil.copy2(preview_resolved, preview_copy)
        else:
            _save_preview(image, preview_copy)
        files.append(_record(preview_copy, "preview_64"))

        webp_added = False
        if include_webp:
            if image_format.upper() == "WEBP":
                webp_added = True
            else:
                webp_copy = temporary / "final-image.webp"
                converted = image.convert("RGB")
                converted.save(
                    webp_copy,
                    format="WEBP",
                    quality=webp_quality,
                    method=6,
                    exact=True,
                )
                files.append(_record(webp_copy, "webp_export"))
                webp_added = True

        source_hashes_after_copy = {
            "image": sha256_file(image_path),
            "manifest": sha256_file(manifest_path),
        }
        if preview_resolved is not None:
            source_hashes_after_copy["preview"] = sha256_file(preview_resolved)
        if source_hashes_before != source_hashes_after_copy:
            raise ToolError("At least one source file changed during packaging.")

        package_index = {
            "package_schema_version": "1.0.0",
            "tool_version": TOOL_VERSION,
            "asset_id": manifest["asset_id"],
            "created_at": manifest["created_at"],
            "source_format": image_format,
            "files": sorted(files, key=lambda item: item["filename"]),
            "webp_requested": include_webp,
            "webp_added": webp_added,
            "source_preserved": True,
        }
        index_path = temporary / "package-index.json"
        atomic_write_bytes(index_path, canonical_json_bytes(package_index))
        files.append(_record(index_path, "package_index"))

        temporary.replace(output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise

    source_hashes_after = {
        "image": sha256_file(image_path),
        "manifest": sha256_file(manifest_path),
    }
    if preview_resolved is not None:
        source_hashes_after["preview"] = sha256_file(preview_resolved)
    if source_hashes_before != source_hashes_after:
        raise ToolError(
            "At least one source file changed during final package publication."
        )

    packaged_files = sorted(
        (
            {
                "filename": path.name,
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
            for path in output_dir.iterdir()
            if path.is_file()
        ),
        key=lambda item: item["filename"],
    )

    return {
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "status": "pass",
        "valid": True,
        "output_dir": str(output_dir),
        "asset_id": manifest["asset_id"],
        "source_preserved": True,
        "source_hashes": source_hashes_after,
        "files": packaged_files,
        "exit_code": EXIT_OK,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        report = package(
            args.image,
            args.manifest,
            preview_path=args.preview,
            output_dir=args.output_dir,
            include_webp=args.include_webp,
            webp_quality=args.webp_quality,
        )
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
