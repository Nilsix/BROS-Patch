import struct, os, sys, json, shutil

HERE = os.path.dirname(os.path.abspath(__file__))


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


INPUT_FILE = find_source_file(HERE)
GAME_FILE_NAME = os.path.basename(INPUT_FILE)   # real in-game name, e.g. "pl022.tadjpkg"

# in_path lives in sourceFile/, out_path lives in moddedFile/ - different
# folders, so no collision risk and no need to rename the output.
MODDED_DIR = os.path.join(HERE, "moddedFile")
os.makedirs(MODDED_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(MODDED_DIR, GAME_FILE_NAME)

# Which entries to patch and what value to set (max 3 digits to keep it simple)
TARGET_ENTRIES = [
    "2_evo_attack_evo_atk_hi01",
    # Ajoute d'autres entries ici si besoin
]
OLD_VALUE = b"50"  # current value in pl022.tadjpkg for this entry
NEW_VALUE = b"100"

raw = bytearray(open(INPUT_FILE, "rb").read())

# Parse entry table
count = struct.unpack_from("<I", bytes(raw), 0x20)[0]
entries = []
off = 0x24
for i in range(count):
    name = raw[off:off+64].split(b"\x00")[0].decode("utf-8", errors="replace")
    start, size = struct.unpack_from("<II", bytes(raw), off+64)
    entries.append({"name": name, "start": start, "size": size, "table_off": off})
    off += 72

for target_name in TARGET_ENTRIES:
    # Find target entry
    target = next((e for e in entries if e["name"] == target_name), None)
    if not target:
        print(f"Entry not found: {target_name}")
        continue

    old_pattern = b"guard_damage\x00" + OLD_VALUE + b"\x00"
    new_pattern = b"guard_damage\x00" + NEW_VALUE + b"\x00"
    diff = len(new_pattern) - len(old_pattern)  # +1 byte

    blob = bytes(raw[target["start"]:target["start"]+target["size"]])
    count_replacements = blob.count(old_pattern)
    if count_replacements == 0:
        print(f"Pattern not found in {target_name}")
        continue

    print(f"{target_name}: {count_replacements} replacement(s), size change: +{diff * count_replacements} bytes")

    # Replace in blob
    new_blob = blob.replace(old_pattern, new_pattern)
    size_delta = len(new_blob) - len(blob)

    # Rebuild raw: replace blob in place
    raw = bytearray(bytes(raw[:target["start"]]) + new_blob + bytes(raw[target["start"]+target["size"]:]))

    # Update size of this entry in table
    struct.pack_into("<I", raw, target["table_off"]+64+4, target["size"] + size_delta)
    target["size"] += size_delta

    # Update start offsets of all entries that come after
    for e in entries:
        if e["start"] > target["start"]:
            e["start"] += size_delta
            struct.pack_into("<I", raw, e["table_off"]+64, e["start"])

    print(f"Done: {target_name}")

open(OUTPUT_FILE, "wb").write(raw)
print(f"\nSaved to {OUTPUT_FILE}")

# ---- also drop it straight into the live game folder, so you can launch
# ---- and test immediately (relaunching the Community Patch launcher
# ---- will robocopy /MIR the official file back over this, so this is
# ---- always a safe, disposable test) ----
repo_root = os.path.dirname(os.path.dirname(HERE))   # .../BalanceLeadTools/change_number_of_bytes -> repo root
config_path = os.path.join(repo_root, "Json", "config.json")
try:
    with open(config_path, "r", encoding="utf-8") as f:
        game_path = json.load(f).get("GAME_PATH", "")
    if not game_path or not os.path.isdir(game_path):
        raise RuntimeError("GAME_PATH is empty or does not exist: %r" % game_path)
    dest = os.path.join(game_path, "Script", "Action", GAME_FILE_NAME)
    shutil.copyfile(OUTPUT_FILE, dest)
    print(f"  pushed to game: {dest}")
except Exception as e:
    print(f"  WARNING: could not push to game_path ({e}). Copy '{OUTPUT_FILE}' there by hand if you want to test.")
