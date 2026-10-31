with open("/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-analysis/continuation-20261031/native-n61-12.5.8/Firmware/dfu/iBSS.n61.RELEASE.im4p", "rb") as f:
    data = f.read()

# An IM4P file is an ASN.1 SEQUENCE:
# [0] 'IM4P'
# [1] type ('ibss')
# [2] description
# [3] payload (encrypted)
# [4] kbag sequence: SEQUENCE of KBAGs (IV 16B + Key 32B = 48B each)
# Let's search for KBAG pattern (48 bytes preceded by tag 0x04)
# KBAG headers in Apple IM4P:
# Type-1 KBAG is preceded by integer 0x01
idx = data.find(b"KBAG")
if idx != -1:
    print(f"Found KBAG marker at offset {hex(idx)}")
    kbag_chunk = data[idx:idx+128]
    print(f"Hex: {kbag_chunk.hex()}")

# Or search for 48-byte octet string
import re
# Look for 48-byte OCTET STRING: 04 30 <48 bytes>
matches = [m.start() for m in re.finditer(b"\x04\x30", data)]
for m in matches:
    kbag_bytes = data[m+2:m+2+48]
    iv = kbag_bytes[:16].hex()
    key = kbag_bytes[16:].hex()
    print(f"Found candidate KBAG at {hex(m)}: {kbag_bytes.hex()}")
    print(f"  IV:  {iv}")
    print(f"  Key: {key}")
