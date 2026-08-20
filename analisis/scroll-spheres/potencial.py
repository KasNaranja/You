#!/usr/bin/env python3
"""Criba de los shorts libres de Scroll Spheres que pasaron del millón.

El criterio no me lo he inventado: sale de mirar qué le funcionó a Tengri y qué
no. Sus aciertos son escenas que se entienden sin haber visto la película, con
algo físico que ver. Sus fracasos son datos de aficionado y cosas que dependen
del inglés. De ahí las cuatro preguntas:

  1. ¿Se entiende sin contexto, en los tres primeros segundos?
  2. ¿Hay algo físico que ver, o es un dato hablado?
  3. ¿Sobrevive a la traducción? Los acentos, los juegos de palabras y las
     frases míticas en inglés se mueren en castellano, y más con el doblaje.
  4. ¿La película o el actor significan algo en España?

Las cuatro a favor es «alto». Una en contra, «medio». Dos o más, «bajo».
"""

# id de Scroll Spheres → short del que ya hemos preparado la portada para
# MejoresClipsCine. Es lo trabajado en sesión, no necesariamente lo publicado:
# si alguno se quedó en el cajón, se quita de aquí y vuelve a la lista de libres.
TUYOS = {
    "-0_FVd4e0-0": "He Noticed Something Was Off - Shutter Island",
    "MDPoyckAAxQ": "Ledger Ignored Nolan & Nailed It - The Dark Knight",
    "GYhNsRaydBE": "Jackie Chan Jumped Down 10 Stories At 52 Years Old",
    "iJzK_F3YbiE": "The Narrator Did This To Get Rid of Tyler",
    "CwqiHkcnY-c": "The Accident That Made The Final Cut",
    "qzJAptTEks0": "The Toughest Henchman In John Wick 2",
    "8HH6maVkTKk": "Nolan Pushed Anne Hathaway To Do Her Own Stunts",
    "_Mgru9x5pfs": "The Marquis Was Doomed Either Way - John Wick 4",
    "rymvu8F3aGA": "It Follows (2014) Came From A Real Nightmare",
    "9LTl48x2keA": "When You Forget To Bring A Backup - Bullet Train",
    "KBLGsUJpTIo": "Kylo Ren Had The Most Terrifying Entrance",
    "_Wyyz-qZdeA": "The Realism Behind Ammo Tracking In John Wick 2",
}

# título de Scroll Spheres → (potencial, por qué)
POTENCIAL = {
    "This 90s Practical Effect Looks Way Too Real For Comfort 💀 - Alien 3 Boneless Prop":
        ("alto", "Efecto práctico noventero que impresiona sin explicación. Alien se conoce aquí de sobra."),
    "D&D: Honor Among Thieves (2023): Owlbear vs. Sofina":
        ("alto", "Una criatura aplasta a la villana: no hace falta haber visto la película para entenderlo."),
    "Breaking the Cycle - Mockingjay Part 2 (2015)":
        ("alto", "Los juegos del hambre es masivo en España y el momento se lee solo."),
    "How Did They Do This In 1937 Without Any CGI? - Sh! The Octopus (1937)":
        ("alto", "La película no la conoce nadie y da igual: el gancho es el truco de 1937."),
    "In Ahsoka (2023) After 20 Years. Anakin Is Still A Goat With The Saber":
        ("medio", "Star Wars vende, pero hay que seguir la serie para que signifique algo."),
    "They Made A Fake Dummy Of Daniel Radcliffe - Swiss Army Man (2016)":
        ("alto", "Radcliffe es reclamo automático y el muñeco se ve en pantalla."),
    "He Wasn't Acting In This Moment - The Passion Of The Christ":
        ("alto", "La Pasión fue fenómeno en España y «no estaba actuando» promete algo que se ve."),
    "1960's Practical Effects Were Different - Mr. Sardonicus (1961)":
        ("alto", "Mismo caso que el de 1937: el efecto es el protagonista, la película es lo de menos."),
    "Did You Notice This Magneto Character Arc Detail?":
        ("medio", "Buen detalle, pero pide conocer el arco entero del personaje."),
    "How They Filmed the Pyramid Fall in Apocalypto":
        ("alto", "Apocalypto tiene mucho tirón aquí y el «cómo se hizo» es puro visual."),
    "Stan Lee's Favorite DC Character - Krypton (2018)":
        ("bajo", "Krypton no la vio nadie en España y el dato es de coleccionista."),
    "During the filming of Pirates Of The Caribbean At Worlds End Johnny Accidently Drank Real Rum On Set":
        ("alto", "Depp y Piratas son de lo más buscado, y la anécdota se cuenta en una frase."),
    "The Most Heartfelt Way A Director Ever Kept His Crew’s Spirits High - Inglourious Basterds":
        ("medio", "Tarantino vende, pero es una historia de rodaje sin golpe visual."),
    "Sam Raimi Gave Alfred Molina \"Extra Motivation\" On Set of Spider-Man 2":
        ("alto", "Spider-Man 2 es masivo y la «motivación» se ve y hace gracia."),
    "Why Momoa Threw A Tooth At Vin Diesel In Fast X":
        ("alto", "Fast & Furious arrastra muchísimo aquí y la anécdota es tan bruta que se comparte sola."),
    "Jaafar Jackson Nailed the Michael Jackson Popcorn Meme":
        ("bajo", "Depende de un meme anglosajón que aquí no tiene el mismo recorrido."),
    "Practical Effects + CGI In Project Power (2020)":
        ("medio", "Visualmente funciona, pero Project Power pasó sin pena ni gloria en España."),
    "The Most Interesting Take On A Sniper Duel You’ll Ever See 💀 - Furiosa: A Mad Max Saga":
        ("alto", "Duelo de francotiradores: se entiende sin una sola palabra."),
    "Lucy Liu Movie: Cillian Murphy’s Kid Cameo":
        ("bajo", "Trivia pura, sin nada que mirar."),
    "The Absolute Realism of Leonardo DiCaprio's Acting":
        ("alto", "DiCaprio es de los nombres que más se buscan y el gancho promete una reacción real."),
    "Marvel’s Best Visual of The Blip In The Entire MCU?":
        ("medio", "Necesita tener el MCU en la cabeza."),
    "Tom Hanks Changed His Accent to Match the Child Actor in Forrest Gump (1994)":
        ("bajo", "Es un dato de acento: con el doblaje al castellano se queda sin nada que enseñar."),
    "Why Nate couldn't change his hair - Legends of Tomorrow":
        ("bajo", "Serie sin recorrido en España."),
    "They Were TOO FAST For The Filmmakers - The Phantom Menace - Obi Wan & Darth Maul Training Session":
        ("alto", "Star Wars más un dato que se demuestra en pantalla: tuvieron que ralentizarlo."),
    "How Did Will Miss This? Stranger Things Season 4":
        ("medio", "Stranger Things arrastra, pero es un detalle de trama, no un golpe."),
    "The Strudel Scene In Inglourious Basterds Is Actually A Form Of Psychological Control":
        ("bajo", "Todo el peso está en el diálogo y en el análisis."),
    "The Quiet Detail Everyone Overlooked In Sinners (2025)":
        ("medio", "Película reciente con poco recorrido aquí todavía."),
    "In Deadpool & Wolverine (2024) Deadpool relives a childhood memory":
        ("medio", "Deadpool vende, pero el detalle es emocional y pide contexto."),
    "George McFly vs. The Rogue Milkshake 🥤💀 - Back To The Future Blooper":
        ("alto", "Regreso al futuro es intocable en España y un blooper no necesita traducción."),
    "Eddie Was Completely Vaporized In Spider-Man 3":
        ("alto", "Escena conocida, desenlace visual y discutible: comentarios asegurados."),
    "Not Feeling Pain Isn't A Superpower - Novocaine":
        ("medio", "La premisa es visual, pero la película no la sitúa casi nadie."),
    "The Scene That Made Radcliffe Do Guns Akimbo":
        ("bajo", "Guns Akimbo es demasiado marginal aquí."),
    "Chris Hemsworth is focusing on memories now more than ever":
        ("bajo", "Es una noticia sobre el actor, no una escena de cine."),
    "Behind the Scenes of The Terminator 3 T-X Practical Gag - Kristanna":
        ("alto", "Terminator más efecto práctico: la combinación que mejor le funciona al canal."),
    "Daniel Radcliffe Becomes A Farting Jetski":
        ("medio", "Es viral y visual, pero fuera de contexto queda más raro que gracioso."),
    "The confidence of Chris Evans - The Losers (2010)":
        ("medio", "Chris Evans es reclamo; la película, no."),
    "Shia LaBeouf Caught Patrick Dempsey Off Guard":
        ("bajo", "Momento de entrevista: todo el peso está en lo que se dice."),
    "Dark Truth Behind Godzilla’s Underdeveloped Form":
        ("medio", "El dato tiene fuerza, pero es más para leer que para ver."),
    "In Smile 2 (2024) Did You Know This Nightmare Monster In Smile 2 Wasn't Just CGI?":
        ("alto", "Terror reciente y «no era CGI»: la contorsionista se ve y da grima."),
    "The start of a legend: Heath Ledger - 10 Things I Hate About You (1999)":
        ("medio", "Ledger es un reclamo enorme, pero la escena es una canción en inglés."),
    "Rocky's Puppeteer Became Rocky's Voice In Project Hail Mary":
        ("bajo", "Tengri ya probó con Project Hail Mary y retuvo un 0,6 %."),
    "How Return Of The King Shot Saruman's Body Sinking":
        ("alto", "El Señor de los Anillos es de las marcas más fuertes aquí y es un «cómo se hizo» puro."),
    "Seann William Scott in The Wrath of Becky (2023)":
        ("bajo", "Película sin ningún recorrido en España."),
    "Chris Pratt's Most Awkward Blooper - Passengers":
        ("medio", "Blooper correcto, pero sin nada memorable."),
    "The Doctor’s Curiousity - 28 Years Later (2025): The Bone Temple":
        ("medio", "Estreno muy reciente: aún no hay masa crítica buscándolo."),
    "Peaky Blinders (2013): 3.000 cigarettes per season?":
        ("medio", "Peaky Blinders arrastra mucho aquí, pero el dato no se ve, se cuenta."),
    "Ryan Reynolds Tanked A Real Fighter's Punch":
        ("alto", "Reynolds, un puñetazo real y una reacción: no hace falta nada más."),
    "Everybodys Gangster Till The He Does This - Nobody":
        ("alto", "Nobody le ha dado a Tengri sus mejores cifras y esta escena todavía está libre."),
    "The Practical Effects Behind The Roadrunner Puppet":
        ("bajo", "Demasiado de nicho y el título no promete gran cosa."),
    "Sanjuro (1962): The mistake that changed cinema":
        ("medio", "El plano es icónico de verdad, pero Kurosawa es público cinéfilo, no masivo."),
    "The Twist Was In Front Of Our Eyes - The Prestige (2006)":
        ("alto", "El truco final tiene culto en España y el giro se enseña señalando la pantalla."),
    "After the premiere of Interstellar (2014) Timothée Chalamet cried for a straight hour":
        ("medio", "Dos nombres fuertes, pero es una anécdota contada, sin imagen propia."),
    "Best Line In Cinema - Once Upon a Time in Mexico (2003)":
        ("bajo", "Toda la gracia está en la frase en inglés."),
    "Obi-Wan realized Anakin might actually know what he’s talking about - ROTS Deleted Scene":
        ("medio", "Escena eliminada de Star Wars, pero es diálogo."),
    "The Director Played Edna - The Incredibles (2004)":
        ("medio", "Buen dato, aunque en España Edna está doblada y se pierde media gracia."),
    "DM is facepalming in D&D: Honor Among Thieves (2023)":
        ("bajo", "Chiste para quien juega a rol."),
    "I’m Convinced Alfred Molina Is The Most Talented Villain In History - Spider-Man 2 Blooper":
        ("alto", "Blooper de una película masiva: se entiende y hace gracia sin subtítulos."),
    "Can Ryan Gosling Top Nicolas Cage's Ghost Rider?":
        ("bajo", "Es una pregunta especulativa, no una escena."),
    "The Lost City Props Team Pranked Daniel Radcliffe":
        ("medio", "Radcliffe tira, la película no tanto."),
    "How Jack Sparrow Outsmarted the Royal Navy With a Lobster Trap | Pirates of the Caribbean 2003":
        ("alto", "Piratas del Caribe y una ocurrencia que se ve en pantalla de principio a fin."),
    "Young Biff Really Had NO Chill With Future Biff - Back To The Future II":
        ("alto", "Regreso al futuro otra vez: reconocible al instante y puramente visual."),
    "During The Filming of Pirates of the Caribbean: At Worlds End. Elizabeth & Barbossa Couldn't Catch":
        ("medio", "Blooper correcto pero menor dentro de la saga."),
    "Johnny Depp Scammed 19 yr old Leonardo DiCaprio 😂":
        ("alto", "Depp y DiCaprio en el mismo titular. La anécdota se cuenta en diez segundos."),
    "Bro Thought He Was Him - Mad Max 2 (1981)":
        ("medio", "Visual, pero el gancho depende de un tono de meme que no traduce igual."),
    "Batman Has The Punching Power Of An SUV":
        ("alto", "Batman más una cifra concreta: el formato que mejor funciona en miniatura."),
    "The Displacer Beast - D&D: Honor Among Thieves (2023)":
        ("bajo", "Criatura para iniciados."),
    "Nicholas Cage Got Blindsided By His Own Cameo":
        ("bajo", "Es un momento de entrevista."),
    "The Deleted Krypto Scene You Missed Superman 2025":
        ("medio", "El perro funciona, pero la película es de ahora mismo."),
    "In Three Thousand Years Of Longing (2022) The most unsettling \"wall-crawl\"":
        ("medio", "El plano inquieta, aunque nadie sitúa la película."),
    "The Background Extras Couldn't Handle This Hilarious Key & Peele Skit":
        ("bajo", "Humor de sketch anglosajón, todo hablado."),
    "Willem Dafoe really went full Green Goblin on Pedro Pascal":
        ("medio", "Dos nombres fuertes, pero el momento es de promoción."),
    "In Twilight (2008). that iconic forest scene where they glide through the trees wasn't CGI":
        ("alto", "Crepúsculo tiene un público enorme aquí y «no era CGI» es el gancho de la casa."),
    "Legendary Interaction Between Jackie Chan & Native Americans - Shanghai Noon (2000)":
        ("alto", "Jackie Chan es el mejor reclamo del catálogo: a Tengri le dio 2,1 y 1,3 millones."),
    "Johnny Is Too Good At Playing A Drunk Pirate - Blooper - Dead Men Tell No Tales":
        ("medio", "Otro blooper de Depp: bueno, pero ya hay mejores en la lista."),
    "This Shot Quietly Exposes Fight Club’s Twist About Marla & Tyler - Fight Club (1999) Movie Detail":
        ("alto", "El club de la lucha ya le rindió 1,1 millones a Tengri con otra escena."),
    "The Mustache Man - Captain America (2011)":
        ("bajo", "Chiste visual demasiado pequeño para sostener un short."),
    "Ryan Reynolds’ \"Suspicious\" Response - Audience Q&A – SNL50":
        ("bajo", "Respuesta en inglés en un programa que aquí no se ve."),
    "The VFX team vs. Justice Smith - D&D: Honor Among Thieves (2023)":
        ("bajo", "De nicho."),
    "The subtle character details you missed - Inglourious Basterds (2009)":
        ("medio", "Análisis interesante, pero hay que explicarlo mucho."),
    "In X-Men: First Class (2011). Magneto reminds Emma Frost that while diamonds are hard":
        ("medio", "El golpe está en la frase, y traducida pierde filo."),
    "This Hand Gesture in Inglourious Basterds (2009) Reveals Everything":
        ("alto", "El gesto de los dedos: se entiende sin idioma y es de las escenas más célebres que hay."),
    "Cap’s Backflip Was 100% PURE Athleticism 🤸‍♂️🔥":
        ("medio", "Marvel y proeza física, aunque el titular ya lo cuenta todo."),
    "Johnny Depp & Jack Blooper - Pirates Of The Caribbean Dead Men Tell No Tales":
        ("bajo", "Tercer blooper de la misma saga: satura."),
    "Wrong guy. wrong grave - D&D Honor Among Thieves (2023)":
        ("bajo", "De nicho."),
    "Nightcrawler In Dark Phoenix Is Officially The Most Terrifying Version Of The Character":
        ("medio", "Secuencia visual buena dentro de una película que gustó poco."),
    "Outfit Detail You Probably Missed In Hostiles (2017)":
        ("bajo", "Película sin recorrido y detalle mínimo."),
    "The moment Swoosie Kurtz actually broke Jim Carrey with a roast - Liar Liar (1997) Blooper":
        ("medio", "Mentiroso compulsivo se conoce aquí, pero la pulla va en inglés."),
    "Why The Ending Of Texas Chainsaw Is Actually The Darkest Moment In Horror History":
        ("medio", "El terror clásico funciona; el título promete análisis, no imagen."),
    "Everything Vanished Except The Cosmic Pager - Avengers: Infinity War":
        ("medio", "Detalle majo para quien ya vio la película."),
    "Robin Williams Delivers A Joke So Fast That Conan Doesn't Even Finish His Sentence":
        ("bajo", "Chiste en inglés a toda velocidad: imposible de trasladar."),
    "Terry Crew's Dancing Scene Is Legendary To This Day - White Chicks":
        ("alto", "Es un meme universal: se entiende sin una palabra y ya se comparte solo."),
    "Sigourney Weaver: Real Life Baller - Alien: Resurrection Behind The Scenes":
        ("alto", "Enceste real de espaldas, en una toma. No hay nada que explicar."),
    "Why \"The Impossible\" Only Had One Shot To Film The Tsunami Scene":
        ("alto", "Película española de Bayona: aquí juegas en casa, y es un «cómo se hizo» de los buenos."),
    "Smoke and Stack’s Suits Tell Their Story -- Sinners (2025)":
        ("medio", "Detalle fino de una película demasiado reciente."),
    "Ryan Gosling Is The Perfect Choice For Ghost Rider":
        ("bajo", "Especulación de reparto."),
    "Sam Witwer’s Kenobi! Scream Darth Maul Recording":
        ("bajo", "Muy de nicho y en inglés."),
    "The Hidden Meaning Behind Jack Sparrow’s Hat. Coat. and Weapons - Pirates of The Caribbean":
        ("medio", "Piratas siempre funciona, pero esto es un vídeo explicado."),
    "Harry Potter Corrects Voldemort's Spell - Parody":
        ("bajo", "Parodia hablada en inglés."),
    "In Pirates of the Caribbean At Worlds End. Barbossa's Hat Kept Getting Blown Off By The Wind":
        ("bajo", "Anécdota menor."),
    "Why The Cast Of Apocalypto (2006) Felt So Real":
        ("medio", "Apocalypto tira, pero esto ya es la tercera pieza sobre lo mismo."),
    "Explosion Scene With The Joker - Deleted Scene":
        ("medio", "El Joker vende siempre; la escena eliminada, menos."),
    "They Ran So Differently In Insurgent (2015) 💀":
        ("bajo", "Burla de una saga que aquí se apagó."),
    "James Earl Jones Used To Stutter - The Angriest Man in Brooklyn (2014)":
        ("medio", "Gran dato —es la voz de Darth Vader—, pero en España esa voz es la de Constantino Romero."),
    "Peeta's Smartest Moment In The Hunger Games":
        ("medio", "Saga masiva, momento correcto sin ser espectacular."),
    "Bullet Train Movie Detail About Every Assassin":
        ("medio", "Película conocida, detalle que hay que explicar."),
    "You can't \"unhear\" it - D&D: Honor Among Thieves (2023)":
        ("bajo", "Depende de oír algo concreto en inglés."),
    "Ryan Reynolds Roasted The Rock’s Hairnet - Red Notice (2021)":
        ("bajo", "Pulla verbal en inglés."),
}
