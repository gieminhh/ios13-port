# Phạm vi sử dụng được người dùng ưu tiên — 31-10-2026 UTC

Người dùng chấp nhận bỏ di động/baseband, Touch ID và chức năng SEP nếu có thể, ưu tiên iOS 13 sử dụng bình thường. Đây là điều chỉnh mục tiêu tính năng; không phải phê duyệt sửa source, gửi lệnh đến iPhone hoặc thay đổi NAND.

Mục tiêu đích được diễn giải là một thiết bị iOS 13 dùng qua Wi-Fi. Boot kernel/ramdisk vẫn là cổng kiểm chứng trung gian, không được tính là hệ thống đã dùng được.

| Hạng mục | Tiêu chí |
|---|---|
| Có thể loại khỏi mục tiêu | SIM, cuộc gọi, SMS, dữ liệu di động, Touch ID; không yêu cầu passcode/Apple Pay trong bản thí nghiệm |
| Phải có để gọi là dùng được | SpringBoard và hiển thị đúng; cảm ứng N61; Wi-Fi có mã hóa với kết nối ổn định; Safari và một số ứng dụng tương thích iOS 13; quản lý nguồn/nhiệt ổn định |
| Cần kiểm chứng bổ sung | Âm thanh, sleep/wake, sạc, khả năng lưu cấu hình/dữ liệu của môi trường thử, Bluetooth/camera nếu sau này được ưu tiên |
| Không mặc nhiên bảo đảm | App Store/Apple ID, Keychain và mọi ứng dụng phụ thuộc dịch vụ bảo mật/SEP; không tuyên bố hoạt động nếu chỉ vào được màn hình chính |

Bỏ cellular/Touch ID làm giảm phạm vi driver và dịch vụ phải hỗ trợ. Tuy nhiên bỏ SEP toàn bộ không chỉ tắt sinh trắc học. README seprmvr64 báo cả passcode/Touch ID hỏng và mạng Wi-Fi mã hóa từ chối mật khẩu: https://github.com/mineek/seprmvr64#caveats . Đây là hạn chế của PoC đó, không phải kết luận mọi cách xử lý SEP đều mất Wi-Fi hoặc không thể sửa. Vì người dùng muốn dùng bình thường qua Wi-Fi, không chọn cách bypass hàng loạt ấy làm phương án mặc định.

Hướng nghiên cứu cập nhật: để baseband và Touch ID ngoài đường thành công; bảo toàn dịch vụ SEP có thể hoạt động, tìm đúng đường SEP đang chặn boot rồi chỉ sửa AP kernel/userland cần thiết trong RAM. Chỉ xem xét shim/fallback keystore khi hiểu giao thức và có phép thử cụ thể; chưa có implementation được kiểm chứng cho N61/13.7. Không giả định firmware SEP12 tương thích kernel13 và không gửi firmware SEP của iPad.

Các blocker vẫn giữ nguyên: loader/handoff, PMU D2186, màn hình Pinot/Chestnut, cảm ứng N61, storage và ABI kernel/kext. Hai patch Gaster là bước mở khóa thí nghiệm, không tự khắc phục các blocker đó.

Cổng kiểm chứng sau khi boot kernel: (1) root RAMDisk và log; (2) UI/hiển thị/cảm ứng; (3) Wi-Fi mã hóa, TLS trong Safari, kiểm tra các lỗi keystore; (4) app tương thích, nguồn/nhiệt, sleep/wake; (5) thiết kế lưu dữ liệu được phê duyệt. Trong giới hạn không ghi NAND hiện tại, chưa thể hứa một cài đặt dùng hằng ngày có dữ liệu bền vững; giai đoạn RAM không được coi là đã đáp ứng điều đó.

Các giới hạn bảo vệ iOS12, không flash/restore/SEP/baseband và phê duyệt trước thử hardware tiếp tục áp dụng.

Cập nhật sau đó: người dùng đã cho phép sửa/build Gaster offline; bước này đã hoàn tất, xem [kết quả](/home/ubuntu/ios13-analysis/build-status.vi.md). Chưa chạy lệnh lên iPhone.
