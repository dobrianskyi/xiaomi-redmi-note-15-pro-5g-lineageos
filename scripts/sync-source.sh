#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
if [[ -e "$BRINGUP_ROOT/cache/build-patches-applied" ]]; then
 echo 'Local build patches are applied. Preserve them; update/rebase in a fresh checkout.' >&2
 exit 1
fi
cd "$BRINGUP_ROOT/source"
log="$BRINGUP_ROOT/logs/repo-sync-$(date -u +%Y%m%dT%H%M%SZ).log"
repo sync -c --optimized-fetch --no-tags --no-clone-bundle --fail-fast -j4 2>&1 | tee "$log"
repo manifest -r -o "$BRINGUP_ROOT/research/synced-manifest.xml"
touch "$BRINGUP_ROOT/cache/source-sync-complete"
