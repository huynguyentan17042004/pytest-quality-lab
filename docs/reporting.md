# Báo cáo và artifact

Mỗi lần chạy tạo một thư mục `artifacts/runs/<run-id>/` độc lập, gồm
`manifest.json`, `reports/summary.json`, log và các thư mục artifact có giới hạn.
Muốn xuất định dạng chuẩn, dùng trực tiếp exporter JUnit XML và pytest-html:

```bash
python -m pytest -q \
  --junitxml=artifacts/junit.xml \
  --html=artifacts/report.html \
  --self-contained-html
```

## Bảo toàn lỗi gốc

Pytest hook ghi loại exception, thông báo và Python traceback đã redaction. Screenshot,
page source hoặc report là artifact hỗ trợ; nếu quá trình tạo chúng thất bại, framework
vẫn giữ exception ban đầu làm nguyên nhân chính.

## Lịch sử nhiều lần chạy

Kết quả dài hạn nằm trong `artifacts/analytics/quality.db`; xem
[phân tích chất lượng](quality-analytics.md). Allure raw results và history là lớp tùy
chọn, được mô tả tại [tích hợp Allure](allure.md).

Các thư mục `artifacts/` không được commit. Khi chia sẻ report, cần kiểm tra lại dữ
liệu nhạy cảm dù framework đã áp dụng redaction tự động.
