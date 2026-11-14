# Fiche 13 — Rappel

> Image : `13_rappel.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 25 — Recall@k](<../../05-RAG/25-RAG-Formule-Recall-at-k.md>)

**Parmi ce qui est juste, quelle part est retrouvée**

## Formule

$$
\text{Rappel} = \frac{VP}{VP + FN}
$$

## Éléments

$$
VP
$$

**VP** : les vrais positifs, éléments justes retrouvés.

$$
FN
$$

**FN** : les faux négatifs, éléments justes manqués.

$$
VP + FN
$$

**Le dénominateur** : tous les éléments vraiment pertinents.

## Ce que c'est

Le rappel mesure la couverture. Il ne dit pas si les résultats renvoyés sont propres : c'est le rôle de la précision (fiche 12).

## Effets et impacts

- Un rappel bas fait répondre l'agent sans la preuve utile.
- Monter le top-k augmente souvent le rappel et baisse la précision.
- Un rappel de 1 obtenu en renvoyant tout est inutile : le contexte est noyé.

## Exemple chiffré

10 passages sont pertinents pour la question. Le top-10 en contient 7 :

$$
\text{Rappel} = \frac{7}{7 + 3} = 0{,}7
$$

Les 3 passages manqués n'arriveront jamais au modèle : il répondra sans eux.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`comptes(renvoyes, pertinents)`** — Cette fonction est le commissaire qui confronte la liste des personnes interpellées à la liste des suspects recherchés : il compte les bons coups de filet, les innocents arrêtés par erreur et les suspects toujours en fuite. Elle reçoit l'ensemble des passages renvoyés et celui des passages pertinents, et rend (VP, FP, FN), c'est-à-dire la taille de l'intersection, celle des renvoyés hors sujet et celle des pertinents manqués. Avec un top-10 qui contient 7 des 10 passages pertinents, elle rend (7, 3, 3).

**`precision(vp, fp)`** — Celle-ci mesure la justesse des interpellations : parmi les personnes arrêtées, combien étaient vraiment recherchées ? Elle reçoit VP et FP, rend VP / (VP + FP), ou `None` si personne n'a été arrêté, puisque la question n'a alors pas de sens. Sur l'exemple, elle rend 0,7 ; elle sert ici de contrepoint au rappel, car un commissaire très prudent peut afficher une précision parfaite tout en laissant filer la plupart des suspects.

**`rappel(vp, fn)`** — Celle-ci est la question qui hante le commissaire : sur tous les suspects recherchés, combien sont derrière les barreaux ? Elle reçoit les vrais positifs et les faux négatifs, et rend VP / (VP + FN), ou `None` s'il n'y avait aucun suspect à trouver. Pour les 10 passages pertinents dont 7 seulement figurent dans le top-10, elle rend 7 / (7 + 3) = 0,7 : les 3 passages manqués n'arriveront jamais au modèle, qui répondra sans eux.

**`f1(p, r)`** — Celle-ci est le rapport de fin d'enquête, qui résume en un seul chiffre la justesse et l'exhaustivité par leur moyenne harmonique. Elle reçoit une précision et un rappel, rend `None` si l'un des deux manque, 0,0 si leur somme est nulle, et sinon 2pr / (p + r). Elle rend 0,7 pour l'exemple de cette fiche, 0,0198 pour un système parfaitement précis mais qui ne retrouve que 1 % des pertinents, et 0,643 pour (0,9 ; 0,5) comme pour (0,5 ; 0,9).

**`main()`** — C'est l'inspection générale qui refait les comptes de l'enquête. Il ne reçoit rien ; il construit 10 passages renvoyés et un ensemble pertinent de 10 passages, dont 7 communs et 3 manqués, appelle les quatre fonctions, imprime VP = 7, FP = 3, FN = 3, une précision, un rappel et une F1 de 0,7, puis les vérifie par `assert`. Il contrôle ensuite les F1 de 0,0198 et 0,643, leur symétrie et leur encadrement, puis les cas indéfinis, qui doivent rendre `None`, et les vrais échecs, qui doivent rendre 0,0 ; il ne rend rien.

```python
"""Fiches 12, 13, 14 — précision, rappel et F1 : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def comptes(renvoyes: set[str], pertinents: set[str]) -> tuple[int, int, int]:
    """VP = renvoyés et pertinents ; FP = renvoyés non pertinents ; FN = pertinents non renvoyés."""
    return len(renvoyes & pertinents), len(renvoyes - pertinents), len(pertinents - renvoyes)


def precision(vp: int, fp: int) -> float | None:
    """VP / (VP + FP) ; None si rien n'est renvoyé : la métrique n'est pas définie."""
    return vp / (vp + fp) if vp + fp else None


def rappel(vp: int, fn: int) -> float | None:
    """VP / (VP + FN) ; None s'il n'y a rien de pertinent : la métrique n'est pas définie."""
    return vp / (vp + fn) if vp + fn else None


def f1(p: float | None, r: float | None) -> float | None:
    if p is None or r is None:
        return None
    return 2 * p * r / (p + r) if p + r else 0.0


def main() -> None:
    renvoyes = {f"d{i}" for i in range(10)}                        # 10 passages renvoyés
    pertinents = {f"d{i}" for i in range(7)} | {"x1", "x2", "x3"}   # 7 d'entre eux + 3 manqués
    vp, fp, fn = comptes(renvoyes, pertinents)
    p, r = precision(vp, fp), rappel(vp, fn)
    print(f"VP = {vp}, FP = {fp}, FN = {fn}   précision = {p}   rappel = {r}   F1 = {f1(p, r):.1f}")
    assert (vp, fp, fn) == (7, 3, 3) and p == 0.7 and r == 0.7
    print(f"P = 1, R = 0,01 : F1 = {f1(1, 0.01):.4f}   P = 0,9, R = 0,5 : F1 = {f1(0.9, 0.5):.3f} = {f1(0.5, 0.9):.3f}")
    assert round(f1(1, 0.01), 4) == 0.0198 and math.isclose(f1(0.9, 0.5), f1(0.5, 0.9))
    assert min(0.9, 0.5) <= f1(0.9, 0.5) <= (0.9 + 0.5) / 2
    assert precision(0, 0) is None and rappel(0, 0) is None and f1(None, 0.5) is None   # indéfini, pas 0
    assert precision(0, 4) == 0.0 and f1(0.0, 0.0) == 0.0                                # 0 est un vrai échec
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
VP = 7, FP = 3, FN = 3   précision = 0.7   rappel = 0.7   F1 = 0.7
P = 1, R = 0,01 : F1 = 0.0198   P = 0,9, R = 0,5 : F1 = 0.643 = 0.643
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`comptes` transforme deux ensembles, les passages renvoyés et les passages pertinents, en trois nombres par des opérations d'ensembles : l'intersection donne les vrais positifs, la différence « renvoyés moins pertinents » les faux positifs, et la différence « pertinents moins renvoyés » les faux négatifs. Utiliser des ensembles garantit qu'un passage n'est compté qu'une fois. `precision` divise les vrais positifs par tout ce qui a été renvoyé, `rappel` par tout ce qui était pertinent, et toutes deux renvoient `None` quand le dénominateur est nul. C'est la convention du cours : une métrique sans dénominateur est indéfinie, ni 0 (qui accuserait un système qui n'a rien affirmé de faux) ni 1, et elle n'entre dans aucune moyenne. `f1` calcule la moyenne harmonique des deux taux ; elle renvoie `None` si l'un d'eux est indéfini, et 0 quand les deux valent 0.

`main` construit l'exemple des fiches 12 et 13 : dix passages renvoyés, dont sept pertinents, et trois passages pertinents manqués. La précision et le rappel valent tous deux 0,7, et F1 aussi. Le programme vérifie ensuite les deux leçons de la fiche 14 : un système qui ne trouve presque rien (P = 1, R = 0,01) obtient un F1 de 0,0198, et deux systèmes aux défauts opposés (P = 0,9 et R = 0,5, ou l'inverse) obtiennent le même F1, qui reste toujours entre le plus petit des deux taux et leur moyenne.

## Squelette algorithmique

```text
ALGORITHME ÉvaluerUnRésultat
ENTRÉES : ensemble R des éléments renvoyés, ensemble P des éléments pertinents
SORTIE  : précision, rappel, F1

  VP ← |R ∩ P|      FP ← |R \ P|      FN ← |P \ R|
  précision ← VP / (VP + FP)        (indéfinie si rien n'est renvoyé)
  rappel    ← VP / (VP + FN)        (indéfini s'il n'y a rien de pertinent)
  F1        ← 2 × précision × rappel / (précision + rappel)     (indéfini si un taux l'est, 0 si les deux sont nuls)
  RETOURNER précision, rappel, F1
```

**Complexité.** Avec des ensembles par hachage, les intersections et différences coûtent O(|R| + |P|) en moyenne ; les trois taux coûtent ensuite O(1). Sur un jeu de Q questions, on répète ce calcul Q fois, puis on fait la moyenne.

**Du squelette au code.** La première ligne est `comptes`, et les trois suivantes sont `precision`, `rappel` et `f1`.

## Dans le cours

- [Étape 25 — Recall@k](<../../05-RAG/25-RAG-Formule-Recall-at-k.md>)
- [Étape 50 — Précision, rappel, F1 et KL](<../../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>)
- [Étape 56 — Precision, Recall, F1 en évaluation](<../../10-Evaluation/56-Evaluation-Formule-Precision-Recall-F1.md>)
