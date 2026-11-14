# Étape 4 — La softmax

> Palier 01, étape 4 sur 7 · Précédent : [Étape 3 — Le faux modèle](<03-Faux-modele-FakeLLM.md>) · Suivant : [Étape 5 — La fiabilité d'une chaîne](<05-Fiabilite-d-une-chaine.md>) · [Retour à l'énoncé](<../../README.md>)

**Objectif de l'étape :** écrire `softmax(logits, temperature)`, d'abord comme on recopie la formule, puis dans sa forme stable. Les quatre tests de `TestSoftmax` passent à la fin.

## Comment raisonner

Le faux modèle de l'étape 3 rend des réponses toutes faites. Le vrai modèle, lui, **choisit** chaque token : il attribue un score brut (un logit) à chaque candidat, puis transforme ces scores en probabilités avec la softmax. Coder cette fonction, c'est comprendre ce que règle le paramètre de température d'un appel au modèle, et pourquoi un agent qui doit produire du JSON exact travaille à basse température.

La méthode, depuis une feuille blanche, tient en trois temps :

1. **recopier la formule** telle quelle, pour avoir une première version qui calcule juste sur les petits nombres ;
2. **chercher les entrées qui la cassent** : une liste vide, une température nulle ou négative, de grands logits ;
3. **corriger** chaque cassure, en commençant par les gardes (on refuse ce qui n'a pas de sens) puis la stabilité numérique (on évite le débordement sans changer le résultat).

La formule à recopier :

$$
p_i = \frac{e^{z_i / T}}{\sum_{j=1}^{n} e^{z_j / T}}
$$

## La version naïve

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(logits, temperature)`** — Cette première version est celle d'un élève qui recopie la formule au tableau sans se demander ce qu'il se passera avec de grands nombres : elle reçoit la liste des logits et une température, 1,0 par défaut, calcule l'exponentielle de chaque logit divisé par T, fait la somme de ces exponentielles, puis renvoie la liste de chaque exponentielle divisée par cette somme. Sur les logits 2, 1 et 0, elle donne bien environ 0,6652, 0,2447 et 0,0900, mais elle déborde sur 1001, 1002 et 1003, divise par zéro à T = 0, rend une liste vide sans protester et, à T = −1, donne en silence 66,5 % au candidat le moins bien noté.

```python
# [extrait] brouillon
import math


def softmax(logits: list[float], temperature: float = 1.0) -> list[float]:
    exps = [math.exp(z / temperature) for z in logits]     # recopie directe de la formule
    total = sum(exps)
    return [e / total for e in exps]
```

Sur l'exemple de l'énoncé, elle est juste : `softmax([2.0, 1.0, 0.0])` rend bien environ `[0.6652, 0.2447, 0.0900]`. La compréhension de liste `[math.exp(z / temperature) for z in logits]` est l'équivalent de `logits.stream().map(z -> Math.exp(z / t)).toList()` en Java.

Elle casse pourtant de quatre façons :

```text
# [extrait] console
>>> softmax([1001.0, 1002.0, 1003.0])
OverflowError: math range error
>>> softmax([1.0], temperature=0)
ZeroDivisionError: division by zero
>>> softmax([])
[]
>>> softmax([2.0, 1.0, 0.0], temperature=-1.0)
[0.09003057317038046, 0.24472847105479764, 0.6652409557748218]
```

- **Les grands logits.** e¹⁰⁰³ dépasse le plus grand `float` (environ 1,8 × 10³⁰⁸ ≈ e⁷⁰⁹) : `math.exp` lève `OverflowError`. Ce n'est pas théorique : un logit de 14,2 divisé par une température de 0,01 donne un exposant de 1 420. En Java, `Math.exp(1003)` ne lèverait rien : il rendrait `Infinity`, puis `Infinity / Infinity` donnerait `NaN`, et l'erreur se propagerait en silence. Python au moins s'arrête.
- **La température nulle.** Division par zéro. T = 0 n'est d'ailleurs pas une softmax mais un argmax (on prend le meilleur, point) : la fonction doit le refuser clairement.
- **La liste vide.** Elle rend `[]` sans erreur. Une distribution de probabilité sur zéro candidat n'existe pas : rendre une liste vide cache un bug de l'appelant au lieu de le signaler.
- **La température négative.** Le pire cas, parce qu'il ne lève rien : diviser par −1 inverse l'ordre des scores, et le candidat le **moins** bien noté prend 66,5 % de la masse.

## La version stable

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(logits, temperature)`** — C'est la même fonction que dans le brouillon, mais tenue cette fois par un comptable prudent qui ramène tous les montants à une même référence avant de les additionner : elle reçoit les logits et la température, lève `ValueError` si la liste est vide ou si T est nulle ou négative, divise chaque logit par T dans la liste `echelles`, retient le plus grand de ces quotients, puis calcule l'exponentielle de chaque quotient diminué de ce maximum. Chaque exponentielle tombe ainsi entre 0 et 1 et la somme vaut au moins 1 ; la fonction renvoie chaque exponentielle divisée par la somme, dans l'ordre des logits, soit environ 0,8668, 0,1173 et 0,0159 pour 2, 1 et 0 à T = 0,5, et exactement les mêmes probabilités pour 1001, 1002, 1003 que pour 1, 2, 3.

```python
# [extrait] agent/modele.py
def softmax(logits: list[float], temperature: float = 1.0) -> list[float]:
    """pᵢ = exp(zᵢ / T) / Σⱼ exp(zⱼ / T) : les scores du modèle deviennent des probabilités.

    On retranche d'abord le plus grand zᵢ / T, ce qui ne change pas le résultat (le facteur commun se
    simplifie) mais évite tout débordement de `math.exp`. Une température basse concentre la masse
    sur le meilleur token, une température haute l'étale.

    Exemple : `softmax([2.0, 1.0, 0.0])` ≈ [0.6652, 0.2447, 0.0900] ;
    à T = 0.5, les mêmes logits donnent ≈ [0.8668, 0.1173, 0.0159].
    """
    if not logits:
        raise ValueError("il faut au moins un logit")
    if temperature <= 0:
        raise ValueError("la température doit être > 0")
    echelles = [z / temperature for z in logits]
    plus_grand = max(echelles)
    exps = [math.exp(z - plus_grand) for z in echelles]
    total = sum(exps)
    return [e / total for e in exps]
```

**Les deux gardes, en premier.**

- `if not logits:` est vrai pour une liste vide : en Python, une liste vide vaut faux dans un test, comme `logits.isEmpty()` en Java. Sans cette garde, l'appel `max(echelles)` plus bas lèverait de toute façon `ValueError: max() iterable argument is empty`, mais avec un message qui parle de `max` et pas du problème de l'appelant. On lève notre propre message, qui dit ce qui est attendu.
- `if temperature <= 0:` refuse à la fois le zéro (division impossible) et le négatif (ordre inversé en silence). Une seule comparaison couvre les deux cassures.

**`echelles = [z / temperature for z in logits]`.** On divise d'abord chaque logit par T. Garder ces quotients dans une liste évite de refaire la division deux fois (pour le maximum, puis pour l'exponentielle).

**`plus_grand = max(echelles)`, puis `math.exp(z - plus_grand)`.** C'est le cœur de la stabilité. On retranche le plus grand quotient m de chaque exposant. Le résultat ne change pas, parce que le facteur commun se simplifie :

$$
\frac{e^{z_i / T - m}}{\sum_{j} e^{z_j / T - m}} = \frac{e^{-m}\, e^{z_i / T}}{e^{-m} \sum_{j} e^{z_j / T}} = \frac{e^{z_i / T}}{\sum_{j} e^{z_j / T}}
$$

Et l'on gagne deux garanties : le plus grand exposant vaut 0, les autres sont négatifs, donc chaque exponentielle est entre 0 et 1 et ne peut pas déborder ; le total contient au moins le terme e⁰ = 1, donc on ne divise jamais par zéro. Pour les logits 1001, 1002 et 1003, les exposants deviennent −2, −1 et 0, exactement comme pour 1, 2 et 3.

**`total = sum(exps)` puis `[e / total for e in exps]`.** La normalisation : chaque exponentielle divisée par la somme. Les probabilités rendues sont dans l'ordre des logits reçus.

**Le piège classique.** Retrancher le maximum des logits **avant** de diviser par T, mais l'oublier dans un des deux endroits, par exemple `math.exp(z / temperature - max(logits))`. Pour T = 1 c'est juste ; pour T = 0,5, on retranche 2 au lieu de 4, et le débordement revient pour les grands logits. Le code de la solution évite la question : il calcule les quotients une fois, et retranche le maximum **des quotients**.

## Vérifier à la main

Logits 2, 1 et 0 à T = 1. Le maximum vaut 2 ; les exposants deviennent 0, −1 et −2 ; e⁰ = 1, e⁻¹ ≈ 0,3679, e⁻² ≈ 0,1353, de somme 1,5032 :

$$
p = \Big( \frac{1}{1{,}5032},\; \frac{0{,}3679}{1{,}5032},\; \frac{0{,}1353}{1{,}5032} \Big) = (0{,}6652 ;\; 0{,}2447 ;\; 0{,}0900)
$$

À T = 0,5, les quotients valent 4, 2 et 0 ; les exposants 0, −2 et −4 ; la somme 1 + 0,1353 + 0,0183 = 1,1536 ; d'où 0,8668, 0,1173 et 0,0159. La basse température a concentré la masse sur le premier candidat.

```text
# [extrait] console
>>> from agent.modele import softmax
>>> [round(p, 4) for p in softmax([2.0, 1.0, 0.0])]
[0.6652, 0.2447, 0.09]
>>> [round(p, 4) for p in softmax([2.0, 1.0, 0.0], 0.5)]
[0.8668, 0.1173, 0.0159]
>>> softmax([1001.0, 1002.0, 1003.0]) == softmax([1.0, 2.0, 3.0])
True
```

## Les tests qui passent maintenant

```powershell
python -m unittest -v tests.test_01_modele.TestSoftmax
```

Les quatre tests sont verts :

- `test_exemple_chiffre` : les trois probabilités à quatre décimales, et la somme égale à 1 à 10⁻¹² près ;
- `test_temperature_concentre` : les valeurs à T = 0,5 ;
- `test_invariance_par_translation_et_grands_logits` : 1, 2, 3 et 1001, 1002, 1003 donnent les mêmes probabilités, ce que la version naïve ne pouvait même pas calculer ;
- `test_entrees_invalides` : `softmax([])` et `softmax([1.0], temperature=0)` lèvent `ValueError`.

## Ce qu'il faut retenir

- On recopie la formule, on cherche ce qui la casse, puis on corrige : gardes d'abord, stabilité ensuite.
- Retrancher le maximum ne change pas le résultat et supprime tout débordement ; c'est une démonstration de trois lignes, pas une astuce.
- Une température basse concentre, une haute étale ; T ≤ 0 n'a pas de sens et se refuse.

> Suivant : [Étape 5 — La fiabilité d'une chaîne](<05-Fiabilite-d-une-chaine.md>)
