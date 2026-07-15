#!/usr/bin/env python3
"""Deterministically validate Obsidian Gold prompt structure and conflicts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    from ._common import (
        EXIT_OPERATIONAL,
        EXIT_OK,
        TOOL_VERSION,
        ToolError,
        atomic_write_json,
        diagnostic,
        emit_report,
        final_exit_code,
        normalize_text,
        operational_failure,
        read_json,
        sha256_bytes,
    )
except ImportError:
    from _common import (
        EXIT_OPERATIONAL,
        EXIT_OK,
        TOOL_VERSION,
        ToolError,
        atomic_write_json,
        diagnostic,
        emit_report,
        final_exit_code,
        normalize_text,
        operational_failure,
        read_json,
        sha256_bytes,
    )

TOOL_NAME = "validate_prompt"

REQUIRED_BLOCKS: dict[str, tuple[str, ...]] = {
    "asset_and_mode": (
        r"\b(generate|generated|create|created|edit|repair|raster|digital sculpture)\b",
    ),
    "subject_and_meaning": (
        r"\b(primary subject|main object|recognition features?|recognizable|sculpture of|subject)\b",
    ),
    "silhouette": (
        r"\b(silhouette|outer contour|profile|key proportions?|pose|orientation)\b",
    ),
    "geometry": (
        r"\b(geometry|faceted|planar|parametric|planes?|structural simplification)\b",
    ),
    "obsidian_material": (
        r"\b(obsidian|matte black|manufactured black)\b",
    ),
    "gold_system": (
        r"\b(gold|golden|satin metallic)\b",
    ),
    "lighting": (
        r"\b(lighting|light|broad soft key|soft key)\b",
    ),
    "composition": (
        r"\b(isolated|single object|one object|negative space|full object)\b",
    ),
    "background": (
        r"\b(pure black background|uniform black background|black background)\b",
    ),
    "fidelity": (
        r"\b(fidelity|preserve|keep unchanged|recognition|recognizable)\b",
    ),
    "negative_constraints": (
        r"\b(no |without |remove|must not appear|forbid|exclude)\b",
    ),
    "output": (
        r"\b(output|aspect ratio|ratio|raster|png|webp|square|1:1|watermark)\b",
    ),
    "input_roles": (
        r"\b(content reference|style reference|silhouette reference|edit target|input role)\b",
    ),
}

EDIT_FIELDS: tuple[str, ...] = (
    "change",
    "keep unchanged",
    "may vary",
    "remove",
    "must not appear",
)

DEFAULT_ALLOW_PATTERNS: tuple[str, ...] = (
    "minimal controlled reflections on gold accents",
    "controlled highlights on satin gold",
    "restrained reflections on gold accents",
    "small controlled gold reflections",
)

DEFAULT_DENY_CONCEPTS: dict[str, tuple[str, ...]] = {
    "STONE_TEXTURE": (
        "stone texture",
        "stone veins",
        "mineral texture",
        "marble texture",
        "lava texture",
        "crystal texture",
        "rock texture",
    ),
    "ENVIRONMENT": (
        "environment",
        "landscape",
        "interior scene",
        "ground plane",
        "floor",
        "pedestal",
        "horizon",
    ),
    "EXTRA_COLORS": (
        "additional colors",
        "extra colors",
        "multicolor",
        "multi-color",
        "colorful accents",
    ),
    "LIGHT_BACKGROUND": (
        "light background",
        "white background",
        "bright background",
        "gray background",
        "grey background",
    ),
    "MULTIPLE_SUBJECTS": (
        "multiple subjects",
        "several objects",
        "group of objects",
        "two separate objects",
        "three objects",
    ),
    "REFLECTION_POLICY": (
        "mirror reflections",
        "chrome reflections",
        "reflected environment",
        "mirror finish",
        "chrome finish",
        "highly reflective surface",
        "environment reflections",
    ),
}

NEGATION_MARKERS: tuple[str, ...] = (
    "no",
    "not",
    "without",
    "avoid",
    "exclude",
    "remove",
    "forbid",
    "prohibit",
    "never",
)


def _stem_token(token: str) -> str:
    """Normalize common English inflections without external NLP dependencies."""
    if len(token) > 5 and token.endswith("ies"):
        return token[:-3] + "y"
    for suffix in ("ingly", "edly", "ing", "ed", "es"):
        if len(token) > len(suffix) + 3 and token.endswith(suffix):
            return token[: -len(suffix)]
    if len(token) > 4 and token.endswith("s") and not token.endswith(("ss", "us")):
        return token[:-1]
    return token


def _stemmed_tokens(value: str) -> list[str]:
    return [_stem_token(token) for token in re.findall(r"[a-z0-9'-]+", normalize_text(value))]


def _sequence_positions(tokens: list[str], phrase: str) -> list[tuple[int, int]]:
    needle = _stemmed_tokens(phrase)
    if not needle or len(needle) > len(tokens):
        return []
    return [
        (index, index + len(needle))
        for index in range(0, len(tokens) - len(needle) + 1)
        if tokens[index : index + len(needle)] == needle
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate required Obsidian Gold prompt blocks and contextual conflicts. "
            "Exit 0 means valid; exit 2 means deterministic validation failure; "
            "exit 3 means an operational error."
        )
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", type=Path, help="UTF-8 prompt text file.")
    source.add_argument("--text", help="Prompt text supplied directly.")
    parser.add_argument(
        "--mode",
        choices=("generate", "edit"),
        required=True,
        help="Prompt execution mode.",
    )
    parser.add_argument(
        "--rules",
        type=Path,
        help=(
            "Optional JSON rules file with allow_patterns, deny_concepts, "
            "and required_blocks additions."
        ),
    )
    parser.add_argument("--report", type=Path, help="Optional JSON report output path.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing report file; never changes the prompt input.",
    )
    return parser


def _load_prompt(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    try:
        return args.file.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ToolError(f"Prompt file does not exist: {args.file}") from exc
    except OSError as exc:
        raise ToolError(f"Cannot read prompt file {args.file}: {exc}") from exc


def _load_rules(path: Path | None) -> tuple[
    dict[str, tuple[str, ...]],
    dict[str, tuple[str, ...]],
    tuple[str, ...],
]:
    required = {key: tuple(values) for key, values in REQUIRED_BLOCKS.items()}
    denied = {key: tuple(values) for key, values in DEFAULT_DENY_CONCEPTS.items()}
    allowed = list(DEFAULT_ALLOW_PATTERNS)
    if path is None:
        return required, denied, tuple(allowed)

    payload = read_json(path)
    if not isinstance(payload, dict):
        raise ToolError("Rules file must contain a JSON object.")

    required_additions = payload.get("required_blocks", {})
    if not isinstance(required_additions, dict):
        raise ToolError("rules.required_blocks must be an object.")
    for block, patterns in required_additions.items():
        if not isinstance(block, str) or not isinstance(patterns, list):
            raise ToolError("Each rules.required_blocks entry must be a string list.")
        if not all(isinstance(item, str) for item in patterns):
            raise ToolError("Required-block patterns must be strings.")
        required[block] = required.get(block, ()) + tuple(patterns)

    deny_additions = payload.get("deny_concepts", {})
    if not isinstance(deny_additions, dict):
        raise ToolError("rules.deny_concepts must be an object.")
    for code, phrases in deny_additions.items():
        if not isinstance(code, str) or not isinstance(phrases, list):
            raise ToolError("Each rules.deny_concepts entry must be a string list.")
        if not all(isinstance(item, str) for item in phrases):
            raise ToolError("Deny-concept phrases must be strings.")
        denied[code] = denied.get(code, ()) + tuple(
            normalize_text(item) for item in phrases
        )

    allow_additions = payload.get("allow_patterns", [])
    if not isinstance(allow_additions, list) or not all(
        isinstance(item, str) for item in allow_additions
    ):
        raise ToolError("rules.allow_patterns must be a string list.")
    allowed.extend(normalize_text(item) for item in allow_additions)

    for block, patterns in required.items():
        for pattern in patterns:
            try:
                re.compile(pattern, flags=re.IGNORECASE)
            except re.error as exc:
                raise ToolError(
                    f"Invalid required-block regex for {block}: {pattern!r}: {exc}"
                ) from exc
    return required, denied, tuple(allowed)


def _block_presence(
    normalized: str, required_blocks: dict[str, tuple[str, ...]]
) -> dict[str, bool]:
    return {
        block: any(re.search(pattern, normalized, flags=re.IGNORECASE) for pattern in patterns)
        for block, patterns in required_blocks.items()
    }


def _is_negated_tokens(tokens: list[str], start: int) -> bool:
    prefix = tokens[max(0, start - 8) : start]
    return any(marker in prefix for marker in NEGATION_MARKERS)


def _conflicts(
    normalized: str,
    deny_concepts: dict[str, tuple[str, ...]],
    allow_patterns: tuple[str, ...],
) -> list[dict[str, Any]]:
    original_tokens = re.findall(r"[a-z0-9'-]+", normalized)
    stemmed = [_stem_token(token) for token in original_tokens]
    allowed_ranges: list[tuple[int, int, str]] = []
    for phrase in allow_patterns:
        for start, end in _sequence_positions(stemmed, phrase):
            allowed_ranges.append((start, end, phrase))

    found: list[dict[str, Any]] = []
    seen_codes: set[str] = set()
    for code, phrases in deny_concepts.items():
        for phrase in phrases:
            needle = normalize_text(phrase)
            for start, end in _sequence_positions(stemmed, needle):
                overlaps_allow = any(
                    not (allow_end <= start or allow_start >= end)
                    for allow_start, allow_end, _ in allowed_ranges
                )
                suffix_free = (
                    end < len(original_tokens)
                    and original_tokens[end] == "free"
                )
                if (
                    not overlaps_allow
                    and not suffix_free
                    and not _is_negated_tokens(stemmed, start)
                    and code not in seen_codes
                ):
                    evidence = " ".join(original_tokens[start:end])
                    found.append(
                        diagnostic(
                            f"PROMPT_CONFLICT_{code}",
                            "error",
                            f"Prohibited positive requirement detected: {evidence}",
                            evidence=evidence,
                        )
                    )
                    seen_codes.add(code)
    return found


def validate(
    text: str,
    mode: str,
    *,
    rules_path: Path | None = None,
) -> dict[str, Any]:
    normalized = normalize_text(text)
    required, denied, allowed = _load_rules(rules_path)
    presence = _block_presence(normalized, required)
    diagnostics: list[dict[str, Any]] = []

    if not normalized:
        diagnostics.append(
            diagnostic("PROMPT_EMPTY", "error", "Prompt is empty.")
        )

    for block, present in presence.items():
        if not present:
            diagnostics.append(
                diagnostic(
                    "PROMPT_BLOCK_MISSING",
                    "error",
                    f"Required semantic block is missing: {block}",
                    field=block,
                )
            )

    if mode == "edit":
        for field in EDIT_FIELDS:
            if re.search(rf"(^|\n)\s*{re.escape(field)}\s*:", text, re.IGNORECASE) is None:
                diagnostics.append(
                    diagnostic(
                        "EDIT_FIELD_MISSING",
                        "error",
                        f"Required edit field is missing: {field}:",
                        field=field,
                    )
                )

    diagnostics.extend(_conflicts(normalized, denied, allowed))

    exit_code = final_exit_code(diagnostics)
    return {
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "status": "pass" if exit_code == EXIT_OK else "fail",
        "valid": exit_code == EXIT_OK,
        "mode": mode,
        "input_sha256": sha256_bytes(text.encode("utf-8")),
        "normalized_sha256": sha256_bytes(normalized.encode("utf-8")),
        "required_blocks": presence,
        "diagnostics": diagnostics,
        "exit_code": exit_code,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        prompt = _load_prompt(args)
        report = validate(prompt, args.mode, rules_path=args.rules)
        if args.report is not None:
            if (
                args.file is not None
                and args.report.resolve(strict=False) == args.file.resolve(strict=False)
            ):
                raise ToolError("Report path must not overwrite the prompt input.")
            atomic_write_json(args.report, report, force=args.force)
        emit_report(report)
        return int(report["exit_code"])
    except ToolError as exc:
        report = operational_failure(TOOL_NAME, str(exc))
        emit_report(report, stream=sys.stderr)
        return EXIT_OPERATIONAL
    except OSError as exc:
        report = operational_failure(TOOL_NAME, str(exc))
        emit_report(report, stream=sys.stderr)
        return EXIT_OPERATIONAL


if __name__ == "__main__":
    raise SystemExit(main())
