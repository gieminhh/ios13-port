import zipfile

with zipfile.ZipFile("/tmp/gaster-win.zip") as z:
    with open("/tmp/vvaske_gaster.exe", "wb") as f:
        f.write(z.read("gaster-Win/gaster.exe"))
print("Extracted vvaske_gaster.exe")
