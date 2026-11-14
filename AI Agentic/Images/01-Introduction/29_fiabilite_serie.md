# Fiche 29 — Fiabilité en série

> Image : `29_fiabilite_serie.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)

**Une chaîne d'outils se fragilise**

## Formule

$$
P(\text{succès}) = p_1 \times p_2 \times \dots \times p_n = \prod_{i=1}^{n} p_i
$$

## Éléments

$$
p_i \in [0, 1]
$$

**pᵢ** : la chance que l'étape i réussisse.

$$
n
$$

**n** : le nombre d'étapes toutes nécessaires.

$$
\prod
$$

**Le produit** : chaque maillon multiplie le précédent.

$$
P(\text{succès})
$$

**P(succès)** : la chance que toute la chaîne réussisse.

## Ce que c'est

Si chaque étape doit réussir, la fiabilité globale est le produit des fiabilités. Cinq étapes à 0,9 donnent environ 0,59. La démonstration complète, avec les bornes sans indépendance, est à l'étape 1.

## Effets et impacts

- Un agent à beaucoup d'outils peut échouer souvent même si chaque outil marche bien.
- Raccourcir la chaîne, vérifier tôt et prévoir une reprise augmentent le succès (étape 11).
- La formule suppose des étapes indépendantes et toutes nécessaires : ce n'est pas toujours vrai.

## Exemple chiffré

$$
0{,}9^5 \approx 0{,}590 \qquad\qquad 0{,}99^5 \approx 0{,}951
$$

Passer chaque étape de 90 % à 99 % fait remonter la chaîne de 59 % à 95 %. Avec deux relances par étape, une étape à 0,9 atteint 0,999 (étape 11), et la chaîne de cinq étapes 0,995.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`fiabilite(probas)`** — Cette fonction raisonne comme un alpiniste qui regarde sa cordée : il suffit qu'un seul mousqueton cède pour que toute l'ascension échoue, si bien que la solidité de l'ensemble est le produit des solidités de chaque prise. Elle reçoit la liste des probabilités de réussite des étapes, lève `ValueError` si la liste est vide ou si l'une des valeurs sort de [0, 1], puis rend leur produit calculé par `math.prod`. C'est la formule de la fiche, valable pour des étapes indépendantes et toutes nécessaires : cinq étapes à 0,9 donnent 0,590, cinq étapes à 0,99 donnent 0,951.

**`avec_relances(p, relances)`** — Celle-ci décrit un serrurier têtu qui a droit à plusieurs essais pour ouvrir une même porte : il n'échoue que si tous ses essais ratent. Elle reçoit la probabilité p de réussir l'étape en un coup et le nombre R de relances autorisées, et rend 1 − (1 − p) à la puissance R + 1, la chance qu'au moins un des R + 1 essais réussisse. Avec p = 0,9 et deux relances, une étape passe de 0,9 à 0,999 ; c'est la ligne qᵢ du squelette, qui transforme une étape fragile en étape presque sûre avant qu'on la multiplie avec les autres.

**`main()`** — C'est le contremaître qui vérifie, chiffre en main, les promesses de la fiche. Il ne reçoit rien ; il calcule la fiabilité de cinq étapes à 0,9, de cinq étapes à 0,99 et de cinq étapes à 0,9 relancées deux fois chacune, imprime les trois valeurs 0,590, 0,951 et 0,995, et confronte chacune par `assert` à la valeur arrondie attendue. Il vérifie encore qu'une sixième étape à 0,9 fait baisser la fiabilité sous celle des cinq, puis annonce que toutes les vérifications sont passées ; il ne rend rien.

```python
"""Fiche 29 — fiabilité en série : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def fiabilite(probas: list[float]) -> float:
    """P(succès) = p₁ × p₂ × … × pₙ, pour des étapes indépendantes et toutes nécessaires."""
    if not probas or any(not 0 <= p <= 1 for p in probas):
        raise ValueError("au moins une étape, chaque p dans [0, 1]")
    return math.prod(probas)


def avec_relances(p: float, relances: int) -> float:
    """Une étape relancée R fois réussit avec 1 − (1 − p)^(R + 1) (étape 11)."""
    return 1 - (1 - p) ** (relances + 1)


def main() -> None:
    a, b = fiabilite([0.9] * 5), fiabilite([0.99] * 5)
    c = fiabilite([avec_relances(0.9, 2)] * 5)
    print(f"5 étapes à 0,9 : {a:.3f}   à 0,99 : {b:.3f}   à 0,9 avec 2 relances chacune : {c:.3f}")
    assert round(a, 3) == 0.590 and round(b, 3) == 0.951 and round(c, 3) == 0.995
    assert fiabilite([0.9] * 6) < a                                   # une étape de plus fait baisser
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
5 étapes à 0,9 : 0.590   à 0,99 : 0.951   à 0,9 avec 2 relances chacune : 0.995
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`fiabilite` vérifie qu'il y a au moins une étape et que chaque probabilité est bien entre 0 et 1, puis multiplie les probabilités avec `math.prod`. La multiplication traduit l'hypothèse de la fiche : les étapes sont indépendantes et toutes nécessaires, donc la chaîne ne réussit que si chaque maillon réussit, et chaque maillon retire sa part de la fiabilité restante. `avec_relances` calcule la fiabilité d'une seule étape qu'on relance jusqu'à R fois en cas d'échec : elle n'échoue que si les R + 1 essais échouent, d'où 1 − (1 − p) puissance R + 1.

`main` vérifie l'exemple de la fiche : cinq étapes fiables à 90 % ne réussissent ensemble que dans 59 % des cas, et le même agent avec des étapes fiables à 99 % monte à 95,1 %. Relancer chaque étape deux fois fait passer chaque étape de 0,9 à 0,999, et la chaîne entière à 99,5 %. Le dernier `assert` vérifie qu'ajouter une sixième étape fait baisser la fiabilité : aucune étape n'est gratuite.

## Squelette algorithmique

```text
ALGORITHME FiabilitéDUneChaîne
ENTRÉES : fiabilités p₁ … pₙ, relances Rᵢ autorisées pour chaque étape
SORTIE  : P(succès) de la chaîne

  P ← 1
  POUR i DE 1 À n FAIRE
      qᵢ ← 1 − (1 − pᵢ)^(Rᵢ + 1)          (fiabilité de l'étape avec ses relances)
      P ← P × qᵢ
  FIN POUR
  RETOURNER P
```

**Complexité.** O(n) multiplications. La formule suppose l'indépendance ; quand les erreurs sont corrélées, la vraie fiabilité reste entre max(0, 1 − Σ(1 − pᵢ)) et min pᵢ (étape 1), et seule une mesure de bout en bout la donne exactement.

**Du squelette au code.** La ligne de qᵢ est `avec_relances`, et le produit est `fiabilite`.

## Dans le cours

- [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)
- [Étape 11 — Taux de validation et relances](<../../03-Schemas-Outils-et-Premiere-Evaluation/11-Schemas-Formule-Taux-de-Validation.md>)
- [Étape 7 — Taux de conformité et intervalle de Wilson](<../../02-LLM-Softmax-et-Prompts/07-Prompts-Formule-Taux-de-Conformite.md>)
