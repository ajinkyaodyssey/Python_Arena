# SauceDemo Test Suite — Week 3 Saturday Project

End-to-end test suite for [saucedemo.com](https://www.saucedemo.com)
built with Playwright and pytest as part of the SDET 90-Day Training Plan.

## What This Covers

42 tests across the complete user journey — no POM yet, raw Playwright
interactions so the pain of scattered locators is felt before the
POM refactor in Week 4.

| File | Tests | What is covered |
|---|---|---|
| test_login.py | 11 | Valid login, invalid credentials, empty fields, locked user, logout |
| test_inventory.py | 10 | Product count, sort A-Z/Z-A/price, add to cart, product detail |
| test_cart.py | 10 | Add item, remove item, quantity, persist after navigation |
| test_checkout.py | 12 | Complete flow, order total math, all validation errors, cancel |

## How to Run

```bash
# All tests
pytest week3/saturday_project/ -v

# One file
pytest week3/saturday_project/test_login.py -v

# One test
pytest week3/saturday_project/test_checkout.py::test_complete_checkout_flow -v

# With print output visible
pytest week3/saturday_project/ -v -s
```

## Architecture Decisions

**Auth state reuse**
Login runs once per session. The browser state (cookies + localStorage)
is saved to a JSON file. All inventory, cart and checkout tests load
from that file — no login flow per test. Cuts suite runtime significantly.

**Function-scoped contexts**
Each test gets a fresh browser context. Cookies, localStorage, and
session state are wiped between tests. No test can pollute another.

**Fixture chain**
`inventory_page` → authenticated, on /inventory.html
`cart_page` → authenticated, backpack added, on /cart.html
`checkout_page` → authenticated, backpack in cart, on checkout step one

**No POM yet — deliberately**
Locators are repeated across files. This is intentional — Week 4
refactors this into Page Objects and the improvement is immediately visible.

## Test Users

| Username | Password | Notes |
|---|---|---|
| standard_user | secret_sauce | Normal user, all features work |
| locked_out_user | secret_sauce | Blocked at login |
| problem_user | secret_sauce | Some UI elements broken |

## What Comes Next

Week 4 refactors this entire suite into Page Object Model:
- Each page gets its own class (LoginPage, InventoryPage, CartPage, CheckoutPage)
- All locators move into page classes
- Tests become 5-line readable flows
- Adding a new test takes minutes not hoursgit checkout -b docs/week3-saturday-readme