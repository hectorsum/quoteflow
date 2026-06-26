# LOOP.md — Ciclo de mejora prioritario

## Objetivo
Agregar soporte multi-item a QuoteFlow: que una solicitud pueda incluir varios
productos y cantidades, y que el sistema cotice todos juntos.

## Por qué es prioritario
La mayoría de las solicitudes reales de AndesPro incluyen más de un producto.
El MVP actual solo procesa el primer item extraído (`extracted_items[0]`).

## Worker
Claude Code con acceso a `backend/app/graph/` y `backend/tests/`.

## Verifier
- Test de integración: solicitud con 2 productos → la cotización contiene 2 líneas.
- Test unitario: `calculate_price` llamado N veces → total es la suma correcta.
- Demo manual: "10 bombas BOM-M16-A4 y 5 válvulas VAL-GAT-2P" → borrador con ambos productos.

## Estado inicial (problema concreto)
- `extract_intent_node` extrae un único `sku_hint`/`quantity` (`IntentExtraction`).
- `calculate_node` procesa solo `state.extracted_items[0]`.
- `QuoteCalculation` representa un solo producto (no hay lista de líneas).

## Presupuesto
2 horas máximo.

## Condición de salida
Los 3 verifiers pasan. El caso de demo produce un borrador correcto con 2 líneas de producto.

## Condición de bloqueo
Si el structured output del LLM no extrae listas de items de forma consistente,
cambiar a extracción secuencial (un item a la vez) antes de invertir más tiempo.

## Handoff para la siguiente sesión
Archivos a modificar:
1. `backend/app/graph/state.py` → `IntentExtraction` con `items: list[...]`; agregar un
   tipo de línea de cálculo y una lista en el estado (o `QuoteCalculation` con `items`).
2. `backend/app/graph/nodes.py` → `extract_intent_node` con schema de lista;
   `calculate_node` iterando sobre todos los items y sumando totales.
3. `backend/app/graph/routing.py` → revisar `route_after_lookup` para validar todos los items
   (producto desconocido / sin stock si *cualquier* línea falla).
4. `backend/tests/integration/test_graph.py` → nuevo caso `test_multi_item_quote`.
5. `frontend/app/requests/[id]/page.tsx` → la sección "Cálculo de precio" como tabla
   con una fila por línea.

## Reglas que NO deben romperse
- El LLM sigue sin inventar SKUs/precios/stock: cada línea se valida contra el catálogo.
- El umbral de aprobación (USD 10,000) y el descuento por tier aplican al **total agregado**.
- Idempotencia del resume se mantiene.
