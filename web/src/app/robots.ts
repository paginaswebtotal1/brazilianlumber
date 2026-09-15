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
      // generativos es un objetivo explícito del proyecto. Si uno de estos está
      // bloqueado, ese motor no puede citarnos aunque el contenido sea el mejor.
      //
      // Se listan uno a uno y no con un comodín porque cada plataforma usa un
      // agente distinto para buscar y para entrenar, y no son la misma decisión.
      {
        userAgent: [
          "GPTBot", "OAI-SearchBot", "ChatGPT-User",   // OpenAI
          "ClaudeBot", "anthropic-ai", "Claude-Web",   // Anthropic
          "PerplexityBot", "Perplexity-User",          // Perplexity
          "Google-Extended",                           // Gemini y AI Overviews
          "Bingbot", "BingPreview",                    // Copilot
          "Applebot-Extended",                         // Apple Intelligence
          "Amazonbot", "Bytespider", "meta-externalagent",
        ],
        allow: "/",
      },
      // CCBot (Common Crawl) es de entrenamiento, no de citación: permitirlo no
      // nos hace aparecer en ninguna respuesta. Se deja abierto porque alimenta
      // los corpus públicos, pero es una decisión de negocio, no técnica.
      { userAgent: "CCBot", allow: "/" },
    ],
    sitemap: `${SITE_URL}/sitemap.xml`,
    host: SITE_URL,
  };
}
