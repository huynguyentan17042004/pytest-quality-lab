# Kiểm thử property-based

Hypothesis tự sinh dữ liệu để kiểm tra các invariant mà bảng CSV, JSON, YAML hoặc XLSX
khó bao phủ hết. Test dùng marker `property`, giới hạn `max_examples` và bật
`derandomize=True` để kết quả trên CI có thể tái lập.

Các property hiện có xác minh:

- Danh sách `case_id` duy nhất luôn được validator chấp nhận.
- Secret hợp lệ sau khi đăng ký không bao giờ còn xuất hiện trong diagnostic đã redaction.
- Mọi tổ hợp biến `QA_PROP_*` đều được phục hồi sau scope cô lập.

Strategy phải sinh dữ liệu phù hợp boundary thật của hệ điều hành và domain; ví dụ,
giá trị biến môi trường loại bỏ NUL và surrogate. Hypothesis tìm counterexample nhỏ
nhất cho property, nhưng không thay thế test case nghiệp vụ có expected result cụ thể.

```bash
python -m pytest tests/framework/property -q
python -m pytest -m property -q
```
