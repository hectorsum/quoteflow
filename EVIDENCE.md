# EVIDENCE.md — Evidencia de ejecución

> Los SKUs y clientes usados aquí son los reales del MVP (ver
> `backend/app/domain/catalog/data.py` y `customers/data.py`).
> Clientes: `CLI-001` Gold (máx 20%), `CLI-002` Silver (máx 12%), `CLI-003` Standard (máx 5%).
> Umbral de aprobación: USD 10,000.

## Comandos para levantar el sistema

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con ANTHROPIC_API_KEY real
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local   # o .env
npm run dev
# Abre http://localhost:3000
```

### Tests (sin LLM real)
```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
# Esperado: 39 passed
```

> Nota de rutas: el endpoint de creación es `POST /quotes` (sin barra final).
> Con barra final (`/quotes/`) responde 404 — el router declara `@router.post("")`.

---

## Caso 1 — Solicitud estándar (→ completed)

**Input:**
```bash
curl -X POST http://localhost:8000/quotes \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CLI-001",
    "raw_request": "Necesito 5 bombas BOM-M16-A4 con 5% de descuento para entrega en Arequipa"
  }'
```
5 u × USD 1,850 = USD 9,250 (< umbral), stock suficiente, 5% ≤ 20% (Gold).

**Output esperado:**
```json
{
  "quote_id": "<uuid>",
  "status": "completed",
  "message": "Borrador de cotización generado correctamente"
}
```

**Verificar detalle:**
```bash
curl http://localhost:8000/quotes/<quote_id>
```
Debe contener `graph_state.draft_quote` (borrador en español) y `status: completed`.

---

## Caso 2 — Solicitud incompleta (→ clarification)

**Input:**
```bash
curl -X POST http://localhost:8000/quotes \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CLI-002",
    "raw_request": "necesito unas válvulas para mi planta"
  }'
```
Falta la cantidad → `missing_fields`.

**Output esperado:**
```json
{
  "quote_id": "<uuid>",
  "status": "clarification",
  "message": "Se necesita información adicional del cliente"
}
```
El detalle contiene `graph_state.clarification_request` con los campos faltantes.

---

## Caso 3 — Producto desconocido (→ unknown_product)

**Input:**
```bash
curl -X POST http://localhost:8000/quotes \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CLI-001",
    "raw_request": "Necesito 5 unidades de PRODUCTO-XYZ"
  }'
```
El SKU no existe en el catálogo.

**Output esperado:** `status: "unknown_product"` con `clarification_request` específico.

---

## Caso 4 — Alto valor con aprobación humana (→ awaiting_approval → completed)

**Paso 1 — Crear solicitud:**
```bash
curl -X POST http://localhost:8000/quotes \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CLI-001",
    "raw_request": "Solicito 6 bombas BOM-M16-A4 para Lima"
  }'
```
6 u × USD 1,850 = USD 11,100 (> umbral) → requiere aprobación.

**Output esperado:**
```json
{
  "quote_id": "<uuid>",
  "status": "awaiting_approval",
  "message": "Solicitud pausada — requiere aprobación del ejecutivo"
}
```

**Paso 2 — Verificar interrupt:**
```bash
curl http://localhost:8000/quotes/<quote_id>
# next_nodes debe contener ["human_approval"]
```

**Paso 3 — Aprobar:**
```bash
curl -X POST http://localhost:8000/quotes/<quote_id>/resume \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approved",
    "comment": "Autorizado por gerencia",
    "decided_by": "gerente_comercial"
  }'
```

**Output esperado:**
```json
{
  "quote_id": "<uuid>",
  "status": "completed",
  "draft_quote": "Estimado cliente..."
}
```

(Para rechazo: `"action": "rejected"` → `status: "rejected"` con `rejection_reason`.)

---

## Caso 5 — Descuento sobre el tier (→ awaiting_approval por política)

```bash
curl -X POST http://localhost:8000/quotes \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CLI-003",
    "raw_request": "Necesito 2 válvulas VAL-GAT-2P con 10% de descuento"
  }'
```
Cliente Standard (máx 5%) pide 10% → `requires_human_approval` por política,
aunque el total sea bajo.

---

## Verificar reanudación durable (restart real sobre SQLite)

```bash
# 1. Crear solicitud de alto valor (queda en awaiting_approval)
curl -X POST http://localhost:8000/quotes -H "Content-Type: application/json" \
  -d '{"customer_id": "CLI-001", "raw_request": "Solicito 6 bombas BOM-M16-A4"}'

# 2. Guardar el quote_id, detener el servidor (Ctrl+C)
# 3. Reiniciar el servidor (el checkpointer lee quoteflow.db)
uvicorn app.main:app --reload --port 8000

# 4. El estado debe persistir
curl http://localhost:8000/quotes/<quote_id>
# status sigue siendo "awaiting_approval", next_nodes = ["human_approval"]

# 5. Reanudar normalmente
curl -X POST http://localhost:8000/quotes/<quote_id>/resume \
  -H "Content-Type: application/json" \
  -d '{"action": "approved", "comment": "OK", "decided_by": "exec"}'
```
