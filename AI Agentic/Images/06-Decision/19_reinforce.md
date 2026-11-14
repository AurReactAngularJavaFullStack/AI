# Fiche 19 — REINFORCE

> Image : `19_reinforce.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**Renforcer les actions bien récompensées**

## Formule

$$
\nabla_\theta J(\theta) = \mathbb{E}\left[ \nabla_\theta \log \pi_\theta(a \mid s) \times R \right]
$$

## Éléments

$$
\theta
$$

**θ (thêta)** : les paramètres de la politique.

$$
\pi_\theta(a \mid s)
$$

**π_θ(a | s)** : la probabilité de l'action a dans l'état s.

$$
\log \pi_\theta(a \mid s)
$$

**log π** : le score de log-vraisemblance de l'action prise.

$$
R
$$

**R** : le retour reçu pour cette trajectoire.

$$
\mathbb{E}
$$

**𝔼** : l'espérance sur les trajectoires (fiche 22).

$$
J(\theta)
$$

**J** : l'objectif à maximiser, le retour moyen.

$$
\nabla_\theta
$$

**∇_θ** : le gradient par rapport aux paramètres (fiche 34).

## Ce que c'est

On augmente la probabilité des actions suivies d'un bon retour, et on baisse celle des actions suivies d'un mauvais retour. Ici on **monte** le gradient (on maximise J), à l'inverse de la descente de gradient sur une perte.

## Effets et impacts

- La variance est haute : un seul R bruyant fait osciller la politique.
- Un bonus de base, la baseline b, réduit ce bruit : on remplace R par R − b.
- Sans garde-fou, la politique peut renforcer un raccourci dangereux.
- À manipuler avec une récompense fidèle à la tâche.

## Exemple chiffré

Deux actions, politique softmax de logits θ = (0 ; 0), donc π = (0,5 ; 0,5). L'agent joue l'action 1 et reçoit R = 1. Pour une softmax, le gradient du log vaut « one-hot de l'action − π » :

$$
\nabla_\theta \log \pi(a_1) = (1 ; 0) - (0{,}5 ; 0{,}5) = (0{,}5\ ;\ -0{,}5)
$$

Avec un pas de 0,1 :

$$
\theta \leftarrow (0 ; 0) + 0{,}1 \times 1 \times (0{,}5\ ;\ -0{,}5) = (0{,}05\ ;\ -0{,}05) \quad\Longrightarrow\quad \pi(a_1) = \frac{e^{0{,}05}}{e^{0{,}05} + e^{-0{,}05}} \approx 0{,}525
$$

Avec une baseline b = 0,6, le même pas est multiplié par R − b = 0,4 au lieu de 1 : la mise à jour est plus douce.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(z)`** — Cette fonction est le répartiteur qui partage un gâteau entre plusieurs invités selon la force de leur appétit : elle reçoit une liste de scores, les logits θ de la politique, retranche d'abord le plus grand d'entre eux à chacun pour que l'exponentielle ne déborde jamais, prend l'exponentielle de chaque écart, puis divise chaque exponentielle par leur somme. Elle renvoie une liste de probabilités positives qui totalisent 1, la politique π elle-même : (0,5 ; 0,5) pour des logits nuls, et environ 0,525 pour la première action une fois les logits passés à (0,05 ; −0,05).

**`grad_log_pi(theta, action)`** — Celle-ci est le moniteur d'auto-école qui indique dans quel sens tourner chaque bouton pour rendre plus probable la manœuvre que l'élève vient de faire : elle reçoit les paramètres θ et l'indice de l'action jouée, calcule les probabilités par `softmax`, puis construit pour chaque action la différence entre 1 ou 0, selon qu'il s'agit ou non de l'action jouée, et sa probabilité. Elle renvoie ce vecteur, le gradient de log π(a) pour une politique softmax : (0,5 ; −0,5) quand on part de θ = (0 ; 0) et que l'agent a joué la première action.

**`pas_reinforce(theta, action, signal, pas)`** — Cette fonction est l'entraîneur qui récompense un geste réussi en l'encourageant d'autant plus que le résultat était bon : elle reçoit les paramètres θ, l'action jouée, un signal qui vaut le retour R dans REINFORCE ou l'avantage A dans la fiche 19b, et la taille du pas, demande le gradient à `grad_log_pi`, le multiplie par le pas et par le signal, et l'ajoute composante par composante aux paramètres. Elle renvoie les nouveaux paramètres, obtenus par une montée de gradient puisqu'on maximise l'objectif J : avec un retour de 1 et un pas de 0,1, θ passe de (0 ; 0) à (0,05 ; −0,05).

**`avantages(q, pi)`** — Celle-ci est le professeur qui note chaque élève par rapport à la moyenne de la classe plutôt que dans l'absolu : elle reçoit la liste des valeurs Q des actions et la liste de leurs probabilités sous la politique, calcule d'abord la valeur moyenne V(s), somme des Q pondérées par π, puis soustrait cette moyenne à chaque Q. Elle renvoie un couple formé de V et de la liste des avantages A(s, a) : pour Q = (5, 2, 2) et une politique uniforme, V vaut 3 et les avantages (2 ; −1 ; −1), ce qui sert à la fiche 19a.

**`main()`** — C'est le tableau de contrôle qui fait jouer les trois fiches de la famille : il applique d'abord un pas de REINFORCE de cette fiche et vérifie que θ vaut (0,05 ; −0,05) et que la première action passe à une probabilité de 0,525, puis calcule V = 3 et les avantages (2 ; −1 ; −1) de la fiche 19a. Il fait enfin trois pas avec des avantages de 1, 2 et −2 pour la fiche 19b, imprime 0,05, 0,10 et −0,10, et vérifie par des `assert` qu'un avantage double donne un pas double et qu'un avantage opposé inverse le sens, avant d'afficher la ligne de succès.

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
- [Étape 73 — Descente de gradient et LoRA](<../../12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md>)
- [Étape 78 — Synthèse : les mathématiques de l'IA agentique](<../../14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md>)
