import subprocess

kc = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/kernelcache-ipad13-decompressed"
# vmaddr 0xfffffff007644474 -> fileoff: 0x640474 in __TEXT_EXEC (vmaddr 0xfffffff0070b4000, off 0xb0000)
# off = 0x7644474 - 0x70b4000 + 0xb0000 = 0x640474
fileoff = 0x640474
with open(kc, "rb") as f:
    f.seek(fileoff)
    data = f.read(64)

with open("/tmp/console_info.bin", "wb") as f:
    f.write(data)

cmd = ["aarch64-linux-gnu-objdump", "-b", "binary", "-m", "aarch64", "-D", "/tmp/console_info.bin"]
subprocess.run(cmd)
