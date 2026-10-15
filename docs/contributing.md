# Đóng góp cho dự án

## Chuẩn bị môi trường

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,allure]'
```

## Nguyên tắc thay đổi

- Mỗi component mới của framework phải có self-test tương ứng.
- Giữ hướng phụ thuộc `tests -> tests/support -> qa_framework`.
- Không thêm public traffic vào lần chạy mặc định.
- Không log credential, token, cookie hoặc dữ liệu cá nhân.
- Cập nhật tài liệu và test khi thay đổi public API, flag hoặc configuration.
- Cập nhật `DESIGN.md` hoặc ADR khi thay đổi boundary, cost policy hay phạm vi.

## Kiểm tra trước khi commit

```bash
python -m ruff check .
python -m mypy src
python -m pytest -q
python -m pytest --collect-only -q
```

Chỉ chạy demo bên ngoài sau khi các bước cục bộ pass và bạn chủ động cho phép bằng
`--run-external`. Pull request nên mô tả phạm vi thay đổi, bằng chứng kiểm thử và mọi
rủi ro còn lại.
