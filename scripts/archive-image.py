#!/usr/bin/env python3
"""Publish a verified copy without overwriting previously archived images."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def archive(image, variant, inspection=None, log=None, publish=True):
    image = image.resolve(strict=True)
    if not image.is_relative_to(ROOT):
        raise ValueError('Image must be inside this workspace')
    digest = hashlib.file_digest(image.open('rb'), 'sha256').hexdigest()
    parent = ROOT / 'out' / variant
    if parent.is_symlink() or (ROOT / 'out').is_symlink():
        raise ValueError('Archive directory must not be a symlink')
    parent.mkdir(parents=True, exist_ok=True)
    destination = None
    for manifest in parent.glob('*/manifest.json'):
        if manifest.parent.name == 'latest' or manifest.parent.name.startswith('.'):
            continue
        data = json.loads(manifest.read_text())
        if data['sha256'] == digest:
            existing = manifest.parent / 'system.img'
            if hashlib.file_digest(existing.open('rb'), 'sha256').hexdigest() != digest:
                raise ValueError(f'Archived image is damaged: {existing}')
            destination = manifest.parent
            break
    if destination is None:
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        destination = parent / f'{stamp}-{digest[:12]}'
        temporary = Path(tempfile.mkdtemp(prefix='.partial-', dir=parent))
        try:
            copy = temporary / 'system.img'
            subprocess.run(['cp', '--reflink=auto', '--sparse=always', '--preserve=timestamps',
                            str(image), str(copy)], check=True)
            if hashlib.file_digest(copy.open('rb'), 'sha256').hexdigest() != digest:
                raise ValueError('Image changed during archival; refusing to publish')
            data = {'variant': variant, 'sha256': digest, 'bytes': copy.stat().st_size,
                    'archived_at_utc': stamp, 'source_image': str(image.relative_to(ROOT)),
                    'inspection_included': bool(inspection),
                    'archiving_recipe_patch_series_sha256': hashlib.sha256((ROOT / 'patches/series.json').read_bytes()).hexdigest()}
            if variant != 'vanilla':
                data['gapps_source'] = json.loads((ROOT / 'research/gapps-source.json').read_text())
            if inspection and inspection.exists():
                report = json.loads(inspection.read_text())
                if report['sha256'] != digest:
                    raise ValueError('Inspection SHA256 does not match image')
                shutil.copy2(inspection, temporary / 'system.img.inspection.json')
            if log and log.exists():
                shutil.copy2(log, temporary / 'build.log')
            (temporary / 'manifest.json').write_text(json.dumps(data, indent=2) + '\n')
            (temporary / 'SHA256SUMS').write_text(f'{digest}  system.img\n')
            temporary.rename(destination)
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)
    # A pre-build rescue copy must never replace the last successful pointer.
    if not publish:
        print(destination / 'system.img')
        return
    if inspection:
        report = json.loads(inspection.read_text())
        if report['sha256'] != digest:
            raise ValueError('Inspection SHA256 does not match image')
        if not (destination / 'system.img.inspection.json').exists():
            shutil.copy2(inspection, destination / 'system.img.inspection.json')
            manifest = destination / 'manifest.json'
            data = json.loads(manifest.read_text())
            data['inspection_included'] = True
            replacement = destination / '.manifest-new'
            replacement.write_text(json.dumps(data, indent=2) + '\n')
            os.replace(replacement, manifest)
    if log and log.exists() and not (destination / 'build.log').exists():
        shutil.copy2(log, destination / 'build.log')
    link = parent / '.latest-new'
    link.unlink(missing_ok=True)
    link.symlink_to(destination.name)
    os.replace(link, parent / 'latest')
    print(destination / 'system.img')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', choices=['vanilla', 'gapps-minimal', 'gapps-full'], required=True)
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--inspection', type=Path)
    parser.add_argument('--log', type=Path)
    parser.add_argument('--preserve-only', action='store_true')
    args = parser.parse_args()
    archive(args.image, args.variant, args.inspection, args.log, not args.preserve_only)
