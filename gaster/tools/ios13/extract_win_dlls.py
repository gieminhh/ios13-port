import os
import zipfile

out_dir = "/mnt/c/Users/cmjnh/Desktop/ios13-port/gaster/windows"
os.makedirs(out_dir, exist_ok=True)

with zipfile.ZipFile("/tmp/gaster-win.zip") as z:
    for name in ["gaster-Win/libusb-1.0.dll", "gaster-Win/libcrypto-1_1-x64.dll"]:
        data = z.read(name)
        base = os.path.basename(name)
        target = os.path.join(out_dir, base)
        with open(target, "wb") as f:
            f.write(data)
        print(f"Extracted {base} ({len(data)} bytes) to {target}")
