# QA Pytest Automation Framework — Design Specification (v2)

> **Trạng thái:** Đã hiện thực và kiểm chứng qua automated quality gates; xem README và `docs/` để chạy lại.
> **Cập nhật:** 14/10/2026.
> **Phạm vi:** Python, pytest, Requests, Selenium, Postman CLI, data-driven testing.
> **Độ phức tạp:** Medium; ưu tiên testability, maintainability và kiểm soát chi phí.
> **Nguyên tắc cốt lõi:** Chính framework phải được kiểm thử trước và trong quá trình phát triển. Hai demo API/UI là bài kiểm tra tích hợp thật, không phải nơi duy nhất phát hiện lỗi framework.

## Thay đổi từ v1

1. Chốt convention `src/qa_framework/` (reusable package) + `tests/support/` (application-specific) + `tests/framework/` (self-tests), chỉ có **một** test root là `tests/`.
2. `tests/framework/unit/` và `tests/framework/integration/` kiểm tra chính framework bằng mocks/fakes/local HTTP/HTML; chạy mặc định, nhanh và không cần Internet. `tests/api/` và `tests/ui/` có 2 demo public để xác minh tích hợp end-to-end khi bật explicit opt-in.
3. Thêm Test Design Strategy cùng hai demo có test ID/expected/technique/criteria; không tự xây hệ thống sinh test case phức tạp trong v1.
4. Chốt isolation cho API authentication, collection-time vs runtime data, tránh custom report exporters trùng pytest plugins.
5. Thêm chính sách *offline-first*, giới hạn external calls/browsers/runtime, fail-fast và không dùng paid infrastructure ở phiên bản đầu.
6. Giữ các phạm vi, guardrails và quyết định còn lại của v1; chi tiết điều chỉnh ở các mục bên dưới.

---

## 1. Cấu trúc thư mục mục tiêu — đã chốt

```text
qa_pytest_framework/
├── configs/
│   ├── environments/
│   │   ├── local.toml
│   │   ├── qa.toml
│   │   └── staging.toml
│   └── postman-variable-map.yaml
│
├── postman/
│   ├── collections/                   # Collection gốc, không chuyển thành DataProvider
│   ├── environments/
│   └── README.md
│
├── schemas/
│   └── api/                           # API contract JSON schemas
│
├── src/
│   └── qa_framework/                 # Reusable installable package
│       ├── __init__.py
│       ├── api/
│       │   ├── base_client.py
│       │   ├── response_mapper.py
│       │   ├── api_response.py
│       │   └── schema_validator.py
│       ├── assertions/
│       │   ├── api_expect.py
│       │   ├── ui_expect.py
│       │   └── soft_assertions.py
│       ├── config/
│       │   ├── settings.py
│       │   ├── environment_loader.py
│       │   └── secret_value.py
│       ├── data/
│       │   ├── loader.py
│       │   ├── converters.py
│       │   ├── validators.py
│       │   ├── provider_factory.py
│       │   └── providers/
│       │       ├── base_provider.py
│       │       ├── csv_provider.py
│       │       ├── json_provider.py
│       │       ├── yaml_provider.py
│       │       └── excel_provider.py
│       ├── exceptions/
│       │   └── framework_errors.py
│       ├── logging/
│       │   ├── config.py
│       │   ├── context.py
│       │   └── redaction.py
│       ├── postman/
│       │   ├── runner.py
│       │   ├── command_builder.py
│       │   ├── report_adapter.py
│       │   └── result.py
│       ├── pytest_plugin/
│       │   ├── plugin.py
│       │   ├── options.py
│       │   ├── fixtures.py
│       │   ├── hooks.py
│       │   └── markers.py
│       ├── reporting/
│       │   ├── models.py
│       │   ├── result_collector.py
│       │   ├── artifact_manager.py
│       │   ├── report_manager.py
│       │   └── manifest.py
│       ├── testdata/
│       │   ├── factories.py
│       │   └── resource_tracker.py
│       └── web/
│           ├── driver_factory.py
│           ├── browser_options.py
│           ├── base_page.py
│           ├── conditions.py
│           ├── download_manager.py
│           └── window_manager.py
│
├── tests/                              # Một test root duy nhất
│   ├── __init__.py
│   ├── conftest.py                    # Register plugin + common fixtures
│   ├── framework/                    # Test framework như System Under Test
│   │   ├── unit/
│   │   │   ├── test_settings.py
│   │   │   ├── test_data_loader.py
│   │   │   ├── test_api_client.py
│   │   │   ├── test_report_models.py
│   │   │   ├── test_secret_redaction.py
│   │   │   └── test_pytest_plugin.py
│   │   ├── integration/
│   │   │   ├── test_api_transport_local.py
│   │   │   ├── test_webdriver_local.py
│   │   │   ├── test_postman_runner_local.py
│   │   │   └── test_failure_artifacts.py
│   │   └── resources/
│   │       └── mini_login.html        # Local controlled UI fixture
│   ├── support/                      # Code của demo SUT, KHÔNG phải framework core
│   │   ├── __init__.py
│   │   ├── api_clients/
│   │   │   └── posts_client.py
│   │   ├── pages/
│   │   │   └── login_page.py
│   │   ├── components/
│   │   ├── flows/
│   │   ├── models/
│   │   └── factories/
│   ├── data/
│   │   ├── api/
│   │   └── ui/
│   ├── api/
│   │   └── test_posts_api.py         # DEMO-API-001; external opt-in
│   ├── ui/
│   │   └── test_locked_out_login.py  # DEMO-UI-001; external opt-in
│   └── integration/                  # Cross-layer tests của SUT (khi có)
│
├── artifacts/
│   └── runs/                         # Generated, .gitignore
│
├── docs/
│   ├── architecture.md
│   ├── api-testing.md
│   ├── ui-testing.md
│   ├── data-driven.md
│   ├── test-strategy.md
│   ├── reporting.md
│   ├── cost-policy.md
│   └── contributing.md
│
├── .env.example
├── .gitignore
├── DESIGN.md
├── pyproject.toml
└── README.md
```

**Quy ước trách nhiệm:**

- `src/qa_framework/`: generic, installable, không có `LoginPage`, `CartPage`, `AuthClient` đặc thù SUT.
- `tests/support/`: page objects, API clients, business flows và models phục vụ **demo/application đang test**. Không coi code này là reusable framework.
- `tests/framework/unit/`: kiểm tra framework bằng unit tests, stub, mock, fake transport; không cần mạng/browser.
- `tests/framework/integration/`: kiểm tra các thành phần framework phối hợp qua localhost và HTML controlled fixture; WebDriver local chỉ chạy trong suite phù hợp.
- `tests/api/`, `tests/ui/`: kiểm chứng framework với hệ thống demo thật. Không coi việc demo lỗi/đổi UI là bằng chứng duy nhất rằng framework sai.
- `tests/data/`: test input; `schemas/`: contract schemas; `postman/`: executable collections; `artifacts/`: output không commit.
- Folder `integration` phía ngoài (`tests/integration/`) dành cho workflow của **SUT**; folder `tests/framework/integration/` dành cho **tích hợp nội bộ framework**.
- Các package import bằng `__init__.py` ở những thư mục cần thiết; không yêu cầu mọi directory đều là Python package.

**Tên thư mục:** chọn theo convention phổ biến thay vì tiêu chuẩn bắt buộc: `src` theo PyPA; `tests`, `conftest.py`, `test_*.py` theo pytest; `pages`/`components` theo Selenium POM. `tests/support` và `tests/framework` là quy ước của dự án, không được tài liệu chính thức bắt buộc. Thêm package/module mới **khi có code và test tương ứng**, không tạo hàng loạt file rỗng.

## 2. Mục tiêu và định nghĩa hoàn thành

Framework phải hỗ trợ:

- Unit, API, UI, integration testing bằng pytest; Requests API, Selenium POM và Postman CLI collection nguyên bản.
- Data-driven CSV/JSON/YAML/XLSX; fixtures, parametrization, markers và multi-environment Settings.
- Explicit waits, assertion helpers khi có diagnostic value, logs có cấu trúc, HTML/JUnit/JSON reports và failure artifacts.
- Kiến trúc không lệ thuộc SUT, an toàn với secrets, có thể mở rộng parallel sau khi xác minh isolation.
- **Self-testing:** framework có test riêng cho core components và các đường đi lỗi; mỗi implementation phase phải chạy test của chính phần vừa hoàn thành.
- **End-to-end confidence:** 2 demo API/UI được chạy thật có kiểm soát để kiểm chứng wiring giữa nhiều layer.
- **Cost control:** mặc định local/offline tests; external demos và Postman/live browser chỉ chạy theo opt-in/CI schedule, không tự tạo chi phí nền tảng trả phí.

**Định nghĩa test object:** Trong `tests/framework/`, đối tượng được kiểm thử là **framework**. Trong `tests/api/` và `tests/ui/`, demo website/API là SUT, còn framework được kiểm chứng gián tiếp qua việc orchestration hoạt động. Tách hai mục tiêu để chẩn đoán lỗi chính xác.

## 3. Ngoài phạm vi phiên bản đầu

Các nội dung sau chỉ là extension point, chưa hiện thực trong phiên bản medium đầu tiên:

- Selenium Grid hoặc cloud browser.
- Docker orchestration.
- Allure server.
- Performance/load testing.
- Visual regression.
- Accessibility testing.
- Kafka/message queue framework.
- Auto-healing locator.
- TestRail/Xray write-back.
- Slack/email notification.
- AI-generated test cases.

### Extension đã hiện thực sau MVP

- Property-based testing bằng Hypothesis cho invariant của validator, redaction và
  environment isolation.
- Redacted Python traceback trong log và SQLite failure history.
- SQLite multi-run analytics và dashboard tĩnh cho pass/fail, flaky rate, execution
  time, requirement coverage và failure fingerprint.
- Raw result tương thích Allure 3; Allure CLI/report publishing vẫn là lớp tùy chọn,
  không phải dependency bắt buộc để chạy test.

## 4. Nguyên tắc kiến trúc

- Test thể hiện hành vi, input và expectation; không nhúng chi tiết Selenium/Requests hoặc file I/O không cần thiết.
- Dependency direction: `tests/*` → `tests/support` → `qa_framework` → external libraries; core tuyệt đối không import `tests/support`.
- Không đặt toàn bộ logic trong `conftest.py`; không dùng global mutable state; ưu tiên DI, composition và extension có nhu cầu thực tế.
- Không hard-code URL, token, password, environment trong tests; demo target URL là config, không là framework constant.
- Framework là SUT cho self-tests: phải kiểm tra cả **expected failure** của chính các utilities, hooks, fixtures và report generation.
- Không cho lỗi chụp artifacts che mất lỗi gốc; không retry để che flaky test hoặc product defect.
- Không ép tất cả hành vi vào một `BasePage` hoặc `AssertionManager` lớn; native pytest assert vẫn là mặc định.
- Không cần sửa test hiện có khi thêm provider/backend mới trong những extension point đã khai báo.
- Tối ưu *feedback-to-cost ratio*: deterministic local check trước, external smoke chỉ khi cần, regression nặng chạy theo lịch.

## 5. Configuration và environment management

### 5.1 Các nguồn cấu hình

- TOML: environment URL, browser, timeout, non-secret retry và report options.
- `.env`: local secrets, không commit; CI sử dụng secret injection của nền tảng.
- OS/CI environment variables: secrets và runtime override.
- CLI: override cho lần chạy; **không truyền password/token qua CLI**.

### 5.2 Thứ tự ưu tiên

```text
CLI option (non-sensitive)
  > OS/CI environment variable
  > local .env
  > configs/environments/<env>.toml
  > framework default
```

- `--env` quyết định chọn TOML trước khi merge; merge theo field (không thay toàn bộ object).
- Validate type/range/URL và required options trước execution; thông báo field sai, không in secret.
- `Settings` là immutable (`frozen=True`) và session scoped trong từng process; mọi client/page nhận qua DI, không rải `os.getenv()`.
- URL/endpoint demo thay được bằng config, không âm thầm gửi request đến public service.

### 5.3 CLI dự kiến

```bash
python -m pytest tests/framework -q
python -m pytest --env=qa --browser=chrome --timeout=15 -m 'smoke and not external'
python -m pytest tests/api/test_posts_api.py --run-external
```

`--timeout=15` ở đây là **wait/HTTP timeout của framework**, không phải job wall-clock timeout. CI runner/job cần timeout riêng. `--run-external` là custom option sẽ được hiện thực theo mục Cost Control.

### 5.4 SecretValue và redaction

- `.env.example` chỉ có tên biến/placeholder rỗng.
- Password/token bọc bởi `SecretValue` (hoặc tương đương); `repr` và traceback không in plain value.
- Log, report, error và external subprocess output cần secret redaction.
- TLS verification luôn bật mặc định; không tự động upload local artifacts.

## 6. DataLoader và data-driven testing

### 6.1 Trách nhiệm

DataLoader quản lý **static test data**, không thực thi Postman collections và không tạo runtime resources.

```text
COLLECTION PHASE: file -> provider -> parse -> static validation -> typed case (safe placeholders) -> pytest.param
RUNTIME PHASE:    typed case -> Settings/secret resolution -> runtime validation -> request/UI action
```

**Quan trọng:** pytest parametrization xảy ra ở **collection time**, còn fixture setup ở runtime. Secret placeholder `${QA_PASSWORD}` không được biến thành raw password bên trong `pytest.param`, test node ID hay collection error repr. Resolve secret ở runtime; missing secret báo lỗi có field/file/row nhưng không lộ giá trị.

### 6.2 Providers và registry

```text
.csv       -> CsvDataProvider
.json      -> JsonDataProvider
.yaml/.yml -> YamlDataProvider
.xlsx      -> ExcelDataProvider
```

`DataProviderFactory.register('.xml', XmlDataProvider)` chỉ là extension example, **không implement XML trong MVP**.

### 6.3 Public API

```python
cases = DataLoader.load("tests/data/ui/login_cases.csv", model=LoginCase)
params = DataLoader.pytest_params(
    "tests/data/ui/login_cases.csv", model=LoginCase, id_field="case_id"
)
```

`pytest_generate_tests` được sử dụng **nếu** cần đọc CLI config tại collection, không cần thêm hook cho mọi parametrized test.

### 6.4 Validation

- File tồn tại, không rỗng; CSV có header; JSON/YAML là danh sách/cấu trúc đúng; Excel có sheet yêu cầu.
- `case_id` duy nhất; required fields, boolean/int/decimal, marker allowlist đúng schema.
- Error messages có file/sheet/row/field; placeholder được validate hai bước: cú pháp + khả năng resolve tại runtime.
- Không thực thi expression, shell, Python/Jinja template từ external test data.

### 6.5 Parametrization ownership

- Inline `@pytest.mark.parametrize`: ít case/unit/boundary tests.
- External DataLoader: business matrix và datasets dùng chung.
- Parametrized fixture: browser/role/locale/dependency; indirect parametrize cho resource cần setup.
- Runtime data unique qua factories/fixtures và `ResourceTracker` (không tạo bằng DataLoader).
- Dữ liệu external demo chỉ 1 row/case mỗi lần trong MVP; không khuếch đại Cartesian combinations vô tình.

## 7. API testing — Requests

### 7.1 Stack và layering

```text
pytest test (tests/api)
  -> business API client (tests/support/api_clients)
  -> BaseApiClient (src/qa_framework/api)
  -> requests.Session / injectable transport
  -> optional ResponseMapper / ApiResponse (preserve raw response)
  -> native assert / ApiExpect / schema validator
```

- `BaseApiClient`: base URL, default headers, timeout, auth strategy, transport errors, logging và redaction.
- Business API clients chỉ định endpoint/payload, không được tạo trong reusable core.
- `requests.Session` dùng connection pooling, nhưng có cookie/header/auth state mutable.
- **Mặc định mỗi test dùng function-scoped session/client**. Không share authenticated session giữa tests; chỉ tối ưu pooling khi chứng minh isolation.
- Cho phép injectable transport/session để unit-test zero network. Response wrapper (nếu có) không đánh mất raw response, headers hoặc timing.

### 7.2 Retry policy

- Không retry assertion failure hoặc rerun toàn test mặc định.
- GET/HEAD/OPTIONS: retry giới hạn cho connection failure / 429 / 502 / 503 / 504 khi phù hợp và theo `Retry-After`.
- HTTP 500 **không retry mặc định** trong functional regression; có thể là bug cần phát hiện.
- POST/PATCH/DELETE không retry mặc định; chỉ ngoại lệ theo service contract (ví dụ idempotency key).
- Retry số lần cố định nhỏ, theo config, tắt cho demo external để budget có thể dự đoán.

### 7.3 Response validation

```text
status -> content type (nếu có body) -> parse -> schema -> required fields -> business values -> duration
```

- `204 No Content`, non-JSON errors, binary download và redirects được xử lý riêng.
- HTTP 4xx/5xx **không tự đồng nghĩa lỗi framework**: test có thể intentionally expect các status này.
- Transport errors, schema mismatches, business assertion failures được phân loại tách biệt.
- Framework core có local HTTP stub test cho timeout, header, query, 204, 404, 500, malformed JSON và redaction.

## 8. API testing — Postman Collection

### 8.1 Ranh giới và ownership

Postman Collection là executable suite (requests, variables, authorization, scripts, run order), **không phải** DataProvider. Runner không parse/translate collection JavaScript. Scenario chỉ có một owner regression chính để tránh duplicate work.

- Postman: shared requests, exploratory, deployment/happy-path smoke và simple chaining.
- Pytest + Requests: negative/boundary matrix, role permission, large data-driven tests, complex cleanup và cross-layer workflows.

### 8.2 PostmanRunner contract

Input: collection file/path hoặc ID, environment file, variables, CLI timeout, local output directory.
Output: `PostmanRunResult(exit_code, stdout_summary, stderr_summary, report_paths, duration, status)`.

- `subprocess.run` với **argument list**, không dùng `shell=True`; timeout và executable presence check.
- Local-only mặc định, không `postman login`, không cloud collection ID nếu chưa opt-in.
- `--no-report-events` khi chạy local demo; nếu dùng tài nguyên linked/cloud cần xem chính sách privacy/CLI version.
- Reporters `cli/json/junit/html` cho collection **HTTP v2 JSON**. Collection v3 YAML có giới hạn reporters khác; cần validate trước execution.
- Giữ Postman reports ở thư mục riêng, master index liên kết theo `run_id`, **không giả lập** Postman assertions thành pytest tests.
- Redact subprocess stdout/stderr và report hoặc cấu hình reporter omit headers/bodies trước khi xuất.

### 8.3 Local verification và chi phí

- `test_postman_runner_local.py`: mock subprocess command building, exit statuses, timeout, invalid runner path; không spawn external CLI trên mỗi unit run.
- Một collection local nhỏ được chạy ở opt-in integration stage, tối đa một iteration, chỉ vào local HTTP fixture khi khả thi.
- Không chạy Postman smoke trùng scenario đang chạy bằng Requests trong PR, trừ khi kiểm chứng **chính PostmanRunner**.
- CI phải thất bại khi Postman assertions fail/exit nonzero theo run policy, và vẫn publish artifacts đã sanitize.

## 9. Selenium UI và Page Object Model

### 9.1 Layers và module boundaries

```text
Test (tests/ui)
  -> Flow (tests/support/flows, only if multi-page)
  -> Page Object (tests/support/pages)
  -> Page Component (tests/support/components, if reused)
  -> generic BasePage/Wait conditions (src/qa_framework/web)
  -> Selenium WebDriver
```

- `DriverFactory` và generic `BasePage` thuộc framework core; `LoginPage`, `InventoryPage`, `CheckoutFlow` thuộc application-specific `tests/support`.
- Page Object chứa stable locators, user-facing services, navigation và technical page readiness; **không** chứa business assertions, driver creation, test data parsing, reports.
- Chỉ verify trang load đúng trong Page Object; business pass/fail thuộc test.
- Trả primitive/typed immutable state, không trả `WebElement` tùy tiện ra test.
- Flow chỉ orchestration nhiều page, không biến thành một test class che assertions.

### 9.2 BasePage tối giản

`open_path`, `visible`, `clickable`, `click`, `type`, `text_of`, `wait_for_url`, `wait_for_text`, `wait_for_invisibility`. Các thao tác ít dùng như window/download/alert ở helper riêng; không phát triển god-object.

### 9.3 Locator policy

```text
data-test / data-testid -> stable ID -> stable name -> simple CSS -> XPath khi cần
```

Không dùng absolute XPath hoặc locator lưu trong CSV/JSON/Excel. Mọi test UI đều đi qua Page Objects.

### 9.4 Local verification

`tests/framework/integration/test_webdriver_local.py` mở `mini_login.html` hoặc local HTTP app đã kiểm soát để chứng minh DriverFactory, explicit waits, Page Object primitives và artifact capture. Không phụ thuộc UI của public demo để kiểm chứng lỗi framework. Browser local integration chỉ chạy khi browser được cài và suite phù hợp được chọn; headless mặc định cho CI.

## 10. Pytest fixtures và isolation

| Fixture | Default scope | Trách nhiệm |
|---|---|---|
| `settings` | session/process | Immutable effective config |
| `run_context` | session/process | Run ID, artifact root, environment metadata |
| `api_session` | **function** | New `requests.Session` per test, close at teardown |
| `api_client` | **function** | Inject transport + auth, no shared mutable state |
| `driver` | **function** | Isolated browser/cookies/storage, quit safely |
| `login_page` | function | Application Page Object (tests/support) |
| `authenticated_user` | function | Unique runtime account/resource + cleanup |
| `resource_tracker` | function | LIFO resource cleanup, even on partial setup |

- Fixture setup errors vẫn được report; teardown failure không che call-phase failure.
- `tests/conftest.py` đăng ký `pytest_plugins = ['qa_framework.pytest_plugin.plugin']` cùng shared test fixtures; implementation logic nằm trong package.
- Không đồng thời auto-load plugin qua `pytest11` **và** đăng ký tay trong cùng repo, để tránh duplicate hooks. `pytest11` là lựa chọn sau nếu phát hành thành reusable distribution.
- Mock/Stub/Test Double ở `tests/framework/unit/`, real local integration ở `tests/framework/integration/`, external SUT demo ở `tests/api`/`tests/ui`.

## 11. Parametrization và markers

- External DataLoader tạo typed cases + `pytest.param` với stable `case_id`, không đưa secrets vào parameter IDs.
- Markers được khai báo tập trung trong `pyproject.toml` (hoặc plugin) và bật `--strict-markers`.
- Folder biểu đạt test layer/ownership; marker biểu đạt lựa chọn execution và mục đích.

| Marker | Ý nghĩa |
|---|---|
| `framework` | Self-test của framework |
| `unit` | Unit test, zero external I/O |
| `integration` | Nhiều component phối hợp, có thể localhost |
| `api`, `ui` | Lớp kiểm thử |
| `smoke`, `regression`, `critical`, `negative` | Test purpose/suite |
| `demo` | Demo verifying live end-to-end integration |
| `external` | Bắt buộc opt-in `--run-external`, không chạy mặc định |
| `serial` | Không chạy parallel, **không có ý nghĩa scheduling tự động** |

**Quy tắc:** Test không có marker `external` vẫn không được âm thầm truy cập Internet. `serial` cần chạy trong job riêng hoặc scheduler/lock được kiểm chứng; không mặc định rằng `pytest-xdist` hiểu marker.

## 12. Explicit waits và WebDriverWait

- Implicit wait = 0; không dùng `time.sleep()` trong automation test; explicit waits dùng condition thực tế.
- Visibility cho input, clickable cho button, invisibility cho spinner/overlay, URL cho navigation, text cho dynamic content, staleness rồi find lại sau DOM re-render.
- `element_to_be_clickable` không bảo đảm overlay không che element; nếu bị intercepted cần chờ overlay/state, không click lặp mù quáng.
- Custom conditions mô tả trạng thái user-visible (toast, cart count, login error), timeout có context/debug information.
- Không retry click có side-effect (submit payment/order) khi chưa chứng minh action chưa thành công.
- Test `WebDriverWait` local bao gồm deliberate delayed element và timeout để xác minh hành vi không flaky; tránh fixed waits trong tests.

## 13. Expected, actual và assertion objects

### 13.1 Object types

- Case object: toàn bộ record test.
- Expected object: kết quả mong đợi.
- Actual object: kết quả API/UI đã chuẩn hóa.
- AssertionContext: run/test/environment/correlation metadata.

Models nên là immutable dataclass với `frozen=True` và `slots=True` khi phù hợp.

### 13.2 API

```text
requests.Response
  -> ResponseMapper
  -> ApiResponse
  -> ApiExpect
  -> expected model
```

`ApiExpect` có thể kiểm tra status, content type, headers, JSON subset/path, schema và response time.

### 13.3 UI

```text
Page Object
  -> primitive/state snapshot
  -> UIExpect hoặc native assert
  -> expected model
```

Page Object không tự quyết định business pass/fail.

### 13.4 Native assert và helper

- Plain pytest `assert`: kiểm tra đơn giản.
- Domain assertion helper: nested JSON, schema, collection hoặc object phức tạp.
- Không tạo generic `AssertionManager.assert_equal()` nếu không bổ sung diagnostic value.

### 13.5 Hard và soft assertions

Hard assertion dùng cho prerequisite: HTTP status, page load, login, resource ID và schema parse.

Soft assertion chỉ dùng cho các field độc lập để thu nhiều mismatch trong một lần chạy. Soft errors phải được reset theo từng test, không dùng global collector.

### 13.6 Wait khác assertion

Wait chỉ chờ technical state. Assertion đánh giá business expectation. Assertion helper không tự chờ ngầm.


**Quyết định v2:** không xây `Expected/Actual` class cho mọi trivial assertion. Chỉ tạo typed models/helpers khi bổ sung khả năng chuẩn hóa, reuse hoặc diagnostics đáng kể. Self-tests xác minh cả assertion pass, failure diff và reset soft collector theo test.

## 14. Test Design Strategy và 2 executable demo cases

### 14.1 Mục tiêu

Framework là *execution infrastructure*; **test design** quyết định khả năng phát hiện defects. Sử dụng kỹ thuật nền tảng: Equivalence Partitioning (ECP), Boundary Value Analysis (BVA), Decision Table, State Transition, Input Space Partitioning, Negative Testing và Test Oracles. Không implement generic test-generator trong MVP. `tests/framework/*` kiểm tra tools; `tests/api/*`, `tests/ui/*` demo xác nhận wiring end-to-end.

Mỗi case có ít nhất: `case_id`, `requirement_id` (có thể là demo contract), technique, preconditions, input, expected, execution cost class (`local`/`external`) và owner. Theo dõi coverage requirement-to-case; không nhầm test count với quality coverage.

### 14.2 Demo API — `DEMO-API-001`

| Thuộc tính | Thiết kế |
|---|---|
| Objective | Kiểm tra public GET end-to-end dùng Requests BaseApiClient, business client, assertion, schema và reporting |
| External target | JSONPlaceholder (`https://jsonplaceholder.typicode.com`) |
| Endpoint | `GET /posts/1` |
| Technique | Positive representative input + API contract/schema testing |
| Preconditions | Cho phép external (`--run-external`), Internet, endpoint sẵn sàng |
| Expected | HTTP 200; JSON object; `id == 1`; `userId` là integer; `title`, `body` là nonempty string |
| Cost budget | **1 external HTTP request**/run; retries off; no write, no auth |
| Verification | Ghi report; local tests của API client đã chạy pass trước |
| Test module | `tests/api/test_posts_api.py` |

Mã minh họa **implementation target**, chưa khẳng định đã có các fixtures/classes:

```python
import pytest

pytestmark = [pytest.mark.demo, pytest.mark.api, pytest.mark.smoke, pytest.mark.external]


def test_get_single_post(posts_client):
    response = posts_client.get_post(1)  # returns requests.Response or supported wrapper
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 1
    assert isinstance(payload["userId"], int)
    assert isinstance(payload["title"], str) and payload["title"].strip()
    assert isinstance(payload["body"], str) and payload["body"].strip()
```

**Framework self-tests song hành (offline):** `test_api_client.py` mock transport và `test_api_transport_local.py` dựng local HTTP server để kiểm tra 200/204/4xx/timeout/header/schema mismatch. Đây **không phải demo thứ ba** mà là regression suite nội bộ của framework.

### 14.3 Demo UI — `DEMO-UI-001`

| Thuộc tính | Thiết kế |
|---|---|
| Objective | Kiểm tra WebDriver/DriverFactory → POM → wait → assertion → failure artifacts/report |
| External target | SauceDemo (`https://www.saucedemo.com/`) |
| Scenario | Negative login bằng demo account `locked_out_user` |
| Technique | Negative testing + valid-format but disabled/locked account partition |
| Preconditions | Local Chrome/WebDriver, opt-in external, demo password từ `SAUCE_DEMO_PASSWORD` (không commit) |
| Expected | Màn hình login hiển thị thông báo có cụm `locked out`; không điều hướng thành công vào inventory |
| Cost budget | **1 browser session**, **1 login attempt**, headless, 1 browser type, no repeated screenshots on pass |
| Verification | Controlled local UI self-tests pass trước; screenshot/page source khi fail, sanitized |
| Test module | `tests/ui/test_locked_out_login.py` |

Mã minh họa **implementation target**:

```python
import pytest

pytestmark = [pytest.mark.demo, pytest.mark.ui, pytest.mark.negative, pytest.mark.external]


def test_locked_out_user_sees_error(login_page, demo_credentials):
    login_page.open()
    login_page.login("locked_out_user", demo_credentials.password)
    assert "locked out" in login_page.error_message().lower()
```

- `LoginPage` và demo credentials nằm ở `tests/support`, không trong `qa_framework`.
- `demo_credentials` resolve password tại fixture setup, không tại collection; sensitive content không nằm trong test ID/log.
- Test không hardcode message đầy đủ để tránh brittle wording, nhưng check đúng behavior. Có thể bổ sung URL invariant nếu ổn định.
- Website public có thể thay đổi hoặc rate limit; failure ở đây phải được triage là *external SUT/infrastructure* hay *framework*, không kết luận framework hỏng chỉ từ một lần live demo fail.

**Framework self-tests song hành (local):** `test_webdriver_local.py` với `mini_login.html` xác minh page actions, waits và screenshot handling; đây vẫn là test chính framework, không phải thêm live demo.

### 14.4 Controlled failures và test oracle

- Chủ động dựng local failure: timeout, invalid settings/data, API 500, missing element, assertion mismatch, setup/teardown failures.
- Self-test **pass** khi xác nhận framework xử lý/ghi nhận các failure đúng contract; tránh khiến cả pipeline đỏ vì một lỗi được cố tình tạo.
- Với pytest plugin hooks có thể dùng fixture `pytester` để chạy nested tests và kiểm tra return code/report/artifact. Nested test tạo temp files và mock/local I/O, không gọi public SUT.
- Expected được xác định từ contract hoặc specified behavior **trước** khi so actual; không derive expected trực tiếp từ actual.

## 15. Logging

### 15.1 Output

- Human-readable `.log`.
- Structured `.jsonl`.
- Console log mức INFO.
- File log mức DEBUG khi cần.

### 15.2 Context

Mỗi record có tối thiểu:

```text
timestamp
level
run_id
test node ID
case_id
environment
layer
component
event
```

### 15.3 Logger hierarchy

```text
qa_framework.api
qa_framework.ui
qa_framework.data
qa_framework.postman
qa_framework.assertions
qa_framework.reporting
```

### 15.4 API logging

Ghi method, path, status, duration, content type và correlation ID. Không ghi raw Authorization, cookie, password hoặc token. Body chỉ lưu có giới hạn khi fail/debug và sau redaction.

### 15.5 UI logging

Ghi business actions và page transitions. Không log mọi vòng polling của WebDriverWait. Locator chi tiết chỉ ở DEBUG.

**Bổ sung v2:** context per test dùng `contextvars` hoặc cơ chế tương đương; log của local controlled-failure test phải được kiểm tra để đảm bảo primary error/case ID và không có secrets. Log level mặc định không ghi HTTP body/screenshot liên tục, tránh artifact growth.

## 16. Reporting và export

### 16.1 Output convention

```text
artifacts/runs/<run-id>/
├── manifest.json
├── logs/
├── reports/                  # pytest-html, junit.xml, summary.json
├── screenshots/
├── page_sources/
├── browser_logs/
├── api_exchanges/
└── postman/                  # Postman local reports, separated
```

### 16.2 Reporting policy (medium-size)

- **Reuse** pytest builtin JUnit XML và `pytest-html` thay vì viết `junit_exporter.py`/`html_exporter.py` riêng.
- Framework chỉ viết `ResultCollector`, `ArtifactManager`, `ReportManager`, `manifest.json`, JSON summary và link/index gộp Postman. Không duplicate pytest reporters.
- Nếu cần custom format sau này, dùng `ResultExporter` Protocol; chưa tạo `exporters/` cho các format chưa có yêu cầu.
- `TestResult` tách `setup/call/teardown` phases; tính test outcome đúng một lần và giữ nguyên primary failure. Unexpected cleanup failure là teardown issue riêng.
- `manifest.json` có `schema_version`, run context, counts, redacted metadata, relative links; worker artifacts không bị overwrite.

### 16.3 Failure capture

- UI: screenshot, page source, URL, console nếu hỗ trợ; chỉ trên fail/debug và luôn giới hạn số lượng/kích thước.
- API: method/path/status, correlation ID, truncated sanitized request/response summary (không dump raw secrets).
- Lỗi chụp artifact chỉ log warning, không thay thế lỗi test.
- `tests/framework/integration/test_failure_artifacts.py` tạo deliberate controlled failures và xác minh output/counter/redaction bằng temp run directory.

## 17. Pytest plugin lifecycle

```text
pytest_addoption       -> register execution options (env, browser, external opt-in)
pytest_configure       -> validate/load settings, logging, markers
pytest_collection_modifyitems -> enforce external gate and selected-case budget
pytest_sessionstart    -> create run context and artifacts directory
pytest_runtest_setup   -> per-test context; guard unsafe live execution
pytest_runtest_makereport -> capture setup/call/teardown failures and worker artifacts
pytest_runtest_logreport  -> controller/normal-process report aggregation
pytest_sessionfinish  -> finalize summary/manifest on controller
```

- Plugin code nằm ở `src/qa_framework/pytest_plugin/` và được register một lần.
- `tests/conftest.py` chỉ plugin registration và project fixtures.
- Khi dùng xdist, **worker** capture artifacts; **controller** aggregate và xuất manifest cuối; tránh mỗi worker đè lên `reports/` chung.
- Self-test plugin thông qua `pytester`: confirm marker registration, option parsing, external skip policy, teardown reporting, unique artifacts và original failure preservation.

## 18. Exception hierarchy

```text
FrameworkError
├── ConfigurationError
├── DataProviderError
│   ├── UnsupportedDataFormatError
│   ├── DataValidationError
│   └── MissingVariableError
├── ApiClientError
│   ├── ApiTransportError
│   ├── ApiTimeoutError
│   └── ResponseParseError
├── UiAutomationError
│   ├── PageNotLoadedError
│   ├── ElementActionError
│   └── WaitConditionError
├── PostmanRunnerError
└── ReportingError
```

Assertion failure phải phân biệt với framework/configuration/data error trong report.

- Khi wrap exception phải giữ `raise ... from exc` và root-cause context; expected non-2xx API response không tự là `ApiClientError` nếu transport vẫn thành công.

## 19. Runtime test data và cleanup

DataLoader chỉ xử lý static data. Runtime resources được tạo bằng factory fixtures và theo dõi bằng `ResourceTracker`.

```text
fixture setup
  -> create resource by API
  -> register cleanup
  -> run test
  -> cleanup reverse order
```

Cleanup failure được log và report như teardown issue nhưng không che call-phase failure.

- **Đăng ký cleanup ngay sau mỗi lần tạo resource thành công**, kể cả khi fixture setup còn bước sau có thể fail. Local self-tests xác minh LIFO, idempotent best-effort cleanup và thông tin teardown riêng biệt.
- External demos v1 là read-only/negative-login, không tạo server-side resources cần cleanup; Postman cases ghi dữ liệu chỉ khi có policy riêng.

## 20. Retry, flaky và quarantine

- Không bật full-test rerun mặc định; test fail phải tạo diagnostic hữu ích.
- API retry chỉ cho request idempotent khi có transient failure và giới hạn; demo external tắt retry để budget chính xác.
- UI reacquire stale element có giới hạn cho read/idempotent operations; không blindly retry payment/submit.
- Flaky test có root-cause ticket, owner, expiry nếu quarantine; không lặng lẽ biến thành `xfail` vô thời hạn.
- `serial` chỉ là annotation, không tự ép xdist chạy tuần tự: serial suite dùng job riêng hoặc scheduler xác định.
- Triage 3 loại: **framework failure**, **SUT product failure**, **external infrastructure failure**; report/issue được gán đúng nhóm.

## 21. Parallel execution — extension sau MVP

Chuẩn bị cho `pytest-xdist`:

- Function-scoped browser/client, worker-specific runtime data, unique artifact path theo worker/nodeid/case_id.
- Không global mutable state, không share sessions giữa processes; worker logs riêng, controller merge.
- Test `serial` không nằm trong parallel job khi chưa có scheduling mechanism đáng tin.
- Mặc định **không** bật parallel cho external demos (chỉ 1 worker). Chỉ bật cho local framework suite sau isolation verification.
- Không bật xdist trong MVP chỉ vì đã cài dependency; overhead có thể cao hơn lợi ích cho ít test.

## 22. Browser, file download và window handling

DriverFactory là nơi duy nhất tạo Chrome/Firefox. Test/Page Object không tự gọi `webdriver.Chrome()`.

DownloadManager phải chờ file xuất hiện và ổn định kích thước, sau đó kiểm tra tên, extension/MIME và nội dung. Không chờ download bằng `sleep()`.

WindowManager quản lý tab/window, alert và frame theo explicit API thay vì rải logic trong test.


- Download completion check phải phân biệt partial/temp download, stable size, expected checksum/content nếu có; không suy luận chỉ từ file existence. Browser fixture always `quit()` ở teardown nếu đã khởi tạo thành công.

## 23. Dependencies và packaging

Package cài được qua:

```bash
python -m pip install -e '.[dev]'
python -m pytest tests/framework -q
```

- `pyproject.toml` là **source of truth** cho project metadata, dependencies/extras, pytest, Ruff và mypy.
- Core: `pytest`, `requests`, `selenium`, `jsonschema` (nếu schema validator là feature chính).
- Data extras: `python-dotenv`, `PyYAML`, `openpyxl`.
- Report extras: `pytest-html` (JUnit dùng pytest built-in).
- Parallel extras (sau MVP): `pytest-xdist`.
- Dev extras: `ruff`, `mypy`, có thể thêm `pytest-timeout` nếu muốn test-level timeout.
- Postman CLI là **external executable**: version pin/check riêng, không nhầm với pip dependency.
- Không thêm `pandas` chỉ để đọc test data dạng bảng; không duy trì `requirements.txt` khác nguồn nếu không có lý do cụ thể.
- Lock/dependency reproducibility cho CI được bổ sung khi chọn package manager, không invent lock format.

## 24. Security & privacy

- Không commit `.env`, password, tokens, cookies, API keys; dùng CI secret store.
- Redaction phải áp dụng cho log, exception, pytest assertion repr, Postman subprocess stdout/stderr/reports, URLs query string và request/response artifacts.
- Screenshots/page sources có thể chứa PII; screenshot chỉ khi fail; artifact access/retention do CI policy quản lý.
- Không chạy arbitrary expressions từ YAML/CSV/Excel; YAML safe loader; secrets resolve ở runtime.
- TLS verify bật mặc định; tuyệt đối không biến workaround `verify=False` thành default.
- Local report mặc định không tự gửi external service; Postman sử dụng local collections và `--no-report-events` trong mode thích hợp.
- External demo chỉ dùng public demo accounts/data; không gửi credential/case data nội bộ lên JSONPlaceholder/SauceDemo.

## 25. Traceability

- Stable `case_id`, ví dụ `FW-CONFIG-001`, `FW-API-001`, `DEMO-API-001`, `DEMO-UI-001`.
- Metadata tối thiểu cho demo: requirement/contract, technique, case_id, owner, expected outcome, cost class (`local`/`external`).
- Test name/nodeid có thể đổi khi refactor, **case_id** dùng trong logs, artifacts, reports.
- Mapping: requirement/quality attribute → test design technique → case IDs → latest execution evidence.
- Dùng bảng/case metadata đơn giản ở MVP; không xây full test management database.

## 26. CI/CD pipeline và chi phí

```text
PR (fast / zero external)
  checkout -> install -> Ruff -> collection -> tests/framework/unit
           -> tests/framework/integration (localhost / controlled)
           -> sanitized reports/artifacts

Merge main (moderate)
  PR gates -> local API/WebDriver contract suite (if browser available)
           -> optional local PostmanRunner smoke -> reports

Manual or scheduled opt-in (external)
  PR gates -> DEMO-API-001 + DEMO-UI-001 (1 worker, strict budget)
           -> triage external vs framework failures -> publish artifacts

Nightly (future)
  wider regression / browser matrix only after isolation + cost approval
```

| Trigger | Default suite | Network paid cost |
|---|---|---|
| Pull request | Framework unit + local integration | 0 intentional public requests; no paid service |
| Merge `main` | Above + local WebDriver/Postman verification when supported | No remote Selenium Grid/cloud |
| Manual `--run-external` | Only 2 approved live demo cases | At most defined budget per run |
| Scheduled | External demos at controlled frequency, optional | Explicitly budgeted, not every commit |

- CI job wall-clock timeout, `--maxfail=1` for expensive smoke, 1 browser worker for external.
- Publish available redacted artifacts even on test failure; report failure CI status appropriately.
- External failures may require human triage; do not automatically re-trigger costly pipelines to hide failures.

## 27. Quality gates

- Ruff lint + format check; mypy where types are defined; pytest collection no errors; strict markers.
- Framework unit tests pass; local integration validates HTTP/driver/reporting behavior (when dependencies are present).
- Không có `time.sleep()` trong test automation; không có `find_element` trong business tests; secrets không hardcoded.
- Negative framework tests validate timeout, bad data, broken settings, setup/teardown failures và artifact capture.
- External tests bị skip theo policy khi chưa `--run-external`; không có network trong default framework test suite.
- External smoke chỉ được chọn sau local quality gates; công khai số external cases/requests/browsers dự kiến.
- Không đánh đồng `skipped` do thiếu Chrome hoặc external disabled với `passed`; báo trạng thái rõ ràng.

## 28. Acceptance criteria — MVP

### 28.1 Framework self-verification (bắt buộc)

- [ ] `python -m pytest tests/framework/unit -q` pass; **không phát sinh public HTTP requests**.
- [ ] Settings precedence và invalid-value diagnostics đúng; `SecretValue` repr/log không lộ value.
- [ ] CSV/JSON/YAML/XLSX providers load cùng API; duplicate ID, missing field, wrong type, missing variable báo file/sheet/row/field đúng.
- [ ] Parametrization không resolve raw secrets ở collection; missing secret fail tại controlled runtime step.
- [ ] Fake/local API test cho success, 204, negative expected status, transport timeout, malformed JSON, schema mismatch, retry-off/limited, close session.
- [ ] Plugin `pytester` test option/marker/external gate/primary failure + teardown failure behavior.
- [ ] Local UI fixture xác minh DriverFactory, explicit waits, Page Objects, screenshot capture trên deliberate fail (nếu Chrome installed).
- [ ] PostmanRunner unit tests mock subprocess để kiểm tra command, timeout, exit code, report paths; optional local collection integration.
- [ ] Reporter tạo HTML, JUnit, JSON summary và `manifest.json` trong run directory bằng pytest plugin/report manager; controlled failure giữ original error.
- [ ] Logs/artifacts không chứa raw secrets; test kiểm tra redaction và file size/budget policies.
- [ ] README có lệnh cài đặt/chạy và giải thích rõ sự khác biệt local/real external tests.

### 28.2 Live demo verification (opt-in, không thuộc default PR cost)

- [ ] `DEMO-API-001` chạy thật đúng expected (`GET /posts/1`), tối đa 1 request và không retry.
- [ ] `DEMO-UI-001` chạy thật negative login, 1 browser, 1 login attempt, không bị mất primary failure nếu capture artifact lỗi.
- [ ] Cả hai tạo traceable report evidence; external environment issue được đánh dấu riêng.
- [ ] Bật/tắt `--run-external` đúng policy; lần chạy không opt-in không chạm public service.

**Lưu ý:** Các checkbox là tiêu chí **cần kiểm chứng khi code**, không phải kết quả đã hoàn thành tại thời điểm viết DESIGN v2.

## 29. Thứ tự hiện thực — vertical slices, verify sau mỗi phase

### Phase 1 — Foundation + framework self-tests

- Package layout, Settings, exceptions, pytest options/markers, minimal logging.
- Viết `tests/framework/unit/test_settings.py`, `test_secret_redaction.py`, `test_pytest_plugin.py` ngay trong phase.
- Verify: install editable, Ruff, collection, options, local-only default.

### Phase 2 — First working API vertical slice

- `BaseApiClient` + transport DI + response handling + native assert/schema validation.
- Unit fake transport + local HTTP integration; basic JUnit/HTML report từ pytest.
- Verify: timeout, unexpected 500, 204, wrong schema, non-leaking logs.

### Phase 3 — First working local UI vertical slice

- DriverFactory, BasePage, explicit waits, controlled mini-login HTML.
- Verify: successful action, element timeout, screenshot/teardown on deliberate fail.
- Nếu local Chrome chưa được cài, báo blocked rõ, không coi là passed.

### Phase 4 — Data-driven + runtime resource lifecycle

- Providers CSV/JSON/YAML/XLSX, typed models, pytest params, runtime secret resolver.
- Verify malformed data/duplicate IDs, collection-vs-runtime security, cleanup LIFO và partial setup.

### Phase 5 — 2 live demo tests (gated)

- Application-specific `PostsClient`/`LoginPage` dưới `tests/support`.
- Implement `DEMO-API-001` và `DEMO-UI-001`; external gate và per-run budget.
- Verify real live execution **chỉ sau** các local checks; không retry, không matrix.

### Phase 6 — Postman CLI + reporting hardening

- Local PostmanRunner, mocked process tests, optional local collection; report linking.
- Manifest, JSON summary, structured logs, controlled failure artifact tests, xdist-ready paths.
- Verify secret redaction, exit-code handling, exporter reuse, controller/worker responsibilities.

### Phase 7 — Final verification, CI và documentation

- PR local gates, opt-in demo job, quality checks, README/docs/ADR cho mọi thay đổi scope.
- Verify reproducibility và cost ceiling; không gọi hoàn thành nếu chưa có evidence chạy thật ở tầng tương ứng.

**Mỗi phase chỉ complete khi self-tests mới và regression của phases trước pass.** Không code tất cả folders rồi mới chạy tests ở cuối dự án.

## 30. Các quyết định bất biến khi hiện thực

- Phải update DESIGN/changelog/ADR nếu đổi boundary, public API, cost policy hoặc scope.
- Mọi component mới có self-test (unit hoặc controlled local integration) trước khi công bố ổn định.
- Test code ngắn, đọc như business scenario; framework code không phụ thuộc vào demo SUT.
- Không tuyên bố API/UI/Postman tích hợp thành công nếu chưa chạy được (và lưu evidence) trong môi trường xác định.
- Chẩn đoán framework defect, SUT defect và environment failure khác nhau; không retry để che lỗi.
- Ưu tiên dễ debug, deterministic, có chi phí đo được hơn abstraction và extension giả định.

## 31. Cost Control, test execution policy và failure diagnosis

### 31.1 Default: offline-first / cheap feedback

- Lệnh mặc định để phát triển: `python -m pytest tests/framework -q` (unit + local integration theo điều kiện môi trường).
- PR chạy framework self-tests; **không tự gọi JSONPlaceholder, SauceDemo, Postman Cloud, Selenium Grid hoặc paid infrastructure**.
- Unit tests mock mọi network/process. Integration framework có thể sử dụng `127.0.0.1` và local browser; chỉ spawn Chrome ở browser-specific suite. Trong hot loop ưu tiên `tests/framework/unit`; local browser integration chạy ở commit/PR gate có chủ đích.
- Không tự chạy full regression trên mỗi source save; chọn tests impacted trước, toàn bộ local suite khi chuẩn bị commit/PR.

### 31.2 External gates (fail closed)

1. Marker `external` **không chạy** khi thiếu `--run-external`, kể cả khi trực tiếp chọn test module/node ID (plugin skip rõ ràng).
2. `--run-external` chỉ cho phép những case đã approve, ban đầu `DEMO-API-001` + `DEMO-UI-001`; không bật bằng default CI. Các demo có allowlist cho URL đích để cấu hình sai không âm thầm chuyển request sang host khác.
3. Trước live run, in planned count/cost class; nếu selected external cases vượt **2** trong MVP thì `pytest.UsageError` và **không chạy bất kỳ external test nào**.
4. `DEMO-API-001`: 1 GET, no retry. `DEMO-UI-001`: 1 browser session, 1 login submission, Chrome headless, no rerun. Không chạy parallel external. `RunContext` giữ các counter tối thiểu (BaseApiClient request attempts, DriverFactory sessions, PostmanRunner invocations); policy fail **trước** khi tạo thêm tài nguyên. Với traffic tải asset bên trong browser, không suy luận toàn bộ network request count chỉ từ browser-session counter.
5. POST/PUT/PATCH/DELETE trên public/live targets, multi-browser matrix, cloud remote session, Postman cloud upload phải có quyết định/authorization riêng; **chưa bật** trong MVP.
6. CI/job wall-clock timeout, subprocess timeout và request/browser wait timeout là ba loại khác nhau; tránh run không giới hạn.
7. Dùng local logs on fail và capped artifacts; dọn cũ theo retention. Không chụp screenshot thường xuyên khi pass.

### 31.3 Không nhầm các khái niệm chi phí

- **Resource cost:** CPU/RAM/browser start/CI minutes, network requests, artifact storage.
- **Financial cost:** paid grid/SaaS, billed CI runner/minutes, metered API, Postman paid features (nếu có).
- **Maintenance cost:** duplicate suites, flaky reruns, false positives, excessive abstractions.

Public demo có thể miễn phí ở thời điểm thiết kế nhưng vẫn tiêu thụ network/CI resources và có thể rate-limit. Chính sách không dựa vào giả định rằng external service luôn miễn phí hoặc luôn sẵn sàng.

### 31.4 Failure diagnosis matrix

| Failure source | Typical evidence | Action |
|---|---|---|
| Framework core | Reproduce với fake/local controlled fixture | Block merge và fix implementation |
| SUT behavior | Local framework pass, live business assertion fail | Triage như product/demo issue |
| External infrastructure | DNS/SSL/429/site unavailable/browser mismatch | Mark external instability, không auto-rerun hàng loạt |
| Test design/oracle | Expected sai, unstable locator, coupling between cases | Update specification/test; không hạ assertion vô điều kiện |
| Reporting/cleanup | Original test failure + artifact/teardown failure | Preserve primary failure; fix supporting infrastructure |

### 31.5 Khuyến nghị run commands sau khi implementation

```bash
# Cheap/default self-tests, no public traffic
python -m pytest tests/framework/unit -q
python -m pytest tests/framework/integration -q

# All framework self-tests
python -m pytest tests/framework -q

# Explicitly approved live demos; requires Internet/browser/secrets where needed
python -m pytest tests/api/test_posts_api.py tests/ui/test_locked_out_login.py \
  --run-external -q --maxfail=1

# Offline static/collection validation
python -m pytest --collect-only -q
```

Lệnh trên là **mục tiêu CLI sau khi implement**; chưa thể chạy thật nếu chưa có source tests/plugin/fixtures.

## 32. Naming conventions và tài liệu đối chiếu

Tên thư mục và module được chọn dựa vào conventions, không được gọi là một tiêu chuẩn thiết kế duy nhất:

- **PyPA, src layout vs flat layout:** https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- **pytest, Good Integration Practices:** https://docs.pytest.org/en/stable/explanation/goodpractices.html
- **pytest, Writing Plugins & `pytester`:** https://docs.pytest.org/en/stable/how-to/writing_plugins.html
- **pytest, Markers:** https://docs.pytest.org/en/stable/example/markers.html
- **Selenium, Page Object Models/Page Components:** https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/
- **Postman CLI, reporters:** https://learning.postman.com/docs/postman-cli/postman-cli-reporters/
- **Postman CLI, collection commands:** https://learning.postman.com/docs/postman-cli/postman-cli-collections/
- **JSONPlaceholder original demo guide:** https://jsonplaceholder.typicode.com/guide/

Trong v2, `tests/framework`, `tests/support`, `test-strategy.md` và `cost-policy.md` là **project-local naming decisions** để thể hiện ownership rõ ràng. Tài liệu chính thức xác nhận pattern chung (`src`, `tests`, test modules, POM), không chuẩn hóa mọi folder con cụ thể.

---

**Approval scope:** Áp dụng các quyết định này cho implementation v2. Bản tài liệu là **design specification**, không thay thế source code/test results. Sau khi implement, cập nhật acceptance checkboxes bằng kết quả chạy thực tế.

## Implementation evidence — 14/10/2026

- Runtime được cô lập tại `.venv` (Python 3.11); package vẫn được lint/type-check theo target Python 3.10.
- `tests/framework/unit`: **30 passed**; không gọi public service.
- `tests/framework/integration`: **7 passed**, gồm localhost API và Chrome headless với controlled HTML.
- Default full run: **37 passed, 2 skipped**; hai external demos bị gate đúng khi thiếu `--run-external`.
- Live opt-in (`--env=qa --run-external`): **2 passed** (`DEMO-API-001`, `DEMO-UI-001`), đúng ngân sách 1 GET + 1 browser/login attempt.
- Collection: **39 tests collected**; Ruff format/lint pass; mypy pass trên **58 source files**.
- HTML, JUnit, JSON summary và `manifest.json` đã được tạo và đọc lại. Postman CLI thật không bắt buộc trong run này; command/exit/redaction contract đã được kiểm tra bằng mocked subprocess.

### Completion update

- Bổ sung 5 deterministic local demo cases: local API success/404, CSV-driven UI positive/negative và API-to-UI flow.
- Default full run: **43 passed, 3 skipped** trên **46 collected tests**. Ba skip được phân loại rõ: hai external cases chưa opt-in và một optional Postman CLI integration do máy không có executable.
- Hai approved live demos được chạy lại: **2 passed**; external budget và allowlist vẫn được giữ nguyên.
- Controlled-failure demo chính thức tạo log text/JSONL, screenshot PNG 1440×857, page source, summary và manifest; primary assertion vẫn là lỗi hiển thị.
- Thêm workflow `.github/workflows/qa-pytest-framework.yml` với quality job, controlled Chrome job và manual-only external job. Workflow YAML đã parse thành công tại local; việc thực thi trên GitHub runner cần push repository.
