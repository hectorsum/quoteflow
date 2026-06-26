"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";

const CUSTOMERS = [
  { id: "CLI-001", name: "Constructora Altamira S.A. (Gold)" },
  { id: "CLI-002", name: "Minera Pacífico Ltda. (Silver)" },
  { id: "CLI-003", name: "Taller Mecánico Rojas (Standard)" },
];

const EXAMPLES = [
  "Necesito 5 bombas BOM-M16-A4 con 5% de descuento para entrega en Arequipa",
  "Quiero unas válvulas para mi planta",
  "Solicito 8 compresores COM-TORN-50L con 15% de descuento para Lima, entrega urgente",
];

interface Props {
  onClose: () => void;
}

export function RequestForm({ onClose }: Props) {
  const router = useRouter();
  const [customerId, setCustomerId] = useState("CLI-001");
  const [rawRequest, setRawRequest] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    if (!rawRequest.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.createQuote(customerId, rawRequest);
      onClose();
      router.push(`/requests/${res.quote_id}`);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-ink-900/30 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-card w-full max-w-lg p-7 flex flex-col gap-5">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-ink-400 text-xs tracking-[0.18em] uppercase">Nueva</p>
            <h2 className="font-serif text-2xl font-semibold text-ink-900 mt-1">Solicitud de cotización</h2>
          </div>
          <button onClick={onClose} className="text-ink-400 hover:text-ink-700 text-2xl leading-none">×</button>
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-ink-700 text-sm font-medium">Cliente</label>
          <select
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
            className="w-full bg-cream-50 border border-line text-ink-900 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-clay-400/40"
          >
            {CUSTOMERS.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-ink-700 text-sm font-medium">Solicitud en texto libre</label>
          <textarea
            value={rawRequest}
            onChange={(e) => setRawRequest(e.target.value)}
            rows={4}
            placeholder="Escribe la solicitud del cliente tal como llegó..."
            className="w-full bg-cream-50 border border-line text-ink-900 rounded-lg px-3 py-2.5 text-sm resize-none placeholder-ink-400 focus:outline-none focus:ring-2 focus:ring-clay-400/40"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <p className="text-ink-400 text-xs">Ejemplos rápidos:</p>
          <div className="flex flex-col gap-1">
            {EXAMPLES.map((ex, i) => (
              <button
                key={i}
                onClick={() => setRawRequest(ex)}
                className="block w-full text-left text-xs text-ink-500 hover:text-clay-600 truncate transition-colors"
              >
                → {ex}
              </button>
            ))}
          </div>
        </div>

        {error && <p className="text-red-600 text-sm bg-red-50 border border-red-100 rounded-lg px-3 py-2">{error}</p>}

        <div className="flex gap-3 pt-1">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2.5 border border-line text-ink-700 rounded-lg text-sm hover:bg-cream-100 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading || !rawRequest.trim()}
            className="flex-1 px-4 py-2.5 bg-clay-500 hover:bg-clay-600 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors"
          >
            {loading ? "Enviando..." : "Enviar solicitud"}
          </button>
        </div>
      </div>
    </div>
  );
}
