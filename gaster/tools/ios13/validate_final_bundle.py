import hashlib
import os
import struct
import subprocess
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm64_const import (
    UC_ARM64_REG_X0, UC_ARM64_REG_X1, UC_ARM64_REG_X2,
    UC_ARM64_REG_X19, UC_ARM64_REG_X20, UC_ARM64_REG_PC
)

BUNDLE_DIR = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/boot-bundle"
KERNEL_BUNDLE = os.path.join(BUNDLE_DIR, "kernelcache.integrated_bundle")
DTB_FILE = os.path.join(BUNDLE_DIR, "devicetree.n61.im4p")
TRAMPOLINE_BIN = "/mnt/c/Users/cmjnh/Desktop/ios13-port/gaster/tools/ios13/trampoline_v2.bin"
HOOK_BIN = "/mnt/c/Users/cmjnh/Desktop/ios13-port/gaster/tools/ios13/visual_hook_v2.bin"

print("=================================================================")
print("=== FINAL INDEPENDENT AUDIT & VERIFICATION OF BOOT BUNDLE ===")
print("=================================================================")

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# 1. Hashes of All Bundle Artifacts
print("\n[STEP 1: HASHES OF ALL BOOT BUNDLE ARTIFACTS]")
for name, p in [
    ("kernelcache.integrated_bundle", KERNEL_BUNDLE),
    ("trampoline_v2.bin", TRAMPOLINE_BIN),
    ("visual_hook_v2.bin", HOOK_BIN),
    ("devicetree.n61.im4p", DTB_FILE),
]:
    sz = os.path.getsize(p)
    h = sha256_file(p)
    print(f"  {name:<30} Size: {sz:>8} bytes | SHA256: {h}")

# 2. Mach-O Integrity Check on kernelcache.integrated_bundle
print("\n[STEP 2: MACH-O HEADER & ENTRY POINT VERIFICATION]")
with open(KERNEL_BUNDLE, "rb") as f:
    hdr = f.read(32)
    magic, cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags, reserved = struct.unpack("<IIIIIIII", hdr)
    assert magic == 0xfeedfacf, f"Invalid Mach-O magic: {hex(magic)}"
    assert cputype == 0x100000c, f"Not ARM64 cputype: {hex(cputype)}"
    print(f"  Mach-O 64-bit Magic: {hex(magic)} [PASS]")
    print(f"  CPU Type: ARM64 ({hex(cputype)}) [PASS]")
    
    # Parse commands to find LC_UNIXTHREAD
    found_thread = False
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack("<II", f.read(8))
        cmd_data = f.read(cmdsize - 8)
        if cmd == 0x5: # LC_UNIXTHREAD
            found_thread = True
            flavor, count = struct.unpack("<II", cmd_data[:8])
            pc = struct.unpack("<Q", cmd_data[8 + 32*8: 8 + 32*8 + 8])[0]
            print(f"  LC_UNIXTHREAD Entry PC: {hex(pc)} [PASS]")
            assert pc == 0xfffffff0070c1490, "Entry PC altered!"
            break
    assert found_thread, "LC_UNIXTHREAD not found!"

# 3. Direct Binary Inspection of Integrated Regions
print("\n[STEP 3: INTEGRATED REGION VERIFICATION DIRECTLY FROM BUNDLE]")
ENTRY_OFF = 0xbd490
IOKIT_OFF = 0x5f5a20

with open(KERNEL_BUNDLE, "rb") as f:
    f.seek(ENTRY_OFF)
    integrated_tramp = f.read(124)
    f.seek(IOKIT_OFF)
    integrated_hook = f.read(48)

with open(TRAMPOLINE_BIN, "rb") as f:
    expected_tramp = f.read()

with open(HOOK_BIN, "rb") as f:
    expected_hook = f.read()

assert integrated_tramp == expected_tramp, "Integrated trampoline bytes mismatch!"
assert integrated_hook == expected_hook, "Integrated visual hook bytes mismatch!"
print(f"  Trampoline v2 at 0xbd490: 124 bytes match binary bit-for-bit [PASS]")
print(f"  Visual Hook v2 at 0x5f5a20: 48 bytes match binary bit-for-bit [PASS]")

# 4. Unicorn CPU Emulation of Integrated Binary
print("\n[STEP 4: UNICORN AARCH64 HARDWARE CPU EMULATION FROM BUNDLE FILE]")
uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
PHYS_BASE = 0x800000000
uc.mem_map(PHYS_BASE, 2 * 1024 * 1024) # 2MB kernel code page
uc.mem_map(PHYS_BASE + 0x200000, 2 * 1024 * 1024) # 2MB boot args page

# Write trampoline directly from integrated bundle
uc.mem_write(PHYS_BASE + ENTRY_OFF, integrated_tramp)

# Setup Darwin 18 boot args
OLD_ARGS_ADDR = PHYS_BASE + 0x201000
ba = bytearray(0x180)
struct.pack_into("<HH", ba, 0x00, 1, 2) # Darwin 18 Rev=1, Ver=2
struct.pack_into("<Q", ba, 0x08, 0xfffffff007004000) # virtBase
struct.pack_into("<Q", ba, 0x10, PHYS_BASE)          # physBase
struct.pack_into("<Q", ba, 0x18, 0x40000000)          # memSize
struct.pack_into("<Q", ba, 0x20, PHYS_BASE + 0x2200000)
struct.pack_into("<Q", ba, 0x60, PHYS_BASE + 0x240000)
struct.pack_into("<I", ba, 0x68, 0x1a000)
cmd = b"debug=0x144 -v keepsyms=1 serial=3"
ba[0x70:0x70+len(cmd)] = cmd
struct.pack_into("<Q", ba, 0x170, 0x00000028)
struct.pack_into("<Q", ba, 0x178, 0x40000000)
uc.mem_write(OLD_ARGS_ADDR, bytes(ba))

# Init register x0
uc.reg_write(UC_ARM64_REG_X0, OLD_ARGS_ADDR)

# Put breakpoint at start_cpu (0xbf058)
DEST_ADDR = PHYS_BASE + 0xbf058
uc.mem_write(DEST_ADDR, bytes.fromhex("1f2003d5c0035fd6")) # nop; ret

# Run CPU
uc.emu_start(PHYS_BASE + ENTRY_OFF, DEST_ADDR)

pc_out = uc.reg_read(UC_ARM64_REG_PC)
x0_out = uc.reg_read(UC_ARM64_REG_X0)

assert pc_out == DEST_ADDR, f"Unicorn CPU reached wrong PC: {hex(pc_out)}"
assert x0_out == PHYS_BASE + 0xbd800, f"Unicorn CPU x0 wrong: {hex(x0_out)}"
print(f"  Unicorn AArch64 CPU Execution: Success! Reached {hex(pc_out)}, X0={hex(x0_out)} [PASS]")

# Check new boot args in memory
new_ba = uc.mem_read(x0_out, 0x2e0)
rev, ver = struct.unpack_from("<HH", new_ba, 0x00)
assert (rev, ver) == (2, 2), f"Version mismatch: {rev}, {ver}"
bflags = struct.unpack_from("<Q", new_ba, 0x2d0)[0]
assert bflags == 0x28, f"bootFlags mismatch: {hex(bflags)}"
msize = struct.unpack_from("<Q", new_ba, 0x2d8)[0]
assert msize == 0x40000000, f"memSize mismatch: {hex(msize)}"
print(f"  Unicorn Output Verification: Rev={rev}, Ver={ver}, bootFlags={hex(bflags)}, memSize={hex(msize)} [PASS]")

print("\n=================================================================")
print("=== ALL INDEPENDENT AUDIT VERIFICATION CHECKS PASSED 100% ===")
print("=================================================================")
