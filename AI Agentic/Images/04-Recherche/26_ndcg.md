# Fiche 26 — NDCG

> Image : `26_ndcg.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 28 — NDCG](<../../05-RAG/28-RAG-Formule-NDCG.md>)

**Un bon passage vaut plus s'il est en tête**

## Formule

$$
\operatorname{NDCG@}k = \frac{\operatorname{DCG@}k}{\operatorname{IDCG@}k}, \qquad \operatorname{DCG@}k = \sum_{i=1}^{k} \frac{2^{\,rel_i} - 1}{\log_2(i + 1)}
$$

## Éléments

$$
k
$$

**k** : le nombre de résultats jugés.

$$
i
$$

**i** : la position, de 1 jusqu'à k.

$$
rel_i
$$

**relᵢ** : la pertinence graduée du résultat en position i (0, 1, 2, 3…).

$$
\log_2(i + 1)
$$

**log₂(i + 1)** : la pénalité de rang, plus forte en bas de liste.

$$
\operatorname{IDCG@}k
$$

**IDCG@k** : le DCG du classement idéal (les plus pertinents en tête).

$$
\operatorname{NDCG@}k \in [0, 1]
$$

**NDCG** : le score normalisé, entre 0 et 1.

## Ce que c'est

NDCG compare le classement obtenu au meilleur classement possible. Placer un passage très pertinent en position 1 compte plus qu'en position 8.

## Effets et impacts

- Il sert quand la pertinence n'est pas oui ou non, mais graduée.
- Un NDCG haut veut dire que le meilleur contexte arrive tôt, là où l'agent le lit.
- Si IDCG vaut 0 (aucun résultat pertinent), il faut fixer une convention explicite.
- Un bon classement ne garantit pas une bonne réponse.

## Exemple chiffré

Quatre passages de pertinence 3, 2, 1 et 0. Classement idéal :

$$
\operatorname{IDCG@}4 = \frac{7}{1} + \frac{3}{1{,}585} + \frac{1}{2} + 0 \approx 9{,}393
$$

Si le passage le plus pertinent arrive en 3ᵉ position (ordre 0, 2, 3, 1) :

$$
\operatorname{DCG@}4 = 0 + \frac{3}{1{,}585} + \frac{7}{2} + \frac{1}{2{,}322} \approx 5{,}823 \quad\Longrightarrow\quad \operatorname{NDCG@}4 \approx 0{,}620
$$

Les mêmes passages, mal ordonnés, perdent 38 % du score.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`dcg(notes, k)`** — Cette fonction se comporte comme un juge de course qui distribue des points aux coureurs selon leur ordre d'arrivée, en pesant aussi leur mérite : elle reçoit la liste des notes de pertinence dans l'ordre où le moteur a classé les passages et le nombre k de places qui comptent, ne garde que les k premières, numérote les places à partir de 1, puis transforme chaque note relᵢ en un gain égal à 2 puissance relᵢ moins 1 (7 pour une note de 3, rien pour une note de 0) et divise ce gain par log₂(i + 1), la pénalité qui s'alourdit à mesure qu'on descend dans la liste. Elle renvoie la somme de ces gains amortis, le DCG@k, qui vaut 9,393 pour l'ordre idéal 3, 2, 1, 0 et seulement 5,823 pour l'ordre 0, 2, 3, 1 ; c'est la brique de base que `ndcg` appelle deux fois.

**`ndcg(notes_obtenues, k)`** — Celle-ci est l'arbitre qui ramène la performance à une échelle commune : elle reçoit les notes dans l'ordre obtenu et la profondeur k, fabrique d'abord le classement rêvé en triant ces mêmes notes de la plus forte à la plus faible, en calcule le DCG, qui devient l'IDCG, le meilleur score possible, puis renvoie aussitôt `None` si ce score idéal est nul, car une liste sans aucun passage pertinent ne permet aucune comparaison honnête. Dans le cas contraire, elle divise le DCG du classement réel par l'IDCG et renvoie un rapport compris entre 0 et 1 : exactement 1 quand l'ordre est déjà parfait, 0,620 quand le passage le plus pertinent n'arrive qu'en troisième position.

**`main()`** — C'est l'inspecteur qui rejoue l'exemple chiffré de la fiche devant témoins : il calcule l'IDCG@4 des notes 3, 2, 1, 0 et le NDCG@4 de l'ordre maladroit 0, 2, 3, 1, imprime ces nombres avec trois décimales, puis vérifie par des `assert` que l'idéal vaut bien 9,393 et le score normalisé 0,620. Il ajoute deux contrôles de bord, un classement parfait qui doit donner exactement 1 et une liste de trois notes nulles qui doit renvoyer `None`, et n'imprime la ligne finale de succès qu'une fois toutes ces vérifications passées.

```python
"""Fiche 26 — NDCG : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def dcg(notes: list[int], k: int) -> float:
    """DCG@k = Σ_{i=1..k} (2^relᵢ − 1) / log₂(i + 1)."""
    return sum((2 ** rel - 1) / math.log2(i + 1) for i, rel in enumerate(notes[:k], start=1))


def ndcg(notes_obtenues: list[int], k: int) -> float | None:
    """NDCG@k = DCG@k / IDCG@k ; None si IDCG vaut 0 (aucun passage pertinent)."""
    idcg = dcg(sorted(notes_obtenues, reverse=True), k)
    if idcg == 0:
        return None
    return dcg(notes_obtenues, k) / idcg


def main() -> None:
    ideal = dcg([3, 2, 1, 0], 4)
    mal = ndcg([0, 2, 3, 1], 4)
    print(f"IDCG@4 = {ideal:.3f}   DCG@4 mal ordonné = {dcg([0, 2, 3, 1], 4):.3f}   NDCG@4 = {mal:.3f}")
    assert round(ideal, 3) == 9.393 and round(mal, 3) == 0.620
    assert ndcg([3, 2, 1, 0], 4) == 1.0 and ndcg([0, 0, 0], 3) is None
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
IDCG@4 = 9.393   DCG@4 mal ordonné = 5.823   NDCG@4 = 0.620
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`dcg` parcourt les k premiers résultats, numérotés à partir de 1, et additionne pour chacun son gain 2^rel − 1 divisé par log₂ de son rang plus un : un passage de pertinence 3 rapporte 7, un passage de pertinence 0 ne rapporte rien, et la division par le logarithme réduit l'apport des passages placés plus bas. `ndcg` calcule ensuite le même total pour le classement idéal, obtenu en triant les notes par ordre décroissant, et divise l'un par l'autre ; quand le total idéal est nul, aucun passage n'est pertinent et le NDCG n'est pas défini, ce que la fonction signale par `None` au lieu d'inventer une valeur. Dans ce programme, l'idéal est calculé à partir des notes obtenues, ce qui suffit quand tous les passages jugés ont été retrouvés ; l'étape 28 montre le cas général, où l'idéal vient de tous les passages jugés.

`main` vérifie l'exemple de la fiche : quatre passages de pertinence 3, 2, 1 et 0 donnent un IDCG@4 de 9,393, et les mêmes passages dans l'ordre 0, 2, 3, 1 ne donnent qu'un DCG de 5,823, soit un NDCG de 0,620 : un bon passage relégué en troisième position fait perdre 38 % du score.

## Squelette algorithmique

```text
ALGORITHME NDCG@k
ENTRÉES : notes de pertinence des résultats dans l'ordre obtenu, notes de tous les passages jugés, k
SORTIE  : NDCG@k dans [0 ; 1], ou « indéfini »

  FONCTION DCG(notes) : RETOURNER Σ sur i=1..k (2^notes[i] − 1) / log₂(i + 1)
  IDCG ← DCG(notes de tous les passages jugés, triées par ordre décroissant)
  SI IDCG = 0 ALORS RETOURNER « indéfini »
  RETOURNER DCG(notes obtenues) / IDCG
```

**Complexité.** O(k) pour chaque DCG, plus O(J log J) pour trier les J notes jugées (ou O(J) par comptage, les notes étant de petits entiers).

**Du squelette au code.** La fonction DCG est `dcg`, et les trois lignes suivantes sont `ndcg`.

## Dans le cours

- [Étape 28 — NDCG](<../../05-RAG/28-RAG-Formule-NDCG.md>)
- [Étape 28 bis — Théorèmes du cosinus et des métriques de classement](<../../05-RAG/28b-Theoremes-Cosinus-et-Metriques-de-Classement.md>)
