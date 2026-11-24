#!/usr/bin/env python3
"""Regenerate entry.png for news-23 b165 front-page-dense (stdlib only, no PIL).

Validates the embedded PNG bytes (signature, IHDR 1024x1024, CRC of every
chunk, IDAT payload, IEND as the last chunk, size bounds, expected sha256)
and writes them ONLY to os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR",
"out"), "entry.png"). Never writes next to this file.
"""
import hashlib
import os
import struct
import sys
import zlib

EXPECTED_SHA256 = "e740f9b6b5187aae7f465eb566c2c73d3d64fea4b39a1cd6564b3a23e73fa4fc"
EXPECTED_SIZE = 146431
MIN_SIZE = 10000
MAX_SIZE = 1024 * 1024
PNG_SIG = b"\x89PNG\r\n\x1a\n"


def fail(msg):
    print("error: " + msg, file=sys.stderr)
    sys.exit(1)


def main():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(src_dir, "entry.png")
    if not os.path.isfile(src):
        fail("entry.png not found next to main.py")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    if not out_dir:
        fail("MAKEFUN_OUTPUT_DIR is empty")
    out_dir_abs = os.path.abspath(out_dir)
    repo_abs = os.path.abspath(src_dir)
    if out_dir_abs == repo_abs or out_dir_abs.startswith(repo_abs + os.sep):
        fail("MAKEFUN_OUTPUT_DIR must not be inside the repo")
    if os.path.exists(out_dir_abs) and not os.path.isdir(out_dir_abs):
        fail("MAKEFUN_OUTPUT_DIR is a file, not a directory")
    out_path = os.path.join(out_dir_abs, "entry.png")
    if os.path.abspath(out_path) == os.path.abspath(src):
        fail("output would overwrite the source entry.png")

    with open(src, "rb") as f:
        data = f.read()

    if len(data) < MIN_SIZE:
        fail("PNG too small: %d bytes" % len(data))
    if len(data) > MAX_SIZE:
        fail("PNG over 1 MiB: %d bytes" % len(data))
    if data[:8] != PNG_SIG:
        fail("bad PNG signature")

    # First chunk must be IHDR, 13 bytes, 1024x1024, bit depth 8,
    # colour type 2 or 6, compression/filter/interlace 0.
    off = 8
    length = struct.unpack(">I", data[off:off + 4])[0]
    ctype = data[off + 4:off + 8]
    if ctype != b"IHDR" or length != 13:
        fail("first chunk is not a 13-byte IHDR")
    ihdr = data[off + 8:off + 21]
    width, height, depth, ctype_byte, comp, filt, inter = struct.unpack(
        ">IIBBBBB", ihdr)
    if (width, height) != (1024, 1024):
        fail("dimensions are %dx%d, expected 1024x1024" % (width, height))
    if depth != 8:
        fail("bit depth %d, expected 8" % depth)
    if ctype_byte not in (2, 6):
        fail("colour type %d, expected 2 or 6" % ctype_byte)
    if comp != 0 or filt != 0 or inter != 0:
        fail("compression/filter/interlace must all be 0")
    stored_crc = struct.unpack(">I", data[off + 21:off + 25])[0]
    calc_crc = zlib.crc32(b"IHDR" + ihdr) & 0xFFFFFFFF
    if stored_crc != calc_crc:
        fail("IHDR CRC mismatch")

    # Chunk walk: CRC covers chunk type + data (not the length field) for
    # every chunk, IDAT non-empty, IEND 0-byte as the last chunk with no
    # trailing data.
    off = 8
    idat_total = 0
    seen_iend = False
    while off < len(data):
        if off + 8 > len(data):
            fail("truncated chunk header at offset %d" % off)
        length = struct.unpack(">I", data[off:off + 4])[0]
        ctype = data[off + 4:off + 8]
        end = off + 8 + length + 4
        if end > len(data):
            fail("truncated chunk %r at offset %d" % (ctype, off))
        chunk_data = data[off + 8:off + 8 + length]
        stored_crc = struct.unpack(">I", data[off + 8 + length:end])[0]
        calc_crc = zlib.crc32(ctype + chunk_data) & 0xFFFFFFFF
        if stored_crc != calc_crc:
            fail("CRC mismatch in chunk %r" % ctype)
        if ctype == b"IDAT":
            if length == 0:
                fail("empty IDAT chunk")
            idat_total += length
        if ctype == b"IEND":
            if length != 0:
                fail("IEND must be 0 bytes")
            if end != len(data):
                fail("trailing data after IEND")
            seen_iend = True
            break
        off = end
    if not seen_iend:
        fail("missing IEND chunk")
    if idat_total < 1000:
        fail("IDAT payload too small: %d bytes" % idat_total)

    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        fail("sha256 mismatch: got %s" % digest)
    if len(data) != EXPECTED_SIZE:
        fail("size mismatch: got %d, expected %d" % (len(data), EXPECTED_SIZE))

    os.makedirs(out_dir_abs, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(data)

    with open(out_path, "rb") as f:
        written = f.read()
    if written != data:
        fail("re-read output differs from source")
    print("wrote %s (%d bytes, sha256 %s)" % (out_path, len(data), digest))


if __name__ == "__main__":
    main()
