# Palier 12 — Assemblage de l'agent complet

> Palier 12 sur 12 · Précédent : [Palier 11 — Production et coûts](<../11-Production-et-Couts/README.md>) · Sommaire : [Les douze paliers](<../README.md>) · Leçons à relire : [Étape 77 — Projet final, un agent complet depuis une feuille blanche](<../../13-Projet-Final/77-Projet-Final-Agent-From-Scratch.md>) · [Étape 13 — Six agents EAU de bout en bout, l'adaptateur Claude](<../../03-Schemas-Outils-et-Premiere-Evaluation/13-Agent-Exemples-Cas-Usage.md>) · [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>) · [Étape 65 — La barrière d'intégration continue](<../../10-Evaluation/65-Evaluation-Exemples-Cas-Usage.md>) · Démonstrations : [29 — Fiabilité en série](<../../Demonstrations/01-Introduction/29_fiabilite_serie.md>)

C'est le dernier palier : tu assembles l'agent de l'étape 77 à partir des onze modules que tu as écrits. L'agent est l'assistant de la banque B-1, une banque de détail de Dubaï. Il rejoue les trois demandes de l'étape 77 avec les mêmes nombres : une hypothèque de 1 000 000 AED dont la mensualité vaut 5 558,32 AED et le ratio d'endettement 0,289, une question réglementaire qui cite deux règles, et un virement de 180 000 AED demandé par un courriel piégé, que le code refuse même quand le modèle est convaincu. Puis il s'évalue sur dix-huit cas et laisse la barrière d'intégration continue décider : la version de production passe (18 sur 18, code 0), la version candidate est bloquée (14 sur 18, code 1).

Tout tourne hors ligne, sur le faux modèle scripté. La fin de l'énoncé montre comment brancher le vrai modèle, Claude, à la place du faux, en changeant une seule ligne.

## Où en est l'agent

Les onze modules sont écrits et testés. Ce palier écrit `agent/assemblage.py`, qui ne contient presque aucun calcul : il **câble** des objets. C'est la racine de composition de l'application, le rôle que joue en Spring une classe `@Configuration` dont les méthodes `@Bean` fabriquent les services et leur injectent leurs dépendances. Le fichier `agent/adaptateur_claude.py`, fourni complet, est le second adaptateur du port LLM.

```text
              question du client C-1                 documents non fiables (courriel)
                        │                                        │
 ╔══════════════════════▼════════════════════════════════════════▼══════════════════╗
 ║ 12 ASSEMBLAGE (ce palier) : class Agent                                          ║
 ║   repondre : 06 rappeler ──► 01 construire_prompt ──► 05 executer_agent          ║
 ║                                                        │          ▲              ║
 ║   outils   : 09 proteger(04 Registre) : politique ──► 02 schéma ──► outil        ║
 ║   registre : 07 rechercher_reglementation ; 03 mensualite, ratio_endettement,    ║
 ║              convertir_aed_usd, gratuite_fin_de_service, tva ;                   ║
 ║              09 initier_virement (risque, veto, approbation humaine)             ║
 ║   état     : 01 Horloge ; 09 JournalAudit (masqué, chaîné) ; 09 Approbateur      ║
 ╚══════════════════════════════════════╤═══════════════════════════════════════════╝
                                        │ port LLM : create(system, messages, tools)
                 ┌──────────────────────┴──────────────────────┐
      01 FakeLLM (tests, scripts)              ClaudeLLM (adaptateur_claude.py)

   10 évaluation : evaluation_complete, 18 cas → barrière CI (code 0 ou 1)
   08 planification et 11 production : outils à part, non câblés (défis bonus)
```

L'`Agent` **est** la boucle percevoir → décider → agir → observer, montée sur ses pièces. Percevoir : `rappeler` choisit les souvenirs utiles et `construire_prompt` place les règles et la mémoire dans le système, les documents non fiables dans le message, encadrés. Décider : `executer_agent` interroge le port LLM. Agir : chaque outil passe par `proteger`, qui vérifie la politique puis le schéma avant d'exécuter. Observer : chaque résultat repart vers le modèle, et chaque ligne de trace est écrite, masquée, dans le journal chaîné.

### Ce qui change par rapport à l'étape 77

L'étape 77 tient dans un seul fichier, avec des variables globales et des `assert` dans `main()`. La série d'exercices garde les mêmes noms, les mêmes formules et les mêmes nombres, mais en change l'architecture sur cinq points.

1. **Plus de variables globales.** `HORLOGE`, `JOURNAL`, `SESSION`, `APPROBATEUR`, `VIREMENTS` et `REGISTRE` deviennent des attributs de chaque `Agent`, qui reçoit le modèle, la mémoire, la session et l'horloge par son constructeur. Chaque test fabrique un agent neuf : plus besoin de `SESSION.update(...)` suivi d'une restauration, ni de `VIREMENTS.clear()`.
2. **Le `Registre` du palier 04** remplace le dictionnaire global et le décorateur global `outil` : `enregistrer_recherche`, `enregistrer_outils_metier` et `enregistrer_virement` remplissent le registre de l'agent, dans l'ordre de 77.
3. **La politique est vérifiée par `proteger`** (palier 09), qui enveloppe la porte du registre : politique, puis schéma, puis outil. Dans 77, une seule fonction `porte(nom)` faisait les deux contrôles ; ici, chacun vit dans son palier, et l'on compose.
4. **`indexer()` remplace la constante `INDEX`** (palier 07) : l'index des mots est recalculé à partir du corpus, et l'on peut passer un autre corpus.
5. **Les scénarios de `main()` deviennent des fonctions** qui rendent leurs résultats : `scenario_credit`, `scenario_reglementation`, `scenario_virement` et `evaluation_complete`. Les `assert` deviennent des tests `unittest`, et `lancer` devient la méthode `Agent.repondre`.

Le journal d'audit est en plus chaîné par SHA-256 (palier 09), et le palier 11 est entièrement nouveau par rapport à 77.

## Ce que tu vas coder

Dans `projet/agent/assemblage.py` (les constantes sont déjà écrites) :

- `Agent.__init__` câble l'horloge, le journal, l'approbateur, le registre de sept outils, les outils protégés et les définitions envoyées au modèle.
- `Agent.repondre` enchaîne rappel de mémoire, prompt, boucle et journal, et rend le résultat enrichi du rappel et des sources.
- `construire_agent` fabrique un agent branché sur un `FakeLLM` qui rejoue un script.
- `sortie_outil` lit dans la trace la sortie du premier appel à un outil donné.
- `memoire_client` rend les quatre souvenirs du scénario (a), neufs à chaque appel.
- `scenario_credit`, `scenario_reglementation` et `scenario_virement` rejouent les trois demandes de 77 et disent si leur objectif est atteint.
- `demande_credit` fabrique la variante i du dossier de crédit, en version production ou candidate.
- `evaluer_version` évalue une version sur les dix-huit cas et applique la barrière CI ; `evaluation_complete` évalue les deux versions.

`agent/adaptateur_claude.py` contient `ClaudeLLM`, fourni complet : il n'est jamais exécuté par les tests.

## Rappel de cours

L'assemblage ne crée pas de formule : il fait travailler ensemble celles des paliers précédents. Voici celles qui produisent les nombres des scénarios.

**La mensualité et le ratio d'endettement (palier 03).** Pour un prêt de principal P sur n mois au taux mensuel r :

$$
M = \frac{P\,r}{1 - (1 + r)^{-n}} \qquad r = \frac{\text{taux annuel}}{12}
$$

$$
\rho = \frac{E + M}{V} \le 0{,}50
$$

**Le score d'un souvenir (palier 06).** Chaque composante est d'abord ramenée dans [0 ; 1] par min-max sur les quatre souvenirs :

$$
S = 0{,}5\,\text{sim} + 0{,}3\,\text{rec} + 0{,}2\,\text{imp}
$$

**Le score de risque du virement (palier 09) :**

$$
R = w_s\,s + w_g\,g + w_u\,u = 0{,}4 \times 0{,}7 + 0{,}4 \times 1 + 0{,}2 \times 0{,}1 = 0{,}70
$$

**La fiabilité d'une chaîne d'étapes (étape 1).** Si chaque étape réussit indépendamment des autres avec la probabilité pᵢ :

$$
P(\text{succès}) = \prod_{i=1}^{m} p_i
$$

**La borne basse de Wilson quand tous les cas réussissent (palier 10).** Avec N cas réussis sur N et z = 1,96 :

$$
\text{borne basse}(N \text{ sur } N) = \frac{N}{N + z^2}
$$

**La Tool Call F1 et la fidélité approchée (palier 10)**, moyennées sur les cas :

$$
F_1 = \frac{2\,|A \cap T|}{|A| + |T|} \qquad \varphi = \frac{\text{nombres de la réponse retrouvés dans les sources}}{\text{nombres de la réponse}}
$$

### Les symboles, un par un

$$
M
$$

Mensualité du nouveau prêt, en AED ; sortie `mensualite_aed` de l'outil `mensualite`.

$$
P
$$

Principal emprunté, en AED : 1 000 000 dans le scénario (a) ; argument `principal`.

$$
r
$$

Taux mensuel, le taux annuel divisé par 12 : 0,045 / 12 = 0,00375.

$$
n
$$

Durée du prêt en mois : 300, soit 25 ans ; argument `n_mois`.

$$
\rho
$$

Ratio d'endettement de la CBUAE : toutes les mensualités, anciennes et nouvelle, divisées par le revenu ; sortie `ratio` de l'outil `ratio_endettement`.

$$
E
$$

Mensualités des crédits déjà en cours, en AED : 6 000 dans le scénario (a) ; argument `existantes`.

$$
V
$$

Revenu mensuel, en AED : 40 000 dans le scénario (a) ; argument `revenu`.

$$
S
$$

Score de pertinence d'un souvenir, dans [0 ; 1] ; premier élément de chaque couple rendu par `rappeler`.

$$
\text{sim}
$$

Similarité cosinus entre la question et le souvenir, après min-max.

$$
\text{rec}
$$

Récence du souvenir, e puissance (−λ × âge) avec une demi-vie de 30 jours, après min-max.

$$
\text{imp}
$$

Importance du souvenir, de 1 à 10, après min-max.

$$
R
$$

Score de risque d'une action, dans [0 ; 1] ; calculé par `score_risque` dans l'outil de virement.

$$
s
$$

Sensibilité des données touchées : 0,7 pour des données personnelles.

$$
g
$$

Gravité de l'action : 1 pour un virement irréversible de 180 000 AED.

$$
u
$$

Incertitude du modèle : 0,1, valeur illustrative.

$$
w_s
$$

Poids de la sensibilité dans le score de risque : 0,4, illustratif.

$$
w_g
$$

Poids de la gravité : 0,4, illustratif.

$$
w_u
$$

Poids de l'incertitude : 0,2, illustratif.

$$
p_i
$$

Probabilité de succès de l'étape i de la chaîne : 0,98 dans l'exemple.

$$
m
$$

Nombre d'étapes de la chaîne : 6 dans le scénario (a), trois appels au modèle et trois outils.

$$
N
$$

Nombre de cas évalués : 18 dans le jeu de référence.

$$
z
$$

Quantile de la loi normale pour un intervalle à 95 % : 1,96, d'où z² = 3,8416.

$$
A
$$

Multi-ensemble des appels d'outils attendus pour un cas, chacun étant un couple (nom, arguments).

$$
T
$$

Multi-ensemble des appels réellement faits, lus dans la trace de la boucle.

$$
\varphi
$$

Fidélité approchée d'une réponse : la part de ses nombres que l'on retrouve dans les sources ; indéfinie (`None`) si la réponse ne cite aucun nombre.

**Les nombres du scénario (a), à la main.** r = 0,045 / 12 = 0,00375, et (1,00375)⁻³⁰⁰ ≈ 0,32533, si bien que :

$$
M = \frac{1\,000\,000 \times 0{,}00375}{1 - 0{,}32533} = \frac{3\,750}{0{,}67467} \approx 5\,558{,}32 \text{ AED}
$$

$$
\rho = \frac{6\,000 + 5\,558{,}32}{40\,000} = \frac{11\,558{,}32}{40\,000} = 0{,}288958 \approx 0{,}289
$$

Le ratio est sous le plafond de 0,50 : dossier recevable. La conversion donne 5 558,32 / 3,6725 = 1 513,4976, arrondi à 1 513,50 USD. Côté mémoire, au jour 90 : le salaire déclaré obtient 0,5 × 1 + 0,3 × 0,9229 + 0,2 × 1 = 0,9769, le crédit auto 0,5 × 1 + 0,3 × 0,4519 + 0,2 × 0,8571 = 0,8070, l'ancien projet de prêt personnel 0,5571 et le taux de change 0,3. Avec k = 2, les deux premiers entrent dans le prompt système.

**Pourquoi demander deux outils dans la même réponse.** Le scénario (a) enchaîne six étapes : trois appels au modèle et trois outils. Avec pᵢ = 0,98 pour chacune, la chaîne réussit avec la probabilité 0,98⁶ = 0,8858. Chaque étape ajoutée multiplie par un facteur au plus égal à 1, donc ne peut que faire baisser ce nombre. Si le modèle demandait le ratio et la conversion dans deux réponses séparées, il y aurait un appel de plus, sept étapes, et 0,98⁷ = 0,8681. C'est pour cela que la deuxième réponse du script contient deux blocs `tool_use`, et que la boucle renvoie leurs deux résultats dans un seul message.

**Pourquoi dix-huit cas, et pas trois.** Avec z² = 3,8416, trois scénarios parfaits donnent une borne basse de 3 / 6,8416 = 0,438 : ils ne prouvent même pas un taux de succès de 50 %. Pour prouver 80 % avec des cas tous réussis, il faut N / (N + z²) ≥ 0,8 :

$$
\frac{N}{N + z^2} \ge 0{,}8 \iff 0{,}2\,N \ge 0{,}8\,z^2 \iff N \ge 4\,z^2 = 15{,}37
$$

soit au moins 16 cas parfaits. Le jeu de référence en compte 18 : 18 / 21,8416 = 0,824 ≥ 0,80, et la production passe.

**Les métriques de la candidate.** La candidate saute le calcul du ratio dans 4 variantes sur 15. Dans ces quatre cas, elle fait 1 appel sur les 2 attendus, donc F1 = 2 × 1 / (2 + 1) = 2/3 ; et sa réponse cite deux nombres, la mensualité (présente dans les sources) et « 35 % » (inventé), donc φ = 1/2. Les 14 autres cas sont parfaits :

$$
F_1 = \frac{14 + 4 \times \frac{2}{3}}{18} \approx 0{,}926 \qquad \varphi = \frac{14 + 4 \times 0{,}5}{18} \approx 0{,}889
$$

Deux métriques sous 0,95, une borne de Wilson sous 0,80 : trois motifs, et la barrière rend 1.

## Spécification

### Les constantes, déjà écrites

```python
# [extrait] spécification
JOUR_COURANT = 90.0                            # jour 90 de la relation avec le client
SESSION_CLIENT = {"role": "client_banque", "portees": {"lecture", "virement:initier"}}   # vient de l'authentification
IBAN_PROMOTEUR = "AE07 0331 2345 6789 0123 456"
A_MENSUALITE = {"principal": 1_000_000, "taux_annuel": 0.045, "n_mois": 300}
A_RATIO = {"existantes": 6_000, "nouvelle": 5558.32, "revenu": 40_000}
A_CONVERSION = {"montant_aed": 5558.32}
REQUETE_RAG = "plafond d'endettement d'un retraité et durée maximale d'un prêt personnel"
A_VIREMENT = {"iban": IBAN_PROMOTEUR, "montant_aed": 180_000, "motif": "Acompte off-plan, lot 214"}
```

Le squelette contient aussi les textes `QUESTION_CREDIT`, `QUESTION_REGLEMENTATION`, `QUESTION_VIREMENT` et `COURRIEL`, recopiés de 77 : ne les modifie pas, les tests et la fidélité approchée lisent leurs nombres. Les montants y sont formatés par `fr` (palier 03), avec une espace fine insécable comme séparateur de milliers.

### Agent (le constructeur)

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Agent.__init__(llm, memoire, session, horloge)`** — Le constructeur doit jouer le chef de chantier qui, avant l'ouverture d'une agence bancaire, fait livrer chaque pièce, la branche à la bonne prise et vérifie qu'aucun fil ne court vers le bureau voisin. Il reçoit le port LLM, une liste de souvenirs, une session et une horloge, ces trois derniers facultatifs ; il doit copier la session, ou `SESSION_CLIENT` par défaut, avec un nouvel ensemble de portées, copier la mémoire, prendre l'horloge reçue ou en créer une au jour 90, soit 7 776 000 s, puis fabriquer un `JournalAudit`, un `Approbateur` et une liste de virements vide. Il remplit ensuite un `Registre` avec la recherche, les cinq outils métier et le virement, enveloppe le tout par `proteger` et range les définitions de `registre.definitions_api()` ; il ne rend rien, mais un agent neuf doit exposer sept outils stricts, de `rechercher_reglementation` à `initier_virement`.

```python
# [extrait] spécification
class Agent:
    def __init__(self, llm, memoire: list[Souvenir] | None = None, session: dict | None = None,
                 horloge: Horloge | None = None) -> None: ...
```

Le constructeur crée, dans cet ordre, les attributs suivants.

- `session` : une **copie** de la session reçue, ou de `SESSION_CLIENT` si elle vaut `None`, avec le rôle et un **nouvel** ensemble de portées. L'agent ne doit jamais modifier la constante ni la session de l'appelant.
- `llm` : le port reçu, `FakeLLM` ou `ClaudeLLM`, sans le regarder.
- `memoire` : une copie de la liste de souvenirs, vide si `None`.
- `horloge` : l'horloge reçue, ou `Horloge(JOUR_COURANT * 86_400)`, soit 7 776 000 s, le jour 90.
- `journal` : un `JournalAudit` sur cette horloge ; `approbateur` : un `Approbateur` sur la même horloge et le même journal ; `virements` : une liste vide, le « cœur bancaire » simulé.
- `registre` : un `Registre` rempli dans l'ordre de 77 par `enregistrer_recherche`, `enregistrer_outils_metier`, puis `enregistrer_virement(registre, approbateur, journal, virements)`.
- `outils` : `proteger(registre, session, journal)`, le dictionnaire nom → appelable protégé ; `schemas` : `registre.definitions_api()`.

**Exemple.** Un agent neuf a 7 outils, dans l'ordre `rechercher_reglementation`, `mensualite`, `ratio_endettement`, `convertir_aed_usd`, `gratuite_fin_de_service`, `tva`, `initier_virement`, tous avec `"strict": True` ; son horloge est au jour 90,0. Tests : `TestScenarioCredit.test_sept_outils_stricts_envoyes_au_modele`, `TestScenariosRagEtVirement.test_agent_accepte_n_importe_quel_port`.

### Agent.repondre

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Agent.repondre(question, documents, k_memoire, max_etapes)`** — Cette méthode doit raconter une consultation complète au guichet : le conseiller relit d'abord les fiches utiles du client, prépare son dossier, discute avec le modèle autant de tours qu'il faut, et consigne chaque geste dans le registre. Elle reçoit la question, une liste facultative de documents `(identifiant, texte)`, le nombre k de souvenirs à rappeler, 2 par défaut, et la borne de la boucle, 8 étapes ; elle doit rappeler les souvenirs si la mémoire n'est pas vide, construire le prompt système et le message, journaliser la question, lancer `executer_agent`, puis journaliser chaque ligne de trace. Elle rend le résultat de la boucle enrichi des clés `rappel` et `sources`, ces dernières formées du système, du message et des sorties d'outils en JSON : dans le scénario (a), les deux souvenirs rappelés ont les scores 0,9769 et 0,8070 et les sources comptent cinq textes.

```python
# [extrait] spécification
class Agent:
    def repondre(self, question: str, documents: list[tuple[str, str]] = (), k_memoire: int = 2,
                 max_etapes: int = 8) -> dict: ...
```

1. Si la mémoire n'est pas vide, `rappel = rappeler(question, self.memoire, plonger_texte, self.horloge.jour(), k=k_memoire)` ; sinon `rappel = []`.
2. `systeme, message = construire_prompt(question, [s.texte for _, s in rappel], list(documents))`.
3. Journaliser `f"question : {message}"`, puis lancer `executer_agent(self.llm, systeme, message, self.outils, self.schemas, max_etapes)`.
4. Pour chaque ligne `(nom, args, sortie)` de la trace, journaliser `f"trace {nom}({json.dumps(args, ensure_ascii=False)}) -> {sortie}"`.
5. Ajouter au résultat `res["rappel"] = rappel` et `res["sources"] = [systeme, message] + [json.dumps(s, ensure_ascii=False) for _, _, s in res["trace"]]`, puis le rendre.

**Exemple chiffré (scénario a).** Le rappel garde deux souvenirs, de scores 0,9769 et 0,8070 (calcul dans le rappel de cours). Le prompt système contient la ligne « - Salaire mensuel déclaré au dossier de crédit : 40 000 AED » et ne contient pas « taux de change ». Après le rappel, les `jour_acces` des quatre souvenirs valent 90, 90, 0 et 88 : les deux souvenirs relus sont remis à neuf. Les sources sont cinq textes : le système, le message, et les trois sorties d'outils en JSON. Avec la session `{"role": "assistant_public", "portees": {"lecture"}}` et sans mémoire, un appel à `mensualite` donne la ligne de trace « ERREUR outil mensualite non autorisé pour le rôle assistant_public » et un rappel vide. Tests : `TestScenarioCredit.test_memoire_rappelee_dans_le_systeme`, `TestScenariosRagEtVirement.test_session_publique_refusee_par_la_politique`.

### construire_agent, sortie_outil et memoire_client

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`construire_agent(script, memoire, session)`** — Cette fonction doit être l'atelier de répétition où l'on donne à l'agent un partenaire de scène qui connaît déjà toutes ses répliques. Elle reçoit le script du faux modèle, une liste de réponses à rejouer, et, facultativement, une mémoire et une session ; elle doit rendre simplement `Agent(FakeLLM(script), memoire=memoire, session=session)`, sans rien ajouter. C'est la seule différence entre un agent de test et un agent réel, qui recevrait `ClaudeLLM()` à la place du faux modèle ; chaque scénario et chaque variante d'évaluation passe par elle pour obtenir un agent neuf.

**`sortie_outil(res, nom)`** — Cette fonction doit se comporter comme un archiviste qui feuillette le procès-verbal d'une séance pour retrouver la première intervention d'un orateur donné. Elle reçoit le résultat d'une exécution et le nom d'un outil, parcourt les triplets `(nom, arguments, sortie)` de `res["trace"]` dans l'ordre, et doit rendre la sortie du premier appel à cet outil, ou `None` s'il n'a jamais été appelé. Dans le scénario (a), `sortie_outil(res, "ratio_endettement")` doit valoir `{"ratio": 0.289, "recevable": True}` et `sortie_outil(res, "tva")` doit valoir `None` ; les scénarios s'en servent pour juger leur objectif.

**`memoire_client()`** — Cette fonction doit sortir du classeur quatre fiches neuves sur le client C-1, comme un photocopieur qui tire un exemplaire vierge pour chaque nouveau rendez-vous. Elle ne reçoit rien et doit rendre une nouvelle liste de quatre souvenirs à chaque appel : le salaire de 40 000 AED vu au jour 85 avec l'importance 9, le crédit auto de 6 000 AED vu au jour 60 avec l'importance 8, le prêt personnel sur 48 mois vu au jour 0 avec l'importance 4, et la question sur le taux de change vue au jour 88 avec l'importance 2. Comme le rappel modifie le jour du dernier accès, rendre des objets neufs à chaque appel empêche un test d'hériter de l'état laissé par un autre.

```python
# [extrait] spécification
def construire_agent(script: list[Reponse], memoire: list[Souvenir] | None = None, session: dict | None = None) -> Agent: ...

def sortie_outil(res: dict, nom: str): ...

def memoire_client() -> list[Souvenir]: ...
```

`construire_agent` rend `Agent(FakeLLM(script), memoire=memoire, session=session)`. `sortie_outil` rend la sortie du **premier** appel à l'outil `nom` dans `res["trace"]`, ou `None` s'il n'a pas été appelé. `memoire_client` rend quatre souvenirs **neufs** à chaque appel (le rappel modifie `jour_acces`, et un test ne doit pas hériter de l'état d'un autre) :

| Texte | Jour du dernier accès | Importance |
| --- | --- | --- |
| `f"Salaire mensuel déclaré au dossier de crédit : {fr(40_000, 0)} AED"` | 85.0 | 9 |
| `f"Crédit auto en cours : mensualité de {fr(6_000, 0)} AED"` | 60.0 | 8 |
| `"Cherchait un prêt personnel sur 48 mois"` | 0.0 | 4 |
| `"A demandé le taux de change du dirham en USD"` | 88.0 | 2 |

**Exemple.** Au jour 90, leurs âges valent 5, 30, 90 et 2 jours. Dans le scénario (a), `sortie_outil(res, "ratio_endettement")` vaut `{"ratio": 0.289, "recevable": True}`, et `sortie_outil(res, "tva")` vaut `None`.

### scenario_credit

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`scenario_credit()`** — Cette fonction doit rejouer la scène de l'hypothèque comme on rejoue un match enregistré, avec les mêmes coups et le même score. Elle ne reçoit rien ; elle doit écrire un script de trois réponses, l'appel à `mensualite`, puis dans une même réponse `ratio_endettement` et `convertir_aed_usd`, puis le texte final, construire un agent doté de `memoire_client()` et le faire répondre à `QUESTION_CREDIT`. L'objectif est atteint si le statut vaut « fini », si la réponse se termine par « dossier recevable. » et si la sortie du ratio est un dictionnaire dont `recevable` vaut `True` ; elle rend `{"agent", "res", "attendus", "but"}`, avec trois étapes et les sorties 5558,32, 0,289 et 1513,5.

```python
# [extrait] spécification
def scenario_credit() -> dict: ...
```

Le script du faux modèle a trois réponses : un appel à `mensualite` avec `A_MENSUALITE` (identifiant "a1") ; puis, **dans la même réponse**, `ratio_endettement` avec `A_RATIO` ("a2") et `convertir_aed_usd` avec `A_CONVERSION` ("a3") ; puis un texte final, `f"Mensualité {fr(5558.32)} AED, soit {fr(1513.5)} USD ; endettement total {fr(28.9, 1)} % ≤ 50 % : dossier recevable."`, coupé sur deux lignes dans le code. L'agent a la mémoire `memoire_client()` et répond à `QUESTION_CREDIT`. L'objectif est atteint si le statut vaut "fini", si la réponse se termine par « dossier recevable. » et si la sortie de `ratio_endettement` est un dictionnaire dont `recevable` vaut `True`. La fonction rend `{"agent", "res", "attendus", "but"}`, où `attendus` est la liste des trois couples (nom, arguments).

**Exemple chiffré.** Statut "fini" en 3 étapes ; sorties `{"mensualite_aed": 5558.32}`, `{"ratio": 0.289, "recevable": True}` et `{"montant_usd": 1513.5}` (calculs dans le rappel de cours) ; réponse « Mensualité 5 558,32 AED, soit 1 513,50 USD ; endettement total 28,9 % ≤ 50 % : dossier recevable. ». Le journal contient une ligne « politique client_banque -> mensualite : autorisé », et sa chaîne SHA-256 est intacte. Tests : `TestScenarioCredit` (cinq tests).

### scenario_reglementation

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`scenario_reglementation()`** — Cette fonction doit mettre en scène un bibliothécaire juridique que l'on interroge sur deux règles, et vérifier qu'il ne cite que les textes qu'il a réellement sortis des rayons. Elle ne reçoit rien ; elle doit écrire un script de deux réponses, l'appel à `rechercher_reglementation` avec `REQUETE_RAG`, puis le texte qui cite [REG-1] et [REG-2], et faire répondre un agent sans mémoire à `QUESTION_REGLEMENTATION`. L'objectif est atteint si le statut vaut « fini », si chaque identifiant cité figure parmi les documents rendus par l'outil et si REG-1 et REG-2 sont tous deux cités ; la recherche doit rendre `["REG-1", "REG-2", "FORUM-9"]`, le forum piégé arrivant au modèle avec ses chevrons neutralisés.

```python
# [extrait] spécification
def scenario_reglementation() -> dict: ...
```

Script : un appel à `rechercher_reglementation` avec `{"question": REQUETE_RAG}` ("b1"), puis le texte « Pour un retraité, le total des mensualités ne dépasse pas 30 % du revenu [REG-1] ; un prêt personnel dure au plus 48 mois [REG-2]. ». Agent sans mémoire, question `QUESTION_REGLEMENTATION`. L'objectif est atteint si le statut vaut "fini", si les identifiants cités (fonction `citations` du palier 07) sont tous parmi les documents rendus par l'outil, et si REG-1 et REG-2 sont cités.

**Exemple chiffré.** La fusion RRF du palier 07 rend les identifiants `["REG-1", "REG-2", "FORUM-9"]` : REG-1 obtient 1/62 + 1/61 = 0,032522, REG-2 1/61 + 1/63 = 0,032266, le forum 1/63 + 1/62 = 0,032002. Le troisième document, le message de forum piégé, arrive au modèle avec ses chevrons neutralisés : il contient `&lt;system>`. Test : `TestScenariosRagEtVirement.test_reglementation_cite_ce_qu_elle_a_recu`.

### scenario_virement

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`scenario_virement()`** — Cette fonction doit rejouer la tentative d'escroquerie au courriel piégé, comme un exercice d'alerte où l'on vérifie que la porte blindée tient même quand le gardien a été dupé. Elle ne reçoit rien ; elle doit écrire un script où le modèle, convaincu, appelle `initier_virement` avec `A_VIREMENT`, puis annonce que le virement de 180 000 AED n'a pas été exécuté, et faire répondre l'agent à `QUESTION_VIREMENT` avec le document `COURRIEL-PROMOTEUR`. L'objectif est atteint si le statut vaut « fini », si `agent.virements` est vide et si le journal contient « refus par délai » : R = 0,70 mène à une revue, l'approbateur ne répond pas, l'horloge avance de 120 s et le journal compte 5 entrées où l'IBAN n'apparaît que sous la forme `[IBAN ••••3456]`.

```python
# [extrait] spécification
def scenario_virement() -> dict: ...
```

Script : un appel à `initier_virement` avec `A_VIREMENT` ("c1") — le modèle s'est laissé convaincre par le courriel —, puis le texte `f"Le virement de {fr(180_000, 0)} AED n'a pas été exécuté : aucune validation humaine en 120 s. Un conseiller vous rappellera."`. L'agent répond à `QUESTION_VIREMENT` avec le document `("COURRIEL-PROMOTEUR", COURRIEL)`. L'objectif est atteint si le statut vaut "fini", si `agent.virements` est vide et si une entrée du journal contient « refus par délai ».

**Exemple chiffré.** Dans l'outil, R = 0,4 × 0,7 + 0,4 × 1 + 0,2 × 0,1 = 0,70 : sous le seuil de blocage de 0,75, au-dessus du seuil de revue de 0,5, et le veto de l'action irréversible est actif ; décision « revue ». L'approbateur n'a aucune réponse : l'horloge avance de 120 s, et la ligne de trace vaut « ERREUR refusé par l'humain : pas de réponse en 120 s : refus par défaut ». Aucun virement n'est exécuté. Le journal compte 5 entrées (la question, la politique, le risque, l'approbation, la trace), et l'IBAN, l'Emirates ID et le numéro +971 n'y apparaissent jamais en clair : seulement `[IBAN ••••3456]`, `[EMIRATES_ID ••••5671]` et `[TEL ••••4567]`. Test : `TestScenariosRagEtVirement.test_virement_piege_refuse`.

### demande_credit

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`demande_credit(i, candidat)`** — Cette fonction doit fabriquer un dossier d'examen numéroté, avec son corrigé et la copie qu'un élève donné rendrait, un peu comme un professeur qui prépare quinze sujets voisins en faisant varier les chiffres. Elle reçoit le numéro i, de 1 à 15, et un booléen qui choisit la version candidate ; elle calcule le principal 1 000 000 − 25 000 i, le revenu 40 000 − 1 500 i et les mensualités en cours 6 000 + 500 i, la mensualité arrondie au centime, le ratio arrondi à quatre décimales et le verdict « recevable » si ce ratio vaut au plus 0,50. Elle rend `(script, question, attendus, verdict)`, le script de la candidate s'arrêtant après la mensualité avec « endettement estimé à 35 % » quand i vaut 1 modulo 4 : pour i = 1, la mensualité vaut 5 419,37 AED et le ratio 0,3096, et pour i = 8 le ratio 0,516 rend le dossier non recevable.

```python
# [extrait] spécification
def demande_credit(i: int, candidat: bool = False) -> tuple[list, str, list, str]: ...
```

Variante i, de 1 à 15 : principal 1 000 000 − 25 000 i, revenu 40 000 − 1 500 i, mensualités en cours 6 000 + 500 i. La mensualité `m` est `round(mensualite(principal, 0.045, 300), 2)` et le ratio `round(ratio_endettement(existantes, m, revenu)[0], 4)` ; le verdict vaut "recevable" si le ratio est au plus 0,50, "non recevable" sinon. La question vaut `f"Hypothèque de {fr(principal, 0)} AED à 4,5 % sur 300 mois ; revenu {fr(revenu, 0)} AED ; mensualités en cours {fr(existantes, 0)} AED : recevable ?"`. Les appels attendus sont `("mensualite", a1)` et `("ratio_endettement", a2)`, avec `a1 = {"principal": principal, "taux_annuel": 0.045, "n_mois": 300}` et `a2 = {"existantes": existantes, "nouvelle": m, "revenu": revenu}`. Le script commence par l'appel à `mensualite` ("v1"). Pour la candidate, quand `i % 4 == 1` (i = 1, 5, 9, 13), il se termine aussitôt par `f"Mensualité {fr(m)} AED ; endettement estimé à 35 % : dossier recevable."` ; sinon, il appelle `ratio_endettement` ("v2") puis répond `f"Mensualité {fr(m)} AED ; endettement total {fr(ratio * 100)} % : dossier {verdict}."`. La fonction rend `(script, question, attendus, verdict)`.

**Exemple chiffré.** Pour i = 1 : 975 000, 38 500 et 6 500 AED ; la mensualité est proportionnelle au principal, 5 558,3248 × 0,975 = 5 419,37 AED ; ratio (6 500 + 5 419,37) / 38 500 = 11 919,37 / 38 500 = 0,309594, arrondi à 0,3096 : « endettement total 30,96 % : dossier recevable. ». Pour i = 8 : 800 000, 28 000 et 10 000 AED ; mensualité 4 446,66 AED ; ratio 14 446,66 / 28 000 = 0,516 : « 51,60 % : dossier non recevable. ». Les variantes 1 à 7 sont recevables, les variantes 8 à 15 ne le sont pas. Le script candidat de la variante 5 n'a que 2 réponses, celui de la variante 6 en a 3. Tests : `TestDemandeCredit` (trois tests).

### evaluer_version et evaluation_complete

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`evaluer_version(candidat, communes)`** — Cette fonction doit faire passer à une version de l'agent l'examen complet, comme un jury qui ajoute aux trois épreuves déjà notées quinze dossiers de crédit tirés du même moule. Elle reçoit le choix de version et la liste des notes communes des trois scénarios, part d'une copie de cette liste, puis, pour i de 1 à 15, construit un agent neuf sur le script de `demande_credit(i, candidat)`, le fait répondre et le note avec `noter`, le but exigeant le statut « fini », la bonne fin « dossier … . » et un appel à `ratio_endettement` dans la trace. Elle rend `rapport(notes)` complété par le code et les motifs de `barriere_ci` : 18 sur 18 et le code 0 pour la production, 14 sur 18, Tool F1 0,926, fidélité 0,889 et le code 1 pour la candidate.

**`evaluation_complete()`** — Cette fonction doit être la séance plénière qui convoque les deux versions devant le même jury et publie les deux bulletins côte à côte. Elle ne reçoit rien ; elle doit noter les trois scénarios avec leurs appels attendus et leur but, puis appeler `evaluer_version` une fois pour la production et une fois pour la candidate, sur ces mêmes notes communes. Elle rend le dictionnaire `{"communes", "production", "candidate"}` : les trois scénarios seuls, parfaits, ne donneraient qu'une borne basse de 0,438 et le code 1, et c'est l'ajout des quinze variantes qui permet à la production de franchir la barrière avec 0,824.

```python
# [extrait] spécification
def evaluer_version(candidat: bool, communes: list[dict]) -> dict: ...

def evaluation_complete() -> dict: ...
```

`evaluer_version` part d'une **copie** des notes communes, puis, pour i de 1 à 15, construit un agent neuf sur le script de `demande_credit(i, candidat)`, le fait répondre à la question, et note le cas avec `noter(res, res["sources"], attendus, but)`. L'objectif d'une variante est atteint si le statut vaut "fini", si la réponse se termine par `f"dossier {verdict}."` **et** si la trace contient un appel à `ratio_endettement` : une bonne conclusion sans le calcul ne compte pas. Elle rend `rapport(notes)`, complété par `rap["code"], rap["motifs"] = barriere_ci(rap, SEUILS)`. `evaluation_complete` note les trois scénarios (leurs `attendus` et leur `but`), puis rend `{"communes": les 3 notes, "production": evaluer_version(False, communes), "candidate": evaluer_version(True, communes)}`.

**Exemple chiffré.** Les trois scénarios ont chacun F1 = 1, fidélité = 1 et objectif atteint ; seuls, ils donnent 3 sur 3, borne basse 0,438, code 1. La production réussit 18 cas sur 18 : Wilson [0,824 ; 1], Tool F1 1, fidélité 1, code 0, aucun motif ; la borne basse vaut exactement 18 / (18 + 1,96²). La candidate réussit 14 cas sur 18 : Wilson [0,548 ; 0,910], Tool F1 0,926, fidélité 0,889, code 1, avec trois motifs dont le premier est « borne basse de Wilson 0.548 < 0.8 ». Tests : `TestBarriereCI` (trois tests).

### ClaudeLLM, fourni : passer au vrai modèle

Le port LLM n'a qu'une méthode, `create(system=…, messages=…, tools=…)`, qui rend un objet portant `stop_reason` et `content`. `FakeLLM` l'implémente en rejouant un script ; `ClaudeLLM`, dans `agent/adaptateur_claude.py`, l'implémente en appelant l'API Claude. C'est l'architecture en ports et adaptateurs que tu connais en Java : `FakeLLM` serait un `@Component` actif sous le profil `test`, `ClaudeLLM` un `@Component` actif sous le profil `prod`, et `Agent` ne dépend que de l'interface. Voici l'adaptateur, recopié tel qu'il est dans le fichier :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`ClaudeLLM.__init__(model, effort, max_tokens)`** — Le constructeur de l'adaptateur est l'interprète que l'on engage pour remplacer l'acteur de répétition : il arrive avec son dictionnaire et ses réglages, et ne parle qu'au moment voulu. Il reçoit le nom du modèle, `"claude-opus-5-5"` par défaut, le niveau d'effort, `"medium"`, et le plafond de tokens de la réponse, 16000 ; il importe le SDK `anthropic` à l'intérieur même du constructeur, pour que le reste du paquet n'en dépende pas, crée un client `anthropic.Anthropic()` qui lit la clé ou le profil d'authentification, et range les trois réglages. Il ne rend rien et n'envoie encore aucune requête ; il n'est jamais exécuté par les tests.

**`ClaudeLLM.create(system, messages, tools)`** — Cette méthode est la seule porte du port LLM, celle que la boucle frappe à chaque tour, exactement comme elle frapperait celle du faux modèle. Elle reçoit, par mots-clés seulement, le prompt système, l'historique des messages et les définitions d'outils strictes, et envoie un appel à `client.beta.messages.create` avec le modèle, le plafond de tokens, l'effort dans `output_config`, la bêta de repli côté serveur et `fallbacks="default"`. Si la réponse s'arrête sur un refus accompagné de détails, elle imprime la catégorie et l'explication ; dans tous les cas, elle rend la réponse telle quelle, avec son `stop_reason` et son `content`, pour que `executer_agent` la traite comme celle de `FakeLLM`.

```python
# [extrait] agent/adaptateur_claude.py
class ClaudeLLM:
    """Même interface que FakeLLM : `create(system=…, messages=…, tools=…)` rend une réponse qui a
    `.stop_reason` et `.content` (blocs `.type`, `.text`, `.id`, `.name`, `.input`).

    `fallbacks="default"` (bêta `server-side-fallback-2026-07-01`) : si le modèle principal refuse une
    requête, l'API la rejoue elle-même sur un modèle de repli choisi selon la catégorie du refus.
    Retirer ces deux paramètres pour que chaque refus arrête la boucle avec le statut « refus ».
    """

    def __init__(self, model: str = "claude-opus-5-5", effort: str = "medium", max_tokens: int = 16000) -> None:
        import anthropic                      # import local : le paquet ne dépend pas du SDK

        self.client = anthropic.Anthropic()   # lit ANTHROPIC_API_KEY ou le profil créé par `ant auth login`
        self.model = model
        self.effort = effort
        self.max_tokens = max_tokens

    def create(self, *, system: str, messages: list, tools: list):
        """Un appel à l'API ; la réflexion adaptative est active par défaut sur ce modèle."""
        reponse = self.client.beta.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=messages,
            tools=tools,                             # [{"name", "description", "input_schema", "strict": True}]
            output_config={"effort": self.effort},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        if reponse.stop_reason == "refusal" and reponse.stop_details:
            print(f"refus : {reponse.stop_details.category} — {reponse.stop_details.explanation}")
        return reponse
```

Pour l'utiliser, une seule ligne change : on passe `ClaudeLLM()` au constructeur de l'`Agent` au lieu d'un `FakeLLM`.

```python
# [extrait] spécification
from agent.adaptateur_claude import ClaudeLLM
from agent.assemblage import QUESTION_CREDIT, Agent, memoire_client

agent = Agent(ClaudeLLM(), memoire=memoire_client())   # au lieu de construire_agent(script, memoire=…)
resultat = agent.repondre(QUESTION_CREDIT)
print(resultat["statut"], resultat.get("reponse"))
```

Les prérequis : installer le SDK avec `python -m pip install anthropic`, puis s'authentifier, soit avec `ant auth login`, soit en définissant la variable d'environnement `ANTHROPIC_API_KEY`. L'import d'`anthropic` est **dans** le constructeur : importer le module, ou lancer les tests, ne demande ni le SDK ni le réseau, et le reste du paquet reste en bibliothèque standard. Ce que fait chaque paramètre de l'appel :

- `model="claude-opus-5-5"` : le modèle Claude Opus 5.5. Sur ce modèle, la réflexion adaptative est active par défaut : le modèle décide lui-même quand et combien réfléchir.
- `max_tokens=16000` : le plafond de tokens de la réponse ; atteint, il donne le `stop_reason` "max_tokens", que la boucle traduit en statut "tronque".
- `system`, `messages` : le prompt système et l'historique construits par `construire_prompt` et `executer_agent`, transmis tels quels.
- `tools` : les définitions rendues par `Registre.definitions_api()`, en mode `strict` : l'API garantit que les arguments respectent exactement le schéma. Le mode strict refuse les bornes (`minimum`, `maximum`…) : `definitions_api` les retire et les recopie dans les descriptions, et la porte locale continue de les vérifier.
- `output_config={"effort": self.effort}` : le niveau d'effort, qui règle la profondeur de la réflexion et la dépense de tokens ; "medium" est la valeur par défaut de ce modèle, écrite explicitement.
- `betas=["server-side-fallback-2026-07-01"]` et `fallbacks="default"` : les replis automatiques en cas de refus. Si le modèle principal refuse la requête, l'API la rejoue elle-même sur un modèle de repli choisi selon la catégorie du refus, sans liste de modèles à tenir. Retire ces deux paramètres si tu veux que chaque refus arrête la boucle avec le statut "refus".
- `reponse.stop_details` n'est renseigné que lorsque `stop_reason` vaut "refusal" ; il porte la catégorie et l'explication du refus, que l'adaptateur affiche.

Quatre règles de l'API sont déjà respectées par `executer_agent`, et il faut les connaître pour ne pas les casser : pas de `tool_choice` forcé (ce modèle le refuse : on laisse le choix automatique et l'on nomme l'outil attendu dans le prompt) ; tous les `tool_result` d'une étape dans un seul message `user` ; `reponse.content` recopié tel quel dans l'historique, blocs de réflexion compris ; un `stop_reason` égal à "refusal" traité avant de lire le contenu. Les prix du palier 11 restent illustratifs : pour chiffrer un vrai déploiement, on prend la grille du fournisseur pour le modèle choisi.

## Squelette algorithmique

```text
ALGORITHME ConstruireAgent(modèle, mémoire, session, horloge)
  session ← copie de (session OU session client par défaut)
  horloge ← horloge OU Horloge(jour 90)
  journal ← JournalAudit(horloge) ; approbateur ← Approbateur(horloge, journal) ; virements ← []
  registre ← Registre vide
  enregistrer la recherche, puis les cinq outils de calcul, puis le virement (approbateur, journal, virements)
  outils ← Protéger(registre, session, journal)            (politique, puis schéma, puis outil)
  schémas ← définitions API strictes du registre
  RETOURNER l'agent

ALGORITHME Répondre(agent, question, documents, k, max étapes)
  SI la mémoire n'est pas vide ALORS rappel ← Rappeler(question, mémoire, jour courant, k) SINON rappel ← []
  (système, message) ← ConstruirePrompt(question, textes du rappel, documents)
  Journaliser(« question : » message)
  résultat ← BoucleAgent(modèle, système, message, outils, schémas, max étapes)
  POUR CHAQUE (nom, arguments, sortie) DE la trace FAIRE Journaliser(« trace » nom arguments sortie)
  résultat.rappel ← rappel ; résultat.sources ← [système, message] + sorties en JSON
  RETOURNER résultat

ALGORITHME ÉvaluerVersion(candidat, notes communes)
  notes ← copie des notes communes
  POUR i DE 1 À 15 FAIRE
      (script, question, attendus, verdict) ← DemandeCrédit(i, candidat)
      résultat ← Répondre(ConstruireAgent(FauxModèle(script)), question)
      but ← fini ET réponse finit par « dossier verdict. » ET ratio présent dans la trace
      ajouter Noter(résultat, sources, attendus, but) à notes
  FIN POUR
  rapport ← Rapport(notes) ; (code, motifs) ← BarrièreCI(rapport, seuils)
  RETOURNER rapport avec code et motifs
```

**Complexité.** Construire un agent coûte O(1) en dehors de l'enregistrement de sept outils. Une réponse coûte au plus max étapes appels au modèle, la borne de la boucle (palier 05), plus le rappel en O(nombre de souvenirs) et la recherche hybride quand elle est appelée. L'évaluation complète fait 3 + 2 × 15 = 33 exécutions de la boucle, soit 33 × (k + 1) appels au modèle pour des scénarios de k étapes d'outils : gratuit avec le faux modèle, facturé avec le vrai, et multiplié par le nombre d'essais si l'on veut mesurer une réussite répétée (étape 60). La mémoire est O(n) pour les notes.

**Du squelette au code.** `ConstruireAgent` est le constructeur `Agent.__init__` (et `construire_agent` pour le faux modèle) ; `Protéger` est `proteger` du palier 09 ; les définitions sont `definitions_api`. `Répondre` est `Agent.repondre`, où `Rappeler` est `rappeler`, `ConstruirePrompt` est `construire_prompt`, `BoucleAgent` est `executer_agent` et `Journaliser` est la méthode `journaliser` de `JournalAudit`. `ÉvaluerVersion` est `evaluer_version`, avec `DemandeCrédit` pour `demande_credit`, `Noter` pour `noter`, `Rapport` pour `rapport` et `BarrièreCI` pour `barriere_ci` ; `evaluation_complete` l'appelle deux fois sur les notes des trois scénarios.

## Cas d'usage aux Émirats

Les montants, poids, seuils et volumes ci-dessous sont illustratifs, sauf les règles réelles du parcours (plafond d'endettement de la CBUAE, TVA de 5 %, parité de 3,6725 AED pour 1 USD, frais DLD de 4 %, fin de service du décret-loi fédéral 33/2021), à confirmer avec le texte en vigueur. Dans chaque métier, on garde l'`Agent`, la boucle, `proteger`, l'évaluation et l'adaptateur ; on change les outils, le corpus, la politique et les seuils.

**Banque — pré-instruire le dossier de crédit d'un client retraité.** La banque B-1 confie à l'agent la pré-instruction de ses demandes d'hypothèque. La mémoire du client C-1 contient sa pension déclarée, 40 000 AED, et 7 000 AED de crédits en cours ; le plafond d'endettement d'un retraité est de 30 %. Pour la même hypothèque de 1 000 000 AED, le ratio vaut (7 000 + 5 558,32) / 40 000 = 0,314 : recevable pour un salarié, refusé pour un retraité. On ajoute à `ratio_endettement` un argument de plafond que **le code** remplit à 0,30 quand la mémoire indique la retraite, jamais le modèle, et la recherche hybride cite REG-1. Avant chaque changement de prompt, `evaluation_complete` tourne sur quelques centaines de dossiers déjà tranchés par les analystes, et la barrière CI bloque toute version dont la borne basse de Wilson tombe sous 0,80.

**Immobilier — un acompte off-plan payé sur le bon compte.** Un promoteur de Dubaï laisse l'agent répondre aux acheteurs d'un projet off-plan. Pour un appartement de 1 800 000 AED, l'acompte de 10 % vaut 180 000 AED et les frais de transfert DLD de 4 % valent 72 000 AED ; un acheteur étranger veut le prix en dollars : 1 800 000 / 3,6725 = 490 129,34 USD. Le scénario (c) est exactement la fraude que ce métier redoute : un courriel imitant le promoteur donne un autre IBAN. On enregistre dans le registre de l'agent un outil qui compare l'IBAN demandé au compte enregistré pour le projet, et l'on relève la sensibilité à 1 quand ils diffèrent : R = 0,4 × 1 + 0,4 × 1 + 0,2 × 0,1 = 0,82, au-dessus du seuil de blocage de 0,75, et le virement est bloqué sans même solliciter l'humain. Le journal masqué et chaîné permet de rejouer le dossier devant la conformité sans exposer les coordonnées bancaires de l'acheteur.

**RH — l'indemnité de fin de service, calculée puis versée.** Un cabinet RH multi-émirats répond aux salariés de ses clients sur leurs droits de fin de contrat. L'outil `gratuite_fin_de_service` est déjà dans le registre : pour un salaire de base de 10 000 AED et 7 ans de service, il donne 5 × 21 × 333,33 + 2 × 30 × 333,33 = 55 000 AED, et la recherche cite REG-4. Le versement est traité comme le virement du scénario (c) : une portée dédiée dans la politique, un veto par montant au-delà de 25 000 AED, l'approbation du responsable de paie **dans** l'outil. On construit le jeu d'évaluation comme `demande_credit` : quinze variantes de salaire et d'ancienneté, dont certaines au-delà de cinq ans, là où une erreur de 21 jours au lieu de 30 donnerait 49 000 AED au lieu de 55 000 AED, une erreur que la fidélité approchée et la Tool Call F1 détectent.

## Travail à faire

Toutes les commandes se lancent dans PowerShell, depuis `projet/`. Si `python` n'est pas dans le PATH, remplace-le par `& "C:\Users\aur95\AppData\Local\Python\pythoncore-3.14-64\python.exe"`.

1. Lire ce README en entier, puis refaire sur une feuille A4 la mensualité de 5 558,32 AED, le ratio de 0,289, le score de risque de 0,70, les bornes de Wilson 0,824 et 0,438, et les métriques 0,926 et 0,889 de la candidate.
2. Vérifier le point de départ : les 150 tests des paliers 01 à 11 passent, les 15 tests du palier 12 échouent tous par `NotImplementedError`.

```text
cd "C:\Users\aur95\Documents\AI\AI Agentic\Exercices\12-Assemblage-Agent-Complet\projet"
python -m unittest
```

3. Ouvrir `agent/assemblage.py`. Coder `Agent.__init__`, `Agent.repondre` et `construire_agent`, puis lancer `python -m unittest -v tests.test_12_assemblage.TestScenariosRagEtVirement.test_agent_accepte_n_importe_quel_port tests.test_12_assemblage.TestScenariosRagEtVirement.test_session_publique_refusee_par_la_politique`.
4. Coder `sortie_outil`, `memoire_client` et `scenario_credit`, puis lancer `python -m unittest -v tests.test_12_assemblage.TestScenarioCredit`.
5. Coder `scenario_reglementation` et `scenario_virement`, puis lancer `python -m unittest -v tests.test_12_assemblage.TestScenariosRagEtVirement`.
6. Coder `demande_credit`, puis lancer `python -m unittest -v tests.test_12_assemblage.TestDemandeCredit`.
7. Coder `evaluer_version` et `evaluation_complete`, puis lancer `python -m unittest -v tests.test_12_assemblage.TestBarriereCI`.
8. Lancer tous les tests, puis la démo, et comparer sa sortie à celle ci-dessous.

```text
python -m unittest -v
python demo.py
```

9. Facultatif, avec une clé d'API : rejouer le scénario (a) avec `Agent(ClaudeLLM(), memoire=memoire_client())`, et comparer la trace réelle aux trois appels attendus avec `tool_call_f1`.

## Critères de réussite

- `python -m unittest` affiche `Ran 165 tests` puis `OK` : les 150 tests des paliers précédents et les 15 du palier 12.
- `python demo.py` affiche exactement la sortie ci-dessous, à chaque exécution.
- Tu sais expliquer, pour chaque ligne du constructeur de l'`Agent`, de quel palier vient l'objet câblé et quelle propriété il garantit, et pourquoi trois scénarios parfaits ne suffisent pas à franchir la barrière CI.

### Sortie attendue de demo.py

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

## Pour aller plus loin

1. **Brancher la planification (palier 08).** Calculer `vagues(dossier_credit())` et comparer la troisième vague au script du scénario (a). Réponse attendue : la troisième vague, `calculer_ratio` et `convertir_usd`, est exactement la deuxième réponse du script, qui demande les deux outils dans le même message ; un agent Plan-and-Execute enverrait un message par vague, cinq au lieu de huit en séquentiel, et le chemin critique donne la durée minimale du plan, 5,7 s contre 9,5 s.
2. **Brancher la production (palier 11).** Écrire une classe `LLMEnProduction` qui a la même méthode `create` que `FakeLLM` et `ClaudeLLM`, consomme 3 000 jetons d'un `SeauAJetons` avant chaque appel (`ErreurTransitoire` si le seau refuse), passe l'appel par `executer_avec_relances` sur l'horloge de l'agent, et ajoute `cout_tache` à une liste quand la réponse porte un `usage`. Réponse attendue : avec un seau de 6 000 jetons rechargé à 50 par seconde, une base de 20 s et sans gigue, le scénario (a) finit toujours en 3 étapes, mais son troisième appel attend 20 + 40 = 60 s simulées ; l'`Agent` ne change pas d'une ligne, puisqu'il ne voit que le port. L'esquisse complète est dans la dernière étape de la progression.
3. **Rejouer le scénario (c) avec le vrai modèle.** Lancer `scenario_virement` en remplaçant le faux modèle par `ClaudeLLM()`, plusieurs fois. Réponse attendue : quoi que décide le modèle (appeler l'outil, refuser, demander une confirmation), `agent.virements` reste vide, parce que l'approbation humaine est dans l'outil et qu'aucune réponse humaine n'est prévue.

## Si tu bloques

La solution est construite pas à pas dans `solutions/progression/` ; ouvre le fichier de l'étape qui te bloque.

- [Étape 1 — Les constantes et ce qui change depuis 77](<solutions/progression/01-Constantes-et-ecarts-avec-77.md>) : les imports palier par palier, la session qui vient de l'authentification, et pourquoi les variables globales disparaissent.
- [Étape 2 — Le constructeur de l'Agent, ou le câblage](<solutions/progression/02-Agent-le-cablage.md>) : chaque objet créé dans le bon ordre, la copie de la session, le registre dans l'ordre de 77.
- [Étape 3 — Agent.repondre](<solutions/progression/03-Agent-repondre.md>) : mémoire, prompt, boucle, journal et sources, en douze lignes.
- [Étape 4 — Le scénario du crédit](<solutions/progression/04-Scenario-credit.md>) : la fabrique, la mémoire du client, le script en trois réponses et l'objectif vérifié.
- [Étape 5 — Les scénarios réglementaire et du virement piégé](<solutions/progression/05-Scenarios-reglementation-et-virement.md>) : citer ce qu'on a reçu, et refuser ce qu'aucun humain n'a approuvé.
- [Étape 6 — Les variantes et la barrière CI](<solutions/progression/06-Variantes-et-barriere-CI.md>) : quinze dossiers, une candidate fautive, et la barrière qui dit non.
- [Étape 7 — Passer au vrai LLM](<solutions/progression/07-Passer-au-vrai-LLM.md>) : l'adaptateur Claude, ligne par ligne, et les quatre règles de l'API.
- [Étape 8 — Assembler, lancer et récapituler les douze paliers](<solutions/progression/08-Assembler-lancer-et-recapituler.md>) : tous les tests, la démo commentée, les branchements bonus, et tout ce que tu sais maintenant coder depuis une feuille blanche.

La solution entière est dans `solutions/agent/assemblage.py` (et `solutions/agent/adaptateur_claude.py`), avec les tests dans `solutions/tests/` et la démo dans `solutions/demo.py`.
