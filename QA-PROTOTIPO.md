# Control de calidad del prototipo

Generado por `pipeline/p4_export.py` el 2026-09-13.

## Cifras

| Concepto | Cantidad |
|---|---|
| URLs rastreadas en los 3 portales | 2197 |
| URLs finales del portal unico | 813 |
| Categorias de producto | 50 |
| Fichas de producto | 295 |
| Articulos del blog | 229 |
| Categorias del blog | 70 |
| Paginas | 166 |
| Redirecciones 301 | 650 |
| URLs antiguas a noindex (etiquetas) | 722 |
| Fichas con contenido reescrito | 109 |

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
- `/` Home - Test 2025
- `/blog-example/` blog example
- `/thank-you-review/` thank you review
- `/thank-you-ibs/` thank you IBS
- `/thank-you/` Thank you!
- `/demo-home/` Demo Home

**3. Fichas sin fotografia (27 de 295).** El prototipo las muestra con una portada generada por color de especie. Hay que subir la foto real antes de publicar.


**4. Paginas absorbidas por la taxonomia (30).** Ocupaban la misma URL que un nodo de categoria; su contenido se fusiono dentro de la categoria.

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