# Étape 25 — RAG — Recall@k

> Étape 25 du parcours · Prérequis : [Reciprocal Rank Fusion](<24-RAG-Formule-RRF.md>) · Suite : [Precision@k](<26-RAG-Formule-Precision-at-k.md>)

**Dossier :** 05-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers, Product Engineers  
**Nom du fichier :** 25-RAG-Formule-Recall-at-k.md

## Définition

Le Recall@k, ou rappel au rang k, mesure la part des documents réellement pertinents pour une question qui figurent parmi les k premiers résultats du retriever. C'est une métrique de couverture : elle répond à la question « le retriever a-t-il ramené ce qu'il fallait ? », sans regarder ni l'ordre à l'intérieur des k premiers résultats, ni le bruit qui les accompagne. Elle exige une vérité terrain : pour chaque question du jeu d'évaluation, une personne du métier a étiqueté l'ensemble des documents pertinents. Quand une question n'a aucun document pertinent, le rappel vaut 0/0 et n'est pas défini : la fonction renvoie `None`, et la question sort des moyennes. Pour un même classement, le Recall@k ne baisse jamais quand k augmente, et il ne peut pas dépasser min(1, k/|Rel|), où |Rel| est le nombre de documents pertinents.

## Rôle dans un agent

Le Recall@k ne se calcule pas pendant la conversation, puisque l'agent ne connaît pas les bonnes réponses ; il sert à l'étape **observer**, hors ligne, sur un jeu de questions étiquetées que l'on rejoue à chaque changement du système. Il mesure la qualité du **retriever**, c'est-à-dire de ce qui arrive dans le prompt : une réponse ne peut pas être meilleure que son contexte, et si le passage nécessaire n'est pas dans les k premiers résultats, le modèle ne peut que deviner. On l'utilise pour choisir k, donc la taille du contexte injecté ; pour comparer des retrievers (BM25, vecteurs, score hybride, RRF, étapes 22 à 24) ; pour vérifier qu'une migration d'index ne change rien (étapes 20 et 21) ; et pour mesurer ce que coûte un index approché par rapport à une recherche exacte. Dans une chaîne d'intégration continue, une baisse du rappel moyen bloque la mise en production, comme un test qui échoue.

## Équation complète

Rappel au rang k pour une question q, défini seulement si q a au moins un document pertinent :

$$
\text{Recall@}k(q) = \frac{\lvert \text{Rel}(q) \cap \text{Top}_k(q) \rvert}{\lvert \text{Rel}(q) \rvert}
$$

Ensemble des questions qui ont au moins un document pertinent :

$$
Q^{+} = \{\, q \in Q \;:\; \lvert \text{Rel}(q) \rvert > 0 \,\}
$$

Rappel moyen (moyenne « macro », une voix par question) :

$$
\overline{\text{Recall@}k} = \frac{1}{\lvert Q^{+} \rvert} \sum_{q \in Q^{+}} \text{Recall@}k(q)
$$

Rappel « micro », une voix par document pertinent :

$$
\text{Recall@}k_{micro} = \frac{\sum_{q \in Q} \lvert \text{Rel}(q) \cap \text{Top}_k(q) \rvert}{\sum_{q \in Q} \lvert \text{Rel}(q) \rvert}
$$

Borne démontrée au point 2 :

$$
\text{Recall@}k(q) \le \min\left(1,\; \frac{k}{\lvert \text{Rel}(q) \rvert}\right)
$$

## Décryptage des symboles

$$
q
$$

Une question du jeu d'évaluation ; dans le code, chaque question est un couple `(retrouves, pertinents)`.

$$
Q
$$

Le jeu d'évaluation, c'est-à-dire l'ensemble des questions étiquetées ; en Python, la liste `evaluations` (ou `jeu`).

$$
\text{Rel}(q)
$$

L'ensemble des documents pertinents pour q, fixé par la vérité terrain ; il peut être vide ; variable `pertinents`, de type `set[str]`.

$$
\text{Top}_k(q)
$$

L'ensemble des k premiers documents renvoyés par le retriever pour q, au plus k documents distincts ; en Python, `set(retrouves[:k])`.

$$
k
$$

Le nombre de résultats que l'on regarde, un entier supérieur ou égal à 1 ; variable `k`. Ce k est celui du top-k, distinct du k₁ de BM25 et du k_RRF de l'étape 24.

$$
\lvert \text{Rel}(q) \cap \text{Top}_k(q) \rvert
$$

Le nombre de documents pertinents effectivement retrouvés parmi les k premiers, un entier entre 0 et min(k, |Rel(q)|) ; en Python, `len(top_k & pertinents)`.

$$
\text{Recall@}k(q)
$$

Le rappel de la question q, un réel dans [0 ; 1], ou `None` si Rel(q) est vide ; valeur renvoyée par `recall_at_k(retrouves, pertinents, k)`.

$$
Q^{+}
$$

Les questions qui ont au moins un document pertinent, les seules qui entrent dans la moyenne ; leur nombre est `len(definies)` dans `recall_moyen`.

$$
\overline{\text{Recall@}k}
$$

Le rappel moyen sur Q⁺, un réel dans [0 ; 1], ou `None` si Q⁺ est vide ; premier élément renvoyé par `recall_moyen(evaluations, k)`, le second étant le nombre de questions exclues.

## Démonstration

### 1. Le Recall@k ne baisse jamais quand k augmente

On fixe une question q et **un** classement des documents. Les k premiers résultats font partie des k + 1 premiers, puisque passer de k à k + 1 ajoute un élément sans en retirer : Topₖ ⊆ Topₖ₊₁. On enchaîne trois implications :

$$
\text{Top}_k \subseteq \text{Top}_{k+1} \;\Longrightarrow\; \text{Rel} \cap \text{Top}_k \subseteq \text{Rel} \cap \text{Top}_{k+1} \;\Longrightarrow\; \lvert \text{Rel} \cap \text{Top}_k \rvert \le \lvert \text{Rel} \cap \text{Top}_{k+1} \rvert
$$

La première vient de ce que l'intersection avec un même ensemble Rel conserve l'inclusion : un document pertinent présent dans Topₖ est aussi présent dans Topₖ₊₁. La seconde vient de ce qu'une partie d'un ensemble fini a au plus autant d'éléments que lui. On divise enfin les deux membres par |Rel|, qui est strictement positif, ce qui ne change pas le sens de l'inégalité :

$$
\text{Recall@}k \le \text{Recall@}(k+1)
$$

Le rappel augmente strictement si et seulement si le document au rang k + 1 est pertinent et n'était pas déjà compté ; sinon il reste égal. Par récurrence, Recall@k ≤ Recall@k′ pour tout k ≤ k′. L'ancienne version de ce fichier écrivait qu'augmenter k fait « généralement » monter le rappel : c'est faux dans l'autre sens, le rappel ne peut **jamais** baisser. Ce qui peut baisser quand k augmente, c'est la précision (étape 26).

Une nuance compte en pratique : la propriété vaut pour une même liste coupée à différents k. Dans certains index approchés, la largeur de la recherche dépend du k demandé, si bien que les dix premiers résultats d'une requête « k = 20 » ne sont pas toujours ceux d'une requête « k = 10 » ; on compare alors deux listes différentes, et rien ne garantit la monotonie. Pour mesurer une courbe de rappel, on demande une seule liste longue et on la coupe.

**Corollaire.** Le rappel moyen est lui aussi croissant en k, parce que c'est une moyenne de fonctions croissantes de k sur un ensemble Q⁺ qui ne dépend pas de k. L'ensemble des valeurs de k qui atteignent un objectif de rappel est donc un intervalle qui commence au plus petit k qui l'atteint et ne s'arrête plus : chercher ce premier k, en partant de k = 1, suffit.

### 2. Borne : Recall@k ≤ min(1, k/|Rel|)

Le numérateur compte des documents qui sont à la fois dans Rel et dans Topₖ. Il est donc au plus égal à |Rel|, et au plus égal à |Topₖ|, qui vaut au plus k :

$$
\lvert \text{Rel} \cap \text{Top}_k \rvert \le \min\left(\lvert \text{Rel} \rvert,\; k\right)
$$

En divisant par |Rel| :

$$
\text{Recall@}k \le \frac{\min(\lvert \text{Rel} \rvert,\, k)}{\lvert \text{Rel} \rvert} = \min\left(1,\; \frac{k}{\lvert \text{Rel} \rvert}\right)
$$

La borne est atteinte par un classement parfait, qui place tous les pertinents en tête : ses k premiers résultats contiennent alors exactement min(k, |Rel|) pertinents. Avec 4 documents pertinents et k = 2, même un retriever parfait ne dépasse pas 2/4 = 0,5. Un rappel faible à petit k ne prouve donc pas qu'un retriever est mauvais quand les questions ont beaucoup de documents pertinents : on le compare à sa borne.

### 3. La moyenne exclut les questions sans document pertinent

Pour une question dont Rel est vide, le rappel vaut 0/0 : il n'est pas défini, et toute valeur choisie par convention fausse la moyenne. L'ancien code renvoyait 0,0 dans ce cas. Sur quatre questions dont les rappels valent 0,5, 1,0, 0,0, et la quatrième n'a aucun pertinent, la moyenne correcte porte sur les trois questions de Q⁺ :

$$
\overline{\text{Recall@}k} = \frac{0{,}5 + 1{,}0 + 0{,}0}{3} = 0{,}5
$$

Avec l'ancienne convention, la quatrième question compte comme un échec du retriever alors qu'il n'y avait rien à trouver :

$$
\frac{0{,}5 + 1{,}0 + 0{,}0 + 0{,}0}{4} = 0{,}375
$$

Et une convention inverse, qui donnerait 1,0 à la question vide, produirait 0,625 : le choix arbitraire de la convention ferait varier la métrique de 0,25. Exclure ces questions est le seul choix neutre, à condition de publier aussi leur nombre. Elles restent utiles ailleurs : ce sont exactement les questions sur lesquelles l'agent doit répondre « je ne sais pas ».

### 4. Moyenne macro ou micro

La moyenne macro donne une voix à chaque question ; la moyenne micro donne une voix à chaque document pertinent. Avec deux questions, l'une qui a un seul pertinent, retrouvé (rappel 1), l'autre qui en a quatre, dont un seul est retrouvé (rappel 0,25) :

$$
\text{macro} = \frac{1 + 0{,}25}{2} = 0{,}625 \qquad \text{micro} = \frac{1 + 1}{1 + 4} = 0{,}4
$$

La moyenne micro pèse davantage sur les questions qui ont beaucoup de pertinents. Aucune n'est « la bonne » : la macro répond à « quelle part des questions sont bien servies ? », la micro à « quelle part des preuves arrive dans le contexte ? ». On annonce toujours laquelle on calcule.

### 5. Exemple fait à la main (le code reprend ces nombres)

Quatre documents sont pertinents, d1, d2, d4 et d6, et le retriever renvoie, dans l'ordre, d3, d7, d1, d9, d4, d2, d8, d6, d5, d10.

| k | Document au rang k | Pertinent ? | Pertinents retrouvés | Recall@k | Borne min(1, k/4) |
|---|---|---|---|---|---|
| 1 | d3 | non | 0 | 0 | 0,25 |
| 2 | d7 | non | 0 | 0 | 0,5 |
| 3 | d1 | oui | 1 | 0,25 | 0,75 |
| 4 | d9 | non | 1 | 0,25 | 1 |
| 5 | d4 | oui | 2 | 0,5 | 1 |
| 6 | d2 | oui | 3 | 0,75 | 1 |
| 7 | d8 | non | 3 | 0,75 | 1 |
| 8 | d6 | oui | 4 | 1 | 1 |
| 9 et 10 | d5, d10 | non | 4 | 1 | 1 |

Le Recall@5 vaut 2/4 = 0,5, comme dans l'ancienne version : la moitié des informations utiles est arrivée dans le contexte, ce qui peut être insuffisant pour une question réglementaire. La colonne du rappel ne baisse jamais (point 1), et elle reste sous la borne (point 2).

Pour choisir k, on rejoue un petit jeu de quatre questions : celle du tableau, une question dont le seul pertinent est premier, une question dont les deux pertinents sont aux rangs 2 et 4, et une question sans pertinent, exclue. Les rappels moyens pour k = 1 à 8 valent 0,333 ; 0,5 ; 0,583 ; 0,75 ; 0,833 ; 0,917 ; 0,917 ; 1. Le plus petit k qui atteint un rappel moyen de 0,9 est k = 6, et, par le corollaire du point 1, tout k plus grand l'atteint aussi.

## Effets et comportement

- **Augmenter k ne fait jamais baisser le rappel** (point 1), mais ajoute du bruit au contexte, ce qui fait baisser la précision (étape 26), augmente le coût en tokens et peut disperser l'attention du modèle sur des passages inutiles.
- **Le rappel ignore l'ordre à l'intérieur du top-k** : un pertinent au rang 1 ou au rang k compte pareil. Pour l'ordre, on utilise le MRR (étape 27) et le NDCG (étape 28).
- **Plus une question a de documents pertinents, plus le rappel à petit k est contraint** par la borne min(1, k/|Rel|) (point 2).
- **Le rappel n'est jamais meilleur que les étiquettes** : un document pertinent que personne n'a étiqueté ne compte ni au numérateur ni au dénominateur, et le rappel mesuré ne porte que sur les pertinents connus.

## Du symbole au code Python

| Notion | Variable ou fonction |
|---|---|
| Rel(q) | `pertinents`, un `set[str]` |
| la liste classée du retriever | `retrouves`, une `list[str]` |
| Topₖ(q) | `set(retrouves[:k])` |
| Recall@k(q) | `recall_at_k(retrouves, pertinents, k)` |
| rappel moyen sur Q⁺ et nombre d'exclues | `recall_moyen(evaluations, k)` |
| rappel micro | `recall_micro(evaluations, k)` |
| plus petit k qui atteint un objectif | `plus_petit_k(evaluations, objectif, k_max)` |

### Déroulé, ligne par ligne

**`recall_at_k(retrouves, pertinents, k)`**. C'est la formule du rappel.

- `if k < 1` : un top-0 n'a pas de sens ; on lève `ValueError` au lieu de renvoyer un nombre arbitraire.
- `if not pertinents: return None` : Rel est vide, la métrique n'est pas définie (point 3). L'ancien code renvoyait `0.0` à cet endroit.
- `top_k = set(retrouves[:k])` : la tranche `[:k]` garde les k premiers résultats, ou toute la liste si elle est plus courte ; `set` retire un éventuel doublon. Pour l'exemple et `k = 5`, on obtient `{'d3', 'd7', 'd1', 'd9', 'd4'}`.
- `return len(top_k & pertinents) / len(pertinents)` : `&` est l'intersection des deux ensembles, ici `{'d1', 'd4'}` ; 2 divisé par 4 donne `0.5`. Le dénominateur est |Rel|, pas k : diviser par k donnerait la précision de l'étape 26.

**`recall_moyen(evaluations, k)`** calcule le rappel de chaque question, garde les valeurs différentes de `None` dans `definies`, et renvoie leur moyenne avec le nombre de questions exclues, `len(valeurs) - len(definies)`. Si aucune question n'est définie, la moyenne vaut elle-même `None`.

**`recall_micro(evaluations, k)`** additionne les pertinents retrouvés de toutes les questions et divise par le total des pertinents ; `None` si ce total est nul.

**`ancien_recall_at_k`** reproduit l'ancien code pour mesurer l'effet de sa convention.

**`plus_petit_k(evaluations, objectif, k_max)`** essaie k = 1, 2, … et renvoie le premier dont le rappel moyen atteint l'objectif. Le corollaire du point 1 garantit que s'arrêter au premier est correct ; si l'objectif n'est jamais atteint jusqu'à `k_max`, la fonction renvoie `None`.

**`main()`**, bloc par bloc.

1. La courbe du point 5 : `[0.0, 0.0, 0.25, 0.25, 0.5, 0.75, 0.75, 1.0, 1.0, 1.0]`, et Recall@5 = 0,5.
2. La monotonie du point 1 : sur la courbe, puis sur 500 classements tirés au hasard (`random.seed(25)` rend le tirage reproductible) de 30 documents, avec 1 à 8 pertinents. Pour chaque k, le rappel ne baisse pas, et il monte si et seulement si `docs[k]`, le document au rang k + 1, est pertinent.
3. La borne du point 2 : la courbe reste sous `min(1.0, k / 4)`, et un classement parfait l'atteint exactement, avec 0,5 à k = 2.
4. La moyenne du point 3 : `[0.5, 1.0, 0.0, None]` donne 0,5 avec une question exclue ; l'ancienne convention donne 0,375.
5. Macro et micro (point 4) : 0,625 et 0,4.
6. Le choix de k (point 5) : les huit rappels moyens, puis `plus_petit_k(..., 0.9, 10)` renvoie 6, et un objectif impossible de 1,01 renvoie `None`.
7. Les cas limites : un doublon dans les deux premiers résultats occupe une place, d'où 0,5 ; une liste plus courte que k est prise entière ; Rel vide donne `None` ; `k = 0` lève `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`recall_at_k(retrouves, pertinents, k)`** — On peut se représenter un pêcheur qui connaît d'avance les poissons qu'il cherche et ne relève que les k premiers casiers de sa ligne : la fonction reçoit la liste ordonnée des documents retrouvés, l'ensemble des documents pertinents et la profondeur k, lève `ValueError` si k est inférieur à 1, et renvoie `None` quand l'ensemble des pertinents est vide, car la question « quelle part ai-je attrapée ? » n'a alors pas de sens. Sinon, elle garde les k premiers résultats sous forme d'ensemble, ce qui fait qu'un doublon occupe une place sans compter deux fois, compte ceux qui sont pertinents et divise par le nombre total de pertinents ; sur l'exemple à quatre pertinents, elle donne 0,5 à k = 5 et 1 dès k = 8.

**`recall_moyen(evaluations, k)`** — Cette fonction est l'inspecteur qui fait la tournée de toutes les questions d'un jeu d'évaluation et en tire une note globale honnête : elle reçoit une liste de couples (documents retrouvés, ensemble des pertinents) et la profondeur k, calcule le rappel de chaque question avec `recall_at_k`, écarte les `None` des questions sans aucun pertinent, puis renvoie un couple formé de la moyenne des valeurs restantes, ou `None` si rien ne reste, et du nombre de questions exclues. Sur le jeu du point 4, les rappels 0,5, 1,0, 0,0 et `None` donnent une moyenne de 0,5 avec une exclusion, là où l'ancienne convention, qui comptait un zéro, tombait à 0,375.

**`recall_micro(evaluations, k)`** — Là où la moyenne précédente donne une voix à chaque question, celle-ci donne une voix à chaque document, comme un recenseur qui compte les têtes plutôt que les familles : la fonction reçoit les mêmes couples et la même profondeur, additionne le nombre total de pertinents sur toutes les questions, renvoie `None` si ce total est nul, et sinon divise la somme des pertinents retrouvés dans les k premiers par ce total. Sur les deux questions du point 5, l'une avec un seul pertinent retrouvé, l'autre avec un pertinent retrouvé sur quatre, elle donne 2/5 = 0,4, quand la moyenne par question donne 0,625.

**`ancien_recall_at_k(retrieved, relevant, k)`** — Cette fonction conserve, comme une pièce d'archive, la version d'origine du calcul : elle reçoit la liste retrouvée, l'ensemble des pertinents et k, renvoie 0,0 au lieu de `None` quand il n'y a aucun pertinent, puis calcule le même rapport que `recall_at_k`, sans vérifier que k vaut au moins 1. Ce zéro silencieux est son défaut : une question sans réponse possible est traitée comme un échec du moteur, et `main` montre qu'elle fait tomber la moyenne du jeu du point 4 de 0,5 à 0,375.

**`main()`** — Le chef d'orchestre déroule sept vérifications : la courbe du rappel de k = 1 à 10 sur l'exemple à la main, de 0 à 1 en passant par 0,5 à k = 5, puis la monotonie, vérifiée sur cette courbe et sur 500 classements tirés au hasard avec une graine fixe, chaque hausse correspondant exactement à un pertinent au rang k + 1. Il contrôle ensuite la borne min(1, k/4) atteinte par un classement parfait, la moyenne qui exclut les `None`, l'écart entre moyenne macro et micro, puis le choix de k, où le plus petit k atteignant un rappel moyen de 0,9 vaut 6 et un objectif de 1,01 n'est jamais atteint. Les cas limites, doublon, liste trop courte, ensemble vide et k = 0 qui doit lever `ValueError`, ferment la marche, et la dernière ligne n'annonce le succès que si chaque `assert` a tenu.

```python
"""Étape 25 — Recall@k : définition, monotonie en k, borne min(1, k/|Rel|), moyenne qui exclut les None."""
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def recall_at_k(retrouves: list[str], pertinents: set[str], k: int) -> float | None:
    """|Rel ∩ Top_k| / |Rel| ; None si aucun document n'est pertinent (la métrique n'est pas définie)."""
    if k < 1:
        raise ValueError("k doit valoir au moins 1")
    if not pertinents:
        return None
    top_k = set(retrouves[:k])
    return len(top_k & pertinents) / len(pertinents)


def recall_moyen(evaluations: list[tuple[list[str], set[str]]], k: int) -> tuple[float | None, int]:
    """Moyenne sur les requêtes qui ont au moins un pertinent ; renvoie aussi le nombre de requêtes exclues."""
    valeurs = [recall_at_k(r, p, k) for r, p in evaluations]
    definies = [v for v in valeurs if v is not None]
    moyenne = sum(definies) / len(definies) if definies else None
    return moyenne, len(valeurs) - len(definies)


def recall_micro(evaluations: list[tuple[list[str], set[str]]], k: int) -> float | None:
    """Total des pertinents retrouvés / total des pertinents : chaque document pèse autant."""
    total = sum(len(p) for _, p in evaluations)
    if total == 0:
        return None
    return sum(len(set(r[:k]) & p) for r, p in evaluations) / total


def ancien_recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    """L'ancienne version : 0.0 quand il n'y a aucun pertinent."""
    if not relevant:
        return 0.0
    top_k = set(retrieved[:k])
    return len(top_k & relevant) / len(relevant)


def plus_petit_k(evaluations: list[tuple[list[str], set[str]]], objectif: float, k_max: int) -> int | None:
    """Le plus petit k dont le rappel moyen atteint l'objectif ; None s'il n'est jamais atteint."""
    for k in range(1, k_max + 1):
        moyenne, _ = recall_moyen(evaluations, k)
        if moyenne is not None and moyenne >= objectif:
            return k
    return None


def main() -> None:
    print("1. Exemple à la main : 4 documents pertinents, 10 résultats")
    pertinents = {"d1", "d2", "d4", "d6"}
    retrouves = ["d3", "d7", "d1", "d9", "d4", "d2", "d8", "d6", "d5", "d10"]
    courbe = [recall_at_k(retrouves, pertinents, k) for k in range(1, 11)]
    print("  Recall@1..10 = " + " ".join(f"{v:.2f}" for v in courbe))
    assert recall_at_k(retrouves, pertinents, 5) == 0.5
    assert courbe == [0.0, 0.0, 0.25, 0.25, 0.5, 0.75, 0.75, 1.0, 1.0, 1.0]

    print("2. Monotonie : Recall@k ne baisse jamais quand k augmente")
    assert all(a <= b for a, b in zip(courbe, courbe[1:]))
    random.seed(25)
    for _ in range(500):
        docs = [f"doc{i:02d}" for i in range(30)]
        random.shuffle(docs)
        rel = set(random.sample(docs, random.randint(1, 8)))
        valeurs = [recall_at_k(docs, rel, k) for k in range(1, 31)]
        for k in range(1, 30):
            assert valeurs[k - 1] <= valeurs[k]
            assert (valeurs[k] > valeurs[k - 1]) == (docs[k] in rel)    # hausse ⇔ le (k+1)-ième est pertinent
    print("  500 classements aléatoires, k de 1 à 30 : aucune baisse, et chaque hausse vient d'un pertinent au rang k + 1")

    print("3. Borne : Recall@k ≤ min(1, k / |Rel|)")
    for k, v in enumerate(courbe, start=1):
        assert v <= min(1.0, k / len(pertinents))
    parfait = sorted(pertinents) + ["d3", "d7", "d9"]
    bornes = [recall_at_k(parfait, pertinents, k) for k in range(1, 6)]
    print(f"  classement parfait : {bornes}   = min(1, k/4) pour k = 1..5")
    assert bornes == [min(1.0, k / 4) for k in range(1, 6)] and recall_at_k(parfait, pertinents, 2) == 0.5

    print("4. Moyenne sur des requêtes : on exclut celles qui n'ont aucun pertinent")
    jeu = [
        (["a1", "x", "y", "z"], {"a1", "a2"}),     # 1 pertinent retrouvé sur 2 → 0.5
        (["b1", "b2", "x"], {"b1", "b2"}),         # 2 sur 2 → 1.0
        (["x", "y", "z"], {"c1"}),                 # 0 sur 1 → 0.0
        (["x", "y", "z"], set()),                  # aucun pertinent → None, exclue
    ]
    par_requete = [recall_at_k(r, p, 3) for r, p in jeu]
    moyenne, exclues = recall_moyen(jeu, 3)
    ancienne = sum(ancien_recall_at_k(r, p, 3) for r, p in jeu) / len(jeu)
    print(f"  par requête : {par_requete}   moyenne = {moyenne} ({exclues} exclue)   ancienne convention = {ancienne}")
    assert par_requete == [0.5, 1.0, 0.0, None] and (moyenne, exclues) == (0.5, 1) and ancienne == 0.375

    print("5. Macro ou micro : deux moyennes qui ne répondent pas à la même question")
    deux = [(["e1", "x"], {"e1"}), (["f1", "x"], {"f1", "f2", "f3", "f4"})]
    macro, _ = recall_moyen(deux, 2)
    micro = recall_micro(deux, 2)
    print(f"  macro (moyenne des requêtes) = {macro}   micro (total des documents) = {micro}")
    assert macro == 0.625 and micro == 0.4

    print("6. Choisir k : le plus petit k qui atteint un rappel moyen de 0.9")
    evaluation = [
        (retrouves, pertinents),
        (["a1", "a2", "a3", "a4", "a5"], {"a1"}),
        (["b5", "b2", "b9", "b1", "b7"], {"b1", "b2"}),
        (["c4", "c8", "c2"], set()),
    ]
    moyennes = [recall_moyen(evaluation, k)[0] for k in range(1, 9)]
    print("  rappel moyen pour k = 1..8 : " + " ".join(f"{v:.3f}" for v in moyennes))
    assert [round(v, 3) for v in moyennes] == [0.333, 0.5, 0.583, 0.75, 0.833, 0.917, 0.917, 1.0]
    assert plus_petit_k(evaluation, 0.9, 10) == 6 and plus_petit_k(evaluation, 1.01, 10) is None

    print("7. Cas limites")
    assert recall_at_k(["d1", "d1", "d2"], {"d1", "d2"}, 2) == 0.5      # un doublon occupe une place du top-k
    assert recall_at_k(["d1"], {"d1", "d2"}, 10) == 0.5                 # k plus grand que la liste
    assert recall_at_k(["x"], set(), 3) is None
    try:
        recall_at_k(retrouves, pertinents, 0)
    except ValueError as e:
        print(f"  doublon dans le top-2 → 0.5 ; liste plus courte que k → 0.5 ; k = 0 → ValueError : {e}")
    else:
        raise AssertionError("k = 0 aurait dû être refusé")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Exemple à la main : 4 documents pertinents, 10 résultats
  Recall@1..10 = 0.00 0.00 0.25 0.25 0.50 0.75 0.75 1.00 1.00 1.00
2. Monotonie : Recall@k ne baisse jamais quand k augmente
  500 classements aléatoires, k de 1 à 30 : aucune baisse, et chaque hausse vient d'un pertinent au rang k + 1
3. Borne : Recall@k ≤ min(1, k / |Rel|)
  classement parfait : [0.25, 0.5, 0.75, 1.0, 1.0]   = min(1, k/4) pour k = 1..5
4. Moyenne sur des requêtes : on exclut celles qui n'ont aucun pertinent
  par requête : [0.5, 1.0, 0.0, None]   moyenne = 0.5 (1 exclue)   ancienne convention = 0.375
5. Macro ou micro : deux moyennes qui ne répondent pas à la même question
  macro (moyenne des requêtes) = 0.625   micro (total des documents) = 0.4
6. Choisir k : le plus petit k qui atteint un rappel moyen de 0.9
  rappel moyen pour k = 1..8 : 0.333 0.500 0.583 0.750 0.833 0.917 0.917 1.000
7. Cas limites
  doublon dans le top-2 → 0.5 ; liste plus courte que k → 0.5 ; k = 0 → ValueError : k doit valoir au moins 1
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : le rappel est une division de deux comptages, mais ses propriétés décident de l'évaluation. Il ne baisse jamais quand k augmente, il est plafonné par min(1, k/|Rel|), et sa moyenne n'a de sens que si l'on écarte, en les comptant, les questions sans document pertinent.

## Squelette algorithmique

Le rappel se mesure par question, puis se moyenne sur un jeu de questions. Le programme y ajoute la recherche du plus petit k qui atteint un objectif de rappel, ce qui fixe la taille du contexte à injecter.

```text
ALGORITHME RappelMoyen
ENTRÉES : évaluations (classement retrouvé, ensemble des pertinents) pour chaque question, k
SORTIE  : rappel moyen (macro) sur les questions qui ont au moins un pertinent, et rappel micro

  valeurs ← liste vide ; touchés_total ← 0 ; pertinents_total ← 0
  POUR CHAQUE (classement, Rel) FAIRE
      SI Rel est vide ALORS passer (le rappel n'est pas défini)
      touchés ← |Rel ∩ (k premiers du classement)|
      ajouter touchés / |Rel| à valeurs
      touchés_total ← touchés_total + touchés ; pertinents_total ← pertinents_total + |Rel|
  FIN POUR
  RETOURNER moyenne(valeurs), touchés_total / pertinents_total

ALGORITHME PlusPetitK
ENTRÉES : évaluations, objectif, k_max
  POUR k DE 1 À k_max FAIRE
      SI RappelMoyen(évaluations, k) ≥ objectif ALORS RETOURNER k
  FIN POUR
  RETOURNER aucun                                      (objectif jamais atteint)
```

**Complexité.** Un rappel coûte O(k) avec un ensemble pour Rel. Le rappel moyen sur Q questions coûte O(Q × k). La recherche du plus petit k répète ce calcul pour k = 1, 2, … : O(Q × k_max²) au pire ; comme le rappel ne peut que monter avec k (point 1 de la démonstration ci-dessus, repris à l'étape 28 bis), on pourrait aussi chercher par dichotomie en O(Q × k_max × log k_max).

**Du squelette au code.** `recall_at_k` est la ligne « touchés / |Rel| », `recall_moyen` et `recall_micro` les deux moyennes, et `plus_petit_k` la boucle sur k. `ancien_recall_at_k` reproduit l'ancienne version, qui renvoyait 0 au lieu de signaler une question sans pertinent.

## Cas d'usage réels aux Émirats

Les volumes, les objectifs et les valeurs de k ci-dessous sont illustratifs ; chaque équipe les fixe sur son propre jeu de questions étiquetées.

### Banque — toutes les règles d'un prêt personnel, pas seulement deux

L'assistant de conformité d'une banque de détail de Dubaï répond aux conseillers sur l'éligibilité aux prêts personnels. Pour la question « quelles limites s'appliquent à un prêt personnel ? », la vérité terrain compte trois sections de la politique interne, qui transposent les règles de la CBUAE : un ratio d'endettement total d'au plus 50 % du salaire, toutes mensualités comprises (30 % pour un retraité), un montant d'au plus 20 fois le salaire, et une durée d'au plus 48 mois. Si les cinq premiers passages ne contiennent que les deux premières sections, le Recall@5 vaut 2/3 ≈ 0,67, et l'agent peut valider un prêt sur 60 mois sans avoir vu le plafond de 48 mois. Avant la mise en production, l'équipe exige un rappel moyen au rang 5 d'au moins 0,95 sur ses questions étiquetées, et traite à part les questions hors périmètre, sans section pertinente : elles sont exclues de la moyenne et servent à vérifier que l'agent répond « je ne sais pas ». Sans cette mesure, les réponses paraissent fluides alors qu'elles reposent sur des preuves incomplètes. L'indicateur suivi est le rappel moyen au rang 5, recalculé à chaque changement d'index, de découpage ou de modèle, publié avec le nombre de questions exclues.

### Immobilier — plus de comparables que de places

L'agent d'estimation d'une agence de Dubaï cherche, dans l'historique des transactions, des ventes comparables (même communauté, surface proche, ventes récentes) pour appuyer un prix en AED/sqft. Pour un deux-pièces de Dubai Marina, l'expert a étiqueté 15 comparables pertinents ; avec k = 10, même un retriever parfait ne dépasse pas 10/15 ≈ 0,667 (démonstration, point 2). L'équipe publie donc le Recall@10 rapporté à sa borne : un rappel mesuré de 0,6 représente 0,6/0,667 = 90 % de ce qui était atteignable, ou bien elle augmente k pour les demandes d'estimation. Sans la borne, elle conclurait à tort que le retriever est mauvais et passerait des semaines à le « réparer ». L'enjeu est concret : une estimation construite sur un échantillon partiel peut tromper le client sur un achat dont les seuls frais de transfert du DLD représentent 4 % du prix. L'indicateur suivi est le Recall@10 divisé par sa borne, communauté par communauté.

### Crypto — le mécanisme dangereux qu'il ne faut pas rater

L'agent d'analyse d'une plateforme d'actifs virtuels agréée par la VARA lit le livre blanc et la documentation du contrat intelligent de chaque jeton candidat à la cotation, et doit faire remonter toutes les clauses de risque : clés d'administration, émission illimitée, possibilité de suspendre les transferts, calendrier de déblocage. Les analystes étiquettent, pour une question d'audit, 6 passages pertinents ; si les dix premiers passages en contiennent 5, le Recall@10 vaut 5/6 ≈ 0,833, et le passage manquant peut être justement celui qui permet au propriétaire de bloquer les transferts. Pour cet usage, le rappel compte plus que la précision : un passage inutile coûte quelques secondes de lecture, une clause manquée peut coûter les fonds des clients. L'équipe augmente k et améliore le découpage des documents jusqu'à atteindre son objectif de rappel moyen, et le rapport de l'agent reste un brouillon qu'un analyste valide. La VARA attend une diligence documentée avant toute cotation (à confirmer avec le règlement en vigueur). L'indicateur suivi est le Recall@10 sur des livres blancs étiquetés, et le nombre de clauses trouvées par les analystes mais manquées par l'agent.

### Assurance — choisir k avec le rappel

L'assistant des gestionnaires de sinistres d'un assureur auto et santé doit retrouver toutes les clauses applicables à un sinistre, en particulier les exclusions : une exclusion manquée conduit à un paiement indu, une clause de garantie manquée à un refus injustifié. Sur son jeu étiqueté, l'équipe calcule le rappel moyen pour k = 1 à 10 et retient le plus petit k qui atteint 0,9 ; dans le mini-exemple du programme, c'est k = 6 (0,917), alors que k = 5 ne donne que 0,833. Comme le rappel moyen ne peut pas baisser quand k augmente (corollaire du point 1), tout k plus grand atteindrait aussi l'objectif, et choisir le plus petit limite la taille du contexte et le coût en tokens. L'assureur est supervisé par la CBUAE, et une décision sur un sinistre doit reposer sur l'ensemble des clauses applicables, que le gestionnaire vérifie avant de décider. Les indicateurs suivis sont le rappel moyen au k retenu, remesuré chaque mois, et le taux de décisions de sinistre révisées après contestation.

### RH — un rappel par langue, une moyenne qui ne triche pas

L'assistant d'un cabinet RH présent dans plusieurs émirats répond en arabe et en anglais aux salariés sur les politiques RH : congés, indemnité de fin de service, visas. L'équipe mesure le Recall@5 séparément pour chaque langue ; avant la normalisation de l'arabe de l'étape 22, le rappel des questions en arabe était nettement inférieur à celui des questions en anglais, et l'écart se réduit après. Certaines questions n'ont aucune politique pertinente, par exemple une question sur un visa familial que l'entreprise cliente ne gère pas : elles sont exclues de la moyenne par la convention `None` et comptées à part comme tests d'abstention. Les compter comme des 0 ferait paraître le retriever plus mauvais dans la langue où ces questions sont les plus fréquentes, et pousserait à « corriger » ce qui fonctionne. L'équipe compare aussi les moyennes macro et micro : les questions à nombreuses sections pertinentes, comme celles qui portent sur des règles différentes selon l'émirat, pèsent davantage dans la seconde. L'indicateur suivi est le Recall@5 par langue, publié avec le nombre de questions exclues.

### Secteur public — le rappel d'un index approché

Un service public en ligne accessible par UAE Pass cherche parmi des millions de passages avec un index HNSW approché. Pour mesurer ce que coûte l'approximation, l'équipe prend la recherche exacte comme vérité terrain : pour chaque question de test, Rel contient les 10 vrais plus proches voisins, et le Recall@10 de l'index est la part de ces voisins qu'il renvoie. Elle règle le paramètre de largeur de recherche jusqu'à dépasser son objectif, par exemple 0,98, tout en tenant son budget de latence au 95e percentile. Elle tient compte de la nuance du point 1 : dans certaines implémentations, la largeur de recherche dépend du k demandé, si bien que les dix premiers résultats d'une requête « k = 20 » diffèrent parfois de ceux d'une requête « k = 10 » ; elle mesure donc toujours le rappel sur une seule liste, coupée à différents k. Une page de procédure manquée renvoie l'usager vers le centre de contact, en arabe comme en anglais. Les indicateurs suivis sont le Recall@10 de l'index à chaque reconstruction et la latence au 95e percentile.

## Pièges et limites

- **Donner une valeur aux questions sans pertinent.** 0 ou 1 par convention fausse la moyenne (point 3) ; on renvoie `None`, on exclut, et on publie le nombre d'exclues.
- **Comparer des rappels sans leur borne.** Un Recall@5 de 0,5 est parfait si la question a 10 pertinents ; on le rapporte à min(1, k/|Rel|) (point 2).
- **Diviser par k au lieu de |Rel|.** On calcule alors la précision de l'étape 26, pas le rappel.
- **Laisser des doublons dans la liste.** Un document répété occupe une place du top-k sans rien apporter ; on dédoublonne avant de mesurer, et surtout avant de remplir le prompt.
- **Oublier que le rappel ne voit ni l'ordre ni le bruit.** Un retriever qui place le bon passage au rang 10 a le même Recall@10 que celui qui le place au rang 1 : on complète avec la précision, le MRR et le NDCG (étapes 26 à 28).

### Exercice feuille blanche

1. Sans regarder le code, écrire `recall_at_k` à partir de la formule, avec `ValueError` pour k < 1 et `None` pour Rel vide, puis vérifier que Recall@5 vaut 0,5 sur l'exemple du point 5.
2. Prédire, puis vérifier : une question a 3 documents pertinents et le classement est parfait ; que vaut Recall@2 ? (Réponse : 2/3 ≈ 0,667, la borne.) Un jeu de quatre questions a pour rappels 1,0, 0,0, `None` et 0,5 ; que vaut la moyenne, et combien de questions sont exclues ? (Réponse : 0,5, une exclue.)
3. Trouver le bug : `return len(top_k & pertinents) / k`. Que mesure cette ligne, et pourquoi vaut-elle 0,4 au lieu de 0,5 sur l'exemple, à k = 5 ?

## Pour aller plus loin

Au rang k = |Rel|, la précision et le rappel coïncident, puisque leurs dénominateurs sont alors égaux : c'est la R-précision, qui évite de choisir k à la main. Certains bancs d'essai publient un rappel « plafonné », qui divise par min(k, |Rel|) au lieu de |Rel| et vaut donc 1 pour un classement parfait, quelle que soit la borne. Enfin, le « context recall » des cadres d'évaluation RAG, étudié à l'[étape 58](<../10-Evaluation/58-Evaluation-Formule-Context-Recall.md>), ne compte pas des documents mais des affirmations de la réponse de référence retrouvées dans le contexte : c'est une autre définition, sous le même nom.

> Suite : [Precision@k](<26-RAG-Formule-Precision-at-k.md>) — étape 26.
