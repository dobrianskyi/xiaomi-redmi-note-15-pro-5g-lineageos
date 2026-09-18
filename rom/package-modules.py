#!/usr/bin/env python3
"""Package only reviewed module directories; never include host keys or logs."""
from pathlib import Path
import hashlib
import zipfile

root = Path(__file__).resolve().parent
out = root / 'modules-out'
out.mkdir(exist_ok=True)
sums = []
for name in ('display-fix', 'fingerprint-fix', 'call-audio-fix', 'dolby-fix'):
    module = root / name / 'module'
    props = dict(line.split('=', 1) for line in (module / 'module.prop').read_text().splitlines() if '=' in line)
    target = out / f"{props['id']}-{props['version']}.zip"
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(module.rglob('*')):
            if not file.is_file():
                continue
            if file.is_symlink() or file.suffix in ('.jks', '.keystore', '.pk8', '.pem'):
                raise SystemExit(f'Refusing unexpected module file: {file.name}')
            archive.write(file, file.relative_to(module))
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert 'module.prop' in archive.namelist()
    sums.append(f'{hashlib.sha256(target.read_bytes()).hexdigest()}  {target.name}')
    print(target)
(out / 'SHA256SUMS').write_text('\n'.join(sums) + '\n')
