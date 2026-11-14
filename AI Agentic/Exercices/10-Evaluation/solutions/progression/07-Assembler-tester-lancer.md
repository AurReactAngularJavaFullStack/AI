# Étape 7 — Assembler, tester, lancer la démo

> [Énoncé du palier 10](<../../README.md>) · Précédent : [Étape 6 — Le rapport et la barrière CI](<06-Rapport-et-barriere-CI.md>) · Palier suivant : [Palier 11 — Production et coûts](<../../../11-Production-et-Couts/README.md>)

## Comment raisonner

Les neuf fonctions passent leurs tests une à une. Il reste à voir le module **au travail** : un vrai jeu de cas, deux versions de l'agent, une décision. La démo fait exactement ce qu'un pipeline d'intégration continue ferait, avec un faux modèle scripté à la place de Claude.

## Le module complet, dans l'ordre

Le fichier `agent/evaluation.py` se lit de haut en bas dans l'ordre des étapes :

1. les imports : `json`, `math`, `re`, `Counter`, et `ESPACE_FINE` du palier 03, le seul module antérieur dont il dépend ;
2. `wilson` (étape 1) ;
3. `tool_call_f1` (étape 2) ;
4. `goal_accuracy` (étape 3) ;
5. `nombres` et `fidelite_approchee` (étape 4), puis `moyenne_definie` (étape 3) ;
6. `noter` (étape 5) ;
7. `rapport`, `SEUILS` et `barriere_ci` (étape 6).

Le module n'importe ni la boucle, ni les outils : il juge des résultats, il ne les produit pas. C'est l'appelant qui fait tourner l'agent.

## Comment la démo fabrique un cas

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cas(i, candidat)`** — Cette fonction de la démonstration est le metteur en scène d'un essai unique : elle écrit le texte que le faux modèle va jouer, le fait jouer sur une vraie boucle, puis tend la copie au correcteur. Elle reçoit le numéro i du dossier C-i et un booléen qui dit s'il faut jouer la version candidate ; la partie en pointillés calcule la vraie mensualité, le vrai ratio et le verdict, puis prépare le script, que la boucle `executer_agent` exécute ensuite sur un registre neuf d'outils métier. Elle prend comme sources les sorties d'outils de la trace, déclare le but atteint seulement si la boucle a fini, si la réponse se termine par le bon verdict et si la trace compte exactement deux appels, et rend la note produite par `noter` face aux appels attendus `mensualite` et `ratio_endettement`.

```python
# [extrait] demo.py
def cas(i: int, candidat: bool) -> dict:
    ...
    registre = enregistrer_outils_metier(Registre())
    res = executer_agent(FakeLLM(script), "s", f"Dossier C-{i}", registre.appelables(), registre.definitions_api())
    sources = [str(s) for _, _, s in res["trace"]]
    but = res["statut"] == "fini" and res["reponse"].endswith(f"dossier {verdict}.") and len(res["trace"]) == 2
    return noter(res, sources, [("mensualite", a1), ("ratio_endettement", a2)], but)
```

Le dossier C-i a un principal de 1 000 000 − 25 000 i AED, un revenu de 40 000 − 1 500 i AED et des mensualités en cours de 6 000 + 500 i AED ; la démo calcule d'abord la vraie mensualité, le vrai ratio et le verdict (« recevable » si le ratio ne dépasse pas 0,50), puis écrit le script du faux modèle. La production appelle `mensualite`, puis `ratio_endettement`, puis répond avec les deux chiffres et le verdict. La candidate, quand i vaut 1 modulo 4, s'arrête après la mensualité et écrit « endettement estimé à 35 % : dossier recevable ».

Ensuite, les lignes ci-dessus : la boucle du palier 05 fait tourner le script sur les outils métier ; les sources sont les sorties d'outils, écrites en texte ; le but est atteint si la boucle a fini, si la réponse se termine par le bon verdict et si les **deux** outils ont été appelés ; `noter` produit les trois mesures. Le critère de réussite vit dans la démo, pas dans le module : c'est le métier qui dit ce qu'est un dossier réussi.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`main()`** — Dans cet extrait, la fonction principale de la démonstration est le jury d'un concours qui fait passer deux candidats, l'un après l'autre, sur les mêmes dix-huit épreuves. Elle ne reçoit rien ; pour la version production puis pour la version candidate, elle appelle `cas` sur les dossiers 1 à 18, rassemble les dix-huit notes dans un `rapport`, et soumet ce rapport à `barriere_ci` avec les `SEUILS` du module pour obtenir un code et ses motifs. La suite, en pointillés, imprime ces résultats : la production obtient 18 sur 18 et le code 0, la candidate 13 sur 18, trois motifs et le code 1 ; elle ne rend rien.

```python
# [extrait] demo.py
def main() -> None:
    ...
    for version in ("production", "candidate"):
        rap = rapport([cas(i, version == "candidate") for i in range(1, 19)])
        code, motifs = barriere_ci(rap, SEUILS)
```

Pour chaque version, 18 cas, un rapport, une décision.

## Toute la suite de tests

Depuis `projet/` :

```text
python -m unittest -v
```

La dernière ligne doit être `OK`, après `Ran 136 tests` : les 122 tests des paliers 01 à 09 et les 14 du palier 10.

## La démo

```text
python demo.py
```

Sortie attendue, identique à celle de l'énoncé :

```text
Palier 10 — 18 dossiers de crédit C-1 à C-18, version production contre version candidate
  production : 18/18   Wilson [0.824 ; 1.000]   Tool F1 1.000   fidélité 1.000   → code 0
  candidate  : 13/18   Wilson [0.491 ; 0.875]   Tool F1 0.907   fidélité 0.861   → code 1
    - borne basse de Wilson 0.491 < 0.8
    - Tool Call F1 0.907 < 0.95
    - fidélité approchée 0.861 < 0.95
Pourquoi 18 cas et pas 3 : la borne basse de n sur n vaut n / (n + 1,96²)
   3 sur 3  → borne basse 0.438
  15 sur 15 → borne basse 0.796
  16 sur 16 → borne basse 0.806
  18 sur 18 → borne basse 0.824
  aucun cas : wilson(0, 0) = None ; barrière : (1, ['aucun cas évalué'])
OK — palier 10 terminé.
```

**Ligne par ligne, ce qui a produit quoi.**

**Production.** Les 18 dossiers ont leurs deux appels (F1 = 1), des chiffres tous présents dans les sorties d'outils (fidélité 1) et le bon verdict : 18 sur 18, borne basse 18 / 21,8416 = 0,824 ≥ 0,80, code 0.

**Candidate.** Les dossiers C-1, C-5, C-9, C-13 et C-17 (i = 4k + 1) sont fautifs : un appel sur deux (F1 2/3), un chiffre sur deux inventé (fidélité 0,5), et le but manqué parce que le ratio n'a pas été calculé (pour C-9, C-13 et C-17, le verdict « recevable » est en plus faux). 13 sur 18 : Tool F1 (13 + 5 × 2/3) / 18 = 0,907, fidélité (13 + 5 × 0,5) / 18 = 0,861, Wilson [0,491 ; 0,875]. Les trois seuils sont violés, d'où trois motifs et le code 1.

**Pourquoi 13 et non 14 comme au palier 12.** Ici, les 18 cas sont les variantes 1 à 18, dont cinq sont de la forme 4k + 1. L'étape 77 et le palier 12 évaluent les 3 scénarios de bout en bout plus les variantes 1 à 15, dont quatre seulement sont fautives : 14 sur 18. Même défaut, autre jeu de référence ; les tests de ce palier reprennent les nombres de 77.

**Le tableau n sur n.** La borne basse n / (n + z²) franchit 0,80 entre 15 cas (0,796) et 16 cas (0,806), comme le prévoit n ≥ 4z² = 15,37.

**Aucun cas.** `wilson(0, 0)` vaut `None`, et la barrière bloque un jeu vide.

## Ce qu'il faut retenir

- On décide sur la **borne basse** de Wilson, pas sur le taux : des cas parfaits ne prouvent pas 100 %, et il en faut au moins 16 pour prouver 80 %.
- La Tool Call F1 compare des **multi-ensembles** de clés canoniques (nom, JSON trié) : `Counter` et `&` font tout le travail.
- La fidélité approchée lit les **nombres** de la réponse, à la française, et cherche chacun dans les sources, à `math.isclose` près.
- Une métrique sans dénominateur vaut **`None`** et sort des moyennes ; `if v is not None`, jamais `if v`.
- `noter` adapte le résultat de la boucle aux métriques, sans lire la réponse d'une exécution qui n'a pas fini.
- La barrière **rend** un code et des motifs ; seul le script de CI quitte le programme.
- Un taux ne se compare qu'à un taux mesuré sur **les mêmes cas**.

## Et ensuite

L'agent sait refuser (palier 09) et se mesurer (palier 10). Il doit maintenant tenir en production : combien coûte une tâche en tokens, en USD et en AED, comment limiter le débit avec un seau à jetons, comment relancer un appel qui échoue sans saturer le fournisseur, et comment suivre le p95 des latences. C'est le [Palier 11 — Production et coûts](<../../../11-Production-et-Couts/README.md>).
