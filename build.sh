#!/usr/bin/env bash
# Local, incremental LineageOS 23.2 / Android 16 build for the prepared workspace.
set -eo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
root=$PWD
jobs=12
check_only=false
clean=false
gapps=none

usage() {
 cat <<'EOF'
Build LineageOS 23.2 / Android 16 (user, ARM64 GSI).

  ./build.sh --gapps none       vanilla without Google (default)
  ./build.sh --gapps minimal    minimal Google services + Play Store
  ./build.sh --gapps full       extended MindTheGapps selection (see docs/BUILD_VARIANTS.md)
  ./build.sh --jobs 8           parallel jobs (default 12)
  ./build.sh --clean            clean only the selected variant build cache
  ./build.sh --check            check prerequisites without compiling/downloading
  ./build.sh --help             show help

Variants have separate build directories and resume their own outputs.
Images: out/<variant>/<timestamp-SHA256>/system.img; latest points to the newest.
--clean preserves archived images. Ctrl+C stops the build.
Missing GApps are fetched from the pinned revision on a normal build.
EOF
}

while (($#)); do
 case "$1" in
  --gapps)
   [[ $# -ge 2 && $2 =~ ^(none|minimal|full)$ ]] || {
    echo "Specify none, minimal or full after --gapps." >&2; exit 2;
   }
   gapps=$2; shift 2 ;;
  --jobs)
   [[ $# -ge 2 && $2 =~ ^[1-9][0-9]*$ ]] || {
    echo 'Error: --jobs requires a positive integer.' >&2; exit 2;
   }
   jobs=$2; shift 2 ;;
  --check) check_only=true; shift ;;
  --clean) clean=true; shift ;;
  --help|-h) usage; exit 0 ;;
  *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
 esac
done

if $clean && $check_only; then
 echo '--clean and --check cannot be combined.' >&2; exit 2
fi

source "$root/scripts/env.sh"
for tool in git python3 flock tee rsync make bison flex zip unzip gperf bc; do
 command -v "$tool" >/dev/null || { echo "Missing tool: $tool" >&2; exit 1; }
done
[[ -d source/.repo && -f source/build/envsetup.sh && -s research/resolved-manifest.xml ]] || {
 echo "Sources are not prepared. See $root/docs/BUILD.md" >&2; exit 1;
}
python3 - <<'PY'
from pathlib import Path
from zipfile import is_zipfile
for arch in ('arm', 'arm64'):
    apk = Path('source/external/chromium-webview/prebuilt') / arch / 'webview.apk'
    if not apk.is_file() or not is_zipfile(apk):
        raise SystemExit(f'Missing complete WebView APK: {apk}. See Git LFS in docs/BUILD.md.')
PY

case "$gapps" in
 none) variant=vanilla; build_out="$root/source/out" ;;
 minimal|full) variant="gapps-$gapps"; build_out="$root/source/out-$variant" ;;
esac
# Explicit paths prevent an inherited OUT_DIR from mixing variants.
export OUT_DIR="${build_out##*/}"
unset OUT_DIR_COMMON_BASE
image="$build_out/target/product/tdgsi_arm64_ab/system.img"
echo "Target: LineageOS 23.2 / Android 16, $variant ARM64 A/B EXT4 GSI"
echo "Build files: $build_out"
echo "Images: $root/out/$variant/"
echo "Working directory: $root"
echo "Parallel jobs: $jobs"
if $check_only; then
 python3 "$root/scripts/prepare-gapps.py" --variant "$gapps" --check
 echo 'Preflight passed. Compilation was not started.'
 exit 0
fi

# Keep the lock through artifact inspection as well as compilation.
exec 9>"$root/cache/build.lock"
flock -n 9 || { echo 'Another build.sh instance is already running.' >&2; exit 1; }
mkdir -p logs
log=$(mktemp "$root/logs/build-$variant-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX.log")
ln -sfn "${log##*/}" "$root/logs/latest-build.log"
echo "Log: $log"
echo 'To stop, press Ctrl+C and wait for the shell prompt.'
# Preserve even a successful image left behind before inspection/publication.
if [[ -s "$image" ]]; then
 python3 "$root/scripts/archive-image.py" --variant "$variant" --image "$image" --preserve-only
fi
if $clean; then
 [[ $(realpath -m "$build_out") == "$build_out" && ! -L "$build_out" ]] || {
  echo 'Refusing cleanup: build path points outside the expected directory.' >&2; exit 1;
 }
 echo "Clean build: removing $build_out" | tee -a "$log"
 rm -rf -- "$build_out"
fi
interrupted=false
trap 'interrupted=true' INT

set +e
LAPIS_GAPPS="$gapps" BUILD_JOBS="$jobs" bash "$root/scripts/build-baseline.sh" 2>&1 | tee "$log"
results=("${PIPESTATUS[@]}")
set -e
if $interrupted || [[ ${results[0]} == 130 || ${results[0]} == 143 ]]; then
 echo "Build stopped. Outputs preserved; run again to resume. Log: $log"
 exit 130
fi
if [[ ${results[0]} != 0 ]]; then
 echo "Build failed (exit code ${results[0]}). Log: $log" >&2
 echo 'Fix the cause and rerun. Cleaning out is not needed to resume.' >&2
 exit "${results[0]}"
fi
if [[ ${results[1]} != 0 ]]; then
 echo "Could not finish writing the log: $log" >&2
 exit 1
fi

[[ -s "$image" ]] || { echo "Build returned success but image is missing: $image" >&2; exit 1; }
set +e
python3 "$root/scripts/inspect-image.py" "$image" --output "$root/artifacts/$variant-system.img.inspection.json" 2>&1 | tee -a "$log"
inspection_status=$?
set -e
if [[ $inspection_status != 0 ]]; then
 echo "Image created, but recording inspection evidence failed. Log: $log" >&2
 exit "$inspection_status"
fi
python3 "$root/scripts/archive-image.py" --variant "$variant" --image "$image" \
 --inspection "$root/artifacts/$variant-system.img.inspection.json" --log "$log"
echo "Image built: $root/out/$variant/latest/system.img"
echo "SHA256 and metadata are stored beside the image."
echo 'Experimental build: this new image has not yet been tested on a phone.'
