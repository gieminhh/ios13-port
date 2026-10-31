# Kết quả sửa/build offline Gaster — 31-10-2026 UTC

> Cập nhật sau lần probe 10:20 UTC: điều kiện `BDID 00` và fixture trong bản build dưới đây đã được xác định là sai; N61AP có `BDID 06`. Mã hiện tại đã sửa và qua 47 ca giả lập cùng ASan/UBSan. Xem [báo cáo sửa nhận dạng](/home/ubuntu/ios13-analysis/identity-fix/report.vi.md). Phần dưới là bản ghi build trước sửa; binary diagnostic cũ không bị thay thế. Không chạy lại probe trong lần sửa này.

Đã thực hiện sau khi người dùng cho phép sửa và build offline. Chưa chạy bất kỳ lệnh nào đến iPhone. Việc người dùng sẵn sàng tự restore nếu cần không được dùng để suy ra rằng recovery đảo ngược được ghi NAND.

## Thay đổi thực tế

- Sửa callback reset A8/A8X theo upstream: 0x1800888A8 → 0x180088898 và 0x180088E28 → 0x180088E18.
- Dành thời hạn tối thiểu 5000 ms cho synchronous A1/02, wValue FFFF, wIndex 0; giữ nguyên thời hạn async/khai thác. IOKit có thay đổi timeout tương ứng nhưng chưa compile/test trên macOS.
- Thêm `probe` và `decrypt_kbag_pwned`: chỉ nhận N61AP (CPID 7000, BDID 00, SRTG được nhận diện), đòi marker PWND và ghim toàn bộ serial qua hai lần mở USB. Nếu không phù hợp, dừng sau một lần tìm; không chạy stage exploit/reset.
- Nhánh guarded libusb chỉ đọc cấu hình hiện tại và yêu cầu configuration 1, không gọi SET_CONFIGURATION.
- `probe` dùng MEMC zero-length: stage 40 byte trong vùng DFU rồi yêu cầu 16 byte gồm DONE_MAGIC và địa chỉ đích trả về. Không gọi AES, không tải OS. Đây vẫn là một thao tác thực lên trạng thái DFU trong RAM, không phải lệnh chỉ in thông tin.
- Thêm `GASTER_USB_TRACE=1`: log setup packet, timeout, mã lỗi backend và elapsed time ở libusb; không log payload hay khóa. Khởi tạo lại transfer length khi có lỗi.
- Từ chối USB_TIMEOUT=0, âm, tràn hoặc có ký tự thừa; xóa cấu hình CPID cũ trước nhận diện; kiểm tra descriptor serial trước khi đọc; từ chối KBAG hex sai.
- Các verb `pwn`, `reset`, `decrypt`, `decrypt_kbag` cũ vẫn tồn tại. Riêng `decrypt_kbag` cũ còn tự pwn; chỉ dùng verb guarded cho phép thử được đề xuất dưới đây.

Mã đã sửa: [gaster.c](/home/ubuntu/gaster/gaster.c). Bộ test: [test_usb_mock.c](/home/ubuntu/gaster/tests/test_usb_mock.c), [hướng dẫn](/home/ubuntu/gaster/tests/README.md). [Diff đã áp dụng](/home/ubuntu/ios13-analysis/gaster-source-applied.patch).

## Build và kiểm chứng

Đã build bốn biến thể bằng GCC 15.2.0, `-Wall -Wextra -Wpedantic -Werror -Os`: baseline, reset-only, timeout-only, diagnostic. Không có warning/error. Baseline/reset-only/timeout-only nằm trong `builds/variants/` và được để không có quyền execute nhằm tránh dùng nhầm.

Binary dùng để duyệt phép thử tiếp theo: `/home/ubuntu/ios13-analysis/builds/gaster-diagnostic`, 47.624 byte.

SHA-256: `b8c2998d7a38c6b8406c4fdf231c5780e91808c6cf99aee5245d5134ade4ad47`.

- 21 ca USB/CLI giả lập qua, gồm các nhánh thiếu thiết bị, không pwned, sai board, sai SoC, serial thay đổi, configuration query lỗi, timeout, short response, sai marker/retval và serialization lệnh AES.
- Các ca đó tiếp tục qua khi bật AddressSanitizer và UndefinedBehaviorSanitizer.
- Test executable không liên kết libusb thật: dynamic dependencies chỉ có libcrypto và libc. Mọi hàm libusb được mock; các byte trả về AES là dữ liệu tổng hợp, không chứng minh phần cứng AES.
- Binary production chỉ được chạy `--help`, một nhánh không khởi tạo USB. Chưa chạy `probe`, AES, pwn hay reset.
- `git diff --check` qua. Binary Gaster gốc `/home/ubuntu/gaster/gaster` giữ nguyên hash; không assemble hay thay đổi payload .bin. `/cdrom` vẫn read-only.

[Manifest và lệnh compiler](/home/ubuntu/ios13-analysis/builds/manifest.json), [kết quả kiểm tra](/home/ubuntu/ios13-analysis/builds/validation.json), [log test](/home/ubuntu/ios13-analysis/builds/test.stdout.log), [log sanitizer](/home/ubuntu/ios13-analysis/builds/sanitizer.stderr.log).

Toolchain được giải nén tại `/home/ubuntu/ios13-analysis/toolchain/`, dùng hai gói GCC có sẵn trên USB và tải khoảng 16 MB gói còn thiếu từ kho Ubuntu. Từng gói đã so SHA-256 với metadata APT có sẵn. Không chạy sudo/apt install/post-install scripts, không thay đổi package đã cài vào OS. [Nguồn và hash gói](/home/ubuntu/ios13-analysis/toolchain/manifest.json).

## Phép thử thiết bị đề xuất, chưa thực hiện

Chỉ khi người dùng duyệt lệnh cụ thể này, máy vẫn đang pwned DFU và chỉ có đúng iPhone N61AP cần thử được nối:

```bash
GASTER_USB_TRACE=1 /home/ubuntu/ios13-analysis/builds/gaster-diagnostic probe
```

Mong đợi: thông tin N61/pwned qua hai lần mở, command A1/02 length=16 timeout=5000, response đủ 16 byte, và `RPC probe succeeded (DONE_MAGIC, zero-length memcpy); AES was not executed.`

Nếu báo không pwned, không matching hoặc timeout: dừng, giữ log; không tự chạy lại, không tự pwn/reset/restore. Nếu treo thiết bị, force restart là đường thoát RAM dự kiến; chưa có bảo đảm phục hồi mọi lỗi bằng recovery.

Quan trọng: callback fix được nhúng vào payload **khi pwn lại**. Chỉ chạy probe trên phiên pwn hiện tại chưa cập nhật callback trong RAM; phép thử này chỉ xác định RPC hiện tại có trả lời hay không. Nếu cần pwn mới để so sánh callback, phải trình riêng command và trạng thái đầu. Hai patch không biến kernel/driver iPad thành tương thích N61.

Sau probe thành công mới đề xuất một lần `decrypt_kbag_pwned` với KBAG type1 iBSS đã trích. Nếu AES thành công, giải mã/audit bootloader offline trước mọi lệnh boot. Chưa có lệnh nạp kernel/bootx được duyệt hoặc thực hiện.
