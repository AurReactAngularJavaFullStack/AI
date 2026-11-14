# Fiche 06a_entropie_croisee_affiche — Entropie croisée, affiche

> Image : `06a_entropie_croisee_affiche.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 52 — Perplexité](<../../10-Evaluation/52-Perplexite-LLM.md>)

**La perte qui entraîne le prochain token**

## Ce que montre l'image

Affiche « Perte cross-entropy en IA agentique ». La formule H(p, q) = −Σ p(x) log q(x), avec p la distribution vraie et q la distribution prédite, et une précision utile : log est en général le logarithme naturel. Deux blocs : ce que c'est (plus p et q diffèrent, plus la perte est grande) et trois usages (prédire la bonne action ou le bon token, mieux raisonner, apprentissage supervisé).

**Défaut de l'image :** le texte du résumé, en bas, est illisible par endroits (lettres mélangées).

**Ce que l'image ajoute à la fiche 06 :** la notation p (vrai) et q (prédit), au lieu de y et p dans la fiche : même formule, autres lettres.

## Formule

$$
L = -\sum_i y_i \log p_i
$$

## Éléments

$$
y_i
$$

**yᵢ** : la cible. Souvent 1 pour le bon token, 0 sinon.

$$
p_i
$$

**pᵢ** : la probabilité prédite.

$$
\log
$$

**log** : le logarithme naturel ln (l'unité est alors le nat). Une petite probabilité sur le bon token rend L grand.

$$
L = -\log p_{\text{bon token}}
$$

**Cas one-hot** : si y vaut 1 sur le bon token et 0 ailleurs, L se réduit à −log de la probabilité du bon token.

## Ce que c'est

Affiche de la perte de la fiche 06. On pénalise une faible probabilité mise sur la bonne cible.

## Effets et impacts

- C'est la perte standard des modèles de langue.
- Le gradient par rapport aux logits (les scores avant la softmax) vaut p − y : le modèle pousse la probabilité vers la cible.

## Exemple chiffré

Le bon token reçoit p = 0,1. Les autres yᵢ valent 0.

$$
L = -\log 0{,}1 \approx 2{,}30
$$

S'il reçoit p = 0,9 :

$$
L = -\log 0{,}9 \approx 0{,}105
$$

La perte a été divisée par environ 22 (2,303 / 0,105 ≈ 21,9). Elle dit que le bon token était probable, pas qu'il est vrai dans le monde.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`entropie_croisee(y, p)`** — Cette fonction ressemble au juge d'un concours de prévision météo, qui note chaque présentateur sur la probabilité qu'il avait donnée au temps qu'il a réellement fait : avoir annoncé la pluie à 10 % un jour d'averse coûte cher, l'avoir annoncée à 90 % ne coûte presque rien. Elle reçoit la cible y et la prédiction p, lève `ValueError` si une classe réellement observée avait reçu une probabilité nulle, puis rend −Σ yᵢ ln pᵢ sur les seules classes de cible non nulle. Pour le bon token à 0,1, elle rend environ 2,303 ; à 0,9, environ 0,105, une perte divisée par près de 22.

**`gradient_logits(y, p)`** — Celle-ci est la consigne que le juge remet au présentateur pour la saison suivante : donner plus de poids au temps qui est vraiment arrivé et moins aux autres. Elle reçoit la cible et la prédiction issue d'une softmax, et rend la liste des différences pᵢ − yᵢ, la dérivée de la perte par rapport aux logits. Pour p = (0,7 ; 0,2 ; 0,1) et y = (1 ; 0 ; 0), elle rend (−0,3 ; 0,2 ; 0,1), et la descente de gradient, qui va dans le sens opposé, fait monter le logit du bon token.

**`main()`** — C'est le jury qui confirme les notes affichées. Il ne reçoit rien ; il calcule la perte quand le bon token reçoit 0,7, 0,1 puis 0,9, imprime 0,357, 2,303 et 0,105 et les vérifie par `assert`, ce qui couvre les deux valeurs de cette affiche. Il calcule ensuite le gradient pour p = (0,7 ; 0,2 ; 0,1), vérifie (−0,3 ; 0,2 ; 0,1), contrôle enfin qu'une prévision parfaite coûte zéro, puis ne rend rien.

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
- [Fiche 06 — Entropie croisée](<06_entropie_croisee.md>)
