from app.graph.state import QuoteState


def route_after_extract(state: QuoteState) -> str:
    if state.missing_fields:
        return "clarify"
    return "lookup_domain"


def route_after_lookup(state: QuoteState) -> str:
    from app.domain.customers.data import customer_exists
    if not customer_exists(state.customer_id):
        return "unknown_customer"
    if not state.product_found:
        return "unknown_product"
    if not state.stock_available:
        return "no_stock"
    return "calculate"


def route_after_calculate(state: QuoteState) -> str:
    if state.requires_human_approval:
        return "human_approval"
    return "draft"


def route_after_decision(state: QuoteState) -> str:
    if state.human_decision and state.human_decision.action == "approved":
        return "draft"
    return "reject"
