#!/usr/bin/env bash
# Source this file; never changes the caller's HOME or system configuration.
BRINGUP_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
export BRINGUP_ROOT
export REPO_CONFIG_DIR="$BRINGUP_ROOT/cache/repo"
export XDG_CACHE_HOME="$BRINGUP_ROOT/cache/xdg"
export XDG_CONFIG_HOME="$BRINGUP_ROOT/cache/config"
export GIT_CONFIG_GLOBAL="$BRINGUP_ROOT/cache/config/git/config"
export TMPDIR="$BRINGUP_ROOT/tmp"
export GRADLE_USER_HOME="$BRINGUP_ROOT/cache/gradle"
export ANDROID_USER_HOME="$BRINGUP_ROOT/cache/android"
export CCACHE_DIR="$BRINGUP_ROOT/cache/ccache"
export PYTHONDONTWRITEBYTECODE=1
export GIT_TERMINAL_PROMPT=0
export PATH="$BRINGUP_ROOT/tools/host/usr/bin:$BRINGUP_ROOT/tools/git-repo:$BRINGUP_ROOT/tools/git-lfs/git-lfs-3.8.0:$PATH"
if [[ -z ${JAVA_HOME:-} ]]; then
 if command -v javac >/dev/null; then
  JAVA_HOME=$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")")
 else
  echo 'JDK 17 is required; install it and set JAVA_HOME.' >&2
  return 1
 fi
fi
export JAVA_HOME
export PATH="$JAVA_HOME/bin:$PATH"
mkdir -p "$REPO_CONFIG_DIR" "$XDG_CACHE_HOME" "$XDG_CONFIG_HOME" "$TMPDIR" "$GRADLE_USER_HOME" "$ANDROID_USER_HOME"
