# STATUS.md — Estado del MVP

## ✅ Implementado y verificado

- [x] Extracción de intención con LLM (structured output, Claude)
- [x] Consulta de dominio determinista (clientes, catálogo, inventario)
- [x] Routing automático sin LLM (clarify / unknown_customer / unknown_product / no_stock / calculate)
- [x] Status de salida distinguible por caso (clarification, unknown_product, no_stock, awaiting_approval, completed, rejected)
- [x] Cálculo de precio con funciones Python puras (`pricing/calculator.py`)
- [x] Interrupt durable para aprobación humana (`interrupt_before=["human_approval"]`)
- [x] Checkpointer SQLite persistente en la API (`AsyncSqliteSaver`, sobrevive restart)
- [x] Resume post-aprobación o rechazo (`human_approval → apply_decision → draft/reject`)
- [x] Generación de borrador en español (Claude)
- [x] API REST FastAPI (create / list / get / resume)
- [x] Frontend Next.js — bandeja de solicitudes con estado
- [x] Frontend Next.js — vista de detalle con trazabilidad
- [x] Frontend Next.js — panel de aprobación/rechazo con observación
- [x] Tests unitarios en verde (pricing, domain, routing)
- [x] Tests de integración en verde (8 casos con LLM mockeado)
- [x] Registro de auditoría (`nodes_visited`, `audit_log`, `errors`)

**Suite completa: `39 passed` (`cd backend && .venv/bin/pytest tests/`).**

## ⚠️ Notas de implementación (diferencias con lo "ideal")

- **Polling en frontend: deshabilitado.** El polling cada 3s causaba un loop de
  renders, por lo que se dejó refresco manual (al navegar o recargar). Re-habilitarlo
  con un patrón correcto (o WebSockets) es trabajo pendiente.
- **Durabilidad SQLite:** la API usa `AsyncSqliteSaver` real. El test de durabilidad
  (`test_durability_same_thread_id_recovers_state`) usa `MemorySaver` con el mismo
  checkpointer entre dos grafos como prueba lógica del mecanismo; la persistencia
  cross-restart sobre disco se valida manualmente (ver EVIDENCE.md).

## ⚠️ Deuda técnica conocida

- Inventario mock en memoria — no transaccional (la reserva de stock no persiste entre restarts)
- Un solo item por solicitud — multi-item no implementado
- Sin autenticación en la API (cualquiera puede aprobar/rechazar)
- Refresco manual en frontend en lugar de polling/WebSockets para estado en tiempo real
- Sin rate limiting ni manejo de cuota de la API de Anthropic
- Error handling básico — no hay retry automático si el LLM falla

## ❌ Fuera de scope (priorizado y documentado)

- Autenticación y autorización empresarial
- Integración con email, WhatsApp o ERP real
- Multi-idioma
- Facturación o documentos legales
- Infraestructura productiva (CI/CD, Docker Compose completo)
- Envío automático al cliente

## Siguiente paso prioritario

Agregar soporte multi-item: que el LLM extraiga una lista de productos en lugar
de uno solo, y que `calculate_node` itere sobre todos.
Estimado: 2 horas. Impacto: cubre la mayoría de solicitudes reales de AndesPro.
Ver `LOOP.md` para el plan detallado.
