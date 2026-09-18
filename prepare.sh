#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
destination=
tools_only=false
while (($#)); do
 case "$1" in
  --directory)
   [[ $# -ge 2 && -n $2 ]] || { echo 'Specify an empty directory after --directory.' >&2; exit 2; }
   destination=$2; shift 2 ;;
  --tools-only) tools_only=true; shift ;;
  --help|-h)
   echo 'prepare.sh [--directory DIR] [--tools-only]'
   echo 'Download LineageOS 23.2 tools and sources without compiling.'
   echo '--directory: create a separate recipe checkout in an empty directory.'
   echo '--tools-only: prepare tools only, without Android repo sync.'
   exit 0 ;;
  *) echo "Unknown argument: $1" >&2; exit 2 ;;
 esac
done

if [[ -n $destination ]]; then
 destination=$(realpath -m -- "$destination")
 [[ $destination != "$root" ]] || { echo 'For the current directory, omit --directory.' >&2; exit 2; }
 if [[ -e $destination/.git ]]; then
  [[ $(git -C "$destination" remote get-url origin) == "$root" && -f $destination/prepare.sh ]] || {
   echo 'This directory already contains another repository.' >&2; exit 1;
  }
 else
  git clone --no-hardlinks -- "$root" "$destination"
 fi
 args=()
 if $tools_only; then args+=(--tools-only); fi
 exec bash "$destination/prepare.sh" "${args[@]}"
fi

cd "$root"
[[ $(uname -s) == Linux && $(uname -m) == x86_64 ]] || {
 echo 'This recipe requires Linux x86_64.' >&2; exit 1;
}
for tool in git curl python3 tar sha256sum flock tee; do
 command -v "$tool" >/dev/null || { echo "Required host tool: $tool" >&2; exit 1; }
done
python3 -c 'import sys; sys.exit("Python 3.11 or newer is required") if sys.version_info < (3, 11) else None'
source "$root/scripts/env.sh"
mkdir -p tools logs cache/config/git
exec 9>"$root/cache/build.lock"
flock -n 9 || { echo 'Another preparation or build is running.' >&2; exit 1; }
log=$(mktemp "$root/logs/prepare-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX.log")
echo "Preparation log: $log"

prepare() {
 repo_revision=c638b54e19f4765904613f729b2c9059fc4799d2
 repo_url=https://gerrit.googlesource.com/git-repo
 if [[ ! -d tools/git-repo/.git ]]; then
  git init tools/git-repo
  git -C tools/git-repo remote add origin "$repo_url"
 fi
 [[ $(git -C tools/git-repo remote get-url origin) == "$repo_url" ]] || {
  echo 'Unexpected tools/git-repo remote; existing checkout unchanged.' >&2; return 1;
 }
 if [[ $(git -C tools/git-repo rev-parse HEAD 2>/dev/null || true) != "$repo_revision" ]]; then
  [[ -z $(git -C tools/git-repo status --porcelain) ]] || {
   echo 'tools/git-repo has local changes; automatic replacement refused.' >&2; return 1;
  }
  git -C tools/git-repo fetch --depth=1 origin "$repo_revision"
  git -C tools/git-repo checkout --detach "$repo_revision"
 fi

 readarray -t lfs < <(python3 -c 'import json; d=json.load(open("research/git-lfs-release.json")); print(d["url"]); print(d["sha256"])')
 archive=tools/git-lfs-linux-amd64-v3.8.0.tar.gz
 if ! printf '%s  %s\n' "${lfs[1]}" "$archive" | sha256sum -c - >/dev/null 2>&1; then
  curl -fL --retry 3 -o "$archive.part" "${lfs[0]}"
  printf '%s  %s\n' "${lfs[1]}" "$archive.part" | sha256sum -c -
  mv "$archive.part" "$archive"
 fi
 mkdir -p tools/git-lfs
 tar -xzf "$archive" -C tools/git-lfs
 git lfs install --skip-repo
 git config --global user.name >/dev/null || git config --global user.name "${BUILD_GIT_NAME:-Local LineageOS Builder}"
 git config --global user.email >/dev/null || git config --global user.email "${BUILD_GIT_EMAIL:-builder@localhost}"

 if ! command -v gperf >/dev/null || ! command -v bc >/dev/null; then
  if [[ -f /var/lib/pacman/sync/extra.db ]] && command -v pacman >/dev/null; then
   python3 scripts/bootstrap-host-tools.py
  else
   echo 'Host gperf and bc are required. See docs/BUILD.md.' >&2; return 1;
  fi
 fi
 for tool in make gcc g++ bison flex zip unzip rsync gperf bc; do
  command -v "$tool" >/dev/null || { echo "Missing host tool: $tool (see docs/BUILD.md)" >&2; return 1; }
 done
 if $tools_only; then
  echo 'Tools ready. Android sources were not downloaded; compilation was not started.'
  return
 fi

 bash scripts/init-source.sh
 if [[ -e cache/build-patches-applied || -e cache/source-sync-complete ]]; then
  echo 'Existing sources preserved; no repeated repo sync needed.'
 else
  bash scripts/sync-source.sh
 fi
 python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
missing = [p.get('path', p.get('name')) for p in ET.parse('research/resolved-manifest.xml').getroot().findall('project')
           if not (Path('source') / p.get('path', p.get('name')) / '.git').exists()]
if missing:
    raise SystemExit('Checkout is missing projects: ' + ', '.join(missing) +
                     '. Use --directory with a fresh folder to preserve existing patches.')
PY
 for arch in arm arm64 x86 x86_64; do
  project="source/external/chromium-webview/prebuilt/$arch"
  if ! python3 -c 'import sys,zipfile; sys.exit(not zipfile.is_zipfile(sys.argv[1]))' "$project/webview.apk"; then
   git -C "$project" lfs pull github
  fi
 done
 python3 scripts/prepare-ims.py
 # build.sh takes the same lock; release it only after all source mutations.
 flock -u 9
 bash build.sh --check
 echo "Preparation complete. Build with: $root/build.sh"
}
prepare 2>&1 | tee "$log"
