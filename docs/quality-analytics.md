# Phân tích chất lượng

Sau mỗi pytest session, plugin ghi kết quả cuối cùng của từng test vào
`artifacts/analytics/quality.db`, rồi tạo lại
`artifacts/analytics/dashboard.html`. SQLite dùng transaction, WAL mode, busy timeout
và khóa duy nhất `(run_id, nodeid)`.

## Chỉ số trên dashboard

- **Tỷ lệ thành công:** tính trên `passed + failed` của lần chạy mới nhất; intentional
  skip không bị xem là failure.
- **Tỷ lệ flaky:** tỷ lệ test từng có cả trạng thái `passed` và `failed` trong lịch
  sử đang lưu.
- **Thời gian thực thi:** tổng duration cuối cùng của các test trong lần chạy mới nhất.
- **Độ bao phủ requirement:** số requirement ID khác nhau đã chạy trên tổng catalog
  `configs/requirements.yaml`.
- **Lịch sử:** bảng các lần chạy, flaky candidate và failure theo fingerprint.

## Lưu lỗi an toàn

Failure fingerprint là SHA-256 rút gọn từ loại lỗi và thông báo đã chuẩn hóa. Traceback
đã redaction được lưu tối đa 12.000 ký tự; thông báo lỗi tối đa 4.000 ký tự. Các biến
môi trường có tên nhạy cảm như password, token, secret, key hoặc cookie được đăng ký
với bộ lọc ngay đầu session. Database không lưu secret thô.

## Điều khiển từ terminal

Tắt analytics cho một lần chạy:

```bash
python -m pytest -q --no-analytics
```

Đổi vị trí database:

```bash
python -m pytest -q --analytics-db=/path/to/quality.db
```

Tạo lại dashboard từ lịch sử hiện có:

```bash
qa-dashboard --db artifacts/analytics/quality.db \
  --output artifacts/analytics/dashboard.html \
  --requirements configs/requirements.yaml
```

`--collect-only` không tạo bản ghi analytics vì chưa có test nào thực thi. Chạy
`demos/controlled_failure/` để kiểm tra traceback, browser artifact và failure
history; exit code `1` là kết quả mong đợi của demo này.
