#!/usr/bin/env python3
"""Build the pinned lapis TrebleApp from source, without Qualcomm handlers."""
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
COMMIT = '96acf04e74d42a08cc841688686ad3c5d8bd5790'
URL = 'https://github.com/TrebleDroid/treble_app.git'
PATCH = ROOT / 'patches/treble_app/0001-lapis-no-qualcomm.patch'
DEST = ROOT / 'local/device/local/gsi/apps/TrebleApp/app.apk'
CACHE = ROOT / 'cache/treble-app'
CACHE.mkdir(parents=True, exist_ok=True)
STAMP = CACHE / 'build.json'
recipe = hashlib.sha256(COMMIT.encode() + PATCH.read_bytes() + Path(__file__).read_bytes()).hexdigest()

def run(*args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if STAMP.exists() and DEST.exists():
    previous = json.loads(STAMP.read_text())
    if previous.get('recipe') == recipe and previous.get('apk_sha256') == sha(DEST):
        print('Verified cached lapis TrebleApp (no Qualcomm handlers)')
        raise SystemExit(0)

repo = ROOT / 'repos/treble_app'
if not (repo / '.git').exists():
    repo.parent.mkdir(exist_ok=True)
    run('git', 'clone', '--no-checkout', URL, repo)
if subprocess.run(['git', '-C', str(repo), 'cat-file', '-e', COMMIT + '^{commit}'],
                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
    run('git', '-C', repo, 'fetch', URL, COMMIT)
# Build in a disposable export: never edit the reference checkout.
work = CACHE / 'source'
if work.exists():
    shutil.rmtree(work)
work.mkdir()
archive = subprocess.check_output(['git', '-C', str(repo), 'archive', COMMIT])
with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
    tar.extractall(work, filter='data')
# Without a nested repository git apply would silently skip paths outside the
# parent bring-up repository's cache/ subdirectory prefix.
run('git', 'init', '-q', work)
run('git', 'apply', '--check', PATCH, cwd=work)
run('git', 'apply', PATCH, cwd=work)

env = os.environ.copy()
if not env.get('JAVA_HOME'):
    javac = shutil.which('javac')
    if not javac:
        raise SystemExit('JDK 17 is required; set JAVA_HOME')
    env['JAVA_HOME'] = str(Path(javac).resolve().parent.parent)
env['PATH'] = env['JAVA_HOME'] + '/bin:' + env['PATH']
# Reuse an SDK when present; otherwise bootstrap a project-local one.
sdk = Path(env.get('ANDROID_HOME', str(Path.home() / 'Android/Sdk')))
manager = sdk / 'cmdline-tools/latest/bin/sdkmanager'
if not manager.exists():
    sdk = ROOT / 'tools/android-sdk'
    manager = sdk / 'cmdline-tools/latest/bin/sdkmanager'
if not manager.exists():
    package = CACHE / 'commandlinetools-linux-14742923.zip'
    if not package.exists():
        urllib.request.urlretrieve('https://dl.google.com/android/repository/commandlinetools-linux-14742923_latest.zip', package)
    # Google's repository2-1.xml pins this SDK tools 20.0 archive with SHA-1.
    if hashlib.sha1(package.read_bytes()).hexdigest() != '48833c34b761c10cb20bcd16582129395d121b27':
        raise SystemExit('Android SDK tools checksum mismatch')
    unpack = CACHE / 'sdk-unpack'
    with zipfile.ZipFile(package) as z:
        z.extractall(unpack)
    manager.parent.parent.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(unpack / 'cmdline-tools'), str(manager.parent.parent))
    for f in manager.parent.iterdir():
        f.chmod(f.stat().st_mode | 0o111)
env['ANDROID_HOME'] = str(sdk)
if not (sdk / 'platforms/android-33/android.jar').exists() or not (sdk / 'build-tools/30.0.3/aapt2').exists():
    run(manager, '--licenses', input='y\n' * 100, text=True, env=env)
    run(manager, 'platforms;android-33', 'build-tools;30.0.3', env=env)
run(work / 'gradlew', '--no-daemon', 'assembleRelease', cwd=work, env=env)
apk = work / 'app/build/outputs/apk/release/app-release-unsigned.apk'
with zipfile.ZipFile(apk) as package:
    dex = b''.join(package.read(n) for n in package.namelist() if n.endswith('.dex'))
    if any(value in dex for value in (b'Lvendor/qti/', b'Lme/phh/treble/app/QtiAudio;',
                                     b'Starting Qualcomm service')):
        raise SystemExit('Qualcomm implementation unexpectedly present in lapis APK')
DEST.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(apk, DEST)
STAMP.write_text(json.dumps(dict(recipe=recipe, commit=COMMIT, patch_sha256=sha(PATCH),
                                apk_sha256=sha(DEST)), indent=2) + '\n')
print('Built lapis TrebleApp from pinned source; platform signing is done by Android')
