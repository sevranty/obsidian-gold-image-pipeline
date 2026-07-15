#!/usr/bin/env python3
"""Owner-review regression tests for OGP#7 deterministic tooling."""

from __future__ import annotations

import contextlib
import io
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


def make_image(path: Path) -> None:
    image = Image.new("RGB", (256, 256), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((64, 64, 192, 192), fill=(26, 26, 26))
    draw.rectangle((112, 112, 144, 144), fill=(199, 162, 86))
    image.save(path, format="PNG", optimize=False)


def valid_spec() -> dict[str, object]:
    return json.loads(
        (FIXTURES / "manifests/valid-spec.json").read_text(encoding="utf-8")
    )


class ReviewRegressionTests(unittest.TestCase):
    def test_invalid_custom_regex_returns_operational_exit_three(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            rules = Path(temporary) / "rules.json"
            rules.write_text(
                json.dumps({"required_blocks": {"custom": ["("]}}) + "\n",
                encoding="utf-8",
            )
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = validate_prompt.main(
                    [
                        "--file",
                        str(FIXTURES / "prompts/valid-generate.txt"),
                        "--mode",
                        "generate",
                        "--rules",
                        str(rules),
                    ]
                )
            self.assertEqual(exit_code, 3)
            self.assertEqual(json.loads(stderr.getvalue())["status"], "operational_error")

    def test_manifest_rejects_missing_qa_category(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            image, spec = directory / "accepted.png", directory / "spec.json"
            make_image(image)
            payload = valid_spec()
            del payload["qa_result"]["category_scores"]["lighting"]
            payload["qa_result"]["score_total"] = 85
            spec.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            manifest, diagnostics = build_manifest.build_manifest(spec, image)
            self.assertEqual(manifest, {})
            self.assertIn("QA_CATEGORY_MISSING", {item["code"] for item in diagnostics})

    def test_manifest_rejects_qa_total_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            image, spec = directory / "accepted.png", directory / "spec.json"
            make_image(image)
            payload = valid_spec()
            payload["qa_result"]["score_total"] = 93
            spec.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            manifest, diagnostics = build_manifest.build_manifest(spec, image)
            self.assertEqual(manifest, {})
            self.assertIn(
                "QA_SCORE_TOTAL_MISMATCH", {item["code"] for item in diagnostics}
            )

    def test_package_refuses_existing_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            image = directory / "accepted.png"
            spec = directory / "spec.json"
            manifest = directory / "manifest.json"
            package_dir = directory / "package"
            make_image(image)
            spec.write_text(json.dumps(valid_spec()) + "\n", encoding="utf-8")
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
            package_dir.mkdir()
            with self.assertRaises(package_asset.ToolError):
                package_asset.package(
                    image,
                    manifest,
                    preview_path=None,
                    output_dir=package_dir,
                    include_webp=False,
                    webp_quality=90,
                )

    def test_all_cli_missing_inputs_return_operational_exit_three(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            missing = directory / "missing.input"
            invocations = (
                lambda: validate_prompt.main(
                    ["--file", str(missing), "--mode", "generate"]
                ),
                lambda: inspect_image.main([str(missing)]),
                lambda: build_manifest.main(
                    [str(missing), "--output", str(directory / "manifest.json")]
                ),
                lambda: package_asset.main(
                    [
                        str(missing),
                        str(missing),
                        "--output-dir",
                        str(directory / "package"),
                    ]
                ),
            )
            for invoke in invocations:
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    exit_code = invoke()
                self.assertEqual(exit_code, 3)
                self.assertEqual(
                    json.loads(stderr.getvalue())["status"], "operational_error"
                )


if __name__ == "__main__":
    unittest.main()
