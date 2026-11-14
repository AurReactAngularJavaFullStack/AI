# Fiche 21a_entropie_en_images — Entropie en images

> Image : `21a_entropie_en_images.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 52 — Perplexité](<../../10-Evaluation/52-Perplexite-LLM.md>)

**Beaucoup de surprises, ou toujours la même face**

## Ce que montre l'image

Deux dés. Le dé violet peut tomber sur plein de faces : on ne sait pas trop. Le dé vert tombe toujours sur la même face : c'est sûr. Pas de formule sur le dessin. La formule de cette surprise est celle de la fiche 21.

## Formule

$$
H(P) = -\sum_i p_i \log p_i
$$

## Éléments

$$
p_i
$$

**pᵢ** : la probabilité du cas i.

$$
\log,\ \ln,\ \log_2
$$

**log** : le logarithme. Avec ln, l'unité est le nat. Avec log₂, le bit.

$$
0 \log 0 = 0
$$

**Par convention**, un cas de probabilité nulle ne compte pas. Le signe moins rend H positive.

## Ce que c'est

L'entropie mesure la dispersion d'une distribution. Elle est nulle si un seul cas est certain, maximale si tous les cas sont équiprobables.

## Effets et impacts

- Une entropie basse sur le prochain token n'est pas une réponse vraie : le modèle peut être sûr d'une erreur.
- Une entropie haute n'est pas une hallucination : il peut hésiter entre deux formulations justes.

## Exemple chiffré

Un dé à 6 faces équitables : H = log 6 ≈ 1,792 nat. Beaucoup de surprises.

Un dé pipé qui tombe toujours sur 6 : un seul pᵢ = 1, les autres 0, H = 0. Aucune surprise.

L'image `21a` dessine exactement ces deux dés.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`entropie(p)`** — Cette fonction est le forain qui, avant d'accepter un dé à son stand, veut savoir combien de surprise il réserve aux joueurs : elle reçoit la liste des probabilités des faces, vérifie qu'elles sont positives et que leur somme vaut 1, et lève une `ValueError` si ce n'est pas une vraie distribution. Elle ajoute ensuite pᵢ × ln pᵢ pour chaque face qui a une chance de sortir, en ignorant les faces impossibles selon la convention 0 log 0 = 0, puis renvoie l'opposé de cette somme, en nats puisque le logarithme est naturel : ln 6 ≈ 1,792 pour le dé violet aux six faces équitables, et 0 pour le dé vert pipé qui tombe toujours sur 6, dont les cinq faces impossibles ne comptent pas.

**`main()`** — C'est la journée d'essai au stand, où l'on lance tous les dés de la famille l'un après l'autre : il commence par les distributions de la fiche 21, ln 2, 0,325 et ln 4, qu'il vérifie par un `assert`, puis mesure les deux dés de cette image, imprime 1,792 nat pour le dé équitable et une entropie nulle pour le dé pipé, affichée `-0.0` à cause du signe moins appliqué à un total nul, et contrôle ces deux valeurs. Il finit par la politique de la fiche 21d, dont l'entropie 0,325 doit rester sous ln 2, puis imprime la ligne de succès.

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
