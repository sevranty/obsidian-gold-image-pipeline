#!/usr/bin/env python3
"""Build the fixed OGP direct skill bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

SKILL_NAME = "obsidian-gold-image-pipeline"
ALLOWED_INTERFACE = {"display_name", "short_description", "default_prompt"}
ALLOWED_POLICY = {"allow_implicit_invocation"}
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache"}
REPOSITORY_ONLY = {"README.md"}


class PackageError(Exception):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_metadata(path: Path) -> dict[str, object]:
    metadata: dict[str, object] = {"interface": {}, "policy": {}}
    section: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not raw.startswith(" ") and line.endswith(":"):
            section = line[:-1]
            if section not in metadata:
                raise PackageError(f"Unsupported metadata section: {section}")
            continue
        if section is None or not raw.startswith("  ") or ":" not in line:
            raise PackageError(f"Invalid metadata line: {line}")
        key, value = line.strip().split(":", 1)
        value = value.strip()
        if section == "interface" and key not in ALLOWED_INTERFACE:
            raise PackageError(f"Unsupported interface key: {key}")
        if section == "policy" and key not in ALLOWED_POLICY:
            raise PackageError(f"Unsupported policy key: {key}")
        if value in {"true", "false"}:
            parsed: object = value == "true"
        elif value.startswith('"') and value.endswith('"'):
            parsed = value[1:-1]
        else:
            raise PackageError(f"Unsupported metadata value for {key}")
        metadata[section][key] = parsed  # type: ignore[index]
    policy = metadata["policy"]
    if set(policy) != ALLOWED_POLICY or not isinstance(policy.get("allow_implicit_invocation"), bool):  # type: ignore[union-attr]
        raise PackageError("Metadata policy must declare one boolean allow_implicit_invocation.")
    return metadata


def repository_root(skill_dir: Path) -> Path:
    parent = skill_dir.resolve().parents[1]
    return parent


def validate_skill_tree(skill_dir: Path) -> dict[str, object]:
    skill_dir = skill_dir.resolve(strict=True)
    if skill_dir.name != SKILL_NAME:
        raise PackageError(f"Skill root must be {SKILL_NAME}.")
    required = ["SKILL.md", "VERSIONS.json", "agents/openai.yaml", "LICENSE.txt"]
    for relative in required:
        if not (skill_dir / relative).is_file():
            raise PackageError(f"Required file missing: {relative}")
    root_license = repository_root(skill_dir) / "LICENSE"
    if not root_license.is_file() or root_license.read_bytes() != (skill_dir / "LICENSE.txt").read_bytes():
        raise PackageError("Root LICENSE and bundled LICENSE.txt must match byte-for-byte.")
    metadata = parse_metadata(skill_dir / "agents/openai.yaml")
    files: list[str] = []
    file_sha256: dict[str, str] = {}
    for path in sorted(skill_dir.rglob("*")):
        if path.is_symlink():
            raise PackageError(f"Symlinks are not allowed in the skill bundle: {path.relative_to(skill_dir).as_posix()}")
        if not path.is_file():
            continue
        relative = path.relative_to(skill_dir).as_posix()
        if any(part in EXCLUDED_PARTS for part in path.relative_to(skill_dir).parts):
            continue
        if path.name in REPOSITORY_ONLY or relative.startswith("docs/"):
            raise PackageError(f"Repository-only file present in skill bundle: {relative}")
        if not relative.isascii():
            raise PackageError(f"Non-ASCII path in bundle: {relative}")
        files.append(relative)
        file_sha256[relative] = sha256(path)
    return {"schema_version": "1.0.0", "skill_name": SKILL_NAME, "allow_implicit_invocation": metadata["policy"]["allow_implicit_invocation"], "files": files, "file_sha256": file_sha256, "license_sha256": sha256(root_license)}


def assert_output_outside_source(skill_dir: Path, output: Path) -> None:
    resolved = output.resolve()
    source = skill_dir.resolve()
    if resolved == source or source in resolved.parents:
        raise PackageError("Package outputs must not be written inside the source skill tree.")


def build(skill_dir: Path, archive_path: Path, manifest_path: Path) -> dict[str, object]:
    validation = validate_skill_tree(skill_dir)
    skill_dir = skill_dir.resolve()
    archive_path = archive_path.resolve()
    manifest_path = manifest_path.resolve()
    if archive_path == manifest_path:
        raise PackageError("Archive and manifest outputs must be different paths.")
    assert_output_outside_source(skill_dir, archive_path)
    assert_output_outside_source(skill_dir, manifest_path)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for relative in validation["files"]:  # type: ignore[index]
            info = zipfile.ZipInfo(f"{SKILL_NAME}/{relative}")
            info.date_time = (2026, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o644 << 16
            bundle.writestr(info, (skill_dir / relative).read_bytes())
    manifest = {**validation, "archive_sha256": sha256(archive_path), "archive_path": archive_path.name, "release_candidate": "0.1.0-rc.1", "release_published": False}
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the OGP direct skill archive.")
    parser.add_argument("--skill", type=Path, default=Path(__file__).resolve().parents[1] / "skill" / SKILL_NAME)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = build(args.skill, args.archive, args.manifest)
    except (OSError, PackageError, ValueError) as exc:
        sys.stderr.write(json.dumps({"status": "operational_error", "error": str(exc)}, sort_keys=True) + "\n")
        return 3
    sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
