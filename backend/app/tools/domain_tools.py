from app.domain.customers.data import get_customer
from app.domain.catalog.data import find_product, search_product_by_name
from app.domain.inventory.data import get_stock, has_stock
from app.domain.pricing.calculator import calculate_price


def lookup_customer(customer_id: str) -> dict:
    customer = get_customer(customer_id)
    if customer is None:
        return {"found": False, "error": "Cliente no encontrado"}
    return {"found": True, **customer}


def lookup_product(sku_hint: str) -> dict:
    product = find_product(sku_hint)
    if product is None:
        product = search_product_by_name(sku_hint)
    if product is None:
        return {"found": False, "error": "Producto no encontrado"}
    return {"found": True, **product}


def check_inventory(sku: str, quantity: int) -> dict:
    available = get_stock(sku)
    return {
        "sku": sku,
        "available": available,
        "sufficient": available >= quantity,
    }


def get_pricing(
    sku: str,
    quantity: int,
    unit_price: float,
    customer_tier: str,
    requested_discount: float,
) -> dict:
    result = calculate_price(
        sku=sku,
        quantity=quantity,
        unit_price=unit_price,
        customer_tier=customer_tier,
        requested_discount=requested_discount,
    )
    return result.model_dump()
