# PROJECT.md — QuoteFlow MVP

## Objetivo

Construir QuoteFlow MVP: sistema agéntico full-stack que asiste al ejecutivo de AndesPro Industrial en la preparación de borradores de cotización B2B, con human-in-the-loop durable y trazabilidad completa.

---

## Alcance

- Registro de solicitudes en lenguaje natural con identificador de cliente
- Extracción estructurada de intención mediante LLM: productos, cantidades, descuento solicitado, ubicación de entrega, fecha requerida
- Consulta de dominio determinista: catálogo de productos, inventario, precios vigentes, política comercial por tier
- Validación y routing automático hacia uno de cuatro caminos: completo / aclaración / producto desconocido / sin stock / requiere aprobación
- Cálculo de precio exclusivamente mediante funciones deterministas (nunca LLM)
- Interrupción durable del grafo para aprobación humana — el estado persiste ante restart del servidor
- Generación de borrador de cotización en español, listo para revisión del ejecutivo
- UI para crear solicitudes, ver bandeja de trabajo, inspeccionar detalle de nodos ejecutados y aprobar/rechazar
- Registro de auditoría: nodos ejecutados, timestamps, decisiones humanas, errores

---

## No alcance

- Autenticación y autorización empresarial
- Integración con sistemas reales (email, WhatsApp, ERP, CRM)
- Facturación o documentos legales
- Envío automático al cliente
- Infraestructura productiva — Docker Compose es suficiente para el MVP
- Diseño visual avanzado

---

## Reglas de negocio críticas

1. **El LLM no puede inventar datos:** clientes, productos, precios, stock, descuentos ni aprobaciones provienen exclusivamente de fuentes de dominio controladas.
2. **Umbral de valor:** toda cotización superior a USD 10,000 requiere aprobación humana antes de generar el borrador final.
3. **Umbral de descuento:** todo descuento que supere el máximo permitido para el tier del cliente requiere aprobación humana.
4. **Cliente desconocido:** un cliente no encontrado en el sistema requiere revisión manual antes de continuar con la cotización.
5. **Información incompleta:** si falta producto o cantidad, el sistema solicita aclaración antes de cotizar — no asume ni inventa.
6. **Idempotencia:** la misma decisión humana no puede generar efectos duplicados; el grafo verifica el estado antes de aplicar una reanudación.
7. **Prompt injection:** el texto del cliente es entrada no confiable y no puede modificar políticas ni instrucciones del sistema.

---

## Criterios de aceptación (Definition of Done)

- [ ] Aplicación ejecutable desde README en entorno limpio (solo `pip install` + `npm install`)
- [ ] Tres casos demostrados end-to-end: caso estándar, caso incompleto, caso con aprobación requerida
- [ ] Reanudación durable: restart del servidor no pierde el estado del grafo (checkpointer SQLite)
- [ ] Reglas protegidas: ningún test ni caso muestra datos inventados por el LLM
- [ ] Tests unitarios en verde sin dependencia de modelo externo (mocks para el LLM)
- [ ] Documentación viva coincide con el código al momento de entrega
- [ ] Otra persona puede continuar el desarrollo sin reconstruir el contexto desde cero

---

## Arquitectura de alto nivel

```
Frontend (Next.js 14)
  └── /app
        ├── page.tsx              # Bandeja de solicitudes
        ├── new/page.tsx          # Crear solicitud
        └── [id]/page.tsx         # Detalle + aprobación

Backend (FastAPI + LangGraph)
  └── app/
        ├── main.py               # FastAPI app, rutas REST
        ├── graph/
        │     ├── state.py        # QuoteState (Pydantic)
        │     ├── nodes.py        # Nodos del grafo
        │     ├── edges.py        # Routing condicional
        │     └── graph.py        # Compilación + checkpointer SQLite
        ├── domain/
        │     ├── catalog.py      # Catálogo y stock (datos seed)
        │     ├── pricing.py      # Cálculo determinista de precios
        │     └── policy.py       # Reglas de descuento por tier
        └── schemas.py            # Modelos de API (Pydantic)
```

### Flujo del grafo LangGraph

```
[START]
  → extract_intent          # LLM: texto libre → intención estructurada
  → lookup_domain           # Determinista: catálogo, stock, política
  → validate_and_route      # Routing condicional
       ├─ needs_clarification  → [INTERRUPT] espera aclaración → extract_intent
       ├─ unknown_product      → genera respuesta de error
       ├─ no_stock             → genera respuesta de alternativa
       ├─ needs_approval       → [INTERRUPT] espera aprobación humana
       └─ complete             → calculate_price → generate_draft
  → [END]
```

---

## Restricciones técnicas

- **LangGraph** obligatorio con checkpointer persistente (SQLite para MVP)
- **Interrupt real** para human-in-the-loop — no simulado con flags en base de datos
- **Estado explícito y tipado** con Pydantic v2 (`QuoteState`)
- **Cálculos de precio y validación de políticas:** solo funciones Python deterministas, nunca LLM
- **Python 3.11** en backend; **Node.js 20 / Next.js 14** en frontend

---

## Datos seed (MVP)

El MVP opera con datos en memoria / JSON para evitar dependencias de base de datos externa:

- **3 clientes:** uno Gold, uno Silver, uno Standard
- **10–15 productos** con SKU, descripción, precio USD y stock
- **Política de descuentos:** Gold ≤ 20%, Silver ≤ 12%, Standard ≤ 5%
- **Umbral de aprobación:** USD 10,000

---

## Stack y dependencias clave

| Componente | Tecnología |
|---|---|
| Backend framework | FastAPI 0.111 |
| Workflow agéntico | LangGraph 0.2 |
| Estado del grafo | Pydantic v2 |
| Persistencia del grafo | SQLite (via LangGraph checkpointer) |
| LLM | Claude claude-sonnet-4-6 (structured output) |
| Frontend framework | Next.js 14 (App Router) |
| UI components | shadcn/ui + Tailwind CSS |
| HTTP client (frontend) | fetch nativo / SWR |
| Tests backend | pytest + pytest-asyncio |

---

## Fases de implementación (timebox 6h)

| Fase | Contenido | Tiempo |
|---|---|---|
| 1 | Grafo LangGraph con MemorySaver + 3 casos de prueba | 1.5h |
| 2 | FastAPI REST + SQLite checkpointer + endpoints CRUD | 1.5h |
| 3 | Frontend Next.js: bandeja, detalle, aprobación | 2h |
| 4 | Integración end-to-end + README ejecutable | 1h |
