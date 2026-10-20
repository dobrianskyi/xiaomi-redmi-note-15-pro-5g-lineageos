# Updates

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
