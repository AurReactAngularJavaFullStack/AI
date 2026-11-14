# Étape 4 — Le scénario du crédit

> Palier 12 · Étape 4 sur 8 · Précédent : [Étape 3 — Agent.repondre](<03-Agent-repondre.md>) · Suivant : [Étape 5 — Les scénarios réglementaire et du virement piégé](<05-Scenarios-reglementation-et-virement.md>) · Énoncé : [README du palier 12](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Un scénario de bout en bout se construit comme un test d'intégration : on fixe ce que le modèle va dire (le script du faux modèle), on fait tourner le vrai code, et l'on vérifie un **objectif métier**, pas seulement l'absence d'erreur. Avant d'écrire le script, refais les nombres à la main, comme dans le rappel de cours de l'énoncé : mensualité 5 558,32 AED, ratio 0,289, conversion 1 513,50 USD, scores de mémoire 0,9769 et 0,8070. Ce sont eux que le modèle scripté « demande » aux outils, et que les outils doivent rendre.

Il faut d'abord trois petites fonctions utilitaires, que les trois scénarios et l'évaluation partagent : une fabrique d'agent sur faux modèle, un lecteur de trace et la mémoire du client. On les écrit en premier, puis les constantes du scénario, puis le scénario.

## Les trois utilitaires

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`construire_agent(script, memoire, session)`** — Cette fonction est la loge où l'on habille l'agent pour une répétition, avec en face de lui un partenaire qui récite un texte appris par cœur. Elle reçoit la liste des réponses que le faux modèle doit rejouer, et facultativement une mémoire et une session, puis rend `Agent(FakeLLM(script), memoire=memoire, session=session)`, sans rien d'autre. Elle ne lève rien par elle-même ; son intérêt est de marquer la frontière entre test et production, puisque c'est cette seule ligne qui deviendrait `Agent(ClaudeLLM(), …)` le jour où l'on branche le vrai modèle.

**`sortie_outil(res, nom)`** — Cette fonction est le greffier qui feuillette le compte rendu d'audience et s'arrête à la première intervention du témoin qu'on lui nomme. Elle reçoit le résultat d'une exécution et un nom d'outil, parcourt avec un générateur les triplets (nom, arguments, sortie) de `res["trace"]` et rend, grâce à `next`, la sortie du premier appel qui porte ce nom, ou `None` si aucun ne le porte. Elle ne dépend d'aucun indice fixe, si bien qu'un modèle qui change l'ordre de ses appels ne la trompe pas : dans le scénario du crédit, elle rend `{'ratio': 0.289, 'recevable': True}` pour le ratio et `None` pour la TVA.

**`memoire_client()`** — Cette fonction tire du classeur quatre fiches toutes neuves sur le client, comme on imprime un formulaire vierge pour chaque rendez-vous plutôt que de réutiliser celui qu'un collègue a déjà annoté. Elle ne reçoit rien et rend une liste de quatre `Souvenir` : le salaire de 40 000 AED vu au jour 85 avec l'importance 9, le crédit auto de 6 000 AED vu au jour 60 avec l'importance 8, le prêt personnel sur 48 mois vu au jour 0 avec l'importance 4, et le taux de change vu au jour 88 avec l'importance 2, les montants étant formatés par `fr`. Comme le rappel remet à 90 le jour d'accès des souvenirs relus, fabriquer des objets neufs à chaque appel garantit que chaque test part de la même mémoire.

```python
# [extrait] agent/assemblage.py
def construire_agent(script: list[Reponse], memoire: list[Souvenir] | None = None, session: dict | None = None) -> Agent:
    """Un agent branché sur un FakeLLM qui rejoue `script`. Pour la production : `Agent(ClaudeLLM(), …)`."""
    return Agent(FakeLLM(script), memoire=memoire, session=session)


def sortie_outil(res: dict, nom: str):
    """La sortie du premier appel à l'outil `nom` dans la trace, ou None s'il n'a pas été appelé."""
    return next((sortie for n, _, sortie in res["trace"] if n == nom), None)


def memoire_client() -> list[Souvenir]:
    """Les quatre souvenirs du scénario (a), neufs à chaque appel (le rappel modifie `jour_acces`)."""
    return [Souvenir(f"Salaire mensuel déclaré au dossier de crédit : {fr(40_000, 0)} AED", 85.0, 9),
            Souvenir(f"Crédit auto en cours : mensualité de {fr(6_000, 0)} AED", 60.0, 8),
            Souvenir("Cherchait un prêt personnel sur 48 mois", 0.0, 4),
            Souvenir("A demandé le taux de change du dirham en USD", 88.0, 2)]
```

**`construire_agent`** est une fabrique d'une ligne : un `FakeLLM` qui rejoue le script, enveloppé dans un `Agent`. Elle existe pour que les scénarios et l'évaluation n'aient pas à répéter `Agent(FakeLLM(...), ...)`, et pour marquer la frontière : en production, c'est cette ligne, et elle seule, qui devient `Agent(ClaudeLLM(), ...)`. En Spring, ce serait la méthode `@Bean` du profil `test`.

**`sortie_outil`** lit la trace, une liste de triplets (nom, arguments, sortie), et rend la sortie du **premier** appel à l'outil demandé. L'expression `next((… for … if …), None)` est l'idiome Python du « premier élément qui vérifie une condition, sinon une valeur par défaut » : le générateur entre parenthèses produit les sorties des appels portant ce nom, `next` prend la première, et rend `None` si le générateur est vide. En Java, on écrirait `trace.stream().filter(l -> l.nom().equals(nom)).map(Ligne::sortie).findFirst().orElse(null)`. Le piège serait d'écrire `res["trace"][1][2]` comme dans 77 : un indice fixe casse dès que le modèle appelle les outils dans un autre ordre, ce qu'un vrai modèle fera.

**`memoire_client`** rend les quatre souvenirs du scénario (a), avec le texte, le jour du dernier accès et l'importance de 77. Les montants passent par `fr(…, 0)` : « 40 000 » avec une espace fine, exactement comme dans 77, pour que le prompt soit identique au caractère près. La fonction fabrique des objets **neufs** à chaque appel. Une constante `MEMOIRE_CLIENT = [...]` partagée serait un piège : le rappel du premier test mettrait le `jour_acces` du salaire à 90, et le test suivant partirait d'une mémoire déjà relue, avec d'autres récences et d'autres scores.

## Les constantes du scénario

```python
# [extrait] agent/assemblage.py
QUESTION_CREDIT = (f"Je voudrais une hypothèque de {fr(1_000_000, 0)} AED sur 25 ans à 4,5 %. Avec mon salaire et mon "
                   f"crédit en cours, mon dossier est-il recevable ? Donnez aussi la mensualité en USD.")
A_MENSUALITE = {"principal": 1_000_000, "taux_annuel": 0.045, "n_mois": 300}
A_RATIO = {"existantes": 6_000, "nouvelle": 5558.32, "revenu": 40_000}
A_CONVERSION = {"montant_aed": 5558.32}
```

**`QUESTION_CREDIT`** est la question de 77. Deux f-strings collées par Python (les littéraux adjacents se concatènent) évitent une ligne trop longue. Remarque ce que le client **ne** dit pas : ni son salaire, ni sa mensualité en cours. C'est la mémoire qui doit les fournir.

**Les trois dictionnaires d'arguments** sont ceux que le modèle scripté envoie aux outils, et ceux que l'évaluation attend : `A_MENSUALITE` (1 000 000 AED, 4,5 %, 300 mois), `A_RATIO` (6 000 AED en cours, la nouvelle mensualité de 5 558,32 AED, 40 000 AED de revenu) et `A_CONVERSION`. Ils sont en constantes parce que deux endroits les utilisent : le script du modèle et la liste des appels attendus. Les écrire deux fois, c'est risquer qu'ils divergent, et que la Tool Call F1 tombe pour une faute de frappe.

## Le scénario

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`scenario_credit()`** — Cette fonction rejoue la scène de l'hypothèque comme un metteur en scène qui fait répéter une pièce dont il connaît chaque réplique, pour vérifier que le décor, les accessoires et les coulisses fonctionnent. Elle ne reçoit rien ; elle écrit un script de trois réponses, l'appel « a1 » à `mensualite`, puis dans une même réponse « a2 » à `ratio_endettement` et « a3 » à `convertir_aed_usd`, puis le texte final construit avec `fr`, crée un agent doté de `memoire_client()` et le fait répondre à `QUESTION_CREDIT`. Elle juge l'objectif atteint si le statut vaut « fini », si la réponse se termine par « dossier recevable. » et si la sortie du ratio est un dictionnaire dont `recevable` vaut exactement `True`, puis rend `{"agent", "res", "attendus", "but"}` : statut « fini » en 3 étapes, scores de mémoire 0,9769 et 0,807, et un journal de sept entrées dont la chaîne est intacte.

```python
# [extrait] agent/assemblage.py
def scenario_credit() -> dict:
    """Scénario (a), la demande de crédit : la mémoire fournit le salaire (0,9769) et le crédit auto (0,8070) ;
    mensualité 5 558,32 AED, puis ratio 0,289 et 1 513,50 USD dans la même réponse ; fini en 3 étapes.

    Rend {"agent", "res", "attendus", "but"}.
    """
    script = [
        Reponse("tool_use", [appel_outil("mensualite", A_MENSUALITE, "a1")]),
        Reponse("tool_use", [appel_outil("ratio_endettement", A_RATIO, "a2"),
                             appel_outil("convertir_aed_usd", A_CONVERSION, "a3")]),
        Reponse("end_turn", [texte(f"Mensualité {fr(5558.32)} AED, soit {fr(1513.5)} USD ; endettement total "
                                   f"{fr(28.9, 1)} % ≤ 50 % : dossier recevable.")]),
    ]
    agent = construire_agent(script, memoire=memoire_client())
    res = agent.repondre(QUESTION_CREDIT)
    ratio = sortie_outil(res, "ratio_endettement")
    but = (res["statut"] == "fini" and res["reponse"].endswith("dossier recevable.")
           and isinstance(ratio, dict) and ratio["recevable"] is True)
    attendus = [("mensualite", A_MENSUALITE), ("ratio_endettement", A_RATIO), ("convertir_aed_usd", A_CONVERSION)]
    return {"agent": agent, "res": res, "attendus": attendus, "but": but}
```

**Le script, réponse par réponse.** La première réponse s'arrête sur `"tool_use"` avec un seul bloc : le modèle demande la mensualité. La deuxième contient **deux** blocs `tool_use` : le ratio et la conversion ne dépendent que de la mensualité, le modèle les demande donc ensemble, et la boucle renverra leurs deux résultats dans un seul message. C'est ce qui fait tenir le scénario en trois appels au modèle au lieu de quatre, et la chaîne en six étapes : 0,98⁶ = 0,8858 au lieu de 0,98⁷ = 0,8681. La troisième réponse s'arrête sur `"end_turn"` avec le texte final. Chaque appel porte un identifiant (`"a1"`, `"a2"`, `"a3"`) que la boucle recopie dans le `tool_result` correspondant, comme l'exige l'API.

**Le texte final** est construit avec `fr` : `fr(5558.32)` donne « 5 558,32 », `fr(1513.5)` « 1 513,50 » et `fr(28.9, 1)` « 28,9 ». On ne tape pas ces nombres à la main : le test compare la réponse au caractère près, espaces fines comprises.

**L'exécution.** `construire_agent(script, memoire=memoire_client())` crée un agent neuf avec la mémoire du client, et `repondre(QUESTION_CREDIT)` fait tout le reste : rappel (le salaire à 0,9769, le crédit auto à 0,8070), prompt, boucle, journal.

**L'objectif métier.** Le cas est réussi si la boucle a fini, si la réponse conclut « dossier recevable. », **et** si l'outil de ratio a réellement rendu `recevable` à `True`. Ce dernier test est le plus important : une réponse qui dit « recevable » sans que le calcul l'ait établi serait un succès de façade. `isinstance(ratio, dict)` protège la lecture `ratio["recevable"]` : si l'outil n'a pas été appelé, `ratio` vaut `None` ; s'il a échoué, la sortie est une chaîne « ERREUR … ». Dans les deux cas, l'objectif est manqué sans que la fonction ne plante. `is True` exige le booléen lui-même, pas une valeur seulement « vraie ».

**Le retour.** Le dictionnaire rend l'agent (pour inspecter son journal, sa mémoire, les requêtes reçues par le faux modèle), le résultat, les appels attendus (pour la Tool Call F1) et l'objectif (pour la Goal Accuracy). L'évaluation de l'étape 6 n'aura qu'à appeler `noter` dessus.

```text
# [extrait] console
>>> from agent.assemblage import scenario_credit, sortie_outil
>>> s = scenario_credit()
>>> s["res"]["statut"], s["res"]["etapes"], s["but"]
('fini', 3, True)
>>> [round(score, 4) for score, _ in s["res"]["rappel"]], [x.jour_acces for x in s["agent"].memoire]
([0.9769, 0.807], [90.0, 90.0, 0.0, 88.0])
>>> sortie_outil(s["res"], "ratio_endettement"), sortie_outil(s["res"], "tva")
({'ratio': 0.289, 'recevable': True}, None)
>>> len(s["agent"].journal.textes()), s["agent"].journal.verifier()
(7, None)
```

Le journal compte sept entrées : la question, trois décisions de politique (une par outil appelé) et trois lignes de trace ; `verifier()` rend `None`, la chaîne SHA-256 est intacte.

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_12_assemblage.TestScenarioCredit
```

Les cinq tests passent : la décision finale (« fini », 3 étapes, la réponse exacte), les appels et leurs sorties, la mémoire rappelée dans le système (et pas le souvenir du taux de change), les sept outils stricts envoyés au modèle, et le journal (une décision de politique pour `mensualite`, chaîne intacte).
