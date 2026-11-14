# Étape 60 bis — Évaluation — Loi bêta et petits échantillons

> Étape 60 bis du parcours · Prérequis : [Agent Goal Accuracy](<60-Evaluation-Formule-Agent-Goal-Accuracy.md>) · Suite : [Mean Average Precision](<61-Evaluation-Formule-MAP.md>)

**Dossier :** 10-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Product Engineers, Forward-Deployed Engineers  
**Nom du fichier :** 60b-Loi-Beta-et-Petits-Echantillons.md

L'étape 60 a mesuré un taux de réussite avec l'intervalle de Wilson, et la section « Pour aller plus loin » annonçait une approche bayésienne. La voici. Elle répond aux questions que posent les **petits échantillons**, fréquents en évaluation d'agents parce que chaque essai coûte un appel au modèle : que dire après 9 réussites sur 10 ? Quelle probabilité donner à la prochaine tâche ? Comment classer un outil testé 3 fois contre un outil testé 100 fois ? Quelle est la probabilité que la version A soit meilleure que la version B ? Tout se fait en Python standard, sans bibliothèque de statistiques.

## Définition

La loi bêta Beta(a, b) est une loi de probabilité sur l'intervalle [0, 1] : elle décrit ce que l'on sait d'un **taux inconnu** p, par exemple le taux de réussite d'un agent. Ses deux paramètres positifs se lisent comme des comptes fictifs : a joue le rôle d'un nombre de succès, b d'un nombre d'échecs. On part d'une loi **a priori**, qui résume ce que l'on savait avant l'évaluation, puis l'on observe s succès sur n essais. La loi **a posteriori** est encore une loi bêta, Beta(a + s, b + n − s) : on ajoute les succès à a et les échecs à b. Cette propriété, la **conjugaison**, fait tenir toute la mise à jour dans deux additions. De la loi a posteriori on tire une estimation (sa moyenne), un intervalle crédible (entre deux quantiles) et des probabilités de décision, comme P(p ≥ 0,90) ou P(p_A > p_B).

## Rôle dans un agent

La loi bêta sert à l'étape **observer**, dans trois composants. Dans le **banc d'évaluation** (étape 13 bis), elle remplace ou complète l'intervalle de Wilson quand le jeu est petit : une catégorie rare de dossiers, une langue peu représentée, une nouvelle version jugée sur dix tâches. Dans la **surveillance en production**, elle se met à jour en continu avec deux compteurs, sans garder l'historique : chaque conversation notée ajoute 1 à a ou à b. Dans un **routeur** qui choisit entre plusieurs outils ou sous-agents, elle évite de donner la priorité à celui qui a réussi 3 fois sur 3 face à celui qui a réussi 90 fois sur 100 : on classe par une borne basse, ou par un tirage dans chaque loi (échantillonnage de Thompson). La barrière de déploiement peut alors s'écrire directement : déployer si P(p ≥ τ | données) ≥ 0,95.

## Équation complète

Densité de la loi bêta et constante de normalisation :

$$
f(p \mid a, b) = \frac{p^{a-1}(1-p)^{b-1}}{B(a, b)}, \qquad B(a, b) = \int_0^1 t^{a-1}(1-t)^{b-1}\,dt = \frac{\Gamma(a)\,\Gamma(b)}{\Gamma(a+b)}
$$

Conjugaison avec la loi binomiale :

$$
p \sim \text{Beta}(a, b), \quad s \mid p \sim \text{Bin}(n, p) \quad\Longrightarrow\quad p \mid s \sim \text{Beta}(a + s,\; b + n - s)
$$

Moyenne a posteriori, qui est une moyenne pondérée de l'a priori et du taux observé :

$$
\mathbb{E}[p \mid s] = \frac{a + s}{a + b + n} = w\,\frac{a}{a+b} + (1 - w)\,\frac{s}{n}, \qquad w = \frac{a+b}{a+b+n}
$$

Règle de Laplace (a priori uniforme, a = b = 1) :

$$
P(\text{le prochain essai réussit} \mid s \text{ succès sur } n) = \frac{s + 1}{n + 2}
$$

Règle de trois : zéro échec observé sur n essais, borne haute à 95 % du taux d'échec q :

$$
q_{\max}^{\text{fréquentiste}} = 1 - 0{,}05^{1/n}, \qquad q_{\max}^{\text{bayésien}} = 1 - 0{,}05^{1/(n+1)}, \qquad \text{les deux} \approx \frac{3}{n}
$$

Fonction de répartition, quantile et intervalle crédible à 95 % à queues égales :

$$
F(x) = \int_0^x f(t \mid a, b)\,dt, \qquad F^{-1}(u) = \text{l'unique } x \text{ tel que } F(x) = u, \qquad \big[\,F^{-1}(0{,}025)\;;\;F^{-1}(0{,}975)\,\big]
$$

Probabilité que la version A soit meilleure que la version B, exacte puis par Monte-Carlo :

$$
P(p_A > p_B \mid \text{données}) = \int_0^1 f_A(x)\,F_B(x)\,dx \;\approx\; \frac{1}{N}\sum_{k=1}^{N} \mathbf{1}\big[\,x_A^{(k)} > x_B^{(k)}\,\big]
$$

## Décryptage des symboles

$$
p
$$

**Sens :** vrai taux de réussite de l'agent sur la population de tâches, inconnu ; la loi bêta décrit ce que l'on en sait · **Type / plage :** réel dans [0, 1] · **Variable Python :** `p`, ou la variable d'intégration `x`

$$
a,\ b
$$

**Sens :** paramètres de la loi bêta ; a se lit comme un nombre de succès, b comme un nombre d'échecs, fictifs dans l'a priori, réels après la mise à jour · **Type / plage :** réels > 0 (le code d'intégration demande ≥ 0,5) · **Variable Python :** `a`, `b`

$$
s,\ n
$$

**Sens :** nombre de succès observés et nombre d'essais · **Type / plage :** entiers, 0 ≤ s ≤ n · **Variable Python :** `succes`, `n`

$$
B(a, b)
$$

**Sens :** fonction bêta, constante qui fait intégrer la densité à 1 ; pour des entiers, B(a, b) = (a − 1)! (b − 1)! / (a + b − 1)! · **Type / plage :** réel > 0, parfois minuscule, d'où le calcul en logarithme · **Variable Python :** `math.exp(log_beta(a, b))`

$$
\Gamma(x)
$$

**Sens :** fonction gamma, qui prolonge la factorielle : Γ(k) = (k − 1)! pour k entier, et Γ(x + 1) = x Γ(x) · **Type / plage :** réel > 0 pour x > 0 · **Variable Python :** `math.lgamma(x)` en donne le logarithme

$$
f(p \mid a, b)
$$

**Sens :** densité de la loi bêta au point p ; ce n'est pas une probabilité, elle peut dépasser 1 · **Type / plage :** réel ≥ 0 · **Variable Python :** `densite_beta(x, a, b)`

$$
F(x)
$$

**Sens :** fonction de répartition : probabilité que p soit inférieur ou égal à x · **Type / plage :** réel dans [0, 1], croissante · **Variable Python :** `cdf_beta(x, a, b)`, ou `cdf_beta_entiers(x, a, b)` pour des paramètres entiers

$$
F^{-1}(u)
$$

**Sens :** quantile de niveau u : le taux x qui laisse une probabilité u en dessous de lui · **Type / plage :** réel dans [0, 1], pour u dans ]0, 1[ · **Variable Python :** `quantile_beta(u, a, b)`

$$
w
$$

**Sens :** poids de l'a priori dans la moyenne a posteriori ; il vaut a + b pseudo-essais rapportés au total · **Type / plage :** réel dans ]0, 1] · **Variable Python :** `poids`

$$
q,\ q_{\max}
$$

**Sens :** taux d'échec (ou de violation, comme à l'étape 7) et sa borne haute à 95 % quand aucun échec n'a été observé · **Type / plage :** réels dans [0, 1] · **Variable Python :** `borne_zero_echec(n)` et `quantile_beta(0.95, 1, n + 1)`

$$
p_A,\ p_B
$$

**Sens :** taux de réussite des versions A et B, chacun décrit par sa loi a posteriori · **Type / plage :** réels dans [0, 1] · **Variable Python :** paramètres `a_a`, `b_a`, `a_b`, `b_b`

$$
N,\ x_A^{(k)}
$$

**Sens :** nombre de tirages Monte-Carlo, et k-ième tirage du taux de A dans sa loi a posteriori · **Type / plage :** entier ≥ 1 ; réel dans [0, 1] · **Variable Python :** `tirages`, `rng.betavariate(a_a, b_a)`

## Démonstration

### 1. La constante B(a, b) et la moyenne a/(a + b)

L'intégrale B(a, b) est finie pour a > 0 et b > 0, parce que près de 0 l'intégrande se comporte comme tᵃ⁻¹, intégrable dès que a > 0, et de même près de 1. Diviser par B(a, b) fait donc intégrer la densité à 1. Pour des entiers, l'égalité B(a, b) = Γ(a) Γ(b) / Γ(a + b) donne B(10, 2) = 9! × 1! / 11! = 1/110. La moyenne se calcule en reconnaissant une autre fonction bêta :

$$
\mathbb{E}[p] = \frac{1}{B(a,b)}\int_0^1 p \cdot p^{a-1}(1-p)^{b-1}\,dp = \frac{B(a+1, b)}{B(a, b)} = \frac{\Gamma(a+1)\,\Gamma(a+b)}{\Gamma(a)\,\Gamma(a+b+1)} = \frac{a}{a+b}
$$

La dernière égalité vient de Γ(x + 1) = x Γ(x), appliqué au numérateur avec x = a et au dénominateur avec x = a + b. Le même calcul avec B(a + 2, b) donne la variance ab / ((a + b)²(a + b + 1)) : elle décroît comme 1/(a + b), c'est-à-dire comme 1/n une fois les essais ajoutés, ce qui redonne l'incertitude en 1/√n de l'étape 60. Pour Beta(10, 2), la variance vaut 20/(144 × 13) ≈ 0,0107, soit un écart-type d'environ 0,103.

### 2. La conjugaison, par la formule de Bayes

La formule de Bayes écrit la densité a posteriori comme la vraisemblance multipliée par la densité a priori, divisée par une constante qui ne dépend pas de p :

$$
f(p \mid s) = \frac{P(s \mid p)\, f(p)}{\int_0^1 P(s \mid u)\, f(u)\,du} \;\propto\; \binom{n}{s} p^{s}(1-p)^{n-s} \cdot \frac{p^{a-1}(1-p)^{b-1}}{B(a,b)} \;\propto\; p^{a+s-1}(1-p)^{b+n-s-1}
$$

Le coefficient binomial et 1/B(a, b) ne dépendent pas de p : ils disparaissent dans la normalisation. Il reste le noyau d'une loi Beta(a + s, b + n − s). Comme une densité qui intègre à 1 est entièrement fixée par son noyau, la constante est forcément 1/B(a + s, b + n − s), et la loi a posteriori est exactement Beta(a + s, b + n − s). Le programme le vérifie sans faire confiance à la formule : il calcule le dénominateur de Bayes par intégration numérique, divise, et retrouve la densité de Beta(10, 2) en p = 0,5, 0,8 et 0,9 à 10⁻⁹ près.

Deux conséquences pratiques. D'abord, l'ordre des observations ne compte pas, parce que l'addition est commutative : 5 réussites sur 5, puis 4 sur 5, donnent Beta(1 + 5 + 4, 1 + 0 + 1) = Beta(10, 2), comme 9 sur 10 d'un coup. Ensuite, la surveillance en ligne ne garde que deux compteurs.

### 3. La moyenne a posteriori tire le taux observé vers l'a priori

On vérifie l'égalité de l'équation complète en développant le membre de droite :

$$
\frac{a+b}{a+b+n}\cdot\frac{a}{a+b} + \frac{n}{a+b+n}\cdot\frac{s}{n} = \frac{a}{a+b+n} + \frac{s}{a+b+n} = \frac{a+s}{a+b+n}
$$

L'a priori pèse comme a + b essais déjà faits. Quand n grandit, le poids w tend vers 0 et la moyenne a posteriori tend vers le taux observé s/n : avec beaucoup de données, l'a priori est oublié. Avec un a priori Beta(8, 2), qui résume « l'équivalent de 10 tâches à 80 % », et 9 réussites sur 10, on obtient Beta(17, 3), de moyenne 17/20 = 0,85 = 0,5 × 0,8 + 0,5 × 0,9.

Le **mode**, point où la densité est maximale, se trouve en annulant la dérivée du logarithme de la densité, (a − 1)/p − (b − 1)/(1 − p) = 0, d'où p = (a − 1)/(a + b − 2) quand a > 1 et b > 1. Avec l'a priori uniforme, il vaut (s + 1 − 1)/(n + 2 − 2) = s/n : le taux brut est le mode a posteriori, pas sa moyenne. Pour 9 sur 10 : mode 0,9, moyenne 10/12 ≈ 0,8333.

### 4. La règle de Laplace et la prédiction de pass^k

On veut la probabilité que la prochaine tâche réussisse, sachant les données. Si l'on connaissait p, ce serait p. Comme on ne le connaît pas, la formule des probabilités totales fait la moyenne sur la loi a posteriori, en supposant les essais indépendants sachant p :

$$
P(\text{succès suivant} \mid s) = \int_0^1 p\, f(p \mid s)\,dp = \mathbb{E}[p \mid s] = \frac{a+s}{a+b+n} \;\overset{a=b=1}{=}\; \frac{s+1}{n+2}
$$

C'est la règle de succession de Laplace. Après 10 réussites sur 10, la prochaine réussit avec la probabilité 11/12 ≈ 0,9167, pas 1 ; sans aucune donnée, 1/2. Le même raisonnement prédit que les k prochaines tâches réussissent toutes, c'est-à-dire le pass^k de l'étape 60, en remplaçant p par pᵏ :

$$
\mathbb{E}[p^k \mid s] = \frac{B(a+s+k,\; b+n-s)}{B(a+s,\; b+n-s)} = \prod_{i=0}^{k-1}\frac{a+s+i}{a+b+n+i}
$$

Le produit s'obtient en appliquant k fois Γ(x + 1) = x Γ(x). Après 10 sur 10 avec l'a priori uniforme, pour k = 3 : 11/12 × 12/13 × 13/14 = 11/14 ≈ 0,7857, par simplification en cascade. La version « plug-in » du taux brut annoncerait 1³ = 1 : elle promet une constance parfaite à partir de dix essais seulement.

### 5. La fonction de répartition : formule exacte et intégration numérique

**Paramètres entiers.** Pour a et b entiers, on a la formule exacte

$$
F(x) = P\big(\text{Bin}(a+b-1,\, x) \ge a\big) = \sum_{j=a}^{a+b-1} \binom{a+b-1}{j}\, x^j (1-x)^{a+b-1-j}
$$

Preuve : on tire a + b − 1 nombres uniformes indépendants sur [0, 1] et l'on note U le a-ième plus petit. La densité de U en x s'obtient en choisissant lequel des a + b − 1 nombres tombe en x, puis lesquels des a + b − 2 autres tombent en dessous (a − 1 d'entre eux) : elle vaut (a + b − 1)! / ((a − 1)! (b − 1)!) × xᵃ⁻¹(1 − x)ᵇ⁻¹, qui est la densité de Beta(a, b). Or U ≤ x exactement quand au moins a des nombres sont ≤ x, et chacun l'est avec la probabilité x, indépendamment : c'est une loi binomiale. Pour Beta(10, 2), la somme n'a que deux termes :

$$
F(x) = 11\,x^{10}(1-x) + x^{11} = 11\,x^{10} - 10\,x^{11}, \qquad F(0{,}8) = 11 \times 0{,}107374 - 10 \times 0{,}085899 = 0{,}322123
$$

Après 9 réussites sur 10 et un a priori uniforme, P(p > 0,8) = 1 − 0,322123 = 0,677877 : environ deux chances sur trois que l'agent dépasse 80 %, loin d'une certitude.

**Paramètres quelconques.** Pour un a priori de Jeffreys, Beta(1/2, 1/2), les paramètres sont demi-entiers et la formule binomiale ne s'applique plus. On intègre la densité numériquement par la méthode de Simpson, après le changement de variable t = v², qui donne dt = 2v dv :

$$
\int_0^x t^{a-1}(1-t)^{b-1}\,dt = \int_0^{\sqrt{x}} 2\,v^{2a-1}(1-v^2)^{b-1}\,dv
$$

Pour a entier ou demi-entier, 2a − 1 est un entier positif ou nul : l'intégrande n'a plus de singularité en 0, alors que tᵃ⁻¹ était infinie en 0 pour a = 1/2. Pour éviter l'autre bord, on utilise la symétrie F(x ; a, b) = 1 − F(1 − x ; b, a), obtenue par le changement t → 1 − t : on n'intègre jamais que sur [0 ; 1/2], où 1 − v² ≥ 1/2. Sur une fonction régulière, l'erreur de Simpson décroît comme h⁴ : le programme trouve le même F(0,8) que la formule exacte à 10⁻⁹ près, et pour Beta(1/2, 1/2), dont la répartition exacte est (2/π) arcsin √x, il retrouve 0,295167 en x = 0,2.

### 6. Le quantile par dichotomie

La densité est strictement positive sur ]0, 1[, donc F est continue et strictement croissante : pour tout u dans ]0, 1[, il existe un unique x tel que F(x) = u. La dichotomie part de [0 ; 1], où F(0) = 0 < u < 1 = F(1), coupe l'intervalle en son milieu m, et garde la moitié où le changement a lieu : [lo ; m] si F(m) ≥ u, [m ; hi] sinon. L'invariant F(lo) < u ≤ F(hi) est conservé, et la largeur est divisée par deux à chaque tour : après k tours, elle vaut 2⁻ᵏ. Pour une tolérance de 10⁻⁹, il faut ⌈log₂ 10⁹⌉ = 30 tours, donc 30 intégrations. Contrôle à la main : pour Beta(6, 1), F(x) = x⁶, et le quantile de niveau 0,025 vaut 0,025^(1/6) ≈ 0,5407, ce que la dichotomie retrouve.

### 7. Intervalle crédible contre intervalle de Wilson

Les deux intervalles ne répondent pas à la même question. L'intervalle **crédible** à 95 % dit : « sachant l'a priori et les données, p est dans cet intervalle avec la probabilité 0,95 ». L'intervalle de **confiance** de Wilson (étape 7) dit : « la procédure qui fabrique cet intervalle couvre le vrai p dans 95 % des répétitions de l'expérience ». Numériquement, ils se rapprochent dès que n dépasse quelques dizaines, et divergent sur les très petits échantillons :

| Observé | A priori uniforme | A priori de Jeffreys | Wilson (étape 7) |
|---|---|---|---|
| 9 sur 10 | [0,5872 ; 0,9772] | [0,6187 ; 0,9890] | [0,5958 ; 0,9821] |
| 45 sur 50 | [0,7859 ; 0,9556] | [0,7946 ; 0,9608] | [0,7864 ; 0,9565] |
| 5 sur 5 | [0,5407 ; 0,9958] | [0,6206 ; 1] | [0,5655 ; 1] |

Sur 5 sur 5, l'a priori uniforme garde un échec fictif : la borne haute reste sous 1, à 0,975^(1/6) ≈ 0,9958, parce que F(x) = x⁶. Par convention, l'intervalle de Jeffreys prend 1 comme borne haute quand aucun échec n'est observé. Sur 45 sur 50, les trois intervalles diffèrent de moins d'un point : la barrière de l'étape 60 rend le même verdict sous les deux écoles. Version bayésienne de cette barrière : P(p ≥ 0,90 | 45 sur 50) = 1 − F(0,90) pour Beta(46, 6), soit 0,4024. On est loin des 0,95 exigés : la version est refusée.

### 8. La règle de trois, des deux côtés

On note q le taux d'échec et l'on observe zéro échec sur n essais. Côté fréquentiste (étape 7), les q compatibles à 95 % vérifient (1 − q)ⁿ ≥ 0,05, d'où q ≤ 1 − 0,05^(1/n). Côté bayésien, avec un a priori uniforme sur q, la loi a posteriori est Beta(1, n + 1), dont la répartition s'intègre directement :

$$
F(x) = (n+1)\int_0^x (1-t)^{n}\,dt = 1 - (1-x)^{n+1} = 0{,}95 \iff x = 1 - 0{,}05^{1/(n+1)}
$$

Les deux bornes valent environ 3/n, parce que 1 − e⁻ʸ ≈ y pour y petit et que ln 20 ≈ 2,9957 ≈ 3. Pour 300 réponses sans violation : 3/n = 0,0100, borne exacte fréquentiste 0,00994, borne bayésienne 0,00990. « Zéro violation » ne veut jamais dire « taux nul » : il faut environ 3 000 réponses sans faute pour descendre à 0,1 %.

### 9. Classer de petits échantillons

L'outil X a réussi 3 fois sur 3, l'outil Y 90 fois sur 100. Classés par taux brut, X (1,000) passe devant Y (0,900). Avec l'a priori uniforme, X suit Beta(4, 1) et Y Beta(91, 11). Pour X, F(x) = x⁴ : la borne basse à 5 % vaut 0,05^(1/4) ≈ 0,473 ; pour Y, elle vaut 0,838. La moyenne a posteriori, 0,800 contre 0,892, et la borne basse classent toutes deux Y devant X. Un classement par taux brut favorise systématiquement les outils peu testés, parce que les extrêmes 0/k et k/k sont fréquents quand k est petit.

### 10. Probabilité qu'une version soit meilleure

On conditionne par la valeur de p_A. Si p_A = x, la probabilité que p_B soit inférieur vaut F_B(x), parce que les deux taux sont indépendants : ils sont estimés sur des échantillons différents. On fait ensuite la moyenne sur x avec la densité de p_A :

$$
P(p_B < p_A) = \int_0^1 P(p_B < x)\, f_A(x)\,dx = \int_0^1 F_B(x)\, f_A(x)\,dx
$$

Monte-Carlo estime la même quantité sans intégrale : on tire N couples de taux dans les deux lois et l'on compte la part des tirages où celui de A dépasse celui de B. Chaque tirage est une variable de Bernoulli de paramètre P, donc la fréquence est sans biais, de variance P(1 − P)/N, comme à l'étape 60. Pour A à 45 sur 50 et B à 41 sur 50, avec l'a priori uniforme, on compare Beta(46, 6) et Beta(42, 10) : l'intégrale donne 0,8684, et 40 000 tirages donnent 0,867, à un écart-type d'environ 0,0017. Avec un seuil de décision de 0,95, on ne conclut pas.

Attention au protocole : cette formule suppose des **échantillons indépendants**, comme un test A/B où chaque version sert des usagers différents. Quand A et B sont jouées sur les **mêmes** tâches, l'appariement contient plus d'information, et le bon outil est le test de McNemar de l'étape 60 : pour ces mêmes chiffres, il donnait une p-valeur exacte de 0,34, et la même absence de conclusion.

### 11. Exemple fait à la main (le code reprend ces nombres)

Une nouvelle version d'agent est évaluée sur 10 tâches et en réussit 9.

| Question | Calcul | Résultat |
|---|---|---|
| loi a posteriori, a priori uniforme | Beta(1 + 9, 1 + 1) | Beta(10, 2) |
| constante | B(10, 2) = 9! × 1! / 11! | 1/110 |
| densité en 0,8 | 110 × 0,8⁹ × 0,2 | 2,952790 |
| moyenne et mode | 10/12 et 9/10 | 0,8333 et 0,9 |
| probabilité de dépasser 80 % | 1 − (11 × 0,8¹⁰ − 10 × 0,8¹¹) | 0,677877 |
| prochaine tâche après 10 sur 10 | 11/12 | 0,9167 |
| pass^3 après 10 sur 10 | 11/12 × 12/13 × 13/14 | 0,7857 |
| a priori Beta(8, 2) | Beta(17, 3), poids 10/20 | moyenne 0,85 |

## Effets et comportement

- **L'a priori pèse a + b essais.** L'uniforme Beta(1, 1) vaut deux essais fictifs, un succès et un échec ; Jeffreys Beta(1/2, 1/2) en vaut un. Un a priori informatif tiré d'une évaluation précédente doit être **escompté** : on le ramène à 10 ou 20 essais au lieu de recopier 100 essais d'une autre version.
- **Le choix de l'a priori ne compte qu'aux petits n.** Sur 9 sur 10, la moyenne vaut 0,8333 (uniforme), 0,8636 (Jeffreys) ou 0,85 (Beta(8, 2)) ; sur 450 sur 500, elles valent 0,8984, 0,8992 et 0,8980 : moins de deux millièmes d'écart.
- **L'estimation ne vaut jamais exactement 0 ou 1.** Tant que a et b sont positifs, la moyenne reste dans ]0, 1[ : 3 sur 3 ne donne pas « 100 % fiable ».
- **La largeur décroît comme 1/√n**, comme pour Wilson : quatre fois plus de tâches pour un intervalle deux fois plus étroit.
- **La mise à jour est incrémentale.** Deux compteurs suffisent ; l'ordre des observations ne change rien.

## Du symbole au code Python

| Notion | Variable ou fonction |
|---|---|
| paramètres a et b | `a`, `b` |
| succès s et essais n | `succes`, `n` |
| logarithme de B(a, b) | `log_beta(a, b)`, avec `math.lgamma` |
| densité f | `densite_beta(x, a, b)` |
| conjugaison | `mise_a_jour(a, b, succes, n)` |
| moyenne, mode | `moyenne_beta(a, b)`, `mode_beta(a, b)` |
| intégration de Simpson | `simpson(f, lo, hi, n)` |
| répartition F, numérique | `cdf_beta(x, a, b)` |
| répartition F, exacte pour des entiers | `cdf_beta_entiers(x, a, b)` |
| quantile, par dichotomie | `quantile_beta(u, a, b)` |
| intervalle crédible | `intervalle_credible(a, b, niveau)` |
| intervalle de Wilson (étape 7) | `wilson(succes, n)`, code canonique |
| règle de trois fréquentiste | `borne_zero_echec(n)` |
| P(p_A > p_B) | `proba_a_superieur_integrale(...)` et `proba_a_superieur_mc(...)` |

### Déroulé, ligne par ligne

**`log_beta(a, b)`** renvoie `math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)`. On ne calcule jamais B(a, b) directement : pour Beta(91, 11), B vaut environ 5,7 × 10⁻¹⁶ et les factorielles dépasseraient vite la capacité des flottants. Pour `(10, 2)`, `math.exp(log_beta(10, 2))` vaut 0,0090909, soit 1/110.

**`densite_beta(x, a, b)`** refuse a ≤ 0 ou b ≤ 0 par `ValueError`, renvoie 0 hors de [0, 1], traite les deux bords à part (la densité y vaut 0, 1/B ou l'infini selon que le paramètre dépasse, égale ou reste sous 1), puis calcule `math.exp((a - 1) * math.log(x) + (b - 1) * math.log1p(-x) - log_beta(a, b))`. `math.log1p(-x)` calcule ln(1 − x) avec précision quand x est petit. En `x = 0.8`, pour `(10, 2)` : 9 × ln 0,8 + ln 0,2 + ln 110 = ln 2,952790.

**`mise_a_jour(a, b, succes, n)`** vérifie `0 <= succes <= n` et renvoie `(a + succes, b + n - succes)` : `mise_a_jour(1, 1, 9, 10)` donne `(10, 2)`.

**`moyenne_beta`** renvoie `a / (a + b)` ; **`mode_beta`** renvoie `(a - 1) / (a + b - 2)` si `a > 1 and b > 1`, et `None` sinon, parce que le maximum est alors au bord et ne se décrit pas par cette formule.

**`simpson(f, lo, hi, n)`** découpe [lo ; hi] en `n` sous-intervalles de largeur `h`, additionne les deux bords, puis les points intérieurs avec les poids 4 (indices impairs) et 2 (indices pairs), et multiplie par `h / 3`. Avec `n = 1000` par défaut, il y a 1 001 évaluations de `f`.

**`cdf_beta(x, a, b)`** applique la démonstration, point 5 :

- `if a < 0.5 or b < 0.5` : sous ce seuil, 2a − 1 devient négatif et l'intégrande retrouve une singularité ; on refuse plutôt que de renvoyer un nombre faux.
- `if x > 0.5: return 1.0 - cdf_beta(1.0 - x, b, a)` : la symétrie. F(0,8) pour `(10, 2)` devient 1 − F(0,2) pour `(2, 10)`.
- `c = 2.0 * math.exp(-log_beta(a, b))` : la constante est calculée **une fois**, hors de l'intégrande, qui sera évaluée 1 001 fois.
- `simpson(lambda w: c * w ** (2 * a - 1) * (1.0 - w * w) ** (b - 1), 0.0, math.sqrt(x))` : l'intégrale après t = v². Pour `(2, 10)` et x = 0,2, l'intégrande vaut 2 × 110 × w³ (1 − w²)⁹, sur [0 ; 0,4472].
- `min(1.0, max(0.0, v))` : les arrondis peuvent produire 1,00000002 ; une probabilité reste dans [0, 1].

**`cdf_beta_entiers(x, a, b)`** additionne les termes binomiaux de `j = a` à `a + b - 1`, avec `math.comb`. Pour `(10, 2)`, deux termes : 11 × 0,8¹⁰ × 0,2 et 0,8¹¹. Elle sert de référence exacte pour contrôler `cdf_beta`, et d'ingrédient rapide de l'intégrale de comparaison.

**`quantile_beta(u, a, b, tol)`** part de `lo, hi = 0.0, 1.0` et, tant que `hi - lo > tol`, compare `cdf_beta(milieu, a, b)` à `u`. Avec `tol = 1e-9`, la boucle fait 30 tours. Pour `(10, 2)` et `u = 0.025`, elle s'arrête sur 0,5872.

**`intervalle_credible(a, b, niveau)`** calcule `queue = (1 - niveau) / 2`, soit 0,025, puis les deux quantiles 0,025 et 0,975.

**`wilson(succes, n)`** est la fonction canonique du parcours, recopiée sans changement. **`borne_zero_echec(n)`** renvoie `1 - alpha ** (1 / n)` : pour 300, 0,00994.

**`proba_a_superieur_mc(...)`** crée un générateur `random.Random(graine)` à part, pour ne pas dépendre de l'état global, tire `tirages` couples avec `rng.betavariate` et renvoie la fréquence des tirages où celui de A dépasse celui de B. **`proba_a_superieur_integrale(...)`** intègre `densite_beta(x, a_a, b_a) * cdf_beta_entiers(x, a_b, b_b)` sur [0 ; 1] avec 2 000 sous-intervalles.

**`main()`**, bloc par bloc.

1. 9 sur 10 depuis Beta(1, 1) donne Beta(10, 2). Le dénominateur de Bayes `constante` est calculé par `simpson` à partir de la vraisemblance binomiale `vrais` ; la densité a posteriori ainsi obtenue est comparée à `densite_beta(p, 10, 2)` en trois points. Puis la mise à jour séquentielle 5/5 puis 4/5, et l'a priori Beta(8, 2), dont la moyenne 0,85 est vérifiée contre la moyenne pondérée.
2. La moyenne 0,8333, le mode 0,9, la règle de Laplace (11/12 et 1/2), puis pass^3 prédit : `math.exp(log_beta(a11 + 3, b11) - log_beta(a11, b11))`, comparé à 11/14.
3. F(0,8) par Simpson et par la formule exacte, P(p > 0,8) = 0,677877, le contrôle par la loi de l'arc sinus, puis douze comparaisons entre `cdf_beta` et `cdf_beta_entiers` à 10⁻⁹ près, dont Beta(1, 301), très concentrée près de 0.
4. Le tableau des intervalles du point 7, l'assert sur [0,5872 ; 0,9772], le quantile de Beta(6, 1) contre 0,025^(1/6), puis la barrière bayésienne sur 45 sur 50.
5. La règle de trois pour n = 300, sous ses trois formes, et ln 20 ≈ 3.
6. Les outils X et Y du point 9, avec la borne basse de Beta(4, 1) vérifiée contre 0,05^(1/4).
7. P(p_A > p_B) par l'intégrale et par 40 000 tirages, avec l'assert `abs(mc - exacte) < 4 * ecart_type` : l'écart toléré est de quatre écarts-types, et non une égalité exacte, parce que Monte-Carlo est aléatoire.
8. Deux entrées invalides lèvent `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`log_beta(a, b)`** — Cette fonction est le géomètre qui mesure de très grands nombres sans jamais les écrire en entier, en ne manipulant que leurs logarithmes : elle reçoit les deux paramètres a et b d'une loi bêta et renvoie ln B(a, b), calculé comme ln Γ(a) + ln Γ(b) − ln Γ(a + b) grâce à `math.lgamma`, sans aucune vérification. Ce détour évite les factorielles qui dépasseraient vite la capacité des flottants ; pour (10, 2), l'exponentielle du résultat vaut 1/110. Elle sert de constante de normalisation à `densite_beta` et à `cdf_beta`, et `main` s'en sert directement pour prédire pass^3 après 10 réussites sur 10, soit exactement 11/14.

**`mise_a_jour(a, b, succes, n)`** — Celle-ci est le greffier bayésien qui tient le registre des réussites et des échecs d'un agent : elle reçoit les paramètres de la loi bêta a priori, un nombre de succès et un nombre d'essais, lève une `ValueError` si a ou b n'est pas strictement positif ou si les succès sortent de [0, n], puis renvoie le couple (a + succès, b + échecs), les paramètres de la loi a posteriori. Partant de Beta(1, 1), 9 succès sur 10 donnent Beta(10, 2), et `main` vérifie que 5 sur 5 puis 4 sur 5, appliqués l'un après l'autre, donnent le même résultat, et qu'un a priori Beta(8, 2) devient Beta(17, 3) ; les appels (0, 1, 1, 2) et (1, 1, 3, 2) sont refusés.

**`moyenne_beta(a, b)`** — Cette fonction est le point d'équilibre de la loi, l'endroit où une planche chargée selon la densité bêta tiendrait sur la pointe d'un doigt : elle reçoit a et b et renvoie a ÷ (a + b), sans aucune vérification. Pour Beta(10, 2), elle vaut 10/12, soit 0,8333, un peu en dessous du taux brut 0,9 ; avec la règle de Laplace, 10 réussites sur 10 donnent 11/12 au lieu de 1, et aucune donnée donne 0,5. Elle vaut 0,85 pour Beta(17, 3), moyenne pondérée de l'a priori 0,8 et des données 0,9, et 0,8 pour l'outil X à 3 sur 3, contre 0,892 pour l'outil Y à 90 sur 100.

**`mode_beta(a, b)`** — Celle-ci cherche le sommet de la colline que dessine la densité, la valeur du taux la plus plausible : elle reçoit a et b et renvoie (a − 1) ÷ (a + b − 2) quand les deux paramètres dépassent 1, et `None` sinon, parce que le maximum se trouve alors sur un bord de [0, 1] et ne se décrit plus par cette formule. Pour Beta(10, 2), elle renvoie 0,9, exactement le taux brut 9/10 : avec l'a priori uniforme, le mode retrouve l'estimation fréquentiste, alors que la moyenne, 0,8333, s'en écarte.

**`cdf_beta(x, a, b)`** — Cette fonction est l'arpenteur qui mesure la surface sous la densité de 0 jusqu'à x, c'est-à-dire la probabilité que le vrai taux soit au plus x : elle reçoit x, a et b, refuse par `ValueError` des paramètres inférieurs à 0,5, renvoie 0 pour x ≤ 0 et 1 pour x ≥ 1, et renvoie 1 − F(1 − x) en échangeant a et b quand x dépasse 0,5, pour toujours intégrer sur [0 ; 1/2]. Elle calcule ensuite une seule fois la constante 2 ÷ B(a, b), intègre par `simpson` l'intégrande obtenue par le changement de variable t = v², qui devient régulière, et ramène le résultat dans [0, 1]. Pour Beta(10, 2), F(0,8) vaut 0,322123, d'où P(p > 0,8) = 0,677877, et `main` la confronte à 10⁻⁹ près à la formule exacte en douze points et à la loi de l'arc sinus.

**`cdf_beta_entiers(x, a, b)`** — Celle-ci est la formule exacte, le corrigé du professeur qu'on garde pour contrôler le calcul numérique : elle reçoit x et deux paramètres entiers, pose m = a + b − 1, et renvoie la somme des termes binomiaux C(m, j) xʲ (1 − x)ᵐ⁻ʲ pour j allant de a à m, c'est-à-dire la probabilité qu'une loi binomiale de m essais au taux x compte au moins a succès. Pour Beta(10, 2), elle n'additionne que deux termes et donne 11 × 0,8¹⁰ − 10 × 0,8¹¹ = 0,322123, comme Simpson ; elle sert aussi d'ingrédient rapide et exact à `proba_a_superieur_integrale`.

**`quantile_beta(u, a, b, tol)`** — Cette fonction joue au jeu du nombre caché, en coupant chaque fois l'intervalle en deux : elle reçoit une probabilité u, a, b et une tolérance de 10⁻⁹ par défaut, lève `ValueError` si u n'est pas strictement entre 0 et 1, puis part de [0 ; 1] et, tant que l'intervalle est plus large que la tolérance, compare `cdf_beta` au milieu avec u pour garder la bonne moitié. Elle renvoie le milieu du dernier intervalle, le x tel que F(x) = u : 0,5872 pour u = 0,025 et Beta(10, 2), 0,025 à la puissance 1/6 pour Beta(6, 1), et la borne basse à 5 % de 0,473 pour l'outil X à 3 sur 3.

**`intervalle_credible(a, b, niveau)`** — Celle-ci encadre le vrai taux comme un gardien qui pose une barrière de chaque côté du troupeau, en laissant la même part de probabilité au-delà de chacune : elle reçoit a, b et un niveau de 0,95 par défaut, calcule la queue (1 − niveau) ÷ 2, soit 0,025, et renvoie le couple des quantiles 0,025 et 0,975 obtenus par `quantile_beta`. Pour Beta(10, 2), l'intervalle vaut [0,5872 ; 0,9772] ; pour 45 sur 50, [0,7859 ; 0,9556], tout proche du Wilson [0,7864 ; 0,9565] ; pour 5 sur 5, [0,5407 ; 0,9958], dont la borne haute reste sous 1, contrairement à celle de Wilson.

**`wilson(succes, n, z)`** — Cette fonction est la même fonction canonique que dans les étapes précédentes, le repère fréquentiste auquel on compare les intervalles bayésiens : elle reçoit les succès, les essais et z, 1,96 par défaut, renvoie `None` si n = 0, lève `ValueError` si les succès sortent de [0, n], et sinon renvoie les deux bornes de l'intervalle de Wilson à 95 %. Elle donne [0,5958 ; 0,9821] pour 9 sur 10, [0,7864 ; 0,9565] pour 45 sur 50 et [0,5655 ; 1] pour 5 sur 5, que `main` aligne à côté des intervalles uniforme et de Jeffreys.

**`borne_zero_echec(n, alpha)`** — Celle-ci répond à l'inquiétude du responsable conformité qui n'a vu aucune violation sur n réponses : jusqu'où le vrai taux de violation peut-il encore monter ? Elle reçoit n et le risque alpha, 0,05 par défaut, et renvoie 1 − alpha à la puissance 1/n, la règle de trois exacte, sans aucune vérification. Pour 300 réponses sans faute, elle donne 0,00994, à comparer à l'approximation 3/n = 0,01 et au quantile bayésien de Beta(1, 301), 0,00990 ; `main` vérifie que ces trois nombres se rangent dans cet ordre et que ln 20 vaut presque 3, d'où le nom de la règle.

**`main()`** — C'est le chef d'orchestre des huit démonstrations : il montre la conjugaison, où 9 succès sur 10 depuis Beta(1, 1) donnent Beta(10, 2), en la vérifiant contre un calcul de Bayes sur grille, puis la moyenne 0,8333, le mode 0,9, la règle de Laplace et le pass^3 prédit 11/14. Il calcule ensuite F(0,8) = 0,322123 de deux façons, dresse le tableau des intervalles uniforme, de Jeffreys et de Wilson, refuse la barrière bayésienne sur 45 sur 50 avec P(p ≥ 0,90) = 0,4024, applique la règle de trois à 300 réponses, classe les outils X et Y par leur borne basse, estime P(pA > pB) = 0,8684 par l'intégrale et par 40 000 tirages, et refuse enfin deux entrées invalides avant le « OK ».

```python
"""Étape 60 bis — loi bêta et petits échantillons : conjugaison, Laplace, règle de trois, intervalle crédible, P(pA > pB)."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- loi bêta
def log_beta(a: float, b: float) -> float:
    """ln B(a, b) = ln Γ(a) + ln Γ(b) − ln Γ(a + b) ; lgamma évite le dépassement de capacité."""
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def densite_beta(x: float, a: float, b: float) -> float:
    """f(x) = x^(a−1) (1 − x)^(b−1) / B(a, b), calculée en logarithmes."""
    if a <= 0 or b <= 0:
        raise ValueError("il faut a > 0 et b > 0")
    if x < 0 or x > 1:
        return 0.0
    if x == 0.0:
        return math.exp(-log_beta(a, b)) if a == 1 else (0.0 if a > 1 else math.inf)
    if x == 1.0:
        return math.exp(-log_beta(a, b)) if b == 1 else (0.0 if b > 1 else math.inf)
    return math.exp((a - 1) * math.log(x) + (b - 1) * math.log1p(-x) - log_beta(a, b))


def mise_a_jour(a: float, b: float, succes: int, n: int) -> tuple[float, float]:
    """A priori Beta(a, b), s succès sur n essais : a posteriori Beta(a + s, b + n − s)."""
    if a <= 0 or b <= 0 or not 0 <= succes <= n:
        raise ValueError("il faut a > 0, b > 0 et 0 <= succes <= n")
    return a + succes, b + n - succes


def moyenne_beta(a: float, b: float) -> float:
    return a / (a + b)


def mode_beta(a: float, b: float) -> float | None:
    """(a − 1)/(a + b − 2) ; None si le maximum est au bord (a <= 1 ou b <= 1)."""
    return (a - 1) / (a + b - 2) if a > 1 and b > 1 else None


def simpson(f, lo: float, hi: float, n: int = 1000) -> float:
    """Méthode de Simpson sur n sous-intervalles (n pair)."""
    h = (hi - lo) / n
    s = f(lo) + f(hi)
    for i in range(1, n):
        s += (4 if i % 2 else 2) * f(lo + i * h)
    return s * h / 3


def cdf_beta(x: float, a: float, b: float) -> float:
    """F(x) = P(p <= x) par intégration numérique ; on pose t = v², ce qui rend l'intégrande régulière."""
    if a < 0.5 or b < 0.5:
        raise ValueError("cette intégration demande a >= 0.5 et b >= 0.5")
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    if x > 0.5:                                     # symétrie : on intègre toujours sur [0 ; 1/2]
        return 1.0 - cdf_beta(1.0 - x, b, a)
    c = 2.0 * math.exp(-log_beta(a, b))             # dt = 2v dv, et t^(a−1) dt = 2 v^(2a−1) dv
    v = simpson(lambda w: c * w ** (2 * a - 1) * (1.0 - w * w) ** (b - 1), 0.0, math.sqrt(x))
    return min(1.0, max(0.0, v))


def cdf_beta_entiers(x: float, a: int, b: int) -> float:
    """Formule exacte pour a, b entiers : P(Bin(a + b − 1, x) >= a)."""
    m = a + b - 1
    return sum(math.comb(m, j) * x ** j * (1 - x) ** (m - j) for j in range(a, m + 1))


def quantile_beta(u: float, a: float, b: float, tol: float = 1e-9) -> float:
    """x tel que F(x) = u, par dichotomie : F croît, l'intervalle est divisé par 2 à chaque tour."""
    if not 0 < u < 1:
        raise ValueError("il faut 0 < u < 1")
    lo, hi = 0.0, 1.0
    while hi - lo > tol:
        milieu = (lo + hi) / 2
        if cdf_beta(milieu, a, b) < u:
            lo = milieu
        else:
            hi = milieu
    return (lo + hi) / 2


def intervalle_credible(a: float, b: float, niveau: float = 0.95) -> tuple[float, float]:
    """Intervalle à queues égales : (1 − niveau)/2 de probabilité de chaque côté."""
    queue = (1 - niveau) / 2
    return quantile_beta(queue, a, b), quantile_beta(1 - queue, a, b)


# ---------------------------------------------------------------- repères fréquentistes (étape 7)
def wilson(succes: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    """Intervalle de Wilson à 95 % pour une proportion ; None si n = 0."""
    if n == 0:
        return None
    if not 0 <= succes <= n:
        raise ValueError("il faut 0 <= succes <= n")
    p = succes / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    demi = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (centre - demi, centre + demi)


def borne_zero_echec(n: int, alpha: float = 0.05) -> float:
    """Règle de trois exacte (étape 7) : 0 échec sur n, borne haute 1 − alpha^(1/n) ≈ 3/n."""
    return 1 - alpha ** (1 / n)


# ---------------------------------------------------------------- comparer deux taux
def proba_a_superieur_mc(a_a: float, b_a: float, a_b: float, b_b: float, tirages: int, graine: int) -> float:
    """P(pA > pB) par Monte-Carlo : on tire les deux taux dans leurs lois a posteriori et l'on compte."""
    rng = random.Random(graine)
    gagnes = sum(1 for _ in range(tirages) if rng.betavariate(a_a, b_a) > rng.betavariate(a_b, b_b))
    return gagnes / tirages


def proba_a_superieur_integrale(a_a: int, b_a: int, a_b: int, b_b: int) -> float:
    """P(pB < pA) = ∫ fA(x) FB(x) dx : on conditionne par pA = x, puis l'indépendance donne FB(x)."""
    return simpson(lambda x: densite_beta(x, a_a, b_a) * cdf_beta_entiers(x, a_b, b_b), 0.0, 1.0, 2000)


def main() -> None:
    print("1. Conjugaison : Beta(1, 1) puis 9 succès sur 10")
    a, b = mise_a_jour(1, 1, 9, 10)
    print(f"   a posteriori Beta({a}, {b})")
    assert (a, b) == (10, 2)
    vrais = lambda p: math.comb(10, 9) * p ** 9 * (1 - p)                      # vraisemblance binomiale
    constante = simpson(lambda p: densite_beta(p, 1, 1) * vrais(p), 0.0, 1.0)   # dénominateur de Bayes
    for p in (0.5, 0.8, 0.9):
        bayes = densite_beta(p, 1, 1) * vrais(p) / constante
        print(f"   p = {p}   Bayes sur grille {bayes:.6f}   densité Beta(10, 2) {densite_beta(p, a, b):.6f}")
        assert abs(bayes - densite_beta(p, a, b)) < 1e-9
    assert mise_a_jour(*mise_a_jour(1, 1, 5, 5), 4, 5) == (10, 2)           # 5/5 puis 4/5 = 9/10 d'un coup
    a2, b2 = mise_a_jour(8, 2, 9, 10)                                       # a priori informatif : 10 tâches à 80 %
    poids = (8 + 2) / (8 + 2 + 10)
    print(f"   a priori Beta(8, 2) : Beta({a2}, {b2}), moyenne {moyenne_beta(a2, b2):.4f}"
          f" = {poids} × 0.8 + {1 - poids} × 0.9")
    assert math.isclose(moyenne_beta(a2, b2), poids * 0.8 + (1 - poids) * 0.9)

    print("2. Estimations ponctuelles")
    print(f"   9/10 : moyenne {moyenne_beta(a, b):.4f}   mode {mode_beta(a, b):.4f}   taux brut {9 / 10:.4f}")
    assert math.isclose(moyenne_beta(a, b), 10 / 12) and math.isclose(mode_beta(a, b), 0.9)
    laplace_10, laplace_0 = moyenne_beta(*mise_a_jour(1, 1, 10, 10)), moyenne_beta(*mise_a_jour(1, 1, 0, 0))
    print(f"   Laplace : 10/10 → {laplace_10:.4f}   0/0 → {laplace_0:.4f}")
    assert math.isclose(laplace_10, 11 / 12) and laplace_0 == 0.5
    a11, b11 = mise_a_jour(1, 1, 10, 10)
    pass3 = math.exp(log_beta(a11 + 3, b11) - log_beta(a11, b11))           # E[p³] = B(a + 3, b) / B(a, b)
    print(f"   10/10 : pass^3 prédit {pass3:.4f} (le taux brut prédirait 1)")
    assert math.isclose(pass3, 11 / 14)

    print("3. Fonction de répartition par intégration numérique")
    num, exact = cdf_beta(0.8, 10, 2), cdf_beta_entiers(0.8, 10, 2)
    print(f"   F(0.8) de Beta(10, 2) : Simpson {num:.6f}   exacte 11·0.8¹⁰ − 10·0.8¹¹ = {exact:.6f}")
    print(f"   P(p > 0.8 | 9 sur 10) = {1 - num:.6f}")
    assert abs(num - exact) < 1e-9 and math.isclose(exact, 11 * 0.8 ** 10 - 10 * 0.8 ** 11)
    arcsin = 2 / math.pi * math.asin(math.sqrt(0.2))                        # Beta(1/2, 1/2) : loi de l'arc sinus
    print(f"   Beta(0.5, 0.5), F(0.2) : Simpson {cdf_beta(0.2, 0.5, 0.5):.6f}   arc sinus {arcsin:.6f}")
    assert abs(cdf_beta(0.2, 0.5, 0.5) - arcsin) < 1e-9
    for (aa, bb) in ((46, 6), (42, 10), (1, 301)):
        for x in (0.005, 0.2, 0.85, 0.95):
            assert abs(cdf_beta(x, aa, bb) - cdf_beta_entiers(x, aa, bb)) < 1e-9

    print("4. Intervalle crédible à 95 % contre Wilson")
    for s, n in ((9, 10), (45, 50), (5, 5)):
        lo_u, hi_u = intervalle_credible(*mise_a_jour(1, 1, s, n))
        lo_w, hi_w = wilson(s, n)
        lo_j = quantile_beta(0.025, s + 0.5, n - s + 0.5)
        hi_j = 1.0 if s == n else quantile_beta(0.975, s + 0.5, n - s + 0.5)   # convention : 1 si aucun échec
        print(f"   {s:>2}/{n:<2}  uniforme [{lo_u:.4f} ; {hi_u:.4f}]   Jeffreys [{lo_j:.4f} ; {hi_j:.4f}]"
              f"   Wilson [{lo_w:.4f} ; {hi_w:.4f}]")
        assert lo_u < s / n and (hi_u < hi_w if s == n else True)
    lo_u, hi_u = intervalle_credible(10, 2)
    assert (round(lo_u, 4), round(hi_u, 4)) == (0.5872, 0.9772)
    assert math.isclose(quantile_beta(0.025, 6, 1), 0.025 ** (1 / 6), abs_tol=1e-8)   # F(x) = x⁶
    p_seuil = 1 - cdf_beta(0.90, 46, 6)
    print(f"   45/50 : P(p >= 0.90) = {p_seuil:.4f}, barrière bayésienne à 0.95 refusée")
    assert p_seuil < 0.95

    print("5. Règle de trois : 0 violation sur 300 réponses")
    n0 = 300
    q_freq, q_bayes = borne_zero_echec(n0), quantile_beta(0.95, 1, n0 + 1)
    print(f"   3/n = {3 / n0:.5f}   exacte 1 − 0.05^(1/n) = {q_freq:.5f}   Beta(1, 301) à 95 % = {q_bayes:.5f}")
    assert abs(q_bayes - (1 - 0.05 ** (1 / (n0 + 1)))) < 1e-8 and q_bayes < q_freq < 3 / n0
    assert abs(math.log(20) - 3) < 0.005                                     # d'où le « 3 »

    print("6. Petits échantillons : classer par la borne basse, pas par le taux brut")
    for nom, s, n in (("outil X", 3, 3), ("outil Y", 90, 100)):
        aa, bb = mise_a_jour(1, 1, s, n)
        print(f"   {nom} {s}/{n}   brut {s / n:.3f}   moyenne {moyenne_beta(aa, bb):.3f}"
              f"   borne basse 5 % {quantile_beta(0.05, aa, bb):.3f}")
    assert quantile_beta(0.05, 4, 1) < quantile_beta(0.05, 91, 11)
    assert math.isclose(quantile_beta(0.05, 4, 1), 0.05 ** 0.25, abs_tol=1e-8)

    print("7. Deux versions : 45/50 contre 41/50, échantillons indépendants")
    exacte = proba_a_superieur_integrale(46, 6, 42, 10)
    mc = proba_a_superieur_mc(46, 6, 42, 10, tirages=40_000, graine=60)
    ecart_type = math.sqrt(exacte * (1 - exacte) / 40_000)
    print(f"   P(pA > pB) : intégrale {exacte:.4f}   Monte-Carlo {mc:.3f} (écart-type {ecart_type:.4f})")
    assert abs(mc - exacte) < 4 * ecart_type and 0.86 < exacte < 0.87
    print(f"   seuil de décision 0.95 : {'A meilleure' if exacte >= 0.95 else 'pas de conclusion'}")

    print("8. Entrées invalides")
    for args in ((0, 1, 1, 2), (1, 1, 3, 2)):
        try:
            mise_a_jour(*args)
        except ValueError:
            print(f"   mise_a_jour{args} → ValueError")
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Conjugaison : Beta(1, 1) puis 9 succès sur 10
   a posteriori Beta(10, 2)
   p = 0.8   Bayes sur grille 2.952790   densité Beta(10, 2) 2.952790
   a priori Beta(8, 2) : Beta(17, 3), moyenne 0.8500 = 0.5 × 0.8 + 0.5 × 0.9
…
   10/10 : pass^3 prédit 0.7857 (le taux brut prédirait 1)
…
   F(0.8) de Beta(10, 2) : Simpson 0.322123   exacte 11·0.8¹⁰ − 10·0.8¹¹ = 0.322123
   P(p > 0.8 | 9 sur 10) = 0.677877
4. Intervalle crédible à 95 % contre Wilson
    9/10  uniforme [0.5872 ; 0.9772]   Jeffreys [0.6187 ; 0.9890]   Wilson [0.5958 ; 0.9821]
   45/50  uniforme [0.7859 ; 0.9556]   Jeffreys [0.7946 ; 0.9608]   Wilson [0.7864 ; 0.9565]
    5/5   uniforme [0.5407 ; 0.9958]   Jeffreys [0.6206 ; 1.0000]   Wilson [0.5655 ; 1.0000]
   45/50 : P(p >= 0.90) = 0.4024, barrière bayésienne à 0.95 refusée
…
   3/n = 0.01000   exacte 1 − 0.05^(1/n) = 0.00994   Beta(1, 301) à 95 % = 0.00990
…
   outil X 3/3   brut 1.000   moyenne 0.800   borne basse 5 % 0.473
   outil Y 90/100   brut 0.900   moyenne 0.892   borne basse 5 % 0.838
…
   P(pA > pB) : intégrale 0.8684   Monte-Carlo 0.867 (écart-type 0.0017)
…
OK — toutes les vérifications sont passées.
```

La ligne Monte-Carlo dépend de l'algorithme de `random.betavariate` ; d'une version de Python à l'autre, son troisième chiffre peut bouger, et c'est pourquoi l'assert compare à l'intégrale avec une tolérance de quatre écarts-types.

Ce que le programme montre : avec deux additions, une intégrale de Simpson et une dichotomie, on obtient tout ce qu'une bibliothèque de statistiques fournirait sur un taux de réussite. Chaque nombre est contrôlé deux fois, par une formule exacte et par le calcul numérique.

## Squelette algorithmique

Trois algorithmes. ÉVALUER_PETIT_ÉCHANTILLON prend un a priori, des résultats d'essais et un seuil, et rend la loi a posteriori, son résumé et la décision de la barrière bayésienne. RÉPARTITION_ET_QUANTILE calcule F par intégration numérique et l'inverse par dichotomie : c'est le moteur des deux autres. COMPARER_DEUX_TAUX estime la probabilité qu'une version soit meilleure que l'autre, sur deux échantillons indépendants.

```text
ALGORITHME ÉVALUER_PETIT_ÉCHANTILLON
ENTRÉES : a priori (a, b) ; résultats r₁ … rₙ (1 = succès) ; seuil τ ; niveau exigé c (0,95)
SORTIE  : (a', b', moyenne, intervalle crédible, P(p ≥ τ), décision)

  SI a ≤ 0 OU b ≤ 0 ALORS ERREUR FIN SI
  a' ← a ; b' ← b
  POUR i de 1 à n FAIRE                         ▷ deux compteurs, l'ordre ne compte pas
      SI rᵢ = 1 ALORS a' ← a' + 1 SINON b' ← b' + 1 FIN SI
  FIN POUR
  moyenne ← a' / (a' + b')
  intervalle ← [ QUANTILE(0,025 ; a', b') ; QUANTILE(0,975 ; a', b') ]
  p_seuil ← 1 − RÉPARTITION(τ ; a', b')
  SI p_seuil ≥ c ALORS décision ← DÉPLOYER SINON décision ← REFUSER FIN SI
  RETOURNER (a', b', moyenne, intervalle, p_seuil, décision)
```

```text
ALGORITHME RÉPARTITION_ET_QUANTILE
ENTRÉES : x dans [0, 1] ou niveau u dans ]0, 1[ ; paramètres a ≥ 0,5 et b ≥ 0,5 ; M sous-intervalles (pair)
SORTIE  : F(x), ou x tel que F(x) = u

RÉPARTITION(x ; a, b)
  SI x ≤ 0 ALORS RETOURNER 0 FIN SI
  SI x ≥ 1 ALORS RETOURNER 1 FIN SI
  SI x > 1/2 ALORS RETOURNER 1 − RÉPARTITION(1 − x ; b, a) FIN SI     ▷ symétrie
  c ← 2 / B(a, b)                                ▷ B calculée par ln Γ
  g(v) ← c × v^(2a − 1) × (1 − v²)^(b − 1)       ▷ changement de variable t = v²
  h ← √x / M ; S ← g(0) + g(√x)
  POUR i de 1 à M − 1 FAIRE
      SI i impair ALORS S ← S + 4 g(i h) SINON S ← S + 2 g(i h) FIN SI
  FIN POUR
  RETOURNER min(1, max(0, S × h / 3))

QUANTILE(u ; a, b)
  lo ← 0 ; hi ← 1
  TANT QUE hi − lo > tolérance FAIRE              ▷ invariant : F(lo) < u ≤ F(hi)
      m ← (lo + hi) / 2
      SI RÉPARTITION(m ; a, b) < u ALORS lo ← m SINON hi ← m FIN SI
  FIN TANT QUE
  RETOURNER (lo + hi) / 2
```

```text
ALGORITHME COMPARER_DEUX_TAUX
ENTRÉES : (s_A, n_A) et (s_B, n_B) sur des échantillons INDÉPENDANTS ; a priori (a, b) ; N tirages ; graine
SORTIE  : estimation de P(p_A > p_B)

  (a_A, b_A) ← (a + s_A, b + n_A − s_A) ; (a_B, b_B) ← (a + s_B, b + n_B − s_B)
  générateur ← nouveau générateur initialisé avec graine
  gagnés ← 0
  POUR k de 1 à N FAIRE
      x_A ← tirage Beta(a_A, b_A) ; x_B ← tirage Beta(a_B, b_B)
      SI x_A > x_B ALORS gagnés ← gagnés + 1 FIN SI
  FIN POUR
  RETOURNER gagnés / N                          ▷ écart-type ≈ √(P(1 − P) / N)
```

**Complexité :** ÉVALUER_PETIT_ÉCHANTILLON fait un passage sur les n résultats, en O(n) et O(1) en mémoire, plus trois appels au moteur. RÉPARTITION coûte M + 1 évaluations de l'intégrande, chacune en O(1) (deux puissances), soit O(M) en temps et O(1) en mémoire ; la récursion de symétrie n'a lieu qu'une fois. QUANTILE fait ⌈log₂(1/tolérance)⌉ tours, chacun d'une RÉPARTITION : O(M log(1/tolérance)), soit 30 × 1 001 évaluations pour M = 1 000 et une tolérance de 10⁻⁹, environ 30 000 opérations. Un intervalle crédible coûte deux quantiles. La formule exacte pour des paramètres entiers coûte O(a + b) termes, ce qui la rend préférable quand a + b est petit. COMPARER_DEUX_TAUX fait 2N tirages ; chaque tirage bêta en demande deux de la loi gamma, d'un coût moyen constant : O(N) en temps, O(1) en mémoire, pour une erreur qui décroît seulement en 1/√N. L'intégrale de comparaison coûte O(M × (a_B + b_B)) et donne une réponse exacte à 10⁻⁹ près : on la préfère quand les paramètres sont entiers, Monte-Carlo servant quand on compare plus de deux versions ou des quantités plus complexes.

**Du squelette au code :** la boucle de comptage d'ÉVALUER_PETIT_ÉCHANTILLON est condensée dans `mise_a_jour(a, b, succes, n)`, qui reçoit directement le nombre de succès ; la moyenne est `moyenne_beta`, l'intervalle `intervalle_credible(a, b, niveau)`, et la barrière la ligne `p_seuil = 1 - cdf_beta(0.90, 46, 6)` du bloc 4 de `main()`, comparée à 0,95. RÉPARTITION est `cdf_beta(x, a, b)` : la symétrie est le `if x > 0.5`, la constante c est `c = 2.0 * math.exp(-log_beta(a, b))`, g est la `lambda w`, la boucle de Simpson est la fonction `simpson`, et le `min(1, max(0, …))` est la dernière ligne. QUANTILE est `quantile_beta(u, a, b, tol)`, ligne pour ligne. COMPARER_DEUX_TAUX est `proba_a_superieur_mc`, dont le générateur est `random.Random(graine)` et le tirage `rng.betavariate` ; sa version exacte est `proba_a_superieur_integrale`.

## Cas d'usage réels aux Émirats

Les volumes, les taux et les seuils ci-dessous sont illustratifs ; seules les règles réglementaires citées sont réelles, à confirmer avec le texte en vigueur.

### Banque — une catégorie rare, dix dossiers seulement

Une banque de détail de Dubaï fait évoluer son agent de pré-instruction des prêts personnels, et veut savoir si la nouvelle version traite correctement les **retraités**, pour qui la règle de la CBUAE plafonne l'endettement total à 30 % du revenu au lieu de 50 %. Le jeu de test ne contient que dix dossiers de retraités anonymisés, parce que la catégorie est rare, et la version en réussit neuf. Le taux brut, 0,90, ne veut presque rien dire : avec un a priori uniforme, la loi a posteriori Beta(10, 2) donne une probabilité de 0,68 seulement que le vrai taux dépasse 80 %, et de 0,51 qu'il dépasse 85 %. L'équipe dispose de l'évaluation de la version précédente, à environ 80 % sur cette catégorie ; elle l'escompte à dix dossiers, soit un a priori Beta(8, 2), et obtient Beta(17, 3), de moyenne 0,85, avec un intervalle crédible de 0,67 à 0,97. La décision est de ne pas déployer la version pour cette catégorie avant d'avoir construit vingt dossiers de plus, parce qu'une erreur sur le plafond de 30 % expose la banque à un dossier non conforme. L'indicateur suivi est P(p ≥ 0,90) par catégorie de clients, mis à jour à chaque nouveau dossier noté.

### Assurance — zéro violation n'est pas un taux nul

Un assureur auto et santé, supervisé par la CBUAE, interdit à son agent de promettre une prise en charge avant la décision du gestionnaire. Sur 300 conversations de test, le vérificateur ne trouve aucune promesse interdite. La règle de trois dit ce que ce résultat prouve : un taux de violation d'au plus 0,99 % environ, à 95 %, que l'on raisonne en fréquentiste (0,00994) ou avec un a priori uniforme (0,00990). Or l'assureur sert des milliers de conversations par mois : 1 % de violations en ferait des dizaines. Pour affirmer un taux inférieur à 0,1 %, il faudrait environ 2 995 conversations sans faute, ce que le jeu de test ne pourra pas fournir. L'assureur ajoute donc un filtre de sortie déterministe qui bloque la formule interdite, et garde la mesure pour suivre la tendance. L'indicateur suivi est la borne haute de la règle de trois, recalculée chaque semaine sur les conversations échantillonnées.

### Crypto — des alertes manquées sur des incidents rares

Une plateforme d'actifs virtuels agréée par la VARA évalue l'agent qui doit lever une alerte quand un pool de liquidité passe sous son seuil. Les vrais incidents sont rares : le jeu n'en contient que 25, rejoués à partir de journaux anonymisés, et l'agent n'en manque aucun. Avec un a priori uniforme sur le taux d'alertes manquées, la loi a posteriori est Beta(1, 26), et la borne haute à 95 % vaut 1 − 0,05^(1/26) ≈ 0,109 : on ne peut pas exclure qu'un incident sur neuf passe inaperçu. Pour descendre la borne à 2 %, il faut 148 incidents sans échec. La plateforme fabrique donc des incidents synthétiques, en abaissant artificiellement la réserve de pools de test, jusqu'à atteindre ce volume. Un manque de liquidité non signalé empêche d'honorer les retraits, ce qui est précisément le risque que la VARA attend de voir maîtrisé. L'indicateur suivi est la borne haute du taux d'alertes manquées, publiée avec le nombre d'incidents qui la fonde.

### Immobilier — un test A/B entre deux agents d'estimation

Une agence qui opère à Dubaï et à Abu Dhabi fait tourner deux agents d'estimation en parallèle : chaque demande de client est servie par l'un ou l'autre, au hasard, et une estimation est réussie si elle tombe à moins de 10 % du prix de transaction constaté ensuite. Après 50 transactions de chaque côté, A en réussit 45 et B 41. Les échantillons sont indépendants (les biens ne sont pas les mêmes), donc McNemar ne s'applique pas, et l'agence calcule P(p_A > p_B) avec deux lois a posteriori Beta(46, 6) et Beta(42, 10) : 0,868 par intégration, 0,867 par 40 000 tirages. Le seuil de décision fixé à l'avance est 0,95 : le test continue, au lieu de basculer tout le trafic sur A après une différence qui pourrait venir du hasard. L'enjeu est concret pour les acheteurs, qui paient en plus 4 % de frais de transfert au DLD sur le prix. L'indicateur suivi est P(p_A > p_B), recalculé chaque semaine, avec la règle d'arrêt écrite avant le début du test.

### RH — choisir entre deux outils de translittération

Un cabinet RH présent dans plusieurs émirats fait vérifier par un agent la cohérence des noms entre le contrat enregistré au MOHRE, la demande de visa et le dossier WPS. Les noms arabes sont translittérés de plusieurs façons, et l'agent dispose de deux outils de rapprochement. Le premier, ajouté récemment, a réussi ses 3 essais ; le second a réussi 90 essais sur 100. Le routeur initial, qui choisissait l'outil au meilleur taux brut, envoyait tout au premier. Le routeur corrigé classe par la borne basse à 5 % de la loi a posteriori : 0,473 pour le premier, 0,838 pour le second, qui reprend la main tant que le nouvel outil n'a pas fait ses preuves. Une variante, l'échantillonnage de Thompson, tire un taux dans chaque loi à chaque dossier et choisit le plus grand : le nouvel outil reçoit alors un peu de trafic et accumule des essais. Un nom mal rapproché bloque un visa ou un versement de salaire. L'indicateur suivi est le taux de rapprochements corrects par outil, avec la taille d'échantillon qui le fonde.

### Secteur public — une langue peu représentée dans la semaine

Un service public en ligne accessible par UAE Pass répond en arabe et en anglais, et l'équipe note chaque semaine un échantillon de conversations. Cette semaine, l'échantillon arabe ne compte que 20 conversations, dont 14 jugées correctes : le taux brut de 0,70 et l'intervalle de Wilson [0,48 ; 0,85] déclencheraient une alerte. L'équipe utilise comme a priori le mois précédent, escompté à 20 conversations à 90 %, soit Beta(18, 2) ; la loi a posteriori Beta(32, 8) a pour moyenne 0,80, et P(p < 0,85) vaut 0,78. Sans a priori, elle vaudrait 0,97. Les deux chiffres disent la même chose avec une force différente : il y a probablement une baisse, mais la semaine seule ne la prouve pas. L'équipe double l'échantillon arabe de la semaine suivante au lieu de revenir sur le déploiement, et vérifie que l'échantillonnage respecte la PDPL. L'indicateur suivi est P(p < 0,85) par langue, avec une alerte au-dessus de 0,9.

## Pièges et limites

- **Recopier un a priori trop lourd.** Un a priori Beta(90, 10) tiré d'une ancienne version pèse 100 essais et écrase dix nouvelles observations ; on l'escompte, ou l'on montre le résultat sous l'a priori uniforme à côté.
- **Lire l'intervalle crédible comme un intervalle de confiance, ou l'inverse.** Le premier est une probabilité sur p sachant les données ; le second une propriété de la procédure. Ils coïncident à peu près pour n grand, pas pour 5 sur 5.
- **Comparer deux versions jouées sur les mêmes tâches avec des lois indépendantes.** L'appariement est perdu ; on utilise McNemar (étape 60), ou un modèle par tâche.
- **Intégrer une densité singulière sans changement de variable.** Pour a < 1, la densité est infinie en 0 et Simpson se trompe ; la substitution t = v² règle les paramètres ≥ 0,5, et le code refuse les autres.
- **Supposer les essais indépendants.** Si les tâches viennent de quelques familles très corrélées, dix tâches valent moins que dix essais : la loi bêta est alors trop confiante.

### Exercice feuille blanche

1. Sans regarder le code, écrire `mise_a_jour`, `cdf_beta_entiers` et `quantile_beta` (avec la formule exacte), puis retrouver l'intervalle crédible [0,5872 ; 0,9772] de 9 sur 10.
2. Prédire, puis vérifier : après 20 réussites sur 20 avec l'a priori uniforme, que valent la règle de Laplace et le pass^3 prédit ? (Réponse : 21/22 ≈ 0,9545 et 21/24 = 0,875, par simplification en cascade.) Que vaut la borne basse à 5 % ? (Réponse : F(x) = x²¹, donc 0,05^(1/21) ≈ 0,867.)
3. Trouver le bug : une variante de `mise_a_jour` renvoie `(a + succes, b + n)`. Que devient la moyenne après 9 sur 10, et dans quel sens se trompe-t-elle ? (Réponse : Beta(10, 11), moyenne 0,476 : les succès sont comptés aussi comme des échecs.)

## Pour aller plus loin

L'échantillonnage de Thompson, cité dans le cas RH, transforme la loi bêta en routeur qui apprend : c'est la solution bayésienne classique du problème du bandit à plusieurs bras. Les tests séquentiels bayésiens arrêtent une évaluation dès que P(p ≥ τ) franchit 0,95 ou tombe sous 0,05, au lieu de fixer n à l'avance ; il faut alors écrire la règle d'arrêt avant de commencer. Quand les tâches se regroupent en familles, un modèle hiérarchique (une loi bêta par famille, dont les paramètres sont eux-mêmes estimés) partage l'information entre familles sans les confondre. Enfin, la loi de Dirichlet généralise la loi bêta à plus de deux issues, par exemple réussite, échec et escalade.

> Étape 60 bis du parcours · Prérequis : [Agent Goal Accuracy](<60-Evaluation-Formule-Agent-Goal-Accuracy.md>) · Suite : [Mean Average Precision](<61-Evaluation-Formule-MAP.md>)
