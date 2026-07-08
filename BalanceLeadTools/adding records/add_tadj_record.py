#!/usr/bin/env python3
# =============================================================================
#  add_tadj_record.py
#  Adds ONE record to a single entry inside a .tadjpkg file, safely.
#  It bumps the record count and rebuilds ALL entry offsets for you, so the
#  game won't crash. See HOWTO_add_tadjpkg_record.txt for the full explanation.
#
#  Usage:  put this script IN THE SAME FOLDER as your pl022.tadjpkg, edit the
#          SETTINGS block below, then run:   python add_tadj_record.py
#          (It looks for the file next to itself, so where your terminal is
#           pointed does not matter.)
# =============================================================================
import struct, os, sys


# ------------------------------- SETTINGS ------------------------------------
INPUT_FILE   = "pl022.tadjpkg"              # file to read (keep a backup!)
OUTPUT_FILE  = "pl022_modded.tadjpkg"       # file to write (use a NEW name)
TARGET_ENTRY = "1_normal_attack_atk_hi01"  # move to add the record to

# The record you want to add:
RECORD_NAME  = "SlowMotionRate"     # record type, e.g. "Enhance", "Visible", "SE_OneShot"
UNIQUE_ID    = 0xc1674abe   # any 4-byte number not already used in the file
START_FRAME  = 00.0          # first float in the 14-byte middle (when it fires)
SECOND_VALUE = 52.0          # second float in the middle (usually end/param)

# Parameters = list of (key, value) text pairs. Order matters. Example is the
PARAMS = [
    ("slow_motion_rate", "0.500000"),
]
# -----------------------------------------------------------------------------



def build_record():
    """Assemble the record bytes exactly per the confirmed layout."""
    rec  = struct.pack("<I", UNIQUE_ID)                 # 4  : unique id
    rec += RECORD_NAME.encode("ascii") + b"\x00"        # name + terminator
    rec += struct.pack("<IBffB", 0, 0,                  # the 14-byte middle:
                       float(START_FRAME),              #   u32=0, u8=0,
                       float(SECOND_VALUE), 0)          #   f32, f32, u8=0
    rec += struct.pack("<I", len(PARAMS))               # 4  : parameter count
    for key, val in PARAMS:                             # each key\0 value\0
        rec += key.encode("shift_jis") + b"\x00"
        rec += val.encode("shift_jis") + b"\x00"
    return rec


def find_record_count_pos(blob):
    """Return the byte offset (within a blob) of its uint32 record count."""
    p = 4                                    # skip "adjb"
    for _ in range(3):                       # skip the 3 text strings
        p = blob.index(b"\x00", p) + 1
    p += 17                                  # skip the 17 fixed bytes
    return p                                 # <- uint32 record count sits here


def main():
    # Resolve paths relative to THIS script's folder, so you can just drop the
    # .tadjpkg next to this script and run it - no matter where your terminal
    # is pointed or if you double-click it. (Absolute paths are used as-is.)
    here = os.path.dirname(os.path.abspath(__file__))
    in_path  = INPUT_FILE  if os.path.isabs(INPUT_FILE)  else os.path.join(here, INPUT_FILE)
    out_path = OUTPUT_FILE if os.path.isabs(OUTPUT_FILE) else os.path.join(here, OUTPUT_FILE)

    if not os.path.exists(in_path):
        sys.exit("ERROR: input file not found.\n"
                 "  Looked here : %s\n"
                 "  Fix         : put '%s' in that folder, or set INPUT_FILE to a\n"
                 "                full path in the SETTINGS block."
                 % (in_path, INPUT_FILE))

    data = open(in_path, "rb").read()
    if data[:10] != b"actadj_pkg":
        sys.exit("ERROR: this does not look like a .tadjpkg file: " + in_path)

    count = struct.unpack_from("<I", data, 0x20)[0]

    # ---- read the entry table into (name, offset, size) ----
    entries = []
    off = 0x24
    for _ in range(count):
        name = data[off:off + 64].split(b"\x00")[0].decode("shift_jis", "replace")
        start, size = struct.unpack_from("<II", data, off + 64)
        entries.append((name, start, size))
        off += 72

    # ---- pull each blob out ----
    blobs = [bytearray(data[o:o + s]) for _, o, s in entries]

    # sanity: blobs must be contiguous
    pos = 0x24 + count * 72
    for (nm, o, s), _b in zip(entries, blobs):
        if o != pos:
            sys.exit("ERROR: file is not contiguous at entry '%s'. Aborting." % nm)
        pos += s

    # ---- locate the target ----
    idx = next((i for i, e in enumerate(entries) if e[0] == TARGET_ENTRY), None)
    if idx is None:
        sys.exit("ERROR: target entry not found: " + TARGET_ENTRY)

    rec = build_record()
    if struct.pack("<I", UNIQUE_ID) in data:
        print("WARNING: UNIQUE_ID may already be in use - consider changing it.")

    blob = blobs[idx]
    cpos = find_record_count_pos(blob)
    old_rc = struct.unpack_from("<I", blob, cpos)[0]

    # ---- insert record (right after the count) + bump this entry's count ----
    struct.pack_into("<I", blob, cpos, old_rc + 1)
    blobs[idx] = blob[:cpos + 4] + rec + blob[cpos + 4:]

    # ---- rebuild the whole file with fresh offsets (Rule 3, done for you) ----
    out = bytearray(data[:0x24])                 # header up to entry table
    out += b"\x00" * (count * 72)                # blank table, filled below
    struct.pack_into("<I", out, 0x20, count)     # entry count unchanged
    pos = 0x24 + count * 72
    for i, (name, _o, _s) in enumerate(entries):
        nb = name.encode("shift_jis")
        row = 0x24 + i * 72
        out[row:row + 64] = nb + b"\x00" * (64 - len(nb))
        struct.pack_into("<II", out, row + 64, pos, len(blobs[i]))
        pos += len(blobs[i])
    for bl in blobs:
        out += bl

    open(out_path, "wb").write(out)

    print("OK - record added.")
    print("  entry         : %s" % TARGET_ENTRY)
    print("  record        : %s (uid 0x%08X)" % (RECORD_NAME, UNIQUE_ID))
    print("  record count  : %d -> %d" % (old_rc, old_rc + 1))
    print("  added bytes   : %d" % len(rec))
    print("  file size     : %d -> %d" % (len(data), len(out)))
    print("  read from     : %s" % in_path)
    print("  saved to      : %s" % out_path)
    print("Test it in-game. If it crashes at load, re-check the 14-byte middle.")


if __name__ == "__main__":
    main()