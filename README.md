# Xiaomi Redmi Note 15 Pro 5G — LineageOS 23.2 / Android 16 (lapis)

Unofficial **Android 16 / LineageOS 23.2** build recipe and device fixes for the
**Xiaomi Redmi Note 15 Pro 5G (codename `lapis`) with an unlocked bootloader**. Check the codename, not just the retail
name: this is not a Redmi Note 5 Pro or a generic installer for other models.

This is an **ARM64 A/B EXT4 GSI** using the phone's stock Xiaomi kernel, vendor and
firmware. It is not an official LineageOS device port, an OTA package, or a
source-built Xiaomi kernel/vendor distribution. The tested firmware baseline is
**HyperOS OS3.0.307.0.WPPMIXM**. SELinux is Enforcing. Magisk/root is not included.
The initial release uses public Android test signing keys, not private production
release keys. Bootloader locking and official OTA updates are not supported.

## Build LineageOS for Xiaomi Redmi Note 15 Pro 5G

Use Linux x86_64, Python 3.12+ (or 3.11 with tarfile extraction-filter support),
JDK 17, and Android build dependencies. See [host setup](docs/BUILD.md).
The tested host has about 60 GiB RAM; reserve several hundred GiB for sources,
build intermediates and archived images. A second full clean-host build has not
been completed; the scripts and patch replay have automated checks.

```sh
git clone https://github.com/dobrianskyi/xiaomi-redmi-note-15-pro-5g-lineageos.git
cd xiaomi-redmi-note-15-pro-5g-lineageos
export JAVA_HOME=/path/to/your/jdk-17  # omit if javac already selects JDK 17
./prepare.sh
./build.sh --gapps minimal --jobs 12
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
- Media-only volume slider in Quick Settings, including its SystemUI theme fix.
- Power schedule under Settings → Battery, gated by RTC capability.
- MediaTek IMS compatibility and carrier config matching for Kyivstar/lifecell.
- TrebleApp built from pinned sources with Qualcomm handlers/dependencies removed.
- Optional home-screen swipe-down notifications (off by default); lockscreen
  shade gestures restricted to the top edge on lapis.
- Stock lapis cutout, rounded-corner and status-bar dimensions, fixing left-clock
  digits disappearing under the physical screen corner.
- Strict privileged permissions, service labels and stock-vendor SELinux/VINTF
  compatibility fixes discovered during bring-up.

All are part of the recipe and apply during future builds and clean installations;
no post-install root modules are required. Details and remaining tests:
[device status](docs/DEVICE_STATUS.md), [fix map](docs/FIXES.md),
[power schedule](docs/POWER_SCHEDULE.md).

## Two ways to try the fixes

1. **Complete ROM, no root required:** build this recipe or download the system
   image from Releases, then follow [installation prerequisites](docs/INSTALL.md).
2. **Selected Magisk workarounds on the older reference GSI:** use the scripts,
   source and module payloads in [`rom/`](rom/README.md), or its release ZIPs.
   Magisk must already be installed. These are individual fixes, not the whole
   ROM; do not stack them on the released image, which already integrates them.

## Downloads and installation

Download the experimental image and checksums from [Releases](https://github.com/dobrianskyi/xiaomi-redmi-note-15-pro-5g-lineageos/releases).
The initial release is **GApps minimal**. Verify checksums before decompression
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
