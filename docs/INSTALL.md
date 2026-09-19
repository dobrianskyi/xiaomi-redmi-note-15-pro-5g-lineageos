# Flashing LineageOS on Xiaomi Redmi Note 15 Pro 5G (lapis)

This guide covers a clean installation from the matching stock HyperOS baseline,
reinstallation over a compatible GSI, first boot, and rollback. **An already
unlocked bootloader is required. A clean installation deletes all phone user data.**

The release is an unofficial **LineageOS 23.2 / Android 16 ARM64 A/B EXT4 GSI**.
It contains a compressed `system.img`, not a recovery ZIP, OTA or complete Xiaomi
firmware. The initial release includes minimal Google apps. Root is not required.

## Scope and tested baseline

- Device codename: **lapis**, Xiaomi Redmi Note 15 Pro 5G Global.
- Stock kernel/vendor/firmware: **OS3.0.307.0.WPPMIXM**, Android 16.
- Active slot: **a**. Commands below intentionally name this slot explicitly.
- Stock `boot`, `vendor_boot`, `dtbo` and vendor partitions are retained.
- A working Xiaomi recovery with **fastbootd** is required.

These steps do not cover arbitrary firmware versions, other regional variants,
modified partition layouts or slot b. If a check differs, stop and investigate;
do not switch slots just to match this guide. The inactive slot is **not** a
verified recovery system: its logical partitions may be empty.

The preceding build passed clean setup on the test phone. The final clock overlays
were subsequently tested on it; the exact downloadable final image has not received
another clean-flash test. See [device status and remaining tests](DEVICE_STATUS.md).
This guide documents the known installation sequence, not a guarantee for every phone.

## 1. Prepare your computer, backups and recovery files

1. Back up photos, files, passwords and account recovery codes **outside the phone**.
2. Charge the phone, use a reliable USB data cable, and connect only the target phone.
3. Install current [Google Android Platform-Tools](https://developer.android.com/tools/releases/platform-tools).
   Ensure `adb` and `fastboot` are on PATH. Linux may need USB/udev permissions;
   Windows needs the appropriate USB driver in both bootloader and fastbootd modes.
4. Commands below use **Linux Bash**, Python 3, `xz`, `sha256sum` and `stat`.
   They are not a PowerShell script. Do not paste the whole guide as one script;
   check the output after each stage and stop on any error.
5. Download the image, `SHA256SUMS` and `release-metadata.json` from the
   [same release](https://github.com/dobrianskyi/xiaomi-redmi-note-15-pro-5g-lineageos/releases/tag/23.2-lapis-20260918).
6. Obtain and unpack the matching **Xiaomi Global fastboot firmware**, not a
   recovery ZIP. The baseline archive used here is
   `lapis_global_images_OS3.0.307.0.WPPMIXM_20260624.0000.00_16.0_global_03d72813f0.tgz`.
   Retain the complete package for recovery. This repository does not redistribute it.

Create a working directory containing the release files and a `stock/` directory.
Copy the firmware package's **original** `images/vbmeta.img`, `images/init_boot.img`
and `images/super.img` into `stock/`. Keep those originals unmodified.
`super.img` is large; unpack it before flashing so rollback files are ready.
Do not use a random empty vbmeta or an image from another phone/firmware.

If the phone does not already have this matching stock baseline, this is not a
firmware upgrade/downgrade procedure. Establish the correct baseline using the
appropriate Xiaomi procedure first; do not mix its boot images with another vendor.
Never choose `flash_all_lock`, `clean all and lock`, or issue a bootloader-lock command.

## 2. Verify and decompress the release

Run in the working directory:

```bash
sha256sum -c SHA256SUMS --ignore-missing
xz -t lineage-23.2-20260918-UNOFFICIAL-lapis-gapps-minimal-system.img.xz
xz -dk lineage-23.2-20260918-UNOFFICIAL-lapis-gapps-minimal-system.img.xz
export IMAGE="$PWD/lineage-23.2-20260918-UNOFFICIAL-lapis-gapps-minimal-system.img"
python3 - <<'PY'
import hashlib, json, os
from pathlib import Path
p = Path(os.environ['IMAGE'])
m = json.loads(Path('release-metadata.json').read_text())
with p.open('rb') as f:
    digest = hashlib.file_digest(f, 'sha256').hexdigest()
assert digest == m['raw_image_sha256'], 'Image checksum mismatch'
assert p.stat().st_size == m['raw_image_bytes'], 'Image size mismatch'
print('Verified raw image:', digest, p.stat().st_size, 'bytes')
PY
```

The initial release expands to **2,494,197,760 bytes** with SHA256
`1e187c136d693cb96a71bc5e0f3f07e6f3bb01a6686d4e88ffb4dd8a844c6a7c`.
Flash the decompressed `.img`, never the `.xz` file. For a later release or your
own build, use its actual filename, metadata and expanded size instead.
The Python snippet above requires Python 3.11+.

## 3. Check the phone and enter bootloader Fastboot

In Android, enable Developer options and USB debugging, connect the cable and
approve your own computer's debugging request. Then:

```bash
adb devices -l
adb shell getprop ro.product.vendor.device
adb shell getprop ro.vendor.build.fingerprint
adb shell getprop ro.boot.slot_suffix
adb reboot bootloader
```

Expected: `lapis`, a vendor fingerprint containing `OS3.0.307.0.WPPMIXM`, and `_a`.
If Android is unbootable, hold **Power + Volume Down** to enter bootloader Fastboot;
you still need a reliable record of the installed firmware baseline.

```bash
fastboot devices
fastboot getvar product
fastboot getvar current-slot
fastboot getvar unlocked
fastboot getvar is-userspace
```

Expected: one device, `lapis`, `a`, `yes`, and `no`, respectively. Bootloader
Fastboot and recovery's fastbootd are different modes. A Xiaomi FASTBOOT screen
alone does not mean logical partitions can be flashed. Some GSI Android properties
can be spoofed; use the bootloader's unlocked check rather than a status app.

## 4. Prepare AVB metadata for the unofficial image

The stock AVB configuration must allow this unsigned-by-Xiaomi system image.
Our tested procedure changes only the verification flags in a **copy** of the
matching stock `vbmeta.img`. The bootloader must remain unlocked.

Prepare that copy locally; this does not write to the phone:

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib
src = Path('stock/vbmeta.img').read_bytes()
expected = '5b71568c087408344864e0a5ebd2dba6b6e674f45db09c9d8b811ff1297d4350'
assert hashlib.sha256(src).hexdigest() == expected, 'Wrong stock vbmeta'
assert src[:4] == b'AVB0' and len(src) == 12288, 'Unexpected AVB header'
patched = bytearray(src)
patched[120:124] = (3).to_bytes(4, 'big')
expected_patched = 'c1be4c7ebec047ec70809c5246f1ce8a5d7293f54d175d263cc7b8b7bd2f63d6'
assert hashlib.sha256(patched).hexdigest() == expected_patched
Path('vbmeta-disable-verification.img').write_bytes(patched)
print('Prepared verified vbmeta copy; stock original retained')
PY
```

These hashes identify our recorded baseline files, not an independent signature
verification of a firmware download. Source the firmware from a trusted Xiaomi
firmware distribution and retain its provenance.

We previously encountered `Failed to find AVB_MAGIC at offset: 0` with the
Platform-Tools 37.0.0 `--disable-verity --disable-verification` path. Preparing the
checked copy above avoids relying on that host-side transformation. Do not ignore
an AVB error or replace unrelated vbmeta partitions. The original signature no
longer validates the changed header; the unlocked bootloader permits this setup.

## 5. Ensure stock init_boot for a root-free installation

Writing `system.img` does not remove an existing Magisk patch. For this root-free
baseline, verify and flash the matching original `init_boot` while in bootloader
Fastboot. This is also safe when that exact stock image is already installed.

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib
p = Path('stock/init_boot.img')
assert p.stat().st_size == 8388608
assert hashlib.sha256(p.read_bytes()).hexdigest() == \
    '249b596b9fdc792365474af9d4011316e541647ec14f25d1192331d47793e3db'
print('Verified stock init_boot')
PY
fastboot flash init_boot_a stock/init_boot.img
```

Continue only after a successful write. This does not install a different kernel.
Do not replace `boot`, `vendor_boot`, `dtbo` or modem partitions with GSI files.

## 6. Enter fastbootd and check logical system

```bash
fastboot reboot fastboot
fastboot getvar product
fastboot getvar current-slot
fastboot getvar is-userspace
fastboot getvar is-logical:system_a
fastboot getvar partition-size:system_a
```

Expected: `lapis`, `a`, **`yes`**, **`yes`**, and a valid partition size (often hex).
Wait for the device to reconnect before issuing the checks. If fastbootd cannot
start or does not expose logical `system_a`, stop; bootloader Fastboot is not a
substitute. With Android still working, `adb reboot fastboot` also enters fastbootd.

On the recorded stock layout, `system_a` was 880,087,040 bytes and needed growth.
The stock dynamic-partition group had room for the image without deleting other
partitions. Other layouts must be assessed separately. Do not delete `product`,
`system_ext`, `vendor`, `*_dlkm` or inactive-slot partitions to force a fit.

## 7. Flash the image and perform the clean reset

**The reset below permanently removes phone apps, accounts and internal files.**
At this point backups and the recovery package must already be on the computer.

In fastbootd, after all preceding checks pass:

```bash
fastboot flash vbmeta_a vbmeta-disable-verification.img
fastboot resize-logical-partition system_a "$(stat -c %s "$IMAGE")"
fastboot flash system_a "$IMAGE"
fastboot -w
fastboot reboot
```

Execute each line separately. Continue only after success. If resize reports
insufficient space, stop; do not improvise partition deletions. If flashing or
formatting fails, do not reboot into a partially installed system. Preserve the
error output and resolve it, or use the rollback below. `fastboot -w` must finish
successfully, including the data/metadata formatting reported by the tool.

The stock product/system_ext files are retained on disk; this GSI's mount
configuration uses its integrated system content. No additional GApps ZIP or
Magisk fix modules are required for the published minimal-GApps image.

## 8. First boot and checks

First boot can take several minutes. A persistent boot animation is different
from repeatedly returning to the Mi logo. If it makes no progress after roughly
10–15 minutes, investigate rather than repeatedly wiping or reflashing blindly.

Complete the setup wizard, then check:

- Brightness adjustment, screen timeout and Power-button sleep/wake.
- PIN and newly enrolled fingerprint unlocking.
- Wi-Fi, mobile data, actual calls, microphone and speakerphone.
- Dolby audio and the Quick Settings media-volume slider.
- Left/right clock visibility and notification-shade gestures.
- [Power schedule](POWER_SCHEDULE.md), if you want to test RTC wake-up.

VoLTE registration is not proof that calls work, and VoWi-Fi still has documented
carrier-dependent issues. See [device status](DEVICE_STATUS.md). Enable debugging
and authorize your computer again if logs are needed: this public image does not
include the maintainer's ADB key or diagnostic startup override.

Do not install the older `rom/` fix modules on top: these fixes are integrated.
Optional Magisk installation is separate from flashing this GSI; follow the
[official Magisk instructions](https://topjohnwu.github.io/Magisk/install.html)
and patch your matching `init_boot` on your own phone. Complete any requested app
environment setup and reboot. Never use another person's patched boot image.

## Updating an existing installation

For an already prepared installation using the same compatible firmware, keys
and data layout, verify the new image, enter fastbootd, repeat the identity/logical
partition checks, then resize/flash `system_a` as above. Existing compatible AVB
metadata need not be changed. Do not reflash stock init_boot if intentionally
retaining your separately installed compatible Magisk setup.

Omit `fastboot -w` **only** when deliberately attempting a compatible update and
after backing up data. Dirty upgrades are not guaranteed. Switching from HyperOS,
another ROM/signing setup, or changing GApps variants should be treated as a clean
installation. A clean reinstall follows all the steps above, including the wipe.

## Rollback to the matching HyperOS baseline

This rollback covers the changes in this guide, provided the original matching
kernel/vendor firmware is otherwise intact and slot a is still active. It is not
a repair recipe for changes to arbitrary physical partitions or firmware versions.
It **wipes user data again** and does not recover previously erased files.

Enter bootloader Fastboot with Power + Volume Down. If currently in fastbootd:

```bash
fastboot reboot bootloader
fastboot getvar product
fastboot getvar current-slot
fastboot getvar unlocked
fastboot getvar is-userspace
```

Require `lapis`, `a`, `yes`, `no`. Use the untouched stock files saved in step 1:

```bash
fastboot flash super stock/super.img
fastboot flash init_boot_a stock/init_boot.img
fastboot flash vbmeta_a stock/vbmeta.img
fastboot -w
fastboot reboot
```

`super.img` restores the original logical partitions and their layout. Wait for
all sparse-image chunks to finish; stop on any write error. The guide's rollback
also removes the Magisk boot patch by restoring stock init_boot. It intentionally
leaves the bootloader unlocked. If other firmware partitions were changed, use a
separately verified complete Xiaomi recovery procedure for your exact variant;
this limited rollback is not sufficient.

## Troubleshooting and reports

| Symptom | Next check |
| --- | --- |
| `adb` unauthorized | Unlock Android and approve your computer's RSA prompt |
| Fastboot waiting for device | Cable, USB permissions/driver and current mode |
| Logical partition not found | Confirm fastbootd and active slot; do not create a guessed partition |
| Resize lacks space | Inspect actual dynamic layout; do not delete unrelated partitions |
| Repeated Mi-logo reboot | Firmware/AVB compatibility, successful writes and clean reset |
| Persistent Lineage animation | Collect logs if ADB is authorized; re-check build and data compatibility |
| Magisk environment incomplete | Complete setup inside the official app and reboot |

When Android and authorized ADB are available, capture `adb logcat -b all -d`
to a local file. Logs may contain identifiers and account information; redact
before posting. Include the image hash, stock firmware version, active slot and
exact failed command. Do not share passwords, complete phone backups or private keys.
