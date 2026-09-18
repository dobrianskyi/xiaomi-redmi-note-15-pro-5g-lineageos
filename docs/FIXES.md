# Fix locations

| Change | Source |
|---|---|
| Brightness / display wake | `patches/frameworks_native`, `patches/device_phh_treble`, `local/device/local/gsi/ueventd` |
| Fingerprint lifecycle / geometry | `patches/frameworks_base/0002-*`, `local/device/local/gsi/overlays/LapisUdfpsGeometry` |
| Call / VoIP speaker gain | `patches/device_phh_treble/0003-*`, `0005-*` |
| Media volume slider / theme | `patches/frameworks_base/0001-*`, `0003-*` |
| Top-edge lockscreen shade | `patches/frameworks_base/0004-*`, `overlays/LapisShadeGestures` |
| Launcher swipe option | `patches/packages_apps_Launcher3` |
| Stock screen geometry / left clock | `overlays/LapisDisplayGeometry`, `overlays/LapisStatusBarGeometry` |
| Dolby / power schedule | `local/device/local/gsi/apps/DolbyControl`, `apps/PowerSchedule` |
| MediaTek IMS / carrier MNC parsing | `apps/MediatekIms`, `overlays/LapisIms*`, `scripts/prepare-ims.py` |
| TrebleApp without QTI handlers | `patches/treble_app`, `scripts/prepare-trebleapp.py`, `apps/TrebleApp` |
| SELinux / VINTF / permissions | `local/device/local/gsi/sepolicy`, `compatibility_matrix.xml`, `lapis-base.mk` |

Paths beginning `overlays/` or `apps/` are relative to `local/device/local/gsi/`.
Android patch order and pinned bases are recorded in `patches/series.json`.
TrebleApp's patch is applied separately by its source-build helper.
A Magisk compile-compatibility patch exists for an upstream dependency, but the
lapis product excludes Magisk from its installed package set.

Display geometry was taken from the matching stock device overlays, not guessed
by changing resolution: radius 156px, portrait bar height 152px, content inset
84px, top padding 38px, centered camera cutout 66px wide. Runtime resource and
physical visibility checks passed. The recipe does not include stock overlay
APKs, device captures, personal configuration or passwords.
