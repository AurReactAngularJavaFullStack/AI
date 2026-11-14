# Fiche 09 — Équation de Bellman

> Image : `09_equation_bellman.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**La valeur d'un état inclut l'avenir**

## Formule

$$
V(s) = \sum_{a} \pi(a \mid s) \sum_{s'} P(s' \mid s, a) \left[ R + \gamma\, V(s') \right]
$$

## Éléments

$$
s
$$

**s** : l'état actuel (ce que l'agent sait et a déjà fait).

$$
a
$$

**a** : une action, par exemple appeler un outil.

$$
\pi(a \mid s)
$$

**π(a | s) (pi)** : la politique, la chance de choisir a dans l'état s.

$$
P(s' \mid s, a)
$$

**P(s′ | s, a)** : la chance d'arriver dans l'état s′ après l'action a.

$$
R
$$

**R** : la récompense immédiate.

$$
\gamma \in [0, 1]
$$

**γ (gamma)** : le facteur d'actualisation, entre 0 et 1.

$$
V(s')
$$

**V(s′)** : la valeur de l'état suivant.

## Ce que c'est

La valeur d'aujourd'hui est la récompense immédiate plus la valeur actualisée de la suite. On moyenne sur les actions (selon la politique) et sur les états d'arrivée (selon les probabilités de transition).

## Effets et impacts

- Elle formalise un agent à plusieurs étapes.
- γ proche de 0 privilégie le gain immédiat.
- γ proche de 1 compte les conséquences lointaines.
- Une mauvaise récompense pousse l'agent vers des outils inutiles ou des boucles.

## Exemple chiffré

Deux outils, transitions certaines, état suivant terminal après le second coup :

$$
\text{outil A} : R = 2, \ V(s') = 10 \qquad\qquad \text{outil B} : R = 5, \ V(s') = 0
$$

$$
\gamma = 0{,}9 : \quad A = 2 + 0{,}9 \times 10 = 11 \ >\ B = 5
$$

$$
\gamma = 0{,}2 : \quad A = 2 + 0{,}2 \times 10 = 4 \ <\ B = 5
$$

Le même agent change de choix selon γ : patient, il investit dans A ; pressé, il prend le gain immédiat de B.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`valeur_action(recompense, gamma, valeur_suivante)`** — Cette fonction raisonne comme un investisseur prudent devant deux placements, ici les outils A et B de l'agent : elle reçoit le gain encaissé tout de suite en choisissant l'action, le facteur d'actualisation γ qui mesure le prix accordé au lendemain, et la valeur de l'état où l'action conduit, puis elle multiplie cette valeur future par γ et y ajoute le gain immédiat, ce qui reproduit le crochet R + γ V(s′) de l'équation pour une transition certaine. Elle renvoie ce nombre, la valeur de l'action : avec γ = 0,9, l'outil A vaut 2 + 0,9 × 10 = 11 et l'outil B vaut 5, alors qu'avec γ = 0,2 l'outil A ne vaut plus que 4, si bien que l'investisseur patient et l'investisseur pressé ne signent pas le même contrat.

**`point_fixe(recompense, gamma, tours)`** — Celle-ci imite l'écho d'une vallée, où chaque cri revient un peu plus faible que le précédent : elle reçoit une récompense, le facteur γ et un nombre de tours, deux cents par défaut, part d'une valeur nulle et applique à chaque tour la même règle, la nouvelle valeur égale la récompense plus γ fois l'ancienne, comme pour un état qui revient toujours sur lui-même. Les échos s'additionnent sans jamais exploser parce que γ est inférieur à 1, et la fonction renvoie la valeur où la suite se stabilise, R / (1 − γ), soit 4 pour R = 2 et γ = 0,5, ce que `main` vérifie pour les fiches 09b à 09d.

**`retour(recompenses, gamma)`** — Cette fonction lit une histoire en commençant par sa dernière page, à la manière d'un généalogiste qui remonte les générations : elle reçoit la liste des récompenses reçues au fil des étapes et le facteur γ, initialise le retour à zéro, puis parcourt la liste à rebours en remplaçant à chaque pas le retour G par la récompense lue plus γ fois G. Cette astuce évite tout calcul de puissance de γ et produit le retour actualisé R₁ + γ R₂ + γ² R₃ + …, que la fonction renvoie : 1,75 pour trois récompenses de 1 avec γ = 0,5, le total de la fiche 09f.

**`main()`** — C'est le banc d'essai où passent tous les exemples de la famille Bellman, à commencer par celui de cette fiche : il évalue les outils A et B avec γ = 0,9 puis avec γ = 0,2, imprime les quatre valeurs et vérifie par un `assert` qu'elles valent 11 et 5, puis 4 et 5, de sorte que le choix bascule de A vers B quand l'agent devient pressé. Il enchaîne avec le bonbon et le gâteau de la fiche 09a (1 contre 4), l'état qui boucle des fiches 09b à 09d (4), la meilleure action de la fiche 09e (4,5) et le retour de la fiche 09f (1,75), confronte chaque nombre à sa valeur attendue et n'imprime le message de succès que si tout concorde.

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
- [Étape 78 — Synthèse : les mathématiques de l'IA agentique](<../../14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md>)
