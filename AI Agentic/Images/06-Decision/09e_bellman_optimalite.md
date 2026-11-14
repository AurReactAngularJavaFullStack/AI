# Fiche 09e_bellman_optimalite — Bellman d'optimalité

> Image : `09e_bellman_optimalite.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**La valeur de la meilleure politique**

## Ce que montre l'image

Affiche « Équation de Bellman d'optimalité pour agents IA agentic », fidèle à la formule de cette fiche. Au centre, la formule et la liste des symboles, π\* compris. Autour : ce que c'est (la valeur de chaque état sous la meilleure politique), conséquences (Policy Iteration et Value Iteration convergent vers V\* et π\*), effets (stratégies optimales dans tout environnement markovien), impacts (planification séquentielle, décision autonome, objectifs à long terme, robustesse à l'incertitude). Un encadré explique chaque terme, dont γ : proche de 1, vision à long terme ; proche de 0, préférence pour le présent.

**Ce que l'image ajoute :** la phrase finale, l'équation d'optimalité transforme des agents réactifs en agents qui optimisent sur le long terme.

**À lire avec prudence :** comme le dit la fiche, le max suppose de connaître P et R, ce qu'un agent LLM en production n'a presque jamais.

## Formule

$$
V^{*}(s) = \max_a \sum_{s'} P(s' \mid s, a)\, \big[ R(s, a, s') + \gamma V^{*}(s') \big]
$$

## Éléments

$$
V^{*}(s)
$$

**V\*(s)** : la plus grande valeur atteignable dans s.

$$
\max_{a}
$$

**maxₐ** : on garde l'action dont le crochet est le plus grand.

$$
P(s' \mid s, a)
$$

**P(s′ | s, a)** : l'incertitude de l'environnement.

$$
R(s, a, s')
$$

**R(s, a, s′)** : la récompense de la transition.

$$
0 \le \gamma < 1
$$

**γ (gamma)** : l'actualisation. Proche de 1, elle regarde loin. Proche de 0, elle regarde le présent.

$$
\pi^{*}
$$

**π\* (pi étoile)** : la politique qui joue, dans chaque état, une action qui atteint ce max.

## Ce que c'est

L'équation d'espérance (fiche 09d) évalue une politique donnée. Celle-ci choisit, à chaque état, l'action qui mène à la plus grande valeur. Policy iteration et value iteration cherchent ce V\*.

## Effets et impacts

- L'agent planifie des conséquences, il ne réagit plus seulement au dernier message.
- Le max suppose que l'on connaît P et R. Un LLM en production ne les a en général pas : on s'en sert comme modèle de pensée, pas comme un solveur exact.
- γ = 1 avec des récompenses qui ne s'arrêtent pas rend V\* infini.

## Exemple chiffré

Deux actions certaines. A : R = 1 puis on s'arrête (valeur future 0). B : R = 0 puis un état de valeur 5. γ = 0,9.

$$
Q(A) = 1, \qquad Q(B) = 0 + 0{,}9 \times 5 = 4{,}5
$$

$$
V^{*} = \max(1,\ 4{,}5) = 4{,}5
$$

π\* joue B.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`valeur_action(recompense, gamma, valeur_suivante)`** — Cette fonction est le jury qui note un candidat à la fois, avant que le président ne proclame le meilleur : elle reçoit la récompense obtenue en jouant une action, le facteur γ et la valeur de l'état où cette action conduit, puis elle renvoie la récompense augmentée de γ fois cette valeur, c'est-à-dire la valeur Q de l'action, le crochet sur lequel porte le max de l'équation d'optimalité. Dans l'exemple de cette fiche, elle note l'action A, qui rapporte 1 puis s'arrête, à 1, et l'action B, qui ne rapporte rien tout de suite mais mène à un état de valeur 5, à 0 + 0,9 × 5 = 4,5 ; elle ne choisit rien elle-même, ce choix revient à `main`.

**`point_fixe(recompense, gamma, tours)`** — Celle-ci décrit un état sans aucune alternative, une pièce dont l'unique porte ramène dans la même pièce, si bien que le max de l'optimalité n'a qu'une seule action à départager et que l'équation se réduit à V = R + γ V : elle reçoit la récompense, le facteur γ et un nombre de tours, deux cents par défaut, part de zéro et applique cette mise à jour encore et encore, exactement comme la value iteration le fait sur un seul état. Elle renvoie la valeur stabilisée R / (1 − γ), soit 4 pour R = 2 et γ = 0,5, le nombre des fiches 09b à 09d.

**`retour(recompenses, gamma)`** — Cette fonction est le comptable qui, une partie terminée, refait l'addition de tout ce qui a été gagné en remontant du dernier coup vers le premier : elle reçoit la liste des récompenses dans l'ordre et le facteur γ, part d'un retour nul, puis remplace pour chaque récompense lue à rebours le retour G par R + γ G. Elle renvoie le retour actualisé, 1,75 pour trois récompenses de 1 avec γ = 0,5, celui de la fiche 09f ; la valeur optimale de cette fiche est le plus grand retour moyen que l'on puisse obtenir en choisissant bien ses actions.

**`main()`** — C'est le président du jury, celui qui proclame le résultat de chaque concours de la famille Bellman : après les outils A et B de la fiche 09 (11 contre 5 avec γ = 0,9, 4 contre 5 avec γ = 0,2), le bonbon et le gâteau de la fiche 09a et l'état qui boucle des fiches 09b à 09d, il fait noter par `valeur_action` les deux actions de cette fiche, puis garde la meilleure avec `max(q_a, q_b)`, ce qui est le max de l'équation d'optimalité. Il vérifie par des `assert` que ce maximum vaut 4,5, donc que la politique optimale joue B, contrôle aussi le retour 1,75 de la fiche 09f, et n'imprime la phrase de succès que si toutes les valeurs concordent.

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
