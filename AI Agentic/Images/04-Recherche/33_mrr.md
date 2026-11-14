# Fiche 33 — MRR (Mean Reciprocal Rank)

> Image : `33_mrr.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 27 — MRR](<../../05-RAG/27-RAG-Formule-MRR.md>)

**Où se trouve le premier bon passage**

## Formule

$$
\operatorname{MRR} = \frac{1}{\lvert Q \rvert} \sum_{q \in Q} \frac{1}{\operatorname{rang}_q}
$$

**Correction par rapport à l'image.** L'image écrit « Σ_q q × 1/rang q » : le « q » placé avant la fraction est en trop.

## Éléments

$$
Q
$$

**Q** : l'ensemble des requêtes évaluées ; |Q| est leur nombre.

$$
\operatorname{rang}_q
$$

**rang_q** : la position du premier document pertinent pour la requête q, à partir de 1.

$$
\frac{1}{\operatorname{rang}_q}
$$

**1 / rang_q** : vaut 1 si le premier résultat est bon, 1/2 s'il est deuxième. Si aucun pertinent n'est trouvé, ce terme vaut 0.

## Ce que c'est

Le MRR est la moyenne des inverses de rang. Il récompense un bon passage placé tout en haut.

## Effets et impacts

- C'est la bonne métrique quand l'agent n'utilise vraiment que le premier passage utile.
- Un MRR de 1 veut dire : le meilleur est toujours en tête.
- Il ignore les autres bons passages plus bas, contrairement au rappel (fiche 13).

## Exemple chiffré

Quatre requêtes. Premier passage pertinent aux rangs 1, 2 et 4, et aucun pour la dernière :

$$
\operatorname{MRR} = \frac{1}{4}\left(1 + \frac{1}{2} + \frac{1}{4} + 0\right) = \frac{1{,}75}{4} = 0{,}4375
$$

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`rang_reciproque(rang)`** — Cette fonction ressemble à un guichetier qui ne s'intéresse qu'à une seule question, à quelle place se trouvait le premier bon passage : elle reçoit ce rang, compté à partir de 1, ou `None` quand la recherche n'a rien rapporté de pertinent, et dans ce dernier cas elle renvoie tout de suite 0. Si on lui tend un rang inférieur à 1, place qui n'existe pas, elle refuse le ticket et lève une `ValueError` avec le message « un rang commence à 1 », pour qu'une erreur de numérotation ne se déguise jamais en simple absence ; sinon elle renvoie l'inverse du rang, 1 pour la tête de liste, 0,5 pour la deuxième place, 0,25 pour la quatrième.

**`mrr(rangs)`** — Celle-ci est le comptable de fin de journée qui réunit tous les tickets : elle reçoit la liste des rangs, un par requête évaluée, fait passer chacun par `rang_reciproque`, additionne les inverses obtenus et divise ce total par le nombre de requêtes, ce qui donne la moyenne des rangs réciproques, un nombre entre 0 et 1. Elle renvoie 0,4375 pour les rangs 1, 2, 4 et une requête sans réponse, 1 quand le bon passage est toujours en tête et 0 quand il n'est jamais trouvé ; une liste vide la ferait diviser par zéro, car elle ne prévoit pas ce cas.

**`main()`** — C'est le contrôleur qui rejoue l'exemple de la fiche : il demande à `mrr` la valeur pour quatre requêtes dont le premier passage pertinent tombe aux rangs 1, 2 et 4, la dernière restant bredouille, imprime le résultat, puis vérifie par un seul `assert` qu'il vaut exactement 0,4375, c'est-à-dire 1,75 divisé par 4. Le même `assert` contrôle les deux bornes, trois requêtes toujours servies en tête qui doivent donner 1 et deux requêtes sans aucun résultat qui doivent donner 0, avant que la ligne de succès ne s'affiche.

```python
"""Fiche 33 — MRR : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def rang_reciproque(rang: int | None) -> float:
    """1 / rang si un passage pertinent est trouvé (rang à partir de 1), 0 sinon."""
    if rang is None:
        return 0.0
    if rang < 1:
        raise ValueError("un rang commence à 1")
    return 1.0 / rang


def mrr(rangs: list[int | None]) -> float:
    """MRR = (1/|Q|) Σ_q 1 / rang_q."""
    return sum(rang_reciproque(r) for r in rangs) / len(rangs)


def main() -> None:
    valeur = mrr([1, 2, 4, None])
    print(f"rangs 1, 2, 4 et aucun : MRR = {valeur}")
    assert valeur == 0.4375 and mrr([1, 1, 1]) == 1.0 and mrr([None, None]) == 0.0
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
rangs 1, 2, 4 et aucun : MRR = 0.4375
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`rang_reciproque` transforme le rang du premier passage pertinent d'une question en un nombre entre 0 et 1 : 1 si ce passage est en tête, 1/2 s'il est deuxième, 1/4 s'il est quatrième, et 0 si aucun passage pertinent n'a été trouvé. L'absence de résultat est codée par `None` plutôt que par un rang 0, qui n'existe pas, et la fonction refuse tout rang inférieur à 1 pour ne pas mélanger une erreur de numérotation avec une absence. `mrr` fait la moyenne de ces rangs réciproques sur toutes les questions évaluées.

`main` vérifie l'exemple de la fiche : quatre questions dont le premier passage pertinent est au rang 1, 2 et 4, et une dernière sans passage pertinent, donnent (1 + 0,5 + 0,25 + 0) / 4 = 0,4375. Il vérifie aussi les deux bornes : 1 quand le meilleur passage est toujours en tête, 0 quand rien n'est jamais trouvé.

## Squelette algorithmique

```text
ALGORITHME MRR
ENTRÉES : pour chaque question q : le classement renvoyé et l'ensemble de ses passages pertinents
SORTIE  : le MRR du système

  somme ← 0
  POUR CHAQUE question q FAIRE
      rang ← position du premier passage pertinent dans le classement, ou « aucun »
      somme ← somme + (1 / rang SI rang existe SINON 0)
  FIN POUR
  RETOURNER somme / nombre de questions
```

**Complexité.** Trouver le premier pertinent coûte au plus la longueur du classement et s'arrête dès qu'il est trouvé ; le total est O(|Q| × longueur) au pire, puis O(1) pour la moyenne.

**Du squelette au code.** La ligne de la somme est `rang_reciproque`, et la moyenne est `mrr`.

## Dans le cours

- [Étape 27 — MRR](<../../05-RAG/27-RAG-Formule-MRR.md>)
- [Étape 28 bis — Théorèmes du cosinus et des métriques de classement](<../../05-RAG/28b-Theoremes-Cosinus-et-Metriques-de-Classement.md>)
