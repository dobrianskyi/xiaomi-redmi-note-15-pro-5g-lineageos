#!/usr/bin/env python3
"""Fetch only the pinned Android 16 GApps source; never update an existing checkout."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--variant', choices=['none', 'minimal', 'full'], required=True)
p.add_argument('--check', action='store_true')
args = p.parse_args()
if args.variant == 'none':
    print('Vanilla: GApps not required')
    raise SystemExit(0)
config = json.loads((root / 'research/gapps-source.json').read_text())
target = root / 'source/vendor/gapps'
if not target.exists():
    if args.check:
        raise SystemExit('Pinned GApps are missing; normal build downloads them automatically.')
    with tempfile.TemporaryDirectory(prefix='.gapps-', dir=target.parent) as temporary:
        checkout = Path(temporary) / 'checkout'
        subprocess.run(['git', 'init', '-q', str(checkout)], check=True)
        def git(*arguments):
            subprocess.run(['git', '-C', str(checkout), *arguments], check=True)
        git('remote', 'add', 'origin', config['url'])
        git('fetch', '--depth=1', 'origin', config['revision'])
        git('checkout', '--detach', config['revision'])
        checkout.rename(target)
if target.is_symlink() or not (target / '.git').is_dir():
    raise SystemExit('Refusing an unexpected GApps directory')
def read(*arguments):
    return subprocess.run(['git', '-C', str(target), *arguments], capture_output=True,
                          text=True, check=True).stdout.strip()
if read('rev-parse', 'HEAD') != config['revision'] or read('status', '--porcelain'):
    raise SystemExit('GApps checkout is modified or uses an unpinned revision; review it first.')
print('Verified MindTheGapps Android 16 revision ' + config['revision'])
