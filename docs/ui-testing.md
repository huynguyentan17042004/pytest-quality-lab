# UI testing

`DriverFactory` is the only browser constructor. Pages use minimal `BasePage` primitives and business assertions stay in tests. Implicit wait is zero; operations use targeted explicit waits. External UI execution is single-browser and opt-in.
