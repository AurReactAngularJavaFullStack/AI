# 06-RAG — Formule 07 — BM25

**Dossier :** 06-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  

**Nom du fichier :** 06-RAG-Formule-07-BM25.md

## Définition complète de chaque élément

BM25 est la fonction de ranking lexicale classique utilisée en recherche d’information. Elle complète la similarité cosinus dans les systèmes hybrides.

La formule pour un terme \( t \) dans un document \( d \) est :

$$
\text{BM25}(t, d) = \text{IDF}(t) \cdot \frac{f(t, d) \cdot (k_1 + 1)}{f(t, d) + k_1 \cdot \left(1 - b + b \cdot \frac{|d|}{\text{avgdl}}\right)}
$$
Le score total d’un document est la somme sur tous les termes de la requête.

### Définition de chaque symbole

- $$
  f(t,d)
  $$

  : fréquence du terme \( t \) dans le document \( d \). Plus elle est élevée, plus le score augmente (avec saturation).

- \( |d| \) : longueur du document (nombre de termes).

- $$
  \text{avgdl}
  $$

   : longueur moyenne des documents dans la collection.

- \( k_1 \) : paramètre de saturation de la fréquence (souvent 1.2 à 2.0). Plus \( k_1 \) est grand, plus la fréquence brute compte.

- \( b \) : paramètre de normalisation par la longueur (souvent 0.75). Plus \( b \) est proche de 1, plus les documents longs sont pénalisés.

- $$
  \text{IDF}(t)
  $$

  : Inverse Document Frequency. Plus le terme est rare dans la collection, plus il est discriminant.

\[
$$
\text{IDF}(t)
$$
 = \log \frac{N - n(t) + 0.5}{n(t) + 0.5}
\]

où \( N \) est le nombre total de documents et \( n(t) \) le nombre de documents contenant \( t \).

### Comportement

- Terme rare + fréquent dans le document → score élevé.
- Document très long → score réduit si \( b \) est élevé.
- Augmenter \( k_1 \) réduit la saturation sur les répétitions de termes.

## Code Python (version simplifiée)

```python
import math

def idf(n_docs_with_term: int, total_docs: int) -> float:
    return math.log((total_docs - n_docs_with_term + 0.5) / (n_docs_with_term + 0.5) + 1)

def bm25_term(tf: float, doc_len: float, avgdl: float, k1: float = 1.5, b: float = 0.75) -> float:
    return (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / avgdl))
```

## Cas d’usage métier maximum

**Finance / Banque** : excellents pour les termes réglementaires exacts (« ratio de solvabilité », « LCR »).

**Immobilier** : codes DPE, surfaces exactes, noms de quartiers.

**Crypto** : noms de fonctions, adresses, termes techniques de protocoles.

**Assurance, RH, BTP** : références légales, numéros de normes, termes contractuels précis.

BM25 est particulièrement fort quand les utilisateurs emploient le vocabulaire exact du domaine.
