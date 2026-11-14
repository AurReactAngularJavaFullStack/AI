# 25 — Reciprocal Rank Fusion : démonstrations

> Fiche : [25 — Reciprocal Rank Fusion](<../../Images/04-Recherche/25_rrf.md>) · Image : `25_rrf.jpg` · Leçon : [Étape 24 — Reciprocal Rank Fusion](<../../05-RAG/24-RAG-Formule-RRF.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
\operatorname{RRF}(d) = \sum_{j \,:\, d \in R_j} \frac{1}{k + \operatorname{rang}_j(d)}
$$

Plusieurs moteurs (sémantique, BM25, mémoire…) classent des documents. Chaque moteur j donne au document d une contribution qui ne dépend que de son rang. k (souvent 60) amortit les écarts entre rangs.

Notation de la leçon 24 : la constante k du bloc ci-dessus y est notée k_RRF, pour ne pas la confondre avec le k du top-k (Recall@k, NDCG@k) ni avec le k₁ de BM25 (fichier 11). La suite de ce fichier écrit donc k_RRF dans le texte ; sa valeur par défaut est 60, celle de Cormack, Clarke et Büttcher (2009).

## Les symboles, un par un

$$
R_j
$$

Le classement du moteur j, une liste ordonnée de documents sans doublon, du meilleur au moins bon ; un élément de la liste `classements`.

$$
d
$$

Un document candidat, repéré par son identifiant ; variable `doc`.

$$
\operatorname{rang}_j(d)
$$

La position de d dans Rⱼ, entier ≥ 1 (1 pour le premier) ; variable `rang`, donnée par `enumerate(..., start=1)`.

$$
k_{RRF}
$$

La constante d'amortissement, réel ≥ 0, 60 par défaut ; argument `k_rrf` de `rrf`. Une valeur négative lève `ValueError`.

$$
\lvert R \rvert
$$

Le nombre de classements fusionnés, entier ≥ 1 ; `len(classements)`.

$$
m(d)
$$

Le nombre de classements qui contiennent d, entier de 1 à |R| ; il n'a pas de variable propre, il se lit dans la boucle de `rrf`.

$$
\operatorname{RRF}(d)
$$

Le score fusionné, réel dans ]0 ; |R|/(k_RRF + 1)], qui ne sert qu'à trier ; valeur associée à `doc` dans la liste triée renvoyée par `rrf(classements, k_rrf)`.

$$
w_j
$$

Le poids facultatif du classement j (RRF pondérée), réel > 0, 1 par défaut ; argument `poids` de `rrf`.

## Le mécanisme, avant les preuves

RRF ne reçoit aucun score, seulement des positions : pour chaque moteur, la liste de ses documents dans l'ordre. Chaque position r est transformée en une contribution 1/(k_RRF + r), une fonction qui décroît avec le rang, de plus en plus lentement, et ne devient jamais négative. Pour chaque document, on additionne les contributions de tous les classements qui le contiennent ; un document absent d'une liste n'y reçoit rien, ce qui n'est pas une pénalité mais l'absence d'un vote. Le résultat ne sert qu'à trier : les scores sont petits (au plus |R|/(k_RRF + 1)), très proches les uns des autres, et ne se comparent pas d'une requête à l'autre. Pourquoi l'inverse du rang plutôt que le rang lui-même ? Parce qu'une somme de rangs obligerait à donner un rang aux documents absents, et qu'un rang n'a pas de borne ; l'inverse, lui, tend vers 0 pour les rangs lointains, si bien qu'un document classé 500ᵉ ne pèse presque rien, sans qu'on ait besoin de connaître la longueur des listes. Pourquoi ajouter k_RRF ? Sans lui, le premier rang vaut 1 et le deuxième 0,5 : le premier de chaque moteur écrase tout le reste. Avec k_RRF = 60, les rangs 1 et 2 valent 1/61 et 1/62, presque autant : ce qui départage les documents, c'est surtout le nombre de moteurs qui les citent. Pourquoi une somme ? Parce que chaque moteur est un vote indépendant ; deux votes moyens valent plus qu'un vote enthousiaste (démonstration 4), et c'est ce que l'on veut quand les moteurs se trompent de façons différentes. Enfin, comme seuls les rangs entrent, l'échelle des scores d'origine n'a aucun effet : un cosinus entre 0 et 1, un BM25 entre 0 et 30 et un montant en AED se fusionnent sans normalisation (démonstration 2). L'analogie Java est un `Comparator` : RRF ne lit que l'ordre produit par chaque moteur, jamais ses valeurs internes.

Petit film chiffré : un document classé 1ᵉʳ par un moteur et 3ᵉ par un autre.

| Opération | k_RRF = 60 | k_RRF = 0 |
|---|---|---|
| contribution du rang 1 | 1/61 ≈ 0,016393 | 1/1 = 1 |
| contribution du rang 3 | 1/63 ≈ 0,015873 | 1/3 ≈ 0,333333 |
| score fusionné | 0,032266 | 1,333333 |

Avec k_RRF = 60, les deux rangs pèsent presque pareil (0,016393 contre 0,015873) ; avec k_RRF = 0, le rang 1 pèse trois fois plus que le rang 3. Un document cité par trois moteurs aux rangs 1, 2 et 3 obtiendrait 1/61 + 1/62 + 1/63 ≈ 0,048395.

## Démonstration 1 — Bornes d'une contribution et du score

**Ce qu'on démontre.** Chaque contribution est dans ]0 ; 1/(k_RRF + 1)], et un document présent dans m(d) classements vérifie :

$$
0 < \operatorname{RRF}(d) \le \frac{m(d)}{k_{RRF} + 1} \le \frac{\lvert R \rvert}{k_{RRF} + 1}
$$

L'égalité n'a lieu que pour un document premier dans chacune des |R| listes. Hypothèse : chaque liste est dédoublonnée.

**L'idée.** Le meilleur rang possible est 1, donc la meilleure contribution possible est 1/(k_RRF + 1) ; un document ne peut recevoir qu'une contribution par liste, donc au plus |R| contributions.

**La preuve, pas à pas.**

**Étape 1.** Le rang vaut au moins 1, donc k_RRF + rang ≥ k_RRF + 1 > 0 ; la fonction inverse étant décroissante sur ]0 ; +∞[ :

$$
0 < \frac{1}{k_{RRF} + \operatorname{rang}_j(d)} \le \frac{1}{k_{RRF} + 1}
$$

**Étape 2.** Un document n'a qu'un rang par liste, parce que chaque liste est dédoublonnée ; RRF(d) est donc la somme de m(d) contributions, chacune au plus 1/(k_RRF + 1), d'où RRF(d) ≤ m(d)/(k_RRF + 1).

**Étape 3.** m(d) ≤ |R|, parce qu'on ne peut pas être dans plus de listes qu'il n'y en a ; l'égalité de l'étape 2 exige que chaque contribution vaille 1/(k_RRF + 1), donc que d soit premier partout. ∎

**Vérification chiffrée.** Avec deux listes et k_RRF = 60, la borne vaut 2/61 ≈ 0,032787, et un document premier dans les deux listes l'atteint exactement ; avec trois listes, 3/61 ≈ 0,049180. Contre-exemple quand l'hypothèse de dédoublonnage manque : dans la liste brute (A, A, B), la boucle donnerait à A les rangs 1 et 2, donc 1/61 + 1/62, au-delà de la borne d'une liste ; après dédoublonnage, A reçoit 1/61 seulement, ce que le programme vérifie.

**Ce que la preuve révèle du mécanisme.** Le score d'un document est d'abord fixé par m(d), le nombre de listes qui le citent, puis affiné par ses rangs. Les scores sont minuscules et serrés : une liste ne peut jamais donner plus de 1/61 ≈ 0,0164 avec la valeur par défaut.

**Conséquence pour un agent.** On ne pose jamais de seuil sur un score RRF (« garder les documents au-dessus de 0,03 ») : sa valeur dépend du nombre de listes et de k_RRF, pas de la pertinence. On garde un nombre fixe de documents, le top-k, et l'on dédoublonne chaque liste avant de fusionner.

## Démonstration 2 — Les échelles de scores ne comptent plus

**Ce qu'on démontre.** Si un moteur transforme ses scores par une fonction φ strictement croissante, ses rangs ne changent pas, donc la fusion RRF non plus :

$$
s_a > s_b \iff \varphi(s_a) > \varphi(s_b) \quad\Longrightarrow\quad \operatorname{rang}_j \text{ inchangés} \quad\Longrightarrow\quad \operatorname{RRF} \text{ inchangé}
$$

Hypothèse : φ strictement croissante, et départage des égalités par une règle fixe (le nom du document).

**L'idée.** RRF ne lit que l'ordre des documents dans chaque liste ; toute transformation qui conserve l'ordre est invisible pour lui, qu'elle soit affine (100 × BM25 + 7) ou qu'elle déforme les écarts (cos³, e¹⁰ᶜᵒˢ, ln(1 + BM25)).

**La preuve, pas à pas.**

**Étape 1.** φ strictement croissante signifie : sₐ > s_b entraîne φ(sₐ) > φ(s_b), et sₐ = s_b entraîne φ(sₐ) = φ(s_b) ; la réciproque vaut aussi, parce qu'une fonction strictement croissante est injective.

**Étape 2.** Le rang d'un document est 1 plus le nombre de documents de score strictement plus grand, plus ceux de même score placés avant lui par le départage ; par l'étape 1, ces deux nombres sont les mêmes avant et après φ.

**Étape 3.** Les rangs étant identiques, chaque contribution 1/(k_RRF + rang) est identique, donc la somme aussi. ∎

**Vérification chiffrée.** Avec les scores sémantiques (A 0,82 ; B 0,80 ; C 0,78 ; D 0,75) et BM25 (C 8 ; A 6 ; E 5 ; B 2), la fusion donne A 0,032522 ; C 0,032266 ; B 0,031754 ; E 0,015873 ; D 0,015625. Après e¹⁰ᶜᵒˢ sur le premier moteur et ln(1 + BM25) sur le second, le programme retrouve exactement la même liste. Contre-exemple quand la croissance n'est pas stricte : plafonner BM25 à 2 (min(BM25, 2)) est croissant mais crée des égalités ; elles sont départagées par le nom, la liste lexicale devient A, B, C, E, et la fusion devient A, B, C, D, E : B passe devant C.

**Ce que la preuve révèle du mécanisme.** RRF est insensible à la calibration des moteurs, mais il perd aussi l'information des écarts : un document très largement en tête d'une liste reçoit la même contribution qu'un document à peine devant le suivant (fichier 11, cas 3).

**Conséquence pour un agent.** RRF est le bon choix par défaut quand les signaux n'ont aucune unité commune (un cosinus, un BM25, un écart en AED/sqft) ou quand on n'a pas encore de requêtes étiquetées pour régler un score hybride. Quand un écart porte une information forte, comme un nom de produit très rare, on l'exploite par une règle explicite avant la fusion.

## Démonstration 3 — Le rôle de k_RRF

**Ce qu'on démontre.** L'écart de contribution entre les rangs r et r + 1, et le rapport entre le rang 1 et le rang 10, valent :

$$
\frac{1}{k_{RRF} + r} - \frac{1}{k_{RRF} + r + 1} = \frac{1}{(k_{RRF} + r)(k_{RRF} + r + 1)}, \qquad \frac{1/(k_{RRF} + 1)}{1/(k_{RRF} + 10)} = \frac{k_{RRF} + 10}{k_{RRF} + 1}
$$

Les deux diminuent quand k_RRF augmente : un grand k_RRF aplatit les contributions.

**L'idée.** Ajouter une constante au dénominateur rapproche les dénominateurs des différents rangs les uns des autres, en proportion : 61 et 70 sont relativement plus proches que 1 et 10.

**La preuve, pas à pas.**

**Étape 1.** On réduit au même dénominateur, parce que (k + r + 1) − (k + r) = 1 :

$$
\frac{1}{k + r} - \frac{1}{k + r + 1} = \frac{(k + r + 1) - (k + r)}{(k + r)(k + r + 1)} = \frac{1}{(k + r)(k + r + 1)}
$$

**Étape 2.** Le dénominateur croît avec k, donc l'écart décroît avec k.

**Étape 3.** Le rapport (k + 10)/(k + 1) = 1 + 9/(k + 1) décroît avec k et tend vers 1. ∎

**Vérification chiffrée.** Avec k_RRF = 0, passer du rang 1 au rang 2 fait perdre 1 − 1/2 = 0,5 ; avec k_RRF = 60, la perte n'est que 1/(61 × 62) ≈ 0,00026. Le rapport rang 1/rang 10 vaut 10 pour k_RRF = 0 et 70/61 ≈ 1,148 pour k_RRF = 60. Basculement : un document X premier dans une seule liste et un document Y cinquième et sixième dans deux listes. Y passe devant X si 1/(k + 5) + 1/(k + 6) > 1/(k + 1), ce qui équivaut, après réduction au même dénominateur, à k² + 2k − 19 > 0 ; la racine positive vaut −1 + √20 ≈ 3,47, donc X gagne pour k_RRF ≤ 3 et Y dès k_RRF = 4.

**Ce que la preuve révèle du mécanisme.** k_RRF règle l'arbitrage entre « être premier quelque part » (petit k_RRF) et « être cité partout » (grand k_RRF). Il ne change rien quand un seul moteur est fusionné : l'ordre d'une liste seule reste son ordre.

**Conséquence pour un agent.** On garde k_RRF = 60 par défaut, et l'on ne le baisse que si une exigence métier précise le demande, après mesure sur des requêtes étiquetées (cas 3) ; c'est un réglage, pas une loi.

## Démonstration 4 — Le consensus bat la première place isolée

**Ce qu'on démontre.** Avec deux classements, tout document classé dans les k_RRF + 1 premiers de chacun bat tout document présent dans un seul classement ; et deux contributions de même rang r battent une première place isolée si et seulement si r < k_RRF + 2 :

$$
r_1, r_2 \le k_{RRF} + 1 \;\Longrightarrow\; \frac{1}{k_{RRF} + r_1} + \frac{1}{k_{RRF} + r_2} \ge \frac{2}{2k_{RRF} + 1} > \frac{1}{k_{RRF} + 1}
$$

**L'idée.** Chaque contribution d'un document bien placé dans les deux listes vaut au moins la moitié de la meilleure contribution possible ; deux moitiés bien comptées dépassent un entier.

**La preuve, pas à pas.**

**Étape 1.** Si r ≤ k + 1, alors k + r ≤ 2k + 1, donc 1/(k + r) ≥ 1/(2k + 1), parce que la fonction inverse est décroissante ; en additionnant pour r₁ et r₂, la somme vaut au moins 2/(2k + 1).

**Étape 2.** 2/(2k + 1) > 1/(k + 1) équivaut, en multipliant par (2k + 1)(k + 1) > 0, à 2(k + 1) > 2k + 1, soit 2 > 1, toujours vrai.

**Étape 3.** Le membre de droite est, par la démonstration 1, le maximum de ce qu'obtient un document présent dans une seule liste. Pour des rangs égaux r, 2/(k + r) > 1/(k + 1) équivaut à 2(k + 1) > k + r, soit r < k + 2. ∎

**Vérification chiffrée.** Avec k_RRF = 60 : un document premier chez un seul moteur obtient 1/61 ≈ 0,016393 ; deuxième chez deux moteurs, 2/62 ≈ 0,032258 ; troisième chez deux moteurs, 2/63 ≈ 0,031746, encore près du double. Au rang 61 dans les deux listes, 2/121 ≈ 0,016529 > 0,016393 ; au rang 62, 2/122 = 1/61 exactement : égalité. Le programme vérifie l'inégalité pour tous les couples de rangs de 1 à 61. Contre-exemple quand l'hypothèse r ≤ k_RRF + 1 manque : avec k_RRF = 0, un document deuxième chez deux moteurs obtient 2/2 = 1, autant qu'une première place isolée (1/1).

**Ce que la preuve révèle du mécanisme.** Comme les listes d'un retriever dépassent rarement 60 documents, un document trouvé par deux moteurs passe en pratique toujours devant un document trouvé par un seul : RRF est d'abord un compteur de votes, puis un départage par les rangs.

**Conséquence pour un agent.** Le consensus n'a de valeur que si les moteurs sont indépendants : deux moteurs qui reposent sur les mêmes signaux fabriquent un faux consensus. On mesure donc la corrélation de leurs classements (corrélation de Spearman, cas 4) avant de leur faire confiance, et l'on ne fusionne pas deux variantes du même moteur comme deux votes.

## Démonstration 5 — Convexité : à somme de rangs égale, un très bon rang l'emporte de peu

**Ce qu'on démontre.** La fonction f(r) = 1/(k + r) est convexe ; à somme de rangs égale, deux rangs inégaux rapportent plus que deux rangs égaux, et l'écart exact est :

$$
\frac{1}{k + 1} + \frac{1}{k + 3} - \frac{2}{k + 2} = \frac{2}{(k + 1)(k + 2)(k + 3)} > 0
$$

**L'idée.** La contribution baisse vite au début puis de plus en plus lentement : ce que l'on gagne en passant du rang 2 au rang 1 dépasse ce que l'on perd en passant du rang 2 au rang 3.

**La preuve, pas à pas.**

**Étape 1.** La dérivée seconde de f vaut 2/(k + r)³ > 0, donc f est convexe, et une fonction convexe vérifie f(a) + f(b) > 2f((a + b)/2) dès que a ≠ b.

**Étape 2.** Pour a = 1 et b = 3, on réduit au même dénominateur P = (k + 1)(k + 2)(k + 3) :

$$
\frac{(k + 2)(k + 3) + (k + 1)(k + 2) - 2(k + 1)(k + 3)}{P} = \frac{(k^2 + 5k + 6) + (k^2 + 3k + 2) - 2(k^2 + 4k + 3)}{P} = \frac{2}{P}
$$

∎

**Vérification chiffrée.** Avec k_RRF = 60, les rangs 1 et 3 donnent 1/61 + 1/63 ≈ 0,032266, les rangs 2 et 2 donnent 2/62 ≈ 0,032258, et l'écart vaut 2/(61 × 62 × 63) ≈ 8,39 × 10⁻⁶. Le programme vérifie la formule de l'écart pour k de 0 à 99. Contre-exemple quand l'hypothèse a ≠ b manque : pour des rangs égaux, il n'y a pas d'écart, f(2) + f(2) = 2f(2).

**Ce que la preuve révèle du mécanisme.** À k_RRF = 60, l'effet est minuscule : il ne départage que des documents presque à égalité. Il explique pourtant des ordres qui surprennent, comme dans l'exemple de la leçon 24 où C (rangs 3 et 1) passe devant B (rangs 2 et 4) : leurs sommes de rangs valent 4 et 6, et la convexité accentue l'avantage de C.

**Conséquence pour un agent.** Deux documents dont les scores RRF diffèrent de quelques millionièmes doivent être traités comme à égalité : l'agent les présente tous les deux, ou les départage par une règle explicite et stable (le nom, la date), jamais au hasard.

## Démonstration 6 — Un grand k_RRF classe par nombre de listes, puis par somme des rangs

**Ce qu'on démontre.** Quand k_RRF → +∞, k_RRF × RRF(d) tend vers m(d), et pour deux documents présents dans le même nombre de listes, k_RRF² × (RRF(a) − RRF(b)) tend vers la différence de leurs sommes de rangs :

$$
k_{RRF}^2 \left(\operatorname{RRF}(a) - \operatorname{RRF}(b)\right) \xrightarrow[k_{RRF} \to +\infty]{} \sum_j \operatorname{rang}_j(b) - \sum_j \operatorname{rang}_j(a)
$$

**L'idée.** Pour k grand, chaque contribution vaut presque 1/k, moins une petite correction proportionnelle au rang : au premier ordre, on compte les listes ; au second ordre, on additionne les rangs.

**La preuve, pas à pas.**

**Étape 1.** k × 1/(k + r) = 1/(1 + r/k) tend vers 1, donc k × RRF(d), somme de m(d) tels termes, tend vers m(d).

**Étape 2.** Pour une liste, la différence de deux contributions vaut, en réduisant au même dénominateur :

$$
\frac{1}{k + r_a} - \frac{1}{k + r_b} = \frac{r_b - r_a}{(k + r_a)(k + r_b)}
$$

**Étape 3.** Multipliée par k², elle tend vers r_b − r_a, parce que k²/((k + r_a)(k + r_b)) tend vers 1 ; en sommant sur les listes communes, on obtient la différence des sommes de rangs. ∎

**Vérification chiffrée.** Un document a aux rangs 1 et 4 (somme 5) contre un document b aux rangs 2 et 2 (somme 4). Pour k_RRF = 0, a obtient 1 + 0,25 = 1,25 > 1 ; pour k_RRF = 60, a obtient 1/61 + 1/64 ≈ 0,032018 < 2/62 ≈ 0,032258. L'égalité a lieu exactement en k_RRF = 2, puisque 1/3 + 1/6 = 1/2 = 2/4 ; et pour k_RRF = 10⁶, k² × (RRF(b) − RRF(a)) ≈ 1,0000 = 5 − 4. Contre-exemple quand m(a) ≠ m(b) : la différence est alors d'ordre 1/k, pas 1/k², et c'est le nombre de listes qui décide, pas la somme des rangs.

**Ce que la preuve révèle du mécanisme.** RRF interpole entre deux règles simples : « le meilleur rang l'emporte » pour k_RRF petit, et « le plus de listes, puis la plus petite somme de rangs » (un vote de Borda) pour k_RRF grand. La valeur 60 est déjà proche du second régime.

**Conséquence pour un agent.** Pour expliquer un classement fusionné à un utilisateur ou à un auditeur, il suffit en général de donner, pour chaque document, le nombre de listes qui le citent et ses rangs : avec k_RRF = 60, ces deux informations expliquent presque toujours l'ordre.

## Exemple simple, à la main

Moteur A : α, β, γ, δ, ε. Moteur B : β, α, δ, ζ, γ. k_RRF = 60. Les contributions de base valent 1/61 ≈ 0,016393 ; 1/62 ≈ 0,016129 ; 1/63 ≈ 0,015873 ; 1/64 = 0,015625 ; 1/65 ≈ 0,015385.

$$
\operatorname{RRF}(\alpha) = \frac{1}{61} + \frac{1}{62} \approx 0{,}016393 + 0{,}016129 = 0{,}032522
$$

| Document | Rang chez A | Rang chez B | Calcul | RRF |
|---|---|---|---|---|
| α | 1 | 2 | 0,016393 + 0,016129 | 0,032522 |
| β | 2 | 1 | 0,016129 + 0,016393 | 0,032522 |
| δ | 4 | 3 | 0,015625 + 0,015873 | 0,031498 |
| γ | 3 | 5 | 0,015873 + 0,015385 | 0,031258 |
| ζ | absent | 4 | 0,015625 | 0,015625 |
| ε | 5 | absent | 0,015385 | 0,015385 |

Classement fusionné : α et β ex æquo, puis δ, γ, ζ, ε. δ passe devant γ, alors que γ est mieux classé par A, parce que sa somme de rangs est plus petite (7 contre 8) ; ζ passe devant ε parce que le rang 4 rapporte plus que le rang 5.

## Cas d'usage complexes, démontrés

### Cas 1 — [BANQUE] : trois moteurs pour l'assistant d'une banque de détail

**Contexte.** L'assistant clients d'une banque de détail de Dubaï répond à une question sur le remboursement anticipé d'un prêt personnel. Il interroge trois moteurs : une recherche sémantique, un index BM25 et la mémoire des conversations résolues. Il fusionne les trois listes par RRF et injecte les trois premiers passages dans son prompt. La banque traite 10 000 questions de ce type par mois ; ce volume et les scores ci-dessous sont illustratifs.

**Données.**

- Sémantique (cosinus) : C2 0,82 ; C5 0,80 ; C1 0,78 ; C4 0,75.
- BM25 : C1 14,2 ; C2 9,1 ; C3 8,0 ; C5 5,5.
- Mémoire (similarité de conversation) : C5 0,95 ; C1 0,60 ; C6 0,40.
- k_RRF = 60 ; l'agent garde 3 passages.

**Calcul pas à pas.**

**Étape 1, les rangs.** Sémantique : C2, C5, C1, C4. BM25 : C1, C2, C3, C5. Mémoire : C5, C1, C6.

**Étape 2, les documents cités trois fois :**

$$
\operatorname{RRF}(C_1) = \frac{1}{63} + \frac{1}{61} + \frac{1}{62} \approx 0{,}048395, \qquad \operatorname{RRF}(C_5) = \frac{1}{62} + \frac{1}{64} + \frac{1}{61} \approx 0{,}048147
$$

**Étape 3, les autres.** C2 = 1/61 + 1/62 ≈ 0,032522 ; C3 = 1/63 ≈ 0,015873 ; C6 = 1/63 ≈ 0,015873 ; C4 = 1/64 = 0,015625.

**Étape 4, le top-3.** C1, C5, C2.

**Décision de l'agent.** L'agent injecte C1, C5 et C2. C1 et C5 sont cités par les trois moteurs, alors qu'aucun des deux n'est premier partout : c'est le consensus de la démonstration 4. Le compromis : C3, trouvé seulement par BM25 (score 8,0, élevé), est écarté ; s'il contenait un terme exact décisif, comme un numéro de produit, il faudrait une règle lexicale explicite avant la fusion (fichier 11, cas 3).

**Contre-calcul.** Additionner les scores bruts mélange trois échelles : C1 = 0,78 + 14,2 + 0,60 = 15,58, C2 = 0,82 + 9,1 = 9,92, C3 = 8,0, C5 = 0,80 + 5,5 + 0,95 = 7,25. BM25, dont les valeurs sont dix fois plus grandes, décide seul : le top-3 devient C1, C2, C3, et C5, le seul passage sur lequel les trois moteurs s'accordent (par exemple le barème à jour des frais de remboursement anticipé), disparaît du contexte. Si 3 % des 10 000 questions mensuelles perdaient ainsi leur source à jour, 300 réponses par mois seraient fausses.

**Sensibilité.** C5 reste devant C2 quel que soit son rang dans BM25, tant qu'il figure dans les trois listes : 1/62 + 1/(60 + r) + 1/61 dépasse toujours 1/61 + 1/62. La valeur de bascule est sa présence dans la mémoire : si la mémoire ne le renvoie plus, il tombe à 1/62 + 1/64 ≈ 0,031754 et passe derrière C2 (0,032522). Avec k_RRF = 1, l'ordre de tête est le même (C1 1,0833 ; C5 1,0333 ; C2 0,8333), avec des écarts bien plus grands, donc plus sensibles au bruit d'un seul moteur.

**En production.** L'indicateur suivi est le Recall@5 sur des questions étiquetées, et la part des questions où les trois moteurs proposent trois premiers passages différents, signe d'une question ambiguë sur laquelle l'agent doit demander une précision ; alerte au-dessus de 20 % (illustratif). Les informations données au client sur un prêt personnel doivent rester cohérentes avec les règles de la CBUAE, par exemple une durée d'au plus 48 mois.

### Cas 2 — [IMMO] : fusionner trois classements qui n'ont pas la même unité

**Contexte.** Pour chaque demande d'acheteur, le moteur d'une agence de Dubaï et d'Abu Dhabi produit trois classements de cinq unités : par similarité sémantique des descriptions, par BM25 sur les noms de projets et les codes d'unité, et par écart entre le prix au sqft et le budget de l'acheteur. Un cosinus, un BM25 non borné et un écart en AED/sqft n'ont aucune unité commune : RRF n'a besoin que des trois ordres. L'agent présente trois unités, avec le prix total frais DLD compris. Les prix et le budget sont illustratifs.

**Données.**

- Sémantique : U2, U1, U3, U5, U4.
- BM25 : U1, U3, U2, U4, U5.
- Écart au budget (du plus proche au plus éloigné) : U3, U1, U4, U5, U2.
- Budget de l'acheteur : 1 800 000 AED ; prix de U1 : 1 750 000 AED ; prix de U2 : 2 100 000 AED.
- Frais de transfert DLD : 4 % du prix ; k_RRF = 60.

**Calcul pas à pas.**

**Étape 1, les scores RRF :**

$$
\operatorname{RRF}(U_1) = \frac{1}{62} + \frac{1}{61} + \frac{1}{62} \approx 0{,}048652, \qquad \operatorname{RRF}(U_3) = \frac{1}{63} + \frac{1}{62} + \frac{1}{61} \approx 0{,}048395
$$

$$
\operatorname{RRF}(U_2) = \frac{1}{61} + \frac{1}{63} + \frac{1}{65} \approx 0{,}047651, \quad \operatorname{RRF}(U_4) = \frac{1}{65} + \frac{1}{64} + \frac{1}{63} \approx 0{,}046883, \quad \operatorname{RRF}(U_5) \approx 0{,}046635
$$

**Étape 2, le top-3.** U1, U3, U2.

**Étape 3, les prix complets.** U1 : 1 750 000 × 1,04 = 1 820 000 AED, soit 20 000 AED au-dessus du budget ; U2 : 2 100 000 × 1,04 = 2 184 000 AED, soit 384 000 AED au-dessus.

**Décision de l'agent.** L'agent montre U1, U3 et U2 dans cet ordre, en indiquant pour chacune son rang dans chaque liste, ce qui rend la recommandation explicable. Il ajoute le prix frais DLD compris et signale que U1 dépasse le budget de 20 000 AED une fois les frais comptés, et U2 de 384 000 AED. Le compromis : U2, la meilleure description, reste dans le top-3 malgré son prix ; c'est voulu, l'acheteur peut décider d'élargir son budget, mais l'agent ne la présente pas en premier.

**Contre-calcul.** Avec la seule recherche sémantique, U2 serait présentée en tête, à 2 184 000 AED frais compris, 384 000 AED au-dessus du budget : une visite inutile, et un acheteur qui perd confiance. Une somme pondérée des trois scores obligerait à normaliser un cosinus, un BM25 et un écart de prix, puis à choisir trois poids sans requêtes étiquetées pour les régler.

**Sensibilité.** Pour passer devant U1, U2 devrait obtenir de la liste des prix au moins RRF(U1) − (1/61 + 1/63) ≈ 0,016385, plus que 1/62 ≈ 0,016129 mais moins que 1/61 ≈ 0,016393 : il faudrait qu'elle soit la plus proche du budget (rang 1). La valeur de bascule est donc le rang 1 dans la liste des prix.

**En production.** Les indicateurs suivis sont le taux de visites programmées après une recommandation et le NDCG@10 (fichier 26) sur des demandes étiquetées, avec une alerte si le NDCG@10 baisse de plus de 0,05 (illustratif). Les frais de transfert du DLD valent 4 % de la valeur du bien à Dubaï, et l'agent les inclut toujours dans la comparaison au budget.

### Cas 3 — [ASSUR] : un doublon exact face à un consensus moyen

**Contexte.** Un assureur auto et santé trie chaque jour ses déclarations de sinistre suspectes en fusionnant deux classements : celui d'un détecteur de déclarations quasi identiques (distance entre embeddings) et celui d'un modèle de facteurs de risque. Les enquêteurs revoient trois dossiers par jour en priorité. Ils exigent qu'un doublon exact, classé premier par le détecteur, soit revu en premier, même si le modèle de risque l'ignore. Les dossiers, les montants et la capacité de revue sont illustratifs.

**Données.**

- Détecteur : SIN-0412 (doublon exact), SIN-0101, SIN-0102, SIN-0103, SIN-0201, SIN-0202, SIN-0203, SIN-0104.
- Modèle de risque : SIN-0587, SIN-0301, SIN-0302, SIN-0303, SIN-0201, SIN-0202, SIN-0203, SIN-0304.
- Fraudes confirmées après enquête : SIN-0412 (18 500 AED, duplicata d'un sinistre déjà payé) et SIN-0201 (42 000 AED).
- Capacité : 3 dossiers revus en priorité par jour.

**Calcul pas à pas.**

**Étape 1, avec k_RRF = 60.** SIN-0201, cinquième dans les deux listes, obtient 2/65 ≈ 0,030769 ; SIN-0202, 2/66 ≈ 0,030303 ; SIN-0203, 2/67 ≈ 0,029851 ; le doublon SIN-0412 n'a que 1/61 ≈ 0,016393, à égalité avec SIN-0587, et arrive quatrième.

**Étape 2, la condition pour que le doublon passe devant SIN-0201.** On compare 1/(k + 1) à 2/(k + 5) :

$$
\frac{1}{k + 1} > \frac{2}{k + 5} \iff k + 5 > 2k + 2 \iff k < 3
$$

**Étape 3, avec k_RRF = 2.** SIN-0412 et SIN-0587 obtiennent 1/3, SIN-0201 2/7 ≈ 0,285714 : le top-3 est SIN-0412, SIN-0587, SIN-0201 (égalité départagée par le numéro de dossier).

**Étape 4, la fraude repérée dans les trois premiers dossiers.** k_RRF = 60 : 42 000 AED (SIN-0201 seulement). k_RRF = 2 : 18 500 + 42 000 = 60 500 AED. Règle « doublon exact en tête », puis k_RRF = 60 : SIN-0412, SIN-0201, SIN-0202, soit 60 500 AED.

**Décision de l'agent.** L'agent garde k_RRF = 60 pour la fusion, et applique avant elle une règle explicite : un doublon exact détecté passe en tête de file. Il obtient le même montant repéré qu'avec k_RRF = 2 (60 500 AED), sans faire entrer dans le top-3 le premier du modèle de risque (SIN-0587), qui n'est pas une fraude. Le compromis : la règle est une exception codée à la main, qu'il faut documenter et revoir ; mais elle traduit exactement l'exigence des enquêteurs, alors qu'un petit k_RRF changerait l'ordre de tous les dossiers.

**Contre-calcul.** Avec k_RRF = 60 sans règle, le doublon arrive quatrième, hors des trois dossiers revus en priorité : le duplicata de 18 500 AED peut être payé avant d'être vu. Et le top-3 contient SIN-0202 et SIN-0203, deux dossiers sans fraude que les deux outils classent moyennement : c'est le faux consensus d'outils qui regardent les mêmes signaux (démonstration 4).

**Sensibilité.** La valeur de bascule est k_RRF = 3 : en dessous, le doublon est strictement premier ; à k_RRF = 3, il est à égalité avec SIN-0201 et SIN-0587 (0,25 chacun) et perd au départage par numéro ; à partir de 4, SIN-0201 passe seul devant. La règle explicite rend la décision indépendante de ce réglage.

**En production.** Les indicateurs suivis sont la part des fraudes confirmées parmi les dossiers revus en priorité et le délai avant qu'un doublon détecté parvienne à un enquêteur, avec une alerte si ce délai dépasse un jour (illustratif). L'assureur est supervisé par la CBUAE ; l'agent ne refuse jamais un sinistre, il ordonne la file des enquêteurs, et la décision reste humaine.

### Cas 4 — [CRYPTO] : trois outils d'alerte aux échelles incompatibles

**Contexte.** L'agent de conformité d'une plateforme d'actifs virtuels agréée par la VARA reçoit chaque matin six alertes de liquidité classées par trois outils : des règles internes (nombre de règles déclenchées), un score d'anomalie (une probabilité) et un score d'exposition (un montant en AED). L'équipe conformité revoit trois alertes en priorité chaque matin. Les alertes, les scores et la capacité sont illustratifs.

**Données.**

- Règles (nombre de règles déclenchées) : A1 9, A2 7, A3 6, A4 5, A5 3, A6 2.
- Anomalie (probabilité) : A4 0,97 ; A5 0,91 ; A6 0,88 ; A2 0,70 ; A1 0,40 ; A3 0,35.
- Exposition (AED) : A6 1 900 000 ; A3 1 200 000 ; A5 300 000 ; A4 250 000 ; A2 120 000 ; A1 50 000.
- k_RRF = 60 ; 3 alertes revues en priorité.

**Calcul pas à pas.**

**Étape 1, les rangs.** Règles : A1, A2, A3, A4, A5, A6. Anomalie : A4, A5, A6, A2, A1, A3. Exposition : A6, A3, A5, A4, A2, A1.

**Étape 2, les scores RRF.** Par exemple, pour A4, rangs 4, 1 et 4 :

$$
\operatorname{RRF}(A_4) = \frac{1}{64} + \frac{1}{61} + \frac{1}{64} \approx 0{,}047643
$$

et de même A6 ≈ 0,047418 ; A5 ≈ 0,047387 ; A3 ≈ 0,047154 ; A2 ≈ 0,047139 ; A1 ≈ 0,046930.

**Étape 3, le top-3.** A4, A6, A5. L'écart entre le premier et le dernier n'est que de 0,000714, et A4 n'a que 1,0152 fois le score de A1 : ces nombres ordonnent, ils ne mesurent pas un risque.

**Étape 4, l'indépendance des outils.** La corrélation de Spearman entre deux classements de n éléments vaut 1 − 6 Σd²/(n(n² − 1)), où d est l'écart de rang de chaque alerte ; ici n(n² − 1) = 6 × 35 = 210. Entre anomalie et exposition, Σd² = 32 :

$$
\rho_{S,T} = 1 - \frac{6 \times 32}{210} \approx 0{,}085714
$$

et de même ρ = −0,6 entre règles et anomalie (Σd² = 56) et ρ ≈ −0,828571 entre règles et exposition (Σd² = 64).

**Décision de l'agent.** L'agent place A4, A6 et A5 en tête de la file de revue, en affichant les trois rangs de chaque alerte. Les trois outils sont faiblement ou négativement corrélés : leur accord n'est pas un faux consensus. L'agent ne gèle jamais un compte : il ordonne la file, et la décision reste à l'équipe conformité. Le compromis : A1, que les règles placent en tête avec 9 règles déclenchées, finit dernière, parce que les deux autres outils la jugent peu risquée ; l'équipe accepte ce choix, mais garde une revue hebdomadaire des alertes « premières d'un seul outil ».

**Contre-calcul.** Additionner les scores bruts revient à trier par exposition, puisque des montants de l'ordre du million écrasent des comptages de 2 à 9 et des probabilités inférieures à 1 : le top-3 serait A6, A3, A5. A4, la plus anormale (0,97), sortirait de la revue prioritaire, et A3, la moins anormale (0,35), y entrerait.

**Sensibilité.** La valeur de bascule est k_RRF = 3 : pour k_RRF ≤ 2, A1 entre dans le top-3 (à k_RRF = 2 : A4, A6, A1 ; à k_RRF = 0 : A4 et A6 à 1,5, A1 à 1,3667), parce qu'un petit k_RRF récompense la première place des règles ; dès k_RRF = 3, A5 la remplace.

**En production.** L'indicateur suivi est la précision des alertes revues en priorité (part des alertes confirmées), et l'équipe surveille la corrélation de Spearman entre chaque paire d'outils, avec une alerte au-dessus de 0,8 (illustratif), signe que deux outils votent pour les mêmes raisons. Les obligations de surveillance des plateformes agréées sont à confirmer avec le règlement de la VARA en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Avec k_RRF = 60, calculer le score d'un document classé 3ᵉ par un moteur et 10ᵉ par un autre.

**Exercice 2.** Avec k_RRF = 0, comparer un document premier chez un seul moteur et un document deuxième chez deux moteurs.

**Exercice 3.** Démontrer que multiplier tous les scores d'un moteur par 1 000 ne change pas la fusion.

**Exercice 4.** Avec k_RRF = 60, jusqu'à quel rang r deux contributions 2/(60 + r) battent-elles une première place isolée ?

**Exercice 5.** Pourquoi faut-il filtrer les documents interdits avant la fusion, et non après ?

**Exercice 6 (modifier un cas).** Dans le cas 1, la mémoire renvoie maintenant C1, C6, C5 (C5 passe du rang 1 au rang 3). Recalculer C1, C5 et C2. Le top-3 injecté change-t-il ?

**Exercice 7 (trouver l'erreur).** Un collègue code la boucle avec `enumerate(liste)` sans `start=1` et obtient, pour α dans l'exemple simple, 1/60 + 1/61 ≈ 0,033060. Trouver l'erreur, dire ce qui se passe avec k_RRF = 0, et dire pourquoi la borne de la démonstration 1 semble violée.

**Exercice 8 (redémontrer de mémoire).** Sans regarder la démonstration 4, montrer qu'avec deux classements, un document classé dans les k_RRF + 1 premiers de chacun bat tout document présent dans un seul classement.

## Corrigé

**Exercice 1.** 1/63 + 1/70 ≈ 0,015873 + 0,014286 = 0,030159.

**Exercice 2.** 1/(0 + 1) = 1 contre 1/(0 + 2) + 1/(0 + 2) = 2/2 = 1 : égalité. Avec k_RRF = 0, le premier rang pèse autant que deux deuxièmes places (démonstration 4, contre-exemple).

**Exercice 3.** Multiplier par 1 000 > 0 est une fonction strictement croissante : elle conserve l'ordre, donc les rangs, donc chaque contribution 1/(k_RRF + rang), donc la fusion (démonstration 2).

**Exercice 4.** 2/(60 + r) > 1/61 équivaut à 2 × 61 > 60 + r, soit r < 62 : jusqu'au rang 61 ; au rang 62, égalité exacte, 2/122 = 1/61.

**Exercice 5.** Un document interdit qui monte dans la fusion peut être injecté dans le contexte de l'agent, puis cité. Le contrôle d'accès s'applique à la source, dans chaque moteur, avant tout classement ; filtrer après la fusion laisserait aussi le document interdit pousser les autres vers le bas.

**Exercice 6.** C1 a les rangs 3, 1 et 1 : 1/63 + 1/61 + 1/61 ≈ 0,048660. C5 a les rangs 2, 4 et 3 : 1/62 + 1/64 + 1/63 ≈ 0,047627. C2 ne change pas : 0,032522. Le top-3 reste C1, C5, C2 : C5 perd 0,000520 mais reste cité par les trois moteurs, et la démonstration 4 garantit qu'il reste devant C2, cité par deux.

**Exercice 7.** Sans `start=1`, le premier document reçoit le rang 0 : α obtient 1/(60 + 0) + 1/(60 + 1) ≈ 0,016667 + 0,016393 = 0,033060 au lieu de 0,032522, et toutes les contributions sont décalées d'un rang. Avec k_RRF = 0, le premier document donne 1/0 : division par zéro. La « borne » 2/61 semble violée (0,033060 > 0,032787) parce qu'elle suppose des rangs ≥ 1 : c'est l'hypothèse de l'étape 1 de la démonstration 1 qui manque.

**Exercice 8.** Étape 1 : si r ≤ k + 1, alors k + r ≤ 2k + 1, donc 1/(k + r) ≥ 1/(2k + 1) ; la somme des deux contributions vaut au moins 2/(2k + 1). Étape 2 : 2/(2k + 1) > 1/(k + 1) équivaut à 2k + 2 > 2k + 1, vrai. Étape 3 : 1/(k + 1) est le maximum pour un document présent dans une seule liste (démonstration 1). Avec k = 60 : 2/121 ≈ 0,016529 > 1/61 ≈ 0,016393.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`dedoublonner(classement)`** — Cette fonction est l'huissier qui veille à ce qu'aucun document ne vote deux fois dans la même liste : elle reçoit un classement, c'est-à-dire une liste ordonnée de noms de documents, et le fait passer dans `dict.fromkeys`, qui ne garde que la première apparition de chaque nom tout en conservant l'ordre. Elle renvoie la liste nettoyée, si bien qu'un document répété ne garde que son meilleur rang ; `rrf` l'appelle sur chaque liste avant de compter, et `main` vérifie qu'avec la liste A, A, B le document A ne reçoit bien que 1/61.

**`rrf(classements, k_rrf, poids)`** — Voici le cœur du programme, un scrutateur qui dépouille plusieurs bulletins de classement sans jamais lire les scores d'origine : la fonction reçoit une liste de classements, la constante `k_rrf`, 60 par défaut, et une liste facultative de poids, un par classement. Elle lève une `ValueError` si `k_rrf` est négatif ou si le nombre de poids ne correspond pas au nombre de listes, puis, pour chaque liste dédoublonnée, donne à chaque document la contribution w / (k + rang), avec des rangs qui commencent à 1, et additionne ces contributions document par document. Elle renvoie la liste des couples (document, score) triée par score décroissant, les égalités étant départagées par ordre alphabétique du nom, par exemple C1 à 0,048395 en tête du cas bancaire.

**`ordre(fusion)`** — Cette petite fonction est le crieur qui ne lit à voix haute que les noms du palmarès, sans les points : elle reçoit la liste de couples (document, score) que renvoie `rrf` et en extrait, dans le même ordre, les seuls noms de documents. Elle renvoie cette liste de noms, que `main` et les cas comparent aux ordres attendus, comme C1, C5, C2, C3, C6, C4 dans le cas bancaire, ou dont ils prennent les trois premiers éléments pour savoir quels dossiers entrent dans la revue prioritaire.

**`classement_depuis_scores(scores)`** — Cette fonction joue le greffier qui transforme le carnet de notes d'un moteur en simple ordre d'arrivée : elle reçoit un dictionnaire qui associe à chaque document son score brut, cosinus, BM25, probabilité ou montant en AED, trie les documents par score décroissant en départageant les égalités par le nom, puis renvoie la liste ordonnée des noms. Elle est la porte d'entrée de tous les cas, car c'est à partir de ce seul ordre que `rrf` travaille, ce qui rend les échelles des moteurs sans importance, comme le vérifie la démonstration 2.

**`spearman(a, b)`** — Cette fonction se comporte comme un enquêteur qui veut savoir si deux témoins racontent la même histoire : elle reçoit deux classements `a` et `b`, lève une `ValueError` s'ils ne portent pas sur les mêmes éléments ou s'ils en comptent moins de deux, note le rang de chaque élément dans `b`, additionne les carrés des écarts de rang avec `a`, puis renvoie 1 − 6 Σd² / (n(n² − 1)). Dans le cas des alertes, elle donne −0,6 entre règles et anomalie, environ −0,828571 entre règles et exposition et 0,085714 entre anomalie et exposition, ce qui montre que les trois outils ne votent pas pour les mêmes raisons.

**`r(x, n)`** — Ce minuscule outil est le copiste qui met les nombres au propre avant de les comparer au texte : il reçoit un nombre `x` et un nombre de décimales `n`, arrondit `x` à `n` décimales avec `round` et ajoute 0.0, ce qui remplace un éventuel zéro négatif par un zéro ordinaire. Il renvoie ce nombre arrondi, et la plupart des `assert` de `main` passent par lui pour confronter les scores aux valeurs à six décimales de la fiche, comme 0,032522 pour α dans l'exemple simple.

**`cas_1_support_banque()`** — Cette fonction rejoue la scène d'un assistant de banque de détail qui interroge trois moteurs sur une question de remboursement anticipé et doit choisir trois passages : sans paramètre, elle transforme les scores du moteur sémantique, de BM25 et de la mémoire en classements, les fusionne avec k = 60 puis k = 1, et obtient en tête C1 (0,048395), C5 (0,048147) et C2 (0,032522). Elle calcule aussi la somme naïve des scores bruts, dont le top-3 C1, C2, C3 écarte C5, et le score de C5 quand la mémoire ne le renvoie plus, 0,031754, qui le fait passer derrière C2 ; elle imprime deux lignes et renvoie un dictionnaire de tous ces résultats.

**`cas_2_unites_immo()`** — Ici, la fonction joue le conseiller d'une agence immobilière qui doit fusionner trois classements d'unités sans unité commune, similarité des descriptions, BM25 sur les codes et écart de prix au budget : sans paramètre, elle fusionne les trois listes avec k = 60 et obtient l'ordre U1, U3, U2, U4, U5, puis calcule les prix frais de transfert de 4 % compris, 1 820 000 AED pour U1 et 2 184 000 AED pour U2, soit 384 000 AED au-dessus du budget de 1 800 000 AED. Elle calcule enfin ce qu'il manquerait à U2 dans la liste des prix pour passer devant U1, environ 0,016385, en déduit qu'il lui faudrait le rang 1, imprime deux lignes et renvoie un dictionnaire de ces valeurs.

**`cas_3_doublons_assur()`** — Cette fonction se met dans la peau d'une cellule d'enquête d'un assureur qui ne peut revoir que trois dossiers de sinistre par jour : sans paramètre, elle fusionne la liste du détecteur de doublons et celle du modèle de risque pour k = 0, 2, 3, 4 et 60, cherche la plus grande valeur de k pour laquelle le doublon exact SIN-0412 reste premier, 2, et construit la liste `regle`, qui place d'office ce doublon en tête avant la fusion à k = 60. Elle additionne ensuite les fraudes confirmées présentes dans chaque top-3, 42 000 AED à k = 60, 60 500 AED à k = 2 et 60 500 AED avec la règle, imprime deux lignes et renvoie un dictionnaire avec les têtes, la valeur limite, la règle, les montants et les scores à k = 60 et k = 3.

**`cas_4_alertes_crypto()`** — Cette fonction joue l'agent de conformité d'une plateforme d'actifs virtuels qui reçoit six alertes classées par trois outils aux échelles incompatibles, un nombre de règles, une probabilité et un montant en AED : sans paramètre, elle transforme chaque outil en classement, fusionne avec k = 60 pour obtenir A4, A6, A5 en tête, et compare à la somme brute des scores, qui revient à trier par exposition et donne A6, A3, A5. Elle cherche la plus petite valeur de k pour laquelle A1 sort du top-3, 3, calcule les trois corrélations de Spearman et l'écart de 0,000714 entre la première et la dernière alerte, imprime deux lignes et renvoie un dictionnaire qui contient aussi les scores à k = 0 et le top-3 à k = 2.

**`main()`** — C'est le chef d'orchestre qui fait jouer toutes les démonstrations de la fiche : il suit d'abord un document classé 1ᵉʳ et 3ᵉ pour k = 60 et k = 0, vérifie la borne 2/61 ≈ 0,032787 et le dédoublonnage, l'invariance de la fusion quand on transforme les scores par une fonction strictement croissante, le rôle de k, à partir duquel un document 5ᵉ et 6ᵉ bat un premier isolé dès k = 4, le consensus jusqu'au rang 61, la convexité et le comportement pour un très grand k. Il refait l'exemple simple, appelle les quatre cas en confrontant chaque nombre par un `assert` aux valeurs du texte, recalcule le corrigé, y compris l'erreur d'un `enumerate` sans `start=1` qui mène à une division par zéro avec k = 0, et n'imprime le message final que si tout concorde.

```python
"""Démonstration 25 — RRF : bornes, invariance, rôle de k_RRF, consensus, convexité, grand k_RRF, quatre cas aux EAU."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def dedoublonner(classement: list[str]) -> list[str]:
    """Garde la première occurrence : un document n'a qu'un rang dans une liste."""
    return list(dict.fromkeys(classement))


def rrf(classements: list[list[str]], k_rrf: float = 60, poids: list[float] | None = None) -> list[tuple[str, float]]:
    """Reciprocal Rank Fusion (leçon 24) ; un document absent d'une liste n'y gagne rien ; égalités par nom."""
    if k_rrf < 0:
        raise ValueError("k_RRF doit être >= 0")
    if poids is not None and len(poids) != len(classements):
        raise ValueError("un poids par classement")
    scores: dict[str, float] = {}
    for j, classement in enumerate(classements):
        w = 1.0 if poids is None else poids[j]
        for rang, doc in enumerate(dedoublonner(classement), start=1):
            scores[doc] = scores.get(doc, 0.0) + w / (k_rrf + rang)
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))


def ordre(fusion: list[tuple[str, float]]) -> list[str]:
    return [d for d, _ in fusion]


def classement_depuis_scores(scores: dict[str, float]) -> list[str]:
    """Les rangs d'un moteur : score décroissant, nom en cas d'égalité."""
    return [d for d, _ in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))]


def spearman(a: list[str], b: list[str]) -> float:
    """Corrélation de rangs de Spearman entre deux classements des mêmes n éléments, sans ex aequo."""
    if sorted(a) != sorted(b) or len(a) < 2:
        raise ValueError("il faut deux classements des mêmes éléments (au moins 2)")
    n = len(a)
    rb = {d: i for i, d in enumerate(b, start=1)}
    s = sum((i - rb[d]) ** 2 for i, d in enumerate(a, start=1))
    return 1 - 6 * s / (n * (n * n - 1))


def r(x: float, n: int) -> float:
    return round(x, n) + 0.0


def cas_1_support_banque() -> dict:
    """[BANQUE] Trois moteurs (sémantique, BM25, mémoire) pour l'assistant d'une banque de détail."""
    cos = {"C2": 0.82, "C5": 0.80, "C1": 0.78, "C4": 0.75}
    bm25 = {"C1": 14.2, "C2": 9.1, "C3": 8.0, "C5": 5.5}
    memoire = {"C5": 0.95, "C1": 0.60, "C6": 0.40}
    moteurs = [classement_depuis_scores(x) for x in (cos, bm25, memoire)]
    s60, s1 = rrf(moteurs, 60), rrf(moteurs, 1)
    somme: dict[str, float] = {}
    for x in (cos, bm25, memoire):
        for d, v in x.items():
            somme[d] = somme.get(d, 0.0) + v
    naif = classement_depuis_scores(somme)
    sans_memoire = dict(rrf([moteurs[0], moteurs[1], ["C1", "C6"]], 60))
    print("Cas 1 — BANQUE : k_RRF = 60 : " + " ; ".join(f"{d} {v:.6f}" for d, v in s60))
    print("  k_RRF = 1 : " + " ; ".join(f"{d} {v:.4f}" for d, v in s1[:3])
          + f" ; somme brute des scores : top-3 {naif[:3]} ; C5 absent de la mémoire : {sans_memoire['C5']:.6f}")
    return {"moteurs": moteurs, "s60": dict(s60), "o60": ordre(s60), "s1": dict(s1), "o1": ordre(s1),
            "somme": somme, "naif": naif, "sans_memoire": sans_memoire}


def cas_2_unites_immo() -> dict:
    """[IMMO] Fusionner trois classements sans unité commune : sémantique, BM25 sur les codes, écart de prix."""
    semantique = ["U2", "U1", "U3", "U5", "U4"]
    lexical = ["U1", "U3", "U2", "U4", "U5"]
    prix = ["U3", "U1", "U4", "U5", "U2"]                          # écart au budget en AED/sqft croissant
    fusion = rrf([semantique, lexical, prix])
    s = dict(fusion)
    budget, prix_u2, prix_u1 = 1_800_000, 2_100_000, 1_750_000
    total_u2, total_u1 = prix_u2 * 1.04, prix_u1 * 1.04
    seuil_u2 = s["U1"] - (1 / 61 + 1 / 63)                          # ce qu'il faudrait à U2 dans la liste des prix
    rang_u2 = next(k for k in range(1, 6) if 1 / (60 + k) <= seuil_u2) - 1
    print("Cas 2 — IMMO : " + " ; ".join(f"{d} {v:.6f}" for d, v in fusion)
          + f" ; U2 seul en tête du sémantique : {total_u2:.0f} AED frais DLD compris, budget {budget}")
    print(f"  U1 : {total_u1:.0f} AED ; U2 devrait être au rang {rang_u2} des prix pour passer devant U1 (il lui manque {seuil_u2:.6f})")
    return {"fusion": s, "ordre": ordre(fusion), "total_u2": total_u2, "total_u1": total_u1,
            "depassement": total_u2 - budget, "seuil_u2": seuil_u2, "rang_u2": rang_u2}


def cas_3_doublons_assur() -> dict:
    """[ASSUR] Un doublon exact, premier d'un seul outil, face à un consensus moyen des deux outils."""
    detecteur = ["SIN-0412", "SIN-0101", "SIN-0102", "SIN-0103", "SIN-0201", "SIN-0202", "SIN-0203", "SIN-0104"]
    risque = ["SIN-0587", "SIN-0301", "SIN-0302", "SIN-0303", "SIN-0201", "SIN-0202", "SIN-0203", "SIN-0304"]
    fraude = {"SIN-0412": 18_500, "SIN-0201": 42_000}               # fraudes confirmées et montants (AED)
    tetes = {k: ordre(rrf([detecteur, risque], k))[:3] for k in (0, 2, 3, 4, 60)}
    k_max = max(k for k in range(0, 61) if ordre(rrf([detecteur, risque], k))[0] == "SIN-0412")
    regle = ["SIN-0412"] + [d for d in ordre(rrf([detecteur, risque], 60)) if d != "SIN-0412"]
    montant = {nom: sum(fraude.get(d, 0) for d in tete) for nom, tete in
               (("k60", tetes[60]), ("k2", tetes[2]), ("regle", regle[:3]))}
    print("Cas 3 — ASSUR : top-3 k = 60 " + str(tetes[60]) + " ; k = 2 " + str(tetes[2])
          + f" ; le doublon reste premier jusqu'à k_RRF = {k_max}")
    print(f"  fraude repérée dans le top-3 : k = 60 {montant['k60']} AED ; k = 2 {montant['k2']} AED ;"
          f" règle doublon + k = 60 {montant['regle']} AED")
    return {"tetes": tetes, "k_max": k_max, "regle": regle, "montant": montant,
            "s60": dict(rrf([detecteur, risque], 60)), "s3": dict(rrf([detecteur, risque], 3))}


def cas_4_alertes_crypto() -> dict:
    """[CRYPTO] Trois outils d'alerte aux échelles incompatibles : comptage, probabilité, montant en AED."""
    regles = {"A1": 9, "A2": 7, "A3": 6, "A4": 5, "A5": 3, "A6": 2}
    anomalie = {"A4": 0.97, "A5": 0.91, "A6": 0.88, "A2": 0.70, "A1": 0.40, "A3": 0.35}
    exposition = {"A6": 1_900_000, "A3": 1_200_000, "A5": 300_000, "A4": 250_000, "A2": 120_000, "A1": 50_000}
    listes = [classement_depuis_scores(x) for x in (regles, anomalie, exposition)]
    fusion = rrf(listes, 60)
    naif = classement_depuis_scores({d: regles[d] + anomalie[d] + exposition[d] for d in regles})
    k_bascule = next(k for k in range(0, 61) if "A1" not in ordre(rrf(listes, k))[:3])
    rho = (spearman(listes[0], listes[1]), spearman(listes[0], listes[2]), spearman(listes[1], listes[2]))
    ecart = fusion[0][1] - fusion[-1][1]
    print("Cas 4 — CRYPTO : RRF " + " ; ".join(f"{d} {v:.6f}" for d, v in fusion)
          + f" ; somme brute : {naif[:3]}")
    print(f"  A1 sort du top-3 dès k_RRF = {k_bascule} ; Spearman R/S {rho[0]:.6f}, R/T {rho[1]:.6f}, S/T {rho[2]:.6f}")
    return {"listes": listes, "fusion": dict(fusion), "ordre": ordre(fusion), "naif": naif,
            "k_bascule": k_bascule, "rho": rho, "ecart": ecart,
            "k0": dict(rrf(listes, 0)), "o2": ordre(rrf(listes, 2))[:3]}


def main() -> None:
    # Le mécanisme : un document suivi dans deux listes, pour k_RRF = 60 et k_RRF = 0
    film = [(k, 1 / (k + 1), 1 / (k + 3), 1 / (k + 1) + 1 / (k + 3)) for k in (60, 0)]
    print("Mécanisme : rangs 1 et 3 → " + " ; ".join(f"k = {k} : {a:.6f} + {b:.6f} = {s:.6f}" for k, a, b, s in film))
    assert [(r(a, 6), r(b, 6), r(s, 6)) for _, a, b, s in film] == [(0.016393, 0.015873, 0.032266), (1.0, 0.333333, 1.333333)]
    assert r(1 / 61 + 1 / 62 + 1 / 63, 6) == 0.048395

    # Démonstration 1 : bornes
    assert all(0 < 1 / (60 + rg) <= 1 / 61 for rg in range(1, 1000))
    premier = dict(rrf([["X", "A"], ["X", "B"]]))["X"]
    print(f"Démo 1 : borne 2/61 = {2 / 61:.6f} ; premier partout = {premier:.6f} ; trois listes 3/61 = {3 / 61:.6f}")
    assert premier == 2 / 61 and r(2 / 61, 6) == 0.032787 and r(3 / 61, 6) == 0.04918
    assert dict(rrf([["A", "A", "B"]]))["A"] == 1 / 61                    # dédoublonnage : un seul rang par liste

    # Démonstration 2 : invariance par transformation strictement croissante des scores
    cos = {"A": 0.82, "B": 0.80, "C": 0.78, "D": 0.75}
    bm = {"C": 8.0, "A": 6.0, "E": 5.0, "B": 2.0}
    base = rrf([classement_depuis_scores(cos), classement_depuis_scores(bm)])
    transf = rrf([classement_depuis_scores({d: math.exp(10 * v) for d, v in cos.items()}),
                  classement_depuis_scores({d: math.log(1 + v) for d, v in bm.items()})])
    arrondi = rrf([classement_depuis_scores(cos), classement_depuis_scores({d: min(v, 2.0) for d, v in bm.items()})])
    print("Démo 2 : " + " ; ".join(f"{d} {v:.6f}" for d, v in base) + f" ; BM25 plafonné à 2 : {ordre(arrondi)}")
    assert transf == base and ordre(base) == ["A", "C", "B", "E", "D"] and ordre(arrondi) == ["A", "B", "C", "D", "E"]
    assert [r(v, 6) for _, v in base] == [0.032522, 0.032266, 0.031754, 0.015873, 0.015625]

    # Démonstration 3 : rôle de k_RRF
    perte = (1 / 1 - 1 / 2, 1 / 61 - 1 / 62)
    rapport = ((0 + 10) / (0 + 1), (60 + 10) / (60 + 1))
    k_y = next(k for k in range(0, 100) if 1 / (k + 5) + 1 / (k + 6) > 1 / (k + 1))
    print(f"Démo 3 : perte rang 1 → 2 : {perte[0]} (k = 0), {perte[1]:.5f} (k = 60) ; rapport rang 1 / rang 10 :"
          f" {rapport[0]:.0f} et {rapport[1]:.3f} ; Y (5e et 6e) bat X (1er seul) dès k_RRF = {k_y}")
    assert perte[0] == 0.5 and r(perte[1], 5) == 0.00026 and r(perte[1], 10) == r(1 / (61 * 62), 10)
    assert rapport[0] == 10 and r(rapport[1], 3) == 1.148 and k_y == 4 and r(-1 + math.sqrt(20), 2) == 3.47
    assert all((1 / (k + 5) + 1 / (k + 6) > 1 / (k + 1)) == (k * k + 2 * k - 19 > 0) for k in range(0, 100))

    # Démonstration 4 : consensus
    print(f"Démo 4 : premier isolé {1 / 61:.6f} ; deux fois deuxième {2 / 62:.6f} ; deux fois 61e {2 / 121:.6f} ; deux fois 62e {2 / 122:.6f}")
    assert 2 / 62 > 1 / 61 and r(1 / 61, 6) == 0.016393 and r(2 / 62, 6) == 0.032258 and r(2 / 121, 6) == 0.016529
    assert max(rg for rg in range(1, 200) if 2 / (60 + rg) > 1 / 61) == 61 and 2 / 122 == 1 / 61
    assert all(1 / (60 + a) + 1 / (60 + b) > 1 / 61 for a in range(1, 62) for b in range(1, 62))
    assert r(2 / 63, 6) == 0.031746 and 2 / 63 > 1 / 61

    # Démonstration 5 : convexité, à somme de rangs égale
    un_trois, deux_deux = 1 / 61 + 1 / 63, 2 / 62
    print(f"Démo 5 : rangs 1 et 3 {un_trois:.6f} ; rangs 2 et 2 {deux_deux:.6f} ; écart {un_trois - deux_deux:.2e} = 2/(61×62×63)")
    assert r(un_trois, 6) == 0.032266 and r(deux_deux, 6) == 0.032258 and abs(un_trois - deux_deux - 2 / (61 * 62 * 63)) < 1e-15
    assert all(abs(1 / (k + 1) + 1 / (k + 3) - 2 / (k + 2) - 2 / ((k + 1) * (k + 2) * (k + 3))) < 1e-12 for k in range(0, 100))

    # Démonstration 6 : grand k_RRF — on classe par nombre de listes, puis par somme des rangs
    a_14, b_22 = (lambda k: 1 / (k + 1) + 1 / (k + 4)), (lambda k: 2 / (k + 2))
    k_ab = [k for k in (0, 1, 2, 3, 60) if a_14(k) > b_22(k)]
    grand = 1e6 ** 2 * (b_22(1e6) - a_14(1e6))
    print(f"Démo 6 : rangs (1, 4) contre (2, 2) : k = 0 {a_14(0):.4f} > {b_22(0):.4f} ; k = 60 {a_14(60):.6f} < {b_22(60):.6f} ;"
          f" égalité en k = {a_14(2) == b_22(2) and 2} ; k² × écart (k = 1e6) = {grand:.4f}")
    assert k_ab == [0, 1] and a_14(2) == b_22(2) and r(a_14(0), 4) == 1.25 and b_22(0) == 1.0
    assert r(a_14(60), 6) == 0.032018 and r(b_22(60), 6) == 0.032258 and r(grand, 4) == 1.0

    # Exemple simple
    s = dict(rrf([["α", "β", "γ", "δ", "ε"], ["β", "α", "δ", "ζ", "γ"]]))
    print("Exemple simple : " + " ; ".join(f"{d} {v:.6f}" for d, v in rrf([["α", "β", "γ", "δ", "ε"], ["β", "α", "δ", "ζ", "γ"]])))
    assert math.isclose(s["α"], s["β"]) and r(s["α"], 6) == 0.032522
    assert [r(s[d], 6) for d in ("δ", "γ", "ζ", "ε")] == [0.031498, 0.031258, 0.015625, 0.015385]
    assert ordre(rrf([["α", "β", "γ", "δ", "ε"], ["β", "α", "δ", "ζ", "γ"]]))[2:] == ["δ", "γ", "ζ", "ε"]
    assert [r(1 / x, 6) for x in (61, 62, 63, 64, 65)] == [0.016393, 0.016129, 0.015873, 0.015625, 0.015385]

    # Cas 1 — BANQUE
    c1 = cas_1_support_banque()
    assert c1["moteurs"] == [["C2", "C5", "C1", "C4"], ["C1", "C2", "C3", "C5"], ["C5", "C1", "C6"]]
    assert c1["o60"] == ["C1", "C5", "C2", "C3", "C6", "C4"]
    assert [r(c1["s60"][d], 6) for d in c1["o60"]] == [0.048395, 0.048147, 0.032522, 0.015873, 0.015873, 0.015625]
    assert c1["o1"][:3] == ["C1", "C5", "C2"] and [r(c1["s1"][d], 4) for d in ("C1", "C5", "C2")] == [1.0833, 1.0333, 0.8333]
    assert [r(c1["s1"][d], 4) for d in ("C3", "C6", "C4")] == [0.25, 0.25, 0.2]
    assert [r(c1["somme"][d], 2) for d in ("C1", "C2", "C3", "C5")] == [15.58, 9.92, 8.0, 7.25]
    assert c1["naif"][:3] == ["C1", "C2", "C3"] and "C5" not in c1["naif"][:3]
    assert r(c1["sans_memoire"]["C5"], 6) == 0.031754 and c1["sans_memoire"]["C5"] < c1["sans_memoire"]["C2"]
    assert all(1 / 62 + 1 / (60 + rg) + 1 / 61 > 1 / 61 + 1 / 62 for rg in range(1, 1000))   # C5 devant C2 à tout rang BM25
    assert 10_000 * 0.03 == 300

    # Cas 2 — IMMO
    c2 = cas_2_unites_immo()
    assert c2["ordre"] == ["U1", "U3", "U2", "U4", "U5"]
    assert [r(c2["fusion"][d], 6) for d in c2["ordre"]] == [0.048652, 0.048395, 0.047651, 0.046883, 0.046635]
    assert (c2["total_u2"], c2["total_u1"], c2["depassement"]) == (2_184_000, 1_820_000, 384_000)
    assert r(c2["seuil_u2"], 6) == 0.016385 and c2["rang_u2"] == 1 and 1 / 61 > c2["seuil_u2"] > 1 / 62
    assert r(1 / 63 + 1 / 61 + 1 / 64, 6) == 0.047891 and r(2_100_000 * 0.04, 6) == 84_000 and r(1_750_000 * 0.04, 6) == 70_000

    # Cas 3 — ASSUR
    c3 = cas_3_doublons_assur()
    assert c3["tetes"][60] == ["SIN-0201", "SIN-0202", "SIN-0203"] and c3["tetes"][2] == ["SIN-0412", "SIN-0587", "SIN-0201"]
    assert c3["tetes"][3][0] == "SIN-0201" and c3["tetes"][4][0] == "SIN-0201" and c3["k_max"] == 2
    assert c3["s3"]["SIN-0412"] == c3["s3"]["SIN-0201"] == 0.25                       # k = 3 : égalité, départagée par le nom
    assert [r(c3["s60"][d], 6) for d in ("SIN-0201", "SIN-0202", "SIN-0203", "SIN-0412")] == [0.030769, 0.030303, 0.029851, 0.016393]
    assert c3["regle"][:3] == ["SIN-0412", "SIN-0201", "SIN-0202"]
    assert c3["montant"] == {"k60": 42_000, "k2": 60_500, "regle": 60_500}
    assert all((1 / (k + 1) > 2 / (k + 5)) == (k < 3) for k in range(0, 100))

    # Cas 4 — CRYPTO
    c4 = cas_4_alertes_crypto()
    assert c4["listes"] == [["A1", "A2", "A3", "A4", "A5", "A6"], ["A4", "A5", "A6", "A2", "A1", "A3"],
                            ["A6", "A3", "A5", "A4", "A2", "A1"]]
    assert c4["ordre"] == ["A4", "A6", "A5", "A3", "A2", "A1"]
    assert [r(c4["fusion"][d], 6) for d in c4["ordre"]] == [0.047643, 0.047418, 0.047387, 0.047154, 0.047139, 0.04693]
    assert c4["naif"][:3] == ["A6", "A3", "A5"] and c4["k_bascule"] == 3 and c4["o2"] == ["A4", "A6", "A1"]
    assert [r(v, 6) for v in c4["rho"]] == [-0.6, -0.828571, 0.085714] and r(c4["ecart"], 6) == 0.000714
    assert [r(1 - 6 * s / 210, 6) for s in (56, 64, 32)] == [r(v, 6) for v in c4["rho"]] and 6 * (36 - 1) == 210
    assert r(1 / 64 + 1 / 61 + 1 / 64, 6) == 0.047643 and 1_820_000 - 1_800_000 == 20_000
    assert [r(c4["k0"][d], 4) for d in ("A4", "A6", "A1")] == [1.5, 1.5, 1.3667]
    assert r(c4["fusion"]["A4"] / c4["fusion"]["A1"], 4) == 1.0152

    print("Corrigé")
    ex6 = dict(rrf([["C2", "C5", "C1", "C4"], ["C1", "C2", "C3", "C5"], ["C1", "C6", "C5"]]))
    print(f"  ex1 {1 / 63 + 1 / 70:.6f} ; ex2 {1 / 1} contre {2 / 2} ; ex4 rang 61 ; ex6 C1 {ex6['C1']:.6f}, C5 {ex6['C5']:.6f}, C2 {ex6['C2']:.6f}")
    assert r(1 / 63 + 1 / 70, 6) == 0.030159 and r(1 / 70, 6) == 0.014286
    assert r(ex6["C5"], 6) == 0.047627 and ex6["C5"] > ex6["C2"] and r(ex6["C1"], 6) == 0.04866
    assert r(c1["s60"]["C5"] - ex6["C5"], 6) == 0.00052 and r(2 / 7, 6) == 0.285714 and 18_500 + 42_000 == 60_500
    decale = sum(1 / (60 + i) for i, d in enumerate(["α", "β", "γ", "δ", "ε"]) if d == "α") + 1 / (60 + 1)
    assert r(decale, 6) == 0.03306 and r(1 / 60, 6) == 0.016667 and decale > s["α"]
    assert decale > 2 / 61
    erreur = 0
    try:
        sum(1 / (0 + i) for i, _ in enumerate(["α", "β"]))
    except ZeroDivisionError:
        erreur = 1
    assert erreur == 1                                                    # sans start=1 et k_RRF = 0 : division par zéro
    assert all(1 / (k + a) + 1 / (k + b) >= 2 / (2 * k + 1) > 1 / (k + 1)
               for k in (0, 1, 60) for a in range(1, k + 2) for b in range(1, k + 2))
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Mécanisme : rangs 1 et 3 → k = 60 : 0.016393 + 0.015873 = 0.032266 ; k = 0 : 1.000000 + 0.333333 = 1.333333
Démo 1 : borne 2/61 = 0.032787 ; premier partout = 0.032787 ; trois listes 3/61 = 0.049180
Démo 2 : A 0.032522 ; C 0.032266 ; B 0.031754 ; E 0.015873 ; D 0.015625 ; BM25 plafonné à 2 : ['A', 'B', 'C', 'D', 'E']
Démo 3 : perte rang 1 → 2 : 0.5 (k = 0), 0.00026 (k = 60) ; rapport rang 1 / rang 10 : 10 et 1.148 ; Y (5e et 6e) bat X (1er seul) dès k_RRF = 4
Démo 4 : premier isolé 0.016393 ; deux fois deuxième 0.032258 ; deux fois 61e 0.016529 ; deux fois 62e 0.016393
Démo 5 : rangs 1 et 3 0.032266 ; rangs 2 et 2 0.032258 ; écart 8.39e-06 = 2/(61×62×63)
Démo 6 : rangs (1, 4) contre (2, 2) : k = 0 1.2500 > 1.0000 ; k = 60 0.032018 < 0.032258 ; égalité en k = 2 ; k² × écart (k = 1e6) = 1.0000
Exemple simple : α 0.032522 ; β 0.032522 ; δ 0.031498 ; γ 0.031258 ; ζ 0.015625 ; ε 0.015385
Cas 1 — BANQUE : k_RRF = 60 : C1 0.048395 ; C5 0.048147 ; C2 0.032522 ; C3 0.015873 ; C6 0.015873 ; C4 0.015625
  k_RRF = 1 : C1 1.0833 ; C5 1.0333 ; C2 0.8333 ; somme brute des scores : top-3 ['C1', 'C2', 'C3'] ; C5 absent de la mémoire : 0.031754
Cas 2 — IMMO : U1 0.048652 ; U3 0.048395 ; U2 0.047651 ; U4 0.046883 ; U5 0.046635 ; U2 seul en tête du sémantique : 2184000 AED frais DLD compris, budget 1800000
  U1 : 1820000 AED ; U2 devrait être au rang 1 des prix pour passer devant U1 (il lui manque 0.016385)
Cas 3 — ASSUR : top-3 k = 60 ['SIN-0201', 'SIN-0202', 'SIN-0203'] ; k = 2 ['SIN-0412', 'SIN-0587', 'SIN-0201'] ; le doublon reste premier jusqu'à k_RRF = 2
  fraude repérée dans le top-3 : k = 60 42000 AED ; k = 2 60500 AED ; règle doublon + k = 60 60500 AED
Cas 4 — CRYPTO : RRF A4 0.047643 ; A6 0.047418 ; A5 0.047387 ; A3 0.047154 ; A2 0.047139 ; A1 0.046930 ; somme brute : ['A6', 'A3', 'A5']
  A1 sort du top-3 dès k_RRF = 3 ; Spearman R/S -0.600000, R/T -0.828571, S/T 0.085714
Corrigé
  ex1 0.030159 ; ex2 1.0 contre 1.0 ; ex4 rang 61 ; ex6 C1 0.048660, C5 0.047627, C2 0.032522
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme fusionne plusieurs classements en un seul, en ne regardant que les rangs de chaque document. Les cas ajoutent une règle de priorité avant la fusion (cas 3), un poids facultatif par classement, et un contrôle de l'indépendance des moteurs par la corrélation de Spearman (cas 4).

```text
ALGORITHME RRF
ENTRÉES : classements R₁ … Rₘ (listes ordonnées de documents), k_RRF (souvent 60), poids w₁ … wₘ (facultatifs, 1 par défaut)
SORTIE  : documents triés par score fusionné

  score ← dictionnaire vide
  POUR CHAQUE classement Rⱼ FAIRE
      Rⱼ ← Dédoublonner(Rⱼ)
      POUR rang DE 1 À longueur(Rⱼ) FAIRE
          d ← Rⱼ[rang]
          score[d] ← score[d] + wⱼ / (k_RRF + rang)
      FIN POUR
  FIN POUR
  RETOURNER les documents triés par score décroissant (égalités par nom)

ALGORITHME Spearman (deux classements des mêmes n éléments)
  S ← somme sur les éléments de (rang dans A − rang dans B)²
  RETOURNER 1 − 6 S / (n (n² − 1))
```

**Complexité.** O(L) où L est le nombre total d'entrées dans tous les classements, puis O(D log D) pour trier les D documents distincts. Aucun score d'origine n'est relu. La corrélation de Spearman coûte O(n) par paire de classements, et la recherche d'une valeur de bascule de k par balayage refait la fusion une fois par valeur essayée.

**Du squelette au code.** RRF est la fonction `rrf(classements, k_rrf, poids)`, qui dédoublonne chaque liste avec `dedoublonner(classement)` et renvoie la liste triée ; `ordre(fusion)` en extrait les documents, et `classement_depuis_scores(scores)` transforme les scores bruts d'un moteur en classement. La corrélation est `spearman(a, b)`. Les quatre cas sont `cas_1_support_banque`, `cas_2_unites_immo`, `cas_3_doublons_assur` (avec la liste `regle`) et `cas_4_alertes_crypto`.
