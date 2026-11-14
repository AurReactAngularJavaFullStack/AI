# 14 — Score F1 : démonstrations

> Fiche : [14 — Score F1](<../../Images/04-Recherche/14_score_f1.md>) · Image : `14_score_f1.jpg` · Leçon : [Étape 50 — Précision, rappel, F1 et KL](<../../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
F_1 = \frac{2 \times P \times R}{P + R}
$$

P est la précision (fiche 12) et R le rappel (fiche 13). F1 les résume en un seul nombre, qui n'est élevé que si les deux le sont.

## Les symboles, un par un

$$
P
$$

La précision, VP/(VP + FP) : part des éléments renvoyés qui sont bons. Réel dans [0 ; 1], indéfini si rien n'est renvoyé. La leçon de l'étape 50 l'écrit Préc, parce qu'elle réserve P aux distributions de probabilité. Variable Python : `p`.

$$
R
$$

Le rappel, VP/(VP + FN) : part des éléments pertinents qui ont été trouvés. Réel dans [0 ; 1], indéfini s'il n'y avait rien à trouver. L'étape 50 l'écrit Rap. Variable Python : `r`.

$$
VP, \quad FP, \quad FN
$$

Vrais positifs (renvoyés et bons), faux positifs (renvoyés à tort, des fausses alertes) et faux négatifs (bons mais manqués, des oublis). Entiers ≥ 0. L'étape 50 les écrit TP, FP, FN. Variables Python : `vp`, `fp`, `fn`.

$$
F_1
$$

La moyenne harmonique de P et R. Réel dans [0 ; 1], indéfini seulement si VP = FP = FN = 0. Variable Python : la valeur renvoyée par `f1(p, r)` ou `f1_comptages(vp, fp, fn)`.

$$
\beta
$$

Le réglage du poids du rappel : β > 1 favorise le rappel, β < 1 la précision, β = 1 redonne F1. Réel > 0, sans unité. Variable Python : `beta`.

$$
F_\beta
$$

La moyenne harmonique pondérée de P et R, où un faux négatif coûte β² faux positifs. Réel dans [0 ; 1]. Variable Python : la valeur renvoyée par `f_beta(p, r, beta)` ou `f_beta_comptes(vp, fp, fn, beta)`.

## Le mécanisme, avant les preuves

La formule prend deux taux et les combine en passant par leurs inverses. L'inverse de la précision, 1/P = (VP + FP)/VP, est le nombre d'éléments renvoyés pour un bon élément : un « coût par succès » côté sortie. L'inverse du rappel, 1/R = (VP + FN)/VP, est le nombre de pertinents existants pour un pertinent trouvé : un coût par succès côté vérité. F1 fait la moyenne arithmétique de ces deux coûts, puis repasse à l'inverse : c'est la moyenne harmonique. Comme l'inverse d'un taux faible est très grand, un seul taux faible fait exploser la moyenne des inverses, et donc chuter F1 ; c'est voulu, puisqu'un système qui ne trouve rien ou qui renvoie tout ne doit pas recevoir une note moyenne. Le produit P × R au numérateur traduit la même idée : si l'un des deux vaut 0, F1 vaut 0. Le facteur 2 sert seulement à ce que F1 = P quand P = R. Les vrais négatifs n'apparaissent nulle part : F1 ne récompense pas un système d'avoir ignoré ce qui était à ignorer, ce qui le rend adapté aux événements rares. Une moyenne arithmétique (P + R)/2 ne conviendrait pas : elle donnerait 0,5 à un agent qui renvoie un seul bon élément sur cent attendus.

Petit film chiffré. Premier cas, P = 0,9 et R = 0,3 : les inverses valent 1,11111 et 3,33333 ; leur moyenne vaut 4,44444/2 = 2,22222 ; son inverse vaut 0,45. Deuxième cas, P = R = 0,5 : les inverses valent 2 et 2, la moyenne 2, l'inverse 0,5, la valeur commune. Troisième cas, P = 1 et R = 0,01 : les inverses valent 1 et 100, la moyenne 50,5, l'inverse 0,0198, alors que la moyenne arithmétique des taux aurait affiché 0,505. En Java, c'est comme juger un service à la fois sur son taux d'erreurs et sur sa couverture fonctionnelle : un service parfait sur 1 % des cas d'usage n'a pas « la moitié » de la note.

## Démonstration 1 — C'est la moyenne harmonique

**Ce qu'on démontre.** Pour P > 0 et R > 0 :

$$
\frac{2}{\dfrac{1}{P} + \dfrac{1}{R}} = \frac{2PR}{P + R}
$$

**L'idée.** La moyenne harmonique est l'inverse de la moyenne des inverses. Il suffit de réduire la somme des inverses au même dénominateur.

**La preuve, pas à pas.**

**Étape 1.** On réduit 1/P + 1/R au dénominateur commun PR, parce que 1/P = R/(PR) et 1/R = P/(PR) :

$$
\frac{1}{P} + \frac{1}{R} = \frac{R + P}{PR}
$$

**Étape 2.** On divise 2 par cette fraction, ce qui revient à multiplier par son inverse :

$$
\frac{2}{\dfrac{R + P}{PR}} = \frac{2PR}{P + R}
$$

∎

**Vérification chiffrée.** P = 0,9 et R = 0,3 : 1/0,9 + 1/0,3 ≈ 1,11111 + 3,33333 = 4,44444, et 2/4,44444 = 0,45 ; par la formule directe, 2 × 0,9 × 0,3/(0,9 + 0,3) = 0,54/1,2 = 0,45. Contre-exemple pour l'hypothèse P > 0 et R > 0 : avec R = 0, la moyenne des inverses n'existe pas (1/0), alors que la forme 2PR/(P + R) donne 0 dès que P > 0 ; c'est cette forme, prolongée, que le code utilise.

**Ce que la preuve révèle du mécanisme.** Le dénominateur P + R est la somme, le numérateur le produit : quand l'un des deux taux est petit, le produit est petit alors que la somme reste de l'ordre du plus grand taux. F1 se comporte alors comme deux fois le plus petit taux.

**Conséquence pour un agent.** Un tableau de bord qui affiche F1 doit aussi afficher P et R : un F1 de 0,45 ne dit pas lequel des deux est faible, et l'action corrective (réduire les fausses alertes ou les oublis) dépend de lui.

## Démonstration 2 — F1 avec les seuls comptages, et quand il est indéfini

**Ce qu'on démontre.** Pour VP > 0 :

$$
F_1 = \frac{2\,VP}{2\,VP + FP + FN}
$$

Cette forme prolonge F1 : elle vaut 0 quand VP = 0 et FP + FN > 0, et elle n'est indéfinie que si VP = FP = FN = 0. Les vrais négatifs n'y figurent pas.

**L'idée.** On remplace P et R par leurs comptages dans la moyenne des inverses ; VP se met en facteur et se simplifie.

**La preuve, pas à pas.**

**Étape 1.** On écrit les inverses avec les comptages, parce que P = VP/(VP + FP) et R = VP/(VP + FN) :

$$
\frac{1}{P} + \frac{1}{R} = \frac{VP + FP}{VP} + \frac{VP + FN}{VP} = \frac{2VP + FP + FN}{VP}
$$

**Étape 2.** On applique la démonstration 1 : F1 = 2/(1/P + 1/R), donc on multiplie 2 par l'inverse de la fraction précédente :

$$
F_1 = \frac{2\,VP}{2\,VP + FP + FN}
$$

**Étape 3.** Si VP = 0 et FP + FN > 0, la fraction vaut 0/(FP + FN) = 0, bien que la précision puisse être indéfinie (FP = 0). Si VP = FP = FN = 0, on obtient 0/0 : rien n'était à trouver et rien n'a été renvoyé, et la fonction renvoie None. ∎

**Vérification chiffrée.** VP = 40, FP = 10, FN = 20 : 80/(80 + 10 + 20) = 80/110 ≈ 0,72727, et par les taux, P = 0,8, R ≈ 0,66667, 2 × 0,8 × 0,66667/1,46667 ≈ 0,72727. Un agent muet, VP = FP = 0 et FN = 10 : précision indéfinie, mais F1 = 0/(0 + 0 + 10) = 0, le bon verdict. Ajouter 10 000 vrais négatifs ne change rien, puisque VN n'apparaît pas ; l'exactitude, elle, passerait à (40 + 10 000)/10 070 ≈ 0,99702.

**Ce que la preuve révèle du mécanisme.** FP et FN entrent au dénominateur avec le même poids 1 : F1 traite une fausse alerte et un oubli comme deux erreurs de même prix. C'est exactement ce que Fβ viendra corriger (démonstration 4).

**Conséquence pour un agent.** La forme en comptages est la référence dans le code : elle reste définie quand la précision ne l'est pas, et elle se calcule en flux avec trois compteurs.

## Démonstration 3 — F1 est coincé entre le minimum et la moyenne, et sous le double du minimum

**Ce qu'on démontre.** Pour P > 0 et R > 0 :

$$
\min(P, R) \le F_1 \le \frac{P + R}{2}
$$

avec égalité partout si et seulement si P = R ; et de plus F1 < 2 min(P, R).

**L'idée.** Une moyenne reste entre ses deux valeurs, et la moyenne harmonique est la plus « pessimiste » des moyennes usuelles : elle reste près de la plus petite valeur.

**La preuve, pas à pas.**

**Étape 1.** On suppose P ≤ R (sinon on échange les rôles, F1 étant symétrique). Alors P + R ≤ 2R, donc 2R/(P + R) ≥ 1, et :

$$
F_1 = P \times \frac{2R}{P + R} \ge P = \min(P, R)
$$

**Étape 2.** Pour la borne haute, on calcule la différence avec la moyenne arithmétique en réduisant au même dénominateur :

$$
\frac{P + R}{2} - \frac{2PR}{P + R} = \frac{(P + R)^2 - 4PR}{2(P + R)} = \frac{(P - R)^2}{2(P + R)} \ge 0
$$

parce qu'un carré est positif ; elle est nulle si et seulement si P = R.

**Étape 3.** Toujours avec P ≤ R : P + R > R, donc 2PR/(P + R) < 2PR/R = 2P = 2 min(P, R). ∎

**Vérification chiffrée.** P = 0,6 et R = 0,8 : F1 = 0,96/1,4 ≈ 0,68571, entre 0,6 et (0,6 + 0,8)/2 = 0,7, et sous 2 × 0,6 = 1,2. P = 1 et R = 0,01 : F1 ≈ 0,0198, entre 0,01 et 0,505, et sous 2 × 0,01 = 0,02 : la borne « double du minimum » est presque atteinte. P = R = 0,5 : F1 = 0,5, égalité.

**Ce que la preuve révèle du mécanisme.** L'écart entre F1 et la moyenne arithmétique vaut (P − R)²/(2(P + R)) : il grandit avec le carré du déséquilibre. Un système équilibré ne perd rien, un système déséquilibré est puni fortement.

**Conséquence pour un agent.** Pour monter F1, on améliore d'abord le taux le plus faible : F1 ne dépassera jamais le double de ce taux. Un objectif « F1 ≥ 0,8 » impose donc P et R tous deux ≥ 0,4 au minimum, et en pratique bien plus.

## Démonstration 4 — Pondérer précision et rappel : F-bêta, où un oubli coûte β² fausses alertes

**Ce qu'on démontre.** Avec les poids 1/(1 + β²) sur 1/P et β²/(1 + β²) sur 1/R, la moyenne harmonique pondérée vaut

$$
F_\beta = \frac{(1 + \beta^2)\, P\, R}{\beta^2 P + R} = \frac{(1 + \beta^2)\, VP}{(1 + \beta^2)\, VP + \beta^2\, FN + FP}
$$

Dans la moyenne, le rappel pèse β² fois plus que la précision ; dans les comptages, un faux négatif coûte β² faux positifs. Cela corrige l'ancienne phrase de ce fichier, « β = 2 compte le rappel deux fois plus » : avec β = 2, le poids est 4.

**L'idée.** On garde le principe de la moyenne des inverses, mais avec des poids inégaux ; au dénominateur, β² se retrouve devant P parce qu'il multipliait 1/R.

**La preuve, pas à pas.**

**Étape 1.** On écrit la moyenne pondérée des inverses et l'on réduit au dénominateur commun (1 + β²)PR :

$$
\frac{1}{F_\beta} = \frac{1}{1 + \beta^2} \cdot \frac{1}{P} + \frac{\beta^2}{1 + \beta^2} \cdot \frac{1}{R} = \frac{R + \beta^2 P}{(1 + \beta^2)\, P R}
$$

**Étape 2.** On retourne la fraction, ce qui donne la forme en taux.

**Étape 3.** On remplace 1/P = (VP + FP)/VP et 1/R = (VP + FN)/VP dans la première ligne et l'on multiplie haut et bas par (1 + β²) VP :

$$
\frac{1}{F_\beta} = \frac{(VP + FP) + \beta^2 (VP + FN)}{(1 + \beta^2)\, VP} = \frac{(1 + \beta^2)\, VP + \beta^2 FN + FP}{(1 + \beta^2)\, VP}
$$

Le retournement donne la forme en comptages : FN y est multiplié par β², FP par 1. ∎

**Vérification chiffrée.** VP = 40, FP = 10, FN = 20, donc P = 0,8 et R ≈ 0,66667. Pour β = 2 : 5 × 40/(5 × 40 + 4 × 20 + 10) = 200/290 ≈ 0,68966 ; par les taux, 5 × 0,8 × 0,66667/(4 × 0,8 + 0,66667) = 2,66667/3,86667 ≈ 0,68966. Pour β = 0,5 : 1,25 × 40/(50 + 0,25 × 20 + 10) = 50/65 ≈ 0,76923. Pour β = 1, on retrouve 0,72727. Contre-exemple d'écriture : placer β² devant R au dénominateur, (1 + β²)PR/(P + β²R), donne pour β = 2 la valeur 0,76923, c'est-à-dire F₀,₅ : la formule favorise alors la précision au lieu du rappel (exercice 7).

**Ce que la preuve révèle du mécanisme.** β² est un taux de change entre erreurs : « un oubli vaut β² fausses alertes ». Quand β → +∞, Fβ → R ; quand β → 0, Fβ → P (exercice 5).

**Conséquence pour un agent.** On ne choisit pas β au hasard : on le dérive du rapport des coûts métier, β² = coût d'un faux négatif / coût d'un faux positif (cas 2 et 3). Un garde-fou anti-fraude prend β > 1, une approbation automatique β < 1.

## Démonstration 5 — Sensibilité : de combien bouge F1 quand P ou R gagne un point

**Ce qu'on démontre.** Pour P > 0 et R > 0, les dérivées partielles de F1 valent

$$
\frac{\partial F_1}{\partial P} = \frac{2R^2}{(P + R)^2}, \qquad \frac{\partial F_1}{\partial R} = \frac{2P^2}{(P + R)^2}
$$

donc le rapport des deux effets vaut (P/R)² : gagner un point sur le taux le plus faible rapporte (grand/petit)² fois plus que sur le plus fort.

**L'idée.** F1 est dominé par le plus petit taux (démonstration 3) ; il est donc logique qu'il réagisse surtout à lui.

**La preuve, pas à pas.**

**Étape 1.** On dérive 2PR/(P + R) par rapport à P avec la règle du quotient, R étant constant : la dérivée du numérateur vaut 2R, celle du dénominateur 1 :

$$
\frac{\partial F_1}{\partial P} = \frac{2R\,(P + R) - 2PR}{(P + R)^2} = \frac{2R^2}{(P + R)^2}
$$

**Étape 2.** Par symétrie de la formule en P et R, la dérivée par rapport à R vaut 2P²/(P + R)².

**Étape 3.** On fait le rapport : les dénominateurs se simplifient, il reste 2P²/(2R²) = (P/R)². ∎

**Vérification chiffrée.** P = 0,9, R = 0,3 : ∂F1/∂P = 2 × 0,09/1,44 = 0,125 et ∂F1/∂R = 2 × 0,81/1,44 = 1,125, neuf fois plus, et (0,9/0,3)² = 9. En différences finies : F1(0,9 ; 0,31) = 0,558/1,21 ≈ 0,46116, soit un gain de 0,01116 ; F1(0,91 ; 0,3) = 0,546/1,21 ≈ 0,45124, soit un gain de 0,00124. Un point de rappel rapporte environ 0,0112, un point de précision 0,0012.

**Ce que la preuve révèle du mécanisme.** Quand P = R, les deux dérivées sont égales à 1/2 : chaque taux compte pour moitié. Plus le déséquilibre est grand, plus F1 devient insensible au taux déjà bon.

**Conséquence pour un agent.** Pour prioriser un chantier d'amélioration, on calcule ces deux dérivées : elles disent quel taux améliorer en premier pour le plus grand gain de F1 par effort.

## Exemple simple, à la main

Un système très précis qui trouve peu de choses : P = 0,9 et R = 0,3. On calcule d'abord le produit 0,9 × 0,3 = 0,27, puis le numérateur 2 × 0,27 = 0,54, puis la somme 0,9 + 0,3 = 1,2 :

$$
F_1 = \frac{2 \times 0{,}9 \times 0{,}3}{0{,}9 + 0{,}3} = \frac{0{,}54}{1{,}2} = 0{,}45
$$

La moyenne arithmétique aurait affiché (0,9 + 0,3)/2 = 0,6 : elle masque le rappel trop faible. Le même calcul par les inverses :

| Étape | Calcul | Valeur |
| --- | --- | --- |
| inverse de P | 1/0,9 | 1,11111 |
| inverse de R | 1/0,3 | 3,33333 |
| somme des inverses | 1,11111 + 3,33333 | 4,44444 |
| F1 | 2/4,44444 | 0,45 |
| encadrement | min 0,3 ; moyenne 0,6 ; double du min 0,6 | 0,3 ≤ 0,45 ≤ 0,6 |

## Cas d'usage complexes, démontrés

### Cas 1 — [BANQUE] Une banque de détail de Dubaï : évaluer les appels d'outils de l'agent d'ouverture de compte

**Contexte.** Une banque de détail de Dubaï déploie un agent qui prépare l'ouverture de compte d'un client : il doit appeler, selon le dossier, des outils comme « vérifier le format de l'Emirates ID » (15 chiffres commençant par 784), « contrôler l'IBAN » (23 caractères, clé mod 97 = 1), « filtrer le nom sur la liste de surveillance » ou « calculer le ratio d'endettement ». Sur un jeu de dossiers rejoués, 60 appels d'outils étaient attendus. La question : la version candidate de l'agent peut-elle passer en production ? Les volumes et l'objectif sont illustratifs.

**Données.**

- appels attendus : 60 ; appels faits par l'agent : 50 ;
- appels corrects : VP = 40 ; appels inutiles ou faux : FP = 10 ; appels oubliés : FN = 20 ;
- dossiers où aucun outil n'était requis, et où l'agent n'en a appelé aucun : 10 000 (vrais négatifs) ;
- règle de mise en production : F2 ≥ 0,85, parce qu'un contrôle oublié est plus grave qu'un appel inutile.

**Calcul pas à pas.**

**Étape 1.** Précision et rappel :

$$
P = \frac{40}{50} = 0{,}8, \qquad R = \frac{40}{60} \approx 0{,}66667
$$

**Étape 2.** F1 en comptages :

$$
F_1 = \frac{2 \times 40}{2 \times 40 + 10 + 20} = \frac{80}{110} \approx 0{,}72727
$$

**Étape 3.** F2 et F₀,₅ (démonstration 4) :

$$
F_2 = \frac{5 \times 40}{5 \times 40 + 4 \times 20 + 10} = \frac{200}{290} \approx 0{,}68966, \qquad F_{0{,}5} = \frac{50}{50 + 5 + 10} \approx 0{,}76923
$$

**Décision de l'agent.** F2 vaut 0,68966, sous 0,85 : la version candidate est bloquée. F2 est plus bas que F1 parce qu'il pèse le rappel faible ; F₀,₅ serait plus haut parce qu'il pèse la bonne précision, mais ce n'est pas le risque de la banque.

**Contre-calcul.** La moyenne arithmétique (0,8 + 0,66667)/2 ≈ 0,73333 aurait paru acceptable. L'exactitude, qui compte les 10 000 vrais négatifs, vaudrait (40 + 10 000)/(40 + 10 + 20 + 10 000) = 10 040/10 070 ≈ 0,99702 : un agent qui oublie un contrôle sur trois aurait une note quasi parfaite. F1 et F2 ignorent les vrais négatifs, et c'est ce qui les rend honnêtes ici.

**Sensibilité.** Si l'on corrige x oublis (ils deviennent des appels corrects, FP restant à 10), F2 = 5(40 + x)/(5(40 + x) + 4(20 − x) + 10) = (200 + 5x)/(290 + x). L'objectif 0,85 exige 200 + 5x ≥ 246,5 + 0,85x, soit x ≥ 11,205 : il faut corriger 12 oublis. À x = 11, F2 ≈ 0,84718 ; à x = 12, F2 ≈ 0,86093. La valeur de bascule est 12 oublis corrigés sur 20.

**En production.** On suit F2 par outil sur le jeu rejoué à chaque version, avec un blocage sous 0,85, et un rappel de 1 exigé sur le filtrage de la liste de surveillance. Le format de l'Emirates ID et la clé mod 97 de l'IBAN sont des faits du cours ; les contrôles KYC exigés par la CBUAE pour chaque produit sont à confirmer avec le texte en vigueur.

### Cas 2 — [IMMO] Une agence à Dubaï : extraire les champs des contrats Ejari

**Contexte.** Une agence qui gère des locations à Dubaï fait extraire par un agent les champs des contrats de bail enregistrés dans Ejari : loyer annuel, dates de début et de fin, numéro de contrat, nombre de chèques, dépôt de garantie, etc. Sur 200 contrats de test à 8 champs, 1 600 champs étaient attendus. Deux modèles sont comparés. Un champ faux (un loyer erroné dans un rappel au locataire) coûte bien plus qu'un champ manquant, qu'un employé saisit à la main. Les coûts sont illustratifs.

**Données.**

- champs attendus : 1 600 ;
- modèle A : 1 500 champs extraits, dont 1 380 justes (VP = 1 380, FP = 120, FN = 220) ;
- modèle B : 1 300 champs extraits, dont 1 274 justes (VP = 1 274, FP = 26, FN = 326) ;
- coût d'un champ faux : 300 AED ; coût d'un champ manquant : 40 AED.

**Calcul pas à pas.**

**Étape 1.** Précisions et rappels : A, P = 1 380/1 500 = 0,92 et R = 1 380/1 600 = 0,8625 ; B, P = 1 274/1 300 = 0,98 et R = 1 274/1 600 = 0,79625.

**Étape 2.** F1 en comptages :

$$
F_1(A) = \frac{2\,760}{2\,760 + 120 + 220} = \frac{2\,760}{3\,100} \approx 0{,}89032, \qquad F_1(B) = \frac{2\,548}{2\,548 + 26 + 326} = \frac{2\,548}{2\,900} \approx 0{,}87862
$$

**Étape 3.** Le β qui reflète les coûts (démonstration 4) : un faux négatif doit valoir β² faux positifs, donc β² = 40/300 ≈ 0,13333 et β ≈ 0,36515. On calcule aussi F₀,₅, plus lisible :

$$
F_{0{,}5}(A) = \frac{1{,}25 \times 1\,380}{1{,}25 \times 1\,380 + 0{,}25 \times 220 + 120} = \frac{1\,725}{1\,900} \approx 0{,}90789, \qquad F_{0{,}5}(B) = \frac{1\,592{,}5}{1\,700} \approx 0{,}93676
$$

**Étape 4.** Les coûts directs : A, 120 × 300 + 220 × 40 = 36 000 + 8 800 = 44 800 AED ; B, 26 × 300 + 326 × 40 = 7 800 + 13 040 = 20 840 AED.

**Décision de l'agent.** L'agence retient B : F₀,₅ le préfère (0,93676 contre 0,90789) et il coûte 23 960 AED de moins sur les 200 contrats.

**Contre-calcul.** F1 aurait choisi A (0,89032 contre 0,87862), parce qu'il traite un loyer faux et un champ vide comme deux erreurs de même prix. Sur 200 contrats, ce choix coûterait 44 800 − 20 840 = 23 960 AED de plus, et chaque loyer faux envoyé à un locataire abîme la relation client.

**Sensibilité.** Avec a le coût d'un champ faux et b celui d'un champ manquant, les deux modèles coûtent autant quand 120a + 220b = 26a + 326b, soit 94a = 106b, a/b ≈ 1,12766. Si un champ faux coûtait moins de 1,128 fois un champ manquant, A redeviendrait meilleur ; avec le rapport actuel de 7,5, B l'emporte largement.

**En production.** On suit la précision par champ sur un échantillon audité chaque mois, avec une alerte si la précision du loyer passe sous 0,99, et le taux de champs laissés à la saisie manuelle. L'enregistrement des baux dans Ejari est un fait du cours ; l'usage des champs extraits dans un document envoyé au locataire est à confirmer avec les règles de la RERA en vigueur.

### Cas 3 — [BTP] Un groupe de construction : repérer les lignes de facture non conformes

**Contexte.** Un groupe de construction sur de grands chantiers à Dubaï fait contrôler par un agent les lignes des factures de ses sous-traitants : TVA différente de 5 %, retenue de garantie non déduite, quantité supérieure au bon de livraison. Par exemple, une ligne de 100 000 AED hors taxes facturée avec 15 % de TVA au lieu de 5 % surfacture 10 000 AED. Sur un mois de 2 000 lignes, l'audit a trouvé 80 lignes non conformes. Deux seuils de l'agent sont comparés ; les volumes et coûts sont illustratifs.

**Données.**

- lignes du mois : 2 000 ; lignes non conformes : 80 ;
- seuil S1 : 100 lignes signalées, dont 64 vraiment non conformes (VP = 64, FP = 36, FN = 16) ;
- seuil S2 : 60 lignes signalées, dont 51 non conformes (VP = 51, FP = 9, FN = 29) ;
- coût moyen d'une ligne non conforme payée : 4 000 AED ; coût de vérification d'une ligne signalée : 50 AED.

**Calcul pas à pas.**

**Étape 1.** Taux : S1, P = 64/100 = 0,64 et R = 64/80 = 0,8 ; S2, P = 51/60 = 0,85 et R = 51/80 = 0,6375.

**Étape 2.** F1 en comptages :

$$
F_1(S1) = \frac{128}{128 + 36 + 16} = \frac{128}{180} \approx 0{,}71111, \qquad F_1(S2) = \frac{102}{102 + 9 + 29} = \frac{102}{140} \approx 0{,}72857
$$

**Étape 3.** F2, puisque l'oubli coûte bien plus que la vérification :

$$
F_2(S1) = \frac{320}{320 + 64 + 36} = \frac{320}{420} \approx 0{,}7619, \qquad F_2(S2) = \frac{255}{255 + 116 + 9} = \frac{255}{380} \approx 0{,}67105
$$

**Étape 4.** Les coûts mensuels : S1, 16 × 4 000 + 100 × 50 = 64 000 + 5 000 = 69 000 AED ; S2, 29 × 4 000 + 60 × 50 = 116 000 + 3 000 = 119 000 AED.

**Décision de l'agent.** Le groupe retient S1 : F2 le préfère nettement et il coûte 50 000 AED de moins par mois.

**Contre-calcul.** F1 préfère S2 de peu (0,72857 contre 0,71111) : le choisir coûterait 50 000 AED par mois. Le rapport des coûts, 4 000/50 = 80, correspondrait même à β = √80 ≈ 8,944 : F2 est déjà une pondération prudente.

**Sensibilité.** Avec m le coût d'une ligne non conforme payée, les deux seuils coûtent autant quand 16m + 5 000 = 29m + 3 000, soit 13m = 2 000 et m ≈ 153,85 AED. Au-dessus d'environ 154 AED par ligne manquée, S1 est meilleur ; en dessous, S2 l'emporte (exercice 6).

**En production.** On suit chaque mois le rappel mesuré sur un échantillon de factures auditées à l'aveugle et le montant récupéré avant paiement. La TVA de 5 % est un fait du cours ; les taux de retenue de garantie sont propres à chaque contrat, et le traitement fiscal d'une facture corrigée est à confirmer avec le texte en vigueur.

### Cas 4 — [PUBLIC] Une entité de services publics : le routage bilingue, classe par classe

**Contexte.** Une entité de services publics en ligne, accessible par UAE Pass, reçoit des demandes en arabe et en anglais et les route vers trois services : état civil (EC), permis (PE), réclamations (RE). Sur un échantillon de 1 000 demandes étiquetées, l'équipe calcule un F1 par service (chaque service contre les deux autres). La règle de mise en production : F1 macro ≥ 0,8 **et** F1 ≥ 0,7 pour chaque service. Les volumes sont illustratifs.

**Données.** Matrice de confusion (lignes : service réel ; colonnes : service choisi par l'agent).

| Service réel ↓ / routé vers → | EC | PE | RE | Total |
| --- | --- | --- | --- | --- |
| EC | 470 | 20 | 10 | 500 |
| PE | 30 | 360 | 10 | 400 |
| RE | 20 | 30 | 50 | 100 |

**Calcul pas à pas.**

**Étape 1.** Les comptages par service : pour EC, VP = 470, FP = 30 + 20 = 50 (colonne), FN = 20 + 10 = 30 (ligne) ; pour PE, VP = 360, FP = 20 + 30 = 50, FN = 30 + 10 = 40 ; pour RE, VP = 50, FP = 10 + 10 = 20, FN = 20 + 30 = 50.

**Étape 2.** Les F1 par service :

$$
F_1(EC) = \frac{940}{1\,020} \approx 0{,}92157, \qquad F_1(PE) = \frac{720}{810} \approx 0{,}88889, \qquad F_1(RE) = \frac{100}{170} \approx 0{,}58824
$$

**Étape 3.** Les moyennes : macro = (0,92157 + 0,88889 + 0,58824)/3 ≈ 0,79956 (calculé sur les valeurs exactes) ; micro, en additionnant les comptages (VP = 880, FP = 120, FN = 120), 1 760/2 000 = 0,88.

**Décision de l'agent.** La règle échoue deux fois : macro 0,79956 < 0,8 et F1(RE) = 0,58824 < 0,7. L'agent ne route pas seul les réclamations : sous un score de confiance donné, une réclamation part vers un tri humain, et l'équipe réentraîne le routeur sur des réclamations en arabe.

**Contre-calcul.** Le F1 micro (0,88), qui égale ici l'exactitude 880/1 000, paraît excellent ; il cache que la moitié des réclamations est mal routée (R = 50/100 = 0,5, précision 50/70 ≈ 0,71429). Une réclamation envoyée à l'état civil attend dans la mauvaise file, ce qui est le pire résultat pour un service public.

**Sensibilité.** Si x réclamations mal routées sont corrigées (FP restant à 20), F1(RE) = 2(50 + x)/(2(50 + x) + 20 + 50 − x) = (100 + 2x)/(170 + x). L'objectif 0,7 exige 100 + 2x ≥ 119 + 0,7x, soit x ≥ 14,6 : il faut 15 réclamations de plus bien routées. À x = 14, F1(RE) ≈ 0,69565 ; à x = 15, ≈ 0,7027.

**En production.** On suit le F1 par service **et par langue**, avec une alerte si un F1 passe sous 0,7 ou si l'écart entre l'arabe et l'anglais dépasse 0,1. Les demandes contiennent des données personnelles : leur traitement relève de la PDPL hors zones franches financières, et la durée de conservation de l'échantillon étiqueté est à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Calculer F1 pour P = R = 0,5.

**Exercice 2.** Calculer F1 pour P = 1 et R = 0,01. Comparer avec la moyenne arithmétique.

**Exercice 3.** VP = 30, FP = 10, FN = 30. Calculer F1 avec la formule des comptages.

**Exercice 4.** Calculer F1 pour P = 0,6 et R = 0,8, puis vérifier l'encadrement de la démonstration 3.

**Exercice 5.** Démontrer que Fβ tend vers R quand β → +∞.

**Exercice 6 (cas modifié).** Dans le cas 3, le coût moyen d'une ligne non conforme payée n'est plus que de 100 AED. Recalculer les coûts de S1 et S2 et donner la décision.

**Exercice 7 (trouver l'erreur).** Un collègue code F2 ainsi : `(1 + b2) * p * r / (p + b2 * r)`, avec `b2 = 4`. Calculer ce que renvoie sa formule pour le cas 1 (P = 0,8 et R ≈ 0,66667), et expliquer l'erreur.

**Exercice 8 (redémontrer de mémoire).** Redémontrer que min(P, R) ≤ F1 ≤ (P + R)/2, et dire quand il y a égalité.

## Corrigé

**Exercice 1.** 2 × 0,5 × 0,5/(0,5 + 0,5) = 0,5/1 = 0,5 : quand P = R, F1 vaut leur valeur commune (démonstration 3, cas d'égalité).

**Exercice 2.** Numérateur 2 × 1 × 0,01 = 0,02, dénominateur 1,01, donc F1 ≈ 0,0198, contre (1 + 0,01)/2 = 0,505 en moyenne arithmétique. F1 reste sous 2 × 0,01 = 0,02, le double du minimum.

**Exercice 3.** 2 × 30 = 60, puis 60/(60 + 10 + 30) = 60/100 = 0,6. Vérification par les taux : P = 30/40 = 0,75, R = 30/60 = 0,5, 2 × 0,75 × 0,5/1,25 = 0,75/1,25 = 0,6.

**Exercice 4.** 2 × 0,6 × 0,8 = 0,96 et 0,6 + 0,8 = 1,4, donc F1 = 0,96/1,4 ≈ 0,68571. L'encadrement tient : 0,6 ≤ 0,68571 ≤ 0,7. L'écart à la moyenne vaut (0,6 − 0,8)²/(2 × 1,4) = 0,04/2,8 ≈ 0,01429, et 0,7 − 0,01429 = 0,68571.

**Exercice 5.** On divise le numérateur et le dénominateur de (1 + β²)PR/(β²P + R) par β² : (1/β² + 1) PR/(P + R/β²). Quand β → +∞, 1/β² → 0, donc l'expression tend vers PR/P = R.

**Exercice 6.** S1 : 16 × 100 + 100 × 50 = 1 600 + 5 000 = 6 600 AED. S2 : 29 × 100 + 60 × 50 = 2 900 + 3 000 = 5 900 AED. Comme 100 AED est sous la valeur de bascule d'environ 154 AED, S2 devient le moins cher : on le retient, et le bon réglage de β baisse en conséquence.

**Exercice 7.** Sa formule met β² devant R au dénominateur : 5 × 0,8 × 0,66667/(0,8 + 4 × 0,66667) = 2,66667/3,46667 ≈ 0,76923. C'est F₀,₅, pas F2 (0,68966) : la formule favorise la précision au lieu du rappel. Dans la vraie formule, β² multiplie P au dénominateur, parce qu'il pondérait 1/R dans la moyenne des inverses (démonstration 4).

**Exercice 8.** On suppose P ≤ R. Comme P + R ≤ 2R, on a F1 = P × 2R/(P + R) ≥ P = min(P, R). Puis (P + R)/2 − 2PR/(P + R) = ((P + R)² − 4PR)/(2(P + R)) = (P − R)²/(2(P + R)) ≥ 0. Il y a égalité dans les deux inégalités si et seulement si P = R.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`precision(vp, fp)`** — Cette fonction se comporte comme un contrôleur qui inspecte le panier de ce que l'agent a rapporté : elle reçoit le nombre de vrais positifs `vp` et de faux positifs `fp`, refuse d'emblée les compteurs négatifs en levant une `ValueError`, puis divise les bonnes trouvailles par tout ce qui a été renvoyé, VP / (VP + FP). Quand le panier est vide, parce que l'agent n'a rien renvoyé du tout, elle ne fabrique pas un faux zéro et renvoie `None`, ce qui permet à `main` de vérifier que l'agent muet a une précision indéfinie ; sinon elle renvoie le taux, par exemple 0,8 pour 40 appels justes sur 50 dans le cas bancaire.

**`rappel(vp, fn)`** — Sa jumelle se tient de l'autre côté du comptoir, celui de tout ce qu'il fallait trouver : elle reçoit les vrais positifs `vp` et les faux négatifs `fn`, lève une `ValueError` si l'un des deux est négatif, puis calcule la part des cibles réellement atteintes, VP / (VP + FN). S'il n'y avait rien à trouver, la question n'a pas de sens et elle renvoie `None` ; sinon elle renvoie le rappel, environ 0,66667 pour 40 appels d'outils trouvés sur 60 attendus, ou 0,8 pour les 64 lignes non conformes repérées sur 80 par le seuil S1 du cas de construction.

**`f_beta(p, r, beta)`** — Voici le juge qui pèse précision et rappel sur une balance dont on règle le contrepoids : il reçoit une précision `p`, un rappel `r` et un poids `beta`, qui vaut 1 par défaut, refuse par une `ValueError` tout β nul ou négatif, renvoie `None` si l'un des deux taux est indéfini et 0.0 si leur somme est nulle, pour éviter la division par zéro. Dans le cas général, il calcule β², puis (1 + β²) P R / (β² P + R), en plaçant bien β² devant la précision au dénominateur, ce qui donne plus de poids au rappel quand β dépasse 1 ; il renvoie ainsi 0,68966 pour F2 et 0,76923 pour F₀,₅ avec P = 0,8 et R ≈ 0,66667.

**`f1(p, r)`** — Cette petite fonction n'est qu'un raccourci, comme un guichet qui ne propose qu'un seul tarif : elle reçoit une précision `p` et un rappel `r`, et confie tout le travail à `f_beta` avec β = 1, ce qui revient à la moyenne harmonique 2PR / (P + R). Elle renvoie donc le F1, ou `None` si un taux manque ; `main` s'en sert à chaque démonstration, par exemple pour retrouver 0,45 avec P = 0,9 et R = 0,3, là où la moyenne arithmétique aurait affiché 0,6, et pour montrer que F1(1 ; 0,01) ≈ 0,0198 reste sous le double du minimum.

**`f_beta_comptes(vp, fp, fn, beta)`** — Cette fonction fait le même travail que `f_beta`, mais à la manière d'un comptable qui préfère les pièces brutes aux pourcentages : elle reçoit directement les trois compteurs VP, FP et FN et le poids `beta`, lève une `ValueError` si β n'est pas strictement positif, puis forme le dénominateur (1 + β²) VP + β² FN + FP. Si ce dénominateur est nul, c'est qu'il n'y avait rien à trouver et rien de renvoyé, et elle renvoie `None` ; sinon elle renvoie (1 + β²) VP divisé par ce dénominateur, soit 200/290 ≈ 0,68966 pour F2 dans le cas bancaire, sans jamais avoir besoin des vrais négatifs.

**`f1_comptages(vp, fp, fn)`** — Raccourci de la précédente pour β = 1, cette fonction reçoit les trois compteurs et appelle `f_beta_comptes` avec un poids égal à 1, ce qui revient à la formule 2 VP / (2 VP + FP + FN). Elle renvoie 80/110 ≈ 0,72727 pour 40 appels justes, 10 inutiles et 20 oubliés, 0.0 pour l'agent muet qui n'a rien renvoyé face à 10 cibles, et `None` lorsque les trois compteurs sont nuls ; c'est elle qui calcule le F1 de chaque service dans le cas 4, puis le F1 micro à partir des comptages additionnés.

**`derivees(p, r)`** — Cette fonction joue le rôle d'un ingénieur qui demande de combien bouge l'aiguille quand on tourne chacun des deux boutons : elle reçoit une précision `p` et un rappel `r`, et renvoie le couple des dérivées partielles de F1, 2R² / (P + R)² par rapport à P et 2P² / (P + R)² par rapport à R. Elle ne lève rien elle-même et suppose P + R non nul ; `main` l'appelle en P = 0,9 et R = 0,3 pour obtenir 0,125 et 1,125, soit un rapport de 9, ce qui montre qu'un point de rappel vaut ici neuf points de précision, et vérifie qu'en P = R = 0,5 les deux dérivées valent 0,5.

**`cas_1_banque_outils()`** — Cette fonction rejoue l'examen de passage d'un agent bancaire d'ouverture de compte, comme un inspecteur qui relit le carnet des appels d'outils : elle ne reçoit rien, fixe VP = 40, FP = 10, FN = 20 et 10 000 vrais négatifs, puis calcule précision, rappel, F1, F2, F₀,₅, la moyenne arithmétique 0,73333 et l'exactitude trompeuse 0,99702. Elle cherche ensuite, en essayant x = 0, 1, 2 et ainsi de suite, le premier nombre d'oublis à corriger pour que F2 atteigne 0,85, soit 12, F2 passant de 0,84718 à 0,86093 entre 11 et 12 corrections, imprime deux lignes et renvoie le dictionnaire des résultats, dont la décision « bloquée » puisque F2 ≈ 0,68966 reste sous 0,85.

**`cas_2_immo_ejari()`** — Ici, la fonction arbitre un concours entre deux extracteurs de champs de baux, comme un chef d'agence qui compare deux stagiaires : elle ne reçoit rien, part des comptages A (1 380, 120, 220) et B (1 274, 26, 326), et calcule pour chacun la précision, le rappel, le F1, le F₀,₅ et le coût, à 300 AED par champ faux et 40 AED par champ manquant. Elle en déduit β² = 40/300 ≈ 0,13333, β ≈ 0,36515 et le rapport de bascule (326 − 220)/(120 − 26) ≈ 1,12766, choisit le modèle au coût minimal, B avec 20 840 AED contre 44 800 AED pour A, imprime le tout et renvoie un dictionnaire avec ces résultats et le choix.

**`cas_3_btp_factures()`** — Cette fonction joue le contrôleur de factures d'un groupe de construction qui hésite entre deux réglages de son agent : sans paramètre, elle prend les comptages S1 (64, 36, 16) et S2 (51, 9, 29) sur 80 lignes non conformes, et calcule pour chacun précision, rappel, F1, F2 et coût mensuel, 4 000 AED par ligne manquée plus 50 AED par ligne signalée. Elle calcule le coût de bascule (60 × 50 − 100 × 50)/(16 − 29) ≈ 153,85 AED et le β équivalent √(4 000/50) ≈ 8,944, retient le seuil le moins cher, S1 à 69 000 AED contre 119 000 AED, imprime deux lignes et renvoie un dictionnaire avec les résultats, la bascule, le choix et ce β équivalent.

**`cas_4_public_routage()`** — Cette fonction se tient devant la matrice de confusion d'un routeur bilingue comme un aiguilleur devant son tableau des voies : sans paramètre, elle lit la matrice 3 × 3 des services EC, PE et RE, et pour chaque service prend la case diagonale comme VP, le reste de sa colonne comme FP et le reste de sa ligne comme FN. Elle calcule les F1 par service, 0,92157, 0,88889 et 0,58824, leur moyenne macro 0,79956 et le F1 micro 0,88 sur les comptages additionnés (880, 120, 120), applique la règle « macro ≥ 0,8 et chaque F1 ≥ 0,7 », qui échoue, trouve qu'il faut 15 réclamations de plus bien routées, imprime la décision « tri humain » et renvoie un dictionnaire de tous ces éléments.

**`main()`** — C'est le chef d'orchestre qui fait jouer toutes les démonstrations de la fiche dans l'ordre : il vérifie d'abord que F1 est bien la moyenne harmonique (0,45 pour P = 0,9 et R = 0,3), puis la forme en comptages et ses cas indéfinis, l'encadrement min(P, R) ≤ F1 ≤ (P + R)/2 sur une grille de valeurs, l'accord entre `f_beta` et `f_beta_comptes` et les limites de F-bêta quand β devient très grand ou très petit, enfin la sensibilité avec `derivees`. Il appelle ensuite les quatre cas, confronte chaque nombre renvoyé par un `assert` aux valeurs du texte, recalcule les exercices du corrigé, vérifie que β = 0 est bien refusé par une `ValueError`, et n'imprime le message final de réussite que si tout concorde.

```python
"""Démonstration 14 — F1 : moyenne harmonique, comptages, encadrement, F-bêta, sensibilité, quatre cas aux Émirats."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def precision(vp: int, fp: int) -> float | None:
    """VP / (VP + FP) ; None si rien n'est renvoyé."""
    if vp < 0 or fp < 0:
        raise ValueError("compteurs négatifs")
    return None if vp + fp == 0 else vp / (vp + fp)


def rappel(vp: int, fn: int) -> float | None:
    """VP / (VP + FN) ; None s'il n'y avait rien à trouver."""
    if vp < 0 or fn < 0:
        raise ValueError("compteurs négatifs")
    return None if vp + fn == 0 else vp / (vp + fn)


def f_beta(p: float | None, r: float | None, beta: float = 1.0) -> float | None:
    """(1 + β²) P R / (β² P + R) : β² multiplie la précision au dénominateur."""
    if beta <= 0:
        raise ValueError("beta doit être > 0")
    if p is None or r is None:
        return None
    if p + r == 0:
        return 0.0
    b2 = beta * beta
    return (1 + b2) * p * r / (b2 * p + r)


def f1(p: float | None, r: float | None) -> float | None:
    return f_beta(p, r, 1.0)


def f_beta_comptes(vp: int, fp: int, fn: int, beta: float = 1.0) -> float | None:
    """(1 + β²) VP / ((1 + β²) VP + β² FN + FP) ; None si VP = FP = FN = 0."""
    if beta <= 0:
        raise ValueError("beta doit être > 0")
    b2 = beta * beta
    den = (1 + b2) * vp + b2 * fn + fp
    return None if den == 0 else (1 + b2) * vp / den


def f1_comptages(vp: int, fp: int, fn: int) -> float | None:
    return f_beta_comptes(vp, fp, fn, 1.0)


def derivees(p: float, r: float) -> tuple[float, float]:
    """(∂F1/∂P, ∂F1/∂R) = (2R² / (P + R)², 2P² / (P + R)²)."""
    return 2 * r * r / (p + r) ** 2, 2 * p * p / (p + r) ** 2


def cas_1_banque_outils() -> dict:
    """[BANQUE] 60 appels attendus, 50 faits : VP 40, FP 10, FN 20 ; objectif F2 >= 0,85."""
    vp, fp, fn, vn = 40, 10, 20, 10_000
    p, r = precision(vp, fp), rappel(vp, fn)
    res = {"p": p, "r": r, "f1": f1_comptages(vp, fp, fn), "f2": f_beta_comptes(vp, fp, fn, 2),
           "f05": f_beta_comptes(vp, fp, fn, 0.5), "moyenne": (p + r) / 2,
           "exactitude": (vp + vn) / (vp + fp + fn + vn)}
    res["bascule"] = next(x for x in range(0, fn + 1) if f_beta_comptes(vp + x, fp, fn - x, 2) >= 0.85)
    res["f2_11"], res["f2_12"] = f_beta_comptes(51, 10, 9, 2), f_beta_comptes(52, 10, 8, 2)
    res["decision"] = "production" if res["f2"] >= 0.85 else "bloquée"
    print(f"Cas 1 [BANQUE] P {p} ; R {r:.5f} ; F1 {res['f1']:.5f} ; F2 {res['f2']:.5f} ; F0,5 {res['f05']:.5f} ;"
          f" décision : {res['decision']}")
    print(f"  moyenne {res['moyenne']:.5f} ; exactitude {res['exactitude']:.5f} ; oublis à corriger : {res['bascule']}"
          f" (F2 {res['f2_11']:.5f} → {res['f2_12']:.5f})")
    return res


def cas_2_immo_ejari() -> dict:
    """[IMMO] 1 600 champs ; A (1 380, 120, 220) ; B (1 274, 26, 326) ; champ faux 300 AED, manquant 40 AED."""
    modeles = {"A": (1_380, 120, 220), "B": (1_274, 26, 326)}
    res = {}
    for nom, (vp, fp, fn) in modeles.items():
        res[nom] = {"p": precision(vp, fp), "r": rappel(vp, fn), "f1": f1_comptages(vp, fp, fn),
                    "f05": f_beta_comptes(vp, fp, fn, 0.5), "cout": fp * 300 + fn * 40}
    beta2 = 40 / 300
    rapport_bascule = (326 - 220) / (120 - 26)
    choix = min(res, key=lambda k: res[k]["cout"])
    print(f"Cas 2 [IMMO] A : F1 {res['A']['f1']:.5f}, F0,5 {res['A']['f05']:.5f}, coût {res['A']['cout']:,} AED ;"
          f" B : F1 {res['B']['f1']:.5f}, F0,5 {res['B']['f05']:.5f}, coût {res['B']['cout']:,} AED ; décision : {choix}")
    print(f"  β² = {beta2:.5f}, β = {math.sqrt(beta2):.5f} ; rapport de bascule {rapport_bascule:.5f}")
    return {"res": res, "beta2": beta2, "beta": math.sqrt(beta2), "rapport_bascule": rapport_bascule, "choix": choix}


def cas_3_btp_factures() -> dict:
    """[BTP] 80 lignes non conformes ; S1 (64, 36, 16) ; S2 (51, 9, 29) ; oubli 4 000 AED ; vérification 50 AED."""
    seuils = {"S1": (64, 36, 16), "S2": (51, 9, 29)}
    res = {}
    for nom, (vp, fp, fn) in seuils.items():
        res[nom] = {"p": precision(vp, fp), "r": rappel(vp, fn), "f1": f1_comptages(vp, fp, fn),
                    "f2": f_beta_comptes(vp, fp, fn, 2), "cout": fn * 4_000 + (vp + fp) * 50}
    m_bascule = (60 * 50 - 100 * 50) / (16 - 29)
    choix = min(res, key=lambda k: res[k]["cout"])
    print(f"Cas 3 [BTP] S1 : F1 {res['S1']['f1']:.5f}, F2 {res['S1']['f2']:.5f}, coût {res['S1']['cout']:,} AED ;"
          f" S2 : F1 {res['S2']['f1']:.5f}, F2 {res['S2']['f2']:.5f}, coût {res['S2']['cout']:,} AED ; décision : {choix}")
    print(f"  bascule {m_bascule:.2f} AED par ligne manquée ; β équivalent {math.sqrt(4_000 / 50):.3f}")
    return {"res": res, "m_bascule": m_bascule, "choix": choix, "beta_equiv": math.sqrt(4_000 / 50)}


def cas_4_public_routage() -> dict:
    """[PUBLIC] matrice 3 × 3 (EC, PE, RE) ; F1 par service, macro et micro ; règle macro >= 0,8 et chaque F1 >= 0,7."""
    services = ("EC", "PE", "RE")
    m = {"EC": (470, 20, 10), "PE": (30, 360, 10), "RE": (20, 30, 50)}
    comptes = {}
    for j, s in enumerate(services):
        vp = m[s][j]
        fp = sum(m[t][j] for t in services if t != s)
        fn = sum(m[s]) - vp
        comptes[s] = (vp, fp, fn)
    f1s = {s: f1_comptages(*comptes[s]) for s in services}
    macro = sum(f1s.values()) / 3
    tot = [sum(c[i] for c in comptes.values()) for i in range(3)]
    micro = f1_comptages(*tot)
    accepte = macro >= 0.8 and all(v >= 0.7 for v in f1s.values())
    bascule = next(x for x in range(0, 51) if f1_comptages(50 + x, 20, 50 - x) >= 0.7)
    print("Cas 4 [PUBLIC] " + " ; ".join(f"{s} {comptes[s]} F1 {f1s[s]:.5f}" for s in services)
          + f" ; macro {macro:.5f} ; micro {micro}")
    print(f"  décision : {'routage automatique' if accepte else 'tri humain des réclamations'} ;"
          f" réclamations à corriger : {bascule} (F1 {f1_comptages(64, 20, 36):.5f} → {f1_comptages(65, 20, 35):.5f})")
    return {"comptes": comptes, "f1s": f1s, "macro": macro, "micro": micro, "tot": tot, "accepte": accepte,
            "bascule": bascule}


def main() -> None:
    # Mécanisme et démonstration 1
    inv_p, inv_r = 1 / 0.9, 1 / 0.3
    print(f"Démonstration 1 : 1/0,9 = {inv_p:.5f} ; 1/0,3 = {inv_r:.5f} ; 2 / somme = {2 / (inv_p + inv_r):.2f}"
          f" = F1 {f1(0.9, 0.3):.2f} ; moyenne arithmétique {(0.9 + 0.3) / 2:.1f}")
    assert round(inv_p, 5) == 1.11111 and round(inv_r, 5) == 3.33333 and round(inv_p + inv_r, 5) == 4.44444
    assert round((inv_p + inv_r) / 2, 5) == 2.22222 and round(2 / (inv_p + inv_r), 2) == 0.45
    assert round(f1(0.9, 0.3), 2) == 0.45 and round(2 * 0.9 * 0.3, 2) == 0.54 and round(0.9 + 0.3, 1) == 1.2
    assert round(0.9 * 0.3, 2) == 0.27 and round((0.9 + 0.3) / 2, 1) == 0.6
    assert f1(0.5, 0.5) == 0.5 and round(f1(1, 0.01), 4) == 0.0198 and (1 + 100) / 2 == 50.5
    assert f1(0.7, 0.0) == 0.0 and f1(None, 0.5) is None
    for pp in (0.1, 0.4, 0.7, 1.0):
        for rr in (0.05, 0.5, 0.9):
            assert abs(f1(pp, rr) - 2 / (1 / pp + 1 / rr)) < 1e-12

    # Démonstration 2
    print(f"Démonstration 2 : F1(40, 10, 20) = {f1_comptages(40, 10, 20):.5f} ; agent muet → précision"
          f" {precision(0, 0)}, F1 {f1_comptages(0, 0, 10)} ; rien du tout → {f1_comptages(0, 0, 0)}")
    assert round(f1_comptages(40, 10, 20), 5) == round(f1(0.8, 40 / 60), 5) == 0.72727
    assert precision(0, 0) is None and f1_comptages(0, 0, 10) == 0.0 and f1_comptages(0, 0, 0) is None
    assert round(0.8 + 40 / 60, 5) == 1.46667

    # Démonstration 3
    print(f"Démonstration 3 : F1(0,6 ; 0,8) = {f1(0.6, 0.8):.5f} ; F1(1 ; 0,01) = {f1(1, 0.01):.4f} < {2 * 0.01}")
    assert round(f1(0.6, 0.8), 5) == 0.68571 and round(2 * 0.6 * 0.8, 2) == 0.96 and round(0.6 + 0.8, 1) == 1.4
    assert f1(1, 0.01) < 2 * 0.01 and round((1 + 0.01) / 2, 3) == 0.505
    for pp in (0.05, 0.3, 0.6, 0.9, 1.0):
        for rr in (0.01, 0.2, 0.5, 0.8, 1.0):
            v = f1(pp, rr)
            assert min(pp, rr) - 1e-12 <= v <= (pp + rr) / 2 + 1e-12
            assert abs((pp + rr) / 2 - v - (pp - rr) ** 2 / (2 * (pp + rr))) < 1e-12
            assert v <= 2 * min(pp, rr) + 1e-12

    # Démonstration 4
    p, r = 0.8, 40 / 60
    print(f"Démonstration 4 : F2 = {f_beta(p, r, 2):.5f} = {f_beta_comptes(40, 10, 20, 2):.5f} ; F0,5 = {f_beta(p, r, 0.5):.5f} ;"
          f" formule inversée = {(5 * p * r) / (p + 4 * r):.5f}")
    assert round(f_beta(p, r, 2), 5) == round(f_beta_comptes(40, 10, 20, 2), 5) == 0.68966
    assert round(f_beta(p, r, 0.5), 5) == round(f_beta_comptes(40, 10, 20, 0.5), 5) == 0.76923
    assert round(5 * p * r, 5) == 2.66667 and round(4 * p + r, 5) == 3.86667 and round(p + 4 * r, 5) == 3.46667
    assert round((5 * p * r) / (p + 4 * r), 5) == 0.76923 and abs(f_beta(p, r, 1) - f1(p, r)) < 1e-12
    assert abs(f_beta(p, r, 1e4) - r) < 1e-6 and abs(f_beta(p, r, 1e-4) - p) < 1e-6
    harmonique = 1 / ((1 / 5) * (1 / p) + (4 / 5) * (1 / r))
    assert abs(harmonique - f_beta(p, r, 2)) < 1e-12

    # Démonstration 5
    dp, dr = derivees(0.9, 0.3)
    g_r, g_p = f1(0.9, 0.31) - f1(0.9, 0.3), f1(0.91, 0.3) - f1(0.9, 0.3)
    print(f"Démonstration 5 : ∂F1/∂P = {dp:.3f} ; ∂F1/∂R = {dr:.3f} ; rapport {dr / dp:.0f} ;"
          f" +0,01 sur R → {g_r:.5f}, sur P → {g_p:.5f}")
    assert round(dp, 3) == 0.125 and round(dr, 3) == 1.125 and round(dr / dp) == 9 == round((0.9 / 0.3) ** 2)
    assert round(f1(0.9, 0.31), 5) == 0.46116 and round(f1(0.91, 0.3), 5) == 0.45124
    assert round(g_r, 5) == 0.01116 and round(g_p, 5) == 0.00124 and round(g_r, 4) == 0.0112 and round(g_p, 4) == 0.0012
    assert round(2 * 0.9 * 0.31, 3) == 0.558 and round(2 * 0.91 * 0.3, 3) == 0.546 and derivees(0.5, 0.5) == (0.5, 0.5)

    # Cas
    c1 = cas_1_banque_outils()
    assert c1["p"] == 0.8 and round(c1["r"], 5) == 0.66667 and round(c1["f1"], 5) == 0.72727
    assert round(c1["f2"], 5) == 0.68966 and round(c1["f05"], 5) == 0.76923 and c1["decision"] == "bloquée"
    assert round(c1["moyenne"], 5) == 0.73333 and round(c1["exactitude"], 5) == 0.99702 and 40 + 10 + 20 + 10_000 == 10_070
    assert c1["bascule"] == 12 and round(c1["f2_11"], 5) == 0.84718 and round(c1["f2_12"], 5) == 0.86093
    assert round((246.5 - 200) / (5 - 0.85), 3) == 11.205 and round(0.85 * 290, 1) == 246.5

    c2 = cas_2_immo_ejari()
    a, b = c2["res"]["A"], c2["res"]["B"]
    assert (a["p"], a["r"], b["p"], b["r"]) == (0.92, 0.8625, 0.98, 0.79625)
    assert round(a["f1"], 5) == 0.89032 and round(b["f1"], 5) == 0.87862
    assert round(a["f05"], 5) == 0.90789 and round(b["f05"], 5) == 0.93676 and 1.25 * 1_380 == 1_725
    assert 1.25 * 1_274 == 1_592.5 and 0.25 * 220 == 55 and 1_592.5 + 0.25 * 326 + 26 == 1_700
    assert (a["cout"], b["cout"], a["cout"] - b["cout"]) == (44_800, 20_840, 23_960) and c2["choix"] == "B"
    assert round(c2["beta2"], 5) == 0.13333 and round(c2["beta"], 5) == 0.36515 and round(c2["rapport_bascule"], 5) == 1.12766
    assert 300 / 40 == 7.5

    c3 = cas_3_btp_factures()
    s1, s2 = c3["res"]["S1"], c3["res"]["S2"]
    assert (s1["p"], s1["r"], s2["p"], s2["r"]) == (0.64, 0.8, 0.85, 0.6375)
    assert round(s1["f1"], 5) == 0.71111 and round(s2["f1"], 5) == 0.72857
    assert round(s1["f2"], 4) == 0.7619 and round(s2["f2"], 5) == 0.67105
    assert (s1["cout"], s2["cout"]) == (69_000, 119_000) and c3["choix"] == "S1" and s2["cout"] - s1["cout"] == 50_000
    assert round(c3["m_bascule"], 2) == 153.85 and round(c3["beta_equiv"], 3) == 8.944 and 0.10 * 100_000 == 10_000

    c4 = cas_4_public_routage()
    assert c4["comptes"] == {"EC": (470, 50, 30), "PE": (360, 50, 40), "RE": (50, 20, 50)}
    assert [round(c4["f1s"][s], 5) for s in ("EC", "PE", "RE")] == [0.92157, 0.88889, 0.58824]
    assert round(c4["macro"], 5) == 0.79956 and c4["micro"] == 0.88 and c4["tot"] == [880, 120, 120]
    assert c4["accepte"] is False and c4["bascule"] == 15 and round(precision(50, 20), 5) == 0.71429
    assert round(f1_comptages(64, 20, 36), 5) == 0.69565 and round(f1_comptages(65, 20, 35), 4) == 0.7027
    assert round((119 - 100) / (2 - 0.7), 1) == 14.6

    # Corrigé
    print("Corrigé")
    print(f"  ex1 {f1(0.5, 0.5)} ; ex2 {f1(1, 0.01):.4f} contre {(1 + 0.01) / 2:.3f} ; ex3 {f1_comptages(30, 10, 30)} ;"
          f" ex4 {f1(0.6, 0.8):.5f} ; ex6 S1 {16 * 100 + 100 * 50:,} S2 {29 * 100 + 60 * 50:,} ; ex7 {(5 * p * r) / (p + 4 * r):.5f}")
    assert f1(0.5, 0.5) == 0.5 and f1_comptages(30, 10, 30) == 0.6 and f1(0.75, 0.5) == 0.6
    assert round(0.04 / 2.8, 5) == 0.01429 and round(0.7 - 0.04 / 2.8, 5) == 0.68571
    assert 16 * 100 + 100 * 50 == 6_600 and 29 * 100 + 60 * 50 == 5_900
    try:
        f_beta(0.5, 0.5, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("beta = 0 aurait dû être refusé")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Démonstration 1 : 1/0,9 = 1.11111 ; 1/0,3 = 3.33333 ; 2 / somme = 0.45 = F1 0.45 ; moyenne arithmétique 0.6
Démonstration 2 : F1(40, 10, 20) = 0.72727 ; agent muet → précision None, F1 0.0 ; rien du tout → None
Démonstration 3 : F1(0,6 ; 0,8) = 0.68571 ; F1(1 ; 0,01) = 0.0198 < 0.02
Démonstration 4 : F2 = 0.68966 = 0.68966 ; F0,5 = 0.76923 ; formule inversée = 0.76923
Démonstration 5 : ∂F1/∂P = 0.125 ; ∂F1/∂R = 1.125 ; rapport 9 ; +0,01 sur R → 0.01116, sur P → 0.00124
Cas 1 [BANQUE] P 0.8 ; R 0.66667 ; F1 0.72727 ; F2 0.68966 ; F0,5 0.76923 ; décision : bloquée
  moyenne 0.73333 ; exactitude 0.99702 ; oublis à corriger : 12 (F2 0.84718 → 0.86093)
Cas 2 [IMMO] A : F1 0.89032, F0,5 0.90789, coût 44,800 AED ; B : F1 0.87862, F0,5 0.93676, coût 20,840 AED ; décision : B
  β² = 0.13333, β = 0.36515 ; rapport de bascule 1.12766
Cas 3 [BTP] S1 : F1 0.71111, F2 0.76190, coût 69,000 AED ; S2 : F1 0.72857, F2 0.67105, coût 119,000 AED ; décision : S1
  bascule 153.85 AED par ligne manquée ; β équivalent 8.944
Cas 4 [PUBLIC] EC (470, 50, 30) F1 0.92157 ; PE (360, 50, 40) F1 0.88889 ; RE (50, 20, 50) F1 0.58824 ; macro 0.79956 ; micro 0.88
  décision : tri humain des réclamations ; réclamations à corriger : 15 (F1 0.69565 → 0.70270)
Corrigé
  ex1 0.5 ; ex2 0.0198 contre 0.505 ; ex3 0.6 ; ex4 0.68571 ; ex6 S1 6,600 S2 5,900 ; ex7 0.76923
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme combine précision et rappel en un score, avec la variante pondérée F-bêta, directement à partir des comptages, puis choisit entre deux réglages en comparant leur Fβ et leur coût.

```text
ALGORITHME ScoreF
ENTRÉES : vp, fp, fn, bêta (1 pour F1)
SORTIE  : F_β, ou INDÉFINI si vp = fp = fn = 0

  dén ← (1 + β²) × vp + β² × fn + fp
  SI dén = 0 ALORS RETOURNER INDÉFINI
  RETOURNER (1 + β²) × vp / dén

ALGORITHME ChoisirUnRéglage
ENTRÉES : réglages (vp, fp, fn), coût d'un faux négatif c_FN, coût d'un faux positif c_FP
  β ← racine carrée de c_FN / c_FP
  POUR CHAQUE réglage FAIRE
      noter ScoreF(vp, fp, fn, β) et le coût fn × c_FN + fp × c_FP
  FIN POUR
  RETOURNER le réglage de coût minimal, avec son F_β comme score sans unité
```

**Complexité.** O(1) une fois les comptages faits ; les comptages eux-mêmes coûtent O(n) sur n éléments, et O(n + m²) pour une matrice de confusion à m classes. Les vrais négatifs n'interviennent nulle part.

**Du squelette au code.** ScoreF est `f_beta_comptes(vp, fp, fn, beta)` ; le cas β = 1 est `f1_comptages(vp, fp, fn)`, et la version à partir des taux est `f_beta(p, r, beta)`, avec `f1(p, r)` pour β = 1. `main` vérifie que les formes coïncident, que F-bêta tend vers R quand β grandit, et la sensibilité avec `derivees(p, r)`. ChoisirUnRéglage correspond à `cas_2_immo_ejari` et `cas_3_btp_factures`, qui comparent F-bêta et coûts ; les autres cas sont `cas_1_banque_outils` et `cas_4_public_routage`.
