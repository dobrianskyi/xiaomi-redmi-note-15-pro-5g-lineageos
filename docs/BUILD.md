# Build environment and reproducibility

The tested host is Arch Linux x86_64 with JDK 17, Python 3.13, around 60 GiB RAM,
and 12 parallel compilation jobs. Use a case-sensitive Linux filesystem and
budget several hundred GiB of disk space. The exact requirement depends on the
number of variants and retained archives. Other Linux distributions have not
received a complete clean-host build test for this recipe.

Provide these tools before running `prepare.sh`: bash, git, curl, Python 3.12+
(or updated Python 3.11 supporting `tarfile.extractall(filter=...)`), tar,
sha256sum, flock, make, gcc/g++, bison, flex, zip/unzip, rsync, gperf, bc, JDK 17,
and the standard Android host development libraries. The Android platform uses
its pinned prebuilt toolchain; JDK 17 is also used for TrebleApp Gradle tooling.
Set `JAVA_HOME` to a JDK 17 installation if `javac` selects another version.

`prepare.sh` supplies project-local repo and Git LFS. On Arch only, the optional
host-tools helper can download gperf/bc using the installed pacman repository
index. It never installs system packages. On other distributions, install the
required equivalents yourself before preparing the source tree.

The exact Android projects are in `research/resolved-manifest.xml`. The recipe
uses a local committed copy of this manifest with `repo init`, so commit reviewed
manifest edits before initializing another source tree. Repo sync and source
patching have completion markers; a later run will not overwrite patched trees.

Additional inputs:

- `research/gapps-source.json`: pinned MindTheGapps revision, used only for Google variants.
- `research/mediatek-ims.json`: pinned upstream IMS APK URL and SHA256. Binary is
  downloaded during preparation/build, excluded from Git, and signed by the ROM.
- `scripts/prepare-trebleapp.py`: pinned upstream TrebleApp commit, local patch,
  disposable build tree, SDK bootstrap and no-Qualcomm DEX checks.
- `research/git-lfs-release.json`: pinned Git LFS download and SHA256.

The SDK bootstrap may invoke `sdkmanager --licenses`; review the SDK terms before
using the toolchain. Existing SDK paths are reused when supported. No Google or
MediaTek APKs are committed to this source repository.

Build output is incremental and variant-specific. A fresh build is not promised
to be byte-identical to a published release: timestamps, host paths, tool versions
and generated signing metadata can change hashes. Sources and patches are pinned.
A patch-tree mismatch or dirty upstream project stops the build; do not bypass it.

## Checks

```sh
python3 -m unittest discover -s tests -v
./build.sh --gapps minimal --check
```

`--check` is a preflight, not a full source build or hardware test. The tests use
small fixtures and do not download or compile Android.

`inspect-image.py` records size and SHA256, but metadata inspection alone is not
release validation. `validate-baseline.py` additionally checks filesystem,
privileged permissions, TrebleApp QTI exclusion, carrier MNC strings, merged
SELinux policy/context labels and VINTF. Full validation requires your own stock
vendor/odm capture and the matching extracted APEX tree; private device captures
are deliberately not published here. Use `--stock-dir` and `--apex-dir`.
The published release metadata reports the checks actually performed by the builder.
