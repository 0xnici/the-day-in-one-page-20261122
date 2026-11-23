#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261122 v2 Force_Last.

Generates the front page via render.py and writes it to MAKEFUN_OUTPUT_DIR (default /output).
"""

import os
import sys
import hashlib
import subprocess
from pathlib import Path

# Import the render module
sys.path.insert(0, str(Path(__file__).parent / "tools"))
from render import main as render_main


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    # Generate the PNG in a temp location
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Call render.py's main: render_main(["render.py", output_path])
        rc = render_main(["render.py", tmp_path])
        if rc != 0:
            sys.exit(f"render failed with code {rc}")

        # Verify PNG signature
        with open(tmp_path, "rb") as f:
            sig = f.read(8)
        if sig != b"\x89PNG\r\n\x1a\n":
            sys.exit("not a valid PNG")

        # Verify dimensions: 1024x1024
        res = subprocess.run(["file", tmp_path], capture_output=True, text=True)
        if "1024 x 1024" not in res.stdout:
            sys.exit(f"unexpected dimensions: {res.stdout.strip()}")

        # Verify size cap: <= 1 MiB
        sz = os.path.getsize(tmp_path)
        if sz > 1048576:
            sys.exit(f"file too large: {sz} > 1048576")

        # Write to output dir (MUST exist, must NOT be deleted)
        out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "entry.png"

        # Copy and verify byte-identical
        import shutil
        shutil.copy2(tmp_path, out_path)
        out_path.chmod(0o644)

        if sha256(Path(tmp_path)) != sha256(out_path):
            sys.exit("copy verification failed")

        print(f"OK {sz} bytes sha256={sha256(Path(tmp_path))} -> {out_path}")

    finally:
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


if __name__ == "__main__":
    main()