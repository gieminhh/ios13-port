# Offline USB regression tests

`test_usb_mock.c` includes the host program with a renamed CLI entry point and
provides all libusb functions used by it. **Do not link this test with libusb.**
The fake device uses synthetic serial numbers and reply bytes; no device access,
AES hardware operation or exploit execution occurs.

On a development machine with a C compiler and OpenSSL/libusb development headers:

```sh
make gen
cc -Wall -Wextra -Wpedantic -Werror -DHAVE_LIBUSB -DVERSION='"offline-test"' \
  tests/test_usb_mock.c lzfse.c -o /tmp/gaster-usb-mock-test -lcrypto
/tmp/gaster-usb-mock-test
```

Alternatively, `make test` and `make test-sanitize` generate headers and test
binaries under ignored `build/tests/`. Neither target links libusb. The current
suite has 56 cases, including the previous 47 identity/USB/CLI cases and nine
status cases. `status` tests allow only descriptor reads and DFU GETSTATE in the
mock control-transfer function and assert zero command uploads/downloads,
resets, SET_CONFIGURATION or async exploit submissions. They cover PWND present
and absent, wrong board, no device, timeout, short/invalid replies and dfuERROR.

The production `status` command uses GETSTATE, not GETSTATUS, to avoid advancing
the DFU state machine. Exit 0 means the status was read successfully; a reported
dfuERROR or dfuMANIFEST-WAIT-RESET is not a boot-readiness certificate.

The tests cover command vs. exploit timeouts, expected STALL handling, initialized
error lengths, no-device/non-pwned/unsupported-board rejection, identity changes,
RPC framing/markers/return values, short replies, backend timeouts, AES command
serialization, malformed KBAG input and timeout validation. They cannot establish
that an A8 ROM address is correct or that a real device completes AES within a
particular deadline.

The N61AP fixture is CPID `7000`, BDID `06` (iPhone7,2), following the
[libirecovery device table](https://github.com/libimobiledevice/libirecovery/blob/master/src/libirecovery.c).
BDID `00` was an incorrect fixture that concealed the original guard bug. The
identity matrix accepts equivalent plain hexadecimal values and reordered fields,
and rejects other boards (including N56AP/`04` and J96AP/`08`), missing fields,
duplicate fields, partial names, invalid digits, signs and 16-bit overflow. It
runs the real USB descriptor decoder and identity callback with mocked USB reads;
each identity-only case asserts zero command uploads/downloads, resets,
configuration changes or asynchronous submissions. The CLI cases also verify
that missing PWND and unsupported SRTG still stop before command downloads.

The `probe` and `decrypt_kbag_pwned` production commands are device operations,
not offline tests. They are restricted to the N61AP A8 profile, require an already
pwned device and refuse automatic exploit/reset. A `PWND` marker still does not
prove payload protocol compatibility. The probe stages a zero-length MEMC command
in the DFU buffer and checks DONE_MAGIC and its return value; it does not call AES.
