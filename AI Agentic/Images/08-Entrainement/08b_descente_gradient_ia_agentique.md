# Fiche 08b_descente_gradient_ia_agentique — Descente de gradient, affiche

> Image : `08b_descente_gradient_ia_agentique.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 73 — Descente de gradient et LoRA](<../../12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md>)

**Le pas qui entraîne un agent**

## Ce que montre l'image

Affiche « Descente de gradient en IA agentique ». La formule (le gradient y est écrit ∇θ L, sans indice), trois symboles expliqués, et un visuel en 3D : une vallée où des points rouge, orange et violet descendent vers une étoile verte, le minimum. Trois usages : comment les agents apprennent, mise à jour des politiques et des modèles, base de l'entraînement des réseaux.

**Ce que l'image ajoute à la fiche 08 :** le mot « minimum local ». La descente arrive au fond de la vallée où elle se trouve, pas forcément au point le plus bas de toute la surface.

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

Même mise à jour que la fiche 08. On soustrait un pas dans le sens du gradient.

## Effets et impacts

- C'est le moteur de l'entraînement, avant Adam (fiche 31) qui adapte le pas.
- La perte baisse. Cela ne dit pas que l'agent réussit la tâche.

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

**`descente(gradient, theta, pas, iterations)`** — Cette fonction suit une goutte de pluie tombée sur la vallée en relief de l'affiche, qui glisse toujours du côté où le terrain descend le plus vite jusqu'à se loger dans le creux le plus proche, sans savoir s'il en existe un plus profond ailleurs : elle reçoit la fonction qui calcule le gradient de la perte, la position initiale θ, le taux d'apprentissage α et le nombre d'étapes. À chaque étape, elle évalue le gradient au point courant, en retranche α fois la valeur à θ et ajoute la nouvelle position à la liste, qu'elle renvoie à la fin, point de départ compris ; elle ne cherche pas de minimum global, elle se contente d'appliquer la mise à jour, ce qui donne 4, 3,2 et 2,56 sur la perte θ² avec α = 0,1.

**`main()`** — C'est l'observateur qui fait tomber plusieurs gouttes, comme les points rouge, orange et violet de l'affiche, et note leurs trajectoires : il fournit à `descente` le gradient 2(θ − 3) de la fiche 08 et vérifie par des `assert` qu'avec un pas de 0,1 la goutte passe par 0,6, 1,08 et 1,464, alors qu'avec un pas de 1,1 elle rebondit vers 6,6, −1,32 et 8,184. Il fournit ensuite le gradient 2θ de cette fiche, vérifie la suite 4, 3,2, 2,56 avec α = 0,1 et l'aller-retour sans fin entre 4 et −4 avec α = 1, puis imprime la ligne de succès.

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
