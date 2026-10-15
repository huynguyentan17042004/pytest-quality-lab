# Tích hợp và triển khai liên tục

Workflow của repository nằm tại `.github/workflows/quality.yml`. Khi push hoặc mở pull
request, workflow chỉ chạy các kiểm tra ổn định và test trình duyệt cục bộ. Hai demo
bên ngoài chỉ chạy qua `workflow_dispatch` khi `run_external=true` và repository đã
cấu hình secret `SAUCE_DEMO_PASSWORD`.

## Pull request và nhánh chính

Hai job không tạo public traffic được chạy độc lập:

1. `quality-and-local`: Ruff, mypy, unit test, localhost API test, reporting test và
   demo API cục bộ.
2. `local-browser`: UI test bằng HTML có kiểm soát, các phân vùng đăng nhập
   positive/negative hướng dữ liệu và luồng localhost từ API sang UI bằng Chrome
   headless.

Mỗi job có timeout toàn cục 15 phút và vẫn upload artifact cục bộ nếu test thất bại.

## Demo bên ngoài

Job `approved-external-demos` chỉ tồn tại cho `workflow_dispatch` với
`run_external=true`. Job chạy đúng `DEMO-API-001` và `DEMO-UI-001`, một worker,
`--maxfail=1`, rồi lấy password SauceDemo từ repository secret
`SAUCE_DEMO_PASSWORD`.

Không có lịch gọi dịch vụ bên ngoài và không tự động rerun.

## Postman

Contract của tiến trình Postman CLI là bắt buộc và được unit test bằng mock. Integration
test cho collection localhost tự chạy khi tìm thấy executable `postman`; nếu chưa cài,
pytest hiển thị một skip rõ ràng. Cài đặt hoặc đăng nhập Postman nằm ngoài thiết lập tự
động của CI và máy cục bộ.
