# Sửa điều kiện nhận dạng N61AP — 31-10-2026 UTC

Đã tiếp tục từ mã nguồn, toolchain, log và kết quả tra cứu của chat trước. Không chạy lại probe, không đọc thiết bị, không gửi RPC/payload, không pwn/reset/flash.

## Nguyên nhân có bằng chứng

Điều kiện cũ trong `checkm8_check_usb_device`:

```c
cpid != 0x7000 ||
strncmp(usb_serial_num, "CPID:7000 ", 10) != 0 ||
strstr(usb_serial_num, " BDID:00 ") == NULL
```

`cpid` ở đây được gán theo chuỗi SRTG; `iBoot-1992.0.0.1.19` chọn profile `0x7000`. Vì thế dòng `CPID: 0x7000` trước thông báo lỗi chỉ xác nhận profile BootROM đã được nhận diện, chưa xác nhận board.

Log lần probe `20261031T102001Z-probe` ghi đúng thông báo yêu cầu `BDID 00`. Metadata cache đã lưu có `prefix="CPID:7000 "`, `CPID=7000`, `BDID=06`, `SRTG=iBoot-1992.0.0.1.19`. Với các trường đã lưu này, hai phép so CPID đều khớp; phép so BDID thất bại vì mã yêu cầu `00` thay vì `06`. Không có bằng chứng lỗi CPID hay SoC.

Bảng thiết bị [libirecovery](https://raw.githubusercontent.com/libimobiledevice/libirecovery/master/src/libirecovery.c) đã được truy xuất trong chat trước (`01a1915a-17fd-7a02-aeb7-4d3a45fb0a48`):

| Model | Board | BDID | CPID |
|---|---|---|---|
| iPhone7,2 / iPhone 6 | n61ap | 0x06 | 0x7000 |
| iPhone7,1 / iPhone 6 Plus | n56ap | 0x04 | 0x7000 |
| iPad5,1 / iPad mini 4 WiFi | j96ap | 0x08 | 0x7000 |

Không truy vấn mạng lại; dùng các hàng nguồn đã lưu trong lịch sử chat. N61AP được xác định bằng cặp CPID/BDID, không có trường tên board `n61ap` được đọc bởi guard này. Chỉ CPID A8 không phân biệt được các board trên.

## Thay đổi

- Yêu cầu profile A8 được nhận diện, CPID thực trong serial bằng `0x7000` và BDID bằng `0x06`.
- Đọc CPID/BDID thành số hex theo từng token độc lập. Chấp nhận thứ tự trường khác và số 0 đứng đầu; từ chối trường thiếu, trùng, tên không đầy đủ, ký tự thừa, dấu và tràn 16 bit. Đây là gia cố phép đọc; lỗi đã chứng minh của lần probe là hằng BDID sai.
- Đổi nhãn log guarded thành `BootROM profile CPID (from SRTG)` để tránh nhầm profile với trường CPID đã xác minh. Thông báo từ chối ghi CPID/BDID nhận được hoặc lỗi định dạng.
- Sửa fixture serial giả lập từ BDID `00` sang `06`. Fixture cũ đồng thuận với hằng sai nên 21 ca test trước không phát hiện được lỗi này.
- Giữ kiểm tra PWND, SRTG, serial không đổi qua hai lần mở USB và việc từ chối tự exploit/reset. Bản sửa không đổi payload hoặc timeout.

## Kiểm chứng offline

- Thêm 26 ca nhận dạng qua chính bộ giải mã descriptor và callback thật, mọi USB call được mock. Mỗi ca kiểm tra không có command upload/download, reset, SET_CONFIGURATION hay async submission.
- Trước sửa: test `CPID:7000 BDID:06` thất bại đúng ở guard, exit `-6` do assertion. Xem `baseline.stderr.log`.
- Sau sửa: toàn bộ **47 ca** qua, gồm 26 ca mới và 21 ca USB/CLI hiện có. Các nhánh không PWND, SRTG lạ, đổi serial, timeout và protocol vẫn được kiểm tra. Xem `test.stdout.log`.
- **47 ca** cũng qua AddressSanitizer + UndefinedBehaviorSanitizer, bật kiểm tra leak và dừng khi gặp lỗi. Xem `sanitizer.stdout.log`, `sanitizer.stderr.log`.
- Compiler dùng toolchain đã có, `-Wall -Wextra -Wpedantic -Werror`, không warning/error. Đã build thêm binary production, chưa thực thi; file `gaster-diagnostic-identity-fixed.elf` có quyền `0644`.
- `readelf` xác nhận executable test không phụ thuộc libusb. Không có thao tác thiết bị thật trong lần sửa này.
- Giữ nguyên hash binary gốc `gaster`, binary diagnostic từng dùng probe và tất cả `payload*.bin`. Lệnh build, log, diff tăng thêm, dependencies và hash nằm cùng thư mục này; xem `validation.json`.

## Giới hạn của bằng chứng về PWND

Metadata cache cũ ghi `pwned: false`, khác thông tin người dùng đã xác nhận trước đó. Log probe chỉ có hai lần GET_DESCRIPTOR và không lưu nội dung serial đầy đủ; không thể suy ra trạng thái PWND trực tiếp lúc probe từ các dòng log đó, cũng không kết luận trạng thái hiện tại. Sau sửa board, nếu serial thực thiếu ` PWND:[checkm8]`, chương trình vẫn dừng trước command. Không bỏ qua yêu cầu PWND và không tự pwn lại.

Bản sửa đã được xác minh bằng giả lập; chưa có kết quả RPC/AES trên phần cứng cho bản sửa này. Binary diagnostic cũ vẫn chứa guard cũ; dùng lại binary đó sẽ không kiểm tra được mã vừa sửa.
