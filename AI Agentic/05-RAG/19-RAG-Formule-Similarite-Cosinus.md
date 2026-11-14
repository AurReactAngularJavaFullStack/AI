# Étape 19 — RAG — Similarité Cosinus

> Étape 19 du parcours · Prérequis : [Formules et algorithmes du RAG](<18-RAG-Formules-Theoremes-Algorithmes.md>) · Suite : [Distance euclidienne](<20-RAG-Formule-Distance-Euclidienne.md>)

**Dossier :** 05-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers, Product Engineers  
**Nom du fichier :** 19-RAG-Formule-Similarite-Cosinus.md

## Définition

La similarité cosinus est la métrique centrale du retrieval sémantique dans les systèmes RAG : elle mesure l'angle entre deux vecteurs d'embeddings, celui de la question et celui d'un passage. Elle ne dépend que de la direction des vecteurs, pas de leur longueur (leur norme), ce que l'étape 14 démontre. Son résultat est un nombre entre −1 et 1, mais ce nombre ne dit rien à lui seul : 0,82 peut être un excellent score pour un modèle d'embedding et un score médiocre pour un autre. Ce fichier traite donc la question que pose tout agent en production : à partir de quel score un passage est-il assez proche pour être utilisé ? La réponse est un seuil, et ce seuil n'appartient pas à la formule : il appartient au modèle d'embedding, et il se calibre sur des paires étiquetées.

## Rôle dans un agent

Le cosinus sert deux fois dans la boucle percevoir → décider → agir → observer. Dans le **retriever**, il classe les passages et garde les k meilleurs (étape 18). Juste après, dans une **garde de décision**, l'agent compare le meilleur score à deux seuils : au-dessus du seuil haut, il poursuit et répond en citant le passage ; sous le seuil bas, il ne devine pas et demande une précision à l'utilisateur ; entre les deux, il élargit la recherche (recherche hybride, reranker) ou passe la main à un humain. C'est ce routage qui transforme un score continu en action, et c'est lui qui casse quand le seuil est mal réglé : trop bas, l'agent répond à partir de passages hors sujet ; trop haut, il harcèle l'utilisateur de questions. Le calibrage se fait hors ligne, sur un jeu de paires jugées par des humains, et se refait à chaque changement de modèle d'embedding.

## Équation complète

La similarité cosinus entre deux vecteurs a et b de dimension n :

$$
\cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\lVert \mathbf{a} \rVert \, \lVert \mathbf{b} \rVert} = \frac{\sum_{i=1}^{n} a_i b_i}{\sqrt{\sum_{i=1}^{n} a_i^2} \cdot \sqrt{\sum_{i=1}^{n} b_i^2}}
$$

Un passage de score s est déclaré pertinent quand s ≥ τ. Sur m paires étiquetées, on compte les vrais positifs TP, les faux positifs FP et les faux négatifs FN au seuil τ, puis :

$$
F_1(\tau) = \frac{2\,TP(\tau)}{2\,TP(\tau) + FP(\tau) + FN(\tau)}
$$

Le seuil calibré est celui qui maximise F₁ parmi les scores observés :

$$
\tau^{*} = \underset{\tau \in \{s_1, \dots, s_m\}}{\arg\max} \; F_1(\tau)
$$

La garde de décision, appliquée au meilleur score s_max d'une question :

$$
\text{décision} = \begin{cases} \text{poursuivre} & \text{si } s_{max} \ge \tau_{haut} \\ \text{élargir ou reclasser} & \text{si } \tau_{bas} \le s_{max} < \tau_{haut} \\ \text{demander une précision} & \text{si } s_{max} < \tau_{bas} \end{cases}
$$

## Décryptage des symboles

$$
\theta
$$

L'angle entre les deux vecteurs, de 0° à 180° : plus il est petit, plus les textes sont proches pour le modèle (0° donne un cosinus de 1, 90° un cosinus de 0) ; il n'a pas de variable Python, car `cosinus` renvoie directement son cosinus.

$$
\mathbf{a}, \ \mathbf{b}
$$

Les deux vecteurs d'embeddings comparés, en général la requête et un passage, ou deux passages : des listes de n réels, `a` et `b` dans le code.

$$
a_i, \ b_i
$$

La i-ème composante de chaque vecteur, c'est-à-dire une dimension de l'espace sémantique appris par le modèle d'embedding ; i va de 1 à n en maths et de 0 à n − 1 en Python, où ces composantes s'appellent `x` et `y` dans les boucles.

$$
\mathbf{a} \cdot \mathbf{b}
$$

Le produit scalaire, somme des produits terme à terme : il mesure l'alignement brut mais mélange direction et longueur, si bien qu'un grand produit scalaire peut venir de vecteurs simplement longs ; un réel quelconque, calculé par `sum(x * y for x, y in zip(a, b))`.

$$
\lVert \mathbf{a} \rVert
$$

La norme euclidienne (la longueur) de a, qui vaut √(∑ aᵢ²) : un réel positif, nul seulement pour le vecteur nul ; la division par les deux normes rend le score indépendant de la longueur, et ces normes s'appellent `na` et `nb` dans `cosinus`.

$$
n
$$

La dimension de l'espace d'embedding, souvent 384, 768, 1536 ou 3072 selon le modèle : un entier, `len(a)`.

$$
s
$$

Le score cosinus d'une paire (question, passage), un réel compris entre −1 et 1 : un élément de `MODELE_A` ou de `MODELE_B`.

$$
\tau
$$

Le seuil de décision : une paire est déclarée pertinente quand s ≥ τ ; un réel, `tau` dans le code.

$$
TP, \ FP, \ FN
$$

Les vrais positifs (paires pertinentes acceptées), les faux positifs (paires non pertinentes acceptées) et les faux négatifs (paires pertinentes rejetées) au seuil τ : des entiers positifs ou nuls, renvoyés par `comptes(scores, etiquettes, tau)`.

$$
F_1
$$

La moyenne harmonique de la précision et du rappel, comprise entre 0 et 1 et indéfinie s'il n'y a ni paire pertinente ni paire acceptée : `f1(tp, fp, fn)`, qui renvoie alors `None`.

$$
\tau^{*}
$$

Le seuil calibré, celui qui maximise F₁ sur les paires étiquetées : c'est toujours l'un des scores observés, renvoyé par `calibrer(scores, etiquettes)`.

$$
m
$$

Le nombre de paires étiquetées, 12 dans le code et plutôt quelques centaines en production : `len(ETIQUETTES)`.

$$
\mu, \ \mathbf{u}
$$

Une direction commune u, de norme 1, que le modèle ajoute à tous ses vecteurs avec l'intensité μ ≥ 0 (démonstration, point 4) : `mu` dans le code.

$$
\tau_{haut}, \ \tau_{bas}
$$

Les deux seuils de la garde de décision, 0,85 et 0,60 pour le modèle A (valeurs illustratives) : les paramètres `haut` et `bas` de `decision`.

$$
s_{max}
$$

Le meilleur score parmi les passages récupérés pour une question : l'argument `score_max` de `decision`.

## Démonstration

### 1. Bornes et invariance d'échelle : renvoi à l'étape 14

L'étape 14 démontre, par le discriminant d'un trinôme, l'inégalité de Cauchy-Schwarz |a · b| ≤ ‖a‖ ‖b‖, d'où −1 ≤ cos θ ≤ 1, avec égalité si et seulement si les vecteurs sont colinéaires. Elle démontre aussi que multiplier un vecteur par un nombre λ > 0 ne change pas le cosinus, et qu'un λ < 0 change seulement son signe. On s'en sert ici sans refaire les preuves. Une conséquence compte pour la suite : l'invariance d'échelle protège contre un vecteur multiplié par une constante, mais pas contre un vecteur auquel on ajoute une direction commune, et c'est ce second effet qui rend les seuils propres à chaque modèle (point 4).

### 2. Démonstration chiffrée et interprétation

Les vecteurs sont q = (0,8 ; 0,3 ; 0,5) pour la requête « choc parking » et d = (0,7 ; 0,4 ; 0,6) pour une clause de contrat. L'ancienne version de ce fichier renvoyait à des « calculs précédents » qui n'y figuraient pas, et son doublon plaçait du texte français à l'intérieur des formules ; voici le calcul complet.

Étape 1, le produit scalaire : les deux vecteurs partagent beaucoup de direction commune.

$$
\mathbf{q} \cdot \mathbf{d} = 0{,}8 \times 0{,}7 + 0{,}3 \times 0{,}4 + 0{,}5 \times 0{,}6 = 0{,}56 + 0{,}12 + 0{,}30 = 0{,}98
$$

Étape 2, la norme de la requête :

$$
\lVert \mathbf{q} \rVert = \sqrt{0{,}64 + 0{,}09 + 0{,}25} = \sqrt{0{,}98} \approx 0{,}990
$$

Étape 3, la norme de la clause :

$$
\lVert \mathbf{d} \rVert = \sqrt{0{,}49 + 0{,}16 + 0{,}36} = \sqrt{1{,}01} \approx 1{,}005
$$

Étape 4, la similarité :

$$
\cos(\theta) = \frac{0{,}98}{0{,}990 \times 1{,}005} \approx \frac{0{,}98}{0{,}995} \approx 0{,}985
$$

**Interprétation du résultat.** Un score de 0,985 signifie que, pour ce modèle, les deux textes sont extrêmement proches : dans un système d'assurance, cela justifie de présenter cette clause en priorité à l'agent. Si le score était de 0,3, on considérerait le passage comme peu pertinent et on ne le passerait pas au LLM. Ces deux lectures supposent qu'on connaît la distribution des scores du modèle : avec le modèle B du point 4, aucun score ne descend sous 0,83, et 0,85 y est le score d'une paire non pertinente.

### 3. Calibrer un seuil : maximiser F₁ sur des paires étiquetées

Un humain juge m paires (question, passage), pertinente ou non. Pour un seuil τ, on accepte les paires de score s ≥ τ et l'on compte TP, FP et FN. La précision P = TP / (TP + FP) dit quelle part des paires acceptées est pertinente ; le rappel R = TP / (TP + FN) dit quelle part des paires pertinentes est acceptée ; F₁ est leur moyenne harmonique, et l'étape 50 démontre leurs propriétés. La forme utilisée dans le code, sans division intermédiaire, vient d'un calcul direct, valable quand TP > 0 :

$$
F_1 = \frac{2PR}{P + R} = \frac{2 \cdot \frac{TP}{TP+FP} \cdot \frac{TP}{TP+FN}}{\frac{TP}{TP+FP} + \frac{TP}{TP+FN}} = \frac{2\,TP^2}{TP\,(TP+FN) + TP\,(TP+FP)} = \frac{2\,TP}{2\,TP + FP + FN}
$$

On passe à la troisième expression en multipliant le haut et le bas par (TP + FP)(TP + FN), puis à la dernière en simplifiant par TP. Cette dernière forme reste définie quand la précision ne l'est pas, c'est-à-dire quand aucune paire n'est acceptée : elle vaut alors 0 dès qu'il existe au moins une paire pertinente.

**Pourquoi il suffit d'essayer les scores observés.** Rangeons les scores distincts dans l'ordre décroissant, s₍₁₎ > s₍₂₎ > … Pour un seuil τ pris entre deux scores consécutifs, s₍ⱼ₊₁₎ < τ ≤ s₍ⱼ₎, les paires acceptées sont exactement celles de score ≥ s₍ⱼ₎, parce qu'aucun score observé ne tombe dans l'intervalle. TP, FP, FN, et donc F₁, sont constants sur tout cet intervalle et égaux à leur valeur en τ = s₍ⱼ₎. Au-dessus du plus grand score, rien n'est accepté et F₁ vaut 0 ; au-dessous du plus petit, tout est accepté, comme au plus petit score. La fonction τ ↦ F₁(τ) est donc en escalier, et son maximum sur tous les réels est atteint en l'un des m scores observés : balayer ces scores est exhaustif. À F₁ égal, on garde le seuil le plus haut, qui est le plus prudent.

Pour le modèle A, sur 12 paires dont 6 pertinentes :

| Seuil τ | TP | FP | FN | F₁ |
|---|---|---|---|---|
| 0,95 | 1 | 0 | 5 | 2/7 = 0,2857 |
| 0,91 | 2 | 0 | 4 | 4/8 = 0,5 |
| 0,88 | 3 | 0 | 3 | 6/9 = 0,6667 |
| 0,86 | 4 | 0 | 2 | 8/10 = 0,8 |
| 0,84 | 4 | 1 | 2 | 8/11 = 0,7273 |
| **0,82** | **5** | **1** | **1** | **10/12 = 0,8333** |
| 0,79 | 5 | 2 | 1 | 10/13 = 0,7692 |
| 0,70 | 6 | 3 | 0 | 12/15 = 0,8 |

Le meilleur seuil du modèle A est 0,82, avec F₁ = 0,8333 : précision et rappel valent tous deux 5/6. Le code essaie aussi 113 seuils de 0,40 à 0,96 par pas de 0,005, et aucun ne fait mieux, comme la démonstration l'annonce. L'ancienne version proposait un seuil de 0,82 et son doublon un seuil de 0,85, sans dire d'où venaient ces nombres : les deux peuvent être justes, chacun pour son modèle et son jeu de paires, et sur ce jeu-ci, le modèle A a justement son meilleur F₁ à 0,82.

### 4. Pourquoi un seuil ne se transporte pas d'un modèle à l'autre

On fait noter les mêmes 12 paires par un modèle B, dont tous les scores tombent entre 0,83 et 0,97. Appliquer le seuil de A, 0,82, revient à tout accepter : TP = 6, FP = 6, FN = 0, F₁ = 12/18 = 0,6667, et une réponse sur deux s'appuie sur un passage non pertinent. Recalibré, B a son meilleur seuil à 0,91, avec F₁ = 12/13 = 0,9231 : il sépare mieux les paires que A, mais dans une autre plage de scores. Inversement, le seuil de B appliqué à A n'accepte que deux paires et donne F₁ = 0,5. La formule du cosinus est la même ; ce qui a changé, c'est la fonction qui transforme un texte en vecteur.

La raison mathématique est l'anisotropie (étape 15) : beaucoup de modèles placent tous leurs vecteurs dans un cône étroit, comme s'ils ajoutaient à chacun une même direction. Prenons deux textes sans rapport, représentés par des vecteurs a et b de norme 1 et orthogonaux, et une direction u de norme 1, orthogonale aux deux. Si le modèle ajoute μu à chaque vecteur :

$$
\cos(\mathbf{a} + \mu\mathbf{u}, \ \mathbf{b} + \mu\mathbf{u}) = \frac{\mathbf{a}\cdot\mathbf{b} + \mu\,\mathbf{a}\cdot\mathbf{u} + \mu\,\mathbf{u}\cdot\mathbf{b} + \mu^2\,\mathbf{u}\cdot\mathbf{u}}{\lVert \mathbf{a} + \mu\mathbf{u} \rVert \, \lVert \mathbf{b} + \mu\mathbf{u} \rVert} = \frac{\mu^2}{1 + \mu^2}
$$

Le numérateur se réduit à μ², parce que a · b = a · u = u · b = 0 et u · u = 1 ; chaque norme vaut √(1 + μ²) par le théorème de Pythagore, puisque a et μu sont orthogonaux. Avec μ = 0, on retrouve 0 ; avec μ = 1, deux textes sans rapport obtiennent 0,5 ; avec μ = 2, ils obtiennent 0,8, presque le seuil calibré de A. Le niveau « de fond » des cosinus est donc une propriété du modèle, et l'invariance d'échelle n'y peut rien : normaliser les vecteurs ne retire pas la direction commune. Le recentrage de l'étape 15, qui soustrait le vecteur moyen du corpus, la retire.

### 5. Les zones de décision

Le doublon de ce fichier proposait deux seuils : au-dessus de 0,85 sur le meilleur passage, l'agent poursuit ; en dessous de 0,6, il demande une clarification ou passe la main. Ces valeurs ont un sens pour le modèle A : un meilleur passage à 0,985 fait poursuivre, un meilleur passage à 0,72 tombe en zone grise, où l'agent élargit la recherche ou reclasse les candidats, et un meilleur passage à 0,41 déclenche une question à l'utilisateur. Avec le modèle B, dont le plus petit score vaut 0,83, la zone « demander une précision » ne serait jamais atteinte : l'agent répondrait toujours, même sans bon passage. Les deux seuils se calibrent donc avec le modèle, par exemple le seuil haut par le balayage du F₁ et le seuil bas en visant un rappel minimal.

## Effets et comportement

- **Plus le produit scalaire augmente** par rapport au produit des normes, plus le score se rapproche de 1 et plus le passage est jugé pertinent.
- **Plus les vecteurs divergent**, plus le score baisse : vers 0 quand ils deviennent orthogonaux, jusqu'à −1 quand ils sont opposés. L'ancienne version s'arrêtait à « vers 0 ».
- **Plus les normes augmentent** sans que le produit scalaire augmente autant, plus le score diminue : c'est l'effet de la normalisation.
- **Un vecteur nul n'a pas de cosinus.** Le doublon le « définissait à 0 » et l'ancienne version ajoutait 1e-8 au dénominateur : dans les deux cas, une panne d'embedding passe pour un passage « sans rapport ». Le code lève `ValueError`.
- **Ajouter des dimensions bruitées** allonge les normes sans augmenter le produit scalaire : le score baisse si le signal utile n'est pas renforcé.
- **Monter le seuil τ** ne peut que diminuer le rappel, parce que l'ensemble des paires acceptées rétrécit ; la précision, elle, n'est pas forcément monotone : dans le tableau, elle passe de 1 à 0,8 entre les seuils 0,86 et 0,84, puis remonte à 5/6 au seuil 0,82.

## Du symbole au code Python

| Notion | Variable ou fonction |
|---|---|
| cosinus de deux vecteurs | `cosinus(a, b)` |
| comptes TP, FP, FN au seuil τ | `comptes(scores, etiquettes, tau)` |
| F₁ | `f1(tp, fp, fn)` |
| seuil calibré τ* | `calibrer(scores, etiquettes)` |
| garde de décision | `decision(score_max, haut, bas)` |
| étiquettes humaines et scores des deux modèles | `ETIQUETTES`, `MODELE_A`, `MODELE_B` |

### Déroulé, ligne par ligne

**`cosinus(a, b)`** est la fonction canonique du parcours, en Python standard. Elle refuse deux vecteurs de dimensions différentes, calcule les deux normes, lève `ValueError` si l'une est nulle, puis rabat le quotient dans l'intervalle de −1 à 1 contre les arrondis. Elle remplace la version NumPy de l'ancien fichier, qui ajoutait 1e-8 au dénominateur et renvoyait donc 0 pour un vecteur nul sans rien signaler ; cette version NumPy, corrigée, figure plus bas comme extrait. Sur la requête « choc parking », le produit scalaire vaut 0,98, les normes 0,990 et 1,005, et le cosinus 0,985.

**`comptes(scores, etiquettes, tau)`** parcourt les paires deux listes en parallèle avec `zip` et compte trois cas : score ≥ τ et paire pertinente (TP), score ≥ τ et paire non pertinente (FP), score < τ et paire pertinente (FN). Pour le modèle A au seuil 0,82, les paires acceptées ont les scores 0,95 ; 0,91 ; 0,88 ; 0,86 ; 0,84 et 0,82 : cinq sont pertinentes, celle à 0,84 ne l'est pas, et la paire pertinente à 0,70 est rejetée, d'où (5, 1, 1).

**`f1(tp, fp, fn)`** calcule le dénominateur `d = 2 * tp + fp + fn`, renvoie `None` s'il est nul (ni paire pertinente ni paire acceptée), sinon `2 * tp / d`. Pour (5, 1, 1), cela donne 10/12, soit 0,8333.

**`calibrer(scores, etiquettes)`** applique la démonstration du point 3.

- `sorted(set(scores), reverse=True)` : les scores distincts, du plus haut au plus bas ; ce sont les seuls seuils qu'il faut essayer.
- Pour chaque seuil, F₁ est calculé à partir de `comptes`.
- `if valeur is not None and valeur > meilleur_f1` : l'inégalité stricte garde le premier maximum rencontré ; comme on descend, c'est le seuil le plus haut parmi les ex aequo.
- Pour le modèle A, la fonction renvoie (0,82 ; 0,8333) ; pour le modèle B, (0,91 ; 0,9231).

**`decision(score_max, haut, bas)`** traduit la garde de décision en trois branches : `poursuivre` si le meilleur score atteint le seuil haut, `demander une précision` s'il reste sous le seuil bas, et la zone grise entre les deux.

**`ETIQUETTES`, `MODELE_A`, `MODELE_B`** décrivent les mêmes douze paires, dans le même ordre : les étiquettes humaines (1 pertinent, 0 non pertinent) et les scores donnés par deux modèles d'embedding. Ces nombres sont illustratifs : ils sont choisis pour que chaque calcul se refasse à la main.

**`main()`**, bloc par bloc.

1. La démonstration chiffrée du point 2 : 0,98 ; 0,990 ; 1,005 et 0,985, puis le refus du vecteur nul, vérifié par `try / except / else`.
2. Le balayage du modèle A : les sept premiers seuils sont imprimés avec leurs comptes, et le tableau du point 3 est vérifié valeur par valeur. Le meilleur seuil vaut 0,82.
3. La preuve en escalier est vérifiée sur 113 seuils de 0,40 à 0,96 : chacun donne les mêmes comptes que le plus petit score observé qui lui est supérieur ou égal, et aucun ne dépasse F₁ = 0,8333.
4. Le transport du seuil : 0,82 appliqué à B accepte tout (6, 6, 0) et donne 0,6667 ; B recalibré donne 0,91 et 0,9231 ; le seuil de B appliqué à A donne 0,5.
5. L'anisotropie : pour μ = 0, 1 et 2, le cosinus calculé égale μ²/(1 + μ²), soit 0, 0,5 et 0,8.
6. Les zones de décision du modèle A sur trois meilleurs scores, puis la vérification que le modèle B n'atteindrait jamais la zone basse. Les derniers `assert` vérifient, sans rien afficher, les réponses des exercices 2 et 3.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`f1(tp, fp, fn)`** — On peut se représenter un examinateur qui note d'un seul chiffre un détecteur à la fois trop bavard et trop distrait : la fonction reçoit les nombres de vrais positifs, de faux positifs et de faux négatifs, calcule le dénominateur 2 TP + FP + FN, et renvoie `None` quand il est nul, c'est-à-dire quand il n'y avait ni paire pertinente ni paire acceptée et que la note n'aurait aucun sens. Sinon elle renvoie 2 TP divisé par ce dénominateur, un nombre entre 0 et 1 qui punit autant les fausses alertes que les oublis ; pour les comptes (5, 1, 1) du modèle A au seuil 0,82, elle donne 10/12, soit 0,8333.

**`calibrer(scores, etiquettes)`** — Cette fonction se conduit comme un accordeur qui essaie, une à une, toutes les positions possibles d'une cheville avant de garder la plus juste : elle reçoit les scores cosinus des paires et leurs étiquettes humaines, parcourt les scores distincts du plus haut au plus bas en les prenant chacun comme seuil, fait calculer les comptes par `comptes` puis la note par `f1`, et ne retient un nouveau seuil que si sa note dépasse strictement la meilleure déjà vue. Comme elle descend, ce choix strict garde, en cas d'égalité, le seuil le plus haut, donc le plus prudent ; elle renvoie le couple (seuil, F₁), soit (0,82 ; 0,8333) pour le modèle A et (0,91 ; 0,9231) pour le modèle B, et (`None`, −1,0) si on ne lui donne aucun score.

**`decision(score_max, haut, bas)`** — C'est l'aiguilleur posté à la sortie de la recherche, qui regarde le meilleur score obtenu et envoie l'agent sur l'une de trois voies : la fonction reçoit ce score maximal, un seuil haut et un seuil bas, renvoie « poursuivre » si le score atteint le seuil haut, « demander une précision » s'il reste strictement sous le seuil bas, et sinon la phrase de la zone grise, qui conseille d'élargir la recherche ou de reclasser. Avec les seuils 0,85 et 0,60 du programme, un meilleur passage à 0,985 fait poursuivre, un passage à 0,72 tombe dans la zone grise et un passage à 0,41 déclenche la question de précision.

**`main()`** — Le chef d'orchestre enchaîne six démonstrations : il recalcule d'abord le cosinus 0,985 de la requête « choc parking » et vérifie que le vecteur nul est refusé, puis balaie les seuils du modèle A, imprime les sept premiers avec leurs comptes et vérifie que le meilleur vaut 0,82 pour un F₁ de 0,8333. Il prouve ensuite sur 113 seuils de 0,40 à 0,96 que F₁ reste constant entre deux scores observés, montre que le seuil 0,82 transporté sur le modèle B fait tomber F₁ à 0,6667 alors que B recalibré atteint 0,9231, illustre l'anisotropie avec les cosinus 0, 0,5 et 0,8 obtenus pour μ = 0, 1 et 2, puis teste les trois zones de décision. Des `assert` silencieux vérifient enfin les réponses des exercices 2 et 3, et la dernière ligne n'annonce le succès que si tous ont tenu.

```python
"""Étape 19 — similarité cosinus : calcul, interprétation, et calibrage du seuil de décision par le F1."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def cosinus(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("dimensions différentes")
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        raise ValueError("vecteur nul : le cosinus n'est pas défini")
    return max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b)) / (na * nb)))


def comptes(scores: list[float], etiquettes: list[int], tau: float) -> tuple[int, int, int]:
    """Prédit « pertinent » quand score >= tau ; renvoie (vrais positifs, faux positifs, faux négatifs)."""
    tp = sum(1 for s, e in zip(scores, etiquettes) if s >= tau and e == 1)
    fp = sum(1 for s, e in zip(scores, etiquettes) if s >= tau and e == 0)
    fn = sum(1 for s, e in zip(scores, etiquettes) if s < tau and e == 1)
    return tp, fp, fn


def f1(tp: int, fp: int, fn: int) -> float | None:
    """F1 = 2TP / (2TP + FP + FN) ; None s'il n'y a ni pertinent ni prédiction."""
    d = 2 * tp + fp + fn
    return None if d == 0 else 2 * tp / d


def calibrer(scores: list[float], etiquettes: list[int]) -> tuple[float, float]:
    """Essaie chaque score observé comme seuil, du plus haut au plus bas ; garde le meilleur F1.
    À F1 égal, le premier rencontré, donc le seuil le plus haut (le plus prudent), gagne."""
    meilleur_tau, meilleur_f1 = None, -1.0
    for tau in sorted(set(scores), reverse=True):
        valeur = f1(*comptes(scores, etiquettes, tau))
        if valeur is not None and valeur > meilleur_f1:
            meilleur_tau, meilleur_f1 = tau, valeur
    return meilleur_tau, meilleur_f1


def decision(score_max: float, haut: float, bas: float) -> str:
    if score_max >= haut:
        return "poursuivre"
    if score_max < bas:
        return "demander une précision"
    return "zone grise : élargir la recherche ou reclasser"


# Douze paires (question, passage) jugées par un humain : 1 = pertinent, 0 = non pertinent.
ETIQUETTES = [1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0]
MODELE_A = [0.95, 0.91, 0.88, 0.86, 0.84, 0.82, 0.79, 0.74, 0.70, 0.66, 0.58, 0.41]
MODELE_B = [0.97, 0.95, 0.94, 0.93, 0.92, 0.915, 0.90, 0.89, 0.91, 0.87, 0.85, 0.83]


def main() -> None:
    print("1. Démonstration chiffrée : requête « choc parking » contre clause de contrat")
    q = [0.8, 0.3, 0.5]
    d = [0.7, 0.4, 0.6]
    produit = sum(x * y for x, y in zip(q, d))
    nq, nd = math.sqrt(sum(x * x for x in q)), math.sqrt(sum(x * x for x in d))
    c = cosinus(q, d)
    print(f"  q·d = {produit:.2f}   ||q|| = {nq:.3f}   ||d|| = {nd:.3f}   cos = {c:.3f}")
    assert round(produit, 2) == 0.98 and round(nq, 3) == 0.990 and round(nd, 3) == 1.005 and round(c, 3) == 0.985
    try:
        cosinus([0.0, 0.0, 0.0], d)
    except ValueError as e:
        print(f"  vecteur nul → ValueError : {e}")
    else:
        raise AssertionError("le vecteur nul aurait dû être refusé")

    print("2. Calibrer le seuil du modèle A : balayage des scores observés")
    for tau in sorted(set(MODELE_A), reverse=True)[:7]:
        tp, fp, fn = comptes(MODELE_A, ETIQUETTES, tau)
        print(f"  τ = {tau:.2f}   TP = {tp}  FP = {fp}  FN = {fn}   F1 = {f1(tp, fp, fn):.4f}")
    tau_a, f1_a = calibrer(MODELE_A, ETIQUETTES)
    print(f"  meilleur seuil pour A : τ = {tau_a:.2f}, F1 = {f1_a:.4f}")
    assert (tau_a, round(f1_a, 4)) == (0.82, 0.8333)
    assert [round(f1(*comptes(MODELE_A, ETIQUETTES, t)), 4) for t in (0.95, 0.91, 0.88, 0.86, 0.84, 0.82, 0.79, 0.70)] \
        == [0.2857, 0.5, 0.6667, 0.8, 0.7273, 0.8333, 0.7692, 0.8]

    print("3. F1 est constant entre deux scores observés : balayer les scores suffit")
    grille = [round(0.40 + 0.005 * i, 3) for i in range(113)]   # de 0.40 à 0.96
    for t in grille:
        au_dessus = [s for s in MODELE_A if s >= t]
        if au_dessus:
            assert comptes(MODELE_A, ETIQUETTES, t) == comptes(MODELE_A, ETIQUETTES, min(au_dessus))
    meilleur_grille = max(f1(*comptes(MODELE_A, ETIQUETTES, t)) for t in grille)
    print(f"  {len(grille)} seuils de 0.40 à 0.96 : aucun ne dépasse F1 = {meilleur_grille:.4f}")
    assert abs(meilleur_grille - f1_a) < 1e-12

    print("4. Le seuil ne se transporte pas d'un modèle d'embedding à l'autre")
    f1_b_avec_tau_a = f1(*comptes(MODELE_B, ETIQUETTES, tau_a))
    tp, fp, fn = comptes(MODELE_B, ETIQUETTES, tau_a)
    print(f"  seuil de A (0.82) appliqué à B : TP = {tp}  FP = {fp}  FN = {fn}   F1 = {f1_b_avec_tau_a:.4f}")
    tau_b, f1_b = calibrer(MODELE_B, ETIQUETTES)
    f1_a_avec_tau_b = f1(*comptes(MODELE_A, ETIQUETTES, tau_b))
    print(f"  B recalibré : τ = {tau_b:.2f}, F1 = {f1_b:.4f}   ;   seuil de B appliqué à A : F1 = {f1_a_avec_tau_b:.4f}")
    assert (tp, fp, fn) == (6, 6, 0) and round(f1_b_avec_tau_a, 4) == 0.6667
    assert (tau_b, round(f1_b, 4)) == (0.91, 0.9231) and round(f1_a_avec_tau_b, 4) == 0.5

    print("5. Pourquoi : une direction commune à tous les vecteurs gonfle tous les cosinus")
    a, b = [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]          # deux textes sans rapport : cosinus 0
    for mu in (0.0, 1.0, 2.0):
        c_mu = cosinus([a[0], a[1], mu], [b[0], b[1], mu])
        print(f"  μ = {mu:.0f} : cos(a + μu, b + μu) = {c_mu:.2f}   (formule μ²/(1 + μ²) = {mu * mu / (1 + mu * mu):.2f})")
        assert abs(c_mu - mu * mu / (1 + mu * mu)) < 1e-12
    assert round(cosinus([1.0, 0.0, 2.0], [0.0, 1.0, 2.0]), 2) == 0.80   # deux textes sans rapport, modèle « biaisé »

    print("6. Zones de décision du modèle A (illustratives) : >= 0.85 poursuivre, < 0.60 demander une précision")
    for s in (0.985, 0.72, 0.41):
        print(f"  meilleur passage à {s:.3f} → {decision(s, 0.85, 0.60)}")
    assert decision(0.985, 0.85, 0.60) == "poursuivre" and decision(0.41, 0.85, 0.60) == "demander une précision"
    assert decision(0.72, 0.85, 0.60).startswith("zone grise")
    assert min(MODELE_B) > 0.60   # avec le modèle B, la zone « demander une précision » ne serait jamais atteinte

    # Réponses des exercices 2 et 3 (vérifiées sans affichage).
    autres = ETIQUETTES[:4] + [1] + ETIQUETTES[5:]
    assert calibrer(MODELE_A, autres)[0] == 0.82 and round(calibrer(MODELE_A, autres)[1], 4) == 0.9231
    strict = {t: sum(1 for s, e in zip(MODELE_A, ETIQUETTES) if s > t and e == 1) for t in MODELE_A}
    f1_strict = {t: f1(strict[t], sum(1 for s, e in zip(MODELE_A, ETIQUETTES) if s > t and e == 0),
                       sum(1 for s, e in zip(MODELE_A, ETIQUETTES) if s <= t and e == 1)) for t in MODELE_A}
    meilleur_strict = max(sorted(f1_strict, reverse=True), key=lambda t: f1_strict[t])
    assert meilleur_strict == 0.79 and round(f1(*comptes(MODELE_A, ETIQUETTES, 0.79)), 4) == 0.7692
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
…
  q·d = 0.98   ||q|| = 0.990   ||d|| = 1.005   cos = 0.985
…
  τ = 0.86   TP = 4  FP = 0  FN = 2   F1 = 0.8000
  τ = 0.84   TP = 4  FP = 1  FN = 2   F1 = 0.7273
  τ = 0.82   TP = 5  FP = 1  FN = 1   F1 = 0.8333
  τ = 0.79   TP = 5  FP = 2  FN = 1   F1 = 0.7692
  meilleur seuil pour A : τ = 0.82, F1 = 0.8333
…
  113 seuils de 0.40 à 0.96 : aucun ne dépasse F1 = 0.8333
…
  seuil de A (0.82) appliqué à B : TP = 6  FP = 6  FN = 0   F1 = 0.6667
  B recalibré : τ = 0.91, F1 = 0.9231   ;   seuil de B appliqué à A : F1 = 0.5000
…
  μ = 2 : cos(a + μu, b + μu) = 0.80   (formule μ²/(1 + μ²) = 0.80)
…
  meilleur passage à 0.985 → poursuivre
  meilleur passage à 0.720 → zone grise : élargir la recherche ou reclasser
  meilleur passage à 0.410 → demander une précision
OK — toutes les vérifications sont passées.
```

La même fonction avec NumPy, pour de grands vecteurs ; elle garde le refus du vecteur nul au lieu de l'ancien epsilon :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cosinus_np(a, b)`** — C'est la même mesure que `cosinus`, confiée cette fois à un atelier mécanisé capable de traiter des vecteurs de plusieurs milliers de coordonnées d'un seul coup : la fonction reçoit deux séquences de nombres, les convertit en tableaux NumPy de flottants, lève `ValueError` si leurs formes diffèrent, calcule les deux normes avec `np.linalg.norm` et lève une seconde `ValueError` si l'une d'elles est nulle, au lieu d'ajouter l'ancien epsilon qui faisait passer un vecteur vide pour un texte sans rapport. Elle divise ensuite le produit scalaire par le produit des normes, rabat le quotient dans [−1, 1] avec `np.clip` contre les arrondis, et renvoie un `float` ordinaire ; ce bloc est un extrait que le harnais n'exécute pas, car il demande NumPy.

```python
# [extrait] — version NumPy, non exécutée par le harnais (pip install numpy)
import numpy as np


def cosinus_np(a, b) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError("dimensions différentes")
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0.0 or nb == 0.0:
        raise ValueError("vecteur nul : le cosinus n'est pas défini")
    return float(np.clip(np.dot(a, b) / (na * nb), -1.0, 1.0))
```

Ce que le programme montre : le cosinus se calcule en trois lignes, mais le seuil qui lui donne un sens se mesure. On le choisit sur des paires étiquetées, on le vérifie sur d'autres, et on le refait à chaque changement de modèle.

## Squelette algorithmique

Le cosinus ne suffit pas à décider : il faut un seuil, choisi sur des exemples étiquetés, puis une règle à trois issues autour de ce seuil. Le programme de ce fichier calibre le seuil en maximisant F1, puis applique la règle au meilleur score d'une recherche.

```text
ALGORITHME CalibrerLeSeuil
ENTRÉES : scores s₁ … s_m (cosinus question–passage), étiquettes y₁ … y_m (1 = pertinent, 0 = non)
SORTIE  : le seuil τ* qui maximise F1, et ce F1

  meilleur_τ ← aucun ; meilleur_F1 ← −1
  POUR CHAQUE τ parmi les scores observés, du plus grand au plus petit FAIRE
      TP ← #{i : sᵢ ≥ τ et yᵢ = 1}    FP ← #{i : sᵢ ≥ τ et yᵢ = 0}    FN ← #{i : sᵢ < τ et yᵢ = 1}
      F1 ← 2 TP / (2 TP + FP + FN)
      SI F1 > meilleur_F1 ALORS meilleur_τ ← τ ; meilleur_F1 ← F1     (à égalité, le seuil le plus haut reste)
  FIN POUR
  RETOURNER meilleur_τ, meilleur_F1

ALGORITHME Décider
ENTRÉES : score maximal s_max d'une recherche, seuils τ_haut ≥ τ_bas
  SI s_max ≥ τ_haut ALORS RETOURNER « poursuivre »
  SI s_max < τ_bas ALORS RETOURNER « demander une précision »
  RETOURNER « zone grise : élargir la recherche ou reclasser »
```

**Complexité.** La calibration essaie au plus m seuils et recompte les m exemples à chaque fois : O(m²). En triant d'abord les scores, on peut mettre à jour TP, FP et FN de façon incrémentale et descendre à O(m log m). La décision coûte O(1). La mémoire est O(m) pour les scores et les étiquettes.

**Du squelette au code.** `CalibrerLeSeuil` correspond à `calibrer`, qui appelle `comptes` puis `f1` pour chaque seuil candidat, et `Décider` à `decision`. Le cosinus lui-même vient de `cosinus` ; la variante `cosinus_np`, plus bas, fait le même calcul avec NumPy.

## Cas d'usage réels aux Émirats

Les seuils, les volumes et les tailles de jeux étiquetés ci-dessous sont illustratifs : chaque équipe les mesure sur ses propres paires et avec son propre modèle d'embedding.

### Assurance — indemniser automatiquement, ou pas

Un assureur auto et santé de Dubaï laisse son agent proposer une indemnisation automatique pour les petits sinistres de stationnement, à condition que la clause qui couvre le dommage soit retrouvée sans ambiguïté. Comme dans la démonstration chiffrée, la description « choc parking » et la clause de stationnement obtiennent 0,985 avec le modèle en service, au-dessus du seuil haut de 0,85 : l'agent poursuit, cite la clause et prépare l'offre. Une description confuse dont le meilleur passage ne dépasse pas 0,41 déclenche au contraire une question à l'assuré, et une description entre les deux part vers un gestionnaire avec les trois meilleurs passages. L'équipe a obtenu ces seuils en faisant juger quelques centaines de paires (déclaration, clause) par des gestionnaires, puis en balayant les scores comme au point 3. Quand elle a changé de modèle d'embedding, elle a refait le calibrage avant la mise en production, parce qu'appliquer les anciens seuils au nouveau modèle aurait pu tout accepter, comme le seuil de A appliqué à B. L'indicateur suivi est le taux d'offres automatiques corrigées par un gestionnaire, avec le F₁ mesuré sur un jeu de paires tenu à part.

### Banque — un seuil par langue

Une banque de détail de Dubaï répond aux questions de ses clients en arabe et en anglais à partir de la même base de procédures, vectorisée par un modèle multilingue. En calibrant sur des paires étiquetées dans chaque langue, l'équipe vérifie si les scores des questions en arabe se distribuent comme ceux des questions en anglais : s'ils sont plus bas pour des passages tout aussi pertinents, un seuil unique réglé sur l'anglais ferait demander des précisions à presque tous les clients arabophones. Elle garde donc un seuil par langue, chacun obtenu par le balayage du F₁, et normalise l'arabe (alef, ta marbuta, diacritiques) avant la vectorisation pour réduire l'écart. Sans ce calibrage, le service se dégraderait précisément pour une partie de la clientèle, sans qu'aucune erreur technique n'apparaisse dans les journaux. Les paires de calibrage sont anonymisées avant d'être montrées aux annotateurs, au titre du secret bancaire. L'indicateur suivi est le taux de demandes de précision par langue, qui doit rester comparable d'une langue à l'autre.

### Immobilier — changer de modèle d'embedding sans casser la FAQ

Une agence immobilière de Dubaï et d'Abu Dhabi fait répondre son agent aux questions des locataires à partir d'une FAQ sur l'enregistrement des baux auprès d'Ejari, les dépôts de garantie et les renouvellements. L'équipe remplace son modèle d'embedding par un modèle plus récent, de même dimension, et constate que tous les scores ont monté : des questions sans rapport avec la FAQ dépassent désormais 0,8, comme les paires du modèle B. Avec l'ancien seuil, l'agent aurait répondu à des questions hors sujet en citant des passages qui n'y répondent pas ; l'équipe recalibre donc sur ses paires étiquetées, trouve un nouveau seuil plus haut, et revectorise toute la FAQ, parce qu'un vecteur de l'ancien modèle comparé à une question vectorisée par le nouveau ne veut rien dire. La démonstration du point 4 explique le phénomène : une direction commune plus marquée gonfle tous les cosinus. Sans cette procédure de migration, la qualité aurait chuté le jour du changement, alors que le nouveau modèle sépare peut-être mieux les paires une fois calibré. L'indicateur suivi pendant la migration est le F₁ sur le jeu de paires, comparé entre l'ancien et le nouveau modèle, chacun à son propre seuil.

### Crypto — privilégier la précision sur un sujet réglementaire

Une plateforme d'actifs virtuels agréée par la VARA donne à son équipe conformité un agent qui cherche dans ses politiques internes et dans les règles qui s'appliquent à elle. Sur ce sujet, citer un passage hors sujet est plus grave que ne rien trouver : l'équipe préfère qu'en cas de doute l'agent réponde « je n'ai pas trouvé de règle applicable » et transmette la question à un juriste. Elle calibre donc le seuil non pas en maximisant F₁, qui pèse précision et rappel à égalité, mais en choisissant le plus petit seuil qui garantit une précision d'au moins 0,95 sur ses paires étiquetées. Le balayage reste le même, car l'argument du point 3 vaut pour toute mesure calculée à partir de TP, FP et FN : elle est constante entre deux scores observés. Sans ce choix explicite, le seuil « optimal » au sens du F₁ accepterait des passages voisins mais faux, et une réponse de conformité fondée sur une règle mal citée pourrait conduire à une décision fautive. L'indicateur suivi est la précision mesurée chaque mois sur un échantillon de réponses relues par un juriste.

### RH — la zone grise traitée par la recherche hybride

Un cabinet RH présent dans plusieurs émirats fait répondre son agent aux questions des recruteurs sur les procédures du MOHRE, le WPS et l'Émiratisation. Beaucoup de questions tombent en zone grise : le meilleur passage obtient un score entre les deux seuils, souvent parce que la question contient un terme précis, comme un type de permis ou un nom de formulaire, que le modèle d'embedding rapproche mal. Dans cette zone, l'agent ne répond pas tout de suite : il relance une recherche hybride qui ajoute BM25 au cosinus (étape 23), puis un reranker, et ne répond que si le nouveau meilleur passage franchit le seuil haut. Sans cette zone intermédiaire, l'agent aurait le choix entre répondre sur un passage incertain et harceler le recruteur de questions. La contrainte est l'exactitude administrative : une procédure mal citée peut retarder un visa, si bien que chaque réponse cite la procédure et sa date de version. L'indicateur suivi est la part des questions passées par la zone grise qui finissent avec une réponse validée.

### Secteur public — seuils et reformulations sur un portail bilingue

Une entité de services publics en ligne, accessible par UAE Pass, compare chaque question d'usager à ses fiches de procédure en arabe et en anglais. Sous le seuil bas, l'agent ne devine pas : il propose deux ou trois reformulations (« voulez-vous renouveler une carte, ou en demander une nouvelle ? ») au lieu d'une réponse au hasard. Les seuils sont calibrés sur des questions réelles d'usagers, anonymisées et jugées par les agents du service, avec un jeu séparé par langue, parce qu'une question en dialecte et une question en arabe standard ne se distribuent pas forcément de la même façon. L'équipe tient à part un jeu de test qui n'a pas servi au calibrage, pour que le F₁ annoncé ne soit pas flatté par le réglage lui-même. Sans seuil bas, l'agent répondrait avec assurance à des questions qu'il n'a pas comprises ; sans seuil haut, il ne répondrait jamais seul. L'indicateur suivi est le taux de sessions résolues sans passage au centre de contact, par langue.

## Pièges et limites

- **Copier un seuil.** Un seuil vient d'un modèle, d'un corpus et d'une langue : 0,82 et 0,85 peuvent être justes tous les deux, chacun chez lui.
- **Calibrer sur trop peu de paires.** Avec 12 paires, changer une seule étiquette fait gagner 9 points de F₁ (exercice 2) ; en production, on étiquette quelques centaines de paires et l'on donne un intervalle de confiance (intervalle de Wilson, étape 7).
- **Annoncer le F₁ du jeu de calibrage.** Le seuil a été choisi pour maximiser ce F₁, qui est donc optimiste : on mesure la performance sur des paires tenues à part.
- **Garder l'epsilon ou le 0.0 du vecteur nul.** Ils transforment une panne d'embedding en score bas silencieux.
- **Changer de modèle sans revectoriser.** Comparer un vecteur de l'ancien modèle à un vecteur du nouveau n'a aucun sens, même à dimension égale.

### Exercice feuille blanche

1. Sans regarder le code, écrire `cosinus` avec le refus du vecteur nul, puis vérifier le 0,985 de la démonstration.
2. Prédire, puis vérifier : si la paire de score 0,84 du modèle A était jugée pertinente, quel serait le meilleur seuil, et son F₁ ? (Réponse : toujours 0,82, mais avec F₁ = 12/13 = 0,9231, car TP = 6, FP = 0 et FN = 1.)
3. Trouver le bug : dans `comptes`, `s > tau` au lieu de `s >= tau`. Quel seuil le balayage renvoie-t-il pour le modèle A, et que se passe-t-il si la production applique ensuite ce seuil avec `>=` ? (Réponse : il renvoie 0,79, parce qu'avec `>` le seuil 0,79 accepte les mêmes paires que le bon seuil 0,82 ; appliqué avec `>=`, le seuil 0,79 accepte en plus la paire non pertinente de score 0,79, et F₁ tombe à 0,7692.)

## Pour aller plus loin

F₁ pèse précision et rappel à égalité ; la famille F_β (étape 56) donne plus de poids à l'un ou à l'autre. La courbe précision-rappel et l'aire sous la courbe ROC (étape 51) résument tous les seuils à la fois, utile pour comparer deux modèles avant même de choisir un seuil. Enfin, on peut transformer le cosinus en probabilité de pertinence par une régression logistique ajustée sur les paires étiquetées (calibration de Platt) : le seuil se lit alors comme une probabilité, plus facile à défendre devant une équipe métier.

> Suite : [Distance euclidienne](<20-RAG-Formule-Distance-Euclidienne.md>) — étape 20.
