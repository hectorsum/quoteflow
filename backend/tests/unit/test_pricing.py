import pytest
from app.domain.pricing.calculator import calculate_price


def test_standard_gold_discount_no_approval():
    """Gold cliente con 5% descuento (máx 20%) — sin capeo."""
    result = calculate_price(
        sku="BOM-M16-A4", quantity=20, unit_price=1850.0,
        customer_tier="Gold", requested_discount=0.05
    )
    assert result.capped is False


def test_discount_exceeds_gold_tier_limit():
    """Gold cliente pide 25% (máx 20%) — capeado."""
    result = calculate_price(
        sku="BOM-M16-A4", quantity=20, unit_price=1850.0,
        customer_tier="Gold", requested_discount=0.25
    )
    assert result.capped is True


def test_silver_discount_within_limit():
    """Silver cliente con 5% (máx 12%) — sin capeo."""
    result = calculate_price(
        sku="MOT-5HP-IE3", quantity=100, unit_price=620.0,
        customer_tier="Silver", requested_discount=0.05
    )
    assert result.capped is False


def test_silver_discount_exceeds_limit():
    """Silver cliente pide 15% (máx 12%) — capeado."""
    result = calculate_price(
        sku="MOT-5HP-IE3", quantity=100, unit_price=620.0,
        customer_tier="Silver", requested_discount=0.15
    )
    assert result.capped is True


def test_standard_tier_max_discount():
    """Standard tier máx 5%."""
    result = calculate_price(
        sku="VAL-GAT-2P", quantity=100, unit_price=95.0,
        customer_tier="Standard", requested_discount=0.10
    )
    assert result.discount_pct == 0.05  # capeado
    assert result.capped is True


def test_zero_discount():
    """Sin descuento — calcula correctamente."""
    result = calculate_price(
        sku="BOM-M16-A4", quantity=5, unit_price=1850.0,
        customer_tier="Standard", requested_discount=0.0
    )
    assert result.discount_pct == 0.0
    assert result.discount_amount == 0.0


def test_calculation_amounts_are_correct():
    """Verifica aritmética exacta: subtotal, descuento, total."""
    result = calculate_price(
        sku="VAL-GAT-2P", quantity=10, unit_price=95.0,
        customer_tier="Gold", requested_discount=0.05
    )
    assert result.subtotal == pytest.approx(950.0, rel=1e-4)
    assert result.discount_amount == pytest.approx(47.50, rel=1e-4)
    assert result.total_usd == pytest.approx(902.50, rel=1e-4)
