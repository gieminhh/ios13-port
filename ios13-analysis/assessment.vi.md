# Đánh giá iOS/iPadOS 13.7 trên iPhone 6 N61AP

Ngày nghiên cứu: 31-10-2026 UTC. Mục tiêu: iPhone7,2 / N61AP / CPID 0x7000. Đây là kết quả phân tích tĩnh và thiết kế thí nghiệm, chưa phải một bản port đã boot.

Phạm vi tính năng mới nhất: người dùng chấp nhận bỏ cellular/Touch ID và một số chức năng SEP để ưu tiên sử dụng qua Wi-Fi; xem [tiêu chí và giới hạn cập nhật](/home/ubuntu/ios13-analysis/usable-wifi-scope.vi.md). Điều này không phê duyệt thao tác lên máy hoặc sửa mã nguồn.

Trạng thái mới sau khi được phép sửa mã: [đã áp dụng bản vá và hoàn tất build/21 ca test offline](/home/ubuntu/ios13-analysis/build-status.vi.md). Các phần kiểm kê ban đầu dưới đây mô tả snapshot trước sửa; chưa có thử nghiệm trên iPhone.

## 1. Kết luận và mức độ chắc chắn

**Có cơ sở kỹ thuật để thử đạt mốc thực thi kernel Darwin 19 trên A8; chưa có bằng chứng đủ để cam kết một hệ thống iOS 13 dùng được trên N61AP.** Bộ iPadOS 13.7 hiện có chứa kernel ARM64 T7000, cùng họ CPU và bộ điều khiển nền tảng với máy đích. Trở ngại chính là cấu hình bo mạch, driver, giao diện giữa bootloader và kernel, và sau đó là SEP, hệ thống tệp và userland. Không có cơ sở kết luận A8 tự nó không thể chạy mã kernel iOS 13.

Phát hiện có thể hành động ngay về Gaster: bản cục bộ giữ địa chỉ callback reset A8 cũ `0x1800888A8`; upstream đã đổi thành `0x180088898`. Ngoài ra cùng timeout mặc định 5 ms được dùng cho khai thác và lệnh AES. Hai vấn đề cần thử riêng. Chỉ từ lỗi `-7` không thể chứng minh vấn đề nào gây ra lần lỗi đã quan sát.

Phân loại bằng chứng trong báo cáo:

- **Xác nhận tại chỗ:** đọc trực tiếp tệp, parse cấu trúc, so sánh byte hoặc checksum.
- **Xác nhận từ nguồn:** mã nguồn/tài liệu của tác giả dự án, có liên kết và phiên bản khi lấy được.
- **Giả thuyết:** giải thích hoặc kiến trúc chưa được kiểm chứng trên máy; mỗi giả thuyết có phép thử và điều kiện bác bỏ.
- **Do người dùng cung cấp:** iOS đang cài là 12.5.8 (16H88), máy đã Pwned DFU và lỗi USB đã ghi nhận. Không truy vấn thiết bị để xác nhận lại các trạng thái này.

Trong phiên này không chạy Gaster, irecovery, exploit, USB probe hay lệnh đặc quyền; không chạm Windows/BitLocker, NAND, SEP, baseband; không remount USB và không tải IPSW mới. Chỉ ghi báo cáo, dữ liệu dẫn xuất và hai tệp diff chưa áp dụng vào `/home/ubuntu/ios13-analysis/`. Mã nguồn Gaster và firmware gốc được giữ nguyên.

## 2. Kiểm kê và xác thực dữ liệu

Tất cả mục được nêu trong yêu cầu đều tồn tại dưới `/cdrom/ios13-research/`. `findmnt` báo `/cdrom` là `/dev/sda1`, vfat, có tùy chọn `ro`. Không thay đổi mount.

| Dữ liệu | Kết quả xác nhận |
|---|---|
| `iPadOS13.7.ipsw` | 3.694.602.857 byte; 53 mục ZIP; manifest ghi 13.7 / 17H35 |
| `extracted-ipad-mini4/BuildManifest.plist` | Trùng byte với mục trong ZIP; hỗ trợ iPad5,1–iPad5,4, không có iPhone7,2 |
| J96AP | `ApChipID=0x7000`, `ApBoardID=0x08`; J97AP là 0x0A; không nhầm A8X J81/J82 0x7001 |
| Kernel nén | IM4P `krnl`, payload `complzss`, không có trường KBAG trong container đã parse |
| Kernel giải nén | Mach-O ARM64; 34.684.928 byte; Darwin 19.6.0, xnu-6153.142.1~8, RELEASE_ARM64_T7000 |
| Xác thực giải nén | Giải LZSS độc lập trong RAM: trùng từng byte với tệp kernel giải nén; Adler-32 `0x1a514294` khớp header |
| DeviceTree J96 | IM4P `dtre`, dữ liệu cây không mã hóa; parse đủ 139.340 byte, 168 node; tập đường dẫn trùng JSON J96 |
| iBSS / iBEC iPad | IM4P `ibss` / `ibec`, mô tả iBoot-5540.140.12, có KBAG type 1 và 2; payload cần giải mã để phân tích mã lệnh |
| Các tệp đã trích | Kernel, DT, iBSS, iBEC trùng byte với mục tương ứng trong ZIP; hai bản sao bootloader trong `bootchain-ipad13/` cũng có mặt |
| Gaster | Commit cục bộ `20958256a4706b6396e2d9ee9ca742618459980b`; cây Git sạch |
| Backup Gaster | Source, binary x86_64, payload notA9 và handler trong tar trùng với bản hiện tại |

SHA-256 kernel giải nén: `43f1596e84dcbd3eb734f91a342a51afff2f045131dbb05c81d92c78222eab0e`.

Dữ liệu máy đọc được nằm trong [evidence.json](/home/ubuntu/ios13-analysis/evidence.json), [kernel13-kexts.json](/home/ubuntu/ios13-analysis/kernel13-kexts.json), [devicetree-paths.json](/home/ubuntu/ios13-analysis/devicetree-paths.json). Không tính hash toàn bộ IPSW nhiều GB; xác thực các thành phần cần dùng không chứng minh ZIP được Apple ký hay nguồn tải đáng tin. Chưa xác minh mật mã chữ ký firmware.

Thiếu trong thư mục đã kiểm tra: kernel iOS 12 N61 gốc để so ABI, iBSS/iBEC N61 bản rõ và DeviceTree N61 dạng nhị phân có nguồn gốc kiểm chứng được. JSON N61 và báo cáo so sánh là dữ liệu đầu vào hữu ích nhưng chưa chứng minh phiên bản firmware tạo ra chúng. Các trường bộ nhớ/tần số đang bằng 0 trong cây tĩnh cần được bootloader điền lúc boot, không phải cấu hình RAM thật.

## 3. Xếp hạng các phương án

Xếp hạng dưới đây dành cho **mốc kernel có bằng chứng**, không phải xác suất thống kê hay lời bảo đảm.

| Hạng | Phương án | Bằng chứng thuận | Trở ngại / phép thử quyết định |
|---|---|---|---|
| 1 | iBSS/iBEC N61 iOS 12 đã audit → kernel J96 13.7 → cây N61 được bổ sung có chọn lọc | Giữ khởi tạo DRAM, màn hình và thông tin bo mạch của N61; kernel đã là T7000 | Chưa có loader bản rõ; phải kiểm tra loader có xử lý được Mach-O, IMG4 và boot_args của kernel 13 hay không. Thử native kernel 12 trước, rồi checkpoint kernel 13 trước StartIOKit |
| 2 | iBSS/iBEC J96 13.7 được sửa riêng cho N61 → kernel 13 | Loader và kernel cùng thế hệ | Có thể thất bại ngay khi iBSS/iBEC đọc board-id hoặc khởi tạo DRAM/PMU/display. Cùng CPID không đủ. Cần giải mã, tìm bảng board và audit đường init trước khi gửi |
| 3 | Môi trường tiền khởi động PongoOS / monitor tùy biến → handoff kernel 13 | PongoOS có driver nền tảng CPID 0x7000 và USB IRQ 182 | Không phải tải `Pongo.bin` thẳng bằng Gaster là dùng được: stage3 của Pongo gắn với trampoline/handoff bootloader và boot_args. Cần thiết kế loader/hook tương thích; hỗ trợ SoC không chứng minh hỗ trợ thay kernel theo ý muốn |
| 4 | Kernel A8 từ mini 4 + userland điện thoại iPhone 6s iOS 13 cùng build | Có khả năng giữ giao diện điện thoại về sau | Kernel/device drivers vẫn là vấn đề; phải kiểm tra arm64/arm64e, dyld cache, framework, entitlements, daemon và version. Chưa có firmware 6s tại chỗ. Không thể chỉ đổi dyld cache hoặc một plist |
| 5 | Kernel 12 N61 + môi trường userland 13 | Driver bản địa có sẵn | Darwin 18 không tự có syscall/Mach/IOKit contract của Darwin 19. Chạy được một binary không chứng minh toàn bộ OS; không đạt mục tiêu kernel iOS 13 |
| 6 | Dùng nguyên IPSW iPad, đổi tên model / nạp kernel 6s A9 nguyên trạng | Rất ít công việc chuẩn bị | Manifest không có N61, cây/driver iPad khác, kernel A9 không phải T7000. Không có đường boot đáng tin cậy chỉ bằng đổi tên |

**Khuyến nghị:** phương án 1, bắt đầu bằng checkpoint kernel rất sớm, chưa khởi tạo storage hoặc SEP. Nếu boot_args/loader 12 không tương thích, chuyển điều tra phương án 2 hoặc 3; không đổi hàng loạt thành phần cùng lúc.

## 4. Bản đồ chướng ngại boot chain

```text
[SecureROM A8 / DFU]
  → [payload checkm8, RAM: sửa xác thực + handler lệnh]
       chặn hiện tại: callback reset cũ; timeout; chưa xác minh RPC/AES
  → [iBSS: board / DRAM / image validation]
       chặn sớm nhất khi dùng nguyên J96: khác N61; payload loader mã hóa
  → [iBEC: image loading, DeviceTree, memory-map, boot_args, framebuffer]
       chặn: signature/type/board checks và ABI handoff chưa kiểm chứng
  → [entry kernel T7000 / CPU / MMU / platform expert]
       mốc chứng minh đầu tiên: checkpoint do kernel chạy, trước StartIOKit
  → [IOKit / PMU / storage / SEP / display]
       chặn: D2186 thiếu, cây/bảng tài nguyên khác, giao thức SEP chưa biết
  → [root RAMDisk + init chẩn đoán]
       chặn: AMFI/trust cache, root-device matching, bộ nhớ
  → [userland 13 / SpringBoard / hệ thống dùng được]
       chặn: driver N61, graphics ABI, SEP, dyld, daemon, bộ nhớ, storage
```

Apple mô tả chuỗi kiểm tra chữ ký, LLB trên A9 trở xuống, và secure boot riêng của SEP/baseband: [Boot process](https://support.apple.com/nl-nl/guide/security/secb3000f149/web). Trong nhánh DFU thí nghiệm iBSS/iBEC là các stage tải qua USB; không vì boot bình thường có LLB mà cần flash hoặc thay LLB trên NAND.

IMG4 có nhiều vấn đề độc lập: giải mã IM4P, xác minh nội dung, kiểm tra loại ảnh, điều kiện board/chip, và ticket IM4M cá thể hóa. Sửa xác thực ở SecureROM không mặc nhiên sửa mọi stage phía sau. IM4M của máy khác không trở thành ticket hợp lệ cho N61; repack ảnh chỉ có ích khi verifier thực sự đã được sửa trong RAM. [Apple: Secure software updates](https://support.apple.com/en-au/guide/security/secf683e0b36/web).

`boot_args` ARM64 có memSize, Video, deviceTreeP/Length, CommandLine và các trường version/revision; phải đối chiếu parser loader thực tế, không đoán theo năm iOS. Nguồn tham chiếu gần kernel hiện có: [XNU arm64/boot.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-6153.141.1/pexpert/pexpert/arm64/boot.h#L57) và [PE_init_platform / PE_init_iokit](https://github.com/apple-oss-distributions/xnu/blob/xnu-6153.141.1/pexpert/arm/pe_init.c). Đây là bản nguồn 6153.141.1 tham khảo, không khẳng định đồng nhất binary 6153.142.1~8.

Với phương án 1, điểm hỏng có thể đến trước IOKit nếu memory map, exception level, page tables, entry point hoặc boot_args sai. Nếu qua được entry/platform expert, PMU/platform services là chướng ngại nghiêm trọng kế tiếp. Chưa có log kernel nên không thể chọn một instruction hay một driver làm “điểm panic chắc chắn”.

## 5. Đánh giá tương thích phần cứng

Kết quả đếm lại: N61 có 147 node, J96 có 168, chung 113, riêng N61 34, riêng J96 55. Các số này khớp báo cáo đầu vào. Tuy nhiên khác số phandle không nhất thiết khác phần cứng: N61 `dart-ave` parent 106 và J96 parent 101 đều trỏ `/arm-io/dart-ave/mapper-ave`; tương tự parent DART của disp0 và DMA mca1. Ngược lại, `disp0/function-lcd_enable` thật sự chuyển từ N61 `/mipi-dsim/lcd` sang J96 `/displayport`.

| Khối | Bằng chứng cụ thể | Đánh giá / cách xử lý |
|---|---|---|
| CPU / AIC / GPIO | Cùng `apple,typhoon`, `arm-io,t7000`; AIC `aic,1`, cùng reg/IRQ/IPI trong JSON; kernel có AppleT7000, AppleS5L8960XGPIOIC | Cơ sở mạnh cho early boot; vẫn phải xác minh timer, MMU và SMP trên máy. Có thể thử CPU0 trước nếu patch/boot-arg thực sự được binary hỗ trợ |
| PMGR | Cùng `pmgr1,t7000` và bảng reg chính; kernel có AppleT7000PMGR | Có khả năng tái sử dụng phần SoC; khác cấu hình điện/nhiệt và PMU ngoài SoC vẫn quan trọng |
| PMU | N61 `pmu,d2186`, J96 `pmu,d2207`; kernel 13 có AppleD2207PMU personality chỉ match `pmu,d2207`, không có AppleD2186PMU | Không đổi compatible thành d2207 để ép match: khác giao thức/thanh ghi có thể tác động nguồn điện. Cần driver d2186 tương thích kernel 13 hoặc chuyển thể có kiểm chứng |
| Display | N61 `mipi-dsim-1,synopsys` + `lcd,pinot`, display PMU Chestnut; J96 `displayport,t7000` + `lcd,edp`; thiếu Pinot/Chestnut trong danh sách kext kernel 13 | Không kỳ vọng màn hình iOS hoạt động nguyên trạng. Framebuffer do native loader để lại có thể là kênh chẩn đoán tạm thời, chỉ khi địa chỉ/stride/cache đúng và không bị kernel tái khởi tạo |
| Touch | N61 `spi2/multi-touch`, `multi-touch,n61`; J96 ở spi1, `multi-touch,j96`; kernel có AppleMultitouchSPIJ96, thiếu AppleMultitouchSPIN61 | Khác bus và personality/firmware. Không đổi tên node để giả J96. Để sau mốc kernel/USB |
| NAND / ANS | Cùng `iop,s5l8960x`; N61 ans có 1 reg range/clock gate 22, J96 4 ranges/gates 22,53 và property mới; AppleStorageDrivers 489.120.1 hiện diện | Cùng tên driver/compatible không chứng minh API hay tài nguyên tương thích. Không thêm mù các reg J96; đầu tiên dùng RAMDisk và ngăn đường storage trước khi test |
| USB | Device controller compatible, IRQ 182, reg và endpoint layout trong JSON trùng; kernel có AppleS5L8960XUSB, USB device mux/NCM | Triển vọng cho telemetry sau IOKit, nhưng bootloader USB, Pongo USB và kernel USB là các tầng khác nhau; mất kết nối lúc handoff không tự nó là panic |
| Baseband | N61 có HSIC baseband và node baseband; J96 là bản Wi-Fi, manifest không có baseband identity cho N61 | Loại khỏi thí nghiệm đầu; không nạp baseband iPad/6s. Kernel boot không đòi hỏi chứng minh gọi điện |
| RAM | iPhone 6 khoảng 1 GiB, mini 4 2 GiB theo teardown; JSON có giới hạn per-task 650 so với 1450 nhưng không có memSize thật | Phải dùng kích thước RAM N61 do loader cung cấp. Không giữ quota iPad. Kernel 34,7 MB không tự tạo rào cản 2 GiB; userland và RAMDisk cần budget thực tế |

Nguồn RAM: [iFixit iPhone 6](https://www.ifixit.com/Device/iPhone_6), [iFixit mini 4](https://www.ifixit.com/News/7383/ipad-mini-4-teardown). IRQ/reg trong cây arm-io là theo bus/ranges; các trường `reg` I2C/SPI do JSON diễn giải không nên coi là địa chỉ MMIO tuyệt đối.

Kernel13 có **203 mục prelink**, được parse trực tiếp tại file offset `0x1eb4000` (section `__PRELINK_INFO,__info`). Không phải mọi mục đều là một executable kext độc lập. Báo cáo kext đầu vào nêu kernel12 có 194, chung 182, thiếu 12 driver và 109 “different versions”; chưa có kernel12 gốc để xác minh nửa so sánh này. Nhiều dòng là `Unknown -> 1`, không phải bằng chứng version đã thay đổi.

Những thành phần iOS12 có thể giữ lại trước: native loader, wiring/bảng phần cứng N61, thông tin runtime về RAM/framebuffer. Driver D2186/Pinot/Chestnut/N61 touch là ứng viên chuyển thể, **không phải kext có thể copy vào là chạy**. Cần so undefined symbols/exports, relocation/fixups, C++ vtable, superclass, IOKit lifecycle, dependency versions và kernel protections. Apple ARMPlatform 13, IOMobileGraphicsFamily 338.6.1, IOSurface/IOAccelerator và firmware GPU phải được xét thành một tập tương thích.

## 6. Gaster: nguyên nhân khả dĩ và bản vá đề xuất

### 6.1 Luồng gọi đã kiểm tra

[gaster_decrypt_kbag](/home/ubuntu/gaster/gaster.c:1583) → [gaster_checkm8](/home/ubuntu/gaster/gaster.c:1249) → [gaster_aes](/home/ubuntu/gaster/gaster.c:1513) → [gaster_command](/home/ubuntu/gaster/gaster.c:1495) → [dfu_send_data](/home/ubuntu/gaster/gaster.c:994) → synchronous control request.

A8 được nhận qua SRTG `iBoot-1992.0.0.1.19` ở [bảng cấu hình](/home/ubuntu/gaster/gaster.c:595). Nhánh dùng payload notA9 **ARM64**, không dùng payload A9 hoặc armv7. Địa chỉ AES là `0x10000DA90`, USB transfer là `0x10000EBB4`, vùng lệnh `0x180380000`.

KBAG 48 byte → request 120 byte: header 72 byte + dữ liệu 48. Response 64 byte gồm DONE_MAGIC 8, retval 8, kết quả 48. Setup packet là `a1 02 ff ff 00 00 40 00`. Các offset input `base+0x48`, output `base+0x10` khớp handler. Không có bằng chứng lỗi chiều IN/OUT hoặc yêu cầu sai độ dài ở đây.

[payload_handle_checkm8_request.S](/home/ubuntu/gaster/payload_handle_checkm8_request.S:32) nhận little-endian halfword `0x02A1`, kiểm tra wValue `0xFFFF`, gọi AES tại `blr x8`, ghi DONE rồi mới gọi `usb_core_do_transfer`. Host chờ **cả thực thi AES và hoàn tất USB**, không chỉ sao chép 64 byte. `x7` được đọc từ đầu payload data do layout dành 7 tham số AES; cách đóng gói tương tự [usbexec.aes](https://github.com/axi0mX/ipwndfu/blob/master/usbexec.py). Chỉ khởi tạo `exec_cmd.x[7]=0` không sửa thanh ghi này, vì phần tử đó không được gửi. Chưa có lý do coi đây là nguyên nhân lỗi.

Đã kiểm tra trực tiếp trailer constants của cả 5 `.bin` khớp `.set` trong `.S`; các LDR literal ARM64 trỏ đúng slot. notA9 dài 216, handler ARM64 dài 248 byte, địa chỉ đích tính được `0x1800e0f08`, entry `+0xC = 0x1800e0f14`. Kiểm tra này xác nhận layout và literal references, không thay thế việc assemble lại rồi so toàn bộ mã máy.

### 6.2 Phát hiện ưu tiên: địa chỉ callback reset A8/A8X cũ

| CPID | Local | Upstream sửa |
|---|---|---|
| 0x7000 A8 | `0x1800888A8` | `0x180088898` |
| 0x7001 A8X | `0x180088E28` | `0x180088E18` |

Đây là thay đổi rõ ràng trong [commit upstream 7fffffff38a1bed1cdc1c5bae0df70f14395129b, ngày 02-02-2023](https://github.com/0x7ff/gaster/commit/7fffffff38a1bed1cdc1c5bae0df70f14395129b). Không phải địa chỉ mới được suy đoán từ model iPhone.

[payload_notA9.S:34](/home/ubuntu/gaster/payload_notA9.S:34) load địa chỉ `dfu_handle_bus_reset` rồi `str xzr, [x2]`. Với bản local, số 0 được ghi lệch 16 byte so với slot upstream muốn vô hiệu hóa. Sau stage patch, [gaster_checkm8:1285](/home/ubuntu/gaster/gaster.c:1285) gọi USB reset. **Giả thuyết ưu tiên:** callback thật chưa bị vô hiệu hóa, trạng thái DFU/lệnh bị xử lý lại sau reset; marker PWND vẫn có thể tồn tại dù RPC không hoạt động. Chưa có dump SecureROM hoặc trace callback để xác nhận tác động chính xác của slot bị ghi nhầm.

Đề xuất [01-a8-reset-callback.proposed.patch](/home/ubuntu/ios13-analysis/01-a8-reset-callback.proposed.patch): chỉ hai hằng số trên. Chưa áp dụng. Các hằng số được C chèn vào payload lúc chạy, nên thay đổi này cần rebuild host binary, không cần sửa hay assemble lại `.S`. Patch không thể sửa payload đã ở RAM của lần pwn trước; thử đúng phải bắt đầu bằng một phiên DFU mới được phê duyệt.

### 6.3 Timeout dùng chung 5 ms

[main:1648](/home/ubuntu/gaster/gaster.c:1648) mặc định `usb_timeout=5`; [wrapper:227](/home/ubuntu/gaster/gaster.c:227) truyền thẳng vào libusb. Theo [libusb synchronous I/O](https://libusb.sourceforge.io/api-1.0/group__libusb__syncio.html), đơn vị là ms và `LIBUSB_ERROR_TIMEOUT` chỉ báo transfer không hoàn tất trong hạn. Không chứng minh AES bị sai khóa, crash hay cáp hỏng. Tài liệu không cho phép suy ra AES A8 chắc chắn cần hơn 5 ms; đây vẫn là giả thuyết cần đo. usbexec gốc dùng CMD_TIMEOUT 5000 ms cho giao thức lệnh, là tham chiếu thiết kế chứ không phải số đo A8.

Đề xuất [02-command-timeout.proposed.patch](/home/ubuntu/ios13-analysis/02-command-timeout.proposed.patch): chỉ synchronous request `A1/02, value=FFFF, index=0` có thời hạn ít nhất 5000 ms, giữ nguyên timeout khai thác/cancel async. Đồng bộ ý nghĩa ở cả libusb và IOKit. Giữ cấu hình lớn hơn 5000 nếu đã đặt. Đây là bản vá tối thiểu để tách thí nghiệm; có thể chuyển thành tham số API/biến cấu hình riêng khi triển khai chính thức.

Không tăng toàn bộ `USB_TIMEOUT` làm bản sửa cuối cùng: biến này còn chi phối cửa sổ abort và phép modulo trong exploit. Giá trị 0 còn gây chia dư cho 0 ở checkm8_stall/setup, dù libusb định nghĩa timeout 0 là vô hạn. Cần kiểm tra dải biến môi trường riêng khi được phép sửa source.

### 6.4 Lỗi USB che khuất chẩn đoán

- Synchronous wrapper luôn trả `true`; mã -7 bị gộp thành USB_TRANSFER_ERROR; `sz` không được gán khi ret âm. Hiện `gaster_command` kiểm tra `ret` trước `sz`, nên không được quy lỗi KBAG trực tiếp cho đọc `sz` chưa khởi tạo ở callsite này.
- Một số callsite stage patch truyền transfer_ret=NULL, vì vậy chỉ thấy `true` ngay cả khi transfer thất bại. Không đổi global thành `return ret>=0` một cách máy móc: STALL và một số lỗi ở stage khai thác là chủ ý.
- Async wrapper có thể free buffer/transfer khi event handling lỗi trước callback hoàn tất. Libusb coi free transfer đang active là undefined behavior; cancel cũng là bất đồng bộ. [Nguồn libusb](https://libusb.sourceforge.io/api-1.0/group__libusb__asyncio.html). Đây là lỗi robustness trước giai đoạn command, chưa phải bằng chứng nguồn gốc timeout synchronous.
- `wait_usb_handle` mở lại chỉ theo VID/PID; gaster_command không đối chiếu ECID/SRTG/PWND. Với nhiều thiết bị hoặc re-enumeration có thể dùng sai phiên. Chưa có bằng chứng điều đó xảy ra ở đây.
- `PWND:[checkm8]` là kiểm tra chuỗi, không có version/capability handshake. Handler từ một công cụ khác có thể không tương thích; `pwn` thành công không chứng minh AES RPC.
- IOKit cũng dùng timeout chung và báo lỗi gộp, nhưng `-7` là giá trị ở nhánh libusb, không phải mã IOKit gốc.
- `Makefile` build host bằng header sinh từ `.bin`; sửa `.S` mà không regenerate `.bin` sẽ không đổi payload thực tế. Không chạy `make payload` hoặc build trong phiên này. Chưa có compiler/toolchain để xác nhận compile các đề xuất.

Nâng cấp chẩn đoán cần làm sau khi được cho phép: lưu raw libusb result, khởi tạo status/sz, đo elapsed monotonic, ghi setup packet/timeout/length và DFU status transitions, không ghi khóa giải mã; giữ rõ semantics expected stall/cancel. Thêm probe RPC không AES (ví dụ MEMC zero-length với DONE_MAGIC) và chỉ chấp nhận đúng thiết bị, không tự chạy exploit nếu không pwned. Không đổi callback, timeout và protocol cùng một thí nghiệm.

### 6.5 Phép thử phân biệt nguyên nhân, chưa chạy

| Thử | Chỉ thay đổi | Kết quả phân biệt |
|---|---|---|
| T0 | Dùng log lỗi hiện có làm baseline, xác minh hash binary | Tránh lặp thử chỉ để tái hiện -7 |
| T1 | Patch reset, timeout vẫn 5 ms, phiên DFU/pwn mới | Nếu RPC/AES hết lỗi, ủng hộ callback; không chứng minh timeout luôn đủ |
| T2 | Timeout command 5000 ms, chưa đổi reset | Nếu hết lỗi mà T1 vẫn lỗi, ủng hộ deadline; phép thử phải dùng phiên pwn tương đương |
| T3 | Hai patch, kèm probe không AES trước | Nếu probe chạy nhưng AES timeout, khoanh vùng AES/hardware/ROM ABI; nếu probe cũng lỗi, điều tra handler/reset/staging/USB |
| T4 | Có response | Kiểm tra đủ 64 byte, DONE_MAGIC, retval=0; giải mã iBSS offline và kiểm tra cấu trúc/chuỗi/version/entry để loại dữ liệu rác |

Sau timeout không tự retry command hoặc re-pwn vô hạn: payload có thể đã chạy và đang có trạng thái khác. Mỗi lần thử phải có trạng thái đầu, giới hạn thời gian, log và một thay đổi kiểm soát được.

## 7. Công trình trước và công cụ thay thế

- [Gaster upstream](https://github.com/0x7ff/gaster/commit/7fffffff38a1bed1cdc1c5bae0df70f14395129b): nguồn sửa callback trực tiếp, ưu tiên cherry-pick thay đổi nhỏ thay vì thay toàn bộ exploit.
- [Bản vá ipwndfu A8/A9 của a1exdandy](https://gist.github.com/a1exdandy/ae3fb332efac879e97a41291f7fef727): có config t7000/1992 và AES `0x10000DA90`. Là ứng viên độc lập để kiểm tra; chưa xác nhận chạy được trên host hiện tại. [ipwndfu gốc](https://github.com/axi0mX/ipwndfu) vẫn liệt kê t7000 ở future support, không được khuyên dùng master như đã có A8 đầy đủ.
- [ipwnder_lite README](https://github.com/dora2ios/ipwnder_lite): bảng hỗ trợ không liệt kê A8; không coi nó là phương án A8 đã có tài liệu xác nhận.
- [PongoOS t7000.c](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/drivers/plat/t7000.c), [stage3.c](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/boot/stage3.c): hữu ích về nền tảng A8 và handoff, không phải bằng chứng port N61/13.7.
- [iBoot64Patcher](https://github.com/tihmstar/iBoot64Patcher/blob/ad4716a52ba87fcab5579b27f1df7d33a2f000fd/iBoot64Patcher/main.cpp): signature/debug/boot-args patchfinder là khởi điểm cho loader. Không chứng minh auto-patch đúng 5540.140.12 hay board adaptation; mọi patch phải báo đúng một match, kiểm tra trước/sau.
- [Kernel64Patcher](https://github.com/iSuns9/Kernel64Patcher/blob/54bb8149b243361483694e4973d5d32dbc6f8558/Kernel64Patcher.c): có các patch AMFI và firmware validation, không cung cấp driver PMU/display N61 hay giải pháp SEP tương thích.
- [seprmvr64](https://github.com/mineek/seprmvr64), [patch_sep](https://github.com/mineek/seprmvr64/blob/e9883cb926369c481b05d56b4418f1d871a39d7f/src/seprmvr64.c): sửa kernel/kext để né một số đường lỗi SEP/keystore/biometric. README tự nêu mất passcode/TouchID và caveat; không phải tạo sepOS mới hoặc bảo đảm iOS13 tương thích SEP12 trên N61. Guide tạo APFS volume/ghi dữ liệu, không dùng nguyên script trong phạm vi nhiệm vụ này.
- [SundanceInH2A](https://github.com/NyanSatan/SundanceInH2A): ví dụ có công cụ/DT/kernel/iBoot adaptation cho port iOS đời khác. Chứng minh loại công việc có thể làm, không chuyển nguyên patch ARM32 sang A8.
- [DoritoYT9/iOS13-A8](https://github.com/DoritoYT9/iOS13-A8/tree/71ac3be0009231384216a68e38e59c934d974d85): tác giả công bố đã boot Darwin19. Snapshot đã kiểm tra chỉ có README và ảnh logo, chưa có patch, boot log hay implementation tái lập; vì vậy xếp là tuyên bố chưa kiểm chứng. `irecovery -q` không đủ chứng minh kernel đang chạy: [print_device_info](https://github.com/libimobiledevice/libirecovery/blob/master/tools/irecovery.c#L147) in thông tin DFU/recovery, không lấy uname từ kernel.

Các tin mạng xã hội gần đây về N56AP/iPhone 6 Plus là hướng tìm thêm bằng chứng, không được dùng làm xác nhận N61AP hoặc làm nguồn offset/driver. Trong các nguồn đã kiểm tra chưa tìm được quy trình N61AP/13.7 có đủ artefact và log để tái lập độc lập.

Khả năng khác để bỏ chặn giải mã bootloader: nếu có IV/key công khai đúng hash/build, có thể giải AES-CBC offline rồi kiểm chứng binary. Chưa tra được bộ khóa với nguồn và định danh đủ chắc chắn trong phiên này; không dùng khóa thiết bị/build khác hoặc yêu cầu giải mã lại kernel/DT vốn đã rõ.

## 8. Kiến trúc thí nghiệm nhỏ nhất

Mốc A là một loader/monitor N61 trong RAM với USB console/serial đã kiểm chứng. Mốc B là kernel19 thực thi checkpoint sớm **trước `StartIOKit`**, ghi nonce và marker riêng từ control flow kernel rồi dừng có kiểm soát. Mốc C mới là IOKit + RAMDisk + init chẩn đoán với `uname`/sysctl kernel version và telemetry. Mốc C không cần SpringBoard, touch, baseband hay mount hệ thống đang cài.

```text
host lưu hash/log
   → DFU payload đã kiểm tra callback và RPC
   → iBSS/iBEC N61 trong RAM, không saveenv/flash/restore
   → handoff ARM64 + RAM map/framebuffer thực + DT N61 có sửa có kiểm soát
   → kernel T7000 13.7 + early instrumentation có patch manifest
   → checkpoint trước IOKit [mục tiêu đầu]
   → chỉ sau audit: RAMDisk nhỏ, init chẩn đoán, không mount physical storage
```

Kênh chứng minh phải được chọn trước: serial nếu có cáp và pinout đã xác minh; hoặc framebuffer N61 do native loader khởi tạo; hoặc instrumentation ghi một vùng RAM được monitor đọc bằng cơ chế handoff/return đã thiết kế. Không giả định host đọc được RAM khi kernel đã chiếm USB, cũng không coi Apple logo/USB disconnect là thành công. Một chuỗi Darwin nằm trong file hoặc in từ loader không đủ; cần marker gắn nonce và vị trí thực thi, tiếp theo là log kernel hoặc uname từ userland RAMDisk.

Cần đo budget resident: kernel khoảng 33 MiB chưa tính các vùng VM/zero-fill, RAMDisk sau giải nén, loader, DT và bộ nhớ runtime. Bắt đầu RAMDisk tối thiểu, không nạp rootfs iPad nguyên khối: ảnh OS trong ZIP khoảng 3,49 GB, có UDIF trailer `koly`; `Restore.plist` mô tả ảnh system là HFS+. Điều đó không xác định định dạng volume trên máy hoặc việc nó có thể mount với kernel thử nghiệm. Manifest có static/restore trust cache, restore RAMDisk khoảng 104–107 MB, nhưng không boot restore RAMDisk có sẵn khi chưa audit các dịch vụ tự động.

AMFI/trust cache: dùng tập binary nhỏ cùng build/arch và chữ ký/entitlements phù hợp; kiểm tra CDHash của binary đã sửa, trust cache iPad không mặc nhiên tin binary thay đổi. Chỉ patch mức tối thiểu cần cho ramdisk. Chưa cần dựng toàn bộ iPhone userland.

SEP: không gửi SEP image và không động firmware SEP trên NAND. Không gửi firmware SEP của J96 để thử xem có chạy hay không. Nếu kernel đợi SEP, đó là blocker để nghiên cứu đường chờ và chỉ sửa AP kernel trong RAM. Một flag DeviceTree như `no-sepfw-load-at-boot` không được coi là có hiệu lực nếu chưa kiểm tra consumer. Không đụng dữ liệu keybag đang cài và không hứa mở khóa data volume bằng cách bỏ SEP.

**Giới hạn an toàn:** tải ảnh vào RAM không tự bảo đảm không có ghi NAND. Bootloader có thể lưu môi trường; kernel có NVRAM/paniclog/storage personalities. Mốc B phải dừng trước driver init, audit phần chạy trước checkpoint và đường lưu panic; mốc C chỉ được đề xuất sau khi audit được các đường physical storage/SEP/NVRAM và cơ chế chặn ghi. Không gắn nhãn “không rủi ro” cho một boot kernel tùy biến.

## 9. Kế hoạch triển khai và các cổng kiểm chứng

| Bước | Công việc | Đầu ra / điều kiện qua |
|---|---|---|
| S0 — đã làm | Kiểm kê, hash thành phần, parse IMG4/DT/Mach-O, giải LZSS đối chiếu, đọc source Gaster và dự án liên quan | evidence.json và báo cáo này; không thiết bị |
| S1 — cần cho phép sửa source | Áp dụng riêng patch callback vào bản thử, chuẩn bị binary baseline/reset-only/timeout-only; thêm diagnostics và require-pwned guard nếu được duyệt | Build có provenance; so diff; không chạy binary vào USB |
| S2 — offline | Lấy các thành phần N61 cần thiết từ nguồn đã có hoặc tải riêng thành phần nhỏ; giải mã và audit loader; kiểm tra binary iBSS/iBEC iPad nếu cần | Hash/build/board rõ, entry/DRAM/board paths hiểu được; mỗi patchfinder đúng một match |
| S3 — cần duyệt thiết bị riêng | Xác minh đúng một ECID/CPID/SRTG; đo RPC và AES với test matrix | DONE_MAGIC/retval/length đúng; bootloader giải mã offline có cấu trúc hợp lý |
| S4 — chuẩn bị offline | Native N61 loader + DT nhị phân, memory layout, kênh log, marker trước IOKit, patch manifest | Không overlap, đúng entry/boot_args, có bằng chứng chặn trước storage và không lưu trạng thái bền vững |
| S5 — cần duyệt chính xác command+hash | Boot monitor/native loader trong RAM và thử checkpoint kernel19 | Marker nonce từ vị trí kernel, log/ảnh đầy đủ; dừng trước IOKit, thử recovery |
| S6 — chưa sẵn sàng | Adapt D2186/platform, RAMDisk/init không ghi storage; kiểm chứng USB/log | uname Darwin19 + log root RAMDisk; không coi panic patch thành công là driver hoạt động |
| S7 — ngoài thử đầu | ABI port display/touch, storage read-only được chứng minh, SEP/userland/memory | Chỉ mở rộng theo kết quả thực tế; mọi thay đổi chính sách NAND cần nhiệm vụ/phê duyệt riêng |

Các phép kiểm tra offline khi được sửa source: patch callback phải đổi đúng hai giá trị và không làm đổi pool layout; mock USB xác nhận A1/02/FFFF có >=5000ms, exploit/async vẫn 5ms; errors/short transfers được báo đúng; unrecognized serial không dùng cấu hình CPID cũ; reject USB_TIMEOUT=0. Không có kiểm tra offline nào thay thế thử hardware cho thời gian AES hoặc tính đúng của địa chỉ ROM.

## 10. Rủi ro, phục hồi và điểm dừng

| Rủi ro | Cách giảm trong thiết kế | Phục hồi / điểm dừng |
|---|---|---|
| Treo / màn hình đen / mất USB | Deadline ngoài host và telemetry đã có baseline; không retry vô hạn | Force restart iPhone6 bằng giữ Home + nút nguồn/cạnh đến logo Apple; boot bình thường iOS12 nếu không có thay đổi bền vững |
| Recovery/DFU còn lại | Không saveenv, không chỉnh auto-boot/NVRAM | Dừng gửi lệnh; xác định mode sau khi được duyệt. Không tự restore. Nếu reboot thường không về iOS12, báo trước khi làm tiếp |
| Ghi NAND ngoài ý muốn | Audit loader, early stop trước IOKit, không boot restored/partitioning scripts; mốc sau có chặn ghi và test riêng | Không giả định force restart đảo ngược dữ liệu đã ghi; loại thử nghiệm nếu chưa chứng minh được giới hạn |
| PMU / nhiệt / nguồn | Không giả D2186 thành D2207, giữ native init, phiên thử ngắn | Dừng ngay khi nóng bất thường hoặc nguồn không ổn định; không tiếp tục bằng ép driver match |
| SEP / dữ liệu / TouchID | Không nạp sepOS khác, không mount data, không copy keybags, không restore | Dừng ở lỗi SEP; không thay firmware để chữa bằng thử-sai |
| Thiếu RAM / driver / userland | Kernel checkpoint rồi ramdisk nhỏ; không rootfs nguyên khối, không mặc định 2GiB | Thu log, giảm phạm vi, không kết luận CPU bất tương thích chỉ từ OOM |

Force restart chỉ là phương án thoát RAM payload, không là bảo đảm phục hồi mọi hậu quả nếu một chương trình đã ghi flash. Trong ràng buộc hiện tại không có phương án “thử rồi restore nếu hỏng”.

## 11. Các bước tiếp theo cần phê duyệt

**Đề xuất xin phép trước hết chỉ cho phần offline S1:** áp dụng hai tệp diff đã chuẩn bị vào bản thử được chọn, thêm diagnostic/protocol guard nhỏ và build các biến thể độc lập. Lý do cần phép: người dùng đã yêu cầu không sửa mã nguồn trước khi cho phép. Không cần cấp quyền thử thiết bị kèm theo quyền sửa source.

Hai đề xuất diff có thể xem ngay; kiểm tra `git apply --check` không áp dụng chúng. Nếu công cụ build thiếu, sẽ phải duyệt riêng lệnh cài dependency đặc quyền trước khi chạy. Không tự chạy `sudo`.

**Một phép thử thiết bị timeout hiện hữu có command cụ thể**, chỉ để người dùng xem xét, **chưa thực hiện và không phải lựa chọn ưu tiên trước khi sửa guard/diagnostics**:

```bash
env USB_TIMEOUT=5000 /home/ubuntu/gaster/gaster decrypt_kbag 5beea1963ffa43cdfc6f096160426d82d653f3ae427a767ed45766998e760108f80c2406305550efe28f5f85961b162e
```

Chuỗi trên được trích từ KBAG type1 iBSS.ipad5 17H35 tại chỗ; là KBAG firmware được bọc, không phải passcode/data-volume keybag. Command này đặt timeout **toàn cục**, nên nếu marker PWND không còn, CLI còn tự chạy checkm8; không được mô tả là một USB read thuần túy. Nó không cài patch callback vào payload đã pwn. Do những hạn chế đó, ưu tiên chuẩn bị binary chẩn đoán có guard rồi trình command/hash của binary ấy để duyệt từng lần. Không chạy lại lệnh này sau timeout mà chưa xác định trạng thái.

Chưa có đủ artifact để trình một chuỗi `irecovery -f ...; bootx` có thể duyệt có trách nhiệm: thiếu native N61 loader bản rõ, DT N61 nhị phân có provenance, patch manifest, entry/handoff audit và kênh bằng chứng. Tên ảnh giả hoặc một command với placeholder sẽ không phải một thí nghiệm đã sẵn sàng. Sau S1/S2/S4, phải trình chính xác từng file SHA-256, ECID đích, command, kết quả mong đợi, timeout và quy trình quay lại iOS12; chỉ chạy khi được duyệt.

Không có đề xuất phê duyệt repartition, restore, flash SEP/baseband hoặc thay đổi Windows/BitLocker/USB boot trong kế hoạch này.
