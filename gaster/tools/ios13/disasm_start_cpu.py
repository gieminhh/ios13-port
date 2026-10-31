import subprocess

with open("/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/kernelcache-ipad13-decompressed", "rb") as f:
    f.seek(0xbf058)
    code = f.read(512)

with open("/tmp/start_cpu.bin", "wb") as f:
    f.write(code)

subprocess.run(["aarch64-linux-gnu-objdump", "-b", "binary", "-m", "aarch64", "--adjust-vma=0xfffffff0070c3058", "-D", "/tmp/start_cpu.bin"])
