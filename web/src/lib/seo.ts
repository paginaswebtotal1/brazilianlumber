import type { Metadata } from "next";
import type { Doc } from "./data";

/**
 * SEO del portal.
 *
 * Aviso importante: mientras NEXT_PUBLIC_INDEXABLE no sea "true", TODO el sitio
 * sale con noindex/nofollow. Es un prototipo alojado en un dominio distinto al
 * real y, si Google lo indexa, compite contra brazilianlumber.com por su propio
 * contenido. Toda la maquinaria de SEO está construida y es verificable, pero
 * el interruptor está en off hasta que el portal sea el de producción.
 */

export const INDEXABLE = process.env.NEXT_PUBLIC_INDEXABLE === "true";

/**
 * La URL con la que el sitio se nombra a sí mismo: canonicals, sitemap, Open
 * Graph y los @id del JSON-LD.
 *
 * Sin esto, en Vercel salían canonicals apuntando a `http://localhost:3000`,
 * porque `NEXT_PUBLIC_SITE_URL` solo está definida en el `.env.local` de
 * desarrollo y en producción no existía. En local no se veía: en local ESA es
 * la respuesta correcta.
 *
 * Vercel inyecta su dominio de producción por su cuenta, así que se usa como
 * respaldo y el prototipo se nombra bien esté donde esté, sin depender de que
 * alguien se acuerde de configurar una variable en el panel.
 */
const VERCEL = process.env.NEXT_PUBLIC_VERCEL_PROJECT_PRODUCTION_URL
  || process.env.NEXT_PUBLIC_VERCEL_URL;

export const SITE_URL = (
  process.env.NEXT_PUBLIC_SITE_URL
  || (VERCEL ? `https://${VERCEL}` : "http://localhost:3000")
).replace(/\/$/, "");

/** Dominio definitivo del portal unificado, el que llevan los canonicals reales. */
export const CANONICAL_HOST = "https://brazilianlumber.com";

export const BRAND = "Brazilian Lumber";

export const ROBOTS = INDEXABLE
  ? { index: true, follow: true }
  : {
      index: false,
      follow: false,
      nocache: true,
      googleBot: { index: false, follow: false, noimageindex: true, "max-snippet": -1 as const },
    };

export function absolute(path: string): string {
  return SITE_URL + path;
}

/**
 * URL canónica. En el prototipo apunta al propio prototipo (autorreferencial),
 * que es lo correcto: un canonical cruzado al dominio real haría que Google
 * consolidara señales de un sitio de pruebas sobre el de producción.
 */
export function canonical(path: string): string {
  return absolute(path);
}

/**
 * Título de la página.
 *
 * Si el documento trae `seoTitle`, ese manda: lo escribe `p23_seo.py` a partir
 * del término que de verdad se busca, con su volumen mensual medido, y ya viene
 * recortado a 60 caracteres y desempatado contra el resto del portal. El resto
 * es el respaldo de siempre, por si un documento llega sin pasar por ese paso.
 */
export function titleFor(doc: Doc): string {
  if (doc.seoTitle) return doc.seoTitle;
  const t = doc.title?.trim() || doc.slug.replace(/-/g, " ");
  switch (doc.kind) {
    case "product":
      return `${t} | ${doc.categoryTitle ?? "Products"} | ${BRAND}`;
    case "category":
      return `${t} | ${BRAND}`;
    case "post":
      return `${t} | ${BRAND} Guides`;
    case "postcat":
      return `${t} Guides | ${BRAND}`;
    default:
      return `${t} | ${BRAND}`;
  }
}

export function descriptionFor(doc: Doc): string {
  if (doc.seoDescription) return doc.seoDescription.slice(0, 158);
  const d = (doc.description || "").replace(/\s+/g, " ").trim();
  if (d.length >= 70) return d.slice(0, 158);
  const body = doc.blocks.find((b) => b.t === "p" && "text" in b) as { text: string } | undefined;
  const fill = (d + " " + (body?.text ?? "")).replace(/\s+/g, " ").trim();
  return (fill || `${doc.title} at ${BRAND}.`).slice(0, 158);
}

export function metaFor(doc: Doc, extra: Partial<Metadata> = {}): Metadata {
  const title = titleFor(doc);
  const description = descriptionFor(doc);
  const url = canonical(doc.path);
  const img = doc.image || undefined;
  return {
    title,
    description,
    alternates: { canonical: url },
    robots: doc.noindex ? { index: false, follow: false } : ROBOTS,
    openGraph: {
      type: doc.kind === "post" ? "article" : "website",
      title,
      description,
      url,
      siteName: BRAND,
      locale: "en_US",
      images: img ? [{ url: img, alt: doc.title }] : undefined,
    },
    twitter: {
      card: img ? "summary_large_image" : "summary",
      title,
      description,
      images: img ? [img] : undefined,
    },
    ...extra,
  };
}

// ---------------------------------------------------------------- JSON-LD

type Json = Record<string, unknown>;

export function orgSchema(): Json {
  return {
    "@type": "Organization",
    "@id": `${SITE_URL}/#organization`,
    name: BRAND,
    url: SITE_URL,
    description:
      "Supplier of tropical hardwood decking, composite decking, cladding and dimensional lumber, with yards in Miami, Los Angeles and New Jersey.",
    foundingDate: "2006",
    knowsAbout: [
      "tropical hardwood decking", "Ipe", "Cumaru", "Garapa", "Jatoba", "Tigerwood",
      "Massaranduba", "Red Balau", "thermally modified wood", "composite decking",
      "PVC decking", "wood cladding", "rainscreen siding", "dimensional lumber",
    ],
    areaServed: "US",
    location: [
      { "@type": "Place", name: "Miami yard", address: { "@type": "PostalAddress", addressLocality: "Miami", addressRegion: "FL", addressCountry: "US" } },
      { "@type": "Place", name: "Los Angeles yard", address: { "@type": "PostalAddress", addressLocality: "Los Angeles", addressRegion: "CA", addressCountry: "US" } },
      { "@type": "Place", name: "New Jersey yard", address: { "@type": "PostalAddress", addressLocality: "Newark", addressRegion: "NJ", addressCountry: "US" } },
    ],
  };
}

export function breadcrumbSchema(items: { path: string; title: string }[]): Json {
  return {
    "@type": "BreadcrumbList",
    itemListElement: items.map((it, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: it.title,
      item: absolute(it.path),
    })),
  };
}

export function productSchema(doc: Doc): Json {
  const props = (doc.specs ?? []).map(([name, value]) => ({
    "@type": "PropertyValue",
    name,
    value,
  }));
  return {
    "@type": "Product",
    "@id": `${absolute(doc.path)}#product`,
    name: doc.title,
    alternateName: doc.alsoKnownAs?.length ? doc.alsoKnownAs : undefined,
    description: descriptionFor(doc),
    url: absolute(doc.path),
    speakable: doc.answerBlock ? SPEAKABLE : undefined,
    image: doc.gallery?.length ? doc.gallery : undefined,
    category: doc.categoryTitle,
    brand: { "@type": "Brand", name: doc.attrs?.marca ? String(doc.attrs.marca) : BRAND },
    material: doc.attrs?.especie ? String(doc.attrs.especie).replace(/-/g, " ") : undefined,
    additionalProperty: props.length ? props : undefined,
    offers: {
      "@type": "Offer",
      availability: "https://schema.org/InStock",
      priceCurrency: "USD",
      url: absolute(doc.path),
      seller: { "@id": `${SITE_URL}/#organization` },
    },
  };
}

export function articleSchema(doc: Doc): Json {
  return {
    "@type": "Article",
    "@id": `${absolute(doc.path)}#article`,
    headline: doc.title,
    description: descriptionFor(doc),
    url: absolute(doc.path),
    image: doc.image || undefined,
    datePublished: doc.date || doc.modified,
    dateModified: doc.modified || doc.date,
    author: { "@type": "Organization", name: BRAND },
    publisher: { "@id": `${SITE_URL}/#organization` },
    speakable: doc.answerBlock ? SPEAKABLE : undefined,
    wordCount: doc.words || undefined,
  };
}

export function faqSchema(faq: { q: string; a: string }[]): Json {
  return {
    "@type": "FAQPage",
    mainEntity: faq.map((f) => ({
      "@type": "Question",
      name: f.q,
      acceptedAnswer: { "@type": "Answer", text: f.a },
    })),
  };
}

/**
 * Bloque de respuesta destacado.
 *
 * Los motores generativos no citan paginas, citan pasajes. `speakable` marca
 * cual es el pasaje que contesta la consulta, y `alternateName` le dice al motor
 * que 'Brazilian cherry' y 'Jatoba' son la misma entidad: sin eso, una pregunta
 * por el nombre comercial no encuentra la pagina del nombre botanico.
 */
const SPEAKABLE = {
  "@type": "SpeakableSpecification",
  cssSelector: [".answer-block", "h1"],
};

export function collectionSchema(doc: Doc, items: Doc[]): Json {
  return {
    "@type": "CollectionPage",
    "@id": `${absolute(doc.path)}#collection`,
    name: doc.title,
    alternateName: doc.alsoKnownAs?.length ? doc.alsoKnownAs : undefined,
    description: descriptionFor(doc),
    url: absolute(doc.path),
    dateModified: doc.reviewed || doc.modified || undefined,
    speakable: doc.answerBlock ? SPEAKABLE : undefined,
    abstract: doc.answerBlock || undefined,
    mainEntity: {
      "@type": "ItemList",
      numberOfItems: items.length,
      itemListElement: items.slice(0, 30).map((p, i) => ({
        "@type": "ListItem",
        position: i + 1,
        name: p.title,
        url: absolute(p.path),
      })),
    },
  };
}

/** Empaqueta varios nodos en un solo @graph, que es como se sirve mejor. */
export function graph(...nodes: Json[]): string {
  return JSON.stringify({ "@context": "https://schema.org", "@graph": nodes.filter(Boolean) });
}
