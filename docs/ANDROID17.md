# Android 17 release — refreshed 2026-11-07

Release: [LineageOS 24.0 for lapis](https://github.com/dobrianskyi/xiaomi-redmi-note-15-pro-5g-lineageos/releases/tag/24.0-lapis-20261106).

- ARM64 A/B raw EXT4 system image, user/test-keys, GApps minimal.
- Android 17 / SDK 37; security patch level 2026-11-01.
- LineageOS 24.0 pinned source lock, release configuration `cp2a`.
- Stock Xiaomi kernel/vendor/firmware baseline: OS3.0.307.0.WPPMIXM.
- MindTheGapps Android 17 `cinnamonbun`, pinned in `research/gapps-source.json`.
- The exact downloadable raw image has SHA256
  `d89f019ca10b90277afa41b93f249f86a4911fb17c3e0b24a66fb2ea67944d92`
  and size **2495303680 bytes**. The release supplies `.img.xz` and checksums.

The existing release has been updated in place: its previous image asset was
replaced with the November 7 build. The release contains one current image.

## Vibration and persistent mute

Stock lapis exposes `android.hardware.vibrator.IVibrator/vibratorfeature` rather
than `/default`. The 27-patch recipe handles discovery and reconnects in Java,
JNI and native clients, while keeping a declared default instance preferred.
The framework now exposes vibrator ID0; a 1500ms one-shot completed and the user
confirmed the Ring vibration preview. This restores access to the existing motor;
its strength continues to follow vendor hardware and system intensity settings.

Explicit media mute survives a real reboot and is restored before the shade is
opened. Unmute restored the exact prior level (4/15 on the tested route). Temporary
DND/internal muting is kept separate; accessibility and TTS remained unmuted.

## Retained controls

**Auto-confirm unlock:** open screen-lock settings, turn on the option, and enter
your current PIN in the phone's confirmation screen. PINs of at least four digits
are eligible; changing the PIN is unnecessary. Enabling the option remains an
explicit choice. Credential verification and failed-attempt lockout are unchanged.
The six-digit recommendation/default selection for newly chosen PINs is retained.

**Media mute:** the speaker button at the trailing end of the Quick Settings media
slider toggles Android's media-stream mute state. It retains AudioService's volume
index rather than setting it to zero or caching a value inside the view. The next
tap restores the retained level. Icons and accessibility descriptions follow the
state; fixed-volume output and user restrictions disable adjustment.

## Validation and limits

The exact release bytes booted on the maintainer's lapis and an update preserved
existing apps/data. Encrypted-user unlock, existing package identities and data
directories, Google services/Play Store identities and SELinux Enforcing were
checked. The earlier PIN and media-button controls are retained. The user physically
confirmed vibration in the updated image, and a real media-mute reboot test passed. Offline checks passed for
EXT4, permissions, IMS carrier strings, merged SELinux, property/service contexts
and VINTF using matching vendor/odm metadata and all image/vendor APEX modules.

These are build and smoke-test results, not certification of every hardware path.
A fresh clean installation of these exact bytes and another clean-host rebuild
have not been repeated. [Device status](DEVICE_STATUS.md) retains earlier hardware
observations and open tests. Android 16 Treble helper revisions are retained where
upstream has no Android 17 branch; their compatibility was checked for this image.

## Updating

Read [installation instructions](INSTALL.md). The tested Android 17-to-17 update
wrote only the active logical system partition and kept userdata, metadata,
boot/vendor and the current verification setup. Existing installation prerequisites
still apply. A successful update on one phone is not a universal data-retention
guarantee; keep an external backup. The image is not an OTA or a complete firmware
package. Legacy Magisk display/audio/Bluetooth payloads are not needed for its
integrated fixes.

The release is built from sources and contains no phone userdata, personal apps,
account databases, PIN records, host ADB authorization keys or private signing keys.
The source checkout and checksums identify the published image. Private device
captures and backup files are not release assets.
