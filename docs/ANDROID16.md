# Android 16 refresh — 2026-11-07

[Current Android16 image](https://github.com/dobrianskyi/xiaomi-redmi-note-15-pro-5g-lineageos/releases/tag/23.2-lapis-20260918)
replaces the previous file in the existing release. Source branch:
[lineage-23.2](https://github.com/dobrianskyi/xiaomi-redmi-note-15-pro-5g-lineageos/tree/lineage-23.2).

LineageOS23.2 / Android16 (SDK36), GApps minimal, ARM64 A/B EXT4, for Xiaomi lapis
with stock vendor OS3.0.307.0.WPPMIXM. Security patch level: 2026-09-01.

The 24-patch build includes native/JNI/Java vibrator discovery and reconnects,
opt-in four-digit PIN confirmation, the media mute button and explicit mute
restoration into stream/group state after boot. Existing device fixes and
Bluetooth defaults remain integrated. Full compilation and offline filesystem,
permissions, SELinux/context, VINTF/APEX and privacy checks passed. Sixteen
source-recipe host tests and ten native/Java discovery-policy tests passed.
Phone boot/hardware/update verification of these exact Android16 bytes is pending;
related implementation testing was performed on Android17.

Raw size: 2494214144 bytes. SHA256:
`1e0016993e61975b2ba80dd5a30c903e5178d9d338d9666e4294678dfe8a7d40`.
The compressed archive was fully decompressed and its SHA256 verified. No phone
userdata, personal apps, private keys, test app or root payload is included.

Download the current image, release-metadata.json and SHA256SUMS. Verify downloaded
files with `sha256sum --ignore-missing -c SHA256SUMS`, decompress the .xz and follow
the installation guide. The legacy Magisk ZIPs retained in that release are
separate reference-GSI workarounds; this image already integrates its fixes.
