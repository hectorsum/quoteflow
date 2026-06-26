import { QuoteStatus } from "./api";

export type StatusGroup =
  | "pendiente"
  | "revision"
  | "aprobada"
  | "cerrada"
  | "rechazada";

// Cada estado del grafo mapeado a una etiqueta amigable y un grupo de negocio.
export const STATUS_META: Record<QuoteStatus, { label: string; group: StatusGroup }> = {
  pending:           { label: "Pendiente",            group: "pendiente" },
  extracting:        { label: "Extrayendo",           group: "pendiente" },
  validating:        { label: "Validando",            group: "pendiente" },
  calculating:       { label: "Calculando",           group: "pendiente" },
  clarification:     { label: "Requiere aclaración",  group: "revision" },
  unknown_product:   { label: "Producto desconocido", group: "revision" },
  unknown_customer:  { label: "Cliente desconocido",  group: "revision" },
  no_stock:          { label: "Sin stock",            group: "revision" },
  awaiting_approval: { label: "Esperando aprobación", group: "revision" },
  approved:          { label: "Aprobado",             group: "aprobada" },
  completed:         { label: "Completado",           group: "cerrada" },
  rejected:          { label: "Rechazado",            group: "rechazada" },
  error:             { label: "Error",                group: "rechazada" },
};

// Metadatos visuales por grupo (colores cálidos, light mode).
export const GROUP_META: Record<
  StatusGroup,
  { label: string; dot: string; bar: string; badgeBg: string; badgeText: string }
> = {
  pendiente: {
    label: "Pendiente",
    dot: "#b3a589",
    bar: "#c4b89d",
    badgeBg: "#ece4d6",
    badgeText: "#7a6f5c",
  },
  revision: {
    label: "En revisión",
    dot: "#d39a4b",
    bar: "#d39a4b",
    badgeBg: "#f6e9d3",
    badgeText: "#a8702a",
  },
  aprobada: {
    label: "Aprobada",
    dot: "#6aa37e",
    bar: "#6aa37e",
    badgeBg: "#dcebe0",
    badgeText: "#3f7d56",
  },
  cerrada: {
    label: "Cerrada",
    dot: "#4a453d",
    bar: "#4a453d",
    badgeBg: "#e6e1d8",
    badgeText: "#4a453d",
  },
  rechazada: {
    label: "Rechazada",
    dot: "#c5544a",
    bar: "#c5544a",
    badgeBg: "#f3dcd9",
    badgeText: "#b04135",
  },
};

export const GROUP_ORDER: StatusGroup[] = [
  "pendiente",
  "revision",
  "aprobada",
  "cerrada",
  "rechazada",
];

export function groupOf(status: QuoteStatus): StatusGroup {
  return STATUS_META[status]?.group ?? "pendiente";
}

export function labelOf(status: QuoteStatus): string {
  return STATUS_META[status]?.label ?? status;
}
