#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
git lfs install --skip-repo
mkdir -p "$BRINGUP_ROOT/source"
if [[ -f "$BRINGUP_ROOT/source/.repo/manifest.xml" ]]; then
 echo 'Source checkout already initialized. Use sync-source.sh only before applying patches.'
 exit 0
fi
# The committed full manifest pins every upstream revision. Its GitHub remote
# is absolute, so cloning this recipe from a local path preserves upstream URLs.
git -C "$BRINGUP_ROOT" diff --quiet HEAD -- research/resolved-manifest.xml || {
 echo 'Commit the reviewed source lock before initializing a reproducible checkout.' >&2
 exit 1
}
recipe_commit=$(git -C "$BRINGUP_ROOT" rev-parse HEAD)
cd "$BRINGUP_ROOT/source"
repo init -u "$BRINGUP_ROOT" -b "$recipe_commit" -m research/resolved-manifest.xml \
 --git-lfs --no-clone-bundle --depth=1 \
 --repo-url=https://gerrit.googlesource.com/git-repo --repo-rev=v2.67
