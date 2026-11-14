# Étape 6 — Rappeler

> Progression du palier 06 · Précédent : [Étape 5 — Le souvenir](<05-Le-souvenir.md>) · Suivant : [Étape 7 — Assemblage, tests et démo](<07-Assemblage-tests-et-demo.md>) · Retour à l'énoncé : [README du palier 06](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Toutes les briques existent ; `rappeler` les enchaîne. Avant d'écrire, on dessine le flux des données sur la feuille, du plus brut au plus fini :

```text
question, souvenirs ──► 3 listes brutes (cosinus, récence, importance), une valeur par souvenir
                    ──► 3 listes min-max, dans [0, 1]
                    ──► 1 score par souvenir (score_pertinence)
                    ──► tri décroissant, k premiers
                    ──► relecture des k gardés
```

Trois décisions de conception se lisent sur ce schéma.

1. **Le min-max se fait par composante, sur tous les candidats**, et pas souvenir par souvenir : il faut avoir calculé les trois listes complètes avant le moindre score.
2. **Les listes restent alignées.** Le rang j désigne le même souvenir dans les trois listes ; c'est ce qui permet de les relire avec un seul indice.
3. **Le plongement est injecté.** La mémoire ne sait pas fabriquer un vecteur ; elle reçoit une fonction `plonger_texte` qui le fait. C'est l'injection de dépendance que tu pratiques avec Spring : `rappeler` dépend d'une interface, `Callable[[str], list[float]]`, l'équivalent d'un `Function<String, List<Double>>`, et pas d'une implémentation. Les tests lui passent `VECTEURS.__getitem__`, la méthode d'accès d'un dictionnaire, qui rend le vecteur d'un texte connu. C'est l'équivalent de la référence de méthode `vecteurs::get`. Le palier 07 lui passera le vrai plongement.

## Les gardes et les trois composantes

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`rappeler(question, souvenirs, plonger_texte, jour, k, demi_vie, poids)`** — Cette première moitié de la fonction est celle d'une bibliothécaire qui, avant de choisir les fiches, mesure chacune selon trois critères : elle reçoit la question, les souvenirs, la fonction de plongement injectée, le jour courant et le réglage, k = 2, une demi-vie de 30 jours et les poids (0,5 ; 0,3 ; 0,2), lève `ValueError` si k est inférieur à 1 et renvoie une liste vide si la mémoire est vide. Sinon, elle plonge la question une seule fois, puis calcule trois listes alignées, le cosinus de chaque souvenir avec la question, la récence de son âge `jour - s.jour_acces` et son importance convertie en `float`, chacune passée aussitôt par `min_max` ; la suite, le score et le tri, vient dans l'extrait suivant.

```python
# [extrait] agent/memoire.py
def rappeler(question: str, souvenirs: list[Souvenir], plonger_texte: Callable[[str], list[float]], jour: float,
             k: int = 2, demi_vie: float = 30.0,
             poids: tuple[float, float, float] = (0.5, 0.3, 0.2)) -> list[tuple[float, Souvenir]]:
    ...
    if k < 1:
        raise ValueError("k doit valoir au moins 1")
    if not souvenirs:
        return []
    vq = plonger_texte(question)
    sims = min_max([cosinus(vq, plonger_texte(s.texte)) for s in souvenirs])
    recs = min_max([recence(jour - s.jour_acces, demi_vie) for s in souvenirs])
    imps = min_max([float(s.importance) for s in souvenirs])
    ...
```

**La signature.** Les quatre premiers paramètres sont obligatoires ; `k`, `demi_vie` et `poids` ont les valeurs de l'étape 77. Le type de retour, `list[tuple[float, Souvenir]]`, annonce des couples (score, souvenir) : l'appelant reçoit le score avec le souvenir, pour le journaliser ou lui appliquer un seuil.

**`if k < 1: raise ValueError(...)`.** Garder zéro souvenir n'a pas de sens : c'est une erreur d'appel, pas une demande de liste vide.

**`if not souvenirs: return []`.** Un client sans mémoire est un cas normal, celui d'un nouveau client. On rend une liste vide **avant** d'appeler `min_max`, qui refuserait une liste vide. On ne plonge même pas la question, puisqu'aucune comparaison n'est à faire.

**`vq = plonger_texte(question)`.** La question est plongée **une seule fois**, hors de la boucle. Avec un vrai modèle d'embedding, chaque appel coûte un aller-retour réseau : le plonger n + 1 fois au lieu de 2n est une vraie économie.

**Les trois compréhensions.** Chacune produit une liste brute, dans l'ordre des souvenirs, aussitôt passée par `min_max`.

- `cosinus(vq, plonger_texte(s.texte))` : la similarité de sens. Un texte au vecteur nul fait lever `ValueError` par `cosinus`, et l'erreur remonte telle quelle.
- `recence(jour - s.jour_acces, demi_vie)` : l'âge se calcule au moment du rappel, à partir du jour courant reçu en paramètre. Le palier 06 ne lit aucune horloge globale ; le palier 12 lui passera `horloge.jour()`.
- `float(s.importance)` : on convertit en `float` pour que les trois listes aient le même type. `min_max` marcherait aussi sur des entiers, mais la conversion dit clairement qu'on passe d'une note à un signal continu.

**Le piège classique.** Plonger la question dans la compréhension, `cosinus(plonger_texte(question), plonger_texte(s.texte))`, ce qui la recalcule n fois. Le résultat est juste, mais le coût est doublé.

## Un brouillon de tri qui casse sur une égalité

Il reste à classer les souvenirs. Le premier réflexe est de trier les couples à l'envers :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`garder(notes, k)`** — Ce brouillon est un huissier qui range les dossiers par note décroissante sans avoir prévu de règle pour départager deux notes égales : il reçoit la liste des couples (score, souvenir) et le nombre k, trie ces couples à l'envers avec `sorted(..., reverse=True)` et renvoie les k premiers. Python compare alors les tuples élément par élément, et, dès que deux scores sont égaux, il tente de comparer les souvenirs eux-mêmes, qu'une dataclass ordinaire ne sait pas ordonner : le tri lève `TypeError`. Le brouillon passe donc le scénario du crédit, aux quatre scores distincts, et plante en production au premier ex aequo.

```python
# [extrait] brouillon
def garder(notes: list, k: int) -> list:
    return sorted(notes, reverse=True)[:k]        # compare les couples (score, souvenir)
```

Python compare les tuples élément par élément : d'abord les scores, puis, **en cas d'égalité**, les souvenirs eux-mêmes. Or une `dataclass` ordinaire ne définit pas d'ordre :

```text
# [extrait] console
>>> sorted([(0.5, Souvenir("b", 1.0, 2)), (0.5, Souvenir("a", 1.0, 2))], reverse=True)
Traceback (most recent call last):
  File "<console>", line 1, in <module>
TypeError: '<' not supported between instances of 'Souvenir' and 'Souvenir'
```

Le brouillon marche sur le scénario du crédit, où les quatre scores diffèrent, et plante en production dès que deux souvenirs ont le même score. Ce n'est pas rare : deux souvenirs relus le même jour, de même importance et de même cosinus, ont le même score. Il faut une **clé de tri** explicite, comme on passe un `Comparator` à `Collections.sort` en Java.

## Le score, le tri et la relecture

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`rappeler(question, souvenirs, plonger_texte, jour, k, demi_vie, poids)`** — C'est la même fonction, dont cet extrait montre la seconde moitié, celle où la bibliothécaire classe ses fiches et pose les meilleures sur le bureau : elle calcule pour chaque souvenir, grâce au rang j des trois listes alignées, le couple (score de pertinence, souvenir), trie ces couples avec une clé explicite, l'opposé du score puis le texte du souvenir pour départager les égalités, et garde les k premiers. Elle relit ensuite les souvenirs gardés, et eux seuls, en faisant passer leur `jour_acces` au jour courant, puis renvoie les couples, du meilleur au moins bon, avec le score calculé avant la relecture ; au jour 90, le client C-1 obtient le salaire à 0,9769 et le crédit auto à 0,807, et sa mémoire passe aux jours d'accès [90, 90, 0, 88].

```python
# [extrait] agent/memoire.py
def rappeler(question: str, souvenirs: list[Souvenir], plonger_texte: Callable[[str], list[float]], jour: float,
             k: int = 2, demi_vie: float = 30.0,
             poids: tuple[float, float, float] = (0.5, 0.3, 0.2)) -> list[tuple[float, Souvenir]]:
    ...
    notes = [(score_pertinence(sims[j], recs[j], imps[j], poids), s) for j, s in enumerate(souvenirs)]
    gardes = sorted(notes, key=lambda x: (-x[0], x[1].texte))[:k]
    for _, s in gardes:
        s.jour_acces = jour                   # relire remet l'horloge du souvenir à zéro (étape 16)
    return gardes
```

**`notes = [(score_pertinence(sims[j], recs[j], imps[j], poids), s) for j, s in enumerate(souvenirs)]`.** `enumerate` donne à la fois le rang j et le souvenir s, comme une boucle `for (int j = 0; j < n; j++)` qui lirait `souvenirs.get(j)`. Le rang sert à lire les trois listes alignées ; le souvenir est gardé dans le couple. Comme les trois composantes sortent de `min_max`, elles sont dans [0, 1] et `score_pertinence` les accepte. Si les poids sont invalides, elle lève `ValueError` dès le premier souvenir.

**`gardes = sorted(notes, key=lambda x: (-x[0], x[1].texte))[:k]`.** La clé de tri est un couple. Son premier élément est `-x[0]`, l'opposé du score : trier les opposés en ordre croissant revient à trier les scores en ordre décroissant. Son second élément est `x[1].texte`, le texte du souvenir, qui départage les égalités dans l'ordre alphabétique. En Java, on écrirait `Comparator.comparingDouble(Note::score).reversed().thenComparing(n -> n.souvenir().texte())`. Le résultat ne dépend donc plus de l'ordre de la liste reçue : deux exécutions donnent toujours le même prompt. `[:k]` garde les k premiers ; si la liste en contient moins de k, elle est rendue entière, sans erreur.

**La relecture.** `for _, s in gardes: s.jour_acces = jour` remet à neuf les souvenirs gardés, et seulement eux : leur âge repartira de 0 à la prochaine question. C'est le point 6 de l'étape 16, « relire un souvenir le remet à neuf ». Les objets modifiés sont **ceux de l'appelant**, puisque les couples contiennent des références vers les souvenirs de la liste reçue, et non des copies. C'est pourquoi le `Souvenir` n'est pas gelé (étape 5).

**`return gardes`.** Les couples (score, souvenir), du meilleur au moins bon. Le score rendu est celui calculé **avant** la relecture.

**Le piège classique.** Relire avant de calculer les scores, ou relire tous les souvenirs. Dans le premier cas, la récence des souvenirs gardés est faussée ; dans le second, tous les souvenirs ont le même âge à la question suivante, et la récence ne départage plus personne.

## Vérification à la console

```text
# [extrait] console
>>> from agent.memoire import Souvenir, rappeler
>>> VECTEURS = {"question": [1, 1, 2, 1, 0, 1, 0, 0], "salaire": [0, 1, 1, 0, 0, 0, 0, 0], "credit auto": [1, 0, 1, 0, 0, 0, 0, 0], "pret personnel": [0, 0, 1, 1, 0, 0, 0, 0], "change": [0, 0, 0, 0, 0, 3, 0, 0]}
>>> memoire = [Souvenir("salaire", 85.0, 9), Souvenir("credit auto", 60.0, 8), Souvenir("pret personnel", 0.0, 4), Souvenir("change", 88.0, 2)]
>>> gardes = rappeler("question", memoire, VECTEURS.__getitem__, 90.0)
>>> [(round(score, 4), s.texte) for score, s in gardes]
[(0.9769, 'salaire'), (0.807, 'credit auto')]
>>> [s.jour_acces for s in memoire]
[90.0, 90.0, 0.0, 88.0]
>>> gardes[0][1] is memoire[0]
True
```

Ce sont les nombres recalculés à la main dans l'énoncé. Les similarités valent [0,75 ; 0,75 ; 0,75 ; 0,3536], soit [1, 1, 1, 0] après min-max. Les récences valent [0,8909 ; 0,5 ; 0,125 ; 0,9548], soit [0,9229 ; 0,4519 ; 0 ; 1]. Les importances deviennent [1 ; 0,8571 ; 0,2857 ; 0]. Le salaire obtient 0,5 + 0,2769 + 0,2 = 0,9769, et le crédit auto 0,5 + 0,1356 + 0,1714 = 0,8070. Le dernier affichage montre que le souvenir rendu est **le même objet** que celui de la liste : la relecture a bien modifié la mémoire de l'appelant.

Un souvenir daté du jour 95, rappelé au jour 90, a un âge de −5 jours, et l'erreur de `recence` remonte jusqu'à l'appelant :

```text
# [extrait] console
>>> rappeler("question", [Souvenir("salaire", 95.0, 9)], VECTEURS.__getitem__, 90.0)
Traceback (most recent call last):
  ...
ValueError: il faut age >= 0 et demi_vie > 0
```

## Les tests qui passent maintenant

```text
python -m unittest -v tests.test_06_memoire
```

Les treize tests du palier passent. Les quatre de `TestRappeler` vérifient les points suivants :

- `test_scenario_de_77` : le salaire puis le crédit auto, avec 0,9769 et 0,8070 à quatre décimales ;
- `test_tous_les_scores` : avec k = 4, les scores 0,9769, 0,8070, 0,5571 et 0,3 ;
- `test_relire_remet_l_horloge_a_zero` : les jours d'accès deviennent [90, 90, 0, 88] ;
- `test_cas_limites_et_erreurs` : une mémoire vide rend `[]` ; `k=0`, un souvenir « du futur » au jour 50 et l'importance 11 lèvent `ValueError`.
