# week4/pom_framework/pages/inventory_page.py
# Page object for https://www.saucedemo.com/inventory.html

import logging
from typing import Optional
from playwright.sync_api import Page, expect
from .base_page import BasePage

log = logging.getLogger(__name__)


class InventoryPage(BasePage):
    """
    Page object for the saucedemo products/inventory page.

    Responsibilities:
    - Knows all locators on the inventory page
    - Exposes business-level methods: sort_by(), add_to_cart(), get_items()
    - Returns appropriate page objects after navigation
    """

    PATH = "/inventory.html"

    # =============================================
    # LOCATORS
    # =============================================

    _PAGE_TITLE = ".title"
    _INVENTORY_LIST = ".inventory_list"
    _INVENTORY_ITEM = ".inventory_item"
    _ITEM_NAME = ".inventory_item_name"
    _ITEM_PRICE = ".inventory_item_price"
    _ITEM_DESC = ".inventory_item_desc"
    _SORT_DROPDOWN = "[data-test='product-sort-container']"
    _CART_BADGE = ".shopping_cart_badge"
    _CART_LINK = ".shopping_cart_link"
    _BURGER_MENU = "#react-burger-menu-btn"
    _LOGOUT_LINK = "#logout_sidebar_link"

    # Dynamic locators — built from item name
    # Usage: self._add_btn("sauce-labs-backpack")
    @staticmethod
    def _add_btn(item_slug: str) -> str:        # Static because this method doesn't use any instance data (self).
        return f"[data-test='add-to-cart-{item_slug}']"

    @staticmethod
    def _remove_btn(item_slug: str) -> str:
        return f"[data-test='remove-{item_slug}']"

    # Known item slugs — constants for the 6 saucedemo products
    BACKPACK = "sauce-labs-backpack"
    BIKE_LIGHT = "sauce-labs-bike-light"
    BOLT_TSHIRT = "sauce-labs-bolt-t-shirt"
    FLEECE_JACKET = "sauce-labs-fleece-jacket"
    ONESIE = "sauce-labs-onesie"
    RED_TSHIRT = "test.allthethings()-t-shirt-(red)"

    def __init__(self, page: Page, base_url: str = "https://www.saucedemo.com"):
        super().__init__(page, base_url)

    # =============================================
    # SORTING
    # =============================================

    def sort_by(self, option: str) -> "InventoryPage":
        """
        Sort products by the given option.
        Valid options: "az", "za", "lohi", "hilo"
        Returns self for chaining.
        """
        log.info(f"Sorting products by: '{option}'")
        self.page.locator(self._SORT_DROPDOWN).select_option(value=option)
        log.info(f"Sort applied: '{option}'")
        return self

    def sort_az(self) -> "InventoryPage":
        return self.sort_by("az")

    def sort_za(self) -> "InventoryPage":
        return self.sort_by("za")

    def sort_price_low_high(self) -> "InventoryPage":
        return self.sort_by("lohi")

    def sort_price_high_low(self) -> "InventoryPage":
        return self.sort_by("hilo")

    def add_to_cart(self, item_slug: str) -> "InventoryPage":
        """
        Add an item to the cart by its slug.
        Usage: inventory.add_to_cart(InventoryPage.BACKPACK)
        """
        log.info(f"Adding to cart: '{item_slug}'")
        self.page.locator(self._add_btn(item_slug)).click()
        cart_count = self.get_cart_count()
        log.info(f"Item added. Cart count now: {cart_count}")
        return self
        # _add_btn() is static, so self is not passed to it automatically.
        # We use self._add_btn() only to access the static method through this class instance.

    def remove_from_the_cart(self, item_slug: str) -> "InventoryPage":
        """Remove an item from cart while on the inventory page."""
        log.info(f"Removing from cart: '{item_slug}'")
        self.page.locator(self._remove_btn(item_slug)).click()
        log.info("Item removed from cart")
        return self

    def go_to_cart(self) -> "CartPage":
        """Click the cart icon. Returns CartPage."""
        from .cart_page import CartPage         # CartPage is a Python class that contains methods for interacting with the Cart screen.
        log.info("Navigating to cart page")
        self.page.locator(self._CART_LINK).click()
        log.info(f"Cart page URL: {self.page.url}")
        # After I click the cart, what page am I going to work with? -> CartPage.
        return CartPage(self.page, self.base_url)       # We are returning self.page because the CartPage constructor expects it - def __init__(self, page, base_url)
        # Return a CartPage object so we can interact with the cart page after navigation.

        # 1. Click Cart
        #         ↓
        # 2. Browser navigates to cart URL
        #         ↓
        # 3. Browser is now showing Cart page
        #         ↓
        # 4. Create CartPage object
        #         ↓
        # 5. Return that object

    # =============================================
    # NAVIGATION
    # =============================================

    def open_product_detail(self, index: int = 0) -> "ProductDetailPage":
        """Click on a product name to open its detail page."""
        from .product_detail_page import ProductDetailPage
        name = self.page.locator(self._ITEM_NAME).nth(index).text_content()
        log.info(f"Opening product detail for: '{name}' (index {index})")
        self.page.locator(self._ITEM_NAME).nth(index).click()
        return ProductDetailPage(self.page, self.base_url)

    def logout(self) -> "LoginPage":
        """Open burger menu and click logout."""
        from .login_page import LoginPage
        log.info("Opening burger menu to logout")
        self.page.locator(self._BURGER_MENU).click()
        self.page.locator(self._LOGOUT_LINK).click()
        log.info("Logged out successfully")
        return LoginPage(self.page, self.base_url)

    # =============================================
    # QUERIES
    # =============================================

    def get_item_count(self) -> int:
        """Returns how many products are visible"""
        count = self.page.locator(self._INVENTORY_ITEM).count()
        log.debug(f"Inventory item count: {count}")
        return count

    def get_cart_count(self) -> Optional[int]:
        """Returns cart badge number, or None if cart is empty."""
        badge = self.page.locator(self._CART_BADGE)
        if not badge.is_visible():
            return None
        count = int(badge.text_content())
        log.debug(f"Cart badge count: {count}")
        return count

    def get_all_product_names(self) -> list[str]:
        """Returns list of all visible product names."""
        names = self.page.locator(self._ITEM_NAME).all_text_contents()
        log.debug(f"Product names: {names}")
        return names

    def get_all_prices(self) -> list[float]:
        """Returns list of all visible prices as float."""
        price_texts = self.page.locator(self._ITEM_PRICE).all_text_contents()
        prices = [float(p.replace("$", "")) for p in price_texts]
        log.debug(f"Prices: {prices}")
        return prices

    def is_cart_badge_visible(self) -> bool:
        """True if cart badge is showing"""
        return self.page.locator(self._CART_BADGE).is_visible()

    # =============================================
    # ASSERTIONS
    # =============================================

    def expect_loaded(self) -> "InventoryPage":
        """Assert inventory page loaded correctly."""
        log.info("Asserting inventory page is loaded")
        expect(self.page).to_have_url(f"{self.base_url}{self.PATH}")
        expect(self.page.locator(self._PAGE_TITLE)).to_have_text("Products")
        expect(self.page.locator(self._INVENTORY_LIST)).to_be_visible()
        log.info("Inventory page loaded assertion passed")
        return self

    def expect_item_count(self, count: int) -> "InventoryPage":
        """Assert exact number of products visible."""
        log.info(f"Asserting inventory item count is: {count}")
        expect(self.page.locator(self._INVENTORY_ITEM)).to_have_count(count)
        log.info(f"Item count assertion passed: {count}")
        return self

    def expect_cart_badge(self, count: int) -> "InventoryPage":
        """Assert cart badge shows the given number."""
        log.info(f"Asserting cart badge shows: {count}")
        expect(self.page.locator(self._CART_BADGE)).to_have_text(str(count))
        log.info("Cart badge assertion passed")
        return self

    def expect_cart_empty(self) -> "InventoryPage":
        """Assert cart badge is not visible."""
        log.info("Asserting cart is empty")
        expect(self.page.locator(self._CART_BADGE)).not_to_be_visible()
        log.info("Cart empty assertion passed")
        return self

    def expect_sorted_az(self) -> "InventoryPage":
        """Assert products are sorted alphabetically A-Z."""
        names = self.get_all_product_names()
        assert names == sorted(names), \
            f"Expected A-Z sort. Got: {names}"
        log.info("A-Z sort assertion passed")
        return self

    def expect_sorted_za(self) -> "InventoryPage":
        """Assert products are sorted Z-A."""
        names = self.get_all_product_names()
        assert names == sorted(names, reverse=True), \
            f"Expected Z-A sort. Got: {names}"
        log.info("Z-A sort assertion passed")
        return self

    def expect_sorted_price_low_high(self) -> "InventoryPage":
        """Assert prices are in ascending order."""
        prices = self.get_all_prices()
        assert prices == sorted(prices), \
            f"Expected price low-high. Got: {prices}"
        log.info("Price low-high sort assertion passed")
        return self

    def expect_sorted_price_high_low(self) -> "InventoryPage":
        """Assert prices are in descending order."""
        prices = self.get_all_prices()
        assert prices == sorted(prices, reverse=True), \
            f"Expected price high-low. Got: {prices}"
        log.info("Price high-low sort assertion passed")
        return self
