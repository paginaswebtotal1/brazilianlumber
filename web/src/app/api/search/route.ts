import { NextResponse } from "next/server";
import { allDocs } from "@/lib/data";
import { searchInDb, usingSupabase } from "@/lib/supabase";

/**
 * Búsqueda del lado del servidor.
 *
 * El buscador de la interfaz resuelve en el navegador contra un índice ya
 * descargado, que es lo más rápido posible. Esta ruta existe para lo otro: que
 * el buscador funcione con JavaScript desactivado, para integraciones y para
 * demostrar el camino de PostgreSQL cuando Supabase está configurado.
 *
 *   GET /api/search?q=ipe+decking&kind=product&limit=24
 */

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function scoreLocal(q: string, limit: number, kind?: string) {
  const terms = q
    .toLowerCase()
    .replace(/[×]/g, "x")
    .split(/[^a-z0-9/]+/)
    .filter((t) => t.length > 1);
  if (!terms.length) return [];

  return allDocs()
    .filter((d) => !d.noindex && d.sub !== "junk" && (!kind || d.kind === kind))
    .map((d) => {
      const title = d.title.toLowerCase();
      const attrs = Object.values(d.attrs ?? {}).join(" ").toLowerCase();
      const body = (d.description ?? "").toLowerCase();
      let s = 0;
      for (const t of terms) {
        if (title === t) s += 30;
        else if (title.startsWith(t)) s += 14;
        else if (title.includes(t)) s += 9;
        if (attrs.includes(t)) s += 6;
        if (body.includes(t)) s += 2;
      }
      // Desempate por demanda real medida en Search Console.
      if (s > 0) s += Math.min((d.clicks ?? 0) / 100, 3);
      return { d, s };
    })
    .filter((x) => x.s > 0)
    .sort((a, b) => b.s - a.s)
    .slice(0, limit)
    .map(({ d, s }) => ({
      path: d.path,
      kind: d.kind,
      title: d.title,
      description: d.description ?? null,
      image: d.image ?? null,
      color: d.color ?? null,
      category_title: d.categoryTitle ?? null,
      rank: Math.round(s * 100) / 100,
    }));
}

export async function GET(req: Request) {
  const url = new URL(req.url);
  const q = (url.searchParams.get("q") ?? "").trim().slice(0, 120);
  const kind = url.searchParams.get("kind") ?? undefined;
  const limit = Math.min(Number(url.searchParams.get("limit") ?? 24) || 24, 60);

  if (q.length < 2) {
    return NextResponse.json({ q, source: "none", count: 0, results: [] });
  }

  const fromDb = usingSupabase ? await searchInDb(q, kind, limit) : null;
  const results = fromDb ?? scoreLocal(q, limit, kind);

  return NextResponse.json(
    { q, source: fromDb ? "supabase" : "local", count: results.length, results },
    { headers: { "Cache-Control": "public, max-age=60, stale-while-revalidate=300" } },
  );
}
