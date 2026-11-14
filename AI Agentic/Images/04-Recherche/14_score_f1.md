# Fiche 14 — Score F1

> Image : `14_score_f1.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 50 — Précision, rappel, F1 et KL](<../../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>)

**L'équilibre entre précision et rappel**

## Formule

$$
F_1 = \frac{2 \times P \times R}{P + R}
$$

## Éléments

$$
P
$$

**P** : la précision (fiche 12).

$$
R
$$

**R** : le rappel (fiche 13).

$$
2
$$

**2** : le facteur de la moyenne harmonique.

$$
P + R
$$

**P + R** : la somme au dénominateur.

## Ce que c'est

F1 est la moyenne harmonique de P et R. Il est élevé seulement si les deux le sont. Un score extrême d'un côté et nul de l'autre donnent un F1 nul. On démontre que F1 reste toujours entre min(P, R) et la moyenne (P + R)/2 (étape 64 bis).

## Effets et impacts

- Il compare des retrievers et des classifieurs quand pureté et couverture comptent ensemble.
- Il cache le sens du compromis : deux systèmes de même F1 peuvent échouer différemment.
- Il ne remplace pas un taux de réussite de la tâche.

## Exemple chiffré

Un système très précis mais qui trouve peu de choses :

$$
P = 1,\ R = 0{,}01 \quad\Longrightarrow\quad F_1 = \frac{2 \times 1 \times 0{,}01}{1{,}01} \approx 0{,}0198
$$

Deux systèmes inverses ont le même F1 :

$$
P = 0{,}9,\ R = 0{,}5 \quad\text{et}\quad P = 0{,}5,\ R = 0{,}9 \quad\Longrightarrow\quad F_1 = \frac{0{,}9}{1{,}4} \approx 0{,}643
$$

Le premier oublie, le second bavarde : même note, défauts opposés.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`comptes(renvoyes, pertinents)`** — Cette fonction est l'assesseur d'un jury de concours qui, avant toute note, établit le relevé des faits : réponses justes données, réponses fausses données, réponses justes oubliées. Elle reçoit l'ensemble des passages renvoyés et celui des passages pertinents, et rend le triplet (VP, FP, FN) formé de la taille de leur intersection, du nombre de renvoyés non pertinents et du nombre de pertinents non renvoyés. Sur l'exemple commun aux fiches 12 à 14, 10 renvoyés dont 7 pertinents et 3 pertinents manqués, elle rend (7, 3, 3).

**`precision(vp, fp)`** — Celle-ci est la première note du jury, celle de la rigueur : sur tout ce que le candidat a affirmé, quelle part était juste ? Elle reçoit VP et FP et rend VP / (VP + FP), ou `None` si le candidat n'a rien affirmé du tout. Sur l'exemple, elle rend 0,7 ; dans cette fiche, elle fournit l'une des deux entrées de la F1, comme la précision de 1 du système qui ne trouve presque rien.

**`rappel(vp, fn)`** — Celle-ci est la seconde note, celle de la complétude : sur tout ce qu'il fallait dire, quelle part le candidat a-t-il dite ? Elle reçoit VP et FN et rend VP / (VP + FN), ou `None` s'il n'y avait rien à trouver. Sur l'exemple, elle rend 0,7 ; dans cette fiche, c'est elle qui tombe à 0,01 pour le système très précis mais avare, et qui fait chuter sa F1.

**`f1(p, r)`** — Celle-ci est le président du jury, qui refuse qu'une note excellente rachète une note désastreuse et les combine donc par leur moyenne harmonique, toujours plus proche de la plus faible. Elle reçoit la précision et le rappel, rend `None` si l'un d'eux est indéfini, 0,0 si les deux sont nuls, et sinon 2pr / (p + r). Pour P = 1 et R = 0,01, elle rend 2 × 0,01 / 1,01 ≈ 0,0198 ; pour (0,9 ; 0,5) et (0,5 ; 0,9), elle rend la même note 0,643, puisque la formule est symétrique.

**`main()`** — C'est la délibération finale, où chaque note est recalculée devant témoin. Il ne reçoit rien ; il établit le relevé de l'exemple commun, (7, 3, 3), imprime une précision, un rappel et une F1 de 0,7 et les vérifie par `assert`, puis imprime les F1 0,0198 et 0,643 de cette fiche. Il vérifie leur valeur arrondie, la symétrie entre (0,9 ; 0,5) et (0,5 ; 0,9), le fait que 0,643 se situe entre le minimum 0,5 et la moyenne arithmétique 0,7, puis les cas indéfinis et les vrais zéros ; il ne rend rien.

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

- [Étape 50 — Précision, rappel, F1 et KL](<../../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>)
- [Étape 56 — Precision, Recall, F1 en évaluation](<../../10-Evaluation/56-Evaluation-Formule-Precision-Recall-F1.md>)
- [Étape 64 bis — Théorèmes de l'évaluation](<../../10-Evaluation/64b-Theoremes-Fidelite-Pertinence-et-F1.md>)
