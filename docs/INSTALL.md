# Experimental GSI installation

This release contains **only system.img**, compressed with xz. It is not a recovery
ZIP, factory firmware package or OTA. It is intended for experienced users of an
already unlocked, correctly prepared Xiaomi `lapis` with compatible stock
OS3.0.307.0.WPPMIXM vendor/kernel/firmware and working fastbootd.

Back up data outside the phone. A clean installation erases all phone user data.
Do not use these files on a similarly named phone with a different codename.
Do not lock the bootloader with this unofficial/test-key image installed.

## Verify

Download the `.img.xz`, `SHA256SUMS` and `release-metadata.json` from the same release.

```sh
sha256sum -c SHA256SUMS --ignore-missing
xz -t lineage-23.2-20260918-UNOFFICIAL-lapis-gapps-minimal-system.img.xz
xz -dk lineage-23.2-20260918-UNOFFICIAL-lapis-gapps-minimal-system.img.xz
sha256sum lineage-23.2-20260918-UNOFFICIAL-lapis-gapps-minimal-system.img
```

The raw image hash must match `raw_image_sha256` in the release metadata.

## Existing compatible GSI installation

Before writing anything, confirm `lapis`, the active slot, unlocked bootloader,
fastbootd (userspace fastboot), the logical system partition and available space.
Use up-to-date Android platform tools. These commands are examples for a single
connected device, **active slot a only**; stop if any check differs:

```sh
adb reboot fastboot
fastboot getvar product             # lapis
fastboot getvar current-slot        # a
fastboot getvar is-userspace        # yes
fastboot getvar is-logical:system_a  # yes
fastboot getvar partition-size:system_a
```

The partition must accommodate the expanded size in release metadata. Do not
copy partition sizes from a different device or delete unrelated logical partitions.
The tested phone already had its GSI/AVB layout prepared and an unmodified stock
init_boot; this repository does not distribute a universal vbmeta image or a
bootloader unlock/initial stock-to-GSI migration tool. If your AVB state, firmware
or dynamic-partition layout is not prepared, resolve that first for the exact
firmware; flashing system alone is not guaranteed to boot.

After all prerequisites match:

```sh
fastboot flash system_a lineage-23.2-20260918-UNOFFICIAL-lapis-gapps-minimal-system.img
# OPTIONAL and DESTRUCTIVE: only for an explicitly intended clean installation:
fastboot -w
fastboot reboot
```

Stop on any write or format error; do not continue to reboot after a failed wipe.
For an incremental update with compatible keys/data, omit `fastboot -w`.
Migrating from another ROM/signing setup should be planned as a clean installation.
No kernel, vendor, modem, boot or init_boot is supplied or flashed by this recipe.
An existing Magisk-patched init_boot is not removed by writing system.img.

After boot, complete setup and verify calls, screen wake, fingerprints, audio and
other hardware. See [status](DEVICE_STATUS.md) and [RTC test](POWER_SCHEDULE.md).
The release does not auto-authorize ADB; enable USB debugging and approve your
own computer in the usual way when needed.
