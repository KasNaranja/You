# -*- coding: utf-8 -*-
"""Las escenas del cuerpo del vídeo 5, una por imagen.

Cada entrada:
    id      la marca del guion donde arranca (y la imagen se llama así)
    cubre   todas las líneas del guion que suenan sobre esta imagen
    dur     duración real en segundos, medida de audio/cuerpo/tramos.json
    efecto  "in" | "out" | "fijo"  (ver la gramática en biblia-visual.md)
    escena  qué se ve, componiendo SIEMPRE las frases literales de la biblia

El prompt final = MUNDO + cámara + escena. Ejecutar este fichero escribe
plan.json para herramientas/generar-imagenes.ps1.
"""

MUNDO = ("Colorful digital illustration with pixel art influence, crisp clean pixel "
         "rendering. Flat overcast grey sky, diffuse daylight, no sun, no harsh cast "
         "shadows. Strictly muted desaturated palette: concrete grey, cool steel blue, "
         "brass and gold accents, dark green, warm beige stone. No teal, no bright cyan, "
         "no neon glow. Figures are small and anonymous, no facial detail. Serious "
         "documentary mood, no whimsy, no cartoon exaggeration. ")

FRONTAL = "Straight-on frontal elevation, camera at street level, symmetrical composition, no perspective distortion. "
ISO = "High isometric three-quarter view looking down at about 40 degrees, clean orthogonal grid. "
CENTRADO = "Centered medium shot at eye level, the subject fills most of the frame. "

# --- Elementos congelados (el gancho ya los enseñó; ni una palabra se cambia) ---
CALLE = ("a grey concrete corner block, its ground floor a small bank branch with a "
         "plain dark sign and one wall-mounted cash machine, apartments with iron "
         "balconies and potted plants above, a green-awning grocery next door, "
         "pedestrians and a cyclist on the pavement, parked cars at the kerb")
BANCO = ("a massive grey stone neoclassical building with four fluted columns, three "
         "tall dark green bronze doors, a wide stone staircase, a round brass emblem "
         "above the central door, two ornate black street lamps flanking the steps, and "
         "the words BANCO CENTRAL in gold capital letters carved across the frieze")
MASTILES = ("five tall brass flagpoles in a row on a stone plaza, flying the flags of "
            "the United States, the United Kingdom, Japan and the European Union, in "
            "front of a wide modern government building whose facade carries a large "
            "dark line chart climbing steadily from bottom left to top right")
CAMARA = ("a huge round brass and steel bank vault door standing open, its spoked "
          "wheel turning outwards, revealing stacked bundles of banknotes inside")
MINIS = ("a white classical government building with a columned portico, a sculpted "
         "pediment and gold-framed doors")
DATOS = ("a modern glass-walled data centre with a flat dark roof, rows of black "
         "server racks visible through the glass, small green indicator lights inside")
COLA_E = "a queue of figures in long grey coats, each carrying a stack of pale document boxes"
COLA_I = "a queue of figures in dark blue work overalls, each carrying a black server rack unit under one arm"

# --- Elementos nuevos (congelados desde aquí) ---
PARQUE = ("a large open trading hall seen in high isometric view, rows of dark wooden "
          "desks with small dark monitors, small anonymous figures at them, and on the "
          "far wall one huge dark display board showing a single dark line chart")
SALA = ("a grand interior room with tall windows, a long dark wooden table with "
        "anonymous figures seated around it, and the round brass emblem of the central "
        "bank mounted on the stone wall behind")
CAMINO = ("a long straight empty road receding to the horizon across a flat plain, "
          "with evenly spaced small stone milestones along its edge")
FABRICA = "a red brick factory with a single tall chimney and a sawtooth roof"
OBRAS = "wrapped in wooden scaffolding, with a small crane beside it"
PISO = ("a beige apartment building with iron balconies, and a large white sign with "
        "the words SE VENDE in dark capital letters by its entrance")
IMPRENTA = ("a heavy dark green industrial printing press with brass fittings, feeding "
            "out a long sheet of pale banknotes onto a roller table")
RUEDA = ("a large iron wheel mounted on a dark machine frame, with a leather belt "
         "running from its rim back into its own axle")
DESPACHO = ("a wooden desk with a brass lamp inside a grand stone room, piled with "
            "tall stacks of pale paper bills")
AGUJERO = ("a dark round hole in a stone floor, with gold coins spilling over its "
           "edge and falling inside")
BASCULA = "an old brass balance scale on a dark wooden table"

ESCENAS = [
 # ---- 1:00 Los dos precios del dinero -------------------------------------
 dict(id="1-00", cubre=["1-00"], dur=2.3, efecto="fijo",
      escena=CENTRADO + "One large gold coin standing upright on a dark stone surface, with two small blank brass price tags tied to it by strings, one hanging to each side."),
 dict(id="1-04", cubre=["1-04"], dur=2.1, efecto="in",
      escena=FRONTAL + f"Scene: {BANCO}. A few small figures on the plaza."),
 dict(id="1-07", cubre=["1-07"], dur=2.9, efecto="fijo",
      escena=CENTRADO + "A dark wooden desk holding a brass desk calendar with a few pages and a brass pocket watch lying beside it."),
 dict(id="1-12", cubre=["1-12"], dur=2.9, efecto="in",
      escena=CENTRADO + f"Scene: {SALA}."),
 dict(id="1-16", cubre=["1-16", "1-19"], dur=3.8, efecto="fijo",
      escena=CENTRADO + f"Scene: {CAMINO}. Slightly misty far distance."),
 dict(id="1-22", cubre=["1-22", "1-25"], dur=3.7, efecto="out",
      escena=f"Scene: {PARQUE}. The hall is busy, the line on the board sits mid-height."),
 dict(id="1-27", cubre=["1-27"], dur=2.7, efecto="fijo",
      escena=FRONTAL + f"Scene: {MINIS}, its gold-framed doors open, and {COLA_E} walking out of them towards the viewer."),
 dict(id="1-32", cubre=["1-32"], dur=2.4, efecto="in",
      escena=f"Scene: {PARQUE}, and in its centre aisle three figures in long grey coats offering pale paper certificates to the seated traders."),
 dict(id="1-36", cubre=["1-36"], dur=2.6, efecto="fijo",
      escena=CENTRADO + f"Scene: {BASCULA}, a pale paper certificate on one pan and a small pile of gold coins on the other, a trader's hand adding one more coin."),
 dict(id="1-40", cubre=["1-40"], dur=3.3, efecto="out",
      escena=f"Scene: {PARQUE}, the hall crowded with many figures waving to lend, the dark line on the board sloping gently downwards."),
 dict(id="1-45", cubre=["1-45"], dur=1.6, efecto="fijo",
      escena=f"Scene: {PARQUE}, the hall almost empty, only two figures at the desks, the dark line on the board sloping steeply upwards."),
 dict(id="1-47", cubre=["1-47"], dur=2.8, efecto="fijo",
      escena=f"Scene: {PARQUE}, seen wide and level, half the desks occupied, the line on the board mid-height."),
 dict(id="1-52", cubre=["1-52"], dur=2.4, efecto="out",
      escena=FRONTAL + f"Scene: {BANCO}, seen from further back so it looks small against a wide grey sky, tiny figures crossing the plaza."),
 dict(id="1-56", cubre=["1-56"], dur=1.9, efecto="fijo",
      escena=FRONTAL + f"Wide scene: {BANCO} on the left and, at a distance on the right, {MASTILES}."),
 dict(id="2-00", cubre=["2-00", "2-03"], dur=3.0, efecto="in",
      escena=FRONTAL + f"Wide scene: on the left {BANCO} with figures carrying a large brass percent symbol DOWN its staircase; on the right {MASTILES} with its facade chart climbing."),
 dict(id="2-06", cubre=["2-06"], dur=1.9, efecto="fijo",
      escena=CENTRADO + "Two anonymous figures standing back to back on a stone floor: one in a dark suit looking left, one in a grey trading coat looking right."),
 dict(id="2-09", cubre=["2-09"], dur=2.1, efecto="in",
      escena=CENTRADO + "The dark-suited figure at a desk, studying a brass desk calendar showing only a few pages."),
 dict(id="2-12", cubre=["2-12"], dur=2.5, efecto="out",
      escena=f"Scene: the grey-coated trader standing at the start of {CAMINO}, looking down its whole length."),

 # ---- 2:15 De dónde sale el dinero: el ahorro -----------------------------
 dict(id="2-15", cubre=["2-15"], dur=3.1, efecto="fijo",
      escena=ISO + f"Scene: {CALLE}."),
 dict(id="2-20", cubre=["2-20", "2-22"], dur=4.1, efecto="in",
      escena=ISO + f"Scene: {CALLE}, with three small figures queuing at the bank branch door, each holding a small gold coin pouch."),
 dict(id="2-26", cubre=["2-26"], dur=2.8, efecto="fijo",
      escena=CENTRADO + f"Scene: {CAMARA}, standing alone on a wide stone floor."),
 dict(id="2-29", cubre=["2-29"], dur=2.2, efecto="in",
      escena=CENTRADO + f"Scene: {CAMARA}, with a line of ordinary small figures placing gold coin pouches inside through the open door."),
 dict(id="2-33", cubre=["2-33"], dur=2.6, efecto="out",
      escena=CENTRADO + f"Scene: {CAMARA}, with three small figures walking away from it, each carrying a bundle of banknotes."),
 dict(id="2-37", cubre=["2-37"], dur=2.2, efecto="fijo",
      escena=ISO + f"Scene: {FABRICA} {OBRAS}, small builder figures on the scaffolding."),
 dict(id="2-40", cubre=["2-40"], dur=2.5, efecto="in",
      escena=FRONTAL + f"Scene: {MINIS}, with gold coins spilling out of its open gold-framed doors down the steps."),
 dict(id="2-44", cubre=["2-44"], dur=2.3, efecto="fijo",
      escena=FRONTAL + f"Scene: {PISO}, a couple of small figures standing at its entrance looking up at it."),
 dict(id="2-47", cubre=["2-47"], dur=2.6, efecto="in",
      escena=CENTRADO + f"Scene: {CAMARA}, filled to the very top, banknote bundles pressing against the opening, gleaming softly."),
 dict(id="2-52", cubre=["2-52"], dur=1.7, efecto="fijo",
      escena=CENTRADO + f"Scene: {CAMARA}, completely full, with an empty stone floor in front of it and nobody anywhere."),
 dict(id="2-54", cubre=["2-54"], dur=2.1, efecto="fijo",
      escena=ISO + f"Scene: {CALLE}, but the grocery's green awning is rolled up and its window shuttered with grey metal, the street almost empty."),
 dict(id="2-57", cubre=["2-57"], dur=3.1, efecto="in",
      escena=ISO + f"Scene: {CALLE}, with several small figures walking slowly, each bent under a heavy pale sack carried on their back."),
 dict(id="3-01", cubre=["3-01"], dur=3.8, efecto="out",
      escena=CENTRADO + f"Scene: {CAMARA}, with a long line of small figures approaching it, each carrying a gold coin pouch towards the open door."),
 dict(id="3-06", cubre=["3-06"], dur=2.4, efecto="fijo",
      escena=ISO + f"Scene: {CALLE}, one figure at the bank branch counter handing over a gold coin pouch, their pale sack on the ground beside them, now half empty."),
 dict(id="3-09", cubre=["3-09", "3-12"], dur=3.6, efecto="in",
      escena=CENTRADO + f"Scene: {CAMARA}, with a steady stream of gold coins pouring in through a brass chute at its top, and nobody at all standing at the open door."),
 dict(id="3-14", cubre=["3-14"], dur=2.4, efecto="fijo",
      escena=CENTRADO + f"Scene: {CAMARA}, overfull, loose gold coins spilling over its rim and scattering on the stone floor."),
 dict(id="3-18", cubre=["3-18"], dur=1.8, efecto="fijo",
      escena=f"Scene: {PARQUE}, the dark line on the board plunging steeply from top left towards the bottom."),
 dict(id="3-21", cubre=["3-21"], dur=3.8, efecto="out",
      escena=f"Scene: {PARQUE}, nearly empty, the dark line on the board lying flat along the very bottom edge of the board."),
 dict(id="3-26", cubre=["3-26", "3-29"], dur=3.1, efecto="fijo",
      escena=FRONTAL + f"Scene: {CAMARA} large in the foreground overflowing with gold coins, and far behind it, small and dim, {BANCO}."),

 # ---- 3:33 Lo que ha cambiado: las dos colas ------------------------------
 dict(id="3-33", cubre=["3-33"], dur=1.7, efecto="fijo",
      escena=CENTRADO + f"Scene: {CAMARA}, lit by a single shaft of pale light on a dark stone floor."),
 dict(id="3-36", cubre=["3-36"], dur=1.8, efecto="fijo",
      escena=CENTRADO + f"Scene: {CAMARA}, filled to the very top, exactly as full as before."),
 dict(id="3-39", cubre=["3-39"], dur=3.2, efecto="out",
      escena=ISO + f"Scene: {CAMARA} in the centre, with {COLA_E} approaching from the left and {COLA_I} approaching from the right, both queues long."),
 dict(id="3-44", cubre=["3-44"], dur=1.9, efecto="in",
      escena=CENTRADO + f"Scene: {COLA_I}, seen from the side, stretching across the whole frame."),
 dict(id="3-47", cubre=["3-47"], dur=3.1, efecto="fijo",
      escena=ISO + "Scene: an office interior with figures in dark blue work overalls gathered around a table, looking at a single black server rack unit standing on it like a discovery."),
 dict(id="3-51", cubre=["3-51"], dur=2.9, efecto="in",
      escena=ISO + "Scene: figures in dark blue work overalls pushing wooden carts loaded with gold coin pouches, all moving in the same direction."),
 dict(id="3-55", cubre=["3-55"], dur=1.6, efecto="fijo",
      escena=FRONTAL + f"Scene: {DATOS}, seen straight on, filling the frame."),
 dict(id="3-58", cubre=["3-58"], dur=3.1, efecto="in",
      escena=ISO + f"Scene: {DATOS}, with a single black server rack unit standing in the foreground and a row of tall steel electricity pylons behind the building."),
 dict(id="4-03", cubre=["4-03"], dur=3.7, efecto="fijo",
      escena=ISO + "Scene: a wide plain with a long row of identical modern glass-walled data centres with flat dark roofs receding into the distance."),
 dict(id="4-07", cubre=["4-07", "4-11"], dur=3.5, efecto="in",
      escena=CENTRADO + f"Scene: {CAMARA}, with figures in dark blue work overalls carrying banknote bundles OUT of the open door, walking away loaded."),
 dict(id="4-13", cubre=["4-13"], dur=2.6, efecto="fijo",
      escena=CENTRADO + f"Scene: {COLA_E}, seen from the side, stretching across the whole frame."),
 dict(id="4-16", cubre=["4-16"], dur=3.4, efecto="in",
      escena=FRONTAL + f"Scene: {MINIS}, its steps covered by tall stacks of pale document boxes piled higher than the figures beside them."),
 dict(id="4-21", cubre=["4-21"], dur=2.1, efecto="fijo",
      escena=CENTRADO + f"Scene: {DESPACHO}."),
 dict(id="4-24", cubre=["4-24"], dur=2.2, efecto="in",
      escena=f"Scene: {PARQUE}, and at one desk a figure in a long grey coat handing over an old creased pale certificate while receiving a fresh crisp one."),
 dict(id="4-26", cubre=["4-26"], dur=2.0, efecto="fijo",
      escena=CENTRADO + "A dark wooden desk with a brass desk calendar shedding loose pages, beside a stack of old creased pale certificates."),
 dict(id="4-29", cubre=["4-29"], dur=2.7, efecto="in",
      escena=f"Scene: {PARQUE}, with {COLA_E} filing down the centre aisle towards the desks, and gold coins being passed back along the queue."),
 dict(id="4-33", cubre=["4-33"], dur=2.2, efecto="out",
      escena=FRONTAL + f"Scene: {MINIS}, with a thin stream of gold coins flowing out of its doors and down the steps."),
 dict(id="4-36", cubre=["4-36"], dur=2.3, efecto="fijo",
      escena=CENTRADO + f"Scene: {CAMARA}, its open door filling the frame."),
 dict(id="4-40", cubre=["4-40"], dur=2.8, efecto="out",
      escena=ISO + f"Scene: {CAMARA} in the centre, with {COLA_E} from the left and {COLA_I} from the right, both queues now enormous, stretching to the frame edges."),
 dict(id="4-44", cubre=["4-44"], dur=2.9, efecto="in",
      escena=CENTRADO + "Scene: a single small figure holding a gold coin pouch, standing between the reaching front figures of two queues: one in a long grey coat, one in dark blue overalls."),
 dict(id="4-49", cubre=["4-49"], dur=2.5, efecto="fijo",
      escena=CENTRADO + f"Scene: {BASCULA}, one pan holding a pale certificate, the other pan being stacked noticeably higher with gold coins by an anonymous hand."),
 dict(id="4-53", cubre=["4-53"], dur=3.1, efecto="in",
      escena=FRONTAL + f"Scene: {MASTILES}, the dark line chart on the facade climbing steeply."),
 dict(id="4-58", cubre=["4-58", "5-00"], dur=3.8, efecto="out",
      escena=CENTRADO + f"Scene: {CAMARA}, its banknote bundles now only reaching halfway up the opening, visible gaps inside."),
 dict(id="5-05", cubre=["5-05"], dur=1.3, efecto="fijo",
      escena=ISO + f"Scene: {CALLE}, a figure looking at a tall price tag standing in the grocery window."),

 # ---- 5:10 No todas las colas son iguales ---------------------------------
 dict(id="5-10", cubre=["5-10", "5-14"], dur=3.8, efecto="fijo",
      escena=CENTRADO + f"Scene: two queues facing each other across an empty stone floor: {COLA_E} on the left, {COLA_I} on the right."),
 dict(id="5-17", cubre=["5-17", "5-22"], dur=4.1, efecto="in",
      escena=ISO + f"Scene: {FABRICA} {OBRAS}, with a figure in dark blue overalls receiving a gold coin pouch at its gate, and a thin trail of gold coins on the ground leading back out of frame."),
 dict(id="5-24", cubre=["5-24"], dur=2.9, efecto="fijo",
      escena=ISO + f"Scene: {FABRICA}, finished and working, pale smoke from the chimney, wooden crates being carried out of its gate by small figures."),
 dict(id="5-28", cubre=["5-28"], dur=3.0, efecto="in",
      escena=ISO + f"Scene: {FABRICA} with a trail of gold coins leading from its gate across the ground towards {CAMARA} in the corner of the frame."),
 dict(id="5-32", cubre=["5-32"], dur=2.1, efecto="out",
      escena=ISO + f"Scene: {FABRICA}, standing complete and proud on open ground, warm windows lit."),
 dict(id="5-35", cubre=["5-35"], dur=2.7, efecto="fijo",
      escena=FRONTAL + f"Scene: {MASTILES}, the chart climbing, the plaza below busy with small walking figures."),
 dict(id="5-39", cubre=["5-39", "5-42"], dur=4.1, efecto="in",
      escena=ISO + "Scene: a wide plain with three separate building sites, each with wooden scaffolding and a small crane, small builder figures at work on all of them."),
 dict(id="5-45", cubre=["5-45"], dur=2.9, efecto="fijo",
      escena=f"Scene: {PARQUE}, nearly empty, the dark line on the board lying low and flat."),
 dict(id="5-48", cubre=["5-48"], dur=3.1, efecto="out",
      escena=ISO + "Scene: a single abandoned building site: bare scaffolding, an idle crane, no figures anywhere, a tarp flapping loose."),
 dict(id="5-52", cubre=["5-52"], dur=2.1, efecto="fijo",
      escena=CENTRADO + f"Scene: {COLA_E}, seen closer, the pale document boxes stacked in their arms."),
 dict(id="5-55", cubre=["5-55"], dur=3.0, efecto="in",
      escena=FRONTAL + f"Scene: {MINIS}, filling the frame."),
 dict(id="5-59", cubre=["5-59"], dur=3.7, efecto="fijo",
      escena=ISO + "Scene: three public works side by side on a plain: a stretch of grey motorway, a row of tall steel electricity pylons, and a harbour crane over a dock with a cargo ship."),
 dict(id="6-04", cubre=["6-04"], dur=4.2, efecto="in",
      escena=CENTRADO + f"Scene: {DESPACHO}, with small streams of gold coins running off the edge of the desk into open pale envelopes held by waiting hands."),
 dict(id="6-09", cubre=["6-09"], dur=2.6, efecto="fijo",
      escena=FRONTAL + f"Scene: {MINIS}, with a small counter window at its side and a line of ordinary figures each receiving a small gold coin pouch."),
 dict(id="6-12", cubre=["6-12"], dur=3.9, efecto="out",
      escena=ISO + f"Scene: {CALLE}, figures with small gold coin pouches shopping at the green-awning grocery, coins passing over the counter."),
 dict(id="6-17", cubre=["6-17"], dur=3.7, efecto="fijo",
      escena=ISO + "Scene: a small corner shop being built, wooden scaffolding around it, a figure proudly holding a gold coin pouch at its door."),
 dict(id="6-22", cubre=["6-22"], dur=2.6, efecto="fijo",
      escena=ISO + "Scene: a figure at the green-awning grocery counter paying with coins from a nearly empty pouch, a full shopping bag on the counter."),
 dict(id="6-25", cubre=["6-25"], dur=4.0, efecto="in",
      escena=ISO + "Scene: two small buildings side by side: on the left the finished corner shop with a trail of gold coins returning from its door; on the right a plain house with a single empty pale envelope on its doorstep."),

 # ---- 6:30 La espiral -----------------------------------------------------
 dict(id="6-30", cubre=["6-30"], dur=1.8, efecto="fijo",
      escena=CENTRADO + f"Scene: {RUEDA}, standing still in half shadow."),
 dict(id="6-33", cubre=["6-33"], dur=1.8, efecto="in",
      escena=CENTRADO + f"Scene: {RUEDA}, now fully lit, the leather belt taut."),
 dict(id="6-36", cubre=["6-36"], dur=2.3, efecto="fijo",
      escena=CENTRADO + f"Scene: {RUEDA}, with gold coins riding upwards on its leather belt."),
 dict(id="6-39", cubre=["6-39"], dur=2.3, efecto="in",
      escena=CENTRADO + f"Scene: {DESPACHO}, the stacks of pale paper bills now taller than the brass lamp."),
 dict(id="6-43", cubre=["6-43"], dur=2.4, efecto="fijo",
      escena=CENTRADO + f"Scene: {DESPACHO}, the stacks now reaching towards the ceiling, the desk barely visible beneath them."),
 dict(id="6-46", cubre=["6-46"], dur=3.3, efecto="in",
      escena=CENTRADO + f"Scene: {AGUJERO}, in the middle of a grand stone room."),
 dict(id="6-49", cubre=["6-49", "6-52"], dur=3.6, efecto="out",
      escena=f"Scene: {PARQUE}, with {COLA_E} now filling the whole centre aisle, waiting."),
 dict(id="6-55", cubre=["6-55"], dur=2.9, efecto="fijo",
      escena=f"Scene: {PARQUE}, the seated traders leaning back from a single figure in a long grey coat standing in the aisle with open hands."),
 dict(id="6-59", cubre=["6-59"], dur=3.0, efecto="in",
      escena=CENTRADO + f"Scene: {BASCULA}, a pale certificate on one pan, and the other pan being loaded with a visibly larger pile of gold coins than before."),
 dict(id="7-04", cubre=["7-04", "7-06"], dur=3.6, efecto="fijo",
      escena=CENTRADO + f"Scene: {RUEDA}, filling the frame, coins riding its belt, faint motion streaks on the rim."),
 dict(id="7-09", cubre=["7-09"], dur=2.0, efecto="in",
      escena=CENTRADO + f"Scene: {RUEDA}, seen closer on its rim and belt, stronger motion streaks."),
 dict(id="7-11", cubre=["7-11"], dur=2.7, efecto="fijo",
      escena=FRONTAL + f"Scene: {MASTILES}, and at the base of each flagpole a tall stack of pale paper bills."),
 dict(id="7-15", cubre=["7-15"], dur=2.0, efecto="in",
      escena=CENTRADO + "Scene: a long dark table with a row of gold coin stacks of similar height, and one single stack towering far above the others."),
 dict(id="7-18", cubre=["7-18"], dur=2.0, efecto="out",
      escena=FRONTAL + f"Scene: three identical white classical government buildings with columned porticos side by side in a row."),
 dict(id="7-21", cubre=["7-21"], dur=3.9, efecto="fijo",
      escena=ISO + "Scene: three public buildings in a row on a plain: a white building with a red cross sign and the word HOSPITAL over its door, a brick school building with the word COLEGIO over its door, and a stretch of grey motorway."),
 dict(id="7-26", cubre=["7-26"], dur=2.8, efecto="in",
      escena=ISO + "Scene: the same three public buildings, with a stream of gold coins flowing along the road PAST them without stopping, heading out of frame."),
 dict(id="7-31", cubre=["7-31"], dur=1.9, efecto="fijo",
      escena=CENTRADO + f"Scene: {AGUJERO}, seen from directly above, coins vanishing into the dark."),

 # ---- 7:37 Japón y la imprenta --------------------------------------------
 dict(id="7-37", cubre=["7-37"], dur=3.8, efecto="fijo",
      escena=FRONTAL + f"Scene: {BANCO}, and at the foot of its staircase, small against it, {IMPRENTA}."),
 dict(id="7-42", cubre=["7-42"], dur=2.5, efecto="fijo",
      escena=FRONTAL + "Scene: a single tall brass flagpole on a stone plaza flying the flag of Japan, a white field with a centered red disc, in front of a wide modern government building."),
 dict(id="7-47", cubre=["7-47"], dur=4.5, efecto="in",
      escena=CENTRADO + f"Scene: {IMPRENTA}, working, the long sheet of pale banknotes rolling out steadily."),
 dict(id="7-52", cubre=["7-52"], dur=2.8, efecto="out",
      escena=CENTRADO + f"Scene: {IMPRENTA}, with printed banknotes piling up in drifts on the floor around it, and nobody there to take them."),
 dict(id="7-57", cubre=["7-57"], dur=1.9, efecto="fijo",
      escena=CENTRADO + f"Scene: {BASCULA}, a thick wad of pale banknotes on one pan hanging LOW, outweighed by a single gold coin on the other pan."),
 dict(id="8-00", cubre=["8-00", "8-04"], dur=4.2, efecto="in",
      escena=ISO + "Scene: a harbour dock with a cargo ship and stacked shipping containers, each container carrying a large blank white price tag, the tags oversized."),
 dict(id="8-06", cubre=["8-06"], dur=3.2, efecto="fijo",
      escena=ISO + "Scene: three goods in a row on a dock: a steel electricity pylon section, wooden crates of vegetables, and a heap of dark coal, each with a large blank white price tag."),
 dict(id="8-09", cubre=["8-09"], dur=3.4, efecto="out",
      escena=FRONTAL + f"Scene: {MINIS}, with {IMPRENTA} beside it feeding its long sheet of pale banknotes directly towards the building's doors."),
 dict(id="8-13", cubre=["8-13"], dur=2.0, efecto="fijo",
      escena=CENTRADO + f"Scene: {BASCULA}, its two pans locked visibly unbalanced, one high, one low."),
 dict(id="8-16", cubre=["8-16"], dur=3.4, efecto="in",
      escena=ISO + f"Scene: {CALLE}, close on the green-awning grocery: a figure at the counter, and standing in the window a price tag noticeably taller than the figure's head."),

 # ---- 8:22 La lección y el cierre -----------------------------------------
 dict(id="8-22", cubre=["8-22"], dur=3.3, efecto="out",
      escena=ISO + f"Wide scene: {CALLE} in the foreground, and behind it across a plaza, {BANCO} and {MASTILES} small in the distance, one continuous city."),
 dict(id="8-26", cubre=["8-26"], dur=2.8, efecto="fijo",
      escena=CENTRADO + f"Scene: {CAMARA}, filled to the very top, gleaming, coins spilling over the rim."),
 dict(id="8-31", cubre=["8-31"], dur=2.8, efecto="in",
      escena=CENTRADO + "Scene: a dark wooden desk with tall pale ledger books stacked into a tower, the whole tower resting on a base of loose gold coins."),
 dict(id="8-36", cubre=["8-36", "8-39"], dur=3.1, efecto="fijo",
      escena=CENTRADO + f"Scene: {CAMARA}, full, with a small blank brass price tag hanging from its door handle."),
 dict(id="8-41", cubre=["8-41"], dur=3.2, efecto="in",
      escena=CENTRADO + f"Scene: the small blank brass price tag hanging from the vault door handle, seen close, the {CAMARA} soft behind it."),
 dict(id="8-46", cubre=["8-46", "8-49"], dur=4.0, efecto="out",
      escena=ISO + f"Scene: {CAMARA} half empty, visible gaps between the banknote bundles inside, with {COLA_E} and {COLA_I} waiting motionless at its door."),
 dict(id="8-52", cubre=["8-52"], dur=2.8, efecto="fijo",
      escena=CENTRADO + "Scene: two framed pictures hanging side by side on a dark stone wall: the left frame holds the flag of Germany, three horizontal bands of black, red and gold; the right frame holds a coastal border fence running into a blue sea."),
 dict(id="8-57", cubre=["8-57"], dur=3.0, efecto="in",
      escena=ISO + f"Scene: {CALLE} at dusk, windows warmly lit, and the single street lamp on the corner flickered out, dark."),
 # El cierre es la plantilla del canal (recursos/cierre/6-engranaje.png):
 # marco dorado para el video superpuesto y el engranaje como boton de canal.
 # La voz acaba y la imagen aguanta ~8 s con cola de silencio para dar tiempo
 # a clicar. NO se genera: se copia de recursos/cierre/.
 dict(id="9-02", cubre=["9-02"], dur=8.4, efecto="fijo",
      escena="PLANTILLA recursos/cierre/6-engranaje.png — no generar"),
]

# --- Canónicas: la imagen que define a cada elemento recurrente -------------
# Las escenas que contienen un elemento se generan con su canónica como
# referencia (flux_2 --image, mismo precio que sin ella). Las canónicas que no
# existen aún se acuñan en la fase A; las escenas-canónica se generan primero
# y el resto las referencia en la fase B.
CANONICAS = {
    "CALLE":    "prueba-literal/1-calle.png",
    "BANCO":    "prueba-literal/2-banco-central.png",
    "MASTILES": "prueba-literal/3-banderas.png",
    "CUATRO":   "prueba-literal/4b-competencia.png",   # minis+datos+camara+colas
    "PARQUE":   "imagenes/1-22.png",
    "SALA":     "imagenes/1-12.png",
    "CAMINO":   "imagenes/1-16.png",
    "BASCULA":  "imagenes/1-36.png",
    "MESA":     "imagenes/1-07.png",
    # acuñadas en fase A (la escena ES la canónica):
    "CAMARA":   "imagenes/2-26.png",
    "MINIS":    "imagenes/5-55.png",
    "DATOS":    "imagenes/3-55.png",
    "COLA_E":   "imagenes/4-13.png",
    "COLA_I":   "imagenes/3-44.png",
    "FABRICA":  "imagenes/5-32.png",
    "RUEDA":    "imagenes/6-33.png",
    "DESPACHO": "imagenes/4-21.png",
    "IMPRENTA": "imagenes/7-47.png",
    "AGUJERO":  "imagenes/6-46.png",
}

# Escenas de la fase A que se acuñan DESDE la imagen compuesta del gancho,
# para que hereden la identidad ya establecida en el vídeo:
ACUNA_DESDE_CUATRO = {"2-26", "5-55", "3-55", "4-13", "3-44"}
# El resto de canónicas nuevas (fábrica, rueda, despacho, imprenta, agujero)
# se acuñan desde texto: son elementos que el gancho no enseñó.

ELEMENTOS = dict(CALLE=CALLE, BANCO=BANCO, MASTILES=MASTILES, CAMARA=CAMARA,
                 MINIS=MINIS, DATOS=DATOS, COLA_E=COLA_E, COLA_I=COLA_I,
                 PARQUE=PARQUE, SALA=SALA, CAMINO=CAMINO, FABRICA=FABRICA,
                 IMPRENTA=IMPRENTA, RUEDA=RUEDA, DESPACHO=DESPACHO,
                 AGUJERO=AGUJERO, BASCULA=BASCULA,
                 MESA="brass desk calendar")   # la mesa se detecta por su objeto


def referencias(escena_txt, propio_id):
    """Qué canónicas necesita una escena, sin referenciarse a sí misma."""
    refs = []
    for nombre, frase in ELEMENTOS.items():
        if frase in escena_txt and CANONICAS[nombre].split("/")[-1] != propio_id + ".png":
            refs.append(CANONICAS[nombre])
    return sorted(set(refs))


if __name__ == "__main__":
    import json, sys
    from pathlib import Path
    base = Path(__file__).parent.parent          # carpeta Video 5
    ids_canonicas = {c.split("/")[-1][:-4] for c in CANONICAS.values()}

    fase_a, fase_b = [], []
    for e in ESCENAS:
        prompt = MUNDO + e["escena"]
        if e["id"] in ids_canonicas:
            item = {"id": e["id"], "prompt": prompt}
            if e["id"] in ACUNA_DESDE_CUATRO:
                item["refs"] = [str(base / CANONICAS["CUATRO"])]
                item["prompt"] += (" Take the corresponding object from the reference "
                                   "image and keep it identical: same shape, same "
                                   "materials, same colours.")
            fase_a.append(item)
        else:
            refs = [str(base / r) for r in referencias(e["escena"], e["id"])]
            item = {"id": e["id"], "prompt": prompt}
            if refs:
                item["refs"] = refs[:3]
                item["prompt"] += (" The recurring objects and buildings must be "
                                   "IDENTICAL to the reference images: same "
                                   "architecture, same materials, same colours, "
                                   "same details. Same crisp pixel art style.")
            fase_b.append(item)

    (Path(__file__).parent / "plan-a.json").write_text(
        json.dumps(fase_a, indent=1, ensure_ascii=False), encoding="utf-8")
    (Path(__file__).parent / "plan-b.json").write_text(
        json.dumps(fase_b, indent=1, ensure_ascii=False), encoding="utf-8")
    con_ref = sum(1 for i in fase_b if "refs" in i)
    print(f"fase A (canonicas y sueltas ya definidas): {len(fase_a)}")
    print(f"fase B: {len(fase_b)}  (con referencia: {con_ref}, sueltas: {len(fase_b)-con_ref})")
    dobles = [i["id"] for i in fase_b if len(i.get("refs", [])) > 1]
    print(f"escenas con 2+ referencias: {len(dobles)}: {', '.join(dobles)}")
