import struct

kc_path = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/kernelcache-ipad13-decompressed"
with open(kc_path, "rb") as f:
    f.seek(32)
    symoff = 0
    nsyms = 0
    stroff = 0
    strsize = 0
    
    # Read commands until LC_SYMTAB
    for _ in range(22):
        cmd, cmdsize = struct.unpack("<II", f.read(8))
        cmd_data = f.read(cmdsize - 8)
        if cmd == 0x2: # LC_SYMTAB
            symoff, nsyms, stroff, strsize = struct.unpack("<IIII", cmd_data[:16])
            break

    f.seek(stroff)
    string_table = f.read(strsize)
    
    f.seek(symoff)
    symbols = []
    for _ in range(nsyms):
        n_strx, n_type, n_sect, n_desc, n_value = struct.unpack("<IBBHQ", f.read(16))
        if n_strx < len(string_table):
            end = string_table.find(b"\x00", n_strx)
            name = string_table[n_strx:end].decode("latin1", errors="ignore")
            symbols.append((name, n_value))

print(f"Total parsed symbols: {len(symbols)}")
matches = [s for s in symbols if any(k in s[0].lower() for k in ["pe_state", "bootargs", "video", "iokit", "panic"])]
for name, val in matches[:40]:
    print(f"  {hex(val)}: {name}")
