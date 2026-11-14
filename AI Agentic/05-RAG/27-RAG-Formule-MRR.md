# Étape 27 — RAG — Mean Reciprocal Rank (MRR)

> Étape 27 du parcours · Prérequis : [Precision@k](<26-RAG-Formule-Precision-at-k.md>) · Suite : [NDCG](<28-RAG-Formule-NDCG.md>)

**Dossier :** 05-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  
**Nom du fichier :** 27-RAG-Formule-MRR.md

## Définition

Le MRR (Mean Reciprocal Rank, rang réciproque moyen) mesure à quelle hauteur apparaît le **premier** document pertinent, en moyenne sur un jeu de questions. Pour chaque question, on prend le rang de ce premier document pertinent et on en calcule l'inverse : 1 s'il est premier, 0,5 s'il est deuxième, 0,2 s'il est cinquième. Si aucun document pertinent n'est trouvé (ou aucun dans les k premiers, pour le MRR@k), le rang réciproque vaut **0** : on ne divise jamais par zéro, on considère que le rang est infini. Le MRR est la moyenne de ces valeurs ; il vaut 1 quand le premier résultat est toujours bon, et il ignore tout ce qui suit le premier document pertinent. Il convient donc aux questions où une seule bonne source suffit, et il complète la Precision@k de l'étape 26, qui ignore l'ordre.

## Rôle dans un agent

Après l'action de recherche, l'agent lit ses résultats dans l'ordre, et beaucoup d'agents n'utilisent vraiment que le premier ou les deux premiers : un routeur qui choisit la procédure à suivre d'après le meilleur résultat, une réponse courte qui cite une seule source, un agent qui ouvre le premier document pour en extraire un montant. Dans ces cas, ce qui compte est la position du premier bon document, et c'est exactement ce que mesure le MRR. On l'utilise hors ligne pour comparer deux retrievers ou deux rerankers sur un jeu de questions annotées (les fonctions de score sont celles des étapes 22 à 24), et en production pour vérifier qu'une mise à jour de l'index ne fait pas reculer les bonnes sources. Le composant visé est d'abord le **reranker**, dont le rôle est précisément de faire remonter le bon document en tête. Quand la réponse a besoin de plusieurs documents à la fois, le MRR ne suffit plus : on lui ajoute le Recall@k (étape 25) ou le NDCG (étape 28).

## Équation complète

Rang réciproque de la question i, défini par morceaux :

$$
\text{RR}_i = \begin{cases} \dfrac{1}{\text{rang}_i} & \text{si un document pertinent est trouvé,} \\ 0 & \text{sinon (on pose } \text{rang}_i = +\infty\text{).} \end{cases}
$$

Version coupée à k, quand l'agent ne lit que les k premiers résultats :

$$
\text{RR}_i@k = \begin{cases} \dfrac{1}{\text{rang}_i} & \text{si } \text{rang}_i \le k, \\ 0 & \text{sinon.} \end{cases}
$$

Moyenne sur le jeu de questions Q :

$$
\text{MRR@}k = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \text{RR}_i@k
$$

Part des questions résolues dans les k premiers (HitRate@k, aussi appelé Success@k) :

$$
\text{HitRate@}k = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \mathbf{1}[\text{rang}_i \le k]
$$

Encadrement :

$$
\frac{\text{HitRate@}k}{k} \le \text{MRR@}k \le \text{HitRate@}k
$$

Inégalité de Jensen, quand toutes les questions sont résolues (r̄ est le rang moyen) :

$$
\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rang}_i} \;\ge\; \frac{1}{\bar{r}}
$$

## Décryptage des symboles

$$
Q
$$

**Sens :** jeu de questions d'évaluation · **Type / plage :** ensemble fini · **Variable Python :** `rangs` (un rang par question)

$$
\text{rang}_i
$$

**Sens :** rang, compté à partir de 1, du premier document pertinent pour la question i, dans la liste dédoublonnée · **Type / plage :** entier ≥ 1, ou +∞ si rien n'est trouvé · **Variable Python :** `first_relevant_rank(...)`, `None` pour +∞

$$
\text{RR}_i
$$

**Sens :** rang réciproque de la question i · **Type / plage :** réel dans [0, 1] · **Variable Python :** `reciprocal_rank(rang)`

$$
k
$$

**Sens :** nombre de résultats que l'agent lit (coupure) · **Type / plage :** entier ≥ 1, ou pas de coupure · **Variable Python :** `k` (ou `None`)

$$
\text{MRR@}k
$$

**Sens :** moyenne des rangs réciproques · **Type / plage :** réel dans [0, 1], indéfini si Q est vide · **Variable Python :** `mrr(rangs, k)`

$$
\text{HitRate@}k
$$

**Sens :** part des questions résolues dans les k premiers · **Type / plage :** réel dans [0, 1] · **Variable Python :** `hit_rate(rangs, k)`

$$
\bar{r}
$$

**Sens :** rang moyen des questions résolues · **Type / plage :** réel ≥ 1 · **Variable Python :** `sum(rangs) / len(rangs)`

$$
\mathbf{1}[\cdot]
$$

**Sens :** indicatrice : 1 si la condition est vraie, 0 sinon · **Type / plage :** 0 ou 1 · **Variable Python :** —

## Démonstration

### 1. Pourquoi 0, et jamais « 1/0 », quand rien n'est trouvé

L'ancien texte disait « si aucun, on considère souvent 0 », ce qui laissait croire que le **rang** valait 0 et invitait à calculer 1/0. La bonne lecture est l'inverse : quand aucun document pertinent n'apparaît, on pose rangᵢ = +∞, et c'est le **rang réciproque** qui vaut 0. Ce choix prolonge naturellement les autres cas, **parce que** 1/r tend vers 0 quand r tend vers +∞ : un pertinent au rang 100 vaut 0,01, au rang 1 000 il vaut 0,001, et pas trouvé du tout il vaut 0. Dans le code, ce cas est porté par `None`, jamais par un rang 0 ou négatif. Un rang est un entier ≥ 1 par construction, donc toute autre valeur trahit un bug en amont (des rangs comptés à partir de 0, un indice -1 renvoyé par une recherche ratée) et doit lever `ValueError`. L'ancienne fonction transformait au contraire un rang négatif en « non trouvé » sans rien dire : `[1, -2]` donnait 0,5.

### 2. Encadrement par le HitRate

Fixons une question i et une coupure k. Si son premier pertinent est dans les k premiers, on a 1 ≤ rangᵢ ≤ k, donc 1/k ≤ RRᵢ@k ≤ 1, **parce que** la fonction r ↦ 1/r est décroissante. Sinon, RRᵢ@k = 0, et l'indicatrice 𝟏[rangᵢ ≤ k] vaut 0 elle aussi. Dans les deux cas :

$$
\frac{1}{k}\,\mathbf{1}[\text{rang}_i \le k] \;\le\; \text{RR}_i@k \;\le\; \mathbf{1}[\text{rang}_i \le k]
$$

En faisant la moyenne de ces inégalités sur les |Q| questions (une moyenne conserve les inégalités terme à terme), on obtient HitRate@k / k ≤ MRR@k ≤ HitRate@k. L'égalité à droite a lieu quand chaque question résolue l'est au rang 1, l'égalité à gauche quand chacune l'est exactement au rang k. En particulier, MRR@1 = HitRate@1 : à k = 1, les deux métriques se confondent. Le MRR ne dépasse donc jamais la part de questions résolues. Un MRR de 0,7 avec un HitRate@5 de 0,72 dit « presque toujours au rang 1 quand c'est trouvé » ; le même MRR avec un HitRate@5 de 1 dit « toujours trouvé, mais souvent au rang 2 ou 3 ».

### 3. Le MRR@k croît avec k

Augmenter k ne peut que faire passer un RRᵢ@k de 0 à 1/rangᵢ, quand le rang de la question passe sous la coupure, et jamais l'inverse. Donc MRR@k est croissant en k, et il atteint le MRR sans coupure dès que k dépasse le plus grand rang trouvé. Contrairement à la précision de l'étape 26, ajouter des résultats ne fait jamais baisser le MRR : c'est le coût du contexte, pas la métrique, qui limite k.

### 4. La moyenne des 1/r n'est pas l'inverse de la moyenne des r

Il est tentant de lire un MRR de 0,5 comme « le bon document est en moyenne au rang 2 ». C'est faux. Contre-exemple chiffré : deux questions résolues aux rangs 1 et 3. Le MRR vaut (1 + 1/3)/2 = 0,667, alors que le rang moyen vaut 2 et que son inverse vaut 0,5. Ce n'est pas un hasard de l'exemple : quand toutes les questions sont résolues, on a toujours MRR ≥ 1/r̄. Preuve par l'inégalité de Cauchy-Schwarz de l'étape 14, appliquée aux vecteurs (√r₁, …, √rₙ) et (1/√r₁, …, 1/√rₙ), dont le produit scalaire vaut n :

$$
n^2 = \left(\sum_{i=1}^{n} \sqrt{r_i} \cdot \frac{1}{\sqrt{r_i}}\right)^2 \le \left(\sum_{i=1}^{n} r_i\right)\left(\sum_{i=1}^{n} \frac{1}{r_i}\right)
$$

En divisant les deux membres par n ∑ rᵢ, qui est positif, on obtient

$$
\frac{1}{n}\sum \frac{1}{r_i} \ge \frac{n}{\sum r_i} = \frac{1}{\bar{r}} .
$$

C'est l'inégalité de Jensen pour la fonction convexe r ↦ 1/r (sa dérivée seconde 2/r³ est positive), et l'égalité n'a lieu que si tous les rangs sont égaux : [2, 2] donne bien MRR = 0,5 = 1/2. Sur [1, 3], on vérifie (1 + 3)(1 + 1/3) ≈ 5,33 ≥ 4. Ce que vaut 1/MRR, ici 1,5, est la **moyenne harmonique** des rangs, toujours inférieure ou égale à leur moyenne arithmétique : elle donne une image trop optimiste du rang typique.

### 5. Tout se joue en tête

Faire gagner une place au premier pertinent, du rang r au rang r − 1, augmente son rang réciproque de :

$$
\frac{1}{r-1} - \frac{1}{r} = \frac{r - (r-1)}{r(r-1)} = \frac{1}{r(r-1)}
$$

Le gain vaut 0,5 pour passer du rang 2 au rang 1, 0,1667 du rang 3 au rang 2, et seulement 0,0111 du rang 10 au rang 9. Le MRR récompense donc presque uniquement les améliorations en tête de liste, **parce que**

$$
\frac{1}{r(r-1)}
$$

décroît comme 1/r². C'est voulu quand l'agent ne lit que le premier résultat ; c'est un défaut quand il en lit dix.

### 6. Seul le premier pertinent compte, et ce que garantit un MRR élevé

Les classements « pertinent, pertinent, pertinent » et « pertinent, non, non » ont le même rang réciproque, 1 : le MRR ne voit ni le deuxième ni le troisième document utile. En contrepartie, un MRR élevé garantit beaucoup de premiers résultats justes. Une question dont le premier pertinent n'est pas au rang 1 a RRᵢ ≤ 1/2, donc elle ajoute au moins 1/2 à la somme ∑ᵢ (1 − RRᵢ). Avec m questions de ce type, |Q| (1 − MRR) ≥ m/2, d'où :

$$
\text{Success@}1 = 1 - \frac{m}{|Q|} \ge 2\,\text{MRR} - 1
$$

Un MRR de 0,9 garantit donc qu'au moins 80 % des questions ont un document pertinent au rang 1. La borne est atteinte par huit questions au rang 1 et deux au rang 2 : MRR = (8 + 2 × 0,5)/10 = 0,9 et Success@1 = 0,8. Le même raisonnement vaut pour le MRR@k, puisqu'une question coupée a un rang réciproque nul, donc lui aussi inférieur à 1/2.

### 7. Exemple fait à la main (le code reprend ces nombres)

Quatre questions posées à l'assistant d'un service public en ligne :

| Question | Résultats renvoyés, dans l'ordre | Pertinents | rangᵢ | RRᵢ |
|---|---|---|---|---|
| q1 | `eid-renouvellement`, `eid-frais`, `horaires` | `eid-renouvellement` | 1 | 1 |
| q2 | `eid-frais`, `eid-frais`, `horaires`, `carte-perdue` | `carte-perdue` | 3 | 0,333 |
| q3 | `horaires`, `eid-frais`, `visa-statut` | `adresse-modification` | +∞ | 0 |
| q4 | `eid-frais`, `delais`, `horaires` | `delais`, `delais-urgence` | 2 | 0,5 |

Pour q2, le doublon `eid-frais` est retiré avant de compter les rangs, avec la même convention qu'à l'étape 26 : `carte-perdue` est au rang 3, pas au rang 4. Le MRR vaut

$$
(1 + 1/3 + 0 + 1/2)/4 = 1{,}8333/4 \approx 0{,}4583 .
$$

Coupé à k = 2, q2 ne compte plus :

$$
\text{MRR@}2 = (1 + 0 + 0 + 0{,}5)/4 = 0{,}375 ,
$$

avec HitRate@2 = 2/4 = 0,5, et l'encadrement 0,25 ≤ 0,375 ≤ 0,5 est vérifié. À k = 1, MRR@1 = HitRate@1 = 0,25. À k = 5, HitRate@5 = 0,75 et 0,15 ≤ 0,4583 ≤ 0,75.

## Effets et comportement

- **Un premier pertinent plus haut fait monter le MRR**, d'autant plus fortement qu'on est près de la tête (point 5).
- **Un MRR proche de 1** signifie bien que le bon document est presque toujours premier, et on peut le chiffrer : Success@1 ≥ 2 MRR − 1 (point 6).
- **Le MRR ne voit que le premier pertinent.** Il convient aux questions à source unique (une procédure, une clause, un barème) et sous-évalue un moteur qui ramène toutes les sources d'une question qui en demande plusieurs. L'ancien texte le disait « particulièrement utile quand on ne récupère que peu de documents » : le bon critère n'est pas la taille du top-k, c'est le nombre de documents dont la réponse a besoin.
- **Il ne se convertit pas en rang moyen** : 1/MRR est la moyenne harmonique des rangs, plus petite que le rang moyen (point 4).
- **Coupure** : le MRR@k croît avec k et reste sous le HitRate@k ; on choisit k égal au nombre de résultats que l'agent lit réellement, et on écrit toujours la coupure à côté du chiffre.

## Du symbole au code Python

$$
\text{rang}_i
$$

**Variable ou fonction :** `first_relevant_rank(retrouves, pertinents)`, qui renvoie un `int` ou `None`

**Symbole :** +∞ (rien trouvé) · **Variable ou fonction :** `None`

$$
\text{RR}_i@k
$$

**Variable ou fonction :** `reciprocal_rank(rang, k)`

$$
\text{MRR@}k
$$

**Variable ou fonction :** `mrr(rangs, k)`

$$
\text{HitRate@}k
$$

**Variable ou fonction :** `hit_rate(rangs, k)`

$$
\frac{1}{r(r-1)}
$$

**Variable ou fonction :** `1 / (r - 1) - 1 / r`

### Déroulé, ligne par ligne

**`dedupliquer(retrouves)`** est la fonction de l'étape 26 : `list(dict.fromkeys(retrouves))` garde la première occurrence de chaque identifiant, dans l'ordre.

**`first_relevant_rank(retrouves, pertinents)`**.

- `for rang, doc in enumerate(dedupliquer(retrouves), start=1)` : `start=1` fait commencer les rangs à 1, comme dans la formule ; sans lui, le premier document aurait le rang 0. Pour q2, la liste dédoublonnée est `["eid-frais", "horaires", "carte-perdue"]`.
- `if doc in pertinents: return rang` : on s'arrête au premier pertinent ; pour q2, cela se produit à `rang = 3`.
- `return None` : la boucle est allée au bout sans rien trouver (q3). `None` représente le rang infini.

**`reciprocal_rank(rang, k)`**.

- `if rang is None: return 0.0` : rien trouvé, donc RR = 0 (point 1).
- `if isinstance(rang, bool) or not isinstance(rang, int) or rang < 1: raise ValueError(...)` : refuse `0`, `-2`, `1.5`, et aussi `True`, que Python considère comme l'entier 1. Un rang invalide est un bug en amont, pas une absence de résultat.
- `if k is not None and rang > k: return 0.0` : la coupure du MRR@k ; avec `k = 2`, le rang 3 de q2 donne 0.
- `return 1.0 / rang` : 1, 0.3333 ou 0.5 dans l'exemple.

**`mrr(rangs, k)`** vérifie `k`, renvoie `None` pour un jeu vide, puis fait la moyenne des `reciprocal_rank(r, k)`. L'ancienne version renvoyait `0.0` pour un jeu vide, valeur indiscernable d'un moteur qui ne trouve jamais rien. Sur `[1, 3, None, 2]`, la somme vaut 1,8333 et la moyenne 0,4583.

**`hit_rate(rangs, k)`** compte les questions dont le rang réciproque coupé à `k` est strictement positif, c'est-à-dire les questions résolues dans les `k` premiers. Passer par `reciprocal_rank` réutilise la même validation des rangs.

**`ancien_mrr(ranks)`** est l'ancienne fonction du fichier, gardée pour le contre-exemple du point 1.

**`main()`**, bloc par bloc.

1. Les rangs des quatre questions sont calculés à partir des listes renvoyées, pas recopiés à la main : `[1, 3, None, 2]`. Le MRR vaut 0,4583.
2. Pour `k` égal à 1, 2, 3 et 5, on vérifie les valeurs du point 7 et l'encadrement `h / k <= m <= h`. La suite des MRR@k, pour `k` allant de 1 à 5, est croissante et finit égale au MRR sans coupure (point 3).
3. Sur `[1, 3]`, le MRR vaut 0,6667 alors que l'inverse du rang moyen vaut 0,5 ; `1 / m` vaut 1,5, la moyenne harmonique. On vérifie aussi l'inégalité de Cauchy-Schwarz (1 + 3)(1 + 1/3) ≥ 4 et le cas d'égalité `[2, 2]`.
4. Les gains d'une place valent 0,5, 0,1667 et 0,0111, et chacun est égal à

$$
\frac{1}{r(r-1)} .
$$

5. Deux listes qui ont le même premier résultat pertinent ont le même RR, quel que soit le nombre de pertinents qui suivent. Les rangs `[1] * 8 + [2, 2]` donnent un MRR de 0,9 et un Success@1 de 0,8 : la borne 2 MRR − 1 est atteinte.
6. Les rangs `-2`, `0` et `1.5` lèvent `ValueError` ; si l'un d'eux passait, `raise AssertionError` arrêterait le programme. L'ancienne fonction donnait 0,5 pour `[1, -2]` et 0,0 pour un jeu vide.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`dedupliquer(retrouves)`** — C'est la même fonction qu'à l'étape 26, un portier qui ne laisse entrer chaque invité qu'une seule fois et à la première place où il s'est présenté : elle reçoit la liste ordonnée des identifiants renvoyés par le moteur, la fait passer par `dict.fromkeys`, qui ne garde qu'une entrée par clé dans l'ordre d'insertion, et renvoie la liste ainsi nettoyée. Pour la question q2, où le même document de frais apparaît deux fois en tête, elle rend une liste de trois éléments au lieu de quatre, si bien que le premier pertinent se trouve au rang 3 et non au rang 4.

**`first_relevant_rank(retrouves, pertinents)`** — Cette fonction joue le lecteur patient qui descend la liste de résultats, doigt sur la page, jusqu'à la première réponse utile : elle reçoit la liste des documents retrouvés et l'ensemble des pertinents, dédoublonne la liste avec `dedupliquer`, puis la parcourt en numérotant les rangs à partir de 1 et renvoie le rang du premier document pertinent rencontré. Si elle arrive au bout sans rien trouver, elle renvoie `None`, qui représente un rang infini ; sur les quatre questions des usagers, elle produit ainsi les rangs 1, 3, `None` et 2, calculés à partir des listes et non recopiés à la main.

**`reciprocal_rank(rang, k)`** — Elle transforme ce rang en note, à la manière d'un barème qui accorde tout à qui répond du premier coup et de moins en moins ensuite : la fonction reçoit un rang, ou `None`, et une coupure k facultative, renvoie 0,0 si le rang vaut `None`, lève `ValueError` si le rang n'est pas un entier au moins égal à 1, en refusant au passage `True`, que Python prendrait pour 1, puis renvoie 0,0 si le rang dépasse la coupure, et sinon 1 / rang. Les rangs 1, 3 et 2 de l'exemple donnent ainsi 1, 0,3333 et 0,5 ; avec k = 2, le rang 3 de q2 ne rapporte plus rien.

**`hit_rate(rangs, k)`** — C'est un pointeur qui ne note pas la vitesse, seulement la réussite : a-t-on trouvé quelque chose d'utile dans les k premiers ? La fonction reçoit la liste des rangs et la coupure k, lève `ValueError` si k est inférieur à 1, renvoie `None` pour un jeu vide, et sinon compte les questions dont le rang réciproque coupé à k est strictement positif, avant de diviser par le nombre de questions. En passant par `reciprocal_rank`, elle profite de la même validation des rangs ; sur l'exemple, elle vaut 0,25 à k = 1, 0,5 à k = 2 et 0,75 à partir de k = 3, et elle encadre le MRR@k entre HitRate@k / k et HitRate@k.

**`ancien_mrr(ranks)`** — Cette fonction est l'ancienne version du fichier, gardée comme témoin d'un barème trop indulgent : elle reçoit une liste de rangs, renvoie 0,0 pour une liste vide, ce qui confond un jeu sans question avec un moteur qui ne trouve jamais rien, et, pour chaque rang, ajoute 1 / rang s'il est positif et 0 sinon, avant de diviser par le nombre de rangs. Un rang aberrant comme −2 passe donc sans bruit et compte comme un échec ordinaire : sur [1, −2], elle donne 0,5, là où la nouvelle fonction `mrr` lève `ValueError`.

**`main()`** — Le chef d'orchestre déroule six vérifications : il calcule les rangs 1, 3, `None` et 2 des quatre questions des usagers et le MRR de 0,4583, puis, pour k égal à 1, 2, 3 et 5, vérifie le MRR@k et le HitRate@k attendus ainsi que leur encadrement, et constate que la suite des MRR@k croît jusqu'au MRR sans coupure. Il illustre ensuite l'inégalité de Jensen, avec un MRR de 0,6667 sur les rangs 1 et 3 contre 0,5 pour l'inverse du rang moyen, mesure les gains d'une place, 0,5, 0,1667 et 0,0111, montre que seul le premier pertinent compte et que la borne 2 MRR − 1 est atteinte, et termine en refusant les rangs −2, 0 et 1,5. Chaque nombre est gardé par un `assert`, et la ligne finale n'annonce le succès que si tous ont tenu.

```python
"""Étape 27 — MRR : rang réciproque par morceaux, bornes par le HitRate, inégalité de Jensen, rangs invalides."""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def dedupliquer(retrouves: list[str]) -> list[str]:
    """Première occurrence de chaque identifiant, dans l'ordre (même convention qu'à l'étape 26)."""
    return list(dict.fromkeys(retrouves))


def first_relevant_rank(retrouves: list[str], pertinents: set[str]) -> int | None:
    """Rang (à partir de 1) du premier document pertinent de la liste dédoublonnée ; None s'il n'y en a aucun."""
    for rang, doc in enumerate(dedupliquer(retrouves), start=1):
        if doc in pertinents:
            return rang
    return None


def reciprocal_rank(rang: int | None, k: int | None = None) -> float:
    """RR = 1/rang si un pertinent est trouvé (dans les k premiers pour MRR@k) ; 0 sinon (rang = +inf)."""
    if rang is None:
        return 0.0
    if isinstance(rang, bool) or not isinstance(rang, int) or rang < 1:
        raise ValueError(f"rang invalide : {rang!r} (il faut un entier >= 1, ou None si rien n'est trouvé)")
    if k is not None and rang > k:
        return 0.0
    return 1.0 / rang


def mrr(rangs: list[int | None], k: int | None = None) -> float | None:
    """MRR (MRR@k si k est donné) = moyenne des rangs réciproques ; None sur un jeu vide."""
    if k is not None and k < 1:
        raise ValueError("k doit être un entier >= 1")
    if not rangs:
        return None
    return sum(reciprocal_rank(r, k) for r in rangs) / len(rangs)


def hit_rate(rangs: list[int | None], k: int) -> float | None:
    """HitRate@k = part des questions qui ont un document pertinent dans leurs k premiers résultats."""
    if k < 1:
        raise ValueError("k doit être un entier >= 1")
    if not rangs:
        return None
    return sum(1 for r in rangs if reciprocal_rank(r, k) > 0) / len(rangs)


def ancien_mrr(ranks: list[int]) -> float:
    """Ancienne version du fichier, gardée pour le contre-exemple."""
    if not ranks:
        return 0.0
    return sum(1.0 / r if r > 0 else 0.0 for r in ranks) / len(ranks)


def main() -> None:
    print("1. Quatre questions d'usagers, rang du premier document pertinent")
    jeu = [
        (["eid-renouvellement", "eid-frais", "horaires"], {"eid-renouvellement"}),
        (["eid-frais", "eid-frais", "horaires", "carte-perdue"], {"carte-perdue"}),   # doublon en tête
        (["horaires", "eid-frais", "visa-statut"], {"adresse-modification"}),          # rien de pertinent
        (["eid-frais", "delais", "horaires"], {"delais", "delais-urgence"}),
    ]
    rangs = [first_relevant_rank(retrouves, pertinents) for retrouves, pertinents in jeu]
    assert rangs == [1, 3, None, 2]                      # q2 : rang 3 après dédoublonnage (4 sans)
    for i, r in enumerate(rangs, start=1):
        print(f"  q{i}  rang = {str(r):<4}  RR = {reciprocal_rank(r):.4f}")
    total = mrr(rangs)
    print(f"  MRR = (1 + 1/3 + 0 + 1/2) / 4 = {total:.4f}")
    assert abs(total - (1 + 1 / 3 + 0 + 1 / 2) / 4) < 1e-12 and round(total, 4) == 0.4583

    print("2. MRR@k croît avec k et reste entre HitRate@k / k et HitRate@k")
    attendus = {1: (0.25, 0.25), 2: (0.375, 0.5), 3: (0.4583, 0.75), 5: (0.4583, 0.75)}
    for k, (m_att, h_att) in attendus.items():
        m, h = mrr(rangs, k), hit_rate(rangs, k)
        print(f"  k = {k}  HitRate/k = {h / k:.4f} <= MRR@k = {m:.4f} <= HitRate = {h:.4f}")
        assert round(m, 4) == m_att and h == h_att and h / k <= m <= h
    suite = [mrr(rangs, k) for k in range(1, 6)]
    assert all(a <= b for a, b in zip(suite, suite[1:])) and suite[-1] == total   # croissante, puis égale au MRR

    print("3. Jensen : la moyenne des 1/r n'est pas 1/(moyenne des r)")
    m = mrr([1, 3])
    print(f"  rangs [1, 3] : MRR = {m:.4f} ; 1 / moyenne = {1 / 2:.4f} ; 1 / MRR = {1 / m:.4f} (moyenne harmonique)")
    assert round(m, 4) == 0.6667 and m > 1 / ((1 + 3) / 2) and abs(1 / m - 1.5) < 1e-12
    assert (1 + 3) * (1 + 1 / 3) >= 2 ** 2                                   # Cauchy-Schwarz : (Σr)(Σ1/r) >= n²
    assert mrr([2, 2]) == 1 / 2                                               # égalité quand tous les rangs sont égaux

    print("4. Gagner une place rapporte 1/(r(r - 1)) : tout se joue en tête")
    gains = {r: 1 / (r - 1) - 1 / r for r in (2, 3, 10)}
    print(f"  2 → 1 : +{gains[2]:.4f} ; 3 → 2 : +{gains[3]:.4f} ; 10 → 9 : +{gains[10]:.4f}")
    assert all(abs(g - 1 / (r * (r - 1))) < 1e-12 for r, g in gains.items())
    assert [round(g, 4) for g in gains.values()] == [0.5, 0.1667, 0.0111]

    print("5. Seul le premier pertinent compte ; et MRR = 0.9 garantit Success@1 >= 0.8")
    assert reciprocal_rank(first_relevant_rank(["a", "b", "c"], {"a", "b", "c"})) == 1.0
    assert reciprocal_rank(first_relevant_rank(["a", "x", "y"], {"a", "b", "c"})) == 1.0
    bon = [1] * 8 + [2, 2]
    m, s1 = mrr(bon), hit_rate(bon, 1)
    print(f"  rangs [1 × 8, 2, 2] : MRR = {m:.4f} ; Success@1 = {s1:.4f} = 2 × MRR - 1 (borne atteinte)")
    assert abs(m - 0.9) < 1e-12 and s1 == 0.8 and s1 >= 2 * m - 1 - 1e-12
    assert hit_rate([1] * 9 + [None], 1) == 0.9 >= 2 * mrr([1] * 9 + [None]) - 1

    print("6. Rangs invalides et jeu vide")
    for invalide in (-2, 0, 1.5):
        try:
            mrr([1, invalide])
        except ValueError:
            pass
        else:
            raise AssertionError(f"le rang {invalide} aurait dû être refusé")
    print(f"  rangs -2, 0, 1.5 → ValueError ; jeu vide → {mrr([])} (l'ancienne fonction donnait {ancien_mrr([1, -2])} et {ancien_mrr([])})")
    assert ancien_mrr([1, -2]) == 0.5 and mrr([]) is None and ancien_mrr([]) == 0.0

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Quatre questions d'usagers, rang du premier document pertinent
  q1  rang = 1     RR = 1.0000
  q2  rang = 3     RR = 0.3333
  q3  rang = None  RR = 0.0000
  q4  rang = 2     RR = 0.5000
  MRR = (1 + 1/3 + 0 + 1/2) / 4 = 0.4583
2. MRR@k croît avec k et reste entre HitRate@k / k et HitRate@k
  k = 1  HitRate/k = 0.2500 <= MRR@k = 0.2500 <= HitRate = 0.2500
  k = 2  HitRate/k = 0.2500 <= MRR@k = 0.3750 <= HitRate = 0.5000
  k = 3  HitRate/k = 0.2500 <= MRR@k = 0.4583 <= HitRate = 0.7500
  k = 5  HitRate/k = 0.1500 <= MRR@k = 0.4583 <= HitRate = 0.7500
3. Jensen : la moyenne des 1/r n'est pas 1/(moyenne des r)
  rangs [1, 3] : MRR = 0.6667 ; 1 / moyenne = 0.5000 ; 1 / MRR = 1.5000 (moyenne harmonique)
4. Gagner une place rapporte 1/(r(r - 1)) : tout se joue en tête
  2 → 1 : +0.5000 ; 3 → 2 : +0.1667 ; 10 → 9 : +0.0111
5. Seul le premier pertinent compte ; et MRR = 0.9 garantit Success@1 >= 0.8
  rangs [1 × 8, 2, 2] : MRR = 0.9000 ; Success@1 = 0.8000 = 2 × MRR - 1 (borne atteinte)
6. Rangs invalides et jeu vide
  rangs -2, 0, 1.5 → ValueError ; jeu vide → None (l'ancienne fonction donnait 0.5 et 0.0)
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : le MRR est simple à calculer mais facile à mal lire. Un rang infini vaut 0, un rang invalide est une erreur, la moyenne des inverses n'est pas l'inverse de la moyenne, et le chiffre ne dit jamais plus que la part de questions résolues.

## Squelette algorithmique

Le MRR ne regarde que le rang du premier passage pertinent de chaque question. Le programme y ajoute le HitRate@k, qui compte seulement si ce premier pertinent est dans les k premiers.

```text
ALGORITHME MRR
ENTRÉES : pour chaque question : classement retrouvé, ensemble des pertinents ; coupure k (facultative)
SORTIE  : MRR@k et HitRate@k

  rangs ← liste vide
  POUR CHAQUE question FAIRE
      classement ← Dédoublonner(classement)
      rang ← position (à partir de 1) du premier document pertinent, ou aucun
      ajouter rang à rangs
  FIN POUR
  POUR CHAQUE rang FAIRE
      RR ← 1 / rang SI rang existe ET (pas de coupure OU rang ≤ k) SINON 0
  FIN POUR
  MRR ← moyenne des RR
  HitRate@k ← proportion des questions dont le rang existe et vaut au plus k
  RETOURNER MRR, HitRate@k
```

**Complexité.** Trouver le premier pertinent coûte O(n) dans le pire cas pour un classement de longueur n, mais s'arrête dès le premier trouvé. Sur Q questions, le tout coûte O(Q × n) au pire, puis O(Q) pour les deux moyennes.

**Du squelette au code.** `dedupliquer` puis `first_relevant_rank` donnent le rang, `reciprocal_rank` applique la coupure à k, `mrr` fait la moyenne et `hit_rate` la proportion. `ancien_mrr` reproduit l'ancienne version, qui codait « aucun pertinent » par un rang 0, une valeur qu'un vrai rang ne peut pas prendre, et qui ne savait pas couper à k : la nouvelle version code l'absence par `None`, refuse tout rang inférieur à 1 et applique la coupure dans `reciprocal_rank`.

## Cas d'usage réels aux Émirats

Les valeurs de MRR, de coupure et de seuil ci-dessous sont illustratives : en production, on les mesure sur un jeu de questions annotées propre à chaque métier.

### Banque — la bonne fiche produit en premier

Une banque de détail de Dubaï a branché un routeur sur l'assistant de son centre d'appels : pour chaque question, l'agent ouvre la **première** fiche produit renvoyée par la recherche et en extrait les conditions (durée, taux, frais) avant de répondre. Les fiches couvrent les prêts personnels, les hypothèques, les cartes, la Murabaha et l'Ijara, et plusieurs se ressemblent beaucoup, comme la Murabaha automobile et le prêt auto conventionnel. Sur 400 questions annotées, le MRR@3 passe de 0,62 avec le cosinus seul à 0,81 avec un reranker ; avec un HitRate@3 de 0,88, l'encadrement du point 2 dit que la bonne fiche, quand elle est dans les trois premières, est le plus souvent en tête, et la borne du point 6 garantit au moins 2 × 0,81 − 1 = 0,62, soit 62 % de premières fiches justes. La décision de l'agent dépend directement de ce rang : si la bonne fiche est deuxième, il décrit la mauvaise offre avec assurance. Sans le MRR, l'équipe aurait mesuré un Recall@3 satisfaisant et conclu que tout allait bien, alors que l'agent ne lit que le premier résultat. Une offre de finance islamique décrite avec les conditions d'un prêt conventionnel est une erreur de conformité, et un prêt personnel présenté avec une durée de plus de 48 mois contredirait les règles de la CBUAE. On suit le MRR@1, c'est-à-dire la part de premières fiches justes, sur un échantillon hebdomadaire, avec une alerte sous 0,75.

### Crypto — une mise à jour de l'index qui fait reculer les bonnes sections

Une plateforme d'actifs virtuels agréée par la VARA met à la disposition de ses analystes conformité un agent qui répond en citant **une** section de ses procédures internes (KYC, surveillance des transactions, signalement des opérations suspectes). L'équipe change de découpage et passe de sections entières à des morceaux de 200 mots. Sur le jeu d'évaluation de 150 questions, le Recall@10 reste à 0,95, mais le MRR passe de 0,78 à 0,55 : la bonne section est toujours trouvée, seulement plus bas, parce que les petits morceaux de la partie « définitions » répètent les mots de la question et passent devant. L'agent citant le premier résultat, il renvoie l'analyste vers une définition au lieu de la procédure à suivre. Le MRR sert désormais de barrière dans la chaîne de déploiement : toute modification de l'index ou du découpage qui fait baisser le MRR de plus de 0,05 sur le jeu d'évaluation est bloquée. Une plateforme agréée doit appliquer ses propres procédures de lutte anti-blanchiment, et un analyste mal orienté peut laisser passer un délai interne de traitement. On suit le MRR à chaque version de l'index, à côté du Recall@10, pour distinguer « pas trouvé » de « trouvé trop bas ».

### Assurance — la clause de la bonne version du contrat

Un assureur auto et santé révise chaque année le texte de ses contrats, et un sinistre se règle selon la version signée par l'assuré, pas selon la plus récente. Pour chaque déclaration, l'agent cite la première clause renvoyée et en tire la franchise applicable ; seule la clause de la bonne version est jugée pertinente. Sur 300 sinistres annotés, le MRR n'atteint que 0,58 : l'ancienne et la nouvelle version d'une même clause se ressemblent presque mot pour mot, et la mauvaise passe souvent première. L'équipe ajoute un filtre sur la version du contrat, lue dans le dossier de l'assuré avant la recherche, et le MRR monte à 0,93, ce qui garantit au moins 86 % de premières clauses justes. Sans ce suivi, l'agent appliquerait la franchise d'une version que l'assuré n'a jamais signée, ce qui expose l'assureur à des contestations. L'assurance est supervisée par la CBUAE, et chaque décision de sinistre doit citer le texte réellement applicable. On suit le MRR@1 par ligne de produit et par millésime de contrat.

### RH — un rang moyen mal lu

Un cabinet RH présent dans plusieurs émirats utilise un routeur qui choisit la procédure de visa à suivre (nouvelle embauche, renouvellement, modification de contrat au MOHRE) d'après le premier résultat de la recherche, dans un top-3. Sur dix questions de test, quatre trouvent la bonne procédure au rang 1, deux au rang 2 et quatre au rang 10, ce qui donne

$$
\text{MRR} = (4 + 2 \times 0{,}5 + 4 \times 0{,}1)/10 = 0{,}54 .
$$

Le tableau de bord affichait « rang moyen ≈ 1,85 », calculé comme 1/MRR ; or le vrai rang moyen vaut (4 + 4 + 40)/10 = 4,8, et c'est le point 4 de la démonstration qui explique l'écart : 1/MRR est la moyenne harmonique, tirée vers le bas par les rangs 1. Plus grave, le HitRate@3 vaut 0,6 : quatre questions sur dix ont la bonne procédure hors du top-3, et le routeur lance alors le mauvais circuit. Le cabinet ajoute l'émirat et le type de visa à la requête, et remplace le « rang moyen » du tableau de bord par le HitRate@3 et le MRR@3. Une démarche lancée sur le mauvais circuit retarde un permis de travail, avec des conséquences pour le salarié comme pour l'employeur. On suit le HitRate@3 et le MRR@3 par émirat et par type de demande.

### BTP — la clause de retenue du bon contrat de sous-traitance

Un groupe de construction qui mène de grands chantiers à Dubaï fait contrôler les factures de ses sous-traitants par un agent : il vérifie le montant hors taxe, la TVA de 5 % et la retenue de garantie prévue au contrat de sous-traitance concerné. La retenue varie d'un contrat à l'autre, et seule la clause du contrat de ce sous-traitant est pertinente ; le modèle générique du groupe, avec un taux par défaut, ne l'est pas. L'agent lit la première clause renvoyée, et quand le modèle générique passe devant, il applique le mauvais taux de retenue. Sur 120 factures de test, le MRR@3 vaut 0,71 et le HitRate@3 0,83 ; la règle de décision est simple : si aucune clause spécifique n'apparaît dans les trois premiers résultats (rang réciproque nul), la facture part en revue humaine au lieu d'être validée. Sans le MRR, l'équipe aurait mesuré la qualité de la seule extraction des montants, sans voir que la règle appliquée venait du mauvais document. Une retenue mal calculée fausse le montant payé et la TVA correspondante, deux erreurs coûteuses à rectifier une fois la facture réglée. On suit le MRR@3 par type de lot (gros œuvre, électricité, plomberie) et la part de factures envoyées en revue humaine.

### Secteur public — la carte réponse affichée en tête

Une entité de services publics en ligne, accessible par UAE Pass, affiche le premier résultat de sa recherche sous forme de « carte réponse » en haut de page, et la plupart des usagers ne lisent que cette carte. Le MRR@1, égal ici au Success@1 (point 2), mesure donc directement la part d'usagers qui reçoivent la bonne procédure. Sur deux jeux de 1 000 questions, l'un en arabe et l'autre en anglais, il vaut 0,71 en arabe contre 0,84 en anglais. L'analyse montre deux causes : l'orthographe arabe non normalisée (formes de l'alef, ta marbuta) et les noms de démarches translittérés de plusieurs façons. L'équipe normalise l'arabe à l'indexation et à la requête et ajoute une table de synonymes bilingue, ce qui réduit l'écart sous le seuil d'alerte de 0,05. Un service public doit la même qualité de réponse dans les deux langues, et les questions conservées pour l'évaluation sont expurgées de tout numéro d'Emirates ID, par minimisation des données personnelles. On suit le MRR@1 par langue, avec une alerte dès que l'écart entre l'arabe et l'anglais dépasse 0,05.

## Pièges et limites

- **Encoder « rien trouvé » par 0 ou par -1** : on finit par diviser par zéro, ou par compter un bug comme une absence. On utilise `None`, et toute valeur inférieure à 1 lève `ValueError`.
- **Lire 1/MRR comme un rang moyen** : c'est la moyenne harmonique des rangs, toujours plus optimiste que la moyenne arithmétique (point 4 et cas RH).
- **Utiliser le MRR pour des questions à plusieurs sources** : il ne voit que le premier pertinent ; on l'associe au Recall@k (étape 25) ou au NDCG (étape 28).
- **Compter les rangs à partir de 0** (`enumerate` sans `start=1`) : tous les rangs sont décalés d'un cran et le premier document provoque une division par zéro.
- **Comparer des MRR calculés avec des coupures différentes** : un MRR@3 et un MRR@10 ne se comparent pas.

### Exercice feuille blanche

1. Sans regarder le code, écrire `first_relevant_rank` et `mrr`, avec `None` pour « rien trouvé », puis retrouver 0,4583 sur l'exemple.
2. Prédire, puis vérifier : pour les rangs `[2, 2, None, 1]`, que valent le MRR, le MRR@1 et le HitRate@2 ? (Réponse : (0,5 + 0,5 + 0 + 1)/4 = 0,5 ; 0,25 ; 0,75.)
3. Trouver le bug : `sum(1.0 / r for r in ranks if r) / len(ranks)`, appliqué à des rangs produits par `enumerate(liste)` sans `start=1`. Que vaut le MRR d'un moteur parfait ? (Réponse : son bon document a le rang 0, éliminé par `if r` ; le moteur parfait obtient 0, et un moteur qui place toujours le bon document deuxième obtient 1.)

## Pour aller plus loin

- **Expected Reciprocal Rank (ERR)** : il prolonge le MRR à la pertinence graduée en modélisant un lecteur qui s'arrête au premier document qui le satisfait, avec une probabilité qui dépend de la note du document. C'est un pont vers le NDCG de l'étape 28.
- **Un ou plusieurs pertinents** : ici, n'importe quel document pertinent arrête le compte. Certains jeux d'évaluation imposent au contraire un document cible unique (recherche d'un élément connu) ; on vérifie la convention avant de comparer deux chiffres.
- **Intervalle de confiance** : le MRR est une moyenne de valeurs entre 0 et 1, pas une proportion de succès. L'intervalle de Wilson (étape 7) s'applique au HitRate@k et au Success@1 ; pour le MRR lui-même, on rééchantillonne les questions (bootstrap).

> Suite : [NDCG](<28-RAG-Formule-NDCG.md>) — étape 28.
