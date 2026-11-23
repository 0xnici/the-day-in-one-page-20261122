#!/usr/bin/env python3
"""Entry point for make.fun news-image-20261122 — stdlib only.

Copies pre-rendered entry.png to MAKEFUN_OUTPUT_DIR/entry.png.
Validates PNG signature, IHDR dimensions (1024x1024), and size <= 1 MiB.
No external dependencies, no subprocess, no network.
"""

import os
import sys
import hashlib
import struct
import shutil
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
REQUIRED_WIDTH = 1024
REQUIRED_HEIGHT = 1024
MAX_SIZE = 1048576  # 1 MiB


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_png(data: bytes) -> tuple[int, int]:
    """Validate PNG signature and IHDR. Returns (width, height). Raises ValueError on failure."""
    if len(data) < 24:
        raise ValueError("file too small for PNG header")
    if data[:8] != PNG_SIGNATURE:
        raise ValueError("invalid PNG signature")
    # IHDR chunk starts at byte 8: length(4) + "IHDR"(4) + width(4) + height(4)
    width, height = struct.unpack(">II", data[16:24])
    if width != REQUIRED_WIDTH or height != REQUIRED_HEIGHT:
        raise ValueError(f"unexpected dimensions: {width}x{height}, expected {REQUIRED_WIDTH}x{REQUIRED_HEIGHT}")
    if len(data) > MAX_SIZE:
        raise ValueError(f"file too large: {len(data)} > {MAX_SIZE}")
    return width, height


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    src_path = repo_root / "entry.png"
    EXPECTED_SHA256 = "429829e99658519453022a9291092f5b5a7cafd491c9e814cff79fb0e2c43586"

    try:
        data = src_path.read_bytes()
    except OSError as e:
        print(f"ERROR: cannot read {src_path}: {e}", file=sys.stderr)
        return 1

    # Anti-tamper: verify source file matches expected hash
    actual_sha256 = sha256_bytes(data)
    if actual_sha256 != EXPECTED_SHA256:
        print(f"ERROR: source hash mismatch: got {actual_sha256}, expected {EXPECTED_SHA256}", file=sys.stderr)
        return 1

    try:
        validate_png(data)
    except ValueError as e:
        print(f"ERROR: validation failed: {e}", file=sys.stderr)
        return 1

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"ERROR: cannot create output dir {out_dir}: {e}", file=sys.stderr)
        return 1

    dst_path = out_dir / "entry.png"

    # Atomic write: write to temp with unique name, then rename
    import tempfile
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=out_dir, prefix=".entry.", suffix=".png.tmp", delete=False) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)
        tmp_path.chmod(0o644)
        os.replace(tmp_path, dst_path)
    except OSError as e:
        print(f"ERROR: write failed: {e}", file=sys.stderr)
        if tmp_path is not None:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
        return 1

    # Verify copy is byte-identical
    try:
        copied = dst_path.read_bytes()
        if copied != data:
            print("ERROR: copy verification failed (bytes differ)", file=sys.stderr)
            return 1
    except OSError as e:
        print(f"ERROR: cannot verify copy: {e}", file=sys.stderr)
        return 1

    print(f"OK {len(data)} bytes sha256={sha256_bytes(data)} -> {dst_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())