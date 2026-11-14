# Étape 23 — RAG — Score hybride (cosinus + BM25)

> Étape 23 du parcours · Prérequis : [BM25](<22-RAG-Formule-BM25.md>) · Suite : [Reciprocal Rank Fusion](<24-RAG-Formule-RRF.md>)

**Dossier :** 05-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  
**Nom du fichier :** 23-RAG-Formule-Score-Hybride.md

## Définition

Le score hybride combine deux signaux de pertinence : le signal **sémantique**, un cosinus entre embeddings (étape 19), qui reconnaît les reformulations et les synonymes, et le signal **lexical**, un score BM25 (étape 22), qui reconnaît les mots exacts. On le calcule comme une moyenne pondérée, α fois le premier plus 1 − α fois le second, avec α entre 0 et 1. Les deux signaux n'ont pas la même échelle : un cosinus vit dans [−1, 1] et, en pratique, dans une bande étroite, alors qu'un score BM25 n'a pas de borne supérieure. On les ramène donc tous les deux dans [0, 1] par la **même** normalisation min-max, calculée sur le **même** ensemble de candidats, avant de les combiner. La valeur de α ne se devine pas : on la choisit en mesurant la qualité du classement, par exemple avec NDCG@k, sur des requêtes dont on connaît les bonnes réponses.

## Rôle dans un agent

Le score hybride intervient dans le **retriever**, entre la recherche et la construction du prompt. L'agent perçoit une question ; il lance en parallèle une recherche vectorielle et une recherche BM25, qui renvoient chacune leurs k meilleurs candidats. L'étape de fusion forme l'union des deux listes, normalise les deux signaux, les combine avec α, trie, puis garde les meilleurs passages pour le prompt ou pour un reranker. α est un paramètre de configuration, réglé hors ligne sur un jeu de requêtes étiquetées et surveillé en production ; il peut dépendre du type de requête. Le score hybride ne dit pas si un passage est pertinent dans l'absolu, seulement s'il est meilleur que les autres candidats : la décision « je n'ai pas trouvé » doit s'appuyer sur d'autres signaux.

## Équation complète

Score hybride d'un candidat d :

$$
s(d) = \alpha \, \tilde{s}_{sem}(d) + (1 - \alpha) \, \tilde{s}_{lex}(d)
$$

Ensemble des candidats, union des deux listes renvoyées :

$$
C = L_{sem} \cup L_{lex}
$$

Normalisation min-max d'un signal x sur C (si max = min, le signal ne départage rien et l'on pose x̃ = 0 partout) :

$$
\tilde{x}(d) = \frac{x(d) - \min_{c \in C} x(c)}{\max_{c \in C} x(c) - \min_{c \in C} x(c)}
$$

Critère de choix de α, avec le NDCG démontré à l'étape 28 (Qₑₜ est l'ensemble des requêtes étiquetées qui ont au moins un document pertinent) :

$$
\alpha^{*} = \arg\max_{\alpha \in \{0 ;\, 0{,}1 ;\, \dots ;\, 1\}} \; \frac{1}{\lvert Q_{et} \rvert} \sum_{q \in Q_{et}} \text{NDCG@}k(q, \alpha)
$$

## Décryptage des symboles

$$
d
$$

**Sens :** un document candidat · **Type / plage :** identifiant · **Variable Python :** clé des dictionnaires

$$
s_{sem}(d)
$$

**Sens :** score sémantique brut : cosinus entre la requête et d · **Type / plage :** réel dans [−1, 1] · **Variable Python :** `sem[d]`

$$
s_{lex}(d)
$$

**Sens :** score lexical brut : BM25 de d · **Type / plage :** réel ≥ 0, non borné · **Variable Python :** `lex[d]`

$$
L_{sem},\quad L_{lex}
$$

**Sens :** listes renvoyées par chaque recherche · **Type / plage :** ensembles de documents · **Variable Python :** `sem`, `lex`

$$
C
$$

**Sens :** candidats : l'union des deux listes · **Type / plage :** ensemble · **Variable Python :** `candidats`

$$
\tilde s_{sem},\quad \tilde s_{lex}
$$

**Sens :** scores min-maxés sur C · **Type / plage :** réels dans [0, 1] · **Variable Python :** `s_sem`, `s_lex`

$$
\alpha
$$

**Sens :** poids du signal sémantique · **Type / plage :** réel dans [0, 1] · **Variable Python :** `alpha`

$$
s(d)
$$

**Sens :** score hybride · **Type / plage :** réel dans [0, 1] · **Variable Python :** valeur de `fusion_hybride`

$$
\text{NDCG@}k
$$

**Sens :** qualité du classement des k premiers (étape 28) · **Type / plage :** réel dans [0, 1], ou `None` · **Variable Python :** `ndcg_at_k(classement, pertinences, k)`

Un document absent d'une liste reçoit, pour ce signal, le score brut 0 **avant** la normalisation : c'est la convention de ce parcours quand on ne peut pas recalculer son vrai score (voir le point 2 de la démonstration).

## Démonstration

### 1. Le défaut de l'ancienne formule : contre-exemple chiffré

L'ancienne version de ce fichier combinait un cosinus brut, décrit comme « normalisé (souvent entre 0 et 1) », avec un BM25 min-maxé. Le mot « normalisé » prêtait à confusion : des **vecteurs** normalisés (étape 20) ne donnent pas un **score** ramené dans [0, 1]. Prenons trois candidats A, B et C, de cosinus 0,82, 0,80 et 0,78, et de scores BM25 bruts 2, 5 et 8, que le min-max transforme en 0, 0,5 et 1. Avec α = 0,7, censé favoriser le sémantique :

$$
s(A) = 0{,}7 \times 0{,}82 + 0{,}3 \times 0 = 0{,}574 \qquad s(B) = 0{,}560 + 0{,}150 = 0{,}710 \qquad s(C) = 0{,}546 + 0{,}300 = 0{,}846
$$

Le classement obtenu, C > B > A, est **exactement celui de BM25**, alors que le cosinus classe A > B > C. La raison est un effet d'échelle. Pour deux candidats i et j, l'écart de score vaut α(xᵢ − xⱼ) + (1 − α)(yᵢ − yⱼ), où x est le cosinus et y le BM25 normalisé. Les cosinus ne s'étalent que sur 0,04, donc le premier terme ne dépasse jamais 0,7 × 0,04 = 0,028 ; le second peut atteindre 0,3 × 1 = 0,3. Dès que deux BM25 normalisés diffèrent de plus de 0,028 / 0,3 ≈ 0,093, c'est le lexical qui décide. Le poids qui compte n'est pas α, mais α multiplié par l'étendue du signal.

En normalisant **aussi** les cosinus, ils deviennent 1, 0,5 et 0, et :

$$
s(A) = 0{,}7 \times 1 + 0{,}3 \times 0 = 0{,}70 \qquad s(B) = 0{,}35 + 0{,}15 = 0{,}50 \qquad s(C) = 0 + 0{,}30 = 0{,}30
$$

Les deux signaux ont maintenant la même étendue, 1, et les poids effectifs valent exactement α et 1 − α : avec α = 0,7, l'ordre du cosinus l'emporte, comme prévu.

### 2. La correction : mêmes candidats, même normalisation

On procède en quatre temps. On forme l'union C des deux listes. Pour chaque candidat et chaque signal, on prend le score brut ; un document absent d'une liste reçoit 0 pour ce signal. On min-maxe chaque signal sur C tout entier. On combine. L'ensemble commun est essentiel, parce que le min-max dépend de l'ensemble sur lequel on le calcule : si l'on normalisait chaque liste sur ses seuls documents, le 0 de la liste sémantique et le 0 de la liste lexicale désigneraient deux références différentes, et le dernier document de chaque liste vaudrait autant qu'un document absent.

Exemple : la recherche sémantique renvoie A (0,82), B (0,80) et C (0,78) ; BM25 renvoie C (8), D (6) et B (5). Sur C = {A, B, C, D}, les cosinus bruts deviennent (0,82 ; 0,80 ; 0,78 ; 0), D étant absent, et se normalisent en (1 ; 0,9756 ; 0,9512 ; 0) ; les BM25 bruts (0 ; 5 ; 8 ; 6) se normalisent en (0 ; 0,625 ; 1 ; 0,75). Avec α = 0,7 : C = 0,9659, B = 0,8704, A = 0,7000, D = 0,2250.

Cette convention a un coût qu'il faut connaître. Le 0 attribué à D étire la plage des cosinus de [0,78 ; 0,82] à [0 ; 0,82], si bien que les trois cosinus présents se retrouvent tassés entre 0,95 et 1 : parmi eux, c'est de nouveau BM25 qui départage. Quand on peut recalculer le vrai score d'un document absent, il faut le faire : le cosinus de D se calcule avec son vecteur, stocké dans l'index. Avec son vrai cosinus, 0,70, les cosinus normalisés deviennent (1 ; 0,8333 ; 0,6667 ; 0) et le classement change : B = 0,7708, C = 0,7667, A = 0,7000, D = 0,2250. L'imputation à 0 reste la convention par défaut, prudente, quand le score manquant est inaccessible ; dans les deux cas, on valide le choix par la mesure du point 6.

### 3. Une combinaison convexe de valeurs de [0, 1] reste dans [0, 1]

Soient x et y dans [0, 1] et α dans [0, 1]. Le score α x + (1 − α) y est positif ou nul, parce que c'est une somme de produits de nombres positifs ou nuls. Il est au plus égal à α × 1 + (1 − α) × 1 = 1, parce que x ≤ 1, y ≤ 1 et que les poids sont positifs. Plus précisément, il est compris entre min(x, y) et max(x, y), puisque

$$
\alpha x + (1 - \alpha) y - \min(x, y) = \alpha (x - \min) + (1 - \alpha)(y - \min) \ge 0 ,
$$

et symétriquement pour le maximum. Le score hybride est donc toujours dans [0, 1], et il vaut 1 seulement pour un candidat premier dans les deux signaux.

### 4. Le min-max efface toute transformation affine croissante, et seulement celles-là

Soit yᵢ = a xᵢ + c avec a > 0. Multiplier par un nombre positif et ajouter une constante préservent l'ordre, donc le minimum des y est a xₘᵢₙ + c et le maximum a xₘₐₓ + c. Alors :

$$
\tilde y_i = \frac{(a x_i + c) - (a x_{min} + c)}{(a x_{max} + c) - (a x_{min} + c)} = \frac{a\,(x_i - x_{min})}{a\,(x_{max} - x_{min})} = \tilde x_i
$$

C'est pourquoi l'échelle non bornée de BM25 ne compte plus après normalisation : que la collection fasse grimper tous les scores, ou qu'un moteur les multiplie par une constante, les valeurs normalisées ne bougent pas. Le programme le vérifie avec 10x + 3.

Ce n'est **pas** vrai pour a < 0. Le minimum des y est alors a xₘₐₓ + c et le maximum a xₘᵢₙ + c, et le même calcul donne

$$
\tilde y_i = (x_{max} - x_i)/(x_{max} - x_{min}) = 1 - \tilde x_i
$$

L'ordre est inversé. Conséquence pratique : une **distance**, plus petite quand le document est meilleur, ne se min-maxe pas comme une similarité ; on la convertit d'abord, par exemple

$$
\cos\theta = 1 - d_{\cos}
$$

(étape 21). Ce n'est pas vrai non plus pour une transformation croissante non affine, comme un carré ou un logarithme : l'ordre de chaque signal est préservé, mais les écarts relatifs changent, et le classement hybride peut changer avec eux. RRF, à l'étape 24, n'a pas cette fragilité.

### 5. Cas limites : α extrême, signal plat, score relatif

- Avec α = 1, s = s̃ₛₑₘ : le classement est celui du cosinus, puisque le min-max est une transformation affine croissante qui ne change pas l'ordre. Avec α = 0, c'est celui de BM25.
- Si un signal est plat (max = min, par exemple tous les BM25 nuls parce qu'aucun mot n'est commun), la fonction canonique `min_max` renvoie 0,0 partout : ce signal ne départage rien, le score hybride vaut α s̃ₛₑₘ, et le classement est celui de l'autre signal. Sans cette convention, la division par max − min = 0 lèverait une erreur.
- Dès qu'un signal n'est pas plat, ses valeurs normalisées contiennent toujours un 0 et un 1. Le score hybride est donc **relatif** : des cosinus bruts de 0,21, 0,18 et 0,15, tous médiocres, deviennent 1, 0,5 et 0. Un score hybride de 1 veut dire « meilleur des candidats », pas « pertinent ».

### 6. Choisir α par NDCG@k sur des requêtes étiquetées

Le NDCG@k, démontré à l'[étape 28](<28-RAG-Formule-NDCG.md>), récompense un classement qui place les documents les plus pertinents en tête : chaque document au rang i apporte un gain 2ʳᵉˡ − 1 divisé par log₂(i + 1), et l'on divise le total par celui du classement idéal. On prend trois requêtes étiquetées, avec des pertinences 2 (très pertinent), 1 (utile) ou 0. Les scores bruts ont été choisis comme des images affines de valeurs simples (cosinus = 0,70 + 0,15 × v, BM25 = 2 + 10 × v), de sorte que, par le point 4, les valeurs normalisées sont exactement ces v :

| Requête | Document (pertinence) | s̃ₛₑₘ | s̃ₗₑₓ |
|---|---|---|---|
| reformulée | a (2), b (1), c (0), d (0) | 1 ; 0,8 ; 0,3 ; 0 | 0,4 ; 0 ; 1 ; 0,6 |
| terme exact | e (2), f (0), g (1), h (0) | 0,5 ; 1 ; 0,4 ; 0 | 1 ; 0 ; 0,65 ; 0,2 |
| mixte | i (2), j (0), k (1), l (0) | 1 ; 0,7 ; 0,5 ; 0 | 0,8 ; 0 ; 1 ; 0,2 |

Vérification à la main pour la première requête, à α = 0,5 : a = 0,70, b = 0,40, c = 0,65, d = 0,30, donc le top-3 est a, c, b. Le DCG vaut

$$
3/\log_2 2 + 0 + 1/\log_2 4 = 3 + 0{,}5 = 3{,}5 ;
$$

le classement idéal (a, b) donne 3 + 1/log₂ 3 = 3,6309 ; le NDCG@3 vaut 3,5 / 3,6309 = 0,964. Les deux autres requêtes sont parfaites à α = 0,5 (NDCG@3 = 1), d'où une moyenne de (0,964 + 1 + 1)/3 = 0,988. Le balayage complet donne :

| α | 0 | 0,1 | 0,2 | 0,3 | 0,4 | 0,5 | 0,6 | 0,7 | 0,8 | 0,9 | 1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NDCG@3 moyen | 0,737 | 0,737 | 0,773 | 0,840 | 0,840 | **0,988** | 0,976 | 0,886 | 0,886 | 0,874 | 0,874 |

Le lexical seul (α = 0) rate la requête reformulée ; le sémantique seul (α = 1) rate la requête à terme exact ; α = 0,5 réussit les trois. Une requête sans aucun document pertinent n'a pas de NDCG (`None`) et sort de la moyenne, selon la convention du parcours. L'ancienne version affirmait que « le score hybride est souvent supérieur à l'un ou l'autre seul en production » : ce n'est pas un théorème, c'est une mesure à refaire sur ses propres données. Trois requêtes suffisent pour comprendre la méthode, pas pour régler un système : en production, on en étiquette des centaines.

### 7. Comparaison avec RRF (étape 24)

La Reciprocal Rank Fusion, étudiée à l'étape suivante, fusionne les **rangs** au lieu des scores : chaque liste apporte

$$
1/(k_{RRF} + \text{rang})
$$

à chaque document. Sur le contre-exemple du point 1, les rangs sont A, B, C pour le cosinus et C, B, A pour BM25 ; RRF donne A = C = 0,032266 et B = 0,032258. Elle n'a pas besoin de normalisation ni de α, et elle est insensible à toute transformation croissante des scores ; en échange, elle ignore de combien un document devance l'autre. Le score hybride exploite ces écarts, au prix d'une normalisation soignée et d'un α à régler. L'étape 24 démontre ces propriétés, y compris la raison pour laquelle B, deuxième partout, passe derrière A et C.

## Effets et comportement

- **Augmenter α** donne plus de poids aux reformulations et aux synonymes, au risque de perdre les correspondances exactes (codes, références, noms propres) ; **diminuer α** fait l'inverse. Ces effets ne sont réels que si les deux signaux sont normalisés de la même façon (point 1).
- **Le score hybride est relatif aux candidats** (point 5) : ajouter ou retirer un candidat extrême change les valeurs normalisées de tous les autres.
- **Un signal plat s'efface de lui-même** (point 5), ce qui rend la fusion robuste quand l'une des deux recherches ne trouve rien.
- **Le meilleur α dépend des requêtes** (point 6) : il varie d'un domaine à l'autre, d'une langue à l'autre, et d'un type de requête à l'autre.

## Du symbole au code Python

$$
\tilde x
$$

**Variable ou fonction :** `min_max(valeurs)`, fonction canonique du parcours

$$
C
$$

**Variable ou fonction :** `candidats = sorted(set(sem) \| set(lex))`

$$
s(d)
$$

**Variable ou fonction :** `fusion_hybride(sem, lex, alpha)`

$$
\text{NDCG@}k
$$

**Variable ou fonction :** `ndcg_at_k(classement, pertinences, k)`

$$
\alpha^{*}
$$

**Variable ou fonction :** `choisir_alpha(requetes, grille, k)`

**Symbole :** fusion par les rangs · **Variable ou fonction :** `rrf(classements, k_rrf)`, fonction canonique (étape 24)

### Déroulé, ligne par ligne

**`min_max(valeurs)`** est la fonction canonique. Pour `[2.0, 5.0, 8.0]`, `lo = 2.0` et `hi = 8.0`, et elle renvoie `[0.0, 0.5, 1.0]`. Si `hi == lo`, elle renvoie 0,0 partout au lieu de diviser par zéro.

**`rrf(classements, k_rrf)`** est la fonction canonique de l'étape 24, utilisée ici seulement pour la comparaison du point 7.

**`ancien_hybride(cos_brut, bm25_norm, alpha)`** reproduit l'ancienne formule, pour montrer son défaut : `0.7 * 0.82 + 0.3 * 0.0 = 0.574` pour A.

**`fusion_hybride(sem, lex, alpha)`**. C'est l'équation complète.

- `if not 0.0 <= alpha <= 1.0` : hors de [0, 1], la combinaison n'est plus convexe et le score peut sortir de [0, 1] ; on lève `ValueError`.
- `candidats = sorted(set(sem) | set(lex))` : l'union des deux listes, triée pour que l'ordre de calcul soit toujours le même. Dans l'exemple du point 2 : `['A', 'B', 'C', 'D']`.
- `s_sem = min_max([sem.get(d, 0.0) for d in candidats])` : `sem.get(d, 0.0)` renvoie le cosinus brut, ou 0 si le document est absent de la liste sémantique ; `[0.82, 0.80, 0.78, 0.0]` devient `[1.0, 0.9756, 0.9512, 0.0]`. Même chose pour `s_lex` : `[0.0, 5.0, 8.0, 6.0]` devient `[0.0, 0.625, 1.0, 0.75]`.
- `scores = {d: alpha * x + (1 - alpha) * y ...}` : la combinaison convexe, candidat par candidat.
- `sorted(..., key=lambda kv: (-kv[1], kv[0]))` : score décroissant, nom en cas d'égalité.

**`ndcg_at_k(classement, pertinences, k)`** calcule le DCG des `k` premiers avec le gain `2 ** rel - 1` et la décote `math.log2(i + 1)`, puis le divise par l'IDCG, obtenu en triant les pertinences par ordre décroissant. Si l'IDCG est nul, aucun document n'est pertinent et la fonction renvoie `None`.

**`choisir_alpha(requetes, grille, k)`** calcule, pour chaque `alpha` de la grille, la moyenne des NDCG@k des requêtes, en écartant les `None`, puis renvoie le meilleur `alpha` ; à égalité de moyenne, la clé `(moyennes[a], -a)` retient le plus petit.

**`main()`**, bloc par bloc.

1. Le contre-exemple du point 1 : l'ancienne formule donne 0,574, 0,710 et 0,846, la nouvelle 0,70, 0,50 et 0,30.
2. L'union du point 2 : C = 0,9659, B = 0,8704, A = 0,7000, D = 0,2250 ; puis, avec le vrai cosinus de D (0,70), B passe devant C.
3. Les propriétés des points 3 à 5 : combinaison convexe sur une grille de valeurs ; `min_max` identique pour `x` et `10x + 3`, inversé pour `-x + 3` ; signal lexical plat qui laisse l'ordre sémantique (A vaut 0,5 × 1 = 0,5) ; cosinus médiocres qui deviennent 1, 0,5 et 0.
4. Le balayage du point 6 : la grille `[0.0, 0.1, …, 1.0]`, les onze moyennes, le meilleur `alpha = 0.5` à 0,988, et les NDCG@3 par requête, 0,964, 1 et 1. Le dernier `assert` vérifie qu'une requête sans pertinent renvoie `None`.
5. RRF sur les deux rangements du contre-exemple : A et C à égalité devant B.
6. `alpha = 1.5` doit lever `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`min_max(valeurs)`** — Cette fonction se comporte comme un traducteur qui ramène deux monnaies très différentes, des cosinus voisins de 0,8 et des scores BM25 qui montent jusqu'à 8, sur une même échelle de 0 à 1 : elle reçoit une liste de nombres, repère le minimum et le maximum, puis renvoie pour chaque valeur sa position relative entre ces deux bornes, si bien que [2, 5, 8] devient [0 ; 0,5 ; 1]. Quand toutes les valeurs sont égales, elle renvoie des zéros au lieu de diviser par zéro, car un signal plat ne départage personne. C'est l'étape sans laquelle la pondération α n'aurait aucun sens, puisqu'elle mélangerait des grandeurs incomparables.

**`rrf(classements, k_rrf)`** — C'est un arbitre qui ne regarde que les places sur le podium, jamais les écarts de temps : la fonction reçoit plusieurs classements, chacun étant une liste de documents du meilleur au moins bon, et la constante k, 60 par défaut, puis ajoute à chaque document, pour chaque classement où il figure, la quantité 1 / (k + rang), un document absent n'y gagnant rien. Elle renvoie la liste des couples (document, score) triée par score décroissant, les égalités départagées par le nom ; ici elle ne sert qu'à la comparaison finale, où les rangements A, B, C et C, B, A laissent A et C à égalité devant B.

**`ancien_hybride(cos_brut, bm25_norm, alpha)`** — Cette fonction reconstitue la recette fautive de l'ancien fichier, comme on garde au musée une balance faussée pour montrer d'où venait l'erreur : elle reçoit un cosinus brut, un score BM25 déjà ramené dans [0, 1] et le poids α, 0,7 par défaut, puis renvoie α × cosinus + (1 − α) × BM25. Le défaut tient au mélange des échelles : les cosinus bruts ne s'écartent que de quelques centièmes alors que le BM25 normalisé va de 0 à 1, si bien que A, B et C obtiennent 0,574, 0,710 et 0,846 et suivent l'ordre du BM25, malgré un poids de 0,7 donné au sens.

**`fusion_hybride(sem, lex, alpha)`** — Voici la recette corrigée, celle d'un chef qui pèse tous ses ingrédients sur la même balance avant de les mélanger : la fonction reçoit le dictionnaire des scores sémantiques, celui des scores lexicaux et le poids α, lève `ValueError` si α sort de [0, 1], forme l'union triée des candidats des deux listes, donne le score brut 0 à un document absent d'une liste, normalise chacun des deux signaux par `min_max`, puis calcule α × sémantique + (1 − α) × lexical pour chaque candidat. Elle renvoie les couples (document, score) triés par score décroissant, les égalités départagées par le nom ; sur le contre-exemple, elle rend 0,70, 0,50 et 0,30, l'ordre du cosinus, et sur l'union du point 2, C = 0,9659, B = 0,8704, A = 0,7000 et D = 0,2250.

**`choisir_alpha(requetes, grille, k)`** — Cette fonction est le dégustateur qui goûte la même sauce avec onze dosages différents avant de fixer la recette : elle reçoit une liste de requêtes étiquetées, chacune donnée par ses scores sémantiques, ses scores lexicaux et ses pertinences humaines, une grille de valeurs de α et la profondeur k, 3 par défaut. Pour chaque α, elle fusionne les deux listes avec `fusion_hybride`, mesure le NDCG@k du classement obtenu avec `ndcg_at_k`, écarte les requêtes sans document pertinent, puis fait la moyenne ; elle renvoie le meilleur α, le plus petit en cas d'égalité, et le dictionnaire de toutes les moyennes. Sur les trois requêtes du programme, elle retient α = 0,5 avec un NDCG@3 moyen de 0,988, contre 0,737 pour α = 0 et 0,874 pour α = 1.

**`main()`** — Le chef d'orchestre joue six scènes : il oppose d'abord l'ancienne formule, qui suit l'ordre du BM25 avec 0,574, 0,710 et 0,846, à la fusion corrigée qui retrouve l'ordre du cosinus, puis montre que l'union des listes fait passer B devant C dès qu'on calcule le vrai cosinus de D. Il vérifie ensuite les propriétés de la combinaison convexe et du min-max, invariance par une transformation affine croissante, inversion par une décroissante, signal plat neutre et cosinus médiocres étirés jusqu'à 1, 0,5 et 0. Il balaie la grille de α pour trouver 0,5, compare avec RRF, qui ignore α et les écarts de score, et termine en vérifiant que α = 1,5 lève bien `ValueError`. Chaque valeur est gardée par un `assert`, et la ligne finale n'annonce le succès que si tous ont tenu.

```python
"""Étape 23 — score hybride : mêmes candidats, même normalisation, puis α choisi par NDCG@k."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def min_max(valeurs: list[float]) -> list[float]:
    """Ramène dans [0, 1] ; si toutes les valeurs sont égales, le signal ne départage rien : 0.0 partout."""
    lo, hi = min(valeurs), max(valeurs)
    if hi == lo:
        return [0.0 for _ in valeurs]
    return [(v - lo) / (hi - lo) for v in valeurs]


def rrf(classements: list[list[str]], k_rrf: int = 60) -> list[tuple[str, float]]:
    """Reciprocal Rank Fusion ; un document absent d'un classement y contribue 0. Sortie triée, égalités par nom."""
    scores: dict[str, float] = {}
    for classement in classements:
        for rang, doc in enumerate(classement, start=1):
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (k_rrf + rang)
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))


def ancien_hybride(cos_brut: float, bm25_norm: float, alpha: float = 0.7) -> float:
    """L'ancienne formule, à ne pas utiliser : cosinus brut mélangé à un BM25 min-maxé."""
    return alpha * cos_brut + (1 - alpha) * bm25_norm


def fusion_hybride(sem: dict[str, float], lex: dict[str, float], alpha: float) -> list[tuple[str, float]]:
    """α · sémantique + (1 − α) · lexical, les deux min-maxés sur l'union des candidats."""
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha doit être dans [0, 1]")
    candidats = sorted(set(sem) | set(lex))                  # union, dans un ordre fixe
    s_sem = min_max([sem.get(d, 0.0) for d in candidats])    # absent d'une liste : score brut 0
    s_lex = min_max([lex.get(d, 0.0) for d in candidats])
    scores = {d: alpha * x + (1 - alpha) * y for d, x, y in zip(candidats, s_sem, s_lex)}
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))


def ndcg_at_k(classement: list[str], pertinences: dict[str, int], k: int) -> float | None:
    """NDCG@k avec le gain 2^rel − 1 (démontré à l'étape 28) ; None si aucun document n'est pertinent."""
    dcg = sum((2 ** pertinences.get(d, 0) - 1) / math.log2(i + 1) for i, d in enumerate(classement[:k], start=1))
    ideal = sorted(pertinences.values(), reverse=True)[:k]
    idcg = sum((2 ** r - 1) / math.log2(i + 1) for i, r in enumerate(ideal, start=1))
    return None if idcg == 0 else dcg / idcg


def choisir_alpha(requetes: list[tuple[dict, dict, dict]], grille: list[float], k: int = 3) -> tuple[float, dict[float, float]]:
    """Moyenne de NDCG@k pour chaque α ; les requêtes sans document pertinent (None) sont exclues."""
    moyennes = {}
    for alpha in grille:
        valeurs = [ndcg_at_k([d for d, _ in fusion_hybride(sem, lex, alpha)], rel, k) for sem, lex, rel in requetes]
        valeurs = [v for v in valeurs if v is not None]
        moyennes[alpha] = sum(valeurs) / len(valeurs)
    meilleur = max(grille, key=lambda a: (moyennes[a], -a))   # à égalité, le plus petit α
    return meilleur, moyennes


def main() -> None:
    print("1. Contre-exemple : cosinus brut + BM25 min-maxé, α = 0.7")
    cos_brut = {"A": 0.82, "B": 0.80, "C": 0.78}
    bm25_brut = {"A": 2.0, "B": 5.0, "C": 8.0}
    bm25_norm = dict(zip(bm25_brut, min_max(list(bm25_brut.values()))))
    ancien = {d: ancien_hybride(cos_brut[d], bm25_norm[d]) for d in cos_brut}
    print("  ancien : " + "   ".join(f"{d} = {v:.3f}" for d, v in ancien.items()) + "   → ordre du BM25")
    assert bm25_norm == {"A": 0.0, "B": 0.5, "C": 1.0}
    assert [round(ancien[d], 3) for d in "ABC"] == [0.574, 0.710, 0.846]
    nouveau = fusion_hybride(cos_brut, bm25_brut, 0.7)
    print("  corrigé : " + "   ".join(f"{d} = {v:.2f}" for d, v in nouveau) + "   → ordre du cosinus, comme α = 0.7 le veut")
    assert [d for d, _ in nouveau] == ["A", "B", "C"] and [round(v, 2) for _, v in nouveau] == [0.70, 0.50, 0.30]

    print("2. Union des deux listes ; un absent reçoit le score brut 0 avant normalisation")
    sem = {"A": 0.82, "B": 0.80, "C": 0.78}
    lex = {"C": 8.0, "D": 6.0, "B": 5.0}
    union = fusion_hybride(sem, lex, 0.7)
    print("  " + "   ".join(f"{d} = {v:.4f}" for d, v in union))
    assert [d for d, _ in union] == ["C", "B", "A", "D"]
    assert [round(v, 4) for _, v in union] == [0.9659, 0.8704, 0.7000, 0.2250]
    avec_vrai_cos = fusion_hybride({**sem, "D": 0.70}, lex, 0.7)
    print("  si l'on recalcule le vrai cosinus de D (0.70) : " + "   ".join(f"{d} = {v:.4f}" for d, v in avec_vrai_cos))
    assert [d for d, _ in avec_vrai_cos] == ["B", "C", "A", "D"]

    print("3. Propriétés")
    grille = [i / 10 for i in range(11)]
    for x in (0.0, 0.3, 1.0):
        for y in (0.0, 0.6, 1.0):
            for a in grille:
                assert min(x, y) - 1e-12 <= a * x + (1 - a) * y <= max(x, y) + 1e-12   # reste dans [0, 1]
    brut = [2.0, 5.0, 8.0, 3.5]
    affine = [10 * v + 3 for v in brut]
    inverse = [-1 * v + 3 for v in brut]
    print(f"  min_max(x) = {min_max(brut)}   min_max(10x + 3) = {[round(v, 12) for v in min_max(affine)]}")
    assert [round(v, 12) for v in min_max(affine)] == [round(v, 12) for v in min_max(brut)]
    assert [round(v, 12) for v in min_max(inverse)] == [round(1 - v, 12) for v in min_max(brut)]
    plat = fusion_hybride(sem, {"A": 0.0, "B": 0.0, "C": 0.0}, 0.5)
    print(f"  signal lexical plat (max = min) : {[(d, round(v, 4)) for d, v in plat]} → ordre sémantique")
    assert [d for d, _ in plat] == ["A", "B", "C"] and plat[0][1] == 0.5
    faibles = fusion_hybride({"X": 0.21, "Y": 0.18, "Z": 0.15}, {}, 1.0)
    print(f"  cosinus bruts 0.21 / 0.18 / 0.15 → scores hybrides {[round(v, 2) for _, v in faibles]} : un score relatif")
    assert [round(v, 2) for _, v in faibles] == [1.0, 0.5, 0.0]

    print("4. Choisir α par NDCG@3 sur trois requêtes étiquetées")
    requetes = [
        ({"a": 0.85, "b": 0.82, "c": 0.745, "d": 0.70}, {"a": 6.0, "b": 2.0, "c": 12.0, "d": 8.0},
         {"a": 2, "b": 1, "c": 0, "d": 0}),                    # requête « reformulée » : le sens compte
        ({"e": 0.775, "f": 0.85, "g": 0.76, "h": 0.70}, {"e": 12.0, "f": 2.0, "g": 8.5, "h": 4.0},
         {"e": 2, "f": 0, "g": 1, "h": 0}),                    # requête à terme exact : le mot compte
        ({"i": 0.85, "j": 0.805, "k": 0.775, "l": 0.70}, {"i": 10.0, "j": 2.0, "k": 12.0, "l": 4.0},
         {"i": 2, "j": 0, "k": 1, "l": 0}),                    # requête mixte
    ]
    meilleur, moyennes = choisir_alpha(requetes, grille)
    print("  " + "  ".join(f"{a:.1f}→{moyennes[a]:.3f}" for a in grille))
    print(f"  meilleur α = {meilleur}   NDCG@3 moyen = {moyennes[meilleur]:.3f}   (α = 0 : {moyennes[0.0]:.3f}, α = 1 : {moyennes[1.0]:.3f})")
    assert meilleur == 0.5 and round(moyennes[0.5], 3) == 0.988
    assert round(moyennes[0.0], 3) == 0.737 and round(moyennes[1.0], 3) == 0.874
    par_requete = [ndcg_at_k([d for d, _ in fusion_hybride(s, l, 0.5)], r, 3) for s, l, r in requetes]
    assert [round(v, 3) for v in par_requete] == [0.964, 1.0, 1.0]
    assert ndcg_at_k(["a", "b"], {"a": 0, "b": 0}, 3) is None    # requête sans pertinent : exclue des moyennes

    print("5. Comparaison avec RRF (étape 24) sur le contre-exemple")
    fusion_rangs = rrf([["A", "B", "C"], ["C", "B", "A"]])
    print("  RRF : " + "   ".join(f"{d} = {v:.6f}" for d, v in fusion_rangs) + "   (α et écarts de score ignorés)")
    assert [d for d, _ in fusion_rangs] == ["A", "C", "B"] and fusion_rangs[0][1] == fusion_rangs[1][1]

    print("6. Entrée invalide refusée")
    try:
        fusion_hybride(sem, lex, 1.5)
    except ValueError as e:
        print(f"  alpha = 1.5 → ValueError : {e}")
    else:
        raise AssertionError("alpha hors de [0, 1] aurait dû être refusé")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Contre-exemple : cosinus brut + BM25 min-maxé, α = 0.7
  ancien : A = 0.574   B = 0.710   C = 0.846   → ordre du BM25
  corrigé : A = 0.70   B = 0.50   C = 0.30   → ordre du cosinus, comme α = 0.7 le veut
2. Union des deux listes ; un absent reçoit le score brut 0 avant normalisation
  C = 0.9659   B = 0.8704   A = 0.7000   D = 0.2250
  si l'on recalcule le vrai cosinus de D (0.70) : B = 0.7708   C = 0.7667   A = 0.7000   D = 0.2250
3. Propriétés
  min_max(x) = [0.0, 0.5, 1.0, 0.25]   min_max(10x + 3) = [0.0, 0.5, 1.0, 0.25]
  signal lexical plat (max = min) : [('A', 0.5), ('B', 0.25), ('C', 0.0)] → ordre sémantique
  cosinus bruts 0.21 / 0.18 / 0.15 → scores hybrides [1.0, 0.5, 0.0] : un score relatif
4. Choisir α par NDCG@3 sur trois requêtes étiquetées
  0.0→0.737  0.1→0.737  0.2→0.773  0.3→0.840  0.4→0.840  0.5→0.988  0.6→0.976  0.7→0.886  0.8→0.886  0.9→0.874  1.0→0.874
  meilleur α = 0.5   NDCG@3 moyen = 0.988   (α = 0 : 0.737, α = 1 : 0.874)
5. Comparaison avec RRF (étape 24) sur le contre-exemple
  RRF : A = 0.032266   C = 0.032266   B = 0.032258   (α et écarts de score ignorés)
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un poids α ne pèse ce qu'il annonce que si les deux signaux ont la même étendue. Normaliser les deux de la même façon, sur les mêmes candidats, puis choisir α par une mesure, transforme un réglage au jugé en décision vérifiable.

## Squelette algorithmique

Le score hybride mélange un classement sémantique et un classement lexical. L'algorithme met d'abord les deux scores à la même échelle sur l'union des candidats, puis les pondère par α ; un second algorithme choisit α sur un jeu de requêtes étiquetées.

```text
ALGORITHME FusionHybride
ENTRÉES : scores sémantiques sem (document → score), scores lexicaux lex, α ∈ [0 ; 1]
SORTIE  : les candidats classés par score hybride

  C ← documents de sem ∪ documents de lex            (ordre fixe)
  POUR CHAQUE d DE C FAIRE  x(d) ← sem[d] ou 0 ; y(d) ← lex[d] ou 0  FIN POUR
  x̃ ← MinMax(x sur C) ; ỹ ← MinMax(y sur C)          (0 partout si le signal est constant)
  POUR CHAQUE d DE C FAIRE  s(d) ← α x̃(d) + (1 − α) ỹ(d)  FIN POUR
  trier par s décroissant (égalités par nom) ; RETOURNER le classement

ALGORITHME ChoisirAlpha
ENTRÉES : requêtes étiquetées (sem, lex, pertinences), grille d'α (0 ; 0,1 ; … ; 1), k
  POUR CHAQUE α de la grille FAIRE
      moyenne(α) ← moyenne de NDCG@k(FusionHybride(sem, lex, α)) sur les requêtes qui ont un pertinent
  FIN POUR
  RETOURNER l'α de meilleure moyenne (à égalité, le plus petit)
```

**Complexité.** Une fusion coûte O(|C|) pour les normalisations et O(|C| log |C|) pour le tri. Choisir α coûte (taille de la grille) × (nombre de requêtes) fusions, plus un NDCG@k par fusion : avec 11 valeurs d'α et Q requêtes, O(11 × Q × |C| log |C|). Ce réglage se fait hors ligne, une fois, sur le jeu d'évaluation.

**Du squelette au code.** `FusionHybride` correspond à `fusion_hybride` (qui appelle `min_max`), `ChoisirAlpha` à `choisir_alpha` (qui appelle `ndcg_at_k`). `ancien_hybride` reproduit l'erreur de l'ancienne version, qui mélangeait un cosinus brut et un BM25 normalisé, et `rrf` sert de point de comparaison avec la fusion par les rangs.

## Cas d'usage réels aux Émirats

Les volumes, les valeurs de α et les seuils ci-dessous sont illustratifs : chaque équipe les mesure sur ses propres requêtes étiquetées.

### Banque — un « 70 % sémantique » qui ne l'était pas

L'assistant clients d'une banque de détail de Dubaï combine une recherche vectorielle et BM25 sur 3 000 fiches produits et pages de FAQ, avec l'ancienne formule et α = 0,7, que l'équipe lisait comme « 70 % de sémantique ». Dans les journaux, les cosinus des vingt premiers candidats restent entre 0,78 et 0,84, tandis que le BM25 normalisé s'étale de 0 à 1 : comme au point 1 de la démonstration, c'est BM25 qui décide de l'ordre. Le symptôme est concret : un client qui demande « puis-je solder mon financement avant l'échéance ? » reçoit la page qui répète « solder » et « échéance », celle du relevé de carte, au lieu de la page sur le remboursement anticipé d'un prêt personnel, rédigée avec d'autres mots. Après la correction, avec les deux signaux min-maxés sur l'union des candidats, les questions reformulées retrouvent la bonne fiche, et l'équipe choisit α par NDCG@5 sur 300 questions étiquetées au lieu de le fixer au jugé. Les conditions de remboursement anticipé des prêts aux particuliers sont encadrées par la CBUAE (à confirmer avec le texte en vigueur) : une mauvaise page, c'est une information erronée donnée au client. Les indicateurs suivis sont le NDCG@5 à chaque mise en production et le taux de conversations transférées à un conseiller.

### Immobilier — un α par type de requête

Le moteur de recherche d'une agence et d'un promoteur de Dubaï et d'Abu Dhabi reçoit deux familles de requêtes : des codes et des noms (« B-1204 », le nom d'un projet off-plan) et des descriptions (« trois chambres avec vue sur la mer, près d'une école »). Sur des requêtes étiquetées de chaque famille, le meilleur α diffère nettement, par exemple 0,2 pour les codes et 0,7 pour les descriptions. L'agent reconnaît la famille par une règle simple, la présence d'un motif de code d'unité ou d'un nom de projet connu, et applique le α correspondant. Chaque valeur est choisie par NDCG@10 sur sa propre famille : une moyenne globale masquerait qu'un α unique de 0,5 est médiocre pour les deux. Sans cette séparation, un acheteur qui tape un code reçoit des unités « semblables » en tête, ce qui est trompeur pour une annonce soumise aux règles de la RERA. On suit le NDCG@10 par famille de requêtes et le taux de visites programmées.

### Assurance — les bons candidats, et leurs vrais scores

L'assistant des gestionnaires de sinistres d'un assureur auto et santé cherche les clauses de police applicables : vingt candidats par la recherche vectorielle, vingt par BM25, soit une trentaine de clauses après union. Au départ, l'équipe normalisait chaque liste sur ses seuls documents : la dernière clause de chaque liste recevait 0, exactement comme une clause absente, et les deux 0 ne désignaient pas la même référence. Elle est passée à la normalisation sur l'union, avec un score brut de 0 pour les absents, puis, puisque les vecteurs des clauses sont stockés, elle recalcule le vrai cosinus des clauses trouvées par BM25 seul au lieu de leur attribuer 0, ce qui évite le tassement des cosinus montré au point 2. L'agent cite la clause et son numéro au gestionnaire, qui décide ; il ne refuse jamais un sinistre de lui-même. L'assureur est supervisé par la CBUAE, et une décision sur un sinistre doit reposer sur la clause exacte. L'indicateur suivi est le Recall@10 de la bonne clause (étape 25) sur des sinistres étiquetés.

### Crypto — changer de modèle d'embedding sans tout casser

L'agent de surveillance d'une plateforme d'actifs virtuels agréée par la VARA cherche les procédures et les incidents passés avec un score hybride. L'équipe change de modèle d'embedding, et les cosinus des candidats passent d'une bande de 0,70 à 0,90 à une bande de 0,30 à 0,50. Si ce changement n'était qu'une transformation affine croissante, le min-max l'absorberait exactement et le classement hybride ne bougerait pas (point 4) ; mais un nouveau modèle change aussi la forme de la distribution et l'ordre relatif de certains documents. L'équipe relance donc le balayage de α sur son jeu étiqueté avant de basculer, et compare le NDCG@5 des deux versions. Elle renonce aussi à tout seuil absolu sur le score hybride, qui est relatif aux candidats (point 5). Les indicateurs suivis sont le NDCG@5 de chaque version du modèle et le délai moyen de résolution des incidents.

### RH — quand le signal lexical est plat

Un cabinet RH présent dans plusieurs émirats répond, en arabe et en anglais, à des questions sur des politiques rédigées surtout en anglais. Pour une question en arabe face à des documents en anglais, BM25 ne trouve aucun mot commun : tous les scores lexicaux valent 0. Avec la fonction canonique `min_max`, ce signal plat devient 0,0 partout (point 5) : le score hybride se réduit à α fois le score sémantique et le classement est exactement celui de la recherche vectorielle, au lieu d'un mélange avec du bruit. Une normalisation écrite à la main, qui divise par max − min sans précaution, lèverait une division par zéro sur chacune de ces questions. L'équipe indexe en plus une version arabe des politiques clés, normalisée comme à l'étape 22, pour que BM25 contribue de nouveau aux questions en arabe, notamment sur l'indemnité de fin de service prévue par le décret-loi fédéral 33/2021. L'indicateur suivi est le NDCG@5 mesuré séparément pour chaque langue.

### BTP — un score hybride de 1 ne veut pas dire « trouvé »

L'agent de contrôle des factures d'un groupe de construction actif sur de grands chantiers à Dubaï cherche, pour chaque ligne de facture, l'article correspondant du cahier des charges et du bordereau de prix. Un jour, une ligne porte sur un article absent du marché : tous les cosinus bruts sont faibles (0,21, 0,18, 0,15) et aucun mot ne correspond. Après min-max, le meilleur candidat obtient pourtant 1 (point 5) ; si l'agent prenait ce score pour une confiance, il rattacherait la ligne à un article sans rapport. L'équipe ajoute une garde sur les signaux **bruts** : si le meilleur cosinus brut reste sous 0,5 et qu'aucun mot ne correspond, l'agent répond « article absent du marché » et envoie la ligne en revue. Payer un article hors marché, TVA de 5 % comprise, est une perte sèche, et les retenues de garantie se calculent sur des montants qui doivent être justes. L'indicateur suivi est le nombre de lignes mal rattachées découvertes lors des audits.

## Pièges et limites

- **Mélanger un score brut et un score normalisé** : le contre-exemple du point 1 montre que le signal le plus étalé décide, quel que soit α.
- **Normaliser chaque liste séparément** : le 0 de chaque liste n'a plus le même sens ; on normalise sur l'union des candidats.
- **Imputer 0 sans le savoir** : la convention est prudente mais tasse les autres valeurs du signal (point 2) ; on recalcule le vrai score quand c'est possible.
- **Min-maxer une distance** : l'ordre s'inverse (point 4) ; on convertit d'abord la distance en similarité.
- **Prendre le score hybride pour une confiance** : il est relatif aux candidats (point 5) ; la décision « je n'ai pas trouvé » se prend sur les signaux bruts ou avec un reranker. De même, un candidat aberrant, par exemple un BM25 dix fois plus grand que les autres, écrase tous les autres scores normalisés vers 0.

### Exercice feuille blanche

1. Sans regarder le code, écrire `fusion_hybride` à partir de l'équation complète (union, score brut 0 pour un absent, `min_max`, combinaison convexe, tri), puis vérifier que le contre-exemple donne A, B, C à α = 0,7.
2. Prédire, puis vérifier : sur le même contre-exemple, les deux signaux étant min-maxés, quel est l'ordre à α = 0,3 ? (Réponse : A = 0,3, B = 0,5, C = 0,7, donc C, B, A : avec α < 0,5, l'ordre de BM25 l'emporte, cette fois parce qu'on l'a demandé.)
3. Trouver le bug : `s_sem = min_max(list(sem.values()))` et `s_lex = min_max(list(lex.values()))`, puis `zip(candidats, s_sem, s_lex)`. Pourquoi les scores sont-ils attribués aux mauvais documents ?

## Pour aller plus loin

D'autres normalisations existent : le z-score, qui centre chaque signal sur sa moyenne et le divise par son écart-type, résiste mieux à un candidat aberrant mais ne borne plus les valeurs ; certaines méthodes normalisent à partir de la distribution des scores observée sur de nombreuses requêtes plutôt que sur les seuls candidats du moment. On peut aussi apprendre la combinaison, par exemple par une régression logistique sur des paires étiquetées, au lieu d'un seul α. Enfin, dans beaucoup de systèmes, le score hybride ne fait que présélectionner quelques dizaines de passages, qu'un reranker plus coûteux reclasse ensuite.

> Suite : [Reciprocal Rank Fusion](<24-RAG-Formule-RRF.md>) — étape 24.
