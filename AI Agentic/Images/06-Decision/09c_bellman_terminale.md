# Fiche 09c_bellman_terminale — Bellman, niveau terminale

> Image : `09c_bellman_terminale.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**La même équation, symboles du lycée**

## Ce que montre l'image

Fiche de niveau terminale, avec la même équation d'optimalité que 09b (un max sur les actions). Les quatre termes sont expliqués, puis l'interprétation (« la meilleure récompense immédiate plus la valeur actualisée des états suivants, pondérée par leur probabilité ») et une remarque : l'équation est au cœur de Value Iteration, Policy Iteration et du Q-learning.

**Erreur dans l'image :** un γ est écrit au-dessus du Σ, comme une borne de somme. Il faut l'ignorer : la somme porte sur tous les états suivants s′.

**Ce que l'image ajoute :** la distinction entre planification (on connaît P et R) et apprentissage par renforcement (sans les connaître).

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

Version terminale de la fiche 09. On lit la somme sur les actions, puis la somme sur les états suivants, puis le crochet récompense plus avenir actualisé.

## Effets et impacts

- Si la politique est certaine, la première somme disparaît : il ne reste qu'une action.
- Une récompense mal définie apprend la mauvaise boucle.

## Exemple chiffré

Un état, une action certaine, R = 2, et l'on reste dans l'état. γ = 0,5.

$$
V = 2 + 0{,}5\, V \implies 0{,}5\, V = 2 \implies V = 4
$$

La récompense 2 répétée à l'infini, actualisée, vaut 4, pas l'infini.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`valeur_action(recompense, gamma, valeur_suivante)`** — Cette fonction fait ce qu'un élève de terminale écrit au tableau quand on lui demande de calculer une seule case du crochet : elle reçoit la récompense R obtenue en jouant une action, le coefficient γ compris entre 0 et 1, et la valeur V(s′) de l'état d'arrivée, puis elle calcule R + γ V(s′), sans aucune somme puisque la transition est supposée certaine et la politique réduite à une seule action. Elle renvoie ce nombre, la valeur de l'action, que `main` utilise pour les comparaisons des fiches 09, 09a et 09e : par exemple 2 + 0,9 × 10 = 11 pour l'outil A de la fiche 09, ou 0 + 0,9 × 5 = 4,5 pour la meilleure action de la fiche 09e.

**`point_fixe(recompense, gamma, tours)`** — Celle-ci est la suite récurrente que le professeur fait étudier en fin de chapitre : elle reçoit R, γ et un nombre de termes à calculer, deux cents par défaut, pose u₀ = 0 puis calcule uₙ₊₁ = R + γ uₙ autant de fois que demandé, exactement l'équation V = R + γ V d'un état qui revient sur lui-même. Comme l'écart à la limite est multiplié par γ à chaque terme, la suite converge, et la fonction renvoie le dernier terme, pratiquement égal à la limite R / (1 − γ) : 4 pour R = 2 et γ = 0,5, la valeur que l'exemple chiffré de cette fiche obtient en résolvant 0,5 V = 2.

**`retour(recompenses, gamma)`** — Cette fonction est la méthode de Horner appliquée à une somme actualisée, celle qu'un élève astucieux emploie pour ne pas calculer γ², γ³ et la suite : elle reçoit la liste des récompenses R₁, R₂, R₃… et le coefficient γ, part de G = 0, puis lit la liste de droite à gauche en remplaçant chaque fois G par R + γ G. Elle renvoie le retour actualisé R₁ + γ R₂ + γ² R₃ + …, soit 1,75 pour trois récompenses de 1 avec γ = 0,5, c'est-à-dire 1 + 0,5 + 0,25, le résultat de la fiche 09f.

**`main()`** — C'est le corrigé de l'épreuve, qui reprend un à un les exercices des fiches 09 à 09f : il évalue les deux outils de la fiche 09 avec γ = 0,9 et γ = 0,2 (11 contre 5, puis 4 contre 5), le bonbon et le gâteau de la fiche 09a (1 contre 4), la suite de `point_fixe` pour cette fiche, la meilleure action de la fiche 09e et le retour de la fiche 09f. Chaque résultat est imprimé puis confronté par un `assert` à la valeur trouvée à la main, notamment V = 4 pour l'état qui boucle, et le message final n'annonce le succès que si toutes les égalités sont vérifiées.

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
