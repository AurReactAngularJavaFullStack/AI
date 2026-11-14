# Étape 26 — RAG — Precision@k

> Étape 26 du parcours · Prérequis : [Recall@k](<25-RAG-Formule-Recall-at-k.md>) · Suite : [MRR](<27-RAG-Formule-MRR.md>)

**Dossier :** 05-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  
**Nom du fichier :** 26-RAG-Formule-Precision-at-k.md

## Définition

La Precision@k, notée P@k, mesure la part de documents pertinents parmi les k premiers résultats renvoyés par le moteur de recherche. C'est une métrique de **pureté** : parmi ce que le retriever a mis dans le contexte du modèle, combien de morceaux servent vraiment à répondre ? Elle suppose un jugement de pertinence fait à l'avance : pour chaque question du jeu d'évaluation, un humain (ou une règle vérifiable) a désigné l'ensemble des documents utiles. Elle ne tient pas compte de l'ordre à l'intérieur du top-k : un document pertinent placé premier ou cinquième compte pareil, et c'est ce que corrigeront le MRR (étape 27) et le NDCG (étape 28). Le dénominateur est toujours k, même quand le moteur renvoie moins de k résultats, et la liste est dédoublonnée avant d'être tronquée.

## Rôle dans un agent

Dans la boucle percevoir → décider → agir → observer, la recherche documentaire est une action : l'agent appelle son outil de recherche, qui renvoie k morceaux de texte, et ces morceaux entrent dans le prompt du tour suivant. La Precision@k dit quelle fraction de cette place est réellement utile. Chaque morceau inutile coûte des tokens, dilue les passages utiles et peut contredire la bonne règle. On la mesure hors ligne, sur un jeu de questions annotées, pour régler trois composants : le **retriever** (BM25, cosinus et fusion, étapes 22 à 24), le **reranker** qui retrie les candidats, et la valeur de k elle-même. En production, un échantillon de requêtes réelles est annoté régulièrement pour vérifier que la précision ne se dégrade pas quand le corpus grandit. Elle se lit toujours avec le Recall@k de l'étape 25 : le rappel dit si rien d'important ne manque, la précision dit si le contexte n'est pas noyé.

## Équation complète

Définition ensembliste :

$$
\text{P@}k = \frac{|\text{Rel} \cap \text{Top}_k|}{k}
$$

La même chose rang par rang, avec dᵢ le document de rang i dans la liste dédoublonnée (un rang vide, quand le moteur a renvoyé moins de k résultats, compte 0) :

$$
\text{P@}k = \frac{1}{k} \sum_{i=1}^{k} \mathbf{1}[d_i \in \text{Rel}]
$$

Identité avec le rappel de l'étape 25, où hₖ est le nombre de documents pertinents présents dans le top-k :

$$
k \cdot \text{P@}k = h_k = |\text{Rel} \cap \text{Top}_k| = |\text{Rel}| \cdot \text{R@}k
$$

Plafond :

$$
0 \le \text{P@}k \le \min\!\left(1, \frac{|\text{Rel}|}{k}\right)
$$

Variation quand on ajoute le document de rang k+1, avec xₖ₊₁ = 1 s'il est pertinent et 0 sinon :

$$
\text{P@}(k+1) - \text{P@}k = \frac{x_{k+1} - \text{P@}k}{k+1}
$$

Moyenne sur un jeu de questions Q :

$$
\overline{\text{P@}k} = \frac{1}{|Q|} \sum_{q \in Q} \text{P@}k(q)
$$

## Décryptage des symboles

$$
k
$$

**Sens :** nombre de résultats regardés (taille du top-k) · **Type / plage :** entier ≥ 1 · **Variable Python :** `k`

$$
\text{Rel}
$$

**Sens :** ensemble des documents jugés pertinents pour la question (vérité terrain) · **Type / plage :** ensemble fini, éventuellement vide · **Variable Python :** `pertinents`

$$
\text{Top}_k
$$

**Sens :** les k premiers identifiants **distincts** renvoyés par le moteur · **Type / plage :** ensemble d'au plus k éléments · **Variable Python :** `dedupliquer(retrouves)[:k]`

$$
d_i
$$

**Sens :** document de rang i (rang 1 = le meilleur) · **Type / plage :** identifiant · **Variable Python :** `retrouves[i - 1]`

$$
\mathbf{1}[\cdot]
$$

**Sens :** indicatrice : 1 si la condition est vraie, 0 sinon · **Type / plage :** 0 ou 1 · **Variable Python :** `1 if d in pertinents else 0`

$$
h_k
$$

**Sens :** nombre de documents pertinents dans le top-k (les « touchés ») · **Type / plage :** entier entre 0 et min(k, | Rel |) · **Variable Python :** `touches_at_k(...)`

$$
\text{P@}k
$$

**Sens :** précision au rang k · **Type / plage :** réel dans [0, 1] · **Variable Python :** `precision_at_k(...)`

$$
\text{R@}k
$$

**Sens :** rappel au rang k (étape 25) · **Type / plage :** réel dans [0, 1], indéfini si Rel est vide · **Variable Python :** `recall_at_k(...)`

$$
x_{k+1}
$$

**Sens :** pertinence du document de rang k+1 · **Type / plage :** 0 ou 1 · **Variable Python :** `x`

$$
Q
$$

**Sens :** jeu de questions d'évaluation · **Type / plage :** ensemble fini · **Variable Python :** —

## Démonstration

### 1. Le numérateur compte des touchés, un par document distinct

L'intersection Rel ∩ Topₖ contient les documents qui sont à la fois dans le top-k et jugés pertinents. Son cardinal est donc la somme des indicatrices 𝟏[dᵢ ∈ Rel] sur les rangs 1 à k, **parce que** chaque document du top-k y est compté une fois et une seule. Cette égalité suppose que les dᵢ sont distincts : si le même identifiant apparaît deux fois dans la liste, la somme le compte deux fois alors que l'ensemble ne le compte qu'une fois. C'est pourquoi on dédoublonne la liste avant tout calcul (point 6).

### 2. Identité avec le rappel : k · P@k = |Rel| · R@k

On multiplie chaque définition par son dénominateur : k · P@k = hₖ ici et |Rel| · R@k = hₖ à l'étape 25. Les deux produits valent le même entier hₖ, **parce que** précision et rappel ont le même numérateur et ne diffèrent que par ce qui divise : la place disponible (k) pour la précision, ce qu'il fallait trouver (|Rel|) pour le rappel. On en tire P@k = R@k · |Rel| / k : connaître l'une des deux métriques et les deux tailles donne l'autre. En particulier, au rang k = |Rel|, précision et rappel sont égaux. Sur l'exemple du point 7,

$$
5 \times 0{,}4 = 2 = 3 \times \tfrac{2}{3} .
$$

### 3. Le plafond min(1, |Rel|/k)

Le nombre de touchés hₖ est le cardinal d'une intersection, donc il ne dépasse le cardinal d'aucun des deux ensembles : hₖ ≤ |Topₖ| ≤ k **parce que** l'intersection est incluse dans le top-k, et hₖ ≤ |Rel| **parce qu'**elle est incluse dans Rel. Donc hₖ ≤ min(k, |Rel|) et, en divisant par k > 0, P@k ≤ min(1, |Rel|/k). La borne est atteinte par un classement parfait, qui place tous les pertinents en tête. Conséquence pratique : une question qui n'a que deux documents pertinents ne peut pas dépasser P@5 = 2/5 = 0,4, même avec un moteur parfait. Comparer la P@5 brute d'une question à deux pertinents avec celle d'une question à dix pertinents, c'est comparer deux échelles différentes.

### 4. P@k n'est pas monotone en k

On passe de k à k+1 en ajoutant un seul document, de pertinence xₖ₊₁ ∈ {0, 1}. Le nombre de touchés devient hₖ + xₖ₊₁, donc :

$$
\text{P@}(k+1) = \frac{k \cdot \text{P@}k + x_{k+1}}{k+1} = \frac{k}{k+1}\,\text{P@}k + \frac{1}{k+1}\,x_{k+1}
$$

La nouvelle précision est une moyenne pondérée de l'ancienne et de xₖ₊₁. On en déduit la variation P@(k+1) − P@k = (xₖ₊₁ − P@k)/(k+1) : elle est positive quand le document ajouté est pertinent (sauf si la précision valait déjà 1) et négative quand il ne l'est pas (sauf si elle valait déjà 0). La précision monte et descend donc au gré des documents rencontrés, **parce que** son dénominateur grandit à chaque rang alors que son numérateur ne grandit qu'aux rangs pertinents. Contre-exemple chiffré : pour le classement pertinent, non pertinent, pertinent, non pertinent, non pertinent, on obtient 1 ; 0,5 ; 0,667 ; 0,5 ; 0,4. La suite baisse, remonte, puis baisse. L'ancienne phrase « un k trop grand fait souvent baisser la précision » décrivait une tendance, pas une règle : c'est le **rappel** qui est monotone (il ne baisse jamais quand k augmente, étape 25), pas la précision.

### 5. Moins de k résultats : on divise quand même par k

Un moteur muni d'un seuil de similarité peut renvoyer moins de k résultats. Exemple : k = 5, et le moteur renvoie trois morceaux dont deux pertinents. Avec la convention retenue, P@5 = 2/5 = 0,4 : les deux places vides comptent comme non pertinentes. On garde k au dénominateur pour trois raisons. D'abord, diviser par le nombre de résultats renvoyés récompenserait un moteur timide : renvoyer un seul document pertinent puis s'arrêter donnerait 1,0. Ensuite, deux systèmes ne seraient plus comparables, chacun ayant son propre dénominateur. Enfin, l'identité du point 2 ne tiendrait plus. C'est la convention usuelle des campagnes d'évaluation en recherche d'information ; certaines bibliothèques divisent pourtant par le nombre de résultats renvoyés, et il faut le vérifier avant de comparer deux chiffres.

### 6. Les doublons : dédoublonner avant de tronquer

Un même identifiant peut apparaître deux fois dans la liste renvoyée : document indexé deux fois, deux morceaux ramenés au même document, ou deux listes concaténées sans fusion. L'ancien code faisait `set(retrouves[:k])` : il tronquait d'abord, retirait ensuite les doublons, et gardait pourtant k au dénominateur. Avec la liste `["plafond-50", "plafond-50", "frais-carte", "retraite-30", "taux-variable"]`, deux pertinents (`plafond-50` et `retraite-30`) et k = 3, il ne voit que deux documents distincts et renvoie 1/3 ≈ 0,333 : le doublon a volé la place de `retraite-30`, troisième document distinct. La version corrigée garde la première occurrence de chaque identifiant (son meilleur rang), **puis** tronque : le top-3 devient `plafond-50`, `frais-carte`, `retraite-30`, et P@3 = 2/3 ≈ 0,667. L'erreur inverse, compter chaque doublon comme un touché, est pire : la liste [d, d, d] face à Rel = {d} donnerait 3/3 = 1, au-dessus du plafond min(1, 1/3) du point 3, ce qui prouve que ce calcul est faux. Le pipeline lui-même doit dédoublonner de la même façon avant de construire le prompt : sinon le doublon y gaspille réellement une place, et la métrique corrigée décrirait un contexte meilleur que celui que le modèle a lu.

### 7. Exemple fait à la main (le code reprend ces nombres)

Question posée à l'assistant crédit d'une banque : « Quel plafond d'endettement s'applique à un prêt personnel ? ». Trois morceaux sont jugés pertinents : `plafond-50` (le ratio d'endettement total de 50 % du revenu), `retraite-30` (30 % pour un retraité) et `toutes-mensualites` (toutes les mensualités comptent, y compris la nouvelle). Le moteur renvoie, dans l'ordre :

| Rang i | Document | Pertinent ? | hᵢ | P@i = hᵢ / i | R@i = hᵢ / 3 | Plafond min(1, 3/i) |
|---|---|---|---|---|---|---|
| 1 | `plafond-50` | oui | 1 | 1 | 0,333 | 1 |
| 2 | `frais-carte` | non | 1 | 0,5 | 0,333 | 1 |
| 3 | `toutes-mensualites` | oui | 2 | 0,667 | 0,667 | 1 |
| 4 | `taux-variable` | non | 2 | 0,5 | 0,667 | 0,75 |
| 5 | `murabaha-profit` | non | 2 | 0,4 | 0,667 | 0,6 |

On y lit trois choses. La précision baisse, remonte, puis baisse (point 4). Au rang 3, k = |Rel| et précision et rappel valent tous deux 0,667 (point 2). Au rang 5, 5 × 0,4 = 3 × 0,667 = 2 touchés. La variation entre les rangs 2 et 3 vaut (1 − 0,5)/3 ≈ 0,1667, comme le prédit la formule du point 4. Enfin, `retraite-30` n'est pas dans le top-5 : c'est le rappel qui le signale (0,667 < 1), pas la précision.

## Effets et comportement

- **Un document pertinent ajouté fait monter la précision, un non pertinent la fait baisser**, de (xₖ₊₁ − P@k)/(k+1) exactement. L'effet d'un document s'amortit quand k grandit : le 21e document change la précision d'au plus 1/21 ≈ 0,048.
- **Augmenter k** : le rappel ne peut que monter ou stagner ; la précision baisse souvent, mais pas toujours (point 4). Le bon k se choisit en regardant les deux courbes, pas la précision seule.
- **L'ordre à l'intérieur du top-k ne compte pas** : `[pertinent, non, non]` et `[non, non, pertinent]` ont la même P@3 = 1/3. Pour récompenser un bon document placé en tête, il faut le MRR (étape 27) ou le NDCG (étape 28).
- **Le plafond dépend de la question** : quand |Rel| < k, même un moteur parfait n'atteint pas 1. On compare deux moteurs sur le même jeu de questions, jamais deux questions entre elles.
- **Une question sans document pertinent** donne P@k = 0 quel que soit le moteur (le dénominateur k existe, la valeur est définie), alors que le rappel est indéfini (`None`). Ces questions ne disent rien du classement ; on les évalue à part, par un test d'abstention où l'agent doit dire qu'il ne trouve pas.

## Du symbole au code Python

$$
\text{Rel}
$$

**Variable ou fonction :** `pertinents` (un `set[str]`)

**Symbole :** liste renvoyée par le moteur · **Variable ou fonction :** `retrouves` (une `list[str]`, dans l'ordre des rangs)

$$
\text{Top}_k
$$

**Variable ou fonction :** `dedupliquer(retrouves)[:k]`

$$
h_k = \lvert \text{Rel} \cap \text{Top}_k \rvert
$$

**Variable ou fonction :** `touches_at_k(retrouves, pertinents, k)`

$$
\text{P@}k = h_k / k
$$

**Variable ou fonction :** `precision_at_k(retrouves, pertinents, k)`

$$
\text{R@}k = h_k / \lvert \text{Rel} \rvert
$$

**Variable ou fonction :** `recall_at_k(retrouves, pertinents, k)`

$$
x_{k+1}
$$

**Variable ou fonction :** `x = 1 if retrouves[k] in pertinents else 0`

### Déroulé, ligne par ligne

**`dedupliquer(retrouves)`** renvoie `list(dict.fromkeys(retrouves))`. Un dictionnaire Python garde l'ordre d'insertion et n'a qu'une entrée par clé : `dict.fromkeys` garde donc la première occurrence de chaque identifiant, c'est-à-dire son meilleur rang. Avec `["plafond-50", "plafond-50", "frais-carte", "retraite-30", "taux-variable"]`, il renvoie `["plafond-50", "frais-carte", "retraite-30", "taux-variable"]`. Un `set` ne conviendrait pas : il retire les doublons mais perd l'ordre, donc les rangs.

**`touches_at_k(retrouves, pertinents, k)`** calcule hₖ.

- `if k < 1: raise ValueError(...)` : un top-0 n'a pas de sens et provoquerait une division par zéro. L'ancienne version renvoyait `0.0` en silence pour `k == 0`, ce qui faisait passer une erreur de configuration pour un mauvais moteur.
- `sum(1 for d in dedupliquer(retrouves)[:k] if d in pertinents)` : dédoublonner, **puis** tronquer à `k`, puis compter les identifiants présents dans `pertinents`. Le test `d in pertinents` est rapide parce que `pertinents` est un `set`. Sur le classement de l'exemple, on obtient 1, 1, 2, 2 et 2 pour `k` allant de 1 à 5.

**`precision_at_k(retrouves, pertinents, k)`** renvoie `touches_at_k(...) / k`. On divise par `k`, pas par la longueur du top-k : pour la liste courte `["plafond-50", "frais-carte", "retraite-30"]` et `k = 5`, on obtient `2 / 5 = 0.4`.

**`recall_at_k(retrouves, pertinents, k)`** reprend la définition de l'étape 25 avec le même compteur `touches_at_k` : c'est ce partage qui rend l'identité du point 2 vraie par construction. Si `pertinents` est vide, il n'y a pas de dénominateur et la fonction renvoie `None`.

**`ancienne_precision(retrouves, pertinents, k)`** est l'ancien code du fichier, gardé uniquement pour le contre-exemple : `set(retrouves[:k])` tronque avant de dédoublonner.

**`main()`**, bloc par bloc.

1. La boucle parcourt `k` de 1 à 5 sur le classement de la démonstration. Pour chaque `k`, elle calcule `h`, `p`, `r` et le plafond `min(1.0, 3 / k)`, puis vérifie les valeurs du tableau, l'identité `k * p == h == 3 * r` (à `1e-12` près, parce que 2/3 n'a pas d'écriture binaire exacte) et la borne `p <= plafond`. Après la boucle, une dernière vérification reprend 5 × 0,4 = 3 × 2/3 = 2.
2. Avec les deux pertinents placés en tête, `P@5` vaut `0.4`, exactement `min(1, 2/5)`, alors que `R@5` vaut `1.0` : un classement parfait plafonne (point 3).
3. Deux `any(...)` vérifient que la suite des précisions monte au moins une fois et descend au moins une fois. La boucle suivante vérifie, pour chaque passage de `k` à `k + 1`, la formule de variation, où `x` vaut 1 si `retrouves[k]` est pertinent : c'est le document de rang `k + 1`, parce que les indices Python commencent à 0. Entre les rangs 2 et 3, la variation vaut `0.1667`.
4. La liste courte de trois résultats donne `P@5 = 0.4` et non `0.6667`, et l'identité du point 2 tient toujours.
5. Sur la liste avec doublon, `dedupliquer` donne la liste attendue, l'ancienne version renvoie `0.3333` et la version corrigée `0.6667`. Le comptage naïf de [d, d, d] donne `1.0`, au-dessus du plafond 1/3, donc il est faux ; la version corrigée renvoie bien 1/3.
6. `k = 0` lève `ValueError`. Une question sans pertinent donne `P@5 = 0.0` et `R@5 = None`.
7. F1@5 vaut `0.5`, soit 2h/(k + |Rel|) = 4/8, et la R-précision (P@3, puisqu'il y a trois pertinents) est égale à R@3.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`touches_at_k(retrouves, pertinents, k)`** — On peut l'imaginer comme un contrôleur qualité qui inspecte les k premiers colis d'un tapis roulant et compte ceux qui correspondent à la commande, après avoir retiré les colis envoyés en double : la fonction reçoit la liste ordonnée des résultats, l'ensemble des pertinents et k, lève `ValueError` si k est inférieur à 1, puis passe la liste par `dedupliquer`, la tronque à ses k premiers éléments et compte ceux qui appartiennent à l'ensemble des pertinents. Elle renvoie ce nombre entier hₖ, qui vaut 1, 1, 2, 2 et 2 pour k allant de 1 à 5 sur le classement de la démonstration ; c'est le compteur commun à la précision et au rappel, ce qui rend leur identité vraie par construction.

**`precision_at_k(retrouves, pertinents, k)`** — Cette fonction répond à la question du client qui ouvre les k premiers colis : quelle part de ce qu'on m'a livré était vraiment utile ? Elle reçoit les mêmes trois arguments, demande hₖ à `touches_at_k`, qui se charge aussi de refuser un k nul ou négatif, et renvoie hₖ / k, en divisant toujours par k même si le moteur a rendu moins de k résultats. Sur le classement de la démonstration, elle donne successivement 1, 0,5, 0,6667, 0,5 et 0,4 ; sur la liste courte de trois résultats dont deux pertinents, elle donne 0,4 à k = 5 et non 0,6667, car les places vides comptent comme des places perdues.

**`recall_at_k(retrouves, pertinents, k)`** — C'est la même inspection vue depuis l'entrepôt : sur tous les colis qui auraient dû partir, combien figurent dans les k premiers ? La fonction reçoit les trois mêmes arguments, renvoie `None` si l'ensemble des pertinents est vide, puisqu'il n'y aurait alors pas de dénominateur, et sinon divise hₖ, obtenu par `touches_at_k`, par le nombre de pertinents. Elle donne 0,3333 aux deux premiers rangs puis 0,6667 à partir du troisième sur le classement de la démonstration, et le programme vérifie avec elle l'identité k × P@k = hₖ = |Rel| × R@k, soit 5 × 0,4 = 3 × 2/3 = 2.

**`ancienne_precision(retrouves, pertinents, k)`** — Cette fonction est l'ancien contrôleur, gardé uniquement pour montrer son erreur de méthode : elle reçoit les mêmes arguments, renvoie 0,0 en silence quand k vaut 0 au lieu de signaler la faute de configuration, puis tronque la liste à k éléments avant de la transformer en ensemble, et divise par k le nombre de pertinents trouvés. Parce qu'elle coupe avant de dédoublonner, un doublon lui vole une place : sur la liste où le même document apparaît deux fois en tête, elle donne 0,3333 à k = 3, alors que la version corrigée donne 0,6667.

**`main()`** — Le chef d'orchestre déroule sept vérifications : le tableau de la démonstration, de k = 1 à 5, avec pour chaque ligne hₖ, la précision, le rappel et le plafond min(1, 3/k), puis le plafond atteint par un classement parfait, 0,4 en précision pour 1 en rappel. Il prouve ensuite que la précision n'est pas monotone et que sa variation suit exactement la formule (x − P@k) / (k + 1), avec 0,1667 entre les rangs 2 et 3, montre qu'on divise par k même quand la liste est plus courte, oppose l'ancienne et la nouvelle façon de traiter les doublons, vérifie les cas de bord, k = 0 qui lève `ValueError` et l'ensemble vide, et termine par F1@5 = 0,5 et la R-précision. Chaque nombre est gardé par un `assert`, et la dernière ligne n'annonce le succès que si tous ont tenu.

```python
"""Étape 26 — Precision@k : identité avec le rappel, plafond, non-monotonie, moins de k résultats, doublons."""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def dedupliquer(retrouves: list[str]) -> list[str]:
    """Garde la première occurrence de chaque identifiant (son meilleur rang), dans l'ordre."""
    return list(dict.fromkeys(retrouves))


def touches_at_k(retrouves: list[str], pertinents: set[str], k: int) -> int:
    """h_k = |Rel ∩ Top_k|, compté sur la liste dédoublonnée PUIS tronquée à k."""
    if k < 1:
        raise ValueError("k doit être un entier >= 1")
    return sum(1 for d in dedupliquer(retrouves)[:k] if d in pertinents)


def precision_at_k(retrouves: list[str], pertinents: set[str], k: int) -> float:
    """P@k = h_k / k. On divise par k même si le moteur a renvoyé moins de k résultats."""
    return touches_at_k(retrouves, pertinents, k) / k


def recall_at_k(retrouves: list[str], pertinents: set[str], k: int) -> float | None:
    """R@k = h_k / |Rel| (étape 25) ; None quand aucun document n'est pertinent."""
    if not pertinents:
        return None
    return touches_at_k(retrouves, pertinents, k) / len(pertinents)


def ancienne_precision(retrouves: list[str], pertinents: set[str], k: int) -> float:
    """Ancienne version du fichier, gardée pour le contre-exemple : elle tronque AVANT de dédoublonner."""
    if k == 0:
        return 0.0
    top_k = set(retrouves[:k])
    return len(top_k & pertinents) / k


def main() -> None:
    pertinents = {"plafond-50", "retraite-30", "toutes-mensualites"}
    retrouves = ["plafond-50", "frais-carte", "toutes-mensualites", "taux-variable", "murabaha-profit"]

    print("1. Le classement de la démonstration (|Rel| = 3)")
    attendu_p = [1.0, 0.5, 0.6667, 0.5, 0.4]
    attendu_r = [0.3333, 0.3333, 0.6667, 0.6667, 0.6667]
    precisions = []
    for k in range(1, 6):
        h = touches_at_k(retrouves, pertinents, k)
        p = precision_at_k(retrouves, pertinents, k)
        r = recall_at_k(retrouves, pertinents, k)
        plafond = min(1.0, len(pertinents) / k)
        precisions.append(p)
        print(f"  k = {k}  {retrouves[k - 1]:<19} h = {h}  P@k = {p:.4f}  R@k = {r:.4f}  plafond = {plafond:.4f}")
        assert round(p, 4) == attendu_p[k - 1] and round(r, 4) == attendu_r[k - 1]
        assert abs(k * p - h) < 1e-12 and abs(len(pertinents) * r - h) < 1e-12   # k·P@k = h = |Rel|·R@k
        assert p <= plafond                                                         # P@k <= min(1, |Rel|/k)
    assert abs(5 * precisions[4] - 3 * recall_at_k(retrouves, pertinents, 5)) < 1e-12   # 5 × 0,4 = 3 × 2/3 = 2

    print("2. Plafond : |Rel| = 2 et k = 5, un classement parfait ne dépasse pas 0.4")
    parfait = ["plafond-50", "retraite-30", "frais-carte", "taux-variable", "murabaha-profit"]
    rel_2 = {"plafond-50", "retraite-30"}
    p, r = precision_at_k(parfait, rel_2, 5), recall_at_k(parfait, rel_2, 5)
    print(f"  P@5 = {p:.4f} = min(1, 2/5) alors que R@5 = {r:.4f}")
    assert p == 0.4 == min(1.0, 2 / 5) and r == 1.0

    print("3. P@k n'est pas monotone en k ; variation exacte (x - P@k) / (k + 1)")
    assert any(b > a for a, b in zip(precisions, precisions[1:]))   # elle monte quelque part…
    assert any(b < a for a, b in zip(precisions, precisions[1:]))   # … et elle descend ailleurs
    for k in range(1, 5):
        x = 1 if retrouves[k] in pertinents else 0                   # le document de rang k + 1 est-il pertinent ?
        assert abs((precisions[k] - precisions[k - 1]) - (x - precisions[k - 1]) / (k + 1)) < 1e-12
    print(f"  P@1..P@5 = {[round(v, 4) for v in precisions]} : baisse, hausse, baisse, baisse")
    assert round(precisions[2] - precisions[1], 4) == 0.1667                 # (1 - 0,5) / 3

    print("4. Moins de k résultats renvoyés : on divise quand même par k")
    courte = ["plafond-50", "frais-carte", "retraite-30"]                   # le moteur s'est arrêté à 3
    p = precision_at_k(courte, pertinents, 5)
    print(f"  3 résultats dont 2 pertinents, k = 5 : P@5 = {p:.4f} (et non 2/3 = 0.6667)")
    assert p == 0.4 and abs(5 * p - 3 * recall_at_k(courte, pertinents, 5)) < 1e-12

    print("5. Doublons : dédoublonner AVANT de tronquer")
    avec_doublon = ["plafond-50", "plafond-50", "frais-carte", "retraite-30", "taux-variable"]
    assert dedupliquer(avec_doublon) == ["plafond-50", "frais-carte", "retraite-30", "taux-variable"]
    ancien, corrige = ancienne_precision(avec_doublon, rel_2, 3), precision_at_k(avec_doublon, rel_2, 3)
    print(f"  ancienne version P@3 = {ancien:.4f} ; corrigée P@3 = {corrige:.4f}")
    assert round(ancien, 4) == 0.3333 and round(corrige, 4) == 0.6667
    triple = ["plafond-50", "plafond-50", "plafond-50"]
    naif = sum(1 for d in triple[:3] if d in {"plafond-50"}) / 3          # compte le même document trois fois
    p = precision_at_k(triple, {"plafond-50"}, 3)
    print(f"  [d, d, d] avec Rel = {{d}} : comptage naïf = {naif:.4f} > plafond 1/3 ; corrigé = {p:.4f}")
    assert naif == 1.0 > min(1.0, 1 / 3) and p == 1 / 3

    print("6. Cas de bord")
    try:
        precision_at_k(retrouves, pertinents, 0)
    except ValueError:
        vide_p, vide_r = precision_at_k(retrouves, set(), 5), recall_at_k(retrouves, set(), 5)
        print(f"  k = 0 → ValueError (l'ancienne version renvoyait {ancienne_precision(retrouves, pertinents, 0)}) ; Rel vide → P@5 = {vide_p}, R@5 = {vide_r}")
        assert vide_p == 0.0 and vide_r is None
    else:
        raise AssertionError("k = 0 aurait dû être refusé")

    print("7. Pour aller plus loin : F1@5 et R-précision")
    p5, r5 = precisions[4], recall_at_k(retrouves, pertinents, 5)
    f1 = 2 * p5 * r5 / (p5 + r5)
    r_prec = precision_at_k(retrouves, pertinents, len(pertinents))
    print(f"  F1@5 = {f1:.4f} = 2h / (k + |Rel|) = 4/8 ; R-précision = P@3 = R@3 = {r_prec:.4f}")
    assert abs(f1 - 2 * 2 / (5 + 3)) < 1e-12 and abs(f1 - 0.5) < 1e-12
    assert r_prec == recall_at_k(retrouves, pertinents, 3)

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Le classement de la démonstration (|Rel| = 3)
  k = 1  plafond-50          h = 1  P@k = 1.0000  R@k = 0.3333  plafond = 1.0000
  k = 2  frais-carte         h = 1  P@k = 0.5000  R@k = 0.3333  plafond = 1.0000
  k = 3  toutes-mensualites  h = 2  P@k = 0.6667  R@k = 0.6667  plafond = 1.0000
  k = 4  taux-variable       h = 2  P@k = 0.5000  R@k = 0.6667  plafond = 0.7500
  k = 5  murabaha-profit     h = 2  P@k = 0.4000  R@k = 0.6667  plafond = 0.6000
2. Plafond : |Rel| = 2 et k = 5, un classement parfait ne dépasse pas 0.4
  P@5 = 0.4000 = min(1, 2/5) alors que R@5 = 1.0000
3. P@k n'est pas monotone en k ; variation exacte (x - P@k) / (k + 1)
  P@1..P@5 = [1.0, 0.5, 0.6667, 0.5, 0.4] : baisse, hausse, baisse, baisse
4. Moins de k résultats renvoyés : on divise quand même par k
  3 résultats dont 2 pertinents, k = 5 : P@5 = 0.4000 (et non 2/3 = 0.6667)
5. Doublons : dédoublonner AVANT de tronquer
  ancienne version P@3 = 0.3333 ; corrigée P@3 = 0.6667
  [d, d, d] avec Rel = {d} : comptage naïf = 1.0000 > plafond 1/3 ; corrigé = 0.3333
6. Cas de bord
  k = 0 → ValueError (l'ancienne version renvoyait 0.0) ; Rel vide → P@5 = 0.0, R@5 = None
7. Pour aller plus loin : F1@5 et R-précision
  F1@5 = 0.5000 = 2h / (k + |Rel|) = 4/8 ; R-précision = P@3 = R@3 = 0.6667
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : la précision n'est pas un simple ratio qu'on recopie. Elle partage son numérateur avec le rappel, elle a un plafond qui dépend de la question, elle n'est pas monotone en k, et ses deux conventions (dénominateur k, dédoublonnage avant troncature) changent le chiffre affiché.

## Squelette algorithmique

La précision regarde la pureté du haut du classement. Le programme commence par dédoublonner le classement, parce qu'un même passage renvoyé deux fois gonflerait les touchés.

```text
ALGORITHME PrecisionAtK
ENTRÉES : classement retrouvé, ensemble des pertinents Rel, k ≥ 1
SORTIE  : P@k, et le nombre de touchés h_k

  classement ← Dédoublonner(classement)
  h_k ← #{d parmi les k premiers du classement : d ∈ Rel}
  RETOURNER h_k / k, h_k

PROPRIÉTÉS vérifiées par le programme :
  k × P@k = h_k = |Rel| × R@k
  0 ≤ P@k ≤ min(1, |Rel| / k)
```

**Complexité.** Le dédoublonnage coûte O(n) avec un ensemble, pour un classement de longueur n ; le comptage des touchés O(k). La mémoire est O(n) pour l'ensemble des documents déjà vus.

**Du squelette au code.** `dedupliquer` est la première ligne, `touches_at_k` le comptage, `precision_at_k` le quotient, et `recall_at_k` sert à vérifier l'identité k × P@k = |Rel| × R@k. `ancienne_precision` reproduit l'ancienne version, qui tronquait le classement à k avant de dédoublonner : un passage renvoyé deux fois dans le top-k y occupait deux places pour un seul touché, et un pertinent placé juste après restait hors du compte.

## Cas d'usage réels aux Émirats

Les valeurs de k, de seuil et de précision ci-dessous sont illustratives : en production, on les mesure sur un jeu de questions annotées propre à chaque métier.

### Banque — un contexte de conformité noyé dans le bruit

Une banque de détail de Dubaï met à la disposition de ses conseillers un assistant qui répond aux questions d'octroi de crédit à partir de sa politique interne et des règles de la CBUAE, découpées en morceaux d'environ 300 mots. Pour la question « un client retraité qui rembourse déjà une carte de crédit peut-il prendre un prêt personnel ? », le jeu d'évaluation désigne trois morceaux pertinents : le plafond d'endettement total de 50 % du revenu, le plafond de 30 % pour un retraité, et la règle qui fait entrer toutes les mensualités existantes dans le calcul. Avec k = 8, le moteur ramène bien les trois, mais aussi cinq morceaux sur les frais de carte, les taux variables et la Murabaha : P@8 = 3/8 = 0,375 pour un rappel de 1, et le modèle reçoit deux plafonds différents noyés au milieu de passages hors sujet, au point d'appliquer parfois 50 % à un retraité. L'équipe ajoute un reranker et réduit le contexte à k = 4 : les trois morceaux pertinents restent en tête, le rappel reste à 1 et la précision passe à 3/4 = 0,75, exactement le plafond min(1, 3/4) du point 3, donc le mieux possible avec quatre places. Sans cette mesure, l'équipe aurait jugé le moteur « bon » sur son seul rappel, sans voir que le bruit faisait dérailler la réponse. La contrainte est réglementaire : appliquer le mauvais plafond revient à accorder un crédit que les règles de la CBUAE interdisent. En production, on suit la P@4 moyenne sur un échantillon de questions annotées chaque semaine et la part des réponses qui citent la règle des 30 % quand le client est retraité.

### Immobilier — des comparables qui gonflent l'estimation

Une agence de Dubaï fait préparer par un agent une première estimation d'appartements à partir des transactions comparables de son historique, chacune décrite par son quartier, son type de bien, sa surface en sqft, sa date et son prix en AED/sqft. Pour un deux-chambres de 1 100 sqft à Jumeirah Village Circle, l'agent récupère les dix transactions les plus proches ; un expert de l'agence juge « comparables » celles du même quartier, du même type, à 15 % près en surface et datant de moins de six mois. Six des dix le sont, soit P@10 = 0,6 : les quatre autres sont des villas d'un quartier voisin vendues autour de 2 100 AED/sqft, contre 1 450 AED/sqft pour les vrais comparables. La moyenne des dix prix monte alors à (6 × 1 450 + 4 × 2 100)/10 = 1 710 AED/sqft, soit une estimation de 1 881 000 AED au lieu de 1 595 000 AED, et l'acheteur prévoirait en plus les 4 % de frais de transfert du DLD sur une valeur gonflée. Comme les critères de l'expert se vérifient sur les métadonnées, l'agent calcule cette précision à chaque requête : sous 0,8, il filtre d'abord par quartier et par type, puis reclasse, et s'il reste moins de cinq comparables il annonce une estimation à faible confiance au lieu d'un chiffre. Sans la mesure de précision, l'erreur reste invisible, parce qu'une estimation fausse reste un nombre plausible. On suit la P@10 sur un échantillon mensuel revu par un expert et l'écart médian entre l'estimation de l'agent et le prix final de vente.

### Crypto — la même page indexée deux fois

Une plateforme d'actifs virtuels agréée par la VARA fait répondre un agent de support aux questions sur les frais et les limites de retrait, à partir de sa documentation publique et de ses procédures internes. Après une mise à jour de la grille des frais, l'ancienne et la nouvelle version de la page ont été indexées sous le même identifiant, si bien que la recherche renvoie deux fois ce document en tête. Le script d'évaluation de l'équipe faisait `set(retrouves[:k])` : pour une question à deux pertinents avec k = 3, il annonçait P@3 = 0,333, alors que la liste dédoublonnée contient bien les deux pertinents parmi ses trois premiers documents distincts (P@3 = 0,667, point 6 de la démonstration). Le vrai problème était ailleurs : le prompt contenait réellement le doublon, l'agent ne voyait donc qu'un des deux passages utiles, et ce pouvait être l'ancienne grille. L'équipe dédoublonne désormais dans le pipeline, avant de tronquer, donne à chaque morceau un identifiant de version (`frais@2026-10`) et ne garde que la version en vigueur. Une plateforme agréée doit donner à ses clients une information exacte et à jour sur ses frais : un passage périmé dans le contexte est un risque de conformité, pas seulement un défaut de qualité. On suit le nombre de doublons par requête, avec un objectif de zéro, et la P@3 sur le jeu d'évaluation.

### Assurance — choisir k avec la précision et le rappel

Un assureur auto et santé fait analyser les déclarations de sinistre par un agent qui retrouve les clauses applicables dans le contrat de l'assuré avant de proposer une décision au gestionnaire. Pour « pare-brise fissuré par un gravillon sur autoroute, véhicule de quatre ans », trois clauses sont pertinentes : la garantie bris de glace, la franchise applicable et l'exclusion des dommages antérieurs à la souscription. Avec k = 3, le moteur en ramène deux, donc P@3 = R@3 = 0,667, égalité attendue puisque k = |Rel| ; avec k = 8, il ramène les trois, mais P@8 = 3/8 = 0,375, et l'identité 8 × 0,375 = 3 × 1 montre que le rappel complet a été obtenu au prix de cinq clauses inutiles. L'équipe retient k = 5 derrière un reranker, ce qui donne P@5 = 0,6 et R@5 = 1 sur cette question, et envoie au modèle environ 2 000 tokens de clauses au lieu de 3 200, à raison de 400 tokens par morceau. Sans la précision, on aurait pris k = 8 « pour ne rien rater », en payant chaque appel plus cher et en exposant le modèle à des clauses santé hors sujet. L'assurance est supervisée par la CBUAE, et chaque refus d'indemnisation doit pouvoir être justifié par la bonne clause. En production, on suit la P@5 et la R@5 moyennes sur un échantillon de sinistres annotés par les gestionnaires, ainsi que le nombre de tokens de contexte par dossier.

### RH — deux régimes de fin de service dans le même contexte

Un cabinet RH présent dans plusieurs émirats répond aux salariés qui l'interrogent sur leur indemnité de fin de service. Pour un salarié expatrié du secteur privé, hors zone franche, trois morceaux sont pertinents : 21 jours de salaire de base par année de service pour les cinq premières années, 30 jours au-delà, et le plafond de 24 mois de salaire de base (décret-loi fédéral 33/2021). Le moteur renvoie ces trois morceaux, mais aussi celui du régime d'épargne propre au DIFC et celui de la GPSSA, qui concerne les ressortissants émiriens : P@5 = 3/5 = 0,6 pour un rappel de 1. Le rappel parfait masque le danger : le modèle mélange parfois les régimes et annonce une indemnité calculée selon les règles du DIFC à un salarié qui n'y travaille pas. Le cabinet filtre désormais les morceaux par juridiction et par statut du salarié avant le classement : il ne reste que les trois pertinents, et P@3 = 1, au plafond min(1, 3/3). Ces règles relèvent de régimes juridiques distincts, et chaque réponse automatique reste à confirmer avec le texte en vigueur avant tout versement. En production, on suit la P@3 par segment (secteur privé fédéral, DIFC, ressortissants émiriens) et le taux d'écart entre l'indemnité annoncée par l'agent et celle calculée par la paie.

### Secteur public — une recherche en arabe qui s'arrête trop tôt

Une entité de services publics en ligne, accessible par UAE Pass, répond en arabe et en anglais aux questions sur ses démarches, à partir de pages de procédure découpées en morceaux. Son moteur applique un seuil de similarité et renvoie donc parfois moins de k = 5 résultats. Pour une question en arabe sur le renouvellement d'un document, quatre morceaux sont pertinents (procédure, pièces à fournir, frais, délai), mais l'orthographe de la requête (alef avec ou sans hamza, ta marbuta écrite comme un ha) fait échouer la correspondance lexicale : le moteur ne renvoie que deux morceaux, tous deux pertinents. Le tableau de bord divisait par le nombre de résultats renvoyés et affichait 1,0 pour les requêtes en arabe, mieux que pour l'anglais ; avec la convention correcte, P@5 = 2/5 = 0,4 et R@5 = 2/4 = 0,5, ce qui révèle le vrai problème. Après normalisation de l'arabe à l'indexation et à la requête (formes de l'alef, ta marbuta, diacritiques), le moteur renvoie cinq morceaux dont les quatre pertinents : P@5 = 0,8, qui est le plafond min(1, 4/5), et R@5 = 1. Un service public doit offrir la même qualité de réponse dans les deux langues ; son corpus ne contient que des pages publiques, pour qu'aucune donnée personnelle d'usager n'entre dans le contexte. On suit P@5 et R@5 séparément par langue, avec une alerte quand l'écart entre l'arabe et l'anglais dépasse 0,1.

## Pièges et limites

- **Diviser par le nombre de résultats renvoyés** au lieu de k : un moteur qui renvoie peu de résultats paraît parfait (cas du secteur public).
- **Tronquer avant de dédoublonner, ou compter un doublon deux fois** : la première erreur fait perdre un document distinct, la seconde dépasse le plafond (démonstration, point 6).
- **Comparer des P@k entre questions** qui n'ont pas le même nombre de pertinents : le plafond min(1, |Rel|/k) change d'une question à l'autre.
- **Jugements incomplets** : un document que personne n'a jugé est compté non pertinent. Si un nouveau moteur remonte des documents utiles jamais annotés, sa précision mesurée baisse alors qu'il est meilleur ; on fait annoter les nouveaux documents du top-k avant de conclure.
- **Confondre les unités** : si la pertinence est jugée par document mais que le moteur renvoie des morceaux, il faut ramener chaque morceau à son document puis dédoublonner, ou bien annoter au niveau du morceau ; mélanger les deux fausse le numérateur.

### Exercice feuille blanche

1. Sans regarder le code, écrire `precision_at_k` (dédoublonnage, troncature, division par k), puis vérifier P@4 = 0,5 sur l'exemple de la démonstration.
2. Prédire, puis vérifier : pour le classement non pertinent, non pertinent, pertinent, pertinent, pertinent avec |Rel| = 3, que valent P@1 à P@5 ? (Réponse : 0 ; 0 ; 0,333 ; 0,5 ; 0,6. Ici la précision ne fait que monter, et R@5 = 1.)
3. Trouver le bug : `top_k = set(retrouves[:k]); return len(top_k & pertinents) / len(top_k)`. Que renvoie cette version pour la liste [d, d, d], Rel = {d} et k = 3, puis pour une liste vide ? (Réponse : 1,0 au lieu de 1/3, puis une division par zéro.)

## Pour aller plus loin

- **F1@k** : la moyenne harmonique de P@k et R@k, dont les propriétés sont démontrées à l'étape 50. Grâce à l'identité du point 2, elle se simplifie en F₁@k = 2hₖ/(k + |Rel|) ; sur l'exemple, 2 × 2/(5 + 3) = 0,5.
- **R-précision** : la précision au rang k = |Rel|. À ce rang, précision et rappel coïncident (point 2) et le plafond vaut 1, ce qui rend les questions comparables entre elles ; sur l'exemple, elle vaut P@3 = 0,667.
- **Précision moyenne (AP) et MAP** : la moyenne des P@k prise aux rangs des documents pertinents, qui fait entrer l'ordre dans le calcul (étape 61) ; la Context Precision de RAGAS en est une variante (étape 57).

> Suite : [MRR](<27-RAG-Formule-MRR.md>) — étape 27.
