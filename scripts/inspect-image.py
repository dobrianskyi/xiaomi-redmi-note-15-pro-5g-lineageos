#!/usr/bin/env python3
"""Record local GSI evidence without mounting, modifying, or flashing an image."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("image", type=Path, nargs="?", default=root / "source/out/target/product/tdgsi_arm64_ab/system.img")
parser.add_argument("--output", type=Path)
args = parser.parse_args()
image = args.image.resolve(strict=True)
if not image.is_relative_to(root):
    parser.error("Only inspect artifacts inside the bring-up directory")

with image.open("rb") as stream:
    header = stream.read(28)
    stream.seek(0)
    digest = hashlib.file_digest(stream, "sha256").hexdigest()
if len(header) != 28:
    raise SystemExit("Image is too short")
magic, major, minor, file_header, chunk_header, block_size, blocks, chunks, checksum = struct.unpack("<I4H4I", header)
if magic == 0xED26FF3A:
    if major != 1 or file_header < 28 or chunk_header < 12 or block_size == 0:
        raise SystemExit("Unsupported sparse header")
    image_format = "Android sparse (header inspected; chunks/filesystem not validated)"
    expanded_bytes = block_size * blocks
else:
    image_format = "raw (filesystem not yet validated)"
    expanded_bytes = image.stat().st_size

product = image.parent
props = {}
for relative in ("system/build.prop", "system/system/build.prop", "system/product/build.prop", "system/system_ext/build.prop"):
    path = product / relative
    if path.exists():
        props[relative] = dict(line.split("=", 1) for line in path.read_text().splitlines()
                               if line.startswith("ro.") and "=" in line)

policy_result = {"status": "NOT CHECKED", "reason": "compiled policy or sepolicy-analyze unavailable"}
analyzer = product.parents[2] / "host/linux-x86/bin/sepolicy-analyze"
policy = product / "root/sepolicy"
if analyzer.is_file() and policy.is_file():
    result = subprocess.run([str(analyzer), str(policy), "permissive"], capture_output=True, text=True)
    policy_result = {"status": "CHECKED" if result.returncode == 0 else "ERROR",
                     "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
                     "policy": str(policy.relative_to(root)),
                     "scope": "build output policy; does not prove stock vendor policy compatibility"}

report = {
    "image": str(image.relative_to(root)), "sha256": digest,
    "file_bytes": image.stat().st_size, "expanded_bytes": expanded_bytes,
    "format": image_format, "build_properties_from_staging_tree": props,
    "selinux_permissive_analysis": policy_result,
    "validation": {"filesystem": "NOT CHECKED", "vintf_with_stock_vendor": "NOT CHECKED",
                   "fits_current_phone_layout": "NOT CHECKED", "boot": "NOT TESTED",
                   "hardware": "NOT TESTED", "clean_rebuild": "NOT CHECKED"},
    "note": "Metadata inspection is not release acceptance. Staging properties must also be checked in the final image."
}
output = args.output or root / "artifacts" / (image.name + ".inspection.json")
if not output.resolve().is_relative_to(root):
    parser.error("Inspection output must be inside the bring-up directory")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2) + "\n")
print(output)
print(f"SHA256 {digest}; expanded size {expanded_bytes} bytes")
