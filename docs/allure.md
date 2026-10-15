# Allure 3 integration

SQLite dashboard là nguồn lịch sử local có thể query và không cần Node.js. Allure là
lớp report tùy chọn để có giao diện chi tiết, retries, history và trend charts mà không
tự viết lại reporting engine.

Pytest adapter ghi raw result:

```bash
python -m pytest tests/framework -q --alluredir=artifacts/allure-results
```

`allurerc.json` cấu hình report output và một file history JSONL bền vững. Khi đã có
Allure 3 CLI, tạo report bằng:

```bash
npx allure generate artifacts/allure-results
```

Không cần Allure CLI để chạy test, ghi SQLite hoặc xem dashboard local. CI luôn upload
`artifacts/allure-results/`, nhờ đó report có thể được dựng ở bước publish riêng.
