import type { MetadataRoute } from "next";
import { indexableDocs } from "@/lib/data";
import { absolute } from "@/lib/seo";

/**
 * sitemap.xml
 *
 * Solo entran URLs indexables: quedan fuera las páginas de utilidad (carrito,
 * cuenta, gracias), las 11 páginas de prueba que sobrevivieron a la
 * consolidación y los resultados de búsqueda. Un sitemap que declara páginas
 * noindex es una contradicción que Search Console reporta como error.
 *
 * La prioridad no se inventa: sale de la jerarquía y de los clics reales que
 * cada URL tuvo en los últimos 16 meses según Search Console.
 */
export default function sitemap(): MetadataRoute.Sitemap {
  const docs = indexableDocs();
  const max = Math.max(...docs.map((d) => d.clicks ?? 0), 1);

  const entries: MetadataRoute.Sitemap = docs.map((d) => {
    const depth = d.path.split("/").filter(Boolean).length;
    const demand = Math.log1p(d.clicks ?? 0) / Math.log1p(max);

    let base = 0.5;
    if (d.kind === "category") base = depth <= 1 ? 0.9 : 0.8;
    else if (d.kind === "product") base = 0.7;
    else if (d.kind === "post") base = 0.6;
    else if (d.kind === "postcat") base = 0.5;
    else if (d.sub === "location") base = 0.6;

    return {
      url: absolute(d.path),
      lastModified: d.modified ? new Date(d.modified) : new Date(),
      changeFrequency:
        d.kind === "category" ? "weekly" : d.kind === "product" ? "monthly" : ("monthly" as const),
      priority: Math.round(Math.min(0.95, base + demand * 0.2) * 100) / 100,
    };
  });

  return [
    {
      url: absolute("/"),
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 1,
    },
    { url: absolute("/shop/"), lastModified: new Date(), changeFrequency: "weekly", priority: 0.9 },
    { url: absolute("/guides/"), lastModified: new Date(), changeFrequency: "weekly", priority: 0.8 },
    ...entries.filter((e) => !["/", "/shop/", "/guides/"].includes(e.url.replace(/^https?:\/\/[^/]+/, ""))),
  ];
}
