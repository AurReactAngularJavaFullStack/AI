# 22 — Espérance : démonstrations

> Fiche : [22 — Espérance](<../../Images/06-Decision/22_esperance.md>) · Image : `22_esperance.jpg` · Leçon : [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
\mathbb{E}[X] = \sum_{x} x \times P(X = x)
$$

L'espérance est la moyenne des valeurs possibles, chacune pondérée par sa probabilité. C'est ce qu'on obtient en moyenne sur un grand nombre de répétitions. Elle ne décrit pas un cas unique : aucune exécution ne coûte forcément 𝔼[X].

## Les symboles, un par un

$$
X
$$

Une quantité aléatoire : le coût d'un ticket, une indemnité, un nombre d'essais, une marge ; un réel dont la valeur dépend du hasard ; dans le programme, une « loi », liste de couples (probabilité, valeur).

$$
x
$$

Une valeur possible de X, dans l'unité de X (USD, AED, essais) ; le second élément de chaque couple de la loi.

$$
P(X = x)
$$

La probabilité que X prenne la valeur x ; un nombre de [0 ; 1], et ces probabilités somment à 1 ; le premier élément de chaque couple ; `esperance` lève `ValueError` si une probabilité est négative ou si la somme n'est pas 1.

$$
\mathbb{E}[X], \; \mu
$$

L'espérance, notée aussi μ : même unité que X, toujours comprise entre la plus petite et la plus grande valeur possible ; la valeur renvoyée par `esperance(loi)`.

$$
\operatorname{Var}(X), \; \sigma
$$

La variance, moyenne des carrés des écarts à μ, en unité de X au carré, toujours ≥ 0 ; σ = √Var(X), l'écart-type, dans l'unité de X ; la valeur renvoyée par `variance(loi)` et sa racine `math.sqrt(...)`.

$$
\mathbb{1}_A
$$

L'indicatrice de l'événement A : elle vaut 1 si A se produit, 0 sinon ; dans le texte on l'écrit 𝟙(A) ; dans le programme, un test booléen compté comme 0 ou 1.

$$
N, \; p, \; r
$$

N est le nombre d'essais jusqu'au premier succès (entier ≥ 1), p la probabilité de succès de chaque essai (dans ]0 ; 1]) et r le nombre maximal d'essais autorisés ; les arguments `p` et `r` de `essais_moyens(p, r)`.

## Le mécanisme, avant les preuves

La formule reçoit une liste de valeurs possibles et la probabilité de chacune. La première opération multiplie chaque valeur par sa probabilité : une valeur rare mais grande peut peser autant qu'une valeur fréquente et petite, car seul le produit compte. La seconde opération additionne ces produits : le résultat est le centre de gravité des valeurs, chacune chargée d'une masse égale à sa probabilité. Comme les poids sont positifs et somment à 1, ce centre reste entre la plus petite et la plus grande valeur, mais il n'a aucune raison d'être lui-même une valeur possible (6,8 dans l'exemple simple, où aucune exécution ne coûte 6,8). On pondère par les probabilités plutôt que de faire la moyenne simple des valeurs, parce que les valeurs ne sont pas également probables : la moyenne simple de l'exemple vaut 7,75, pas 6,8. L'espérance prédit un total : sur un grand nombre de répétitions indépendantes, la moyenne observée se rapproche de 𝔼[X] (loi des grands nombres), donc 50 000 tickets coûtent environ 50 000 × 𝔼[C]. L'espérance est linéaire : l'espérance d'une somme est la somme des espérances, même quand les termes dépendent les uns des autres (démonstration 1), ce qui permet d'additionner le coût moyen de chaque étape d'un agent. Elle ne commute pas avec les fonctions non linéaires : 𝔼[X²] n'est pas 𝔼[X]², et 𝔼[max(0, Y)] n'est pas max(0, 𝔼[Y]) (cas 2). Enfin, déplacer une probabilité δ d'une valeur x₁ vers une valeur x₂ change l'espérance d'exactement δ(x₂ − x₁) : c'est la règle de sensibilité qui dit où agir (démonstration 5). Pour un développeur Java, c'est un `stream().mapToDouble(v -> v.proba() * v.valeur()).sum()` : une réduction par somme, sans état caché.

**Petit film chiffré** (exemple simple : valeurs 2, 5, 9 et 15 de probabilités 0,2 ; 0,5 ; 0,1 ; 0,2).

| Valeur x | Probabilité | x × P | Somme cumulée |
|---|---|---|---|
| 2 | 0,2 | 0,4 | 0,4 |
| 5 | 0,5 | 2,5 | 2,9 |
| 9 | 0,1 | 0,9 | 3,8 |
| 15 | 0,2 | 3,0 | 6,8 |

La valeur 15, qui n'arrive qu'une fois sur cinq, apporte 3,0 des 6,8 : près de la moitié de l'espérance.

## Démonstration 1 — La linéarité, même pour des variables dépendantes

**Ce qu'on démontre.** Pour deux variables X et Y définies sur les mêmes issues ω, de probabilités P(ω), et deux nombres a et b :

$$
\mathbb{E}[aX + bY] = \sum_\omega \big(a X(\omega) + b Y(\omega)\big) P(\omega) = a \sum_\omega X(\omega) P(\omega) + b \sum_\omega Y(\omega) P(\omega) = a\,\mathbb{E}[X] + b\,\mathbb{E}[Y]
$$

Aucune hypothèse d'indépendance n'est nécessaire.

**L'idée.** L'espérance est une somme pondérée sur les issues ; une somme se distribue sur une addition et laisse sortir les constantes. Le lien entre X et Y ne joue aucun rôle, parce que l'on additionne issue par issue.

**La preuve, pas à pas.**

**Étape 1.** On écrit l'espérance de aX + bY comme une somme sur les issues, par définition : chaque issue ω apporte (aX(ω) + bY(ω)) P(ω).

**Étape 2.** On distribue P(ω) sur la parenthèse, parce que la multiplication se distribue sur l'addition, puis on coupe la somme en deux sommes.

**Étape 3.** On sort a de la première somme et b de la seconde, parce que ce sont des constantes ; il reste a 𝔼[X] + b 𝔼[Y]. Nulle part on n'a eu besoin de savoir comment X et Y varient ensemble. ∎

**Vérification chiffrée.** Le programme tire 1 000 nombres X au hasard (graine fixée) et pose Y = X², qui dépend entièrement de X : la moyenne de 2X + 3Y vaut 1,982678, exactement 2 fois la moyenne de X plus 3 fois celle de Y. Deux dés : 𝔼[X₁ + X₂] = 3,5 + 3,5 = 7. **Contre-exemple : la linéarité ne vaut que pour les fonctions linéaires.** Pour un dé, 𝔼[X²] = 91/6 ≈ 15,1667, alors que 𝔼[X]² = 3,5² = 12,25 ; et au cas 2, appliquer la franchise à l'espérance du dommage au lieu de l'appliquer issue par issue donne une erreur de 36 AED par sinistre.

**Ce que la preuve révèle du mécanisme.** L'espérance travaille issue par issue, puis additionne : c'est pourquoi elle traverse les sommes sans condition. Pour les produits ou les fonctions non linéaires, il faut connaître la loi commune (démonstration 6).

**Conséquence pour un agent.** Le coût moyen d'un agent est la somme des coûts moyens de ses étapes, même si elles s'influencent (une relance n'arrive qu'après un échec). On peut donc budgéter étape par étape, mais jamais calculer un coût non linéaire (franchise, plafond, seuil) sur la moyenne.

## Démonstration 2 — L'espérance d'une indicatrice est une probabilité

**Ce qu'on démontre.** Pour tout événement A, et pour n événements A₁, …, Aₙ :

$$
\mathbb{E}[\mathbb{1}_A] = 1 \times P(A) + 0 \times P(\text{non } A) = P(A), \qquad \mathbb{E}\Big[ \sum_{i=1}^{n} \mathbb{1}_{A_i} \Big] = \sum_{i=1}^{n} P(A_i)
$$

**L'idée.** Une indicatrice ne prend que les valeurs 0 et 1 : sa moyenne est la fréquence de 1, c'est-à-dire la probabilité de A. Compter des succès, c'est additionner des indicatrices, et la linéarité fait le reste.

**La preuve, pas à pas.**

**Étape 1.** 𝟙(A) vaut 1 avec la probabilité P(A) et 0 avec la probabilité 1 − P(A) ; la définition de l'espérance donne 1 × P(A) + 0 × (1 − P(A)) = P(A).

**Étape 2.** Le nombre de succès parmi n tentatives est la somme des indicatrices 𝟙(Aᵢ), parce que chaque succès ajoute 1 et chaque échec 0.

**Étape 3.** Par la démonstration 1, l'espérance de la somme est la somme des espérances, soit Σ P(Aᵢ), sans hypothèse d'indépendance. Si toutes les probabilités valent p, on obtient np. ∎

**Vérification chiffrée.** L'agent d'achats de la leçon a trois étapes de fiabilités 0,99 ; 0,98 ; 0,97. Nombre moyen d'étapes réussies : 0,99 + 0,98 + 0,97 = 2,94 sur 3, quelle que soit la dépendance. Probabilité que les trois réussissent, sous indépendance : 0,99 × 0,98 × 0,97 = 0,9702 × 0,97 = 0,941094. **Contre-exemple d'une lecture fausse :** conclure de 2,94 sur 3 que « l'agent réussit 98 % du temps » confond le taux de réussite moyen par étape (2,94/3 = 0,98) avec la réussite de bout en bout, 0,941094 sous indépendance.

**Ce que la preuve révèle du mécanisme.** L'espérance d'un compte n'a besoin que des probabilités individuelles ; la probabilité que tout réussisse a besoin, elle, de la façon dont les échecs se combinent. Ce sont deux questions différentes, et seule la première est toujours additive.

**Conséquence pour un agent.** Pour prévoir une charge (nombre moyen d'escalades, de relances, de départs), on additionne les probabilités. Pour promettre une fiabilité de bout en bout, on utilise le produit de la leçon et ses bornes, et on le mesure.

## Démonstration 3 — La variance

**Ce qu'on démontre.** La variance mesure l'écart moyen au carré autour de l'espérance μ = 𝔼[X], et elle se calcule par la formule « moyenne des carrés moins carré de la moyenne » :

$$
\operatorname{Var}(X) = \mathbb{E}\big[(X - \mu)^2\big] = \mathbb{E}[X^2] - 2\mu\,\mathbb{E}[X] + \mu^2 = \mathbb{E}[X^2] - \mu^2
$$

**L'idée.** On développe le carré, puis on applique la linéarité ; deux termes en μ² se compensent en partie. La variance est la moyenne d'un carré, donc elle n'est jamais négative.

**La preuve, pas à pas.**

**Étape 1.** On développe (X − μ)² = X² − 2μX + μ², par l'identité remarquable.

**Étape 2.** On prend l'espérance terme à terme (démonstration 1), en sortant les constantes 2μ et μ² : 𝔼[X²] − 2μ 𝔼[X] + μ².

**Étape 3.** On remplace 𝔼[X] par μ : 𝔼[X²] − 2μ² + μ² = 𝔼[X²] − μ². Comme (X − μ)² ≥ 0 pour chaque issue, sa moyenne est ≥ 0, donc 𝔼[X²] ≥ μ². ∎

**Vérification chiffrée.** Exemple simple : 𝔼[X²] = 4 × 0,2 + 25 × 0,5 + 81 × 0,1 + 225 × 0,2 = 0,8 + 12,5 + 8,1 + 45 = 66,4 ; μ² = 6,8² = 46,24 ; Var = 66,4 − 46,24 = 20,16 et σ ≈ 4,49. Ticket du cas 1 : Var = 0,450695 − 0,1735² = 0,42059. **Contre-exemple : la moyenne seule ne suffit pas.** Deux agents de même coût moyen, 0,1735 USD : l'un coûte toujours 0,1735 USD (variance 0), l'autre presque rien sauf de temps en temps 3 USD (variance 0,42059, écart-type 0,64853 USD).

**Ce que la preuve révèle du mécanisme.** La variance est dominée par les grandes valeurs, élevées au carré : dans le ticket, la branche à 3 USD apporte 0,45 des 0,450695 de 𝔼[C²]. Multiplier X par a multiplie la variance par a² (exercice 5) ; ajouter une constante ne la change pas.

**Conséquence pour un agent.** On publie toujours l'écart-type avec la moyenne, et l'on dimensionne les budgets et les réserves sur μ plus quelques σ (cas 3), jamais sur μ seul.

## Démonstration 4 — Le nombre moyen d'essais jusqu'au premier succès

**Ce qu'on démontre.** Chaque essai réussit avec la probabilité p, indépendamment des autres. Le nombre N d'essais jusqu'au premier succès vérifie P(N > k) = (1 − p)ᵏ et :

$$
\mathbb{E}[N] = \sum_{k=0}^{\infty} P(N > k) = \sum_{k=0}^{\infty} (1 - p)^k = \frac{1}{p}
$$

Avec au plus r essais, la somme s'arrête à k = r − 1 et vaut (1 − (1 − p)ʳ)/p.

**L'idée.** N > k exactement quand les k premiers essais échouent. Et N est la somme des indicatrices « on fait encore un essai après le k-ième », dont l'espérance est la probabilité de cet événement (démonstration 2).

**La preuve, pas à pas.**

**Étape 1.** N > k si et seulement si les k premiers essais échouent ; par indépendance, P(N > k) = (1 − p) × … × (1 − p) = (1 − p)ᵏ.

**Étape 2.** On écrit N comme un compte : N = Σₖ≥₀ 𝟙(N > k), parce que les termes valent 1 pour k = 0, 1, …, N − 1 et 0 ensuite, soit N termes égaux à 1.

**Étape 3.** Par les démonstrations 1 et 2, 𝔼[N] = Σₖ≥₀ P(N > k) = Σ (1 − p)ᵏ, une série géométrique de raison 1 − p < 1, qui vaut 1/(1 − (1 − p)) = 1/p.

**Étape 4.** Avec au plus r essais, N ≤ r et 𝟙(N > k) = 0 dès k ≥ r ; la somme géométrique finie de k = 0 à r − 1 vaut (1 − (1 − p)ʳ)/(1 − (1 − p)). ∎

**Vérification chiffrée.** p = 0,8 : 𝔼[N] = 1/0,8 = 1,25 ; le programme simule 50 000 séries (graine fixée) et trouve 1,2559 ; la somme des queues calculée vaut 1,2500. Avec au plus 3 essais : (1 − 0,2³)/0,8 = 0,992/0,8 = 1,24 essai en moyenne, et la probabilité de finir par un succès vaut 0,992. **Contre-exemple quand les essais ne sont pas indépendants :** si une erreur se répète à l'identique (même entrée, même prompt), un premier échec entraîne les deux suivants ; la probabilité de succès en 3 essais reste 0,8 au lieu de 0,992, et l'agent fait en moyenne 1 × 0,8 + 3 × 0,2 = 1,4 essai pour rien de plus.

**Ce que la preuve révèle du mécanisme.** Le nombre moyen d'essais ne dépend que de p : 1/p. Une relance n'est utile que si l'essai suivant a une chance réelle de réussir autrement, c'est-à-dire si l'on change quelque chose (message d'erreur ajouté au prompt, autre outil).

**Conséquence pour un agent.** Le coût moyen d'une étape avec relances vaut coût d'un essai × (1 − (1 − p)ʳ)/p, et la fiabilité de l'étape devient 1 − (1 − p)ʳ, à condition que les essais soient indépendants ; on borne r et l'on enrichit chaque relance.

## Démonstration 5 — Sensibilité : déplacer de la probabilité d'une valeur à une autre

**Ce qu'on démontre.** Si l'on déplace une masse de probabilité δ de la valeur x₁ vers la valeur x₂, les autres probabilités restant fixes, l'espérance change d'exactement :

$$
\Delta \mathbb{E}[X] = \delta \, (x_2 - x_1)
$$

Et, pour toute loi, la plus petite valeur ≤ 𝔼[X] ≤ la plus grande valeur.

**L'idée.** Seuls deux termes de la somme changent : x₁ perd δ, x₂ gagne δ. Le gain net est l'écart des deux valeurs, multiplié par la masse déplacée.

**La preuve, pas à pas.**

**Étape 1.** Avant : … + x₁ P₁ + x₂ P₂ + … ; après : … + x₁ (P₁ − δ) + x₂ (P₂ + δ) + …, les autres termes étant identiques.

**Étape 2.** On soustrait : −δ x₁ + δ x₂ = δ(x₂ − x₁).

**Étape 3.** Pour les bornes : chaque x vérifie min ≤ x ≤ max ; on multiplie par P(X = x) ≥ 0 et on additionne, en utilisant Σ P = 1 : min ≤ 𝔼[X] ≤ max. ∎

**Vérification chiffrée.** Ticket du cas 1 : déplacer 2 points de probabilité de l'escalade (3 USD) vers la résolution directe (0,02 USD) change l'espérance de 0,02 × (0,02 − 3) = −0,0596, de 0,1735 à 0,1139 USD. Une hausse de 1 % du taux d'escalade (5 % → 5,05 %, pris sur la résolution directe) ajoute 0,0005 × 2,98 = 0,00149 USD, soit +0,86 % du coût moyen. **Contre-exemple quand la masse n'est retirée nulle part :** ajouter 2 points à l'escalade sans les retirer ailleurs donnerait 0,1735 + 0,06 = 0,2335 avec des probabilités de somme 1,02 ; ce n'est plus une loi, et `esperance` lève `ValueError`.

**Ce que la preuve révèle du mécanisme.** La sensibilité de l'espérance à une probabilité est l'écart de valeur entre les issues concernées : un point de probabilité vaut 2,98 USD entre résolution et escalade, et 0,03 USD entre résolution et relance. C'est là qu'il faut agir.

**Conséquence pour un agent.** Pour baisser un coût moyen, on classe les leviers par δ × écart de valeur : réduire une branche rare mais chère (l'escalade) bat presque toujours l'optimisation de la branche fréquente et bon marché (cas 1).

## Démonstration 6 — Espérance d'un produit, indépendance et fiabilité composée

**Ce qu'on démontre.** Si X et Y sont indépendantes, alors l'espérance du produit est le produit des espérances ; appliqué à des indicatrices indépendantes, cela redonne la fiabilité composée de la leçon :

$$
\mathbb{E}[XY] = \mathbb{E}[X]\,\mathbb{E}[Y], \qquad P(A_1 \cap \dots \cap A_n) = \mathbb{E}\Big[ \prod_{i} \mathbb{1}_{A_i} \Big] = \prod_{i} p_i
$$

Sans indépendance, l'égalité est fausse en général.

**L'idée.** L'indépendance dit que la loi commune est le produit des lois : P(X = x, Y = y) = P(X = x) P(Y = y). La double somme se factorise alors en produit de deux sommes. Un produit d'indicatrices vaut 1 exactement quand tous les événements se produisent.

**La preuve, pas à pas.**

**Étape 1.** On écrit 𝔼[XY] comme une double somme sur les couples de valeurs, par définition : Σₓ Σᵧ x y P(X = x, Y = y).

**Étape 2.** On remplace la probabilité commune par le produit P(X = x) P(Y = y), ce qui est la définition de l'indépendance.

**Étape 3.** On factorise : Σₓ x P(X = x) × Σᵧ y P(Y = y) = 𝔼[X] 𝔼[Y].

**Étape 4.** Le produit des indicatrices 𝟙(Aᵢ) vaut 1 si toutes les étapes réussissent et 0 sinon : c'est l'indicatrice de l'intersection, d'espérance P(A₁ ∩ … ∩ Aₙ) (démonstration 2) ; avec l'indépendance mutuelle et l'étape 3 répétée, on obtient ∏ pᵢ. ∎

**Vérification chiffrée.** Deux dés indépendants : 𝔼[XY] = 12,25 = 3,5 × 3,5. Le même dé deux fois (dépendance totale) : 𝔼[X × X] = 91/6 ≈ 15,1667, soit 2,9167 de plus, la variance du dé. Deux étapes fiables à 0,95 : indépendantes, elles réussissent ensemble avec la probabilité 0,9025 ; avec une cause commune (elles échouent toujours ensemble), avec 0,95. **Contre-exemple :** dans ce dernier cas, 𝔼[𝟙₁ 𝟙₂] = 0,95 ≠ 𝔼[𝟙₁] 𝔼[𝟙₂] = 0,9025 ; la valeur reste pourtant entre les bornes de la leçon, 1 − 2 × 0,05 = 0,90 et 0,95.

**Ce que la preuve révèle du mécanisme.** La linéarité n'a besoin de rien, le produit a besoin de l'indépendance. Quand la valeur et la probabilité d'un événement sont liées (les salariés anciens, qui coûtent le plus cher, partent le moins), multiplier deux moyennes donne un résultat faux (cas 3).

**Conséquence pour un agent.** On ne multiplie deux moyennes que si l'on a une raison de croire à l'indépendance ; sinon on calcule groupe par groupe, ou issue par issue, puis on additionne. La fiabilité composée se vérifie par la mesure de bout en bout.

## Exemple simple, à la main

Issues 2, 5, 9 et 15, de probabilités 0,2 ; 0,5 ; 0,1 ; 0,2.

**Étape 1.** Produits : 2 × 0,2 = 0,4 ; 5 × 0,5 = 2,5 ; 9 × 0,1 = 0,9 ; 15 × 0,2 = 3.

**Étape 2.** Somme : 0,4 + 2,5 + 0,9 + 3 = 6,8.

$$
\mathbb{E}[X] = 2 \times 0{,}2 + 5 \times 0{,}5 + 9 \times 0{,}1 + 15 \times 0{,}2 = 0{,}4 + 2{,}5 + 0{,}9 + 3 = 6{,}8
$$

**Étape 3.** Avec des probabilités égales (0,25 chacune), la moyenne serait (2 + 5 + 9 + 15)/4 = 31/4 = 7,75 : les probabilités déplacent l'espérance.

**Étape 4.** Dispersion (démonstration 3) : 𝔼[X²] = 0,8 + 12,5 + 8,1 + 45 = 66,4 ; Var = 66,4 − 6,8² = 66,4 − 46,24 = 20,16 ; σ = √20,16 ≈ 4,49.

| Valeur x | P | x × P | x² × P |
|---|---|---|---|
| 2 | 0,2 | 0,4 | 0,8 |
| 5 | 0,5 | 2,5 | 12,5 |
| 9 | 0,1 | 0,9 | 8,1 |
| 15 | 0,2 | 3,0 | 45,0 |
| total | 1 | 6,8 | 66,4 |

Aucune exécution ne coûte 6,8 : c'est une moyenne, et une exécution sur cinq coûte 15.

## Cas d'usage complexes, démontrés

Les probabilités, coûts, salaires, prix et volumes des quatre cas sont illustratifs, sauf les règles de fin de service, la TVA et les frais DLD, qui sont celles autorisées par le guide du cours. Les montants en USD se convertissent au taux fixe de 3,6725 AED par USD.

### Cas 1 — Banque de détail [BANQUE] : le coût moyen d'un ticket de support, et la branche rare qui pèse tout

**Contexte.** Une banque de détail de Dubaï fait traiter par un agent les demandes de ses clients sur l'application (carte bloquée, frais, virement en attente), environ 50 000 tickets par mois. Chaque ticket finit de trois façons : résolution directe, une relance, ou escalade à un conseiller. L'équipe dispose d'un budget pour un seul projet d'amélioration et hésite entre deux : diviser par deux le coût en tokens de la résolution directe (projet A), ou faire baisser l'escalade de 5 % à 3 % (projet B).

**Données.**

- Résolution directe : 80 %, coût 0,02 USD.
- Une relance : 15 %, coût 0,05 USD.
- Escalade à un conseiller : 5 %, coût 3 USD.
- Projet A : résolution directe à 0,01 USD. Projet B : escalade à 3 %, les 2 points passant en résolution directe.
- Volume : 50 000 tickets par mois.

**Calcul pas à pas.**

**Étape 1.** Coût moyen (arrondi à 4 décimales) :

$$
\mathbb{E}[C] = 0{,}8 \times 0{,}02 + 0{,}15 \times 0{,}05 + 0{,}05 \times 3 = 0{,}016 + 0{,}0075 + 0{,}15 = 0{,}1735 \text{ USD}
$$

soit 0,6372 AED par ticket.

**Étape 2.** Coût mensuel : 50 000 × 0,1735 = 8 675 USD, soit 31 858,94 AED. L'escalade, qui ne concerne que 5 % des tickets, représente 0,15/0,1735 = 86,5 % de ce coût.

**Étape 3.** Dispersion : 𝔼[C²] = 0,8 × 0,0004 + 0,15 × 0,0025 + 0,05 × 9 = 0,00032 + 0,000375 + 0,45 = 0,450695 ; Var = 0,450695 − 0,1735² = 0,42059 ; σ ≈ 0,64853 USD, soit 3,74 fois la moyenne.

**Étape 4.** Gain des projets (démonstration 5) : A fait passer l'espérance à 0,8 × 0,01 + 0,0075 + 0,15 = 0,1655, soit 0,008 × 50 000 = 400 USD par mois ; B la fait passer à 0,1139, soit 0,0596 × 50 000 = 2 980 USD par mois.

**Décision de l'agent.** Le seuil est le gain mensuel : B rapporte 2 980 USD contre 400 pour A, l'équipe lance le projet B (meilleure détection des demandes que l'agent sait résoudre, meilleures réponses aux cas fréquents d'escalade).

**Contre-calcul.** La moyenne simple des trois coûts, (0,02 + 0,05 + 3)/3 = 1,0233 USD, donnerait 51 167 USD par mois, 5,9 fois trop. Le « cas typique » à 0,02 USD donnerait 1 000 USD par mois, 8,7 fois trop peu : un budget faux dans les deux sens.

**Sensibilité.** B gagne 0,02 × (c − 0,02) par ticket, où c est le coût d'une escalade, et A gagne 0,008 : B reste meilleur tant qu'une escalade coûte plus de 0,02 + 0,008/0,02 = 0,42 USD. Une hausse de 1 % du taux d'escalade coûte +0,86 % sur le coût moyen (démonstration 5).

**En production.** Indicateur : le taux d'escalade quotidien ; alerte au-dessus de 6 %, qui porterait le coût moyen à 0,2033 USD (+17 %). On suit aussi le coût mensuel réel contre 50 000 × 𝔼[C]. Contraintes : le traitement des réclamations des clients suit les règles de protection des consommateurs de la CBUAE, et les données des clients la loi de protection des données applicable (la PDPL ne s'applique pas en zone DIFC ou ADGM) : à confirmer avec le texte en vigueur.

### Cas 2 — Assureur auto et santé [ASSUR] : choisir la franchise d'une offre auto

**Contexte.** Un assureur auto de Dubaï prépare une nouvelle offre. Son agent de tarification calcule la prime pure, l'indemnité moyenne par sinistre, pour plusieurs franchises, et doit proposer la plus petite franchise qui tient la cible de 4 500 AED par sinistre. Volume illustratif : 2 400 sinistres par an.

**Données.**

- Montant du dommage D : 1 500 AED (probabilité 0,2) ; 4 000 (0,5) ; 9 000 (0,25) ; 40 000, perte totale (0,05).
- Vétusté : 20 % sur les pièces, qui font 60 % du dommage, soit 12 % du dommage ; l'indemnité vaut max(0 ; 0,88 × D − F).
- Franchises étudiées : F = 500, 1 000 ou 1 500 AED.
- Cible : prime pure ≤ 4 500 AED par sinistre.
- Volume : 2 400 sinistres par an.

**Calcul pas à pas.**

**Étape 1.** Dommage moyen : 𝔼[D] = 0,2 × 1 500 + 0,5 × 4 000 + 0,25 × 9 000 + 0,05 × 40 000 = 300 + 2 000 + 2 250 + 2 000 = 6 550 AED.

**Étape 2.** F = 500 : indemnités 0,88 × 1 500 − 500 = 820 ; 3 020 ; 7 420 ; 34 700. Aucun plancher n'est atteint, donc la linéarité s'applique : 𝔼 = 0,88 × 6 550 − 500 = 5 764 − 500 = 5 264 AED. F = 1 000 : 5 764 − 1 000 = 4 764 AED, encore au-dessus de la cible.

**Étape 3.** F = 1 500 : le petit sinistre donne 0,88 × 1 500 − 1 500 = 1 320 − 1 500 < 0, donc 0 ; les autres donnent 2 020 ; 6 420 ; 33 700.

$$
\mathbb{E}[\text{indemnité}] = 0{,}2 \times 0 + 0{,}5 \times 2\,020 + 0{,}25 \times 6\,420 + 0{,}05 \times 33\,700 = 0 + 1\,010 + 1\,605 + 1\,685 = 4\,300
$$

**Étape 4.** Dispersion à F = 1 500 : σ ≈ 7 116,1 AED, plus de une fois et demie la moyenne, à cause de la perte totale de 5 %.

**Décision de l'agent.** La plus petite franchise de la grille qui tient la cible est F = 1 500 AED (4 300 ≤ 4 500) ; l'agent la propose, avec l'écart-type, à l'actuaire qui valide.

**Contre-calcul.** Le raccourci « on applique la franchise à la moyenne », 0,88 × 6 550 − 1 500 = 4 264 AED, sous-estime la prime pure de 36 AED par sinistre (0,2 × 180, la part de franchise que le petit sinistre ne peut pas absorber), soit 36 × 2 400 = 86 400 AED par an de réserve manquante. C'est la limite de la linéarité : 𝔼[max(0 ; Y)] n'est pas max(0 ; 𝔼[Y]).

**Sensibilité.** Valeur de bascule de la franchise : tant que le plancher n'agit pas (F ≤ 1 320), 𝔼 = 5 764 − F, qui vaut 4 500 pour F = 1 264 AED. Si la probabilité de perte totale monte de 10 % (5 % → 5,5 %, prise sur la classe à 4 000), l'espérance gagne 0,005 × (33 700 − 2 020) = 158,4 et passe à 4 458,4 AED : la franchise 1 500 tient encore.

**En production.** Indicateur : l'indemnité moyenne réelle par sinistre, mois par mois ; alerte au-dessus de 4 400 AED, avant la cible. Contrainte : l'assurance est supervisée par la CBUAE ; les règles de vétusté et de franchise sont celles du contrat (à confirmer avec le texte en vigueur), et l'agent ne fait que calculer : l'actuaire décide.

### Cas 3 — Cabinet RH multi-émirats [RH] : provisionner les indemnités de fin de service de l'année

**Contexte.** Un cabinet RH présent dans plusieurs émirats gère la paie d'un client de 200 salariés du secteur privé, hors ressortissants émiriens (qui relèvent de la GPSSA) et hors DIFC (régime DEWS). Son agent doit proposer la provision de l'année pour les indemnités de fin de service des salariés qui partiront. Les départs sont supposés indépendants.

**Données.**

- Salaire de base : 9 000 AED par mois pour tous (simplification), soit 9 000/30 = 300 AED par jour.
- Règle : au moins 1 an de service ; 21 jours de salaire de base par an pour les 5 premières années, 30 jours au-delà ; plafond de 24 mois de salaire de base ; pas de réduction en cas de démission.
- Groupes : 60 salariés à 2 ans d'ancienneté (probabilité de départ dans l'année 0,2) ; 100 à 6 ans (0,1) ; 40 à 12 ans (0,05).
- Budget de provision proposé par la direction : 800 000 AED.

**Calcul pas à pas.**

**Étape 1.** Indemnité par salarié : 2 ans, 21 × 2 × 300 = 12 600 AED ; 6 ans, (21 × 5 + 30 × 1) × 300 = 135 × 300 = 40 500 AED ; 12 ans, (105 + 30 × 7) × 300 = 315 × 300 = 94 500 AED. Le plafond, 24 × 9 000 = 216 000 AED, n'est atteint par personne.

**Étape 2.** Provision attendue, par linéarité (démonstrations 1 et 2) :

$$
60 \times 0{,}2 \times 12\,600 + 100 \times 0{,}1 \times 40\,500 + 40 \times 0{,}05 \times 94\,500 = 151\,200 + 405\,000 + 189\,000 = 745\,200 \text{ AED}
$$

pour 12 + 10 + 2 = 24 départs attendus.

**Étape 3.** Dispersion, départs indépendants : Var = Σ n p (1 − p) m², d'où σ ≈ 182 356 AED ; une provision à deux écarts-types vaut 745 200 + 2 × 182 356 ≈ 1 109 913 AED.

**Décision de l'agent.** L'agent inscrit 745 200 AED en provision attendue, signale que le budget de 800 000 AED ne couvre que 0,3 écart-type au-dessus (54 800/182 356), et propose une réserve complémentaire jusqu'à 1 109 913 AED si le client veut couvrir une mauvaise année.

**Contre-calcul.** Le raccourci « indemnité moyenne × nombre de départs » prend l'indemnité moyenne de l'effectif, (60 × 12 600 + 100 × 40 500 + 40 × 94 500)/200 = 8 586 000/200 = 42 930 AED, et la multiplie par 24 : 1 030 320 AED, soit 285 120 AED de trop. L'erreur vient de la démonstration 6 : le montant et la probabilité de départ sont liés (les anciens, chers, partent peu), donc la moyenne du produit n'est pas le produit des moyennes.

**Sensibilité.** Le budget de 800 000 AED est tenu tant que la probabilité de départ du groupe à 6 ans reste sous (800 000 − 151 200 − 189 000)/(100 × 40 500) = 459 800/4 050 000 = 0,11353, soit à peine 13,5 % au-dessus de l'hypothèse 0,1. Une démission coûte autant qu'un licenciement, puisque la règle ne prévoit pas de réduction.

**En production.** Indicateur : les départs réels cumulés, comparés aux 2 départs attendus par mois (24/12) et pondérés par leur indemnité ; alerte si le montant cumulé dépasse de 20 % la trajectoire attendue. Contraintes : les fins de contrat sont déclarées auprès du MOHRE et les soldes versés par le WPS ; la règle de calcul est celle du décret-loi fédéral 33/2021 pour le secteur privé, à appliquer au salaire de base et au prorata des années incomplètes.

### Cas 4 — Promoteur immobilier [IMMO] : offrir les frais DLD de 4 % pour accélérer les ventes

**Contexte.** Un promoteur de Dubaï commercialise des appartements neufs à 1 200 000 AED ; la première vente d'un bien résidentiel neuf est au taux zéro de TVA. Son équipe propose une promotion « frais DLD offerts » : le promoteur paie à la place de l'acheteur les frais de transfert de 4 %. Un agent d'analyse doit dire si la promotion augmente la marge attendue sur les 2 000 prospects qualifiés du mois (volume illustratif).

**Données.**

- Prix : 1 200 000 AED ; marge du promoteur : 15 %, soit 180 000 AED par vente (illustratif).
- Frais de transfert DLD : 4 % du prix, soit 48 000 AED, payés par le promoteur pendant la promotion.
- Conversion d'un prospect qualifié : 8 % sans promotion, 11 % avec (estimation d'un test, illustratif).
- Volume : 2 000 prospects qualifiés par mois.

**Calcul pas à pas.**

**Étape 1.** Marge par vente avec promotion : 180 000 − 48 000 = 132 000 AED.

**Étape 2.** Marge attendue par prospect (démonstration 2, l'indicatrice « le prospect achète ») : sans promotion, 0,08 × 180 000 = 14 400 AED ; avec, 0,11 × 132 000 = 14 520 AED.

**Étape 3.** Sur le mois : (14 520 − 14 400) × 2 000 = 240 000 AED de plus ; les ventes passent de 160 à 220, et la marge totale de 160 × 180 000 = 28 800 000 à 220 × 132 000 = 29 040 000 AED.

**Étape 4.** Valeur de bascule de la conversion avec promotion : 14 400/132 000 = 0,10909.

**Décision de l'agent.** La promotion rapporte 240 000 AED de plus par mois si la conversion atteint vraiment 11 %, au-dessus de la bascule 10,91 % : l'agent recommande de la lancer pour un mois de test, avec un arrêt automatique si la conversion mesurée passe sous la bascule.

**Contre-calcul.** Le raisonnement naïf ne compte que les 60 ventes supplémentaires : 60 × (180 000 − 48 000) = 7 920 000 AED, 33 fois le vrai gain. Il oublie que la promotion est aussi payée aux 160 acheteurs qui auraient acheté de toute façon : 160 × 48 000 = 7 680 000 AED, et 7 920 000 − 7 680 000 = 240 000 AED.

**Sensibilité.** La décision est fragile : si la conversion avec promotion n'était que de 10,7 %, la marge attendue tomberait à 0,107 × 132 000 = 14 124 AED par prospect, et la promotion ferait perdre (14 124 − 14 400) × 2 000 = 552 000 AED par mois.

**En production.** Indicateur : la conversion hebdomadaire des prospects qualifiés pendant la promotion ; alerte et arrêt sous 10,91 %. Contraintes : les frais de transfert de 4 % sont enregistrés auprès du DLD ; la publicité de la promotion suit les règles de la RERA (à confirmer avec le texte en vigueur) ; l'agent analyse pour le promoteur, il n'oriente pas le choix des acheteurs.

## Entraînement sur feuille A4

**Exercice 1.** Un dé équilibré à six faces. Calculer 𝔼[X] et Var(X).

**Exercice 2.** Une étape coûte 0,01 USD et une autre 0,04 USD, chacune exécutée avec probabilité 0,9 et 0,5. Calculer le coût moyen total.

**Exercice 3.** Une tâche réussit avec p = 0,25 par essai. Combien d'essais en moyenne jusqu'au succès ?

**Exercice 4.** Dans le cas 1, le taux d'escalade passe de 5 % à 3 % (les 2 points vont en résolution directe). Nouveau coût moyen ?

**Exercice 5.** Démontrer que Var(aX) = a² Var(X).

**Exercice 6 (modifier une donnée).** Dans le cas 4, le test montre une conversion de 12 % avec la promotion. Recalculer la marge attendue par prospect et l'écart mensuel.

**Exercice 7 (trouver l'erreur).** Un collègue écrit : « 𝔼[C²] = 𝔼[C]² = 0,1735² = 0,030102, donc la variance du ticket est nulle et chaque ticket coûte 0,1735 USD. » Trouver l'erreur et la corriger.

**Exercice 8 (redémontrer de mémoire).** Redémontrer la formule des queues de la démonstration 4, puis calculer le nombre moyen d'essais d'une étape réussie à 60 % et relancée au plus 3 fois.

## Corrigé

**Exercice 1.** 𝔼[X] = (1 + 2 + 3 + 4 + 5 + 6)/6 = 21/6 = 3,5. 𝔼[X²] = (1 + 4 + 9 + 16 + 25 + 36)/6 = 91/6, donc Var = 91/6 − 12,25 ≈ 2,9167.

**Exercice 2.** Chaque étape a pour coût moyen sa probabilité d'exécution fois son coût (démonstration 2) ; par linéarité, 0,9 × 0,01 + 0,5 × 0,04 = 0,009 + 0,02 = 0,029 USD.

**Exercice 3.** Démonstration 4 : 1/0,25 = 4 essais.

**Exercice 4.** 0,82 × 0,02 + 0,15 × 0,05 + 0,03 × 3 = 0,0164 + 0,0075 + 0,09 = 0,1139 USD ; la démonstration 5 donne directement 0,1735 + 0,02 × (0,02 − 3) = 0,1139.

**Exercice 5.** 𝔼[aX] = aμ par linéarité, donc Var(aX) = 𝔼[(aX − aμ)²] = 𝔼[a²(X − μ)²] = a² 𝔼[(X − μ)²] = a² Var(X). Le programme le vérifie avec a = 3 sur le ticket.

**Exercice 6.** 0,12 × 132 000 = 15 840 AED par prospect, contre 14 400 sans promotion : écart (15 840 − 14 400) × 2 000 = 2 880 000 AED par mois ; la promotion est nettement rentable, puisque 12 % > 10,91 %.

**Exercice 7.** L'erreur : 𝔼[C²] n'est pas 𝔼[C]² (démonstration 1, contre-exemple : la linéarité ne vaut pas pour le carré). On calcule 𝔼[C²] issue par issue : 0,8 × 0,02² + 0,15 × 0,05² + 0,05 × 3² = 0,450695, d'où Var = 0,450695 − 0,030102 = 0,42059 et σ ≈ 0,64853 USD : les coûts sont très dispersés, et aucun ticket ne coûte 0,1735 USD.

**Exercice 8.** Preuve : N = Σₖ≥₀ 𝟙(N > k), donc 𝔼[N] = Σ P(N > k) ; avec des essais indépendants, P(N > k) = (1 − p)ᵏ, et au plus r essais arrêtent la somme à k = r − 1 : (1 − (1 − p)ʳ)/p. Application : (1 − 0,4³)/0,6 = (1 − 0,064)/0,6 = 0,936/0,6 = 1,56 essai.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`proche(x, y, tol)`** — Cette petite fonction est le contrôleur des poids et mesures qui tolère une poussière sur le plateau : elle reçoit deux nombres et une tolérance, un milliardième par défaut, mesure la valeur absolue de leur écart et renvoie vrai s'il ne dépasse pas cette tolérance, faux sinon. Elle ne porte aucune théorie, mais elle permet aux `assert` de `main` de comparer des flottants sans se laisser piéger par les arrondis, par exemple pour constater que l'espérance de la somme de deux dés vaut bien 7 ou que 6,8² vaut bien 46,24.

**`esperance(loi)`** — Cette fonction est le comptable qui fait la moyenne de toutes les issues possibles, chacune pesée par sa chance d'arriver : elle reçoit une loi sous la forme d'une liste de couples probabilité et valeur, refuse par une `ValueError` une probabilité négative ou des probabilités dont la somme s'écarte de 1, puis renvoie la somme des produits probabilité × valeur. Elle donne 6,8 pour l'exemple simple, 0,1735 USD pour le coût moyen d'un ticket du cas 1, et refuse une loi dont les probabilités somment à 1,02 ; toutes les autres fonctions de calcul passent par elle.

**`variance(loi)`** — On la voit en mesureuse de dispersion, qui dit à quel point les issues s'éloignent de leur moyenne : elle reçoit la même loi que `esperance`, calcule l'espérance des carrés des valeurs, puis lui retranche le carré de l'espérance, selon la formule Var(X) = E[X²] − E[X]² de la démonstration 3. Elle renvoie cette variance, 20,16 pour l'exemple simple, dont l'écart-type vaut 4,49, et 0,42059 pour le coût d'un ticket, un écart-type de 0,64853 USD, soit 3,74 fois la moyenne.

**`essais_moyens(p, r)`** — Cette fonction raconte un livreur qui sonne à une porte jusqu'à ce qu'on lui ouvre : elle reçoit la probabilité p qu'un essai réussisse et, facultativement, un nombre maximal r d'essais, refuse par une `ValueError` un p hors de ]0 ; 1], puis renvoie le nombre moyen d'essais, 1/p sans limite ou (1 − (1 − p)ʳ)/p quand on s'arrête au bout de r essais. Elle donne 1,25 pour p = 0,8, 1,24 avec au plus trois essais, 4 pour p = 0,25 et 1,56 pour p = 0,6 avec trois essais, la réponse de l'exercice 8.

**`indemnite_fin_service(base, annees)`** — Celle-ci est le préposé à la paie qui calcule ce que touche un salarié du secteur privé à son départ : elle reçoit le salaire de base mensuel et l'ancienneté en années, renvoie 0 sous un an, puis compte 21 jours par an pour les cinq premières années et 30 jours au-delà, au salaire journalier base/30, avec un plafond de 24 mois de salaire. Pour une base de 9 000 AED, elle renvoie 12 600 AED à deux ans, 40 500 à six ans, 94 500 à douze ans et le plafond de 216 000 à trente ans, et le cas 3 s'en sert pour chaque groupe de salariés.

**`demo_1_linearite()`** — Cette fonction met à l'épreuve la linéarité de l'espérance là où on la croirait en danger, entre deux variables liées : elle ne reçoit rien, fixe la graine du hasard à 22, tire mille nombres X uniformes et pose Y = X², qui dépend entièrement de X, puis compare la moyenne de 2X + 3Y à 2 fois la moyenne de X plus 3 fois celle de Y. Les deux valent 1,982678 ; elle vérifie aussi que la somme de deux dés a pour espérance 7, deux fois 3,5, imprime ces résultats et les renvoie.

**`demo_2_indicatrices()`** — On y suit une chaîne de trois étapes qui réussissent avec les probabilités 0,99, 0,98 et 0,97 : la fonction ne reçoit rien, additionne ces probabilités pour obtenir le nombre moyen d'étapes réussies, 2,94 sur 3, grâce à l'astuce des indicatrices qui n'exige aucune indépendance. Elle calcule ensuite la probabilité que les trois réussissent toutes, 0,941094, qui, elle, suppose l'indépendance, puisque c'est un produit ; elle imprime les deux nombres et les renvoie.

**`demo_4_essais()`** — Cette fonction joue cinquante mille fois la scène du livreur, avec une porte qui s'ouvre huit fois sur dix : elle ne reçoit rien, fixe la graine du hasard à 1, compte pour chaque partie le nombre d'essais jusqu'au premier succès et obtient une moyenne de 1,2559, tout près de la théorie 1/0,8 = 1,25. Elle retrouve aussi 1,25 par la somme des queues, Σ P(N > k) sur soixante termes, puis le nombre moyen de 1,24 quand on s'arrête au bout de trois essais, imprime ces résultats et les renvoie.

**`demo_5_sensibilite()`** — Celle-ci mesure combien le coût moyen d'un ticket réagit quand on déplace un peu de probabilité : elle ne reçoit rien, part de la loi du cas 1, 80 % de résolutions à 0,02 USD, 15 % de relances à 0,05 USD et 5 % d'escalades à 3 USD, d'espérance 0,1735, puis déplace deux points de l'escalade vers la résolution, ce qui donne 0,1139, soit 0,0596 de moins. Elle augmente ensuite l'escalade de 1 % relatif, ce qui ajoute 0,00149, soit 0,86 %, et calcule l'espérance 7,75 de quatre valeurs équiprobables ; elle imprime et renvoie ces nombres.

**`demo_6_produit()`** — Cette fonction montre que l'espérance d'un produit n'est le produit des espérances que pour des variables indépendantes : elle ne reçoit rien, calcule l'espérance du produit de deux dés indépendants, 12,25 = 3,5², puis celle du carré d'un seul dé, 15,1667, nettement plus grande. Elle compare aussi deux étapes réussies chacune à 0,95, qui réussissent ensemble avec la probabilité 0,9025 si elles sont indépendantes, mais 0,95 si une cause commune les fait toujours échouer en même temps, imprime ces résultats et les renvoie avec l'espérance 3,5 d'un dé.

**`cas_1_tickets_banque()`** — Cette fonction raconte une banque de détail dont l'agent traite environ 50 000 tickets par mois et qui ne peut financer qu'un seul projet : diviser par deux le coût de la résolution directe, ou faire passer l'escalade de 5 % à 3 %. Elle ne reçoit rien, calcule le coût moyen d'un ticket, 0,1735 USD, soit 8 675 USD par mois, dont 86,5 % viennent de la seule branche rare de l'escalade, ainsi que sa variance, 0,42059, et son écart-type, 0,64853 USD. Elle chiffre le gain du projet A à 400 USD par mois et celui du projet B à 2 980, montre qu'une moyenne naïve des trois coûts, 1,0233 USD, et le cas typique, 1 000 USD par mois, trompent tous deux, calcule le coût d'escalade de bascule, 0,42 USD, et renvoie ces nombres.

**`cas_2_franchise_assur(franchise, p_perte_totale, afficher)`** — On y suit l'agent de tarification d'un assureur auto qui cherche la plus petite franchise tenant une prime pure de 4 500 AED par sinistre : la fonction reçoit la franchise, 1 500 AED par défaut, la probabilité d'une perte totale, 0,05 par défaut, et un drapeau d'affichage, refuse une franchise négative par une `ValueError`, puis décrit quatre dommages de 1 500, 4 000, 9 000 et 40 000 AED et calcule, pour chacun, l'indemnité après une vétusté de 12 % et la franchise, jamais en dessous de 0. Elle renvoie les indemnités 0, 2 020, 6 420 et 33 700, leur espérance de 4 300 AED, le dommage moyen de 6 550, le raccourci fautif 0,88 E − F = 4 264, qui oublie le plancher à zéro, et l'écart-type de 7 116,1 ; à 1 264 AED de franchise, l'espérance atteint tout juste 4 500.

**`cas_3_fin_de_service_rh(p_6ans)`** — Cette fonction met en scène un cabinet de ressources humaines qui doit provisionner les indemnités de fin de service d'un client de 200 salariés payés 9 000 AED de base : elle reçoit la probabilité de départ du groupe de six ans d'ancienneté, 0,1 par défaut, et décrit trois groupes, 60 salariés à deux ans qui partent avec la probabilité 0,2, 100 à six ans qui partent avec la probabilité reçue, et 40 à douze ans qui partent avec la probabilité 0,05. Elle calcule les indemnités 12 600, 40 500 et 94 500 AED, la provision attendue de 745 200 AED pour 24 départs, l'écart-type de 182 356 sous l'hypothèse de départs indépendants et le calcul naïf de 1 030 320 AED, qui multiplie l'indemnité moyenne de l'effectif, 42 930, par le nombre de départs, puis renvoie ces nombres sans rien imprimer.

**`cas_4_promotion_immo(conversion_promo)`** — Ici, un promoteur qui vend des appartements neufs à 1 200 000 AED, avec une marge de 15 %, se demande s'il doit offrir les frais DLD de 4 %, soit 48 000 AED, à ses 2 000 prospects qualifiés du mois : la fonction reçoit le taux de conversion avec la promotion, 0,11 par défaut, et compare la marge attendue par prospect, 0,08 × 180 000 = 14 400 AED sans promotion, à 0,11 × 132 000 = 14 520 avec. Elle renvoie un écart de 240 000 AED par mois, un taux de bascule de 0,10909, les 160 et 220 ventes attendues, et le raisonnement naïf de 7 920 000 AED, qui oublie que les 160 acheteurs qui auraient acheté de toute façon reçoivent eux aussi les frais offerts.

**`main()`** — C'est le chef d'orchestre de la fiche : il vérifie d'abord l'exemple simple, d'espérance 6,8, de moment d'ordre deux 66,4, de variance 20,16 et d'écart-type 4,49, en notant que la moyenne ne figure parmi aucune des valeurs possibles, puis appelle les démonstrations 1, 2, 4, 5 et 6 et contrôle qu'une loi dont les probabilités ne somment pas à 1 est refusée. Il joue ensuite les quatre cas, imprime lui-même les résultats des cas 3 et 4 et les bascules du cas 2, puis recalcule le corrigé des exercices ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tout concorde.

```python
"""Démonstration 22 — espérance : linéarité, indicatrice, variance, essais jusqu'au succès, sensibilité, produit et indépendance, quatre cas aux Émirats."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

USD_EN_AED = 3.6725


def proche(x: float, y: float, tol: float = 1e-9) -> bool:
    return abs(x - y) <= tol


def esperance(loi):
    """E[X] = Σ x P(X = x) ; loi = liste de (probabilité, valeur), probabilités ≥ 0 de somme 1."""
    if any(p < 0 for p, _ in loi) or not math.isclose(sum(p for p, _ in loi), 1.0):
        raise ValueError("probabilités positives de somme 1 attendues")
    return sum(p * x for p, x in loi)


def variance(loi):
    """Var(X) = E[X²] − E[X]² (démonstration 3)."""
    return esperance([(p, x * x) for p, x in loi]) - esperance(loi) ** 2


def essais_moyens(p: float, r: int | None = None) -> float:
    """Nombre moyen d'essais : 1/p sans limite, (1 − (1 − p)^r)/p avec au plus r essais (démonstration 4)."""
    if not 0 < p <= 1:
        raise ValueError("p dans ]0 ; 1]")
    return 1 / p if r is None else (1 - (1 - p) ** r) / p


def indemnite_fin_service(base: float, annees: float) -> float:
    """Secteur privé : 21 jours par an les 5 premières années, 30 au-delà, salaire journalier = base / 30, plafond 24 mois."""
    if annees < 1:
        return 0.0
    jours = 21 * min(annees, 5) + 30 * max(annees - 5, 0)
    return min(jours * base / 30, 24 * base)


def demo_1_linearite() -> dict:
    random.seed(22)
    x = [random.random() for _ in range(1000)]
    y = [a * a for a in x]                                                 # Y dépend de X
    moy = lambda l: sum(l) / len(l)
    gauche, droite = moy([2 * a + 3 * b for a, b in zip(x, y)]), 2 * moy(x) + 3 * moy(y)
    lancer = [(1 / 6, k) for k in range(1, 7)]
    somme_deux = esperance([(1 / 36, a + b) for a in range(1, 7) for b in range(1, 7)])
    print(f"démo 1 : E[2X + 3X²] = {gauche:.6f} = 2 E[X] + 3 E[X²] = {droite:.6f} ; deux dés : E = {somme_deux:.1f}"
          f" = 2 × {esperance(lancer)}")
    return {"gauche": gauche, "droite": droite, "somme_deux": somme_deux}


def demo_2_indicatrices() -> dict:
    probas = [0.99, 0.98, 0.97]
    nb_reussies = sum(probas)
    toutes = math.prod(probas)
    print(f"démo 2 : étapes réussies en moyenne {nb_reussies:.2f} sur 3 ; toutes réussies (indépendance) {toutes:.6f}")
    return {"nb": nb_reussies, "toutes": toutes}


def demo_4_essais() -> dict:
    random.seed(1)
    essais = []
    for _ in range(50_000):
        n = 1
        while random.random() >= 0.8:
            n += 1
        essais.append(n)
    simule = sum(essais) / len(essais)
    queues = sum((1 - 0.8) ** k for k in range(60))
    print(f"démo 4 : essais moyens simulés (p = 0,8) {simule:.4f} ; théorie {1 / 0.8} ; somme des queues {queues:.4f} ;"
          f" au plus 3 essais {essais_moyens(0.8, 3):.2f}")
    return {"simule": simule, "queues": queues, "tronque": essais_moyens(0.8, 3)}


def demo_5_sensibilite() -> dict:
    ticket = [(0.8, 0.02), (0.15, 0.05), (0.05, 3.00)]
    e = esperance(ticket)
    deplace = esperance([(0.82, 0.02), (0.15, 0.05), (0.03, 3.00)])
    plus_1pc = esperance([(0.7995, 0.02), (0.15, 0.05), (0.0505, 3.00)])
    egales = esperance([(0.25, x) for x in (2, 5, 9, 15)])
    print(f"démo 5 : 2 points d'escalade vers la résolution : {e:.4f} → {deplace:.4f} (écart {deplace - e:.4f}) ;"
          f" escalade +1 % : +{plus_1pc - e:.5f} ({(plus_1pc - e) / e:.2%}) ; probabilités égales {egales}")
    return {"e": e, "deplace": deplace, "plus_1pc": plus_1pc, "egales": egales}


def demo_6_produit() -> dict:
    de = [(1 / 6, k) for k in range(1, 7)]
    produit_indep = esperance([(1 / 36, a * b) for a in range(1, 7) for b in range(1, 7)])
    produit_meme = esperance([(1 / 6, k * k) for k in range(1, 7)])
    p = 0.95
    ensemble = p                                                           # deux étapes qui échouent toujours ensemble
    independantes = p * p
    print(f"démo 6 : dés indépendants E[XY] = {produit_indep:.2f} = 3.5² ; même dé E[X·X] = {produit_meme:.4f} ;"
          f" deux étapes à 0.95 : indépendantes {independantes:.4f}, cause commune {ensemble:.2f}")
    return {"indep": produit_indep, "meme": produit_meme, "independantes": independantes, "ensemble": ensemble,
            "e_de": esperance(de)}


def cas_1_tickets_banque() -> dict:
    """[BANQUE] coût moyen d'un ticket de support : la branche rare qui pèse tout."""
    ticket = [(0.8, 0.02), (0.15, 0.05), (0.05, 3.00)]
    e, v = esperance(ticket), variance(ticket)
    e2 = esperance([(p, x * x) for p, x in ticket])
    mensuel = 50_000 * e
    part = 0.05 * 3 / e
    projet_a = esperance([(0.8, 0.01), (0.15, 0.05), (0.05, 3.00)])
    projet_b = esperance([(0.82, 0.02), (0.15, 0.05), (0.03, 3.00)])
    gain_a, gain_b = (e - projet_a) * 50_000, (e - projet_b) * 50_000
    naif_moyenne = (0.02 + 0.05 + 3.00) / 3
    c_bascule = 0.02 + (e - projet_a) / 0.02
    print(f"cas 1 : E = {e:.4f} USD ({e * USD_EN_AED:.4f} AED) ; mensuel {mensuel:,.0f} USD ({mensuel * USD_EN_AED:,.2f} AED) ;"
          f" part de l'escalade {part:.1%}")
    print(f"        E[C²] = {e2:.6f} ; variance {v:.5f} ; écart-type {math.sqrt(v):.5f} USD ({math.sqrt(v) / e:.2f} × E) ;"
          f" projet A {gain_a:,.0f} USD/mois, projet B {gain_b:,.0f} USD/mois")
    print(f"        moyenne naïve {naif_moyenne:.4f} USD ({50_000 * naif_moyenne:,.0f} USD/mois) ; cas typique {50_000 * 0.02:,.0f} USD/mois ;"
          f" bascule coût d'escalade {c_bascule:.2f} USD")
    return {"e": e, "v": v, "e2": e2, "mensuel": mensuel, "part": part, "gain_a": gain_a, "gain_b": gain_b,
            "naif": naif_moyenne, "c_bascule": c_bascule, "projet_b": projet_b, "projet_a": projet_a}


def cas_2_franchise_assur(franchise: float = 1500.0, p_perte_totale: float = 0.05, afficher: bool = True) -> dict:
    """[ASSUR] prime pure d'un sinistre auto : vétusté 12 % du dommage, franchise, plancher à 0."""
    if franchise < 0:
        raise ValueError("franchise positive attendue")
    dommages = [(0.2, 1500), (0.5 - (p_perte_totale - 0.05), 4000), (0.25, 9000), (p_perte_totale, 40000)]
    indemnites = [(p, max(0.0, 0.88 * d - franchise)) for p, d in dommages]
    e = esperance(indemnites)
    e_dommage = esperance(dommages)
    raccourci = 0.88 * e_dommage - franchise
    sd = math.sqrt(variance(indemnites))
    if afficher:
        print(f"cas 2 : franchise {franchise:,.0f} ; indemnités {[round(x) for _, x in indemnites]} ; E = {e:,.1f} AED ;"
              f" E[dommage] = {e_dommage:,.0f} ; raccourci 0.88 E − F = {raccourci:,.1f} ; écart-type {sd:,.1f}")
    return {"indemnites": indemnites, "e": e, "e_dommage": e_dommage, "raccourci": raccourci, "sd": sd}


def cas_3_fin_de_service_rh(p_6ans: float = 0.1) -> dict:
    """[RH] provision annuelle d'indemnités de fin de service pour une cohorte de 200 salariés."""
    base = 9000
    groupes = [(60, 2, 0.2), (100, 6, p_6ans), (40, 12, 0.05)]           # effectif, ancienneté, probabilité de départ
    montants = [indemnite_fin_service(base, a) for _, a, _ in groupes]
    attendu = sum(n * p * m for (n, _, p), m in zip(groupes, montants))
    departs = sum(n * p for n, _, p in groupes)
    var = sum(n * p * (1 - p) * m * m for (n, _, p), m in zip(groupes, montants))
    sd = math.sqrt(var)
    moyenne_montants = sum(n * m for (n, _, _), m in zip(groupes, montants)) / 200
    naif = moyenne_montants * departs
    return {"montants": montants, "attendu": attendu, "departs": departs, "sd": sd, "naif": naif,
            "moyenne_montants": moyenne_montants, "plafond": 24 * base}


def cas_4_promotion_immo(conversion_promo: float = 0.11) -> dict:
    """[IMMO] promoteur : offrir les frais DLD de 4 % ou non, pour 2 000 prospects qualifiés par mois."""
    prix, marge = 1_200_000, 0.15 * 1_200_000
    frais_dld = 0.04 * prix
    sans = 0.08 * marge
    avec = conversion_promo * (marge - frais_dld)
    ecart_mois = (avec - sans) * 2000
    bascule = sans / (marge - frais_dld)
    ventes_sans, ventes_avec = 0.08 * 2000, conversion_promo * 2000
    naif = (ventes_avec - ventes_sans) * marge - (ventes_avec - ventes_sans) * frais_dld
    return {"frais_dld": frais_dld, "marge": marge, "sans": sans, "avec": avec, "ecart_mois": ecart_mois,
            "bascule": bascule, "ventes": (ventes_sans, ventes_avec), "naif": naif}


def main() -> None:
    simple = [(0.2, 2), (0.5, 5), (0.1, 9), (0.2, 15)]
    e_s, v_s = esperance(simple), variance(simple)
    print(f"exemple simple : E = {e_s:.1f} ; E[X²] = {esperance([(p, x * x) for p, x in simple]):.1f} ;"
          f" variance {v_s:.2f} ; écart-type {math.sqrt(v_s):.2f}")
    assert math.isclose(e_s, 6.8) and math.isclose(esperance([(p, x * x) for p, x in simple]), 66.4)
    assert round(v_s, 2) == 20.16 and round(math.sqrt(v_s), 2) == 4.49 and proche(6.8 ** 2, 46.24)
    assert [round(p * x, 1) for p, x in simple] == [0.4, 2.5, 0.9, 3.0] and e_s not in [x for _, x in simple]

    d1 = demo_1_linearite()
    assert math.isclose(d1["gauche"], d1["droite"]) and proche(d1["somme_deux"], 7)
    assert round(d1["gauche"], 6) == round(d1["droite"], 6) == 1.982678
    d2 = demo_2_indicatrices()
    assert round(d2["nb"], 2) == 2.94 and round(d2["toutes"], 6) == 0.941094 and proche(0.99 * 0.98, 0.9702)
    d4 = demo_4_essais()
    assert abs(d4["simule"] - 1.25) < 0.01 and round(d4["simule"], 4) == 1.2559
    assert round(d4["queues"], 4) == 1.25 and round(d4["tronque"], 2) == 1.24 and proche(1 - 0.2 ** 3, 0.992)
    assert proche(1 * 0.8 + 3 * 0.2, 1.4) and proche(0.992 / 0.8, 1.24)                 # échecs corrélés : 1,4 essai
    d5 = demo_5_sensibilite()
    assert round(d5["e"], 4) == 0.1735 and round(d5["deplace"], 4) == 0.1139 and round(d5["deplace"] - d5["e"], 4) == -0.0596
    assert round(d5["plus_1pc"] - d5["e"], 5) == 0.00149 and round((d5["plus_1pc"] - d5["e"]) / d5["e"], 4) == 0.0086
    try:
        esperance([(0.8, 0.02), (0.15, 0.05), (0.07, 3.00)])
        refuse = False
    except ValueError:
        refuse = True
    assert refuse and proche(0.1735 + 0.02 * 3, 0.2335)
    assert d5["egales"] == 7.75 and proche(0.02 * (0.02 - 3), -0.0596) and proche(0.0005 * (3 - 0.02), 0.00149)
    d6 = demo_6_produit()
    assert round(d6["indep"], 2) == 12.25 and round(d6["meme"], 4) == 15.1667 and round(d6["independantes"], 4) == 0.9025
    assert proche(max(0.0, 1 - 2 * 0.05), 0.9) and d6["ensemble"] == 0.95 and proche(d6["e_de"], 3.5) and round(d6["meme"] - 3.5 ** 2, 4) == 2.9167

    c1 = cas_1_tickets_banque()
    assert round(c1["e"], 4) == 0.1735 and round(c1["mensuel"]) == 8675 and round(c1["part"], 3) == 0.865
    assert round(c1["e"] * USD_EN_AED, 4) == 0.6372 and round(c1["mensuel"] * USD_EN_AED, 2) == 31858.94
    assert round(c1["e2"], 6) == 0.450695 and round(c1["v"], 5) == 0.42059 and round(math.sqrt(c1["v"]), 5) == 0.64853
    assert round(math.sqrt(c1["v"]) / c1["e"], 2) == 3.74 and round(c1["gain_a"]) == 400 and round(c1["gain_b"]) == 2980
    assert round(c1["naif"], 4) == 1.0233 and round(50_000 * c1["naif"]) == 51167 and 50_000 * 0.02 == 1000
    assert round(c1["c_bascule"], 2) == 0.42 and round(c1["projet_a"], 4) == 0.1655
    assert proche(0.8 * 0.02 + 0.15 * 0.05 + 0.05 * 3, 0.1735) and proche(0.8 * 0.0004 + 0.15 * 0.0025 + 0.05 * 9, 0.450695)
    assert round(c1["mensuel"] / (50_000 * 0.02), 1) == 8.7 and round(51167 / 8675, 1) == 5.9
    assert round(esperance([(0.79, 0.02), (0.15, 0.05), (0.06, 3.00)]), 4) == 0.2033 and proche(0.8 * 0.01, 0.008)
    assert round(esperance([(0.79, 0.02), (0.15, 0.05), (0.06, 3.00)]) / c1["e"] - 1, 2) == 0.17 and proche(0.05 * 9, 0.45)
    assert round(0.0596 * 50_000) == 2980 and round(0.008 * 50_000) == 400 and round(0.450695 - 0.030102, 5) == 0.42059
    c2 = cas_2_franchise_assur()
    assert [round(x) for _, x in c2["indemnites"]] == [0, 2020, 6420, 33700] and round(c2["e"], 1) == 4300.0
    assert round(c2["e_dommage"]) == 6550 and round(c2["raccourci"], 1) == 4264.0 and round(c2["e"] - c2["raccourci"], 1) == 36.0
    assert c2["sd"] / c2["e"] > 1.5 and round(c2["sd"], 1) == 7116.1 and round(c2["e"] - c2["raccourci"]) * 2400 == 86400
    assert (0.5 * 2020, 0.25 * 6420, 0.05 * 33700, round(0.88 * 1500)) == (1010, 1605, 1685, 1320)
    f500 = cas_2_franchise_assur(500, afficher=False)
    f1000 = cas_2_franchise_assur(1000, afficher=False)
    assert [round(x) for _, x in f500["indemnites"]] == [820, 3020, 7420, 34700] and round(f500["e"]) == 5264
    assert proche(f500["e"], f500["raccourci"]) and round(f1000["e"]) == 4764 and round(0.88 * 6550) == 5764
    assert proche(cas_2_franchise_assur(1264, afficher=False)["e"], 4500) and 1264 < 0.88 * 1500
    pt = cas_2_franchise_assur(1500, p_perte_totale=0.055, afficher=False)
    assert round(pt["e"] - c2["e"], 1) == 158.4 and round(pt["e"], 1) == 4458.4 and pt["e"] <= 4500
    print(f"        bascule franchise 1,264 → E = 4,500 ; perte totale 5.5 % → E = {pt['e']:,.1f}")
    c3 = cas_3_fin_de_service_rh()
    assert c3["montants"] == [12600, 40500, 94500] and round(c3["attendu"]) == 745200 and round(c3["departs"]) == 24
    assert round(c3["sd"]) == 182356 and round(c3["attendu"] + 2 * c3["sd"]) == 1109913 and c3["plafond"] == 216000
    assert round(c3["moyenne_montants"]) == 42930 and round(c3["naif"]) == 1030320 and round(c3["naif"] - c3["attendu"]) == 285120
    assert indemnite_fin_service(9000, 0.5) == 0 and indemnite_fin_service(9000, 30) == 216000      # plancher et plafond
    assert round(cas_3_fin_de_service_rh(459800 / 4050000)["attendu"]) == 800000 and round(459800 / 4050000, 5) == 0.11353
    assert (60 * 0.2 * 12600, 100 * 0.1 * 40500, 40 * 0.05 * 94500) == (151200, 405000, 189000)
    assert 800000 - 745200 == 54800 and round(54800 / c3["sd"], 1) == 0.3 and round(0.11353 / 0.1 - 1, 3) == 0.135
    assert 800000 - 151200 - 189000 == 459800 and (21 * 5 + 30, 105 + 30 * 7) == (135, 315)
    print(f"cas 3 : indemnités {[round(m) for m in c3['montants']]} AED ; provision attendue {c3['attendu']:,.0f} AED pour {c3['departs']:.0f} départs ;"
          f" écart-type {c3['sd']:,.0f} ; μ + 2σ = {c3['attendu'] + 2 * c3['sd']:,.0f}")
    print(f"        naïf : {c3['moyenne_montants']:,.0f} × 24 = {c3['naif']:,.0f} AED (+{c3['naif'] - c3['attendu']:,.0f}) ;"
          f" bascule budget 800,000 : départ du groupe 6 ans {459800 / 4050000:.5f}")
    c4 = cas_4_promotion_immo()
    assert c4["frais_dld"] == 48000 and c4["marge"] == 180000 and round(c4["sans"]) == 14400 and round(c4["avec"]) == 14520
    assert round(c4["ecart_mois"]) == 240000 and round(c4["bascule"], 5) == 0.10909 and c4["ventes"] == (160, 220)
    assert round(c4["naif"]) == 7920000 and round(c4["naif"] / c4["ecart_mois"]) == 33
    assert round(cas_4_promotion_immo(0.107)["avec"]) == 14124 and cas_4_promotion_immo(0.107)["avec"] < c4["sans"]
    assert round(160 * 180000) == 28_800_000 and round(220 * 132000) == 29_040_000 and 160 * 48000 == 7_680_000
    assert round((cas_4_promotion_immo(0.107)["avec"] - c4["sans"]) * 2000) == -552000
    print(f"cas 4 : frais DLD {c4['frais_dld']:,.0f} ; marge par prospect sans {c4['sans']:,.0f}, avec {c4['avec']:,.0f} ;"
          f" écart {c4['ecart_mois']:,.0f} AED/mois ; bascule {c4['bascule']:.5f} ; raisonnement naïf {c4['naif']:,.0f}")

    print("Corrigé")
    de = [(1 / 6, k) for k in range(1, 7)]
    e4 = esperance([(0.82, 0.02), (0.15, 0.05), (0.03, 3.00)])
    ex6 = cas_4_promotion_immo(0.12)
    faux = c1["e"] ** 2
    ex8 = essais_moyens(0.6, 3)
    print(f"  ex1 E = {esperance(de):.1f}, Var = {variance(de):.4f} ; ex2 {0.9 * 0.01 + 0.5 * 0.04:.3f} ;"
          f" ex3 {essais_moyens(0.25):.0f} ; ex4 {e4:.4f}")
    print(f"  ex6 avec promotion {ex6['avec']:,.0f} > {ex6['sans']:,.0f} ; ex7 E[C]² = {faux:.6f} ≠ E[C²] ;"
          f" ex8 {ex8:.2f} essais")
    assert math.isclose(esperance(de), 3.5) and round(variance(de), 4) == 2.9167 and proche(91 / 6 - 12.25, variance(de))
    assert round(0.9 * 0.01 + 0.5 * 0.04, 3) == 0.029 and round(e4, 4) == 0.1139 and essais_moyens(0.25) == 4
    assert round(ex6["avec"]) == 15840 and ex6["avec"] > ex6["sans"] and round(faux, 6) == 0.030102
    assert round(ex8, 2) == 1.56 and proche(1 - 0.4 ** 3, 0.936) and round(ex6["ecart_mois"]) == 2880000
    assert math.isclose(variance([(p, 3 * x) for p, x in [(0.8, 0.02), (0.15, 0.05), (0.05, 3.00)]]), 9 * c1["v"])
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
exemple simple : E = 6.8 ; E[X²] = 66.4 ; variance 20.16 ; écart-type 4.49
démo 1 : E[2X + 3X²] = 1.982678 = 2 E[X] + 3 E[X²] = 1.982678 ; deux dés : E = 7.0 = 2 × 3.5
démo 2 : étapes réussies en moyenne 2.94 sur 3 ; toutes réussies (indépendance) 0.941094
démo 4 : essais moyens simulés (p = 0,8) 1.2559 ; théorie 1.25 ; somme des queues 1.2500 ; au plus 3 essais 1.24
démo 5 : 2 points d'escalade vers la résolution : 0.1735 → 0.1139 (écart -0.0596) ; escalade +1 % : +0.00149 (0.86%) ; probabilités égales 7.75
démo 6 : dés indépendants E[XY] = 12.25 = 3.5² ; même dé E[X·X] = 15.1667 ; deux étapes à 0.95 : indépendantes 0.9025, cause commune 0.95
cas 1 : E = 0.1735 USD (0.6372 AED) ; mensuel 8,675 USD (31,858.94 AED) ; part de l'escalade 86.5%
        E[C²] = 0.450695 ; variance 0.42059 ; écart-type 0.64853 USD (3.74 × E) ; projet A 400 USD/mois, projet B 2,980 USD/mois
        moyenne naïve 1.0233 USD (51,167 USD/mois) ; cas typique 1,000 USD/mois ; bascule coût d'escalade 0.42 USD
cas 2 : franchise 1,500 ; indemnités [0, 2020, 6420, 33700] ; E = 4,300.0 AED ; E[dommage] = 6,550 ; raccourci 0.88 E − F = 4,264.0 ; écart-type 7,116.1
        bascule franchise 1,264 → E = 4,500 ; perte totale 5.5 % → E = 4,458.4
cas 3 : indemnités [12600, 40500, 94500] AED ; provision attendue 745,200 AED pour 24 départs ; écart-type 182,356 ; μ + 2σ = 1,109,913
        naïf : 42,930 × 24 = 1,030,320 AED (+285,120) ; bascule budget 800,000 : départ du groupe 6 ans 0.11353
cas 4 : frais DLD 48,000 ; marge par prospect sans 14,400, avec 14,520 ; écart 240,000 AED/mois ; bascule 0.10909 ; raisonnement naïf 7,920,000
Corrigé
  ex1 E = 3.5, Var = 2.9167 ; ex2 0.029 ; ex3 4 ; ex4 0.1139
  ex6 avec promotion 15,840 > 14,400 ; ex7 E[C]² = 0.030102 ≠ E[C²] ; ex8 1.56 essais
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme calcule l'espérance et la variance d'une variable discrète, par exemple le coût d'un ticket, les vérifie par simulation, et calcule une provision comme une somme d'espérances groupe par groupe.

```text
ALGORITHME EspéranceEtVariance
ENTRÉE  : loi (probabilité pᵢ, valeur xᵢ) pour i de 1 à n, avec pᵢ ≥ 0 et Σ pᵢ = 1
SORTIE  : (μ, variance)

  SI une probabilité est négative OU Σ pᵢ ≠ 1 ALORS ERREUR
  μ ← 0 ; m2 ← 0
  POUR i DE 1 À n FAIRE
      μ  ← μ + pᵢ × xᵢ
      m2 ← m2 + pᵢ × xᵢ²
  FIN POUR
  RETOURNER μ, m2 − μ²

ALGORITHME EssaisJusquAuSuccès (simulation)
  n ← 1
  TANT QUE le tirage échoue (probabilité 1 − p) FAIRE n ← n + 1 FIN TANT QUE
  RETOURNER n

ALGORITHME ProvisionParGroupes
ENTRÉES : groupes (effectif nⱼ, probabilité pⱼ, montant mⱼ), supposés indépendants
SORTIE  : provision attendue, écart-type
  RETOURNER Σ nⱼ × pⱼ × mⱼ, racine de Σ nⱼ × pⱼ × (1 − pⱼ) × mⱼ²
```

**Complexité.** O(n) pour la loi, O(1) en mémoire. La simulation de N séries d'essais coûte O(N / p) en moyenne, puisque chaque série fait 1/p essais en moyenne. La provision coûte O(nombre de groupes) : on ne parcourt jamais les salariés un par un, grâce à la linéarité.

**Du squelette au code.** `esperance(loi)` et `variance(loi)` sont les deux accumulations ; la variance utilise 𝔼[X²] − μ² (démonstration 3), et `esperance` lève `ValueError` si la loi n'en est pas une. La boucle `while random.random() >= 0.8` de `demo_4_essais` est la simulation, comparée à 1/0,8 = 1,25 et à la formule `essais_moyens(p, r)`. Le montant de chaque groupe du cas 3 vient de `indemnite_fin_service(base, annees)`, qui applique les 21 puis 30 jours par an et le plafond de 24 mois. Les démonstrations sont rejouées par `demo_1_linearite`, `demo_2_indicatrices`, `demo_5_sensibilite` et `demo_6_produit` ; les quatre cas par `cas_1_tickets_banque`, `cas_2_franchise_assur`, `cas_3_fin_de_service_rh` et `cas_4_promotion_immo`.
