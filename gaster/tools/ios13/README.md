# Offline baseline tools

These scripts use Python's standard library and never open USB devices. Default
outputs go under ignored `local-artifacts/ios13/`. Apple firmware bytes, decoded
payloads and encrypted KBAG files must stay local.

```sh
python3 tools/ios13/fetch_native_baseline.py
python3 tools/ios13/inspect_native_baseline.py
python3 tools/ios13/compare_native_drivers.py --ios13-kexts /path/to/kernel13-kexts.json
```

`fetch_native_baseline.py` uses the recorded iPhone7,2 iOS12.5.8/16H88 Apple CDN
URL, validates HTTP Content-Range and ZIP CRC, checks the native N61 manifest
identity, and fetches only the manifest, restore plist, iBSS, iBEC, DeviceTree and
kernelcache. It limits total range downloads to 64 MiB. It does not fetch a full
restore IPSW or certify current Apple signing status. `--metadata` can select a
different metadata JSON with the same schema; `--output` selects the workspace.

`inspect_native_baseline.py --workspace /path/to/workspace` checks IM4P structure
and recorded manifest digests, extracts encrypted type-1 KBAG inputs for later
authorized hardware tests, and decompresses plaintext LZSS payloads with Adler32
verification. It does not recover encryption keys or decrypt iBSS/iBEC.

`compare_native_drivers.py --workspace /path/to/workspace --ios13-kexts ...` reads
the native kernel's prelink metadata, including Apple XML ID/IDREF references,
and compares bundle presence and versions against an existing iOS13 inventory.
Matching bundle names or versions do not establish ABI or hardware compatibility.

Previously acquired local workspaces can be inspected directly; no repeat
download is needed. The iOS13 inventory used in this project remains in the
original local analysis directory and is not a firmware artifact shipped here.
