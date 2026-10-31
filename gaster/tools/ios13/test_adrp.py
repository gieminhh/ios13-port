import subprocess

with open("/tmp/test_adrp.bin", "wb") as f:
    f.write(bytes.fromhex("c8d5ffb0"))

cmd = ["aarch64-linux-gnu-objdump", "-b", "binary", "-m", "aarch64", "--adjust-vma=0xfffffff0075f9a20", "-D", "/tmp/test_adrp.bin"]
subprocess.run(cmd)
