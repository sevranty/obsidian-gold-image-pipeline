#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_skill_package
import smoke_test_install

SKILL = ROOT / "skill/obsidian-gold-image-pipeline"


class DistributionTests(unittest.TestCase):
    def test_metadata_and_tree_validate(self) -> None:
        result = build_skill_package.validate_skill_tree(SKILL)
        self.assertEqual(result["skill_name"], "obsidian-gold-image-pipeline")
        self.assertTrue(result["allow_implicit_invocation"])
        self.assertGreater(len(result["files"]), 20)

    def test_reproducible_archives(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = build_skill_package.build(SKILL, root / "a.zip", root / "a.json")
            second = build_skill_package.build(SKILL, root / "b.zip", root / "b.json")
            self.assertEqual(first["archive_sha256"], second["archive_sha256"])
            self.assertEqual((root / "a.zip").read_bytes(), (root / "b.zip").read_bytes())

    def test_archive_contains_only_skill_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "skill.zip"
            build_skill_package.build(SKILL, archive, root / "manifest.json")
            with zipfile.ZipFile(archive) as bundle:
                names = bundle.namelist()
            self.assertTrue(names)
            self.assertTrue(all(name.startswith("obsidian-gold-image-pipeline/") for name in names))
            self.assertFalse(any("README.md" in name or "/docs/" in name for name in names))

    def test_smoke_test_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive, manifest = root / "skill.zip", root / "manifest.json"
            build_skill_package.build(SKILL, archive, manifest)
            report = smoke_test_install.smoke(archive, manifest)
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["cli_help_commands"], 4)
            self.assertEqual(report["prompt_validation_exit"], 0)

    def test_repository_only_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "LICENSE").write_bytes((ROOT / "LICENSE").read_bytes())
            copy = root / "skill/obsidian-gold-image-pipeline"
            shutil.copytree(SKILL, copy)
            (copy / "README.md").write_text("not runtime\n", encoding="utf-8")
            with self.assertRaises(build_skill_package.PackageError):
                build_skill_package.validate_skill_tree(copy)

    def test_unknown_external_dependencies_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "LICENSE").write_bytes((ROOT / "LICENSE").read_bytes())
            copy = root / "skill/obsidian-gold-image-pipeline"
            shutil.copytree(SKILL, copy)
            path = copy / "agents/openai.yaml"
            path.write_text(path.read_text(encoding="utf-8") + "dependencies:\n  tools: \"invented\"\n", encoding="utf-8")
            with self.assertRaises(build_skill_package.PackageError):
                build_skill_package.validate_skill_tree(copy)

    def test_invalid_archive_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive, manifest = root / "invalid.zip", root / "manifest.json"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("other-skill/file.txt", "x")
            manifest.write_text('{"archive_sha256":"' + smoke_test_install.digest(archive) + '"}\n', encoding="utf-8")
            with self.assertRaises(smoke_test_install.SmokeError):
                smoke_test_install.smoke(archive, manifest)

    def test_outputs_inside_source_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "LICENSE").write_bytes((ROOT / "LICENSE").read_bytes())
            copy = root / "skill/obsidian-gold-image-pipeline"
            shutil.copytree(SKILL, copy)
            with self.assertRaises(build_skill_package.PackageError):
                build_skill_package.build(copy, copy / "bundle.zip", root / "manifest.json")

    def test_unknown_metadata_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "LICENSE").write_bytes((ROOT / "LICENSE").read_bytes())
            copy = root / "skill/obsidian-gold-image-pipeline"
            shutil.copytree(SKILL, copy)
            path = copy / "agents/openai.yaml"
            path.write_text(path.read_text(encoding="utf-8").replace("  display_name:", "  invented: \"x\"\n  display_name:"), encoding="utf-8")
            with self.assertRaises(build_skill_package.PackageError):
                build_skill_package.validate_skill_tree(copy)

    def test_bundled_license_must_match_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "LICENSE").write_text("different\n", encoding="utf-8")
            copy = root / "skill/obsidian-gold-image-pipeline"
            shutil.copytree(SKILL, copy)
            with self.assertRaises(build_skill_package.PackageError):
                build_skill_package.validate_skill_tree(copy)


if __name__ == "__main__":
    unittest.main()
