# Étape 24 — RAG — Reciprocal Rank Fusion (RRF)

> Étape 24 du parcours · Prérequis : [Score hybride](<23-RAG-Formule-Score-Hybride.md>) · Suite : [Recall@k](<25-RAG-Formule-Recall-at-k.md>)

**Dossier :** 05-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  
**Nom du fichier :** 24-RAG-Formule-RRF.md

## Définition

La Reciprocal Rank Fusion (RRF), proposée par Cormack, Clarke et Büttcher à la conférence SIGIR en 2009, fusionne plusieurs classements d'un même ensemble de documents, par exemple celui d'une recherche vectorielle et celui de BM25. Chaque classement apporte à chaque document qu'il contient la quantité

$$
1/(k_{RRF} + \text{rang}) ,
$$

où le rang vaut 1 pour le premier ; on additionne ces apports, puis on trie. Un document absent d'un classement n'y reçoit rien. La méthode n'utilise **que les rangs**, jamais les scores : elle ne demande aucune normalisation et aucun poids à régler, contrairement au score hybride de l'étape 23. La constante

$$
k_{RRF}
$$

vaut 60 par défaut, la valeur retenue par les auteurs de la méthode ; elle règle l'écart entre les apports des premiers rangs et ceux des suivants.

## Rôle dans un agent

RRF se place dans le **retriever**, à l'étape de fusion, entre la recherche et la construction du prompt. L'agent perçoit une question, lance plusieurs recherches (vectorielle, BM25, recherche dans les titres, ou la même recherche sur plusieurs reformulations de la question), puis fusionne les listes obtenues par RRF avant de garder les meilleurs passages. C'est le choix par défaut quand on ne dispose pas encore de requêtes étiquetées pour régler un α, ou quand les signaux à fusionner n'ont aucune unité commune (un cosinus, un BM25, un écart de prix). RRF sert aussi hors du RAG : pour fusionner les propositions de plusieurs outils ou de plusieurs agents qui classent chacun les mêmes options, par exemple les alertes d'une file de revue.

## Équation complète

Score RRF d'un document d ; la somme ne porte que sur les classements qui contiennent d (un document absent contribue 0) :

$$
\text{RRF}(d) = \sum_{r \in R,\; d \in r} \frac{1}{k_{RRF} + \text{rang}_r(d)}
$$

Valeur par défaut de la constante :

$$
k_{RRF} = 60
$$

Borne démontrée au point 2 :

$$
0 \le \text{RRF}(d) \le \frac{|R|}{k_{RRF} + 1}
$$

## Décryptage des symboles

$$
R
$$

**Sens :** l'ensemble des classements à fusionner · **Type / plage :** liste de listes · **Variable Python :** `classements`

$$
\lvert R \rvert
$$

**Sens :** nombre de classements · **Type / plage :** entier ≥ 1 · **Variable Python :** `len(classements)`

$$
r
$$

**Sens :** un classement, du meilleur au moins bon · **Type / plage :** liste d'identifiants sans doublon · **Variable Python :** `classement`

$$
d
$$

**Sens :** un document · **Type / plage :** identifiant · **Variable Python :** `doc`

$$
\text{rang}_r(d)
$$

**Sens :** rang de d dans r, 1 pour le premier · **Type / plage :** entier ≥ 1 · **Variable Python :** `rang`, donné par `enumerate(..., start=1)`

$$
k_{RRF}
$$

**Sens :** constante de lissage · **Type / plage :** entier ≥ 0, 60 par défaut · **Variable Python :** `k_rrf`

$$
\text{RRF}(d)
$$

**Sens :** score fusionné, qui ne sert qu'à trier · **Type / plage :** réel ≥ 0 · **Variable Python :** valeur associée à `doc` dans la sortie de `rrf`

## Démonstration

### 1. Une notation sans collision, une convention pour les absents

L'ancienne version de ce fichier notait la constante k. C'est la lettre du k de « top-k » (Recall@k à l'étape suivante), et elle ressemble au k₁ de BM25 (étape 22) : dans un pipeline « BM25 top-k, puis RRF, puis Recall@k », une seule lettre aurait trois sens. On écrit donc

$$
k_{RRF} .
$$

La valeur 60 est celle de Cormack, Clarke et Büttcher, qui l'ont fixée lors d'une étude préliminaire puis gardée pour toutes leurs expériences ; c'est une valeur robuste, pas une loi. Les rangs commencent à 1, et un document absent d'un classement n'y contribue pas : la somme ne porte que sur les classements qui le contiennent.

### 2. Borne :

$$
\text{RRF}(d) \le \lvert R \rvert / (k_{RRF} + 1)
$$

Dans un classement, le rang d'un document vaut au moins 1, donc

$$
k_{RRF} + \text{rang} \ge k_{RRF} + 1 ,
$$

et, parce que la fonction inverse est décroissante sur les nombres positifs,

$$
1/(k_{RRF} + \text{rang}) \le 1/(k_{RRF} + 1) .
$$

Un document n'apparaît qu'une fois dans un classement (on dédoublonne sinon, voir les pièges), donc chaque classement lui apporte au plus

$$
1/(k_{RRF} + 1) ,
$$

et la somme sur | R | classements est au plus

$$
\lvert R \rvert / (k_{RRF} + 1) .
$$

L'égalité n'a lieu que pour un document premier partout. Avec deux classements et

$$
k_{RRF} = 60 ,
$$

la borne vaut 2/61 = 0,032787. Les scores RRF sont donc petits et très proches les uns des autres : ils servent à trier, pas à mesurer une confiance, et l'on ne pose jamais de seuil dessus.

### 3. Invariance : seuls les rangs comptent

Soit φ une fonction strictement croissante appliquée aux scores d'une recherche. Pour deux documents, sᵢ > sⱼ équivaut à φ(sᵢ) > φ(sⱼ) : l'ordre est le même, donc les rangs sont les mêmes, donc RRF ne change pas. Cela vaut pour les transformations affines, comme 100 × BM25 + 7, mais aussi pour des transformations qui déforment les écarts, comme cos³, e¹⁰ᶜᵒˢ ou ln(1 + BM25) : le programme vérifie que RRF reste identique au bit près. Le score hybride, lui, n'est invariant que par les transformations affines croissantes (étape 23, point 4). Deux précisions : la transformation doit être **strictement** croissante, car un arrondi qui crée des égalités peut déplacer des rangs ; et un changement qui modifie l'**ordre**, comme un nouveau modèle d'embedding, change évidemment le résultat.

### 4. Consensus : deux rangs moyens battent un premier rang isolé

Un document classé 2e dans une liste et 3e dans l'autre obtient 1/62 + 1/63 = 0,0320, presque le double d'un document classé 1er dans une seule liste, 1/61 = 0,0164. Plus généralement, avec deux classements : **tout document classé dans les**

$$
k_{RRF} + 1
$$

**premiers de chacun bat tout document présent dans un seul**. En effet, si

$$
r_1 \le k_{RRF} + 1
$$

et

$$
r_2 \le k_{RRF} + 1 ,
$$

chaque apport vaut au moins

$$
1/(2k_{RRF} + 1) ,
$$

donc :

$$
\frac{1}{k_{RRF} + r_1} + \frac{1}{k_{RRF} + r_2} \ge \frac{2}{2k_{RRF} + 1} > \frac{1}{k_{RRF} + 1}
$$

La dernière inégalité équivaut à

$$
2(k_{RRF} + 1) > 2k_{RRF} + 1 ,
$$

toujours vraie, et le membre de droite est, par le point 2, le maximum de ce qu'obtient un document présent dans une seule liste. Avec

$$
k_{RRF} = 60
$$

2/121 = 0,016529 > 1/61 = 0,016393. La limite est exacte : au rang

$$
k_{RRF} + 2 = 62
$$

dans les deux listes, 2/122 = 1/61, et il y a égalité. Comme les listes renvoyées par un retriever dépassent rarement soixante documents, un document trouvé par les deux recherches passe, en pratique, toujours devant un document trouvé par une seule. C'est ce que l'on veut quand les deux recherches sont bonnes et indépendantes ; c'est trompeur quand elles se recopient l'une l'autre.

### 5. Convexité : à somme de rangs égale, un très bon rang l'emporte de peu

La fonction f(r) = 1/(k + r) est convexe, parce que sa dérivée seconde 2/(k + r)³ est positive. Une fonction convexe vérifie

$$
f(a) + f(b) > 2 f\left(\frac{a + b}{2}\right)
$$

dès que a ≠ b : à somme de rangs égale, deux rangs inégaux rapportent plus que deux rangs égaux. Le calcul direct, avec P = (k + 1)(k + 2)(k + 3), le confirme :

$$
\frac{1}{k + 1} + \frac{1}{k + 3} - \frac{2}{k + 2} = \frac{(k + 2)(k + 3) + (k + 1)(k + 2) - 2(k + 1)(k + 3)}{P} = \frac{2}{P} > 0
$$

Le numérateur vaut en effet

$$
(k^2 + 5k + 6) + (k^2 + 3k + 2) - 2(k^2 + 4k + 3) = 2 .
$$

Avec k = 60, les rangs 1 et 3 donnent 0,032266, les rangs 2 et 2 donnent 0,032258, et l'écart vaut 2/(61 × 62 × 63) = 8,39 × 10⁻⁶. L'effet est minuscule à

$$
k_{RRF} = 60 ,
$$

mais il explique la comparaison de l'étape 23 : B, deuxième dans les deux listes, passait derrière A et C, premiers dans une liste et troisièmes dans l'autre.

### 6. Le rôle de la constante k_RRF

Le rapport entre l'apport du rang 1 et celui du rang 10 vaut

$$
(k_{RRF} + 10)/(k_{RRF} + 1)
$$

10 pour

$$
k_{RRF} = 0 ,
$$

où le premier rang écrase tout, et seulement 1,148 pour

$$
k_{RRF} = 60 ,
$$

où les apports sont presque plats. Un exemple montre le basculement. Le document X est premier dans une seule liste ; le document Y est cinquième dans une liste et sixième dans l'autre. Y passe devant X si et seulement si :

$$
\frac{1}{k + 5} + \frac{1}{k + 6} > \frac{1}{k + 1} \iff (2k + 11)(k + 1) > (k + 5)(k + 6) \iff k^2 + 2k - 19 > 0
$$

La première équivalence vient de ce que l'on réduit au même dénominateur, (2k + 11)/((k + 5)(k + 6)), puis que l'on multiplie des deux côtés par des nombres positifs ; la seconde, du développement 2k² + 13k + 11 > k² + 11k + 30. La racine positive vaut

$$
-1 + \sqrt{20} \approx 3{,}47
$$

X gagne pour

$$
k_{RRF} \le 3 ,
$$

Y gagne dès

$$
k_{RRF} = 4 .
$$

Un petit

$$
k_{RRF}
$$

récompense le fait d'être premier quelque part ; un grand

$$
k_{RRF}
$$

récompense l'accord entre les listes. Quand

$$
k_{RRF}
$$

devient très grand, 1/(k + r) ≈ 1/k − r/k² : RRF classe d'abord par nombre de listes qui contiennent le document, puis par plus petite somme des rangs.

### 7. Exemple fait à la main (le code reprend ces nombres)

La recherche sémantique renvoie A, B, C, D ; BM25 renvoie C, A, E, B. Avec

$$
k_{RRF} = 60
$$

| Document | Rang sémantique | Rang lexical | Calcul | RRF |
|---|---|---|---|---|
| A | 1 | 2 | 1/61 + 1/62 = 0,016393 + 0,016129 | 0,032522 |
| C | 3 | 1 | 1/63 + 1/61 = 0,015873 + 0,016393 | 0,032266 |
| B | 2 | 4 | 1/62 + 1/64 = 0,016129 + 0,015625 | 0,031754 |
| E | absent | 3 | 1/63 | 0,015873 |
| D | 4 | absent | 1/64 | 0,015625 |

Le classement fusionné est A, C, B, E, D. Les trois documents trouvés par les deux recherches passent devant les deux autres, comme le prévoit le point 4, et E devance D parce que le rang 3 rapporte plus que le rang 4. L'ancien code renvoyait un dictionnaire non trié, dans l'ordre où les documents avaient été rencontrés : A, B, C, D, E. Un appelant qui prenait ses trois premières clés obtenait A, B, C, alors que le vrai top-3 est A, C, B.

## Effets et comportement

- **RRF ignore l'échelle des scores** (point 3) : c'est ce que disait l'ancienne version, et c'est exact ; la raison précise est qu'il ne lit que les rangs.
- **RRF ignore aussi les écarts** : un document très largement en tête d'une liste reçoit le même apport qu'un document à peine devant le suivant. Quand ces écarts portent de l'information et que l'on dispose de requêtes étiquetées, le score hybride réglé par NDCG (étape 23) peut faire mieux ; cela se mesure.
- **Plus**

$$
k_{RRF}
$$

**est grand, moins les écarts de rang en tête comptent**, comme le disait l'ancienne version : de 10 à 1,148 entre

$$
k_{RRF} = 0
$$

et

$$
k_{RRF} = 60
$$

pour le rapport rang 1 / rang 10 (point 6).
- **Ajouter un classement favorise les documents qu'il partage avec les autres** (point 4) ; un classement de mauvaise qualité ajoute donc surtout du bruit au consensus.

## Du symbole au code Python

$$
\text{RRF}(d)
$$

**Variable ou fonction :** `rrf(classements, k_rrf)`, fonction canonique du parcours

$$
R,\quad r
$$

**Variable ou fonction :** `classements`, `classement`

$$
\text{rang}_r(d)
$$

**Variable ou fonction :** `rang`, de `enumerate(classement, start=1)`

$$
k_{RRF}
$$

**Variable ou fonction :** `k_rrf = 60`

**Symbole :** rangs à partir de scores · **Variable ou fonction :** `classement_depuis_scores(scores)`

**Symbole :** un seul rang par document · **Variable ou fonction :** `dedoublonner(classement)`

### Déroulé, ligne par ligne

**`rrf(classements, k_rrf)`** est la fonction canonique, recopiée telle quelle.

- `scores: dict[str, float] = {}` : un score par document rencontré ; un document jamais rencontré n'a pas de clé, ce qui revient à lui donner 0.
- `for rang, doc in enumerate(classement, start=1)` : `start=1` fait commencer les rangs à 1, comme dans la formule. Pour la liste lexicale `["C", "A", "E", "B"]`, on obtient les couples (1, C), (2, A), (3, E), (4, B).
- `scores[doc] = scores.get(doc, 0.0) + 1.0 / (k_rrf + rang)` : pour A, la liste sémantique ajoute `1 / 61 = 0.016393`, puis la liste lexicale `1 / 62 = 0.016129`, d'où 0,032522.
- `return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))` : score décroissant, puis nom en cas d'égalité. La sortie est une liste de couples, déjà triée, et elle est la même à chaque exécution.

**`ancienne_rrf(rankings, k)`** reproduit l'ancien code : même calcul, mais `return scores` renvoie le dictionnaire dans l'ordre d'insertion. `list(ancienne_rrf([sem, lex]))[:3]` vaut `['A', 'B', 'C']`.

**`classement_depuis_scores(scores)`** transforme les scores d'une recherche en classement, par score décroissant ; elle sert à vérifier l'invariance du point 3.

**`dedoublonner(classement)`** garde la première occurrence de chaque document : `["A", "A", "B"]` devient `["A", "B"]`.

**`main()`**, bloc par bloc.

1. L'exemple du point 7 : les cinq scores, l'ordre A, C, B, E, D, et l'erreur de l'ancien code.
2. La borne du point 2 : tous les scores sont sous `2 / 61`, et un document premier dans les deux listes l'atteint exactement.
3. L'invariance du point 3 : on retrouve d'abord les deux classements à partir de scores bruts (cosinus et BM25), puis on applique deux paires de transformations strictement croissantes ; `rrf` renvoie exactement la même liste.
4. Le consensus du point 4 : 0,0320 contre 0,0164 ; puis la double boucle vérifie l'inégalité pour tous les rangs de 1 à 61 dans les deux listes, et l'égalité exacte au rang 62.
5. La convexité du point 5 : 0,032266 contre 0,032258, et l'écart égal à `2 / (61 * 62 * 63)`.
6. Le rôle de

$$
k_{RRF}
$$

(point 6) : les rapports 10 et 1,148 ; `next(...)` cherche le plus petit `k` pour lequel Y passe devant X et trouve 4 ; la boucle finale vérifie le sens de la comparaison pour `k` = 0, 3, 4 et 60.
7. Un doublon : sans dédoublonnage, A reçoit `1/61 + 1/62` dans une seule liste ; après, A et B reçoivent `1/61` et `1/62`.
8. Le contre-exemple de l'étape 23 : A et C à égalité, départagés par le nom, devant B.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`rrf(classements, k_rrf)`** — On peut se figurer un jury de course qui ignore les chronomètres et ne regarde que les places obtenues dans plusieurs épreuves : la fonction reçoit une liste de classements, chacun ordonné du meilleur au moins bon, et la constante k, 60 par défaut, puis, pour chaque classement et chaque rang à partir de 1, ajoute au document la récompense 1 / (k + rang), un document absent d'une épreuve n'y gagnant rien. Elle renvoie la liste des couples (document, score) triée par score décroissant, les égalités départagées par le nom pour que la sortie soit toujours la même ; sur les listes A, B, C, D et C, A, E, B, elle donne A = 0,032522, C = 0,032266, B = 0,031754, E = 0,015873 et D = 0,015625.

**`ancienne_rrf(rankings, k)`** — Cette fonction est l'ancien jury, consciencieux dans ses calculs mais distrait au moment de proclamer les résultats : elle reçoit les mêmes classements et la même constante, 60 par défaut, et additionne exactement les mêmes récompenses 1 / (k + rang), mais elle renvoie le dictionnaire brut des scores, dont les clés restent dans l'ordre où les documents ont été rencontrés pour la première fois. Qui prend ses trois premières clés pour un podium lit donc A, B, C, alors que le vrai top 3 est A, C, B ; le programme la conserve uniquement pour exhiber cette erreur.

**`classement_depuis_scores(scores)`** — Elle joue le greffier qui transforme les temps bruts d'un retriever en simple ordre d'arrivée : la fonction reçoit un dictionnaire qui associe un score à chaque document, trie les documents par score décroissant en départageant les égalités par le nom, et renvoie la liste ordonnée des noms. Le programme s'en sert pour retrouver les deux classements de départ à partir des cosinus et des scores BM25, puis pour prouver l'invariance de RRF : après des transformations strictement croissantes comme le cube, l'exponentielle ou le logarithme, les rangs ne bougent pas et la fusion reste identique au bit près.

**`dedoublonner(classement)`** — C'est le contrôleur d'entrée qui ne laisse passer chaque coureur qu'une seule fois sur la ligne d'arrivée : la fonction reçoit une liste de documents qui peut contenir des répétitions, la parcourt dans l'ordre en notant dans un ensemble ceux qu'elle a déjà vus, et ne garde que la première occurrence de chacun. Elle renvoie la liste nettoyée, [A, B] pour [A, A, B] ; sans elle, RRF compterait A deux fois dans la même liste et lui donnerait 1/61 + 1/62 au lieu de 1/61, ce que `main` montre au point 7.

**`main()`** — Le chef d'orchestre déroule huit vérifications : l'exemple à la main et l'erreur de l'ancien code, la borne 2/61 atteinte exactement par un document premier dans les deux listes, puis l'invariance de la fusion sous quatre transformations croissantes des scores. Il prouve ensuite qu'un document classé aux rangs 2 et 3 bat un premier rang isolé, 0,0320 contre 0,0164, et que cela vaut pour tous les rangs jusqu'au 61e avec égalité au 62e, mesure l'effet de la convexité, 0,032266 contre 0,032258, cherche le plus petit k qui fait passer Y devant X et trouve 4, montre l'effet d'un doublon et départage l'égalité de A et C par le nom. Chaque nombre est gardé par un `assert`, et la ligne finale n'annonce le succès que si tous ont tenu.

```python
"""Étape 24 — Reciprocal Rank Fusion : rangs seulement, borne, invariance, consensus, convexité, rôle de k_RRF."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def rrf(classements: list[list[str]], k_rrf: int = 60) -> list[tuple[str, float]]:
    """Reciprocal Rank Fusion ; un document absent d'un classement y contribue 0. Sortie triée, égalités par nom."""
    scores: dict[str, float] = {}
    for classement in classements:
        for rang, doc in enumerate(classement, start=1):
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (k_rrf + rang)
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))


def ancienne_rrf(rankings: list[list[str]], k: int = 60) -> dict[str, float]:
    """L'ancienne version : un dictionnaire dans l'ordre d'insertion, pas un classement."""
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, 1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return scores


def classement_depuis_scores(scores: dict[str, float]) -> list[str]:
    """Les rangs d'un retriever : score décroissant, nom en cas d'égalité."""
    return [d for d, _ in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))]


def dedoublonner(classement: list[str]) -> list[str]:
    """Garde la première occurrence : un document n'a qu'un rang dans une liste."""
    vus: set[str] = set()
    sortie = []
    for d in classement:
        if d not in vus:
            vus.add(d)
            sortie.append(d)
    return sortie


def main() -> None:
    print("1. Exemple à la main (k_RRF = 60) : sémantique = A, B, C, D ; lexical = C, A, E, B")
    sem, lex = ["A", "B", "C", "D"], ["C", "A", "E", "B"]
    fusion = rrf([sem, lex])
    print("  " + "   ".join(f"{d} = {v:.6f}" for d, v in fusion))
    assert [d for d, _ in fusion] == ["A", "C", "B", "E", "D"]
    assert [round(v, 6) for _, v in fusion] == [0.032522, 0.032266, 0.031754, 0.015873, 0.015625]
    ancien_top3 = list(ancienne_rrf([sem, lex]))[:3]
    print(f"  ancien code, trois premières clés du dictionnaire : {ancien_top3}   vrai top-3 : {[d for d, _ in fusion[:3]]}")
    assert ancien_top3 == ["A", "B", "C"] and [d for d, _ in fusion[:3]] == ["A", "C", "B"]

    print("2. Borne : RRF(d) ≤ |R| / (k_RRF + 1)")
    borne = 2 / 61
    assert all(v <= borne for _, v in fusion)
    premier_partout = dict(rrf([["X", "A"], ["X", "B"]]))["X"]
    print(f"  deux listes : borne = 2/61 = {borne:.6f} ; un document premier dans les deux listes = {premier_partout:.6f}")
    assert premier_partout == borne

    print("3. Invariance : une transformation strictement croissante des scores ne change rien")
    cos = {"A": 0.82, "B": 0.80, "C": 0.78, "D": 0.75}
    bm25 = {"C": 8.0, "A": 6.0, "E": 5.0, "B": 2.0}
    assert classement_depuis_scores(cos) == sem and classement_depuis_scores(bm25) == lex
    transformees = [
        ({d: v ** 3 for d, v in cos.items()}, {d: math.log(1 + v) for d, v in bm25.items()}),
        ({d: math.exp(10 * v) for d, v in cos.items()}, {d: 100 * v + 7 for d, v in bm25.items()}),
    ]
    for c2, b2 in transformees:
        assert rrf([classement_depuis_scores(c2), classement_depuis_scores(b2)]) == fusion
    print("  cos³, exp(10·cos), log(1 + BM25), 100·BM25 + 7 : RRF identique, au bit près")

    print("4. Consensus : deux rangs moyens battent un premier rang isolé")
    deux_trois, premier_seul = 1 / 62 + 1 / 63, 1 / 61
    print(f"  rangs 2 et 3 : 1/62 + 1/63 = {deux_trois:.4f}   rang 1 dans une seule liste : 1/61 = {premier_seul:.4f}")
    assert round(deux_trois, 4) == 0.0320 and round(premier_seul, 4) == 0.0164
    assert all(1 / (60 + r1) + 1 / (60 + r2) > 1 / 61 for r1 in range(1, 62) for r2 in range(1, 62))
    assert 1 / (60 + 62) + 1 / (60 + 62) == 1 / 61          # au rang 62 dans les deux listes : égalité exacte
    print("  tout document des 61 premiers rangs de deux listes bat tout document présent dans une seule")

    print("5. Convexité de 1/(k + r) : à somme de rangs égale, un très bon rang l'emporte de peu")
    un_trois, deux_deux = 1 / 61 + 1 / 63, 2 / 62
    print(f"  rangs 1 et 3 : {un_trois:.6f}   rangs 2 et 2 : {deux_deux:.6f}   écart = {un_trois - deux_deux:.2e}")
    assert round(un_trois, 6) == 0.032266 and round(deux_deux, 6) == 0.032258
    assert abs((un_trois - deux_deux) - 2 / (61 * 62 * 63)) < 1e-15

    print("6. Rôle de k_RRF")
    for k in (0, 60):
        print(f"  k_RRF = {k:>2} : contribution du rang 1 / contribution du rang 10 = {(k + 10) / (k + 1):.3f}")
    assert (0 + 10) / (0 + 1) == 10.0 and round((60 + 10) / (60 + 1), 3) == 1.148
    seuil = next(k for k in range(0, 100) if 1 / (k + 5) + 1 / (k + 6) > 1 / (k + 1))
    print(f"  X premier dans une seule liste, Y cinquième et sixième dans deux : Y passe devant dès k_RRF = {seuil}")
    assert seuil == 4
    listes = [["X", "a", "b", "c", "Y"], ["p", "q", "r", "s", "t", "Y"]]
    for k, x_devant in ((0, True), (3, True), (4, False), (60, False)):
        s = dict(rrf(listes, k_rrf=k))
        assert (s["X"] > s["Y"]) == x_devant

    print("7. Un document en double dans une liste serait compté deux fois")
    brut = dict(rrf([["A", "A", "B"]]))
    propre = dict(rrf([dedoublonner(["A", "A", "B"])]))
    print(f"  sans dédoublonnage : A = {brut['A']:.6f}   après : A = {propre['A']:.6f}, B = {propre['B']:.6f}")
    assert brut["A"] == 1 / 61 + 1 / 62 and propre == {"A": 1 / 61, "B": 1 / 62}

    print("8. Égalités départagées par le nom : sortie identique à chaque exécution")
    egalite = rrf([["A", "B", "C"], ["C", "B", "A"]])
    print("  " + "   ".join(f"{d} = {v:.6f}" for d, v in egalite))
    assert [d for d, _ in egalite] == ["A", "C", "B"] and egalite[0][1] == egalite[1][1]

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Exemple à la main (k_RRF = 60) : sémantique = A, B, C, D ; lexical = C, A, E, B
  A = 0.032522   C = 0.032266   B = 0.031754   E = 0.015873   D = 0.015625
  ancien code, trois premières clés du dictionnaire : ['A', 'B', 'C']   vrai top-3 : ['A', 'C', 'B']
2. Borne : RRF(d) ≤ |R| / (k_RRF + 1)
  deux listes : borne = 2/61 = 0.032787 ; un document premier dans les deux listes = 0.032787
3. Invariance : une transformation strictement croissante des scores ne change rien
  cos³, exp(10·cos), log(1 + BM25), 100·BM25 + 7 : RRF identique, au bit près
4. Consensus : deux rangs moyens battent un premier rang isolé
  rangs 2 et 3 : 1/62 + 1/63 = 0.0320   rang 1 dans une seule liste : 1/61 = 0.0164
  tout document des 61 premiers rangs de deux listes bat tout document présent dans une seule
5. Convexité de 1/(k + r) : à somme de rangs égale, un très bon rang l'emporte de peu
  rangs 1 et 3 : 0.032266   rangs 2 et 2 : 0.032258   écart = 8.39e-06
6. Rôle de k_RRF
  k_RRF =  0 : contribution du rang 1 / contribution du rang 10 = 10.000
  k_RRF = 60 : contribution du rang 1 / contribution du rang 10 = 1.148
  X premier dans une seule liste, Y cinquième et sixième dans deux : Y passe devant dès k_RRF = 4
…
  sans dédoublonnage : A = 0.032522   après : A = 0.016393, B = 0.016129
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : RRF tient en cinq lignes, mais chacune de ses propriétés se démontre et se vérifie. La borne, l'invariance, le consensus, la convexité et le rôle de

$$
k_{RRF}
$$

disent exactement ce que la fusion récompense, et ce qu'elle ignore.

## Squelette algorithmique

RRF fusionne plusieurs classements en n'utilisant que les rangs. Il ne demande aucune normalisation, ce qui le rend robuste quand les scores des moteurs n'ont pas la même échelle.

```text
ALGORITHME RRF
ENTRÉES : classements r₁ … r_|R| (listes de documents, du meilleur au moins bon), k_RRF (souvent 60)
SORTIE  : le classement fusionné

  scores ← dictionnaire vide
  POUR CHAQUE classement r FAIRE
      r ← Dédoublonner(r)                              (un document n'a qu'un rang par liste)
      POUR rang DE 1 À longueur(r) FAIRE
          d ← r[rang]
          scores[d] ← scores[d] + 1 / (k_RRF + rang)    (un document absent d'une liste n'y gagne rien)
      FIN POUR
  FIN POUR
  trier par score décroissant (égalités par nom) ; RETOURNER le classement

ALGORITHME Dédoublonner(r)
  vus ← ensemble vide ; sortie ← liste vide
  POUR CHAQUE d de r FAIRE  SI d ∉ vus ALORS ajouter d à vus et à sortie  FIN POUR
  RETOURNER sortie
```

**Complexité.** Si L est la somme des longueurs des classements, la fusion coûte O(L) pour les scores et O(U log U) pour le tri final, où U est le nombre de documents distincts. La mémoire est O(U). Le score est borné : 0 ≤ RRF(d) ≤ |R| / (k_RRF + 1), atteint quand d est premier partout.

**Du squelette au code.** `RRF` correspond à `rrf`, `Dédoublonner` à `dedoublonner`, et `classement_depuis_scores` transforme les scores d'un moteur en classement avant la fusion. `ancienne_rrf` reproduit l'ancienne version, que le programme compare à la nouvelle sur les mêmes listes.

## Cas d'usage réels aux Émirats

Les rangs, les volumes et les valeurs de

$$
k_{RRF}
$$

ci-dessous sont illustratifs ; les calculs suivent exactement la formule.

### Banque — reformuler la question trois fois, fusionner une seule fois

L'assistant clients d'une banque de détail de Dubaï reformule chaque question en trois variantes : la question d'origine en français, sa traduction anglaise, et une version en mots-clés comme « remboursement anticipé prêt personnel frais ». Il lance la recherche pour chacune et fusionne les trois listes de dix passages par RRF, sans aucun poids à régler entre les variantes. La fiche sur le remboursement anticipé arrive 2e, 3e et 2e dans les trois listes et obtient 1/62 + 1/63 + 1/62 = 0,0481, très loin devant une page sur les frais de carte classée 1re dans une seule variante (0,0164) : c'est le consensus du point 4. L'agent cite cette fiche ; sans fusion, sa réponse dépendrait de la formulation, chanceuse ou non, d'une seule variante. Les informations sur le remboursement anticipé relèvent des règles de protection du consommateur de la CBUAE (à confirmer avec le texte en vigueur), d'où l'exigence de citer la bonne fiche. L'équipe suit le Recall@5 (étape 25) sur des questions étiquetées, et la part des questions où les trois variantes désignent des premiers passages différents, signe d'une question ambiguë sur laquelle l'agent doit demander une précision.

### Immobilier — fusionner des classements qui n'ont pas la même unité

Pour chaque demande d'acheteur, le moteur d'une agence de Dubaï et d'Abu Dhabi produit trois classements : par similarité sémantique des descriptions, par BM25 sur les noms de projets et les codes d'unité, et par proximité du prix au sqft avec le budget de l'acheteur. Ces trois « scores » n'ont aucune unité commune, un cosinus, un BM25 non borné et un écart en AED/sqft, et une somme pondérée obligerait à normaliser trois grandeurs différentes ; RRF n'a besoin que des trois ordres. Une unité classée 3e, 1re et 4e obtient 1/63 + 1/61 + 1/64 = 0,0479. L'agent montre les cinq premières unités en indiquant, pour chacune, son rang dans chaque liste, ce qui rend la recommandation explicable à l'acheteur. Il ajoute au prix les frais de transfert du DLD, 4 % de la valeur, soit 80 000 AED pour une unité de 2 000 000 AED, pour que la comparaison avec le budget soit honnête. On suit le taux de visites programmées après une recommandation et le NDCG@10 sur des demandes étiquetées.

### Crypto — un consensus d'outils, à condition qu'ils soient indépendants

L'agent de conformité d'une plateforme d'actifs virtuels agréée par la VARA reçoit chaque matin les classements d'alertes de trois outils : des règles internes, un score d'anomalie et un score d'exposition on-chain, dont les valeurs ne sont pas comparables (un comptage, une probabilité, un montant en AED). RRF les fusionne : une alerte classée 4e, 5e et 6e par les trois outils obtient 1/64 + 1/65 + 1/66 = 0,0462, devant une alerte classée 1re par un seul outil (0,0164), si bien que l'équipe conformité voit d'abord les alertes sur lesquelles plusieurs outils s'accordent. La limite est connue : si deux outils reposent sur les mêmes variables, leur accord est compté deux fois et RRF le surestime. L'équipe mesure donc la corrélation entre les classements des outils et, si besoin, leur donne des poids différents. L'agent ne gèle jamais un compte : il ordonne la file de revue, et la décision reste humaine. L'indicateur suivi est la précision des vingt premières alertes revues chaque jour (étape 50).

### Assurance — choisir

$$
k_{RRF}
$$

en le mesurant

Un assureur auto et santé trie les déclarations suspectes en fusionnant deux classements : celui d'un détecteur de descriptions quasi identiques (distance L2 entre embeddings normalisés, étape 20) et celui d'un modèle de facteurs de risque. Les enquêteurs exigent qu'un doublon exact, classé 1er par le détecteur, soit revu en premier, même si le second modèle l'ignore. Or, avec

$$
k_{RRF} = 60 ,
$$

le consensus l'emporte : une déclaration classée 5e et 6e par les deux outils passe devant le doublon isolé, et le point 6 montre que l'ordre ne s'inverse que pour

$$
k_{RRF} \le 3 .
$$

L'équipe mesure sur des dossiers étiquetés la part de fraudes confirmées dans les cinquante premiers dossiers pour plusieurs valeurs de

$$
k_{RRF} ,
$$

et garde celle qui la maximise, ou bien passe à une fusion pondérée ; la valeur 60 est un point de départ, pas une obligation. L'agent ne refuse jamais un sinistre : il ordonne la file des enquêteurs, sous la supervision de la CBUAE qui s'applique à l'assureur. Les indicateurs suivis sont le taux de fraudes confirmées dans les cinquante premiers dossiers et le délai avant qu'un doublon parvienne à un enquêteur.

### RH — une question en arabe, deux recherches, une seule liste

L'assistant d'un cabinet RH présent dans plusieurs émirats traduit chaque question posée en arabe vers l'anglais, interroge l'index arabe, normalisé comme à l'étape 22, avec la question d'origine, et l'index anglais avec sa traduction, puis fusionne les deux classements par RRF. Une section de politique trouvée aux rangs 2 et 3 par les deux recherches (0,0320) passe devant une section que seule la recherche arabe place au rang 1 (0,0164) : l'accord entre les deux langues indique que la section répond vraiment à la question. Les deux index n'ont ni la même taille ni la même échelle de scores, et RRF n'a besoin d'aucune normalisation entre eux ; un document absent d'une liste n'y reçoit simplement rien. L'agent répond en arabe et cite la section, par exemple celle sur l'indemnité de fin de service prévue par le décret-loi fédéral 33/2021. L'indicateur suivi est le Recall@5 mesuré séparément pour les questions en arabe et en anglais.

### Secteur public — une fusion reproductible et auditable

Un service public en ligne accessible par UAE Pass doit pouvoir expliquer, lors d'un audit, pourquoi telle page de procédure a été montrée à tel usager. L'ancienne fonction RRF renvoyait un dictionnaire non trié, et l'interface affichait ses trois premières clés, c'est-à-dire l'ordre de rencontre des documents : sur l'exemple du point 7, elle montrait A, B, C au lieu de A, C, B. La fonction canonique renvoie une liste triée, avec un départage par nom en cas d'égalité, si bien que les mêmes entrées donnent toujours la même sortie ; le journal conserve, pour chaque page montrée, son rang dans chaque liste et son score RRF, ce qui suffit à recalculer la décision. Les classements sont dédoublonnés avant la fusion. Pour respecter la PDPL, le journal ne garde que des identifiants de documents et des rangs, pas le texte libre saisi par l'usager. Les indicateurs suivis sont le nombre d'écarts constatés en audit, avec un objectif de zéro, et la part des usagers qui trouvent leur procédure sans appeler le centre de contact.

## Pièges et limites

- **Une même lettre pour trois paramètres** : on écrit

$$
k_{RRF} ,
$$

distinct du k du top-k et du k₁ de BM25.
- **Une sortie non triée** : l'ancien code renvoyait un dictionnaire ; on renvoie une liste triée, avec un départage déterministe.
- **Un document en double dans une liste** est compté deux fois par la boucle ; on dédoublonne chaque classement avant la fusion.
- **Un score RRF n'est pas une confiance** : il est petit, borné par

$$
\lvert R \rvert/(k_{RRF} + 1) ,
$$

et ne se compare pas d'une requête à l'autre ; aucun seuil dessus.
- **Des listes tronquées et des recherches corrélées** : un document classé juste après la coupe d'une liste y est « absent », et deux recherches qui se ressemblent fabriquent un faux consensus. La longueur des listes et l'indépendance des recherches se choisissent et se vérifient.

### Exercice feuille blanche

1. Sans regarder le code, écrire `rrf` à partir de l'équation complète (un dictionnaire, `enumerate(..., start=1)`, un tri avec départage par nom), puis vérifier l'exemple du point 7.
2. Prédire, puis vérifier : dans l'exemple du point 6, qui de X ou de Y est devant pour

$$
k_{RRF} = 3 ,
$$

puis pour

$$
k_{RRF} = 4
$$

? (Réponse : X, puis Y.) Et dans l'exemple du point 7 avec

$$
k_{RRF} = 0 ,
$$

l'ordre change-t-il ? (Réponse : non ; A = 1,5, C = 1,333, B = 0,75, E = 0,333, D = 0,25.)
3. Trouver le bug : `for rang, doc in enumerate(classement):`, sans `start=1`. Que se passe-t-il avec `k_rrf=0`, et que deviennent les apports avec `k_rrf=60` ?

## Pour aller plus loin

La RRF pondérée multiplie l'apport de chaque classement par un poids,

$$
\sum_r w_r / (k_{RRF} + \text{rang}_r(d)) ,
$$

pour faire davantage confiance à une recherche qu'à une autre. Avant RRF, Fox et Shaw avaient proposé en 1994 des fusions par les scores, CombSUM et CombMNZ, qui exigent une normalisation, comme le score hybride de l'étape 23. La technique de « RAG-Fusion » combine la reformulation d'une question en plusieurs requêtes et leur fusion par RRF, comme dans le cas bancaire ci-dessus.

> Suite : [Recall@k](<25-RAG-Formule-Recall-at-k.md>) — étape 25.
