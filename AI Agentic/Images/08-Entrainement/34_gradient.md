# Fiche 34 — Gradient

> Image : `34_gradient.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 73 — Descente de gradient et LoRA](<../../12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md>)

**La direction de plus forte pente**

## Formule

$$
\nabla L = \left( \frac{\partial L}{\partial \theta_1},\ \frac{\partial L}{\partial \theta_2},\ \dots,\ \frac{\partial L}{\partial \theta_n} \right)
$$

## Éléments

$$
L
$$

**L** : la perte.

$$
\theta_i
$$

**θᵢ** : un paramètre.

$$
\frac{\partial L}{\partial \theta_i}
$$

**∂L/∂θᵢ** : la sensibilité de la perte à ce paramètre, sa dérivée partielle.

$$
\nabla L
$$

**∇L (nabla L)** : le vecteur de toutes ces sensibilités.

$$
n
$$

**n** : le nombre de paramètres.

## Ce que c'est

Le gradient indique dans quelle direction la perte augmente le plus vite. L'apprentissage fait un pas dans le sens opposé (fiche 08).

## Effets et impacts

- Un gradient nul : plus rien à apprendre, ou un plateau.
- Un gradient explosif rend l'entraînement instable.
- Il se calcule par la règle de la chaîne, de la perte vers les premières couches (rétropropagation).
- Le lire explique la divergence, la saturation et les couches qui n'apprennent plus.

## Exemple chiffré

Perte à deux paramètres, au point (1 ; 1) :

$$
L(\theta_1, \theta_2) = \theta_1^2 + 3\,\theta_2^2 \quad\Longrightarrow\quad \nabla L = (2\theta_1\ ;\ 6\theta_2) = (2\ ;\ 6)
$$

Un pas de 0,1 contre le gradient mène en (0,8 ; 0,4) : θ₂, plus sensible, bouge trois fois plus.

Règle de la chaîne, pour un neurone L = (w x − y)² avec w = 1, x = 2, y = 3 :

$$
\frac{\partial L}{\partial w} = 2\,(w x - y) \times x = 2 \times (2 - 3) \times 2 = -4
$$

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`gradient_numerique(L, theta, h)`** — Cette fonction est le géomètre qui, posé sur un terrain vallonné, mesure la pente en faisant un tout petit pas en avant puis un tout petit pas en arrière dans chaque direction, l'une après l'autre : elle reçoit la fonction de perte L, le point θ sous forme de liste et un écart h qui vaut 10⁻⁶ par défaut, puis, pour chaque coordonnée, fabrique deux copies du point, l'une décalée de +h et l'autre de −h sur cette seule coordonnée. Elle évalue la perte aux deux copies, divise la différence par 2h, ce qui donne une estimation de la dérivée partielle ∂L/∂θᵢ, et renvoie la liste de ces estimations, le gradient : environ (2 ; 6) pour θ₁² + 3θ₂² au point (1 ; 1). Elle ne sert pas à entraîner un réseau, trop lente pour cela, mais à vérifier une dérivée calculée autrement.

**`derivee_par_la_chaine(x)`** — Celle-ci est l'horloger qui démonte un mécanisme à deux engrenages et multiplie leurs rapports de transmission pour savoir de combien tourne la dernière roue quand on tourne la première : elle reçoit le nombre x, calcule l'étage intermédiaire y = 2x, puis les deux dérivées locales, dL/dy = 2y pour l'étage L = y² et dy/dx = 2 pour l'étage y = 2x. Elle renvoie leur produit, la dérivée exacte dL/dx, qui vaut 8x et donc 12 en x = 1,5 ; c'est le geste élémentaire que la rétropropagation répète couche après couche, et que les fiches 34a et 34b décrivent.

**`main()`** — C'est le contrôleur qui confronte chaque dérivée calculée à la main à la mesure du géomètre : il estime le gradient de θ₁² + 3θ₂² en (1 ; 1), fait un pas de 0,1 contre lui et vérifie par un `assert` qu'on obtient (2 ; 6) puis le point (0,8 ; 0,4), où θ₂, plus sensible, a bougé trois fois plus. Il calcule ensuite la dérivée du neurone (w x − y)² en w = 1, x = 2, y = 3, soit −4, la compare au gradient numérique, puis appelle `derivee_par_la_chaine` en x = 1,5, vérifie le résultat 12 de la même façon, et imprime la ligne de succès.

```python
"""Fiches 34, 34a, 34b — gradient et règle de la chaîne : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def gradient_numerique(L, theta: list[float], h: float = 1e-6) -> list[float]:
    """∂L/∂θᵢ ≈ (L(θ + h eᵢ) − L(θ − h eᵢ)) / 2h, coordonnée par coordonnée."""
    g = []
    for i in range(len(theta)):
        plus, moins = theta[:], theta[:]
        plus[i] += h
        moins[i] -= h
        g.append((L(plus) - L(moins)) / (2 * h))
    return g


def derivee_par_la_chaine(x: float) -> float:
    """y = 2x, L = y² : dL/dx = dL/dy × dy/dx = 2y × 2."""
    y = 2 * x
    dL_dy, dy_dx = 2 * y, 2
    return dL_dy * dy_dx


def main() -> None:
    L = lambda t: t[0] ** 2 + 3 * t[1] ** 2
    g = gradient_numerique(L, [1.0, 1.0])
    pas = [t - 0.1 * gi for t, gi in zip([1.0, 1.0], g)]
    print(f"fiche 34 : ∇L(1, 1) ≈ ({g[0]:.3f} ; {g[1]:.3f})   après un pas de 0,1 : ({pas[0]:.1f} ; {pas[1]:.1f})")
    assert round(g[0], 3) == 2 and round(g[1], 3) == 6 and [round(p, 1) for p in pas] == [0.8, 0.4]
    w, x, y = 1.0, 2.0, 3.0
    dl_dw = 2 * (w * x - y) * x
    print(f"neurone L = (wx − y)² : dL/dw = {dl_dw}")
    assert dl_dw == -4 and math.isclose(gradient_numerique(lambda t: (t[0] * x - y) ** 2, [w])[0], -4, abs_tol=1e-6)
    d = derivee_par_la_chaine(1.5)
    print(f"fiches 34a/34b : dL/dx en x = 1,5 : {d} = 8x")
    assert d == 12 and math.isclose(gradient_numerique(lambda t: (2 * t[0]) ** 2, [1.5])[0], 12, abs_tol=1e-6)
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
fiche 34 : ∇L(1, 1) ≈ (2.000 ; 6.000)   après un pas de 0,1 : (0.8 ; 0.4)
neurone L = (wx − y)² : dL/dw = -4.0
fiches 34a/34b : dL/dx en x = 1,5 : 12.0 = 8x
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`gradient_numerique` calcule chaque dérivée partielle par une différence centrée : elle augmente puis diminue une seule coordonnée d'une petite quantité h, évalue la perte dans les deux cas, et divise l'écart par 2h. Le vecteur de ces dérivées est le gradient, la direction dans laquelle la perte augmente le plus vite. Cette méthode est trop lente pour entraîner un vrai réseau, qui a des milliards de paramètres, mais elle sert à vérifier une dérivée calculée à la main ou par rétropropagation.

`derivee_par_la_chaine` calcule au contraire la dérivée de façon exacte, en suivant la règle de la chaîne des fiches 34a et 34b : y = 2x, puis L = y², donc dL/dx est le produit de dL/dy = 2y et de dy/dx = 2, soit 8x. C'est ce produit, répété couche après couche de la sortie vers l'entrée, qui constitue la rétropropagation.

`main` vérifie les trois exemples : le gradient de θ₁² + 3θ₂² au point (1, 1) vaut (2 ; 6), et un pas de 0,1 contre lui mène en (0,8 ; 0,4), le paramètre le plus sensible bougeant trois fois plus ; la dérivée du neurone (wx − y)² par rapport à w vaut −4 ; et la règle de la chaîne donne 12 en x = 1,5. Dans chaque cas, le calcul exact est comparé au gradient numérique.

## Squelette algorithmique

```text
ALGORITHME Rétropropagation (règle de la chaîne, réseau en couches)
ENTRÉES : entrée x, couches f₁ … f_K, perte L
SORTIE  : la dérivée de L par rapport à chaque paramètre

  PASSE AVANT : a₀ ← x ; POUR k DE 1 À K FAIRE aₖ ← fₖ(aₖ₋₁) FIN POUR ; calculer L(a_K)
  δ ← dL/da_K
  POUR k DE K À 1 FAIRE                                        (de la sortie vers l'entrée)
      dL/dθₖ ← δ × ∂fₖ/∂θₖ                                      (gradient des paramètres de la couche k)
      δ ← δ × ∂fₖ/∂aₖ₋₁                                        (règle de la chaîne)
  FIN POUR
  VÉRIFICATION : comparer à (L(θ + h) − L(θ − h)) / 2h sur quelques coordonnées
```

**Complexité.** La rétropropagation coûte de l'ordre de deux passes avant, quel que soit le nombre de paramètres P. Le gradient numérique coûte au contraire 2 évaluations de la perte par paramètre, soit O(P) passes avant : c'est pourquoi il ne sert qu'à vérifier.

**Du squelette au code.** La boucle de vérification est `gradient_numerique`, et un pas de la boucle arrière, sur deux couches, est `derivee_par_la_chaine`.

## Dans le cours

- [Étape 73 — Descente de gradient et LoRA](<../../12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md>)
- [Étape 75 — Optimisation : formules](<../../12-Production-Couts-Optimisation/75-Optimisation-Formules.md>)
