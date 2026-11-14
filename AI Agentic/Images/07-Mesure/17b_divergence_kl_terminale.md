# Fiche 17b_divergence_kl_terminale — Divergence KL, niveau terminale

> Image : `17b_divergence_kl_terminale.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 50 — Précision, rappel, F1 et KL](<../../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>)

**La somme des écarts pondérés par P**

## Ce que montre l'image

Fiche de niveau terminale. Un graphique montre une distribution vraie P (trait plein) et une approximation Q (pointillés) décalée vers la droite. Une note insiste sur l'asymétrie, puis trois usages : régularisation, inférence variationnelle (ELBO), alignement des prédictions.

**Erreur dans l'image :** la somme est indexée de n = 1 à n, alors que les termes dépendent de x. Il faut lire « somme sur tous les x ».

**Ce que l'image ajoute à la fiche 17 :** l'unité, bits ou nats selon la base du logarithme, comme pour l'entropie.

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

Version terminale de la fiche 17. On insiste sur le quotient dans le logarithme et sur le fait que la somme est pondérée par P, pas par Q.

## Effets et impacts

- Si Q(x) = 0 là où P(x) > 0, la divergence devient infinie.
- Inverser P et Q change le diagnostic.

## Exemple chiffré

P = (0,5, 0,5) et Q = (0,9, 0,1), logarithme naturel.

$$
D_{\mathrm{KL}} = 0{,}5 \ln \frac{0{,}5}{0{,}9} + 0{,}5 \ln \frac{0{,}5}{0{,}1} \approx 0{,}5(-0{,}588) + 0{,}5(1{,}609) \approx 0{,}511
$$

Dans l'autre sens, KL(Q ‖ P) ≈ 0,368. Même paire, deux nombres.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`kl(p, q)`** — Cette fonction refait, terme après terme, le calcul qu'un élève de terminale mène à la calculatrice en remplissant un tableau à une ligne par valeur de x : elle reçoit les distributions P et Q sous forme de listes, vérifie que chacune a une somme égale à 1 et lève une `ValueError` sinon, puis, pour chaque x, saute la ligne si P(x) vaut 0, renvoie l'infini si Q(x) vaut 0 alors que P(x) est positive, et sinon ajoute P(x) × ln(P(x) / Q(x)), pondéré par P et non par Q. Le logarithme utilisé est le logarithme naturel, si bien que le résultat renvoyé s'exprime en nats : pour P = (0,5 ; 0,5) et Q = (0,9 ; 0,1), le premier terme est négatif, 0,5 × (−0,588), le second positif, 0,5 × 1,609, et leur somme vaut 0,511.

**`main()`** — C'est le corrigé de l'exercice, qui vérifie le résultat dans les deux sens comme le demande la note de l'image : il calcule la divergence de P vers Q, 0,511, puis celle de Q vers P, 0,368, et celle de P vers elle-même, 0,0, les imprime et les vérifie par un `assert`. Il ajoute l'exemple de la fiche 17c, une politique (0,7 ; 0,2 ; 0,1) comparée à une référence (0,5 ; 0,3 ; 0,2), qui donne 0,0851, puis deux cas limites, dont celui où Q interdit un événement possible et où la divergence devient infinie, avant d'imprimer la ligne de succès.

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
