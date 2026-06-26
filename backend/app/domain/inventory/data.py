from __future__ import annotations

_INVENTORY: dict[str, int] = {
    "BOM-M16-A4": 8,
    "MOT-5HP-IE3": 15,
    "VAL-GAT-2P": 120,
    "FIL-HEPA-IND": 4,
    "COM-TORN-50L": 3,
    "MAN-DIG-600": 50,
    "TUB-AC-2IN": 500,
    "SOLD-MIG-250": 6,
    "RED-ENGR-5-1": 2,
    "SEN-TEMP-PT100": 30,
}


def get_stock(sku: str) -> int:
    return _INVENTORY.get(sku, 0)


def has_stock(sku: str, quantity: int) -> bool:
    return get_stock(sku) >= quantity
