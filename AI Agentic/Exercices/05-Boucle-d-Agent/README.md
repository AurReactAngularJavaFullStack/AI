# Palier 05 — La boucle d'agent

> Palier 05 sur 12 · Précédent : [Palier 04 — Registre d'outils](<../04-Registre-d-Outils/README.md>) · Suivant : [Palier 06 — Mémoire](<../06-Memoire/README.md>) · Leçons à relire : [Étape 1 — Ce qu'est un agent IA](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>) · [Étape 13 — Agent, exemples et cas d'usage](<../../03-Schemas-Outils-et-Premiere-Evaluation/13-Agent-Exemples-Cas-Usage.md>) · [Étape 77 — Projet final](<../../13-Projet-Final/77-Projet-Final-Agent-From-Scratch.md>) · Démonstrations : [29 — Fiabilité en série](<../../Demonstrations/01-Introduction/29_fiabilite_serie.md>) · [15 — Budget de contexte](<../../Demonstrations/05-Contexte/15_budget_contexte.md>)

## Où en est l'agent

Les quatre premiers paliers ont posé les pièces une par une, sans jamais les faire tourner ensemble :

- palier 01, `agent/modele.py` : le port LLM (`Bloc`, `Reponse`, `texte`, `appel_outil`), le faux modèle scripté `FakeLLM` et `construire_prompt` ;
- palier 02, `agent/schemas.py` : `validate` et `objet`, le contrat des arguments ;
- palier 03, `agent/metier.py` : les calculs EAU (mensualité, ratio d'endettement CBUAE, conversion AED/USD à 3,6725, TVA de 5 %, fin de service) ;
- palier 04, `agent/outils.py` : le `Registre`, sa `porte` qui valide avant d'exécuter, et `executer_appel`, qui transforme un bloc `tool_use` en `tool_result`, erreur comprise.

Il manque le chef d'orchestre. C'est `agent/boucle.py`, que tu écris dans ce palier : une fonction qui fait parler le modèle et les outils à tour de rôle jusqu'à une raison d'arrêt toujours connue.

```text
                       ┌──────────────────────────── paquet agent/ ───────────────────────────┐
  question ──────────► │  modele.construire_prompt (01) ── système, message ──┐               │
                       │                                                      ▼               │
                       │   ╔══════════════════════════════════════════════════════════════╗   │
   port LLM            │   ║  boucle.executer_agent                     PALIER 05 (ICI)   ║   │
   FakeLLM (01) ◄──────┼───║   percevoir → décider → agir → observer → … → arrêt          ║   │
   llm.create(…)  ─────┼──►║   statuts : fini, refus, tronque, boucle, max_etapes         ║   │
                       │   ╚══════════════════════════════════════════════════════════════╝   │
                       │            │ bloc tool_use                    ▲ tool_result           │
                       │            ▼                                  │ (is_error si échec)   │
                       │   outils.executer_appel (04) → Registre.porte → validate (02)         │
                       │                                              → metier (03)            │
                       └──────────────────────────────────────────────────────────────────────┘
```

Dans la boucle percevoir → décider → agir → observer, `executer_agent` tient les quatre temps. Il **perçoit** en rassemblant le prompt système, l'historique `messages` et les schémas d'outils. Il fait **décider** le modèle par un appel à `llm.create`. Il **agit** en confiant chaque bloc `tool_use` à `executer_appel`. Il **observe** en renvoyant tous les `tool_result` dans un seul message `user`. Puis il recommence, sauf si un des cinq arrêts se déclenche. Le palier 06 donnera à l'agent une mémoire, que `construire_prompt` placera dans le prompt système avant le premier tour.

## Ce que tu vas coder

- `STATUTS` : le tuple des cinq statuts d'arrêt, dans l'ordre `fini`, `refus`, `tronque`, `boucle`, `max_etapes`.
- `signature_appels(appels)` : la liste des couples (nom, arguments en JSON à clés triées) d'une étape, qui sert à reconnaître la même action répétée.
- `executer_agent(llm, system, question, outils, schemas, max_etapes=8)` : la boucle ReAct complète, qui rend un dictionnaire avec le statut, la trace, le nombre d'étapes, l'historique et, si le statut est `fini`, la réponse.

## Rappel de cours

La boucle elle-même n'a pas de formule. Ce sont ses garanties qui en ont : combien d'appels au modèle elle fait au plus, combien elle en fait quand tout va bien, combien de messages elle relit en tout, et pourquoi chaque étape de plus coûte de la fiabilité.

La borne : quel que soit le modèle, le nombre d'appels au modèle ne dépasse jamais `max_etapes`.

$$
N_{LLM} \le E_{max}
$$

Le coût d'une tâche ReAct qui demande k étapes d'outils, sans `pause_turn` : un appel par étape d'outils, plus un pour la réponse finale.

$$
N_{LLM} = k + 1
$$

Le nombre de messages envoyés au e-ième appel, quand toutes les étapes d'avant ont exécuté des outils : la question, puis deux messages par étape passée (la réponse du modèle et le message de résultats).

$$
\lvert M_e \rvert = 1 + 2\,(e - 1) = 2e - 1
$$

Le total des messages relus sur E appels est donc un carré : c'est le coût caché d'une boucle longue.

$$
\sum_{e=1}^{E} (2e - 1) = E^{2}
$$

L'arrêt `boucle` : la signature d'une étape est comparée à celle de l'étape d'avant.

$$
\sigma_e = \sigma_{e-1} \;\Longrightarrow\; \text{statut} = \text{boucle}
$$

La fiabilité composée (étape 1) : une chaîne de n étapes indépendantes ne réussit que si toutes réussissent.

$$
P(\text{succès}) = \prod_{i=1}^{n} p_i
$$

### Les symboles, un par un

$$
E_{max}
$$

La borne d'étapes, un entier ≥ 1 ; en Python, le paramètre `max_etapes`, qui vaut 8 par défaut.

$$
N_{LLM}
$$

Le nombre d'appels au modèle pendant une exécution ; en Python, `llm.appels` pour le faux modèle, et `r["etapes"]` dans le résultat.

$$
e
$$

Le numéro de l'étape en cours, de 1 à E max ; en Python, la variable de boucle `etape`.

$$
k
$$

Le nombre d'étapes qui exécutent des outils ; une étape peut exécuter plusieurs outils à la fois, elle compte pour une.

$$
\lvert M_e \rvert
$$

La longueur de l'historique envoyé au e-ième appel ; en Python, `len(llm.requetes[e - 1]["messages"])`.

$$
\sigma_e
$$

La signature de l'étape e : la liste des couples (nom, arguments triés) ; en Python, `signature_appels(appels)`, comparée à `precedente`.

$$
p_i
$$

La probabilité que l'étape i réussisse (un appel au modèle ou une exécution d'outil), un réel dans [0, 1].

$$
n
$$

Le nombre d'étapes de la chaîne : dans le scénario du crédit, trois appels au modèle et trois exécutions d'outils, donc n = 6.

**Pourquoi la borne tient.** Le seul appel à `llm.create` est dans le corps d'une boucle `for etape in range(1, max_etapes + 1)`, qui fait au plus E max tours, avec exactement un appel par tour. Les cinq sorties sont des `return` et `pause_turn` passe au tour suivant : aucune branche ne rappelle le modèle en dehors de ce tour. La borne vaut donc pour un modèle adversaire qui demanderait des outils sans fin.

**Pourquoi le total est un carré.** On passe de E − 1 à E appels en ajoutant le dernier terme, 2E − 1, et E² − (E − 1)² = 2E − 1 ; comme le total vaut 1 = 1² pour E = 1, il vaut E² pour tout E (récurrence). Trois appels relisent 1 + 3 + 5 = 9 messages ; huit appels en relisent 64. Quand l'historique est renvoyé en entier à chaque appel, le coût en tokens d'entrée croît comme le carré du nombre de tours (démonstration 3 de la fiche [15 — Budget de contexte](<../../Demonstrations/05-Contexte/15_budget_contexte.md>)).

**Pourquoi grouper les appels.** Dans le scénario du crédit, le modèle demande le ratio et la conversion dans la même réponse. La chaîne compte alors six étapes et, à 0,98 par étape, réussit avec la probabilité 0,98⁶ ≈ 0,8858 ; avec un appel au modèle de plus, elle en compterait sept, soit 0,98⁷ ≈ 0,8681. C'est pourquoi la boucle exécute **tous** les appels d'une réponse et renvoie **tous** les résultats ensemble.

## Spécification

Le module importe `json` et `executer_appel` (palier 04). Il ne connaît ni le modèle ni les outils : il les reçoit en paramètres.

### STATUTS

```python
# [extrait] spécification
STATUTS = ("fini", "refus", "tronque", "boucle", "max_etapes")
```

Le tuple des statuts que `executer_agent` peut rendre, dans cet ordre. Seul `fini` porte une réponse utilisable. `refus` et `tronque` viennent de l'API ; `boucle` et `max_etapes` sont les deux arrêts de sûreté propres à l'agent. Le test `test_cinq_statuts` fait tourner cinq scripts, un par statut, avec `max_etapes=2`, et vérifie qu'on obtient exactement ce tuple, dans cet ordre.

### signature_appels

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`signature_appels(appels)`** — Cette fonction doit relever l'empreinte d'une étape, comme un contrôleur qui note sur son registre chaque ordre de mission dans le même format, afin de reconnaître au premier coup d'œil un ordre déjà donné : elle reçoit la liste des blocs `tool_use` d'une réponse et renvoie une liste de couples (nom de l'outil, arguments écrits en JSON à clés triées), dans l'ordre des blocs. Le tri rend la signature indépendante de l'ordre d'écriture des arguments, et l'identifiant de l'appel n'y entre pas ; une liste plutôt qu'un ensemble garde l'ordre et les répétitions. Les arguments `{"b": 2, "a": 1}` et `{"a": 1, "b": 2}` d'un même outil « ratio » doivent ainsi donner la même signature, celle que `executer_agent` comparera d'une étape à l'autre pour déclencher l'arrêt `boucle`.

```python
# [extrait] spécification
def signature_appels(appels: list) -> list[tuple[str, str]]:
    """La signature d'une étape : la liste des couples (nom, arguments en JSON trié)."""
```

- Entrée : la liste des blocs `tool_use` d'une réponse (attributs `name` et `input`).
- Sortie : une liste de couples `(nom, texte JSON des arguments)`, dans l'ordre des blocs, avec les clés du JSON triées.
- Pourquoi trier : `{"b": 2, "a": 1}` et `{"a": 1, "b": 2}` sont les mêmes arguments. Sans tri, `json.dumps` suit l'ordre d'insertion du dictionnaire et donne deux textes différents, et l'arrêt `boucle` raterait la répétition.
- Pourquoi une liste et pas un ensemble : l'ordre des blocs et les répétitions font partie de l'action. Deux appels identiques dans la même réponse ne se confondent pas avec un seul.

**Exemple chiffré.** Pour `appel_outil("ratio", {"b": 2, "a": 1}, "x")`, `json.dumps(…, sort_keys=True)` écrit d'abord la clé `a`, puis `b` : la signature vaut `[("ratio", '{"a": 1, "b": 2}')]`. Le bloc `appel_outil("ratio", {"a": 1, "b": 2}, "y")` a la même signature, bien que son identifiant diffère : l'identifiant n'y entre pas. Le premier appel du scénario du crédit, `mensualite` avec `{"principal": 1000000, "taux_annuel": 0.045, "n_mois": 300}`, a la signature `[("mensualite", '{"n_mois": 300, "principal": 1000000, "taux_annuel": 0.045}')]`, dans l'ordre alphabétique des clés. Test : `TestErreurs.test_signature_independante_de_l_ordre_des_arguments`.

### executer_agent

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — Cette fonction doit être le chef d'orchestre qui fait jouer le modèle et les outils à tour de rôle jusqu'à ce qu'une raison d'arrêt, toujours connue, baisse le rideau : elle reçoit le port du modèle, le prompt système et la question, le dictionnaire des portes, les définitions d'outils au format de l'API et la borne `max_etapes`, 8 par défaut, et lève `ValueError` si cette borne est inférieure à 1. À chaque étape, elle doit appeler le modèle une seule fois, ajouter sa réponse telle quelle à l'historique, s'arrêter sur un refus ou une troncature, passer au tour suivant sur `pause_turn`, rendre `fini` s'il n'y a plus d'appel d'outil, rendre `boucle` si la signature répète celle de l'étape d'avant, et sinon exécuter tous les appels et renvoyer tous leurs résultats dans un seul message. Elle renvoie un dictionnaire aux clés `statut`, `trace`, `etapes` et `messages`, plus `reponse` pour le seul statut `fini` ; le scénario du crédit de C-1 doit finir en 3 étapes, avec trois lignes de trace et un historique de 6 messages.

```python
# [extrait] spécification
def executer_agent(llm, system: str, question: str, outils: dict, schemas: list, max_etapes: int = 8) -> dict:
    """Fait tourner la boucle ReAct ; rend {"statut", "trace", "etapes", "messages"} (+ "reponse" si fini)."""
```

**Entrées.**

- `llm` : tout objet qui a une méthode `create(*, system, messages, tools)` et rend une réponse portant `stop_reason` et `content` (le `FakeLLM` du palier 01, ou l'adaptateur Claude du palier 12).
- `system` et `question` : les deux textes rendus par `construire_prompt`.
- `outils` : le dictionnaire nom → appelable, `Registre.appelables()`.
- `schemas` : les définitions au format de l'API, `Registre.definitions_api()`, transmises telles quelles au modèle à chaque appel.
- `max_etapes` : la borne, un entier ≥ 1 ; une valeur plus petite lève `ValueError`.

**Sortie.** Un dictionnaire avec toujours quatre clés : `statut` (un élément de `STATUTS`), `trace` (une ligne `(nom, arguments, sortie)` par outil exécuté), `etapes` (le nombre d'appels au modèle, ou `max_etapes`) et `messages` (l'historique complet). La clé `reponse`, la concaténation des blocs de texte de la dernière réponse, n'existe **que** pour le statut `fini`.

**Comportement, dans l'ordre exact des tests à faire à chaque étape.**

1. Appeler le modèle avec des arguments nommés : `llm.create(system=…, messages=…, tools=schemas)`.
2. Ajouter aussitôt `{"role": "assistant", "content": reponse.content}` à l'historique : le contenu est recopié tel quel, c'est le même objet liste, sans copie ni retouche.
3. `stop_reason` vaut `"refusal"` : rendre `refus`. Il vaut `"max_tokens"` : rendre `tronque`, car une réponse coupée ne doit jamais servir de réponse finale. Il vaut `"pause_turn"` : passer à l'étape suivante, sans rien exécuter ni comparer.
4. Extraire les blocs de type `tool_use`. Si `stop_reason` vaut `"end_turn"`, ou s'il n'y a aucun bloc `tool_use`, rendre `fini` avec la réponse.
5. Calculer la signature des appels ; si elle est égale à celle de l'étape précédente, rendre `boucle` **avant** d'exécuter quoi que ce soit. Sinon, la mémoriser.
6. Exécuter chaque appel avec `executer_appel(outils, bloc)`, qui ne lève jamais : un échec devient un `tool_result` marqué `is_error` et une ligne de trace `"ERREUR …"`. Ranger tous les `tool_result` de l'étape dans **un seul** message `user`.
7. Si la boucle épuise ses `max_etapes` tours, rendre `max_etapes`, avec `etapes` égal à `max_etapes`.

**Exemple chiffré : la trace complète du scénario du crédit (étape 77).** Le client C-1 demande une hypothèque de 1 000 000 AED sur 25 ans à 4,5 %. Il gagne 40 000 AED par mois et rembourse déjà 6 000 AED. Le faux modèle joue trois réponses, et la boucle les traite ainsi, tour par tour.

```text
appel  messages envoyés  réponse du modèle (script)                     ce que fait la boucle
-----  ----------------  ---------------------------------------------  ------------------------------------------------
1      1  (user)         tool_use : mensualite(a1)                      σ₁ ≠ précédente (rien) → exécute 1 outil
                                                                        sortie {"mensualite_aed": 5558.32}
                                                                        + assistant + user[a1]          → 3 messages
2      3                 tool_use : ratio_endettement(a2),              σ₂ ≠ σ₁ → exécute 2 outils
                                    convertir_aed_usd(a3)               {"ratio": 0.289, "recevable": True}
                                                                        {"montant_usd": 1513.5}
                                                                        + assistant + user[a2, a3]      → 5 messages
3      5                 end_turn : texte « Dossier recevable. »        statut fini, etapes = 3         → 6 messages
```

Les sorties se recalculent à la main. Le taux mensuel vaut 0,045 / 12 = 0,00375, et la mensualité 1 000 000 × 0,00375 / (1 − 1,00375⁻³⁰⁰) = 3 750 / 0,67467 ≈ 5 558,32 AED. Le ratio additionne toutes les mensualités : (6 000 + 5 558,32) / 40 000 = 11 558,32 / 40 000 = 0,288958, arrondi à 0,289, sous le plafond de 0,50, donc recevable. La conversion donne 5 558,32 / 3,6725 = 1 513,4976, arrondi à 1 513,50 USD. Le résultat vaut donc `statut == "fini"` et `etapes == 3`, avec trois lignes de trace. L'historique final compte 6 messages, de rôles user, assistant, user, assistant, user, assistant. Le troisième appel a reçu 5 messages, dont le dernier contient les deux `tool_result`, `a2` puis `a3`. On retrouve N LLM = k + 1 = 2 + 1 = 3, et 1 + 3 + 5 = 9 = 3² messages relus. Tests : `TestScenarioCredit.test_trois_etapes_et_sorties`, `test_tous_les_resultats_dans_un_seul_message` et `test_contenu_recopie_tel_quel_et_outils_transmis`.

**Les autres arrêts, chacun avec son test.**

- `Reponse("end_turn", [texte("Bonjour"), texte(" !")])` : `fini` à l'étape 1, réponse `"Bonjour !"` (les textes sont collés sans séparateur), trace vide. Test : `test_reponse_finale_directe`.
- `Reponse("refusal", [])` : `refus` à l'étape 1. `Reponse("max_tokens", [texte("coupé")])` : `tronque` à l'étape 1, et le résultat n'a **pas** de clé `reponse`. Test : `test_refus_et_troncature`.
- La même réponse `tva(100)` deux fois : à l'étape 2, σ₂ = σ₁, d'où `boucle` à l'étape 2 avec une seule ligne de trace, car la seconde demande n'est pas exécutée. Test : `test_meme_action_deux_fois`.
- Trois appels `tva` de montants 1, 2 et 3 avec `max_etapes=2` : deux outils exécutés, puis `max_etapes`, et le faux modèle n'a été appelé que 2 fois. `max_etapes=0` lève `ValueError`. Test : `test_max_etapes_borne_les_appels`.
- `pause_turn` puis `end_turn` : `fini` en 2 étapes, trace vide. Test : `test_pause_turn_relance_sans_executer`.
- `tva` avec `{"montant_ht": -5}` puis `end_turn` : la porte du palier 04 lève `ArgumentsInvalides`. `executer_appel` la transforme en `tool_result` dont le contenu vaut `ArgumentsInvalides: $.montant_ht : -5 < minimum 0`, avec `is_error` à vrai, et en ligne de trace `ERREUR $.montant_ht : -5 < minimum 0`. Le modèle lit l'erreur au tour 2 et répond : `fini`. Test : `TestErreurs.test_erreur_d_outil_renvoyee_au_modele`.

**Cas limites.** Une réponse `end_turn` qui contient aussi des blocs `tool_use` rend `fini` : ces blocs ne sont pas exécutés. Une réponse `tool_use` sans aucun bloc `tool_use` rend aussi `fini`. Un outil inconnu ne fait pas planter la boucle : `executer_appel` rend `ErreurOutil: outil inconnu : x`. Un script de faux modèle trop court lève `RuntimeError` : c'est voulu, un scénario mal écrit doit se voir.

### Ce qui change par rapport à l'étape 77

Le code de 77 tient dans un seul fichier ; ici, il est découpé en modules testés un par un. Quatre écarts en découlent, tous voulus.

- **Plus de variable globale.** Dans 77, la boucle recevait `OUTILS_AGENT`, construit à partir d'un `REGISTRE` global. Ici, `outils` et `schemas` sont fabriqués par un objet `Registre` que l'appelant crée et passe en paramètre : chaque test a le sien.
- **L'exécution d'un outil est déléguée.** Le bloc `try … except` de 77 est devenu `executer_appel` au palier 04 : la boucle ne fait plus que l'appeler. Conséquence visible : un outil inconnu donne `ErreurOutil: outil inconnu : x` au lieu d'un `KeyError` brut.
- **Le résultat contient aussi `messages`.** L'historique complet permet aux tests de vérifier ce que le modèle a reçu, et à l'appelant d'auditer toute la conversation, réponses refusées ou tronquées comprises.
- **Deux ajouts de robustesse.** La signature est calculée par une fonction à part, `signature_appels`, testable seule. `max_etapes < 1` lève `ValueError`, alors que 77 aurait rendu `max_etapes` après zéro appel, un statut trompeur.

## Squelette algorithmique

```text
ALGORITHME SignatureAppels
ENTRÉE  : appels, liste de blocs tool_use
SORTIE  : liste de couples (nom, arguments écrits en JSON à clés triées)
  RETOURNER [ (a.nom, JSON trié de a.arguments) POUR CHAQUE a DANS appels ]

ALGORITHME ExécuterAgent
ENTRÉES : modèle (port LLM), système, question, outils (nom → porte), schémas, max_étapes
SORTIE  : statut ∈ {fini, refus, tronque, boucle, max_etapes}, trace, étapes, messages (+ réponse si fini)

  SI max_étapes < 1 ALORS ERREUR « max_étapes doit valoir au moins 1 »
  messages ← [ (user, question) ] ; trace ← liste vide ; précédente ← rien
  POUR étape DE 1 À max_étapes FAIRE
      réponse ← modèle.create(système, messages, schémas)                 (un appel par tour)
      ajouter (assistant, réponse.contenu) à messages                      (tel quel)
      SI réponse.arrêt = refusal    ALORS RETOURNER (refus, trace, étape, messages)
      SI réponse.arrêt = max_tokens ALORS RETOURNER (tronque, trace, étape, messages)
      SI réponse.arrêt = pause_turn ALORS passer au tour suivant
      appels ← blocs tool_use de réponse.contenu
      SI réponse.arrêt = end_turn OU appels est vide ALORS
          RETOURNER (fini, textes de la réponse mis bout à bout, trace, étape, messages)
      signature ← SignatureAppels(appels)
      SI signature = précédente ALORS RETOURNER (boucle, trace, étape, messages)
      précédente ← signature ; résultats ← liste vide
      POUR CHAQUE appel a DANS appels FAIRE
          (résultat, ligne) ← ExécuterAppel(outils, a)                     (palier 04, ne lève jamais)
          ajouter résultat à résultats ; ajouter ligne à trace
      FIN POUR
      ajouter (user, résultats) à messages                                 (UN seul message)
  FIN POUR
  RETOURNER (max_etapes, trace, max_étapes, messages)
```

**Complexité.** La boucle fait au plus `max_etapes` appels au modèle, quel que soit son comportement, et k + 1 appels pour une tâche de k étapes d'outils. Chaque tour exécute autant d'outils que la réponse contient de blocs, et le calcul de la signature coûte un temps proportionnel à la taille des arguments. L'historique gagne deux messages par tour d'outils. Comme il est renvoyé en entier à chaque appel, E appels relisent E² messages en tout : c'est ce carré, et non le calcul local, qui domine le coût en tokens. La mémoire occupée est celle de l'historique et de la trace, linéaire en nombre de tours.

**Du squelette au code.** `ExécuterAgent` est `executer_agent` : la boucle `POUR` est `for etape in range(1, max_etapes + 1)`, les cinq `RETOURNER` sont les cinq dictionnaires rendus, et « tel quel » est `messages.append({"role": "assistant", "content": reponse.content})`. `SignatureAppels` est `signature_appels`, avec `json.dumps(b.input, sort_keys=True)`. `ExécuterAppel` est `executer_appel`, importée du palier 04. Les statuts possibles sont ceux de `STATUTS`.

## Cas d'usage aux Émirats

Les montants sont illustratifs ; les règles citées (plafond d'endettement de 50 % de la CBUAE, TVA de 5 %, parité de 3,6725 AED pour 1 USD) sont celles du parcours.

### Banque — une variante du dossier de crédit, instruite en trois appels

Une banque de détail B-1 de Dubaï laisse son agent pré-instruire les demandes d'hypothèque. Le client C-2 demande 975 000 AED sur 25 ans à 4,5 %. Il gagne 38 500 AED par mois et rembourse déjà 6 500 AED. Au premier appel, le modèle demande `mensualite`, et l'outil rend 5 419,37 AED. Au deuxième, il demande dans la même réponse `ratio_endettement` et `convertir_aed_usd`. La boucle exécute les deux et renvoie les deux résultats dans un seul message : (6 500 + 5 419,37) / 38 500 = 0,3096, recevable, et 5 419,37 / 3,6725 = 1 475,66 USD. Au troisième appel, le modèle rédige la réponse, et la boucle rend `fini` en 3 étapes. La trace garde les trois appels avec leurs arguments : l'analyste refait le calcul sans relire la conversation. Si le modèle avait demandé la conversion dans un quatrième appel, la chaîne aurait eu sept étapes au lieu de six, et sa fiabilité serait passée de 0,8858 à 0,8681 à 0,98 par étape.

### BTP — une erreur d'outil que le modèle corrige

Un groupe de construction fait préparer par son agent le paiement d'une situation de travaux de 120 000 AED HT. Au premier appel, le modèle lit « avoir » dans le courriel du sous-traitant et demande `tva` avec un montant de −120 000. La porte du palier 04 refuse avant tout calcul, et `executer_appel` renvoie au modèle le contenu `ArgumentsInvalides: $.montant_ht : -120000 < minimum 0`, marqué `is_error`. La trace porte `ERREUR $.montant_ht : -120000 < minimum 0`. Au deuxième appel, le modèle redemande avec 120 000 et reçoit 6 000 AED de TVA, soit 126 000 AED TTC. La boucle rend `fini` en 3 étapes, avec deux lignes de trace. Si la boucle avait avalé l'erreur, ou renvoyé une chaîne vide, le modèle aurait cru l'outil réussi et inventé un montant.

### Crypto — un modèle qui oscille, et la facture qu'il aurait coûtée

Une plateforme d'actifs virtuels agréée par la VARA branche un modèle sur ses outils de reporting. Sur une demande ambiguë, il alterne sans fin entre `tva` et `convertir_aed_usd`, avec les mêmes arguments : A, B, A, B. L'arrêt `boucle` ne compare que deux étapes consécutives, et σ₂ ≠ σ₁ : il ne voit rien. La borne `max_etapes=8` arrête le modèle au huitième appel, avec 8 outils exécutés. Le modèle a relu 1 + 3 + … + 15 = 8² = 64 messages, contre 9 pour une tâche normale en trois appels. Si chaque message pèse environ 500 tokens (illustratif), cela fait 32 000 tokens d'entrée au lieu de 4 500 : sept fois plus, pour aucun résultat. C'est pour cela que `max_etapes` doit rester bas et que son dépassement se journalise.

## Travail à faire

1. Ouvre un terminal PowerShell dans le dossier `projet/` du palier, puis vérifie que les tests des paliers 01 à 04 passent déjà et que ceux du palier 05 échouent tous par `NotImplementedError` :

   ```text
   cd "C:\Users\aur95\Documents\AI\AI Agentic\Exercices\05-Boucle-d-Agent\projet"
   python -m unittest -v
   ```

   Si `python` ouvre le Microsoft Store, remplace-le par le chemin complet de l'interpréteur, comme dans le parcours de lecture : `& "C:\Users\aur95\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m unittest -v`.

2. Lis le fichier de tests `tests/test_05_boucle.py` : chaque test est un exemple de la spécification. Repère `outils()`, qui fabrique un registre neuf, et `tva(v)`, qui fabrique une réponse demandant la TVA.

3. Ouvre `agent/boucle.py` et code `executer_agent` dans l'ordre des TODO. D'abord le contrat : la garde sur `max_etapes`, l'historique initial, la boucle bornée et le retour `max_etapes`. Ensuite l'appel au modèle et les trois arrêts de l'API, puis lance :

   ```text
   python -m unittest -v tests.test_05_boucle.TestArrets.test_refus_et_troncature
   ```

4. Ajoute la réponse finale (statut `fini`), puis lance :

   ```text
   python -m unittest -v tests.test_05_boucle.TestArrets.test_reponse_finale_directe tests.test_05_boucle.TestArrets.test_pause_turn_relance_sans_executer
   ```

5. Ajoute l'exécution des outils et le message unique de résultats, puis lance les tests du scénario et des erreurs :

   ```text
   python -m unittest -v tests.test_05_boucle.TestScenarioCredit tests.test_05_boucle.TestErreurs.test_erreur_d_outil_renvoyee_au_modele
   ```

6. Code `signature_appels` et l'arrêt `boucle`, puis lance tout le palier :

   ```text
   python -m unittest -v tests.test_05_boucle
   ```

7. Lance tous les tests, puis la démo :

   ```text
   python -m unittest -v
   python demo.py
   ```

## Critères de réussite

- `python -m unittest -v`, lancé depuis `projet/`, affiche `OK` : les 11 tests du palier 05 et tous les tests des paliers 01 à 04 passent.
- `python demo.py` affiche exactement la sortie ci-dessous, et sa dernière ligne est `OK — palier 05 terminé.`
- Tu sais expliquer, sans le code sous les yeux, pourquoi `refusal` et `max_tokens` sont testés avant de lire le contenu, pourquoi les résultats partent dans un seul message, et pourquoi le nombre d'appels au modèle ne dépasse jamais `max_etapes`.

### Sortie attendue de demo.py

```text
Palier 05 — client C-1 : hypothèque de 1 000 000 AED, revenu 40 000 AED, crédit auto 6 000 AED
  outil mensualite({"principal": 1000000, "taux_annuel": 0.045, "n_mois": 300}) -> {'mensualite_aed': 5558.32}
  outil ratio_endettement({"existantes": 6000, "nouvelle": 5558.32, "revenu": 40000}) -> {'ratio': 0.289, 'recevable': True}
  outil convertir_aed_usd({"montant_aed": 5558.32}) -> {'montant_usd': 1513.5}
  [fini, 3 étapes] Mensualité 5 558,32 AED, soit 1 513,50 USD ; endettement total 28,9 % ≤ 50 % : dossier recevable.
  résultats renvoyés ensemble à l'étape 3 : ['a2', 'a3']
Les arrêts qui protègent la facture :
  même action deux fois : boucle à l'étape 2, 1 outil exécuté
  trois appels différents, max_etapes = 2 : max_etapes, 2 appels au modèle
  refus du modèle : refus à l'étape 1
  erreur d'outil renvoyée au modèle : ERREUR $.montant_ht : -5 < minimum 0
OK — palier 05 terminé.
```

## Pour aller plus loin

1. **Attraper l'oscillation A, B, A, B.** Remplace la comparaison avec la seule étape précédente par un ensemble des signatures déjà vues (converties en tuples, car une liste n'est pas hachable). À quelle étape s'arrête le modèle oscillant du cas crypto ? Réponse : à l'étape 3, avec le statut `boucle` et deux outils exécutés, car σ₃ = σ₁.
2. **Compter les messages relus.** Avec le faux modèle, calcule `sum(len(r["messages"]) for r in llm.requetes)` pour le scénario du crédit, puis pour un modèle qui demande huit outils différents avec `max_etapes=8`. Réponse : 9 puis 64, soit E² dans les deux cas, parce que chaque tour ajoute exactement deux messages.
3. **Trouver le bug.** Dans une variante, la ligne `precedente = signature` est placée avant le test `if signature == precedente`. Que rend le scénario du crédit ? Réponse : `boucle` dès l'étape 1, sans aucun outil exécuté, parce que la comparaison est alors toujours vraie.

## Si tu bloques

La solution est construite pas à pas dans `solutions/progression/`. Chaque fichier part de ce qui est déjà écrit, montre le bloc suivant, l'explique ligne par ligne et dit quel test passe :

- [01 — Le contrat et la boucle bornée](<solutions/progression/01-Le-contrat-et-la-boucle-bornee.md>) : lire les tests, écrire `STATUTS`, la garde, l'historique initial, la boucle `for` et le retour `max_etapes`.
- [02 — Décider, et les arrêts de l'API](<solutions/progression/02-Decider-et-les-arrets-de-l-API.md>) : appeler le modèle, recopier son contenu tel quel, traiter `refusal`, `max_tokens` et `pause_turn`.
- [03 — La réponse finale](<solutions/progression/03-La-reponse-finale.md>) : extraire les blocs `tool_use` et rendre `fini` avec le texte.
- [04 — Agir et observer](<solutions/progression/04-Agir-et-observer.md>) : exécuter chaque appel avec `executer_appel`, remplir la trace, renvoyer tous les résultats dans un seul message.
- [05 — L'arrêt boucle et la signature](<solutions/progression/05-L-arret-boucle-et-la-signature.md>) : `signature_appels`, le tri des clés et la comparaison avec l'étape précédente.
- [06 — Les preuves, vérifiées sur le code](<solutions/progression/06-Les-preuves-verifiees-sur-le-code.md>) : la borne d'appels, les k + 1 appels, les E² messages relus et la fiabilité composée, mesurés avec le faux modèle.
- [07 — Assemblage, tests et démo](<solutions/progression/07-Assemblage-tests-et-demo.md>) : le module complet, tous les tests, la démo et le passage au palier 06.

La solution entière est dans `solutions/agent/boucle.py`. Ses tests et sa démo sont dans `solutions/tests/` et `solutions/demo.py`.
