# Étape 1 — L'horloge simulée

> Palier 01, étape 1 sur 7 · Précédent : aucun · Suivant : [Étape 2 — Blocs et réponses](<02-Blocs-et-reponses.md>) · [Retour à l'énoncé](<../../README.md>)

**Objectif de l'étape :** écrire l'en-tête du module `agent/modele.py`, la constante `SECONDES_PAR_JOUR` et la classe `Horloge`, puis faire passer les trois tests de `TestHorloge`.

## Comment raisonner

Devant le fichier vide, la première question n'est pas « comment appeler le modèle ? » mais « de quoi tout le reste dépendra-t-il ? ». Deux choses traversent tout l'agent : la forme des messages échangés avec le modèle, et le temps. Le temps vient en premier parce que c'est la pièce la plus simple et qu'elle fixe une règle pour tout le paquet : **aucun composant ne lit l'heure réelle**.

Pourquoi cette règle ? Plus tard, l'approbateur humain du palier 09 attendra 120 secondes avant de refuser un virement, le seau à jetons du palier 11 se remplira au fil des secondes, et la mémoire du palier 06 calculera l'âge d'un souvenir en jours. Si chacun appelait `time.time()`, un test qui vérifie « refus après 120 s » devrait vraiment attendre deux minutes, et deux exécutions de la démo n'afficheraient pas la même chose. Le temps devient donc une **donnée** : un objet qu'on crée, qu'on fait avancer à la main et qu'on passe en paramètre.

On écrit d'abord le test dans sa tête, puis le code qui le fait passer. Le test le plus simple est : « une horloge réglée sur 90 jours en secondes doit dire jour 90 ». Il impose déjà trois choses : un constructeur qui reçoit un nombre de secondes, un attribut qui le garde, une méthode qui convertit en jours.

## Le piège à éviter d'abord

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Horloge.maintenant()`** — Dans ce brouillon, la méthode se comporte comme un employé qui, chaque fois qu'on lui demande l'heure, lève les yeux vers la pendule murale du bureau : elle ne reçoit rien, interroge `time.time()` et renvoie le nombre de secondes écoulées depuis le 1er janvier 1970 au moment précis de l'appel. C'est exactement ce qu'il faut éviter : la valeur change à chaque exécution, on ne peut ni se placer au jour 90 de la relation avec le client, ni simuler une attente de 120 secondes sans attendre vraiment, et la sortie de la démo cesse d'être reproductible.

```python
# [extrait] brouillon
import time


class Horloge:
    def maintenant(self) -> float:
        return time.time()          # l'heure réelle : change à chaque exécution
```

Ce brouillon est ce que l'on écrit par réflexe, et il casse tout ce qui suit.

- `time.time()` rend le nombre de secondes depuis le 1er janvier 1970 au moment de l'appel : la valeur change à chaque exécution, donc la sortie de la démo aussi.
- Impossible de se placer au « jour 90 de la relation avec le client », comme le fait l'étape 77, sans tricher avec l'horloge du système.
- Impossible d'attendre 120 secondes en test sans attendre réellement 120 secondes.

En Java, c'est la différence entre appeler `System.currentTimeMillis()` partout et injecter un `java.time.Clock` dans chaque service : en test, on passe `Clock.fixed(...)` ou `Clock.offset(...)`, et le temps devient prévisible. Notre `Horloge` joue le rôle de ce `Clock`.

## L'en-tête du module

```python
# [extrait] agent/modele.py
import math
from dataclasses import dataclass, field

SECONDES_PAR_JOUR = 86_400
```

**Les imports.** On les écrit tous en haut, même ceux qui ne servent qu'aux étapes suivantes : `math` pour l'exponentielle de la softmax (étape 4) et le produit de la fiabilité (étape 5), `dataclass` et `field` pour les classes de données de l'étape 2. Python ne refuse pas un import inutilisé, mais l'habitude de tout déclarer en tête rend le module lisible d'un coup d'œil, comme les `import` d'une classe Java.

**La constante.** `SECONDES_PAR_JOUR = 86_400` nomme le nombre au lieu de l'écrire en dur dans `jour()`. Le tiret bas est un séparateur de milliers, ignoré par l'interpréteur : `86_400 == 86400`. Java l'accepte aussi depuis Java 7 (`86_400`). La majuscule est une convention, pas une protection : Python n'a pas de `static final`, rien n'empêche techniquement de réaffecter la constante, et c'est la majuscule qui dit au lecteur de ne pas le faire.

**Le piège classique, côté Java.** En Java, `7_776_000 / 86_400` entre deux `int` donne une division entière. En Python 3, l'opérateur `/` rend **toujours** un `float` : `7_776_000 / 86_400` vaut `90.0`. La division entière s'écrit `//`. Ici, on veut bien un `float`, car un souvenir peut avoir 2,5 jours.

Aucun test ne passe encore : il faut la classe.

## Le constructeur

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Horloge.__init__(t)`** — Le constructeur règle le sablier au moment où l'on crée l'horloge, comme un régisseur qui inscrit l'heure de départ en tête de sa feuille de service : il reçoit un instant t en secondes, 0,0 par défaut, vérifie d'abord qu'il n'est pas négatif et lève sinon `ValueError` avec le message « l'horloge démarre à t >= 0 », puis range `float(t)` dans l'attribut public `t`. La conversion garantit que `Horloge(10)` et `Horloge(10.0)` portent toutes deux 10,0, et cet objet, passé en paramètre plutôt que lu dans une variable globale, est le temps que liront plus tard l'approbateur du palier 09, le seau à jetons du palier 11 et la mémoire du palier 06.

```python
# [extrait] agent/modele.py
class Horloge:
    ...
    def __init__(self, t: float = 0.0) -> None:
        if t < 0:
            raise ValueError("l'horloge démarre à t >= 0")
        self.t = float(t)                       # secondes simulées
```

La ligne `...` remplace la docstring de la classe, que tu as déjà dans le squelette.

**`def __init__(self, t: float = 0.0) -> None:`** C'est le constructeur. `self` est l'équivalent explicite de `this` en Java : Python l'écrit en premier paramètre de chaque méthode, et l'appelant ne le passe pas (`Horloge(10.0)` appelle `__init__(nouvel_objet, 10.0)`). La valeur par défaut `0.0` permet d'écrire `Horloge()`. Les annotations `float` et `-> None` ne sont pas vérifiées à l'exécution : ce sont des indications pour le lecteur et pour l'éditeur, pas des types Java.

**`if t < 0: raise ValueError(...)`** On refuse un instant de départ négatif. `ValueError` est l'équivalent de `IllegalArgumentException` : l'argument a le bon type mais une valeur interdite. Le message dit ce qui est attendu, pas seulement ce qui ne va pas. C'est la convention de tout le paquet : une entrée invalide lève `ValueError` avec un message clair.

**`self.t = float(t)`** En Python, un attribut n'est pas déclaré dans le corps de la classe comme un champ Java : il naît la première fois qu'on l'affecte, ici dans le constructeur. On convertit en `float` pour que l'attribut ait toujours le même type : `Horloge(10)` et `Horloge(10.0)` donnent toutes deux `t == 10.0`. L'attribut est public (pas de tiret bas devant) parce que les tests et les autres modules le lisent directement : `h.t`.

**Le piège classique.** Oublier `self.` et écrire `t = float(t)` : cela crée une variable locale qui disparaît à la fin du constructeur, et l'objet n'a aucun attribut `t`. L'erreur n'apparaît qu'à la première lecture, sous la forme `AttributeError: 'Horloge' object has no attribute 't'`.

Aucun test ne passe encore : les trois tests de `TestHorloge` appellent aussi `jour()` ou `avancer()`.

## Avancer et lire en jours

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Horloge.avancer(secondes)`** — Cette méthode est le geste du régisseur qui pousse l'aiguille d'un nombre de secondes décidé par le programme : elle reçoit une durée, contrôle d'abord qu'elle n'est pas négative, lève sinon `ValueError` (« une horloge ne recule pas ») avant d'avoir touché à quoi que ce soit, et seulement ensuite ajoute la durée à `t`. Elle ne renvoie rien ; partant de 0, deux appels avec 45 puis 75 secondes laissent l'horloge à 120,0, et une horloge à 10,0 qui refuse d'avancer de −1 reste à 10,0, exactement ce que vérifie `test_le_temps_ne_recule_pas`.

**`Horloge.jour()`** — Celle-ci lit le compteur sans jamais le modifier, comme un greffier qui reporte une durée en secondes dans le calendrier du dossier : elle ne reçoit rien, divise `t` par la constante `SECONDES_PAR_JOUR`, soit 86 400, et renvoie un `float`, puisqu'en Python 3 l'opérateur `/` ne fait jamais de division entière. Avec t égal à 7 776 000 secondes, elle renvoie 90,0, le jour de la relation avec le client que fixe l'étape 77, et un souvenir pourra plus tard avoir un âge de 2,5 jours sans être arrondi.

```python
# [extrait] agent/modele.py
class Horloge:
    ...
    def avancer(self, secondes: float) -> None:
        """Avance de `secondes` (>= 0) ; le temps ne recule jamais.

        Exemple : t = 0.0, `avancer(45)` puis `avancer(75)` donnent t = 120.0.
        """
        if secondes < 0:
            raise ValueError("une horloge ne recule pas : secondes >= 0")
        self.t += secondes

    def jour(self) -> float:
        """Le temps en jours : t / 86 400. Exemple : t = 7 776 000 s donne le jour 90.0."""
        return self.t / SECONDES_PAR_JOUR
```

**`avancer`.** Deux lignes de logique, dans un ordre qui compte : on **vérifie d'abord**, on **modifie ensuite**. Si l'on écrivait `self.t += secondes` puis le test, un appel `avancer(-1)` lèverait bien `ValueError`, mais l'horloge aurait déjà reculé d'une seconde. Le test `test_le_temps_ne_recule_pas` le vérifie : après l'échec de `avancer(-1)`, `h.t` doit valoir encore `10.0`. C'est la règle du « fail fast » que tu appliques déjà en Java avant de toucher à l'état d'un objet : un appel refusé ne laisse aucune trace.

**`self.t += secondes`** ajoute la durée. Un `int` ajouté à un `float` donne un `float`, donc `t` garde son type.

**`jour`.** Une division par la constante. Avec t = 7 776 000, le résultat vaut 7 776 000 / 86 400 = 90,0. La méthode ne modifie rien : c'est un accesseur calculé, comme un `getJour()` sans champ associé.

**Pourquoi pas de variable globale.** L'étape 77 crée une horloge globale, `HORLOGE = Horloge(90 * 86_400.0)`, que tous les composants lisent. Ici, il n'y en a pas : le palier 09 écrira `Approbateur(horloge, ...)` et le palier 11 `SeauAJetons(..., horloge)`. Chaque test crée sa propre horloge, si bien que deux tests ne peuvent pas se perturber en faisant avancer le même objet. C'est l'injection de dépendances que Spring fait pour toi, faite ici à la main.

**Le test qui passe maintenant.** Depuis `projet/` :

```powershell
python -m unittest -v tests.test_01_modele.TestHorloge
```

Les trois tests sont verts : `test_jour_90` (7 776 000 s donnent le jour 90,0), `test_avancer_cumule` (45 puis 75 secondes donnent 120,0) et `test_le_temps_ne_recule_pas` (un temps négatif est refusé au constructeur comme dans `avancer`, et l'horloge reste à 10,0). Pour n'en lancer qu'un : `python -m unittest -v tests.test_01_modele.TestHorloge.test_le_temps_ne_recule_pas`.

## Ce qu'il faut retenir

- Le temps est une donnée que l'on passe en paramètre, jamais une lecture de l'horloge du système : c'est ce qui rend l'agent testable et sa sortie reproductible.
- On valide avant de modifier : un appel refusé laisse l'objet intact.
- En Python 3, `/` rend toujours un `float`.

> Suivant : [Étape 2 — Blocs et réponses](<02-Blocs-et-reponses.md>)
