# Étape 3 — La porte et les appelables

> Palier 04, étape 3 sur 7 · Précédent : [Étape 2 — Le registre et son décorateur](<02-Registre-et-decorateur.md>) · Suivant : [Étape 4 — Les cinq outils métier](<04-Outils-metier.md>) · Retour à l'énoncé : [README](<../../README.md>)

## Comment raisonner

Pars de ce que la boucle du palier 05 aura en main : un bloc `tool_use`, avec un nom (`bloc.name`) et un dictionnaire d'arguments (`bloc.input`), par exemple `{"principal": 1000000, "taux_annuel": 0.045, "n_mois": 300}`. Elle a besoin, pour chaque nom, de quelque chose qu'elle peut appeler avec ce dictionnaire. Ce « quelque chose » ne doit pas être la fonction métier nue : il doit d'abord vérifier le contrat. C'est la porte.

Deux décisions en découlent. La porte reçoit des arguments **nommés**, parce que le modèle envoie un objet JSON, et l'on écrira `porte(**bloc.input)`. Et la validation se fait **avant** l'appel, jamais après : un outil à effet de bord (le virement du palier 09) aurait déjà agi.

## Bloc 1 — Une porte qui ne garde rien

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Registre.porte(nom)`** — Dans ce brouillon, la méthode fabrique un portier qui tient la porte ouverte à tout le monde : elle reçoit un nom d'outil, ne vérifie même pas qu'il existe, et renvoie aussitôt la fonction interne `appeler`. Une faute de frappe comme `porte("virement")` ne lève donc rien à la fabrication ; l'erreur n'apparaîtra qu'au premier appel, sous la forme d'un `KeyError` sans explication, au milieu d'une conversation plutôt qu'au démarrage de l'agent.

**`appeler(arguments)`** — Cette fonction interne vit dans `Registre.porte` et reçoit les arguments nommés envoyés par le modèle, rassemblés dans un dictionnaire par la double étoile de sa signature : dans ce brouillon, elle cherche l'outil dans la table et appelle directement sa fonction avec ces arguments, puis renvoie sa sortie, sans aucune validation. Pour l'outil « compter », qui attend un entier au moins égal à 1 et note chacun de ses appels, `n="3"` atteint donc la fonction, la liste `appels` vaut `["3"]` au lieu de rester vide, et aucune exception n'est levée.

```python
# [extrait] brouillon
class Registre:
    ...
    def porte(self, nom: str) -> Callable:
        def appeler(**arguments):
            return self.outils[nom].fonction(**arguments)
        return appeler
```

Ce brouillon a la bonne forme, une fonction qui rend une fonction, mais il ne fait qu'un détour. Dans le test `test_le_schema_arrete_avant_la_fonction`, l'outil « compter » attend un entier `n` ≥ 1 et note chaque appel dans une liste `appels`. `porte("compter")(n="3")` exécute la fonction avec la chaîne « 3 » : `appels` vaut `["3"]` au lieu de rester vide, et aucune exception n'est levée. Et `porte("virement")` ne lève rien non plus : l'erreur n'apparaîtrait qu'au premier appel, sous la forme d'un `KeyError` sans explication.

## Bloc 2 — La porte, version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Registre.porte(nom)`** — C'est la même méthode, qui fabrique maintenant un vrai portier, posté au démarrage de l'agent devant la salle d'un outil précis : elle reçoit un nom, lève `ValueError` (« outil inconnu ») tout de suite si aucun outil ne le porte, lit l'outil une seule fois dans la table pour que la fonction interne le capture, puis renvoie cette fonction `appeler`. Une faute de frappe dans un nom d'outil se voit ainsi dès la fabrication des portes, comme un contexte Spring qui refuse de démarrer quand un bean manque.

**`appeler(arguments)`** — Cette fonction interne vit dans `Registre.porte` et n'accepte que des arguments nommés, réunis en dictionnaire : elle les valide d'abord avec `validate` contre le schéma complet de l'outil, bornes comprises, lève `ArgumentsInvalides` avec tous les écarts joints par « ; » s'il y en a, et seulement sinon déplie le dictionnaire en arguments nommés pour appeler la fonction métier, dont elle renvoie la sortie. Pour l'outil « compter », `n="3"` produit le message « type attendu integer, reçu string » sur le chemin du champ, un champ `bonus` inventé est refusé comme « champ non prévu », et la liste `appels` reste vide : la fonction n'a jamais été atteinte.

```python
# [extrait] agent/outils.py
class Registre:
    ...
    def porte(self, nom: str) -> Callable:
        """L'appelable que voit la boucle : schéma d'abord, fonction ensuite.

        Exemple : `porte("mensualite")(principal=1_000_000, taux_annuel=0.045, n_mois="300")` lève
        `ArgumentsInvalides("$.n_mois : type attendu integer, reçu string")` sans exécuter le calcul.
        """
        if nom not in self.outils:
            raise ValueError(f"outil inconnu : {nom}")
        o = self.outils[nom]

        def appeler(**arguments):
            erreurs = validate(arguments, o.schema)
            if erreurs:
                raise ArgumentsInvalides(" ; ".join(erreurs))
            return o.fonction(**arguments)
        return appeler
```

**Le contrôle du nom, à la fabrication.** `if nom not in self.outils` lève `ValueError` dès `porte("virement")`, avant tout appel. On fabrique les portes au démarrage de l'agent (étape suivante, `appelables`) : une faute de frappe dans un nom d'outil se voit donc au démarrage, pas au milieu d'une conversation. C'est le principe *fail fast*, celui d'un contexte Spring qui refuse de démarrer quand un bean manque.

**`o = self.outils[nom]`.** On lit l'outil une fois, et la fonction interne le capture. Comme un nom ne peut pas être réenregistré (étape 2), la porte appellera toujours le même outil.

**`def appeler(**arguments)`.** La syntaxe `**arguments` dans une définition rassemble tous les arguments nommés dans un dictionnaire : `appeler(n="3")` donne `arguments == {"n": "3"}`. Java n'a pas d'équivalent direct ; ce serait une méthode qui reçoit une `Map<String, Object>`. La fonction n'accepte **aucun** argument positionnel : `porte("mensualite")(1_000_000, 0.045, 300)` lève `TypeError: ... takes 0 positional arguments but 3 were given`. C'est une sécurité : des arguments sans nom ne pourraient pas être validés contre un schéma d'objet.

**La validation.** `validate(arguments, o.schema)` est la fonction du palier 02, appliquée au schéma **complet** de l'outil, bornes comprises. Elle rend la liste des écarts, chacun avec son chemin JSON : `["$.n : type attendu integer, reçu string"]`. Une liste vide est fausse en Python, d'où `if erreurs:`.

**Le refus.** `raise ArgumentsInvalides(" ; ".join(erreurs))` met tous les écarts dans un seul message, séparés par « ; » : le modèle les lira tous en une fois et pourra tout corriger au prochain essai, au lieu de découvrir les erreurs une par une. Pour `n=1, bonus=True`, le message vaut `$ : champ non prévu « bonus »` : le schéma construit par `objet` refuse tout champ non prévu (`additionalProperties` faux), ce qui empêche le modèle d'inventer un paramètre.

**L'appel.** `o.fonction(**arguments)` : ici, `**` fait l'inverse, il déplie le dictionnaire en arguments nommés. `{"principal": 1000000, "taux_annuel": 0.045, "n_mois": 300}` devient `fonction(principal=1000000, taux_annuel=0.045, n_mois=300)`. Les noms des clés doivent donc être exactement ceux des paramètres de la fonction : c'est le schéma qui le garantit, puisqu'il exige les champs obligatoires et refuse les autres.

**Analogie Spring.** La porte est l'aspect qui entoure la méthode : `@Valid` vérifie le corps de la requête, et la méthode du contrôleur n'est jamais appelée si la validation échoue. Au palier 09, `proteger` ajoutera une seconde enveloppe autour de cette porte, pour la politique d'accès, comme un `@PreAuthorize` placé avant `@Valid`.

**Le test qui passe maintenant.**

```text
python -m unittest -v tests.test_04_outils.TestPorte.test_le_schema_arrete_avant_la_fonction
```

Il vérifie le message exact `$.n : type attendu integer, reçu string`, le refus du champ `bonus`, et que la liste `appels` est restée vide : la fonction n'a jamais été atteinte.

## Bloc 3 — Les appelables, version piégée

La boucle veut un dictionnaire nom → porte. Le réflexe d'un développeur Java est d'écrire une lambda par outil :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Registre.appelables()`** — Dans ce brouillon, la méthode ressemble à un concierge qui étiquette cinq clés différentes mais les accroche toutes au même anneau : elle ne reçoit rien et renvoie un dictionnaire qui associe à chaque nom une lambda chargée d'appeler `self.porte(nom)` au moment de l'usage. Chaque lambda capture la variable `nom` et non sa valeur, qu'elle ne lit qu'à l'appel, une fois la compréhension terminée : les cinq entrées appellent alors la porte de « tva », et l'entrée « mensualite », appelée avec les bons arguments, lève `ArgumentsInvalides` parce que le champ `montant_ht` manque.

```python
# [extrait] brouillon
class Registre:
    ...
    def appelables(self) -> dict[str, Callable]:
        return {nom: (lambda **a: self.porte(nom)(**a)) for nom in self.outils}
```

Sur le registre des cinq outils métier, appeler l'entrée « mensualite » avec les bons arguments lève pourtant `ArgumentsInvalides` : `$ : champ obligatoire absent « montant_ht »`, puis trois champs « non prévus ». C'est la porte de « tva » qui a répondu. Chaque lambda capture la **variable** `nom`, pas sa valeur ; elle ne la lit qu'au moment où on l'appelle, et à ce moment la compréhension est terminée : `nom` vaut sa dernière valeur, « tva ». Les cinq entrées appellent le même outil. Java interdit ce bug, puisqu'une lambda ne peut capturer qu'une variable effectivement finale ; Python l'autorise.

## Bloc 4 — Les appelables, version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Registre.appelables()`** — C'est la même méthode, devenue le concierge soigneux qui taille une clé distincte pour chaque porte au moment même où il l'étiquette : elle ne reçoit rien et renvoie un dictionnaire nom → porte, construit par une compréhension qui appelle `self.porte(nom)` tout de suite, une fois par outil, dans l'ordre de la table. Chaque appel ouvre son propre cadre d'exécution, si bien que chaque porte capture un nom qui ne changera plus ; c'est ce dictionnaire que la boucle du palier 05 recevra, et sur un petit registre, l'entrée « double » appelée avec 21 renvoie bien 42.

```python
# [extrait] agent/outils.py
class Registre:
    ...
    def appelables(self) -> dict[str, Callable]:
        """Le dictionnaire nom → porte que l'on passe à la boucle d'agent."""
        return {nom: self.porte(nom) for nom in self.outils}
```

**Pourquoi c'est juste.** `self.porte(nom)` est **appelé** tout de suite, une fois par nom, pendant la compréhension. Chaque appel ouvre un nouveau cadre d'exécution, avec son propre paramètre `nom`, et la fonction `appeler` qu'il rend capture ce paramètre-là, qui ne changera plus. Les portes sont donc fabriquées au démarrage, et chaque nom inconnu (impossible ici, puisqu'on parcourt la table) serait signalé à ce moment.

**La compréhension de dictionnaire.** `{clé: valeur for élément in itérable}` construit un dictionnaire en une ligne, comme `stream().collect(Collectors.toMap(...))`. Parcourir `self.outils` parcourt ses clés, dans l'ordre d'insertion.

**Vérifier à la console**, avec un petit registre :

```text
>>> from agent.outils import Registre
>>> from agent.schemas import objet
>>> r = Registre()
>>> @r.outil("double", "Double un nombre.", objet({"x": {"type": "number"}}))
... def double(x):
...     return 2 * x
...
>>> r.appelables()["double"](x=21)
42
```

Les tests de `appelables` sur les cinq outils métier passeront à l'étape 4.

**Ce qu'il faut retenir.** La porte est une fermeture qui valide **avant** d'appeler, reçoit des arguments nommés seulement, et réunit tous les écarts dans un seul message. Dans une boucle ou une compréhension, ne jamais capturer la variable de boucle dans une lambda : appeler une fonction qui fabrique la fermeture.
