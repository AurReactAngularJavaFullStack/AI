# Fiche 08 — Descente de gradient

> Image : `08_descente_de_gradient.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 73 — Descente de gradient et LoRA](<../../12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md>)

**Ajuster les paramètres**

## Formule

$$
\theta_{t+1} = \theta_t - \eta \times \nabla L(\theta_t)
$$

**Correction par rapport à l'image.** L'image note le taux d'apprentissage η̂ (êta chapeau). Il s'écrit η, sans chapeau : le chapeau désigne d'habitude une estimation.

## Éléments

$$
\theta_t
$$

**θₜ (thêta)** : les paramètres du modèle à l'étape t.

$$
L
$$

**L** : la fonction de perte, à faire baisser.

$$
\nabla L(\theta_t)
$$

**∇L (nabla L)** : le gradient de L, la direction de plus forte hausse de la perte (fiche 34).

$$
\eta
$$

**η (êta)** : le taux d'apprentissage, la taille du pas.

$$
-
$$

**Le signe moins** : on descend, on ne monte pas.

## Ce que c'est

À chaque pas, les poids bougent à l'opposé du gradient. Le modèle apprend en réduisant la perte.

## Effets et impacts

- η trop grand : oscillations ou divergence.
- η trop petit : apprentissage lent.
- Cette règle explique le sous-apprentissage, l'instabilité et l'effet d'un mauvais réglage.
- Elle ne garantit un minimum global que sur une perte convexe.

## Exemple chiffré

Perte à un paramètre, de minimum en θ = 3 :

$$
L(\theta) = (\theta - 3)^2, \qquad \nabla L(\theta) = 2(\theta - 3)
$$

En partant de θ₀ = 0, l'écart au minimum est multiplié par (1 − 2η) à chaque pas :

$$
\theta_{t+1} - 3 = (\theta_t - 3) - 2\eta(\theta_t - 3) = (1 - 2\eta)(\theta_t - 3)
$$

Avec η = 0,1 : facteur 0,8, θ vaut 0,6 puis 1,08 puis 1,464, et converge vers 3. Avec η = 1,1 : facteur −1,2, θ vaut 6,6 puis −1,32 puis 8,184, et diverge en oscillant.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`descente(gradient, theta, pas, iterations)`** — Cette fonction est le randonneur surpris par le brouillard, qui ne voit pas la vallée mais sent sous ses pieds de quel côté le sol monte, et fait chaque fois un pas dans l'autre sens : elle reçoit une fonction qui donne le gradient de la perte en un point, la position de départ θ, la taille du pas η et le nombre de pas à faire. À chaque itération, elle calcule le gradient au point courant, le multiplie par le pas et le retranche de θ, puis note la nouvelle position dans un carnet ; elle renvoie la liste complète des positions, départ compris, ce qui permet de voir si la marche converge, oscille ou s'emballe : 0, 0,6, 1,08 et 1,464 sur la perte (θ − 3)² avec un pas de 0,1.

**`main()`** — C'est le guide de montagne qui fait faire le même parcours à deux randonneurs aux foulées différentes : sur la perte (θ − 3)² de cette fiche, il lance `descente` depuis 0 avec un pas de 0,1, qui rapproche du minimum 3 à chaque pas, puis avec un pas de 1,1, qui fait sauter de 6,6 à −1,32 puis à 8,184, et vérifie ces deux suites par des `assert`. Il passe ensuite à la perte θ² des fiches 08a à 08e, où un pas de 0,1 depuis 4 donne 3,2 puis 2,56 et un pas de 1 fait rebondir indéfiniment entre 4 et −4, vérifie aussi ces valeurs et imprime la ligne de succès.

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
- [Étape 75 — Optimisation : formules](<../../12-Production-Couts-Optimisation/75-Optimisation-Formules.md>)
- [Étape 78 — Synthèse : les mathématiques de l'IA agentique](<../../14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md>)
