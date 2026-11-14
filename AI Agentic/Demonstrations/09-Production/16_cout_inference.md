# 16 — Coût d'inférence : démonstrations

> Fiche : [16 — Coût d'inférence](<../../Images/09-Production/16_cout_inference.md>) · Image : `16_cout_inference.jpg` · Leçon : [Étape 72 — Coûts et gestion des tokens](<../../12-Production-Couts-Optimisation/72-Couts-et-Gestion-des-Tokens.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4. Les prix sont illustratifs : 3 USD par million de tokens d'entrée, 15 USD par million en sortie, cache lu à 10 % et écrit à 125 % du prix d'entrée ; on refait le calcul avec la grille du fournisseur et du modèle choisis. La conversion en AED utilise le taux fixe de 3,6725 AED par USD.

## La formule

$$
C_{\text{total}} \approx N_{\text{in}} \times c_{\text{in}} + N_{\text{out}} \times c_{\text{out}} + C_{\text{outils}}
$$

Nᵢₙ et Nₒᵤₜ sont les tokens lus et écrits par le modèle, cᵢₙ et cₒᵤₜ leurs prix unitaires, Cₒᵤₜᵢₗₛ le coût des appels d'outils (API externes, recherche, calcul).

## Les symboles, un par un

$$
N_{\text{in}}
$$

Le nombre de tokens envoyés au modèle (prompt système, outils, historique, documents, résultats d'outils), entier ≥ 0 ; sur une tâche de plusieurs tours, c'est la somme des entrées de chaque tour. Variable `entree`, argument `n_in`.

$$
N_{\text{out}}
$$

Le nombre de tokens générés par le modèle, entier ≥ 0. Argument `n_out`, et `sortie` (tokens écrits par tour).

$$
c_{\text{in}}
$$

Le prix d'un token d'entrée, en USD par token : 3 × 10⁻⁶ ici (3 USD par million, illustratif) ; la leçon 72 l'écrit Pᵢₙ. Constante `C_IN`.

$$
c_{\text{out}}
$$

Le prix d'un token de sortie : 15 × 10⁻⁶ USD ici, cinq fois le prix d'entrée (illustratif) ; la leçon 72 l'écrit Pₒᵤₜ. Constante `C_OUT`.

$$
C_{\text{outils}}
$$

Le coût des appels d'outils d'une tâche, en USD, réel ≥ 0. Argument `outils`.

$$
T
$$

Le nombre de tours (allers-retours avec le modèle) d'une tâche, entier ≥ 1 ; la leçon 72 l'écrit K. Argument `tours`.

$$
n_0
$$

La taille du préfixe stable renvoyé à chaque tour (instructions, définitions d'outils), en tokens ; la leçon 72 l'écrit S₀. Argument `n0`.

$$
\Delta
$$

Le nombre de tokens qu'ajoute chaque tour à l'historique relu au tour suivant. Argument `delta`.

$$
\rho
$$

Le facteur de prix d'un token relu depuis le cache, en fraction de cᵢₙ, dans [0 ; 1[ : 0,1 ici (illustratif) ; la leçon 72 l'écrit f. Argument `rho`, `None` sans cache.

$$
w
$$

Le facteur de prix d'un token écrit dans le cache au premier passage, en multiple de cᵢₙ : 1,25 ici (illustratif), ou 1 si l'on ignore le supplément d'écriture. Argument `w`.

$$
M
$$

La taille d'une fenêtre glissante, en nombre de tours d'historique conservés. Argument `fenetre`.

$$
p
$$

La probabilité qu'une tentative réussisse, dans ]0 ; 1]. Argument `p` de `cout_par_succes`.

## Le mécanisme, avant les preuves

La formule prend des volumes (tokens lus, tokens écrits) et des prix unitaires, les multiplie terme à terme, puis additionne les postes : c'est une facture à trois lignes. Chaque produit est linéaire : deux fois plus de tokens d'entrée coûtent deux fois plus, sans effet de seuil ni de remise, d'où le signe « ≈ » quand un fournisseur applique des paliers. L'addition rend les postes indépendants : réduire la sortie ne touche pas l'entrée, et chaque poste pèse dans le total selon sa part, ce qui dit tout de suite quel levier vaut la peine (démonstration 5). Ce qui n'est pas linéaire, c'est Nᵢₙ lui-même dans une boucle d'agent : chaque tour relit tout ce qui précède, si bien que la somme des entrées croît comme le carré du nombre de tours (démonstration 4). Le cache de préfixe ne retire aucun token : il change le prix d'une partie de Nᵢₙ, de cᵢₙ à ρ cᵢₙ, après un premier passage facturé w cᵢₙ (démonstration 3). Enfin, une tâche peut échouer : diviser par le taux de réussite convertit le coût d'une tentative en coût d'un résultat (démonstration 2). L'analogie Java/Spring utile est celle d'un appel à une API payante dans une boucle : on ne chiffre pas un appel, on chiffre la boucle, ses relances et son cache.

Petit film chiffré, sur une tâche de 3 tours avec un préfixe de 5 000 tokens, 1 500 tokens d'historique ajoutés par tour et 400 tokens écrits par tour. Entrées : 5 000, puis 6 500, puis 8 000 tokens, soit 19 500 ; coût d'entrée 19 500 × 3 × 10⁻⁶ = 0,0585 USD. Sortie : 3 × 400 = 1 200 tokens, soit 1 200 × 15 × 10⁻⁶ = 0,018 USD. Total sans outils : 0,0765 USD. Le dernier appel seul n'aurait coûté que 8 000 × 3 × 10⁻⁶ + 400 × 15 × 10⁻⁶ = 0,03 USD.

## Démonstration 1 — Le coût moyen se calcule avec les moyennes

**Ce qu'on démontre.** Si les prix cᵢₙ et cₒᵤₜ sont constants (pas de paliers), le coût moyen d'une tâche se calcule avec les moyennes des volumes :

$$
\mathbb{E}[C] = \mathbb{E}[N_{\text{in}}]\, c_{\text{in}} + \mathbb{E}[N_{\text{out}}]\, c_{\text{out}} + \mathbb{E}[C_{\text{outils}}]
$$

**L'idée.** L'espérance est linéaire : la moyenne d'une somme est la somme des moyennes, et une constante sort de la moyenne. Il n'y a besoin d'aucune hypothèse d'indépendance entre Nᵢₙ et Nₒᵤₜ.

**La preuve, pas à pas.**

**Étape 1.** Par linéarité de l'espérance (fiche 22), parce que 𝔼[X + Y] = 𝔼[X] + 𝔼[Y] pour toutes variables d'espérance finie :

$$
\mathbb{E}[C] = \mathbb{E}[N_{\text{in}} c_{\text{in}}] + \mathbb{E}[N_{\text{out}} c_{\text{out}}] + \mathbb{E}[C_{\text{outils}}]
$$

**Étape 2.** Les prix sont des constantes, et 𝔼[aX] = a 𝔼[X] pour une constante a, ce qui donne l'énoncé. ∎

**Vérification chiffrée.** 70 % de tâches courtes (8 000 tokens lus, 300 écrits) et 30 % de tâches longues (30 000 lus, 1 200 écrits). Par les moyennes : 𝔼[Nᵢₙ] = 0,7 × 8 000 + 0,3 × 30 000 = 14 600 et 𝔼[Nₒᵤₜ] = 0,7 × 300 + 0,3 × 1 200 = 570, d'où 14 600 × 3 × 10⁻⁶ + 570 × 15 × 10⁻⁶ = 0,0438 + 0,00855 = 0,05235 USD. Par les coûts : une tâche courte coûte 0,0285 USD et une longue 0,108 USD, et 0,7 × 0,0285 + 0,3 × 0,108 = 0,05235 USD. Contre-exemple quand l'hypothèse « prix constants » manque : si un palier doublait le prix d'entrée au-delà de 20 000 tokens de contexte, la tâche longue coûterait 0,198 USD, la moyenne réelle 0,07935 USD, et le calcul par les moyennes (14 600 tokens, sous le palier) resterait faux à 0,05235 USD.

**Ce que la preuve révèle du mécanisme.** Pour un budget moyen, la forme de la distribution des tokens n'importe pas : seule sa moyenne compte. Pour un pire jour, il faut en plus la variance, parce que la moyenne d'une journée chargée ne dit rien de sa queue.

**Conséquence pour un agent.** Le budget mensuel se calcule avec le nombre de tâches × le coût moyen d'une tâche, mesuré sur les journaux réels ; le garde-fou par tâche, lui, se règle sur les tâches longues (démonstration 6).

## Démonstration 2 — Le coût d'une tâche réussie

**Ce qu'on démontre.** On relance une tâche jusqu'au succès, les tentatives étant indépendantes et réussissant chacune avec la probabilité p ∈ ]0 ; 1]. Une tentative réussie coûte en moyenne Cₛ, une tentative échouée C_f (échec compris : vérification, reprise humaine). Le coût moyen d'un succès vaut

$$
C_{\text{succès}} = C_s + \frac{1 - p}{p}\, C_f
$$

et, si toutes les tentatives coûtent C (Cₛ = C_f = C), C_succès = C/p.

**L'idée.** Avant le succès, il y a un nombre aléatoire d'échecs, en moyenne (1 − p)/p ; chacun coûte C_f, et le succès final coûte Cₛ.

**La preuve, pas à pas.**

**Étape 1.** Le nombre total de tentatives K suit une loi géométrique de paramètre p, d'espérance 1/p (fiche 22, démonstration 4), parce que chaque tentative réussit indépendamment avec la probabilité p.

**Étape 2.** Le nombre d'échecs vaut K − 1, d'espérance 1/p − 1 = (1 − p)/p.

**Étape 3.** Par linéarité de l'espérance, le coût moyen vaut Cₛ (une réussite) plus (1 − p)/p fois C_f, ce qui donne l'énoncé ; avec Cₛ = C_f = C, C + C(1 − p)/p = C/p. ∎

**Vérification chiffrée.** C = 0,121 USD et p = 0,9 (cas 1) : C/p ≈ 0,13444 USD. Deux agents : 0,05 USD à 80 % de réussite et 0,07 USD à 98 % ; si un échec ne coûte que sa tentative, 0,05/0,8 = 0,0625 et 0,07/0,98 ≈ 0,07143 : le premier gagne. Si chaque échec coûte en plus une vérification humaine de 8 AED, soit environ 2,17835 USD, le premier coûte 0,60709 USD par succès et le second 0,11588 USD : le classement s'inverse (cas 2). Contre-exemple quand l'hypothèse « tentatives indépendantes » manque : si une tâche échoue toujours sur le même document illisible, p vaut 0 pour ce document et le coût par succès n'existe pas ; la fonction renvoie `None` pour p = 0.

**Ce que la preuve révèle du mécanisme.** Le facteur (1 − p)/p explose quand p baisse : il vaut 0,25 à 80 % de réussite et 0,0204 à 98 %, douze fois moins. Quand l'échec coûte plus cher que la tentative (temps humain, client mal servi), c'est la fiabilité qui fixe le coût, pas le prix du token.

**Conséquence pour un agent.** On choisit un modèle sur le coût par succès complet, échecs compris, et non sur le prix par appel ; on mesure p et C_f en production, par type de tâche.

## Démonstration 3 — Le cache du préfixe, son supplément d'écriture et son seuil de rentabilité

**Ce qu'on démontre.** Dans une boucle de T tours, le préfixe stable de n₀ tokens est relu à chaque tour. Servi depuis le cache, il coûte w cᵢₙ par token au premier tour (écriture) et ρ cᵢₙ ensuite (lecture), au lieu de T n₀ cᵢₙ :

$$
C_{\text{préfixe}} = n_0\, c_{\text{in}} \bigl( w + (T - 1)\, \rho \bigr)
$$

L'économie vaut n₀ cᵢₙ [(T − 1)(1 − ρ) − (w − 1)], et le cache est rentable dès que

$$
T > 1 + \frac{w - 1}{1 - \rho}
$$

**L'idée.** Le premier passage coûte un peu plus cher (on paie l'écriture), chaque passage suivant beaucoup moins : il suffit de quelques relectures pour amortir le supplément.

**La preuve, pas à pas.**

**Étape 1.** Sans cache, les T passages coûtent T n₀ cᵢₙ, parce que chaque tour renvoie les mêmes n₀ tokens au plein tarif.

**Étape 2.** Avec cache, un passage à w cᵢₙ par token et T − 1 passages à ρ cᵢₙ, d'où C_préfixe.

**Étape 3.** On soustrait, en écrivant T = 1 + (T − 1), parce que cela fait apparaître les deux effets séparément :

$$
T n_0 c_{\text{in}} - n_0 c_{\text{in}} (w + (T-1)\rho) = n_0 c_{\text{in}} \bigl( (T - 1)(1 - \rho) - (w - 1) \bigr)
$$

**Étape 4.** L'économie est positive si et seulement si (T − 1)(1 − ρ) > w − 1 ; on divise par 1 − ρ > 0, ce qui donne le seuil. ∎

**Vérification chiffrée.** n₀ = 5 000, T = 4, cᵢₙ = 3 × 10⁻⁶ USD, ρ = 0,1, w = 1,25 : sans cache 4 × 5 000 × 3 × 10⁻⁶ = 0,06 USD ; avec cache 5 000 × 3 × 10⁻⁶ × (1,25 + 3 × 0,1) = 0,02325 USD ; économie 0,03675 USD, égale à 0,015 × (3 × 0,9 − 0,25). Seuil : 1 + 0,25/0,9 ≈ 1,27778, donc le cache est rentable dès 2 passages. Contre-exemple quand l'hypothèse « le cache est encore valide au tour suivant » manque : si chaque tour arrive après l'expiration du cache, chaque passage repaie l'écriture, et 4 passages coûtent 4 × 1,25 × 0,015 = 0,075 USD, plus que sans cache.

**Ce que la preuve révèle du mécanisme.** L'économie croît linéairement avec le nombre de relectures, au taux (1 − ρ) n₀ cᵢₙ par tour ; le supplément d'écriture est un coût fixe. Le cache ne touche ni la sortie ni la partie de l'historique qui change à chaque tour, et il ne diminue pas Nᵢₙ : les tokens sont toujours envoyés et lus par le modèle.

**Conséquence pour un agent.** On place en tête du prompt tout ce qui est stable (instructions, outils, documents de référence) pour qu'il forme un préfixe cachable, et l'on regroupe les appels qui partagent ce préfixe dans la durée de vie du cache (cas 3).

## Démonstration 4 — Les tokens d'entrée d'une boucle croissent comme un carré, sauf avec une fenêtre

**Ce qu'on démontre.** Si chaque tour renvoie le préfixe n₀ et tout l'historique, et que chaque tour ajoute Δ tokens, l'entrée cumulée sur T tours vaut

$$
N_{\text{in}} = \sum_{t=1}^{T} \bigl(n_0 + (t - 1)\,\Delta\bigr) = T n_0 + \Delta\, \frac{T(T - 1)}{2}
$$

Avec une fenêtre glissante qui ne garde que les M derniers tours, et pour T ≥ M + 1 :

$$
N_{\text{in, fen}} = T n_0 + \Delta\, \frac{M (2T - M - 1)}{2}
$$

**L'idée.** Sans fenêtre, le tour t relit t − 1 morceaux d'historique : la somme 0 + 1 + … + (T − 1) est triangulaire, donc quadratique. Avec une fenêtre, le nombre de morceaux plafonne à M, et la somme devient linéaire.

**La preuve, pas à pas.**

**Étape 1.** On sépare la somme en deux, parce qu'une somme de sommes se coupe : T n₀ plus Δ fois la somme des t − 1.

**Étape 2.** La somme 0 + 1 + … + (T − 1), écrite à l'endroit puis à l'envers et additionnée terme à terme, donne T paires valant chacune T − 1 (argument de Gauss), d'où T(T − 1)/2.

**Étape 3.** Avec la fenêtre, le tour t relit min(t − 1, M) morceaux : les M + 1 premiers tours relisent 0, 1, …, M morceaux, soit M(M + 1)/2, et les T − M − 1 suivants M chacun ; on met M en facteur, parce que (M + 1)/2 + T − M − 1 = (2T − M − 1)/2 :

$$
\frac{M(M+1)}{2} + M\,(T - M - 1) = \frac{M\,(2T - M - 1)}{2}
$$

∎

**Vérification chiffrée.** n₀ = 5 000, Δ = 1 500 : T = 4 donne 20 000 + 1 500 × 6 = 29 000 tokens ; T = 8 donne 40 000 + 1 500 × 28 = 82 000 tokens, 2,82759 fois plus pour deux fois plus de tours. Avec n₀ = 3 000, Δ = 800 et T = 60 (cas 4) : 1 596 000 tokens sans fenêtre, et, avec M = 4, 180 000 + 800 × 4 × 115/2 = 364 000 tokens. Contre-exemple quand l'hypothèse T ≥ M + 1 manque : pour T = 3 et M = 4, la fenêtre n'est jamais pleine, la formule de la fenêtre donnerait 9 000 + 800 × 4 × 1/2 = 10 600 alors que la vraie somme vaut 9 000 + 800 × 3 = 11 400, celle sans fenêtre.

**Ce que la preuve révèle du mécanisme.** Le terme ΔT²/2 domine les longues boucles : doubler les tours fait plus que doubler la facture d'entrée, et le rapport tend vers 4. La fenêtre remplace ce terme par ΔMT, linéaire, au prix de l'oubli des tours anciens.

**Conséquence pour un agent.** Au-delà de quelques tours, on borne l'historique (fenêtre, résumé) et l'on recopie les faits durables dans le préfixe fixe ou dans une mémoire structurée, pour que la fenêtre ne les fasse pas disparaître.

## Démonstration 5 — De combien bouge le coût si un volume change de 1 %

**Ce qu'on démontre.** Pour C = Nᵢₙcᵢₙ + Nₒᵤₜcₒᵤₜ + Cₒᵤₜᵢₗₛ, une variation relative de x % d'un seul poste fait varier C de sₓ × x %, où sₓ est la part de ce poste dans C :

$$
\frac{\Delta C}{C} = s_{\text{in}}\, \frac{\Delta N_{\text{in}}}{N_{\text{in}}}, \qquad s_{\text{in}} = \frac{N_{\text{in}}\, c_{\text{in}}}{C}
$$

et de même pour la sortie et les outils ; les trois parts ont pour somme 1.

**L'idée.** La formule est linéaire : changer Nᵢₙ de 1 % change le poste d'entrée de 1 %, et le total d'autant, rapporté à son poids dans le total.

**La preuve, pas à pas.**

**Étape 1.** Seul le premier terme dépend de Nᵢₙ, et il est proportionnel à Nᵢₙ, donc ΔC = cᵢₙ ΔNᵢₙ, parce que les deux autres termes ne bougent pas.

**Étape 2.** On divise par C et l'on multiplie et divise par Nᵢₙ, parce que cela fait apparaître la variation relative :

$$
\frac{\Delta C}{C} = \frac{c_{\text{in}} N_{\text{in}}}{C} \times \frac{\Delta N_{\text{in}}}{N_{\text{in}}}
$$

**Étape 3.** La somme des trois parts vaut (Nᵢₙcᵢₙ + Nₒᵤₜcₒᵤₜ + Cₒᵤₜᵢₗₛ)/C = 1. ∎

**Vérification chiffrée.** Tâche du cas 1 sans cache : 0,121 USD, dont 0,087 d'entrée, 0,024 de sortie et 0,01 d'outils, soit des parts de 71,901 %, 19,835 % et 8,264 %. Réduire la sortie de 10 % fait baisser le coût de 1,983 % seulement ; réduire l'entrée de 10 % le fait baisser de 7,190 %. Contre-exemple quand l'hypothèse « un seul poste bouge » manque : raccourcir les réponses de 400 à 300 tokens raccourcit aussi l'historique relu aux tours suivants, si les réponses en font partie, et l'économie est plus grande que la part de sortie ne l'annonce.

**Ce que la preuve révèle du mécanisme.** Les parts sont les « élasticités » du coût : elles disent sans calcul supplémentaire quel poste attaquer. Une fois l'entrée réduite par le cache, la part de la sortie monte, et elle devient le levier suivant.

**Conséquence pour un agent.** Le tableau de bord de coût d'un agent affiche les trois parts, par type de tâche, et chaque optimisation est chiffrée par sa part avant d'être développée.

## Démonstration 6 — Le nombre maximal de tours sous un budget

**Ce qu'on démontre.** Sans fenêtre ni cache, avec une sortie de s tokens et des outils de coût k par tour, le coût d'une tâche de T tours est un trinôme croissant en T :

$$
C(T) = a\,T^2 + b\,T, \qquad a = \frac{\Delta\, c_{\text{in}}}{2}, \qquad b = c_{\text{in}}\left(n_0 - \frac{\Delta}{2}\right) + s\, c_{\text{out}} + k
$$

Pour un budget B > 0 par tâche, le plus grand nombre de tours admissible est la partie entière de la racine positive :

$$
T_{\max} = \left\lfloor \frac{-b + \sqrt{b^2 + 4 a B}}{2a} \right\rfloor
$$

**L'idée.** On a déjà la somme des entrées (démonstration 4) ; les sorties et les outils ajoutent un terme linéaire. Chercher le nombre de tours qui épuise le budget revient à résoudre une équation du second degré.

**La preuve, pas à pas.**

**Étape 1.** On ajoute les trois postes, parce que la formule est une somme : cᵢₙ(T n₀ + ΔT(T − 1)/2) + T s cₒᵤₜ + T k ; on développe ΔT(T − 1)/2 = (Δ/2)T² − (Δ/2)T, ce qui donne a et b.

**Étape 2.** a > 0 et b > 0 quand n₀ > Δ/2, donc C est croissante sur T ≥ 0, parce que sa dérivée 2aT + b est positive : l'ensemble des T admissibles est un intervalle [0 ; T*].

**Étape 3.** T* est la racine positive de aT² + bT − B = 0, par la formule du second degré ; T doit être entier, d'où la partie entière. ∎

**Vérification chiffrée.** n₀ = 5 000, Δ = 1 500, 400 tokens écrits et 0,005 USD d'outils par tour, budget 0,50 USD : a = 1 500 × 3 × 10⁻⁶/2 = 0,00225, b = 3 × 10⁻⁶ × 4 250 + 0,006 + 0,005 = 0,02375, et la racine vaut ≈ 10,53605, donc T_max = 10 ; contrôle : C(10) = 0,4625 USD ≤ 0,50 et C(11) = 0,5335 USD > 0,50. Contre-exemple quand l'hypothèse « ni fenêtre ni cache » manque : avec une fenêtre, C(T) devient linéaire pour T ≥ M + 1 et la formule du trinôme ne s'applique plus ; le programme cherche alors T_max par une boucle (cas 4).

**Ce que la preuve révèle du mécanisme.** Comme C croît comme T², doubler le budget ne double pas le nombre de tours permis : il le multiplie par moins de √2 quand le terme quadratique domine. C'est la croissance quadratique qui rend un garde-fou de budget indispensable aux boucles ouvertes.

**Conséquence pour un agent.** Le garde-fou de budget compare, avant chaque tour, le coût cumulé plus le coût prévu du tour suivant au budget de la tâche, et arrête proprement (résumé, passage à un humain) au lieu de couper au milieu d'une action.

## Exemple simple, à la main

Un appel lit 12 000 tokens, en écrit 800, et un outil coûte 0,005 USD, aux prix illustratifs de 3 USD par million en entrée et 15 USD par million en sortie :

$$
C = 12\,000 \times 3 \times 10^{-6} + 800 \times 15 \times 10^{-6} + 0{,}005 = 0{,}036 + 0{,}012 + 0{,}005 = 0{,}053 \text{ USD}
$$

| poste | volume | prix unitaire | coût (USD) | part |
|---|---|---|---|---|
| entrée | 12 000 tokens | 3 × 10⁻⁶ USD | 0,036 | 67,925 % |
| sortie | 800 tokens | 15 × 10⁻⁶ USD | 0,012 | 22,642 % |
| outil | 1 appel | 0,005 USD | 0,005 | 9,434 % |
| total | | | 0,053 | 100 % |

En AED : 0,053 × 3,6725 ≈ 0,19464 AED. Sur 5 tours où chaque tour ajoute 2 000 tokens à l'historique relu (fiche 16), l'entrée devient 5 × 12 000 + 2 000 × (0 + 1 + 2 + 3 + 4) = 60 000 + 20 000 = 80 000 tokens, soit 0,24 USD rien qu'en entrée.

## Cas d'usage complexes, démontrés

### Cas 1 — Services publics [PUBLIC] : budget mensuel de l'assistant de démarches

**Contexte.** Une entité de services publics en ligne, accessible par UAE Pass, fait accompagner les démarches des usagers, en arabe et en anglais, par un agent qui résout chaque demande en 4 tours. L'équipe doit présenter un budget mensuel et décider d'activer le cache du préfixe. Les volumes sont illustratifs, comme les prix.

**Données.**

- 4 tours par tâche ; préfixe stable n₀ = 5 000 tokens ; Δ = 1 500 tokens d'historique ajoutés par tour ; 400 tokens écrits par tour.
- 2 appels d'outils à 0,005 USD par tâche.
- 100 000 tâches par mois ; taux de réussite p = 0,9.
- Cache : lecture ρ = 0,1 ; écriture w = 1,25 (ou w = 1 dans l'ancienne version de ce fichier).

**Calcul pas à pas.**

**Étape 1.** Tokens d'entrée par tâche (démonstration 4) :

$$
\sum_{t=1}^{4} \bigl(5\,000 + (t - 1) \times 1\,500\bigr) = 20\,000 + 1\,500 \times 6 = 29\,000
$$

**Étape 2.** Sans cache : 29 000 × 3 × 10⁻⁶ + 1 600 × 15 × 10⁻⁶ + 0,01 = 0,087 + 0,024 + 0,01 = 0,121 USD par tâche, soit 12 100 USD par mois (44 437,25 AED).

**Étape 3.** Avec cache (démonstration 3) : le préfixe coûte 5 000 × 3 × 10⁻⁶ × (1,25 + 3 × 0,1) = 0,02325 USD, l'historique 9 000 × 3 × 10⁻⁶ = 0,027 USD, et la tâche 0,02325 + 0,027 + 0,024 + 0,01 = 0,08425 USD, soit 8 425 USD par mois (30 940,81 AED). L'ancienne version de ce fichier, qui ignorait le supplément d'écriture (w = 1), trouvait 0,0805 USD et 8 050 USD.

**Étape 4.** Par tâche réussie (démonstration 2) : 0,121/0,9 ≈ 0,13444 USD sans cache, 0,08425/0,9 ≈ 0,09361 USD avec.

**Décision de l'agent.** L'équipe active le cache du préfixe : −3 675 USD par mois. Le poste suivant à réduire est la sortie (0,024 USD par tâche, que le cache ne touche pas), par des réponses plus courtes et structurées.

**Contre-calcul.** Un budget fait sur le seul dernier appel (9 500 tokens lus, 400 écrits, outils compris) donnerait 0,0445 USD par tâche, soit 4 450 USD par mois : une sous-estimation de 63,223 % de la facture sans cache. L'entité découvrirait le dépassement à la première facture.

**Sensibilité.** Le gain du cache est effacé si le taux de réussite tombe assez pour que le coût par succès avec cache rejoigne celui sans cache à 90 % : 0,08425/p = 0,13444 donne p ≈ 0,62665. Plus près : si p passe de 0,9 à 0,8, le coût par succès avec cache monte à 0,10531 USD, encore sous les 0,13444 USD sans cache.

**En production.** Indicateurs : la part des tokens d'entrée lus dans le cache, avec une alerte sous 60 % (illustratif), et le coût par démarche aboutie. Les journaux de coût ne contiennent pas les textes des usagers ; le régime de protection des données applicable à l'entité (PDPL ou texte propre) est à confirmer avec le texte en vigueur.

### Cas 2 — Assurance [ASSUR] : modèle bon marché ou modèle fiable pour instruire les sinistres

**Contexte.** Un assureur auto et santé fait préinstruire les déclarations de sinistre par un agent, et hésite entre deux modèles. Chaque échec (dossier mal lu) est détecté par un contrôle et vérifié par un gestionnaire pendant quelques minutes, puis relancé. La question : lequel coûte le moins par dossier correctement instruit ? Volumes et coûts illustratifs.

**Données.**

- Modèle A : 0,05 USD par tentative, réussite pA = 0,80.
- Modèle B : 0,07 USD par tentative, réussite pB = 0,98.
- Vérification humaine d'un échec : 8 AED, soit 8/3,6725 ≈ 2,17835 USD.
- 20 000 dossiers par mois.

**Calcul pas à pas.**

**Étape 1.** Échecs moyens par succès, (1 − p)/p : 0,2/0,8 = 0,25 pour A, 0,02/0,98 ≈ 0,02041 pour B.

**Étape 2.** Coût par succès (démonstration 2), avec C_f = tentative + vérification humaine :

$$
C_A = \frac{0{,}05}{0{,}8} + 0{,}25 \times 2{,}17835 \approx 0{,}60709, \qquad C_B = \frac{0{,}07}{0{,}98} + 0{,}02041 \times 2{,}17835 \approx 0{,}11588
$$

**Étape 3.** Coût mensuel : 20 000 × 0,60709 ≈ 12 141,76 USD pour A, 20 000 × 0,11588 ≈ 2 317,69 USD pour B.

**Étape 4.** Écart : environ 9 824,07 USD par mois, soit environ 36 078,89 AED.

**Décision de l'agent.** L'assureur retient le modèle B, 40 % plus cher par appel mais 5,2 fois moins cher par dossier instruit.

**Contre-calcul.** Sur le seul prix par appel (0,05 < 0,07), ou même sur le coût par succès sans temps humain (0,0625 < 0,07143), on choisirait A, et l'on paierait environ 9 824,07 USD de plus par mois, avec un gestionnaire occupé à reprendre un dossier sur cinq.

**Sensibilité.** Valeur de bascule du coût humain h d'un échec : A et B coûtent autant quand 0,0625 + 0,25h = 0,07143 + 0,02041h, soit h ≈ 0,03889 USD, environ 0,14282 AED : dès qu'un échec coûte plus d'environ 14 fils de temps humain (1 AED = 100 fils), B gagne. À coût humain fixé (8 AED), A ne rattraperait B qu'avec un taux de réussite de 97,128 %.

**En production.** Indicateurs : le coût par dossier instruit, temps humain compris, et le taux d'échec par type de sinistre. L'assurance est supervisée par la CBUAE ; la décision finale sur un sinistre reste documentée par le gestionnaire, et les exigences précises sur l'usage de modèles sont à confirmer avec le texte en vigueur.

### Cas 3 — Construction [BTP] : un contrat de 60 000 tokens relu vingt fois

**Contexte.** Un groupe de construction de Dubaï fait interroger par un agent un contrat de sous-traitance de 60 000 tokens (retenues de garantie, pénalités de retard, TVA de 5 % sur les situations de travaux). Un ingénieur pose 20 questions sur ce contrat dans la journée. Le cache a une durée de vie de quelques minutes (illustratif), renouvelée à chaque lecture. La question : faut-il mettre le contrat en cache, et comment organiser les questions ?

**Données.**

- Contrat : 60 000 tokens ; 20 questions ; 300 tokens de réponse par question.
- cᵢₙ = 3 × 10⁻⁶ USD, cₒᵤₜ = 15 × 10⁻⁶ USD (illustratifs) ; cache ρ = 0,1 et w = 1,25.
- Deux rythmes : questions groupées dans une session courte, ou espacées de 20 minutes (cache expiré à chaque fois).

**Calcul pas à pas.**

**Étape 1.** Sans cache : chaque question paie 60 000 × 3 × 10⁻⁶ = 0,18 USD d'entrée, soit 3,60 USD pour 20 questions.

**Étape 2.** Avec cache, session groupée (démonstration 3) : la première question écrit le contrat (0,225 USD), les 19 suivantes le relisent à 0,018 USD :

$$
60\,000 \times 3 \times 10^{-6} \times (1{,}25 + 19 \times 0{,}1) = 0{,}567 \text{ USD}
$$

**Étape 3.** Avec cache, questions espacées : chaque question repaie l'écriture, 20 × 0,225 = 4,50 USD, plus cher que sans cache.

**Étape 4.** Sortie, identique dans les trois cas : 20 × 300 × 15 × 10⁻⁶ = 0,09 USD. Totaux : 3,69 USD, 0,657 USD et 4,59 USD.

**Décision de l'agent.** L'agent regroupe les questions sur un même contrat dans une session courte (0,657 USD au lieu de 3,69 USD) ; quand le rythme de travail ne le permet pas, il désactive le cache pour ce contrat, ou choisit une durée de cache plus longue, plus chère à l'écriture.

**Contre-calcul.** Activer le cache « par principe » sur des questions espacées coûte 4,59 USD au lieu de 3,69 USD, 0,90 USD de plus par contrat et par jour ; sur 200 contrats interrogés par jour (illustratif), cela fait 180 USD par jour, environ 661,05 AED, payés pour rien.

**Sensibilité.** Seuil de rentabilité en nombre de lectures : 1 + 0,25/0,9 ≈ 1,27778 passage, soit au moins 2 questions dans la durée de vie du cache. En fraction de questions servies par le cache, h, le facteur moyen vaut 1,25 − 1,15h, inférieur à 1 dès que h > 0,25/1,15 ≈ 0,21739 : il faut qu'au moins 21,739 % des questions tombent dans le cache.

**En production.** Indicateur : la part des tokens d'entrée lus dans le cache, par contrat, avec une alerte sous 50 % (illustratif). Les montants de retenue, de pénalité et de TVA de 5 % cités par l'agent sont recalculés par un outil, jamais par le modèle de mémoire ; le découpage du contrat par clauses réduit encore l'entrée quand une question ne porte que sur une section.

### Cas 4 — Ressources humaines [RH] : un garde-fou de budget sur un dossier d'embauche

**Contexte.** Un cabinet RH présent dans plusieurs émirats confie à un agent tout le parcours d'un recrutement : offre, permis, visite médicale, Emirates ID, contrat MOHRE, ouverture du compte salaire pour le WPS. Un dossier demande 60 tours. Le cabinet fixe un budget de 1,50 USD par dossier et un garde-fou qui arrête l'agent avant de le dépasser. La question : quelle architecture permet de finir un dossier sous ce budget ? Valeurs illustratives.

**Données.**

- Préfixe n₀ = 3 000 tokens (instructions et mémoire structurée du dossier) ; Δ = 800 tokens par tour ; 300 tokens écrits par tour ; outils 0,004 USD par tour.
- 60 tours par dossier ; budget 1,50 USD ; 2 000 dossiers par mois.
- Architectures : historique complet ; fenêtre de M = 4 tours ; fenêtre et cache du préfixe (ρ = 0,1, w = 1,25).

**Calcul pas à pas.**

**Étape 1.** Historique complet (démonstration 6) : a = 800 × 3 × 10⁻⁶/2 = 0,0012 et b = 3 × 10⁻⁶ × 2 600 + 300 × 15 × 10⁻⁶ + 0,004 = 0,0163, donc C(60) = 0,0012 × 3 600 + 0,0163 × 60 = 4,32 + 0,978 = 5,298 USD, et la racine (−0,0163 + √(0,0163² + 4 × 0,0012 × 1,5))/(2 × 0,0012) ≈ 29,21009 donne T_max = 29 tours.

**Étape 2.** Fenêtre M = 4 (démonstration 4) : 364 000 tokens d'entrée, soit 1,092 USD, plus 60 × 0,0085 = 0,51 USD de sortie et d'outils : 1,602 USD, au-dessus du budget ; T_max = 56 tours.

**Étape 3.** Fenêtre et cache du préfixe : le préfixe coûte 3 000 × (1,25 + 59 × 0,1) = 21 450 tokens équivalents, la fenêtre 800 × 4 × 115/2 = 184 000, soit 205 450 × 3 × 10⁻⁶ ≈ 0,61635 USD, et le dossier 1,12635 USD ; T_max = 79 tours.

**Étape 4.** Mensuel : 2 000 × 5,298 = 10 596 USD avec l'historique complet, 2 000 × 1,12635 = 2 252,70 USD avec fenêtre et cache, 4,70369 fois moins.

**Décision de l'agent.** Le cabinet retient la fenêtre avec cache du préfixe : c'est la seule architecture qui finit un dossier de 60 tours sous 1,50 USD (1,12635 USD, avec un plafond de 79 tours). Le garde-fou reste actif et arrête proprement l'agent au tour 79 au plus.

**Contre-calcul.** Avec l'historique complet, le garde-fou arrêterait l'agent au tour 29 sur 60 : la moitié des dossiers resteraient bloqués à mi-parcours, à reprendre à la main. Sans garde-fou, la facture serait de 10 596 USD par mois au lieu de 2 252,70 USD. La fenêtre seule ne suffit pas : 1,602 USD, et un arrêt au tour 56, juste avant la signature du contrat.

**Sensibilité.** Le coût du dossier avec fenêtre et cache vaut 0,06435 + 0,00069Δ + 0,51 USD ; il atteint le budget de 1,50 USD pour Δ ≈ 1 341,52 tokens : au-delà d'environ 1 342 tokens ajoutés par tour, il faut réduire la fenêtre ou résumer. Une hausse de 10 % de Δ (880 tokens) donne 1,18155 USD, encore sous le budget.

**En production.** Indicateurs : le coût par dossier, la part des dossiers arrêtés par le garde-fou, et le nombre d'erreurs causées par un fait sorti de la fenêtre. Les faits administratifs (date d'arrivée, type de visa) sont écrits dans la mémoire structurée du préfixe, relue à chaque tour. Les données d'identité des candidats sont des données personnelles : leur traitement relève de la PDPL, ou du régime propre au DIFC ou à l'ADGM si le cabinet y est établi, à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Un appel lit 50 000 tokens et en écrit 2 000, aux prix de l'exemple. Calculer son coût.

**Exercice 2.** Un agent coûte 0,05 USD par tâche avec 80 % de réussite ; un autre 0,07 USD avec 98 %. Lequel coûte le moins par succès, si un échec ne coûte que sa tentative ?

**Exercice 3.** Calculer l'économie du cache sur 10 tours, pour un préfixe de 8 000 tokens, ρ = 0,1, cᵢₙ = 3 USD par million, d'abord en ignorant le supplément d'écriture (w = 1), puis avec w = 1,25.

**Exercice 4.** Démontrer que 𝔼[Nᵢₙcᵢₙ + Nₒᵤₜcₒᵤₜ] = 𝔼[Nᵢₙ]cᵢₙ + 𝔼[Nₒᵤₜ]cₒᵤₜ.

**Exercice 5.** Dans le cas 1, que devient le coût mensuel sans cache si les tâches font 8 tours au lieu de 4 ?

**Exercice 6 (modifier une donnée).** Dans le cas 2, la vérification humaine d'un échec ne coûte plus que 0,5 AED (contrôle automatisé). Recalculer les deux coûts par succès. La décision change-t-elle ?

**Exercice 7 (trouver l'erreur).** Un collègue écrit : « Avec le cache du préfixe de 5 000 tokens, la tâche du cas 1 n'envoie plus que 29 000 − 3 × 5 000 = 14 000 tokens d'entrée, donc son entrée coûte 14 000 × 3 × 10⁻⁶ = 0,042 USD. » Trouver l'erreur et donner le bon coût d'entrée.

**Exercice 8 (redémontrer de mémoire).** Sans regarder, redémontrer que l'entrée cumulée d'une boucle de T tours vaut T n₀ + ΔT(T − 1)/2, puis l'appliquer à n₀ = 2 000, Δ = 500, T = 15.

## Corrigé

**Exercice 1.** 50 000 × 3 × 10⁻⁶ = 0,15 USD et 2 000 × 15 × 10⁻⁶ = 0,03 USD, soit 0,18 USD.

**Exercice 2.** 0,05/0,8 = 0,0625 USD et 0,07/0,98 ≈ 0,07143 USD : le premier, par succès. Mais 20 % d'échecs sont à traiter par ailleurs : dès qu'un échec coûte plus de 0,03889 USD de temps humain, le second gagne (cas 2).

**Exercice 3.** Avec w = 1 : économie (T − 1)(1 − ρ) n₀ cᵢₙ = 9 × 0,9 × 8 000 × 3 × 10⁻⁶ = 0,1944 USD par tâche. Avec w = 1,25, on retire le supplément (w − 1) n₀ cᵢₙ = 0,25 × 0,024 = 0,006 USD : 0,1884 USD.

**Exercice 4.** Linéarité de l'espérance, puis sortie des constantes cᵢₙ et cₒᵤₜ (démonstration 1, étapes 1 et 2).

**Exercice 5.** Entrée : 8 × 5 000 + 1 500 × 28 = 82 000 tokens, soit 0,246 USD ; sortie 3 200 × 15 × 10⁻⁶ = 0,048 USD ; outils 0,01 USD. Total 0,304 USD par tâche, soit 30 400 USD par mois : doubler les tours fait plus que doubler le coût (12 100 USD à 4 tours).

**Exercice 6.** h = 0,5/3,6725 ≈ 0,13615 USD. A : 0,0625 + 0,25 × 0,13615 ≈ 0,09654 USD ; B : 0,07143 + 0,02041 × 0,13615 ≈ 0,07421 USD. B reste moins cher, parce que h ≈ 0,13615 USD dépasse encore la bascule de 0,03889 USD.

**Exercice 7.** Le cache ne retire aucun token : la tâche envoie toujours 29 000 tokens. Parmi eux, les 20 000 tokens de préfixe (5 000 à chacun des 4 tours) changent de prix : 5 000 sont facturés w = 1,25 fois au premier tour, et 15 000 sont relus à ρ = 0,1 fois aux tours 2 à 4 ; les 9 000 tokens d'historique restent au plein tarif. Coût d'entrée exact : 0,02325 + 0,027 = 0,05025 USD, pas 0,042 USD.

**Exercice 8.** Étapes 1 et 2 de la démonstration 4. Application : 15 × 2 000 + 500 × 15 × 14/2 = 30 000 + 52 500 = 82 500 tokens, la valeur de la leçon 72.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cout_appel(n_in, n_out, outils, c_in, c_out)`** — Cette fonction est la caisse enregistreuse d'un seul appel au modèle : elle reçoit le nombre de tokens d'entrée, le nombre de tokens de sortie, le coût des outils, nul par défaut, et les deux prix unitaires, 3 USD et 15 USD par million de tokens par défaut, refuse par une `ValueError` tout volume ou coût négatif, puis additionne N entrée × c entrée, N sortie × c sortie et les outils. Elle renvoie le coût en dollars, soit 0,053 USD, ou 0,19464 AED, pour 12 000 tokens d'entrée, 800 de sortie et 0,005 USD d'outils, et sert de brique aux autres calculs.

**`tokens_entree(tours, n0, delta, fenetre)`** — On la voit en archiviste qui empile, tour après tour, tout l'historique qu'il faut relire au modèle : elle reçoit le nombre de tours, la taille n₀ du premier envoi, l'ajout Δ de chaque tour et une fenêtre facultative M, refuse moins d'un tour par une `ValueError`, puis additionne n₀ + min(t − 1, M) × Δ sur tous les tours, sans plafond si aucune fenêtre n'est donnée. Elle renvoie le total des tokens d'entrée, qui croît comme le carré du nombre de tours : 29 000 en 4 tours et 82 000 en 8, et 1 596 000 en 60 tours contre 364 000 avec une fenêtre de 4.

**`cout_tache(tours, n0, delta, sortie, outils, rho, w, fenetre, outils_par_tour)`** — Cette fonction est le comptable d'une tâche entière de plusieurs tours : elle reçoit le nombre de tours, les tailles n₀ = 5 000 et Δ = 1 500 par défaut, 400 tokens de sortie par tour, 0,01 USD d'outils, un taux de relecture ρ du cache, son coefficient d'écriture w, une fenêtre et un coût d'outils par tour, tous facultatifs. Sans cache, elle facture toute l'entrée au plein tarif ; avec cache, elle facture le préfixe n₀ une fois à w puis à ρ aux tours suivants, et le reste au plein tarif ; elle ajoute la sortie et les outils, et renvoie le couple tokens d'entrée et coût, soit 29 000 tokens et 0,121 USD pour 4 tours sans cache.

**`cout_par_succes(c_s, p, c_f)`** — Celle-ci raconte qu'une tentative ratée se paie aussi, et qu'il faut la compter dans le prix de chaque réussite : elle reçoit le coût d'une tentative, la probabilité de succès p et, facultativement, le coût d'un échec, égal par défaut à celui d'une tentative, refuse un p hors de l'intervalle de 0 à 1 par une `ValueError`, renvoie `None` si p = 0, puisque aucun succès n'est alors possible, et sinon renvoie C succès + (1 − p)/p × C échec. Elle donne 0,13444 USD pour une tâche à 0,121 USD réussie 9 fois sur 10.

**`seuil_cache(w, rho)`** — Cette fonction est le conseiller qui dit à partir de combien de passages un abonnement devient rentable : elle reçoit le coefficient w de l'écriture en cache et le coefficient ρ des relectures, refuse un ρ hors de [0 ; 1[ par une `ValueError`, puis renvoie 1 + (w − 1)/(1 − ρ). Avec w = 1,25 et ρ = 0,1, elle donne 1,27778 passage : dès qu'un préfixe est relu au moins une seconde fois, le cache rapporte, ce que la démonstration 3 et le cas 3 exploitent.

**`tours_max(budget, cout)`** — On l'imagine en gardien d'un portefeuille qui laisse l'agent continuer tant que la dépense prévue reste dans l'enveloppe : elle reçoit un budget et une fonction croissante qui donne le coût de T tours, puis augmente T d'une unité tant que le coût du tour suivant reste sous le budget. Elle renvoie le plus grand nombre de tours autorisé, 0 si même un seul tour dépasse : 10 tours pour 0,50 USD dans la démonstration 6, et 29, 56 ou 79 tours pour 1,50 USD selon l'architecture du cas 4.

**`cas_1_budget_public()`** — Cette fonction met en scène un service public dont l'agent résout chaque démarche en 4 tours, à raison de 100 000 tâches par mois réussies à 90 %, et qui doit présenter un budget et décider d'activer le cache : elle ne reçoit rien et calcule 29 000 tokens et 0,1210 USD par tâche sans cache, 0,08425 avec un cache dont l'écriture coûte 1,25 fois le tarif et 0,0805 si elle ne coûtait rien de plus. Elle en tire 12 100 contre 8 425 USD par mois, 0,13444 contre 0,09361 USD par succès, montre que compter le seul dernier appel, 0,0445 USD, sous-estimerait le coût de 63,223 %, calcule le taux de succès de bascule 0,62665 et le coût de 0,10531 à 80 % de succès, puis renvoie ces résultats.

**`cas_2_modeles_assur()`** — On y suit un assureur qui hésite entre un modèle A à 0,05 USD réussi à 80 % et un modèle B à 0,07 USD réussi à 98 %, chaque échec coûtant une nouvelle tentative et 8 AED de temps de gestionnaire : la fonction ne reçoit rien, convertit ces 8 AED en 2,17835 USD, compte 0,25 échec par succès pour A et 0,02041 pour B, et trouve un coût par succès de 0,60709 USD pour A contre 0,11588 pour B. Pour 20 000 dossiers correctement instruits par mois, l'écart atteint 9 824,07 USD, soit 36 078,89 AED ; elle calcule que B l'emporte dès qu'un échec coûte plus de 0,03889 USD de temps humain et que A devrait réussir à 97,128 % pour rattraper B, puis renvoie ces nombres.

**`cas_3_contrat_btp()`** — Cette fonction raconte un ingénieur qui pose 20 questions dans la journée sur un contrat de sous-traitance de 60 000 tokens, alors que le cache expire au bout de quelques minutes : elle ne reçoit rien, calcule qu'une question coûte 0,18 USD sans cache, que l'écriture en cache en coûte 0,225 et chaque relecture 0,018, puis les totaux de la journée, 3,69 USD sans cache, 0,657 si les questions sont groupées pour profiter du cache, et 4,59 si elles sont espacées au point que le cache expire et soit réécrit à chaque fois. Elle calcule le seuil de 1,27778 passage, la part minimale de 0,21739 servie par le cache pour rentrer dans ses frais, la perte de 180 USD par jour sur 200 contrats aux questions espacées, et renvoie le tout.

**`cas_4_garde_fou_rh()`** — Ici, un cabinet de recrutement confie à un agent un parcours complet de 60 tours par dossier, avec un budget de 1,50 USD et un garde-fou qui l'arrête avant de le dépasser : la fonction ne reçoit rien et compare trois architectures, l'historique complet, qui coûte 5,298 USD et ne tient que 29 tours, une fenêtre de 4 tours, à 1,602 USD et 56 tours, et une fenêtre avec cache, à 1,12635 USD et 79 tours, seule à finir le dossier. Elle vérifie le premier résultat par la racine 29,21009 de l'équation du second degré du coût, chiffre le mois de 2 000 dossiers à 10 596 contre 2 252,70 USD, trouve l'ajout par tour de bascule, 1 341,52 tokens, et le coût de 1,18155 USD si cet ajout passe à 880, puis renvoie ces résultats.

**`cout(t, fenetre, rho, delta)`** — Cette fonction interne vit dans `cas_4_garde_fou_rh`, comme le barème que le cabinet applique à chacune de ses trois architectures : elle reçoit un nombre de tours t, une fenêtre et un taux de cache facultatifs et l'ajout par tour, 800 tokens par défaut, puis appelle `cout_tache` avec un premier envoi de 3 000 tokens, 300 tokens de sortie, une écriture de cache à 1,25 et 0,004 USD d'outils par tour. Elle ne renvoie que le coût, 5,298 USD pour 60 tours sans fenêtre, et c'est elle que `tours_max` interroge pour trouver les 29, 56 et 79 tours.

**`main()`** — C'est le chef d'orchestre de la fiche : il vérifie d'abord le coût d'un appel, 0,053 USD, et sa décomposition en 67,925 % d'entrée, 22,642 % de sortie et 9,434 % d'outils, puis le film de trois tours et les six démonstrations, la linéarité de l'espérance du coût, le coût par succès, le seuil du cache, la croissance quadratique des entrées, les parts du coût et le nombre maximal de 10 tours sous 0,50 USD. Il joue ensuite les quatre cas et le corrigé, du coût de 0,18 USD de l'exercice 1 aux 30 400 USD par mois de l'exercice 5, puis s'assure qu'une probabilité de 1,2 est refusée ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tout concorde.

```python
"""Démonstration 16 — coût d'inférence : linéarité, coût par succès, cache et seuil de rentabilité, croissance des entrées, parts, tours maximaux, quatre cas aux Émirats."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

C_IN, C_OUT = 3e-6, 15e-6          # USD par token, prix illustratifs
AED_PAR_USD = 3.6725


def cout_appel(n_in, n_out, outils=0.0, c_in=C_IN, c_out=C_OUT):
    """C ≈ N_in × c_in + N_out × c_out + C_outils."""
    if n_in < 0 or n_out < 0 or outils < 0:
        raise ValueError("volumes et coûts doivent être >= 0")
    return n_in * c_in + n_out * c_out + outils


def tokens_entree(tours, n0, delta, fenetre=None):
    """Σ (n0 + min(t − 1, M) Δ) sur les tours ; sans fenêtre, M est infini (démonstration 4)."""
    if tours < 1:
        raise ValueError("au moins un tour")
    return sum(n0 + (t - 1 if fenetre is None else min(t - 1, fenetre)) * delta for t in range(1, tours + 1))


def cout_tache(tours, n0=5_000, delta=1_500, sortie=400, outils=0.01, rho=None, w=1.0, fenetre=None, outils_par_tour=None):
    """Coût d'une tâche de plusieurs tours ; rho=None : pas de cache ; sinon le préfixe n0 est écrit (w) puis relu (rho)."""
    entree = tokens_entree(tours, n0, delta, fenetre)
    if rho is None:
        c_entree = entree * C_IN
    else:
        prefixe = n0 * C_IN * (w + (tours - 1) * rho)
        c_entree = prefixe + (entree - tours * n0) * C_IN
    c_outils = outils if outils_par_tour is None else outils_par_tour * tours
    return entree, c_entree + tours * sortie * C_OUT + c_outils


def cout_par_succes(c_s, p, c_f=None):
    """C_s + (1 − p)/p × C_f (démonstration 2) ; None si p = 0 (aucun succès possible)."""
    if not 0 <= p <= 1:
        raise ValueError("p doit être dans [0 ; 1]")
    if p == 0:
        return None
    return c_s + (1 - p) / p * (c_s if c_f is None else c_f)


def seuil_cache(w, rho):
    """Nombre de passages au-delà duquel le cache est rentable : 1 + (w − 1)/(1 − ρ)."""
    if not 0 <= rho < 1:
        raise ValueError("rho doit être dans [0 ; 1[")
    return 1 + (w - 1) / (1 - rho)


def tours_max(budget, cout):
    """Plus grand T tel que cout(T) <= budget, cout étant croissante ; 0 si même un tour dépasse."""
    t = 0
    while cout(t + 1) <= budget:
        t += 1
    return t


def cas_1_budget_public():
    """Services publics : 4 tours, 100 000 tâches par mois, p = 0.9, cache ρ = 0.1."""
    entree, sans = cout_tache(4)
    _, avec_w1 = cout_tache(4, rho=0.1)
    _, avec = cout_tache(4, rho=0.1, w=1.25)
    dernier = cout_appel(9_500, 400, 0.01)
    res = {"entree": entree, "sans": sans, "avec_w1": avec_w1, "avec": avec, "prefixe": 5_000 * C_IN * (1.25 + 3 * 0.1),
           "mois_sans": 100_000 * sans, "mois_avec": 100_000 * avec, "mois_w1": 100_000 * avec_w1,
           "succes_sans": cout_par_succes(sans, 0.9), "succes_avec": cout_par_succes(avec, 0.9),
           "dernier": dernier, "mois_dernier": 100_000 * dernier, "sous_estimation": 1 - dernier / sans,
           "p_bascule": avec / cout_par_succes(sans, 0.9), "succes_08": cout_par_succes(avec, 0.8)}
    print(f"Cas 1 [PUBLIC] : {entree:_} tokens ; {sans:.4f} USD sans cache, {avec:.5f} avec (w = 1.25),"
          f" {avec_w1:.4f} (w = 1) ; mois {res['mois_sans']:_.0f} contre {res['mois_avec']:_.0f} USD")
    print(f"  par succès {res['succes_sans']:.5f} contre {res['succes_avec']:.5f} USD ; dernier appel seul {dernier:.4f} USD ;"
          f" bascule p = {res['p_bascule']:.5f}")
    return res


def cas_2_modeles_assur():
    """Assurance : modèle A (0.05 USD, 80 %) contre B (0.07 USD, 98 %), échec = tentative + 8 AED humains."""
    h = 8 / AED_PAR_USD
    res = {"h": h, "echecs_a": (1 - 0.8) / 0.8, "echecs_b": (1 - 0.98) / 0.98,
           "a": cout_par_succes(0.05, 0.8, 0.05 + h), "b": cout_par_succes(0.07, 0.98, 0.07 + h),
           "a_seul": cout_par_succes(0.05, 0.8), "b_seul": cout_par_succes(0.07, 0.98)}
    res["mois_a"], res["mois_b"] = 20_000 * res["a"], 20_000 * res["b"]
    res["ecart"] = res["mois_a"] - res["mois_b"]
    res["h_bascule"] = (res["b_seul"] - res["a_seul"]) / (res["echecs_a"] - res["echecs_b"])
    res["p_a_bascule"] = (0.05 + h) / (res["b"] + h)
    print(f"Cas 2 [ASSUR] : par succès A = {res['a']:.5f}, B = {res['b']:.5f} USD ; mois {res['mois_a']:_.2f}"
          f" contre {res['mois_b']:_.2f} USD ; bascule h = {res['h_bascule']:.5f} USD")
    print(f"  écart mensuel {res['ecart']:_.2f} USD = {res['ecart'] * AED_PAR_USD:_.2f} AED ;"
          f" A rattraperait B à p = {res['p_a_bascule']:.5f}")
    return res


def cas_3_contrat_btp():
    """BTP : contrat de 60 000 tokens, 20 questions, cache groupé ou expiré à chaque question."""
    contrat, n, sortie = 60_000, 20, 20 * 300 * C_OUT
    sans = n * contrat * C_IN
    groupe = contrat * C_IN * (1.25 + (n - 1) * 0.1)
    espace = n * contrat * C_IN * 1.25
    res = {"q_sans": contrat * C_IN, "sans": sans, "ecriture": contrat * C_IN * 1.25, "lecture": contrat * C_IN * 0.1,
           "groupe": groupe, "espace": espace, "sortie": sortie, "totaux": (sans + sortie, groupe + sortie, espace + sortie),
           "seuil": seuil_cache(1.25, 0.1), "h_min": 0.25 / 1.15}
    res["perte_jour"] = 200 * (res["totaux"][2] - res["totaux"][0])
    print(f"Cas 3 [BTP] : totaux {[round(v, 3) for v in res['totaux']]} USD (sans cache, groupé, espacé) ;"
          f" seuil {res['seuil']:.5f} passage ; fraction minimale servie par le cache {res['h_min']:.5f}")
    print(f"  une question : {res['q_sans']:.2f} USD sans cache, écriture {res['ecriture']:.3f}, lecture {res['lecture']:.3f} ;"
          f" 200 contrats aux questions espacées : {res['perte_jour']:.2f} USD perdus par jour")
    return res


def cas_4_garde_fou_rh():
    """RH : dossier de 60 tours, budget 1.50 USD, trois architectures."""
    def cout(t, fenetre=None, rho=None, delta=800):
        return cout_tache(t, n0=3_000, delta=delta, sortie=300, outils=0.0, rho=rho, w=1.25,
                          fenetre=fenetre, outils_par_tour=0.004)[1]

    a, b = 800 * C_IN / 2, C_IN * (3_000 - 400) + 300 * C_OUT + 0.004
    res = {"a": a, "b": b, "racine": (-b + math.sqrt(b * b + 4 * a * 1.5)) / (2 * a),
           "complet": cout(60), "fenetre": cout(60, fenetre=4), "fen_cache": cout(60, fenetre=4, rho=0.1),
           "tmax": (tours_max(1.5, cout), tours_max(1.5, lambda t: cout(t, fenetre=4)),
                    tours_max(1.5, lambda t: cout(t, fenetre=4, rho=0.1))),
           "entree_fen": tokens_entree(60, 3_000, 800, 4), "entree_complet": tokens_entree(60, 3_000, 800),
           "delta_bascule": (1.5 - 0.06435 - 0.51) / 0.00069, "fen_cache_880": cout(60, fenetre=4, rho=0.1, delta=880)}
    print(f"Cas 4 [RH] : 60 tours → {res['complet']:.3f} / {res['fenetre']:.3f} / {res['fen_cache']:.5f} USD ;"
          f" tours maximaux sous 1.50 USD {res['tmax']} ; bascule Δ = {res['delta_bascule']:.2f}")
    print(f"  mensuel {2_000 * res['complet']:_.0f} contre {2_000 * res['fen_cache']:_.2f} USD ;"
          f" avec Δ = 880 : {res['fen_cache_880']:.5f} USD par dossier")
    return res


def main() -> None:
    simple = cout_appel(12_000, 800, 0.005)
    print(f"un appel : {simple:.3f} USD = {simple * AED_PAR_USD:.5f} AED")
    assert round(simple, 3) == 0.053 and round(simple * AED_PAR_USD, 5) == 0.19464
    assert [round(100 * v / simple, 3) for v in (0.036, 0.012, 0.005)] == [67.925, 22.642, 9.434]
    assert tokens_entree(5, 12_000, 2_000) == 80_000 and math.isclose(80_000 * C_IN, 0.24)
    # film du mécanisme : 3 tours
    film = tokens_entree(3, 5_000, 1_500)
    assert film == 19_500 and math.isclose(film * C_IN, 0.0585) and math.isclose(1_200 * C_OUT, 0.018)
    assert math.isclose(cout_tache(3, outils=0.0)[1], 0.0765) and math.isclose(cout_appel(8_000, 400), 0.03)

    # démonstration 1 : linéarité
    e_in, e_out = 0.7 * 8_000 + 0.3 * 30_000, 0.7 * 300 + 0.3 * 1_200
    courte, longue = cout_appel(8_000, 300), cout_appel(30_000, 1_200)
    assert math.isclose(e_in, 14_600) and math.isclose(e_out, 570) and math.isclose(cout_appel(e_in, e_out), 0.05235)
    assert math.isclose(e_in * C_IN, 0.0438) and math.isclose(e_out * C_OUT, 0.00855)
    assert math.isclose(courte, 0.0285) and math.isclose(longue, 0.108) and math.isclose(0.7 * courte + 0.3 * longue, 0.05235)
    palier = cout_appel(30_000, 1_200, c_in=2 * C_IN)
    assert math.isclose(palier, 0.198) and round(0.7 * courte + 0.3 * palier, 5) == 0.07935
    print(f"démonstration 1 : par les moyennes {cout_appel(e_in, e_out):.5f} USD = par les coûts {0.7 * courte + 0.3 * longue:.5f} USD")
    # démonstration 2 : coût par succès
    assert round(cout_par_succes(0.121, 0.9), 5) == 0.13444 and cout_par_succes(0.05, 0.0) is None
    assert round(0.25, 2) == round((1 - 0.8) / 0.8, 2) and round((1 - 0.98) / 0.98, 4) == 0.0204
    assert round(((1 - 0.8) / 0.8) / ((1 - 0.98) / 0.98)) == 12
    print(f"démonstration 2 : 0.121 / 0.9 = {cout_par_succes(0.121, 0.9):.5f} USD ; échecs par succès"
          f" {(1 - 0.8) / 0.8:.2f} (p = 0.8) et {(1 - 0.98) / 0.98:.5f} (p = 0.98)")
    # démonstration 3 : cache, supplément d'écriture, seuil
    sans4, avec4 = 4 * 5_000 * C_IN, 5_000 * C_IN * (1.25 + 3 * 0.1)
    assert math.isclose(sans4, 0.06) and math.isclose(avec4, 0.02325) and math.isclose(sans4 - avec4, 0.03675)
    assert math.isclose(sans4 - avec4, 5_000 * C_IN * (3 * 0.9 - 0.25)) and round(seuil_cache(1.25, 0.1), 5) == 1.27778
    assert math.isclose(4 * 1.25 * 5_000 * C_IN, 0.075) and math.isclose(5_000 * C_IN, 0.015)
    print(f"démonstration 3 : préfixe 0.06 → {avec4:.5f} USD ; rentable au-delà de {seuil_cache(1.25, 0.1):.5f} passage")
    # démonstration 4 : croissance quadratique, fenêtre
    assert tokens_entree(4, 5_000, 1_500) == 29_000 and tokens_entree(8, 5_000, 1_500) == 82_000
    assert round(82_000 / 29_000, 5) == 2.82759 and tokens_entree(60, 3_000, 800) == 1_596_000
    assert tokens_entree(60, 3_000, 800, 4) == 364_000 == 180_000 + 800 * 4 * 115 // 2
    assert tokens_entree(3, 3_000, 800, 4) == 11_400 and 3 * 3_000 + 800 * 4 * (2 * 3 - 4 - 1) / 2 == 10_600
    print(f"démonstration 4 : 4 tours {tokens_entree(4, 5_000, 1_500):_} tokens, 8 tours {tokens_entree(8, 5_000, 1_500):_} ;"
          f" 60 tours {tokens_entree(60, 3_000, 800):_} contre {tokens_entree(60, 3_000, 800, 4):_} avec fenêtre")
    # démonstration 5 : parts du coût
    _, c = cout_tache(4)
    parts = [29_000 * C_IN / c, 1_600 * C_OUT / c, 0.01 / c]
    assert [round(100 * s, 3) for s in parts] == [71.901, 19.835, 8.264] and math.isclose(sum(parts), 1)
    assert round(10 * parts[1], 3) == 1.983 and round(10 * parts[0], 3) == 7.19
    print(f"démonstration 5 : parts entrée {parts[0]:.5f}, sortie {parts[1]:.5f}, outils {parts[2]:.5f}")
    # démonstration 6 : tours maximaux sous un budget
    a, b = 1_500 * C_IN / 2, C_IN * (5_000 - 750) + 400 * C_OUT + 0.005
    racine = (-b + math.sqrt(b * b + 4 * a * 0.5)) / (2 * a)
    cout6 = lambda t: cout_tache(t, outils=0.0, outils_par_tour=0.005)[1]
    assert math.isclose(a, 0.00225) and math.isclose(b, 0.02375) and round(racine, 5) == 10.53605
    assert tours_max(0.5, cout6) == 10 == math.floor(racine)
    assert math.isclose(cout6(10), 0.4625) and math.isclose(cout6(11), 0.5335)
    print(f"démonstration 6 : racine {racine:.5f}, T_max = {tours_max(0.5, cout6)} ; C(10) = {cout6(10):.4f}, C(11) = {cout6(11):.4f}")

    c1 = cas_1_budget_public()
    assert c1["entree"] == 29_000 and round(c1["sans"], 4) == 0.121 and round(c1["avec"], 5) == 0.08425
    assert math.isclose(c1["prefixe"], 0.02325) and math.isclose(9_000 * C_IN, 0.027) and math.isclose(1_600 * C_OUT, 0.024)
    assert round(c1["avec_w1"], 4) == 0.0805 and round(c1["mois_w1"]) == 8_050
    assert round(c1["mois_sans"]) == 12_100 and round(c1["mois_avec"]) == 8_425
    assert round(c1["mois_sans"] * AED_PAR_USD, 2) == 44_437.25 and round(c1["mois_avec"] * AED_PAR_USD, 2) == 30_940.81
    assert (round(c1["succes_sans"], 5), round(c1["succes_avec"], 5)) == (0.13444, 0.09361)
    assert round(c1["mois_sans"] - c1["mois_avec"]) == 3_675
    assert round(c1["dernier"], 4) == 0.0445 and round(c1["mois_dernier"]) == 4_450 and round(100 * c1["sous_estimation"], 3) == 63.223
    assert round(c1["p_bascule"], 5) == 0.62665 and round(c1["succes_08"], 5) == 0.10531
    assert math.isclose(5_000 + 3 * 1_500, 9_500)

    c2 = cas_2_modeles_assur()
    assert round(c2["h"], 5) == 2.17835 and math.isclose(c2["echecs_a"], 0.25) and round(c2["echecs_b"], 5) == 0.02041
    assert round(c2["a"], 5) == 0.60709 and round(c2["b"], 5) == 0.11588
    assert round(c2["mois_a"], 2) == 12_141.76 and round(c2["mois_b"], 2) == 2_317.69
    assert round(c2["ecart"], 2) == 9_824.07 and round(c2["ecart"] * AED_PAR_USD, 2) == 36_078.89
    assert round(c2["h_bascule"], 5) == 0.03889 and round(c2["h_bascule"] * AED_PAR_USD, 5) == 0.14282
    assert round(100 * c2["p_a_bascule"], 3) == 97.128 and round(c2["a"] / c2["b"], 1) == 5.2
    assert round(0.07 / 0.05 - 1, 2) == 0.4 and round(c2["a_seul"], 4) == 0.0625 and round(c2["b_seul"], 5) == 0.07143

    c3 = cas_3_contrat_btp()
    assert math.isclose(c3["q_sans"], 0.18) and math.isclose(c3["sans"], 3.6) and math.isclose(c3["ecriture"], 0.225)
    assert math.isclose(c3["lecture"], 0.018) and math.isclose(c3["groupe"], 0.567) and math.isclose(c3["espace"], 4.5)
    assert math.isclose(c3["sortie"], 0.09) and [round(v, 3) for v in c3["totaux"]] == [3.69, 0.657, 4.59]
    assert round(c3["totaux"][2] - c3["totaux"][0], 2) == 0.9 and round(c3["perte_jour"], 2) == 180
    assert round(c3["perte_jour"] * AED_PAR_USD, 2) == 661.05
    assert round(c3["seuil"], 5) == 1.27778 and round(c3["h_min"], 5) == 0.21739 and math.isclose(1.25 - 0.1, 1.15)

    c4 = cas_4_garde_fou_rh()
    assert math.isclose(c4["a"], 0.0012) and math.isclose(c4["b"], 0.0163) and round(c4["racine"], 5) == 29.21009
    assert math.isclose(c4["complet"], 5.298) and math.isclose(0.0012 * 3_600, 4.32) and math.isclose(0.0163 * 60, 0.978)
    assert c4["entree_fen"] == 364_000 and math.isclose(364_000 * C_IN, 1.092) and math.isclose(60 * 0.0085, 0.51)
    assert math.isclose(c4["fenetre"], 1.602) and math.isclose(c4["fen_cache"], 1.12635)
    assert 3_000 * (1.25 + 59 * 0.1) == 21_450 and 800 * 4 * 115 / 2 == 184_000 and round(205_450 * C_IN, 5) == 0.61635
    assert c4["tmax"] == (29, 56, 79) and math.isclose(300 * C_OUT + 0.004, 0.0085)
    assert math.isclose(2_000 * c4["complet"], 10_596) and round(2_000 * c4["fen_cache"], 2) == 2_252.7
    assert round(c4["complet"] / c4["fen_cache"], 5) == 4.70369
    assert round(c4["delta_bascule"], 2) == 1_341.52 and round(c4["fen_cache_880"], 5) == 1.18155
    assert math.isclose(3_000 * C_IN * 7.15, 0.06435) and math.isclose(4 * 115 / 2 * C_IN, 0.00069)

    print("Corrigé")
    e1 = cout_appel(50_000, 2_000)
    e3, e3w = 9 * 0.9 * 8_000 * C_IN, 9 * 0.9 * 8_000 * C_IN - 0.25 * 8_000 * C_IN
    _, e5 = cout_tache(8)
    h6 = 0.5 / AED_PAR_USD
    e6 = (cout_par_succes(0.05, 0.8, 0.05 + h6), cout_par_succes(0.07, 0.98, 0.07 + h6))
    print(f"  ex1 {e1:.2f} USD ; ex2 {0.05 / 0.8:.4f} et {0.07 / 0.98:.5f} ; ex3 {e3:.4f} puis {e3w:.4f} USD ;"
          f" ex5 {e5:.3f} USD -> {100_000 * e5:_.0f} USD ; ex6 {e6[0]:.5f} et {e6[1]:.5f}")
    assert round(e1, 2) == 0.18 and math.isclose(50_000 * C_IN, 0.15) and math.isclose(2_000 * C_OUT, 0.03)
    assert 0.05 / 0.8 < 0.07 / 0.98 and round(e3, 4) == 0.1944 and round(e3w, 4) == 0.1884
    assert math.isclose(0.25 * 8_000 * C_IN, 0.006) and math.isclose(8_000 * C_IN, 0.024)
    assert cout_tache(8)[0] == 82_000 and round(e5, 3) == 0.304 and round(100_000 * e5) == 30_400
    assert math.isclose(82_000 * C_IN, 0.246) and math.isclose(3_200 * C_OUT, 0.048) and 100_000 * e5 > 2 * 100_000 * c
    assert round(h6, 5) == 0.13615 and [round(v, 5) for v in e6] == [0.09654, 0.07421] and e6[1] < e6[0]
    assert math.isclose(0.02325 + 0.027, 0.05025) and math.isclose(14_000 * C_IN, 0.042) and 4 * 5_000 == 20_000
    assert 29_000 - 20_000 == 9_000 and 3 * 5_000 == 15_000 and round(100 * c2["h_bascule"] * AED_PAR_USD) == 14
    assert tokens_entree(15, 2_000, 500) == 82_500 == 30_000 + 52_500
    try:
        cout_par_succes(0.05, 1.2)
    except ValueError:
        print("  p = 1.2 refusé : ValueError")
    else:
        raise AssertionError("une probabilité > 1 aurait dû être refusée")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
un appel : 0.053 USD = 0.19464 AED
démonstration 1 : par les moyennes 0.05235 USD = par les coûts 0.05235 USD
démonstration 2 : 0.121 / 0.9 = 0.13444 USD ; échecs par succès 0.25 (p = 0.8) et 0.02041 (p = 0.98)
démonstration 3 : préfixe 0.06 → 0.02325 USD ; rentable au-delà de 1.27778 passage
démonstration 4 : 4 tours 29_000 tokens, 8 tours 82_000 ; 60 tours 1_596_000 contre 364_000 avec fenêtre
démonstration 5 : parts entrée 0.71901, sortie 0.19835, outils 0.08264
démonstration 6 : racine 10.53605, T_max = 10 ; C(10) = 0.4625, C(11) = 0.5335
Cas 1 [PUBLIC] : 29_000 tokens ; 0.1210 USD sans cache, 0.08425 avec (w = 1.25), 0.0805 (w = 1) ; mois 12_100 contre 8_425 USD
  par succès 0.13444 contre 0.09361 USD ; dernier appel seul 0.0445 USD ; bascule p = 0.62665
Cas 2 [ASSUR] : par succès A = 0.60709, B = 0.11588 USD ; mois 12_141.76 contre 2_317.69 USD ; bascule h = 0.03889 USD
  écart mensuel 9_824.07 USD = 36_078.89 AED ; A rattraperait B à p = 0.97128
Cas 3 [BTP] : totaux [3.69, 0.657, 4.59] USD (sans cache, groupé, espacé) ; seuil 1.27778 passage ; fraction minimale servie par le cache 0.21739
  une question : 0.18 USD sans cache, écriture 0.225, lecture 0.018 ; 200 contrats aux questions espacées : 180.00 USD perdus par jour
Cas 4 [RH] : 60 tours → 5.298 / 1.602 / 1.12635 USD ; tours maximaux sous 1.50 USD (29, 56, 79) ; bascule Δ = 1341.52
  mensuel 10_596 contre 2_252.70 USD ; avec Δ = 880 : 1.18155 USD par dossier
Corrigé
  ex1 0.18 USD ; ex2 0.0625 et 0.07143 ; ex3 0.1944 puis 0.1884 USD ; ex5 0.304 USD -> 30_400 USD ; ex6 0.09654 et 0.07421
  p = 1.2 refusé : ValueError
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme estime le coût d'une tâche d'agent sur plusieurs tours, avec ou sans cache du préfixe et fenêtre glissante, puis le coût par tâche réussie et le nombre maximal de tours sous un budget.

```text
ALGORITHME CoûtDUneTâche
ENTRÉES : tours T ≥ 1, préfixe n₀, ajout Δ par tour, fenêtre M ou RIEN, sortie par tour,
          coût des outils, prix c_in et c_out, cache (ρ, w) ou RIEN
SORTIE  : (tokens d'entrée, coût de la tâche)

  entrée ← 0
  POUR t DE 1 À T FAIRE
      SI fenêtre ALORS r ← min(t − 1, M) SINON r ← t − 1
      entrée ← entrée + n₀ + r × Δ
  FIN POUR
  SI pas de cache ALORS
      coût_entrée ← entrée × c_in
  SINON
      coût_préfixe ← n₀ × c_in × (w + (T − 1) × ρ)
      coût_entrée ← coût_préfixe + (entrée − T × n₀) × c_in
  FIN SI
  coût ← coût_entrée + T × sortie × c_out + outils
  RETOURNER entrée, coût

ALGORITHME CoûtParSuccès
ENTRÉES : coût d'une réussite Cs, coût d'un échec Cf, probabilité p
SORTIE  : coût moyen d'un succès, ou RIEN si p = 0
  SI p = 0 ALORS RETOURNER RIEN
  RETOURNER Cs + (1 − p) / p × Cf

ALGORITHME ToursMaximaux
ENTRÉES : budget B, fonction de coût croissante C(T)
SORTIE  : le plus grand T tel que C(T) ≤ B
  T ← 0
  TANT QUE C(T + 1) ≤ B FAIRE T ← T + 1 FIN TANT QUE
  RETOURNER T
```

**Complexité.** CoûtDUneTâche est en O(T) pour T tours et O(1) en mémoire. CoûtParSuccès est en O(1). ToursMaximaux appelle C pour chaque T essayé, soit O(T²max) avec un coût en O(T) ; la formule du trinôme (démonstration 6) le ramène à O(1) quand il n'y a ni fenêtre ni cache. Le budget mensuel multiplie simplement par le nombre de tâches (linéarité de l'espérance, démonstration 1).

**Du squelette au code.** L'algorithme est la fonction `cout_tache(tours, n0, delta, sortie, outils, rho)`, avec `rho=None` pour l'absence de cache, `w` pour le facteur d'écriture et `fenetre` pour la fenêtre glissante ; la somme des entrées est `tokens_entree(tours, n0, delta, fenetre)` et un appel isolé `cout_appel(n_in, n_out, outils)`. CoûtParSuccès est `cout_par_succes(c_s, p, c_f)`, qui renvoie `None` pour p = 0 ; le seuil de rentabilité du cache est `seuil_cache(w, rho)` et ToursMaximaux est `tours_max(budget, cout)`. Les quatre cas sont `cas_1_budget_public`, `cas_2_modeles_assur`, `cas_3_contrat_btp` et `cas_4_garde_fou_rh`.
