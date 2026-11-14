# Fiche 24 — TF-IDF

> Image : `24_tfidf.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 22 — BM25](<../../05-RAG/22-RAG-Formule-BM25.md>)

**Fréquent ici, rare dans le corpus**

## Formule

$$
\operatorname{TF\text{-}IDF}(t, d) = \operatorname{TF}(t, d) \times \log\left( \frac{N}{\operatorname{DF}(t)} \right)
$$

## Éléments

$$
t
$$

**t** : un terme.

$$
d
$$

**d** : un document.

$$
\operatorname{TF}(t, d)
$$

**TF(t, d)** : la fréquence du terme dans le document.

$$
N
$$

**N** : le nombre de documents du corpus.

$$
\operatorname{DF}(t)
$$

**DF(t)** : le nombre de documents qui contiennent t.

$$
\log\left( \frac{N}{\operatorname{DF}(t)} \right)
$$

**log(N / DF)** : le poids de rareté, l'IDF.

## Ce que c'est

TF-IDF valorise un mot souvent répété dans un document, et peu présent ailleurs. Un mot présent partout dans le corpus pèse presque rien. BM25 (fiche 11) en est la version améliorée.

## Effets et impacts

- Il explique la recherche lexicale et pourquoi elle complète les embeddings.
- Il rate les synonymes et les reformulations.
- Les noms propres, codes et termes rares montent.
- Un corpus trop petit rend DF instable.

## Exemple chiffré

Corpus de 1 000 documents. « splendide » apparaît 3 fois dans le document et dans 10 documents du corpus. « le » apparaît dans les 1 000 :

$$
\operatorname{TF\text{-}IDF}(\text{splendide}) = 3 \times \ln\frac{1\,000}{10} = 3 \times 4{,}605 \approx 13{,}8
$$

$$
\operatorname{TF\text{-}IDF}(\text{le}) = \operatorname{TF} \times \ln\frac{1\,000}{1\,000} = \operatorname{TF} \times 0 = 0
$$

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`tfidf(terme, doc, corpus)`** — Cette fonction est le critique littéraire qui repère les mots qui caractérisent vraiment un livre : un mot répété souvent dans ce livre mais rare dans la bibliothèque mérite d'être souligné, tandis qu'un « le » présent dans tous les ouvrages ne dit rien. Elle reçoit le terme, le document sous forme de liste de mots et le corpus, compte la fréquence du terme dans le document et le nombre de documents qui le contiennent, rend 0,0 si aucun ne le contient, et sinon TF × ln(N / DF). Sur le petit corpus de quatre documents, « splendide », présent une fois et dans un seul document, vaut ln 4 ≈ 1,386, et « le », présent partout, vaut 0.

**`main()`** — C'est le relecteur qui vérifie l'exemple de la fiche puis un cas en miniature. Il ne reçoit rien ; il calcule directement 3 × ln(1 000 / 10) ≈ 13,82 pour le terme rare de la fiche et 3 × ln(1 000 / 1 000) = 0 pour un terme présent partout, et vérifie ces deux valeurs par `assert`. Il construit ensuite un corpus de quatre petits documents, appelle `tfidf` pour « splendide » et « le » dans le premier, imprime 1,386 et 0,0, vérifie que le premier égale ln 4 et le second 0, et ne rend rien.

```python
"""Fiche 24 — TF-IDF : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def tfidf(terme: str, doc: list[str], corpus: list[list[str]]) -> float:
    """TF-IDF(t, d) = TF(t, d) × ln(N / DF(t))."""
    tf = doc.count(terme)
    df = sum(1 for d in corpus if terme in d)
    if df == 0:
        return 0.0
    return tf * math.log(len(corpus) / df)


def main() -> None:
    print(f"fiche : TF = 3, N = 1 000, DF = 10 : {3 * math.log(1000 / 10):.2f}   DF = N : {3 * math.log(1000 / 1000):.1f}")
    assert round(3 * math.log(100), 2) == 13.82 and math.log(1) == 0
    corpus = [["le", "contrat", "splendide"], ["le", "devis"], ["le", "contrat"], ["le", "chantier"]]
    s1, s2 = tfidf("splendide", corpus[0], corpus), tfidf("le", corpus[0], corpus)
    print(f"petit corpus : « splendide » = {s1:.3f}   « le » = {s2:.1f}")
    assert math.isclose(s1, math.log(4)) and s2 == 0
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
fiche : TF = 3, N = 1 000, DF = 10 : 13.82   DF = N : 0.0
petit corpus : « splendide » = 1.386   « le » = 0.0
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`tfidf` compte d'abord combien de fois le terme apparaît dans le document (TF), puis dans combien de documents du corpus il apparaît au moins une fois (DF). Si aucun document ne contient le terme, elle renvoie 0, ce qui évite une division par zéro. Sinon, elle multiplie TF par le logarithme de N / DF : plus le terme est rare dans le corpus, plus ce poids de rareté est grand, et un terme présent dans tous les documents reçoit un poids nul, puisque ln(N / N) = ln 1 = 0.

`main` vérifie d'abord l'exemple de la fiche : un terme répété 3 fois dans un document et présent dans 10 documents sur 1 000 obtient 3 × ln 100 ≈ 13,82, et un terme présent partout obtient 0. Il construit ensuite un petit corpus de quatre documents où « le » apparaît partout et « splendide » une seule fois : « splendide » obtient ln 4 ≈ 1,386, « le » obtient 0, ce qui est le comportement voulu pour une recherche lexicale qui doit faire ressortir les mots distinctifs et ignorer les mots vides.

## Squelette algorithmique

```text
ALGORITHME IndexTFIDF
ENTRÉES : corpus D₁ … D_N
SORTIE  : un vecteur de poids par document

  POUR CHAQUE terme t du vocabulaire FAIRE  DF(t) ← nombre de documents contenant t  FIN POUR
  POUR CHAQUE document D FAIRE
      POUR CHAQUE terme t de D FAIRE
          poids(D, t) ← TF(t, D) × ln(N / DF(t))
      FIN POUR
  FIN POUR
  REQUÊTE : score(D) ← Σ sur t ∈ requête poids(D, t)  (ou cosinus entre vecteurs TF-IDF)
```

**Complexité.** Construire l'index coûte O(taille totale du corpus) avec un comptage par dictionnaire. Le programme, plus simple, recompte DF en parcourant le corpus pour chaque appel : O(N × L) par terme. Une requête sur l'index ne lit que les documents qui contiennent ses termes.

**Du squelette au code.** Le calcul de DF et la ligne du poids sont les deux comptages et la valeur renvoyée par `tfidf`.

## Dans le cours

- [Étape 22 — BM25](<../../05-RAG/22-RAG-Formule-BM25.md>)
- [Étape 78 — Synthèse : les mathématiques de l'IA agentique](<../../14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md>)
