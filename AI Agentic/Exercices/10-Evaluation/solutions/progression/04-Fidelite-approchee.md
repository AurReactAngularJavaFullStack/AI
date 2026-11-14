# Étape 4 — La fidélité approchée

> [Énoncé du palier 10](<../../README.md>) · Précédent : [Étape 3 — Goal Accuracy et moyenne définie](<03-Goal-Accuracy-et-moyenne-definie.md>) · Suivant : [Étape 5 — Noter un cas](<05-Noter-un-cas.md>)

## Comment raisonner

La fidélité de l'étape 54 découpe la réponse en affirmations et demande à un juge si chacune se déduit du contexte. Sans juge, on garde l'essentiel pour un agent bancaire : **les chiffres**. Une réponse qui cite un nombre absent de toutes les sources l'a inventé. C'est exactement le défaut de la candidate, qui écrit « endettement estimé à 35 % » sans avoir appelé l'outil de ratio.

Il faut donc deux fonctions. D'abord un **lecteur** de nombres, qui comprend l'écriture française de l'agent (espace fine pour les milliers, virgule décimale, pourcentages) et ignore ce qui n'est pas un chiffre cité (les références `[REG-1]`). Ensuite la **comparaison** des nombres de la réponse avec ceux des sources. On écrit le lecteur en premier : c'est lui qui décide de ce qu'on compare.

## Un lecteur naïf

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`nombres(t)`** — Ce brouillon lit un texte comme un enfant qui épelle chaque paquet de chiffres sans rien savoir des virgules, des milliers ou des pourcentages. Il reçoit une chaîne, y cherche toutes les suites ininterrompues de chiffres décimaux, et rend la liste de ces suites converties en flottants. Sur « 5 558,32 AED ; 28,9 % [REG-1] », écrit avec une espace fine, il rend six nombres, 5, 558, 32, 28, 9 et 1, dont aucun n'est celui que l'agent a voulu écrire : les milliers et les décimales sont coupés, le pourcentage n'est pas divisé par 100 et le renvoi de citation est compté comme un chiffre.

```python
# [extrait] brouillon
def nombres(t):
    return [float(v) for v in re.findall(r"\d+", t)]
```

Sur « 5 558,32 AED ; 28,9 % [REG-1] », écrit avec une espace fine, ce brouillon lit 5, 558, 32, 28, 9 et 1 : six nombres dont aucun n'est juste. L'espace fine coupe les milliers, la virgule coupe les décimales, le pourcentage n'est pas divisé par 100 (la source dira 0.289, la réponse 28,9 %), et le 1 de la citation est compté.

## Le lecteur à la française

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`nombres(t)`** — La bonne version lit comme un comptable français habitué aux relevés : elle sait que l'espace fine sépare les milliers, que la virgule annonce les décimales et que « % » divise par cent. Elle reçoit une chaîne, efface d'abord les citations comme `[REG-1]`, puis les espaces fines `ESPACE_FINE`, et cherche ensuite chaque nombre, avec sa partie décimale facultative après un point ou une virgule, suivi d'éventuelles espaces et d'un `%` facultatif. Elle rend la liste des flottants obtenus en remplaçant la virgule par un point et en divisant par 100 les pourcentages : `[5558.32, 0.289]` pour l'exemple de l'énoncé, et une liste vide pour « aucun chiffre [REG-2] ».

```python
# [extrait] agent/evaluation.py
def nombres(t: str) -> list[float]:
    ...
    t = re.sub(r"\[[A-Z]+-\d+\]", "", t).replace(ESPACE_FINE, "")
    return [float(v.replace(",", ".")) / (100 if pct else 1) for v, pct in re.findall(r"(\d+(?:[.,]\d+)?)\s*(%?)", t)]
```

**Ligne par ligne.**

- `re.sub(r"\[[A-Z]+-\d+\]", "", t)` efface les citations : un crochet ouvrant (échappé, sinon il ouvrirait une classe de caractères), des majuscules, un tiret, des chiffres, un crochet fermant. `[REG-2]` disparaît, son 2 aussi.
- `.replace(ESPACE_FINE, "")` recolle les milliers : « 5 558,32 » devient « 5558,32 ». `ESPACE_FINE` vient du palier 03, où `fr` l'insère ; on l'importe au lieu de recopier le caractère, invisible dans un éditeur.
- `re.findall` avec **deux groupes** rend une liste de couples : le nombre `(\d+(?:[.,]\d+)?)`, avec une partie décimale facultative après un point ou une virgule, et le `%` facultatif `(%?)`, séparé par d'éventuelles espaces `\s*`. Sur « 5558,32 AED ; 28,9 % », on obtient deux couples : le nombre « 5558,32 » avec un pourcentage vide, puis le nombre « 28,9 » avec « % ».
- Pour chaque couple, `v.replace(",", ".")` rend la chaîne lisible par `float`, et `/ (100 if pct else 1)` divise les pourcentages : `pct` vaut `"%"` (vrai) ou `""` (faux). Résultat `[5558.32, 0.289]`.

**Analogie Java.** Une boucle `while (matcher.find())` qui lit `matcher.group(1)` et `matcher.group(2)`, puis `Double.parseDouble(g1.replace(',', '.'))`. Python condense la boucle dans une compréhension.

**Le piège classique.** L'espace ordinaire. Seule l'espace fine est retirée : « 55 000 » écrit avec une espace normale est lu comme 55 et 0. C'est voulu (une espace ordinaire sépare aussi deux nombres distincts, « 3 4 ») mais cela impose que l'agent formate ses montants avec `fr`. Deuxième limite : tout chiffre compte, y compris le 7 de « C-7 » ou le 214 de « lot 214 ». La mesure est **approchée**, et on le dit dans son nom.

## La comparaison

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`fidelite_approchee(reponse, sources)`** — Cette fonction est le documentaliste qui reprend chaque chiffre d'une note de synthèse et va le chercher, un à un, dans les dossiers d'archives. Elle reçoit la réponse de l'agent et la liste des sources, extrait les nombres cités par la réponse avec `nombres` et rend `None` s'il n'y en a aucun ; sinon elle aplatit en une seule liste tous les nombres des sources, compte les nombres cités qui ont un voisin connu au sens de `math.isclose` avec des tolérances relative et absolue de 10⁻⁹, et divise par le nombre de cités. La réponse fautive, qui cite 5419,37 et 35 % face à la seule sortie de l'outil de mensualité, obtient 1 / 2 = 0,5 ; la tolérance évite qu'un 35,61 % lu comme `0.35609999999999997` soit pris pour une invention face au `0.3561` de l'outil.

```python
# [extrait] agent/evaluation.py
def fidelite_approchee(reponse: str, sources: list[str]) -> float | None:
    ...
    cites = nombres(reponse)
    if not cites:
        return None
    connus = [x for s in sources for x in nombres(s)]
    return sum(1 for c in cites if any(math.isclose(c, k, rel_tol=1e-9, abs_tol=1e-9) for k in connus)) / len(cites)
```

**Ligne par ligne.**

- `cites` est X, la liste des nombres de la réponse. Vide : `None`, car une réponse sans chiffre n'a pas de fidélité chiffrée (étape 3).
- `connus` est K : la compréhension à deux `for` aplatit les listes de nombres de toutes les sources, comme un `flatMap` Java. Une source est une chaîne : la sortie JSON d'un outil, le prompt, un document.
- Pour chaque nombre cité, `any(...)` cherche un nombre connu proche ; `sum(1 for … if …)` compte ceux qui en ont un. On divise par le nombre de cités.
- `math.isclose(c, k, rel_tol=1e-9, abs_tol=1e-9)` compare à une tolérance près. Pourquoi ? Dans le dossier C-3 de la démo, « 35,61 % » lu dans la réponse donne `35.61 / 100`, soit `0.35609999999999997`, alors que la sortie de l'outil contient `0.3561` : l'égalité stricte échouerait sur un chiffre parfaitement fidèle. La tolérance absolue sert aux valeurs proches de zéro, où une tolérance relative seule serait trop stricte.

**Les nombres de l'énoncé.** La réponse fautive cite X = [5419,37 ; 0,35] ; la sortie de l'outil `{"mensualite_aed": 5419.37}` donne K = [5419,37]. 5419,37 est retrouvé, 0,35 non : 1 / 2 = 0,5. Avec la source supplémentaire « plafond 35 % », K contient 0,35 et la fidélité vaut 1.

**Le piège classique.** Inverser les rôles et compter les nombres des sources retrouvés dans la réponse : on mesurerait alors la couverture des sources, pas l'invention de la réponse. Le dénominateur est la réponse.

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_10_evaluation.TestGoalEtFidelite
```

`test_nombres_a_la_francaise` vérifie `[5558.32, 0.289]` et la liste vide pour « aucun chiffre [REG-2] ». `test_fidelite` vérifie 0,5, puis 1,0 avec la source « plafond 35 % », puis `None` pour « Dossier recevable. ». Avec les deux tests de l'étape 3, toute la classe est verte.
