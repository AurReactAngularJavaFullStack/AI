# Étape 5 — Veto et décision

> [Énoncé du palier 09](<../../README.md>) · Précédent : [Étape 4 — Gravité et score de risque](<04-Gravite-et-score-de-risque.md>) · Suivant : [Étape 6 — L'approbation humaine](<06-Approbation-humaine.md>)

## Comment raisonner

Le score est une moyenne, et une moyenne **compense** : un signal faible peut cacher un signal fort. Avec les poids (0,4 ; 0,4 ; 0,2), une action irréversible sur des données peu sensibles, avec un modèle confiant, donne R = 0,4 × 0,1 + 0,4 × 1 + 0,2 × 0,1 = 0,46, sous le seuil de revue. Le cas général : si s = u = 0, R = 0,4 × g ≤ 0,4 < 0,5, donc **aucune** action irréversible ne déclenche de revue par sa seule gravité.

Deux réponses possibles. Relever le poids de la gravité déformerait le score pour toutes les autres actions. La bonne réponse est de **sortir l'irréversibilité de la somme** : une règle dure, non compensatoire, le veto. On écrit donc deux fonctions séparées : `veto`, qui ne regarde pas le score, et `decider`, qui combine le score et le veto en une décision.

## Le veto

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`veto(type_action, montant_aed)`** — Cette fonction tient le rôle du cadenas que l'on pose sur certains tiroirs, quelle que soit la confiance qu'inspire celui qui veut les ouvrir. Elle reçoit le type d'action et le montant en AED, ne consulte aucun score, et rend un booléen qui vaut vrai si le type est `"irreversible"` ou si le montant atteint `MONTANT_VETO_AED`, c'est-à-dire 25 000 AED, bornes comprises. Elle ne lève aucune exception ; son verdict est transmis à `decider` pour forcer une revue humaine là où la moyenne pondérée, qui compense un signal fort par deux signaux faibles, aurait laissé passer l'action.

```python
# [extrait] agent/garde_fous.py
def veto(type_action: str, montant_aed: float) -> bool:
    ...
    return type_action == "irreversible" or montant_aed >= MONTANT_VETO_AED
```

Une expression booléenne, deux causes indépendantes. L'action est irréversible : on ne peut pas revenir en arrière, donc un humain doit la voir. Ou le montant atteint 25 000 AED, quel que soit le type : même une écriture réversible de ce montant mérite un regard. Le seuil est `>=` : 25 000 AED exactement déclenchent le veto, ce que dit l'énoncé (« montant ≥ 25 000 AED »).

**Analogie Java.** C'est une règle métier qui court-circuite le calcul, comme un `if (operation.isIrreversible()) return Decision.REVIEW;` placé avant tout scoring dans un service de détection de fraude.

## La décision : la zone la plus grave d'abord

Le brouillon qui suit l'ordre de lecture « autoriser, revue, bloquer » à l'envers se trompe :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`decider(r, veto_actif, tau_revue, tau_blocage)`** — Ce brouillon est un aiguilleur qui ouvre d'abord la voie du milieu et ne regarde la voie de garage qu'ensuite, quand le train est déjà parti. Il reçoit le score R, le drapeau de veto et deux seuils, 0,5 et 0,75 par défaut, rend `"revue"` dès que R atteint le seuil de revue ou que le veto est actif, puis seulement `"bloquer"` si R atteint le seuil de blocage, et sinon `"autoriser"`. Comme tout R au-dessus de 0,75 est aussi au-dessus de 0,5, la branche du blocage n'est jamais atteinte : un R de 0,88 part en revue, et il ne valide même pas ses seuils.

```python
# [extrait] brouillon
def decider(r, veto_actif, tau_revue=0.5, tau_blocage=0.75):
    if r >= tau_revue or veto_actif:
        return "revue"
    if r >= tau_blocage:
        return "bloquer"          # jamais atteint : 0.88 >= 0.5 a déjà rendu « revue »
    return "autoriser"
```

Pour R = 0,88, avec ou sans veto, la première condition est vraie et la fonction rend « revue » : la branche « bloquer » est inaccessible, puisque tout R ≥ 0,75 est aussi ≥ 0,5. Un virement poussé par une injection détectée partirait chez un humain au lieu d'être refusé, et l'humain pourrait l'approuver par erreur. Il faut tester les zones **de la plus grave à la moins grave** :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`decider(r, veto_actif, tau_revue, tau_blocage)`** — Le même aiguilleur, devenu prudent, inspecte maintenant les voies dans l'ordre du danger. La fonction reçoit le score R, le veto et les seuils `TAU_REVUE` et `TAU_BLOCAGE` par défaut ; elle lève d'abord `ValueError` si l'on n'a pas 0 ≤ τ_revue < τ_blocage ≤ 1, puis rend `"bloquer"` si R ≥ τ_blocage, veto ou pas, ensuite `"revue"` si R ≥ τ_revue ou si le veto est actif, et enfin `"autoriser"`. Le retrait à R = 0,46 est ainsi autorisé sans veto et mis en revue avec, R = 0,88 est bloqué dans les deux cas, et pour une action irréversible la branche « autoriser » ne peut plus jamais être atteinte.

```python
# [extrait] agent/garde_fous.py
def decider(r: float, veto_actif: bool, tau_revue: float = TAU_REVUE, tau_blocage: float = TAU_BLOCAGE) -> str:
    ...
    if not 0 <= tau_revue < tau_blocage <= 1:
        raise ValueError("il faut 0 <= tau_revue < tau_blocage <= 1")
    if r >= tau_blocage:
        return "bloquer"
    if r >= tau_revue or veto_actif:
        return "revue"
    return "autoriser"
```

**Ligne par ligne.**

- La validation des seuils : `0 <= tau_revue < tau_blocage <= 1` en une comparaison chaînée. L'inégalité **stricte** au milieu garantit que la zone de revue existe ; des seuils égaux ou inversés feraient disparaître une des trois décisions.
- `r >= tau_blocage` d'abord : au-dessus de 0,75, on bloque, **veto ou pas**. Le veto ne peut que durcir une décision, jamais l'adoucir en revue.
- Ensuite la revue, pour un score moyen **ou** un veto actif. C'est ici que le veto rattrape le retrait de 0,46.
- Sinon, l'action part seule.

**La propriété qui compte.** Pour une action irréversible, le veto est vrai. Il ne reste que deux chemins : R ≥ 0,75 donne « bloquer », sinon la deuxième condition est vraie (à cause du veto) et donne « revue ». La branche « autoriser » est **inaccessible** : c'est la démonstration 3 de l'étape 77, vérifiée ici par trois lignes de code.

**Analogie Java.** L'ordre des tests est celui des blocs `catch`, du plus spécifique au plus général, ou celui des règles d'un pare-feu : la première règle qui correspond l'emporte, donc la plus restrictive passe en premier.

**Le piège classique.** Mettre le veto dans la première condition, `if r >= tau_blocage or veto_actif: return "bloquer"`. Tout virement, même un loyer de 2 500 AED, serait refusé sans recours : le veto doit envoyer chez l'humain, pas interdire.

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_09_garde_fous.TestRisque
```

`test_veto_et_decision` vérifie les trois veto de l'énoncé (irréversible à 10 AED : oui ; lecture à 30 000 AED : oui ; écriture réversible à 2 500 AED : non), puis R = 0,46 qui donne « autoriser » sans veto et « revue » avec, R = 0,88 qui donne « bloquer » malgré le veto, et le refus des seuils inversés (0,8 ; 0,7). Avec les deux tests de l'étape 4, toute la classe `TestRisque` est verte.
