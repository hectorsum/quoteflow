# Business Case: QuoteFlow para AndesPro Industrial

## Usuario y proceso actual

El ejecutivo comercial de AndesPro Industrial recibe solicitudes de cotización B2B por tres canales: correo electrónico, formularios web y WhatsApp. Cada solicitud llega en texto libre y requiere una secuencia manual de pasos:

1. Identificar al cliente en el sistema interno (tier: Gold / Silver / Standard)
2. Interpretar los productos solicitados y sus cantidades desde el texto libre
3. Consultar el catálogo para confirmar SKUs, precios vigentes y stock disponible
4. Aplicar la política de descuentos correspondiente al tier del cliente
5. Calcular el subtotal, descuentos e IVA
6. Redactar la respuesta de cotización en español formal
7. Archivar la solicitud y el borrador enviado

Tiempo promedio estimado por cotización: **20–25 minutos**. Con un volumen de 15–20 solicitudes semanales, el ejecutivo dedica entre 5 y 8 horas por semana exclusivamente a preparar cotizaciones.

---

## Problema

El proceso es **100% manual** y presenta cuatro fallas sistémicas:

- **Errores de política:** el ejecutivo aplica descuentos incorrectos cuando la solicitud es compleja o el cliente tiene tier mixto — no hay validación automática.
- **Sin trazabilidad:** no existe registro de qué reglas se aplicaron, qué alternativas se consideraron ni quién aprobó cada decisión.
- **No escala:** a mayor volumen, el cuello de botella es el ejecutivo. No hay forma de distribuir o automatizar parcialmente la carga.
- **Calidad inconsistente:** el formato y completitud de las cotizaciones varía según la carga de trabajo del día.

---

## Hipótesis de valor

> **QuoteFlow puede reducir el tiempo de preparación de borrador de ~25 minutos a menos de 5 minutos, manteniendo control humano total sobre la decisión final.**

Hipótesis secundaria: cero errores de política de descuento en cotizaciones procesadas por QuoteFlow, porque el cálculo es determinista y la validación es automática.

---

## MVP y no alcance

**MVP (lo que se construye):**
`Registrar solicitud → Extraer intención (LLM) → Consultar dominio (catálogo, stock, política) → Validar y rutear → Calcular precio (determinista) → Pausar para aprobación humana si aplica → Generar borrador`

**No alcance del MVP:**
- Autenticación y autorización empresarial
- Integración real con email, WhatsApp o ERP
- Facturación o documentos legales
- Envío automático al cliente (el sistema nunca envía)
- Multi-idioma y diseño visual avanzado

---

## Métricas de éxito

| Métrica | Línea base | Objetivo MVP |
|---|---|---|
| Tiempo de preparación por cotización | ~25 min | < 5 min |
| Tasa de errores de política de descuento | Desconocida (manual) | 0% en procesadas por QuoteFlow |
| Adopción del ejecutivo piloto | — | > 80% de solicitudes en semana 2 |

---

## Guardrails (líneas que el sistema nunca cruza)

1. **El sistema nunca envía mensajes al cliente.** Solo genera borradores que el ejecutivo revisa y envía manualmente.
2. **Toda cotización superior a USD 10,000 requiere aprobación humana explícita** antes de generar el borrador final.
3. **Toda excepción a la política de descuento requiere aprobación humana** — el sistema no puede auto-aprobar descuentos fuera del rango del tier.
4. **El LLM no puede inventar datos:** clientes, SKUs, precios, stock, políticas y descuentos provienen exclusivamente de fuentes de dominio controladas.

---

## Principales riesgos

| Riesgo | Mitigación |
|---|---|
| LLM malinterpreta SKUs o cantidades en texto ambiguo | Structured output + validación contra catálogo real; productos no reconocidos van a ruta de aclaración |
| Latencia del LLM frustra al ejecutivo | Feedback de estado en tiempo real (streaming de nodos del grafo) |
| Resistencia al cambio del ejecutivo | Piloto acotado de 2 semanas; el proceso manual sigue disponible en paralelo |

---

## Nivel de autonomía: L2 — El sistema propone, el humano aprueba

El sistema ejecuta el análisis completo y genera un borrador, pero el ejecutivo revisa, modifica si es necesario y decide el envío. Para casos de alto valor o excepción de política, el grafo se detiene y espera aprobación explícita antes de continuar.

---

## Propuesta de piloto

- **Duración:** 2 semanas
- **Participantes:** 1 ejecutivo comercial de AndesPro
- **Modalidad:** procesamiento real en paralelo con el flujo manual existente
- **Criterio de éxito:** 8 de 10 cotizaciones piloto producen un borrador correcto sin intervención adicional del ejecutivo
- **Criterio de no-éxito y parada:** más de 3 borradores con errores de política en la primera semana → revisión del pipeline de validación antes de continuar
