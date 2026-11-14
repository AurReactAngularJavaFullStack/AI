# Fiche 12 — Précision

> Image : `12_precision.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 26 — Precision@k](<../../05-RAG/26-RAG-Formule-Precision-at-k.md>)

**Parmi ce qui est renvoyé, quelle part est juste**

## Formule

$$
\text{Précision} = \frac{VP}{VP + FP}
$$

## Éléments

$$
VP
$$

**VP** : les vrais positifs, résultats justes et renvoyés.

$$
FP
$$

**FP** : les faux positifs, résultats renvoyés mais faux.

$$
VP + FP
$$

**Le dénominateur** : tout ce que le système a renvoyé.

## Ce que c'est

La précision mesure la pureté des résultats. Elle ne dit pas si des éléments justes ont été oubliés : c'est le rôle du rappel (fiche 13).

## Effets et impacts

- Une précision haute donne un RAG propre, avec peu de passages hors sujet.
- Elle peut rester haute en ne renvoyant presque rien : il faut la lire avec le rappel.
- Sur un agent, des faux positifs polluent le contexte et augmentent les hallucinations.

## Exemple chiffré

Le retriever renvoie 10 passages, dont 7 pertinents :

$$
\text{Précision} = \frac{7}{7 + 3} = 0{,}7
$$

S'il n'avait renvoyé que le meilleur passage, pertinent, la précision serait de 1/1 = 1, même si 9 autres passages utiles existaient.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`comptes(renvoyes, pertinents)`** — Cette fonction est le pêcheur qui trie sa prise sur le quai : d'un côté les poissons qu'il cherchait et qu'il a remontés, de l'autre les algues ramassées pour rien, et dans un coin la liste des poissons qu'il savait présents mais qui ont filé. Elle reçoit l'ensemble des passages renvoyés et l'ensemble des passages pertinents, et rend le triplet (VP, FP, FN) : la taille de leur intersection, celle des renvoyés non pertinents et celle des pertinents non renvoyés. Pour les 10 passages renvoyés de la fiche, dont 7 pertinents, et 3 pertinents manqués, elle rend (7, 3, 3).

**`precision(vp, fp)`** — Celle-ci juge la pureté du filet : sur tout ce qui a été remonté, quelle part valait la peine ? Elle reçoit le nombre de vrais positifs et de faux positifs, et rend VP / (VP + FP), ou `None` si rien n'a été renvoyé, car une précision sans dénominateur n'est pas définie. Pour la prise de cette fiche, elle rend 7 / (7 + 3) = 0,7 ; un filet vide de bons poissons mais plein d'algues, `precision(0, 4)`, rend 0,0, un vrai échec et non une absence de mesure.

**`rappel(vp, fn)`** — Celle-ci regarde l'autre côté du quai : sur tous les poissons qu'il fallait attraper, combien sont dans la caisse ? Elle reçoit les vrais positifs et les faux négatifs, et rend VP / (VP + FN), ou `None` s'il n'y avait rien de pertinent à trouver. Sur l'exemple, elle rend 7 / (7 + 3) = 0,7 ; c'est la mesure que la précision seule ne voit pas, puisqu'un pêcheur qui ne remonte qu'un poisson, bon, a une précision de 1 et un rappel minuscule.

**`f1(p, r)`** — Celle-ci est le juge de la criée, qui donne une seule note à la pêche en combinant pureté et exhaustivité par leur moyenne harmonique. Elle reçoit une précision et un rappel, rend `None` si l'un des deux est indéfini, 0,0 si leur somme est nulle, et sinon 2pr / (p + r). Elle rend 0,7 pour p = r = 0,7, seulement 0,0198 pour une précision de 1 et un rappel de 0,01, et la même valeur 0,643 pour (0,9 ; 0,5) et (0,5 ; 0,9).

**`main()`** — C'est le contrôleur des pêches qui recompte la prise devant témoin. Il ne reçoit rien ; il fabrique 10 passages renvoyés, d0 à d9, et un ensemble pertinent formé de d0 à d6 et de trois passages manqués, appelle `comptes`, `precision` et `rappel`, imprime VP = 7, FP = 3, FN = 3, une précision et un rappel de 0,7 et une F1 de 0,7, puis vérifie ces valeurs par `assert`. Il contrôle ensuite les F1 de 0,0198 et 0,643, leur symétrie, leur place entre le minimum et la moyenne arithmétique, les cas indéfinis qui rendent `None` et les vrais zéros ; il ne rend rien.

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

- [Étape 26 — Precision@k](<../../05-RAG/26-RAG-Formule-Precision-at-k.md>)
- [Étape 50 — Précision, rappel, F1 et KL](<../../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>)
- [Étape 56 — Precision, Recall, F1 en évaluation](<../../10-Evaluation/56-Evaluation-Formule-Precision-Recall-F1.md>)
