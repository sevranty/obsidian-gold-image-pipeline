#!/usr/bin/env python3
"""Materialize the deterministic OGP#8 structural QA corpus."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BLACK, OBSIDIAN, DARK = (0, 0, 0), (26, 26, 26), (44, 44, 44)
GOLD, GOLD2 = (255, 215, 0), (199, 162, 86)
WHITE, BLUE, RED, GREEN = (242, 242, 242), (28, 130, 247), (230, 49, 54), (31, 183, 92)
RIGHTS = "self_authored_cc0_like_project_fixture"
CLASSES = [
    ("case-01-symmetric", "simple_symmetric_object", "symmetric ceremonial orb"),
    ("case-02-asymmetric", "asymmetric_object", "asymmetric folded wing"),
    ("case-03-hollow", "hollow_object", "hollow ring portal"),
    ("case-04-thin", "thin_elements", "antenna lattice"),
    ("case-05-machinery", "transport_machinery", "tracked engineering vehicle"),
    ("case-06-animal", "animal_sculpture", "stylized falcon"),
    ("case-07-architecture", "architectural_symbol", "monolithic arch tower"),
    ("case-08-finance", "financial_metaphor", "rising arrow vault"),
    ("case-09-technology", "technology_symbol", "neural core chip"),
    ("case-10-complex", "complex_to_single_object", "network city monolith"),
]
OUTPUTS = [
    ("accepted-01-symmetric-orb", 1, "accepted", []),
    ("accepted-02-hollow-portal", 3, "accepted", []),
    ("accepted-03-machinery", 5, "accepted", []),
    ("accepted-04-falcon", 6, "accepted", []),
    ("accepted-05-neural-core", 9, "accepted", []),
    ("repairable-01-edge-crop", 2, "repairable", ["composition_error"]),
    ("repairable-02-weak-light", 4, "repairable", ["lighting_error"]),
    ("repairable-03-gold-dominance", 7, "repairable", ["gold_ratio_error"]),
    ("repairable-04-stray-artifact", 8, "repairable", ["artifact_error"]),
    ("repairable-05-weak-silhouette", 10, "repairable", ["silhouette_error"]),
    ("rejected-01-environment-multiple", 1, "rejected", ["composition_error", "background_error"]),
    ("rejected-02-stone-texture", 2, "rejected", ["material_error", "style_drift"]),
    ("rejected-03-chrome", 3, "rejected", ["material_error", "style_drift"]),
    ("rejected-04-extra-colors-light-bg", 4, "rejected", ["background_error", "style_drift"]),
    ("rejected-05-crop-pseudotext", 5, "rejected", ["composition_error", "text_or_logo_error"]),
]
NOTES = {
    "accepted": "No declared blocking defect in the structural fixture.",
    "repairable": "Exactly one localized diagnostic category is declared.",
    "rejected": "One or more critical scope or style violations are declared.",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=False)


def shape(draw: ImageDraw.ImageDraw, kind: int, *, offset: int = 0, pale: bool = False) -> None:
    o, d, g = ((80, 80, 80) if pale else OBSIDIAN), ((105, 105, 105) if pale else DARK), ((230, 230, 235) if pale else GOLD2)
    if kind == 1:
        draw.ellipse((145 + offset, 70, 367 + offset, 292), fill=o, outline=d, width=5)
        draw.arc((164 + offset, 90, 348 + offset, 274), 200, 340, fill=g, width=20)
        draw.rectangle((225 + offset, 286, 287 + offset, 390), fill=o)
        draw.polygon([(184 + offset, 390), (328 + offset, 390), (294 + offset, 438), (218 + offset, 438)], fill=g)
    elif kind == 2:
        draw.polygon([(86 + offset, 380), (142 + offset, 116), (230 + offset, 72), (258 + offset, 192), (420 + offset, 108), (372 + offset, 328), (228 + offset, 420)], fill=o)
        draw.polygon([(258 + offset, 192), (420 + offset, 108), (372 + offset, 328), (292 + offset, 280)], fill=g)
    elif kind == 3:
        draw.ellipse((88, 88, 424, 424), fill=o)
        draw.ellipse((178, 178, 334, 334), fill=BLACK)
        draw.arc((106, 106, 406, 406), 210, 330, fill=g, width=30)
    elif kind == 4:
        draw.line((116, 404, 256, 82, 396, 404), fill=o, width=14)
        for y, inset in ((326, 146), (258, 176), (190, 204)):
            draw.line((inset, y, 512 - inset, y), fill=g if y == 190 else o, width=8)
        draw.ellipse((238, 58, 274, 94), fill=g)
    elif kind == 5:
        draw.rounded_rectangle((70, 246, 392, 358), radius=28, fill=o)
        draw.polygon([(152, 142), (292, 142), (334, 246), (120, 246)], fill=d)
        draw.polygon([(392, 258), (462, 224), (462, 346), (392, 330)], fill=g)
        for x in (116, 190, 266, 340):
            draw.ellipse((x - 31, 322, x + 31, 384), fill=BLACK, outline=g if x in (116, 340) else d, width=8)
    elif kind == 6:
        draw.polygon([(82, 286), (212, 196), (246, 80), (286, 190), (430, 230), (330, 286), (304, 424), (244, 316), (150, 378)], fill=o)
        draw.polygon([(286, 190), (430, 230), (330, 286), (280, 250)], fill=g)
    elif kind == 7:
        draw.rectangle((142, 92, 370, 420), fill=o)
        draw.polygon([(142, 92), (256, 42), (370, 92)], fill=d)
        draw.rounded_rectangle((208, 198, 304, 420), radius=48, fill=BLACK)
        draw.rectangle((142, 92, 370, 126), fill=g)
    elif kind == 8:
        draw.polygon([(88, 390), (88, 326), (158, 326), (158, 266), (226, 266), (226, 208), (296, 208), (296, 150), (366, 150), (366, 92), (444, 170), (366, 248), (366, 192), (324, 192), (324, 254), (254, 254), (254, 314), (184, 314), (184, 390)], fill=o)
        draw.polygon([(366, 92), (444, 170), (366, 248)], fill=g)
    elif kind == 9:
        draw.rounded_rectangle((112, 112, 400, 400), radius=52, fill=o)
        draw.ellipse((198, 198, 314, 314), fill=BLACK, outline=g, width=18)
        for x in (144, 200, 256, 312, 368):
            draw.line((x, 82, x, 112), fill=g if x == 256 else d, width=10)
            draw.line((x, 400, x, 430), fill=d, width=10)
    else:
        draw.polygon([(88, 408), (112, 150), (166, 210), (210, 86), (262, 186), (312, 118), (378, 218), (424, 170), (448, 408)], fill=o)
        for x, y in ((150, 254), (220, 174), (286, 238), (360, 204)):
            draw.ellipse((x - 13, y - 13, x + 13, y + 13), fill=g)


def render(kind: int, verdict: str) -> Image.Image:
    background = WHITE if (verdict == "rejected" and kind == 4) else BLACK
    image = Image.new("RGB", (512, 512), background)
    draw = ImageDraw.Draw(image)
    offset = -70 if (verdict == "repairable" and kind == 2) else 0
    pale = verdict == "repairable" and kind in (4, 10)
    shape(draw, kind, offset=offset, pale=pale)
    if verdict == "repairable" and kind == 7:
        draw.rectangle((142, 92, 370, 220), fill=GOLD)
    if verdict == "repairable" and kind == 8:
        draw.ellipse((470, 72, 486, 88), fill=GOLD)
    if verdict == "rejected" and kind == 1:
        draw.rectangle((0, 420, 512, 512), fill=(34, 34, 34))
        draw.ellipse((25, 320, 135, 430), fill=OBSIDIAN)
        draw.ellipse((377, 310, 500, 433), fill=GOLD2)
    if verdict == "rejected" and kind == 2:
        for x in range(70, 450, 24):
            draw.line((x, 74, x + 75, 430), fill=(82, 82, 82), width=5)
    if verdict == "rejected" and kind == 3:
        draw.arc((104, 104, 408, 408), 98, 194, fill=(248, 248, 255), width=36)
    if verdict == "rejected" and kind == 4:
        draw.line((116, 404, 256, 82, 396, 404), fill=BLUE, width=15)
        draw.line((150, 326, 362, 326), fill=RED, width=10)
        draw.line((180, 258, 332, 258), fill=GREEN, width=8)
    if verdict == "rejected" and kind == 5:
        image = image.crop((80, 0, 512, 512)).resize((512, 512))
        draw = ImageDraw.Draw(image)
        for i in range(5):
            draw.rectangle((50 + i * 54, 450, 82 + i * 54, 474), fill=WHITE)
    return image


def preview(source: Path, target: Path) -> None:
    with Image.open(source) as image:
        reduced = ImageOps.contain(image.convert("RGB"), (64, 64), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (64, 64), BLACK)
        canvas.paste(reduced, ((64 - reduced.width) // 2, (64 - reduced.height) // 2))
        save(canvas, target)


def main() -> None:
    references, outputs = [], []
    subjects = {row[0]: row[2] for row in CLASSES}
    for index, (case_id, coverage, subject) in enumerate(CLASSES, 1):
        path = ROOT / f"evals/fixtures/references/{case_id}.png"
        ref = Image.new("RGB", (320, 320), WHITE)
        draw = ImageDraw.Draw(ref)
        draw.rounded_rectangle((15, 15, 305, 305), radius=22, outline=(210, 210, 210), width=3)
        scaled = render(index, "accepted").resize((260, 260))
        ref.paste(scaled, (30, 30))
        save(ref, path)
        references.append({"id": case_id, "coverage_class": coverage, "primary_subject": subject, "source_type": "programmatic_reference_fixture", "rights_status": RIGHTS, "reference_role": "content_reference", "file": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "width": 320, "height": 320, "format": "PNG", "notes": "Self-authored geometric fixture; no external asset."})
    case_map = {1: "case-01-symmetric", 2: "case-02-asymmetric", 3: "case-03-hollow", 4: "case-04-thin", 5: "case-05-machinery", 6: "case-06-animal", 7: "case-07-architecture", 8: "case-08-finance", 9: "case-09-technology", 10: "case-10-complex"}
    for output_id, kind, verdict, codes in OUTPUTS:
        image_path = ROOT / f"examples/{verdict}/{output_id}.png"
        preview_path = ROOT / f"examples/{verdict}/{output_id}-preview-64.png"
        eval_path = ROOT / f"evals/fixtures/outputs/{output_id}.png"
        save(render(kind, verdict), image_path)
        preview(image_path, preview_path)
        eval_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(image_path, eval_path)
        outputs.append({"id": output_id, "case_id": case_map[kind], "source_type": "programmatic_structural_qa_asset", "rights_status": RIGHTS, "reference_role": "content_reference", "primary_subject": subjects[case_map[kind]], "expected_invariants": ["one isolated object or fused metaphor", "recognizable silhouette at 64px", "matte manufactured obsidian-black material", "controlled satin-gold accents", "pure black background", "no text or logo"], "known_risks": ["structural QA fixture, not image-generator evidence"], "verdict": verdict, "failure_codes": codes, "notes": NOTES[verdict], "image": image_path.relative_to(ROOT).as_posix(), "preview_64": preview_path.relative_to(ROOT).as_posix(), "eval_output": eval_path.relative_to(ROOT).as_posix(), "image_sha256": sha(image_path), "preview_sha256": sha(preview_path), "eval_output_sha256": sha(eval_path), "width": 512, "height": 512, "format": "PNG"})
    for verdict in ("accepted", "repairable", "rejected"):
        path = ROOT / f"examples/{verdict}/index.json"
        path.write_text(json.dumps({"schema_version": "1.0.0", "verdict": verdict, "cases": [item for item in outputs if item["verdict"] == verdict]}, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    checks = sorted({ROOT / item["file"] for item in references} | {ROOT / item[field] for item in outputs for field in ("image", "preview_64", "eval_output")})
    checksum_path = ROOT / "docs/evidence/ogp8-materialized-checksums.txt"
    checksum_path.parent.mkdir(parents=True, exist_ok=True)
    checksum_path.write_text("".join(f"{sha(path)}  {path.relative_to(ROOT).as_posix()}\n" for path in checks), encoding="utf-8")
    anchors = []
    for path in sorted((ROOT / "skill/obsidian-gold-image-pipeline/assets/anchors").glob("*.svg")):
        anchors.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "width": 64, "height": 64, "format": "SVG"})
    inventory = {
        "schema_version": "1.0.0",
        "project": "obsidian-gold-image-pipeline",
        "task": "OGP#8",
        "generated_at": "2026-07-15T00:00:00Z",
        "generator": "scripts/generate_evidence_corpus.py",
        "generator_type": "deterministic_programmatic_fixture_generator",
        "image_generator_output": False,
        "rights_policy": "All assets are self-authored geometric fixtures; no external, user, brand, logo, personal, or private-source image is included.",
        "counts": {"coverage_cases": 10, "accepted": 5, "repairable": 5, "rejected": 5, "runtime_anchors": 3},
        "coverage_cases": references,
        "verdict_indexes": [{"verdict": verdict, "path": f"examples/{verdict}/index.json", "sha256": sha(ROOT / f"examples/{verdict}/index.json"), "cases": 5} for verdict in ("accepted", "repairable", "rejected")],
        "runtime_anchors": anchors,
        "materialized_checksums": checksum_path.relative_to(ROOT).as_posix(),
        "manual_rubric": "docs/evidence/ogp8-manual-rubric.md",
        "inspection_report": "reports/ogp8-inspection.json",
        "manual_review": "reports/ogp8-manual-review.json",
        "limitations": ["Structural QA fixtures, not image-generator performance evidence.", "Visual verdicts require the committed manual rubric."],
    }
    inventory_path = ROOT / "docs/evidence/ogp8-inventory.json"
    inventory_path.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(inventory["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
