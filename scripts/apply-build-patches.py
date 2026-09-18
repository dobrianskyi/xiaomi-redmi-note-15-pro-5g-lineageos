#!/usr/bin/env python3
"""Apply reviewed patch sequences; recognize their cumulative tree on reruns."""
from pathlib import Path
import json
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = root / 'source'
projects = {}
for item in json.loads((root / 'patches/series.json').read_text()):
    project = (source / item['project']).resolve()
    patch = (root / 'patches' / item['patch']).resolve()
    if not project.is_relative_to(source) or not patch.is_relative_to(root / 'patches'):
        raise SystemExit('Patch series path escapes workspace')
    projects.setdefault(project, []).append((item, patch))

(root / 'cache').mkdir(exist_ok=True)
(root / 'cache/build-patches-applied').write_text(
    'Do not resync over local patch commits. Use a fresh checkout for updates.\n')
for project, entries in projects.items():
    def git(*args, **kwargs):
        return subprocess.run(['git', '-C', str(project), *args], **kwargs)

    name = entries[0][0]['project']
    base = entries[0][0]['base']
    if any(item['base'] != base for item, _ in entries):
        raise SystemExit(f'Inconsistent patch bases for {name}')
    if git('status', '--porcelain', capture_output=True, text=True, check=True).stdout:
        raise SystemExit(f'Dirty project: {name}; review before patching')
    head_tree = git('rev-parse', 'HEAD^{tree}', capture_output=True,
                    text=True, check=True).stdout.strip()
    # A later patch can edit a file created by an earlier one, invalidating an
    # individual reverse-apply check. Compare cumulative trees instead. The
    # temporary index does not change the real index or working tree.
    applied = None
    with tempfile.TemporaryDirectory(prefix='build-patches-') as directory:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(directory) / 'index'))
        git('read-tree', base, env=env, check=True)
        for count in range(len(entries) + 1):
            tree = git('write-tree', env=env, capture_output=True,
                       text=True, check=True).stdout.strip()
            if tree == head_tree:
                applied = count
            if count < len(entries):
                git('apply', '--cached', str(entries[count][1]), env=env, check=True)
    if applied is None:
        raise SystemExit(f'Unexpected source tree for {name}; does not match the '
                         'pinned base or a reviewed patch prefix. Review before patching.')
    for count, (item, patch) in enumerate(entries):
        if count < applied:
            print('Already applied:', item['patch'])
            continue
        git('apply', '--check', str(patch), check=True)
        git('am', str(patch), check=True)
