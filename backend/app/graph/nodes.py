import logging
from datetime import datetime, timezone
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic

from app.graph.state import QuoteState, ExtractedItem, QuoteCalculation, HumanDecision
from app.tools.domain_tools import lookup_customer, lookup_product, check_inventory, get_pricing
from app.domain.customers.data import customer_exists
from app.core.config import settings

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _visited(state: QuoteState, node: str) -> list[str]:
    return state.nodes_visited + [node]


def _log(state: QuoteState, node: str, msg: str) -> list[str]:
    return state.audit_log + [f"{_now()} [{node}] {msg}"]


# ── Schema de extracción ────────────────────────────────────────────────────

class IntentExtraction(BaseModel):
    sku_hint: str
    quantity: int | None = None
    requested_discount_pct: float = 0.0
    delivery_location: str | None = None
    required_delivery_date: str | None = None


# ── Nodos ───────────────────────────────────────────────────────────────────

async def extract_intent_node(state: QuoteState) -> dict:
    node = "extract_intent"
    llm = ChatAnthropic(
        model="claude-opus-4-5",
        api_key=settings.anthropic_api_key,
    ).with_structured_output(IntentExtraction)

    system = (
        "Eres un asistente de extracción de datos para AndesPro Industrial. "
        "Tu ÚNICA función es extraer información estructurada de solicitudes de cotización. "
        "NUNCA inventes SKUs, clientes, precios, cantidades ni descuentos. "
        "Si no puedes extraer un campo con certeza, déjalo como null."
    )

    try:
        result: IntentExtraction = await llm.ainvoke([
            {"role": "system", "content": system},
            {"role": "user", "content": state.raw_request},
        ])
    except Exception as exc:
        logger.exception("extract_intent failed")
        return {
            "status": "error",
            "errors": state.errors + [str(exc)],
            "nodes_visited": _visited(state, node),
            "audit_log": _log(state, node, f"ERROR: {exc}"),
        }

    missing: list[str] = []
    if not result.sku_hint:
        missing.append("producto")
    if result.quantity is None:
        missing.append("cantidad")

    item = ExtractedItem(
        sku_hint=result.sku_hint,
        quantity=result.quantity,
        requested_discount=result.requested_discount_pct / 100.0,
    )

    return {
        "extracted_items": [item],
        "missing_fields": missing,
        "delivery_location": result.delivery_location,
        "required_delivery_date": result.required_delivery_date,
        "nodes_visited": _visited(state, node),
        "audit_log": _log(state, node, f"extracted sku_hint={result.sku_hint!r} qty={result.quantity}"),
    }


async def lookup_domain_node(state: QuoteState) -> dict:
    node = "lookup_domain"
    item = state.extracted_items[0]

    customer = lookup_customer(state.customer_id)
    customer_name = customer.get("name") if customer["found"] else None
    customer_tier = customer.get("tier") if customer["found"] else None

    product = lookup_product(item.sku_hint)
    product_found = product["found"]
    stock_available = False

    updated_item = item.model_copy()
    if product_found:
        updated_item = item.model_copy(update={
            "resolved_sku": product["sku"],
            "unit_price": product["unit_price"],
        })
        inv = check_inventory(product["sku"], item.quantity or 0)
        stock_available = inv["sufficient"]

    log_msg = (
        f"customer={'found' if customer['found'] else 'NOT FOUND'} "
        f"product={'found:' + product.get('sku', '') if product_found else 'NOT FOUND'} "
        f"stock={'ok' if stock_available else 'insufficient'}"
    )

    return {
        "customer_name": customer_name,
        "customer_tier": customer_tier,
        "extracted_items": [updated_item],
        "product_found": product_found,
        "stock_available": stock_available,
        "nodes_visited": _visited(state, node),
        "audit_log": _log(state, node, log_msg),
    }


async def validate_and_route_node(state: QuoteState) -> dict:
    node = "validate_route"

    if state.missing_fields:
        status = "clarification"
    elif not customer_exists(state.customer_id):
        status = "unknown_customer"
    elif not state.product_found:
        status = "unknown_product"
    elif not state.stock_available:
        status = "no_stock"
    else:
        status = "calculating"

    return {
        "status": status,
        "nodes_visited": _visited(state, node),
        "audit_log": _log(state, node, f"routed to status={status}"),
    }


async def calculate_node(state: QuoteState) -> dict:
    node = "calculate"
    item = state.extracted_items[0]

    pricing = get_pricing(
        sku=item.resolved_sku,
        quantity=item.quantity,
        unit_price=item.unit_price,
        customer_tier=state.customer_tier,
        requested_discount=item.requested_discount,
    )

    calculation = QuoteCalculation(
        sku=pricing["sku"],
        quantity=pricing["quantity"],
        unit_price=pricing["unit_price"],
        subtotal=pricing["subtotal"],
        discount_pct=pricing["discount_pct"],
        discount_amount=pricing["discount_amount"],
        total_usd=pricing["total_usd"],
        applied_tier=pricing["applied_tier"],
    )

    reasons: list[str] = []
    if calculation.total_usd > settings.approval_threshold_usd:
        reasons.append(f"Total USD {calculation.total_usd:,.2f} supera el umbral de {settings.approval_threshold_usd:,.0f}")
    if pricing["capped"]:
        reasons.append(
            f"Descuento solicitado ({item.requested_discount:.0%}) supera el máximo del tier "
            f"{state.customer_tier} ({pricing['discount_pct']:.0%})"
        )

    requires_approval = bool(reasons)

    return {
        "calculation": calculation,
        "requires_human_approval": requires_approval,
        "approval_reasons": reasons,
        "nodes_visited": _visited(state, node),
        "audit_log": _log(state, node, f"total={calculation.total_usd:.2f} requires_approval={requires_approval}"),
    }


async def draft_quote_node(state: QuoteState) -> dict:
    node = "draft"
    calc = state.calculation
    llm = ChatAnthropic(
        model="claude-opus-4-5",
        api_key=settings.anthropic_api_key,
    )

    system = (
        "Redacta un borrador de cotización profesional en español para AndesPro Industrial. "
        "Usa EXCLUSIVAMENTE los datos numéricos que se te proporcionan. "
        "No calcules ni modifiques precios."
    )

    context = (
        f"Cliente: {state.customer_name} (Tier: {calc.applied_tier})\n"
        f"Producto SKU: {calc.sku}\n"
        f"Cantidad: {calc.quantity} unidades\n"
        f"Precio unitario: USD {calc.unit_price:,.2f}\n"
        f"Subtotal: USD {calc.subtotal:,.2f}\n"
        f"Descuento ({calc.discount_pct:.0%}): -USD {calc.discount_amount:,.2f}\n"
        f"TOTAL: USD {calc.total_usd:,.2f}\n"
        f"Lugar de entrega: {state.delivery_location or 'Por confirmar'}\n"
        f"Fecha requerida: {state.required_delivery_date or 'Por confirmar'}\n"
    )

    response = await llm.ainvoke([
        {"role": "system", "content": system},
        {"role": "user", "content": f"Genera el borrador con estos datos:\n\n{context}"},
    ])

    return {
        "draft_quote": response.content,
        "status": "completed",
        "nodes_visited": _visited(state, node),
        "audit_log": _log(state, node, "draft generated"),
    }


async def clarify_node(state: QuoteState) -> dict:
    node = "clarify"

    status = state.status

    if status == "unknown_customer":
        msg = f"No se encontró el cliente con ID '{state.customer_id}' en el sistema. Verifique el identificador antes de continuar."
    elif status == "unknown_product":
        item = state.extracted_items[0] if state.extracted_items else None
        hint = item.sku_hint if item else "desconocido"
        msg = f"No se encontró el producto '{hint}' en el catálogo. Proporcione el SKU exacto o revise el nombre del producto."
    elif status == "no_stock":
        item = state.extracted_items[0] if state.extracted_items else None
        sku = item.resolved_sku or (item.sku_hint if item else "desconocido")
        qty = item.quantity if item else "?"
        msg = f"Stock insuficiente para {sku} (solicitado: {qty} unidades). Consulte disponibilidad o ajuste la cantidad."
    else:
        # missing_fields
        fields = ", ".join(state.missing_fields)
        msg = f"Faltan datos obligatorios para procesar la cotización: {fields}. Por favor, proporcione esta información."

    return {
        "clarification_request": msg,
        "status": "clarification",
        "nodes_visited": _visited(state, node),
        "audit_log": _log(state, node, f"clarification: {msg}"),
    }


async def human_approval_node(state: QuoteState) -> dict:
    node = "human_approval"
    # LangGraph interrumpe ANTES de ejecutar este nodo (interrupt_before=["human_approval"]).
    # Cuando se reanuda, human_decision ya está seteado en el estado.
    return {
        "status": "awaiting_approval",
        "nodes_visited": _visited(state, node),
        "audit_log": _log(state, node, "awaiting human approval"),
    }


async def apply_decision_node(state: QuoteState) -> dict:
    node = "apply_decision"
    decision = state.human_decision

    if decision and decision.action == "approved":
        return {
            "status": "approved",
            "nodes_visited": _visited(state, node),
            "audit_log": _log(state, node, f"approved by {decision.decided_by}"),
        }

    reason = decision.comment if decision else "Sin motivo especificado"
    return {
        "status": "rejected",
        "rejection_reason": reason,
        "nodes_visited": _visited(state, node),
        "audit_log": _log(state, node, f"rejected: {reason}"),
    }
