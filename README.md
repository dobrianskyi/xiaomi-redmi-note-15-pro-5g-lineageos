# Xiaomi Redmi Note 15 Pro 5G — LineageOS 24.0 / Android 17 (lapis)

Unofficial **Android 17 / LineageOS 24.0** build recipe and device fixes for the
**Xiaomi Redmi Note 15 Pro 5G (codename `lapis`) with an unlocked bootloader**. Check the codename, not just the retail
name: this is not a Redmi Note 5 Pro or a generic installer for other models.

This is an **ARM64 A/B EXT4 GSI** using the phone's stock Xiaomi kernel, vendor and
firmware. It is not an official LineageOS device port, an OTA package, or a
source-built Xiaomi kernel/vendor distribution. The tested firmware baseline is
**HyperOS OS3.0.307.0.WPPMIXM**. SELinux is Enforcing. Magisk/root is not included.
Images use public Android test signing keys, not private production
release keys. Bootloader locking and official OTA updates are not supported.

## Update — 2026-11-06: Android 17

**[Download LineageOS 24.0 / Android 17 — GApps minimal](https://github.com/dobrianskyi/xiaomi-redmi-note-15-pro-5g-lineageos/releases/tag/24.0-lapis-20261106)**

The new system image includes the existing lapis fixes and Bluetooth profile
defaults, plus:

- **Four-digit PIN auto-confirm:** enable **Auto-confirm unlock** in the screen-lock
  settings, then confirm your existing PIN on the phone. Entering the correct
  fourth digit unlocks without pressing Enter. The option is off until enabled.
- **One-tap media mute:** a separate speaker button beside the Quick Settings
  media-volume slider mutes playback and restores the previous level on the next
  tap. Android retains the volume; closing the shade does not lose it.
- Android 17-compatible SystemUI resources, restored HIDL interface declarations
  required by the Treble helpers, and memory-bounded compilation.

The exact downloadable image booted on the maintainer's lapis. An update preserving
existing apps/data passed, SELinux remains Enforcing, and both new controls were
user-confirmed. This is an **experimental GSI**, not official LineageOS support or
full hardware certification. See [release details](docs/ANDROID17.md).

**Module installation update (2026-11-06):** exact build-date restrictions have
been removed from the optional Android 16 Magisk ZIPs. Device/vendor and duplicate-fix
checks remain. [Downloads and compatibility](rom/README.md). These modules are not
needed on the integrated ROM and do not contain the pending vibration fix.

## Build LineageOS for Xiaomi Redmi Note 15 Pro 5G

Use Linux x86_64, Python 3.12+ (or 3.11 with tarfile extraction-filter support),
JDK 17 for TrebleApp tooling, systemd user scopes, and Android build dependencies.
Android uses its pinned platform toolchain. See [host setup](docs/BUILD.md).
The tested host has about 60 GiB RAM; start with four parallel jobs. Compilation
runs in its own scope (44 GiB high / 48 GiB hard limit). Reserve several hundred GiB for sources,
build intermediates and archived images. A second full clean-host build has not
been completed; the scripts and patch replay have automated checks.

```sh
git clone https://github.com/dobrianskyi/xiaomi-redmi-note-15-pro-5g-lineageos.git
cd xiaomi-redmi-note-15-pro-5g-lineageos
export JAVA_HOME=/path/to/your/jdk-17  # omit if javac already selects JDK 17
./prepare.sh
./build.sh --gapps minimal --jobs 4
```

`prepare.sh` downloads pinned source revisions and tools. Re-run it after an
interrupted download. It does not install host packages with sudo or flash a phone.
`build.sh` resumes incremental compilation and fetches missing IMS/TrebleApp/GApps
inputs. The initial source sync must be completed with `prepare.sh` first.

```sh
./build.sh --gapps none             # vanilla (default)
./build.sh --gapps minimal          # Play services/store and required setup/sync
./build.sh --gapps full             # pinned MindTheGapps selection
./build.sh --gapps minimal --clean  # discard this variant's build cache, then build
./build.sh --gapps minimal --check  # preflight only
```

Ctrl+C stops a build; wait for it to exit, then repeat the same command to resume.
`--clean` preserves sources, downloads and archived images. Never manually sync
upstream over patched checkouts; prepare a fresh checkout for upstream changes.

Images are archived under `out/vanilla`, `out/gapps-minimal`, or `out/gapps-full`,
with a timestamp and SHA256 in each directory name. `latest/system.img` points to
the newest archive for that variant. See [build variants](docs/BUILD_VARIANTS.md).

## Included fixes

- MediaTek screen brightness and Power-button display wake-up.
- Xiaomi fingerprint lifecycle and sensor geometry.
- Native speaker gain handling for calls and communication apps.
- English Dolby audio controls and launcher icon using the stock vendor effect.
- Media-only volume slider in Quick Settings, including its SystemUI theme fix
  and a mute/unmute button that retains the previous level.
- Optional PIN auto-confirm for four or more digits; enable it in screen-lock settings.
- Power schedule under Settings → Battery, gated by RTC capability.
- MediaTek IMS compatibility and carrier config matching for Kyivstar/lifecell.
- TrebleApp built from pinned sources with Qualcomm handlers/dependencies removed.
- Optional home-screen swipe-down notifications (off by default); lockscreen
  shade gestures restricted to the top edge on lapis.
- Stock lapis cutout, rounded-corner and status-bar dimensions, fixing left-clock
  digits disappearing under the physical screen corner.
- Strict privileged permissions, service labels and stock-vendor SELinux/VINTF
  compatibility fixes discovered during bring-up.
- Bluetooth profile defaults integrated into the image (October 20 fix).

All are part of the recipe and apply during future builds and clean installations;
no post-install root modules are required for the integrated fixes. Details and remaining tests:
[device status](docs/DEVICE_STATUS.md), [fix map](docs/FIXES.md),
[power schedule](docs/POWER_SCHEDULE.md).

## Two ways to try the fixes

1. **Complete ROM, no root required:** build this recipe or download the system
   image from Releases, then follow [installation prerequisites](docs/INSTALL.md).
2. **Selected Magisk workarounds on the older reference GSI:** use the scripts,
   source and module payloads in [`rom/`](rom/README.md), or its release ZIPs.
   Magisk must already be installed. These are individual fixes, not the whole
   ROM; do not stack them on the released image, which already integrates them.

The October [Bluetooth hotfix](rom/bluetooth-fix/README.md) targets only the old
September Android 16 image. Android 17 already includes its profile defaults;
do not install the legacy module on this release.

## Downloads and installation

**[Full flashing guide for an unlocked Xiaomi Redmi Note 15 Pro 5G](docs/INSTALL.md)** —
stock firmware prerequisites, image verification, Fastboot/fastbootd, AVB setup,
clean installation, updates, first boot and rollback to HyperOS.

Download the experimental image and checksums from [Releases](https://github.com/dobrianskyi/xiaomi-redmi-note-15-pro-5g-lineageos/releases).
The current release is **Android 17, GApps minimal**. Verify checksums before decompression
and flashing. Read [installation prerequisites](docs/INSTALL.md); there is no
universal one-click flashing script. Source builds do not flash the phone.

The release is built from an empty system image, not a backup of a used phone.
It contains no user accounts, password databases, personal apps, patched video
apps, host ADB authorization key, or diagnostic ADB startup override.

## Contributing

Source revisions are pinned in `research/resolved-manifest.xml`; patch order and
base commits are in `patches/series.json`. Product definitions and local components
are under `local/device/local/gsi`. Please include the device codename, firmware
baseline, release hash and reproduction steps in bug reports. Remove identifiers,
phone numbers, credentials and account data from logs before sharing them.

This project is a bring-up base for eventual upstream contributions, not a claim
of official LineageOS support. Thanks to LineageOS, AOSP, TrebleDroid/PHH,
AndyCGYan, MindTheGapps, and MisterZtr for public sources and reference build work.
See [provenance and licensing](NOTICE.md).
