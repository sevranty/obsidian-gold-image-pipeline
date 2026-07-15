#!/usr/bin/env python3
"""Inspect deterministic raster properties without making aesthetic claims."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageOps, UnidentifiedImageError

try:
    from ._common import (
        EXIT_OPERATIONAL,
        EXIT_OK,
        TOOL_VERSION,
        ToolArgumentParser,
        ToolError,
        atomic_write_json,
        diagnostic,
        emit_report,
        ensure_distinct_paths,
        final_exit_code,
        operational_failure,
        sha256_file,
    )
except ImportError:
    from _common import (
        EXIT_OPERATIONAL,
        EXIT_OK,
        TOOL_VERSION,
        ToolArgumentParser,
        ToolError,
        atomic_write_json,
        diagnostic,
        emit_report,
        ensure_distinct_paths,
        final_exit_code,
        operational_failure,
        sha256_file,
    )

TOOL_NAME = "inspect_image"
ALLOWED_FORMATS = {"PNG", "JPEG", "WEBP"}


def build_parser() -> argparse.ArgumentParser:
    parser = ToolArgumentParser(
        description=(
            "Inspect raster dimensions, format, mode, alpha, file size, corner blackness, "
            "empty-image risk, and edge-touch risk. Optionally write a 64x64 preview. "
            "Exit 0 means no deterministic errors; exit 2 means validation failure; "
            "exit 3 means an operational error."
        )
    )
    parser.add_argument("image", type=Path, help="Input raster image.")
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional JSON report output path.",
    )
    parser.add_argument(
        "--preview-output",
        type=Path,
        help="Optional 64x64 PNG preview output path.",
    )
    parser.add_argument(
        "--corner-threshold",
        type=int,
        default=12,
        choices=range(0, 256),
        metavar="0..255",
        help="Maximum RGB channel value accepted as near-black in corners.",
    )
    parser.add_argument(
        "--content-threshold",
        type=int,
        default=18,
        choices=range(0, 256),
        metavar="0..255",
        help="RGB threshold used for non-background content heuristics.",
    )
    parser.add_argument(
        "--edge-margin",
        type=int,
        default=2,
        choices=range(0, 65),
        metavar="0..64",
        help="Pixel margin used to flag content touching image edges.",
    )
    parser.add_argument(
        "--max-file-bytes",
        type=int,
        default=25_000_000,
        help="Maximum accepted file size in bytes.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing report or preview outputs; never changes the source image.",
    )
    return parser


def _has_alpha(image: Image.Image) -> bool:
    return "A" in image.getbands() or (
        image.mode == "P" and "transparency" in image.info
    )


def _pixel_rgba(image: Image.Image, xy: tuple[int, int]) -> tuple[int, int, int, int]:
    rgba = image.convert("RGBA")
    value = rgba.getpixel(xy)
    return tuple(int(channel) for channel in value)


def _corner_metrics(
    image: Image.Image, threshold: int
) -> tuple[list[dict[str, Any]], bool, int]:
    width, height = image.size
    coordinates = {
        "top_left": (0, 0),
        "top_right": (width - 1, 0),
        "bottom_left": (0, height - 1),
        "bottom_right": (width - 1, height - 1),
    }
    metrics: list[dict[str, Any]] = []
    max_channel = 0
    all_near_black = True
    for name, xy in coordinates.items():
        rgba = _pixel_rgba(image, xy)
        rgb_max = max(rgba[:3])
        max_channel = max(max_channel, rgb_max)
        near_black = rgb_max <= threshold and rgba[3] == 255
        all_near_black = all_near_black and near_black
        distance = math.sqrt(sum(channel * channel for channel in rgba[:3]))
        metrics.append(
            {
                "corner": name,
                "xy": [xy[0], xy[1]],
                "rgba": list(rgba),
                "rgb_max": rgb_max,
                "distance_to_black": round(distance, 4),
                "near_black": near_black,
            }
        )
    return metrics, all_near_black, max_channel


def _content_bbox(
    image: Image.Image, threshold: int
) -> tuple[int, int, int, int] | None:
    rgba = image.convert("RGBA")
    background = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
    difference = ImageChops.difference(rgba, background)
    rgb = difference.convert("RGB")
    luminance = rgb.convert("L")
    binary = luminance.point(lambda value: 255 if value > threshold else 0)
    if _has_alpha(image):
        alpha = rgba.getchannel("A")
        opaque = Image.new("L", rgba.size, 255)
        alpha_difference = ImageChops.difference(alpha, opaque)
        alpha_binary = alpha_difference.point(lambda value: 255 if value > 0 else 0)
        binary = ImageChops.lighter(binary, alpha_binary)
    return binary.getbbox()


def _touches_edge(
    bbox: tuple[int, int, int, int] | None,
    width: int,
    height: int,
    margin: int,
) -> bool:
    if bbox is None:
        return False
    left, top, right, bottom = bbox
    return (
        left <= margin
        or top <= margin
        or right >= width - margin
        or bottom >= height - margin
    )


def _write_preview(
    image: Image.Image,
    output: Path,
    *,
    force: bool,
) -> None:
    output = output.resolve(strict=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not force:
        raise ToolError(f"Preview output already exists: {output}")
    source = image.convert("RGBA")
    contained = ImageOps.contain(source, (64, 64), method=Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 255))
    offset = ((64 - contained.width) // 2, (64 - contained.height) // 2)
    canvas.alpha_composite(contained, dest=offset)
    temporary = output.with_name(f".{output.name}.tmp")
    try:
        canvas.convert("RGB").save(temporary, format="PNG", optimize=False)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)


def inspect(
    image_path: Path,
    *,
    corner_threshold: int,
    content_threshold: int,
    edge_margin: int,
    max_file_bytes: int,
    preview_output: Path | None = None,
    force: bool = False,
) -> dict[str, Any]:
    image_path = image_path.resolve(strict=True)
    source_sha_before = sha256_file(image_path)
    file_size = image_path.stat().st_size
    diagnostics: list[dict[str, Any]] = []

    try:
        with Image.open(image_path) as opened:
            opened.load()
            image = opened.copy()
            detected_format = opened.format or "UNKNOWN"
    except (UnidentifiedImageError, OSError) as exc:
        raise ToolError(f"Cannot decode raster image {image_path}: {exc}") from exc

    width, height = image.size
    if width <= 0 or height <= 0:
        diagnostics.append(
            diagnostic("IMAGE_DIMENSIONS_INVALID", "error", "Image dimensions must be positive.")
        )
    if detected_format not in ALLOWED_FORMATS:
        diagnostics.append(
            diagnostic(
                "IMAGE_FORMAT_UNSUPPORTED",
                "error",
                f"Unsupported raster format: {detected_format}",
                evidence=detected_format,
            )
        )
    if file_size > max_file_bytes:
        diagnostics.append(
            diagnostic(
                "IMAGE_FILE_TOO_LARGE",
                "error",
                f"Image exceeds maximum file size: {file_size} > {max_file_bytes}",
            )
        )

    corners, corners_near_black, corner_max = _corner_metrics(image, corner_threshold)
    if not corners_near_black:
        diagnostics.append(
            diagnostic(
                "BACKGROUND_CORNER_NOT_BLACK",
                "error",
                "At least one corner is not opaque near-black.",
                evidence=str(corner_max),
            )
        )

    bbox = _content_bbox(image, content_threshold)
    empty = bbox is None
    edge_touch = _touches_edge(bbox, width, height, edge_margin)
    if empty:
        diagnostics.append(
            diagnostic(
                "IMAGE_EMPTY_OR_ALL_BLACK",
                "error",
                "No non-background content was detected by the technical heuristic.",
            )
        )
    elif edge_touch:
        diagnostics.append(
            diagnostic(
                "CONTENT_EDGE_TOUCH",
                "warning",
                "Detected content touches or approaches an image edge; review crop manually.",
                evidence=str(list(bbox)),
            )
        )

    if preview_output is not None:
        ensure_distinct_paths(preview_output, [image_path])
        _write_preview(image, preview_output, force=force)

    source_sha_after = sha256_file(image_path)
    if source_sha_after != source_sha_before:
        raise ToolError("Source image changed during inspection.")

    aspect_ratio = width / height if height else None
    divisor = math.gcd(width, height) if width > 0 and height > 0 else 1
    aspect_ratio_text = (
        f"{width // divisor}:{height // divisor}" if width > 0 and height > 0 else None
    )
    exit_code = final_exit_code(diagnostics)
    report: dict[str, Any] = {
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "status": "pass" if exit_code == EXIT_OK else "fail",
        "valid": exit_code == EXIT_OK,
        "source": str(image_path),
        "source_sha256": source_sha_before,
        "source_preserved": source_sha_before == source_sha_after,
        "width": width,
        "height": height,
        "aspect_ratio": round(aspect_ratio, 8) if aspect_ratio is not None else None,
        "aspect_ratio_text": aspect_ratio_text,
        "format": detected_format,
        "mode": image.mode,
        "bands": list(image.getbands()),
        "has_alpha": _has_alpha(image),
        "file_size_bytes": file_size,
        "max_file_bytes": max_file_bytes,
        "corner_threshold": corner_threshold,
        "corners": corners,
        "corners_near_black": corners_near_black,
        "content_threshold": content_threshold,
        "content_bbox": list(bbox) if bbox is not None else None,
        "empty_or_all_black": empty,
        "edge_margin": edge_margin,
        "content_edge_touch": edge_touch,
        "preview_output": str(preview_output.resolve(strict=False))
        if preview_output is not None
        else None,
        "diagnostics": diagnostics,
        "exit_code": exit_code,
        "limitations": [
            "Corner sampling does not prove global background uniformity.",
            "Content bounding-box checks do not identify the subject or aesthetic quality.",
            "No OCR, style classification, or gold-coverage estimation is performed.",
        ],
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.report is not None:
            ensure_distinct_paths(args.report, [args.image])
            if args.report.exists() and not args.force:
                raise ToolError(f"Report output already exists: {args.report}")
        if args.preview_output is not None:
            ensure_distinct_paths(args.preview_output, [args.image])
            if args.preview_output.exists() and not args.force:
                raise ToolError(f"Preview output already exists: {args.preview_output}")
        if args.report is not None and args.preview_output is not None:
            ensure_distinct_paths(args.report, [args.preview_output])

        report = inspect(
            args.image,
            corner_threshold=args.corner_threshold,
            content_threshold=args.content_threshold,
            edge_margin=args.edge_margin,
            max_file_bytes=args.max_file_bytes,
            preview_output=args.preview_output,
            force=args.force,
        )
        if args.report is not None:
            atomic_write_json(args.report, report, force=args.force)
        emit_report(report)
        return int(report["exit_code"])
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
