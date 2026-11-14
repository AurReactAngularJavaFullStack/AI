# Fiche 09b_equation_bellman_affiche — Équation de Bellman, affiche

> Image : `09b_equation_bellman_affiche.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**La valeur d'un état inclut la suite**

## Ce que montre l'image

Affiche « L'équation de Bellman en IA agentique ». **Attention : l'image montre l'équation d'optimalité**, avec un max sur les actions, V(s) = max sur a de [R(s, a) + γ Σ P(s′ | s, a) V(s′)], alors que cette fiche donne l'équation d'une politique fixée π (une moyenne sur les actions au lieu d'un max). Les deux sont démontrées dans les fiches 09 et 09e. Le crochet de l'image n'est pas refermé. Les éléments sont expliqués un à un : valeur d'état, récompense, γ entre 0 et 1, probabilités de transition. Trois usages : planifier à long terme, équilibrer récompense immédiate et future, base des MDP.

**Ce que l'image ajoute :** une phrase à retenir, « la valeur d'un état est le meilleur compromis entre ce que l'on gagne maintenant et ce que cela ouvre comme possibilités futures ».

## Formule

$$
V^{\pi}(s) = \sum_a \pi(a \mid s) \sum_{s'} P(s' \mid s, a)\, \big[ R(s, a, s') + \gamma V^{\pi}(s') \big]
$$

## Éléments

$$
V^{\pi}(s)
$$

**Vπ(s)** : la valeur de l'état s si l'on suit la politique π.

$$
\pi,\ P,\ R,\ \gamma
$$

**π, P, R, γ (pi, P, R, gamma)** : politique, transitions, récompense, actualisation. Voir la fiche 09.

## Ce que c'est

Affiche de la fiche 09. La valeur se définit à partir d'elle-même : c'est une équation de point fixe, pas une somme qu'on développe à la main sur un horizon infini.

## Effets et impacts

- Elle évalue une politique déjà choisie. Elle ne choisit pas encore la meilleure action. Cela, c'est la fiche 09e.
- γ proche de 0 privilégie le gain immédiat.

## Exemple chiffré

Un état, une action certaine, R = 2, et l'on reste dans l'état. γ = 0,5.

$$
V = 2 + 0{,}5\, V \implies 0{,}5\, V = 2 \implies V = 4
$$

La récompense 2 répétée à l'infini, actualisée, vaut 4, pas l'infini.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`valeur_action(recompense, gamma, valeur_suivante)`** — Cette fonction joue le rôle d'un voyageur qui, arrivé à un carrefour, pèse ce que lui rapporte une seule route : elle reçoit la récompense qu'il touchera tout de suite en la prenant, le facteur d'actualisation γ qui dit combien il tient au lendemain, et la valeur de l'état où cette route le dépose, puis elle additionne la récompense immédiate et γ fois cette valeur future, exactement le crochet R + γ V(s′) de l'équation de Bellman. Elle renvoie ce seul nombre, la valeur Q de l'action, et c'est lui que `main` compare d'une action à l'autre : 11 contre 5 quand γ = 0,9, mais 4 contre 5 quand γ = 0,2, si bien que le voyageur patient et le voyageur pressé ne prennent pas la même route.

**`point_fixe(recompense, gamma, tours)`** — Celle-ci raconte l'histoire d'un état qui revient sans cesse sur lui-même, comme une pièce dont l'unique porte ramène dans la même pièce : partant d'une estimation nulle, elle répète `tours` fois, deux cents par défaut, la même opération, qui remplace V par la récompense du jour augmentée de γ fois ce que V valait au tour précédent. À chaque passage, l'écart avec la vraie valeur est multiplié par γ, donc divisé par deux quand γ = 0,5, comme un marcheur qui franchit chaque fois la moitié du chemin qui le sépare du mur ; la fonction renvoie la valeur stabilisée, R / (1 − γ), soit 4 pour R = 2, celle de l'exemple chiffré des fiches 09b à 09d.

**`retour(recompenses, gamma)`** — Cette fonction remonte le temps, comme un comptable qui relit un carnet de la dernière page vers la première : elle reçoit la liste des récompenses touchées étape après étape et le facteur γ, part d'un retour nul à la fin de l'histoire, puis, pour chaque récompense lue à rebours, ajoute cette récompense à γ fois le retour déjà accumulé derrière elle, selon la règle G ← R + γ G. Ce chemin à reculons lui évite de calculer la moindre puissance de γ, et elle renvoie le retour actualisé de toute la suite : 1,75 pour trois récompenses de 1 avec γ = 0,5, c'est-à-dire 1 + 0,5 + 0,25.

**`main()`** — C'est le chef d'orchestre qui fait jouer, une à une, toutes les fiches de la famille Bellman : il appelle `valeur_action` pour montrer que le choix entre A et B bascule quand γ passe de 0,9 à 0,2 (fiche 09), puis pour opposer le bonbon qui vaut 1 au gâteau qui vaut 4 (fiche 09a), et pour garder la meilleure des deux actions, 4,5, dans la fiche 09e ; il demande à `point_fixe` la valeur 4 de l'état qui boucle (fiches 09b à 09d) et à `retour` le total 1,75 de la fiche 09f. Chaque nombre imprimé est aussitôt confronté par un `assert` à la valeur calculée à la main, et la dernière ligne n'annonce que toutes les vérifications sont passées que si tous concordent.

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
