# Property-based data-driven testing

Hypothesis bổ sung dữ liệu sinh tự động cho các invariant mà bảng CSV/JSON/YAML/XLSX
khó bao phủ hết. Các test dùng marker `property`, giới hạn `max_examples` và bật
`derandomize=True` để CI tái lập được.

Các property hiện có kiểm tra:

- Danh sách `case_id` duy nhất luôn được validator chấp nhận.
- Secret hợp lệ sau khi đăng ký không bao giờ còn trong diagnostic đã redaction.
- Mọi tổ hợp biến `QA_PROP_*` đều được phục hồi sau scope cô lập.

Strategy phải sinh dữ liệu hợp lệ với boundary thật của hệ điều hành và domain; ví dụ
environment value loại NUL và surrogate. Hypothesis tìm counterexample cho property,
không thay thế các example-based business case có expected result cụ thể.

```bash
python -m pytest tests/framework/property -q
python -m pytest -m property -q
```
