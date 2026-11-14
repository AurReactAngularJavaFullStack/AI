# Fiche 17 — Divergence KL

> Image : `17_divergence_kl.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 50 — Précision, rappel, F1 et KL](<../../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>)

**Écart entre deux distributions**

## Formule

$$
D_{KL}(P \parallel Q) = \sum_{x} P(x) \times \log\left( \frac{P(x)}{Q(x)} \right)
$$

## Éléments

$$
P
$$

**P** : la distribution de référence.

$$
Q
$$

**Q** : la distribution comparée.

$$
x
$$

**x** : un événement possible.

$$
\frac{P(x)}{Q(x)}
$$

**P(x) / Q(x)** : l'écart local entre les deux distributions.

$$
\log
$$

**log** : le logarithme (naturel en général).

## Ce que c'est

La KL mesure l'information perdue quand on utilise Q à la place de P. Elle vaut zéro seulement si P et Q sont identiques. Elle n'est pas symétrique : KL(P‖Q) diffère de KL(Q‖P).

## Effets et impacts

- Elle sert en distillation, en alignement et pour comparer deux politiques.
- Une KL forte veut dire que le modèle s'éloigne de la référence.
- L'ordre P‖Q change le diagnostic : ne pas l'inverser sans le dire.

## Exemple chiffré

P = (0,5 ; 0,5) et Q = (0,9 ; 0,1) :

$$
D_{KL}(P \parallel Q) = 0{,}5 \ln\frac{0{,}5}{0{,}9} + 0{,}5 \ln\frac{0{,}5}{0{,}1} \approx -0{,}294 + 0{,}805 = 0{,}511
$$

$$
D_{KL}(Q \parallel P) = 0{,}9 \ln\frac{0{,}9}{0{,}5} + 0{,}1 \ln\frac{0{,}1}{0{,}5} \approx 0{,}529 - 0{,}161 = 0{,}368
$$

Deux nombres différents pour les mêmes distributions : la KL n'est pas une distance.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`kl(p, q)`** — Cette fonction se comporte comme un cartographe qui compare la carte officielle P à une carte de remplacement Q et compte, région par région, ce qu'on perd à se fier à la seconde : elle reçoit les deux distributions sous forme de listes, vérifie que chacune totalise 1 et lève une `ValueError` sinon, puis parcourt les événements deux à deux. Elle saute ceux que P juge impossibles, selon la convention 0 ln 0 = 0, renvoie aussitôt l'infini dès que Q déclare impossible un événement que P juge possible, et ajoute pour tous les autres P(x) × ln(P(x) / Q(x)) au total qu'elle renvoie à la fin : 0,511 pour P = (0,5 ; 0,5) face à Q = (0,9 ; 0,1), mais 0,368 dans l'autre sens, et exactement 0 quand on compare P à elle-même.

**`main()`** — C'est l'expert qui fait comparer les cartes dans les deux sens pour montrer que l'ordre compte : il calcule KL(P ‖ Q), KL(Q ‖ P) et KL(P ‖ P), imprime 0,511, 0,368 et 0,0, et vérifie ces trois valeurs par un `assert`. Il applique ensuite la fonction à la politique et à la référence de la fiche 17c, (0,7 ; 0,2 ; 0,1) contre (0,5 ; 0,3 ; 0,2), imprime 0,0851, puis vérifie que cette divergence est positive, qu'une distribution certaine comparée à une distribution uniforme donne aussi un nombre positif, et qu'une référence qui interdit un événement possible donne l'infini, avant d'imprimer la ligne de succès.

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
- [Étape 67 — Score de risque](<../../11-GardeFous/67-GardeFous-Formule-Score-de-Risque.md>)
- [Étape 78 — Synthèse : les mathématiques de l'IA agentique](<../../14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md>)
