#!/usr/bin/env python3
"""Validate the deterministic OGP#8 visual evidence corpus."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image

ALLOWED_DIAGNOSTICS = {
    'semantic_error', 'subject_error', 'silhouette_error', 'composition_error',
    'style_drift', 'material_error', 'gold_ratio_error', 'lighting_error',
    'background_error', 'geometry_error', 'artifact_error',
    'text_or_logo_error', 'delivery_error'
}
FORBIDDEN_TOKENS = ('Finu' + 'slugi', 'Фину' + 'слуги', 'MO' + 'EX', 'F' + 'DS', 'FF' + '0508')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    inventory_path = root / 'docs/evidence/ogp8-inventory.json'
    if not inventory_path.exists():
        return {'status':'fail','errors':['inventory missing'],'warnings':[]}
    inventory = json.loads(inventory_path.read_text(encoding='utf-8'))
    refs = inventory.get('references', inventory.get('coverage_cases', []))
    outputs = inventory.get('outputs', [])
    if not outputs:
        for entry in inventory.get('verdict_indexes', []):
            index_path = root / entry.get('path', '')
            if not index_path.exists():
                fail(errors, f"verdict index missing: {entry.get('path')}")
                continue
            payload = json.loads(index_path.read_text(encoding='utf-8'))
            outputs.extend(payload.get('cases', []))
    counts = inventory.get('counts', {})

    for entry in inventory.get('verdict_indexes', []):
        index_path = root / entry.get('path', '')
        if not index_path.exists():
            fail(errors, f"verdict index missing: {entry.get('path')}")
        elif sha(index_path) != entry.get('sha256'):
            fail(errors, f"verdict index checksum mismatch: {entry.get('path')}")

    checksum_path = root / inventory.get('materialized_checksums', '')
    declared_checksums: dict[str, str] = {}
    if not checksum_path.exists():
        fail(errors, 'materialized checksum manifest missing')
    else:
        for line in checksum_path.read_text(encoding='utf-8').splitlines():
            digest, separator, relative = line.partition('  ')
            if not separator or len(digest) != 64:
                fail(errors, f'invalid checksum line: {line}')
                continue
            declared_checksums[relative] = digest
        if len(declared_checksums) != 55:
            fail(errors, f'materialized checksum entries must be 55, got {len(declared_checksums)}')

    expected_counts = {'coverage_cases':10,'accepted':5,'repairable':5,'rejected':5,'runtime_anchors':3}
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            fail(errors, f'count {key}: expected {expected}, got {counts.get(key)}')
    if len(refs) != 10:
        fail(errors, f'reference count must be 10, got {len(refs)}')
    verdict_counts = {v: sum(o.get('verdict') == v for o in outputs) for v in ('accepted','repairable','rejected')}
    for verdict, expected in [('accepted',5),('repairable',5),('rejected',5)]:
        if verdict_counts[verdict] != expected:
            fail(errors, f'{verdict} count must be {expected}, got {verdict_counts[verdict]}')

    coverage_classes = {r.get('coverage_class') for r in refs}
    if len(coverage_classes) != 10:
        fail(errors, f'coverage classes must be unique and total 10, got {len(coverage_classes)}')

    inspection_path = root / 'reports/ogp8-inspection.json'
    inspection_payload = json.loads(inspection_path.read_text(encoding='utf-8')) if inspection_path.exists() else {'reports': []}
    inspection_by_id = {Path(item.get('source','')).stem: item for item in inspection_payload.get('reports', [])}
    seen_ids: set[str] = set()
    checked_files = 0
    for record in refs + outputs:
        rid = record.get('id')
        if not isinstance(rid, str) or not rid:
            fail(errors, 'record id missing')
            continue
        if rid in seen_ids:
            fail(errors, f'duplicate id: {rid}')
        seen_ids.add(rid)
        if record.get('rights_status') != 'self_authored_cc0_like_project_fixture':
            fail(errors, f'{rid}: rights_status not approved')
        if not str(record.get('source_type','')).startswith('programmatic_'):
            fail(errors, f'{rid}: source_type not programmatic')
        file_fields = [('file','sha256')] if record in refs else [('image','image_sha256'),('preview_64','preview_sha256'),('eval_output','eval_output_sha256')]
        for file_field, hash_field in file_fields:
            rel = record.get(file_field)
            if not isinstance(rel, str):
                fail(errors, f'{rid}: {file_field} missing')
                continue
            if not rel.isascii():
                fail(errors, f'{rid}: non-ASCII path {rel}')
            path = root / rel
            if not path.exists():
                fail(errors, f'{rid}: missing {rel}')
                continue
            checked_files += 1
            actual_digest = sha(path)
            if actual_digest != record.get(hash_field):
                fail(errors, f'{rid}: checksum mismatch for {rel}')
            if declared_checksums.get(rel) != actual_digest:
                fail(errors, f'{rid}: materialized checksum manifest mismatch for {rel}')
            with Image.open(path) as image:
                image.load()
                if image.format != 'PNG':
                    fail(errors, f'{rid}: non-PNG asset {rel}')
                if file_field == 'preview_64' and image.size != (64,64):
                    fail(errors, f'{rid}: preview is {image.size}, expected 64x64')
        if record in outputs:
            codes = record.get('failure_codes')
            if not isinstance(codes, list) or any(code not in ALLOWED_DIAGNOSTICS for code in codes):
                fail(errors, f'{rid}: invalid failure_codes')
            if record.get('verdict') == 'accepted' and codes:
                fail(errors, f'{rid}: accepted record has failure codes')
            if record.get('verdict') == 'repairable' and len(codes) != 1:
                fail(errors, f'{rid}: repairable record must have exactly one diagnostic category')
            if record.get('verdict') == 'rejected' and not codes:
                fail(errors, f'{rid}: rejected record requires failure codes')
            report = inspection_by_id.get(rid)
            if report is None:
                fail(errors, f'{rid}: OGP#7 inspection report missing')
            else:
                if not report.get('source_preserved'):
                    fail(errors, f'{rid}: OGP#7 source_preserved false')
                if report.get('source_sha256') != record.get('image_sha256'):
                    fail(errors, f'{rid}: OGP#7 report SHA does not match indexed image')
                if report.get('width') != 512 or report.get('height') != 512 or report.get('format') != 'PNG':
                    fail(errors, f'{rid}: OGP#7 technical dimensions/format mismatch')
                if record.get('verdict') == 'accepted' and report.get('exit_code') != 0:
                    fail(errors, f'{rid}: accepted output failed OGP#7 technical inspection')
                if record.get('verdict') != 'accepted' and report.get('exit_code') == 0:
                    warnings.append(f'{rid}: deterministic inspection passes; rejection/repair remains a manual visual verdict')

    anchors = sorted((root / 'skill/obsidian-gold-image-pipeline/assets/anchors').glob('*.svg'))
    if len(anchors) != 3:
        fail(errors, f'runtime SVG anchors must be 3, got {len(anchors)}')
    anchor_inventory = {entry.get('path'): entry for entry in inventory.get('runtime_anchors', [])}
    for path in anchors:
        text = path.read_text(encoding='utf-8')
        relative = path.relative_to(root).as_posix()
        if 'width="64"' not in text or 'height="64"' not in text:
            fail(errors, f'runtime SVG anchor must declare 64x64: {path.name}')
        if anchor_inventory.get(relative, {}).get('sha256') != sha(path):
            fail(errors, f'runtime anchor inventory checksum mismatch: {relative}')

    text_files = sorted(p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in {'.md','.json','.txt','.py','.yaml','.yml'})
    for path in text_files:
        data = path.read_bytes()
        if not data.endswith(b'\n'):
            fail(errors, f'final newline missing: {path.relative_to(root)}')
        text = data.decode('utf-8')
        for token in FORBIDDEN_TOKENS:
            if token in text:
                fail(errors, f'forbidden token {token!r}: {path.relative_to(root)}')
    all_paths = [p.relative_to(root).as_posix() for p in root.rglob('*')]
    for rel in all_paths:
        if not rel.isascii():
            fail(errors, f'non-ASCII repository path: {rel}')

    return {
        'schema_version':'1.0.0','task':'OGP#8','status':'pass' if not errors else 'fail','counts':counts,'verdict_counts':verdict_counts,
        'checked_binary_references_and_outputs':checked_files,'inspection_reports':len(inspection_by_id),'runtime_anchors':len(anchors),'text_files_checked':len(text_files),
        'ascii_paths':not any('non-ASCII repository path' in e for e in errors),'forbidden_tokens_absent':not any('forbidden token' in e for e in errors),'errors':errors,'warnings':warnings,
        'limitations':['OGP#7 deterministic inspection does not judge aesthetics, material realism, semantic recognition, or gold coverage.','All visual verdicts are structural manual-rubric fixtures, not image-generator performance claims.']
    }


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(); parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]); parser.add_argument('--output',type=Path); args=parser.parse_args(argv); report=validate(args.root.resolve()); payload=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if args.output: args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(payload,encoding='utf-8')
    sys.stdout.write(payload); return 0 if report['status']=='pass' else 2

if __name__=='__main__':
    raise SystemExit(main())
