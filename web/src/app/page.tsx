import Link from "next/link";
import Image from "next/image";
import type { Metadata } from "next";
import { ArrowUpRight, Ruler, Truck, Trees } from "lucide-react";
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
  const featured = topProducts(8);

  // Foto de portada elegida a mano entre las 193 imágenes apaisadas que trajo el
  // pipeline. Una foto de ambiente al atardecer sostiene texto blanco encima;
  // una ficha de producto sobre fondo blanco, no. El resto del sitio sí usa la
  // foto real de cada contenido.
  const HERO = "/img/548bb56de39f7b87.webp";

  return (
    <>
      {/* ================================================================ hero */}
      <section className="relative isolate overflow-hidden bg-bark-950">
        <Image src={HERO} alt="" fill priority sizes="100vw" className="scale-105 object-cover" />
        <div
          className="absolute inset-0 bg-gradient-to-r from-bark-950/92 via-bark-950/62 to-bark-950/20"
          aria-hidden
        />

        <div className="relative mx-auto max-w-7xl px-4 py-20 lg:py-28">
          <div className="max-w-2xl">
            <p className="rise mb-5 text-[11px] font-medium uppercase tracking-[0.22em] text-ember-300">
              Miami · Los Angeles · New Jersey
            </p>
            <h1 className="rise display text-[2.75rem] text-white sm:text-[3.75rem] lg:text-[4.25rem]">
              Every board we stock,
              <br />
              finally in one catalog.
            </h1>
            <p
              className="rise mt-6 max-w-xl text-[17px] leading-relaxed text-bark-200"
              style={{ animationDelay: "80ms" }}
            >
              Tropical hardwood decking, composite and PVC, cladding, fencing, flooring and dimensional lumber. Milled
              to order in our own shop and shipped anywhere in the United States.
            </p>

            <div className="rise mt-9 max-w-xl" style={{ animationDelay: "160ms" }}>
              <SearchBox placeholder="Search 838 pages — try “ipe 5/4x6”, “trex”, “deck tiles”…" />
              <p className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1.5 text-[12.5px] text-bark-400">
                <span>Popular</span>
                {["Ipe decking", "Cumaru 1x4", "Trex", "Deck tiles", "Hidden fasteners"].map((k) => (
                  <Link
                    key={k}
                    href={`/search/?q=${encodeURIComponent(k)}`}
                    className="rounded-full border border-white/15 px-2.5 py-1 transition-colors hover:border-ember-400 hover:text-ember-300"
                  >
                    {k}
                  </Link>
                ))}
              </p>
            </div>
          </div>
        </div>

        {/* franja de argumentos, pegada al hero */}
        <div className="relative border-t border-white/10">
          <dl className="mx-auto grid max-w-7xl gap-px bg-white/10 px-4 sm:grid-cols-3">
            {[
              [Trees, "23 species in stock", "From Ipe at 3,680 lbf Janka to Western Red Cedar, graded and kiln dried."],
              [Ruler, "Milled to order", "Cut lists handled in house, so you pay freight on the wood you use."],
              [Truck, "Three yards, one catalog", "Miami, Los Angeles and New Jersey, with nationwide freight."],
            ].map(([Icon, t, d], i) => {
              const I = Icon as typeof Trees;
              return (
                <div key={t as string} className="bg-bark-950 px-2 py-7 sm:px-6">
                  <I size={19} className="mb-3 text-ember-400" aria-hidden />
                  <dt className="text-[14.5px] font-semibold text-white">{t as string}</dt>
                  <dd className="mt-1 text-[13px] leading-relaxed text-bark-400">{d as string}</dd>
                </div>
              );
            })}
          </dl>
        </div>
      </section>

      <div className="mx-auto max-w-7xl px-4">
        {/* ========================================================= categorías */}
        <Section title="Shop by category" kicker="Catalog" href="/shop/" linkLabel="Full catalog">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {tops.map((c, i) => (
              <CategoryCard key={c.path} doc={c} i={i} />
            ))}
          </div>
        </Section>

        {/* ========================================================== especies */}
        <Section
          title="Tropical hardwood by species"
          kicker="The real thing"
          href="/decking/tropical-hardwood/"
        >
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {species.map((c, i) => (
              <CategoryCard key={c.path} doc={c} i={i} tall />
            ))}
          </div>
        </Section>

        {/* ========================================================= productos */}
        <Section title="Most requested products" kicker="Moving now" href="/shop/">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {featured.map((p, i) => (
              <ProductCard key={p.path} doc={p} priority={i < 4} i={i} />
            ))}
          </div>
        </Section>
      </div>

      {/* ============================================================== guías */}
      <div className="mt-8 border-y border-bark-200 bg-bark-100/60">
        <div className="mx-auto max-w-7xl px-4">
          <Section title="Guides from the yard" kicker="Know-how" href="/guides/">
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {topPosts(6).map((p, i) => (
                <PostCard key={p.path} doc={p} i={i} />
              ))}
            </div>
          </Section>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4">
        {/* ======================================================= ubicaciones */}
        <Section title="Where we deliver" kicker="Coverage" href={nav.locations.path} linkLabel="All areas">
          <ul className="flex flex-wrap gap-2">
            {nav.locations.items.slice(0, 30).map((l) => (
              <li key={l.path}>
                <Link
                  href={l.path}
                  className="inline-block rounded-full border border-bark-200 bg-white px-4 py-2 text-[13.5px] text-bark-700 transition-all hover:border-ember-400 hover:text-ember-600"
                >
                  {l.title}
                </Link>
              </li>
            ))}
          </ul>
        </Section>

        {/* ============================================================= cierre */}
        <section className="mb-16 overflow-hidden rounded-[--radius-lg] bg-bark-900 px-6 py-12 sm:px-12">
          <div className="max-w-2xl">
            <h2 className="display text-[2rem] text-white sm:text-[2.4rem]">Send us the cut list.</h2>
            <p className="mt-4 text-[15.5px] leading-relaxed text-bark-300">
              Dimensions, quantities and the delivery address. The sales desk comes back with pricing, lead time and
              freight, usually the same day.
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Link
                href="/request-a-quote/"
                className="group flex items-center gap-1.5 rounded-full bg-ember-500 px-6 py-3 text-sm font-semibold text-bark-950 transition-colors hover:bg-ember-400"
              >
                Request a quote
                <ArrowUpRight size={16} className="transition-transform group-hover:translate-x-0.5" aria-hidden />
              </Link>
              <Link
                href="/request-samples/"
                className="rounded-full border border-white/25 px-6 py-3 text-sm font-semibold text-white transition-colors hover:border-white/60"
              >
                Request samples
              </Link>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}
