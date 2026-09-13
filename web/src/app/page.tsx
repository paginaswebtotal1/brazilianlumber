import Link from "next/link";
import type { Metadata } from "next";
import SearchBox from "@/components/SearchBox";
import { CategoryCard, PostCard, ProductCard, Section } from "@/components/ui";
import { categories, nav, stats, topPosts, topProducts } from "@/lib/data";
import { BRAND, ROBOTS, canonical } from "@/lib/seo";

export const metadata: Metadata = {
  title: `${BRAND} — Tropical Hardwood, Composite Decking and Lumber`,
  description:
    "Ipe, Cumaru, Garapa, Jatoba and Tigerwood decking, composite and PVC decking, cladding, fencing and dimensional lumber. Three yards, one catalog, nationwide freight.",
  alternates: { canonical: canonical("/") },
  robots: ROBOTS,
};

export default function Home() {
  const tops = categories().filter((c) => !c.parent);
  const species = categories().filter((c) => c.route?.startsWith("decking/tropical-hardwood/"));

  return (
    <>
      {/* -------------------------------------------------- hero */}
      <section className="border-b border-bark-200 bg-bark-900">
        <div className="mx-auto grid max-w-7xl gap-8 px-4 py-14 lg:grid-cols-[1.1fr_0.9fr] lg:py-20">
          <div>
            <p className="mb-3 text-xs font-medium uppercase tracking-[0.2em] text-ember-400">
              Miami · Los Angeles · New Jersey
            </p>
            <h1 className="font-[family-name:var(--font-display)] text-4xl font-semibold leading-[1.1] text-white sm:text-5xl">
              Every board we stock, finally in one catalog.
            </h1>
            <p className="mt-5 max-w-xl text-[15px] leading-relaxed text-bark-300">
              Tropical hardwood decking, composite and PVC, cladding, fencing, flooring and dimensional lumber. Cut to
              order in our own mill and shipped anywhere in the United States.
            </p>
            <div className="mt-7 max-w-xl">
              <SearchBox placeholder="Search 838 pages: try “ipe 5/4x6”, “trex”, “deck tiles”…" />
              <p className="mt-2.5 flex flex-wrap gap-x-3 gap-y-1 text-xs text-bark-400">
                <span>Popular:</span>
                {["Ipe decking", "Cumaru 1x4", "Trex", "Deck tiles", "Hidden fasteners"].map((k) => (
                  <Link
                    key={k}
                    href={`/search/?q=${encodeURIComponent(k)}`}
                    className="underline decoration-bark-600 underline-offset-2 hover:text-ember-400"
                  >
                    {k}
                  </Link>
                ))}
              </p>
            </div>
          </div>

          <dl className="grid grid-cols-2 gap-3 self-center sm:grid-cols-2">
            {[
              ["838", "unique pages"],
              [stats.products.toString(), "products"],
              [stats.posts.toString(), "guides"],
              [stats.redirects.toLocaleString("en-US"), "URL mappings documented"],
            ].map(([n, l]) => (
              <div key={l} className="rounded-[--radius-card] border border-bark-700 bg-bark-800/60 px-4 py-5">
                <dt className="font-[family-name:var(--font-display)] text-3xl font-semibold text-white">{n}</dt>
                <dd className="mt-1 text-xs uppercase tracking-wide text-bark-400">{l}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      <div className="mx-auto max-w-7xl px-4">
        {/* -------------------------------------------------- categorías raíz */}
        <Section title="Shop by category" href="/shop/">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {tops.map((c) => (
              <CategoryCard key={c.path} doc={c} />
            ))}
          </div>
        </Section>

        {/* -------------------------------------------------- especies */}
        <Section title="Tropical hardwood by species" href="/decking/tropical-hardwood/">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {species.map((c) => (
              <CategoryCard key={c.path} doc={c} />
            ))}
          </div>
        </Section>

        {/* -------------------------------------------------- productos */}
        <Section title="Most requested products" href="/shop/">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {topProducts(8).map((p, i) => (
              <ProductCard key={p.path} doc={p} priority={i < 4} />
            ))}
          </div>
        </Section>

        {/* -------------------------------------------------- guías */}
        <Section title="Guides from the yard" href="/guides/">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {topPosts(6).map((p) => (
              <PostCard key={p.path} doc={p} />
            ))}
          </div>
        </Section>

        {/* -------------------------------------------------- ubicaciones */}
        <Section title="Where we deliver" href={nav.locations.path}>
          <ul className="flex flex-wrap gap-2">
            {nav.locations.items.slice(0, 28).map((l) => (
              <li key={l.path}>
                <Link
                  href={l.path}
                  className="inline-block rounded-full border border-bark-200 bg-white px-3.5 py-1.5 text-[13px] text-bark-700 transition-colors hover:border-ember-500 hover:text-ember-600"
                >
                  {l.title}
                </Link>
              </li>
            ))}
          </ul>
        </Section>
      </div>
    </>
  );
}
