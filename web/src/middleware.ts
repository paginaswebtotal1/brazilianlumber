import { NextResponse, type NextRequest } from "next/server";

/**
 * El prototipo NO ejecuta redirecciones.
 *
 * Las 622 redirecciones 301 del mapa son una instrucción para el día de la
 * migración real, no un comportamiento de esta maqueta: aquí solo se enseña
 * cómo queda el portal único. El mapa completo está en la hoja 08 del Excel de
 * consolidación, exportado en data/redirect-map.csv y consultable dentro del
 * propio prototipo en /redirect-map/.
 *
 * Lo único que hace este middleware es impedir que una URL con parámetro sea
 * rastreable, que es exactamente el problema que el portal único viene a
 * resolver: los tres sitios de origen generaban 1.379 direcciones con parámetro.
 */
export function middleware(req: NextRequest) {
  if (req.nextUrl.search) {
    const res = NextResponse.next();
    res.headers.set("X-Robots-Tag", "noindex, follow");
    return res;
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|search-index.json|robots.txt|sitemap.xml).*)"],
};
