"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { SlidersHorizontal, X } from "lucide-react";
import Thumb from "./Thumb";

/**
 * Catálogo filtrable.
 *
 * Los filtros viven en el estado del cliente y NO en la URL a propósito: el
 * problema que este portal viene a resolver es que los tres sitios generaban
 * 1.379 URLs con parámetros de filtro, todas indexables y todas duplicadas
 * entre sí. Aquí filtrar no crea ninguna URL nueva; las direcciones indexables
 * son exactamente las de la taxonomía.
 */

export type Item = {
  path: string;
  title: string;
  cat: string;
  catTitle: string;
  root: string;
  species: string;
  brand: string;
  size: string;
  img: string;
  color: string;
  desc: string;
};

export default function ShopBrowser({ items, roots }: { items: Item[]; roots: { key: string; title: string }[] }) {
  const [root, setRoot] = useState("");
  const [species, setSpecies] = useState("");
  const [brand, setBrand] = useState("");
  const [size, setSize] = useState("");
  const [open, setOpen] = useState(false);

  const opts = useMemo(() => {
    const pool = root ? items.filter((i) => i.root === root) : items;
    const uniq = (f: (i: Item) => string) =>
      [...new Set(pool.map(f).filter(Boolean))].sort((a, b) =>
        a.localeCompare(b, "en", { numeric: true }),
      );
    return { species: uniq((i) => i.species), brand: uniq((i) => i.brand), size: uniq((i) => i.size) };
  }, [items, root]);

  const shown = useMemo(
    () =>
      items.filter(
        (i) =>
          (!root || i.root === root) &&
          (!species || i.species === species) &&
          (!brand || i.brand === brand) &&
          (!size || i.size === size),
      ),
    [items, root, species, brand, size],
  );

  const active = [root, species, brand, size].filter(Boolean).length;
  const clear = () => {
    setRoot("");
    setSpecies("");
    setBrand("");
    setSize("");
  };

  const cap = (s: string) => s.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <div>
      <div className="sticky top-[68px] z-20 -mx-4 mb-6 border-y border-bark-200 bg-bark-50/95 px-4 py-3 backdrop-blur">
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => setOpen(!open)}
            aria-expanded={open}
            className="flex items-center gap-1.5 rounded-full border border-bark-300 bg-white px-3.5 py-1.5 text-[13px] font-medium text-bark-700 sm:hidden"
          >
            <SlidersHorizontal size={14} aria-hidden /> Filters{active > 0 && ` (${active})`}
          </button>

          <div className={`${open ? "flex" : "hidden"} w-full flex-wrap gap-2 sm:flex sm:w-auto`}>
            <Select label="Category" value={root} onChange={setRoot} options={roots.map((r) => [r.key, r.title])} />
            <Select
              label="Species"
              value={species}
              onChange={setSpecies}
              options={opts.species.map((s) => [s, cap(s)])}
            />
            <Select label="Brand" value={brand} onChange={setBrand} options={opts.brand.map((s) => [s, cap(s)])} />
            <Select
              label="Size"
              value={size}
              onChange={setSize}
              options={opts.size.map((s) => [s, s.replace("x", " x ")])}
            />
          </div>

          <p className="ml-auto text-[13px] text-bark-500" aria-live="polite">
            {shown.length} of {items.length}
          </p>
          {active > 0 && (
            <button
              type="button"
              onClick={clear}
              className="flex items-center gap-1 rounded-full bg-bark-200 px-3 py-1.5 text-[13px] text-bark-700 hover:bg-bark-300"
            >
              <X size={13} aria-hidden /> Clear
            </button>
          )}
        </div>
      </div>

      {shown.length === 0 ? (
        <p className="rounded-[--radius-card] border border-dashed border-bark-300 bg-white p-8 text-center text-sm text-bark-500">
          No products match that combination.{" "}
          <button type="button" onClick={clear} className="text-ember-600 underline">
            Clear the filters
          </button>
          .
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {shown.map((p, i) => (
            <Link
              key={p.path}
              href={p.path}
              className="group block overflow-hidden rounded-[--radius-card] border border-bark-200 bg-white transition-shadow hover:shadow-md"
            >
              <Thumb src={p.img || null} alt={p.title} color={p.color} priority={i < 4} label={p.title} />
              <div className="p-3.5">
                <p className="mb-1 truncate text-[11px] uppercase tracking-wide text-bark-400">{p.catTitle}</p>
                <h3 className="text-[15px] font-medium leading-snug text-bark-900 group-hover:text-ember-600">
                  {p.title}
                </h3>
                {p.desc && <p className="mt-1.5 line-clamp-2 text-[13px] text-bark-500">{p.desc}</p>}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

function Select({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: [string, string][];
}) {
  if (options.length === 0) return null;
  return (
    <label className="inline-flex items-center gap-1.5 rounded-full border border-bark-300 bg-white pl-3 pr-1 text-[13px]">
      <span className="text-bark-400">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="cursor-pointer appearance-none bg-transparent py-1.5 pr-2 text-bark-800 outline-none"
      >
        <option value="">All</option>
        {options.map(([v, l]) => (
          <option key={v} value={v}>
            {l}
          </option>
        ))}
      </select>
    </label>
  );
}
