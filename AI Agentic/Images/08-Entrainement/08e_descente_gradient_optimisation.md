# Fiche 08e_descente_gradient_optimisation — Descente de gradient, optimisation

> Image : `08e_descente_gradient_optimisation.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 73 — Descente de gradient et LoRA](<../../12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md>)

**La version de l'affiche : θ, α, et le gradient de L**

## Ce que montre l'image

Affiche « Descente de gradient, optimisation fondamentale pour IA agentique ». Quatre panneaux : une surface avec la trajectoire du départ au minimum ; des courbes de niveau où la trajectoire converge en spirale ; un réseau de neurones ; un agent qui agit dans un environnement et reçoit une récompense. Le panneau « Conséquences » donne la condition : avec un pas adapté et une perte convexe ou assez lisse, la suite θₜ converge vers un minimum. Variantes citées : SGD, Adam, RMSprop.

**Ce que l'image ajoute à la fiche 08 :** la condition de convergence, démontrée pour une parabole dans `Demonstrations/08-Entrainement/08_descente_de_gradient.md` (démonstration 3).

## Formule

$$
\theta_{t+1} = \theta_t - \alpha \nabla_{\theta} L(\theta_t)
$$

## Éléments

$$
\theta_t
$$

**θₜ (thêta)** : les paramètres à l'étape t.

$$
L
$$

**L** : la perte.

$$
\nabla L
$$

**∇L (nabla L)** : la direction de plus forte hausse de la perte.

$$
\alpha
$$

**α (alpha)** : le taux d'apprentissage, la taille du pas.

$$
-
$$

**Le signe moins** : on descend.

## Ce que c'est

L'affiche écrit α pour le taux et ∇θ L(θₜ) pour la pente. À chaque itération on se déplace à l'opposé du gradient pour diminuer L.

## Effets et impacts

- Sous des conditions raisonnables (pas adapté, perte assez lisse), la suite se rapproche d'un minimum.
- SGD, Adam, RMSProp sont des variantes de ce pas.
- Le minimum de L n'est pas, à lui seul, un agent sûr.

## Exemple chiffré

L(θ) = θ², donc ∇L = 2θ. On part de θ = 4, avec α = 0,1.

$$
\theta_1 = 4 - 0{,}1 \times 8 = 3{,}2
$$

$$
\theta_2 = 3{,}2 - 0{,}1 \times 6{,}4 = 2{,}56
$$

On se rapproche de 0. Avec α = 1, θ passe de 4 à 4 − 8 = −4, puis revient à 4 : il oscille sans fin entre 4 et −4 sans jamais approcher le minimum.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`descente(gradient, theta, pas, iterations)`** — Cette fonction est le pilote d'un avion en approche, qui lit à chaque instant l'inclinaison du terrain sous lui et corrige son altitude d'une quantité proportionnelle à cette pente : elle reçoit la fonction qui calcule le gradient de la perte, la position de départ θ, le pas α et le nombre de corrections à effectuer. À chaque correction, elle évalue ∇θ L(θₜ) au point courant, retranche α fois ce gradient et inscrit la nouvelle position dans le journal de vol qu'elle renvoie à la fin, départ compris ; la condition de convergence de l'affiche s'y lit directement, car sur la perte θ² chaque pas multiplie θ par 1 − 2α, si bien que la suite converge pour α entre 0 et 1 exclus, comme avec α = 0,1 (4, 3,2, 2,56), et oscille sans fin pour α = 1.

**`main()`** — C'est la tour de contrôle qui fait faire deux approches sur deux terrains et vérifie chaque trajectoire : sur la perte (θ − 3)² de la fiche 08, il contrôle par des `assert` qu'un pas de 0,1 descend en douceur vers 3 par 0,6, 1,08 et 1,464, tandis qu'un pas de 1,1 dépasse la cible et s'en éloigne par 6,6, −1,32 et 8,184. Sur la perte θ² de cette fiche, il vérifie la descente 4, 3,2, 2,56 avec α = 0,1 et l'aller-retour 4, −4, 4 avec α = 1, preuve qu'un pas mal adapté empêche la convergence, puis imprime la ligne de succès.

```python
"""Fiches 08, 08a à 08e — descente de gradient : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def descente(gradient, theta: float, pas: float, iterations: int) -> list[float]:
    """θ ← θ − pas × ∇L(θ), répété ; renvoie la suite des θ."""
    suite = [theta]
    for _ in range(iterations):
        theta = theta - pas * gradient(theta)
        suite.append(theta)
    return suite


def main() -> None:
    lente = descente(lambda t: 2 * (t - 3), 0.0, 0.1, 3)      # fiche 08 : L = (θ − 3)²
    folle = descente(lambda t: 2 * (t - 3), 0.0, 1.1, 3)
    print("fiche 08, η = 0,1 :", [round(t, 3) for t in lente], "  η = 1,1 :", [round(t, 3) for t in folle])
    assert [round(t, 3) for t in lente] == [0.0, 0.6, 1.08, 1.464]
    assert [round(t, 3) for t in folle] == [0.0, 6.6, -1.32, 8.184]
    variante = descente(lambda t: 2 * t, 4.0, 0.1, 2)        # fiches 08a à 08e : L = θ²
    saut = descente(lambda t: 2 * t, 4.0, 1.0, 2)
    print("fiches 08a à 08e, α = 0,1 :", [round(t, 2) for t in variante], "  α = 1 :", saut)
    assert [round(t, 2) for t in variante] == [4.0, 3.2, 2.56] and saut == [4.0, -4.0, 4.0]
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
fiche 08, η = 0,1 : [0.0, 0.6, 1.08, 1.464]   η = 1,1 : [0.0, 6.6, -1.32, 8.184]
fiches 08a à 08e, α = 0,1 : [4.0, 3.2, 2.56]   α = 1 : [4.0, -4.0, 4.0]
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`descente` reçoit une fonction qui calcule le gradient de la perte, un point de départ, un pas (le taux d'apprentissage η ou α selon les fiches) et un nombre d'itérations. À chaque itération, elle calcule le gradient au point courant, le multiplie par le pas et le retranche du point : le signe moins fait descendre, à l'opposé de la direction où la perte augmente le plus vite. Elle garde toute la suite des points, ce qui permet de voir si la descente converge, oscille ou diverge.

`main` rejoue les deux exemples de la famille. Sur la perte (θ − 3)² de la fiche 08, dont le minimum est en 3, un pas de 0,1 donne 0,6 puis 1,08 puis 1,464 : chaque pas réduit l'écart au minimum d'un facteur 0,8. Un pas de 1,1 multiplie au contraire cet écart par −1,2 à chaque itération, et la suite 6,6 ; −1,32 ; 8,184 s'éloigne en oscillant. Sur la perte θ² des fiches 08a à 08e, un pas de 0,1 depuis 4 donne 3,2 puis 2,56, tandis qu'un pas de 1 saute de 4 à −4 puis revient à 4, sans jamais approcher le minimum.

## Squelette algorithmique

```text
ALGORITHME DescenteDeGradient
ENTRÉES : gradient ∇L, point de départ θ₀, pas η, nombre d'itérations N (ou tolérance ε)
SORTIE  : θ final

  θ ← θ₀
  POUR t DE 1 À N FAIRE
      g ← ∇L(θ)
      SI ‖g‖ < ε ALORS sortir (plateau ou minimum atteint)
      θ ← θ − η × g
  FIN POUR
  RETOURNER θ
```

**Complexité.** N itérations, chacune au coût d'un calcul de gradient : O(N × coût de ∇L). Pour un réseau de P paramètres, la rétropropagation calcule ∇L en O(P) par exemple, donc une époque sur m exemples coûte O(m × P).

**Du squelette au code.** La boucle `POUR` est la boucle `for _ in range(iterations)` de `descente`, et la mise à jour est la ligne `theta = theta - pas * gradient(theta)`. Le programme omet le test d'arrêt sur ε pour garder exactement le nombre d'itérations des fiches.

## Dans le cours

- [Étape 73 — Descente de gradient et LoRA](<../../12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md>)
- [Fiche 08 — Descente de gradient](<08_descente_de_gradient.md>)
- [Fiche 31 — Adam](<31_adam.md>)
