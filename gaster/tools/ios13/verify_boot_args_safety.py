import struct

KERNEL = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/kernelcache-ipad13-decompressed"

with open(KERNEL, "rb") as f:
    # Check 0xbd490 to 0xbe000
    f.seek(0xbd490)
    entry_branch = f.read(4)
    f.seek(0xbd494)
    nop_region = f.read(0xbe000 - 0xbd494)

print(f"Entry instruction: {entry_branch.hex()} (expected f2060014 = b 0xbf058)")
print(f"NOP padding length: {len(nop_region)} bytes ({len(nop_region)//4} instructions)")
all_nop = all(nop_region[i:i+4] == bytes.fromhex("1f2003d5") for i in range(0, len(nop_region), 4))
print(f"All instructions from 0xbd494 to 0xbe000 are NOP (1f2003d5): {all_nop}")

# Check 0xbd800 specifically for 736 bytes
offset_in_nop = 0xbd800 - 0xbd494
print(f"0xbd800 offset within NOP region: {offset_in_nop} to {offset_in_nop + 736}")
print(f"Remaining NOP space after new_boot_args: {len(nop_region) - (offset_in_nop + 736)} bytes")

# Check vector table at 0xbe000
with open(KERNEL, "rb") as f:
    f.seek(0xbe000)
    vbar_data = f.read(64)
print(f"First 16 bytes of VBAR table at 0xbe000: {vbar_data[:16].hex()}")
