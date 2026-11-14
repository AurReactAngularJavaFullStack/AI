# Fiche 31 — Adam

> Image : `31_adam.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 74 — Optimiseur Adam](<../../12-Production-Couts-Optimisation/74-Optimiseur-Adam.md>)

**Un pas adapté à chaque paramètre**

## Formule

$$
\theta_{t+1} = \theta_t - \frac{\alpha \times \hat{m}_t}{\sqrt{\hat{v}_t} + \varepsilon}
$$

## Éléments

$$
\theta_t
$$

**θₜ** : les paramètres à l'étape t.

$$
\alpha
$$

**α (alpha)** : le taux d'apprentissage.

$$
\hat{m}_t
$$

**m̂ₜ** : la moyenne corrigée des gradients, la direction.

$$
\hat{v}_t
$$

**v̂ₜ** : la moyenne corrigée des gradients au carré, l'ampleur.

$$
\varepsilon \approx 10^{-8}
$$

**ε (epsilon)** : un petit nombre pour ne pas diviser par zéro.

## Ce que c'est

Adam divise la direction moyenne du gradient par son ampleur. Un gradient énorme et un gradient minuscule font des pas de longueur comparable.

## Effets et impacts

- C'est l'optimiseur usuel du fine-tuning.
- Un batch aberrant gonfle v̂ longtemps et rapetisse les pas suivants.
- AdamW applique le weight decay à part, après le pas. Sinon, la division par √v̂ l'affaiblit, et les grands poids cessent de rétrécir en proportion d'eux-mêmes.

## Exemple chiffré

Premier pas, β₁ = 0,9 et β₂ = 0,999 (les coefficients des moyennes). Avec un gradient g = 2 :

$$
m_1 = 0{,}1 \times 2 = 0{,}2, \quad v_1 = 0{,}001 \times 4 = 0{,}004, \quad \hat{m}_1 = \frac{0{,}2}{0{,}1} = 2, \quad \hat{v}_1 = \frac{0{,}004}{0{,}001} = 4
$$

$$
\text{pas} = \alpha \times \frac{2}{\sqrt{4}} = \alpha
$$

Avec un gradient g = 0,001, on trouve m̂₁ = 0,001 et √v̂₁ = 0,001 : le pas vaut encore α. Les deux paramètres avancent pareil, malgré un gradient 2 000 fois plus petit.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`adam(gradients, alpha, b1, b2, eps)`** — Cette fonction est un ingénieur du son qui règle le volume d'un micro en écoutant à la fois la direction moyenne des derniers sons et leur puissance moyenne, pour que le chuchoteur et le crieur sortent des haut-parleurs à la même intensité : elle reçoit la suite des gradients d'un même paramètre, le taux α, qui vaut 0,001 par défaut, les coefficients β₁ = 0,9 et β₂ = 0,999 des deux moyennes mobiles et le petit ε = 10⁻⁸. À chaque étape t, elle met à jour m, la moyenne mobile des gradients, et v, celle de leurs carrés, corrige le biais vers zéro des premiers pas en divisant par 1 − β₁ᵗ et 1 − β₂ᵗ, puis calcule le pas α × m̂ / (√v̂ + ε) ; elle renvoie la liste de ces pas, que l'on retrancherait à θ, et non la suite des θ eux-mêmes.

**`main()`** — C'est la balance d'essai qui compare deux voix opposées puis simule un cri soudain : il demande à `adam` le premier pas pour un gradient de 2 et pour un gradient de 0,001, imprime 0,001000 dans les deux cas et vérifie par un `assert` que tous deux valent α = 0,001, malgré un rapport de 2 000 entre les gradients. Il fait ensuite passer une suite de cinq gradients égaux à 1, un gradient aberrant de 100, puis cinq gradients de 1, imprime le pas d'avant le choc, 0,001000, et celui d'après, 0,000478, et vérifie que le second est plus petit, car v̂ a gonflé, avant d'imprimer la ligne de succès.

```python
"""Fiche 31 — Adam : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def adam(gradients: list[float], alpha: float = 0.001, b1: float = 0.9, b2: float = 0.999, eps: float = 1e-8) -> list[float]:
    """Renvoie les pas successifs α m̂ₜ / (√v̂ₜ + ε) pour une suite de gradients d'un même paramètre."""
    m = v = 0.0
    pas = []
    for t, g in enumerate(gradients, start=1):
        m = b1 * m + (1 - b1) * g              # moyenne mobile des gradients : la direction
        v = b2 * v + (1 - b2) * g * g          # moyenne mobile des carrés : l'ampleur
        m_hat = m / (1 - b1 ** t)              # corrections du biais vers 0 des premières étapes
        v_hat = v / (1 - b2 ** t)
        pas.append(alpha * m_hat / (math.sqrt(v_hat) + eps))
    return pas


def main() -> None:
    gros, petit = adam([2.0])[0], adam([0.001])[0]
    print(f"premier pas : gradient 2 -> {gros:.6f}   gradient 0,001 -> {petit:.6f}   (α = 0,001)")
    assert math.isclose(gros, 0.001, rel_tol=1e-6) and math.isclose(petit, 0.001, rel_tol=1e-4)
    apres_choc = adam([1.0] * 5 + [100.0] + [1.0] * 5)
    print(f"pas avant le choc : {apres_choc[4]:.6f}   juste après : {apres_choc[6]:.6f}")
    assert apres_choc[6] < apres_choc[4]                  # un gradient aberrant gonfle v̂ et rapetisse les pas suivants
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
premier pas : gradient 2 -> 0.001000   gradient 0,001 -> 0.001000   (α = 0,001)
pas avant le choc : 0.001000   juste après : 0.000478
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`adam` suit un seul paramètre à travers une suite de gradients. À chaque étape, elle met à jour deux moyennes mobiles : m, la moyenne des gradients, qui donne la direction, et v, la moyenne des gradients au carré, qui mesure leur ampleur. Ces deux moyennes partent de zéro, ce qui les tire vers zéro aux premières étapes ; les lignes `m_hat` et `v_hat` corrigent ce biais en divisant par 1 − β puissance t. Le pas vaut enfin α × m̂ / (√v̂ + ε), où ε évite une division par zéro.

Le cœur de la méthode est dans ce quotient : un gradient énorme et un gradient minuscule font des pas de même longueur, parce que la direction est divisée par l'ampleur. `main` le vérifie au premier pas : un gradient de 2 et un gradient de 0,001 donnent tous deux un pas d'environ α = 0,001. Le programme vérifie ensuite l'effet décrit par la fiche : après un gradient aberrant de 100 au milieu d'une suite de gradients égaux à 1, v̂ gonfle et les pas suivants deviennent plus petits qu'avant le choc.

## Squelette algorithmique

```text
ALGORITHME Adam
ENTRÉES : paramètres θ, gradient ∇L, α, β₁, β₂, ε, nombre d'étapes
SORTIE  : θ

  m ← 0 ; v ← 0                          (un m et un v par paramètre)
  POUR t DE 1 À nombre d'étapes FAIRE
      g ← ∇L(θ)
      m ← β₁ m + (1 − β₁) g
      v ← β₂ v + (1 − β₂) g²
      m̂ ← m / (1 − β₁ᵗ) ; v̂ ← v / (1 − β₂ᵗ)
      θ ← θ − α m̂ / (√v̂ + ε)
      (AdamW : θ ← θ − α λ θ, appliqué à part)
  FIN POUR
  RETOURNER θ
```

**Complexité.** O(P) par étape pour P paramètres, comme la descente de gradient, mais avec deux fois plus de mémoire : m et v pour chaque paramètre, soit 2P nombres de plus. C'est l'une des raisons du coût mémoire du fine-tuning complet.

**Du squelette au code.** Les quatre lignes centrales de la boucle sont les quatre premières lignes de la boucle de `adam`, et la mise à jour de θ correspond au pas qu'elle renvoie.

## Dans le cours

- [Étape 74 — Optimiseur Adam](<../../12-Production-Couts-Optimisation/74-Optimiseur-Adam.md>)
- [Étape 75 — Optimisation : formules](<../../12-Production-Couts-Optimisation/75-Optimisation-Formules.md>)
- [Étape 73 — Descente de gradient et LoRA](<../../12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md>)
