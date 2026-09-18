#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SDK="${ANDROID_SDK_ROOT:-${ANDROID_HOME:-$HOME/Android/Sdk}}"
BT="$SDK/build-tools/35.0.0"
mkdir -p geometry/build
"$BT/aapt2" compile --dir geometry/res -o geometry/build/resources.zip
"$BT/aapt2" link -o geometry/build/unsigned.apk --manifest geometry/AndroidManifest.xml \
 -I "$SDK/platforms/android-35/android.jar" geometry/build/resources.zip
"$BT/zipalign" -f 4 geometry/build/unsigned.apk geometry/build/aligned.apk
# Disposable local development key; never commit it or share it with users.
if [[ ! -f geometry/build/development.jks ]]; then
 keytool -genkeypair -keystore geometry/build/development.jks -storepass android \
  -keypass android -alias overlay -keyalg RSA -keysize 2048 -validity 3650 \
  -dname 'CN=Lapis overlay development'
fi
"$BT/apksigner" sign --ks geometry/build/development.jks --ks-key-alias overlay \
 --ks-pass pass:android --key-pass pass:android \
 --out module/system/system_ext/overlay/lapis-udfps-geometry.apk geometry/build/aligned.apk
