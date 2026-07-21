from tests.utils.logger import get_logger
from tests.config.settings import settings

logger = get_logger(__name__)


class BasePlaywrightPage:
    """Base Page Object Model class for Playwright"""

    MODELS_LIST_BUTTON = "button.MuiButton-root:has-text('Модели')"

    MODELS_BUTTON = "a[role='menuitem']:has-text('Модели устройств')"
    SUBMODELS_BUTTON = "a[role='menuitem']:has-text('Подмодели')"

    PACKAGING_BUTTON = "button.MuiButton-root:has-text('Упаковки')"

    PRODUCT_PACKS_BUTTON = "a[role='menuitem']:has-text('Единичные упаковки')"
    GROUP_PACKS_BUTTON = "a[role='menuitem']:has-text('Групповые упаковки')"

    PRODUCTS_CARDS_BUTTON = "a.MuiButton-root:has-text('Продукты')"
    DEFECTS_BUTTON = "a.MuiButton-root:has-text('Дефекты')"
    EXPORTS_BUTTON = "a.MuiButton-root:has-text('Отгрузка/выгрузка')"

    # Expected URLs for navigation
    MODELS_URL = ""
    SUBMODELS_URL = "/submodels"
    PRODUCT_PACKS_URL = "/product-packs"
    GROUP_PACKS_URL = "/group-packs"
    PRODUCTS_CARDS_URL = "/products-cards"
    DEFECTS_URL = "/defects"
    EXPORTS_URL = "/exports"

    def __init__(self, page, page_path: str = ""):
        """
        Initialize base page.

        Args:
            page: Playwright page object
            page_path: Path for this page (e.g., '/submodels')
        """
        self.page = page
        self.base_url = settings.base_url
        self.page_path = page_path
        self.full_url = f"{self.base_url}{page_path}"

    # ============== Basic navigation methods ==============

    def navigate(self, path: str = ""):
        """Navigate to page"""

        url = f"{self.base_url}{path}"
        logger.info(f"Navigating to {url}")
        self.page.goto(url)

    def wait_for_element(self, selector: str, timeout: int = 5):
        """Wait for element to be visible"""

        logger.info(f"Waiting for element: {selector}")
        self.page.wait_for_selector(selector, timeout=timeout * 1000)

    def wait_for_element_hidden(self, selector: str, timeout: int = 5):
        """Wait for element to be hidden"""

        logger.info(f"Waiting for element to be hidden: {selector}")
        self.page.wait_for_selector(selector, state="hidden", timeout=timeout * 1000)

    def get_element(self, selector: str):
        """Get element by selector"""

        return self.page.locator(selector)

    def click(self, selector: str):
        """Click element"""

        logger.info(f"Clicking element: {selector}")
        self.page.click(selector)

    def fill(self, selector: str, text: str):
        """Fill text input"""

        logger.info(f"Filling {selector} with: {text}")
        self.page.fill(selector, text)

    def get_text(self, selector: str) -> str:
        """Get element text"""

        logger.info(f"Getting text from: {selector}")
        return self.page.text_content(selector)

    def is_visible(self, selector: str) -> bool:
        """Check if element is visible"""

        logger.info(f"Checking visibility of: {selector}")
        return self.page.is_visible(selector)

    def is_hidden(self, selector: str) -> bool:
        """Check if element is hidden"""

        logger.info(f"Checking if element is hidden: {selector}")
        return self.page.is_hidden(selector)

    def take_screenshot(self, filename: str):
        """Take screenshot"""

        logger.info(f"Taking screenshot: {filename}")
        self.page.screenshot(path=filename)

    def wait_for_url(self, url_pattern: str, timeout: int = 5):
        """Wait for URL to match pattern"""

        logger.info(f"Waiting for URL: {url_pattern}")
        self.page.wait_for_url(url_pattern, timeout=timeout * 1000)

    def reload(self):
        """Reload page"""

        logger.info("Reloading page")
        self.page.reload()

    def go_back(self):
        """Go back to previous page"""

        logger.info("Going back")
        self.page.go_back()

    def get_current_url(self) -> str:
        """Get current URL"""

        return self.page.url

    def get_title(self) -> str:
        """Get page title"""

        return self.page.title()

    # ---------- Methods for clicking on the main buttons ----------

    def click_models_list(self):
        """Click on Models list button (главная кнопка 'Модели')"""

        logger.info("Clicking Models list button")
        self.click(self.MODELS_LIST_BUTTON)

    def click_models(self):
        """Click on Models button ('Модели устройств')"""

        logger.info("Clicking Models button")
        self.click(self.MODELS_BUTTON)

    def click_submodels(self):
        """Click on Submodels button ('Подмодели')"""

        logger.info("Clicking Submodels button")
        self.click(self.SUBMODELS_BUTTON)

    def click_packaging(self):
        """Click on Packaging button ('Единичные упаковки')"""

        logger.info("Clicking Packaging button")
        self.click(self.PACKAGING_BUTTON)

    def click_product_packs(self):
        """Click on Product Packs button ('Групповые упаковки')"""

        logger.info("Clicking Product Packs button")
        self.click(self.PRODUCT_PACKS_BUTTON)

    def click_group_packs(self):
        """Click on Group Packs button ('Упаковки')"""

        logger.info("Clicking Group Packs button")
        self.click(self.GROUP_PACKS_BUTTON)

    def click_products_cards(self):
        """Click on Products Cards button ('Продукты')"""

        logger.info("Clicking Products Cards button")
        self.click(self.PRODUCTS_CARDS_BUTTON)

    def click_defects(self):
        """Click on Defects button ('Дефекты')"""

        logger.info("Clicking Defects button")
        self.click(self.DEFECTS_BUTTON)

    def click_exports(self):
        """Click on Exports button ('Отгрузка/выгрузка')"""

        logger.info("Clicking Exports button")
        self.click(self.EXPORTS_BUTTON)

    # ---------- Methods for checking the visibility of elements ----------

    def is_models_list_visible(self) -> bool:
        """Check if Models list button is visible"""

        return self.is_visible(self.MODELS_LIST_BUTTON)

    def is_models_button_visible(self) -> bool:
        """Check if Models button is visible"""

        return self.is_visible(self.MODELS_BUTTON)

    def is_submodels_button_visible(self) -> bool:
        """Check if Submodels button is visible"""

        return self.is_visible(self.SUBMODELS_BUTTON)

    def is_packaging_button_visible(self) -> bool:
        """Check if Packaging button is visible"""

        return self.is_visible(self.PACKAGING_BUTTON)

    def is_product_packs_button_visible(self) -> bool:
        """Check if Product Packs button is visible"""

        return self.is_visible(self.PRODUCT_PACKS_BUTTON)

    def is_group_packs_button_visible(self) -> bool:
        """Check if Group Packs button is visible"""

        return self.is_visible(self.GROUP_PACKS_BUTTON)

    def is_products_cards_button_visible(self) -> bool:
        """Check if Products Cards button is visible"""

        return self.is_visible(self.PRODUCTS_CARDS_BUTTON)

    def is_defects_button_visible(self) -> bool:
        """Check if Defects button is visible"""

        return self.is_visible(self.DEFECTS_BUTTON)

    def is_exports_button_visible(self) -> bool:
        """Check if Exports button is visible"""

        return self.is_visible(self.EXPORTS_BUTTON)

    # ---------- Methods for working with dropdowns ----------

    def is_models_dropdown_open(self) -> bool:
        """Check if Models dropdown is open"""

        return (self.is_visible(self.MODELS_BUTTON) and
                self.is_visible(self.SUBMODELS_BUTTON))

    def is_packaging_dropdown_open(self) -> bool:
        """Check if Packaging dropdown is open"""

        return (self.is_visible(self.PACKAGING_BUTTON) and
                self.is_visible(self.PRODUCT_PACKS_BUTTON) and
                self.is_visible(self.GROUP_PACKS_BUTTON))

    def wait_for_models_dropdown(self, timeout: int = 5):
        """Wait for Models dropdown to appear"""

        logger.info("Waiting for Models dropdown")
        self.wait_for_element(self.MODELS_BUTTON, timeout)
        self.wait_for_element(self.SUBMODELS_BUTTON, timeout)

    def wait_for_packaging_dropdown(self, timeout: int = 5):
        """Wait for Packaging dropdown to appear"""

        logger.info("Waiting for Packaging dropdown")
        self.wait_for_element(self.PACKAGING_BUTTON, timeout)
        self.wait_for_element(self.PRODUCT_PACKS_BUTTON, timeout)
        self.wait_for_element(self.GROUP_PACKS_BUTTON, timeout)

    def wait_for_models_dropdown_hidden(self, timeout: int = 5):
        """Wait for Models dropdown to be hidden"""

        logger.info("Waiting for Models dropdown to hide")
        self.wait_for_element_hidden(self.MODELS_BUTTON, timeout)
        self.wait_for_element_hidden(self.SUBMODELS_BUTTON, timeout)

    def wait_for_packaging_dropdown_hidden(self, timeout: int = 5):
        """Wait for Packaging dropdown to be hidden"""

        logger.info("Waiting for Packaging dropdown to hide")
        self.wait_for_element_hidden(self.PACKAGING_BUTTON, timeout)
        self.wait_for_element_hidden(self.PRODUCT_PACKS_BUTTON, timeout)
        self.wait_for_element_hidden(self.GROUP_PACKS_BUTTON, timeout)

    # ---------- Methods for navigating through sections ----------

    def navigate_to_models(self):
        """Navigate to Models page"""

        logger.info("Navigating to Models page")
        self.click_models()
        self.wait_for_url(f"{self.base_url}{self.MODELS_URL}")

    def navigate_to_submodels(self):
        """Navigate to Submodels page"""

        logger.info("Navigating to Submodels page")
        self.click_submodels()
        self.wait_for_url(f"{self.base_url}{self.SUBMODELS_URL}")

    def navigate_to_product_packs(self):
        """Navigate to Product Packs page"""

        logger.info("Navigating to Product Packs page")
        self.click_product_packs()
        self.wait_for_url(f"{self.base_url}{self.PRODUCT_PACKS_URL}")

    def navigate_to_group_packs(self):
        """Navigate to Group Packs page"""

        logger.info("Navigating to Group Packs page")
        self.click_group_packs()
        self.wait_for_url(f"{self.base_url}{self.GROUP_PACKS_URL}")

    def navigate_to_products_cards(self):
        """Navigate to Products Cards page"""

        logger.info("Navigating to Products Cards page")
        self.click_products_cards()
        self.wait_for_url(f"{self.base_url}{self.PRODUCTS_CARDS_URL}")

    def navigate_to_defects(self):
        """Navigate to Defects page"""

        logger.info("Navigating to Defects page")
        self.click_defects()
        self.wait_for_url(f"{self.base_url}{self.DEFECTS_URL}")

    def navigate_to_exports(self):
        """Navigate to Exports page"""

        logger.info("Navigating to Exports page")
        self.click_exports()
        self.wait_for_url(f"{self.base_url}{self.EXPORTS_URL}")

    # ---------- Additional methods ----------

    def get_current_path(self) -> str:
        """Get current path without base URL"""

        url = self.get_current_url()
        if url.startswith(self.base_url):
            return url[len(self.base_url):]
        return url

    def verify_navigation(self, expected_path: str) -> bool:
        """Verify that current URL contains expected path"""

        current_url = self.get_current_url()
        expected_full_url = f"{self.base_url}{expected_path}"
        logger.info(f"Verifying navigation to {expected_full_url}, current: {current_url}")
        return expected_full_url in current_url or expected_path in current_url

