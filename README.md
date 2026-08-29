# Python Arena — SDET 90-Day Training Journey

Personal training repository documenting my progression from
framework-user to framework-designer over 90 days, targeting
product-company SDET roles.

---

## What Is Here

| Week | Focus | Key Deliverable |
|---|---|---|
| Week 1 | Python OOP foundations | LibrarySystem — 4-class OOP project with inheritance |
| Week 2 | Decorators, generators, context managers, Git | @retry decorator, paginated API reader, ManagedDB |
| Week 3 | Playwright fundamentals | 42-test suite against saucedemo.com (raw interactions) |
| Week 4 | Page Object Model, pytest fixtures, CI/CD | Complete POM framework with 5 page classes |
| Week 5+ | API testing, SQL, capstone framework | Coming |

---

## Framework Architecture

```
                    TESTS
                    (what)
          test_login_pom.py
          test_checkout_pom.py
                   |
                   | calls methods on
                   v
              PAGE OBJECTS
              (how to interact)
    LoginPage    InventoryPage    CartPage
    CheckoutPage  ProductDetailPage
                   |
                   | uses
                   v
              BASE PAGE
         navigate() screenshot()
         expect_url() get_title()
                   |
                   | wraps
                   v
              PLAYWRIGHT
         (browser automation)
                   |
                   v
           SAUCEDEMO.COM
         (application under test)
```

```
                  FIXTURES
                 (test setup)
    browser ──── session scope ──── one launch per run
    auth_storage ─ session scope ──── login once, save JSON
    logged_in_page ─ function scope ── fresh context per test
    cart / checkout ─ function scope ── pre-navigated fixtures
                   |
                   | wired by
                   v
    week4/pom_framework/tests/conftest.py
```


               CI/CD
every push → smoke tests (2 min)
nightly     → full regression suite
               |
.github/workflows/tests.yml

---

## Folder Structure

Python_Arena/
│
├── week1/
│ ├── day1-5/ Python fundamentals and OOP exercises
│ └── saturday_project/
│ ├── library_system.py 4-class OOP project
│ └── test_library_system.py 11 pytest unit tests
│
├── week2/
│ ├── day6/ Decorators — @timer, @retry from scratch
│ ├── day7/ Generators — paginated API reader, log parser
│ └── day8/ Context managers — ManagedDB class + @contextmanager
│
├── week3/
│ ├── day12/ First Playwright tests — login flows
│ ├── day13/ Locator strategies — role, label, CSS comparison
│ ├── day14/ All actions — check, select, hover, file upload
│ ├── day15/ All assertions — visibility, text, count, state
│ ├── day16/ Advanced — network interception, auth state, tabs
│ └── saturday_project/
│ ├── conftest.py Fixtures for raw test suite
│ ├── test_login.py 11 login scenario tests
│ ├── test_inventory.py 10 product listing tests
│ ├── test_cart.py 10 cart management tests
│ └── test_checkout.py 12 checkout flow tests
│ (42 tests total, raw Playwright — no POM)
│
├── week4/
│ ├── conftest.py Screenshot on failure hook
│ ├── day19/ Parametrize, markers, pytest.ini
│ ├── day20/ HTML report, logging, debugging system
│ └── pom_framework/
│ ├── pages/
│ │ ├── base_page.py Shared navigation + assertions
│ │ ├── login_page.py Login locators + methods
│ │ ├── inventory_page.py Product listing + sort + cart
│ │ ├── cart_page.py Cart management
│ │ ├── checkout_page.py 3-step checkout flow
│ │ └── product_detail_page.py Individual product page
│ └── tests/
│ ├── conftest.py Fixtures — browser, auth, pages
│ ├── test_login_pom.py 11 POM login tests
│ ├── test_inventory_pom.py 12 POM inventory tests
│ ├── test_cart_pom.py 13 POM cart tests
│ ├── test_checkout_pom.py 14 POM checkout tests
│ └── test_full_flow_pom.py 4 end-to-end chain tests
│
├── LeetCode Solutions/ Daily DSA problems (ongoing)
├── pytest.ini Test runner configuration
├── requirements.txt Python dependencies
└── .github/
└── workflows/
└── tests.yml CI pipeline — smoke + regression jobs


---

## How to Run

All code runs in GitHub Codespaces — no local install needed.

**Open a Codespace:**
Go to the repo on GitHub → Code → Codespaces → New codespace

**Install dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

**Run everything:**
```bash
pytest
```

**Run by marker:**
```bash
pytest -m smoke        # Critical path only (~2 min)
pytest -m regression   # Full suite (~8 min)
pytest -m api          # API tests only, no browser
pytest -m ui           # Browser tests only
```

**Run one specific suite:**
```bash
pytest week1/saturday_project/                    # Unit tests
pytest week3/saturday_project/                    # Raw Playwright
pytest week4/pom_framework/tests/                 # POM framework
```

**Run one specific file:**
```bash
pytest week4/pom_framework/tests/test_login_pom.py -v
```

**Run one specific test:**
```bash
pytest week4/pom_framework/tests/test_full_flow_pom.py::test_complete_purchase_flow -v
```

**View the HTML report:**
After any run, open `reports/report.html` in your browser.
The report shows pass/fail status, duration, and log output per test.

---

## Markers

| Marker | Purpose | When it runs |
|---|---|---|
| `smoke` | Critical path — login, basic navigation, add to cart | Every commit via CI |
| `regression` | Full suite coverage | Nightly at 2AM UTC |
| `ui` | Tests that need a browser | With Playwright job |
| `api` | Tests that only use HTTP requests | With API job (Week 5) |
| `slow` | Tests taking more than 10 seconds | Excluded from quick runs |
| `wip` | Work in progress, not ready | Skipped in CI |

Run without slow tests:
```bash
pytest -m "smoke and not slow"
```

---

## Page Object Design Decisions

**Why methods return page objects**
`login_page.login(user, pass)` returns an `InventoryPage`.
This enables chaining: `LoginPage(page).navigate().login(u, p).expect_loaded()`
and makes navigation intent explicit in the test.

**Why locators are private class constants**
```python
class LoginPage(BasePage):
    _USERNAME_INPUT = "#user-name"   # private constant
    _ERROR_MSG = "[data-test='error']"
```
Changing `#user-name` to `#username` requires one edit in one file.
Without POM you would grep through 40 test files.

**Why there are two login methods**
```python
login()                    # expects success, returns InventoryPage
login_expecting_failure()  # expects failure, returns LoginPage
```
The test's intent is explicit before you read the assertions.
A test using `login_expecting_failure` tells you immediately
it is testing an error path — no need to read the assertion.

**Why session scope for browser and auth_storage**
Browser launch = 1-2 seconds. Auth state creation = 2-3 seconds.
With 40 authenticated tests:
- Without session scope: 40 * 2s = 80 seconds wasted on browser launch
- With session scope: 2 seconds total for browser launch
- Auth state: 2-3 seconds once vs 2-3 seconds * 30 tests = 75 seconds saved

**Why function scope for page and logged_in_page**
Each test gets a fresh browser context — isolated cookies, localStorage,
sessionStorage. Test 1 adding items to cart cannot affect Test 2's cart.
`new_context(storage_state=path)` gives each test a COPY of the auth state,
not a shared reference.

---

## CI Pipeline

On every push to main or PR:
┌─────────────┐
│ Unit Tests │ pytest week1/ (fast, no browser)
└──────┬──────┘
│
┌──────▼──────┐
│ Smoke Tests │ pytest -m smoke (browser, ~2 min)
└─────────────┘

Nightly at 2AM UTC:
┌──────────────────┐
│ Regression Suite │ pytest -m regression (full, ~8 min)



Failure artifacts uploaded automatically:
- `reports/screenshots/` — browser state at failure moment
- `reports/report.html` — full HTML report with log traces

---

## Test Counts

| Suite | Tests | Type | Speed |
|---|---|---|---|
| LibrarySystem unit tests | 11 | Pure Python | < 5s |
| Week 3 raw Playwright | 42 | UI | ~45s |
| Week 4 POM login | 11 | UI | ~15s |
| Week 4 POM inventory | 12 | UI | ~20s |
| Week 4 POM cart | 13 | UI | ~20s |
| Week 4 POM checkout | 14 | UI | ~25s |
| Week 4 POM full flow | 4 | UI end-to-end | ~30s |
| **Total** | **107** | | **~3 min** |

---

## Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12 | Primary language |
| Playwright | latest | Browser automation |
| pytest | 8.3.5 | Test runner |
| pytest-playwright | 0.5.0 | Playwright fixtures |
| pytest-html | 4.1.1 | HTML report generation |
| GitHub Actions | — | CI/CD pipeline |

---

## Author

**Ajinkya** — SDET in training  
GitHub: [@ajinkyaodyssey](https://github.com/ajinkyaodyssey)  
Timeline: 90-day structured plan, started August 2026