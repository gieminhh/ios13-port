orig_path = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/kernelcache-ipad13-decompressed"
patched_path = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/boot-bundle/kernelcache.visual_checkpoint"
hook_path = "/mnt/c/Users/cmjnh/Desktop/ios13-port/gaster/tools/ios13/visual_hook.bin"

with open(orig_path, "rb") as f:
    f.seek(0x5f5a20)
    orig_bytes = f.read(56)

with open(patched_path, "rb") as f:
    f.seek(0x5f5a20)
    patched_bytes = f.read(56)

with open(hook_path, "rb") as f:
    hook_bytes = f.read()

print(f"Hook length: {len(hook_bytes)}")
print(f"Patched slice == hook_bytes: {patched_bytes == hook_bytes}")

same_indices = []
for i in range(56):
    is_diff = orig_bytes[i] != hook_bytes[i]
    if not is_diff:
        same_indices.append((i, hex(orig_bytes[i])))
    print(f"[{i:02d}] Orig: {orig_bytes[i]:02x} | Hook: {hook_bytes[i]:02x} | Changed: {is_diff}")

print(f"Indices where orig byte equaled hook byte: {same_indices}")
