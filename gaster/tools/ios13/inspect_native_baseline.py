"""Inspect downloaded IM4P baseline and extract encrypted KBAG test inputs offline."""
from pathlib import Path
import argparse
import hashlib
import json
import plistlib
import struct
import zlib

ROOT = Path(__file__).resolve().parents[2] / 'local-artifacts/ios13'


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


def decompress_lzss(data, expected):
    ring = bytearray(b' ' * 4096)
    cursor, flags, offset = 4096 - 18, 0, 0
    output = bytearray()
    while len(output) < expected:
        flags >>= 1
        if not flags & 256:
            flags = data[offset] | 0xff00
            offset += 1
        if flags & 1:
            b = data[offset]
            offset += 1
            output.append(b)
            ring[cursor] = b
            cursor = (cursor + 1) & 4095
        else:
            i, j = data[offset:offset + 2]
            offset += 2
            i |= (j & 0xf0) << 4
            for k in range((j & 15) + 3):
                assert len(output) < expected
                b = ring[(i + k) & 4095]
                output.append(b)
                ring[cursor] = b
                cursor = (cursor + 1) & 4095
    return bytes(output)


def main():
    global ROOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=ROOT)
    ROOT = parser.parse_args().workspace.resolve()
    download = json.loads((ROOT / 'native-baseline-download.json').read_text())
    assert download['success']
    native = ROOT / 'native-n61-12.5.8'
    manifest = plistlib.loads((native / 'BuildManifest.plist').read_bytes())
    identity = next(i for i in manifest['BuildIdentities'] if i['Info']['DeviceClass'] == 'n61ap' and i['Info']['RestoreBehavior'] == 'Erase')
    result = {'components': {}}
    for component in ['iBSS', 'iBEC', 'DeviceTree', 'KernelCache']:
        entry = identity['Manifest'][component]
        path = native / entry['Info']['Path']
        data = path.read_bytes()
        tag, value, end = tlv(data)
        assert tag == 0x30 and end == len(data)
        fields = children(value)
        assert fields[0] == (0x16, b'IM4P') and fields[3][0] == 4
        payload = fields[3][1]
        summary = {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'manifest_digest_bytes': len(entry.get('Digest', b'')), 'type': fields[1][1].decode(), 'description': fields[2][1].decode(), 'payload_bytes': len(payload), 'payload_first16_hex': payload[:16].hex(), 'kbag_present': len(fields) > 4 and fields[4][0] == 4}
        if entry.get('Digest'):
            digest = hashlib.sha1(data).digest() if len(entry['Digest']) == 20 else hashlib.sha384(data).digest() if len(entry['Digest']) == 48 else None
            summary['whole_im4p_manifest_digest_matches'] = digest == entry['Digest']
        if summary['kbag_present']:
            tag, bags, end = tlv(fields[4][1])
            assert tag == 0x30 and end == len(fields[4][1])
            bags = children(bags)
            summary['kbag_types'] = []
            for tag, bag in bags:
                assert tag == 0x30
                b = children(bag)
                assert len(b) == 3 and b[0][0] == 2 and b[1][0] == b[2][0] == 4
                kind = int.from_bytes(b[0][1], 'big')
                summary['kbag_types'].append(kind)
                if kind == 1:
                    encrypted = b[1][1] + b[2][1]
                    assert len(b[1][1]) == 16 and len(b[2][1]) == 32
                    dest = ROOT / f'{component.lower()}-type1-encrypted-kbag.hex'
                    dest.write_text(encrypted.hex() + '\n')
                    dest.chmod(0o600)
                    summary['encrypted_kbag_file'] = str(dest)
            summary['plaintext_available'] = False
        else:
            dest = native / (component + '.payload')
            dest.write_bytes(payload)
            summary['plaintext_payload_file'] = str(dest)
            summary['plaintext_available'] = True
            if payload.startswith(b'complzss'):
                checksum, uncomp, comp = struct.unpack_from('>III', payload, 8)
                assert comp <= len(payload) - 384 and uncomp < 128 * 1024**2
                raw = decompress_lzss(payload[384:384 + comp], uncomp)
                assert zlib.adler32(raw) & 0xffffffff == checksum
                dest = native / (component + '.decompressed')
                dest.write_bytes(raw)
                summary['decompressed_file'] = str(dest)
                summary['decompressed_bytes'] = len(raw)
                summary['decompressed_sha256'] = hashlib.sha256(raw).hexdigest()
                summary['adler32_matches'] = True
                summary['mach_o_arm64'] = raw[:4] == b'\xcf\xfa\xed\xfe' and struct.unpack_from('<I', raw, 4)[0] == 0x100000c
                strings = [s for s in raw.split(b'\0') if b'Darwin Kernel Version' in s]
                summary['darwin_versions'] = [s[s.index(b'Darwin Kernel Version'):].decode(errors='replace') for s in strings]
        result['components'][component] = summary
        print(component, json.dumps(summary), flush=True)
    (ROOT / 'native-baseline-inspection.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
