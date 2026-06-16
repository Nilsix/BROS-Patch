import sys, re, ctypes, random, pathlib

def make_key(key_signed):
    key32 = ctypes.c_int32(key_signed).value
    k = [(i + (key32 >> (4*i))) & 0xFF for i in range(8)]
    mbit = [ki & 1 for ki in k]
    return k, mbit

def decode_cso_bytes(data: bytes):
    line, sep, blob = data.partition(b"\n")
    if not sep:
        raise ValueError("No newline in header")
    m = re.match(rb"_cso_(\d+)_(\-?\d+)$", line.strip())
    if not m:
        raise ValueError("Not a _cso_ header")
    key = int(m.group(2))
    k, mbit = make_key(key)
    out = bytearray(len(blob))
    for i, b in enumerate(blob):
        ki = k[i & 7]
        delta = ki if mbit[i & 7] else ((-ki) & 0xFF)
        out[i] = (b - delta) & 0xFF
    while out and out[-1] == 0:
        out.pop()
    return bytes(out)

def encode_cso_bytes(csv_bytes: bytes) -> bytes:
    # always version=1, random key
    key = random.randint(-2**31, 2**31-1)
    k, mbit = make_key(key)
    out = bytearray(len(csv_bytes))
    for i, b in enumerate(csv_bytes):
        ki = k[i & 7]
        delta = ki if mbit[i & 7] else ((-ki) & 0xFF)
        out[i] = (b + delta) & 0xFF
    header = f"_cso_1_{key}\n".encode("ascii")
    return header + bytes(out)

def to_csv(path: str):
    data = pathlib.Path(path).read_bytes()
    #remove the last 16 bytes
    data = data[:-16]
    
    csv_bytes = decode_cso_bytes(data)
    outpath = pathlib.Path(path).with_suffix(".csv")
    outpath.write_bytes(csv_bytes)
    print(f"Decoded -> {outpath}")

def to_fsv(path: str):
    csv_bytes = pathlib.Path(path).read_bytes()
    fsv_bytes = encode_cso_bytes(csv_bytes)
    # add 16 null bytes
    fsv_bytes += b"\x00" * 16
    outpath = pathlib.Path(path).with_suffix(".fsv")
    outpath.write_bytes(fsv_bytes)
    print(f"Encoded -> {outpath}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cso_tool.py to_csv <file> | to_fsv <file>")
        sys.exit(1)
    cmd, file = sys.argv[1], sys.argv[2]
    if cmd == "to_csv":
        to_csv(file)
    elif cmd == "to_fsv":
        to_fsv(file)
    else:
        print("Unknown command")
