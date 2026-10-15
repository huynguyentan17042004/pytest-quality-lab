def add_options(parser) -> None:
    group = parser.getgroup("qa-framework")
    group.addoption("--env", default="local", help="environment TOML name")
    group.addoption("--browser", choices=("chrome", "firefox"), default=None)
    group.addoption("--timeout", type=float, default=None, help="framework HTTP/UI wait timeout")
    group.addoption("--headed", action="store_true", default=False)
    group.addoption(
        "--run-external", action="store_true", default=False, help="allow approved external demos"
    )
    group.addoption("--analytics-db", default=None, help="persistent SQLite analytics path")
    group.addoption("--no-analytics", action="store_true", default=False)
