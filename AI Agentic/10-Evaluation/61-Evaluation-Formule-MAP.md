# Étape 61 — Évaluation — Mean Average Precision (MAP)

> Étape 61 du parcours · Prérequis : [Loi bêta et petits échantillons](<60b-Loi-Beta-et-Petits-Echantillons.md>) · Suite : [Perplexité en évaluation](<62-Evaluation-Formule-Perplexite.md>)

**Dossier :** 10-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  
**Nom du fichier :** 61-Evaluation-Formule-MAP.md

## Définition

L'**Average Precision** (AP) résume en un seul nombre la qualité d'un classement pour une requête. On parcourt la liste renvoyée par le retriever ; à chaque rang k où se trouve un document pertinent, on note la Precision@k (étape 26), c'est-à-dire la part de pertinents parmi les k premiers. On additionne ces précisions et on divise par **R**, le nombre total de documents pertinents qui existent pour cette requête dans le corpus annoté, **y compris ceux que le retriever n'a jamais renvoyés**. Un pertinent oublié n'ajoute rien à la somme mais compte dans R : c'est ainsi que l'AP punit l'oubli. La **Mean Average Precision** (MAP) est la moyenne des AP sur les requêtes du jeu d'évaluation qui ont au moins un document pertinent. Une requête sans aucun pertinent (R = 0) n'a pas d'AP : elle est exclue de la moyenne et se mesure autrement.

## Rôle dans un agent

Dans la boucle percevoir → décider → agir → observer, l'agent décide de chercher, appelle le retriever, puis observe une liste classée dont il injecte le haut dans son prompt. Quand la réponse a besoin de **plusieurs** documents à la fois (une réponse de conformité qui cite trois règles, un dossier qui réunit quatre pièces), il faut savoir si le retriever et le reranker les trouvent tous, et s'ils les placent en tête. Les métriques déjà vues en regardent chacune une partie : le MRR (étape 27) ne voit que le premier pertinent, le Recall@k (étape 25) ignore l'ordre, la Precision@k (étape 26) ignore les pertinents absents, le NDCG (étape 28) sert aux pertinences graduées, et Context Precision (étape 57) ne pénalise pas les pertinents non retrouvés. L'AP réunit ordre, précision et rappel pour une pertinence binaire. On la calcule hors ligne sur un jeu de requêtes annotées, et la MAP sert de barrière avant tout changement d'index, de découpage en chunks ou de modèle d'embedding.

## Équation complète

Pertinence binaire du document placé au rang k :

$$
\text{rel}(k) \in \{0,\, 1\}
$$

Precision@k (étape 26) :

$$
\text{P@}k = \frac{1}{k} \sum_{j=1}^{k} \text{rel}(j)
$$

Average Precision d'une requête q, avec une liste de n documents et R_q pertinents annotés :

$$
\text{AP}(q) = \frac{1}{R_q} \sum_{k=1}^{n} \text{P@}k \cdot \text{rel}(k), \qquad R_q \ge 1
$$

Forme par les rangs, quand les m pertinents retrouvés occupent les rangs k₁ < k₂ < … < kₘ :

$$
\text{AP}(q) = \frac{1}{R_q} \sum_{i=1}^{m} \frac{i}{k_i}
$$

Mean Average Precision sur les requêtes qui ont au moins un pertinent :

$$
\text{MAP} = \frac{1}{|Q^{+}|} \sum_{q \in Q^{+}} \text{AP}(q), \qquad Q^{+} = \{\, q \in Q : R_q \ge 1 \,\}
$$

Context Precision (étape 57), placée à côté pour la comparaison : même numérateur, autre dénominateur :

$$
\text{CP}(q) = \frac{\sum_{k=1}^{n} \text{P@}k \cdot \text{rel}(k)}{\sum_{k=1}^{n} \text{rel}(k)}
$$

Le lien entre les deux, démontré plus bas :

$$
\text{AP}(q) = \text{CP}(q) \times \text{Recall@}n(q)
$$

Version tronquée, quand l'agent ne lit que les K premiers résultats (convention TREC : on divise toujours par R_q) :

$$
\text{AP@}K(q) = \frac{1}{R_q} \sum_{k=1}^{K} \text{P@}k \cdot \text{rel}(k)
$$

## Décryptage des symboles

$$
q,\; Q
$$

**Sens :** une requête du jeu d'évaluation, et l'ensemble de ces requêtes · **Type / plage :** ensemble fini · **Variable Python :** `requetes`, une liste de couples (pertinences, R)

$$
Q^{+}
$$

**Sens :** les requêtes qui ont au moins un document pertinent annoté ; les seules qui entrent dans la MAP · **Type / plage :** sous-ensemble de Q · **Variable Python :** `definies`

$$
n
$$

**Sens :** longueur de la liste classée renvoyée pour la requête (l'ancienne version de ce fichier utilisait n sans le définir) · **Type / plage :** entier ≥ 0 · **Variable Python :** `len(rel)`

$$
k
$$

**Sens :** un rang dans la liste, compté à partir de 1 · **Type / plage :** entier de 1 à n · **Variable Python :** `k` dans `enumerate(rel, start=1)`

$$
\text{rel}(k)
$$

**Sens :** 1 si le document du rang k est pertinent pour la requête, 0 sinon ; un même document renvoyé deux fois ne compte qu'une fois · **Type / plage :** 0 ou 1 · **Variable Python :** `rel[k - 1]`

$$
\text{P@}k
$$

**Sens :** part de pertinents parmi les k premiers documents · **Type / plage :** réel dans [0, 1] · **Variable Python :** `precision_at_k(rel, k)`, ou `trouves / k` dans la boucle

$$
R_q
$$

**Sens :** nombre total de documents pertinents annotés pour la requête, retrouvés ou non · **Type / plage :** entier ≥ 0 ; AP n'est définie que si R_q ≥ 1 · **Variable Python :** `n_pertinents_total`

$$
m,\; k_i
$$

**Sens :** nombre de pertinents effectivement retrouvés, et rang du i-ème d'entre eux · **Type / plage :** 0 ≤ m ≤ R_q, et kᵢ ≥ i · **Variable Python :** `trouves`, et `k` au moment où `trouves` vaut i

$$
\text{AP}(q)
$$

**Sens :** Average Precision de la requête · **Type / plage :** réel dans [0, 1], ou indéfinie si R_q = 0 · **Variable Python :** `average_precision(rel, n_pertinents_total)`, qui renvoie `None` si R = 0

$$
\text{MAP}
$$

**Sens :** moyenne des AP définies · **Type / plage :** réel dans [0, 1], ou indéfinie si aucune requête n'a de pertinent · **Variable Python :** `mean_average_precision(requetes)`

$$
\text{CP}(q)
$$

**Sens :** Context Precision de l'étape 57, divisée par les pertinents présents dans la liste · **Type / plage :** réel dans [0, 1], indéfinie si la liste ne contient aucun pertinent · **Variable Python :** `context_precision(rel)`

$$
K
$$

**Sens :** coupure : nombre de résultats que l'agent lit vraiment · **Type / plage :** entier ≥ 1 · **Variable Python :** `k_max`

## Démonstration

### 1. La forme par les rangs

Dans la somme qui définit l'AP, tous les termes où rel(k) = 0 valent zéro : il ne reste que les m rangs k₁ < … < kₘ où se trouve un pertinent. Au rang kᵢ, les pertinents placés aux rangs inférieurs ou égaux à kᵢ sont exactement ceux des rangs k₁, …, kᵢ, parce que les rangs sont rangés dans l'ordre croissant. Il y en a donc i parmi les kᵢ premiers documents, et

$$
\text{P@}k_i = \frac{i}{k_i}
\qquad\Longrightarrow\qquad
\text{AP}(q) = \frac{1}{R_q} \sum_{i=1}^{m} \frac{i}{k_i}
$$

C'est cette forme que le code calcule : un compteur `trouves` monte de 1 à chaque pertinent, et l'on ajoute `trouves / k`.

### 2. Les bornes : 0 ≤ AP ≤ 1, et le seul cas où AP = 1

Les rangs k₁ < k₂ < … sont des entiers distincts qui commencent à 1 au moins. Par récurrence, k₁ ≥ 1 et kᵢ ≥ kᵢ₋₁ + 1, donc kᵢ ≥ i : le i-ème pertinent ne peut pas être placé avant le rang i. Chaque terme i/kᵢ vaut donc au plus 1, et la somme vaut au plus m. Comme les documents de la liste sont distincts, on ne peut pas retrouver plus de pertinents qu'il n'en existe : m ≤ R. D'où

$$
0 \;\le\; \text{AP}(q) \;\le\; \frac{m}{R_q} \;\le\; 1
$$

L'égalité AP = 1 demande que les deux inégalités soient des égalités : m = R (tous les pertinents sont retrouvés) et kᵢ = i pour tout i (ils occupent les rangs 1 à R, sans aucun document inutile devant). Réciproquement, dans ce cas chaque terme vaut 1 et la somme vaut R. L'AP vaut 0 si et seulement si m = 0. L'hypothèse « documents distincts » n'est pas un détail : si le même document pertinent revient deux fois en tête avec R = 1, la formule naïve donne (1 + 1)/1 = 2. C'est pourquoi le code marque un doublon comme non pertinent et refuse une liste qui contient plus de pertinents que R.

### 3. Le bug de l'ancienne version, sur un contre-exemple chiffré

L'ancien code divisait la somme par `relevant_so_far`, le nombre de pertinents **retrouvés** (m), au lieu de R. Avec R = 3 :

- pour le classement [1, 0, 0], l'ancien code donnait 1/1 = 1,0, alors que l'AP vaut 1/3 ≈ 0,333 : deux pertinents sur trois manquent ;
- pour le classement [0, 1, 0, 1], il donnait (1/2 + 2/4)/2 = 0,5, alors que l'AP vaut (0,5 + 0,5)/3 ≈ 0,333.

Le défaut crée une incitation perverse. Avec R = 2, le classement [1, 0, 0, 1] a une AP de (1 + 2/4)/2 = 0,75 dans les deux versions, parce que tout est retrouvé. Si le retriever ne renvoie plus que son document le plus sûr, [1], l'ancienne version monte à 1,0 alors que la vraie AP tombe à 0,5. Un système qui renvoie moins de documents serait récompensé par l'ancienne formule : c'est exactement le contraire de ce que l'on veut mesurer.

### 4. AP = Context Precision × rappel

Notons S la somme des P@k · rel(k). Par définition, AP = S/R et CP = S/m. Si m ≥ 1 :

$$
\text{AP}(q) = \frac{S}{R_q} = \frac{S}{m} \cdot \frac{m}{R_q} = \text{CP}(q) \times \text{Recall@}n(q)
$$

parce que m/R est la part des pertinents retrouvés, c'est-à-dire le rappel sur toute la liste. Trois conséquences. L'AP est toujours inférieure ou égale à CP, avec égalité si et seulement si le rappel vaut 1. L'ancienne version de ce fichier calculait donc en réalité Context Precision, pas l'AP. Et l'on comprend pourquoi les codes des étapes 57 et 61 sont presque identiques : seul le dénominateur change, et avec lui la question posée. Context Precision demande « les pertinents présents sont-ils devant ? », l'AP demande « les pertinents sont-ils tous là, et devant ? ».

### 5. Remonter un pertinent d'un rang fait toujours monter l'AP

Échangeons un pertinent placé au rang k + 1 avec un document inutile placé au rang k. Si ce pertinent est le i-ème, seul son terme change : il passe de i/(k + 1) à i/k. Les pertinents placés avant gardent leur rang et leur compte ; ceux placés après gardent leur rang, et le nombre de pertinents devant eux ne change pas. Le gain vaut

$$
\Delta\text{AP} = \frac{1}{R_q}\left(\frac{i}{k} - \frac{i}{k+1}\right) = \frac{i}{R_q\, k\,(k+1)} > 0
$$

Il est d'autant plus grand que k est petit : comme le MRR et le NDCG, l'AP se joue surtout en tête. Exemple : passer de [1, 0, 1, 0, 1] à [1, 1, 0, 0, 1] avec R = 3 remonte le 2e pertinent du rang 3 au rang 2 ; le gain vaut 2/(3 × 2 × 3) = 1/9 ≈ 0,111.

### 6. Ce qui ne change pas l'AP : la queue de liste

Ajouter un document inutile **après** le dernier pertinent n'ajoute aucun terme : l'AP ne bouge pas. L'AP ne voit donc pas une longue traîne de bruit en fin de liste. Ce bruit coûte pourtant des tokens s'il est injecté dans le prompt ; on le mesure avec la Precision@K (étape 26) et le budget de contexte (étape 72). À l'inverse, ajouter en position n + 1 un pertinent jusque-là oublié ajoute le terme (m + 1)/(n + 1), divisé par R : l'AP monte.

### 7. Pourquoi exclure R = 0 au lieu de compter 0 ou 1

Si R = 0, la somme est nulle et le dénominateur aussi : 0/0 n'a pas de valeur. Compter 0 punirait le retriever pour une question dont la réponse n'existe pas dans le corpus ; compter 1 le récompenserait quoi qu'il renvoie. Dans les deux cas, la MAP mélangerait deux questions différentes. Si l'on compte 0 pour les requêtes sans pertinent, on obtient exactement la MAP multipliée par |Q⁺|/|Q| : sur l'exemple du point 9, 0,64074 devient 0,48056. Ces requêtes hors périmètre se mesurent à part, par le taux de réponses « je ne trouve pas cette information » correctes (étape 60).

### 8. L'AP est une aire sous la courbe précision–rappel

À chaque pertinent retrouvé, le rappel augmente de 1/R. On peut donc réécrire

$$
\text{AP}(q) = \sum_{i=1}^{m} \text{P@}k_i \times \Delta\text{Recall}_i, \qquad \Delta\text{Recall}_i = \frac{1}{R_q}
$$

C'est l'aire sous la courbe en escalier de la précision en fonction du rappel. Le nom « Average Precision » vient de là : c'est la précision moyenne sur les niveaux de rappel 1/R, 2/R, …, 1, avec une précision nulle pour les niveaux jamais atteints.

### 9. Exemple fait à la main (le code reprend ces nombres)

Quatre requêtes d'un assistant de conformité bancaire :

| Requête | Classement | R | Rangs des pertinents | Calcul | AP |
|---|---|---|---|---|---|
| 1 | [1, 0, 1, 0, 1] | 3 | 1, 3, 5 | (1/1 + 2/3 + 3/5) / 3 = 2,26667 / 3 | 0,75556 |
| 2 | [0, 1, 0, 0] | 3 | 2 | (1/2) / 3 | 0,16667 |
| 3 | [1, 1, 0] | 2 | 1, 2 | (1 + 1) / 2 | 1 |
| 4 | [0, 0, 0] | 0 | aucun | 0 / 0 | indéfinie, exclue |

La MAP vaut (0,75556 + 0,16667 + 1) / 3 = 1,92222 / 3 ≈ 0,64074. L'ancienne version aurait donné 0,5 à la requête 2 (un seul pertinent retrouvé, divisé par 1) et une MAP de 0,75185 : elle surestimait le retriever de 11 points. Pour la requête 2, Context Precision vaut 0,5 et le rappel 1/3 : leur produit redonne bien 0,16667.

## Effets et comportement

- **L'AP récompense trois choses à la fois.** Placer les pertinents tôt (point 5), n'en oublier aucun (le dénominateur R) et ne pas intercaler de bruit devant eux. Elle ignore le bruit placé après le dernier pertinent (point 6).
- **La MAP est une moyenne de ratios.** Chaque requête pèse autant, qu'elle ait 1 ou 10 pertinents. Une requête facile à R = 1 compte autant qu'une requête de synthèse à R = 8.
- **La MAP dépend de la qualité de l'annotation.** Si les annotateurs ont oublié un pertinent, R est sous-estimé et ce document, s'il est retrouvé, compte comme du bruit. On annote par mise en commun (*pooling*) des résultats de plusieurs retrievers.
- **La pertinence est binaire.** Un document « partiellement utile » doit être tranché ; si les degrés comptent, on passe au NDCG (étape 28).
- **Une petite MAP ne dit pas où est le problème.** On la décompose avec l'identité AP = CP × rappel : un rappel bas pointe le retriever ou le découpage, une CP basse pointe le reranker.

## Du symbole au code Python

$$
\text{rel}(k)
$$

**Variable ou fonction :** `rel`, liste de 0 et de 1 ; `rel_depuis_ids(classement, pertinents)` la fabrique à partir d'identifiants

$$
R_q
$$

**Variable ou fonction :** `n_pertinents_total`

$$
\text{P@}k
$$

**Variable ou fonction :** `precision_at_k(rel, k)`

$$
\frac{1}{R_q} \sum_{k} \text{P@}k \cdot \text{rel}(k)
$$

**Variable ou fonction :** `average_precision(rel, n_pertinents_total, k_max=None)`

$$
\frac{1}{|Q^{+}|} \sum_{q \in Q^{+}} \text{AP}(q)
$$

**Variable ou fonction :** `mean_average_precision(requetes)`

$$
\text{CP}(q)
$$

**Variable ou fonction :** `context_precision(rel)`

### Déroulé, ligne par ligne

**`verifier_pertinences(rel)`** lève `ValueError` si une valeur n'est ni 0 ni 1. Un score de pertinence gradué (2, 3…) passé par erreur gonflerait la somme sans prévenir.

**`precision_at_k(rel, k)`** renvoie `sum(rel[:k]) / k`. Pour `rel = [1, 0, 1, 0, 1]` et `k = 3`, la tranche `rel[:3]` vaut `[1, 0, 1]`, sa somme 2, et le résultat 0,6667.

**`average_precision(rel, n_pertinents_total, k_max=None)`**, le cœur du fichier.

- `liste = rel if k_max is None else rel[:k_max]` : sans coupure, on lit toute la liste ; avec `k_max = 2`, on ne garde que les deux premiers rangs.
- `if sum(liste) > n_pertinents_total` : plus de pertinents retrouvés que de pertinents annotés est impossible avec des documents distincts (démonstration, point 2). C'est le signe d'un doublon ou d'une annotation fausse : on lève `ValueError` plutôt que de renvoyer une AP supérieure à 1.
- `if n_pertinents_total == 0: return None` : l'AP n'est pas définie (point 7).
- La boucle `for k, v in enumerate(liste, start=1)` compte les rangs à partir de 1. À chaque pertinent, `trouves += 1`, puis `somme += trouves / k`. Pour `[1, 0, 1, 0, 1]`, on ajoute 1/1, puis 2/3, puis 3/5 : `somme` vaut 2,26667.
- `return somme / n_pertinents_total` : on divise par R = 3, pas par `trouves`. Résultat 0,75556. C'est la ligne que l'ancienne version avait fausse.

**`ap_ancienne_version(rel)`** recopie l'ancien code pour le contraste : même boucle, mais `return sum(precisions) / trouves`. Sur `[1, 0, 0]`, elle renvoie 1,0.

**`context_precision(rel)`** a la même boucle et divise par `trouves` : c'est la définition de l'étape 57, et c'est pourquoi elle coïncide avec l'ancienne version.

**`mean_average_precision(requetes)`** calcule l'AP de chaque couple `(rel, r)`, ne garde que les valeurs différentes de `None` dans `definies`, et renvoie leur moyenne, ou `None` si la liste est vide.

**`rel_depuis_ids(classement, pertinents)`** transforme une liste d'identifiants en pertinences. L'ensemble `vus` retient les documents déjà rencontrés : pour `["d7", "d3", "d7", "d9"]` avec les pertinents `{"d7", "d9"}`, le deuxième `d7` donne 0, et l'on obtient `[1, 0, 0, 1]`.

**`main()`**, bloc par bloc.

1. Les deux classements de la démonstration, point 3 : l'AP vaut 0,3333 dans les deux cas, l'ancienne version 1,0 et 0,5.
2. Les quatre requêtes du tableau. Pour chaque requête définie, le programme imprime AP, CP et le rappel `sum(rel) / r`, et vérifie l'identité AP = CP × rappel. La MAP vaut 0,64074, l'ancienne version 0,75185, et compter 0 pour la requête sans pertinent donnerait 0,48056.
3. Tronquer `[1, 0, 0, 1]` en `[1]` fait passer la vraie AP de 0,75 à 0,5, et l'ancienne de 0,75 à 1,0.
4. Remonter le deuxième pertinent du rang 3 au rang 2 rapporte exactement `(2 / (2 * 3)) / 3`, soit 0,11111.
5. `itertools.product((0, 1), repeat=n)` énumère tous les classements binaires de longueur 1 à 6, et `r` parcourt toutes les valeurs de R possibles, de `max(m, 1)` à 6. Pour chacun des 555 couples, on vérifie 0 ≤ AP ≤ 1, que AP = 1 exactement quand les R pertinents occupent les R premiers rangs, et AP ≤ CP. Le total se recompte à la main : 12 + 23 + 43 + 79 + 143 + 255 = 555 couples pour les longueurs 1 à 6.
6. Le doublon est neutralisé, et trois entrées invalides lèvent `ValueError` : trois pertinents pour R = 2, une pertinence égale à 2, un R négatif. Enfin, une MAP sans aucune requête définie vaut `None`, et la coupure `k_max = 2` sur `[0, 1, 0, 1]` ne garde que le terme 1/2.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`verifier_pertinences(rel)`** — Cette fonction est le douanier qui contrôle les étiquettes avant que la moindre addition ne commence : elle reçoit la liste des pertinences d'un classement, rang par rang, et lève une `ValueError` dès qu'une valeur n'est ni 0 ni 1, parce qu'une note graduée comme 2 ou 3, passée par erreur, gonflerait la somme sans prévenir. Elle ne renvoie rien quand tout est en règle ; `average_precision` et `context_precision` l'appellent en premier, et `main` vérifie que la liste [1, 2, 0] est bien refusée.

**`precision_at_k(rel, k)`** — Celle-ci est le contrôleur qui s'arrête au rang k et fait le compte de ce qu'il a déjà vu : elle reçoit la liste des pertinences et un rang k, lève une `ValueError` si k n'est pas compris entre 1 et la longueur de la liste, et renvoie la somme des k premières pertinences divisée par k. Pour [1, 0, 1, 0, 1] et k = 3, elle donne 2/3, soit 0,6667 ; c'est la brique élémentaire de la formule de l'AP, même si `average_precision` recalcule cette précision à la volée avec son propre compteur plutôt que de l'appeler.

**`average_precision(rel, n_pertinents_total, k_max)`** — Cette fonction est le juge de l'Average Precision, qui n'oublie jamais les documents pertinents restés dans le corpus : elle reçoit les pertinences du classement, le nombre total R de pertinents annotés et une coupure facultative `k_max`, vérifie les pertinences, refuse un R négatif, tronque la liste si une coupure est donnée, et lève `ValueError` si l'on a retrouvé plus de pertinents qu'il n'en existe, signe d'un doublon ou d'une annotation fausse. Elle renvoie `None` si R = 0, et sinon la somme des précisions aux rangs pertinents divisée par R, et non par le nombre de pertinents trouvés : 0,75556 pour [1, 0, 1, 0, 1] avec R = 3, 1/3 pour [1, 0, 0] avec R = 3, et 0,5 pour la liste tronquée [1] avec R = 2.

**`ap_ancienne_version(rel)`** — Celle-ci est l'ancienne recette du fichier, gardée sous verre pour qu'on voie où elle se trompe : elle reçoit seulement la liste des pertinences, renvoie 0 si aucun document n'est pertinent, puis fait la même boucle que la bonne version mais divise la somme des précisions par le nombre de pertinents trouvés, sans rien savoir de R. Elle renvoie donc 1 pour [1, 0, 0], alors que deux pertinents sur trois n'ont jamais été retrouvés, et 0,5 pour [0, 1, 0, 1] ; sur les requêtes du tableau, elle donne une MAP de 0,75185 au lieu de 0,64074, et elle récompense un retriever qui raccourcit sa liste.

**`context_precision(rel)`** — Cette fonction est la Context Precision de l'étape 57, rappelée ici pour comparer : elle reçoit les pertinences, les vérifie, renvoie `None` quand aucun pertinent n'est présent, contrairement à la copie de l'étape 57 qui renvoie 0 dans ce cas, et sinon divise la somme des précisions aux rangs pertinents par le nombre de pertinents présents dans la liste. Elle coïncide donc avec l'ancienne version de l'AP, et `main` vérifie l'identité AP = CP × rappel, par exemple 0,16667 = 0,5 × 1/3 pour [0, 1, 0, 0] avec R = 3, ainsi que AP ≤ CP sur les 555 couples de l'énumération.

**`mean_average_precision(requetes)`** — Celle-ci est le président du jury qui fait la moyenne des notes de toutes les requêtes, mais refuse de noter une épreuve qui n'avait pas de sujet : elle reçoit une liste de couples (pertinences, R), calcule l'AP de chacun, écarte les valeurs `None` des requêtes sans aucun pertinent, et renvoie la moyenne des AP restantes, ou `None` si aucune n'est définie. Sur les quatre requêtes du tableau, elle renvoie 0,64074 ; compter 0 pour la requête sans pertinent aurait donné 0,48056, une pénalité pour une faute que le retriever n'a pas commise.

**`rel_depuis_ids(classement, pertinents)`** — Cette fonction est l'archiviste qui transforme la liste des cotes renvoyées par le retriever en une colonne de 0 et de 1, en se souvenant de ce qu'elle a déjà vu : elle reçoit la liste ordonnée des identifiants et l'ensemble des identifiants pertinents, garde dans `vus` les documents déjà rencontrés, et inscrit 1 seulement pour un document pertinent qui apparaît pour la première fois. Elle renvoie la liste des pertinences : [1, 0, 0, 1] pour le classement d7, d3, d7, d9 avec les pertinents d7 et d9, où le doublon d7 ne compte qu'une fois, ce qui donne une AP de 0,75 au lieu de lever une erreur.

**`main()`** — C'est le chef d'orchestre des six démonstrations : il montre d'abord le bug de l'ancienne version, 1 et 0,5 au lieu de 1/3, puis calcule les quatre requêtes du tableau avec leur AP, leur CP et leur rappel, la MAP 0,64074, l'ancienne 0,75185 et la variante à 0,48056. Il vérifie ensuite que tronquer une liste fait baisser la vraie AP de 0,75 à 0,5 et monter l'ancienne jusqu'à 1, que remonter un pertinent rapporte exactement 0,11111, énumère les 555 couples (classement, R) pour contrôler les bornes, le cas AP = 1 et AP ≤ CP, et termine par le doublon, trois entrées invalides et la coupure `k_max`, avant d'afficher « OK ».

```python
"""Étape 61 — Average Precision et MAP : division par R, exclusion de R = 0, lien avec Context Precision."""
import itertools
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def verifier_pertinences(rel: list[int]) -> None:
    if any(v not in (0, 1) for v in rel):
        raise ValueError("chaque pertinence vaut 0 ou 1")


def precision_at_k(rel: list[int], k: int) -> float:
    """P@k = (1/k) · somme des rel(j) pour j <= k."""
    if not 1 <= k <= len(rel):
        raise ValueError("il faut 1 <= k <= len(rel)")
    return sum(rel[:k]) / k


def average_precision(rel: list[int], n_pertinents_total: int, k_max: int | None = None) -> float | None:
    """AP = (1/R) · somme des P@k · rel(k). R compte AUSSI les pertinents jamais retrouvés.
    Renvoie None si R = 0 : la requête n'a aucun document pertinent, AP n'est pas défini."""
    verifier_pertinences(rel)
    if n_pertinents_total < 0:
        raise ValueError("R >= 0")
    liste = rel if k_max is None else rel[:k_max]
    if sum(liste) > n_pertinents_total:
        raise ValueError("plus de pertinents retrouvés que de pertinents annotés : doublons ou annotation fausse")
    if n_pertinents_total == 0:
        return None
    somme = 0.0
    trouves = 0
    for k, v in enumerate(liste, start=1):
        if v:
            trouves += 1
            somme += trouves / k          # P@k au rang du trouves-ième pertinent
    return somme / n_pertinents_total


def ap_ancienne_version(rel: list[int]) -> float:
    """Version d'origine du fichier, FAUSSE : divise par les pertinents retrouvés au lieu de R."""
    if not any(rel):
        return 0.0
    precisions, trouves = [], 0
    for k, v in enumerate(rel, start=1):
        if v:
            trouves += 1
            precisions.append(trouves / k)
    return sum(precisions) / trouves


def context_precision(rel: list[int]) -> float | None:
    """Étape 57 : même numérateur, mais divisé par les pertinents PRÉSENTS dans la liste."""
    verifier_pertinences(rel)
    if sum(rel) == 0:
        return None
    somme, trouves = 0.0, 0
    for k, v in enumerate(rel, start=1):
        if v:
            trouves += 1
            somme += trouves / k
    return somme / trouves


def mean_average_precision(requetes: list[tuple[list[int], int]]) -> float | None:
    """MAP = moyenne des AP sur les requêtes où R >= 1 ; None si aucune requête n'est définie."""
    aps = [average_precision(rel, r) for rel, r in requetes]
    definies = [a for a in aps if a is not None]
    if not definies:
        return None
    return sum(definies) / len(definies)


def rel_depuis_ids(classement: list[str], pertinents: set[str]) -> list[int]:
    """Transforme une liste d'identifiants en pertinences ; un doublon ne compte qu'à sa première apparition."""
    vus: set[str] = set()
    rel = []
    for doc in classement:
        rel.append(1 if doc in pertinents and doc not in vus else 0)
        vus.add(doc)
    return rel


def main() -> None:
    print("1. Le bug : diviser par les pertinents retrouvés au lieu de R")
    for rel, r, juste in (([1, 0, 0], 3, 1 / 3), ([0, 1, 0, 1], 3, 1 / 3)):
        ap = average_precision(rel, r)
        bug = ap_ancienne_version(rel)
        print(f"  {rel}  R = {r}   AP juste = {ap:.4f}   ancienne version = {bug:.4f}")
        assert math.isclose(ap, juste)
    assert ap_ancienne_version([1, 0, 0]) == 1.0 and ap_ancienne_version([0, 1, 0, 1]) == 0.5

    print("2. Exemple fait à la main : trois requêtes notées, une sans pertinent")
    requetes = [([1, 0, 1, 0, 1], 3), ([0, 1, 0, 0], 3), ([1, 1, 0], 2), ([0, 0, 0], 0)]
    attendus = [0.75556, 0.16667, 1.0, None]
    for (rel, r), att in zip(requetes, attendus):
        ap = average_precision(rel, r)
        cp = context_precision(rel)
        if ap is None:
            print(f"  {rel}  R = {r}   AP = None (exclue de la MAP)")
            assert att is None
            continue
        rappel = sum(rel) / r
        print(f"  {rel}  R = {r}   AP = {ap:.5f}   CP = {cp:.5f}   rappel = {rappel:.4f}   CP × rappel = {cp * rappel:.5f}")
        assert abs(ap - att) < 5e-6
        assert math.isclose(ap, cp * rappel)                  # AP = CP × Recall (démonstration, point 4)
    m = mean_average_precision(requetes)
    m_bug = sum(ap_ancienne_version(rel) for rel, r in requetes if r > 0) / 3
    print(f"  MAP = {m:.5f}   (ancienne version : {m_bug:.5f})")
    assert abs(m - 0.64074) < 5e-6 and abs(m_bug - 0.75185) < 5e-6
    m_zero = (0.75556 + 0.16667 + 1.0 + 0.0) / 4
    print(f"  si la requête R = 0 comptait pour 0 : MAP = {m_zero:.5f}")
    assert abs(m_zero - 0.48056) < 5e-6

    print("3. Tronquer la liste fait monter l'ancienne version, baisser la vraie AP")
    longue, courte = [1, 0, 0, 1], [1]
    print(f"  {longue} R = 2 : AP = {average_precision(longue, 2):.4f}, ancienne = {ap_ancienne_version(longue):.4f}")
    print(f"  {courte}          : AP = {average_precision(courte, 2):.4f}, ancienne = {ap_ancienne_version(courte):.4f}")
    assert average_precision(longue, 2) == 0.75 and average_precision(courte, 2) == 0.5
    assert ap_ancienne_version(courte) == 1.0 > ap_ancienne_version(longue)

    print("4. Remonter un pertinent d'un rang augmente l'AP de i / (k(k+1))")
    avant, apres = [1, 0, 1, 0, 1], [1, 1, 0, 0, 1]          # le 2e pertinent passe du rang 3 au rang 2
    gain = average_precision(apres, 3) - average_precision(avant, 3)
    print(f"  {avant} → {apres} : gain = {gain:.5f} = (2/(2×3)) / 3")
    assert math.isclose(gain, (2 / (2 * 3)) / 3)

    print("5. Vérification exhaustive : 0 <= AP <= 1, et AP = 1 ssi tout est retrouvé en tête")
    nb = 0
    for n in range(1, 7):
        for rel in itertools.product((0, 1), repeat=n):
            rel = list(rel)
            m_trouves = sum(rel)
            for r in range(max(m_trouves, 1), 7):
                ap = average_precision(rel, r)
                assert 0.0 <= ap <= 1.0 + 1e-12
                en_tete = m_trouves == r and rel[:r] == [1] * r
                assert (abs(ap - 1.0) < 1e-12) == en_tete
                cp = context_precision(rel)
                if cp is not None:
                    assert ap <= cp + 1e-12                  # AP <= CP, égalité ssi rappel = 1
                nb += 1
    print(f"  {nb} couples (classement, R) vérifiés")
    assert nb == 555                                     # 12 + 23 + 43 + 79 + 143 + 255

    print("6. Doublons et entrées invalides")
    rel = rel_depuis_ids(["d7", "d3", "d7", "d9"], {"d7", "d9"})
    print(f"  classement d7, d3, d7, d9 → pertinences {rel} → AP = {average_precision(rel, 2):.4f}")
    assert rel == [1, 0, 0, 1] and average_precision(rel, 2) == 0.75
    for args in (([1, 1, 1], 2), ([1, 2, 0], 3), ([1, 0], -1)):
        try:
            average_precision(*args)
        except ValueError as e:
            print(f"  {args} → ValueError ({e})")
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")
    assert mean_average_precision([([0, 0], 0)]) is None
    assert average_precision([0, 1, 0, 1], 3, k_max=2) == (1 / 2) / 3
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Le bug : diviser par les pertinents retrouvés au lieu de R
  [1, 0, 0]  R = 3   AP juste = 0.3333   ancienne version = 1.0000
  [0, 1, 0, 1]  R = 3   AP juste = 0.3333   ancienne version = 0.5000
2. Exemple fait à la main : trois requêtes notées, une sans pertinent
  [1, 0, 1, 0, 1]  R = 3   AP = 0.75556   CP = 0.75556   rappel = 1.0000   CP × rappel = 0.75556
  [0, 1, 0, 0]  R = 3   AP = 0.16667   CP = 0.50000   rappel = 0.3333   CP × rappel = 0.16667
  [1, 1, 0]  R = 2   AP = 1.00000   CP = 1.00000   rappel = 1.0000   CP × rappel = 1.00000
  [0, 0, 0]  R = 0   AP = None (exclue de la MAP)
  MAP = 0.64074   (ancienne version : 0.75185)
  si la requête R = 0 comptait pour 0 : MAP = 0.48056
3. Tronquer la liste fait monter l'ancienne version, baisser la vraie AP
…
  [1]          : AP = 0.5000, ancienne = 1.0000
4. Remonter un pertinent d'un rang augmente l'AP de i / (k(k+1))
  [1, 0, 1, 0, 1] → [1, 1, 0, 0, 1] : gain = 0.11111 = (2/(2×3)) / 3
5. Vérification exhaustive : 0 <= AP <= 1, et AP = 1 ssi tout est retrouvé en tête
  555 couples (classement, R) vérifiés
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : l'AP n'est pas « la moyenne des précisions aux pertinents trouvés ». C'est cette somme divisée par **tous** les pertinents qui existent. Sans ce dénominateur, la métrique devient Context Precision et récompense un retriever qui renvoie moins de documents.

## Squelette algorithmique

Pour chaque requête, les entrées sont la liste classée des identifiants renvoyés par le retriever, l'ensemble G des identifiants pertinents annotés et, si l'agent ne lit que le haut de la liste, une coupure K. La sortie est l'AP de chaque requête, puis la MAP du jeu. L'idée : un seul passage sur la liste, avec un compteur des pertinents déjà trouvés ; à chaque nouveau pertinent, on ajoute la précision à ce rang, et à la fin on divise par R = |G|, jamais par le nombre de pertinents trouvés.

```text
ALGORITHME AveragePrecision
ENTRÉES : classement d₁ … d_n (identifiants), ensemble G des pertinents annotés, coupure K (∞ si aucune)
SORTIE  : AP ∈ [0, 1], ou INDÉFINI si G est vide
    R ← |G|
    SI R = 0 ALORS
        RETOURNER INDÉFINI                      ▹ aucun pertinent : AP n'existe pas
    FIN SI
    vus ← ∅ ; trouvés ← 0 ; somme ← 0 ; k ← 1
    TANT QUE k ≤ n ET k ≤ K FAIRE
        SI d_k ∈ G ET d_k ∉ vus ALORS            ▹ un doublon ne compte qu'une fois
            trouvés ← trouvés + 1
            somme ← somme + trouvés / k          ▹ P@k au rang de ce pertinent
        FIN SI
        vus ← vus ∪ {d_k}
        k ← k + 1
    FIN TANT QUE
    RETOURNER somme / R                          ▹ R et non trouvés ; 0 ≤ AP ≤ 1

ALGORITHME MeanAveragePrecision
ENTRÉES : requêtes q₁ … q_m, chacune avec son classement et son ensemble G
SORTIE  : MAP ∈ [0, 1], ou INDÉFINI
    définies ← liste vide
    POUR j DE 1 À m FAIRE
        a ← AveragePrecision(q_j)
        SI a ≠ INDÉFINI ALORS
            ajouter a à définies
        SINON
            compter q_j parmi les requêtes hors périmètre   ▹ mesurées à part
        FIN SI
    FIN POUR
    SI définies est vide ALORS
        RETOURNER INDÉFINI
    FIN SI
    RETOURNER (Σ des éléments de définies) / |définies|
```

**Complexité :** pour une requête, construire l'ensemble G coûte O(R), puis la boucle TANT QUE fait au plus n tours, et chaque tour fait un nombre fixe d'opérations, dont deux tests d'appartenance à un ensemble en temps constant moyen (table de hachage) : l'AP coûte O(n + R) en temps. La mémoire supplémentaire est O(n + R) pour les ensembles `vus` et G ; si l'on reçoit directement la liste des pertinences 0/1, comme `average_precision`, elle tombe à O(1) en plus de la liste. Pour la MAP, on additionne ces coûts : O(Σ (n + R)) en temps, la somme portant sur toutes les requêtes, et O(m) en mémoire pour la liste des AP définies, ou O(1) avec une somme et un compteur courants. La vérification exhaustive du programme énumère les 2ⁿ classements de chaque longueur n ≤ 6 : son coût est exponentiel en n, ce qui est acceptable pour un test sur de petites listes, jamais pour une évaluation réelle.

**Du squelette au code :** la ligne R ← |G| correspond au paramètre `n_pertinents_total`, et le test « R = 0 » à `if n_pertinents_total == 0: return None`. Le test « d_k ∈ G et d_k ∉ vus » est fait en amont par `rel_depuis_ids`, qui transforme les identifiants en pertinences 0/1 en marquant les doublons à 0 ; `average_precision` reçoit ensuite cette liste et la coupe à K par `rel[:k_max]`. La boucle TANT QUE est la boucle `for k, v in enumerate(liste, start=1)`, avec `trouves += 1` puis `somme += trouves / k`. La division finale est `return somme / n_pertinents_total`, la ligne que l'ancienne version avait fausse. Le code ajoute une garde que le squelette rend inutile : si la liste de pertinences n'a pas été dédoublonnée et contient plus de pertinents que R, `average_precision` lève `ValueError`. MeanAveragePrecision est `mean_average_precision`, où la liste `definies` garde les AP différentes de `None`.

## Cas d'usage réels aux Émirats

Les volumes, seuils et classements ci-dessous sont illustratifs ; les règles citées sont celles du guide du parcours, à confirmer avec le texte en vigueur.

### Banque — une réponse de conformité qui a besoin de trois règles

Une banque de détail de Dubaï met à la disposition de ses conseillers un assistant qui répond aux questions de crédit à partir d'un recueil interne des règles de la CBUAE. À la question « un salarié qui gagne 25 000 AED par mois peut-il obtenir un prêt personnel de 600 000 AED sur 60 mois ? », une réponse juste doit s'appuyer sur trois passages : le ratio d'endettement total limité à 50 % du salaire, le plafond de 20 fois le salaire (ici 500 000 AED) et la durée maximale de 48 mois. La requête a donc R = 3. Le premier retriever testé place le passage sur les 50 % au rang 1 et rien d'autre d'utile dans ses cinq résultats : AP = 1/3 ≈ 0,333, alors que l'ancienne formule aurait affiché 1,0 et déclaré ce retriever parfait. L'agent, nourri de ce seul passage, aurait répondu « oui si l'endettement passe » en omettant deux motifs de refus, ce qui est une erreur de conseil. L'équipe exige une MAP d'au moins 0,80 sur un jeu de 150 questions de conformité avant tout changement d'index, et suit la part des réponses qui citent toutes les règles requises.

### Immobilier — les pièces d'un dossier de transfert

Une agence qui opère à Dubaï et à Abu Dhabi utilise un agent qui prépare la liste des pièces d'une revente. Pour « quelles pièces pour transférer un appartement loué à Dubai Marina ? », les annotateurs ont retenu quatre documents de procédure : titre de propriété, contrat Ejari, attestation de non-objection du promoteur et calcul des frais de transfert DLD de 4 % de la valeur, soit R = 4 (liste à confirmer avec la procédure en vigueur). Le retriever renvoie [Ejari, brochure, titre, attestation, brochure, frais], soit les pertinences [1, 0, 1, 1, 0, 1], et l'AP vaut (1 + 2/3 + 3/4 + 4/6) / 4 ≈ 0,771. Après l'ajout d'un reranker qui envoie les brochures en fin de liste, le classement devient [1, 1, 1, 1, 0, 0] et l'AP vaut 1. L'agent produit alors une liste complète du premier coup. Sans cette mesure, une pièce manquante n'apparaît qu'au rendez-vous de transfert, qui doit être reporté. L'indicateur suivi en production est le nombre de transferts reportés pour pièce manquante.

### Crypto — deux retrievers que le MRR ne départage pas

Une plateforme d'actifs virtuels agréée par la VARA fait instruire par un agent les demandes de retrait vers un portefeuille non hébergé. Pour une demande de 60 000 AED, trois procédures internes sont pertinentes : vérification renforcée de l'identité, collecte des informations du bénéficiaire et contrôle contre les listes de surveillance, donc R = 3. Le retriever A renvoie [1, 0, 0, 0, 0] et le retriever B [1, 1, 1, 0, 0]. Les deux ont un MRR de 1, puisque leur premier résultat est pertinent ; leurs AP valent 0,333 et 1. Seule l'AP voit que A laisse l'agent sans deux des trois procédures, et c'est B qui est retenu. Sans cette mesure, un retrait aurait pu être validé sans le contrôle des listes, ce que la plateforme doit justement empêcher. On suit la MAP par type d'opération et le nombre de dossiers renvoyés par la conformité pour contrôle manquant.

### Assurance — la même clause en arabe et en anglais

Un assureur auto et santé indexe chaque police dans ses deux langues, arabe et anglais. Pour « la franchise s'applique-t-elle à un bris de glace ? », trois clauses sont pertinentes : franchise, bris de glace et avenant de l'année, soit R = 3. Le retriever renvoie la clause de franchise en anglais, la même en arabe, puis la clause de bris de glace et l'avenant. Si l'on compte chaque version comme un pertinent distinct, la somme vaut 1 + 1 + 1 + 1 = 4 et l'« AP » atteint 4/3 ≈ 1,33, une valeur impossible qui trahit le doublon. En identifiant chaque clause par son numéro, quelle que soit la langue, on obtient [1, 0, 1, 1] et une AP de (1 + 2/3 + 3/4) / 3 ≈ 0,806, qui révèle aussi que le doublon occupe une place utile au rang 2. L'équipe ajoute alors un dédoublonnage par clause avant l'injection dans le prompt, et suit la part du contexte occupée par des doublons.

### RH — des questions sans réponse dans le corpus

Un cabinet RH présent dans plusieurs émirats évalue son assistant sur 40 questions, dont 4 portent sur des régimes absents de son corpus, par exemple une zone franche dont il n'a pas les règles internes. Pour ces 4 questions, R = 0 : leur AP est indéfinie et elles sortent de la MAP, calculée sur les 36 autres. Si un script les comptait pour 0, une MAP réelle de 0,82 serait publiée à 0,82 × 36/40 ≈ 0,738, et l'équipe chercherait un défaut de retrieval qui n'existe pas. Les 4 questions sont mesurées à part : l'agent doit répondre qu'il n'a pas l'information et orienter vers le texte applicable, et non inventer une règle. Pour une question sur l'indemnité de fin de service, R vaut 3 (21 jours par an les cinq premières années puis 30, plafond de 24 mois de salaire de base, exclusion des ressortissants émiriens et du DIFC). L'indicateur suivi est la MAP sur les questions couvertes et le taux de refus correct sur les autres.

### BTP — une coupure à K = 5 et deux conventions qui ne se comparent pas

Un groupe de construction qui mène de grands chantiers à Dubaï interroge un corpus de contrats de sous-traitance. Pour « retenue de garantie et TVA sur une facture de sous-traitant », 8 clauses sont pertinentes, mais l'agent n'injecte que K = 5 chunks. Avec la convention TREC, qui divise par R = 8, même un classement parfait [1, 1, 1, 1, 1] plafonne à AP@5 = 5/8 = 0,625 ; avec la convention qui divise par min(R, K), il vaut 1. Deux équipes qui publient leur « MAP@5 » sans dire laquelle des deux elles utilisent ne peuvent pas se comparer. Le groupe fixe la convention TREC, parce qu'elle rappelle que 3 clauses n'entrent jamais dans le contexte, et en tire une décision d'architecture : passer à K = 8 pour ces questions de synthèse, malgré le coût en tokens. On suit la MAP@K et le coût moyen du contexte par question.

## Pièges et limites

- **Diviser par les pertinents retrouvés.** C'est le bug corrigé ici : on obtient Context Precision, qui récompense un retriever qui renvoie moins de documents.
- **Prendre R dans la liste renvoyée.** R vient de l'annotation du corpus, pas des résultats : sinon, les pertinents oubliés disparaissent du calcul.
- **Compter deux fois le même document.** Un doublon peut faire dépasser 1 à l'AP. On dédoublonne par identifiant avant de calculer.
- **Mettre 0 ou 1 pour une requête sans pertinent.** L'AP est indéfinie : `None`, exclue de la moyenne, et la requête se mesure par un autre indicateur.
- **Comparer des AP@K de conventions différentes.** Division par R ou par min(R, K) : la convention fait partie de la métrique et se publie avec le chiffre.

### Exercice feuille blanche

1. Sans regarder le code, écrire `average_precision(rel, n_pertinents_total)` à partir de la forme par les rangs, puis vérifier qu'elle renvoie 0,75556 pour [1, 0, 1, 0, 1] avec R = 3.
2. Prédire, puis vérifier : que vaut l'AP de [0, 0, 1, 1] avec R = 2 ? Et avec R = 4 ? (Réponses : (1/3 + 2/4)/2 ≈ 0,41667 ; puis la moitié, ≈ 0,20833.)
3. Trouver le bug : une variante se termine par `return somme / trouves`. Sur quels classements donne-t-elle encore la bonne valeur ? (Réponse : seulement quand tous les pertinents sont retrouvés, c'est-à-dire quand le rappel vaut 1.)

## Pour aller plus loin

L'AP interpolée (11 points de rappel, utilisée dans les anciennes campagnes TREC et en détection d'objets) remplace chaque précision par la meilleure précision obtenue à un rappel supérieur. La GMAP, moyenne géométrique des AP, donne plus de poids aux requêtes difficiles. La R-précision, Precision@R, est une alternative à une seule valeur, très corrélée à l'AP. Pour des pertinences graduées, on revient au NDCG de l'étape 28.

> Suite : [Perplexité en évaluation](<62-Evaluation-Formule-Perplexite.md>) — étape 62.
