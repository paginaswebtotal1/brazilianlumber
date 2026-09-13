# Control de calidad del prototipo

Generado por `pipeline/p4_export.py` el 2026-09-13.

## Cifras

| Concepto | Cantidad |
|---|---|
| URLs rastreadas en los 3 portales | 2197 |
| URLs finales del portal unico | 838 |
| Categorias de producto | 50 |
| Fichas de producto | 295 |
| Articulos del blog | 229 |
| Categorias del blog | 70 |
| Paginas | 194 |
| Redirecciones 301 | 622 |
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

**1. Categorias del menu sin ningun producto (13).** Existen en el arbol acordado pero ningun producto de los 3 portales cae en ellas. O se les asigna surtido, o se sacan del menu.

- `/decking/composite/azek/` AZEK Decking
- `/decking/composite/moistureshield/` MoistureShield Decking
- `/decking/thermally-modified/ayous/` Thermo Ayous Decking
- `/decking/thermally-modified/durathermo/` Durathermo Decking
- `/cladding-siding/composite/` Composite Cladding
- `/cladding-siding/battens-louvers/` Battens and Louvers
- `/fencing-gates/` Fencing and Gates
- `/fencing-gates/wood/` Wood Fencing
- `/fencing-gates/composite/` Composite Fencing
- `/fencing-gates/gates/` Gates
- `/flooring/engineered/` Engineered Flooring
- `/accessories/tools/` Tools
- `/accessories/maintenance/` Cleaning and Maintenance

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


**4. Paginas absorbidas por la taxonomia (2).** Ocupaban la misma URL que un nodo de categoria; su contenido se fusiono dentro de la categoria.

- `/decking/` <- https://brazilianlumber.com/decking/
- `/flooring/` <- https://brazilianlumber.com/flooring/