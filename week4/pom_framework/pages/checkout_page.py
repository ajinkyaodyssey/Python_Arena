# week4/pom_framework/pages/checkout_page.py

import logging
from playwright.sync_api import Page, expect
from .base_page import BasePage

log = logging.getLogger(__name__)


class CheckoutPage(BasePage):
    """
    Page object for the 3-step checkout flow:
    Step 1: /checkout-step-one.html   (customer info)
    Step 2: /checkout-step-two.html   (order review)
    Step 3: /checkout-complete.html   (confirmation)

    One class handles all three steps because they are
    a single linear flow — you never jump between them.
    Methods are named to reflect which step they belong to.
    """

    PATH = "/checkout-step-one.html"

    # =============================================
    # LOCATORS — Step 1 (Customer Info)
    # =============================================

    _FIRST_NAME = "[data-test='firstName']"
    _LAST_NAME = "[data-test='lastName']"
    _POSTAL_CODE = "[data-test='postalCode']"
    _CONTINUE_BTN = "[data-test='continue']"
    _CANCEL_BTN = "[data-test='cancel']"
    _ERROR_MSG = "[data-test='error']"

    # =============================================
    # LOCATORS — Step 2 (Order Review)
    # =============================================

    _FINISH_BTN = "[data-test='finish']"
    _ORDER_ITEM_NAME = ".inventory_item_name"
    _ORDER_ITEM_PRICE = ".inventory_item_price"
    _SUBTOTAL_LABEL = ".summary_subtotal_label"
    _TAX_LABEL = ".summary_tax_label"
    _TOTAL_LABEL = ".summary_total_label"

    # =============================================
    # LOCATORS — Step 3 (Confirmation)
    # =============================================

    _COMPLETE_HEADER = "[data-test='complete-header']"
    _COMPLETE_TEXT = "[data-test='complete-text']"
    _BACK_HOME_BTN = "[data-test='back-to-products']"
    

    def __init__(self, page: Page, base_url: str = "httos://www.saucedemo.com"):
        super().__init__(page, base_url)
        
    
    # =============================================
    # STEP 1 ACTIONS — Customer Info
    # =============================================
    
    def fill_customer_info(self, first_name: str, last_name: str, postal_code: str) -> "CheckoutPage":
        """Fill all three fields in the customer info form."""
        log.info(f"Filling checkout info: {first_name} {last_name}")
        self.page.fill(self._FIRST_NAME, first_name)
        self.page.fill(self._LAST_NAME, last_name)
        self.page.fill(self._POSTAL_CODE, postal_code)
        return self
        
    def continue_to_review(self) -> "CheckoutPage":
        """Click Continue to move to order review (Step 2)."""
        log.info("Clicking Continue to order review")
        self.page.locator(self._CONTINUE_BTN).click()
        return self
    
    def fill_and_continue(
        self,
        first_name: str,
        last_name: str,
        postal_code: str
    ) -> "CheckoutPage":
        """
        Combined: fill info + click continue.
        Most common pattern in tests.
        Returns self because we are still in the checkout flow.
        """
        return self.fill_customer_info(first_name, last_name, postal_code).continue_to_review()
        
    def cancel(self) -> "CartPage":
        """Cancel from Step 1 — returns to cart."""
        from .cart_page import CartPage
        log.info("Cancelling checkout from step 1")
        self.page.locator(self._CANCEL_BTN).click()
        return CartPage(self.page, self.base_url)


    # =============================================
    # STEP 2 ACTIONS — Order Review
    # =============================================
        
    def finish_order(self) -> "CheckoutPage":
        """Click Finish to complete the order (Step 3)."""
        log.info("Clicking Finish to complete order")
        self.page.locator(self._FINISH_BTN).click()
        return self

    def cancel_review(self) -> "InventoryPage":
        """Cancel from Step 2 — returns to inventory."""
        from .inventory_page import InventoryPage
        log.info("Cancelling from order review")
        self.page.locator(self._CANCEL_BTN).click()
        return InventoryPage(self.page, self.base_url)
        
    
    # =============================================
    # STEP 3 ACTIONS — Confirmation
    # =============================================
    
    def back_to_products(self) -> "InventoryPage":
        """Click Back Home after order complete."""
        from .inventory_page import InventoryPage
        self.page.locator(self._BACK_HOME_BTN).click()
        return InventoryPage(self.page, self.base_url)
        
        
    # =============================================
    # QUERIES
    # =============================================
    
    def get_error_text(self) -> str:
        """Error message text on Step 1."""
        return self.page.locator(self._ERROR_MSG).text_content().strip()
        
    def get_subtotal(self) -> float:
        """Parse subtotal from Step 2 summary."""
        text = self.page.locator(self._SUBTOTAL_LABEL).text_content()
        return float(text.split("$")[1])        # Get the subtotal text, split by "$", use [1] - (2nd spilt) to get the amount, and convert it to a float.
        
    def get_tax(self) -> float:
        """Parse tax from Step 2 summary."""
        text = self.page.locator(self._TAX_LABEL).text_content()
        return float(text.split("$")[1])
        
    def get_total(self) -> float:
        """Parse total from Step 2 summary."""
        text = self.page.locator(
            self._TOTAL_LABEL
        ).text_content()
        return float(text.split("$")[1])
        
    def get_order_item_names(self) -> list[str]:
        """Names of items shown in Step 2 summary."""
        return self.page.locator(
            self._ORDER_ITEM_NAME
        ).all_text_contents()


    # =============================================
    # ASSERTIONS — Step 1
    # =============================================
        
    def expect_on_step_one(self) -> "CheckoutPage":
        """Assert we are on checkout step 1."""
        expect(self.page).to_have_url(
            f"{self.base_url}/checkout-step-one.html"
        )
        return self
        
    def expect_error_containing(self, text: str) -> "CheckoutPage":
        """Assert validation error contains given text."""
        expect(
            self.page.locator(self._ERROR_MSG)
        ).to_be_visible()
        expect(
            self.page.locator(self._ERROR_MSG)
        ).to_contain_text(text)
        return self
        
    
    # =============================================
    # ASSERTIONS — Step 2
    # =============================================

    def expect_on_step_two(self) -> "CheckoutPage":
        """Assert we are on the order review page."""
        expect(self.page).to_have_url(
            f"{self.base_url}/checkout-step-two.html"
        )
        return self
        
    def expect_total_equals_subtotal_plus_tax(self) -> "CheckoutPage":
        """Assert total = subtotal + tax (within rounding)."""
        subtotal = self.get_subtotal()
        tax = self.get_tax()
        total = self.get_total()
        assert abs((subtotal + tax) - total) < 0.01, \
            f"Total {total} != subtotal {subtotal} + tax {tax}"
        return self
        
    def expect_item_in_summary(
        self, item_name: str
    ) -> "CheckoutPage":
        """Assert a specific item appears in the order summary."""
        names = self.get_order_item_names()
        assert item_name in names, \
            f"'{item_name}' not in order summary. Got: {names}"
        return self
        
    
    # =============================================
    # ASSERTIONS — Step 3
    # =============================================

    def expect_order_complete(self) -> "CheckoutPage":
        """Assert order completion page loaded."""
        expect(self.page).to_have_url(
            f"{self.base_url}/checkout-complete.html"
        )
        expect(
            self.page.locator(self._COMPLETE_HEADER)
        ).to_have_text("Thank you for your order!")
        return self


    # =============================================
    # COMPLETE FLOW HELPER
    # =============================================

    def complete_checkout(
        self,
        first_name: str = "Test",
        last_name: str = "User",
        postal_code: str = "12345"
    ) -> "CheckoutPage":
        """
        One-method complete checkout from Step 1 to Step 3.
        Fills info, continues to review, clicks finish.
        Returns self positioned on the completion page.

        Usage:
            checkout_page.complete_checkout().expect_order_complete()

        Or with custom details:
            checkout_page.complete_checkout(
                "Divya", "Kumar", "600001"
            ).expect_order_complete()
        """
        
        return (self.fill_and_continue(first_name, last_name, postal_code).finish_order())  # You are using self for finish_order() too — it's just attached to the result of the previous method