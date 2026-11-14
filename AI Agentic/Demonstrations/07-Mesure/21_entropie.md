# 21 — Entropie : démonstrations

> Fiche : [21 — Entropie](<../../Images/07-Mesure/21_entropie.md>) · Image : `21_entropie.jpg` · Leçon : [Étape 52 — Perplexité](<../../10-Evaluation/52-Perplexite-LLM.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
H(P) = -\sum_{i} p_i \times \ln(p_i)
$$

L'entropie mesure l'incertitude d'une distribution : 0 quand une issue est certaine, maximale quand toutes les issues se valent. Elle se lit en nats avec ln, en bits avec log₂. Par convention, 0 × ln 0 = 0.

## Les symboles, un par un

$$
P = (p_1, \dots, p_n)
$$

**P** : une distribution discrète sur n issues (outils d'un routeur, types de document, fournisseurs, orthographes candidates), des nombres ≥ 0 qui somment à 1 ; en Python, l'argument `P` de `H(P, base)`, qui lève `ValueError` sinon.

$$
p_i
$$

**pᵢ** : la probabilité de l'issue i, dans [0 ; 1] ; une issue de probabilité nulle ne compte pas (convention 0 × ln 0 = 0).

$$
-\ln p_i
$$

**−ln pᵢ** : la « surprise » de l'issue i, en nats, ≥ 0 : 0 pour une issue certaine, 0,693 pour une chance sur deux, 2,303 pour une chance sur dix.

$$
\ln,\ \log_2
$$

**ln** : le logarithme naturel, unité le nat ; **log₂** : le logarithme en base 2, unité le bit ; en Python, `math.log(p, base)` avec `base` égal à `math.e` ou à `2`.

$$
H(P)
$$

**H(P)** : la moyenne des surprises, pondérée par les probabilités, entre 0 et ln n ; en Python, `H(P)` en nats et `H(P, 2)` en bits.

$$
\frac{H(P)}{\ln n},\ e^{H(P)}
$$

**H(P) / ln n** : l'entropie normalisée, entre 0 et 1, en Python `ratio_max(P)` ; **exp(H)** : le nombre effectif d'issues, entre 1 et n, celui d'une loi uniforme qui aurait la même incertitude, en Python `nombre_effectif(P)`.

## Le mécanisme, avant les preuves

Une liste de probabilités entre. Le logarithme transforme chaque probabilité en surprise −ln pᵢ : une issue sûre ne surprend pas, une issue rare surprend beaucoup, et la surprise grandit sans limite quand pᵢ tend vers 0. On prend le logarithme plutôt que 1/pᵢ parce que la surprise de deux événements indépendants doit s'additionner : ln(pq) = ln p + ln q, et c'est ce qui rend l'entropie additive (démonstration 3). Le signe moins sert seulement à rendre positif ce logarithme d'un nombre ≤ 1. Chaque surprise est ensuite pondérée par sa probabilité : l'entropie est la surprise moyenne, celle qu'on attend avant de voir l'issue. Une issue très rare a une grande surprise mais un petit poids, et p ln p tend vers 0 quand p tend vers 0 : d'où la convention 0 × ln 0 = 0. Le total est nul pour une certitude et maximal, ln n, pour la loi uniforme (démonstrations 1 et 2). L'exponentielle exp(H) retraduit ce total en nombre effectif d'options, ce qui relie l'entropie à la perplexité de la leçon 52. En bits, H compte le nombre moyen de questions oui/non qu'il faut poser pour connaître l'issue, quand on les pose au mieux (cas 2).

Petit film chiffré avec P = (0,9 ; 0,1). Surprises : −ln 0,9 ≈ 0,10536 et −ln 0,1 ≈ 2,30259. Pondération : 0,9 × 0,10536 ≈ 0,09482 et 0,1 × 2,30259 ≈ 0,23026. Somme : H ≈ 0,32508 nat. Nombre effectif : exp(0,32508) ≈ 1,38415 issue : la distribution est presque aussi peu incertaine qu'un choix unique. L'issue rare apporte plus des deux tiers de l'entropie, parce que sa surprise est 22 fois plus grande.

## Démonstration 1 — L'entropie est positive, et nulle seulement pour une certitude

**Ce qu'on démontre.** Pour toute distribution P :

$$
H(P) \ge 0, \qquad H(P) = 0 \iff \text{une issue a la probabilité } 1
$$

**L'idée.** Chaque terme −pᵢ ln pᵢ est positif ou nul, parce qu'une probabilité est au plus 1 et que le logarithme d'un nombre ≤ 1 est ≤ 0. Une somme de termes positifs n'est nulle que si chaque terme l'est.

**La preuve, pas à pas.**

**Étape 1.** Pour 0 < p ≤ 1, ln p ≤ 0 parce que ln est croissant et ln 1 = 0 ; donc −p ln p ≥ 0. Pour p = 0, le terme vaut 0 par convention, justifiée par la limite :

$$
\lim_{p \to 0^+} p \ln p = 0
$$

**Étape 2.** H(P) est une somme de termes ≥ 0, donc H(P) ≥ 0.

**Étape 3.** H(P) = 0 exige que chaque terme soit nul. Pour 0 < p < 1, ln p < 0 strictement, donc −p ln p > 0 ; un terme n'est nul que si p = 0 ou p = 1. Comme les pᵢ somment à 1, une seule issue vaut 1 et les autres 0. ∎

**Vérification chiffrée.** Pour (0,9 ; 0,1), les deux termes valent 0,09482 et 0,23026, tous deux positifs ; pour (1 ; 0), H = 0. Contre-exemple quand l'hypothèse « pᵢ ≤ 1 » manque : un « score » de 2 donnerait le terme −2 ln 2 ≈ −1,386 < 0. Le programme refuse donc toute liste qui n'est pas une distribution.

**Ce que la preuve révèle du mécanisme.** L'entropie ne peut pas « compenser » : aucune issue n'enlève d'incertitude, chacune en ajoute ou n'en ajoute pas. Les termes nuls sont exactement les issues certaines ou impossibles.

**Conséquence pour un agent.** Une entropie nulle ou presque est le signal « un seul choix possible » ; un garde-fou peut alors laisser l'agent agir sans clarification, à condition que ce choix soit aussi juste, ce que l'entropie ne dit pas (cas 4, et fiche 20 pour la calibration).

## Démonstration 2 — Le maximum est atteint par la loi uniforme

**Ce qu'on démontre.** Pour toute distribution P sur n issues, avec égalité seulement pour la loi uniforme U :

$$
H(P) \le \ln n
$$

**L'idée.** On compare P à la loi uniforme avec la divergence KL (fiche 17), toujours positive ou nulle. Le calcul montre que cette divergence vaut exactement ln n − H(P).

**La preuve, pas à pas.**

**Étape 1.** On écrit la divergence de P par rapport à U, qui vaut 1/n partout :

$$
D_{KL}(P \parallel U) = \sum_i p_i \ln \frac{p_i}{1/n} = \sum_i p_i \ln p_i + \sum_i p_i \ln n
$$

**Étape 2.** Le premier terme vaut −H(P) ; le second vaut ln n parce que la somme des pᵢ vaut 1 :

$$
D_{KL}(P \parallel U) = \ln n - H(P)
$$

**Étape 3.** Par l'inégalité de Gibbs (fiche 17, démonstration 1), D ≥ 0, donc H(P) ≤ ln n ; et D = 0 seulement si P = U (fiche 17, démonstration 2). ∎

**Vérification chiffrée.** Pour la demande « claire » du cas 1, P = (0,7 ; 0,1 ; 0,1 ; 0,1) : ln 4 − H(P) ≈ 1,38629 − 0,94045 = 0,44585, et le calcul direct de D(P‖U) donne bien 0,44585. Pour la loi uniforme sur 4 issues, H = ln 4 ≈ 1,38629.

**Ce que la preuve révèle du mécanisme.** L'écart au maximum, ln n − H, mesure exactement combien P s'éloigne de « je n'en sais rien ». Plus le nombre d'issues est grand, plus le plafond ln n monte : on ne compare donc pas des entropies brutes sur des nombres d'issues différents.

**Conséquence pour un agent.** Pour fixer un seuil qui ne dépende pas du nombre d'outils, on normalise : H / ln n, entre 0 et 1. La règle « clarifier au-dessus de 85 % du maximum » garde le même sens avec 4 outils ou avec 12.

## Démonstration 3 — Deux sources indépendantes : les entropies s'additionnent

**Ce qu'on démontre.** Si X et Y sont indépendantes :

$$
H(X, Y) = H(X) + H(Y)
$$

et le nombre effectif d'issues de la paire est le produit des deux nombres effectifs.

**L'idée.** L'indépendance transforme la probabilité jointe en produit ; le logarithme transforme ce produit en somme ; la moyenne d'une somme est la somme des moyennes.

**La preuve, pas à pas.**

**Étape 1.** Par indépendance, P(x, y) = P(x) P(y), donc, parce que ln(ab) = ln a + ln b :

$$
-\ln P(x, y) = -\ln P(x) - \ln P(y)
$$

**Étape 2.** On multiplie par P(x) P(y) et on additionne sur tous les couples ; on sépare les deux sommes :

$$
H(X, Y) = -\sum_x \sum_y P(x) P(y) \ln P(x) - \sum_x \sum_y P(x) P(y) \ln P(y)
$$

**Étape 3.** Dans le premier terme, la somme sur y de P(y) vaut 1 ; dans le second, la somme sur x de P(x) vaut 1 :

$$
H(X, Y) = -\sum_x P(x) \ln P(x) - \sum_y P(y) \ln P(y) = H(X) + H(Y)
$$

**Étape 4.** En prenant l'exponentielle, exp(H(X, Y)) = exp(H(X)) × exp(H(Y)) : les nombres effectifs se multiplient. ∎

**Vérification chiffrée.** X = (0,3 ; 0,7) et Y = (0,5 ; 0,25 ; 0,25) : H(X) ≈ 0,61086 et H(Y) ≈ 1,03972 ; la loi jointe, à 6 cases, a une entropie de 1,65059 = 0,61086 + 1,03972. Nombres effectifs : 1,842 × 2,828 ≈ 5,21. Contre-exemple quand l'indépendance manque : si Y est une copie de X, avec X = (0,5 ; 0,5), la loi jointe n'a que deux cases et H(X, Y) = ln 2 ≈ 0,69315, moins que H(X) + H(Y) = 2 ln 2 ≈ 1,38629.

**Ce que la preuve révèle du mécanisme.** L'additivité est la raison d'être du logarithme dans la formule. Sans indépendance, la somme H(X) + H(Y) compte deux fois l'information commune : l'entropie de la paire est alors plus petite.

**Conséquence pour un agent.** L'incertitude de plusieurs choix indépendants (outil, puis paramètre) s'additionne ; un agent qui enchaîne des décisions indépendantes accumule donc de l'incertitude. Si les choix sont liés, il faut mesurer l'entropie de la paire et non additionner.

## Démonstration 4 — Changer d'unité, garder le nombre effectif

**Ce qu'on démontre.** L'entropie en bits est l'entropie en nats divisée par ln 2, et le nombre effectif d'issues ne dépend pas de l'unité :

$$
H_{\text{bits}} = \frac{H_{\text{nats}}}{\ln 2} \approx 1{,}4427 \times H_{\text{nats}}, \qquad 2^{H_{\text{bits}}} = e^{H_{\text{nats}}}
$$

**L'idée.** Changer de base de logarithme multiplie chaque logarithme par la même constante, donc multiplie toute la somme. L'exponentielle dans la bonne base défait exactement ce changement.

**La preuve, pas à pas.**

**Étape 1.** Par la formule de changement de base, log₂ x = ln x / ln 2 pour tout x > 0 :

$$
-\sum_i p_i \log_2 p_i = -\sum_i p_i \frac{\ln p_i}{\ln 2} = \frac{H_{\text{nats}}}{\ln 2}
$$

**Étape 2.** On élève 2 à cette puissance, parce que 2 à la puissance a / ln 2 vaut exp(a ln 2 / ln 2) = exp(a) :

$$
2^{H_{\text{bits}}} = 2^{H_{\text{nats}} / \ln 2} = e^{H_{\text{nats}}}
$$

∎

**Vérification chiffrée.** Une pièce équilibrée vaut ln 2 ≈ 0,693 nat, soit exactement 1 bit, et son nombre effectif vaut 2. Pour (0,9 ; 0,1) : 0,32508 nat = 0,46900 bit, et exp(0,32508) = 2 puissance 0,469 ≈ 1,38415.

**Ce que la preuve révèle du mécanisme.** Le nombre effectif exp(H) est la quantité qui ne dépend d'aucune convention : c'est la perplexité d'une distribution sur elle-même, au sens de la leçon 52. Le bit a un sens concret : une question oui/non équilibrée apporte exactement 1 bit.

**Conséquence pour un agent.** Dans les journaux et les seuils, on écrit toujours l'unité (nats ou bits), et l'on préfère afficher le nombre effectif, que tout le monde comprend : « le routeur hésite entre 2,6 outils ».

## Démonstration 5 — Regrouper les choix

**Ce qu'on démontre.** On répartit les issues en groupes g, de poids w(g) égal à la somme des pᵢ du groupe. Alors l'entropie se décompose en « choisir le groupe » plus « choisir dans le groupe » :

$$
H(P) = H(w) + \sum_g w_g \, H\!\left( \frac{p_i}{w_g},\ i \in g \right)
$$

**L'idée.** Tirer une issue revient à tirer d'abord son groupe, puis l'issue à l'intérieur du groupe. La surprise totale est la surprise du groupe plus la surprise à l'intérieur du groupe, parce que les probabilités se multiplient.

**La preuve, pas à pas.**

**Étape 1.** Pour une issue i du groupe g, pᵢ = w(g) × (pᵢ / w(g)), donc, parce que le logarithme d'un produit est la somme des logarithmes :

$$
-\ln p_i = -\ln w_g - \ln \frac{p_i}{w_g}
$$

**Étape 2.** On multiplie par pᵢ et on additionne sur toutes les issues, groupe par groupe. Le premier morceau donne −Σ w(g) ln w(g) = H(w), parce que la somme des pᵢ d'un groupe vaut w(g).

**Étape 3.** Le second morceau se réécrit en mettant w(g) en facteur dans chaque groupe :

$$
-\sum_g \sum_{i \in g} p_i \ln \frac{p_i}{w_g} = \sum_g w_g \left( -\sum_{i \in g} \frac{p_i}{w_g} \ln \frac{p_i}{w_g} \right) = \sum_g w_g \, H\!\left( \frac{p_i}{w_g},\ i \in g \right)
$$

∎

**Vérification chiffrée.** La distribution (0,5 ; 0,25 ; 0,25) se lit en deux temps : d'abord un choix équiprobable entre « première issue » et « les deux autres », puis, dans la moitié des cas, un choix équiprobable entre les deux autres :

$$
H(0{,}5\ ;\ 0{,}25\ ;\ 0{,}25) = H(0{,}5\ ;\ 0{,}5) + 0{,}5 \times H(0{,}5\ ;\ 0{,}5) = 1{,}5 \ln 2 \approx 1{,}03972
$$

Le calcul direct donne 0,5 ln 2 + 2 × 0,25 ln 4 = 0,5 ln 2 + ln 2 = 1,5 ln 2, le même nombre.

**Ce que la preuve révèle du mécanisme.** L'incertitude se range par étages : on peut dire quelle part vient du choix du groupe et quelle part vient du détail. Un étage dont l'incertitude est sans conséquence (des orthographes d'un même nom, par exemple) peut être retiré du calcul.

**Conséquence pour un agent.** On mesure l'entropie au niveau qui compte pour la décision : entre entités et non entre orthographes, entre familles d'outils avant les outils (cas 4). Une vérification déterministe qui tranche un étage supprime exactement l'entropie de cet étage.

## Exemple simple, à la main

$$
H(0{,}5\ ;\ 0{,}5) = -2 \times 0{,}5 \ln 0{,}5 = \ln 2 \approx 0{,}693
$$

Une distribution (0,9 ; 0,1) est beaucoup moins incertaine :

$$
H(0{,}9\ ;\ 0{,}1) = -(0{,}9 \ln 0{,}9 + 0{,}1 \ln 0{,}1) \approx 0{,}09482 + 0{,}23026 = 0{,}32508 \approx 0{,}325
$$

| distribution | surprises −ln pᵢ | termes −pᵢ ln pᵢ | H (nats) | H (bits) | nombre effectif |
| --- | --- | --- | --- | --- | --- |
| (0,5 ; 0,5) | 0,69315 ; 0,69315 | 0,34657 ; 0,34657 | 0,69315 | 1 | 2 |
| (0,9 ; 0,1) | 0,10536 ; 2,30259 | 0,09482 ; 0,23026 | 0,32508 | 0,46900 | 1,38415 |

## Cas d'usage complexes, démontrés

### Cas 1 — Entité de services publics en ligne : un routeur bilingue qui sait quand demander une précision

**Contexte.** Une entité de services publics en ligne, accessible par UAE Pass, fait router par un agent les demandes des résidents, en arabe, en anglais ou mélangées, vers 4 outils (rendez-vous, paiement, suivi de dossier, réclamation). Elle reçoit 30 000 demandes par jour ; on estime que 70 % ressemblent à la demande « claire » ci-dessous et 30 % à la demande « ambiguë » (chiffres illustratifs). Un mauvais outil coûte 4 AED (reprise, session recommencée) ; une question de clarification coûte 1,5 AED (un tour de plus, quelques abandons) et mène au bon outil. Question : quand l'agent doit-il demander une précision au lieu d'appeler l'outil le plus probable ?

**Données.**

- Demande claire : (0,7 ; 0,1 ; 0,1 ; 0,1). Demande ambiguë : (0,4 ; 0,35 ; 0,15 ; 0,1).
- Maximum possible : ln 4 ≈ 1,38629 ; seuil de clarification : 85 % du maximum.
- Coûts : mauvais outil 4 AED, clarification 1,5 AED ; volume 30 000 par jour.

**Calcul pas à pas.**

**Étape 1.** Demande claire : 0,7 × 0,35667 ≈ 0,24967 et 3 × 0,1 × 2,30259 ≈ 3 × 0,23026 = 0,69078.

$$
H(\text{claire}) \approx 0{,}24967 + 0{,}69078 = 0{,}94045, \qquad \frac{0{,}94045}{1{,}38629} \approx 68\ \%
$$

**Étape 2.** Demande ambiguë : termes 0,36652 ; 0,36744 ; 0,28457 ; 0,23026.

$$
H(\text{ambiguë}) \approx 1{,}24878, \qquad \frac{1{,}24878}{1{,}38629} \approx 90\ \%
$$

**Étape 3.** Coût attendu d'un appel direct à l'outil le plus probable : (1 − 0,7) × 4 = 1,2 AED pour la demande claire, (1 − 0,4) × 4 = 2,4 AED pour l'ambiguë. Clarifier coûte 1,5 AED.

**Étape 4.** Par jour : toujours appeler l'outil coûte 30 000 × (0,7 × 1,2 + 0,3 × 2,4) = 30 000 × (0,84 + 0,72) = 46 800 AED ; la règle des 85 % coûte 30 000 × (0,7 × 1,2 + 0,3 × 1,5) = 30 000 × (0,84 + 0,45) = 38 700 AED.

**Décision de l'agent.** Au-dessus de 85 % de l'entropie maximale, l'agent pose une question de clarification, dans la langue de la demande ; en dessous, il appelle l'outil le plus probable. Ici : appel direct pour la demande claire (68 %), clarification pour l'ambiguë (90 %).

**Contre-calcul.** Sans la règle, l'agent appelle toujours l'outil le plus probable : 46 800 AED par jour au lieu de 38 700, soit 8 100 AED par jour de reprises évitables (illustratif).

**Sensibilité.** Clarifier même la demande claire ne vaudrait la peine que si un mauvais outil coûtait plus de 1,5 / 0,3 = 5,0 AED ; pour l'ambiguë, la clarification reste meilleure tant que le coût dépasse 1,5 / 0,6 = 2,5 AED. Une baisse de 10 % du coût d'erreur (4 → 3,6 AED) ne change rien : 0,6 × 3,6 = 2,16 > 1,5 et 0,3 × 3,6 = 1,08 < 1,5. Limite de la règle : (0,5 ; 0,5 ; 0 ; 0) et (0,5 ; 1/6 ; 1/6 ; 1/6) ont le même risque d'erreur 0,5, soit 0,5 × 4 = 2,0 AED > 1,5, mais des entropies normalisées de 50 % et 89,624 % : la règle des 85 % laisserait passer la première, une hésitation franche entre deux outils.

**En production.** La règle finale combine les deux tests : clarifier si l'entropie normalisée dépasse 85 % ou si (1 − pmax) × coût d'erreur dépasse le coût d'une clarification. On suit la part des demandes clarifiées (alerte au-dessus de 40 %) et le taux d'abandon après une clarification. Une entropie basse dit que le routeur est sûr de lui, pas qu'il a raison : on mesure aussi sa calibration (fiche 20). Les données des résidents relèvent de la PDPL hors DIFC et ADGM.

### Cas 2 — Cabinet RH multi-émirats : poser le moins de questions possible pour identifier le type de permis

**Contexte.** Un cabinet RH multi-émirats accompagne 4 000 candidats par mois ; pour préparer un dossier de permis de travail, son agent doit identifier, par des questions oui/non posées au candidat, lequel de cinq types de dossier s'applique (types A à E, illustratifs ; les catégories réelles du MOHRE sont à confirmer avec le texte en vigueur). Chaque question fait abandonner 2 % des candidats (illustratif). Question : dans quel ordre poser les questions « est-ce le type … ? » ?

**Données.**

- Fréquences des types A à E : 0,5 ; 0,25 ; 0,125 ; 0,0625 ; 0,0625 (illustratif).
- Questions posées l'une après l'autre ; quand il ne reste qu'un type possible, on ne pose plus de question.
- Risque d'abandon : 2 % par question ; 4 000 candidats par mois.

**Calcul pas à pas.**

**Étape 1.** Entropie en bits (démonstration 4) :

$$
H = 0{,}5 \times 1 + 0{,}25 \times 2 + 0{,}125 \times 3 + 2 \times 0{,}0625 \times 4 = 0{,}5 + 0{,}5 + 0{,}375 + 0{,}5 = 1{,}875 \text{ bit}
$$

**Étape 2.** Questions dans l'ordre des fréquences décroissantes : il en faut 1 pour A, 2 pour B, 3 pour C, 4 pour D et 4 pour E (après trois « non », la quatrième question tranche entre D et E). Moyenne : 0,5 × 1 + 0,25 × 2 + 0,125 × 3 + 0,0625 × 4 + 0,0625 × 4 = 1,875 question, exactement H.

**Étape 3.** Ordre inverse (E, D, C, B, A) : 0,0625 × 1 + 0,0625 × 2 + 0,125 × 3 + 0,25 × 4 + 0,5 × 4 = 0,0625 + 0,125 + 0,375 + 1 + 2 = 3,5625 questions.

**Étape 4.** Abandon : un candidat qui reçoit k questions abandonne avec la probabilité 1 − 0,98ᵏ, soit 0,02 ; 0,0396 ; 0,05881 ; 0,07763 pour k = 1 à 4. En moyenne : 0,03695 dans l'ordre des fréquences, 0,06930 dans l'ordre inverse, soit 4 000 × 0,0323 ≈ 129,4 candidats perdus de plus par mois dans le mauvais ordre.

**Décision de l'agent.** Poser les questions dans l'ordre des fréquences décroissantes, recalculées chaque mois. Avec ces fréquences, la moyenne atteint exactement l'entropie en bits, et un résultat classique de théorie de l'information, admis ici, dit qu'aucune stratégie de questions oui/non ne peut faire mieux en moyenne.

**Contre-calcul.** Un ordre fixé sans regarder les fréquences (ici l'ordre inverse) coûte 3,5625 questions en moyenne au lieu de 1,875, et environ 129 candidats perdus par mois (illustratif). Si les cinq types étaient équiprobables, l'entropie vaudrait log₂ 5 ≈ 2,32193 bits et le questionnement séquentiel 2,8 questions : c'est l'inégalité des fréquences qui permet d'économiser des questions.

**Sensibilité.** Avec des fréquences non dyadiques (0,4 ; 0,3 ; 0,15 ; 0,1 ; 0,05), l'entropie vaut 2,00869 bits et l'ordre des fréquences donne 2,05 questions : l'écart à l'entropie reste petit (exercice 6). L'ordre optimal ne change que si deux fréquences se croisent : c'est la seule bascule à surveiller.

**En production.** On recalcule chaque mois les fréquences des types de dossier et l'ordre des questions, et l'on suit le taux d'abandon pendant le questionnement (alerte au-dessus de 5 %). Les données des candidats relèvent de la PDPL hors DIFC et ADGM ; les pièces exigées par le MOHRE pour chaque type sont à confirmer avec le texte en vigueur.

### Cas 3 — Groupe de construction à Dubaï : le nombre effectif de fournisseurs d'armatures

**Contexte.** Un groupe de construction sur de grands chantiers à Dubaï achète pour 12 M AED d'armatures en acier par an auprès de cinq fournisseurs (chiffres illustratifs). Sa politique d'achats exige au moins 4 fournisseurs « effectifs » pour un matériau critique, afin qu'une défaillance n'arrête pas les chantiers. L'agent achats mesure la concentration par le nombre effectif exp(H) des parts d'achat. Question : la politique est-elle respectée, et sinon, quel transfert faut-il ?

**Données.**

- Achats annuels par fournisseur, en M AED : 6,0 ; 3,0 ; 1,5 ; 1,0 ; 0,5 (total 12).
- Seuil : nombre effectif ≥ 4. Le fournisseur 5 est 3 % plus cher que le fournisseur 1 (illustratif).

**Calcul pas à pas.**

**Étape 1.** Parts : 0,5 ; 0,25 ; 0,125 ; 0,0833 ; 0,0417. Termes −p ln p : 0,34657 ; 0,34657 ; 0,25993 ; 0,20708 ; 0,13242.

$$
H \approx 1{,}29257, \qquad e^{H} \approx 3{,}642 < 4
$$

**Étape 2.** Transfert de 1,5 M AED du fournisseur 1 au fournisseur 5 : achats 4,5 ; 3,0 ; 1,5 ; 1,0 ; 2,0, parts 0,375 ; 0,25 ; 0,125 ; 0,0833 ; 0,1667. Les termes qui changent valent 0,36781 et 0,29863.

$$
H \approx 0{,}36781 + 0{,}34657 + 0{,}25993 + 0{,}20708 + 0{,}29863 = 1{,}48002, \qquad e^{H} \approx 4{,}393
$$

**Étape 3.** Transfert minimal x tel que exp(H) = 4, trouvé par dichotomie : x ≈ 0,558 M AED.

**Étape 4.** Surcoût de 3 % : 0,03 × 1,5 M = 45 000 AED pour le transfert de 1,5 M ; 0,03 × 0,558 M ≈ 16 738 AED pour le transfert minimal.

**Décision de l'agent.** Proposer à la direction des achats de transférer au moins 0,558 M AED par an du fournisseur 1 au fournisseur 5, pour un surcoût d'environ 16 738 AED : la politique est alors respectée au moindre coût.

**Contre-calcul.** Compter les fournisseurs donne 5 ≥ 4 : la politique semblerait respectée alors que la moitié des achats dépend d'un seul fournisseur. Le nombre effectif, 3,642, dit la vérité sur la concentration ; il vaut 5 seulement si les cinq parts sont égales (démonstration 2).

**Sensibilité.** Le nombre effectif réagit fortement aux grosses parts : déplacer 0,558 M sur 12 (4,7 % des achats) suffit à gagner 0,358 fournisseur effectif. Si le surcoût du fournisseur 5 passait de 3 % à 6 %, le transfert minimal coûterait le double, environ 33 476 AED, sans changer la quantité à transférer.

**En production.** On suit chaque mois le nombre effectif de fournisseurs par matériau critique (alerte sous 4) et, en complément, la plus grosse part (alerte au-dessus de 45 %), car l'entropie seule ne borne pas assez la dépendance à un fournisseur. Les factures des fournisseurs portent une TVA de 5 %, sans effet sur les parts calculées hors taxes.

### Cas 4 — Banque de détail de Dubaï : orthographes d'un même prénom, ou deux personnes différentes ?

**Contexte.** Une banque de détail de Dubaï fait rapprocher par un agent le certificat de salaire d'un client de sa fiche KYC, avant de calculer son ratio d'endettement. Le certificat est en arabe ; l'agent propose plusieurs translittérations du prénom, avec des probabilités. Sur 3 000 certificats par mois, 300 présentent ce genre d'ambiguïté (chiffres illustratifs). Une revue humaine à quatre options coûte 8 AED, à deux options 3 AED (illustratif). Question : envoyer en revue, et avec combien d'options ?

**Données.**

- Candidats : « Mohammed » 0,35 ; « Muhammad » 0,30 ; « Mohamed » 0,15 ; « Mahmoud » 0,20. Les trois premiers sont des orthographes du même prénom (محمد), le quatrième un autre prénom (محمود).
- Règle de la banque : rapprochement automatique seulement si l'entropie normalisée des entités est < 0,85 et si l'entité la plus probable a au moins 0,95.
- Dossier : salaire 18 000 AED, mensualités existantes 5 000 AED, nouvelle mensualité 3 500 AED.

**Calcul pas à pas.**

**Étape 1.** Entropie brute sur les quatre orthographes : H ≈ 1,33509, soit 1,33509 / 1,38629 ≈ 0,96306 du maximum.

**Étape 2.** Regroupement par entité (démonstration 5) : poids (0,8 ; 0,2), dont l'entropie vaut H(0,8 ; 0,2) ≈ 0,50040 ; à l'intérieur du groupe « محمد », les parts 0,4375 ; 0,375 ; 0,1875 ont une entropie de 1,04335.

$$
H \approx 0{,}50040 + 0{,}8 \times 1{,}04335 = 0{,}50040 + 0{,}83468 = 1{,}33509
$$

**Étape 3.** Entropie normalisée des entités : 0,50040 / ln 2 ≈ 0,72193 < 0,85. Mais l'entité la plus probable n'a que 0,8 < 0,95.

**Étape 4.** Ratio d'endettement, si le rapprochement est confirmé : 5 000 + 3 500 = 8 500 AED ≤ 50 % × 18 000 = 9 000 AED.

**Décision de l'agent.** Revue humaine à deux options (« محمد » ou « محمود »), à 3 AED au lieu de 8 : l'incertitude entre orthographes (0,83468 nat sur 1,33509) ne concerne pas l'identité et ne justifie pas une revue à quatre options. Le ratio d'endettement n'est calculé qu'après la confirmation.

**Contre-calcul.** Sur l'entropie brute (96 % du maximum), on enverrait 300 revues à quatre options par mois, soit 300 × 8 = 2 400 AED au lieu de 300 × 3 = 900 AED. À l'inverse, sur la seule entropie des entités (72 % < 85 %), on rapprocherait automatiquement et l'on se tromperait de personne dans 20 % des cas : 0,2 × 300 = 60 erreurs KYC par mois.

**Sensibilité.** L'entropie normalisée des entités atteint 0,85 quand la part de « Mahmoud » vaut m ≈ 0,2760 ; mais le test de probabilité est plus exigeant : à m = 0,05, l'entropie normalisée ne vaut que 0,28640, et c'est seulement là que le rapprochement automatique devient permis. Pour une décision de conformité, c'est la probabilité, calibrée (fiche 20), qui décide ; l'entropie sert à choisir la forme de la revue.

**En production.** On normalise l'arabe (alef, ta marbuta, diacritiques) et l'on regroupe les translittérations connues avant de mesurer l'entropie ; on suit la part des certificats envoyés en revue et le taux d'erreurs de rapprochement découvertes plus tard. Les règles CBUAE (ratio d'endettement total ≤ 50 % du salaire) s'appliquent après le rapprochement ; les exigences KYC précises sont à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Calculer H pour une loi uniforme sur 8 issues, en nats puis en bits.

**Exercice 2.** Calculer H(1 ; 0) et H(0,25 ; 0,25 ; 0,25 ; 0,25).

**Exercice 3.** Calculer H(0,9 ; 0,1) en bits.

**Exercice 4.** Vérifier la démonstration 5 en calculant directement H(0,5 ; 0,25 ; 0,25).

**Exercice 5.** Pourquoi la loi (0,4 ; 0,35 ; 0,15 ; 0,1) a-t-elle une entropie plus grande que (0,7 ; 0,1 ; 0,1 ; 0,1) ?

**Exercice 6 (cas modifié).** Dans le cas 2, les fréquences des types deviennent 0,4 ; 0,3 ; 0,15 ; 0,1 ; 0,05. Calculer l'entropie en bits et le nombre moyen de questions dans l'ordre des fréquences.

**Exercice 7 (trouver l'erreur).** Un collègue écrit : « H(0,5 ; 0,25 ; 0,25) = 1,5, donc le routeur a 1,5 nat d'incertitude. » Trouver l'erreur.

**Exercice 8 (redémontrer de mémoire).** Redémontrer que H(P) ≤ ln n, avec égalité pour la loi uniforme, puis en déduire que le nombre effectif exp(H) ne dépasse jamais n.

## Corrigé

**Exercice 1.** Chaque issue a la probabilité 1/8 : H = −8 × (1/8) ln(1/8) = ln 8 ≈ 2,079 nats ; en bits, log₂ 8 = 3 bits.

**Exercice 2.** H(1 ; 0) = −1 × ln 1 − 0 = 0 (convention 0 × ln 0 = 0). H(uniforme sur 4) = ln 4 ≈ 1,386.

**Exercice 3.** 0,32508 / 0,69315 ≈ 0,469 bit.

**Exercice 4.** 0,5 ln 2 + 2 × 0,25 ln 4 = 0,5 ln 2 + 0,5 × 2 ln 2 = 0,5 ln 2 + ln 2 = 1,5 ln 2 ≈ 1,03972.

**Exercice 5.** Elle est plus proche de l'uniforme : l'écart ln 4 − H vaut 1,38629 − 1,24878 ≈ 0,138 contre 0,44585 (démonstration 2). Les probabilités sont plus étalées, donc l'issue est plus difficile à deviner.

**Exercice 6.** H = −(0,4 log₂ 0,4 + 0,3 log₂ 0,3 + 0,15 log₂ 0,15 + 0,1 log₂ 0,1 + 0,05 log₂ 0,05) ≈ 2,00869 bits. Questions : 0,4 × 1 + 0,3 × 2 + 0,15 × 3 + 0,1 × 4 + 0,05 × 4 = 0,4 + 0,6 + 0,45 + 0,4 + 0,2 = 2,05, un peu plus que H, parce que les fréquences ne sont pas des puissances de 1/2.

**Exercice 7.** L'unité est fausse : 1,5 est la valeur en bits (H(0,5 ; 0,5) = 1 bit, plus 0,5 × 1 bit). En nats, H = 1,5 ln 2 ≈ 1,03972. Le nombre effectif est le même dans les deux unités : 2 puissance 1,5 = exp(1,03972) ≈ 2,83.

**Exercice 8.** D(P‖U) = Σ pᵢ ln(pᵢ / (1/n)) = −H(P) + ln n ≥ 0 par Gibbs, avec égalité seulement si P = U. Comme l'exponentielle est croissante, exp(H) ≤ exp(ln n) = n ; pour l'uniforme sur 4, exp(H) = 4.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`H(P, base)`** — Cette fonction est la mesureuse de surprise, qui dit combien il est difficile de deviner l'issue d'un tirage : elle reçoit une distribution et une base de logarithme, e par défaut pour un résultat en nats, refuse par une `ValueError` des valeurs négatives ou une somme qui s'écarte de 1, puis additionne −p log p sur les seules issues de probabilité positive, puisque 0 × log 0 vaut 0 par convention. Elle renvoie l'entropie, soit 0,693 nat pour une pièce équilibrée, 0,325 nat ou 0,469 bit pour la loi (0,9 ; 0,1), et presque toutes les autres fonctions l'appellent.

**`ratio_max(P)`** — On la voit en jauge qui indique où se situe une incertitude entre la certitude et le brouillard complet : elle reçoit une distribution, renvoie `None` s'il n'y a qu'une seule issue, faute de maximum à comparer, et sinon divise l'entropie par ln n, sa plus grande valeur possible. Elle renvoie un nombre entre 0 et 1, soit 0,96306 pour les quatre translittérations du cas 4, au-dessus du seuil de 0,85 qui déclenche une demande de précision ou une revue.

**`nombre_effectif(P)`** — Cette fonction traduit l'entropie en une image parlante, le nombre de choix équiprobables qui laisseraient la même incertitude : elle reçoit une distribution et renvoie exp(H). Quatre issues équiprobables donnent exactement 4, et les parts d'achat du cas 3 donnent 3,642 fournisseurs « effectifs » sur 5, sous le minimum de 4 qu'exige la politique d'achats ; `effectif_apres` l'appelle pour mesurer l'effet d'un transfert.

**`entropie_groupee(groupes)`** — Celle-ci raconte un tri en deux temps, comme un postier qui range d'abord le courrier par quartier, puis par rue : elle reçoit une liste de groupes de probabilités, calcule le poids de chaque groupe, puis renvoie l'entropie des poids augmentée de la moyenne, pondérée par ces poids, des entropies à l'intérieur de chaque groupe renormalisé. Elle illustre la règle du regroupement de la démonstration 5 : pour (0,5) et (0,25 ; 0,25), elle redonne 1,03972, l'entropie de (0,5 ; 0,25 ; 0,25), et dans le cas 4 elle retrouve exactement les 1,33509 de la distribution brute.

**`questions_moyennes(probas)`** — Cette fonction compte les questions d'un jeu où l'on demande « est-ce la catégorie i ? » dans un ordre fixé : elle reçoit les probabilités des catégories dans l'ordre où on les teste et additionne, pour chacune, sa probabilité multipliée par le nombre de questions nécessaires pour l'atteindre, k + 1 pour la k-ième, sans dépasser n − 1, la dernière se déduisant de l'avant-dernière réponse. Elle renvoie le nombre moyen de questions : 1,875 dans l'ordre probable du cas 2, exactement l'entropie en bits, 3,5625 dans l'ordre inverse et 2,05 pour l'exercice 6.

**`abandon_moyen(probas, risque)`** — Celle-ci chiffre l'usure du candidat à qui l'on pose trop de questions : elle reçoit les probabilités des catégories dans l'ordre des questions et le risque qu'une question fasse abandonner, 2 % par défaut, puis additionne pour chaque catégorie sa probabilité multipliée par la chance d'abandonner au moins une fois au fil des questions qu'elle exige. Elle renvoie le taux d'abandon moyen, 0,03695 dans l'ordre probable du cas 2 contre 0,06930 dans l'ordre inverse.

**`bisection(f, a, b, pas)`** — Cette fonction est le chercheur de trésor qui coupe chaque fois la zone de fouille en deux : elle reçoit une fonction f, un intervalle aux bornes de signes opposés et un nombre de pas, soixante par défaut, regarde le signe au milieu et garde la moitié où le signe change, puis renvoie le milieu final. Elle trouve dans le cas 3 le transfert minimal de 0,558 M AED qui porte le nombre effectif à 4, et dans le cas 4 la part de bascule 0,2760 du prénom distinct.

**`proche(x, attendu, decimales)`** — Ce petit contrôleur compare deux nombres comme on rapproche deux lignes d'un registre arrondi : il reçoit la valeur calculée, la valeur attendue et un nombre de décimales, arrondit les deux à ce nombre de chiffres et renvoie vrai s'ils coïncident. Presque tous les `assert` de `main` passent par lui, de l'écart 0,44585 à la loi uniforme jusqu'aux 129,4 candidats du cas 2, pour confronter les résultats aux valeurs écrites dans la fiche.

**`demonstrations()`** — Cette fonction rejoue les cinq démonstrations : elle ne reçoit rien, montre que les deux termes de la loi (0,9 ; 0,1), 0,09482 et 0,23026, sont positifs alors qu'un « score » de 2 pris pour une probabilité donnerait −1,386, puis que ln 4 moins l'entropie de la demande claire vaut 0,44585, exactement sa divergence à la loi uniforme. Elle montre ensuite qu'une variable copiée sur une autre a une entropie jointe de 0,69315, inférieure à la somme 1,38629, que 0,32508 nat font 0,46900 bit avec le même nombre effectif 1,38415, et que la règle du regroupement redonne 1,03972 ; elle imprime ces nombres et les renvoie.

**`cas_1_public_routeur(claire, ambigue)`** — Cette fonction met en scène un service public dont l'agent route 30 000 demandes par jour vers quatre outils, 70 % de demandes claires et 30 % de demandes ambiguës, sachant qu'un mauvais outil coûte 4 AED et une question de clarification 1,5 AED : elle reçoit les deux distributions et calcule le coût d'un appel direct, 1,20 AED pour la demande claire et 2,40 pour l'ambiguë. Toujours appeler coûte 46 800 AED par jour, contre 38 700 avec la règle qui clarifie au-dessus de 85 % de l'entropie maximale ; elle calcule les coûts d'erreur de bascule, 5,0 et 2,5 AED, et montre que deux demandes de même probabilité maximale 0,5 peuvent être à 0,50 ou à 0,89624 du maximum, puis renvoie ces résultats.

**`cas_2_rh_questions()`** — On y suit un cabinet de recrutement qui accompagne 4 000 candidats par mois et doit identifier, par des questions oui ou non, lequel de cinq types de dossier s'applique, chaque question faisant abandonner 2 % des candidats : la fonction ne reçoit rien, calcule l'entropie de 1,875 bit des probabilités 0,5, 0,25, 0,125, 0,0625 et 0,0625, et la compare aux 1,875 questions de l'ordre probable et aux 3,5625 de l'ordre inverse, ainsi qu'aux 2,32193 bits d'une loi uniforme. Elle en déduit des taux d'abandon de 0,03695 et 0,06930, soit 129,4 candidats gardés par mois en posant les questions dans le bon ordre, et renvoie ces nombres.

**`cas_3_btp_fournisseurs()`** — Cette fonction raconte un groupe de construction qui achète 12 M AED d'armatures par an à cinq fournisseurs, pour 6, 3, 1,5, 1 et 0,5 M AED, et dont la politique exige au moins quatre fournisseurs effectifs : elle ne reçoit rien, calcule une entropie de 1,29257 et un nombre effectif de 3,642, donc insuffisant, puis 1,48002 et 4,393 après un transfert de 1,5 M AED du plus gros au plus petit. Elle cherche par `bisection` le transfert minimal, 0,558 M AED, et chiffre le surcoût de 3 % du cinquième fournisseur, plus cher que le premier, soit 45 000 AED pour le transfert complet et 16 738 au minimum, puis renvoie ces résultats.

**`effectif_apres(x)`** — Cette fonction interne vit dans `cas_3_btp_fournisseurs`, comme le simulateur que l'acheteur fait tourner avant de signer : elle reçoit un montant x en millions d'AED, le retire au premier fournisseur, qui passe de 6 à 6 − x, l'ajoute au dernier, qui passe de 0,5 à 0,5 + x, renormalise les cinq parts et renvoie leur nombre effectif. Elle vaut 4,393 pour x = 1,5, et c'est la fonction dont `bisection` cherche le passage par 4, à x = 0,558.

**`cas_4_banque_translitteration()`** — Ici, une banque rapproche le certificat de salaire en arabe d'un client de sa fiche de connaissance client, et l'agent propose quatre translittérations du prénom, avec les probabilités 0,35, 0,30, 0,15 et 0,20, dont les trois premières désignent en réalité le même prénom : la fonction ne reçoit rien et trouve une entropie brute de 1,33509, à 0,96306 du maximum, mais de 0,50040 seulement, à 0,72193, une fois les variantes regroupées en deux prénoms distincts. Elle vérifie que la règle du regroupement redonne l'entropie brute, trouve la part de bascule 0,2760 du prénom distinct, compte 60 erreurs par mois si l'on automatisait sur les 300 cas ambigus, contrôle que des mensualités de 8 500 AED restent sous les 9 000 autorisés, et renvoie ces nombres.

**`main()`** — C'est le chef d'orchestre de la fiche : il appelle `demonstrations` et vérifie chacun de ses nombres, recalcule les entropies 0,693 et 0,325, puis décide pour les demandes claire et ambiguë, à 68 % et 90 % du maximum, d'appeler un outil ou de demander une précision. Il contrôle encore les bornes de l'entropie et son additivité pour deux variables indépendantes, joue les quatre cas et le corrigé, puis s'assure qu'une seule issue rend le ratio indéfini et que des distributions invalides lèvent une `ValueError` ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tout concorde.

```python
"""Démonstration 21 — entropie : positivité, maximum uniforme, additivité, unités, regroupement, quatre cas."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def H(P, base=math.e):
    """Entropie −Σ p log p dans la base choisie ; 0 × log 0 = 0 ; ValueError si P n'est pas une distribution."""
    if any(p < 0 for p in P) or abs(sum(P) - 1) > 1e-9:
        raise ValueError("une distribution a des valeurs >= 0 qui somment à 1")
    return 0.0 - sum(p * math.log(p, base) for p in P if p > 0)


def ratio_max(P):
    """H(P) / ln n : 0 pour une certitude, 1 pour l'uniforme ; None s'il n'y a qu'une issue."""
    return None if len(P) < 2 else H(P) / math.log(len(P))


def nombre_effectif(P):
    """exp(H) : le nombre d'issues équiprobables qui auraient la même incertitude."""
    return math.exp(H(P))


def entropie_groupee(groupes):
    """groupes = listes de probabilités ; H(poids des groupes) + Σ poids × H(intérieur du groupe)."""
    poids = [sum(g) for g in groupes]
    return H(poids) + sum(w * H([p / w for p in g]) for w, g in zip(poids, groupes) if w > 0)


def questions_moyennes(probas):
    """Nombre moyen de questions « est-ce la catégorie i ? » posées dans l'ordre donné."""
    n = len(probas)
    return sum(p * min(k + 1, n - 1) for k, p in enumerate(probas))


def abandon_moyen(probas, risque=0.02):
    n = len(probas)
    return sum(p * (1 - (1 - risque) ** min(k + 1, n - 1)) for k, p in enumerate(probas))


def bisection(f, a, b, pas=60):
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
    termes = [-p * math.log(p) for p in (0.9, 0.1)]
    print(f"  D1 termes de (0.9 ; 0.1) : {termes[0]:.5f} et {termes[1]:.5f} ; un « score » 2 : {-2 * math.log(2):.3f}")
    claire = (0.7, 0.1, 0.1, 0.1)
    d_unif = sum(p * math.log(p / 0.25) for p in claire)
    print(f"  D2 ln 4 - H(claire) = {math.log(4) - H(claire):.5f} = D(claire || U) = {d_unif:.5f}")
    copie = H((0.5, 0, 0, 0.5))
    print(f"  D3 X copie de Y : H(X, Y) = {copie:.5f} < H(X) + H(Y) = {2 * math.log(2):.5f}")
    nats, bits = H((0.9, 0.1)), H((0.9, 0.1), 2)
    print(f"  D4 (0.9 ; 0.1) : {nats:.5f} nat = {bits:.5f} bit ; e^H = {math.exp(nats):.5f} = 2^H = {2 ** bits:.5f}")
    groupe = entropie_groupee([[0.5], [0.25, 0.25]])
    print(f"  D5 H(0.5 ; 0.25 ; 0.25) = {H((0.5, 0.25, 0.25)):.5f} = regroupé {groupe:.5f}")
    return {"termes": termes, "d_unif": d_unif, "copie": copie, "nats": nats, "bits": bits, "groupe": groupe}


def cas_1_public_routeur(claire, ambigue):
    couts = {}
    for nom, P in (("claire", claire), ("ambiguë", ambigue)):
        couts[nom] = (1 - max(P)) * 4
    direct = 30_000 * (0.7 * couts["claire"] + 0.3 * couts["ambiguë"])
    regle = 30_000 * (0.7 * couts["claire"] + 0.3 * 1.5)
    meme_max = (H((0.5, 0.5, 0, 0)) / math.log(4), H((0.5, 1 / 6, 1 / 6, 1 / 6)) / math.log(4))
    print(f"Cas 1 : coût d'un appel direct : claire {couts['claire']:.2f}, ambiguë {couts['ambiguë']:.2f} AED ;"
          f" par jour : toujours appeler {direct:.0f}, règle 85 % {regle:.0f} AED")
    print(f"  bascules du coût d'erreur : claire {1.5 / (1 - max(claire)):.1f}, ambiguë {1.5 / (1 - max(ambigue)):.1f} AED ;"
          f" même max 0.5 : {meme_max[0]:.2f} et {meme_max[1]:.5f} du maximum")
    return {"couts": couts, "direct": direct, "regle": regle, "meme_max": meme_max}


def cas_2_rh_questions():
    probas = [0.5, 0.25, 0.125, 0.0625, 0.0625]          # types A à E de permis (illustratifs)
    bits = H(probas, 2)
    bon, inverse = questions_moyennes(probas), questions_moyennes(probas[::-1])
    ab_bon, ab_inv = abandon_moyen(probas), abandon_moyen(probas[::-1])
    perdus = 4000 * (ab_inv - ab_bon)
    uniforme = math.log2(5)
    print(f"Cas 2 : H = {bits:.3f} bits ; questions : ordre probable {bon:.4f}, ordre inverse {inverse:.4f} ;"
          f" uniforme {uniforme:.5f} bits")
    print(f"  abandon : {ab_bon:.5f} contre {ab_inv:.5f} ; candidats perdus évités {perdus:.1f}/mois")
    return {"bits": bits, "bon": bon, "inverse": inverse, "ab_bon": ab_bon, "ab_inv": ab_inv, "perdus": perdus,
            "uniforme": uniforme, "questions_uniforme": questions_moyennes([0.2] * 5)}


def cas_3_btp_fournisseurs():
    achats = [6.0, 3.0, 1.5, 1.0, 0.5]                    # millions d'AED d'armatures par fournisseur
    parts = [a / sum(achats) for a in achats]
    h0, n0 = H(parts), nombre_effectif(parts)

    def effectif_apres(x):
        a = [6.0 - x, 3.0, 1.5, 1.0, 0.5 + x]
        return nombre_effectif([v / sum(a) for v in a])

    n1 = effectif_apres(1.5)
    h1 = math.log(n1)
    x_min = bisection(lambda x: effectif_apres(x) - 4, 0.0, 1.5)
    surcout = 0.03 * 1.5e6
    surcout_min = 0.03 * x_min * 1e6
    print(f"Cas 3 : H = {h0:.5f}, nombre effectif {n0:.3f} sur 5 ; après transfert de 1.5 M : H = {h1:.5f},"
          f" effectif {n1:.3f}")
    print(f"  transfert minimal {x_min:.3f} M AED ; surcoût 3 % : {surcout:.0f} AED, au minimum {surcout_min:.0f} AED")
    return {"parts": parts, "h0": h0, "n0": n0, "n1": n1, "h1": h1, "x_min": x_min, "surcout": surcout,
            "surcout_min": surcout_min}


def cas_4_banque_translitteration():
    candidats = [0.35, 0.30, 0.15, 0.20]                  # Mohammed, Muhammad, Mohamed, Mahmoud
    h_brut, r_brut = H(candidats), ratio_max(candidats)
    groupes = [[0.35, 0.30, 0.15], [0.20]]
    h_groupe = entropie_groupee(groupes)
    h_entites = H([0.80, 0.20])
    r_entites = h_entites / math.log(2)
    interieur = H([0.35 / 0.8, 0.30 / 0.8, 0.15 / 0.8])
    m_bascule = bisection(lambda m: H([1 - m, m]) / math.log(2) - 0.85, 0.01, 0.5)
    mensualites = 5000 + 3500
    print(f"Cas 4 : H brut {h_brut:.5f} ({r_brut:.5f} du maximum) ; entités {h_entites:.5f} ({r_entites:.5f}) ;"
          f" intérieur {interieur:.5f} ; regroupé {h_groupe:.5f}")
    print(f"  bascule part « Mahmoud » {m_bascule:.4f} ; erreurs si automatique {0.2 * 300:.0f}/mois ;"
          f" mensualités {mensualites} <= {0.5 * 18000:.0f}")
    return {"h_brut": h_brut, "r_brut": r_brut, "h_groupe": h_groupe, "h_entites": h_entites,
            "r_entites": r_entites, "interieur": interieur, "m": m_bascule, "mensualites": mensualites}


def main() -> None:
    d = demonstrations()
    assert [round(t, 5) for t in d["termes"]] == [0.09482, 0.23026] and proche(-2 * math.log(2), -1.386, 3)
    assert proche(d["d_unif"], 0.44585, 5) and math.isclose(d["d_unif"], math.log(4) - H((0.7, 0.1, 0.1, 0.1)))
    assert proche(d["copie"], 0.69315, 5) and d["copie"] < 2 * math.log(2) and proche(2 * math.log(2), 1.38629, 5)
    assert proche(d["nats"], 0.32508, 5) and proche(d["bits"], 0.46900, 5) and proche(math.exp(d["nats"]), 1.38415, 5)
    assert math.isclose(math.exp(d["nats"]), 2 ** d["bits"]) and proche(1 / math.log(2), 1.4427, 4)
    assert proche(d["groupe"], 1.03972, 5) and math.isclose(d["groupe"], 1.5 * math.log(2))
    assert [round(-math.log(p), 5) for p in (0.9, 0.1, 0.5)] == [0.10536, 2.30259, 0.69315]
    assert round(math.log(10) / -math.log(0.9)) == 22 and 0.1 * math.log(10) / H((0.9, 0.1)) > 2 / 3
    assert proche(math.exp(H((0.7, 0.1, 0.1, 0.1))), 2.6, 1) and proche(-math.log(0.7), 0.35667, 5)
    assert proche(0.558 / 12, 0.047, 3) and proche(4 - math.exp(H([0.5, 0.25, 0.125, 1 / 12, 1 / 24])), 0.358, 3)
    assert proche(2 * 0.03 * 0.5579288522589578e6, 33_476, 0) and proche(math.log(4) - 1.24878, 0.138, 3)
    assert proche(2 ** 1.5, 2.83, 2) and proche(math.exp(1.5 * math.log(2)), 2 ** 1.5, 12)

    print(f"H(0,5 ; 0,5) = {H((0.5, 0.5)):.3f} ; H(0,9 ; 0,1) = {H((0.9, 0.1)):.3f}")
    assert round(H((0.5, 0.5)), 3) == 0.693 and round(H((0.9, 0.1)), 3) == 0.325
    claire, ambigue = (0.7, 0.1, 0.1, 0.1), (0.4, 0.35, 0.15, 0.1)
    for nom, P in (("claire", claire), ("ambiguë", ambigue)):
        r = H(P) / math.log(4)
        print(f"demande {nom} : H = {H(P):.5f} ; {r:.0%} du maximum -> {'clarifier' if r > 0.85 else 'appeler un outil'}")
    assert round(H(claire), 5) == 0.94045 and round(H(ambigue), 5) == 1.24878
    assert round(H(claire) / math.log(4), 2) == 0.68 and round(H(ambigue) / math.log(4), 2) == 0.90
    assert [round(-p * math.log(p), 5) for p in (0.7, 0.1)] == [0.24967, 0.23026] and proche(3 * 0.23026, 0.69078, 5)
    assert [round(-p * math.log(p), 5) for p in ambigue] == [0.36652, 0.36744, 0.28457, 0.23026]

    for P in (claire, ambigue, (0.2, 0.3, 0.5)):
        assert 0 <= H(P) <= math.log(len(P))                                              # démonstrations 1 et 2
    X, Y = (0.3, 0.7), (0.5, 0.25, 0.25)
    jointe = [a * b for a in X for b in Y]
    assert math.isclose(H(jointe), H(X) + H(Y))                                           # démonstration 3
    assert proche(H(X), 0.61086, 5) and proche(H(jointe), 1.65059, 5) and proche(math.exp(H(jointe)), 5.21, 2)
    assert math.isclose(H((0.5, 0.5), 2), 1) and math.isclose(H((0.5, 0.25, 0.25)), 1.5 * math.log(2))

    c1 = cas_1_public_routeur(claire, ambigue)
    assert proche(c1["couts"]["claire"], 1.2, 9) and proche(c1["couts"]["ambiguë"], 2.4, 9)
    assert c1["couts"]["claire"] < 1.5 < c1["couts"]["ambiguë"]
    assert proche(c1["direct"], 46_800, 6) and proche(c1["regle"], 38_700, 6) and proche(c1["direct"] - c1["regle"], 8_100, 6)
    assert proche(0.7 * 1.2, 0.84, 9) and proche(0.3 * 2.4, 0.72, 9) and proche(0.3 * 1.5, 0.45, 9)
    assert proche(1.5 / 0.3, 5, 9) and proche(1.5 / 0.6, 2.5, 9) and proche(0.6 * 3.6, 2.16, 9) and proche(0.3 * 3.6, 1.08, 9)
    assert proche(c1["meme_max"][0], 0.5, 9) and proche(c1["meme_max"][1], 0.89624, 5)
    assert proche(H((0.5, 1 / 6, 1 / 6, 1 / 6)), 1.24245, 5)

    c2 = cas_2_rh_questions()
    assert proche(c2["bits"], 1.875, 9) and proche(c2["bon"], 1.875, 9) and proche(c2["inverse"], 3.5625, 9)
    assert proche(c2["uniforme"], 2.32193, 5) and proche(c2["questions_uniforme"], 2.8, 9)
    assert proche(c2["ab_bon"], 0.03695, 5) and proche(c2["ab_inv"], 0.06930, 5) and proche(c2["perdus"], 129.4, 1)
    assert [round(x, 4) for x in (0.5 * 1, 0.25 * 2, 0.125 * 3, 0.0625 * 4)] == [0.5, 0.5, 0.375, 0.25]
    assert [round(1 - 0.98 ** k, 5) for k in (1, 2, 3, 4)] == [0.02, 0.0396, 0.05881, 0.07763]
    assert proche(c2["ab_inv"] - c2["ab_bon"], 0.0323, 4) and proche(0.0625 + 0.125 + 0.375 + 1.0 + 2.0, 3.5625, 9)

    c3 = cas_3_btp_fournisseurs()
    assert [round(x, 4) for x in c3["parts"]] == [0.5, 0.25, 0.125, 0.0833, 0.0417]
    assert proche(c3["h0"], 1.29257, 5) and proche(c3["n0"], 3.642, 3) and c3["n0"] < 4
    assert proche(c3["h1"], 1.48002, 5) and proche(c3["n1"], 4.393, 3) and c3["n1"] >= 4
    assert proche(c3["x_min"], 0.558, 3) and proche(c3["surcout"], 45_000, 6) and proche(c3["surcout_min"], 16_738, 0)
    assert [round(-p * math.log(p), 5) for p in c3["parts"]] == [0.34657, 0.34657, 0.25993, 0.20708, 0.13242]
    assert [round(-p * math.log(p), 5) for p in (0.375, 2 / 12)] == [0.36781, 0.29863]
    assert [round(x, 4) for x in (4.5 / 12, 2.0 / 12)] == [0.375, 0.1667] and proche(0.03 * 0.558e6, 16_740, 0)

    c4 = cas_4_banque_translitteration()
    assert proche(c4["h_brut"], 1.33509, 5) and proche(c4["r_brut"], 0.96306, 5) and c4["r_brut"] > 0.85
    assert proche(c4["h_entites"], 0.50040, 5) and proche(c4["r_entites"], 0.72193, 5) and c4["r_entites"] < 0.85
    assert proche(c4["interieur"], 1.04335, 5) and math.isclose(c4["h_groupe"], c4["h_brut"])
    assert math.isclose(c4["h_brut"], c4["h_entites"] + 0.8 * c4["interieur"]) and proche(0.8 * c4["interieur"], 0.83468, 5)
    assert proche(c4["m"], 0.2760, 4) and c4["mensualites"] == 8500 and 8500 <= 0.5 * 18000
    assert [round(x, 4) for x in (0.35 / 0.8, 0.30 / 0.8, 0.15 / 0.8)] == [0.4375, 0.375, 0.1875]
    assert proche(H((0.95, 0.05)) / math.log(2), 0.28640, 5) and 300 * 8 == 2400 and 300 * 3 == 900
    assert proche(0.5 * 4, 2.0, 9) and 2.0 > 1.5 and proche(math.exp(H(X)), 1.842, 3) and proche(math.exp(H(Y)), 2.828, 3)

    print("Corrigé")
    print(f"  ex1 {H([1 / 8] * 8):.3f} nats = {H([1 / 8] * 8, 2):.0f} bits ; ex2 {H((1, 0))} et {H([0.25] * 4):.3f} ;"
          f" ex3 {H((0.9, 0.1), 2):.3f} bit ; ex4 {H((0.5, 0.25, 0.25)):.5f}")
    assert round(H([1 / 8] * 8), 3) == 2.079 and math.isclose(H([1 / 8] * 8, 2), 3)
    assert H((1, 0)) == 0 and round(H((0.9, 0.1), 2), 3) == 0.469 and round(H((0.5, 0.25, 0.25)), 5) == 1.03972
    e6 = questions_moyennes([0.4, 0.3, 0.15, 0.1, 0.05])
    e7 = H((0.5, 0.25, 0.25), 2)
    print(f"  ex6 {H([0.4, 0.3, 0.15, 0.1, 0.05], 2):.5f} bits, {e6:.2f} questions ; ex7 {e7:.1f} bits ;"
          f" ex8 effectif {nombre_effectif([0.25] * 4):.0f}")
    assert proche(H([0.4, 0.3, 0.15, 0.1, 0.05], 2), 2.00869, 5) and proche(e6, 2.05, 9) and proche(e7, 1.5, 9)
    assert proche(nombre_effectif([0.25] * 4), 4, 9) and ratio_max([1.0]) is None
    for mauvais in (lambda: H((0.6, 0.6)), lambda: H((-0.1, 1.1))):
        try:
            mauvais()
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError attendue")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Démonstrations
  D1 termes de (0.9 ; 0.1) : 0.09482 et 0.23026 ; un « score » 2 : -1.386
  D2 ln 4 - H(claire) = 0.44585 = D(claire || U) = 0.44585
  D3 X copie de Y : H(X, Y) = 0.69315 < H(X) + H(Y) = 1.38629
  D4 (0.9 ; 0.1) : 0.32508 nat = 0.46900 bit ; e^H = 1.38415 = 2^H = 1.38415
  D5 H(0.5 ; 0.25 ; 0.25) = 1.03972 = regroupé 1.03972
H(0,5 ; 0,5) = 0.693 ; H(0,9 ; 0,1) = 0.325
demande claire : H = 0.94045 ; 68% du maximum -> appeler un outil
demande ambiguë : H = 1.24878 ; 90% du maximum -> clarifier
Cas 1 : coût d'un appel direct : claire 1.20, ambiguë 2.40 AED ; par jour : toujours appeler 46800, règle 85 % 38700 AED
  bascules du coût d'erreur : claire 5.0, ambiguë 2.5 AED ; même max 0.5 : 0.50 et 0.89624 du maximum
Cas 2 : H = 1.875 bits ; questions : ordre probable 1.8750, ordre inverse 3.5625 ; uniforme 2.32193 bits
  abandon : 0.03695 contre 0.06930 ; candidats perdus évités 129.4/mois
Cas 3 : H = 1.29257, nombre effectif 3.642 sur 5 ; après transfert de 1.5 M : H = 1.48002, effectif 4.393
  transfert minimal 0.558 M AED ; surcoût 3 % : 45000 AED, au minimum 16738 AED
Cas 4 : H brut 1.33509 (0.96306 du maximum) ; entités 0.50040 (0.72193) ; intérieur 1.04335 ; regroupé 1.33509
  bascule part « Mahmoud » 0.2760 ; erreurs si automatique 60/mois ; mensualités 8500 <= 9000
Corrigé
  ex1 2.079 nats = 3 bits ; ex2 0.0 et 1.386 ; ex3 0.469 bit ; ex4 1.03972
  ex6 2.00869 bits, 2.05 questions ; ex7 1.5 bits ; ex8 effectif 4
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme calcule l'entropie d'une distribution, dans la base voulue, la compare au maximum ln n pour décider si l'agent doit demander une précision, et peut d'abord regrouper les issues équivalentes.

```text
ALGORITHME EntropieEtDécision
ENTRÉES : distribution p₁ … pₙ, base, seuil (par exemple 0,85),
          groupes d'issues équivalentes (facultatif)
SORTIE  : (H, décision)

  VÉRIFIER que les pᵢ sont ≥ 0 et somment à 1
  SI des groupes sont fournis ALORS remplacer P par les poids des groupes
  H ← 0
  POUR i DE 1 À n FAIRE
      SI pᵢ > 0 ALORS H ← H − pᵢ × log(pᵢ) dans la base choisie
  FIN POUR
  ratio ← H / log(n), dans la même base
  SI ratio > seuil ALORS décision ← « clarifier » SINON décision ← « appeler un outil »
  RETOURNER H, décision
```

**Complexité.** O(n) en temps, O(1) en mémoire, O(n) de plus pour le regroupement. Ignorer les pᵢ nuls applique la convention 0 × ln 0 = 0.

**Du squelette au code.** L'entropie est la fonction `H(P, base)` ; le ratio et la décision sont la boucle sur `claire` et `ambigue` de `main`. L'additivité est vérifiée sur la loi jointe `jointe`, le regroupement sur (0,5 ; 0,25 ; 0,25) et dans `entropie_groupee(groupes)`. Le ratio est aussi `ratio_max(P)`, le nombre effectif `nombre_effectif(P)`, et le nombre moyen de questions `questions_moyennes(probas)`. Les quatre cas sont `cas_1_public_routeur(claire, ambigue)`, `cas_2_rh_questions()`, `cas_3_btp_fournisseurs()` et `cas_4_banque_translitteration()`.
