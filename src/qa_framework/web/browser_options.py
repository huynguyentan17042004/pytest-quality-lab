from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


def chrome_options(headless: bool = True, download_dir=None) -> ChromeOptions:
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--disable-dev-shm-usage")
    if download_dir:
        options.add_experimental_option("prefs", {"download.default_directory": str(download_dir)})
    return options


def firefox_options(headless: bool = True) -> FirefoxOptions:
    options = FirefoxOptions()
    if headless:
        options.add_argument("-headless")
    return options
