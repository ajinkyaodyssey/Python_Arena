# Playwright expect() Assertions — Quick Reference

## Page Level
```python
expect(page).to_have_url("https://example.com/dashboard")
expect(page).to_have_url(re.compile(r"/dashboard$"))
expect(page).to_have_title("Dashboard - Example")
expect(page).to_have_title(re.compile(r"Dashboard"))
```

## Visibility
```python
expect(locator).to_be_visible()
expect(locator).not_to_be_visible()
expect(locator).to_be_hidden()
```

## Text Content
```python
expect(locator).to_have_text("exact full text")
expect(locator).to_have_text(re.compile(r"pattern"))
expect(locator).to_contain_text("partial text")
expect(locator).to_contain_text(re.compile(r"pattern"))
```

## Count
```python
expect(locator).to_have_count(6)
```

## State
```python
expect(locator).to_be_enabled()
expect(locator).to_be_disabled()
expect(locator).to_be_checked()
expect(locator).not_to_be_checked()
expect(locator).to_be_editable()
```

## Attributes and Values
```python
expect(locator).to_have_attribute("type", "text")
expect(locator).to_have_attribute("data-test", "error")
expect(locator).to_have_value("standard_user")
expect(locator).to_have_class(re.compile(r"active"))
```

## Soft Assertions (continue past failures)
```python
page.expect_soft(locator).to_be_visible()
page.expect_soft(locator).to_have_text("Products")
# All failures reported together at end of test
```

## Key Rule
Always prefer expect() over assert for UI state.
expect() auto-retries. assert checks once and fails on timing.