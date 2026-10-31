import zipfile

with zipfile.ZipFile("/tmp/gaster-win.zip") as z:
    for info in z.infolist():
        print(f"{info.filename}: {info.file_size} bytes")
