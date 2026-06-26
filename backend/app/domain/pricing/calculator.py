from pydantic import BaseModel

TIER_MAX_DISCOUNT = {
    "Gold": 0.20,
    "Silver": 0.12,
    "Standard": 0.05,
}


class PriceCalculation(BaseModel):
    sku: str
    quantity: int
    unit_price: float
    subtotal: float
    discount_pct: float
    discount_amount: float
    total_usd: float
    applied_tier: str
    capped: bool = False  # True si el descuento solicitado fue recortado al máximo del tier


def calculate_price(
    sku: str,
    quantity: int,
    unit_price: float,
    customer_tier: str,
    requested_discount: float,  # decimal, ej: 0.15
) -> PriceCalculation:
    max_discount = TIER_MAX_DISCOUNT.get(customer_tier, 0.05)
    effective_discount = min(requested_discount, max_discount)
    capped = effective_discount < requested_discount

    subtotal = quantity * unit_price
    discount_amount = subtotal * effective_discount
    total_usd = subtotal - discount_amount

    return PriceCalculation(
        sku=sku,
        quantity=quantity,
        unit_price=unit_price,
        subtotal=subtotal,
        discount_pct=effective_discount,
        discount_amount=discount_amount,
        total_usd=total_usd,
        applied_tier=customer_tier,
        capped=capped,
    )
