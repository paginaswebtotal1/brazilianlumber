# Brazilian Lumber — prototipo del portal único

Maqueta funcional del portal que sustituye a **brazilianlumber.com**, **brazilianlumberlosangeles.com** y **brazilianlumbernewyork.com**.

No es una presentación ni un mockup: es el sitio construido, navegable y con las **797 URLs finales** publicadas, cada una con su contenido, su canonical, sus migas de pan y su marcado de datos estructurados.

> **Aviso.** Es un prototipo interno. Está bloqueado a todos los buscadores (`robots.txt`, `<meta robots>` y cabecera `X-Robots-Tag`) porque reproduce el contenido de tres dominios que siguen vivos. Si Google lo indexara, Brazilian Lumber competiría contra sí misma por duplicado.

---

## De dónde sale esto

No se ha inventado nada. Todo viene del trabajo que ya estaba hecho en `ARQUITECTURA WEB BL/MENÙ VISUAL`:

| Fuente | Qué aporta |
|---|---|
| Carpeta 8, `datos/mapa.json` | Las 2.197 URLs decididas: qué se conserva, qué se fusiona, qué se apaga |
| Carpeta 8, `datos/rest_full.jsonl` | El contenido real de las tres webs, extraído por la API REST de WordPress (48 MB) |
| Carpeta 8, `datos/taxonomia.py` | El árbol de destino acordado y la regla de oro: los productos viven siempre en `/product/{slug}/` |
| Carpeta 3 y 4 | El menú unificado y las keywords que lo sostienen |
| Search Console (16 meses) | Los clics reales de cada URL, que aquí ordenan resultados de búsqueda y prioridades del sitemap |

---

## Las cifras

| Concepto | Cantidad |
|---|---|
| URLs rastreadas en los 3 portales | 2.197 |
| **URLs únicas en el portal nuevo** | **797** |
| Categorías de producto | 50 |
| Fichas de producto | 268 |
| Artículos del blog | 229 |
| Temas del blog | 70 |
| Páginas (institucionales, ciudad, campaña) | 180 |
| Equivalencias de URL documentadas | **1.505** |
| URLs de etiqueta que pasan a noindex | 722 |
| Fichas con contenido reescrito por duplicidad | 97 |

Comprobado automáticamente en cada build (`pipeline/p5_check.py`, 803 URLs):

```
no 200          : 0
sin un unico H1 : 0
sin <title>     : 0
sin description : 0
sin canonical   : 0
sin JSON-LD     : 0
SIN noindex     : 0
```

---

## Qué resuelve

**1. La duplicidad.** Los tres portales tenían 488 páginas con contenido duplicado, incluido un grupo de 135 fichas de Ipe que compartían la descripción palabra por palabra. Aquí cada URL tiene texto propio: especie, dureza Janka real, densidad, medida nominal y real, vida útil, notas de instalación y FAQ, generados a partir de los atributos de cada producto.

**2. Las URLs con parámetro.** Había 1.379. En el portal nuevo filtrar **no crea ninguna URL**: los filtros del catálogo viven en el estado del cliente, y las direcciones indexables son exactamente las de la taxonomía.

**3. La canonicalización.** Un producto puede estar en varias categorías y sigue teniendo una sola dirección, `/product/{slug}/`. Es la decisión de arquitectura que corta el problema de raíz.

**4. Los tres menús.** Uno solo, de tres niveles como máximo, con el árbol acordado en la carpeta 3.

---

## Las redirecciones

**El prototipo no redirige nada.** Es una maqueta del destino, no la migración.

El mapa de qué dirección antigua corresponde a cuál nueva está en tres sitios, con el mismo contenido:

- La hoja **08** del Excel `8 - CONSOLIDACION - MAPA DE URLS UNICAS.xlsx`
- `data/redirect-map.csv`, listo para el desarrollador (lo genera `pipeline/p21_redirect_map.py`)
- **`/redirect-map/`** dentro del propio prototipo: tabla filtrable, para responder en la reunión sin abrir el Excel

De las 622 equivalencias, 71 salen de brazilianlumber.com y 551 de los dos dominios que se apagan. Esas 551 se configuran en el hosting de cada dominio el día de la migración, no aquí.

---

## Tecnología

Todo gratuito y estándar, sin ninguna licencia de pago:

| Pieza | Elección | Por qué |
|---|---|---|
| Framework | Next.js 15 (App Router) + React 19 | Renderizado en servidor: HTML completo en la primera respuesta, que es lo que leen Googlebot y los rastreadores de citación de IA |
| Lenguaje | TypeScript | |
| Estilos | Tailwind CSS v4 | Sin runtime de CSS-in-JS |
| Buscador | MiniSearch (MIT) en cliente + PostgreSQL full-text en servidor | Ver abajo |
| Base de datos | Supabase (plan gratuito) | PostgreSQL con `tsvector` y `pg_trgm` |
| Iconos | lucide-react (ISC) | |
| Alojamiento | Vercel, Cloudflare Pages o cualquier Node | Ver `docs/DESPLIEGUE.md` |

**La base de datos es opcional por diseño.** Si no hay credenciales de Supabase, el portal funciona igual leyendo el dataset generado. Es deliberado: el prototipo que ve dirección no puede caerse porque un plan gratuito se haya dormido.

---

## El buscador

Es la pieza que más se va a mirar en la demo, así que está resuelto en dos capas.

**En el navegador.** Un índice de 827 documentos (~620 KB, ~120 KB comprimido) se descarga **una sola vez**, la primera vez que alguien toca el buscador, nunca en la carga inicial de la página. A partir de ahí cada pulsación se resuelve en memoria: el resultado aparece en menos de 10 ms sin ida y vuelta al servidor.

Detalles que lo hacen útil de verdad:

- **Entiende las medidas.** `5/4x6`, `5/4 x 6` y `54x6` caen en el mismo término. Buscar `ipe 5/4x6` devuelve la ficha correcta en primer lugar.
- **Tolera erratas** (distancia de edición) y busca por prefijo mientras se escribe.
- **Pondera por campo**: el título y los atributos (especie, marca, medida) pesan seis y cuatro veces más que el cuerpo del texto.
- **Desempata con datos reales**: entre dos páginas igual de relevantes gana la que más clics tiene en Search Console.
- Atajo `/` desde cualquier página, navegación con flechas y Enter.

**En el servidor.** `GET /api/search/?q=...` responde sin JavaScript, para integraciones y para rastreadores. Usa la función `search_documents` de PostgreSQL (`tsvector` con pesos A/B/C + similitud por trigramas) cuando Supabase está configurado, y un ranking local equivalente cuando no.

---

## La propuesta de keywords, aplicada

El 3 de septiembre de 2026 Felipe pidió por escrito que la estrategia dejara de dar por hecho que el cliente conoce el nombre de la especie. El **archivo 11** de `ARQUITECTURA WEB BL/MENÙ VISUAL` mide esa demanda; `p23_seo.py` la aplica al portal. Qué cambia en el sitio:

| Cambio | Alcance |
|---|---|
| Título y meta escritos desde el término que de verdad se busca, con su volumen medido | Las 797 URLs |
| Metas reescritas porque no contenían la keyword de la página | 64 |
| Títulos desempatados para que no haya dos iguales en el portal | 38 |
| Párrafo que explica la equivalencia comercial y la diferencia botánica | 10 especies |
| H1 que lidera con el nombre comercial donde ese nombre gana en volumen | Jatoba, Red Balau |
| Etiqueta del menú con el nombre por el que se busca | 2 |

**La regla, en una línea:** manda el término con más volumen. `brazilian cherry` mide 1.600 búsquedas/mes y `jatoba` 1.300, así que la categoría titula «Brazilian Cherry Decking (Jatoba)» y el menú dice «Brazilian Cherry (Jatoba)». Donde gana el botánico —Ipe, Cumaru, Garapa, Tigerwood— el título no se toca y el nombre comercial entra en el cuerpo.

**Ninguna página afirma una especie que no es.** Cada una lleva el párrafo que lo aclara con el nombre botánico delante: Jatoba es *Hymenaea courbaril*, no cerezo; Red Balau es *Shorea*, no *Swietenia*, y la página lo dice con esas palabras. Era una condición explícita del correo.

**Red Balau / Batu no tiene surtido.** `philippine mahogany` mide 720 búsquedas/mes, el doble que `red balau`, y en los tres portales no hay ni una ficha: lo único que existía era una landing heredada de Los Ángeles. Se ha reescrito como `/batu/`, con el contenido que captura esa búsqueda y explica la diferencia técnica, y **queda pendiente la decisión de negocio** de darle surtido y convertirla en categoría. Crear la categoría vacía repetiría el problema de las 3 categorías sin producto.

## La capa GEO: que nos citen los motores generativos

Un motor generativo no cita páginas, cita **pasajes**, y solo puede citar lo que se sostiene solo. `p24_geo.py` aplica eso a las 797 URLs:

| Cambio | Alcance |
|---|---|
| **Bloque de respuesta** de 35 a 70 palabras, con cifras, al principio de la página | **426 URLs** |
| Preguntas medidas contestadas con dato propio, dentro del FAQ | 17 |
| **Tablas comparativas** — el formato más citado, ~33 % de las citas | 10 |
| Cifras unificadas contra un solo origen (`kb.ESPECIES`) | 37 |
| Afirmaciones de fuego matizadas | 32 |
| Entidades con `alternateName` en el JSON-LD | 12 |
| Fecha de revisión y autoría visibles | 797 |
| `llms.txt` publicado | 8 KB |

Así queda la página de Ipe, y es lo que un motor puede citar entero sin leer nada más:

> Ipe is a tropical hardwood used for exterior decking, cladding and dimensional lumber. It rates 3,680 lbf on the Janka hardness scale, weighs about 1,100 kg/m3 air dried, and lasts 50+ years outdoors with no chemical treatment. It is also sold as Brazilian Walnut. Brazilian Lumber stocks 34 Ipe items in Miami, Los Angeles and New Jersey.

Va con la clase `answer-block`, que es a la que apunta `speakable` en el JSON-LD.

**Tres arreglos que hicieron falta antes.** Las cifras Janka no coincidían entre páginas (3.510 contra 3.680 para el mismo Ipe): un motor que lea las dos versiones descarta las dos, así que ahora hay un solo origen. **99 páginas afirmaban un `Class A fire rating` sin respaldo**, que es justo lo que Felipe advirtió por escrito; las 32 menciones activas ahora dicen que es un resultado ASTM E84 de la especie ensayada, no una certificación de un tablón concreto. Y `robots.txt` solo permitía cuatro robots de IA: ahora lista los catorce que importan, uno a uno, porque **si uno está bloqueado ese motor no puede citarnos** por bueno que sea el contenido.

## Enlazado interno

La auditoría contra el sitio construido encontró **115 páginas sin un solo enlace entrante**. No eran páginas menores: un artículo con 768 clics, la calculadora, la página de contacto y `/ceiling-soffit/`, que tiene 18.100 búsquedas/mes medidas. Google llegaba a ellas solo por el sitemap y la autoridad del dominio no les llegaba en absoluto.

`p25_enlaces.py` lo arregla con cuatro mecanismos, todos a partir de datos que ya estaban:

| Mecanismo | Enlaces |
|---|---|
| Enlace contextual por entidad: la primera mención de una especie, marca o categoría con página propia pasa a ser enlace | **2.465** |
| Artículo enlazado a sus hermanos del mismo tema | 181 |
| Ficha enlazada a contacto y presupuesto | 268 |
| Guía enlazada a la categoría de la que habla | 104 |
| Landing de mercado enlazada desde su categoría fuerte | 20 |
| Páginas útiles añadidas a la navegación | 7 |
| **Índice HTML reconstruido** (`/sitemap/` venía de WordPress en noindex, con un bloque de base64 y listas sin enlaces) | **729** |

**Resultado medido: de 115 páginas huérfanas a 26, y ninguna de las 26 es indexable.** Son páginas de prueba y de utilidad que ya estaban en noindex a propósito.

Los enlaces por entidad se guardan como datos (`refs: [{term, path}]`), no como HTML: el renderizador busca texto plano y enlaza la primera aparición, así que no hay forma de inyectar marcado desde el contenido.

## Datos estructurados

| Añadido | Por qué |
|---|---|
| `sku` en las 268 fichas | Un `Product` sin identificador no se consolida como entidad |
| `AggregateOffer` en lugar de `Offer` | Un `Offer` sin `price` ni `priceSpecification` es inválido y sale como error en Search Console. Aquí el precio depende de medida, largo y flete: no hay un número que poner |
| `LocalBusiness` de las **tres** sedes | La capa transaccional/local tiene el mejor CTR de las cinco (1,156 %) y sin esto un motor no sabe que hay un almacén físico detrás de una página de ciudad |
| `telephone` en `Organization` | +1-877-606-3306, el que aparece 241 veces en el contenido de origen |
| `knowsAbout` con 14 entidades | Resolución de entidad para los motores generativos |

Las tres direcciones salen del contenido de los portales de origen, que las declara con todas las letras: *"We have warehouses and showrooms in Miami, FL; Los Angeles, CA; and North Brunswick, NJ"*.

| Sede | Dirección | Teléfono |
|---|---|---|
| Miami | 777 NW 71st St, Miami, FL 33150 | (954) 287-0816 |
| Los Ángeles | 4629 S Alameda St, Los Angeles, CA 90058 | (323) 990-7871 |
| New Jersey | 593 Nassau St, North Brunswick Township, NJ 08902 | (908) 388-4434 |

**No se declaran horarios.** El contenido solo dice *"generally open Monday through Friday, with Saturday hours at select locations"*, y un `openingHours` inventado es peor que ninguno.

Queda una dirección sin identificar: **2800 N 29th Ave, Hollywood FL 33020**, que aparece junto a la de Miami en un bloque de contacto pero sin decir qué es. Si es una cuarta sede, hay que añadirla; si no, hay que quitarla del contenido.

## SEO y GEO

Implementado y verificable, con el interruptor de indexación en **off**:

- Canonical autorreferencial en las 838 URLs
- `sitemap.xml` generado desde los datos, solo con URLs indexables, con prioridad calculada a partir de la jerarquía y de los clics reales
- `robots.txt` con dos modos: bloqueo total en prototipo; en producción, reglas finas más permiso explícito a GPTBot, ClaudeBot, PerplexityBot y Google-Extended
- Migas de pan visibles y `BreadcrumbList`
- JSON-LD en `@graph`: `Organization`, `WebSite` con `SearchAction`, `Product` con `additionalProperty`, `Article`, `FAQPage`, `CollectionPage`
- Un solo `<h1>` por página, jerarquía de encabezados correcta
- Open Graph y Twitter Card
- Sin URLs con parámetro indexables
- Core Web Vitals: `aspect-ratio` reservado en toda imagen para no generar CLS, `preconnect` a los dominios que sirven las fotos, `priority` solo en las imágenes visibles al cargar

---

## Cómo se levanta

```bash
cd web
npm install
npm run dev          # http://localhost:3000
```

Para regenerar el dataset desde los datos originales:

```bash
cd pipeline
python p1_extract.py    # limpia el contenido de los 3 portales
python p2_classify.py   # clasifica los 295 productos en la taxonomía
python p3_build.py      # genera el contenido único y el menú
python p23_seo.py       # aplica la propuesta de keywords: títulos, metas, nombres comerciales
python p4_export.py     # índice de búsqueda, SQL de Supabase, informe de QA
python p5_check.py      # comprueba las 844 URLs contra el servidor local
```

Supabase es opcional y está documentado en `docs/SUPABASE.md`.

Por qué cada ficha acaba donde acaba — y por qué dejó de acabar en `/accessories/` — está en `docs/CLASIFICACION.md`.

---

## Qué falta antes de que esto sea el sitio real

Está todo en **`QA-PROTOTIPO.md`**, generado automáticamente. En resumen:

1. **13 categorías del menú no tienen ningún producto.** Existen en el árbol acordado pero ningún producto de los tres portales cae en ellas. Hay que asignarles surtido o sacarlas del menú.
2. **285 de las 295 fichas llegaron sin fotografía.** El prototipo las muestra con una portada generada por color de especie. Hacen falta las fotos reales.
3. **11 páginas de prueba sobrevivieron a la consolidación** (`demo-home`, `hometest`, `blog-example`, `test-form-flowsly`…). Están publicadas para no perder ninguna URL, pero en noindex y fuera del menú y del sitemap. Deberían eliminarse.
4. Los textos generados son **técnicamente correctos y únicos**, pero conviene que Marketing los revise antes de publicarlos como definitivos.

---

## Estructura

El pipeline va numerado por orden de ejecucion. Los ficheros sin numero son datos de
apoyo que consumen varios pasos.

```
BL-PORTAL-UNICO/
├── pipeline/                 Python. Extrae, clasifica, genera, comprueba
│   │
│   ├─ EXTRACCION
│   ├── p1_extract.py         limpia el HTML de WordPress y los shortcodes
│   ├── p1b_woo.py            categoria, etiquetas y atributos reales de la tienda
│   ├── p9_gsc.py             clics e impresiones via API de Search Console
│   ├── p17_keywords_zonas.py demanda por ciudad via API de KeywordTool
│   ├── p20_descubrir_zonas.py mercados con demanda y sin pagina
│   │
│   ├─ CONSTRUCCION
│   ├── p2_classify.py        a que categoria va cada ficha
│   ├── p18_renombrar_zonas.py como se llama cada pagina de zona
│   ├── p3_build.py           contenido unico, menu, relacionados, redirecciones
│   ├── p22_demanda.py        cruza la demanda medida contra las 797 URLs
│   ├── p23_seo.py            titulos, metas y nombres comerciales por demanda
│   ├── p4_export.py          indice de busqueda, esquema SQL, informe de QA
│   │
│   ├─ IMAGENES Y FICHEROS
│   ├── p6_images.py p7_download.py p8_body_images.py
│   ├── p11_ficheros.py       biblioteca de medios, conservando su ruta
│   ├── p15_fotos_faltantes.py
│   │
│   ├─ ENTREGABLES
│   ├── p10_excel.py          el Excel de 13 hojas que contesta a direccion
│   ├── p21_redirect_map.py   el CSV de redirecciones para el desarrollador
│   │
│   ├─ VERIFICACION  (ninguna es opcional)
│   ├── p5_check.py           las 803 URLs y el SEO de cada una
│   ├── p12_auditoria.py      destinos: sin caidas, sin cadenas, sin bucles
│   ├── p13_duplicados.py     contenido duplicado, origen contra destino
│   ├── p14_validar_gsc.py    toda URL de Search Console tiene destino vivo
│   ├── p16_coherencia.py     17 reglas de coherencia sobre las 6.169 URLs
│   ├── p19_excel_vs_portal.py el Excel contra el portal, fila por fila
│   │
│   └─ DATOS DE APOYO
│       ├── taxonomia.py      el arbol de destino acordado (copia de la carpeta 8)
│       ├── woo.py            resuelve atributos y etiquetas con datos de la tienda
│       ├── kb.py             23 especies y 12 marcas: Janka, densidad, vida util
│       ├── medidas.py        cobertura y peso por medida
│       ├── ciudades.py       terreno, condado y almacen de cada zona
│       └── contenido.py contenido_paginas.py
├── data/                     dataset generado, CSV del mapa, esquema SQL
├── web/                      la aplicacion Next.js
│   ├── src/app/              rutas
│   ├── src/components/       interfaz
│   ├── src/lib/              datos, SEO, Supabase
│   └── supabase-schema.sql
├── docs/
│   ├── DECISIONES.md         por que esta hecho asi
│   ├── CLASIFICACION.md      por que cada ficha acaba donde acaba
│   ├── DESPLIEGUE.md         como publicarlo
│   └── SUPABASE.md           como conectar la base de datos
├── QA-PROTOTIPO.md           informe de control de calidad, regenerado en cada build
└── README.md
```
