import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langgraph.checkpoint.memory import MemorySaver
from app.graph.builder import build_graph
from app.graph.state import QuoteState, ExtractedItem, QuoteCalculation, HumanDecision


@pytest.fixture
def state_standard() -> QuoteState:
    return QuoteState(
        quote_id="test-001",
        customer_id="CLI-001",
        raw_request="Necesito 20 cascos HX-200 con 5% de descuento para Arequipa",
    )


@pytest.fixture
def state_incomplete() -> QuoteState:
    return QuoteState(
        quote_id="test-002",
        customer_id="CLI-002",
        raw_request="necesito cascos",
        missing_fields=["quantity"],
    )


@pytest.fixture
def state_high_value() -> QuoteState:
    return QuoteState(
        quote_id="test-003",
        customer_id="CLI-001",
        raw_request="Solicito 500 cascos HX-200 con 8% de descuento",
        extracted_items=[
            ExtractedItem(
                sku_hint="cascos HX-200",
                resolved_sku="HX-200",
                quantity=500,
                requested_discount=0.08,
            )
        ],
        customer_name="Minera Horizonte SAC",
        customer_tier="Gold",
        product_found=True,
        stock_available=False,
    )


@pytest.fixture
def state_ready_to_calculate() -> QuoteState:
    return QuoteState(
        quote_id="test-004",
        customer_id="CLI-001",
        raw_request="20 cascos HX-200 con 5% descuento",
        extracted_items=[
            ExtractedItem(
                sku_hint="cascos HX-200",
                resolved_sku="HX-200",
                quantity=20,
                requested_discount=0.05,
            )
        ],
        customer_name="Minera Horizonte SAC",
        customer_tier="Gold",
        product_found=True,
        stock_available=True,
        status="calculating",
    )


@pytest.fixture
def state_awaiting_approval() -> QuoteState:
    return QuoteState(
        quote_id="test-005",
        customer_id="CLI-001",
        raw_request="500 cascos HX-200 con 8% descuento",
        extracted_items=[
            ExtractedItem(
                sku_hint="cascos HX-200",
                resolved_sku="HX-200",
                quantity=500,
                requested_discount=0.08,
            )
        ],
        customer_name="Minera Horizonte SAC",
        customer_tier="Gold",
        product_found=True,
        stock_available=True,
        status="awaiting_approval",
        requires_human_approval=True,
        approval_reasons=[
            "Total USD 11,270.00 supera umbral de aprobación (USD 10,000.00)",
            "Descuento solicitado 8% supera máximo permitido para tier Gold (8%)",
        ],
        calculation=QuoteCalculation(
            sku="HX-200",
            quantity=500,
            unit_price_usd=24.50,
            applied_discount=0.08,
            subtotal_usd=12250.0,
            discount_amount_usd=980.0,
            total_usd=11270.0,
            requires_approval=True,
            approval_reasons=[],
        ),
    )


@pytest.fixture
def memory_graph():
    return build_graph(MemorySaver())
