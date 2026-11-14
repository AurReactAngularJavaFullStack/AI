# Étape 1 — La tâche et le dossier de crédit

> Palier 08 · Étape 1 sur 7 · Précédent : [Énoncé du palier](<../../README.md>) · Suivant : [Étape 2 — Le graphe et les degrés entrants](<02-Graphe-et-degres-entrants.md>) · Retour à l'énoncé : [README du palier 08](<../../README.md>)

## Comment raisonner

Avant tout algorithme de graphe, il faut savoir ce qu'est un **nœud**. Pour un plan, c'est une tâche, et l'on se pose trois questions :

1. **Qu'est-ce qui l'identifie ?** Son nom. Les prérequis désignent d'autres tâches par leur nom ; il doit donc être non vide et, dans un plan, unique (l'unicité se contrôle au niveau du plan, à l'étape 2).
2. **Qu'est-ce qui la décrit ?** Sa durée, pour le calendrier et le chemin critique ; une durée négative n'a aucun sens.
3. **De quoi dépend-elle ?** De ses prérequis : un ensemble de noms. Une tâche sans prérequis peut partir tout de suite.

Ensuite, une décision de conception : une tâche doit-elle pouvoir changer après sa création ? Non. Le même objet est lu par le tri, les vagues, le calendrier et les tests ; si l'un le modifiait, les autres calculeraient sur un plan différent. On veut donc un **objet valeur immuable** : en Java, un `record` avec un constructeur compact qui valide ; en Python, une `dataclass(frozen=True)` avec un `__post_init__`.

## Les imports

```python
# [extrait] agent/planification.py
import heapq
from dataclasses import dataclass
```

- `heapq` fournit le tas binaire qui servira à Kahn (étape 3) : il rend toujours le plus petit élément en O(log n).
- `dataclass` génère `__init__`, `__repr__` et `__eq__` à partir des champs annotés, comme Lombok ou un `record` Java.
- Le module n'importe rien des paliers précédents : un plan ne manipule que des noms et des durées. C'est l'orchestrateur, plus tard, qui associera chaque nom à un outil.

## Une première version, qui ne se charge même pas

```python
# [extrait] brouillon
@dataclass
class Tache:
    nom: str
    duree: float
    prerequis: list[str] = []
```

Python refuse cette classe dès sa définition, avec `ValueError: mutable default <class 'list'> for field prerequis is not allowed: use default_factory`. La raison est le piège des valeurs par défaut mutables : la liste `[]` serait créée **une seule fois** et partagée par toutes les tâches sans prérequis ; ajouter un prérequis à l'une l'ajouterait à toutes. `dataclass` détecte ce cas pour les listes et les dictionnaires. Et même corrigée avec `field(default_factory=list)`, cette version laisserait passer un nom vide, une durée de −1 et des prérequis modifiables après coup.

## La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Tache.__post_init__()`** — Cette méthode est le contrôleur qui tamponne chaque fiche de travail au moment où elle entre au planning, avant qu'elle ne soit scellée pour de bon : appelée par le constructeur généré de la dataclass gelée, elle ne reçoit que la tâche qui vient d'être construite, lève `ValueError` (« une tâche a un nom non vide ») si le nom est vide, puis `ValueError` (« durée négative pour … ») si la durée est négative, une durée nulle restant permise. Elle range enfin les prérequis en tuple sans doublon, dans l'ordre de leur première apparition, grâce à `dict.fromkeys`, en passant par `object.__setattr__` puisque la classe est gelée ; elle ne renvoie rien, et `("a", "a", "z")` devient `("a", "z")`, ce qui protège plus tard le décompte de Kahn.

```python
# [extrait] agent/planification.py
@dataclass(frozen=True)
class Tache:
    """Une tâche du plan : un nom unique, une durée >= 0 (secondes simulées), des prérequis.

    Exemple : `Tache("calculer_ratio", 0.6, ("calculer_mensualite",))`.
    """
    nom: str
    duree: float
    prerequis: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.nom:
            raise ValueError("une tâche a un nom non vide")
        if self.duree < 0:
            raise ValueError(f"durée négative pour {self.nom}")
        object.__setattr__(self, "prerequis", tuple(dict.fromkeys(self.prerequis)))   # tuple, sans doublon
```

Groupe par groupe :

- **`@dataclass(frozen=True)`** : après `__init__`, toute affectation `t.duree = 3` lève `FrozenInstanceError`. En prime, une tâche gelée est hachable : on pourrait la mettre dans un `set`.
- **`prerequis: tuple[str, ...] = ()`** : le tuple vide est immuable, donc il peut servir de valeur par défaut sans le piège du brouillon. L'annotation `tuple[str, ...]` signifie « un tuple de chaînes, de longueur quelconque ».
- **`__post_init__`** est appelé par le `__init__` généré, juste après l'affectation des champs : c'est l'équivalent du constructeur compact d'un `record` Java, le bon endroit pour valider.
- **`if not self.nom`** refuse la chaîne vide. **`if self.duree < 0`** refuse une durée négative mais accepte 0 : une tâche instantanée (un contrôle de format, par exemple) est légitime, et un test le vérifie.
- **`object.__setattr__(self, "prerequis", …)`** : la classe est gelée, donc `self.prerequis = …` lèverait `FrozenInstanceError`, même dans `__post_init__`. On contourne le gel en appelant directement la méthode de la classe de base `object`. C'est l'idiome officiel des dataclasses gelées ; il n'est à employer que dans `__post_init__`.
- **`tuple(dict.fromkeys(self.prerequis))`** fait deux choses. Il convertit une liste en tuple, pour que `Tache("calculer_ratio", 0.6, ["calculer_mensualite"])` soit aussi immuable que les autres. Et il retire les doublons en gardant l'ordre : les clés d'un dictionnaire sont uniques et gardent leur ordre d'insertion, ce que `set` ne garantit pas. `("a", "a", "z")` devient `("a", "z")`.

**Pourquoi dédoublonner ici.** Un plan produit par un modèle répète parfois une dépendance. Kahn compte les prérequis d'une tâche et retire 1 chaque fois qu'un prérequis sort ; si « a » figurait deux fois, il faudrait compter deux fois partout, sinon la sortie de « a » ferait deux décréments et libérerait la tâche avant ses autres prérequis. Le plus sûr est de régler le problème à la source : une tâche n'a jamais deux fois le même prérequis.

Vérification dans la console, puisque aucun test ne passe encore (ils ont tous besoin d'un algorithme) :

```text
# [extrait] console
>>> from agent.planification import Tache
>>> Tache("calculer_ratio", 0.6, ["calculer_mensualite"])
Tache(nom='calculer_ratio', duree=0.6, prerequis=('calculer_mensualite',))
>>> Tache("v", 1, ("a", "a", "z")).prerequis
('a', 'z')
>>> Tache("a", -1.0)
Traceback (most recent call last):
  ...
ValueError: durée négative pour a
```

- **Piège classique :** écrire `if self.duree <= 0`. Le test `TestTache.test_entrees_invalides` crée `Tache("a", 0)` et attend un chemin critique de durée 0 : la durée nulle doit être acceptée.
- **Piège classique bis :** `("calculer_mensualite")` sans virgule n'est pas un tuple, c'est une chaîne entre parenthèses. `tuple("abc")` vaudrait `('a', 'b', 'c')` : trois prérequis inconnus d'une lettre. Le tuple à un élément s'écrit `("calculer_mensualite",)`.

## Le dossier de crédit

Cette fonction est fournie dans le squelette : ce sont les données de l'énoncé. Elle ne fonctionne qu'une fois `__post_init__` écrit.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`dossier_credit()`** — Cette fonction est le classeur de référence qu'un conseiller sort au début de chaque dossier de crédit à Dubaï : elle ne reçoit rien et renvoie une liste neuve de 8 tâches, avec leurs durées illustratives en secondes simulées, de `verifier_identite` à 1,5 s jusqu'à `rediger_reponse` à 2,5 s, et leurs prérequis, `evaluer_risque` attendant par exemple l'identité, le ratio et les règles. Parce que c'est une fonction et non une constante, chaque appel fabrique des objets neufs, si bien qu'un test ou la démo peuvent ajouter une tâche à leur liste sans toucher aux autres.

```python
# [extrait] agent/planification.py
def dossier_credit() -> list[Tache]:
    """Plan illustratif d'un dossier de crédit à Dubaï : 8 tâches, durées en secondes simulées."""
    return [
        Tache("verifier_identite", 1.5),                     # format de l'Emirates ID, liste de sanctions
        Tache("lire_memoire", 0.5),                          # salaire et crédits en cours (palier 06)
        Tache("rechercher_regles", 2.0),                     # RAG hybride sur les règles CBUAE (palier 07)
        Tache("calculer_mensualite", 0.8, ("lire_memoire",)),
        Tache("calculer_ratio", 0.6, ("calculer_mensualite",)),
        Tache("convertir_usd", 0.4, ("calculer_mensualite",)),
        Tache("evaluer_risque", 1.2, ("verifier_identite", "calculer_ratio", "rechercher_regles")),
        Tache("rediger_reponse", 2.5, ("evaluer_risque", "convertir_usd")),
    ]
```

- C'est une **fonction** et non une constante : chaque appel rend des objets neufs, et un test qui modifierait sa liste (en ajoutant une tâche, comme la démo) ne toucherait pas les autres.
- Trois tâches n'ont pas de prérequis : elles pourront partir ensemble. `calculer_mensualite` a besoin du salaire et des crédits en cours, donc de la mémoire. `evaluer_risque` rassemble trois branches : l'identité, le ratio et les règles. `rediger_reponse` attend le risque et la conversion en USD.
- L'ordre des tâches dans la liste n'a **aucune** importance : `rediger_reponse` pourrait être écrite en premier. C'est le tri topologique qui décidera de l'ordre d'exécution.
- Les durées sont illustratives : elles donnent un ordre de grandeur (une recherche hybride est plus lente qu'un calcul de mensualité, la rédaction par le modèle est la plus lente), pas une mesure.

**Test à cette étape :** aucun test du palier ne passe encore, mais tous échouent maintenant plus loin, dans `tri_topologique` ou `chemin_critique`, et non plus à la création des tâches. Lance `python -m unittest -v tests.test_08_planification` pour le constater : les erreurs `NotImplementedError` viennent désormais des fonctions de l'étape 2 et des suivantes.
