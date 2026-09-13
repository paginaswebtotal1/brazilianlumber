import Link from "next/link";
import type { Nav } from "@/lib/data";

export default function Footer({ nav, stats }: { nav: Nav; stats: Record<string, number> }) {
  const year = new Date().getFullYear();
  return (
    <footer className="mt-16 border-t border-bark-200 bg-bark-900 text-bark-300">
      <div className="mx-auto max-w-7xl px-4 py-12">
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <p className="font-[family-name:var(--font-display)] text-lg font-semibold text-white">Brazilian Lumber</p>
            <p className="mt-2 max-w-xs text-sm leading-relaxed text-bark-400">
              Tropical hardwood, composite decking, cladding and dimensional lumber. One catalog, three yards, freight
              anywhere in the United States.
            </p>
            <p className="mt-4 text-xs text-bark-500">Miami, FL · Los Angeles, CA · Newark, NJ</p>
          </div>

          <nav aria-label="Products">
            <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-bark-400">Products</h2>
            <ul className="space-y-1.5">
              {nav.shop.map((n) => (
                <li key={n.path}>
                  <Link href={n.path} className="text-sm text-bark-300 hover:text-white">
                    {n.title}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          <nav aria-label="Company">
            <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-bark-400">Company</h2>
            <ul className="space-y-1.5">
              {nav.company.map((n) => (
                <li key={n.path}>
                  <Link href={n.path} className="text-sm text-bark-300 hover:text-white">
                    {n.title}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          <nav aria-label="Top locations">
            <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-bark-400">Areas we serve</h2>
            <ul className="space-y-1.5">
              {nav.locations.items.slice(0, 10).map((n) => (
                <li key={n.path}>
                  <Link href={n.path} className="text-sm text-bark-300 hover:text-white">
                    {n.title}
                  </Link>
                </li>
              ))}
              <li>
                <Link href={nav.locations.path} className="text-sm font-medium text-ember-400 hover:text-ember-500">
                  All locations →
                </Link>
              </li>
            </ul>
          </nav>
        </div>

        {/* Aviso permanente: nadie debe confundir el prototipo con el sitio real. */}
        <div className="mt-10 rounded-lg border border-ember-600/40 bg-ember-600/10 px-4 py-3 text-xs leading-relaxed text-ember-400">
          <strong className="font-semibold">Internal prototype.</strong> Unified architecture proposal for
          brazilianlumber.com, brazilianlumberlosangeles.com and brazilianlumbernewyork.com. It consolidates{" "}
          {stats.crawled?.toLocaleString("en-US")} crawled URLs into {(838).toLocaleString("en-US")} unique pages. The{" "}
          {stats.redirects?.toLocaleString("en-US")} URL mappings are documented, not executed here — see{" "}
          <Link href="/redirect-map/" className="underline">
            the URL map
          </Link>
          . Blocked from every search engine and not a live storefront.
        </div>

        <div className="mt-6 flex flex-col gap-2 border-t border-bark-800 pt-6 text-xs text-bark-500 sm:flex-row sm:items-center sm:justify-between">
          <p>© {year} Brazilian Lumber. Prototype build.</p>
          <p className="flex gap-4">
            <Link href="/privacy-policy/" className="hover:text-bark-300">
              Privacy
            </Link>
            <Link href="/terms-conditions/" className="hover:text-bark-300">
              Terms
            </Link>
            <Link href="/sitemap/" className="hover:text-bark-300">
              Sitemap
            </Link>
          </p>
        </div>
      </div>
    </footer>
  );
}
