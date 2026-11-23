#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261122.
Checks the rendered PNG and writes it to MAKEFUN_OUTPUT_DIR (default /output)."""
import os, sys, hashlib, shutil
from pathlib import Path

ENTRY = Path(__file__).with_name("entry.png")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    if not ENTRY.is_file():
        sys.exit(f"entry.png not found at {ENTRY}")

    # PNG signature
    with open(ENTRY, "rb") as f:
        sig = f.read(8)
    if sig != b"\x89PNG\r\n\x1a\n":
        sys.exit("not a valid PNG")

    # size & 1 MiB cap
    import subprocess, json
    res = subprocess.run(["file", str(ENTRY)], capture_output=True, text=True)
    if "1024 x 1024" not in res.stdout:
        sys.exit(f"unexpected dimensions: {res.stdout.strip()}")
    sz = ENTRY.stat().st_size
    if sz > 1048576:
        sys.exit(f"file too large: {sz} > 1048576")

    # write to output dir
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "entry.png"
    shutil.copy2(ENTRY, out_path)
    out_path.chmod(0o644)

    # verify byte-identical
    if sha256(ENTRY) != sha256(out_path):
        sys.exit("copy verification failed")

    print(f"OK {sz} bytes sha256={sha256(ENTRY)} -> {out_path}")

if __name__ == "__main__":
    main()