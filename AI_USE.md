# AI_USE.md — Uso de IA en este proyecto

## Herramientas utilizadas

| Herramienta | Uso |
|-------------|-----|
| Claude (chat) | Diseño de arquitectura, decisiones técnicas, redacción de documentación |
| Claude Code | Generación del scaffold e implementación de archivos por fase |
| Claude API (`claude-opus-4-5` vía `langchain-anthropic`) | LLM en runtime: extracción de intención y redacción de borradores |

El modelo en runtime está fijado en `backend/app/graph/nodes.py`
(`extract_intent_node` y `draft_quote_node`).

---

## Qué generó la IA y qué se aceptó

- Estructura de directorios del proyecto — aceptado
- `backend/app/graph/state.py` (tipos Pydantic) — aceptado, con revisión de nombres de campos (se añadió `quote_id` y `product_name`)
- `backend/app/domain/*/data.py` (datos mock y funciones deterministas) — aceptado
- `backend/app/domain/pricing/calculator.py` (descuentos por tier `TIER_MAX_DISCOUNT`) — verificado con tests unitarios
- `backend/app/graph/routing.py` (routing puro) — aceptado tras verificar todas las rutas
- `backend/app/graph/nodes.py` (nodos) — revisado; system prompt de extracción endurecido ("nunca inventes…")
- `backend/app/graph/builder.py` (compilación) — revisado; **se corrigieron dos bugs reales** (ver abajo)
- `backend/app/api/routes/quotes.py` (FastAPI) — revisado; se cambió a checkpointer compartido en `lifespan` vía `app.state` (no por request) y `@router.post("")` para evitar el 307/404 por barra final
- `frontend/app`, `frontend/components`, `frontend/lib` (Next.js, sin `src/`) — aceptado, con rediseño UX a light mode
- Tests unitarios e integración — aceptados, ejecutados y verificados en verde

## Qué se rechazó o corrigió

- Se evitó cualquier consulta de dominio (cliente/producto/stock/precio) por parte del LLM: todo eso vive en `domain/` y se invoca con funciones Python.
- Se reforzó el system prompt de redacción con "no calcules ni modifiques precios".
- El routing es 100% determinista (sin LLM), para que sea testeable sin mocks.
- **Dos bugs reales detectados por los tests de integración y corregidos:**
  1. `human_approval` apuntaba a `END` → `apply_decision` quedaba huérfano y la
     decisión humana nunca se aplicaba (sin borrador al aprobar, sin `rejected` al rechazar).
     Fix: `human_approval → apply_decision`.
  2. El status quedaba en `calculating` durante el interrupt → el panel de aprobación
     del frontend (que depende de `awaiting_approval`) nunca aparecía.
     Fix: `calculate_node` fija `awaiting_approval` antes de la pausa.

## Cómo se verificó cada output del LLM

- Funciones deterministas (pricing, routing, domain): tests unitarios.
- Nodos del grafo: tests de integración con `ChatAnthropic` mockeado vía `AsyncMock`
  sobre `ainvoke` (los nodos son async).
- Reglas de negocio críticas: cada una con al menos un test que la cubre.
- Interrupt/resume: `test_resume_after_approval` y `test_resume_after_rejection`.
- Durabilidad del checkpointer: `test_durability_same_thread_id_recovers_state`
  (mecanismo) + verificación manual sobre SQLite (ver EVIDENCE.md).
