# ADR-001: Python + FastAPI + LangGraph como stack de backend

**Fecha:** 2025-06-26
**Estado:** Aceptado

---

## Contexto

El reto requiere implementar un workflow agéntico con LangGraph en un timebox de 6 horas. El candidato tiene experiencia primaria en TypeScript/Node.js (NestJS), pero LangGraph tiene dos implementaciones: Python (`langgraph`) y TypeScript (`@langchain/langgraph`).

La decisión más crítica del proyecto es el stack de backend, porque determina:
- La madurez del checkpointer persistente (necesario para durable interrupt)
- La disponibilidad de ejemplos de interrupt/resume en la documentación oficial
- La velocidad de implementación dadas las capacidades del candidato

---

## Decisión

Usar **Python 3.11 + FastAPI + LangGraph (Python)** en el backend. Mantener **Next.js 14** en el frontend, por ser el stack de mayor dominio del candidato para UI.

---

## Consecuencias positivas

- **LangGraph Python es la implementación canónica:** documentación completa, más ejemplos de interrupt/resume, checkpointers maduros (SQLite via `langgraph-checkpoint-sqlite`, Postgres disponible para producción).
- **FastAPI tiene DX similar a NestJS:** decoradores, tipado explícito, async nativo, validación con Pydantic — la curva de adaptación es mínima para un desarrollador NestJS.
- **Pydantic v2 para el estado tipado del grafo** es más expresivo que Zod para modelar `QuoteState` con campos opcionales y discriminated unions.
- **En caso de bloqueo técnico**, la comunidad, ejemplos en GitHub y respuestas en Stack Overflow están en Python — reduce el riesgo de perder tiempo buscando workarounds.
- **Reduce el riesgo técnico en el componente más crítico del reto** (el grafo agéntico con interrupt durable), a costa de menor velocidad de escritura en el lenguaje.

---

## Consecuencias negativas

- El backend está en Python mientras el frontend está en TypeScript: **dos lenguajes en el mismo proyecto**. Aumenta la fricción de setup (dos entornos virtuales) y reduce la portabilidad del código entre capas.
- **El candidato escribe Python más lentamente que TypeScript.** La ganancia en madurez de la librería compensa esta diferencia, pero se debe monitorear en la Fase 1.

---

## Alternativas consideradas

### TypeScript full-stack (Next.js + `@langchain/langgraph`)

**Descartado.** El checkpointer SQLite para JS (`@langchain/langgraph-checkpoint-sqlite`) tiene menor madurez y documentación que su equivalente Python. Los ejemplos oficiales de interrupt/resume con checkpointer persistente son escasos en la versión JS. En un timebox de 6 horas, este riesgo no es aceptable.

### TypeScript full-stack (Next.js + LangChain.js sin LangGraph)

**Descartado.** El reto exige LangGraph explícitamente para el control de flujo agéntico con interrupt durable. LangChain.js sin LangGraph no provee el mecanismo de checkpointing ni el interrupt/resume que son requisitos funcionales del MVP.

---

## Verificación

**Condición de éxito de la Fase 1:** el grafo compila, los 3 casos de prueba (estándar, incompleto, aprobación) pasan con `MemorySaver`, y el interrupt/resume funciona sin restart.

Si esta condición se cumple antes de los 90 minutos de la Fase 1, la decisión fue correcta y se procede con SQLite checkpointer en la Fase 2.

Si el candidato se bloquea más de 30 minutos en el interrupt/resume de LangGraph Python, se reevalúa migrar a una simulación de estado en FastAPI puro (degradación controlada, sin LangGraph).
