import pytest
from app.graph.state import QuoteState, HumanDecision
from app.graph.routing import (
    route_after_extract,
    route_after_lookup,
    route_after_calculate,
    route_after_decision,
)


def make_state(**kwargs) -> QuoteState:
    defaults = dict(quote_id="test", customer_id="CLI-001", raw_request="test")
    return QuoteState(**{**defaults, **kwargs})


# ── route_after_extract ───────────────────────────────────────────────────────

def test_route_to_clarify_when_missing_fields():
    state = make_state(missing_fields=["quantity"])
    assert route_after_extract(state) == "clarify"

def test_route_to_lookup_when_no_missing_fields():
    state = make_state(missing_fields=[])
    assert route_after_extract(state) == "lookup_domain"


# ── route_after_lookup ────────────────────────────────────────────────────────

def test_route_unknown_customer():
    state = make_state(customer_id="CLI-999", product_found=True, stock_available=True)
    assert route_after_lookup(state) == "unknown_customer"

def test_route_unknown_product():
    state = make_state(product_found=False, stock_available=False)
    assert route_after_lookup(state) == "unknown_product"

def test_route_no_stock():
    state = make_state(product_found=True, stock_available=False)
    assert route_after_lookup(state) == "no_stock"

def test_route_to_calculate_when_all_valid():
    state = make_state(product_found=True, stock_available=True)
    assert route_after_lookup(state) == "calculate"


# ── route_after_calculate ─────────────────────────────────────────────────────

def test_route_to_approval_when_required():
    state = make_state(requires_human_approval=True)
    assert route_after_calculate(state) == "human_approval"

def test_route_to_draft_when_no_approval_needed():
    state = make_state(requires_human_approval=False)
    assert route_after_calculate(state) == "draft"


# ── route_after_decision ──────────────────────────────────────────────────────

def test_route_approved_to_draft():
    state = make_state(
        human_decision=HumanDecision(action="approved", comment="OK", decided_by="exec")
    )
    assert route_after_decision(state) == "draft"

def test_route_rejected_to_reject():
    state = make_state(
        human_decision=HumanDecision(action="rejected", comment="No aplica", decided_by="exec")
    )
    assert route_after_decision(state) == "reject"
