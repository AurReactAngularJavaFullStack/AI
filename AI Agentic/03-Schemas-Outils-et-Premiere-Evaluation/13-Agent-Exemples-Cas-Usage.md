# Étape 13 — Agent — Exemples et cas d'usage

> Étape 13 du parcours · Prérequis : [Le registre d'outils](<12-Outils-Definitions-Fondamentaux.md>) · Suite : [Évaluer un agent : définitions](<13b-Evaluation-Definitions-Fondamentaux.md>)

**Dossier :** 03-Schemas-Outils-et-Premiere-Evaluation  
**Métiers :** AI Engineers, Product Engineers, Forward-Deployed Engineers

Ce fichier termine le bloc « forme, outil, boucle ». L'étape 1 a écrit la boucle d'agent, l'étape 8 le contrat des données, l'étape 12 les outils ; ici, on fait tourner la même boucle sur six métiers des Émirats, avec des traces chiffrées que le programme vérifie, puis on écrit les deux autres façons d'organiser un agent, Plan-and-Execute et Reflexion, sur le même port LLM. On termine en branchant le vrai modèle à la place du faux, sans toucher à la boucle. L'ancienne version de ce fichier listait six agents en une ligne chacun, sans une seule trace ; son en-tête indiquait aussi un dossier « 04-Agents », alors que le dossier s'appelle `04-Agent`.

## Le moteur commun

Les six agents utilisent `executer_agent`, la boucle canonique du parcours, recopiée telle quelle de l'étape 1. À chaque étape, elle envoie l'historique au modèle ; si la réponse contient des blocs `tool_use`, elle exécute chaque outil demandé, renvoie **tous** les résultats dans un seul message `user`, et recommence. Elle s'arrête avec l'un de cinq statuts : `fini` (réponse finale), `refus`, `tronque`, `boucle` (la même action deux fois de suite) ou `max_etapes`. Une exception levée par un outil ne fait pas planter la boucle : elle repart vers le modèle dans un `tool_result` marqué `is_error`, et le modèle peut corriger sa demande.

Les outils sont les fonctions de l'étape 12, recopiées, plus trois nouvelles : `ratio_endettement`, `zscore_liquidite` et `retenue_garantie`. Pour garder ce fichier centré sur la boucle, ils sont appelés directement, sans le registre de l'étape 12 ; en production, chaque entrée du dictionnaire `OUTILS` passerait par `appeler_outil` (validation, portées, timeout, idempotence), et `executer_agent` ne changerait pas d'une ligne. Le tableau suivant résume, pour chaque cas, les outils appelés dans l'ordre, la règle de décision et son seuil, la métrique suivie en production et le garde-fou.

| Cas | Outils appelés, dans l'ordre | Règle de décision et seuil | Métrique suivie | Garde-fou |
|---|---|---|---|---|
| Banque | `mensualite`, puis `ratio_endettement` | endettement total ≤ 50 % (CBUAE) | part des dossiers recevables confirmés par l'analyste | aucune décision de crédit sans les deux calculs |
| Immobilier | `estimer_prix` deux fois, en parallèle | prix = médiane × surface, fourchette Q1-Q3 | écart relatif estimation / prix de vente | au moins 3 comparables |
| Crypto | `zscore_liquidite` | alerte si la valeur absolue de z dépasse 3 | délai de prise en charge des alertes | série de référence non constante |
| Assurance | `indemnite_sinistre` (deux fois : erreur, puis correction) | indemnité plafonnée au contrat | écart avec l'indemnité validée par le gestionnaire | l'erreur d'outil repart vers le modèle |
| RH | `gratuite_fin_de_service` | décret-loi fédéral 33/2021, régime de gratuité | réponses confirmées par la paie | régime vérifié à l'étape 9 avant l'appel |
| BTP | `tva`, puis `retenue_garantie` | TTC = HT × 1,05 ; retenue illustrative de 10 % du HT | factures payées sans correction | montants calculés en code, jamais par le modèle |

## Cas d'usage réels aux Émirats

Les montants, séries et taux de retenue sont illustratifs ; les règles citées (plafond d'endettement de la CBUAE, TVA de 5 %, fin de service du décret-loi fédéral 33/2021) sont celles du parcours, à confirmer avec le texte en vigueur. Dans le programme, le faux modèle joue un scénario écrit à l'avance : il montre ce que la boucle fait de chaque réponse, pas ce qu'un vrai modèle déciderait.

### Banque — une demande d'hypothèque instruite en trois étapes

Une banque de détail de Dubaï laisse son agent pré-instruire les demandes de crédit immobilier avant qu'un analyste ne les reprenne. Le client demande 1 000 000 AED sur 25 ans ; il gagne 40 000 AED par mois et rembourse déjà 6 000 AED de crédits. À l'étape 1, le modèle appelle `mensualite` avec un taux de 4,5 % sur 300 mois, et l'outil renvoie 5 558,32 AED ; à l'étape 2, il appelle `ratio_endettement` avec les mensualités existantes, la nouvelle et le revenu, et l'outil renvoie un ratio de 0,289 et le verdict « recevable » ; à l'étape 3, le modèle rédige la réponse : endettement total de 28,9 %, sous le plafond de 50 % de la CBUAE. La boucle s'arrête avec le statut `fini` après trois étapes, et la trace garde les deux appels avec leurs arguments, ce qui permet à l'analyste de refaire le calcul. Sans outils, le modèle aurait estimé la mensualité de tête et pu oublier les crédits en cours, exactement l'erreur que le plafond « total » interdit. Le garde-fou est structurel : la réponse finale ne cite que des nombres produits par les outils. On suit la part des dossiers jugés recevables par l'agent puis confirmés par l'analyste.

### Immobilier — deux estimations demandées dans la même réponse

Une agence de Dubaï et d'Abu Dhabi demande à son agent d'estimer deux appartements de Dubai Marina, de 1 250 et 900 sqft, à partir des mêmes cinq transactions comparables (1 850, 1 900, 1 920, 1 980 et 2 050 AED/sqft). Le modèle émet deux blocs `tool_use` dans une seule réponse ; la boucle exécute les deux appels et renvoie les deux `tool_result` dans un seul message `user`, ce que le programme vérifie en enregistrant les messages reçus par le modèle. La médiane vaut 1 920 AED/sqft : 2 400 000 AED pour le premier bien, avec la fourchette interquartile [2 375 000 ; 2 475 000], et 1 728 000 AED pour le second. La fourchette Q1-Q3 dit au vendeur ce qui est plausible au lieu d'un chiffre unique faussement précis ; les frais de transfert de la DLD, 4 % de la valeur, s'y ajoutent. Si les résultats étaient renvoyés en deux messages séparés, le modèle apprendrait à ne plus demander d'appels parallèles, et chaque estimation coûterait un aller-retour de plus. On suit l'écart relatif entre estimation et prix de vente enregistré, avec le critère de 10 % de l'étape 65.

### Crypto — une alerte de liquidité par z-score

Une plateforme d'actifs virtuels agréée par la VARA surveille la liquidité de ses pools heure par heure. La série des dix dernières heures, en millions d'AED, va de 11,8 à 12,4, avec une moyenne de 12,1 et un écart-type de 0,18257 ; la nouvelle mesure vaut 11,5. L'agent appelle `zscore_liquidite`, qui renvoie z = −3,29, au-delà du seuil de 3 en valeur absolue, et donc une alerte ; une mesure à 11,8 aurait donné z = −1,64 et aucune alerte. Le z-score rapporte l'écart à la variabilité habituelle : une baisse de 0,6 M AED est banale sur un pool qui varie de 2 M AED par heure, alarmante sur un pool qui ne varie que de 0,2 M AED. Le seuil de 3 a une justification (démonstration, point 1), mais une série de dix points est courte, et son écart-type est lui-même incertain : l'alerte déclenche une vérification humaine, pas une action automatique sur le pool. La plateforme doit pouvoir montrer à la VARA comment ses alertes sont produites, et la trace de l'appel en fait foi. On suit le délai de prise en charge des alertes et la part d'alertes confirmées.

### Assurance — une erreur d'outil que le modèle corrige

Un assureur auto et santé laisse son agent proposer l'indemnité d'un accrochage à Sharjah, chiffré à 18 000 AED par le garage, avec une vétusté de 20 % et une franchise de 500 AED. Au premier appel, le modèle oublie l'argument `plafond_aed` : Python lève `TypeError`, la boucle l'attrape et renvoie au modèle un `tool_result` marqué `is_error` qui nomme l'argument manquant. Au deuxième appel, le modèle ajoute le plafond du contrat, 50 000 AED, et l'outil renvoie 18 000 × 0,8 − 500 = 13 900 AED ; la réponse finale arrive à la troisième étape. Le programme montre aussi le danger inverse : avec une vétusté écrite 20 au lieu de 0,2, la fonction seule renvoie 0 sans erreur, parce que `max(0, …)` absorbe le résultat négatif ; seul le schéma de l'étape 12, qui borne la vétusté à [0 ; 1], arrête cette valeur. C'est pourquoi, en production, les outils passent par le registre et ne sont jamais appelés nus. L'assurance étant supervisée par la CBUAE, chaque proposition d'indemnité est journalisée avec sa trace. On suit l'écart entre les indemnités proposées et celles validées par les gestionnaires.

### RH — l'indemnité de fin de service

Un cabinet RH multi-émirats laisse un agent répondre aux salariés de ses clients sur leurs droits de fin de contrat. Pour un salaire de base de 10 000 AED et sept ans d'ancienneté dans le secteur privé, l'agent appelle `gratuite_fin_de_service`, qui applique 21 jours de salaire de base par an pour les cinq premières années et 30 jours au-delà, avec un salaire journalier de 10 000 / 30 : 35 000 + 20 000 = 55 000 AED. La réponse cite le détail du calcul, ce qui permet au salarié et au service paie de le vérifier. Avant l'appel, la fiche validée à l'étape 9 a établi que le salarié relève bien du régime de gratuité, et non du régime de retraite des nationaux ou du régime d'épargne DEWS du DIFC. Sans outil, un modèle répond volontiers « environ 49 000 AED » en appliquant 21 jours à toutes les années : c'est l'erreur que la variante Reflexion de ce fichier rattrape. La paie passe ensuite par le WPS, sous le contrôle du MOHRE. On suit la part des réponses dont le montant est confirmé par le service paie, avec un objectif de 100 %.

### BTP — une situation de travaux, sa TVA et sa retenue de garantie

Un groupe de construction qui mène de grands chantiers à Dubaï laisse un agent préparer le paiement des situations de travaux de ses sous-traitants. Pour une situation de 120 000 AED HT, l'agent appelle d'abord `tva`, qui renvoie 6 000 AED de TVA et 126 000 AED TTC, puis `retenue_garantie` avec un taux de 10 % du HT, taux illustratif fixé par le contrat de sous-traitance : la retenue vaut 12 000 AED et le net à payer 114 000 AED. La retenue de garantie protège le maître d'ouvrage contre les malfaçons ; elle est libérée à la réception des travaux, selon le contrat, et son assiette comme son traitement en TVA sont à confirmer avec le contrat et le texte en vigueur. L'ordre des appels compte : la retenue s'applique à des montants que le modèle n'a pas calculés lui-même, mais qu'il a reçus d'un outil. Sans ces outils, une erreur de 5 % sur la TVA ou sur la retenue se propagerait à toute la chaîne de paiement et aux déclarations auprès de l'autorité fiscale fédérale. On suit le taux de situations payées sans correction.

## Trois façons d'organiser la boucle

**ReAct** (raisonner, puis agir) est la boucle canonique : le modèle choisit une action à la fois, voit son résultat et décide de la suivante. Elle s'adapte à l'imprévu, comme l'argument oublié de l'assurance, mais elle coûte un appel au modèle par étape.

**Plan-and-Execute** demande d'abord un plan complet, une liste JSON d'étapes, puis l'exécute en code, sans repasser par le modèle, et ne le rappelle qu'une fois pour rédiger la synthèse. Une étape peut utiliser le résultat d'une étape précédente grâce à une référence : `"@1.mensualite_aed"` désigne le champ `mensualite_aed` du résultat de l'étape 1. Le plan se relit et se valide avant toute action, et il coûte deux appels au modèle quel que soit le nombre d'étapes ; en contrepartie, si un outil échoue ou si une donnée manque, l'exécutant ne sait pas improviser, et il faut redemander un plan.

**Reflexion** ajoute une boucle autour de l'agent : on le fait agir, un évaluateur juge le résultat, et en cas d'échec un critique écrit une **leçon** que l'essai suivant lit dans son prompt système. L'évaluateur doit être fiable et, autant que possible, déterministe : ici, il vérifie que la réponse a bien été calculée par l'outil et cite le bon montant. La mémoire des leçons est courte et ciblée ; elle ne remplace pas un meilleur outil.

| Organisation | Appels au modèle pour k étapes d'outils | Ce qu'elle fait bien | Ce qui la casse |
|---|---|---|---|
| ReAct | k + 1 | s'adapter à chaque résultat | le coût et la latence quand k grandit |
| Plan-and-Execute | 2 | un plan vérifiable, un coût fixe | un résultat imprévu au milieu du plan |
| Reflexion | jusqu'à E × (k + 1) + (E − 1) pour E essais | apprendre d'un échec détecté | un évaluateur qui se trompe |

## Démonstration

### 1. Le z-score et le seuil de 3

Le z-score d'une nouvelle mesure x rapporte son écart à la moyenne x̄ de la série de référence à l'écart-type s de cette série, calculé avec n − 1 au dénominateur :

$$
z = \frac{x - \bar{x}}{s} \qquad \text{avec} \qquad s = \sqrt{\frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})^{2}}
$$

Sur la série du programme, la somme des dix valeurs vaut 121,0, donc x̄ = 12,1. Les écarts à la moyenne valent 0 ; 0,3 ; −0,2 ; 0,1 ; −0,1 ; 0,2 ; 0 ; −0,3 ; 0,1 ; −0,1, leurs carrés totalisent 0,30, et s = √(0,30 / 9) = √0,0333 = 0,18257. Pour x = 11,5 : z = −0,6 / 0,18257 = −3,29.

Pourquoi 3 ? Sans aucune hypothèse sur la loi des mesures, l'inégalité de Bienaymé-Tchebychev borne la probabilité d'un écart d'au moins k écarts-types, pour une variable de moyenne μ et d'écart-type σ :

$$
P\big(\lvert X - \mu \rvert \ge k\,\sigma\big) \le \frac{1}{k^{2}}
$$

Elle se démontre en une ligne. L'événement « l'écart vaut au moins kσ » est l'événement « (X − μ)² ≥ k²σ² », et pour une variable positive Y et un seuil a > 0, on a a × 𝟙(Y ≥ a) ≤ Y ; en prenant l'espérance, a × P(Y ≥ a) ≤ E[Y], c'est-à-dire l'inégalité de Markov. Avec Y = (X − μ)², a = k²σ² et E[Y] = σ², on obtient la borne 1/k². Pour k = 3, elle vaut 1/9, soit 11 % au plus ; si les mesures suivent une loi normale, la probabilité réelle tombe à 0,27 %. Un dépassement de 3 est donc rare sous le fonctionnement habituel, ce qui en fait un bon déclencheur d'alerte. Deux réserves : μ et σ sont ici estimés sur dix points seulement, et une série constante a un écart-type nul, pour lequel le z-score n'est pas défini (l'outil lève alors `ValueError` au lieu de diviser par zéro).

### 2. Combien d'appels au modèle coûte chaque organisation

En ReAct, chaque étape d'outil commence par un appel au modèle, et la réponse finale en demande un de plus : k étapes coûtent k + 1 appels. Le cas bancaire a deux étapes d'outils, donc trois appels, ce que vérifie `r["etapes"] == 3`. En Plan-and-Execute, le nombre d'appels ne dépend pas de k : un pour le plan, un pour la synthèse, ce que vérifie `llm.appels == 2`. En Reflexion, chaque essai est une exécution ReAct complète, et chaque échec ajoute un appel au critique : pour E essais, au plus E × (k + 1) + (E − 1) appels. Dans le cas RH, le premier essai coûte 1 appel (réponse sans outil), la leçon 1, le second essai 2 : 4 appels au total. La fiabilité suit la même logique : une chaîne de k étapes indépendantes de fiabilité p réussit avec la probabilité pᵏ (étape 1), ce qui pousse à réduire le nombre d'étapes où le modèle peut se tromper.

### 3. Le net à payer d'une situation de travaux

Avec un montant HT noté H, un taux de TVA de 5 % et un taux de retenue t appliqué au HT, le net à payer vaut :

$$
\text{Net} = H \times 1{,}05 - t \times H = H\,(1{,}05 - t)
$$

Pour H = 120 000 AED et t = 0,10 : 120 000 × 0,95 = 114 000 AED, ce que donnent bien les deux outils successifs (126 000 − 12 000). La factorisation montre que le net est proportionnel au HT : une erreur de 1 % sur le HT se retrouve à l'identique sur le net, quel que soit t.

### 4. Pourquoi la boucle ne change pas avec le vrai modèle

`executer_agent` ne lit que sept attributs : `stop_reason` et `content` sur la réponse, `type`, `text`, `id`, `name` et `input` sur les blocs. Tout objet qui les fournit convient : c'est le typage structurel, le même principe qu'un port dans une architecture hexagonale, où le domaine dépend d'une interface et non d'une implémentation. La section 10 du programme le vérifie en faisant tourner la boucle, sans modification, sur des réponses fabriquées avec `SimpleNamespace`, qui imitent les objets du SDK au lieu des classes `Bloc` et `Reponse`. L'adaptateur Claude ci-dessous fournit ces mêmes attributs, puisque ce sont ceux des réponses de l'API.

## Le programme

### Déroulé, ligne par ligne

**Le port et la boucle** (`Bloc`, `Reponse`, `texte`, `appel_outil`, `FakeLLM`, `executer_agent`) sont recopiés tels quels du code canonique ; leur déroulé détaillé est à l'étape 1.

**Les fonctions canoniques** `mensualite`, `ratio_endettement`, `gratuite_fin_de_service` et `tva`, et **les outils de l'étape 12** (`outil_mensualite`, `outil_estimer_prix`, `outil_indemnite`, `outil_gratuite`, `outil_tva`) sont recopiés sans changement.

**Les trois nouveaux outils.**

- `outil_ratio(existantes, nouvelle, revenu)` appelle `ratio_endettement` et arrondit le ratio à quatre décimales : (6 000 + 5 558,32) / 40 000 = 0,288958, arrondi à 0,289.
- `outil_zscore(serie, derniere, seuil=3.0)` refuse une série de moins de deux points ou constante, calcule `statistics.stdev` (écart-type à n − 1) et `statistics.fmean`, puis z. Le résultat est arrondi à deux décimales : −3,29.
- `outil_retenue(montant_ht, ttc, taux_retenue)` refuse un taux hors de [0 ; 1[, calcule la retenue sur le HT et la retranche du TTC.

**`OUTILS`** associe chaque nom public, celui que le modèle écrit, à sa fonction. C'est l'argument `outils` d'`executer_agent`.

**`plan_and_execute(llm, system, question, outils)`**.

- Le premier appel au modèle renvoie le plan sous forme de texte JSON, lu par `json.loads`.
- Pour chaque étape, la boucle intérieure remplace toute valeur qui commence par `@` : `"@1.mensualite_aed"` est découpé en `k = "1"` et `champ = "mensualite_aed"`, puis remplacé par `resultats[0]["mensualite_aed"]`, soit 5 558,32.
- Les outils s'exécutent en code, dans l'ordre du plan, sans repasser par le modèle.
- Le second appel reçoit la question et les résultats, et rédige la synthèse.

**`reflexion(acteur, critique, system, question, outils, evaluer, essais_max=2)`**.

- À chaque essai, le prompt système reçoit les leçons accumulées, puis `executer_agent` fait agir l'acteur.
- `evaluer(resultat)` renvoie un couple : le succès et un diagnostic. S'il y a succès, la fonction s'arrête.
- Sinon, le critique lit le diagnostic et écrit une leçon, ajoutée à `lecons`.
- Dans le cas RH, le premier essai répond « 49 000 AED » sans appeler l'outil ; l'évaluateur, qui cherche un appel à `gratuite_fin_de_service` dans la trace, échoue ; la leçon dit d'appeler l'outil ; le second essai l'appelle, obtient 55 000 AED et le cite, et l'évaluateur, qui formate 55000 en « 55 000 », le retrouve dans la réponse.

**`LLMEnregistreur`** enveloppe n'importe quel modèle au même port et garde une copie de chaque liste de messages reçue. C'est un adaptateur au sens hexagonal : la boucle ne voit aucune différence.

**`main()`**, section par section.

1. Banque : trois réponses scriptées, deux appels d'outils, statut `fini` en trois étapes, mensualité et ratio vérifiés.
2. Immobilier : deux blocs `tool_use` dans une même réponse ; `llm.recus[-1][-1]` est le dernier message reçu par le modèle au second appel, un message `user` qui contient les deux `tool_result`, dans l'ordre des demandes.
3. Crypto : z = −3,29 et alerte ; la mesure 11,8 donne −1,64 et pas d'alerte ; la moyenne 12,1 et l'écart-type 0,18257 de la démonstration sont vérifiés.
4. Assurance : le premier appel échoue avec `TypeError`, dont le message nomme `plafond_aed` ; le second rend 13 900 AED ; enfin, la vétusté 20 donne 0 en silence quand l'outil est appelé sans le registre.
5. RH : 55 000 AED.
6. BTP : 6 000 et 126 000 AED, puis 12 000 et 114 000 AED.
7. Un refus arrête la boucle ; la même action deux fois de suite aussi, avec le statut `boucle`.
8. Plan-and-Execute retrouve les résultats du cas bancaire avec deux appels au modèle.
9. Reflexion réussit au second essai, avec une leçon.
10. La boucle tourne sans modification sur des objets `SimpleNamespace` à la forme des réponses du SDK.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`texte(t)`** — C'est la même fonction que dans le programme de l'étape 1 : le copiste reçoit une chaîne et la range dans un `Bloc` de type `"text"`, sans rien vérifier, puis renvoie ce bloc. Dans ce fichier, elle écrit toutes les répliques finales des six agents, comme « Mensualité 5 558,32 AED ; endettement total 28,9 % ≤ 50 % : dossier recevable. », mais aussi le plan JSON de Plan-and-Execute et la leçon que rédige le critique de Reflexion.

**`appel_outil(nom, arguments, id_)`** — Même fonction que dans le programme de l'étape 1 : elle rédige le bon de commande du modèle et renvoie un `Bloc` de type `"tool_use"` qui porte le nom public de l'outil, le dictionnaire de ses arguments et l'identifiant de la demande. Les scripts de `main` l'utilisent à chaque tour d'outil, par exemple pour les deux demandes `estimer_prix` d'identifiants `"i1"` et `"i2"` réunies dans une même réponse, dont la boucle doit renvoyer les résultats dans le même ordre.

**`FakeLLM.__init__(script)`** — Le constructeur est identique à celui de l'étape 1 : comme un souffleur qui reçoit son cahier de répliques, il garde une copie de la liste des réponses prévues et met le compteur d'appels à zéro, sans rien renvoyer. Ici, on en crée pour chacun des six agents, pour l'acteur et le critique de Reflexion, et même pour un script fait d'objets `SimpleNamespace` à la forme des réponses du SDK, que le faux modèle restitue sans les distinguer de ses propres `Reponse`.

**`FakeLLM.create(system, messages, tools)`** — Même méthode que dans le programme de l'étape 1 : elle reçoit en arguments nommés le prompt système, l'historique et les outils, n'en lit aucun, renvoie la réponse suivante du script en incrémentant son compteur, et lève `RuntimeError` si le script est épuisé. Le compteur `appels` sert dans la section 8 à prouver que Plan-and-Execute ne consulte le modèle que deux fois, alors que la boucle ReAct du cas bancaire en avait eu besoin de trois.

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — C'est la boucle canonique de l'étape 1, recopiée à l'identique : le chef de chantier appelle le modèle, recopie sa réponse, sort sur `refus`, `tronque`, `boucle` ou `max_etapes`, exécute chaque outil demandé en renvoyant toute exception au modèle dans un `tool_result` marqué `is_error`, range tous les résultats d'un tour dans un seul message et renvoie un dictionnaire avec le statut, la trace, le nombre d'étapes et, pour `fini`, la réponse. Ce fichier la fait tourner sur six domaines, puis l'emploie comme exécutant de Reflexion, et montre qu'elle accepte sans modification des réponses à la forme du SDK.

**`mensualite(principal, taux_annuel, n_mois)`** — C'est le calculateur du banquier, commun à tout le parcours : il reçoit le capital, le taux annuel et la durée, lève `ValueError` si le capital ou la durée ne sont pas positifs ou si le taux est négatif, et renvoie P r / (1 − (1 + r)⁻ⁿ) avec le taux mensuel r, ou P / n à taux nul. Pour l'hypothèque de 1 000 000 AED à 4,5 % sur 300 mois, il donne 5 558,32 AED à moins d'un demi-fils près, ce que vérifie le dernier `assert` de `main`.

**`ratio_endettement(mensualites_existantes, nouvelle_mensualite, revenu_mensuel, plafond)`** — Cette fonction commune est l'analyste qui pèse toutes les charges du client contre son revenu : elle reçoit les mensualités en cours, la nouvelle, le revenu et un plafond, 0,50 par défaut, lève `ValueError` si le revenu n'est pas positif, et renvoie le couple formé du ratio et du booléen de conformité. Elle travaille ici pour l'outil `ratio_endettement` : avec 6 000 AED de dettes, 5 558,32 AED de nouvelle mensualité et 40 000 AED de revenu, le ratio vaut 0,288958 et respecte le plafond.

**`gratuite_fin_de_service(salaire_base_mensuel, annees)`** — Cette fonction commune est le gestionnaire de paie du décret-loi fédéral 33/2021 : elle reçoit le salaire de base et l'ancienneté, renvoie 0 sous un an, compte 21 jours par an pour les cinq premières années et 30 jours au-delà, au prorata, avec un salaire journalier égal au trentième du salaire de base, et plafonne à 24 mois de salaire de base. Elle renvoie 55 000 AED pour 10 000 AED et 7 ans, le montant que l'agent RH puis le second essai de Reflexion doivent citer.

**`tva(montant_ht, taux)`** — Même fonction commune que dans les programmes précédents : le percepteur sobre renvoie le produit d'un montant hors taxes par un taux, 0,05 par défaut, sans arrondi ni contrôle. Ici, c'est l'outil `tva` de l'agent de facturation qui l'appelle deux fois, pour la taxe et pour le total : sur une situation de travaux de 120 000 AED hors taxes, il obtient 6 000 AED de TVA et 126 000 AED TTC, avant que la retenue de garantie soit déduite.

**`outil_mensualite(principal, taux_annuel, n_mois)`** — Reprise de l'étape 12, cette fonction est le guichet de crédit de l'agent, publié sous le nom `mensualite` dans le dictionnaire `OUTILS` : elle appelle la fonction canonique et renvoie `{"mensualite_aed": ...}` arrondi au fils. Ici, il n'y a plus de registre ni de schéma devant elle, si bien qu'une `ValueError` de la fonction canonique remonterait jusqu'à la boucle, qui la renverrait au modèle. Pour 1 000 000 AED à 4,5 % sur 300 mois, elle renvoie 5 558,32 AED, dans le cas bancaire comme dans Plan-and-Execute.

**`outil_estimer_prix(surface_sqft, comparables_aed_sqft)`** — Reprise de l'étape 12 et publiée sous le nom `estimer_prix`, cette fonction est l'expert immobilier qui estime un bien d'après ses voisins : elle prend la médiane des prix au sqft, la multiplie par la surface et calcule la fourchette à partir des quartiles inclusifs, puis renvoie médiane, prix et fourchette arrondis. Sur les comparables 1 850, 1 900, 1 920, 1 980 et 2 050, elle estime 2 400 000 AED pour 1 250 sqft, avec une fourchette de 2 375 000 à 2 475 000 AED, et 1 728 000 AED pour 900 sqft.

**`outil_indemnite(dommage_aed, vetuste, franchise_aed, plafond_aed)`** — Reprise de l'étape 12 et publiée sous le nom `indemnite_sinistre`, cette fonction est l'expert d'assurance de l'agent : elle applique la vétusté au dommage, retranche la franchise, ramène à 0 un résultat négatif, plafonne et renvoie l'indemnité arrondie. Sans le registre de l'étape 12, rien ne vérifie ses arguments : un appel sans `plafond_aed` lève une `TypeError` que la boucle renvoie au modèle, qui corrige et obtient 13 900 AED, mais une vétusté de 20 au lieu de 0,2 donne 0 en silence.

**`outil_gratuite(salaire_base_mensuel, annees)`** — Reprise de l'étape 12 et publiée sous le nom `gratuite_fin_de_service`, cette fonction est le guichet RH de l'agent : elle appelle la fonction canonique du décret-loi 33/2021 et renvoie `{"indemnite_aed": ...}` arrondi au centième, sans autre contrôle. Pour 10 000 AED de salaire de base et 7 ans de service, elle renvoie 55 000 AED, et c'est la présence de son appel dans la trace que cherche l'évaluateur de Reflexion pour juger qu'un essai a vraiment calculé au lieu de deviner.

**`outil_tva(montant_ht)`** — Reprise de l'étape 12 et publiée sous le nom `tva`, cette fonction est la caisse enregistreuse de l'agent de facturation : elle calcule la TVA de 5 % avec la fonction canonique et renvoie la taxe et le total TTC, arrondis au centième. Pour 120 000 AED hors taxes, elle renvoie 6 000 AED et 126 000 AED. Dans la section 7, c'est aussi elle que le faux modèle demande deux fois de suite avec 100 AED, ce qui déclenche l'arrêt `boucle` après un seul calcul réellement exécuté.

**`outil_ratio(existantes, nouvelle, revenu)`** — Ce premier nouvel outil, publié sous le nom `ratio_endettement`, est le conseiller qui rend un avis lisible au lieu d'un couple brut : il reçoit les mensualités en cours, la nouvelle mensualité et le revenu, appelle `ratio_endettement` avec le plafond de 50 % et renvoie un dictionnaire avec le ratio arrondi à quatre décimales et le booléen `recevable`. Une `ValueError` sur un revenu nul remonterait telle quelle. Avec 6 000, 5 558,32 et 40 000 AED, il renvoie un ratio de 0,289 et un dossier recevable.

**`outil_zscore(serie, derniere, seuil)`** — Ce deuxième nouvel outil, publié sous le nom `zscore_liquidite`, est la vigie qui mesure à quel point la dernière observation s'écarte de l'habitude : il reçoit une série de référence, la dernière mesure et un seuil, 3 par défaut, lève `ValueError` si la série a moins de deux points ou si elle est constante, calcule la moyenne et l'écart-type à n − 1, puis z = (x − moyenne) / écart-type. Il renvoie z arrondi à deux décimales et une alerte si |z| dépasse le seuil : sur les dix heures de liquidité, de moyenne 12,1 et d'écart-type 0,18257, la mesure 11,5 donne −3,29 et une alerte, la mesure 11,8 donne −1,64 et aucune.

**`outil_retenue(montant_ht, ttc, taux_retenue)`** — Ce troisième nouvel outil, publié sous le nom `retenue_garantie`, est le maître d'ouvrage qui garde une part du paiement jusqu'à la réception des travaux : il reçoit le hors taxes, le TTC et le taux de retenue, lève `ValueError` si ce taux sort de [0 ; 1[, calcule la retenue sur le hors taxes, arrondie au centième, et la retranche du TTC. Il renvoie la retenue et le net à payer : pour 120 000 AED hors taxes, 126 000 AED TTC et un taux illustratif de 10 %, la retenue vaut 12 000 AED et le net 114 000 AED.

**`plan_and_execute(llm, system, question, outils)`** — C'est l'architecte qui dessine tout le plan avant que le premier ouvrier ne prenne ses outils : la fonction reçoit un modèle, un prompt système, une question et le dictionnaire des outils, demande d'abord au modèle un plan JSON qu'elle lit avec `json.loads`, puis exécute chaque étape en code, dans l'ordre, en remplaçant toute valeur de la forme `@k.champ` par le champ du résultat de l'étape k. Elle rappelle enfin le modèle avec la question et les résultats pour la synthèse, et renvoie le plan, les résultats, la réponse et deux appels au modèle ; un plan illisible lèverait une erreur de décodage. Sur le cas bancaire, elle retrouve la mensualité de 5 558,32 AED et le ratio de 0,289.

**`reflexion(acteur, critique, system, question, outils, evaluer, essais_max)`** — Cette fonction met en scène un élève et son professeur : elle reçoit le modèle acteur, le modèle critique, le prompt système, la question, les outils, une fonction d'évaluation et un nombre d'essais, 2 par défaut. À chaque essai, elle ajoute au prompt les leçons déjà écrites, fait agir l'acteur avec `executer_agent`, puis soumet le résultat à `evaluer` ; en cas de succès, elle renvoie le statut « reussi », le nombre d'essais, les leçons et la réponse, sinon elle confie le diagnostic au critique et range sa leçon. Après le dernier échec, elle renvoie « echec » sans réponse ; dans le cas RH, elle réussit au second essai, avec une seule leçon.

**`LLMEnregistreur.__init__(llm)`** — Le constructeur de cet adaptateur installe un greffier entre la boucle et le modèle : il reçoit n'importe quel objet qui respecte le port, ici un `FakeLLM`, le garde dans `self.llm` et ouvre une liste vide `recus`, qui recevra une copie de chaque historique transmis. Il ne renvoie rien. Comme il expose la même méthode `create` que le modèle qu'il enveloppe, la boucle ne voit aucune différence : c'est un adaptateur au sens de l'architecture hexagonale.

**`LLMEnregistreur.create(system, messages, tools)`** — Cette méthode note avant de transmettre, comme un greffier qui photocopie chaque pièce avant de la passer au juge : elle reçoit les mêmes arguments nommés que tout modèle du port, ajoute à `recus` une copie de la liste des messages telle qu'elle est à cet instant, puis délègue l'appel au modèle enveloppé et renvoie sa réponse. Dans la section 2, le dernier message reçu au second appel est un message `user` qui contient les deux `tool_result`, d'identifiants `"i1"` puis `"i2"`, dans l'ordre des demandes.

**`afficher(titre, resultat)`** — Cette petite fonction est le rapporteur qui résume chaque cas pour le lecteur : elle reçoit un titre et le dictionnaire renvoyé par `executer_agent`, imprime le titre, puis une ligne par entrée de la trace avec le nom de l'outil, ses arguments en JSON et sa sortie, et enfin le statut, le nombre d'étapes et la réponse finale entre crochets. Elle ne renvoie rien et ne vérifie rien ; c'est elle qui produit les lignes de la sortie attendue, comme le refus de l'outil d'indemnité auquel manque `plafond_aed`.

**`main()`** — C'est le metteur en scène des dix tableaux du chapitre : il fait tourner les six agents, crédit, immobilier avec deux appels parallèles, liquidité crypto, sinistre auto avec un argument oublié puis corrigé, fin de service RH et facturation BTP avec retenue de garantie, en vérifiant chaque sortie d'outil par un `assert`. Il éprouve ensuite les arrêts `refus` et `boucle`, montre que Plan-and-Execute retrouve les résultats bancaires en deux appels au modèle, que Reflexion réussit au second essai grâce à une leçon, et que la même boucle tourne sur des réponses à la forme du SDK, avant d'imprimer la ligne finale.

**`evaluer(res)`** — Cette fonction interne, définie à l'intérieur de `main` pour le cas Reflexion, est l'examinateur qui vérifie que la copie a été calculée et non devinée : elle reçoit le résultat d'un essai, cherche dans sa trace les sorties de l'outil `gratuite_fin_de_service` et, s'il n'y en a aucune, renvoie un échec avec le diagnostic « donnée sans appeler l'outil de calcul ». Sinon, elle écrit le montant calculé avec une espace pour les milliers, « 55 000 », et renvoie un succès seulement si ce texte figure dans la réponse, accompagné du diagnostic « montant attendu 55 000 AED ».

```python
"""Étape 13 — six agents EAU sur la boucle ReAct canonique, puis Plan-and-Execute et Reflexion sur le même port."""
import json
import math
import statistics
import sys
from dataclasses import dataclass, field
from types import SimpleNamespace

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
def mensualite(principal: float, taux_annuel: float, n_mois: int) -> float:
    """M = P r / (1 - (1 + r)^-n), r = taux mensuel ; M = P / n si le taux est nul."""
    if principal <= 0 or n_mois <= 0 or taux_annuel < 0:
        raise ValueError("principal > 0, n_mois > 0, taux >= 0")
    r = taux_annuel / 12
    return principal / n_mois if r == 0 else principal * r / (1 - (1 + r) ** -n_mois)


def ratio_endettement(mensualites_existantes: float, nouvelle_mensualite: float, revenu_mensuel: float,
                      plafond: float = 0.50) -> tuple[float, bool]:
    """Ratio d'endettement CBUAE : TOUTES les mensualités (existantes + nouvelle) / revenu ; plafond 50 % (30 % retraité)."""
    if revenu_mensuel <= 0:
        raise ValueError("revenu > 0")
    ratio = (mensualites_existantes + nouvelle_mensualite) / revenu_mensuel
    return ratio, ratio <= plafond


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


# ---------------------------------------------------------------- outils de l'étape 12 (fonctions recopiées) + trois nouveaux
def outil_mensualite(principal: float, taux_annuel: float, n_mois: int) -> dict:
    return {"mensualite_aed": round(mensualite(principal, taux_annuel, n_mois), 2)}


def outil_estimer_prix(surface_sqft: float, comparables_aed_sqft: list[float]) -> dict:
    mediane = statistics.median(comparables_aed_sqft)
    q1, _, q3 = statistics.quantiles(comparables_aed_sqft, n=4, method="inclusive")
    return {"mediane_aed_sqft": mediane, "prix_estime_aed": round(mediane * surface_sqft),
            "fourchette_aed": [round(q1 * surface_sqft), round(q3 * surface_sqft)]}


def outil_indemnite(dommage_aed: float, vetuste: float, franchise_aed: float, plafond_aed: float) -> dict:
    return {"indemnite_aed": round(min(plafond_aed, max(0.0, dommage_aed * (1 - vetuste) - franchise_aed)), 2)}


def outil_gratuite(salaire_base_mensuel: float, annees: float) -> dict:
    return {"indemnite_aed": round(gratuite_fin_de_service(salaire_base_mensuel, annees), 2)}


def outil_tva(montant_ht: float) -> dict:
    return {"tva_aed": round(tva(montant_ht), 2), "ttc_aed": round(montant_ht + tva(montant_ht), 2)}


def outil_ratio(existantes: float, nouvelle: float, revenu: float) -> dict:
    ratio, recevable = ratio_endettement(existantes, nouvelle, revenu)
    return {"ratio": round(ratio, 4), "recevable": recevable}


def outil_zscore(serie: list[float], derniere: float, seuil: float = 3.0) -> dict:
    """z = (x − moyenne) / écart-type de la série de référence ; alerte si |z| > seuil."""
    if len(serie) < 2:
        raise ValueError("il faut au moins 2 points de référence")
    ecart = statistics.stdev(serie)
    if ecart == 0:
        raise ValueError("série constante : le z-score n'est pas défini")
    z = (derniere - statistics.fmean(serie)) / ecart
    return {"z": round(z, 2), "alerte": abs(z) > seuil}


def outil_retenue(montant_ht: float, ttc: float, taux_retenue: float) -> dict:
    """Retenue de garantie calculée sur le HT (taux et assiette illustratifs), déduite du TTC à payer."""
    if not 0 <= taux_retenue < 1:
        raise ValueError("taux de retenue dans [0 ; 1[")
    retenue = round(montant_ht * taux_retenue, 2)
    return {"retenue_aed": retenue, "net_a_payer_aed": round(ttc - retenue, 2)}


OUTILS = {"mensualite": outil_mensualite, "ratio_endettement": outil_ratio, "estimer_prix": outil_estimer_prix,
          "indemnite_sinistre": outil_indemnite, "gratuite_fin_de_service": outil_gratuite, "tva": outil_tva,
          "zscore_liquidite": outil_zscore, "retenue_garantie": outil_retenue}


# ---------------------------------------------------------------- variantes sur le même port
def plan_and_execute(llm, system: str, question: str, outils: dict) -> dict:
    """1 appel pour le plan (JSON), exécution en code, 1 appel pour la synthèse. « @k.champ » = champ du résultat k."""
    plan = json.loads(llm.create(system=system + " Réponds par un plan JSON.", messages=[
        {"role": "user", "content": question}], tools=[]).content[0].text)
    resultats = []
    for etape in plan:
        args = {}
        for cle, valeur in etape["arguments"].items():
            if isinstance(valeur, str) and valeur.startswith("@"):
                k, champ = valeur[1:].split(".")
                valeur = resultats[int(k) - 1][champ]          # référence à une étape déjà exécutée
            args[cle] = valeur
        resultats.append(outils[etape["outil"]](**args))
    synthese = llm.create(system=system, messages=[{"role": "user", "content": question + "\nRésultats : "
                          + json.dumps(resultats, ensure_ascii=False)}], tools=[])
    return {"plan": plan, "resultats": resultats, "reponse": synthese.content[0].text, "appels_llm": 2}


def reflexion(acteur, critique, system: str, question: str, outils: dict, evaluer, essais_max: int = 2) -> dict:
    """Agir, évaluer, et en cas d'échec écrire une leçon que l'essai suivant lit dans son prompt système."""
    lecons = []
    for essai in range(1, essais_max + 1):
        prompt = system if not lecons else system + "\nLeçons des essais précédents :\n" + "\n".join(lecons)
        resultat = executer_agent(acteur, prompt, question, outils, [])
        reussi, diagnostic = evaluer(resultat)
        if reussi:
            return {"statut": "reussi", "essais": essai, "lecons": lecons, "reponse": resultat.get("reponse")}
        retour = critique.create(system="Analyse l'échec et écris une leçon courte.",
                                 messages=[{"role": "user", "content": diagnostic}], tools=[])
        lecons.append(retour.content[0].text)
    return {"statut": "echec", "essais": essais_max, "lecons": lecons, "reponse": None}


class LLMEnregistreur:
    """Enveloppe n'importe quel LLM au même port et garde une copie des messages reçus."""

    def __init__(self, llm):
        self.llm, self.recus = llm, []

    def create(self, *, system: str, messages: list, tools: list):
        self.recus.append(list(messages))
        return self.llm.create(system=system, messages=messages, tools=tools)


def afficher(titre: str, resultat: dict) -> None:
    print(titre)
    for nom, args, sortie in resultat["trace"]:
        print(f"  outil {nom}({json.dumps(args, ensure_ascii=False)}) -> {sortie}")
    print(f"  [{resultat['statut']}, {resultat['etapes']} étapes] {resultat.get('reponse', '')}")


def main() -> None:
    T = "tool_use"

    # 1. Banque : mensualité puis endettement total.
    r = executer_agent(FakeLLM([
        Reponse(T, [appel_outil("mensualite", {"principal": 1_000_000, "taux_annuel": 0.045, "n_mois": 300}, "b1")]),
        Reponse(T, [appel_outil("ratio_endettement", {"existantes": 6000, "nouvelle": 5558.32, "revenu": 40000}, "b2")]),
        Reponse("end_turn", [texte("Mensualité 5 558,32 AED ; endettement total 28,9 % ≤ 50 % : dossier recevable.")]),
    ]), "Agent crédit", "Hypothèque de 1 000 000 AED sur 25 ans, revenu 40 000 AED, 6 000 AED de crédits en cours ?",
        OUTILS, [])
    afficher("1. Banque — demande de crédit", r)
    assert r["statut"] == "fini" and r["etapes"] == 3
    assert r["trace"][0][2] == {"mensualite_aed": 5558.32} and r["trace"][1][2] == {"ratio": 0.289, "recevable": True}

    # 2. Immobilier : deux estimations demandées dans la même réponse (appels parallèles).
    comparables = [1850, 1900, 1920, 1980, 2050]
    llm = LLMEnregistreur(FakeLLM([
        Reponse(T, [appel_outil("estimer_prix", {"surface_sqft": 1250, "comparables_aed_sqft": comparables}, "i1"),
                    appel_outil("estimer_prix", {"surface_sqft": 900, "comparables_aed_sqft": comparables}, "i2")]),
        Reponse("end_turn", [texte("1 250 sqft : 2 400 000 AED [2 375 000 ; 2 475 000] ; 900 sqft : 1 728 000 AED.")]),
    ]))
    r = executer_agent(llm, "Agent immobilier", "Estimer deux appartements à Dubai Marina.", OUTILS, [])
    afficher("2. Immobilier — deux estimations en parallèle", r)
    assert r["trace"][0][2] == {"mediane_aed_sqft": 1920, "prix_estime_aed": 2_400_000, "fourchette_aed": [2_375_000, 2_475_000]}
    assert r["trace"][1][2]["prix_estime_aed"] == 1_728_000 and r["etapes"] == 2
    dernier = llm.recus[-1][-1]                                   # le message user reçu au 2e appel
    assert dernier["role"] == "user" and [x["tool_use_id"] for x in dernier["content"]] == ["i1", "i2"]

    # 3. Crypto : z-score de la liquidité d'un pool, en millions d'AED, sur les 10 dernières heures.
    serie = [12.1, 12.4, 11.9, 12.2, 12.0, 12.3, 12.1, 11.8, 12.2, 12.0]
    r = executer_agent(FakeLLM([
        Reponse(T, [appel_outil("zscore_liquidite", {"serie": serie, "derniere": 11.5}, "c1")]),
        Reponse("end_turn", [texte("Alerte : liquidité à 11,5 M AED, z = −3,29 : astreinte prévenue.")]),
    ]), "Agent surveillance", "Liquidité du pool ETH/AED ?", OUTILS, [])
    afficher("3. Crypto — liquidité d'un pool", r)
    assert r["trace"][0][2] == {"z": -3.29, "alerte": True}
    assert outil_zscore(serie, 11.8) == {"z": -1.64, "alerte": False}
    assert statistics.fmean(serie) == 12.1 and round(statistics.stdev(serie), 5) == 0.18257

    # 4. Assurance : un argument oublié, l'erreur repart vers le modèle, qui corrige.
    args = {"dommage_aed": 18_000, "vetuste": 0.2, "franchise_aed": 500}
    r = executer_agent(FakeLLM([
        Reponse(T, [appel_outil("indemnite_sinistre", args, "a1")]),
        Reponse(T, [appel_outil("indemnite_sinistre", dict(args, plafond_aed=50_000), "a2")]),
        Reponse("end_turn", [texte("Indemnité proposée : 13 900 AED (dommage 18 000, vétusté 20 %, franchise 500).")]),
    ]), "Agent sinistres", "Accrochage à Sharjah, devis du garage 18 000 AED.", OUTILS, [])
    afficher("4. Assurance — indemnité", r)
    assert r["trace"][0][2].startswith("ERREUR") and "plafond_aed" in r["trace"][0][2]
    assert r["trace"][1][2] == {"indemnite_aed": 13_900} and r["statut"] == "fini"
    assert outil_indemnite(18_000, 20, 500, 50_000) == {"indemnite_aed": 0.0}   # vétusté 20 au lieu de 0.2 : 0 en silence

    # 5. RH : fin de service.
    r = executer_agent(FakeLLM([
        Reponse(T, [appel_outil("gratuite_fin_de_service", {"salaire_base_mensuel": 10_000, "annees": 7}, "h1")]),
        Reponse("end_turn", [texte("Indemnité de fin de service : 55 000 AED (5 × 21 + 2 × 30 jours de salaire de base).")]),
    ]), "Agent RH", "Salaire de base 10 000 AED, 7 ans d'ancienneté : combien en fin de contrat ?", OUTILS, [])
    afficher("5. RH — fin de service", r)
    assert r["trace"][0][2] == {"indemnite_aed": 55_000}

    # 6. BTP : TVA, puis retenue de garantie de 10 % du HT (taux illustratif).
    r = executer_agent(FakeLLM([
        Reponse(T, [appel_outil("tva", {"montant_ht": 120_000}, "t1")]),
        Reponse(T, [appel_outil("retenue_garantie", {"montant_ht": 120_000, "ttc": 126_000, "taux_retenue": 0.10}, "t2")]),
        Reponse("end_turn", [texte("TTC 126 000 AED, retenue 12 000 AED, net à payer 114 000 AED.")]),
    ]), "Agent facturation", "Situation de travaux de 120 000 AED HT.", OUTILS, [])
    afficher("6. BTP — facture et retenue de garantie", r)
    assert r["trace"][0][2] == {"tva_aed": 6000, "ttc_aed": 126_000}
    assert r["trace"][1][2] == {"retenue_aed": 12_000, "net_a_payer_aed": 114_000}

    print("7. Les arrêts : refus et boucle")
    assert executer_agent(FakeLLM([Reponse("refusal", [])]), "s", "q", OUTILS, [])["statut"] == "refus"
    meme = appel_outil("tva", {"montant_ht": 100}, "x")
    r = executer_agent(FakeLLM([Reponse(T, [meme]), Reponse(T, [meme])]), "s", "q", OUTILS, [])
    print(f"  refus → refus ; même appel deux fois → {r['statut']} après {r['etapes']} étapes")
    assert r["statut"] == "boucle" and len(r["trace"]) == 1

    print("8. Plan-and-Execute : le plan d'abord, deux appels au modèle au lieu de trois")
    plan = [{"outil": "mensualite", "arguments": {"principal": 1_000_000, "taux_annuel": 0.045, "n_mois": 300}},
            {"outil": "ratio_endettement", "arguments": {"existantes": 6000, "nouvelle": "@1.mensualite_aed", "revenu": 40000}}]
    llm = FakeLLM([Reponse("end_turn", [texte(json.dumps(plan))]),
                   Reponse("end_turn", [texte("Endettement 28,9 % : recevable.")])])
    r = plan_and_execute(llm, "Agent crédit", "Hypothèque de 1 000 000 AED ?", OUTILS)
    print(f"  résultats = {r['resultats']} ; appels au modèle = {llm.appels}")
    assert r["resultats"] == [{"mensualite_aed": 5558.32}, {"ratio": 0.289, "recevable": True}] and llm.appels == 2

    print("9. Reflexion : un premier essai faux, une leçon, un second essai juste")
    acteur = FakeLLM([
        Reponse("end_turn", [texte("Environ 49 000 AED (21 jours par an).")]),             # essai 1 : sans outil
        Reponse(T, [appel_outil("gratuite_fin_de_service", {"salaire_base_mensuel": 10_000, "annees": 7}, "r1")]),
        Reponse("end_turn", [texte("55 000 AED, calculés par l'outil.")]),
    ])
    critique = FakeLLM([Reponse("end_turn", [texte("Toujours appeler gratuite_fin_de_service : 30 jours par an après 5 ans.")])])

    def evaluer(res: dict) -> tuple[bool, str]:
        calculs = [s for nom, _, s in res["trace"] if nom == "gratuite_fin_de_service"]
        if not calculs:
            return False, f"réponse « {res.get('reponse', '')} » donnée sans appeler l'outil de calcul"
        montant = f"{calculs[0]['indemnite_aed']:,.0f}".replace(",", " ")
        return montant in res.get("reponse", ""), f"montant attendu {montant} AED"

    r = reflexion(acteur, critique, "Agent RH", "10 000 AED de base, 7 ans ?", OUTILS, evaluer)
    print(f"  {r['statut']} en {r['essais']} essais ; leçon : {r['lecons'][0]}")
    assert r["statut"] == "reussi" and r["essais"] == 2 and len(r["lecons"]) == 1 and "55 000" in r["reponse"]

    print("10. Le même executer_agent sur des réponses à la forme du SDK")
    sdk = [SimpleNamespace(stop_reason="tool_use", content=[SimpleNamespace(
               type="tool_use", id="toolu_01", name="mensualite",
               input={"principal": 1_000_000, "taux_annuel": 0.045, "n_mois": 300})]),
           SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text="5 558,32 AED.")])]
    r = executer_agent(FakeLLM(sdk), "Agent crédit", "Mensualité ?", OUTILS, [])
    print(f"  {r['statut']} : {r['trace'][0][2]} — la boucle ne lit que stop_reason, content, type, text, id, name, input")
    assert r["statut"] == "fini" and r["trace"][0][2] == {"mensualite_aed": 5558.32}
    assert math.isclose(mensualite(1_000_000, 0.045, 300), 5558.32, abs_tol=0.005)

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Banque — demande de crédit
  outil mensualite({"principal": 1000000, "taux_annuel": 0.045, "n_mois": 300}) -> {'mensualite_aed': 5558.32}
  outil ratio_endettement({"existantes": 6000, "nouvelle": 5558.32, "revenu": 40000}) -> {'ratio': 0.289, 'recevable': True}
  [fini, 3 étapes] Mensualité 5 558,32 AED ; endettement total 28,9 % ≤ 50 % : dossier recevable.
…
3. Crypto — liquidité d'un pool
  outil zscore_liquidite({"serie": [12.1, 12.4, 11.9, 12.2, 12.0, 12.3, 12.1, 11.8, 12.2, 12.0], "derniere": 11.5}) -> {'z': -3.29, 'alerte': True}
…
4. Assurance — indemnité
  outil indemnite_sinistre({"dommage_aed": 18000, "vetuste": 0.2, "franchise_aed": 500}) -> ERREUR outil_indemnite() missing 1 required positional argument: 'plafond_aed'
  outil indemnite_sinistre({"dommage_aed": 18000, "vetuste": 0.2, "franchise_aed": 500, "plafond_aed": 50000}) -> {'indemnite_aed': 13900.0}
…
  outil gratuite_fin_de_service({"salaire_base_mensuel": 10000, "annees": 7}) -> {'indemnite_aed': 55000.0}
…
  outil retenue_garantie({"montant_ht": 120000, "ttc": 126000, "taux_retenue": 0.1}) -> {'retenue_aed': 12000.0, 'net_a_payer_aed': 114000.0}
…
  reussi en 2 essais ; leçon : Toujours appeler gratuite_fin_de_service : 30 jours par an après 5 ans.
…
OK — toutes les vérifications sont passées.
```

## Passer au vrai modèle : l'adaptateur Claude

Pour passer du faux modèle au vrai, on remplace une seule ligne : l'objet passé à `executer_agent`. L'adaptateur ci-dessous a la même méthode `create(system=..., messages=..., tools=...)` que `FakeLLM`, et il renvoie la réponse de l'API, qui porte `stop_reason` et `content`. La boucle, les outils et les cas de ce fichier restent identiques ; seule la liste `schemas` doit maintenant contenir les définitions d'outils au format de l'API, que `definitions_api()` produit à l'étape 12.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`ClaudeLLM.__init__(model, effort)`** — Le constructeur de l'adaptateur ouvre la ligne vers le vrai modèle, comme un standardiste qui branche la prise avant le premier appel : il reçoit le nom du modèle, `"claude-opus-5-5"` par défaut, et un niveau d'effort, `"medium"` par défaut, crée un client `anthropic.Anthropic()`, qui lit la clé `ANTHROPIC_API_KEY` ou le profil créé par `ant auth login`, et garde ces deux réglages pour chaque requête. Il ne renvoie rien ; une configuration absente ou invalide serait signalée par la bibliothèque `anthropic` elle-même.

**`ClaudeLLM.create(system, messages, tools)`** — Cette méthode est l'adaptateur proprement dit, qui parle au vrai modèle en gardant exactement la signature de `FakeLLM` : elle reçoit en arguments nommés le prompt système, l'historique et les définitions d'outils, envoie une requête avec le modèle retenu, 16 000 tokens de sortie au plus, l'effort choisi et le repli côté serveur activé, puis, si la réponse est un refus accompagné de détails, imprime sa catégorie et son explication. Elle renvoie la réponse de l'API telle quelle, qui porte `stop_reason` et `content` ; la boucle `executer_agent` la consomme donc sans aucune modification, et une erreur réseau remonterait depuis le client.

```python
# [extrait] — adaptateur Claude, non exécuté par le harnais (pip install anthropic + clé API ou `ant auth login`)
import anthropic


class ClaudeLLM:
    """Même interface que FakeLLM : create(system=..., messages=..., tools=...) renvoie une réponse
    qui a .stop_reason et .content (blocs .type, .text, .id, .name, .input). executer_agent() ne change pas."""

    def __init__(self, model: str = "claude-opus-5-5", effort: str = "medium"):
        self.client = anthropic.Anthropic()   # lit ANTHROPIC_API_KEY ou le profil créé par `ant auth login`
        self.model = model
        self.effort = effort

    def create(self, *, system: str, messages: list, tools: list):
        reponse = self.client.beta.messages.create(
            model=self.model,
            max_tokens=16000,
            system=system,
            messages=messages,
            tools=tools,                             # [{"name", "description", "input_schema", "strict": True}]
            output_config={"effort": self.effort},   # réflexion adaptative active par défaut sur ce modèle
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",                     # en cas de refus, l'API relance la requête sur un modèle de repli
        )
        if reponse.stop_reason == "refusal" and reponse.stop_details:
            print(f"refus : {reponse.stop_details.category} — {reponse.stop_details.explanation}")
        return reponse


# Schéma d'outil au format de l'API (strict : les arguments respectent exactement le schéma)
SCHEMA_MENSUALITE = {
    "name": "mensualite",
    "description": "Calcule la mensualité d'un prêt amortissable en AED.",
    "input_schema": {
        "type": "object",
        "properties": {
            "principal": {"type": "number"},
            "taux_annuel": {"type": "number"},
            "n_mois": {"type": "integer"},
        },
        "required": ["principal", "taux_annuel", "n_mois"],
        "additionalProperties": False,
    },
    "strict": True,
}

# resultat = executer_agent(ClaudeLLM(), system, question, outils, [SCHEMA_MENSUALITE])
```

Quatre règles de l'API sont déjà respectées par la boucle, et il faut les connaître pour ne pas les casser en la modifiant.

- **Pas de `tool_choice` forcé.** Ce modèle refuse qu'on lui impose un outil précis (erreur 400) : on laisse le choix automatique, on nomme l'outil attendu dans le prompt, et l'on déclare les outils en mode `strict` pour que leurs arguments respectent le schéma.
- **Tous les `tool_result` dans un seul message `user`.** Quand le modèle demande plusieurs outils dans une réponse, on renvoie tous les résultats ensemble, comme le fait `executer_agent` ; les séparer en plusieurs messages lui apprend à ne plus demander d'appels parallèles.
- **Recopier `reponse.content` tel quel dans l'historique.** La réponse peut contenir des blocs de réflexion en plus des blocs `text` et `tool_use` ; la boucle les recopie sans les retoucher, et le modèle en a besoin pour poursuivre son raisonnement.
- **Traiter `stop_reason` égal à `"refusal"` avant de lire le contenu.** Un refus n'est pas une réponse à interpréter : la boucle s'arrête avec le statut `refus`, et l'adaptateur affiche la catégorie et l'explication fournies par l'API. Le paramètre `fallbacks` demande en plus à l'API de rejouer la requête sur un modèle de repli en cas de refus.

## Squelette algorithmique

Les six agents de ce fichier partagent le même moteur, la boucle de l'étape 1, et ne diffèrent que par leurs outils. Les trois patterns (ReAct, Plan-and-Execute, Reflexion) changent seulement la façon d'enchaîner les appels au modèle. Les formules de la démonstration, le score z et l'inégalité de Bienaymé-Tchebychev, servent à un outil de détection d'anomalie.

```text
ALGORITHME ReAct
ENTRÉES : modèle, outils, question, max_étapes
  messages ← [question]
  RÉPÉTER au plus max_étapes fois
      réponse ← modèle(messages, outils)
      SI réponse est finale ALORS RETOURNER réponse
      résultat ← exécuter l'outil demandé ; ajouter (demande, résultat) à messages
  FIN

ALGORITHME PlanPuisExécution
  plan ← modèle(« donne la liste JSON des étapes pour : » question)        (1 appel)
  vérifier le plan : outils autorisés, références @k vers des étapes antérieures
  POUR k DE 1 À longueur(plan) FAIRE
      arguments ← plan[k].arguments, où chaque « @j.champ » est remplacé par résultats[j].champ
      résultats[k] ← outils[plan[k].outil](arguments)                         (en code, sans le modèle)
  FIN POUR
  RETOURNER modèle(« synthétise : » résultats)                              (1 appel)

ALGORITHME Reflexion
ENTRÉES : acteur, critique, question, évaluer (le contrôle du résultat), E essais
  leçons ← liste vide
  POUR e DE 1 À E FAIRE
      tentative ← ReAct(acteur, question + leçons)
      SI évaluer(tentative) ALORS RETOURNER tentative
      SI e < E ALORS ajouter critique(tentative) à leçons                     (1 appel)
  FIN POUR
  RETOURNER tentative

ALGORITHME ScoreZ (outil d'anomalie)
ENTRÉES : historique x₁ … xₙ, nouvelle valeur x, seuil k
  x̄ ← Σ xᵢ / n        s ← √( Σ (xᵢ − x̄)² / (n − 1) )
  z ← (x − x̄) / s
  SI |z| ≥ k ALORS RETOURNER « anomalie »     (au plus 1/k² des valeurs ici, quelle que soit la loi)
  RETOURNER « normal »
```

**Complexité.** Le coût de chaque pattern se compte en appels au modèle, comme dans la démonstration : ReAct fait k + 1 appels pour k étapes d'outils, Plan-and-Execute en fait toujours 2 (le plan et la synthèse), quel que soit le nombre d'étapes, et Reflexion en fait au plus E × (k + 1) + (E − 1) pour E essais. Les outils eux-mêmes sont des calculs en O(1), sauf l'estimation de prix et le score z, linéaires en la taille de leur série. Le score z coûte O(n) pour la moyenne et l'écart-type. La mémoire de ReAct croît avec l'historique des messages.

**Du squelette au code.** `ReAct` correspond à `executer_agent`, réutilisée telle quelle par chaque cas d'usage. `PlanPuisExécution` correspond à `plan_and_execute`, qui résout les références `@k` avant chaque appel d'outil, et `Reflexion` à `reflexion(acteur, critique, …, evaluer, essais_max=2)`. `ScoreZ` correspond à `outil_zscore`, avec un seuil de 3. Les autres outils (`outil_mensualite`, `outil_estimer_prix`, `outil_indemnite`, `outil_gratuite`, `outil_tva`, `outil_ratio`, `outil_retenue`) appellent les fonctions de calcul, et l'adaptateur `ClaudeLLM` remplace le faux modèle sans toucher à la boucle.

## Pièges et limites

- **Appeler les outils sans le registre.** Une fonction appelée nue accepte une vétusté de 20 et renvoie 0 sans erreur ; c'est le schéma de l'étape 12 qui l'arrête. Ce fichier appelle les outils directement pour rester lisible, pas pour montrer la façon de faire en production.
- **Croire le scénario.** Le faux modèle joue un script : il prouve que la boucle traite correctement chaque réponse, pas qu'un vrai modèle choisirait ces outils. La qualité des décisions du modèle se mesure à part, sur un jeu de cas étiquetés (étapes 13 bis et suivantes).
- **Laisser le modèle recopier les nombres.** Dans les six cas, la réponse finale recopie des résultats d'outils ; un modèle peut encore mal les recopier (« 5 585,32 »). Pour les montants qui engagent la banque ou l'assureur, on construit la phrase finale en code à partir de la trace, ou l'on vérifie que chaque nombre cité figure dans la trace.
- **Un plan qui ne se relit pas.** Plan-and-Execute n'apporte de sécurité que si le plan est validé avant l'exécution : schéma du plan, outils autorisés, références `@k` qui pointent vers des étapes antérieures.
- **Un évaluateur de Reflexion trop indulgent ou trop sévère.** Il décide de tout : s'il accepte une réponse fausse, la leçon n'est jamais écrite ; s'il refuse une réponse juste, l'agent tourne jusqu'à épuiser ses essais.

### Exercice feuille blanche

1. Sans regarder le code, écrire `executer_agent` avec ses cinq statuts, puis le faire tourner sur le scénario bancaire. Vérifier que la boucle s'arrête en trois étapes.
2. Prédire, puis vérifier : dans le cas crypto, quelle mesure x donnerait exactement z = −3 ? (Réponse : x = 12,1 − 3 × 0,18257 = 11,552 M AED ; une mesure à 11,55 déclenche l'alerte, une mesure à 11,56 non.)
3. Trouver le bug : une variante d'`executer_agent` ajoute un message `user` par `tool_result`, dans la boucle sur les appels. Quel cas de ce fichier le révèle, et quelle règle de l'API viole-t-elle ?

> Suite : [Évaluer un agent : définitions](<13b-Evaluation-Definitions-Fondamentaux.md>) — étape 13 bis.
