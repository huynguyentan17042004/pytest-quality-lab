# Chiến lược kiểm thử

Framework áp dụng nhiều tầng để phản hồi nhanh nhưng vẫn có bằng chứng end-to-end:

| Tầng | Mục đích | Phụ thuộc |
| --- | --- | --- |
| Unit | Xác minh từng component và contract lỗi | Fake/mock, không network |
| Property | Tìm trường hợp biên của invariant | Hypothesis, deterministic |
| Integration cục bộ | Kiểm tra nhiều lớp phối hợp | Localhost, HTML có kiểm soát |
| Demo bên ngoài | Xác minh tích hợp thực tế đã duyệt | Internet, opt-in |

Hai demo công khai là `DEMO-API-001` (contract API) và `DEMO-UI-001` (phân vùng tài
khoản bị khóa). `case_id` ổn định cung cấp traceability độc lập với pytest node ID.

Các demo deterministic bổ sung gồm contract posts cục bộ và expected 404, bảng CSV
positive/negative cho đăng nhập, cùng luồng health-check-to-login đi qua API và UI.
`demos/controlled_failure` bị loại khỏi collection mặc định và cố ý thất bại để chứng
minh khả năng chẩn đoán.

Nguyên tắc assertion:

- Mỗi test thể hiện rõ input, hành động và expected result.
- Wait chỉ đồng bộ trạng thái; wait không thay thế assertion.
- Negative test chủ động assert error contract thay vì coi mọi 4xx/5xx là lỗi framework.
- Requirement ID được gắn vào test để dashboard tính coverage.
