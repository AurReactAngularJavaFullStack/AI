# Étape 47 — MCP — Exemples et cas d'usage

> Étape 47 du parcours · Prérequis : [MCP : définitions et serveur stdio](<46-MCP-Definitions-Fondamentaux.md>) · Suite : [MCP par domaine](<48-MCP-Applications-Domaines.md>)

**Dossier :** 09-MCP  
**Métiers :** AI Agent Ops, Forward-Deployed Engineers, AI Platform Team

L'ancienne version de ce fichier tenait en quatre puces (« serveur MCP bancaire », « serveur immobilier », « serveur crypto », « intégration chez le client »). Ce fichier les remplace par des scénarios complets, exécutés de bout en bout : un host découvre un serveur bancaire, lit une resource et un prompt ; l'agent consulte un solde puis initie un virement que seul un humain peut autoriser, **dans** l'outil ; un adaptateur place une API REST héritée d'assureur derrière MCP ; un appel tombe en `isError`, un autre en timeout ; enfin, on mesure le p95 des temps de réponse. Chaque scénario affiche sa trace et vérifie sa décision par `assert`.

## Le moteur commun

Le programme reprend trois pièces déjà construites. La boucle canonique `executer_agent` et le faux LLM scripté viennent de l'étape 1 : ils ne changent pas d'une ligne. Le validateur de schéma vient de l'étape 46, et le serveur reprend le même découpage en méthodes JSON-RPC, augmenté de `resources/list`, `resources/read`, `prompts/list` et `prompts/get`. La seule pièce nouvelle est l'adaptateur `outils_pour_agent`, qui transforme la réponse de `tools/list` en deux choses : les fonctions que la boucle appelle, et les définitions d'outils que le modèle lit.

Pour que la démonstration soit instantanée et reproductible, le client parle au serveur par un **transport en mémoire** : chaque message est réellement sérialisé en une ligne JSON, passé au serveur, puis relu, exactement comme sur stdio, mais sans sous-processus. Le temps est une horloge simulée : un outil « coûte » des secondes en faisant avancer un compteur, ce qui permet de provoquer un timeout de 5 s sans attendre 5 s. Le transport réel (stdio à l'étape 46, ou Streamable HTTP) se branche à la place sans toucher au reste : c'est l'architecture hexagonale appliquée au protocole.

## Les scénarios en un tableau

| Scénario | Entrées | Méthodes et outils, dans l'ordre | Sortie | Garde-fou |
|---|---|---|---|---|
| 1. Découverte | serveur `banque-paiements` | `initialize`, `notifications/initialized`, `tools/list`, `resources/read`, `prompts/get` | 3 capacités, 2 outils, barème, consigne | capacités déclarées ; `destructiveHint` sur l'écriture |
| 2. Virement approuvé | 12 500 AED, deux IBAN AE valides | `solde_compte`, puis `initier_virement` | exécuté, nouveau solde 35 750,75 AED | approbation humaine dans l'outil, plafond 50 000 AED dans le schéma |
| 3. Virement refusé | 9 000 AED, même bénéficiaire | `initier_virement` | `isError` « refusé par l'humain » | aucun débit sans « approuvé » |
| 4. API héritée | sinistres CLM-2026-0042 et CLM-2026-9999 | `statut_sinistre` × 3 | ouvert, 13 900 AED ; `isError` inconnu ; timeout | timeout client de 5 s, annulation notifiée |
| 5. Latence | 20 appels de `statut_sinistre` | `tools/call` × 20 | p95 = 0,240 s | SLO sur le p95 |

Le tableau suivant sépare, pour la latence et les refus, la **fonction mesurée** sur chaque appel, la **métrique** calculée sur une fenêtre d'appels et le **seuil** qui déclenche une action. Les seuils sont illustratifs.

| Fonction mesurée sur un appel | Métrique sur la fenêtre | Seuil | Action si dépassé |
|---|---|---|---|
| durée d'un `tools/call` (horloge du client) | p95 au rang le plus proche | 0,300 s | alerte d'astreinte, réduction du trafic |
| `isError` vrai ou faux | part des `isError` par outil | 5 % | revue de la description ou du système amont |
| décision de l'approbateur | part des refus | 20 % | revue du comportement de l'agent |
| timeout client | nombre de `notifications/cancelled` par heure | 3 | bascule sur un message d'attente |

## Le JSON complet d'un appel

Voici, mise en forme sur plusieurs lignes, la requête `tools/call` que le host envoie pour le virement du scénario 2. Le programme l'imprime sur une seule ligne, comme l'exige le transport stdio.

```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "tools/call",
  "params": {
    "name": "initier_virement",
    "arguments": {
      "iban_source": "AE07 0331 2345 6789 0123 456",
      "iban_beneficiaire": "AE49 0339 8765 4321 0987 654",
      "montant_aed": 12500,
      "reference": "VIR-2026-0001"
    }
  }
}
```

La réponse porte le même `id`. Le résultat est donné deux fois : en texte, pour le modèle, et en `structuredContent`, pour le code qui veut un objet.

```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "result": {
    "content": [{"type": "text", "text": "{\"statut\": \"exécuté\", \"reference\": \"VIR-2026-0001\", \"nouveau_solde_aed\": 35750.75}"}],
    "structuredContent": {"statut": "exécuté", "reference": "VIR-2026-0001", "nouveau_solde_aed": 35750.75},
    "isError": false
  }
}
```

Quand l'humain refuse (scénario 3), le résultat est un échec d'outil, pas une erreur de protocole : il n'y a pas de champ `error`, et le texte dit au modèle ce qui s'est passé.

```json
{"content": [{"type": "text", "text": "refusé par l'humain : bénéficiaire non reconnu par le client"}], "isError": true}
```

Quand le client cesse d'attendre (scénario 4), il envoie une notification d'annulation, sans `id`, à laquelle le serveur ne répond pas :

```json
{"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 5, "reason": "timeout client de 5.0 s"}}
```

## Démonstration

### 1. Le p95 au rang le plus proche laisse au moins 95 % des appels sous lui

On trie les N durées mesurées, x₍₁₎ ≤ x₍₂₎ ≤ … ≤ x₍N₎, et l'on prend la valeur de rang k :

$$
k = \lceil 0{,}95\,N \rceil
$$

$$
\mathrm{p95} = x_{(k)}
$$

Par définition de la partie entière supérieure, k est le plus petit entier qui n'est pas inférieur à 0,95 N, ce qui s'écrit :

$$
0{,}95\,N \le k < 0{,}95\,N + 1
$$

**Au moins 95 % des valeurs sont inférieures ou égales au p95**, parce que x₍₁₎, …, x₍k₎ le sont toutes, et qu'il y en a k ≥ 0,95 N. **C'est la plus petite valeur observée qui a cette propriété** : si v est une valeur observée strictement inférieure à x₍k₎, alors toutes les valeurs de rang k ou plus sont strictement supérieures à v, donc au plus k − 1 valeurs sont inférieures ou égales à v, et k − 1 < 0,95 N. Le p95 au rang le plus proche est donc toujours une durée réellement observée, jamais une interpolation.

Avec N = 20, on obtient k = ⌈19⌉ = 19. Les 20 durées du programme, triées, en millisecondes, sont 95, 99, 101, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 180, 240, 900 : la 19e vaut 240 ms. Le programme vérifie qu'au moins 0,95 × 20 = 19 durées sont inférieures ou égales à 0,240 s.

### 2. Pourquoi la moyenne ne suffit pas

Au-dessus du p95, il reste N − k valeurs, ici une seule : 900 ms. Le p95 ne dépend pas de sa valeur. Si cet appel avait duré 9 000 ms, le p95 vaudrait toujours 240 ms. La moyenne, elle, se déplace avec chaque valeur :

$$
\bar{x} = \frac{1}{N}\sum_{i=1}^{N} x_i = \frac{3\,540}{20} = 177 \text{ ms}
$$

Sans l'appel de 900 ms, la moyenne des 19 autres vaudrait 2 640 / 19 ≈ 138,9 ms ; avec un appel de 9 000 ms, elle vaudrait (2 640 + 9 000) / 20 = 582 ms. Une moyenne de 177 ms ne dit donc ni combien d'utilisateurs attendent longtemps, ni combien de temps ils attendent. Le p95 dit : « 19 appels sur 20 répondent en 240 ms ou moins ». Le maximum, enfin, dépend d'un seul appel et ne se compare pas à un SLO : il sert à repérer les incidents, pas à piloter le service.

### 3. Aucun virement sans approbation : un invariant du code

Dans `initier_virement`, les trois seules lignes qui modifient l'état (les deux soldes et la liste `VIREMENTS`) sont placées **après** le test `if decision != "approuvé": raise ErreurOutil(...)`. Tout chemin qui atteint ces lignes passe donc par une décision « approuvé ». Or le modèle ne peut pas modifier l'état autrement : il ne fait qu'émettre un bloc `tool_use`, que la boucle transforme en un `tools/call`, que le serveur transforme en un appel de cette fonction. Quel que soit le texte que lit le modèle, injection comprise, l'invariant tient : **nombre de virements exécutés ≤ nombre d'approbations accordées**. La décision est lue à chaque appel, sans mémoire : deux appels ont produit deux demandes, ce que vérifie l'`assert` `len(DEMANDES_APPROBATION) == 2`.

Retirer l'outil de la liste en cours de boucle, au lieu de demander l'approbation dans l'outil, ne donne pas cette garantie. L'historique contient déjà des blocs `tool_use` qui citent l'outil ; la liste des outils fait partie du préfixe mis en cache, que l'on invalide ; et rien n'empêche un autre chemin du code d'appeler la fonction. L'approbation dans la fonction est le seul point de passage obligé.

### 4. Un timeout n'annule pas l'appel

Notons t₀ l'instant où le client envoie la requête, d le délai du client et L la durée réelle du traitement côté serveur. Le client abandonne en t₀ + d si L > d ; le serveur finit son traitement en t₀ + L. Dans le scénario 4, d = 5 s et L = 6 s : pendant la seconde qui sépare ces deux instants, le client a déjà annoncé l'échec alors que le serveur travaille encore, puis le serveur termine. La notification `notifications/cancelled` est une demande de bonne volonté : le serveur peut l'ignorer, et il l'ignore forcément s'il a déjà fini. Pour un outil de lecture, la conséquence est nulle. Pour un outil d'écriture, l'effet a peut-être eu lieu : on ne relance qu'avec une clé d'idempotence (la référence du virement), comme démontré à l'étape 12.

### 5. Les montants en fils : une conversion exacte

Le système hérité compte en fils, 100 fils faisant 1 AED, et en entiers : 1 390 000 fils. La division par 100 donne exactement 13 900,0, parce que les deux nombres et leur quotient sont des entiers représentables sans erreur en virgule flottante. Ce n'est plus vrai pour des montants non entiers en dirhams : 0,1 + 0,2 ne vaut pas exactement 0,3 en binaire. On garde donc les montants en fils entiers dans les calculs, et l'on ne convertit en AED qu'à l'affichage ou à la frontière de l'outil, avec un arrondi au centième.

## Le programme

### Déroulé, ligne par ligne

**Le code canonique** (`Bloc`, `Reponse`, `texte`, `appel_outil`, `FakeLLM`, `executer_agent`, `p95`, `iban_ae_valide`) est recopié tel quel du guide du parcours, et **`valider`** de l'étape 46. **`objet(**proprietes)`** fabrique un schéma d'objet strict : tous les champs sont obligatoires (`required` trié), aucun champ non prévu n'est admis.

**`Horloge`** est un compteur `t` en secondes simulées ; `avancer(duree)` l'incrémente et arrondit à 10⁻⁶ pour que les durées s'impriment sans bruit de virgule flottante. Il n'y a ni `time.sleep`, ni horloge réelle.

**`ServeurMCP`** reçoit des listes d'`Outil`, de `Resource` et de `Prompt`.

- `capacites()` ne déclare `resources` et `prompts` que si le serveur en a : le serveur d'assurance ne déclare que `tools`.
- `traiter(ligne)` est le point d'entrée du transport en mémoire. Une notification est journalisée dans `self.journal` et reçoit `None`. Une requête passe à `executer`, et une `ErreurProtocole` devient une réponse `error` avec son code.
- `executer(methode, p)` traite chaque méthode. `tools/list` ajoute à chaque outil les annotations `readOnlyHint` et `destructiveHint`. `tools/call` refuse un outil inconnu ou des arguments non conformes (−32602), transforme une `ErreurOutil` en résultat `isError: true`, et un succès en `content` plus `structuredContent`. `resources/read` renvoie `{"contents": [{"uri", "mimeType", "text"}]}`, ou l'erreur −32002 (resource introuvable) pour une URI inconnue. `prompts/get` remplit le gabarit avec `str.format` et renvoie `{"description", "messages": [{"role": "user", "content": {"type": "text", "text": …}}]}`.

**`ClientMCP.requete(methode, params)`** numérote la requête, la sérialise, note `debut = HORLOGE.t`, la passe au serveur, puis calcule `duree = HORLOGE.t - debut`. Si `duree > delai_s`, le client se comporte comme un client réel qui aurait cessé d'attendre : il envoie `notifications/cancelled` avec `requestId` et lève `TimeoutError`, sans lire la réponse tardive. Sinon, il garde la paire (requête, réponse) dans `dernier_echange` et renvoie la réponse décodée.

**`outils_pour_agent(client)`** appelle `tools/list` et fabrique, pour chaque outil, une fonction `appeler(**arguments)` qui fait le `tools/call`. Une réponse `error` lève `RuntimeError` ; un résultat `isError` lève `ErreurOutilDistant` avec le texte de l'outil ; un succès renvoie `structuredContent`. La boucle canonique attrape ces exceptions et les renvoie au modèle avec `is_error`. La fonction renvoie aussi les définitions d'outils au format de l'API (`name`, `description`, `input_schema`), prêtes pour `ClaudeLLM`.

**Le serveur bancaire.** `IBAN_CLIENT` (`AE07…456`, solde fictif 48 250,75 AED) et `IBAN_PROPRIETAIRE` (`AE49…654`, 3 100 AED) passent tous deux le contrôle mod 97. `APPROBATEUR["decision"]` simule l'humain : chaque scénario y place `("approuvé", "")` ou `("refusé", motif)`.

- `solde_compte(iban)` retire les espaces, refuse un IBAN invalide ou inconnu par `ErreurOutil`, fait avancer l'horloge de 0,12 s et renvoie le solde.
- `initier_virement(...)` vérifie les deux IBAN, puis le solde (48 250,75 ≥ 12 500), écrit la demande dans `DEMANDES_APPROBATION`, lit la décision, et lève `ErreurOutil("refusé par l'humain : …")` si elle n'est pas « approuvé ». Sinon seulement, elle débite 12 500 AED (48 250,75 − 12 500 = 35 750,75), crédite le bénéficiaire (3 100 + 12 500 = 15 600), enregistre le virement et renvoie le statut.
- `SCHEMA_IBAN` accepte 23 caractères, ou 29 avec les six espaces de l'écriture usuelle ; le schéma de `montant_aed` plafonne le virement à 50 000 AED, ce qu'annonce aussi le barème. `SERVEUR_BANQUE` réunit les deux outils, la resource `banque://baremes/frais-virement` et le prompt `preparer_virement`.

**Le serveur d'assurance.** `api_rest_heritee(methode, chemin)` simule le système existant : elle consomme la prochaine durée de `LATENCES_HERITEES` (0,15 s par défaut) et renvoie `(200, corps)` ou `(404, {"ERR": "NOT_FOUND"})`. `statut_sinistre(numero)` est l'adaptateur : 404 devient un `isError` qui dit quoi faire, un code 5xx un `isError` d'indisponibilité, et un 200 un objet lisible, avec `1390000 / 100 = 13900.0` AED.

**`main()`**, scénario par scénario.

1. Le host initialise le serveur bancaire, reçoit trois capacités et deux outils, et vérifie que `initier_virement` porte `destructiveHint: true`. Il lit le barème (2 lignes), récupère la consigne du prompt et vérifie qu'une URI inconnue donne −32002.
2. L'approbateur accepte. Le faux LLM appelle `solde_compte`, puis `initier_virement`, puis répond. La trace montre 48 250,75 puis 35 750,75 AED ; le programme affiche le JSON complet de la requête et de la réponse d'`id` 8, puis la demande d'approbation. Les `assert` vérifient le statut, le nombre d'étapes (3), le virement unique et le solde du bénéficiaire (15 600 AED).
3. L'approbateur refuse. L'outil renvoie `isError`, la trace porte `ERREUR refusé par l'humain : …`, et les soldes ne bougent pas.
4. Le host initialise le serveur d'assurance. Les latences simulées sont 0,18 s, 0,21 s et 6,0 s. Le premier appel réussit, le deuxième tombe sur un numéro inconnu (`isError`), le troisième dépasse le délai de 5 s : `TimeoutError`, et le journal du serveur contient la notification d'annulation pour la requête 5.
5. Vingt appels consomment les 20 durées de la liste canonique de `p95`, converties en secondes. Le client les mesure lui-même sur l'horloge : p95 = 0,240 s, moyenne = 0,177 s, maximum = 0,900 s. Le SLO de 0,300 s est respecté par le p95, alors que le maximum le dépasse.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`texte(t)`** — Cette petite fonction est l'imprimeur qui met en forme une réplique du modèle avant qu'on la glisse dans le script : elle reçoit une chaîne et renvoie un `Bloc` de type `text` qui la contient, avec tous les autres champs vides. Elle ne fait rien d'autre ; `main` s'en sert pour écrire les réponses finales des faux LLM, par exemple « Virement de 12 500 AED exécuté, réf. VIR-2026-0001 », que `executer_agent` recolle ensuite pour former la réponse de l'agent.

**`appel_outil(nom, arguments, id_)`** — C'est le formulaire qu'un modèle remplit quand il veut faire agir un outil : la fonction reçoit le nom de l'outil, le dictionnaire de ses arguments et un identifiant d'appel, et renvoie un `Bloc` de type `tool_use` qui porte ces trois informations. Elle ne vérifie rien ; les scripts de `main` l'utilisent pour faire demander au faux LLM `solde_compte`, puis `initier_virement`, ou trois fois `statut_sinistre`, et l'identifiant, comme `t1` ou `a2`, permet de relier chaque résultat à son appel.

**`FakeLLM.__init__(script)`** — Le constructeur prépare un comédien qui jouera le modèle de langage en récitant des répliques apprises d'avance : il reçoit la liste des réponses prévues, en fait une copie et met à 0 le compteur des appels. Il ne renvoie rien ; grâce à lui, chaque scénario de `main` est déterministe et gratuit, sans aucun appel réseau, et la même boucle d'agent pourrait tourner avec un vrai modèle derrière le même port.

**`FakeLLM.create(system, messages, tools)`** — Cette méthode est la réplique du comédien chaque fois que la boucle lui donne la parole : elle reçoit, par mots-clés, le message système, l'historique des messages et la liste des outils, comme le ferait l'API d'un vrai modèle, mais les ignore et renvoie simplement la prochaine `Reponse` du script, en avançant son compteur. Si le script est épuisé, elle lève une `RuntimeError` « script épuisé », ce qui signalerait qu'un scénario a demandé plus d'étapes que prévu.

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — C'est la boucle de l'agent, un contremaître qui fait tourner le cycle percevoir, décider, agir, observer : la fonction reçoit le modèle, le message système, la question, le dictionnaire des outils appelables, leurs définitions et un nombre maximal de 8 étapes par défaut, puis, à chaque étape, appelle le modèle, ajoute sa réponse telle quelle à l'historique et s'arrête sur un refus, une troncature, une fin de tour ou deux demandes identiques de suite. Sinon, elle exécute chaque appel d'outil, renvoie toute exception au modèle comme résultat d'erreur au lieu de l'avaler, et regroupe tous les résultats dans un seul message ; elle renvoie un dictionnaire avec le statut, la trace des appels, le nombre d'étapes et la réponse finale, par exemple `fini` en 3 étapes pour le virement approuvé.

**`p95(valeurs)`** — Cette fonction est le statisticien qui ne s'intéresse pas à la moyenne, mais à ce que vivent 19 utilisateurs sur 20 : elle reçoit une liste de durées, lève une `ValueError` si elle est vide, la trie et renvoie la valeur de rang ⌈0,95 N⌉, une durée réellement observée et jamais une interpolation. Sur les 20 appels du scénario 5, le rang vaut 19 et le p95 vaut 0,240 seconde, alors que la moyenne est de 0,177 seconde et le maximum de 0,900 seconde ; `main` vérifie qu'au moins 19 durées sont inférieures ou égales à ce p95.

**`iban_ae_valide(iban)`** — C'est la même fonction que dans le programme de l'étape 46, recopiée sans changement, le guichetier qui contrôle un numéro de compte : elle reçoit un IBAN, retire les espaces, passe en majuscules, exige 23 caractères, le préfixe `AE` et 21 chiffres, puis déplace les quatre premiers caractères à la fin, convertit les lettres en nombres et vérifie un reste de 1 modulo 97. Elle renvoie vrai ou faux ; ici, l'IBAN du client et celui du propriétaire passent tous deux le contrôle, et `solde_compte` comme `initier_virement` s'appuient sur elle.

**`Horloge.__init__()`** — Le constructeur pose sur la table une horloge simulée que seuls les outils font avancer : il ne reçoit rien d'autre que l'objet lui-même et met son compteur `t` à zéro seconde. Il ne renvoie rien ; le programme crée une seule horloge globale, `HORLOGE`, que le client lit avant et après chaque requête pour mesurer sa durée, sans jamais appeler `time.sleep` ni lire l'heure réelle.

**`Horloge.avancer(duree)`** — Cette méthode est le geste de l'outil qui « prend du temps » : elle reçoit une durée en secondes, l'ajoute au compteur et arrondit le résultat à 10⁻⁶ près, pour que les durées s'impriment sans bruit de virgule flottante. Elle ne renvoie rien ; `solde_compte` la fait avancer de 0,12 seconde, `initier_virement` de 0,35, et `api_rest_heritee` de la prochaine latence prévue, 6,0 secondes pour l'appel qui dépasse le délai du client.

**`ErreurProtocole.__init__(code, message)`** — Le constructeur de cette exception prépare un refus officiel, numéroté selon JSON-RPC : il reçoit le code d'erreur et le message, transmet le message à la classe `Exception` et range le code dans l'attribut `code`. Il ne renvoie rien ; `ServeurMCP.traiter` attrape ensuite cette exception et la transforme en réponse `error` avec ce code, par exemple −32602 pour un outil inconnu, −32002 pour une resource introuvable ou −32601 pour une méthode inconnue.

**`ServeurMCP.__init__(nom, outils, resources, prompts)`** — Le constructeur ouvre un serveur générique avec ses trois rayons, outils, resources et prompts : il reçoit le nom du serveur, la liste des outils et, facultativement, celles des resources et des prompts, range chaque outil sous son nom, chaque resource sous son URI et chaque prompt sous son nom, puis crée un journal vide pour les notifications. Il ne renvoie rien ; le programme en construit deux, le serveur bancaire, avec deux outils, une resource et un prompt, et le serveur d'assurance, avec un seul outil.

**`ServeurMCP.capacites()`** — Cette méthode est la vitrine du serveur, qui n'annonce que ce qu'il a réellement en rayon : elle ne reçoit rien, déclare toujours la capacité `tools`, ajoute `resources` si le serveur possède au moins une resource et `prompts` s'il possède au moins un prompt, puis renvoie ce dictionnaire. `executer` le place dans la réponse à `initialize` ; le host du scénario 1 reçoit ainsi les trois capacités `prompts`, `resources` et `tools` du serveur bancaire, alors que le serveur d'assurance ne déclare que `tools`.

**`ServeurMCP.traiter(ligne)`** — C'est le guichet d'entrée du transport en mémoire, où une ligne JSON arrive et une ligne JSON repart : la méthode reçoit une ligne de texte, la décode, et si le message n'a pas d'`id`, l'inscrit dans le journal comme notification avec ses paramètres et renvoie `None`. Sinon, elle confie la méthode et ses paramètres à `executer`, emballe le résultat dans une réponse JSON-RPC, ou transforme une `ErreurProtocole` en réponse `error` avec son code, puis renvoie la réponse sérialisée ; c'est ainsi que l'annulation de la requête 5 se retrouve dans le journal du serveur d'assurance.

**`ServeurMCP.executer(methode, p)`** — Cette méthode est le standard téléphonique qui oriente chaque méthode MCP vers le bon service : elle reçoit le nom de la méthode et ses paramètres, répond à `initialize` avec la version et les capacités, à `tools/list` avec les outils et leurs annotations `readOnlyHint` et `destructiveHint`, et à `tools/call` après avoir refusé un outil inconnu ou des arguments non conformes par −32602, en transformant une `ErreurOutil` en résultat `isError`. Elle sert aussi la liste et la lecture des resources, avec −32002 pour une URI inconnue, la liste et le remplissage des prompts, et lève −32601 pour toute autre méthode ; elle renvoie le dictionnaire du résultat.

**`ClientMCP.__init__(serveur, delai_s)`** — Le constructeur prépare le host qui parlera à un serveur : il reçoit le serveur à joindre et le délai d'attente, 5 secondes par défaut, met le prochain identifiant à 1, crée la liste des durées mesurées et initialise le dernier échange à deux chaînes vides. Il ne renvoie rien ; `main` crée un client pour le serveur bancaire et un autre, avec un délai explicite de 5 secondes, pour le serveur d'assurance, dont le troisième appel dépassera ce délai.

**`ClientMCP.notifier(methode, params)`** — Cette méthode est le client qui laisse un mot sans attendre de réponse : elle reçoit le nom d'une méthode et ses paramètres, construit un message JSON-RPC sans `id` et le passe directement à `traiter` du serveur, sans rien lire en retour. Elle ne renvoie rien ; `main` l'utilise pour `notifications/initialized`, et `requete` l'appelle elle-même pour envoyer `notifications/cancelled` avec l'identifiant de la requête quand le délai est dépassé.

**`fabriquer(nom)`** — Cette fonction interne vit dans `outils_pour_agent` et joue l'artisan qui fabrique, pour chaque outil distant, une poignée que l'agent pourra tourner comme s'il s'agissait d'une fonction locale : elle reçoit le nom d'un outil et renvoie la fonction `appeler`, une fermeture qui garde ce nom en mémoire. Sans cette fabrique, une simple boucle créerait des fonctions qui partageraient toutes le dernier nom vu ; avec elle, `outils_pour_agent` construit un dictionnaire où chaque nom d'outil pointe vers sa propre fonction d'appel.

**`appeler(**arguments)`** — Cette fonction interne vit dans `fabriquer`, elle-même dans `outils_pour_agent`, et c'est le coursier qui porte un appel d'outil jusqu'au serveur MCP : elle reçoit les arguments par mots-clés, envoie une requête `tools/call` avec le nom gardé en mémoire, lève une `RuntimeError` si la réponse est une erreur de protocole, puis une `ErreurOutilDistant` avec le texte de l'outil si le résultat porte `isError`. Sinon, elle renvoie le `structuredContent` ; la boucle d'agent attrape ces exceptions et les renvoie au modèle, si bien que le refus de l'humain ou le sinistre inconnu apparaissent comme des lignes `ERREUR` dans la trace.

**`solde_compte(iban)`** — Cet outil de lecture joue le teneur de comptes de la banque : il reçoit un IBAN, retire ses espaces, lève une `ErreurOutil` « compte introuvable ou IBAN invalide » si le contrôle échoue ou si le compte n'est pas dans `SOLDES_AED`, fait avancer l'horloge de 0,12 seconde et renvoie l'IBAN normalisé avec son solde fictif. Au scénario 2, il annonce 48 250,75 AED pour le compte du client avant le virement, et c'est sur ce solde que le faux LLM décide ensuite d'initier le virement.

**`initier_virement(iban_source, iban_beneficiaire, montant_aed, reference)`** — C'est l'outil d'écriture, un caissier qui ne bouge pas un dirham sans la signature d'un responsable : il reçoit les deux IBAN, le montant et une référence, lève une `ErreurOutil` si un IBAN est invalide ou si le solde ne suffit pas, inscrit la demande dans `DEMANDES_APPROBATION`, puis lit la décision de l'approbateur et lève une `ErreurOutil` « refusé par l'humain » si elle n'est pas « approuvé ». Seulement alors, il débite la source, crédite le bénéficiaire, enregistre le virement, avance l'horloge de 0,35 seconde et renvoie le statut `exécuté` avec le nouveau solde : 48 250,75 − 12 500 = 35 750,75 AED, et 3 100 + 12 500 = 15 600 AED pour le bénéficiaire.

**`api_rest_heritee(methode, chemin)`** — Cette fonction met en scène le vieux système de l'assureur, qu'on ne modifie pas et qui parle sa propre langue : elle reçoit une méthode HTTP et un chemin, fait avancer l'horloge de la prochaine latence de `LATENCES_HERITEES`, ou de 0,15 seconde si la liste est vide, extrait le numéro de sinistre à la fin du chemin, et renvoie le code 200 avec le corps hérité, aux champs en majuscules et au montant en fils, si c'est un `GET` sur un sinistre connu. Dans tous les autres cas, elle renvoie 404 avec `{"ERR": "NOT_FOUND"}`.

**`statut_sinistre(numero)`** — C'est l'adaptateur, l'interprète qui traduit le jargon du vieux système en phrases que le modèle comprend : la fonction reçoit un numéro de sinistre, appelle `api_rest_heritee` en `GET`, transforme un 404 en `ErreurOutil` qui dit quoi faire, « demander à l'assuré de vérifier le numéro », et un code 5xx en `ErreurOutil` d'indisponibilité. Sinon, elle renvoie un dictionnaire lisible avec le numéro, le statut traduit, « ouvert » pour le code `O`, et le montant converti en dirhams, 1 390 000 fils divisés par 100, soit 13 900,0 AED.

**`afficher_trace(resultat)`** — Ce petit utilitaire est le greffier qui lit à haute voix le procès-verbal d'une session d'agent : il reçoit le dictionnaire renvoyé par `executer_agent`, imprime pour chaque entrée de la trace le nom de l'outil, ses arguments en JSON et sa sortie, puis une dernière ligne avec le statut, le nombre d'étapes et la réponse finale de l'agent. Il ne renvoie rien ; `main` l'appelle après chacun des scénarios 2, 3 et 4, d'où des lignes comme « agent [fini, 3 étapes] ».

**`main()`** — Le chef d'orchestre déroule les cinq scénarios du chapitre : il fait découvrir au host le serveur bancaire, ses trois capacités, ses deux outils, son barème et son prompt, puis fait exécuter par un faux LLM un virement de 12 500 AED approuvé dans l'outil, et rejouer un virement de 9 000 AED que l'humain refuse, sans qu'aucun solde ne bouge. Il branche ensuite l'API héritée de l'assureur derrière MCP, avec un appel réussi, un sinistre inconnu et un dépassement de délai annulé, et mesure enfin vingt appels pour obtenir un p95 de 0,240 seconde sous le SLO de 0,300 seconde ; il ne renvoie rien et n'imprime le message final que si tous les `assert` passent.

```python
"""Étape 47 — scénarios MCP aux Émirats : lecture, virement approuvé dans l'outil, API REST héritée, timeout, p95."""
import json
import math
import sys
from dataclasses import dataclass, field

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- port LLM et boucle (code canonique, recopié tel quel)
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


# ---------------------------------------------------------------- fonctions canoniques du parcours (recopiées)
def p95(valeurs: list[float]) -> float:
    """Percentile 95 au rang le plus proche : la valeur de rang ceil(0,95 × N) dans la liste triée."""
    if not valeurs:
        raise ValueError("liste vide")
    s = sorted(valeurs)
    return s[math.ceil(0.95 * len(s)) - 1]


def iban_ae_valide(iban: str) -> bool:
    """IBAN émirien : 23 caractères, « AE », puis 21 chiffres ; contrôle ISO 13616 mod 97 = 1."""
    s = iban.replace(" ", "").upper()
    if len(s) != 23 or not s.startswith("AE") or not s[2:].isdigit():
        return False
    reorganise = s[4:] + s[:4]
    return int("".join(str(int(c, 36)) for c in reorganise)) % 97 == 1


# ---------------------------------------------------------------- validateur de l'étape 46 (recopié sans changement)
def valider(valeur, schema: dict, chemin: str = "$") -> list[str]:
    """Renvoie la liste des écarts entre `valeur` et `schema` ; liste vide = conforme."""
    t = schema.get("type")
    if t == "object":
        if not isinstance(valeur, dict):
            return [f"{chemin} : objet attendu"]
        erreurs = [f"{chemin}.{c} : champ obligatoire manquant" for c in schema.get("required", []) if c not in valeur]
        proprietes = schema.get("properties", {})
        for cle in sorted(valeur):
            if cle in proprietes:
                erreurs += valider(valeur[cle], proprietes[cle], f"{chemin}.{cle}")
            elif schema.get("additionalProperties") is False:
                erreurs.append(f"{chemin}.{cle} : champ non prévu")
        return erreurs
    if t == "string":
        if not isinstance(valeur, str):
            return [f"{chemin} : chaîne attendue"]
        if len(valeur) < schema.get("minLength", 0) or len(valeur) > schema.get("maxLength", math.inf):
            return [f"{chemin} : longueur {len(valeur)} hors bornes"]
        return []
    if t in ("number", "integer"):
        entier_ok = isinstance(valeur, int) and not isinstance(valeur, bool)
        nombre_ok = entier_ok or isinstance(valeur, float)
        if not (entier_ok if t == "integer" else nombre_ok):
            return [f"{chemin} : {t} attendu"]
        if valeur < schema.get("minimum", -math.inf) or valeur > schema.get("maximum", math.inf):
            return [f"{chemin} : {valeur} hors de [{schema.get('minimum', '-inf')} ; {schema.get('maximum', 'inf')}]"]
        if "exclusiveMinimum" in schema and valeur <= schema["exclusiveMinimum"]:
            return [f"{chemin} : {valeur} doit être > {schema['exclusiveMinimum']}"]
        return []
    raise ValueError(f"type de schéma non géré : {t}")


def objet(**proprietes) -> dict:
    """Schéma d'objet strict : tous les champs obligatoires, aucun champ non prévu."""
    return {"type": "object", "properties": proprietes, "required": sorted(proprietes), "additionalProperties": False}


# ---------------------------------------------------------------- horloge simulée (aucune durée réelle)
class Horloge:
    def __init__(self):
        self.t = 0.0

    def avancer(self, duree: float) -> None:
        self.t = round(self.t + duree, 6)


HORLOGE = Horloge()


# ---------------------------------------------------------------- un serveur MCP générique : tools, resources, prompts
class ErreurOutil(Exception):
    """Échec métier : part dans le résultat avec isError = true."""


class ErreurProtocole(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


@dataclass
class Outil:
    nom: str
    description: str
    schema: dict
    fonction: object
    lecture_seule: bool = True


@dataclass
class Resource:
    uri: str
    nom: str
    texte: str
    mime: str = "text/plain"


@dataclass
class Prompt:
    nom: str
    description: str
    arguments: list
    gabarit: str


class ServeurMCP:
    def __init__(self, nom: str, outils: list, resources: list | None = None, prompts: list | None = None):
        self.nom = nom
        self.outils = {o.nom: o for o in outils}
        self.resources = {r.uri: r for r in resources or []}
        self.prompts = {p.nom: p for p in prompts or []}
        self.journal: list[str] = []

    def capacites(self) -> dict:
        c = {"tools": {"listChanged": False}}
        if self.resources:
            c["resources"] = {"subscribe": False, "listChanged": False}
        if self.prompts:
            c["prompts"] = {"listChanged": False}
        return c

    def traiter(self, ligne: str) -> str | None:
        """Transport en mémoire : une ligne JSON entre, une ligne JSON sort (ou rien pour une notification)."""
        msg = json.loads(ligne)
        if "id" not in msg:
            self.journal.append(f"notification {msg['method']} {json.dumps(msg.get('params', {}), ensure_ascii=False)}")
            return None
        try:
            rep = {"jsonrpc": "2.0", "id": msg["id"], "result": self.executer(msg["method"], msg.get("params", {}))}
        except ErreurProtocole as e:
            rep = {"jsonrpc": "2.0", "id": msg["id"], "error": {"code": e.code, "message": str(e)}}
        return json.dumps(rep, ensure_ascii=False)

    def executer(self, methode: str, p: dict) -> dict:
        if methode == "initialize":
            return {"protocolVersion": "2025-06-18", "capabilities": self.capacites(),
                    "serverInfo": {"name": self.nom, "version": "1.0.0"}}
        if methode == "tools/list":
            return {"tools": [{"name": o.nom, "description": o.description, "inputSchema": o.schema,
                               "annotations": {"readOnlyHint": o.lecture_seule, "destructiveHint": not o.lecture_seule}}
                              for o in self.outils.values()]}
        if methode == "tools/call":
            o = self.outils.get(p.get("name"))
            if o is None:
                raise ErreurProtocole(-32602, f"Unknown tool: {p.get('name')}")
            ecarts = valider(p.get("arguments", {}), o.schema, "$.arguments")
            if ecarts:
                raise ErreurProtocole(-32602, "Invalid params : " + " ; ".join(ecarts))
            try:
                sortie = o.fonction(**p["arguments"])
            except ErreurOutil as e:
                return {"content": [{"type": "text", "text": str(e)}], "isError": True}
            return {"content": [{"type": "text", "text": json.dumps(sortie, ensure_ascii=False)}],
                    "structuredContent": sortie, "isError": False}
        if methode == "resources/list" and self.resources:
            return {"resources": [{"uri": r.uri, "name": r.nom, "mimeType": r.mime} for r in self.resources.values()]}
        if methode == "resources/read" and self.resources:
            r = self.resources.get(p.get("uri"))
            if r is None:
                raise ErreurProtocole(-32002, f"Resource not found: {p.get('uri')}")
            return {"contents": [{"uri": r.uri, "mimeType": r.mime, "text": r.texte}]}
        if methode == "prompts/list" and self.prompts:
            return {"prompts": [{"name": q.nom, "description": q.description,
                                 "arguments": [{"name": a, "required": True} for a in q.arguments]}
                                for q in self.prompts.values()]}
        if methode == "prompts/get" and self.prompts:
            q = self.prompts.get(p.get("name"))
            args = p.get("arguments", {})
            if q is None or sorted(args) != sorted(q.arguments):
                raise ErreurProtocole(-32602, "Invalid params : prompt inconnu ou arguments incomplets")
            return {"description": q.description,
                    "messages": [{"role": "user", "content": {"type": "text", "text": q.gabarit.format(**args)}}]}
        raise ErreurProtocole(-32601, f"Method not found: {methode}")


# ---------------------------------------------------------------- le client du host (transport en mémoire)
class ClientMCP:
    """Même rôle que le client stdio de l'étape 46 ; le transport est un détail, le JSON est le même."""

    def __init__(self, serveur: ServeurMCP, delai_s: float = 5.0):
        self.serveur = serveur
        self.delai_s = delai_s
        self.prochain_id = 1
        self.durees: list[tuple[str, float]] = []
        self.dernier_echange: tuple[str, str] = ("", "")

    def requete(self, methode: str, params: dict | None = None) -> dict:
        id_ = self.prochain_id
        self.prochain_id += 1
        ligne = json.dumps({"jsonrpc": "2.0", "id": id_, "method": methode, "params": params or {}}, ensure_ascii=False)
        debut = HORLOGE.t
        rep_ligne = self.serveur.traiter(ligne)
        duree = round(HORLOGE.t - debut, 6)
        self.durees.append((methode, duree))
        if duree > self.delai_s:              # le client a cessé d'attendre : il annule et ignore la réponse tardive
            self.notifier("notifications/cancelled", {"requestId": id_, "reason": f"timeout client de {self.delai_s} s"})
            raise TimeoutError(f"{methode} : aucune réponse en {self.delai_s} s, requête {id_} annulée")
        self.dernier_echange = (ligne, rep_ligne)
        return json.loads(rep_ligne)

    def notifier(self, methode: str, params: dict) -> None:
        self.serveur.traiter(json.dumps({"jsonrpc": "2.0", "method": methode, "params": params}, ensure_ascii=False))


class ErreurOutilDistant(Exception):
    """Un résultat isError = true, remonté à la boucle d'agent qui le renvoie au modèle."""


def outils_pour_agent(client: ClientMCP) -> tuple[dict, list]:
    """Transforme tools/list en (fonctions appelables par executer_agent, définitions d'outils pour le modèle)."""
    liste = client.requete("tools/list")["result"]["tools"]

    def fabriquer(nom: str):
        def appeler(**arguments):
            rep = client.requete("tools/call", {"name": nom, "arguments": arguments})
            if "error" in rep:
                raise RuntimeError(f"erreur MCP {rep['error']['code']} : {rep['error']['message']}")
            if rep["result"]["isError"]:
                raise ErreurOutilDistant(rep["result"]["content"][0]["text"])
            return rep["result"]["structuredContent"]
        return appeler

    outils = {o["name"]: fabriquer(o["name"]) for o in liste}
    schemas = [{"name": o["name"], "description": o["description"], "input_schema": o["inputSchema"]} for o in liste]
    return outils, schemas


# ---------------------------------------------------------------- serveur 1 : paiements d'une banque de détail
IBAN_CLIENT = "AE070331234567890123456"
IBAN_PROPRIETAIRE = "AE490339876543210987654"
SOLDES_AED = {IBAN_CLIENT: 48250.75, IBAN_PROPRIETAIRE: 3100.00}   # soldes fictifs
VIREMENTS: list[dict] = []
DEMANDES_APPROBATION: list[str] = []
APPROBATEUR = {"decision": ("refusé", "aucun approbateur configuré")}   # l'humain, simulé par scénario


def solde_compte(iban: str) -> dict:
    cle = iban.replace(" ", "")
    if not iban_ae_valide(cle) or cle not in SOLDES_AED:
        raise ErreurOutil(f"compte introuvable ou IBAN invalide : {iban}")
    HORLOGE.avancer(0.12)
    return {"iban": cle, "solde_aed": SOLDES_AED[cle]}


def initier_virement(iban_source: str, iban_beneficiaire: str, montant_aed: float, reference: str) -> dict:
    src, dst = iban_source.replace(" ", ""), iban_beneficiaire.replace(" ", "")
    if not (iban_ae_valide(src) and iban_ae_valide(dst)):
        raise ErreurOutil("IBAN invalide : le contrôle mod 97 échoue")
    if SOLDES_AED.get(src, 0.0) < montant_aed:
        raise ErreurOutil("solde insuffisant")
    demande = f"{montant_aed:.2f} AED de {src[:4]}…{src[-3:]} vers {dst[:4]}…{dst[-3:]}, réf. {reference}"
    DEMANDES_APPROBATION.append(demande)
    decision, motif = APPROBATEUR["decision"]          # l'approbation se fait DANS l'outil, à chaque appel
    if decision != "approuvé":
        raise ErreurOutil(f"refusé par l'humain : {motif}")
    SOLDES_AED[src] = round(SOLDES_AED[src] - montant_aed, 2)
    SOLDES_AED[dst] = round(SOLDES_AED[dst] + montant_aed, 2)
    VIREMENTS.append({"reference": reference, "montant_aed": montant_aed})
    HORLOGE.avancer(0.35)
    return {"statut": "exécuté", "reference": reference, "nouveau_solde_aed": SOLDES_AED[src]}


SCHEMA_IBAN = {"type": "string", "minLength": 23, "maxLength": 29}   # 23 caractères, ou 29 avec les espaces

SERVEUR_BANQUE = ServeurMCP(
    "banque-paiements",
    outils=[
        Outil("solde_compte", "Solde d'un compte, en AED. Lecture seule.",
              objet(iban=SCHEMA_IBAN), solde_compte),
        Outil("initier_virement", "Initie un virement en AED. Écriture : demande l'approbation d'un humain avant d'exécuter.",
              objet(iban_source=SCHEMA_IBAN, iban_beneficiaire=SCHEMA_IBAN,
                    montant_aed={"type": "number", "exclusiveMinimum": 0, "maximum": 50000},
                    reference={"type": "string", "minLength": 6, "maxLength": 20}),
              initier_virement, lecture_seule=False),
    ],
    resources=[Resource("banque://baremes/frais-virement", "Barème des frais de virement",
                        "Virement domestique en AED : sans frais (barème illustratif).\n"
                        "Plafond par virement initié par l'assistant : 50 000 AED ; au-delà, agence.")],
    prompts=[Prompt("preparer_virement", "Prépare un virement à faire approuver.", ["montant_aed", "beneficiaire"],
                    "Prépare un virement de {montant_aed} AED vers {beneficiaire}. "
                    "Vérifie le solde, puis initie le virement : l'approbation sera demandée.")],
)


# ---------------------------------------------------------------- serveur 2 : une API REST héritée d'assureur, derrière MCP
SINISTRES_HERITES = {"CLM-2026-0042": {"CLM_NO": "CLM-2026-0042", "STATUS_CD": "O", "AMT_FILS": 1390000}}
STATUTS = {"O": "ouvert", "P": "en paiement", "C": "clos"}
LATENCES_HERITEES: list[float] = []      # durée simulée de chaque appel, consommée dans l'ordre


def api_rest_heritee(methode: str, chemin: str) -> tuple[int, dict]:
    """Le système existant, qu'on ne modifie pas : codes HTTP, champs en majuscules, montants en fils."""
    HORLOGE.avancer(LATENCES_HERITEES.pop(0) if LATENCES_HERITEES else 0.15)
    numero = chemin.rsplit("/", 1)[-1]
    if methode == "GET" and chemin.startswith("/api/v1/claims/") and numero in SINISTRES_HERITES:
        return 200, SINISTRES_HERITES[numero]
    return 404, {"ERR": "NOT_FOUND"}


def statut_sinistre(numero: str) -> dict:
    """L'adaptateur forward-deployed : traduit le contrat hérité en un outil lisible par le modèle."""
    code, corps = api_rest_heritee("GET", f"/api/v1/claims/{numero}")
    if code == 404:
        raise ErreurOutil(f"sinistre inconnu : {numero}. Demander à l'assuré de vérifier le numéro.")
    if code >= 500:
        raise ErreurOutil(f"système de sinistres indisponible (HTTP {code})")
    return {"sinistre": corps["CLM_NO"], "statut": STATUTS[corps["STATUS_CD"]],
            "montant_evalue_aed": corps["AMT_FILS"] / 100}   # 1 AED = 100 fils


SERVEUR_ASSURANCE = ServeurMCP("assurance-sinistres", outils=[
    Outil("statut_sinistre", "Statut et montant évalué d'un sinistre, en AED. Lecture seule.",
          objet(numero={"type": "string", "minLength": 13, "maxLength": 13}), statut_sinistre)])


def afficher_trace(resultat: dict) -> None:
    for nom, args, sortie in resultat["trace"]:
        print(f"  outil {nom}({json.dumps(args, ensure_ascii=False)}) -> {sortie}")
    print(f"  agent [{resultat['statut']}, {resultat['etapes']} étapes] : {resultat.get('reponse', '')}")


def main() -> None:
    print("1. Banque : le host découvre le serveur banque-paiements")
    client = ClientMCP(SERVEUR_BANQUE)
    init = client.requete("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                         "clientInfo": {"name": "host-banque", "version": "1.0.0"}})["result"]
    client.notifier("notifications/initialized", {})
    outils, schemas = outils_pour_agent(client)
    annotations = {o["name"]: o["annotations"] for o in client.requete("tools/list")["result"]["tools"]}
    print(f"  capacités : {sorted(init['capabilities'])} ; outils : {sorted(outils)}")
    assert sorted(init["capabilities"]) == ["prompts", "resources", "tools"]
    assert annotations["initier_virement"]["destructiveHint"] is True
    bareme = client.requete("resources/read", {"uri": "banque://baremes/frais-virement"})["result"]["contents"][0]
    print(f"  resource lue par le host : {bareme['uri']} ({bareme['mimeType']}, {len(bareme['text'].splitlines())} lignes)")
    prompt = client.requete("prompts/get", {"name": "preparer_virement",
                                            "arguments": {"montant_aed": "12500", "beneficiaire": "AE49 0339 8765 4321 0987 654"}})
    consigne = prompt["result"]["messages"][0]["content"]["text"]
    print(f"  prompt choisi par l'usager : « {consigne[:60]}… »")
    assert consigne.startswith("Prépare un virement de 12500 AED")
    rep = client.requete("resources/read", {"uri": "banque://baremes/inconnu"})
    assert rep["error"]["code"] == -32002

    print("2. Banque : virement de 12 500 AED, approuvé par l'humain DANS l'outil")
    APPROBATEUR["decision"] = ("approuvé", "")
    system = "Agent de paiements. Lis le barème fourni. Tout virement passe par initier_virement.\n" + bareme["text"]
    args_virement = {"iban_source": "AE07 0331 2345 6789 0123 456", "iban_beneficiaire": "AE49 0339 8765 4321 0987 654",
                     "montant_aed": 12500, "reference": "VIR-2026-0001"}
    script = [
        Reponse("tool_use", [appel_outil("solde_compte", {"iban": "AE07 0331 2345 6789 0123 456"}, "t1")]),
        Reponse("tool_use", [appel_outil("initier_virement", args_virement, "t2")]),
        Reponse("end_turn", [texte("Virement de 12 500 AED exécuté, réf. VIR-2026-0001 ; nouveau solde 35 750,75 AED.")]),
    ]
    r = executer_agent(FakeLLM(script), system, consigne, outils, schemas)
    afficher_trace(r)
    requete_json, reponse_json = client.dernier_echange
    print(f"  JSON de la requête : {requete_json}")
    print(f"  JSON de la réponse : {reponse_json}")
    print(f"  approbation demandée : {DEMANDES_APPROBATION[-1]}")
    assert r["statut"] == "fini" and r["etapes"] == 3
    assert r["trace"][1][2] == {"statut": "exécuté", "reference": "VIR-2026-0001", "nouveau_solde_aed": 35750.75}
    assert len(VIREMENTS) == 1 and SOLDES_AED[IBAN_PROPRIETAIRE] == 15600.0

    print("3. Banque : le même type de virement, refusé par l'humain")
    APPROBATEUR["decision"] = ("refusé", "bénéficiaire non reconnu par le client")
    args_refus = dict(args_virement, montant_aed=9000, reference="VIR-2026-0002")
    script = [
        Reponse("tool_use", [appel_outil("initier_virement", args_refus, "t3")]),
        Reponse("end_turn", [texte("Le virement n'a pas été exécuté : il a été refusé lors de l'approbation.")]),
    ]
    r = executer_agent(FakeLLM(script), system, "Envoie 9 000 AED au même bénéficiaire.", outils, schemas)
    afficher_trace(r)
    assert r["trace"][0][2] == "ERREUR refusé par l'humain : bénéficiaire non reconnu par le client"
    assert len(VIREMENTS) == 1 and len(DEMANDES_APPROBATION) == 2 and SOLDES_AED[IBAN_CLIENT] == 35750.75

    print("4. Assurance : une API REST héritée placée derrière MCP (forward-deployed)")
    client_a = ClientMCP(SERVEUR_ASSURANCE, delai_s=5.0)
    client_a.requete("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                    "clientInfo": {"name": "host-assurance", "version": "1.0.0"}})
    client_a.notifier("notifications/initialized", {})
    outils_a, schemas_a = outils_pour_agent(client_a)
    LATENCES_HERITEES[:] = [0.18, 0.21, 6.0]
    script = [
        Reponse("tool_use", [appel_outil("statut_sinistre", {"numero": "CLM-2026-0042"}, "a1")]),
        Reponse("tool_use", [appel_outil("statut_sinistre", {"numero": "CLM-2026-9999"}, "a2")]),
        Reponse("tool_use", [appel_outil("statut_sinistre", {"numero": "CLM-2026-0042"}, "a3")]),
        Reponse("end_turn", [texte("CLM-2026-0042 est ouvert (13 900 AED évalués). Le numéro CLM-2026-9999 est "
                                   "introuvable ; le système de sinistres ne répond plus, je reviens vers vous.")]),
    ]
    r = executer_agent(FakeLLM(script), "Agent sinistres.", "Où en sont mes deux sinistres ?", outils_a, schemas_a)
    afficher_trace(r)
    assert r["trace"][0][2] == {"sinistre": "CLM-2026-0042", "statut": "ouvert", "montant_evalue_aed": 13900.0}
    assert r["trace"][1][2].startswith("ERREUR sinistre inconnu")                  # isError : un échec métier
    assert r["trace"][2][2].startswith("ERREUR tools/call : aucune réponse en 5.0 s")   # timeout côté client
    print(f"  journal du serveur : {SERVEUR_ASSURANCE.journal[-1]}")
    assert SERVEUR_ASSURANCE.journal[-1].startswith('notification notifications/cancelled {"requestId": 5')

    print("5. p95 au rang le plus proche sur 20 appels de l'outil hérité")
    latences_ms = [120, 95, 180, 240, 110, 130, 105, 900, 150, 99, 101, 140, 160, 170, 115, 125, 135, 145, 155, 165]
    LATENCES_HERITEES[:] = [ms / 1000 for ms in latences_ms]
    client_a.durees.clear()
    for _ in latences_ms:
        client_a.requete("tools/call", {"name": "statut_sinistre", "arguments": {"numero": "CLM-2026-0042"}})
    mesures = [d for m, d in client_a.durees]
    moyenne = sum(mesures) / len(mesures)
    print(f"  N = {len(mesures)} ; rang = ceil(0.95 × 20) = {math.ceil(0.95 * 20)} ; p95 = {p95(mesures):.3f} s ; "
          f"moyenne = {moyenne:.3f} s ; max = {max(mesures):.3f} s")
    slo = 0.300
    print(f"  SLO p95 ≤ {slo:.3f} s : {'respecté' if p95(mesures) <= slo else 'violé'}")
    assert p95(mesures) == 0.240 and round(moyenne, 3) == 0.177 and max(mesures) == 0.900
    assert p95(mesures) <= slo < max(mesures)
    assert sum(1 for x in mesures if x <= p95(mesures)) >= 0.95 * len(mesures)
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Banque : le host découvre le serveur banque-paiements
  capacités : ['prompts', 'resources', 'tools'] ; outils : ['initier_virement', 'solde_compte']
  resource lue par le host : banque://baremes/frais-virement (text/plain, 2 lignes)
2. Banque : virement de 12 500 AED, approuvé par l'humain DANS l'outil
  outil solde_compte({"iban": "AE07 0331 2345 6789 0123 456"}) -> {'iban': 'AE070331234567890123456', 'solde_aed': 48250.75}
…
  agent [fini, 3 étapes] : Virement de 12 500 AED exécuté, réf. VIR-2026-0001 ; nouveau solde 35 750,75 AED.
…
  approbation demandée : 12500.00 AED de AE07…456 vers AE49…654, réf. VIR-2026-0001
3. Banque : le même type de virement, refusé par l'humain
…
  agent [fini, 2 étapes] : Le virement n'a pas été exécuté : il a été refusé lors de l'approbation.
4. Assurance : une API REST héritée placée derrière MCP (forward-deployed)
  outil statut_sinistre({"numero": "CLM-2026-0042"}) -> {'sinistre': 'CLM-2026-0042', 'statut': 'ouvert', 'montant_evalue_aed': 13900.0}
  outil statut_sinistre({"numero": "CLM-2026-9999"}) -> ERREUR sinistre inconnu : CLM-2026-9999. Demander à l'assuré de vérifier le numéro.
  outil statut_sinistre({"numero": "CLM-2026-0042"}) -> ERREUR tools/call : aucune réponse en 5.0 s, requête 5 annulée
…
  journal du serveur : notification notifications/cancelled {"requestId": 5, "reason": "timeout client de 5.0 s"}
5. p95 au rang le plus proche sur 20 appels de l'outil hérité
  N = 20 ; rang = ceil(0.95 × 20) = 19 ; p95 = 0.240 s ; moyenne = 0.177 s ; max = 0.900 s
  SLO p95 ≤ 0.300 s : respecté
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : avec MCP, la boucle d'agent ne change pas. Ce qui change, c'est l'endroit où se placent les contrôles : le schéma et les capacités dans le serveur, l'approbation dans l'outil d'écriture, le délai et l'annulation dans le client, la mesure du p95 dans le host.

## Squelette algorithmique

Le programme repose sur cinq algorithmes : le serveur générique qui répartit les méthodes MCP, le client qui mesure chaque appel et l'annule au-delà de son délai, l'adaptateur qui branche les outils MCP sur la boucle d'agent, l'outil d'écriture qui demande l'approbation, et le calcul du p95. Dans les complexités, L est la longueur d'une ligne JSON, a la taille des arguments, n_o le nombre d'outils d'un serveur et N le nombre de durées mesurées.

### Serveur générique : tools, resources, prompts

Entrée : une ligne JSON. Sortie : une ligne JSON de réponse, ou rien pour une notification. Idée : une seule table de méthodes, et des capacités qui ne déclarent que ce qui existe.

```text
ALGORITHME Executer
ENTRÉES : méthode, p (paramètres) ; outils, resources, prompts du serveur
SORTIE  : un résultat, ou une ErreurProtocole(code)
  SI méthode = "initialize" ALORS
    RETOURNER {version, capacités ← {tools} ∪ {resources si resources ≠ ∅} ∪ {prompts si prompts ≠ ∅}}
  SINON SI méthode = "tools/list" ALORS
    RETOURNER [ (nom, description, schéma, readOnlyHint, destructiveHint) POUR chaque outil ]
  SINON SI méthode = "tools/call" ALORS
    SI p.name ∉ outils ALORS lever ErreurProtocole(−32602) FIN SI
    SI Valider(p.arguments) ≠ ∅ ALORS lever ErreurProtocole(−32602) FIN SI
    ESSAYER RETOURNER succès(outil(p.arguments))
    SI échec métier e ALORS RETOURNER {texte(e), isError ← VRAI}
  SINON SI méthode = "resources/read" ET resources ≠ ∅ ALORS
    SI p.uri ∉ resources ALORS lever ErreurProtocole(−32002) FIN SI
    RETOURNER {contents ← [(uri, mimeType, texte)]}
  SINON SI méthode = "prompts/get" ET prompts ≠ ∅ ALORS
    SI p.name ∉ prompts OU clés(p.arguments) ≠ arguments attendus ALORS lever ErreurProtocole(−32602) FIN SI
    RETOURNER {messages ← [(user, gabarit rempli avec p.arguments)]}
  SINON
    lever ErreurProtocole(−32601)
  FIN SI
```

**Complexité :** `tools/list` coûte O(Σ taille des définitions), parce que chaque définition est recopiée une fois dans la réponse. `tools/call` coûte O(L + a + k log k) comme à l'étape 46 (analyse, validation, tri des clés), plus le coût de l'outil. `resources/read` coûte O(1) pour la recherche dans un dictionnaire et O(taille du texte) pour la sérialisation ; `prompts/get` coûte O(q log q) pour comparer les q noms d'arguments triés et O(taille du gabarit) pour le remplir. En mémoire, O(L) par requête : le serveur ne garde que son journal de notifications.

**Du squelette au code :** `Executer` est `ServeurMCP.executer`, appelé par `ServeurMCP.traiter`, qui transforme une `ErreurProtocole` en réponse `error` ; les capacités viennent de `ServeurMCP.capacites`, la validation de `valider`, et les trois sortes de primitives des dataclasses `Outil`, `Resource` et `Prompt`.

### Client avec délai et annulation

Entrée : une méthode et ses paramètres. Sortie : la réponse, ou une `TimeoutError` après avoir notifié l'annulation. Idée : mesurer la durée sur l'horloge simulée et se comporter comme un client qui aurait cessé d'attendre.

```text
ALGORITHME RequeteAvecDelai
ENTRÉES : méthode, params ; délai δ (5 s) ; horloge simulée H
SORTIE  : réponse, ou ERREUR « timeout »
  id ← prochain_id ; prochain_id ← prochain_id + 1
  début ← H.t
  r ← serveur.traiter(JSON(id, méthode, params))       ▷ l'outil fait avancer H
  durée ← H.t − début
  ajouter (méthode, durée) aux durées mesurées
  SI durée > δ ALORS
    notifier "notifications/cancelled" avec requestId ← id
    lever ERREUR « aucune réponse en δ s »              ▷ la réponse tardive est ignorée
  FIN SI
  RETOURNER décoder(r)
```

**Complexité :** O(L) en temps de calcul pour sérialiser et décoder ; O(1) de plus pour la mesure et l'éventuelle notification. En mémoire, O(L) pour l'échange courant, et O(R) pour la liste des durées d'une session de R requêtes, que l'on garde pour le p95.

**Du squelette au code :** c'est `ClientMCP.requete` : `debut = HORLOGE.t`, `self.serveur.traiter(ligne)`, `duree = round(HORLOGE.t - debut, 6)`, `self.durees.append(...)`, puis `self.notifier("notifications/cancelled", ...)` et `raise TimeoutError(...)` si `duree > self.delai_s`.

### Brancher les outils MCP sur la boucle d'agent

Entrée : un client initialisé. Sortie : un dictionnaire nom → fonction pour `executer_agent`, et les définitions d'outils pour le modèle. Idée : chaque fonction fait un `tools/call` et transforme un échec en exception, que la boucle canonique renvoie au modèle.

```text
ALGORITHME OutilsPourAgent
ENTRÉES : client
SORTIE  : (fonctions, définitions)
  liste ← client.requete("tools/list").tools
  fonctions ← {} ; définitions ← []
  POUR chaque outil o DANS liste FAIRE
    fonctions[o.name] ← fonction(arguments) :
        r ← client.requete("tools/call", {name ← o.name, arguments})
        SI r contient error ALORS lever ERREUR protocole FIN SI
        SI r.result.isError ALORS lever ERREUR outil(r.result.content[0].text) FIN SI
        RETOURNER r.result.structuredContent
    ajouter (o.name, o.description, o.inputSchema) à définitions
  FIN POUR
  RETOURNER (fonctions, définitions)
```

**Complexité :** O(Σ taille des définitions) une seule fois, pour `tools/list` et la construction des deux structures ; ensuite O(L) par appel d'outil. En mémoire, O(n_o) fonctions et définitions.

**Du squelette au code :** c'est `outils_pour_agent` et sa fonction interne `fabriquer`, qui produit `appeler(**arguments)` ; les deux erreurs sont `RuntimeError` et `ErreurOutilDistant`. La boucle `executer_agent` les attrape dans son `except Exception` et renvoie au modèle un `tool_result` avec `is_error`.

### Outil d'écriture approuvé dans l'outil

Entrée : les arguments validés du virement. Sortie : le statut, ou un échec « refusé par l'humain ». Idée : tous les contrôles avant la demande d'approbation, et toutes les écritures après la décision.

```text
ALGORITHME InitierVirement
ENTRÉES : source, bénéficiaire, montant, référence ; approbateur
SORTIE  : {statut, référence, nouveau solde}, ou échec métier
  SI source ou bénéficiaire ne passe pas le contrôle mod 97 ALORS échec "IBAN invalide" FIN SI
  SI solde(source) < montant ALORS échec "solde insuffisant" FIN SI
  demande ← (montant, source masquée, bénéficiaire masqué, référence)   ▷ construite par l'outil
  (décision, motif) ← approbateur(demande)                              ▷ à chaque appel, sans mémoire
  SI décision ≠ "approuvé" ALORS échec "refusé par l'humain : " + motif FIN SI
  solde(source) ← solde(source) − montant
  solde(bénéficiaire) ← solde(bénéficiaire) + montant
  enregistrer le virement
  RETOURNER {statut ← "exécuté", référence, nouveau solde}
```

**Complexité :** O(1) en temps et en mémoire, parce que le contrôle mod 97 porte sur 23 caractères, longueur fixe, et que les soldes sont dans un dictionnaire. Le temps réel est dominé par l'attente de la décision humaine, que l'étape 66 bornera par un délai qui vaut refus.

**Du squelette au code :** c'est `initier_virement` ; les contrôles appellent `iban_ae_valide`, la demande est ajoutée à `DEMANDES_APPROBATION`, la décision est lue dans `APPROBATEUR["decision"]`, et les trois écritures (`SOLDES_AED[src]`, `SOLDES_AED[dst]`, `VIREMENTS.append`) sont après le `raise`. L'adaptateur de l'API héritée, `statut_sinistre`, suit le même schéma, sans approbation : appeler `api_rest_heritee`, puis traduire 404 et 5xx en échec métier et 200 en objet lisible.

### p95 au rang le plus proche

Entrée : N durées mesurées. Sortie : la durée de rang ⌈0,95 N⌉. Idée : trier, puis lire une seule case.

```text
ALGORITHME P95
ENTRÉES : x₁, …, x_N, avec N ≥ 1
SORTIE  : p95
  SI N = 0 ALORS ERREUR "liste vide" FIN SI
  s ← trier(x)                               ▷ ordre croissant
  k ← ⌈0,95 × N⌉
  RETOURNER s[k]                             ▷ indice 1 ; s[k − 1] en Python
```

**Complexité :** O(N log N) en temps pour le tri, puis O(1) pour la lecture ; O(N) en mémoire pour la copie triée, parce que `sorted` ne modifie pas la liste d'origine. Un algorithme de sélection ramènerait le temps à O(N) en moyenne, ce qui n'a d'intérêt que pour de très grandes fenêtres.

**Du squelette au code :** c'est la fonction canonique `p95`, appelée dans la section 5 de `main()` sur `mesures`, la liste des durées tirée de `client_a.durees`.

## Cas d'usage réels aux Émirats

Les soldes, latences, plafonds et seuils sont illustratifs ; les règles citées sont à confirmer avec le texte en vigueur.

### Banque — un virement que seul un humain peut autoriser

Une banque de détail de Dubaï offre à ses clients un assistant qui prépare les virements domestiques en AED, par exemple le loyer mensuel versé au propriétaire. Le client choisit dans le menu de l'application le prompt `preparer_virement`, avec 12 500 AED et l'IBAN du bénéficiaire ; le host a déjà lu la resource `banque://baremes/frais-virement` et l'a placée dans le prompt système, si bien que l'agent connaît les frais et le plafond de 50 000 AED sans appeler d'outil. L'agent appelle d'abord `solde_compte`, qui renvoie 48 250,75 AED, puis `initier_virement` avec la référence `VIR-2026-0001`. L'outil vérifie les deux IBAN par mod 97, vérifie le solde, puis demande l'approbation : « 12500.00 AED de AE07…456 vers AE49…654, réf. VIR-2026-0001 ». Le client confirme dans l'application, l'outil débite le compte et renvoie un nouveau solde de 35 750,75 AED, que l'agent annonce. Sans approbation dans l'outil, une phrase injectée dans un relevé ou un e-mail pourrait suffire à déclencher un virement. On suit le taux de virements approuvés du premier coup et le délai entre la demande d'approbation et la décision.

### Banque — un refus qui ne se transforme pas en succès

Le même client demande ensuite d'envoyer 9 000 AED au même bénéficiaire, mais refuse au moment de l'approbation : il ne reconnaît pas le compte, qui a été modifié dans une conversation précédente. L'outil lève alors `ErreurOutil("refusé par l'humain : bénéficiaire non reconnu par le client")` **avant** toute écriture, et le serveur renvoie un résultat avec `isError: true`. La boucle d'agent transmet ce résultat au modèle avec `is_error`, et le modèle répond que le virement n'a pas été exécuté, au lieu d'annoncer un succès. Le programme vérifie que le nombre de virements reste à 1, que le solde reste à 35 750,75 AED et que deux approbations ont été demandées, une par appel. Sans ce contrôle, une réponse polie du modèle (« c'est fait ») masquerait une opération qui n'a pas eu lieu, ou pire, une opération qui a eu lieu sans accord. La banque suit la part des refus par type de bénéficiaire, un signal précoce de fraude au changement de coordonnées bancaires.

### Assurance — une API REST héritée placée derrière MCP

Un assureur auto et santé possède un système de sinistres ancien, exposé par une API REST interne : `GET /api/v1/claims/CLM-2026-0042` renvoie des champs en majuscules (`CLM_NO`, `STATUS_CD`) et des montants en fils, la centième partie du dirham. Un ingénieur déployé chez l'assureur (forward-deployed) ne touche pas à ce système : il écrit un adaptateur MCP, l'outil `statut_sinistre`, qui appelle l'API, traduit `"O"` en « ouvert » et 1 390 000 fils en 13 900 AED, et transforme un 404 en résultat `isError` lisible : « sinistre inconnu : CLM-2026-9999. Demander à l'assuré de vérifier le numéro. » L'agent de première ligne, qui ne connaît que l'outil MCP, répond à l'assuré dans sa langue sans jamais voir les codes internes. Sans cet adaptateur, il faudrait soit réécrire le système de sinistres, soit donner au modèle la documentation de l'API et le laisser construire des URL, ce qui ouvre la porte à des appels non prévus. L'assurance étant supervisée par la CBUAE, chaque appel de l'adaptateur est journalisé avec le numéro de sinistre et le code HTTP reçu. On suit la part des `isError` par code HTTP d'origine.

### Assurance — un timeout qui ne fige pas la conversation

Lors d'une fin de mois chargée, le système de sinistres met 6 secondes à répondre, alors que le client MCP du host n'attend que 5 secondes. Au bout de 5 s, le client abandonne, envoie `notifications/cancelled` avec l'`id` 5 de la requête et lève `TimeoutError`. La boucle canonique attrape l'exception et la renvoie au modèle comme un résultat d'outil en erreur, et le modèle répond à l'assuré qu'il reviendra vers lui, au lieu de laisser la conversation muette. Le système hérité, lui, a bien fini son travail à 6 s : la réponse est simplement ignorée (démonstration, point 4). Mesurées sur 20 appels, les durées donnent un p95 de 0,240 s, sous le SLO de 0,300 s, alors que le pire appel dure 0,900 s : c'est le p95, et non le maximum ni la moyenne, que l'équipe suit et compare au SLO. Sans timeout côté client, un seul appel lent bloquerait la conversation, puis, si les appels s'empilent, toutes les conversations servies par la même instance.

### Immobilier — une resource pour les comparables, un prompt pour la fiche

Une agence et un promoteur de Dubaï et d'Abu Dhabi exposent un serveur MCP avec un outil de recherche de biens, une resource par quartier (les transactions comparables en AED/sqft issues des enregistrements DLD) et un prompt `fiche_bien`. Quand un conseiller ouvre le dossier d'un appartement de 1 250 sqft, le host lit la resource du quartier et l'injecte dans le contexte, comme le barème du scénario 1 : la lecture est décidée par l'application, une fois, et non par le modèle à chaque tour. Le conseiller choisit ensuite le prompt `fiche_bien`, qui produit la consigne en anglais et en arabe. Le prix estimé et les frais de transfert DLD de 4 % viennent d'outils, jamais du modèle. Sans resource, le modèle relancerait la même recherche à chaque question et paierait plusieurs fois les mêmes tokens ; sans prompt partagé, chaque conseiller écrirait sa propre consigne et les fiches ne se ressembleraient plus. On suit le nombre d'appels d'outil par fiche produite.

### RH — une écriture réglementée derrière la même approbation

Un cabinet RH multi-émirats prépare chaque mois, pour ses clients, le fichier de salaires déposé dans le système de protection des salaires (WPS) sous la supervision du MOHRE. Le serveur MCP de paie expose des outils de lecture (contrats, présence) et un seul outil d'écriture, `deposer_fichier_wps`, construit exactement comme `initier_virement` : contrôles, puis demande d'approbation au gestionnaire de paie, puis dépôt, ou `isError` « refusé par l'humain ». Le schéma de l'outil plafonne le nombre de salariés par fichier et exige la référence du mois, qui sert de clé d'idempotence (étape 12) si un timeout oblige à relancer. Sans approbation, une erreur de l'agent sur un seul salaire se propagerait à des dizaines de salariés, avec un retard de paiement que l'employeur devrait ensuite justifier. On suit le nombre de fichiers rejetés après dépôt, avec un objectif de zéro.

### Crypto — un serveur de lecture, et des timeouts qui ne se cumulent pas

Une plateforme d'actifs virtuels agréée par la VARA donne à son agent de surveillance un serveur MCP de lecture seule sur les carnets d'ordres. Les outils sont annotés `readOnlyHint: true`, mais le host ne s'y fie pas : le serveur d'exécution des ordres est simplement absent de la configuration de cet agent. En période de forte volatilité, le fournisseur de données ralentit : le client coupe chaque appel à 2 s et l'agent signale l'alerte avec la dernière donnée valide et son âge, au lieu d'attendre. Un timeout étant ambigu, l'agent ne relance qu'une fois, et seulement les lectures. Sans délai côté client, trois outils lents en série figeraient l'agent pendant que le marché bouge. On suit le p95 par outil et le nombre d'alertes émises avec une donnée de plus de 60 secondes.

## Pièges et limites

- **Approuver une fois pour toutes.** Une approbation mise en cache (« le client a déjà dit oui ce matin ») ouvre la porte à un deuxième virement que personne n'a vu. La décision se lit à chaque appel, sur la demande exacte : montant, bénéficiaire, référence.
- **Montrer à l'approbateur ce que le modèle dit, et non ce que l'outil va faire.** La demande d'approbation est construite par l'outil à partir des arguments validés, pas à partir du texte du modèle, qui peut être trompeur.
- **Relancer une écriture après un timeout sans clé d'idempotence.** Le serveur a peut-être exécuté le virement (démonstration, point 4) ; la référence `VIR-2026-0001` doit servir de clé, vérifiée par le système bancaire lui-même.
- **Exposer l'API héritée telle quelle.** Donner au modèle les URL et les codes internes revient à lui confier l'intégration. L'adaptateur traduit le contrat, borne les arguments et transforme chaque code HTTP en un message qui dit quoi faire.
- **Piloter un SLO sur la moyenne ou sur un trop petit échantillon.** Sur 20 appels, le p95 repose sur un seul appel au-dessus de lui ; on calcule le p95 sur une fenêtre d'au moins quelques centaines d'appels avant d'en tirer une alerte.

### Exercice feuille blanche

1. Sans regarder le code, écrire `initier_virement` avec ses quatre contrôles dans l'ordre (IBAN, solde, demande d'approbation, décision) et vérifier qu'avec `("refusé", "test")` aucun solde ne change.
2. Prédire, puis vérifier : si l'on remplace la latence 6,0 s par 4,9 s dans le scénario 4, que devient la trace, et que répond l'agent ? (Réponse : le troisième appel réussit et renvoie le statut « ouvert », donc l'`assert` qui attend un timeout échoue. Le script du faux LLM, inchangé, répondrait pourtant que le système ne répond plus : un faux LLM scripté ne réagit pas aux résultats, c'est pourquoi on vérifie la trace, et pas seulement le texte final.)
3. Trouver le bug : une variante place `VIREMENTS.append(...)` avant `decision, motif = APPROBATEUR["decision"]`. Quel `assert` du scénario 3 échoue ? (Réponse : `len(VIREMENTS) == 1`, qui vaut alors 2.)
4. Calculer à la main le p95 au rang le plus proche de 40 durées, sachant que les trois plus grandes valent 0,8 s, 1,2 s et 3,0 s et que la quatrième plus grande vaut 0,31 s. (Réponse : k = 38, la 38e valeur triée est la troisième plus grande, 0,8 s.)

## Pour aller plus loin

L'élicitation (étape 46) permet de demander l'approbation par le protocole lui-même : le serveur envoie `elicitation/create` avec un petit schéma (« confirmer le virement : oui ou non »), et c'est le host qui affiche la question à l'utilisateur. Dans ce fichier, l'approbation est une fonction injectée, ce qui revient au même pour la logique de l'outil. Les notifications de progression permettent aussi à un outil long de signaler son avancement plutôt que de risquer un timeout.

> Suite : [MCP par domaine](<48-MCP-Applications-Domaines.md>) — étape 48.
