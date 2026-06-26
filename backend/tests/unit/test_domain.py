import pytest
from app.domain.customers.data import get_customer, customer_exists
from app.domain.catalog.data import find_product, search_product_by_name
from app.domain.inventory.data import get_stock, has_stock


# ── Customers ─────────────────────────────────────────────────────────────────

def test_known_customer_exists():
    assert customer_exists("CLI-001") is True

def test_all_known_customers_exist():
    for cid in ["CLI-001", "CLI-002", "CLI-003"]:
        assert customer_exists(cid) is True

def test_unknown_customer_returns_false():
    assert customer_exists("CLI-999") is False

def test_get_customer_returns_correct_data():
    customer = get_customer("CLI-001")
    assert customer is not None
    assert customer["tier"] == "Gold"

def test_get_unknown_customer_returns_none():
    assert get_customer("CLI-999") is None


# ── Catalog ───────────────────────────────────────────────────────────────────

def test_find_product_by_exact_sku():
    product = find_product("BOM-M16-A4")
    assert product is not None
    assert product["sku"] == "BOM-M16-A4"

def test_unknown_product_returns_none():
    assert find_product("XX-999") is None

def test_search_by_name_finds_product():
    result = search_product_by_name("bomba")
    assert result is not None

def test_search_unknown_name_returns_none():
    result = search_product_by_name("producto_inexistente_xyz")
    assert result is None


# ── Inventory ─────────────────────────────────────────────────────────────────

def test_get_stock_known_product():
    stock = get_stock("BOM-M16-A4")
    assert stock > 0

def test_get_stock_unknown_product_returns_zero():
    assert get_stock("XX-999") == 0

def test_has_stock_sufficient():
    assert has_stock("BOM-M16-A4", 1) is True

def test_has_stock_insufficient():
    assert has_stock("BOM-M16-A4", 99999) is False

def test_has_stock_zero_quantity():
    assert has_stock("BOM-M16-A4", 0) is True
