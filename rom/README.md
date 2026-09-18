# Optional Magisk workarounds for Xiaomi lapis

These are the earlier, separately tested root-module implementations of selected
fixes. They let an experienced user try individual fixes **without replacing the
whole system image**, on the documented compatible reference GSI.
They do not turn stock HyperOS into LineageOS and are not an alternate installer
for the complete ROM.

**Requirements:** Xiaomi Redmi Note 15 Pro 5G (`lapis`), unlocked bootloader,
working Magisk already installed, stock vendor OS3.0.307.0.WPPMIXM, and the tested
reference GSI reporting `ro.lineage.version=23.2-20260524-GAPPS-EXT4-GSI`.
The new installer guard rejects other builds. These ZIP wrappers have been
checked on the host; the underlying module payloads were tested during bring-up.
They have not been installed again on the current root-free phone.

**Do not install these modules on this repository's released ROM:** its equivalent
fixes are already integrated without root, and duplicate handlers can conflict.
No Magisk boot/init_boot image or personal signing key is distributed here.

| Directory | Module | Effect |
|---|---|---|
| `display-fix` | `lapis_backlight_bridge` v0.1 | Mirrors MediaTek brightness to Xiaomi panel backlight; Power wake workaround |
| `fingerprint-fix` | `lapis_fod_bridge` v0.3 | Xiaomi display-device path, FOD state notifications and resource-only sensor geometry overlay |
| `call-audio-fix` | `lapis_call_volume` v0.2 | Bounded speaker gain for SIM and VoIP communication calls, maximum vendor index 11 |
| `dolby-fix` | `lapis_dolby_control` v0.3 | Existing native Dolby effect daemon; no separate controller application included |

The module directories contain boot scripts and their small runtime payloads.
C/Java and overlay resource sources are included. The fingerprint APK is strictly
a resource overlay with no executable DEX; it is not an unrelated user app.
No password-manager application/database or patched video application is included.

## Package and install

```sh
python3 rom/package-modules.py
```

The ZIPs and checksums appear in `rom/modules-out/`. Ready-made ZIPs are also
attached to the experimental GitHub release. Copy the desired ZIP to the phone,
open **Magisk → Modules → Install from storage**, select it, and reboot.
Install only the required modules, one at a time, and verify the affected feature.
These are Magisk-app ZIPs, not recovery-flashable installers; their format follows
[Magisk's module guide](https://topjohnwu.github.io/Magisk/guides.html#magisk-module-installer).

Remove modules through Magisk and reboot to roll back. For the call module,
uninstall restores the default state of `org.lineageos.mediatek.incallservice`.
If merely disabling it, restore that helper's default state separately using root
before rebooting. Do not disable MediaTek IMS: it is a different component.

The Dolby daemon reads `/data/adb/lapis_dolby/config`; the existing payload defaults
to `1 20 9 0` (enabled, gain, profile selection, device selection). Review
`daemon/DolbyDaemon.java` before changing values. Its original Android controller
APK is intentionally not included. The ROM's English Dolby controls are built
separately from `local/device/local/gsi/apps/DolbyControl`.

IMS/VoLTE/VoWi-Fi were handled by firmware components and settings, not a separate
Magisk module. The source-built ROM adds its own carrier/IMS compatibility fixes;
no made-up IMS module is supplied. Power scheduling, Quick Settings media volume,
shade gesture preferences and the latest status-bar geometry are provided by the
ROM build, not all by these older modules.

## Rebuild payloads

- Brightness: `bash rom/display-fix/build.sh` (clang/lld, Python, qemu-aarch64).
- Call gain: `bash rom/call-audio-fix/build.sh` (JDK 17, Android SDK 35 and build-tools 35.0.0).
- Dolby: `bash rom/dolby-fix/build.sh` (same Android SDK/JDK requirements).
- Fingerprint resource overlay: `bash rom/fingerprint-fix/build-overlay.sh`.
  This generates a new local development signing key in an ignored build folder;
  no original private key is published. A newly signed overlay is for a fresh
  module installation, not an in-place APK update with a different certificate.
