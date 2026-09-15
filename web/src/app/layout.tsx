import type { Metadata, Viewport } from "next";
import { Inter, Fraunces } from "next/font/google";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { JsonLd } from "@/components/ui";
import { nav, stats } from "@/lib/data";
import { BRAND, ROBOTS, SITE_URL, graph, orgSchema, yardSchemas } from "@/lib/seo";

/**
 * Las fuentes se autoalojan en el build (next/font). No hay petición a Google
 * en tiempo de ejecución: evita el bloqueo de render, el aviso de privacidad y
 * el salto de texto (FOUT), que cuenta como CLS.
 */
const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const fraunces = Fraunces({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-fraunces",
  axes: ["SOFT", "WONK", "opsz"],
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: `${BRAND} — Tropical Hardwood, Composite Decking and Lumber`,
    template: `%s`,
  },
  description:
    "Tropical hardwood decking, composite decking, cladding, fencing and dimensional lumber. In stock in Miami, Los Angeles and New Jersey, cut to order, shipped nationwide.",
  applicationName: BRAND,
  robots: ROBOTS,
  formatDetection: { telephone: false },
};

export const viewport: Viewport = {
  themeColor: "#262019",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en-US" className={`${inter.variable} ${fraunces.variable}`}>
      <body className="flex min-h-screen flex-col antialiased">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-bark-900 focus:px-4 focus:py-2 focus:text-white"
        >
          Skip to content
        </a>
        <Header nav={nav} />
        <main id="main" className="flex-1">
          {children}
        </main>
        <Footer nav={nav} stats={stats} />
        <JsonLd
          data={graph(orgSchema(), {
            "@type": "WebSite",
            "@id": `${SITE_URL}/#website`,
            url: SITE_URL,
            name: BRAND,
            publisher: { "@id": `${SITE_URL}/#organization` },
            potentialAction: {
              "@type": "SearchAction",
              target: { "@type": "EntryPoint", urlTemplate: `${SITE_URL}/search/?q={search_term_string}` },
              "query-input": "required name=search_term_string",
            },
          },
          ...yardSchemas())}
        />
      </body>
    </html>
  );
}
