# Fiche 28 — Valeur de l'information

> Image : `28_valeur_information.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**Chercher encore, ou agir maintenant**

## Formule

$$
\operatorname{VOI} = \mathbb{E}\left[ \max_{a} U(a \mid E) \right] - \max_{a} U(a)
$$

## Éléments

$$
a
$$

**a** : une action possible.

$$
U(a)
$$

**U(a)** : l'utilité de a avec ce que l'on sait déjà (fiche 10).

$$
E
$$

**E** : une information pas encore observée.

$$
U(a \mid E)
$$

**U(a | E)** : l'utilité de a une fois E connue.

$$
\max_{a}
$$

**max** : la meilleure action.

$$
\mathbb{E}[\ ]
$$

**𝔼[ ]** : la moyenne sur les informations possibles.

## Ce que c'est

La VOI est le gain attendu à obtenir une information avant de décider. Si ce gain est inférieur au coût de la recherche, on agit tout de suite.

## Effets et impacts

- Elle arrête les boucles d'agent qui cherchent sans fin.
- Une VOI faible dit : ne pas appeler un outil de plus.
- Une VOI haute justifie une question, une recherche ou une revue humaine avant une action coûteuse.

## Exemple chiffré

Un agent doit valider ou refuser un remboursement. 20 % des demandes sont frauduleuses. Valider une demande saine rapporte 100, valider une fraude coûte 400, refuser une demande saine coûte 50.

$$
\text{sans information} : \ U(\text{valider}) = 0{,}8 \times 100 - 0{,}2 \times 400 = 0, \quad U(\text{refuser}) = -0{,}8 \times 50 = -40 \ \Longrightarrow\ \max = 0
$$

Avec une vérification parfaite, on valide les saines et on refuse les fraudes :

$$
\mathbb{E}[\max] = 0{,}8 \times 100 + 0{,}2 \times 0 = 80 \quad\Longrightarrow\quad \operatorname{VOI} = 80 - 0 = 80
$$

Si la vérification coûte 30, elle vaut le coup. Si elle coûte 120, on décide sans elle.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`voi(probas, utilite)`** — Cette fonction est un juge d'instruction qui se demande si une enquête de plus changerait vraiment son verdict : elle reçoit un dictionnaire des probabilités de chaque état du monde, ici une demande saine ou frauduleuse, et un dictionnaire qui donne, pour chaque action, son utilité dans chaque état. Elle calcule d'abord la meilleure décision prise à l'aveugle, en faisant pour chaque action la moyenne de ses utilités pondérée par les probabilités et en gardant la plus haute, puis la décision prise en connaissant l'état, en choisissant pour chaque état la meilleure action et en faisant la moyenne de ces meilleures utilités. Elle renvoie un triplet formé de la valeur de l'information, la différence entre les deux, puis de la valeur avec information et de la valeur sans, soit 80, 80 et 0 dans l'exemple du remboursement.

**`main()`** — C'est le conseil de direction qui décide s'il faut payer une vérification avant de traiter les remboursements : il décrit les deux états, 80 % de demandes saines et 20 % de fraudes, et les utilités des deux actions, valider rapportant 100 sur une demande saine et coûtant 400 sur une fraude, refuser coûtant 50 sur une demande saine et rien sur une fraude. Il appelle `voi`, imprime 0, 80 et 80, les vérifie par un `assert`, puis compare la valeur de l'information à deux prix de vérification : à 30, il conclut qu'il faut vérifier, à 120, qu'il faut décider sans vérifier, avant d'imprimer la ligne de succès.

```python
"""Fiche 28 — valeur de l'information : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def voi(probas: dict[str, float], utilite: dict[str, dict[str, float]]) -> tuple[float, float, float]:
    """VOI = E[max_a U(a | E)] − max_a E[U(a)], pour une information parfaite sur l'état."""
    actions = list(utilite)
    sans = max(sum(p * utilite[a][e] for e, p in probas.items()) for a in actions)
    avec = sum(p * max(utilite[a][e] for a in actions) for e, p in probas.items())
    return avec - sans, avec, sans


def main() -> None:
    probas = {"saine": 0.8, "fraude": 0.2}
    u = {"valider": {"saine": 100, "fraude": -400}, "refuser": {"saine": -50, "fraude": 0}}
    valeur, avec, sans = voi(probas, u)
    print(f"sans information : {sans:.0f}   avec information parfaite : {avec:.0f}   VOI = {valeur:.0f}")
    assert math.isclose(sans, 0) and math.isclose(avec, 80) and math.isclose(valeur, 80)
    for cout in (30, 120):
        print(f"vérification à {cout} : {'vérifier' if valeur > cout else 'décider sans vérifier'}")
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
sans information : 0   avec information parfaite : 80   VOI = 80
vérification à 30 : vérifier
vérification à 120 : décider sans vérifier
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`voi` compare deux situations. Sans information, l'agent doit choisir une seule action pour tous les cas : pour chaque action, il calcule son utilité moyenne sur les états possibles, pondérée par leurs probabilités, et garde la meilleure. Avec une information parfaite, il connaît l'état avant de choisir : pour chaque état, il prend la meilleure action dans cet état, puis fait la moyenne de ces meilleures utilités sur les états. La différence entre les deux est la valeur de l'information : ce que la connaissance de l'état ajoute, en moyenne, à la décision.

`main` rejoue l'exemple de la fiche : 80 % des demandes de remboursement sont saines et 20 % frauduleuses ; valider une demande saine rapporte 100, valider une fraude coûte 400, refuser une demande saine coûte 50. Sans information, valider vaut 0,8 × 100 − 0,2 × 400 = 0 et refuser vaut −40, donc la meilleure décision vaut 0. Avec une vérification parfaite, on valide les saines et on refuse les fraudes, pour une moyenne de 80. La vérification vaut donc 80 : elle vaut la peine si elle coûte 30, pas si elle coûte 120.

## Squelette algorithmique

```text
ALGORITHME ChercherOuAgir
ENTRÉES : états possibles et leurs probabilités, actions, utilités U(a, état), coût c de la recherche
SORTIE  : « chercher d'abord » ou l'action à jouer tout de suite

  sans ← maxₐ Σ_état P(état) × U(a, état)
  avec ← Σ_état P(état) × maxₐ U(a, état)
  VOI ← avec − sans
  SI VOI > c ALORS RETOURNER « chercher d'abord »
  RETOURNER argmaxₐ Σ_état P(état) × U(a, état)
```

**Complexité.** O(|A| × |états|) pour chacune des deux moyennes. Avec une information imparfaite (un test qui se trompe parfois), on remplace « connaître l'état » par une mise à jour de Bayes après le résultat du test, ce qui ajoute O(|états|) par résultat possible.

**Du squelette au code.** `sans` et `avec` sont les deux lignes du même nom dans `voi`, et la comparaison avec le coût est la boucle finale de `main`.

## Dans le cours

- [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)
- [Étape 78 — Synthèse : les mathématiques de l'IA agentique](<../../14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md>)
