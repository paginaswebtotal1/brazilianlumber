"use client";

import { useState } from "react";
import Link from "next/link";
import { Menu, X, ChevronDown, MapPin, Phone } from "lucide-react";
import SearchBox from "./SearchBox";
import type { Nav, NavNode } from "@/lib/data";

/**
 * Cabecera y menú unificado.
 *
 * Es la traducción a código del menú que se acordó en el estudio: un solo árbol
 * de producto de tres niveles como máximo, más Guides, Areas We Serve y Company.
 * Sustituye a los tres menús distintos que tenían Miami, Los Ángeles y Nueva
 * Jersey, cada uno con su propia nomenclatura para el mismo producto.
 */
export default function Header({ nav }: { nav: Nav }) {
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [mobile, setMobile] = useState(false);

  const close = () => setOpenMenu(null);

  return (
    <header className="sticky top-0 z-40 border-b border-bark-200 bg-bark-50/95 backdrop-blur supports-[backdrop-filter]:bg-bark-50/80">
      <div className="hidden bg-bark-900 text-bark-200 md:block">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-1.5 text-xs">
          <p className="flex items-center gap-1.5">
            <MapPin size={13} aria-hidden /> Yards in Miami, Los Angeles and New Jersey · Nationwide freight
          </p>
          <p className="flex items-center gap-4">
            <Link href="/request-a-quote/" className="hover:text-white">
              Request a quote
            </Link>
            <span className="flex items-center gap-1.5">
              <Phone size={13} aria-hidden /> Sales desk open 7am – 5pm ET
            </span>
          </p>
        </div>
      </div>

      <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3">
        <Link href="/" className="shrink-0" onClick={close}>
          <span className="block font-[family-name:var(--font-display)] text-xl leading-none font-semibold tracking-tight text-bark-900">
            Brazilian Lumber
          </span>
          <span className="block text-[10px] uppercase tracking-[0.18em] text-bark-500">
            One catalog · Three yards
          </span>
        </Link>

        <nav aria-label="Main" className="ml-4 hidden items-center gap-1 lg:flex">
          <MenuButton
            label="Products"
            open={openMenu === "shop"}
            onToggle={() => setOpenMenu(openMenu === "shop" ? null : "shop")}
          />
          <MenuButton
            label="Guides"
            open={openMenu === "guides"}
            onToggle={() => setOpenMenu(openMenu === "guides" ? null : "guides")}
          />
          <MenuButton
            label="Areas We Serve"
            open={openMenu === "loc"}
            onToggle={() => setOpenMenu(openMenu === "loc" ? null : "loc")}
          />
          <MenuButton
            label="Company"
            open={openMenu === "co"}
            onToggle={() => setOpenMenu(openMenu === "co" ? null : "co")}
          />
        </nav>

        <div className="ml-auto hidden min-w-0 flex-1 max-w-md lg:block">
          <SearchBox placeholder="Search products and guides…" />
        </div>

        <button
          type="button"
          aria-label={mobile ? "Close menu" : "Open menu"}
          aria-expanded={mobile}
          onClick={() => setMobile(!mobile)}
          className="ml-auto rounded-md p-2 text-bark-700 lg:hidden"
        >
          {mobile ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* ---- mega menú de escritorio ---- */}
      {openMenu && (
        <>
          <div className="fixed inset-0 top-0 -z-10 hidden lg:block" onMouseDown={close} aria-hidden />
          <div className="hidden border-t border-bark-200 bg-white shadow-lg lg:block" onMouseLeave={close}>
            <div className="mx-auto max-w-7xl px-4 py-6">
              {openMenu === "shop" && <ShopMenu nodes={nav.shop} onNav={close} />}
              {openMenu === "guides" && (
                <Columns
                  title="Guides"
                  href={nav.guides.path}
                  items={nav.guides.cats.map((c) => ({ ...c, meta: `${c.count}` }))}
                  onNav={close}
                />
              )}
              {openMenu === "loc" && (
                <Columns title="Areas We Serve" href={nav.locations.path} items={nav.locations.items} onNav={close} />
              )}
              {openMenu === "co" && <Columns title="Company" items={nav.company} onNav={close} />}
            </div>
          </div>
        </>
      )}

      {/* ---- menú móvil ---- */}
      {mobile && (
        <div className="border-t border-bark-200 bg-white lg:hidden">
          <div className="px-4 py-3">
            <SearchBox />
          </div>
          <nav aria-label="Mobile" className="max-h-[70vh] overflow-y-auto px-4 pb-6">
            <MobileGroup label="Products">
              {nav.shop.map((n) => (
                <MobileNode key={n.path} node={n} onNav={() => setMobile(false)} />
              ))}
            </MobileGroup>
            <MobileGroup label="Guides">
              <MobileLink href={nav.guides.path} onNav={() => setMobile(false)}>
                All guides
              </MobileLink>
              {nav.guides.cats.slice(0, 14).map((c) => (
                <MobileLink key={c.path} href={c.path} onNav={() => setMobile(false)}>
                  {c.title}
                </MobileLink>
              ))}
            </MobileGroup>
            <MobileGroup label="Areas We Serve">
              {nav.locations.items.slice(0, 18).map((c) => (
                <MobileLink key={c.path} href={c.path} onNav={() => setMobile(false)}>
                  {c.title}
                </MobileLink>
              ))}
            </MobileGroup>
            <MobileGroup label="Company">
              {nav.company.map((c) => (
                <MobileLink key={c.path} href={c.path} onNav={() => setMobile(false)}>
                  {c.title}
                </MobileLink>
              ))}
            </MobileGroup>
          </nav>
        </div>
      )}
    </header>
  );
}

function MenuButton({ label, open, onToggle }: { label: string; open: boolean; onToggle: () => void }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      onMouseEnter={onToggle}
      aria-expanded={open}
      className={`flex items-center gap-1 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
        open ? "bg-bark-100 text-bark-900" : "text-bark-700 hover:text-bark-900"
      }`}
    >
      {label}
      <ChevronDown size={14} className={open ? "rotate-180 transition-transform" : "transition-transform"} aria-hidden />
    </button>
  );
}

function ShopMenu({ nodes, onNav }: { nodes: NavNode[]; onNav: () => void }) {
  return (
    <div className="grid grid-cols-4 gap-x-8 gap-y-6">
      {nodes.map((n) => (
        <div key={n.path}>
          <Link
            href={n.path}
            onClick={onNav}
            className="flex items-baseline justify-between gap-2 border-b border-bark-200 pb-1.5 text-sm font-semibold text-bark-900 hover:text-ember-600"
          >
            {n.title}
            <span className="text-[11px] font-normal text-bark-400">{n.count}</span>
          </Link>
          <ul className="mt-2 space-y-1">
            {n.children.map((c) => (
              <li key={c.path}>
                <Link
                  href={c.path}
                  onClick={onNav}
                  className="block truncate py-0.5 text-[13px] text-bark-600 hover:text-ember-600"
                >
                  {c.title}
                  {c.count > 0 && <span className="ml-1.5 text-[11px] text-bark-400">{c.count}</span>}
                </Link>
                {c.children.length > 0 && (
                  <ul className="ml-3 border-l border-bark-200 pl-2">
                    {c.children.map((g) => (
                      <li key={g.path}>
                        <Link
                          href={g.path}
                          onClick={onNav}
                          className="block truncate py-0.5 text-[12px] text-bark-500 hover:text-ember-600"
                        >
                          {g.title}
                        </Link>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

function Columns({
  title,
  href,
  items,
  onNav,
}: {
  title: string;
  href?: string;
  items: { path: string; title: string; meta?: string }[];
  onNav: () => void;
}) {
  return (
    <div>
      <div className="mb-3 flex items-baseline gap-3 border-b border-bark-200 pb-1.5">
        <h2 className="text-sm font-semibold text-bark-900">{title}</h2>
        {href && (
          <Link href={href} onClick={onNav} className="text-xs text-ember-600 hover:underline">
            View all
          </Link>
        )}
      </div>
      <ul className="grid grid-cols-5 gap-x-6 gap-y-1">
        {items.map((c) => (
          <li key={c.path}>
            <Link
              href={c.path}
              onClick={onNav}
              className="block truncate py-0.5 text-[13px] text-bark-600 hover:text-ember-600"
            >
              {c.title}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

function MobileGroup({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <details className="border-b border-bark-200 py-1">
      <summary className="cursor-pointer list-none py-2.5 text-sm font-semibold text-bark-900">{label}</summary>
      <div className="pb-2">{children}</div>
    </details>
  );
}

function MobileNode({ node, onNav }: { node: NavNode; onNav: () => void }) {
  return (
    <div className="py-1">
      <Link href={node.path} onClick={onNav} className="block py-1 text-[13px] font-medium text-bark-800">
        {node.title}
      </Link>
      <ul className="ml-3 border-l border-bark-200 pl-3">
        {node.children.map((c) => (
          <li key={c.path}>
            <Link href={c.path} onClick={onNav} className="block py-1 text-[13px] text-bark-600">
              {c.title}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

function MobileLink({ href, children, onNav }: { href: string; children: React.ReactNode; onNav: () => void }) {
  return (
    <Link href={href} onClick={onNav} className="block py-1.5 text-[13px] text-bark-600">
      {children}
    </Link>
  );
}
