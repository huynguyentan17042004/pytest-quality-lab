# Quality analytics

Plugin ghi kết quả cuối cùng của từng test vào `artifacts/analytics/quality.db` sau
mỗi pytest session và tạo lại `artifacts/analytics/dashboard.html`. Ghi SQLite dùng
transaction, WAL mode, busy timeout và unique key `(run_id, nodeid)`.

Dashboard hiển thị:

- Pass rate của run mới nhất, tính trên `passed + failed` và không coi intentional skip
  là failure.
- Flaky rate: tỷ lệ test từng có cả kết quả `passed` và `failed` trong lịch sử đang lưu.
- Execution time: tổng duration cuối cùng của các test trong run mới nhất.
- Requirement coverage: số requirement ID khác nhau đã được chạy trên tổng catalog
  `configs/requirements.yaml`.
- Run history, flaky candidates và failure history theo fingerprint.

Failure fingerprint là SHA-256 rút gọn của loại lỗi và thông báo đã chuẩn hóa. Full
traceback đã redaction được lưu tối đa 12.000 ký tự; thông báo lỗi tối đa 4.000 ký tự.
Các giá trị từ biến môi trường có tên nhạy cảm (password/token/secret/key/cookie) được
đăng ký với bộ lọc ngay đầu session. Không ghi secret thô vào DB.

Tắt analytics cho một run bằng `--no-analytics`, hoặc đổi DB bằng
`--analytics-db=/path/to/quality.db`. Tái tạo dashboard độc lập:

`--collect-only` không tạo run analytics vì chưa có test nào được thực thi.

```bash
qa-dashboard --db artifacts/analytics/quality.db \
  --output artifacts/analytics/dashboard.html \
  --requirements configs/requirements.yaml
```

Run controlled-failure ở `demos/controlled_failure/` để kiểm tra traceback, browser
artifacts và failure history. Exit code `1` là kết quả mong đợi của demo này.
