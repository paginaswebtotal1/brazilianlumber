import type { MetadataRoute } from "next";
import { INDEXABLE, SITE_URL } from "@/lib/seo";

/**
 * robots.txt
 *
 * Mientras el portal sea un prototipo, se bloquea TODO para TODOS los bots,
 * incluidos los de los motores generativos (GPTBot, ClaudeBot, PerplexityBot,
 * Google-Extended). El sitio reproduce el contenido de tres dominios que están
 * vivos: si se indexa, Brazilian Lumber compite contra sí misma por duplicado.
 *
 * El bloque de producción, con el sitemap y las reglas finas, está escrito y
 * entra solo con poner NEXT_PUBLIC_INDEXABLE=true.
 */
export default function robots(): MetadataRoute.Robots {
  if (!INDEXABLE) {
    return {
      rules: [{ userAgent: "*", disallow: "/" }],
      // A propósito no se declara sitemap: no hay nada que ofrecer a un
      // rastreador mientras esto sea una prueba.
    };
  }

  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: [
          "/search/", // resultados internos: thin content
          "/cart/",
          "/my-cart/",
          "/checkout/",
          "/my-account/",
          "/register/",
          "/thank-you/",
          "/*?*", // ninguna URL con parámetro debe rastrearse
        ],
      },
      // Los rastreadores de citación de IA sí entran: la visibilidad en motores
      // generativos es un objetivo explícito del proyecto.
      { userAgent: ["GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot"], allow: "/" },
    ],
    sitemap: `${SITE_URL}/sitemap.xml`,
    host: SITE_URL,
  };
}
