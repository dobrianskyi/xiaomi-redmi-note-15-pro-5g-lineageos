# Bluetooth profile hotfix — 2026-10-20

For Xiaomi Redmi Note 15 Pro 5G (`lapis`), the tested LineageOS build
`23.2-20260918-UNOFFICIAL-gsi_lapis` and stock Xiaomi vendor
`OS3.0.307.0.WPPMIXM`.

## Installer update — 2026-11-06

Version 0.2 removes the exact September 18 date restriction. Other LineageOS 23.2
`gsi_lapis` dates are accepted on lapis with Android 16 / SDK 36 and the same stock
vendor. Both installer and boot script enforce this environment. Existing profile
values remain untouched, including in later builds with integrated defaults.
Only the original September payload has been tested on hardware; other dates
remain experimental. Android 17 is outside this module's supported environment.
[Download the updated ZIP](https://github.com/dobrianskyi/xiaomi-redmi-note-15-pro-5g-lineageos/releases/tag/module-installers-20261106).

## Problem and fix

The lapis product does not inherit PHH's generic `base.mk`/`system.prop`.
Its ordinary Bluetooth profile defaults were therefore missing. Android's
A2DP, HFP and AVRCP services treat an absent enable property as false.
The adapter could report ON while music/headset and other ordinary profile
services were disabled. The initial runtime dump listed only GATT,
HEARING_AID and VAPS_SERVER.

The fix restores the missing profile defaults from the matching stock firmware
and the smartphone Class of Device from the PHH base. It preserves explicitly
configured values, including the vendor's disabled LE Audio and SAP roles.
It does not force unsupported profiles on.

- **Future source builds:** `local/device/local/gsi/bluetooth-defaults.mk` is
  inherited by `lapis-base.mk`; no Magisk is required for that build change.
- **Existing September image:** the separate `lapis_bluetooth_profiles-0.1.zip`
  asset requires an already working Magisk installation. Its boot script adds
  only absent properties. There is no daemon or polling loop, and no Bluetooth
  database, pairing, Wi-Fi, SELinux or firmware-partition edit.

This hotfix is compatible with the documented September build. The older
brightness/fingerprint/audio modules elsewhere in `rom/` remain excluded from
this image because their fixes are already integrated.

## Install on the existing build

1. Check lapis, LineageOS 23.2 `gsi_lapis`, SDK 36 and the vendor above. The
   build date can differ; compatibility with that exact build remains unverified.
2. Verify the ZIP against the release's `SHA256SUMS`.
3. With Magisk already installed, open **Magisk → Modules → Install from storage**
   and select the Bluetooth ZIP, then reboot normally.
4. Check discovery and pair a headset or other peripheral in pairing mode.
   Recheck media, calls, reconnect and battery behavior on your own hardware.

Disable/remove this module in Magisk and reboot to return to the firmware's
original property defaults. Existing pairings are not deleted. Once a later
ROM includes these properties itself, the script leaves those values alone.

## Verified on 2026-10-20

On one lapis phone with the build/vendor above:

- Applied the same boot payload at runtime and restarted only Bluetooth.
- A2DP, AVRCP, HEADSET, BATTERY, HID_DEVICE, HID_HOST, MAP, OPP, PAN and PBAP
  started alongside the previously available profiles: 13 profile services total.
- A controlled Classic inquiry found the computer made temporarily discoverable.
- A separate controlled BLE test found the computer's named test advertisement;
  BLE scan error code was 0.
- Adapter stayed ON, with zero Bluetooth crashes during the checks.
- During a 30.81-second idle interval, the Bluetooth process used 0.04 seconds
  of CPU (about 0.13% of one core); the vendor HAL used no additional CPU time.
  Stack/native wake locks were released. Ordinary Google Fast Pair background
  scans may still exist while Bluetooth is enabled.

**Limits:** real headset pairing, sustained audio/call connections, disconnect
reproduction and long battery tests have not been completed. The idle sample
does not measure radio energy or prove that a battery-drain complaint is fixed.
The boot payload is installed on the test phone, but a full reboot with it and
installation through this new distribution ZIP have not yet been tested.
No rebuilt system image is included in the October hotfix release; the September
image download has not been replaced.

## Reproduce host checks

```sh
python3 -m unittest discover -s tests -p 'test_bluetooth_fix.py' -v
bash -n rom/bluetooth-fix/module/post-fs-data.sh
bash -n rom/bluetooth-fix/module/customize.sh
python3 rom/package-modules.py
```

The property-script tests use isolated mock property commands, never a phone.
The ZIP adds a Magisk installer guard and permission setup to the tested runtime
payload. Private device captures, addresses, app data and signing keys are not
included in the public source or assets.
