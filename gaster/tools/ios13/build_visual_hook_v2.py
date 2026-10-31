import subprocess

hook_hex = (
    "c8d5ffb0" # adrp x8, 0xfffffff0070b2000
    "08ee2e91" # add x8, x8, #0xbb8 -> x8 = 0xfffffff0070b2bb8 (PE_Video)
    "000140f9" # ldr x0, [x8] -> x0 = v_baseAddr
    "e00000b4" # cbz x0, 0x28 (halt)
    "01e09f52" # mov w1, #0xff00 (Solid Green ARGB)
    "02009dd2" # mov x2, #0xe800
    "6200a0f2" # movk x2, #0x3, lsl #16 -> x2 = 256,000 pixels
    "014400b8" # str w1, [x0], #4
    "420400f1" # subs x2, x2, #1
    "c1ffff54" # b.ne loop
    "5f2003d5" # wfe
    "ff17ffff" # wait, b 0x28 is ff ff ff 17 in little endian!
)

# Correct b 0x28: offset is 0, so b . is 00 00 00 14 or b -4 is fd ff ff 17!
# At offset 0x28: wfe (5f 20 03 d5)
# At offset 0x2c: b 0x28 (relative offset -4 bytes = -1 instruction = 0x17fffffd -> fd ff ff 17)
hook_bytes = (
    bytes.fromhex("c8d5ffb0") + # adrp x8, -1351 pages -> 0xfffffff0070b2000
    bytes.fromhex("08e12e91") + # add x8, x8, #0xbb8 -> 0xfffffff0070b2bb8 (PE_Video)
    bytes.fromhex("000140f9") + # ldr x0, [x8] -> v_baseAddr
    bytes.fromhex("e00000b4") + # cbz x0, halt (+0x1c = offset 0x28)
    bytes.fromhex("01e09f52") + # mov w1, #0xff00
    bytes.fromhex("02009dd2") + # mov x2, #0xe800
    bytes.fromhex("6200a0f2") + # movk x2, #0x3, lsl #16 (256,000 pixels)
    bytes.fromhex("014400b8") + # str w1, [x0], #4
    bytes.fromhex("420400f1") + # subs x2, x2, #1
    bytes.fromhex("c1ffff54") + # b.ne paint_loop (-16 bytes)
    bytes.fromhex("5f2003d5") + # wfe
    bytes.fromhex("ffffff17")   # b halt (-4 bytes -> offset 0x28)
)

print(f"Hook bytes size: {len(hook_bytes)} bytes")
assert len(hook_bytes) == 48, f"Expected 48 bytes, got {len(hook_bytes)}"

out_path = "/mnt/c/Users/cmjnh/Desktop/ios13-port/gaster/tools/ios13/visual_hook_v2.bin"
with open(out_path, "wb") as f:
    f.write(hook_bytes)

print(f"Written to {out_path}")
cmd = ["aarch64-linux-gnu-objdump", "-b", "binary", "-m", "aarch64", "--adjust-vma=0xfffffff0075f9a20", "-D", out_path]
subprocess.run(cmd)
