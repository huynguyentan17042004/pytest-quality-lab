# Kiến trúc framework

## Mục tiêu

Kiến trúc tách phần dùng chung của framework khỏi logic của ứng dụng được kiểm thử.
Nhờ đó, API client, Page Object và dữ liệu nghiệp vụ của một sản phẩm không làm thay
đổi lõi logging, configuration, reporting hoặc pytest plugin.

Hướng phụ thuộc bắt buộc:

```text
tests -> tests/support -> qa_framework -> thư viện bên ngoài
```

`src/qa_framework/` không được import module thuộc `tests/support/`. Mỗi lớp có trách
nhiệm riêng:

- `config/`: đọc TOML, áp dụng biến môi trường và CLI override.
- `api/`: HTTP transport, retry có giới hạn, schema validation và logging an toàn.
- `ui/`: tạo WebDriver và cung cấp các thao tác Page Object tối thiểu.
- `data/`: đọc, kiểm tra và chuẩn hóa CSV, JSON, YAML, XLSX.
- `logging/`: structured log, redaction và traceback.
- `reporting/`: artifact theo từng lần chạy, SQLite analytics và dashboard.
- `pytest_plugin.py`: nối các thành phần vào vòng đời pytest.

## Luồng thực thi

1. Pytest plugin đọc cấu hình và tạo `run_id`.
2. Fixture khởi tạo API client, WebDriver hoặc dữ liệu theo nhu cầu của test.
3. Test thực thi assertion nghiệp vụ; framework ghi log có context.
4. Khi thất bại, hook giữ nguyên exception gốc rồi cố gắng thu thập artifact hỗ trợ.
5. Cuối session, kết quả được ghi vào SQLite và dashboard được tạo lại.

## Ranh giới kiểm thử

`tests/framework/` xác minh hành vi của framework bằng unit test hoặc fixture localhost
có kiểm soát. Các demo gọi dịch vụ công khai được tách riêng, đánh marker `external`
và chỉ chạy khi người dùng truyền `--run-external`.
