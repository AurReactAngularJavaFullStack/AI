# Review — les réponses de Grok sur l'agent « feuille blanche », les dépendances et Jev

Relu le 17 novembre 2026.

Trois réponses sont relues ici :

- la réponse sur l'agent construit depuis une feuille blanche, les dépendances et les outils les plus utilisés : [AI Agent from scratch vs with Tools Libraries and dependencies.md](<../../AI Agent from scratch vs with Tools Libraries and dependencies.md>) ;
- la réponse sur Jev et la facture impayée de chantier ;
- la réponse sur le coût de Jev et les modèles génératifs qui feraient mieux. Ces deux dernières sont dans [JEV Utility Assessment.md](<../../JEV Utility Assessment.md>).

Chaque affirmation a été vérifiée de deux façons : dans le cours lui-même (les fichiers sont cités en lien), ou dans les sources publiques de 2026 (liste à la fin).

Légende : ✓ d'accord · ~ d'accord avec une nuance · ✗ désaccord.

## Plan

1. Le verdict
2. Réponse 1 — construire un agent depuis une feuille blanche
3. Réponse 2 — Jev et la facture impayée de chantier
4. Réponse 3 — coûts, erreurs, et quels modèles génératifs
5. Programme de vérification des chiffres
6. Exercices à refaire sur feuille blanche
7. À corriger dans JEV Utility Assessment.md
8. Sources

---

## 1. Le verdict

**Non, je ne suis pas d'accord sur tout.**

Je suis d'accord avec le fond : l'agent se construit à la main, les frameworks sont facultatifs, Jev donne des probabilités et le code garde les euros et le veto.

Mais il y a :

- un contresens : « JEV » lu comme Java ;
- un benchmark introuvable ;
- un test mal daté et lu à moitié, qui va en réalité plutôt dans le sens de Jev pour l'usage visé ;
- des oublis qui comptent pour des factures de chantier : les PDF, la confidentialité, l'architecture hybride et le droit français des retards de paiement.

| Ce que Grok affirme | Avis | Section |
| --- | --- | --- |
| Le cours suffit pour partir d'une feuille blanche | ✓ vérifié dans le dépôt | 2.1 |
| « Si jev veut dire Java » | ✗ contresens | 2.2 |
| Le tableau des dépendances | ✓ avec une correction (Kafka, Redis) | 2.3 |
| Le classement « le plus utilisé » | ~ confond importance et usage | 2.4 |
| Les faits sur Jev (TypeSafe, fondateur, types de questions) | ✓ vérifiés | 3.1 |
| Les probabilités dans Jev, les euros dans le code | ✓ entièrement d'accord | 3.1 |
| « Les probabilités disent à quel point le texte ressemble au libellé » | ~ caricatural | 3.2 |
| L'exemple chiffré de la facture | ~ options qui se recouvrent, droit absent | 3.4 à 3.8 |
| Les prix de Jev et de Haiku 5.5 | ✓ exacts | 4.1 |
| Le « test de novembre 2026 » (15, 30 et 41 erreurs) | ~ chiffres justes, date fausse, contexte manquant | 4.2 |
| Le « relevé du 14 novembre » (400 textes, 81 %) | ✗ introuvable | 4.3 |
| Quels modèles génératifs sont meilleurs | ~ réponse incomplète | 4.4 |

---

## 2. Réponse 1 — construire un agent depuis une feuille blanche

### 2.1 Le cours suffit-il ? ✓

Oui. J'ai vérifié dans le dépôt :

- les douze paliers sont dans `Exercices/`, et le projet final est l'[étape 77](<../13-Projet-Final/77-Projet-Final-Agent-From-Scratch.md>) ;
- les affiches vont bien de 01 à 45, et le [sommaire des affiches](<../Images/00-Sommaire/00_Sommaire.md>) range les « dix-huit classes » citées par Grok ;
- l'utilité espérée est bien rattachée à l'étape 38 (classe 14 du sommaire), et le score de risque à l'[étape 67](<../11-GardeFous/67-GardeFous-Formule-Score-de-Risque.md>) ;
- le palier 12 contient bien un [adaptateur Claude](<../Exercices/12-Assemblage-Agent-Complet/solutions/agent/adaptateur_claude.py>) et une progression [« Passer au vrai LLM »](<../Exercices/12-Assemblage-Agent-Complet/solutions/progression/07-Passer-au-vrai-LLM.md>).

**La nuance : savoir construire n'est pas savoir faire tourner en vrai.** Le faux modèle des tests ne fait jamais ce que fait un vrai modèle :

- sortir du schéma demandé ;
- se laisser manipuler par une phrase cachée dans un document ;
- coûter plus que prévu, parce que l'historique grossit à chaque tour.

Le palier 12 et l'évaluation sur des données réelles ne sont donc pas une formalité. C'est là que ces trois problèmes apparaissent.

### 2.2 « Si jev veut dire Java » ✗

La question portait sur **Jev, le modèle de décision de TypeSafe**, pas sur Java. Le dossier [JEV](<../../JEV/How JEV Fits Inside an AI Agent.jpg>) contient d'ailleurs « How JEV Fits Inside an AI Agent.jpg » et « JEV vs LLM.jpg ». Ce paragraphe de Grok répond à une question qui n'a pas été posée.

Même pour Java, la réponse est incomplète. Une équipe qui vit dans Spring regarderait d'abord Spring AI ou LangChain4j, avant Google ADK.

La vraie question était : faut-il refaire pour Jev la même série d'affiches que pour les dix-huit classes ? Grok n'y répond que dans sa deuxième réponse, et là je suis d'accord avec lui : **non**. Jev n'apporte aucune formule nouvelle. Tout ce qu'il faut est déjà dans le cours :

- la softmax, pour lire une loi de probabilité sur des options (classe 3, [fiche 04](<../Images/03-Modele/04_softmax_temperature.md>)) ;
- l'utilité espérée, pour choisir (classe 14, [fiche 10](<../Images/06-Decision/10_utilite_esperee.md>)) ;
- la valeur de l'information, pour savoir si un renseignement de plus vaut son coût (classe 15, [fiche 28](<../Images/06-Decision/28_valeur_information.md>)) ;
- le score de Brier, pour savoir si l'on peut croire un pourcentage (classe 16, [fiche 20](<../Images/07-Mesure/20_score_brier.md>)) ;
- le veto, pour l'irréversible (étape 67).

### 2.3 Le tableau des dépendances ✓, avec une correction

D'accord sur le principe. Une dépendance qui est un contrat est saine : MCP, OpenTelemetry, Postgres. On peut changer ce qu'il y a derrière sans toucher à l'agent. Un framework qui possède la boucle, le schéma et le veto l'est beaucoup moins.

**La correction.** Grok range Kafka et Redis « hors sujet pour l'agent ». Cela contredit le cours lui-même, qui a deux étapes là-dessus : le [journal d'événements partitionné](<../08-Orchestration/45b-Journal-d-Evenements-Partitionne.md>) et les [déclencheurs et tâches longues](<../08-Orchestration/45c-Declencheurs-Webhooks-et-Taches-Longues.md>).

- Redis sert souvent de mémoire de session et de cache.
- Un journal d'événements permet de reprendre une tâche longue après une panne.

Ils sont hors sujet pour la justesse d'une réponse. Ils ne le sont pas pour un agent qui tourne pendant des heures.

### 2.4 Le classement « le plus utilisé » ~

La question était « qu'est-ce qui est le plus utilisé ». Grok répond plutôt « qu'est-ce qui compte le plus », et colle un nom d'outil sur chaque pièce de l'agent. Ce sont deux classements différents.

**Ce que disent les chiffres disponibles :**

| Mesure | Résultat | Limite |
| --- | --- | --- |
| Usage général des développeurs (sondage Stack Overflow, avril 2026, environ 1 100 personnes) | LangChain 22 %, OpenClaw 17 %, LangGraph 14 % | usage général, pas production ; chiffre relayé, pas vu à la source |
| Classements orientés production | LangGraph en tête, puis Claude Agent SDK, OpenAI Agents SDK, Mastra | blogs de praticiens, pas une enquête |
| Pydantic AI | aucun chiffre d'adoption trouvé | le « souvent Pydantic AI » de Grok n'est pas sourcé |

« LangGraph est le plus cité en production » est donc plausible. Mais oublier le Claude Agent SDK est notable, alors que le palier 12 branche justement Claude.

**L'ordre d'importance.** 

Je suis d'accord avec l'ordre de Grok, sauf pour le modèle, qu'il place en 7ᵉ position parce qu'il serait « interchangeable ». Il est interchangeable dans le code, pas dans les résultats. Sur la même tâche de routage à 77 classes, Claude Opus 5.5 fait 85,7 % et Jev 78,3 % : 7,4 points d'écart, avec p < 0,001. Changer de modèle oblige donc à refaire toute l'évaluation. C'est pour cela que l'évaluation, 3ᵉ dans sa liste, doit exister avant de changer de modèle.

---

## 3. Réponse 2 — Jev et la facture impayée de chantier

### 3.1 Ce qui est juste et vérifié ✓

**Les faits sur Jev :**

- Jev est le modèle de décision de TypeSafe, sorti le 15 septembre 2026.
- Diogo Almeida en est le cofondateur et le PDG. Il est auteur d'InstructGPT. La phrase de Grok, « il a travaillé sur l'alignement qui a mené à ChatGPT », est plus juste que le « co-inventeur de ChatGPT » qui circule.
- Il y a trois types de questions. **Choice** choisit une option parmi une liste, avec la probabilité de chacune. **Score** place l'état sur une échelle. **Noul** donne la probabilité du oui.
- La documentation dit que les questions d'un même appel sont « évaluées indépendamment et en parallèle ». Le conseil de Grok est donc correct : « est-ce un litige ? » puis « quelle suite, sachant que c'est un litige ? », ce sont deux appels, ou un branchement dans le code.

**La frontière entre probabilités et euros.** 

Je suis entièrement d'accord, et TypeSafe la confirme lui-même :

- parmi les limites de Jev, ils citent « l'arithmétique et les dates imprécises ». Or une facture, ce sont justement des montants et des dates ;
- ils écrivent aussi que « la confiance n'est pas une autorisation » : une probabilité élevée ne peut ni approuver un accès ni lever une limite de risque.

**Le veto sur l'appel de caution** est conforme à la règle de l'[étape 67](<../11-GardeFous/67-GardeFous-Formule-Score-de-Risque.md#L31>) : veto si l'action est irréversible, ou si le montant atteint le seuil M\*.

**La calibration sur ses propres factures** est indispensable. TypeSafe indique que la qualité de Jev varie selon la langue et selon l'ordre des options. Il faut donc la mesurer sur des factures en français, avec ses propres libellés.

### 3.2 Une nuance sur « le texte ressemble au libellé » ~

Grok écrit que, si l'on demande à Jev « laquelle de ces cinq suites est la meilleure ? », les probabilités disent « à quel point le texte ressemble à chaque libellé ». C'est une caricature. Jev est entraîné pour que ses probabilités soient calibrées sur la question posée.

Le vrai problème est ailleurs :

- Jev ne connaît ni le taux de portage de l'entreprise, ni sa marge, ni ses intérêts contractuels ;
- sa probabilité dit quelle réponse est juste, pas quelle issue va se produire.

La conclusion de Grok reste donc vraie : ce ne sont pas des euros. Seul le raisonnement qui y mène est à corriger.

### 3.3 Rappel du cours : l'utilité espérée

L'utilité espérée d'une action, classe 14 du sommaire, étape 38 :

$$
EU(a) = \sum_{o} P(o \mid a)\, U(o)
$$

Les symboles, un par un :

$$
a
$$

L'action envisagée : ici l'une des suites possibles, par exemple appeler la caution, porter le trou de trésorerie, ou accepter le retard contre intérêts.

$$
o
$$

Une issue possible après l'action, par exemple « le client paie sous 90 jours » ou « le client ne paie pas ».

$$
P(o \mid a)
$$

La probabilité de l'issue o quand on choisit l'action a. C'est la seule place où une probabilité de Jev peut entrer, et seulement si la question posée à Jev portait vraiment sur cette issue.

$$
U(o)
$$

Ce que vaut l'issue o, calculé dans le code à partir du grand livre. Grok la prend en euros ; la section 3.7 montre pourquoi c'est une simplification.

$$
EU(a)
$$

L'utilité espérée de l'action a : la moyenne des valeurs des issues, chacune pesée par sa probabilité. On retient l'action dont ce nombre est le plus haut, sous réserve du veto.

### 3.4 Dans l'exemple, les options se recouvrent ~

Grok présente deux suites séparées : « porter le trou en besoin en fonds de roulement », qui coûte environ 2 000 € quoi qu'il arrive, et « accepter le retard avec intérêts », qui rapporte les intérêts si le client paie. Mais **accepter le retard, c'est aussi porter le trou pendant ce temps.** La seconde option contient la première.

Les grandeurs de l'exemple :

$$
M
$$

Le montant de la facture impayée : 100 000 €.

$$
j
$$

La durée du report, en jours : 90.

$$
r_p
$$

Le taux annuel du portage, c'est-à-dire ce que coûte le découvert ou la ligne de trésorerie qui comble le trou : 8 %.

$$
r_i
$$

Le taux annuel des intérêts de retard que le client devra s'il paie : 10 %.

$$
C = M \cdot r_p \cdot \frac{j}{365}
$$

Le coût du portage sur la période. Il est payé que le client paie ou non.

$$
I = M \cdot r_i \cdot \frac{j}{365}
$$

Les intérêts de retard sur la période. Ils ne sont encaissés que si le client paie.

Avec les chiffres de Grok :

$$
C = 100\,000 \times 0{,}08 \times \frac{90}{365} \approx 1\,972{,}60\ \text{€}
$$

$$
I = 100\,000 \times 0{,}10 \times \frac{90}{365} \approx 2\,465{,}75\ \text{€}
$$

Si le client paie, le report laisse I − C :

$$
I - C \approx 493{,}15\ \text{€}
$$

S'il ne paie pas, le report laisse seulement −C, soit −1 972,60 €, et la créance est toujours due. Présenter les deux options comme séparées revient à compter le portage d'un côté et pas de l'autre.

### 3.5 Démonstration ajoutée : le seuil de paiement p\*

**Ce qu'on démontre.** 

Accepter le retard contre intérêts rapporte en moyenne si et seulement si la probabilité que le client paie dépasse le rapport des deux taux.

**L'idée.** 

On pèse les deux issues, « il paie » et « il ne paie pas », par leurs probabilités, comme dans l'utilité espérée de la section 3.3.

**Hypothèses.** Intérêts simples sur 365 jours. Si le client ne paie pas, la suite (relance, caution, justice) est la même que l'on ait accepté le report ou non ; on ne compare donc que ce que le report ajoute.
$$
p
$$

La probabilité que le client paie à l'échéance du report. C'est la question à poser à Jev, sous forme de question oui/non (Noul) : « le client paiera-t-il sous 90 jours ? ».

$$
E = p\,(I - C) + (1 - p)\,(-C)
$$

Le gain moyen du report : l'issue « il paie » pesée par p, l'issue « il ne paie pas » pesée par 1 − p.

**La preuve, pas à pas.** 

On développe et on simplifie :
$$
E = p\,I - p\,C - C + p\,C = p\,I - C
$$

On remplace I et C par leurs formules, et on met en facteur ce qu'elles ont en commun :

$$
E = M \cdot \frac{j}{365} \cdot (p\,r_i - r_p)
$$

Le facteur devant la parenthèse est toujours positif. Le report rapporte donc en moyenne exactement quand la parenthèse est positive :

$$
E \geq 0 \iff p \geq \frac{r_p}{r_i}
$$

$$
p^{*} = \frac{r_p}{r_i}
$$

Le seuil de paiement : la probabilité de paiement à partir de laquelle accepter le retard contre intérêts rapporte en moyenne.

**La vérification chiffrée.** 

Avec les taux de l'exemple :
$$
p^{*} = \frac{0{,}08}{0{,}10} = 0{,}8
$$

Au seuil, le gain moyen est nul, au centime près :

$$
0{,}8 \times 2\,465{,}75 - 1\,972{,}60 = 0
$$

**Ce que la preuve révèle.**

- Le montant et la durée ont disparu du seuil. Ils multiplient les deux côtés de la balance. Ils comptent pour la taille du gain ou de la perte, et pour le veto (montant ≥ M\*), pas pour le sens de la décision.
- Jev ne doit pas répondre à « quelle suite est la meilleure ? ». Il doit répondre à « le client paiera-t-il sous 90 jours ? ». Sa probabilité p se compare ensuite à p\* = 0,8, que le code calcule à partir de ses propres taux.

**La conséquence pour l'agent.** 

La frontière de Grok devient une seule ligne de code, dans le domaine et non dans le modèle : `p >= taux_portage / taux_interets`.

### 3.6 Ce que coûte une mauvaise calibration

Supposons que Jev annonce 0,85 pour une facture. C'est au-dessus du seuil de 0,8 : on accepte le report. Le gain moyen annoncé est :

$$
E_{\text{annoncée}} = 0{,}85 \times 2\,465{,}75 - 1\,972{,}60 \approx +123{,}29\ \text{€}
$$

Mais si, sur les factures de l'entreprise, les 0,85 de Jev ne sont justes que 75 % du temps, le gain moyen réel est :

$$
E_{\text{réelle}} = 0{,}75 \times 2\,465{,}75 - 1\,972{,}60 \approx -123{,}29\ \text{€}
$$

**Même décision, signe opposé.** 

C'est pour cela que le score de Brier, mesuré sur ses propres factures, passe avant tout seuil ([fiche 20](<../Images/07-Mesure/20_score_brier.md>)) :
$$
\mathrm{Brier} = \frac{1}{N} \sum_{n=1}^{N} (p_n - o_n)^2
$$

L'écart moyen au carré entre la probabilité annoncée et ce qui s'est réellement passé. Plus il est petit, plus on peut croire les pourcentages.

$$
N
$$

Le nombre de factures du jeu de contrôle, déjà réglées ou définitivement impayées.

$$
p_n
$$

La probabilité de paiement annoncée par Jev pour la facture numéro n.

$$
o_n
$$

Ce qui s'est réellement passé pour la facture numéro n : 1 si le client a payé dans le délai, 0 sinon. Ici, o désigne une issue observée, notée 0 ou 1.

### 3.7 Des euros ne sont pas une utilité ~

Prendre U(o) en euros, c'est supposer que l'entreprise est neutre au risque : perdre 100 000 € d'un coup compterait exactement comme deux pertes de 50 000 €. Pour une PME du BTP, ce n'est pas vrai. Une grosse perte peut faire tomber la trésorerie, et l'entreprise avec.

L'espérance en euros maximise la moyenne, pas la survie. Il faut ajouter au moins l'une de ces deux protections :

- une contrainte : trésorerie minimale à respecter, ou probabilité de rupture de trésorerie plafonnée ;
- une utilité qui pèse davantage les grosses pertes que les petites.

### 3.8 Le droit français est absent ~

Voici ce que j'en sais, à faire valider par un juriste ou un expert-comptable.

- **Les pénalités de retard sont dues d'office entre professionnels.** 

  C'est l'article L441-10 du Code de commerce : par défaut, le taux de la BCE majoré de 10 points, et jamais moins de trois fois le taux d'intérêt légal, plus une indemnité forfaitaire de 40 € pour frais de recouvrement. « Accepter le retard avec intérêts » n'est donc pas une concession, c'est le régime normal. La vraie option est d'y renoncer, comme geste commercial.

- **En marché public**, les intérêts moratoires courent aussi d'office.

- **La caution qui protège l'entreprise est la garantie de paiement.** 

  En marché privé de travaux, c'est l'article 1799-1 du Code civil, au-delà de 12 000 € HT. Si le client ne l'a pas fournie et ne paie pas, l'entreprise peut suspendre les travaux après une mise en demeure restée sans effet pendant 15 jours.

- **Des options manquent dans la liste :** la mise en demeure, la suspension des travaux, l'injonction de payer, l'échéancier, l'affacturage ou la cession Dailly, l'assurance-crédit.

### 3.9 Ce qui manque pour des factures réelles

- **Le format.** 

  Jev lit du texte. 

  Les images PNG et JPEG ne sont acceptées qu'en mode expérimental, et il ne lit pas les PDF. Il est limité à 64 000 jetons par appel, et 32 000 par question. Une facture scannée demande donc une étape d'extraction avant Jev. 

  À l'inverse, Gemini Decision 1, sorti le 11 novembre 2026, lit les PDF et les images jusqu'à 256 000 jetons, pour 0,10 USD par million de jetons d'entrée.

- **La confidentialité.**

   TypeSafe n'annonce pas de région d'hébergement, et la rétention zéro des données est réservée aux contrats entreprise. Pour des contrats et des factures clients, il faut vérifier le RGPD et le secret des affaires dans leur accord de traitement des données (DPA).

- **La sécurité.** 

  Le texte d'un courrier client entre dans l'état que lit Jev, et peut influencer sa décision. C'est une porte d'entrée pour une manipulation, comme pour n'importe quel modèle.

- **La version.** 

  L'alias jev-latest change sans prévenir. Il faut fixer la version testée et l'enregistrer dans le journal à chaque appel.

---

## 4. Réponse 3 — coûts, erreurs, et quels modèles génératifs

### 4.1 Facultatif, et pas à cause du prix ✓

D'accord : Jev est facultatif pour cette décision. D'accord aussi que son prix n'est pas le frein. Ce qui coûte, c'est un fournisseur de plus et un jeu de factures étiquetées, pour une décision rare dont les euros sont déjà dans le code.

**Les prix cités sont exacts :**

| Modèle | Entrée, par million de jetons | Sortie, par million de jetons |
| --- | --- | --- |
| Jev | 0,042 USD | gratuite |
| Claude Haiku 5.5 (tarif officiel Anthropic, jusqu'à 100 000 jetons) | 0,10 USD | 0,50 USD |

En entrée, Haiku 5.5 coûte donc environ 2,4 fois plus cher que Jev, et sa sortie est payante.

### 4.2 Le « test de novembre » (15, 30 et 41 erreurs), relu ~

Ce test existe : c'est celui de Vincent van Deth. Les chiffres que cite Grok sont justes, mais le contexte qui permet de les lire manque.

| Point | Ce que dit Grok | Ce que dit le test |
| --- | --- | --- |
| Date | novembre 2026 | lancé le 26 septembre, relancé le 9 octobre 2026 |
| Erreurs sur 600 réponses | Haiku 15, OpenAI 30, Jev 41 | ✓ identique |
| Coût pour 1 000 décisions | 1 à 2 centimes pour Jev, 6 à 7 pour Haiku | ✓ 0,011 à 0,016 USD pour Jev, 0,063 à 0,071 USD pour Haiku |
| Latence | Haiku environ dix fois plus lent | ✓ 293 ms contre 3 105 ms, mais avec réflexion ; 1,1 s sans réflexion |
| API Decisions d'OpenAI | non précisé | plus rapide que Jev : 179 ms |
| Écart entre OpenAI et Jev | 30 contre 41 | p = 0,09 : écart non démontré |
| Calibration | absente | erreur de calibration : Jev 0,014, OpenAI 0,054, Haiku 0,112 |
| Corpus | absent | 450 textes en néerlandais, écrits par un modèle Claude, 3 tâches, une seule exécution |

Trois points changent la lecture :

- **Un avantage à domicile.** 

  Les textes avaient été écrits par un modèle Claude. L'auteur dit lui-même que cela a pu avantager Haiku, qui est aussi un modèle Claude.

- **Le seul écart net** est celui entre Haiku et Jev. Entre OpenAI et Jev, rien n'est démontré.

- **Le résultat qui compte pour cet usage est absent : la calibration.** 

  Quand Jev annonce 90 % ou plus, il a raison 98,7 % du temps. Pour multiplier une probabilité par des euros, comme en section 3.5, c'est ce chiffre qui compte, pas le nombre d'erreurs. Ce test penche donc vers Jev pour la facture, pas contre lui.

### 4.3 Le « relevé du 14 novembre » : introuvable ✗

Je ne trouve nulle part ce relevé de 400 textes donnant GPT-6 Luna à 81,5 %, Jev à 81,0 % et Gemini à 81,2 %. 

Les sources les plus proches :

- AIMLAPI, le 25 septembre 2026, sur 300 exemples par tâche (chiffres en section 4.4) ;
- Mastra, le 22 octobre 2026, sur 400 questions, mais à propos de la dégradation en contexte long, et sans ces chiffres ;
- les chiffres de Google au lancement de Gemini Decision 1, le 11 novembre : 92,2 % pour Gemini Decision 1, 90,9 % pour Luna, 90,0 % pour Jev, mesurés par Google lui-même.

Je le traite comme non sourcé.

En revanche, l'affirmation « Jev est devant sur les questions oui/non » est soutenue ailleurs : sur BoolQ, Jev fait 91,0 %, l'API Decisions d'OpenAI 83,8 % et Haiku 87,2 %.

### 4.4 Quels modèles génératifs sont meilleurs ~

Grok cite Haiku 5.5 et GPT-6 Luna. Il manque l'essentiel : **les grands modèles battent Jev sur les tâches difficiles, et les petits sont à égalité avec lui.**

Routage d'intentions à 77 classes (AIMLAPI, 25 septembre 2026, 300 exemples) :

| Modèle | Bonnes réponses | Coût pour un million de décisions | Latence médiane |
| --- | --- | --- | --- |
| Claude Opus 5.5 | 85,7 % | 8 243 USD | 2,97 s |
| GPT-6 Sol | 85,3 % | 2 321 USD | 1,81 s |
| GPT-6 Luna | 80,7 % | 116 USD | 1,47 s |
| Gemini 3.5 Flash | 80,3 % | 661 USD | 1,56 s |
| DeepSeek V4 Flash | 79,3 % | 77 USD | 1,69 s |
| Jev 1.13 | 78,3 % | 98 USD | 0,84 s |

- Opus 5.5 et GPT-6 Sol ont environ 7 points d'avance sur Jev, avec p < 0,001.

- Luna, Gemini 3.5 Flash et DeepSeek V4 Flash sont à égalité statistique avec Jev. Haiku 5.5 l'est aussi dans d'autres tests.

- Sur des contrats (ContractNLI, article arXiv 2609.27678), les grands modèles hébergés sont plus précis ; Jev reste le plus rapide et le moins cher.

- **Deux modèles au même score ne font pas les mêmes erreurs.** 

  C'est le titre de cet article : « Same Scores, Different Decisions ». Il faut donc comparer les modèles facture par facture, pas seulement sur un pourcentage global.

**L'architecture qui manque dans la réponse de Grok : l'hybride.**

 Jev répond d'abord. Seuls les cas où sa confiance est sous un seuil partent vers un grand modèle.

| Montage | Bonnes réponses | Coût pour un million de décisions |
| --- | --- | --- |
| Opus 5.5 seul | 85,7 % | 8 243 USD |
| Jev d'abord (confiance ≥ 0,9), puis Opus 5.5 | 85,3 % | 3 154 USD |
| GPT-6 Sol seul | 85,3 % | 2 321 USD |
| Jev d'abord (confiance ≥ 0,9), puis GPT-6 Sol | 84,7 % | 895 USD |

Avec Opus, on garde presque la même précision pour 38 % du coût.

Pour les factures, cela donne :

1. Jev trie chaque facture avec des questions fermées : litige ou simple retard, paiement probable sous 90 jours.
2. Les cas douteux partent vers un grand modèle, ou vers un humain.
3. Les euros, le seuil p\*, le veto et la caution restent dans le code.

---

## 5. Programme de vérification des chiffres

Ce programme recalcule tous les nombres de cette review : le portage et les intérêts de l'exemple, le seuil p\*, l'effet d'une mauvaise calibration, les rapports tirés des tests publics, et les corrigés de la section 6. Chaque `assert` arrête le programme si un nombre a glissé.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`interets_simples(montant, taux_annuel, jours)`** — Imagine le trésorier de l'entreprise de travaux, calculette en main, qui se demande ce que coûte un trou de 100 000 euros laissé ouvert pendant trois mois : cette fonction reçoit le montant, le taux annuel et le nombre de jours, multiplie les trois puis divise par 365, et renvoie les intérêts simples de la période. Elle sert deux fois dans `main` : avec 8 %, elle donne le prix du découvert qui porte le trou, 1 972,60 euros ; avec 10 %, elle donne les intérêts que le client devra s'il finit par payer, 2 465,75 euros.

**`esperance_report(p_paiement, interets, portage)`** — Cette fonction joue le pari du chef d'entreprise qui accepte d'attendre : elle reçoit la probabilité que le client paie, les intérêts qu'il versera alors, et le coût du portage, qui sera payé de toute façon, que le client paie ou non. Elle renvoie la probabilité multipliée par les intérêts, moins le portage, c'est-à-dire le gain moyen du report une fois les deux issues pesées. C'est elle qui montre, dans `main`, qu'un 0,85 annoncé promet +123,29 euros, alors qu'un 0,85 juste seulement trois fois sur quatre en fait perdre autant.

**`seuil_paiement(taux_portage, taux_interets)`** — Celle-ci répond à la seule question que le trésorier devrait poser avant d'interroger Jev, « à partir de quelle probabilité de paiement le report vaut-il la peine ? » : elle reçoit les deux taux, divise celui du portage par celui des intérêts, et renvoie le seuil p\*, ici 0,08 divisé par 0,10, soit 0,8. Le montant et la durée ont disparu du calcul, parce qu'ils multiplient les deux côtés de la balance ; `main` vérifie qu'à ce seuil exact, le gain moyen du report tombe à zéro euro.

**`virgule(x, decimales, signe)`** — Petite fonction de mise au propre, comme le comptable qui recopie les chiffres de son brouillon dans le registre : elle reçoit un nombre, le nombre de décimales voulu, deux par défaut, et un drapeau qui dit s'il faut afficher le signe plus ou moins devant. Elle écrit le nombre avec le point décimal de Python, remplace ce point par la virgule française, et renvoie le texte, par exemple « +493,15 » ou « 10,6 », pour que la sortie se lise comme le reste de la review.

**`main()`** — Le chef d'orchestre de la vérification rejoue un à un les chiffres de la review : il force la console en UTF-8 pour que le symbole euro passe sous Windows, calcule le portage et les intérêts sur 100 000 euros et 90 jours, vérifie le gain net de 493,15 euros, le seuil de 0,8 et l'écart de 123,29 euros dû à une mauvaise calibration, puis recalcule les rapports tirés des tests publics : 38 % du coût pour l'hybride, 10,6 fois plus lent pour Haiku avec réflexion, 7,4 points d'écart entre Opus 5.5 et Jev, un prix d'entrée 2,4 fois plus élevé pour Haiku. Il termine par les corrigés des exercices, sur 250 000 euros et 60 jours, et la dernière ligne n'apparaît que si chaque `assert` a tenu.

```python
"""Review Grok — vérification des nombres cités : portage, intérêts, seuil de paiement, calibration, rapports tirés des tests publics."""
import sys


def interets_simples(montant: float, taux_annuel: float, jours: int) -> float:
    """Intérêts simples d'une période, sur une base de 365 jours."""
    return montant * taux_annuel * jours / 365


def esperance_report(p_paiement: float, interets: float, portage: float) -> float:
    """Gain moyen du report : les intérêts si le client paie, le portage dans tous les cas."""
    return p_paiement * interets - portage


def seuil_paiement(taux_portage: float, taux_interets: float) -> float:
    """Probabilité de paiement à partir de laquelle le report rapporte en moyenne."""
    return taux_portage / taux_interets


def virgule(x: float, decimales: int = 2, signe: bool = False) -> str:
    """Écrit un nombre avec la virgule décimale française, signe affiché si demandé."""
    texte = f"{x:+.{decimales}f}" if signe else f"{x:.{decimales}f}"
    return texte.replace(".", ",")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    # 1. L'exemple de Grok : 100 000 euros, 90 jours, portage à 8 %, intérêts à 10 %
    montant, jours = 100_000, 90
    portage = interets_simples(montant, 0.08, jours)
    interets = interets_simples(montant, 0.10, jours)
    net = interets - portage
    assert round(portage, 2) == 1972.60
    assert round(interets, 2) == 2465.75
    assert round(net, 2) == 493.15
    print(f"portage 90 j à 8 % : {virgule(portage)} €   intérêts 90 j à 10 % : {virgule(interets)} €   "
          f"net si le client paie : {virgule(net, signe=True)} €")

    # 2. Le seuil : le report rapporte en moyenne dès que p >= taux de portage / taux d'intérêts
    seuil = seuil_paiement(0.08, 0.10)
    au_seuil = esperance_report(seuil, interets, portage)
    assert abs(seuil - 0.8) < 1e-12
    assert abs(au_seuil) < 1e-9
    assert esperance_report(0.81, interets, portage) > 0 > esperance_report(0.79, interets, portage)
    print(f"seuil de paiement p* = {virgule(seuil, 1)}   espérance au seuil : {virgule(abs(au_seuil))} €")

    # 3. La calibration : un 0,85 annoncé, juste seulement 75 % du temps
    annoncee = esperance_report(0.85, interets, portage)
    reelle = esperance_report(0.75, interets, portage)
    assert round(annoncee, 2) == 123.29
    assert round(reelle, 2) == -123.29
    print(f"Jev annonce 0,85 : {virgule(annoncee, signe=True)} €   "
          f"Jev juste 75 % du temps : {virgule(reelle, signe=True)} €")

    # 4. Les rapports tirés des tests publics cités dans la review
    hybride = 3154 / 8243
    lenteur = 3105 / 293
    ecart = 85.7 - 78.3
    prix_entree = 0.10 / 0.042
    assert round(hybride * 100) == 38
    assert round(lenteur, 1) == 10.6
    assert round(ecart, 1) == 7.4
    assert round(prix_entree, 1) == 2.4
    print(f"hybride Jev + Opus : {round(hybride * 100)} % du coût d'Opus seul   "
          f"Haiku avec réflexion : {virgule(lenteur, 1)} fois plus lent   "
          f"écart Opus 5.5 − Jev : {virgule(ecart, 1)} points   "
          f"prix d'entrée Haiku / Jev : {virgule(prix_entree, 1)}")

    # 5. Les exercices de la fin : 250 000 euros, 60 jours, portage à 7 %, intérêts à 12 %
    c_ex = interets_simples(250_000, 0.07, 60)
    i_ex = interets_simples(250_000, 0.12, 60)
    seuil_ex = seuil_paiement(0.07, 0.12)
    annonce_ex = esperance_report(0.70, i_ex, c_ex)
    reel_ex = esperance_report(0.52, i_ex, c_ex)
    assert round(c_ex, 2) == 2876.71
    assert round(i_ex, 2) == 4931.51
    assert round(seuil_ex, 3) == 0.583
    assert round(annonce_ex, 2) == 575.34
    assert round(reel_ex, 2) == -312.33
    assert 0.52 < seuil_ex < 0.70
    print(f"exercice 1 : C = {virgule(c_ex)} €   I = {virgule(i_ex)} €   p* = {virgule(seuil_ex, 3)}")
    print(f"exercice 3 : annoncé {virgule(annonce_ex, signe=True)} €   réel {virgule(reel_ex, signe=True)} €")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
portage 90 j à 8 % : 1972,60 €   intérêts 90 j à 10 % : 2465,75 €   net si le client paie : +493,15 €
seuil de paiement p* = 0,8   espérance au seuil : 0,00 €
Jev annonce 0,85 : +123,29 €   Jev juste 75 % du temps : -123,29 €
hybride Jev + Opus : 38 % du coût d'Opus seul   Haiku avec réflexion : 10,6 fois plus lent   écart Opus 5.5 − Jev : 7,4 points   prix d'entrée Haiku / Jev : 2,4
exercice 1 : C = 2876,71 €   I = 4931,51 €   p* = 0,583
exercice 3 : annoncé +575,34 €   réel -312,33 €
OK — toutes les vérifications sont passées.
```

---

## 6. Exercices à refaire sur feuille blanche

### Exercice 1 — recalculer le portage et les intérêts

Une facture de 250 000 € est impayée. On envisage un report de 60 jours. Le portage coûte 7 % par an, et les intérêts de retard sont de 12 % par an. Calcule C, I et le seuil p\*.

**Corrigé.**

$$
C = 250\,000 \times 0{,}07 \times \frac{60}{365} \approx 2\,876{,}71\ \text{€}
$$

$$
I = 250\,000 \times 0{,}12 \times \frac{60}{365} \approx 4\,931{,}51\ \text{€}
$$

$$
p^{*} = \frac{0{,}07}{0{,}12} \approx 0{,}583
$$

Le report rapporte en moyenne dès que le client a plus de 58,3 % de chances de payer.

### Exercice 2 — démontrer le seuil

Sans regarder la section 3.5, démontre que le seuil p\* ne dépend ni du montant M ni de la durée j.

**Corrigé.** On écrit le gain moyen E = p·(I − C) + (1 − p)·(−C), qui se simplifie en p·I − C. On remplace I et C par leurs formules. M et j/365 se mettent en facteur :

$$
E = M \cdot \frac{j}{365} \cdot (p\,r_i - r_p)
$$

Ce facteur est positif, donc le signe de E est celui de la parenthèse. E est positif exactement quand p ≥ rₚ / rᵢ. M et j n'y figurent pas.

### Exercice 3 — la calibration

Pour la facture de l'exercice 1, Jev annonce 0,70. Mais sur les 200 dernières factures de l'entreprise, ses 0,70 n'ont été justes que 52 % du temps. Que décides-tu ?

**Corrigé.** Avec la formule factorisée de l'exercice 2 :

$$
E_{\text{annoncée}} = 250\,000 \times \frac{60}{365} \times (0{,}70 \times 0{,}12 - 0{,}07) \approx +575{,}34\ \text{€}
$$

$$
E_{\text{réelle}} = 250\,000 \times \frac{60}{365} \times (0{,}52 \times 0{,}12 - 0{,}07) \approx -312{,}33\ \text{€}
$$

On refuse le report : la probabilité réelle, 0,52, est sous le seuil de 0,583. Le 0,70 de Jev ne doit entrer dans le calcul qu'après correction par sa calibration mesurée.

### Exercice 4 — le droit avant la caution

Cite trois démarches qui viennent normalement avant l'appel de la garantie de paiement, pour un marché privé de travaux en France.

**Corrigé.** La mise en demeure ; la suspension des travaux quinze jours après une mise en demeure restée sans effet, si la garantie de l'article 1799-1 n'a pas été fournie ; l'injonction de payer. On peut aussi proposer un échéancier. Les pénalités de retard et l'indemnité de 40 € sont dues d'office et n'ont pas à être négociées.

---

## 7. À corriger dans JEV Utility Assessment.md

Dans [JEV Utility Assessment.md](<../../JEV Utility Assessment.md>), entre les lignes 35 et 58, les formules mélangent les délimiteurs `\(` et `\)` avec les blocs maths. Typora n'affiche rien de correct.

La correction : un bloc maths par formule et par symbole, seul sur ses lignes, en colonne 0, avec une ligne vide avant et après, comme dans la section 3.3 de cette review.

---

## 8. Sources

**Jev et TypeSafe**

- [Eden AI — Jev, un modèle fait pour décider](https://www.edenai.co/post/jev-a-new-kind-of-ai-model-built-for-decisions-not-conversation)
- [Wavect — revue de Jev (types de questions, limites, confidentialité)](https://wavect.io/blog/jev-ai-decision-model-review/)
- [The Neuron — TypeSafe Jev expliqué](https://www.theneuron.ai/explainer-articles/typesafe-jev-system-one-models-explained/)
- [eesel — tarifs de Jev](https://www.eesel.ai/fr/blog/typesafe-jev-tarifs)

**Tests et comparaisons**

- [Vincent van Deth — Jev, OpenAI Decisions et Haiku 5.5](https://vincentvandeth.nl/blog/jev-vs-openai-decisions-api-vs-haiku-5-5-benchmark)
- [haiku-decides — Haiku 5.5 comme modèle de décision](https://github.com/Kungie/haiku-decides)
- [AIMLAPI — Jev contre six LLM](https://aimlapi.com/blog/what-is-jev)
- [Mastra — les modèles de décision et le contexte long](https://mastra.ai/research/decision-models-context-rot)
- [arXiv 2609.27678 — Same Scores, Different Decisions](https://arxiv.org/abs/2609.27678)
- [jev-router-bench — banc de routage en russe, sans résultats publiés](https://github.com/feD0s/jev-router-bench)

**Gemini Decision 1**

- [Let's Data Science — lancement de l'API Gemini Decisions](https://letsdatascience.com/news/google-deepmind-launches-gemini-decisions-api-for-fast-multi-f88f4710)
- [VentureBeat — Gemini Decision 1](https://venturebeat.com/technology/googles-gemini-decision-1-model-scores-up-to-1-000-questions-in-one-api-call)
- [DataCamp — Gemini Decision 1, benchmarks et prix](https://www.datacamp.com/blog/gemini-decision-1)

**Frameworks d'agents**

- [AI Weekly — LangGraph en tête](https://aiweekly.co/alerts/langgraph-leads-as-88-of-ai-agent-projects-fail)
- [Alice Labs — les frameworks d'agents en 2026](https://alicelabs.ai/en/insights/best-ai-agent-frameworks-2026)

**Prix de Claude Haiku 5.5** : tarif officiel Anthropic, 0,10 USD par million de jetons d'entrée et 0,50 USD par million de jetons de sortie, jusqu'à 100 000 jetons.
