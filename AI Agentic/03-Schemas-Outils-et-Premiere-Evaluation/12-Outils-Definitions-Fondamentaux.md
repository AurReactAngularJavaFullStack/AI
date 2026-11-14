# Étape 12 — Outils — Définitions fondamentales

> Étape 12 du parcours · Prérequis : [Taux de validation de schéma](<11-Schemas-Formule-Taux-de-Validation.md>) · Suite : [Six agents EAU de bout en bout](<13-Agent-Exemples-Cas-Usage.md>)

**Dossier :** 03-Schemas-Outils-et-Premiere-Evaluation  
**Métiers :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers

Un outil est la seule façon dont un agent agit sur le monde : le modèle ne fait que **demander** un appel, et c'est votre code qui l'exécute. Ce fichier construit, depuis une feuille blanche, la pièce qui se place entre les deux : un registre d'outils qui valide les arguments, vérifie les droits, coupe les appels trop longs, relance les erreurs passagères, n'exécute jamais deux fois le même effet de bord et renvoie toujours la même forme d'erreur. L'ancienne version de ce fichier remplaçait les outils de l'assurance, du BTP et des RH par une phrase vide (« outils métier déjà présents dans tes projets ») et proposait un outil `calculate_dpe_impact`, tiré d'un diagnostic énergétique français sans objet aux Émirats ; les cinq outils EAU ci-dessous les remplacent, avec leur code.

## Définitions

### Outil

Un outil est une fonction ordinaire, exposée au modèle avec un contrat : un nom, une description et un schéma d'entrée. Le modèle choisit l'outil et ses arguments ; le programme vérifie la demande, exécute la fonction et renvoie le résultat au modèle, qui décide de la suite. Dans une architecture hexagonale, chaque outil est un **port sortant** de l'agent : la fonction métier vit dans le domaine, l'outil n'est que l'adaptateur qui la rend appelable par le modèle.

### Nom et description

Le nom est l'identifiant stable que le modèle écrit dans sa demande (`mensualite`, `emettre_facture`) : court, en minuscules, sans espace, et jamais réutilisé pour un autre sens. La description est la seule documentation que le modèle lit avant de choisir : elle dit ce que fait l'outil, dans quelle unité il répond (AED, sqft) et quand **ne pas** l'utiliser. Une description vague fait choisir le mauvais outil ; une description qui promet plus que le code fait inventer des arguments.

### Schéma d'entrée

C'est le JSON Schema des arguments, validé avant toute exécution par le validateur de l'étape 8. Le registre de ce fichier garde le schéma complet (avec les bornes) pour la validation locale, et en dérive le schéma allégé que l'on envoie à l'API en mode strict, sans les mots-clés que le décodage contraint refuse. Le registre est ainsi la source unique du contrat : on ne recopie jamais un schéma à la main à deux endroits.

### Effet de bord

Un outil a un effet de bord quand il change l'état du monde : il émet une facture, enregistre une déclaration, initie un virement. Un outil sans effet de bord (une mensualité, une TVA) peut être appelé dix fois sans conséquence ; un outil avec effet de bord appelé deux fois émet deux factures. Le registre marque chaque outil (`effet_de_bord=True`), et c'est cette marque qui décide des précautions : portée d'écriture, idempotence, et, à l'étape 66, approbation humaine **dans** l'outil.

### Idempotence

Une opération est idempotente quand l'exécuter deux fois a le même effet que l'exécuter une fois. On la garantit par une **clé d'idempotence** : ici, le SHA-256 du nom de l'outil suivi des arguments sérialisés en JSON à clés triées, de sorte que le même appel, quel que soit l'ordre des champs, donne la même clé. Le premier appel stocke son résultat sous cette clé ; un second appel identique renvoie le résultat stocké sans réexécuter l'effet de bord. Pour que deux opérations légitimes différentes ne se confondent pas, les arguments doivent contenir un identifiant métier, comme la référence du devis.

### Timeout

Un timeout est la durée maximale accordée à un appel ; au-delà, on l'abandonne et on le traite comme un échec. Sans timeout, un service distant bloqué bloque l'agent entier, qui ne répond plus à l'utilisateur. Un timeout est une erreur **ambiguë** : le service a peut-être exécuté la demande sans avoir eu le temps de répondre, et c'est pourquoi on ne relance un outil à effet de bord qu'avec une clé d'idempotence.

### Erreur transitoire, erreur permanente

Une erreur transitoire (timeout, service saturé, coupure réseau) peut disparaître d'elle-même : on relance. Une erreur permanente (arguments invalides, client inconnu, droit manquant) reviendrait à l'identique : relancer ne fait que perdre du temps et de l'argent, on renvoie l'erreur au modèle. Le registre distingue les deux familles et ne relance que la première.

### Backoff exponentiel et jitter

Entre deux tentatives, on attend un délai qui double à chaque relance, dₙ = min(D_max, b × 2ⁿ), pour laisser au service le temps de se rétablir sans le noyer sous les relances. Le **jitter** ajoute au délai une part aléatoire, tirée d'un générateur à graine fixe pour que les tests soient reproductibles : il évite que mille agents qui ont échoué au même instant relancent tous au même instant.

### Authentification et portée

L'authentification établit **qui** appelle (un utilisateur connecté par UAE Pass, un service interne muni d'un jeton) ; l'autorisation décide de **ce qu'il peut faire**, exprimé ici par des portées (`lecture`, `ecriture:facturation`). Le registre refuse l'appel d'un outil dont la portée n'a pas été accordée, avant toute validation et toute exécution. Le modèle ne reçoit jamais de secret : les jetons restent dans le code qui exécute l'outil.

### Enveloppe d'erreur

Tous les échecs prennent la même forme, `{"ok": false, "erreur": {"type", "message", "outil", "tentatives", "details"}}`, et tous les succès la forme `{"ok": true, "resultat", "tentatives", "depuis_cache"}`. Le modèle apprend ainsi à lire une seule structure, le journal se requête par `erreur.type`, et aucune exception Python n'atteint la boucle d'agent.

## Rôle dans un agent

Dans la boucle percevoir → décider → agir → observer, le registre **est** l'étape « agir ». La boucle d'agent (étape 13) reçoit du modèle un bloc `tool_use` avec un nom et des arguments, appelle `appeler_outil`, et renvoie l'enveloppe au modèle dans un bloc `tool_result`, qu'elle soit un succès ou une erreur. Tout ce que le modèle peut faire de dangereux passe par ce point : c'est donc là que se placent la validation, les portées, l'idempotence et, plus tard, l'approbation humaine et le journal d'audit (étape 66).

## Construire depuis une feuille blanche

Le programme ci-dessous est autonome : il recopie le validateur de l'étape 8, les fonctions canoniques du parcours, puis construit l'horloge simulée, le décorateur `@outil`, le registre, `appeler_outil` et six outils EAU.

### Déroulé, ligne par ligne

**Le validateur et `schema_pour_api_strict`** sont recopiés de l'étape 8 sans changement, avec `mots_cles_utilises`. **Les fonctions canoniques** `mensualite`, `gratuite_fin_de_service`, `tva` et `disponibilite_serie` sont recopiées du code commun.

**`Horloge`** est un simple compteur `t`, en secondes simulées. Aucun `time.sleep` ni aucune horloge réelle : un outil « coûte » du temps en faisant avancer ce compteur, et une attente avant relance aussi. Les tests deviennent instantanés et reproductibles, et l'on peut vérifier une durée totale au centième près.

**`delai_backoff(n, base, plafond, rng, jitter)`** calcule l'attente avant la relance `n` (0 pour la première). `nominal = min(plafond, base * 2 ** n)` : avec `base = 0.5`, cela donne 0,5, 1, 2, 4… secondes, bloquées au plafond. Sans générateur (`rng=None`), la fonction renvoie le délai nominal ; en mode `"additif"`, elle ajoute un tirage uniforme dans [0 ; base] ; en mode `"complet"`, elle tire uniformément dans [0 ; nominal].

**`Outil`** est une `dataclass` qui porte le contrat d'un outil (nom, description, schéma, fonction, effet de bord, portée) et sa simulation : `latences` liste la durée simulée de chaque appel successif, la dernière valeur se répétant. `latence_suivante()` lit la durée du prochain appel et incrémente `appels`. Mettre `latences = [3.0, 3.0, 0.4]` simule un service qui répond en 3 s deux fois de suite, puis en 0,4 s.

**`outil(nom, description, schema, effet_de_bord, portee)`** est un décorateur à paramètres : `outil(...)` renvoie la fonction `enregistrer`, que Python applique à la fonction décorée. `enregistrer` crée l'`Outil`, le range dans `REGISTRE[nom]` et rend la fonction inchangée. Un nom déjà pris lève `ValueError`, pour qu'un outil n'en écrase jamais un autre en silence.

**`erreur(type_, message, nom, tentatives, details)`** fabrique l'enveloppe d'erreur unique ; `cle_idempotence(nom, arguments)` calcule `sha256(nom + json.dumps(arguments, sort_keys=True))`.

**`appeler_outil(nom, arguments, ...)`**, dans l'ordre exact des contrôles.

1. Outil inconnu : enveloppe `outil_inconnu`, sans exception.
2. Portée : si `o.portee` n'est pas dans `portees`, enveloppe `non_autorise`. Le contrôle passe avant la validation, pour ne rien révéler du contrat à qui n'y a pas droit.
3. Validation : `validate(arguments, o.schema)` ; la moindre erreur donne `arguments_invalides`, avec les chemins JSON dans `details`, et la fonction n'est pas appelée (le compteur `appels` ne bouge pas).
4. Idempotence : si la clé est dans `CACHE`, on renvoie une copie du résultat stocké, marquée `depuis_cache=True`.
5. La boucle `for tentative in range(1, relances_max + 2)` fait au plus `relances_max + 1 = 4` tentatives. Si la durée simulée dépasse `timeout`, l'horloge avance de `timeout` seulement (l'appel est coupé) et la fonction n'est pas exécutée : c'est l'hypothèse de la simulation, plus optimiste que la réalité (voir les pièges). Sinon, l'horloge avance de la durée et la fonction s'exécute. `ServiceIndisponible` est transitoire ; `ValueError` et `TypeError` sont permanentes et sortent tout de suite en `erreur_metier`. Un succès est stocké dans `CACHE`.
6. Après un échec transitoire, si une relance reste possible, l'horloge avance de `delai_backoff(tentative - 1, ...)`. Après la dernière tentative, l'enveloppe `transitoire_epuise` porte le dernier motif.

**`definitions_api()`** transforme le registre en liste d'outils au format de l'API : `name`, `description`, `input_schema` allégé par `schema_pour_api_strict`, et `strict: True`. C'est cette liste que la boucle de l'étape 13 passe au modèle. Pour `mensualite`, elle produit :

```json
{
  "name": "mensualite",
  "description": "Mensualité d'un prêt amortissable, en AED.",
  "input_schema": {
    "type": "object",
    "properties": {
      "principal": {"type": "number", "description": "Contraintes : exclusiveMinimum=0."},
      "taux_annuel": {"type": "number", "description": "Contraintes : minimum=0, maximum=0.3."},
      "n_mois": {"type": "integer", "description": "Contraintes : minimum=1, maximum=300."}
    },
    "required": ["principal", "taux_annuel", "n_mois"],
    "additionalProperties": false
  },
  "strict": true
}
```

**Les six outils EAU.** Chaque fonction est décorée par `@outil` avec son schéma, construit par `objet(...)` (tous les champs obligatoires, aucun champ non prévu), et renvoie un dictionnaire JSON.

- `mensualite` arrondit la mensualité canonique au fils : 5 558,32 AED pour 1 000 000 AED à 4,5 % sur 300 mois.
- `estimer_prix` prend la médiane des prix au sqft des comparables, `statistics.median([1850, 1900, 1920, 1980, 2050])` = 1 920, et la multiplie par la surface : 1 920 × 1 250 = 2 400 000 AED. Les quartiles inclusifs, 1 900 et 1 980, donnent la fourchette [2 375 000 ; 2 475 000]. La médiane résiste à un comparable aberrant, contrairement à la moyenne.
- `indemnite_sinistre` applique `min(plafond, max(0, dommage × (1 − vétusté) − franchise))` : 18 000 × 0,8 − 500 = 13 900 AED ; 80 000 × 0,9 − 500 = 71 500, plafonné à 50 000 ; 400 − 500 = −100, ramené à 0, parce qu'une franchise supérieure au dommage ne fait pas payer l'assuré.
- `gratuite_fin_de_service` enveloppe la fonction canonique : 10 000 AED de base et 7 ans donnent 5 × 21 × 333,33 + 2 × 30 × 333,33 = 35 000 + 20 000 = 55 000 AED.
- `tva` renvoie la TVA de 5 % et le TTC : 600 et 12 600 AED pour 12 000 AED HT.
- `emettre_facture` a un effet de bord : elle ajoute une facture à `FACTURES_EMISES` et lui donne le numéro suivant. Elle exige la portée `ecriture:facturation` et refuse un client inconnu par `ValueError`.

**`main()`**, section par section.

1. Le registre contient six outils ; les définitions pour l'API ne contiennent plus aucun mot-clé refusé en mode strict.
2. Les cinq outils de calcul rendent les valeurs ci-dessus, vérifiées par `assert`.
3. Deux comparables seulement : `arguments_invalides` et `appels` inchangé. Un outil inconnu, une facture sans la portée d'écriture, puis un client inconnu (`erreur_metier` dès la première tentative, sans relance) : `FACTURES_EMISES` reste vide. L'enveloppe a exactement les clés annoncées.
4. On vide le cache (sinon le résultat de la section 2 reviendrait sans appel) et l'on simule `[3.0, 3.0, 0.4]` : deux timeouts à 2 s, deux attentes de 0,5 puis 1 seconde plus un jitter d'au plus 0,5 s, puis un succès en 0,4 s ; la durée totale, 6,211 s, est bien dans l'intervalle [5,9 ; 6,9] calculé à la main. Sans jitter et avec un service toujours trop lent, quatre tentatives coûtent exactement 4 × 2 + 0,5 × (2³ − 1) = 11,5 s.
5. La même facture envoyée deux fois, la seconde avec ses champs dans l'autre ordre, ne crée qu'une facture ; une référence de devis différente en crée une seconde, numérotée `FAC-2026-00002`.
6. Les délais cumulés sans plafond valent `0.5 * (2 ** k - 1)` pour k de 1 à 5 ; avec un plafond de 4, la suite 0,5 ; 1 ; 2 ; 4 ; 4 ; 4 totalise 15,5 s ; la moyenne de 100 000 tirages du jitter complet sur [0 ; 4] vaut 1,9961, à moins de 0,02 de la valeur théorique 2.
7. Trois outils à 0,99 en série donnent 0,970299 ; avec une relance par outil, 0,999700.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`type_json(x)`** — C'est la même fonction que dans le programme de l'étape 8 : l'officier d'état civil reçoit une valeur Python et renvoie son nom JSON, `"null"`, `"boolean"`, `"integer"`, `"number"`, `"string"`, `"array"` ou `"object"`, en testant les booléens avant les entiers puisque `True` est aussi un `int`. Une valeur sans équivalent JSON lève `ValueError`. Dans le registre, elle sert au validateur pour écrire le type reçu quand les arguments d'un outil ne respectent pas son schéma, avant même que la fonction de l'outil soit appelée.

**`entier_json(x)`** — Reprise sans changement de l'étape 8, cette fonction est le contrôleur qui ne reconnaît comme entier que ce que JSON appellerait ainsi : elle renvoie `None` pour un booléen, l'entier lui-même pour un `int`, sa conversion en `int` pour un flottant dont la partie décimale est nulle, et `None` pour tout le reste. Elle ne lève rien. Ici, elle garantit par exemple que l'argument `n_mois` de l'outil `mensualite` est un vrai entier, et qu'un `true` envoyé par le modèle ne passe pas pour 1 mois.

**`correspond(x, nom)`** — Même fonction que dans le programme de l'étape 8 : comme un portier qui compare un badge à la liste des accès, elle reçoit une valeur et un nom de type JSON, délègue à `entier_json` pour `"integer"`, accepte entiers et décimaux pour `"number"` et compare `type_json(x)` au nom attendu dans les autres cas. Elle renvoie ce booléen, que `validate` consulte pour chaque argument d'outil, comme la surface en sqft ou le montant hors taxes d'une facture, qui doivent être des nombres.

**`egal_json(a, b)`** — Reprise de l'étape 8, cette fonction est l'arbitre qui compare deux valeurs comme JSON et non comme Python : elle renvoie vrai seulement si les deux valeurs sont toutes deux booléennes ou toutes deux non booléennes, et égales. Ainsi `False` n'égale pas 0, alors que 1.0 égale 1. Elle ne lève rien. Aucun des six schémas d'outils de ce fichier n'utilise d'énumération, mais le validateur la garde pour rester identique à celui de l'étape 8, qui s'en sert dans le mot-clé `enum`.

**`validate(instance, schema, path)`** — C'est le validateur de l'étape 8, recopié sans changement : l'inspecteur reçoit une instance, un schéma et un chemin, `"$"` par défaut, refuse par `ValueError` tout mot-clé qu'il ne sait pas vérifier, renvoie une seule erreur si le type ne correspond pas, puis contrôle énumérations, bornes, longueurs, motifs, tableaux et objets en se rappelant sur chaque champ. Il renvoie la liste des erreurs avec leur chemin ; dans `appeler_outil`, c'est le troisième contrôle, et la liste devient les `details` de l'erreur `arguments_invalides`, comme `$.comparables_aed_sqft : 2 élément(s) < minItems 3`.

**`schema_pour_api_strict(schema)`** — Reprise de l'étape 8, cette fonction est le traducteur qui adapte un contrat aux exigences d'un guichet plus pointilleux : elle reçoit un schéma, en recopie les clés en retirant les sept mots-clés que le mode strict de l'API refuse, ainsi que `minItems` au-delà de 1, traite récursivement `properties` et `items`, et reporte les contraintes retirées dans la description, par exemple « Contraintes : minimum=1, maximum=300. » pour `n_mois`. Elle renvoie cette copie sans modifier l'original ; `definitions_api` l'applique au schéma de chaque outil du registre.

**`mots_cles_utilises(schema)`** — Même géomètre que dans le programme de l'étape 8 : la fonction reçoit un schéma, part de l'ensemble de ses clés et y ajoute récursivement celles des sous-schémas de `properties` et de `items`, puis renvoie cet ensemble. Elle ne lève rien. La première section de `main` s'en sert pour vérifier que chacune des six définitions produites pour l'API ne contient plus aucun des mots-clés de `NON_PRIS_EN_CHARGE_STRICT`, sans quoi l'API refuserait la requête.

**`mensualite(principal, taux_annuel, n_mois)`** — C'est le calculateur du banquier, commun à tout le parcours : il reçoit le capital, le taux annuel et la durée en mois, lève `ValueError` si le capital ou la durée ne sont pas positifs ou si le taux est négatif, puis renvoie P r / (1 − (1 + r)⁻ⁿ) avec le taux mensuel r, ou P / n à taux nul. Dans ce fichier, il est enveloppé par l'outil `mensualite`, qui arrondit le résultat au fils : 5 558,32 AED pour 1 000 000 AED à 4,5 % sur 300 mois.

**`gratuite_fin_de_service(salaire_base_mensuel, annees)`** — Cette fonction commune est le gestionnaire de paie qui solde un départ selon le décret-loi fédéral 33/2021 : elle reçoit le salaire de base et l'ancienneté, renvoie 0 sous un an de service, compte 21 jours de salaire de base par an pour les cinq premières années et 30 jours au-delà, au prorata, avec un salaire journalier égal au trentième du salaire de base, et plafonne le total à 24 mois de salaire de base. Elle renvoie ce montant : 55 000 AED pour 10 000 AED de base et 7 ans, que l'outil du même nom renvoie arrondi.

**`tva(montant_ht, taux)`** — Même fonction commune que dans les programmes précédents, le percepteur sobre qui renvoie le produit d'un montant hors taxes par un taux, 0,05 par défaut, sans arrondi ni contrôle de signe. Ici, c'est l'outil `tva` du registre qui l'appelle deux fois, pour la taxe et pour le total : sur 12 000 AED hors taxes, il renvoie 600 AED de TVA et 12 600 AED TTC, les deux valeurs que la deuxième section de `main` compare au résultat de l'enveloppe.

**`disponibilite_serie(dispos)`** — Cette fonction est l'ingénieur fiabilité qui sait qu'une chaîne ne vaut que par tous ses maillons : elle reçoit la liste des disponibilités des outils appelés en série et renvoie leur produit, calculé par `math.prod`, c'est-à-dire la probabilité que tous répondent quand leurs pannes sont indépendantes. Elle ne contrôle pas ses entrées. Trois outils à 0,99 donnent 0,970299, et la même chaîne avec une relance par outil, chaque outil passant alors à 1 − 0,01² = 0,9999, atteint 0,9997, comme le vérifie la dernière section de `main`.

**`Horloge.__init__()`** — Le constructeur de l'horloge simulée remet les aiguilles à zéro, comme un chronométreur qui arme son chronomètre avant la course : il ne reçoit rien et fixe le compteur `t` à 0,0 seconde, sans rien renvoyer. Le programme n'en crée qu'une, la constante `HORLOGE`, qui remplace toute horloge réelle et tout `time.sleep` : les tests de timeout et de relance deviennent ainsi instantanés et reproductibles, et l'on peut vérifier une durée totale au millième près.

**`Horloge.avancer(secondes)`** — Cette méthode est le seul moyen de faire passer le temps dans ce monde simulé : elle reçoit un nombre de secondes et l'ajoute au compteur `t`, sans rien renvoyer ni rien vérifier. `appeler_outil` l'appelle dans trois cas, comme un huissier qui note chaque minute facturée : la durée simulée d'un appel réussi, la valeur du timeout quand l'appel est coupé, et l'attente calculée par `delai_backoff` avant une relance. C'est ce qui donne les 6,211 s de la section 4 et les 11,5 s exactes du service toujours trop lent.

**`delai_backoff(n, base, plafond, rng, jitter)`** — C'est le régulateur qui espace les relances comme un standardiste qui rappelle un correspondant occupé de moins en moins souvent : la fonction reçoit l'indice n de la relance, 0 pour la première, le délai de base, le plafond, un générateur aléatoire facultatif et le mode de jitter, `"additif"` par défaut. Elle calcule le délai nominal, le plus petit entre le plafond et base × 2ⁿ, le renvoie tel quel sans générateur, y ajoute un tirage uniforme dans [0 ; base] en mode additif ou le remplace par un tirage dans [0 ; nominal] en mode complet, et lève `ValueError` pour tout autre mode. Avec base 0,5 et plafond 4, la suite vaut 0,5, 1, 2, 4, 4 et 4, soit 15,5 s.

**`Outil.latence_suivante()`** — Cette méthode de la fiche d'un outil joue le service distant dont on a écrit d'avance les temps de réponse : elle lit dans la liste `latences` la durée du prochain appel, à l'indice du nombre d'appels déjà faits, la dernière valeur se répétant ensuite, incrémente le compteur `appels` et renvoie cette durée. Avec `[3.0, 3.0, 0.4]`, le service répond en 3 s deux fois, ce qui dépasse le timeout de 2 s, puis en 0,4 s ; et c'est parce que le compteur ne bouge pas quand la validation échoue que `main` peut prouver qu'un outil mal appelé n'a jamais été exécuté.

**`outil(nom, description, schema, effet_de_bord, portee)`** — C'est le notaire qui inscrit chaque outil au registre avec son contrat : la fonction reçoit le nom public de l'outil, sa description, son schéma JSON, un indicateur d'effet de bord, faux par défaut, et la portée requise, `"lecture"` par défaut, puis renvoie la fonction interne `enregistrer`, que Python applique à la fonction décorée. On s'en sert comme décorateur à paramètres, `@outil(...)`, au-dessus de chacun des six outils EAU, et c'est grâce à elle que le registre devient la source unique du contrat, de la validation à la liste envoyée à l'API.

**`enregistrer(fonction)`** — Cette fonction interne, définie à l'intérieur d'`outil`, est le geste même de l'inscription : elle reçoit la fonction Python décorée, lève `ValueError` avec le message « outil déjà enregistré » si le nom est déjà pris, pour qu'aucun outil n'en écrase un autre en silence, puis crée la fiche `Outil` avec le nom, la description, le schéma, la fonction, l'effet de bord et la portée, et la range dans `REGISTRE`. Elle renvoie la fonction inchangée, qui reste donc appelable directement ; à la fin du chargement du module, le registre compte six outils.

**`erreur(type_, message, nom, tentatives, details)`** — C'est le formulaire unique de réclamation, que tous les échecs remplissent de la même façon : la fonction reçoit le type d'erreur, un message, le nom de l'outil, le nombre de tentatives, 0 par défaut, et une liste de détails facultative, puis renvoie le dictionnaire `{"ok": False, "erreur": {...}}` avec exactement les cinq clés type, message, outil, tentatives et details, cette dernière valant une liste vide si rien n'est fourni. Ainsi, le modèle comme le journal lisent toujours la même forme, que l'échec vienne d'un outil inconnu, d'une portée manquante ou d'un client inconnu.

**`cle_idempotence(nom, arguments)`** — Celle-ci est l'archiviste qui reconnaît un dossier déjà traité même si les pièces arrivent dans un autre ordre : elle reçoit le nom de l'outil et ses arguments, sérialise les arguments en JSON avec les clés triées, concatène le nom et cette chaîne, l'encode en UTF-8 et renvoie l'empreinte SHA-256 en hexadécimal. Deux appels identiques, même avec leurs champs dans un ordre différent, ont donc la même clé ; dans `main`, la facture envoyée une seconde fois avec ses champs inversés est reconnue et ne crée pas de deuxième document.

**`appeler_outil(nom, arguments, portees, timeout, relances_max, base, plafond, rng, journal)`** — C'est le guichet unique par lequel passe chaque action de l'agent, avec six contrôles dans un ordre fixe : il reçoit le nom de l'outil, ses arguments et, en paramètres nommés, les portées accordées, `{"lecture"}` par défaut, un timeout de 2 s, 3 relances au plus, la base et le plafond du backoff, un générateur et un journal facultatifs. Il renvoie `outil_inconnu`, `non_autorise` ou `arguments_invalides` sans rien exécuter, puis le résultat en cache marqué `depuis_cache` si la clé d'idempotence est connue ; sinon il fait jusqu'à quatre tentatives, coupe celles qui dépassent le timeout, relance après une erreur transitoire en avançant l'horloge du délai de backoff, renvoie aussitôt `erreur_metier` sur une `ValueError` ou une `TypeError`, et `transitoire_epuise` après la dernière tentative. Il ne lève jamais d'exception vers la boucle d'agent : succès comme échec reviennent dans une enveloppe, et un succès est mis en cache.

**`definitions_api()`** — Cette fonction est le crieur public qui annonce au modèle la liste des outils disponibles, dans la langue de l'API : elle ne reçoit rien, parcourt le registre et renvoie, pour chaque outil, un dictionnaire avec son nom, sa description, son schéma allégé par `schema_pour_api_strict` et le drapeau `strict` à vrai. Elle ne lève rien ; avec les six outils du fichier, la liste commence par `mensualite` puis `estimer_prix`, et c'est elle que la boucle de l'étape 13 passe au modèle, si bien que le contrat n'est écrit qu'une seule fois.

**`objet(proprietes)`** — C'est la même fonction que dans le programme de l'étape 9 : le notaire qui rédige un contrat sans clause facultative reçoit un dictionnaire de propriétés et renvoie un schéma d'objet où `required` contient tous les champs et où `additionalProperties` vaut `False`. Elle ne vérifie rien et ne lève rien. Les six schémas d'outils sont construits avec elle, si bien qu'un argument manquant ou inventé par le modèle est refusé par `validate` avant que l'outil ne s'exécute.

**`outil_mensualite(principal, taux_annuel, n_mois)`** — Cette fonction, inscrite au registre sous le nom public `mensualite`, est le guichet de crédit de l'agent : son schéma exige un capital strictement positif, un taux entre 0 et 0,3 et une durée entière de 1 à 300 mois, puis elle appelle la fonction canonique `mensualite` et renvoie le dictionnaire `{"mensualite_aed": ...}` arrondi au fils. Une erreur de la fonction canonique remonterait en `ValueError`, que `appeler_outil` transforme en `erreur_metier`. Pour 1 000 000 AED à 4,5 % sur 300 mois, l'enveloppe contient 5 558,32 AED, obtenus en une seule tentative.

**`outil_estimer_prix(surface_sqft, comparables_aed_sqft)`** — Inscrite sous le nom `estimer_prix`, cette fonction est l'expert immobilier qui estime un bien d'après ses voisins : son schéma exige une surface positive et au moins trois prix au sqft positifs, puis elle prend la médiane des comparables, qui résiste à une vente aberrante, la multiplie par la surface, et calcule la fourchette à partir du premier et du troisième quartile inclusifs. Elle renvoie la médiane, le prix estimé et la fourchette, arrondis : pour 1 250 sqft et les prix 1 850, 1 900, 1 920, 1 980 et 2 050, la médiane vaut 1 920, le prix 2 400 000 AED et la fourchette va de 2 375 000 à 2 475 000 AED.

**`outil_indemnite(dommage_aed, vetuste, franchise_aed, plafond_aed)`** — Inscrite sous le nom `indemnite_sinistre`, cette fonction est l'expert d'assurance de l'agent : son schéma borne la vétusté entre 0 et 1 et exige des montants positifs, puis elle applique la vétusté au dommage, retranche la franchise, ramène à 0 un résultat négatif, plafonne et renvoie `{"indemnite_aed": ...}` arrondi au centième. Les trois cas de `main` donnent 13 900 AED pour 18 000 AED à 20 % de vétusté, 50 000 AED plafonnés pour 80 000 AED à 10 %, et 0 quand la franchise de 500 AED dépasse un dommage de 400 AED.

**`outil_gratuite(salaire_base_mensuel, annees)`** — Inscrite sous le nom `gratuite_fin_de_service`, cette fonction est le guichet RH de l'agent : son schéma exige un salaire de base strictement positif et une ancienneté comprise entre 0 et 60 ans, puis elle appelle la fonction canonique du décret-loi 33/2021 et renvoie `{"indemnite_aed": ...}` arrondi au centième. Elle ne lève rien elle-même. Pour 10 000 AED de salaire de base et 7 ans de service, l'enveloppe contient 55 000 AED, soit 35 000 AED pour les cinq premières années et 20 000 AED pour les deux suivantes.

**`outil_tva(montant_ht)`** — Inscrite sous le nom `tva`, cette fonction est la caisse enregistreuse de l'agent : son schéma n'exige qu'un montant hors taxes positif ou nul, puis elle calcule la TVA de 5 % avec la fonction canonique et renvoie un dictionnaire avec la taxe et le total TTC, chacun arrondi au centième. Elle ne lève pas d'exception. Pour 12 000 AED hors taxes, elle renvoie 600 AED de TVA et 12 600 AED TTC ; c'est l'un des cinq outils de calcul sans effet de bord, appelables avec la seule portée `"lecture"`.

**`outil_emettre_facture(reference_devis, client, montant_ht_aed)`** — Inscrite sous le nom `emettre_facture`, c'est la seule fonction du registre qui change le monde, comme un comptable qui tamponne un document officiel : elle exige la portée `ecriture:facturation`, une référence de devis au format DEV suivi de cinq chiffres, un client au format CLI suivi de quatre chiffres et un montant positif, lève `ValueError` si le client n'est pas dans `CLIENTS_CONNUS`, puis numérote la facture d'après le nombre de factures déjà émises, l'ajoute à `FACTURES_EMISES` et renvoie le numéro et le TTC. Pour 120 000 AED, elle renvoie `FAC-2026-00001` et 126 000 AED ; la même demande renvoyée sort du cache, et un autre devis donne `FAC-2026-00002`.

**`main()`** — C'est l'inspecteur qui éprouve le registre en sept tournées : il liste les six outils et vérifie leurs définitions pour l'API, appelle les cinq outils de calcul et compare leurs résultats, puis montre ce qui n'est jamais exécuté, deux comparables seulement, un outil « virement » inconnu, une facture sans la portée d'écriture et un client inconnu, sans qu'aucune facture soit émise. Il simule ensuite un service lent, réussi à la troisième tentative en 6,211 s, puis toujours trop lent, abandonné après 11,5 s, vérifie l'idempotence de la facture, la suite des délais de relance et la moyenne 1,9961 du jitter complet, et termine par la disponibilité 0,970299 de trois outils en série.

```python
"""Étape 12 — un registre d'outils écrit à la main : validation, timeout simulé, relances, idempotence."""
import hashlib
import json
import math
import random
import re
import statistics
import sys
from dataclasses import dataclass, field

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- validateur de l'étape 8 (recopié sans changement)
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


# ---------------------------------------------------------------- fonctions canoniques du parcours (recopiées)
def mensualite(principal: float, taux_annuel: float, n_mois: int) -> float:
    """M = P r / (1 - (1 + r)^-n), r = taux mensuel ; M = P / n si le taux est nul."""
    if principal <= 0 or n_mois <= 0 or taux_annuel < 0:
        raise ValueError("principal > 0, n_mois > 0, taux >= 0")
    r = taux_annuel / 12
    return principal / n_mois if r == 0 else principal * r / (1 - (1 + r) ** -n_mois)


def gratuite_fin_de_service(salaire_base_mensuel: float, annees: float) -> float:
    """Décret-loi fédéral 33/2021 (secteur privé, hors ressortissants émiriens et hors DIFC) :
    au moins 1 an de service ; salaire journalier = base / 30 ; 21 jours par an les 5 premières années,
    30 jours au-delà, au prorata ; plafond : 24 mois de salaire de base."""
    if annees < 1:
        return 0.0
    jour = salaire_base_mensuel / 30
    brut = min(annees, 5) * 21 * jour + max(annees - 5, 0) * 30 * jour
    return min(brut, 24 * salaire_base_mensuel)


def tva(montant_ht: float, taux: float = 0.05) -> float:
    """TVA standard des EAU : 5 %. (Loyer résidentiel exonéré ; première livraison d'un bien résidentiel au taux zéro.)"""
    return montant_ht * taux


def disponibilite_serie(dispos: list[float]) -> float:
    return math.prod(dispos)


# ---------------------------------------------------------------- horloge simulée et délais de relance
class Horloge:
    """Le temps n'avance que lorsqu'un outil « coûte » du temps ou qu'on attend avant une relance."""

    def __init__(self) -> None:
        self.t = 0.0

    def avancer(self, secondes: float) -> None:
        self.t += secondes


HORLOGE = Horloge()


def delai_backoff(n: int, base: float, plafond: float, rng: random.Random | None = None,
                  jitter: str = "additif") -> float:
    """Attente avant la relance n (n = 0 pour la première) : min(plafond, base × 2^n), plus un jitter."""
    nominal = min(plafond, base * 2 ** n)
    if rng is None:
        return nominal
    if jitter == "additif":
        return nominal + rng.uniform(0.0, base)        # délai nominal + tirage dans [0 ; base]
    if jitter == "complet":
        return rng.uniform(0.0, nominal)               # tirage dans [0 ; délai nominal]
    raise ValueError("jitter : 'additif' ou 'complet'")


# ---------------------------------------------------------------- registre d'outils
@dataclass
class Outil:
    nom: str
    description: str
    schema: dict
    fonction: object
    effet_de_bord: bool
    portee: str
    latences: list[float] = field(default_factory=lambda: [0.2])   # durée simulée de chaque appel, en secondes
    appels: int = 0                                                # appels réellement exécutés ou coupés

    def latence_suivante(self) -> float:
        duree = self.latences[min(self.appels, len(self.latences) - 1)]
        self.appels += 1
        return duree


REGISTRE: dict[str, Outil] = {}
CACHE: dict[str, dict] = {}


def outil(nom: str, description: str, schema: dict, effet_de_bord: bool = False, portee: str = "lecture"):
    """Décorateur : enregistre la fonction dans REGISTRE sous son nom public, avec son contrat."""
    def enregistrer(fonction):
        if nom in REGISTRE:
            raise ValueError(f"outil déjà enregistré : {nom}")
        REGISTRE[nom] = Outil(nom, description, schema, fonction, effet_de_bord, portee)
        return fonction
    return enregistrer


class ServiceIndisponible(Exception):
    """Erreur transitoire (service distant saturé, coupure réseau) : on peut relancer."""


def erreur(type_: str, message: str, nom: str, tentatives: int = 0, details: list | None = None) -> dict:
    """L'enveloppe d'erreur unique : le modèle et le journal lisent toujours la même forme."""
    return {"ok": False, "erreur": {"type": type_, "message": message, "outil": nom,
                                    "tentatives": tentatives, "details": details or []}}


def cle_idempotence(nom: str, arguments: dict) -> str:
    return hashlib.sha256((nom + json.dumps(arguments, sort_keys=True, ensure_ascii=False)).encode("utf-8")).hexdigest()


def appeler_outil(nom: str, arguments: dict, *, portees: frozenset = frozenset({"lecture"}), timeout: float = 2.0,
                  relances_max: int = 3, base: float = 0.5, plafond: float = 8.0,
                  rng: random.Random | None = None, journal: list | None = None) -> dict:
    """Valide, autorise, déduplique, exécute avec un timeout simulé et relance les erreurs transitoires."""
    if nom not in REGISTRE:
        return erreur("outil_inconnu", f"aucun outil ne s'appelle {nom!r}", nom)
    o = REGISTRE[nom]
    if o.portee not in portees:
        return erreur("non_autorise", f"portée {o.portee!r} requise", nom)
    details = validate(arguments, o.schema)
    if details:
        return erreur("arguments_invalides", "les arguments ne respectent pas le schéma", nom, 0, details)
    cle = cle_idempotence(nom, arguments)
    if cle in CACHE:
        return dict(CACHE[cle], depuis_cache=True)
    derniere = ""
    for tentative in range(1, relances_max + 2):
        duree = o.latence_suivante()
        if duree > timeout:                              # coupé : l'horloge avance du timeout, pas plus
            HORLOGE.avancer(timeout)
            derniere = f"timeout après {timeout} s"
        else:
            HORLOGE.avancer(duree)
            try:
                resultat = o.fonction(**arguments)
            except ServiceIndisponible as e:
                derniere = f"service indisponible : {e}"
            except (ValueError, TypeError) as e:          # erreur permanente : relancer ne changerait rien
                return erreur("erreur_metier", str(e), nom, tentative)
            else:
                enveloppe = {"ok": True, "resultat": resultat, "tentatives": tentative, "depuis_cache": False}
                CACHE[cle] = enveloppe
                return enveloppe
        if journal is not None:
            journal.append((round(HORLOGE.t, 3), nom, tentative, derniere))
        if tentative <= relances_max:
            HORLOGE.avancer(delai_backoff(tentative - 1, base, plafond, rng))
    return erreur("transitoire_epuise", derniere, nom, relances_max + 1)


def definitions_api() -> list[dict]:
    """Le registre est la source unique : il produit aussi la liste d'outils au format de l'API (mode strict)."""
    return [{"name": o.nom, "description": o.description, "input_schema": schema_pour_api_strict(o.schema),
             "strict": True} for o in REGISTRE.values()]


# ---------------------------------------------------------------- outils EAU
def objet(proprietes: dict) -> dict:
    return {"type": "object", "properties": proprietes, "required": list(proprietes), "additionalProperties": False}


@outil("mensualite", "Mensualité d'un prêt amortissable, en AED.", objet({
    "principal": {"type": "number", "exclusiveMinimum": 0},
    "taux_annuel": {"type": "number", "minimum": 0, "maximum": 0.3},
    "n_mois": {"type": "integer", "minimum": 1, "maximum": 300}}))
def outil_mensualite(principal: float, taux_annuel: float, n_mois: int) -> dict:
    return {"mensualite_aed": round(mensualite(principal, taux_annuel, n_mois), 2)}


@outil("estimer_prix", "Prix d'un bien : médiane des prix au sqft de comparables × surface, avec la fourchette Q1-Q3.",
       objet({"surface_sqft": {"type": "number", "exclusiveMinimum": 0},
              "comparables_aed_sqft": {"type": "array", "items": {"type": "number", "exclusiveMinimum": 0},
                                       "minItems": 3}}))
def outil_estimer_prix(surface_sqft: float, comparables_aed_sqft: list[float]) -> dict:
    mediane = statistics.median(comparables_aed_sqft)
    q1, _, q3 = statistics.quantiles(comparables_aed_sqft, n=4, method="inclusive")
    return {"mediane_aed_sqft": mediane, "prix_estime_aed": round(mediane * surface_sqft),
            "fourchette_aed": [round(q1 * surface_sqft), round(q3 * surface_sqft)]}


@outil("indemnite_sinistre", "Indemnité : min(plafond, max(0, dommage × (1 − vétusté) − franchise)), en AED.", objet({
    "dommage_aed": {"type": "number", "minimum": 0},
    "vetuste": {"type": "number", "minimum": 0, "maximum": 1},
    "franchise_aed": {"type": "number", "minimum": 0},
    "plafond_aed": {"type": "number", "exclusiveMinimum": 0}}))
def outil_indemnite(dommage_aed: float, vetuste: float, franchise_aed: float, plafond_aed: float) -> dict:
    return {"indemnite_aed": round(min(plafond_aed, max(0.0, dommage_aed * (1 - vetuste) - franchise_aed)), 2)}


@outil("gratuite_fin_de_service", "Indemnité de fin de service (décret-loi fédéral 33/2021, secteur privé), en AED.",
       objet({"salaire_base_mensuel": {"type": "number", "exclusiveMinimum": 0},
              "annees": {"type": "number", "minimum": 0, "maximum": 60}}))
def outil_gratuite(salaire_base_mensuel: float, annees: float) -> dict:
    return {"indemnite_aed": round(gratuite_fin_de_service(salaire_base_mensuel, annees), 2)}


@outil("tva", "TVA de 5 % et montant TTC, en AED.", objet({"montant_ht": {"type": "number", "minimum": 0}}))
def outil_tva(montant_ht: float) -> dict:
    return {"tva_aed": round(tva(montant_ht), 2), "ttc_aed": round(montant_ht + tva(montant_ht), 2)}


FACTURES_EMISES: list[dict] = []          # l'effet de bord observable : le « système de facturation » simulé
CLIENTS_CONNUS = {"CLI-0042", "CLI-0107"}


@outil("emettre_facture", "Émet une facture de sous-traitance (effet de bord : crée un document comptable).", objet({
    "reference_devis": {"type": "string", "pattern": "^DEV-[0-9]{5}$"},
    "client": {"type": "string", "pattern": "^CLI-[0-9]{4}$"},
    "montant_ht_aed": {"type": "number", "exclusiveMinimum": 0}}), effet_de_bord=True, portee="ecriture:facturation")
def outil_emettre_facture(reference_devis: str, client: str, montant_ht_aed: float) -> dict:
    if client not in CLIENTS_CONNUS:
        raise ValueError(f"client inconnu : {client}")
    numero = f"FAC-2026-{len(FACTURES_EMISES) + 1:05d}"
    FACTURES_EMISES.append({"numero": numero, "devis": reference_devis, "ht": montant_ht_aed})
    return {"numero": numero, "ttc_aed": round(montant_ht_aed * 1.05, 2)}


def main() -> None:
    rng = random.Random(2026)

    print("1. Le registre")
    for o in REGISTRE.values():
        print(f"  {o.nom:<24} portée={o.portee:<22} effet de bord={o.effet_de_bord}")
    api = definitions_api()
    assert len(REGISTRE) == 6 and [d["name"] for d in api][:2] == ["mensualite", "estimer_prix"]
    assert all(d["strict"] and not mots_cles_utilises(d["input_schema"]) & set(NON_PRIS_EN_CHARGE_STRICT) for d in api)

    print("2. Les outils EAU")
    r = appeler_outil("mensualite", {"principal": 1_000_000, "taux_annuel": 0.045, "n_mois": 300})
    assert r == {"ok": True, "resultat": {"mensualite_aed": 5558.32}, "tentatives": 1, "depuis_cache": False}
    comparables = [1850, 1900, 1920, 1980, 2050]
    r = appeler_outil("estimer_prix", {"surface_sqft": 1250, "comparables_aed_sqft": comparables})
    print(f"  estimer_prix : {r['resultat']}")
    assert r["resultat"] == {"mediane_aed_sqft": 1920, "prix_estime_aed": 2_400_000, "fourchette_aed": [2_375_000, 2_475_000]}
    for args, attendu in (((18_000, 0.2, 500, 50_000), 13_900), ((80_000, 0.1, 500, 50_000), 50_000),
                          ((400, 0.0, 500, 50_000), 0.0)):
        r = appeler_outil("indemnite_sinistre", dict(zip(("dommage_aed", "vetuste", "franchise_aed", "plafond_aed"), args)))
        print(f"  indemnite_sinistre{args} = {r['resultat']['indemnite_aed']}")
        assert r["resultat"]["indemnite_aed"] == attendu
    assert appeler_outil("gratuite_fin_de_service", {"salaire_base_mensuel": 10_000, "annees": 7})["resultat"] == {"indemnite_aed": 55_000}
    assert appeler_outil("tva", {"montant_ht": 12_000})["resultat"] == {"tva_aed": 600, "ttc_aed": 12_600}

    print("3. Ce qui n'est jamais exécuté")
    avant = REGISTRE["estimer_prix"].appels
    r = appeler_outil("estimer_prix", {"surface_sqft": 1250, "comparables_aed_sqft": [1900, 1920]})
    print(f"  {r['erreur']['type']} : {r['erreur']['details']}")
    assert r["erreur"]["type"] == "arguments_invalides" and REGISTRE["estimer_prix"].appels == avant
    assert appeler_outil("virement", {})["erreur"]["type"] == "outil_inconnu"
    facture = {"reference_devis": "DEV-00417", "client": "CLI-0042", "montant_ht_aed": 120_000}
    r = appeler_outil("emettre_facture", facture)                       # portée « lecture » seulement
    assert r["erreur"]["type"] == "non_autorise" and FACTURES_EMISES == []
    ecriture = frozenset({"lecture", "ecriture:facturation"})
    r = appeler_outil("emettre_facture", dict(facture, client="CLI-9999"), portees=ecriture)
    print(f"  {r['erreur']['type']} après {r['erreur']['tentatives']} tentative : {r['erreur']['message']}")
    assert r["erreur"]["type"] == "erreur_metier" and r["erreur"]["tentatives"] == 1 and FACTURES_EMISES == []
    assert set(r) == {"ok", "erreur"} and set(r["erreur"]) == {"type", "message", "outil", "tentatives", "details"}

    print("4. Timeout simulé et relances avec backoff")
    REGISTRE["estimer_prix"].latences, REGISTRE["estimer_prix"].appels = [3.0, 3.0, 0.4], 0
    CACHE.clear()
    debut, journal = HORLOGE.t, []
    r = appeler_outil("estimer_prix", {"surface_sqft": 1250, "comparables_aed_sqft": comparables}, rng=rng, journal=journal)
    for t, nom, tentative, motif in journal:
        print(f"  t = {t - debut:6.3f} s  tentative {tentative} : {motif}")
    duree = HORLOGE.t - debut
    print(f"  succès à la tentative {r['tentatives']}, durée simulée totale = {duree:.3f} s")
    assert r["ok"] and r["tentatives"] == 3 and 2 + 0.5 + 2 + 1.0 + 0.4 <= duree <= 2 + 1.0 + 2 + 1.5 + 0.4
    REGISTRE["estimer_prix"].latences, REGISTRE["estimer_prix"].appels = [3.0], 0
    CACHE.clear()
    debut = HORLOGE.t
    r = appeler_outil("estimer_prix", {"surface_sqft": 1250, "comparables_aed_sqft": comparables})   # sans jitter
    print(f"  {r['erreur']['type']} après {r['erreur']['tentatives']} tentatives, durée = {HORLOGE.t - debut} s = 4 × 2 + 0.5 × (2³ − 1)")
    assert r["erreur"]["type"] == "transitoire_epuise" and HORLOGE.t - debut == 4 * 2.0 + 0.5 * (2 ** 3 - 1)

    print("5. Idempotence : la même facture deux fois")
    r1 = appeler_outil("emettre_facture", facture, portees=ecriture)
    r2 = appeler_outil("emettre_facture", dict(reversed(list(facture.items()))), portees=ecriture)   # autre ordre
    print(f"  1er appel : {r1['resultat']} ; 2e : depuis_cache={r2['depuis_cache']} ; factures émises = {len(FACTURES_EMISES)}")
    assert r1["resultat"] == r2["resultat"] and r2["depuis_cache"] and len(FACTURES_EMISES) == 1
    r3 = appeler_outil("emettre_facture", dict(facture, reference_devis="DEV-00418"), portees=ecriture)
    assert r3["resultat"]["numero"] == "FAC-2026-00002" and len(FACTURES_EMISES) == 2
    cle = cle_idempotence("emettre_facture", facture)
    print(f"  clé = sha256(nom + JSON trié) = {cle[:16]}…")
    assert cle == hashlib.sha256(("emettre_facture" + json.dumps(facture, sort_keys=True)).encode()).hexdigest()

    print("6. Les délais de relance")
    for k in range(1, 6):                                  # attente cumulée sans plafond : base × (2^k − 1)
        assert sum(delai_backoff(n, 0.5, math.inf) for n in range(k)) == 0.5 * (2 ** k - 1)
    avec_plafond = [delai_backoff(n, 0.5, 4.0) for n in range(6)]
    print(f"  base 0.5, plafond 4 : {avec_plafond} → total {sum(avec_plafond)}")
    assert avec_plafond == [0.5, 1.0, 2.0, 4.0, 4.0, 4.0] and sum(avec_plafond) == 15.5
    tirages = [delai_backoff(3, 0.5, 8.0, rng, "complet") for _ in range(100_000)]
    moyenne = statistics.fmean(tirages)
    print(f"  jitter complet sur [0 ; 4] : moyenne de 100 000 tirages = {moyenne:.4f} (théorie : 4 / 2 = 2)")
    assert abs(moyenne - 2.0) < 0.02 and 0.0 <= min(tirages) and max(tirages) <= 4.0

    print("7. Disponibilité d'une chaîne d'outils en série")
    a = disponibilite_serie([0.99, 0.99, 0.99])
    avec_relance = disponibilite_serie([1 - 0.01 ** 2] * 3)        # une relance par outil (étape 11)
    print(f"  3 outils à 0.99 : {a:.6f} ; indisponibilité {1 - a:.4f} ≤ 0.03 ; avec une relance : {avec_relance:.6f}")
    assert round(a, 6) == 0.970299 and round(a, 4) == 0.9703 and 1 - a <= 0.03 and a <= 0.99
    assert round(avec_relance, 6) == 0.9997

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
2. Les outils EAU
  estimer_prix : {'mediane_aed_sqft': 1920, 'prix_estime_aed': 2400000, 'fourchette_aed': [2375000, 2475000]}
  indemnite_sinistre(18000, 0.2, 500, 50000) = 13900.0
…
3. Ce qui n'est jamais exécuté
  arguments_invalides : ['$.comparables_aed_sqft : 2 élément(s) < minItems 3']
  erreur_metier après 1 tentative : client inconnu : CLI-9999
4. Timeout simulé et relances avec backoff
  t =  2.000 s  tentative 1 : timeout après 2.0 s
  t =  4.560 s  tentative 2 : timeout après 2.0 s
  succès à la tentative 3, durée simulée totale = 6.211 s
  transitoire_epuise après 4 tentatives, durée = 11.5 s = 4 × 2 + 0.5 × (2³ − 1)
5. Idempotence : la même facture deux fois
  1er appel : {'numero': 'FAC-2026-00001', 'ttc_aed': 126000.0} ; 2e : depuis_cache=True ; factures émises = 1
…
  jitter complet sur [0 ; 4] : moyenne de 100 000 tirages = 1.9961 (théorie : 4 / 2 = 2)
7. Disponibilité d'une chaîne d'outils en série
  3 outils à 0.99 : 0.970299 ; indisponibilité 0.0297 ≤ 0.03 ; avec une relance : 0.999700
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un appel d'outil n'est pas un simple appel de fonction. Entre la demande du modèle et l'effet sur le monde, il y a six contrôles, et chacun se teste sans réseau ni horloge réelle.

## Formule naturelle : relances et disponibilité

Trois résultats chiffrent le comportement du registre. Le premier donne l'attente cumulée de k relances sans plafond :

$$
W_k = \sum_{n=0}^{k-1} b\,2^{n} = b\,(2^{k} - 1)
$$

Le deuxième donne l'attente moyenne d'un jitter complet, quand l'attente réelle est tirée uniformément entre 0 et le délai nominal :

$$
\mathbb{E}[w_n] = \frac{d_n}{2} \qquad \text{quand} \qquad w_n \sim \mathcal{U}[0\,;\,d_n]
$$

Le troisième donne la disponibilité d'une chaîne de m outils appelés en série :

$$
A_{chaine} = \prod_{i=1}^{m} A_i
$$

### Décryptage des symboles

$$
b
$$

Le délai de base avant la première relance, un réel strictement positif en secondes ; variable Python `base`.

$$
D_{\max}
$$

Le plafond d'un délai, un réel supérieur ou égal à b ; variable `plafond`.

$$
n
$$

L'indice de la relance, un entier positif ou nul qui vaut 0 pour la première relance ; dans le code, `n`, ou `tentative - 1` dans `appeler_outil`.

$$
d_n = \min(D_{\max},\; b\,2^{n})
$$

Le délai nominal de la relance n, un réel strictement positif ; variable `nominal` dans `delai_backoff`.

$$
w_n
$$

L'attente réellement observée avant la relance n, jitter compris, un réel positif ou nul ; c'est la valeur renvoyée par `delai_backoff`.

$$
k
$$

Le nombre de relances effectuées, un entier positif ou nul, au plus `relances_max`.

$$
W_k
$$

L'attente cumulée des k premières relances, un réel positif ou nul ; dans le programme, `sum(delai_backoff(n, ...) for n in range(k))`.

$$
t_{\max}
$$

Le timeout d'une tentative, un réel strictement positif en secondes ; variable `timeout`.

$$
R
$$

Le nombre maximal de relances, un entier positif ou nul, avec le même sens qu'à l'étape 11 ; variable `relances_max`.

$$
A_i
$$

La disponibilité de l'outil i, c'est-à-dire la probabilité qu'il réponde correctement à un instant pris au hasard, un réel dans [0 ; 1] ; un élément de la liste `dispos`.

$$
m
$$

Le nombre d'outils appelés en série, un entier supérieur ou égal à 1 ; dans le code, `len(dispos)`.

## Démonstration

### 1. L'attente cumulée sans plafond vaut b × (2ᵏ − 1)

Sans plafond, la relance n attend b × 2ⁿ. Posons S = 1 + 2 + 4 + … + 2ᵏ⁻¹. En multipliant par 2, on obtient 2S = 2 + 4 + … + 2ᵏ. En soustrayant terme à terme, tous les termes s'annulent, sauf le dernier de 2S et le premier de S :

$$
2S - S = 2^{k} - 1
\qquad\Longrightarrow\qquad
W_k = b\,S = b\,(2^{k} - 1)
$$

Avec b = 0,5 s, on obtient 0,5 ; 1,5 ; 3,5 ; 7,5 et 15,5 s pour k = 1 à 5, ce que le programme vérifie. La conséquence pratique est que **la dernière attente compte autant que toutes les précédentes réunies**, puisque b × 2ᵏ⁻¹ = Wₖ₋₁ + b : ajouter une relance ne rallonge pas l'attente d'un terme fixe, il la double à peu près.

Avec un plafond, les termes cessent de doubler dès qu'ils atteignent D_max. Si j termes restent strictement sous le plafond, l'attente cumulée devient :

$$
W_k = b\,(2^{j} - 1) + (k - j)\,D_{\max}
$$

Avec b = 0,5, D_max = 4 et k = 6, on a j = 3 (les attentes 0,5 ; 1 ; 2), puis trois attentes de 4, soit 0,5 × 7 + 3 × 4 = 15,5 s. Le plafond transforme une croissance exponentielle en croissance linéaire.

### 2. Le jitter complet attend en moyenne la moitié du délai

Si l'attente wₙ suit la loi uniforme sur [0 ; dₙ], sa densité vaut 1/dₙ sur cet intervalle, et son espérance se calcule par une intégrale :

$$
\mathbb{E}[w_n] = \int_{0}^{d_n} x\,\frac{1}{d_n}\,dx = \frac{1}{d_n}\cdot\frac{d_n^{2}}{2} = \frac{d_n}{2}
$$

Pour d₃ = 0,5 × 2³ = 4 s, l'attente moyenne vaut 2 s ; la moyenne de 100 000 tirages du programme, 1,9961, en est à moins de 0,004. Par linéarité de l'espérance, l'attente cumulée moyenne d'un jitter complet sans plafond vaut b × (2ᵏ − 1) / 2, la moitié du backoff sans jitter.

Avec le jitter additif du registre, l'attente vaut wₙ = dₙ + Jₙ, où Jₙ suit la loi uniforme sur [0 ; b] : son espérance vaut dₙ + b/2, et l'attente reste comprise entre dₙ et dₙ + b. C'est ce qui donne l'intervalle [5,9 ; 6,9] de la section 4 du programme.

L'intérêt du jitter n'est pas de raccourcir l'attente, mais de la **disperser**. Mille agents en échec au même instant, sans jitter, relanceraient tous après b, puis tous après 2b, en pics synchrones. Avec un jitter complet, les relances de rang n se répartissent uniformément sur [0 ; dₙ], et un intervalle de durée ε n'en reçoit en moyenne que 1 000 × ε / dₙ.

### 3. La pire durée d'un appel, pour le budget de latence

Un appel fait au plus R + 1 tentatives, chacune coupée au plus tard à t_max, et R attentes. Avec le jitter additif, chaque attente vaut au plus dₙ + b, donc :

$$
T_{pire} \le (R + 1)\,t_{\max} + b\,(2^{R} - 1) + R\,b
$$

Avec t_max = 2 s, R = 3 et b = 0,5 s, on obtient 8 + 3,5 + 1,5 = 13 s, et 11,5 s sans jitter, valeur que le programme retrouve exactement. Une boucle d'agent qui appelle trois outils successifs doit donc prévoir jusqu'à 39 s dans le pire cas : c'est ce chiffre, et non la latence moyenne, qui fixe le budget de temps d'un agent et le moment où il doit répondre « je reviens vers vous ».

### 4. La disponibilité d'une chaîne en série est le produit des disponibilités

Une chaîne d'outils appelés en série ne réussit que si **chaque** outil répond. Notons Bᵢ l'événement « l'outil i répond ». Si les pannes des outils sont indépendantes, la règle de multiplication démontrée à l'[étape 1](<../01-Agent/01-Agent-Definitions-Fondamentaux.md>) pour les étapes d'un agent s'applique telle quelle :

$$
P(B_1 \cap \dots \cap B_m) = \prod_{i=1}^{m} P(B_i) = \prod_{i=1}^{m} A_i
$$

Trois outils à 0,99 donnent 0,99³ = 0,9801 × 0,99 = 0,970299, soit 0,9703. Deux bornes restent vraies sans l'hypothèse d'indépendance, et servent à la vérifier. La première dit qu'une chaîne n'est jamais plus disponible que son maillon le plus faible, parce que chaque facteur du produit est au plus 1 :

$$
\prod_{i=1}^{m} A_i \le \min_i A_i
$$

La seconde dit que la chaîne tombe dès qu'un outil tombe, et que la probabilité d'une réunion d'événements est au plus la somme de leurs probabilités :

$$
1 - \prod_{i=1}^{m} A_i \le \sum_{i=1}^{m} (1 - A_i)
$$

Ici, 0,0297 ≤ 0,03. Si chaque outil est relancé une fois et que ses deux tentatives échouent indépendamment, sa probabilité de réussite devient 1 − 0,01² = 0,9999 (c'est la formule 1 − (1 − p)ᴿ⁺¹ démontrée à l'étape 11), et la chaîne atteint 0,9999³ = 0,9997. L'hypothèse d'indépendance est la plus fragile ici : une relance immédiate vers un service en panne échoue presque toujours avec lui, et c'est précisément pourquoi on attend, avec un délai croissant, avant de relancer. Les montages en parallèle et la disponibilité calculée sur la durée (MTBF, MTTR) sont traités à l'étape 49.

### 5. Pourquoi la clé d'idempotence reconnaît le même appel

`json.dumps(arguments, sort_keys=True)` écrit les champs dans l'ordre alphabétique : deux dictionnaires égaux, quel que soit l'ordre d'insertion de leurs clés, produisent la même chaîne, donc la même clé, ce que la section 5 du programme vérifie avec un dictionnaire inversé. Inversement, deux appels différents ont des chaînes différentes, et SHA-256 rend une collision accidentelle négligeable : sur N appels distincts, la probabilité d'au moins une collision est au plus de l'ordre de N² / 2²⁵⁷. La limite est sémantique, pas cryptographique : deux factures légitimes de même client et de même montant auraient la même clé si les arguments ne contenaient pas la référence du devis.

## Du symbole au code Python

Le programme complet de ce fichier, plus haut, construit le registre d'outils avant de présenter la formule des relances. Voici les fonctions de la formule isolées, juste après leur démonstration : l'attente cumulée sans plafond, le délai d'une relance avec plafond et jitter, et la disponibilité d'une chaîne d'outils en série.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`attente_cumulee(b, k)`** — Cette fonction est le comptable qui additionne toutes les minutes passées à attendre entre les relances : elle reçoit le délai de base b et le nombre k de relances, et renvoie la somme des attentes b × 2ⁿ pour n allant de 0 à k − 1, sans plafond ni jitter. Elle ne contrôle pas ses entrées. Pour b = 0,5 seconde et quatre relances, elle renvoie 7,5 secondes, que le premier `assert` compare à la formule fermée b × (2ᵏ − 1) démontrée plus haut, preuve que la dernière attente pèse autant que toutes les précédentes réunies.

**`delai_backoff(n, base, plafond, rng, jitter)`** — C'est la même fonction que dans le programme complet du registre : le standardiste qui espace ses rappels reçoit l'indice de la relance, la base, le plafond, un générateur facultatif et le mode de jitter, calcule le délai nominal, le plus petit entre le plafond et base × 2ⁿ, puis le renvoie tel quel, y ajoute un tirage dans [0 ; base] ou le remplace par un tirage dans [0 ; nominal], et lève `ValueError` pour un mode inconnu. Ici, elle donne la suite 0,5, 1, 2, 4 et 4 avec un plafond de 4, et, avec le jitter complet et la graine 1, une moyenne de 20 000 tirages à moins de 0,05 de 2 secondes.

**`disponibilite_serie(dispos)`** — Identique à celle du programme complet, cette fonction est l'ingénieur fiabilité qui multiplie entre elles les disponibilités des outils appelés à la suite, par `math.prod`, et renvoie la probabilité que toute la chaîne réponde quand les pannes sont indépendantes. Elle ne contrôle pas ses entrées. Le dernier `assert` de l'extrait l'applique à trois outils disponibles à 0,999, 0,995 et 0,99, et vérifie qu'elle renvoie bien leur produit, soit environ 98,4 % : une chaîne n'est jamais plus disponible que son maillon le plus faible.

```python
# [extrait] Étape 12 — attente cumulée, backoff exponentiel avec jitter, disponibilité en série.
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def attente_cumulee(b: float, k: int) -> float:
    """W_k = b + 2b + … + 2^(k−1) b = b × (2^k − 1), sans plafond."""
    return sum(b * 2 ** n for n in range(k))


def delai_backoff(n: int, base: float, plafond: float, rng: random.Random | None = None,
                  jitter: str = "additif") -> float:
    """Attente avant la relance n : min(plafond, base × 2^n), plus un jitter."""
    nominal = min(plafond, base * 2 ** n)
    if rng is None:
        return nominal
    if jitter == "additif":
        return nominal + rng.uniform(0.0, base)
    if jitter == "complet":
        return rng.uniform(0.0, nominal)
    raise ValueError("jitter : 'additif' ou 'complet'")


def disponibilite_serie(dispos: list[float]) -> float:
    """A_chaîne = A_1 × A_2 × … × A_m : la chaîne ne marche que si tous ses outils marchent."""
    return math.prod(dispos)


assert attente_cumulee(0.5, 4) == 0.5 * (2 ** 4 - 1) == 7.5
assert [delai_backoff(n, 0.5, 4.0) for n in range(5)] == [0.5, 1.0, 2.0, 4.0, 4.0]
rng = random.Random(1)
moyenne = sum(delai_backoff(3, 0.5, 4.0, rng, "complet") for _ in range(20_000)) / 20_000
assert abs(moyenne - 2.0) < 0.05
assert math.isclose(disponibilite_serie([0.999, 0.995, 0.99]), 0.999 * 0.995 * 0.99)
print("OK — toutes les vérifications sont passées.")
```

### Comment le code fonctionne

`attente_cumulee` additionne les délais d'une suite de relances sans plafond : la relance numéro n attend b × 2ⁿ, et la somme des k premières attentes vaut b × (2ᵏ − 1), ce que vérifie le premier `assert` avec b = 0,5 seconde et quatre relances (7,5 secondes). Cette somme explique pourquoi on plafonne : sans plafond, la dixième relance attendrait à elle seule plus de quatre minutes.

`delai_backoff` calcule d'abord le délai nominal, le plus petit entre le plafond et b × 2ⁿ, ce qui donne la suite 0,5 ; 1 ; 2 ; 4 ; 4 du deuxième `assert`. Sans générateur aléatoire, elle s'arrête là. Avec un générateur, elle ajoute du hasard pour que des milliers de clients qui échouent en même temps ne relancent pas tous à la même milliseconde : le jitter « additif » ajoute un tirage entre 0 et b au délai nominal, le jitter « complet » remplace le délai par un tirage entre 0 et le délai nominal. Le troisième `assert` vérifie le point 2 de la démonstration : avec le jitter complet, l'attente moyenne vaut la moitié du délai nominal, ici 2 secondes pour un délai de 4.

`disponibilite_serie` multiplie les disponibilités, exactement comme la fiabilité composée de l'étape 1 : une chaîne de trois outils disponibles à 99,9 %, 99,5 % et 99 % n'est disponible qu'à environ 98,4 %.

## Squelette algorithmique

L'algorithme central de ce fichier est l'appel d'un outil fiable : vérifier la portée et les arguments, servir une réponse déjà connue si la clé d'idempotence l'a déjà vue, sinon appeler avec un délai maximal, et relancer seulement les erreurs transitoires, avec un backoff plafonné et un jitter.

```text
ALGORITHME AppelerOutil
ENTRÉES : nom, arguments, portée de l'agent, clé d'idempotence, timeout, relances max K, base b, plafond D
SORTIE  : un résultat, ou une enveloppe d'erreur { type, message, outil, tentatives }

  outil ← registre[nom]                    SI absent ALORS RETOURNER erreur « outil inconnu »
  SI outil.portée n'est pas autorisée ALORS RETOURNER erreur « interdit »
  erreurs ← Valider(arguments, outil.schéma)      SI non vide ALORS RETOURNER erreur « arguments »
  SI outil a un effet de bord ET clé ∈ cache ALORS RETOURNER cache[clé]
  POUR n DE 0 À K FAIRE
      essayer
          résultat ← outil.fonction(arguments) en moins de timeout secondes
          SI outil a un effet de bord ALORS cache[clé] ← résultat
          RETOURNER résultat
      en cas d'erreur permanente : RETOURNER erreur « permanente » (pas de relance)
      en cas d'erreur transitoire ou de timeout :
          SI n = K ALORS RETOURNER erreur « transitoire, abandon »
          attendre min(D, b × 2ⁿ) + jitter
  FIN POUR
```

**Complexité.** Le temps est dominé par les appels : au plus K + 1 exécutions, chacune bornée par le timeout, plus des attentes dont la somme vaut au plus b × (2ᴷ − 1) sans plafond et au plus K × D avec plafond. La pire durée d'un appel est donc (K + 1) × timeout + Σ attentes (point 3 de la démonstration), qui sert au budget de latence. La vérification du schéma est linéaire en la taille des arguments, et la recherche dans le cache coûte O(1) en moyenne avec un dictionnaire. La mémoire du cache croît d'une entrée par appel à effet de bord distinct.

**Du squelette au code.** L'algorithme entier est la fonction `appeler_outil` : elle cherche l'outil dans `REGISTRE` (rempli par le décorateur `outil`), vérifie la portée avec son paramètre `portees`, valide les arguments avec `validate`, calcule la clé avec `cle_idempotence` et la cherche dans `CACHE`, puis exécute la boucle de relances. Les erreurs transitoires sont signalées par `ServiceIndisponible`, les durées d'appel sont simulées par `latence_suivante` et par la classe `Horloge` (aucune attente réelle), l'attente entre deux essais vient de `delai_backoff`, et toute sortie en erreur passe par l'enveloppe `erreur`.

## Cas d'usage réels aux Émirats

Les latences, timeouts, plafonds et volumes ci-dessous sont illustratifs ; les règles citées (TVA de 5 %, fin de service du décret-loi fédéral 33/2021, frais DLD de 4 %) sont celles du parcours, à confirmer avec le texte en vigueur.

### Banque — un outil de calcul derrière un cœur bancaire lent

Une banque de détail de Dubaï expose à son agent de crédit l'outil `mensualite`, qui calcule localement, et un outil de lecture des encours existants, qui interroge le système central de la banque et répond en général en 300 ms, mais parfois en plusieurs secondes en fin de mois. Le registre coupe ce second appel à 2 s et le relance au plus trois fois, avec des attentes de 0,5, 1 et 2 s plus un jitter, si bien qu'un appel ne bloque jamais l'agent plus de 13 s (démonstration, point 3). Une fois les encours lus, `mensualite` donne 5 558,32 AED pour 1 000 000 AED à 4,5 % sur 300 mois, et l'agent peut calculer l'endettement total que la CBUAE plafonne à 50 %. Sans timeout, un pic de charge du système central figerait toutes les conversations en cours ; sans relances espacées, les agents relanceraient tous en même temps et prolongeraient eux-mêmes la saturation. Les deux outils n'ont que la portée `lecture` : l'agent de pré-instruction ne peut rien écrire dans le système de la banque, quelle que soit la question posée. On suit le p95 de la durée d'appel et le taux d'enveloppes `transitoire_epuise`.

### Immobilier — une estimation à partir de comparables

Une agence de Dubaï et d'Abu Dhabi donne à son agent l'outil `estimer_prix`, alimenté par une liste de transactions comparables extraites des enregistrements de la DLD. Pour un appartement de 1 250 sqft et cinq comparables à 1 850, 1 900, 1 920, 1 980 et 2 050 AED/sqft, l'outil renvoie la médiane, 1 920 AED/sqft, un prix estimé de 2 400 000 AED et la fourchette interquartile [2 375 000 ; 2 475 000] ; l'agent ajoute à part les frais de transfert de 4 %, soit 96 000 AED. Le schéma exige au moins trois comparables : avec deux seulement, l'appel est refusé avant exécution et l'agent répond qu'il manque des données au lieu d'inventer un prix. La médiane est un choix délibéré : un comparable mal saisi à 19 200 AED/sqft déplacerait la moyenne de plus de 3 000 AED/sqft, mais ne changerait pas la médiane de cinq valeurs dont il occupe l'extrémité. Sans cet outil, le modèle donnerait un prix « plausible » tiré de sa mémoire, invérifiable et daté. On suit l'écart relatif entre estimation et prix de vente enregistré, et la part des appels refusés faute de comparables.

### Crypto — lire la liquidité sans saturer le fournisseur

Une plateforme d'actifs virtuels agréée par la VARA fait lire par ses agents de surveillance l'état des pools de liquidité auprès d'un fournisseur de données qui limite le nombre de requêtes par seconde. Lors d'un pic de volatilité, des dizaines d'agents reçoivent en même temps une erreur de dépassement de quota, une erreur transitoire que le registre relance. Sans jitter, ils relanceraient tous ensemble 0,5 s après l'échec, puis de nouveau ensemble 1 s après le deuxième échec, et ainsi de suite, en vagues synchrones qui dépassent à nouveau le quota ; avec le jitter complet, les relances de rang n se répartissent sur [0 ; dₙ] et le fournisseur reçoit un débit régulier (démonstration, point 2). Les outils de lecture sont sans effet de bord et peuvent être relancés librement, mais leur cache doit expirer vite : un état de pool vieux de dix minutes est une information fausse dans un marché qui bouge. La plateforme doit pouvoir montrer à la VARA que ses alertes reposent sur des données fraîches, et l'enveloppe journalise le nombre de tentatives de chaque lecture. On suit le taux de lectures en erreur après relances et l'âge moyen des données utilisées par les alertes.

### Assurance — une indemnité calculée par un outil, pas par le modèle

Un assureur auto et santé donne à son agent de gestion des sinistres l'outil `indemnite_sinistre`, qui applique la formule du contrat : min(plafond, max(0, dommage × (1 − vétusté) − franchise)). Pour un dommage de 18 000 AED, une vétusté de 20 % et une franchise de 500 AED, l'outil renvoie 13 900 AED ; pour 80 000 AED à 10 % de vétusté, il renvoie le plafond du contrat, 50 000 AED ; pour un dommage de 400 AED, il renvoie 0, parce que la franchise l'absorbe. Le schéma refuse une vétusté de 1,5 ou une franchise négative, valeurs qu'un modèle peut produire en lisant mal un document. Sans outil, le modèle ferait le calcul « de tête » et se tromperait tôt ou tard d'un ordre de grandeur ou de l'ordre des opérations, sans qu'aucune trace ne permette de le vérifier. L'assurance étant supervisée par la CBUAE, chaque calcul d'indemnité est journalisé avec ses arguments et son résultat, que l'on peut rejouer à l'identique. On suit l'écart entre les indemnités proposées par l'agent et celles validées par les gestionnaires.

### RH — l'indemnité de fin de service, au prorata

Un cabinet RH multi-émirats fait répondre par un agent aux questions des salariés de ses clients sur leurs droits de fin de contrat. L'outil `gratuite_fin_de_service` applique le décret-loi fédéral 33/2021 pour le secteur privé : 21 jours de salaire de base par an pour les cinq premières années, 30 jours au-delà, au prorata, avec un plafond de 24 mois de salaire et aucun droit avant un an de service. Pour 10 000 AED de base et sept ans, il renvoie 55 000 AED ; pour 3,5 ans, 24 500 AED ; pour huit mois, 0. Le schéma accepte des années décimales, parce que le calcul se fait au prorata, mais refuse une durée négative. L'outil ne s'applique ni aux salariés émiriens, qui relèvent du régime de retraite des nationaux, ni aux salariés du DIFC, qui relèvent du régime d'épargne DEWS : la fiche validée à l'étape 9 indique le régime, et l'agent n'appelle l'outil que pour le régime de gratuité. On suit le taux de réponses dont le montant est confirmé par le service paie, avec un objectif de 100 %.

### BTP — une facture émise une seule fois, même après un timeout

Un groupe de construction qui mène de grands chantiers à Dubaï laisse un agent émettre les factures de situation à partir des devis acceptés, avec l'outil `emettre_facture`, qui crée un document comptable et porte la portée `ecriture:facturation`. Un jour de forte charge, le système comptable crée la facture mais répond après le timeout ; l'agent relance. Sans clé d'idempotence, la relance crée une seconde facture de 126 000 AED TTC, le client la reçoit en double, et l'annulation demande un avoir et une correction de la déclaration de TVA auprès de l'autorité fiscale fédérale. Avec la clé, calculée sur l'outil et ses arguments, qui contiennent la référence du devis `DEV-00417`, la relance renvoie le résultat déjà stocké, et le compteur de factures reste à 1 ; un devis différent, `DEV-00418`, produit bien une seconde facture. La simulation de ce fichier ne couvre que le cas où le timeout survient avant l'effet de bord ; en production, la clé doit aussi être transmise au système comptable, qui la vérifie de son côté. On suit le nombre de doublons détectés au rapprochement comptable, avec un objectif de zéro.

### Secteur public — des portées liées à l'usager

Une entité de services publics en ligne permet à l'usager, connecté par UAE Pass, de faire préparer une demande administrative par un agent bilingue arabe-anglais. L'outil qui dépose la demande a un effet de bord et exige la portée d'écriture que seule la session de l'usager accorde ; un agent qui ne dispose que de la portée de lecture peut consulter l'état d'un dossier, mais pas en déposer un, quelle que soit la formulation de la conversation. Le jeton de session reste dans le code qui exécute l'outil : il n'apparaît jamais dans le prompt, si bien qu'une injection de prompt ne peut ni le lire ni le réutiliser. L'enveloppe d'erreur `non_autorise` est renvoyée au modèle, qui explique à l'usager ce qu'il doit confirmer, au lieu d'échouer en silence. La minimisation des données s'applique aussi aux arguments : le schéma de l'outil n'accepte que les champs nécessaires à la démarche. On suit le nombre d'appels refusés pour portée manquante, dont une hausse soudaine signale une tentative de détournement ou un défaut du prompt.

## Pièges et limites

- **Le timeout n'annule rien.** Dans la simulation, un appel coupé n'a pas exécuté la fonction ; dans la réalité, le service a peut-être créé la facture avant de répondre trop tard. Un outil à effet de bord ne se relance qu'avec une clé d'idempotence transmise au service et vérifiée par lui.
- **Relancer une erreur permanente.** Des arguments invalides ou un client inconnu échoueront à l'identique : les relancer multiplie la latence et le coût par R + 1 sans aucune chance de succès. Seules les erreurs transitoires se relancent.
- **Un cache sans durée de vie.** La clé d'idempotence est parfaite pour une facture, dangereuse pour une donnée qui change : un prix de pool ou un statut de dossier mis en cache sans expiration devient faux. On donne une durée de vie au cache des outils de lecture.
- **Des relances empilées.** Si le client HTTP relance déjà (beaucoup de SDK relancent 2 fois par défaut), si le registre relance 3 fois et si la boucle d'agent relance l'étape, le nombre réel de tentatives se multiplie : 3 × 4 × 2 = 24 appels pour une seule demande. On fixe les relances à un seul niveau.
- **Une description qui ment.** Le modèle croit la description : si elle annonce des AED alors que l'outil répond en USD, toutes les réponses seront fausses d'un facteur 3,6725. La description fait partie du contrat et se teste comme le code.

### Exercice feuille blanche

1. Sans regarder le code, écrire le décorateur `outil(nom, description, schema)` et une version minimale d'`appeler_outil` qui fait seulement : outil inconnu, validation, exécution, enveloppe d'erreur. La tester sur `tva` avec `{"montant_ht": -5}`.
2. Prédire, puis vérifier : avec `base = 1`, `plafond = 10` et 5 relances sans jitter, quelle est l'attente cumulée ? (Réponse : 1 + 2 + 4 + 8 + 10 = 25 s ; la formule sans plafond donnerait 2⁵ − 1 = 31 s.)
3. Trouver le bug : une variante calcule la clé par `hashlib.sha256((nom + str(arguments)).encode())`. Pourquoi deux appels identiques peuvent-ils alors produire deux factures ? (Indice : `str` d'un dictionnaire suit l'ordre d'insertion des clés.)

## Pour aller plus loin

Le motif du **disjoncteur** (circuit breaker) complète les relances : après un nombre d'échecs consécutifs, on cesse d'appeler l'outil pendant une durée donnée et l'on renvoie immédiatement une erreur, ce qui protège à la fois le service et le budget de latence de l'agent. Le jitter « décorrélé », où chaque attente est tirée entre b et trois fois l'attente précédente, est une autre variante courante. Le protocole MCP (étapes 46 à 49) standardise la découverte et l'appel des outils entre un agent et des serveurs distants ; le registre de ce fichier en est la version locale.

> Suite : [Six agents EAU de bout en bout](<13-Agent-Exemples-Cas-Usage.md>) — étape 13.
