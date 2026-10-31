import subprocess

KERNEL = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/kernelcache-ipad13-decompressed"

with open(KERNEL, "rb") as f:
    f.seek(0xbf058)
    code = f.read(128)

with open("/tmp/inspect_code.bin", "wb") as f:
    f.write(code)

subprocess.run(["aarch64-linux-gnu-objdump", "-b", "binary", "-m", "aarch64", "--adjust-vma=0xbf058", "-D", "/tmp/inspect_code.bin"])
