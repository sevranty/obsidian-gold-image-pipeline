#!/usr/bin/env python3
"""Smoke-test the fixed OGP direct skill bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

SKILL_NAME = "obsidian-gold-image-pipeline"
CLI_NAMES = ("validate_prompt.py", "inspect_image.py", "build_manifest.py", "package_asset.py")


class SmokeError(Exception):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def smoke(archive_path: Path, manifest_path: Path) -> dict[str, object]:
    archive_path = archive_path.resolve(strict=True)
    manifest = json.loads(manifest_path.resolve(strict=True).read_text(encoding="utf-8"))
    if manifest.get("archive_sha256") != digest(archive_path):
        raise SmokeError("Archive checksum does not match the package manifest.")
    prefix = f"{SKILL_NAME}/"
    with tempfile.TemporaryDirectory(prefix="ogp-smoke-") as temporary:
        destination = Path(temporary) / ".agents" / "skills"
        destination.mkdir(parents=True)
        with zipfile.ZipFile(archive_path) as bundle:
            names = bundle.namelist()
            if not names:
                raise SmokeError("Archive is empty.")
            for name in names:
                normalized = PurePosixPath(name)
                if not name.startswith(prefix) or normalized.is_absolute() or ".." in normalized.parts or "\\" in name:
                    raise SmokeError("Archive layout is outside the fixed skill root.")
            bundle.extractall(destination)
        skill_dir = destination / SKILL_NAME
        if (skill_dir / "README.md").exists() or (skill_dir / "docs").exists():
            raise SmokeError("Repository-only documentation is present in the skill bundle.")
        command_results: list[dict[str, object]] = []
        for name in CLI_NAMES:
            script = skill_dir / "scripts" / name
            completed = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True)
            if completed.returncode != 0:
                raise SmokeError(f"CLI help failed: {name}")
            command_results.append({"script": name, "exit_code": 0, "stderr_bytes": len(completed.stderr.encode("utf-8"))})
        prompt = "Generate one raster digital sculpture from the content reference. Primary subject: a recognizable tracked vehicle. Silhouette: preserve the outer contour and key proportions. Geometry: faceted planar geometry. Materials: matte manufactured obsidian-black with satin gold accents. Lighting: one broad soft key with controlled gold highlights. Composition: one isolated full object with negative space. Background: pure black background. Fidelity: preserve recognition and silhouette. Input role: content reference. Remove and forbid: no environment, stone texture, extra colors, text, logo, or watermark. Output: square 1:1 PNG raster."
        completed = subprocess.run([sys.executable, str(skill_dir / "scripts" / "validate_prompt.py"), "--text", prompt, "--mode", "generate"], capture_output=True, text=True)
        if completed.returncode != 0:
            raise SmokeError("Installed prompt validation failed.")
        return {"schema_version": "1.0.0", "status": "pass", "archive_sha256": digest(archive_path), "installed_path": f".agents/skills/{SKILL_NAME}", "cli_help_commands": 4, "prompt_validation_exit": 0, "commands": command_results, "versions": json.loads((skill_dir / "VERSIONS.json").read_text(encoding="utf-8")), "release_published": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke-test the fixed OGP skill archive.")
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = smoke(args.archive, args.manifest)
        if args.report.exists():
            raise SmokeError(f"Report already exists: {args.report}")
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (SmokeError, OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        sys.stderr.write(json.dumps({"status": "operational_error", "error": str(exc)}, sort_keys=True) + "\n")
        return 3
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
