import sys
sys.path.append("/mnt/c/Users/cmjnh/Desktop/ios13-port/gaster/tools/ios13")
import decrypt_im4p

for path in [
    "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-analysis/continuation-20261031/native-n61-12.5.8/Firmware/dfu/iBSS.n61.RELEASE.im4p",
    "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-analysis/continuation-20261031/native-n61-12.5.8/Firmware/dfu/iBEC.n61.RELEASE.im4p"
]:
    with open(path, "rb") as f:
        data = f.read()
    parsed = decrypt_im4p.parse_im4p(data)
    name = path.split("/")[-1]
    print(f"File: {name}")
    print(f"  Type: {parsed.type_str}")
    print(f"  Description: {parsed.desc}")
    print(f"  Has KBAG: {parsed.has_kbag}")
    if parsed.has_kbag:
        print(f"  KBAG IV: {parsed.kbag_iv.hex()}")
        print(f"  KBAG Key: {parsed.kbag_key.hex()}")
