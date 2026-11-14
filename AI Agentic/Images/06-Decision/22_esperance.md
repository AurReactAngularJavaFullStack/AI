# Fiche 22 — Espérance

> Image : `22_esperance.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)

**Le résultat moyen, pondéré par les chances**

## Formule

$$
\mathbb{E}[X] = \sum_{x} x \times P(X = x)
$$

## Éléments

$$
X
$$

**X** : une quantité aléatoire : coût, délai ou récompense.

$$
x
$$

**x** : une valeur possible de X.

$$
P(X = x)
$$

**P(X = x)** : la chance de cette valeur.

$$
\mathbb{E}[X]
$$

**𝔼[X]** : la moyenne qu'on obtiendrait sur beaucoup de répétitions.

## Ce que c'est

L'espérance additionne chaque issue multipliée par sa probabilité. Elle ne décrit pas un cas unique. Elle décrit la moyenne si l'on répète.

## Effets et impacts

- Elle compare des stratégies d'agent : appels, reprises, validations humaines.
- Une moyenne acceptable peut cacher un incident très coûteux.
- Pour une action irréversible, il faut lire aussi les cas extrêmes, pas seulement 𝔼[X].

## Exemple chiffré

L'image montre les issues 2, 5, 9 et 15 et la moyenne 6,8, sans donner les probabilités. Par exemple, avec les probabilités 0,2 ; 0,5 ; 0,1 ; 0,2 :

$$
\mathbb{E}[X] = 2 \times 0{,}2 + 5 \times 0{,}5 + 9 \times 0{,}1 + 15 \times 0{,}2 = 0{,}4 + 2{,}5 + 0{,}9 + 3{,}0 = 6{,}8
$$

Aucune exécution ne coûte 6,8 : c'est une moyenne. Une sur cinq coûte 15.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`esperance(valeurs, probas)`** — Cette fonction est le comptable d'une entreprise de dépannage qui veut connaître le coût moyen d'une intervention sans attendre la fin de l'année : elle reçoit la liste des valeurs possibles et la liste de leurs probabilités, vérifie qu'il y a bien une probabilité par valeur et que ces probabilités font 1 au total, et lève une `ValueError` dans le cas contraire. Elle multiplie ensuite chaque valeur par sa probabilité, additionne ces produits et renvoie l'espérance : 0,4 + 2,5 + 0,9 + 3,0 = 6,8 pour les issues 2, 5, 9 et 15 pesées 0,2, 0,5, 0,1 et 0,2.

**`moyenne_simulee(valeurs, probas, tirages, graine)`** — Celle-ci est le stagiaire qu'on envoie vérifier le calcul du comptable en faisant vraiment les interventions, une par une, sur le papier : elle reçoit les mêmes valeurs et probabilités, un nombre de tirages et une graine qui vaut 3 par défaut, crée un générateur aléatoire réglé sur cette graine pour que le résultat soit reproductible, puis tire autant de fois qu'on le demande une valeur au hasard selon les probabilités données. Elle renvoie la moyenne de tous ces tirages, 6,78 pour 100 000 tirages, un nombre proche de 6,8 qui illustre la loi des grands nombres.

**`main()`** — C'est la réunion de fin de mois où le calcul et l'expérience sont confrontés : il fixe les valeurs 2, 5, 9 et 15 et leurs probabilités, demande l'espérance à `esperance` et la moyenne de 100 000 tirages à `moyenne_simulee`, puis imprime les deux nombres ainsi que la valeur la plus haute, 15. Un `assert` vérifie que l'espérance vaut 6,8, que la moyenne simulée s'en écarte de moins de 0,1 et que 6,8 n'est aucune des valeurs possibles, rappel qu'aucune intervention ne coûte la moyenne, avant que la ligne de succès ne s'affiche.

```python
"""Fiche 22 — espérance : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import random


def esperance(valeurs: list[float], probas: list[float]) -> float:
    """E[X] = Σ x × P(X = x)."""
    if len(valeurs) != len(probas) or not math.isclose(sum(probas), 1):
        raise ValueError("une probabilité par valeur, de somme 1")
    return sum(x * p for x, p in zip(valeurs, probas))


def moyenne_simulee(valeurs: list[float], probas: list[float], tirages: int, graine: int = 3) -> float:
    rng = random.Random(graine)
    return sum(rng.choices(valeurs, probas)[0] for _ in range(tirages)) / tirages


def main() -> None:
    valeurs, probas = [2, 5, 9, 15], [0.2, 0.5, 0.1, 0.2]
    e = esperance(valeurs, probas)
    m = moyenne_simulee(valeurs, probas, 100_000)
    print(f"E[X] = {e:.1f}   moyenne de 100 000 tirages = {m:.2f}   valeur la plus haute : {max(valeurs)}")
    assert math.isclose(e, 6.8) and abs(m - 6.8) < 0.1 and e not in valeurs
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
E[X] = 6.8   moyenne de 100 000 tirages = 6.78   valeur la plus haute : 15
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`esperance` vérifie qu'il y a une probabilité par valeur et que ces probabilités somment à 1, puis additionne chaque valeur multipliée par sa probabilité. Avec les valeurs 2, 5, 9 et 15 et les probabilités 0,2 ; 0,5 ; 0,1 et 0,2, elle trouve 0,4 + 2,5 + 0,9 + 3,0 = 6,8, la moyenne de l'image.

`moyenne_simulee` montre ce que veut dire ce nombre : elle tire 100 000 fois une valeur au hasard selon ces probabilités, avec un générateur à graine fixe pour que le résultat soit reproductible, et calcule la moyenne des tirages. Le programme vérifie que cette moyenne est proche de 6,8, ce qui est la loi des grands nombres : l'espérance est la moyenne qu'on obtient en répétant. Il vérifie aussi que 6,8 n'est aucune des valeurs possibles, et rappelle que la valeur la plus haute, 15, arrive une fois sur cinq : pour une action irréversible, il faut lire ce cas extrême, pas seulement la moyenne.

## Squelette algorithmique

```text
ALGORITHME ComparerDesStratégies
ENTRÉES : stratégies, et pour chacune ses issues (valeur, probabilité)
SORTIE  : la stratégie de meilleure espérance, avec son pire cas

  POUR CHAQUE stratégie s FAIRE
      E(s) ← Σ valeur × probabilité
      pire(s) ← la plus mauvaise valeur de probabilité non nulle
  FIN POUR
  garder les stratégies dont le pire cas est acceptable
  RETOURNER celle de plus grande (ou plus petite, pour un coût) espérance
```

**Complexité.** O(nombre total d'issues) pour les espérances et les pires cas, puis O(nombre de stratégies) pour choisir. La simulation de vérification coûte O(tirages).

**Du squelette au code.** Le calcul de E(s) est `esperance`, et la vérification par tirages est `moyenne_simulee`.

## Dans le cours

- [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)
- [Étape 11 — Taux de validation et relances](<../../03-Schemas-Outils-et-Premiere-Evaluation/11-Schemas-Formule-Taux-de-Validation.md>)
- [Étape 78 — Synthèse : les mathématiques de l'IA agentique](<../../14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md>)
