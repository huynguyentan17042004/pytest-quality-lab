# Kiểm thử API

## Phân chia trách nhiệm

`BaseApiClient` quản lý base URL, timeout, transport error, logging an toàn, retry cho
request idempotent và giới hạn số request. Client của ứng dụng chỉ khai báo endpoint,
payload, header và cách chuyển response thành model nghiệp vụ.

HTTP response 4xx/5xx vẫn được trả về bình thường để test có thể chủ động assert các
tình huống negative. Chỉ lỗi transport, timeout hoặc dữ liệu không thể giải mã mới
được chuyển thành exception của framework.

## Nguyên tắc sử dụng

- Truyền timeout rõ ràng từ configuration; không để request chờ vô hạn.
- Chỉ retry phương thức an toàn/idempotent và giữ số lần retry ở mức giới hạn.
- Kiểm tra status code trước, sau đó mới kiểm tra schema và giá trị nghiệp vụ.
- Không ghi raw password, token, cookie hoặc authorization header vào log.
- Dùng injectable transport trong unit test để không phát sinh network traffic.

Chạy self-test của lớp API:

```bash
python -m pytest tests/framework/unit/test_api_client.py -q
```

Chạy demo API cục bộ:

```bash
python -m pytest tests/api/test_local_posts_api.py -q
```

Demo công khai chỉ được phép chạy khi truyền `--run-external`; xem thêm
[chính sách chi phí và thực thi](cost-policy.md).
