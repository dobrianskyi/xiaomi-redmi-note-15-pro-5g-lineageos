#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/env.sh"
jobs=${BUILD_JOBS:-12}
[[ $jobs =~ ^[1-9][0-9]*$ ]] || { echo 'BUILD_JOBS must be a positive integer' >&2; exit 2; }
cd "$BRINGUP_ROOT/source"
[[ -s "$BRINGUP_ROOT/research/resolved-manifest.xml" ]] || {
 echo 'Run a successful sync-source.sh first; no resolved manifest.' >&2; exit 1;
}
python3 - <<'PY_CHECK'
from pathlib import Path
from zipfile import is_zipfile
for arch in ('arm', 'arm64'):
    apk = Path('external/chromium-webview/prebuilt') / arch / 'webview.apk'
    if not apk.is_file() or not is_zipfile(apk):
        raise SystemExit(f'{apk}: missing APK or unresolved Git LFS pointer; hydrate LFS before building')
PY_CHECK
python3 "$BRINGUP_ROOT/scripts/prepare-gapps.py" --variant "${LAPIS_GAPPS:-none}"
python3 "$BRINGUP_ROOT/scripts/prepare-ims.py"
python3 "$BRINGUP_ROOT/scripts/prepare-trebleapp.py"
python3 "$BRINGUP_ROOT/scripts/apply-build-patches.py"
mkdir -p device/local/gsi
rsync -a --checksum --no-times --exclude '__pycache__' "$BRINGUP_ROOT/local/device/local/gsi/" device/local/gsi/
printf 'LAPIS_GAPPS := %s\n' "${LAPIS_GAPPS:-none}" > device/local/gsi/build-variant.mk
source build/envsetup.sh
lunch lineage_gsi_lapis-bp4a-user
m systemimage -j"$jobs"
