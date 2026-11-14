# Étape 3 — L'IDF de BM25

> Palier 07 · Étape 3 sur 8 · Précédent : [Étape 2 — Indexer le corpus](<02-Indexer-le-corpus.md>) · Suivant : [Étape 4 — Le score BM25](<04-Score-BM25.md>) · Retour à l'énoncé : [README du palier 07](<../../README.md>)

## Comment raisonner

BM25 est une somme de termes, et chaque terme est le produit de deux facteurs : le poids de rareté du mot (l'IDF) et ce que rapporte sa fréquence dans le document. On isole le premier facteur dans sa propre fonction, pour trois raisons : il ne dépend que de deux entiers, donc il se teste à la main en une ligne ; il a ses propres cas impossibles à refuser ; et l'étape suivante sera plus lisible si elle appelle `idf_bm25(n_t, n_docs)` au lieu d'aligner un logarithme au milieu d'une formule déjà longue.

On part de la formule du cours :

$$
\mathrm{IDF}(t) = \ln\left(1 + \frac{N - n(t) + 0{,}5}{n(t) + 0{,}5}\right)
$$

et l'on se demande d'abord quelles entrées n'ont pas de sens : un corpus sans document (N < 1), un mot présent dans un nombre négatif de documents, ou dans plus de documents qu'il n'en existe.

## Une première version, la formule classique

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`idf_bm25(n_t, n_docs)`** — Dans ce brouillon, la fonction est un numismate qui finit par attribuer une valeur négative aux pièces trop répandues : elle reçoit le nombre de documents qui contiennent le mot et le nombre total de documents, et renvoie le logarithme de (N − n(t) + 0,5) / (n(t) + 0,5), l'IDF classique de Robertson et Spärck Jones, sans aucune garde. Dès qu'un mot figure dans plus de la moitié des documents, le résultat devient négatif : pour 4 documents sur 7, il vaut −0,2513, si bien qu'un document qui contient ce mot courant perdrait des points face à un document qui ne le contient pas.

```python
# [extrait] brouillon
def idf_bm25(n_t: int, n_docs: int) -> float:
    return math.log((n_docs - n_t + 0.5) / (n_t + 0.5))
```

C'est l'IDF de Robertson et Spärck Jones, celle qu'on trouve dans beaucoup d'articles. Elle devient négative dès qu'un mot est présent dans plus de la moitié des documents. Pour N = 7 et n(t) = 4 : ln(3,5 / 4,5) = ln 0,7778 = −0,2513. Un document qui contient ce mot courant **perdrait** des points par rapport à un document qui ne le contient pas : le classement devient absurde. Lucene, et la plupart des moteurs, ajoutent 1 dans le logarithme ; pour le même mot, ln(1 + 0,7778) = 0,5754, petit mais positif.

## La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`idf_bm25(n_t, n_docs)`** — C'est la même fonction, devenue le numismate de Lucene, pour qui même la pièce la plus commune garde une petite valeur positive : elle reçoit le nombre de documents qui contiennent le mot et le nombre total de documents, lève `ValueError` si le corpus compte moins d'un document ou si n(t) sort de [0, N], puis renvoie le logarithme népérien de 1 + (N − n(t) + 0,5) / (n(t) + 0,5). Sur 7 documents, un mot présent dans un seul, comme `retraite` ou `pret`, pèse 1,6740, `endettement`, présent dans deux, 1,1632, `plafond`, présent dans trois, 0,8267, et `idf_bm25(8, 7)` est refusé au lieu de rendre en silence −0,0606.

```python
# [extrait] agent/recherche.py
def idf_bm25(n_t: int, n_docs: int) -> float:
    """IDF(t) = ln(1 + (N − n(t) + 0,5) / (n(t) + 0,5)), la variante de Lucene : toujours positive.

    Exemple : un mot présent dans 1 document sur 7 : ln(1 + 6.5 / 1.5) ≈ 1.6740.
    """
    if n_docs < 1 or not 0 <= n_t <= n_docs:
        raise ValueError("il faut n_docs >= 1 et 0 <= n_t <= n_docs")
    return math.log(1 + (n_docs - n_t + 0.5) / (n_t + 0.5))
```

Ligne par ligne :

- `if n_docs < 1 or not 0 <= n_t <= n_docs:` regroupe les trois cas impossibles. `0 <= n_t <= n_docs` est une **comparaison chaînée** : Python la lit comme `0 <= n_t and n_t <= n_docs`. En Java, il faudrait écrire `n_t < 0 || n_t > n_docs`.
- `raise ValueError(…)` : la convention de tout le cours pour une entrée invalide. Le message dit ce qu'il faut, pas seulement ce qui ne va pas.
- `math.log(x)` est le logarithme **népérien** (ln), comme `Math.log` en Java. `math.log10` serait une erreur silencieuse : tous les IDF seraient divisés par ln 10 ≈ 2,3026, et l'ordre des documents pourrait changer une fois les termes additionnés.
- `0.5` est un flottant, donc toute l'expression l'est. En Java, `(n_docs - n_t + 0.5) / (n_t + 0.5)` serait aussi en `double` ; le piège de la division entière (`/` entre deux `int`) n'existe pas en Python 3, où `/` rend toujours un flottant.

**Pourquoi la garde est nécessaire, et pas seulement prudente.** Sans elle, `idf_bm25(8, 7)` calculerait (7 − 8 + 0,5) / 8,5 = −0,0588, puis ln(0,9412) = −0,0606 : un IDF négatif, rendu sans bruit, qui ferait baisser des scores. Une incohérence dans le comptage de n(t), comme celle du brouillon de l'étape 4, passerait donc inaperçue. Avec la garde, elle lève une erreur à l'endroit exact où elle se produit.

**Exemple fait à la main.** Pour un mot présent dans un seul document sur 7 :

$$
\mathrm{IDF} = \ln\left(1 + \frac{7 - 1 + 0{,}5}{1 + 0{,}5}\right) = \ln\left(1 + \frac{6{,}5}{1{,}5}\right) = \ln 5{,}3333 = 1{,}6740
$$

C'est le cas de `retraite`, `duree`, `pret` et `personnel` dans le corpus. `endettement` (2 documents : REG-1 et FORUM-9) pèse ln(1 + 5,5 / 2,5) = ln 3,2 = 1,1632, et `plafond` (3 documents : REG-1, REG-4, FORUM-9) pèse ln(1 + 4,5 / 3,5) = 0,8267.

```text
# [extrait] console
>>> from agent.recherche import idf_bm25
>>> round(idf_bm25(1, 7), 4), round(idf_bm25(2, 7), 4), round(idf_bm25(3, 7), 4)
(1.674, 1.1632, 0.8267)
```

- **Piège classique :** croire qu'un IDF élevé suffit à faire monter un document. `maximale` n'est dans aucun document : son IDF vaudrait ln(1 + 7,5 / 0,5) = ln 16 = 2,7726, le plus grand de tous, mais il ne rapportera rien, parce que sa fréquence vaut 0 dans chaque document. C'est la partie fréquence, à l'étape suivante, qui décide si le terme compte.

**Test qui passe maintenant :**

```powershell
python -m unittest -v tests.test_07_recherche.TestBM25.test_idf
```

Il compare `idf_bm25(1, 7)` à `math.log(1 + 6.5 / 1.5)` à 12 décimales, puis à 1,6740 à 4 décimales, et vérifie que `idf_bm25(8, 7)` lève `ValueError`.
