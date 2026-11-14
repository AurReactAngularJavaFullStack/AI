# Fiche 09f_retour_attendu — Retour attendu

> Image : `09f_retour_attendu.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**Ce que l'agent maximise**

## Ce que montre l'image

Affiche « Retour attendu, objectif des agents IA ». La formule Gₜ, somme pour k de 0 à l'infini de γᵏ Rₜ₊ₖ₊₁, avec γ compris entre 0 et 1 exclu, puis quatre lignes illustrées : ce que c'est (somme pondérée des récompenses futures, avec une courbe de poids qui décroît), conséquences (c'est ce que l'agent maximise), effets (base des fonctions de valeur), impacts (comportements optimaux).

**Ce que l'image ajoute :** la courbe des poids γᵏ : avec γ = 0,9, une récompense reçue dans 10 pas ne pèse plus que 0,35.

**Lien :** la relation Gₜ = Rₜ₊₁ + γ Gₜ₊₁ est démontrée dans `Demonstrations/06-Decision/09_equation_bellman.md`.

## Formule

$$
G_t = \sum_{k=0}^{\infty} \gamma^{k} R_{t+k+1}
$$

## Éléments

$$
G_t
$$

**Gₜ** : le retour cumulé actualisé à partir du temps t.

$$
k
$$

**k** : le nombre de pas dans le futur.

$$
0 \le \gamma < 1
$$

**γ (gamma)** : l'actualisation. L'affiche la borne strictement sous 1.

$$
R_{t+k+1}
$$

**Rₜ₊ₖ₊₁** : la récompense reçue k + 1 pas plus tard.

$$
V^{\pi}(s) = \mathbb{E}_{\pi}\left[ G_t \mid S_t = s \right]
$$

**Lien avec la fiche 09d** : Vπ(s) est l'espérance de Gₜ quand on part de s.

## Ce que c'est

L'objectif d'un agent, au sens de l'apprentissage par renforcement, est de maximiser ce retour. Ce n'est pas de maximiser la prochaine récompense seule.

## Effets et impacts

- γ = 0 : Gₜ = Rₜ₊₁, seulement le pas suivant.
- γ = 0,9 : une récompense dans 10 pas ne vaut plus que 0,9¹⁰ ≈ 0,35 fois sa valeur.
- Une récompense rare et lointaine disparaît si γ est trop petit, ou domine le court terme si γ est trop proche de 1.

## Exemple chiffré

Récompenses 1, puis 1, puis 1, et γ = 0,5. À partir de t :

$$
G = 1 + 0{,}5 \times 1 + 0{,}25 \times 1 = 1{,}75
$$

Sans actualisation, les trois 1 vaudraient 3. γ a retiré 1,25.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`valeur_action(recompense, gamma, valeur_suivante)`** — Cette fonction est un aiguilleur qui ne regarde qu'un pas devant lui et résume tout le reste du trajet par un seul chiffre : elle reçoit la récompense du prochain pas, le facteur γ et la valeur de l'état d'arrivée, qui vaut le retour moyen qu'on peut encore espérer à partir de là, puis renvoie la récompense plus γ fois cette valeur, la forme courte Gₜ = Rₜ₊₁ + γ Gₜ₊₁ de la somme infinie de cette fiche. Dans le programme, elle sert aux comparaisons des fiches 09, 09a et 09e, par exemple 11 contre 5 pour les deux outils de la fiche 09 quand γ = 0,9.

**`point_fixe(recompense, gamma, tours)`** — Celle-ci calcule le retour d'un agent qui toucherait exactement la même récompense à chaque pas, pour toujours, comme un abonné qui recevrait chaque matin le même journal : elle reçoit cette récompense, le facteur γ et un nombre de tours, deux cents par défaut, part de zéro et applique la règle V ← R + γ V à chaque tour, ce qui revient à sommer R, γ R, γ² R et ainsi de suite. Grâce à γ inférieur à 1, la série géométrique converge, et la fonction renvoie sa somme R / (1 − γ), soit 4 pour R = 2 et γ = 0,5, l'exemple des fiches 09b à 09d.

**`retour(recompenses, gamma)`** — Voici la fonction de cette fiche, qui fait rouler une boule de neige à reculons depuis la fin de l'épisode : elle reçoit la liste des récompenses dans l'ordre où elles arrivent et le facteur γ, part d'un retour nul, puis, pour chaque récompense lue de la dernière à la première, rétrécit la boule déjà formée en la multipliant par γ et y colle la récompense du pas, selon G ← R + γ G. Sur les récompenses 1, 1, 1 avec γ = 0,5, la boule vaut 1, puis 1,5, puis 1,75, nombre que la fonction renvoie, alors qu'avec γ = 1, sans actualisation, elle renverrait 3 ; aucun γᵏ n'est jamais calculé explicitement.

**`main()`** — C'est le metteur en scène qui fait jouer toutes les fiches de la famille Bellman avant d'en venir à celle-ci : il compare les outils A et B de la fiche 09 (11 et 5 avec γ = 0,9, 4 et 5 avec γ = 0,2), le bonbon et le gâteau de la fiche 09a, l'état qui boucle des fiches 09b à 09d et la meilleure action de la fiche 09e, puis demande à `retour` le total des trois récompenses de 1 avec γ = 0,5. Chaque nombre est imprimé puis vérifié par un `assert`, en particulier le retour, qui doit valoir exactement 1,75, et la ligne de succès n'apparaît que si toutes les vérifications passent.

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
