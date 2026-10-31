import subprocess

kc = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/kernelcache-ipad13-decompressed"
with open(kc, "rb") as f:
    f.seek(0x5f5a20)
    data = f.read(128)

with open("/tmp/start_iokit.bin", "wb") as f:
    f.write(data)

cmd = ["aarch64-linux-gnu-objdump", "-b", "binary", "-m", "aarch64", "-D", "/tmp/start_iokit.bin"]
subprocess.run(cmd)
