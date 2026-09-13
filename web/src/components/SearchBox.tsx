"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import MiniSearch, { type SearchResult } from "minisearch";
import { Search, Loader2, CornerDownLeft } from "lucide-react";

/**
 * Buscador del portal.
 *
 * Decisión de arquitectura: el índice completo (827 documentos, ~620 KB sin
 * comprimir, ~120 KB con brotli) se descarga UNA vez, la primera vez que el
 * usuario toca el buscador, y a partir de ahí cada pulsación se resuelve en
 * memoria. No hay ida y vuelta al servidor, así que el resultado aparece en
 * menos de 10 ms incluso con la red en 3G.
 *
 * El índice NO se descarga en la carga inicial de la página: eso arruinaría el
 * LCP. Se precarga al pasar el ratón por encima o al enfocar, que da 200-300 ms
 * de ventaja antes de que se escriba la primera letra.
 */

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

let CACHE: MiniSearch<Row> | null = null;
let LOADING: Promise<MiniSearch<Row>> | null = null;

async function getIndex(): Promise<MiniSearch<Row>> {
  if (CACHE) return CACHE;
  if (LOADING) return LOADING;
  LOADING = (async () => {
    const res = await fetch("/search-index.json");
    const rows: Row[] = await res.json();
    const ms = new MiniSearch<Row>({
      fields: ["t", "w", "d", "b"],
      storeFields: ["t", "k", "d", "img", "col", "ct", "p"],
      idField: "id",
      searchOptions: {
        // El título y las palabras clave (especie, marca, medida) pesan mucho
        // más que el cuerpo: quien busca "ipe 1x4" quiere la ficha, no un
        // artículo que mencione ipe de pasada.
        boost: { t: 6, w: 4, d: 2, b: 1 },
        prefix: true,
        fuzzy: 0.2,
        combineWith: "AND",
      },
      // "5/4x6", "5/4 x 6" y "54x6" tienen que caer en el mismo término.
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
    CACHE = ms;
    return ms;
  })();
  return LOADING;
}

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

export default function SearchBox({
  autoFocus = false,
  placeholder = "Search 838 pages: try “ipe 5/4x6”, “trex”, “deck tiles”…",
  className = "",
}: {
  autoFocus?: boolean;
  placeholder?: string;
  className?: string;
}) {
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<(SearchResult & Partial<Row>)[]>([]);
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [active, setActive] = useState(0);
  const box = useRef<HTMLDivElement>(null);
  const input = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const warm = useCallback(() => {
    void getIndex();
  }, []);

  // Atajo global: "/" para saltar al buscador desde cualquier página.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const el = document.activeElement;
      const typing = el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement;
      if (e.key === "/" && !typing) {
        e.preventDefault();
        input.current?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (box.current && !box.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  useEffect(() => {
    let live = true;
    const term = q.trim();
    if (term.length < 2) {
      setHits([]);
      setBusy(false);
      return;
    }
    setBusy(true);
    const id = setTimeout(async () => {
      const ms = await getIndex();
      if (!live) return;
      let r = ms.search(term) as (SearchResult & Partial<Row>)[];
      if (r.length === 0) {
        // Segunda pasada más permisiva antes de rendirse: erratas y plurales.
        r = ms.search(term, { fuzzy: 0.35, prefix: true, combineWith: "OR" }) as typeof r;
      }
      // La demanda real medida en Search Console desempata: entre dos páginas
      // igual de relevantes gana la que la gente abre de verdad.
      r.sort((a, b) => b.score + (b.p ?? 0) / 40 - (a.score + (a.p ?? 0) / 40));
      if (!live) return;
      setHits(r.slice(0, 8));
      setActive(0);
      setBusy(false);
      setOpen(true);
    }, 90);
    return () => {
      live = false;
      clearTimeout(id);
    };
  }, [q]);

  function go(path?: string) {
    setOpen(false);
    router.push(path ?? `/search/?q=${encodeURIComponent(q)}`);
  }

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActive((i) => Math.min(i + 1, hits.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      go(hits[active]?.id);
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  }

  return (
    <div ref={box} className={`relative ${className}`}>
      <div className="flex items-center gap-2 rounded-full border border-bark-300 bg-white px-4 py-2.5 shadow-sm transition-colors focus-within:border-ember-500">
        <Search size={18} className="shrink-0 text-bark-500" aria-hidden />
        <input
          ref={input}
          type="search"
          role="combobox"
          aria-expanded={open}
          aria-controls="search-suggestions"
          aria-label="Search the catalog and guides"
          autoFocus={autoFocus}
          value={q}
          placeholder={placeholder}
          onChange={(e) => setQ(e.target.value)}
          onFocus={() => {
            warm();
            if (hits.length) setOpen(true);
          }}
          onMouseEnter={warm}
          onKeyDown={onKeyDown}
          className="w-full bg-transparent text-[15px] text-bark-900 outline-none placeholder:text-bark-400"
        />
        {busy ? (
          <Loader2 size={16} className="shrink-0 animate-spin text-bark-400" aria-hidden />
        ) : (
          <kbd className="hidden shrink-0 rounded border border-bark-200 px-1.5 py-0.5 text-[11px] text-bark-400 sm:block">
            /
          </kbd>
        )}
      </div>

      {open && q.trim().length >= 2 && (
        <div
          id="search-suggestions"
          role="listbox"
          className="absolute left-0 right-0 top-[calc(100%+8px)] z-50 overflow-hidden rounded-xl border border-bark-200 bg-white shadow-xl"
        >
          {hits.length === 0 && !busy && (
            <p className="px-4 py-6 text-sm text-bark-500">
              Nothing matched <strong className="text-bark-800">{q}</strong>. Try a species, a size or a brand.
            </p>
          )}
          {hits.map((h, i) => (
            <Link
              key={h.id}
              href={h.id}
              role="option"
              aria-selected={i === active}
              onMouseEnter={() => setActive(i)}
              onClick={() => setOpen(false)}
              className={`flex items-center gap-3 border-b border-bark-100 px-3 py-2.5 last:border-0 ${
                i === active ? "bg-bark-100" : "bg-white"
              }`}
            >
              <span
                className="woodfill grid h-9 w-9 shrink-0 place-items-center rounded-md text-[11px] font-semibold text-white/90"
                style={{ background: h.col ?? "#6b4f3a" }}
                aria-hidden
              >
                {(h.t ?? "").slice(0, 2).toUpperCase()}
              </span>
              <span className="min-w-0 flex-1">
                <span className="block truncate text-sm font-medium text-bark-900">{h.t}</span>
                <span className="block truncate text-xs text-bark-500">
                  {LABEL[h.k ?? ""] ?? "Page"}
                  {h.ct ? ` · ${h.ct}` : ""}
                </span>
              </span>
              {i === active && <CornerDownLeft size={14} className="shrink-0 text-bark-400" aria-hidden />}
            </Link>
          ))}
          <button
            type="button"
            onClick={() => go()}
            className="w-full bg-bark-100 px-4 py-2.5 text-left text-xs font-medium text-bark-700 hover:bg-bark-200"
          >
            See all results for “{q}”
          </button>
        </div>
      )}
    </div>
  );
}
