import hashlib
import os
import struct
import subprocess

KERNEL_IN = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/kernelcache-ipad13-decompressed"
TRAMPOLINE_BIN = "/mnt/c/Users/cmjnh/Desktop/ios13-port/gaster/tools/ios13/trampoline_v2.bin"
HOOK_BIN = "/mnt/c/Users/cmjnh/Desktop/ios13-port/gaster/tools/ios13/visual_hook_v2.bin"
BUNDLE_DIR = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/boot-bundle"
KERNEL_OUT = os.path.join(BUNDLE_DIR, "kernelcache.integrated_bundle")

ENTRY_OFF = 0xbd490
IOKIT_OFF = 0x5f5a20

print("=== INTEGRATING ALL-IN-ONE KERNELCACHE BUNDLE ===")

with open(TRAMPOLINE_BIN, "rb") as f:
    trampoline_data = f.read()

with open(HOOK_BIN, "rb") as f:
    hook_data = f.read()

print(f"Trampoline v2 size: {len(trampoline_data)} bytes")
print(f"Visual Hook v2 size: {len(hook_data)} bytes")

with open(KERNEL_IN, "rb") as f:
    kernel_data = bytearray(f.read())

orig_len = len(kernel_data)
orig_sha = hashlib.sha256(kernel_data).hexdigest()
print(f"Original Kernel Size: {orig_len} bytes")
print(f"Original Kernel SHA-256: {orig_sha}")

# 1. Verify Entry Region before patch: b 0xbf058 (140006f2) + nops
assert kernel_data[ENTRY_OFF:ENTRY_OFF+4] == bytes.fromhex("f2060014"), "Entry branch mismatch!"
# Verify that region from ENTRY_OFF+4 to ENTRY_OFF+len(trampoline_data) is all NOPs
nops_to_replace = kernel_data[ENTRY_OFF+4:ENTRY_OFF+len(trampoline_data)]
assert all(nops_to_replace[i:i+4] == bytes.fromhex("1f2003d5") for i in range(0, len(nops_to_replace), 4)), "Non-NOP code in trampoline target area!"
print("[PASS] Verified entry region contains b 0xbf058 followed by pure NOP padding.")

# 2. Verify _StartIOKit prologue before patch: sub sp, sp, #0x50; stp x24, x23, [sp, #16]
expected_prologue = bytes.fromhex("ff4301d1f85f01a9")
assert kernel_data[IOKIT_OFF:IOKIT_OFF+8] == expected_prologue, "_StartIOKit prologue mismatch!"
print("[PASS] Verified _StartIOKit prologue.")

# Apply Injections
kernel_data[ENTRY_OFF:ENTRY_OFF+len(trampoline_data)] = trampoline_data
kernel_data[IOKIT_OFF:IOKIT_OFF+len(hook_data)] = hook_data

# Save Integrated Kernel
with open(KERNEL_OUT, "wb") as f:
    f.write(kernel_data)

out_len = len(kernel_data)
out_sha = hashlib.sha256(kernel_data).hexdigest()
print(f"\nSaved Integrated Bundle to: {KERNEL_OUT}")
print(f"Integrated Kernel Size:    {out_len} bytes")
print(f"Integrated Kernel SHA-256: {out_sha}")
assert orig_len == out_len, "FATAL: Output size altered!"

# 3. Strict Byte-Diff Boundary Verification
with open(KERNEL_IN, "rb") as f:
    orig_bytes = f.read()

diff_indices = [i for i in range(orig_len) if kernel_data[i] != orig_bytes[i]]
print(f"\nTotal modified bytes across 34.6MB: {len(diff_indices)}")

region1 = [i for i in diff_indices if ENTRY_OFF <= i < ENTRY_OFF + len(trampoline_data)]
region2 = [i for i in diff_indices if IOKIT_OFF <= i < IOKIT_OFF + len(hook_data)]
outside = [i for i in diff_indices if i not in region1 and i not in region2]

print(f"  Region 1 (Trampoline @ {hex(ENTRY_OFF)}): {len(region1)} bytes modified")
print(f"  Region 2 (Visual Hook @ {hex(IOKIT_OFF)}): {len(region2)} bytes modified")
print(f"  Outside unexpected modifications: {len(outside)}")
assert len(outside) == 0, f"FATAL: Unintended byte modifications at: {[hex(x) for x in outside[:10]]}"
print("[PASS] All byte modifications strictly confined to verified injection targets!")

# 4. Disassemble Injected Regions Directly from the Output File
print("\n=== VERIFYING DISASSEMBLY OF INTEGRATED ENTRY POINT ===")
with open("/tmp/integrated_entry.bin", "wb") as f:
    f.write(kernel_data[ENTRY_OFF:ENTRY_OFF+len(trampoline_data)])
cmd_entry = ["aarch64-linux-gnu-objdump", "-b", "binary", "-m", "aarch64", f"--adjust-vma={hex(ENTRY_OFF)}", "-D", "/tmp/integrated_entry.bin"]
subprocess.run(cmd_entry)

print("\n=== VERIFYING DISASSEMBLY OF INTEGRATED VISUAL HOOK ===")
with open("/tmp/integrated_hook.bin", "wb") as f:
    f.write(kernel_data[IOKIT_OFF:IOKIT_OFF+len(hook_data)])
cmd_hook = ["aarch64-linux-gnu-objdump", "-b", "binary", "-m", "aarch64", "--adjust-vma=0xfffffff0075f9a20", "-D", "/tmp/integrated_hook.bin"]
subprocess.run(cmd_hook)

print("\n=== ALL INTEGRATION & VERIFICATION CHECKS COMPLETED ===")
