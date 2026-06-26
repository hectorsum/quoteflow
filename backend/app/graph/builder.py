from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.graph.state import QuoteState
from app.graph.nodes import (
    extract_intent_node,
    lookup_domain_node,
    validate_and_route_node,
    calculate_node,
    draft_quote_node,
    clarify_node,
    human_approval_node,
    apply_decision_node,
)
from app.graph.routing import (
    route_after_extract,
    route_after_lookup,
    route_after_calculate,
    route_after_decision,
)
from app.core.config import settings


def build_graph(checkpointer):
    builder = StateGraph(QuoteState)

    builder.add_node("extract_intent", extract_intent_node)
    builder.add_node("lookup_domain", lookup_domain_node)
    builder.add_node("validate_route", validate_and_route_node)
    builder.add_node("calculate", calculate_node)
    builder.add_node("draft", draft_quote_node)
    builder.add_node("clarify", clarify_node)
    builder.add_node("human_approval", human_approval_node)
    builder.add_node("apply_decision", apply_decision_node)
    builder.add_node("reject", lambda s: {"status": "rejected"})

    builder.set_entry_point("extract_intent")

    builder.add_conditional_edges("extract_intent", route_after_extract, {
        "clarify": "clarify",
        "lookup_domain": "lookup_domain",
    })
    builder.add_edge("lookup_domain", "validate_route")
    builder.add_conditional_edges("validate_route", route_after_lookup, {
        "unknown_customer": "clarify",
        "unknown_product": "clarify",
        "no_stock": "clarify",
        "calculate": "calculate",
    })
    builder.add_conditional_edges("calculate", route_after_calculate, {
        "human_approval": "human_approval",
        "draft": "draft",
    })
    # interrupt_before pausa ANTES de human_approval; al reanudar, human_approval
    # ejecuta y el flujo continúa hacia apply_decision para aplicar la decisión.
    builder.add_edge("human_approval", "apply_decision")
    builder.add_conditional_edges("apply_decision", route_after_decision, {
        "draft": "draft",
        "reject": "reject",
    })
    builder.add_edge("draft", END)
    builder.add_edge("clarify", END)
    builder.add_edge("reject", END)

    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_approval"],
    )


async def get_async_checkpointer():
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    return AsyncSqliteSaver.from_conn_string(settings.checkpoint_db_path)
