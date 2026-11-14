# Étape 6 — Les variantes et la barrière CI

> Palier 12 · Étape 6 sur 8 · Précédent : [Étape 5 — Les scénarios réglementaire et du virement piégé](<05-Scenarios-reglementation-et-virement.md>) · Suivant : [Étape 7 — Passer au vrai LLM](<07-Passer-au-vrai-LLM.md>) · Énoncé : [README du palier 12](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Trois scénarios réussis ne prouvent pas qu'un agent est bon. Le calcul du rappel de cours le montre : trois cas parfaits sur trois donnent une borne basse de Wilson de 3 / (3 + 1,96²) = 0,438, et il faut au moins 16 cas parfaits pour franchir 0,80. On a donc besoin d'un **jeu de référence** plus grand, que l'on fabrique à partir du scénario qui compte le plus : la demande de crédit, en quinze variantes dont les montants changent de façon régulière.

On veut aussi vérifier que la barrière sait dire **non**. Il faut donc une seconde version de l'agent, la « candidate », qui a un défaut réaliste : une fois sur quatre, elle saute le calcul du ratio et invente un chiffre plausible. Un bon jeu d'évaluation doit la bloquer.

L'ordre d'écriture : la fabrique des variantes (`demande_credit`), l'évaluation d'une version (`evaluer_version`), puis l'évaluation complète, qui ajoute les trois scénarios et compare les deux versions.

## Les quinze variantes

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`demande_credit(i, candidat)`** — Cette fonction est l'imprimerie d'un concours, qui tire le sujet numéro i, son corrigé et la copie qu'un candidat donné rendrait, en faisant glisser les montants d'un sujet au suivant. Elle reçoit le numéro i, de 1 à 15, et le choix de version ; elle calcule le principal 1 000 000 − 25 000 i, le revenu 40 000 − 1 500 i et les mensualités en cours 6 000 + 500 i, puis la mensualité arrondie au centime et le ratio arrondi à quatre décimales avec les fonctions mêmes des outils, et en déduit le verdict « recevable » si le ratio vaut au plus 0,50. Le script commence toujours par l'appel « v1 » à `mensualite` ; pour la candidate, quand i vaut 1 modulo 4, il conclut aussitôt avec un « endettement estimé à 35 % » inventé, sinon il appelle « v2 » le ratio et conclut avec le vrai pourcentage. Elle rend le quadruplet (script, question, appels attendus, verdict) : pour i = 1, 5 419,37 AED et 30,96 %, recevable ; pour i = 8, 51,60 %, non recevable.

```python
# [extrait] agent/assemblage.py
def demande_credit(i: int, candidat: bool = False) -> tuple[list, str, list, str]:
    """Variante i (1 à 15) du scénario (a) : principal 1 000 000 − 25 000 i, revenu 40 000 − 1 500 i,
    mensualités en cours 6 000 + 500 i. Rend (script, question, appels attendus, verdict).

    La version candidate, pour i = 1, 5, 9 et 13, saute le ratio et invente « endettement estimé à 35 % ».
    Exemple : i = 1 donne 975 000, 38 500 et 6 500 AED, une mensualité de 5 419,37 AED et un ratio de
    0,3096 (recevable) ; i = 8 donne un ratio de 0,516 (non recevable).
    """
    principal, revenu, existantes = 1_000_000 - 25_000 * i, 40_000 - 1_500 * i, 6_000 + 500 * i
    m = round(mensualite(principal, 0.045, 300), 2)
    ratio = round(ratio_endettement(existantes, m, revenu)[0], 4)
    verdict = "recevable" if ratio <= 0.50 else "non recevable"
    a1 = {"principal": principal, "taux_annuel": 0.045, "n_mois": 300}
    a2 = {"existantes": existantes, "nouvelle": m, "revenu": revenu}
    q = (f"Hypothèque de {fr(principal, 0)} AED à 4,5 % sur 300 mois ; revenu {fr(revenu, 0)} AED ; "
         f"mensualités en cours {fr(existantes, 0)} AED : recevable ?")
    script = [Reponse("tool_use", [appel_outil("mensualite", a1, "v1")])]
    if candidat and i % 4 == 1:
        script.append(Reponse("end_turn", [texte(f"Mensualité {fr(m)} AED ; endettement estimé à 35 % : dossier recevable.")]))
    else:
        script += [Reponse("tool_use", [appel_outil("ratio_endettement", a2, "v2")]),
                   Reponse("end_turn", [texte(f"Mensualité {fr(m)} AED ; endettement total {fr(ratio * 100)} % : "
                                              f"dossier {verdict}.")])]
    return script, q, [("mensualite", a1), ("ratio_endettement", a2)], verdict
```

**Les montants.** Chaque variante emprunte 25 000 AED de moins, gagne 1 500 AED de moins et rembourse déjà 500 AED de plus par mois que la précédente : le ratio monte régulièrement, et le dossier finit par passer le plafond. L'affectation multiple de la première ligne calcule les trois montants d'un coup.

**La vérité terrain.** La mensualité et le ratio sont calculés par **les mêmes fonctions que les outils** (palier 03), avec les mêmes arrondis : la mensualité au centime (`round(…, 2)`, comme l'outil `mensualite`), le ratio à quatre décimales (comme l'outil `ratio_endettement`). Le verdict attendu en découle, avec le plafond de 0,50 de la CBUAE. C'est une précaution essentielle : si la variante arrondissait autrement que l'outil, l'argument `nouvelle` du ratio différerait d'un centime, et la Tool Call F1 compterait une erreur qui n'existe pas. `ratio_endettement` rend un couple (ratio, recevable) : `[0]` prend le ratio.

**Les appels attendus et la question.** `a1` et `a2` sont les arguments exacts que le modèle doit envoyer. La question, construite avec `fr`, donne au modèle tous les montants : ici, pas de mémoire, le test porte sur le calcul.

**Le script.** Il commence toujours par l'appel à `mensualite`. Pour la candidate, quand `i % 4 == 1` (i = 1, 5, 9 et 13), il se termine tout de suite par une réponse qui **invente** « endettement estimé à 35 % » et conclut « recevable », sans appeler le ratio : c'est le défaut que l'évaluation doit attraper. Pour i = 9 et 13, la conclusion est même fausse, puisque ces dossiers ne sont pas recevables. Dans tous les autres cas, le script appelle le ratio, puis conclut avec le vrai pourcentage, `fr(ratio * 100)`, et le bon verdict.

**Le retour** est un quadruplet : le script pour le faux modèle, la question, les appels attendus (les **deux**, même pour la candidate fautive : on attend ce qu'un bon agent aurait fait) et le verdict.

Pour i = 1 : 975 000, 38 500 et 6 500 AED ; mensualité 5 419,37 AED ; ratio (6 500 + 5 419,37) / 38 500 = 0,309594, arrondi à 0,3096, d'où « endettement total 30,96 % : dossier recevable. ». Pour i = 8 : ratio 0,516, « 51,60 % : dossier non recevable. ». Les variantes 1 à 7 sont recevables, les variantes 8 à 15 ne le sont pas : le jeu contient les deux verdicts, ce qui empêche un agent qui répondrait toujours « recevable » de réussir.

## Évaluer une version

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`evaluer_version(candidat, communes)`** — Cette fonction est la session d'examen d'un candidat : on reprend son livret déjà noté sur trois épreuves, on y agrafe quinze copies nouvelles corrigées une à une, puis le jury rend son verdict. Elle reçoit le choix de version et les notes communes, en fait une copie pour ne pas toucher la liste de l'appelant, puis, pour i de 1 à 15, appelle `demande_credit`, fait répondre un agent neuf construit sur ce script et note le cas avec `noter`, le but exigeant une boucle finie, la bonne conclusion et un appel à `ratio_endettement` dans la trace. Elle agrège les dix-huit notes avec `rapport`, y range le code et les motifs de `barriere_ci` avec `SEUILS`, et rend ce rapport : 18 succès et le code 0 pour la production, 14 succès, une borne basse de 0,548 et le code 1 pour la candidate.

```python
# [extrait] agent/assemblage.py
def evaluer_version(candidat: bool, communes: list[dict]) -> dict:
    """Rapport d'une version sur les notes communes + les 15 variantes, avec "code" et "motifs" de la barrière CI."""
    notes = list(communes)
    for i in range(1, 16):
        script, q, attendus, verdict = demande_credit(i, candidat)
        res = construire_agent(script).repondre(q)
        but = (res["statut"] == "fini" and res["reponse"].endswith(f"dossier {verdict}.")
               and any(nom == "ratio_endettement" for nom, _, _ in res["trace"]))
        notes.append(noter(res, res["sources"], attendus, but))
    rap = rapport(notes)
    rap["code"], rap["motifs"] = barriere_ci(rap, SEUILS)
    return rap
```

**La copie des notes communes.** `list(communes)` crée une nouvelle liste : la boucle y ajoute quinze notes sans toucher la liste de l'appelant. Sans cette copie, l'évaluation de la production ajouterait ses quinze notes aux notes communes, et la candidate serait évaluée sur 33 cas au lieu de 18. C'est le même réflexe de copie défensive qu'à l'étape 2.

**Un agent neuf par cas.** `construire_agent(script).repondre(q)` crée un agent, avec sa propre horloge, son journal et son registre, pour chaque variante : aucun cas ne peut influencer le suivant. C'est l'isolation que l'on exige de tests unitaires, appliquée à l'évaluation.

**L'objectif d'une variante** a trois conditions : la boucle a fini, la réponse se termine par le bon verdict, **et** la trace contient un appel à `ratio_endettement`. La troisième condition est celle qui attrape la candidate pour i = 1 et 5 : sa conclusion « dossier recevable. » est juste par hasard, mais elle n'a pas été calculée. Un agent qui a raison sans savoir pourquoi n'est pas fiable, et l'évaluation ne doit pas le récompenser.

**La note du cas.** `noter` (palier 10) calcule la Tool Call F1 (les appels de la trace contre les deux appels attendus), recopie l'objectif, et calcule la fidélité approchée de la réponse dans les sources que `repondre` a préparées.

**Le rapport et la barrière.** `rapport` agrège : nombre de cas, succès, intervalle de Wilson, moyennes de la F1 et de la fidélité. `barriere_ci` compare aux seuils (borne basse 0,80, F1 et fidélité 0,95) et rend le couple (code, motifs), que l'on range dans le rapport. La barrière ne quitte jamais le programme : c'est le script d'intégration continue qui appellera `sys.exit(rap["code"])`, comme une étape de pipeline qui échoue sur un code non nul.

## L'évaluation complète

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`evaluation_complete()`** — Cette fonction est la cérémonie de clôture où les deux versions passent devant le même jury, sur les mêmes épreuves, et où l'on affiche les deux bulletins côte à côte. Elle ne reçoit rien ; elle joue une fois chacun des trois scénarios, note chacun avec ses propres appels attendus et son propre but, puis appelle `evaluer_version` pour la production et pour la candidate sur ces mêmes notes communes. Elle rend `{"communes", "production", "candidate"}` : la production obtient 18 sur 18, une borne basse de 0,824 et le code 0, tandis que la candidate obtient 14 sur 18, une Tool Call F1 de 0,926, une fidélité de 0,889 et le code 1, avec trois motifs.

```python
# [extrait] agent/assemblage.py
def evaluation_complete() -> dict:
    """Les 18 cas de référence de 77 : {"communes": 3 notes, "production": rapport, "candidate": rapport}.

    Exemple : production 18/18, code 0 ; candidate 14/18, Tool F1 0,926, fidélité 0,889, code 1 (3 motifs).
    """
    communes = []
    for s in (scenario_credit(), scenario_reglementation(), scenario_virement()):
        communes.append(noter(s["res"], s["res"]["sources"], s["attendus"], s["but"]))
    return {"communes": communes, "production": evaluer_version(False, communes),
            "candidate": evaluer_version(True, communes)}
```

**Les notes communes.** Les trois scénarios sont joués une fois et notés avec leurs propres appels attendus et leur propre objectif. C'est ici que la forme commune des scénarios, le dictionnaire `{"agent", "res", "attendus", "but"}`, paie : une seule ligne note n'importe lequel des trois.

**Deux versions, les mêmes cas.** La production et la candidate sont évaluées sur les mêmes notes communes et sur les mêmes quinze variantes ; seule change la valeur de `candidat`. Comparer deux versions sur des cas différents ne prouverait rien.

**Ce que donnent les nombres.** La production réussit les 18 cas : borne basse de Wilson 18 / (18 + 1,96²) = 18 / 21,8416 = 0,824 ≥ 0,80, F1 et fidélité à 1, code 0. La candidate manque les variantes 1, 5, 9 et 13 : 14 succès, borne basse 0,548. Dans ces quatre cas, sa F1 vaut 2 × 1 / (2 + 1) = 2/3, puisqu'elle fait un appel sur les deux attendus, et sa fidélité 1/2, puisque sa réponse cite la mensualité (présente dans les sources) et 35 % (présent nulle part). D'où une F1 moyenne de (14 + 4 × 2/3) / 18 = 0,926 et une fidélité moyenne de (14 + 4 × 0,5) / 18 = 0,889 : trois seuils violés, trois motifs, code 1.

```text
# [extrait] console
>>> from agent.assemblage import evaluation_complete
>>> ev = evaluation_complete()
>>> [(v, ev[v]["succes"], round(ev[v]["wilson"][0], 3), ev[v]["code"]) for v in ("production", "candidate")]
[('production', 18, 0.824, 0), ('candidate', 14, 0.548, 1)]
>>> ev["candidate"]["motifs"]
['borne basse de Wilson 0.548 < 0.8', 'Tool Call F1 0.926 < 0.95', 'fidélité approchée 0.889 < 0.95']
```

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_12_assemblage.TestDemandeCredit tests.test_12_assemblage.TestBarriereCI
```

Les six tests passent : la variante 1, les verdicts des quinze variantes, la candidate qui oublie le ratio, les trois scénarios parfaits qui ne franchissent pourtant pas la barrière (code 1), la production déployable (18 sur 18, code 0) et la candidate bloquée (14 sur 18, trois motifs).
