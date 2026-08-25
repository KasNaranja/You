#!/usr/bin/env python3
"""Orden de publicación para MejoresClipsCine.

Son los 34 verdes de `potencial.py` ordenados. El orden no es por visitas: un
canal que empieza no tiene suscriptores, así que **todo lo que entra viene del
feed de Shorts**, delante de gente que no te conoce de nada. Eso manda en los
primeros vídeos y pesa más que el número del original.

Tres cosas deciden la posición:

  · **Reconocimiento inmediato en España.** En frío ganan las marcas que
    cualquiera identifica en medio segundo: Regreso al futuro, Piratas, El
    Señor de los Anillos, Fast & Furious.
  · **Lo que ya está probado.** Jackie Chan es el nombre con mejor conversión
    de todo el cruce con Tengri: sus dos mayores éxitos salen de ahí. Va
    primero aunque el original no sea de los más vistos.
  · **No repetir saga seguida.** Dos de Piratas pegados se comen el uno al
    otro en el feed.

Ritmo: **dos al día**. No es un capricho — es lo que dicen los datos de Scroll
Spheres. Cuando subían diez al día (enero-abril) su mediana cayó a 11.471
visitas; ahora publican 3,8 y su mediana va por 165.530. Dos al día son
suficientes tiros para que el algoritmo encuentre el canal sin que baje la
calidad de cada uno.

Diecisiete días. **Al séptimo, parar y mirar**: un short madura en una semana,
así que los catorce primeros ya se pueden juzgar. Lo que haya funcionado marca
por dónde seguir, y el resto de la lista se reordena con eso.
"""

# (título de Scroll Spheres, por qué va en esta posición)
ORDEN = [
    # ── Publicados (11) — se quedan arriba para que el histórico no baile ──
    ('Legendary Interaction Between Jackie Chan & Native Americans - Shanghai Noon (2000)',
     'Empezamos por lo único probado: Jackie Chan es el nombre con mejor conversión de todo el cruce, los dos mayores éxitos de Tengri salen de ahí. Y es el último que queda libre.'),
    ('George McFly vs. The Rogue Milkshake 🥤💀 - Back To The Future Blooper',
     'Un blooper de Regreso al futuro no necesita ni una palabra traducida, y la marca la reconoce todo el mundo en medio segundo. El segundo vídeo tiene que confirmar de qué va el canal.'),
    ('Why Momoa Threw A Tooth At Vin Diesel In Fast X',
     'Fast & Furious arrastra muchísimo en España y la anécdota es lo bastante bruta para comentarse sola.'),
    ('This 90s Practical Effect Looks Way Too Real For Comfort 💀 - Alien 3 Boneless Prop',
     'El vídeo más visto de todo el catálogo (39,7 M) y no hace falta explicar nada: se ve y da grima.'),
    ('Why "The Impossible" Only Had One Shot To Film The Tsunami Scene',
     'El más pequeño de los verdes en el original y aun así va aquí: es una película española de Bayona. Esa ventaja no la recoge ningún número de un canal inglés.'),
    ('Sam Raimi Gave Alfred Molina "Extra Motivation" On Set of Spider-Man 2',
     'Spider-Man 2 es masivo, la anécdota se ve en pantalla y hace gracia. Cambia de tono respecto al anterior.'),
    ("How Return Of The King Shot Saruman's Body Sinking",
     'El Señor de los Anillos es de las marcas más fuertes que hay aquí, y el «cómo se hizo» es el formato que mejor le funciona al canal original.'),
    ('Breaking the Cycle - Mockingjay Part 2 (2015)',
     'El mayor múltiplo de todo el catálogo: 1.695 veces la mediana de su mes. Saga masiva y momento que se lee sin contexto.'),
    ('They Made A Fake Dummy Of Daniel Radcliffe - Swiss Army Man (2016)',
     '17,9 M y x1.562. Radcliffe es reclamo automático aunque la película no la sitúe nadie.'),
    ('They Were TOO FAST For The Filmmakers - The Phantom Menace - Obi Wan & Darth Maul Training Session',
     'Star Wars con un dato que se demuestra solo: tuvieron que ralentizar la escena.'),
    ("The Absolute Realism of Leonardo DiCaprio's Acting",
     'DiCaprio está entre los nombres más buscados y el gancho promete una reacción real, no un análisis.'),
    # ── Ola caliente del 20-25/08 — inmediatez primero ──
    ('The Village Stood No Chance In The Northman (2022)',
     '4,7 M en 5 días: el vídeo más fuerte de la ola nueva y el único gordo que sigue libre. El asalto vikingo se entiende sin una palabra.'),
    ("Ryan Reynolds Tanked A Real Fighter's Punch",
     '+800.000 visitas solo en los últimos 4 días: es el pendiente que sigue más vivo. Reynolds, un puñetazo real y una reacción.'),
    ('Nothing On Genna Is Harmless - Predator Badlands',
     '4,8 M en 5 días, la ola de Predator: Badlands es la del momento y LA PORTADA YA ESTÁ HECHA. Ojo: Tengri lo sacó ayer (2.300 visitas aún) — se compite, pero la ola da para dos.'),
    ('Everybodys Gangster Till The He Does This - Nobody',
     '+595.000 en 4 días, el otro pendiente que sigue creciendo. Nobody le ha dado a Tengri algunas de sus mejores cifras.'),
    ('The Split-Second Move In The Matrix Reloaded',
     '240.000 en menos de 5 días y libre. Matrix es marca masiva en España y la esquiva es puro visual.'),
    ('Brendan Fraser Passed Out Filming in The Mummy',
     'Recién salido y libre. La momia es nostalgia fuerte aquí y el dato es físico: se desmayó rodando.'),
    ("Morpheus' Weapons Training For The Matrix Reloaded",
     '102.000 en días y libre. Segundo de Matrix, separado del primero a propósito.'),
    ('How Did They Do This In 1937 Without Any CGI? - Sh! The Octopus (1937)',
     '23,2 M sin que nadie conozca la película: el truco es el protagonista. Prueba si ese formato aguanta en castellano, que es información útil para las otras dos de cine antiguo.'),
    ('The Bug Scene In The Matrix Is Creepy',
     '27.000 en días y libre. Tercero de Matrix, ya con un día de distancia de los otros dos.'),
    # ── Verdes estáticos — el orden anterior, que sigue siendo la mejor apuesta ──
    ("He Wasn't Acting In This Moment - The Passion Of The Christ",
     'La Pasión fue un fenómeno en España y «no estaba actuando» promete algo que se ve.'),
    ("In Twilight (2008), that iconic forest scene where they glide through the trees wasn't CGI",
     'Crepúsculo trae un público distinto al de los siete anteriores. Ensanchar pronto evita quedarse encasillado en cine de acción.'),
    ('D&D: Honor Among Thieves (2023): Owlbear vs. Sofina',
     '27,9 M y x1.528. La película no funcionó aquí, pero una criatura aplastando a la villana se entiende sin haberla visto.'),
    ('How They Filmed the Pyramid Fall in Apocalypto',
     'Apocalypto tiene mucho tirón en España y es puro «cómo se hizo».'),
    ('Behind the Scenes of The Terminator 3 T-X Practical Gag - Kristanna',
     'Terminator más efecto práctico: la combinación que mejor rinde en el canal original.'),
    ('The Twist Was In Front Of Our Eyes - The Prestige (2006)',
     'El truco final tiene culto aquí y el giro se enseña señalando la pantalla.'),
    ('The Most Interesting Take On A Sniper Duel You’ll Ever See 💀 - Furiosa: A Mad Max Saga',
     'Un duelo de francotiradores se entiende sin una sola palabra.'),
    ('During the filming of Pirates Of The Caribbean At Worlds End Johnny Accidently Drank Real Rum On Set',
     'Depp y Piratas son de lo más buscado. Es el primero de tres de esta saga, repartidos a propósito.'),
    ("1960's Practical Effects Were Different - Mr. Sardonicus (1961)",
     'x868. Si el de 1937 funcionó, este va detrás; si no, se baja al final de la lista.'),
    ("In Smile 2 (2024) Did You Know This Nightmare Monster In Smile 2 Wasn't Just CGI?",
     'Terror reciente y «no era CGI»: la contorsionista se ve y da grima. Abre el terreno del terror.'),
    ('Young Biff Really Had NO Chill With Future Biff - Back To The Future II',
     'Segundo de Regreso al futuro, lejos del primero para no saturar.'),
    ('Batman Has The Punching Power Of An SUV',
     'Batman más una cifra concreta: el formato que mejor entra en una miniatura.'),
    ('How Jack Sparrow Outsmarted the Royal Navy With a Lobster Trap | Pirates of the Caribbean 2003',
     'Segundo de Piratas. Una ocurrencia que se ve de principio a fin.'),
    ('I’m Convinced Alfred Molina Is The Most Talented Villain In History - Spider-Man 2 Blooper',
     'Blooper de una película masiva. Va tarde porque ya hubo otro de Spider-Man 2 en el puesto 6.'),
    ('Johnny Depp Scammed 19 yr old Leonardo DiCaprio 😂',
     'Depp y DiCaprio en el mismo titular, y ambos ya presentados al público del canal.'),
    ('This Shot Quietly Exposes Fight Club’s Twist About Marla & Tyler - Fight Club (1999) Movie Detail',
     'El club de la lucha ya le rindió 1,1 M a Tengri con otra escena. Ojo: nosotros ya hicimos la del narrador, así que este va de segundo de la película, no de primero.'),
    ('This Hand Gesture in Inglourious Basterds (2009) Reveals Everything',
     'El gesto de los dedos se entiende sin idioma y es de las escenas más célebres que hay.'),
    ('Sigourney Weaver: Real Life Baller - Alien: Resurrection Behind The Scenes',
     'Un enceste real de espaldas, en una toma. Cero explicación.'),
    ("Terry Crew's Dancing Scene Is Legendary To This Day - White Chicks",
     'Es un meme universal y ya circula solo. Buen cierre de tanda: ligero y muy compartible.'),
    ('Eddie Was Completely Vaporized In Spider-Man 3',
     'Escena conocida con un desenlace discutible: de los pocos que abren conversación en comentarios. OJO: Tengri acaba de sacar «Este Detalle Reveló el Destino de Eddie Brock» — comprobar si es la misma escena antes de hacerlo.'),
]

# Ya publicados en el canal. Fuente: el Excel que el usuario devolvió el
# 25/08/2026 con estas filas marcadas en amarillo — los 11 primeros del
# plan, en orden. Se pintan de amarillo y no consumen días pendientes.
PUBLICADOS = {
    'Legendary Interaction Between Jackie Chan & Native Americans - Shanghai Noon (2000)',
    'George McFly vs. The Rogue Milkshake 🥤💀 - Back To The Future Blooper',
    'Why Momoa Threw A Tooth At Vin Diesel In Fast X',
    'This 90s Practical Effect Looks Way Too Real For Comfort 💀 - Alien 3 Boneless Prop',
    'Why "The Impossible" Only Had One Shot To Film The Tsunami Scene',
    'Sam Raimi Gave Alfred Molina "Extra Motivation" On Set of Spider-Man 2',
    "How Return Of The King Shot Saruman's Body Sinking",
    'Breaking the Cycle - Mockingjay Part 2 (2015)',
    'They Made A Fake Dummy Of Daniel Radcliffe - Swiss Army Man (2016)',
    'They Were TOO FAST For The Filmmakers - The Phantom Menace - Obi Wan & Darth Maul Training Session',
    "The Absolute Realism of Leonardo DiCaprio's Acting",
}

RITMO = 2          # shorts al día
REVISION = 7       # a los siete días se para y se mira qué ha funcionado
