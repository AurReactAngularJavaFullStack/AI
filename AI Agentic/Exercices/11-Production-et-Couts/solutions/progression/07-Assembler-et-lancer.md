# Étape 7 — Assembler, lancer et retenir

> Palier 11 · Étape 7 sur 7 · Précédent : [Étape 6 — Le budget et les tâches possibles](<06-Budget-et-taches-possibles.md>) · Énoncé : [README du palier 11](<../../README.md>) · Palier suivant : [Palier 12 — Assemblage de l'agent complet](<../../../12-Assemblage-Agent-Complet/README.md>)

## Comment raisonner : relire le module d'un seul coup d'œil

Le module est complet. Avant de lancer les tests, relis sa structure de haut en bas : chaque pièce n'utilise que ce qui est écrit au-dessus d'elle, et l'on peut le réécrire de tête dans cet ordre.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cout_tache(tokens_entree, tokens_sortie, cache_lus, cache_ecrits, prix_entree, prix_sortie)`** — Première pièce du module, c'est le caissier de l'étape 1, qui facture chaque sorte de token à son tarif. Elle reçoit les tokens d'entrée hors cache, de sortie, lus et écrits dans le cache, ainsi que les deux prix en USD par million ; elle lève `ValueError` pour un nombre ou un prix négatif, applique 0,1 fois le prix d'entrée aux tokens relus et 1,25 fois aux tokens écrits, divise une seule fois par un million et rend `{"usd": …, "aed": …}`. Dans la démonstration, elle donne 0,0570 USD sans cache et 0,0384 USD, soit 0,141024 AED, avec le préfixe mis en cache.

**`SeauAJetons.__init__(capacite, recharge_par_s, horloge)`** — Le constructeur de l'étape 2 installe la citerne, pleine, sous son robinet à débit constant. Il reçoit la capacité, la recharge par seconde et l'horloge simulée partagée, lève `ValueError` si la capacité est nulle ou négative ou si la recharge est négative, range les trois paramètres, met `jetons` à la capacité convertie en flottant et note l'instant courant dans `dernier`. Il ne rend rien ; ces deux nombres, les jetons et l'instant de la dernière mise à jour, sont tout l'état dont le seau aura besoin pour régler le débit des appels.

**`SeauAJetons.consommer(cout)`** — La méthode de l'étape 2 est le gardien qui recharge d'abord, puis décide. Elle reçoit le coût d'une demande, lève `ValueError` s'il est négatif, ajoute aux jetons la recharge du temps écoulé sans dépasser la capacité, met `dernier` à l'heure, puis retire le coût et rend `True` s'il tient dans le seau, ou rend `False` sans rien retirer. Au point 3 de la démonstration, un seau de 10 000 jetons rechargé à 50 par seconde répond `[True, True, True, False, True, False]` à six appels de 3 000, les deux derniers à t = 40 s.

**`attente_backoff(tentative, base_s, plafond_s, gigue, rng)`** — Cette fonction de l'étape 3 est le sablier qui double à chaque essai, plafonné, et que la gigue peut seulement raccourcir. Elle reçoit le numéro de relance, la base, le plafond, la gigue et un générateur facultatif, lève `ValueError` pour une tentative inférieure à 1, une base nulle, un plafond sous la base ou une gigue hors de [0 ; 1], et rend min(plafond, base × 2ᵏ⁻¹), multiplié par 1 − gigue × u si un générateur est fourni et la gigue positive. Avec une gigue de 0,2 et la graine 11, les trois premières attentes de la démonstration valent 0,910, 1,776 et 3,261 s, chacune sous sa valeur nominale.

**`executer_avec_relances(fonction, max_tentatives, base_s, plafond_s, gigue, graine, horloge)`** — Cette fonction de l'étape 4 est le standardiste qui ne rappelle que les lignes occupées et tient registre de tout. Elle reçoit l'appelable, le nombre maximal de tentatives, les paramètres du backoff, une graine et une horloge facultative ; elle crée un seul générateur local, appelle la fonction, rend un dictionnaire « succes » dès qu'elle réussit, note chaque `ErreurTransitoire` et, s'il reste une tentative, l'attente correspondante qu'elle ajoute à l'horloge, et laisse remonter toute autre exception. Au point 4, trois surcharges puis un succès donnent 4 tentatives et une horloge avancée de 5,946 s ; une panne longue sur trois tentatives donne « echec » et les attentes [1.0, 2.0].

**`percentile(valeurs, p)`** — Cette fonction de l'étape 5 est le juge d'arrivée qui désigne le coureur d'un rang donné sur une copie du classement. Elle reçoit une liste de mesures et un ordre p dans ]0, 100], lève `ValueError` pour une liste vide ou un p hors bornes, trie une copie, calcule le rang ⌈p × n / 100⌉ en multipliant avant de diviser, et rend la valeur d'indice rang − 1, toujours une valeur observée. Sur les 20 latences de la démonstration, la médiane, au rang 10, vaut 1,4 s.

**`p95(valeurs)`** — Cette fonction de l'étape 5 est le cadran unique du contrat de service, celui qu'une requête sur vingt dépasse. Elle reçoit la liste des latences et rend `percentile(valeurs, 95)`, avec les mêmes erreurs pour une liste vide. Au point 5 de la démonstration, le rang 19 des 20 latences donne 3,4 s, alors que la moyenne de 1,775 s ferait croire que tout va bien et que le maximum isolé de 6,0 s, au rang 20, est volontairement ignoré.

**`budget_restant(budget_aed, depenses_aed)`** — Cette fonction de l'étape 6 tient le carnet d'un trésorier qui n'efface jamais le rouge. Elle reçoit le budget et la liste des dépenses en AED, lève `ValueError` si l'un d'eux est négatif, et rend le budget moins la somme des dépenses, négatif en cas de dépassement. Au point 2 de la démonstration, un budget journalier de 50 AED dont 39,75 AED sont déjà dépensés laisse 10,25 AED, que la fonction suivante convertit en nombre de tâches.

**`taches_possibles(reste_aed, cout_tache_aed)`** — Dernière pièce du module, c'est le trésorier qui ne promet que ce qu'il peut payer en entier. Elle reçoit le reste en AED et le coût d'une tâche, lève `ValueError` si ce coût est nul ou négatif, et rend le plus grand de 0 et de la partie entière inférieure du quotient. Au point 2, 10,25 AED à 0,141024 AED la tâche donnent 72 tâches et non 73, car la 73e ne serait pas financée ; un reste négatif donne 0.

```python
# [extrait] agent/production.py
def cout_tache(tokens_entree: int, tokens_sortie: int, cache_lus: int = 0, cache_ecrits: int = 0,
               prix_entree: float = PRIX_ENTREE_USD_MTOK, prix_sortie: float = PRIX_SORTIE_USD_MTOK) -> dict:
    ...
class SeauAJetons:
    ...
    def __init__(self, capacite: float, recharge_par_s: float, horloge: Horloge) -> None:
        ...
    def consommer(self, cout: float) -> bool:
        ...
def attente_backoff(tentative: int, base_s: float = 1.0, plafond_s: float = 30.0, gigue: float = 0.0,
                    rng: random.Random | None = None) -> float:
    ...
class ErreurTransitoire(Exception):
    ...
def executer_avec_relances(fonction, max_tentatives: int = 4, base_s: float = 1.0, plafond_s: float = 30.0,
                           gigue: float = 0.1, graine: int = 0, horloge: Horloge | None = None) -> dict:
    ...
def percentile(valeurs: list[float], p: float) -> float:
    ...
def p95(valeurs: list[float]) -> float:
    ...
def budget_restant(budget_aed: float, depenses_aed: list[float]) -> float:
    ...
def taches_possibles(reste_aed: float, cout_tache_aed: float) -> int:
    ...
```

Les lignes `...` remplacent les corps et les docstrings que les étapes 1 à 6 ont expliqués. On lit trois familles. **Le coût** : les quatre constantes illustratives (étape 1), `cout_tache`, puis `budget_restant` et `taches_possibles`, qui le comparent à un budget. **Le débit et les pannes** : `SeauAJetons`, qui dit si un appel peut partir maintenant, et le trio `attente_backoff`, `ErreurTransitoire`, `executer_avec_relances`, qui survit aux surcharges passagères. **La latence** : `percentile` et `p95`, qui résument une liste de mesures par la valeur que le contrat de service surveille. Aucune de ces fonctions n'appelle le modèle : elles se branchent autour de n'importe quel appel, celui du faux modèle comme celui de Claude.

Deux principes traversent tout le module, et ce sont eux qu'il faut retenir pour la feuille blanche. **Rien de réel** : pas de `time.sleep`, pas de `time.time()`, pas de `random.random()` global ; le temps est une `Horloge` injectée, le hasard un `random.Random(graine)` injecté ou créé localement. **Rien de caché** : un refus du seau ne coûte rien, un dépassement de budget reste négatif, un échec après relances rend toute son histoire, une liste vide lève une erreur au lieu de rendre 0.

## Lancer tous les tests

Depuis `projet/` (ou depuis `solutions/` pour voir la solution passer) :

```text
python -m unittest
```

La dernière ligne doit être `OK`, après `Ran 150 tests` : les 136 tests des paliers 01 à 10, que tu n'as pas touchés, et les 14 tests du palier 11. Si un test d'un palier antérieur échoue, c'est qu'un fichier autre que `agent/production.py` a été modifié : le principe de la série est de composer, jamais de réécrire un module déjà fait.

## Lancer la démo

```text
python demo.py
```

```text
Palier 11 — l'agent de la banque B-1 en production (prix illustratifs : 3 et 15 USD par million)
1. Une tâche, 14 000 tokens d'entrée sans cache : 0.0570 USD = 0.209333 AED
   avec 4 000 écrits et 8 000 relus dans le cache : 0.0384 USD = 0.141024 AED
2. Budget journalier 50 AED, déjà dépensé 39,75 AED : reste 10.25 AED, soit 72 tâches
3. Seau de 10 000 tokens, recharge 50/s, appels de 3 000 : [True, True, True, False, True, False] (deux derniers à t = 40 s)
4. Trois surcharges puis succès : succes en 4 tentatives ; attentes 0.910, 1.776, 3.261 s ; horloge +5.946 s
   panne longue : echec après 3 tentatives, attentes [1.0, 2.0]
5. 20 latences (s) : médiane 1.4, p95 3.4, max 6.0
OK — palier 11 terminé.
```

Chaque point numéroté se recalcule à la main, et c'est le meilleur exercice de révision du palier.

- **Point 1.** Sans cache : (14 000 × 3 + 1 000 × 15) / 10⁶ = 0,057 USD, soit 0,2093325 AED, affiché avec six décimales. Avec cache : 0,0384 USD, soit 0,141024 AED. Les mêmes 14 000 tokens d'entrée, un tiers moins cher : le cache change le prix, pas le nombre de tokens.
- **Point 2.** 50 − 39,75 = 10,25 AED, et ⌊10,25 / 0,141024⌋ = 72 tâches au coût avec cache.
- **Point 3.** La table de l'étape 2 : trois acceptées, une refusée, puis à t = 40 s une acceptée (le seau a regagné 2 000 jetons) et une refusée. Six demandes, quatre passées, 12 000 tokens = C + r T.
- **Point 4.** La fonction échoue trois fois puis réussit : quatre tentatives, donc trois attentes. Avec une gigue de 0,2 et la graine 11, les trois tirages valent environ 0,4524, 0,5598 et 0,9242 ; les attentes valent 1 × (1 − 0,2 × 0,4524) = 0,910 s, 2 × (1 − 0,2 × 0,5598) = 1,776 s et 4 × (1 − 0,2 × 0,9242) = 3,261 s, et l'horloge a avancé de leur somme, 5,946 s. Chaque attente est sous sa valeur nominale (1, 2, 4), jamais au-dessus.
- **Point 4, la panne longue.** Trois tentatives, toutes ratées, sans gigue : deux attentes seulement, 1 s et 2 s, et le statut « echec ». Pas d'attente après le dernier échec.
- **Point 5.** Les 20 latences triées ont une médiane de rang 10, 1,4 s, et un p95 de rang 19, 3,4 s. Le maximum, 6,0 s, est la 20e : le p95 l'ignore, c'est voulu, une valeur isolée ne doit pas déclencher d'alerte. La moyenne, 1,775 s, cacherait la queue de 3,4 s.

## Ce que tu sais maintenant faire depuis une feuille blanche

- Chiffrer une tâche d'agent en USD et en AED, avec des prix illustratifs paramétrables, et montrer par le calcul que le cache du préfixe est rentable dès la première relecture.
- Coder un seau à jetons à recharge paresseuse sur une horloge simulée, et démontrer qu'il ne laisse jamais passer plus de C + r T.
- Coder une attente exponentielle plafonnée avec une gigue qui raccourcit, tirée d'un générateur local à graine fixe, et expliquer pourquoi la gigue évite de recréer le pic.
- Relancer seulement ce qui mérite de l'être, sans attendre après le dernier échec, en rendant toute l'histoire des tentatives à l'appelant, comme le ferait `@Retryable` avec `noRetryFor`.
- Calculer un percentile au rang le plus proche sans erreur d'indice ni piège du flottant, et expliquer pourquoi un contrat de service se surveille sur le p95.
- Tenir un budget sans jamais cacher un dépassement, et compter les tâches finançables par la partie entière inférieure.

Le palier 12 assemble tous les modules en un seul `Agent`, rejoue les trois scénarios et l'évaluation de l'étape 77, puis montre comment remplacer le faux modèle par Claude. Le module de production n'y est pas câblé dans la boucle : le brancher autour du port du modèle est l'un de ses défis bonus.

Suite : [Palier 12 — Assemblage de l'agent complet](<../../../12-Assemblage-Agent-Complet/README.md>).
