import type { NextConfig } from "next";

const config: NextConfig = {
  // Las URLs acordadas en el estudio terminan en barra. Sin esto, Next las
  // reescribiria y romperia la equivalencia 1 a 1 con el mapa de redirecciones.
  trailingSlash: true,
  reactStrictMode: true,
  poweredByHeader: false,
  compress: true,
  images: {
    // IMPORTANTE: con trailingSlash activado, Next redirige /_next/image a
    // /_next/image/ con un 308 y el optimizador deja de responder, asi que NO
    // se renderiza ni una sola imagen. Como el pipeline ya entrega las 724
    // fotos en WebP a 1000 px y 34 KB de media, no hay nada que optimizar en
    // tiempo de ejecucion: se sirven tal cual, desde el propio dominio.
    // Ventaja anadida: cero transformaciones de imagen facturables en Vercel.
    unoptimized: true,
    // Se conservan por si algun contenido vuelve a enlazar a los portales viejos.
    remotePatterns: [
      { protocol: "https", hostname: "brazilianlumber.com" },
      { protocol: "https", hostname: "www.brazilianlumber.com" },
      { protocol: "https", hostname: "brazilianlumberlosangeles.com" },
      { protocol: "https", hostname: "www.brazilianlumberlosangeles.com" },
      { protocol: "https", hostname: "brazilianlumbernewyork.com" },
      { protocol: "https", hostname: "www.brazilianlumbernewyork.com" },
    ],
    formats: ["image/avif", "image/webp"],
  },
  async headers() {
    // PROTOTIPO PRIVADO: ningun buscador debe indexar esto. Se manda por cabecera
    // ademas de por meta y por robots.txt, que es lo unico que respetan todos los bots.
    const noindex = process.env.NEXT_PUBLIC_INDEXABLE !== "true";
    return [
      {
        source: "/:path*",
        headers: [
          ...(noindex
            ? [{ key: "X-Robots-Tag", value: "noindex, nofollow, noarchive, nosnippet, noimageindex" }]
            : []),
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "X-Frame-Options", value: "SAMEORIGIN" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline'",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: blob: https:",
              "font-src 'self' data:",
              "connect-src 'self' https://*.supabase.co",
              "frame-ancestors 'self'",
              "base-uri 'self'",
              "form-action 'self'",
            ].join("; "),
          },
        ],
      },
      {
        source: "/search-index.json",
        headers: [{ key: "Cache-Control", value: "public, max-age=3600, stale-while-revalidate=86400" }],
      },
    ];
  },
};

export default config;
