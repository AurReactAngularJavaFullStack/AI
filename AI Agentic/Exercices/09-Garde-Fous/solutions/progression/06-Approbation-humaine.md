# Étape 6 — L'approbation humaine

> [Énoncé du palier 09](<../../README.md>) · Précédent : [Étape 5 — Veto et décision](<05-Veto-et-decision.md>) · Suivant : [Étape 7 — La porte protégée](<07-Porte-protegee.md>)

## Comment raisonner

La décision « revue » veut dire : un humain doit dire oui. Dans un programme de test, il n'y a pas d'humain, et l'on ne veut pas attendre deux vraies minutes. On simule donc deux choses : **les réponses** de l'humain, rangées à l'avance dans une file, et **le temps**, porté par l'horloge simulée du palier 01.

La question de conception tient en une phrase : que se passe-t-il quand l'humain ne répond pas ? Un délai qui vaudrait accord transformerait l'absence de l'approbateur en autorisation, et un vendredi après-midi suffirait à faire partir un virement. Le silence vaut donc **refus**. On écrit d'abord ce chemin-là, le plus important, puis le chemin où l'humain répond.

## Un brouillon dangereux

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Approbateur.demander(demande)`** — Ce brouillon de méthode ressemble à un employé qui, trouvant le bureau du chef vide, signe lui-même le bon de sortie en se disant que qui ne dit mot consent. Il reçoit le libellé de la demande, retire la première réponse de la file ou obtient `None` si elle est vide, et dans ce dernier cas rend aussitôt `(True, "pas d'objection")`. Sinon il déballe la décision et son délai, mais n'utilise jamais ce délai, et rend le couple formé de « décision égale à approuvé » et de la décision. L'horloge ne bouge pas, rien n'est journalisé, et une réponse arrivée au bout de dix minutes serait acceptée comme une réponse immédiate.

```python
# [extrait] brouillon
def demander(self, demande):
    reponse = self.reponses.pop(0) if self.reponses else None
    if reponse is None:
        return True, "pas d'objection"          # le silence vaut accord : erreur grave
    decision, delai = reponse
    return decision == "approuvé", decision
```

Deux fautes. Le silence vaut accord : le virement de 180 000 AED du courriel piégé partirait dès que le conseiller est absent (c'est le bug de l'exercice 3 de l'étape 66). Et le temps n'avance jamais : une réponse arrivée au bout de dix minutes serait acceptée, et la sortie de la démo ne pourrait pas afficher le « +120 s » de l'étape 77.

## La classe

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Approbateur.__init__(horloge, journal, delai_s)`** — Le constructeur installe au guichet un conseiller dont le texte est écrit d'avance, avec un sablier posé devant lui. Il reçoit l'horloge simulée et le journal d'audit du monde, ceux-là mêmes qu'utilisent les autres pièces, et un délai de 120 secondes par défaut ; il lève `ValueError` si ce délai est nul ou négatif, range les trois objets dans l'instance et crée la file vide `self.reponses`, que les tests et la démonstration rempliront de couples comme `("approuvé", 45.0)`. Il ne rend rien : il prépare un humain simulé qui partage le temps et la mémoire de son monde, sans aucune variable globale.

**`Approbateur.demander(demande)`** — La méthode raconte l'attente devant ce guichet : on tend la demande, on retourne le sablier, et l'on voit qui de l'humain ou du sable finit le premier. Elle reçoit le libellé de la demande et retire la première réponse de la file, ou `None` si elle est vide ; sans réponse, ou si le délai de la réponse dépasse `delai_s`, elle avance l'horloge des 120 secondes d'attente, journalise « approbation : … -> refus par délai » et rend `(False, "pas de réponse en 120 s : refus par défaut")`. Sinon elle avance l'horloge du délai de l'humain, journalise sa décision et rend `True` seulement si cette décision vaut exactement « approuvé » : avec les réponses à 45 puis 130 secondes, l'horloge finit à 45 + 120 = 165 s.

```python
# [extrait] agent/garde_fous.py
class Approbateur:
    ...
    def __init__(self, horloge: Horloge, journal: JournalAudit, delai_s: float = 120.0) -> None:
        if delai_s <= 0:
            raise ValueError("délai > 0")
        self.horloge, self.journal, self.delai_s = horloge, journal, delai_s
        self.reponses: list = []

    def demander(self, demande: str) -> tuple[bool, str]:
        """Rend (approuvé ?, décision ou motif), et journalise la demande et sa décision."""
        reponse = self.reponses.pop(0) if self.reponses else None
        if reponse is None or reponse[1] > self.delai_s:
            self.horloge.avancer(self.delai_s)
            self.journal.journaliser(f"approbation : {demande} -> refus par délai")
            return False, f"pas de réponse en {self.delai_s:.0f} s : refus par défaut"
        decision, delai = reponse
        self.horloge.avancer(delai)
        self.journal.journaliser(f"approbation : {demande} -> {decision}")
        return decision == "approuvé", decision
```

**Le constructeur.** Un délai nul ou négatif n'a pas de sens : `ValueError`. L'approbateur reçoit **la même** horloge et **le même** journal que le reste du monde, au lieu des globales `HORLOGE` et `JOURNAL` de l'étape 77 : chaque test construit son propre monde, et deux tests ne se marchent pas dessus. `reponses` est une file publique que les tests et la démo remplissent, par exemple `[("approuvé", 45.0)]`.

**`demander`, ligne par ligne.**

- `self.reponses.pop(0) if self.reponses else None` retire la **première** réponse (une file, premier arrivé, premier servi) ou rend `None` si la file est vide. `pop(0)` sur une liste coûte O(n), sans importance pour quelques réponses ; une `collections.deque` et `popleft()` feraient la même chose en O(1).
- La condition de refus réunit deux cas : pas de réponse du tout, ou une réponse arrivée **après** le délai (`reponse[1] > self.delai_s`). Une réponse à 120 s pile est acceptée : le délai est inclusif.
- Sur refus, l'horloge avance de tout le délai, parce que c'est le temps qu'on a réellement attendu ; la décision est journalisée (la demande contient un IBAN, que `journaliser` masque) ; le motif est formaté avec `:.0f`, ce qui écrit « 120 » et non « 120.0 ».
- Sinon, on déballe `(decision, delai)`, l'horloge avance du délai de l'humain, et la méthode rend `True` **seulement** si la décision est exactement « approuvé ». Toute autre réponse (« refusé », « à revoir ») est un refus, avec la décision comme motif.

**Analogie Java.** C'est un `future.get(120, TimeUnit.SECONDS)` dont le `catch (TimeoutException e)` rend un refus, jamais un accord. L'horloge simulée est le `java.time.Clock` que l'on injecte pour rendre testable un code qui dépend du temps.

**Le piège classique.** Avancer l'horloge du délai de l'humain **avant** de comparer ce délai au maximum, ou ne pas l'avancer du tout sur refus. Le test de la file `[("approuvé", 45.0), ("approuvé", 130.0)]` attend une horloge à 45 + 120 = 165 s : la deuxième réponse est trop tardive, et ce sont les 120 s d'attente qui comptent, pas les 130 s de l'humain.

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_09_garde_fous.TestApprobateur
```

`test_pas_de_reponse_vaut_refus` vérifie le refus, l'horloge passée de 0 à 120 s (le « +120 s » de l'étape 77) et la ligne de journal « approbation : virement -> refus par délai ». `test_reponse_dans_le_delai_ou_trop_tardive` vérifie la première demande approuvée en 45 s, la seconde refusée parce que 130 s dépassent 120 s, et l'horloge finale à 165 s.
