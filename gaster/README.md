# gaster

Fork of gaster for palera1n

This branch records work toward experimental iOS 13 boot on iPhone 6
(iPhone7,2 / N61AP). **It does not contain a working iOS 13 port or an iOS 13
flash procedure.**

- [Current progress and handoff (Vietnamese)](docs/ios13/PROGRESS.vi.md)
- [RAM boot gates and recovery plan](docs/ios13/BOOT-AND-RECOVERY.vi.md)
- [Offline regression tests](tests/README.md)
- [Native baseline acquisition tools](tools/ios13/README.md)

`status` reads the guarded N61AP identity, configuration, DFU state and PWND
marker. `probe` and `decrypt_kbag_pwned` stage RPC commands in DFU RAM and are
device operations. A PWND marker does not prove RPC or AES compatibility.
Legacy `pwn`, `reset`, `decrypt` and `decrypt_kbag` can modify the device's
session; `decrypt_kbag` can automatically exploit it.

Run the host-only checks with `make test` and `make test-sanitize` after
installing a C compiler, xxd, and OpenSSL/libusb development headers. The mock
tests never link the real libusb library. Firmware downloads, keys, device
identifiers and locally built executables stay outside version control.
