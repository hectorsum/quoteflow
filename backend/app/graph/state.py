from __future__ import annotations
from typing import Annotated, Literal
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages


class ExtractedItem(BaseModel):
    sku_hint: str
    quantity: int | None = None
    resolved_sku: str | None = None
    unit_price: float | None = None
    requested_discount: float = 0.0  # decimal, ej: 0.05


class QuoteCalculation(BaseModel):
    sku: str
    quantity: int
    unit_price: float
    subtotal: float
    discount_pct: float
    discount_amount: float
    total_usd: float
    applied_tier: str


class HumanDecision(BaseModel):
    action: Literal["approved", "rejected"]
    comment: str | None = None
    decided_by: str | None = None


class QuoteState(BaseModel):
    # Entrada
    quote_id: str = ""
    customer_id: str = ""
    raw_request: str = ""

    # Extracción
    extracted_items: list[ExtractedItem] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    delivery_location: str | None = None
    required_delivery_date: str | None = None

    # Dominio
    customer_name: str | None = None
    customer_tier: str | None = None
    product_found: bool = False
    stock_available: bool = False

    # Cálculo
    calculation: QuoteCalculation | None = None
    requires_human_approval: bool = False
    approval_reasons: list[str] = Field(default_factory=list)

    # Human-in-the-loop
    human_decision: HumanDecision | None = None
    clarification_request: str | None = None
    rejection_reason: str | None = None

    # Salida
    draft_quote: str | None = None
    status: str = "pending"

    # Auditoría
    nodes_visited: list[str] = Field(default_factory=list)
    audit_log: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
