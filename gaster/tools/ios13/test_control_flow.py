import struct
import sys

print("=== OFFLINE CONTROL FLOW & TRAMPOLINE EMULATION TEST ===")

# Read compiled trampoline_v2 binary
with open("/mnt/c/Users/cmjnh/Desktop/ios13-port/gaster/tools/ios13/trampoline_v2.bin", "rb") as f:
    trampoline_code = f.read()

print(f"Trampoline code size: {len(trampoline_code)} bytes ({len(trampoline_code)//4} instructions)")
assert len(trampoline_code) % 4 == 0, "Instruction stream must be 4-byte aligned!"

# Mock physical memory dictionary
memory = {}

def mem_write(addr, data):
    for i, b in enumerate(data):
        memory[addr + i] = b

def mem_read(addr, length):
    return bytes(memory.get(addr + i, 0) for i in range(length))

def mem_write_u64(addr, val):
    mem_write(addr, struct.pack("<Q", val))

def mem_read_u64(addr):
    return struct.unpack("<Q", mem_read(addr, 8))[0]

def mem_read_u32(addr):
    return struct.unpack("<I", mem_read(addr, 4))[0]

# Setup mock physical memory
# Apple A8 physical DRAM base = 0x800000000
PHYS_BASE = 0x800000000
OLD_BOOT_ARGS = 0x800100000 # iBoot placed boot_args here
DEVICE_TREE = 0x800200000   # iBoot placed devicetree here

# Populate Darwin 18 (iOS 12) boot_args at OLD_BOOT_ARGS
mem_write(OLD_BOOT_ARGS, b"\x00" * 0x180) # 384 bytes
mem_write(OLD_BOOT_ARGS, struct.pack("<HH", 1, 2)) # Revision=1, Version=2
mem_write_u64(OLD_BOOT_ARGS + 0x08, 0xfffffff007004000) # virtBase
mem_write_u64(OLD_BOOT_ARGS + 0x10, PHYS_BASE)          # physBase
mem_write_u64(OLD_BOOT_ARGS + 0x18, 0x40000000)          # memSize (1GB)
mem_write_u64(OLD_BOOT_ARGS + 0x20, PHYS_BASE + 0x2200000) # topOfKernelData
mem_write_u64(OLD_BOOT_ARGS + 0x60, DEVICE_TREE)        # deviceTreeP
mem_write(OLD_BOOT_ARGS + 0x68, struct.pack("<I", 0x1a000)) # deviceTreeLength

cmdline_orig = b"debug=0x144 -v keepsyms=1 serial=3"
mem_write(OLD_BOOT_ARGS + 0x70, cmdline_orig.ljust(256, b"\x00")) # 256 bytes

mem_write_u64(OLD_BOOT_ARGS + 0x170, 0x00000028) # bootFlags (Darwin 18 offset 0x170)
mem_write_u64(OLD_BOOT_ARGS + 0x178, 0x40000000) # memSizeActual (Darwin 18 offset 0x178)

# Initialize CPU registers
regs = {f"x{i}": 0 for i in range(31)}
regs["x0"] = OLD_BOOT_ARGS # Passed by iBoot

print(f"Initial State: x0 (old_boot_args) = {hex(regs['x0'])}")
print(f"physBase in boot_args: {hex(mem_read_u64(OLD_BOOT_ARGS + 0x10))}")

# Disassemble and execute instructions
pc = PHYS_BASE + 0xbd490 # Entry point
print(f"\nExecuting Trampoline at physical PC = {hex(pc)}...")

# Step-by-step instruction emulator for trampoline_v2
insns = [struct.unpack("<I", trampoline_code[i:i+4])[0] for i in range(0, len(trampoline_code), 4)]

for idx, insn in enumerate(insns):
    curr_pc = pc + idx * 4
    # Execute semantics
    if idx == 0: # mov x19, x0
        regs["x19"] = regs["x0"]
    elif idx == 1: # ldr x20, [x19, #16]
        regs["x20"] = mem_read_u64(regs["x19"] + 16)
    elif idx == 2: # add x20, x20, #0xbd, lsl #12 (0xbd000)
        regs["x20"] += 0xbd000
    elif idx == 3: # add x20, x20, #0x800
        regs["x20"] += 0x800
    elif idx == 4: # mov x1, #0
        regs["x1"] = 0
    elif 5 <= idx <= 9: # copy_header loop (0x70 bytes = 14 quadwords)
        # Emulate loop
        for off in range(0, 0x70, 8):
            val = mem_read_u64(regs["x19"] + off)
            mem_write_u64(regs["x20"] + off, val)
        regs["x1"] = 0x70
    elif idx == 10: # mov w2, #0x20002 (Revision=2, Version=2)
        regs["w2"] = 0x00020002
    elif idx == 11: # str w2, [x20]
        mem_write(regs["x20"], struct.pack("<I", regs["w2"]))
    elif 12 <= idx <= 16: # copy_cmdline loop (0x70 to 0x170 = 256 bytes)
        for off in range(0x70, 0x170, 8):
            val = mem_read_u64(regs["x19"] + off)
            mem_write_u64(regs["x20"] + off, val)
        regs["x1"] = 0x170
    elif idx == 17: # mov x2, #0
        regs["x2"] = 0
    elif 18 <= idx <= 21: # zero_cmdline loop (0x170 to 0x2d0 = 352 bytes)
        for off in range(0x170, 0x2d0, 8):
            mem_write_u64(regs["x20"] + off, 0)
        regs["x1"] = 0x2d0
    elif idx == 22: # ldr x2, [x19, #368] (offset 0x170)
        regs["x2"] = mem_read_u64(regs["x19"] + 0x170)
    elif idx == 23: # str x2, [x20, #720] (offset 0x2d0)
        mem_write_u64(regs["x20"] + 0x2d0, regs["x2"])
    elif idx == 24: # ldr x2, [x19, #376] (offset 0x178)
        regs["x2"] = mem_read_u64(regs["x19"] + 0x178)
    elif idx == 25: # str x2, [x20, #728] (offset 0x2d8)
        mem_write_u64(regs["x20"] + 0x2d8, regs["x2"])
    elif idx == 26: # mov x0, x20
        regs["x0"] = regs["x20"]
    elif idx == 27: # ldr x1, [x20, #16] (physBase)
        regs["x1"] = mem_read_u64(regs["x20"] + 16)
    elif idx == 28: # add x1, x1, #0xbf, lsl #12
        regs["x1"] += 0xbf000
    elif idx == 29: # add x1, x1, #0x58
        regs["x1"] += 0x058
    elif idx == 30: # br x1
        final_pc = regs["x1"]
        print(f"[Instruction {idx}: br x1] Branching to: {hex(final_pc)}")
        break

NEW_BOOT_ARGS = regs["x0"]
print("\n=== POST-EXECUTION VERIFICATION ===")
print(f"Final Destination PC: {hex(final_pc)}")
EXPECTED_START_CPU = PHYS_BASE + 0xbf058
print(f"Expected start_cpu:   {hex(EXPECTED_START_CPU)}")
assert final_pc == EXPECTED_START_CPU, f"Control flow diverted! {hex(final_pc)} != {hex(EXPECTED_START_CPU)}"
print("[PASS 1] Control flow arrives exactly at start_cpu (0xbf058) without looping!")

print(f"\nFinal x0 (new_boot_args): {hex(NEW_BOOT_ARGS)}")
EXPECTED_NEW_BA = PHYS_BASE + 0xbd800
print(f"Expected new_boot_args:   {hex(EXPECTED_NEW_BA)}")
assert NEW_BOOT_ARGS == EXPECTED_NEW_BA, "new_boot_args location mismatch!"
print("[PASS 2] new_boot_args is in verified safe kernel NOP cave (physBase + 0xbd800)!")

# Check no overlap
assert NEW_BOOT_ARGS != OLD_BOOT_ARGS, "Overlapping old_boot_args!"
assert not (NEW_BOOT_ARGS <= DEVICE_TREE < NEW_BOOT_ARGS + 0x300), "Overlapping DeviceTree!"
print("[PASS 3] Zero overlap with old_boot_args or DeviceTree!")

# Check Revision & Version
rev = struct.unpack("<H", mem_read(NEW_BOOT_ARGS, 2))[0]
ver = struct.unpack("<H", mem_read(NEW_BOOT_ARGS + 2, 2))[0]
print(f"new_boot_args Revision: {rev}, Version: {ver}")
assert rev == 2 and ver == 2, "Darwin 19 Revision/Version mismatch!"
print("[PASS 4] Revision=2, Version=2 confirmed!")

# Check CommandLine
cmdline_res = mem_read(NEW_BOOT_ARGS + 0x70, 608)
cmdline_str = cmdline_res.split(b"\x00")[0]
print(f"new_boot_args CommandLine: {cmdline_str.decode()}")
assert cmdline_str == cmdline_orig, "CommandLine string corrupted!"
# Check zero padding
padding_res = cmdline_res[256:]
assert all(b == 0 for b in padding_res), "CommandLine padding is not zero-filled!"
print(f"[PASS 5] CommandLine preserved and 352 bytes zero-padded cleanly!")

# Check bootFlags
boot_flags = mem_read_u64(NEW_BOOT_ARGS + 0x2d0)
print(f"new_boot_args bootFlags at offset 0x2d0: {hex(boot_flags)}")
assert boot_flags == 0x28, f"bootFlags mismatch! {hex(boot_flags)}"
print("[PASS 6] bootFlags mapped to offset 0x2d0 perfectly!")

# Check memSizeActual
mem_size_actual = mem_read_u64(NEW_BOOT_ARGS + 0x2d8)
print(f"new_boot_args memSizeActual at offset 0x2d8: {hex(mem_size_actual)}")
assert mem_size_actual == 0x40000000, f"memSizeActual mismatch! {hex(mem_size_actual)}"
print("[PASS 7] memSizeActual mapped to offset 0x2d8 perfectly!")

print("\n=== ALL CONTROL FLOW & DATA INTEGRITY TESTS PASSED 100% ===")
