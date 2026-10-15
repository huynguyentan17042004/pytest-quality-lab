class FrameworkError(Exception):
    """Base error raised by framework infrastructure."""


class ConfigurationError(FrameworkError):
    pass


class DataProviderError(FrameworkError):
    pass


class UnsupportedDataFormatError(DataProviderError):
    pass


class DataValidationError(DataProviderError):
    pass


class MissingVariableError(DataProviderError):
    pass


class ApiClientError(FrameworkError):
    pass


class ApiTransportError(ApiClientError):
    pass


class ApiTimeoutError(ApiTransportError):
    pass


class ResponseParseError(ApiClientError):
    pass


class UiAutomationError(FrameworkError):
    pass


class PageNotLoadedError(UiAutomationError):
    pass


class ElementActionError(UiAutomationError):
    pass


class WaitConditionError(UiAutomationError):
    pass


class PostmanRunnerError(FrameworkError):
    pass


class ReportingError(FrameworkError):
    pass
