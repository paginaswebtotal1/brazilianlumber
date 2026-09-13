#!/usr/bin/env node
/**
 * Carga el dataset del portal en Supabase.
 *
 *   1. En Supabase Studio > SQL Editor, ejecutar web/supabase-schema.sql
 *   2. Poner en .env.local:
 *        NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
 *        SUPABASE_SERVICE_ROLE_KEY=eyJ...   (Settings > API > service_role)
 *   3. npm run seed
 *
 * La service_role salta las políticas RLS, así que esta clave NUNCA va al
 * navegador ni al repositorio. Solo se usa aquí, en local.
 */
import { createClient } from "@supabase/supabase-js";
import { readFileSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");

// Carga .env.local sin dependencias externas.
for (const f of [".env.local", ".env"]) {
  const p = resolve(root, f);
  if (!existsSync(p)) continue;
  for (const line of readFileSync(p, "utf8").split(/\r?\n/)) {
    const m = /^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/.exec(line);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2].replace(/^["']|["']$/g, "");
  }
}

const URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
const KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!URL || !KEY) {
  console.error("Faltan NEXT_PUBLIC_SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en .env.local");
  process.exit(1);
}

const sitePath = resolve(root, "src/data/site.json");
const site = JSON.parse(readFileSync(sitePath, "utf8"));

// Las filas se derivan del mismo dataset que consume la web, para que no haya
// dos copias del contenido que puedan desincronizarse.
const plain = (doc, limit) => {
  const out = [];
  for (const b of doc.blocks ?? []) {
    out.push(b.t === "list" ? b.items.join(" ") : (b.text ?? ""));
    if (out.join(" ").length > limit) break;
  }
  return out.join(" ").replace(/\s+/g, " ").slice(0, limit).trim();
};

const keywords = (d) => {
  const a = d.attrs ?? {};
  const k = [];
  if (a.especie) k.push(String(a.especie).replace(/-/g, " "));
  if (a.marca) k.push(a.marca);
  if (a.medida) k.push(a.medida, a.medida.replace("x", " x "), a.medida.replace("x", ""));
  if (a.grado) k.push(a.grado);
  if (d.categoryTitle) k.push(d.categoryTitle);
  k.push(...(d.catNames ?? []));
  return [...new Set(k)].join(" ");
};

const rows = ["categories", "products", "posts", "postcats", "pages"].flatMap((c) =>
  site[c].map((d) => ({
    path: d.path, kind: d.kind, sub: d.sub ?? null, slug: d.slug,
    title: d.title, h1: d.h1 ?? d.title, description: d.description ?? null,
    category: d.category ?? null, category_title: d.categoryTitle ?? null,
    parent: d.parent ?? null, children: d.children ?? [], blocks: d.blocks ?? [],
    specs: d.specs ?? [], faq: d.faq ?? [], attrs: d.attrs ?? {},
    gallery: d.gallery ?? [], cats: d.cats ?? [], cat_names: d.catNames ?? [],
    image: d.image ?? null, color: d.color ?? null,
    keywords: keywords(d), body: plain(d, 6000),
    product_count: d.productCount ?? 0, post_count: d.postCount ?? 0,
    clicks: d.clicks ?? 0, impressions: d.impressions ?? 0,
    noindex: Boolean(d.noindex) || d.sub === "junk",
    origins: d.origins ?? [], modified: d.modified ?? null,
    published_at: d.date ?? d.modified ?? null,
  })),
);
const sb = createClient(URL, KEY, { auth: { persistSession: false } });

const chunk = (arr, n) => Array.from({ length: Math.ceil(arr.length / n) }, (_, i) => arr.slice(i * n, i * n + n));

async function upsert(table, data, key, size) {
  let done = 0;
  for (const part of chunk(data, size)) {
    const { error } = await sb.from(table).upsert(part, { onConflict: key });
    if (error) {
      console.error(`\n  ${table}: ${error.message}`);
      process.exit(1);
    }
    done += part.length;
    process.stdout.write(`\r  ${table}: ${done}/${data.length}`);
  }
  process.stdout.write("\n");
}

console.log(`Cargando en ${URL}`);
await upsert("documents", rows, "path", 100);

const redirects = site.redirects.map((r) => ({
  from_url: r.from,
  to_path: r.to,
  portal: r.portal,
  kind: r.type,
}));
await upsert("redirects", redirects, "from_url", 200);

const { count } = await sb.from("documents").select("*", { count: "exact", head: true });
console.log(`\nListo. ${count} documentos y ${redirects.length} redirecciones en Supabase.`);

const { data: test, error: testErr } = await sb.rpc("search_documents", { q: "ipe decking", k: null, lim: 3 });
if (testErr) {
  console.error("La funcion search_documents fallo: " + testErr.message);
  console.error("Revisa que se ejecuto web/supabase-schema.sql completo.");
  process.exit(1);
}
console.log(`Prueba de busqueda "ipe decking": ${test.length} resultados. Primero: ${test[0]?.title ?? "-"}`);
