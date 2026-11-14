# Étape 57 — Évaluation — Context Precision

> Étape 57 du parcours · Prérequis : [Precision, Recall et F1](<56-Evaluation-Formule-Precision-Recall-F1.md>) · Suite : [Context Recall](<58-Evaluation-Formule-Context-Recall.md>)

**Dossier :** 10-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  
**Nom du fichier :** 57-Evaluation-Formule-Context-Precision.md

## Définition

La Context Precision mesure si les passages (chunks) utiles du contexte injecté dans le prompt sont placés **en tête**, et pas seulement présents. Pour chaque rang k où se trouve un chunk pertinent, on calcule la Precision@k de l'étape 26, la part de chunks pertinents parmi les k premiers ; la Context Precision est la moyenne de ces Precision@k sur les seuls rangs pertinents. C'est la définition de la bibliothèque d'évaluation RAGAS, et non une version simplifiée : chaque chunk pertinent compte pour une précision qui dépend de son rang, ce qui en fait une précision **pondérée par le rang**. Le verdict « pertinent ou non » est rendu par un juge LLM, qui compare le chunk à la réponse de référence, ou par des étiquettes humaines. Le score vaut 1 exactement quand aucun chunk inutile ne précède un chunk utile ; il vaut 0 quand aucun chunk récupéré n'est pertinent ; il n'est pas défini quand rien n'a été récupéré.

## Rôle dans un agent

La Context Precision s'utilise à l'étape **observer**, hors ligne, sur un jeu de questions dont on connaît les passages utiles. Elle évalue le couple **retriever + reranker** : le retriever choisit les K passages, le reranker les réordonne, puis le constructeur de prompt les injecte dans cet ordre. L'ordre compte pour deux raisons. Quand le budget de contexte oblige à tronquer (étape 13 ter), ce sont les derniers passages qui disparaissent ; et le modèle exploite en général moins bien un passage noyé au milieu d'un long contexte qu'un passage placé en tête. La métrique sert donc à choisir et à régler un reranker, à vérifier qu'un changement d'embedding ne dégrade pas l'ordre, et à alimenter la barrière d'intégration continue de l'étape 13 bis. Elle ne mesure pas la couverture : un retriever qui renvoie un seul bon passage sur trois nécessaires peut avoir un score parfait, et c'est le Context Recall de l'étape 58 qui le détecte.

## Équation complète

Context Precision au rang K, définie quand au moins un chunk a été récupéré :

$$
\text{CP@}K = \frac{\sum_{k=1}^{K} \text{P@}k \cdot v_k}{\sum_{k=1}^{K} v_k}
$$

Precision@k, la part de chunks pertinents parmi les k premiers :

$$
\text{P@}k = \frac{1}{k} \sum_{j=1}^{k} v_j
$$

Conventions :

$$
K = 0 \;\Longrightarrow\; \text{CP indéfinie} \qquad\qquad \sum_{k=1}^{K} v_k = 0 \;\Longrightarrow\; \text{CP@}K = 0
$$

Lien avec la précision moyenne de l'étape 61, qui divise par tous les pertinents du corpus :

$$
\text{AP@}K = \frac{\sum_{k=1}^{K} \text{P@}k \cdot v_k}{\lvert \text{Rel} \rvert} = \text{CP@}K \times \text{Recall@}K
$$

## Décryptage des symboles

$$
K
$$

**Sens :** nombre de chunks récupérés et injectés dans le prompt · **Type / plage :** entier ≥ 0 · **Variable Python :** `len(v)`

$$
k
$$

**Sens :** rang d'un chunk dans le contexte, 1 pour le premier · **Type / plage :** entier de 1 à K · **Variable Python :** `k` dans `enumerate(v, start=1)`

$$
v_k
$$

**Sens :** verdict du juge pour le chunk au rang k : 1 s'il est utile pour répondre, 0 sinon · **Type / plage :** 0 ou 1 · **Variable Python :** `v[k - 1]`, produit par `verdicts(classement, pertinents)`

$$
\text{P@}k
$$

**Sens :** Precision@k, la part de chunks pertinents parmi les k premiers · **Type / plage :** réel dans [0, 1] · **Variable Python :** `precision_at_k(v, k)`, ou `vus / k` dans la boucle

$$
r
$$

**Sens :** nombre de chunks pertinents parmi les K récupérés, le dénominateur de CP · **Type / plage :** entier de 0 à K · **Variable Python :** `r = sum(v)`

$$
\text{CP@}K
$$

**Sens :** Context Precision, moyenne des Precision@k aux rangs pertinents · **Type / plage :** réel dans [0, 1], ou indéfinie si K = 0 · **Variable Python :** `context_precision(v)`

$$
\lvert \text{Rel} \rvert
$$

**Sens :** nombre total de passages pertinents dans le corpus, retrouvés ou non · **Type / plage :** entier ≥ r · **Variable Python :** `n_pertinents_total`

$$
\text{AP@}K
$$

**Sens :** précision moyenne de l'étape 61 : même numérateur que CP, divisé par |Rel| au lieu de r · **Type / plage :** réel dans [0, 1] · **Variable Python :** `average_precision(v, n_pertinents_total)`

## Démonstration

### 1. Le score est compris entre 0 et 1

Quand r ≥ 1, CP@K est la moyenne de r nombres : les Precision@k prises aux rangs pertinents. Chacune est dans [0, 1], parce qu'elle compte une partie des k premiers chunks et la divise par k. Une moyenne de nombres de [0, 1] est dans [0, 1]. Le score est même strictement positif dès qu'un chunk est pertinent : au premier rang pertinent k₁, la Precision@k₁ vaut 1/k₁ > 0.

### 2. Remonter un chunk pertinent d'un rang augmente toujours le score

On suppose qu'au rang m se trouve un chunk non pertinent et au rang m + 1 un chunk pertinent, et l'on échange les deux. Soit h le nombre de chunks pertinents aux rangs 1 à m − 1. Avant l'échange, le chunk pertinent est au rang m + 1, et le préfixe des m + 1 premiers contient h + 1 pertinents. Après, il est au rang m, et le préfixe des m premiers contient h + 1 pertinents. Son terme passe donc de (h + 1)/(m + 1) à (h + 1)/m. Les autres termes ne bougent pas, parce que :

- pour un rang pertinent avant m, le préfixe est inchangé ;
- pour un rang pertinent après m + 1, le préfixe contient les mêmes chunks, seulement dans un autre ordre, donc le même nombre de pertinents ;
- le chunk non pertinent n'apporte de terme ni avant ni après, puisque v vaut 0 pour lui.

Le dénominateur r ne change pas non plus. Le gain vaut donc

$$
\Delta \text{CP} = \frac{1}{r}\left(\frac{h+1}{m} - \frac{h+1}{m+1}\right) = \frac{h+1}{r\,m\,(m+1)} > 0
$$

Exemple : [0, 1, 1] vaut 0,5833 ; on échange les rangs 1 et 2 (m = 1, h = 0, r = 2), on obtient [1, 0, 1], qui vaut 0,8333 : le gain est 1/(2 × 1 × 2) = 0,25. Le programme vérifie l'inégalité et la valeur exacte du gain sur les 769 échanges possibles des listes de 2 à 8 chunks.

### 3. Conséquence : CP = 1 si et seulement si les pertinents sont devant

Si aucun chunk non pertinent ne précède un chunk pertinent, les r pertinents occupent les rangs 1 à r, chaque Precision@k vaut k/k = 1, et la moyenne vaut 1. Réciproquement, s'il existe un chunk non pertinent au rang j avant un pertinent au rang k > j, la Precision@k vaut au plus (k − 1)/k < 1 ; ce terme entre dans la moyenne, qui est donc < 1. Le point 2 donne en plus le chemin : à partir de n'importe quel ordre, on peut remonter les pertinents un rang à la fois, comme dans un tri à bulles, et chaque échange augmente strictement le score jusqu'à 1. C'est exactement ce qu'on attend d'un reranker parfait.

### 4. Ce que le score ne voit pas

Chaque terme ne dépend que du préfixe qui s'arrête à un rang pertinent. Deux conséquences, que l'ancienne version de ce fichier ne disait pas :

- **le bruit placé après le dernier pertinent ne coûte rien** : [1, 1, 0, 0, 0, 0] vaut 1, alors que sa Precision@6 vaut 1/3 et que les quatre derniers chunks consomment des tokens pour rien ;
- **les pertinents non récupérés ne coûtent rien** : si trois passages sont nécessaires et que le retriever n'en renvoie qu'un, en tête, [1, 0, 0] vaut 1. La couverture est le rôle du Context Recall de l'étape 58.

On publie donc toujours la Context Precision avec un rappel, et l'on surveille la Precision@K ou le nombre de tokens injectés si le coût du contexte compte.

### 5. Aucun pertinent : 0 ; rien récupéré : indéfini

Quand K ≥ 1 et qu'aucun chunk n'est pertinent, le dénominateur r est nul, mais chaque Precision@k vaut aussi 0 : le contexte n'est que du bruit, et toute moyenne de ces précisions vaut 0. RAGAS renvoie 0 dans ce cas, en ajoutant un epsilon au dénominateur, et ce parcours retient la même valeur, qui a un sens : le retriever a échoué. Une précaution s'impose pour les questions hors périmètre, pour lesquelles aucun passage pertinent n'existe dans le corpus : leur 0 ne dit rien du retriever. On les sépare du jeu, comme à l'étape 25, et on les utilise pour vérifier que l'agent répond « je ne sais pas ». Quand K = 0, il n'y a rien à juger : la fonction renvoie `None`, et la question sort de la moyenne.

### 6. Context Precision et précision moyenne : seul le dénominateur change

La précision moyenne de l'étape 61 a le même numérateur, mais elle divise par |Rel|, le nombre de pertinents du corpus, au lieu de r, le nombre de pertinents récupérés. Comme Recall@K = r / |Rel| (étape 25) :

$$
\text{AP@}K = \frac{\sum_k \text{P@}k \cdot v_k}{\lvert \text{Rel} \rvert} = \frac{\sum_k \text{P@}k \cdot v_k}{r} \cdot \frac{r}{\lvert \text{Rel} \rvert} = \text{CP@}K \times \text{Recall@}K
$$

L'AP combine donc l'ordre (CP) et la couverture (rappel). Comme r ≤ |Rel|, on a toujours AP ≤ CP, avec égalité seulement si tous les pertinents ont été récupérés. Avec trois pertinents au total, [1, 0, 0] donne CP = 1 mais AP = 1 × 1/3 ≈ 0,333 ; [0, 1, 0, 1] donne CP = (1/2 + 2/4)/2 = 0,5 et AP = 0,5 × 2/3 ≈ 0,333. Le code de l'ancienne version de ce fichier est donc juste pour la Context Precision, et faux s'il est réutilisé tel quel pour calculer une AP : c'est le défaut signalé à l'étape 61.

### 7. Exemple fait à la main (le code reprend ces nombres)

Trois chunks, pertinence [1, 0, 1] : P@1 = 1 et P@3 = 2/3, aux deux rangs pertinents.

$$
\text{CP@}3 = \frac{1 + \frac{2}{3}}{2} = \frac{5}{6} \approx 0{,}8333
$$

Les mêmes chunks dans l'ordre [0, 1, 1] : P@2 = 1/2 et P@3 = 2/3.

$$
\text{CP@}3 = \frac{\frac{1}{2} + \frac{2}{3}}{2} = \frac{7}{12} \approx 0{,}5833
$$

Et [1, 1, 0] vaut 1. Même contenu, trois scores : seul l'ordre change. Dans le scénario bancaire du programme, le retriever renvoie cinq passages dans l'ordre [0, 1, 0, 1, 1], soit

$$
\text{CP@}5 = \frac{\frac{1}{2} + \frac{2}{4} + \frac{3}{5}}{3} = \frac{1{,}6}{3} \approx 0{,}5333
$$

puis le reranker place les trois passages réglementaires en tête, [1, 1, 1, 0, 0], et le score passe à 1.

## Effets et comportement

- **Un chunk inutile placé devant pénalise tous les pertinents qui le suivent**, parce qu'il entre dans chacun de leurs préfixes ; placé derrière le dernier pertinent, il ne pénalise rien (point 4).
- **Le gain d'un échange est plus grand en tête** : il vaut (h + 1)/(r m (m + 1)), qui décroît vite avec le rang m. Remonter un pertinent du rang 2 au rang 1 rapporte bien plus que du rang 9 au rang 8.
- **Le score ne dépend que de l'ordre des verdicts**, pas des scores du retriever : deux rerankers qui produisent le même ordre ont la même Context Precision.
- **Le score hérite des défauts du juge.** Un juge LLM n'est pas déterministe : on fixe la version du modèle et la température, on répète la mesure et l'on publie la dispersion (étape 13 bis).

## Du symbole au code Python

| Notion | Variable ou fonction |
|---|---|
| verdicts v₁ … v_K | `verdicts(classement, pertinents)`, une `list[int]` |
| Precision@k | `precision_at_k(v, k)` |
| CP@K | `context_precision(v)` |
| AP@K de l'étape 61 | `average_precision(v, n_pertinents_total)` |
| Recall@K de l'étape 25 | `sum(v) / n_tot` |
| ordre du reranker | `sorted(retriever, key=lambda c: (-scores_reranker[c], c))` |

### Déroulé, ligne par ligne

**`verdicts(classement, pertinents)`** remplace le juge : pour chaque identifiant du classement, 1 s'il est dans l'ensemble étiqueté, 0 sinon. Pour le classement bancaire, on obtient `[0, 1, 0, 1, 1]`. En production, cette fonction appelle un juge LLM chunk par chunk.

**`precision_at_k(v, k)`** vérifie que k est entre 1 et K, sinon `ValueError`, puis renvoie `sum(v[:k]) / k` : pour `[0, 1, 0, 1, 1]` et `k = 4`, 2/4 = 0,5.

**`context_precision(v)`**, la formule.

- `if not v: return None` : rien n'a été récupéré, il n'y a rien à juger (point 5).
- `if any(x not in (0, 1) for x in v)` : un verdict qui ne vaut ni 0 ni 1 trahit une erreur du juge ; on lève `ValueError`.
- `r = sum(v)` puis `if r == 0: return 0.0` : aucun pertinent, le contexte n'est que du bruit (point 5).
- La boucle `for k, vk in enumerate(v, start=1)` parcourt les rangs à partir de 1. Quand `vk` vaut 1, `vus += 1` compte les pertinents vus jusqu'au rang k inclus, et `total += vus / k` ajoute la Precision@k. Pour `[0, 1, 1]` : au rang 2, `vus = 1` et l'on ajoute 0,5 ; au rang 3, `vus = 2` et l'on ajoute 0,6667. `total` vaut 1,1667.
- `return total / r` : 1,1667 / 2 = 0,5833. Le dénominateur est r, le nombre de pertinents **récupérés**.

**`average_precision(v, n_pertinents_total)`** a le même numérateur mais divise par `n_pertinents_total`, |Rel|. Elle renvoie `None` si ce nombre est nul et lève `ValueError` si l'on prétend avoir retrouvé plus de pertinents qu'il n'en existe.

**`main()`**, bloc par bloc.

1. Les trois exemples à la main, avec le détail des Precision@k aux rangs pertinents : 0,8333, 0,5833 et 1.
2. Le point 2 sur toutes les listes de 0 et de 1 de longueur 2 à 8, produites par `itertools.product((0, 1), repeat=K)`. Pour chaque paire « non pertinent au rang j + 1, pertinent au rang j + 2 » (indices Python à partir de 0), on construit la liste échangée `w`, on vérifie que le score monte et que le gain vaut exactement la formule. On vérifie aussi le point 3 : CP = 1 si et seulement si aucun 0 ne précède un 1.
3. Le point 4 : `[1, 1, 0, 0, 0, 0]` vaut 1 alors que P@6 = 1/3 ; puis les deux exemples du point 6 avec trois pertinents au total, et l'identité AP = CP × Recall@K. La même identité, et AP ≤ CP, sont ensuite vérifiées sur 2 000 listes tirées au hasard ; `random.seed(57)` rend le tirage reproductible.
4. Les conventions : liste vide → `None`, aucun pertinent → 0,0, verdict invalide → `ValueError`.
5. Le scénario bancaire : cinq passages, trois réglementaires. Le reranker trie par score décroissant, et par identifiant en cas d'égalité pour que l'ordre soit déterministe. Le score passe de 0,5333 à 1, et l'on vérifie que le reranker n'a ni ajouté ni retiré de passage.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`verdicts(classement, pertinents)`** — Cette fonction tient le rôle du juge qui, debout devant la pile de passages remontés par le retriever, lève pour chacun un carton 1 ou 0 : elle reçoit la liste des identifiants dans l'ordre des rangs et l'ensemble des identifiants étiquetés comme pertinents, et renvoie la liste des verdicts, 1 quand le passage figure dans l'ensemble et 0 sinon, sans rien vérifier d'autre. Pour le classement bancaire du retriever, elle produit [0, 1, 0, 1, 1], et pour l'ordre du reranker [1, 1, 1, 0, 0] ; en production, ce serait un juge LLM appelé passage par passage.

**`precision_at_k(v, k)`** — Celle-ci est le contrôleur qui s'arrête au k-ième passage de la pile et compte combien de bons il a déjà vus : elle reçoit la liste des verdicts et un rang k, lève une `ValueError` si k n'est pas compris entre 1 et la longueur de la liste, puis renvoie la somme des k premiers verdicts divisée par k. Pour [0, 1, 0, 1, 1] et k = 4, elle donne 2/4 = 0,5, et pour [1, 1, 0, 0, 0, 0] et k = 6, seulement 1/3 ; `average_precision` l'appelle à chaque rang pertinent, et `main` l'utilise pour détailler les termes de chaque exemple.

**`context_precision(v)`** — Cette fonction est la critique exigeante qui ne juge un classement qu'aux endroits où se trouvent les bons passages : elle reçoit la liste des verdicts, renvoie `None` si elle est vide, lève `ValueError` si un verdict vaut autre chose que 0 ou 1, et renvoie 0 si aucun passage n'est pertinent. Sinon, elle parcourt les rangs à partir de 1, ajoute à chaque rang pertinent la Precision@k, calculée à la volée avec le nombre de pertinents déjà vus, et divise la somme par le nombre de pertinents récupérés. Elle renvoie 0,8333 pour [1, 0, 1], 0,5833 pour [0, 1, 1], 1 pour [1, 1, 0], 0,5333 pour le classement bancaire avant reranking et 1 après.

**`average_precision(v, n_pertinents_total)`** — Celle-ci est la cousine plus sévère de la précédente, qui n'oublie pas les bons passages restés dans le corpus : elle reçoit les verdicts et le nombre total de pertinents qui existent, renvoie `None` si ce nombre est nul et lève `ValueError` si l'on prétend en avoir retrouvé davantage qu'il n'en existe. Elle additionne la Precision@k aux rangs pertinents, comme `context_precision`, mais divise par tous les pertinents existants : [1, 0, 0] et [0, 1, 0, 1], avec trois pertinents au total, valent toutes deux 1/3, et `main` vérifie sur 2 000 listes tirées au hasard que l'AP égale la Context Precision multipliée par le Recall@K et ne la dépasse jamais.

**`main()`** — C'est le chef d'orchestre des cinq vérifications : il refait les trois exemples à la main avec le détail de leurs termes, puis parcourt toutes les listes de 0 et de 1 de longueur 2 à 8 pour vérifier, sur 769 échanges, que remonter un pertinent d'un rang fait toujours monter le score du gain prévu, et que le score vaut 1 exactement quand aucun 0 ne précède un 1. Il montre ensuite que le bruit après le dernier pertinent est invisible et que l'AP vaut CP × Recall@K, contrôle les conventions `None`, 0 et `ValueError`, puis rejoue le scénario bancaire où le reranker fait passer le score de 0,5333 à 1 sans ajouter ni retirer de passage, avant d'afficher « OK ».

```python
"""Étape 57 — Context Precision : précision pondérée par le rang, échanges, différence avec l'AP."""
import itertools
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def verdicts(classement: list[str], pertinents: set[str]) -> list[int]:
    """vₖ = 1 si le chunk au rang k est pertinent. Le juge est ici une liste d'identifiants étiquetés."""
    return [1 if c in pertinents else 0 for c in classement]


def precision_at_k(v: list[int], k: int) -> float:
    """Part de chunks pertinents parmi les k premiers (étape 26)."""
    if not 1 <= k <= len(v):
        raise ValueError("il faut 1 <= k <= K")
    return sum(v[:k]) / k


def context_precision(v: list[int]) -> float | None:
    """CP@K = Σ P@k·vₖ / Σ vₖ. None si rien n'est récupéré ; 0.0 si aucun chunk n'est pertinent (comme RAGAS)."""
    if not v:
        return None
    if any(x not in (0, 1) for x in v):
        raise ValueError("chaque verdict vaut 0 ou 1")
    r = sum(v)
    if r == 0:
        return 0.0
    total, vus = 0.0, 0
    for k, vk in enumerate(v, start=1):
        if vk:
            vus += 1              # pertinents vus jusqu'au rang k inclus
            total += vus / k      # P@k, comptée seulement aux rangs pertinents
    return total / r


def average_precision(v: list[int], n_pertinents_total: int) -> float | None:
    """AP@K de l'étape 61 : même numérateur, mais divisé par TOUS les pertinents du corpus."""
    if n_pertinents_total == 0:
        return None
    if sum(v) > n_pertinents_total:
        raise ValueError("plus de pertinents retrouvés que de pertinents existants")
    numerateur = sum(precision_at_k(v, k) for k in range(1, len(v) + 1) if v[k - 1])
    return numerateur / n_pertinents_total


def main() -> None:
    print("1. Exemples à la main")
    for v, attendu in (([1, 0, 1], 0.8333), ([0, 1, 1], 0.5833), ([1, 1, 0], 1.0)):
        cp = context_precision(v)
        detail = " + ".join(f"{precision_at_k(v, k):.4f}" for k in range(1, len(v) + 1) if v[k - 1])
        print(f"   v = {v}   CP = ({detail}) / {sum(v)} = {cp:.4f}")
        assert round(cp, 4) == attendu

    print("2. Remonter un pertinent d'un rang augmente toujours CP (vérifié sur toutes les listes, K <= 8)")
    nb_echanges = 0
    for K in range(2, 9):
        for v in itertools.product((0, 1), repeat=K):
            v = list(v)
            for j in range(K - 1):
                if v[j] == 0 and v[j + 1] == 1:
                    w = v[:j] + [1, 0] + v[j + 2:]
                    h = sum(v[:j])                                        # pertinents avant le rang j + 1
                    gain = ((h + 1) / (j + 1) - (h + 1) / (j + 2)) / sum(v)
                    assert context_precision(w) > context_precision(v)
                    assert math.isclose(context_precision(w) - context_precision(v), gain)
                    nb_echanges += 1
            devant = all(not (v[a] == 0 and v[b] == 1) for a in range(K) for b in range(a + 1, K))
            assert (context_precision(v) == 1.0) == (sum(v) > 0 and devant)
    print(f"   {nb_echanges} échanges testés : CP monte à chaque fois ; CP = 1 exactement quand les pertinents sont devant")

    print("3. CP ne voit ni le bruit après le dernier pertinent, ni les pertinents non retrouvés")
    v = [1, 1, 0, 0, 0, 0]
    print(f"   v = {v}   CP = {context_precision(v):.4f}   P@6 = {precision_at_k(v, 6):.4f}")
    assert context_precision(v) == 1.0 and math.isclose(precision_at_k(v, 6), 1 / 3)
    for v, n_tot, ap_att in (([1, 0, 0], 3, 1 / 3), ([0, 1, 0, 1], 3, 1 / 3)):
        cp, ap, rec = context_precision(v), average_precision(v, n_tot), sum(v) / n_tot
        print(f"   v = {v}, {n_tot} pertinents au total : CP = {cp:.4f}   Recall@K = {rec:.4f}   AP = {ap:.4f}")
        assert math.isclose(ap, ap_att) and math.isclose(ap, cp * rec)

    random.seed(57)
    for _ in range(2000):                                                 # AP@K = CP@K × Recall@K
        K = random.randint(1, 12)
        v = [random.randint(0, 1) for _ in range(K)]
        n_tot = sum(v) + random.randint(0, 5)
        if n_tot == 0:
            continue
        assert math.isclose(average_precision(v, n_tot), context_precision(v) * sum(v) / n_tot)
        assert average_precision(v, n_tot) <= context_precision(v) + 1e-12

    print("4. Conventions")
    print(f"   rien récupéré : {context_precision([])}   aucun pertinent : {context_precision([0, 0, 0])}")
    assert context_precision([]) is None and context_precision([0, 0, 0]) == 0.0
    try:
        context_precision([1, 2])
    except ValueError as e:
        print(f"   v = [1, 2] → ValueError : {e}")
    else:
        raise AssertionError("un verdict hors de {0, 1} aurait dû être refusé")

    print("5. Banque : cinq passages avant et après le reranker")
    pertinents = {"pol-dbr-50", "pol-duree-48", "pol-montant-20x"}
    retriever = ["faq-cartes", "pol-dbr-50", "blog-epargne", "pol-duree-48", "pol-montant-20x"]
    scores_reranker = {"pol-dbr-50": 0.94, "pol-duree-48": 0.91, "pol-montant-20x": 0.88,
                       "faq-cartes": 0.42, "blog-epargne": 0.17}               # scores illustratifs
    rerank = sorted(retriever, key=lambda c: (-scores_reranker[c], c))
    v_avant, v_apres = verdicts(retriever, pertinents), verdicts(rerank, pertinents)
    print(f"   avant : {v_avant}  CP = {context_precision(v_avant):.4f}")
    print(f"   après : {v_apres}  CP = {context_precision(v_apres):.4f}   ordre : {rerank[:3]}")
    assert math.isclose(context_precision(v_avant), (1 / 2 + 2 / 4 + 3 / 5) / 3)
    assert context_precision(v_apres) == 1.0 and sorted(retriever) == sorted(rerank)

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Exemples à la main
   v = [1, 0, 1]   CP = (1.0000 + 0.6667) / 2 = 0.8333
   v = [0, 1, 1]   CP = (0.5000 + 0.6667) / 2 = 0.5833
   v = [1, 1, 0]   CP = (1.0000 + 1.0000) / 2 = 1.0000
2. Remonter un pertinent d'un rang augmente toujours CP (vérifié sur toutes les listes, K <= 8)
   769 échanges testés : CP monte à chaque fois ; CP = 1 exactement quand les pertinents sont devant
3. CP ne voit ni le bruit après le dernier pertinent, ni les pertinents non retrouvés
   v = [1, 1, 0, 0, 0, 0]   CP = 1.0000   P@6 = 0.3333
   v = [1, 0, 0], 3 pertinents au total : CP = 1.0000   Recall@K = 0.3333   AP = 0.3333
   v = [0, 1, 0, 1], 3 pertinents au total : CP = 0.5000   Recall@K = 0.6667   AP = 0.3333
4. Conventions
   rien récupéré : None   aucun pertinent : 0.0
   v = [1, 2] → ValueError : chaque verdict vaut 0 ou 1
5. Banque : cinq passages avant et après le reranker
   avant : [0, 1, 0, 1, 1]  CP = 0.5333
   après : [1, 1, 1, 0, 0]  CP = 1.0000   ordre : ['pol-dbr-50', 'pol-duree-48', 'pol-montant-20x']
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : la Context Precision est une moyenne de précisions prises aux rangs utiles. Elle monte à chaque fois qu'on remonte un passage utile, vaut 1 quand ils sont tous devant, et ne dit rien de ce qui manque : multipliée par le rappel, elle redonne l'AP.

## Squelette algorithmique

Trois algorithmes. Le premier prend la liste des K verdicts du juge, dans l'ordre des rangs, et rend la Context Precision : un seul passage suffit, parce qu'il suffit de compter les pertinents déjà vus pour connaître la Precision@k à chaque rang pertinent. Le deuxième prend les mêmes verdicts et le nombre total de pertinents du corpus, et rend l'AP de l'étape 61 : même numérateur, autre dénominateur. Le troisième mesure l'effet d'un reranker : il calcule les verdicts avant et après le réordonnancement, puis la Context Precision des deux ordres.

```text
ALGORITHME CONTEXT_PRECISION
ENTRÉES : v[1..K], verdicts du juge dans l'ordre des rangs (0 ou 1)
SORTIE  : CP@K, ou INDÉFINI si K = 0

  SI K = 0 ALORS RETOURNER INDÉFINI FIN SI
  POUR k de 1 à K FAIRE
      SI v[k] ∉ {0, 1} ALORS ERREUR FIN SI
  FIN POUR
  r ← Σ v[k]
  SI r = 0 ALORS RETOURNER 0 FIN SI              ▷ aucun chunk pertinent : le contexte n'est que du bruit
  total ← 0 ; vus ← 0
  POUR k de 1 à K FAIRE
      SI v[k] = 1 ALORS
          vus ← vus + 1                            ▷ pertinents parmi les k premiers
          total ← total + vus / k                  ▷ Precision@k, prise au rang pertinent k
      FIN SI
  FIN POUR
  RETOURNER total / r
```

```text
ALGORITHME AVERAGE_PRECISION
ENTRÉES : v[1..K] ; nRel, nombre total de pertinents dans le corpus
SORTIE  : AP@K, ou INDÉFINI si nRel = 0

  SI nRel = 0 ALORS RETOURNER INDÉFINI FIN SI
  SI Σ v[k] > nRel ALORS ERREUR FIN SI
  numérateur ← 0
  POUR k de 1 à K FAIRE
      SI v[k] = 1 ALORS
          numérateur ← numérateur + (Σ v[j] pour j de 1 à k) / k
      FIN SI
  FIN POUR
  RETOURNER numérateur / nRel                      ▷ égale CP@K × r / nRel
```

```text
ALGORITHME MESURER_UN_RERANKER
ENTRÉES : classement[1..K] du retriever ; score(c) donné par le reranker ; Pertinents, ensemble étiqueté
SORTIE  : (CP avant, CP après)

  réordonné ← classement trié par score décroissant, puis par identifiant croissant
  POUR k de 1 à K FAIRE
      SI classement[k] ∈ Pertinents ALORS avant[k] ← 1 SINON avant[k] ← 0 FIN SI
      SI réordonné[k] ∈ Pertinents ALORS après[k] ← 1 SINON après[k] ← 0 FIN SI
  FIN POUR
  RETOURNER (CONTEXT_PRECISION(avant), CONTEXT_PRECISION(après))
```

**Complexité :** CONTEXT_PRECISION fait deux passages sur les K verdicts, l'un pour les valider, l'autre pour sommer, plus le calcul de r : O(K) en temps, et O(1) en mémoire en dehors de la liste reçue, puisqu'il ne garde que `total` et `vus`. AVERAGE_PRECISION, écrit comme dans le code, recalcule la somme du préfixe à chaque rang pertinent : chaque recalcul coûte O(k), donc O(K²) dans le pire cas où tous les chunks sont pertinents, avec O(1) de mémoire. Un compteur courant, comme `vus` dans CONTEXT_PRECISION, ou l'identité AP = CP × r / nRel du point 6, ramènerait l'AP à O(K). MESURER_UN_RERANKER est dominé par le tri, O(K log K) ; les tests d'appartenance à l'ensemble des pertinents coûtent O(1) en moyenne chacun, d'où O(K) pour les verdicts, et la liste réordonnée occupe O(K). En production, le coût réel est ailleurs : le juge LLM est appelé une fois par chunk, soit K appels par question, et c'est ce nombre d'appels qu'il faut budgéter. La vérification exhaustive du programme, sur les 2ᴷ listes de longueur K ≤ 8, coûte O(2ᴷ × K²) : c'est une preuve par énumération, pas un algorithme à utiliser.

**Du squelette au code :** la première ligne de CONTEXT_PRECISION est `if not v: return None` dans `context_precision(v)` ; la boucle de validation est `any(x not in (0, 1) for x in v)`, suivie du `ValueError` ; les lignes `r ← Σ v[k]` et `SI r = 0` sont `r = sum(v)` et `return 0.0` ; la boucle principale est `for k, vk in enumerate(v, start=1)`, avec `vus += 1` et `total += vus / k` ; le RETOURNER final est `return total / r`. AVERAGE_PRECISION est `average_precision(v, n_pertinents_total)`, et la somme du préfixe recalculée à chaque rang est l'appel `precision_at_k(v, k)`, qui fait `sum(v[:k]) / k` : c'est ce recalcul qui donne le O(K²). MESURER_UN_RERANKER est le bloc 5 de `main()` : le tri est `sorted(retriever, key=lambda c: (-scores_reranker[c], c))`, où le signe moins donne l'ordre décroissant et l'identifiant départage les égalités, et les deux lignes SI de la boucle sont les deux appels `verdicts(retriever, pertinents)` et `verdicts(rerank, pertinents)`.

## Cas d'usage réels aux Émirats

Les volumes, les scores et les seuils ci-dessous sont illustratifs ; seules les règles réglementaires citées sont réelles.

### Banque — les règles d'un prêt personnel en tête du contexte

L'assistant de conformité d'une banque de détail de Dubaï répond aux conseillers sur les prêts personnels à partir de la politique interne, qui transpose les règles de la CBUAE : ratio d'endettement total d'au plus 50 % du salaire, montant d'au plus 20 fois le salaire, durée d'au plus 48 mois. Pour la question « quelles limites s'appliquent ? », le retriever renvoie cinq passages dans l'ordre [0, 1, 0, 1, 1] : une FAQ sur les cartes passe en tête, un article sur l'épargne au milieu, et la Context Precision vaut 0,533. Le budget de contexte de l'agent ne garde que trois passages quand la conversation s'allonge : avec cet ordre, le plafond de 48 mois et celui de 20 fois le salaire seraient coupés, et l'agent pourrait valider un prêt sur 60 mois. L'équipe ajoute un reranker, qui place les trois passages réglementaires en tête, et le score passe à 1. Avant chaque mise en production, la barrière exige une Context Precision moyenne d'au moins 0,9 sur les questions étiquetées, publiée avec le rappel du même jeu, parce qu'un score parfait sur un seul passage ne garantit pas que les trois règles sont là. Les indicateurs suivis sont la Context Precision moyenne et la part de réponses dont tous les passages réglementaires tiennent dans les trois premiers rangs.

### Immobilier — des comparables de la bonne communauté d'abord

L'agent d'estimation d'une agence de Dubaï appuie chaque prix en AED/sqft sur des ventes comparables tirées de l'historique des transactions. Pour un deux-pièces de Dubai Marina, le retriever mélange des ventes de la même communauté et des ventes de communautés voisines, dont les prix au sqft sont différents. Un expert a marqué comme pertinentes les ventes de la même communauté, de surface proche, des douze derniers mois. Si les trois premiers passages viennent d'une communauté voisine, l'agent les lit en premier et ancre son estimation sur eux, même si les bons comparables suivent : la Context Precision chute alors que le rappel reste bon. L'agence règle son reranker pour faire remonter la communauté et la date, et suit la Context Precision par communauté, parce qu'une erreur de quelques pourcents sur le prix d'un bien pèse lourd pour l'acheteur, qui paie en plus 4 % de frais de transfert au DLD. L'indicateur suivi est la Context Precision moyenne par communauté, recalculée à chaque mise à jour de l'historique.

### Assurance — un score parfait qui cache une exclusion manquée

L'assistant des gestionnaires de sinistres d'un assureur auto et santé doit retrouver toutes les clauses qui s'appliquent à un sinistre, y compris les exclusions. Sur une question de test, le retriever renvoie [1, 0, 0, 0, 0] : la clause de garantie est en tête, la Context Precision vaut 1, et l'équipe pourrait croire le retrieval parfait. Or deux clauses étaient nécessaires, la garantie et l'exclusion « conduite sans permis valide », et l'exclusion n'a pas été récupérée : c'est exactement l'angle mort du point 4. L'assureur publie donc la Context Precision avec le Context Recall de l'étape 58, et ne déclare un retrieval sain que si les deux dépassent leur seuil. L'assureur est supervisé par la CBUAE, et une décision de sinistre doit reposer sur l'ensemble des clauses applicables, vérifiées par le gestionnaire. Les indicateurs suivis sont le couple Context Precision et Context Recall, mois par mois, et le nombre de décisions révisées pour clause oubliée.

### Crypto — un contexte tronqué par le budget

L'agent d'analyse d'une plateforme d'actifs virtuels agréée par la VARA lit des livres blancs longs, découpés en dizaines de passages, pour faire remonter les clauses de risque d'un jeton candidat à la cotation : clés d'administration, émission illimitée, suspension des transferts. Le budget de contexte ne laisse passer que les huit premiers passages ; un passage pertinent classé dixième n'est jamais lu. La Context Precision mesurée sur les vingt passages renvoyés peut paraître correcte alors que l'agent n'a vu que la tête de liste : l'équipe calcule donc la métrique sur les seuls passages réellement injectés, après la troncature, et non sur la sortie brute du retriever. Le gain d'un échange étant plus grand en tête (effets et comportement), les réglages du reranker portent d'abord sur les trois premiers rangs. Le rapport de l'agent reste un brouillon validé par un analyste, la VARA attendant une diligence documentée avant toute cotation (à confirmer avec le règlement en vigueur). Les indicateurs suivis sont la Context Precision après troncature et le nombre de clauses de risque présentes dans le corpus mais absentes du contexte injecté.

### RH — des passages en arabe relégués en fin de liste

L'assistant d'un cabinet RH présent dans plusieurs émirats répond en arabe et en anglais sur les congés, les visas et l'indemnité de fin de service. Sur les questions posées en arabe, le retriever renvoie bien les bons passages, mais souvent après des passages anglais proches du sujet : le rappel est correct, la Context Precision plus basse que pour l'anglais. La cause est la normalisation de l'arabe (alef, ta marbuta, diacritiques) appliquée aux documents mais pas toujours aux requêtes, ce qui fait baisser le score des passages arabes. L'équipe mesure la Context Precision séparément par langue, corrige la normalisation, et refuse toute version qui creuse l'écart entre les deux langues. Les questions sans politique pertinente, par exemple un type de visa que le client ne gère pas, valent 0 par convention ; elles sont sorties du calcul et servent de tests d'abstention. L'indicateur suivi est l'écart de Context Precision entre l'arabe et l'anglais.

### Secteur public — un reranker dans la barrière de déploiement

Un service public en ligne accessible par UAE Pass répond aux usagers à partir de pages de procédures. L'équipe veut remplacer son reranker par un modèle plus récent ; avant la bascule, elle rejoue son jeu de questions étiquetées et compare la Context Precision des deux versions, question par question, avec un test apparié (étape 13 bis). Le nouveau reranker gagne en moyenne, mais perd sur les procédures qui existent dans deux versions, l'une pour les citoyens et l'autre pour les résidents, où il remonte la mauvaise. Comme le score ne dépend que de l'ordre des verdicts, l'équipe a pu localiser la régression sur cette seule famille de questions et ajouter une règle de filtrage par profil avant le reranker. Les données des usagers sont soumises à la PDPL : le jeu d'évaluation est construit sur des questions anonymisées. Les indicateurs suivis sont la Context Precision par famille de procédures et le taux de redirection vers le centre de contact.

## Pièges et limites

- **Lire la Context Precision comme une couverture.** [1, 0, 0] vaut 1 même si trois passages étaient nécessaires ; on la publie toujours avec le Context Recall (étape 58).
- **La croire sensible au bruit en fin de liste.** Les chunks inutiles placés après le dernier pertinent ne coûtent rien au score, mais des tokens à chaque appel ; on suit la Precision@K ou la taille du contexte à part.
- **Diviser par |Rel| au lieu de r**, ou l'inverse. Diviser par |Rel| calcule l'AP de l'étape 61, pas la Context Precision ; réutiliser le code de la Context Precision pour l'AP surévalue l'AP dès qu'un pertinent manque.
- **Mesurer sur la sortie brute du retriever** alors que le prompt est tronqué : on mesure ce que le modèle lit, après la troncature.
- **Mélanger dans la moyenne les questions hors périmètre**, dont le 0 n'accuse pas le retriever.

### Exercice feuille blanche

1. Sans regarder le code, écrire `context_precision` à partir de la formule, avec `None` pour une liste vide et 0 quand aucun chunk n'est pertinent, puis vérifier 0,8333 et 0,5833.
2. Prédire, puis vérifier : que valent [0, 0, 1] et [1, 0, 0, 0, 1] ? (Réponse : 1/3 ≈ 0,333 ; (1 + 2/5)/2 = 0,7.) En échangeant les rangs 4 et 5 de la seconde liste, que devient le score, et quel gain donne la formule du point 2 avec m = 4, h = 1, r = 2 ? (Réponse : 0,75, soit un gain de 2/(2 × 4 × 5) = 0,05.)
3. Trouver le bug : la dernière ligne devient `return total / len(v)`. Que vaut alors [1, 1, 0, 0, 0, 0], et quelle métrique proche cette version calcule-t-elle par accident ?

## Pour aller plus loin

Quand la pertinence est graduée (très utile, utile, inutile) plutôt que binaire, le NDCG de l'[étape 28](<../05-RAG/28-RAG-Formule-NDCG.md>) remplace la Context Precision. RAGAS propose deux juges : l'un compare chaque chunk à la réponse de référence, l'autre à la réponse générée, quand on n'a pas de référence ; le second est moins coûteux à mettre en place mais récompense un contexte qui justifie une réponse fausse. Enfin, l'effet « perdu au milieu » (Liu et al., 2023) montre qu'un modèle exploite moins bien l'information placée au milieu d'un long contexte que celle placée au début ou à la fin, ce qui justifie de mesurer l'ordre et pas seulement la présence.

> Suite : [Context Recall](<58-Evaluation-Formule-Context-Recall.md>) — étape 58.
