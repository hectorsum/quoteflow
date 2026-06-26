# ROADMAP.md — Fases de implementación de QuoteFlow MVP

Timebox total: 6 horas. Cuatro fases, cada una con tareas atómicas, archivos
afectados, pruebas y Definition of Done. Estado real marcado con `[x]`.

> Refleja lo efectivamente construido. La síntesis de alto nivel está en
> `PROJECT.md`; aquí está el detalle accionable por fase.

---

## Fase 1 — Grafo LangGraph (núcleo agéntico) · ~1.5h · ✅ Completada

**Objetivo:** workflow agéntico tipado que va de texto libre a borrador, con
routing determinista e interrupt para aprobación humana.

**Tareas atómicas**
- [x] Definir estado tipado `QuoteState` + sub-modelos (`ExtractedItem`, `QuoteCalculation`, `HumanDecision`)
- [x] Capa de dominio determinista: clientes, catálogo, inventario, pricing
- [x] Funciones puras de dominio (`domain_tools.py`) que el grafo invoca
- [x] 8 nodos async (extract, lookup, validate, calculate, draft, clarify, human_approval, apply_decision)
- [x] Routing condicional sin LLM (`routing.py`)
- [x] Compilar grafo con `interrupt_before=["human_approval"]`

**Archivos / módulos afectados**
- `backend/app/graph/state.py`, `nodes.py`, `routing.py`, `builder.py`
- `backend/app/domain/{customers,catalog,inventory,pricing}/`
- `backend/app/tools/domain_tools.py`
- `backend/app/core/config.py`

**Pruebas**
- `tests/unit/test_routing.py` — todas las rutas de decisión
- `tests/unit/test_pricing.py` — descuentos por tier, capeo, umbral
- `tests/unit/test_domain.py` — clientes, catálogo, inventario

**Definition of Done**
- [x] El grafo compila e imprime sus nodos
- [x] Los 3 casos base (estándar / incompleto / aprobación) recorren la ruta esperada
- [x] Ningún nodo de routing o cálculo usa el LLM

---

## Fase 2 — API REST FastAPI + persistencia · ~1.5h · ✅ Completada

**Objetivo:** exponer el grafo por HTTP con checkpointer durable e interrupt/resume real.

**Tareas atómicas**
- [x] `AsyncSqliteSaver` abierto una vez en `lifespan`, compartido vía `app.state`
- [x] SQLite de metadata de quotes (`core/database.py`)
- [x] Endpoints: `POST /quotes`, `GET /quotes`, `GET /quotes/{id}`, `POST /quotes/{id}/resume`
- [x] `thread_id = quote_id` para durabilidad
- [x] Resume inyecta `human_decision` y reanuda desde el interrupt

**Archivos / módulos afectados**
- `backend/app/main.py`
- `backend/app/api/routes/quotes.py`
- `backend/app/core/database.py`

**Pruebas**
- `tests/integration/test_graph.py` — interrupt/resume, durabilidad (mismo checkpointer)
- Verificación manual con `curl` (ver `EVIDENCE.md`)

**Definition of Done**
- [x] `GET /health` responde `{"status":"ok"}`
- [x] `POST /quotes` devuelve `quote_id` + `status`
- [x] El estado del grafo persiste y se recupera por `thread_id`

---

## Fase 3 — Frontend Next.js 14 · ~2h · ✅ Completada

**Objetivo:** UI operacional para crear, inspeccionar y decidir cotizaciones.

**Tareas atómicas**
- [x] Cliente API tipado (`lib/api.ts`)
- [x] Bandeja de solicitudes con estado (`app/requests/page.tsx`)
- [x] Detalle: extraídos, cálculo, riesgos, trazabilidad (`app/requests/[id]/page.tsx`)
- [x] Panel de aprobación/rechazo con observación
- [x] Formulario de creación (`components/quote/RequestForm.tsx`)
- [x] Rediseño light mode (sidebar, paleta cálida, `StatusBadge`, `lib/status.ts`)

**Archivos / módulos afectados**
- `frontend/app/layout.tsx`, `app/page.tsx`, `app/requests/page.tsx`, `app/requests/[id]/page.tsx`
- `frontend/components/Sidebar.tsx`, `components/quote/{StatusBadge,RequestForm}.tsx`
- `frontend/lib/api.ts`, `lib/status.ts`
- `frontend/tailwind.config.ts`, `app/globals.css`

**Pruebas**
- Verificación manual de los 3 flujos en navegador (crear, ver, aprobar/rechazar)
- Compilación sin errores de las rutas (`/requests`, `/requests/[id]`)

**Definition of Done**
- [x] Se puede crear una solicitud desde la UI
- [x] La bandeja lista solicitudes con su estado
- [x] El detalle muestra extraídos, cálculo, trazabilidad y borrador final
- [x] El panel de aprobación aparece en `awaiting_approval` y permite aprobar/rechazar

---

## Fase 4 — Tests, fixes y documentación de entrega · ~1h · ✅ Completada

**Objetivo:** suite verde sin LLM real, bugs corregidos y documentación viva.

**Tareas atómicas**
- [x] Mockear `ChatAnthropic` vía `AsyncMock` sobre `ainvoke`
- [x] Cobertura de integración: estándar, incompleto, producto desconocido, sin stock, aprobación, rechazo, durabilidad
- [x] Fix HITL: `human_approval → apply_decision` (nodo huérfano)
- [x] Fix status: `calculate_node` fija `awaiting_approval` antes del interrupt
- [x] Status distinguibles en `clarify_node` (unknown_product / no_stock)
- [x] Docs: STATUS, EVIDENCE, AI_USE, LOOP, IMPACT, este ROADMAP

**Archivos / módulos afectados**
- `backend/tests/` (unit + integration), `pytest.ini`, `conftest.py`
- `backend/app/graph/builder.py`, `nodes.py` (fixes)
- Documentos raíz `.md` + `docs/`

**Pruebas**
- `cd backend && .venv/bin/pytest tests/` → **`39 passed`**

**Definition of Done**
- [x] Toda la suite pasa sin dependencia de modelo externo
- [x] Los 5 outcomes de negocio son distinguibles por status
- [x] La documentación coincide con el código (verificado contra `nodes.py`, `calculator.py`, rutas API)

---

## Próxima fase candidata (no incluida en el timebox)

**Fase 5 — Soporte multi-item.** Plan detallado en `LOOP.md` (objetivo, verifier,
presupuesto 2h, condición de bloqueo y handoff de archivos).
