with open("/mnt/c/Users/cmjnh/Desktop/ios13-port/gaster/gaster.c") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "status" in line or "decrypt_kbag_pwned" in line:
        print(f"{i+1}: {line.strip()}")
