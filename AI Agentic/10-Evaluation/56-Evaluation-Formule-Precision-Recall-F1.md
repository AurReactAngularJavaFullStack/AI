# Étape 56 — Évaluation — Precision, Recall et F1

> Étape 56 du parcours · Prérequis : [Answer Relevancy](<55-Evaluation-Formule-Answer-Relevancy.md>) · Suite : [Context Precision](<57-Evaluation-Formule-Context-Precision.md>)

**Dossier :** 10-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  
**Nom du fichier :** 56-Evaluation-Formule-Precision-Recall-F1.md

## Définition

La précision, le rappel et la F1 comparent, pour un cas d'évaluation, l'ensemble des éléments que l'agent a produits (pièces réclamées, entités extraites, alertes levées, outils appelés) à l'ensemble des éléments qu'il aurait dû produire. Un vrai positif (TP) est un élément produit et attendu, un faux positif (FP) un élément produit mais pas attendu, un faux négatif (FN) un élément attendu mais oublié. La précision dit quelle part de ce que l'agent a produit était juste, le rappel quelle part de ce qui était attendu il a trouvée, et la F1 est leur moyenne harmonique ; la Fᵦ la généralise en donnant au rappel β² fois plus de poids qu'à la précision. Sur un jeu de plusieurs cas, il faut choisir comment agréger : la moyenne **micro** additionne les comptes de tous les cas avant de diviser, la moyenne **macro** calcule le score de chaque cas puis en fait la moyenne. Enfin, un cas où rien n'était attendu et rien n'a été produit donne 0/0 partout : la convention retenue, exclusion ou score de 1, fait partie de la définition de la métrique et se publie avec le résultat.

## Rôle dans un agent

Ces taux ne se calculent pas pendant la conversation, puisque l'agent ne connaît pas la vérité terrain : ils servent à l'étape **observer**, hors ligne, sur un jeu de cas étiquetés que l'on rejoue à chaque changement de prompt, de modèle ou d'outil, selon le protocole de l'étape 13 bis. Ils évaluent tout composant qui produit un *ensemble* : l'extracteur qui lit un dossier KYC, le détecteur d'un garde-fou qui lève des alertes, le routeur qui choisit une intention, le retriever qui renvoie des passages, la boucle qui appelle des outils. Les étapes suivantes en sont des spécialisations : Context Precision (étape 57) pondère la précision par le rang, Context Recall (étape 58) applique le rappel aux affirmations d'une réponse de référence, Tool Call F1 (étape 59) applique la F1 aux appels d'outils. Dans la barrière d'intégration continue, on fixe un seuil sur une moyenne précise, micro ou macro, avec une convention précise pour le cas vide : changer l'une ou l'autre change le nombre, donc la décision.

## Équation complète

Pour un cas :

$$
P = \frac{TP}{TP + FP} \qquad R = \frac{TP}{TP + FN}
$$

$$
F_1 = \frac{2PR}{P + R} = \frac{2\,TP}{2\,TP + FP + FN}
$$

$$
F_\beta = \frac{(1+\beta^2)\,P\,R}{\beta^2 P + R} = \frac{(1+\beta^2)\,TP}{(1+\beta^2)\,TP + \beta^2 FN + FP}
$$

Moyenne micro sur N cas : on additionne d'abord les comptes, puis on divise une seule fois.

$$
P_{micro} = \frac{\sum_{i=1}^{N} TP_i}{\sum_{i=1}^{N} (TP_i + FP_i)} \qquad R_{micro} = \frac{\sum_{i=1}^{N} TP_i}{\sum_{i=1}^{N} (TP_i + FN_i)}
$$

$$
F_{1,micro} = \frac{2 \sum_{i} TP_i}{2 \sum_{i} TP_i + \sum_{i} FP_i + \sum_{i} FN_i}
$$

Moyenne macro : on moyenne les scores des seuls cas définis.

$$
F_{1,macro} = \frac{1}{|D|} \sum_{i \in D} F_{1,i} \qquad D = \{\, i \;:\; TP_i + FP_i + FN_i > 0 \,\}
$$

Convention du cas vide, retenue dans ce parcours :

$$
TP_i = FP_i = FN_i = 0 \;\Longrightarrow\; F_{1,i} \text{ indéfini : le cas sort de } D \text{ et son nombre est publié}
$$

## Décryptage des symboles

$$
TP
$$

**Sens :** nombre de vrais positifs d'un cas, les éléments produits et attendus · **Type / plage :** entier ≥ 0 · **Variable Python :** `c.tp`

$$
FP
$$

**Sens :** nombre de faux positifs, les éléments produits mais pas attendus (bruit, fausses alertes, réclamations inutiles) · **Type / plage :** entier ≥ 0 · **Variable Python :** `c.fp`

$$
FN
$$

**Sens :** nombre de faux négatifs, les éléments attendus mais oubliés · **Type / plage :** entier ≥ 0 · **Variable Python :** `c.fn`

$$
P
$$

**Sens :** précision, la part des éléments produits qui étaient attendus · **Type / plage :** réel dans [0, 1], indéfini si TP + FP = 0 · **Variable Python :** `precision(c)`

$$
R
$$

**Sens :** rappel, la part des éléments attendus que l'agent a produits · **Type / plage :** réel dans [0, 1], indéfini si TP + FN = 0 · **Variable Python :** `rappel(c)`

$$
F_1
$$

**Sens :** moyenne harmonique de P et R · **Type / plage :** réel dans [0, 1], défini dès que TP + FP + FN > 0 · **Variable Python :** `f_beta(c)`

$$
F_\beta
$$

**Sens :** moyenne harmonique pondérée, qui donne au rappel β² fois le poids de la précision · **Type / plage :** réel dans [0, 1] · **Variable Python :** `f_beta(c, beta)`

$$
\beta
$$

**Sens :** réglage du compromis : β = 2 favorise le rappel (un oubli coûte cher), β = 0,5 la précision (une fausse alerte coûte cher), β = 1 redonne F₁ · **Type / plage :** réel > 0 · **Variable Python :** `beta`

$$
i
$$

**Sens :** indice d'un cas du jeu d'évaluation (un dossier, une requête, une conversation) · **Type / plage :** entier de 1 à N · **Variable Python :** la position dans la liste `dossiers`

$$
N
$$

**Sens :** nombre de cas du jeu d'évaluation · **Type / plage :** entier ≥ 1 · **Variable Python :** `len(dossiers)`

$$
D
$$

**Sens :** ensemble des cas définis, ceux qui ont au moins un élément attendu ou produit · **Type / plage :** sous-ensemble des N cas · **Variable Python :** `macro_f` garde ces cas et renvoie le nombre des autres

$$
P_{micro}
$$

**Sens :** précision calculée sur les comptes additionnés de tous les cas (même lecture pour le rappel et la F1 micro) · **Type / plage :** réel dans [0, 1] · **Variable Python :** `micro(cas)`

$$
F_{1,macro}
$$

**Sens :** moyenne des F₁ des cas définis : chaque cas a une voix, quelle que soit sa taille · **Type / plage :** réel dans [0, 1] · **Variable Python :** `macro_f(cas)`

## Démonstration

### 1. Ce qui est déjà démontré à l'étape 50

La forme par les comptes F₁ = 2TP / (2TP + FP + FN), l'encadrement min(P, R) ≤ F₁ ≤ (P + R)/2 et le choix de la moyenne harmonique sont démontrés à l'[étape 50](<50-Precision-Rappel-F1-et-KL.md>). On s'en sert ici sans les refaire. À retenir : la F1 reste proche du plus petit des deux taux, et sa forme par les comptes reste définie quand P et R valent tous deux 0. Les points suivants ajoutent ce dont on a besoin pour évaluer un agent sur un jeu entier : la Fᵦ, le cas vide, et l'agrégation micro ou macro.

### 2. Fᵦ est une moyenne harmonique pondérée

On prend l'inverse de Fᵦ et on coupe la fraction en deux :

$$
\frac{1}{F_\beta} = \frac{\beta^2 P + R}{(1+\beta^2)\,P\,R} = \frac{1}{1+\beta^2}\cdot\frac{1}{P} + \frac{\beta^2}{1+\beta^2}\cdot\frac{1}{R}
$$

La deuxième égalité tient parce que (β²P + R)/(PR) = β²/R + 1/P. L'inverse de Fᵦ est donc une moyenne pondérée des inverses de P et de R, avec le poids w = β²/(1 + β²) sur le rappel et 1 − w sur la précision : c'est la définition d'une moyenne harmonique pondérée. Pour β = 1, w = 1/2, et l'on retrouve F₁. Trois conséquences se lisent directement :

- Fᵦ est toujours comprise entre P et R, parce qu'une moyenne pondérée de 1/P et 1/R est comprise entre les deux.
- Quand β tend vers 0, w tend vers 0 et Fᵦ tend vers P ; quand β tend vers l'infini, w tend vers 1 et Fᵦ tend vers R.
- Si R > P, alors 1/R < 1/P : augmenter β déplace le poids vers le plus petit des deux inverses, donc 1/Fᵦ baisse et Fᵦ monte. C'est pourquoi, sur l'exemple du point 7 où R = 1 > P, on observe F₀,₅ < F₁ < F₂.

### 3. Forme par les comptes : un oubli coûte β² fausses alertes

On remplace P par TP/(TP + FP) et R par TP/(TP + FN). Le numérateur vaut

$$
(1+\beta^2)\,P\,R = \frac{(1+\beta^2)\,TP^2}{(TP+FP)(TP+FN)}
$$

et le dénominateur, mis au même dénominateur commun,

$$
\beta^2 P + R = \frac{TP\,\big[\beta^2 (TP+FN) + (TP+FP)\big]}{(TP+FP)(TP+FN)}
$$

Le quotient fait disparaître le dénominateur commun et un facteur TP :

$$
F_\beta = \frac{(1+\beta^2)\,TP}{(1+\beta^2)\,TP + \beta^2 FN + FP}
$$

Lecture : au dénominateur, chaque FN ajoute β² et chaque FP ajoute 1. Avec β = 2, un oubli coûte autant que quatre fausses alertes ; avec β = 0,5, quatre fois moins. Cette forme a un second avantage : elle est définie dès que TP + FP + FN > 0, sans cas particulier quand P et R sont nuls. Avec TP = 0, FP = 3 et FN = 4, elle donne directement Fᵦ = 0.

### 4. Le cas vide : 0/0 n'est ni 0 ni 1

Quand TP = FP = FN = 0, les trois formules donnent 0/0. Ce cas est fréquent et il est souvent un **succès** : un dossier de crédit complet pour lequel l'agent ne réclame aucune pièce, un message sain sur lequel le garde-fou ne lève aucune alerte. L'ancien code de ce fichier renvoyait 0,0 : il punissait l'agent précisément quand il avait raison de ne rien faire. Deux conventions sont défendables, à condition de les annoncer :

- **l'exclusion**, retenue par défaut dans ce parcours : le cas sort de la moyenne macro, on publie le nombre de cas exclus et, à part, un taux d'abstention correcte (cas vides réussis divisés par cas où rien n'était attendu) ;
- **le score de 1**, quand l'équipe veut un seul nombre qui récompense l'abstention correcte ; il fait monter la moyenne et doit être écrit à côté du résultat.

Les cas à moitié vides n'ont pas besoin de convention. Si l'agent n'a rien produit alors que quelque chose était attendu, P est indéfinie mais R = 0 et Fᵦ = 0 par la forme du point 3 : l'agent a tout manqué, le 0 est mérité. Si rien n'était attendu mais que l'agent a produit quelque chose, R est indéfini mais P = 0 et Fᵦ = 0 : il n'a levé que de fausses alertes. Seul le cas entièrement vide est un vrai 0/0.

### 5. Micro et macro ne répondent pas à la même question

La précision micro est une moyenne des précisions par cas, pondérée par le nombre d'éléments que chaque cas a produits :

$$
P_{micro} = \frac{\sum_i TP_i}{\sum_j (TP_j + FP_j)} = \sum_i \frac{TP_i + FP_i}{\sum_j (TP_j + FP_j)} \cdot \frac{TP_i}{TP_i + FP_i} = \sum_i w_i \, P_i
$$

On passe à la deuxième expression en multipliant et en divisant chaque terme par TPᵢ + FPᵢ. Un cas qui n'a rien produit a un poids nul et disparaît, ce qui est cohérent avec son P indéfini. De même, le rappel micro est la moyenne des rappels pondérée par le nombre d'éléments attendus. La micro donne donc une voix à chaque **élément** et la macro une voix à chaque **cas** : un gros dossier domine la micro, un petit dossier raté pèse autant qu'un gros dans la macro. Aucune n'est « la bonne ». La macro répond à « quelle part des dossiers est bien traitée ? », la micro à « quelle part des pièces est bien traitée ? », comme pour le rappel de l'[étape 25](<../05-RAG/25-RAG-Formule-Recall-at-k.md>). Il existe en outre deux définitions de la F1 macro : la moyenne des F₁ par cas, retenue ici, et la F₁ calculée à partir de la précision macro et du rappel macro ; elles ne donnent pas le même nombre, on annonce donc laquelle on publie.

### 6. En classification à une seule étiquette, la micro vaut l'exactitude

Un routeur d'intentions reçoit N requêtes ; chacune a une vraie intention et une intention prédite. Pour chaque classe k, on compte TPₖ, FPₖ et FNₖ. Une prédiction juste est un TP pour sa classe. Une erreur, vraie intention a et intention prédite b ≠ a, est **à la fois** un FP pour b et un FN pour a. Si E est le nombre d'erreurs, la somme des FPₖ et la somme des FNₖ valent donc toutes deux E, et la somme des TPₖ vaut N − E. D'où :

$$
P_{micro} = R_{micro} = F_{1,micro} = \frac{N - E}{(N - E) + E} = \frac{N - E}{N} = \text{exactitude}
$$

Dans ce cadre, la F1 micro n'apprend rien de plus que l'exactitude. C'est la F1 macro qui révèle une classe rare sacrifiée : sur l'exemple du programme, l'exactitude vaut 0,90 alors que la F1 macro vaut 0,641, parce que l'unique réclamation a été routée vers les visas.

### 7. Exemple fait à la main (le code reprend ces nombres)

Un agent de back-office liste les pièces manquantes d'un dossier de crédit. Pour le dossier D1, les pièces réellement manquantes sont le relevé bancaire et le certificat de salaire ; l'agent réclame ces deux pièces et le passeport, déjà fourni. Donc TP = 2, FP = 1, FN = 0 :

$$
P = \frac{2}{3} \approx 0{,}667 \qquad R = \frac{2}{2} = 1 \qquad F_1 = \frac{2 \times 2}{2 \times 2 + 1 + 0} = \frac{4}{5} = 0{,}8
$$

$$
F_2 = \frac{5 \times 2}{5 \times 2 + 4 \times 0 + 1} = \frac{10}{11} \approx 0{,}909 \qquad F_{0{,}5} = \frac{1{,}25 \times 2}{1{,}25 \times 2 + 0{,}25 \times 0 + 1} = \frac{2{,}5}{3{,}5} \approx 0{,}714
$$

L'erreur est une fausse alerte : la F₂, qui valorise le rappel, est indulgente ; la F₀,₅, qui valorise la précision, est sévère. On ajoute trois dossiers :

| Dossier | Situation | TP | FP | FN | P | R | F₁ |
|---|---|---|---|---|---|---|---|
| D1 | pièces de l'exemple ci-dessus | 2 | 1 | 0 | 0,667 | 1 | 0,8 |
| D2 | société de BTP : 15 pièces manquantes, l'agent en réclame 10 dont 9 justes | 9 | 1 | 6 | 0,9 | 0,6 | 0,72 |
| D3 | dossier complet, l'agent ne réclame rien | 0 | 0 | 0 | indéfinie | indéfini | indéfinie |
| D4 | deux pièces manquent, l'agent ne réclame rien | 0 | 0 | 2 | indéfinie | 0 | 0 |

Pour D2, F₁ = 2 × 9 / (2 × 9 + 1 + 6) = 18/25 = 0,72. Les trois conventions donnent trois moyennes macro différentes :

$$
\text{exclusion : } \frac{0{,}8 + 0{,}72 + 0}{3} \approx 0{,}5067 \qquad \text{vide} = 1 : \frac{0{,}8 + 0{,}72 + 1 + 0}{4} = 0{,}63 \qquad \text{ancien code : } \frac{0{,}8 + 0{,}72 + 0 + 0}{4} = 0{,}38
$$

La micro additionne les comptes, 11 TP, 2 FP et 8 FN, et le gros dossier D2 y pèse lourd :

$$
P_{micro} = \frac{11}{13} \approx 0{,}846 \qquad R_{micro} = \frac{11}{19} \approx 0{,}579 \qquad F_{1,micro} = \frac{22}{22 + 2 + 8} = 0{,}6875
$$

## Effets et comportement

- **Un FP fait baisser P et laisse R intact ; un FN fait baisser R et laisse P intact.** La F1 baisse dans les deux cas, et la Fᵦ pèse les deux erreurs dans le rapport β² (point 3).
- **Augmenter β fait monter Fᵦ quand R > P, et la fait baisser quand R < P** (point 2). Choisir β après avoir vu les résultats revient à choisir le chiffre qui arrange : on le fixe à partir des coûts métier, avant la mesure.
- **La micro suit les gros cas, la macro suit les cas nombreux.** Un agent excellent sur les gros dossiers et mauvais sur les petits a une bonne micro et une macro médiocre (point 5).
- **La convention du cas vide déplace la moyenne macro** : de 0,38 à 0,63 sur l'exemple, avec exactement les mêmes décisions de l'agent.
- **Les vrais négatifs n'apparaissent nulle part.** Précision et rappel ne récompensent pas les milliers de choses que l'agent a eu raison de ne pas faire ; pour cela, on utilise la spécificité de l'[étape 51](<51-Specificite-NPV-AUC.md>).

## Du symbole au code Python

| Notion | Variable ou fonction |
|---|---|
| TP, FP, FN d'un cas | `Comptes(tp, fp, fn)`, construit par `comptes(attendus, predits)` |
| P et R | `precision(c)`, `rappel(c)` |
| F₁ et Fᵦ, forme par les comptes | `f_beta(c, beta)` |
| Fᵦ, forme par les taux | `f_beta_par_taux(p, r, beta)` |
| moyenne micro | `micro(cas, beta)` |
| moyenne macro et nombre de cas exclus | `macro_f(cas, beta, vide)` |
| l'ancien calcul, pour comparer | `ancien_f1(tp, fp, fn)` |
| comptes par classe d'un routeur | `comptes_par_classe(vrais, predits)` |

### Déroulé, ligne par ligne

**`Comptes`** est une `dataclass` figée (`frozen=True`) qui porte les trois compteurs d'un cas. Sa méthode `__post_init__` s'exécute à la construction et lève `ValueError` si l'un des comptes est négatif : un compte négatif signale un bug en amont, pas une mesure.

**`comptes(attendus, predits)`** traduit deux ensembles en compteurs.

- `attendus & predits` est l'intersection : pour D1, `{'releve_bancaire', 'certificat_salaire'}`, donc `tp = 2`.
- `predits - attendus` garde ce qui a été produit sans être attendu : `{'passeport'}`, donc `fp = 1`.
- `attendus - predits` garde ce qui a été oublié : l'ensemble vide, donc `fn = 0`.

**`precision(c)`** et **`rappel(c)`** renvoient `None` quand leur dénominateur est nul, au lieu d'un 0 trompeur. Pour D1 : `2 / 3`, soit 0,6667, et `2 / 2`, soit 1,0.

**`f_beta(c, beta)`** applique la forme par les comptes du point 3.

- `if beta <= 0` : un β nul ou négatif n'a pas de sens, on lève `ValueError`.
- `b2 = beta * beta`, puis `denominateur = (1 + b2) * c.tp + b2 * c.fn + c.fp`. Pour D1 et β = 1 : 2 × 2 + 0 + 1 = 5, et la fonction renvoie 4/5 = 0,8. Pour β = 2 : `b2 = 4`, le dénominateur vaut 5 × 2 + 4 × 0 + 1 = 11 et le résultat 10/11.
- `return None if denominateur == 0` : le dénominateur ne s'annule que si TP = FP = FN = 0, c'est-à-dire pour le seul vrai cas vide (point 4).

**`f_beta_par_taux(p, r, beta)`** calcule la forme par les taux. Elle ne sert qu'à vérifier, par `assert`, que les deux formes donnent le même nombre.

**`micro(cas, beta)`** construit un `Comptes` total en additionnant les trois compteurs de tous les cas, puis appelle les mêmes fonctions qu'un cas seul. Pour les quatre dossiers, le total vaut `Comptes(11, 2, 8)`, d'où P = 11/13, R = 11/19 et F₁ = 22/32.

**`macro_f(cas, beta, vide)`** parcourt les cas. Quand `f_beta` renvoie `None`, le cas est soit exclu (`vide=None`, la valeur par défaut, et `exclus` augmente de 1), soit remplacé par la valeur annoncée (`vide=1.0`). La fonction renvoie la moyenne et le nombre d'exclus, pour que le rapport puisse publier les deux.

**`ancien_f1(tp, fp, fn)`** reproduit l'ancien code du fichier, qui renvoyait 0,0 dès qu'une division était impossible, pour mesurer l'effet de cette convention.

**`comptes_par_classe(vrais, predits)`** vérifie d'abord que les deux listes ont la même longueur, sinon `zip` couperait en silence. Elle parcourt ensuite les classes dans l'ordre trié, pour une sortie reproductible, et compte pour chacune les TP, les FP (prédite k, vraie autre) et les FN (vraie k, prédite autre).

**`main()`**, bloc par bloc.

1. D1 donne `Comptes(tp=2, fp=1, fn=0)`, puis P = 0,6667, R = 1 et F₁ = 0,8. On vérifie l'égalité des deux formes et l'encadrement de l'étape 50.
2. F₂ = 10/11 et F₀,₅ = 2,5/3,5 ; l'ordre F₀,₅ < F₁ < F₂ (point 2) ; les limites β → 0 et β → ∞, approchées avec β = 10⁻⁶ et β = 10⁴ ; et `Comptes(0, 3, 4)` qui donne bien 0.
3. Les quatre dossiers du tableau. D2 est fabriqué avec des noms `piece_00` à `piece_14` ; l'agent en réclame neuf justes plus `piece_inexistante`. On affiche P, R et F₁ par dossier, puis les trois moyennes macro (0,5067, 0,63 et 0,38) et la micro. Une dernière vérification recalcule la précision micro comme moyenne pondérée des précisions par cas (point 5).
4. Le routeur : 6 demandes de visa, 3 d'amende, 1 réclamation routée vers les visas. On vérifie que la somme des FP et celle des FN valent 1, que P, R et F₁ micro valent l'exactitude 0,9, et que la F1 macro vaut (12/13 + 1 + 0)/3.
5. Trois entrées invalides doivent lever `ValueError` ; si l'une passe, `raise AssertionError` arrête le programme.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Comptes.__post_init__()`** — Cette méthode est le contrôleur posté à la sortie de l'atelier, qui inspecte chaque fiche de comptes au moment même où elle est fabriquée : la dataclass figée l'appelle automatiquement juste après avoir rangé les trois compteurs TP, FP et FN, et elle ne reçoit donc aucun autre argument que l'objet lui-même. Elle vérifie que le plus petit des trois n'est pas négatif et lève une `ValueError` dans le cas contraire, parce qu'un compte négatif trahit un bug en amont et non une mesure ; elle ne renvoie rien, et `main` vérifie à la fin que `Comptes(-1, 0, 0)` est bien refusé.

**`comptes(attendus, predits)`** — Celle-ci est la vérificatrice qui pose côte à côte la liste des pièces qu'un dossier de crédit exigeait et celle que l'agent a réclamées : elle reçoit ces deux ensembles, compte leur intersection pour les vrais positifs, ce qui a été réclamé sans être attendu pour les faux positifs, et ce qui était attendu sans être réclamé pour les faux négatifs. Elle renvoie un objet `Comptes` : pour le dossier D1, deux pièces justes et un passeport réclamé à tort donnent `Comptes(tp=2, fp=1, fn=0)`, et pour D2, quinze pièces attendues contre neuf justes et une pièce inexistante donnent (9, 1, 6).

**`precision(c)`** — Cette fonction est l'auditrice qui ne regarde que ce que l'agent a réclamé : elle reçoit un objet `Comptes` et renvoie TP ÷ (TP + FP), la part des pièces réclamées qui étaient vraiment manquantes, ou `None` quand l'agent n'a rien réclamé du tout, au lieu d'un zéro qui fausserait les moyennes. Pour D1, elle vaut 2/3, soit 0,6667 ; pour D2, 0,9 ; pour D3 et D4, où rien n'a été réclamé, elle vaut `None`. Elle sert aussi aux moyennes micro et à la vérification finale, qui retrouve la précision micro comme moyenne des précisions par dossier pondérée par le nombre de réclamations.

**`rappel(c)`** — Celle-ci est l'inspecteur qui part de la liste des pièces réellement manquantes et vérifie qu'aucune n'a été oubliée : elle reçoit un objet `Comptes` et renvoie TP ÷ (TP + FN), ou `None` si rien n'était attendu, comme pour le dossier complet D3. Pour D1, les deux pièces attendues ont été réclamées et le rappel vaut 1 ; pour D2, neuf sur quinze donnent 0,6 ; pour D4, où l'agent n'a rien réclamé alors que deux pièces manquaient, il tombe à 0, et c'est ce zéro qui trahit l'oubli.

**`f_beta(c, beta)`** — Cette fonction est la balance réglable de l'évaluateur, qui décide combien un oubli pèse face à une réclamation superflue : elle reçoit un objet `Comptes` et β, 1 par défaut, lève `ValueError` si β n'est pas strictement positif, puis calcule la forme par les comptes, (1 + β²)TP ÷ ((1 + β²)TP + β²FN + FP), où chaque faux négatif pèse β² faux positifs. Elle ne renvoie `None` que pour le seul vrai cas vide, TP = FP = FN = 0 ; sinon elle donne 0,8 pour D1 en F1, 10/11 en F2 et 2,5/3,5 en F0,5, et 0 pour `Comptes(0, 3, 4)`, défini et nul dès qu'il y a une erreur sans aucun succès.

**`f_beta_par_taux(p, r, beta)`** — Celle-ci est le témoin de contrôle, la seconde méthode de calcul qu'un professeur demande pour vérifier la première : elle reçoit une précision, un rappel et β, renvoie 0 si les deux taux sont nuls, et sinon (1 + β²)PR ÷ (β²P + R), la forme classique du Fβ par les taux. Elle ne vérifie pas β et ne sait pas traiter un taux `None` ; elle ne sert dans `main` qu'à confirmer, par des `assert`, que pour D1 elle donne exactement le même nombre que `f_beta` avec β = 0,5, 1 et 2.

**`micro(cas, beta)`** — Cette fonction verse tous les dossiers dans un même grand panier avant de compter, comme un inspecteur qui additionne les registres de toutes les agences avant de calculer un seul taux : elle reçoit la liste des comptes et β, construit un `Comptes` total en sommant séparément les TP, les FP et les FN, puis renvoie le triplet précision, rappel et Fβ de ce total. Pour les quatre dossiers, le total vaut (11, 2, 8), d'où P = 11/13, R = 11/19 et F1 = 0,6875 ; pour le routeur d'intentions, la même fonction donne 0,9 pour les trois taux, exactement l'exactitude.

**`ancien_f1(tp, fp, fn)`** — Celle-ci est la vieille recette conservée dans un tiroir pour en montrer le défaut : elle reçoit les trois compteurs, remplace par 0 chaque taux dont le dénominateur est nul, puis renvoie la moyenne harmonique des deux taux, ou 0 si leur somme est nulle. Elle ne renvoie donc jamais `None`, si bien que le dossier complet D3, où il n'y avait rien à trouver ni rien à réclamer, reçoit la même note que l'échec total de D4 ; la macro-moyenne tombe alors à 0,38, au lieu de 0,5067 avec exclusion ou 0,63 avec un cas vide compté comme parfait.

**`main()`** — C'est le chef d'orchestre des cinq vérifications : il compte D1 à la main et vérifie P = 0,6667, R = 1 et F1 = 0,8 par les deux formes, montre ensuite qu'un faux négatif pèse β² faux positifs avec F2 = 10/11, F0,5 = 2,5/3,5 et les limites β → 0 et β → ∞. Il évalue ensuite les quatre dossiers de crédit, compare les trois macro-moyennes 0,5067, 0,63 et 0,38 à la micro 0,6875, puis compte un routeur de dix demandes où une réclamation part vers les visas, et vérifie que micro-P, micro-R et micro-F1 valent l'exactitude 0,9 ; trois entrées invalides doivent enfin lever `ValueError` avant le « OK ».

```python
"""Étape 56 — précision, rappel, F1 et Fβ en évaluation : cas vide, micro et macro, exactitude."""
import math
import sys
from dataclasses import dataclass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


@dataclass(frozen=True)
class Comptes:
    tp: int
    fp: int
    fn: int

    def __post_init__(self) -> None:
        if min(self.tp, self.fp, self.fn) < 0:
            raise ValueError("TP, FP et FN sont des entiers >= 0")


def comptes(attendus: set[str], predits: set[str]) -> Comptes:
    """Compare, pour un cas, ce qui était attendu à ce que le système a produit."""
    return Comptes(tp=len(attendus & predits), fp=len(predits - attendus), fn=len(attendus - predits))


def precision(c: Comptes) -> float | None:
    """TP / (TP + FP) ; None si le système n'a rien produit (0/0)."""
    return None if c.tp + c.fp == 0 else c.tp / (c.tp + c.fp)


def rappel(c: Comptes) -> float | None:
    """TP / (TP + FN) ; None si rien n'était attendu (0/0)."""
    return None if c.tp + c.fn == 0 else c.tp / (c.tp + c.fn)


def f_beta(c: Comptes, beta: float = 1.0) -> float | None:
    """(1 + β²)TP / ((1 + β²)TP + β²FN + FP) ; None seulement si TP = FP = FN = 0."""
    if beta <= 0:
        raise ValueError("il faut beta > 0")
    b2 = beta * beta
    denominateur = (1 + b2) * c.tp + b2 * c.fn + c.fp
    return None if denominateur == 0 else (1 + b2) * c.tp / denominateur


def f_beta_par_taux(p: float, r: float, beta: float = 1.0) -> float:
    """Forme par les taux, (1 + β²)PR / (β²P + R), pour vérifier qu'elle égale la forme par les comptes."""
    b2 = beta * beta
    return 0.0 if p == 0 and r == 0 else (1 + b2) * p * r / (b2 * p + r)


def micro(cas: list[Comptes], beta: float = 1.0) -> tuple[float | None, float | None, float | None]:
    """On additionne les comptes de tous les cas, puis on applique les formules une seule fois."""
    total = Comptes(sum(c.tp for c in cas), sum(c.fp for c in cas), sum(c.fn for c in cas))
    return precision(total), rappel(total), f_beta(total, beta)


def macro_f(cas: list[Comptes], beta: float = 1.0, vide: float | None = None) -> tuple[float | None, int]:
    """Moyenne des Fβ par cas. vide=None : un cas vide est exclu (défaut) ; vide=1.0 : il compte comme parfait.
    Renvoie (moyenne, nombre de cas exclus)."""
    valeurs, exclus = [], 0
    for c in cas:
        f = f_beta(c, beta)
        if f is None:
            if vide is None:
                exclus += 1
                continue
            f = vide
        valeurs.append(f)
    return (sum(valeurs) / len(valeurs) if valeurs else None), exclus


def ancien_f1(tp: int, fp: int, fn: int) -> float:
    """Ancien code du fichier : 0.0 dès qu'une division est impossible."""
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    return 2 * p * r / (p + r) if (p + r) else 0.0


def comptes_par_classe(vrais: list[str], predits: list[str]) -> dict[str, Comptes]:
    """Classification à une seule étiquette : une erreur est un FP pour la classe prédite et un FN pour la vraie."""
    if len(vrais) != len(predits):
        raise ValueError("autant de prédictions que de vraies étiquettes")
    res = {}
    for k in sorted(set(vrais) | set(predits)):
        tp = sum(1 for v, p in zip(vrais, predits) if v == k and p == k)
        fp = sum(1 for v, p in zip(vrais, predits) if v != k and p == k)
        fn = sum(1 for v, p in zip(vrais, predits) if v == k and p != k)
        res[k] = Comptes(tp, fp, fn)
    return res


def main() -> None:
    print("1. Exemple à la main : TP = 2, FP = 1, FN = 0")
    d1 = comptes({"releve_bancaire", "certificat_salaire"}, {"releve_bancaire", "certificat_salaire", "passeport"})
    p, r, f1 = precision(d1), rappel(d1), f_beta(d1)
    print(f"   {d1}  P = {p:.4f}  R = {r:.4f}  F1 = {f1:.4f}")
    assert (d1.tp, d1.fp, d1.fn) == (2, 1, 0)
    assert math.isclose(p, 2 / 3) and r == 1.0 and math.isclose(f1, 0.8)
    assert math.isclose(f1, f_beta_par_taux(p, r))                       # forme par les comptes = forme par les taux
    assert min(p, r) <= f1 <= (p + r) / 2                                 # étape 50

    print("2. Fβ : un FN pèse β² fois un FP")
    f2, f05 = f_beta(d1, 2.0), f_beta(d1, 0.5)
    print(f"   F2 = {f2:.4f} (= 10/11)   F0.5 = {f05:.4f} (= 2.5/3.5)")
    assert math.isclose(f2, 10 / 11) and math.isclose(f05, 2.5 / 3.5)
    for beta in (0.5, 2.0):
        assert math.isclose(f_beta(d1, beta), f_beta_par_taux(p, r, beta))
    assert f05 < f1 < f2                                                  # R > P : Fβ croît avec β
    assert math.isclose(f_beta(d1, 1e-6), p, rel_tol=1e-9)                # β → 0 : Fβ → P
    assert abs(f_beta(d1, 1e4) - r) < 1e-7                                # β → ∞ : Fβ → R
    assert f_beta(Comptes(0, 3, 4)) == 0.0                                # défini, et nul, dès qu'il y a une erreur

    print("3. Quatre dossiers de crédit : pièces manquantes attendues contre pièces réclamées")
    attendus_d2 = {f"piece_{i:02d}" for i in range(15)}
    predits_d2 = {f"piece_{i:02d}" for i in range(9)} | {"piece_inexistante"}
    dossiers = [
        d1,
        comptes(attendus_d2, predits_d2),                                 # TP = 9, FP = 1, FN = 6
        comptes(set(), set()),                                            # dossier complet, rien réclamé
        comptes({"emirates_id", "lettre_employeur"}, set()),              # l'agent ne réclame rien à tort
    ]
    for i, c in enumerate(dossiers, start=1):
        vals = [precision(c), rappel(c), f_beta(c)]
        txt = "  ".join("None  " if v is None else f"{v:.4f}" for v in vals)
        print(f"   D{i} TP={c.tp:>2} FP={c.fp} FN={c.fn}   P R F1 = {txt}".rstrip())
    assert dossiers[1] == Comptes(9, 1, 6) and math.isclose(f_beta(dossiers[1]), 0.72)
    assert f_beta(dossiers[2]) is None and precision(dossiers[3]) is None and f_beta(dossiers[3]) == 0.0

    mac, exclus = macro_f(dossiers)
    mac_un, _ = macro_f(dossiers, vide=1.0)
    mac_ancien = sum(ancien_f1(c.tp, c.fp, c.fn) for c in dossiers) / len(dossiers)
    mp, mr, mf = micro(dossiers)
    print(f"   macro-F1 : exclusion {mac:.4f} ({exclus} exclu)   vide = 1 {mac_un:.4f}   ancien code {mac_ancien:.4f}")
    print(f"   micro : P = {mp:.4f}  R = {mr:.4f}  F1 = {mf:.4f}  (11 TP, 2 FP, 8 FN)")
    assert exclus == 1 and math.isclose(mac, 1.52 / 3) and math.isclose(mac_un, 0.63) and math.isclose(mac_ancien, 0.38)
    assert math.isclose(mp, 11 / 13) and math.isclose(mr, 11 / 19) and math.isclose(mf, 0.6875)

    # micro-P = moyenne des P par cas pondérée par le nombre de prédictions (les cas sans prédiction pèsent 0)
    poids = [c.tp + c.fp for c in dossiers]
    pond = sum(w * precision(c) for w, c in zip(poids, dossiers) if w) / sum(poids)
    assert math.isclose(pond, mp)

    print("4. Routeur d'intentions : en classification à une étiquette, micro-P = micro-R = exactitude")
    vrais = ["visa"] * 6 + ["amende"] * 3 + ["reclamation"]
    predits = ["visa"] * 6 + ["amende"] * 3 + ["visa"]
    par_classe = comptes_par_classe(vrais, predits)
    exactitude = sum(v == q for v, q in zip(vrais, predits)) / len(vrais)
    up, ur, uf = micro(list(par_classe.values()))
    mf_cls, _ = macro_f(list(par_classe.values()))
    for k, c in par_classe.items():
        print(f"   {k:<12} TP={c.tp} FP={c.fp} FN={c.fn}  F1 = {f_beta(c):.4f}")
    print(f"   exactitude = {exactitude:.2f}   micro-F1 = {uf:.2f}   macro-F1 = {mf_cls:.4f}")
    assert sum(c.fp for c in par_classe.values()) == sum(c.fn for c in par_classe.values()) == 1
    assert up == ur == uf == exactitude == 0.9
    assert math.isclose(mf_cls, (12 / 13 + 1 + 0) / 3)

    print("5. Entrées invalides refusées")
    for fabrique in (lambda: Comptes(-1, 0, 0), lambda: f_beta(d1, 0.0), lambda: comptes_par_classe(["a"], [])):
        try:
            fabrique()
        except ValueError as e:
            print(f"   ValueError : {e}")
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Exemple à la main : TP = 2, FP = 1, FN = 0
   Comptes(tp=2, fp=1, fn=0)  P = 0.6667  R = 1.0000  F1 = 0.8000
2. Fβ : un FN pèse β² fois un FP
   F2 = 0.9091 (= 10/11)   F0.5 = 0.7143 (= 2.5/3.5)
3. Quatre dossiers de crédit : pièces manquantes attendues contre pièces réclamées
   D1 TP= 2 FP=1 FN=0   P R F1 = 0.6667  1.0000  0.8000
   D2 TP= 9 FP=1 FN=6   P R F1 = 0.9000  0.6000  0.7200
   D3 TP= 0 FP=0 FN=0   P R F1 = None    None    None
   D4 TP= 0 FP=0 FN=2   P R F1 = None    0.0000  0.0000
   macro-F1 : exclusion 0.5067 (1 exclu)   vide = 1 0.6300   ancien code 0.3800
   micro : P = 0.8462  R = 0.5789  F1 = 0.6875  (11 TP, 2 FP, 8 FN)
4. Routeur d'intentions : en classification à une étiquette, micro-P = micro-R = exactitude
   amende       TP=3 FP=0 FN=0  F1 = 1.0000
   reclamation  TP=0 FP=0 FN=1  F1 = 0.0000
   visa         TP=6 FP=1 FN=0  F1 = 0.9231
   exactitude = 0.90   micro-F1 = 0.90   macro-F1 = 0.6410
5. Entrées invalides refusées
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : une F1 « sur le jeu » n'existe pas tant qu'on n'a pas dit comment on agrège et ce qu'on fait des cas vides. Les mêmes quatre dossiers donnent 0,38, 0,51, 0,63 ou 0,69 selon ces deux choix.

## Squelette algorithmique

Deux algorithmes portent ce fichier, et un troisième, plus court, sert au routeur. Le premier prend un cas, c'est-à-dire l'ensemble des éléments attendus et l'ensemble des éléments produits, et rend ses trois compteurs, sa précision, son rappel et sa Fᵦ. Le deuxième prend les comptes de tous les cas du jeu et rend les moyennes micro et macro, avec le nombre de cas exclus. Le troisième compte, pour un routeur à une seule étiquette, les TP, FP et FN de chaque classe. L'idée commune est de ne jamais diviser avant d'avoir regardé le dénominateur : une division impossible donne INDÉFINI, jamais 0.

```text
ALGORITHME FBETA_D_UN_CAS
ENTRÉES : A, ensemble des éléments attendus ; P, ensemble des éléments produits ; β > 0
SORTIE  : (TP, FP, FN, précision, rappel, Fβ) ; les trois taux peuvent valoir INDÉFINI

  TP ← |A ∩ P|
  FP ← |P ∖ A|
  FN ← |A ∖ P|
  SI TP + FP = 0 ALORS précision ← INDÉFINI SINON précision ← TP / (TP + FP) FIN SI
  SI TP + FN = 0 ALORS rappel ← INDÉFINI SINON rappel ← TP / (TP + FN) FIN SI
  b2 ← β × β
  dénominateur ← (1 + b2) × TP + b2 × FN + FP
  SI dénominateur = 0 ALORS
      Fβ ← INDÉFINI                              ▷ cas vide : rien attendu, rien produit
  SINON
      Fβ ← (1 + b2) × TP / dénominateur
  FIN SI
  RETOURNER (TP, FP, FN, précision, rappel, Fβ)
```

```text
ALGORITHME AGRÉGER_MICRO_ET_MACRO
ENTRÉES : comptes (TPᵢ, FPᵢ, FNᵢ) de N cas ; β ; convention vide ∈ {EXCLURE, 1}
SORTIE  : (précision micro, rappel micro, Fβ micro, Fβ macro, nombre de cas exclus)

  ΣTP ← 0 ; ΣFP ← 0 ; ΣFN ← 0
  valeurs ← liste vide ; exclus ← 0
  POUR i de 1 à N FAIRE
      ΣTP ← ΣTP + TPᵢ ; ΣFP ← ΣFP + FPᵢ ; ΣFN ← ΣFN + FNᵢ
      f ← Fβ calculée sur (TPᵢ, FPᵢ, FNᵢ) comme dans FBETA_D_UN_CAS
      SI f = INDÉFINI ALORS
          SI vide = EXCLURE ALORS exclus ← exclus + 1 SINON ajouter 1 à valeurs FIN SI
      SINON
          ajouter f à valeurs
      FIN SI
  FIN POUR
  (précision micro, rappel micro, Fβ micro) ← formules de FBETA_D_UN_CAS sur (ΣTP, ΣFP, ΣFN)
  SI valeurs est vide ALORS Fβ macro ← INDÉFINI SINON Fβ macro ← Σ valeurs / |valeurs| FIN SI
  RETOURNER (précision micro, rappel micro, Fβ micro, Fβ macro, exclus)
```

```text
ALGORITHME COMPTES_PAR_CLASSE
ENTRÉES : vrais[1..N], prédits[1..N], une étiquette vraie et une étiquette prédite par requête
SORTIE  : pour chaque classe k, le triplet (TPₖ, FPₖ, FNₖ)

  SI longueur(vrais) ≠ longueur(prédits) ALORS ERREUR FIN SI
  POUR chaque classe k, dans l'ordre trié FAIRE
      TPₖ ← 0 ; FPₖ ← 0 ; FNₖ ← 0
      POUR i de 1 à N FAIRE
          SI vrais[i] = k ET prédits[i] = k ALORS TPₖ ← TPₖ + 1 FIN SI
          SI vrais[i] ≠ k ET prédits[i] = k ALORS FPₖ ← FPₖ + 1 FIN SI
          SI vrais[i] = k ET prédits[i] ≠ k ALORS FNₖ ← FNₖ + 1 FIN SI
      FIN POUR
  FIN POUR
  RETOURNER les triplets, classe par classe
```

**Complexité :** dans FBETA_D_UN_CAS, l'intersection et les deux différences d'ensembles coûtent O(|A| + |P|) en moyenne, parce que chaque élément d'un ensemble est cherché une fois dans l'autre et qu'une recherche dans une table de hachage prend un temps constant en moyenne ; tout le reste est un nombre fixe d'opérations, en O(1). La mémoire est en O(|A| + |P|) pour les ensembles intermédiaires, qu'on pourrait éviter en comptant sans les construire. AGRÉGER_MICRO_ET_MACRO fait un seul passage sur les N cas, avec un travail constant par cas, donc O(N) en temps ; la liste `valeurs` occupe O(N) en mémoire, ce qu'une somme courante et un compteur ramèneraient à O(1). Sur tout le jeu, la construction des comptes domine : O(Σ (|Aᵢ| + |Pᵢ|)). COMPTES_PAR_CLASSE, écrit comme dans le code, parcourt les N paires trois fois pour chacune des K classes : O(K × N) en temps et O(K) en mémoire. Un seul passage qui incrémente un dictionnaire indexé par classe donnerait O(N + K log K), le log venant du tri des classes ; la différence est invisible avec 3 intentions et 10 requêtes, mais avec 200 intentions et 100 000 requêtes, elle sépare 6 × 10⁷ tests de 10⁵.

**Du squelette au code :** les trois premières lignes de FBETA_D_UN_CAS sont la fonction `comptes(attendus, predits)`, où `&` calcule l'intersection et `-` les différences ; les deux lignes SI qui donnent la précision et le rappel sont `precision(c)` et `rappel(c)`, qui renvoient `None` pour INDÉFINI ; les lignes `b2`, `dénominateur` et le dernier SI sont `f_beta(c, beta)`, qui refuse en plus β ≤ 0 par `ValueError`. Dans AGRÉGER_MICRO_ET_MACRO, l'accumulation de ΣTP, ΣFP et ΣFN puis l'application des formules sont `micro(cas, beta)`, qui fait les trois sommes avec `sum` au lieu d'une boucle unique, pour la même complexité ; la boucle sur `valeurs` et `exclus` est `macro_f(cas, beta, vide)`, où la convention EXCLURE correspond à `vide=None` et la convention 1 à `vide=1.0`. COMPTES_PAR_CLASSE est `comptes_par_classe(vrais, predits)` : l'ERREUR est le `ValueError` sur les longueurs, l'ordre trié est `sorted(set(vrais) | set(predits))`, et chacune des trois lignes SI est l'un des trois `sum(1 for v, p in zip(vrais, predits) if …)`. La `dataclass` `Comptes`, qui refuse un compte négatif, n'apparaît pas dans le squelette : c'est une garde d'entrée, pas une étape de calcul.

## Cas d'usage réels aux Émirats

Les volumes, les taux et les seuils ci-dessous sont illustratifs ; seules les règles réglementaires citées sont réelles.

### Banque — les pièces manquantes d'un dossier de prêt personnel

Une banque de détail de Dubaï confie à un agent la première lecture des dossiers de prêt personnel : il liste les pièces manquantes (certificat de salaire, relevés bancaires, Emirates ID, lettre de l'employeur) avant qu'un conseiller ne valide. Ces pièces servent à vérifier les règles de la CBUAE : un ratio d'endettement total d'au plus 50 % du salaire, toutes mensualités comprises, un montant d'au plus 20 fois le salaire et une durée d'au plus 48 mois. Le back-office a étiqueté, pour chaque dossier d'un jeu de test, l'ensemble des pièces réellement manquantes ; un FP est une réclamation inutile, qui agace le client et retarde le dossier, un FN est un dossier transmis incomplet, sur lequel le ratio d'endettement ne peut pas être vérifié. Les dossiers d'entreprise, avec quinze pièces ou plus, dominent la micro, alors que l'expérience du client se juge dossier par dossier : la banque publie donc la F1 macro par type de dossier, et la micro seulement comme indicateur de charge du back-office. Un dossier complet pour lequel l'agent ne réclame rien est exclu de la macro et compté dans un taux d'abstention correcte, publié à côté ; sans cette convention, l'ancien calcul faisait paraître l'agent plus mauvais à mesure que les clients envoyaient des dossiers complets. Les indicateurs suivis sont la F1 macro par type de dossier, le taux d'abstention correcte et le nombre de dossiers exclus.

### Assurance — repérer les sinistres à faire examiner

Un assureur auto et santé fait relire chaque déclaration de sinistre par un agent qui liste les indices de fraude présents : facture en double, garage lié à l'assuré, date du sinistre proche de la souscription, pièces contradictoires. Les enquêteurs ont étiqueté un jeu de déclarations ; un FN est un indice manqué, qui peut conduire à un paiement indu, un FP est une enquête ouverte sur un assuré honnête. L'équipe choisit la F₂ avant toute mesure, parce qu'une enquête inutile coûte moins cher qu'un paiement frauduleux, mais elle publie aussi la précision, qui mesure la charge des enquêteurs. Avec une précision de 0,6 et un rappel de 0,9, la F₁ vaut 0,72 et la F₂ vaut 5 × 0,54 / (4 × 0,6 + 0,9) ≈ 0,818 : la F₂ récompense le choix d'un rappel élevé, et l'équipe le sait parce qu'elle a fixé β à partir des coûts et non des résultats. L'assureur est supervisé par la CBUAE, et la décision de refuser un sinistre reste humaine : l'agent ne fait qu'orienter la file des enquêteurs. Les indicateurs suivis sont la F₂ mensuelle sur un échantillon étiqueté et le nombre d'enquêtes ouvertes par enquêteur.

### Crypto — alerter un analyste ou geler un compte

Une plateforme d'actifs virtuels agréée par la VARA fait produire par un agent, pour chaque client et chaque journée, un ensemble d'alertes : fractionnement de dépôts, portefeuille lié à une adresse figurant sur une liste de sanctions, pic de volume inhabituel. Les mêmes alertes servent à deux actions de coûts opposés. Envoyer une alerte à un analyste de conformité coûte peu, et une alerte manquée coûte cher : l'équipe l'évalue en F₂. Geler automatiquement un compte bloque un client légitime si l'alerte est fausse : cette action est évaluée en F₀,₅. Sur un échantillon où TP = 8, FP = 4 et FN = 2, la forme par les comptes donne F₂ = 40/52 ≈ 0,769 et F₀,₅ = 10/14,5 ≈ 0,690 : la même liste d'alertes est assez bonne pour alerter, pas assez pour geler. La plateforme n'autorise donc le gel automatique que pour les types d'alerte dont la F₀,₅ dépasse le seuil fixé par la conformité, et envoie tous les autres vers un humain. Les indicateurs suivis sont la F₂ des alertes et la F₀,₅ des gels, type d'alerte par type d'alerte.

### RH — les éléments d'un calcul de fin de service

Un cabinet RH présent dans plusieurs émirats prépare, pour chaque départ d'un salarié du secteur privé, les éléments du calcul de l'indemnité de fin de service : salaire de base, date d'entrée, date de sortie, jours d'absence non payés. L'agent les extrait du dossier sous forme de paires champ = valeur, et la vérité terrain contient les bonnes paires. Une erreur de valeur compte deux fois : extraire le salaire total, allocations comprises, au lieu du salaire de base produit une paire fausse (un FP) et laisse la bonne paire manquante (un FN). L'enjeu est direct : pour dix ans de service et un salaire de base de 10 000 AED, l'indemnité vaut 5 × 21 + 5 × 30 jours de salaire, soit 85 000 AED, alors qu'un salaire total de 15 000 AED pris à tort donnerait 127 500 AED. Le régime du décret-loi fédéral 33/2021 ne s'applique ni aux ressortissants émiriens, qui relèvent de la GPSSA, ni aux salariés du DIFC, qui ont leur propre régime : l'agent doit aussi extraire ces deux indicateurs, et un oubli y vaut un FN. Les indicateurs suivis sont la F1 micro sur les paires champ = valeur et le rappel du seul champ « salaire de base », publié à part.

### BTP — des clauses absentes dans beaucoup de contrats

Un groupe de construction qui travaille sur de grands chantiers à Dubaï fait extraire par un agent, de chaque contrat de sous-traitance, les clauses sensibles : retenue de garantie, pénalités de retard, mention de la TVA à 5 %, conditions de paiement. Une bonne partie des bons de commande ne contient aucune de ces clauses, et l'agent a raison de ne rien extraire : ce sont des cas vides. Si, sur les cas définis, la F1 moyenne vaut 0,75 et que 40 % des documents sont vides, l'exclusion donne 0,75, la convention du score de 1 donne 0,6 × 0,75 + 0,4 = 0,85 et l'ancien calcul donne 0,6 × 0,75 = 0,45. Le même agent passe donc de « mauvais » à « excellent » selon une ligne de code que personne n'a lue. Le groupe retient l'exclusion, publie la part de documents vides, et mesure à part le taux de documents vides sur lesquels l'agent invente une clause, qui est le vrai risque : une retenue de garantie inventée bloque un paiement dû au sous-traitant. Les indicateurs suivis sont la F1 macro sur les contrats qui ont au moins une clause et le taux de clauses inventées sur les documents vides.

### Secteur public — un routeur d'intentions bilingue

Un service public en ligne accessible par UAE Pass reçoit des demandes en arabe et en anglais, qu'un routeur oriente vers une intention : renouvellement de visa, paiement d'une amende, réclamation, et d'autres. Chaque demande a une seule intention : l'exactitude, la précision micro, le rappel micro et la F1 micro valent alors exactement le même nombre (démonstration, point 6). Sur un échantillon, l'exactitude atteint 0,90 alors que les réclamations, rares, partent toutes vers les visas : la F1 de la classe « réclamation » vaut 0 et la F1 macro tombe à 0,641. L'équipe publie donc la F1 macro et le rappel de chaque classe, séparément en arabe et en anglais, et refuse toute version dont le rappel des réclamations baisse, parce qu'une réclamation mal routée n'arrive jamais à un agent humain. Les demandes contiennent des données personnelles soumises à la PDPL : le jeu d'évaluation est construit sur des demandes anonymisées. Les indicateurs suivis sont la F1 macro par langue et le rappel des classes rares.

## Pièges et limites

- **Renvoyer 0 pour 0/0.** C'est punir l'agent quand il a raison de ne rien faire ; on renvoie `None`, on exclut le cas ou on annonce le score de 1, et l'on publie le nombre de cas concernés.
- **Ne pas dire si la moyenne est micro ou macro.** Deux équipes qui comparent « leur F1 » peuvent comparer deux mesures différentes ; on écrit l'agrégation, et la définition de la F1 macro, dans le rapport.
- **Choisir β après avoir vu les résultats.** β se déduit du rapport des coûts d'un oubli et d'une fausse alerte, avant la mesure.
- **Ne publier que la F1.** Une F1 de 0,8 peut venir de P = 0,67 et R = 1, ou de P = 1 et R = 0,67 : deux agents très différents. On publie toujours P et R à côté.
- **Compter des ensembles là où les répétitions comptent.** Un appel d'outil fait deux fois ou une alerte levée deux fois disparaît dans un `set` ; l'étape 59 passe aux multi-ensembles.

### Exercice feuille blanche

1. Sans regarder le code, écrire `f_beta` sous la forme par les comptes, avec `None` pour le seul cas vide, puis vérifier 0,8, 10/11 et 2,5/3,5 sur TP = 2, FP = 1, FN = 0.
2. Prédire, puis vérifier : avec TP = 3, FP = 0 et FN = 3, que valent P, R, F₁ et F₂ ? (Réponse : 1 ; 0,5 ; 6/9 ≈ 0,667 ; 15/27 ≈ 0,556.) Quelle est la F1 macro des deux cas « TP = 2, FP = 1, FN = 0 » et « vide », avec l'exclusion, puis avec le score de 1 ? (Réponse : 0,8, puis 0,9.)
3. Trouver le bug : `micro = sum(precision(c) for c in cas) / len(cas)`. Que calcule réellement cette ligne, et pourquoi plante-t-elle sur les dossiers D3 et D4 ?

## Pour aller plus loin

La moyenne macro pondérée donne à chaque classe un poids proportionnel à son nombre d'exemples ; elle se situe entre la micro et la macro. Les bibliothèques d'évaluation exposent souvent un paramètre qui fixe la valeur rendue pour 0/0 (dans scikit-learn, `zero_division`) : il faut le lire, parce que sa valeur par défaut décide de la convention du cas vide à votre place. Quand l'agent produit un score et non un oui ou non, on trace la courbe précision-rappel en faisant varier le seuil, et on la résume par la précision moyenne de l'[étape 61](<61-Evaluation-Formule-MAP.md>).

> Suite : [Context Precision](<57-Evaluation-Formule-Context-Precision.md>) — étape 57.
