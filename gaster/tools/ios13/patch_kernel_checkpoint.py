import hashlib
import os
import sys

KERNEL_IN = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/kernelcache-ipad13-decompressed"
HOOK_BIN = "/mnt/c/Users/cmjnh/Desktop/ios13-port/gaster/tools/ios13/visual_hook_v2.bin"
BUNDLE_DIR = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/boot-bundle"
KERNEL_OUT = os.path.join(BUNDLE_DIR, "kernelcache.visual_checkpoint")

START_IOKIT_OFF = 0x5f5a20

os.makedirs(BUNDLE_DIR, exist_ok=True)

with open(HOOK_BIN, "rb") as f:
    hook_data = f.read()

print(f"Hook data size: {len(hook_data)} bytes")

with open(KERNEL_IN, "rb") as f:
    kernel_data = bytearray(f.read())

print(f"Original kernel size: {len(kernel_data)} bytes")
orig_sha = hashlib.sha256(kernel_data).hexdigest()
print(f"Original kernel SHA-256: {orig_sha}")

# Verify prologue at offset 0x5f5a20
orig_prologue = kernel_data[START_IOKIT_OFF:START_IOKIT_OFF+8]
expected_prologue = bytes.fromhex("ff4301d1f85f01a9") # sub sp, sp, #0x50; stp x24, x23, [sp, #16]
assert orig_prologue == expected_prologue, f"Prologue mismatch at {hex(START_IOKIT_OFF)}: {orig_prologue.hex()} != {expected_prologue.hex()}"

# Apply hook
kernel_data[START_IOKIT_OFF:START_IOKIT_OFF+len(hook_data)] = hook_data

with open(KERNEL_OUT, "wb") as f:
    f.write(kernel_data)

patched_sha = hashlib.sha256(kernel_data).hexdigest()
print(f"Patched kernel saved to: {KERNEL_OUT}")
print(f"Patched kernel SHA-256: {patched_sha}")

# Verify exact diff
diff_count = sum(1 for a, b in zip(open(KERNEL_IN, "rb").read(), kernel_data) if a != b)
print(f"Total modified bytes: {diff_count} (expected: <= {len(hook_data)})")
print("[SUCCESS] Kernel early visual checkpoint hook applied cleanly.")
