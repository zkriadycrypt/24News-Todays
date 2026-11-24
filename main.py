"""Decode the bundled newspaper image and write it to /output/entry.png.

The entry image is stored as base64 text in assets/entry.png.b64 so the
repository stays plain UTF-8 text. Decoding is deterministic: the same
input bytes always produce the same /output/entry.png.
"""

import base64
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "assets" / "entry.png.b64"
DST = Path("/output") / "entry.png"


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def main():
    text = SRC.read_text(encoding="ascii")
    data = base64.b64decode("".join(text.split()))
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("decoded bytes are not a PNG image")
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if (width, height) != (1024, 1024):
        raise ValueError(f"unexpected image size {width}x{height}, want 1024x1024")
    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    # Round-trip check: what landed on disk must be byte-identical to what
    # was decoded, so a partial or corrupt write cannot slip through.
    if DST.read_bytes() != data:
        raise ValueError(f"round-trip mismatch writing {DST}")
    print(f"wrote {DST} ({len(data)} bytes, {width}x{height}, sha256 {digest})")


if __name__ == "__main__":
    main()
