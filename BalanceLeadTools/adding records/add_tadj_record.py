#!/usr/bin/env python3
# =============================================================================
#  add_tadj_record.py
#  Adds ONE record to a single entry inside a .tadjpkg file, safely.
#  It bumps the record count and rebuilds ALL entry offsets for you, so the
#  game won't crash. See HOWTO_add_tadjpkg_record.txt for the full explanation.
#
#  Usage:  put your source .tadjpkg file inside a "sourceFile" folder next to
#          this script (that's the ONLY file that should be in there), edit the
#          SETTINGS block below, then run:   python add_tadj_record.py
#          The input file, the in-game push name, and the modded output name
#          are all derived automatically from whatever file sits in sourceFile/
#          - no path to type or rename by hand, ever.
# =============================================================================
import struct, os, sys, json, shutil, random


# ------------------------------- SETTINGS ------------------------------------
# INPUT_FILE / GAME_FILE_NAME / OUTPUT_FILE are all derived automatically from
# the single file found inside the "sourceFile" folder next to this script:
#   sourceFile/pl022.tadjpkg
#     -> read from          : sourceFile/pl022.tadjpkg
#     -> written to         : moddedFile/pl022.tadjpkg (created if missing -
#                             different folder than sourceFile/, so same name is fine)
#     -> pushed in-game as  : Script/Action/pl022.tadjpkg
# To work on a different character/file, just swap the file inside sourceFile/.
TARGET_ENTRY = "1_normal_attack_atk_hi01"  # move to add the record to

# The record you want to add:
RECORD_NAME  = "Grab"     # record type, e.g. "Enhance", "Visible", "SE_OneShot"
UNIQUE_ID    = "AUTO"       # "AUTO" = generate a random id and verify it's not already used
                            # by an existing record in the file. Or set a fixed 4-byte
                            # number yourself (e.g. 0xc1674abe) - it will still be checked
                            # against every real record id in the file and rejected if it collides.
START_FRAME  = 00.0          # first float in the 14-byte middle (when it fires)
SECOND_VALUE = 52.0          # second float in the middle (usually end/param)

# Parameters = list of (key, value) text pairs. Order matters. Example is the
PARAMS = [
    ("MyBindJoint", "hand_L"),
    ("EnemyBindJoint", "neck"),
    ("EnemyOffsetRot", "0.000000,0.000000,0.000000"),
    ("EnemyStartAction", "dam_neckbind_hit"),
    ("EnemyEndAction", "dam_blown_fall_loop"),
    ("EnemyCancelAction", "dam_blown_fall_loop"),
    ("EndFixTime", "20.000000"),
    ("CancelFixTime", "20.000000"),
]
# -----------------------------------------------------------------------------



def build_record(uid):
    """Assemble the record bytes exactly per the confirmed layout."""
    rec  = struct.pack("<I", uid)                       # 4  : unique id
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


def is_uid_used(data, uid):
    """True if these exact 4 bytes appear anywhere in the file.

    NOTE: only the "Enhance" record's 14-byte-middle layout from the HOWTO is
    confirmed. Pre-existing record types (ComboStart, CancelTiming, AfterCombo
    Reset, ...) do NOT follow that same layout (verified against the real
    pl022.tadjpkg - trying to walk them record-by-record misparses and throws).
    So instead of a structural walk, we substring-search the raw bytes: every
    real uid is necessarily stored as those literal 4 bytes somewhere, so this
    can never miss a real collision. It can rarely flag a coincidental 4-byte
    match that isn't really a uid, but that just costs a harmless retry."""
    return struct.pack("<I", uid) in data


def pick_unique_id(data):
    """Generate a random 4-byte id that does not collide per is_uid_used()."""
    while True:
        candidate = random.randint(0x10000000, 0xFFFFFFFF)
        if not is_uid_used(data, candidate):
            return candidate


def find_source_file(here):
    """Auto-detect the input file: the single file sitting inside the
    "sourceFile" folder next to this script. That way you never type or
    rename a path by hand - just swap the file in that folder."""
    source_dir = os.path.join(here, "sourceFile")
    if not os.path.isdir(source_dir):
        os.makedirs(source_dir, exist_ok=True)
        sys.exit("ERROR: 'sourceFile' folder was missing (just created it).\n"
                  "  Fix : put your .tadjpkg source file inside : %s" % source_dir)

    candidates = [f for f in os.listdir(source_dir)
                  if os.path.isfile(os.path.join(source_dir, f))]
    if len(candidates) == 0:
        sys.exit("ERROR: no file found in '%s'.\n"
                  "  Fix : put your .tadjpkg source file inside it." % source_dir)
    if len(candidates) > 1:
        sys.exit("ERROR: more than one file found in '%s' (%s).\n"
                  "  Fix : keep only the one source file you want to work on in there."
                  % (source_dir, ", ".join(candidates)))
    return os.path.join(source_dir, candidates[0])


def main():
    # Resolve paths relative to THIS script's folder, so you can just drop the
    # script anywhere and run it - no matter where your terminal is pointed or
    # if you double-click it. (Absolute paths are used as-is.)
    here = os.path.dirname(os.path.abspath(__file__))
    in_path = find_source_file(here)
    game_file_name = os.path.basename(in_path)     # real in-game name, e.g. "pl022.tadjpkg"
    # in_path lives in sourceFile/, out_path lives in moddedFile/ - different
    # folders, so no collision risk and no need for a "_modded" suffix in the name.
    out_dir = os.path.join(here, "moddedFile")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, game_file_name)

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

    # ---- resolve the unique id: AUTO picks + verifies, a fixed value only gets verified ----
    if isinstance(UNIQUE_ID, str) and UNIQUE_ID.strip().upper() == "AUTO":
        actual_uid = pick_unique_id(data)
        print("  UNIQUE_ID (AUTO) : 0x%08X (verified absent from the file)" % actual_uid)
    else:
        actual_uid = UNIQUE_ID
        if is_uid_used(data, actual_uid):
            sys.exit("ERROR: UNIQUE_ID 0x%08X already appears in this file.\n"
                      "  Fix : pick another value, or set UNIQUE_ID = \"AUTO\" in the SETTINGS block."
                      % actual_uid)

    rec = build_record(actual_uid)

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
    print("  record        : %s (uid 0x%08X)" % (RECORD_NAME, actual_uid))
    print("  record count  : %d -> %d" % (old_rc, old_rc + 1))
    print("  added bytes   : %d" % len(rec))
    print("  file size     : %d -> %d" % (len(data), len(out)))
    print("  read from     : %s" % in_path)
    print("  saved to      : %s" % out_path)

    # ---- also drop it straight into the live game folder, so you can launch
    # ---- and test immediately (relaunching the Community Patch launcher
    # ---- will robocopy /MIR the official file back over this, so this is
    # ---- always a safe, disposable test) ----
    repo_root = os.path.dirname(os.path.dirname(here))   # .../BalanceLeadTools/adding records -> repo root
    config_path = os.path.join(repo_root, "Json", "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            game_path = json.load(f).get("GAME_PATH", "")
        if not game_path or not os.path.isdir(game_path):
            raise RuntimeError("GAME_PATH is empty or does not exist: %r" % game_path)
        dest = os.path.join(game_path, "Script", "Action", game_file_name)
        shutil.copyfile(out_path, dest)
        print("  pushed to game: %s" % dest)
    except Exception as e:
        print("  WARNING: could not push to game_path (%s). Copy '%s' there by hand if you want to test."
              % (e, out_path))

    print("Test it in-game. If it crashes at load, re-check the 14-byte middle.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        print(e)
    input("Press Enter to close...")