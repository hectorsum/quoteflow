from __future__ import annotations

_CATALOG: dict[str, dict] = {
    "BOM-M16-A4": {"sku": "BOM-M16-A4", "name": "Bomba Centrífuga M16 Acero Inox", "unit_price": 1_850.0},
    "MOT-5HP-IE3": {"sku": "MOT-5HP-IE3", "name": "Motor Eléctrico 5HP IE3 Trifásico", "unit_price": 620.0},
    "VAL-GAT-2P": {"sku": "VAL-GAT-2P", "name": "Válvula de Compuerta 2 Pulgadas", "unit_price": 95.0},
    "FIL-HEPA-IND": {"sku": "FIL-HEPA-IND", "name": "Filtro HEPA Industrial 500CFM", "unit_price": 340.0},
    "COM-TORN-50L": {"sku": "COM-TORN-50L", "name": "Compresor Tornillo 50L 10Bar", "unit_price": 3_200.0},
    "MAN-DIG-600": {"sku": "MAN-DIG-600", "name": "Manómetro Digital 600PSI", "unit_price": 78.0},
    "TUB-AC-2IN": {"sku": "TUB-AC-2IN", "name": "Tubería Acero Carbono 2\" sch40 (metro)", "unit_price": 42.0},
    "SOLD-MIG-250": {"sku": "SOLD-MIG-250", "name": "Soldadora MIG 250A Inverter", "unit_price": 890.0},
    "RED-ENGR-5-1": {"sku": "RED-ENGR-5-1", "name": "Reductor de Engranajes 5:1 B5", "unit_price": 1_150.0},
    "SEN-TEMP-PT100": {"sku": "SEN-TEMP-PT100", "name": "Sensor de Temperatura PT100 -50/+200°C", "unit_price": 55.0},
}


def find_product(sku: str) -> dict | None:
    return _CATALOG.get(sku)


def search_product_by_name(query: str) -> dict | None:
    q = query.lower()
    for product in _CATALOG.values():
        if q in product["name"].lower():
            return product
    return None
