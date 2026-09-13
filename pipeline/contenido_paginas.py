# -*- coding: utf-8 -*-
"""Contenido para las paginas sueltas que llegaron vacias o casi vacias.

No se rellenan con paja. A cada pagina se le da el contenido que esa pagina
tiene que tener para ser util, escrito con los datos reales del negocio. Si una
pagina no tiene razon de existir porque duplica una categoria, no se rellena:
se consolida (ver CONSOLIDAR en p3_build.py).
"""
from contenido import unir

YARDS = ("Miami, Florida", "Los Angeles, California", "Newark, New Jersey")

# slug -> lista de bloques (tipo, valor)
PAGINA = {
    "calculator": [
        ("p", "Work out how much decking you need before you ask for a price. The number that "
              "matters is coverage, not board count, because board width and gap change the "
              "answer more than anything else."),
        ("h2", "How to calculate decking"),
        ("list", [
            "Measure the deck area in square feet: length times width, plus any bump-outs.",
            "Add 10% for a straight, perpendicular layout. Add 15% for a diagonal layout, and "
            "20% for herringbone or a picture frame border.",
            "Divide by the coverage of the board you chose. A 5/4x6 covers about 0.48 square "
            "feet per linear foot once you allow a 3/16 inch gap; a 1x4 covers about 0.31.",
            "Order the substructure separately: joists at 16 inches on center, plus blocking at "
            "every board joint.",
        ]),
        ("h2", "Or send us the measurements"),
        ("p", "Give us the deck dimensions, the board you want and the layout, and we come back "
              "with the exact linear footage, the cut list and the freight. We mill to order, so "
              "a good cut list removes most of the waste from the job."),
    ],
    "request-a-quote": [
        ("p", "Quotes go out from the sales desk, usually the same day. The more of this we have "
              "up front, the faster and the more accurate the number comes back."),
        ("h2", "What to include"),
        ("list", [
            "The material and profile, or the application if you have not chosen yet.",
            "Quantities in linear or square feet, and the lengths you can accept on site.",
            "The delivery address, so we quote from the closest of the three yards.",
            "The date you need it, which decides whether it ships from stock or from the mill.",
        ]),
        ("h2", "What comes back"),
        ("p", "Unit pricing, total material, lead time and freight, itemised. If a substitution "
              "would save you money without changing the result, we say so in the same email."),
    ],
    "request-samples": [
        ("p", "Nobody should specify a hardwood from a photograph. Screen color is not wood "
              "color, and grain reads completely differently at full size."),
        ("h2", "How it works"),
        ("list", [
            "Tell us which species or brands you are comparing.",
            "Samples ship as short offcuts of the real profile, not printed chips.",
            "Tropical hardwood samples arrive unfinished. Wet one half with mineral spirits to "
            "see the color it holds if you oil it, and leave the other half to weather.",
        ]),
    ],
    "contact": [
        ("p", "Three yards, one sales desk. Whoever picks up can quote, check stock and book "
              "freight from any of the three locations."),
        ("h2", "Where we are"),
        ("list", ["{} yard".format(y) for y in YARDS]),
        ("h2", "What we can answer on the phone"),
        ("list", [
            "Stock and lead time on any item in the catalog.",
            "Freight cost to a jobsite anywhere in the continental United States.",
            "Whether a substitution makes sense for your application and your budget.",
            "Span, gapping and fastener questions, before you order rather than after.",
        ]),
    ],
    "sustainability": [
        ("p", "Tropical hardwood is only defensible if it is legally harvested and properly "
              "documented. Ours is, and the paperwork travels with the order."),
        ("h2", "How the supply chain works"),
        ("list", [
            "Every shipment of South American hardwood carries its chain of custody "
            "documentation from the country of origin.",
            "All imports comply with the Lacey Act, which makes it a federal offense in the "
            "United States to trade illegally harvested timber.",
            "The species we carry are managed commercial species, not the rare timbers that "
            "belong in a museum.",
        ]),
        ("h2", "The part people forget"),
        ("p", "A deck that lasts fifty years without chemical treatment has a smaller footprint "
              "than one rebuilt three times over the same period. Durability is a "
              "sustainability argument, not just a sales one."),
    ],
    "wholesale": [
        ("p", "Contractor and trade pricing, on account, with the volumes and the lead times "
              "that a build schedule actually needs."),
        ("h2", "What trade accounts get"),
        ("list", [
            "Tiered pricing by volume, quoted per project rather than per order.",
            "Container and truckload quantities direct from the mill.",
            "Reserved stock against a build schedule, so material is there when the crew is.",
            "Cut-to-length milling in house, which takes waste out of the labor line.",
        ]),
    ],
    "wholesale-prices": [
        ("p", "Trade pricing is quoted per project, not published per item, because volume, "
              "lengths and delivery schedule move the number more than the list price does."),
        ("h2", "What changes the price"),
        ("list", [
            "Volume, and whether it ships as one delivery or several.",
            "Lengths: a mixed-length order costs less than an all-16-foot order of the same "
            "footage.",
            "Grade, on tropical hardwood especially. Grade B is sound and structural with more "
            "color variation, at a real saving.",
            "Distance from the nearest of the three yards.",
        ]),
    ],
    "in-house-custom-milling": [
        ("p", "We run our own mill, which is why we can quote a profile that is not in the "
              "catalog and why a cut list costs you less than buying long and cutting on site."),
        ("h2", "What we mill"),
        ("list", [
            "Cut to length, so the waste stays in our yard instead of your dumpster.",
            "Custom profiles: grooved for hidden fasteners, rain screen, shiplap, tongue and "
            "groove, bullnose and custom radius.",
            "Resawing and surfacing of rough stock to a finished dimension.",
            "Pre-grooving on species and sizes that do not come grooved from the supplier.",
        ]),
    ],
    "estimate-take-off-design-services": [
        ("p", "Send drawings and we return a material take-off: quantities, lengths, "
              "substructure and fasteners, itemised and priced."),
        ("h2", "What we need"),
        ("list", [
            "A plan with dimensions, in any format that opens.",
            "The board and the layout, or a description of what the deck has to do.",
            "The site address and the target date.",
        ]),
        ("h2", "Why it is worth doing"),
        ("p", "Most overordering happens at the take-off stage, not in the yard. Getting lengths "
              "right against the joist layout routinely saves more than the design time costs."),
    ],
    "hot-deals": [
        ("p", "Short-run stock, overs from finished jobs and remainders of discontinued "
              "profiles, at a discount. Quantities are what they are, and when they are gone "
              "they do not come back."),
        ("h2", "What usually shows up here"),
        ("list", [
            "Odd lengths left over from a milled order.",
            "Discontinued colors from composite manufacturers.",
            "Grade B tropical hardwood: sound and structural, with more color variation.",
        ]),
    ],
    "sale-items": [
        ("p", "Current reductions across the catalog: stock lines, discounted while the quantity "
              "lasts."),
        ("h2", "Before you order"),
        ("list", [
            "Sale quantities are not reserved until the order is placed.",
            "Ask about lengths. A discount on a length that does not suit your joist layout is "
            "not a discount.",
            "Freight is quoted the same way as on any other order.",
        ]),
    ],
    "projects": [
        ("p", "Decks, facades, fences and interiors built with material from our yards, across "
              "residential, hospitality and commercial work."),
        ("h2", "What these have in common"),
        ("list", [
            "A substructure specified to outlast the boards, not the other way round.",
            "Stainless fasteners throughout, pre-drilled on dense hardwood.",
            "End grain sealed on every cut, the same day it was cut.",
        ]),
    ],
    "submit-a-photo": [
        ("p", "Built something with material from one of our yards? Send us the photographs. We "
              "credit the builder and, with permission, the project goes into the gallery."),
        ("h2", "What works best"),
        ("list", [
            "Daylight, and the whole deck or facade rather than a detail.",
            "One shot straight after installation and one a year later: the weathering is the "
            "part people want to see.",
            "The species, the profile and the year it was installed.",
        ]),
    ],
    "media-faq": [
        ("p", "For press and media enquiries: background on the company, the species we carry "
              "and the supply chain behind them."),
        ("h2", "The basics"),
        ("list", [
            "Three yards: {}.".format(", ".join(YARDS)),
            "Tropical hardwood, composite and PVC decking, cladding, fencing, flooring and "
            "dimensional lumber.",
            "All imported timber complies with the Lacey Act, with chain of custody "
            "documentation from the country of origin.",
        ]),
    ],
    "download-our-brochure": [
        ("p", "The full catalog as a PDF: species, profiles, sizes and the technical data behind "
              "each one, in the format that survives a jobsite."),
        ("h2", "What is in it"),
        ("list", [
            "Every species we stock, with Janka hardness, density and expected service life.",
            "Milled sizes and profiles, nominal and actual.",
            "Installation basics: joist spacing, gapping, fasteners and end sealing.",
        ]),
    ],
    "free-shipping-terms": [
        ("p", "Freight terms for orders that qualify for free shipping."),
        ("h2", "How it works"),
        ("list", [
            "Applies to the continental United States only.",
            "Calculated per order, not per item, and quoted before the order is confirmed.",
            "Oversized and overlength material is quoted separately, because it ships on a "
            "different truck.",
        ]),
    ],
}

# Bloques de cierre por tipo de pagina, cuando no hay contenido a medida.
# No es relleno: es la informacion que un comprador necesita igualmente y que,
# ademas, es lo que un motor generativo puede citar sobre el proveedor.
COMUN = [
    ("h2", "How ordering works"),
    ("list", [
        "Send the specification, the quantities and the delivery address. If you have drawings, "
        "send those instead and we do the take-off.",
        "You get unit pricing, total material, lead time and freight in one email, itemised.",
        "The order ships from whichever of the three yards is closest to the jobsite.",
        "We mill to order in house, so a cut list costs you less than buying long and cutting "
        "on site.",
    ]),
    ("h2", "Common questions"),
    ("h3", "Do you sell to the public, or only to trade?"),
    ("p", "Both. Trade accounts get tiered pricing by volume and reserved stock against a build "
          "schedule, but anyone can order."),
    ("h3", "How fast can it ship?"),
    ("p", "Stock items usually leave within a day or two. Milled-to-order profiles depend on the "
          "queue, and we tell you the date before you commit, not after."),
    ("h3", "Can I see the material before I buy?"),
    ("p", "Yes. Samples ship as short offcuts of the real profile, not printed color chips. On "
          "tropical hardwood, wet half the sample with mineral spirits to see the tone it holds "
          "if you oil it."),
]

GENERICA = {
    "landing": [
        ("h2", "How we work"),
        ("list", [
            "Three yards: {}, with nationwide freight.".format(", ".join(YARDS)),
            "Milled to order in house, so you pay for the wood you use.",
            "Technical answers before the order, not after: spans, gapping, fasteners and "
            "finishes.",
        ]),
    ] + COMUN,
    "company": [
        ("h2", "About Brazilian Lumber"),
        ("p", "We supply tropical hardwood, composite and PVC decking, cladding, fencing, "
              "flooring and dimensional lumber from three yards in the United States: {}."
              .format(", ".join(YARDS))),
        ("list", [
            "Our own mill, so custom profiles and cut lists are routine rather than an "
            "exception.",
            "Freight to any jobsite in the continental United States, from whichever yard is "
            "closest.",
            "Chain of custody documentation on every shipment of imported hardwood.",
        ]),
    ] + COMUN,
}


def _bloques(specs):
    out = []
    for tipo, val in specs:
        out.append({"t": "list", "items": val} if tipo == "list" else {"t": tipo, "text": val})
    return out


def gen_pagina(slug, sub, originales):
    """Devuelve los bloques finales de una pagina suelta."""
    if slug in PAGINA:
        # El contenido a medida va primero; el bloque comun cierra la pagina con
        # lo que cualquier comprador necesita saber igualmente.
        return _bloques(PAGINA[slug]) + _bloques(GENERICA.get(sub, GENERICA["company"])[-9:])
    base = GENERICA.get(sub, GENERICA["company"])
    return list(originales) + _bloques(base)


def gen_ubicacion(ciudad, especies_top):
    """Pagina de ciudad. Lo que aporta es cercania y logistica, no palabreria."""
    return [
        {"t": "p", "text":
            "We deliver to {} from the closest of our three yards, with the full catalog "
            "available: tropical hardwood and composite decking, cladding, fencing, flooring "
            "and dimensional lumber.".format(ciudad)},
        {"t": "h2", "text": "Delivering to {}".format(ciudad)},
        {"t": "list", "items": [
            "Orders ship from {}, whichever is nearest to the jobsite.".format(unir(YARDS)),
            "Cut to length in our own mill before it ships, so you are not paying freight on "
            "offcuts.",
            "Lead time and freight are quoted together with the material, never added later.",
        ]},
        {"t": "h2", "text": "What gets specified here"},
        {"t": "p", "text":
            "The most requested materials in this area are {}. If you are comparing options, "
            "ask for samples before you commit: screen color is not wood color.".format(
                unir(especies_top) if especies_top else
                "Ipe, Cumaru and capped composite decking")},
    ]
