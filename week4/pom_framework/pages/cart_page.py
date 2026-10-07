# week4/pom_framework/pages/cart_page.py

import logging
from playwright.sync_api import Page, expect
from .base_page import BasePage

log = logging.getLogger(__name__)


class CartPage(BasePage):
    """
    Page object for https://www.saucedemo.com/cart.html

    Responsibilities:
    - All locators for the cart page in one place
    - Business methods: remove_item(), continue_shopping(), go_to_checkout()
    - Query methods: get_item_names(), get_item_count()
    - Assertion methods: expect_loaded(), expect_item_count()
    """

    PATH = "/cart.html"

    # =============================================
    # LOCATORS
    # =============================================

    _PAGE_TITLE = ".title"
    _CART_ITEM = ".cart_item"
    _CART_ITEM_NAME = ".inventory_item_name"
    _CART_ITEM_PRICE = ".inventory_item_price"
    _CART_ITEM_QUANTITY = ".cart_quantity"
    _CONTINUE_SHOPPING_BTN = "[data-test='continue-shopping']"
    _CHECKOUT_BTN = "[data-test='checkout']"

    @staticmethod
    def _remove_btn(item_slug: str) -> str:
        return f"[data-test='remove-{item_slug}']"

    def __init__(
        self, page: Page, base_url: str = "https://www.saucedemo.com"
    ):
        super().__init__(page, base_url)

    # =============================================
    # ACTIONS
    # =============================================

    def remove_item(self, item_slug: str) -> "CartPage":
        """Remove a specific item from the cart."""
        log.info(f"Removing from cart: {item_slug}")
        self.page.locator(self._remove_btn(item_slug)).click()
        return self

    def continue_shopping(self) -> "InventoryPage":
        """Click Continue Shopping — returns to inventory."""
        from .inventory_page import InventoryPage
        log.info("Clicking continue shopping")
        self.page.locator(self._CONTINUE_SHOPPING_BTN).click()
        return InventoryPage(self.page, self.base_url)      # The browser is now on the inventory page, so give me an InventoryPage object.
        # Take my page     → give it to InventoryPage
        # Take my base_url → give it to InventoryPage

    def go_to_checkout(self) -> "CheckoutPage":
        """Click Checkout — navigates to checkout step one."""
        from .checkout_page import CheckoutPage
        log.info("Clicking checkout")
        self.page.locator(self._CHECKOUT_BTN).click()
        return CheckoutPage(self.page, self.base_url)

    # =============================================
    # QUERIES
    # =============================================

    def get_item_count(self) -> int:
        """How many items are in the cart."""
        return self.page.locator(self._CART_ITEM).count()

    def get_item_names(self) -> list[str]:
        """Names of all items currently in cart."""
        return self.page.locator(
            self._CART_ITEM_NAME
        ).all_text_contents()

    def get_item_prices(self) -> list[float]:
        """Prices of all items as floats."""
        price_texts = self.page.locator(
            self._CART_ITEM_PRICE
        ).all_text_contents()
        return [float(p.replace("$", "")) for p in price_texts]

    def get_item_quantity(self, index: int = 0) -> int:
        """Quantity of item at given index."""
        qty_text = self.page.locator(
            self._CART_ITEM_QUANTITY
        ).nth(index).text_content()
        return int(qty_text)

    def is_empty(self) -> bool:
        """True if cart has no items."""
        return self.get_item_count() == 0

    # =============================================
    # ASSERTIONS
    # =============================================

    def expect_loaded(self) -> "CartPage":
        """Assert cart page loaded correctly."""
        expect(self.page).to_have_url(f"{self.base_url}{self.PATH}")
        expect(
            self.page.locator(self._PAGE_TITLE)
        ).to_have_text("Your Cart")
        return self

    def expect_item_count(self, count: int) -> "CartPage":
        """Assert exact number of items in cart."""
        expect(
            self.page.locator(self._CART_ITEM)
        ).to_have_count(count)
        return self

    def expect_item_present(self, item_name: str) -> "CartPage":
        """Assert a specific item name is in the cart."""
        names = self.get_item_names()
        assert item_name in names, \
            f"'{item_name}' not found in cart. Cart contains: {names}"
        return self

    def expect_item_not_present(self, item_name: str) -> "CartPage":
        """Assert a specific item name is NOT in the cart."""
        names = self.get_item_names()
        assert item_name not in names, \
            f"'{item_name}' should not be in cart. Cart contains: {names}"
        return self

    def expect_empty(self) -> "CartPage":
        """Assert cart is completely empty."""
        expect(
            self.page.locator(self._CART_ITEM)
        ).to_have_count(0)
        return self
