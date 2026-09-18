#!/usr/bin/env python3
"""Read-only filesystem, VINTF and SELinux checks against a saved stock capture."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("image", type=Path)
parser.add_argument("--stock-dir", type=Path, default=root / "artifacts/stock/lapis-OS3.0.307.0.WPPMIXM")
parser.add_argument("--apex-dir", type=Path, help="Extracted APEX tree with apex-info-list.xml from this image and stock vendor")
args = parser.parse_args()
image = args.image.resolve(strict=True)
stock = args.stock_dir.resolve(strict=True)
if not (stock / "vendor/etc/selinux/vendor_service_contexts").is_file():
    parser.error("Incomplete lapis stock capture: vendor_service_contexts is required")
apex = args.apex_dir.resolve(strict=True) if args.apex_dir else None
if apex and not (apex / "apex-info-list.xml").is_file():
    parser.error("--apex-dir must contain apex-info-list.xml")
if not image.is_relative_to(root):
    parser.error("The image must be inside the bring-up directory")
tools = root / "source/out/host/linux-x86/bin"
for name in ("debugfs", "e2fsck", "checkvintf", "secilc", "sepolicy-analyze", "property_info_checker"):
    if not (tools / name).is_file():
        parser.error(f"Missing host tool: {name}")
with image.open("rb") as stream:
    stream.seek(0x438)
    if stream.read(2) != b"\x53\xef":
        parser.error("This validator currently supports raw EXT4 images only")
    stream.seek(0)
    digest = hashlib.file_digest(stream, "sha256").hexdigest()
work = Path(tempfile.mkdtemp(prefix=f"validation-{digest[:12]}-", dir=root / "artifacts"))
report = {"image": str(image.relative_to(root)), "sha256": digest,
          "bytes": image.stat().st_size, "evidence": str(work.relative_to(root)),
          "stock_capture": str(stock), "hardware": "NOT TESTED", "checks": {}}


def run(name, command):
    result = subprocess.run([str(x) for x in command], capture_output=True, text=True)
    (work / (name + ".log")).write_text(result.stdout + result.stderr)
    report["checks"][name] = {"returncode": result.returncode,
                              "command": [str(x) for x in command]}
    return result


run("filesystem", [tools / "e2fsck", "-fn", image])
# TrebleApp is installed by hardware_overlay, independently of PHH base.mk.
# Its missing allowlist aborts system_server on this strict user build.
treble_permissions = work / "privapp-permissions-me.phh.treble.app.xml"
run("extract-treble-permissions", [tools / "debugfs", "-R",
    f"dump /system/etc/permissions/{treble_permissions.name} {treble_permissions}", image])
required_permissions = {"android.permission.INSTALL_PACKAGES",
                        "android.permission.INTERACT_ACROSS_USERS"}
try:
    entries = ET.parse(treble_permissions).findall(
        "./privapp-permissions[@package='me.phh.treble.app']/permission")
    allowed_permissions = {entry.get("name") for entry in entries}
    missing_permissions = sorted(required_permissions - allowed_permissions)
    permission_error = None
except (OSError, ET.ParseError) as error:
    missing_permissions = sorted(required_permissions)
    permission_error = str(error)
report["checks"]["treble-privapp-permissions"] = {
    "returncode": int(bool(missing_permissions)),
    "missing": missing_permissions, "error": permission_error,
}
treble_apk = work / "LapisTrebleApp.apk"
run("extract-lapis-treble", [tools / "debugfs", "-R",
    f"dump /system/priv-app/LapisTrebleApp/LapisTrebleApp.apk {treble_apk}", image])
try:
    with zipfile.ZipFile(treble_apk) as package:
        dex = b"".join(package.read(n) for n in package.namelist() if n.endswith(".dex"))
    qti_present = any(value in dex for value in
                      (b"Lvendor/qti/", b"Lme/phh/treble/app/QtiAudio;", b"Starting Qualcomm service"))
    report["checks"]["treble-lapis-no-qti"] = {"returncode": int(not dex or qti_present)}
except (OSError, zipfile.BadZipFile) as error:
    report["checks"]["treble-lapis-no-qti"] = {"returncode": 1, "error": str(error)}
# AAPT normally coerces MNC="03" to 3, which never matches the SIM string.
carrier_apk = work / "LapisImsCarriers.apk"
run("extract-carrier-overlay", [tools / "debugfs", "-R",
    f"dump /system/system_ext/overlay/LapisImsCarriers.apk {carrier_apk}", image])
carrier_xml = run("ims-carrier-mnc", [tools / "aapt2", "dump", "xmltree",
    "--file", "res/xml/vendor.xml", carrier_apk])
if carrier_xml.returncode == 0:
    missing_mnc = [mnc for mnc in ("03", "06")
                   if f'mnc={int(mnc)} (Raw: "{mnc}")' not in carrier_xml.stdout]
    report["checks"]["ims-carrier-mnc"].update(
        returncode=int(bool(missing_mnc)), missing_raw_mnc=missing_mnc)
for partition, path in (("system", "/system"), ("system_ext", "/system/system_ext"), ("product", "/system/product")):
    destination = work / partition
    (destination / "etc").mkdir(parents=True)
    for directory in ("selinux", "vintf"):
        run(f"extract-{partition}-{directory}", [tools / "debugfs", "-R",
            f"rdump {path}/etc/{directory} {destination / 'etc'}", image])
    run(f"extract-{partition}-properties", [tools / "debugfs", "-R",
        f"dump {path}/build.prop {destination / 'build.prop'}", image])

platform = work / "system/etc/selinux"
if not (platform / "plat_sepolicy.cil").is_file() or not (work / "system/build.prop").is_file():
    raise SystemExit("Required image metadata was not extracted; inspect debugfs logs")
version = (stock / "vendor/etc/selinux/plat_sepolicy_vers.txt").read_text().strip()
inputs = [platform / "plat_sepolicy.cil", platform / "mapping" / (version + ".cil")]
optional = [platform / "mapping" / (version + ".compat.cil")]
for partition in ("system_ext", "product"):
    directory = work / partition / "etc/selinux"
    optional += [directory / (partition + "_sepolicy.cil"), directory / "mapping" / (version + ".cil")]
    if partition == "system_ext":
        optional.append(directory / "mapping" / (version + ".compat.cil"))
inputs += [path for path in optional if path.is_file()]
inputs += [stock / "vendor/etc/selinux/plat_pub_versioned.cil", stock / "vendor/etc/selinux/vendor_sepolicy.cil"]
odm = stock / "odm/etc/selinux/odm_sepolicy.cil"
if odm.is_file():
    inputs.append(odm)
genfs_version = stock / "vendor/etc/selinux/genfs_labels_version.txt"
genfs = genfs_version.read_text().strip() if genfs_version.is_file() else "202404"
genfs_cil = platform / f"plat_sepolicy_genfs_{genfs}.cil"
if genfs_cil.is_file():
    inputs.append(genfs_cil)
report["policy_input_sha256"] = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
# Match init's runtime merge. This is NOT a neverallow acceptance check.
merged = run("selinux-runtime-merge", [tools / "secilc", "-m", "-M", "true", "-G", "-N", "-c", "30",
    *inputs, "-o", work / "sepolicy", "-f", work / "file_contexts"])
if merged.returncode == 0:
    permissive = run("selinux-permissive", [tools / "sepolicy-analyze", work / "sepolicy", "permissive"])
    report["permissive_domains"] = permissive.stdout.splitlines() if permissive.returncode == 0 else None

# Init serializes all partitions' property contexts into one trie. A duplicate
# prefix is fatal even when SELinux policy compilation and VINTF both pass.
property_contexts = []
for partition, prefix in (("system", "plat"), ("system_ext", "system_ext"),
                          ("vendor", "vendor"), ("product", "product"), ("odm", "odm")):
    directory = stock if partition in ("vendor", "odm") else work
    path = directory / partition / "etc/selinux" / (prefix + "_property_contexts")
    if path.is_file():
        property_contexts.append(path)
run("property-contexts", [tools / "property_info_checker", work / "sepolicy", *property_contexts])

# Check the same combined tables loaded by service managers. Policy compilation
# alone does not notice conflicting service names in different partitions.
for suffix in ("service_contexts", "hwservice_contexts"):
    context_files = []
    for partition, prefix in (("system", "plat"), ("system_ext", "system_ext"),
                              ("product", "product"), ("vendor", "vendor"), ("odm", "odm")):
        directory = stock if partition in ("vendor", "odm") else work
        path = directory / partition / "etc/selinux" / (prefix + "_" + suffix)
        if path.is_file():
            context_files.append(path)
    combined = work / ("merged_" + suffix)
    combined.write_text("\n".join(path.read_text() for path in context_files))
    run(suffix, [sys.executable, root / "scripts/check-service-contexts.py", combined])
    report["checks"][suffix]["inputs"] = {
        str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in context_files}
    if suffix == "service_contexts":
        ims_labels = {"mwis": [], "mtkIms": []}
        for line in combined.read_text().splitlines():
            fields = line.split("#", 1)[0].split()
            if len(fields) == 2 and fields[0] in ims_labels:
                ims_labels[fields[0]].append(fields[1])
        report["checks"]["ims-service-labels"] = {
            "returncode": int(any(set(labels) != {"u:object_r:radio_service:s0"}
                                  for labels in ims_labels.values())),
            "labels": ims_labels,
        }

command = [tools / "checkvintf", "--check-compat"]
for partition in ("system", "system_ext", "product", "vendor", "odm"):
    directory = stock / partition if partition in ("vendor", "odm") else work / partition
    command += ["--dirmap", f"/{partition}:{directory}"]
# Never mix an archived image with APEX staging from another build variant.
if apex is None:
    apex = work / "apex-unavailable"
    apex.mkdir()
command += ["--dirmap", f"/apex:{apex}"]
for prop in ("ro.product.first_api_level=35", "ro.vendor.api_level=34",
             "ro.boot.product.hardware.sku=lapis_gl", "ro.boot.product.vendor.sku="):
    command += ["--property", prop]
command += ["--kernel", f"{root / 'artifacts/stock/kernel-release.txt'}:{root / 'artifacts/stock/kernel.config'}"]
run("vintf", command)
report["limitations"] = [
    "VINTF uses the supplied stock capture; this script does not itself inspect the phone.",
    "SELinux merge matches init (-N); neverallow compliance is not established.",
    "No image modification, mount, flashing, phone reboot or hardware test is performed.",
]
report["apex_directory"] = str(apex)
report["apex_coverage"] = "supplied extracted tree" if args.apex_dir else "INCOMPLETE"
if not args.apex_dir:
    report["limitations"].append("No extracted APEX tree supplied; APEX HAL coverage is incomplete.")
output = root / "artifacts/system.img.validation.json"
output.write_text(json.dumps(report, indent=2) + "\n")
print(output)
print(json.dumps({name: report["checks"][name]["returncode"] for name in
                  ("filesystem", "treble-privapp-permissions", "treble-lapis-no-qti", "ims-carrier-mnc", "selinux-runtime-merge", "property-contexts",
                   "service_contexts", "hwservice_contexts", "ims-service-labels", "vintf")}))
print("Permissive domains:", report.get("permissive_domains"))
# A successful diagnostic run does not turn an incompatible image into an accepted build.
raise SystemExit(1 if any(report["checks"][name]["returncode"] for name in
                         ("filesystem", "treble-privapp-permissions", "treble-lapis-no-qti", "ims-carrier-mnc", "selinux-runtime-merge", "property-contexts",
                          "service_contexts", "hwservice_contexts", "ims-service-labels", "vintf"))
                 or report.get("permissive_domains") != [] or not args.apex_dir else 0)
