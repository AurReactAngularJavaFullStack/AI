# Fiche 06 — Entropie croisée

> Image : `06_entropie_croisee.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 52 — Perplexité](<../../10-Evaluation/52-Perplexite-LLM.md>)

**La perte qui entraîne le prochain token**

## Formule

$$
L = -\sum_{i} y_i \log(p_i)
$$

## Éléments

$$
y_i
$$

**yᵢ** : la cible, souvent 1 pour le bon token et 0 pour tous les autres (vecteur one-hot).

$$
p_i
$$

**pᵢ** : la probabilité prédite pour la classe i, en sortie de softmax.

$$
\log
$$

**log** : le logarithme (en pratique le logarithme naturel ln ; l'unité est alors le nat).

$$
L \ge 0
$$

**L** : la perte. Elle est toujours positive ou nulle si p est une probabilité, car log p ≤ 0.

## Ce que c'est

Elle pénalise une faible probabilité mise sur la bonne réponse. Si y est one-hot, la somme n'a qu'un terme non nul, et L se réduit à −log(p du bon token).

## Effets et impacts

- C'est la perte standard des LLM et des classifieurs.
- Une perte basse veut dire que le bon token était probable, pas qu'il est vrai dans le monde.
- Avec une softmax en sortie, le gradient par rapport aux logits vaut p − y : le modèle pousse la probabilité vers la cible.
- La perplexité (fiche 32) est l'exponentielle de l'entropie croisée moyenne.

## Exemple chiffré

Le bon token reçoit 0,7, puis 0,1 :

$$
L = -\ln 0{,}7 \approx 0{,}357 \qquad\qquad L = -\ln 0{,}1 \approx 2{,}303
$$

Gradient, pour p = (0,7 ; 0,2 ; 0,1) et y = (1 ; 0 ; 0) :

$$
p - y = (-0{,}3\ ;\ 0{,}2\ ;\ 0{,}1)
$$

Le logit du bon token monte (gradient négatif, on descend à l'opposé), ceux des autres baissent.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`entropie_croisee(y, p)`** — Cette fonction est le bookmaker qui présente l'addition à un parieur : plus celui-ci a misé peu sur le cheval qui a réellement gagné, plus la note est salée, et elle devient infinie s'il n'a rien misé du tout. Elle reçoit la distribution cible y et la distribution prédite p, lève `ValueError` si une classe de cible positive a reçu une probabilité nulle ou négative, puis additionne yᵢ × ln pᵢ sur les seules classes de cible non nulle et change le signe. Elle rend la perte L : −ln 0,7 ≈ 0,357 quand le bon token avait reçu 0,7, et −ln 0,1 ≈ 2,303 quand il n'avait reçu que 0,1.

**`gradient_logits(y, p)`** — Celle-ci est le conseil que le bookmaker glisse au parieur pour la course suivante : misez davantage sur le gagnant, moins sur les autres. Elle reçoit la cible y et la prédiction p d'une sortie softmax et rend, coordonnée par coordonnée, la différence pᵢ − yᵢ, la dérivée de la perte par rapport aux logits. Pour p = (0,7 ; 0,2 ; 0,1) et y = (1 ; 0 ; 0), elle rend (−0,3 ; 0,2 ; 0,1) : le signe négatif du bon token indique que la descente de gradient fera monter son logit.

**`main()`** — C'est le contrôleur des jeux qui vérifie trois additions et un conseil. Il ne reçoit rien ; il calcule la perte d'une prédiction à deux classes où le bon token reçoit 0,7, 0,1 puis 0,9, imprime 0,357, 2,303 et 0,105 et les vérifie par `assert`, puis calcule le gradient (−0,3 ; 0,2 ; 0,1) et le contrôle de même. Un dernier `assert` vérifie qu'une prédiction parfaite, 1 sur le bon token, donne une perte nulle ; il ne rend rien.

```python
"""Fiches 06, 06a, 06b — entropie croisée : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def entropie_croisee(y: list[float], p: list[float]) -> float:
    """L = −Σ yᵢ ln pᵢ ; les termes où yᵢ = 0 ne comptent pas."""
    if any(pi <= 0 for pi, yi in zip(p, y) if yi > 0):
        raise ValueError("une probabilité nulle sur une cible : perte infinie")
    return -sum(yi * math.log(pi) for yi, pi in zip(y, p) if yi > 0)


def gradient_logits(y: list[float], p: list[float]) -> list[float]:
    """Avec une softmax en sortie, ∂L/∂zᵢ = pᵢ − yᵢ."""
    return [pi - yi for pi, yi in zip(p, y)]


def main() -> None:
    l07, l01, l09 = (entropie_croisee([1, 0], [q, 1 - q]) for q in (0.7, 0.1, 0.9))
    print(f"p(bon token) = 0,7 : L = {l07:.3f}   0,1 : L = {l01:.3f}   0,9 : L = {l09:.3f}")
    assert round(l07, 3) == 0.357 and round(l01, 2) == 2.30 and round(l09, 3) == 0.105
    g = gradient_logits([1, 0, 0], [0.7, 0.2, 0.1])
    print("gradient p − y :", [round(x, 1) for x in g])
    assert [round(x, 1) for x in g] == [-0.3, 0.2, 0.1]
    assert entropie_croisee([1, 0], [1.0, 0.0]) == 0                # prédiction parfaite : perte nulle
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
p(bon token) = 0,7 : L = 0.357   0,1 : L = 2.303   0,9 : L = 0.105
gradient p − y : [-0.3, 0.2, 0.1]
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`entropie_croisee` additionne, pour chaque classe dont la cible est non nulle, la cible multipliée par le logarithme de la probabilité prédite, et change le signe du total. Comme la cible est le plus souvent « one-hot », un seul terme reste : la perte vaut −ln de la probabilité donnée au bon token. La fonction refuse le cas où la cible est positive alors que la probabilité prédite vaut zéro, parce que ln 0 est −∞ et que la perte serait infinie ; elle ignore en revanche les classes de cible nulle, qui ne contribuent pas à la somme.

`gradient_logits` donne la dérivée de cette perte par rapport aux logits quand la sortie passe par une softmax : chaque coordonnée vaut pᵢ − yᵢ. Le bon token reçoit un gradient négatif, donc la descente de gradient augmente son logit, et les autres tokens reçoivent un gradient positif, donc leurs logits baissent.

`main` vérifie les nombres des trois fiches : une probabilité de 0,7 sur le bon token coûte 0,357, une probabilité de 0,1 coûte 2,30 et une probabilité de 0,9 coûte 0,105, soit une perte environ 22 fois plus faible qu'à 0,1 (2,303 / 0,105 ≈ 21,9). Il vérifie aussi le gradient (−0,3 ; 0,2 ; 0,1) et qu'une prédiction parfaite donne une perte nulle.

## Squelette algorithmique

```text
ALGORITHME EntropieCroiséeEtGradient
ENTRÉES : logits z₁ … z_n, indice c du bon token
SORTIE  : la perte L et le gradient g par rapport aux logits

  p ← Softmax(z)
  L ← −ln p_c
  POUR i DE 1 À n FAIRE
      gᵢ ← pᵢ − 1 SI i = c SINON pᵢ
  FIN POUR
  RETOURNER L, g

ENTRAÎNEMENT : moyenne de L sur tous les tokens d'un lot, puis un pas de descente de gradient.
```

**Complexité.** O(n) pour la softmax, O(1) pour la perte et O(n) pour le gradient, où n est la taille du vocabulaire. Le gradient a une forme si simple qu'on ne calcule jamais le jacobien de la softmax, qui coûterait O(n²).

**Du squelette au code.** La ligne de la perte correspond à `entropie_croisee` avec une cible one-hot, et la boucle du gradient à `gradient_logits`.

## Dans le cours

- [Étape 52 — Perplexité](<../../10-Evaluation/52-Perplexite-LLM.md>)
- [Étape 73 — Descente de gradient et LoRA](<../../12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md>)
- [Étape 78 — Synthèse : les mathématiques de l'IA agentique](<../../14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md>)
