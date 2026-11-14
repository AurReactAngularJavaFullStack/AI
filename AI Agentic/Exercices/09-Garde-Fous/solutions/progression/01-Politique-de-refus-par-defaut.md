# Étape 1 — La politique de refus par défaut

> [Énoncé du palier 09](<../../README.md>) · Suivant : [Étape 2 — Masquer les données personnelles](<02-Masquer-les-donnees-personnelles.md>)

## Comment raisonner

Devant la feuille blanche, on commence par la question la plus simple et la plus importante : **qui a le droit d'appeler quoi ?** Tant qu'elle n'a pas de réponse dans le code, tous les autres garde-fous sont contournables, puisque n'importe quel rôle pourrait appeler n'importe quel outil.

On écrit d'abord la **donnée** (la table de politique), ensuite la **fonction** qui la lit. C'est l'ordre naturel : la table fixe le vocabulaire (rôle, outil, portée), et la fonction n'a plus qu'à la parcourir. On choisit enfin la règle par défaut : tout ce qui n'est pas écrit dans la table est **refusé**. Une politique qui autorise par défaut et liste des interdictions finit toujours par oublier un outil ajouté plus tard ; une politique qui refuse par défaut oublie, au pire, une autorisation, et l'erreur se voit tout de suite.

## La table : rôle → outil → portées requises

```python
# [extrait] agent/garde_fous.py
LECTURE = {"lecture"}
POLITIQUE = {                                  # rôle → outil → portées requises ; tout le reste est refusé
    "client_banque": dict.fromkeys(["rechercher_reglementation", "mensualite", "ratio_endettement",
                                    "convertir_aed_usd", "gratuite_fin_de_service", "tva"], LECTURE)
                     | {"initier_virement": {"lecture", "virement:initier"}},
    "assistant_public": dict.fromkeys(["rechercher_reglementation", "tva"], LECTURE),
}
```

**Ligne par ligne.**

- `LECTURE = {"lecture"}` nomme l'ensemble de portées le plus courant. Une portée (scope) est une permission élémentaire, accordée par l'authentification : `lecture`, `virement:initier`.
- `dict.fromkeys([...], LECTURE)` fabrique un dictionnaire dont chaque clé (un nom d'outil) vaut `LECTURE`. C'est l'équivalent d'une boucle qui ferait `regles[outil] = LECTURE` pour chacun des six outils de lecture.
- `| {"initier_virement": {...}}` est l'union de deux dictionnaires (Python 3.9 et suivants) : on ajoute l'outil de virement, qui demande **deux** portées.
- Le rôle `assistant_public` (un assistant sans client authentifié) n'a que la recherche et la TVA.

**Analogie Java.** Le type est `Map<String, Map<String, Set<String>>>`. Dans Spring Security, c'est l'équivalent d'une configuration `requestMatchers(...).hasAuthority(...)` écrite sous forme de données plutôt que de code : la table peut être relue, testée et auditée sans exécuter quoi que ce soit.

**Le piège.** `dict.fromkeys` met le **même** objet `LECTURE` sous les six clés (`regles["tva"] is LECTURE` est vrai). Si l'on modifiait un jour `regles["tva"].add("ecriture")`, les six outils recevraient la portée en même temps. Ce n'est pas un problème ici, parce que personne ne modifie la table, mais c'est un réflexe à avoir : en Java, ce serait partager la même instance de `HashSet` entre plusieurs entrées d'une `Map`.

## Un brouillon, et ce qui ne va pas

Le premier réflexe donne souvent ceci :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`autoriser(role, outil, portees)`** — Ce brouillon ressemble à un portier distrait qui vérifie seulement que le nom du visiteur figure sur la liste de l'étage, sans jamais regarder son badge. Il reçoit le rôle, l'outil et les portées de la session, cherche les règles du rôle avec `POLITIQUE.get(role, {})`, qui rend un dictionnaire vide pour un rôle inconnu, et rend `(True, "autorisé")` dès que l'outil figure dans ces règles, `(False, "refusé")` dans tous les autres cas. Le paramètre `portees` n'est jamais lu, et le motif unique « refusé » ne dit pas lequel des trois contrôles a échoué : c'est précisément ce que la version suivante va corriger.

```python
# [extrait] brouillon
def autoriser(role, outil, portees):
    if outil in POLITIQUE.get(role, {}):
        return True, "autorisé"
    return False, "refusé"
```

Trois défauts. Il **ignore les portées** : un client qui n'a que `lecture` pourrait initier un virement. Il donne **un seul motif** pour trois causes différentes, si bien que le journal d'audit ne dira jamais pourquoi un appel a été refusé. Et `POLITIQUE.get(role, {})` confond « rôle inconnu » et « rôle sans outil », alors qu'un rôle inconnu est souvent le signe d'une session mal construite, à signaler comme tel.

## La fonction

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`autoriser(role, outil, portees, politique)`** — Cette fois, le portier fait son métier jusqu'au bout et sait dire pourquoi il refuse. La fonction reçoit le rôle, l'outil, les portées de la session sous n'importe quelle forme itérable et une politique facultative ; elle choisit la table `POLITIQUE` si `politique` vaut `None`, sinon celle qu'on lui donne, puis cherche les règles du rôle et rend `(False, "rôle inconnu : …")` s'il n'y en a pas, en écrivant `(aucun)` pour un rôle vide. Elle cherche ensuite les portées requises par l'outil et rend `(False, "outil … non autorisé pour le rôle …")` s'il est absent, puis calcule la différence triée entre ces portées requises et celles de la session et rend `(False, "portée manquante : …")` si elle n'est pas vide. Ce n'est qu'après ces trois épreuves qu'elle rend `(True, "autorisé")`, sans jamais lever d'exception : la conséquence d'un refus appartient à l'enveloppe de l'étape 7.

```python
# [extrait] agent/garde_fous.py
def autoriser(role: str, outil: str, portees: set, politique: dict | None = None) -> tuple[bool, str]:
    ...
    regles = (POLITIQUE if politique is None else politique).get(role)
    if regles is None:
        return False, f"rôle inconnu : {role or '(aucun)'}"
    requises = regles.get(outil)
    if requises is None:
        return False, f"outil {outil} non autorisé pour le rôle {role}"
    manquantes = sorted(requises - set(portees))
    if manquantes:
        return False, "portée manquante : " + ", ".join(manquantes)
    return True, "autorisé"
```

**Ligne par ligne.**

- `(POLITIQUE if politique is None else politique)` choisit la table : celle du module par défaut, ou celle que l'appelant fournit (un test, un autre métier). `.get(role)` rend `None` si le rôle n'existe pas, sans lever d'exception.
- Premier test : rôle inconnu. `role or '(aucun)'` affiche `(aucun)` quand le rôle est la chaîne vide, pour que le motif reste lisible dans le journal.
- Deuxième test : l'outil n'est pas dans les règles du rôle. C'est le refus par défaut à l'état pur : il n'y a aucune ligne « interdire », seulement l'absence d'une ligne « autoriser ».
- Troisième test : `requises - set(portees)` est la différence d'ensembles, les portées demandées par l'outil que la session n'a pas. `set(portees)` accepte une liste ou un tuple aussi bien qu'un ensemble ; `sorted` rend le motif déterministe, car l'ordre d'itération d'un `set` de chaînes peut changer d'une exécution à l'autre.
- Si les trois tests passent, et seulement alors, `(True, "autorisé")`.

**Pourquoi un couple (booléen, motif) et pas une exception ?** La fonction **décide**, elle n'agit pas. C'est l'enveloppe de l'étape 7 qui transformera un refus en `RefusPolitique`, après l'avoir journalisé. Séparer la décision de sa conséquence rend `autoriser` testable en une ligne, sans `assertRaises`.

**Analogie Java.** C'est un `AuthorizationManager` de Spring Security qui rendrait une `AuthorizationDecision` accompagnée de sa raison. La différence d'ensembles s'écrirait `Set<String> manquantes = new TreeSet<>(requises); manquantes.removeAll(portees);`, le `TreeSet` jouant le rôle de `sorted`.

**Le piège classique.** Écrire `regles = (politique or POLITIQUE).get(role)`. Une politique vide, `{}`, est « fausse » en Python, et `or` retomberait alors sur la table complète : l'appelant qui voulait **tout interdire** donnerait au contraire tous les droits. Le test `is None` ne confond pas « pas de politique fournie » et « politique vide ».

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_09_garde_fous.TestPolitique
```

`test_trois_refus_et_un_accord` vérifie les trois motifs et l'accord, exactement comme dans l'énoncé : `assistant_public` n'a pas `initier_virement`, le rôle vide est inconnu, `client_banque` avec la seule portée `lecture` manque de `virement:initier`. `test_politique_personnalisee` passe une table `{"rh": {"gratuite_fin_de_service": {"paie:lire"}}}` : le rôle `rh` est autorisé avec sa portée, et `client_banque`, absent de cette table, est refusé même pour la TVA, preuve que la table fournie remplace bien celle du module.
