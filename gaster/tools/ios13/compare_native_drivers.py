"""Compare native iOS12 kext metadata with the existing iOS13 inventory."""
from pathlib import Path
import argparse
import base64
import json
import re
import struct
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2] / 'local-artifacts/ios13'


def main():
    global ROOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=ROOT)
    parser.add_argument('--ios13-kexts', type=Path, required=True, help='Existing iOS13 prelink kext inventory JSON')
    args = parser.parse_args()
    ROOT = args.workspace.resolve()
    data = (ROOT / 'native-n61-12.5.8/KernelCache.decompressed').read_bytes()
    offset, segments, xml = 32, [], None
    for _ in range(struct.unpack_from('<I', data, 16)[0]):
        command, size = struct.unpack_from('<II', data, offset)
        assert size >= 8 and offset + size <= len(data)
        if command == 0x19:
            name = data[offset + 8:offset + 24].split(b'\0')[0].decode()
            addr, vmsize, fileoff, filesize = struct.unpack_from('<QQQQ', data, offset + 24)
            segments.append(dict(name=name, vmaddr=addr, vmsize=vmsize, fileoff=fileoff, filesize=filesize))
            if name == '__PRELINK_INFO':
                for index in range(struct.unpack_from('<I', data, offset + 64)[0]):
                    section = offset + 72 + index * 80
                    if data[section:section + 16].split(b'\0')[0] == b'__info':
                        _, length, start = struct.unpack_from('<QQI', data, section + 32)
                        xml = data[start:start + length].rstrip(b'\0')
        offset += size
    assert xml is not None
    refs = {}

    def decode(node):
        if 'IDREF' in node.attrib:
            return refs[node.attrib['IDREF']]
        text = node.text or ''
        if node.tag == 'dict':
            children = list(node)
            assert len(children) % 2 == 0
            value = {}
            for index in range(0, len(children), 2):
                assert children[index].tag == 'key'
                key = decode(children[index])
                assert key not in value
                value[key] = decode(children[index + 1])
        elif node.tag == 'array': value = [decode(child) for child in node]
        elif node.tag in {'key', 'string'}: value = text
        elif node.tag == 'integer': value = int(text, 16 if text.lower().startswith('0x') else 10)
        elif node.tag == 'data': value = base64.b64decode(text).hex()
        elif node.tag in {'true', 'false'}: value = node.tag == 'true'
        else: raise ValueError('Unexpected metadata tag: ' + node.tag)
        if 'ID' in node.attrib: refs[node.attrib['ID']] = value
        return value

    k12 = decode(ET.fromstring(xml))['_PrelinkInfoDictionary']
    k13 = json.loads(args.ios13_kexts.read_text())
    (ROOT / 'kernel12-kexts.json').write_text(json.dumps(k12, indent=2) + '\n')
    m12 = {k['CFBundleIdentifier']: k for k in k12}
    m13 = {k['CFBundleIdentifier']: k for k in k13}
    rows = []
    for name, kext in m12.items():
        if re.search(r'D2186|Pinot|Chestnut|MultitouchSPIN61|CLCD|T7000|AppleANS|Storage|BCMWLAN|MobileFrame|AppleSPU|AppleSEP', name, re.I):
            current = m13.get(name)
            rows.append({'id': name, 'native12_version': kext.get('CFBundleVersion'), 'present_in_13': current is not None, 'ios13_version': current.get('CFBundleVersion') if current else None, 'native12_dependencies': kext.get('OSBundleLibraries'), 'native12_executable_size': kext.get('_PrelinkExecutableSize')})
    summary = {'native12_kext_count': len(k12), 'ios13_kext_count': len(k13), 'only_native12': sorted(set(m12) - set(m13)), 'only_ios13': sorted(set(m13) - set(m12)), 'critical_components': rows, 'native12_segments': segments, 'limitation': 'Metadata comparison establishes presence and declared versions, not ABI compatibility or hardware behavior.'}
    (ROOT / 'native12-vs-ios13-drivers.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('Native12 kexts:', len(k12), 'iOS13:', len(k13))
    for row in rows:
        print(row['id'], row['native12_version'], '=>', row['ios13_version'] if row['present_in_13'] else 'ABSENT')
    print('Only native12:', summary['only_native12'])


if __name__ == '__main__':
    main()
