# Locator Strategy Notes — saucedemo.com

## Priority Order (best to worst resilience)

1. get_by_role — survives any implementation change
2. get_by_label / get_by_placeholder — survives CSS changes
3. get_by_test_id / [data-test='x'] — survives CSS changes
4. locator("#id") — survives CSS changes, breaks on ID change
5. locator(".class") — breaks on any class rename

## saucedemo.com Specific Decisions

| Element | Chosen Locator | Why | What Would Break It |
|---|---|---|---|
| Username input | get_by_placeholder("Username") | No label element exists | Changing the placeholder text |
| Password input | get_by_placeholder("Password") | No label element exists | Changing the placeholder text |
| Login button | get_by_role("button", name="Login") | Semantic, survives redesign | Changing the button text |
| Error message | [data-test='error'] | data-test set for testing | Removing the data-test attribute |
| Page heading | get_by_role("heading", name="Products") | Semantic | Changing the heading text |
| Inventory items | .inventory_item | No better option available | Any CSS class rename |

## Rule Applied Here

Prefer role and placeholder over CSS classes.
Use CSS only for elements with no semantic alternative.
Never use XPath unless nothing else works.