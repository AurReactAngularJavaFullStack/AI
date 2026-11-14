# Étape 7 — Assemblage et démo

> Palier 04, étape 7 sur 7 · Précédent : [Étape 6 — L'enveloppe d'erreur](<06-Executer-appel.md>) · Suivant : [Palier 05 — Boucle d'agent](<../../../05-Boucle-d-Agent/README.md>) · Retour à l'énoncé : [README](<../../README.md>)

## Comment raisonner

Les pièces sont écrites. Relis le module de haut en bas en te demandant, pour chaque ligne, qui l'appellera : la boucle du palier 05, les garde-fous du palier 09, l'assemblage du palier 12. Puis lance toute la suite de tests, et la démo.

## Bloc 1 — Le plan du module

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Registre.__init__()`** — C'est le constructeur de l'étape 2, qui ouvre le grand livre vide de l'archiviste : il ne reçoit rien et crée sur `self` la table `outils`, un dictionnaire nom → `Outil` qui garde l'ordre d'inscription. Parce que la table naît ici et non au niveau de la classe, il n'existe aucune variable globale modifiable dans le module : chaque `Registre()` est neuf, et la démo comme chaque test travaillent sur le leur.

**`Registre.__len__()`** — C'est la méthode spéciale de l'étape 2 que Python appelle derrière `len(registre)` : elle ne reçoit rien et renvoie le nombre d'outils de la table, comme un archiviste qui compte ses fiches. Au point 1 de la démo, elle annonce les 5 outils du registre de la banque B-1, avant que leurs noms ne soient affichés dans l'ordre d'inscription.

**`Registre.__contains__(nom)`** — C'est l'autre méthode spéciale de l'étape 2, celle de l'opérateur `in` : elle reçoit un nom et renvoie vrai si un outil de la table le porte, faux sinon. Le décorateur s'en sert pour refuser un nom déjà pris, et l'on peut écrire `"tva" in registre` comme une phrase ; sur le registre de la démo, « virement » n'y figure pas.

**`Registre.outil(nom, description, schema)`** — C'est le décorateur à paramètres de l'étape 2, le greffier qui contrôle le nom dès qu'on le lui tend : il reçoit le nom public, la description et le schéma, lève `ValueError` si le nom est vide ou déjà pris, puis renvoie la fonction interne qui range l'`Outil` dans la table et rend la fonction décorée inchangée. C'est par lui que `enregistrer_outils_metier` inscrit les cinq outils métier.

**`Registre.porte(nom)`** — C'est la méthode de l'étape 3, qui fabrique le portier d'un outil : elle reçoit un nom, lève `ValueError` s'il est inconnu, et renvoie une fonction qui n'accepte que des arguments nommés, les valide contre le schéma complet et lève `ArgumentsInvalides` avec tous les écarts, avant d'appeler la fonction métier seulement s'ils sont conformes. Au point 3 de la démo, une durée écrite « 300 » est arrêtée avec son chemin JSON, sans que le calcul soit exécuté.

**`Registre.appelables()`** — C'est la méthode de l'étape 3 qui remet à la boucle le trousseau complet : elle ne reçoit rien et renvoie un dictionnaire nom → porte, fabriqué par un appel à `porte` pour chaque outil, ce qui évite le piège de la lambda qui capture la variable de boucle. Au point 2 de la démo, ses portes rendent une mensualité de 5558,32, un ratio de 0,289 recevable et 1513,5 USD.

**`Registre.definitions_api()`** — C'est la méthode de l'étape 5 qui rédige la carte présentée au modèle : elle ne reçoit rien et renvoie une définition par outil, dans l'ordre du registre, avec le nom, la description, `strict` à `True` et le schéma allégé par `schema_pour_api_strict`, dont les bornes sont recopiées dans la description. Au point 1 de la démo, toutes les définitions sont strictes, et `n_mois` part sans ses bornes de 1 et 300.

**`executer_appel(outils, bloc)`** — C'est la fonction libre de l'étape 6, l'agent de liaison qui ne laisse jamais sortir d'exception : elle reçoit un dictionnaire d'appelables et un bloc `tool_use`, et renvoie toujours un `tool_result` avec sa ligne de trace, succès en JSON ou erreur marquée `is_error` dont le contenu commence par le nom de la classe. Au point 4 de la démo, la TVA de 12 000 AED réussit, un montant de −5 est refusé par le schéma, et l'outil « virement », inconnu, donne une `ErreurOutil`.

**`enregistrer_outils_metier(registre)`** — C'est la fonction libre de l'étape 4, la cérémonie d'embauche des calculateurs du palier 03 : elle reçoit un registre, y inscrit dans l'ordre « mensualite », « ratio_endettement », « convertir_aed_usd », « gratuite_fin_de_service » et « tva », chacun avec un schéma construit par `objet` et une sortie arrondie, puis renvoie ce registre complété. C'est elle qui fournit les 5 outils que la démo énumère au point 1.

```python
# [extrait] agent/outils.py
@dataclass
class Outil:
    ...


class RefusPolitique(PermissionError):
    ...


class ArgumentsInvalides(ValueError):
    ...


class ErreurOutil(Exception):
    ...


class Registre:
    ...

    def __init__(self) -> None:
        ...

    def __len__(self) -> int:
        ...

    def __contains__(self, nom: str) -> bool:
        ...

    def outil(self, nom: str, description: str, schema: dict):
        ...

    def porte(self, nom: str) -> Callable:
        ...

    def appelables(self) -> dict[str, Callable]:
        ...

    def definitions_api(self) -> list[dict]:
        ...


def executer_appel(outils: dict, bloc) -> tuple[dict, tuple]:
    ...


def enregistrer_outils_metier(registre: Registre) -> Registre:
    ...
```

Les `...` remplacent les corps écrits aux étapes 1 à 6. Le module se lit en trois couches.

1. **Les données** : `Outil` et les trois exceptions. Aucune logique.
2. **Le registre** : la table, le décorateur qui la remplit, la porte qui garde chaque outil, et deux vues dérivées de la même table, `appelables` pour la boucle et `definitions_api` pour le modèle.
3. **Deux fonctions libres** : `executer_appel`, qui ne dépend que d'un dictionnaire d'appelables et pas du registre (la boucle pourra lui passer les portes protégées du palier 09), et `enregistrer_outils_metier`, qui remplit un registre avec les cinq outils du palier 03.

**Ce que le module ne contient pas.** Aucune variable globale modifiable : `Registre()` crée une table neuve à chaque fois. Aucun contrôle de politique : la porte ne vérifie que le schéma. Aucune boucle d'agent : `executer_appel` traite un bloc, et c'est le palier 05 qui les enchaînera.

## Bloc 2 — Toute la suite de tests

Depuis `projet/` :

```text
python -m unittest -v
```

La fin de la sortie doit être :

```text
----------------------------------------------------------------------
Ran 58 tests in 0.025s

OK
```

58 tests : les 46 des paliers 01 à 03 et les 12 du palier 04. La durée varie d'une machine à l'autre. Si un test du palier 04 échoue encore, relance-le seul : le message d'`assertEqual` montre côte à côte le dictionnaire obtenu et le dictionnaire attendu, et la différence porte presque toujours sur un nom de clé, un arrondi ou un message d'erreur.

## Bloc 3 — La démo

```text
python demo.py
```

```text
Palier 04 — les outils de la banque B-1, derrière leur porte
1. 5 outils : mensualite, ratio_endettement, convertir_aed_usd, gratuite_fin_de_service, tva
   définitions API strictes : True ; n_mois envoyé : {'type': 'integer', 'description': 'Contraintes : minimum=1, maximum=300.'}
2. mensualite(1 000 000 AED, 4,5 %, 300 mois) → {'mensualite_aed': 5558.32}
   ratio_endettement(6 000, 5 558,32, 40 000) → {'ratio': 0.289, 'recevable': True}
   convertir_aed_usd(5 558,32) → {'montant_usd': 1513.5}
3. n_mois="300" arrêté par le schéma, la fonction n'est pas exécutée : $.n_mois : type attendu integer, reçu string
4. tva({'montant_ht': 12000}) → is_error = False ; {"tva_aed": 600.0, "ttc_aed": 12600.0}
4. tva({'montant_ht': -5}) → is_error = True ; ArgumentsInvalides: $.montant_ht : -5 < minimum 0
4. virement({'montant_aed': 180000}) → is_error = True ; ErreurOutil: outil inconnu : virement
OK — palier 04 terminé.
```

Chaque point de la sortie vient d'une pièce que tu as écrite.

- Point 1 : `len(registre)` et l'ordre de `registre.outils` (étapes 2 et 4), puis `definitions_api` (étape 5) : toutes les définitions sont strictes, et `n_mois` part sans ses bornes, recopiées dans la description.
- Point 2 : trois appels par `appelables()` (étapes 3 et 4). Les sorties sont des dictionnaires Python, affichés avec des apostrophes, et arrondis comme dans 77.
- Point 3 : la porte lève `ArgumentsInvalides` avant d'appeler le calcul, avec le chemin JSON du champ fautif.
- Point 4 : `executer_appel` (étape 6) sur trois blocs. Le premier réussit, et son contenu est du JSON (guillemets doubles) ; le deuxième est arrêté par le schéma (`"minimum": 0`) ; le troisième demande un outil qui n'existe pas. Dans les deux derniers cas, aucune exception ne sort : la démo continue, et le modèle recevrait ces deux messages pour se corriger. Le « virement » de 180 000 AED n'existe pas encore : il arrivera au palier 09, protégé par la politique, le score de risque et l'approbation humaine.

## Ce que tu as appris

- Un outil, ce sont quatre champs : un nom, une description et un schéma pour le modèle, une fonction pour le programme.
- Chaque façon d'échouer a sa classe d'exception, sous la bonne classe mère, parce que le nom de la classe est une information pour le modèle.
- Un registre est un objet, pas une variable globale ; sa table se crée dans `__init__`.
- Un décorateur à paramètres est une fonction qui rend une fonction ; on contrôle au premier temps, on rend la fonction décorée inchangée au second.
- La porte valide **avant** d'appeler, avec des arguments nommés seulement, et réunit tous les écarts dans un seul message.
- Une lambda dans une compréhension capture la variable, pas sa valeur : on fabrique les fermetures par un appel de fonction.
- Les définitions pour l'API se dérivent du registre ; le schéma envoyé est une copie sans bornes, et la porte seule vérifie les bornes.
- `executer_appel` ne lève jamais : toute erreur devient un `tool_result` marqué `is_error`, que le modèle lira.

**Les écarts avec l'étape 77, en résumé.** Pas de `REGISTRE` global, mais un objet `Registre` passé en paramètre ; le décorateur, la porte et les définitions deviennent ses méthodes, et `appelables` remplace `OUTILS_AGENT` ; la porte ne vérifie que le schéma, la politique arrivant au palier 09 par composition (`proteger` enveloppe `registre.porte(nom)`) ; et le `try`/`except` de la boucle devient la fonction `executer_appel`, qui renvoie une enveloppe `is_error` au lieu de laisser sortir une exception.

## La suite : le palier 05

Tu as maintenant tout ce qu'il faut pour l'étape « agir ». Au [palier 05 — Boucle d'agent](<../../../05-Boucle-d-Agent/README.md>), tu écris `executer_agent`, la boucle percevoir → décider → agir → observer : elle envoie au modèle la question et `definitions_api()`, passe chacun de ses blocs `tool_use` à `executer_appel` avec les portes de `appelables()`, renvoie tous les `tool_result` d'une étape dans un seul message, et s'arrête dans tous les cas : fin de tour, nombre maximal d'étapes, ou action répétée à l'identique.
