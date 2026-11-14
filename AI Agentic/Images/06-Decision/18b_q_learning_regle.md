# Fiche 18b_q_learning_regle — Q-learning, la règle

> Image : `18b_q_learning_regle.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**La même mise à jour, relue comme une règle d'apprentissage**

## Ce que montre l'image

Fiche « Apprentissage par renforcement : la règle Q-learning ». Elle précise les domaines, 0 < α ≤ 1 et 0 ≤ γ < 1, et définit chaque lettre : s, a, s′ et a′. L'encadré « Ce que c'est » décompose la mise à jour en trois morceaux : la récompense reçue, la valeur anticipée des meilleurs choix futurs, et l'erreur entre cette cible et l'estimation actuelle. L'affiche insiste : l'agent apprend sans modèle de l'environnement.

**Ce que l'image ajoute à la fiche 18 :** l'effet de α. Grand, l'agent apprend vite mais devient instable ; la démonstration 2 de `Demonstrations/06-Decision/18_q_learning.md` le chiffre.

## Formule

$$
Q(s, a) \leftarrow Q(s, a) + \alpha \big[ r + \gamma \max_{a'} Q(s', a') - Q(s, a) \big]
$$

## Éléments

$$
Q(s, a)
$$

**Q(s, a)** : la valeur estimée de l'action a dans s.

$$
r
$$

**r** : la récompense reçue.

$$
\gamma \max_{a'} Q(s', a')
$$

**γ max Q(s′, a′)** : la meilleure valeur estimée dans l'état suivant, actualisée par γ (gamma).

$$
\alpha \in\ ]0, 1]
$$

**α (alpha)** : le pas, entre 0 et 1.

$$
r + \gamma \max_{a'} Q(s', a') - Q(s, a)
$$

**Le crochet** : l'erreur, cible moins estimation.

## Ce que c'est

Même règle que la fiche 18. Le terme entre crochets est une différence temporelle : ce qu'on vient de voir, moins ce qu'on croyait.

## Effets et impacts

- γ trop grand fait poursuivre des gains lointains et incertains.
- Une récompense mal définie apprend le mauvais comportement.

## Exemple chiffré

Q = 1, r = 0, γ = 1, max Q(s') = 3, α = 0,5.

Cible = 0 + 3 = 3. Erreur = 2.

$$
Q \leftarrow 1 + 0{,}5 \times 2 = 2
$$

On a fait la moitié du chemin vers 3, pas tout le chemin.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`maj_q(q, r, gamma, max_q_suivant, alpha)`** — Cette fonction est un élève qui compare la note qu'il espérait à celle qu'il vient de recevoir et ne révise son opinion de lui-même que d'une partie de l'écart : elle reçoit l'estimation actuelle Q, la récompense r, le facteur γ, la meilleure valeur anticipée dans l'état suivant et le pas α, puis contrôle le seul domaine qu'elle impose, 0 < α ≤ 1, en levant une `ValueError` s'il n'est pas respecté ; γ, lui, n'est pas vérifié, ce qui laisse passer le γ = 1 de l'exemple. Elle calcule l'erreur, ce qu'on vient de voir moins ce qu'on croyait, déplace Q d'une fraction α de cet écart, et renvoie la nouvelle estimation avec l'erreur : 2 et 2 pour Q = 1, r = 0, une valeur suivante de 3 et α = 0,5, alors qu'avec α = 1 elle sauterait d'un coup sur la cible.

**`main()`** — C'est le relevé de notes qui suit l'élève sur plusieurs contrôles : il vérifie d'abord l'exemple de la fiche 18, où Q = 2 passe à 3,75 avec une erreur de 3,5, puis celui de cette fiche, imprime l'erreur 2 et la nouvelle valeur 2,0, et contrôle chaque nombre par un `assert`. Il fait enfin repasser cinquante fois la même épreuve, une récompense de 1, une valeur suivante de 5, γ = 0,9 et α = 0,5, à partir d'une estimation nulle, et vérifie que celle-ci a rejoint la cible 5,5 sans aucun modèle de l'environnement, avant d'imprimer la ligne de succès.

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
- [Fiche 18 — Q-learning](<18_q_learning.md>)
