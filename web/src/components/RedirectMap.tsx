"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { ArrowRight, Search } from "lucide-react";

type Row = { from: string; to: string; portal: string; type: string };

const PORTAL: Record<string, string> = {
  MIA: "brazilianlumber.com",
  LA: "brazilianlumberlosangeles.com",
  NJ: "brazilianlumbernewyork.com",
};

/**
 * Tabla consultable del mapa de equivalencias.
 *
 * No ejecuta nada: es la misma información de la hoja 08 del Excel, puesta
 * dentro del prototipo para poder responder en el momento a "¿y esta página
 * mía dónde queda?" sin abrir el Excel.
 */
export default function RedirectMap({ rows }: { rows: Row[] }) {
  const [q, setQ] = useState("");
  const [portal, setPortal] = useState("");
  const [type, setType] = useState("");

  const types = useMemo(() => [...new Set(rows.map((r) => r.type))].sort(), [rows]);

  const shown = useMemo(() => {
    const term = q.trim().toLowerCase();
    return rows
      .filter(
        (r) =>
          (!portal || r.portal === portal) &&
          (!type || r.type === type) &&
          (!term || r.from.toLowerCase().includes(term) || r.to.toLowerCase().includes(term)),
      )
      .slice(0, 400);
  }, [rows, q, portal, type]);

  const total = useMemo(
    () =>
      rows.filter(
        (r) =>
          (!portal || r.portal === portal) &&
          (!type || r.type === type) &&
          (!q.trim() ||
            r.from.toLowerCase().includes(q.trim().toLowerCase()) ||
            r.to.toLowerCase().includes(q.trim().toLowerCase())),
      ).length,
    [rows, q, portal, type],
  );

  return (
    <div>
      <div className="flex flex-wrap items-center gap-2">
        <label className="flex flex-1 items-center gap-2 rounded-full border border-bark-300 bg-white px-4 py-2 focus-within:border-ember-500">
          <Search size={16} className="shrink-0 text-bark-400" aria-hidden />
          <span className="sr-only">Filter the map</span>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Filter by old or new URL…"
            className="w-full bg-transparent text-sm outline-none placeholder:text-bark-400"
          />
        </label>
        <select
          value={portal}
          onChange={(e) => setPortal(e.target.value)}
          className="rounded-full border border-bark-300 bg-white px-3 py-2 text-sm text-bark-700"
          aria-label="Source portal"
        >
          <option value="">All portals</option>
          {Object.entries(PORTAL).map(([k, v]) => (
            <option key={k} value={k}>
              {v}
            </option>
          ))}
        </select>
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="rounded-full border border-bark-300 bg-white px-3 py-2 text-sm text-bark-700"
          aria-label="Content type"
        >
          <option value="">All types</option>
          {types.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </div>

      <p className="mt-3 text-sm text-bark-600" aria-live="polite">
        <strong className="font-semibold text-bark-900">{total}</strong> of {rows.length} mappings
        {shown.length < total && <span className="text-bark-400"> · showing the first {shown.length}</span>}
      </p>

      <div className="mt-4 overflow-x-auto rounded-[--radius-card] border border-bark-200 bg-white">
        <table className="w-full min-w-[640px] text-sm">
          <thead className="border-b border-bark-200 bg-bark-100 text-left">
            <tr>
              <th scope="col" className="px-4 py-2.5 font-medium text-bark-600">
                Old URL
              </th>
              <th scope="col" className="w-8" />
              <th scope="col" className="px-4 py-2.5 font-medium text-bark-600">
                Unified portal
              </th>
              <th scope="col" className="px-4 py-2.5 font-medium text-bark-600">
                Type
              </th>
            </tr>
          </thead>
          <tbody>
            {shown.map((r) => (
              <tr key={r.from} className="border-b border-bark-100 last:border-0 align-top">
                <td className="px-4 py-2.5">
                  <span className="block break-all text-[13px] text-bark-700">
                    {r.from.replace(/^https?:\/\//, "")}
                  </span>
                </td>
                <td className="px-1 py-2.5 text-bark-300">
                  <ArrowRight size={14} aria-hidden />
                </td>
                <td className="px-4 py-2.5">
                  <Link href={r.to} className="break-all text-[13px] text-ember-600 hover:underline">
                    {r.to}
                  </Link>
                </td>
                <td className="px-4 py-2.5 text-[12px] text-bark-500">{r.type}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {shown.length === 0 && (
        <p className="mt-4 text-sm text-bark-500">Nothing in the map matches that filter.</p>
      )}
    </div>
  );
}
