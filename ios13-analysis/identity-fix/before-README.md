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

The tests cover command vs. exploit timeouts, expected STALL handling, initialized
error lengths, no-device/non-pwned/unsupported-board rejection, identity changes,
RPC framing/markers/return values, short replies, backend timeouts, AES command
serialization, malformed KBAG input and timeout validation. They cannot establish
that an A8 ROM address is correct or that a real device completes AES within a
particular deadline.

The `probe` and `decrypt_kbag_pwned` production commands are device operations,
not offline tests. They are restricted to the N61AP A8 profile, require an already
pwned device and refuse automatic exploit/reset. A `PWND` marker still does not
prove payload protocol compatibility. The probe stages a zero-length MEMC command
in the DFU buffer and checks DONE_MAGIC and its return value; it does not call AES.
