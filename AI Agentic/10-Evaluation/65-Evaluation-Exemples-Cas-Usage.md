# Étape 65 — Évaluation — Exemples et cas d'usage

> Étape 65 du parcours · Prérequis : [Théorèmes de fidélité, pertinence et F1](<64b-Theoremes-Fidelite-Pertinence-et-F1.md>) · Suite : [Classement par duels : Elo et Bradley-Terry](<65b-Classement-par-Duels-Elo-Bradley-Terry.md>)

**Dossier :** 10-Evaluation  
**Métiers :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers

Ce fichier assemble les métriques du chapitre dans un **harnais d'évaluation de bout en bout**, écrit en Python standard. Le protocole lui-même (jeu de développement et jeu de test, essais répétés, intervalle de Wilson, test de McNemar, barrière d'intégration continue) a été posé à l'étape 13 bis ; on le reprend ici sans le redémontrer, et l'on y renvoie. Ce qui est nouveau : un jeu de référence de 70 cas répartis sur sept domaines des Émirats, un agent qui passe par la vraie boucle de l'étape 1 avec de vrais outils, trois métriques calculées sur chaque cas (réussite de la tâche, Tool Call F1, fidélité approchée), et une barrière qui **renvoie** un code de sortie au lieu de quitter le programme. La version candidate de l'agent contient trois défauts plantés exprès ; l'enjeu est de voir quelle métrique attrape lequel.

## Ce que mesure chaque métrique, et ce qu'elle ne voit pas

| Métrique | Question posée | Étape | Calcul dans le harnais | Ce qu'elle ne voit pas |
|---|---|---|---|---|
| Réussite de la tâche (Goal Accuracy) | la tâche est-elle accomplie ? | 60 | un critère vérifiable par cas, codé dans le cas | une invention à côté d'un montant juste ; un mauvais chemin qui tombe juste |
| Tool Call F1 | les bons outils, avec les bons arguments ? | 59 | F1 sur les multi-ensembles de couples (nom, arguments en JSON trié) | ce que l'agent écrit après les outils |
| Fidélité approchée | les nombres cités viennent-ils des sources ? | 54 | part des nombres de la réponse présents dans le prompt système, la question ou les sorties d'outils | une affirmation sans nombre ; un nombre juste mal utilisé |
| Intervalle de Wilson | quelle confiance accorder au taux de réussite ? | 7 et 13 bis | borne basse à 95 % | la répartition des échecs par domaine |
| McNemar | la candidate régresse-t-elle sur les mêmes cas ? | 13 bis | paires discordantes, correction de continuité | une régression concentrée sur une petite catégorie |

## Fonction de score, métrique d'évaluation, seuil : trois objets différents

Une **fonction de score** est calculée par l'agent ou par un outil, en production, pour prendre une décision : le ratio d'endettement, une estimation en AED par sqft. Une **métrique d'évaluation** est calculée après coup, sur le jeu de référence, pour juger l'agent : la réussite de la tâche, la Tool Call F1. Un **seuil** transforme un nombre en décision, et il y en a deux sortes qu'il ne faut pas confondre : le seuil métier, utilisé par la fonction de score (50 % pour l'endettement), et le seuil de barrière, utilisé par l'évaluation (une borne basse d'au moins 0,85). Les seuils de barrière ci-dessous sont illustratifs.

| Domaine | Fonction de score (agent, outil) | Seuil métier | Critère de réussite du cas | Métriques qui comptent le plus | Seuil de barrière |
|---|---|---|---|---|---|
| Banque | toutes les mensualités, nouvelle comprise, divisées par le revenu | 50 % (CBUAE) | verdict « recevable » si et seulement si le ratio de référence est sous le plafond | réussite, Tool Call F1 | borne basse ≥ 0,85 ; F1 ≥ 0,95 |
| Immobilier | surface multipliée par le prix médian des comparables en AED/sqft | aucun | erreur relative au prix réel ≤ 10 % | réussite | borne basse ≥ 0,85 |
| Crypto | réserve du pool comparée au seuil de liquidité | 2 000 000 USD | même état (alerte ou normal) que la référence | réussite | borne basse ≥ 0,85 |
| Assurance | réparation diminuée de la vétusté, moins la franchise, jamais négative | aucun | indemnité exacte | réussite, Tool Call F1 | F1 ≥ 0,95 |
| RH | indemnité de fin de service, 21 puis 30 jours par an, plafond de 24 mois | aucun | montant exact | réussite, fidélité | fidélité ≥ 0,95 |
| BTP | TVA de 5 % du hors taxe, total toutes taxes comprises | 5 % | total exact, boucle terminée | réussite | borne basse ≥ 0,85 |
| Secteur public | statut de la demande lu dans le système de référence | aucun | même statut que le système | réussite | borne basse ≥ 0,85 |

Deux règles s'ajoutent pour tous les domaines : aucune catégorie ne perd plus de 5 points par rapport à la production, et un test de McNemar significatif (χ² > 3,84 avec plus de cas perdus que gagnés) bloque le déploiement.

## Démonstration

### 1. « ±10 % » se mesure sur le prix réel, pas autour de l'estimation

L'ancienne version de ce fichier disait « l'objectif est atteint si la fourchette est correcte à ±10 % », sans dire autour de quoi. Notons p le prix réel de la transaction et p̂ l'estimation de l'agent. Le critère retenu est l'erreur relative au prix réel :

$$
\frac{|\hat p - p|}{p} \le 0{,}10 \iff 0{,}9\,p \le \hat p \le 1{,}1\,p
$$

On passe de l'un à l'autre en multipliant par p > 0, puis en écrivant la valeur absolue comme deux inégalités. L'autre lecture, « le prix réel tombe dans une fourchette de ±10 % autour de l'estimation », s'écrit 0,9 p̂ ≤ p ≤ 1,1 p̂, c'est-à-dire p̂ entre p/1,1 ≈ 0,909 p et p/0,9 ≈ 1,111 p : ce n'est pas le même intervalle. Avec p = 2 450 000 AED et p̂ = 2 205 000 AED, l'erreur relative vaut exactement 0,10 et le cas est réussi selon la première lecture ; la fourchette autour de l'estimation, de 1 984 500 à 2 425 500 AED, ne contient pas le prix réel, et le cas échoue selon la seconde. Deux équipes qui lisent la consigne différemment publient donc deux taux de réussite différents pour le même agent.

Dans le harnais, le prix réel vaut le prix estimé multiplié par un facteur de marché f. L'erreur relative vaut alors |1 − f| / f = |1/f − 1|, qui est au plus 0,10 si et seulement si 1/1,1 ≤ f ≤ 1/0,9, soit 0,909 ≤ f ≤ 1,111. Les facteurs 1,12 et 0,89 sortent de cet intervalle : ce sont les deux échecs immobiliers, pour les deux versions de l'agent, alors que l'outil a fait exactement son travail.

### 2. Combien de cas faut-il pour prouver un taux ?

Si les n cas réussissent tous, l'estimation vaut p̂ = 1 et le terme p̂(1 − p̂) de la formule de Wilson (étape 7) s'annule. Le centre de l'intervalle vaut (1 + z²/2n)/(1 + z²/n), la demi-largeur vaut (z²/2n)/(1 + z²/n), et leur différence se simplifie :

$$
\text{borne basse}(n \text{ sur } n) = \frac{1}{1 + z^2/n} = \frac{n}{n + z^2}
$$

Avec z = 1,96, donc z² = 3,8416, sept cas parfaits ne prouvent qu'un taux de 7/10,8416 ≈ 0,646. Pour qu'une barrière à τ puisse passer, il faut au minimum

$$
\frac{n}{n + z^2} \ge \tau \iff n \ge \frac{\tau\, z^2}{1 - \tau}
$$

soit 16 cas parfaits pour τ = 0,80 (4 × 3,8416 ≈ 15,37) et 73 pour τ = 0,95 (19 × 3,8416 ≈ 72,99). C'est pourquoi le harnais utilise 70 cas, dix par domaine, et compare toujours la **borne basse** au seuil : la production réussit 68 cas sur 70 (0,971, borne basse 0,902), la candidate 59 sur 70 (0,843, borne basse 0,740).

### 3. McNemar sur les paires discordantes

On ne redémontre pas le test, présenté à l'étape 13 bis ; on l'applique. Sur les 70 cas, la production réussit et la candidate échoue sur 9 cas (7 en assurance, 2 en BTP), et l'inverse n'arrive jamais. D'où

$$
\chi^2 = \frac{(|9 - 0| - 1)^2}{9 + 0} = \frac{64}{9} \approx 7{,}11 > 3{,}84
$$

La régression est significative. Les 61 cas sur lesquels les deux versions sont d'accord n'apportent aucune information sur leur différence, et c'est ce qui rend le test apparié plus sensible qu'une comparaison des deux taux globaux.

### 4. Chaque défaut n'est vu que par certaines métriques

La candidate B contient trois défauts. Le tableau donne ce que chaque métrique en dit, sur les cas où le défaut se produit :

| Défaut planté dans B | Réussite | Tool Call F1 | Fidélité approchée | Qui le voit |
|---|---|---|---|---|
| oublie la vétusté en assurance (7 cas sur 10) | échec | 0 | 1 | réussite, Tool Call F1 |
| invente une prime de 2 500 AED en RH (10 cas) | succès | 1 | 0,5 | fidélité seulement |
| rappelle le même outil en BTP (2 cas) | échec (arrêt « boucle ») | 1 | indéfinie | réussite seulement |

Trois enseignements. La fidélité vaut 1 sur l'indemnité fausse, parce que le nombre faux vient bien de l'outil, appelé avec un mauvais argument : la fidélité mesure l'accord avec les sources, pas la justesse. La réussite de la tâche est parfaite en RH, parce que le montant attendu est juste : seule la fidélité voit l'invention. Et la Tool Call F1 vaut 1 sur la boucle, parce que la boucle canonique s'arrête **avant** d'exécuter le second appel identique : la trace ne contient qu'un appel. Sur toute la candidate, la Tool Call F1 moyenne vaut 63/70 = 0,900 (sept zéros) et la fidélité moyenne 63/68 ≈ 0,926 (les deux cas sans réponse sont exclus, ni 0 ni 1). Aucune métrique ne suffit seule : c'est la raison d'une barrière à plusieurs conditions.

## Construire le harnais depuis une feuille blanche

Le programme réutilise tel quel le port LLM et la boucle `executer_agent` du code canonique (étape 1). Seul le modèle est remplacé : `FauxLLMPlan` a la même méthode `create(system=…, messages=…, tools=…)` que le faux LLM du parcours et que l'adaptateur Claude (étape 13), mais au lieu de réciter un script fixe, il joue un plan d'appels d'outils puis rédige sa réponse **à partir des `tool_result` qu'il a réellement reçus**. Les outils sont de vraies fonctions déterministes, avec des données illustratives. Le harnais fait passer les 70 cas aux deux versions, calcule les métriques, puis la barrière.

### Déroulé, ligne par ligne

**Le port LLM et `executer_agent`** sont recopiés du code canonique : `Bloc`, `Reponse`, `texte`, `appel_outil`, puis la boucle et ses trois arrêts. Le point qui compte ici est l'arrêt « boucle » : avant d'exécuter les appels d'une réponse, la boucle calcule leur signature `(nom, json.dumps(arguments, sort_keys=True))` et la compare à celle de l'étape précédente ; si elles sont égales, elle rend la main avec le statut `"boucle"` sans exécuter le second appel.

**`FauxLLMPlan(plan, rediger)`** garde un compteur `appels`. Tant que ce compteur ne dépasse pas la longueur du plan, `create` renvoie une `Reponse("tool_use", …)` qui contient l'appel prévu, avec un identifiant `t1`, `t2`… Ensuite, il parcourt `messages`, garde les messages `user` dont le contenu est une liste (ce sont les résultats d'outils, que la boucle range dans un seul message par étape), décode chaque `content` avec `json.loads`, et passe la liste des sorties à `rediger`, qui écrit la réponse finale. Pour banque-00, `rediger` reçoit `[3334.99, 0.2112]` et écrit « Mensualité 3334.99 AED ; endettement 21.12 % : dossier recevable. ».

**Les outils** sont des fonctions pures. `mensualite` et `ratio_endettement` reprennent les formules canoniques et arrondissent à 2 et 4 décimales ; `estimer_bien` lit le prix médian dans `PRIX_SQFT` et multiplie par la surface, pour que l'agent n'ait jamais à faire le calcul de tête ; `liquidite_pool` et `statut_demande` lisent des tables simulées ; `indemnite_sinistre`, `fin_de_service` et `facture_tva` appliquent les règles du domaine. `OUTILS` les rassemble par nom, comme le registre de l'étape 12. `SYSTEME` contient les règles chiffrées (50 %, 5 %, 10 %), qui font partie des sources de la fidélité.

**`Cas`** regroupe l'identifiant, la catégorie, la question, le plan attendu (la liste ordonnée des appels corrects), la fonction `rediger` qui écrit la bonne réponse, et la fonction `reussite`, critère vérifiable au sens de l'étape 13 bis. Les sept fabriques `cas_banque` … `cas_public` construisent dix variantes chacune à partir de l'indice `i`. Dans `cas_banque`, le verdict de référence `recevable` est calculé à part, en appelant les outils de référence, et `reussite` vérifie que la réponse contient « recevable » exactement quand ce verdict est vrai. Dans `cas_immo`, `prix_reel` vaut l'estimation multipliée par `FACTEURS_MARCHE[i]`, et `reussite` extrait le montant avec `nombre_apres("Estimation : ", …)` puis vérifie `erreur_relative(est, prix_reel) <= 0.10`. Chaque critère commence par `res["statut"] == "fini"` : un arrêt sur boucle ou sur refus est un échec.

**`politique(version, cas)`** renvoie le plan et la fonction de rédaction de la version demandée. Pour A, c'est le plan attendu. Pour B, trois défauts : en assurance, si la vétusté est non nulle, `dict(args, vetuste=0.0)` remplace l'argument ; en RH, une nouvelle fonction `rediger` ajoute une prime inventée à la réponse correcte (le paramètre par défaut `base=cas.rediger` fige la fonction d'origine) ; en BTP, pour les variantes 0 et 5, `plan * 2` répète le même appel.

**`tool_call_f1(attendus, reels)`** construit deux `Counter` de clés `cle_appel(nom, args)`, prend l'intersection `a & r`, qui garde le plus petit compte de chaque clé, et renvoie 2 × TP / (|attendus| + |réels|), ou `None` si les deux listes sont vides. Pour assur-01 sous B, la clé réelle contient `"vetuste": 0.0` et la clé attendue `"vetuste": 0.1` : l'intersection est vide et la F1 vaut 0.

**`nombres(t)`** et **`fidelite_approchee(reponse, sources)`** forment l'approximation de la fidélité. L'expression régulière capture chaque nombre et un éventuel « % » qui le suit ; « 21.12 % » devient 0,2112, la valeur que renvoie l'outil. La fidélité est la part des nombres cités qui apparaissent, à `math.isclose` près, parmi les nombres des sources ; elle vaut `None` si la réponse ne cite aucun nombre. Pour rh-00 sous B, les nombres cités sont 5600.00 (présent dans la sortie de l'outil) et 2500 (absent partout) : 1/2 = 0,5.

**`evaluer(cas_list, version)`** fait tourner la boucle sur chaque cas avec `FauxLLMPlan(*politique(version, cas))`, extrait la liste des appels de la trace, assemble les sources (prompt système, question, sorties d'outils sérialisées en JSON), et range pour chaque cas le statut, les outils appelés, la réussite, la F1 et la fidélité, cette dernière à `None` si la boucle n'a pas fini.

**`rapport(resultats)`** compte les succès, calcule le taux et l'intervalle de `wilson`, le taux par catégorie, et les moyennes de F1 et de fidélité avec `moyenne_definie`, qui ignore les `None` au lieu de les compter comme 0.

**`mcnemar(res_prod, res_cand)`** reprend la fonction de l'étape 13 bis, appariée par identifiant de cas : `perdus` compte les cas réussis par la production et ratés par la candidate, `gagnes` l'inverse.

**`barriere_ci(res_prod, res_cand, seuils)`** calcule les deux rapports et McNemar, puis ajoute un motif lisible pour chaque condition violée : borne basse de Wilson, perte de plus de 5 points dans une catégorie (parcourues dans l'ordre alphabétique par `sorted` pour que la sortie soit stable), régression significative, Tool Call F1 et fidélité sous leur seuil. Elle renvoie `(1, motifs)` s'il y a au moins un motif, `(0, [])` sinon. Elle n'appelle jamais `sys.exit` : c'est le script de CI qui le fait, avec le code renvoyé (extrait plus bas). La démonstration peut donc vérifier le code par `assert` sans que le programme s'arrête.

**`main()`**, bloc par bloc.

1. Les traces de sept cas de la candidate, un par domaine, choisis pour montrer chaque comportement. Les `assert` vérifient les trois défauts : F1 nulle et fidélité 1 pour assur-01, réussite et fidélité 0,5 pour rh-00, statut « boucle » et fidélité indéfinie pour btp-00 ; et que la production elle-même échoue sur immo-06 et immo-09.
2. Les deux rapports : 68/70 et 59/70, avec leurs intervalles, la F1 moyenne (1 et 63/70) et la fidélité moyenne (1 et 63/68).
3. Le taux par catégorie, puis McNemar : 9 perdus, 0 gagné, χ² = 64/9.
4. La barrière sur la candidate renvoie le code 1 avec six motifs ; la production rejouée contre elle-même renvoie 0 et aucun motif.
5. Les contrôles de la démonstration : le cas à exactement 10 % d'erreur est accepté mais sort d'une fourchette autour de l'estimation ; la borne basse de 7 sur 7 vaut 7/(7 + 1,96²) ≈ 0,646 ; le plus petit n qui prouve 80 % vaut 16 ; une F1 sans aucun appel et une réponse sans nombre donnent `None`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`texte(t)`** — Cette petite fonction du port LLM canonique est l'imprimeur qui compose une réplique prête à être glissée dans une réponse du modèle : elle reçoit une chaîne et renvoie un `Bloc` de type `"text"` qui la porte, sans identifiant ni nom d'outil, sans rien vérifier. Dans ce harnais, c'est `FauxLLMPlan.create` qui l'appelle, au dernier tour, pour emballer la réponse finale écrite par `rediger`, par exemple « Mensualité 3334.99 AED ; endettement 21.12 % : dossier recevable. » pour le cas banque-00.

**`appel_outil(nom, arguments, id_)`** — Celle-ci fabrique le bon de commande qu'un modèle adresse à un outil : elle reçoit le nom de l'outil, le dictionnaire de ses arguments et un identifiant d'appel, et renvoie un `Bloc` de type `"tool_use"` qui réunit ces trois informations, sans aucune vérification. `FauxLLMPlan.create` s'en sert à chaque étape du plan, avec les identifiants `t1`, `t2` et ainsi de suite, si bien que la boucle reçoit exactement la même forme de demande qu'elle recevrait d'un vrai modèle.

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — Cette fonction est la boucle canonique de l'agent, recopiée sans changement, un chef de chantier qui demande au modèle quoi faire, fait travailler les outils et rapporte les résultats jusqu'à la fin du travail : elle reçoit le modèle, le prompt système, la question, le registre des outils, leurs schémas et un maximum de 8 étapes. À chaque tour, elle appelle `create`, range la réponse telle quelle, s'arrête sur un refus, une troncature ou un `end_turn` en recollant le texte final, saute un `pause_turn`, puis compare la signature des appels à celle du tour précédent et rend la main avec le statut « boucle » si elle est identique, sans exécuter le second appel. Sinon, elle exécute chaque appel, transforme une exception en résultat marqué `is_error` et renvoie tous les résultats dans un seul message ; elle renvoie un dictionnaire avec le statut, la trace et le nombre d'étapes, et c'est cet arrêt « boucle » qui fait échouer les cas btp-00 et btp-05 de la candidate.

**`FauxLLMPlan.__init__(plan, rediger)`** — Le constructeur prépare un comédien qui connaît le déroulé de la scène mais improvise sa dernière réplique d'après ce qu'il entend : il reçoit le plan, la liste ordonnée des appels d'outils à jouer, en garde une copie, mémorise la fonction `rediger` qui écrira la réponse finale à partir des sorties d'outils, et met à zéro le compteur `appels`. Il ne renvoie rien ; `evaluer` en crée un neuf pour chaque cas, avec le plan et la rédaction que `politique` choisit selon la version A ou B.

**`FauxLLMPlan.create(system, messages, tools)`** — Cette méthode est la réplique du comédien à chaque tour de la boucle : elle reçoit, comme l'API d'un vrai modèle, le prompt système, l'historique et les schémas d'outils, augmente son compteur, et tant que celui-ci ne dépasse pas la longueur du plan, renvoie une réponse `"tool_use"` qui contient l'appel prévu à ce rang. Ensuite, elle parcourt l'historique, garde les messages de rôle `"user"` dont le contenu est une liste de résultats d'outils, décode chaque résultat non marqué en erreur avec `json.loads`, passe la liste des sorties à `rediger` et renvoie une réponse `"end_turn"` qui porte ce texte : pour banque-00, `rediger` reçoit [3334,99 ; 0,2112].

**`mensualite(principal, taux_annuel, n_mois)`** — Cet outil est le banquier qui calcule la mensualité d'un prêt amortissable : il reçoit le capital, le taux annuel et la durée en mois, prend le taux mensuel r = taux ÷ 12, renvoie capital ÷ durée si ce taux est nul et sinon la formule de l'annuité, capital × r ÷ (1 − (1 + r)⁻ⁿ), arrondie au centime. Pour 600 000 AED à 4,5 % sur 300 mois, il renvoie 3 334,99 AED, la première étape du plan de chaque cas bancaire, avant le calcul du ratio d'endettement.

**`ratio_endettement(existantes, nouvelle, revenu)`** — Celui-ci est l'analyste de crédit qui additionne toutes les charges d'un emprunteur avant de les rapporter à son revenu : il reçoit les mensualités déjà existantes, la nouvelle mensualité et le revenu mensuel, et renvoie (existantes + nouvelle) ÷ revenu arrondi à quatre décimales, sans aucune vérification. Pour banque-00, 3 000 AED existants et 3 334,99 AED nouveaux sur un revenu de 30 000 AED donnent 0,2112, soit 21,12 %, sous le plafond de 50 % du prompt système, et le dossier est recevable.

**`estimer_bien(zone, chambres, surface_sqft)`** — Cet outil est l'expert immobilier qui consulte sa grille de prix au lieu de deviner : il reçoit la zone, le nombre de chambres et la surface en pieds carrés, lit le prix médian au pied carré dans la table `PRIX_SQFT`, ce qui lève une `KeyError` pour un couple inconnu, et renvoie un dictionnaire avec ce prix et l'estimation, prix × surface. Pour immo-00, un appartement d'une chambre de 700 sqft dans la zone dubai_marina, à 1 650 AED le pied carré, est estimé à 1 155 000 AED ; l'agent n'a jamais à faire ce calcul de tête.

**`liquidite_pool(pool)`** — Celui-ci est le trésorier qui ouvre le registre des réserves d'un pool de liquidité : il reçoit le nom du pool, lit sa réserve dans la table simulée `RESERVES`, ce qui lève une `KeyError` pour un pool inconnu, et renvoie un dictionnaire avec cette réserve en dollars et le seuil fixe de 2 000 000. Les réserves vont de 1 500 000 pour AED-USDT-0 à 2 400 000 pour AED-USDT-9, si bien que les cinq premiers pools sont en alerte et les cinq derniers en état normal.

**`indemnite_sinistre(reparation, franchise, vetuste)`** — Cet outil est l'expert d'assurance qui applique la règle de l'indemnisation : il reçoit le coût de la réparation, la franchise et le taux de vétusté, retire d'abord la part de vétusté du coût, puis la franchise, ne descend jamais sous zéro et arrondit au centime. Pour assur-01, 9 000 AED de réparation, 500 de franchise et 10 % de vétusté donnent 7 600 AED ; la version candidate, qui passe la vétusté à 0, obtient 8 500 AED, un montant faux qui vient pourtant bien de l'outil.

**`fin_de_service(salaire_base_mensuel, annees)`** — Celui-ci est le responsable de la paie qui calcule l'indemnité de fin de service : il reçoit le salaire de base mensuel et l'ancienneté en années, renvoie 0 sous un an, puis compte 21 jours de salaire par an pour les cinq premières années et 30 jours au-delà, sur la base d'un salaire journalier égal au mensuel divisé par 30, et plafonne le total à 24 mois de salaire avant d'arrondir. Pour rh-00, 8 000 AED et un an donnent 5 600 AED ; pour rh-09, 17 000 AED et dix ans donnent 144 500 AED, loin du plafond.

**`facture_tva(montant_ht)`** — Cet outil est le comptable de chantier qui établit la facture d'un sous-traitant : il reçoit le montant hors taxe et renvoie un dictionnaire avec la TVA à 5 % et le total TTC, tous deux arrondis au centime, sans aucune vérification. Pour btp-00, 100 000 AED HT donnent 5 000 AED de TVA et 105 000 AED TTC, le nombre que le critère de réussite du cas va chercher après « TTC : ».

**`statut_demande(reference)`** — Celui-ci est le guichet d'un service public qui retrouve un dossier par sa référence : il reçoit une référence de la forme REQ-2026-0100, lit son statut dans la table simulée `STATUTS`, ce qui lève une `KeyError` pour une référence inconnue, et renvoie un dictionnaire avec la référence et ce statut. Les statuts tournent sur « approuvée », « en cours » et « refusée » selon le reste de la division de l'indice par 3 : REQ-2026-0100 est approuvée, REQ-2026-0101 en cours.

**`nombre_apres(motif, reponse)`** — Cette fonction est le correcteur qui pose le doigt sur une étiquette de la réponse et lit le nombre qui la suit : elle reçoit un motif, comme « Estimation : » ou « TTC : », et le texte de la réponse, cherche avec une expression régulière ce motif suivi d'un nombre, entier ou décimal, et renvoie ce nombre en flottant, ou `None` s'il est introuvable. Les critères de réussite des cas immobilier, assurance, RH et BTP s'en servent pour comparer le montant annoncé au montant attendu.

**`erreur_relative(estimation, prix_reel)`** — Celle-ci est l'arbitre de la tolérance de 10 % du prompt système, qui mesure l'écart par rapport au prix réel et non à l'estimation : elle reçoit une estimation et un prix réel, lève une `ValueError` si ce prix n'est pas strictement positif, et renvoie la valeur absolue de leur différence divisée par le prix réel. Une estimation de 2 205 000 face à un prix réel de 2 450 000 donne exactement 0,10 et passe, alors qu'elle sortirait d'une fourchette de ±10 % autour de l'estimation ; pour immo-06 et immo-09, l'écart dépasse 10 % et même la production échoue.

**`cas_banque(i)`** — Cette fabrique est le rédacteur d'un dossier d'examen bancaire, qui écrit une variante nouvelle pour chaque indice : elle reçoit l'indice i, de 0 à 9, calcule le capital, 600 000 + 100 000 i, le revenu, 30 000 + 2 000 i, et les mensualités existantes, 3 000 + 1 500 i, puis appelle elle-même les outils de référence pour connaître le verdict « recevable » attendu. Elle construit le plan de deux appels, `mensualite` puis `ratio_endettement`, la question, et deux fonctions internes, puis renvoie un `Cas` nommé banque-00 à banque-09.

**`rediger(s)`** — Cette fonction interne, qui vit dans `cas_banque`, est la plume qui rédige la bonne réponse à partir des sorties d'outils : elle reçoit la liste des sorties, la mensualité puis le ratio, choisit le verdict « recevable » si le ratio ne dépasse pas 0,50 et « refusé » sinon, et renvoie une phrase qui cite la mensualité, le ratio en pourcentage à deux décimales et le verdict, comme « Mensualité 3334.99 AED ; endettement 21.12 % : dossier recevable. ».

**`reussite(res)`** — Cette fonction interne, qui vit dans `cas_banque`, est le critère vérifiable du cas : elle reçoit le résultat de la boucle, exige d'abord que le statut soit « fini », puis vérifie que le mot « recevable » apparaît dans la réponse exactement quand le verdict de référence calculé par la fabrique est vrai. Elle renvoie un booléen ; un arrêt sur boucle ou sur refus vaut échec, et un verdict inversé aussi, même si la phrase est bien tournée.

**`cas_immo(i)`** — Cette fabrique prépare une demande d'estimation immobilière pour chaque indice : elle reçoit i, alterne la zone entre dubai_marina et jvc, fait tourner le nombre de chambres de 1 à 3, fixe la surface à 700 + 150 i pieds carrés, et calcule le prix réel en multipliant l'estimation de la grille par le facteur de marché `FACTEURS_MARCHE[i]`, de 0,89 à 1,12. Elle renvoie un `Cas` nommé immo-00 à immo-09, avec un plan d'un seul appel à `estimer_bien`, ses deux fonctions internes et la question.

**`rediger(s)`** — Cette fonction interne, qui vit dans `cas_immo`, est la plume de l'expert qui recopie l'avis de valeur : elle reçoit la liste des sorties d'outils, dont la première est le dictionnaire renvoyé par `estimer_bien`, et renvoie la phrase « Estimation : … AED (… AED/sqft). », qui cite l'estimation et le prix au pied carré, par exemple 1 155 000 AED et 1 650 AED/sqft pour immo-00.

**`reussite(res)`** — Cette fonction interne, qui vit dans `cas_immo`, compare l'estimation annoncée au prix réel du marché : elle reçoit le résultat de la boucle, lit avec `nombre_apres` le nombre qui suit « Estimation : », et renvoie vrai seulement si le statut est « fini », si ce nombre existe et si son erreur relative au prix réel ne dépasse pas 0,10. Pour immo-06, estimé à 2 640 000 AED alors que le marché est à 1,12 fois ce montant, le critère échoue, même pour la production.

**`cas_crypto(i)`** — Cette fabrique prépare une question de surveillance de liquidité pour chaque indice : elle reçoit i, forme le nom du pool AED-USDT-i, détermine l'état attendu, « alerte » si la réserve de la table est sous 2 000 000 et « normal » sinon, et renvoie un `Cas` nommé crypto-00 à crypto-09, avec un plan d'un seul appel à `liquidite_pool`, la question et ses deux fonctions internes.

**`rediger(s)`** — Cette fonction interne, qui vit dans `cas_crypto`, est le trésorier qui lit son registre à voix haute : elle reçoit la liste des sorties d'outils, compare la réserve au seuil du premier résultat pour choisir « alerte » ou « normal », et renvoie la phrase « Réserve … USD, seuil … USD : … », par exemple « Réserve 1500000 USD, seuil 2000000 USD : alerte. » pour crypto-00.

**`reussite(res)`** — Cette fonction interne, qui vit dans `cas_crypto`, est le contrôleur qui ne regarde que la conclusion : elle reçoit le résultat de la boucle et renvoie vrai si le statut est « fini » et si la réponse se termine exactement par deux points, une espace, l'état attendu calculé par la fabrique et un point final. Une réponse qui annoncerait « normal » pour un pool sous son seuil serait donc un échec, quelle que soit la qualité du reste de la phrase.

**`cas_assur(i)`** — Cette fabrique prépare un dossier de sinistre automobile pour chaque indice : elle reçoit i, fixe la réparation à 8 000 + 1 000 i AED, la franchise à 500 AED et la vétusté à 0, 10, 20 ou 30 % selon le reste de i divisé par 4, calcule l'indemnité attendue avec `indemnite_sinistre`, et renvoie un `Cas` nommé assur-00 à assur-09, avec un plan d'un seul appel et ses deux fonctions internes. Ce sont les sept cas à vétusté non nulle que la candidate B fait échouer.

**`rediger(s)`** — Cette fonction interne, qui vit dans `cas_assur`, est la plume du gestionnaire de sinistres : elle reçoit la liste des sorties d'outils, dont la première est le montant calculé par `indemnite_sinistre`, et renvoie la phrase « Indemnité : … AED. » avec ce montant à deux décimales. Comme elle recopie fidèlement la sortie de l'outil, la fidélité approchée vaut 1 même quand l'outil a été appelé avec une vétusté fausse, ce qui est tout l'enseignement du cas assur-01.

**`reussite(res)`** — Cette fonction interne, qui vit dans `cas_assur`, compare le montant annoncé au montant de référence : elle reçoit le résultat de la boucle et renvoie vrai si le statut est « fini » et si le nombre lu après « Indemnité : » par `nombre_apres` est exactement l'indemnité attendue. Pour assur-01, la candidate annonce 8 500 AED au lieu de 7 600, et le critère échoue, comme la Tool Call F1, alors que la fidélité ne voit rien.

**`cas_rh(i)`** — Cette fabrique prépare une demande d'indemnité de fin de service pour chaque indice : elle reçoit i, fixe le salaire de base à 8 000 + 1 000 i AED et l'ancienneté à 1 + i années, calcule l'indemnité attendue avec `fin_de_service`, et renvoie un `Cas` nommé rh-00 à rh-09, avec un plan d'un seul appel, la question et ses deux fonctions internes. C'est dans ces dix cas que la candidate B invente une prime.

**`rediger(s)`** — Cette fonction interne, qui vit dans `cas_rh`, est la plume du service de paie : elle reçoit la liste des sorties d'outils, dont la première est le montant calculé par `fin_de_service`, et renvoie la phrase « Indemnité de fin de service : … AED. » avec ce montant à deux décimales, soit 5 600,00 AED pour rh-00. La version B la garde comme base et y ajoute sa phrase inventée.

**`reussite(res)`** — Cette fonction interne, qui vit dans `cas_rh`, vérifie le seul montant qui compte : elle reçoit le résultat de la boucle et renvoie vrai si le statut est « fini » et si le nombre lu après « fin de service : » est exactement l'indemnité attendue. Comme la prime inventée par la candidate vient après, dans une autre phrase, ce critère reste satisfait : seule la fidélité approchée, à 0,5 pour rh-00, révèle l'invention.

**`cas_btp(i)`** — Cette fabrique prépare une facture de sous-traitance pour chaque indice : elle reçoit i, fixe le montant hors taxe à 100 000 + 20 000 i AED, calcule le TTC attendu avec `facture_tva`, et renvoie un `Cas` nommé btp-00 à btp-09, avec un plan d'un seul appel, la question et ses deux fonctions internes. La candidate B double ce plan pour les cas 0 et 5, ce qui déclenche l'arrêt « boucle ».

**`rediger(s)`** — Cette fonction interne, qui vit dans `cas_btp`, est la plume du comptable de chantier : elle reçoit la liste des sorties d'outils, dont la première est le dictionnaire de `facture_tva`, et renvoie la phrase « TVA 5 % : … AED ; total TTC : … AED. », avec les deux montants à deux décimales, soit 5 000,00 et 105 000,00 AED pour btp-00.

**`reussite(res)`** — Cette fonction interne, qui vit dans `cas_btp`, contrôle le total de la facture : elle reçoit le résultat de la boucle et renvoie vrai si le statut est « fini » et si le nombre lu après « TTC : » par `nombre_apres` est exactement le TTC attendu. Pour btp-00 sous la version candidate, la boucle s'arrête avec le statut « boucle » avant toute réponse, et le critère échoue d'emblée.

**`cas_public(i)`** — Cette fabrique prépare la question d'un usager qui suit son dossier administratif : elle reçoit i, forme la référence REQ-2026-0100 à REQ-2026-0109, et renvoie un `Cas` nommé public-00 à public-09, avec un plan d'un seul appel à `statut_demande`, la question « Où en est ma demande … ? » et ses deux fonctions internes. Le statut attendu n'est pas recopié dans le cas : le critère le relit directement dans la table `STATUTS`.

**`rediger(s)`** — Cette fonction interne, qui vit dans `cas_public`, est l'agent de guichet qui lit la fiche du dossier : elle reçoit la liste des sorties d'outils, dont la première est le dictionnaire de `statut_demande`, et renvoie la phrase « La demande … est : … », avec la référence et le statut, par exemple « La demande REQ-2026-0100 est : approuvée. ».

**`reussite(res)`** — Cette fonction interne, qui vit dans `cas_public`, vérifie la conclusion donnée à l'usager : elle reçoit le résultat de la boucle et renvoie vrai si le statut est « fini » et si la réponse se termine exactement par « est : », le statut de la table `STATUTS` pour cette référence et un point final. Un statut mal recopié, ou un arrêt de la boucle avant la réponse, donne un échec.

**`jeu()`** — Cette fonction est le professeur qui assemble le sujet complet de l'examen : elle ne reçoit rien, parcourt les sept fabriques dans l'ordre, banque, immobilier, crypto, assurance, RH, BTP et service public, appelle chacune avec les indices 0 à 9, et renvoie la liste des 70 cas ainsi construits. C'est ce jeu de référence que `main`, puis le script de CI, font passer aux deux versions de l'agent.

**`rediger(s, base)`** — Cette fonction interne, qui vit dans `politique` et n'existe que pour la version B des cas RH, est le faussaire qui recopie la bonne réponse puis glisse une ligne de trop : elle reçoit la liste des sorties d'outils et, par un paramètre par défaut qui fige la fonction d'origine, la rédaction correcte du cas, l'appelle, puis ajoute « Une prime de fin de contrat de 2500 AED s'ajoute. ». Le nombre 2500 ne figure dans aucune source, d'où une fidélité approchée de 0,5 pour rh-00.

**`cle_appel(nom, args)`** — Cette fonction est le notaire qui rend un appel d'outil comparable à un autre : elle reçoit le nom de l'outil et ses arguments, et renvoie le couple formé du nom et des arguments sérialisés en JSON à clés triées, sans la normalisation des valeurs de l'étape 59. Pour assur-01 sous la version candidate, la clé réelle contient une vétusté de 0.0 et la clé attendue une vétusté de 0.1 : les deux clés diffèrent et `tool_call_f1` vaut 0.

**`wilson(succes, n, z)`** — Cette fonction est la fonction canonique du parcours, recopiée sans changement, l'arpenteur qui entoure chaque taux de sa marge d'incertitude : elle reçoit les succès, le nombre de cas et z, 1,96 par défaut, renvoie `None` si n = 0, lève `ValueError` si les succès sortent de [0, n], puis renvoie les deux bornes de l'intervalle à 95 %. Elle donne [0,902 ; 0,992] pour les 68 réussites sur 70 de la production et [0,740 ; 0,910] pour les 59 de la candidate, dont la borne basse sous 0,85 déclenche le premier motif de la barrière ; pour 7 sur 7, la borne basse n'est que 0,646.

**`moyenne_definie(valeurs)`** — Celle-ci est le statisticien qui refuse de compter comme zéro une note qui n'existe pas : elle reçoit une liste de valeurs dont certaines peuvent être `None`, écarte ces dernières, et renvoie la moyenne des valeurs restantes, ou `None` s'il n'en reste aucune. C'est grâce à elle que la fidélité moyenne de la candidate vaut 63/68, environ 0,926, les deux cas arrêtés en boucle étant exclus, et non 63/70.

**`rapport(resultats)`** — Cette fonction est le greffier qui rédige le bulletin d'une version : elle reçoit le dictionnaire des résultats par cas, compte les réussites, calcule le taux et son intervalle de Wilson, puis, catégorie par catégorie, le taux de réussite, et enfin les moyennes de la Tool Call F1 et de la fidélité avec `moyenne_definie`. Elle renvoie ce bulletin sous forme de dictionnaire : 68 sur 70, F1 1 et fidélité 1 pour la production ; 59 sur 70, F1 0,900 et fidélité 0,926 pour la candidate, dont l'assurance tombe à 0,3 et le BTP à 0,8.

**`mcnemar(res_prod, res_cand)`** — Celle-ci est le juge de paix qui ne regarde que les cas où les deux versions ne sont pas d'accord : elle reçoit les résultats de la production et de la candidate, appariés par identifiant de cas, compte les cas perdus, réussis par la production et ratés par la candidate, et les cas gagnés, l'inverse. Elle renvoie le χ² avec correction de continuité, (|perdus − gagnés| − 1)² ÷ (perdus + gagnés), suivi des deux comptes, ou (0, 0, 0) sans aucune discordance : ici 9 perdus, 0 gagné et χ² = 64/9, soit 7,11, au-dessus de 3,84.

**`fmt(x)`** — Cette petite fonction est le typographe du tableau des traces : elle reçoit un nombre ou `None`, et renvoie un tiret cadratin quand la valeur est indéfinie, sinon le nombre écrit avec deux décimales. `main` l'emploie pour afficher la F1 et la fidélité de chaque cas, si bien que la fidélité de btp-00, arrêté en boucle, s'affiche « — » au lieu d'un 0 trompeur qui laisserait croire à une réponse infidèle.

**`main()`** — C'est le chef d'orchestre du harnais : il construit les 70 cas, les fait passer aux versions A et B, imprime les traces de sept cas de la candidate et vérifie ses trois défauts, F1 nulle et fidélité 1 pour assur-01, réussite et fidélité 0,5 pour rh-00, arrêt « boucle » pour btp-00, ainsi que l'échec de la production sur immo-06 et immo-09. Il compare ensuite les deux rapports, 68 sur 70 contre 59 sur 70, les taux par catégorie et le test de McNemar à 9 perdus et 0 gagné, applique la barrière, qui renvoie le code 1 et six motifs pour la candidate et 0 pour la production rejouée, puis fait les contrôles à la main sur la tolérance de 10 %, la borne 0,646 de 7 sur 7 et les 16 cas parfaits qui prouvent 80 %, avant d'afficher « OK ».

```python
"""Étape 65 — harnais d'évaluation de bout en bout : jeu de référence, boucle canonique, trois métriques, barrière CI."""
import json
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass, field

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- port LLM et boucle (code canonique du parcours)
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


class FauxLLMPlan:
    """Faux LLM réactif, même port que FakeLLM : il joue un plan d'appels d'outils,
    puis rédige sa réponse à partir des tool_result qu'il a réellement reçus dans `messages`."""

    def __init__(self, plan: list, rediger):
        self.plan = list(plan)
        self.rediger = rediger
        self.appels = 0

    def create(self, *, system: str, messages: list, tools: list) -> Reponse:
        self.appels += 1
        if self.appels <= len(self.plan):
            nom, args = self.plan[self.appels - 1]
            return Reponse("tool_use", [appel_outil(nom, args, f"t{self.appels}")])
        sorties = [json.loads(b["content"]) for m in messages
                   if m["role"] == "user" and isinstance(m["content"], list)
                   for b in m["content"] if not b.get("is_error")]
        return Reponse("end_turn", [texte(self.rediger(sorties))])


# ---------------------------------------------------------------- outils EAU (déterministes ; données illustratives)
def mensualite(principal: float, taux_annuel: float, n_mois: int) -> float:
    r = taux_annuel / 12
    return round(principal / n_mois if r == 0 else principal * r / (1 - (1 + r) ** -n_mois), 2)


def ratio_endettement(existantes: float, nouvelle: float, revenu: float) -> float:
    return round((existantes + nouvelle) / revenu, 4)      # TOUTES les mensualités / revenu (CBUAE : <= 50 %)


PRIX_SQFT = {("dubai_marina", 1): 1650, ("dubai_marina", 2): 1750, ("dubai_marina", 3): 1900,
             ("jvc", 1): 1050, ("jvc", 2): 1100, ("jvc", 3): 1150}                # AED par sqft, illustratifs


def estimer_bien(zone: str, chambres: int, surface_sqft: int) -> dict:
    prix = PRIX_SQFT[(zone, chambres)]
    return {"prix_sqft": prix, "estimation": prix * surface_sqft}


RESERVES = {f"AED-USDT-{i}": 1_500_000 + 100_000 * i for i in range(10)}            # USD, illustratifs


def liquidite_pool(pool: str) -> dict:
    return {"reserve_usd": RESERVES[pool], "seuil_usd": 2_000_000}


def indemnite_sinistre(reparation: float, franchise: float, vetuste: float) -> float:
    return round(max(0.0, reparation * (1 - vetuste) - franchise), 2)


def fin_de_service(salaire_base_mensuel: float, annees: float) -> float:
    """Décret-loi fédéral 33/2021 : 21 jours par an les 5 premières années, 30 au-delà, plafond 24 mois."""
    if annees < 1:
        return 0.0
    jour = salaire_base_mensuel / 30
    brut = min(annees, 5) * 21 * jour + max(annees - 5, 0) * 30 * jour
    return round(min(brut, 24 * salaire_base_mensuel), 2)


def facture_tva(montant_ht: float) -> dict:
    return {"tva": round(montant_ht * 0.05, 2), "ttc": round(montant_ht * 1.05, 2)}


STATUTS = {f"REQ-2026-{100 + i:04d}": ("approuvée", "en cours", "refusée")[i % 3] for i in range(10)}


def statut_demande(reference: str) -> dict:
    return {"reference": reference, "statut": STATUTS[reference]}


OUTILS = {"mensualite": mensualite, "ratio_endettement": ratio_endettement, "estimer_bien": estimer_bien,
          "liquidite_pool": liquidite_pool, "indemnite_sinistre": indemnite_sinistre,
          "fin_de_service": fin_de_service, "facture_tva": facture_tva, "statut_demande": statut_demande}
SYSTEME = "Agent EAU. Règles : endettement total plafonné à 50 % du revenu ; TVA 5 % ; écart toléré sur une estimation : 10 %."


# ---------------------------------------------------------------- jeu de référence
@dataclass
class Cas:
    id: str
    categorie: str
    question: str
    plan: list            # appels attendus, dans l'ordre : (nom, arguments)
    rediger: object       # sorties des outils → réponse correcte
    reussite: object      # résultat de la boucle → bool : le critère vérifiable de l'étape 13 bis


def nombre_apres(motif: str, reponse: str) -> float | None:
    m = re.search(motif + r"(\d+(?:\.\d+)?)", reponse)
    return float(m.group(1)) if m else None


def erreur_relative(estimation: float, prix_reel: float) -> float:
    """« ±10 % » veut dire |estimation − prix réel| / prix réel <= 0,10 : on divise par le prix RÉEL."""
    if prix_reel <= 0:
        raise ValueError("prix réel > 0")
    return abs(estimation - prix_reel) / prix_reel


FACTEURS_MARCHE = [1.02, 0.97, 1.05, 0.93, 1.08, 0.99, 1.12, 0.95, 1.01, 0.89]     # prix réel / estimation


def cas_banque(i: int) -> Cas:
    principal, revenu, existantes = 600_000 + 100_000 * i, 30_000 + 2_000 * i, 3_000 + 1_500 * i
    m = mensualite(principal, 0.045, 300)
    recevable = ratio_endettement(existantes, m, revenu) <= 0.50
    plan = [("mensualite", {"principal": principal, "taux_annuel": 0.045, "n_mois": 300}),
            ("ratio_endettement", {"existantes": existantes, "nouvelle": m, "revenu": revenu})]

    def rediger(s):
        verdict = "recevable" if s[1] <= 0.50 else "refusé"
        return f"Mensualité {s[0]} AED ; endettement {s[1] * 100:.2f} % : dossier {verdict}."

    def reussite(res):
        return res["statut"] == "fini" and (("recevable" in res["reponse"]) == recevable)
    q = f"Prêt de {principal} AED à 4.5 % sur 300 mois, revenu {revenu} AED, mensualités existantes {existantes} AED : recevable ?"
    return Cas(f"banque-{i:02d}", "banque", q, plan, rediger, reussite)


def cas_immo(i: int) -> Cas:
    zone, chambres, surface = ("dubai_marina", "jvc")[i % 2], 1 + i % 3, 700 + 150 * i
    prix_reel = round(PRIX_SQFT[(zone, chambres)] * surface * FACTEURS_MARCHE[i])

    def rediger(s):
        return f"Estimation : {s[0]['estimation']} AED ({s[0]['prix_sqft']} AED/sqft)."

    def reussite(res):
        est = nombre_apres("Estimation : ", res.get("reponse", ""))
        return res["statut"] == "fini" and est is not None and erreur_relative(est, prix_reel) <= 0.10
    q = f"Estimer un bien de {chambres} chambre(s), {surface} sqft, zone {zone}."
    return Cas(f"immo-{i:02d}", "immo", q, [("estimer_bien", {"zone": zone, "chambres": chambres, "surface_sqft": surface})],
               rediger, reussite)


def cas_crypto(i: int) -> Cas:
    pool = f"AED-USDT-{i}"
    attendu = "alerte" if RESERVES[pool] < 2_000_000 else "normal"

    def rediger(s):
        etat = "alerte" if s[0]["reserve_usd"] < s[0]["seuil_usd"] else "normal"
        return f"Réserve {s[0]['reserve_usd']} USD, seuil {s[0]['seuil_usd']} USD : {etat}."

    def reussite(res):
        return res["statut"] == "fini" and res["reponse"].endswith(f": {attendu}.")
    return Cas(f"crypto-{i:02d}", "crypto", f"Le pool {pool} est-il sous son seuil de liquidité ?",
               [("liquidite_pool", {"pool": pool})], rediger, reussite)


def cas_assur(i: int) -> Cas:
    reparation, franchise, vetuste = 8_000 + 1_000 * i, 500, round(0.1 * (i % 4), 1)
    attendu = indemnite_sinistre(reparation, franchise, vetuste)

    def rediger(s):
        return f"Indemnité : {s[0]:.2f} AED."

    def reussite(res):
        return res["statut"] == "fini" and nombre_apres("Indemnité : ", res["reponse"]) == attendu
    q = f"Sinistre auto : réparation {reparation} AED, franchise {franchise} AED, vétusté {vetuste * 100:.0f} %."
    return Cas(f"assur-{i:02d}", "assur", q,
               [("indemnite_sinistre", {"reparation": reparation, "franchise": franchise, "vetuste": vetuste})],
               rediger, reussite)


def cas_rh(i: int) -> Cas:
    salaire, annees = 8_000 + 1_000 * i, 1 + i
    attendu = fin_de_service(salaire, annees)

    def rediger(s):
        return f"Indemnité de fin de service : {s[0]:.2f} AED."

    def reussite(res):
        return res["statut"] == "fini" and nombre_apres("fin de service : ", res["reponse"]) == attendu
    q = f"Fin de service : salaire de base {salaire} AED, {annees} an(s) d'ancienneté, secteur privé."
    return Cas(f"rh-{i:02d}", "rh", q, [("fin_de_service", {"salaire_base_mensuel": salaire, "annees": annees})],
               rediger, reussite)


def cas_btp(i: int) -> Cas:
    ht = 100_000 + 20_000 * i
    attendu = facture_tva(ht)["ttc"]

    def rediger(s):
        return f"TVA 5 % : {s[0]['tva']:.2f} AED ; total TTC : {s[0]['ttc']:.2f} AED."

    def reussite(res):
        return res["statut"] == "fini" and nombre_apres("TTC : ", res["reponse"]) == attendu
    return Cas(f"btp-{i:02d}", "btp", f"Facture de sous-traitance de {ht} AED hors taxe : TVA et TTC ?",
               [("facture_tva", {"montant_ht": ht})], rediger, reussite)


def cas_public(i: int) -> Cas:
    ref = f"REQ-2026-{100 + i:04d}"

    def rediger(s):
        return f"La demande {s[0]['reference']} est : {s[0]['statut']}."

    def reussite(res):
        return res["statut"] == "fini" and res["reponse"].endswith(f"est : {STATUTS[ref]}.")
    return Cas(f"public-{i:02d}", "public", f"Où en est ma demande {ref} ?",
               [("statut_demande", {"reference": ref})], rediger, reussite)


def jeu() -> list[Cas]:
    fabriques = (cas_banque, cas_immo, cas_crypto, cas_assur, cas_rh, cas_btp, cas_public)
    return [f(i) for f in fabriques for i in range(10)]


# ---------------------------------------------------------------- deux versions de l'agent
def politique(version: str, cas: Cas) -> tuple[list, object]:
    """A = production. B = nouveau prompt, avec trois défauts plantés pour que la barrière ait quelque chose à voir."""
    plan, rediger = list(cas.plan), cas.rediger
    if version == "B":
        n = int(cas.id[-2:])
        if cas.categorie == "assur" and cas.plan[0][1]["vetuste"] > 0:            # oublie la vétusté
            nom, args = cas.plan[0]
            plan = [(nom, dict(args, vetuste=0.0))]
        if cas.categorie == "rh":                                                  # invente une prime
            def rediger(s, base=cas.rediger):
                return base(s) + " Une prime de fin de contrat de 2500 AED s'ajoute."
        if cas.categorie == "btp" and n % 5 == 0:                                  # rappelle le même outil
            plan = plan * 2
    return plan, rediger


# ---------------------------------------------------------------- métriques
def cle_appel(nom: str, args: dict) -> tuple[str, str]:
    return nom, json.dumps(args, sort_keys=True)


def tool_call_f1(attendus: list, reels: list) -> float | None:
    """Étape 59 : F1 sur des multi-ensembles d'appels (nom, arguments) ; None si rien d'attendu ni d'appelé."""
    a = Counter(cle_appel(n, x) for n, x in attendus)
    r = Counter(cle_appel(n, x) for n, x in reels)
    total = sum(a.values()) + sum(r.values())
    if total == 0:
        return None
    return 2 * sum((a & r).values()) / total


def nombres(t: str) -> list[float]:
    """Nombres cités dans un texte ; « 28.97 % » est lu 0.2897."""
    return [float(v) / 100 if pct else float(v) for v, pct in re.findall(r"(\d+(?:\.\d+)?)\s*(%?)", t)]


def fidelite_approchee(reponse: str, sources: list[str]) -> float | None:
    """Approximation de l'étape 54 : part des NOMBRES de la réponse présents dans les sources ; None sans nombre."""
    cites = nombres(reponse)
    if not cites:
        return None
    connus = [x for s in sources for x in nombres(s)]
    soutenus = sum(1 for c in cites if any(math.isclose(c, k, rel_tol=1e-9, abs_tol=1e-9) for k in connus))
    return soutenus / len(cites)


def wilson(succes: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    """Intervalle de Wilson à 95 % pour une proportion ; None si n = 0."""
    if n == 0:
        return None
    if not 0 <= succes <= n:
        raise ValueError("il faut 0 <= succes <= n")
    p = succes / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    demi = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (centre - demi, centre + demi)


def moyenne_definie(valeurs: list) -> float | None:
    definies = [v for v in valeurs if v is not None]
    return sum(definies) / len(definies) if definies else None


# ---------------------------------------------------------------- harnais
def evaluer(cas_list: list[Cas], version: str) -> dict[str, dict]:
    resultats = {}
    for cas in cas_list:
        plan, rediger = politique(version, cas)
        res = executer_agent(FauxLLMPlan(plan, rediger), SYSTEME, cas.question, OUTILS, [])
        appels = [(nom, args) for nom, args, _ in res["trace"]]
        sources = [SYSTEME, cas.question] + [json.dumps(s, ensure_ascii=False) for _, _, s in res["trace"]]
        resultats[cas.id] = {
            "categorie": cas.categorie, "statut": res["statut"], "outils": [n for n, _ in appels],
            "but": cas.reussite(res),
            "f1": tool_call_f1(cas.plan, appels),
            "fidelite": fidelite_approchee(res["reponse"], sources) if res["statut"] == "fini" else None,
        }
    return resultats


def rapport(resultats: dict[str, dict]) -> dict:
    n = len(resultats)
    succes = sum(r["but"] for r in resultats.values())
    categories = {}
    for r in resultats.values():
        ok, nb = categories.get(r["categorie"], (0, 0))
        categories[r["categorie"]] = (ok + r["but"], nb + 1)
    return {"n": n, "succes": succes, "taux": succes / n, "wilson": wilson(succes, n),
            "categories": {c: ok / nb for c, (ok, nb) in categories.items()},
            "tool_f1": moyenne_definie([r["f1"] for r in resultats.values()]),
            "fidelite": moyenne_definie([r["fidelite"] for r in resultats.values()])}


def mcnemar(res_prod: dict, res_cand: dict) -> tuple[float, int, int]:
    """Étape 13 bis : paires discordantes, correction de continuité."""
    perdus = sum(1 for i in res_prod if res_prod[i]["but"] and not res_cand[i]["but"])
    gagnes = sum(1 for i in res_prod if not res_prod[i]["but"] and res_cand[i]["but"])
    if perdus + gagnes == 0:
        return 0.0, 0, 0
    return (abs(perdus - gagnes) - 1) ** 2 / (perdus + gagnes), perdus, gagnes


SEUILS = {"borne_basse": 0.85, "perte_max_categorie": 0.05, "tool_f1": 0.95, "fidelite": 0.95, "chi2": 3.84}


def barriere_ci(res_prod: dict, res_cand: dict, seuils: dict) -> tuple[int, list[str]]:
    """Renvoie (code de sortie, motifs) : 0 autorise le déploiement, 1 le bloque. Ne quitte jamais le programme."""
    prod, cand = rapport(res_prod), rapport(res_cand)
    chi2, perdus, gagnes = mcnemar(res_prod, res_cand)
    motifs = []
    if cand["wilson"][0] < seuils["borne_basse"]:
        motifs.append(f"borne basse de Wilson {cand['wilson'][0]:.3f} < {seuils['borne_basse']}")
    for c, taux in sorted(cand["categories"].items()):
        if taux < prod["categories"][c] - seuils["perte_max_categorie"]:
            motifs.append(f"catégorie {c} : {prod['categories'][c]:.2f} → {taux:.2f}")
    if chi2 > seuils["chi2"] and perdus > gagnes:
        motifs.append(f"régression significative (McNemar χ² = {chi2:.2f})")
    if cand["tool_f1"] is not None and cand["tool_f1"] < seuils["tool_f1"]:
        motifs.append(f"Tool Call F1 {cand['tool_f1']:.3f} < {seuils['tool_f1']}")
    if cand["fidelite"] is not None and cand["fidelite"] < seuils["fidelite"]:
        motifs.append(f"fidélité approchée {cand['fidelite']:.3f} < {seuils['fidelite']}")
    return (1 if motifs else 0), motifs


def fmt(x: float | None) -> str:
    return "—" if x is None else f"{x:.2f}"


def main() -> None:
    cas_list = jeu()
    res_a, res_b = evaluer(cas_list, "A"), evaluer(cas_list, "B")

    print("Traces de la version candidate B (un cas par domaine)")
    for cid in ("banque-00", "immo-06", "crypto-00", "assur-01", "rh-00", "btp-00", "public-00"):
        r = res_b[cid]
        outils = " → ".join(r["outils"])
        print(f"  {cid:<10} {outils:<32} {r['statut']:<6} but {'oui' if r['but'] else 'non'}   F1 {fmt(r['f1'])}   fidélité {fmt(r['fidelite'])}")
    assert res_b["assur-01"]["f1"] == 0.0 and res_b["assur-01"]["fidelite"] == 1.0 and not res_b["assur-01"]["but"]
    assert res_b["rh-00"]["but"] and res_b["rh-00"]["fidelite"] == 0.5
    assert res_b["btp-00"]["statut"] == "boucle" and res_b["btp-00"]["fidelite"] is None
    assert not res_a["immo-06"]["but"] and not res_a["immo-09"]["but"]          # le marché s'écarte de plus de 10 %

    rap_a, rap_b = rapport(res_a), rapport(res_b)
    for nom, rap in (("A (production)", rap_a), ("B (candidate) ", rap_b)):
        lo, hi = rap["wilson"]
        print(f"{nom} : {rap['succes']}/{rap['n']} = {rap['taux']:.3f}   Wilson [{lo:.3f} ; {hi:.3f}]"
              f"   Tool F1 {rap['tool_f1']:.3f}   fidélité {rap['fidelite']:.3f}")
    assert (rap_a["succes"], rap_b["succes"]) == (68, 59)
    assert rap_a["tool_f1"] == 1.0 and math.isclose(rap_b["tool_f1"], 63 / 70)
    assert rap_a["fidelite"] == 1.0 and math.isclose(rap_b["fidelite"], 63 / 68)
    print("Par catégorie (A → B) : " + ", ".join(f"{c} {rap_a['categories'][c]:.1f} → {rap_b['categories'][c]:.1f}"
                                                 for c in rap_a["categories"]))
    chi2, perdus, gagnes = mcnemar(res_a, res_b)
    print(f"McNemar : {perdus} cas perdus, {gagnes} gagnés, χ² = {chi2:.2f}")
    assert (perdus, gagnes) == (9, 0) and math.isclose(chi2, 64 / 9)

    code_b, motifs_b = barriere_ci(res_a, res_b, SEUILS)
    print(f"Barrière CI, candidate B → code {code_b}")
    for m in motifs_b:
        print(f"  - {m}")
    code_a, motifs_a = barriere_ci(res_a, res_a, SEUILS)
    print(f"Barrière CI, production rejouée → code {code_a} ({'déploiement autorisé' if code_a == 0 else motifs_a})")
    assert code_b == 1 and len(motifs_b) == 6 and code_a == 0 and motifs_a == []

    print("Contrôles à la main")
    assert erreur_relative(2_205_000, 2_450_000) <= 0.10                   # 10 % sous le prix réel : accepté
    assert not 0.9 * 2_205_000 <= 2_450_000 <= 1.1 * 2_205_000             # mais hors d'une fourchette ±10 % de l'estimation
    assert math.isclose(wilson(7, 7)[0], 7 / (7 + 1.96 ** 2))              # 7 cas parfaits ne prouvent que 64,6 %
    n_min = next(n for n in range(1, 100) if n / (n + 1.96 ** 2) >= 0.80)
    assert n_min == 16 and round(wilson(7, 7)[0], 3) == 0.646
    assert tool_call_f1([], []) is None and fidelite_approchee("Votre demande est prête.", [SYSTEME]) is None
    print(f"  ±10 % mesuré sur le prix réel ; 7/7 → borne basse 0.646 ; {n_min} cas parfaits pour prouver 80 %")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Traces de la version candidate B (un cas par domaine)
…
  assur-01   indemnite_sinistre               fini   but non   F1 0.00   fidélité 1.00
  rh-00      fin_de_service                   fini   but oui   F1 1.00   fidélité 0.50
  btp-00     facture_tva                      boucle but non   F1 1.00   fidélité —
…
A (production) : 68/70 = 0.971   Wilson [0.902 ; 0.992]   Tool F1 1.000   fidélité 1.000
B (candidate)  : 59/70 = 0.843   Wilson [0.740 ; 0.910]   Tool F1 0.900   fidélité 0.926
…
McNemar : 9 cas perdus, 0 gagnés, χ² = 7.11
Barrière CI, candidate B → code 1
  - borne basse de Wilson 0.740 < 0.85
  - catégorie assur : 1.00 → 0.30
  - catégorie btp : 1.00 → 0.80
  - régression significative (McNemar χ² = 7.11)
  - Tool Call F1 0.900 < 0.95
  - fidélité approchée 0.926 < 0.95
Barrière CI, production rejouée → code 0 (déploiement autorisé)
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un harnais d'évaluation n'est pas une métrique, c'est un assemblage. La même boucle qu'en production, des critères vérifiables par cas, plusieurs métriques qui voient des défauts différents, des intervalles plutôt que des chiffres seuls, et une règle écrite qui décide.

Dans le pipeline d'intégration continue, un script court appelle le harnais et transforme le code renvoyé en code de sortie du processus. C'est le seul endroit où `sys.exit` apparaît :

```python
# [extrait] — script lancé par le pipeline d'intégration continue (non exécuté par le harnais du parcours)
import sys

cas_list = jeu()
code, motifs = barriere_ci(evaluer(cas_list, "A"), evaluer(cas_list, "B"), SEUILS)
for m in motifs:
    print(m)
sys.exit(code)          # 1 fait échouer l'étape du pipeline et bloque le déploiement
```

Pour passer au vrai modèle, on remplace `FauxLLMPlan(plan, rediger)` par l'adaptateur `ClaudeLLM` de l'étape 13 : `executer_agent`, les métriques et la barrière ne changent pas. Il faut alors répéter plusieurs essais par cas, parce que le modèle n'est plus déterministe (pass@k et pass^k, étapes 13 bis et 60).

## Squelette algorithmique

Les entrées sont un jeu de référence (pour chaque cas : une question, la liste des appels d'outils attendus et un critère de réussite vérifiable), deux versions de l'agent (la production et la candidate) et une table de seuils. La sortie est un code de sortie, 0 pour autoriser le déploiement et 1 pour le bloquer, accompagné de la liste des motifs. L'idée : faire passer chaque cas aux deux versions par la même boucle qu'en production, noter chaque cas sur plusieurs métriques, agréger avec des intervalles et un test apparié, puis appliquer des règles écrites à l'avance.

```text
ALGORITHME HarnaisDÉvaluation
ENTRÉES : jeu de référence C (chaque cas : question, appels attendus, critère de réussite, catégorie),
          version de production A, version candidate B, seuils
SORTIE  : (code, motifs), code = 0 pour déployer, 1 pour bloquer
    POUR chaque version v DANS {A, B} FAIRE
        POUR chaque cas c DE C FAIRE
            r ← ExécuterAgent(v, c.question)                 ▹ la boucle de production, jamais une copie
            but[v][c] ← c.critère(r)                          ▹ faux si r.statut ≠ fini
            f1[v][c] ← ToolCallF1(c.appels_attendus, appels de r.trace)
            SI r.statut = fini ALORS
                fid[v][c] ← FidélitéApprochée(r.réponse, système + question + sorties d'outils)
            SINON
                fid[v][c] ← INDÉFINI                          ▹ ni 0 ni 1 : exclu des moyennes
            FIN SI
        FIN POUR
    FIN POUR
    motifs ← liste vide ; n ← |C| ; s ← Σ but[B][c]
    SI BorneBasseWilson(s, n) < seuil_borne ALORS ajouter un motif FIN SI
    POUR chaque catégorie k FAIRE
        SI taux_B(k) < taux_A(k) − perte_max ALORS ajouter un motif FIN SI
    FIN POUR
    perdus ← nombre de cas c tels que but[A][c] ET NON but[B][c]
    gagnés ← nombre de cas c tels que NON but[A][c] ET but[B][c]
    SI perdus + gagnés > 0 ALORS
        χ² ← (|perdus − gagnés| − 1)² / (perdus + gagnés)
        SI χ² > 3,84 ET perdus > gagnés ALORS ajouter un motif FIN SI
    FIN SI
    SI moyenne des f1[B] définis < seuil_f1 ALORS ajouter un motif FIN SI
    SI moyenne des fid[B] définis < seuil_fid ALORS ajouter un motif FIN SI
    SI motifs est vide ALORS
        RETOURNER (0, motifs)
    SINON
        RETOURNER (1, motifs)                                 ▹ seul le script de CI appelle sys.exit
    FIN SI

ALGORITHME ExécuterAgent                                      ▹ rappel de l'étape 1
ENTRÉES : modèle, question, outils, max_étapes (borné : jamais ∞)
    messages ← [question] ; précédente ← aucune ; étape ← 1
    TANT QUE étape ≤ max_étapes FAIRE
        réponse ← modèle(messages)
        SI réponse est finale ALORS RETOURNER (fini, réponse, trace) FIN SI
        SI ses appels sont identiques à précédente ALORS RETOURNER (boucle, trace) FIN SI
        exécuter chaque appel ; ajouter TOUS les résultats dans UN message
        précédente ← ses appels ; étape ← étape + 1
    FIN TANT QUE
    RETOURNER (max_étapes, trace)

ALGORITHME FidélitéApprochée
ENTRÉES : réponse, sources
    cités ← nombres de la réponse (« x % » est lu x / 100)
    SI cités est vide ALORS RETOURNER INDÉFINI FIN SI
    connus ← nombres de toutes les sources
    RETOURNER |{ c ∈ cités : c ∈ connus }| / |cités|
```

**Complexité :** notons N le nombre de cas, E le nombre maximal d'étapes de la boucle (ici 8, et au plus 3 utilisées), et L la longueur des textes d'un cas. Le harnais fait tourner 2 × N exécutions de l'agent, chacune d'au plus E appels au modèle : avec un vrai LLM, c'est ce nombre d'appels, O(N·E), facturés et lents, qui domine tout le reste. Avec `FauxLLMPlan`, chaque appel relit l'historique, qui a au plus E messages : O(E²) par cas, négligeable. La Tool Call F1 d'un cas coûte O(a + r) pour a appels attendus et r appels réels, grâce aux compteurs (tables de hachage). La fidélité approchée compare chaque nombre cité à chaque nombre connu : O(c × k) pour c nombres cités et k nombres connus, une boucle quadratique acceptable sur quelques dizaines de nombres, qu'un ensemble de valeurs arrondies ramènerait à O(c + k). L'agrégation (taux, catégories, McNemar) est un passage linéaire, O(N), et Wilson se calcule en O(1). La mémoire est O(N) pour les résultats des deux versions, plus O(E) pour l'historique du cas en cours.

**Du squelette au code :** la double boucle POUR est `evaluer(cas_list, version)`, appelée une fois par version dans `main()`. ExécuterAgent est la fonction canonique `executer_agent`, à qui l'on passe `FauxLLMPlan(*politique(version, cas))` comme modèle ; ses trois sorties de la boucle TANT QUE sont les statuts `"fini"`, `"boucle"` et `"max_etapes"`. Le critère de réussite est `cas.reussite(res)`, défini dans chaque fabrique `cas_banque` … `cas_public`. ToolCallF1 est `tool_call_f1` avec `cle_appel` ; FidélitéApprochée est `fidelite_approchee` avec `nombres`, et l'INDÉFINI est le `None` rangé par `evaluer` quand le statut n'est pas `"fini"`. La somme s, le taux par catégorie et les moyennes définies sont dans `rapport` et `moyenne_definie` ; la borne basse est `wilson(succes, n)[0]`. Les compteurs `perdus` et `gagnés` et le χ² sont `mcnemar`. Les SI qui ajoutent un motif, puis le RETOURNER final, sont le corps de `barriere_ci`, qui renvoie `(1 if motifs else 0), motifs`.

## Cas d'usage réels aux Émirats

Chaque cas reprend un domaine du harnais, avec ses entrées, les outils appelés dans l'ordre, la sortie, la métrique et le garde-fou. Les données sont illustratives ; les règles sont celles du guide du parcours, à confirmer avec le texte en vigueur.

### Banque — un dossier de prêt, deux outils, un verdict

Une banque de détail de Dubaï évalue l'agent qui pré-instruit les demandes de prêt hypothécaire. Entrées du cas banque-00 : un prêt de 600 000 AED à 4,5 % sur 300 mois, un revenu de 30 000 AED et 3 000 AED de mensualités existantes. L'agent appelle d'abord `mensualite`, qui renvoie 3 334,99 AED, puis `ratio_endettement` avec les mensualités existantes **et** la nouvelle, qui renvoie 0,2112 ; il répond « endettement 21.12 % : dossier recevable », puisque la règle de la CBUAE plafonne l'endettement total à 50 % du revenu. La réussite se vérifie par code contre un verdict de référence calculé à part ; la Tool Call F1 vaut 1, et la fidélité vaut 1 parce que les deux nombres cités viennent des outils. Le garde-fou est structurel : le verdict n'est jamais calculé de tête par le modèle, il découle de la sortie d'un outil déterministe. Le jeu de cet exemple a un défaut que la banque corrige dans son vrai jeu : 9 dossiers recevables pour 1 refusé (banque-09, à 51,74 %), donc trop peu de refus pour mesurer la capacité de l'agent à dire non. L'indicateur suivi est le taux de réussite par verdict, recevable et refusé séparément.

### Immobilier — une estimation jugée contre le prix réel

Une agence qui opère à Dubaï et à Abu Dhabi évalue son agent d'estimation sur des ventes conclues, dont le prix réel est connu après coup. Entrées du cas immo-06 : un appartement d'une chambre de 1 600 sqft à Dubai Marina. L'agent appelle `estimer_bien`, qui renvoie un prix médian de 1 650 AED/sqft et une estimation de 2 640 000 AED ; le prix réel de la transaction est de 2 956 800 AED. L'erreur relative vaut 316 800 / 2 956 800 ≈ 0,107, au-dessus de 0,10 : le cas échoue pour les deux versions, avec une Tool Call F1 et une fidélité parfaites. Le défaut n'est donc pas dans l'agent mais dans les données de comparables, trop anciennes pour un marché qui a monté de 12 % : l'agence sépare dans son rapport les échecs d'exécution (mauvais outil, mauvais argument) des échecs de méthode, et rafraîchit ses comparables à partir des transactions récentes. Le garde-fou : l'agent présente une estimation avec sa méthode, jamais une promesse de prix, et toute estimation destinée à un financement passe par un évaluateur humain. L'indicateur suivi est la part des estimations à moins de 10 % du prix réel, par zone.

### Crypto — une alerte de liquidité qui doit partir

Une plateforme d'actifs virtuels agréée par la VARA fait surveiller ses pools par un agent. Entrées du cas crypto-00 : le pool AED-USDT-0. L'agent appelle `liquidite_pool`, qui renvoie une réserve de 1 500 000 USD pour un seuil de 2 000 000 USD, et répond « alerte ». Dans le jeu, la moitié des pools sont sous leur seuil, pour que l'agent soit mesuré autant sur les alertes que sur les situations normales. La métrique est la réussite de la tâche, et la plateforme regarde à part les faux négatifs (une alerte manquée), qu'elle veut à zéro, parce qu'un manque de liquidité non signalé empêche d'honorer les retraits. Le garde-fou : l'agent n'a que des outils de lecture ; suspendre les retraits passe par un outil d'écriture qui demande une approbation humaine **dans l'outil** (étape 66). L'indicateur suivi en production est le délai entre le franchissement du seuil et l'alerte.

### Assurance — la vétusté oubliée

Un assureur auto teste une nouvelle version du prompt de son agent d'indemnisation. Entrées du cas assur-01 : une réparation de 9 000 AED, une franchise de 500 AED et une vétusté de 10 %. L'indemnité attendue vaut 9 000 × 0,9 − 500 = 7 600 AED ; la candidate appelle `indemnite_sinistre` avec une vétusté de 0 et répond 8 500 AED, soit 900 AED de trop. La Tool Call F1 vaut 0, parce que l'argument diffère, et la tâche échoue ; la fidélité vaut 1, parce que le montant faux sort bien de l'outil. Sur les dix cas d'assurance, sept ont une vétusté non nulle et échouent : la catégorie passe de 1,00 à 0,30 et la barrière bloque, alors que la moyenne globale de la candidate (0,843) aurait pu sembler acceptable. Le garde-fou ajouté en production : l'outil exige la vétusté, calculée à partir de l'âge du véhicule, au lieu de l'accepter du modèle, et toute indemnité au-dessus d'un montant fixé passe en revue humaine. L'indicateur suivi est l'écart moyen entre l'indemnité proposée et l'indemnité de référence.

### RH — un montant juste, une prime inventée

Un cabinet RH présent dans plusieurs émirats évalue son assistant de fin de service. Entrées du cas rh-00 : un salaire de base de 8 000 AED et un an d'ancienneté dans le secteur privé. L'agent appelle `fin_de_service`, qui applique le décret-loi fédéral 33/2021 (21 jours de salaire de base par année les cinq premières années) et renvoie 8 000 / 30 × 21 = 5 600 AED. La candidate écrit ce montant juste, puis ajoute « une prime de fin de contrat de 2 500 AED », qui n'existe dans aucune source. La tâche est réussie, la Tool Call F1 vaut 1, et seule la fidélité, à 0,5, voit l'invention : la catégorie RH reste à 1,00 en réussite, et c'est la fidélité moyenne de 0,926, sous le seuil de 0,95, qui bloque. Un salarié qui aurait reçu cette réponse aurait réclamé une prime à son employeur. Le garde-fou : l'agent ne cite que des montants renvoyés par un outil, et rappelle les exclusions (ressortissants émiriens, qui relèvent de la GPSSA, et salariés du DIFC, qui ont leur propre régime). L'indicateur suivi est le nombre de montants non sourcés pour 100 réponses.

### BTP — une boucle arrêtée, comptée comme un échec

Un groupe de construction qui mène de grands chantiers à Dubaï fait calculer par un agent la TVA des factures de sous-traitance. Entrées du cas btp-00 : une facture de 100 000 AED hors taxe. L'agent attendu appelle `facture_tva` une fois et répond « TVA 5 % : 5000.00 AED ; total TTC : 105000.00 AED ». La candidate rappelle le même outil avec les mêmes arguments : la boucle canonique reconnaît la répétition et s'arrête avec le statut « boucle » avant le second appel, sans réponse. La tâche échoue, la fidélité est indéfinie et sort de la moyenne, et la Tool Call F1 vaut 1 puisque l'appel en double n'a jamais été exécuté. Le garde-fou de la boucle a donc protégé la production (pas de boucle sans fin, pas de double écriture si l'outil avait émis une facture), mais l'évaluation doit compter cet arrêt comme un échec, sinon le défaut passerait inaperçu. L'indicateur suivi est le taux d'arrêts « boucle » par version, avec la question qui l'a déclenché.

### Secteur public — un statut lu dans le système, jamais deviné

Une entité de services publics en ligne, accessible par UAE Pass, fait répondre un agent aux usagers qui demandent où en est leur dossier. Entrées du cas public-00 : la référence REQ-2026-0100. L'agent appelle `statut_demande`, qui lit le système de référence et renvoie « approuvée » ; il répond avec ce statut, mot pour mot. Le critère de réussite est l'égalité exacte avec le statut du système, et le jeu contient autant de demandes approuvées, en cours et refusées, pour que l'agent ne soit pas récompensé de répondre toujours « en cours ». Le garde-fou : l'outil ne renvoie que les dossiers de l'usager authentifié, et le jeu d'évaluation utilise des références fictives, pour respecter la PDPL. L'indicateur suivi est le nombre de divergences entre la réponse de l'agent et le système, mesuré chaque jour sur un échantillon, avec un objectif de zéro.

## Pièges et limites

- **Ne regarder qu'une métrique.** Chaque défaut planté n'est vu que par une ou deux des trois métriques (démonstration, point 4). Une barrière se construit sur plusieurs conditions.
- **Évaluer sur trop peu de cas.** Sept cas parfaits ne prouvent qu'un taux de 64,6 % ; il en faut au moins 16 pour prouver 80 %, 73 pour 95 %.
- **Écrire « ±10 % » sans dire autour de quoi.** On mesure l'erreur relative au prix réel, et on l'écrit dans le code.
- **Appeler `sys.exit` dans la fonction de barrière.** Elle doit renvoyer un code ; seul le script de CI quitte le processus. Sinon, impossible de tester la barrière elle-même.
- **Prendre la fidélité approchée pour la fidélité.** Elle ne voit que les nombres, et un nombre peut figurer dans les sources par coïncidence. La vraie mesure passe par l'extraction des affirmations et un juge (étape 54).

### Exercice feuille blanche

1. Sans regarder le code, réécrire `barriere_ci` à partir du squelette, avec les cinq conditions, en renvoyant `(code, motifs)`, puis l'extrait de CI qui appelle `sys.exit(code)`.
2. Prédire, puis vérifier : on corrige le défaut d'assurance de la candidate (on supprime la ligne qui met la vétusté à 0). Quels motifs restent ? (Réponse : 66 cas réussis sur 70, borne basse 0,862 ≥ 0,85 ; McNemar avec 2 perdus et 0 gagné donne χ² = 0,5, non significatif ; la Tool Call F1 remonte à 1. Restent deux motifs : la catégorie BTP, de 1,00 à 0,80, et la fidélité de 0,926.)
3. Trouver le bug : une variante de `moyenne_definie` remplace `None` par 0. Que devient la fidélité moyenne de la candidate, et pourquoi est-ce faux ? (Réponse : 63/70 = 0,900 au lieu de 63/68 ≈ 0,926 ; les deux cas sans réponse sont déjà comptés comme des échecs par la réussite de la tâche, les compter aussi comme infidèles les punit deux fois.)

## Pour aller plus loin

Avec un vrai modèle, on lance plusieurs essais par cas et l'on publie pass@1, pass@k et pass^k (étapes 13 bis et 60). Le juge LLM qui remplace la fidélité approchée se calibre contre des notes humaines, avec un accord mesuré par le kappa. On découpe les résultats par catégorie **et** par langue, arabe et anglais, et l'on fait entrer dans le jeu les cas découverts en production, comme le décrit l'étape 13 bis. Les garde-fous de l'étape 66 reprennent les signaux de ce harnais (fidélité basse, outil d'écriture, montant élevé) pour décider, en ligne, ce qui passe et ce qui s'arrête.

> Suite : [Classement par duels : Elo et Bradley-Terry](<65b-Classement-par-Duels-Elo-Bradley-Terry.md>) — étape 65 bis.
