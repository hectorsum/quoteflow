import uuid
from typing import Annotated
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

from app.graph.state import QuoteState, HumanDecision
from app.core.database import save_quote, update_quote_status, get_quote_meta, list_quotes_meta

router = APIRouter(prefix="/quotes", tags=["quotes"], redirect_slashes=False)


class CreateQuoteRequest(BaseModel):
    customer_id: str
    raw_request: str


class ResumeQuoteRequest(BaseModel):
    action: str  # "approved" | "rejected"
    comment: str = ""
    decided_by: str = "executive"


def get_graph(request: Request):
    return request.app.state.graph

@router.post("")
async def create_quote(body: CreateQuoteRequest, graph=Depends(get_graph)):
    quote_id = str(uuid.uuid4())
    await save_quote(quote_id, body.customer_id, body.raw_request)

    initial_state = QuoteState(
        quote_id=quote_id,
        customer_id=body.customer_id,
        raw_request=body.raw_request,
    )
    config = {"configurable": {"thread_id": quote_id}}

    try:
        async for _ in graph.astream(initial_state.model_dump(), config):
            pass

        snapshot = await graph.aget_state(config)
        current_status = snapshot.values.get("status", "pending") if snapshot else "pending"
        await update_quote_status(quote_id, current_status)

        return {
            "quote_id": quote_id,
            "status": current_status,
            "message": _status_message(current_status),
        }
    except Exception as exc:
        await update_quote_status(quote_id, "error")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("")
async def list_quotes():
    return await list_quotes_meta()


@router.get("/{quote_id}")
async def get_quote(quote_id: str, graph=Depends(get_graph)):
    meta = await get_quote_meta(quote_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    config = {"configurable": {"thread_id": quote_id}}
    try:
        snapshot = await graph.aget_state(config)
        if not snapshot or not snapshot.values:
            return {**meta, "graph_state": None, "next_nodes": []}

        return {
            **meta,
            "graph_state": snapshot.values,
            "next_nodes": list(snapshot.next) if snapshot.next else [],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/{quote_id}/resume")
async def resume_quote(quote_id: str, body: ResumeQuoteRequest, graph=Depends(get_graph)):
    meta = await get_quote_meta(quote_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if body.action not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="action debe ser 'approved' o 'rejected'")

    config = {"configurable": {"thread_id": quote_id}}

    try:
        snapshot = await graph.aget_state(config)
        if not snapshot or not snapshot.next:
            raise HTTPException(status_code=409, detail="La solicitud no está esperando aprobación")

        human_decision = HumanDecision(
            action=body.action,
            comment=body.comment or None,
            decided_by=body.decided_by,
        )

        # Inyectar decisión y reanudar desde apply_decision
        await graph.aupdate_state(
            config,
            {"human_decision": human_decision.model_dump()},
            as_node="human_approval",
        )

        async for _ in graph.astream(None, config):
            pass

        snapshot = await graph.aget_state(config)
        current_status = snapshot.values.get("status", "completed") if snapshot else "completed"
        draft = snapshot.values.get("draft_quote") if snapshot else None

        await update_quote_status(quote_id, current_status)

        return {
            "quote_id": quote_id,
            "status": current_status,
            "draft_quote": draft,
            "message": _status_message(current_status),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


def _status_message(status: str) -> str:
    return {
        "completed": "Borrador de cotización generado correctamente",
        "awaiting_approval": "Solicitud pausada — requiere aprobación del ejecutivo",
        "clarification": "Se necesita información adicional del cliente",
        "unknown_product": "Producto no encontrado en el catálogo",
        "no_stock": "Sin stock suficiente para esta solicitud",
        "rejected": "Solicitud rechazada",
        "error": "Error procesando la solicitud",
    }.get(status, "Procesando")
