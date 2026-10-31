import struct
import sys
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm64_const import (
    UC_ARM64_REG_X0, UC_ARM64_REG_X1, UC_ARM64_REG_X2,
    UC_ARM64_REG_X19, UC_ARM64_REG_X20, UC_ARM64_REG_PC
)

print("=== TRUE HARDWARE-LEVEL ARM64 EMULATION (UNICORN ENGINE) ===")

# Read compiled trampoline_v2 binary
with open("/mnt/c/Users/cmjnh/Desktop/ios13-port/gaster/tools/ios13/trampoline_v2.bin", "rb") as f:
    trampoline_code = f.read()

print(f"Loaded trampoline binary: {len(trampoline_code)} bytes")

# Initialize Unicorn AArch64 CPU
uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)

# Physical Memory Map (Aligned to 2MB or 64KB for Unicorn page tables)
PHYS_BASE     = 0x800000000 # 32GB boundary (A8 DRAM physical space)
CODE_PAGE     = 0x800000000 # 2MB page containing kernel & trampoline
OLD_ARGS_PAGE = 0x800200000 # 2MB page containing old boot args & DTB

PAGE_SIZE = 2 * 1024 * 1024 # 2MB pages

uc.mem_map(CODE_PAGE, PAGE_SIZE)
uc.mem_map(OLD_ARGS_PAGE, PAGE_SIZE)

# Place trampoline code at physical entry point: PHYS_BASE + 0xbd490
ENTRY_PC = PHYS_BASE + 0xbd490
uc.mem_write(ENTRY_PC, trampoline_code)

# Setup realistic iOS 12 (Darwin 18) boot_args in DRAM at OLD_ARGS_PAGE
OLD_BOOT_ARGS = OLD_ARGS_PAGE + 0x1000
mem_buf = bytearray(0x180) # 384 bytes
struct.pack_into("<HH", mem_buf, 0x00, 1, 2)              # Revision=1, Version=2
struct.pack_into("<Q", mem_buf, 0x08, 0xfffffff007004000) # virtBase
struct.pack_into("<Q", mem_buf, 0x10, PHYS_BASE)          # physBase
struct.pack_into("<Q", mem_buf, 0x18, 0x40000000)          # memSize (1 GB)
struct.pack_into("<Q", mem_buf, 0x20, PHYS_BASE + 0x2200000) # topOfKernelData
struct.pack_into("<Q", mem_buf, 0x60, OLD_ARGS_PAGE + 0x40000) # deviceTreeP
struct.pack_into("<I", mem_buf, 0x68, 0x1a000)            # deviceTreeLength

orig_cmdline = b"debug=0x144 -v keepsyms=1 serial=3"
mem_buf[0x70:0x70+len(orig_cmdline)] = orig_cmdline

struct.pack_into("<Q", mem_buf, 0x170, 0x00000028)        # bootFlags
struct.pack_into("<Q", mem_buf, 0x178, 0x40000000)        # memSizeActual

uc.mem_write(OLD_BOOT_ARGS, bytes(mem_buf))

# Initialize CPU registers
uc.reg_write(UC_ARM64_REG_X0, OLD_BOOT_ARGS)

print(f"Emulated CPU initialized: PC = {hex(ENTRY_PC)}, X0 = {hex(OLD_BOOT_ARGS)}")

# Trace every instruction executed by Unicorn CPU
trace_count = 0
def hook_code(uc, address, size, user_data):
    global trace_count
    trace_count += 1
    # Read instruction bytes
    code = uc.mem_read(address, size)
    # print(f"  [Cycle {trace_count:02d}] PC: {hex(address)}: {code.hex()}")

uc.hook_add(UC_HOOK_CODE, hook_code)

# Expected destination: physBase + 0xbf058 (start_cpu)
EXPECTED_DEST = PHYS_BASE + 0xbf058

# Put a simple breakpoint instruction at EXPECTED_DEST so emulator halts
# Place 'nop; ret' at destination
uc.mem_write(EXPECTED_DEST, bytes.fromhex("1f2003d5c0035fd6"))

print(f"Starting AArch64 CPU emulation until {hex(EXPECTED_DEST)}...")
try:
    uc.emu_start(ENTRY_PC, EXPECTED_DEST)
except Exception as e:
    print(f"Emulation halted: {e}")

final_pc = uc.reg_read(UC_ARM64_REG_PC)
final_x0 = uc.reg_read(UC_ARM64_REG_X0)
final_x1 = uc.reg_read(UC_ARM64_REG_X1)

print("\n=== UNICORN HARDWARE EMULATION RESULTS ===")
print(f"Total CPU instructions executed: {trace_count}")
print(f"Final CPU PC: {hex(final_pc)}")
print(f"Final CPU X0: {hex(final_x0)}")
print(f"Final CPU X1: {hex(final_x1)}")

assert final_pc == EXPECTED_DEST, f"FATAL: PC did not arrive at start_cpu! PC = {hex(final_pc)}"
print("[PASS 1 - UNICORN] Virtual AArch64 CPU arrived exactly at start_cpu (0xbf058)!")

EXPECTED_NEW_BA = PHYS_BASE + 0xbd800
assert final_x0 == EXPECTED_NEW_BA, f"FATAL: X0 does not point to new_boot_args! X0 = {hex(final_x0)}"
print("[PASS 2 - UNICORN] Register X0 holds new_boot_args physical address (0xbd800)!")

# Inspect memory populated by the real AArch64 CPU
new_ba_bytes = uc.mem_read(final_x0, 0x2e0)
rev, ver = struct.unpack_from("<HH", new_ba_bytes, 0x00)
print(f"Unicorn Emulated new_boot_args Revision: {rev}, Version: {ver}")
assert rev == 2 and ver == 2, "Revision/Version check failed!"
print("[PASS 3 - UNICORN] Revision=2, Version=2 confirmed!")

cmdline_read = bytes(new_ba_bytes[0x70:0x70+256]).split(b"\x00")[0]
print(f"Unicorn Emulated CommandLine: {cmdline_read.decode()}")
assert cmdline_read == orig_cmdline, "CommandLine corrupted!"
print("[PASS 4 - UNICORN] CommandLine string preserved identically!")

padding_read = bytes(new_ba_bytes[0x170:0x2d0])
assert all(b == 0 for b in padding_read), "Padding not zero-filled!"
print("[PASS 5 - UNICORN] 352-byte CommandLine expansion zero-filled!")

boot_flags = struct.unpack_from("<Q", new_ba_bytes, 0x2d0)[0]
print(f"Unicorn Emulated bootFlags at 0x2d0: {hex(boot_flags)}")
assert boot_flags == 0x28, "bootFlags mapping failed!"
print("[PASS 6 - UNICORN] bootFlags mapped to offset 0x2d0!")

mem_size_act = struct.unpack_from("<Q", new_ba_bytes, 0x2d8)[0]
print(f"Unicorn Emulated memSizeActual at 0x2d8: {hex(mem_size_act)}")
assert mem_size_act == 0x40000000, "memSizeActual mapping failed!"
print("[PASS 7 - UNICORN] memSizeActual mapped to offset 0x2d8!")

print("\n=== GENUINE ARM64 HARDWARE EMULATION VERIFIED 100% ===")
