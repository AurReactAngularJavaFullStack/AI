# Étape 4 — Gravité et score de risque

> [Énoncé du palier 09](<../../README.md>) · Précédent : [Étape 3 — Le journal d'audit chaîné](<03-Journal-d-audit-chaine.md>) · Suivant : [Étape 5 — Veto et décision](<05-Veto-et-decision.md>)

## Comment raisonner

La politique dit si un rôle **a le droit** d'appeler un outil. Elle ne dit rien de **cet appel-là** : un client a le droit de virer de l'argent, mais un virement de 180 000 AED demandé par un courriel douteux ne se traite pas comme un loyer de 2 500 AED. Il faut un nombre qui résume le risque d'un appel précis, et des seuils qui transforment ce nombre en décision.

On part de la formule de l'étape 67 et on la traduit dans l'ordre où elle se lit : d'abord les **constantes** (poids, seuils, tables), parce qu'elles fixent l'échelle ; puis la **gravité**, qui est une entrée du score ; enfin le **score**, dont on protège la propriété essentielle, rester dans [0, 1], par deux validations.

## Les constantes

```python
# [extrait] agent/garde_fous.py
POIDS = (0.4, 0.4, 0.2)             # (w_s, w_g, w_u) : sensibilité, gravité de l'action, incertitude
TAU_REVUE, TAU_BLOCAGE = 0.5, 0.75  # seuils illustratifs, à calibrer sur l'historique
MONTANT_VETO_AED = 25_000           # illustratif : au-delà, revue humaine obligatoire
SENSIBILITE = {"publique": 0.0, "interne": 0.3, "personnelle": 0.7, "sensible": 1.0}
GRAVITE = {"lecture": 0.0, "ecriture_reversible": 0.5, "irreversible": 1.0}
INCERTITUDE_MODELE = 0.1            # illustratif : par exemple 1 − fidélité mesurée (étape 67)
```

**Ligne par ligne.**

- `POIDS` : la sensibilité des données et la gravité de l'action comptent autant (0,4 chacune), l'incertitude du modèle un peu moins (0,2). La somme vaut 1, condition de la borne [0, 1].
- `TAU_REVUE, TAU_BLOCAGE = 0.5, 0.75` : une affectation multiple. Deux seuils pour deux décisions de nature différente (une revue coûte quelques minutes d'un humain, un blocage interdit l'action) ; un seul seuil obligerait à choisir entre trop bloquer et laisser passer sans regard (étape 67, point 3).
- `MONTANT_VETO_AED` : 25 000 AED, la valeur que l'étape 67 justifie par le coût espéré, une revue à 25 AED divisée par une probabilité de dommage plancher de 0,001. `25_000` s'écrit avec un tiret bas pour la lisibilité, comme `25_000` en Java.
- `SENSIBILITE` et `GRAVITE` traduisent des catégories métier en nombres de [0, 1]. On ne laisse pas le modèle choisir ces nombres : ils viennent de l'étiquetage des données et du type de l'outil.
- `INCERTITUDE_MODELE` : l'incertitude par défaut, par exemple 1 − fidélité mesurée ; un détecteur d'injection la pousserait à 1.

Tous ces chiffres sont **illustratifs** : en production, on les calibre sur l'historique des actions déjà jugées.

## La gravité

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`gravite(type_action, montant_aed, montant_ref_aed)`** — Cette fonction se comporte comme un expert en sinistres qui lit d'abord la catégorie du dossier, puis jette un œil au montant pour décider s'il faut monter d'un cran. Elle reçoit le type d'action, le montant en AED, nul par défaut, et un montant de référence de 50 000 AED ; elle lève `ValueError` si le type n'est pas une clé de `GRAVITE`, si le montant est négatif ou si la référence est nulle ou négative. Sinon, elle ramène le rapport montant / référence sous le plafond de 1 et rend le plus grand des deux nombres, la gravité du type ou ce rapport plafonné : 180 000 AED donnent 3,6, ramené à 1, et une écriture réversible de 40 000 AED passe de 0,5 à 0,8. Le montant peut donc relever la gravité, jamais l'abaisser.

```python
# [extrait] agent/garde_fous.py
def gravite(type_action: str, montant_aed: float = 0.0, montant_ref_aed: float = 50_000) -> float:
    ...
    if type_action not in GRAVITE:
        raise ValueError(f"type d'action inconnu : {type_action}")
    if montant_aed < 0 or montant_ref_aed <= 0:
        raise ValueError("montant >= 0 et montant de référence > 0")
    return max(GRAVITE[type_action], min(1.0, montant_aed / montant_ref_aed))
```

**Ligne par ligne.**

- Un type inconnu lève `ValueError` au lieu d'une `KeyError` obscure : le message dit quoi corriger. Un montant négatif n'a pas de sens, et un montant de référence nul provoquerait une division par zéro.
- `min(1.0, montant / référence)` ramène le montant dans [0, 1] : 180 000 AED donnent 3,6, plafonné à 1.
- `max(gravité du type, …)` : le montant ne peut que **relever** la gravité, jamais l'abaisser. Une action irréversible de 10 AED reste à 1 ; une écriture réversible de 40 000 AED monte de 0,5 à 0,8.

**Le piège classique.** Écrire `min(1.0, max(...))` dans l'autre ordre, ou oublier le plafond : sans `min(1.0, …)`, un virement de 180 000 AED donnerait g = 3,6, et le score de risque sortirait de [0, 1] (`score_risque` le refuserait d'ailleurs, ce qui est la deuxième ligne de défense).

## Le score

D'abord la version qui « marche » sur l'exemple :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`score_risque(s, g, u, poids)`** — Ce brouillon est une balance de marché qui pèse tout ce qu'on pose sur ses plateaux sans jamais vérifier que les poids sont étalonnés. Il reçoit les trois signaux s, g, u et le triplet de poids, `POIDS` par défaut, déballe ce triplet en trois coefficients et rend directement la somme pondérée. Il donne bien 0,70 pour (0,7 ; 1 ; 0,1), mais il ne lève jamais d'exception : une entrée de 1,2 ou des poids de somme 1,5 produisent un nombre qui sort de [0, 1] sans que personne ne s'en aperçoive, et les seuils de décision perdent alors leur sens.

```python
# [extrait] brouillon
def score_risque(s, g, u, poids=POIDS):
    w_s, w_g, w_u = poids
    return w_s * s + w_g * g + w_u * u
```

Elle rend bien 0,70 pour (0,7 ; 1 ; 0,1). Mais `score_risque(1.2, 0, 0)` rend 0,48 sans broncher, alors qu'une entrée de 1,2 est une erreur en amont (une perplexité brute passée sans transformation, par exemple), et `score_risque(1, 1, 1, (0.5, 0.5, 0.5))` rend 1,5 : les seuils 0,5 et 0,75 n'ont plus de sens. La propriété R ∈ [0, 1] démontrée dans l'énoncé repose sur deux hypothèses ; le code doit les **imposer** :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`score_risque(s, g, u, poids)`** — La même balance, cette fois tenue par un vérificateur des poids et mesures qui contrôle l'instrument avant chaque pesée. La fonction reçoit les mêmes trois signaux et le même triplet de poids ; elle lève `ValueError` si l'une des entrées sort de [0, 1], puis une seconde `ValueError` si un poids est négatif ou si la somme des poids s'écarte de 1 de plus de 10⁻⁹, tolérance nécessaire parce que des flottants ne s'additionnent jamais tout à fait exactement. Une fois ces deux préconditions tenues, elle déballe les poids et rend la somme pondérée R, garantie dans [0, 1] : 0,70 pour le virement de l'étape 77, et sur la grille de 125 points un minimum de 0 et un maximum de 1 à 10⁻¹² près.

```python
# [extrait] agent/garde_fous.py
def score_risque(s: float, g: float, u: float, poids: tuple[float, float, float] = POIDS) -> float:
    ...
    if not all(0 <= x <= 1 for x in (s, g, u)):
        raise ValueError("chaque entrée doit être dans [0, 1]")
    if any(w < 0 for w in poids) or abs(sum(poids) - 1) > 1e-9:
        raise ValueError("les poids doivent être >= 0 et de somme 1")
    w_s, w_g, w_u = poids
    return w_s * s + w_g * g + w_u * u
```

**Ligne par ligne.**

- `all(0 <= x <= 1 for x in (s, g, u))` : la comparaison chaînée de Python, `0 <= x <= 1`, se lit comme en mathématiques (en Java, `0 <= x && x <= 1`).
- `any(w < 0 for w in poids)` refuse un poids négatif, qui inverserait l'effet d'un signal (plus de risque ferait baisser le score).
- `abs(sum(poids) - 1) > 1e-9` : la somme des poids doit valoir 1, **à une tolérance près**. Comparer des flottants par égalité est fragile : en Python, `0.6 + 0.3 + 0.1` vaut `0.9999999999999999`.
- `w_s, w_g, w_u = poids` déballe le tuple, puis la somme pondérée.

**Pourquoi R est dans [0, 1].** Chaque terme est compris entre 0 et son poids, puisque l'entrée est entre 0 et 1 et le poids positif ; la somme est donc comprise entre 0 et la somme des poids, qui vaut 1. C'est la démonstration 2 de l'étape 77, et le test de la grille la vérifie sur 125 points.

**Analogie Java.** Ces deux validations sont des préconditions, comme `Objects.requireNonNull` ou un `@DecimalMin("0") @DecimalMax("1")` de Bean Validation : on refuse l'entrée invalide à la frontière plutôt que de rendre un résultat faux plus loin.

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_09_garde_fous.TestRisque.test_gravite_et_score
python -m unittest -v tests.test_09_garde_fous.TestRisque.test_borne_sur_la_grille
```

Le premier vérifie `gravite("irreversible", 180_000) == 1.0`, `gravite("ecriture_reversible", 40_000) ≈ 0.8`, le score du virement de 77 (0,28 + 0,40 + 0,02 = 0,70) et le refus d'un type inconnu. Le second calcule R sur les 125 combinaisons de {0 ; 0,25 ; 0,5 ; 0,75 ; 1}³ : le minimum vaut exactement 0, le maximum 1 à 10⁻¹² près (les flottants, encore), une entrée de 1,2 et des poids de somme 1,5 sont refusés. Le troisième test de la classe, sur le veto et la décision, attend l'étape suivante.
