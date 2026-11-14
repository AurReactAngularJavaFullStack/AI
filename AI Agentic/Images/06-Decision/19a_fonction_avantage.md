# Fiche 19a_fonction_avantage — Fonction d'avantage

> Image : `19a_fonction_avantage.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**Meilleure, égale, ou pire que la moyenne**

## Ce que montre l'image

Affiche « Fonction d'avantage dans le RL ». La formule A(s, a) = Q(s, a) − V(s), avec trois lectures : A > 0, l'action est meilleure que la moyenne ; A = 0, équivalente ; A < 0, moins bonne. Conséquences : soustraire V(s), une ligne de base qui ne dépend pas de l'action, réduit la variance du gradient de politique sans introduire de biais. Usages : A2C, PPO et méthodes acteur-critique.

**Précision :** V(s) est la moyenne des Q(s, a) pondérée par la politique, et non la moyenne simple, sauf si la politique joue toutes les actions à égalité.

**Lien :** l'absence de biais est démontrée dans `Demonstrations/06-Decision/19_reinforce.md` (démonstration 3).

## Formule

$$
A(s, a) = Q(s, a) - V(s)
$$

## Éléments

$$
A(s, a)
$$

**A(s, a)** : l'avantage de l'action a dans l'état s.

$$
Q(s, a)
$$

**Q(s, a)** : la valeur de prendre a puis de continuer.

$$
V(s)
$$

**V(s)** : la valeur moyenne des actions dans s, sous la politique.

A > 0 : meilleure que la moyenne. A = 0 : dans la moyenne. A < 0 : pire.

## Ce que c'est

On ne demande plus « cette action vaut combien ? ». On demande « vaut-elle mieux que ce que l'agent fait d'habitude dans cet état ? ». V(s) ne dépend pas de a : le soustraire ne change pas quelle action est la meilleure, et cela réduit la variance du gradient.

## Effets et impacts

- Utilisée dans les méthodes acteur-critique, dont la fiche 19b.
- Moins de variance, mises à jour plus stables.
- Si V est mal estimée, A est décalée et le gradient pousse dans le mauvais sens.

## Exemple chiffré

Dans s, trois actions. Q vaut 5, 2 et 2. Si la politique les joue de façon équiprobable,

$$
V = (5+2+2)/3 = 3, \qquad A = (2,\ -1,\ -1)
$$

Seule la première action est au-dessus de la moyenne. Les trois Q étaient positives : sans A, on aurait renforcé les trois.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(z)`** — Cette fonction est l'urne qui transforme des préférences brutes en chances de tirage : elle reçoit la liste des logits de la politique, soustrait le plus grand à chacun pour garder des exponentielles de taille raisonnable, calcule ces exponentielles puis les divise par leur total. Elle renvoie une liste de probabilités positives dont la somme vaut 1, c'est-à-dire la politique π ; dans ce programme, elle donne (0,5 ; 0,5) pour des logits nuls et environ 0,525 pour la première action après le pas de la fiche 19, mais cette fiche-ci lui préfère une politique uniforme donnée directement.

**`grad_log_pi(theta, action)`** — Celle-ci est la boussole qui indique, pour chaque paramètre, la direction qui rend plus probable l'action qu'on vient de jouer : elle reçoit les paramètres θ et l'indice de l'action, calcule les probabilités avec `softmax`, puis renvoie pour chaque action la quantité 1 moins sa probabilité si c'est l'action jouée, et 0 moins sa probabilité sinon. Ce vecteur, le gradient de log π(a), vaut (0,5 ; −0,5) depuis θ = (0 ; 0) quand la première action est jouée ; c'est lui que l'avantage de cette fiche viendra pondérer dans la fiche 19b.

**`pas_reinforce(theta, action, signal, pas)`** — Cette fonction est le jardinier qui arrose davantage la plante qui a donné plus de fruits que la moyenne, et retient l'eau de celle qui a déçu : elle reçoit les paramètres, l'action jouée, un signal, le retour R ou l'avantage A, et la taille du pas, multiplie le gradient fourni par `grad_log_pi` par le pas et par le signal, puis l'ajoute aux paramètres. Elle renvoie les nouveaux paramètres ; avec un avantage négatif, comme le −1 des deux dernières actions de cette fiche, le pas part dans l'autre sens et l'action devient moins probable.

**`avantages(q, pi)`** — Voici la fonction de cette fiche, qui raisonne comme un golfeur comparant son score au par du trou plutôt qu'à zéro : elle reçoit les valeurs Q des actions et leurs probabilités sous la politique, calcule la valeur moyenne V(s) comme la somme des Q pondérées par ces probabilités, puis retranche V à chaque Q. Elle renvoie un couple formé de V et de la liste des avantages A(s, a) : pour Q = (5, 2, 2) jouées à égalité, V vaut 3 et les avantages (2 ; −1 ; −1), si bien qu'une seule action se trouve au-dessus du par alors que les trois Q étaient positives.

**`main()`** — C'est le greffier qui consigne les trois exemples de la famille : il vérifie d'abord le pas de la fiche 19, θ = (0,05 ; −0,05) et une probabilité de 0,525 pour la première action, puis appelle `avantages` avec Q = (5, 2, 2) et une politique uniforme d'un tiers par action, imprime V = 3 et A = (2, −1, −1) et contrôle ces valeurs par un `assert`. Il termine par les pas de la fiche 19b avec des avantages de 1, 2 et −2, vérifie qu'ils valent 0,05, le double et l'opposé du double, puis imprime la ligne de succès.

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
- [Fiche 18 — Q-learning](<18_q_learning.md>)
- [Fiche 19 — REINFORCE](<19_reinforce.md>)
