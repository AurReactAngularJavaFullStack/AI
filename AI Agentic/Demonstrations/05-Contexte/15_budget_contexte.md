# 15 — Budget de contexte : démonstrations

> Fiche : [15 — Budget de contexte](<../../Images/05-Contexte/15_budget_contexte.md>) · Image : `15_budget_contexte.jpg` · Leçon : [Étape 13 ter — Ingénierie du contexte](<../../04-Contexte-Similarite-et-Memoire/13c-Contexte-Definitions-Fondamentaux.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
B_{\text{disponible}} = B_{\text{total}} - B_{\text{instructions}} - B_{\text{historique}} - B_{\text{sortie}}
$$

Tout ce que l'on envoie au modèle prend des tokens dans une fenêtre de taille fixe. Ce qui reste, B disponible, est la place pour les documents et les résultats d'outils du tour.

## Les symboles, un par un

$$
B_{\text{total}}
$$

La taille de la fenêtre de contexte du modèle, en tokens (entrée et sortie comprises chez la plupart des fournisseurs). Entier > 0, par exemple 200 000. La leçon de l'étape 13 ter l'écrit B. Variable Python : `total`.

$$
B_{\text{instructions}} = n_0
$$

Le préfixe fixe : définitions d'outils, prompt système, règles. Il est renvoyé à chaque tour. Entier ≥ 0, en tokens. La leçon l'écrit n₀. Variable Python : `instructions`, ou `n0`.

$$
B_{\text{historique}}
$$

Les tours déjà accumulés : messages, appels d'outils et leurs résultats. Entier ≥ 0, en tokens ; il grandit à chaque tour. Variable Python : `historique`.

$$
B_{\text{sortie}}
$$

La réserve de sortie : les tokens que le modèle doit pouvoir écrire, fixés par le paramètre `max_tokens`. Entier > 0. La leçon l'écrit nₛₒᵣₜᵢₑ. Variable Python : `sortie`.

$$
B_{\text{disponible}}
$$

La place qui reste pour les documents et résultats d'outils du tour. Entier, en tokens ; s'il est négatif, la requête ne tient pas. Variable Python : la valeur renvoyée par `disponible(...)`.

$$
B_{\text{documents}}
$$

Les tokens des documents que l'on veut injecter à ce tour (RAG, mémoire, pièces d'un dossier). Entier ≥ 0. Variable Python : somme des tailles dans `docs`.

$$
\Delta
$$

Les tokens ajoutés à l'historique à chaque tour (un appel d'outil et son résultat). Entier > 0. Variable Python : `delta`.

$$
t, \quad T, \quad T_{\max}
$$

t est le numéro du tour (1, 2, …), T le nombre total de tours d'une conversation, Tₘₐₓ le plus grand nombre de tours qui tient dans la fenêtre sans gestion du contexte. Entiers ≥ 1. Variables Python : `t`, `T`, valeur de `t_max(...)`.

$$
M, \quad r
$$

Pour la fenêtre glissante : M est le nombre de tours récents gardés en entier, r la taille du résumé qui remplace les tours plus anciens. Entiers ≥ 0, en tours et en tokens. Variables Python : `M`, `resume`.

## Le mécanisme, avant les preuves

La formule ne fait que des soustractions : elle part de la fenêtre entière et retire, un bloc après l'autre, ce qui est déjà réservé. Le premier bloc retiré, les instructions, est fixe : il coûte la même chose à chaque tour. Le deuxième, l'historique, grandit à chaque tour d'environ Δ tokens : c'est lui qui finit par manger la place. Le troisième, la réserve de sortie, n'est pas encore écrit au moment de l'appel, mais il faut le retirer quand même, parce que la fenêtre compte aussi les tokens que le modèle produira : oublier cette réserve, c'est accepter une réponse coupée au milieu. Ce qui reste est la seule place où les documents du tour peuvent entrer. Une soustraction a une propriété simple : chaque token ajouté à un bloc retire exactement un token de place, sans effet de seuil ni de pondération. Mais comme l'historique est renvoyé à chaque tour, un token qui y entre est payé à tous les tours suivants : c'est ce qui rend la facture quadratique (démonstration 3). La formule a la forme d'un budget, et non d'un ratio, parce que la contrainte est dure : une requête qui dépasse d'un seul token est refusée par l'API.

Petit film chiffré, sur l'exemple de la fiche. On part de 200 000 tokens. On retire les instructions : 200 000 − 6 000 = 194 000. On retire l'historique : 194 000 − 40 000 = 154 000. On retire la réserve de sortie : 154 000 − 8 000 = 146 000 tokens disponibles. Second film, sur une conversation qui avance avec Δ = 2 500 : au tour 1, l'historique est vide et il reste 200 000 − 6 000 − 8 000 = 186 000 tokens ; au tour 2, 186 000 − 2 500 = 183 500 ; au tour 11, 186 000 − 10 × 2 500 = 161 000 ; au tour 75, 186 000 − 74 × 2 500 = 1 000, et au tour 76 la place deviendrait négative. En Java, c'est le dimensionnement d'un tas JVM : la mémoire maximale moins ce qui est réservé au code et aux piles laisse la place aux objets, et on ne la remplit pas jusqu'au dernier octet.

## Démonstration 1 — Une requête tient si et seulement si les documents tiennent dans le reste

**Ce qu'on démontre.** La fenêtre d'un appel contient exactement les instructions, l'historique, les documents et la réserve de sortie. Alors :

$$
B_{\text{instructions}} + B_{\text{historique}} + B_{\text{documents}} + B_{\text{sortie}} \le B_{\text{total}} \iff B_{\text{documents}} \le B_{\text{disponible}}
$$

Si B disponible est négatif, aucune requête ne tient, même sans document.

**L'idée.** On fait passer trois des quatre blocs de l'autre côté de l'inégalité : ce qui reste à droite est, par définition, B disponible.

**La preuve, pas à pas.**

**Étape 1.** On part de la condition d'acceptation de l'API : la somme des quatre blocs ne dépasse pas la fenêtre.

**Étape 2.** On soustrait B instructions, B historique et B sortie des deux membres ; soustraire la même quantité des deux côtés conserve l'inégalité :

$$
B_{\text{documents}} \le B_{\text{total}} - B_{\text{instructions}} - B_{\text{historique}} - B_{\text{sortie}}
$$

**Étape 3.** On reconnaît à droite la définition de B disponible. Chaque étape étant une équivalence (on peut rajouter les mêmes quantités pour revenir en arrière), on a bien « si et seulement si ».

**Étape 4.** Si B disponible < 0, l'inégalité B documents ≤ B disponible est impossible, puisque B documents ≥ 0. ∎

**Vérification chiffrée.** Avec 200 000, 6 000, 40 000 et 8 000, B disponible = 146 000. Des documents de 140 000 tokens tiennent (140 000 ≤ 146 000) ; des documents de 150 000 ne tiennent pas, et en effet 6 000 + 40 000 + 150 000 + 8 000 = 204 000 > 200 000. Contre-exemple quand on oublie la réserve : on calcule 200 000 − 6 000 − 40 000 = 154 000 et l'on injecte 150 000 tokens ; la requête part avec 196 000 tokens d'entrée, il ne reste que 4 000 tokens pour une réponse qui en demandait 8 000, et elle est coupée à mi-parcours.

**Ce que la preuve révèle du mécanisme.** Tous les blocs sont interchangeables : un token de moins dans l'historique donne exactement un token de plus aux documents. La place des documents est donc ce qui reste après les engagements, jamais l'inverse.

**Conséquence pour un agent.** L'assembleur de contexte calcule B disponible avant de choisir les documents ; si la valeur est négative, il compacte l'historique ou lève une erreur explicite, au lieu d'envoyer une requête que l'API refusera.

## Démonstration 2 — Le nombre maximal de tours d'une boucle

**Ce qu'on démontre.** Si chaque tour ajoute Δ tokens à l'historique, qui part de zéro, le tour t envoie n₀ + (t − 1)Δ tokens d'entrée, et le plus grand nombre de tours qui tiennent est

$$
T_{\max} = \left\lfloor \frac{B_{\text{total}} - n_0 - B_{\text{sortie}}}{\Delta} \right\rfloor + 1
$$

Hypothèses : Δ > 0 et B total − n₀ − B sortie ≥ 0 (sinon aucun tour ne tient). Si l'on injecte en plus d documents à chaque tour, on remplace B sortie par B sortie + d.

**L'idée.** La condition « le tour t tient » est une inégalité linéaire en t ; le plus grand entier qui la vérifie est une partie entière.

**La preuve, pas à pas.**

**Étape 1.** Au tour t, t − 1 tours ont déjà été ajoutés, donc l'historique vaut (t − 1)Δ. Le tour tient si l'entrée et la réserve tiennent dans la fenêtre :

$$
n_0 + (t - 1)\Delta + B_{\text{sortie}} \le B_{\text{total}}
$$

**Étape 2.** On isole t − 1, en divisant par Δ > 0, ce qui conserve le sens :

$$
t - 1 \le \frac{B_{\text{total}} - n_0 - B_{\text{sortie}}}{\Delta}
$$

**Étape 3.** t − 1 est un entier ; le plus grand entier inférieur ou égal à un réel x est sa partie entière ⌊x⌋. Le plus grand t qui convient vérifie donc t − 1 = ⌊x⌋, soit t = ⌊x⌋ + 1. ∎

**Vérification chiffrée.** B total = 200 000, n₀ = 6 000, B sortie = 8 000, Δ = 2 500 : x = 186 000/2 500 = 74,4, ⌊x⌋ = 74, Tₘₐₓ = 75. Contrôle direct : au tour 75, 6 000 + 74 × 2 500 + 8 000 = 199 000 ≤ 200 000 ; au tour 76, 6 000 + 75 × 2 500 + 8 000 = 201 500 > 200 000. Contre-exemple de l'oubli du « + 1 » : écrire Tₘₐₓ = ⌊x⌋ = 74 refuserait un tour qui tient, parce que le tour 1 n'a pas encore d'historique.

**Ce que la preuve révèle du mécanisme.** Tₘₐₓ est inversement proportionnel à Δ : diviser Δ par deux (résultats d'outils tronqués) double presque le nombre de tours. n₀ et B sortie ne jouent que par leur somme, retirée une fois pour toutes.

**Conséquence pour un agent.** Le premier levier pour allonger une boucle n'est pas une plus grande fenêtre, mais un Δ plus petit : tronquer les résultats d'outils, effacer les anciens, ou confier une sous-tâche à un sous-agent.

## Démonstration 3 — L'entrée cumulée croît comme un carré

**Ce qu'on démontre.** Sans gestion du contexte, chaque tour renvoie tout l'historique, et l'entrée cumulée sur T tours vaut

$$
\sum_{t=1}^{T} \big( n_0 + (t - 1)\Delta \big) = T n_0 + \Delta \frac{T (T - 1)}{2}
$$

**L'idée.** On paie n₀ à chaque tour, et l'on paie de nouveau, à chaque tour, tout ce qui a été ajouté avant : le premier ajout est payé T − 1 fois, le dernier zéro fois.

**La preuve, pas à pas.**

**Étape 1.** On sépare la somme en deux, parce qu'une somme de sommes est la somme des sommes :

$$
\sum_{t=1}^{T} \big( n_0 + (t - 1)\Delta \big) = T n_0 + \Delta \sum_{t=0}^{T-1} t
$$

le premier terme parce que n₀ est répété T fois, le second en posant t − 1 comme nouvel indice.

**Étape 2.** On calcule S = 0 + 1 + … + (T − 1). On l'écrit deux fois, à l'endroit et à l'envers, et l'on additionne terme à terme : chaque paire vaut (T − 1), et il y a T paires :

$$
2S = T (T - 1) \quad\Longrightarrow\quad S = \frac{T (T - 1)}{2}
$$

∎

**Vérification chiffrée.** T = 30, n₀ = 6 000, Δ = 2 500 : S = 30 × 29/2 = 435, et l'entrée cumulée vaut 30 × 6 000 + 2 500 × 435 = 180 000 + 1 087 500 = 1 267 500 tokens. Le programme refait la somme tour par tour et trouve le même nombre. Contre-exemple de l'estimation naïve « 30 tours de 6 000 tokens » : 180 000 tokens, sept fois moins que la réalité.

**Ce que la preuve révèle du mécanisme.** Le terme en T² vient du produit « un ajout × le nombre de tours restants ». Doubler T multiplie environ par quatre le terme d'historique : de 30 à 60 tours, il passe de 1 087 500 à 2 500 × 60 × 59/2 = 4 425 000.

**Conséquence pour un agent.** Une boucle longue sans gestion du contexte coûte de plus en plus cher par tour : on fixe un plafond de tours, ou un mécanisme qui rend le coût par tour constant (démonstration 4).

## Démonstration 4 — Une fenêtre glissante rend le coût linéaire

**Ce qu'on démontre.** On garde en entier les M derniers tours et l'on remplace les plus anciens par un résumé de r tokens. Pour T ≥ M + 1, l'entrée cumulée vaut exactement

$$
C_M(T) = (M + 1)\, n_0 + \Delta\, \frac{M (M + 1)}{2} + (T - M - 1)\,(n_0 + M \Delta + r)
$$

et elle croît linéairement en T, de n₀ + MΔ + r par tour.

**L'idée.** Tant que l'historique a au plus M tours, rien ne change ; au-delà, chaque tour envoie le préfixe, M tours et un résumé : une taille constante.

**La preuve, pas à pas.**

**Étape 1.** Aux tours t = 1 à M + 1, l'historique contient t − 1 ≤ M tours : on applique la démonstration 3 avec T = M + 1, ce qui donne (M + 1) n₀ + Δ M(M + 1)/2.

**Étape 2.** Aux tours t = M + 2 à T, il y a T − M − 1 tours, et chacun envoie n₀ + MΔ + r, parce que l'historique est réduit à M tours plus le résumé.

**Étape 3.** On additionne les deux morceaux. Le premier ne dépend pas de T, le second est T − M − 1 fois une constante : la croissance est linéaire. ∎

**Vérification chiffrée.** M = 8, r = 800, T = 30 : premier morceau 9 × 6 000 + 2 500 × 36 = 54 000 + 90 000 = 144 000 ; chaque tour suivant coûte 6 000 + 20 000 + 800 = 26 800, et il y en a 21, soit 562 800 ; total 706 800 tokens, contre 1 267 500 sans fenêtre, soit 1,79 fois moins. Contre-exemple de l'hypothèse « résumé de taille fixe » : un résumé qui grandit de 200 tokens à chaque compaction réintroduit un terme en T², et l'économie fond avec la longueur de la conversation.

**Ce que la preuve révèle du mécanisme.** Le rapport entre les deux coûts grandit avec T : à 30 tours la fenêtre divise la facture par 1,79, et l'écart augmente encore à 60 tours, parce qu'on remplace un terme en T² par un terme en T.

**Conséquence pour un agent.** M et r se règlent ensemble : M assez grand pour garder la tâche en cours en entier, r assez court pour rester constant, et une consigne de résumé qui conserve les engagements et les incertitudes.

## Démonstration 5 — Remplir la place par le meilleur score n'est pas optimal

**Ce qu'on démontre.** Choisir, parmi des documents de tailles tᵢ et de scores vᵢ, ceux qui tiennent dans B disponible en maximisant la somme des scores est un problème de sac à dos. Le choix glouton « meilleur score d'abord » peut être strictement moins bon que l'optimum, et le glouton « meilleur score par token d'abord » aussi.

**L'idée.** Un document à fort score mais très long peut bloquer la place de deux documents un peu moins bons qui, ensemble, valent davantage.

**La preuve, pas à pas.**

**Étape 1.** Il suffit d'un contre-exemple. Place : 1 000 tokens ; A (600 tokens, score 0,9), B (500 ; 0,7), C (500 ; 0,65).

**Étape 2.** Le glouton par score prend A (0,9), il reste 1 000 − 600 = 400 tokens : ni B ni C ne tiennent. Total : 0,9.

**Étape 3.** Le choix B + C prend exactement 500 + 500 = 1 000 tokens et vaut 0,7 + 0,65 = 1,35 > 0,9.

**Étape 4.** Le glouton par densité calcule 0,9/600 = 0,0015, 0,7/500 = 0,0014 et 0,65/500 = 0,0013 : il prend aussi A d'abord, et échoue de la même façon. ∎

**Vérification chiffrée.** Le programme essaie les 2³ = 8 combinaisons : la meilleure est (B, C) avec 1,35. Sur l'exercice 5 (place 900 ; A 500 et 0,8 ; B 450 et 0,6 ; C 450 et 0,55), le glouton prend A (0,8) et l'optimum B + C (1,15).

**Ce que la preuve révèle du mécanisme.** La contrainte de place rend les choix dépendants les uns des autres : la valeur d'un document dépend de ce qu'il empêche d'entrer. Aucun tri simple ne capte cette dépendance dans tous les cas.

**Conséquence pour un agent.** Pour une dizaine de candidats, on essaie toutes les combinaisons (2¹⁰ = 1 024) ; au-delà, une programmation dynamique sur les tokens, ou un glouton par densité contrôlé sur un jeu d'essai. Les pièces obligatoires entrent d'abord, hors de toute optimisation (cas 3).

## Démonstration 6 — Sensibilité : ce que coûte un token de plus dans le préfixe ou dans chaque tour

**Ce qu'on démontre.** Sans gestion du contexte, l'entrée cumulée C = T n₀ + Δ T(T − 1)/2 vérifie

$$
\frac{\partial C}{\partial n_0} = T, \qquad \frac{\partial C}{\partial \Delta} = \frac{T (T - 1)}{2}
$$

et ses élasticités, la variation relative de C pour 1 % de variation de n₀ ou de Δ, ont pour somme 1.

**L'idée.** Un token de préfixe est payé à chaque tour ; un token d'ajout par tour est payé à chaque tour suivant. Et comme C est une somme de termes proportionnels à n₀ ou à Δ, multiplier les deux par un même facteur multiplie C par ce facteur.

**La preuve, pas à pas.**

**Étape 1.** C est linéaire en n₀ (coefficient T) et linéaire en Δ (coefficient T(T − 1)/2) : les dérivées partielles sont ces coefficients.

**Étape 2.** L'élasticité par rapport à n₀ vaut (∂C/∂n₀) × n₀/C = T n₀/C ; celle par rapport à Δ vaut Δ T(T − 1)/(2C).

**Étape 3.** Leur somme vaut (T n₀ + Δ T(T − 1)/2)/C = C/C = 1. ∎

**Vérification chiffrée.** T = 30 : un token de plus dans le préfixe coûte 30 tokens d'entrée cumulée, un token de plus par tour en coûte 435. Élasticités : 30 × 6 000/1 267 500 ≈ 0,14201 et 435 × 2 500/1 267 500 ≈ 0,85799, de somme 1. Une hausse de 1 % de Δ (25 tokens) ajoute 435 × 25 = 10 875 tokens ; une hausse de 1 % de n₀ (60 tokens) en ajoute 30 × 60 = 1 800.

**Ce que la preuve révèle du mécanisme.** Sur une conversation longue, presque toute la facture vient de Δ : ici 86 % de la sensibilité. Le préfixe compte peu en volume, mais il est payé plein tarif à chaque tour s'il sort du cache.

**Conséquence pour un agent.** On optimise d'abord la taille des résultats d'outils, puis la stabilité du préfixe (pour le cache), et seulement ensuite sa longueur.

## Exemple simple, à la main

Fenêtre de 200 000 tokens, prompt et outils 6 000, historique 40 000, réserve de sortie 8 000 :

$$
B_{\text{disponible}} = 200\,000 - 6\,000 - 40\,000 - 8\,000 = 146\,000
$$

| Étape | Calcul | Reste |
| --- | --- | --- |
| fenêtre | — | 200 000 |
| moins les instructions | 200 000 − 6 000 | 194 000 |
| moins l'historique | 194 000 − 40 000 | 154 000 |
| moins la réserve de sortie | 154 000 − 8 000 | 146 000 |

Si l'agent veut injecter 10 passages de 12 000 tokens, soit 10 × 12 000 = 120 000 tokens, ils tiennent (120 000 ≤ 146 000) et il reste 26 000 tokens de marge. Avec 13 passages, 156 000 > 146 000 : il faut en retirer au moins 1, parce que 12 × 12 000 = 144 000 tient.

## Cas d'usage complexes, démontrés

### Cas 1 — [RH] Un cabinet RH multi-émirats : l'agent de suivi des dossiers de visa sur 30 tours

**Contexte.** Un cabinet RH présent dans plusieurs émirats fait suivre par un agent les dossiers de visa et de permis de travail : à chaque tour, l'agent interroge un outil (statut MOHRE, contrat, visite médicale, Emirates ID) et ajoute l'appel et son résultat à l'historique. Une conversation type dure 30 tours, et le cabinet en traite 20 000 par mois. La question : faut-il mettre en place une fenêtre glissante ? Les volumes et le prix (3 USD par million de tokens d'entrée) sont illustratifs.

**Données.**

- fenêtre : B total = 200 000 ; préfixe : n₀ = 6 000 ; réserve de sortie : 8 000 ;
- ajout par tour : Δ = 2 500 ; tours par conversation : T = 30 ;
- fenêtre glissante envisagée : M = 8 tours, résumé de r = 800 tokens ;
- prix : 3 USD par million de tokens d'entrée, soit 3 × 3,6725 = 11,0175 AED ;
- conversations par mois : 20 000.

**Calcul pas à pas.**

**Étape 1.** Le nombre maximal de tours (démonstration 2) :

$$
T_{\max} = \left\lfloor \frac{200\,000 - 6\,000 - 8\,000}{2\,500} \right\rfloor + 1 = 74 + 1 = 75
$$

**Étape 2.** L'entrée cumulée sans gestion (démonstration 3) :

$$
30 \times 6\,000 + 2\,500 \times \frac{30 \times 29}{2} = 180\,000 + 1\,087\,500 = 1\,267\,500 \text{ tokens}
$$

**Étape 3.** Avec la fenêtre glissante (démonstration 4) : 144 000 + 21 × 26 800 = 706 800 tokens, soit 1,79 fois moins.

**Étape 4.** Le coût par conversation, arrondi au centime : 1 267 500 × 3/10⁶ = 3,80 USD (13,96 AED) contre 706 800 × 3/10⁶ = 2,12 USD (7,79 AED).

**Étape 5.** L'écart mensuel : (1 267 500 − 706 800) × 20 000 = 560 700 × 20 000 = 11 214 000 000 tokens, soit 11 214 × 3 = 33 642 USD, environ 123 550 AED par mois.

**Décision de l'agent.** Les 30 tours tiennent dans la fenêtre (30 ≤ 75) : la fenêtre glissante n'est pas nécessaire pour que la requête passe, mais elle divise la facture par 1,79. Le cabinet l'adopte, avec une consigne de résumé qui garde les dates d'expiration et les pièces manquantes.

**Contre-calcul.** L'estimation naïve « 30 tours × 6 000 tokens » donne 180 000 tokens par conversation, soit 0,54 USD : sept fois moins que la réalité, et un budget mensuel faux de plusieurs dizaines de milliers d'USD. Sans fenêtre, le cabinet paierait 33 642 USD de plus chaque mois.

**Sensibilité.** Une hausse de 10 % de Δ (2 750 tokens par tour) donne Tₘₐₓ = ⌊186 000/2 750⌋ + 1 = 67 + 1 = 68 et une entrée cumulée de 180 000 + 2 750 × 435 = 1 376 250 tokens sans fenêtre. La valeur de bascule pour la tenue dans la fenêtre est Tₘₐₓ = 75 tours sans gestion ; avec la fenêtre, chaque tour coûte 26 800 tokens, sous les 192 000 disponibles hors réserve, quel que soit le nombre de tours.

**En production.** On suit les tokens d'entrée par conversation (alerte au-dessus de 1 000 000) et la part de la fenêtre occupée par l'historique (alerte au-dessus de 60 %). Les résultats d'outils contiennent des données personnelles de salariés : leur conservation dans les résumés relève de la PDPL hors zones franches financières, et la durée de conservation est à confirmer avec le texte en vigueur.

### Cas 2 — [BTP] Un groupe de construction : lire un cahier des charges de 300 pages, directement ou par sous-agents

**Contexte.** Un groupe de construction sur de grands chantiers à Dubaï doit répondre à 25 questions de ses ingénieurs sur un cahier des charges de 300 pages (gros œuvre, MEP, finitions). Deux architectures sont possibles : injecter tout le cahier à chaque question, ou faire lire chaque lot une seule fois par un sous-agent qui renvoie une fiche de 400 tokens. Les tailles et le prix sont illustratifs.

**Données.**

- fenêtre : 200 000 ; préfixe de l'agent principal : 5 000 ; historique : 3 000 ; réserve de sortie : 4 000 ;
- taille d'une page : 600 tokens ; lots : gros œuvre 120 pages, MEP 110, finitions 70 ;
- préfixe d'un sous-agent : 2 000 ; fiche renvoyée par lot : 400 tokens ; questions : 25 ;
- prix : 3 USD par million de tokens d'entrée.

**Calcul pas à pas.**

**Étape 1.** La place disponible pour l'agent principal, et la taille du cahier :

$$
200\,000 - 5\,000 - 3\,000 - 4\,000 = 188\,000, \qquad 300 \times 600 = 180\,000 \text{ tokens}
$$

Le cahier tient, avec 8 000 tokens de marge.

**Étape 2.** Lecture directe : chaque question envoie 5 000 + 3 000 + 180 000 = 188 000 tokens, soit 25 × 188 000 = 4 700 000 tokens.

**Étape 3.** Sous-agents : la lecture unique coûte (2 000 + 72 000) + (2 000 + 66 000) + (2 000 + 42 000) = 186 000 tokens ; chaque question n'envoie plus que 5 000 + 3 000 + 3 × 400 = 9 200 tokens, soit 25 × 9 200 = 230 000 ; total 416 000 tokens.

**Étape 4.** Le rapport et les coûts : 4 700 000/416 000 ≈ 11,3 ; 14,10 USD contre 1,25 USD (arrondi au centime de 1,248).

**Décision de l'agent.** Le groupe adopte les sous-agents : onze fois moins de tokens, et un contexte de 9 200 tokens où chaque fiche est lue en entier, au lieu d'un passage utile noyé au milieu de 180 000 tokens.

**Contre-calcul.** Le contrôle naïf « le cahier fait moins que la fenêtre » oublie les autres blocs. Pour un cahier de 320 pages (192 000 tokens), il conclut « 192 000 < 200 000, ça tient » ; or B disponible vaut 188 000 : la requête dépasse de 4 000 tokens et l'API la refuse, ou la réserve de sortie est rognée et la réponse est coupée.

**Sensibilité.** La lecture directe cesse de tenir au-delà de 188 000/600 ≈ 313,3 pages, donc à partir de 314 pages : valeur de bascule 313 pages. Côté coût, les sous-agents sont moins chers dès que 188 000 Q > 186 000 + 9 200 Q, soit Q > 186 000/178 800 ≈ 1,04 : dès la deuxième question.

**En production.** On suit les tokens par question et la marge de B disponible, avec une alerte si la marge passe sous 10 % de la fenêtre, et l'on vérifie sur un échantillon que les fiches des sous-agents citent les pénalités et délais du cahier. Les clauses de pénalité et de retenue sont propres à chaque marché et restent à confirmer avec le contrat en vigueur.

### Cas 3 — [BANQUE] Une banque de détail de Dubaï : choisir les pièces d'un dossier KYC qui tiennent dans la place

**Contexte.** Une banque de détail de Dubaï fait préparer par un agent l'avis KYC d'un client entreprise. Plutôt que d'injecter les 40 pièces du dossier, l'agent reçoit leur liste et charge celles qui tiennent dans la place restante. Sept pièces candidates ont une taille et un score d'utilité ; quatre sont obligatoires pour la politique interne de la banque (statuts, extrait du registre, pièces d'identité des deux bénéficiaires effectifs). Les tailles et scores sont illustratifs.

**Données.**

- fenêtre : 128 000 ; instructions (outils et règles KYC) : 12 000 ; historique : 70 000 ; réserve de sortie : 16 000 ;

| Pièce | Tokens | Score | Obligatoire |
| --- | --- | --- | --- |
| statuts | 9 000 | 0,9 | oui |
| extrait du registre | 4 000 | 0,8 | oui |
| identité bénéficiaire 1 | 3 000 | 0,85 | oui |
| identité bénéficiaire 2 | 3 000 | 0,8 | oui |
| relevés bancaires 12 mois | 16 000 | 0,95 | non |
| organigramme du groupe | 5 000 | 0,6 | non |
| rapport annuel | 14 000 | 0,7 | non |

**Calcul pas à pas.**

**Étape 1.** La place disponible :

$$
128\,000 - 12\,000 - 70\,000 - 16\,000 = 30\,000 \text{ tokens}
$$

**Étape 2.** Le glouton par score prend les relevés (16 000, 0,95 ; reste 14 000), les statuts (9 000, 0,9 ; reste 5 000), l'identité 1 (3 000, 0,85 ; reste 2 000), puis plus rien ne tient : score 2,7, et l'extrait du registre et l'identité 2 manquent.

**Étape 3.** Les pièces obligatoires d'abord : 9 000 + 4 000 + 3 000 + 3 000 = 19 000 tokens, score 3,35, reste 11 000. Parmi les facultatives, seul l'organigramme tient (5 000) : total 24 000 tokens, score 3,95.

**Étape 4.** Le programme essaie les 2⁷ = 128 combinaisons sans contrainte : l'optimum vaut aussi 3,95, avec les mêmes cinq pièces.

**Décision de l'agent.** L'agent charge les quatre pièces obligatoires et l'organigramme (24 000 tokens, score 3,95), et note dans son avis que les relevés et le rapport annuel n'ont pas été lus.

**Contre-calcul.** Le glouton par score aurait produit un avis KYC sans l'extrait du registre ni l'identité du second bénéficiaire effectif, avec un score de 2,7 au lieu de 3,95 : un avis incomplet sur le point que la conformité contrôle en premier.

**Sensibilité.** À 31 000 tokens disponibles, l'optimum sans contrainte change : il remplace les statuts par les relevés (registre, deux identités, relevés et organigramme, score 4,0 > 3,95) et laisserait de côté une pièce obligatoire. La contrainte « obligatoires d'abord » doit donc être explicite. Avec cette contrainte, les relevés n'entrent qu'à partir de 19 000 + 16 000 = 35 000 tokens disponibles (score 4,3) : c'est la valeur de bascule, atteignable en compactant 5 000 tokens d'historique.

**En production.** On journalise les pièces lues et non lues pour chaque avis, avec une alerte si une pièce obligatoire manque, et l'on suit la marge de place. Les exigences KYC de la CBUAE pour une entreprise cliente sont à confirmer avec le texte en vigueur ; la liste des pièces obligatoires ci-dessus est une politique interne illustrative.

### Cas 4 — [ASSUR] Un assureur auto et santé : la réserve de sortie d'un rapport de sinistre

**Contexte.** Un assureur auto et santé fait rédiger par un agent un rapport de décision pour chaque sinistre auto : analyse, décision, clause appliquée. Le modèle choisi a une fenêtre de 32 000 tokens. Les rapports mesurés font jusqu'à 3 200 tokens au 95e centile, alors que la réserve de sortie était réglée à 2 000 ; 30 % des rapports dépassaient cette réserve sur 5 000 sinistres par mois. Les tailles et volumes sont illustratifs.

**Données.**

- fenêtre : 32 000 ; instructions : 3 500 ; historique : 6 000 ;
- documents du dossier (police, constat, devis du garage) : 18 000 ;
- réserve actuelle : 2 000 ; réserve proposée : 3 500 (95e centile 3 200 plus une marge) ;
- sinistres par mois : 5 000 ; part des rapports coupés : 30 % ; une relance coûte 25 000 tokens d'entrée et 10 minutes de gestionnaire ; prix : 3 USD par million de tokens.

**Calcul pas à pas.**

**Étape 1.** La place avec la réserve actuelle : 32 000 − 3 500 − 6 000 − 2 000 = 20 500, et les documents tiennent (18 000 ≤ 20 500).

**Étape 2.** La place avec la réserve proposée :

$$
32\,000 - 3\,500 - 6\,000 - 3\,500 = 19\,000 \ge 18\,000
$$

Les documents tiennent encore, avec 1 000 tokens de marge.

**Étape 3.** Le coût des rapports coupés avec l'ancienne réserve : 0,3 × 5 000 = 1 500 relances par mois, soit 1 500 × 25 000 = 37 500 000 tokens (112,50 USD) et 1 500 × 10/60 = 250 heures de gestionnaire.

**Décision de l'agent.** L'assureur passe la réserve à 3 500 tokens : la requête tient toujours, et les rapports ne sont plus coupés avant la décision et la clause appliquée, qui viennent en fin de texte.

**Contre-calcul.** Avec la réserve de 2 000 tokens, un rapport de 3 200 tokens perd ses 1 200 derniers tokens, c'est-à-dire la décision et sa justification. Le coût direct en tokens est faible (112,50 USD par mois), mais les 250 heures de gestionnaire et les décisions sans clause citée sont le vrai prix.

**Sensibilité.** Avec la réserve de 3 500, les documents ne doivent pas dépasser 19 000 tokens : un second devis de garage de 1 500 tokens (19 500) ne tient plus, et une hausse de 10 % des documents (19 800) non plus. La valeur de bascule est 19 000 tokens de documents, soit +5,56 % par rapport aux 18 000 actuels ; au-delà, l'agent doit résumer l'historique ou le devis avant l'appel.

**En production.** On suit le taux de réponses arrêtées par la limite de sortie, avec une alerte au-dessus de 1 %, et la marge de B disponible par dossier. L'assurance est supervisée par la CBUAE ; les exigences de motivation d'une décision de sinistre sont à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Fenêtre 128 000, instructions 4 000, historique 70 000, sortie 16 000. Calculer B disponible.

**Exercice 2.** Calculer Tₘₐₓ pour B total = 128 000, n₀ = 5 000, B sortie = 8 000, Δ = 2 500.

**Exercice 3.** Calculer l'entrée cumulée sur 10 tours avec n₀ = 3 000 et Δ = 1 000.

**Exercice 4.** Démontrer que 1 + 2 + … + n = n(n + 1)/2.

**Exercice 5.** Place 900 tokens ; documents A (500, 0,8), B (450, 0,6), C (450, 0,55). Quel choix est optimal ?

**Exercice 6 (cas modifié).** Dans le cas 1, chaque tour ajoute désormais Δ = 3 000 tokens. Recalculer Tₘₐₓ, l'entrée cumulée sur 30 tours sans gestion et avec la fenêtre glissante (M = 8, r = 800).

**Exercice 7 (trouver l'erreur).** Un collègue écrit : « fenêtre 200 000, instructions 6 000, historique 40 000 : il reste 154 000 tokens, j'injecte 150 000 tokens de documents ». Trouver l'erreur et dire ce qui se passe.

**Exercice 8 (redémontrer de mémoire).** Redémontrer la formule de Tₘₐₓ, en justifiant le « + 1 » et la partie entière.

## Corrigé

**Exercice 1.** On retire les blocs un par un : 128 000 − 4 000 = 124 000 ; 124 000 − 70 000 = 54 000 ; 54 000 − 16 000 = 38 000 tokens disponibles.

**Exercice 2.** x = (128 000 − 5 000 − 8 000)/2 500 = 115 000/2 500 = 46, entier, donc ⌊x⌋ = 46 et Tₘₐₓ = 47. Contrôle : au tour 47, 5 000 + 46 × 2 500 + 8 000 = 128 000 ≤ 128 000.

**Exercice 3.** La somme 0 + 1 + … + 9 vaut 10 × 9/2 = 45, donc 10 × 3 000 + 1 000 × 45 = 30 000 + 45 000 = 75 000 tokens.

**Exercice 4.** On écrit S = 1 + 2 + … + n et S = n + (n − 1) + … + 1. En additionnant terme à terme, chacune des n paires vaut n + 1 : 2S = n(n + 1), donc S = n(n + 1)/2.

**Exercice 5.** A seul : 500 tokens, score 0,8, et il reste 400 tokens où ni B ni C ne tiennent. B + C : 450 + 450 = 900 tokens, score 0,6 + 0,55 = 1,15. A + B ou A + C font 950 tokens et ne tiennent pas. Le choix optimal est B + C, que le glouton par score manque.

**Exercice 6.** Tₘₐₓ = ⌊186 000/3 000⌋ + 1 = 62 + 1 = 63. Sans gestion : 30 × 6 000 + 3 000 × 435 = 180 000 + 1 305 000 = 1 485 000 tokens. Avec la fenêtre : 9 × 6 000 + 3 000 × 36 = 54 000 + 108 000 = 162 000, puis 21 × (6 000 + 8 × 3 000 + 800) = 21 × 30 800 = 646 800, total 808 800 tokens. La décision ne change pas : 30 ≤ 63 et la fenêtre divise la facture par 1 485 000/808 800 ≈ 1,84.

**Exercice 7.** Il a oublié la réserve de sortie de 8 000 tokens : B disponible vaut 154 000 − 8 000 = 146 000, et 150 000 > 146 000. La requête contient 196 000 tokens d'entrée, il ne reste que 4 000 tokens pour une réponse prévue à 8 000 : elle est coupée, ou l'API refuse l'appel. Il faut retirer au moins 4 000 tokens de documents.

**Exercice 8.** Au tour t, l'historique vaut (t − 1)Δ, et le tour tient si n₀ + (t − 1)Δ + B sortie ≤ B total. On divise par Δ > 0 : t − 1 ≤ (B total − n₀ − B sortie)/Δ = x. Le plus grand entier t − 1 qui vérifie cela est ⌊x⌋ (partie entière, parce que t − 1 est entier), d'où t = ⌊x⌋ + 1 ; le « + 1 » vient de ce que le tour 1 n'a pas d'historique.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`disponible(total, instructions, historique, sortie)`** — Cette fonction se comporte comme un intendant qui répartit les places d'une salle de réception avant l'arrivée des invités : elle reçoit la taille de la fenêtre, puis ce que prennent déjà les instructions, l'historique et la réserve de sortie, refuse par une `ValueError` toute taille négative, et retranche les trois réservations du total. Elle renvoie la place laissée aux documents, qui peut être négative quand rien ne tient, par exemple 146 000 tokens pour une fenêtre de 200 000 avec 6 000 d'instructions, 40 000 d'historique et 8 000 de sortie ; tous les cas s'en servent pour savoir si une requête passe.

**`t_max(total, n0, sortie, delta)`** — On la voit en horloger qui compte combien de tours de conversation la fenêtre supporte avant de déborder : elle reçoit la taille de la fenêtre, la taille fixe n₀ du premier tour, la réserve de sortie et l'ajout Δ de chaque tour, refuse un Δ nul ou négatif par une `ValueError`, puis calcule le reste B total − n₀ − B sortie. Elle renvoie 0 si ce reste est négatif, faute de quoi la partie entière du reste divisé par Δ, plus 1, puisque le premier tour n'a pas d'historique : 75 tours pour 200 000, 6 000, 8 000 et 2 500, et 0 quand la fenêtre ne fait que 10 000 tokens.

**`cumul(T, n0, delta, M, resume)`** — Cette fonction tient le registre d'un comptable qui additionne, tour après tour, tout ce qu'on a envoyé au modèle : elle reçoit le nombre de tours T, la taille n₀, l'ajout Δ, une fenêtre glissante M facultative et la taille du résumé qui remplace les vieux tours. Pour chaque tour t, elle compte n₀ + (t − 1)Δ tant qu'aucune fenêtre n'est fixée ou que t − 1 ≤ M, puis, au-delà, le plafond n₀ + MΔ augmenté du résumé ; elle renvoie la somme, soit 1 267 500 tokens pour trente tours sans gestion et 706 800 avec une fenêtre de huit tours et un résumé de 800 tokens.

**`cumul_fenetre_ferme(T, n0, delta, M, resume)`** — Celle-ci est le raccourci du mathématicien qui refuse de recompter à la main ce qu'une formule donne d'un coup : elle reçoit les mêmes nombres que `cumul` avec une fenêtre fixée, et renvoie (M + 1)n₀ + ΔM(M + 1)/2 pour les tours qui grandissent encore, plus (T − M − 1) fois le plafond n₀ + MΔ + r pour les tours suivants. Elle n'est valable que pour T ≥ M + 1, la condition de la démonstration 4, et `main` vérifie qu'elle redonne exactement le résultat de `cumul` pour tous les nombres de tours de 9 à 79, dont les 706 800 tokens des trente tours.

**`meilleur_choix(docs, place)`** — On l'imagine en déménageur scrupuleux qui essaie toutes les manières de remplir son camion avant de partir : elle reçoit une liste de documents, chacun avec un nom, une taille en tokens et un score, ainsi que la place disponible, puis parcourt avec `itertools.combinations` toutes les combinaisons, de la vide à la complète, et garde, parmi celles qui tiennent, le couple score total arrondi et noms le plus grand. Elle renvoie ce couple, soit B et C pour un score de 1,35 dans la démonstration 5, là où le glouton s'arrête à A ; le cas 3 l'emploie pour compléter les pièces obligatoires, en sachant qu'elle essaie 2ⁿ combinaisons, 128 pour sept pièces.

**`glouton(docs, place, cle)`** — Cette fonction est le voyageur pressé qui remplit sa valise dans l'ordre où les objets lui tombent sous la main : elle reçoit les documents, la place et une clé de tri, range les documents selon cette clé, puis prend chacun d'eux s'il tient encore, en ajoutant son score et en retranchant sa taille de la place restante, sans jamais revenir sur un choix. Elle renvoie la liste des noms pris, le score arrondi et la place qui reste ; triée par score décroissant ou par densité, elle ne prend que A dans la démonstration 5, et dans le cas 3 elle choisit relevés, statuts et première identité pour un score de 2,7, en oubliant deux pièces obligatoires.

**`cout_usd(tokens)`** — Ce petit caissier convertit un volume de texte en argent : il reçoit un nombre de tokens d'entrée, le multiplie par le prix `PRIX_USD`, fixé à 3 USD par million de tokens dans ce programme à titre illustratif, et divise par un million. Il renvoie le montant en dollars, par exemple 3,80 USD pour les 1 267 500 tokens de trente tours sans gestion, et les quatre cas s'en servent pour traduire chaque économie de tokens en facture, parfois convertie ensuite en dirhams avec le taux `USD_AED` de 3,6725.

**`cas_1_rh_visas()`** — Cette fonction raconte l'agent d'un service de ressources humaines qui accompagne des demandes de visa sur trente tours : elle ne reçoit rien, calcule le nombre maximal de 75 tours, puis l'entrée cumulée de trente tours, 1 267 500 tokens sans gestion contre 706 800 avec une fenêtre de huit tours et un résumé de 800, soit une facture divisée par 1,79, de 3,80 à 2,12 USD. Elle multiplie l'écart par 20 000 conversations, ce qui donne 11 214 000 000 tokens, 33 642 USD ou 123 550 AED par mois, teste un Δ augmenté de 10 %, qui ramène le maximum à 68 tours, imprime la décision en faveur de la fenêtre glissante et renvoie tous ces nombres dans un dictionnaire.

**`cas_2_btp_cahier()`** — On y suit un chantier dont l'agent doit répondre à 25 questions sur un cahier des charges de 300 pages à 600 tokens : la fonction ne reçoit rien, calcule une place de 188 000 tokens qui accueille tout juste le cahier de 180 000, puis compare la lecture directe, 4 700 000 tokens, à des sous-agents qui lisent une seule fois trois lots de 120, 110 et 70 pages pour 186 000 tokens et ne renvoient ensuite que des fiches de 400 tokens, soit 9 200 tokens par question et 416 000 en tout. Elle imprime ce rapport de 11,3, le seuil de 313 pages au-delà duquel le cahier ne tient plus, la bascule à partir d'un peu plus d'une question, et renvoie la décision « sous-agents » avec ses chiffres.

**`cas_3_banque_kyc()`** — Cette fonction met en scène l'agent de conformité d'une banque qui doit monter un dossier d'ouverture de compte avec sept pièces, dont quatre obligatoires, dans une place de 30 000 tokens : elle ne reçoit rien, montre que le glouton par score prend relevés, statuts et première identité pour 2,7 et laisse tomber des pièces obligatoires, puis réserve d'abord les 19 000 tokens des obligatoires, de score 3,35, et complète avec `meilleur_choix`, qui ajoute l'organigramme pour un total de 3,95. Elle montre aussi qu'à 31 000 tokens l'optimum libre sacrifierait les statuts pour un score de 4,0, que les relevés n'entrent qu'à 35 000 tokens, avec un score de 4,3, imprime ces étapes et renvoie le tout.

**`cas_4_assur_reserve()`** — Ici, un assureur voit 30 % des rapports de sinistre coupés parce que la réserve de sortie de 2 000 tokens était trop courte : la fonction ne reçoit rien, calcule la place laissée aux documents dans une fenêtre de 32 000 tokens avant et après le passage de la réserve à 3 500, soit 20 500 puis 19 000, avec une marge de 1 000 sur les 18 000 tokens de documents. Elle chiffre le coût de l'ancienne réserve, 1 500 relances sur 5 000 sinistres, 37 500 000 tokens, 112,50 USD et 250 heures de gestionnaire, puis la hausse de documents que la nouvelle place tolère encore, 5,56 %, imprime la décision et renvoie ces nombres.

**`main()`** — C'est le chef d'orchestre de la fiche : il vérifie d'abord la place de 146 000 tokens de l'exemple et le fait que 150 000 tokens de documents ne tiennent pas, puis le maximum de 75 tours, la somme arithmétique qui donne 1 267 500 tokens, la fenêtre glissante qui les ramène à 706 800, le contre-exemple du glouton et les élasticités 0,14201 et 0,85799 qui somment à 1. Il joue ensuite les quatre cas, recalcule le corrigé des exercices et s'assure qu'un Δ nul est bien refusé ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tout concorde.

**`resume_croissant(T)`** — Cette fonction interne vit à l'intérieur de `main`, comme un témoin à charge qu'on appelle pour un seul interrogatoire : elle reçoit un nombre de tours T et recalcule l'entrée cumulée de la fenêtre glissante de huit tours, mais avec un résumé qui, au lieu de rester à 800 tokens, grossit de 200 tokens à chaque tour au-delà du dixième. Elle renvoie cette somme, et `main` vérifie que le coût du 61ᵉ tour dépasse celui du 31ᵉ, preuve qu'un résumé qui enfle fait repartir la facture à la hausse et que la fenêtre ne plafonne le coût par tour que si le résumé garde une taille fixe.

```python
"""Démonstration 15 — budget de contexte : reste, T_max, somme arithmétique, fenêtre glissante, sac à dos, sensibilité, quatre cas."""
import itertools
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PRIX_USD = 3.0          # USD par million de tokens d'entrée (illustratif)
USD_AED = 3.6725


def disponible(total: int, instructions: int, historique: int, sortie: int) -> int:
    """B_total − B_instructions − B_historique − B_sortie ; négatif si rien ne tient."""
    if min(total, instructions, historique, sortie) < 0:
        raise ValueError("tailles négatives")
    return total - instructions - historique - sortie


def t_max(total: int, n0: int, sortie: int, delta: int) -> int:
    """⌊(B_total − n0 − B_sortie) / Δ⌋ + 1 ; 0 si même le premier tour ne tient pas."""
    if delta <= 0:
        raise ValueError("delta doit être > 0")
    reste = total - n0 - sortie
    return 0 if reste < 0 else reste // delta + 1


def cumul(T: int, n0: int, delta: int, M: int | None = None, resume: int = 0) -> int:
    """Entrée cumulée sur T tours, sans gestion (M = None) ou avec fenêtre glissante de M tours."""
    return sum(n0 + (t - 1) * delta if M is None or t - 1 <= M else n0 + M * delta + resume
               for t in range(1, T + 1))


def cumul_fenetre_ferme(T: int, n0: int, delta: int, M: int, resume: int) -> int:
    """Forme fermée de la démonstration 4, pour T >= M + 1."""
    return (M + 1) * n0 + delta * M * (M + 1) // 2 + (T - M - 1) * (n0 + M * delta + resume)


def meilleur_choix(docs: list[tuple[str, int, float]], place: int) -> tuple[float, tuple[str, ...]]:
    """Essaie toutes les combinaisons qui tiennent ; renvoie (score total, noms)."""
    meilleur = (0.0, ())
    for k in range(len(docs) + 1):
        for combo in itertools.combinations(docs, k):
            if sum(d[1] for d in combo) <= place:
                meilleur = max(meilleur, (round(sum(d[2] for d in combo), 10), tuple(d[0] for d in combo)))
    return meilleur


def glouton(docs: list[tuple[str, int, float]], place: int, cle) -> tuple[list[str], float, int]:
    """Prend les documents dans l'ordre de la clé tant qu'ils tiennent ; renvoie (noms, score, reste)."""
    pris, score = [], 0.0
    for nom, tok, val in sorted(docs, key=cle):
        if tok <= place:
            pris.append(nom)
            score += val
            place -= tok
    return pris, round(score, 10), place


def cout_usd(tokens: int) -> float:
    return tokens * PRIX_USD / 1e6


def cas_1_rh_visas() -> dict:
    """[RH] 30 tours, fenêtre 200 000, n0 6 000, Δ 2 500, sortie 8 000, M = 8, r = 800, 20 000 conversations."""
    tm = t_max(200_000, 6_000, 8_000, 2_500)
    brut, fenetre = cumul(30, 6_000, 2_500), cumul(30, 6_000, 2_500, 8, 800)
    ecart_mois = (brut - fenetre) * 20_000
    res = {"tm": tm, "brut": brut, "fenetre": fenetre, "ratio": brut / fenetre,
           "usd_brut": cout_usd(brut), "usd_fenetre": cout_usd(fenetre),
           "aed_brut": cout_usd(brut) * USD_AED, "aed_fenetre": cout_usd(fenetre) * USD_AED,
           "ecart_mois": ecart_mois, "usd_mois": cout_usd(ecart_mois), "aed_mois": cout_usd(ecart_mois) * USD_AED,
           "tm_10": t_max(200_000, 6_000, 8_000, 2_750), "brut_10": cumul(30, 6_000, 2_750),
           "naif": 30 * 6_000, "par_tour": 6_000 + 8 * 2_500 + 800}
    print(f"Cas 1 [RH] T_max {tm} ; 30 tours : {brut:,} → {fenetre:,} tokens (÷{res['ratio']:.2f}) ;"
          f" {res['usd_brut']:.2f} → {res['usd_fenetre']:.2f} USD ({res['aed_brut']:.2f} → {res['aed_fenetre']:.2f} AED)")
    print(f"  écart mensuel {ecart_mois:,} tokens = {res['usd_mois']:,.0f} USD = {res['aed_mois']:,.0f} AED ;"
          f" Δ + 10 % : T_max {res['tm_10']}, {res['brut_10']:,} tokens ; décision : fenêtre glissante")
    return res


def cas_2_btp_cahier() -> dict:
    """[BTP] 300 pages à 600 tokens ; lots 120 / 110 / 70 pages ; 25 questions ; fiches de 400 tokens."""
    place = disponible(200_000, 5_000, 3_000, 4_000)
    cahier = 300 * 600
    direct = 25 * (5_000 + 3_000 + cahier)
    lecture = sum(2_000 + pages * 600 for pages in (120, 110, 70))
    par_question = 5_000 + 3_000 + 3 * 400
    sous_agents = lecture + 25 * par_question
    pages_max = place // 600
    q_bascule = lecture / ((5_000 + 3_000 + cahier) - par_question)
    choix = "sous-agents" if sous_agents < direct else "lecture directe"
    print(f"Cas 2 [BTP] place {place:,} ; cahier {cahier:,} ; direct {direct:,} ; sous-agents {lecture:,} + 25 × {par_question:,}"
          f" = {sous_agents:,} (÷{direct / sous_agents:.1f}) ; {cout_usd(direct):.2f} contre {cout_usd(sous_agents):.3f} USD")
    print(f"  320 pages : {320 * 600:,} > {place:,} ; bascule {place / 600:.1f} pages ; sous-agents moins chers dès Q > {q_bascule:.2f} ;"
          f" décision : {choix}")
    return {"place": place, "cahier": cahier, "direct": direct, "lecture": lecture, "par_question": par_question,
            "sous_agents": sous_agents, "pages_max": pages_max, "q_bascule": q_bascule, "choix": choix}


def cas_3_banque_kyc() -> dict:
    """[BANQUE] 7 pièces, 4 obligatoires ; place = 128 000 − 12 000 − 70 000 − 16 000."""
    pieces = [("statuts", 9_000, 0.9), ("registre", 4_000, 0.8), ("identite1", 3_000, 0.85),
              ("identite2", 3_000, 0.8), ("releves", 16_000, 0.95), ("organigramme", 5_000, 0.6),
              ("rapport", 14_000, 0.7)]
    obligatoires = {"statuts", "registre", "identite1", "identite2"}
    place = disponible(128_000, 12_000, 70_000, 16_000)
    pris_g, score_g, _ = glouton(pieces, place, lambda d: -d[2])
    oblig = [p for p in pieces if p[0] in obligatoires]
    taille_oblig = sum(p[1] for p in oblig)
    score_oblig = round(sum(p[2] for p in oblig), 10)
    reste = place - taille_oblig
    score_fac, noms_fac = meilleur_choix([p for p in pieces if p[0] not in obligatoires], reste)
    score_contraint = round(score_oblig + score_fac, 10)
    libre = meilleur_choix(pieces, place)
    libre_31 = meilleur_choix(pieces, 31_000)
    bascule = next(P for P in range(place, 60_001, 1_000)
                   if "releves" in meilleur_choix([p for p in pieces if p[0] not in obligatoires], P - taille_oblig)[1])
    score_35 = round(score_oblig + meilleur_choix([p for p in pieces if p[0] not in obligatoires], bascule - taille_oblig)[0], 10)
    print(f"Cas 3 [BANQUE] place {place:,} ; glouton par score {pris_g} = {score_g}")
    print(f"  obligatoires {taille_oblig:,} tokens ({score_oblig}) + {list(noms_fac)} = {score_contraint} ;"
          f" optimum libre {libre[0]} ; décision : obligatoires puis {list(noms_fac)}")
    print(f"  à 31 000 l'optimum libre devient {list(libre_31[1])} = {libre_31[0]}")
    print(f"  relevés admis à {bascule:,} tokens (score {score_35})")
    return {"place": place, "pris_g": pris_g, "score_g": score_g, "taille_oblig": taille_oblig,
            "score_oblig": score_oblig, "noms_fac": noms_fac, "score_contraint": score_contraint, "libre": libre,
            "libre_31": libre_31, "bascule": bascule, "score_35": score_35, "n_combinaisons": 2 ** len(pieces)}


def cas_4_assur_reserve() -> dict:
    """[ASSUR] fenêtre 32 000 ; instructions 3 500 ; historique 6 000 ; documents 18 000 ; réserve 2 000 → 3 500."""
    avant = disponible(32_000, 3_500, 6_000, 2_000)
    apres = disponible(32_000, 3_500, 6_000, 3_500)
    relances = round(0.3 * 5_000)
    tokens_relances = relances * 25_000
    heures = relances * 10 / 60
    marge = apres - 18_000
    hausse_max = apres / 18_000 - 1
    print(f"Cas 4 [ASSUR] place {avant:,} → {apres:,} (marge {marge:,}) ; décision : réserve 3 500")
    print(f"  relances {relances:,} = {tokens_relances:,} tokens ({cout_usd(tokens_relances):.2f} USD) et {heures:.0f} h ;"
          f" bascule documents {apres:,} (+{100 * hausse_max:.2f} %)")
    return {"avant": avant, "apres": apres, "relances": relances, "tokens_relances": tokens_relances,
            "usd": cout_usd(tokens_relances), "heures": heures, "marge": marge, "hausse_max": hausse_max}


def main() -> None:
    # Mécanisme, exemple simple et démonstration 1
    d = disponible(200_000, 6_000, 40_000, 8_000)
    print(f"Démonstration 1 : disponible {d:,} ; 140 000 tient : {140_000 <= d} ; 150 000 tient : {150_000 <= d}"
          f" ({6_000 + 40_000 + 150_000 + 8_000:,} > 200 000)")
    assert d == 146_000 and 200_000 - 6_000 == 194_000 and 194_000 - 40_000 == 154_000 and 154_000 - 8_000 == 146_000
    assert 6_000 + 40_000 + 150_000 + 8_000 == 204_000 and 6_000 + 40_000 + 150_000 == 196_000
    assert 10 * 12_000 == 120_000 and d - 120_000 == 26_000 and 13 * 12_000 == 156_000 and 12 * 12_000 == 144_000
    for tour, attendu in ((1, 186_000), (2, 183_500), (11, 161_000), (75, 1_000)):
        assert disponible(200_000, 6_000, (tour - 1) * 2_500, 8_000) == attendu
    assert disponible(200_000, 6_000, 75 * 2_500, 8_000) < 0
    for total, ins, hist, doc, sortie in ((200_000, 6_000, 40_000, 140_000, 8_000), (128_000, 4_000, 70_000, 40_000, 16_000)):
        assert (ins + hist + doc + sortie <= total) == (doc <= disponible(total, ins, hist, sortie))

    # Démonstration 2
    tm = t_max(200_000, 6_000, 8_000, 2_500)
    print(f"Démonstration 2 : x = {186_000 / 2_500} ; T_max = {tm} ; tour 75 : {6_000 + 74 * 2_500 + 8_000:,} ;"
          f" tour 76 : {6_000 + 75 * 2_500 + 8_000:,}")
    assert 186_000 / 2_500 == 74.4 and tm == 75 and 6_000 + 74 * 2_500 + 8_000 == 199_000 and 6_000 + 75 * 2_500 + 8_000 == 201_500
    assert t_max(10_000, 6_000, 8_000, 2_500) == 0

    # Démonstration 3
    brut = cumul(30, 6_000, 2_500)
    print(f"Démonstration 3 : 30 tours = {30 * 6_000:,} + {2_500 * 435:,} = {brut:,} ; 60 tours, historique {2_500 * 60 * 59 // 2:,}")
    assert brut == 1_267_500 == 30 * 6_000 + 2_500 * 30 * 29 // 2 and 30 * 29 // 2 == 435 and 2_500 * 435 == 1_087_500
    assert 2_500 * 60 * 59 // 2 == 4_425_000 and round(brut / 180_000) == 7
    assert all(sum(range(1, n + 1)) == n * (n + 1) // 2 for n in range(1, 200))              # exercice 4

    # Démonstration 4
    fenetre = cumul(30, 6_000, 2_500, 8, 800)
    print(f"Démonstration 4 : fenêtre M = 8 : {9 * 6_000 + 2_500 * 36:,} + 21 × {6_000 + 8 * 2_500 + 800:,} = {fenetre:,}"
          f" (÷{brut / fenetre:.2f})")
    assert fenetre == 706_800 == cumul_fenetre_ferme(30, 6_000, 2_500, 8, 800) and 9 * 6_000 + 2_500 * 36 == 144_000
    assert 21 * 26_800 == 562_800 and round(brut / fenetre, 2) == 1.79
    for T in range(9, 80):
        assert cumul(T, 6_000, 2_500, 8, 800) == cumul_fenetre_ferme(T, 6_000, 2_500, 8, 800)
    assert cumul(60, 6_000, 2_500) / cumul(60, 6_000, 2_500, 8, 800) > brut / fenetre

    def resume_croissant(T: int) -> int:                  # contre-exemple : le résumé grandit de 200 tokens par tour
        return sum(6_000 + (t - 1) * 2_500 if t - 1 <= 8 else 6_000 + 8 * 2_500 + 800 + 200 * (t - 10)
                   for t in range(1, T + 1))
    assert resume_croissant(61) - resume_croissant(60) > resume_croissant(31) - resume_croissant(30)

    # Démonstration 5
    docs = [("A", 600, 0.9), ("B", 500, 0.7), ("C", 500, 0.65)]
    glouton_score, place = [], 1000
    for nom, tok, score in sorted(docs, key=lambda d: -d[2]):
        if tok <= place:
            glouton_score.append(nom)
            place -= tok
    optimum = meilleur_choix(docs, 1000)
    densite = glouton(docs, 1000, lambda d: -d[2] / d[1])
    print(f"Démonstration 5 : glouton {glouton_score} (score 0,9) ; densité {densite[0]} ; optimal {list(optimum[1])} (score {optimum[0]:.2f})")
    assert glouton_score == ["A"] and place == 400 and optimum[1] == ("B", "C") and round(optimum[0], 2) == 1.35
    assert densite[0] == ["A"] and (0.9 / 600, 0.7 / 500, round(0.65 / 500, 4)) == (0.0015, 0.0014, 0.0013)
    assert 2 ** 10 == 1_024

    # Démonstration 6
    e_n0, e_delta = 30 * 6_000 / brut, 435 * 2_500 / brut
    print(f"Démonstration 6 : ∂C/∂n0 = 30, ∂C/∂Δ = 435 ; élasticités {e_n0:.5f} + {e_delta:.5f} = {e_n0 + e_delta:.0f} ;"
          f" +1 % de Δ → +{cumul(30, 6_000, 2_525) - brut:,} ; +1 % de n0 → +{cumul(30, 6_060, 2_500) - brut:,}")
    assert cumul(30, 6_001, 2_500) - brut == 30 and cumul(30, 6_000, 2_501) - brut == 435
    assert round(e_n0, 5) == 0.14201 and round(e_delta, 5) == 0.85799 and abs(e_n0 + e_delta - 1) < 1e-12
    assert cumul(30, 6_000, 2_525) - brut == 10_875 and cumul(30, 6_060, 2_500) - brut == 1_800 and round(100 * e_delta) == 86

    # Cas
    c1 = cas_1_rh_visas()
    assert c1["tm"] == 75 and c1["brut"] == 1_267_500 and c1["fenetre"] == 706_800 and round(c1["ratio"], 2) == 1.79
    assert round(c1["usd_brut"], 2) == 3.8 and round(c1["usd_fenetre"], 2) == 2.12
    assert round(c1["aed_brut"], 2) == 13.96 and round(c1["aed_fenetre"], 2) == 7.79 and round(3 * USD_AED, 4) == 11.0175
    assert c1["ecart_mois"] == 11_214_000_000 and 1_267_500 - 706_800 == 560_700
    assert round(c1["usd_mois"]) == 33_642 and round(c1["aed_mois"]) == 123_550 and 11_214 * 3 == 33_642
    assert c1["tm_10"] == 68 and 186_000 // 2_750 == 67 and c1["brut_10"] == 1_376_250 and 2_750 * 435 == 1_196_250
    assert c1["naif"] == 180_000 and round(cout_usd(180_000), 2) == 0.54 and c1["par_tour"] == 26_800
    assert c1["par_tour"] <= 200_000 - 8_000 == 192_000

    c2 = cas_2_btp_cahier()
    assert c2["place"] == 188_000 and c2["cahier"] == 180_000 and c2["place"] - c2["cahier"] == 8_000
    assert c2["direct"] == 4_700_000 and 5_000 + 3_000 + 180_000 == 188_000 and c2["lecture"] == 186_000
    assert (2_000 + 72_000, 2_000 + 66_000, 2_000 + 42_000) == (74_000, 68_000, 44_000)
    assert c2["par_question"] == 9_200 and 25 * 9_200 == 230_000 and c2["sous_agents"] == 416_000
    assert round(c2["direct"] / c2["sous_agents"], 1) == 11.3 and round(cout_usd(c2["direct"]), 2) == 14.1
    assert round(cout_usd(c2["sous_agents"]), 3) == 1.248 and round(cout_usd(c2["sous_agents"]), 2) == 1.25
    assert 320 * 600 == 192_000 and 192_000 - c2["place"] == 4_000 and c2["pages_max"] == 313
    assert round(188_000 / 600, 1) == 313.3 and round(c2["q_bascule"], 2) == 1.04 and 188_000 - 9_200 == 178_800
    assert c2["choix"] == "sous-agents"

    c3 = cas_3_banque_kyc()
    assert c3["place"] == 30_000 and c3["pris_g"] == ["releves", "statuts", "identite1"] and c3["score_g"] == 2.7
    assert c3["taille_oblig"] == 19_000 and c3["score_oblig"] == 3.35 and c3["noms_fac"] == ("organigramme",)
    assert c3["score_contraint"] == 3.95 and c3["libre"][0] == 3.95 and 19_000 + 5_000 == 24_000
    assert set(c3["libre"][1]) == {"statuts", "registre", "identite1", "identite2", "organigramme"}
    assert c3["libre_31"][0] == 4.0 and "statuts" not in c3["libre_31"][1] and "releves" in c3["libre_31"][1]
    assert c3["bascule"] == 35_000 and c3["score_35"] == 4.3 and c3["n_combinaisons"] == 128
    assert 30_000 - 16_000 == 14_000 and 14_000 - 9_000 == 5_000 and 5_000 - 3_000 == 2_000 and 35_000 - 30_000 == 5_000

    c4 = cas_4_assur_reserve()
    assert c4["avant"] == 20_500 and c4["apres"] == 19_000 and c4["marge"] == 1_000
    assert c4["relances"] == 1_500 and c4["tokens_relances"] == 37_500_000 and round(c4["usd"], 2) == 112.5
    assert c4["heures"] == 250 and round(100 * c4["hausse_max"], 2) == 5.56 and 3_200 - 2_000 == 1_200
    assert 18_000 + 1_500 == 19_500 > c4["apres"] and round(18_000 * 1.1) == 19_800 > c4["apres"]

    # Corrigé
    print("Corrigé")
    ex5 = meilleur_choix([("A", 500, 0.8), ("B", 450, 0.6), ("C", 450, 0.55)], 900)
    ex6 = (t_max(200_000, 6_000, 8_000, 3_000), cumul(30, 6_000, 3_000), cumul(30, 6_000, 3_000, 8, 800))
    print(f"  ex1 {disponible(128_000, 4_000, 70_000, 16_000):,} ; ex2 {t_max(128_000, 5_000, 8_000, 2_500)} ;"
          f" ex3 {cumul(10, 3_000, 1_000):,} ; ex5 {list(ex5[1])} = {ex5[0]:.2f} ; ex6 {ex6[0]}, {ex6[1]:,}, {ex6[2]:,}"
          f" (÷{ex6[1] / ex6[2]:.2f})")
    assert disponible(128_000, 4_000, 70_000, 16_000) == 38_000 and t_max(128_000, 5_000, 8_000, 2_500) == 47
    assert 5_000 + 46 * 2_500 + 8_000 == 128_000 and cumul(10, 3_000, 1_000) == 75_000 and 10 * 9 // 2 == 45
    assert ex5[1] == ("B", "C") and round(ex5[0], 2) == 1.15
    assert ex6 == (63, 1_485_000, 808_800) and 3_000 * 435 == 1_305_000 and 21 * 30_800 == 646_800
    assert 9 * 6_000 + 3_000 * 36 == 162_000 and round(ex6[1] / ex6[2], 2) == 1.84
    assert 154_000 - 8_000 == 146_000 and 150_000 - 146_000 == 4_000
    try:
        t_max(200_000, 6_000, 8_000, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("delta = 0 aurait dû être refusé")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Démonstration 1 : disponible 146,000 ; 140 000 tient : True ; 150 000 tient : False (204,000 > 200 000)
Démonstration 2 : x = 74.4 ; T_max = 75 ; tour 75 : 199,000 ; tour 76 : 201,500
Démonstration 3 : 30 tours = 180,000 + 1,087,500 = 1,267,500 ; 60 tours, historique 4,425,000
Démonstration 4 : fenêtre M = 8 : 144,000 + 21 × 26,800 = 706,800 (÷1.79)
Démonstration 5 : glouton ['A'] (score 0,9) ; densité ['A'] ; optimal ['B', 'C'] (score 1.35)
Démonstration 6 : ∂C/∂n0 = 30, ∂C/∂Δ = 435 ; élasticités 0.14201 + 0.85799 = 1 ; +1 % de Δ → +10,875 ; +1 % de n0 → +1,800
Cas 1 [RH] T_max 75 ; 30 tours : 1,267,500 → 706,800 tokens (÷1.79) ; 3.80 → 2.12 USD (13.96 → 7.79 AED)
  écart mensuel 11,214,000,000 tokens = 33,642 USD = 123,550 AED ; Δ + 10 % : T_max 68, 1,376,250 tokens ; décision : fenêtre glissante
Cas 2 [BTP] place 188,000 ; cahier 180,000 ; direct 4,700,000 ; sous-agents 186,000 + 25 × 9,200 = 416,000 (÷11.3) ; 14.10 contre 1.248 USD
  320 pages : 192,000 > 188,000 ; bascule 313.3 pages ; sous-agents moins chers dès Q > 1.04 ; décision : sous-agents
Cas 3 [BANQUE] place 30,000 ; glouton par score ['releves', 'statuts', 'identite1'] = 2.7
  obligatoires 19,000 tokens (3.35) + ['organigramme'] = 3.95 ; optimum libre 3.95 ; décision : obligatoires puis ['organigramme']
  à 31 000 l'optimum libre devient ['registre', 'identite1', 'identite2', 'releves', 'organigramme'] = 4.0
  relevés admis à 35,000 tokens (score 4.3)
Cas 4 [ASSUR] place 20,500 → 19,000 (marge 1,000) ; décision : réserve 3 500
  relances 1,500 = 37,500,000 tokens (112.50 USD) et 250 h ; bascule documents 19,000 (+5.56 %)
Corrigé
  ex1 38,000 ; ex2 47 ; ex3 75,000 ; ex5 ['B', 'C'] = 1.15 ; ex6 63, 1,485,000, 808,800 (÷1.84)
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme vérifie qu'une requête tient dans la fenêtre, calcule le nombre de tours possibles et le coût cumulé d'une boucle, avec ou sans fenêtre glissante, puis choisit les documents qui tiennent dans la place restante, les pièces obligatoires en premier.

```text
ALGORITHME BudgetDeContexte
ENTRÉES : B_total, n₀ (instructions), historique H, Δ (ajout par tour), B_sortie, T tours, M (fenêtre), r (résumé)
SORTIE  : (place disponible, T_max, entrée cumulée)

  disponible ← B_total − n₀ − H − B_sortie
  SI B_total − n₀ − B_sortie < 0 ALORS T_max ← 0
  SINON T_max ← partie entière de (B_total − n₀ − B_sortie) / Δ, plus 1
  cumul ← 0
  POUR t DE 1 À T FAIRE
      SI M non fixé OU t − 1 ≤ M ALORS cumul ← cumul + n₀ + (t − 1) × Δ
      SINON cumul ← cumul + n₀ + M × Δ + r
  FIN POUR
  RETOURNER disponible, T_max, cumul

ALGORITHME ChoisirDocuments (exact, pour peu de documents)
ENTRÉES : documents (nom, tokens, score), pièces obligatoires, place
  prendre d'abord toutes les pièces obligatoires ; place ← place − leurs tokens
  SI place < 0 ALORS ERREUR « les pièces obligatoires ne tiennent pas »
  essayer toutes les combinaisons des autres documents qui tiennent dans la place
  RETOURNER les obligatoires plus la combinaison de plus grand score total
```

**Complexité.** O(1) pour la place et le nombre maximal de tours, O(T) pour le cumul (ou O(1) avec la forme fermée de la démonstration 4). Le choix exact des documents essaie 2ⁿ combinaisons : acceptable pour n ≤ 20 environ ; au-delà, on utilise une programmation dynamique sur les tokens, en O(n × place), ou un glouton, en sachant qu'il peut se tromper (démonstration 5).

**Du squelette au code.** Les trois calculs sont `disponible`, `t_max` et `cumul`, et la forme fermée de la fenêtre glissante est `cumul_fenetre_ferme`. Le choix exact est `meilleur_choix(docs, place)`, qui parcourt `itertools.combinations` ; le glouton contre-exemple est la boucle sur `sorted(docs, key=lambda d: -d[2])` de `main`, et sa version générale `glouton(docs, place, cle)`. ChoisirDocuments avec pièces obligatoires est `cas_3_banque_kyc`. Les autres cas sont `cas_1_rh_visas`, `cas_2_btp_cahier` et `cas_4_assur_reserve`, et le coût en USD est `cout_usd`.
