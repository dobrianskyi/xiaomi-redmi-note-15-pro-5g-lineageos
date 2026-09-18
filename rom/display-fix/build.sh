#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
clang --target=aarch64-linux-android -fuse-ld=lld -nostdlib -static -fno-stack-protector -fno-builtin -O2 -Wl,-e,_start -Wl,--build-id=none bridge.c -o module/lapis-backlight
python3 test_bridge.py
