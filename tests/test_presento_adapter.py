#!/usr/bin/env python3
"""Offline contract checks for OGP#37; no Presento runtime or provider calls."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "skill/obsidian-gold-image-pipeline/scripts/presento_adapter.py"
SPEC = importlib.util.spec_from_file_location("ogp_presento_adapter", ADAPTER_PATH)
assert SPEC is not None and SPEC.loader is not None
adapter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adapter)


def request() -> dict:
    return {
        "schema_version": "1.0.0",
        "request_id": "ogp-contract-001",
        "provider_id": "ogp",
        "asset_kind": "raster-image",
        "prompt_profile": None,
        "requirements": {"width_px": 8, "height_px": 8},
        "config": {"style": "obsidian-gold", "revision": 1},
    }


class PresentoAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.asset = self.root / "accepted.png"
        self.manifest = self.root / "manifest.json"
        Image.new("RGB", (8, 8), (0, 0, 0)).save(self.asset, "PNG")
        self.digest = hashlib.sha256(self.asset.read_bytes()).hexdigest()
        self.data = {
            "qa_result": {"verdict": "ACCEPT"},
            "selected_output": "accepted.png",
            "selected_output_sha256": self.digest,
            "output_dimensions": {"width": 8, "height": 8},
        }
        self.save_manifest()

    def save_manifest(self) -> None:
        self.manifest.write_text(json.dumps(self.data), encoding="utf-8")

    def result(self, req=None, revision="ogp-verified-sha"):
        return adapter.result_from_accepted_asset(
            request() if req is None else req,
            manifest_path=self.manifest,
            asset_path=self.asset,
            provider_revision=revision,
        )

    def test_success_has_exact_presento_fields_and_provenance(self) -> None:
        result = self.result()
        self.assertEqual(set(result), {
            "schema_version", "request_id", "provider_id", "provider_project_id",
            "provider_revision", "config_sha256", "asset_kind", "materialization",
            "mime_type", "path", "checksum", "dimensions", "diagnostics",
        })
        self.assertEqual(result["checksum"], self.digest)
        self.assertEqual(result["dimensions"], {"width_px": 8, "height_px": 8})
        self.assertEqual(result["path"], self.asset.as_posix())
        self.assertEqual(len(result["config_sha256"]), 64)
        self.assertEqual(result["diagnostics"], [])

    def test_explicit_executor_returns_accepted_bytes_only(self) -> None:
        execute = adapter.make_executor(self.manifest, self.asset)
        payload, mime, dims = execute(request(), self.root / "presento-output")
        self.assertEqual(hashlib.sha256(payload).hexdigest(), self.digest)
        self.assertEqual(mime, "image/png")
        self.assertEqual(dims, {"width_px": 8, "height_px": 8})
        self.assertFalse((self.root / "presento-output").exists())

    def test_missing_revision_is_rejected(self) -> None:
        with self.assertRaises(adapter.AdapterError) as caught:
            self.result(revision="")
        self.assertEqual(caught.exception.code, "missing_provider_revision")

    def test_changed_bytes_fail_closed(self) -> None:
        Image.new("RGB", (8, 8), (1, 0, 0)).save(self.asset, "PNG")
        with self.assertRaises(adapter.AdapterError) as caught:
            self.result()
        self.assertEqual(caught.exception.code, "asset_checksum_mismatch")

    def test_unaccepted_qa_fails_closed(self) -> None:
        self.data["qa_result"]["verdict"] = "BLOCKED"
        self.save_manifest()
        with self.assertRaises(adapter.AdapterError) as caught:
            self.result()
        self.assertEqual(caught.exception.code, "not_accepted")

    def test_missing_checksum_fails_closed(self) -> None:
        del self.data["selected_output_sha256"]
        self.save_manifest()
        with self.assertRaises(adapter.AdapterError) as caught:
            self.result()
        self.assertEqual(caught.exception.code, "missing_asset_provenance")

    def test_invalid_provider_and_asset_kind_fail_closed(self) -> None:
        for field, value in (("provider_id", "mfp"), ("asset_kind", "3d-render")):
            with self.subTest(field=field):
                req = request()
                req[field] = value
                with self.assertRaises(adapter.AdapterError) as caught:
                    self.result(req)
                self.assertEqual(caught.exception.code, "unsupported_capability")

    def test_dimensions_mismatch_fails_closed(self) -> None:
        self.data["output_dimensions"]["width"] = 9
        self.save_manifest()
        with self.assertRaises(adapter.AdapterError) as caught:
            self.result()
        self.assertEqual(caught.exception.code, "dimensions_mismatch")


if __name__ == "__main__":
    unittest.main()
