import type { Metadata } from "next";
import Link from "next/link";
import { Breadcrumbs, JsonLd, PostCard } from "@/components/ui";
import { allPosts, postcats } from "@/lib/data";
import { BRAND, ROBOTS, breadcrumbSchema, canonical, graph } from "@/lib/seo";

/**
 * Índice del blog unificado.
 *
 * Los tres portales tenían cada uno su propio blog, con artículos repetidos
 * entre ellos. Aquí quedan 229 artículos únicos bajo /guides/, con sus 69 temas.
 */

export const metadata: Metadata = {
  title: `Guides and Technical Articles | ${BRAND}`,
  description:
    "Decking, cladding and lumber guides written from the yard: species comparisons, installation detail, finishing and maintenance.",
  alternates: { canonical: canonical("/guides/") },
  robots: ROBOTS,
};

export const revalidate = 300;

export default function GuidesIndex() {
  const posts = allPosts();
  const cats = postcats();
  const crumbs = [
    { path: "/", title: "Home" },
    { path: "/guides/", title: "Guides" },
  ];

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <Breadcrumbs items={crumbs} />

      <header className="max-w-3xl">
        <h1 className="font-[family-name:var(--font-display)] text-4xl font-semibold leading-tight text-bark-900">
          Guides
        </h1>
        <p className="mt-4 text-[15px] leading-relaxed text-bark-600">
          {posts.length} articles on decking, cladding, lumber and finishing, written by the Brazilian Lumber team from
          what we see in the yard and on jobsites. Everything the three separate blogs used to publish, deduplicated
          into one library.
        </p>
      </header>

      <nav aria-label="Guide topics" className="mt-7">
        <ul className="flex flex-wrap gap-2">
          {cats.slice(0, 30).map((c) => (
            <li key={c.path}>
              <Link
                href={c.path}
                className="inline-block rounded-full border border-bark-200 bg-white px-3.5 py-1.5 text-[13px] text-bark-700 transition-colors hover:border-ember-500 hover:text-ember-600"
              >
                {c.title}
                <span className="ml-1.5 text-[11px] text-bark-400">{c.postCount}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      <div className="mt-9 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {posts.map((p, i) => (
          <PostCard key={p.path} doc={p} priority={i < 3} />
        ))}
      </div>

      <JsonLd
        data={graph(breadcrumbSchema(crumbs), {
          "@type": "CollectionPage",
          name: "Guides",
          url: canonical("/guides/"),
          mainEntity: {
            "@type": "ItemList",
            numberOfItems: posts.length,
            itemListElement: posts.slice(0, 30).map((p, i) => ({
              "@type": "ListItem",
              position: i + 1,
              name: p.title,
              url: canonical(p.path),
            })),
          },
        })}
      />
    </div>
  );
}
