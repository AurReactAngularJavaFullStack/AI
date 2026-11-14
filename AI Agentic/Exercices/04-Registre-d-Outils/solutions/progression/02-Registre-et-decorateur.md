# Étape 2 — Le registre et son décorateur

> Palier 04, étape 2 sur 7 · Précédent : [Étape 1 — L'outil et les exceptions](<01-Outil-et-exceptions.md>) · Suivant : [Étape 3 — La porte et les appelables](<03-Porte-et-appelables.md>) · Retour à l'énoncé : [README](<../../README.md>)

## Comment raisonner

Un registre, c'est une table nom → `Outil`. La question est : où vit cette table ? Dans 77, c'est un dictionnaire global, `REGISTRE`, rempli au moment où Python lit le fichier. Simple, mais deux agents dans le même processus partagent alors les mêmes outils, et deux tests aussi : un test qui enregistre « double » le laisse pour le suivant. Ici, la table est un attribut d'objet : chaque `Registre()` a la sienne, et on la passe en paramètre à qui en a besoin.

Ensuite, comment remplit-on la table ? On veut écrire l'outil à l'endroit même où l'on écrit sa fonction, avec son contrat juste au-dessus, comme une annotation Java. C'est le rôle d'un décorateur. Écris d'abord la classe et ses deux méthodes de confort, puis le décorateur, dans sa version naïve, puis dans sa version juste.

## Bloc 1 — La table et deux méthodes spéciales

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Registre.__init__()`** — Le constructeur ouvre le grand livre neuf d'un archiviste qui va inscrire, un à un, les outils de l'agent : il ne reçoit rien et crée sur `self` l'attribut `outils`, un dictionnaire vide annoté `dict[str, Outil]`, qui associera chaque nom public à son `Outil` et gardera l'ordre d'inscription. Parce que la table naît dans le constructeur et non au niveau de la classe, chaque registre a la sienne : deux agents, ou deux tests, ne partagent jamais leurs outils, contrairement au `REGISTRE` global de l'étape 77.

**`Registre.__len__()`** — Cette méthode spéciale répond, comme l'archiviste qui compte les pages remplies, à la question « combien d'outils sont inscrits ? » : elle ne reçoit rien et renvoie la longueur de la table `self.outils`, en déléguant simplement à `len`. C'est elle que Python appelle quand on écrit `len(registre)`, sans qu'aucune interface ne soit déclarée ; après l'inscription des outils métier de l'étape 4, elle renverra 5.

**`Registre.__contains__(nom)`** — Celle-ci permet de demander d'un mot à l'archiviste si un nom figure dans son livre : elle reçoit un nom d'outil et renvoie le booléen `nom in self.outils`, en déléguant elle aussi à la table. Python l'appelle derrière l'opérateur `in`, si bien que `"tva" in registre` se lit comme une phrase ; c'est ce test qui, dans le décorateur, refusera un nom déjà pris.

```python
# [extrait] agent/outils.py
class Registre:
    """Table nom → `Outil`. Exemple : après `enregistrer_outils_metier(Registre())`, `len(registre)` vaut 5."""

    def __init__(self) -> None:
        self.outils: dict[str, Outil] = {}

    def __len__(self) -> int:
        return len(self.outils)

    def __contains__(self, nom: str) -> bool:
        return nom in self.outils
```

**`__init__`.** Le constructeur crée une table vide, annotée `dict[str, Outil]`. L'annotation ne contrôle rien à l'exécution ; elle documente, et un vérificateur de types (mypy, l'IDE) s'en sert. Un `dict` Python garde l'ordre d'insertion depuis la version 3.7 : l'ordre des outils sera celui de leur enregistrement, ce que vérifient les tests.

**Le piège de l'attribut de classe.** Écrire la table au niveau de la classe, `class Registre: outils = {}`, semble équivalent. Ça ne l'est pas : ce dictionnaire serait créé une seule fois, partagé par **toutes** les instances, et l'on retrouverait exactement la variable globale qu'on voulait éviter. En Java, ce serait un champ `static`. Un attribut modifiable se crée toujours dans `__init__`, sur `self`.

**`__len__` et `__contains__`.** Ce sont des méthodes « spéciales » (dunder, pour *double underscore*) : Python les appelle quand on écrit `len(registre)` et `"tva" in registre`. C'est le même principe qu'implémenter `Collection` en Java pour avoir `size()` et `contains()`, sauf qu'ici on ne déclare aucune interface : il suffit d'avoir la méthode, c'est le *duck typing*. Les deux délèguent à la table.

## Bloc 2 — Le décorateur, version de l'étape 77

Un décorateur à paramètres se lit en deux temps. Quand Python rencontre :

```text
@r.outil("double", "Double un nombre.", objet({"x": {"type": "number"}}))
def double(x):
    return 2 * x
```

il exécute exactement `double = r.outil("double", "Double un nombre.", objet(...))(double)`. Premier appel : `r.outil(...)` reçoit le contrat et rend une fonction. Second appel : cette fonction reçoit `double` et rend ce qui sera désormais lié au nom `double`. On reprend d'abord l'écriture de 77, transposée en méthode :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Registre.outil(nom, description, schema)`** — Dans ce brouillon, le décorateur est un greffier qui accepte n'importe quel nom sur le formulaire et ne vérifie les doublons qu'au moment de ranger le dossier : il reçoit le nom, la description et le schéma de l'outil, ne contrôle rien sur le moment et renvoie aussitôt la fonction interne `enregistrer`. Un appel `r.outil("tva", "doublon", objet({}))` fait sans décorer de fonction ne lève donc rien, ce qui fait échouer le test `test_nom_deja_pris_ou_vide`, et un nom vide, qu'aucun modèle ne pourrait appeler, passe sans protester.

**`enregistrer(fonction)`** — Cette fonction interne vit dans `Registre.outil` et reçoit, au second temps du décorateur, la fonction décorée : dans ce brouillon, c'est elle seule qui lève `ValueError` (« outil déjà enregistré ») quand le nom est déjà dans la table, puis elle range un `Outil` qui réunit le nom, la description, le schéma et la fonction, et renvoie la fonction inchangée. Elle enregistre correctement et refuse bien un doublon décoré, mais son contrôle arrive trop tard, une fois seulement qu'une fonction lui est passée.

```python
# [extrait] brouillon
class Registre:
    ...
    def outil(self, nom: str, description: str, schema: dict):
        def enregistrer(fonction: Callable) -> Callable:
            if nom in self.outils:
                raise ValueError(f"outil déjà enregistré : {nom}")
            self.outils[nom] = Outil(nom, description, schema, fonction)
            return fonction
        return enregistrer
```

Elle enregistre bien, et refuse bien un doublon décoré. Mais le test `test_nom_deja_pris_ou_vide` appelle `r.outil("tva", "doublon", objet({}))` **sans** décorer de fonction : le premier temps seul. Dans ce brouillon, le contrôle n'a lieu qu'au second temps, dans `enregistrer` : l'appel ne lève rien, et le test échoue. Il accepte aussi un nom vide, qu'aucun modèle ne pourrait appeler.

## Bloc 3 — Le décorateur, version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Registre.outil(nom, description, schema)`** — C'est le même décorateur, devenu le greffier qui examine le nom dès qu'on le lui tend, avant même d'ouvrir le dossier : il reçoit le nom public, la description destinée au modèle et le schéma, lève `ValueError` (« un outil a un nom non vide ») si le nom est vide, puis `ValueError` (« outil déjà enregistré ») s'il est déjà dans la table, et seulement ensuite renvoie la fonction interne `enregistrer`. L'erreur éclate ainsi dès la ligne `@registre.outil(...)`, au démarrage de l'agent, et un outil n'en écrase jamais un autre en silence.

**`enregistrer(fonction)`** — Cette fonction interne vit dans `Registre.outil` et forme avec elle une fermeture qui voit `self`, `nom`, `description` et `schema` : elle reçoit la fonction décorée, range dans `self.outils` un `Outil` qui réunit les quatre informations, puis renvoie cette fonction telle quelle. C'est ce retour qui permet à `double(4)` de valoir toujours 8 après décoration ; l'oublier ferait lier `None` au nom de la fonction, et le premier appel lèverait `TypeError` loin de la cause.

```python
# [extrait] agent/outils.py
class Registre:
    ...
    def outil(self, nom: str, description: str, schema: dict):
        """Décorateur : enregistre la fonction sous son nom public, avec son contrat.

        Un nom vide ou déjà pris lève `ValueError` ; la fonction décorée est rendue inchangée.
        Exemple : `@registre.outil("tva", "TVA de 5 %", objet({...}))` au-dessus de `def outil_tva(...)`.
        """
        if not nom:
            raise ValueError("un outil a un nom non vide")
        if nom in self.outils:
            raise ValueError(f"outil déjà enregistré : {nom}")

        def enregistrer(fonction: Callable) -> Callable:
            self.outils[nom] = Outil(nom, description, schema, fonction)
            return fonction
        return enregistrer
```

**Les deux gardes, au premier temps.** `if not nom` refuse la chaîne vide (une chaîne vide est « fausse » en Python, comme `None`, `0` ou une liste vide). `if nom in self.outils` refuse un nom déjà pris. Les deux lèvent `ValueError` **avant** de rendre `enregistrer` : l'erreur se produit dès la ligne `@registre.outil(...)`, au démarrage de l'agent, avec un message qui nomme l'outil en cause. Un outil n'en écrase jamais un autre en silence.

**La fonction interne `enregistrer`.** Elle est définie à l'intérieur de `outil`, et elle « voit » `self`, `nom`, `description` et `schema` : c'est une fermeture (*closure*), comme une lambda Java qui capture des variables effectivement finales. Elle construit l'`Outil` et le range dans la table.

**`return fonction`.** La fonction décorée est rendue **inchangée** : `double(4)` vaut toujours 8, et l'on peut tester la fonction métier sans passer par le registre. C'est le piège classique des décorateurs : oublier ce `return`. La fonction rend alors `None`, et Python lie `None` au nom `double` ; le premier appel `double(4)` lève `TypeError: 'NoneType' object is not callable`, loin de la cause.

**`return enregistrer`.** Sans parenthèses : on rend la fonction elle-même, pas le résultat de son appel. C'est ce que Python applique au second temps.

**Décorateur Python ou annotation Java ?** Une annotation `@Component` est une métadonnée inerte : c'est Spring qui, au démarrage, parcourt les classes et décide quoi en faire. Un décorateur Python est du code ordinaire, exécuté immédiatement quand Python lit la définition de la fonction. Ici, `@registre.outil(...)` revient à écrire `registre.enregistrer("double", ..., this::double)` à la main, juste sous la méthode. Cela a une conséquence pratique : les outils ne sont enregistrés que si le code qui les définit s'exécute. C'est pourquoi l'étape 4 les placera dans une fonction, `enregistrer_outils_metier(registre)`, qu'on appelle sur le registre de son choix.

**Le test qui passe maintenant.**

```text
python -m unittest -v tests.test_04_outils.TestRegistre.test_le_decorateur_rend_la_fonction
```

Il décore `double`, vérifie que `double(4)` vaut 8 et que `r.outils["double"].fonction` est bien `double`. `test_nom_deja_pris_ou_vide` utilise le registre des cinq outils métier : il passera à l'étape 4.

**Ce qu'il faut retenir.** La table est un attribut d'instance, créé dans `__init__`. Un décorateur à paramètres, c'est une fonction qui rend une fonction qui reçoit la fonction décorée ; les contrôles se font au premier temps, et le second temps rend la fonction inchangée.
