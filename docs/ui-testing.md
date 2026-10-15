# Kiểm thử UI

`DriverFactory` là nơi duy nhất khởi tạo trình duyệt. Page Object kế thừa
`BasePage`, chỉ chứa locator và thao tác trên trang; assertion nghiệp vụ phải nằm trong
test để expected result luôn dễ đọc.

## Đồng bộ và độ ổn định

- Implicit wait luôn bằng `0`.
- Mỗi thao tác dùng explicit wait đúng với trạng thái cần quan sát: visible, clickable,
  URL thay đổi hoặc text xuất hiện.
- Không dùng `sleep()` để che race condition.
- Sau thao tác điều hướng hoặc submit, lấy lại element thay vì giữ tham chiếu đã stale.
- Test bên ngoài chỉ chạy một trình duyệt, không retry và phải bật bằng `--run-external`.

## Chẩn đoán lỗi

Khi UI test thất bại, pytest hook cố gắng lưu:

- Screenshot PNG tại `artifacts/runs/<run-id>/screenshots/`.
- Page source HTML tại `artifacts/runs/<run-id>/page_sources/`.
- Log text, JSONL và traceback đã che secret.

Nếu việc chụp artifact cũng lỗi, assertion ban đầu vẫn là nguyên nhân thất bại chính.

Chạy toàn bộ UI test cục bộ ở chế độ headless:

```bash
python -m pytest tests/ui/test_local_login_data_driven.py -q
```

Thêm `--headed --browser=chrome` để quan sát trực tiếp trên Chrome.
