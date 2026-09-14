# Control de calidad del prototipo

Generado por `pipeline/p4_export.py` el 2026-09-13.

## Cifras

| Concepto | Cantidad |
|---|---|
| URLs rastreadas en los 3 portales | 2197 |
| URLs finales del portal unico | 798 |
| Categorias de producto | 50 |
| Fichas de producto | 269 |
| Articulos del blog | 229 |
| Categorias del blog | 70 |
| Paginas | 180 |
| De todas ellas, indexables | 730 |
| Redirecciones 301 | 741 |
| URLs antiguas a noindex (etiquetas) | 722 |
| Fichas con contenido reescrito | 97 |

## Comprobaciones

| Comprobacion | Resultado |
|---|---|
| Rutas duplicadas | 0 |
| Redirecciones que apuntan a una URL inexistente | 0 |
| Descripciones meta vacias | 0 |
| Titulos vacios | 0 |
| Fichas sin categoria | 0 |

## Puntos que necesitan una decision de negocio

Nada de esto rompe el prototipo, pero conviene resolverlo antes de la migracion real.

**1. Categorias del menu sin ningun producto (3).** Existen en el arbol acordado pero ningun producto de los 3 portales cae en ellas. O se les asigna surtido, o se sacan del menu.

- `/decking/thermally-modified/durathermo/` Durathermo Decking
- `/fencing-gates/wood/` Wood Fencing
- `/flooring/engineered/` Engineered Flooring

**2. Paginas de prueba que sobrevivieron a la consolidacion (11).** Estan publicadas en el prototipo para no perder ninguna URL, pero marcadas noindex y fuera del menu y del sitemap. Recomendacion: eliminarlas en la migracion real.

- `/hometest/` HomeTest
- `/carousel-home/` Carousel Home
- `/thank-you-page/` Thank You Page
- `/cont-form-example/` cont form example
- `/test-form-flowsly/` test form flowsly
- `/home-test-2025/` Home - Test 2025
- `/blog-example/` blog example
- `/thank-you-review/` thank you review
- `/thank-you-ibs/` thank you IBS
- `/thank-you/` Thank you!
- `/demo-home/` Demo Home

**3. Fichas sin fotografia (0 de 269).** El prototipo las muestra con una portada generada por color de especie. Hay que subir la foto real antes de publicar.


**4. Paginas absorbidas por la taxonomia (70).** Ocupaban la misma URL que un nodo de categoria; su contenido se fusiono dentro de la categoria.

- `/product/deckwise-stainless-steel-trim-head-screws-8x1-1-2-half-inches/` <- https://brazilianlumber.com/product/deckwise-stainless-steel-trim-head-screws-8x1-inches/
- `/product/lowest-prices-deckwise-master-plug-kit/` <- https://brazilianlumber.com/product/deckwise-master-plug-kit/
- `/product/heavy-duty-cable-cutters-wisecable-accessory/` <- https://brazilianlumber.com/product/light-duty-cable-cutters-wisecable-accessory/
- `/product/armadillo-pvc-decking-2/` <- https://brazilianlumber.com/product/armadillo-pvc-decking/
- `/product/armadillo-1x6-12-grooved-lifestyle-pvc-decking/` <- https://brazilianlumber.com/product/armadillo-1x6-12-grooved-lifestyle-composite-decking-2/
- `/product/jatoba-tropical-hardwood-1x6/` <- https://brazilianlumber.com/product/jatoba-tropical-hardwood-1x6-2/
- `/product/phillip-lawn-artificial-turf/` <- https://brazilianlumber.com/product/louis-grawsy-artificial-turf/
- `/product/berkshire-moss-artificial-ivy/` <- https://brazilianlumber.com/product/birkhall-artificial-ivy/
- `/product/timbertech-pro-pvc-decking-terrain-collection/` <- https://brazilianlumber.com/product/timbertech-pro-pvc-decking-terrain-collection-1x6/
- `/product/origens-tauari-8-x-12-x-0-3/` <- https://brazilianlumber.com/product/jungle-duma-8-x-12-x-0-3/
- `/product/origens-tauari-8-x-12-x-0-3/` <- https://brazilianlumber.com/product/origens-angelim-8-x-12-x-0-3/
- `/product/origens-tauari-8-x-12-x-0-3/` <- https://brazilianlumber.com/product/origens-carvalho-8-x-12-x-0-3/
- `/product/origens-tauari-8-x-12-x-0-3/` <- https://brazilianlumber.com/product/origens-okan-8-x-12-x-0-3/
- `/product/teca-castanho-8-x-12-x-0-3/` <- https://brazilianlumber.com/product/teca-bege-8-x-12-x-0-3/
- `/product/grad-concept-start-rail-2495gc-decking-profiles/` <- https://brazilianlumber.com/product/grad-concepts-start-rail-1888gc/
- `/product/luna-arctic-triple-32x140-brushed/` <- https://brazilianlumber.com/product/luna-arctic-layer-19x188-brushed/
- `/product/luna-arctic-layer-19x142-brushed/` <- https://brazilianlumber.com/product/luna-bevel-hn-26x142/
- `/product/luna-arctic-layer-19x142-brushed/` <- https://brazilianlumber.com/product/luna-femma-26x142/
- `/product/ipe-1x4-standard/` <- https://brazilianlumberlosangeles.com/product/ipe-1x4/
- `/product/ipe-2x4-dimensional-lumber/` <- https://brazilianlumberlosangeles.com/product/ipe-2x4/
- `/product/ipe-1x12-decking/` <- https://brazilianlumberlosangeles.com/product/ipe-1x12/
- `/product/ipe-5-4x8-decking/` <- https://brazilianlumberlosangeles.com/product/ipe-5-4x8/
- `/product/ipe-5-4x12-lumber/` <- https://brazilianlumberlosangeles.com/product/ipe-5-4x12/
- `/product/garapa-tropical-hardwood-1x6-hot-deals/` <- https://brazilianlumberlosangeles.com/product/garapa-wood-1x6/
- `/product/garapa-wood-wall-panels-5-4x6/` <- https://brazilianlumberlosangeles.com/product/garapa-wood-wall-panels-5-4x6-2/
- `/product/prestige-collection-grand-grid-cladding-by-deckotech/` <- https://brazilianlumberlosangeles.com/product/prestige-collection-grand-grid-cladding-1x8-by-deckotech/
- `/` <- https://brazilianlumber.com/my-cart/
- `/` <- https://brazilianlumber.com/download-or-digital-brochure/
- `/` <- https://brazilianlumber.com/download-our-deck-preparation-checklist/
- `/locations/best-price-brazilian-lunber-los-angeles-ca/` <- https://brazilianlumbernewyork.com/best-price-brazilian-lunber-los-angeles-ca/
- `/` <- https://brazilianlumber.com/
- `/guides/` <- https://brazilianlumber.com/brazilian-lumber-blogs/
- `/decking/tropical-hardwood/garapa/` <- https://brazilianlumber.com/hot-deals/garapa/
- `/decking/tropical-hardwood/tigerwood/` <- https://brazilianlumber.com/hot-deals/tigerwood/
- `/decking/tropical-hardwood/cumaru/` <- https://brazilianlumber.com/hot-deals/cumaru/
- `/shop/` <- https://brazilianlumber.com/menu-shop/
- `/cladding-siding/wood-wall-panels/` <- https://brazilianlumber.com/wood-wall-panels/
- `/decking/thermally-modified/` <- https://brazilianlumber.com/thermally-enhanced-wood/
- `/decking/` <- https://brazilianlumber.com/decking/
- `/cladding-siding/` <- https://brazilianlumber.com/siding-and-cladding/
- `/flooring/` <- https://brazilianlumber.com/flooring/
- `/fencing-gates/` <- https://brazilianlumber.com/fences-docks/
- `/decking/deck-tiles/` <- https://brazilianlumber.com/decktiles/
- `/decking/composite/deckotech/` <- https://brazilianlumber.com/deckotech/
- `/decking/thermally-modified/` <- https://brazilianlumber.com/lunawood/
- `/accessories/tools/` <- https://brazilianlumber.com/tools/
- `/decking/composite/deckotech/` <- https://brazilianlumber.com/deckotech-2/
- `/decking/composite/trex/` <- https://brazilianlumber.com/trex-decking/
- `/decking/pvc/` <- https://brazilianlumber.com/pvc-decking/
- `/accessories/` <- https://brazilianlumber.com/decking-accessories/
- `/decking/thermally-modified/` <- https://brazilianlumber.com/thermally-modified-wood/
- `/decking/tropical-hardwood/piquia/` <- https://brazilianlumberlosangeles.com/piquia/
- `/decking/composite/` <- https://brazilianlumberlosangeles.com/composite-decking/
- `/decking/tropical-hardwood/ipe/` <- https://brazilianlumberlosangeles.com/ipe/
- `/decking/tropical-hardwood/jatoba/` <- https://brazilianlumberlosangeles.com/jatoba/
- `/decking/deck-tiles/` <- https://brazilianlumberlosangeles.com/ipe-deck-tiles/
- `/cladding-siding/` <- https://brazilianlumberlosangeles.com/cladding/
- `/decking/composite/timbertech/` <- https://brazilianlumberlosangeles.com/timbertech-composite-decking/
- `/shop/` <- https://brazilianlumberlosangeles.com/new-shop/
- `/guides/` <- https://brazilianlumberlosangeles.com/brazilian-lumber-los-angeles-blogs/
- `/guides/` <- https://brazilianlumbernewyork.com/blogs/
- `/brazilian-lumber/` <- https://brazilianlumberlosangeles.com/about-us/
- `/wholesale-prices/` <- https://brazilianlumberlosangeles.com/wholesale/
- `/ipe-decking-florida/` <- https://brazilianlumber.com/areas-we-serve/florida/
- `/texas/` <- https://brazilianlumber.com/ipe-decking-texas/
- `/thermo-woods-fl/` <- https://brazilianlumberlosangeles.com/thermo-woods-ca/
- `/garapa-landing/` <- https://brazilianlumber.com/garapa-landing-2/
- `/locations/ipe-decking-san-diego/` <- https://brazilianlumberlosangeles.com/ipe-decking-san-diego-ca/
- `/composite-brands/` <- https://brazilianlumberlosangeles.com/composite-brands-la/
- `/faq/` <- https://brazilianlumberlosangeles.com/faqs/