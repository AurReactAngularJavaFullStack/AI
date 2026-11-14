# Étape 1 — Agent — Définitions fondamentales : ce qu'est un agent IA

> Étape 1 du parcours · Prérequis : [Parcours de lecture](<../00-Parcours-de-Lecture.md>) · Suite : [Softmax et température](<../02-LLM-Softmax-et-Prompts/02-Softmax-Temperature-Prochain-Token.md>)

**Dossier :** 01-Agent  
**Nom du fichier :** 01-Agent-Definitions-Fondamentaux.md  
**Métiers :** AI Engineers, Product Engineers, Forward-Deployed Engineers, AI Agent Ops


Ce fichier est la première rencontre avec un agent. Il pose le vocabulaire, puis construit un agent complet en Python, sans aucune bibliothèque externe, avec un faux modèle de langage qui permet de tout faire tourner hors ligne. Il se termine par la seule formule de la pièce, la fiabilité composée, qui explique pourquoi un agent à vingt étapes échoue bien plus souvent qu'on ne le croit.

## Définitions

### Agent IA

Un agent IA est un programme qui poursuit un objectif en alternant deux choses : un modèle de langage qui **décide** de la prochaine action, et des outils, c'est-à-dire des fonctions ordinaires, qui **agissent** (calculer, chercher, écrire dans un système). Après chaque action, l'agent lit le résultat et décide à nouveau, jusqu'à ce que l'objectif soit atteint ou qu'un critère d'arrêt l'interrompe. Le modèle n'exécute rien lui-même : il produit une réponse qui *demande* l'appel d'un outil, et c'est un programme (le vôtre, ou celui du fournisseur pour les rares outils exécutés côté serveur) qui fait l'appel. Le périmètre d'un agent est donc exactement la liste des outils qu'on lui donne.

### Agent et chatbot : la différence

Un chatbot transforme un message en une réponse : il ne peut ni vérifier un chiffre, ni consulter un système, ni agir, et tout ce qu'il affirme vient de ce que le modèle a mémorisé pendant son entraînement. Un agent possède en plus un objectif explicite, des outils, une mémoire, une trace de ses décisions et des critères d'arrêt. La différence se voit sur une question aussi simple que « combien font 2 000 USD en AED, TVA comprise ? » : le chatbot écrit un nombre plausible, l'agent appelle un outil de conversion puis un outil de TVA, et sa réponse reprend des résultats calculés. Un agent n'est pas pour autant « autonome sans contrôle » : il ne peut faire que ce que ses outils permettent, dans la limite du nombre d'étapes qu'on lui accorde.

### État

L'état est tout ce que l'agent sait à un instant donné : la question, les réponses précédentes du modèle et les résultats des outils. Dans le code de ce fichier, c'est simplement la liste `messages`, qui grandit à chaque tour. Ce qui n'est ni dans cette liste ni dans le prompt système, le modèle ne le voit pas.

### Outil

Un outil est une fonction du programme, décrite au modèle par un nom, une phrase de description et un schéma JSON de ses arguments (étapes [8](<../03-Schemas-Outils-et-Premiere-Evaluation/08-Schemas-Definitions-Fondamentaux.md>) et [12](<../03-Schemas-Outils-et-Premiere-Evaluation/12-Outils-Definitions-Fondamentaux.md>)). Le modèle choisit l'outil et remplit les arguments ; le programme vérifie, exécute et renvoie le résultat. Une règle métier (TVA de 5 %, parité de 3,6725 AED pour 1 USD, plafond d'endettement de 50 %) se code dans un outil et non dans le prompt : elle devient alors testable comme n'importe quelle fonction.

### Mémoire courte et mémoire longue

La mémoire courte est l'historique de la conversation, renvoyé au modèle à chaque appel ; elle est bornée par la taille de la fenêtre de contexte et coûte des tokens à chaque tour. La mémoire longue est un stockage extérieur (base de données, index vectoriel) où l'agent range des souvenirs et d'où il en ressort quelques-uns quand ils sont utiles. Les étapes 16 et 17 montrent comment les classer et les laisser s'effacer.

### Trace

La trace est la liste des actions réellement exécutées : quel outil, avec quels arguments, pour quel résultat. Elle sert à déboguer, à justifier une décision quand un client ou un régulateur demande « sur quelle base ? », et à évaluer l'agent en comparant ses appels à ceux attendus ([étape 59](<../10-Evaluation/59-Evaluation-Formule-Tool-Call-F1.md>)). Un agent sans trace est invérifiable.

### Critère d'arrêt

Une boucle d'agent doit toujours pouvoir s'arrêter. La boucle de ce fichier a cinq statuts de sortie : `fini` (le modèle a donné sa réponse), `max_etapes` (le budget d'étapes est épuisé), `boucle` (le modèle répète exactement la même action), `refus` (le modèle refuse de poursuivre) et `tronque` (la réponse a été coupée par la limite de tokens). Seul `fini` produit une réponse utilisable ; les quatre autres doivent être journalisés et, selon le métier, remontés à un humain.

## La boucle fondamentale

Quel que soit le framework, un agent tourne dans la même boucle en six temps. Chaque temps correspond à une ligne précise de `executer_agent`, plus bas.

1. **Percevoir.** L'agent rassemble son état : le prompt système, l'historique `messages` et la liste des outils disponibles. C'est tout ce que le modèle verra.
2. **Décider.** Le programme appelle le modèle (`llm.create(...)`). Le modèle répond soit par du texte, qui est sa réponse finale, soit par une ou plusieurs demandes d'appel d'outil. C'est ici que joue la softmax de l'étape 2 : chaque token de la réponse, y compris le nom de l'outil choisi, est tiré dans une distribution de probabilités.
3. **Agir.** Le programme exécute chaque outil demandé, avec les arguments fournis par le modèle (`outils[b.name](**b.input)`). C'est le seul moment où quelque chose change dans le monde.
4. **Observer.** Le résultat, ou l'erreur, est emballé dans un bloc `tool_result` qui porte l'identifiant de la demande, pour que le modèle sache quel résultat répond à quelle demande.
5. **Mettre à jour l'état.** La réponse du modèle, puis les résultats des outils, sont ajoutés à `messages` ; tous les résultats d'un même tour partent dans un seul message.
6. **Répéter ou s'arrêter.** La boucle repart au temps 1, sauf si un critère d'arrêt se déclenche.

## Les trois patterns principaux

Ces trois façons d'organiser la boucle sont décrites ici en mots ; leur code, construit sur la même fonction `executer_agent`, est à l'étape 13 ([exemples d'agents](<../03-Schemas-Outils-et-Premiere-Evaluation/13-Agent-Exemples-Cas-Usage.md>)).

**ReAct** (Yao et al., 2022), pour « Reason + Act », fait alterner à chaque tour une courte réflexion écrite, une action, puis l'observation de son résultat. La boucle de ce fichier est un ReAct : le modèle peut écrire une phrase (« je convertis d'abord le montant ») juste avant sa demande d'outil, puis il lit le résultat avant de choisir l'étape suivante. Sa force est de s'adapter à ce qu'il découvre ; sa faiblesse est de pouvoir tourner en rond, d'où les arrêts `boucle` et `max_etapes`.

**Plan-and-Execute** sépare le travail en deux temps : un premier appel au modèle produit un plan complet, c'est-à-dire une liste d'étapes, puis un exécutant déroule ce plan étape par étape, souvent avec du code déterministe ou un modèle moins cher. Le plan est lisible et vérifiable avant toute action, et il coûte moins d'appels au modèle. En contrepartie, si le monde ne correspond pas au plan (un outil échoue, une donnée manque), il faut savoir replanifier.

**Reflexion** (Shinn et al., 2023) ajoute une autocritique : après une tentative ratée, l'agent rédige en quelques phrases ce qui n'a pas marché, garde ce texte en mémoire et le relit au début de la tentative suivante. Il lui faut un signal d'échec fiable (un test qui échoue, un juge, une règle métier violée) ; sans ce signal, il « corrige » des réponses qui étaient justes.

## Architecture hexagonale : le modèle est un port

Dans une architecture hexagonale, l'agent runtime vit dans l'infrastructure ; les règles métier restent dans le domaine. Concrètement, la boucle `executer_agent` ne dépend que d'un **port** : un objet qui possède une méthode `create(system=..., messages=..., tools=...)` et renvoie une réponse ayant `stop_reason` et `content`. Le faux LLM de ce fichier (`FakeLLM`) et l'adaptateur Claude de l'étape 13 (`ClaudeLLM`) sont deux **adaptateurs** de ce même port : on passe de l'un à l'autre sans changer une ligne de la boucle ni des outils. Les règles métier (parité de l'AED, TVA, plafonds de la CBUAE) restent dans les fonctions du domaine, les outils, que l'on teste sans aucun modèle.

Pour un développeur Spring, c'est le découpage habituel d'une interface injectée :

```java
// Le port (côté domaine) et ses deux adaptateurs (côté infrastructure)
public interface LlmPort {
    Reponse create(String system, List<Message> messages, List<ToolSchema> tools);
}
public class FakeLlmAdapter implements LlmPort { /* réponses scriptées, pour les tests */ }
public class ClaudeLlmAdapter implements LlmPort { /* appel HTTP à l'API */ }
```

Python n'a pas besoin de déclarer l'interface : tout objet qui a la bonne méthode convient (typage structurel). `typing.Protocol` permet de l'écrire explicitement pour un vérificateur de types, mais le code tourne sans.

## Construire depuis une feuille blanche

On construit l'agent d'achats d'un groupe de construction à Dubaï. Il dispose de deux outils : `convertir_usd_aed`, qui applique la parité fixe de 3,6725 AED pour 1 USD, et `calculer_tva`, qui applique la TVA de 5 %. Le modèle est remplacé par un faux LLM qui joue un script : on sait donc à l'avance ce que l'agent doit faire, et les `assert` vérifient qu'il le fait. Le programme teste ensuite chacun des arrêts de la boucle, puis calcule les nombres de la formule de fiabilité démontrée dans la section suivante.

### Déroulé, ligne par ligne

**`Bloc` et `Reponse`** sont deux `dataclass`, l'équivalent Python des `record` de Java. Une `Reponse` contient un `stop_reason` et une liste de blocs `content`. Un bloc de type `"text"` porte du texte dans `.text` ; un bloc de type `"tool_use"` porte une demande d'outil : `.id` (identifiant unique de la demande), `.name` (l'outil) et `.input` (les arguments, un dictionnaire). C'est exactement la forme des réponses de l'API Claude, ce qui permet de brancher le vrai modèle sans toucher à la boucle.

- `input: dict = field(default_factory=dict)` : chaque bloc reçoit son propre dictionnaire vide. Python refuse `input: dict = {}` dans une `dataclass`, parce que ce dictionnaire unique serait partagé par tous les blocs.
- Les cinq valeurs de `stop_reason` : `"end_turn"` (le modèle a fini son tour), `"tool_use"` (il attend le résultat d'outils), `"max_tokens"` (sa réponse a été coupée par la limite de tokens de la requête), `"refusal"` (il refuse de poursuivre) et `"pause_turn"` (l'API a mis en pause un tour long ; on renvoie la conversation telle quelle pour qu'il continue).

**`texte(t)` et `appel_outil(nom, arguments, id_)`** fabriquent ces blocs en une ligne, pour écrire des scripts lisibles. Le paramètre s'appelle `id_` parce que `id` est une fonction intégrée de Python.

**`FakeLLM`** est un bouchon de test, comme un `when(...).thenReturn(r1, r2, r3)` de Mockito. Il ignore ce qu'on lui envoie et renvoie la réponse suivante du script ; `self.appels` compte les appels. L'étoile dans `create(self, *, system, messages, tools)` rend les paramètres nommés obligatoires, comme dans le vrai SDK. Si la boucle demande une réponse de plus que prévu, `RuntimeError` arrête le test au lieu d'inventer une suite.

**`executer_agent(llm, system, question, outils, schemas, max_etapes=8)`**, avec les valeurs du premier scénario (2 000 USD HT à convertir, puis à taxer).

- `messages = [{"role": "user", "content": question}]` : l'état initial, un seul message. C'est ce que le modèle perçoit au premier tour.
- `for etape in range(1, max_etapes + 1)` : au plus 8 tours ; ici, `etape` vaudra 1, 2 puis 3.
- `reponse = llm.create(system=system, messages=messages, tools=schemas)` : le temps « décider ». Au tour 1, le script renvoie un bloc de texte (« Je convertis d'abord le montant en AED. ») et une demande `convertir_usd_aed` avec `{"montant_usd": 2000}` et l'identifiant `"t1"`.
- `messages.append({"role": "assistant", "content": reponse.content})` : la réponse est recopiée telle quelle. Avec le vrai modèle, elle peut contenir des blocs de réflexion qui doivent revenir intacts au tour suivant.
- Les trois tests sur `stop_reason` : `"refusal"` renvoie le statut `refus` ; `"max_tokens"` renvoie `tronque`, parce qu'une réponse coupée ne doit jamais servir de réponse finale ; `"pause_turn"` fait `continue`, c'est-à-dire un nouvel appel avec l'historique inchangé. La docstring parle de « trois arrêts » : ce sont les trois arrêts propres à l'agent (`fini`, `boucle`, `max_etapes`) ; `refus` et `tronque` viennent de l'API.
- `appels = [b for b in reponse.content if b.type == "tool_use"]` : la liste des demandes d'outils du tour. Au tour 1, elle contient un bloc.
- `if reponse.stop_reason == "end_turn" or not appels` : s'il n'y a rien à exécuter, le texte est la réponse finale. Au tour 3, le script renvoie `"end_turn"` : le statut est `fini`, en 3 étapes.
- `signature = [(b.name, json.dumps(b.input, sort_keys=True)) for b in appels]` : au tour 1, `[("convertir_usd_aed", '{"montant_usd": 2000}')]`. `sort_keys=True` donne la même chaîne pour `{"a": 1, "b": 2}` et `{"b": 2, "a": 1}`.
- `if signature == precedente` : même outil et mêmes arguments qu'au tour précédent, le modèle tourne en rond, d'où le statut `boucle`. Au tour 1, `precedente` vaut `None`.
- `sortie = outils[b.name](**b.input)` : le temps « agir ». `**` déplie le dictionnaire en arguments nommés : `convertir_usd_aed(montant_usd=2000)`, qui renvoie 7345.0.
- `resultats.append({"type": "tool_result", "tool_use_id": b.id, ...})` : le temps « observer ». Le résultat est sérialisé en JSON (`"7345.0"`) et rattaché à la demande `"t1"`.
- `except Exception as e` : si l'outil lève une exception, le bloc porte `"is_error": True` et le message `"ValueError: montant négatif : -2000"` (scénario 2). Le modèle voit l'erreur et peut corriger ses arguments ; une erreur avalée en silence lui ferait croire que l'outil a réussi.
- `messages.append({"role": "user", "content": resultats})` : le temps « mettre à jour ». Tous les résultats du tour partent dans **un seul** message. Au tour 2, le modèle reçoit donc 3 messages ; au tour 3, il en reçoit 5.
- `return {"statut": "max_etapes", ...}` : si la boucle épuise ses tours sans réponse finale, elle s'arrête quand même.

**`convertir_usd_aed(montant_usd)`** renvoie `round(montant_usd * AED_PAR_USD, 2)` : pour 2 000 USD, 2 000 × 3,6725 = 7 345,00 AED, arrondi au fils (1 AED = 100 fils). Un montant négatif lève `ValueError`.

**`calculer_tva(montant_ht_aed)`** appelle la fonction commune `tva()` du parcours : 7 345 × 0,05 = 367,25 AED de TVA, donc 7 712,25 AED TTC. L'outil renvoie un dictionnaire, que la boucle sérialise en JSON pour le modèle.

**`SCHEMAS`** est ce que le modèle voit des outils : un nom, une description et le schéma JSON des arguments, au format de l'API. Le faux LLM ne les lit pas, mais un vrai modèle choisit son outil d'après eux ; `"strict": True` demande à l'API de garantir des arguments conformes au schéma (étapes 8 et 12).

**`EspionLLM`** hérite de `FakeLLM`, comme un `spy` de Mockito : même comportement, mais il note `len(messages)` à chaque appel et garde une référence à la liste `messages`. Après le premier scénario, `tailles` vaut `[1, 3, 5]` : l'état grossit de deux messages par tour, une réponse du modèle et un message de résultats.

**Les fonctions de la formule**, démontrées dans la section suivante.

- `fiabilite_composee(probas)` renvoie `math.prod(probas)`, le produit des pᵢ, après avoir refusé une liste vide ou une probabilité hors de [0, 1].
- `bornes_sans_independance(probas)` renvoie la plus petite et la plus grande valeur possibles de la probabilité de succès quand on ne suppose rien sur la corrélation des erreurs : `max(0.0, 1.0 - sum(1.0 - p for p in probas))` et `min(probas)`.
- `etapes_max(p, cible)` ajoute des étapes tant que pⁿ⁺¹ reste au-dessus de la cible ; `p_min_par_etape(n, cible)` renvoie `cible ** (1.0 / n)`.
- `simuler(p, n, essais)` fait tourner des agents fictifs : `rng.random() < p` est vrai avec la probabilité p, et `all(...)` n'est vrai que si les n étapes réussissent. La graine fixe (`random.Random(42)`) rend la sortie identique à chaque exécution.

**`main()`**, bloc par bloc.

1. Le scénario complet : deux outils, puis la réponse finale. On vérifie le statut, le nombre d'étapes, le nom et le résultat de chaque outil, la taille de l'historique à chaque appel, l'alternance des rôles `user` et `assistant`, et le contenu exact du premier `tool_result`.
2. Le modèle demande la conversion de −2 000 USD : l'outil lève `ValueError`, la boucle renvoie l'erreur au modèle avec `is_error`, et le modèle redemande avec 2 000. L'agent finit normalement.
3. Un scénario par arrêt, avec le nombre d'étapes et d'outils exécutés attendus : `fini` en 1 étape ; `max_etapes` après 3 conversions différentes avec `max_etapes=3` ; `boucle` à la 2e étape, quand la même conversion de 5 USD revient, alors qu'un seul outil a été exécuté ; `refus` et `tronque` dès la 1re étape. Un dernier scénario vérifie que `pause_turn` relance simplement le modèle.
4. Les nombres de la démonstration : 0,95¹⁰, 0,95²⁰, 0,99²⁰, l'agent à trois étapes, les bornes sans indépendance, la simulation, pₘᵢₙ et nₘₐₓ. La dernière boucle vérifie que les entrées invalides sont refusées.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`texte(t)`** — Cette petite fonction est le copiste du théâtre de marionnettes que joue le faux modèle : elle reçoit une chaîne `t`, la phrase qu'un acteur doit prononcer, et la range dans un `Bloc` de type `"text"` dont le champ `.text` porte exactement ces mots, les autres champs restant vides. Elle ne vérifie rien et ne lève aucune exception ; elle renvoie ce bloc tout prêt, ce qui permet d'écrire dans `main` des scripts lisibles comme « Je convertis d'abord le montant en AED. » au lieu d'empiler des constructeurs, et c'est ce même texte que la boucle recolle pour former la réponse finale.

**`appel_outil(nom, arguments, id_)`** — Celle-ci rédige le bon de commande que le modèle tend au magasinier : elle reçoit le nom de l'outil voulu, le dictionnaire de ses arguments et un identifiant de demande, et elle renvoie un `Bloc` de type `"tool_use"` dont `.name`, `.input` et `.id` reprennent ces trois valeurs, exactement comme une réponse de l'API Claude. Le paramètre s'appelle `id_` parce que `id` est déjà une fonction intégrée de Python. Dans le premier scénario, elle fabrique la demande `convertir_usd_aed` avec `{"montant_usd": 2000}` et l'identifiant `"t1"`, que la boucle exécutera puis rattachera à son résultat grâce à cet identifiant.

**`FakeLLM.__init__(script)`** — Le constructeur du faux modèle ressemble à un souffleur qui reçoit, avant le lever de rideau, la liste des répliques qu'il devra murmurer une à une : il prend la liste `script` des objets `Reponse` prévus, en garde une copie avec `list(script)` pour qu'une modification ultérieure de la liste d'origine ne change pas la pièce en cours, et met le compteur `self.appels` à zéro. Il ne renvoie rien et ne lève rien ; il prépare seulement un adaptateur du port LLM entièrement déterministe et gratuit, sur lequel reposent tous les scénarios de `main`.

**`FakeLLM.create(system, messages, tools)`** — C'est la méthode que la boucle prend pour un vrai modèle : elle reçoit, en arguments nommés obligatoires grâce à l'étoile de sa signature, le prompt système, l'historique des messages et les schémas des outils, mais, comme un acteur qui connaît son texte par cœur, elle n'en lit aucun. Si le compteur `appels` a déjà atteint la longueur du script, elle lève `RuntimeError` avec le message « script épuisé », pour qu'un test qui demande une réponse de trop échoue bruyamment au lieu d'inventer une suite ; sinon elle prend la réplique suivante, incrémente le compteur et renvoie cette `Reponse`.

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — Voici le cœur du fichier, un chef de chantier qui fait tourner la boucle percevoir, décider, agir, observer : il reçoit le modèle (tout objet doté d'une méthode `create`), le prompt système, la question, le dictionnaire des outils, leurs schémas et un budget de tours, 8 par défaut. À chaque tour, il appelle le modèle, recopie sa réponse dans `messages`, sort avec le statut `refus` ou `tronque` si le `stop_reason` vaut `"refusal"` ou `"max_tokens"`, relance simplement après un `"pause_turn"`, et renvoie `fini` avec le texte recollé quand il n'y a plus d'outil à appeler. Sinon, il compare la signature des demandes à celle du tour précédent pour renvoyer `boucle` en cas de répétition, exécute chaque outil, transforme toute exception en `tool_result` marqué `is_error`, consigne la trace et range tous les résultats dans un seul message ; au bout du budget, il renvoie `max_etapes`. Le dictionnaire renvoyé porte toujours le statut, la trace et le nombre d'étapes, et c'est lui que `main` contrôle scénario après scénario, par exemple `fini` en 3 étapes pour les 2 000 USD.

**`tva(montant_ht, taux)`** — Cette fonction commune du parcours tient le rôle du percepteur le plus sobre qui soit : elle reçoit un montant hors taxes et un taux, 0,05 par défaut pour la TVA standard des Émirats, et renvoie simplement leur produit, sans arrondi ni vérification de signe. Sa docstring rappelle les cas particuliers du droit fiscal local (loyer résidentiel exonéré, première livraison d'un bien résidentiel au taux zéro), que la fonction elle-même ne traite pas. Dans ce programme, c'est `calculer_tva` qui l'appelle : sur 7 345 AED hors taxes, elle donne 367,25 AED de taxe.

**`convertir_usd_aed(montant_usd)`** — Premier outil de l'agent, c'est le guichetier d'un bureau de change qui n'a qu'un seul tarif affiché au mur : il reçoit un montant en dollars, refuse tout montant négatif en levant `ValueError` avec le message « montant négatif », puis multiplie par la parité fixe `AED_PAR_USD` de 3,6725 et arrondit au fils, c'est-à-dire au centième de dirham. Il renvoie un flottant, 7345.0 pour 2 000 USD. Dans le deuxième scénario, c'est son refus de −2 000 qui part vers le modèle sous la forme `"ValueError: montant négatif : -2000"`, ce qui permet au faux modèle de se corriger au tour suivant.

**`calculer_tva(montant_ht_aed)`** — Second outil, c'est le comptable qui établit le bas de facture : il reçoit un montant hors taxes en dirhams, lève `ValueError` s'il est négatif, demande la taxe à `tva`, l'arrondit au centième, puis additionne et arrondit à nouveau le total. Il renvoie un dictionnaire à trois clés, `ht`, `tva` et `ttc`, que la boucle sérialise en JSON pour le modèle : pour 7 345 AED, on obtient 367,25 AED de TVA et 7 712,25 AED TTC, les nombres que `main` compare ensuite à la deuxième entrée de la trace.

**`EspionLLM.__init__(script)`** — Le constructeur de l'espion commence par appeler celui de `FakeLLM`, si bien que le script et le compteur d'appels sont installés exactement de la même façon, puis il ouvre deux carnets vides, comme un inspecteur qui s'assoit au fond de la salle avec son calepin : `tailles`, qui recevra le nombre de messages vus à chaque appel, et `historique`, qui gardera une référence à la liste `messages` elle-même. Il ne renvoie rien ; il fabrique un faux modèle qui joue la même pièce mais observe ce que la boucle lui transmet.

**`EspionLLM.create(system, messages, tools)`** — Cette méthode note avant d'agir : elle reçoit les mêmes arguments nommés que la version de `FakeLLM`, ajoute `len(messages)` à la liste `tailles`, garde dans `historique` une référence à la liste que la boucle continue de compléter, puis délègue à `super().create`, qui renvoie la réplique suivante ou lève `RuntimeError` si le script est épuisé. Comme un greffier qui compte les pièces du dossier à chaque audience, elle permet à `main` de vérifier que l'état grossit de deux messages par tour, `[1, 3, 5]` dans le premier scénario, et que les rôles alternent bien entre `user` et `assistant`.

**`fiabilite_composee(probas)`** — Cette fonction est l'actuaire de la chaîne d'étapes : elle reçoit la liste des probabilités de réussite pᵢ, lève `ValueError` si la liste est vide ou si une valeur sort de l'intervalle [0, 1], puis renvoie leur produit calculé par `math.prod`, c'est-à-dire la probabilité que toutes les étapes réussissent quand elles sont indépendantes. Elle donne 0,5987 pour dix étapes à 0,95, 0,3585 pour vingt, 0,8179 pour vingt étapes à 0,99, et 0,941094 pour l'agent à trois étapes (0,99, 0,98, 0,97) ; la dernière boucle de `main` vérifie qu'elle refuse bien `[]`, `[1.2]` et `[0.9, -0.1]`.

**`bornes_sans_independance(probas)`** — Celle-ci raisonne comme un expert prudent qui refuse de supposer que les pannes sont indépendantes : elle reçoit la même liste de probabilités, la fait d'abord contrôler par `fiabilite_composee` sans garder le produit, ce qui lui transmet les mêmes `ValueError`, puis renvoie un couple de bornes. La borne basse vaut 1 moins la somme des probabilités d'échec 1 − pᵢ, ramenée à 0 si elle devient négative ; la borne haute est la plus petite des pᵢ, le maillon le plus fragile. Pour dix étapes à 0,95, elle renvoie 0,5 et 0,95, qui encadrent bien 0,5987, et pour vingt étapes la borne basse tombe à 0.

**`etapes_max(p, cible)`** — Cette fonction est un alpiniste qui ajoute des longueurs de corde tant que la chaîne tient : elle reçoit la fiabilité p d'une étape et la fiabilité visée pour l'agent entier, lève `ValueError` si l'une des deux n'est pas strictement comprise entre 0 et 1, puis part de n = 0 et l'augmente tant que p puissance n + 1 reste supérieur ou égal à la cible. Elle renvoie ce plus grand n entier sans passer par un logarithme : 2 étapes au plus pour p = 0,95 et une cible de 0,9, 10 étapes pour p = 0,99, ce que `main` recoupe avec la formule ⌊ln c / ln p⌋.

**`p_min_par_etape(n, cible)`** — C'est le calcul inverse, celui de l'ingénieur qui connaît la longueur du pont et cherche la solidité de chaque pile : la fonction reçoit un nombre d'étapes n et une fiabilité visée, lève `ValueError` si n est inférieur à 1 ou si la cible n'est pas strictement entre 0 et 1, et renvoie la racine n-ième de la cible, `cible ** (1.0 / n)`. C'est la plus petite fiabilité par étape qui garantit pⁿ ≥ c ; pour tenir 90 % sur 20 étapes, elle donne 0,9947, valeur vérifiée par un `assert` de `main`.

**`simuler(p, n, essais, graine)`** — Cette fonction organise une grande répétition générale : elle reçoit la fiabilité p d'une étape, le nombre n d'étapes, le nombre d'agents fictifs à faire tourner et une graine, 42 par défaut, qui fixe le générateur `random.Random` pour que la sortie soit identique à chaque exécution. Pour chaque agent, elle lance n dés, chaque étape réussissant si `rng.random() < p`, et ne compte l'agent comme réussi que si `all` confirme que toutes ses étapes ont réussi ; elle renvoie la fréquence des réussites. Avec 20 000 agents à 10 étapes de 0,95, elle donne 0,5990, que `main` exige à moins de 0,015 de la valeur théorique 0,5987.

**`main()`** — C'est le metteur en scène qui fait jouer quatre actes et vérifie chaque réplique : il lance d'abord le scénario complet avec un `EspionLLM`, deux outils puis la réponse finale, et contrôle le statut `fini` en 3 étapes, la trace, les tailles `[1, 3, 5]`, l'alternance des rôles et le premier `tool_result`. Il rejoue ensuite une conversion de −2 000 USD pour montrer que l'erreur revient au modèle avec `is_error`, puis un scénario par statut d'arrêt, avec les nombres d'étapes et d'outils attendus, et une relance après `pause_turn`. Le dernier acte calcule les nombres de la fiabilité composée, les bornes, la simulation, pₘᵢₙ et nₘₐₓ, et vérifie que les entrées invalides sont refusées ; la ligne « OK — toutes les vérifications sont passées. » n'apparaît que si tous les `assert` ont tenu.

**`conv(montant, id_)`** — Cette fonction interne, définie à l'intérieur de `main` au début de la troisième partie, est un tampon encreur qui évite de recopier toujours la même demande : elle reçoit un montant en dollars et un identifiant, et renvoie, par `appel_outil`, un bloc `tool_use` qui demande `convertir_usd_aed` avec ce montant. Elle sert à écrire en une ligne les scripts des arrêts : trois conversions différentes, de 1, 2 et 3 USD, pour épuiser le budget dans le scénario `max_etapes`, et deux fois la conversion de 5 USD, sous les identifiants `"t1"` et `"t2"`, pour déclencher le statut `boucle` dès la deuxième étape.

```python
"""Étape 1 — un agent minimal depuis une feuille blanche : port LLM, faux LLM, boucle, arrêts, fiabilité composée."""
import json
import math
import random
import sys
from dataclasses import dataclass, field

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- port LLM (code canonique du parcours)
@dataclass
class Bloc:
    type: str                      # "text" ou "tool_use"
    text: str = ""
    id: str = ""
    name: str = ""
    input: dict = field(default_factory=dict)


@dataclass
class Reponse:
    stop_reason: str               # "end_turn", "tool_use", "max_tokens", "refusal", "pause_turn"
    content: list


def texte(t: str) -> Bloc:
    return Bloc(type="text", text=t)


def appel_outil(nom: str, arguments: dict, id_: str) -> Bloc:
    return Bloc(type="tool_use", id=id_, name=nom, input=arguments)


class FakeLLM:
    """Faux LLM scripté : renvoie les réponses prévues, dans l'ordre. Déterministe, gratuit."""

    def __init__(self, script: list):
        self.script = list(script)
        self.appels = 0

    def create(self, *, system: str, messages: list, tools: list) -> Reponse:
        if self.appels >= len(self.script):
            raise RuntimeError("script épuisé : le faux LLM n'a plus de réponse prévue")
        reponse = self.script[self.appels]
        self.appels += 1
        return reponse


def executer_agent(llm, system: str, question: str, outils: dict, schemas: list, max_etapes: int = 8) -> dict:
    """Boucle percevoir → décider → agir → observer, avec trois arrêts."""
    messages = [{"role": "user", "content": question}]
    trace = []
    precedente = None
    for etape in range(1, max_etapes + 1):
        reponse = llm.create(system=system, messages=messages, tools=schemas)
        messages.append({"role": "assistant", "content": reponse.content})   # tel quel, sans retouche
        if reponse.stop_reason == "refusal":
            return {"statut": "refus", "trace": trace, "etapes": etape}
        if reponse.stop_reason == "max_tokens":
            return {"statut": "tronque", "trace": trace, "etapes": etape}
        if reponse.stop_reason == "pause_turn":
            continue
        appels = [b for b in reponse.content if b.type == "tool_use"]
        if reponse.stop_reason == "end_turn" or not appels:
            final = "".join(b.text for b in reponse.content if b.type == "text")
            return {"statut": "fini", "reponse": final, "trace": trace, "etapes": etape}
        signature = [(b.name, json.dumps(b.input, sort_keys=True)) for b in appels]
        if signature == precedente:           # même action, mêmes arguments, deux fois de suite
            return {"statut": "boucle", "trace": trace, "etapes": etape}
        precedente = signature
        resultats = []
        for b in appels:
            try:
                sortie = outils[b.name](**b.input)
                resultats.append({"type": "tool_result", "tool_use_id": b.id,
                                  "content": json.dumps(sortie, ensure_ascii=False)})
                trace.append((b.name, b.input, sortie))
            except Exception as e:            # l'erreur repart vers le modèle, elle n'est pas avalée
                resultats.append({"type": "tool_result", "tool_use_id": b.id,
                                  "content": f"{type(e).__name__}: {e}", "is_error": True})
                trace.append((b.name, b.input, f"ERREUR {e}"))
        messages.append({"role": "user", "content": resultats})   # tous les résultats dans UN message
    return {"statut": "max_etapes", "trace": trace, "etapes": max_etapes}


def tva(montant_ht: float, taux: float = 0.05) -> float:
    """TVA standard des EAU : 5 %. (Loyer résidentiel exonéré ; première livraison d'un bien résidentiel au taux zéro.)"""
    return montant_ht * taux


# ---------------------------------------------------------------- les deux outils de l'agent
AED_PAR_USD = 3.6725   # parité fixe du dirham


def convertir_usd_aed(montant_usd: float) -> float:
    """Outil 1 : USD -> AED au taux fixe, arrondi au fils (centième de dirham)."""
    if montant_usd < 0:
        raise ValueError(f"montant négatif : {montant_usd}")
    return round(montant_usd * AED_PAR_USD, 2)


def calculer_tva(montant_ht_aed: float) -> dict:
    """Outil 2 : TVA de 5 % et total TTC, en AED."""
    if montant_ht_aed < 0:
        raise ValueError(f"montant négatif : {montant_ht_aed}")
    taxe = round(tva(montant_ht_aed), 2)
    return {"ht": montant_ht_aed, "tva": taxe, "ttc": round(montant_ht_aed + taxe, 2)}


OUTILS = {"convertir_usd_aed": convertir_usd_aed, "calculer_tva": calculer_tva}

# Ce que le modèle voit des outils : un nom, une description, un schéma JSON des arguments (étapes 8 et 12).
SCHEMAS = [
    {"name": "convertir_usd_aed", "description": "Convertit un montant en USD vers l'AED au taux fixe de 3,6725.",
     "input_schema": {"type": "object", "properties": {"montant_usd": {"type": "number"}},
                      "required": ["montant_usd"], "additionalProperties": False}, "strict": True},
    {"name": "calculer_tva", "description": "Calcule la TVA de 5 % et le total TTC d'un montant HT en AED.",
     "input_schema": {"type": "object", "properties": {"montant_ht_aed": {"type": "number"}},
                      "required": ["montant_ht_aed"], "additionalProperties": False}, "strict": True},
]

SYSTEM = ("Tu es l'assistant achats d'un groupe de construction à Dubaï. "
          "Tu ne calcules jamais de tête : tu appelles les outils, puis tu réponds en AED.")


class EspionLLM(FakeLLM):
    """Comme un spy Mockito : même comportement que FakeLLM, mais note ce que la boucle lui envoie."""

    def __init__(self, script: list):
        super().__init__(script)
        self.tailles = []          # nombre de messages reçus à chaque appel
        self.historique = []       # la liste messages elle-même (la boucle la complète ensuite)

    def create(self, *, system: str, messages: list, tools: list) -> Reponse:
        self.tailles.append(len(messages))
        self.historique = messages
        return super().create(system=system, messages=messages, tools=tools)


# ---------------------------------------------------------------- la formule : fiabilité composée
def fiabilite_composee(probas: list[float]) -> float:
    """P(toutes les étapes réussissent) = p_1 × p_2 × … × p_n, si les étapes sont indépendantes."""
    if not probas:
        raise ValueError("il faut au moins une étape")
    if any(not 0.0 <= p <= 1.0 for p in probas):
        raise ValueError("chaque p_i doit être dans [0, 1]")
    return math.prod(probas)


def bornes_sans_independance(probas: list[float]) -> tuple[float, float]:
    """Vrai même si les erreurs sont corrélées : max(0, 1 − Σ(1 − p_i)) <= P(succès) <= min(p_i)."""
    fiabilite_composee(probas)                          # mêmes vérifications d'entrée
    return max(0.0, 1.0 - sum(1.0 - p for p in probas)), min(probas)


def etapes_max(p: float, cible: float) -> int:
    """Plus grand n tel que p^n >= cible."""
    if not (0.0 < p < 1.0 and 0.0 < cible < 1.0):
        raise ValueError("il faut 0 < p < 1 et 0 < cible < 1")
    n = 0
    while p ** (n + 1) >= cible:
        n += 1
    return n


def p_min_par_etape(n: int, cible: float) -> float:
    """Plus petite fiabilité par étape qui garantit p^n >= cible : p = cible^(1/n)."""
    if n < 1 or not 0.0 < cible < 1.0:
        raise ValueError("il faut n >= 1 et 0 < cible < 1")
    return cible ** (1.0 / n)


def simuler(p: float, n: int, essais: int, graine: int = 42) -> float:
    """Fait tourner `essais` agents de n étapes ; chaque étape tire son propre dé (indépendance)."""
    rng = random.Random(graine)
    reussis = sum(1 for _ in range(essais) if all(rng.random() < p for _ in range(n)))
    return reussis / essais


def main() -> None:
    print("1. Boucle complète : 2 000 USD HT -> AED TTC")
    script = [
        Reponse("tool_use", [texte("Je convertis d'abord le montant en AED."),
                             appel_outil("convertir_usd_aed", {"montant_usd": 2000}, "t1")]),
        Reponse("tool_use", [appel_outil("calculer_tva", {"montant_ht_aed": 7345.0}, "t2")]),
        Reponse("end_turn", [texte("2 000 USD = 7 345,00 AED HT ; TVA 5 % = 367,25 AED ; total TTC = 7 712,25 AED.")]),
    ]
    espion = EspionLLM(script)
    question = "Un loueur de grues de Dubaï facture 2 000 USD HT. Combien payons-nous en AED, TVA comprise ?"
    r = executer_agent(espion, SYSTEM, question, OUTILS, SCHEMAS)
    for nom, args, sortie in r["trace"]:
        print(f"  outil {nom}({args}) -> {sortie}")
    print(f"  statut = {r['statut']} en {r['etapes']} étapes ; messages reçus par le modèle : {espion.tailles}")
    print(f"  réponse : {r['reponse']}")
    assert r["statut"] == "fini" and r["etapes"] == 3 and espion.appels == 3
    assert [nom for nom, _, _ in r["trace"]] == ["convertir_usd_aed", "calculer_tva"]
    assert r["trace"][0][2] == 7345.0
    assert r["trace"][1][2] == {"ht": 7345.0, "tva": 367.25, "ttc": 7712.25}
    assert espion.tailles == [1, 3, 5]                       # l'état grossit de 2 messages par tour
    roles = [m["role"] for m in espion.historique]
    assert roles == ["user", "assistant", "user", "assistant", "user", "assistant"]
    resultat_t1 = espion.historique[2]["content"][0]
    assert resultat_t1["tool_use_id"] == "t1" and resultat_t1["content"] == "7345.0"

    print("2. Une erreur d'outil repart vers le modèle, qui se corrige")
    script = [
        Reponse("tool_use", [appel_outil("convertir_usd_aed", {"montant_usd": -2000}, "t1")]),
        Reponse("tool_use", [appel_outil("convertir_usd_aed", {"montant_usd": 2000}, "t2")]),
        Reponse("end_turn", [texte("7 345,00 AED HT.")]),
    ]
    espion = EspionLLM(script)
    r = executer_agent(espion, SYSTEM, question, OUTILS, SCHEMAS)
    for nom, args, sortie in r["trace"]:
        print(f"  outil {nom}({args}) -> {sortie}")
    assert r["statut"] == "fini" and r["trace"][0][2] == "ERREUR montant négatif : -2000"
    erreur = espion.historique[2]["content"][0]
    assert erreur["is_error"] is True and erreur["content"] == "ValueError: montant négatif : -2000"

    print("3. Les arrêts de la boucle")

    def conv(montant: float, id_: str) -> Bloc:
        return appel_outil("convertir_usd_aed", {"montant_usd": montant}, id_)

    scenarios = {
        "fini": ([Reponse("end_turn", [texte("Rien à calculer.")])], 8),
        "max_etapes": ([Reponse("tool_use", [conv(m, f"t{m}")]) for m in (1, 2, 3)], 3),
        "boucle": ([Reponse("tool_use", [conv(5, "t1")]), Reponse("tool_use", [conv(5, "t2")])], 8),
        "refus": ([Reponse("refusal", [])], 8),
        "tronque": ([Reponse("max_tokens", [texte("Le total TTC est de 7 7")])], 8),
    }
    attendus = {"fini": (1, 0), "max_etapes": (3, 3), "boucle": (2, 1), "refus": (1, 0), "tronque": (1, 0)}
    for statut, (scr, limite) in scenarios.items():
        r = executer_agent(FakeLLM(scr), SYSTEM, question, OUTILS, SCHEMAS, max_etapes=limite)
        print(f"  {statut:<10} : {r['etapes']} étape(s), {len(r['trace'])} appel(s) d'outil exécuté(s)")
        assert r["statut"] == statut and (r["etapes"], len(r["trace"])) == attendus[statut]
    r = executer_agent(FakeLLM([Reponse("pause_turn", [texte("Je cherche…")]), Reponse("end_turn", [texte("Fait.")])]),
                       SYSTEM, question, OUTILS, SCHEMAS)
    assert r["statut"] == "fini" and r["etapes"] == 2       # pause_turn : on relance, sans compter d'outil

    print("4. Fiabilité composée")
    puissances = []
    for (p, n), attendu in {(0.95, 10): 0.5987, (0.95, 20): 0.3585, (0.99, 20): 0.8179}.items():
        valeur = fiabilite_composee([p] * n)
        puissances.append(f"{p}^{n} = {valeur:.4f}")
        assert round(valeur, 4) == attendu
    print("  " + " ; ".join(puissances))
    agent_3_etapes = fiabilite_composee([0.99, 0.98, 0.97])
    outils_fusionnes = fiabilite_composee([0.99, 0.97])
    print(f"  agent à 3 étapes (0.99, 0.98, 0.97) : {agent_3_etapes:.4f} ; "
          f"deux outils fusionnés en un (0.99, 0.97) : {outils_fusionnes:.4f}")
    assert round(agent_3_etapes, 6) == 0.941094 and round(outils_fusionnes, 4) == 0.9603
    bas, haut = bornes_sans_independance([0.95] * 10)
    print(f"  sans hypothèse d'indépendance, p = 0.95 et n = 10 : entre {bas:.4f} et {haut:.4f}")
    assert (round(bas, 4), haut) == (0.5, 0.95) and bas <= fiabilite_composee([0.95] * 10) <= haut
    assert bornes_sans_independance([0.95] * 20)[0] == 0.0
    frequence = simuler(0.95, 10, 20_000)
    print(f"  20 000 agents simulés à 10 étapes de p = 0.95 : {frequence:.4f} réussissent")
    assert abs(frequence - 0.5987) < 0.015
    print(f"  pour 90 % sur 20 étapes, il faut p >= {p_min_par_etape(20, 0.9):.4f} par étape")
    print(f"  avec p = 0.95 : {etapes_max(0.95, 0.9)} étapes au plus ; avec p = 0.99 : {etapes_max(0.99, 0.9)}")
    assert round(p_min_par_etape(20, 0.9), 4) == 0.9947
    assert etapes_max(0.95, 0.9) == 2 == math.floor(math.log(0.9) / math.log(0.95))
    assert etapes_max(0.99, 0.9) == 10 == math.floor(math.log(0.9) / math.log(0.99))
    for invalide in ([], [1.2], [0.9, -0.1]):
        try:
            fiabilite_composee(invalide)
        except ValueError:
            pass
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Boucle complète : 2 000 USD HT -> AED TTC
  outil convertir_usd_aed({'montant_usd': 2000}) -> 7345.0
  outil calculer_tva({'montant_ht_aed': 7345.0}) -> {'ht': 7345.0, 'tva': 367.25, 'ttc': 7712.25}
  statut = fini en 3 étapes ; messages reçus par le modèle : [1, 3, 5]
…
  outil convertir_usd_aed({'montant_usd': -2000}) -> ERREUR montant négatif : -2000
…
3. Les arrêts de la boucle
  fini       : 1 étape(s), 0 appel(s) d'outil exécuté(s)
  max_etapes : 3 étape(s), 3 appel(s) d'outil exécuté(s)
  boucle     : 2 étape(s), 1 appel(s) d'outil exécuté(s)
  refus      : 1 étape(s), 0 appel(s) d'outil exécuté(s)
  tronque    : 1 étape(s), 0 appel(s) d'outil exécuté(s)
4. Fiabilité composée
  0.95^10 = 0.5987 ; 0.95^20 = 0.3585 ; 0.99^20 = 0.8179
  agent à 3 étapes (0.99, 0.98, 0.97) : 0.9411 ; deux outils fusionnés en un (0.99, 0.97) : 0.9603
  sans hypothèse d'indépendance, p = 0.95 et n = 10 : entre 0.5000 et 0.9500
  20 000 agents simulés à 10 étapes de p = 0.95 : 0.5990 réussissent
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un agent n'a rien de magique. C'est une boucle `for` qui appelle un modèle, exécute les outils qu'il demande, lui rend les résultats et s'arrête pour une raison toujours connue. Le faux LLM permet de tester cette boucle comme n'importe quel service, avant de dépenser le moindre token.

## Formule naturelle : la fiabilité composée

Un agent qui enchaîne n étapes (choisir le bon outil, lui passer les bons arguments, lire correctement le résultat, rédiger la réponse) ne va au bout sans erreur que si **toutes** ses étapes réussissent. Si l'étape i réussit avec la probabilité pᵢ et que les étapes sont indépendantes :

$$
P(\text{succès}) = \prod_{i=1}^{n} p_i = p_1 \times p_2 \times \cdots \times p_n
$$

Quand toutes les étapes ont la même fiabilité p :

$$
P(\text{succès}) = p^{n}
$$

Deux formules d'ingénierie en découlent, pour une fiabilité visée c de l'agent entier :

$$
n_{\max} = \left\lfloor \frac{\ln c}{\ln p} \right\rfloor
$$

$$
p_{\min} = c^{1/n}
$$

### Décryptage des symboles

$$
n
$$

**Sens :** nombre d'étapes qui doivent toutes réussir · **Type / plage :** entier ≥ 1 · **Variable Python :** `n`, `len(probas)`

$$
p_i
$$

**Sens :** probabilité que l'étape i réussisse · **Type / plage :** réel dans [0, 1] · **Variable Python :** `probas[i]`

$$
p
$$

**Sens :** fiabilité commune, quand toutes les étapes se valent · **Type / plage :** réel dans [0, 1] ; ]0, 1[ pour nₘₐₓ · **Variable Python :** `p`

$$
A_i
$$

**Sens :** événement « l'étape i réussit » · **Type / plage :** événement · **Variable Python :** —

$$
P(\text{succès})
$$

**Sens :** probabilité que l'agent aille au bout sans erreur · **Type / plage :** réel dans [0, 1] · **Variable Python :** `fiabilite_composee(probas)`

$$
c
$$

**Sens :** fiabilité visée pour l'agent entier · **Type / plage :** réel dans ]0, 1[ · **Variable Python :** `cible`

$$
n_{\max}
$$

**Sens :** plus grand nombre d'étapes compatible avec la cible · **Type / plage :** entier ≥ 0 · **Variable Python :** `etapes_max(p, cible)`

$$
p_{\min}
$$

**Sens :** fiabilité minimale de chaque étape pour tenir la cible · **Type / plage :** réel dans ]0, 1[ · **Variable Python :** `p_min_par_etape(n, cible)`

$$
\lfloor x \rfloor
$$

**Sens :** partie entière : arrondi vers le bas · **Type / plage :** entier · **Variable Python :** `math.floor(x)`

## Démonstration

### 1. Deux étapes : la règle de multiplication

Notons A₁ l'événement « l'étape 1 réussit » et A₂ l'événement « l'étape 2 réussit ». Par définition de la probabilité conditionnelle, P(A₂ | A₁) = P(A₁ ∩ A₂) / P(A₁), donc :

$$
P(A_1 \cap A_2) = P(A_1) \times P(A_2 \mid A_1)
$$

Cette égalité est toujours vraie. L'hypothèse d'**indépendance** dit que savoir que l'étape 1 a réussi ne change pas la probabilité de réussir l'étape 2 : P(A₂ | A₁) = P(A₂) = p₂. On obtient P(A₁ ∩ A₂) = p₁ p₂, parce qu'on remplace simplement le facteur conditionnel par p₂.

### 2. De deux à n étapes, par récurrence

Notons Bₖ = A₁ ∩ A₂ ∩ ⋯ ∩ Aₖ l'événement « les k premières étapes réussissent ». On a Bₖ₊₁ = Bₖ ∩ Aₖ₊₁, donc, par la même règle :

$$
P(B_{k+1}) = P(B_k) \times P(A_{k+1} \mid B_k) = P(B_k) \times p_{k+1}
$$

La seconde égalité est l'hypothèse d'indépendance appliquée à l'étape k+1 face à l'**ensemble** des étapes précédentes. On parle d'indépendance mutuelle : il ne suffit pas que les étapes soient indépendantes deux à deux. Comme P(B₁) = p₁, la récurrence donne P(B₂) = p₁ p₂, puis P(B₃) = p₁ p₂ p₃, et ainsi de suite jusqu'à P(Bₙ) = ∏ᵢ₌₁ⁿ pᵢ. Quand toutes les pᵢ valent p, le produit de n facteurs égaux vaut pⁿ.

### 3. Une étape de plus ne peut que faire baisser la fiabilité

P(Bₙ₊₁) = P(Bₙ) × pₙ₊₁ ≤ P(Bₙ), parce que pₙ₊₁ ≤ 1 ; l'inégalité est stricte dès que pₙ₊₁ < 1 et P(Bₙ) > 0. Il n'existe donc aucune étape « gratuite » : même un outil fiable à 99 % retire 1 % de ce qui reste.

### 4. Les nombres, à la main

On calcule les puissances par carrés successifs, ce qui se fait au crayon.

**Pour p = 0,95.** 0,95² = 0,9025, puis 0,95⁴ = 0,9025² = 0,814506, puis 0,95⁸ = 0,814506² = 0,663420, donc

$$
0{,}95^{10} = 0{,}95^8 \times 0{,}95^2 = 0{,}663420 \times 0{,}9025 = 0{,}598737 ,
$$

soit 0,5987, puis

$$
0{,}95^{20} = (0{,}95^{10})^2 = 0{,}598737^2 = 0{,}358486 ,
$$

soit 0,3585.

**Pour p = 0,99.** 0,99² = 0,9801, puis 0,99⁴ = 0,960596, 0,99⁵ = 0,950990, 0,99¹⁰ = 0,904382, donc 0,99²⁰ = 0,904382² = 0,817907, soit 0,8179.

Lecture : un agent à 10 étapes fiables à 95 % ne va au bout sans erreur que 6 fois sur 10 ; à 20 étapes, à peine plus d'une fois sur trois. Faire passer chaque étape de 95 % à 99 % fait remonter l'agent à 20 étapes de 35,85 % à 81,79 %.

### 5. Conséquence d'ingénierie : moins d'étapes, ou des étapes plus fiables

On cherche le nombre d'étapes qui garde l'agent au-dessus d'une cible c. Pour 0 < p < 1 :

$$
p^n \ge c \iff n \ln p \ge \ln c \iff n \le \frac{\ln c}{\ln p}
$$

La première équivalence vient de ce que ln est strictement croissante et que ln(pⁿ) = n ln p ; la seconde inverse le sens de l'inégalité parce qu'on divise par ln p, qui est **négatif** quand p < 1. Avec c = 0,9 : pour p = 0,95,

$$
\ln 0{,}9 / \ln 0{,}95 = 0{,}10536 / 0{,}05129 = 2{,}05 ,
$$

donc nₘₐₓ = 2 ; pour p = 0,99, 0,10536 / 0,01005 = 10,48, donc nₘₐₓ = 10. Dans l'autre sens, à n fixé,

$$
p^n \ge c \iff p \ge c^{1/n} ,
$$

parce que x ↦ xⁿ est strictement croissante sur [0, +∞[. Pour tenir 90 % sur 20 étapes, il faut donc

$$
p \ge 0{,}9^{1/20} = e^{\ln 0{,}9 / 20} = e^{-0{,}005268} = 0{,}9947
$$

à chaque étape.

Il n'y a que deux leviers, et la formule les nomme : **réduire le nombre d'étapes** où le modèle peut se tromper (fusionner deux outils en un, calculer en code ce qui n'a pas besoin du modèle), ou **rendre chaque étape plus fiable** (schémas stricts à l'étape 8, validation et relance à l'étape 11, prompt plus précis à l'étape 4).

### 6. Sans indépendance : ce qui reste vrai

En pratique, les erreurs d'un agent sont corrélées : une question mal comprise fausse toutes les étapes à la fois, une panne du service de change fait échouer plusieurs outils ensemble, et à l'inverse une question claire rend toutes les étapes plus faciles. Le produit n'est alors plus exact, mais deux bornes restent vraies quelle que soit la corrélation :

$$
\max\left(0,\; 1 - \sum_{i=1}^{n} (1 - p_i)\right) \;\le\; P(\text{succès}) \;\le\; \min_i \, p_i
$$

- La borne haute : l'événement « toutes les étapes réussissent » est contenu dans l'événement « l'étape i réussit », donc sa probabilité est au plus pᵢ, pour chaque i, donc au plus la plus petite d'entre elles.
- La borne basse : l'agent échoue si au moins une étape échoue, c'est-à-dire sur la réunion des événements « l'étape i échoue ». La probabilité d'une réunion est au plus la somme des probabilités, parce que

$$
P(E \cup F) = P(E) + P(F) - P(E \cap F) \le P(E) + P(F) ,
$$

puis par récurrence. Donc P(échec) ≤ ∑ᵢ (1 − pᵢ) et P(succès) ≥ 1 − ∑ᵢ (1 − pᵢ) ; une probabilité n'étant jamais négative, on garde le maximum avec 0.

Avec p = 0,95 et n = 10, la probabilité de succès est donc comprise entre 1 − 10 × 0,05 = 0,50 et 0,95, et la valeur « indépendante », 0,5987, tombe entre les deux. Les deux extrêmes sont atteints : si toutes les étapes échouent toujours ensemble (une cause commune), l'agent réussit avec la probabilité 0,95 ; si deux étapes n'échouent jamais en même temps, il réussit avec la probabilité 0,50. L'indépendance est donc un modèle à vérifier par la mesure : on fait tourner l'agent sur un jeu de cas et on compte les succès de bout en bout, avec l'intervalle de confiance de l'[étape 7](<../02-LLM-Softmax-et-Prompts/07-Prompts-Formule-Taux-de-Conformite.md>).

### 7. Exemple fait à la main (le code reprend ces nombres)

L'agent d'achats de ce fichier a trois étapes où le modèle peut se tromper : demander la bonne conversion (fiabilité illustrative de 0,99), passer le bon montant à l'outil de TVA (0,98), recopier correctement les chiffres dans la réponse (0,97). Sa fiabilité vaut

$$
0{,}99 \times 0{,}98 \times 0{,}97 = 0{,}9702 \times 0{,}97 = 0{,}941094
$$

Environ 6 réponses sur 100 contiennent au moins une erreur. Si l'on fusionne les deux outils en un seul outil `montant_ttc_aed`, calculé entièrement en code, l'étape « passer le bon montant » disparaît et il reste 0,99 × 0,97 = 0,9603. La simulation de 20 000 agents à 10 étapes de p = 0,95 donne une fréquence de succès de 0,5990, à moins de 0,001 de la valeur théorique 0,5987.

## Du symbole au code Python

Le programme complet de ce fichier, plus haut, contient déjà les quatre fonctions de la fiabilité composée, mais il les présente avant la formule. Voici ces fonctions isolées, juste après leur démonstration, avec les nombres calculés à la main au point 4 et au point 7. Le bloc tourne seul.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`fiabilite_composee(probas)`** — C'est la même fonction que dans le programme complet, recopiée à l'identique : comme un actuaire qui vérifie d'abord que le dossier est complet, elle reçoit la liste des pᵢ, lève `ValueError` si elle est vide ou si une probabilité sort de [0, 1], puis renvoie leur produit par `math.prod`. Dans cet extrait, elle sert aux deux premiers `assert` : 0,5987 pour dix étapes à 0,95 et 0,941094 pour l'agent d'achats à trois étapes (0,99, 0,98, 0,97), les nombres calculés à la main aux points 4 et 7.

**`bornes_sans_independance(probas)`** — Identique elle aussi à celle du programme complet, elle délègue d'abord les contrôles d'entrée à `fiabilite_composee`, dont elle ignore le résultat, puis renvoie le couple formé de la borne basse, 1 moins la somme des probabilités d'échec ramenée à 0 au minimum, et de la borne haute, la plus petite des pᵢ. Comme un inspecteur qui encadre une estimation sans croire à l'indépendance des pannes, elle donne ici 0,50 et 0,95 pour dix étapes à 0,95, et l'`assert` vérifie que la valeur indépendante 0,5987 tombe bien entre les deux.

**`etapes_max(p, cible)`** — C'est le même alpiniste que dans le programme complet, qui ajoute une étape tant que p puissance n + 1 reste au-dessus de la cible et renvoie le dernier n qui tient ; la différence est que cette version d'extrait n'a pas la garde qui exige 0 < p < 1 et 0 < cible < 1, si bien qu'elle ne lève aucune exception et qu'avec p = 1 elle ne s'arrêterait jamais. Elle renvoie ici 2 étapes pour p = 0,95 et 10 pour p = 0,99, avec une cible de 0,9, comme au point 5 de la démonstration.

**`p_min_par_etape(n, cible)`** — C'est encore la racine n-ième de la cible, `cible ** (1.0 / n)`, la plus petite fiabilité par étape qui garantit pⁿ ≥ c, mais sans les vérifications du programme complet : un n nul provoquerait ici une `ZeroDivisionError` au lieu d'une `ValueError` explicite. Comme l'ingénieur qui déduit la solidité de chaque pile de celle du pont entier, elle renvoie 0,9947 pour vingt étapes et une cible de 0,9, le dernier nombre que vérifie l'extrait avant d'imprimer sa ligne de succès.

```python
# [extrait] Étape 1 — fiabilité composée : produit, bornes sans indépendance, n_max, p_min.
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def fiabilite_composee(probas: list[float]) -> float:
    """P(toutes les étapes réussissent) = p_1 × p_2 × … × p_n, si les étapes sont indépendantes."""
    if not probas:
        raise ValueError("il faut au moins une étape")
    if any(not 0.0 <= p <= 1.0 for p in probas):
        raise ValueError("chaque p_i doit être dans [0, 1]")
    return math.prod(probas)


def bornes_sans_independance(probas: list[float]) -> tuple[float, float]:
    """Vrai même si les erreurs sont corrélées : max(0, 1 − Σ(1 − p_i)) <= P(succès) <= min(p_i)."""
    fiabilite_composee(probas)
    return max(0.0, 1.0 - sum(1.0 - p for p in probas)), min(probas)


def etapes_max(p: float, cible: float) -> int:
    """Plus grand n tel que p^n >= cible."""
    n = 0
    while p ** (n + 1) >= cible:
        n += 1
    return n


def p_min_par_etape(n: int, cible: float) -> float:
    """Plus petite fiabilité par étape qui garantit p^n >= cible."""
    return cible ** (1.0 / n)


assert round(fiabilite_composee([0.95] * 10), 4) == 0.5987
assert round(fiabilite_composee([0.99, 0.98, 0.97]), 6) == 0.941094
bas, haut = bornes_sans_independance([0.95] * 10)
assert round(bas, 2) == 0.50 and haut == 0.95 and bas <= 0.5987 <= haut
assert etapes_max(0.95, 0.9) == 2 and etapes_max(0.99, 0.9) == 10
assert round(p_min_par_etape(20, 0.9), 4) == 0.9947
print("OK — toutes les vérifications sont passées.")
```

### Comment le code fonctionne

`fiabilite_composee` commence par refuser les entrées qui n'ont pas de sens : une liste vide, parce qu'un agent sans étape n'a pas de fiabilité, et toute probabilité hors de l'intervalle [0, 1], parce qu'une valeur comme 1,2 ferait croire à une étape « plus que sûre » et fausserait silencieusement le produit. Une fois ces gardes passées, la fonction appelle `math.prod`, qui multiplie les probabilités de gauche à droite : c'est exactement le produit Π pᵢ de la formule, et c'est aussi la récurrence de la démonstration, puisque chaque multiplication ajoute une étape à la chaîne déjà calculée.

`bornes_sans_independance` réutilise d'abord `fiabilite_composee` uniquement pour ses vérifications d'entrée, sans garder son résultat, puis calcule les deux bornes du point 6 : la borne basse additionne les probabilités d'échec 1 − pᵢ (l'inégalité de la réunion) et la retranche de 1, en la ramenant à 0 si la somme dépasse 1 ; la borne haute est simplement la plus petite des pᵢ, parce que la chaîne entière ne peut pas réussir plus souvent que son maillon le plus fragile.

`etapes_max` ne calcule pas le logarithme ln c / ln p de la formule : elle cherche le plus grand n en ajoutant une étape tant que p puissance n + 1 reste au-dessus de la cible. Ce choix évite l'erreur d'arrondi d'un `math.floor` appliqué à un quotient qui tomberait presque sur un entier, et il donne le même résultat que la formule, ce que vérifient les deux `assert` (2 étapes à 95 %, 10 étapes à 99 % pour une cible de 90 %). `p_min_par_etape`, enfin, prend la racine n-ième de la cible, ce qui est la seconde formule d'ingénierie : pour tenir 90 % sur 20 étapes, chaque étape doit être fiable à 99,47 %.

## Squelette algorithmique

La boucle d'agent de ce fichier et sa fiabilité composée se résument en deux algorithmes. Le premier exécute la boucle percevoir, décider, agir, observer, jusqu'à une raison d'arrêt toujours connue. Le second mesure la fiabilité d'une chaîne de n étapes qui doivent toutes réussir.

```text
ALGORITHME ExécuterAgent
ENTRÉES : llm, prompt système, question, outils (nom → fonction), max_étapes
SORTIE  : (statut, réponse, trace)

  messages ← [question]
  précédente ← aucune
  POUR étape DE 1 À max_étapes FAIRE
      réponse ← llm.créer(prompt système, messages, outils)
      SI réponse.arrêt = "fin" ALORS RETOURNER ("fini", texte de la réponse, trace)
      SI réponse.arrêt ∈ {"refus", "tronqué"} ALORS RETOURNER (réponse.arrêt, …, trace)
      demande ← l'appel d'outil contenu dans la réponse
      SI (demande.nom, demande.arguments) = précédente ALORS RETOURNER ("boucle", …, trace)
      précédente ← (demande.nom, demande.arguments)
      résultat ← outils[demande.nom](demande.arguments)     (une erreur devient un résultat marqué « erreur »)
      ajouter (demande, résultat) à la trace et aux messages
  FIN POUR
  RETOURNER ("max_étapes", aucune, trace)

ALGORITHME FiabilitéComposée
ENTRÉES : p₁ … pₙ, cible c
SORTIE  : P(succès), bornes sans indépendance, n_max, p_min

  P ← 1
  POUR i DE 1 À n FAIRE  P ← P × pᵢ  FIN POUR
  bas ← max(0, 1 − Σ (1 − pᵢ))     haut ← min(pᵢ)
  n_max ← 0
  TANT QUE p^(n_max + 1) ≥ c FAIRE  n_max ← n_max + 1  FIN TANT QUE
  p_min ← c^(1/n)
  RETOURNER P, (bas, haut), n_max, p_min
```

**Complexité.** La boucle d'agent fait au plus `max_étapes` appels au modèle et autant d'appels d'outils : son coût en temps est dominé par ces appels réseau, pas par le calcul local. L'historique grossit d'un échange à chaque tour, donc le nombre total de tokens relus croît comme le carré du nombre de tours (démontré à l'étape 72). La fiabilité composée coûte O(n) multiplications et O(n) en mémoire pour la liste des pᵢ ; la recherche de n_max fait au plus n_max + 1 tours de boucle.

**Du squelette au code.** `ExécuterAgent` correspond à la fonction `executer_agent` du programme : la boucle `for etape in range(...)`, les cinq statuts de sortie et la comparaison avec `precedente` pour l'arrêt `boucle`. `FiabilitéComposée` correspond aux quatre fonctions de l'extrait : la boucle `POUR` est `math.prod`, la ligne des bornes est `bornes_sans_independance`, la boucle `TANT QUE` est `etapes_max` et la dernière affectation est `p_min_par_etape`.

## Cas d'usage réels aux Émirats

Les fiabilités par étape, les taux d'intérêt, les seuils et les volumes ci-dessous sont illustratifs. Les règles citées (plafonds de la CBUAE, TVA, fin de service, parité de l'AED, frais du DLD) sont à confirmer avec le texte en vigueur avant toute mise en production.

### Banque — pré-instruire une demande de prêt personnel

Une banque de détail de Dubaï confie à un agent la pré-instruction des demandes de prêt personnel déposées dans son application : l'agent reçoit le montant demandé (150 000 AED sur 48 mois), le salaire mensuel déclaré (25 000 AED) et les mensualités en cours fournies par le bureau de crédit (6 000 AED par mois). Sa boucle appelle quatre outils dans l'ordre imposé par le prompt système : contrôle du format de l'Emirates ID et de l'IBAN, calcul de la mensualité (3 522,75 AED au taux illustratif de 6 % par an), calcul du ratio d'endettement total, puis vérification des plafonds de la CBUAE. Le ratio vaut (6 000 + 3 522,75) / 25 000 = 38,1 %, sous le plafond de 50 % ; le montant reste sous 20 fois le salaire (500 000 AED) et la durée ne dépasse pas 48 mois : l'agent prépare donc un dossier « recevable », que l'analyste signe ou rejette, parce que la décision de crédit n'est jamais déléguée à la boucle. Sans outils, un assistant conversationnel « estimerait » la mensualité de mémoire, et une erreur de 750 AED sur la mensualité suffit, avec ce salaire, à faire passer un ratio de 49 % à 52 %, donc à recommander un crédit contraire à la règle. Avec quatre étapes fiables chacune à 99 %, le dossier n'est entièrement juste que dans 0,99⁴ ≈ 96,1 % des cas : l'équipe ajoute donc une vérification automatique de chaque sortie d'outil avant l'étape suivante, plutôt que de se fier au seul résultat final. L'arrêt `max_etapes` est fixé à 6, parce qu'un dossier qui demande davantage de tours est anormal et doit partir directement en revue humaine. On suit l'écart entre le ratio calculé par l'agent et celui recalculé par l'analyste, avec un objectif de zéro, et la part des dossiers arrêtés autrement que par `fini`.

### Immobilier — estimer un appartement à Dubai Marina

Une agence de Dubaï propose aux propriétaires une estimation en ligne : l'agent reçoit l'adresse, la surface (1 250 sqft), le nombre de chambres et l'étage, puis appelle un outil qui cherche les ventes comparables enregistrées au DLD dans la base de l'agence, un outil qui calcule le premier et le troisième quartile du prix au sqft, et un outil qui rédige le rapport. Sur 14 comparables, Q1 vaut 1 650 AED/sqft et Q3 vaut 1 900 AED/sqft : la fourchette annoncée va de 1 250 × 1 650 = 2 062 500 AED à 1 250 × 1 900 = 2 375 000 AED, et l'agent ajoute que les frais de transfert du DLD, 4 % de la valeur, représenteraient 88 000 AED pour une vente à 2,2 millions d'AED. La règle d'arrêt est métier : avec moins de cinq comparables, l'outil lève une erreur explicite, l'erreur repart vers le modèle, et l'agent répond qu'il transmet la demande à un conseiller au lieu d'inventer une fourchette. Une première version enchaînait cinq appels d'outils fiables à 97 % chacun, soit 0,97⁵ ≈ 85,9 % de rapports corrects ; en fusionnant la recherche et le calcul des quartiles dans un seul outil déterministe, l'équipe passe à trois étapes et à 0,97³ ≈ 91,3 %, sans changer de modèle. Sans boucle d'outils, un modèle seul citerait des prix au sqft appris pendant son entraînement, donc périmés et invérifiables, ce qu'un vendeur conteste immédiatement. L'indicateur suivi est la part des estimations dont le prix de vente final tombe dans la fourchette annoncée, mesurée chaque trimestre.

### Crypto — surveiller la liquidité d'un carnet d'ordres

Une plateforme d'actifs virtuels agréée par la VARA fait tourner un agent de surveillance toutes les cinq minutes : à chaque cycle, il lit la profondeur du carnet d'ordres à ±2 % du prix médian, la compare au seuil fixé par l'équipe risques (250 000 USD), puis relit les trois mesures précédentes pour écarter un creux isolé avant de décider d'alerter. Son périmètre est volontairement étroit : il a des outils de lecture et un outil d'alerte, mais aucun outil capable de passer un ordre, si bien que même un raisonnement faux ne peut pas déplacer de fonds. L'arrêt `boucle` compte ici : un modèle qui relance la lecture de profondeur avec les mêmes arguments consommerait des appels sans jamais conclure, et la boucle s'arrête dès la deuxième demande identique consécutive. La fiabilité composée change d'échelle sur une journée : un cycle de trois étapes fiables à 99,5 % réussit dans 0,995³ ≈ 98,5 % des cas, mais la probabilité que les 288 cycles de la journée réussissent tous tombe à 0,995⁸⁶⁴ ≈ 1,3 %, et l'on compte en moyenne 4,3 cycles ratés par jour. Un échec quotidien est donc presque certain et doit être prévu : relance automatique (étape 11) et alerte sur l'agent lui-même quand un cycle ne finit pas en statut `fini`. Sans ce calcul, l'équipe croirait qu'un agent « fiable à 99,5 % » ne rate jamais rien et découvrirait les trous de surveillance pendant un incident. On suit le délai entre la chute de profondeur et l'alerte, et le nombre de cycles terminés par un autre statut que `fini`.

### Assurance — qualifier un sinistre auto déclaré par chat

Un assureur auto et santé laisse ses assurés déclarer un sinistre par chat, en arabe ou en anglais : l'agent reçoit le numéro de police, la description des dégâts et le devis du garage, 12 000 AED. Il appelle d'abord l'outil de vérification de la police, qui renvoie la garantie active, un plafond de 50 000 AED, une franchise de 500 AED et une vétusté de 20 % liée à l'âge du véhicule (valeurs d'un contrat type), puis l'outil d'indemnité qui calcule min(plafond, max(0, dommage × (1 − vétusté) − franchise)) = 12 000 × 0,8 − 500 = 9 100 AED, puis l'outil de score de fraude. Si ce score dépasse le seuil fixé par l'assureur, l'agent remet le dossier à un gestionnaire et l'annonce à l'assuré sans promettre de montant ; sinon il présente les 9 100 AED comme une estimation provisoire, soumise à validation. Sans boucle d'outils, un assistant conversationnel répondrait « environ 10 000 AED » en oubliant la franchise ou la vétusté, et l'assureur se retrouverait face à une promesse écrite qu'il ne peut pas tenir. L'assurance étant supervisée par la CBUAE, chaque calcul doit être reproductible : la trace (outil, arguments, résultat) est conservée avec le dossier, et un statut `tronque` déclenche une nouvelle génération au lieu d'envoyer une réponse coupée. On suit la part des dossiers clos sans reprise par un gestionnaire et l'écart moyen entre l'estimation de l'agent et l'indemnité finale.

### RH — préparer l'indemnité de fin de service

Un cabinet RH présent dans plusieurs émirats prépare pour ses clients les soldes de tout compte des salariés du secteur privé : l'agent reçoit une demande comme « calcule l'indemnité de fin de service de ce salarié, qui part après 7 ans », avec l'identifiant du dossier. Il appelle d'abord l'outil qui lit le contrat (salaire de base de 10 000 AED, date d'entrée, nationalité, émirat et zone), puis l'outil de calcul qui applique le décret-loi fédéral 33/2021 : 21 jours de salaire de base par an pour les cinq premières années et 30 jours au-delà, soit 5 × 21 + 2 × 30 = 165 jours à 10 000 / 30 AED, donc 55 000 AED, sous le plafond de 24 mois de salaire de base (240 000 AED). L'outil refuse lui-même les cas hors périmètre, un ressortissant émirien (qui relève de la GPSSA) ou un salarié du DIFC (régime DEWS), et ce refus repart vers le modèle, qui répond alors que le dossier relève d'un autre régime au lieu de calculer quand même. Sans outil, un modèle de langage appliquerait parfois une réduction pour démission apprise sur d'anciens textes, alors que le décret-loi n'en prévoit pas, et produirait un montant faux, contestable devant le MOHRE. Le montant n'est jamais versé par l'agent : il part au service paie, qui le valide avant le paiement par le WPS. On suit le nombre de soldes corrigés par la paie, avec un objectif de zéro, et la part des demandes hors périmètre correctement détectées.

### BTP — contrôler une facture de location d'engins

Un groupe de construction qui mène de grands chantiers à Dubaï reçoit chaque mois des centaines de factures de sous-traitants et de loueurs d'engins, dont certaines sont libellées en USD : l'agent de contrôle reçoit la facture extraite (48 000 USD HT pour la location de deux grues) et le bon de commande correspondant. Il appelle exactement les deux outils de ce fichier, la conversion au taux fixe de 3,6725, qui donne 176 280 AED HT, puis le calcul de TVA à 5 %, qui donne 8 814 AED de TVA et 185 094 AED TTC, avant un troisième outil qui compare ces montants au bon de commande et applique la retenue de garantie prévue au contrat. Si la facture affiche une TVA différente de celle recalculée, l'agent ne corrige rien de lui-même : il bloque la facture et ouvre une demande de rectification auprès du fournisseur. Sans outils, le modèle multiplierait de tête, et une erreur d'un chiffre sur 176 280 AED passerait dans la comptabilité, puis dans la déclaration de TVA du groupe. Le taux de 3,6725 est une constante du code et non une phrase du prompt, parce que l'AED est indexé sur l'USD à cette parité et qu'un taux qui varierait d'une conversation à l'autre rendrait la trace invérifiable. On suit le taux de factures bloquées à raison, c'est-à-dire confirmées par la comptabilité, et le délai moyen de traitement d'une facture.

## Pièges et limites

- **Croire que le modèle agit.** Le modèle ne fait que demander ; c'est le dictionnaire `outils` qui fixe ce que l'agent peut faire. Un outil dangereux (virement, suppression) se protège dans l'outil lui-même : contrôle des arguments, approbation humaine qui renvoie « refusé par l'humain » au modèle.
- **Prendre l'indépendance pour acquise.** pⁿ est un modèle ; les erreurs réelles sont corrélées. On mesure le succès de bout en bout sur un jeu de cas, et l'on garde en tête les bornes de la démonstration (point 6).
- **Se fier au seul arrêt `boucle`.** Il ne détecte que la répétition immédiate de la même action ; une oscillation A, B, A, B lui échappe. `max_etapes` reste le filet de sécurité, et il doit être bas.
- **Avaler une erreur d'outil.** Renvoyer `None` ou une chaîne vide au lieu d'un `tool_result` marqué `is_error` fait croire au modèle que l'outil a réussi : il invente alors la suite.
- **Calculer de l'argent en `float`.** `round()` arrondit la valeur binaire du flottant (`round(2.675, 2)` donne 2.67). En production, les montants se calculent en `decimal.Decimal` avec une règle d'arrondi explicite, comme `BigDecimal` en Java ; ce fichier garde `float` pour rester court.

### Exercice feuille blanche

1. Sans regarder le code, réécrire `executer_agent` avec ses cinq statuts de sortie, puis la tester avec un script de trois réponses : deux appels d'outils différents, puis `"end_turn"`.
2. Prédire, puis vérifier : que vaut 0,98¹⁵ ? Combien d'étapes au plus un agent à p = 0,98 peut-il enchaîner en gardant 90 % de fiabilité ? (Réponses : 0,7386 ; 5 étapes, car 0,98⁵ = 0,9039 et 0,98⁶ = 0,8858.)
3. Trouver le bug : dans une variante, la ligne `precedente = signature` est placée **avant** le test `if signature == precedente`. Que renvoie l'agent sur le premier scénario, et après combien d'outils exécutés ? (Réponse : `boucle` dès la 1re étape, sans aucun outil exécuté, parce que la comparaison est toujours vraie.)

## Pour aller plus loin

- Réussir **au moins une fois** sur k essais et réussir **à chaque fois** sur k essais sont deux mesures très différentes d'un même agent (pass@k et pass^k) : elles sont démontrées à l'[étape 60](<../10-Evaluation/60-Evaluation-Formule-Agent-Goal-Accuracy.md>).
- L'espion montre un historique qui grossit à chaque tour (`[1, 3, 5]`) et qui est renvoyé en entier à chaque appel : le nombre total de tokens lus croît donc comme le carré du nombre de tours. La démonstration est à l'[étape 72](<../12-Production-Couts-Optimisation/72-Couts-et-Gestion-des-Tokens.md>).
- Le code de ReAct, de Plan-and-Execute et de Reflexion, puis l'adaptateur Claude branché sur la même boucle, sont à l'[étape 13](<../03-Schemas-Outils-et-Premiere-Evaluation/13-Agent-Exemples-Cas-Usage.md>).

> Suite : [Softmax et température](<../02-LLM-Softmax-et-Prompts/02-Softmax-Temperature-Prochain-Token.md>) — étape 2.
