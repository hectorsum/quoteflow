"use client";
import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { api, QuoteListItem } from "@/lib/api";
import { StatusBadge } from "@/components/quote/StatusBadge";
import { RequestForm } from "@/components/quote/RequestForm";

export default function RequestsPage() {
  const router = useRouter();
  const [quotes, setQuotes] = useState<QuoteListItem[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

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
    // Polling deshabilitado por ahora — el usuario puede recargar manualmente
    // intervalRef.current = setInterval(fetchQuotes, 3000);
    // return () => {
    //   if (intervalRef.current) clearInterval(intervalRef.current);
    // };
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-xl font-semibold text-white">Solicitudes de cotización</h1>
          <p className="text-gray-400 text-sm mt-0.5">
            {quotes.length} solicitud{quotes.length !== 1 ? "es" : ""} registrada{quotes.length !== 1 ? "s" : ""}
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm font-medium"
        >
          + Nueva solicitud
        </button>
      </div>

      {loading ? (
        <p className="text-gray-500 text-sm">Cargando...</p>
      ) : quotes.length === 0 ? (
        <div className="border border-dashed border-gray-700 rounded-lg p-12 text-center">
          <p className="text-gray-500">No hay solicitudes aún.</p>
          <button
            onClick={() => setShowForm(true)}
            className="mt-3 text-blue-400 hover:text-blue-300 text-sm"
          >
            Crear la primera solicitud →
          </button>
        </div>
      ) : (
        <div className="border border-gray-800 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-900 border-b border-gray-800">
              <tr>
                <th className="text-left px-4 py-3 text-gray-400 font-medium">ID</th>
                <th className="text-left px-4 py-3 text-gray-400 font-medium">Cliente</th>
                <th className="text-left px-4 py-3 text-gray-400 font-medium">Estado</th>
                <th className="text-left px-4 py-3 text-gray-400 font-medium">Fecha</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {quotes.map(q => (
                <tr
                  key={q.id}
                  onClick={() => router.push(`/requests/${q.id}`)}
                  className="hover:bg-gray-900 cursor-pointer transition-colors"
                >
                  <td className="px-4 py-3 font-mono text-gray-300 text-xs">
                    {q.id.slice(0, 8)}...
                  </td>
                  <td className="px-4 py-3 text-gray-200">{q.customer_id}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={q.status} />
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-xs">
                    {new Date(q.created_at).toLocaleString("es-PE")}
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
