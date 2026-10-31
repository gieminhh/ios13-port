# Cổng boot RAM và kế hoạch ghi/khôi phục

Ngày 31-10-2026 UTC: **chưa đủ điều kiện boot thử kernel iOS13 hoặc flash**.
Đã xác minh danh tính N61/PWND thật, chưa xác minh RPC/AES. Không có chuỗi lệnh
flash iOS13 đã được kiểm chứng; không biến kế hoạch dưới đây thành script tự chạy.

## Thứ tự thử nghiệm

| Cổng | Phép thử / việc cần hoàn thành | Tiêu chí qua |
|---|---|---|
| 1. Danh tính | `gaster status`, guard 7000/06 và SRTG, GETSTATE | Đã qua ở snapshot; kiểm lại trước phiên mới |
| 2. RPC | Một `gaster probe` đã được cho phép; 40 byte MEMC và DFU framing trong RAM | DONE_MAGIC, đúng retval/16-byte reply; dừng khi lỗi, không retry/pwn/reset |
| 3. AES | Chỉ nếu RPC qua: một `decrypt_kbag_pwned` với KBAG type1 iBSS N61 16H88 đã trích | Đúng marker/retval/64-byte reply; dùng IV/key giải iBSS offline và kiểm cấu trúc ARM64 iBoot |
| 4. Loader native | Giải iBSS/iBEC N61, audit DRAM/entry/IMG4/board và handoff | Artifact + hash + patch manifest; không saveenv/flash/NVRAM |
| 5. Baseline RAM | Chuỗi loader/monitor native và kernel12 chẩn đoán | Kênh log và đường thoát RAM được thử; không mount physical storage |
| 6. Kernel19 sớm | Native N61 init → DT N61 runtime → kernel T7000 13.7 | Nonce từ control flow kernel trước StartIOKit, cùng PC/checkpoint và log |
| 7. RAMDisk19 | Driver/platform tối thiểu, init chẩn đoán và trust hợp lệ | uname Darwin19 từ RAMDisk, audit chặn storage/NVRAM/panic writes |
| 8. UI/useful | Port PMU/display/touch/Wi-Fi và dịch vụ cần thiết | SpringBoard, cảm ứng, Wi-Fi mã hóa, nhiệt/nguồn và sleep/wake ổn định |
| 9. Cài bền vững | Thiết kế storage/boot chain và recovery đã thử | Mới trình từng lệnh ghi kèm hash/phân vùng để người dùng duyệt |

PWND không chứng minh payload RPC tương thích. Timeout 5000 ms/callback đã sửa
ở host không chứng minh lỗi AES đã hết hoặc payload hiện tại đã có callback mới.
Nếu RPC/AES lỗi, lưu log rồi dừng; không tự thêm lần thử hoặc reset.

## Thiết kế RAM cần xây

```text
host: kiểm hash/identity, deadline và log
  → phiên DFU/RPC đã kiểm chứng
  → loader N61 đã audit, chỉ nạp RAM
  → DRAM/framebuffer/DT runtime thực của N61
  → handoff boot_args, MMU/cache và kernel19 đúng địa chỉ
  → marker nonce trước StartIOKit, rồi dừng có kiểm soát
  → sau audit riêng: RAMDisk + init chẩn đoán không ghi storage
```

Phải có memory layout chứa loader, kernel, các segment zero-fill, DT, ramdisk,
framebuffer và vùng log mà không overlap; dùng RAM thực N61, không giả định RAM
iPad. Kernel13 hiện có dài 34684928 byte trước tính resident VM/runtime. Không
đưa rootfs iPad khoảng 3,49 GB nguyên khối vào RAM iPhone6.

Kênh chứng minh có thể là serial đã xác minh hoặc framebuffer native còn hợp lệ.
Nếu dùng vùng RAM chứa marker phải có cách đọc sau handoff đã thiết kế; không
giả định DFU USB vẫn sống khi kernel chiếm USB. Apple logo, USB disconnect hay
chuỗi Darwin in từ loader không chứng minh kernel đã thực thi.

Chưa thể chốt các lệnh như `irecovery -f ...`, `devicetree`, `ramdisk`, `bootx`:
loader/artifact, định dạng ảnh, entry, trust và hành vi ghi chưa audit. Các lệnh
đó chỉ được lập thành argv cụ thể sau cổng 4–5, kèm ECID, hash, thứ tự và điểm
dừng. Không boot restore RAMDisk iPad nguyên trạng hoặc dùng
`idevicerestore --no-restore` như một chứng nhận “chỉ RAM”; nó có thể nạp các
thành phần restore khác trước khi dừng.

## Kế hoạch flash iOS13

Chưa có custom IPSW N61, layout phân vùng, patch boot chain và bộ driver dùng
được. Vì vậy hiện **không có lệnh ghi iOS13 hợp lệ để đề nghị phê duyệt**.
Chạy idevicerestore với IPSW iPad, sửa tên model trong manifest hoặc dùng
`--custom` không tự tạo được port. Phải hoàn thành các cổng RAM trước.

Hồ sơ xin duyệt ghi sau này phải có: hash tất cả ảnh, mapping ảnh → đích ghi,
boot chain khi mất điện/reboot, ranh giới SEP/baseband/NVRAM, backup dữ liệu,
giới hạn dung lượng, bằng chứng khôi phục và **toàn bộ argv thực tế**. Không
ghi SEP/baseband iPad lên N61. Không dùng `--ignore-errors` để vượt blocker.

## Khôi phục iOS12.5.8

Đã xác nhận manifest Apple của gói `iPhone_4.7_12.5.8_16H88_Restore.ipsw` chứa
iPhone7,2/N61AP, CPID7000/BDID06. Apple có phát hành 12.5.8 cho iPhone6.
[Apple security releases](https://support.apple.com/en-sa/100100).

Chỉ mục IPSW.me ngày 31-10-2026 ghi gói 16H88 đang signed; đó là metadata bên
thứ ba, **chưa phải TSS response thành công cho thiết bị này**. Phải kiểm lại
signing/TSS sát lúc restore. Gói full 3032495130 byte chưa được tải; SHA256 dự
kiến từ chỉ mục nằm trong [metadata](evidence/ios12-recovery-metadata.json),
chưa được đối chiếu full file. Chỉ tải các thành phần nhỏ không đủ để restore.

Trước thử nghiệm ghi phải chuẩn bị full IPSW Apple đúng model, kiểm hash,
không gian cho file và cache/extraction, bản sao dữ liệu đã kiểm khả năng đọc,
cáp/nguồn ổn định và thông tin Apple Account/Activation Lock nếu áp dụng. Host
ban đầu chỉ còn khoảng 2,3 GB trống, thiếu ngay cả chỗ cho full IPSW 3,03 GB;
cần phân vùng ghi được với dung lượng dự phòng. Không remount USB nghiên cứu
read-only để giải quyết việc này trong phiên hiện tại.

Lệnh restore Linux dự kiến, **chưa chạy và cần duyệt riêng**, sau khi đã có
IPSW đầy đủ, target ECID thật, phiên DFU sạch và signing phù hợp:

```text
idevicerestore --ecid <ECID-da-xac-minh> --erase \
  --cache-path <thu-muc-cache-du-dung-luong> \
  <duong-dan>/iPhone_4.7_12.5.8_16H88_Restore.ipsw
```

Đây là lệnh ghi/erase toàn máy, không phải bước kiểm tra. Cú pháp đã đối chiếu
`--help` của công cụ đang cài và [tài liệu idevicerestore](https://github.com/libimobiledevice/idevicerestore/blob/master/docs/idevicerestore.1).
Không thêm `--latest` nếu cần chốt chính xác 12.5.8; không tự chạy lệnh trên khi
thiết bị treo. Trên Mac/Windows có thể dùng Finder/Apple Devices theo
[hướng dẫn restore của Apple](https://support.apple.com/en-us/118107).

## Rủi ro và điểm dừng

- RAM payload có thể treo/mất USB. Force restart iPhone6 bằng Home + nút cạnh
  là đường thoát dự kiến khi chưa có thay đổi bền vững; không đảo ngược ghi NAND.
- Kernel/loader tải từ RAM vẫn có thể ghi storage, NVRAM hoặc paniclog. Phải audit
  đường thực thi và giới hạn driver, không dựa vào tên “RAM boot”.
- Sai driver PMU/display/charger có thể gây lỗi nguồn/nhiệt. Dừng khi có bất thường;
  không ép compatible để tiến tiếp.
- SEP/keybag/storage và restore có thể làm mất dữ liệu/khả năng mở khóa; không
  hứa khôi phục dữ liệu bằng restore. `--erase` xóa dữ liệu và cài lại firmware.
- Recovery chính thức còn phụ thuộc signing và phần cứng. DFU/PWND không bảo đảm
  cứu được mọi lỗi. Thao tác vào recovery/restore thực hiện theo
  [hướng dẫn Apple](https://support.apple.com/en-us/118106), với phê duyệt ghi riêng.
