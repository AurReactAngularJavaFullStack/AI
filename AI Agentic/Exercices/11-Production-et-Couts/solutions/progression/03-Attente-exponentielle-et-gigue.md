# Étape 3 — L'attente exponentielle et la gigue

> Palier 11 · Étape 3 sur 7 · Précédent : [Étape 2 — Le seau à jetons](<02-Seau-a-jetons.md>) · Suivant : [Étape 4 — Les relances sur erreur transitoire](<04-Relances-sur-erreur-transitoire.md>) · Énoncé : [README du palier 11](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Quand le fournisseur du modèle répond « surchargé » (529) ou « trop de requêtes » (429), relancer tout de suite aggrave la surcharge. On attend, et l'on attend de plus en plus longtemps : 1 s, puis 2 s, puis 4 s. Le test `TestBackoff.test_exponentielle_plafonnee` donne la suite exacte pour les tentatives 1 à 7 : `[1, 2, 4, 8, 16, 30, 30]`. Écris-la en face des numéros de tentative, et la formule apparaît : la tentative k attend b × 2ᵏ⁻¹, avec b = 1, et jamais plus que le plafond de 30 s. L'exposant est k − 1, pas k : la première relance attend la base elle-même.

Le second test, `test_gigue_tiree_d_un_generateur_local`, fabrique un `random.Random(3)`, lit son premier tirage u, puis appelle la fonction avec un **autre** `random.Random(3)` et vérifie que l'attente vaut 4 × (1 − 0,5 u). Cela impose deux choses : la fonction **reçoit** son générateur au lieu d'appeler le hasard global, et elle en consomme exactement un tirage. C'est la seule façon d'avoir un hasard reproductible, donc testable.

L'ordre d'écriture : les gardes, l'attente nominale plafonnée, puis la gigue.

## Une première version, avec trois erreurs

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`attente_backoff(tentative, base_s, plafond_s, gigue)`** — Ce brouillon ressemble à un visiteur impatient qui double sa patience à chaque porte close, mais en commençant trop tard, sans jamais se fixer de limite et en tirant au sort une rallonge plutôt qu'un raccourci. Il reçoit le numéro de la tentative, la base, un plafond qu'il n'utilise jamais et la gigue, calcule base × 2 à la puissance `tentative`, puis multiplie par 1 + gigue × un tirage du hasard global du module `random`. Il rend cette attente : 2 s au lieu de 1 à la première relance, 32 768 s à la quinzième, et une valeur imprévisible d'une exécution à l'autre, donc intestable.

```python
# [extrait] brouillon
import random


def attente_backoff(tentative, base_s=1.0, plafond_s=30.0, gigue=0.0):
    attente = base_s * 2 ** tentative                 # 2, 4, 8… : décalé d'un rang
    return attente * (1 + gigue * random.random())    # hasard global, et peut dépasser le plafond
```

**L'exposant est décalé** : la première relance attend 2 s au lieu de 1, et le test échoue dès le premier élément. **Il n'y a pas de plafond** : la tentative 15 attendrait 2¹⁵ = 32 768 s, plus de neuf heures, alors que le client est parti depuis longtemps. **La gigue est mal faite, deux fois** : `1 + g × u` **allonge** l'attente, si bien qu'aucun plafond ne tiendrait même s'il existait ; et `random.random()` lit l'état global du module, partagé par tout le programme, si bien que deux exécutions donnent deux attentes différentes et qu'aucun test ne peut prédire la valeur.

## La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`attente_backoff(tentative, base_s, plafond_s, gigue, rng)`** — La version juste est un sablier réglable qu'on retourne avant chaque nouvel essai : sa durée double d'une fois sur l'autre jusqu'à une butée, et une petite main tremblante en retire parfois quelques grains pour que tous les sabliers d'une même salle ne se vident pas ensemble. Elle reçoit le numéro de la relance, la base de 1 s, le plafond de 30 s, la gigue, nulle par défaut, et un générateur `rng` facultatif ; elle lève `ValueError` pour une tentative inférieure à 1, une base nulle ou négative ou un plafond sous la base, et une gigue hors de [0 ; 1]. Elle calcule min(plafond, base × 2ᵏ⁻¹), puis, seulement si un générateur est fourni et la gigue positive, la multiplie par 1 − gigue × u avec un seul tirage. Elle rend 1, 2, 4, 8, 16, 30 et 30 s pour les tentatives 1 à 7, et 3,524071 s pour la troisième avec une gigue de 0,5 et `random.Random(3)`.

```python
# [extrait] agent/production.py
def attente_backoff(tentative: int, base_s: float = 1.0, plafond_s: float = 30.0, gigue: float = 0.0,
                    rng: random.Random | None = None) -> float:
    """Attente avant la relance n° `tentative` (>= 1) : a = min(P, b · 2^(n−1)) × (1 − g · u), u ∈ [0, 1).

    La gigue ne fait que RACCOURCIR l'attente, d'au plus la fraction g : elle désynchronise des
    clients qui ont échoué ensemble, et le plafond P tient toujours. Sans `rng` (ou g = 0), pas de gigue.
    Exemple : b = 1 s, P = 30 s : 1, 2, 4, 8, 16, 30, 30… ; avec g = 0.5 et u = 0.4, la 3e attente
    vaut 4 × (1 − 0.2) = 3.2 s.
    """
    if tentative < 1:
        raise ValueError("tentative >= 1")
    if base_s <= 0 or plafond_s < base_s:
        raise ValueError("il faut 0 < base_s <= plafond_s")
    if not 0 <= gigue <= 1:
        raise ValueError("la gigue est dans [0, 1]")
    attente = min(plafond_s, base_s * 2 ** (tentative - 1))
    if rng is not None and gigue > 0:
        attente *= 1 - gigue * rng.random()
    return attente
```

**La signature.** Les valeurs par défaut (1 s de base, 30 s de plafond, pas de gigue) donnent la suite du test sans autre argument. Le générateur est un paramètre optionnel typé `random.Random | None` : la fonction ne crée jamais son hasard, elle le reçoit. En Java, on passerait de la même façon un `java.util.Random` construit avec une graine, au lieu d'appeler `Math.random()`.

**Les trois gardes.** Une tentative 0 n'a pas de sens : la première relance est la numéro 1. Une base nulle ou négative ferait des attentes nulles ou négatives, et un plafond inférieur à la base rendrait la première attente plus courte que la base, ce qui contredit le paramètre ; on refuse les deux d'un coup avec `base_s <= 0 or plafond_s < base_s`. Enfin, une gigue hors de [0 ; 1] donnerait, au-delà de 1, un facteur 1 − g u négatif, donc une attente négative. Le test `test_entrees_invalides` essaie exactement ces quatre cas (tentative 0, base 0, plafond 0,5 sous une base de 1, gigue 1,5).

**L'attente nominale** : `min(plafond_s, base_s * 2 ** (tentative - 1))`. L'opérateur `**` est la puissance en Python ; `2 ** (tentative - 1)` vaut 1, 2, 4, 8… Le `min` applique le plafond : à la tentative 6, la formule donne 32 et le plafond ramène à 30.

**La gigue.** On ne l'applique que si un générateur est fourni **et** que la gigue est strictement positive. La seconde condition n'est pas cosmétique : avec g = 0, le facteur vaudrait 1, mais l'appel à `rng.random()` consommerait quand même un tirage et décalerait toute la suite des tirages suivants du même générateur. Le facteur `1 - gigue * rng.random()` est dans ]1 − g ; 1], puisque u est dans [0 ; 1) : l'attente est **raccourcie** d'au plus la fraction g, jamais allongée, et le plafond reste vrai. Avec g = 0,5, la troisième attente tombe quelque part dans ]2 ; 4] secondes.

**Pourquoi raccourcir au hasard ?** Quand 500 clients reçoivent la même erreur au même instant, ils relanceraient tous au même instant, sans gigue, et recréeraient le pic qui a causé l'erreur. La gigue les étale. C'est ce que fait Spring Retry avec `ExponentialRandomBackOffPolicy` (intervalle initial, multiplicateur, intervalle maximal), ou Resilience4j avec `IntervalFunction.ofExponentialRandomBackoff`. L'étape 12 du cours compare plusieurs façons de tirer la gigue ; celle-ci, multiplicative et bornée par g, garde la croissance exponentielle visible.

```text
# [extrait] console
>>> import random
>>> from agent.production import attente_backoff
>>> [attente_backoff(n) for n in range(1, 8)]
[1.0, 2.0, 4.0, 8.0, 16.0, 30.0, 30.0]
>>> random.Random(3).random()
0.23796462709189137
>>> attente_backoff(3, gigue=0.5, rng=random.Random(3))
3.5240707458162173
>>> rng = random.Random(7)
>>> [round(attente_backoff(3, gigue=0.5, rng=rng), 3) for _ in range(5)]
[3.352, 3.698, 2.698, 3.855, 2.928]
```

La troisième ligne montre le calcul du test : 4 × (1 − 0,5 × 0,237965) = 3,524071. La dernière montre cinq troisièmes attentes avec le même générateur : toutes dans ]2 ; 4], toutes différentes, et pourtant identiques à chaque exécution du programme, parce que la graine est fixée.

**Le piège classique** est de tester `if rng:` au lieu de `if rng is not None:`. Ici, cela marcherait, parce qu'un objet `random.Random` est toujours vrai ; mais l'habitude est mauvaise, car avec un entier ou une liste vide, la valeur 0 ou `[]` serait prise pour une absence. On compare explicitement à `None`, comme on écrit `if (rng != null)` en Java.

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_11_production.TestBackoff
```

Les trois tests passent : la suite plafonnée, la gigue tirée d'un générateur local, et les quatre entrées invalides.
