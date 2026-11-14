# Fiche 09a_bellman_en_images — Bellman en images

> Image : `09a_bellman_en_images.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**Un bonbon maintenant, ou le gâteau plus tard**

## Ce que montre l'image

Pas de formule. Le robot choisit entre un bonbon tout de suite et un gâteau plus tard, et il prend le gâteau. C'est le facteur γ de la fiche 09 : le futur compte, mais il est actualisé.

## Formule

$$
V^{\pi}(s) = \sum_a \pi(a \mid s) \sum_{s'} P(s' \mid s, a)\, \big[ R + \gamma V^{\pi}(s') \big]
$$

## Éléments

$$
s
$$

**s** : l'état.

$$
a
$$

**a** : l'action.

$$
\pi(a \mid s)
$$

**π(a | s) (pi)** : la politique.

$$
P(s' \mid s, a)
$$

**P(s′ | s, a)** : la chance d'arriver en s′.

$$
R
$$

**R** : la récompense immédiate. Le bonbon.

$$
\gamma \in [0, 1]
$$

**γ (gamma)** : entre 0 et 1. Proche de 0, seul le bonbon compte. Proche de 1, le gâteau compte presque autant.

$$
V(s')
$$

**V(s′)** : la valeur de la suite.

## Ce que c'est

La valeur d'aujourd'hui est le gain immédiat plus la valeur actualisée de la suite.

## Effets et impacts

- γ = 0 : l'agent prend toujours le bonbon.
- γ proche de 1 : il peut refuser le bonbon pour le gâteau.
- Une mauvaise récompense (le bonbon noté trop haut) enferme l'agent dans le court terme.

## Exemple chiffré

Bonbon R = 1 maintenant, puis plus rien. Gâteau : R = 0 maintenant, puis R = 5. γ = 0,8. Une étape.

$$
V(\text{bonbon}) = 1, \qquad V(\text{gâteau}) = 0 + 0{,}8 \times 5 = 4
$$

L'agent de l'image choisit 4, pas 1.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`valeur_action(recompense, gamma, valeur_suivante)`** — Cette fonction est le petit robot de l'image planté devant la vitrine d'une pâtisserie : elle reçoit ce qu'il gagne tout de suite en faisant un choix, le facteur γ qui dit combien il tient à ce qui viendra ensuite, et la valeur de ce qui l'attend après ce choix, puis elle ajoute au gain immédiat γ fois cette valeur future, ce qui est le crochet R + γ V(s′) de l'équation quand la suite est certaine. Elle renvoie la valeur du choix : le bonbon, qui rapporte 1 maintenant et plus rien ensuite, vaut 1, tandis que le gâteau, qui ne rapporte rien maintenant mais 5 à l'étape suivante, vaut 0 + 0,8 × 5 = 4, et c'est en comparant ces deux nombres que le robot renonce au bonbon.

**`point_fixe(recompense, gamma, tours)`** — Celle-ci raconte le cas d'un enfant qui recevrait chaque jour la même friandise, pour toujours, et voudrait savoir ce que vaut ce rendez-vous sans fin : elle reçoit la friandise du jour, le facteur γ et un nombre de tours, deux cents par défaut, part d'une valeur nulle et répète la mise à jour V ← R + γ V, chaque friandise future pesant un peu moins que la précédente. La somme ne grossit pas indéfiniment, elle se fige sur R / (1 − γ), et la fonction renvoie cette valeur stabilisée, 4 pour une friandise de 2 et γ = 0,5, celle des fiches 09b à 09d.

**`retour(recompenses, gamma)`** — Cette fonction fait les comptes d'une journée de gourmandises en partant du soir pour revenir au matin : elle reçoit la liste des récompenses dans l'ordre où elles arrivent et le facteur γ, commence avec un total nul, puis, pour chaque récompense lue de la dernière à la première, remplace le total G par la récompense plus γ fois G. Elle renvoie ainsi le retour actualisé de toute la suite sans calculer une seule puissance de γ, par exemple 1,75 pour trois récompenses de 1 avec γ = 0,5, le nombre de la fiche 09f.

**`main()`** — C'est le maître de cérémonie qui fait défiler les exemples des sept fiches de la famille Bellman : il commence par le choix entre les outils A et B de la fiche 09, qui valent 11 et 5 quand γ = 0,9 mais 4 et 5 quand γ = 0,2, puis il pèse le bonbon et le gâteau de cette fiche avec γ = 0,8, l'état qui boucle des fiches 09b à 09d, la meilleure des deux actions de la fiche 09e et le retour de la fiche 09f. Il imprime chaque résultat, exige par des `assert` que le bonbon vaille 1, le gâteau 4, l'état qui boucle 4, la meilleure action 4,5 et le retour 1,75, et n'affiche la phrase de succès que si toutes ces égalités tiennent.

```python
"""Fiches 09, 09a à 09f — équation de Bellman et retour actualisé : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def valeur_action(recompense: float, gamma: float, valeur_suivante: float) -> float:
    """Q = R + γ V(s′) pour une transition certaine."""
    return recompense + gamma * valeur_suivante


def point_fixe(recompense: float, gamma: float, tours: int = 200) -> float:
    """V = R + γ V, itéré : un état qui boucle sur lui-même converge vers R / (1 − γ)."""
    V = 0.0
    for _ in range(tours):
        V = recompense + gamma * V
    return V


def retour(recompenses: list[float], gamma: float) -> float:
    """G = R₁ + γ R₂ + γ² R₃ + …, calculé depuis la fin : G ← R + γ G."""
    G = 0.0
    for r in reversed(recompenses):
        G = r + gamma * G
    return G


def main() -> None:
    a9, b9 = valeur_action(2, 0.9, 10), valeur_action(5, 0.9, 0)                     # fiche 09
    a2, b2 = valeur_action(2, 0.2, 10), valeur_action(5, 0.2, 0)
    print(f"fiche 09 : γ = 0,9 : A = {a9:.0f}, B = {b9:.0f}   γ = 0,2 : A = {a2:.0f}, B = {b2:.0f}")
    assert (a9, b9) == (11, 5) and math.isclose(a2, 4) and b2 == 5
    bonbon, gateau = valeur_action(1, 0.8, 0), valeur_action(0, 0.8, 5)              # fiche 09a
    v = point_fixe(2, 0.5)                                                         # fiches 09b à 09d
    q_a, q_b = valeur_action(1, 0.9, 0), valeur_action(0, 0.9, 5)                    # fiche 09e
    g = retour([1, 1, 1], 0.5)                                                     # fiche 09f
    print(f"09a : bonbon {bonbon:.0f}, gâteau {gateau:.0f}   09b-d : V = {v:.4f}   09e : V* = {max(q_a, q_b)}   09f : G = {g}")
    assert bonbon == 1 and math.isclose(gateau, 4) and math.isclose(v, 4) and max(q_a, q_b) == 4.5 and g == 1.75
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
fiche 09 : γ = 0,9 : A = 11, B = 5   γ = 0,2 : A = 4, B = 5
09a : bonbon 1, gâteau 4   09b-d : V = 4.0000   09e : V* = 4.5   09f : G = 1.75
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

Le programme découpe l'équation de Bellman en trois fonctions. `valeur_action` calcule la valeur d'une action dont la transition est certaine : la récompense immédiate plus γ fois la valeur de l'état d'arrivée, ce qui est le crochet [R + γ V(s′)] de la formule. Quand plusieurs états d'arrivée sont possibles, on pondère ce crochet par les probabilités P(s′ | s, a), et quand la politique hésite entre plusieurs actions, on pondère encore par π(a | s) ; les fiches choisissent des cas sans hasard pour que le calcul se fasse de tête.

`point_fixe` applique l'équation à un état qui revient sur lui-même : partant de V = 0, elle remplace V par R + γ V deux cents fois, et la valeur converge vers R / (1 − γ), soit 4 pour R = 2 et γ = 0,5, l'exemple des fiches 09b à 09d. C'est le principe de l'itération sur les valeurs : appliquer l'équation jusqu'à ce que V ne bouge plus. `retour` calcule le retour actualisé d'une suite de récompenses en partant de la fin, avec G ← R + γ G, ce qui évite de calculer des puissances de γ.

`main` vérifie chaque exemple : le choix entre A et B qui change avec γ (fiche 09), le gâteau qui vaut 4 contre 1 pour le bonbon (09a), la valeur 4 de l'état qui boucle (09b à 09d), la valeur optimale 4,5 obtenue en gardant la meilleure action (09e) et le retour 1,75 de trois récompenses de 1 avec γ = 0,5 (09f).

## Squelette algorithmique

```text
ALGORITHME ÉvaluerUnePolitique (Bellman d'espérance)
ENTRÉES : états S, politique π(a | s), transitions P(s′ | s, a), récompenses R, γ ∈ [0 ; 1[, tolérance ε
SORTIE  : Vπ

  V ← 0 pour tous les états
  RÉPÉTER
      POUR CHAQUE état s FAIRE
          V′(s) ← Σₐ π(a | s) × Σ sur s′ P(s′ | s, a) × [R(s, a, s′) + γ × V(s′)]
      FIN POUR
      écart ← maxₛ |V′(s) − V(s)| ; V ← V′
  JUSQU'À écart < ε
  RETOURNER V

VARIANTE Bellman d'optimalité : remplacer Σₐ π(a | s) × … par maxₐ … ; la politique optimale joue l'action qui atteint ce max.
```

**Complexité.** Une itération coûte O(|S|² × |A|). Comme l'équation contracte les écarts d'un facteur γ à chaque tour, il faut de l'ordre de ln(1/ε) / ln(1/γ) itérations : une trentaine pour γ = 0,5 et ε = 10⁻⁹, mais plusieurs centaines quand γ approche 1.

**Du squelette au code.** Le terme entre crochets est `valeur_action`, la boucle `RÉPÉTER` sur un seul état est `point_fixe`, la variante d'optimalité est le `max(q_a, q_b)` de `main`, et `retour` calcule la quantité dont Vπ est l'espérance.

## Dans le cours

- [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)
- [Fiche 09 — Équation de Bellman](<09_equation_bellman.md>)
