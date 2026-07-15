#!/usr/bin/env python3
"""Shared deterministic helpers for the Obsidian Gold tooling."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, Iterable

EXIT_OK = 0
EXIT_VALIDATION = 2
EXIT_OPERATIONAL = 3

TOOL_VERSION = "1.0.0"


class ToolError(Exception):
    """Operational error that should produce a stable machine-readable failure."""


class ToolArgumentParser(argparse.ArgumentParser):
    """Argument parser that reports usage errors through the operational contract."""

    def error(self, message: str) -> None:
        tool = Path(self.prog).stem
        emit_report(
            operational_failure(tool, f"Argument error: {message}"),
            stream=sys.stderr,
        )
        raise SystemExit(EXIT_OPERATIONAL)


def normalize_text(value: str) -> str:
    """Return a stable lowercase, whitespace-normalized Unicode representation."""
    normalized = unicodedata.normalize("NFKC", value).lower()
    normalized = normalized.replace("\u2010", "-").replace("\u2011", "-")
    normalized = normalized.replace("\u2012", "-").replace("\u2013", "-")
    normalized = normalized.replace("\u2014", "-").replace("\u2212", "-")
    return " ".join(normalized.split())


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize JSON deterministically with UTF-8, sorted keys, and a final newline."""
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            indent=2,
            separators=(",", ": "),
        )
        + "\n"
    ).encode("utf-8")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ToolError(f"Input file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ToolError(f"Invalid JSON in {path}: {exc}") from exc
    except OSError as exc:
        raise ToolError(f"Cannot read {path}: {exc}") from exc


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except FileNotFoundError as exc:
        raise ToolError(f"Input file does not exist: {path}") from exc
    except OSError as exc:
        raise ToolError(f"Cannot read {path}: {exc}") from exc
    return digest.hexdigest()


def ensure_distinct_paths(output: Path, inputs: Iterable[Path]) -> None:
    output_resolved = output.resolve(strict=False)
    for source in inputs:
        if output_resolved == source.resolve(strict=False):
            raise ToolError(f"Output path must not overwrite input: {output}")


def atomic_write_bytes(path: Path, payload: bytes, *, force: bool = False) -> None:
    path = path.resolve(strict=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        raise ToolError(f"Output already exists: {path}")
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def atomic_write_json(path: Path, value: Any, *, force: bool = False) -> None:
    atomic_write_bytes(path, canonical_json_bytes(value), force=force)


def emit_report(report: dict[str, Any], *, stream: Any = sys.stdout) -> None:
    stream.write(canonical_json_bytes(report).decode("utf-8"))
    stream.flush()


def diagnostic(
    code: str,
    severity: str,
    message: str,
    *,
    evidence: str | None = None,
    field: str | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "code": code,
        "severity": severity,
        "message": message,
    }
    if field is not None:
        item["field"] = field
    if evidence is not None:
        item["evidence"] = evidence
    return item


def final_exit_code(diagnostics: Iterable[dict[str, Any]]) -> int:
    severities = {item.get("severity") for item in diagnostics}
    if "error" in severities:
        return EXIT_VALIDATION
    return EXIT_OK


def operational_failure(tool: str, message: str) -> dict[str, Any]:
    return {
        "tool": tool,
        "tool_version": TOOL_VERSION,
        "status": "operational_error",
        "valid": False,
        "diagnostics": [
            diagnostic("OPERATIONAL_ERROR", "error", message),
        ],
    }
