import type { Metadata } from "next";
import { Breadcrumbs } from "@/components/ui";
import RedirectMap from "@/components/RedirectMap";
import { absorbed, redirects, stats } from "@/lib/data";
import { BRAND, canonical } from "@/lib/seo";

/**
 * Mapa de equivalencias, dentro del prototipo.
 *
 * Es documentación, no comportamiento: el prototipo no redirige nada. Sirve
 * para contestar en la reunión "¿y esta página mía dónde queda?" sin salir del
 * navegador. La fuente es la misma hoja 08 del Excel de consolidación.
 */
export const metadata: Metadata = {
  title: `URL Map | ${BRAND}`,
  description: "Where every URL from the three portals lands in the unified portal.",
  alternates: { canonical: canonical("/redirect-map/") },
  robots: { index: false, follow: false },
};

export default function RedirectMapPage() {
  const byPortal = redirects.reduce<Record<string, number>>((acc, r) => {
    acc[r.portal] = (acc[r.portal] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <Breadcrumbs
        items={[
          { path: "/", title: "Home" },
          { path: "/redirect-map/", title: "URL map" },
        ]}
      />

      <header className="max-w-3xl">
        <p className="text-xs font-medium uppercase tracking-wider text-ember-600">Internal reference</p>
        <h1 className="mt-1.5 font-[family-name:var(--font-display)] text-4xl font-semibold leading-tight text-bark-900">
          Where every old URL lands
        </h1>
        <p className="mt-4 text-[15px] leading-relaxed text-bark-600">
          This prototype does not redirect anything: it only shows the unified portal. This table is the migration
          instruction, the same one in sheet 08 of the consolidation workbook. On launch day these{" "}
          {stats.redirects.toLocaleString("en-US")} mappings become 301 redirects, configured on each of the three
          domains.
        </p>
      </header>

      <dl className="mt-7 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[
          [stats.crawled.toLocaleString("en-US"), "URLs crawled"],
          ["838", "unique pages kept"],
          [stats.redirects.toLocaleString("en-US"), "301 mappings"],
          [stats.noindexed.toLocaleString("en-US"), "tag URLs to noindex"],
        ].map(([n, l]) => (
          <div key={l} className="rounded-[--radius-card] border border-bark-200 bg-white px-4 py-4">
            <dt className="font-[family-name:var(--font-display)] text-2xl font-semibold text-bark-900">{n}</dt>
            <dd className="mt-0.5 text-xs uppercase tracking-wide text-bark-500">{l}</dd>
          </div>
        ))}
      </dl>

      <p className="mt-4 text-[13px] text-bark-500">
        By source portal: brazilianlumber.com {byPortal.MIA ?? 0} · brazilianlumberlosangeles.com {byPortal.LA ?? 0} ·
        brazilianlumbernewyork.com {byPortal.NJ ?? 0}. Plus {absorbed.length} legacy pages absorbed into a taxonomy
        node that occupied the same address.
      </p>

      <div className="mt-8">
        <RedirectMap rows={redirects} />
      </div>
    </div>
  );
}
