import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { Blocks, Breadcrumbs, JsonLd, ProductCard, Section, SpecTable } from "@/components/ui";
import Thumb from "@/components/Thumb";
import { breadcrumbs, getDoc, related } from "@/lib/data";
import { breadcrumbSchema, faqSchema, graph, metaFor, productSchema } from "@/lib/seo";

/**
 * Ficha de producto.
 *
 * La decisión de arquitectura del estudio se aplica aquí: todo producto vive en
 * /product/{slug}/ y en ninguna otra URL. Pertenecer a varias categorías no
 * genera una segunda dirección, que era el origen de las 488 páginas duplicadas
 * detectadas en los tres portales.
 */

type Params = { params: Promise<{ slug: string }> };

export const revalidate = 300;

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { slug } = await params;
  const doc = getDoc(`/product/${slug}/`);
  if (!doc) return {};
  return metaFor(doc);
}

export default async function ProductPage({ params }: Params) {
  const { slug } = await params;
  const doc = getDoc(`/product/${slug}/`);
  if (!doc || doc.kind !== "product") notFound();

  const crumbs = breadcrumbs(doc);
  const sisters = related(doc, 8);
  const gallery = doc.gallery ?? [];

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <Breadcrumbs items={crumbs} />

      <div className="grid gap-10 lg:grid-cols-[minmax(0,420px)_minmax(0,1fr)]">
        {/* ---------------------------------------------- media */}
        <div>
          <Thumb
            src={doc.image}
            alt={doc.imageAlt ?? doc.title}
            color={doc.color}
            ratio="1 / 1"
            priority
            sizes="(max-width: 1024px) 100vw, 420px"
            label={doc.title}
          />
          {gallery.length > 1 && (
            <ul className="mt-3 grid grid-cols-4 gap-2">
              {gallery.slice(1, 5).map((g) => (
                <li key={g} className="media rounded-md" style={{ aspectRatio: "1 / 1" }}>
                  <Image src={g} alt={`${doc.title} detail`} fill sizes="100px" loading="lazy" />
                </li>
              ))}
            </ul>
          )}

          <div className="mt-5 rounded-[--radius-card] border border-bark-200 bg-white p-4">
            <p className="text-sm font-semibold text-bark-900">Need a quote or a cut list?</p>
            <p className="mt-1 text-[13px] leading-relaxed text-bark-600">
              We mill to order. Send dimensions and quantities and the sales desk comes back with pricing and freight.
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              <Link
                href="/request-a-quote/"
                className="rounded-full bg-ember-500 px-4 py-2 text-sm font-medium text-white hover:bg-ember-600"
              >
                Request a quote
              </Link>
              <Link
                href="/request-samples/"
                className="rounded-full border border-bark-300 px-4 py-2 text-sm font-medium text-bark-700 hover:border-bark-400"
              >
                Request samples
              </Link>
            </div>
          </div>
        </div>

        {/* ---------------------------------------------- contenido */}
        <div className="min-w-0">
          {doc.categoryTitle && doc.category && (
            <Link href={doc.category} className="text-xs font-medium uppercase tracking-wider text-ember-600">
              {doc.categoryTitle}
            </Link>
          )}
          <h1 className="mt-1.5 font-[family-name:var(--font-display)] text-3xl font-semibold leading-tight text-bark-900 sm:text-4xl">
            {doc.h1 ?? doc.title}
          </h1>

          {/* Atributos detectados por el pipeline a partir del slug y del contenido. */}
          <ul className="mt-4 flex flex-wrap gap-2">
            {[
              doc.attrs?.especie &&
                ["Species", String(doc.attrs.especie).replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())],
              doc.attrs?.medida && ["Size", String(doc.attrs.medida).replace("x", " x ")],
              doc.attrs?.grado && ["Grade", String(doc.attrs.grado)],
              doc.attrs?.marca &&
                ["Brand", String(doc.attrs.marca).replace(/\b\w/g, (c) => c.toUpperCase())],
            ]
              .filter((x): x is [string, string] => Array.isArray(x))
              .map(([k, v]) => (
                <li
                  key={k}
                  className="rounded-full border border-bark-200 bg-white px-3 py-1 text-xs text-bark-600"
                >
                  <span className="text-bark-400">{k}:</span> <strong className="font-medium text-bark-800">{v}</strong>
                </li>
              ))}
          </ul>

          <div className="mt-6">
            <Blocks blocks={doc.blocks} />
          </div>

          {doc.specs && doc.specs.length > 0 && (
            <div className="mt-8">
              <h2 className="mb-3 font-[family-name:var(--font-display)] text-xl font-semibold text-bark-900">
                Specifications
              </h2>
              <SpecTable rows={doc.specs} />
            </div>
          )}
        </div>
      </div>

      {sisters.length > 0 && (
        <Section title="Related products" href={doc.category}>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {sisters.slice(0, 8).map((p) => (
              <ProductCard key={p.path} doc={p} />
            ))}
          </div>
        </Section>
      )}

      <JsonLd
        data={graph(
          productSchema(doc),
          breadcrumbSchema(crumbs),
          ...(doc.faq?.length ? [faqSchema(doc.faq)] : []),
        )}
      />
    </div>
  );
}
