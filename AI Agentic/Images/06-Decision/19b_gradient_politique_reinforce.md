# Fiche 19b_gradient_politique_reinforce — Gradient de politique

> Image : `19b_gradient_politique_reinforce.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**REINFORCE, avec l'avantage à la place du retour brut**

## Ce que montre l'image

Affiche « Théorème du gradient de politique, REINFORCE pour agents IA ». La formule utilise l'avantage A à la place de la récompense brute, et trois zones fléchées l'expliquent : le gradient de l'objectif, la log-probabilité de l'action, l'avantage. En bas : optimisation sans modèle de l'environnement, mise à jour θ ← θ + α × gradient (une montée, puisqu'on maximise), usage dans le RLHF et PPO pour aligner les LLM.

**Défauts d'écriture dans l'image :** l'indice de l'espérance est écrit deux fois, et le produit est noté « ∗ ».

**Différence avec la fiche 19 :** la fiche multiplie par R ; l'image multiplie par l'avantage, c'est-à-dire R moins une ligne de base.

## Formule

$$
\nabla_{\theta} J(\theta) = \mathbb{E}_{\pi_{\theta}}\!\left[ \nabla_{\theta} \log \pi_{\theta}(a \mid s) \; A^{\pi}(s, a) \right]
$$

## Éléments

$$
J(\theta)
$$

**J(θ)** : l'objectif, le retour moyen.

$$
\theta
$$

**θ (thêta)** : les paramètres de la politique.

$$
\log \pi_{\theta}(a \mid s)
$$

**log πθ(a | s)** : à quel point l'action prise était probable.

$$
A^{\pi}(s, a)
$$

**Aπ(s, a)** : l'avantage (fiche 19a). La fiche 19 utilise à la place le retour brut R. Les deux sont des gradients de politique. L'avantage est la version à plus faible variance.

$$
\theta \leftarrow \theta + \alpha\, \nabla_{\theta} J(\theta)
$$

**La mise à jour dessinée à côté** : on additionne, on ne soustrait pas, car J se maximise.

## Ce que c'est

On augmente la probabilité des actions meilleures que la moyenne, et on baisse celle des actions pires, sans modèle de l'environnement.

## Effets et impacts

- Un avantage bruyant fait encore osciller la politique. A réduit le bruit, il ne l'annule pas.
- PPO et les méthodes d'alignement s'appuient sur ce gradient, avec un frein de KL (fiche 17c).
- Sans garde-fou, renforcer « ce qui a rapporté » peut renforcer un raccourci dangereux.

## Exemple chiffré

Une action a été prise. ∇ log π est un vecteur. A = 2.

Le pas va dans le sens de ∇ log π, deux fois plus loin que si A valait 1. Si A = −2, le pas va dans l'autre sens : cette action devient moins probable.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(z)`** — Cette fonction est le bureau de vote qui convertit des voix brutes en parts de marché : elle reçoit la liste des logits θ, retire à chacun le plus grand pour éviter tout débordement numérique, passe chaque écart à l'exponentielle et divise par la somme de ces exponentielles. Elle renvoie la politique πθ, une liste de probabilités positives qui font 1 au total, par exemple (0,5 ; 0,5) quand tous les logits sont nuls, point de départ des trois pas que `main` fait pour cette fiche.

**`grad_log_pi(theta, action)`** — Celle-ci est le panneau indicateur de l'affiche, la flèche qui montre la direction du gradient de la log-probabilité : elle reçoit les paramètres θ et l'indice de l'action prise, obtient π par `softmax`, puis renvoie le vecteur qui vaut, pour chaque action, 1 moins sa probabilité si c'est l'action prise et 0 moins sa probabilité sinon. Depuis θ = (0 ; 0) et pour la première action, ce vecteur vaut (0,5 ; −0,5) : il dit dans quel sens pousser θ, mais pas de combien, ce qui est le rôle de l'avantage.

**`pas_reinforce(theta, action, signal, pas)`** — Cette fonction est le bouton de volume d'une console : la flèche de `grad_log_pi` fixe la direction, et le signal, ici l'avantage A, règle à la fois la force et le sens du mouvement. Elle reçoit les paramètres, l'action prise, ce signal et le pas d'apprentissage, multiplie chaque composante du gradient par le pas et par le signal, puis l'ajoute aux paramètres, car J se maximise. Elle renvoie les nouveaux paramètres : avec un pas de 0,1 depuis (0 ; 0), le premier paramètre monte de 0,05 pour A = 1, de 0,10 pour A = 2, et descend de 0,10 pour A = −2.

**`avantages(q, pi)`** — Celle-ci est le critique de la méthode acteur-critique, qui ne juge pas une action dans l'absolu mais par rapport à l'habitude de l'agent : elle reçoit les valeurs Q des actions et leurs probabilités sous la politique, calcule la moyenne pondérée V(s), puis renvoie un couple formé de V et de la liste des écarts Q − V. Pour Q = (5, 2, 2) et une politique uniforme, elle renvoie V = 3 et les avantages (2 ; −1 ; −1), les signaux que la fiche 19a fournit à `pas_reinforce`.

**`main()`** — C'est le banc d'essai à trois postes de la famille REINFORCE : au premier, il vérifie le pas de la fiche 19, θ = (0,05 ; −0,05) et une probabilité de 0,525 ; au deuxième, les avantages de la fiche 19a, V = 3 et (2 ; −1 ; −1). Au troisième, propre à cette fiche, il fait trois pas depuis des logits nuls avec des avantages de 1, 2 et −2, imprime 0,05, 0,10 et −0,10, et vérifie par un `assert` que le pas de A = 2 est exactement le double de celui de A = 1 et que celui de A = −2 en est l'opposé, avant d'afficher la ligne de succès.

```python
"""Fiches 19, 19a, 19b — REINFORCE et fonction d'avantage : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def softmax(z: list[float]) -> list[float]:
    m = max(z)
    e = [math.exp(x - m) for x in z]
    return [x / sum(e) for x in e]


def grad_log_pi(theta: list[float], action: int) -> list[float]:
    """Pour une politique softmax : ∇θ log π(a) = one_hot(a) − π."""
    pi = softmax(theta)
    return [(1.0 if i == action else 0.0) - pi[i] for i in range(len(theta))]


def pas_reinforce(theta: list[float], action: int, signal: float, pas: float) -> list[float]:
    """θ ← θ + pas × signal × ∇ log π(a) ; signal = R (fiche 19) ou A(s, a) (fiche 19b). On MONTE : J se maximise."""
    return [t + pas * signal * g for t, g in zip(theta, grad_log_pi(theta, action))]


def avantages(q: list[float], pi: list[float]) -> tuple[float, list[float]]:
    """V(s) = Σ π(a) Q(s, a) ; A(s, a) = Q(s, a) − V(s)."""
    v = sum(p * x for p, x in zip(pi, q))
    return v, [x - v for x in q]


def main() -> None:
    theta = pas_reinforce([0.0, 0.0], 0, 1.0, 0.1)          # fiche 19
    print(f"fiche 19 : θ = {[round(t, 3) for t in theta]}   π(a₁) = {softmax(theta)[0]:.3f}")
    assert [round(t, 3) for t in theta] == [0.05, -0.05] and round(softmax(theta)[0], 3) == 0.525
    v, a = avantages([5, 2, 2], [1 / 3, 1 / 3, 1 / 3])      # fiche 19a
    print(f"fiche 19a : V = {v:.0f}   A = {[round(x) for x in a]}")
    assert math.isclose(v, 3) and [round(x) for x in a] == [2, -1, -1]
    un, deux, moins = (pas_reinforce([0.0, 0.0], 0, s, 0.1) for s in (1, 2, -2))   # fiche 19b
    print(f"fiche 19b : pas avec A = 1 : {un[0]:.2f}, A = 2 : {deux[0]:.2f}, A = −2 : {moins[0]:.2f}")
    assert math.isclose(deux[0], 2 * un[0]) and math.isclose(moins[0], -deux[0])
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
fiche 19 : θ = [0.05, -0.05]   π(a₁) = 0.525
fiche 19a : V = 3   A = [2, -1, -1]
fiche 19b : pas avec A = 1 : 0.05, A = 2 : 0.10, A = −2 : -0.10
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

Le programme écrit le gradient de politique pour la politique la plus simple, une softmax sur deux ou trois actions de paramètres θ. `grad_log_pi` donne la dérivée de log π(a) par rapport à θ, qui vaut, pour une softmax, le vecteur « 1 sur l'action jouée, 0 ailleurs » moins le vecteur des probabilités : augmenter le paramètre de l'action jouée la rend plus probable, augmenter les autres la rend moins probable. `pas_reinforce` multiplie ce gradient par un signal (le retour R dans REINFORCE, l'avantage A dans sa version améliorée) et par un pas, puis l'**ajoute** aux paramètres, parce qu'on maximise l'objectif J au lieu de minimiser une perte. `avantages` calcule la valeur moyenne V(s) des actions sous la politique, puis l'avantage de chaque action, son écart à cette moyenne.

`main` vérifie les trois fiches. Fiche 19 : après un retour de 1 sur la première action, θ passe à (0,05 ; −0,05) et la probabilité de cette action à 0,525. Fiche 19a : avec Q = (5, 2, 2) et une politique uniforme, V vaut 3 et les avantages (2 ; −1 ; −1), si bien que seule la première action est renforcée, alors que ses trois Q sont positives. Fiche 19b : un avantage de 2 fait un pas deux fois plus long qu'un avantage de 1, et un avantage de −2 fait le même pas dans l'autre sens.

## Squelette algorithmique

```text
ALGORITHME REINFORCEAvecAvantage
ENTRÉES : politique πθ, environnement, pas η, nombre d'épisodes
SORTIE  : θ

  POUR CHAQUE épisode FAIRE
      jouer un épisode avec πθ ; garder (sₜ, aₜ, rₜ) à chaque pas
      POUR CHAQUE pas t FAIRE
          Gₜ ← rₜ + γ rₜ₊₁ + γ² rₜ₊₂ + …                (retour à partir de t)
          Aₜ ← Gₜ − V(sₜ)                                (avantage, avec une baseline V)
          θ ← θ + η × Aₜ × ∇θ log πθ(aₜ | sₜ)           (montée de gradient)
      FIN POUR
  FIN POUR
  RETOURNER θ
```

**Complexité.** Chaque pas coûte un calcul de ∇ log π, O(P) pour P paramètres. La difficulté n'est pas le temps de calcul mais la variance : un seul retour bruité fait osciller θ, et la baseline V(s) sert justement à réduire ce bruit sans biaiser le gradient.

**Du squelette au code.** La ligne de l'avantage correspond à `avantages`, et la mise à jour à `pas_reinforce`, qui appelle `grad_log_pi`.

## Dans le cours

- [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)
- [Fiche 19 — REINFORCE](<19_reinforce.md>)
- [Fiche 19a — Avantage](<19a_fonction_avantage.md>)
