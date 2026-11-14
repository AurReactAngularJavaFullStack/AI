# Fiche 21b_entropie_shannon — Entropie de Shannon, affiche

> Image : `21b_entropie_shannon.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 52 — Perplexité](<../../10-Evaluation/52-Perplexite-LLM.md>)

**La formule de la surprise moyenne**

## Ce que montre l'image

Affiche « Entropie de Shannon ». La formule H(X) = −Σ p(x) log p(x), avec un ∞ parasite écrit au-dessus du Σ. L'intuition d'un dé : équilibré, entropie maximale ; pipé, entropie plus faible. Quatre usages : exploration contre exploitation, régularisation, mesure de confiance, gestion de l'incertitude.

**Ce que l'image ajoute à la fiche 21 :** l'image du dé, à transformer en calcul : un dé équilibré a une entropie de log₂ 6 ≈ 2,585 bits.

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

Affiche de la fiche 21. Shannon : l'information moyenne d'un tirage selon P.

## Effets et impacts

- Deux choix équiprobables : H = log 2.
- Elle ne détecte pas, seule, une hallucination.

## Exemple chiffré

Un dé à 6 faces équitables : H = log 6 ≈ 1,792 nat. Beaucoup de surprises.

Un dé pipé qui tombe toujours sur 6 : un seul pᵢ = 1, les autres 0, H = 0. Aucune surprise.

L'image `21a` dessine exactement ces deux dés.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`entropie(p)`** — Cette fonction est le télégraphiste de Shannon qui se demande combien de signal il faudra, en moyenne, pour transmettre le résultat d'un tirage : elle reçoit les probabilités des issues, s'assure qu'elles sont positives et totalisent 1, et lève une `ValueError` sinon, puis additionne p(x) × ln p(x) sur les seules issues possibles, la convention 0 log 0 = 0 écartant les autres. Elle renvoie l'opposé de cette somme, la surprise moyenne d'un tirage, exprimée en nats parce que le programme emploie le logarithme naturel : 1,792 pour un dé équilibré, qu'il suffirait de diviser par ln 2 pour retrouver les 2,585 bits de log₂ 6 annoncés plus haut, et 0 pour un dé pipé qui ne surprend jamais.

**`main()`** — C'est le bureau de poste où l'on chronomètre toutes les transmissions de la famille : il calcule d'abord les entropies de la fiche 21, ln 2 ≈ 0,693, 0,325 et ln 4 ≈ 1,386, et les vérifie par un `assert`, puis celles des deux dés de l'affiche, 1,792 nat pour le dé équilibré et zéro, imprimé `-0.0`, pour le dé pipé. Il vérifie enfin, pour la fiche 21d, qu'une politique qui joue sa première action neuf fois sur dix est moins incertaine qu'une politique qui hésite à parts égales, puis imprime la ligne de succès.

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
