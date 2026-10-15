class WindowManager:
    def __init__(self, driver) -> None:
        self.driver = driver

    def switch_to_new(self, previous_handles: set[str]) -> str:
        new_handles = set(self.driver.window_handles) - previous_handles
        if len(new_handles) != 1:
            raise RuntimeError(f"expected one new window, got {len(new_handles)}")
        handle = new_handles.pop()
        self.driver.switch_to.window(handle)
        return str(handle)
