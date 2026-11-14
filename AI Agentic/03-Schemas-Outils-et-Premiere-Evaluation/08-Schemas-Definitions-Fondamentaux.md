# Étape 8 — Schémas — Définitions fondamentales

> Étape 8 du parcours · Prérequis : [Score de conformité du prompt](<../02-LLM-Softmax-et-Prompts/07-Prompts-Formule-Taux-de-Conformite.md>) · Suite : [Six schémas EAU vérifiés](<09-Schemas-Exemples-Cas-Usage.md>)

**Dossier :** 03-Schemas-Outils-et-Premiere-Evaluation  
**Métiers :** AI Engineers, Product Engineers, AI Agent Ops

Ce fichier ouvre le bloc « forme, outil, boucle » (étapes 8 à 13). Aux étapes 4 à 7, le prompt disait au modèle quoi faire ; ici, on fixe la forme exacte de ce qu'il doit rendre, et on vérifie cette forme avant que l'agent n'agisse. À la fin, vous saurez écrire de mémoire un validateur JSON Schema, une boucle de réparation et un objet typé équivalent, puis expliquer pourquoi le mode « strict » d'une API ne dispense d'aucun des trois.

## Définitions

### Schéma

Un schéma est un contrat qui décrit la forme d'une donnée : quels champs elle contient, de quels types, avec quelles bornes. Dans un agent, on en trouve à trois endroits : les arguments de chaque outil (schéma d'entrée), la réponse structurée qu'on demande au modèle (schéma de sortie) et ce que l'outil renvoie. Un schéma ne dit rien de la vérité d'une donnée : un montant de 150 000 AED peut être parfaitement valide et pourtant faux s'il a été mal lu dans le courriel du client.

### JSON Schema

JSON Schema est le langage standard pour écrire ces contrats ; sa version la plus récente est datée 2020-12. Un schéma est lui-même un objet JSON : `{"type": "integer", "minimum": 12}` décrit un entier supérieur ou égal à 12. C'est le format qu'attendent les API de modèles pour décrire un outil (champ `input_schema`) ou une sortie structurée. La donnée que l'on vérifie s'appelle l'**instance**. Les mots-clés utilisés dans ce parcours sont les suivants.

| Mot-clé | S'applique à | Ce qu'il impose | Exemple |
|---|---|---|---|
| `type` | toute valeur | le type JSON : `object`, `array`, `string`, `number`, `integer`, `boolean` ou `null` (ou une liste de types) | `{"type": "integer"}` |
| `enum` | toute valeur | la valeur appartient à une liste fermée | `{"enum": ["hypothecaire", "personnel"]}` |
| `properties` | objet | le schéma de chaque champ présent | `{"properties": {"duree_mois": {"type": "integer"}}}` |
| `required` | objet | les champs qui doivent être présents | `{"required": ["montant_aed"]}` |
| `additionalProperties` | objet | avec `false`, aucun champ hors de `properties` | un champ `commentaire` imprévu est refusé |
| `minimum`, `maximum` | nombre | bornes incluses | `{"minimum": 12, "maximum": 300}` |
| `exclusiveMinimum`, `exclusiveMaximum` | nombre | bornes exclues | `{"exclusiveMinimum": 0}` pour « strictement positif » |
| `minLength`, `maxLength` | chaîne | nombre de caractères | `{"minLength": 1}` |
| `pattern` | chaîne | une expression régulière qui doit trouver une correspondance | `{"pattern": "^784-[0-9]{4}-[0-9]{7}-[0-9]$"}` |
| `items` | tableau | le schéma de chaque élément | `{"items": {"type": "string"}}` |
| `minItems`, `maxItems` | tableau | nombre d'éléments | `{"maxItems": 5}` |

### Validation et chemin JSON

Valider, c'est vérifier qu'une instance respecte chaque mot-clé du schéma et produire la liste des écarts ; une liste vide signifie que l'instance est valide. Chaque erreur est localisée par un chemin JSON : `$` désigne la racine, `.champ` un champ d'objet et `[i]` l'élément d'indice i d'un tableau, comme dans `$.garanties[1]`. Cette notation reprend celle de JSONPath (RFC 9535). Elle sert deux lecteurs : le développeur qui lit les journaux, et le modèle qui, dans la boucle de réparation, doit corriger exactement le champ fautif.

### Sortie structurée

Une sortie structurée est une réponse du modèle qui est un objet JSON conforme à un schéma, au lieu d'un texte libre. Il y a deux niveaux. Au premier, on décrit le schéma dans le prompt et on valide après coup : cela marche avec tous les modèles, mais rien n'est garanti. Au second, l'API contraint la génération elle-même par une grammaire tirée du schéma (paramètre `output_config.format` chez Claude) : le texte rendu est toujours un JSON lisible qui respecte les mots-clés pris en charge. Même au second niveau, une réponse arrêtée par un refus (`stop_reason` égal à `"refusal"`) ou par la limite de longueur (`"max_tokens"`) peut ne pas respecter le schéma : on teste donc `stop_reason` avant de lire le contenu.

### Outil « strict »

Un outil déclaré avec `strict: true` reçoit la même garantie pour ses arguments : l'API contraint l'échantillonnage pour que `tool_use.input` respecte exactement le schéma d'entrée (types, champs obligatoires, énumérations, aucun champ non prévu) ; le schéma doit alors comporter `required` et `additionalProperties: false`. La garantie a des limites précises. Les bornes numériques (`minimum`, `maximum`, `multipleOf`) et les longueurs de chaîne (`minLength`, `maxLength`) ne sont pas prises en charge, et un schéma qui les contient est refusé avec une erreur 400 ; `pattern` est accepté pour des motifs simples, sans référence arrière, ni assertion avant ou arrière, ni limite de mot. Les assistants des SDK, comme `client.messages.parse()` en Python, retirent ces contraintes du schéma envoyé et les recopient dans la description du champ ; ceux qui valident la réponse les revérifient ensuite. La conséquence est simple : la validation locale reste obligatoire, même en mode strict, et c'est ce que fait la fonction `schema_pour_api_strict` du programme.

### Pydantic, Zod, Bean Validation

Ces bibliothèques décrivent le même contrat sous forme de classe typée : Pydantic en Python, Zod en TypeScript, Bean Validation (aujourd'hui Jakarta Validation) en Java. Elles valident une donnée contre la classe et renvoient des erreurs localisées ; Pydantic et Zod savent aussi produire le JSON Schema correspondant, à donner au modèle. Pour un développeur Spring, l'équivalence est directe : un `record` annoté `@Min`, `@Max`, `@Pattern` et reçu par `@Valid @RequestBody` joue le rôle du schéma et du validateur réunis.

| JSON Schema | Pydantic v2 | Zod | Bean Validation (Jakarta) |
|---|---|---|---|
| `"type": "integer", "minimum": 12, "maximum": 300` | `int = Field(ge=12, le=300)` | `z.number().int().min(12).max(300)` | `@Min(12) @Max(300) int` |
| `"exclusiveMinimum": 0` | `Field(gt=0)` | `.positive()` | `@Positive` |
| `"enum": ["hypothecaire", "personnel"]` | `Literal["hypothecaire", "personnel"]` | `z.enum(["hypothecaire", "personnel"])` | un `enum` Java |
| `"pattern": "^784-…$"` | `Field(pattern=r"^784-…$")` | `.regex(/^784-…$/)` | `@Pattern(regexp = "^784-…$")` |
| `"minLength": 1` | `Field(min_length=1)` | `.min(1)` | `@Size(min = 1)` |
| `"maxItems": 5` | `Field(max_length=5)` | `.max(5)` | `@Size(max = 5)` |
| `"required": [...]` | champ sans valeur par défaut | champ sans `.optional()` | `@NotNull` |
| `"additionalProperties": false` | `ConfigDict(extra="forbid")` | `.strict()` | `fail-on-unknown-properties=true` (Jackson) |

### Boucle de réparation

Quand la validation échoue, l'agent renvoie au modèle la liste des erreurs, avec leurs chemins, et lui redemande le JSON corrigé. On borne le nombre de relances R (ici R = 2, donc au plus trois appels) ; au-delà, on escalade vers un humain au lieu de deviner. La probabilité de réussir en au plus R + 1 essais et le nombre moyen d'essais sont démontrés à l'étape 11.

### Règle inter-champs

Une règle inter-champs lie plusieurs champs entre eux : la durée d'un prêt personnel ne dépasse pas 48 mois, la date du sinistre précède la date de déclaration, le TTC vaut le HT majoré de 5 %. JSON Schema sait exprimer une condition sur une valeur fixe (mots-clés `if` et `then`), mais pas une comparaison entre deux valeurs de l'instance ; de plus, la liste des mots-clés acceptés en mode strict ne comprend pas `if`. On écrit donc ces règles en code, juste après la validation du schéma : c'est l'objet de l'étape 9.

## Rôle dans un agent

Dans la boucle percevoir → décider → agir → observer de l'étape 1, le schéma intervient à deux charnières. Entre décider et agir : le modèle a proposé un appel d'outil avec des arguments ; avant d'exécuter quoi que ce soit, l'agent valide ces arguments contre le schéma d'entrée de l'outil, et une erreur repart vers le modèle au lieu de déclencher un effet de bord (le registre d'outils de l'étape 12 le fait systématiquement). Entre observer et répondre : quand l'agent doit rendre un objet exploitable par un autre programme, un dossier de crédit ou une facture, il valide sa sortie finale contre le schéma de sortie et lance la boucle de réparation si besoin. Le validateur est donc un **garde-fou d'entrée**, comme un contrôleur REST qui refuse une requête mal formée avant d'appeler le service métier ; dans une architecture hexagonale, il vit dans l'adaptateur, à la frontière du domaine, et le domaine ne reçoit que des objets déjà valides.

## Construire depuis une feuille blanche

Le programme ci-dessous tient en un seul fichier, sans aucune bibliothèque externe. Il contient le port LLM du parcours (recopié du code canonique), un validateur JSON Schema pour les quinze mots-clés du tableau, la préparation du schéma pour le mode strict, la boucle de réparation et le jumeau `dataclass` du schéma de demande de crédit.

### Déroulé, ligne par ligne

**Port LLM** (`Bloc`, `Reponse`, `texte`, `FakeLLM`). Ces quatre définitions sont recopiées telles quelles du code canonique ; elles reviennent à l'étape 13 dans la boucle d'agent. Ici, le faux modèle ne renvoie que du texte : chaque `Reponse("end_turn", [texte(...)])` contient le JSON que le « modèle » aurait écrit. Le compteur `FakeLLM.appels` permet de vérifier combien d'appels la réparation a coûté.

**`type_json(x)`** donne le nom JSON d'une valeur Python.

- `if isinstance(x, bool)` est placé **avant** `if isinstance(x, int)`. En Python, `bool` est une sous-classe de `int` : `isinstance(True, int)` vaut `True`, et `True + True` vaut 2. Si l'ordre était inversé, `type_json(True)` renverrait `"integer"`.
- La dernière ligne lève `ValueError` pour une valeur qu'aucun JSON ne peut produire, comme un tuple : `json.loads` ne renvoie que des `dict`, `list`, `str`, `int`, `float`, `bool` et `None`.

**`entier_json(x)`** renvoie l'entier que représente `x`, ou `None`. `entier_json(36)` vaut 36 ; `entier_json(36.0)` vaut aussi 36, parce que `(36.0).is_integer()` est vrai et que JSON Schema considère comme entier tout nombre dont la partie décimale est nulle ; `entier_json(36.5)`, `entier_json(True)` et `entier_json("36")` valent `None`.

**`correspond(x, nom)`** dit si `x` a le type JSON `nom`. Pour `"integer"`, elle délègue à `entier_json` ; pour `"number"`, elle accepte les entiers et les décimaux, parce que tout entier est un nombre ; pour les autres types, elle compare `type_json(x)` au nom attendu.

**`egal_json(a, b)`** compare deux valeurs comme JSON le fait. En Python, `False in [0, 1]` est vrai, parce que `False == 0`. La condition `isinstance(a, bool) == isinstance(b, bool)` exige que les deux valeurs soient booléennes ou qu'aucune ne le soit : `egal_json(False, 0)` vaut donc `False`, alors que `egal_json(1.0, 1)` reste vrai, comme en JSON.

**`validate(instance, schema, path="$")`**, bloc par bloc.

- `inconnus = set(schema) - MOTS_CLES - ANNOTATIONS` : un mot-clé que le validateur ne sait pas vérifier, comme `multipleOf`, lève `ValueError`. Un validateur qui l'ignorerait en silence donnerait une fausse assurance. Les annotations (`description`, `title`, `default`…) n'imposent rien et sont acceptées.
- Le bloc `type` accepte un nom ou une liste de noms (`["string", "null"]` pour un champ qui peut être nul). Si aucun ne correspond, la fonction renvoie tout de suite une seule erreur, parce que comparer `"36"` à un minimum n'aurait pas de sens : pour `"duree_mois": "36"`, l'erreur est `$.duree_mois : type attendu integer, reçu string`.
- Le bloc `enum` utilise `egal_json` : `False` n'est pas accepté dans `[0, 1]`.
- Le bloc des nombres teste d'abord `math.isfinite`. En Python, `json.loads('{"x": NaN}')` réussit, et `nan < 0` comme `nan > 300` valent `False` : sans ce test, NaN franchirait toutes les bornes. Viennent ensuite les quatre bornes ; `exclusiveMinimum: 0` refuse 0 avec le message `doit être > 0`.
- Le bloc des chaînes compte les caractères avec `len` et applique `pattern` avec `re.search`, comme le prévoit JSON Schema : le motif n'est pas ancré, il suffit qu'il trouve une correspondance quelque part. C'est pourquoi les motifs de ce parcours commencent par `^` et finissent par `$`.
- Le bloc des tableaux vérifie le nombre d'éléments, puis appelle `validate` sur chaque élément avec le chemin `f"{path}[{i}]"` : la chaîne vide en deuxième position de `garanties` donne `$.garanties[1] : longueur 0 < minLength 1`, parce que `enumerate` compte à partir de 0.
- Le bloc des objets vérifie d'abord les champs obligatoires, dans l'ordre de `required`, puis parcourt les champs de l'instance dans leur ordre : un champ connu est validé récursivement avec le chemin `f"{path}.{cle}"`, un champ inconnu est refusé si `additionalProperties` vaut `False`. Sur l'instance `mauvaise` du programme, on obtient cinq erreurs, dans cet ordre : `emirates_id` absent, `'auto'` hors de l'énumération, `6 < minimum 12`, la garantie vide, puis le champ `commentaire`.

**`schema_pour_api_strict(schema)`** prépare le schéma envoyé à l'API en mode strict. Les sept mots-clés de `NON_PRIS_EN_CHARGE_STRICT`, ainsi que `minItems` au-delà de 1, sont retirés et notés dans `retirees` ; `properties` et `items` sont traités récursivement ; le reste est recopié. Les contraintes retirées passent dans la description, pour que le modèle les lise quand même : `duree_mois` devient `{"type": "integer", "description": "Contraintes : minimum=12, maximum=300."}`. La fonction `mots_cles_utilises` parcourt le résultat pour vérifier qu'il ne reste aucun mot-clé refusé.

**`lire_et_valider(texte_llm, schema)`** enchaîne `json.loads` et `validate`. Une réponse enveloppée dans un bloc de code Markdown (trois accents graves, puis le mot json) n'est pas du JSON : `json.loads` lève `JSONDecodeError`, que la fonction transforme en une erreur à la racine, `$ : JSON illisible (Expecting value, position 0)`. Le premier caractère, un accent grave, ne commence aucune valeur JSON.

**`extraire_avec_reparation(llm, schema, demande, relances_max=2)`**.

- `system` contient le schéma sérialisé : c'est le premier niveau, « le schéma est dans le prompt ». Avec l'API, on passerait en plus `schema_pour_api_strict(schema)` dans `output_config.format` (extrait plus bas).
- `for essai in range(1, relances_max + 2)` : avec `relances_max = 2`, `essai` prend les valeurs 1, 2 et 3, soit un premier essai et deux relances.
- `if reponse.stop_reason in ("refusal", "max_tokens")` vient avant toute lecture du contenu : un refus ou une réponse tronquée ne se « répare » pas.
- Si la validation échoue, on ajoute à `messages` la réponse du modèle telle quelle (`reponse.content`), puis un message `user` qui liste les erreurs. Au deuxième appel, le modèle voit donc sa propre réponse et les chemins à corriger.
- Après le dernier essai raté, la fonction renvoie le statut `"echec"` : c'est à l'appelant de passer la main à un humain.

**`DemandeCredit`** est le jumeau typé du schéma. Une `dataclass` ne vérifie pas les annotations de type à l'exécution : sans `__post_init__`, `DemandeCredit(duree_mois="36", ...)` serait accepté. Cette méthode, appelée juste après le constructeur, réécrit les contraintes en Python, comme le constructeur compact d'un `record` Java. Elle convertit `36.0` en `36` avec `setattr`, comme le fait Pydantic dans son mode par défaut. Un champ inconnu ou manquant n'a pas besoin de test : `DemandeCredit(**donnees)` lève alors `TypeError`, ce qui joue le rôle de `additionalProperties: false` et de `required`.

**`main()`**, bloc par bloc.

1. L'instance `base` passe. L'instance `mauvaise` accumule cinq défauts ; l'`assert` vérifie la liste exacte des messages, dans l'ordre.
2. `isinstance(True, int)` est vrai et `True + True == 2` : un test naïf accepterait `true` comme « une personne à charge ». `validate` le refuse ; `False` est refusé dans `[0, 1]`, alors que `False in [0, 1]` est vrai.
3. `36.0` est un entier JSON, `36.5` non. `json.loads` lit `NaN` sans erreur et `nan < 0` vaut `False` ; `validate` le refuse. L'Emirates ID sans tirets est refusé ; un motif sans `^` trouve `784-1990` dans une chaîne qui commence par `x`. Deux lignes montrent deux pièges du module `re` : `$` accepte un saut de ligne final, et `\d` accepte le chiffre arabe-indien ٧, contrairement à `[0-9]`. Enfin, `multipleOf` est refusé au lieu d'être ignoré.
4. Le schéma pour l'API ne contient plus aucun mot-clé refusé. Une durée de 6 mois passe ce schéma allégé mais pas le schéma complet : c'est la preuve, sur un exemple, que la validation locale reste nécessaire.
5. Premier scénario : trois erreurs au premier essai (`'perso'`, la durée `"36"` écrite en texte, le champ `commentaire`), puis un JSON valide. Deux appels au modèle.
6. Second scénario : un JSON enveloppé dans un bloc de code, puis deux fois un montant nul. La clôture de ce bloc est fabriquée en répétant trois fois un accent grave (variable `fence`) : écrits en toutes lettres dans le programme, les trois accents graves pourraient refermer, pour certains outils, le bloc Markdown qui contient ce code. Trois appels, statut `echec` : le dossier part en revue humaine. Un refus, lui, arrête la boucle dès le premier appel, sans erreur de validation.
7. Dix instances sont soumises à `validate` et au jumeau : les deux rendent le même verdict sur les dix, dont deux acceptées (`base` et la durée `36.0`).

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`texte(t)`** — C'est la même fonction que dans le programme de l'étape 1 : le copiste reçoit une chaîne et la range dans un `Bloc` de type `"text"`, sans rien vérifier, puis renvoie ce bloc. Ici, le faux modèle ne demande jamais d'outil ; chaque réplique scriptée est donc un seul bloc de texte qui contient le JSON que le « modèle » aurait écrit, du premier essai fautif avec `"perso"` et la durée `"36"` jusqu'au JSON enveloppé dans un bloc de code Markdown du second scénario.

**`FakeLLM.__init__(script)`** — Le constructeur est identique à celui de l'étape 1 : comme un souffleur qui reçoit le cahier des répliques avant la séance, il garde une copie de la liste des réponses prévues et met le compteur `appels` à zéro, sans rien renvoyer. Ce compteur prend ici un rôle central, puisque `main` s'en sert pour vérifier ce qu'a coûté la réparation : 2 appels quand une relance suffit, 3 quand la boucle épuise ses deux relances, et 1 seul quand le modèle refuse d'emblée.

**`FakeLLM.create(system, messages, tools)`** — Même méthode que dans le programme de l'étape 1 : elle reçoit en arguments nommés le prompt système, l'historique et la liste des outils, n'en lit aucun, renvoie la réponse suivante du script et incrémente son compteur, ou lève `RuntimeError` si le script est épuisé. Dans ce fichier, c'est `extraire_avec_reparation` qui l'appelle, avec un prompt système qui contient le schéma sérialisé et une liste d'outils vide ; un vrai modèle y lirait les erreurs de validation renvoyées à chaque relance.

**`type_json(x)`** — Cette fonction est l'officier d'état civil qui inscrit chaque valeur Python sous son nom JSON : elle reçoit une valeur et renvoie `"null"` pour `None`, `"boolean"` pour un booléen, `"integer"` pour un entier, `"number"` pour un flottant, puis `"string"`, `"array"` ou `"object"` pour une chaîne, une liste ou un dictionnaire. Le test des booléens passe avant celui des entiers, parce qu'en Python `True` est aussi un `int`, sans quoi `true` serait inscrit comme un entier. Toute autre valeur, un tuple par exemple, lève `ValueError` avec le message « valeur sans équivalent JSON ».

**`validate(instance, schema, path)`** — C'est l'inspecteur qui parcourt l'instance et le schéma côte à côte, nœud par nœud, en notant l'adresse exacte de chaque défaut : il reçoit une valeur, un schéma et un chemin, `"$"` par défaut, lève `ValueError` sur un mot-clé qu'il ne sait pas vérifier, comme `multipleOf`, puis renvoie aussitôt une seule erreur si le type ne correspond pas. Sinon il contrôle l'énumération, la finitude et les bornes d'un nombre, la longueur et le motif d'une chaîne, la taille d'un tableau et chacun de ses éléments, les champs obligatoires et les champs non prévus d'un objet, en se rappelant lui-même avec les chemins `[i]` et `.clé`. Il renvoie la liste des erreurs, vide si l'instance est valide : cinq erreurs, dans l'ordre, pour l'instance `mauvaise`, de `emirates_id` absent au champ `commentaire`.

**`mots_cles_utilises(schema)`** — Celle-ci est le géomètre qui fait l'inventaire de tous les mots-clés d'un schéma, à tous les étages : elle reçoit un schéma, part de l'ensemble de ses clés au premier niveau, puis y ajoute récursivement les mots-clés de chaque sous-schéma de `properties` et, s'il existe, ceux du sous-schéma `items`. Elle renvoie cet ensemble sans lever d'exception. Dans `main`, elle sert de contre-vérification au schéma préparé par `schema_pour_api_strict` : l'intersection de son résultat avec les sept mots-clés de `NON_PRIS_EN_CHARGE_STRICT` doit être vide, sans quoi l'API refuserait le schéma.

**`extraire_avec_reparation(llm, schema, demande, relances_max)`** — C'est le chef d'atelier qui renvoie la pièce au tourneur tant qu'elle ne passe pas le calibre : il reçoit un modèle, un schéma, la demande de l'usager et un nombre de relances, 2 par défaut, place le schéma sérialisé dans le prompt système et fait au plus relances_max + 1 essais. À chaque essai, il appelle le modèle, s'arrête aussitôt avec le statut `"refusal"` ou `"max_tokens"` si la réponse est refusée ou tronquée, recolle le texte, le fait lire et valider, et renvoie `"valide"` avec les données s'il n'y a aucune erreur ; sinon il ajoute la réponse fautive et la liste des erreurs à l'historique avant de relancer. Après le dernier échec, il renvoie le statut `"echec"`, avec le nombre d'essais et la liste des erreurs de chaque essai : 2 essais pour le premier scénario, 3 et un échec pour le second.

**`DemandeCredit.__post_init__()`** — Cette méthode, que Python appelle juste après le constructeur de la `dataclass`, est le contrôleur des douanes qui refuse l'entrée à tout objet mal formé : elle vérifie que le type de prêt vaut « hypothecaire » ou « personnel », que la durée et le nombre de personnes à charge sont des entiers au sens JSON, qu'elle réécrit au passage avec `setattr` pour que 36.0 devienne 36, que la durée tient entre 12 et 300 mois, que les deux montants sont des nombres finis strictement positifs, que l'Emirates ID respecte le motif `784-AAAA-NNNNNNN-C` et que les garanties sont au plus cinq chaînes non vides. Elle ne renvoie rien et lève `ValueError` au premier défaut, ce qui donne au jumeau typé les mêmes règles que le schéma.

**`accepte_par_dataclass(donnees)`** — Celle-ci est l'arbitre qui traduit le verdict du jumeau typé en simple oui ou non : elle reçoit un dictionnaire, tente de construire `DemandeCredit(**donnees)` et renvoie `True` si l'objet naît sans encombre, `False` si la construction lève `ValueError`, venue de `__post_init__`, ou `TypeError`, qui signale un champ inconnu ou un champ obligatoire manquant. Elle ne laisse sortir aucune exception. `main` la compare à `validate` sur dix instances : les deux acceptent les deux mêmes, `base` et la durée 36.0, et refusent les huit autres, soit 10 accords sur 10.

**`main()`** — C'est le chef de laboratoire qui fait passer au validateur sept épreuves successives : il vérifie que l'instance `base` passe et que l'instance `mauvaise` produit les cinq erreurs attendues dans l'ordre, démonte le piège du booléen qui se fait passer pour un entier, puis contrôle l'entier 36.0, le `NaN` que `json.loads` accepte, les motifs ancrés ou non et le refus de `multipleOf`. Il prépare ensuite le schéma pour l'API en mode strict et montre qu'une durée de 6 mois le franchit alors que le schéma complet la refuse, fait tourner deux scénarios de réparation, une relance réussie en 2 appels puis un échec en 3 appels, ainsi qu'un refus immédiat, et termine par l'accord 10 sur 10 entre `validate` et le jumeau `dataclass`.

```python
"""Étape 8 — un validateur JSON Schema écrit à la main, la boucle de réparation et le jumeau dataclass."""
import json
import math
import re
import sys
from dataclasses import dataclass, field

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- port LLM (code canonique, recopié tel quel)
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


# ---------------------------------------------------------------- validateur JSON Schema minimal
MOTS_CLES = {"type", "enum", "properties", "required", "additionalProperties", "items", "minItems", "maxItems",
             "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "minLength", "maxLength", "pattern"}
ANNOTATIONS = {"title", "description", "default", "examples", "$schema"}


def type_json(x) -> str:
    """Nom JSON d'une valeur Python. bool est testé AVANT int, parce que isinstance(True, int) est vrai."""
    if x is None:
        return "null"
    if isinstance(x, bool):
        return "boolean"
    if isinstance(x, int):
        return "integer"
    if isinstance(x, float):
        return "number"
    if isinstance(x, str):
        return "string"
    if isinstance(x, list):
        return "array"
    if isinstance(x, dict):
        return "object"
    raise ValueError(f"valeur sans équivalent JSON : {type(x).__name__}")


def entier_json(x) -> int | None:
    """L'entier que représente x (36 ou 36.0), ou None si x n'est pas un entier JSON (True, 36.5, "36")."""
    if isinstance(x, bool):
        return None
    if isinstance(x, int):
        return x
    if isinstance(x, float) and x.is_integer():
        return int(x)
    return None


def correspond(x, nom: str) -> bool:
    if nom == "integer":
        return entier_json(x) is not None
    if nom == "number":
        return type_json(x) in ("integer", "number")
    return type_json(x) == nom


def egal_json(a, b) -> bool:
    """Égalité au sens JSON : true n'est pas 1, alors qu'en Python True == 1 est vrai."""
    return isinstance(a, bool) == isinstance(b, bool) and a == b


def validate(instance, schema: dict, path: str = "$") -> list[str]:
    """Liste des erreurs, chacune préfixée par son chemin JSON ($.garanties[0]) ; liste vide = instance valide."""
    inconnus = set(schema) - MOTS_CLES - ANNOTATIONS
    if inconnus:
        raise ValueError(f"mots-clés non pris en charge : {sorted(inconnus)}")   # refuser plutôt qu'ignorer
    if "type" in schema:
        attendus = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(correspond(instance, t) for t in attendus):
            noms = " ou ".join(attendus)
            return [f"{path} : type attendu {noms}, reçu {type_json(instance)}"]
    erreurs = []
    if "enum" in schema and not any(egal_json(instance, v) for v in schema["enum"]):
        erreurs.append(f"{path} : {instance!r} hors de l'énumération {schema['enum']}")
    t = type_json(instance)
    if t in ("integer", "number"):
        if not math.isfinite(instance):
            return erreurs + [f"{path} : nombre non fini ({instance}), interdit en JSON"]
        if "minimum" in schema and instance < schema["minimum"]:
            erreurs.append(f"{path} : {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            erreurs.append(f"{path} : {instance} > maximum {schema['maximum']}")
        if "exclusiveMinimum" in schema and instance <= schema["exclusiveMinimum"]:
            erreurs.append(f"{path} : {instance} doit être > {schema['exclusiveMinimum']}")
        if "exclusiveMaximum" in schema and instance >= schema["exclusiveMaximum"]:
            erreurs.append(f"{path} : {instance} doit être < {schema['exclusiveMaximum']}")
    elif t == "string":
        if "minLength" in schema and len(instance) < schema["minLength"]:
            erreurs.append(f"{path} : longueur {len(instance)} < minLength {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            erreurs.append(f"{path} : longueur {len(instance)} > maxLength {schema['maxLength']}")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            erreurs.append(f"{path} : {instance!r} ne respecte pas le motif {schema['pattern']}")
    elif t == "array":
        if "minItems" in schema and len(instance) < schema["minItems"]:
            erreurs.append(f"{path} : {len(instance)} élément(s) < minItems {schema['minItems']}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            erreurs.append(f"{path} : {len(instance)} élément(s) > maxItems {schema['maxItems']}")
        if "items" in schema:
            for i, element in enumerate(instance):
                erreurs += validate(element, schema["items"], f"{path}[{i}]")
    elif t == "object":
        proprietes = schema.get("properties", {})
        supplementaires = schema.get("additionalProperties", True)
        if not isinstance(supplementaires, bool):
            raise ValueError("additionalProperties : seuls true et false sont pris en charge ici")
        for cle in schema.get("required", []):
            if cle not in instance:
                erreurs.append(f"{path} : champ obligatoire absent « {cle} »")
        for cle, valeur in instance.items():
            if cle in proprietes:
                erreurs += validate(valeur, proprietes[cle], f"{path}.{cle}")
            elif not supplementaires:
                erreurs.append(f"{path} : champ non prévu « {cle} »")
    return erreurs


# ---------------------------------------------------------------- schéma envoyé à l'API en mode strict
NON_PRIS_EN_CHARGE_STRICT = ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "minLength", "maxLength",
                             "maxItems")


def schema_pour_api_strict(schema: dict) -> dict:
    """Copie sans les contraintes que le décodage contraint refuse (erreur 400) ; elles passent dans la description."""
    copie, retirees = {}, []
    for cle, valeur in schema.items():
        if cle in NON_PRIS_EN_CHARGE_STRICT or (cle == "minItems" and valeur > 1):
            retirees.append(f"{cle}={valeur}")
        elif cle == "properties":
            copie[cle] = {nom: schema_pour_api_strict(sous) for nom, sous in valeur.items()}
        elif cle == "items":
            copie[cle] = schema_pour_api_strict(valeur)
        else:
            copie[cle] = valeur
    if retirees:
        copie["description"] = (schema.get("description", "") + " Contraintes : " + ", ".join(retirees) + ".").strip()
    return copie


def mots_cles_utilises(schema: dict) -> set[str]:
    trouves = set(schema)
    for sous in schema.get("properties", {}).values():
        trouves |= mots_cles_utilises(sous)
    if "items" in schema:
        trouves |= mots_cles_utilises(schema["items"])
    return trouves


# ---------------------------------------------------------------- boucle de réparation
def lire_et_valider(texte_llm: str, schema: dict) -> tuple[dict | None, list[str]]:
    try:
        donnees = json.loads(texte_llm)
    except json.JSONDecodeError as e:
        return None, [f"$ : JSON illisible ({e.msg}, position {e.pos})"]
    erreurs = validate(donnees, schema)
    return (None if erreurs else donnees), erreurs


def extraire_avec_reparation(llm, schema: dict, demande: str, relances_max: int = 2) -> dict:
    """json.loads → validate → erreurs renvoyées au modèle → nouvel essai ; au plus relances_max relances."""
    system = "Réponds uniquement par un objet JSON conforme à ce schéma : " + json.dumps(schema, ensure_ascii=False)
    messages = [{"role": "user", "content": demande}]
    erreurs_par_essai = []
    for essai in range(1, relances_max + 2):
        reponse = llm.create(system=system, messages=messages, tools=[])
        if reponse.stop_reason in ("refusal", "max_tokens"):           # se traite AVANT de lire le contenu
            return {"statut": reponse.stop_reason, "donnees": None, "essais": essai, "erreurs": erreurs_par_essai}
        brut = "".join(b.text for b in reponse.content if b.type == "text")
        donnees, erreurs = lire_et_valider(brut, schema)
        erreurs_par_essai.append(erreurs)
        if not erreurs:
            return {"statut": "valide", "donnees": donnees, "essais": essai, "erreurs": erreurs_par_essai}
        messages.append({"role": "assistant", "content": reponse.content})
        messages.append({"role": "user", "content": "Ta réponse ne respecte pas le schéma :\n" + "\n".join(erreurs)
                         + "\nRenvoie uniquement l'objet JSON corrigé."})
    return {"statut": "echec", "donnees": None, "essais": relances_max + 1, "erreurs": erreurs_par_essai}


# ---------------------------------------------------------------- le contrat de l'étape 8
MOTIF_EID = "^784-[0-9]{4}-[0-9]{7}-[0-9]$"
SCHEMA_DEMANDE_CREDIT = {
    "type": "object",
    "properties": {
        "type_pret": {"type": "string", "enum": ["hypothecaire", "personnel"]},
        "montant_aed": {"type": "number", "exclusiveMinimum": 0},
        "duree_mois": {"type": "integer", "minimum": 12, "maximum": 300},
        "revenu_mensuel_aed": {"type": "number", "exclusiveMinimum": 0},
        "emirates_id": {"type": "string", "pattern": MOTIF_EID},
        "garanties": {"type": "array", "items": {"type": "string", "minLength": 1}, "maxItems": 5},
        "personnes_a_charge": {"type": "integer", "minimum": 0},
    },
    "required": ["type_pret", "montant_aed", "duree_mois", "revenu_mensuel_aed", "emirates_id"],
    "additionalProperties": False,
}


@dataclass
class DemandeCredit:
    """Jumeau typé du schéma : les mêmes contraintes écrites en Python (comme un record Java + Bean Validation)."""
    type_pret: str
    montant_aed: float
    duree_mois: int
    revenu_mensuel_aed: float
    emirates_id: str
    garanties: list[str] = field(default_factory=list)
    personnes_a_charge: int = 0

    def __post_init__(self) -> None:
        if self.type_pret not in ("hypothecaire", "personnel"):
            raise ValueError(f"type_pret inconnu : {self.type_pret!r}")
        for nom in ("duree_mois", "personnes_a_charge"):
            n = entier_json(getattr(self, nom))
            if n is None:
                raise ValueError(f"{nom} doit être un entier")
            setattr(self, nom, n)                                    # 36.0 devient 36
        if not 12 <= self.duree_mois <= 300 or self.personnes_a_charge < 0:
            raise ValueError("duree_mois hors de [12 ; 300] ou personnes_a_charge négatif")
        for nom in ("montant_aed", "revenu_mensuel_aed"):
            v = getattr(self, nom)
            if type_json(v) not in ("integer", "number") or not math.isfinite(v) or v <= 0:
                raise ValueError(f"{nom} doit être un nombre fini > 0")
        if not isinstance(self.emirates_id, str) or re.search(MOTIF_EID, self.emirates_id) is None:
            raise ValueError("emirates_id hors format 784-AAAA-NNNNNNN-C")
        if len(self.garanties) > 5 or any(not isinstance(g, str) or g == "" for g in self.garanties):
            raise ValueError("garanties : au plus 5 chaînes non vides")


def accepte_par_dataclass(donnees: dict) -> bool:
    try:
        DemandeCredit(**donnees)       # champ inconnu ou manquant : TypeError, comme additionalProperties/required
        return True
    except (ValueError, TypeError):
        return False


def main() -> None:
    base = {"type_pret": "personnel", "montant_aed": 150000, "duree_mois": 36, "revenu_mensuel_aed": 25000,
            "emirates_id": "784-1990-1234567-1", "garanties": ["domiciliation du salaire"], "personnes_a_charge": 2}

    print("1. Le validateur et ses chemins d'erreur")
    assert validate(base, SCHEMA_DEMANDE_CREDIT) == []
    mauvaise = dict(base, type_pret="auto", duree_mois=6, garanties=["caution", ""], commentaire="urgent")
    del mauvaise["emirates_id"]
    erreurs = validate(mauvaise, SCHEMA_DEMANDE_CREDIT)
    for e in erreurs:
        print("  " + e)
    assert erreurs == [
        "$ : champ obligatoire absent « emirates_id »",
        "$.type_pret : 'auto' hors de l'énumération ['hypothecaire', 'personnel']",
        "$.duree_mois : 6 < minimum 12",
        "$.garanties[1] : longueur 0 < minLength 1",
        "$ : champ non prévu « commentaire »",
    ]

    print("2. Le piège bool : en Python, True est un int")
    assert isinstance(True, int) and True + True == 2 and True == 1
    naif = isinstance(True, int)                        # un test naïf accepterait True comme 1 personne à charge
    erreurs_bool = validate(dict(base, personnes_a_charge=True), SCHEMA_DEMANDE_CREDIT)
    print(f"  test naïf isinstance(True, int) = {naif} ; validate : {erreurs_bool}")
    assert naif and erreurs_bool == ["$.personnes_a_charge : type attendu integer, reçu boolean"]
    assert validate(False, {"enum": [0, 1]}) == ["$ : False hors de l'énumération [0, 1]"]   # False in [0, 1] est vrai
    assert False in [0, 1]

    print("3. Entier JSON, nombre non fini, motif")
    assert validate(36.0, {"type": "integer"}) == []                         # partie décimale nulle : entier
    assert validate(36.5, {"type": "integer"}) == ["$ : type attendu integer, reçu number"]
    nan = json.loads('{"montant_aed": NaN}')["montant_aed"]                    # json.loads accepte NaN !
    erreurs_nan = validate(nan, {"type": "number", "minimum": 0})
    print(f"  json.loads lit NaN : {nan} ; nan < 0 vaut {nan < 0} ; validate : {erreurs_nan}")
    assert not nan < 0 and erreurs_nan == ["$ : nombre non fini (nan), interdit en JSON"]
    assert validate("784199012345671", {"type": "string", "pattern": MOTIF_EID}) != []
    assert validate("x784-1990-1234567-1", {"type": "string", "pattern": "784-[0-9]{4}"}) == []   # motif non ancré
    assert re.search(MOTIF_EID, "784-1990-1234567-1\n") is not None        # piège : en Python, $ accepte un \n final
    assert re.search(r"^\d$", "٧") is not None and re.search(r"^[0-9]$", "٧") is None   # chiffre arabe-indien 7
    try:
        validate(1, {"type": "integer", "multipleOf": 5})
    except ValueError as e:
        print(f"  mot-clé inconnu refusé : {e}")
    else:
        raise AssertionError("un mot-clé non vérifié aurait dû être refusé")

    print("4. Schéma envoyé à l'API en mode strict")
    api = schema_pour_api_strict(SCHEMA_DEMANDE_CREDIT)
    print(f"  duree_mois envoyé : {api['properties']['duree_mois']}")
    assert not mots_cles_utilises(api) & set(NON_PRIS_EN_CHARGE_STRICT)
    assert api["properties"]["duree_mois"] == {"type": "integer", "description": "Contraintes : minimum=12, maximum=300."}
    six_mois = dict(base, duree_mois=6)
    assert validate(six_mois, api) == [] and validate(six_mois, SCHEMA_DEMANDE_CREDIT) == ["$.duree_mois : 6 < minimum 12"]

    print("5. Boucle de réparation : une relance suffit")
    essai1 = ('{"type_pret": "perso", "montant_aed": 150000, "duree_mois": "36", "revenu_mensuel_aed": 25000, '
              '"emirates_id": "784-1990-1234567-1", "commentaire": "client fidèle"}')
    llm = FakeLLM([Reponse("end_turn", [texte(essai1)]), Reponse("end_turn", [texte(json.dumps(base))])])
    r = extraire_avec_reparation(llm, SCHEMA_DEMANDE_CREDIT, "Prêt personnel de 150 000 AED sur 36 mois ...")
    for e in r["erreurs"][0]:
        print("  essai 1 : " + e)
    print(f"  statut = {r['statut']}, essais = {r['essais']}, appels au LLM = {llm.appels}")
    assert r["statut"] == "valide" and r["essais"] == 2 and llm.appels == 2 and r["donnees"] == base
    assert len(r["erreurs"][0]) == 3 and r["erreurs"][1] == []

    print("6. Boucle de réparation : échec après 2 relances, puis refus")
    fence = "`" * 3                     # trois accents graves, écrits sans clore le bloc Markdown qui contient ce code
    clos = fence + "json\n" + json.dumps(base) + "\n" + fence
    faux = json.dumps(dict(base, montant_aed=0))
    llm = FakeLLM([Reponse("end_turn", [texte(clos)])] + [Reponse("end_turn", [texte(faux)])] * 2)
    r = extraire_avec_reparation(llm, SCHEMA_DEMANDE_CREDIT, "...")
    print(f"  essai 1 : {r['erreurs'][0][0]}")
    print(f"  essais 2 et 3 : {r['erreurs'][1][0]}")
    print(f"  statut = {r['statut']}, essais = {r['essais']}, appels au LLM = {llm.appels} → revue humaine")
    assert r["statut"] == "echec" and r["essais"] == 3 and llm.appels == 3
    r = extraire_avec_reparation(FakeLLM([Reponse("refusal", [])]), SCHEMA_DEMANDE_CREDIT, "...")
    assert r["statut"] == "refusal" and r["essais"] == 1 and r["erreurs"] == []

    print("7. Le jumeau dataclass rend le même verdict que validate")
    cas = [base, dict(base, duree_mois=True), dict(base, duree_mois=36.0), dict(base, duree_mois=6),
           dict(base, montant_aed=0), dict(base, type_pret="auto"), dict(base, emirates_id="784199012345671"),
           dict(base, commentaire="urgent"), {k: v for k, v in base.items() if k != "emirates_id"},
           dict(base, garanties=[""])]
    verdicts = [(validate(d, SCHEMA_DEMANDE_CREDIT) == [], accepte_par_dataclass(d)) for d in cas]
    print(f"  {sum(a for a, _ in verdicts)} acceptées sur {len(cas)} ; accords : {sum(a == b for a, b in verdicts)}/{len(cas)}")
    assert all(a == b for a, b in verdicts) and [a for a, _ in verdicts] == [True, False, True] + [False] * 7
    assert DemandeCredit(**dict(base, duree_mois=36.0)).duree_mois == 36

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Le validateur et ses chemins d'erreur
  $ : champ obligatoire absent « emirates_id »
  $.type_pret : 'auto' hors de l'énumération ['hypothecaire', 'personnel']
  $.duree_mois : 6 < minimum 12
  $.garanties[1] : longueur 0 < minLength 1
  $ : champ non prévu « commentaire »
2. Le piège bool : en Python, True est un int
  test naïf isinstance(True, int) = True ; validate : ['$.personnes_a_charge : type attendu integer, reçu boolean']
…
4. Schéma envoyé à l'API en mode strict
  duree_mois envoyé : {'type': 'integer', 'description': 'Contraintes : minimum=12, maximum=300.'}
…
  statut = valide, essais = 2, appels au LLM = 2
6. Boucle de réparation : échec après 2 relances, puis refus
  essai 1 : $ : JSON illisible (Expecting value, position 0)
  essais 2 et 3 : $.montant_aed : 0 doit être > 0
  statut = echec, essais = 3, appels au LLM = 3 → revue humaine
7. Le jumeau dataclass rend le même verdict que validate
  2 acceptées sur 10 ; accords : 10/10
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un schéma n'est pas une documentation, c'est un test exécutable. Le même contrat s'écrit en JSON Schema pour le modèle, en `dataclass` pour le code, et les deux rendent le même verdict.

### Le même contrat dans d'autres langages (extraits non exécutés)

Pydantic produit le JSON Schema à partir de la classe et valide la réponse du modèle. Dans son mode par défaut, il convertit `"36"` en `36` ; `ConfigDict(strict=True)` désactive ces conversions implicites.

```python
# [extrait] — équivalent Pydantic v2, non exécuté (pip install pydantic)
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class DemandeCredit(BaseModel):
    model_config = ConfigDict(extra="forbid")                 # additionalProperties: false
    type_pret: Literal["hypothecaire", "personnel"]
    montant_aed: float = Field(gt=0)                          # exclusiveMinimum: 0
    duree_mois: int = Field(ge=12, le=300)
    revenu_mensuel_aed: float = Field(gt=0)
    emirates_id: str = Field(pattern=r"^784-[0-9]{4}-[0-9]{7}-[0-9]$")
    garanties: list[Annotated[str, Field(min_length=1)]] = Field(default_factory=list, max_length=5)
    personnes_a_charge: int = Field(default=0, ge=0)


schema = DemandeCredit.model_json_schema()                    # le JSON Schema à donner au modèle
demande = DemandeCredit.model_validate_json(texte_du_modele)  # lève ValidationError, erreurs localisées
```

En TypeScript, `typeof true` vaut `"boolean"` : le piège `bool`/`int` est propre à Python, et `z.number()` refuse un booléen sans précaution particulière.

```typescript
// [extrait] — équivalent Zod, non exécuté
import { z } from "zod";

const DemandeCredit = z.object({
  type_pret: z.enum(["hypothecaire", "personnel"]),
  montant_aed: z.number().positive(),                  // exclusiveMinimum: 0
  duree_mois: z.number().int().min(12).max(300),
  revenu_mensuel_aed: z.number().positive(),
  emirates_id: z.string().regex(/^784-[0-9]{4}-[0-9]{7}-[0-9]$/),
  garanties: z.array(z.string().min(1)).max(5).default([]),
  personnes_a_charge: z.number().int().min(0).default(0),
}).strict();                                           // champ inconnu refusé (Zod 4 propose aussi z.strictObject)

const resultat = DemandeCredit.safeParse(JSON.parse(texteDuModele));   // { success, data } ou { success, error }
```

En Java, le même contrat est un `record` annoté, validé par Spring quand le paramètre porte `@Valid`. Attention : Spring Boot configure Jackson pour **ignorer** les champs inconnus ; l'équivalent de `additionalProperties: false` demande la propriété `spring.jackson.deserialization.fail-on-unknown-properties=true` (vérifier le défaut de votre version).

```java
// Équivalent Java : record + Bean Validation (Jakarta), noms JSON en snake_case via la stratégie de nommage de Jackson
public record DemandeCredit(
        @NotNull TypePret typePret,                                   // enum Java { hypothecaire, personnel }
        @NotNull @Positive BigDecimal montantAed,
        @Min(12) @Max(300) int dureeMois,
        @NotNull @Positive BigDecimal revenuMensuelAed,
        @NotNull @Pattern(regexp = "^784-[0-9]{4}-[0-9]{7}-[0-9]$") String emiratesId,
        @Size(max = 5) List<@NotBlank String> garanties,
        @PositiveOrZero int personnesACharge) {
}

// @PostMapping("/demandes")
// ResponseEntity<Void> creer(@Valid @RequestBody DemandeCredit demande) { ... }
```

Avec l'API Claude, la sortie structurée se demande par `output_config.format`. On envoie le schéma allégé et on revalide avec le schéma complet. L'adaptateur complet (repli en cas de refus, effort) est présenté à l'étape 13.

```python
# [extrait] — sortie structurée avec l'API Claude, non exécuté (pip install anthropic + clé API ou `ant auth login`)
import json

import anthropic

client = anthropic.Anthropic()
reponse = client.beta.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,
    messages=[{"role": "user", "content": courriel_du_client}],
    output_config={"effort": "medium",
                   "format": {"type": "json_schema", "schema": schema_pour_api_strict(SCHEMA_DEMANDE_CREDIT)}},
    betas=["server-side-fallback-2026-07-01"],
    fallbacks="default",
)
if reponse.stop_reason in ("refusal", "max_tokens"):          # la sortie peut alors ne pas respecter le schéma
    raise RuntimeError(f"réponse inexploitable : {reponse.stop_reason}")
donnees = json.loads(next(b.text for b in reponse.content if b.type == "text"))
erreurs = validate(donnees, SCHEMA_DEMANDE_CREDIT)            # les bornes retirées sont revérifiées ici
```

## Démonstration

On démontre trois propriétés du validateur, puis on montre sur un contre-exemple chiffré pourquoi le test du type entier doit écarter les booléens. La probabilité de succès de la boucle de réparation est démontrée à l'étape 11 ; on en rappelle seulement le résultat.

### 1. La liste est vide si et seulement si l'instance est valide

Disons qu'une instance x est **valide** pour un schéma S quand elle satisfait chacun des mots-clés de S, y compris ceux des sous-schémas, pour chaque champ présent et pour chaque élément. On note E(x, S) la liste renvoyée par `validate(x, S)`, et h la profondeur de S : le nombre maximal de niveaux `properties` ou `items` imbriqués. On raisonne par récurrence sur h.

- Cas h = 0 : S n'a pas de sous-schéma. Chaque mot-clé présent est traduit par un test explicite, et une erreur est ajoutée si et seulement si ce test échoue ; quand le type ne correspond pas, la fonction renvoie une erreur et l'instance est bien invalide. La liste est donc vide si et seulement si tous les tests passent, c'est-à-dire si x est valide.
- Hérédité : supposons la propriété vraie pour toute profondeur inférieure à h, et prenons S de profondeur h. La liste E(x, S) est la concaténation des erreurs locales (type, bornes, champs obligatoires, champs non prévus) et des listes

$$
E(x_c, S_c)
$$

des enfants, où chaque sous-schéma

$$
S_c
$$

est de profondeur au plus h − 1. Une concaténation de listes est vide si et seulement si chaque liste l'est. Par hypothèse de récurrence,

$$
E(x_c, S_c)
$$

est vide si et seulement si l'enfant

$$
x_c
$$

est valide pour

$$
S_c .
$$

Donc E(x, S) est vide si et seulement si les mots-clés locaux sont satisfaits et tous les enfants sont valides : c'est exactement la définition.

La fonction termine, parce que chaque appel récursif descend d'un niveau dans le schéma, qui est un arbre fini : il y a au plus h appels imbriqués. La propriété ne vaut que pour les quinze mots-clés traités ; c'est pourquoi un mot-clé inconnu lève une exception au lieu d'être ignoré.

### 2. Le chemin désigne l'élément fautif

Le chemin passé à un enfant est celui du parent suivi de `.clé` ou de `[i]`, et la racine reçoit `$`. Par récurrence sur la profondeur, le chemin d'une erreur est donc la suite exacte des clés et des indices qui mènent de la racine à l'élément fautif : `$.garanties[1]` désigne le deuxième élément du tableau `garanties`, parce que `enumerate` compte à partir de 0.

### 3. Le coût est linéaire en la taille de l'instance

Chaque appel traite un couple formé d'un nœud de l'instance et d'un nœud du schéma, et chaque nœud de l'instance est rencontré au plus une fois, parce qu'un champ ou un élément n'a qu'un sous-schéma. Le travail par nœud est borné par le nombre de mots-clés, au plus quinze. Si n est le nombre de nœuds de l'instance, le coût est donc proportionnel à n, à une exception près : le temps d'une expression régulière dépend du motif, ce qui fait l'objet d'un piège plus bas.

### 4. Contre-exemple chiffré : le test naïf du type entier

Le test naïf `isinstance(x, int)` accepte `True`, parce qu'en Python `bool` hérite de `int` : `True == 1` et `True + True == 2`. Sur l'instance `{"personnes_a_charge": true}`, il accepterait « une personne à charge » que personne n'a déclarée, et le calcul de capacité d'emprunt en tiendrait compte. Le même piège touche `enum` : `False in [0, 1]` vaut `True`. La version corrigée écarte `bool` en premier, dans `type_json` comme dans `entier_json`, et compare les valeurs d'une énumération avec `egal_json` ; le programme vérifie les deux cas par `assert`.

### 5. Le coût de la boucle de réparation

La boucle fait au plus R + 1 appels au modèle, parce que `essai` parcourt `range(1, R + 2)` : trois appels pour R = 2, ce que vérifie `llm.appels == 3`. Si chaque essai réussit avec la probabilité p, indépendamment des autres, la probabilité de réussir en au plus R + 1 essais vaut :

$$
P_{succ}(R) = 1 - (1 - p)^{R+1}
$$

Avec p = 0,9 et R = 2, on obtient 0,999, pour 1,11 essai en moyenne. Ces deux résultats, et la limite de l'hypothèse d'indépendance, sont démontrés à l'[étape 11](<11-Schemas-Formule-Taux-de-Validation.md>).

## Du symbole au code Python

La formule de ce fichier, la probabilité de réussir en au plus R + 1 essais, est démontrée à l'étape 11. Son code équivalent est court, et il se vérifie sur les nombres cités plus haut.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`p_succes(p, relances)`** — Cette fonction est le parieur qui calcule ses chances de gagner au moins une manche quand il a droit à plusieurs essais : elle reçoit la probabilité p qu'un essai produise un JSON valide et le nombre R de relances autorisées, lève `ValueError` si p n'est pas dans ]0, 1] ou si R est négatif, puis renvoie 1 − (1 − p) puissance R + 1, le complément de la probabilité que tous les essais échouent quand ils sont indépendants. Avec p = 0,9 et deux relances, elle renvoie 0,999, la valeur que vérifie le premier `assert` et que démontre l'étape 11.

**`essais_moyens(p, relances)`** — Celle-ci est le comptable qui prévoit combien d'appels au modèle la boucle coûtera en moyenne : elle reçoit la même probabilité p et le même nombre de relances R, puis additionne, pour i allant de 0 à R, la probabilité (1 − p) puissance i de devoir faire un essai de plus, c'est-à-dire que les i premiers aient tous échoué. Elle renvoie cette somme sans contrôler ses entrées : 1 + 0,1 + 0,01 = 1,11 essai pour p = 0,9 et R = 2, et le troisième `assert` vérifie qu'elle vaut aussi `p_succes` divisé par p.

```python
# [extrait] Étape 8 — probabilité de succès de la boucle de réparation et nombre moyen d'essais.
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def p_succes(p: float, relances: int) -> float:
    """P_succ(R) = 1 − (1 − p)^(R + 1) : au moins un essai valide parmi R + 1 essais indépendants."""
    if not 0 < p <= 1 or relances < 0:
        raise ValueError("il faut 0 < p <= 1 et relances >= 0")
    return 1 - (1 - p) ** (relances + 1)


def essais_moyens(p: float, relances: int) -> float:
    """E[A] = 1 + (1 − p) + … + (1 − p)^R : on ne fait l'essai i + 1 que si les i premiers ont échoué."""
    return sum((1 - p) ** i for i in range(relances + 1))


assert math.isclose(p_succes(0.9, 2), 0.999)
assert math.isclose(essais_moyens(0.9, 2), 1.11)
assert math.isclose(essais_moyens(0.9, 2), p_succes(0.9, 2) / 0.9)
print("OK — toutes les vérifications sont passées.")
```

### Comment le code fonctionne

`p_succes` passe par le complément, comme la démonstration : la boucle de réparation échoue seulement si les R + 1 essais échouent tous, ce qui arrive avec la probabilité (1 − p) puissance R + 1 quand les essais sont indépendants, et le succès est donc 1 moins ce nombre. La garde refuse p = 0, car aucun essai ne pourrait jamais réussir, et un nombre de relances négatif, qui n'a pas de sens. `essais_moyens` ne calcule pas la formule fermée : elle additionne directement les probabilités de faire un essai de plus, c'est-à-dire la formule des queues de l'étape 11, où chaque terme (1 − p) puissance i est la chance que les i premiers essais aient échoué. Le troisième `assert` vérifie l'identité E[A] = P_succ / p, qui relie les deux fonctions : 0,999 divisé par 0,9 donne bien 1,11 essai.

## Squelette algorithmique

L'algorithme de ce fichier est la boucle de réparation : demander un JSON, le valider, renvoyer les erreurs au modèle, recommencer au plus R fois, puis escalader. La validation elle-même est un parcours récursif du schéma.

```text
ALGORITHME ExtraireAvecRéparation
ENTRÉES : modèle, schéma, demande, R (relances autorisées)
SORTIE  : (statut, données, nombre d'essais)

  messages ← [demande]
  POUR essai DE 1 À R + 1 FAIRE
      réponse ← modèle(messages)
      SI réponse.arrêt ∈ {refus, tronquée} ALORS RETOURNER (réponse.arrêt, aucune, essai)
      (données, erreurs) ← LireEtValider(texte de la réponse, schéma)
      SI erreurs est vide ALORS RETOURNER (« valide », données, essai)
      ajouter la réponse fautive et la liste des erreurs (avec leurs chemins) à messages
  FIN POUR
  RETOURNER (« échec », aucune, R + 1)                 (escalade vers un humain)

ALGORITHME Valider(x, S, chemin)
  SI un mot-clé de S est inconnu ALORS lever une erreur
  SI le type de x ne correspond pas à S.type ALORS RETOURNER [chemin : type attendu]
  erreurs ← erreurs locales (énumération, bornes, motif, longueur, champs obligatoires, champs en trop)
  POUR CHAQUE champ c présent dans x et décrit dans S FAIRE
      erreurs ← erreurs + Valider(x[c], S.properties[c], chemin + "." + c)
  FIN POUR
  POUR CHAQUE élément d'indice i d'un tableau x FAIRE
      erreurs ← erreurs + Valider(x[i], S.items, chemin + "[" + i + "]")
  FIN POUR
  RETOURNER erreurs
```

**Complexité.** La validation visite chaque nœud de l'instance une seule fois, avec au plus une quinzaine de mots-clés par nœud : O(n) pour une instance de n nœuds (démonstration, point 3), à l'exception des expressions régulières dont le coût dépend du motif. La boucle de réparation fait au plus R + 1 appels au modèle, en moyenne 1 + (1 − p) + … + (1 − p)^R, soit 1,11 appel pour p = 0,9 et R = 2. La mémoire grossit d'une réponse et d'une liste d'erreurs par relance, ce qui alourdit chaque appel suivant.

**Du squelette au code.** `ExtraireAvecRéparation` correspond à `extraire_avec_reparation` (la boucle `for essai in range(1, relances_max + 2)`, le traitement de `refusal` et `max_tokens` avant la lecture, l'ajout des erreurs aux messages). `Valider` correspond à `validate`, et `LireEtValider` à `lire_et_valider`, qui fait `json.loads` puis appelle `validate`. Le test du type entier qui écarte les booléens est dans `type_json` et `entier_json`.

## Cas d'usage réels aux Émirats

Les schémas ci-dessous sont des exemples de conception ; les seuils et volumes cités sont illustratifs, sauf les règles réglementaires nommées (plafonds de la CBUAE, TVA de 5 %, formats de l'Emirates ID et de l'IBAN).

### Banque — extraire une demande de crédit d'un courriel

Une banque de détail de Dubaï reçoit des demandes de prêt personnel par courriel, en anglais, en arabe ou en français, que son agent doit transformer en dossier structuré avant tout calcul. Le schéma `DemandeCredit` de ce fichier fixe sept champs : le type de prêt dans une énumération fermée, un montant et un revenu strictement positifs en AED, une durée entière entre 12 et 300 mois, un Emirates ID au format `784-AAAA-NNNNNNN-C`, au plus cinq garanties et un nombre entier de personnes à charge. Quand le modèle écrit `"duree_mois": "36"` ou `"type_pret": "perso"`, le validateur renvoie les erreurs avec leur chemin, et la boucle de réparation relance le modèle une fois, deux au plus ; au troisième échec, le dossier part en revue humaine au lieu d'être deviné. Sans schéma, une durée écrite en texte ou un champ imprévu irait jusqu'au calcul de la mensualité, qui planterait ou, pire, calculerait sur une valeur mal lue. Les plafonds de la CBUAE (ratio d'endettement total de 50 % du revenu, 48 mois pour un prêt personnel) sont des règles inter-champs, vérifiées juste après le schéma à l'étape 9. En production, l'équipe suit le taux de validation au premier passage et après réparation, chacun avec son intervalle de Wilson (étape 11).

### Immobilier — structurer une annonce dictée par un agent

Une agence de Dubaï et d'Abu Dhabi laisse ses agents dicter leurs annonces en une phrase, du type « 2BR Marina 1250 sqft 2.4M ready » (deux chambres, 1 250 sqft, 2,4 millions d'AED, livrable), et un agent IA en tire une fiche structurée. Le schéma impose l'émirat dans l'énumération des sept émirats, une surface en sqft strictement positive, un prix en AED strictement positif, un nombre entier de chambres et un statut dans `["pret", "off-plan"]`. Déclaré `strict: true`, l'outil `publier_annonce` reçoit à coup sûr un émirat de la liste et des nombres là où il faut des nombres, mais pas une surface positive : cette borne est retirée du schéma envoyé et revérifiée localement. Une fois la fiche valide, le prix au sqft se calcule sans ambiguïté : 2 400 000 / 1 250 = 1 920 AED/sqft. Sans schéma, « 2.4M » resterait une chaîne de caractères et l'annonce afficherait un prix illisible, ou le calcul du prix au sqft échouerait au milieu d'un lot. La publication doit respecter les exigences d'information de la DLD et de la RERA (à confirmer avec le texte en vigueur), ce qui ajoute des champs obligatoires que le schéma rend visibles. On suit la part des fiches refusées par le validateur, agent par agent.

### Crypto — un ordre de swap borné

Une plateforme d'actifs virtuels agréée par la VARA prépare des ordres d'échange pour ses clients institutionnels à partir de leurs instructions écrites. Le schéma de l'outil `preparer_swap` impose une adresse de destination au motif `^0x[0-9a-fA-F]{40}$`, un actif dans une énumération, un montant strictement positif et un glissement maximal (slippage) dans [0 ; 0,05]. En mode strict, le motif de l'adresse est garanti par la grammaire, mais la borne `maximum: 0.05` ne l'est pas : seul le validateur local refuse un glissement de 0,5 que le modèle aurait écrit en pensant « 0,5 % ». Cette confusion entre pour cent et fraction autoriserait un glissement de 50 % : un ordre exécuté à la moitié de sa valeur au pire moment. L'agent refuse donc de transmettre l'ordre et repose la question au client. La plateforme doit pouvoir montrer à la VARA quels contrôles précèdent chaque ordre, et le journal des erreurs de validation en fait partie. On suit le nombre d'ordres bloqués par la validation et, comme objectif ferme, zéro ordre transmis hors bornes.

### Assurance — déclarer un sinistre auto sans ambiguïté de date

Un assureur auto et santé laisse ses assurés déclarer un accrochage dans une conversation, en arabe ou en anglais ; l'agent remplit la déclaration. Le schéma impose une date de sinistre au format `AAAA-MM-JJ` (motif `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`, ou `"format": "date"`, que l'API prend aussi en charge), un montant estimé positif ou nul, l'émirat du sinistre et au moins une photo. Quand le modèle recopie « 12/03 », le motif échoue et la réparation demande la date complète ; or « 12/03 » peut vouloir dire le 12 mars ou le 3 décembre, et la garantie n'était peut-être pas en vigueur à l'une des deux dates. Sans schéma, la date ambiguë passerait, et le contrôle de couverture ou de fraude se ferait sur la mauvaise période. La règle « date du sinistre antérieure ou égale à la date de déclaration », qui compare deux champs, s'ajoute à l'étape 9. L'assurance étant supervisée par la CBUAE, la traçabilité de chaque correction est conservée. On suit le taux de déclarations qu'un gestionnaire doit ressaisir à la main.

### RH — une fiche d'embauche qui ne collecte que le nécessaire

Un cabinet RH présent dans plusieurs émirats fait extraire par un agent les données des lettres d'offre : Emirates ID, nationalité au format ISO 3166 alpha-2 (motif `^[A-Z]{2}$`), salaire de base strictement positif et type de contrat dans une énumération. Le mot-clé `additionalProperties: false` sert ici aussi d'outil de minimisation des données : si le modèle ajoute un champ « religion » ou « état de santé » lu dans un document joint, la fiche est refusée avant tout stockage. La PDPL impose de ne traiter que les données nécessaires, et range ce type d'information parmi les données sensibles (à confirmer avec le texte en vigueur) ; le schéma rend cette règle exécutable. Le salaire de base validé alimente ensuite le calcul de fin de service et la déclaration WPS auprès du MOHRE, où une valeur mal typée provoquerait un rejet de paie. Sans schéma, un champ sensible imprévu finirait dans la base, et sa suppression demanderait une procédure d'effacement. On suit le nombre de champs non prévus refusés par semaine : une hausse signale une dérive du prompt ou des documents reçus.

### BTP — lire une facture de sous-traitant

Un groupe de construction qui mène de grands chantiers à Dubaï reçoit des centaines de factures de sous-traitants en PDF chaque mois ; un agent les lit et prépare l'écriture comptable. Le schéma impose un numéro de facture, un montant HT, une TVA et un TTC numériques et positifs, et un IBAN au motif `^AE[0-9]{21}$`. Le schéma garantit la forme ; deux contrôles métier s'ajoutent à l'étape 9 : la clé de contrôle mod 97 de l'IBAN, et l'égalité du TTC avec le HT majoré de la TVA de 5 %, au centime près. Sans schéma, un IBAN recopié avec une espace en trop ou un chiffre manquant passerait jusqu'au virement, qui serait rejeté, ou partirait vers un autre compte si le numéro restait valide par hasard. L'agent bloque la facture invalide et demande au sous-traitant un document corrigé. On suit le taux de factures rejetées par fournisseur, qui sert aussi à repérer les gabarits de facture mal lus.

### Secteur public — un formulaire bilingue rempli par la conversation

Une entité de services publics en ligne, accessible par UAE Pass, laisse l'usager formuler sa demande en arabe ou en anglais ; l'agent remplit le formulaire administratif. Le schéma impose la langue de réponse dans `["ar", "en"]`, l'émirat de résidence dans l'énumération des sept, un motif de demande dans une liste fermée et un numéro de mobile au motif `^\+9715[0-9]{8}$`. Un usager qui tape son numéro en chiffres arabes-indiens (٠٥٠…) pose un vrai problème : en Python, `\d` accepte ces chiffres, alors que JSON Schema prescrit les expressions régulières de JavaScript (norme ECMA-262), où `\d` ne désigne que les chiffres de 0 à 9. Un validateur Python et la grammaire de l'API peuvent donc ne pas accepter les mêmes chaînes : on écrit `[0-9]` dans les motifs et l'on convertit les chiffres arabes-indiens avant la validation. Sans cette normalisation, le même numéro passerait en test et échouerait en production, ou l'inverse. La minimisation des données justifie là encore `additionalProperties: false` ; le régime de protection applicable dépend du statut de l'entité, la PDPL excluant de son champ les autorités publiques, qui relèvent de règles propres (à confirmer avec le texte en vigueur). On suit la part des formulaires transmis sans correction humaine, par langue.

## Pièges et limites

- **Le booléen qui se fait passer pour un entier.** `isinstance(True, int)` est vrai et `False in [0, 1]` aussi : on teste `bool` avant `int` et l'on compare les valeurs d'une énumération avec le type. En TypeScript ou en Java, ce piège n'existe pas ; en Python, il est silencieux.
- **Les motifs de `re` ne sont pas ceux de JavaScript.** `pattern` s'applique avec `re.search`, donc sans ancrage implicite : il faut `^` et `$`. En Python, `$` accepte un saut de ligne final et `\d` accepte les chiffres arabes-indiens, alors que JSON Schema prescrit la syntaxe de JavaScript, où ni l'un ni l'autre n'est vrai ; on écrit `[0-9]`, et les contrôles métier de l'étape 9 (format de l'Emirates ID, IBAN) rattrapent le saut de ligne. Un motif mal écrit, comme `^(a+)+$`, peut prendre un temps exponentiel sur une longue chaîne : on n'accepte jamais un motif fourni par un utilisateur ou par le modèle.
- **`json.loads` accepte `NaN` et `Infinity`.** Ce ne sont pas des valeurs JSON, mais Python les lit, et toute comparaison avec NaN est fausse. Le validateur les refuse ; on peut aussi les bloquer à la lecture avec l'argument `parse_constant` de `json.loads`.
- **Strict ne veut pas dire complet.** Le mode strict garantit la forme, pas les bornes, et un schéma qui contient `minimum` ou `maxLength` est refusé par l'API : on envoie un schéma allégé et l'on garde le schéma complet pour la validation locale. Un refus ou une réponse tronquée peut, de plus, ne pas respecter le schéma.
- **Valide ne veut pas dire vrai.** Un JSON parfaitement conforme peut contenir un montant inventé ou mal lu. La conformité au schéma se complète par un contrôle de fidélité à la source (étape 54) et, pour les montants, par un recalcul (étape 9).

### Exercice feuille blanche

1. Sans regarder le code, écrire `type_json`, `entier_json`, puis une version de `validate` limitée à `type`, `required`, `properties` et `additionalProperties`. La tester avec le schéma `{"type": "object", "properties": {"duree_mois": {"type": "integer"}}, "required": ["duree_mois"], "additionalProperties": false}` sur l'instance `{"duree_mois": "36", "commentaire": "x"}` : elle doit produire deux erreurs, l'une sur `$.duree_mois` (type), l'autre sur `$` (champ non prévu).
2. Prédire, puis vérifier : que renvoie `validate(36.0, {"type": "integer", "maximum": 30})` ? (Réponse : `['$ : 36.0 > maximum 30']`, parce que 36,0 est bien un entier JSON, mais dépasse la borne.)
3. Trouver le bug : une variante d'`entier_json` oublie sa première ligne, `if isinstance(x, bool): return None`. Que renvoie alors `validate(True, {"type": "integer", "minimum": 0})` ? (Réponse : une liste vide. `isinstance(True, int)` étant vrai, `True` passe pour l'entier 1 ; ensuite `type_json(True)` vaut `"boolean"`, si bien qu'aucune borne numérique n'est même testée.) Pourquoi est-ce grave pour le champ `personnes_a_charge` d'un dossier de crédit ?

## Pour aller plus loin

JSON Schema compte bien d'autres mots-clés : `anyOf` et `oneOf` (plusieurs formes possibles), `$ref` et `$defs` (schémas réutilisables), `format` (`date`, `email`, `uuid`), `const`. L'API Claude prend en charge `anyOf`, `allOf` (sans `$ref`), `$ref`, `const` et une liste de formats ; en sortie structurée, les champs obligatoires sont émis avant les champs facultatifs. En Python, la bibliothèque libre `jsonschema` implémente la spécification complète ; le validateur de ce fichier sert à comprendre ce qu'elle fait, pas à la remplacer.

> Suite : [Six schémas EAU vérifiés](<09-Schemas-Exemples-Cas-Usage.md>) — étape 9.
