from pathlib import Path
from decrypt_im4p import tlv, children

p = Path("/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-analysis/continuation-20261031/native-n61-12.5.8/Firmware/dfu/iBSS.n61.RELEASE.im4p")
data = p.read_bytes()
tag, value, end = tlv(data)
fields = children(value)
print(f"Total top-level fields: {len(fields)}")
for i, f in enumerate(fields):
    print(f"Field {i}: tag {hex(f[0])}, len {len(f[1])}")

if len(fields) > 4:
    kbag_seq = fields[4][1]
    # parse kbag sequence
    kbag_fields = children(kbag_seq)
    print(f"KBAG entries: {len(kbag_fields)}")
    for j, kf in enumerate(kbag_fields):
        k_items = children(kf[1])
        print(f"  Entry {j}: items {len(k_items)}")
        for it in k_items:
            print(f"    tag: {hex(it[0])}, data: {it[1].hex()}")
