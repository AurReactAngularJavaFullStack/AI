# Étape 72 quater — Production — Observabilité : traces, coûts et dérive

**Dossier :** 12-Production-Couts-Optimisation

> Étape 72 quater du parcours · Prérequis : [Décodage spéculatif](<72c-Decodage-Speculatif.md>) · Suite : [Budget de raisonnement](<72e-Budget-de-Raisonnement.md>)

**Métiers concernés :** AI Agent Ops, AI Platform Team, AI Engineers, Forward-Deployed Engineers

Les étapes 69 à 72 ont chiffré la charge et le coût d'un agent sur le papier ; les étapes 72 bis et 72 ter ont accéléré le service du modèle. En production, il reste à **voir** ce que fait chaque exécution : combien de temps a pris chaque étape, combien de tokens elle a consommés, ce qu'elle a coûté, quel outil a échoué, et si le trafic de cette semaine ressemble encore à celui sur lequel l'agent a été évalué. Ce fichier construit, depuis une feuille blanche et en bibliothèque standard, un traceur à base de *context manager*, instrumente la boucle canonique `executer_agent` **sans la modifier** (en décorant ses ports, comme un adaptateur hexagonal), agrège les durées et les coûts en p50 et p95, mesure la consommation du budget d'erreur de l'étape 49, et détecte la dérive avec le PSI, dont la positivité découle de l'inégalité de Gibbs de l'étape 50.

## Définition

L'**observabilité** est la capacité d'expliquer de l'extérieur ce qu'un système a fait, à partir des seules données qu'il émet. Pour un agent, la donnée centrale est la **trace** : l'arbre des opérations d'une exécution. Chaque nœud est un **span**, une opération nommée (un appel au modèle, un appel d'outil, l'exécution entière) qui porte un identifiant de trace commun, son propre identifiant, celui de son parent, un instant de début et de fin, un statut et des **attributs** : tokens d'entrée et de sortie, coût, nom de l'outil. En agrégeant les spans de milliers d'exécutions, on obtient des **métriques** : le p50 et le p95 des durées par type de span, le coût par exécution, le taux d'exécutions ratées. La **dérive** est le changement de la distribution des entrées ou des comportements entre une période de référence et la période courante ; l'indice de stabilité de population (PSI) la mesure par une somme qui vaut la somme des deux divergences de Kullback-Leibler.

## Rôle dans un agent

L'observabilité sert l'étape « observer » de la boucle, mais pour l'**opérateur** et non pour le modèle. Chaque tour percevoir → décider → agir devient un span `llm.create`, chaque action un span `outil.<nom>`, et l'exécution entière un span racine `agent.executer` : la trace dit où passent le temps et l'argent, tour par tour, avec la formule de coût de l'étape 72 appliquée à chaque span. Les agrégats alimentent trois composants. Le **garde-fou de budget** compare le coût par exécution à un plafond. Le budget d'erreur de l'étape 49 décide s'il faut geler les déploiements. Le **routeur** de l'étape 72 quinquies choisit l'effort de raisonnement selon le coût et la latence observés par route. La surveillance de dérive prévient avant que la qualité ne baisse en silence : si la part des questions en arabe double, les prompts s'allongent, les coûts montent et l'évaluation faite sur l'ancien trafic (étape 13 bis) ne vaut plus. Enfin, l'identifiant de trace voyage dans l'en-tête `traceparent` des événements de l'étape 45 bis et des webhooks de l'étape 45 ter, si bien qu'une trace traverse les frontières asynchrones.

## Équation complète

Durée d'un span s, puis temps propre : la durée qui n'est passée dans aucun de ses enfants :

$$
d(s) = t_{fin}(s) - t_{debut}(s)
$$

$$
d_{propre}(s) = d(s) - \sum_{c \,\in\, \mathrm{enf}(s)} d(c)
$$

Identité de la trace : les temps propres de tous les spans d'une trace somment à la durée de la racine.

$$
\sum_{s} d_{propre}(s) = d(\text{racine})
$$

Coût d'un span de modèle (étape 72, avec un cache écrit au facteur w et lu au facteur f), puis d'une exécution :

$$
C(s) = P_{in}\left(N_{in} + w\, N_{ecrit} + f\, N_{lu}\right) + P_{out}\, N_{out}
$$

$$
C_{exec} = \sum_{s \,\in\, \text{spans de modèle}} C(s)
$$

Percentile d'ordre r au rang le plus proche (fonction canonique `p95` pour r = 0,95, et p50 pour r = 0,5), sur n valeurs triées :

$$
P_r = x_{\left(\lceil r\, n \rceil\right)}
$$

Vitesse de consommation du budget d'erreur d'un objectif A* (étape 49), avec m exécutions mauvaises sur n :

$$
v = \frac{1 - A_{obs}}{1 - A^{*}} \qquad A_{obs} = 1 - \frac{m}{n}
$$

Indice de stabilité de population entre une distribution de référence p et une distribution courante q sur B cases :

$$
\mathrm{PSI}(p, q) = \sum_{i=1}^{B} (p_i - q_i) \ln\frac{p_i}{q_i} = D_{KL}(p \parallel q) + D_{KL}(q \parallel p)
$$

Niveau du PSI dû au seul bruit d'échantillonnage, quand q est estimée sur M observations tirées de la loi p elle-même :

$$
\mathbb{E}\left[\mathrm{PSI}(p, \hat{q})\right] \approx \frac{B - 1}{M}
$$

## Décryptage des symboles

$$
s,\; \mathrm{enf}(s)
$$

Un span de la trace, et l'ensemble de ses enfants directs ; une instance de `Span`, et `par_parent[s.span_id]` dans le code.

$$
t_{debut}(s),\; t_{fin}(s),\; d(s)
$$

Les instants de début et de fin sur l'horloge simulée, en millisecondes, et la durée ; `debut_ms`, `fin_ms`, `duree_ms`.

$$
d_{propre}(s)
$$

Le temps propre du span, en millisecondes ; positif ou nul quand les enfants s'exécutent l'un après l'autre ; `temps_propre(s, par_parent)`.

$$
N_{in},\; N_{ecrit},\; N_{lu},\; N_{out}
$$

Les tokens d'entrée non mis en cache, les tokens écrits dans le cache, les tokens lus dans le cache et les tokens de sortie d'un appel, des entiers ; les champs `input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens` et `output_tokens` de l'usage d'une réponse de l'API, où `input_tokens` n'inclut pas le cache.

$$
P_{in},\; P_{out},\; w,\; f
$$

Les prix d'un token d'entrée et de sortie, 3 et 15 USD par million (illustratifs, comme à l'étape 72), et les facteurs d'écriture et de lecture du cache, 1,25 et 0,10 ; `PRIX_IN`, `PRIX_OUT`, `FACTEUR_ECRITURE`, `FACTEUR_LECTURE`.

$$
C(s),\; C_{exec}
$$

Le coût d'un span de modèle et d'une exécution, en USD ; `cout_usd(u)` et la somme des attributs `cout_usd`.

$$
r,\; n,\; x_{(k)},\; P_r
$$

L'ordre du percentile (0,5 ou 0,95), le nombre de valeurs, la k-ième plus petite valeur et le percentile au rang le plus proche ; `p50(valeurs)` et `p95(valeurs)`.

$$
A^{*},\; A_{obs},\; m,\; v
$$

L'objectif de bonnes exécutions (0,99 ici), la part observée, le nombre d'exécutions mauvaises et la vitesse de consommation du budget ; `slo`, `1 - mauvais / total`, `mauvais` et `taux_de_consommation(mauvais, total, slo)`.

$$
p,\; q,\; p_i,\; q_i,\; B
$$

La distribution de référence et la distribution courante, leurs masses sur la case i et le nombre de cases ; des listes de réels positifs de somme 1, `p` et `q`, de longueur B.

$$
D_{KL}(p \parallel q),\; \mathrm{PSI}(p, q)
$$

La divergence de Kullback-Leibler de l'étape 50 et le PSI, des réels positifs ou nuls, éventuellement infinis ; `kl(p, q)` et `psi(p, q)`.

$$
M,\; \hat{q}
$$

Le nombre d'observations de la fenêtre courante et la distribution empirique qui en est tirée ; `m` et `[c / m for c in comptes]` dans la section 6 du programme.

## Démonstration

### 1. Les temps propres d'une trace somment à la durée de la racine

On additionne la définition du temps propre sur tous les spans de la trace :

$$
\sum_{s} d_{propre}(s) = \sum_{s} d(s) - \sum_{s} \sum_{c \,\in\, \mathrm{enf}(s)} d(c)
$$

Dans la double somme, chaque span autre que la racine apparaît exactement une fois, parce qu'il a exactement un parent ; la racine n'y apparaît jamais, parce qu'elle n'a pas de parent. La double somme vaut donc la somme des durées de tous les spans sauf la racine, et la différence se réduit à d(racine). L'identité est purement algébrique : elle ne suppose rien sur les horloges. Sur la trace du programme, 9 + 1 260 + 30 + 1 277,5 + 120 + 2 195 = 4 891,5 ms, la durée de la racine. Les 9 ms propres à la racine sont les trois préparations de requête de 3 ms, faites hors des spans du modèle.

Ce qui n'est pas garanti, c'est le **signe** du temps propre. Si deux appels d'outils s'exécutent en parallèle pendant 100 ms chacun, sous un parent qui dure 100 ms, le temps propre du parent vaut 100 − 200 = −100 ms. Dans ce cas, on ne lit plus la trace par les temps propres mais par le **chemin critique**, la plus longue chaîne d'enfants qui se suivent.

### 2. Le coût d'une exécution, tour par tour, et le piège du double comptage

Au tour 1, le préfixe de 1 000 tokens (prompt système et outils) est écrit dans le cache, et 200 tokens de question sont lus sans cache ; aux tours 2 et 3, le préfixe est relu dans le cache, et l'historique non mis en cache passe à 550 puis à 900 tokens. Avec la formule de l'étape 72 :

$$
C_1 = 3 \times 10^{-6} \left(200 + 1{,}25 \times 1\,000\right) + 15 \times 10^{-6} \times 60 = 0{,}00435 + 0{,}0009 = 0{,}00525
$$

De même, C₂ = 3 × 10⁻⁶ × (550 + 0,10 × 1 000) + 15 × 10⁻⁶ × 60 = 0,00285, et C₃ = 3 × 10⁻⁶ × (900 + 100) + 15 × 10⁻⁶ × 120 = 0,0048. L'exécution coûte 0,0129 USD, contre 3 × 10⁻⁶ × 4 650 + 15 × 10⁻⁶ × 240 = 0,01755 USD sans cache. Le span du tour 1 coûte plus cher que celui du tour 2 alors qu'il lit moins de tokens : c'est l'écriture du cache, visible seulement si la trace porte les compteurs de cache.

Le piège est dans les conventions. Dans l'usage d'une réponse de l'API Messages, `input_tokens` **exclut** les tokens de cache ; dans les attributs des conventions GenAI d'OpenTelemetry, tels que les décrit la documentation de l'éditeur, `gen_ai.usage.input_tokens` les **inclut**, et les attributs de cache en détaillent une partie. Le programme suit la seconde convention dans ses spans : le modèle a lu 1 200 + 1 550 + 1 900 = 4 650 tokens. Un tableau de bord qui additionne `gen_ai.usage.input_tokens` et les deux attributs de cache compte 4 650 + 3 000 = 7 650 tokens, soit 64 % de trop. On choisit une convention, on l'écrit, et l'on ne somme qu'une source par requête.

### 3. Percentiles : la moyenne trompe, et les p95 ne s'additionnent pas

Sur les 20 latences de l'exemple canonique (120, 95, 180, 240, 110, 130, 105, 900, 150, 99, 101, 140, 160, 170, 115, 125, 135, 145, 155, 165 ms), la somme vaut 3 540, donc la moyenne 177 ms. Triées, la 10ᵉ valeur, de rang ⌈0,5 × 20⌉ = 10, vaut 135 ms, et la 19ᵉ, de rang ⌈0,95 × 20⌉ = 19, vaut 240 ms. La moyenne dépasse la médiane de 42 ms à cause d'une seule valeur, 900 ms : elle ne décrit ni la requête typique, ni la pire. On suit donc p50 pour le cas typique, p95 pour l'expérience des utilisateurs les moins bien servis, et le maximum à part.

Un percentile ne se compose pas comme une moyenne. Si X et Y sont parfaitement corrélées (l'une grande exactement quand l'autre l'est), les quantiles s'additionnent. Indépendantes, rien n'est garanti dans un sens ni dans l'autre. Contre-exemple : X et Y valent 0 avec une probabilité de 0,96 et 100 avec une probabilité de 0,04. Le p95 de chacune vaut 0, puisque P(X = 0) = 0,96 ≥ 0,95. Mais

$$
\Pr(X + Y > 0) = 1 - 0{,}96^{2} = 0{,}0784 > 0{,}05
$$

donc le p95 de X + Y vaut 100, alors que la somme des p95 vaut 0. Dans l'autre sens, sur la semaine simulée, la somme des p95 des cinq étapes d'une exécution vaut 7 169 ms, alors que le p95 de la durée totale vaut 6 623 ms : les étapes lentes ne tombent pas toutes dans la même exécution. Deux conséquences pratiques : on ne fabrique pas le p95 d'un agent en additionnant les p95 de ses étapes, et l'on ne moyenne pas les p95 de plusieurs instances. On fusionne les valeurs brutes, ou des histogrammes, puis on calcule le percentile.

### 4. Le budget d'erreur se lit sur les traces, pas sur le statut final

L'objectif est que 99 % des exécutions soient bonnes : terminées, sans aucun span en erreur et en moins de 8 s. Le statut « fini » ne suffit pas. Quand l'outil `ratio_endettement` expire, `executer_agent` renvoie l'erreur au modèle et l'exécution peut tout de même se terminer ; seul le span en erreur révèle que la réponse finale ne s'appuie pas sur un résultat d'outil. La semaine de référence compte 4 exécutions mauvaises sur 400 : 2 erreurs d'outil et 2 exécutions de plus de 8 s. A_obs = 0,99, d'où v = 0,01 / 0,01 = 1 : on consomme le budget exactement au rythme permis. La semaine courante en compte 7, d'où A_obs = 0,9825 et v = 0,0175 / 0,01 = 1,75 : à ce rythme, un budget de 30 jours est épuisé en 30 / 1,75 ≈ 17,1 jours (raisonnement de l'étape 49).

### 5. Le PSI est la somme des deux divergences de Kullback-Leibler, donc il est positif

On développe le produit de la définition, puis on regroupe chaque moitié en divergence de l'étape 50 :

$$
\sum_i (p_i - q_i)\ln\frac{p_i}{q_i} = \sum_i p_i \ln\frac{p_i}{q_i} + \sum_i q_i \ln\frac{q_i}{p_i} = D_{KL}(p \parallel q) + D_{KL}(q \parallel p)
$$

La seconde égalité vient de ce que −ln(pᵢ/qᵢ) = ln(qᵢ/pᵢ). Chaque divergence est positive ou nulle, et nulle seulement si p = q, par l'inégalité de Gibbs démontrée à l'étape 50 : le PSI est donc positif ou nul, et nul seulement si p = q. On le voit aussi terme à terme, sans Gibbs : le logarithme étant croissant, pᵢ − qᵢ et ln(pᵢ/qᵢ) ont toujours le même signe, si bien que chaque terme est positif ou nul. Contrairement à la KL, le PSI est **symétrique** : échanger p et q ne change pas la somme. Il est infini dès qu'une case est vide d'un seul côté ; on construit donc les cases sur la référence, par exemple ses déciles, pour qu'aucune ne soit vide, et l'on documente tout lissage éventuel.

Exemple à la main, avec p = (0,5 ; 0,3 ; 0,2) et q = (0,3 ; 0,3 ; 0,4) :

$$
\mathrm{PSI} = 0{,}2 \ln\frac{0{,}5}{0{,}3} + 0 + (-0{,}2) \ln\frac{0{,}2}{0{,}4} = 0{,}10217 + 0{,}13863 = 0{,}2408
$$

D_KL(p‖q) = 0,5 ln(5/3) + 0,2 ln(1/2) = 0,25541 − 0,13863 = 0,1168, et D_KL(q‖p) = 0,3 ln 0,6 + 0,4 ln 2 = −0,15325 + 0,27726 = 0,1240 ; la somme redonne 0,2408. Avec les seuils usuels, sous 0,1 la population est jugée stable, entre 0,1 et 0,25 elle est à surveiller, au-delà elle a dérivé. Ces seuils sont une **règle empirique** issue de la pratique des grilles de score de crédit, pas un test statistique : 0,2408 est « à surveiller ».

### 6. Sans aucune dérive, le PSI d'un petit échantillon n'est pas nul

Supposons que la fenêtre courante soit tirée de la même loi p, sur M observations : q̂ᵢ = pᵢ + εᵢ, où εᵢ est une erreur d'échantillonnage. Pour un petit ε, ln(1 + x) ≈ x, donc ln(pᵢ/q̂ᵢ) ≈ −εᵢ/pᵢ, et chaque terme du PSI vaut environ (−εᵢ)(−εᵢ/pᵢ) = εᵢ²/pᵢ :

$$
\mathrm{PSI}(p, \hat{q}) \approx \sum_i \frac{\varepsilon_i^{2}}{p_i}
$$

Le compte de la case i suit une loi binomiale (étape 4) de paramètres M et pᵢ, donc la proportion q̂ᵢ a une variance pᵢ(1 − pᵢ)/M, et l'espérance de εᵢ² vaut cette variance. En prenant l'espérance de la somme :

$$
\mathbb{E}\left[\mathrm{PSI}\right] \approx \sum_i \frac{p_i (1 - p_i)}{M\, p_i} = \frac{1}{M}\sum_i (1 - p_i) = \frac{B - 1}{M}
$$

Avec B = 10 déciles et M = 100 requêtes, le bruit seul donne déjà 0,09 en moyenne ; le programme mesure 0,0948 sur 300 fenêtres, et 39 % des fenêtres dépassent le seuil de 0,1 **sans aucune dérive**. Avec M = 1 000, le bruit tombe à 0,009 (mesuré : 0,0088) et aucune fenêtre ne dépasse 0,1. Les seuils de 0,1 et 0,25 supposent donc des fenêtres de plusieurs centaines d'observations au moins ; sur une petite fenêtre, on compare le PSI à (B − 1)/M, ou l'on calcule sa loi sous l'hypothèse « pas de dérive » par permutation.

### 7. La dérive des entrées précède celle des coûts

La semaine de référence compte 19,5 % de questions en arabe, la semaine courante 42,25 %. Sur la langue :

$$
\mathrm{PSI} = 0{,}2275 \ln\frac{0{,}805}{0{,}5775} + 0{,}2275 \ln\frac{0{,}4225}{0{,}195} = 0{,}0756 + 0{,}1759 = 0{,}2515
$$

au-dessus de 0,25 : la population a dérivé. Sur les tokens d'entrée par exécution, découpés en déciles de la référence, le PSI vaut 0,1209 (« à surveiller ») : le dernier décile passe de 10,5 % à 21,2 % des exécutions, parce qu'une question en arabe compte, dans cette simulation, 35 % de tokens de plus (facteur illustratif ; le vrai facteur dépend du tokeniseur, étape 2 bis). Le coût moyen, lui, ne monte que de 0,014002 à 0,014275 USD, soit 2 %, parce que le préfixe en cache domine. L'indicateur de coût réagit à peine, alors que l'agent reçoit déjà un trafic sur lequel il n'a pas été évalué : c'est la dérive des entrées qui doit déclencher une nouvelle évaluation (étape 13 bis), et non l'attente d'une hausse de la facture ou des plaintes.

### 8. Exemple fait à la main (le code reprend ces nombres)

| Grandeur | Calcul | Résultat |
|---|---|---|
| durée de la racine | 9 + 1 260 + 30 + 1 277,5 + 120 + 2 195 | 4 891,5 ms |
| coût des trois tours | 0,00525 + 0,00285 + 0,0048 | 0,0129 USD |
| même exécution sans cache | 4 650 × 3 × 10⁻⁶ + 240 × 15 × 10⁻⁶ | 0,01755 USD |
| tokens comptés deux fois | 4 650 + 1 000 + 2 000 | 7 650 au lieu de 4 650 |
| moyenne, p50, p95 des 20 latences | 3 540 / 20 ; 10ᵉ ; 19ᵉ valeur triée | 177 ; 135 ; 240 ms |
| contre-exemple d'additivité | 1 − 0,96² = 0,0784 > 0,05 | p95(X + Y) = 100, somme des p95 = 0 |
| vitesse de consommation | 0,0175 / 0,01 | 1,75 |
| PSI de l'exemple | 0,10217 + 0,13863 | 0,2408 |
| bruit pour B = 10, M = 100 | 9 / 100 | 0,09 |

## Effets et comportement

- **Plus une trace porte d'attributs, plus elle explique, et plus elle coûte** à stocker et à protéger : les prompts complets dans les spans sont précieux pour déboguer et dangereux pour la confidentialité.
- **Le p95 réagit aux queues que la moyenne écrase.** Un outil lent dans 2 % des cas déplace peu la moyenne, mais il déplace le p95 dès que sa part dépasse 5 %, puisque le p95 est la frontière des 5 % les plus lents.
- **Un objectif plus strict raccourcit le budget.** Passer de 99 % à 99,9 % divise le nombre d'exécutions mauvaises autorisées par dix, et multiplie v par dix pour le même trafic.
- **Le PSI grandit avec le nombre de cases à dérive égale**, et son bruit aussi, en (B − 1)/M : plus de cases donnent plus de détail, pas plus de certitude.
- **Le PSI ne dit pas où est la dérive.** On regarde les termes (pᵢ − qᵢ) ln(pᵢ/qᵢ) case par case, et l'on surveille plusieurs variables séparément (langue, longueur, outil choisi, raison d'arrêt).

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| s, trace, parent | `Span`, `trace_id`, `parent_id` |
| ouvrir et fermer un span | `Traceur.span(nom, **attributs)` |
| d(s), d propre | `Span.duree_ms`, `temps_propre(s, par_parent)` |
| enf(s) | `enfants(spans)[s.span_id]` |
| N in, N écrit, N lu, N out | champs de `ReponseMesuree.usage` |
| C(s) | `cout_usd(usage)` |
| p50, p95 | `p50(valeurs)`, `p95(valeurs)` (canonique) |
| v | `taux_de_consommation(mauvais, total, slo)` |
| D KL, PSI | `kl(p, q)`, `psi(p, q)`, `classer_psi(v)` |
| p, q sur des déciles | `statistics.quantiles(..., n=10)`, `histogramme(valeurs, bornes)` |
| traceparent | `Traceur.traceparent()` |

### Déroulé, ligne par ligne

**Le code canonique** (`Bloc`, `Reponse`, `texte`, `appel_outil`, `FakeLLM`, `executer_agent`, `p95`, `mensualite`, `ratio_endettement`) est recopié tel quel du parcours. La boucle n'est jamais modifiée : toute l'observabilité passe par les deux ports qu'elle reçoit, le LLM et le dictionnaire d'outils.

**`Horloge`** compte des millisecondes simulées ; les durées des appels sont calculées, pas mesurées, ce qui rend chaque trace reproductible.

**`Span`** est une `dataclass` : identifiants, nom, début, fin, attributs, statut ; `duree_ms` est une propriété calculée.

**`Traceur.span(nom, **attributs)`** est un *context manager* écrit avec `@contextmanager`.

- Le parent est le dernier span ouvert, en haut de `pile` ; un span sans parent ouvre une nouvelle trace, avec un `trace_id` de 16 octets (32 caractères hexadécimaux), et chaque span reçoit un `span_id` de 8 octets, tirés d'un générateur à graine.
- Le `yield` rend la main au bloc `with`. Si ce bloc lève une exception, le span passe en statut `"erreur"`, note le type et le message, puis relance l'exception : l'observabilité ne doit jamais changer le comportement de l'agent.
- Le `finally` date la fin, dépile, et range le span dans `spans` ; les spans sont donc rangés dans l'ordre où ils se **ferment**, les enfants avant leur parent.

**`Traceur.traceparent()`** fabrique l'en-tête du standard W3C Trace Context, `00-<trace_id>-<span_id>-01`, à recopier dans les en-têtes d'un événement publié (étape 45 bis) ou d'une requête sortante.

**`ReponseMesuree`** hérite de `Reponse` et ajoute `usage`, le dictionnaire de tokens d'une réponse de l'API. **`cout_usd(u)`** applique C(s) : pour le tour 1, 200 × 3 × 10⁻⁶ + 1 000 × 1,25 × 3 × 10⁻⁶ + 60 × 15 × 10⁻⁶ = 0,00525 USD.

**`LLMInstrumente.create`** a la même signature que `FakeLLM.create` ou que l'adaptateur Claude du parcours. Elle avance l'horloge de 3 ms de préparation, ouvre un span `llm.create` avec le numéro du tour, appelle le vrai port, calcule les tokens lus (`entree = input + lu + ecrit`, 1 200 au tour 1), une durée simulée de 300 + 0,05 × entrée + 15 × sortie millisecondes (1 260 ms au tour 1), éventuellement multipliée par un bruit, puis range les attributs : les tokens sous les noms des conventions GenAI, le coût et la raison d'arrêt.

**`instrumenter_outils`** renvoie un nouveau dictionnaire d'outils. Chaque fonction est enveloppée dans un span `outil.<nom>` qui avance l'horloge de la latence de l'outil et peut simuler un `TimeoutError`. Le span note l'erreur, puis `executer_agent` la reçoit et la renvoie au modèle, comme sans instrumentation.

**`script_credit(q, sortie_finale)`** écrit les trois réponses du faux LLM, avec leur usage : `q` tokens de question au tour 1 plus 1 000 écrits en cache, puis `q + 350` et `q + 700` tokens non mis en cache avec 1 000 lus dans le cache. **`executer_trace`** ouvre le span racine, appelle `executer_agent` avec les ports instrumentés et note le statut et le nombre d'étapes.

**`enfants`**, **`temps_propre`** et **`arbre`** relisent une trace : `enfants` range les spans par parent, triés par début ; `temps_propre` soustrait la durée des enfants ; `arbre` imprime l'arbre en profondeur, avec deux espaces par niveau.

**`exporter`** écrit une ligne JSON par span, à clés triées, après avoir remplacé tout numéro d'Emirates ID (`784-AAAA-NNNNNNN-C`) par un masque. Le masquage a lieu **avant** que la donnée ne quitte le processus.

**`p50`** suit la même règle de rang que la fonction canonique `p95`. **`agreger`** regroupe les spans par nom et calcule n, p50, p95, le coût et le nombre d'erreurs. **`taux_de_consommation`** renvoie `None` sans trafic, selon la convention du parcours pour une métrique sans dénominateur.

**`kl`** et **`psi`** suivent les définitions : `kl` renvoie l'infini quand q s'annule là où p ne s'annule pas ; `psi` refuse deux listes de tailles différentes ou qui ne somment pas à 1, ignore une case vide des deux côtés et renvoie l'infini pour une case vide d'un seul côté. **`classer_psi`** applique les seuils de 0,1 et 0,25. **`histogramme`** range chaque valeur dans sa case par `bisect.bisect_right` sur les bornes.

**`simuler(n, part_arabe, graine)`** joue n exécutions avec un générateur à graine : langue tirée au hasard, facteur de tokens de 1,35 pour l'arabe, bruit log-normal sur la durée du modèle, outil `ratio_endettement` lent (2 500 ms) dans 2 % des appels et en erreur dans 1 %. Elle renvoie le traceur et, par exécution, la durée, le statut, la langue, la présence d'une erreur, les tokens lus et le coût.

**`main()`**, section par section.

1. Une exécution sans bruit, avec une question qui contient un Emirates ID. L'arbre a une racine et cinq enfants ; la racine dure 4 891,5 ms, dont 9 ms propres, et la somme des temps propres redonne exactement cette durée. Les coûts des tours valent 0,00525, 0,00285 et 0,0048 USD.
2. 4 650 tokens lus, 7 650 si l'on rajoute les attributs de cache. Le `traceparent` d'un span de publication respecte le format W3C, et l'export ne contient plus aucun Emirates ID en clair.
3. 400 exécutions de la semaine de référence : p50 et p95 par type de span, coût par exécution, comparaison entre le p95 de la durée totale (6 623 ms) et la somme des p95 des cinq étapes (7 169 ms), puis les 20 latences et le contre-exemple d'additivité.
4. Budget d'erreur sur les deux semaines : v = 1,00, puis 1,75.
5. L'exemple à la main du PSI, sa décomposition en deux KL, sa symétrie, puis la dérive de la langue (0,2515) et des tokens (0,1209).
6. 300 fenêtres de 100, puis de 1 000 observations tirées de la loi uniforme sur 10 cases : PSI moyen proche de 9/M.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`texte(t)`** — Cette petite fonction du code canonique est le greffier qui met en forme une réplique du faux modèle : elle reçoit une chaîne de caractères et renvoie un `Bloc` de type « text » dont le champ `text` contient cette chaîne, les autres champs restant vides. Elle sert ici à écrire la dernière réponse du script de `script_credit`, « Mensualité 5 558,32 AED ; endettement 28,9 % ≤ 50 %. », que la boucle d'agent lira comme la réponse finale.

**`appel_outil(nom, arguments, id_)`** — Celle-ci rédige, comme un standardiste qui remplit un bon de commande, la demande d'outil qu'un vrai modèle enverrait : elle reçoit le nom de l'outil, le dictionnaire de ses arguments et un identifiant, et renvoie un `Bloc` de type « tool_use » qui range ces trois informations dans `name`, `input` et `id`. Dans `script_credit`, elle fabrique l'appel « t1 » à `mensualite` pour 1 000 000 AED à 4,5 % sur 300 mois, puis l'appel « t2 » à `ratio_endettement`.

**`FakeLLM.__init__(script)`** — Le constructeur prépare un comédien qui ne connaît que son texte : il reçoit la liste des réponses prévues, en garde une copie dans `self.script`, pour ne jamais modifier la liste d'origine, et met à zéro le compteur `self.appels` des répliques déjà jouées. Il ne renvoie rien ; c'est cet état minimal qui rend le faux modèle déterministe et gratuit, si bien que chaque trace de ce fichier se reproduit à l'identique d'une exécution à l'autre.

**`FakeLLM.create(system, messages, tools)`** — Cette méthode imite l'appel d'API d'un modèle de langage, comme un souffleur qui tend la réplique suivante sans écouter ce qu'on lui dit : elle reçoit, par mots-clés seulement, le prompt système, l'historique et les outils, les ignore, puis renvoie la réponse scriptée de rang `self.appels` en avançant le compteur. Quand le script est épuisé, elle lève une `RuntimeError` au lieu d'inventer une réponse ; dans ce fichier, c'est elle que `LLMInstrumente.create` appelle à l'intérieur de son span.

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — C'est la boucle canonique de l'agent, recopiée telle quelle et jamais modifiée, qui joue le chef de chantier faisant la navette entre le modèle et ses outils : elle reçoit le modèle, le prompt système, la question, le dictionnaire des outils, leurs schémas et au plus huit étapes par défaut, puis, à chaque tour, demande une réponse, l'ajoute à l'historique, s'arrête sur un refus, une troncature ou une réponse finale, et sinon exécute les outils demandés en renvoyant au modèle leur résultat en JSON ou l'erreur marquée `is_error`. Elle arrête aussi une boucle qui répète deux fois le même appel, et renvoie un dictionnaire avec le statut, la trace et le nombre d'étapes ; toute l'observabilité de ce fichier passe par les deux ports qu'elle reçoit, sans toucher à son code.

**`p95(valeurs)`** — Cette fonction canonique est le juge de ligne qui ne regarde que les retardataires : elle reçoit une liste de durées ou de coûts, lève une `ValueError` si elle est vide, la trie et renvoie la valeur de rang ⌈0,95 × N⌉, le percentile 95 au rang le plus proche. Sur les 20 latences de la section 3, elle rend 240 ms alors que la moyenne vaut 177 ms, et le contre-exemple de `main` montre qu'elle n'est pas additive : p95(X) + p95(Y) vaut 0 alors que p95(X + Y) vaut 100.

**`mensualite(principal, taux_annuel, n_mois)`** — Celle-ci est le banquier du parcours, recopié tel quel, qui calcule la traite mensuelle d'un prêt amortissable : elle reçoit le capital, le taux annuel et la durée en mois, lève une `ValueError` si le capital ou la durée ne sont pas positifs ou si le taux est négatif, puis renvoie P × r / (1 − (1 + r)⁻ⁿ) avec r le taux mensuel, ou simplement P/n si le taux est nul. Pour 1 000 000 AED à 4,5 % sur 300 mois, elle donne 5 558,32 AED, le premier outil appelé par l'agent crédit.

**`ratio_endettement(mensualites_existantes, nouvelle_mensualite, revenu_mensuel, plafond)`** — Cette fonction est l'analyste crédit qui vérifie que le client ne s'étrangle pas : elle reçoit les mensualités déjà en cours, la nouvelle mensualité, le revenu mensuel et un plafond de 0,50 par défaut, lève une `ValueError` si le revenu n'est pas positif, puis renvoie le ratio de toutes les mensualités sur le revenu et un booléen qui dit s'il reste sous le plafond. Avec 6 000 AED existants, 5 558,32 AED nouveaux et 40 000 AED de revenu, le ratio vaut environ 0,289, soit 28,9 %, bien sous les 50 %.

**`Horloge.__init__()`** — Le constructeur pose sur la table une montre arrêtée à zéro : il ne reçoit rien et initialise l'attribut `t`, le temps courant en millisecondes simulées. Aucune heure réelle n'est jamais lue dans ce programme, si bien que toutes les durées des spans sont calculées et non mesurées, ce qui rend chaque trace reproductible au dixième de milliseconde près, comme les 4 891,5 ms de la racine dans la section 1 de `main`.

**`Horloge.avancer(ms)`** — Cette méthode est la main qui fait tourner l'aiguille de la montre simulée : elle reçoit un nombre de millisecondes et l'ajoute au temps courant `t`, sans rien renvoyer. Les 3 ms de préparation d'une requête, la durée calculée d'un appel au modèle et la latence d'un outil passent toutes par elle, et c'est la valeur de `t` au moment où un span s'ouvre puis se ferme qui fixe son début et sa fin.

**`Span.duree_ms()`** — Cette propriété calculée est le chronométreur d'un span, qui lit les deux dates inscrites sur sa fiche : elle ne reçoit rien d'autre que le span lui-même et renvoie la fin moins le début, en millisecondes simulées. Elle n'est pas stockée mais recalculée à chaque lecture, si bien qu'elle reste juste après la fermeture du span ; `temps_propre`, `agreger` et `simuler` s'en servent pour mesurer chaque appel, chaque outil et chaque exécution entière.

**`Traceur.__init__(horloge, graine)`** — Le constructeur installe le greffier des traces dans son bureau : il reçoit l'horloge simulée et une graine, garde l'horloge, crée un générateur pseudo-aléatoire à cette graine pour que les identifiants soient reproductibles, et prépare deux listes vides, `spans` pour les spans fermés et `pile` pour ceux qui sont encore ouverts. Il ne renvoie rien ; dans la section 1, `main` l'appelle avec la graine 1, et `simuler` avec la graine de sa semaine.

**`Traceur._id(octets)`** — Cette méthode est le graveur de numéros de série : elle reçoit un nombre d'octets, tire au générateur du traceur autant de bits aléatoires que huit fois ce nombre, et renvoie cette valeur écrite en hexadécimal sur deux caractères par octet, avec les zéros de tête. Elle produit ainsi un `trace_id` de 16 octets, soit 32 caractères, pour chaque nouvelle trace, et un `span_id` de 8 octets, soit 16 caractères, pour chaque span, les formats qu'exige l'en-tête W3C vérifié dans la section 2.

**`Traceur.span(nom, attributs)`** — Ce gestionnaire de contexte est l'huissier qui ouvre et ferme chaque séance : il reçoit le nom du span et des attributs nommés, prend pour parent le dernier span ouvert, crée un `Span` qui hérite du `trace_id` du parent ou en tire un nouveau s'il n'y en a pas, le date avec l'horloge, l'empile et le cède au bloc `with`. Si ce bloc lève une exception, il passe le span en statut « erreur », note le type et le message, puis relance l'exception sans l'avaler ; dans tous les cas, il date la fin, dépile et range le span dans `spans`, si bien que les enfants y apparaissent avant leur parent.

**`Traceur.traceparent()`** — Cette méthode est le tampon qu'on appose sur une lettre pour que le destinataire sache de quelle affaire elle relève : elle ne reçoit rien, lit le span au sommet de la pile et renvoie l'en-tête du standard W3C Trace Context, composé de « 00 », du `trace_id`, du `span_id` et de « 01 », séparés par des tirets. On le recopie dans un événement publié ou une requête sortante pour rattacher la suite du travail à la même trace ; `main` vérifie qu'il a bien 32 puis 16 caractères hexadécimaux.

**`cout_usd(u)`** — Cette fonction est la caisse enregistreuse de chaque tour de modèle : elle reçoit le dictionnaire `usage` d'une réponse, facture les tokens d'entrée non mis en cache au prix d'entrée de 3 USD le million, les tokens écrits en cache à 1,25 fois ce prix, les tokens lus dans le cache à 0,10 fois ce prix et les tokens de sortie à 15 USD le million, et renvoie la somme en USD. Pour le tour 1, 200 tokens, 1 000 écrits et 60 en sortie donnent 0,00525 USD ; les tours 2 et 3 coûtent 0,00285 et 0,0048 USD, soit 0,0129 USD pour l'exécution.

**`LLMInstrumente.__init__(llm, traceur, horloge, bruit)`** — Le constructeur branche un compteur sur le port du modèle, comme un électricien qui pose un wattmètre sans toucher à l'appareil : il reçoit le vrai modèle, le traceur, l'horloge et une fonction de bruit facultative, absente par défaut, qui multipliera les durées simulées, puis range ces quatre éléments et met à zéro le compteur de tours. Il ne renvoie rien ; l'objet obtenu a la même méthode `create` que le modèle qu'il enveloppe, si bien que `executer_agent` l'utilise sans savoir qu'il est observé.

**`envelopper(nom, f)`** — Cette fonction interne, qui vit dans `instrumenter_outils`, est le tailleur qui coud une doublure de mesure autour de chaque outil : elle reçoit le nom de l'outil et la fonction d'origine, et renvoie une nouvelle fonction, `appel`, qui garde en mémoire ce nom et cette fonction. Passer par elle plutôt que d'écrire la fonction interne directement dans la compréhension de dictionnaire évite le piège classique des fermetures en Python, où toutes les enveloppes finiraient par appeler le dernier outil de la boucle.

**`appel(kwargs)`** — Cette fonction interne, fabriquée par `envelopper`, est l'outil tel que la boucle d'agent le voit, avec une caméra fixée dessus : elle reçoit les arguments nommés que le modèle a choisis, ouvre un span « outil.nom » avec le nom de l'outil en attribut, avance l'horloge de la latence de cet outil, lève une `TimeoutError` si la fonction `en_erreur` le décide, et sinon appelle l'outil d'origine et renvoie son résultat. Le span note l'erreur éventuelle, puis `executer_agent` la reçoit et la renvoie au modèle exactement comme sans instrumentation.

**`outils_credit()`** — Celle-ci est l'armurier qui remet à l'agent sa boîte à outils de crédit : elle ne reçoit rien et renvoie un dictionnaire de deux fonctions, `mensualite`, qui arrondit la traite au centime, et `ratio_endettement`, qui ne garde que le ratio arrondi à quatre décimales et prend des arguments aux noms plus courts, existantes, nouvelle et revenu. Ce sont ces deux outils que `instrumenter_outils` enveloppe dans la section 1 de `main` comme dans chaque exécution de `simuler`.

**`executer_trace(traceur, llm, question, outils)`** — Cette fonction est le metteur en scène qui ouvre le rideau et le referme sur une exécution entière : elle reçoit le traceur, le modèle instrumenté, la question et les outils instrumentés, ouvre le span racine « agent.executer » avec la question en attribut, lance `executer_agent` avec le prompt « Agent crédit », puis note sur la racine le statut et le nombre d'étapes. Elle renvoie le résultat de la boucle et le span racine ; dans la section 1, la racine dure 4 891,5 ms et compte cinq enfants, trois appels au modèle et deux appels d'outils.

**`enfants(spans)`** — Celle-ci est l'archiviste qui reconstitue l'arbre généalogique d'une trace à partir de fiches en vrac : elle reçoit une liste de spans, les trie par date de début et les range dans un dictionnaire dont chaque clé est l'identifiant d'un parent, la clé `None` regroupant les racines. Elle renvoie ce dictionnaire, où les enfants de chaque span apparaissent dans l'ordre chronologique ; `temps_propre`, `arbre` et la section 3 de `main` s'en servent pour descendre d'un span vers ses enfants.

**`temps_propre(s, par_parent)`** — Cette fonction est le comptable qui sépare le temps qu'un service a passé à travailler lui-même de celui qu'il a délégué : elle reçoit un span et le dictionnaire de `enfants`, et renvoie la durée du span moins la somme des durées de ses enfants directs. Pour la racine de la section 1, il reste 9 ms, les trois préparations de 3 ms, et `main` vérifie que la somme des temps propres de tous les spans redonne exactement les 4 891,5 ms de la racine.

**`arbre(spans)`** — Celle-ci est le dessinateur qui met une trace sous forme d'organigramme lisible : elle reçoit une liste de spans, construit le dictionnaire des enfants, puis lance la visite en profondeur à partir de chaque racine et renvoie la liste des lignes de texte obtenues. Chaque ligne indique le nom du span, décalé de deux espaces par niveau, son début, sa fin et son temps propre, plus les tokens et le coût pour un appel au modèle, comme dans la sortie de la section 1.

**`visiter(s, profondeur)`** — Cette fonction interne, qui vit dans `arbre`, est le guide qui parcourt l'organigramme étage par étage : elle reçoit un span et sa profondeur, prépare un détail avec les tokens d'entrée, de sortie et le coût lorsque le span est un « llm.create », ajoute à la liste `lignes` de la fonction englobante une ligne alignée en colonnes, puis s'appelle elle-même sur chaque enfant avec une profondeur augmentée de un. Elle ne renvoie rien ; c'est cette récursion qui imprime la racine, puis ses cinq enfants indentés, dans l'ordre où ils ont commencé.

**`exporter(spans)`** — Celle-ci est le service courrier qui caviarde les lettres avant qu'elles ne quittent le bâtiment : elle reçoit une liste de spans et, pour chacun, remplace dans tout attribut textuel chaque numéro d'Emirates ID par un masque d'astérisques, puis sérialise le span en une ligne JSON à clés triées, avec ses identifiants, son nom, ses dates, son statut et ses attributs. Elle renvoie la liste de ces lignes ; dans la section 2, les six lignes de la trace ne contiennent plus aucun numéro en clair, alors que la question d'origine en portait un.

**`p50(valeurs)`** — Cette fonction est la jumelle de `p95` pour le milieu de la distribution : elle reçoit une liste, lève une `ValueError` si elle est vide, la trie et renvoie la valeur de rang ⌈0,5 × N⌉, la médiane au rang le plus proche, selon la même règle que la fonction canonique. Sur les 20 latences de la section 3, elle rend 135 ms, et `agreger` l'utilise pour donner la durée typique de chaque type de span, à côté de son p95.

**`agreger(spans)`** — Celle-ci est le statisticien de fin de semaine qui dépouille toutes les fiches d'une période : elle reçoit une liste de spans, les regroupe par nom, et renvoie pour chaque nom, dans l'ordre alphabétique, le nombre de spans, le p50 et le p95 de leurs durées, leur coût total et le nombre de spans en erreur. Sur la semaine de référence, elle compte 400 exécutions et 1 200 appels au modèle, et le p95 de la durée totale, 6 623 ms, reste sous la somme des p95 des cinq étapes, 7 169 ms.

**`taux_de_consommation(mauvais, total, slo)`** — Cette fonction est la jauge du budget d'erreur, qui dit à quelle vitesse on brûle la marge que l'objectif autorise : elle reçoit le nombre d'exécutions mauvaises, le nombre total et l'objectif de disponibilité, renvoie `None` quand il n'y a eu aucun trafic, faute de dénominateur, et sinon le taux d'échec observé divisé par 1 − objectif. Avec un objectif de 99 %, 10 mauvaises sur 400 donnent 2,5 ; la semaine de référence, 4 sur 400, consomme au rythme 1,00 et la semaine courante, 7 sur 400, au rythme 1,75.

**`kl(p, q)`** — Celle-ci mesure de combien une loi q trahit une loi p, comme un traducteur qui compte les nuances perdues : elle reçoit deux distributions de même taille, lève une `ValueError` sinon, additionne pᵢ ln(pᵢ/qᵢ) sur les cases où p n'est pas nulle, et renvoie l'infini dès qu'une case possible sous p est impossible sous q. Elle sert à vérifier, dans la section 5, que le PSI de l'exemple à la main égale exactement KL(p‖q) + KL(q‖p).

**`psi(p, q)`** — Cette fonction est le sismographe de la dérive, qui compare la distribution d'une variable entre deux périodes : elle reçoit deux distributions, refuse par une `ValueError` des tailles différentes ou des sommes qui s'écartent de 1 de plus de 10⁻⁹, ignore une case vide des deux côtés, renvoie l'infini pour une case vide d'un seul côté, et sinon la somme des (pᵢ − qᵢ) ln(pᵢ/qᵢ). Pour 0,5 ; 0,3 ; 0,2 contre 0,3 ; 0,3 ; 0,4, elle donne 0,2408, symétrique en p et q, et sur les deux semaines simulées 0,2515 pour la langue et 0,1209 pour les tokens d'entrée.

**`classer_psi(v)`** — Celle-ci est le feu tricolore posé sur le sismographe : elle reçoit une valeur de PSI et renvoie « stable » sous 0,1, « à surveiller » de 0,1 à moins de 0,25, et « dérive » à partir de 0,25, des seuils usuels qui sont une règle empirique et non un test statistique. L'exemple à la main, à 0,2408, est donc à surveiller, la langue, à 0,2515, est en dérive, et les tokens, à 0,1209, sont à surveiller.

**`proportions(valeurs, cases)`** — Cette fonction est le recenseur qui compte la part de chaque catégorie dans une population : elle reçoit une liste de valeurs et la liste des catégories à compter, et renvoie, pour chaque catégorie dans l'ordre donné, le nombre de valeurs qui lui sont égales divisé par le nombre total de valeurs. Elle transforme les langues des 400 exécutions de chaque semaine en une distribution sur « en » et « ar », que `psi` compare ensuite pour détecter la dérive : la probabilité de l'arabe, réglée à 0,20 puis à 0,45 dans `simuler`, donne une part observée de 19,5 % puis de 42,25 %.

**`histogramme(valeurs, bornes)`** — Celle-ci est le trieur postal qui range chaque lettre dans le bon casier selon son poids : elle reçoit des valeurs numériques et une liste croissante de bornes, prépare une case de plus qu'il n'y a de bornes, place chaque valeur dans sa case grâce à `bisect.bisect_right`, et renvoie la proportion de valeurs dans chaque case. Avec les neuf déciles des tokens d'entrée de la semaine de référence comme bornes, elle donne dix cases d'environ 10 % pour cette semaine, et la distribution de la semaine courante dans les mêmes cases, prête pour `psi`.

**`latence(nom)`** — Cette fonction interne, qui vit dans `simuler`, est le dé truqué qui décide combien de temps répond chaque outil : elle reçoit le nom de l'outil et renvoie, pour `ratio_endettement`, qui lit les encours dans le cœur bancaire, 2 500 ms avec la probabilité 0,02 et sinon une durée uniforme entre 80 et 160 ms, et pour tout autre outil une durée uniforme entre 20 et 40 ms. Elle tire ses nombres au générateur à graine de `simuler`, ce qui rend la semaine entière reproductible.

**`en_erreur(nom)`** — Cette autre fonction interne de `simuler` est la panne programmée du banc d'essai : elle reçoit le nom d'un outil et renvoie `True` seulement pour `ratio_endettement`, et seulement avec la probabilité 0,01, auquel cas l'enveloppe de l'outil lève une `TimeoutError` que le span note et que la boucle renvoie au modèle. Elle alimente ainsi les erreurs comptées par `agreger` et les exécutions mauvaises du budget d'erreur de la section 4.

**`main()`** — C'est le responsable de l'exploitation qui passe la journée devant ses tableaux de bord, en six sections : il trace d'abord une exécution sans bruit, imprime l'arbre de six spans et vérifie la durée de 4 891,5 ms, les temps propres et les trois coûts, puis montre qu'il ne faut pas compter le cache deux fois, 4 650 tokens lus et non 7 650, contrôle le `traceparent` et le masquage de l'export. Il simule ensuite deux semaines de 400 exécutions, agrège p50 et p95, calcule le budget d'erreur, 1,00 puis 1,75, mesure la dérive de la langue et des tokens, et termine en montrant qu'un PSI d'échantillon n'est jamais nul sans dérive, proche de 9/M ; chaque résultat est verrouillé par un `assert`.

```python
"""Étape 72 quater — observabilité d'un agent : traces et spans, coûts, p50 et p95, budget d'erreur, dérive (PSI)."""
import bisect
import json
import math
import random
import re
import statistics
import sys
from contextlib import contextmanager
from dataclasses import dataclass, field

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- code canonique du parcours (recopié tel quel)
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


def p95(valeurs: list[float]) -> float:
    """Percentile 95 au rang le plus proche : la valeur de rang ceil(0,95 × N) dans la liste triée."""
    if not valeurs:
        raise ValueError("liste vide")
    s = sorted(valeurs)
    return s[math.ceil(0.95 * len(s)) - 1]


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


# ---------------------------------------------------------------- horloge, spans, traceur
class Horloge:
    """Millisecondes simulées : aucune heure réelle n'est lue."""

    def __init__(self) -> None:
        self.t = 0.0

    def avancer(self, ms: float) -> None:
        self.t += ms


@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_id: str | None
    nom: str
    debut_ms: float
    fin_ms: float = 0.0
    attributs: dict = field(default_factory=dict)
    statut: str = "ok"

    @property
    def duree_ms(self) -> float:
        return self.fin_ms - self.debut_ms


class Traceur:
    """Ouvre des spans imbriqués avec `with` ; le parent est le span ouvert le plus récent."""

    def __init__(self, horloge: Horloge, graine: int) -> None:
        self.horloge = horloge
        self.rng = random.Random(graine)       # identifiants reproductibles
        self.spans: list[Span] = []
        self.pile: list[Span] = []

    def _id(self, octets: int) -> str:
        return f"{self.rng.getrandbits(8 * octets):0{2 * octets}x}"

    @contextmanager
    def span(self, nom: str, **attributs):
        parent = self.pile[-1] if self.pile else None
        s = Span(parent.trace_id if parent else self._id(16), self._id(8), parent.span_id if parent else None,
                 nom, self.horloge.t, attributs=dict(attributs))
        self.pile.append(s)
        try:
            yield s
        except Exception as e:
            s.statut = "erreur"
            s.attributs["erreur"] = f"{type(e).__name__}: {e}"
            raise                              # le span note l'erreur, il ne l'avale pas
        finally:
            s.fin_ms = self.horloge.t
            self.pile.pop()
            self.spans.append(s)

    def traceparent(self) -> str:
        """En-tête W3C Trace Context du span courant, à propager dans un événement ou une requête sortante."""
        s = self.pile[-1]
        return f"00-{s.trace_id}-{s.span_id}-01"


# ---------------------------------------------------------------- instrumentation des ports, sans toucher à la boucle
PRIX_IN, PRIX_OUT = 3 / 1_000_000, 15 / 1_000_000      # USD par token, illustratifs (étape 72)
FACTEUR_LECTURE, FACTEUR_ECRITURE = 0.10, 1.25          # cache lu, cache écrit (étape 72)


@dataclass
class ReponseMesuree(Reponse):
    """Même forme que Reponse, plus le champ usage d'une réponse de l'API (input_tokens n'inclut PAS le cache)."""
    usage: dict = field(default_factory=dict)


def cout_usd(u: dict) -> float:
    return (u["input_tokens"] * PRIX_IN + u.get("cache_creation_input_tokens", 0) * PRIX_IN * FACTEUR_ECRITURE
            + u.get("cache_read_input_tokens", 0) * PRIX_IN * FACTEUR_LECTURE + u["output_tokens"] * PRIX_OUT)


class LLMInstrumente:
    """Adaptateur du port LLM : même méthode create(), plus un span, les tokens, le coût et la durée."""

    def __init__(self, llm, traceur: Traceur, horloge: Horloge, bruit=None) -> None:
        self.llm, self.traceur, self.horloge, self.bruit = llm, traceur, horloge, bruit
        self.tours = 0

    def create(self, *, system: str, messages: list, tools: list):
        self.horloge.avancer(3.0)                          # préparation de la requête : hors du span du modèle
        self.tours += 1
        with self.traceur.span("llm.create", tour=self.tours) as s:
            reponse = self.llm.create(system=system, messages=messages, tools=tools)
            u = reponse.usage
            lu, ecrit = u.get("cache_read_input_tokens", 0), u.get("cache_creation_input_tokens", 0)
            entree = u["input_tokens"] + lu + ecrit       # ce que le modèle a lu, cache compris
            duree = 300 + 0.05 * entree + 15 * u["output_tokens"]
            self.horloge.avancer(duree * (self.bruit() if self.bruit else 1.0))
            s.attributs.update({"gen_ai.usage.input_tokens": entree, "gen_ai.usage.output_tokens": u["output_tokens"],
                                "gen_ai.usage.cache_read.input_tokens": lu,
                                "gen_ai.usage.cache_write.input_tokens": ecrit,
                                "cout_usd": cout_usd(u), "stop_reason": reponse.stop_reason})
        return reponse


def instrumenter_outils(outils: dict, traceur: Traceur, horloge: Horloge, latence_ms, en_erreur) -> dict:
    def envelopper(nom: str, f):
        def appel(**kwargs):
            with traceur.span(f"outil.{nom}", outil=nom):
                horloge.avancer(latence_ms(nom))
                if en_erreur(nom):
                    raise TimeoutError(f"{nom} : délai dépassé")
                return f(**kwargs)
        return appel
    return {nom: envelopper(nom, f) for nom, f in outils.items()}


def outils_credit() -> dict:
    return {"mensualite": lambda principal, taux_annuel, n_mois: round(mensualite(principal, taux_annuel, n_mois), 2),
            "ratio_endettement": lambda existantes, nouvelle, revenu: round(ratio_endettement(existantes, nouvelle, revenu)[0], 4)}


def script_credit(q: int, sortie_finale: int) -> list:
    """Trois tours ; le préfixe de 1 000 tokens est écrit en cache au tour 1, relu aux tours 2 et 3."""
    usages = [{"input_tokens": q, "cache_creation_input_tokens": 1000, "output_tokens": 60},
              {"input_tokens": q + 350, "cache_read_input_tokens": 1000, "output_tokens": 60},
              {"input_tokens": q + 700, "cache_read_input_tokens": 1000, "output_tokens": sortie_finale}]
    return [ReponseMesuree("tool_use", [appel_outil("mensualite", {"principal": 1_000_000, "taux_annuel": 0.045,
                                                                   "n_mois": 300}, "t1")], usages[0]),
            ReponseMesuree("tool_use", [appel_outil("ratio_endettement", {"existantes": 6000, "nouvelle": 5558.32,
                                                                          "revenu": 40000}, "t2")], usages[1]),
            ReponseMesuree("end_turn", [texte("Mensualité 5 558,32 AED ; endettement 28,9 % ≤ 50 %.")], usages[2])]


def executer_trace(traceur: Traceur, llm, question: str, outils: dict) -> tuple[dict, Span]:
    with traceur.span("agent.executer", question=question) as racine:
        r = executer_agent(llm, "Agent crédit", question, outils, [])
        racine.attributs.update({"statut": r["statut"], "etapes": r["etapes"]})
    return r, racine


# ---------------------------------------------------------------- lecture des traces
def enfants(spans: list[Span]) -> dict:
    par_parent: dict = {}
    for s in sorted(spans, key=lambda s: s.debut_ms):
        par_parent.setdefault(s.parent_id, []).append(s)
    return par_parent


def temps_propre(s: Span, par_parent: dict) -> float:
    return s.duree_ms - sum(c.duree_ms for c in par_parent.get(s.span_id, []))


def arbre(spans: list[Span]) -> list[str]:
    par_parent, lignes = enfants(spans), []

    def visiter(s: Span, profondeur: int) -> None:
        a = s.attributs
        detail = (f"  in={a['gen_ai.usage.input_tokens']} out={a['gen_ai.usage.output_tokens']} "
                  f"coût={a['cout_usd']:.6f} USD" if s.nom == "llm.create" else "")
        lignes.append(f"{'  ' * profondeur}{s.nom:<{26 - 2 * profondeur}}{s.debut_ms:>7.1f} → {s.fin_ms:>7.1f} ms"
                      f"  propre {temps_propre(s, par_parent):>6.1f} ms{detail}")
        for c in par_parent.get(s.span_id, []):
            visiter(c, profondeur + 1)

    for racine in par_parent.get(None, []):
        visiter(racine, 0)
    return lignes


EMIRATES_ID = re.compile(r"784-\d{4}-\d{7}-\d")


def exporter(spans: list[Span]) -> list[str]:
    """Une ligne JSON par span, données personnelles masquées AVANT de sortir du processus."""
    lignes = []
    for s in spans:
        attributs = {k: (EMIRATES_ID.sub("784-****-*******-*", v) if isinstance(v, str) else v)
                     for k, v in s.attributs.items()}
        lignes.append(json.dumps({"trace_id": s.trace_id, "span_id": s.span_id, "parent_id": s.parent_id,
                                  "nom": s.nom, "debut_ms": s.debut_ms, "fin_ms": s.fin_ms, "statut": s.statut,
                                  "attributs": attributs}, ensure_ascii=False, sort_keys=True))
    return lignes


def p50(valeurs: list[float]) -> float:
    """Médiane au rang le plus proche : la valeur de rang ceil(0,5 × N) dans la liste triée."""
    if not valeurs:
        raise ValueError("liste vide")
    s = sorted(valeurs)
    return s[math.ceil(0.5 * len(s)) - 1]


def agreger(spans: list[Span]) -> dict:
    par_nom: dict = {}
    for s in spans:
        par_nom.setdefault(s.nom, []).append(s)
    return {nom: {"n": len(ss), "p50": p50([s.duree_ms for s in ss]), "p95": p95([s.duree_ms for s in ss]),
                  "cout": sum(s.attributs.get("cout_usd", 0.0) for s in ss),
                  "erreurs": sum(1 for s in ss if s.statut == "erreur")} for nom, ss in sorted(par_nom.items())}


def taux_de_consommation(mauvais: int, total: int, slo: float) -> float | None:
    """v = (1 − A_obs) / (1 − A*) (étape 49) ; None sans trafic."""
    if total == 0:
        return None
    return (mauvais / total) / (1 - slo)


# ---------------------------------------------------------------- dérive
def kl(p: list[float], q: list[float]) -> float:
    if len(p) != len(q):
        raise ValueError("distributions de tailles différentes")
    total = 0.0
    for pi, qi in zip(p, q):
        if pi > 0:
            if qi == 0:
                return math.inf
            total += pi * math.log(pi / qi)
    return total


def psi(p: list[float], q: list[float]) -> float:
    """PSI = Σ (pᵢ − qᵢ) ln(pᵢ / qᵢ) ; +∞ si une case est vide d'un seul côté ; 0 pour une case vide des deux côtés."""
    if len(p) != len(q) or abs(sum(p) - 1) > 1e-9 or abs(sum(q) - 1) > 1e-9:
        raise ValueError("deux distributions de même taille, de somme 1")
    total = 0.0
    for pi, qi in zip(p, q):
        if pi == qi == 0:
            continue
        if pi == 0 or qi == 0:
            return math.inf
        total += (pi - qi) * math.log(pi / qi)
    return total


def classer_psi(v: float) -> str:
    """Seuils usuels 0,1 et 0,25 : une règle empirique, pas un test statistique."""
    return "stable" if v < 0.1 else ("à surveiller" if v < 0.25 else "dérive")


def proportions(valeurs: list, cases: list) -> list[float]:
    return [sum(1 for v in valeurs if v == c) / len(valeurs) for c in cases]


def histogramme(valeurs: list[float], bornes: list[float]) -> list[float]:
    comptes = [0] * (len(bornes) + 1)
    for v in valeurs:
        comptes[bisect.bisect_right(bornes, v)] += 1
    return [c / len(valeurs) for c in comptes]


# ---------------------------------------------------------------- une semaine simulée
def simuler(n: int, part_arabe: float, graine: int) -> tuple[Traceur, list[dict]]:
    rng = random.Random(graine)
    h = Horloge()
    traceur = Traceur(h, graine)

    def latence(nom: str) -> float:
        if nom == "ratio_endettement":                     # lit les encours dans le cœur bancaire
            return 2500.0 if rng.random() < 0.02 else rng.uniform(80, 160)
        return rng.uniform(20, 40)

    def en_erreur(nom: str) -> bool:
        return nom == "ratio_endettement" and rng.random() < 0.01

    runs = []
    for _ in range(n):
        arabe = rng.random() < part_arabe
        f = 1.35 if arabe else 1.0                         # facteur de tokens illustratif (étape 2 bis)
        q = round(rng.randint(150, 350) * f)
        llm = LLMInstrumente(FakeLLM(script_credit(q, round((120 + rng.randint(0, 40)) * f))), traceur, h,
                             bruit=lambda: rng.lognormvariate(0, 0.15))
        outils = instrumenter_outils(outils_credit(), traceur, h, latence, en_erreur)
        r, racine = executer_trace(traceur, llm, "Hypothèque de 1 M AED sur 25 ans ?", outils)
        siens = [s for s in traceur.spans if s.trace_id == racine.trace_id]
        llms = [s for s in siens if s.nom == "llm.create"]
        runs.append({"duree": racine.duree_ms, "statut": r["statut"], "langue": "ar" if arabe else "en",
                     "erreur": any(s.statut == "erreur" for s in siens),
                     "tokens_in": sum(s.attributs["gen_ai.usage.input_tokens"] for s in llms),
                     "cout": sum(s.attributs["cout_usd"] for s in llms)})
    return traceur, runs


def main() -> None:
    print("1. La trace d'une exécution de executer_agent (horloge simulée, en ms)")
    h = Horloge()
    traceur = Traceur(h, graine=1)
    latences = {"mensualite": 30.0, "ratio_endettement": 120.0}
    outils = instrumenter_outils(outils_credit(), traceur, h, latences.__getitem__, lambda nom: False)
    llm = LLMInstrumente(FakeLLM(script_credit(200, 120)), traceur, h)
    question = "Client 784-1990-1234567-1 : hypothèque de 1 M AED sur 25 ans ?"
    r, racine = executer_trace(traceur, llm, question, outils)
    for ligne in arbre(traceur.spans):
        print("  " + ligne)
    par_parent = enfants(traceur.spans)
    llms = [s for s in traceur.spans if s.nom == "llm.create"]
    cout = sum(s.attributs["cout_usd"] for s in llms)
    sans_cache = sum(s.attributs["gen_ai.usage.input_tokens"] for s in llms) * PRIX_IN + 240 * PRIX_OUT
    print(f"  coût de l'exécution = {cout:.6f} USD (sans cache : {sans_cache:.6f} USD)")
    assert r["statut"] == "fini" and len(traceur.spans) == 6 and len(par_parent[racine.span_id]) == 5
    assert all(s.trace_id == racine.trace_id for s in traceur.spans)
    assert abs(racine.duree_ms - 4891.5) < 1e-9 and temps_propre(racine, par_parent) == 9.0
    assert abs(sum(temps_propre(s, par_parent) for s in traceur.spans) - racine.duree_ms) < 1e-9
    assert [round(s.attributs["cout_usd"], 6) for s in llms] == [0.00525, 0.00285, 0.0048]
    assert round(cout, 6) == 0.0129 and round(sans_cache, 6) == 0.01755

    print("2. Tokens : ne pas compter le cache deux fois ; propagation ; export masqué")
    lus = sum(s.attributs["gen_ai.usage.input_tokens"] for s in llms)
    double = lus + sum(s.attributs["gen_ai.usage.cache_read.input_tokens"]
                       + s.attributs["gen_ai.usage.cache_write.input_tokens"] for s in llms)
    print(f"  tokens d'entrée lus par le modèle = {lus} ; en rajoutant les attributs de cache : {double} (faux)")
    assert lus == 1200 + 1550 + 1900 == 4650 and double == 7650
    with traceur.span("publication.evenement"):
        entete = traceur.traceparent()
    print(f"  traceparent = {entete[:24]}…")
    assert re.fullmatch(r"00-[0-9a-f]{32}-[0-9a-f]{16}-01", entete)
    export = exporter([s for s in traceur.spans if s.trace_id == racine.trace_id])
    print(f"  {len(export)} lignes JSON ; Emirates ID en clair dans l'export : {any(EMIRATES_ID.search(l) for l in export)}")
    assert len(export) == 6 and not any(EMIRATES_ID.search(l) for l in export)

    print("3. Une semaine simulée de 400 exécutions : p50 et p95 par type de span")
    t_ref, ref = simuler(400, part_arabe=0.20, graine=72)
    stats = agreger(t_ref.spans)
    for nom, st in stats.items():
        print(f"  {nom:<24} n = {st['n']:>4}  p50 = {st['p50']:>7.1f} ms  p95 = {st['p95']:>7.1f} ms  erreurs = {st['erreurs']}")
    couts = [x["cout"] for x in ref]
    print(f"  coût par exécution : p50 = {p50(couts):.6f} USD, p95 = {p95(couts):.6f} USD ; semaine = {sum(couts):.4f} USD")
    par_parent_ref = enfants(t_ref.spans)
    positions = list(zip(*[[c.duree_ms for c in par_parent_ref[rac.span_id]] for rac in par_parent_ref[None]]))
    somme_p95 = sum(p95(list(pos)) for pos in positions)            # 5 positions : 3 tours de LLM, 2 outils
    print(f"  p95 de la durée totale = {stats['agent.executer']['p95']:.1f} ms ; "
          f"somme des p95 des 5 étapes = {somme_p95:.1f} ms")
    assert stats["agent.executer"]["n"] == 400 and stats["llm.create"]["n"] == 1200 and len(positions) == 5
    assert stats["agent.executer"]["p95"] < somme_p95
    assert (round(stats["agent.executer"]["p95"], 1), round(somme_p95, 1)) == (6623.0, 7169.0)
    lat = [120, 95, 180, 240, 110, 130, 105, 900, 150, 99, 101, 140, 160, 170, 115, 125, 135, 145, 155, 165]
    print(f"  20 latences (ms) : moyenne = {statistics.fmean(lat):.0f}, p50 = {p50(lat)}, p95 = {p95(lat)}, max = {max(lat)}")
    assert (statistics.fmean(lat), p50(lat), p95(lat)) == (177, 135, 240)
    x = [0] * 24 + [100]                                # P(X = 100) = 0.04 ; X et Y indépendantes, de même loi
    somme = [a + b for a in x for b in x]
    print(f"  contre-exemple : p95(X) + p95(Y) = {p95(x) + p95(x)}, mais p95(X + Y) = {p95(somme)}")
    assert p95(x) == 0 and p95(somme) == 100

    print("4. Budget d'erreur : objectif 99 % d'exécutions finies, sans erreur, en moins de 8 s")
    t_cour, cour = simuler(400, part_arabe=0.45, graine=73)
    bilan = {}
    for nom, runs in (("semaine de référence", ref), ("semaine courante", cour)):
        mauvais = sum(1 for x in runs if x["statut"] != "fini" or x["erreur"] or x["duree"] > 8000)
        bilan[nom] = (mauvais, taux_de_consommation(mauvais, len(runs), 0.99))
        print(f"  {nom:<21} mauvaises = {mauvais:>2} / {len(runs)} ; disponibilité = {1 - mauvais / len(runs):.4f} ; "
              f"vitesse de consommation v = {bilan[nom][1]:.2f}")
    assert taux_de_consommation(0, 0, 0.99) is None and abs(taux_de_consommation(10, 400, 0.99) - 2.5) < 1e-9
    assert {nom: (mv, round(v, 2)) for nom, (mv, v) in bilan.items()} == {"semaine de référence": (4, 1.0),
                                                                          "semaine courante": (7, 1.75)}

    print("5. Dérive : PSI = KL(p‖q) + KL(q‖p)")
    p, q = [0.5, 0.3, 0.2], [0.3, 0.3, 0.4]
    print(f"  PSI = {psi(p, q):.4f} ; KL(p‖q) + KL(q‖p) = {kl(p, q):.4f} + {kl(q, p):.4f} ; classe : {classer_psi(psi(p, q))}")
    assert abs(psi(p, q) - (kl(p, q) + kl(q, p))) < 1e-12 and psi(p, q) == psi(q, p)
    assert round(psi(p, q), 4) == 0.2408 and psi(p, p) == 0.0 and psi([0.5, 0.5], [1.0, 0.0]) == math.inf
    langues_ref = proportions([x["langue"] for x in ref], ["en", "ar"])
    langues_cour = proportions([x["langue"] for x in cour], ["en", "ar"])
    bornes = statistics.quantiles([x["tokens_in"] for x in ref], n=10)
    p_tok = histogramme([x["tokens_in"] for x in ref], bornes)
    q_tok = histogramme([x["tokens_in"] for x in cour], bornes)
    for nom, (a, b) in {"langue": (langues_ref, langues_cour), "tokens d'entrée (déciles)": (p_tok, q_tok)}.items():
        print(f"  {nom:<26} PSI = {psi(a, b):.4f} -> {classer_psi(psi(a, b))}")
    print(f"  coût moyen par exécution : {statistics.fmean(couts):.6f} -> {statistics.fmean(x['cout'] for x in cour):.6f} USD")
    assert (round(psi(langues_ref, langues_cour), 4), round(psi(p_tok, q_tok), 4)) == (0.2515, 0.1209)

    print("6. Sans aucune dérive, le PSI d'un petit échantillon n'est pas nul : E ≈ (B − 1) / M")
    rng = random.Random(2026)
    uniforme = [0.1] * 10
    for m in (100, 1000):
        valeurs = []
        for _ in range(300):
            comptes = [0] * 10
            for _ in range(m):
                comptes[rng.randrange(10)] += 1
            valeurs.append(psi(uniforme, [c / m for c in comptes]))
        finies = [x for x in valeurs if math.isfinite(x)]
        au_dessus = sum(1 for x in finies if x >= 0.1) / len(finies)
        print(f"  M = {m:>4} : PSI moyen = {statistics.fmean(finies):.4f} (théorie 9 / {m} = {9 / m:.4f}) ; "
              f"fenêtres ≥ 0.1 : {au_dessus:.0%} ; cases vides : {len(valeurs) - len(finies)}")
        assert abs(statistics.fmean(finies) - 9 / m) < 0.25 * 9 / m
        assert (au_dessus > 0.25) if m == 100 else (au_dessus == 0.0)

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. La trace d'une exécution de executer_agent (horloge simulée, en ms)
  agent.executer                0.0 →  4891.5 ms  propre    9.0 ms
    llm.create                  3.0 →  1263.0 ms  propre 1260.0 ms  in=1200 out=60 coût=0.005250 USD
    outil.mensualite         1263.0 →  1293.0 ms  propre   30.0 ms
    llm.create               1296.0 →  2573.5 ms  propre 1277.5 ms  in=1550 out=60 coût=0.002850 USD
    outil.ratio_endettement  2573.5 →  2693.5 ms  propre  120.0 ms
    llm.create               2696.5 →  4891.5 ms  propre 2195.0 ms  in=1900 out=120 coût=0.004800 USD
  coût de l'exécution = 0.012900 USD (sans cache : 0.017550 USD)
2. Tokens : ne pas compter le cache deux fois ; propagation ; export masqué
  tokens d'entrée lus par le modèle = 4650 ; en rajoutant les attributs de cache : 7650 (faux)
…
  p95 de la durée totale = 6623.0 ms ; somme des p95 des 5 étapes = 7169.0 ms
…
  semaine courante      mauvaises =  7 / 400 ; disponibilité = 0.9825 ; vitesse de consommation v = 1.75
…
  langue                     PSI = 0.2515 -> dérive
…
  M =  100 : PSI moyen = 0.0948 (théorie 9 / 100 = 0.0900) ; fenêtres ≥ 0.1 : 39% ; cases vides : 0
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : observer un agent ne demande ni de modifier sa boucle, ni d'acheter un outil. Il suffit de décorer ses ports, de dater chaque span sur une horloge, de compter les tokens selon une convention unique, et de comparer les distributions avec une mesure dont on connaît le niveau de bruit.

## Squelette algorithmique

Trois algorithmes : tracer une exécution en décorant les ports, agréger les spans d'une période, surveiller la dérive entre deux périodes. Entrées : la boucle d'agent et ses ports ; les spans exportés ; deux échantillons d'une même variable. Sorties : une trace, des percentiles et une vitesse de consommation, un PSI et une décision.

```text
ALGORITHME OuvrirSpan(nom, attributs)              (context manager)
  parent ← sommet de la pile, ou rien
  span ← { trace = parent.trace OU nouvel identifiant, id ← nouvel identifiant,
           parent = parent.id, nom, début ← horloge, attributs }
  empiler span
  exécuter le bloc
      en cas d'exception : span.statut ← « erreur » ; noter le message ; RELANCER l'exception
  span.fin ← horloge ; dépiler ; ranger span

ALGORITHME TracerExécution(question, LLM, outils)
  LLM' ← LLM décoré : pour chaque create, OuvrirSpan(« llm.create ») ;
         noter tokens lus, tokens écrits, tokens en cache, coût C(s), raison d'arrêt
  outils' ← chaque outil décoré : OuvrirSpan(« outil.nom »)
  OuvrirSpan(« agent.executer ») :
      résultat ← BoucleAgent(LLM', question, outils')     (la boucle n'est pas modifiée)
  exporter les spans après masquage des données personnelles

ALGORITHME AgrégerPériode(spans, objectif A*, seuil de durée)
  POUR CHAQUE nom de span FAIRE
      durées ← durées des spans de ce nom, triées
      p50 ← durées[⌈0,5 × n⌉] ; p95 ← durées[⌈0,95 × n⌉]
  FIN POUR
  m ← nombre d'exécutions non finies OU avec un span en erreur OU plus longues que le seuil
  SI n = 0 ALORS v ← indéfini SINON v ← (m / n) / (1 − A*)
  SI v nettement > 1 ALORS alerter, geler les déploiements risqués

ALGORITHME SurveillerDérive(référence, courant, B)
  bornes ← quantiles de la référence en B cases
  p ← proportions de la référence par case ; q ← proportions du courant par case
  SI une case est vide d'un seul côté ALORS PSI ← ∞
  SINON PSI ← Σ (pᵢ − qᵢ) × ln(pᵢ / qᵢ)
  bruit ← (B − 1) / M
  SI PSI ≥ 0,25 ET PSI ≫ bruit ALORS « dérive » : relancer l'évaluation
  SINON SI PSI ≥ 0,1 ET PSI > bruit ALORS « à surveiller »
  SINON « stable »
```

**Complexité :** ouvrir et fermer un span coûte O(1) en temps, plus le nombre d'attributs ; une exécution de K tours produit O(K) spans, et la mémoire du traceur croît d'autant, d'où l'export par lots en production. Agréger N spans coûte O(N log N) pour trier les durées de chaque type ; un histogramme ou une structure de quantiles approchés le ramène à O(N) en mémoire bornée. Le PSI coûte O(M log B) pour ranger M observations dans B cases par recherche dichotomique, puis O(B) pour la somme ; les quantiles de la référence coûtent O(n log n) une fois par période.

**Du squelette au code :** `OuvrirSpan` est `Traceur.span`, avec la pile, le `yield`, la relance dans le bloc `except` et le `finally`. `TracerExécution` est `executer_trace`, appelé avec `LLMInstrumente` pour le LLM décoré et `instrumenter_outils` pour les outils décorés ; `cout_usd` calcule C(s) et `exporter` fait le masquage. `AgrégerPériode` est `agreger` pour les percentiles par nom (avec `p50` et la fonction canonique `p95`) et la section 4 de `main` pour m et `taux_de_consommation`. `SurveillerDérive` est la section 5 : `statistics.quantiles` pour les bornes, `histogramme` et `proportions` pour p et q, `psi` pour la somme et `classer_psi` pour les seuils ; le niveau de bruit (B − 1)/M est celui que vérifie la section 6.

## Cas d'usage réels aux Émirats

Les prix, durées, volumes et seuils ci-dessous sont illustratifs ; les produits cités le sont comme exemples du marché.

### Banque — retrouver l'étape qui fait dépasser 8 secondes

Une banque de détail de Dubaï suit son agent de pré-instruction de crédit avec un objectif de 99 % d'exécutions finies, sans erreur, en moins de 8 s. Un lundi, la vitesse de consommation du budget passe de 1,00 à 1,75 (démonstration, point 4). L'arbre des traces lentes montre que le temps se concentre dans le span `outil.ratio_endettement`, qui lit les encours dans le cœur bancaire : la moyenne de cet outil reste à 120 ms, mais 2 % de ses appels prennent 2,5 s. Sans traces, l'équipe aurait accusé le modèle, dont les spans sont les plus longs en moyenne, et aurait payé un modèle plus rapide sans rien résoudre. La trace montre aussi deux exécutions « finies » dont l'outil avait échoué : l'agent a répondu sans le ratio d'endettement que la CBUAE plafonne à 50 %, ce qui doit déclencher une revue humaine. Les spans exportés ne contiennent que des Emirates ID masqués. On suit le p95 par span, la vitesse de consommation et le nombre de réponses produites malgré une erreur d'outil.

### Immobilier — le coût par conversation, poste par poste

Une agence de Dubaï et d'Abu Dhabi facture à ses commerciaux un assistant qui rédige les annonces et répond aux prospects, et veut connaître le coût réel d'une conversation. L'attribut de coût de chaque span de modèle, calculé par la formule de l'étape 72 avec les compteurs de cache, montre que le premier tour coûte plus cher que les suivants, parce qu'il écrit le préfixe dans le cache, et qu'une conversation de trois tours coûte 0,0129 USD au lieu de 0,01755 sans cache (démonstration, point 2). Le tableau de bord initial additionnait les tokens d'entrée des conventions GenAI et les attributs de cache : il affichait 64 % de tokens de trop et faisait croire que le cache ne servait à rien. Une fois la convention écrite et la double addition retirée, le coût affiché correspond à la facture du fournisseur à quelques pour cent près. Les prix sont suivis en USD, puis convertis en AED au taux fixe de 3,6725. On suit le p50 et le p95 du coût par conversation, et l'écart entre le coût calculé et le coût facturé.

### Assurance — un p95 par instance qui ne veut rien dire

Un assureur auto et santé fait tourner son agent d'analyse de sinistres sur six instances, et son premier tableau de bord affichait la moyenne des six p95. Une instance surchargée avait un p95 de 20 s et les cinq autres de 4 s ; la moyenne affichait 6,7 s, alors que le p95 réel, calculé sur toutes les requêtes fusionnées, dépendait de la part de trafic de l'instance lente et ne valait aucune des deux valeurs. L'équipe a remplacé la moyenne par un histogramme fusionné, d'où elle tire le percentile, conformément à la démonstration du point 3 : les percentiles ne se moyennent pas et ne s'additionnent pas. Elle a aussi cessé d'estimer le p95 d'un dossier complet en additionnant les p95 des étapes, qui surestimait de plusieurs secondes la durée réelle. L'assurance étant supervisée par la CBUAE, les traces des décisions automatiques sont conservées avec leurs attributs pour pouvoir être rejouées. On suit le p95 fusionné de la durée d'analyse et la part de dossiers traités dans le délai promis.

### Secteur public — la langue des demandes change avant les coûts

Une entité de services publics en ligne, accessible par UAE Pass, répond en arabe et en anglais. Après une campagne d'information en arabe, la part des demandes en arabe passe d'environ 20 % à plus de 40 % ; le PSI de la langue vaut 0,25, au seuil de la dérive, et celui des tokens d'entrée 0,12 (démonstration, point 7). Le coût moyen n'a bougé que de 2 %, et aucun indicateur de qualité n'a encore bougé, parce que les plaintes arrivent avec retard. La surveillance de dérive déclenche pourtant une nouvelle évaluation sur un échantillon de demandes en arabe (étape 13 bis), qui révèle des réponses moins précises sur les noms de démarches translittérés. Le PSI est calculé chaque jour sur plusieurs milliers de demandes, jamais sur une heure de trafic, où le bruit seul atteindrait le seuil (démonstration, point 6). Les spans ne contiennent que la langue, la longueur et l'issue, pas le texte des demandes, conformément à la minimisation des données de la PDPL. On suit le PSI de la langue et de la longueur, et la justesse mesurée par langue.

### Crypto — une alerte de dérive qui n'en était pas une

Une plateforme d'actifs virtuels agréée par la VARA surveille la distribution des outils choisis par son agent de support (consultation de solde, statut de retrait, réinitialisation d'accès) en dix cases, par fenêtres d'une heure. Chaque nuit, une alerte « à surveiller » se déclenche, alors que rien ne change dans le comportement de l'agent. L'explication est le bruit d'échantillonnage : la nuit, une fenêtre ne compte qu'une centaine de conversations, et le PSI attendu sans aucune dérive vaut déjà (10 − 1) / 100 = 0,09, avec environ 40 % de fenêtres au-dessus de 0,1 (démonstration, point 6). L'équipe passe à des fenêtres d'au moins 1 000 conversations, où le bruit tombe à 0,009, et compare chaque PSI à son niveau de bruit. Les fausses alertes disparaissent, et une vraie dérive, la hausse des demandes de statut de retrait un jour d'incident sur une chaîne, est détectée en moins d'une fenêtre. On suit le nombre d'alertes par semaine et la part d'alertes confirmées par un opérateur.

### RH — le prompt complet dans les traces, puis plus du tout

Un cabinet RH multi-émirats avait activé l'enregistrement complet des prompts dans ses spans pour déboguer son agent de calcul des indemnités de fin de service. Un audit interne découvre dans l'outil d'observabilité des noms, des salaires et des numéros d'Emirates ID en clair, conservés plus longtemps que les dossiers eux-mêmes. Le cabinet masque désormais les identifiants avant l'export, comme la fonction `exporter` du programme, ne conserve le texte des prompts que sur un échantillon et pour une durée courte, et garde dans tous les spans les compteurs de tokens, les durées, les noms d'outils et les statuts, qui suffisent pour le coût, la latence et la dérive. Pour les données traitées dans les zones financières du DIFC ou de l'ADGM, le régime de protection applicable est celui de la zone, à confirmer avec le texte en vigueur. On suit le nombre de champs sensibles détectés dans les exports, avec un objectif de zéro.

## Pièges et limites

- **Compter deux fois les tokens de cache.** Selon la source, `input_tokens` inclut ou exclut les tokens de cache ; on écrit la convention retenue et l'on ne somme qu'une source par requête.
- **Moyenner ou additionner des percentiles.** Le p95 d'un agent ne s'obtient ni en additionnant les p95 de ses étapes, ni en moyennant ceux de ses instances : on fusionne les valeurs ou les histogrammes, puis on calcule.
- **Comparer un PSI au seuil sans regarder la taille de la fenêtre.** Sur 100 observations et 10 cases, le bruit seul vaut 0,09 ; un seuil de 0,1 y déclenche des alertes dans près de quatre fenêtres sur dix.
- **Échantillonner les traces au hasard.** Ne garder que 10 % des traces garde aussi 10 % des exécutions en erreur ; on conserve toutes les traces en erreur ou lentes (échantillonnage après coup, dit *tail sampling*) et l'on échantillonne les autres.
- **Mettre des données personnelles dans les attributs.** Un prompt complet dans un span est copié dans un système tiers, conservé longtemps et lu par d'autres équipes ; on masque avant l'export et l'on minimise ce qui est conservé.

### Exercice feuille blanche

1. Sans regarder le code, écrire `Traceur.span` (pile, parent, statut d'erreur, `finally`) et `temps_propre`, puis vérifier sur une trace à trois niveaux que la somme des temps propres vaut la durée de la racine.
2. Prédire, puis vérifier avec `psi` : que vaut le PSI entre p = (0,5 ; 0,5) et q = (0,6 ; 0,4) ? (Réponse : 0,1 ln(0,6/0,5) − 0,1 ln(0,4/0,5) ≈ 0,0182 + 0,0223 = 0,0405, « stable ».) Et quel est le niveau de bruit pour B = 2 et M = 50 ? (Réponse : 1/50 = 0,02.)
3. Trouver le bug : une variante de `Traceur.span` met `s.fin_ms = self.horloge.t` dans le bloc `try`, juste après le `yield`, au lieu du `finally`. Que deviennent la fin et la durée d'un span dont le bloc lève une exception ? (Réponse : la fin n'est jamais datée, la durée vaut moins le début, et le span en erreur, le plus utile, devient illisible.)

## Pour aller plus loin

OpenTelemetry est le standard ouvert des traces, métriques et journaux ; ses conventions sémantiques GenAI (`gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`…) sont encore en évolution et se vérifient dans la spécification. Le traceur de ce fichier s'y transpose directement : un span par appel, les mêmes identifiants, l'en-tête `traceparent` du W3C, puis un exportateur au lieu de la liste en mémoire. Des outils du marché, comme Langfuse, Arize Phoenix ou Datadog LLM Observability, ajoutent l'interface, la conservation et l'évaluation ; on garde la liberté d'en changer tant que les spans suivent une convention standard. Pour comparer deux distributions continues sans choisir de cases, on utilise le test de Kolmogorov-Smirnov ou la distance de Wasserstein ; pour des quantiles en mémoire bornée sur un flux, les structures t-digest ou les histogrammes HDR. L'étape 72 quinquies utilise ces mesures de coût et de latence pour régler le budget de raisonnement de l'agent.

> Étape 72 quater du parcours · Prérequis : [Décodage spéculatif](<72c-Decodage-Speculatif.md>) · Suite : [Budget de raisonnement](<72e-Budget-de-Raisonnement.md>)
