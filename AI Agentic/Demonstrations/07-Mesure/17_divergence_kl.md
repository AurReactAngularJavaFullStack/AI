# 17 — Divergence KL : démonstrations

> Fiche : [17 — Divergence KL](<../../Images/07-Mesure/17_divergence_kl.md>) · Image : `17_divergence_kl.jpg` · Leçon : [Étape 50 — Précision, rappel, F1 et KL](<../../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4. log désigne ici le logarithme naturel ln.

## La formule

$$
D_{KL}(P \parallel Q) = \sum_{x} P(x) \times \log\left( \frac{P(x)}{Q(x)} \right)
$$

La divergence de Kullback-Leibler mesure combien une distribution Q s'écarte d'une distribution de référence P, du point de vue de P. Elle sert à surveiller une dérive ou à garder un modèle proche d'une référence.

## Les symboles, un par un

$$
P
$$

**P** : la distribution de référence (trafic du mois dernier, politique validée, modèle enseignant), une liste de probabilités ≥ 0 qui somment à 1 ; en Python, le premier argument de `kl(P, Q)`.

$$
Q
$$

**Q** : la distribution comparée (trafic de la semaine, politique entraînée, modèle élève), sur les mêmes issues que P ; en Python, le second argument de `kl(P, Q)`.

$$
x
$$

**x** : une issue possible (une catégorie de demande, une action, une tranche de prix, un service) ; en Python, la position commune dans les deux listes parcourues par `zip(P, Q)`.

$$
\frac{P(x)}{Q(x)}
$$

**P(x) / Q(x)** : l'écart local entre les deux distributions, sans unité ; il vaut 1 quand elles sont d'accord sur x, plus de 1 quand Q sous-estime x, moins de 1 quand Q le surestime.

$$
\log
$$

**log** : le logarithme naturel ; la divergence se lit alors en nats (en bits avec log₂) ; en Python, `math.log`.

$$
D_{KL}(P \parallel Q)
$$

**D(P‖Q)** : la divergence, un réel ≥ 0, éventuellement +∞, nul si et seulement si P = Q, et pas symétrique ; en Python, `kl(P, Q)`, qui renvoie `math.inf` quand Q oublie une issue que P juge possible.

$$
H(P),\ H(P, Q)
$$

**H(P)** : l'entropie de P (fiche 21), `entropie(P)` ; **H(P, Q)** : l'entropie croisée, la perte d'entraînement d'un modèle Q sur des données de loi P (fiche 06), `entropie_croisee(P, Q)`.

## Le mécanisme, avant les preuves

Deux listes de probabilités entrent, P et Q, sur les mêmes issues. Pour chaque issue, on forme le rapport P(x) / Q(x) : il dit dans quel sens et de combien Q se trompe sur x. Le logarithme transforme ce rapport en un écart signé : 0 quand le rapport vaut 1, positif quand Q sous-estime x, négatif quand il le surestime. On prend le logarithme plutôt que le rapport lui-même parce qu'il rend additifs les effets multiplicatifs et parce qu'il est la quantité d'information gagnée en apprenant que x s'est produit. Chaque écart est ensuite pondéré par P(x) : on regarde le monde avec les yeux de P, donc une issue fréquente sous P compte beaucoup et une issue impossible sous P ne compte pas. La somme pondérée peut contenir des termes négatifs, mais le total ne l'est jamais (démonstration 1). Inverser P et Q change les poids, donc la question posée (démonstration 3). Si Q donne 0 à une issue que P juge possible, le rapport est infini et la divergence aussi (démonstration 4). Pour de petits écarts, la divergence se comporte comme la moitié d'un écart quadratique relatif (démonstration 6) : doubler l'écart la multiplie par environ 4. Ce qui sort est un nombre en nats, que l'agent compare à un seuil.

Petit film chiffré avec P = (0,5 ; 0,5) et Q = (0,9 ; 0,1). Rapports : 0,5 / 0,9 ≈ 0,5556 et 0,5 / 0,1 = 5. Logarithmes : ln 0,5556 ≈ −0,58779 et ln 5 ≈ 1,60944. Pondération par P : 0,5 × (−0,58779) ≈ −0,29389 et 0,5 × 1,60944 ≈ 0,80472. Somme : −0,29389 + 0,80472 = 0,51083 nat. Le terme négatif ne suffit pas à compenser le terme positif, parce que Q a écrasé la seconde issue d'un facteur 5 alors qu'il n'a gonflé la première que d'un facteur 1,8.

## Démonstration 1 — La KL est toujours positive ou nulle (inégalité de Gibbs)

**Ce qu'on démontre.** Pour deux distributions P et Q sur le même ensemble fini, avec Q(x) > 0 partout où P(x) > 0 (sinon la divergence vaut +∞, démonstration 4) :

$$
D_{KL}(P \parallel Q) \ge 0
$$

**L'idée.** On utilise une seule inégalité, ln u ≤ u − 1 pour tout u > 0 (fiche 06, démonstration 3, et exercice 3) : la courbe du logarithme reste sous sa tangente en 1. Appliquée au rapport Q / P et moyennée sous P, elle donne une somme de Q moins une somme de P, qui ne dépasse pas 1 − 1 = 0.

**La preuve, pas à pas.**

**Étape 1.** On note S l'ensemble des issues où P(x) > 0 ; les autres termes valent 0 par convention. On change le signe en inversant le rapport, parce que ln(P/Q) = −ln(Q/P) :

$$
-D_{KL}(P \parallel Q) = \sum_{x \in S} P(x) \ln \frac{Q(x)}{P(x)}
$$

**Étape 2.** On applique ln u ≤ u − 1 avec u = Q(x) / P(x) > 0, et on multiplie par P(x) > 0, ce qui garde le sens de l'inégalité :

$$
\sum_{x \in S} P(x) \ln \frac{Q(x)}{P(x)} \le \sum_{x \in S} P(x) \left( \frac{Q(x)}{P(x)} - 1 \right) = \sum_{x \in S} Q(x) - \sum_{x \in S} P(x)
$$

**Étape 3.** La somme de P sur S vaut 1, parce que P est nulle hors de S ; la somme de Q sur S vaut au plus 1, parce que Q est une distribution :

$$
\sum_{x \in S} Q(x) - 1 \le 1 - 1 = 0
$$

**Étape 4.** En enchaînant, −D ≤ 0, donc D ≥ 0. ∎

**Vérification chiffrée.** P = (0,5 ; 0,5), Q = (0,9 ; 0,1). Termes de l'étape 2 : ln(0,9 / 0,5) ≈ 0,58779 ≤ 0,8 et ln(0,1 / 0,5) ≈ −1,60944 ≤ −0,8. La somme pondérée vaut −0,51083 ≤ Σ Q − Σ P = 0. Contre-exemple quand l'hypothèse « Q est une distribution » manque : avec des scores bruts non normalisés Q = (0,8 ; 0,8), dont la somme vaut 1,6, la formule donne 0,5 ln(0,5 / 0,8) + 0,5 ln(0,5 / 0,8) = ln 0,625 ≈ −0,47000 : une « divergence » négative, sans aucun sens.

**Ce que la preuve révèle du mécanisme.** Les termes négatifs existent (Q surestime certaines issues), mais ils sont toujours payés par des termes positifs plus grands ailleurs, parce que Q ne peut pas surestimer partout : sa masse totale vaut 1. La seconde inégalité perd exactement la masse que Q met hors du support de P.

**Conséquence pour un agent.** Avant de calculer une KL, on vérifie que P et Q sont des distributions (valeurs ≥ 0, somme 1) : le programme lève `ValueError` sinon. Des sorties de modèle brutes (logits, scores) passent d'abord par une normalisation, softmax ou division par la somme.

## Démonstration 2 — Elle est nulle si et seulement si P = Q

**Ce qu'on démontre.** Avec les hypothèses de la démonstration 1 :

$$
D_{KL}(P \parallel Q) = 0 \iff P = Q
$$

**L'idée.** La preuve de Gibbs contient deux inégalités. La divergence n'est nulle que si les deux sont des égalités ; or ln u = u − 1 seulement en u = 1, et Σ Q = 1 sur le support de P seulement si Q ne met rien ailleurs.

**La preuve, pas à pas.**

**Étape 1.** Si P = Q, chaque terme vaut P(x) ln 1 = 0, donc D = 0 : c'est le sens facile.

**Étape 2.** Réciproquement, supposons D = 0. L'égalité dans l'étape 2 de la démonstration 1 exige ln u = u − 1 pour chaque x de S, parce que des écarts tous ≥ 0 pondérés par des P(x) > 0 ne somment à 0 que s'ils sont tous nuls. La fonction u − 1 − ln u ne s'annule qu'en u = 1 (exercice 3) :

$$
\frac{Q(x)}{P(x)} = 1 \quad \text{pour tout } x \in S
$$

**Étape 3.** L'égalité dans l'étape 3 exige que la somme de Q sur S vaille 1, donc que Q soit nulle hors de S, là où P l'est aussi. Donc Q = P partout. ∎

**Vérification chiffrée.** D(P‖P) = 0 pour P = (0,6 ; 0,4). Un écart d'un point, Q = (0,61 ; 0,39), donne déjà 0,6 ln(0,6 / 0,61) + 0,4 ln(0,4 / 0,39) ≈ 0,000210 > 0. Le rôle de l'étape 3 : P = (0,5 ; 0,5 ; 0) et Q = (0,4 ; 0,4 ; 0,2) ont un rapport constant 0,8 sur le support de P, mais Q met 0,2 hors du support, et D = ln(1 / 0,8) = ln 1,25 ≈ 0,22314 > 0.

**Ce que la preuve révèle du mécanisme.** La KL ne s'annule pas « à peu près » : le moindre écart donne une valeur strictement positive, même minuscule. Un écart d'un point de pourcentage donne une divergence de l'ordre de 10⁻⁴, ce que la démonstration 6 explique.

**Conséquence pour un agent.** Un seuil de dérive n'est jamais 0 : deux échantillons du même trafic donnent toujours une KL positive à cause du hasard. On fixe un seuil au-dessus de ce bruit (0,05 dans les cas ci-dessous, valeur illustrative à recaler sur l'historique).

## Démonstration 3 — Elle n'est pas symétrique

**Ce qu'on démontre.** Il existe des distributions P et Q telles que :

$$
D_{KL}(P \parallel Q) \ne D_{KL}(Q \parallel P)
$$

La KL n'est donc pas une distance au sens mathématique.

**L'idée.** Les deux sens utilisent les mêmes rapports, mais pas les mêmes poids : D(P‖Q) pondère par P, D(Q‖P) par Q. Une issue fréquente sous P et rare sous Q pèse lourd dans le premier sens et peu dans le second.

**La preuve, pas à pas.**

**Étape 1.** On prend P = (0,5 ; 0,5) et Q = (0,9 ; 0,1) et on calcule le premier sens, terme par terme :

$$
D(P \parallel Q) = 0{,}5 \ln \frac{0{,}5}{0{,}9} + 0{,}5 \ln \frac{0{,}5}{0{,}1} \approx -0{,}29389 + 0{,}80472 = 0{,}51083
$$

**Étape 2.** Le second sens, avec les poids de Q :

$$
D(Q \parallel P) = 0{,}9 \ln \frac{0{,}9}{0{,}5} + 0{,}1 \ln \frac{0{,}1}{0{,}5} \approx 0{,}52901 - 0{,}16094 = 0{,}36806
$$

**Étape 3.** 0,51083 ≠ 0,36806 : un seul contre-exemple suffit à réfuter la symétrie. ∎

**Vérification chiffrée.** La différence vient du terme de la seconde issue : sous P, elle pèse 0,5 et contribue 0,80472 ; sous Q, elle ne pèse que 0,1 et contribue −0,16094. Si l'on veut une mesure symétrique, on additionne les deux sens : 0,51083 + 0,36806 = 0,87889 (divergence de Jeffreys).

**Ce que la preuve révèle du mécanisme.** D(P‖Q) punit surtout une issue que P rend fréquente et que Q rend rare ; D(Q‖P) punit une issue que Q rend fréquente et que P rend rare (leçon 50). Le sens choisit la question : « Q explique-t-il bien ce que P produit ? » ou l'inverse.

**Conséquence pour un agent.** Le sens est une décision d'ingénierie, écrite dans la documentation du garde-fou. Pour une dérive où l'on craint l'apparition d'une catégorie nouvelle, on regarde D(Q‖P), qui pèse avec le trafic actuel ; dans le doute, on calcule les deux (cas 1).

## Démonstration 4 — Elle devient infinie si Q oublie une possibilité

**Ce qu'on démontre.** S'il existe une issue x₀ avec P(x₀) > 0 et Q(x₀) = 0, alors :

$$
D_{KL}(P \parallel Q) = +\infty
$$

**L'idée.** Le terme de x₀ contient ln(P(x₀) / Q(x₀)), qui grandit sans limite quand Q(x₀) tend vers 0. Les autres termes sont finis : ils ne peuvent pas le compenser.

**La preuve, pas à pas.**

**Étape 1.** Pour q > 0, le terme de x₀ vaut P(x₀) [ln P(x₀) − ln q], et −ln q tend vers +∞ quand q tend vers 0, parce que ln q tend vers −∞ :

$$
\lim_{q \to 0^+} P(x_0) \ln \frac{P(x_0)}{q} = +\infty
$$

**Étape 2.** Chacun des autres termes est fini, et leur somme est au moins −1 par l'étape 2 de la démonstration 1 appliquée à eux seuls. Une somme qui contient un terme infini et des termes bornés inférieurement est infinie ; on pose donc D = +∞. ∎

**Vérification chiffrée.** Avec P(x₀) = 0,9 : q = 10⁻⁶ donne 0,9 ln(0,9 / 10⁻⁶) ≈ 12,34 ; q = 10⁻⁹ donne ≈ 18,56 ; q = 0 donne l'infini. Le sens inverse n'a pas ce problème : une issue que P juge impossible ne compte pas, si bien que D((1 ; 0)‖(0,5 ; 0,5)) = ln 2, fini, alors que D((0,5 ; 0,5)‖(1 ; 0)) est infini.

**Ce que la preuve révèle du mécanisme.** La KL punit sans limite un modèle sûr de lui qui déclare impossible ce qui arrive. Plus Q est petit sur x₀, plus la pénalité croît, comme ln(1/q) : chaque division de q par 1 000 ajoute 0,9 × ln 1 000 ≈ 6,2 nats.

**Conséquence pour un agent.** Sur des fréquences observées, une catégorie absente de la semaine donne Q(x) = 0. On lisse les comptes de façon explicite et documentée (lissage de Laplace, +1 par catégorie, comme le recommande la leçon 50), au lieu de remplacer 0 par un epsilon caché dont la valeur fixerait arbitrairement le résultat (cas 3).

## Démonstration 5 — Entropie croisée = entropie + KL

**Ce qu'on démontre.** Pour P et Q avec Q > 0 sur le support de P :

$$
H(P, Q) = -\sum_x P(x) \ln Q(x) = H(P) + D_{KL}(P \parallel Q)
$$

**L'idée.** On glisse P(x) au numérateur et au dénominateur dans le logarithme de Q : ln Q = ln P − ln(P/Q). La première partie donne l'entropie, la seconde la divergence.

**La preuve, pas à pas.**

**Étape 1.** Pour chaque x du support, on écrit Q(x) = P(x) × Q(x) / P(x), puis on utilise ln(ab) = ln a + ln b :

$$
-\ln Q(x) = -\ln P(x) + \ln \frac{P(x)}{Q(x)}
$$

**Étape 2.** On multiplie par P(x) et on additionne sur x, parce qu'une somme se distribue sur une addition :

$$
-\sum_x P(x) \ln Q(x) = -\sum_x P(x) \ln P(x) + \sum_x P(x) \ln \frac{P(x)}{Q(x)} = H(P) + D_{KL}(P \parallel Q)
$$

∎

**Vérification chiffrée.** Avec les distributions du cas 1, P = (0,5 ; 0,3 ; 0,15 ; 0,05) et Q = (0,35 ; 0,3 ; 0,2 ; 0,15) : H(P) ≈ 1,14212, D(P‖Q) ≈ 0,08025 et H(P, Q) ≈ 1,22237 = 1,14212 + 0,08025. Le programme vérifie l'identité sur trois couples de distributions.

**Ce que la preuve révèle du mécanisme.** H(P) ne dépend pas de Q : c'est l'incertitude propre des données, que personne ne descend. Comme D ≥ 0, l'entropie croisée est toujours au moins H(P), et l'écart est exactement l'erreur du modèle.

**Conséquence pour un agent.** Minimiser la perte d'entropie croisée d'un modèle, ou d'un élève en distillation, revient exactement à minimiser sa KL par rapport aux données ou à l'enseignant (cas 4). La perplexité de la leçon 52 est l'exponentielle de cette entropie croisée.

## Démonstration 6 — Pour de petits écarts, la KL est quadratique

**Ce qu'on démontre.** Si Q(x) = P(x) (1 + δₓ) avec des δₓ petits, alors :

$$
D_{KL}(P \parallel Q) \approx \frac{1}{2} \sum_x \frac{(Q(x) - P(x))^2}{P(x)}
$$

**L'idée.** On développe le logarithme autour de 1. Le terme du premier ordre disparaît, parce que P et Q ont la même masse totale ; il reste le terme du second ordre, un écart au carré.

**La preuve, pas à pas.**

**Étape 1.** On pose δₓ = Q(x)/P(x) − 1 ; comme P et Q somment à 1, la somme de P(x) δₓ = Σ (Q(x) − P(x)) vaut 0 :

$$
\sum_x P(x)\, \delta_x = \sum_x Q(x) - \sum_x P(x) = 0
$$

**Étape 2.** On réécrit la divergence avec ln(P/Q) = −ln(1 + δ), puis on développe ln(1 + δ) = δ − δ²/2 + δ³/3 − …, valable pour |δ| < 1 :

$$
D_{KL}(P \parallel Q) = -\sum_x P(x) \ln(1 + \delta_x) = -\sum_x P(x)\,\delta_x + \frac{1}{2} \sum_x P(x)\,\delta_x^2 - \dots
$$

**Étape 3.** Le premier terme est nul par l'étape 1, et P(x) δₓ² = (Q(x) − P(x))² / P(x) ; on garde le terme du second ordre :

$$
D_{KL}(P \parallel Q) \approx \frac{1}{2} \sum_x \frac{(Q(x) - P(x))^2}{P(x)}
$$

∎

**Vérification chiffrée.** P = (0,70 ; 0,20 ; 0,10) et Q = (0,65 ; 0,25 ; 0,10), l'exemple « proche » de la leçon 50 : la valeur exacte vaut 0,0072 et l'approximation 0,5 × (0,0025 / 0,70 + 0,0025 / 0,20) ≈ 0,5 × (0,003571 + 0,0125) ≈ 0,008036. En doublant l'écart, Q = (0,60 ; 0,30 ; 0,10), la valeur exacte passe à 0,02681 (approximation 0,032143, avec 0,01 / 0,7 ≈ 0,014286) : la divergence est multipliée par 3,70, près du facteur 4 annoncé.

**Ce que la preuve révèle du mécanisme.** Près de P, la KL est une distance au carré pondérée par 1/P : un même écart absolu coûte plus cher sur une issue rare. Un écart relatif de 1 % sur chaque issue donne une divergence d'environ ½ × 0,01² = 0,00005 : minuscule.

**Conséquence pour un agent.** Un seuil de KL se lit comme le carré d'un seuil d'écart : pour signaler un écart deux fois plus petit, il faut un seuil environ quatre fois plus bas. Cela explique aussi pourquoi un seuil comme 0,05 ne réagit qu'à des déplacements de plusieurs points sur des issues rares.

## Exemple simple, à la main

P = (0,5 ; 0,5) et Q = (0,9 ; 0,1). Les rapports valent 0,5 / 0,9 ≈ 0,5556 et 0,5 / 0,1 = 5, leurs logarithmes −0,58779 et 1,60944 :

$$
D_{KL}(P \parallel Q) = 0{,}5 \ln \frac{0{,}5}{0{,}9} + 0{,}5 \ln \frac{0{,}5}{0{,}1} \approx 0{,}5 \times (-0{,}58779) + 0{,}5 \times 1{,}60944 \approx 0{,}51083
$$

Dans l'autre sens, les rapports valent 0,9 / 0,5 = 1,8 et 0,1 / 0,5 = 0,2 :

$$
D_{KL}(Q \parallel P) = 0{,}9 \ln 1{,}8 + 0{,}1 \ln 0{,}2 \approx 0{,}52901 - 0{,}16094 = 0{,}36806
$$

| issue | P | Q | ln(P/Q) | P × ln(P/Q) | Q × ln(Q/P) |
| --- | --- | --- | --- | --- | --- |
| 1 | 0,5 | 0,9 | −0,58779 | −0,29389 | 0,52901 |
| 2 | 0,5 | 0,1 | 1,60944 | 0,80472 | −0,16094 |
| somme | 1 | 1 | | 0,51083 | 0,36806 |

## Cas d'usage complexes, démontrés

### Cas 1 — Groupe de construction à Dubaï : détecter une dérive des demandes reçues par l'agent fournisseurs

**Contexte.** Un groupe de construction sur de grands chantiers à Dubaï fait traiter par un agent les demandes de ses fournisseurs et sous-traitants : factures (avec TVA à 5 %), livraisons de matériaux, comptes fournisseurs et litiges (retenues de garantie, pénalités). L'agent a été évalué sur la répartition du trimestre de référence. Il reçoit 12 000 demandes par semaine ; il résout 90 % des demandes courantes mais seulement 60 % des litiges, les autres étant escaladés à 90 AED pièce (chiffres illustratifs). Question : la répartition de la semaine s'est-elle assez éloignée de la référence pour réévaluer l'agent ?

**Données.**

- Référence P = (0,5 ; 0,3 ; 0,15 ; 0,05) pour factures, livraisons, comptes, litiges.
- Semaine : 4 200, 3 600, 2 400 et 1 800 demandes sur 12 000, soit Q = (0,35 ; 0,30 ; 0,20 ; 0,15).
- Seuil d'alerte : 0,05 nat (illustratif) ; taux d'échec 10 % hors litiges, 40 % sur les litiges ; escalade 90 AED.

**Calcul pas à pas.**

**Étape 1.** Termes de D(Q‖P), arrondis à 5 décimales : 0,35 ln(0,35 / 0,5) = 0,35 × ln 0,7 ≈ 0,35 × (−0,35667) ≈ −0,12484 ; 0,30 ln 1 = 0 ; 0,20 ln(0,20 / 0,15) ≈ 0,20 × 0,28768 ≈ 0,05754 ; 0,15 ln(0,15 / 0,05) = 0,15 × ln 3 ≈ 0,15 × 1,09861 ≈ 0,16479.

$$
D(Q \parallel P) \approx -0{,}12484 + 0 + 0{,}05754 + 0{,}16479 = 0{,}09749
$$

**Étape 2.** Termes de D(P‖Q) : 0,5 ln(0,5 / 0,35) ≈ 0,17834 ; 0 ; 0,15 ln(0,15 / 0,20) ≈ −0,04315 ; 0,05 ln(0,05 / 0,15) ≈ −0,05493.

$$
D(P \parallel Q) \approx 0{,}17834 + 0 - 0{,}04315 - 0{,}05493 = 0{,}08025
$$

**Étape 3.** Les deux sens dépassent 0,05. Dans D(Q‖P), le terme des litiges (0,16479) est le plus gros : c'est la catégorie qui a triplé. Dans D(P‖Q), le terme dominant est celui des factures (0,17834), devenues moins fréquentes, et le terme des litiges est négatif : vu depuis la référence, les litiges étaient rares et comptent peu.

**Étape 4.** Coût de la dérive : échecs attendus avec la référence, 12 000 × (0,05 × 0,4 + 0,95 × 0,1) = 12 000 × 0,115 = 1 380 ; avec la semaine, 12 000 × (0,15 × 0,4 + 0,85 × 0,1) = 12 000 × 0,145 = 1 740. Soit 360 escalades de plus, 360 × 90 = 32 400 AED par semaine.

**Décision de l'agent.** Alerte : D(Q‖P) ≈ 0,0975 > 0,05. L'agent de surveillance déclenche une réévaluation de l'agent fournisseurs sur les litiges et prévient l'équipe qui les traite. Le rapport cite la contribution de chaque catégorie, pour que l'équipe voie tout de suite que les litiges en sont la cause.

**Contre-calcul.** Le volume total ne bouge pas, 12 000 demandes : un suivi du seul volume ne voit rien, et la dérive coûte 32 400 AED par semaine d'escalades sans que personne ne sache pourquoi (illustratif).

**Sensibilité.** Si seuls les litiges montaient, en prenant leur part aux factures, Q(x) = (0,55 − x ; 0,30 ; 0,15 ; x), l'alerte D(Q‖P) = 0,05 se déclencherait pour x ≈ 0,1291 : dès que les litiges dépassent 12,9 % des demandes, contre 5 % en référence.

**En production.** On calcule chaque semaine les deux sens de la divergence et la contribution de chaque catégorie, sur des comptes lissés si une catégorie est vide (démonstration 4) ; l'alerte part au-dessus de 0,05. On suit aussi le taux d'escalade des litiges, qui confirme ou non l'effet métier de la dérive.

### Cas 2 — Banque de détail de Dubaï : choisir le coefficient β qui retient un assistant près de sa politique validée

**Contexte.** Une banque de détail de Dubaï affine par renforcement l'assistant de son service client. Pour chaque conversation, l'assistant choisit entre trois actions : répondre directement, proposer une offre, transférer à un conseiller. La politique de référence, notée π₀ (variable `ref`), a été validée par la conformité. L'entraînement maximise récompense − β × KL(π‖π₀) pour que la nouvelle politique ne s'éloigne pas trop de la référence. Deux candidates sortent de l'entraînement ; 20 000 conversations par mois (chiffres illustratifs). Question : laquelle déployer, et avec quel β ?

**Données.**

- π₀ = (0,5 ; 0,3 ; 0,2).
- Candidate A : π = (0,7 ; 0,2 ; 0,1), récompense moyenne 0,80 (score d'un modèle de récompense, illustratif).
- Candidate B : (0,9 ; 0,07 ; 0,03), récompense 0,86.
- β proposé par l'équipe d'entraînement : 0,1 ; β fixé par l'équipe des risques : 0,25 (illustratifs). 8 % des conversations sont des réclamations qui exigent un conseiller (illustratif).

**Calcul pas à pas.**

**Étape 1.** KL(A‖π₀) = 0,7 ln 1,4 + 0,2 ln(2/3) + 0,1 ln 0,5 ≈ 0,08512.

**Étape 2.** KL(B‖π₀), terme par terme : 0,9 ln 1,8 ≈ 0,52901 ; 0,07 ln(0,07 / 0,3) ≈ −0,10187 ; 0,03 ln 0,15 ≈ −0,05691 ; total ≈ 0,37022.

**Étape 3.** Objectifs avec β = 0,1 : A vaut 0,80 − 0,1 × 0,08512 ≈ 0,80 − 0,00851 = 0,79149 ; B vaut 0,86 − 0,03702 = 0,82298. B gagne.

**Étape 4.** Objectifs avec β = 0,25 : A vaut 0,80 − 0,02128 = 0,77872 ; B vaut 0,86 − 0,09256 = 0,76744. A gagne.

**Étape 5.** β de bascule, où les deux objectifs sont égaux :

$$
0{,}80 - \beta \times 0{,}08512 = 0{,}86 - \beta \times 0{,}37022 \iff \beta = \frac{0{,}06}{0{,}28510} \approx 0{,}21045
$$

**Décision de l'agent.** Avec le β = 0,25 fixé par l'équipe des risques, on déploie A. B gagne 0,06 de récompense en s'éloignant beaucoup de la référence : ses transferts vers un conseiller tombent de 20 % à 3 %.

**Contre-calcul.** Sans terme KL (β = 0), on déploierait B, la meilleure récompense. Les transferts passeraient de 20 000 × 0,2 = 4 000 à 20 000 × 0,03 = 600 par mois (A en garde 20 000 × 0,1 = 2 000), alors que 0,08 × 20 000 = 1 600 réclamations exigent un conseiller : au moins 1 600 − 600 = 1 000 réclamations par mois ne seraient pas transférées.

**Sensibilité.** La décision bascule à β ≈ 0,21045 ; l'équipe des risques a donc une marge de 0,04 sous 0,25. Si une nouvelle version de B atteignait une récompense de 0,90, le β de bascule monterait à 0,1 / 0,28510 ≈ 0,35075 > 0,25 et B l'emporterait : l'objectif seul ne suffit pas, il faut aussi un garde-fou direct sur le taux de transfert.

**En production.** On mesure chaque semaine la KL entre la politique déployée et π₀ sur le trafic réel, avec une alerte au-dessus de 0,15 (illustratif), et le taux de transfert vers un conseiller, avec une alerte sous 8 %. Les règles de protection du consommateur de la CBUAE sur le traitement des réclamations sont à confirmer avec le texte en vigueur.

### Cas 3 — Agence immobilière à Dubaï et Abu Dhabi : une tranche de prix vide, et le piège de l'epsilon

**Contexte.** Une agence et un promoteur à Dubaï et Abu Dhabi utilisent un modèle d'estimation des prix entraîné sur la répartition des ventes par tranche de prix au sqft. Chaque trimestre, un agent compare la répartition des ventes récentes à celle de référence et déclenche un recalibrage du modèle (40 000 AED de travail, illustratif) si la divergence dépasse 0,05. Ce trimestre, aucune vente n'a été enregistrée dans la tranche la plus chère. Question : faut-il recalibrer ?

**Données.**

| tranche (AED/sqft) | moins de 1 000 | 1 000 à 1 500 | 1 500 à 2 000 | 2 000 à 3 000 | plus de 3 000 |
| --- | --- | --- | --- | --- | --- |
| référence, 1 000 ventes | 150 | 350 | 300 | 180 | 20 |
| trimestre, 200 ventes | 20 | 60 | 70 | 50 | 0 |

**Calcul pas à pas.**

**Étape 1.** Fréquences brutes : P = (0,15 ; 0,35 ; 0,30 ; 0,18 ; 0,02) et Q = (0,10 ; 0,30 ; 0,35 ; 0,25 ; 0). Comme Q = 0 sur la dernière tranche et P > 0, D(P‖Q) = +∞ (démonstration 4) ; l'autre sens est fini, D(Q‖P) ≈ 0,04929.

**Étape 2.** Lissage de Laplace explicite, +1 par tranche : P′ = (151 ; 351 ; 301 ; 181 ; 21) / 1 005 ≈ (0,1502 ; 0,3493 ; 0,2995 ; 0,1801 ; 0,0209) et Q′ = (21 ; 61 ; 71 ; 51 ; 1) / 205 ≈ (0,1024 ; 0,2976 ; 0,3463 ; 0,2488 ; 0,0049).

**Étape 3.** Divergences lissées :

$$
D(P' \parallel Q') \approx 0{,}04219 \qquad D(Q' \parallel P') \approx 0{,}03670
$$

**Étape 4.** Test séparé de la tranche vide : si la référence était toujours vraie, la probabilité de ne voir aucune vente à plus de 3 000 AED/sqft sur 200 vaut (1 − 0,02)²⁰⁰ ≈ 0,0176, alors qu'on en attendait 200 × 0,02 = 4.

**Décision de l'agent.** Pas de recalibrage global : avec le lissage documenté (+1), les deux sens restent sous 0,05. En revanche, l'absence de ventes de luxe, qui n'avait que 1,8 % de chances d'arriver par hasard, déclenche une vérification ciblée : flux de données incomplet, ou retournement réel de ce segment.

**Contre-calcul.** Remplacer le 0 par un epsilon caché donne n'importe quoi : avec ε = 10⁻⁹, D(P‖Q) ≈ 0,34562, 6,9 fois le seuil, et un recalibrage de 40 000 AED pour rien ; avec ε = 10⁻⁶, ≈ 0,20747. Le résultat dépend de la valeur arbitraire de ε, pas des données.

**Sensibilité.** Le choix du pseudo-compte compte aussi, mais de façon bornée : avec +0,5 au lieu de +1, D(P′‖Q′) ≈ 0,05383 dépasse le seuil. La bascule se produit pour un pseudo-compte d'environ 0,623. Le pseudo-compte et le seuil se fixent donc à l'avance, et un résultat proche du seuil mène à une revue humaine plutôt qu'à une action automatique.

**En production.** On calcule la divergence chaque trimestre avec un lissage +1 écrit dans la configuration, et un contrôle séparé « tranche vide alors qu'on en attendait au moins 3 ». Les ventes sont celles enregistrées auprès du DLD ; l'usage d'un modèle d'estimation dans une transaction et les règles de la RERA sur la publicité des prix sont à confirmer avec le texte en vigueur.

### Cas 4 — Entité de services publics en ligne : distiller un routeur bilingue sans dégrader les requêtes mélangées

**Contexte.** Une entité de services publics en ligne, accessible par UAE Pass, route 30 000 requêtes par jour vers quatre services : visas, permis, paiements, réclamations. Le routeur actuel, un grand modèle « enseignant », coûte 0,012 AED par requête ; un petit modèle « élève », distillé à partir de lui, coûte 0,002 AED (chiffres illustratifs). Les requêtes sont en arabe (45 %), en anglais (35 %) ou mélangées (20 %). Question : remplacer l'enseignant par l'élève, et pour quels segments ?

**Données.** Distributions de routage moyennes sur un jeu de test, pour (visas ; permis ; paiements ; réclamations) :

| segment | enseignant T | élève S |
| --- | --- | --- |
| arabe | 0,80 ; 0,10 ; 0,05 ; 0,05 | 0,75 ; 0,12 ; 0,07 ; 0,06 |
| anglais | 0,10 ; 0,70 ; 0,15 ; 0,05 | 0,12 ; 0,65 ; 0,17 ; 0,06 |
| mélangé | 0,60 ; 0,30 ; 0,05 ; 0,05 | 0,30 ; 0,55 ; 0,10 ; 0,05 |

Seuil d'acceptation : D(T‖S) < 0,1 par segment (illustratif) ; une requête mal routée coûte 15 AED de reprise (illustratif).

**Calcul pas à pas.**

**Étape 1.** Divergence par segment, avec l'enseignant comme référence : arabe ≈ 0,00746 ; anglais ≈ 0,00575. Pour le segment mélangé, terme par terme : 0,60 ln 2 ≈ 0,41589 ; 0,30 ln(0,30 / 0,55) ≈ 0,30 × (−0,60614) ≈ −0,18184 ; 0,05 ln 0,5 ≈ −0,03466 ; 0.

$$
D(T \parallel S)_{\text{mélangé}} \approx 0{,}41589 - 0{,}18184 - 0{,}03466 + 0 = 0{,}19939
$$

**Étape 2.** Lien avec la perte de distillation (démonstration 5) : H(T) ≈ 0,96726 et H(T, S) ≈ 1,16665 = 0,96726 + 0,19939 pour le segment mélangé.

**Étape 3.** Moyenne pondérée par le trafic : 0,45 × 0,00746 + 0,35 × 0,00575 + 0,20 × 0,19939 ≈ 0,00336 + 0,00201 + 0,03988 = 0,04525.

**Étape 4.** Économie si l'élève prend l'arabe et l'anglais : 0,80 × 30 000 = 24 000 requêtes par jour, à 0,012 − 0,002 = 0,010 AED d'économie chacune, soit 240 AED par jour.

**Décision de l'agent.** L'élève prend les requêtes en arabe et en anglais (divergences < 0,1) ; l'enseignant garde les requêtes mélangées (0,199 > 0,1), repérées avant le routage par un détecteur de langue.

**Contre-calcul.** La moyenne pondérée, 0,04525 < 0,1, dirait de tout confier à l'élève. Sur les 0,20 × 30 000 = 6 000 requêtes mélangées par jour, le service le plus probable change (visas à 0,60 pour l'enseignant, permis à 0,55 pour l'élève) : en prenant l'enseignant comme vérité, la part de bons routages tombe de 0,60 à 0,30, soit 0,30 × 6 000 = 1 800 erreurs de plus par jour et 1 800 × 15 = 27 000 AED de reprises, pour 6 000 × 0,010 = 60 AED économisés. Une moyenne cache le segment qui casse.

**Sensibilité.** L'approximation quadratique (démonstration 6) donne 0,20417 pour le segment mélangé, proche de 0,19939. Elle annonce qu'un réentraînement qui réduirait l'écart de moitié, S = (0,45 ; 0,425 ; 0,075 ; 0,05), diviserait la divergence par environ 4 : le calcul exact donne 0,04784 (rapport 4,17), sous le seuil. Un réentraînement ciblé sur des requêtes mélangées rendrait donc l'élève acceptable sur ce segment aussi.

**En production.** Sur 1 % des requêtes, l'enseignant note aussi la requête en parallèle, et l'on calcule D(T‖S) par segment de langue chaque semaine, avec une alerte au-dessus de 0,1. La normalisation de l'arabe (alef, ta marbuta, diacritiques) se fait avant les deux modèles, pour comparer ce qui est comparable. Les données des requêtes relèvent de la PDPL hors DIFC et ADGM.

## Entraînement sur feuille A4

**Exercice 1.** Calculer D(P‖P) pour P = (0,6 ; 0,4).

**Exercice 2.** P = (1 ; 0), Q = (0,5 ; 0,5). Calculer D(P‖Q) et D(Q‖P).

**Exercice 3.** Démontrer que ln u ≤ u − 1 en étudiant u − 1 − ln u.

**Exercice 4.** Pourquoi la KL d'une distribution sur n issues par rapport à l'uniforme vaut-elle ln n − H(P) ? Le vérifier pour la référence du cas 1.

**Exercice 5.** Dans le cas 2, quel β ferait passer l'objectif de la candidate A sous 0,7 ?

**Exercice 6 (cas modifié).** Dans le cas 2, l'équipe des risques accepte finalement β = 0,15. Quelle candidate déployer ? Que faut-il surveiller en plus ?

**Exercice 7 (trouver l'erreur).** Un collègue calcule la dérive du cas 1 avec Σ P ln(Q/P) et trouve −0,08025. Il conclut : « la divergence est négative, le trafic s'est rapproché de la référence ». Trouver l'erreur.

**Exercice 8 (redémontrer de mémoire).** Redémontrer l'inégalité de Gibbs et son cas d'égalité (démonstrations 1 et 2), en disant où sert chaque hypothèse.

## Corrigé

**Exercice 1.** Chaque terme vaut 0,6 ln 1 = 0 et 0,4 ln 1 = 0 : D = 0, comme l'annonce la démonstration 2.

**Exercice 2.** D(P‖Q) = 1 × ln(1 / 0,5) + 0 = ln 2 ≈ 0,693 : la seconde issue ne compte pas, car P lui donne 0. D(Q‖P) contient 0,5 ln(0,5 / 0) : elle est infinie, car Q donne 0,5 à une issue que P dit impossible (démonstration 4).

**Exercice 3.** On pose f(u) = u − 1 − ln u pour u > 0. Sa dérivée vaut 1 − 1/u : négative pour u < 1, nulle en u = 1, positive pour u > 1. f décroît puis croît, son minimum est f(1) = 0, donc f(u) ≥ 0, c'est-à-dire ln u ≤ u − 1, avec égalité seulement en u = 1.

**Exercice 4.** Avec Q(x) = 1/n : Σ P ln(P / (1/n)) = Σ P ln P + Σ P ln n = −H(P) + ln n. Pour P = (0,5 ; 0,3 ; 0,15 ; 0,05) : ln 4 ≈ 1,38629 et H(P) ≈ 1,14212, donc D ≈ 0,24417. Comme D ≥ 0, on retrouve H(P) ≤ ln n (fiche 21).

**Exercice 5.** 0,8 − β × 0,08512 < 0,7 ⟺ β × 0,08512 > 0,1 ⟺ β > 0,1 / 0,08512 ≈ 1,1748.

**Exercice 6.** Avec β = 0,15 : A vaut 0,8 − 0,15 × 0,08512 ≈ 0,78723 et B vaut 0,86 − 0,15 × 0,37022 ≈ 0,80447. B l'emporte, ce qui est cohérent avec la bascule 0,21045 > 0,15. Il faut alors surveiller directement le taux de transfert vers un conseiller, qui tomberait à 3 % sous les 8 % de réclamations.

**Exercice 7.** Le rapport est inversé : Σ P ln(Q/P) est l'opposé de la divergence (étape 1 de la démonstration 1). La vraie valeur est D(P‖Q) = +0,08025, toujours ≥ 0 par Gibbs ; une « KL négative » signale toujours une erreur de calcul (rapport inversé ou distribution non normalisée).

**Exercice 8.** On restreint la somme au support S de P (hypothèse : Q > 0 sur S, sinon D = +∞). On écrit −D = Σ P ln(Q/P), on majore ln u par u − 1 (u > 0 grâce à Q > 0 sur S), on obtient (somme de Q sur S) − 1 ≤ 0 (hypothèse : Q est une distribution). Égalité : ln u = u − 1 force Q = P sur S, et une somme de Q sur S égale à 1 force Q = 0 hors de S.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`verifier_distribution(P)`** — Cette fonction est l'inspecteur qui vérifie qu'une balance est bien tarée avant toute pesée : elle reçoit une liste de probabilités, contrôle qu'aucune n'est négative et que leur somme vaut 1 à un milliardième près, et lève une `ValueError` dans le cas contraire. Elle ne renvoie rien quand tout est en ordre ; `kl` l'appelle sur ses deux arguments, si bien qu'une « distribution » comme (0,6 ; 0,6), qui somme à 1,2, est refusée avant le moindre logarithme, ce que `main` vérifie à la fin.

**`kl(P, Q)`** — Cette fonction est le géomètre qui mesure combien une carte Q trahit le territoire P : elle reçoit deux distributions, refuse par une `ValueError` des longueurs différentes, les fait contrôler par `verifier_distribution`, puis additionne P(x) ln(P(x)/Q(x)) sur les seules issues où P est positif, en renvoyant aussitôt l'infini si Q y vaut 0. Elle renvoie la divergence D(P‖Q), toujours positive ou nulle : 0,51083 pour P = (0,5 ; 0,5) et Q = (0,9 ; 0,1), mais 0,36806 dans l'autre sens, ce qui montre son asymétrie, et c'est le cœur de tous les cas.

**`termes(P, Q)`** — Celle-ci est le comptable qui détaille la facture ligne par ligne au lieu d'en donner le seul total : elle reçoit les deux distributions et renvoie la liste des contributions P(x) ln(P(x)/Q(x)) de chaque issue, avec 0 là où P est nul, en supposant Q positif ailleurs. Dans l'exemple de base, elle donne −0,29389 et 0,80472, dont la somme est 0,51083 ; le cas 1 s'en sert pour voir que ce sont les litiges qui pèsent le plus, 0,16479 sur un total de 0,09749.

**`entropie(P)`** — On la voit en mesureuse de surprise moyenne, qui dit à quel point une distribution est imprévisible : elle reçoit une distribution, additionne −P(x) ln P(x) sur les issues de probabilité positive, et renvoie cette entropie en nats. Elle vaut 1,14212 pour la répartition de référence du cas 1 et 0,96726 pour les requêtes mélangées de l'enseignant du cas 4, et `main` l'utilise pour vérifier que l'entropie croisée égale exactement l'entropie plus la divergence.

**`entropie_croisee(P, Q)`** — Cette fonction raconte le coût d'un codage fait avec la mauvaise carte : elle reçoit la vraie distribution P et le modèle Q, additionne −P(x) ln Q(x) sur les issues où P est positif, et renvoie l'entropie croisée, la quantité que minimise l'entraînement d'un classifieur. Elle vaut 1,22237 pour le cas 1 et 1,16665 pour le cas 4, soit dans chaque cas l'entropie de P augmentée de la divergence, comme le prouve la démonstration 5.

**`lisser(comptes, pseudo)`** — Celle-ci est le jardinier prudent qui ne laisse aucune case vide dans son potager de fréquences : elle reçoit une liste de comptes et un pseudo-compte, 1 par défaut, refuse par une `ValueError` un pseudo-compte nul ou négatif et des comptes négatifs, ajoute ce pseudo-compte à chaque issue, puis divise par le nouveau total. Elle renvoie une distribution sans aucun zéro, comme le lissage de Laplace du cas 3, où la tranche la plus chère, vide ce trimestre, reçoit 0,0049 au lieu de 0, ce qui rend la divergence finie.

**`normaliser(comptes)`** — Cette petite fonction est le caissier qui convertit des effectifs en parts : elle reçoit une liste de comptes, renvoie `None` si leur somme est nulle, puisqu'aucune part n'a alors de sens, et sinon divise chaque compte par le total. Elle transforme les 4 200, 3 600, 2 400 et 1 800 demandes de la semaine du cas 1 en 0,35, 0,30, 0,20 et 0,15, et les ventes du cas 3 en répartitions comparables à la référence.

**`approx_quadratique(P, Q)`** — On l'imagine en arpenteur qui, faute de temps, mesure une petite distance au mètre ruban plutôt qu'au théodolite : elle reçoit deux distributions proches et renvoie l'approximation ½ Σ (Q − P)²/P, valable quand Q est voisin de P. Pour un écart de cinq points, elle donne 0,008036 contre une divergence exacte de 0,0072, et pour un écart doublé 0,032143 contre 0,02681 : elle sert dans la démonstration 6 à montrer que la divergence croît comme le carré de l'écart, donc environ quatre fois quand l'écart double.

**`bisection(f, a, b, pas)`** — Cette fonction est le chercheur de trésor qui coupe chaque fois la zone de fouille en deux : elle reçoit une fonction f, un intervalle aux bornes de signes opposés et un nombre de pas, soixante par défaut, regarde le signe au milieu et garde la moitié où le signe change, puis renvoie le milieu final. Elle trouve dans le cas 1 la part de litiges, 0,12912, à laquelle la divergence atteint 0,05, et dans le cas 3 le pseudo-compte de bascule, 0,623.

**`proche(x, attendu, decimales)`** — Ce petit contrôleur compare deux nombres comme on rapproche deux lignes d'un registre arrondi : il reçoit la valeur calculée, la valeur attendue et un nombre de décimales, arrondit les deux à ce nombre de chiffres et renvoie vrai s'ils coïncident. Presque tous les `assert` de `main` passent par lui, de la divergence 0,51083 de l'exemple jusqu'au β de bascule 0,21045 du cas 2, pour confronter les résultats aux valeurs écrites dans la fiche.

**`demonstrations()`** — Cette fonction rejoue les démonstrations de la fiche sur de petites distributions : elle ne reçoit rien, montre que Σ P ln(Q/P) vaut −0,51083, donc reste négatif comme l'exige l'inégalité de Gibbs, mais que des scores bruts non normalisés de 0,8 et 0,8 fabriquent une fausse « divergence » de −0,47. Elle vérifie ensuite qu'une distribution est à distance nulle d'elle-même, qu'un voisin donne 0,000210 et qu'une masse hors du support donne ln 1,25 = 0,22314, puis l'asymétrie 0,51083 contre 0,36806, l'explosion du terme 0,9 ln(0,9/q) quand q tend vers 0, jusqu'à l'infini, et l'approximation quadratique ; elle imprime ces nombres et les renvoie dans un dictionnaire.

**`exemple_simple()`** — Celle-ci raconte la scène de base, une pièce équilibrée P décrite par un modèle Q qui croit à 90 % au premier côté : elle ne reçoit rien, calcule les deux logarithmes ln(P/Q), −0,58779 et 1,60944, puis les deux divergences, 0,51083 dans un sens et 0,36806 dans l'autre. Elle imprime ces quatre nombres et renvoie les logarithmes, que `main` compare aux valeurs de la fiche avant de vérifier les termes 0,52901 et −0,16094 de la divergence inverse.

**`cas_1_btp_derive()`** — Cette fonction met en scène l'agent d'un groupe de construction qui traite 12 000 demandes de fournisseurs par semaine, évalué sur une répartition de référence de 50 % de factures, 30 % de livraisons, 15 % de comptes et 5 % de litiges : elle ne reçoit rien, normalise les comptes de la semaine, puis trouve D(P‖Q) = 0,08025 et D(Q‖P) = 0,09749, au-dessus du seuil d'alerte de 0,05. Elle détaille les termes, où les litiges dominent, chiffre la hausse des échecs de 1 380 à 1 740 par semaine, soit 32 400 AED à 90 AED l'escalade, cherche par `bisection` la part de litiges de bascule, 0,12912, et renvoie ces résultats.

**`cas_2_banque_renforcement()`** — On y suit une banque qui affine son assistant par renforcement en pénalisant l'écart à une politique de référence validée par la conformité, qui répond, propose une offre ou transfère à un conseiller avec les probabilités 0,5, 0,3 et 0,2 : la fonction ne reçoit rien, calcule la divergence de la candidate A, de récompense 0,8, soit 0,08512, et de la candidate B, de récompense 0,86, soit 0,37022. Avec β = 0,1, B l'emporte, 0,82298 contre 0,79149 ; avec β = 0,25, A reprend la tête, 0,77872 contre 0,76744 ; elle calcule le β de bascule, 0,21045, note que B ferait tomber les transferts de 4 000 à 600 par mois, et renvoie ces nombres.

**`cas_3_immo_lissage()`** — Cette fonction raconte un modèle d'estimation des prix immobiliers à recalibrer si la répartition des ventes par tranche s'éloigne de plus de 0,05 de la référence, alors qu'aucune vente n'est tombée ce trimestre dans la tranche la plus chère : elle ne reçoit rien et constate que la divergence brute D(P‖Q) est infinie, tandis que D(Q‖P) vaut 0,04929. Avec le lissage de Laplace, elle obtient 0,04219, sous le seuil, mais 0,05383 avec un pseudo-compte de 0,5, montre qu'un ε arbitraire de 10⁻⁹ ou de 10⁻⁶ donne 0,34562 ou 0,20747, calcule la probabilité de 0,0176 de n'observer aucune vente dans cette tranche sur 200, puis le pseudo-compte de bascule 0,623, et renvoie le tout.

**`cas_4_public_distillation()`** — Ici, un service public en ligne veut remplacer son routeur « enseignant », à 0,012 AED par requête, par un « élève » distillé à 0,002 AED, sur 30 000 requêtes par jour en arabe, en anglais ou mélangées : la fonction ne reçoit rien et mesure la divergence entre les deux modèles pour chaque segment, 0,00746, 0,00575 et 0,19939, dont la moyenne pondérée, 0,04525, cache le problème des requêtes mélangées. Elle chiffre l'économie de 240 AED par jour en ne basculant que l'arabe et l'anglais, les 1 800 erreurs de plus par jour si tout passait à l'élève, la divergence de 0,04784 si l'écart était divisé par deux, et vérifie que l'entropie 0,96726 plus la divergence donne l'entropie croisée 1,16665, puis renvoie ces résultats.

**`corrige()`** — Celle-ci est le correcteur qui refait au propre les exercices chiffrés : elle ne reçoit rien et calcule la divergence nulle d'une distribution à elle-même, les valeurs ln 2 ≈ 0,693 et l'infini de l'exercice 2, la divergence 0,24417 à la loi uniforme, égale à ln 4 moins l'entropie, le β minimal de 1,1748 de l'exercice 5 et les objectifs 0,78723 et 0,80447 des candidates A et B pour β = 0,15. Elle imprime ces résultats et renvoie le β, le couple d'objectifs et la divergence à la loi uniforme.

**`main()`** — C'est le chef d'orchestre de la fiche : il appelle `demonstrations` et vérifie chacun de ses nombres, puis contrôle sur trois paires de distributions que la divergence reste positive et que l'entropie croisée égale l'entropie plus la divergence. Il enchaîne avec l'exemple simple, les quatre cas et le corrigé, puis s'assure que des longueurs différentes, une distribution qui ne somme pas à 1 ou un pseudo-compte nul lèvent une `ValueError` et que des comptes tous nuls donnent `None` ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tout concorde.

```python
"""Démonstration 17 — divergence KL : Gibbs, égalité, asymétrie, infini, entropie croisée, approximation, quatre cas."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def verifier_distribution(P):
    if any(p < 0 for p in P) or abs(sum(P) - 1) > 1e-9:
        raise ValueError("une distribution a des valeurs >= 0 qui somment à 1")


def kl(P, Q):
    """D(P || Q) = Σ P ln(P / Q) ; 0 · ln(0 / q) = 0 ; P > 0 et Q = 0 donnent +∞."""
    if len(P) != len(Q):
        raise ValueError("P et Q doivent avoir la même longueur")
    verifier_distribution(P)
    verifier_distribution(Q)
    total = 0.0
    for p, q in zip(P, Q):
        if p > 0:
            if q == 0:
                return math.inf
            total += p * math.log(p / q)
    return total


def termes(P, Q):
    """Contribution P(x) ln(P(x) / Q(x)) de chaque issue (Q > 0 supposé là où P > 0)."""
    return [p * math.log(p / q) if p > 0 else 0.0 for p, q in zip(P, Q)]


def entropie(P):
    return -sum(p * math.log(p) for p in P if p > 0)


def entropie_croisee(P, Q):
    return -sum(p * math.log(q) for p, q in zip(P, Q) if p > 0)


def lisser(comptes, pseudo=1.0):
    """Lissage de Laplace explicite : on ajoute pseudo à chaque issue, puis on normalise."""
    if pseudo <= 0 or any(c < 0 for c in comptes):
        raise ValueError("pseudo-compte > 0 et comptes >= 0")
    total = sum(comptes) + pseudo * len(comptes)
    return [(c + pseudo) / total for c in comptes]


def normaliser(comptes):
    total = sum(comptes)
    if total == 0:
        return None
    return [c / total for c in comptes]


def approx_quadratique(P, Q):
    """D(P || Q) ≈ ½ Σ (Q − P)² / P quand Q est proche de P."""
    return 0.5 * sum((q - p) ** 2 / p for p, q in zip(P, Q) if p > 0)


def bisection(f, a, b, pas=60):
    """Racine de f sur [a, b], f(a) et f(b) de signes opposés."""
    for _ in range(pas):
        m = (a + b) / 2
        if (f(a) < 0) == (f(m) < 0):
            a = m
        else:
            b = m
    return (a + b) / 2


def proche(x, attendu, decimales):
    return round(x, decimales) == round(attendu, decimales)


def demonstrations():
    print("Démonstrations")
    P, Q = (0.5, 0.5), (0.9, 0.1)
    gauche = sum(p * math.log(q / p) for p, q in zip(P, Q))
    brut = sum(p * math.log(p / q) for p, q in zip(P, (0.8, 0.8)))       # Q non normalisé
    print(f"  D1 Σ P ln(Q/P) = {gauche:.5f} <= Σ Q - Σ P = 0 ; scores bruts (0.8 ; 0.8) : {brut:.5f}")
    voisin = kl((0.6, 0.4), (0.61, 0.39))
    hors = kl((0.5, 0.5, 0.0), (0.4, 0.4, 0.2))
    print(f"  D2 D(P||P) = {kl((0.6, 0.4), (0.6, 0.4)):.1f} ; Q voisin {voisin:.6f} ; masse hors support {hors:.5f}")
    a, b = kl(P, Q), kl(Q, P)
    print(f"  D3 D(P||Q) = {a:.5f} ; D(Q||P) = {b:.5f} ; somme symétrique {a + b:.5f}")
    t6, t9 = 0.9 * math.log(0.9 / 1e-6), 0.9 * math.log(0.9 / 1e-9)
    print(f"  D4 0.9 ln(0.9/q) : q = 1e-6 -> {t6:.2f} ; q = 1e-9 -> {t9:.2f} ; Q = 0 -> {kl((0.9, 0.1), (0.0, 1.0))}")
    ref, proche_q, double_q = (0.70, 0.20, 0.10), (0.65, 0.25, 0.10), (0.60, 0.30, 0.10)
    print(f"  D6 exact {kl(ref, proche_q):.4f} / approché {approx_quadratique(ref, proche_q):.6f} ;"
          f" écart doublé {kl(ref, double_q):.5f} / {approx_quadratique(ref, double_q):.6f}")
    return {"gauche": gauche, "brut": brut, "voisin": voisin, "hors": hors, "a": a, "b": b, "t6": t6, "t9": t9,
            "e1": kl(ref, proche_q), "a1": approx_quadratique(ref, proche_q), "e2": kl(ref, double_q),
            "a2": approx_quadratique(ref, double_q), "tP": termes(P, Q), "tQ": termes(Q, P)}


def exemple_simple():
    P, Q = (0.5, 0.5), (0.9, 0.1)
    logs = [math.log(p / q) for p, q in zip(P, Q)]
    print(f"Exemple simple : ln(P/Q) = {logs[0]:.5f} et {logs[1]:.5f} ; D(P||Q) = {kl(P, Q):.5f} ; D(Q||P) = {kl(Q, P):.5f}")
    return logs


def cas_1_btp_derive():
    P = (0.5, 0.3, 0.15, 0.05)                            # factures, livraisons, comptes, litiges
    Q = normaliser([4200, 3600, 2400, 1800])
    d_pq, d_qp = kl(P, Q), kl(Q, P)
    t_pq, t_qp = termes(P, Q), termes(Q, P)
    echecs_p = 12_000 * (P[3] * 0.4 + (1 - P[3]) * 0.1)
    echecs_q = 12_000 * (Q[3] * 0.4 + (1 - Q[3]) * 0.1)
    surcout = (echecs_q - echecs_p) * 90
    x_bascule = bisection(lambda x: kl((0.55 - x, 0.3, 0.15, x), P) - 0.05, 0.05, 0.5)
    ce = entropie_croisee(P, Q)
    print(f"Cas 1 : D(P||Q) = {d_pq:.5f} ; D(Q||P) = {d_qp:.5f} ; alerte {d_qp > 0.05} ;"
          f" termes D(Q||P) {[round(t, 5) for t in t_qp]}")
    print(f"  termes D(P||Q) {[round(t, 5) for t in t_pq]} ; échecs {echecs_p:.0f} -> {echecs_q:.0f} ;"
          f" surcoût {surcout:.0f} AED/semaine ; bascule litiges {x_bascule:.4f}")
    return {"P": P, "Q": Q, "d_pq": d_pq, "d_qp": d_qp, "t_pq": t_pq, "t_qp": t_qp, "echecs_p": echecs_p,
            "echecs_q": echecs_q, "surcout": surcout, "x": x_bascule, "ce": ce}


def cas_2_banque_renforcement():
    pi, ref = (0.7, 0.2, 0.1), (0.5, 0.3, 0.2)            # répondre, proposer une offre, transférer
    agressive = (0.9, 0.07, 0.03)
    kl_a, kl_b = kl(pi, ref), kl(agressive, ref)
    objectif = {beta: (0.8 - beta * kl_a, 0.86 - beta * kl_b) for beta in (0.1, 0.25)}
    beta_bascule = (0.86 - 0.8) / (kl_b - kl_a)
    print(f"Cas 2 : KL(A||ref) = {kl_a:.5f} ; KL(B||ref) = {kl_b:.5f} ; objectif β = 0.1 :"
          f" A {0.8 - 0.1 * kl(pi, ref):.5f}, B {objectif[0.1][1]:.5f}")
    print(f"  β = 0.25 : A {objectif[0.25][0]:.5f}, B {objectif[0.25][1]:.5f} ; β de bascule {beta_bascule:.5f} ;"
          f" transferts {20_000 * ref[2]:.0f} -> {20_000 * agressive[2]:.0f} par mois")
    return {"kl_a": kl_a, "kl_b": kl_b, "objectif": objectif, "beta": beta_bascule,
            "termes_b": termes(agressive, ref)}


def cas_3_immo_lissage():
    ref, cur = [150, 350, 300, 180, 20], [20, 60, 70, 50, 0]
    P, Q = normaliser(ref), normaliser(cur)
    brut_pq, brut_qp = kl(P, Q), kl(Q, P)
    Pl, Ql = lisser(ref), lisser(cur)
    lisse_pq, lisse_qp = kl(Pl, Ql), kl(Ql, Pl)
    demi = kl(lisser(ref, 0.5), lisser(cur, 0.5))
    epsilons = {eps: kl(P, normaliser([max(q, eps) for q in Q])) for eps in (1e-9, 1e-6)}
    p_zero = (1 - P[4]) ** 200
    pseudo_bascule = bisection(lambda a: kl(lisser(ref, a), lisser(cur, a)) - 0.05, 0.5, 1.0)
    print(f"Cas 3 : brut D(P||Q) = {brut_pq} ; D(Q||P) = {brut_qp:.5f} ; Laplace +1 : D(P||Q) = {lisse_pq:.5f},"
          f" D(Q||P) = {lisse_qp:.5f} ; +0.5 : {demi:.5f}")
    print(f"  epsilon 1e-9 -> {epsilons[1e-9]:.5f} ; 1e-6 -> {epsilons[1e-6]:.5f} ;"
          f" P(0 vente > 3 000 AED/sqft sur 200) = {p_zero:.4f} ; pseudo-compte de bascule {pseudo_bascule:.3f}")
    return {"P": P, "Q": Q, "brut_pq": brut_pq, "brut_qp": brut_qp, "Pl": Pl, "Ql": Ql, "lisse_pq": lisse_pq,
            "lisse_qp": lisse_qp, "demi": demi, "eps": epsilons, "p_zero": p_zero, "pseudo": pseudo_bascule}


def cas_4_public_distillation():
    T = {"arabe": (0.80, 0.10, 0.05, 0.05), "anglais": (0.10, 0.70, 0.15, 0.05), "mélangé": (0.60, 0.30, 0.05, 0.05)}
    S = {"arabe": (0.75, 0.12, 0.07, 0.06), "anglais": (0.12, 0.65, 0.17, 0.06), "mélangé": (0.30, 0.55, 0.10, 0.05)}
    parts = {"arabe": 0.45, "anglais": 0.35, "mélangé": 0.20}
    d = {k: kl(T[k], S[k]) for k in T}
    moyenne = sum(parts[k] * d[k] for k in d)
    economie = (parts["arabe"] + parts["anglais"]) * 30_000 * (0.012 - 0.002)
    erreurs_en_plus = parts["mélangé"] * 30_000 * (T["mélangé"][0] - T["mélangé"][1])
    demi = tuple((t + s) / 2 for t, s in zip(T["mélangé"], S["mélangé"]))
    d_demi = kl(T["mélangé"], demi)
    h_t, ce = entropie(T["mélangé"]), entropie_croisee(T["mélangé"], S["mélangé"])
    print(f"Cas 4 : KL arabe {d['arabe']:.5f}, anglais {d['anglais']:.5f}, mélangé {d['mélangé']:.5f} ;"
          f" moyenne pondérée {moyenne:.5f}")
    print(f"  économie {economie:.0f} AED/jour ; erreurs en plus si tout passe à l'élève {erreurs_en_plus:.0f}/jour ;"
          f" écart divisé par 2 -> KL {d_demi:.5f} ; H(T) {h_t:.5f} + KL = CE {ce:.5f}")
    return {"d": d, "moyenne": moyenne, "economie": economie, "erreurs": erreurs_en_plus, "demi": demi,
            "d_demi": d_demi, "h_t": h_t, "ce": ce, "approx": approx_quadratique(T["mélangé"], S["mélangé"])}


def corrige():
    P = (0.5, 0.3, 0.15, 0.05)
    u = (0.25,) * 4
    pi, ref = (0.7, 0.2, 0.1), (0.5, 0.3, 0.2)
    beta = (0.8 - 0.7) / kl(pi, ref)
    e6 = (0.8 - 0.15 * kl(pi, ref), 0.86 - 0.15 * kl((0.9, 0.07, 0.03), ref))
    print(f"Corrigé : ex1 {kl((0.6, 0.4), (0.6, 0.4))} ; ex2 {kl((1, 0), (0.5, 0.5)):.3f} et {kl((0.5, 0.5), (1, 0))} ;"
          f" ex4 {kl(P, u):.5f} = {math.log(4) - entropie(P):.5f} ; ex5 β > {beta:.4f} ;"
          f" ex6 A {e6[0]:.5f} / B {e6[1]:.5f}")
    return beta, e6, kl(P, u)


def main() -> None:
    d = demonstrations()
    assert proche(d["gauche"], -0.51083, 5) and d["gauche"] <= 0 and proche(d["brut"], -0.47000, 5)
    assert [round(math.log(q / p), 5) for p, q in ((0.5, 0.9), (0.5, 0.1))] == [0.58779, -1.60944]
    assert d["voisin"] > 0 and proche(d["voisin"], 0.000210, 6) and proche(d["hors"], math.log(1.25), 12)
    assert proche(d["hors"], 0.22314, 5) and kl((0.6, 0.4), (0.6, 0.4)) == 0
    assert proche(d["a"], 0.51083, 5) and proche(d["b"], 0.36806, 5) and proche(d["a"] + d["b"], 0.87889, 5)
    assert [round(t, 5) for t in d["tP"]] == [-0.29389, 0.80472] and [round(t, 5) for t in d["tQ"]] == [0.52901, -0.16094]
    assert proche(d["t6"], 12.34, 2) and proche(d["t9"], 18.56, 2) and kl((0.9, 0.1), (0.0, 1.0)) == math.inf
    assert kl((1, 0), (0.5, 0.5)) == math.log(2) and kl((0.5, 0.5), (1, 0)) == math.inf   # démonstration 4
    assert proche(d["e1"], 0.0072, 4) and proche(d["a1"], 0.008036, 6) and proche(d["e2"], 0.02681, 5)
    assert proche(d["a2"], 0.032143, 6) and proche(d["e2"] / d["e1"], 3.70, 2)
    assert proche(0.0025 / 0.70, 0.003571, 6) and proche(0.0025 / 0.20, 0.0125, 9) and proche(0.01 / 0.7, 0.014286, 6)
    for X, Y in (((0.5, 0.3, 0.15, 0.05), (0.35, 0.3, 0.2, 0.15)), ((0.7, 0.2, 0.1), (0.5, 0.3, 0.2)),
                 ((0.2, 0.8), (0.6, 0.4))):
        assert kl(X, Y) >= 0 and math.isclose(entropie_croisee(X, Y), entropie(X) + kl(X, Y))  # D1 et D5

    logs = exemple_simple()
    assert [round(x, 5) for x in logs] == [-0.58779, 1.60944]
    assert proche(0.5 / 0.9, 0.5556, 4) and proche(0.9 * math.log(1.8), 0.52901, 5) and proche(0.1 * math.log(0.2), -0.16094, 5)

    c1 = cas_1_btp_derive()
    assert [round(x, 2) for x in c1["Q"]] == [0.35, 0.30, 0.20, 0.15]
    assert proche(c1["d_pq"], 0.08025, 5) and proche(c1["d_qp"], 0.09749, 5) and c1["d_qp"] > 0.05
    assert [round(t, 5) for t in c1["t_qp"]] == [-0.12484, 0.0, 0.05754, 0.16479]
    assert [round(t, 5) for t in c1["t_pq"]] == [0.17834, 0.0, -0.04315, -0.05493]
    assert [round(math.log(x), 5) for x in (0.7, 4 / 3, 3)] == [-0.35667, 0.28768, 1.09861]
    assert proche(c1["echecs_p"], 1380, 6) and proche(c1["echecs_q"], 1740, 6) and proche(c1["surcout"], 32400, 6)
    assert proche(0.05 * 0.4 + 0.95 * 0.1, 0.115, 9) and proche(0.15 * 0.4 + 0.85 * 0.1, 0.145, 9)
    assert proche(c1["x"], 0.12912, 5) and proche(kl((0.55 - c1["x"], 0.3, 0.15, c1["x"]), c1["P"]), 0.05, 9)
    assert proche(c1["ce"], entropie(c1["P"]) + c1["d_pq"], 12) and proche(entropie(c1["P"]), 1.14212, 5)
    assert proche(c1["ce"], 1.22237, 5)

    c2 = cas_2_banque_renforcement()
    assert proche(c2["kl_a"], 0.08512, 5) and proche(c2["kl_b"], 0.37022, 5)
    assert proche(c2["objectif"][0.1][0], 0.79149, 5) and proche(c2["objectif"][0.1][1], 0.82298, 5)
    assert proche(c2["objectif"][0.25][0], 0.77872, 5) and proche(c2["objectif"][0.25][1], 0.76744, 5)
    assert c2["objectif"][0.1][1] > c2["objectif"][0.1][0] and c2["objectif"][0.25][0] > c2["objectif"][0.25][1]
    assert proche(c2["beta"], 0.21045, 5) and proche(c2["kl_b"] - c2["kl_a"], 0.28510, 5)
    assert [round(t, 5) for t in c2["termes_b"]] == [0.52901, -0.10187, -0.05691]
    assert proche(0.1 * c2["kl_a"], 0.00851, 5) and proche(0.1 * c2["kl_b"], 0.03702, 5)
    assert proche(0.25 * c2["kl_a"], 0.02128, 5) and proche(0.25 * c2["kl_b"], 0.09256, 5)

    c3 = cas_3_immo_lissage()
    assert [round(x, 3) for x in c3["P"]] == [0.15, 0.35, 0.30, 0.18, 0.02] and [round(x, 2) for x in c3["Q"]] == [0.1, 0.3, 0.35, 0.25, 0.0]
    assert c3["brut_pq"] == math.inf and proche(c3["brut_qp"], 0.04929, 5)
    assert [round(x, 4) for x in c3["Pl"]] == [0.1502, 0.3493, 0.2995, 0.1801, 0.0209]
    assert [round(x, 4) for x in c3["Ql"]] == [0.1024, 0.2976, 0.3463, 0.2488, 0.0049]
    assert proche(c3["lisse_pq"], 0.04219, 5) and proche(c3["lisse_qp"], 0.03670, 5) and c3["lisse_pq"] < 0.05
    assert proche(c3["demi"], 0.05383, 5) and c3["demi"] > 0.05
    assert proche(c3["eps"][1e-9], 0.34562, 5) and proche(c3["eps"][1e-6], 0.20747, 5)
    assert proche(c3["p_zero"], 0.0176, 4) and proche(200 * 0.02, 4, 9) and 1000 + 5 == 1005 and 200 + 5 == 205
    assert proche(c3["pseudo"], 0.623, 3) and proche(kl(lisser([150, 350, 300, 180, 20], c3["pseudo"]),
                                                       lisser([20, 60, 70, 50, 0], c3["pseudo"])), 0.05, 9)
    assert proche(c3["eps"][1e-9] / 0.05, 6.9, 1)

    c4 = cas_4_public_distillation()
    assert proche(c4["d"]["arabe"], 0.00746, 5) and proche(c4["d"]["anglais"], 0.00575, 5)
    assert proche(c4["d"]["mélangé"], 0.19939, 5) and proche(c4["moyenne"], 0.04525, 5) and c4["moyenne"] < 0.1
    assert c4["d"]["arabe"] < 0.1 and c4["d"]["anglais"] < 0.1 < c4["d"]["mélangé"]
    assert proche(c4["economie"], 240, 6) and proche(c4["erreurs"], 1800, 6) and proche(1800 * 15, 27000, 9)
    assert proche(0.2 * 30_000 * 0.01, 60, 9) and proche(0.2 * 30_000, 6000, 9) and proche(0.8 * 30_000, 24000, 9)
    assert [round(x, 3) for x in c4["demi"]] == [0.45, 0.425, 0.075, 0.05] and proche(c4["d_demi"], 0.04784, 5)
    assert proche(c4["d"]["mélangé"] / 4, 0.04985, 5) and proche(c4["d"]["mélangé"] / c4["d_demi"], 4.17, 2)
    assert proche(c4["approx"], 0.20417, 5) and proche(c4["h_t"], 0.96726, 5) and proche(c4["ce"], 1.16665, 5)
    assert math.isclose(c4["ce"], c4["h_t"] + c4["d"]["mélangé"])
    assert [round(t, 5) for t in termes((0.60, 0.30, 0.05, 0.05), (0.30, 0.55, 0.10, 0.05))] == [0.41589, -0.18184,
                                                                                                -0.03466, 0.0]
    assert [round(x, 5) for x in (0.45 * c4["d"]["arabe"], 0.35 * c4["d"]["anglais"], 0.2 * c4["d"]["mélangé"])] == [
        0.00336, 0.00201, 0.03988]
    assert proche(math.log(0.3 / 0.55), -0.60614, 5) and proche(0.60 - 0.30, 0.30, 9)
    assert proche(0.1 * 20_000, 2000, 9) and proche(0.08 * 20_000, 1600, 9) and 1600 - 600 == 1000
    assert proche(0.1 / (c2["kl_b"] - c2["kl_a"]), 0.35075, 5) and 0.35075 > 0.25
    assert proche(0.9 * math.log(1000), 6.2, 1) and proche(0.5 * 0.01 ** 2, 0.00005, 12) and proche(0.25 - c2["beta"], 0.04, 2)

    beta, e6, e4 = corrige()
    assert round(beta, 4) == 1.1748 and proche(e4, 0.24417, 5) and math.isclose(e4, math.log(4) - entropie((0.5, 0.3, 0.15, 0.05)))
    assert proche(e6[0], 0.78723, 5) and proche(e6[1], 0.80447, 5) and e6[1] > e6[0] and 0.15 < c2["beta"]
    assert proche(math.log(4), 1.38629, 5) and proche(0.8 - 1.1748 * 0.08512, 0.7, 4)
    for mauvais in (lambda: kl((0.5, 0.5), (0.3, 0.3, 0.4)), lambda: kl((0.6, 0.6), (0.5, 0.5)),
                    lambda: lisser([1, 2], 0)):
        try:
            mauvais()
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError attendue")
    assert normaliser([0, 0]) is None
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Démonstrations
  D1 Σ P ln(Q/P) = -0.51083 <= Σ Q - Σ P = 0 ; scores bruts (0.8 ; 0.8) : -0.47000
  D2 D(P||P) = 0.0 ; Q voisin 0.000210 ; masse hors support 0.22314
  D3 D(P||Q) = 0.51083 ; D(Q||P) = 0.36806 ; somme symétrique 0.87889
  D4 0.9 ln(0.9/q) : q = 1e-6 -> 12.34 ; q = 1e-9 -> 18.56 ; Q = 0 -> inf
  D6 exact 0.0072 / approché 0.008036 ; écart doublé 0.02681 / 0.032143
Exemple simple : ln(P/Q) = -0.58779 et 1.60944 ; D(P||Q) = 0.51083 ; D(Q||P) = 0.36806
Cas 1 : D(P||Q) = 0.08025 ; D(Q||P) = 0.09749 ; alerte True ; termes D(Q||P) [-0.12484, 0.0, 0.05754, 0.16479]
  termes D(P||Q) [0.17834, 0.0, -0.04315, -0.05493] ; échecs 1380 -> 1740 ; surcoût 32400 AED/semaine ; bascule litiges 0.1291
Cas 2 : KL(A||ref) = 0.08512 ; KL(B||ref) = 0.37022 ; objectif β = 0.1 : A 0.79149, B 0.82298
  β = 0.25 : A 0.77872, B 0.76744 ; β de bascule 0.21045 ; transferts 4000 -> 600 par mois
Cas 3 : brut D(P||Q) = inf ; D(Q||P) = 0.04929 ; Laplace +1 : D(P||Q) = 0.04219, D(Q||P) = 0.03670 ; +0.5 : 0.05383
  epsilon 1e-9 -> 0.34562 ; 1e-6 -> 0.20747 ; P(0 vente > 3 000 AED/sqft sur 200) = 0.0176 ; pseudo-compte de bascule 0.623
Cas 4 : KL arabe 0.00746, anglais 0.00575, mélangé 0.19939 ; moyenne pondérée 0.04525
  économie 240 AED/jour ; erreurs en plus si tout passe à l'élève 1800/jour ; écart divisé par 2 -> KL 0.04784 ; H(T) 0.96726 + KL = CE 1.16665
Corrigé : ex1 0.0 ; ex2 0.693 et inf ; ex4 0.24417 = 0.24417 ; ex5 β > 1.1748 ; ex6 A 0.78723 / B 0.80447
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme calcule la divergence KL entre deux distributions, en traitant le cas où Q donne 0 à une issue possible pour P, et lisse d'abord les comptes quand les distributions viennent de fréquences observées.

```text
ALGORITHME DivergenceKL
ENTRÉES : distributions P = (p₁ … pₙ), Q = (q₁ … qₙ), ou comptes et pseudo-compte a > 0
SORTIE  : D(P ‖ Q) ≥ 0, éventuellement infinie

  SI on reçoit des comptes ALORS
      pᵢ ← (cᵢ + a) / (Σ c + n × a) ; de même pour q     (lissage de Laplace)
  VÉRIFIER que P et Q ont la même longueur, des valeurs ≥ 0 et une somme 1
  total ← 0
  POUR i DE 1 À n FAIRE
      SI pᵢ > 0 ALORS
          SI qᵢ = 0 ALORS RETOURNER +∞
          total ← total + pᵢ × ln(pᵢ / qᵢ)
      FIN SI
  FIN POUR
  RETOURNER total
```

**Complexité.** O(n) en temps, O(1) en mémoire (O(n) si l'on garde les contributions de chaque issue pour le rapport). Pour surveiller une dérive, on recalcule D chaque semaine sur n catégories : un coût négligeable.

**Du squelette au code.** L'algorithme est la fonction `kl(P, Q)`, avec le retour `math.inf`, et la vérification des distributions est `verifier_distribution(P)`. Le lissage est `lisser(comptes, pseudo)`, les contributions par issue sont `termes(P, Q)`. L'entropie `entropie(P)` sert à vérifier H(P, Q) = H(P) + D(P ‖ Q) avec `entropie_croisee(P, Q)` ; l'approximation quadratique est `approx_quadratique(P, Q)`. L'objectif de renforcement est `0.8 - 0.1 * kl(pi, ref)`. Les quatre cas sont `cas_1_btp_derive()`, `cas_2_banque_renforcement()`, `cas_3_immo_lissage()` et `cas_4_public_distillation()`.
