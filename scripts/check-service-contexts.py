#!/usr/bin/env python3
"""Load merged service contexts with Android's libselinux service backend.

Matches servicemanager's syntax/duplicate checks, not full policy validation.
"""
import argparse
import ctypes
import os
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("contexts", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
library = root / "source/out/host/linux-x86/lib64/libselinux.so"
lib = ctypes.CDLL(str(library), use_errno=True)


class Option(ctypes.Structure):
    _fields_ = [("type", ctypes.c_int), ("value", ctypes.c_char_p)]


# Constants from libselinux/include/selinux/label.h. As in servicemanager,
# SELABEL_OPT_VALIDATE is not enabled; duplicate identical labels are allowed.
options = (Option * 1)(Option(3, os.fsencode(args.contexts.resolve(strict=True))))
lib.selabel_open.argtypes = [ctypes.c_uint, ctypes.POINTER(Option), ctypes.c_uint]
lib.selabel_open.restype = ctypes.c_void_p
lib.selabel_close.argtypes = [ctypes.c_void_p]
lib.selabel_close.restype = None
handle = lib.selabel_open(5, options, 1)
if not handle:
    raise SystemExit(f"Service context backend failed: {os.strerror(ctypes.get_errno())}")
lib.selabel_close(handle)
print("Service context backend: PASS")
