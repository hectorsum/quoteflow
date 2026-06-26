"use client";
import { useEffect, useState, useRef } from "react";
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
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchQuote = async () => {
    try {
      const data = await api.getQuote(id);
      setQuote(data);
      setError(null);
    } catch (e: any) {
      console.error("Error fetching quote:", e);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuote();
    // Polling deshabilitado por ahora — el usuario puede recargar manualmente
    // intervalRef.current = setInterval(fetchQuote, 4000);
    // return () => {
    //   if (intervalRef.current) clearInterval(intervalRef.current);
    // };
  }, [id]);

  async function handleDecision(action: "approved" | "rejected") {
    setResuming(true);
    setError(null);
    try {
      await api.resumeQuote(id, { action, comment, decided_by: "executive" });
      await fetchQuote();
    } catch (e: any) {
      setError(e.message);
    }
    setResuming(false);
  }

  if (loading) return <p className="text-gray-500 text-sm">Cargando...</p>;
  if (!quote) return <p className="text-red-400 text-sm">{error || "Solicitud no encontrada"}</p>;

  const gs = quote.graph_state;

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <button onClick={() => router.push("/requests")} className="text-gray-500 hover:text-gray-300 text-xs">
            ← Volver a solicitudes
          </button>
          <h1 className="text-white font-semibold text-lg font-mono">{id.slice(0, 8)}...</h1>
          <div className="flex items-center gap-3">
            <StatusBadge status={quote.status as QuoteStatus} />
            <span className="text-gray-400 text-xs">{quote.customer_id}</span>
            <span className="text-gray-600 text-xs">{new Date(quote.created_at).toLocaleString("es-PE")}</span>
          </div>
        </div>
      </div>

      <Section title="Solicitud original">
        <p className="text-gray-200 text-sm leading-relaxed">{quote.raw_request}</p>
      </Section>

      {gs && gs.extracted_items.length > 0 && (
        <Section title="Extracción de intención">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-gray-500">
                <th className="text-left pb-2">Texto del cliente</th>
                <th className="text-left pb-2">SKU resuelto</th>
                <th className="text-left pb-2">Cantidad</th>
                <th className="text-left pb-2">Descuento solicitado</th>
              </tr>
            </thead>
            <tbody>
              {gs.extracted_items.map((item, i) => (
                <tr key={i} className="text-gray-300">
                  <td className="py-1">{item.sku_hint}</td>
                  <td className="py-1 font-mono">{item.resolved_sku ?? <span className="text-red-400">—</span>}</td>
                  <td className="py-1">{item.quantity ?? <span className="text-yellow-400">?</span>}</td>
                  <td className="py-1">{(item.requested_discount * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
          {gs.missing_fields.length > 0 && (
            <p className="text-yellow-400 text-xs mt-2">
              Campos faltantes: {gs.missing_fields.join(", ")}
            </p>
          )}
        </Section>
      )}

      {gs && (gs.customer_name || gs.product_found !== null) && (
        <Section title="Validación de dominio">
          <div className="grid grid-cols-3 gap-4 text-xs">
            <Field label="Cliente" value={gs.customer_name ?? "—"} />
            <Field label="Tier" value={gs.customer_tier ?? "—"} />
            <Field label="Producto encontrado" value={gs.product_found === true ? "✅ Sí" : gs.product_found === false ? "❌ No" : "—"} />
            <Field label="Stock disponible" value={gs.stock_available === true ? "✅ Suficiente" : gs.stock_available === false ? "❌ Insuficiente" : "—"} />
            {gs.delivery_location && <Field label="Entrega" value={gs.delivery_location} />}
            {gs.required_delivery_date && <Field label="Fecha requerida" value={gs.required_delivery_date} />}
          </div>
        </Section>
      )}

      {gs?.calculation && (
        <Section title="Cálculo de precio">
          <div className="grid grid-cols-2 gap-4 text-xs">
            <Field label="SKU" value={gs.calculation.sku} mono />
            <Field label="Cantidad" value={String(gs.calculation.quantity)} />
            <Field label="Precio unitario" value={`USD ${gs.calculation.unit_price.toFixed(2)}`} />
            <Field label="Descuento aplicado" value={`${(gs.calculation.discount_pct * 100).toFixed(1)}%`} />
            <Field label="Subtotal" value={`USD ${gs.calculation.subtotal.toLocaleString("es-PE", { minimumFractionDigits: 2 })}`} />
            <Field label="Descuento (monto)" value={`USD ${gs.calculation.discount_amount.toLocaleString("es-PE", { minimumFractionDigits: 2 })}`} />
          </div>
          <div className="mt-3 pt-3 border-t border-gray-700 flex justify-between items-center">
            <span className="text-gray-400 text-sm">Total</span>
            <span className="text-white font-mono font-bold text-lg">
              USD {gs.calculation.total_usd.toLocaleString("es-PE", { minimumFractionDigits: 2 })}
            </span>
          </div>
        </Section>
      )}

      {gs?.clarification_request && (
        <Section title="Aclaración requerida">
          <p className="text-yellow-300 text-sm">{gs.clarification_request}</p>
        </Section>
      )}

      {quote.status === "awaiting_approval" && gs && (
        <Section title="Aprobación requerida" highlight>
          <div className="space-y-3">
            <div className="space-y-1">
              {gs.approval_reasons.map((r, i) => (
                <p key={i} className="text-yellow-300 text-sm flex gap-2">
                  <span>⚠️</span> {r}
                </p>
              ))}
            </div>
            <textarea
              value={comment}
              onChange={e => setComment(e.target.value)}
              placeholder="Comentario (opcional)..."
              rows={2}
              className="w-full bg-gray-800 border border-gray-600 text-white rounded px-3 py-2 text-sm resize-none"
            />
            {error && <p className="text-red-400 text-sm">{error}</p>}
            <div className="flex gap-3">
              <button
                onClick={() => handleDecision("rejected")}
                disabled={resuming}
                className="flex-1 px-4 py-2 border border-red-700 text-red-400 hover:bg-red-950 rounded text-sm disabled:opacity-50"
              >
                {resuming ? "..." : "Rechazar"}
              </button>
              <button
                onClick={() => handleDecision("approved")}
                disabled={resuming}
                className="flex-1 px-4 py-2 bg-green-700 hover:bg-green-600 text-white rounded text-sm font-medium disabled:opacity-50"
              >
                {resuming ? "Procesando..." : "Aprobar"}
              </button>
            </div>
          </div>
        </Section>
      )}

      {gs?.draft_quote && (
        <Section title="Borrador de cotización" highlight>
          <pre className="text-gray-200 text-sm whitespace-pre-wrap font-sans leading-relaxed">
            {gs.draft_quote}
          </pre>
        </Section>
      )}

      {gs?.rejection_reason && (
        <Section title="Motivo de rechazo">
          <p className="text-red-400 text-sm">{gs.rejection_reason}</p>
        </Section>
      )}

      {gs && gs.nodes_visited.length > 0 && (
        <Section title="Trazabilidad del agente">
          <div className="space-y-4">
            <div>
              <p className="text-gray-500 text-xs mb-2">Nodos ejecutados</p>
              <div className="flex flex-wrap gap-2">
                {gs.nodes_visited.map((node, i) => (
                  <span key={i} className="px-2 py-1 bg-gray-800 text-gray-300 rounded text-xs font-mono">
                    {i + 1}. {node}
                  </span>
                ))}
              </div>
            </div>
            {gs.audit_log.length > 0 && (
              <div>
                <p className="text-gray-500 text-xs mb-2">Registro de auditoría</p>
                <div className="bg-gray-900 rounded p-3 space-y-1 max-h-40 overflow-y-auto">
                  {gs.audit_log.map((entry, i) => (
                    <p key={i} className="text-gray-400 text-xs font-mono">{entry}</p>
                  ))}
                </div>
              </div>
            )}
            {gs.errors.length > 0 && (
              <div>
                <p className="text-red-400 text-xs mb-1">Errores</p>
                {gs.errors.map((e, i) => (
                  <p key={i} className="text-red-300 text-xs font-mono">{e}</p>
                ))}
              </div>
            )}
          </div>
        </Section>
      )}
    </div>
  );
}

function Section({ title, children, highlight }: {
  title: string;
  children: React.ReactNode;
  highlight?: boolean;
}) {
  return (
    <div className={`rounded-lg border p-4 space-y-3 ${highlight ? "border-yellow-700 bg-yellow-950/20" : "border-gray-800 bg-gray-900/50"}`}>
      <h2 className="text-gray-300 text-xs font-semibold uppercase tracking-wider">{title}</h2>
      {children}
    </div>
  );
}

function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <p className="text-gray-500 text-xs">{label}</p>
      <p className={`text-gray-200 text-sm ${mono ? "font-mono" : ""}`}>{value}</p>
    </div>
  );
}
