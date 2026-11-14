# Étape 4 — Le score BM25

> Palier 07 · Étape 4 sur 8 · Précédent : [Étape 3 — L'IDF de BM25](<03-IDF-de-BM25.md>) · Suivant : [Étape 5 — Classement et RRF](<05-Classement-et-RRF.md>) · Retour à l'énoncé : [README du palier 07](<../../README.md>)

## Comment raisonner

On recopie d'abord la formule, puis on la lit de l'extérieur vers l'intérieur :

$$
\mathrm{BM25}(Q, D) = \sum_{t \in Q} \mathrm{IDF}(t) \cdot \frac{f(t, D)\,(k_1 + 1)}{f(t, D) + k_1 \left(1 - b + b\,\dfrac{\lvert D \rvert}{\mathrm{avgdl}}\right)}
$$

- Le signe somme sur t ∈ Q, c'est une boucle `for t in requete` avec un accumulateur.
- Ce qui ne dépend pas de t (N et avgdl) se calcule **avant** la boucle, une seule fois.
- Dans la boucle, il faut f(t, D), puis n(t), puis l'IDF (étape 3), puis la partie fréquence.
- Un terme où f = 0 vaut exactement 0 : on peut le sauter, ce qui évite aussi de compter n(t) pour rien.

Il reste à décider des cas impossibles : un corpus vide n'a pas de longueur moyenne, et un corpus de documents tous vides a une longueur moyenne nulle, qui ferait diviser par zéro.

## Une première version, qui ressemble à BM25

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`bm25_score(requete, doc, corpus)`** — Dans ce brouillon, la fonction est un examinateur qui compte les occurrences au lieu des copies et récompense sans fin la répétition : elle reçoit les mots de la requête, ceux du document et le corpus, puis, pour chaque mot de la requête, compte ses occurrences dans tout le corpus, en tire un IDF, et ajoute au score cet IDF multiplié par le nombre d'occurrences dans le document, avant de renvoyer la somme. C'est en réalité un TF-IDF sans saturation ni prise en compte de la longueur : REG-4 obtient 2,3263 pour `jours` au lieu de 2,0664, et la requête du client C-5 donne 5,0219 à REG-2 et 3,6638 à REG-1, au lieu de 5,0951 et 3,1771.

```python
# [extrait] brouillon
def bm25_score(requete: list[str], doc: list[str], corpus: list[list[str]]) -> float:
    n_docs = len(corpus)
    score = 0.0
    for t in requete:
        n_t = sum(d.count(t) for d in corpus)           # FAUX : compte des occurrences
        score += idf_bm25(n_t, n_docs) * doc.count(t)   # FAUX : ni saturation, ni longueur
    return score
```

Ce brouillon est en réalité un TF-IDF, avec deux erreurs classiques.

- **n(t) compte des documents, pas des occurrences.** Pour la requête `["jours"]`, REG-4 contient deux fois `jours` et c'est le seul document qui le contient : n(t) vaut 1, pas 2. Le brouillon surestime n(t), donc sous-estime l'IDF (1,1632 au lieu de 1,6740). Sur un plus gros corpus, un mot très répété pourrait même dépasser N, et la garde de l'étape 3 lèverait `ValueError` : c'est elle qui trahirait le bug.
- **Le score croît sans limite avec f, et ignore la longueur.** Ici, REG-4 obtient 1,1632 × 2 = 2,3263 pour `jours`, alors que BM25 lui donne 2,0664. Sur la requête du client C-5, le brouillon donne 5,0219 à REG-2 et 3,6638 à REG-1, au lieu de 5,0951 et 3,1771 : REG-1, long de 18 mots, est surévalué, et REG-2, plus court que la moyenne, sous-évalué.

## La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`bm25_score(requete, doc, corpus, k1, b)`** — C'est la même fonction, confiée à l'examinateur de BM25, qui compte les copies, plafonne les répétitions et tient compte de la longueur de chaque devoir : elle reçoit la requête, le document, le corpus tokenisé et les paramètres k₁ = 1,5 et b = 0,75, lève `ValueError` si le corpus est vide ou si sa longueur moyenne est nulle, puis calcule une fois le nombre de documents et la longueur moyenne. Pour chaque mot de la requête présent dans le document, elle compte les documents qui le contiennent, appelle `idf_bm25` et ajoute l'IDF multiplié par la partie fréquence saturée ; les mots absents sont sautés. Elle renvoie la somme, 5,0951 pour REG-2 sur la requête de référence.

```python
# [extrait] agent/recherche.py
def bm25_score(requete: list[str], doc: list[str], corpus: list[list[str]], k1: float = 1.5, b: float = 0.75) -> float:
    """BM25(q, d) = Σ_{t ∈ q} IDF(t) · f(t,d) · (k₁ + 1) / (f(t,d) + k₁ · (1 − b + b · |d| / avgdl)).

    Un mot absent du document ne compte pour rien. Exemple (scénario b de 77) : REG-2 obtient ≈ 5.0951.
    """
    if not corpus:
        raise ValueError("corpus vide")
    n_docs = len(corpus)
    avgdl = sum(len(d) for d in corpus) / n_docs
    if avgdl == 0:
        raise ValueError("corpus sans aucun mot : avgdl nul")
    score = 0.0
    for t in requete:
        f = doc.count(t)
        if f == 0:
            continue
        n_t = sum(1 for d in corpus if t in d)
        score += idf_bm25(n_t, n_docs) * f * (k1 + 1) / (f + k1 * (1 - b + b * len(doc) / avgdl))
    return score
```

Groupe par groupe :

- **La signature.** `k1: float = 1.5, b: float = 0.75` : les valeurs usuelles, en paramètres nommés avec défaut. En Java, il faudrait une surcharge `bm25Score(requete, doc, corpus)` qui appelle la version complète ; en Python, un seul `def` suffit. `corpus` est une liste de listes de mots, pas l'index : la fonction ne connaît pas les identifiants, elle reste réutilisable.
- **Les gardes.** `if not corpus` attrape la liste vide (ici, tester la vérité est correct, puisqu'on veut justement refuser le vide). `if avgdl == 0` attrape un corpus dont tous les documents sont vides : sans elle, `len(doc) / avgdl` lèverait un `ZeroDivisionError` beaucoup moins parlant.
- **Les statistiques du corpus.** `n_docs` et `avgdl` sont calculées une fois, avant la boucle. `sum(len(d) for d in corpus) / n_docs` est la moyenne du rappel de cours ; sur le corpus complet, 94 / 7 = 13,4286.
- **La boucle.** `f = doc.count(t)` compte les occurrences de t dans le document, comme `Collections.frequency(doc, t)` en Java. `continue` saute un mot absent, qui rapporterait 0 de toute façon.
- **n(t).** `sum(1 for d in corpus if t in d)` compte les documents qui contiennent t au moins une fois : `t in d` vaut vrai ou faux, quelle que soit la répétition. C'est la correction du premier défaut du brouillon.
- **La formule.** Elle est écrite telle quelle, sans variable intermédiaire. Les parenthèses suivent exactement celles du cours : `(1 - b + b * len(doc) / avgdl)` est le facteur de longueur, multiplié par `k1`, ajouté à `f`.

**Exemple fait à la main, REG-2.** Le document a 13 mots, un peu moins que la moyenne, donc son dénominateur de saturation est un peu plus petit que k₁ :

$$
K = 1{,}5 \times \left(1 - 0{,}75 + 0{,}75 \times \frac{13}{13{,}4286}\right) = 1{,}5 \times 0{,}9761 = 1{,}4641
$$

`duree`, `pret` et `personnel` y figurent une fois chacun, et dans aucun autre document : IDF = 1,6740, partie fréquence 1 × 2,5 / (1 + 1,4641) = 1,0146, soit 1,6984 par mot. Les quatre autres mots de la requête sont absents de REG-2 et sautés par `continue`.

$$
\mathrm{BM25}(Q, \text{REG-2}) = 3 \times 1{,}6740 \times 1{,}0146 = 3 \times 1{,}6984 = 5{,}0951
$$

```text
# [extrait] console
>>> from agent.recherche import bm25_score, indexer, tokeniser
>>> index = indexer()
>>> q = tokeniser("plafond d'endettement d'un retraité et durée maximale d'un prêt personnel")
>>> round(bm25_score(q, index["REG-2"], list(index.values())), 4)
5.0951
```

- **Analogie Java :** une méthode statique pure, sans état, que l'on pourrait annoter `@Contract(pure = true)` ; elle ne lit ni ne modifie rien en dehors de ses paramètres, ce qui la rend triviale à tester.
- **Piège classique :** utiliser `len(set(doc))` comme longueur. La longueur de BM25 est le nombre de mots, répétitions comprises ; avec des mots distincts, REG-3 et REG-4 paraîtraient plus courts qu'ils ne le sont.
- **Piège classique bis :** lemmatiser dans sa tête. FORUM-9 contient `retraites`, pas `retraite` : pour BM25, ce sont deux mots différents, et le forum n'obtient que 1,9524 (plafond et endettement). Le plongement, lui, range les deux formes dans le concept revenu : c'est l'une des raisons de combiner les deux signaux.

**Test qui passe maintenant :**

```powershell
python -m unittest -v tests.test_07_recherche.TestBM25.test_mot_absent_et_corpus_vide
```

Il vérifie qu'un mot absent rapporte exactement 0.0 et qu'un corpus vide lève `ValueError`. Le test des quatre scores du scénario, `TestBM25.test_scores_du_scenario_b`, passe par `rechercher_hybride` : il deviendra vert à l'étape 6.
