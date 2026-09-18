# Provenance and licenses

This repository is a build recipe and patch collection, not a replacement license
for Android, LineageOS, TrebleDroid, proprietary firmware or Google applications.
Original copyright and license notices in source files and patch context remain
applicable. Derived changes to upstream files follow their respective upstream
licenses. No blanket claim of ownership over third-party code is made here.

- Android / AOSP: https://source.android.com/
- LineageOS: https://github.com/LineageOS
- TrebleDroid: https://github.com/TrebleDroid
- PHH / Treble experiments: https://github.com/phhusson/treble_experimentations
- AndyCGYan GSI sources: https://github.com/AndyCGYan
- MindTheGapps: https://github.com/MindTheGapps/vendor_gapps

Pinned revisions, download URLs and SHA256 values are included with the recipe.
The minimal Google configuration overlay is derived from MindTheGapps; its GPLv2
license is retained alongside that source. Upstream patch authors and notices
are retained. The stock vendor/kernel are used on the device but not distributed
by this repository.

The MediaTek IMS APK is a proprietary input fetched from PHH's public endpoint;
its provenance and hash are recorded in `research/mediatek-ims.json`. No APK is
committed to Git. Optional Google packages retain their upstream signatures and
remain governed by their own terms. Recipe source availability does not relicense
these binary components. Published GApps-minimal images contain the documented
Google/IMS components; vanilla builds omit Google applications.

Firmware-integrated Dolby controls and RTC power scheduling source are part of
this ROM's fixes. Unrelated desktop/mobile applications, user databases, personal
signing material and separately patched video applications are not part of this
repository or its releases.
