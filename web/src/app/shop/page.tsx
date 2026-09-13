import type { Metadata } from "next";
import { Breadcrumbs, CategoryCard, JsonLd, Section } from "@/components/ui";
import ShopBrowser, { type Item } from "@/components/ShopBrowser";
import { categories, getDoc, productsIn } from "@/lib/data";
import { BRAND, ROBOTS, breadcrumbSchema, canonical, collectionSchema, graph } from "@/lib/seo";

export const metadata: Metadata = {
  title: `Full Catalog | ${BRAND}`,
  description:
    "The complete Brazilian Lumber catalog: tropical hardwood and composite decking, cladding, fencing, flooring, slabs, landscaping and accessories. Filter by species, brand and size.",
  alternates: { canonical: canonical("/shop/") },
  robots: ROBOTS,
};

export const revalidate = 300;

export default function Shop() {
  const roots = categories().filter((c) => !c.parent);
  const all = productsIn("/", true);
  const products = categories()
    .filter((c) => !c.parent)
    .flatMap((r) => productsIn(r.path, true))
    .filter((p, i, a) => a.findIndex((x) => x.path === p.path) === i);

  const items: Item[] = products.map((p) => ({
    path: p.path,
    title: p.title,
    cat: p.category ?? "",
    catTitle: p.categoryTitle ?? "",
    root: (p.category ?? "").split("/").filter(Boolean)[0] ?? "",
    species: String(p.attrs?.especie ?? ""),
    brand: String(p.attrs?.marca ?? ""),
    size: String(p.attrs?.medida ?? ""),
    img: p.image ?? "",
    color: p.color ?? "#6b4f3a",
    desc: p.description ?? "",
  }));

  const crumbs = [
    { path: "/", title: "Home" },
    { path: "/shop/", title: "Products" },
  ];
  const doc = getDoc("/shop/");

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <Breadcrumbs items={crumbs} />

      <header className="max-w-3xl">
        <h1 className="font-[family-name:var(--font-display)] text-4xl font-semibold leading-tight text-bark-900">
          The full catalog
        </h1>
        <p className="mt-4 text-[15px] leading-relaxed text-bark-600">
          {items.length} products across {roots.length} top-level categories, consolidated from the Miami, Los Angeles
          and New Jersey portals. Filtering here never creates a new URL: the indexable addresses are the category
          pages below and the product pages themselves.
        </p>
      </header>

      <Section title="Categories">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {roots.map((c) => (
            <CategoryCard key={c.path} doc={c} />
          ))}
        </div>
      </Section>

      <div className="mt-4">
        <ShopBrowser items={items} roots={roots.map((r) => ({ key: r.route!.split("/")[0], title: r.title }))} />
      </div>

      <JsonLd
        data={graph(
          collectionSchema(
            doc ?? {
              kind: "page",
              path: "/shop/",
              slug: "shop",
              title: "Full Catalog",
              blocks: [],
              description: metadata.description as string,
            },
            all,
          ),
          breadcrumbSchema(crumbs),
        )}
      />
    </div>
  );
}
