# Updates

## 2026-11-07 — Android16 image refreshed

Replaced the old image in the existing Android16 release with the new 24-patch
build. It includes the vibration-discovery backport, four-digit PIN opt-in and
media mute/reboot persistence, retaining earlier device fixes. Full compilation
and offline compatibility/privacy checks passed; exact-image phone validation is
pending. Android16 source is on lineage-23.2; main remains Android17.
[Download and details](docs/ANDROID16.md).

## 2026-11-07 — Vibration restored; media mute retained after reboot

Updated the existing Android 17 release in place with the tested November 7 image.
The old image asset is replaced, keeping one current image in that release.
Java and native vibrator clients now find the declared lapis stock instance and
retain it on reconnect. A framework one-shot completed; the user physically confirmed the Ring preview. Explicit media mute is restored into both stream and volume-group
state at startup; a real reboot retained mute, and unmute restored the prior
volume without muting accessibility/TTS. The full 27-patch image passed offline
checks, boot/unlock, enforcing SELinux and retention checks for 35 user apps.
[Download and details](docs/ANDROID17.md).

## 2026-11-06 — Module installer compatibility

Removed exact build-date gates from the five optional Magisk modules. Eligibility
now checks lapis, LineageOS 23.2 / SDK 36 and the documented Xiaomi vendor. The
four legacy display/FOD/audio modules reject integrated lapis ROMs; Bluetooth
defaults target 23.2 `gsi_lapis` and preserve explicit values. Corresponding boot
guards are aligned with installer eligibility. New module versions and separate
ZIPs leave the original release assets intact. Host compatibility tests pass;
installation on additional GSI builds has not been tested on hardware. This
update contains no system image and no vibration fix. See [module instructions](rom/README.md).

## 2026-11-06 — LineageOS 24.0 / Android 17

[New system image, GApps minimal](https://github.com/dobrianskyi/xiaomi-redmi-note-15-pro-5g-lineageos/releases/tag/24.0-lapis-20261106). The prior lapis display,
fingerprint, audio/IMS, geometry, gestures, Dolby, power-schedule and Bluetooth
recipe fixes are ported to Android 17.

New: opt-in auto-confirm for PINs of four or more digits, and a dedicated media
mute/unmute button beside the Quick Settings slider. Mute retains the native
volume level for restoration. Existing credential checks and lockout handling
remain in place.

The exact release image was flashed without wiping the maintainer's existing
Android 17 data. Boot, encrypted-user unlock, app retention, enforcing SELinux and
the two new controls passed. Filesystem, permissions, service/property contexts,
SELinux merge and VINTF checks passed with matching vendor/APEX metadata. Other
hardware paths have not all been retested; see [device status](docs/DEVICE_STATUS.md).

Builds now use bounded systemd scopes and Go memory controls. Four parallel jobs
completed the tested incremental build; eight caused sustained memory reclaim.
The source lock contains 1246 projects and the ordered recipe has 22 patches.

## 2026-10-20 — Bluetooth profile hotfix

Fixed missing Bluetooth profile defaults in the lapis build recipe. Affected
builds could turn Bluetooth on while ordinary music/headset services stayed
disabled. Future builds now include the profile properties without root.

For the existing September 18 image, an experimental, separately installable
Magisk ZIP restores only missing defaults while preserving explicit vendor
settings. This Bluetooth hotfix has its own compatibility guard; it is distinct
from the older reference-GSI display/audio modules.

Controlled Classic discovery and BLE advertisement reception passed on the
tested lapis. Profile startup was verified and no Bluetooth crashes occurred.
Real-device connection stability, long-term battery use and a full reboot with
the new module remain unverified. This update does not certify those issues fixed.

**No new system image:** the September image and its checksums are unchanged.
See the [hotfix details and installation](rom/bluetooth-fix/README.md) and the
[October hotfix release](https://github.com/dobrianskyi/xiaomi-redmi-note-15-pro-5g-lineageos/releases/tag/bluetooth-fix-20261020).
