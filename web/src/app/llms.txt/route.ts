import { INDEXABLE } from "@/lib/seo";
import llms from "@/data/llms.json";

/**
 * /llms.txt — el mapa del sitio para sistemas de IA.
 *
 * Va detrás del MISMO interruptor que robots.txt, y por una razón concreta:
 * este fichero no es documentación, es una invitación. Le entrega a un modelo
 * el catálogo entero, las especies con sus cifras y las zonas que servimos.
 *
 * Mientras esto sea un prototipo que reproduce el contenido de tres dominios
 * vivos, esa invitación no puede estar abierta: responde 404. Servirlo como
 * fichero estático en /public fue un error, porque los estáticos no pasan por
 * la cabecera X-Robots-Tag y se quedaba fuera del bloqueo.
 */
export const dynamic = "force-static";

export function GET() {
  if (!INDEXABLE) {
    return new Response("Not found", {
      status: 404,
      headers: {
        "content-type": "text/plain; charset=utf-8",
        "x-robots-tag": "noindex, nofollow, noarchive, nosnippet, noimageindex",
      },
    });
  }
  return new Response(llms.text, {
    headers: {
      "content-type": "text/plain; charset=utf-8",
      "cache-control": "public, max-age=3600",
    },
  });
}
