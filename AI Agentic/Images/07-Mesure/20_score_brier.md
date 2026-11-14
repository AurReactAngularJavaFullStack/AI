# Fiche 20 — Score de Brier

> Image : `20_score_brier.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 51 — Spécificité, NPV, AUC](<../../10-Evaluation/51-Specificite-NPV-AUC.md>)

**La confiance annoncée est-elle juste**

## Formule

$$
BS = \frac{1}{N} \sum_{i=1}^{N} (p_i - y_i)^2
$$

## Éléments

$$
N
$$

**N** : le nombre de prédictions.

$$
p_i \in [0, 1]
$$

**pᵢ** : la probabilité annoncée.

$$
y_i \in \{0, 1\}
$$

**yᵢ** : l'issue réelle, 0 ou 1.

$$
(p_i - y_i)^2
$$

**(pᵢ − yᵢ)²** : l'erreur au carré de la prédiction i.

$$
BS
$$

**BS** : la moyenne de ces erreurs. Plus bas est meilleur ; 0 est parfait.

## Ce que c'est

Brier mesure l'écart entre la confiance annoncée et la fréquence réelle. Un modèle sûr et souvent faux est mal calibré, et Brier le punit fort, car l'erreur est au carré.

## Effets et impacts

- Une confiance calibrée dit à l'agent quand vérifier, s'abstenir ou escalader.
- Un score bas n'est pas une exactitude de réponse.
- « 95 % » non calibré ne doit pas déclencher une action irréversible.

## Exemple chiffré

Trois prédictions, confiances 0,9 ; 0,8 ; 0,3, issues réelles 1 ; 0 ; 0 :

$$
BS = \frac{(0{,}9 - 1)^2 + (0{,}8 - 0)^2 + (0{,}3 - 0)^2}{3} = \frac{0{,}01 + 0{,}64 + 0{,}09}{3} \approx 0{,}247
$$

Annoncer 0,5 à chaque fois donnerait 0,25. Le 0,8 sûr de lui et faux coûte à lui seul 0,64 : presque tout le score.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`brier(probas, issues)`** — Cette fonction est l'examinateur d'un concours de météorologues qui, une fois la semaine passée, ressort les bulletins et les confronte au ciel réel : elle reçoit la liste des confiances annoncées et la liste des issues observées, refuse par une `ValueError` deux listes de longueurs différentes ou vides, puis par une seconde `ValueError` toute confiance hors de [0, 1] ou toute issue qui ne vaut ni 0 ni 1. Elle élève ensuite au carré, pour chaque prédiction, l'écart entre la confiance annoncée et ce qui s'est passé, ce qui punit lourdement l'assurance déplacée, et renvoie la moyenne de ces carrés : environ 0,2467 pour les confiances 0,9, 0,8 et 0,3 face aux issues 1, 0 et 0, avec 0 pour un prédicteur parfait et 1 pour un prédicteur toujours sûr et toujours faux.

**`main()`** — C'est la remise des prix où l'on compare le météorologue audacieux au prudent : il calcule le score de l'exemple de la fiche, 0,2467, puis celui d'un prévisionniste qui annoncerait 0,5 à chaque fois sur les mêmes issues, 0,25, et la part apportée par la seule deuxième prédiction, sûre à 80 % et fausse, 0,2133. Il vérifie ces valeurs par un `assert`, contrôle aussi les deux bornes, 0 pour un prédicteur parfait et 1 pour un prédicteur toujours à contre-sens, puis imprime la ligne qui annonce que toutes les vérifications sont passées.

```python
"""Fiche 20 — score de Brier : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def brier(probas: list[float], issues: list[int]) -> float:
    """BS = (1/N) Σ (pᵢ − yᵢ)², avec pᵢ ∈ [0, 1] et yᵢ ∈ {0, 1}."""
    if len(probas) != len(issues) or not probas:
        raise ValueError("autant de probabilités que d'issues, et au moins une")
    if any(not 0 <= p <= 1 for p in probas) or any(y not in (0, 1) for y in issues):
        raise ValueError("p dans [0, 1] et y dans {0, 1}")
    return sum((p - y) ** 2 for p, y in zip(probas, issues)) / len(probas)


def main() -> None:
    bs = brier([0.9, 0.8, 0.3], [1, 0, 0])
    prudent = brier([0.5, 0.5, 0.5], [1, 0, 0])
    print(f"BS = {bs:.4f}   toujours 0,5 : {prudent:.2f}   part de la 2e prédiction : {(0.8 - 0) ** 2 / 3:.4f}")
    assert round(bs, 4) == 0.2467 and prudent == 0.25
    assert brier([1, 0], [1, 0]) == 0 and brier([0, 1], [1, 0]) == 1
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
BS = 0.2467   toujours 0,5 : 0.25   part de la 2e prédiction : 0.2133
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`brier` vérifie d'abord qu'il y a autant de probabilités annoncées que d'issues observées, que chaque probabilité est entre 0 et 1 et que chaque issue vaut 0 ou 1, puis fait la moyenne des carrés des écarts entre la confiance annoncée et ce qui s'est réellement passé. L'élévation au carré a deux effets : elle rend tous les écarts positifs, et elle punit beaucoup plus une erreur faite avec assurance qu'une erreur prudente.

`main` vérifie l'exemple de la fiche : trois prédictions annoncées à 0,9, 0,8 et 0,3, pour des issues 1, 0 et 0, donnent un score de 0,2467. Annoncer 0,5 à chaque fois donnerait 0,25, à peine plus, et la deuxième prédiction, sûre d'elle à 80 % et fausse, apporte à elle seule 0,2133 au score. Les deux derniers `assert` vérifient les bornes : un prédicteur parfait obtient 0, un prédicteur toujours sûr et toujours faux obtient 1.

## Squelette algorithmique

```text
ALGORITHME MesurerLaCalibration
ENTRÉES : confiances annoncées p₁ … p_N, issues y₁ … y_N ∈ {0, 1}
SORTIE  : le score de Brier, et un tableau de calibration

  BS ← (1/N) × Σᵢ (pᵢ − yᵢ)²
  POUR CHAQUE tranche de confiance [0 ; 0,1[, [0,1 ; 0,2[, … FAIRE
      fréquence ← proportion de yᵢ = 1 parmi les prédictions de la tranche
      comparer fréquence et confiance moyenne de la tranche      (calibré si elles sont proches)
  FIN POUR
  RETOURNER BS, tableau
```

**Complexité.** Une passe sur les N prédictions pour le score, une seconde pour ranger les prédictions dans les tranches : O(N) en temps, O(nombre de tranches) en mémoire pour le tableau.

**Du squelette au code.** La première ligne est la fonction `brier`. Le tableau de calibration n'est pas dans le programme : il se construit avec les mêmes données en groupant les prédictions par tranche.

## Dans le cours

- [Étape 51 — Spécificité, NPV, AUC](<../../10-Evaluation/51-Specificite-NPV-AUC.md>)
- [Étape 78 — Synthèse : les mathématiques de l'IA agentique](<../../14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md>)
