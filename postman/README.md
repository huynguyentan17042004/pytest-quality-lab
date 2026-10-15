# Postman collection

Collection vẫn là test suite Postman có thể thực thi và không được chuyển thành record
của `DataLoader`. Collection cục bộ chỉ phục vụ integration test opt-in trên localhost.

Runner truyền đối số dưới dạng danh sách, dùng `shell=False`, report cục bộ, timeout
và `--no-report-events`. Biến runtime được hợp nhất vào một file Postman environment
tạm rồi truyền qua `-e`. File tạm luôn bị xóa sau khi subprocess kết thúc, kể cả khi
timeout hoặc thất bại.

Runner cục bộ không dùng `postman login`, collection ID hoặc `--env-var`; vì vậy
không cần đưa credential vào command line.
