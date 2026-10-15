# API testing

`BaseApiClient` owns base URL, timeout, transport errors, safe logging, idempotent retry limits, and request budget. Application clients own endpoint paths. HTTP 4xx/5xx responses are returned normally for intentional negative assertions.
