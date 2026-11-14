# Fiche 17a_divergence_kl_affiche — Divergence KL, affiche

> Image : `17a_divergence_kl_affiche.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 50 — Précision, rappel, F1 et KL](<../../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>)

**L'écart entre deux distributions**

## Ce que montre l'image

Affiche « Divergence KL (Kullback-Leibler) ». La formule, avec « x ∈ X » écrit au-dessus et au-dessous du Σ (une fois suffit). Deux définitions (la différence entre P et Q ; l'information perdue quand on approxime P par Q) et une propriété : la KL est toujours positive ou nulle, et nulle si et seulement si P = Q. Quatre usages : régularisation, inférence variationnelle, guide de l'apprentissage, alignement des prédictions. En bas : la KL n'est pas symétrique et n'est pas une distance.

**À lire avec prudence :** en inférence variationnelle, on minimise en général KL(Q ‖ P), c'est-à-dire l'autre sens que la formule affichée. L'asymétrie compte.

## Formule

$$
D_{\mathrm{KL}}(P \,\|\, Q) = \sum_x P(x)\, \log \frac{P(x)}{Q(x)}
$$

## Éléments

$$
P
$$

**P** : la distribution de référence.

$$
Q
$$

**Q** : la distribution qu'on lui compare.

$$
\frac{P(x)}{Q(x)}
$$

**P(x) / Q(x)** : l'écart local.

$$
D_{KL}(P \parallel Q) \ne D_{KL}(Q \parallel P)
$$

**L'ordre compte** : la KL n'est pas symétrique.

## Ce que c'est

Affiche de la fiche 17. KL vaut 0 seulement si P et Q sont identiques.

## Effets et impacts

- Elle sert à comparer une politique à une référence, et deux modèles entre eux.
- Elle n'est pas une distance : elle n'est pas symétrique.

## Exemple chiffré

P = (0,5, 0,5) et Q = (0,9, 0,1), logarithme naturel.

$$
D_{\mathrm{KL}} = 0{,}5 \ln \frac{0{,}5}{0{,}9} + 0{,}5 \ln \frac{0{,}5}{0{,}1} \approx 0{,}5(-0{,}588) + 0{,}5(1{,}609) \approx 0{,}511
$$

Dans l'autre sens, KL(Q ‖ P) ≈ 0,368. Même paire, deux nombres.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`kl(p, q)`** — Cette fonction est le traducteur scrupuleux qui mesure ce qui se perd quand on remplace un texte original P par une version approchée Q, mot à mot : elle reçoit les deux distributions sous forme de listes de même longueur, refuse par une `ValueError` toute liste dont la somme ne vaut pas 1, puis passe en revue les événements par paires. Un événement absent de l'original ne coûte rien, selon la convention 0 ln 0 = 0 ; un événement présent dans l'original mais que la traduction déclare impossible rend la perte infinie, et la fonction renvoie aussitôt l'infini ; pour tous les autres, elle ajoute P(x) × ln(P(x) / Q(x)) au total, qu'elle renvoie à la fin, toujours positif ou nul comme le dit l'affiche : 0,511 pour P = (0,5 ; 0,5) et Q = (0,9 ; 0,1).

**`main()`** — C'est l'atelier où l'on vérifie, chiffres en main, les trois promesses de l'affiche : il calcule la divergence de P vers Q et celle de Q vers P, imprime 0,511 et 0,368 pour montrer que la KL n'est pas symétrique, puis la divergence de P avec elle-même, 0,0, puisqu'elle n'est nulle que si les deux distributions sont identiques, et contrôle les trois nombres par un `assert`. Il calcule enfin l'exemple de la fiche 17c, 0,0851, vérifie qu'il est positif, qu'un cas certain comparé au cas uniforme l'est aussi, et qu'une référence qui interdit un événement possible donne l'infini, puis imprime la ligne de succès.

```python
"""Fiches 17, 17a à 17c — divergence KL : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def kl(p: list[float], q: list[float]) -> float:
    """D_KL(P ‖ Q) = Σ P(x) ln(P(x) / Q(x)) ; infini si Q(x) = 0 là où P(x) > 0."""
    if not (math.isclose(sum(p), 1) and math.isclose(sum(q), 1)):
        raise ValueError("P et Q doivent être des distributions")
    total = 0.0
    for px, qx in zip(p, q):
        if px == 0:
            continue                       # convention 0 ln 0 = 0
        if qx == 0:
            return math.inf
        total += px * math.log(px / qx)
    return total


def main() -> None:
    P, Q = [0.5, 0.5], [0.9, 0.1]
    pq, qp = kl(P, Q), kl(Q, P)
    print(f"KL(P ‖ Q) = {pq:.3f}   KL(Q ‖ P) = {qp:.3f}   KL(P ‖ P) = {kl(P, P)}")
    assert round(pq, 3) == 0.511 and round(qp, 3) == 0.368 and kl(P, P) == 0
    pi_theta, pi_ref = [0.7, 0.2, 0.1], [0.5, 0.3, 0.2]      # fiche 17c : politique et référence
    print(f"fiche 17c : KL(πθ ‖ πref) = {kl(pi_theta, pi_ref):.4f}")
    assert kl(pi_theta, pi_ref) > 0 and kl([1.0, 0.0], [0.5, 0.5]) > 0 and kl([0.5, 0.5], [1.0, 0.0]) == math.inf
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
KL(P ‖ Q) = 0.511   KL(Q ‖ P) = 0.368   KL(P ‖ P) = 0.0
fiche 17c : KL(πθ ‖ πref) = 0.0851
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`kl` vérifie d'abord que P et Q sont bien des distributions, puis parcourt les événements un par un. Un événement de probabilité nulle sous P ne compte pas, selon la convention 0 ln 0 = 0 ; un événement possible sous P mais impossible sous Q rend la divergence infinie, parce que Q affirme impossible ce que la référence considère possible, et la fonction le renvoie immédiatement. Pour les autres événements, elle ajoute P(x) multiplié par le logarithme du rapport P(x) / Q(x), l'écart local de la fiche.

`main` vérifie l'exemple des fiches 17, 17a et 17b : avec P = (0,5 ; 0,5) et Q = (0,9 ; 0,1), KL(P ‖ Q) vaut 0,511 et KL(Q ‖ P) vaut 0,368, deux nombres différents pour la même paire, ce qui montre que la KL n'est pas symétrique ; et la divergence d'une distribution avec elle-même est nulle. Le programme applique enfin la formule à la situation de la fiche 17c, une politique en cours d'apprentissage comparée à sa politique de référence, et vérifie qu'une référence qui interdit une action possible donne une pénalité infinie.

## Squelette algorithmique

```text
ALGORITHME DivergenceKL
ENTRÉES : distributions P et Q sur les mêmes événements
SORTIE  : D_KL(P ‖ Q) ≥ 0, éventuellement +∞

  total ← 0
  POUR CHAQUE événement x FAIRE
      SI P(x) = 0 ALORS passer
      SI Q(x) = 0 ALORS RETOURNER +∞
      total ← total + P(x) × ln(P(x) / Q(x))
  FIN POUR
  RETOURNER total

USAGE EN ALIGNEMENT (fiche 17c) : objectif ← récompense − β × KL(πθ ‖ πref), pour ne pas trop s'éloigner de la référence.
```

**Complexité.** Une passe sur les événements : O(n). Pour un modèle de langage, n est la taille du vocabulaire, et la KL se calcule à chaque position de la séquence.

**Du squelette au code.** Les deux tests et l'accumulation sont, dans l'ordre, le `continue`, le `return math.inf` et la ligne `total += …` de `kl`.

## Dans le cours

- [Étape 50 — Précision, rappel, F1 et KL](<../../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>)
- [Fiche 17 — Divergence KL](<17_divergence_kl.md>)
