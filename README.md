# Python Arena — SDET 90-Day Training Framework
 
![CI](https://github.com/ajinkyaodyssey/Python_Arena/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Playwright](https://img.shields.io/badge/playwright-latest-green)
![pytest](https://img.shields.io/badge/pytest-8.3.5-orange)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
 
A production-grade SDET framework built from scratch over 90 days —
covering UI automation, REST API testing, database validation, CI/CD pipelines,
and Docker containerisation. Every decision here is documented and defensible
in an interview.
 
> Built by an SDET targeting product company roles at 25–30 LPA.
> This is not a tutorial project — it is a working framework with real
> engineering decisions behind every design choice.
 
---
 
## What This Demonstrates
 
| Area | What Was Built | Where |
|---|---|---|
| UI Automation | Playwright POM — 5 page classes, session auth reuse, screenshot on failure | `week4/pom_framework/` |
| API Testing | Full CRUD suite, JSON schema validation, 3-fixture auth chain, secrets management | `week5/` |
| DB Validation | SQLite + pytest — 15 data integrity tests post-API | `week6/day31/` |
| SQL | SELECT, WHERE, JOIN, GROUP BY, 8 classic interview problems | `week6/` |
| CI/CD | lint gate → parallel jobs → matrix browsers → nightly schedule | `.github/workflows/` |
| Docker | Containerised test environment, layer-cached Dockerfile | `Dockerfile` |
| Secrets | python-dotenv, zero hardcoded credentials, GitHub encrypted secrets | `week5/config/` |
 
---
 
## CI Pipeline Architecture
 
```
push / PR
  └── lint (flake8, ~10s)           ← blocks everything if code quality fails
        ├── unit-tests (~10s)        ← parallel
        ├── UI Tests/chromium (~3min) ← parallel  } matrix strategy
        └── UI Tests/firefox  (~3min) ← parallel  } one job definition
 
nightly 2:00 AM UTC
  └── lint
        ├── test-api (reqres.in)     ← rate limit resets daily at midnight
        └── regression (full suite)  ← all layers: unit + UI + DB
```
 
**Design decisions in the pipeline:**
 
- **Lint runs first** — flake8 catches syntax errors in 10 seconds before
  wasting 3 minutes on browser setup
- **Matrix strategy** — one job definition runs on Chromium AND Firefox in
  parallel. Adding webkit is one word change
- **fail-fast: false** — if Chromium fails, Firefox still completes.
  Cross-browser data is never lost
- **API tests nightly only** — reqres.in free tier = ~100 req/day.
  Suite uses ~50 per run. Running on every push exhausts the quota.
  2AM schedule means limit resets before each run
- **if: always() on all uploads** — report exists even when tests fail.
  Without this, the artifact is skipped exactly when you need it most
- **pip cache** — `cache: 'pip'` cuts 30–60 seconds per job on repeat runs
- **concurrency cancel** — rapid pushes cancel old runs, preventing queue buildup
---
 
## Framework Architecture
 
```
                    TESTS
                    (what)
        test_login_pom.py
        test_checkout_pom.py
               |
               | calls methods, never selectors
               v
          PAGE OBJECTS
          (how to interact)
  LoginPage    InventoryPage    CartPage
  CheckoutPage  ProductDetailPage
               |
               | inherits from
               v
          BASE PAGE
     navigate()  screenshot()
     expect_url()  get_title()
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
              FIXTURES (test setup)
  browser ─────────── session scope ── launched once per run (saves 80s)
  auth_storage ─────── session scope ── login once, save JSON (saves 75s)
  logged_in_page ────── function scope ── fresh context per test (isolation)
  cart / checkout ───── function scope ── pre-navigated fixtures
               |
               | defined in
               v
  week4/pom_framework/tests/conftest.py
```
 
---
 
## Page Object Design Decisions
 
**Why methods return page objects**
 
`login_page.login(user, pass)` returns an `InventoryPage`.
This enables chaining and makes navigation intent explicit:
```python
# Test reads like a user story
inventory = LoginPage(page, url).navigate().login("standard_user", "secret_sauce")
inventory.expect_loaded()
```
 
**Why locators are private class constants**
```python
class LoginPage(BasePage):
    _USERNAME_INPUT = "#user-name"
    _ERROR_MSG      = "[data-test='error']"
```
Changing `#user-name` to `#username` requires one edit in one file.
Without POM: grep through 40+ test files.
 
**Why two login methods**
```python
login()                   # expects success → returns InventoryPage
login_expecting_failure() # expects failure → returns LoginPage
```
Test intent is clear before reading the assertions.
 
**Why session scope for browser and auth_storage**
```
Browser launch  = 1–2s × 40 tests = 80 seconds wasted without session scope
Auth state      = 2–3s × 30 tests = 75 seconds wasted without session scope
With session scope: each costs 2–3 seconds once for the entire run
```
 
**Why function scope for page and logged_in_page**
 
Each test gets a fresh browser context — isolated cookies, localStorage,
sessionStorage. `new_context(storage_state=path)` gives each test a COPY
of the auth state, not a shared reference. Test 1 cart cannot affect Test 2.
 
---
 
## API Testing Design Decisions
 
**Why requests.Session over bare requests.get()**
 
Session maintains a connection pool and reuses TCP connections — faster.
Session persists headers across all calls — set `x-api-key` once, every
request carries it automatically. Mirrors real user session behaviour.
 
**Why schema validation beyond status code checks**
 
Status 200 says the response arrived. Schema validation says it is correct.
A bug that changes `id` from integer to `null` returns 200 and crashes every
client reading the id field. Schema catches it immediately.
 
**The three-fixture auth chain**
```
api_client (session)     unauthenticated session + x-api-key header
    ↓
auth_token (session)     login once → extract token string
    ↓
auth_client (session)    api_client + Authorization: Bearer token
```
Login happens once per run. Token reused across all authenticated tests.
 
**Why secrets never appear in source code**
 
`.env` is gitignored. `python-dotenv` loads variables into `os.environ`.
A central `config.py` module is the only file that calls `os.getenv()`.
Test files import from config — never touch environment variables directly.
In CI, GitHub encrypted secrets inject the key before tests run.
 
---
 
## DB Validation Design
 
**Why validate the database after API tests?**
 
API response says 201 Created. That means the server accepted the request.
SQL query confirms the row actually exists with the correct field values.
These are different things. A bug can return 201 and fail to persist data.
DB validation catches what API response checks cannot.
 
**The three helper functions**
```python
fetch_all(sql, params)   # list of dicts
fetch_one(sql, params)   # one dict or None
fetch_value(sql, params) # single scalar (COUNT, SUM, AVG)
 
# Always use ? for params — never f-string SQL (injection risk)
fetch_value("SELECT COUNT(*) FROM users WHERE role = ?", ("sdet",))
```
 
---
 
## Docker Setup
 
```bash
# Build the image
docker build -t python-arena .
 
# Run default (week1 unit tests)
docker run --rm python-arena
 
# Run specific suite
docker run --rm python-arena pytest week6/ -v
 
# Run with API key (secrets passed at runtime, never baked in)
docker run --rm -e REQRES_API_KEY=your_key python-arena pytest week5/ -v
```
 
**Why layer order matters in the Dockerfile**
```dockerfile
COPY requirements.txt .      # copy deps first
RUN pip install ...          # install — cached unless deps change
RUN playwright install ...   # install browser — cached unless deps change
COPY . .                     # copy source last — changes most often
```
Code change → only the last COPY reruns. First build: ~5 min.
Subsequent builds after code change: ~15 seconds.
 
---
 
## Project Structure
 
```
Python_Arena/
├── week1/
│   ├── day1-5/               Python fundamentals
│   └── saturday_project/
│       ├── library_system.py     4-class OOP project
│       └── test_library_system.py 12 pytest unit tests
│
├── week2/
│   ├── day6/    Decorators — @timer, @retry from scratch
│   ├── day7/    Generators — paginated API reader
│   └── day8/    Context managers — ManagedDB class
│
├── week3/
│   └── saturday_project/
│       ├── test_login.py        11 login scenario tests
│       ├── test_inventory.py    10 product listing tests
│       ├── test_cart.py         10 cart management tests
│       └── test_checkout.py     12 checkout flow tests
│       (42 tests — raw Playwright, no POM)
│
├── week4/
│   └── pom_framework/
│       ├── pages/
│       │   ├── base_page.py         Shared navigation + assertions
│       │   ├── login_page.py        Login locators + methods
│       │   ├── inventory_page.py    Product listing + sort + cart
│       │   ├── cart_page.py         Cart management
│       │   ├── checkout_page.py     3-step checkout flow
│       │   └── product_detail_page.py Individual product page
│       └── tests/
│           ├── conftest.py          Fixtures with justified scopes
│           ├── test_login_pom.py    11 tests
│           ├── test_inventory_pom.py 12 tests
│           ├── test_cart_pom.py     13 tests
│           ├── test_checkout_pom.py  14 tests
│           └── test_full_flow_pom.py 4 end-to-end tests
│
├── week5/
│   ├── config/config.py        Central env var management
│   ├── day22/  GET tests + schema validation
│   ├── day23/  POST, PUT, PATCH, DELETE tests
│   ├── day24/  JSON schema library
│   ├── day25/  Auth flow + token fixtures
│   └── day26/  Secrets management tests
│
├── week6/
│   ├── day27/  SELECT, WHERE, LIKE, IN, BETWEEN, IS NULL
│   ├── day28/  INNER JOIN, LEFT JOIN, no-orders pattern
│   ├── day29/  GROUP BY, HAVING, COUNT, SUM, AVG
│   ├── day30/  8 classic SQL interview problems
│   └── day31/  DB validation pytest suite (15 tests)
│
├── week7/
│   ├── day35/  Nightly schedule, if:always() artifacts demo
│   ├── day36/  Docker container validation tests
│   └── day37/  Matrix browser strategy demo
│
├── Dockerfile              Container for test framework
├── .dockerignore           Excludes .venv, .env, __pycache__
├── .flake8                 Lint configuration
├── .env.example            Required environment variables
├── pytest.ini              Test runner configuration
├── requirements.txt        Pinned dependencies
└── .github/
    └── workflows/
        └── tests.yml       CI pipeline
```
 
---
 
## How to Run
 
All code runs in GitHub Codespaces — no local install needed.
 
```bash
# Clone or open in Codespace
pip install -r requirements.txt
playwright install chromium
 
# Copy env vars template
cp .env.example .env
# Add your REQRES_API_KEY from app.reqres.in/api-keys
```
 
```bash
# Run everything
pytest
 
# Run by marker
pytest -m smoke       # critical path only (~2 min)
pytest -m regression  # full suite (~8 min)
 
# Run specific week
pytest week1/saturday_project/ -v    # unit tests
pytest week4/pom_framework/tests/ -v # POM framework
pytest week5/ -v                     # API tests
pytest week6/day31/ -v               # DB validation
 
# Run in Docker
docker build -t python-arena .
docker run --rm python-arena
```
 
---
 
## Environment Setup
 
```bash
# Required in .env file (gitignored — never committed)
REQRES_API_KEY=your_key_here
 
# Get free key at: app.reqres.in/api-keys
```
 
See `.env.example` for all required variables.
 
---
 
## Test Coverage
 
| Suite | Tests | Type | Speed |
|---|---|---|---|
| Week 1 LibrarySystem | 12 | Unit — OOP | < 5s |
| Week 3 raw Playwright | 42 | UI E2E | ~45s |
| Week 4 POM login | 11 | UI E2E | ~15s |
| Week 4 POM inventory | 12 | UI E2E | ~20s |
| Week 4 POM cart | 13 | UI E2E | ~20s |
| Week 4 POM checkout | 14 | UI E2E | ~25s |
| Week 4 POM full flow | 4 | UI end-to-end | ~30s |
| Week 5 API suite | 40+ | API | ~30s |
| Week 6 DB validation | 15 | Database | ~5s |
| Week 7 container env | 5 | Infrastructure | ~10s |
| **Total** | **168+** | | **~3.5 min** |
 
---
 
## Tech Stack
 
| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12 | Primary language |
| Playwright | latest | Browser automation |
| pytest | 8.3.5 | Test runner |
| pytest-playwright | 0.5.0 | Playwright fixtures |
| pytest-html | 4.1.1 | HTML report generation |
| requests | 2.32.3 | HTTP API testing |
| jsonschema | 4.23.0 | API response validation |
| python-dotenv | 1.0.1 | Environment variable management |
| flake8 | 7.0.0 | Code quality linting |
| Docker | — | Test containerisation |
| GitHub Actions | — | CI/CD pipeline |
 
---
 
## Author
 
**Ajinkya** — SDET 
 
[GitHub](https://github.com/ajinkyaodyssey) ·
[LinkedIn](https://linkedin.com/in/ajinkyahegu)