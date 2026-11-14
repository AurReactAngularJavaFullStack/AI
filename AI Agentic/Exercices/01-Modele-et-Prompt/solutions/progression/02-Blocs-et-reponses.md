# Étape 2 — Blocs et réponses

> Palier 01, étape 2 sur 7 · Précédent : [Étape 1 — L'horloge simulée](<01-Horloge-simulee.md>) · Suivant : [Étape 3 — Le faux modèle](<03-Faux-modele-FakeLLM.md>) · [Retour à l'énoncé](<../../README.md>)

**Objectif de l'étape :** écrire les données qui circulent entre l'agent et le modèle : `Bloc`, `STOP_REASONS`, `Reponse`, puis les deux fabriques `texte` et `appel_outil`. Le test `TestPortLLM.test_blocs` passe à la fin.

## Comment raisonner

Avant d'écrire un faux modèle, il faut savoir **ce qu'un modèle rend**. On ne l'invente pas : on recopie la forme des réponses de l'API Claude, pour que le jour où l'on branche le vrai modèle (palier 12), la boucle n'ait pas une ligne à changer. Une réponse de l'API porte deux choses :

1. `stop_reason` : pourquoi le modèle s'est arrêté (il a fini, il veut un outil, il a été coupé, il refuse…) ;
2. `content` : une **liste** de blocs, parce qu'une seule réponse peut contenir du texte puis deux demandes d'outils.

Chaque bloc a un `type`. Un bloc `"text"` porte du texte ; un bloc `"tool_use"` porte un identifiant d'appel, un nom d'outil et des arguments. On pourrait faire deux classes, mais l'API n'en a qu'une forme avec des champs optionnels, et la boucle lit `b.type`, `b.text`, `b.name`, `b.input` sans se demander de quelle classe vient le bloc. On écrit donc **une** classe `Bloc` avec cinq champs, dont quatre ont une valeur par défaut.

L'ordre d'écriture suit les dépendances : `Bloc` d'abord, puis `Reponse` qui contient des blocs, puis les fabriques qui construisent des blocs.

## Le piège du dictionnaire par défaut

```python
# [extrait] brouillon
from dataclasses import dataclass


@dataclass
class Bloc:
    type: str
    text: str = ""
    id: str = ""
    name: str = ""
    input: dict = {}            # ValueError dès la définition de la classe
```

Ce brouillon semble naturel : « par défaut, pas d'arguments ». Python refuse pourtant de créer la classe :

```text
# [extrait] console
>>> @dataclass
... class Bloc:
...     input: dict = {}
...
Traceback (most recent call last):
  (lignes de la pile, raccourcies)
ValueError: mutable default <class 'dict'> for field input is not allowed: use default_factory
```

La raison : la valeur par défaut est évaluée **une seule fois**, quand la classe est définie. Tous les blocs partageraient alors le **même** dictionnaire, et un outil qui écrirait dans `bloc.input` d'un bloc modifierait les arguments de tous les autres. C'est le piège le plus célèbre de Python (le même existe avec `def f(x=[])`). Les dataclasses le détectent et refusent. En Java, ce serait un champ `static` partagé par toutes les instances au lieu d'un `new HashMap<>()` dans chaque constructeur.

## La classe Bloc

```python
# [extrait] agent/modele.py
@dataclass
class Bloc:
    """Un bloc de contenu, à la forme des blocs de l'API Claude.

    `type` vaut "text" (champ `text`) ou "tool_use" (champs `id`, `name`, `input`).
    Exemple : `Bloc(type="text", text="Bonjour").text` vaut "Bonjour".
    """
    type: str
    text: str = ""
    id: str = ""
    name: str = ""
    input: dict = field(default_factory=dict)
```

**`@dataclass`.** Ce décorateur lit les champs annotés du corps de la classe et génère pour toi le constructeur `__init__(self, type, text="", id="", name="", input=...)`, l'affichage `__repr__` et l'égalité `__eq__`. C'est l'équivalent d'un `record` Java, ou d'une classe Lombok `@Data`. Dans le squelette, cette classe est fournie telle quelle : ses champs sont le contrat avec les tests.

**Les champs.** `type: str` n'a pas de valeur par défaut : il est obligatoire et vient en premier (un champ sans défaut ne peut pas suivre un champ avec défaut). `text`, `id` et `name` valent la chaîne vide par défaut ; une chaîne est immuable, donc la partager ne pose aucun problème.

**`field(default_factory=dict)`.** C'est la correction du brouillon : au lieu d'une valeur, on donne une **fabrique**, ici la fonction `dict`, que la dataclass appelle à chaque création de bloc. Chaque bloc reçoit son propre dictionnaire vide.

**Les noms `type`, `id` et `input`.** Ce sont aussi des fonctions natives de Python. Comme noms de champs, ils ne gênent pas (on écrit `bloc.type`, jamais `type` seul dans la classe), et on les garde parce que ce sont les noms de l'API : un bloc du SDK Anthropic a exactement ces attributs.

## Les raisons d'arrêt et la classe Reponse

```python
# [extrait] agent/modele.py
STOP_REASONS = ("end_turn", "tool_use", "max_tokens", "refusal", "pause_turn")


@dataclass
class Reponse:
    """Une réponse du modèle : pourquoi il s'est arrêté (`stop_reason`) et ce qu'il a produit (`content`).

    Exemple : `Reponse("end_turn", [texte("Fini.")])` est une réponse finale d'un seul bloc de texte.
    """
    stop_reason: str               # "end_turn", "tool_use", "max_tokens", "refusal", "pause_turn"
    content: list
```

**`STOP_REASONS`.** Un tuple des cinq valeurs possibles, à lire comme une documentation exécutable. Voici ce que chacune déclenchera dans la boucle du palier 05 :

| Valeur | Ce que le modèle signale | Ce que fera la boucle |
| --- | --- | --- |
| `"end_turn"` | il a fini sa réponse | arrêt avec le statut `fini` et le texte final |
| `"tool_use"` | il demande un ou plusieurs outils | exécution des outils, résultats renvoyés au modèle |
| `"max_tokens"` | il a été coupé par la limite de longueur | arrêt avec le statut `tronque` |
| `"refusal"` | il refuse de répondre | arrêt avec le statut `refus`, avant de lire le contenu |
| `"pause_turn"` | l'API a mis le tour en pause | nouvel appel, sans rien exécuter |

On choisit un tuple plutôt qu'une liste parce qu'il est immuable : personne ne pourra y ajouter une valeur par erreur. En Java, ce serait un `enum StopReason` ; on garde des chaînes parce que l'API envoie des chaînes et que la boucle les compare directement.

**`Reponse`.** Deux champs obligatoires, sans valeur par défaut. `content: list` reste une liste de `Bloc` ; l'annotation dit seulement `list` parce qu'une réponse du vrai SDK contient aussi d'autres types de blocs (par exemple des blocs de réflexion), que la boucle recopie sans les lire. On construit une réponse par position, `Reponse("end_turn", [...])`, ou par nom, `Reponse(stop_reason="end_turn", content=[...])`.

**Le piège classique.** Croire que la dataclass vérifie les types : `Reponse(42, "pas une liste")` est accepté sans erreur. Les annotations décrivent, elles ne contrôlent pas. Le contrôle des données venues du modèle sera le travail du palier 02.

## Les deux fabriques

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`texte(t)`** — Cette fabrique est le tampon d'un employé de bureau qui imprime toujours le même formulaire : elle reçoit une chaîne t et renvoie un `Bloc` de type `"text"` dont le champ `text` porte cette chaîne, en nommant les arguments pour ne pas dépendre de l'ordre des champs, les autres gardant leur valeur par défaut. Elle sert aux scripts du faux modèle de tous les paliers suivants, qui écrivent des dizaines de réponses : `texte("Fini.")` se lit mieux que le constructeur complet, et deux appels identiques donnent deux blocs égaux, puisque la dataclass compare les champs un à un.

**`appel_outil(nom, arguments, id_)`** — Celle-ci remplit le bon de commande que le modèle adresse à l'agent quand il réclame un outil : elle reçoit le nom de l'outil, le dictionnaire de ses arguments et l'identifiant de l'appel, puis renvoie un `Bloc` de type `"tool_use"` en traduisant les paramètres français vers les champs anglais de l'API, `id_` dans `id`, `nom` dans `name` et `arguments` dans `input`. Le tiret bas de `id_` évite de masquer la fonction native `id` ; l'appel pour l'outil « tva » avec un montant hors taxe de 12 000 et l'identifiant « t1 » produit ainsi le bloc que la console affiche plus bas, et la chaîne `"tool_use"` n'est écrite qu'à un seul endroit.

```python
# [extrait] agent/modele.py
def texte(t: str) -> Bloc:
    """Bloc de texte. Exemple : `texte("Mensualité 5 558,32 AED").type` vaut "text"."""
    return Bloc(type="text", text=t)


def appel_outil(nom: str, arguments: dict, id_: str) -> Bloc:
    """Bloc `tool_use` : le modèle demande l'outil `nom` avec `arguments`.

    Exemple : `appel_outil("tva", {"montant_ht": 12_000}, "t1").name` vaut "tva".
    """
    return Bloc(type="tool_use", id=id_, name=nom, input=arguments)
```

**Pourquoi des fabriques.** Les scripts du faux modèle, dans tous les tests des paliers suivants, écriront des dizaines de blocs. `texte("Fini.")` se lit mieux que `Bloc(type="text", text="Fini.")`, et une faute de frappe dans la chaîne `"tool_use"` devient impossible puisqu'elle n'est écrite qu'une fois. C'est le rôle d'une méthode de fabrique statique en Java, comme `List.of(...)` ou `Optional.of(...)`.

**`return Bloc(type="text", text=t)`.** Les arguments sont **nommés** : on n'a pas à se souvenir que `text` est le deuxième champ. Les champs non cités gardent leur défaut.

**`appel_outil(nom, arguments, id_)`.** Les paramètres sont en français, les champs du bloc en anglais : la ligne fait la traduction, `id=id_`, `name=nom`, `input=arguments`. Le tiret bas final de `id_` est la convention Python pour éviter de masquer la fonction native `id` dans le corps de la fonction.

**Le piège classique.** Écrire `Bloc("tool_use", nom, arguments, id_)` par position : `nom` irait dans `text`, `arguments` dans `id`, et ainsi de suite. Rien ne plante ici, mais la boucle du palier 05 lirait un `name` vide. Les arguments nommés évitent ce genre d'erreur silencieuse.

**Le test qui passe maintenant.**

```powershell
python -m unittest -v tests.test_01_modele.TestPortLLM.test_blocs
```

Il vérifie que `appel_outil("tva", {"montant_ht": 12_000}, "t1")` a pour type, nom, identifiant et arguments `("tool_use", "tva", "t1", {"montant_ht": 12000})`, que `texte("Fini.")` a le type `"text"` et le texte `"Fini."`, et que `Bloc(type="text").input` vaut `{}`. Les deux autres tests de `TestPortLLM` attendent `FakeLLM`.

Pour voir ce que la dataclass a généré, une session interactive depuis `projet/` :

```text
# [extrait] console
>>> from agent.modele import appel_outil, texte
>>> appel_outil("tva", {"montant_ht": 12_000}, "t1")
Bloc(type='tool_use', text='', id='t1', name='tva', input={'montant_ht': 12000})
>>> texte("Fini.") == texte("Fini.")
True
```

L'égalité vaut `True` parce que `@dataclass` compare les champs un à un, comme le `equals` d'un `record` Java.

## Ce qu'il faut retenir

- On recopie la forme de l'API (`stop_reason`, `content`, blocs `type`/`text`/`id`/`name`/`input`) pour que le faux modèle et le vrai soient interchangeables.
- Jamais de valeur par défaut mutable : `field(default_factory=dict)`.
- Les fabriques et les arguments nommés évitent les erreurs silencieuses de position.

> Suivant : [Étape 3 — Le faux modèle](<03-Faux-modele-FakeLLM.md>)
