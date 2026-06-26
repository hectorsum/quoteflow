const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface QuoteListItem {
  id: string;
  customer_id: string;
  status: QuoteStatus;
  created_at: string;
  updated_at: string;
}

export type QuoteStatus =
  | "pending"
  | "extracting"
  | "validating"
  | "clarification"
  | "unknown_product"
  | "unknown_customer"
  | "no_stock"
  | "calculating"
  | "awaiting_approval"
  | "approved"
  | "rejected"
  | "completed"
  | "error";

export interface ExtractedItem {
  sku_hint: string;
  resolved_sku: string | null;
  quantity: number | null;
  requested_discount: number;
}

export interface QuoteCalculation {
  sku: string;
  quantity: number;
  unit_price: number;
  discount_pct: number;
  subtotal: number;
  discount_amount: number;
  total_usd: number;
  applied_tier: string;
}

export interface HumanDecision {
  action: "approved" | "rejected";
  comment: string;
  decided_by: string;
}

export interface GraphState {
  quote_id: string;
  customer_id: string;
  raw_request: string;
  status: QuoteStatus;
  customer_name: string | null;
  customer_tier: string | null;
  extracted_items: ExtractedItem[];
  delivery_location: string | null;
  required_delivery_date: string | null;
  missing_fields: string[];
  product_found: boolean | null;
  stock_available: boolean | null;
  calculation: QuoteCalculation | null;
  requires_human_approval: boolean;
  approval_reasons: string[];
  human_decision: HumanDecision | null;
  draft_quote: string | null;
  clarification_request: string | null;
  rejection_reason: string | null;
  nodes_visited: string[];
  errors: string[];
  audit_log: string[];
}

export interface QuoteDetail extends QuoteListItem {
  graph_state: GraphState | null;
  next_nodes: string[];
}

export interface ResumePayload {
  action: "approved" | "rejected";
  comment: string;
  decided_by: string;
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Error en la API");
  }
  return res.json();
}

export const api = {
  createQuote: (customer_id: string, raw_request: string) =>
    apiFetch<{ quote_id: string; status: string; message: string }>("/quotes", {
      method: "POST",
      body: JSON.stringify({ customer_id, raw_request }),
    }),

  listQuotes: () => apiFetch<QuoteListItem[]>("/quotes"),

  getQuote: (id: string) => apiFetch<QuoteDetail>(`/quotes/${id}`),

  resumeQuote: (id: string, payload: ResumePayload) =>
    apiFetch<{ quote_id: string; status: string; draft_quote: string | null; message: string }>(
      `/quotes/${id}/resume`,
      { method: "POST", body: JSON.stringify(payload) }
    ),
};
