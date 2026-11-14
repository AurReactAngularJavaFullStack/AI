# Étape 2 — Le seau à jetons

> Palier 11 · Étape 2 sur 7 · Précédent : [Étape 1 — Les prix et le coût d'une tâche](<01-Prix-et-cout-d-une-tache.md>) · Suivant : [Étape 3 — L'attente exponentielle et la gigue](<03-Attente-exponentielle-et-gigue.md>) · Énoncé : [README du palier 11](<../../README.md>)

## Comment raisonner depuis la feuille blanche

La première question est : **quel état faut-il garder ?** On pourrait imaginer un minuteur qui ajoute r jetons au seau chaque seconde. C'est inutile, et c'est même dangereux (un fil d'exécution de plus, du temps réel, des tests lents). Il suffit de connaître deux nombres : combien de jetons il y avait à la dernière mise à jour, et à quel instant. Au moment d'une demande, on calcule ce que la recharge a ajouté depuis, en une multiplication. On appelle cela une recharge paresseuse : c'est exactement ce que font le `RateLimiter` de Guava et celui de Resilience4j en Java.

La deuxième question est : **dans quel ordre ?** Toujours recharger d'abord, décider ensuite. Si l'on décidait avant de recharger, une demande arrivée après 40 secondes d'inactivité serait refusée sur la foi d'un compte périmé.

Le test `TestSeauAJetons.test_sequence_de_l_etape_66` donne la séquence à reproduire : trois demandes de 3 000 tokens acceptées à t = 0, la quatrième refusée, puis une acceptée et une refusée à t = 40 s. Il lit aussi l'attribut `seau.jetons` : les noms d'attributs font partie du contrat.

On écrit donc le constructeur (l'état), puis `consommer` (la recharge, puis la décision).

## Une première version, avec deux erreurs

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`SeauAJetons.__init__(capacite, recharge_par_s, horloge)`** — Ce constructeur de brouillon installe la citerne sans vérifier qu'elle a un fond ni un robinet dans le bon sens. Il reçoit la capacité, la recharge par seconde et l'horloge simulée, range les trois dans l'instance, remplit le seau avec `capacite` jetons et note l'instant courant dans `dernier`. Il ne lève jamais d'exception, si bien qu'une capacité nulle ou une recharge négative passeraient inaperçues ; pour le reste, son état de départ est celui qu'attend le test, un seau plein de 10 000 jetons à l'instant 0.

**`SeauAJetons.consommer(cout)`** — Cette méthode de brouillon est un porteur d'eau qui verse sans mesure et qui puise même quand la citerne est trop basse. Elle reçoit le coût de la demande, ajoute la recharge du temps écoulé sans aucun plafond, remet `dernier` à l'heure, retire le coût dans tous les cas et rend `True` si le solde reste positif ou nul. Après 1 000 secondes d'inactivité, le seau monterait à 51 000 jetons au lieu de 10 000 ; et la quatrième demande refusée fait tomber le solde à −2 000, si bien qu'à 40 s le seau ne contient que 0 jeton et que la cinquième demande, qui devait passer, est refusée.

```python
# [extrait] brouillon
class SeauAJetons:
    def __init__(self, capacite, recharge_par_s, horloge):
        self.capacite, self.recharge, self.horloge = capacite, recharge_par_s, horloge
        self.jetons = capacite
        self.dernier = horloge.t

    def consommer(self, cout):
        self.jetons += self.recharge * (self.horloge.t - self.dernier)   # sans plafond
        self.dernier = self.horloge.t
        self.jetons -= cout                                              # retire même en cas de refus
        return self.jetons >= 0
```

Ce brouillon passe les trois premières demandes du test, puis se trompe deux fois. **Il oublie le plafond** : après 1 000 secondes d'inactivité, le seau contiendrait 1 000 + 50 × 1 000 = 51 000 jetons, et laisserait partir dix-sept appels de 3 000 tokens d'un coup. La borne C + r T est violée, et le seau ne protège plus rien. Le test `test_recharge_plafonnee`, qui attend 10 000 jetons après une longue pause, échoue. **Il retire le coût même quand il refuse** : la quatrième demande fait tomber le seau à −2 000, si bien qu'à t = 40 s il ne contient que −2 000 + 2 000 = 0 jeton, et la cinquième demande, qui devait passer, est refusée. Une demande refusée ne doit rien coûter.

## Le constructeur

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`SeauAJetons.__init__(capacite, recharge_par_s, horloge)`** — Le constructeur définitif est l'installateur qui contrôle la cuve avant de la remplir : il refuse de poser un seau sans fond ou un robinet qui aspirerait l'eau. Il reçoit la capacité C, la recharge r par seconde et l'horloge partagée, lève `ValueError("capacité > 0 et recharge >= 0")` si la capacité est nulle ou négative ou si la recharge est négative, puis range `capacite`, `recharge` et la référence à l'horloge. Il démarre le seau plein avec `float(capacite)` jetons, en flottant parce que la recharge produira des fractions, note dans `dernier` l'instant de création et ne rend rien ; une recharge nulle reste permise, pour un quota qui ne se renouvelle pas.

```python
# [extrait] agent/production.py
class SeauAJetons:
    """Seau à jetons (étape 66) : capacité C, recharge r jetons par seconde (horloge simulée).

    Une demande de coût c passe si le seau contient au moins c jetons ; sinon elle est refusée et le
    seau ne change pas. Sur toute fenêtre de durée T, il ne passe jamais plus de C + r·T jetons.
    Exemple : C = 10 000, r = 50/s, demandes de 3 000 à t = 0 : 7 000, 4 000, 1 000 restants, la 4e
    est refusée ; à t = 40 s, le seau a regagné 2 000 jetons (3 000 au total) et la demande passe.
    """

    def __init__(self, capacite: float, recharge_par_s: float, horloge: Horloge) -> None:
        if capacite <= 0 or recharge_par_s < 0:
            raise ValueError("capacité > 0 et recharge >= 0")
        self.capacite = capacite
        self.recharge = recharge_par_s
        self.horloge = horloge
        self.jetons = float(capacite)
        self.dernier = horloge.t
```

**La docstring de la classe** énonce le contrat et la borne C + r T démontrée à l'étape 66 : c'est elle qui justifie le plafond que le brouillon avait oublié.

**La garde** refuse une capacité nulle ou négative (un seau qui ne laisserait jamais rien passer est une erreur de configuration) et une recharge négative. Une recharge nulle reste permise : c'est un quota fixe, qui ne se renouvelle pas, par exemple 100 000 tokens pour toute une campagne de tests.

**Les trois attributs de configuration.** `capacite` et `recharge` sont des nombres. `horloge` est une **référence** vers l'objet `Horloge` partagé : quand le test appelle `h.avancer(40)`, le seau voit le nouvel instant sans qu'on le prévienne, parce qu'il lit `self.horloge.t` au moment de chaque demande. C'est l'injection de dépendance que tu connais en Spring : le seau reçoit son horloge, il ne la fabrique pas, et un test peut lui en donner une qu'il contrôle, comme on injecte un `java.time.Clock` fixe dans un service.

**L'état.** Le seau démarre **plein** : `float(capacite)` jetons. On convertit en flottant parce que la recharge (50 × 0,5 s, par exemple) produira des fractions de jeton ; le test `assertEqual(seau.jetons, 1_000)` reste vrai, puisque 1000.0 == 1000 en Python. `dernier` retient l'instant de la dernière mise à jour, ici la création du seau.

## La méthode consommer

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`SeauAJetons.consommer(cout)`** — La méthode définitive est le gardien de la citerne qui, à chaque visiteur, regarde d'abord la jauge, ajoute ce que le robinet a versé depuis le dernier passage sans laisser déborder, et ne sert que si la réserve suffit. Elle reçoit le coût de la demande, lève `ValueError` s'il est négatif, met les jetons à min(capacité, jetons + recharge × temps écoulé), remet `dernier` à l'heure que la demande passe ou non, puis, si le coût tient dans le seau, égalité comprise, le retire et rend `True`. Sinon elle rend `False` sans rien toucher : la séquence de l'étape 66 donne trois acceptations, un refus avec 1 000 jetons restants, puis, à t = 40 s, une acceptation qui vide le seau et un dernier refus.

```python
# [extrait] agent/production.py
class SeauAJetons:
    ...
    def consommer(self, cout: float) -> bool:
        """Recharge pour le temps écoulé (sans dépasser C), puis accepte la demande si cout <= jetons."""
        if cout < 0:
            raise ValueError("coût >= 0")
        self.jetons = min(self.capacite, self.jetons + self.recharge * (self.horloge.t - self.dernier))
        self.dernier = self.horloge.t
        if cout <= self.jetons:
            self.jetons -= cout
            return True
        return False
```

**La garde** refuse un coût négatif : sans elle, `consommer(-5_000)` **ajouterait** des jetons, et n'importe quel appelant pourrait remplir le seau à volonté. Un coût nul est permis ; il sert à forcer une recharge sans rien consommer, ce que fait `test_recharge_plafonnee`.

**La recharge plafonnée**, en une ligne : le temps écoulé `self.horloge.t - self.dernier`, multiplié par la recharge, ajouté aux jetons, puis `min(self.capacite, …)`. C'est la formule j ← min(C, j + r (t − t_d)) du README, recopiée telle quelle.

**La mise à jour de `dernier`** vient juste après, **avant** la décision, et elle a lieu que la demande soit acceptée ou refusée. Le piège classique est de ne mettre `dernier` à jour qu'en cas d'acceptation : la demande suivante rechargerait alors une deuxième fois le même intervalle de temps, et le seau fabriquerait des jetons qui n'existent pas.

**La décision.** Si le coût tient dans le seau (`cout <= self.jetons`, l'égalité comprise : une demande qui vide exactement le seau passe), on retire le coût et l'on rend `True`. Sinon, on rend `False` et l'on ne touche à rien. Le seau ne lève pas d'exception sur un refus : un refus est un résultat normal, que l'appelant traduit comme il veut, par exemple en `ErreurTransitoire("429")` à l'étape 4, ou en message d'attente pour le client.

On retrouve la table du README dans la console :

```text
# [extrait] console
>>> from agent.modele import Horloge
>>> from agent.production import SeauAJetons
>>> h = Horloge()
>>> seau = SeauAJetons(10_000, 50, h)
>>> [seau.consommer(3_000) for _ in range(4)], seau.jetons
([True, True, True, False], 1000.0)
>>> h.avancer(40)
>>> seau.consommer(3_000), seau.jetons, seau.consommer(3_000)
(True, 0.0, False)
```

Sur [0 ; 40], quatre demandes de 3 000 tokens sont passées : 12 000 = C + r T. La borne est atteinte, et elle ne peut pas l'être davantage.

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_11_production.TestSeauAJetons
```

Les trois tests passent : la séquence de l'étape 66, la recharge plafonnée (10 000 jetons après 1 000 s, puis `consommer(10_001)` refusé) et les entrées invalides (capacité 0, coût −1).
