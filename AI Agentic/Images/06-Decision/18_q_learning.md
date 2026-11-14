# Fiche 18 — Q-learning

> Image : `18_q_learning.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**Corriger la valeur d'une action**

## Formule

$$
Q(s, a) \leftarrow Q(s, a) + \alpha \left[ r + \gamma \max_{a'} Q(s', a') - Q(s, a) \right]
$$

## Éléments

$$
Q(s, a)
$$

**Q(s, a)** : la valeur estimée de l'action a dans l'état s.

$$
r
$$

**r** : la récompense reçue.

$$
\gamma
$$

**γ (gamma)** : l'actualisation de l'avenir, entre 0 et 1.

$$
\max_{a'} Q(s', a')
$$

**max Q(s′, a′)** : la meilleure valeur disponible dans l'état suivant.

$$
\alpha \in\ ]0, 1]
$$

**α (alpha)** : le pas d'apprentissage.

$$
r + \gamma \max_{a'} Q(s', a') - Q(s, a)
$$

**Le crochet** : l'erreur de différence temporelle (TD), l'écart entre la cible et l'estimation actuelle.

$$
\leftarrow
$$

**←** : « devient ». C'est une mise à jour, pas une égalité.

## Ce que c'est

On rapproche l'estimation actuelle de la cible r + γ max Q. L'agent apprend sans connaître le modèle de transition : il lui suffit d'essayer et d'observer.

## Effets et impacts

- α trop grand rend l'estimation instable.
- γ trop grand fait poursuivre des gains lointains incertains.
- Une récompense mal définie apprend le mauvais comportement.
- Q-learning suppose des essais répétés, rares tels quels pour un LLM en production.

## Exemple chiffré

Estimation actuelle Q = 2, récompense r = 1, meilleure valeur suivante 5, γ = 0,9 et α = 0,5 :

$$
\text{cible} = 1 + 0{,}9 \times 5 = 5{,}5, \qquad \text{erreur TD} = 5{,}5 - 2 = 3{,}5
$$

$$
Q \leftarrow 2 + 0{,}5 \times 3{,}5 = 3{,}75
$$

L'estimation fait la moitié du chemin vers la cible, parce que α = 0,5.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`maj_q(q, r, gamma, max_q_suivant, alpha)`** — Cette fonction se conduit comme un navigateur qui corrige son estime après chaque relevé de position : elle reçoit l'estimation actuelle Q de l'action, la récompense r qui vient d'être reçue, le facteur γ, la meilleure valeur estimée dans l'état suivant et le pas d'apprentissage α, et refuse d'abord tout pas qui ne serait pas dans ]0, 1] en levant une `ValueError`. Elle calcule ensuite l'erreur de différence temporelle, la cible r + γ × max Q(s′, a′) diminuée de l'estimation actuelle, puis déplace Q d'une fraction α de cette erreur ; elle renvoie un couple formé de la nouvelle estimation et de l'erreur, par exemple 3,75 et 3,5 pour Q = 2, r = 1, une valeur suivante de 5, γ = 0,9 et α = 0,5.

**`main()`** — C'est le carnet de bord où l'on note chaque correction : il applique d'abord `maj_q` à l'exemple de cette fiche, imprime la cible 5,5, l'erreur 3,5 et la nouvelle estimation 3,75, puis vérifie ces nombres par un `assert`. Il passe ensuite à l'exemple des fiches 18a et 18b, où Q = 1, r = 0, γ = 1, une valeur suivante de 3 et α = 0,5 donnent une erreur de 2 et une estimation qui passe à 2, et il termine en répétant cinquante fois la même expérience à partir de Q = 0, pour vérifier que l'estimation finit collée à la cible 5,5 à un milliardième près, avant d'imprimer la ligne de succès.

```python
"""Fiches 18, 18a, 18b — Q-learning : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def maj_q(q: float, r: float, gamma: float, max_q_suivant: float, alpha: float) -> tuple[float, float]:
    """Q ← Q + α [r + γ max Q(s′, a′) − Q] ; renvoie aussi l'erreur de différence temporelle."""
    if not 0 < alpha <= 1:
        raise ValueError("α doit être dans ]0, 1]")
    erreur = r + gamma * max_q_suivant - q
    return q + alpha * erreur, erreur


def main() -> None:
    q, err = maj_q(2, 1, 0.9, 5, 0.5)                       # fiche 18
    print(f"fiche 18 : cible = {2 + err:.1f}, erreur TD = {err:.1f}, Q devient {q}")
    assert math.isclose(err, 3.5) and q == 3.75
    q2, err2 = maj_q(1, 0, 1, 3, 0.5)                       # fiches 18a et 18b
    print(f"fiches 18a/18b : erreur TD = {err2}, Q devient {q2}")
    assert err2 == 2 and q2 == 2
    q3 = 0.0
    for _ in range(50):                                     # répéter la même expérience : Q converge vers la cible
        q3, _ = maj_q(q3, 1, 0.9, 5, 0.5)
    assert math.isclose(q3, 5.5, abs_tol=1e-9)
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
fiche 18 : cible = 5.5, erreur TD = 3.5, Q devient 3.75
fiches 18a/18b : erreur TD = 2, Q devient 2.0
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`maj_q` applique une mise à jour du Q-learning. Elle refuse un pas α hors de l'intervalle ]0, 1], puis calcule l'erreur de différence temporelle, le crochet de la formule : la cible r + γ × la meilleure valeur estimée dans l'état suivant, moins l'estimation actuelle. Elle déplace enfin l'estimation d'une fraction α de cette erreur, et renvoie la nouvelle valeur avec l'erreur, pour qu'on puisse suivre l'apprentissage.

`main` vérifie les exemples. Fiche 18 : avec Q = 2, r = 1, γ = 0,9, une meilleure valeur suivante de 5 et α = 0,5, la cible vaut 5,5, l'erreur 3,5, et Q passe à 3,75, à mi-chemin de la cible. Fiches 18a et 18b : avec Q = 1, r = 0, γ = 1, une meilleure valeur suivante de 3 et α = 0,5, l'erreur vaut 2 et Q passe à 2. Le programme répète enfin cinquante fois la même expérience : l'estimation converge vers la cible 5,5, ce qui montre que la règle n'a besoin d'aucun modèle des transitions, seulement d'essais répétés.

## Squelette algorithmique

```text
ALGORITHME QLearning
ENTRÉES : environnement, α, γ, ε (exploration), nombre d'épisodes
SORTIE  : la table Q(s, a)

  Q ← 0 pour tout couple (s, a)
  POUR CHAQUE épisode FAIRE
      s ← état initial
      TANT QUE s n'est pas terminal FAIRE
          a ← action au hasard avec probabilité ε, SINON argmaxₐ Q(s, a)
          jouer a ; observer r et s′
          Q(s, a) ← Q(s, a) + α × [r + γ × maxₐ′ Q(s′, a′) − Q(s, a)]
          s ← s′
      FIN TANT QUE
  FIN POUR
  RETOURNER Q
```

**Complexité.** Une mise à jour coûte O(|A|) pour trouver le maximum sur les actions suivantes. La mémoire est O(|S| × |A|) pour la table, ce qui devient impossible quand les états sont des textes : on remplace alors la table par un réseau, et la convergence n'est plus garantie.

**Du squelette au code.** La ligne de mise à jour est `maj_q`, et la boucle de cinquante répétitions de `main` joue le rôle des épisodes, sur un seul couple (s, a).

## Dans le cours

- [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)
- [Étape 78 — Synthèse : les mathématiques de l'IA agentique](<../../14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md>)
