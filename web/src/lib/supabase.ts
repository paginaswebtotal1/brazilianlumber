import { createClient, type SupabaseClient } from "@supabase/supabase-js";

/**
 * Cliente de Supabase.
 *
 * Es opcional por diseño. Si las variables no están puestas, `db()` devuelve
 * null y el portal sigue funcionando con el dataset local. Así el prototipo que
 * ve dirección no depende de que un plan gratuito esté despierto.
 */

const URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
const KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

let client: SupabaseClient | null = null;

export function db(): SupabaseClient | null {
  if (!URL || !KEY) return null;
  if (!client) {
    client = createClient(URL, KEY, {
      auth: { persistSession: false, autoRefreshToken: false },
      global: { headers: { "x-application-name": "bl-portal-unico" } },
    });
  }
  return client;
}

export const usingSupabase = Boolean(URL && KEY);

export type SearchRow = {
  path: string;
  kind: string;
  title: string;
  description: string | null;
  image: string | null;
  color: string | null;
  category_title: string | null;
  rank: number;
};

/** Búsqueda en PostgreSQL: tsvector con pesos + trigramas para las erratas. */
export async function searchInDb(q: string, kind?: string, limit = 24): Promise<SearchRow[] | null> {
  const sb = db();
  if (!sb) return null;
  const { data, error } = await sb.rpc("search_documents", { q, k: kind ?? null, lim: limit });
  if (error) {
    console.error("[supabase] search_documents:", error.message);
    return null;
  }
  return (data ?? []) as SearchRow[];
}
