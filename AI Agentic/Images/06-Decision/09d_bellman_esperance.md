# Fiche 09d_bellman_esperance — Bellman d'espérance

> Image : `09d_bellman_esperance.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**La valeur, écrite comme une espérance**

## Ce que montre l'image

Affiche « Équation de Bellman d'espérance ». Elle écrit Vπ(s) = Eπ[Rₜ₊₁ + γ Vπ(Sₜ₊₁) | Sₜ = s] : c'est la forme de cette fiche, écrite comme une espérance. Le crochet n'est pas refermé. Cinq symboles sont expliqués, puis : conséquences (évaluer une politique de façon récursive), effets (base du Q-learning, du DQN et de l'apprentissage par différence temporelle), impacts (agents qui maximisent la récompense cumulée).

**À lire avec prudence :** l'affiche autorise γ = 1 (0 ≤ γ ≤ 1). C'est possible seulement si l'épisode se termine toujours ; sinon la valeur peut devenir infinie (fiche 09, démonstration 2).

## Formule

$$
V^{\pi}(s) = \mathbb{E}_{\pi}\!\left[ R_{t+1} + \gamma V^{\pi}(S_{t+1}) \mid S_t = s \right]
$$

## Éléments

$$
V^{\pi}(s)
$$

**Vπ(s)** : le retour moyen en partant de s et en suivant π.

$$
\mathbb{E}_{\pi}
$$

**𝔼π** : la moyenne sous la politique et les transitions.

$$
R_{t+1}
$$

**Rₜ₊₁** : la récompense du prochain pas.

$$
0 \le \gamma \le 1
$$

**γ (gamma)** : l'actualisation, entre 0 et 1 sur l'affiche. Pour que la somme infinie converge, on prend en pratique γ < 1 si les récompenses ne s'arrêtent pas.

$$
V^{\pi}(S_{t+1})
$$

**Vπ(Sₜ₊₁)** : la valeur de l'état d'après.

## Ce que c'est

C'est la fiche 09 écrite en une ligne. L'espérance cache les deux sommes (politique et transitions). Elle permet d'évaluer une politique sans la redérouler.

## Effets et impacts

- C'est la base de l'évaluation de politique, puis du Q-learning (fiche 18).
- Elle ne dit pas quelle action est la meilleure. Elle dit ce que vaut la politique actuelle.

## Exemple chiffré

Un état, une action certaine, R = 2, et l'on reste dans l'état. γ = 0,5.

$$
V = 2 + 0{,}5\, V \implies 0{,}5\, V = 2 \implies V = 4
$$

La récompense 2 répétée à l'infini, actualisée, vaut 4, pas l'infini.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`valeur_action(recompense, gamma, valeur_suivante)`** — Cette fonction calcule ce qui se trouve à l'intérieur de l'espérance quand le hasard a déjà parlé, comme un actuaire qui chiffrerait un seul scénario avant de faire la moyenne de tous : elle reçoit la récompense Rₜ₊₁ du prochain pas, le facteur γ et la valeur de l'état d'après, puis renvoie Rₜ₊₁ + γ Vπ(Sₜ₊₁), le terme que l'espérance de cette fiche moyenne sur les actions et les transitions. Ici les transitions sont certaines, il n'y a donc qu'un scénario et pas de moyenne à faire, ce qui permet à `main` de comparer directement les valeurs 11 et 5 de la fiche 09, 1 et 4 de la fiche 09a, puis 1 et 4,5 de la fiche 09e.

**`point_fixe(recompense, gamma, tours)`** — Celle-ci est le registre d'une rente perpétuelle qu'on réévalue chaque année, la nouvelle estimation valant le versement de l'année plus γ fois l'ancienne estimation : elle reçoit le versement R, le facteur γ et le nombre de réévaluations, deux cents par défaut, part de zéro et applique cette règle V ← R + γ V à un état qui revient toujours sur lui-même. Avec γ = 0,5 et R = 2, la valeur renvoyée se fige sur 4, l'exemple chiffré de cette fiche ; avec γ = 1, cas que l'affiche autorise, rien ne s'amortit et la fonction renverrait 2 × 200 = 400, un nombre qui grandit avec le nombre de tours au lieu de converger, d'où la mise en garde de la fiche.

**`retour(recompenses, gamma)`** — Cette fonction donne ce que l'espérance moyenne, un retour réalisé le long d'une seule trajectoire, et le calcule comme un archiviste qui dépouille un registre en commençant par la dernière ligne : elle reçoit les récompenses de la trajectoire dans l'ordre et le facteur γ, part d'un retour nul, puis remplace pour chaque récompense lue à rebours le retour G par R + γ G. Elle renvoie le retour actualisé, 1,75 pour trois récompenses de 1 avec γ = 0,5, le nombre de la fiche 09f ; la valeur Vπ(s) est précisément la moyenne de ces retours sur toutes les trajectoires possibles.

**`main()`** — C'est le vérificateur qui fait passer, dans l'ordre, les exemples des sept fiches de la famille : il compare les outils A et B de la fiche 09 avec γ = 0,9 et γ = 0,2 (11 et 5, puis 4 et 5), le bonbon et le gâteau de la fiche 09a (1 et 4), demande à `point_fixe` la valeur 4 de l'état qui boucle, propre à cette fiche, garde la meilleure action de la fiche 09e (4,5) et calcule le retour 1,75 de la fiche 09f. Il imprime les résultats sur deux lignes, contrôle chacun par un `assert`, et n'écrit le message de succès que si tous les nombres sont ceux attendus.

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
- [Fiche 22 — Espérance](<22_esperance.md>)
