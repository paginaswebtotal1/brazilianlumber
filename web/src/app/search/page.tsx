import type { Metadata } from "next";
import { Suspense } from "react";
import { Breadcrumbs } from "@/components/ui";
import SearchResults from "@/components/SearchResults";
import { BRAND, canonical } from "@/lib/seo";

/**
 * Resultados de busqueda.
 *
 * Siempre noindex, pase lo que pase con el interruptor global: una pagina de
 * resultados internos es contenido generado por el usuario y Google la trata
 * como thin content. Es una de las causas de las 1.379 URLs con parametro que
 * se detectaron en los tres portales de origen.
 */
export const metadata: Metadata = {
  title: `Search | ${BRAND}`,
  description: "Search the full Brazilian Lumber catalog and guide library.",
  alternates: { canonical: canonical("/search/") },
  robots: { index: false, follow: true },
};

export default function SearchPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <Breadcrumbs items={[{ path: "/", title: "Home" }, { path: "/search/", title: "Search" }]} />
      <h1 className="mb-6 font-[family-name:var(--font-display)] text-4xl font-semibold text-bark-900">Search</h1>
      <Suspense fallback={<p className="text-sm text-bark-500">Loading search…</p>}>
        <SearchResults />
      </Suspense>
    </div>
  );
}
