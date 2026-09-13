import Image from "next/image";

/**
 * Imagen de una tarjeta o de una cabecera.
 *
 * Las fotos son las reales de los tres portales, descargadas y recomprimidas a
 * WebP por el pipeline (724 ficheros, 34 KB de media). Se sirven desde el propio
 * portal, no enlazadas: Cloudflare bloquea las peticiones que no vienen de un
 * navegador y su protección de hotlinking podría activarse en cualquier momento.
 *
 * Las pocas fichas que siguen sin foto reciben una portada generada con el color
 * real de la especie. No inventa una fotografía que no existe, y evita el hueco
 * gris que hace que un catálogo parezca roto.
 */
export default function Thumb({
  src,
  alt,
  color = "#5d5344",
  ratio = "4 / 3",
  priority = false,
  sizes = "(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 340px",
  label,
  className = "",
  scrim = false,
}: {
  src?: string | null;
  alt: string;
  color?: string;
  ratio?: string;
  priority?: boolean;
  sizes?: string;
  label?: string;
  className?: string;
  scrim?: boolean;
}) {
  const base = `media ${scrim ? "scrim" : ""} ${className}`;

  if (src) {
    return (
      <div className={base} style={{ aspectRatio: ratio }}>
        <Image
          src={src}
          alt={alt}
          fill
          sizes={sizes}
          priority={priority}
          loading={priority ? undefined : "lazy"}
          quality={82}
        />
      </div>
    );
  }

  // Solo cuentan las palabras que empiezan por letra: si no, "Ipe 5/4x6" daría
  // "I5", que se lee como un error y no como una inicial.
  const words = (label ?? alt).split(/[\s/-]+/).filter((w) => /^[a-z]/i.test(w));
  const initials =
    words.length >= 2
      ? (words[0]![0]! + words[1]![0]!).toUpperCase()
      : (words[0] ?? alt).slice(0, 2).toUpperCase();

  return (
    <div
      className={`woodfill ${base} grid place-items-center`}
      style={{ aspectRatio: ratio, background: color }}
      aria-hidden="true"
    >
      <span className="display text-[2.6rem] leading-none text-white/80">{initials}</span>
    </div>
  );
}
