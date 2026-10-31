# Tiến độ port iOS 13 lên iPhone 6

Cập nhật ngày 31-10-2026 UTC. Đích: iPhone7,2 / N61AP / Apple A8, CPID
`0x7000`, BDID `0x06`. Mục tiêu cuối là iOS 13 hoạt động trên máy, trước hết
chứng minh kernel Darwin 19 chạy từ RAM. Chưa có bản port đã boot thành công.

## Kết quả hiện tại

| Hạng mục | Bằng chứng | Trạng thái |
|---|---|---|
| Guard CPID/BDID | N61AP là `7000/06`; mã và fixture cũ yêu cầu `7000/00` | Đã sửa; 47 ca trước đó qua |
| Chỉ đọc trạng thái | Lệnh `status` mới; tổng cộng 56 ca mock qua, cả ASan/UBSan | Đã chạy thành công trên máy thật |
| Danh tính thật | CPID `7000`, BDID `06`, VID/PID `05ac:1227`, configuration 1 | Khớp N61AP/iPhone7,2 |
| PWND thật | Descriptor đọc trực tiếp có `PWND:[checkm8]` | Hiện diện lúc 10:30:17 UTC |
| Trạng thái DFU thật | GETSTATE trả 8, `dfuMANIFEST-WAIT-RESET` | Đã ghi nhận; không reset |
| RPC/AES sau sửa | Chưa chạy; test mock dùng byte tổng hợp | Chưa xác định lỗi AES đã hết hay chưa |
| Native iOS12 baseline | Tải riêng từ Apple; kiểm manifest, digest, CRC/checksum | Đã có file N61 đúng nguồn |
| Boot RAM / flash | Chưa có loader đã audit, patch manifest và kênh chứng minh | Chưa đủ điều kiện thực hiện |

Người dùng đã cho phép **một** lần RPC probe, rồi **chỉ khi probe thành công**
mới một lần AES trên KBAG iBSS N61 12.5.8. Chưa chạy hai phép thử này trước yêu
cầu đóng gói/commit. Không suy diễn quyền chạy lại, pwn/reset hay flash từ quyền
thử RPC/AES. Mọi lệnh ghi firmware vẫn cần kế hoạch cụ thể và người dùng duyệt.

## Những thay đổi trong Gaster

- Sửa callback reset A8 `0x1800888A8 → 0x180088898`, A8X
  `0x180088E28 → 0x180088E18` theo upstream. Đây là dữ liệu được chèn vào
  payload khi pwn; rebuild host không thay payload đang nằm trong RAM.
- Dành ít nhất 5000 ms cho synchronous RPC `A1/02/FFFF/0000`; giữ timing
  khai thác/async. Khởi tạo transfer length khi lỗi; kiểm đầu vào timeout/KBAG.
- `probe` và `decrypt_kbag_pwned` kiểm CPID/BDID/SRTG, PWND, rồi ghim serial qua
  hai lần mở USB; không tự exploit/reset hoặc SET_CONFIGURATION ở libusb.
- Đọc CPID/BDID thành số hex theo token, từ chối trường thiếu/trùng/sai/tràn.
  Nhãn CPID từ SRTG được ghi rõ là profile BootROM, tránh hiểu nhầm là board.
- `status` dùng guard đã sửa nhưng cho phép báo PWND absent; chỉ đọc descriptor,
  cấu hình hiện tại và GETSTATE. Không dùng GETSTATUS vì có thể chuyển DFU state.
- Thêm `make test`, `make test-sanitize`, log setup packet và các script baseline.
  IOKit/macOS chưa được build hoặc thử hardware trong phiên này.

Exit 0 của `status` chứng minh đọc trạng thái thành công, không chứng minh RPC,
AES hay boot khả dụng. State 8 không tự chứng minh thiết bị hỏng hoặc cần reset.
Không bỏ guard khi lỗi, không tự clear trạng thái hoặc chạy exploit lại.

## Thành phần hiện có và phần thiếu

| Thành phần | Đã có | Còn thiếu để dùng cho boot |
|---|---|---|
| iPadOS 13.7, 17H35 | IPSW; kernel ARM64_T7000 Darwin 19.6.0 đã giải nén và đối chiếu checksum; 203 kext | Patch/handoff N61 đã audit; không có identity N61 trong manifest |
| Bootloader iPad13 | iBSS/iBEC `ipad5` có file mã hóa | Key và audit; không dùng loader J96 nguyên trạng cho N61 |
| Native iOS12.5.8, 16H88 | iBSS/iBEC N61, đều iBoot-4513.270.14, đúng digest manifest | Giải mã, audit DRAM/board/entry/verifier, tạo artifact thử có hash |
| DeviceTree N61 | IM4P gốc Apple; payload rõ 119852 byte, 147 node; model/compatible đúng N61; paths khớp JSON cũ | Runtime RAM/framebuffer/boot fields do loader điền; các sửa cho kernel19 có kiểm chứng |
| Kernel12 native | Darwin 18.7.0 ARM64_T7000; raw 28258824 byte, Adler32 khớp; 194 kext | Chưa chứng minh ABI driver12 tương thích kernel19 |
| RAMDisk/log | Có restore RAMDisk/trustcache trong IPSW iPad13 | RAMDisk chẩn đoán tối thiểu, trust cho binary sửa, init không ghi storage; kênh log độc lập |
| Userland/UI iOS13 | Rootfs iPad nằm trong IPSW | Thích nghi iPhone, driver, bộ nhớ và dịch vụ; chưa chứng minh SpringBoard |

Lần này tải riêng khoảng 14,24 MB cho baseline N61, không tải full IPSW 12.5.8.
Mỗi thành phần N61 đối chiếu được SHA1 trong manifest Apple và có SHA256 riêng
trong [bằng chứng](evidence/native-baseline.json). CRC và hash không thay cho
ticket/chữ ký cần thiết khi boot.

So sánh native12 mới với inventory13 cũ xác nhận thiếu các bundle:
`AppleD2186PMU`, `AppleChestnutDisplayPMU`, `ApplePinotLCD`,
`AppleMultitouchSPIN61`. Còn thiếu `AppleCS42L67Audio`, `AppleSN2400Charger` và
một số bundle khác trong tập iPad. Xem [driver-gaps.json](evidence/driver-gaps.json).
Không phải mọi bundle chỉ có ở kernel iPhone7 đều cần N61; tập kernel có cả
personality cho thiết bị khác. Trùng bundle/version cũng không chứng minh ABI.

Không đổi `pmu,d2186` thành `pmu,d2207` để ép driver match, không copy kext12
vào kernel13 khi chưa kiểm imports, vtable, relocation và dependency contract.
Đích sử dụng qua Wi-Fi vẫn cần hiển thị, cảm ứng, nguồn/nhiệt và Wi-Fi mã hóa;
bỏ cellular/Touch ID không giải quyết các blocker này. Không giả định bỏ toàn
bộ SEP vẫn giữ được keystore/Wi-Fi.

## Bằng chứng và cách tiếp tục

- [Log đọc thiết bị thật](evidence/device-status.stdout.log),
  [USB request log](evidence/device-status.stderr.log),
  [record binary/hash](evidence/device-status-result.json).
- [Validation](evidence/validation.json): 56 ca mock, sanitizer, trạng thái phần
  cứng và các phép thử chưa làm. Chỉ có GET_DESCRIPTOR, GET_CONFIGURATION và
  GETSTATE trong lần đọc thật; không ghi firmware.
- [Cổng boot RAM và kế hoạch khôi phục](BOOT-AND-RECOVERY.vi.md).
- [Script baseline](../../tools/ios13/README.md): tải lại được các file N61 mà
  không cần đưa firmware Apple lên GitHub.

## Cập nhật tiếp quản phiên mới (Host Windows + WSL2)

- **Môi trường:** Chuyển giao sang Windows 10/11 + WSL2 (Ubuntu 24.04 LTS). Chạy kiểm
  chứng toàn bộ 56 mock tests và sanitizer trên WSL2: PASS 56/56 cases (exit code 0).
- **Phát hiện lệch ABI boot_args:** Phân tích mã máy `start.s` giữa Darwin 18 (iOS 12)
  và Darwin 19 (iOS 13) phát hiện `CommandLine` mở rộng từ 256 lên 608 bytes, khiến
  offset của `bootFlags` bị đẩy từ `0x170` (Darwin 18) lên `0x2d0` (Darwin 19). iBoot 12
  nếu gọi trực tiếp sẽ khiến Darwin 19 đọc vùng nhớ rác làm bootFlags.
- **Trampoline chuyển đổi:** Đã xây dựng `generate_trampoline.py` tạo stub ARM64 chuyển
  đổi `old_boot_args` sang `new_boot_args` chuẩn Darwin 19 trong RAM trước khi trao quyền
  cho kernel.
- **Visual Checkpoint:** Xác định chính xác entry function `_StartIOKit` tại địa chỉ
  `0xfffffff0075f9a20` (file offset `0x5f5a20`). Toàn bộ core MMU, CPU, Mach scheduler
  khởi tạo trước mốc này; cho phép hiển thị dải màu framebuffer để xác nhận thực thi kernel
  mà không cần driver IOKit hay đụng NAND.
- **Công cụ giải mã:** Đã xây dựng `decrypt_im4p.py` kết nối OpenSSL để giải mã tự động
  `iBSS`/`iBEC` ngay khi trích xuất được IV/Key từ phần cứng.

Trên máy làm việc ban đầu, phân tích và firmware đã có vẫn nằm tại
`/home/ubuntu/ios13-analysis/` và `/cdrom/ios13-research/`; không bắt đầu lại
nghiên cứu khi các artifact này còn nguyên. Danh sách lệnh RPC/AES đã chuẩn bị
ở `continuation-20261031/proposed-hardware-tests.json` trong thư mục phân tích
cục bộ. File đó chứa KBAG mã hóa và đường dẫn local nên không đưa vào Git.
Trước tiếp tục thử thiết bị sau bàn giao phải kiểm lại hash binary và trạng
thái/danh tính hiện tại, vì kết quả ở đây là snapshot ngày 31-10-2026.

Nguồn: [libirecovery device table](https://github.com/libimobiledevice/libirecovery/blob/master/src/libirecovery.c),
[upstream callback fix](https://github.com/0x7ff/gaster/commit/7fffffff38a1bed1cdc1c5bae0df70f14395129b),
[USB DFU 1.1 §6.1.5](https://www.usb.org/sites/default/files/DFU_1.1.pdf).
