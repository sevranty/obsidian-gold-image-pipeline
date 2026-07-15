#!/usr/bin/env python3
"""Unit tests for OGP#7 deterministic tooling."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "skill/obsidian-gold-image-pipeline/scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SCRIPTS))

import build_manifest  # noqa: E402
import inspect_image  # noqa: E402
import package_asset  # noqa: E402
import validate_prompt  # noqa: E402


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_valid_image(path: Path, size: tuple[int, int] = (256, 256)) -> None:
    image = Image.new("RGB", size, (0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.polygon(
        [(72, 82), (177, 63), (198, 156), (91, 188), (58, 139)],
        fill=(26, 26, 26),
    )
    draw.rectangle((110, 105, 158, 132), fill=(199, 162, 86))
    image.save(path, format="PNG", optimize=False)


class PromptValidationTests(unittest.TestCase):
    def test_valid_generate_allows_controlled_gold_reflections(self) -> None:
        prompt = (FIXTURES / "prompts/valid-generate.txt").read_text(encoding="utf-8")
        report = validate_prompt.validate(prompt, "generate")
        self.assertTrue(report["valid"], report)
        self.assertEqual(report["exit_code"], 0)
        codes = {item["code"] for item in report["diagnostics"]}
        self.assertNotIn("PROMPT_CONFLICT_REFLECTION_POLICY", codes)

    def test_invalid_generate_reports_contextual_conflicts_and_missing_blocks(self) -> None:
        prompt = (FIXTURES / "prompts/invalid-generate.txt").read_text(encoding="utf-8")
        report = validate_prompt.validate(prompt, "generate")
        self.assertFalse(report["valid"])
        codes = {item["code"] for item in report["diagnostics"]}
        self.assertIn("PROMPT_BLOCK_MISSING", codes)
        self.assertIn("PROMPT_CONFLICT_STONE_TEXTURE", codes)
        self.assertIn("PROMPT_CONFLICT_LIGHT_BACKGROUND", codes)
        self.assertIn("PROMPT_CONFLICT_MULTIPLE_SUBJECTS", codes)

    def test_valid_edit_requires_all_contract_fields(self) -> None:
        prompt = (FIXTURES / "prompts/valid-edit.txt").read_text(encoding="utf-8")
        report = validate_prompt.validate(prompt, "edit")
        self.assertTrue(report["valid"], report)

    def test_case_and_inflection_normalization_catches_mirror_reflection(self) -> None:
        prompt = (FIXTURES / "prompts/valid-generate.txt").read_text(encoding="utf-8")
        prompt = prompt.replace(
            "minimal controlled reflections on gold accents",
            "MIRROR REFLECTION on gold accents",
        )
        report = validate_prompt.validate(prompt, "generate")
        self.assertFalse(report["valid"])
        self.assertIn(
            "PROMPT_CONFLICT_REFLECTION_POLICY",
            {item["code"] for item in report["diagnostics"]},
        )

    def test_edit_without_contract_fields_fails(self) -> None:
        prompt = (FIXTURES / "prompts/valid-generate.txt").read_text(encoding="utf-8")
        report = validate_prompt.validate(prompt, "edit")
        self.assertFalse(report["valid"])
        missing = [
            item for item in report["diagnostics"] if item["code"] == "EDIT_FIELD_MISSING"
        ]
        self.assertEqual(len(missing), 5)


class ImageInspectionTests(unittest.TestCase):
    def test_inspection_creates_64_preview_and_preserves_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "accepted.png"
            preview = directory / "preview.png"
            make_valid_image(source)
            before = file_hash(source)
            report = inspect_image.inspect(
                source,
                corner_threshold=12,
                content_threshold=18,
                edge_margin=2,
                max_file_bytes=1_000_000,
                preview_output=preview,
            )
            self.assertTrue(report["valid"], report)
            self.assertTrue(report["source_preserved"])
            self.assertEqual(file_hash(source), before)
            with Image.open(preview) as generated:
                self.assertEqual(generated.size, (64, 64))
                self.assertEqual(generated.format, "PNG")

    def test_all_black_image_fails_without_modifying_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "black.png"
            Image.new("RGB", (128, 128), (0, 0, 0)).save(source)
            before = file_hash(source)
            report = inspect_image.inspect(
                source,
                corner_threshold=12,
                content_threshold=18,
                edge_margin=2,
                max_file_bytes=1_000_000,
            )
            self.assertFalse(report["valid"])
            self.assertTrue(report["empty_or_all_black"])
            self.assertEqual(file_hash(source), before)


class ManifestTests(unittest.TestCase):
    def test_manifest_is_repeatable_for_same_spec_and_image(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            image = directory / "accepted.png"
            spec = directory / "valid-spec.json"
            out_a = directory / "manifest-a.json"
            out_b = directory / "manifest-b.json"
            make_valid_image(image)
            spec.write_bytes((FIXTURES / "manifests/valid-spec.json").read_bytes())

            first = build_manifest.main(
                [str(spec), "--selected-output", str(image), "--output", str(out_a)]
            )
            second = build_manifest.main(
                [str(spec), "--selected-output", str(image), "--output", str(out_b)]
            )
            self.assertEqual(first, 0)
            self.assertEqual(second, 0)
            self.assertEqual(out_a.read_bytes(), out_b.read_bytes())
            payload = json.loads(out_a.read_text(encoding="utf-8"))
            self.assertEqual(payload["manifest_schema_version"], "1.0.0")
            self.assertEqual(payload["selected_output_sha256"], file_hash(image))

    def test_missing_scene_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            image = directory / "accepted.png"
            spec = directory / "invalid-spec.json"
            make_valid_image(image)
            spec.write_bytes(
                (
                    FIXTURES
                    / "manifests/invalid-spec-missing-composition-fidelity.json"
                ).read_bytes()
            )
            manifest, diagnostics = build_manifest.build_manifest(spec, image)
            self.assertEqual(manifest, {})
            self.assertIn(
                "SCENE_FIELD_MISSING", {item["code"] for item in diagnostics}
            )

    def test_created_at_without_timezone_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            image = directory / "accepted.png"
            spec = directory / "invalid-created-at.json"
            make_valid_image(image)
            payload = json.loads(
                (FIXTURES / "manifests/valid-spec.json").read_text(encoding="utf-8")
            )
            payload["created_at"] = "2026-07-15T10:00:00"
            spec.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            manifest, diagnostics = build_manifest.build_manifest(spec, image)
            self.assertEqual(manifest, {})
            self.assertIn(
                "MANIFEST_CREATED_AT_TIMEZONE_MISSING",
                {item["code"] for item in diagnostics},
            )


class PackagingTests(unittest.TestCase):
    def test_package_is_non_destructive_and_complete(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            image = directory / "accepted.png"
            spec = directory / "valid-spec.json"
            manifest = directory / "manifest.json"
            package_dir = directory / "delivery/ogp-fixture-001"
            make_valid_image(image)
            spec.write_bytes((FIXTURES / "manifests/valid-spec.json").read_bytes())
            self.assertEqual(
                build_manifest.main(
                    [
                        str(spec),
                        "--selected-output",
                        str(image),
                        "--output",
                        str(manifest),
                    ]
                ),
                0,
            )
            before = {"image": file_hash(image), "manifest": file_hash(manifest)}
            report = package_asset.package(
                image,
                manifest,
                preview_path=None,
                output_dir=package_dir,
                include_webp=True,
                webp_quality=90,
            )
            self.assertTrue(report["valid"])
            self.assertTrue(report["source_preserved"])
            self.assertEqual(before["image"], file_hash(image))
            self.assertEqual(before["manifest"], file_hash(manifest))
            names = {path.name for path in package_dir.iterdir()}
            self.assertEqual(
                names,
                {
                    "accepted.png",
                    "final-image.webp",
                    "manifest.json",
                    "package-index.json",
                    "preview-64.png",
                },
            )
            packaged_manifest = json.loads(
                (package_dir / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertTrue((package_dir / packaged_manifest["selected_output"]).exists())
            with Image.open(package_dir / "preview-64.png") as preview:
                self.assertEqual(preview.size, (64, 64))


class CliContractTests(unittest.TestCase):
    def test_all_cli_parsers_produce_help(self) -> None:
        for module in (
            validate_prompt,
            inspect_image,
            build_manifest,
            package_asset,
        ):
            help_text = module.build_parser().format_help()
            self.assertIn("usage:", help_text.lower())
            self.assertIn("exit", help_text.lower())


if __name__ == "__main__":
    unittest.main()
