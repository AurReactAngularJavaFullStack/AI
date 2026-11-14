# Fiche 18a_q_learning_affiche — Q-learning, affiche

> Image : `18a_q_learning_affiche.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**Corriger Q après chaque essai**

## Ce que montre l'image

Affiche « Mise à jour Q-learning ». La règle complète, puis cinq pastilles : Q (valeur action-état), α (taux d'apprentissage), r (récompense), γ (actualisation), max (meilleure valeur future). Deux blocs : ce que c'est (une règle par différence temporelle, qui combine la récompense immédiate et la meilleure estimation future) et trois usages (apprendre une politique par essais et erreurs, s'améliorer avec l'expérience, décisions séquentielles).

**Ce que l'image ajoute à la fiche 18 :** le nom de la méthode, différence temporelle : on corrige Q par l'écart entre la cible r + γ max Q(s′, ·) et l'estimation actuelle.

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

Affiche de la fiche 18. On rapproche l'estimation de la cible r + γ max Q, sans connaître le modèle de transition.

## Effets et impacts

- α trop grand rend Q instable.
- Cette règle suppose des essais répétés. Elle ne s'applique pas telle quelle à un appel de LLM.

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

**`maj_q(q, r, gamma, max_q_suivant, alpha)`** — Cette fonction est l'apprenti cuisinier qui goûte sa sauce après chaque essai et rectifie l'assaisonnement d'un cran, sans jamais tout refaire d'un coup : elle reçoit l'estimation actuelle Q, la récompense r, le facteur γ, la meilleure valeur estimée dans l'état suivant et le pas α, vérifie que ce pas tombe bien dans ]0, 1] et lève une `ValueError` sinon. Elle forme alors la cible r + γ × max Q, en retire l'estimation actuelle pour obtenir l'erreur de différence temporelle, le crochet de l'affiche, puis avance Q d'une fraction α de cette erreur ; elle renvoie la nouvelle valeur et l'erreur, soit 2 et 2 dans l'exemple de cette fiche, où Q = 1, r = 0, γ = 1, une valeur suivante de 3 et α = 0,5.

**`main()`** — C'est la séance de dégustation où l'on vérifie chaque rectification : il traite d'abord l'exemple de la fiche 18, où Q = 2 devient 3,75 après une erreur de 3,5, puis celui de cette affiche, imprime l'erreur 2 et la nouvelle estimation 2,0, et contrôle les deux résultats par des `assert`. Il répète ensuite cinquante fois l'expérience de la fiche 18 en partant de zéro, chaque passage faisant la moitié du chemin restant, et vérifie que l'estimation finit à 5,5, la cible, avant d'imprimer que toutes les vérifications sont passées.

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
