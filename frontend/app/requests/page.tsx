"use client";
import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api, QuoteListItem } from "@/lib/api";
import { StatusBadge } from "@/components/quote/StatusBadge";
import { RequestForm } from "@/components/quote/RequestForm";

export default function RequestsPage() {
  // useSearchParams requiere un límite de Suspense para el build de Next.
  return (
    <Suspense fallback={<div className="px-10 py-8 text-ink-400 text-sm">Cargando...</div>}>
      <RequestsInner />
    </Suspense>
  );
}

function RequestsInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [quotes, setQuotes] = useState<QuoteListItem[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchQuotes = async () => {
    try {
      const data = await api.listQuotes();
      setQuotes(data);
    } catch (e) {
      console.error("Error fetching quotes:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuotes();
  }, []);

  // Abrir el modal si se llega con ?new=1 (desde el sidebar)
  useEffect(() => {
    if (searchParams.get("new") === "1") setShowForm(true);
  }, [searchParams]);

  return (
    <div className="px-10 py-8">
      {/* Header */}
      <header className="flex items-start justify-between border-b border-line pb-6 mb-8">
        <div>
          <p className="text-ink-400 text-xs tracking-[0.18em] uppercase">Bandeja</p>
          <h1 className="font-serif text-4xl font-semibold text-ink-900 mt-1">Solicitudes</h1>
          <p className="text-ink-500 text-sm mt-2">
            {quotes.length} solicitud{quotes.length !== 1 ? "es" : ""} registrada{quotes.length !== 1 ? "s" : ""}
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-clay-500 hover:bg-clay-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium shadow-card transition-colors"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 5v14M5 12h14" />
          </svg>
          Nueva
        </button>
      </header>

      {loading ? (
        <p className="text-ink-400 text-sm">Cargando...</p>
      ) : quotes.length === 0 ? (
        <div className="bg-white rounded-xl border border-dashed border-line p-14 text-center">
          <p className="text-ink-500">No hay solicitudes aún.</p>
          <button
            onClick={() => setShowForm(true)}
            className="mt-3 text-clay-600 hover:text-clay-700 text-sm font-medium"
          >
            Crear la primera solicitud →
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-line shadow-card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-line">
                <th className="text-left px-6 py-3.5 text-ink-400 font-medium text-xs uppercase tracking-wider">ID</th>
                <th className="text-left px-6 py-3.5 text-ink-400 font-medium text-xs uppercase tracking-wider">Cliente</th>
                <th className="text-left px-6 py-3.5 text-ink-400 font-medium text-xs uppercase tracking-wider">Estado</th>
                <th className="text-right px-6 py-3.5 text-ink-400 font-medium text-xs uppercase tracking-wider">Fecha</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {quotes.map((q) => (
                <tr
                  key={q.id}
                  onClick={() => router.push(`/requests/${q.id}`)}
                  className="hover:bg-cream-50 cursor-pointer transition-colors"
                >
                  <td className="px-6 py-4 font-mono text-ink-400 text-xs">{q.id.slice(0, 8)}</td>
                  <td className="px-6 py-4 text-ink-900 font-medium">{q.customer_id}</td>
                  <td className="px-6 py-4">
                    <StatusBadge status={q.status} />
                  </td>
                  <td className="px-6 py-4 text-ink-400 text-xs text-right">
                    {new Date(q.created_at).toLocaleString("es-PE", {
                      day: "2-digit", month: "short", year: "numeric",
                      hour: "2-digit", minute: "2-digit",
                    })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && <RequestForm onClose={() => { setShowForm(false); fetchQuotes(); }} />}
    </div>
  );
}
