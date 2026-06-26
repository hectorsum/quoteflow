import pytest
from unittest.mock import patch, MagicMock
from langgraph.checkpoint.memory import MemorySaver
from app.graph.builder import build_graph
from app.graph.state import QuoteState, HumanDecision


def make_graph():
    return build_graph(MemorySaver())


def mock_extract(sku_hint, quantity, discount_pct=5.0, location="Lima"):
    """Helper que crea el mock de IntentExtraction."""
    from app.graph.nodes import IntentExtraction
    return IntentExtraction(
        sku_hint=sku_hint,
        quantity=quantity,
        requested_discount_pct=discount_pct,
        delivery_location=location,
        required_delivery_date=None,
    )


@pytest.mark.asyncio
async def test_happy_path_standard_quote():
    """Caso 1: Ruta feliz — solicitud estándar."""
    graph = make_graph()
    config = {"configurable": {"thread_id": "integration-001"}}

    initial = QuoteState(
        quote_id="integration-001",
        customer_id="CLI-001",
        raw_request="Necesito 20 bombas BOM-M16-A4 con 5% de descuento para Arequipa",
    )

    with patch("app.graph.nodes.ChatAnthropic") as MockLLM:
        mock_instance = MagicMock()
        mock_instance.with_structured_output.return_value.invoke.return_value = mock_extract(
            "bombas BOM-M16-A4", 20, 5.0, "Arequipa"
        )
        mock_instance.invoke.return_value = MagicMock(
            content="Estimado cliente, adjunto cotización por 20 bombas.\n\nTotal: USD 35,000\n\nAtentamente,\nAndesPro Industrial"
        )
        MockLLM.return_value = mock_instance

        async for _ in graph.astream(initial.model_dump(), config):
            pass

    snapshot = await graph.aget_state(config)
    state = snapshot.values

    assert state["status"] == "completed"
    assert state["draft_quote"] is not None
    assert len(state["draft_quote"]) > 0


@pytest.mark.asyncio
async def test_incomplete_request_triggers_clarification():
    """Caso 2: Solicitud incompleta — sin cantidad."""
    graph = make_graph()
    config = {"configurable": {"thread_id": "integration-002"}}

    initial = QuoteState(
        quote_id="integration-002",
        customer_id="CLI-002",
        raw_request="necesito bombas",
    )

    with patch("app.graph.nodes.ChatAnthropic") as MockLLM:
        mock_instance = MagicMock()
        mock_instance.with_structured_output.return_value.invoke.return_value = mock_extract(
            "bombas", None, 0.0
        )
        MockLLM.return_value = mock_instance

        async for _ in graph.astream(initial.model_dump(), config):
            pass

    snapshot = await graph.aget_state(config)
    state = snapshot.values

    assert state["status"] == "clarification"
    assert state["clarification_request"] is not None


@pytest.mark.asyncio
async def test_high_value_triggers_approval_interrupt():
    """Caso 3: Alto valor — trigger de aprobación."""
    graph = make_graph()
    config = {"configurable": {"thread_id": "integration-003"}}

    initial = QuoteState(
        quote_id="integration-003",
        customer_id="CLI-001",
        raw_request="Solicito 10 bombas BOM-M16-A4 con 5% de descuento",
    )

    with patch("app.graph.nodes.ChatAnthropic") as MockLLM:
        mock_instance = MagicMock()
        mock_instance.with_structured_output.return_value.invoke.return_value = mock_extract(
            "bombas BOM-M16-A4", 10, 5.0
        )
        MockLLM.return_value = mock_instance

        async for _ in graph.astream(initial.model_dump(), config):
            pass

    snapshot = await graph.aget_state(config)
    state = snapshot.values

    assert state["status"] == "awaiting_approval"
    assert state["requires_human_approval"] is True


@pytest.mark.asyncio
async def test_durability_same_thread_id_recovers_state():
    """Caso 6: Durabilidad — mismo thread_id recupera estado."""
    checkpointer = MemorySaver()
    graph = build_graph(checkpointer)
    config = {"configurable": {"thread_id": "integration-004"}}

    initial = QuoteState(
        quote_id="integration-004",
        customer_id="CLI-001",
        raw_request="20 bombas BOM-M16-A4 con 5% descuento",
    )

    with patch("app.graph.nodes.ChatAnthropic") as MockLLM:
        mock_instance = MagicMock()
        mock_instance.with_structured_output.return_value.invoke.return_value = mock_extract(
            "bombas BOM-M16-A4", 20, 5.0
        )
        mock_instance.invoke.return_value = MagicMock(content="Borrador de cotización.")
        MockLLM.return_value = mock_instance

        async for _ in graph.astream(initial.model_dump(), config):
            pass

    graph2 = build_graph(checkpointer)
    snapshot = await graph2.aget_state(config)

    assert snapshot is not None
    assert snapshot.values["quote_id"] == "integration-004"
