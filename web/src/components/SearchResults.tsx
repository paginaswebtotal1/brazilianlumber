"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import MiniSearch, { type SearchResult } from "minisearch";
import Thumb from "./Thumb";

type Row = {
  id: string;
  t: string;
  k: string;
  d: string;
  b: string;
  w: string;
  c: string;
  ct: string;
  img: string;
  col: string;
  p: number;
};

type Hit = SearchResult & Partial<Row>;

const GROUPS: [string, string][] = [
  ["", "Everything"],
  ["product", "Products"],
  ["category", "Categories"],
  ["post", "Guides"],
  ["page:location", "Locations"],
  ["page:company", "Company"],
];

const LABEL: Record<string, string> = {
  product: "Product",
  category: "Category",
  post: "Guide",
  postcat: "Guide topic",
  "page:location": "Location",
  "page:company": "Company",
  "page:landing": "Page",
  "page:utility": "Page",
};

let CACHE: { ms: MiniSearch<Row>; rows: Map<string, Row> } | null = null;

async function load() {
  if (CACHE) return CACHE;
  const rows: Row[] = await (await fetch("/search-index.json")).json();
  const ms = new MiniSearch<Row>({
    fields: ["t", "w", "d", "b"],
    storeFields: ["t", "k", "d", "img", "col", "ct", "p"],
    idField: "id",
    searchOptions: { boost: { t: 6, w: 4, d: 2, b: 1 }, prefix: true, fuzzy: 0.2, combineWith: "AND" },
    tokenize: (text) =>
      text
        .toLowerCase()
        .replace(/[×]/g, "x")
        .split(/[^a-z0-9/.]+/)
        .flatMap((tk) => (tk.includes("x") ? [tk, ...tk.split("x")] : [tk]))
        .filter(Boolean),
    processTerm: (term) => (term.length < 2 ? null : term.replace(/[/.]/g, "")),
  });
  ms.addAll(rows);
  CACHE = { ms, rows: new Map(rows.map((r) => [r.id, r])) };
  return CACHE;
}

export default function SearchResults() {
  const sp = useSearchParams();
  const router = useRouter();
  const q = sp.get("q") ?? "";
  const [input, setInput] = useState(q);
  const [hits, setHits] = useState<Hit[] | null>(null);
  const [kind, setKind] = useState("");

  useEffect(() => setInput(q), [q]);

  useEffect(() => {
    let live = true;
    if (q.trim().length < 2) {
      setHits([]);
      return;
    }
    (async () => {
      const { ms } = await load();
      if (!live) return;
      let r = ms.search(q) as Hit[];
      if (r.length === 0) r = ms.search(q, { fuzzy: 0.35, prefix: true, combineWith: "OR" }) as Hit[];
      r.sort((a, b) => b.score + (b.p ?? 0) / 40 - (a.score + (a.p ?? 0) / 40));
      setHits(r);
    })();
    return () => {
      live = false;
    };
  }, [q]);

  const counts = useMemo(() => {
    const c: Record<string, number> = {};
    (hits ?? []).forEach((h) => {
      c[h.k ?? ""] = (c[h.k ?? ""] ?? 0) + 1;
    });
    return c;
  }, [hits]);

  const shown = useMemo(() => (kind ? (hits ?? []).filter((h) => h.k === kind) : (hits ?? [])), [hits, kind]);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    router.push(`/search/?q=${encodeURIComponent(input)}`);
  }

  return (
    <div>
      <form onSubmit={submit} className="max-w-2xl">
        <label htmlFor="q" className="sr-only">
          Search
        </label>
        <div className="flex items-center gap-2 rounded-full border border-bark-300 bg-white px-4 py-2.5 focus-within:border-ember-500">
          <input
            id="q"
            type="search"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Search products, categories and guides…"
            className="w-full bg-transparent text-[15px] outline-none placeholder:text-bark-400"
          />
          <button type="submit" className="rounded-full bg-bark-900 px-4 py-1.5 text-sm font-medium text-white">
            Search
          </button>
        </div>
      </form>

      {q.trim().length >= 2 && (
        <>
          <p className="mt-6 text-sm text-bark-600" aria-live="polite">
            {hits === null ? (
              "Searching…"
            ) : (
              <>
                <strong className="font-semibold text-bark-900">{hits.length}</strong> result
                {hits.length === 1 ? "" : "s"} for <strong className="font-semibold text-bark-900">{q}</strong>
              </>
            )}
          </p>

          {hits !== null && hits.length > 0 && (
            <nav aria-label="Filter results" className="mt-4 flex flex-wrap gap-2">
              {GROUPS.filter(([k]) => !k || counts[k]).map(([k, label]) => (
                <button
                  key={k}
                  type="button"
                  onClick={() => setKind(k)}
                  aria-pressed={kind === k}
                  className={`rounded-full px-3.5 py-1.5 text-[13px] font-medium transition-colors ${
                    kind === k
                      ? "bg-bark-900 text-white"
                      : "border border-bark-200 bg-white text-bark-700 hover:border-bark-400"
                  }`}
                >
                  {label}
                  <span className={`ml-1.5 text-[11px] ${kind === k ? "text-bark-300" : "text-bark-400"}`}>
                    {k ? counts[k] : hits.length}
                  </span>
                </button>
              ))}
            </nav>
          )}

          <ul className="mt-6 divide-y divide-bark-200 border-y border-bark-200">
            {shown.map((h) => (
              <li key={h.id}>
                <Link href={h.id} className="group flex items-start gap-4 py-4">
                  <span className="w-20 shrink-0 sm:w-24">
                    <Thumb src={h.img || null} alt="" color={h.col} ratio="4 / 3" label={h.t} />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="mb-0.5 block text-[11px] uppercase tracking-wide text-bark-400">
                      {LABEL[h.k ?? ""] ?? "Page"}
                      {h.ct ? ` · ${h.ct}` : ""}
                    </span>
                    <span className="block text-[15px] font-medium text-bark-900 group-hover:text-ember-600">
                      {h.t}
                    </span>
                    {h.d && <span className="mt-1 line-clamp-2 block text-[13px] text-bark-500">{h.d}</span>}
                    <span className="mt-1 block truncate text-[11px] text-bark-400">{h.id}</span>
                  </span>
                </Link>
              </li>
            ))}
          </ul>

          {hits !== null && hits.length === 0 && (
            <div className="mt-6 rounded-[--radius-card] border border-dashed border-bark-300 bg-white p-8">
              <p className="text-sm font-medium text-bark-800">Nothing matched that.</p>
              <p className="mt-1.5 text-[13px] text-bark-600">
                Try a species (ipe, cumaru, garapa), a brand (trex, timbertech, azek), a size (5/4x6, 1x4) or a
                product type (deck tiles, cladding, fasteners).
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
