#!/usr/bin/env python3
"""Offline IM4P decryptor using recovered AES-256-CBC IV and Key."""
import argparse
import hashlib
import struct
import subprocess
import tempfile
from pathlib import Path

def tlv(data, offset=0):
    assert offset + 2 <= len(data)
    tag, length = data[offset:offset + 2]
    offset += 2
    if length & 128:
        count = length & 127
        assert 0 < count <= 8 and offset + count <= len(data)
        length = int.from_bytes(data[offset:offset + count], 'big')
        offset += count
    end = offset + length
    assert end <= len(data)
    return tag, data[offset:end], end

def children(data):
    result, offset = [], 0
    while offset < len(data):
        tag, value, offset = tlv(data, offset)
        result.append((tag, value))
    return result

def extract_im4p_payload(im4p_path: Path):
    data = im4p_path.read_bytes()
    tag, value, end = tlv(data)
    assert tag == 0x30 and end == len(data)
    fields = children(value)
    assert fields[0] == (0x16, b'IM4P') and fields[3][0] == 4
    comp_type = fields[1][1].decode('latin1', errors='replace')
    comp_desc = fields[2][1].decode('latin1', errors='replace')
    payload = fields[3][1]
    return comp_type, comp_desc, payload

def decrypt_payload(payload: bytes, iv_hex: str, key_hex: str) -> bytes:
    assert len(iv_hex) == 32, f"IV must be 32 hex chars (16 bytes), got {len(iv_hex)}"
    assert len(key_hex) == 64, f"Key must be 64 hex chars (32 bytes), got {len(key_hex)}"
    with tempfile.NamedTemporaryFile('wb', delete=True) as fin, \
         tempfile.NamedTemporaryFile('rb', delete=True) as fout:
        fin.write(payload)
        fin.flush()
        cmd = [
            'openssl', 'enc', '-d', '-aes-256-cbc',
            '-K', key_hex, '-iv', iv_hex,
            '-nopad', '-in', fin.name, '-out', fout.name
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"OpenSSL failed: {res.stderr}")
        return fout.read()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--im4p', type=Path, required=True, help="Input .im4p file")
    parser.add_argument('--iv', type=str, required=True, help="16-byte IV in hex (32 characters)")
    parser.add_argument('--key', type=str, required=True, help="32-byte Key in hex (64 characters)")
    parser.add_argument('--out', type=Path, required=True, help="Output decrypted binary path")
    args = parser.parse_args()

    comp_type, comp_desc, payload = extract_im4p_payload(args.im4p)
    print(f"IM4P Component: {comp_type} ({comp_desc}), encrypted size: {len(payload)} bytes")

    decrypted = decrypt_payload(payload, args.iv, args.key)
    args.out.write_bytes(decrypted)
    print(f"Successfully decrypted to {args.out} ({len(decrypted)} bytes)")
    print(f"SHA-256: {hashlib.sha256(decrypted).hexdigest()}")

    # Inspect headers
    if b'iBoot' in decrypted:
        for s in decrypted.split(b'\x00'):
            if b'iBoot-' in s:
                print(f"Found iBoot build banner: {s.decode(errors='replace')}")
                break

if __name__ == '__main__':
    main()
