#!/usr/bin/env python3
"""Fetch the exact IMS APK verified against the working lapis phone."""
import hashlib
import json
from pathlib import Path
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
spec = json.loads((ROOT / "research/mediatek-ims.json").read_text())
destination = ROOT / "local/device/local/gsi/apps/MediatekIms/ims.apk"


def matches(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() == spec["sha256"]


if destination.exists():
    if not matches(destination):
        raise SystemExit(f"IMS APK hash mismatch: {destination}; refusing to overwrite")
    print("Verified pinned MediaTek IMS APK")
else:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as out:
            temporary = Path(out.name)
            with urllib.request.urlopen(spec["url"], timeout=60) as response:
                while chunk := response.read(1024 * 1024):
                    out.write(chunk)
        if not matches(temporary):
            raise SystemExit("Downloaded IMS APK differs from the verified phone APK")
        temporary.chmod(0o644)
        temporary.replace(destination)
        print("Downloaded and verified pinned MediaTek IMS APK")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
