"""Fetch only native N61 baseline ZIP members; never opens a USB device."""
from pathlib import Path
import argparse
import datetime
import hashlib
import io
import json
import plistlib
import re
import urllib.parse
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2] / 'local-artifacts/ios13'


class AppleRangeFile(io.RawIOBase):
    def __init__(self, url, size):
        if urllib.parse.urlparse(url).scheme != 'https' or urllib.parse.urlparse(url).hostname not in {'updates.cdn-apple.com', 'secure-appldnld.apple.com', 'appldnld.apple.com'}:
            raise ValueError('Expected an HTTPS Apple firmware URL')
        self.url, self.size, self.pos = url, size, 0
        self.requests = []
        self.total = 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        target = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        if target < 0 or target > self.size:
            raise ValueError('Invalid ZIP seek')
        self.pos = target
        return target

    def read(self, count=-1):
        count = self.size - self.pos if count < 0 else min(count, self.size - self.pos)
        if not count:
            return b''
        if count > 32 * 1024**2 or self.total + count > 64 * 1024**2 or len(self.requests) >= 60:
            raise ValueError('Partial-download budget exceeded')
        start, end = self.pos, self.pos + count - 1
        request = urllib.request.Request(self.url, headers={'Range': f'bytes={start}-{end}', 'Accept-Encoding': 'identity'})
        with urllib.request.urlopen(request, timeout=30) as response:
            content_range = response.headers.get('Content-Range', '')
            match = re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)', content_range)
            if response.status != 206 or not match or tuple(map(int, match.groups())) != (start, end, self.size):
                raise ValueError(f'Unexpected range response: HTTP {response.status}, {content_range}')
            data = response.read(count + 1)
            if len(data) != count:
                raise ValueError('Short or oversized range response')
        self.requests.append({'start': start, 'end': end, 'size': count})
        self.total += count
        self.pos += count
        return data


def main():
    global ROOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT)
    parser.add_argument('--metadata', type=Path, default=Path(__file__).resolve().parents[2] / 'docs/ios13/evidence/ios12-recovery-metadata.json')
    args = parser.parse_args()
    ROOT = args.output.resolve()
    ROOT.mkdir(parents=True, exist_ok=True)
    fw = json.loads(args.metadata.read_text())['firmwares']
    assert len(fw) == 1
    fw = fw[0]
    output = ROOT / 'native-n61-12.5.8'
    output.mkdir(exist_ok=True)
    remote = AppleRangeFile(fw['url'], fw['filesize'])
    record = {'source_url': fw['url'], 'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'members': [], 'device_operations': 0}
    try:
        with zipfile.ZipFile(remote) as archive:
            def extract(name):
                data = archive.read(name)  # zipfile verifies each member CRC32
                destination = output / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                record['members'].append({'zip_path': name, 'local_path': str(destination), 'bytes': len(data), 'zip_crc32': f'{archive.getinfo(name).CRC:08x}', 'sha256': hashlib.sha256(data).hexdigest()})
                print('Saved', name, len(data), 'bytes', flush=True)
                return data
            manifest = plistlib.loads(extract('BuildManifest.plist'))
            extract('Restore.plist')
            assert manifest['ProductVersion'] == '12.5.8' and manifest['ProductBuildVersion'] == '16H88'
            assert 'iPhone7,2' in manifest['SupportedProductTypes']
            identities = [i for i in manifest['BuildIdentities'] if i['Info']['DeviceClass'] == 'n61ap' and i['Info'].get('RestoreBehavior') == 'Erase']
            assert len(identities) == 1
            identity = identities[0]
            assert int(identity['ApChipID'], 16) == 0x7000 and int(identity['ApBoardID'], 16) == 6
            record['identity'] = {'ProductVersion': manifest['ProductVersion'], 'ProductBuildVersion': manifest['ProductBuildVersion'], 'SupportedProductTypes': manifest['SupportedProductTypes'], 'DeviceClass': identity['Info']['DeviceClass'], 'ApChipID': identity['ApChipID'], 'ApBoardID': identity['ApBoardID'], 'Variant': identity['Info']['Variant']}
            record['component_paths'] = {key: value.get('Info', {}).get('Path') for key, value in identity['Manifest'].items()}
            for component in ['iBSS', 'iBEC', 'DeviceTree', 'KernelCache']:
                extract(identity['Manifest'][component]['Info']['Path'])
            record['success'] = True
    except Exception as error:
        record['success'] = False
        record['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        record['http_ranges'] = remote.requests
        record['network_bytes'] = remote.total
        (ROOT / 'native-baseline-download.json').write_text(json.dumps(record, indent=2) + '\n')


if __name__ == '__main__':
    main()
