import subprocess

kc = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/kernelcache-ipad13-decompressed"
with open(kc, "rb") as f:
    f.seek(0xbd480)
    data = f.read(128)

with open("/tmp/entry_region.bin", "wb") as f:
    f.write(data)

print("=== Disassembly of Entry Region (offset 0xbd480 .. 0xbd500) ===")
cmd = ["aarch64-linux-gnu-objdump", "-b", "binary", "-m", "aarch64", "--adjust-vma=0xbd480", "-D", "/tmp/entry_region.bin"]
subprocess.run(cmd)

with open(kc, "rb") as f:
    f.seek(0xbd494)
    data = f.read(4096)

nop_count = 0
for i in range(0, len(data), 4):
    if data[i:i+4] == bytes.fromhex("1f2003d5"):
        nop_count += 1
    else:
        print(f"Non-nop encountered at offset {hex(0xbd494 + i)}: {data[i:i+4].hex()}")
        break
print(f"Consecutive NOP instructions: {nop_count} ({nop_count * 4} bytes)")
