#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SDK="${ANDROID_SDK_ROOT:-$HOME/Android/Sdk}"
mkdir -p build/dex
javac -classpath "$SDK/platforms/android-35/android.jar" -d build CallVolumeBridge.java
"$SDK/build-tools/35.0.0/d8" --lib "$SDK/platforms/android-35/android.jar" --output build/dex build/CallVolumeBridge.class
cp build/dex/classes.dex module/bridge.dex
