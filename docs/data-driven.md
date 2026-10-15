# Kiểm thử hướng dữ liệu

`DataLoader` đọc CSV, JSON, YAML và XLSX qua cùng một public API. Dữ liệu được chuẩn
hóa thành record, kiểm tra trường bắt buộc và bảo đảm `case_id` là duy nhất ngay trong
giai đoạn pytest collection.

## Hai giai đoạn xử lý

1. **Collection time:** đọc file, kiểm tra schema và tạo danh sách test case. Placeholder
   dạng `${VARIABLE}` vẫn được giữ nguyên để không làm lộ hoặc đóng băng secret.
2. **Runtime:** fixture resolve placeholder từ môi trường, bọc giá trị nhạy cảm bằng
   `SecretValue` và đăng ký với redaction filter trước khi ghi log.

Một bảng dữ liệu nên có tối thiểu:

- `case_id`: định danh ổn định và duy nhất.
- Input của hành vi được kiểm thử.
- Expected result có thể assert rõ ràng.
- `requirement_id` nếu test tham gia tính coverage.

Property-based test bằng Hypothesis bổ sung độ bao phủ invariant và trường hợp biên,
nhưng không thay thế business case có expected result cụ thể; xem
[property-based testing](property-based-testing.md).

Khi test thay đổi biến môi trường, dùng `isolated_env` hoặc `EnvironmentSandbox` để
mọi giá trị được phục hồi sau scope, kể cả khi test thất bại.
