"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";

const CUSTOMERS = [
  { id: "CLI-001", name: "Minera Horizonte SAC (Gold)" },
  { id: "CLI-002", name: "Constructora Andina EIRL (Silver)" },
  { id: "CLI-003", name: "Agroindustrias Sur SRL (Standard)" },
];

const EXAMPLES = [
  "Necesito 20 cascos HX-200 con 5% de descuento para entrega en Arequipa",
  "Quiero cascos para mi equipo",
  "Solicito 500 cascos HX-200 con 8% de descuento para Lima, entrega urgente",
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
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-lg w-full max-w-lg p-6 space-y-5">
        <div className="flex justify-between items-center">
          <h2 className="text-white font-semibold text-lg">Nueva solicitud de cotización</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-xl leading-none">×</button>
        </div>

        <div className="space-y-1">
          <label className="text-gray-400 text-sm">Cliente</label>
          <select
            value={customerId}
            onChange={e => setCustomerId(e.target.value)}
            className="w-full bg-gray-800 border border-gray-600 text-white rounded px-3 py-2 text-sm"
          >
            {CUSTOMERS.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>

        <div className="space-y-1">
          <label className="text-gray-400 text-sm">Solicitud en texto libre</label>
          <textarea
            value={rawRequest}
            onChange={e => setRawRequest(e.target.value)}
            rows={4}
            placeholder="Escribe la solicitud del cliente tal como llegó..."
            className="w-full bg-gray-800 border border-gray-600 text-white rounded px-3 py-2 text-sm resize-none placeholder-gray-600"
          />
        </div>

        <div className="space-y-1">
          <p className="text-gray-500 text-xs">Ejemplos rápidos:</p>
          <div className="space-y-1">
            {EXAMPLES.map((ex, i) => (
              <button
                key={i}
                onClick={() => setRawRequest(ex)}
                className="block w-full text-left text-xs text-gray-400 hover:text-blue-400 truncate"
              >
                → {ex}
              </button>
            ))}
          </div>
        </div>

        {error && <p className="text-red-400 text-sm">{error}</p>}

        <div className="flex gap-3 pt-1">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-600 text-gray-300 rounded text-sm hover:bg-gray-800"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading || !rawRequest.trim()}
            className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded text-sm font-medium"
          >
            {loading ? "Enviando..." : "Enviar solicitud"}
          </button>
        </div>
      </div>
    </div>
  );
}
