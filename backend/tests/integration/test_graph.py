import pytest
from unittest.mock import patch, MagicMock, AsyncMock
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


def make_llm_mock(extraction, draft_content="Borrador de cotización."):
    """Mock de ChatAnthropic. Los nodos usan ainvoke (async):
    - extract_intent_node: ChatAnthropic(...).with_structured_output(...).ainvoke(...)
    - draft_quote_node:     ChatAnthropic(...).ainvoke(...)
    """
    instance = MagicMock()
    instance.with_structured_output.return_value.ainvoke = AsyncMock(return_value=extraction)
    instance.ainvoke = AsyncMock(return_value=MagicMock(content=draft_content))
    return instance


@pytest.mark.asyncio
async def test_happy_path_standard_quote():
    """Caso 1: Ruta feliz — solicitud estándar."""
    graph = make_graph()
    config = {"configurable": {"thread_id": "integration-001"}}

    initial = QuoteState(
        quote_id="integration-001",
        customer_id="CLI-001",
        raw_request="Necesito 5 bombas BOM-M16-A4 con 5% de descuento para Arequipa",
    )

    with patch("app.graph.nodes.ChatAnthropic") as MockLLM:
        # 5 u x 1850 = 9250 < 10000, stock 8 OK, 5% < 20% Gold → completed
        MockLLM.return_value = make_llm_mock(
            mock_extract("BOM-M16-A4", 5, 5.0, "Arequipa"),
            draft_content="Estimado cliente, adjunto cotización por 5 bombas.",
        )

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
        MockLLM.return_value = make_llm_mock(mock_extract("bombas", None, 0.0))

        async for _ in graph.astream(initial.model_dump(), config):
            pass

    snapshot = await graph.aget_state(config)
    state = snapshot.values

    assert state["status"] == "clarification"
    assert state["clarification_request"] is not None


@pytest.mark.asyncio
async def test_unknown_product_halts_with_specific_status():
    """Caso 3a: Producto desconocido — status distinguible."""
    graph = make_graph()
    config = {"configurable": {"thread_id": "integration-003a"}}

    initial = QuoteState(
        quote_id="integration-003a",
        customer_id="CLI-001",
        raw_request="Necesito 5 unidades de PRODUCTO-XYZ",
    )

    with patch("app.graph.nodes.ChatAnthropic") as MockLLM:
        MockLLM.return_value = make_llm_mock(mock_extract("PRODUCTO-XYZ", 5, 0.0))

        async for _ in graph.astream(initial.model_dump(), config):
            pass

    snapshot = await graph.aget_state(config)
    state = snapshot.values

    assert state["status"] == "unknown_product"
    assert state["clarification_request"] is not None


@pytest.mark.asyncio
async def test_no_stock_halts_with_specific_status():
    """Caso 3b: Sin stock — status distinguible."""
    graph = make_graph()
    config = {"configurable": {"thread_id": "integration-003b"}}

    initial = QuoteState(
        quote_id="integration-003b",
        customer_id="CLI-001",
        raw_request="Necesito 99999 bombas BOM-M16-A4",
    )

    with patch("app.graph.nodes.ChatAnthropic") as MockLLM:
        # SKU resuelve pero 99999 > stock 8 → no_stock
        MockLLM.return_value = make_llm_mock(mock_extract("BOM-M16-A4", 99999, 0.0))

        async for _ in graph.astream(initial.model_dump(), config):
            pass

    snapshot = await graph.aget_state(config)
    state = snapshot.values

    assert state["status"] == "no_stock"


@pytest.mark.asyncio
async def test_high_value_triggers_approval_interrupt():
    """Caso 4: Alto valor — interrupt de aprobación humana."""
    graph = make_graph()
    config = {"configurable": {"thread_id": "integration-004"}}

    initial = QuoteState(
        quote_id="integration-004",
        customer_id="CLI-001",
        raw_request="Solicito 6 bombas BOM-M16-A4 con 5% de descuento",
    )

    with patch("app.graph.nodes.ChatAnthropic") as MockLLM:
        # 6 u x 1850 = 11100 > 10000, stock 8 OK → requiere aprobación humana
        MockLLM.return_value = make_llm_mock(mock_extract("BOM-M16-A4", 6, 5.0))

        async for _ in graph.astream(initial.model_dump(), config):
            pass

    snapshot = await graph.aget_state(config)
    state = snapshot.values

    assert state["status"] == "awaiting_approval"
    assert state["requires_human_approval"] is True
    assert snapshot.next  # interrupt pendiente


@pytest.mark.asyncio
async def test_resume_after_approval():
    """Caso 5: Resume tras aprobación humana → borrador completado."""
    graph = make_graph()
    config = {"configurable": {"thread_id": "integration-005"}}

    initial = QuoteState(
        quote_id="integration-005",
        customer_id="CLI-001",
        raw_request="Solicito 6 bombas BOM-M16-A4",
    )

    with patch("app.graph.nodes.ChatAnthropic") as MockLLM:
        # 6 u x 1850 = 11100 > 10000 → pausa para aprobación
        MockLLM.return_value = make_llm_mock(
            mock_extract("BOM-M16-A4", 6, 5.0),
            draft_content="Borrador aprobado de cotización.",
        )

        async for _ in graph.astream(initial.model_dump(), config):
            pass

        decision = HumanDecision(action="approved", comment="Autorizado", decided_by="gerente")
        await graph.aupdate_state(
            config, {"human_decision": decision.model_dump()}, as_node="human_approval"
        )

        async for _ in graph.astream(None, config):
            pass

    snapshot = await graph.aget_state(config)
    state = snapshot.values

    assert state["status"] == "completed"
    assert state["draft_quote"] is not None
    assert state["human_decision"]["action"] == "approved"


@pytest.mark.asyncio
async def test_resume_after_rejection():
    """Caso 5b: Resume tras rechazo humano."""
    graph = make_graph()
    config = {"configurable": {"thread_id": "integration-005b"}}

    initial = QuoteState(
        quote_id="integration-005b",
        customer_id="CLI-001",
        raw_request="Solicito 6 bombas BOM-M16-A4",
    )

    with patch("app.graph.nodes.ChatAnthropic") as MockLLM:
        # 6 u x 1850 = 11100 > 10000 → pausa para aprobación
        MockLLM.return_value = make_llm_mock(mock_extract("BOM-M16-A4", 6, 5.0))

        async for _ in graph.astream(initial.model_dump(), config):
            pass

        decision = HumanDecision(action="rejected", comment="Fuera de política", decided_by="gerente")
        await graph.aupdate_state(
            config, {"human_decision": decision.model_dump()}, as_node="human_approval"
        )

        async for _ in graph.astream(None, config):
            pass

    snapshot = await graph.aget_state(config)
    state = snapshot.values

    assert state["status"] == "rejected"
    assert state["human_decision"]["action"] == "rejected"


@pytest.mark.asyncio
async def test_durability_same_thread_id_recovers_state():
    """Caso 6: Durabilidad — mismo thread_id recupera estado."""
    checkpointer = MemorySaver()
    graph = build_graph(checkpointer)
    config = {"configurable": {"thread_id": "integration-006"}}

    initial = QuoteState(
        quote_id="integration-006",
        customer_id="CLI-001",
        raw_request="5 bombas BOM-M16-A4 con 5% descuento",
    )

    with patch("app.graph.nodes.ChatAnthropic") as MockLLM:
        MockLLM.return_value = make_llm_mock(mock_extract("BOM-M16-A4", 5, 5.0))

        async for _ in graph.astream(initial.model_dump(), config):
            pass

    # Simular restart: nuevo grafo con el MISMO checkpointer
    graph2 = build_graph(checkpointer)
    snapshot = await graph2.aget_state(config)

    assert snapshot is not None
    assert snapshot.values["quote_id"] == "integration-006"
