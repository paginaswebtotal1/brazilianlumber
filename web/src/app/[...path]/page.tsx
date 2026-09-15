import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { Blocks, Breadcrumbs, CategoryRow, JsonLd, ProductCard, Related, Section } from "@/components/ui";
import Thumb from "@/components/Thumb";
import {
  breadcrumbs,
  getCategory,
  getDoc,
  norm,
  pagesOfKind,
  productsIn,
  related,
} from "@/lib/data";
import { absolute, breadcrumbSchema, collectionSchema, descriptionFor, faqSchema, graph, metaFor } from "@/lib/seo";

/**
 * Ruta comodín: resuelve las categorías de producto (rutas jerárquicas de hasta
 * tres niveles, como /decking/tropical-hardwood/ipe/) y las páginas sueltas
 * (institucionales, de ciudad, de campaña).
 *
 * Solo sirve las 838 URLs del portal único. Las direcciones antiguas de los
 * tres portales no se redirigen aquí: el mapa de equivalencias se consulta en
 * /redirect-map/ y es la instrucción para el día de la migración real.
 */

type Params = { params: Promise<{ path: string[] }> };

export const revalidate = 300;

function resolve(path: string[]) {
  return norm("/" + path.join("/"));
}

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { path } = await params;
  const doc = getDoc(resolve(path));
  if (!doc) return {};
  return metaFor(doc);
}

export default async function CatchAll({ params }: Params) {
  const { path } = await params;
  const url = resolve(path);
  const doc = getDoc(url);

  // El prototipo no redirige: si la URL no es una de las 838 del portal único,
  // es un 404. El mapa de qué dirección antigua va a cuál nueva se consulta en
  // /redirect-map/ y en la hoja 08 del Excel de consolidación.
  if (!doc) notFound();

  const crumbs = breadcrumbs(doc);

  // ------------------------------------------------------ categoría
  if (doc.kind === "category") {
    const kids = (doc.children ?? []).map((c) => getCategory(c)).filter((c): c is NonNullable<typeof c> => !!c);
    const direct = productsIn(doc.path, true);
    const siblings = related(doc, 6);

    return (
      <div className="mx-auto max-w-7xl px-4 py-8">
        <Breadcrumbs items={crumbs} />

        <header className="grid gap-8 lg:grid-cols-[1fr_320px]">
          <div>
            <h1 className="font-[family-name:var(--font-display)] text-4xl font-semibold leading-tight text-bark-900">
              {doc.h1 ?? doc.title}
            </h1>
            <div className="mt-4">
              <Blocks blocks={doc.blocks} answer={doc.answerBlock} />
          <Related
            titulo="Related pages"
            items={[
              ...(doc.relatedCats ?? [])
                .map((p) => getDoc(p))
                .filter(Boolean)
                .map((c) => ({ path: c!.path, title: c!.title })),
              ...(doc.relatedGuides ?? []),
              ...(doc.relatedPages ?? []),
            ]}
          />
              <Related titulo="Guides on this material" items={doc.relatedGuides ?? []} />
              <Related titulo="By market" items={doc.relatedPages ?? []} />
            </div>
          </div>
          {doc.image && (
            <div className="hidden lg:block">
              <Thumb src={doc.image} alt={doc.title} color={doc.color} ratio="4 / 3" priority sizes="320px" />
            </div>
          )}
        </header>

        {kids.length > 0 && (
          <Section title="Subcategories">
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {kids.map((c) => (
                <CategoryRow key={c.path} doc={c} />
              ))}
            </div>
          </Section>
        )}

        {direct.length > 0 ? (
          <Section title={`${direct.length} product${direct.length === 1 ? "" : "s"}`}>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {direct.map((p, i) => (
                <ProductCard key={p.path} doc={p} priority={i < 4} />
              ))}
            </div>
          </Section>
        ) : (
          <div className="mt-10 rounded-[--radius-card] border border-dashed border-bark-300 bg-white p-6">
            <p className="text-sm font-medium text-bark-800">No products mapped to this category yet.</p>
            <p className="mt-1.5 max-w-2xl text-[13px] leading-relaxed text-bark-600">
              The category is part of the agreed menu, but none of the products crawled across the three portals falls
              under it. It needs either an assortment assigned to it or removal from the menu before launch. This is
              flagged in the QA report.
            </p>
            <Link href="/shop/" className="mt-3 inline-block text-sm font-medium text-ember-600 hover:underline">
              Browse the full catalog →
            </Link>
          </div>
        )}

        {siblings.length > 0 && (
          <Section title="Related categories">
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {siblings.map((c) => (
                <CategoryRow key={c.path} doc={c} />
              ))}
            </div>
          </Section>
        )}

        <JsonLd
          data={graph(
            collectionSchema(doc, direct),
            breadcrumbSchema(crumbs),
            ...(doc.faq?.length ? [faqSchema(doc.faq)] : []),
          )}
        />
      </div>
    );
  }

  // ------------------------------------------------------ página
  const isLocations = doc.slug === "areas-we-serve";
  const locations = isLocations ? pagesOfKind("location") : [];

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <Breadcrumbs items={crumbs} />

      <div className="mx-auto max-w-3xl">
        <h1 className="font-[family-name:var(--font-display)] text-4xl font-semibold leading-tight text-bark-900">
          {doc.h1 ?? doc.title}
        </h1>
        {doc.image && (
          <div className="mt-6">
            <Thumb src={doc.image} alt={doc.title} color={doc.color} ratio="16 / 9" priority sizes="100vw" />
          </div>
        )}
        <div className="mt-6">
          <Blocks blocks={doc.blocks} answer={doc.answerBlock} />
        </div>

        {doc.sub === "location" && (
          <div className="mt-8 rounded-[--radius-card] border border-bark-200 bg-white p-5">
            <h2 className="text-sm font-semibold text-bark-900">Delivering to {doc.title}</h2>
            <p className="mt-1.5 text-[13px] leading-relaxed text-bark-600">
              Orders for this area ship from the nearest of our three yards. Send a cut list and we come back with
              pricing and a delivery window.
            </p>
            <Link
              href="/request-a-quote/"
              className="mt-3 inline-block rounded-full bg-ember-500 px-4 py-2 text-sm font-medium text-white hover:bg-ember-600"
            >
              Request a quote
            </Link>
          </div>
        )}
      </div>

      {isLocations && (
        <Section title={`${locations.length} areas we serve`}>
          <ul className="flex flex-wrap gap-2">
            {locations.map((l) => (
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
      )}

      <JsonLd
        data={graph(
          {
            // Una pagina normal tambien es una entidad: /batu/ ES Philippine
            // mahogany para el mercado, y si el JSON-LD no lo dice, un motor
            // que recibe esa pregunta no sabe que esta pagina la contesta.
            "@type": "WebPage",
            name: doc.title,
            alternateName: doc.alsoKnownAs?.length ? doc.alsoKnownAs : undefined,
            description: descriptionFor(doc),
            url: absolute(doc.path),
            dateModified: doc.reviewed || doc.modified || undefined,
            abstract: doc.answerBlock || undefined,
            speakable: doc.answerBlock
              ? { "@type": "SpeakableSpecification", cssSelector: [".answer-block", "h1"] }
              : undefined,
          },
          breadcrumbSchema(crumbs),
          ...(doc.faq?.length ? [faqSchema(doc.faq)] : []),
        )}
      />
    </div>
  );
}
