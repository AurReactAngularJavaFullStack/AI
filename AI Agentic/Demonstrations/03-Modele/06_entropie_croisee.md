# 06 — Entropie croisée : démonstrations

> Fiche : [06 — Entropie croisée](<../../Images/03-Modele/06_entropie_croisee.md>) · Image : `06_entropie_croisee.jpg` · Leçon : [Étape 52 — Perplexité](<../../10-Evaluation/52-Perplexite-LLM.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4. Ici, log désigne le logarithme naturel ln.

## La formule

$$
L = -\sum_{i} y_i \log(p_i)
$$

yᵢ est la cible (souvent 1 sur le bon token, 0 ailleurs), pᵢ la probabilité prédite par le modèle.

## Les symboles, un par un

$$
L
$$

La perte d'entropie croisée d'une prédiction, un réel ≥ 0 mesuré en nats (logarithme naturel), éventuellement +∞. Elle est calculée par `entropie_croisee(y, p)`.

$$
i
$$

L'indice d'une classe, c'est-à-dire d'un token du vocabulaire, de 1 à k où k est la taille du vocabulaire (des dizaines de milliers pour un LLM, 2 ou 3 dans les exemples). Dans le programme, c'est la position dans les listes `y` et `p`.

$$
y_i
$$

La cible pour la classe i, un réel de [0 ; 1], avec ∑ yᵢ = 1. Le plus souvent, elle vaut 1 sur le bon token et 0 ailleurs (cible « one-hot ») ; pour une cible souple (distillation, lissage), elle répartit la masse. Variable `y`.

$$
p_i
$$

La probabilité que le modèle donne à la classe i, un réel de ]0 ; 1] en sortie de softmax, avec ∑ pᵢ = 1. Variable `p`, calculée par `softmax(z)`.

$$
p_b
$$

La probabilité donnée au bon token b quand la cible est one-hot. Dans un lot, la liste de ces probabilités s'appelle `lot`.

$$
z_i
$$

Le logit de la classe i : le score brut du modèle avant la softmax, un réel quelconque. Variable `z`.

$$
\bar{L}
$$

La perte moyenne sur les n tokens d'un lot, en nats par token ; son exponentielle est la perplexité (fiche 32). Variable `moy`, calculée aussi par `perte_moyenne`.

$$
H(y)
$$

L'entropie de la cible, −∑ yᵢ ln yᵢ, un réel ≥ 0 ; elle vaut 0 pour une cible one-hot. C'est la plus petite perte atteignable (démonstration 3). Dans le programme : `entropie_croisee(y, y)`.

$$
D_{KL}(y \parallel p)
$$

La divergence de Kullback-Leibler de la cible au modèle, un réel ≥ 0 (fiche 17) : l'excès de perte dû au modèle. Dans le programme : la différence `L - H`.

## Le mécanisme, avant les preuves

Ce qui entre : une cible y et une prédiction p, deux distributions sur les mêmes k classes. Le logarithme transforme chaque probabilité en une « surprise » : −ln pᵢ vaut 0 quand pᵢ = 1, grandit quand pᵢ baisse et devient infini quand pᵢ tend vers 0. Le produit par yᵢ choisit quelles surprises comptent, et dans quelle proportion : avec une cible one-hot, seule la surprise du bon token reste. La somme additionne ces surprises pondérées, et le signe moins rend le résultat positif, parce que le logarithme d'une probabilité est négatif. Pourquoi un logarithme plutôt que 1 − pᵢ ? D'abord parce que la probabilité d'une phrase est un produit de probabilités (fiche 23) et que le logarithme change ce produit en somme : la perte d'un texte est la somme des pertes de ses tokens. Ensuite parce que le logarithme punit sans limite une erreur sûre d'elle : diviser la probabilité du bon token par 2 ajoute toujours ln 2 ≈ 0,69315, que l'on parte de 0,9 ou de 0,01. Enfin parce que, combiné à la softmax, il donne un gradient très simple, p − y (démonstration 4), et que son minimum est atteint quand le modèle reproduit la cible (démonstration 3). Ce qui sort : un nombre en nats, qui dit combien le modèle a été surpris par la bonne réponse.

Le petit film chiffré, avec une cible one-hot, sur trois probabilités du bon token :

| Probabilité du bon token | Logarithme | Perte |
|---|---|---|
| 0,9 | −0,10536 | 0,10536 |
| 0,5 | −0,69315 | 0,69315 |
| 0,05 | −2,99573 | 2,99573 |

Passer de 0,9 à 0,5 coûte 0,58779 nat ; passer de 0,5 à 0,05, soit une division par 10, coûte 2,30259 nats, exactement ln 10. Un modèle qui place 5 % sur la bonne réponse paie environ 28,4 fois plus qu'un modèle qui en place 90 % (2,99573 / 0,10536). Pour un développeur Java, on peut voir la perte comme un compteur de « surprise » : chaque prédiction ajoute son coût, et une seule prédiction fausse et sûre d'elle peut faire exploser le total.

## Démonstration 1 — Avec une cible one-hot, il ne reste qu'un terme

**Ce qu'on démontre.** Si y vaut 1 sur le bon token b et 0 ailleurs, alors :

$$
L = -\log p_b
$$

**L'idée.** Dans la somme, chaque terme est multiplié par sa cible : les termes de cible nulle disparaissent, et il ne reste que celui du bon token, multiplié par 1.

**La preuve, pas à pas.**

**Étape 1.** On sépare le terme b des autres termes de la somme, parce que la somme est finie et que l'ordre de ses termes ne compte pas :

$$
L = -y_b \log p_b - \sum_{i \ne b} y_i \log p_i
$$

**Étape 2.** On remplace yᵦ par 1 et chaque yᵢ (i ≠ b) par 0, parce que la cible est one-hot ; chaque terme 0 × log pᵢ vaut 0, parce que log pᵢ est fini dès que pᵢ > 0 :

$$
L = -1 \times \log p_b - 0 = -\log p_b
$$

∎

**Vérification chiffrée.** Avec y = (0 ; 1 ; 0) et p = (0,2 ; 0,7 ; 0,1), la somme complète vaut −(0 × ln 0,2 + 1 × ln 0,7 + 0 × ln 0,1) = −ln 0,7 ≈ 0,35667. Contre-exemple quand la cible n'est pas one-hot : avec une cible lissée y = (0,05 ; 0,9 ; 0,05), les trois termes comptent, et L = −(0,05 ln 0,2 + 0,9 ln 0,7 + 0,05 ln 0,1) ≈ 0,51661, qui n'est plus −ln 0,7.

**Ce que la preuve révèle du mécanisme.** Avec une cible one-hot, la perte ne regarde que la probabilité du bon token : la façon dont le modèle répartit le reste de la masse entre les mauvais tokens n'apparaît pas dans L. Elle apparaît seulement à travers la normalisation de la softmax, puisque toute masse posée ailleurs est retirée au bon token.

**Conséquence pour un agent.** Pour noter une réponse de modèle, il suffit des log-probabilités des tokens réellement écrits, que certaines API exposent : pas besoin de la distribution entière. Le programme ne somme que sur les yᵢ > 0, ce qui évite de calculer ln 0 pour les classes absentes.

## Démonstration 2 — La perte est positive, et nulle seulement si le modèle est sûr et juste

**Ce qu'on démontre.** Si 0 < pᵦ ≤ 1, alors

$$
L = -\log p_b \ge 0, \qquad L = 0 \iff p_b = 1, \qquad \lim_{p_b \to 0^+} L = +\infty
$$

**L'idée.** Le logarithme est négatif sur ]0 ; 1[ et nul en 1 ; le signe moins le rend positif. Près de 0, le logarithme plonge vers −∞, donc la perte monte sans limite.

**La preuve, pas à pas.**

**Étape 1.** La fonction ln est strictement croissante et ln 1 = 0 ; donc pᵦ ≤ 1 donne ln pᵦ ≤ ln 1 = 0, parce qu'une fonction croissante conserve l'ordre.

**Étape 2.** On change de signe, ce qui renverse l'inégalité :

$$
-\log p_b \ge 0
$$

**Étape 3.** L'égalité −ln pᵦ = 0 équivaut à ln pᵦ = 0, donc à pᵦ = e⁰ = 1, parce que ln est injective (strictement croissante).

**Étape 4.** Quand pᵦ tend vers 0 par valeurs positives, ln pᵦ tend vers −∞, donc −ln pᵦ tend vers +∞. ∎

**Vérification chiffrée.** −ln 1 = 0 ; −ln 0,01 ≈ 4,60517 ; −ln 0,001 ≈ 6,90776 : chaque division par 10 ajoute ln 10 ≈ 2,30259. Contre-exemple quand l'hypothèse pᵦ ≤ 1 manque : si un bug de normalisation produit une « probabilité » de 1,2, la perte vaut −ln 1,2 ≈ −0,18232 < 0. Une perte négative est donc le signe d'un bug en amont.

**Ce que la preuve révèle du mécanisme.** La perte est un coût de surprise sans plafond : elle est clémente avec les erreurs modestes et impitoyable avec les erreurs sûres d'elles. Une seule prédiction à 0,001 coûte autant que 66 prédictions à 0,9 (6,90776 / 0,10536 ≈ 65,6).

**Conséquence pour un agent.** Le programme refuse une probabilité nulle posée sur une cible (`ValueError`) au lieu de renvoyer l'infini en silence. En production, on vérifie que les probabilités lues dans une API sont dans ]0 ; 1] : une perte négative ou infinie dans un tableau de bord est une alerte de qualité des données.

## Démonstration 3 — Le minimum est atteint quand la prédiction égale la cible

**Ce qu'on démontre.** Pour deux distributions y et p sur les mêmes classes, avec pᵢ > 0 partout où yᵢ > 0 :

$$
L(y, p) = H(y) + D_{KL}(y \parallel p) \ge H(y), \qquad \text{égalité si et seulement si } p = y
$$

**L'idée.** On sépare la perte en deux morceaux : l'incertitude propre de la cible, que personne ne peut descendre, et l'écart entre le modèle et la cible, qui est toujours positif. L'outil est l'inégalité ln x ≤ x − 1.

**La preuve, pas à pas.**

**Étape 1.** On montre ln x ≤ x − 1 pour x > 0. La fonction g(x) = x − 1 − ln x a pour dérivée 1 − 1/x, négative sur ]0 ; 1[ et positive sur ]1 ; +∞[ ; g décroît puis croît, donc son minimum est g(1) = 0, et g(x) ≥ 0 partout.

**Étape 2.** On ajoute et on retire ∑ yᵢ ln yᵢ, parce que log pᵢ = log yᵢ − log(yᵢ/pᵢ) pour les yᵢ > 0 :

$$
-\sum_i y_i \log p_i = -\sum_i y_i \log y_i + \sum_i y_i \log \frac{y_i}{p_i} = H(y) + D_{KL}(y \parallel p)
$$

**Étape 3.** On applique l'étape 1 à x = pᵢ/yᵢ, terme par terme, parce que chaque yᵢ > 0 conserve l'inégalité :

$$
-D_{KL}(y \parallel p) = \sum_i y_i \log \frac{p_i}{y_i} \le \sum_i y_i \left( \frac{p_i}{y_i} - 1 \right) = \sum_i p_i - \sum_i y_i \le 1 - 1 = 0
$$

**Étape 4.** Donc la KL est positive ou nulle, et L ≥ H(y). L'égalité exige pᵢ/yᵢ = 1 pour chaque yᵢ > 0, parce que ln x = x − 1 seulement en x = 1 ; donc p = y. ∎

**Vérification chiffrée.** Avec y = (0,5 ; 0,5) et p = (0,9 ; 0,1) : L = 0,5 × 0,10536 + 0,5 × 2,30259 = 0,05268 + 1,15129 = 1,20397 ; H(y) = ln 2 ≈ 0,69315 ; KL = 1,20397 − 0,69315 = 0,51083 > 0. L'inégalité ln x ≤ x − 1 se vérifie en x = 0,1 ; 0,5 ; 1 ; 2 ; 7 dans le programme.

**Ce que la preuve révèle du mécanisme.** Minimiser l'entropie croisée revient à minimiser la KL, puisque H(y) ne dépend pas du modèle : l'entraînement pousse le modèle à reproduire la distribution cible, ni plus sûre ni moins sûre qu'elle. Avec une cible one-hot, H(y) = 0 et la perte est toute entière de la KL.

**Conséquence pour un agent.** Quand on distille un grand modèle vers un petit, la perte ne descendra jamais sous H(y) : on suit donc la KL, pas la perte brute, pour savoir quand arrêter (cas 3).

## Démonstration 4 — Le gradient par rapport aux logits vaut p − y

**Ce qu'on démontre.** Si p = softmax(z) et ∑ yᵢ = 1, alors pour chaque classe k :

$$
\frac{\partial L}{\partial z_k} = p_k - y_k
$$

**L'idée.** La perte se réécrit comme « log de la somme des exponentielles moins le logit cible ». La dérivée du premier morceau est exactement la softmax ; celle du second est la cible.

**La preuve, pas à pas.**

**Étape 1.** On remplace log pᵢ par sa valeur, parce que pᵢ = e^(zᵢ) / ∑ⱼ e^(zⱼ) :

$$
\log p_i = z_i - \log \sum_j e^{z_j}
$$

**Étape 2.** On reporte dans L et on sort le second morceau de la somme, parce qu'il ne dépend pas de i et que ∑ yᵢ = 1 :

$$
L = -\sum_i y_i z_i + \Big( \sum_i y_i \Big) \log \sum_j e^{z_j} = -\sum_i y_i z_i + \log \sum_j e^{z_j}
$$

**Étape 3.** On dérive par rapport à zₖ : le premier morceau donne −yₖ, parce que seul le terme i = k contient zₖ ; le second donne e^(zₖ) / ∑ⱼ e^(zⱼ), par la règle de dérivation de log u :

$$
\frac{\partial L}{\partial z_k} = -y_k + \frac{e^{z_k}}{\sum_j e^{z_j}} = p_k - y_k
$$

∎

**Vérification chiffrée.** Logits z = (2 ; 1 ; 0), bon token le deuxième. Exponentielles e² ≈ 7,38906, e¹ ≈ 2,71828, e⁰ = 1, de somme 11,10734, donc p ≈ (0,66524 ; 0,24473 ; 0,09003) et le gradient vaut (0,66524 ; 0,24473 − 1 ; 0,09003) = (0,66524 ; −0,75527 ; 0,09003). Le programme le retrouve par différences finies. Contre-exemple quand l'hypothèse ∑ yᵢ = 1 manque : avec la cible non normalisée (0 ; 2 ; 0), l'étape 2 laisse le facteur ∑ yᵢ = 2, et le vrai gradient vaut 2p − y ≈ (1,33048 ; −1,51054 ; 0,18006), pas p − y.

**Ce que la preuve révèle du mécanisme.** Le signal d'apprentissage est l'écart entre prédiction et cible : il est borné (chaque coordonnée est dans [−1 ; 1]), il est négatif seulement sur le bon token, et il s'annule quand p = y. Le modèle monte le logit du bon token d'autant plus fort qu'il lui donnait peu de probabilité.

**Conséquence pour un agent.** C'est la raison pour laquelle softmax et entropie croisée vont toujours ensemble dans les bibliothèques (une seule fonction « cross-entropy sur logits ») : on ne calcule jamais le jacobien de la softmax. Une cible mal normalisée (étiquettes dupliquées, poids de classes mal appliqués) multiplie silencieusement le gradient : on vérifie ∑ yᵢ = 1, comme le fait `gradient_logits`.

## Démonstration 5 — Le lien avec la perplexité

**Ce qu'on démontre.** Sur une séquence de n tokens, si L̄ est la perte moyenne, alors la perplexité de la fiche 32 vaut exp(L̄), et c'est aussi l'inverse de la moyenne géométrique des probabilités des bons tokens :

$$
\bar{L} = -\frac{1}{n} \sum_{t=1}^{n} \log P(x_t \mid x_{<t}), \qquad \operatorname{PPL} = e^{\bar{L}} = \Big( \prod_{t=1}^{n} P(x_t \mid x_{<t}) \Big)^{-1/n}
$$

**L'idée.** La perte de chaque token est −log de sa probabilité (démonstration 1) ; la moyenne de ces pertes, remise à l'échelle des probabilités par l'exponentielle, donne la perplexité.

**La preuve, pas à pas.**

**Étape 1.** Chaque position t a une cible one-hot sur le token réel xₜ, donc sa perte vaut −log P(xₜ | x₍<ₜ₎), par la démonstration 1. La moyenne de ces n pertes est L̄.

**Étape 2.** La perplexité est définie comme l'exponentielle de cette moyenne (fiche 32) : PPL = e^L̄.

**Étape 3.** On écrit −(1/n) ∑ log Pₜ = log ((∏ Pₜ)^(−1/n)), parce que le logarithme change un produit en somme et un exposant en facteur ; l'exponentielle annule le logarithme. ∎

**Vérification chiffrée.** Pour le lot du cas 1, la perte moyenne vaut 1,00781 nat, et e^1,00781 ≈ 2,73959 ; le programme vérifie que (0,9 × 0,6 × 0,05 × 0,8 × 0,3)^(−1/5) donne le même nombre.

**Ce que la preuve révèle du mécanisme.** Baisser la perte moyenne de 0,1 nat multiplie la perplexité par e^(−0,1) ≈ 0,905 : la perte et la perplexité sont deux lectures du même nombre, l'une additive, l'autre multiplicative.

**Conséquence pour un agent.** Quand un fournisseur de modèle annonce une perte et un autre une perplexité, on convertit avec exp ou ln avant de comparer, à tokenizer et jeu de test identiques (leçon, point 8).

## Démonstration 6 — Sensibilité : une baisse relative coûte la même perte, quel que soit p

**Ce qu'on démontre.** Si la probabilité du bon token est multipliée par (1 − ε), avec 0 ≤ ε < 1, la perte augmente de −ln(1 − ε), quelle que soit pᵦ ; et le gradient a une norme ‖p − y‖₁ = 2(1 − pᵦ) ≤ 2 :

$$
-\log\big((1 - \varepsilon)\, p_b\big) = -\log p_b - \log(1 - \varepsilon), \qquad \sum_k |p_k - y_k| = 2\,(1 - p_b)
$$

**L'idée.** Le logarithme transforme les rapports en différences : une baisse de 1 % est une baisse de 1 %, qu'elle parte de 0,9 ou de 0,05. Le gradient, lui, répartit sur les mauvais tokens exactement la masse qui manque au bon.

**La preuve, pas à pas.**

**Étape 1.** Le logarithme d'un produit est la somme des logarithmes, donc −ln((1 − ε) pᵦ) = −ln pᵦ − ln(1 − ε) ; l'augmentation ne dépend que de ε.

**Étape 2.** Sur le bon token, |pᵦ − 1| = 1 − pᵦ, parce que pᵦ ≤ 1 ; sur les autres, |pₖ − 0| = pₖ, parce que pₖ ≥ 0.

**Étape 3.** On additionne, avec ∑ₖ≠ᵦ pₖ = 1 − pᵦ, parce que les probabilités somment à 1 :

$$
\sum_k |p_k - y_k| = (1 - p_b) + (1 - p_b) = 2\,(1 - p_b)
$$

∎

**Vérification chiffrée.** Avec ε = 1 %, l'augmentation vaut −ln 0,99 ≈ 0,01005 nat, et le programme le vérifie pour pᵦ = 0,9 ; 0,24473 ; 0,05. Sur l'exemple de la démonstration 4 : |0,66524| + |−0,75527| + |0,09003| = 1,51054 = 2 × (1 − 0,24473). Pour comparer, la dérivée de la perte par rapport à pᵦ vaut −1/pᵦ : environ −1,11111 en 0,9, mais −20 en 0,05.

**Ce que la preuve révèle du mécanisme.** En échelle relative, la perte réagit pareil partout ; en échelle absolue, elle est 18 fois plus sensible à 0,05 qu'à 0,9. Le gradient sur les logits reste borné par 2 même quand la perte est énorme : l'entraînement ne « explose » pas sur un token très improbable.

**Conséquence pour un agent.** Pour comparer deux versions d'un modèle, on raisonne en écarts de perte (en nats), qui correspondent à des rapports de probabilités : 0,01 nat de mieux, c'est environ 1 % de probabilité en plus sur les bons tokens, à tous les niveaux de confiance.

## Exemple simple, à la main

Le bon token reçoit p = 0,7, puis p = 0,1. Avec la démonstration 1, la perte vaut −ln pᵦ :

$$
L = -\ln 0{,}7 \approx 0{,}35667, \qquad L = -\ln 0{,}1 \approx 2{,}30259
$$

Le premier calcul : ln 0,7 ≈ −0,35667, et le signe moins donne 0,35667. Le second : ln 0,1 = −ln 10 ≈ −2,30259, d'où 2,30259. Le rapport des deux pertes vaut 2,30259 / 0,35667 ≈ 6,456 : diviser la probabilité du bon token par 7 multiplie ici la perte par environ 6,5. La différence des deux pertes vaut −ln 0,1 − (−ln 0,7) = ln(0,7 / 0,1) = ln 7 ≈ 1,94591, comme l'annonce la démonstration 6 : seule compte la division de la probabilité par 7.

## Cas d'usage complexes, démontrés

Les probabilités, volumes et montants de ces cas sont illustratifs ; seules les règles citées (TVA, rôles des autorités) viennent du guide du cours.

### Cas 1 — Entité de services publics en ligne : la perte d'un lot de fine-tuning bilingue

**Contexte.** Une entité de services publics en ligne, accessible par UAE Pass, adapte un petit modèle à son assistant bilingue arabe et anglais. L'équipe évalue chaque lot de validation et veut savoir quels tokens tirent la perte vers le haut. Sur une réponse type de 5 tokens, l'un d'eux est le nom translittéré d'un quartier, écrit de plusieurs façons dans les données (par exemple « Al Qusais » et « Al Qusays »). Volume : environ 20 000 réponses de validation par version (illustratif).

**Données.** Probabilités données aux 5 bons tokens : 0,9 ; 0,6 ; 0,05 ; 0,8 ; 0,3. Le troisième est le nom translittéré. Règle de revue (illustrative) : si un seul token porte plus de 50 % de la perte d'une réponse, l'exemple part en revue.

**Calcul pas à pas.**

**Étape 1.** Perte de chaque token, −ln q, arrondie à 5 décimales :

$$
(0{,}10536\ ;\ 0{,}51083\ ;\ 2{,}99573\ ;\ 0{,}22314\ ;\ 1{,}20397)
$$

**Étape 2.** Somme 5,03903, perte moyenne et perplexité :

$$
\bar{L} = \frac{5{,}03903}{5} \approx 1{,}00781, \qquad \operatorname{PPL} = e^{1{,}00781} \approx 2{,}73959
$$

**Étape 3.** Part du token rare dans la perte totale :

$$
\frac{2{,}99573}{5{,}03903} \approx 0{,}59 = 59\ \%
$$

**Décision de l'agent.** Le token du nom de quartier porte 59 % de la perte, au-delà du seuil de 50 % : l'exemple part en revue, et l'équipe décide que l'assistant ne génère plus les noms de lieux de mémoire : il les copie depuis un outil de référentiel des adresses, qui normalise les variantes de translittération. L'entraînement corrigera en priorité ce token, puisque son gradient est le plus fort (démonstration 4).

**Contre-calcul.** Avec une pénalité linéaire 1 − q au lieu de −ln q, les pénalités valent 0,1 ; 0,4 ; 0,95 ; 0,2 ; 0,7, de somme 2,35, et le token rare n'en porte que 0,95 / 2,35 ≈ 40 % : il passerait sous le seuil, et l'erreur de nom de lieu resterait invisible. Pour un service public, un nom de quartier mal écrit envoie un usager au mauvais centre ou bloque une démarche, et la correction se fait au guichet.

**Sensibilité.** La valeur de bascule est la probabilité q du token rare pour laquelle sa part vaut exactement 50 % : sa perte doit égaler la somme des quatre autres, 0,10536 + 0,51083 + 0,22314 + 1,20397 = 2,04330, donc −ln q = 2,04330 et q = e^(−2,04330) ≈ 0,1296. Si le token rare passe de 0,05 à 0,1, la perte totale baisse de ln 2 ≈ 0,69315, la moyenne baisse de 0,13863 et vaut 0,86918, la perplexité tombe à 2,38495 ; la part du token reste au-dessus de 50 %, puisque 0,1 < 0,1296.

**En production.** On suit la perte moyenne par catégorie de token (noms propres, nombres, texte courant) sur le jeu de validation figé, avec une alerte si la perte des noms propres dépasse le double de celle du texte courant (seuil illustratif). Les réponses de validation sont anonymisées avant usage, conformément à la PDPL, dont l'application précise au cas de l'entité est à confirmer avec le texte en vigueur.

### Cas 2 — Assureur auto et santé : deux modèles de triage à exactitude égale

**Contexte.** Un assureur auto et santé, supervisé par la CBUAE, compare deux modèles qui trient les sinistres entre « légitime » et « fraude ». Un sinistre est approuvé automatiquement si le modèle lui donne au moins 0,9 de probabilité d'être légitime ; sinon il part en revue humaine. Sur un échantillon de 5 dossiers étiquetés, les deux modèles ont la même exactitude, et l'équipe doit choisir. Montants et coûts illustratifs.

**Données.** Probabilité donnée à la vraie classe, dossier par dossier (les dossiers 1 à 4 sont légitimes, le dossier 5 est une fraude) :

| Dossier | 1 | 2 | 3 | 4 | 5 (fraude) |
|---|---|---|---|---|---|
| Modèle A | 0,7 | 0,8 | 0,6 | 0,7 | 0,4 |
| Modèle B | 0,95 | 0,99 | 0,9 | 0,97 | 0,02 |

Montant moyen d'un sinistre : 8 000 AED. Coût d'une revue humaine : 50 AED. Seuil d'approbation automatique : 0,9.

**Calcul pas à pas.**

**Étape 1.** Exactitude : un dossier est bien classé si la vraie classe reçoit plus de 0,5. A : 4 sur 5 ; B : 4 sur 5. Les deux valent 80 %.

**Étape 2.** Pertes de A : 0,35667 ; 0,22314 ; 0,51083 ; 0,35667 ; 0,91629, de somme 2,36361 ; pertes de B : 0,05129 ; 0,01005 ; 0,10536 ; 0,03046 ; 3,91202, de somme 4,10919. Moyennes :

$$
\bar{L}_A = \frac{2{,}36361}{5} \approx 0{,}47272, \qquad \bar{L}_B = \frac{4{,}10919}{5} \approx 0{,}82184
$$

**Étape 3.** Coût opérationnel. A ne dépasse jamais 0,9 de probabilité « légitime » (au plus 0,8) : 5 revues, 5 × 50 = 250 AED. B approuve les 5 dossiers, y compris la fraude, à qui il donne 1 − 0,02 = 0,98 de probabilité d'être légitime : 0 revue, mais 8 000 AED payés à tort.

**Décision de l'agent.** L'équipe retient le modèle A, dont l'entropie croisée est plus basse (0,47272 < 0,82184), malgré une exactitude égale et un modèle B qui automatise davantage. Le coût de l'échantillon le confirme : 250 AED contre 8 000 AED.

**Contre-calcul.** Avec l'exactitude seule, les deux modèles sont à égalité (80 %) ; avec la « confiance moyenne » sur la vraie classe, B semble meilleur (0,766 contre 0,64). Seule l'entropie croisée voit que B s'est trompé avec une certitude de 98 % : ce seul dossier coûte 3,91202 nats, plus que les cinq dossiers de A réunis (2,36361).

**Sensibilité.** La valeur de bascule est la probabilité que B devrait donner à la fraude pour égaler la perte de A : les quatre premiers dossiers de B coûtent 0,19716, il resterait donc 2,36361 − 0,19716 = 2,16645 nats pour le dernier, soit q = e^(−2,16645) ≈ 0,11458. Au-dessus de cette valeur, B passerait devant A ; l'exercice 6 le vérifie avec q = 0,2.

**En production.** On suit chaque semaine l'entropie croisée moyenne sur un échantillon de sinistres étiquetés, et la part des dossiers où la vraie classe reçoit moins de 0,05 (erreurs sûres d'elles), avec une alerte dès que cette part dépasse 1 % (seuil illustratif). Les règles de traitement des sinistres relèvent de la supervision de la CBUAE et sont à confirmer avec le texte en vigueur.

### Cas 3 — Cabinet RH multi-émirats : distiller un grand modèle vers un petit routeur

**Contexte.** Un cabinet RH multi-émirats route les messages des salariés entre deux files : « visa » et « WPS » (versement des salaires). Un grand modèle, coûteux, sert de professeur ; l'équipe distille ses probabilités vers un petit modèle rapide. Sur une famille de messages ambigus, environ 400 par mois (illustratif), le professeur donne 0,8 à « visa » et 0,2 à « WPS » : une partie de ces messages parle en réalité de salaire bloqué par un problème de visa.

**Données.** Cible souple du professeur : y = (0,8 ; 0,2). Élève au départ : p = (0,6 ; 0,4). Élève après entraînement : p = (0,75 ; 0,25). Variante entraînée sur la cible dure (1 ; 0) : p = (0,95 ; 0,05). Critère d'arrêt (illustratif) : KL < 0,01.

**Calcul pas à pas.**

**Étape 1.** Plancher de la perte, l'entropie de la cible :

$$
H(y) = -(0{,}8 \ln 0{,}8 + 0{,}2 \ln 0{,}2) \approx 0{,}50040
$$

**Étape 2.** Perte et KL au départ :

$$
L = -(0{,}8 \ln 0{,}6 + 0{,}2 \ln 0{,}4) \approx 0{,}59192, \qquad D_{KL} = 0{,}59192 - 0{,}50040 = 0{,}09152
$$

**Étape 3.** Perte et KL après entraînement :

$$
L = -(0{,}8 \ln 0{,}75 + 0{,}2 \ln 0{,}25) \approx 0{,}50740, \qquad D_{KL} = 0{,}50740 - 0{,}50040 = 0{,}00700
$$

**Décision de l'agent.** La KL vaut 0,00700 < 0,01 : on arrête la distillation et l'on déploie l'élève. La perte (0,50740) paraît encore « haute », mais elle ne peut pas descendre sous 0,50040 (démonstration 3) : c'est la KL qui dit qu'il ne reste presque plus rien à gagner.

**Contre-calcul.** Entraîné sur la cible dure (1 ; 0), l'élève devient sûr de lui, p = (0,95 ; 0,05) ; sa perte face au professeur monte à 0,64018 et sa KL à 0,13978, pire qu'au départ. Il enverrait ces messages ambigus vers « visa » avec 95 % de certitude : si 20 % d'entre eux concernent un salaire, cela fait 0,2 × 400 = 80 salariés par mois dont la demande sur le WPS arrive dans la mauvaise file.

**Sensibilité.** Le critère KL < 0,01 accepte toute probabilité q de « visa » comprise entre 0,73967 et 0,85238 (valeurs de bascule trouvées par dichotomie dans le programme) : l'élève peut être un peu moins ou un peu plus sûr que le professeur, mais pas au point de 0,95.

**En production.** On suit la KL moyenne entre professeur et élève sur un échantillon de messages réels chaque semaine ; une remontée au-dessus de 0,01 déclenche une nouvelle distillation. Le WPS et les procédures du MOHRE ont leurs propres délais et obligations, à confirmer avec le texte en vigueur : l'agent ne promet aucun délai, il route.

### Cas 4 — Groupe de construction à Dubaï : corriger le classement TVA d'une ligne de facture

**Contexte.** Un groupe de construction qui mène de grands chantiers à Dubaï fait classer par un modèle chaque ligne de ses factures dans l'une de trois catégories de TVA : 5 %, taux zéro (par exemple la première livraison d'un bien résidentiel) ou exonéré. Une ligne de 200 000 AED (illustratif) a été classée à tort « 5 % » ; un contrôleur la corrige en « taux zéro ». L'équipe applique, sur un modèle jouet dont les paramètres sont directement les logits, des pas de descente de gradient et veut savoir quand la ligne peut être classée automatiquement.

**Données.** Logits initiaux z = (2 ; 1 ; 0) pour (5 % ; taux zéro ; exonéré). Vraie catégorie : taux zéro, donc y = (0 ; 1 ; 0). Pas d'apprentissage η = 0,5. Seuil d'application automatique (illustratif) : probabilité ≥ 0,9 sur la catégorie choisie ; seuil de classement correct : la vraie catégorie a plus de 0,5.

**Calcul pas à pas.**

**Étape 1.** Probabilités, perte et gradient (démonstration 4) :

$$
p \approx (0{,}66524\ ;\ 0{,}24473\ ;\ 0{,}09003), \qquad L = -\ln 0{,}24473 \approx 1{,}40761, \qquad p - y \approx (0{,}66524\ ;\ -0{,}75527\ ;\ 0{,}09003)
$$

**Étape 2.** Premier pas, z ← z − η (p − y) :

$$
z \approx (2 - 0{,}33262\ ;\ 1 + 0{,}37764\ ;\ 0 - 0{,}04502) = (1{,}66738\ ;\ 1{,}37764\ ;\ -0{,}04502)
$$

d'où p ≈ (0,51843 ; 0,38802 ; 0,09354) et une perte qui tombe à −ln 0,38802 ≈ 0,94669.

**Étape 3.** Second pas, avec le nouveau gradient p − y ≈ (0,51843 ; −0,61198 ; 0,09354) : les logits deviennent z ≈ (1,40816 ; 1,68362 ; −0,09179), et la probabilité du taux zéro passe à 0,5185, au-dessus de 0,5, avec p ≈ (0,39366 ; 0,5185 ; 0,08784).

**Décision de l'agent.** Après 2 pas, la ligne est bien classée (0,5185 > 0,5), mais sa probabilité reste loin du seuil d'application automatique de 0,9 : la ligne reste en revue humaine. Le modèle corrigé sert à préremplir la catégorie, pas à appliquer la TVA. L'enjeu par ligne est de 5 % × 200 000 = 10 000 AED de TVA facturée à tort.

**Contre-calcul.** Avec une erreur de signe, z ← z + η (p − y), le pas éloigne le modèle de la cible : la probabilité du taux zéro tombe à 0,14101 et la perte monte à 1,95893 au lieu de descendre à 0,94669. C'est l'erreur classique qu'un test « la perte baisse après un pas » attrape tout de suite.

**Sensibilité.** Avec un pas 10 % plus petit (η = 0,45), il faut 3 pas au lieu de 2 pour franchir 0,5. La valeur de bascule pour réussir en un seul pas est η* ≈ 0,8439 : au-dessus, un seul exemple corrigé suffit à retourner le classement, ce qui est aussi le signe d'un pas assez grand pour abîmer les autres lignes déjà bien classées. Le compromis réel est là : corriger vite un exemple ou préserver les autres.

**En production.** On suit la part des lignes que le contrôleur corrige après préremplissage, par catégorie de TVA, avec une alerte si elle dépasse 2 % (seuil illustratif). La TVA aux Émirats est de 5 %, avec un taux zéro pour la première livraison d'un bien résidentiel et une exonération pour le loyer résidentiel ; la qualification de chaque ligne de chantier reste à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Calculer la perte pour p_bon = 0,25, puis 0,5. (ln 2 ≈ 0,693.)

**Exercice 2.** Un modèle donne p_bon = 1. Que vaut la perte, et pourquoi n'est-ce jamais atteint avec une softmax ?

**Exercice 3.** Logits (0 ; 0), bon token = le premier. Donner p, L et le gradient.

**Exercice 4.** Démontrer, sans regarder, que log x ≤ x − 1.

**Exercice 5.** Pertes de trois tokens : 0,1 ; 0,2 ; 3,0. Quelle part de la perte totale vient du dernier ?

**Exercice 6 (cas modifié).** Dans le cas 2, le modèle B donne désormais 0,2 (au lieu de 0,02) à la vraie classe du dossier frauduleux. Recalculer sa perte moyenne, son coût sur l'échantillon et la décision.

**Exercice 7 (trouver l'erreur).** Un collègue calcule la perte moyenne du lot du cas 1 ainsi : « la moyenne des probabilités vaut (0,9 + 0,6 + 0,05 + 0,8 + 0,3) / 5 = 0,53, donc la perte moyenne vaut −ln 0,53 ≈ 0,63488 et la perplexité 1 / 0,53 ≈ 1,88679. » Trouver l'erreur et donner les bonnes valeurs.

**Exercice 8 (redémontrer de mémoire).** Redémontrer, sans regarder, que le gradient de l'entropie croisée par rapport aux logits vaut p − y, en précisant où sert l'hypothèse ∑ yᵢ = 1.

## Corrigé

**Exercice 1.** −ln 0,25 = −ln(1/4) = ln 4 = 2 ln 2 ≈ 1,386 ; −ln 0,5 = ln 2 ≈ 0,693. Diviser la probabilité par 2 ajoute ln 2.

**Exercice 2.** L = −ln 1 = 0. Une softmax donne toujours une probabilité strictement positive à chaque token, parce que e^(zᵢ) > 0 pour tout logit fini (fiche 04) ; la somme des probabilités des autres tokens est donc > 0, et p_bon = 1 − (cette somme) < 1. La perte s'approche de 0 sans l'atteindre.

**Exercice 3.** e⁰ = 1 pour les deux logits, donc p = (1/2 ; 1/2) = (0,5 ; 0,5). L = −ln 0,5 = ln 2 ≈ 0,693. Gradient p − y = (0,5 − 1 ; 0,5 − 0) = (−0,5 ; 0,5) : le premier logit doit monter, le second baisser.

**Exercice 4.** On pose g(x) = x − 1 − ln x pour x > 0. Sa dérivée vaut 1 − 1/x : négative si x < 1, nulle en 1, positive si x > 1. Donc g décroît puis croît, son minimum est g(1) = 1 − 1 − 0 = 0, et g(x) ≥ 0, c'est-à-dire ln x ≤ x − 1, avec égalité seulement en x = 1.

**Exercice 5.** Total 0,1 + 0,2 + 3,0 = 3,3 ; part du dernier 3,0 / 3,3 ≈ 0,909, soit environ 91 %.

**Exercice 6.** Les quatre premiers dossiers de B coûtent toujours 0,19716 ; le cinquième coûte −ln 0,2 ≈ 1,60944. Perte moyenne : (0,19716 + 1,60944) / 5 ≈ 0,36132, désormais inférieure à celle de A (0,47272) ; 0,2 dépasse bien la bascule 0,11458. Coût : B donne 1 − 0,2 = 0,8 < 0,9 de probabilité « légitime » à la fraude, qui part donc en revue (50 AED), et approuve les quatre autres : 50 AED contre 250 AED pour A. Décision : on retient B.

**Exercice 7.** L'erreur : la perte moyenne est la moyenne des −ln q, pas le −ln de la moyenne des q. Comme −ln est convexe, −ln(moyenne) ≤ moyenne des −ln (inégalité de Jensen) : le raccourci sous-estime la perte. Bonnes valeurs : pertes 0,10536 ; 0,51083 ; 2,99573 ; 0,22314 ; 1,20397, moyenne 1,00781, perplexité e^1,00781 ≈ 2,73959, au lieu de 0,63488 et 1,88679. Le raccourci efface justement le token à 0,05.

**Exercice 8.** Étape 1 : log pᵢ = zᵢ − log ∑ⱼ e^(zⱼ), par définition de la softmax. Étape 2 : L = −∑ yᵢ zᵢ + (∑ yᵢ) log ∑ⱼ e^(zⱼ) ; l'hypothèse ∑ yᵢ = 1 sert ici, pour remplacer le facteur (∑ yᵢ) par 1. Étape 3 : la dérivée de −∑ yᵢ zᵢ par rapport à zₖ vaut −yₖ ; celle de log ∑ⱼ e^(zⱼ) vaut e^(zₖ) / ∑ⱼ e^(zⱼ) = pₖ. Donc ∂L/∂zₖ = pₖ − yₖ. ∎

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(z)`** — Cette fonction est le traducteur qui transforme des logits bruts, nombres sans unité que le modèle aligne pour chaque classe, en probabilités qu'on peut comparer à une cible : elle reçoit la liste `z`, retire son maximum à chaque élément pour que l'exponentielle ne déborde jamais, prend l'exponentielle de chaque écart, puis divise chacune par leur somme. Elle renvoie une liste de nombres strictement positifs dont le total vaut 1, par exemple (0,66524 ; 0,24473 ; 0,09003) pour les logits (2 ; 1 ; 0) de la démonstration 4 et du cas 4 ; c'est elle qu'appellent `gradient_logits` et la descente du cas de la TVA.

**`entropie_croisee(y, p)`** — On peut la voir comme un examinateur qui note la surprise du modèle devant la bonne réponse : elle reçoit la cible `y` et la distribution prédite `p`, refuse par une `ValueError` deux listes de longueurs différentes, puis refuse aussi, toujours par une `ValueError`, toute cible posée sur une probabilité nulle ou négative, car la perte serait alors infinie. Elle additionne ensuite −yᵢ ln pᵢ en sautant les termes où yᵢ vaut 0, et renvoie cette somme : −ln 0,7 ≈ 0,35667 pour une cible one-hot, 0,51661 pour la cible lissée (0,05 ; 0,9 ; 0,05) de la démonstration 1, et, appliquée à la cible contre elle-même, l'entropie H(y) qui sert à calculer la divergence KL.

**`gradient_logits(z, y)`** — Cette fonction est la boussole de l'apprentissage : elle reçoit les logits `z` et la cible `y`, vérifie d'abord que la cible somme à 1 à 10⁻¹² près, sinon elle lève une `ValueError`, puisque c'est précisément l'hypothèse dont la démonstration 4 a besoin, puis elle calcule `softmax(z)` et soustrait la cible coordonnée par coordonnée. Elle renvoie le vecteur p − y, qui indique de combien chaque logit doit bouger : (0,66524 ; −0,75527 ; 0,09003) pour les logits (2 ; 1 ; 0) et le bon token au milieu, ce qui dit que le deuxième logit doit monter et les deux autres baisser ; `main` le confronte aux différences finies et la descente du cas 4 l'utilise à chaque pas.

**`perte_moyenne(probas_bon)`** — Cette fonction joue le rôle d'un correcteur qui fait la moyenne d'une copie entière plutôt que de noter une seule réponse : elle reçoit la liste des probabilités que le modèle a données au bon token, renvoie `None` si cette liste est vide, puisqu'une moyenne de rien n'a pas de sens, et sinon additionne les −ln q de chaque token avant de diviser par leur nombre. Elle renvoie la perte moyenne du lot, 1,00781 pour le lot (0,9 ; 0,6 ; 0,05 ; 0,8 ; 0,3) du cas 1, dont l'exponentielle donne la perplexité 2,73959 ; elle sert aussi à comparer les deux modèles de triage du cas 2.

**`r5(xs)`** — Cette petite fonction est le copiste qui met les résultats au propre : elle reçoit une liste de nombres et renvoie une nouvelle liste où chacun est arrondi à cinq décimales. Elle ne calcule rien de neuf, mais elle permet aux `assert` de `main` et aux affichages des cas de comparer des listes de pertes, de probabilités ou de gradients aux valeurs écrites dans la fiche, comme [0,10536 ; 0,51083 ; 2,99573 ; 0,22314 ; 1,20397], sans être gênés par les derniers chiffres des nombres flottants.

**`cas_1_lot_public()`** — On y suit une administration qui entraîne un modèle sur un lot de cinq tokens dont le troisième, un nom propre rare, ne reçoit que 0,05 de probabilité : la fonction calcule les cinq pertes −ln q, leur moyenne 1,00781 et la perplexité 2,73959, puis la part de la perte totale due au token rare, 59 %, contre 40 % seulement si l'on mesurait l'erreur par 1 − q. Elle cherche ensuite la probabilité de bascule à laquelle ce token pèserait exactement la moitié, e à la puissance moins la somme des autres pertes, soit 0,1296, et la nouvelle moyenne, 0,86918, si sa probabilité doublait jusqu'à 0,1 ; elle renvoie ces huit grandeurs avec la décision « revue de l'exemple et nom copié par outil », prise parce que la part dépasse 50 %.

**`cas_2_triage_assurance()`** — Cette fonction met face à face deux modèles de triage de sinistres qui ont la même exactitude, 80 %, sur cinq dossiers dont le cinquième est une fraude de 8 000 AED : pour chacun, elle compte les dossiers approuvés automatiquement, ceux où la probabilité « légitime » atteint 0,9, facture 50 AED de revue pour chaque dossier restant et ajoute 8 000 AED si la fraude est passée sans contrôle. Le modèle A, prudent, coûte 250 AED avec une perte moyenne de 0,47272, tandis que le modèle B, trop sûr de lui, laisse passer la fraude et coûte 8 000 AED avec une perte de 0,82184 ; la fonction calcule aussi la probabilité de bascule, 0,11458, que B devrait donner à la vraie classe de la fraude pour égaler A, et renvoie les résultats, la somme des pertes des quatre bons dossiers de B, cette bascule et le choix du modèle de plus faible perte, A.

**`cas_3_distillation_rh()`** — Un service des ressources humaines distille un modèle professeur, qui répartit un message ambigu en 0,8 « visa » et 0,2 « WPS », dans un modèle élève : la fonction calcule l'entropie de cette cible souple, 0,5004, puis, pour l'élève de départ (0,6 ; 0,4), l'élève après entraînement (0,75 ; 0,25) et l'élève entraîné sur la cible dure (0,95 ; 0,05), la perte face au professeur, la KL, qui est cette perte moins l'entropie, et la perte face à la cible dure. Elle encadre ensuite par deux dichotomies de 60 tours, l'une dans [0,5 ; 0,8] et l'autre dans [0,8 ; 0,99], les probabilités 0,73967 et 0,85238 entre lesquelles la KL reste sous 0,01, et renvoie l'entropie, le dictionnaire des trois états, ces deux bornes et l'ordre d'arrêt, vrai puisque la KL après entraînement vaut 0,007.

**`cas_4_tva_btp()`** — Cette fonction raconte un contrôleur de chantier qui corrige le classement TVA d'une ligne de 200 000 AED, rangée à tort à 5 % alors qu'elle relève du taux zéro : partant des logits (2 ; 1 ; 0) et de la cible (0 ; 1 ; 0), elle calcule les probabilités et le gradient de départ, puis confie à sa fonction interne `descendre` la descente avec η = 0,5, qui demande 2 pas, et avec η = 0,45, qui en demande 3, ainsi qu'un pas à signe inversé qui fait chuter la probabilité du taux zéro à 0,14101. Elle cherche aussi par dichotomie, en 60 tours entre 0,1 et 2, le plus petit pas η* qui franchit 0,5 en une seule fois, environ 0,8439, et renvoie les probabilités et le gradient initiaux, les trois trajectoires, ce η* et la décision « revue humaine », car la probabilité finale 0,5185 reste loin du seuil d'application automatique de 0,9.

**`descendre(eta_, signe)`** — Cette fonction interne vit dans `cas_4_tva_btp` et y joue le marcheur qui descend la pente de la perte à petits pas : elle reçoit la taille du pas `eta_` et un `signe` qui vaut 1 par défaut, part d'une copie des logits initiaux (2 ; 1 ; 0) et, tant que la probabilité du taux zéro reste sous 0,5 et qu'elle n'a pas fait 20 pas, elle demande le gradient à `gradient_logits`, retranche signe × η × gradient aux logits et note dans sa trace les nouveaux logits et leurs probabilités. Avec un signe négatif, elle s'arrête après le premier pas, juste assez pour montrer qu'une erreur de signe fait monter la perte à 1,95893 ; elle renvoie la liste des étapes, dont la longueur donne le nombre de pas nécessaires.

**`main()`** — C'est le banc d'essai qui rejoue la fiche dans l'ordre de lecture : il commence par le film des −ln q, de 0,10536 pour 0,9 à 4,60517 pour 0,01, vérifie qu'une cible one-hot ne garde que le terme du bon token, que la perte est positive et ne devient négative qu'avec une fausse probabilité 1,2, puis que L = H(y) + KL avec 1,20397 = 0,69315 + 0,51083 et que ln x ≤ x − 1 sur cinq valeurs. Il contrôle ensuite le gradient p − y par différences finies, montre qu'une cible (0 ; 2 ; 0) donnerait 2p − y et s'assure que `gradient_logits` la refuse, retrouve la perplexité 2,73959 comme exponentielle de la perte moyenne, vérifie que réduire q de 1 % ajoute toujours 0,01005 à la perte, lance les quatre cas et refait le corrigé ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tous concordent.

```python
"""Démonstration 06 — entropie croisée : one-hot, positivité, KL, gradient p − y, perplexité, sensibilité, quatre cas aux EAU."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def softmax(z: list[float]) -> list[float]:
    m = max(z)
    e = [math.exp(x - m) for x in z]
    s = sum(e)
    return [x / s for x in e]


def entropie_croisee(y: list[float], p: list[float]) -> float:
    """L = −Σ yᵢ ln pᵢ ; les termes où yᵢ = 0 ne comptent pas ; une cible posée sur pᵢ = 0 est refusée."""
    if len(y) != len(p):
        raise ValueError("y et p doivent avoir la même longueur")
    if any(b <= 0 for a, b in zip(y, p) if a > 0):
        raise ValueError("probabilité nulle sur une cible : perte infinie")
    return -sum(a * math.log(b) for a, b in zip(y, p) if a > 0)


def gradient_logits(z: list[float], y: list[float]) -> list[float]:
    """∂L/∂z_k = p_k − y_k quand p = softmax(z) et que la cible somme à 1."""
    if abs(sum(y) - 1) > 1e-12:
        raise ValueError("la cible doit sommer à 1")
    return [a - b for a, b in zip(softmax(z), y)]


def perte_moyenne(probas_bon: list[float]) -> float | None:
    """Moyenne des −ln q sur les tokens d'un lot ; None si le lot est vide."""
    if not probas_bon:
        return None
    return sum(-math.log(q) for q in probas_bon) / len(probas_bon)


def r5(xs):
    return [round(x, 5) for x in xs]


def cas_1_lot_public():
    """Secteur public : perte d'un lot de 5 tokens, part du token rare, bascule de cette part à 50 %."""
    lot = [0.9, 0.6, 0.05, 0.8, 0.3]
    pertes = [-math.log(q) for q in lot]
    moy = perte_moyenne(lot)
    part = pertes[2] / sum(pertes)
    autres = sum(pertes) - pertes[2]
    q_bascule = math.exp(-autres)                         # part = 50 %  <=>  −ln q = somme des autres pertes
    lineaire = [1 - q for q in lot]
    part_lineaire = lineaire[2] / sum(lineaire)
    moy_double = (sum(pertes) - math.log(2)) / len(lot)   # le token rare passe de 0.05 à 0.1
    decision = "revue de l'exemple et nom copié par outil" if part > 0.5 else "lot normal"
    print(f"cas 1 PUBLIC : pertes {r5(pertes)} ; moyenne {moy:.5f} ; PPL {math.exp(moy):.5f} ; part du token rare {part:.0%}")
    print(f"  part avec 1 − q : {part_lineaire:.0%} ; q de bascule {q_bascule:.5f} ; si q = 0.1 : moyenne {moy_double:.5f},"
          f" PPL {math.exp(moy_double):.5f} ; décision : {decision}")
    return pertes, moy, part, autres, q_bascule, part_lineaire, moy_double, decision


def cas_2_triage_assurance():
    """Assurance : deux modèles de triage à exactitude égale, départagés par l'entropie croisée."""
    A = [0.7, 0.8, 0.6, 0.7, 0.4]          # probabilité donnée à la vraie classe ; le dossier 5 est une fraude
    B = [0.95, 0.99, 0.9, 0.97, 0.02]
    montant, cout_revue, seuil_auto = 8000, 50, 0.9
    res = {}
    for nom, X in (("A", A), ("B", B)):
        exactitude = sum(q > 0.5 for q in X) / len(X)
        auto = [i for i, q in enumerate(X) if (q if i < 4 else 1 - q) >= seuil_auto]   # p(légitime) >= 0.9
        perte_aed = (montant if 4 in auto else 0) + cout_revue * (len(X) - len(auto))
        res[nom] = (perte_moyenne(X), exactitude, len(auto), perte_aed)
    autres_b = sum(-math.log(q) for q in B[:4])
    q_bascule = math.exp(-(len(A) * res["A"][0] - autres_b))
    choix = min(res, key=lambda k: res[k][0])
    print(f"cas 2 ASSUR : A perte {res['A'][0]:.5f}, exactitude {res['A'][1]:.0%}, coût {res['A'][3]} AED ;"
          f" B perte {res['B'][0]:.5f}, exactitude {res['B'][1]:.0%}, coût {res['B'][3]} AED")
    print(f"  pertes A {r5([-math.log(q) for q in A])} ; pertes B {r5([-math.log(q) for q in B])}")
    print(f"  bascule du pire dossier de B : {q_bascule:.5f} ; choix : modèle {choix}")
    return res, autres_b, q_bascule, choix


def cas_3_distillation_rh():
    """RH : distillation sur une cible souple (visa ; WPS), arrêt quand la KL passe sous 0.01."""
    y = (0.8, 0.2)
    H = entropie_croisee(y, y)
    etats = {}
    for nom, p in (("départ", (0.6, 0.4)), ("après", (0.75, 0.25)), ("cible dure", (0.95, 0.05))):
        L = entropie_croisee(y, p)
        etats[nom] = (L, L - H, entropie_croisee((1, 0), p))
    bornes = []
    for bas, haut in ((0.5, 0.8), (0.8, 0.99)):           # q tel que KL((0.8 ; 0.2) ‖ (q ; 1 − q)) = 0.01
        f_bas = entropie_croisee(y, (bas, 1 - bas)) - H - 0.01
        for _ in range(60):
            m = (bas + haut) / 2
            f_m = entropie_croisee(y, (m, 1 - m)) - H - 0.01
            if f_m * f_bas > 0:
                bas, f_bas = m, f_m
            else:
                haut = m
        bornes.append((bas + haut) / 2)
    arret = etats["après"][1] < 0.01
    print(f"cas 3 RH : H(y) {H:.5f} ; départ L {etats['départ'][0]:.5f}, KL {etats['départ'][1]:.5f} ;"
          f" après L {etats['après'][0]:.5f}, KL {etats['après'][1]:.5f}")
    print(f"  cible dure : L souple {etats['cible dure'][0]:.5f}, KL {etats['cible dure'][1]:.5f} ;"
          f" KL < 0.01 pour q dans [{bornes[0]:.5f} ; {bornes[1]:.5f}] ; arrêt : {arret}")
    return H, etats, bornes, arret


def cas_4_tva_btp():
    """BTP : classement TVA d'une ligne (5 % ; taux zéro ; exonéré), pas de gradient p − y sur les logits."""
    z0, y = [2.0, 1.0, 0.0], [0, 1, 0]                    # la vraie catégorie est le taux zéro
    montant, eta, seuil_auto = 200000, 0.5, 0.9

    def descendre(eta_, signe=1):
        z, trace = list(z0), []
        while softmax(z)[1] < 0.5 and len(trace) < 20:
            g = gradient_logits(z, y)
            z = [a - signe * eta_ * b for a, b in zip(z, g)]
            trace.append((list(z), softmax(z)))
            if signe < 0:
                break
        return trace

    p0 = softmax(z0)
    g0 = gradient_logits(z0, y)
    trace = descendre(eta)
    trace_m10 = descendre(0.9 * eta)
    faux = descendre(eta, signe=-1)
    bas, haut = 0.1, 2.0                                    # η minimal pour franchir 0.5 en un seul pas
    for _ in range(60):
        m = (bas + haut) / 2
        if softmax([a - m * b for a, b in zip(z0, g0)])[1] < 0.5:
            bas = m
        else:
            haut = m
    p_final = trace[-1][1]
    decision = "application automatique" if p_final[1] >= seuil_auto else "revue humaine"
    print(f"cas 4 BTP : p {r5(p0)} ; L {-math.log(p0[1]):.5f} ; gradient {r5(g0)} ; erreur évitée {0.05 * montant:.0f} AED")
    print(f"  pas 1 : z {r5(trace[0][0])}, p {r5(trace[0][1])} ; {len(trace)} pas à η = 0.5, {len(trace_m10)} à η = 0.45 ;"
          f" η* = {haut:.4f}")
    print(f"  pas 2 : z {r5(trace[1][0])}, p {r5(trace[1][1])}")
    print(f"  signe inversé : p {r5(faux[0][1])}, L {-math.log(faux[0][1][1]):.5f} ; p final {r5(p_final)} ; décision : {decision}")
    return p0, g0, trace, trace_m10, faux, haut, decision


def main() -> None:
    # Film et exemple simple
    film = [(q, -math.log(q)) for q in (0.9, 0.5, 0.05, 0.7, 0.1, 0.01)]
    print("film : " + " ; ".join(f"−ln {q} = {v:.5f}" for q, v in film))
    assert r5([v for _, v in film]) == [0.10536, 0.69315, 2.99573, 0.35667, 2.30259, 4.60517]
    assert round(-math.log(0.7), 5) == 0.35667 and round(-math.log(0.1), 5) == 2.30259
    assert round(-math.log(0.1) / -math.log(0.7), 3) == 6.456 and round(math.log(0.7), 5) == -0.35667

    # Démonstration 1 : one-hot, puis contre-exemple avec une cible lissée
    y1, p1 = [0, 1, 0], [0.2, 0.7, 0.1]
    lisse = entropie_croisee([0.05, 0.9, 0.05], p1)
    print(f"démo 1 : one-hot {entropie_croisee(y1, p1):.5f} = −ln 0.7 ; cible lissée {lisse:.5f}")
    assert entropie_croisee(y1, p1) == -math.log(0.7) and round(lisse, 5) == 0.51661

    # Démonstration 2 : positivité, limites, contre-exemple p > 1
    assert entropie_croisee([1, 0], [1.0, 0.0]) == 0
    assert round(-math.log(0.001), 5) == 6.90776 and round(-math.log(1.2), 5) == -0.18232
    print(f"démo 2 : −ln 1 = 0 ; −ln 0.01 = {-math.log(0.01):.5f} ; −ln 0.001 = {-math.log(0.001):.5f} ;"
          f" « probabilité » 1.2 : {-math.log(1.2):.5f} < 0")

    # Démonstration 3 : L = H(y) + KL, KL ≥ 0, inégalité ln x ≤ x − 1
    ys, ps = (0.5, 0.5), (0.9, 0.1)
    L3, H3 = entropie_croisee(ys, ps), entropie_croisee(ys, ys)
    print(f"démo 3 : L = {L3:.5f}, H(y) = ln 2 = {H3:.5f}, KL = {L3 - H3:.5f}")
    assert round(L3, 5) == 1.20397 and round(H3, 5) == 0.69315 and round(L3 - H3, 5) == 0.51083
    for x in (0.1, 0.5, 1.0, 2.0, 7.0):
        assert math.log(x) <= x - 1 + 1e-15
    print("  ln x <= x − 1 : " + " ; ".join(f"x = {x} : {math.log(x):.5f} <= {x - 1:.1f}" for x in (0.1, 0.5, 1.0, 2.0, 7.0)))
    assert round(0.5 * -math.log(0.9), 5) == 0.05268 and round(0.5 * -math.log(0.1), 5) == 1.15129

    # Démonstration 4 : gradient p − y, différences finies, contre-exemple cible non normalisée
    z, y = [2, 1, 0], [0, 1, 0]
    p = softmax(z)
    grad = gradient_logits(z, y)
    h = 1e-6
    for k in range(3):
        zk = list(z)
        zk[k] += h
        numerique = (entropie_croisee(y, softmax(zk)) - entropie_croisee(y, p)) / h
        assert math.isclose(numerique, grad[k], rel_tol=1e-4, abs_tol=1e-6)
    y2 = [0, 2, 0]
    vrai2 = [2 * a - b for a, b in zip(p, y2)]
    for k in range(3):
        zk = list(z)
        zk[k] += h
        numerique = (-sum(a * math.log(b) for a, b in zip(y2, softmax(zk)) if a > 0)
                     + sum(a * math.log(b) for a, b in zip(y2, p) if a > 0)) / h
        assert math.isclose(numerique, vrai2[k], rel_tol=1e-4, abs_tol=1e-6)
    print(f"démo 4 : p {r5(p)} ; gradient p − y {r5(grad)} ; cible (0 ; 2 ; 0) : {r5(vrai2)}")
    assert r5(p) == [0.66524, 0.24473, 0.09003] and r5(grad) == [0.66524, -0.75527, 0.09003]
    assert r5(vrai2) == [1.33048, -1.51054, 0.18006]
    try:
        gradient_logits(z, y2)
    except ValueError:
        pass
    else:
        raise AssertionError("une cible qui ne somme pas à 1 aurait dû être refusée")

    # Démonstration 5 : perplexité = exp(perte moyenne)
    lot = [0.9, 0.6, 0.05, 0.8, 0.3]
    pertes = [-math.log(q) for q in lot]
    moy = sum(pertes) / len(pertes)
    assert math.isclose(math.exp(moy), math.prod(lot) ** (-1 / 5))
    print(f"démo 5 : perte moyenne {moy:.5f} ; PPL = e^L = {math.exp(moy):.5f} = (Π q)^(−1/5)")
    assert perte_moyenne([]) is None

    # Démonstration 6 : sensibilité relative et borne du gradient
    for q in (0.9, 0.24473, 0.05):
        assert math.isclose(-math.log(0.99 * q) - (-math.log(q)), -math.log(0.99))
    norme1 = sum(abs(g) for g in grad)
    print(f"démo 6 : −ln 0.99 = {-math.log(0.99):.5f} quel que soit q ; ‖p − y‖₁ = {norme1:.5f} = 2(1 − p_b)")
    assert round(-math.log(0.99), 5) == 0.01005 and round(norme1, 5) == 1.51054
    assert math.isclose(norme1, 2 * (1 - p[1])) and round(1 / 0.05, 0) == 20 and round(1 / 0.9, 5) == 1.11111

    # Cas
    c1 = cas_1_lot_public()
    pertes1, moy1, part1, autres1, qb1, part_lin, moy_d, dec1 = c1
    assert r5(pertes1) == [0.10536, 0.51083, 2.99573, 0.22314, 1.20397] and round(moy1, 5) == 1.00781
    assert round(math.exp(moy1), 5) == 2.73959 and round(part1, 2) == 0.59 and round(sum(pertes1), 5) == 5.03903
    assert round(autres1, 5) == 2.0433 and round(qb1, 5) == 0.1296 and round(part_lin, 2) == 0.40 and round(sum([1 - q for q in lot]), 10) == 2.35
    assert round(moy_d, 5) == 0.86918 and round(math.exp(moy_d), 5) == 2.38495 and dec1.startswith("revue")
    assert round(math.log(2) / 5, 5) == 0.13863 and 0.95 / 2.35 > 0.4

    res2, autres_b, qb2, choix = cas_2_triage_assurance()
    assert round(res2["A"][0], 5) == 0.47272 and round(res2["B"][0], 5) == 0.82184
    assert res2["A"][1] == res2["B"][1] == 0.8 and res2["A"][3] == 250 and res2["B"][3] == 8000 and choix == "A"
    assert res2["A"][2] == 0 and res2["B"][2] == 5
    assert round(autres_b, 5) == 0.19716 and round(qb2, 5) == 0.11458 and round(5 * res2["A"][0], 5) == 2.36361
    assert r5([-math.log(q) for q in (0.95, 0.99, 0.9, 0.97, 0.02)]) == [0.05129, 0.01005, 0.10536, 0.03046, 3.91202]
    assert round(-math.log(0.4), 5) == 0.91629 and round(-math.log(0.8), 5) == 0.22314

    H, etats, bornes, arret = cas_3_distillation_rh()
    assert round(H, 5) == 0.5004 and round(etats["départ"][0], 5) == 0.59192 and round(etats["départ"][1], 5) == 0.09152
    assert round(etats["après"][0], 5) == 0.5074 and round(etats["après"][1], 5) == 0.007 and arret
    assert round(etats["cible dure"][0], 5) == 0.64018 and round(etats["cible dure"][1], 5) == 0.13978
    assert round(etats["départ"][2], 5) == 0.51083 and [round(b, 5) for b in bornes] == [0.73967, 0.85238]
    assert 0.2 * 400 == 80

    p0, g0, trace, trace_m10, faux, eta_star, dec4 = cas_4_tva_btp()
    assert r5(p0) == [0.66524, 0.24473, 0.09003] and round(-math.log(p0[1]), 5) == 1.40761
    assert r5(trace[0][0]) == [1.66738, 1.37764, -0.04502] and r5(trace[0][1]) == [0.51843, 0.38802, 0.09354]
    assert round(-math.log(trace[0][1][1]), 5) == 0.94669 and len(trace) == 2 and r5(trace[1][1]) == [0.39366, 0.5185, 0.08784]
    assert len(trace_m10) == 3 and round(eta_star, 4) == 0.8439
    assert r5(trace[1][0]) == [1.40816, 1.68362, -0.09179] and r5(gradient_logits(trace[0][0], [0, 1, 0])) == [0.51843, -0.61198, 0.09354]
    assert r5(faux[0][1]) == [0.77983, 0.14101, 0.07916] and round(-math.log(faux[0][1][1]), 5) == 1.95893
    assert dec4 == "revue humaine" and 0.05 * 200000 == 10000

    # Corrigé
    p3 = softmax([0, 0])
    e6 = (autres_b - math.log(0.2)) / 5
    e7 = -math.log(sum(lot) / 5)
    print("Corrigé")
    print(f"  ex1 {-math.log(0.25):.3f} et {-math.log(0.5):.3f} ; ex3 p = {p3}, L = {-math.log(p3[0]):.3f},"
          f" gradient {[p3[0] - 1, p3[1]]} ; ex5 {3.0 / 3.3:.0%}")
    print(f"  ex6 B : perte {e6:.5f} < {res2['A'][0]:.5f} ; ex7 −ln(moyenne) {e7:.5f} -> PPL {math.exp(e7):.5f} au lieu de"
          f" {math.exp(moy1):.5f}")
    assert round(-math.log(0.25), 3) == 1.386 and p3 == [0.5, 0.5] and round(3.0 / 3.3, 2) == 0.91
    assert round(e6, 5) == 0.36132 and e6 < res2["A"][0] and round(-math.log(0.2), 5) == 1.60944
    assert round(e7, 5) == 0.63488 and round(math.exp(e7), 5) == 1.88679 and sum(lot) / 5 == 0.53 and e7 < moy1
    assert round(math.log(2), 3) == 0.693 and round(2 * math.log(2), 3) == 1.386
    # nombres cités dans le texte (film, démonstrations, cas)
    assert round(math.exp(2) + math.exp(1) + 1, 5) == 11.10734 and round(math.exp(2), 5) == 7.38906 and round(math.e, 5) == 2.71828
    assert round(-math.log(0.5) + math.log(0.9), 5) == 0.58779 and round(math.log(10), 5) == 2.30259
    assert round(-math.log(0.05) / -math.log(0.9), 1) == 28.4 and round(-math.log(0.001) / -math.log(0.9), 1) == 65.6
    assert round(math.exp(-0.1), 3) == 0.905 and round(20 / (1 / 0.9)) == 18 and round(math.log(7), 5) == 1.94591
    assert math.isclose(-math.log(0.1) + math.log(0.7), math.log(7))
    assert round(sum((0.95, 0.99, 0.9, 0.97, 0.02)) / 5, 3) == 0.766 and round(sum((0.7, 0.8, 0.6, 0.7, 0.4)) / 5, 2) == 0.64
    assert round(5 * res2["A"][0] - autres_b, 5) == 2.16645 and round(1 - 0.02, 2) == 0.98 and 1 - 0.2 == 0.8 < 0.9
    assert r5([0.5 * g for g in g0]) == [0.33262, -0.37764, 0.04502] and 4 * 0 + 1 * 50 == 50 < 250
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
film : −ln 0.9 = 0.10536 ; −ln 0.5 = 0.69315 ; −ln 0.05 = 2.99573 ; −ln 0.7 = 0.35667 ; −ln 0.1 = 2.30259 ; −ln 0.01 = 4.60517
démo 1 : one-hot 0.35667 = −ln 0.7 ; cible lissée 0.51661
démo 2 : −ln 1 = 0 ; −ln 0.01 = 4.60517 ; −ln 0.001 = 6.90776 ; « probabilité » 1.2 : -0.18232 < 0
démo 3 : L = 1.20397, H(y) = ln 2 = 0.69315, KL = 0.51083
  ln x <= x − 1 : x = 0.1 : -2.30259 <= -0.9 ; x = 0.5 : -0.69315 <= -0.5 ; x = 1.0 : 0.00000 <= 0.0 ; x = 2.0 : 0.69315 <= 1.0 ; x = 7.0 : 1.94591 <= 6.0
démo 4 : p [0.66524, 0.24473, 0.09003] ; gradient p − y [0.66524, -0.75527, 0.09003] ; cible (0 ; 2 ; 0) : [1.33048, -1.51054, 0.18006]
démo 5 : perte moyenne 1.00781 ; PPL = e^L = 2.73959 = (Π q)^(−1/5)
démo 6 : −ln 0.99 = 0.01005 quel que soit q ; ‖p − y‖₁ = 1.51054 = 2(1 − p_b)
cas 1 PUBLIC : pertes [0.10536, 0.51083, 2.99573, 0.22314, 1.20397] ; moyenne 1.00781 ; PPL 2.73959 ; part du token rare 59%
  part avec 1 − q : 40% ; q de bascule 0.12960 ; si q = 0.1 : moyenne 0.86918, PPL 2.38495 ; décision : revue de l'exemple et nom copié par outil
cas 2 ASSUR : A perte 0.47272, exactitude 80%, coût 250 AED ; B perte 0.82184, exactitude 80%, coût 8000 AED
  pertes A [0.35667, 0.22314, 0.51083, 0.35667, 0.91629] ; pertes B [0.05129, 0.01005, 0.10536, 0.03046, 3.91202]
  bascule du pire dossier de B : 0.11458 ; choix : modèle A
cas 3 RH : H(y) 0.50040 ; départ L 0.59192, KL 0.09152 ; après L 0.50740, KL 0.00700
  cible dure : L souple 0.64018, KL 0.13978 ; KL < 0.01 pour q dans [0.73967 ; 0.85238] ; arrêt : True
cas 4 BTP : p [0.66524, 0.24473, 0.09003] ; L 1.40761 ; gradient [0.66524, -0.75527, 0.09003] ; erreur évitée 10000 AED
  pas 1 : z [1.66738, 1.37764, -0.04502], p [0.51843, 0.38802, 0.09354] ; 2 pas à η = 0.5, 3 à η = 0.45 ; η* = 0.8439
  pas 2 : z [1.40816, 1.68362, -0.09179], p [0.39366, 0.5185, 0.08784]
  signe inversé : p [0.77983, 0.14101, 0.07916], L 1.95893 ; p final [0.39366, 0.5185, 0.08784] ; décision : revue humaine
Corrigé
  ex1 1.386 et 0.693 ; ex3 p = [0.5, 0.5], L = 0.693, gradient [-0.5, 0.5] ; ex5 91%
  ex6 B : perte 0.36132 < 0.47272 ; ex7 −ln(moyenne) 0.63488 -> PPL 1.88679 au lieu de 2.73959
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme calcule la perte d'entropie croisée d'une prédiction et son gradient par rapport aux logits, puis la perte moyenne d'un lot.

```text
ALGORITHME EntropieCroisée
ENTRÉES : logits z₁ … zₖ, cible y₁ … yₖ (somme 1)
SORTIE  : (perte L, gradient g)

  SI |Σ yᵢ − 1| > tolérance ALORS ERREUR          (sinon le gradient n'est plus p − y)
  p ← Softmax(z)
  L ← 0
  POUR i DE 1 À k FAIRE
      SI yᵢ > 0 ALORS
          SI pᵢ ≤ 0 ALORS ERREUR                   (perte infinie)
          L ← L − yᵢ × ln pᵢ
  FIN POUR
  POUR i DE 1 À k FAIRE
      gᵢ ← pᵢ − yᵢ
  FIN POUR
  RETOURNER L, g

ALGORITHME PerteDUnLot
ENTRÉE : probabilités données au bon token q₁ … qₙ
SORTIE : perte moyenne, ou INDÉFINI si n = 0
  SI n = 0 ALORS RETOURNER INDÉFINI
  RETOURNER la moyenne des −ln qₜ
```

**Complexité.** O(k) par prédiction pour la softmax, la perte et le gradient. Un lot de n tokens coûte O(n × k). Ne calculer la somme que sur les yᵢ > 0 évite ln 0 avec une cible one-hot.

**Du squelette au code.** EntropieCroisée combine `softmax` et `entropie_croisee(y, p)`, qui refuse une cible posée sur une probabilité nulle ; le gradient est la fonction `gradient_logits(z, y)`, qui vérifie la somme de la cible, et la liste `grad` de `main` est vérifiée par différences finies. PerteDUnLot est la fonction `perte_moyenne`, ainsi que la liste `pertes` et sa moyenne `moy`, dont l'exponentielle donne la perplexité (fiche 32). Les quatre cas sont `cas_1_lot_public`, `cas_2_triage_assurance`, `cas_3_distillation_rh` et `cas_4_tva_btp` ; le dernier enchaîne des pas de descente de gradient dans sa fonction interne `descendre`.
