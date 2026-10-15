# Tích hợp Allure 3

Dashboard SQLite là nguồn lịch sử cục bộ có thể truy vấn và không cần Node.js. Allure
là lớp báo cáo tùy chọn để có giao diện chi tiết, retries, history và trend chart mà
không phải tự xây lại toàn bộ reporting engine.

Pytest adapter ghi raw results bằng lệnh:

```bash
python -m pytest tests/framework -q --alluredir=artifacts/allure-results
```

`allurerc.json` cấu hình report output và file history JSONL bền vững. Khi đã cài
Allure 3 CLI, tạo report bằng:

```bash
allure generate artifacts/allure-results
```

Một số môi trường cài Allure qua npm có thể dùng:

```bash
npx allure generate artifacts/allure-results
```

Không cần Allure CLI để chạy test, ghi SQLite hoặc xem dashboard cục bộ. CI luôn upload
`artifacts/allure-results/`, vì vậy report có thể được dựng ở bước publish riêng.
