# -*- coding: utf-8 -*-
"""Generador de contenido para las paginas que no lo traen de WordPress.

El problema que resuelve: las categorias y los temas del blog no tienen texto
propio en el origen. Publicadas tal cual salen con 25-45 palabras, que es
contenido pobre: ni posiciona en Google ni da a un motor generativo nada que
citar.

Criterios aplicados, en este orden:

  SEO   - texto unico por URL, construido desde los atributos reales de lo que
          cuelga de esa categoria, nunca una plantilla rellenada igual dos veces.
        - encabezados que reproducen la pregunta que hace el usuario.
        - enlazado interno explicito a las ramas hermanas y al padre.

  GEO   - datos concretos y verificables (dureza Janka, densidad, medida real,
          vida util, garantia), que es lo que un modelo puede citar.
        - una tabla comparativa cuando hay varias especies o marcas: es el
          formato que mejor extraen los motores generativos.
        - preguntas y respuestas literales, que alimentan el FAQPage.

Todo dato tecnico sale de kb.py. Nada se inventa.
"""
import hashlib
from kb import ESPECIES, MARCAS


def pick(seed, opts):
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    return opts[h % len(opts)]


def unir(xs):
    xs = list(xs)
    if not xs:
        return ""
    if len(xs) == 1:
        return xs[0]
    return ", ".join(xs[:-1]) + " and " + xs[-1]


# --------------------------------------------------------------- por familia
#
# Cada rama raiz tiene su propio angulo. Un comprador de tarima pregunta por
# durabilidad y separacion entre tablas; uno de revestimiento, por ventilacion
# y fijacion oculta. Escribirles lo mismo seria la definicion de pagina pobre.

FAMILIA = {
    "decking": {
        "que_es": "Decking is the wearing surface of the deck: the boards people walk on, "
                  "and the only part of the structure exposed to sun, rain and foot traffic "
                  "every single day.",
        "elegir": [
            ("Hardness", "Janka hardness predicts how the surface survives furniture legs, "
                          "dog claws and dropped tools. Anything above 1,600 lbf holds up to "
                          "normal residential use; above 3,000 lbf is commercial territory."),
            ("Exposure", "Full southern sun and salt air are the hardest conditions there are. "
                         "Dense tropical hardwoods and capped composites handle them; softwoods "
                         "need treatment and a maintenance schedule."),
            ("Movement", "Wood moves with humidity, composite moves with temperature. That is "
                         "why gapping rules differ: a hardwood gap is set by moisture content at "
                         "install, a composite gap by the thermometer that morning."),
            ("Maintenance", "Decide before you buy whether you will oil the deck once a year. If "
                            "the answer is no, either accept a silver patina on hardwood, or "
                            "choose a capped composite that never needs it."),
        ],
        "instalacion": "Boards run perpendicular to joists spaced at 16 inches on center, or "
                       "12 inches for a diagonal layout. Every deck needs airflow underneath: a "
                       "sealed, unventilated substructure is the single most common cause of "
                       "premature failure, well ahead of the choice of board.",
        "faq": [
            ("How far apart should deck joists be?",
             "Sixteen inches on center for a standard perpendicular layout, twelve inches for a "
             "diagonal pattern or for boards thinner than 1 inch. Stair treads and cantilevers "
             "need their own blocking."),
            ("What gap should I leave between deck boards?",
             "About 3/16 of an inch for kiln dried tropical hardwood, which absorbs moisture and "
             "swells slightly after install. Composite and PVC follow the manufacturer chart, "
             "because the gap depends on the air temperature the day the boards go down."),
        ],
    },
    "lumber": {
        "que_es": "Dimensional lumber is structural and millwork stock: posts, beams, joists, "
                  "framing and the pieces that get cut, planed and joined on site.",
        "elegir": [
            ("Grade", "Grade describes knots, grain and defect allowance, not strength class. "
                      "Ask for the grade before the price: a cheaper board with more defect costs "
                      "more once you account for the waste."),
            ("Moisture", "Kiln dried stock at 12-16% is stable enough for exterior work. Green "
                         "lumber will shrink, cup and open joints after it is fastened."),
            ("Span", "Span tables depend on species, grade, spacing and load. Send us the span "
                     "and the load and we come back with the section, rather than guessing from "
                     "a nominal size."),
        ],
        "instalacion": "Sticker and cover the stack on delivery and let it acclimate to local "
                       "humidity before cutting. Lumber that is fastened down straight off the "
                       "truck will move afterwards, and it will move in the frame.",
        "faq": [
            ("What is the difference between nominal and actual size?",
             "Nominal is the rough sawn dimension before milling; actual is what you measure. A "
             "2x6 finishes at 1-1/2 by 5-1/2 inches, a 5/4x6 at 1 by 5-1/2 inches."),
            ("Do you cut to length?",
             "Yes. We mill to order in house, which cuts jobsite waste and freight cost on long "
             "runs. Send the cut list with the quote request."),
        ],
    },
    "cladding-siding": {
        "que_es": "Cladding is the exterior skin of the building: a rain screen that takes the "
                  "weather so the wall behind it stays dry.",
        "elegir": [
            ("Profile", "Shiplap and tongue and groove shed water by geometry; open joint "
                        "profiles rely on the membrane behind them. Choose the profile before "
                        "the species, because it decides the whole detail."),
            ("Ventilation", "A cladding system needs a drained and ventilated cavity behind it. "
                            "Boards fixed flat to sheathing will trap moisture and fail early, "
                            "whatever the material."),
            ("Fixing", "Face fixing is faster and cheaper; concealed fixing is what makes a "
                       "facade look designed. Decide early, because it changes the profile."),
            ("Orientation", "Vertical boards drain faster, horizontal boards read wider. Both "
                            "work, but the flashing detail is different."),
        ],
        "instalacion": "Fix over battens to create a ventilated cavity of at least 3/4 of an "
                       "inch, with insect mesh top and bottom. Seal every cut end the same day, "
                       "and keep fasteners stainless: a corroding fastener stains the facade "
                       "long before it fails.",
        "faq": [
            ("Does wood cladding need a ventilated cavity?",
             "Yes. A drained and back-ventilated cavity of at least 3/4 of an inch is what lets "
             "the board dry from both faces. Without it the board cups and the coating fails."),
            ("Can I use decking boards as cladding?",
             "Sometimes, but not automatically. Cladding profiles are thinner and lighter, and "
             "they are milled to shed water in a vertical plane. Ask before you substitute."),
        ],
    },
    "fencing-gates": {
        "que_es": "Fencing and gates are the boundary: the part of the property people see from "
                  "the street and touch every day on their way in.",
        "elegir": [
            ("Privacy", "A board on board or horizontal slat fence gives full privacy; a spaced "
                        "picket gives airflow and keeps the yard from feeling closed in. Decide "
                        "the gap before the species."),
            ("Posts", "The fence fails at the post, never in the middle of a panel. Set posts in "
                      "concrete below the frost line, and use a rot resistant species or a metal "
                      "post sleeve."),
            ("Gate", "A gate is a moving structure, not a panel with hinges. It needs a braced "
                     "frame, heavy hardware and a diagonal that runs from the bottom hinge "
                     "upward, or it will drop within a season."),
            ("Height", "Check the local code before ordering. Front yard limits are usually "
                       "lower than rear, and a gate over six feet often needs a permit."),
        ],
        "instalacion": "Set posts first and let the concrete cure before hanging anything. Keep "
                       "the bottom rail at least two inches clear of grade so the fence is not "
                       "wicking water out of the soil.",
        "faq": [
            ("What is the best wood for a fence?",
             "For rot resistance without chemical treatment, Ipe and Cumaru outlast everything "
             "else, at a price. Western Red Cedar is the traditional choice: light, stable and "
             "naturally resistant, at around 350 lbf Janka."),
            ("How deep should fence posts go?",
             "A third of the total post length, or below the local frost line, whichever is "
             "deeper. A six foot fence usually means an eight foot post."),
        ],
    },
    "flooring": {
        "que_es": "Flooring is the interior surface: the one specified for how it looks, and "
                  "judged on how it wears.",
        "elegir": [
            ("Hardness", "Janka matters more indoors than outdoors, because dents show under "
                         "interior light. Above 1,300 lbf handles a family home; below that, "
                         "expect character."),
            ("Solid or engineered", "Solid boards can be sanded many times and suit a stable, "
                                    "dry interior. Engineered boards handle humidity swings and "
                                    "underfloor heating far better, and go over concrete."),
            ("Finish", "Site finished floors give a seamless surface and let you match a color "
                       "exactly. Prefinished floors go down faster and carry a wear warranty."),
        ],
        "instalacion": "Acclimate the flooring inside the finished, conditioned space for at "
                       "least 72 hours before installation, and check the subfloor moisture. "
                       "Almost every flooring complaint traces back to one of those two steps "
                       "being skipped.",
        "faq": [
            ("Solid or engineered hardwood?",
             "Engineered, if the floor sits over concrete, over underfloor heating, or in a "
             "humid climate. Solid, if you want a floor that can be sanded back several times "
             "over its life."),
            ("Can hardwood flooring go over concrete?",
             "Engineered can, with the right moisture barrier. Solid hardwood generally cannot "
             "be fastened directly to a slab."),
        ],
    },
    "slabs": {
        "que_es": "Live edge slabs are single pieces of tree, kept full width with the natural "
                  "edge intact: tables, counters, bar tops and reception desks.",
        "elegir": [
            ("Drying", "A slab must be kiln dried to interior moisture content before it is "
                       "worked. An air dried slab looks identical and will split after it is "
                       "finished."),
            ("Movement", "A wide slab moves across the grain with the seasons. The base has to "
                         "let it: slotted fixings, never a rigid frame."),
            ("Thickness", "Two inches for a dining table, three or more for a bar top or a piece "
                          "that spans without a center support."),
        ],
        "instalacion": "Fix the base with slotted or figure eight fasteners so the slab can move "
                       "across its width. A slab bolted rigidly to a steel frame will crack, and "
                       "it will crack straight down the middle.",
        "faq": [
            ("Are your slabs kiln dried?",
             "Yes, to interior moisture content. That is the difference between a table that "
             "stays flat and one that opens up after the first heating season."),
            ("How thick should a table slab be?",
             "Two inches finished for a dining table, three inches or more for a bar top or an "
             "unsupported span."),
        ],
    },
    "landscaping": {
        "que_es": "Landscaping products finish the space around the structure: ground cover and "
                  "green screening that stay green without irrigation or trimming.",
        "elegir": [
            ("Drainage", "Artificial turf needs a compacted, permeable base. Laid over soil or "
                         "over an impermeable slab it will hold water and smell."),
            ("Pile and density", "Pile height reads as realism, stitch density decides how long "
                                 "it stays upright. Density is the number that matters."),
            ("UV", "Anything outdoors in the southern United States needs a UV stabilized "
                   "product, or it fades within two seasons."),
        ],
        "instalacion": "Compact the base, lay a weed membrane, and secure the perimeter. On "
                       "green screening, fix the panels to a rigid frame rather than direct to "
                       "the fence, so the panels can be replaced individually.",
        "faq": [
            ("Does artificial turf get hot?",
             "In direct sun it runs hotter than natural grass. A lighter color and an infill "
             "designed for heat reduction both help."),
            ("How long does artificial ivy last outdoors?",
             "A UV stabilized panel holds its color for several seasons. Untreated panels fade "
             "within two summers in Florida or Southern California sun."),
        ],
    },
    "accessories": {
        "que_es": "Accessories are the parts that decide whether the deck lasts: fasteners, "
                  "substructure, finishes and the tools to install them correctly.",
        "elegir": [
            ("Stainless only", "On tropical hardwood, use stainless steel. The tannins in dense "
                               "hardwood corrode coated and galvanized fasteners, and the "
                               "corrosion stains the board around every screw."),
            ("Hidden or face fixed", "Hidden fasteners give a clean surface and let boards be "
                                     "lifted later. Face fixing is faster, cheaper and, "
                                     "counterbored and plugged, perfectly respectable."),
            ("End grain", "End grain sealer on every cut, the same day it is cut. It is the "
                          "cheapest item on the order and the one that prevents the most visible "
                          "defect, which is end checking."),
            ("Substructure", "The boards will outlast the frame under them unless the frame is "
                             "specified to match. An aluminum system removes that problem "
                             "entirely."),
        ],
        "instalacion": "Pre-drill and counterbore in dense hardwood: a screw driven straight in "
                       "will snap or split the board. Carbide tooling is not optional either, "
                       "because these species dull standard steel blades within a few cuts.",
        "faq": [
            ("What fasteners should I use on Ipe?",
             "Stainless steel, always, and always pre-drilled. Coated and galvanized screws "
             "corrode against the tannins in dense tropical hardwood and stain the board."),
            ("Do I have to seal the ends of the boards?",
             "Yes, every cut, the same day. End grain absorbs moisture far faster than the face, "
             "and unsealed ends check and split within the first season."),
        ],
    },
}


def tabla_especies(especies):
    """Tabla comparativa. Es el formato que mejor extraen los motores generativos."""
    filas = []
    for k in especies:
        e = ESPECIES.get(k)
        if e:
            filas.append((e[0], "{:,} lbf".format(e[1]), "{} kg/m3".format(e[2]), e[4]))
    return filas


def gen_categoria(ruta, titulo, hijos, prods, padre_titulo=None):
    """Contenido completo de una pagina de categoria."""
    raiz = ruta.split("/")[0]
    fam = FAMILIA.get(raiz, FAMILIA["accessories"])
    key = ruta.rsplit("/", 1)[-1]
    esp = ESPECIES.get(key)
    mrc = MARCAS.get(key)

    especies = sorted({p["attr"]["especie"] for p in prods
                       if (p.get("attr") or {}).get("especie") in ESPECIES})
    marcas = sorted({p["attr"]["marca"] for p in prods
                     if (p.get("attr") or {}).get("marca") in MARCAS})
    medidas = sorted({p["attr"]["medida"] for p in prods
                      if (p.get("attr") or {}).get("medida")})
    n = len(prods)

    bl, faq = [], []

    # ---------------------------------------------------------- entrada
    if esp:
        bl.append({"t": "p", "text":
            "{} covers every {} profile we stock. The wood is {}, it rates {:,} lbf on the "
            "Janka hardness scale, and it delivers {} outdoors with no chemical treatment. "
            "{}.".format(titulo, esp[0], esp[3], esp[1], esp[4], esp[5][0].upper() + esp[5][1:])})
    elif mrc:
        bl.append({"t": "p", "text":
            "{} brings together the {} range we carry, built as {} and backed by a {}. "
            "{}.".format(titulo, mrc[0], mrc[1], mrc[2], mrc[3][0].upper() + mrc[3][1:])})
    else:
        bl.append({"t": "p", "text": "{} {}".format(titulo + ".", fam["que_es"])})

    # ---------------------------------------------------------- inventario real
    if n:
        partes = []
        if medidas:
            partes.append("{} milled size{} ({})".format(
                len(medidas), "s" if len(medidas) != 1 else "",
                unir(m.replace("x", " x ") for m in medidas[:8])))
        if especies and not esp:
            partes.append("{} species ({})".format(
                len(especies), unir(ESPECIES[e][0] for e in especies[:6])))
        if marcas and not mrc:
            partes.append("{} brand{} ({})".format(
                len(marcas), "s" if len(marcas) != 1 else "",
                unir(MARCAS[m][0] for m in marcas[:6])))
        linea = "We stock {} product{} in this category".format(n, "s" if n != 1 else "")
        if partes:
            linea += ", covering " + unir(partes)
        bl.append({"t": "p", "text": linea + ". Everything ships from our own yards in Miami, "
                                             "Los Angeles and New Jersey, cut to length on request."})
    else:
        # Categoria sin surtido todavia: la pagina tiene que sostenerse sola.
        bl.append({"t": "p", "text":
            "We are building out this range. In the meantime the sales desk sources it to "
            "order, and the guidance below is what we tell customers who ask. Send us the "
            "specification and we come back with options, pricing and lead time."})

    # Lo que de verdad distingue a una categoria de su hermana es lo que hay
    # dentro. Sin esto, /landscaping/artificial-turf/ y /landscaping/artificial-ivy/
    # salian con un 99,9% de similitud: misma familia, mismo texto.
    if prods:
        nombres = [p["titulo"] for p in sorted(prods, key=lambda x: -(x.get("clics") or 0))[:6]]
        bl.append({"t": "p", "text":
            "What sits in this category right now: {}. Stock moves, so ask the sales desk to "
            "confirm before you specify.".format(unir(n[:60] for n in nombres))})

    # ---------------------------------------------------------- como elegir
    bl.append({"t": "h2", "text": pick(ruta + "e", [
        "How to choose",
        "What to look at before you order",
        "Choosing the right one",
    ])})
    # Tres criterios de los cuatro, rotando por ruta: las categorias hermanas
    # comparten familia, y con la lista completa salian casi identicas.
    _h = int(hashlib.md5(ruta.encode()).hexdigest(), 16)
    _sel = [fam["elegir"][(_h + i) % len(fam["elegir"])] for i in range(3)]
    bl.append({"t": "list", "items": ["{}. {}".format(t, d) for t, d in _sel]})

    # ---------------------------------------------------------- tabla comparativa
    if len(especies) > 1:
        bl.append({"t": "h2", "text": "The species side by side"})
        bl.append({"t": "table",
                   "head": ["Species", "Janka hardness", "Density", "Service life"],
                   "rows": tabla_especies(especies)})
        mas_dura = max(especies, key=lambda k: ESPECIES[k][1])
        bl.append({"t": "p", "text":
            "{} is the hardest of the group at {:,} lbf, which is what you want where the "
            "surface takes a beating. The softer species are easier to work and easier on the "
            "budget.".format(ESPECIES[mas_dura][0], ESPECIES[mas_dura][1])})
    elif esp:
        bl.append({"t": "h2", "text": "{} specifications".format(esp[0])})
        bl.append({"t": "table",
                   "head": ["Property", "Value"],
                   "rows": [("Janka hardness", "{:,} lbf".format(esp[1])),
                            ("Average dry density", "{} kg/m3".format(esp[2])),
                            ("Color", esp[3]),
                            ("Service life untreated", esp[4]),
                            ("Moisture content", "Kiln dried to 12-16%"),
                            ("Fasteners", "Stainless steel, pre-drilled")]})

    if len(marcas) > 1:
        bl.append({"t": "h2", "text": "The brands we carry here"})
        bl.append({"t": "list", "items": [
            "{}: {}, {}. Warranty: {}.".format(MARCAS[m][0], MARCAS[m][1], MARCAS[m][3], MARCAS[m][2])
            for m in marcas]})

    # ---------------------------------------------------------- instalacion
    bl.append({"t": "h2", "text": "Installation"})
    bl.append({"t": "p", "text": fam["instalacion"]})
    if esp and esp[1] >= 1600:
        bl.append({"t": "p", "text":
            "At {:,} lbf, {} has to be pre-drilled and counterbored before fastening, fixed with "
            "stainless steel only, and sealed on every cut end the same day it is cut.".format(
                esp[1], esp[0])})

    # ---------------------------------------------------------- subcategorias
    if hijos:
        bl.append({"t": "h2", "text": "Browse {}".format(titulo.lower())})
        bl.append({"t": "list", "items": [h[1] for h in hijos]})

    # ---------------------------------------------------------- preguntas
    faq = list(fam["faq"])
    if esp:
        faq.insert(0, ("How long does {} last outdoors?".format(esp[0]),
                       "{} in a ventilated installation, with no chemical treatment. The "
                       "limiting factor is almost never the board, it is the substructure "
                       "underneath it.".format(esp[4].capitalize())))
        faq.insert(1, ("Does {} need to be sealed?".format(esp[0]),
                       "Only the cut ends, and only to stop end checking. Surface oil is a "
                       "cosmetic choice: it holds the {} tone instead of letting the board "
                       "weather to silver.".format(esp[3].split(" with ")[0])))
    if mrc:
        faq.insert(0, ("What warranty comes with {}?".format(mrc[0]),
                       "A {}. Registration is handled by the manufacturer and we supply the "
                       "proof of purchase.".format(mrc[2])))
    if medidas:
        faq.append(("What sizes do you stock?",
                    "Currently {}. We also mill to order, so ask if the size you need is not "
                    "listed.".format(unir(m.replace("x", " x ") for m in medidas[:8]))))
    faq.append(("Do you deliver outside Florida, California and New Jersey?",
                "Yes. The three yards cover the country by freight, and the order ships from "
                "whichever one is closest to the jobsite."))

    faq = faq[:5]
    bl.append({"t": "h2", "text": "Frequently asked questions"})
    for q, a in faq:
        bl.append({"t": "h3", "text": q})
        bl.append({"t": "p", "text": a})

    return bl, [{"q": q, "a": a} for q, a in faq]


def gen_postcat(titulo, posts, categoria=None):
    """Pagina de tema del blog.

    Un listado de titulos con una linea de introduccion es contenido pobre y
    canibaliza a los propios articulos. Aqui la pagina explica que cubre el tema,
    que preguntas responde y adonde ir a comprar, que es lo que la hace util
    tanto para el lector como para un motor que quiera citarla.
    """
    n = len(posts)
    t = titulo.lower()
    recientes = sorted(posts, key=lambda p: p.get("date") or "", reverse=True)
    bl = []

    bl.append({"t": "p", "text":
        "Everything we have published on {}. {} article{} written by the Brazilian Lumber team "
        "from what we see in the yard and on jobsites, not from a manufacturer brochure."
        .format(t, n, "s" if n != 1 else "")})

    bl.append({"t": "p", "text": pick(titulo, [
        "These are the questions customers actually ask at the counter about {}, answered with "
        "the numbers behind them: hardness, density, spans, gaps and service life.".format(t),
        "The guides below cover {} from specification through to maintenance, with the same "
        "figures we use ourselves when we quote a job.".format(t),
        "Written for whoever is doing the specifying: what {} is, where it works, where it does "
        "not, and what it costs in maintenance once it is installed.".format(t),
    ])})

    if recientes:
        bl.append({"t": "h2", "text": "What these guides answer"})
        bl.append({"t": "list", "items": [p["title"] for p in recientes[:6]]})

    bl.append({"t": "h2", "text": pick(titulo + "b", [
        "Before you specify", "What we tell customers first", "Worth knowing up front"])})
    _consejos = [
        "Ask for samples. Screen color is not wood color, and grain reads completely "
        "differently at full size.",
        "Check the substructure before the surface. The boards almost always outlast the frame "
        "underneath them unless the frame was specified to match.",
        "Use stainless steel fasteners on dense hardwood, pre-drilled. Coated screws corrode "
        "against the tannins and stain the board around every fixing.",
        "Seal every cut end the same day it is cut. It is the cheapest item on the order and it "
        "prevents the most visible defect there is.",
        "Check the local code before you order. Rail heights, fence heights and stair geometry "
        "are decided by the inspector, not by the catalog.",
        "Order the substructure at the same time. The frame under the boards is what usually "
        "fails first, and it is the part nobody budgets for.",
    ]
    # Tres consejos de seis, elegidos por tema: dos paginas distintas no salen
    # con la misma lista.
    h = int(hashlib.md5(titulo.encode()).hexdigest(), 16)
    bl.append({"t": "list", "items": [_consejos[(h + i * 2) % len(_consejos)] for i in range(3)]})

    bl.append({"t": "h2", "text": pick(titulo + "w", [
        "Where to buy", "Getting it from us", "Ordering"])})
    bl.append({"t": "p", "text": pick(titulo + "x", [
        "Everything discussed in these guides is stocked in Miami, Los Angeles and New Jersey, "
        "milled to order and shipped anywhere in the continental United States.",
        "We hold this material in three yards and mill it to order, so the cut list goes out with "
        "the quote rather than being solved on site.",
        "Send the specification and the sales desk comes back with pricing, lead time and "
        "freight, usually the same day, from whichever yard is closest to the job.",
    ])})
    return bl
