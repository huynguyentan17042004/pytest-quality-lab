# Chính sách chi phí và thực thi

Lần chạy mặc định theo nguyên tắc offline-first: ưu tiên unit test, fake/mock, localhost
API và HTML cục bộ. Test có marker `external` bị skip nếu không truyền
`--run-external`.

Allowlist chỉ gồm `DEMO-API-001` và `DEMO-UI-001`, với các giới hạn:

- Tối đa hai test case được chọn.
- Tối đa một API request cho demo API.
- Một trình duyệt headless cho demo UI.
- Không retry và không chạy song song.
- CI không chạy theo lịch; chỉ chạy thủ công.

Giới hạn này kiểm soát traffic và độ bất định, không thay thế quota hoặc chính sách
thanh toán của dịch vụ bên thứ ba. Nếu thêm endpoint bên ngoài, phải cập nhật allowlist,
test, tài liệu và quality gate trước khi sử dụng.
