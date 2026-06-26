from __future__ import annotations

_CUSTOMERS: dict[str, dict] = {
    "CLI-001": {"id": "CLI-001", "name": "Constructora Altamira S.A.", "tier": "Gold"},
    "CLI-002": {"id": "CLI-002", "name": "Minera Pacífico Ltda.", "tier": "Silver"},
    "CLI-003": {"id": "CLI-003", "name": "Taller Mecánico Rojas", "tier": "Standard"},
}


def get_customer(customer_id: str) -> dict | None:
    return _CUSTOMERS.get(customer_id)


def customer_exists(customer_id: str) -> bool:
    return customer_id in _CUSTOMERS
