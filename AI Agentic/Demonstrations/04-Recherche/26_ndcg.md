# 26 — NDCG : démonstrations

> Fiche : [26 — NDCG](<../../Images/04-Recherche/26_ndcg.md>) · Image : `26_ndcg.jpg` · Leçon : [Étape 28 — NDCG](<../../05-RAG/28-RAG-Formule-NDCG.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
\operatorname{NDCG@}k = \frac{\operatorname{DCG@}k}{\operatorname{IDCG@}k}, \qquad \operatorname{DCG@}k = \sum_{i=1}^{k} \frac{2^{\,rel_i} - 1}{\log_2(i + 1)}
$$

relᵢ est la pertinence graduée du résultat au rang i (par exemple 0 à 3). Le gain 2^rel − 1 récompense fortement les très bons documents ; la remise 1/log₂(i + 1) les récompense davantage s'ils sont en haut. IDCG est le DCG du classement idéal.

Précision de la leçon 28 : le classement idéal se construit avec les notes de **tous** les documents jugés pour la question, retrouvés ou non, triées par ordre décroissant et tronquées à k. Quand aucun document jugé n'est pertinent, IDCG@k = 0 et le NDCG est indéfini : la fonction renvoie `None`, et la question sort de la moyenne.

## Les symboles, un par un

$$
k
$$

Le nombre de rangs évalués, entier ≥ 1 ; argument `k`. Une valeur inférieure à 1 lève `ValueError`.

$$
i
$$

Le rang, de 1 à k, 1 pour le premier résultat ; variable `i` de `enumerate(..., start=1)`.

$$
rel_i
$$

La note du document de rang i dans la liste retrouvée, entier ≥ 0 (ici de 0 à 3), 0 pour un document non jugé ; élément de `rels_retrouves`.

$$
rel^*_i
$$

La i-ième plus grande note parmi tous les documents jugés ; élément de `sorted(rels_tous_juges, reverse=True)`.

$$
g(rel)
$$

Le gain d'un document, g(rel) = 2^rel − 1 : 0, 1, 3 et 7 pour les notes 0 à 3 ; fonction `gain_exponentiel(rel)`, et sa variante `gain_lineaire(rel)` qui renvoie la note elle-même.

$$
w_i
$$

La remise du rang i, wᵢ = 1/log₂(i + 1), réel dans ]0 ; 1], strictement décroissant ; fonction `remise(i)`.

$$
\operatorname{DCG@}k
$$

Le gain cumulé actualisé de la liste retrouvée, réel ≥ 0 ; fonction `dcg_at_k(rels, k, gain)`.

$$
\operatorname{IDCG@}k
$$

Le DCG du classement idéal de tous les documents jugés, tronqué à k, réel ≥ 0 ; `dcg_at_k(sorted(rels_tous_juges, reverse=True), k)`.

$$
\operatorname{NDCG@}k
$$

Le rapport des deux, réel dans [0 ; 1], indéfini (`None`) si l'IDCG est nul ; fonction `ndcg_at_k(rels_retrouves, rels_tous_juges, k, gain)`.

## Le mécanisme, avant les preuves

Le NDCG reçoit deux listes de notes : celles des documents que le moteur a renvoyés, dans l'ordre, et celles de tous les documents que des experts ont jugés pour la question. Chaque note passe d'abord par le gain 2^rel − 1, qui l'étire : les notes 0, 1, 2, 3 deviennent 0, 1, 3, 7, si bien qu'un document parfait vaut plus que deux bons réunis (démonstration 4). Le gain est ensuite multiplié par la remise de son rang, 1/log₂(i + 1) : 1 au rang 1, environ 0,63 au rang 2, 0,5 au rang 3, puis une baisse de plus en plus lente. Pourquoi un logarithme et pas 1/i ? Parce que 1/i écraserait presque tout ce qui suit le rang 2 (le MRR fait ce choix, fichier 33) ; le logarithme garde un poids réel aux rangs 3 à 10, là où l'agent lit encore. Le DCG additionne ces contributions sur les k premiers rangs : c'est une somme, parce que chaque document lu apporte sa propre information. Ce total n'a pas d'échelle fixe : il dépend du nombre de documents pertinents qui existent pour la question. On le divise donc par le meilleur total possible, l'IDCG, obtenu en rangeant les meilleures notes jugées dans l'ordre décroissant ; le rapport tombe entre 0 et 1 et devient comparable d'une question à l'autre. La division explique aussi pourquoi l'IDCG doit venir de tous les documents jugés : s'il venait de la liste retrouvée, un moteur qui ne trouve rien de bon mais range bien ses mauvais résultats aurait un score parfait (démonstration 6).

Petit film chiffré : trois documents suivis à travers le gain et la remise.

| Document | Note | Gain 2^rel − 1 | Rang | Remise | Contribution |
|---|---|---|---|---|---|
| parfait, en tête | 3 | 7 | 1 | 1 | 7 |
| parfait, troisième | 3 | 7 | 3 | 0,5 | 3,5 |
| bon, deuxième | 2 | 3 | 2 | 0,63093 | 1,89279 |

Le même document parfait perd la moitié de sa contribution en descendant du rang 1 au rang 3 ; un bon document au rang 2 rapporte encore moins qu'un parfait au rang 3.

## Démonstration 1 — La remise décroît avec le rang

**Ce qu'on démontre.** La remise wᵢ = 1/log₂(i + 1) est strictement décroissante en i, vaut 1 au rang 1 et reste strictement positive :

$$
1 = w_1 > w_2 > w_3 > \dots > 0
$$

**L'idée.** log₂(i + 1) croît avec i, donc son inverse décroît ; il vaut log₂ 2 = 1 au rang 1, et il ne s'annule jamais parce que log₂(i + 1) reste fini.

**La preuve, pas à pas.**

**Étape 1.** La fonction x ↦ log₂ x est strictement croissante sur ]0 ; +∞[, donc i < j entraîne log₂(i + 1) < log₂(j + 1).

**Étape 2.** Pour i ≥ 1, log₂(i + 1) ≥ log₂ 2 = 1 > 0 ; la fonction inverse étant strictement décroissante sur ]0 ; +∞[ :

$$
i < j \;\Longrightarrow\; \frac{1}{\log_2(i + 1)} > \frac{1}{\log_2(j + 1)} > 0
$$

**Étape 3.** Au rang 1, w₁ = 1/log₂ 2 = 1. ∎

**Vérification chiffrée.** Les remises des rangs 1 à 5 valent 1 ; 1/log₂ 3 ≈ 0,63093 ; 1/2 = 0,5 ; 1/log₂ 5 ≈ 0,43068 ; 1/log₂ 6 ≈ 0,38685 ; au rang 10, 1/log₂ 11 ≈ 0,28906. Le programme vérifie la décroissance stricte jusqu'au rang 100. Contre-exemple quand on compte les rangs à partir de 0 : la remise du premier serait 1/log₂ 1 = 1/0, une division par zéro.

**Ce que la preuve révèle du mécanisme.** La remise baisse fort entre les rangs 1 et 2 (−37 %), puis de plus en plus lentement : le dixième rang garde encore près de 29 % du poids du premier. Le NDCG valorise donc toute la tête de liste, pas seulement le premier document.

**Conséquence pour un agent.** k doit être égal au nombre de documents que l'agent injecte réellement dans son contexte : au-delà, la remise donne encore du poids à des documents que le modèle ne lira jamais.

## Démonstration 2 — Échanger deux documents mal ordonnés augmente le DCG

**Ce qu'on démontre.** Si une liste place un gain g au rang i et un gain plus grand g′ > g à un rang j > i plus bas, échanger les deux documents augmente le DCG exactement de :

$$
(g' w_i + g w_j) - (g w_i + g' w_j) = (g' - g)(w_i - w_j) > 0
$$

**L'idée.** L'échange déplace le meilleur document vers une remise plus forte et le moins bon vers une remise plus faible ; seuls ces deux termes changent, et le bilan est le produit de deux écarts positifs.

**La preuve, pas à pas.**

**Étape 1.** Les autres rangs ne bougent pas, donc la variation du DCG se limite aux deux termes échangés.

**Étape 2.** On développe et on factorise, parce que g′wᵢ − gwᵢ = (g′ − g)wᵢ et gwⱼ − g′wⱼ = −(g′ − g)wⱼ :

$$
g' w_i + g w_j - g w_i - g' w_j = (g' - g)\,w_i - (g' - g)\,w_j = (g' - g)(w_i - w_j)
$$

**Étape 3.** g′ − g > 0 par hypothèse, et wᵢ − wⱼ > 0 par la démonstration 1 puisque i < j : le produit est positif. ∎

**Vérification chiffrée.** La liste (2 ; 3 ; 0 ; 1) a les gains 3 et 7 aux rangs 1 et 2 ; les échanger rapporte (7 − 3)(1 − 0,63093) ≈ 1,47628, et le DCG@4 passe de 7,84718 à 9,32347. Le programme vérifie l'énoncé sur toutes les permutations de (0 ; 2 ; 3 ; 1) et tous les couples de voisins mal ordonnés. Contre-exemple quand l'hypothèse g′ > g manque : échanger deux documents de même note ne change rien, (g′ − g) = 0.

**Ce que la preuve révèle du mécanisme.** Le bénéfice d'un échange est le produit d'un écart de qualité par un écart de position : remonter un document parfait au-dessus d'un document hors sujet en tête de liste rapporte beaucoup ; corriger l'ordre de deux documents moyens en bas de liste presque rien.

**Conséquence pour un agent.** Un reranker doit d'abord corriger les erreurs en tête de liste ; le NDCG lui donne exactement ce signal d'entraînement, avec un poids proportionnel à (g′ − g)(wᵢ − wⱼ).

## Démonstration 3 — Le classement idéal est le maximum, donc 0 ≤ NDCG ≤ 1

**Ce qu'on démontre.** Si les notes de la liste retrouvée proviennent des jugements (chaque note positive retrouvée correspond à un document jugé distinct), alors :

$$
0 \le \operatorname{DCG@}k \le \operatorname{IDCG@}k, \qquad 0 \le \operatorname{NDCG@}k \le 1 \quad (\operatorname{IDCG@}k > 0)
$$

Si IDCG@k = 0, aucun document jugé n'est pertinent et le NDCG est indéfini : on renvoie `None`.

**L'idée.** Le meilleur top-k possible prend les k meilleures notes jugées et les range dans l'ordre décroissant : c'est l'inégalité de réarrangement (associer les plus grands gains aux plus grandes remises), et c'est la définition de l'IDCG.

**La preuve, pas à pas.**

**Étape 1.** Tant qu'une liste contient deux documents mal ordonnés, un échange l'améliore strictement (démonstration 2) ; comme il n'y a qu'un nombre fini d'ordres, le maximum est atteint par une liste sans paire mal ordonnée, donc triée par gain décroissant.

**Étape 2.** Remplacer un document de la liste par un document jugé de meilleure note ne fait jamais baisser le DCG, parce que chaque remise est positive. Le meilleur top-k utilise donc les k meilleures notes jugées, triées : son DCG est l'IDCG.

**Étape 3.** Tous les gains et toutes les remises sont ≥ 0, donc DCG ≥ 0 ; en divisant DCG ≤ IDCG par IDCG > 0, on obtient 0 ≤ NDCG ≤ 1. ∎

**Vérification chiffrée.** Avec les sept notes jugées (3, 3, 2, 1, 1, 0, 0) de la leçon 28, le programme énumère les 2 520 façons de ranger cinq d'entre eux : le meilleur DCG@5 vaut 13,73404, exactement l'IDCG@5. Une question sans aucun pertinent jugé donne `None`. Contre-exemple quand l'hypothèse manque : une liste (3 ; 3) face aux jugements (3) contient un document noté 3 que personne n'a jugé ; sans la garde, le rapport vaudrait 11,41651/7 ≈ 1,63093 > 1. La fonction `ndcg_at_k` refuse ce cas par `ValueError`.

**Ce que la preuve révèle du mécanisme.** La borne 1 n'est pas une simple normalisation : c'est un théorème qui suppose un idéal construit sur les mêmes jugements que la liste. Le NDCG mesure donc la distance à un optimum réellement atteignable.

**Conséquence pour un agent.** Avant de comparer deux moteurs, on fait noter les nouveaux documents de leur top-k ; sinon, un document non jugé compte 0 et un moteur qui ramène de bons documents inédits paraît moins bon. On exclut des moyennes les questions sans pertinent (valeur `None`), au lieu de les compter 0.

## Démonstration 4 — Pourquoi 2^rel − 1 et pas rel

**Ce qu'on démontre.** Avec le gain exponentiel, un document parfait (note 3) vaut plus que deux bons (note 2) réunis, et le choix du gain peut inverser le classement de deux moteurs :

$$
2^3 - 1 = 7 > (2^2 - 1) + (2^2 - 1) = 6
$$

En pertinence binaire (notes 0 ou 1), les deux gains coïncident, puisque 2⁰ − 1 = 0 et 2¹ − 1 = 1.

**L'idée.** Le gain exponentiel double presque à chaque note : il traduit l'idée qu'un document excellent change la décision, alors que plusieurs documents moyens ne la changent pas.

**La preuve, pas à pas.**

**Étape 1.** Les gains valent 2⁰ − 1 = 0, 2¹ − 1 = 1, 2² − 1 = 3 et 2³ − 1 = 7 ; 7 > 3 + 3.

**Étape 2.** Plus généralement, 2ⁿ⁺¹ − 1 = 2(2ⁿ − 1) + 1 > 2(2ⁿ − 1) : chaque note vaut plus que le double de la précédente.

**Étape 3.** Pour l'inversion, il suffit d'un exemple chiffré (ci-dessous). ∎

**Vérification chiffrée.** Avec les jugements (2 ; 1 ; 1 ; 1), comparons A qui renvoie (2 ; 0 ; 0), un très bon document puis du bruit, et B qui renvoie (1 ; 1 ; 1), trois documents moyens. En gain exponentiel, IDCG@3 = 3 + 0,63093 + 0,5 ≈ 4,1309, A obtient 0,7262 et B 0,5158 : A gagne. En gain linéaire, IDCG@3 ≈ 3,1309, A obtient 0,6388 et B 0,6806 : B gagne. Contre-exemple en binaire : les deux gains donnent le même NDCG, et la question du choix ne se pose pas.

**Ce que la preuve révèle du mécanisme.** Le gain est un choix métier, pas un détail technique : exponentiel quand un document excellent suffit à décider (la règle exacte, la clause applicable), linéaire quand chaque document utile apporte à peu près autant.

**Conséquence pour un agent.** On écrit toujours le gain et k à côté du chiffre (« NDCG@5, gain exponentiel ») ; deux NDCG calculés avec des gains différents ne se comparent pas.

## Démonstration 5 — Ce qui ne change pas le NDCG, et ce qui le change

**Ce qu'on démontre.** (a) Multiplier tous les gains par une constante c > 0 ne change pas le NDCG. (b) Changer la base du logarithme des remises ne le change pas non plus. (c) En revanche, le NDCG@k n'est pas monotone en k.

$$
\frac{\sum c\, g_i\, w_i}{\sum c\, g^*_i\, w_i} = \frac{\sum g_i\, w_i}{\sum g^*_i\, w_i}, \qquad \log_b(i + 1) = \frac{\ln(i + 1)}{\ln b}
$$

**L'idée.** Une constante commune au numérateur et au dénominateur se simplifie. Mais augmenter k ajoute des termes au numérateur et au dénominateur à des rythmes différents, si bien que le rapport peut monter ou descendre.

**La preuve, pas à pas.**

**Étape 1.** Pour (a), c se met en facteur dans les deux sommes, puis se simplifie, parce que c ≠ 0.

**Étape 2.** Pour (b), passer de la base 2 à la base b multiplie chaque remise par la même constante ln b/ln 2 (au DCG comme à l'IDCG), qui se simplifie comme en (a).

**Étape 3.** Pour (c), un contre-exemple suffit (ci-dessous). ∎

**Vérification chiffrée.** Avec les jugements (3 ; 3) et la liste (3 ; 0 ; 3) : NDCG@1 = 7/7 = 1 ; NDCG@2 = 7/(7 + 7 × 0,63093) = 7/11,41651 ≈ 0,6131 ; NDCG@3 = (7 + 7 × 0,5)/11,41651 = 10,5/11,41651 ≈ 0,9197 : la valeur baisse puis remonte. Sur l'exemple simple, le NDCG@4 recalculé avec des logarithmes décimaux vaut encore 0,83545, et tripler tous les gains ne le change pas. Contre-exemple pour (a) quand la constante n'est pas commune : changer seulement le gain de la note 3 (de 7 à 10, par exemple) change les rapports, donc le NDCG.

**Ce que la preuve révèle du mécanisme.** Les unités ne comptent pas, la forme des gains et la coupure k comptent. Le NDCG@k mesure la qualité d'un top-k précis, pas une qualité « en général ».

**Conséquence pour un agent.** On compare toujours deux moteurs au même k, et l'on choisit k avant de regarder les résultats ; changer de k après coup pour flatter un moteur est un biais.

## Démonstration 6 — Un idéal tiré de la liste retrouvée surestime toujours le NDCG

**Ce qu'on démontre.** Notons NDCG_ancien le rapport calculé avec un idéal obtenu en triant la liste retrouvée elle-même (l'erreur corrigée par la leçon 28). Si la liste retrouvée provient des jugements :

$$
\operatorname{NDCG}_{ancien}@k \ge \operatorname{NDCG@}k
$$

avec égalité si et seulement si le top-k retrouvé contient déjà les k meilleures notes jugées.

**L'idée.** L'ancien idéal ne voit que ce qui a été retrouvé ; il ignore les documents pertinents manqués, donc il est plus petit que le vrai idéal, et diviser par un nombre plus petit donne un rapport plus grand.

**La preuve, pas à pas.**

**Étape 1.** Les notes retrouvées sont une partie des notes jugées ; par la démonstration 3, le meilleur DCG possible avec une partie des notes est au plus le meilleur DCG avec toutes les notes :

$$
\operatorname{IDCG}_{ancien}@k \le \operatorname{IDCG@}k
$$

**Étape 2.** Le numérateur DCG@k est le même dans les deux rapports ; diviser un nombre positif par un dénominateur plus petit donne un résultat plus grand. ∎

**Vérification chiffrée.** Trois documents sont pertinents (note 1) et le moteur n'en trouve qu'un, au rang 1 : la liste (1 ; 0 ; 0) donne NDCG_ancien = 1, un score parfait, alors que le vrai idéal (1 ; 1 ; 1) a IDCG@3 = 1 + 0,63093 + 0,5 ≈ 2,1309 et NDCG@3 ≈ 0,4693. Le programme vérifie l'inégalité sur toutes les listes de quatre documents tirées des sept jugés de la démonstration 3. Contre-exemple quand l'hypothèse manque : si la liste contient une note absente des jugements, l'inégalité de l'étape 1 peut tomber, et la garde de `ndcg_at_k` lève `ValueError`.

**Ce que la preuve révèle du mécanisme.** L'ancien calcul mesurait seulement si le moteur avait bien rangé ce qu'il avait trouvé, jamais s'il avait trouvé les bons documents : un moteur pauvre mais bien ordonné obtenait 1.

**Conséquence pour un agent.** Une barrière de déploiement fondée sur l'ancien calcul laisserait passer un index qui perd des documents pertinents (cas 2). On calcule l'IDCG sur tous les jugés, et l'on garde l'ancien calcul seulement comme contre-exemple.

## Exemple simple, à la main

Quatre passages de pertinences 3, 2, 1, 0. Classement idéal (3 ; 2 ; 1 ; 0), gains 7, 3, 1, 0. Les remises des rangs 1 à 4 valent 1 ; 0,63093 ; 0,5 ; 0,43068.

**Étape 1, l'IDCG.** 3 × 0,63093 ≈ 1,89279 au rang 2, 1 × 0,5 au rang 3 :

$$
\operatorname{IDCG@}4 = 7 + 3 \times 0{,}63093 + 1 \times 0{,}5 + 0 \approx 7 + 1{,}89279 + 0{,}5 = 9{,}39279
$$

**Étape 2, le DCG.** Le retriever renvoie (2 ; 3 ; 0 ; 1), de gains 3, 7, 0, 1 ; 7 × 0,63093 ≈ 4,41651 au rang 2, 1 × 0,43068 au rang 4 :

$$
\operatorname{DCG@}4 = 3 + 7 \times 0{,}63093 + 0 + 1 \times 0{,}43068 \approx 3 + 4{,}41651 + 0{,}43068 = 7{,}84718
$$

**Étape 3, le rapport.**

$$
\operatorname{NDCG@}4 = \frac{7{,}84718}{9{,}39279} \approx 0{,}83545
$$

## Cas d'usage complexes, démontrés

### Cas 1 — [BANQUE] : comparer deux retrievers sur une question de remboursement anticipé

**Contexte.** Une banque de détail de Dubaï doit choisir entre deux retrievers pour son assistant clients. Sur la question « remboursement anticipé d'un prêt personnel : quels frais ? », des experts ont noté six passages de 0 à 3 : 3 pour la règle applicable et le barème à jour, 2 pour la procédure interne, 1 pour une FAQ générale, 0 pour un passage hors sujet. L'agent n'injecte que les deux premiers passages dans son prompt. Les notes et les listes sont illustratives.

**Données.**

- Notes jugées : 3, 3, 2, 1, 0, 0.
- Retriever X renvoie (3 ; 0 ; 2 ; 1 ; 0).
- Retriever Y renvoie (1 ; 3 ; 2 ; 0 ; 0).
- k = 5 pour l'évaluation, 2 pour ce que l'agent lit ; gain exponentiel.

**Calcul pas à pas.**

**Étape 1, l'IDCG@5.** Idéal (3 ; 3 ; 2 ; 1 ; 0) :

$$
\operatorname{IDCG@}5 = 7 + 7 \times 0{,}63093 + 3 \times 0{,}5 + 1 \times 0{,}43068 + 0 \approx 13{,}34718
$$

**Étape 2, les DCG@5.** X : 7 + 0 + 1,5 + 0,43068 ≈ 8,93068. Y : 1 + 4,41651 + 1,5 + 0 + 0 ≈ 6,91651.

**Étape 3, les NDCG@5 :**

$$
\operatorname{NDCG}_X@5 = \frac{8{,}93068}{13{,}34718} \approx 0{,}66911, \qquad \operatorname{NDCG}_Y@5 = \frac{6{,}91651}{13{,}34718} \approx 0{,}51820
$$

**Étape 4, ce que l'agent lit (k = 2).** IDCG@2 = 7 + 7 × 0,63093 ≈ 11,41651 ; X : 7/11,41651 ≈ 0,61315 ; Y : (1 + 4,41651)/11,41651 ≈ 0,47445.

**Décision de l'agent.** La banque choisit X : il place un passage parfait en tête, là où le modèle le lit d'abord, alors que Y commence par une FAQ générale. Le compromis : X ne retrouve qu'un des deux passages parfaits, comme Y ; aucun des deux n'atteint 0,7, et la banque garde X tout en planifiant un reranker.

**Contre-calcul.** Les métriques binaires ne tranchent pas, ou tranchent à l'envers. La Precision@5 (notes > 0) vaut 3/5 = 0,6 pour les deux ; le MRR vaut 1 pour les deux, puisque chacun a un document pertinent au rang 1. Le NDCG binaire préfère même Y : 1,93068/2,56161 ≈ 0,75370 pour X contre 2,13093/2,56161 ≈ 0,83187 pour Y. Choisir Y donnerait au modèle une FAQ en premier passage, qui peut être en retard sur le barème : une réponse fausse sur des frais est une erreur de conformité.

**Sensibilité.** La valeur de bascule est la note du premier document de Y : avec une note 2 au lieu de 1, son DCG@5 monterait à 8,91651, encore 0,01417 sous celui de X ; il faut une note 3 (DCG@5 = 12,91651) pour que Y passe devant. La comparaison se joue donc sur le premier rang.

**En production.** L'indicateur suivi est le NDCG@5 hebdomadaire sur un échantillon de questions notées, avec une alerte s'il baisse de plus de 0,05 (illustratif), et la part des réponses qui citent le barème à jour. Les informations sur un prêt personnel doivent rester cohérentes avec les règles de la CBUAE (montant au plus 20 fois le salaire, durée au plus 48 mois).

### Cas 2 — [IMMO] : trois comparables pour estimer un appartement à Al Reem Island

**Contexte.** Une agence qui opère à Dubaï et à Abu Dhabi estime un deux-chambres de 1 250 sqft à Al Reem Island à partir des trois meilleurs comparables de son historique, moyennés en AED/sqft. Les métadonnées permettent de noter chaque transaction de 0 à 3 (3 : même tour et même type ; 2 : même quartier ; 1 : quartier voisin ; 0 : bien non comparable). La règle de l'agent : estimer seulement si le NDCG@3 atteint 0,8, sinon élargir la recherche et reclasser. Les prix et les notes sont illustratifs.

**Données.**

- Notes jugées des huit transactions de l'historique : 3, 3, 2, 2, 1, 1, 0, 0.
- Top-3 retrouvé : c1 (note 2, 1 650 AED/sqft), c2 (note 3, 1 720 AED/sqft), c3 (villa non comparable, note 0, 2 400 AED/sqft).
- L'autre comparable noté 3, c4, à 1 700 AED/sqft, n'a pas été retrouvé.
- Surface : 1 250 sqft ; seuil de NDCG@3 : 0,8 ; frais DLD de 4 % pour l'acheteur à Dubaï (rappel dans la réponse).

**Calcul pas à pas.**

**Étape 1, le DCG@3.** (2 ; 3 ; 0) donne 3 + 7 × 0,63093 + 0 ≈ 7,41651.

**Étape 2, l'IDCG@3.** Les trois meilleures notes jugées sont (3 ; 3 ; 2) : 7 + 4,41651 + 1,5 ≈ 12,91651.

**Étape 3, le NDCG@3 :**

$$
\operatorname{NDCG@}3 = \frac{7{,}41651}{12{,}91651} \approx 0{,}57419 < 0{,}8
$$

**Étape 4, les deux estimations :**

$$
\text{brute} = \frac{1\,650 + 1\,720 + 2\,400}{3} \times 1\,250 \approx 1\,923{,}3 \times 1\,250 \approx 2\,404\,167 \ \text{AED}, \qquad \text{reclassée} = \frac{1\,720 + 1\,700 + 1\,650}{3} \times 1\,250 = 2\,112\,500 \ \text{AED}
$$

**Décision de l'agent.** Le NDCG@3 vaut 0,57419, sous le seuil : l'agent n'estime pas avec ce top-3. Il élargit la recherche dans le même quartier, reclasse, obtient (c2 ; c4 ; c1) de notes (3 ; 3 ; 2), soit NDCG@3 = 1, et annonce 2 112 500 AED, en rappelant que l'estimation reste indicative. Le compromis : la deuxième recherche coûte un appel de plus, mais elle évite d'inclure une villa dans la moyenne.

**Contre-calcul.** L'ancien calcul, avec un idéal tiré de la liste retrouvée (3 ; 2 ; 0), donnerait 7,41651/8,89279 ≈ 0,83399 ≥ 0,8 : l'agent accepterait le top-3 et annoncerait 2 404 167 AED, 291 667 AED de trop (+13,8 %). Le vendeur afficherait un prix trop haut, et l'acheteur, qui paiera en plus 4 % de frais DLD (84 500 AED sur 2 112 500 AED), perdrait du temps sur un bien surévalué.

**Sensibilité.** La valeur de bascule porte sur la note du troisième comparable, les deux premiers étant (2 ; 3) : note 0, 1 ou 2, le NDCG@3 vaut 0,57419, 0,61290 ou 0,69032, toujours sous 0,8 ; il faut un troisième comparable noté 3 pour atteindre 0,84516. Autrement dit, avec un premier comparable seulement noté 2, il faut les deux comparables parfaits dans le top-3.

**En production.** L'indicateur suivi est le NDCG@3 moyen par quartier et l'écart médian entre l'estimation et le prix final de vente, avec une alerte si cet écart dépasse 5 % (illustratif). Les frais de transfert du DLD valent 4 % de la valeur du bien à Dubaï ; une estimation produite par un agent ne remplace pas une évaluation officielle.

### Cas 3 — [RH] : un salaire versé en retard par le WPS

**Contexte.** Un cabinet RH présent dans plusieurs émirats répond aux salariés de ses clients. Un salarié du secteur privé demande quoi faire quand son salaire, versé par le système WPS, arrive en retard. Les jugements notent 3 la procédure applicable (MOHRE et WPS), 2 la politique de paie de l'employeur, 1 une FAQ générale, 0 un passage d'un autre régime, par exemple celui du DIFC. L'agent garde trois passages. Les notes sont illustratives.

**Données.**

- Notes jugées : 3, 2, 1, 1, 0, 0.
- Liste retrouvée : (1 ; 0 ; 2 ; 3 ; 0), c'est-à-dire FAQ, passage DIFC, politique de paie, procédure applicable, hors sujet.
- Après filtre par régime et reclassement : (3 ; 2 ; 1 ; 1 ; 0).
- k = 3 (ce que l'agent garde) et k = 5 (évaluation).

**Calcul pas à pas.**

**Étape 1, le DCG@3 retrouvé.** (1 ; 0 ; 2) : 1 + 0 + 3 × 0,5 = 2,5.

**Étape 2, l'IDCG@3.** (3 ; 2 ; 1) : 7 + 1,89279 + 0,5 ≈ 9,39279.

**Étape 3, les NDCG :**

$$
\operatorname{NDCG@}3 = \frac{2{,}5}{9{,}39279} \approx 0{,}26616, \qquad \operatorname{NDCG@}5 \approx 0{,}56138
$$

**Étape 4, après filtre.** (3 ; 2 ; 1 ; 1 ; 0) donne NDCG@3 = NDCG@5 = 1.

**Décision de l'agent.** Avec 0,26616, la procédure applicable n'est pas dans les trois passages gardés : l'agent applique un filtre par régime (secteur privé fédéral, pas DIFC) avant le reclassement, et répond à partir de la procédure, en citant la politique de paie en complément. Le compromis : le filtre suppose de connaître le régime du salarié ; s'il est inconnu, l'agent le demande avant de répondre.

**Contre-calcul.** En gain linéaire, le NDCG@3 vaut 0,42000 ; en pertinence binaire (note > 0), 0,70392 : la FAQ et la politique de paie comptent alors autant que la procédure, et le problème paraît mineur alors que la source applicable manque. Une réponse tirée du passage DIFC appliquerait à un salarié du secteur privé les règles d'un autre régime : conseil faux, et risque de litige.

**Sensibilité.** L'écart entre les trois mesures montre la sensibilité au choix du gain : 0,26616 (exponentiel), 0,42000 (linéaire), 0,70392 (binaire). À k = 5, la procédure entre dans la fenêtre au rang 4 et le NDCG@5 remonte à 0,56138 : un agent qui garderait cinq passages la verrait, au prix d'un contexte plus long.

**En production.** L'indicateur suivi est le NDCG@3 par régime (secteur privé fédéral, DIFC, ressortissants émiriens), avec une alerte sous 0,8 (illustratif). Les démarches liées au WPS et au MOHRE sont à confirmer avec le texte en vigueur ; le DIFC a son propre régime d'emploi.

### Cas 4 — [BTP] : la barrière de déploiement d'un nouvel index

**Contexte.** Un groupe de construction qui mène de grands chantiers à Dubaï fait répondre ses ingénieurs de site par un agent qui cherche dans les spécifications techniques. Avant de déployer un nouvel index, l'équipe calcule le NDCG@5 sur un jeu de questions notées (3 : spécification approuvée du projet ; 2 : standard du groupe ; 1 : fiche fabricant ; 0 : autre projet). Règle de déploiement : moyenne des NDCG@5 définis ≥ 0,85, et pas plus de 0,02 sous l'ancien index. Le jeu, réduit ici à trois questions, et les seuils sont illustratifs.

**Données.**

- Q1, jugements (3 ; 2 ; 1) : ancien index (3 ; 2 ; 0 ; 1 ; 0), nouvel index (3 ; 2 ; 1 ; 0 ; 0).
- Q2, une question sur un lot sans document pertinent, jugements (0 ; 0) : les deux index renvoient (0 ; 0 ; 0 ; 0 ; 0).
- Q3, jugements (3 ; 2 ; 1 ; 1) : ancien index (2 ; 3 ; 1 ; 0 ; 0), nouvel index (3 ; 1 ; 2 ; 0 ; 0).

**Calcul pas à pas.**

**Étape 1, Q1.** Ancien : DCG@5 = 7 + 1,89279 + 0 + 0,43068 ≈ 9,32347, IDCG@5 ≈ 9,39279, NDCG ≈ 0,99262 ; nouveau : 1,0.

**Étape 2, Q2.** IDCG@5 = 0 : NDCG indéfini, `None`, pour les deux index.

**Étape 3, Q3.** Ancien ≈ 0,80588 (la spécification du projet au rang 2) ; nouveau ≈ 0,92950.

**Étape 4, les moyennes des valeurs définies :**

$$
\overline{\operatorname{NDCG}}_{ancien} = \frac{0{,}99262 + 0{,}80588}{2} \approx 0{,}89925, \qquad \overline{\operatorname{NDCG}}_{nouveau} = \frac{1 + 0{,}92950}{2} \approx 0{,}96475
$$

**Décision de l'agent.** Le nouvel index passe la barrière (0,96475 ≥ 0,85 et au-dessus de l'ancien) : il est déployé. Q2 est signalée à part, comme une question à laquelle le corpus ne sait pas répondre, au lieu d'être comptée comme un échec du moteur. Le compromis : trois questions ne suffisent pas à conclure en vrai ; la règle est la même avec quelques centaines de questions.

**Contre-calcul.** Si l'on compte Q2 comme 0 au lieu de `None`, les moyennes tombent à 0,59950 et 0,64317 : le nouvel index, pourtant meilleur, serait bloqué par la règle des 0,85, et chaque question sans réponse possible tirerait la moyenne vers le bas. Si un ingénieur suivait le standard du groupe au lieu de la spécification du projet, l'écart serait une non-conformité à reprendre sur le chantier.

**Sensibilité.** Avec Q1 à 1, la moyenne atteint 0,85 dès que Q3 atteint 0,7. En plaçant la spécification du projet au rang p de Q3 (les autres documents dans l'ordre 2, 1, 0, 0), le NDCG@5 vaut 0,95616 au rang 1, 0,80588 au rang 2, 0,72591 au rang 3 et 0,67651 au rang 4 : la valeur de bascule est le rang 4, où le déploiement serait refusé.

**En production.** L'indicateur suivi est le NDCG@5 moyen par projet à chaque version d'index, avec la barrière ci-dessus, et la part des réponses qui citent la spécification du projet. Les spécifications approuvées font partie du contrat ; les retenues de garantie ne se libèrent qu'une fois les non-conformités levées.

## Entraînement sur feuille A4

**Exercice 1.** Calculer les remises des rangs 1 à 4.

**Exercice 2.** Classement (3 ; 3). Calculer DCG@2. Puis (0 ; 3) et (3 ; 0).

**Exercice 3.** Démontrer que NDCG ne change pas si l'on multiplie tous les gains par une constante.

**Exercice 4.** Un classement a NDCG@5 = 1. Que peut-on dire de lui ?

**Exercice 5.** Pertinences (1 ; 2) contre l'idéal (2 ; 1). Calculer le NDCG@2.

**Exercice 6 (modifier un cas).** Dans le cas 2, le troisième comparable retrouvé est c4 (note 3) au lieu de la villa c3. Calculer le NDCG@3 et dire si l'agent estime directement.

**Exercice 7 (trouver l'erreur).** Pour la liste (0 ; 0 ; 1) face aux jugements (1 ; 1 ; 1), un collègue écrit `idcg = dcg_at_k(sorted(rels_retrouves, reverse=True), k)` et obtient NDCG@3 = 0,5. Trouver l'erreur et donner la bonne valeur.

**Exercice 8 (redémontrer de mémoire).** Sans regarder la démonstration 2, montrer qu'échanger un gain g au rang i et un gain g′ > g au rang j > i augmente le DCG de (g′ − g)(wᵢ − wⱼ), puis vérifier sur (2 ; 3 ; 0 ; 1).

## Corrigé

**Exercice 1.** 1/log₂ 2 = 1 ; 1/log₂ 3 ≈ 0,63093 ; 1/log₂ 4 = 1/2 ; 1/log₂ 5 ≈ 0,43068.

**Exercice 2.** (3 ; 3) : 7 + 7 × 0,63093 ≈ 11,41651. (0 ; 3) : 0 + 7 × 0,63093 ≈ 4,41651. (3 ; 0) : 7 + 0 = 7.

**Exercice 3.** Avec des gains c gᵢ, le DCG devient c × DCG et l'IDCG c × IDCG (les mêmes remises) ; le rapport c × DCG/(c × IDCG) se simplifie par c > 0 (démonstration 5).

**Exercice 4.** Son DCG@5 est égal à l'IDCG@5 : ses cinq premiers documents portent les cinq meilleures notes jugées, triées par ordre décroissant (aux ex æquo près). Cela suppose IDCG@5 > 0.

**Exercice 5.** DCG = 1 + 3 × 0,63093 ≈ 2,89279 ; IDCG = 3 + 1 × 0,63093 = 3,63093 ; NDCG ≈ 2,89279/3,63093 ≈ 0,79671.

**Exercice 6.** La liste devient (2 ; 3 ; 3) : DCG@3 = 3 + 4,41651 + 7 × 0,5 = 10,91651 ; IDCG@3 = 12,91651 ; NDCG@3 ≈ 0,84516 ≥ 0,8. L'agent estime directement, avec (1 650 + 1 720 + 1 700)/3 × 1 250 = 2 112 500 AED, la même estimation qu'après reclassement.

**Exercice 7.** L'idéal est calculé sur la liste retrouvée : trier (0 ; 0 ; 1) donne (1 ; 0 ; 0), d'IDCG 1, et le DCG vaut 1 × 0,5, d'où 0,5. Le bon idéal vient de tous les jugés, (1 ; 1 ; 1), d'IDCG ≈ 2,1309, d'où NDCG@3 = 0,5/2,1309 ≈ 0,23464 (démonstration 6).

**Exercice 8.** Étape 1 : seuls les rangs i et j changent. Étape 2 : la variation vaut g′wᵢ + gwⱼ − gwᵢ − g′wⱼ = (g′ − g)wᵢ − (g′ − g)wⱼ = (g′ − g)(wᵢ − wⱼ). Étape 3 : g′ > g et wᵢ > wⱼ (la remise décroît), donc le produit est positif. Vérification : échanger les rangs 1 et 2 de (2 ; 3 ; 0 ; 1) rapporte (7 − 3)(1 − 0,63093) ≈ 1,47628, et 7,84718 + 1,47628 = 9,32347 (à l'arrondi près), le DCG@4 de (3 ; 2 ; 0 ; 1).

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`remise(i)`** — Cette fonction est le métronome du programme, qui dit combien l'attention du lecteur s'émousse à mesure qu'il descend dans la liste, comme un spectateur qui regarde de moins en moins les rangs du fond : elle reçoit un rang `i`, compté à partir de 1, et renvoie 1 / log₂(i + 1). Elle donne 1 au rang 1, environ 0,63093 au rang 2, 0,5 au rang 3, 0,43068 au rang 4 et 0,28906 au rang 10, et c'est elle qui pondère chaque gain dans `dcg_at_k` ; `main` vérifie qu'elle décroît strictement sur les cent premiers rangs.

**`gain_exponentiel(rel)`** — Celle-ci est le barème des récompenses qui fait d'un document excellent une vraie trouvaille : elle reçoit une note de pertinence entière `rel` et renvoie 2ʳᵉˡ − 1, soit 0, 1, 3 et 7 pour les notes 0, 1, 2 et 3. Ce barème qui double presque à chaque marche fait qu'un document noté 3 vaut plus que deux documents notés 2, puisque 7 dépasse 3 + 3 ; c'est le gain par défaut de `dcg_at_k` et de `ndcg_at_k`, celui qui permet de préférer le retriever X dans le cas bancaire.

**`gain_lineaire(rel)`** — Cette fonction est le barème plat que l'on oppose au précédent, comme un juge qui donne autant de points qu'il y a d'étoiles sans jamais récompenser l'exceptionnel : elle reçoit une note `rel` et la renvoie telle quelle. Passée en paramètre `gain` à `dcg_at_k` ou `ndcg_at_k`, elle sert dans la démonstration 4 à montrer que le choix du gain peut inverser deux moteurs, 0,6388 contre 0,6806 au lieu de 0,7262 contre 0,5158, et dans le cas RH à obtenir le NDCG@3 linéaire de 0,42.

**`dcg_at_k(rels, k, gain)`** — Voici le caissier qui additionne les gains d'une liste en appliquant à chacun la remise de son rang : la fonction reçoit la liste des notes `rels` dans l'ordre du classement, la profondeur `k` et une fonction de gain, exponentielle par défaut. Elle lève une `ValueError` si `k` vaut moins de 1 ou si une note est négative, puis, pour les `k` premières notes seulement, multiplie le gain de chacune par `remise` de son rang et additionne le tout ; elle renvoie ce DCG, par exemple 7,84718 pour la liste (2 ; 3 ; 0 ; 1) de l'exemple simple et 9,39279 pour l'idéal (3 ; 2 ; 1 ; 0).

**`ndcg_at_k(rels_retrouves, rels_tous_juges, k, gain)`** — Cette fonction joue l'examinateur qui compare la copie rendue au corrigé parfait, en prenant soin de bâtir ce corrigé à partir de tous les documents jugés et non de la seule liste retrouvée : elle reçoit les notes de la liste retrouvée, les notes de tous les documents jugés, la profondeur `k` et la fonction de gain. Elle vérifie d'abord, en comparant deux `Counter`, que la liste retrouvée ne contient pas de note positive absente des jugements, et lève sinon une `ValueError`, puis calcule l'IDCG sur les jugements triés par ordre décroissant ; elle renvoie `None` si cet IDCG est nul, faute de document pertinent, et sinon le rapport DCG / IDCG, compris entre 0 et 1, soit 0,66911 pour le retriever X du cas bancaire.

**`ancien_ndcg(rels, k)`** — Cette fonction reproduit volontairement une erreur, comme un professeur qui montre au tableau la faute à ne pas commettre : elle reçoit une liste de notes `rels` et une profondeur `k`, et divise le DCG de la liste par celui de la même liste triée, c'est-à-dire par un idéal tiré de ce qui a été retrouvé et non de tous les jugés. Elle renvoie un score toujours au moins égal au vrai NDCG, 1,0 pour la liste (1 ; 0 ; 0) quand le vrai vaut 0,4693, ou 0,83399 au lieu de 0,57419 dans le cas immobilier, et elle n'a aucune garde, si bien qu'une liste toute à zéro y provoquerait une division par zéro.

**`moyenne_definie(valeurs)`** — Cette petite fonction est le comptable scrupuleux qui refuse de compter comme une note zéro un examen qui n'a pas eu lieu : elle reçoit une liste de NDCG dont certains peuvent valoir `None`, écarte ces valeurs indéfinies, puis renvoie la moyenne des valeurs restantes, ou `None` s'il n'en reste aucune. Dans le cas de construction, elle donne 0,89925 pour l'ancien index et 0,96475 pour le nouveau, là où compter la question sans document pertinent comme 0 ferait tomber les moyennes à 0,5995 et 0,64317.

**`r(x, n)`** — Ce minuscule outil est le copiste qui met les nombres au propre avant de les comparer au texte : il reçoit un nombre `x` et un nombre de décimales `n`, arrondit `x` à `n` décimales avec `round` et ajoute 0.0, ce qui remplace un éventuel zéro négatif par un zéro ordinaire. Il renvoie ce nombre arrondi, et la plupart des `assert` de `main` passent par lui pour confronter les DCG et les NDCG aux valeurs à cinq décimales de la fiche, comme 13,34718 pour l'IDCG@5 du cas bancaire.

**`cas_1_retrievers_banque()`** — Cette fonction rejoue la scène d'une banque de détail qui doit choisir entre deux retrievers pour une question de remboursement anticipé : sans paramètre, elle part des notes jugées (3, 3, 2, 1, 0, 0), de la liste de X (3 ; 0 ; 2 ; 1 ; 0) et de celle de Y (1 ; 3 ; 2 ; 0 ; 0), et calcule l'IDCG@5 de 13,34718, les DCG@5 de 8,93068 et 6,91651, les NDCG@5 de 0,66911 et 0,5182 et les NDCG@2 de 0,61315 et 0,47445. Elle calcule aussi la Precision@5, 0,6 pour les deux, le NDCG binaire, qui préfère Y à tort, et le DCG@5 de Y quand on change la note de son premier document de 0 à 3, imprime deux lignes et renvoie le dictionnaire de tous ces résultats.

**`cas_2_comparables_immo()`** — Ici, la fonction joue l'estimateur d'une agence immobilière qui ne veut chiffrer un appartement de 1 250 sqft qu'avec de bons comparables : sans paramètre, elle part des huit notes jugées et du top-3 retrouvé (2 ; 3 ; 0), calcule le NDCG@3 de 0,57419, sous le seuil de 0,8, puis l'ancien calcul trompeur à 0,83399, l'estimation brute d'environ 2 404 167 AED qui inclut la villa à 2 400 AED/sqft et l'estimation reclassée de 2 112 500 AED. Elle calcule enfin le NDCG@3 selon la note du troisième comparable, 0,57419, 0,6129, 0,69032 et 0,84516 pour les notes 0 à 3, imprime deux lignes et renvoie un dictionnaire qui contient aussi le NDCG de 1 obtenu après reclassement.

**`cas_3_paie_rh()`** — Cette fonction se met dans la peau d'un assistant RH à qui un salarié demande quoi faire quand son salaire arrive en retard : sans paramètre, elle part des jugements (3, 2, 1, 1, 0, 0), de la liste retrouvée (1 ; 0 ; 2 ; 3 ; 0) et de la liste filtrée (3 ; 2 ; 1 ; 1 ; 0), et calcule pour k = 3 et k = 5 le NDCG en gain exponentiel, en gain linéaire, en pertinence binaire et après filtre. Elle imprime 0,26616, 0,42 et 0,70392 à k = 3, puis 0,56138, 0,63399 et 0,7537 à k = 5, avec 1 après filtre dans les deux cas, et renvoie ces résultats avec le DCG@3 de 2,5 et l'IDCG@3 de 9,39279.

**`cas_4_deploiement_btp()`** — Cette fonction joue le gardien de la barrière de déploiement d'un nouvel index de spécifications techniques : sans paramètre, elle calcule le NDCG@5 des trois questions pour l'ancien et le nouvel index, soit 0,99262, `None` et 0,80588 contre 1, `None` et 0,9295, en fait la moyenne des seules valeurs définies avec `moyenne_definie`, et la compare à la fausse moyenne qui compte `None` comme 0. Elle décide le déploiement si la moyenne du nouvel index atteint 0,85 sans tomber plus de 0,02 sous l'ancien, ce qui est le cas avec 0,96475, cherche les rangs de la spécification dans Q3 pour lesquels la barrière tient encore, 1, 2 et 3, imprime deux lignes et renvoie un dictionnaire de tous ces éléments.

**`q3_avec_spec_au_rang(p)`** — Cette fonction interne vit dans `cas_4_deploiement_btp`, où elle joue un petit théâtre de sensibilité : elle reçoit un rang `p`, glisse la spécification du projet, notée 3, à cette place dans la liste (2 ; 1 ; 0 ; 0), et calcule le NDCG@5 de la question Q3 face à ses jugements (3 ; 2 ; 1 ; 1). Elle renvoie 0,95616 au rang 1, 0,80588 au rang 2, 0,72591 au rang 3 et 0,67651 au rang 4, ce qui permet au cas de trouver qu'au rang 4 la moyenne avec Q1 tomberait sous 0,85 et que le déploiement serait refusé.

**`main()`** — C'est le chef d'orchestre qui fait jouer toute la fiche : il suit d'abord trois documents à travers gain, remise et contribution, vérifie que la remise décroît, que l'échange de deux voisins mal ordonnés rapporte 1,47628 dans l'exemple et augmente toujours le DCG sur toutes les permutations de quatre notes, que l'idéal est bien le maximum des 2 520 rangements de 5 documents parmi 7, que le NDCG renvoie `None` sans pertinent et lève une `ValueError` pour une note étrangère aux jugements. Il montre ensuite que le choix du gain peut inverser deux moteurs, que multiplier les gains ou changer la base du logarithme ne change rien, que l'ancien idéal surestime toujours le score, refait l'exemple simple à 0,83545, appelle les quatre cas en confrontant chaque nombre par un `assert` et recalcule le corrigé avant d'imprimer le message final.

```python
"""Démonstration 26 — NDCG : remise, échange de voisins, réarrangement, gain 2^rel − 1, invariances, idéal sur tous les jugés, quatre cas."""
import itertools
import math
import sys
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def remise(i: int) -> float:
    """Facteur de remise du rang i (compté à partir de 1) : 1 / log2(i + 1)."""
    return 1.0 / math.log2(i + 1)


def gain_exponentiel(rel: int) -> float:
    return 2 ** rel - 1


def gain_lineaire(rel: int) -> float:
    return rel


def dcg_at_k(rels: list[int], k: int, gain=gain_exponentiel) -> float:
    """DCG@k = somme, pour i de 1 à k, de gain(rel_i) / log2(i + 1)."""
    if k < 1:
        raise ValueError("k doit être un entier >= 1")
    if any(x < 0 for x in rels):
        raise ValueError("une note de pertinence est un entier >= 0")
    return sum(gain(x) * remise(i) for i, x in enumerate(rels[:k], start=1))


def ndcg_at_k(rels_retrouves: list[int], rels_tous_juges: list[int], k: int, gain=gain_exponentiel) -> float | None:
    """NDCG@k (leçon 28) : l'IDCG vient de TOUS les documents jugés ; None si aucun n'est pertinent."""
    manque = Counter(x for x in rels_retrouves if x > 0) - Counter(x for x in rels_tous_juges if x > 0)
    if manque:
        raise ValueError(f"notes retrouvées absentes des jugements : {dict(manque)}")
    idcg = dcg_at_k(sorted(rels_tous_juges, reverse=True), k, gain)
    if idcg == 0.0:
        return None
    return dcg_at_k(rels_retrouves, k, gain) / idcg


def ancien_ndcg(rels: list[int], k: int) -> float:
    """L'erreur corrigée par la leçon 28 : l'« idéal » tiré de la liste RETROUVÉE elle-même."""
    return dcg_at_k(rels, k) / dcg_at_k(sorted(rels, reverse=True), k)


def moyenne_definie(valeurs: list[float | None]) -> float | None:
    """Moyenne des seules valeurs définies ; None s'il n'y en a aucune."""
    d = [v for v in valeurs if v is not None]
    return sum(d) / len(d) if d else None


def r(x: float, n: int) -> float:
    return round(x, n) + 0.0


def cas_1_retrievers_banque() -> dict:
    """[BANQUE] Comparer deux retrievers sur la question du remboursement anticipé d'un prêt personnel."""
    pool, x, y = [3, 3, 2, 1, 0, 0], [3, 0, 2, 1, 0], [1, 3, 2, 0, 0]
    binaire = lambda l: [1 if v > 0 else 0 for v in l]
    res = {"idcg": dcg_at_k(sorted(pool, reverse=True), 5), "dcg_x": dcg_at_k(x, 5), "dcg_y": dcg_at_k(y, 5),
           "x5": ndcg_at_k(x, pool, 5), "y5": ndcg_at_k(y, pool, 5), "x2": ndcg_at_k(x, pool, 2), "y2": ndcg_at_k(y, pool, 2),
           "p5": (sum(binaire(x)) / 5, sum(binaire(y)) / 5),
           "bin": (ndcg_at_k(binaire(x), binaire(pool), 5), ndcg_at_k(binaire(y), binaire(pool), 5)),
           "y_g": [dcg_at_k([g, 3, 2, 0, 0], 5) for g in range(4)]}
    print(f"Cas 1 — BANQUE : IDCG@5 {res['idcg']:.5f} ; X {res['dcg_x']:.5f} → {res['x5']:.5f} ; Y {res['dcg_y']:.5f} → {res['y5']:.5f} ;"
          f" NDCG@2 X {res['x2']:.5f}, Y {res['y2']:.5f}")
    print(f"  P@5 {res['p5'][0]} = {res['p5'][1]} ; NDCG binaire X {res['bin'][0]:.5f} < Y {res['bin'][1]:.5f} ;"
          f" Y avec un premier noté 2 : {res['y_g'][2]:.5f} < {res['dcg_x']:.5f}, noté 3 : {res['y_g'][3]:.5f}")
    return res


def cas_2_comparables_immo() -> dict:
    """[IMMO] Estimer un deux-chambres de 1 250 sqft à Al Reem Island avec les trois meilleurs comparables."""
    juges = [3, 3, 2, 2, 1, 1, 0, 0]
    retrouves = [2, 3, 0]                                   # c1 (noté 2), c2 (noté 3), c3 villa non comparable (0)
    prix = {"c1": 1650, "c2": 1720, "c3": 2400, "c4": 1700}  # AED/sqft ; c4 est l'autre comparable noté 3
    surface = 1250
    n3 = ndcg_at_k(retrouves, juges, 3)
    ancien = ancien_ndcg(retrouves, 3)
    estimation_brute = (prix["c1"] + prix["c2"] + prix["c3"]) / 3 * surface
    estimation_reclassee = (prix["c2"] + prix["c4"] + prix["c1"]) / 3 * surface
    troisieme = [ndcg_at_k([2, 3, g], juges, 3) for g in range(4)]
    print(f"Cas 2 — IMMO : DCG@3 {dcg_at_k(retrouves, 3):.5f} / IDCG@3 {dcg_at_k([3, 3, 2], 3):.5f} = {n3:.5f} ;"
          f" ancien calcul {ancien:.5f} ; estimations {estimation_brute:.0f} contre {estimation_reclassee:.0f} AED")
    print("  troisième comparable noté 0, 1, 2, 3 → " + ", ".join(f"{v:.5f}" for v in troisieme))
    return {"n3": n3, "ancien": ancien, "brute": estimation_brute, "reclassee": estimation_reclassee,
            "troisieme": troisieme, "dcg": dcg_at_k(retrouves, 3), "idcg": dcg_at_k([3, 3, 2], 3),
            "apres": ndcg_at_k([3, 3, 2], juges, 3)}


def cas_3_paie_rh() -> dict:
    """[RH] Retard de salaire versé par le WPS : la source applicable doit être en tête."""
    juges, retrouves, apres = [3, 2, 1, 1, 0, 0], [1, 0, 2, 3, 0], [3, 2, 1, 1, 0]
    binaire = lambda l: [1 if v > 0 else 0 for v in l]
    res = {k: (ndcg_at_k(retrouves, juges, k), ndcg_at_k(retrouves, juges, k, gain_lineaire),
               ndcg_at_k(binaire(retrouves), binaire(juges), k), ndcg_at_k(apres, juges, k)) for k in (3, 5)}
    print("Cas 3 — RH : " + " ; ".join(f"@{k} exponentiel {v[0]:.5f}, linéaire {v[1]:.5f}, binaire {v[2]:.5f}, après filtre {v[3]:.1f}"
                                     for k, v in res.items()))
    return {"res": res, "dcg3": dcg_at_k(retrouves, 3), "idcg3": dcg_at_k(sorted(juges, reverse=True), 3)}


def cas_4_deploiement_btp() -> dict:
    """[BTP] Barrière de déploiement d'un nouvel index : moyenne des NDCG@5 définis, seuil 0.85."""
    ancien_index = {"Q1": ([3, 2, 0, 1, 0], [3, 2, 1]), "Q2": ([0, 0, 0, 0, 0], [0, 0]), "Q3": ([2, 3, 1, 0, 0], [3, 2, 1, 1])}
    nouvel_index = {"Q1": ([3, 2, 1, 0, 0], [3, 2, 1]), "Q2": ([0, 0, 0, 0, 0], [0, 0]), "Q3": ([3, 1, 2, 0, 0], [3, 2, 1, 1])}
    valeurs = {nom: [ndcg_at_k(l, j, 5) for l, j in idx.values()] for nom, idx in (("ancien", ancien_index), ("nouveau", nouvel_index))}
    moyennes = {nom: moyenne_definie(v) for nom, v in valeurs.items()}
    faux_zero = {nom: sum(x or 0.0 for x in v) / len(v) for nom, v in valeurs.items()}
    deploie = moyennes["nouveau"] >= 0.85 and moyennes["nouveau"] >= moyennes["ancien"] - 0.02

    def q3_avec_spec_au_rang(p: int) -> float:
        reste = [2, 1, 0, 0]
        return ndcg_at_k(reste[:p - 1] + [3] + reste[p - 1:], [3, 2, 1, 1], 5)

    rangs_ok = [p for p in range(1, 6) if (1.0 + q3_avec_spec_au_rang(p)) / 2 >= 0.85]
    print("Cas 4 — BTP : ancien " + str([None if v is None else round(v, 5) for v in valeurs["ancien"]])
          + f" moyenne {moyennes['ancien']:.5f} ; nouveau " + str([None if v is None else round(v, 5) for v in valeurs["nouveau"]])
          + f" moyenne {moyennes['nouveau']:.5f} ; déploiement {deploie}")
    print(f"  None compté 0 : {faux_zero['ancien']:.5f} et {faux_zero['nouveau']:.5f} ; spécification au rang p de Q3 :"
          f" " + ", ".join(f"{p} → {q3_avec_spec_au_rang(p):.5f}" for p in range(1, 5)) + f" ; rangs acceptés {rangs_ok}")
    return {"valeurs": valeurs, "moyennes": moyennes, "faux_zero": faux_zero, "deploie": deploie,
            "q3p": [q3_avec_spec_au_rang(p) for p in range(1, 6)], "rangs_ok": rangs_ok}


def main() -> None:
    # Le mécanisme : trois documents suivis à travers gain, remise, contribution
    film = [(rel, i, gain_exponentiel(rel), remise(i), gain_exponentiel(rel) * remise(i)) for rel, i in ((3, 1), (3, 3), (2, 2))]
    print("Mécanisme : " + " ; ".join(f"note {a} au rang {i} : {g} × {w:.5f} = {c:.5f}" for a, i, g, w, c in film))
    assert [(g, r(w, 5), r(c, 5)) for _, _, g, w, c in film] == [(7, 1.0, 7.0), (7, 0.5, 3.5), (3, 0.63093, 1.89279)]

    # Démonstration 1 : la remise décroît strictement
    rem = [r(remise(i), 5) for i in range(1, 6)]
    print(f"Démo 1 : remises des rangs 1 à 5 {rem} ; rang 10 {remise(10):.5f}")
    assert rem == [1.0, 0.63093, 0.5, 0.43068, 0.38685] and r(remise(10), 5) == 0.28906
    assert all(remise(i) > remise(i + 1) > 0 for i in range(1, 100))
    assert r(100 * (1 - remise(2)), 0) == 37 and r(100 * remise(10), 0) == 29

    # Démonstration 2 : échanger deux voisins mal ordonnés augmente le DCG de (g' − g)(w − w')
    gain_ech = dcg_at_k([3, 2, 0, 1], 4) - dcg_at_k([2, 3, 0, 1], 4)
    print(f"Démo 2 : (2, 3, 0, 1) → (3, 2, 0, 1) : + {gain_ech:.5f} = (7 − 3)(1 − 0.63093)")
    assert r(gain_ech, 5) == 1.47628 and abs(gain_ech - (7 - 3) * (remise(1) - remise(2))) < 1e-12
    for p in itertools.permutations([0, 2, 3, 1]):
        p = list(p)
        for i in range(len(p) - 1):
            if p[i] < p[i + 1]:
                assert dcg_at_k(p[:i] + [p[i + 1], p[i]] + p[i + 2:], 4) > dcg_at_k(p, 4)

    # Démonstration 3 : le classement idéal est le maximum ; NDCG dans [0, 1] ; IDCG nul : None
    juges7 = [3, 3, 2, 1, 1, 0, 0]
    meilleur = max(dcg_at_k(list(p), 5) for p in itertools.permutations(juges7, 5))
    idcg7 = dcg_at_k(sorted(juges7, reverse=True), 5)
    refus = 0
    try:
        ndcg_at_k([3, 3], [3], 2)
    except ValueError:
        refus = 1
    print(f"Démo 3 : max sur {len(list(itertools.permutations(juges7, 5)))} classements = {meilleur:.5f} = IDCG@5 ;"
          f" aucun pertinent → {ndcg_at_k([0, 0], [0, 0], 2)} ; note hors jugements → ValueError ({refus})")
    assert abs(meilleur - idcg7) < 1e-12 and r(idcg7, 5) == 13.73404 and refus == 1
    assert ndcg_at_k([0, 0], [0, 0], 2) is None and r(dcg_at_k([3, 3], 2) / dcg_at_k([3], 2), 5) == 1.63093

    # Démonstration 4 : pourquoi 2^rel − 1 ; le choix du gain peut inverser deux moteurs
    gains = [gain_exponentiel(x) for x in range(4)]
    j4 = [2, 1, 1, 1]
    e = (ndcg_at_k([2, 0, 0], j4, 3), ndcg_at_k([1, 1, 1], j4, 3))
    l = (ndcg_at_k([2, 0, 0], j4, 3, gain_lineaire), ndcg_at_k([1, 1, 1], j4, 3, gain_lineaire))
    print(f"Démo 4 : gains {gains} ; [2, 0, 0] contre [1, 1, 1] : exponentiel {e[0]:.4f} > {e[1]:.4f}, linéaire {l[0]:.4f} < {l[1]:.4f}")
    assert gains == [0, 1, 3, 7] and 7 > 3 + 3 and [r(v, 4) for v in e + l] == [0.7262, 0.5158, 0.6388, 0.6806]
    assert r(dcg_at_k([2, 1, 1], 3), 4) == 4.1309 and r(dcg_at_k([2, 1, 1], 3, gain_lineaire), 4) == 3.1309

    # Démonstration 5 : invariances (échelle des gains, base du log) et non-monotonie en k
    triple = lambda x: 3 * gain_exponentiel(x)
    suite = [ndcg_at_k([3, 0, 3], [3, 3], k) for k in (1, 2, 3)]
    base10 = sum(gain_exponentiel(x) / math.log10(i + 1) for i, x in enumerate([2, 3, 0, 1], start=1)) / \
        sum(gain_exponentiel(x) / math.log10(i + 1) for i, x in enumerate([3, 2, 1, 0], start=1))
    print(f"Démo 5 : NDCG@1, @2, @3 de [3, 0, 3] face à [3, 3] = {[round(v, 4) for v in suite]} ; base 10 {base10:.5f}")
    assert [r(v, 4) for v in suite] == [1.0, 0.6131, 0.9197] and r(base10, 5) == 0.83545
    assert math.isclose(ndcg_at_k([2, 3, 0, 1], [3, 2, 1, 0], 4, triple), ndcg_at_k([2, 3, 0, 1], [3, 2, 1, 0], 4))
    assert r(dcg_at_k([3, 3], 3), 5) == 11.41651 and r(7 + 7 * remise(3), 1) == 10.5

    # Démonstration 6 : l'idéal tiré de la liste retrouvée surestime toujours le NDCG
    a1, n1 = ancien_ndcg([1, 0, 0], 3), ndcg_at_k([1, 0, 0], [1, 1, 1], 3)
    print(f"Démo 6 : [1, 0, 0] avec 3 pertinents : ancien {a1:.4f} ; corrigé {n1:.4f} (IDCG@3 = {dcg_at_k([1, 1, 1], 3):.4f})")
    assert a1 == 1.0 and r(n1, 4) == 0.4693 and r(dcg_at_k([1, 1, 1], 3), 4) == 2.1309
    for p in itertools.permutations(juges7, 4):
        assert ancien_ndcg(list(p), 4) >= ndcg_at_k(list(p), juges7, 4) - 1e-12 if dcg_at_k(list(p), 4) > 0 else True

    # Exemple simple
    idcg4, dcg4 = dcg_at_k([3, 2, 1, 0], 4), dcg_at_k([2, 3, 0, 1], 4)
    print(f"Exemple simple : IDCG@4 {idcg4:.5f} ; DCG@4 {dcg4:.5f} ; NDCG@4 {ndcg_at_k([2, 3, 0, 1], [3, 2, 1, 0], 4):.5f}")
    assert r(idcg4, 5) == 9.39279 and r(dcg4, 5) == 7.84718 and r(dcg4 / idcg4, 5) == 0.83545
    assert [r(3 * remise(2), 5), r(7 * remise(2), 5), r(remise(4), 5)] == [1.89279, 4.41651, 0.43068]

    # Cas 1 — BANQUE
    c1 = cas_1_retrievers_banque()
    assert r(c1["idcg"], 5) == 13.34718 and r(c1["dcg_x"], 5) == 8.93068 and r(c1["dcg_y"], 5) == 6.91651
    assert (r(c1["x5"], 5), r(c1["y5"], 5)) == (0.66911, 0.5182) and (r(c1["x2"], 5), r(c1["y2"], 5)) == (0.61315, 0.47445)
    assert c1["p5"] == (0.6, 0.6) and [r(v, 5) for v in c1["bin"]] == [0.7537, 0.83187]
    assert [r(v, 5) for v in c1["y_g"]] == [5.91651, 6.91651, 8.91651, 12.91651] and r(c1["dcg_x"] - c1["y_g"][2], 5) == 0.01417
    assert r(dcg_at_k([3, 3], 2), 5) == 11.41651 and r(dcg_at_k([1, 1, 1, 1], 4), 5) == 2.56161

    # Cas 2 — IMMO
    c2 = cas_2_comparables_immo()
    assert r(c2["dcg"], 5) == 7.41651 and r(c2["idcg"], 5) == 12.91651 and r(c2["n3"], 5) == 0.57419
    assert r(c2["ancien"], 5) == 0.83399 and c2["ancien"] >= 0.8 > c2["n3"] and c2["apres"] == 1.0
    assert r(c2["brute"], 0) == 2404167 and c2["reclassee"] == 2112500 and r(c2["brute"] - c2["reclassee"], 0) == 291667
    assert r(100 * (c2["brute"] - c2["reclassee"]) / c2["reclassee"], 1) == 13.8 and 0.04 * 2112500 == 84500
    assert [r(v, 5) for v in c2["troisieme"]] == [0.57419, 0.6129, 0.69032, 0.84516] and c2["troisieme"][2] < 0.8 <= c2["troisieme"][3]
    assert r(dcg_at_k([3, 2, 0], 3), 5) == 8.89279 and r((1650 + 1720 + 2400) / 3, 1) == 1923.3

    # Cas 3 — RH
    c3 = cas_3_paie_rh()
    assert [r(v, 5) for v in c3["res"][3][:3]] == [0.26616, 0.42, 0.70392] and c3["res"][3][3] == 1.0
    assert [r(v, 5) for v in c3["res"][5][:3]] == [0.56138, 0.63399, 0.7537] and c3["res"][5][3] == 1.0
    assert r(c3["dcg3"], 5) == 2.5 and r(c3["idcg3"], 5) == 9.39279

    # Cas 4 — BTP
    c4 = cas_4_deploiement_btp()
    assert [None if v is None else r(v, 5) for v in c4["valeurs"]["ancien"]] == [0.99262, None, 0.80588]
    assert [None if v is None else r(v, 5) for v in c4["valeurs"]["nouveau"]] == [1.0, None, 0.9295]
    assert (r(c4["moyennes"]["ancien"], 5), r(c4["moyennes"]["nouveau"], 5)) == (0.89925, 0.96475) and c4["deploie"]
    assert (r(c4["faux_zero"]["ancien"], 5), r(c4["faux_zero"]["nouveau"], 5)) == (0.5995, 0.64317)
    assert c4["faux_zero"]["nouveau"] < 0.85 and [r(v, 5) for v in c4["q3p"][:3]] == [0.95616, 0.80588, 0.72591]
    assert c4["rangs_ok"] == [1, 2, 3] and r(0.85 * 2 - 1, 2) == 0.7
    assert r(c4["q3p"][3], 5) == 0.67651 and r(dcg_at_k([3, 2, 0, 1, 0], 5), 5) == 9.32347
    assert r(dcg_at_k([1, 0, 1, 1, 0], 5), 5) == 1.93068 and r(dcg_at_k([1, 1, 1, 0, 0], 5), 5) == 2.13093

    print("Corrigé")
    ex6 = ndcg_at_k([2, 3, 3], [3, 3, 2, 2, 1, 1, 0, 0], 3)
    faux = dcg_at_k([0, 0, 1], 3) / dcg_at_k([1, 0, 0], 3)
    print(f"  ex1 {rem[:4]} ; ex2 {dcg_at_k([3, 3], 2):.5f}, {dcg_at_k([0, 3], 2):.5f}, {dcg_at_k([3, 0], 2)} ;"
          f" ex5 {ndcg_at_k([1, 2], [2, 1], 2):.5f} ; ex6 {ex6:.5f} ; ex7 {faux:.1f} au lieu de {ndcg_at_k([0, 0, 1], [1, 1, 1], 3):.5f}")
    assert r(dcg_at_k([0, 3], 2), 5) == 4.41651 and dcg_at_k([3, 0], 2) == 7.0
    assert r(ndcg_at_k([1, 2], [2, 1], 2), 5) == 0.79671 and r(dcg_at_k([1, 2], 2), 5) == 2.89279 and r(dcg_at_k([2, 1], 2), 5) == 3.63093
    assert r(ex6, 5) == 0.84516 and faux == 0.5 and r(ndcg_at_k([0, 0, 1], [1, 1, 1], 3), 5) == 0.23464
    assert r(dcg_at_k([2, 3, 3], 3), 5) == 10.91651 and (1650 + 1720 + 1700) / 3 * 1250 == 2112500
    assert all(2 ** (n + 1) - 1 == 2 * (2 ** n - 1) + 1 for n in range(10))
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Mécanisme : note 3 au rang 1 : 7 × 1.00000 = 7.00000 ; note 3 au rang 3 : 7 × 0.50000 = 3.50000 ; note 2 au rang 2 : 3 × 0.63093 = 1.89279
Démo 1 : remises des rangs 1 à 5 [1.0, 0.63093, 0.5, 0.43068, 0.38685] ; rang 10 0.28906
Démo 2 : (2, 3, 0, 1) → (3, 2, 0, 1) : + 1.47628 = (7 − 3)(1 − 0.63093)
Démo 3 : max sur 2520 classements = 13.73404 = IDCG@5 ; aucun pertinent → None ; note hors jugements → ValueError (1)
Démo 4 : gains [0, 1, 3, 7] ; [2, 0, 0] contre [1, 1, 1] : exponentiel 0.7262 > 0.5158, linéaire 0.6388 < 0.6806
Démo 5 : NDCG@1, @2, @3 de [3, 0, 3] face à [3, 3] = [1.0, 0.6131, 0.9197] ; base 10 0.83545
Démo 6 : [1, 0, 0] avec 3 pertinents : ancien 1.0000 ; corrigé 0.4693 (IDCG@3 = 2.1309)
Exemple simple : IDCG@4 9.39279 ; DCG@4 7.84718 ; NDCG@4 0.83545
Cas 1 — BANQUE : IDCG@5 13.34718 ; X 8.93068 → 0.66911 ; Y 6.91651 → 0.51820 ; NDCG@2 X 0.61315, Y 0.47445
  P@5 0.6 = 0.6 ; NDCG binaire X 0.75370 < Y 0.83187 ; Y avec un premier noté 2 : 8.91651 < 8.93068, noté 3 : 12.91651
Cas 2 — IMMO : DCG@3 7.41651 / IDCG@3 12.91651 = 0.57419 ; ancien calcul 0.83399 ; estimations 2404167 contre 2112500 AED
  troisième comparable noté 0, 1, 2, 3 → 0.57419, 0.61290, 0.69032, 0.84516
Cas 3 — RH : @3 exponentiel 0.26616, linéaire 0.42000, binaire 0.70392, après filtre 1.0 ; @5 exponentiel 0.56138, linéaire 0.63399, binaire 0.75370, après filtre 1.0
Cas 4 — BTP : ancien [0.99262, None, 0.80588] moyenne 0.89925 ; nouveau [1.0, None, 0.9295] moyenne 0.96475 ; déploiement True
  None compté 0 : 0.59950 et 0.64317 ; spécification au rang p de Q3 : 1 → 0.95616, 2 → 0.80588, 3 → 0.72591, 4 → 0.67651 ; rangs acceptés [1, 2, 3]
Corrigé
  ex1 [1.0, 0.63093, 0.5, 0.43068] ; ex2 11.41651, 4.41651, 7.0 ; ex5 0.79671 ; ex6 0.84516 ; ex7 0.5 au lieu de 0.23464
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme note un classement à pertinence graduée en le comparant au classement idéal de tous les documents jugés. Les cas ajoutent une moyenne sur un jeu de questions qui exclut les questions sans pertinent (cas 4) et une règle de décision par seuil (cas 2).

```text
ALGORITHME NDCG
ENTRÉES : notes du classement rel₁ … relₙ, notes de tous les documents jugés, k, gain (exponentiel par défaut)
SORTIE  : NDCG@k dans [0 ; 1], ou « indéfini »

  FONCTION DCG(liste, k)
      SI k < 1 OU une note < 0 ALORS ERREUR
      total ← 0
      POUR i DE 1 À min(k, longueur(liste)) FAIRE
          total ← total + gain(relᵢ) / log₂(i + 1)
      FIN POUR
      RETOURNER total
  SI une note retrouvée positive n'existe pas dans les jugements ALORS ERREUR
  IDCG ← DCG(notes de tous les jugés triées par ordre décroissant, k)
  SI IDCG = 0 ALORS RETOURNER « indéfini »
  RETOURNER DCG(notes retrouvées, k) / IDCG

ALGORITHME MoyenneDéfinie (jeu de questions)
  RETOURNER la moyenne des NDCG définis, ou « indéfini » s'il n'y en a aucun
```

**Complexité.** O(k) pour chaque DCG, O(J log J) pour trier les J notes jugées (ou O(J) par comptage, les notes étant de petits entiers), O(n + J) pour la garde par compteurs. La vérification par toutes les permutations de `main` coûte O(n!) et n'est faite que sur 4 éléments, ou sur les 2 520 rangements de 5 documents parmi 7.

**Du squelette au code.** La remise est `remise(i)`, les gains `gain_exponentiel(rel)` et `gain_lineaire(rel)`, la fonction DCG est `dcg_at_k(rels, k, gain)` et l'algorithme complet `ndcg_at_k(rels_retrouves, rels_tous_juges, k, gain)`, qui construit l'idéal avec `sorted(rels_tous_juges, reverse=True)` et renvoie `None` quand l'IDCG est nul. La moyenne est `moyenne_definie(valeurs)`, et `ancien_ndcg(rels, k)` reproduit l'erreur corrigée de la démonstration 6. Les quatre cas sont `cas_1_retrievers_banque`, `cas_2_comparables_immo`, `cas_3_paie_rh` et `cas_4_deploiement_btp`.
