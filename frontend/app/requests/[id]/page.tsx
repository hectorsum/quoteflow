"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, QuoteDetail, QuoteStatus } from "@/lib/api";
import { StatusBadge } from "@/components/quote/StatusBadge";

export default function QuoteDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [quote, setQuote] = useState<QuoteDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [comment, setComment] = useState("");
  const [resuming, setResuming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchQuote = async () => {
    try {
      const data = await api.getQuote(id);
      setQuote(data);
      setError(null);
    } catch (e) {
      console.error("Error fetching quote:", e);
      setError(e instanceof Error ? e.message : "Error al cargar la solicitud");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuote();
  }, [id]);

  async function handleDecision(action: "approved" | "rejected") {
    setResuming(true);
    setError(null);
    try {
      await api.resumeQuote(id, { action, comment, decided_by: "executive" });
      await fetchQuote();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al procesar la decisión");
    }
    setResuming(false);
  }

  if (loading) return <div className="px-10 py-8"><p className="text-ink-400 text-sm">Cargando...</p></div>;
  if (!quote) return <div className="px-10 py-8"><p className="text-red-600 text-sm">{error || "Solicitud no encontrada"}</p></div>;

  const gs = quote.graph_state;

  return (
    <div className="px-10 py-8 max-w-3xl">
      <button onClick={() => router.push("/requests")} className="text-ink-500 hover:text-ink-700 text-sm mb-4">
        ← Volver a solicitudes
      </button>

      <header className="border-b border-line pb-6 mb-8">
        <p className="text-ink-400 text-xs tracking-[0.18em] uppercase">Solicitud</p>
        <h1 className="font-serif text-3xl font-semibold text-ink-900 mt-1 font-mono">{id.slice(0, 8)}</h1>
        <div className="flex items-center gap-3 mt-3">
          <StatusBadge status={quote.status as QuoteStatus} />
          <span className="text-ink-500 text-sm">{quote.customer_id}</span>
          <span className="text-ink-400 text-xs">{new Date(quote.created_at).toLocaleString("es-PE")}</span>
        </div>
      </header>

      <div className="flex flex-col gap-6">
        <Section title="Solicitud original">
          <p className="text-ink-700 text-sm leading-relaxed">{gs?.raw_request || "—"}</p>
        </Section>

        {gs && gs.extracted_items.length > 0 && (
          <Section title="Extracción de intención">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-ink-400 text-xs">
                  <th className="text-left pb-2 font-medium">Texto del cliente</th>
                  <th className="text-left pb-2 font-medium">SKU resuelto</th>
                  <th className="text-left pb-2 font-medium">Cantidad</th>
                  <th className="text-left pb-2 font-medium">Descuento</th>
                </tr>
              </thead>
              <tbody>
                {gs.extracted_items.map((item, i) => (
                  <tr key={i} className="text-ink-700">
                    <td className="py-1.5">{item.sku_hint}</td>
                    <td className="py-1.5 font-mono">{item.resolved_sku ?? <span className="text-red-500">—</span>}</td>
                    <td className="py-1.5">{item.quantity ?? <span className="text-clay-600">?</span>}</td>
                    <td className="py-1.5">{(item.requested_discount * 100).toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {gs.missing_fields.length > 0 && (
              <p className="text-clay-600 text-xs mt-3">Campos faltantes: {gs.missing_fields.join(", ")}</p>
            )}
          </Section>
        )}

        {gs && (gs.customer_name || gs.product_found !== null) && (
          <Section title="Validación de dominio">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              <Field label="Cliente" value={gs.customer_name ?? "—"} />
              <Field label="Tier" value={gs.customer_tier ?? "—"} />
              <Field label="Producto" value={gs.product_found ? "✓ Encontrado" : "✗ No encontrado"} />
              <Field label="Stock" value={gs.stock_available ? "✓ Suficiente" : "✗ Insuficiente"} />
              {gs.delivery_location && <Field label="Entrega" value={gs.delivery_location} />}
              {gs.required_delivery_date && <Field label="Fecha requerida" value={gs.required_delivery_date} />}
            </div>
          </Section>
        )}

        {gs?.calculation && (
          <Section title="Cálculo de precio">
            <div className="grid grid-cols-2 gap-4">
              <Field label="SKU" value={gs.calculation.sku} mono />
              <Field label="Cantidad" value={String(gs.calculation.quantity)} />
              <Field label="Precio unitario" value={`USD ${gs.calculation.unit_price.toFixed(2)}`} />
              <Field label="Descuento aplicado" value={`${(gs.calculation.discount_pct * 100).toFixed(1)}%`} />
              <Field label="Subtotal" value={`USD ${gs.calculation.subtotal.toLocaleString("es-PE", { minimumFractionDigits: 2 })}`} />
              <Field label="Descuento (monto)" value={`USD ${gs.calculation.discount_amount.toLocaleString("es-PE", { minimumFractionDigits: 2 })}`} />
            </div>
            <div className="mt-4 pt-4 border-t border-line flex justify-between items-center">
              <span className="text-ink-500 text-sm">Total</span>
              <span className="font-serif text-ink-900 font-semibold text-2xl">
                USD {gs.calculation.total_usd.toLocaleString("es-PE", { minimumFractionDigits: 2 })}
              </span>
            </div>
          </Section>
        )}

        {gs?.clarification_request && (
          <Section title="Aclaración requerida" tone="amber">
            <p className="text-ink-700 text-sm">{gs.clarification_request}</p>
          </Section>
        )}

        {quote.status === "awaiting_approval" && gs && (
          <Section title="Aprobación requerida" tone="amber">
            <div className="flex flex-col gap-3">
              <div className="flex flex-col gap-1.5">
                {gs.approval_reasons.map((r, i) => (
                  <p key={i} className="text-ink-700 text-sm flex gap-2">
                    <span className="text-clay-500">⚠</span> {r}
                  </p>
                ))}
              </div>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Comentario (opcional)..."
                rows={2}
                className="w-full bg-white border border-line text-ink-900 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-clay-400/40"
              />
              {error && <p className="text-red-600 text-sm">{error}</p>}
              <div className="flex gap-3">
                <button
                  onClick={() => handleDecision("rejected")}
                  disabled={resuming}
                  className="flex-1 px-4 py-2.5 border border-red-300 text-red-600 hover:bg-red-50 rounded-lg text-sm font-medium disabled:opacity-50 transition-colors"
                >
                  {resuming ? "..." : "Rechazar"}
                </button>
                <button
                  onClick={() => handleDecision("approved")}
                  disabled={resuming}
                  className="flex-1 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-medium disabled:opacity-50 transition-colors"
                >
                  {resuming ? "Procesando..." : "Aprobar"}
                </button>
              </div>
            </div>
          </Section>
        )}

        {gs?.draft_quote && (
          <Section title="Borrador de cotización" tone="green">
            <pre className="text-ink-700 text-sm whitespace-pre-wrap font-sans leading-relaxed">{gs.draft_quote}</pre>
          </Section>
        )}

        {gs?.rejection_reason && (
          <Section title="Motivo de rechazo" tone="red">
            <p className="text-red-600 text-sm">{gs.rejection_reason}</p>
          </Section>
        )}

        {gs && gs.nodes_visited.length > 0 && (
          <Section title="Trazabilidad del agente">
            <div className="flex flex-col gap-4">
              <div>
                <p className="text-ink-400 text-xs mb-2">Nodos ejecutados</p>
                <div className="flex flex-wrap gap-2">
                  {gs.nodes_visited.map((node, i) => (
                    <span key={i} className="px-2.5 py-1 bg-cream-100 text-ink-700 rounded-md text-xs font-mono">
                      {i + 1}. {node}
                    </span>
                  ))}
                </div>
              </div>
              {gs.audit_log.length > 0 && (
                <div>
                  <p className="text-ink-400 text-xs mb-2">Registro de auditoría</p>
                  <div className="bg-cream-50 border border-line rounded-lg p-3 flex flex-col gap-1 max-h-40 overflow-y-auto scroll-soft">
                    {gs.audit_log.map((entry, i) => (
                      <p key={i} className="text-ink-500 text-xs font-mono">{entry}</p>
                    ))}
                  </div>
                </div>
              )}
              {gs.errors.length > 0 && (
                <div>
                  <p className="text-red-600 text-xs mb-1">Errores</p>
                  {gs.errors.map((e, i) => (
                    <p key={i} className="text-red-500 text-xs font-mono">{e}</p>
                  ))}
                </div>
              )}
            </div>
          </Section>
        )}
      </div>
    </div>
  );
}

const TONES = {
  default: "border-line bg-white",
  amber: "border-clay-400/40 bg-[#fdf6ec]",
  green: "border-emerald-200 bg-emerald-50/50",
  red: "border-red-200 bg-red-50/40",
} as const;

function Section({
  title,
  children,
  tone = "default",
}: {
  title: string;
  children: React.ReactNode;
  tone?: keyof typeof TONES;
}) {
  return (
    <div className={`rounded-xl border shadow-card p-5 flex flex-col gap-3 ${TONES[tone]}`}>
      <h2 className="text-ink-400 text-xs font-semibold uppercase tracking-wider">{title}</h2>
      {children}
    </div>
  );
}

function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <p className="text-ink-400 text-xs">{label}</p>
      <p className={`text-ink-900 text-sm mt-0.5 ${mono ? "font-mono" : ""}`}>{value}</p>
    </div>
  );
}
