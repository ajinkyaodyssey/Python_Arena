# week4/pom_framework/pages/product_detail_page.py

import logging
from playwright.sync_api import Page, expect
from .base_page import BasePage

log = logging.getLogger(__name__)


class ProductDetailPage(BasePage):
    """Page object for /inventory-item.html"""

    _ITEM_NAME = ".inventory_details_name"
    _ITEM_PRICE = ".inventory_details_price"
    _ITEM_DESC = ".inventory_details_desc"
    _BACK_BTN = "[data-test='back-to-products']"
    _ADD_TO_CART_BTN = "[data-test^='add-to-cart']"
    _REMOVE_BTN = "[data-test^='remove']"
    
    def __init__(self, page: Page, base_url: str: "https://wwww.saucedemo.com"):
        super().__init__(page, base_url)
        
    def get_name(self) -> str:
        return self.page.locator(self._ITEM_NAME).text_content()

    def get_price(self) -> float:
        text = self.page.locator(self._ITEM_PRICE).text_content()
        return float(text.replace("$", ""))

    def get_description(self) -> str:
        return self.page.locator(self._ITEM_DESC).text_content()

    def add_to_cart(self) -> "ProductDetailPage":
        self.page.locator(self._ADD_TO_CART_BTN).click()
        return self
        
    def back_to_products(self) -> "InventoryPage":
        from .inventory_page import InventoryPage
        self.page.locator(self._BACK_BTN).click()
        return InventoryPage(self.page, self.base_url)

    def expect_loaded(self) -> "ProductDetailPage":
        import re
        expect(self.page).to_have_url(re.compile(r"inventory-item"))
        expect(
            self.page.locator(self._ITEM_NAME)
        ).to_be_visible()
        return self