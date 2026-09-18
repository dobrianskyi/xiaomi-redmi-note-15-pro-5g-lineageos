# Build variants and preserved images

Run the same launcher from any directory:

```bash
./build.sh --gapps none
./build.sh --gapps minimal
./build.sh --gapps full
```

`none` is the default. All variants use the same pinned LineageOS23.2/Android16
sources and lapis fixes. All remain experimental until tested on the phone.

| Option | Contents | Build cache | Published images |
|---|---|---|---|
| none | Vanilla, no Google packages | source/out | out/vanilla |
| minimal | Play Store, Play services, Services Framework, Google account setup, contacts/calendar sync and required configuration | source/out-gapps-minimal | out/gapps-minimal |
| full | MindTheGapps ARM64 set (legacy Exchange excluded), including Search, speech services, TalkBack, Digital Wellbeing, restore, Markup, parental controls and Android Auto stub | source/out-gapps-full | out/gapps-full |

Full means the standard MindTheGapps application set, not every Google application.
The pinned PrebuiltExchange3Google APK fails signature verification (missing v2
signature declared by its v1 signer). It and its advertised Exchange feature are
excluded from our full profile; no APK is re-signed and no signature check is bypassed.
Chrome, Gmail, Maps, Photos and YouTube are not preinstalled by this provider;
they can be installed through Play Store. Minimal omits optional-app defaults
and does not advertise contextual search, Exchange or Assistant availability.
Its framework overlay is derived from the pinned MindTheGapps overlay, with
those optional settings removed (GPLv2; license retained alongside the source).

GApps source: https://github.com/MindTheGapps/vendor_gapps/tree/baklava
The exact revision is recorded in research/gapps-source.json. The launcher
fetches it automatically when a Google variant is selected. Existing modified
or differently pinned checkouts are rejected, not overwritten. Proprietary
APKs remain in the ignored source checkout and retain upstream signatures.
This optional packaging is separate from vanilla upstream contribution work.

## Resume and clean

Repeat the same `--gapps` option to resume that variant. `--jobs 8` controls jobs.
The first build of each Google variant starts with a separate cache; it does
not reuse the existing vanilla objects. Budget extra time and disk space.
Downloaded source trees and GApps inputs are shared, not fetched per variant.

`./build.sh --gapps minimal --clean` removes only source/out-gapps-minimal.
It preserves existing images first and never deletes out/ archives or other
variant caches. One exclusive lock covers all variants, source preparation,
compilation, cleanup and image publication. The generated product selector is
written under that lock. Changed local device files receive fresh timestamps
when copied, so each variant invalidates stale build rules. Do not run the
internal backend directly.

`--check` checks prerequisites and the pinned GApps checkout without downloads,
image copying, cleanup or compilation. If GApps are missing, normal build fetches
them. `--check` is not a complete Soong build or a phone compatibility test.

## Output layout

Each successfully published image has its own directory:

```
out/vanilla/<UTC-date>-<SHA256-prefix>/system.img
out/gapps-minimal/<UTC-date>-<SHA256-prefix>/system.img
out/gapps-full/<UTC-date>-<SHA256-prefix>/system.img
```

Each variant has a `latest` symlink to its latest successfully published image.
Pre-build rescue copies do not change that pointer. Beside the image
are SHA256SUMS and manifest.json, plus inspection/build log when published after
successful compilation. An existing image preserved before a build may have only
its checksum and archive manifest; preservation does not establish build success.
Identical image bytes reuse their existing archive. Failed builds never publish
a new successful result. Archives use independent copies (reflinks where supported),
not hardlinks to mutable build outputs. Copies are hashed before publication.

Before flashing a Google variant, check final image size against the phone's
partition layout and validate account setup, Play Store and IMS. Host checks do
not establish phone behavior or Play certification.

## Validation

The minimal variant has completed full compilation and a preceding image passed
clean setup on the test phone. Both Google profiles previously passed Soong/Kati
product-graph checks; this does not claim that the full profile has been flashed.
The latest release's exact hash and validation scope are in release-metadata.json.
See [device status](DEVICE_STATUS.md) for hardware checks and remaining work.
Seven recipe regression tests cover patch replay, pinned fetching, variant
isolation, archive preservation, resume/error handling and selected cleanup.
