import hashlib
import struct
import sys

ORIG_PATH = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/kernelcache-ipad13-decompressed"
PATCHED_PATH = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/boot-bundle/kernelcache.visual_checkpoint"
START_IOKIT_OFF = 0x5f5a20
HOOK_LEN = 48

print("=== 1. HASH & FILE SIZE INTEGRITY ===")
with open(ORIG_PATH, "rb") as f:
    orig_data = f.read()
with open(PATCHED_PATH, "rb") as f:
    patched_data = f.read()

print(f"Original size: {len(orig_data)} bytes")
print(f"Patched size:  {len(patched_data)} bytes")
assert len(orig_data) == len(patched_data), "FATAL: File size altered!"

orig_sha = hashlib.sha256(orig_data).hexdigest()
patched_sha = hashlib.sha256(patched_data).hexdigest()
print(f"Original SHA-256: {orig_sha}")
print(f"Patched  SHA-256: {patched_sha}")
assert orig_sha != patched_sha, "FATAL: Patch did not change file hash!"

print("\n=== 2. STRICT BYTE DIFF BOUNDARY AUDIT ===")
diffs = [i for i in range(len(orig_data)) if orig_data[i] != patched_data[i]]
print(f"Total modified bytes: {len(diffs)}")

min_diff = min(diffs)
max_diff = max(diffs)
print(f"First modified byte offset: {hex(min_diff)}")
print(f"Last  modified byte offset: {hex(max_diff)}")

assert min_diff >= START_IOKIT_OFF, f"Diff below hook start: {hex(min_diff)} < {hex(START_IOKIT_OFF)}"
assert max_diff < START_IOKIT_OFF + HOOK_LEN, f"Diff above hook end: {hex(max_diff)} >= {hex(START_IOKIT_OFF + HOOK_LEN)}"
print(f"[PASS] All {len(diffs)} byte changes are strictly confined to [0x5f5a20 .. 0x5f5a57].")

print("\n=== 3. MACH-O STRUCTURAL VALIDATION ===")
magic, cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags, reserved = struct.unpack("<IIIIIIII", patched_data[:32])
assert magic == 0xfeedfacf, f"Invalid Mach-O 64 magic: {hex(magic)}"
assert cputype == 0x100000c, f"Invalid CPUType (expected ARM64): {hex(cputype)}"
print(f"[PASS] Mach-O 64-bit Header intact: ncmds = {ncmds}, sizeofcmds = {sizeofcmds}")

offset = 32
for i in range(ncmds):
    cmd, cmdsize = struct.unpack("<II", patched_data[offset:offset+8])
    cmd_data = patched_data[offset+8:offset+cmdsize]
    if cmd == 0x19: # LC_SEGMENT_64
        segname = cmd_data[:16].rstrip(b"\x00").decode("latin1", errors="ignore")
        vmaddr, vmsize, fileoff, filesize = struct.unpack("<QQQQ", cmd_data[16:48])
        assert fileoff + filesize <= len(patched_data), f"Segment {segname} exceeds file boundary!"
    elif cmd == 0x5: # LC_UNIXTHREAD
        pc = struct.unpack("<Q", cmd_data[264:272])[0]
        assert pc == 0xfffffff0070c1490, f"Entry PC corrupted: {hex(pc)}"
    offset += cmdsize

print("[PASS] All 22 load commands validated without structural corruption.")
print("[ALL AUDIT CHECKS PASSED]")
