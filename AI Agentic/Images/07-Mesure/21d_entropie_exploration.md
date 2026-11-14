# Fiche 21d_entropie_exploration — Entropie d'une politique

> Image : `21d_entropie_exploration.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 52 — Perplexité](<../../10-Evaluation/52-Perplexite-LLM.md>)

**Rester capable d'essayer autre chose**

## Ce que montre l'image

Affiche « Entropie pour l'exploration dans les agents IA ». La formule appliquée à une politique, H(π), décomposée terme à terme. L'effet clé : en apprentissage par renforcement, on ajoute λ H(π) à l'objectif (λ > 0) pour récompenser une politique qui garde un peu d'incertitude, ce qui l'empêche de se figer trop tôt sur une seule action. En bas, une courbe : l'entropie de la politique baisse au fil de l'apprentissage.

**Ce que l'image ajoute :** l'objectif régularisé, que l'affiche note L mais qu'il faut **maximiser** (récompense plus bonus d'entropie), à l'inverse d'une perte.

## Formule

$$
H(\pi) = -\sum_a \pi(a \mid s)\, \log \pi(a \mid s)
$$

## Éléments

$$
H(\pi(\cdot \mid s))
$$

**H(π)** : l'entropie de la politique dans l'état s.

$$
\pi(a \mid s)
$$

**π(a | s) (pi)** : la probabilité de l'action a.

$$
\sum_{a}
$$

**La somme** porte sur les actions possibles.

Une politique qui joue toujours la même action a H = 0. Une politique uniforme a l'entropie la plus haute.

L'affiche ajoute un bonus dans l'objectif :

$$
L = \mathbb{E}\!\left[\sum_t R_t\right] + \lambda H(\pi), \qquad \lambda > 0
$$

## Ce que c'est

On mesure l'incertitude de la politique, puis on la récompense un peu. L'agent est pénalisé s'il devient trop déterministe trop tôt.

## Effets et impacts

- λ trop grand : l'agent explore et n'exploite plus.
- λ = 0 : on retrouve le retour seul, et le risque de figer une mauvaise action.
- H(π) n'est pas l'incertitude sur les faits. C'est l'incertitude sur le choix d'action.

## Exemple chiffré

Deux actions, π = (0,9, 0,1), logarithme naturel.

$$
H = -0{,}9 \ln 0{,}9 - 0{,}1 \ln 0{,}1 \approx 0{,}325
$$

La loi équiprobable (0,5, 0,5) vaut ln 2 ≈ 0,693. La politique à 0,9 est déjà assez sûre d'elle.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`entropie(p)`** — Cette fonction est l'explorateur qui mesure, avant chaque départ, à quel point il est encore prêt à prendre un chemin qu'il ne connaît pas : elle reçoit les probabilités π(a | s) des actions de la politique, vérifie qu'elles sont positives et que leur somme vaut 1, et lève une `ValueError` si ce n'est pas le cas, puis ajoute π(a) × ln π(a) pour chaque action jouable, les actions de probabilité nulle ne comptant pas. Elle renvoie l'opposé de cette somme, l'entropie H(π) en nats, qui vaut 0 pour une politique figée sur une seule action et grandit à mesure que les choix restent ouverts : 0,325 pour π = (0,9 ; 0,1), contre ln 2 ≈ 0,693 pour une politique qui hésite à parts égales ; c'est cette quantité que l'objectif récompense par le bonus λ H(π).

**`main()`** — C'est le carnet de route qui relève l'esprit d'aventure de toutes les distributions de la famille : il vérifie d'abord les trois cas de la fiche 21, ln 2, 0,325 et ln 4, puis les deux dés des fiches 21a à 21c, 1,792 nat pour le dé équitable et une entropie nulle, imprimée `-0.0`, pour le dé pipé. Il en vient ensuite à la politique de cette fiche, imprime son entropie 0,325 à côté de ln 2 = 0,693, vérifie par un `assert` que la politique sûre d'elle est bien moins incertaine que la politique uniforme, et imprime la ligne de succès.

```python
"""Fiches 21, 21a à 21d — entropie : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def entropie(p: list[float]) -> float:
    """H(P) = −Σ pᵢ ln pᵢ, en nats ; convention 0 ln 0 = 0."""
    if not math.isclose(sum(p), 1) or any(x < 0 for x in p):
        raise ValueError("P doit être une distribution")
    return -sum(x * math.log(x) for x in p if x > 0)


def main() -> None:
    h2, h91, h4 = entropie([0.5, 0.5]), entropie([0.9, 0.1]), entropie([0.25] * 4)
    print(f"(½, ½) : {h2:.3f}   (0,9 ; 0,1) : {h91:.3f}   uniforme sur 4 : {h4:.3f}")
    assert math.isclose(h2, math.log(2)) and round(h91, 3) == 0.325 and math.isclose(h4, math.log(4))
    de, pipe = entropie([1 / 6] * 6), entropie([0, 0, 0, 0, 0, 1])          # fiches 21a à 21c
    print(f"dé équitable : {de:.3f} nat   dé pipé : {pipe}")
    assert round(de, 3) == 1.792 and pipe == 0
    print(f"fiche 21d : politique (0,9 ; 0,1) : {entropie([0.9, 0.1]):.3f} < ln 2 = {math.log(2):.3f}")
    assert entropie([0.9, 0.1]) < entropie([0.5, 0.5])
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
(½, ½) : 0.693   (0,9 ; 0,1) : 0.325   uniforme sur 4 : 1.386
dé équitable : 1.792 nat   dé pipé : -0.0
fiche 21d : politique (0,9 ; 0,1) : 0.325 < ln 2 = 0.693
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`entropie` vérifie que la liste reçue est une distribution (positive, de somme 1), puis additionne pᵢ × ln pᵢ sur les cas de probabilité non nulle et change le signe du total. Ignorer les cas de probabilité nulle applique la convention 0 ln 0 = 0, qui est la limite de p ln p quand p tend vers 0 ; sans elle, `math.log(0)` lèverait une erreur. Comme chaque ln pᵢ est négatif ou nul, le signe moins rend l'entropie positive ou nulle, et l'unité est le nat parce qu'on utilise le logarithme naturel.

`main` vérifie les exemples de toute la famille : deux cas équiprobables valent ln 2 ≈ 0,693, la distribution (0,9 ; 0,1) seulement 0,325, et quatre cas équiprobables ln 4 ≈ 1,386. Les fiches 21a à 21c comparent deux dés : le dé équitable vaut ln 6 ≈ 1,792 nat, le dé pipé qui tombe toujours sur 6 vaut 0, aucune surprise. La fiche 21d applique la même formule à une politique : jouer la première action 9 fois sur 10 donne 0,325, moins que les 0,693 d'une politique qui hésite, ce qui sert de bonus d'exploration dans l'objectif d'apprentissage.

## Squelette algorithmique

```text
ALGORITHME Entropie
ENTRÉE  : distribution p₁ … p_n
SORTIE  : H ≥ 0, au plus ln n

  H ← 0
  POUR i DE 1 À n FAIRE
      SI pᵢ > 0 ALORS H ← H − pᵢ × ln pᵢ
  FIN POUR
  RETOURNER H

USAGE (fiche 21d) : objectif d'une politique ← retour moyen + λ × H(π(· | s)), pour ne pas s'enfermer trop tôt dans une action.
```

**Complexité.** Une passe sur les n cas : O(n). Pour un modèle de langage, l'entropie du prochain token se calcule à partir de la softmax, donc en O(|V|) par position.

**Du squelette au code.** La boucle et son test sont la somme `sum(x * math.log(x) for x in p if x > 0)` de `entropie`, précédée de la vérification que P est une distribution.

## Dans le cours

- [Étape 52 — Perplexité](<../../10-Evaluation/52-Perplexite-LLM.md>)
- [Fiche 21 — Entropie](<21_entropie.md>)
- [Fiche 19 — REINFORCE](<../06-Decision/19_reinforce.md>)
