# Các demo

Demo cục bộ phải pass nằm trong `tests/api`, `tests/ui` và `tests/integration`.

Demo lỗi có kiểm soát bị loại khỏi collection mặc định. Chạy riêng demo này để kiểm tra
logging, screenshot, page source, failure report và khả năng bảo toàn assertion gốc:

```bash
python -m pytest demos/controlled_failure/test_ui_failure.py -q
```

Exit code `1` là kết quả mong đợi. Thư mục mới nhất trong `artifacts/runs/` phải có
`logs/run.log`, `logs/run.jsonl`, một file PNG trong `screenshots/`, page source
HTML, `reports/summary.json` và `manifest.json` ghi nhận một test thất bại.
