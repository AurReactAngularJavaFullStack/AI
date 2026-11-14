# Fiche 34a_regle_de_la_chaine — Règle de la chaîne

> Image : `34a_regle_de_la_chaine.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 73 — Descente de gradient et LoRA](<../../12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md>)

**Dériver une composition, couche après couche**

## Ce que montre l'image

Affiche « Règle de la chaîne (rétropropagation) ». La formule dL/dx = dL/dy × dy/dx, une explication (L dépend de y, qui dépend de x), un schéma x → y = f(x) → L = g(y) avec la dérivée locale sous chaque flèche, et trois usages : entraîner des réseaux profonds, apprendre des représentations, base de la rétropropagation des agents neuronaux.

**Ce que l'image ajoute à la fiche 34 :** la lecture couche par couche : L est la perte, y la sortie d'une couche, x son entrée. Le calcul complet d'un neurone est dans `Demonstrations/08-Entrainement/34_gradient.md` (démonstration 4).

## Formule

$$
\frac{\mathrm{d} L}{\mathrm{d} x} = \frac{\mathrm{d} L}{\mathrm{d} y} \times \frac{\mathrm{d} y}{\mathrm{d} x}
$$

## Éléments

$$
x
$$

**x** : l'entrée d'une couche.

$$
y = f(x)
$$

**y = f(x)** : sa sortie.

$$
L = g(y)
$$

**L = g(y)** : la perte, qui dépend de y.

$$
\frac{dL}{dy}
$$

**dL/dy** : comment la perte change si y change.

$$
\frac{dy}{dx}
$$

**dy/dx** : comment y change si x change.

$$
\frac{dL}{dx} = \frac{dL}{dy} \times \frac{dy}{dx}
$$

**Le produit enchaîne les deux.** Sur un réseau, on répète ce produit de la sortie vers l'entrée.

## Ce que c'est

La règle de la chaîne calcule la dérivée d'une composition. La rétropropagation, c'est cette règle appliquée à chaque couche, de la perte vers les premiers poids. Elle rend le gradient de la fiche 34 calculable.

## Effets et impacts

- Elle permet d'entraîner un réseau profond : on ne dérive pas la formule géante d'un coup.
- Un maillon nul (dérivée locale à 0) bloque tout le gradient en amont : la couche n'apprend plus.
- Elle ne choisit pas le pas. Le pas est la descente (fiche 08) ou Adam (fiche 31).

## Exemple chiffré

y = 2x et L = y². Alors dL/dy = 2y et dy/dx = 2.

$$
\frac{\mathrm{d} L}{\mathrm{d} x} = 2y \times 2 = 4y = 8x
$$

On retrouve la dérivée directe de L = (2x)² = 4x², dont la dérivée est 8x. La chaîne a évité de réécrire L en fonction de x.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`gradient_numerique(L, theta, h)`** — Cette fonction est le témoin impartial qu'on appelle pour confirmer un calcul fait à la main, comme un expert qui pèse deux fois la même marchandise sur une balance différente : elle reçoit la fonction de perte L, le point θ sous forme de liste et un petit écart h, 10⁻⁶ par défaut, puis pour chaque coordonnée évalue la perte un pas de h au-dessus et un pas de h au-dessous, sans toucher aux autres coordonnées. Elle divise chaque différence par 2h et renvoie la liste de ces pentes, une approximation du gradient ; dans ce programme, elle confirme notamment que la dérivée de (2x)² en x = 1,5 vaut bien 12, le résultat que la règle de la chaîne obtient sans réécrire L en fonction de x.

**`derivee_par_la_chaine(x)`** — Voici la fonction de cette fiche, qui suit le relais d'une course où chaque coureur transmet le témoin au suivant en multipliant son élan : elle reçoit l'entrée x de la couche, calcule sa sortie y = 2x, puis la dérivée locale sous chaque flèche du schéma, dL/dy = 2y pour la perte L = y² et dy/dx = 2 pour la couche y = 2x. Elle renvoie le produit de ces deux maillons, dL/dx = 2y × 2 = 8x, soit 12 en x = 1,5, et illustre ainsi la remarque de la fiche : si l'un des maillons valait 0, le produit serait nul et rien ne remonterait vers x.

**`main()`** — C'est le juge d'arrivée qui confronte chaque relais au chronométrage officiel : il vérifie d'abord le gradient (2 ; 6) de θ₁² + 3θ₂² en (1 ; 1) et le point (0,8 ; 0,4) atteint après un pas de 0,1, puis la dérivée −4 du neurone (w x − y)² de la fiche 34, chaque fois en comparant au calcul numérique. Il appelle enfin `derivee_par_la_chaine` en x = 1,5, imprime 12 et la formule 8x, vérifie par un `assert` que ce résultat exact coïncide avec le gradient numérique de (2x)² au millionième près, et imprime la ligne de succès.

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
- [Fiche 34 — Gradient](<34_gradient.md>)
- [Fiche 08 — Descente de gradient](<08_descente_de_gradient.md>)
