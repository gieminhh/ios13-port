with open("/mnt/c/Users/cmjnh/Desktop/ios13-port/gaster/gaster.c") as f:
    for i, line in enumerate(f):
        if "#include" in line or "AES" in line or "EVP" in line or "SHA" in line:
            print(f"{i+1}: {line.strip()}")
