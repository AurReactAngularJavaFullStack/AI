# Étape 8 — Assembler, lancer et récapituler les douze paliers

> Palier 12 · Étape 8 sur 8 · Précédent : [Étape 7 — Passer au vrai LLM](<07-Passer-au-vrai-LLM.md>) · Énoncé : [README du palier 12](<../../README.md>) · Sommaire : [Les douze paliers](<../../../README.md>) · Agent de référence : [Étape 77 — Projet final](<../../../../13-Projet-Final/77-Projet-Final-Agent-From-Scratch.md>)

## Comment raisonner : relire l'assemblage d'un seul coup d'œil

Le fichier est complet. Relis sa structure de haut en bas avant de lancer les tests : c'est l'ordre dans lequel tu le réécriras de tête.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Agent.__init__(llm, memoire, session, horloge)`** — Le constructeur, écrit à l'étape 2, est le chef de chantier qui monte toutes les pièces dans l'ordre de leurs dépendances. Il reçoit le port LLM et, facultativement, une mémoire, une session et une horloge ; il copie la session ou `SESSION_CLIENT` avec un nouvel ensemble de portées, copie la mémoire, prend l'horloge reçue ou une horloge au jour 90, puis crée le journal, l'approbateur et la liste des virements. Il remplit un registre neuf avec la recherche, les cinq calculs et le virement, l'enveloppe par `proteger` et calcule les définitions strictes ; il ne rend rien et ne fait aucun travail métier, et chaque agent obtient ainsi son propre monde de sept outils.

**`Agent.repondre(question, documents, k_memoire, max_etapes)`** — Cette méthode de l'étape 3 est la consultation complète au guichet, du rappel des fiches au registre final. Elle reçoit la question, des documents facultatifs, le nombre de souvenirs à garder, 2, et la borne de 8 étapes ; elle rappelle la mémoire si elle existe, construit le prompt qui encadre les documents, journalise le message masqué, lance `executer_agent` avec les outils protégés et journalise chaque ligne de trace. Elle rend le résultat de la boucle enrichi de `rappel` et de `sources` : dans la démonstration, le scénario (a) rappelle le salaire à 0,9769 et le crédit auto à 0,8070.

**`construire_agent(script, memoire, session)`** — Cette fabrique de l'étape 4 est la loge où l'on donne à l'agent un partenaire de scène qui récite son texte. Elle reçoit le script du faux modèle et, facultativement, une mémoire et une session, et rend `Agent(FakeLLM(script), memoire=memoire, session=session)`. C'est la seule ligne qu'il faudrait changer pour passer au vrai modèle ; les trois scénarios et les quinze variantes de l'évaluation passent tous par elle pour obtenir un agent neuf, isolé de tous les autres.

**`sortie_outil(res, nom)`** — Cet utilitaire de l'étape 4 est le greffier qui retrouve, dans le procès-verbal, la première intervention d'un témoin précis. Il reçoit le résultat d'une exécution et un nom d'outil, parcourt les triplets de la trace et rend la sortie du premier appel portant ce nom, ou `None` s'il n'y en a aucun. Il ne dépend d'aucun indice fixe, si bien qu'un modèle qui change l'ordre de ses appels ne le trompe pas ; le scénario du crédit s'en sert pour lire `{'ratio': 0.289, 'recevable': True}`.

**`memoire_client()`** — Cet utilitaire de l'étape 4 tire du classeur quatre fiches neuves sur le client, à chaque rendez-vous. Il ne reçoit rien et rend quatre souvenirs : le salaire de 40 000 AED, le crédit auto de 6 000 AED, le prêt personnel sur 48 mois et la question sur le taux de change, avec leurs jours d'accès 85, 60, 0 et 88 et leurs importances 9, 8, 4 et 2. Comme le rappel remet à neuf les souvenirs relus, des objets neufs à chaque appel évitent qu'un test hérite de l'état d'un autre.

**`scenario_credit()`** — Ce scénario de l'étape 4 rejoue l'hypothèque comme une répétition dont chaque réplique est connue. Il ne reçoit rien ; il écrit un script où le modèle demande la mensualité, puis le ratio et la conversion dans une même réponse, puis conclut, fait répondre un agent doté de `memoire_client()` à `QUESTION_CREDIT` et juge l'objectif sur le statut, la conclusion « dossier recevable. » et la sortie réelle du ratio. Il rend `{"agent", "res", "attendus", "but"}` : dans la démonstration, 5 558,32 AED, 0,289 et 1 513,50 USD, statut « fini » en 3 étapes.

**`scenario_reglementation()`** — Ce scénario de l'étape 5 interroge un clerc juridique et vérifie qu'il ne cite que ce qu'il a reçu. Il ne reçoit rien ; il écrit un script avec un appel à `rechercher_reglementation` puis une réponse qui cite [REG-1] et [REG-2], fait répondre un agent sans mémoire et déclare l'objectif atteint si la boucle a fini, si toutes les citations figurent parmi les documents rendus et si les deux règles sont citées. Il rend le même dictionnaire à quatre clés ; la démonstration affiche les documents rendus `['REG-1', 'REG-2', 'FORUM-9']`.

**`scenario_virement()`** — Ce scénario de l'étape 5 est l'exercice d'alerte où le modèle est dupé exprès, pour prouver que la porte blindée tient sans lui. Il ne reçoit rien ; il écrit un script où le modèle appelle `initier_virement` avec les données du courriel piégé, puis rend compte de l'échec, fait répondre l'agent avec le courriel passé comme document, et juge l'objectif atteint si la boucle a fini, si aucun virement n'est exécuté et si le journal note « refus par délai ». Il rend le dictionnaire à quatre clés ; la démonstration montre R = 0,70, une horloge avancée de 120 s et un journal de 5 entrées intact.

**`demande_credit(i, candidat)`** — Cette fabrique de l'étape 6 imprime le sujet numéro i d'un concours, son corrigé et la copie d'un candidat donné. Elle reçoit i, de 1 à 15, et le choix de version, calcule principal, revenu et mensualités en cours, puis la mensualité et le ratio avec les fonctions des outils et le verdict au seuil de 0,50, et écrit le script : la candidate, quand i vaut 1 modulo 4, invente « endettement estimé à 35 % » sans appeler le ratio. Elle rend le quadruplet (script, question, appels attendus, verdict), les variantes 1 à 7 étant recevables et les variantes 8 à 15 non.

**`evaluer_version(candidat, communes)`** — Cette fonction de l'étape 6 fait passer à une version l'examen complet sur dix-huit copies. Elle reçoit le choix de version et les trois notes communes, en fait une copie, y ajoute pour chacune des quinze variantes la note d'un agent neuf, l'objectif exigeant un appel réel au ratio, puis agrège avec `rapport` et range le code et les motifs de `barriere_ci`. Elle rend ce rapport : dans la démonstration, la production obtient 18/18 et le code 0, la candidate 14/18, Wilson [0,548 ; 0,910] et le code 1.

**`evaluation_complete()`** — Cette fonction de l'étape 6 est la séance plénière où les deux versions passent devant le même jury. Elle ne reçoit rien, joue et note les trois scénarios, puis appelle `evaluer_version` pour la production et pour la candidate sur ces mêmes notes communes, et rend `{"communes", "production", "candidate"}`. La dernière ligne de la démonstration rappelle pourquoi les quinze variantes sont nécessaires : les trois scénarios seuls, pourtant parfaits, n'atteignent qu'une borne basse de 0,438 et reçoivent le code 1.

```python
# [extrait] agent/assemblage.py
JOUR_COURANT = 90.0                            # jour 90 de la relation avec le client
...
class Agent:
    ...
    def __init__(self, llm, memoire: list[Souvenir] | None = None, session: dict | None = None,
                 horloge: Horloge | None = None) -> None:
        ...
    def repondre(self, question: str, documents: list[tuple[str, str]] = (), k_memoire: int = 2,
                 max_etapes: int = 8) -> dict:
        ...
def construire_agent(script: list[Reponse], memoire: list[Souvenir] | None = None, session: dict | None = None) -> Agent:
    ...
def sortie_outil(res: dict, nom: str):
    ...
def memoire_client() -> list[Souvenir]:
    ...
def scenario_credit() -> dict:
    ...
def scenario_reglementation() -> dict:
    ...
def scenario_virement() -> dict:
    ...
def demande_credit(i: int, candidat: bool = False) -> tuple[list, str, list, str]:
    ...
def evaluer_version(candidat: bool, communes: list[dict]) -> dict:
    ...
def evaluation_complete() -> dict:
    ...
```

Trois couches se lisent dans cet ordre. **Le câblage** : `Agent`, dont le constructeur fabrique et relie les objets des paliers 01 à 10, et dont `repondre` fait passer une question à travers eux. **Les scénarios** : trois fonctions qui fixent le comportement du modèle par un script et vérifient un objectif métier, avec trois utilitaires partagés. **L'évaluation** : quinze variantes, deux versions, et la barrière qui décide du déploiement. Aucune de ces fonctions ne recalcule une formule : chacune appelle celle du palier qui la porte.

## Lancer tous les tests

Depuis `projet/` (ou depuis `solutions/` pour voir la solution passer) :

```text
python -m unittest
```

La dernière ligne doit être `OK`, après `Ran 165 tests` : les 150 tests des paliers 01 à 11, que tu n'as pas touchés, et les 15 tests du palier 12. Tout tourne en moins d'une seconde, sans réseau et sans clé : le faux modèle répond toujours la même chose dans le même ordre.

## Lancer la démo

```text
python demo.py
```

```text
Palier 12 — l'assistant de la banque B-1 (Dubaï), assemblé
(a) hypothèque : mémoire rappelée Salaire mensuel déclaré au dossier de crédit : 40 000 AED (0.9769) | Crédit auto en cours : mensualité de 6 000 AED (0.8070)
    outil mensualite({"principal": 1000000, "taux_annuel": 0.045, "n_mois": 300}) -> {'mensualite_aed': 5558.32}
    outil ratio_endettement({"existantes": 6000, "nouvelle": 5558.32, "revenu": 40000}) -> {'ratio': 0.289, 'recevable': True}
    outil convertir_aed_usd({"montant_aed": 5558.32}) -> {'montant_usd': 1513.5}
    [fini, 3 étapes] Mensualité 5 558,32 AED, soit 1 513,50 USD ; endettement total 28,9 % ≤ 50 % : dossier recevable.
    fiabilité de la chaîne, 6 étapes à 0.98 : 0.8858
(b) réglementation : documents rendus ['REG-1', 'REG-2', 'FORUM-9'] ; [fini] Pour un retraité, le total des mensualités ne dépasse pas 30…
(c) virement piégé : ERREUR refusé par l'humain : pas de réponse en 120 s : refus par défaut
    horloge +120 s ; virements exécutés : 0 ; journal de 5 entrées, chaîne intacte : True
    risque virement [IBAN ••••3456] de 180000 AED : R = 0.70, veto, décision revue
Évaluation : 18 cas de référence (3 scénarios + 15 variantes du dossier de crédit)
  production : 18/18   Wilson [0.824 ; 1.000]   Tool F1 1.000   fidélité 1.000   → barrière CI : code 0
  candidate  : 14/18   Wilson [0.548 ; 0.910]   Tool F1 0.926   fidélité 0.889   → barrière CI : code 1
    - borne basse de Wilson 0.548 < 0.8
    - Tool Call F1 0.926 < 0.95
    - fidélité approchée 0.889 < 0.95
  les 3 scénarios seuls : 3/3, Wilson basse 0.438 → code 1
OK — palier 12 terminé.
```

Chaque ligne se relit avec ce que tu as codé.

- **(a) hypothèque.** La mémoire rappelée : le salaire à 0,9769 et le crédit auto à 0,8070, les deux souvenirs gardés par `rappeler` avec k = 2. Puis les trois lignes de trace, dans l'ordre du script : la mensualité de 5 558,32 AED, le ratio de 0,289 jugé recevable, la conversion en 1 513,50 USD. Puis le statut « fini » en 3 étapes et la réponse exacte du test. La fiabilité 0,8858 est 0,98⁶ : trois appels au modèle et trois outils, chacun réussi à 98 %.
- **(b) réglementation.** La recherche rend REG-1, REG-2 et FORUM-9, dans l'ordre de la fusion RRF ; la réponse, tronquée à soixante caractères par la démo, cite les deux règles.
- **(c) virement piégé.** La ligne de trace porte le refus de l'humain : l'outil a levé `ErreurOutil`, et la boucle l'a renvoyé au modèle. L'horloge a avancé de 120 s, aucun virement n'est exécuté, le journal compte cinq entrées et sa chaîne SHA-256 est intacte. La troisième entrée du journal montre le score de risque, 0,70, et la décision « revue », avec l'IBAN masqué.
- **Évaluation.** La production : 18 sur 18, Wilson [0,824 ; 1,000], F1 et fidélité à 1, code 0. La candidate : 14 sur 18, Wilson [0,548 ; 0,910], F1 0,926, fidélité 0,889, code 1, avec ses trois motifs. Et les trois scénarios seuls : borne basse 0,438, code 1.

## Les deux branchements bonus

L'énoncé propose de brancher les deux modules que l'`Agent` n'utilise pas. Voici une solution pour chacun ; elles sont marquées « brouillon » parce qu'elles ne font pas partie du paquet ni des tests, mais elles ont été exécutées avec la solution du palier.

**La planification (palier 08).** Le plan du dossier de crédit se découpe en vagues de tâches indépendantes :

```python
# [extrait] brouillon
from agent.planification import chemin_critique, dossier_credit, vagues

for k, vague in enumerate(vagues(dossier_credit()), start=1):
    print(k, vague)
print(chemin_critique(dossier_credit()))
```

```text
1 ['lire_memoire', 'rechercher_regles', 'verifier_identite']
2 ['calculer_mensualite']
3 ['calculer_ratio', 'convertir_usd']
4 ['evaluer_risque']
5 ['rediger_reponse']
(5.7, ['rechercher_regles', 'evaluer_risque', 'rediger_reponse'])
```

La troisième vague, `calculer_ratio` et `convertir_usd`, est exactement la deuxième réponse du script du scénario (a), qui demande les deux outils dans le même message : le modèle scripté suit déjà le plan. Un agent Plan-and-Execute (étape 13 du cours) calculerait ces vagues d'abord, puis enverrait un message par vague, cinq au lieu de huit en séquentiel ; le chemin critique donne la durée minimale, 5,7 s contre 9,5 s si l'on enchaînait les huit tâches. On ne câble pas ce plan dans `Agent` parce que la boucle ReAct décide ses étapes une à une, au vu des résultats : un plan fixé d'avance se brancherait comme une **autre** stratégie de boucle, sur le même port et les mêmes outils protégés.

**La production (palier 11).** Elle se branche autour du port, comme un décorateur, sans toucher à `Agent` :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`LLMEnProduction.__init__(llm, seau, tokens_par_appel)`** — Le constructeur installe un portier devant la salle où travaille le modèle, avec un compteur de passages et un carnet de dépenses. Il reçoit le port à envelopper, `FakeLLM` ou `ClaudeLLM`, un `SeauAJetons` du palier 11 et le nombre de jetons qu'un appel est censé consommer, 3 000 par défaut ; il range ces trois objets dans l'instance et ouvre la liste vide `couts_aed`, où s'accumulera le coût de chaque appel facturé. Il ne rend rien et n'appelle encore personne : il prépare un objet qui aura la même méthode `create` que le port qu'il enveloppe.

**`LLMEnProduction._appel(requete)`** — Cette méthode interne est le portier qui consulte son compteur avant de laisser entrer chaque visiteur. Elle reçoit les arguments nommés de la requête, demande au seau `tokens_par_appel` jetons et, s'il refuse, lève `ErreurTransitoire("429 : débit dépassé")`, comme le ferait un fournisseur saturé ; sinon elle transmet la requête intacte au port enveloppé et rend sa réponse. C'est cette fonction, et non le port lui-même, que `create` confie au mécanisme de relances, pour qu'un refus du seau soit traité exactement comme une limite de débit.

**`LLMEnProduction.create(system, messages, tools)`** — Cette méthode est le guichet décoré, identique vu de la boucle à celui du port enveloppé, mais doublé d'un service d'attente et d'une caisse. Elle reçoit par mots-clés le système, les messages et les outils, appelle `executer_avec_relances` sur `_appel` avec une base de 20 s, un plafond de 60 s, sans gigue et sur l'horloge du seau, et lève `RuntimeError` si toutes les tentatives échouent. Sinon elle lit l'éventuel champ `usage` de la réponse, absent chez le faux modèle, ajoute à `couts_aed` le coût calculé par `cout_tache`, puis rend la réponse : sur le scénario (a) avec un seau de 6 000 jetons, la démonstration finit en 3 étapes avec 60 secondes simulées de plus.

```python
# [extrait] brouillon
from agent.production import ErreurTransitoire, SeauAJetons, cout_tache, executer_avec_relances


class LLMEnProduction:
    """Même port que FakeLLM et ClaudeLLM : débit, relances et coût autour de n'importe quel modèle."""

    def __init__(self, llm, seau: SeauAJetons, tokens_par_appel: int = 3_000) -> None:
        self.llm, self.seau, self.tokens_par_appel = llm, seau, tokens_par_appel
        self.couts_aed: list[float] = []

    def _appel(self, **requete):
        if not self.seau.consommer(self.tokens_par_appel):
            raise ErreurTransitoire("429 : débit dépassé")
        return self.llm.create(**requete)

    def create(self, *, system: str, messages: list, tools: list):
        r = executer_avec_relances(lambda: self._appel(system=system, messages=messages, tools=tools),
                                   base_s=20, plafond_s=60, gigue=0, horloge=self.seau.horloge)
        if r["statut"] == "echec":
            raise RuntimeError(f"modèle indisponible après {r['tentatives']} tentatives")
        reponse = r["resultat"]
        usage = getattr(reponse, "usage", None)          # FakeLLM n'en a pas ; l'API Claude, si
        if usage is not None:
            self.couts_aed.append(cout_tache(usage.input_tokens, usage.output_tokens,
                                             usage.cache_read_input_tokens or 0,
                                             usage.cache_creation_input_tokens or 0)["aed"])
        return reponse
```

**Le principe** est celui du patron décorateur, ou d'un proxy Spring AOP : `LLMEnProduction` a la même méthode `create` que le port qu'il enveloppe, donc l'`Agent` l'accepte sans le savoir. **Avant l'appel**, `_appel` demande 3 000 jetons au seau du palier 11 ; un refus devient une `ErreurTransitoire`, comme une réponse 429 du fournisseur. **L'appel** passe par `executer_avec_relances`, sur l'horloge du seau, sans gigue pour que le résultat soit reproductible ; un échec définitif lève une erreur, que l'appelant verra remonter de `repondre`. **Après l'appel**, si la réponse porte un `usage` (c'est le cas des réponses de l'API, pas du faux modèle), on calcule le coût de l'appel avec `cout_tache` : les tokens d'entrée hors cache, de sortie, lus et écrits dans le cache, exactement les quatre termes de la formule du palier 11.

Pour l'essayer sur le scénario (a), l'agent et le seau doivent partager **la même horloge** :

```python
# [extrait] brouillon
from agent.assemblage import A_CONVERSION, A_MENSUALITE, A_RATIO, QUESTION_CREDIT, Agent, memoire_client
from agent.modele import FakeLLM, Horloge, Reponse, appel_outil, texte

script = [Reponse("tool_use", [appel_outil("mensualite", A_MENSUALITE, "a1")]),
          Reponse("tool_use", [appel_outil("ratio_endettement", A_RATIO, "a2"),
                               appel_outil("convertir_aed_usd", A_CONVERSION, "a3")]),
          Reponse("end_turn", [texte("Fini.")])]
h = Horloge(90 * 86_400)
seau = SeauAJetons(6_000, 50, h)
agent = Agent(LLMEnProduction(FakeLLM(script), seau), memoire=memoire_client(), horloge=h)
res = agent.repondre(QUESTION_CREDIT)
print(res["statut"], res["etapes"], h.t - 90 * 86_400)
```

La dernière ligne affiche `fini 3 60.0`. Les deux premiers appels vident le seau de 6 000 jetons. Le troisième est refusé : on attend 20 s, le seau remonte à 1 000 jetons, encore trop peu ; on attend 40 s, il atteint 3 000, et l'appel passe. Le scénario finit toujours en trois étapes, avec 60 secondes simulées de plus, et les entrées du journal qui suivent sont datées en conséquence. Avec `ClaudeLLM()` à la place de `FakeLLM(script)`, la liste `couts_aed` se remplit, et `budget_restant` peut la comparer au budget du jour. Pour le p95, on mesurerait en plus la durée réelle de chaque appel et l'on passerait la liste à `p95`.

## Ce que tu sais maintenant coder depuis une feuille blanche

Tu as écrit, palier par palier, chaque ligne de l'agent de l'étape 77, et tu sais la réécrire sans modèle sous les yeux.

1. **Modèle et prompt.** Un port LLM scripté (`FakeLLM`) qui a la forme exacte des réponses de l'API, une horloge simulée, et un prompt qui sépare les règles de l'équipe des documents non fiables, encadrés et neutralisés.
2. **Schémas et validation.** Un validateur de schéma JSON écrit à la main, qui rend des erreurs avec leur chemin, et la préparation des schémas pour le mode strict de l'API.
3. **Outils métier des Émirats.** La mensualité, le ratio d'endettement de la CBUAE, la conversion à 3,6725, la fin de service, la TVA de 5 %, l'IBAN AE et le format de l'Emirates ID, testés au centime.
4. **Registre d'outils.** Un registre, un décorateur d'enregistrement, une porte qui valide avant d'exécuter, et une enveloppe qui renvoie toute erreur au modèle au lieu de l'avaler.
5. **Boucle d'agent.** La boucle ReAct et ses cinq arrêts, dont la borne qui arrête n'importe quel modèle, même adversaire.
6. **Mémoire.** Le cosinus, la récence exponentielle, le min-max et le score de pertinence pondéré qui choisit les souvenirs utiles.
7. **Recherche hybride.** BM25, un plongement, le cosinus et la fusion RRF, avec des citations que l'on peut vérifier.
8. **Planification.** Un plan en graphe sans cycle, le tri topologique de Kahn, les vagues parallèles et le chemin critique.
9. **Garde-fous.** Le refus par défaut, le masquage des données personnelles, le score de risque, le veto, l'approbation humaine dans l'outil, et un journal chaîné qui détecte une falsification.
10. **Évaluation.** La Tool Call F1, la Goal Accuracy et son intervalle de Wilson, la fidélité approchée, et une barrière d'intégration continue qui sait bloquer une version moins bonne.
11. **Production.** Le coût d'une tâche en USD et en AED avec le cache, un seau à jetons, des relances exponentielles avec gigue, le p95 et le budget du jour.
12. **Assemblage.** Un agent câblé par injection de dépendances, sans variable globale, trois scénarios de bout en bout, une évaluation sur dix-huit cas, et un adaptateur qui remplace le faux modèle par Claude en changeant une seule ligne.

Pour vérifier que tout est acquis, fais l'exercice feuille blanche de l'étape 77 : refaire l'agent de tête, en 60 minutes, dans un éditeur vide, avec la seule bibliothèque standard, chaque tranche se terminant par un test qui doit passer. Puis efface `agent/assemblage.py` de ce palier et récris-le sans regarder : le palier est acquis quand les 165 tests passent du premier coup.

Retour au sommaire : [Les douze paliers](<../../../README.md>) · Agent de référence : [Étape 77 — Projet final](<../../../../13-Projet-Final/77-Projet-Final-Agent-From-Scratch.md>).
