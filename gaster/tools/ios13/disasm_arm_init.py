import subprocess

OFFSET = 0x1eaf8c

with open("/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/kernelcache-ipad13-decompressed", "rb") as f:
    f.seek(OFFSET)
    code = f.read(256)

with open("/tmp/arm_init.bin", "wb") as f:
    f.write(code)

subprocess.run(["aarch64-linux-gnu-objdump", "-b", "binary", "-m", "aarch64", f"--adjust-vma=0xfffffff0071eef8c", "-D", "/tmp/arm_init.bin"])
