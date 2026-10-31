.PHONY: macos libusb ios payload clean test-headers test test-sanitize
.DEFAULT_GOAL := macos

CC ?= clang
GIT_VERSION := $(shell git rev-parse HEAD 2>/dev/null | tr -d '\n')
ifeq ($(GIT_VERSION),)
VERSION ?= ios13-n61-fixed
else
VERSION ?= $(GIT_VERSION)-$(shell git rev-list --count HEAD 2>/dev/null | tr -d '\n')
endif
TEST_BUILD_DIR ?= build/tests
TEST_CFLAGS ?= -Wall -Wextra -Wpedantic -Werror
TEST_LDLIBS ?= -lcrypto
SANITIZER_LDFLAGS ?=

# Offline only: these binaries provide their own libusb mocks. Never link libusb.
test-headers:
	mkdir -p "$(TEST_BUILD_DIR)/include"
	for payload in payload_A9.bin payload_notA9.bin payload_notA9_armv7.bin payload_handle_checkm8_request.bin payload_handle_checkm8_request_armv7.bin; do \
		xxd -iC "$$payload" "$(TEST_BUILD_DIR)/include/$${payload%.bin}.h" || exit; \
	done

test: test-headers
	$(CC) $(CPPFLAGS) $(CFLAGS) $(TEST_CFLAGS) -DHAVE_LIBUSB -DVERSION='"offline-test"' -I"$(TEST_BUILD_DIR)/include" tests/test_usb_mock.c lzfse.c -o "$(TEST_BUILD_DIR)/test_usb_mock" $(LDFLAGS) $(TEST_LDLIBS)
	"$(TEST_BUILD_DIR)/test_usb_mock"

test-sanitize: test-headers
	$(CC) $(CPPFLAGS) $(CFLAGS) $(TEST_CFLAGS) -DHAVE_LIBUSB -DVERSION='"offline-test"' -I"$(TEST_BUILD_DIR)/include" -fsanitize=address,undefined -fno-omit-frame-pointer -g tests/test_usb_mock.c lzfse.c -o "$(TEST_BUILD_DIR)/test_usb_mock_sanitized" $(LDFLAGS) $(SANITIZER_LDFLAGS) $(TEST_LDLIBS)
	ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 "$(TEST_BUILD_DIR)/test_usb_mock_sanitized"

macos: gen
	xcrun -sdk macosx clang -mmacosx-version-min=10.9 -Weverything gaster.c lzfse.c -o gaster -framework CoreFoundation -framework IOKit -Os -DVERSION=\"$(VERSION)\"
	$(RM) payload_A9.h payload_notA9.h payload_notA9_armv7.h payload_handle_checkm8_request.h payload_handle_checkm8_request_armv7.h

gen:
	xxd -iC payload_A9.bin payload_A9.h
	xxd -iC payload_notA9.bin payload_notA9.h
	xxd -iC payload_notA9_armv7.bin payload_notA9_armv7.h
	xxd -iC payload_handle_checkm8_request.bin payload_handle_checkm8_request.h
	xxd -iC payload_handle_checkm8_request_armv7.bin payload_handle_checkm8_request_armv7.h

libusb: gen
	$(CC) -Wall -Wextra -Wpedantic -DHAVE_LIBUSB gaster.c lzfse.c -o gaster -lusb-1.0 -lcrypto -pthread -ldl -Os -DVERSION=\"$(VERSION)\"
	$(RM) payload_A9.h payload_notA9.h payload_notA9_armv7.h payload_handle_checkm8_request.h payload_handle_checkm8_request_armv7.h

windows: gen
	x86_64-w64-mingw32-gcc -Wall -Wextra -DHAVE_LIBUSB -Iwindows/include gaster.c lzfse.c windows/libusb-1.0.dll windows/libcrypto-1_1-x64.dll -lpthread -o windows/gaster.exe -Os -DVERSION=\"$(VERSION)-win\"
	$(RM) payload_A9.h payload_notA9.h payload_notA9_armv7.h payload_handle_checkm8_request.h payload_handle_checkm8_request_armv7.h

libusb-static: gen
	$(CC) $(CFLAGS) $(LIBS) $(LDFLAGS) -Wall -Wextra -Wpedantic -DHAVE_LIBUSB gaster.c lzfse.c -o gaster -Os -static -DVERSION=\"$(VERSION)\"
	$(RM) payload_A9.h payload_notA9.h payload_notA9_armv7.h payload_handle_checkm8_request.h payload_handle_checkm8_request_armv7.h

payload:
	as -arch arm64 payload_A9.S -o payload_A9.o
	gobjcopy -O binary -j .text payload_A9.o payload_A9.bin
	$(RM) payload_A9.o
	as -arch arm64 payload_notA9.S -o payload_notA9.o
	gobjcopy -O binary -j .text payload_notA9.o payload_notA9.bin
	$(RM) payload_notA9.o
	as -arch armv7 payload_notA9_armv7.S -o payload_notA9_armv7.o
	gobjcopy -O binary -j .text payload_notA9_armv7.o payload_notA9_armv7.bin
	$(RM) payload_notA9_armv7.o
	as -arch arm64 payload_handle_checkm8_request.S -o payload_handle_checkm8_request.o
	gobjcopy -O binary -j .text payload_handle_checkm8_request.o payload_handle_checkm8_request.bin
	$(RM) payload_handle_checkm8_request.o
	as -arch armv7 payload_handle_checkm8_request_armv7.S -o payload_handle_checkm8_request_armv7.o
	gobjcopy -O binary -j .text payload_handle_checkm8_request_armv7.o payload_handle_checkm8_request_armv7.bin
	$(RM) payload_handle_checkm8_request_armv7.o

clean:
	$(RM) gaster
