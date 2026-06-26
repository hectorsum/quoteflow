import { QuoteStatus } from "@/lib/api";

const STATUS_CONFIG: Record<QuoteStatus, { label: string; classes: string }> = {
  pending:            { label: "Pendiente",          classes: "bg-gray-700 text-gray-300" },
  extracting:         { label: "Extrayendo",          classes: "bg-blue-900 text-blue-300" },
  validating:         { label: "Validando",           classes: "bg-blue-900 text-blue-300" },
  calculating:        { label: "Calculando",          classes: "bg-blue-900 text-blue-300" },
  clarification:      { label: "Aclaración",          classes: "bg-yellow-900 text-yellow-300" },
  unknown_product:    { label: "Producto desconocido",classes: "bg-orange-900 text-orange-300" },
  unknown_customer:   { label: "Cliente desconocido", classes: "bg-orange-900 text-orange-300" },
  no_stock:           { label: "Sin stock",           classes: "bg-orange-900 text-orange-300" },
  awaiting_approval:  { label: "Esperando aprobación",classes: "bg-yellow-500 text-yellow-950 font-semibold" },
  approved:           { label: "Aprobado",            classes: "bg-green-900 text-green-300" },
  rejected:           { label: "Rechazado",           classes: "bg-red-900 text-red-300" },
  completed:          { label: "Completado",          classes: "bg-green-500 text-green-950 font-semibold" },
  error:              { label: "Error",               classes: "bg-red-900 text-red-400" },
};

export function StatusBadge({ status }: { status: QuoteStatus }) {
  const config = STATUS_CONFIG[status] ?? { label: status, classes: "bg-gray-700 text-gray-300" };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded text-xs font-mono ${config.classes}`}>
      {config.label}
    </span>
  );
}
