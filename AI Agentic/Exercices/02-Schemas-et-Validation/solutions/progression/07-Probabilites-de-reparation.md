# Étape 7 — Les probabilités de la réparation

> Palier 02, étape 7 sur 8 · Précédent : [Étape 6 — La boucle de réparation](<06-Boucle-de-reparation.md>) · Suivant : [Étape 8 — Assemblage et vérification](<08-Assemblage-et-verification.md>) · [Retour à l'énoncé](<../../README.md>)

**Objectif de l'étape :** écrire `p_succes` et `essais_moyens`, les deux formules qui disent ce que rapporte et ce que coûte la boucle de l'étape 6. Le test `test_probabilites` passe à la fin, et avec lui tout le palier.

## Comment raisonner

La boucle de réparation a un paramètre, `max_essais`, et il faut savoir le choisir. Trop petit, trop de dossiers partent chez un humain ; trop grand, on paie des appels qui ne rapportent presque plus rien. Les deux formules de l'étape 11 du cours répondent, sous une hypothèse simple : chaque essai réussit avec la même probabilité p, indépendamment des autres.

On raisonne en **relances** R, comme le cours : R relances, c'est R + 1 essais, donc `reparer(..., max_essais=R + 1)`.

1. **Le gain.** La demande échoue seulement si les R + 1 essais échouent tous. Chacun échoue avec la probabilité 1 − p ; par indépendance, ils échouent tous avec (1 − p)^(R+1), le produit de l'étape 5 du palier 01. Le succès est le complément.
2. **Le coût.** L'essai numéro i + 1 n'a lieu que si les i premiers ont échoué, ce qui arrive avec la probabilité (1 − p)ⁱ. Le nombre moyen d'essais est la somme de ces probabilités, de i = 0 (le premier essai a toujours lieu) à i = R.

$$
P_{\text{succ}}(R) = 1 - (1 - p)^{R+1}, \qquad \mathbb{E}[A] = \sum_{i=0}^{R} (1 - p)^i
$$

Avant de coder, on cherche les entrées qui n'ont pas de sens : p = 0 (un modèle qui ne réussit jamais n'a pas besoin d'une boucle de réparation, mais d'une correction), p > 1 (ce n'est pas une probabilité), R < 0 (un nombre de relances négatif).

## Les deux fonctions

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`p_succes(p, relances)`** — Cette fonction fait le calcul d'un assureur qui se demande combien de dossiers aboutiront si l'on accorde au modèle quelques secondes chances : elle reçoit la probabilité p qu'un essai rende un JSON valide et le nombre R de relances, lève `ValueError` si p n'est pas dans ]0, 1] ou si R est négatif, puis renvoie 1 moins (1 − p) élevé à la puissance R + 1, la probabilité qu'au moins un des R + 1 essais réussisse. Pour p = 0,9, elle donne successivement 0,9, 0,99, 0,999, 0,9999 et 0,99999 quand R va de 0 à 4, ce qui montre les rendements décroissants et justifie la valeur par défaut `max_essais=3`.

**`essais_moyens(p, relances)`** — Celle-ci est le comptable de la même boucle, qui chiffre combien d'appels au modèle coûte une demande en moyenne : elle reçoit les mêmes p et R, applique la même garde, puis additionne les R + 1 termes (1 − p) puissance i, pour i allant de 0 à R, parce que l'essai numéro i + 1 n'a lieu que si les i premiers ont échoué. Elle renvoie cette somme, soit 1 + 0,1 + 0,01 = 1,11 pour p = 0,9 et deux relances, affichée `1.1099999999999999` en flottants ; le test vérifie qu'elle vaut bien 0,999 divisé par 0,9.

```python
# [extrait] agent/schemas.py
def p_succes(p: float, relances: int) -> float:
    """P = 1 − (1 − p)^(R + 1) : au moins un essai valide parmi R + 1 essais indépendants (étape 8).

    `reparer(..., max_essais=R + 1)` fait au plus R relances. Exemple : `p_succes(0.9, 2)` = 0.999.
    """
    if not 0 < p <= 1 or relances < 0:
        raise ValueError("il faut 0 < p <= 1 et relances >= 0")
    return 1 - (1 - p) ** (relances + 1)


def essais_moyens(p: float, relances: int) -> float:
    """E[A] = 1 + (1 − p) + … + (1 − p)^R : l'essai i + 1 n'a lieu que si les i premiers ont échoué.

    Exemple : `essais_moyens(0.9, 2)` = 1 + 0.1 + 0.01 = 1.11 appels au modèle en moyenne.
    """
    if not 0 < p <= 1 or relances < 0:
        raise ValueError("il faut 0 < p <= 1 et relances >= 0")
    return sum((1 - p) ** i for i in range(relances + 1))
```

**La garde, `if not 0 < p <= 1 or relances < 0:`.** La comparaison chaînée `0 < p <= 1` vaut `0 < p and p <= 1` : p strictement positif, au plus 1. Attention à la priorité : `not` s'applique à la comparaison seule, puis `or` relie les deux conditions. La ligne se lit « si p n'est pas dans ]0, 1], ou si les relances sont négatives ». En cas de doute, des parenthèses ne coûtent rien : `if not (0 < p <= 1) or relances < 0:` est identique.

**`return 1 - (1 - p) ** (relances + 1)`.** L'opérateur `**` est la puissance (`Math.pow` en Java). Les parenthèses autour de `relances + 1` sont indispensables : `**` est plus prioritaire que `+`, et `(1 - p) ** relances + 1` vaudrait (1 − p)^R + 1, un nombre plus grand que 1.

**`return sum((1 - p) ** i for i in range(relances + 1))`.** `range(relances + 1)` donne 0, 1, …, R : exactement les R + 1 termes de la somme. On additionne les termes plutôt que d'utiliser la forme fermée P_succ / p : le code suit la démonstration (la formule des queues), et l'identité entre les deux devient une vérification, faite par le test.

**Vérifier à la main.** p = 0,9, donc 1 − p = 0,1, et R = 2 :

$$
P_{\text{succ}}(2) = 1 - 0{,}1^3 = 0{,}999, \qquad \mathbb{E}[A] = 1 + 0{,}1 + 0{,}01 = 1{,}11 = \frac{0{,}999}{0{,}9}
$$

Deux relances suffisent à faire passer 99,9 % des demandes, pour seulement 11 % d'appels en plus d'un essai unique : la plupart des demandes s'arrêtent au premier essai.

```text
# [extrait] console
>>> from agent.schemas import essais_moyens, p_succes
>>> [round(p_succes(0.9, r), 6) for r in range(5)]
[0.9, 0.99, 0.999, 0.9999, 0.99999]
>>> [round(essais_moyens(0.9, r), 6) for r in range(5)]
[1.0, 1.1, 1.11, 1.111, 1.1111]
>>> essais_moyens(0.9, 2)
1.1099999999999999
```

La première liste montre les rendements décroissants : chaque relance divise par dix l'échec restant, et la quatrième n'apporte plus que 0,00009. C'est pourquoi la valeur par défaut est `max_essais=3`, soit R = 2. La dernière ligne rappelle qu'en flottants 1,11 s'écrit `1.1099999999999999` : le test compare avec `assertAlmostEqual`.

**Vérifier par la simulation.** On peut aussi jouer la boucle 100 000 fois avec un générateur à graine fixe (jamais l'état global du module `random`, pour que le résultat soit reproductible) :

```text
# [extrait] console
>>> import random
>>> g = random.Random(2026)
>>> succes = essais = 0
>>> for _ in range(100_000):
...     for essai in range(1, 4):
...         essais += 1
...         if g.random() < 0.9:
...             succes += 1
...             break
...
>>> succes / 100_000, essais / 100_000
(0.99901, 1.10868)
```

La fréquence observée, 0,99901, et le coût observé, 1,10868 essai, sont à quelques millièmes des valeurs théoriques 0,999 et 1,11.

**La limite de l'hypothèse.** En production, les essais ne sont pas indépendants : une demande difficile (une date ambiguë, une information absente du courriel) le reste à chaque relance. L'étape 11 du cours montre qu'une fraction f de demandes irréparables plafonne le succès à 1 − f, quel que soit R. Les formules donnent un ordre de grandeur pour choisir R ; seule la mesure, avec la liste `erreurs` que rend `reparer`, dit ce qui se passe vraiment.

## Le test qui passe maintenant

```powershell
python -m unittest -v tests.test_02_schemas.TestReparation.test_probabilites
```

Il vérifie `p_succes(0.9, 2)` ≈ 0,999, `essais_moyens(0.9, 2)` ≈ 1,11, l'identité entre les deux (1,11 = 0,999 / 0,9), et le refus de p = 0, de p = 1,2 et d'un nombre de relances égal à −1. Les quinze tests du palier sont maintenant verts.

## Ce qu'il faut retenir

- R relances, c'est R + 1 essais : `max_essais = R + 1`.
- Le succès se calcule par le complément ; le coût est une somme de probabilités « d'aller plus loin ».
- Chaque relance rapporte beaucoup moins que la précédente : deux relances suffisent quand p est grand.

> Suivant : [Étape 8 — Assemblage et vérification](<08-Assemblage-et-verification.md>)
