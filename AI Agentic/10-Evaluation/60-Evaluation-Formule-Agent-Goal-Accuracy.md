# Étape 60 — Évaluation — Agent Goal Accuracy

> Étape 60 du parcours · Prérequis : [Tool Call F1](<59-Evaluation-Formule-Tool-Call-F1.md>) · Suite : [Loi bêta et petits échantillons](<60b-Loi-Beta-et-Petits-Echantillons.md>)

**Dossier :** 10-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Product Engineers, Forward-Deployed Engineers  
**Nom du fichier :** 60-Evaluation-Formule-Agent-Goal-Accuracy.md

## Définition

L'Agent Goal Accuracy dit si l'agent a atteint l'**objectif métier** de la tâche, quel que soit le chemin qu'il a pris : la facture existe et elle est conforme, la décision de crédit respecte les règles, l'estimation tombe dans la fourchette convenue. Chaque tâche reçoit une note binaire, 1 si l'objectif est atteint et 0 sinon, rendue par un correcteur : un programme qui inspecte l'état final (le meilleur cas), un LLM juge qui compare le résultat à une référence, ou un humain. Le taux publié est la moyenne de ces notes sur les tâches du jeu d'évaluation, toujours accompagné de son intervalle de Wilson, parce que 45 réussites sur 50 et 900 sur 1 000 donnent le même 0,90 mais pas la même certitude. Une phrase finale juste ne suffit pas : un agent qui écrit « facture émise » sans avoir appelé l'outil n'a pas atteint l'objectif. Un jeu vide ne donne pas de taux : la fonction renvoie `None`.

## Rôle dans un agent

L'Agent Goal Accuracy se mesure à l'étape **observer**, à la fin de chaque tâche du jeu d'évaluation ; c'est l'évaluation du **résultat**, quand la Tool Call F1 de l'étape 59 évalue le **processus** (étape 13 bis). Le correcteur lit ce que la boucle a laissé derrière elle : les écritures dans la base, les fichiers produits, les appels à effet, et seulement en dernier recours le texte final. Le taux alimente la barrière d'intégration continue posée à l'étape 13 bis : on ne déploie que si la **borne basse** de Wilson dépasse le seuil métier, et si la nouvelle version n'est pas significativement moins bonne que l'ancienne sur les mêmes tâches. L'étape 13 bis a présenté les formules de pass@k, pass^k et McNemar et construit le banc d'essai ; ce fichier démontre pass@k contre pass^k, dit combien de tâches il faut évaluer et dérive le test qui compare deux prompts.

## Équation complète

Note de la tâche i et taux mesuré sur n tâches :

$$
y_i = \begin{cases} 1 & \text{si l'objectif de la tâche } i \text{ est atteint} \\ 0 & \text{sinon} \end{cases}
\qquad\qquad
\widehat{GA} = \frac{1}{n} \sum_{i=1}^{n} y_i = \frac{s}{n}
$$

Intervalle de Wilson à 95 % (démontré à l'étape 7) et barrière de déploiement :

$$
\text{Wilson}(s, n) = \frac{\widehat{GA} + \dfrac{z^2}{2n} \pm z\sqrt{\dfrac{\widehat{GA}\,(1-\widehat{GA})}{n} + \dfrac{z^2}{4n^2}}}{1 + \dfrac{z^2}{n}}
\qquad\qquad
\text{déployer} \iff \text{borne basse} \ge \tau
$$

Nombre de tâches pour une demi-largeur d'au plus e :

$$
n \ge \frac{z^2\,p\,(1-p)}{e^2}
$$

Réussir au moins une fois sur k essais, réussir les k essais :

$$
\text{pass@}k = 1 - (1-p)^k \qquad\qquad \text{pass}^k = p^k
$$

Estimateurs sans biais à partir de c réussites sur m essais d'une même tâche (formules de l'étape 13 bis) :

$$
\widehat{\text{pass@}k} = 1 - \frac{\binom{m-c}{k}}{\binom{m}{k}} \qquad\qquad \widehat{\text{pass}^k} = \frac{\binom{c}{k}}{\binom{m}{k}}
$$

Comparaison appariée de deux prompts (McNemar) :

$$
\chi^2 = \frac{\big(\lvert n_{10} - n_{01} \rvert - 1\big)^2}{n_{10} + n_{01}}, \qquad \text{significatif à 5 \% si } \chi^2 > 3{,}84
$$

## Décryptage des symboles

$$
y_i
$$

**Sens :** note de la tâche i rendue par le correcteur : 1 si l'objectif est atteint, 0 sinon · **Type / plage :** 0 ou 1 · **Variable Python :** un élément de `resultats`, calculé par `objectif_atteint(...)`

$$
n
$$

**Sens :** nombre de tâches évaluées · **Type / plage :** entier ≥ 0 · **Variable Python :** `len(resultats)`

$$
s
$$

**Sens :** nombre de tâches réussies · **Type / plage :** entier de 0 à n · **Variable Python :** `sum(resultats)`

$$
\widehat{GA}
$$

**Sens :** Agent Goal Accuracy mesurée, estimation du vrai taux de réussite · **Type / plage :** réel dans [0, 1], ou indéfini si n = 0 · **Variable Python :** `goal_accuracy(resultats)`

$$
p
$$

**Sens :** vraie probabilité que l'agent atteigne l'objectif sur un essai, inconnue · **Type / plage :** réel dans [0, 1] · **Variable Python :** `p`

$$
z
$$

**Sens :** quantile de la loi normale qui fixe le niveau de confiance ; 1,96 pour 95 % · **Type / plage :** réel > 0 · **Variable Python :** `z`

$$
\tau
$$

**Sens :** seuil métier de la barrière, par exemple 0,90 · **Type / plage :** réel dans [0, 1] · **Variable Python :** `seuil`

$$
e
$$

**Sens :** demi-largeur visée de l'intervalle, par exemple 0,05 pour ±5 points · **Type / plage :** réel dans ]0, 1[ · **Variable Python :** `marge`

$$
k
$$

**Sens :** nombre d'essais considérés pour pass@k et pass^k · **Type / plage :** entier ≥ 1 · **Variable Python :** `k`

$$
m,\ c
$$

**Sens :** nombre d'essais réellement joués sur une même tâche, et nombre de ces essais réussis · **Type / plage :** entiers, 0 ≤ c ≤ m et k ≤ m · **Variable Python :** `m`, `c`

$$
\text{pass@}k
$$

**Sens :** probabilité de réussir au moins une fois sur k essais · **Type / plage :** réel dans [0, 1] · **Variable Python :** `1 - (1 - p) ** k`, estimé par `pass_at_k(m, c, k)`

$$
\text{pass}^k
$$

**Sens :** probabilité de réussir les k essais, c'est-à-dire d'être constant · **Type / plage :** réel dans [0, 1] · **Variable Python :** `p ** k`, estimé par `pass_puissance_k(m, c, k)`

$$
n_{10},\ n_{01}
$$

**Sens :** tâches réussies par le prompt A et ratées par le prompt B, et l'inverse : les paires discordantes · **Type / plage :** entiers ≥ 0 · **Variable Python :** `perdus`, `gagnes`

$$
\chi^2
$$

**Sens :** statistique de McNemar, avec correction de continuité · **Type / plage :** réel ≥ 0 · **Variable Python :** `chi2`

## Démonstration

### 1. Le taux est une moyenne de notes de Bernoulli

Si les tâches sont tirées dans la même population et que l'agent réussit chacune avec la probabilité p, chaque yᵢ vaut 1 avec la probabilité p : son espérance vaut p et sa variance p(1 − p). La moyenne de n notes indépendantes a donc pour espérance p, ce qui en fait un estimateur sans biais, et pour variance p(1 − p)/n, parce que la variance d'une somme de variables indépendantes est la somme des variances et que diviser par n divise la variance par n². L'incertitude décroît comme 1/√n : pour la diviser par deux, il faut quatre fois plus de tâches.

### 2. La barrière se juge sur la borne basse

Pour 45 tâches réussies sur 50, le taux vaut 0,90, et l'intervalle de Wilson, démontré à l'[étape 7](<../02-LLM-Softmax-et-Prompts/07-Prompts-Formule-Taux-de-Conformite.md>), se calcule à la main avec z² = 3,8416 :

$$
\frac{z^2}{2n} = 0{,}038416 \qquad \sqrt{\frac{0{,}9 \times 0{,}1}{50} + \frac{3{,}8416}{10\,000}} = \sqrt{0{,}00218416} \approx 0{,}046735 \qquad 1 + \frac{z^2}{n} = 1{,}076832
$$

$$
\text{borne basse} = \frac{0{,}938416 - 1{,}96 \times 0{,}046735}{1{,}076832} \approx 0{,}7864 \qquad \text{borne haute} = \frac{0{,}938416 + 0{,}091601}{1{,}076832} \approx 0{,}9565
$$

Le vrai taux est compatible avec toute valeur entre 78,6 % et 95,7 %. Une barrière à 0,90 appliquée au taux mesuré laisserait passer cette version ; appliquée à la borne basse, elle la refuse : 50 tâches ne suffisent pas pour affirmer « au moins 90 % ».

### 3. Combien de tâches évaluer

L'intervalle normal a pour demi-largeur z√(p(1 − p)/n). Exiger qu'elle soit au plus e, puis élever au carré et isoler n, donne

$$
z\sqrt{\frac{p(1-p)}{n}} \le e \iff n \ge \frac{z^2\,p\,(1-p)}{e^2}
$$

Le produit p(1 − p) est maximal en p = 1/2, parce que p(1 − p) = 1/4 − (p − 1/2)² et qu'un carré est positif : sans rien savoir de p, on prend 1/4. Pour ±5 points à 95 % :

$$
n \ge \frac{3{,}8416 \times 0{,}25}{0{,}0025} = 384{,}16 \quad\Longrightarrow\quad n = 385 \qquad\qquad p = 0{,}9 : \frac{3{,}8416 \times 0{,}09}{0{,}0025} \approx 138{,}3 \quad\Longrightarrow\quad n = 139
$$

La question pratique est souvent différente : « mon agent fait environ 95 %, combien de tâches pour prouver qu'il dépasse 90 % ? ». L'approximation normale répond 3,8416 × 0,95 × 0,05 / 0,05² ≈ 73. Wilson, dont le centre est tiré vers 1/2 et qui est donc plus prudent près des bords, en demande davantage : en testant n par pas de 20, pour que 95 % de n soit un entier, la borne basse dépasse 0,90 à partir de n = 140 (0,9004), et vaut encore 0,888 avec 95 réussites sur 100. Le programme fait cette recherche.

### 4. pass@k contre pass^k

On suppose que les k essais d'une même tâche sont indépendants et réussissent chacun avec la probabilité p. « Au moins une réussite » est le contraire de « k échecs », et la probabilité de k échecs indépendants est le produit de leurs probabilités :

$$
\text{pass@}k = 1 - P(k \text{ échecs}) = 1 - (1-p)^k \qquad\qquad \text{pass}^k = P(k \text{ réussites}) = p^k
$$

Les deux s'encadrent autour de p. Comme p ≤ 1, on a pᵏ⁻¹ ≤ 1 et donc pᵏ = p · pᵏ⁻¹ ≤ p ; de même (1 − p)ᵏ ≤ 1 − p, donc 1 − (1 − p)ᵏ ≥ p :

$$
\text{pass}^k \;\le\; p \;\le\; \text{pass@}k
$$

Quand k grandit, pass@k tend vers 1 dès que p > 0, et pass^k tend vers 0 dès que p < 1. Avec p = 0,9 : pass@3 = 1 − 0,1³ = 0,999 et pass^3 = 0,9³ = 0,729 ; pass@8 = 1 − 10⁻⁸, presque 1, et pass^8 = 0,9⁸ ≈ 0,430. Le même agent paraît infaillible ou peu fiable selon la question posée. pass@k a un sens quand un vérificateur automatique peut choisir le bon essai parmi k (un test unitaire, un validateur de schéma) ; pass^k mesure ce que vit un client qui repose sa question : la constance.

### 5. Les estimateurs de l'étape 13 bis sont sans biais

On joue m essais d'une tâche et l'on observe c réussites. On imagine qu'on choisit au hasard k essais distincts parmi les m, indépendamment de leurs résultats. Sachant les résultats, la probabilité que les k essais choisis soient tous des échecs vaut le nombre de façons de choisir k échecs parmi m − c, divisé par le nombre de façons de choisir k essais parmi m :

$$
P(\text{k échecs choisis} \mid c) = \frac{\binom{m-c}{k}}{\binom{m}{k}}
$$

Si l'on fait maintenant la moyenne sur les résultats possibles, les k essais choisis sont k essais indépendants de probabilité d'échec 1 − p, parce que le choix ne dépend pas des résultats ; ils échouent tous avec la probabilité (1 − p)ᵏ. L'espérance de la fraction ci-dessus vaut donc exactement (1 − p)ᵏ, et 1 moins cette fraction est un estimateur sans biais de pass@k. Le même raisonnement, avec « k réussites choisies parmi c », donne l'estimateur de pass^k. Le programme vérifie les deux égalités en fractions exactes pour p = 7/10, m = 10 et k = 3. Sur 7 réussites sur 10, les estimateurs donnent pass@3 = 1 − 1/120 ≈ 0,9917 et pass^3 = 35/120 ≈ 0,2917.

Remplacer p par c/m dans les formules théoriques serait biaisé. La fonction x ↦ xᵏ est convexe sur [0, 1], et l'inégalité de Jensen donne E[(1 − c/m)ᵏ] ≥ (1 − p)ᵏ : la version « plug-in » sous-estime pass@k en moyenne, et surestime pass^k. Sur 7/10, elle donne 1 − 0,3³ = 0,973 et 0,7³ = 0,343. Enfin, la même convexité impose de calculer pass^k **tâche par tâche** puis de moyenner : avec deux tâches à p = 1 et p = 0,6, la moyenne des pass^3 vaut (1 + 0,216)/2 = 0,608, alors que (moyenne des p)³ = 0,8³ = 0,512.

### 6. Comparer deux prompts sur les mêmes tâches

On joue les prompts A et B sur les mêmes n tâches. Les tâches réussies par les deux, ou ratées par les deux, ne disent rien sur leur différence ; seules comptent les paires discordantes, n₁₀ tâches où A réussit et B échoue, n₀₁ tâches où c'est l'inverse. Si les deux prompts ont la même probabilité de succès sur chaque tâche, une tâche discordante a autant de chances d'aller dans un sens que dans l'autre, puisque p(1 − p) = (1 − p)p. Sachant le nombre D = n₁₀ + n₀₁ de discordances, n₁₀ suit donc une loi binomiale de paramètres D et 1/2. La p-valeur exacte bilatérale est

$$
p_{\text{exacte}} = \min\Big(1,\ 2 \sum_{i=\max(n_{10},\,n_{01})}^{D} \binom{D}{i} \Big/ 2^D \Big)
$$

et le χ² de McNemar en est l'approximation normale : n₁₀ a pour moyenne D/2 et pour écart-type √D/2, donc (n₁₀ − D/2)/(√D/2) = (n₁₀ − n₀₁)/√D, dont le carré, corrigé de 1 pour la continuité, est la formule de l'équation complète. Deux exemples sur 50 tâches :

- A réussit 45 tâches et B 41, avec n₁₀ = 7 et n₀₁ = 3 : χ² = (4 − 1)²/10 = 0,9 et p exacte = 2 × 176/1 024 ≈ 0,344. Rien ne prouve que B soit moins bon.
- A réussit 45 tâches et C 35, avec n₁₀ = 12 et n₀₁ = 2 : χ² = 9²/14 ≈ 5,786 > 3,84 et p exacte = 2 × 106/16 384 ≈ 0,0129. C est significativement moins bon.

Dans le second cas, les intervalles de Wilson se chevauchent : [0,5625 ; 0,8090] pour C et [0,7864 ; 0,9565] pour A. Le chevauchement ne prouve pas l'absence de différence : l'appariement élimine la difficulté propre à chaque tâche, qui gonfle les deux intervalles séparés, et c'est ce qui rend le test apparié plus sensible.

### 7. Exemple fait à la main (le code reprend ces nombres)

Un agent de facturation reçoit quatre fois la même demande : « facturez 12 000 AED HT au client BTP-017 ». L'objectif est atteint si la base contient **une** facture de ce client, de 12 000 AED HT, avec 600 AED de TVA à 5 %, soit 12 600 AED TTC.

| Tâche | Ce que fait l'agent | Phrase finale juste ? | Objectif atteint ? |
|---|---|---|---|
| T1 | émet la facture de 12 000 AED HT, puis l'annonce | oui | oui |
| T2 | annonce « facture émise : 12 600 AED TTC » sans appeler l'outil | oui | non |
| T3 | passe 12 600 comme montant HT : facture de 13 230 AED TTC | oui | non |
| T4 | consulte la fiche client, émet la bonne facture, répond « c'est fait » | non | oui |

Un correcteur qui lit la phrase compte 3 réussites sur 4, soit 0,75 ; le correcteur qui lit l'état en compte 2 sur 4, soit 0,50. Le premier se trompe sur trois tâches sur quatre : il récompense T2 et T3, qui n'ont rien fait de juste, et punit T4, qui a pris un autre chemin vers le bon résultat.

## Effets et comportement

- **Le taux ne dit pas où l'agent échoue.** On le lit avec la Tool Call F1 (étape 59) et les métriques de contexte (étapes 57 et 58) pour localiser la panne.
- **Une tâche longue se dégrade comme un produit.** Si chacune de 5 étapes réussit avec la probabilité 0,97, indépendamment, la tâche réussit avec 0,97⁵ ≈ 0,859 (fiabilité composée, [étape 1](<../01-Agent/01-Agent-Definitions-Fondamentaux.md>)) : une Goal Accuracy basse peut venir d'étapes toutes « assez bonnes ».
- **L'intervalle rétrécit comme 1/√n** (point 1) : quatre fois plus de tâches pour une incertitude deux fois plus petite.
- **pass@k monte et pass^k baisse quand k augmente** (point 4) : annoncer un pass@5 comme une fiabilité revient à compter sur cinq essais que le client ne fera pas.
- **Le correcteur fait la métrique.** Un correcteur qui lit le texte mesure la rédaction ; un correcteur qui lit l'état mesure le travail fait.

## Du symbole au code Python

| Notion | Variable ou fonction |
|---|---|
| boucle de l'agent et faux LLM | `executer_agent`, `FakeLLM`, `Reponse`, `appel_outil`, `texte` (code canonique de l'étape 1) |
| état du monde | `Comptabilite`, avec `consulter_client` et `emettre_facture` |
| correcteur, yᵢ | `objectif_atteint(compta, client, montant_ht)` |
| taux mesuré | `goal_accuracy(resultats)` |
| intervalle de Wilson | `wilson(succes, n)` (canonique) |
| taille d'échantillon | `taille_echantillon(p, marge)` et `n_minimal_barriere(taux, seuil)` |
| estimateurs de pass@k et pass^k | `pass_at_k(m, c, k)`, `pass_puissance_k(m, c, k)` |
| McNemar, χ² et p exacte | `mcnemar(a, b)` |

### Déroulé, ligne par ligne

**Le port LLM et `executer_agent`** sont recopiés sans changement du code canonique : la boucle appelle le faux LLM, exécute les blocs `tool_use`, renvoie les résultats dans un seul message, et s'arrête sur `end_turn`. Le correcteur ne lit **pas** ce que la boucle renvoie, sauf pour le contraste avec la phrase.

**`wilson(succes, n)`** et **`tva(montant_ht)`** sont aussi canoniques. Pour 45 sur 50, `wilson` renvoie (0,7864 ; 0,9565), et `None` si n = 0.

**`Comptabilite`** joue le monde extérieur : une liste `factures`. `emettre_facture` refuse un montant nul ou négatif par `ValueError`, calcule la TVA à 5 % et le TTC, ajoute la facture et la renvoie. Pour 12 000 AED HT : 600 de TVA, 12 600 TTC ; pour 12 600 pris à tort comme HT : 13 230 TTC.

**`objectif_atteint(compta, client, montant_ht)`** est le correcteur par code. Il filtre les factures du client, puis exige `len(fs) == 1` (une facture émise deux fois est un échec), le bon montant HT et la bonne TVA. T4 passe `montant_ht` à `12000.0` : la comparaison `12000.0 == 12000` est vraie en Python, et la tâche est réussie par un autre chemin.

**`goal_accuracy(resultats)`** renvoie `sum(resultats) / len(resultats)`, et `None` pour une liste vide. L'ancien code renvoyait 0,0, comme si un jeu vide prouvait un agent nul.

**`taille_echantillon(p, marge)`** applique `math.ceil(z * z * p * (1 - p) / (marge * marge))` : 384,16 arrondi au-dessus donne 385. **`n_minimal_barriere(taux, seuil)`** essaie n = 20, 40, … et renvoie le premier n pour lequel la borne basse de Wilson, à `round(taux * n)` réussites, dépasse le seuil : 140 pour 95 % contre 90 %.

**`pass_at_k(m, c, k)`** et **`pass_puissance_k(m, c, k)`** vérifient 0 ≤ c ≤ m et 1 ≤ k ≤ m, sinon `ValueError`, puis appliquent les formules avec `math.comb`. Pour m = 10, c = 7, k = 3 : `comb(3, 3) / comb(10, 3)` vaut 1/120, et `comb(7, 3) / comb(10, 3)` vaut 35/120.

**`mcnemar(a, b)`** vérifie que les deux listes portent sur les mêmes tâches, compte `perdus` (n₁₀) et `gagnes` (n₀₁), renvoie `None` pour le χ² et la p-valeur s'il n'y a aucune discordance, puis calcule le χ² corrigé et la p-valeur exacte en sommant les coefficients binomiaux de la queue de la loi.

**`main()`**, bloc par bloc.

1. Les quatre tâches du point 7, chacune avec une `Comptabilite` neuve et un script de faux LLM. On affiche le statut de la boucle, le nombre d'appels, les factures créées, le verdict de la phrase et celui de l'état, puis les deux taux 0,50 et 0,75.
2. 45 réussites sur 50 : taux 0,90, Wilson [0,7864 ; 0,9565], barrière refusée.
3. 385 et 139 tâches pour ±5 points ; 140 tâches pour prouver 90 % avec un agent à 95 %, et l'on vérifie que 120 ne suffisent pas.
4. pass@k et pass^k pour p = 0,9 et k = 3 ou 8, avec l'encadrement du point 4 ; les estimateurs sur 7/10 ; puis, avec `fractions.Fraction`, les espérances exactes sur la loi binomiale : elles valent exactement (1 − p)³ et p³, alors que la version « plug-in » sous-estime pass@3. Une dernière ligne vérifie l'effet de l'hétérogénéité entre tâches.
5. Les deux comparaisons du point 6, construites tâche par tâche, avec leurs χ² et p-valeurs exactes, puis le chevauchement des intervalles de Wilson de A et C. Le dernier `assert` vérifie la fiabilité composée 0,97⁵ ≈ 0,859.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`texte(t)`** — Cette petite fonction est l'imprimeur qui compose une réplique prête à être glissée dans une réponse du faux LLM : elle reçoit une chaîne et renvoie un `Bloc` de type `"text"` qui la porte, sans identifiant, sans nom d'outil et sans arguments. Elle ne vérifie rien et ne lève aucune exception ; elle sert à écrire les scripts de `main`, par exemple la phrase finale « Facture émise : 12 600 AED TTC. » que l'agent prononce dans trois des quatre tâches, et « C'est fait. » dans la tâche T4, phrases que la boucle recolle ensuite pour former la réponse finale.

**`appel_outil(nom, arguments, id_)`** — Celle-ci fabrique le bon de commande qu'un modèle adresse à un outil : elle reçoit le nom de l'outil, le dictionnaire de ses arguments et un identifiant d'appel, et renvoie un `Bloc` de type `"tool_use"` qui réunit ces trois informations, sans aucune vérification. C'est avec elle que `main` écrit, dans les scripts du faux LLM, les demandes `emettre_facture` au client BTP-017 pour 12 000 AED HT, l'erreur de la tâche T3 qui facture 12 600 comme si c'était du HT, ou la consultation préalable `consulter_client` de la tâche T4.

**`FakeLLM.__init__(script)`** — Le constructeur prépare un comédien qui ne connaît que son texte : il reçoit la liste des réponses prévues, en garde une copie pour que le script d'origine ne soit jamais modifié, et met à zéro le compteur `appels`, qui dira à quelle réplique il en est. Il ne renvoie rien ; ce faux LLM, déterministe et gratuit, remplace le vrai modèle pour que chaque tâche de `main` rejoue exactement la même conversation à chaque exécution.

**`FakeLLM.create(system, messages, tools)`** — Cette méthode est le moment où le comédien donne sa réplique suivante, quoi qu'on lui dise : elle reçoit, par mots-clés, le prompt système, l'historique des messages et les schémas d'outils, exactement comme l'API d'un vrai modèle, mais les ignore. Elle lève une `RuntimeError` si le script est épuisé, et sinon renvoie la réponse prévue au rang du compteur, puis avance ce compteur d'une case ; c'est elle que `executer_agent` appelle à chaque tour de boucle.

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — Cette fonction est la boucle de l'agent, un chef de chantier qui demande au modèle quoi faire, le fait faire par les outils et rapporte le résultat, jusqu'à ce que le travail soit fini : elle reçoit le modèle, le prompt système, la question, le dictionnaire des outils, leurs schémas et un maximum de 8 étapes par défaut. À chaque tour, elle appelle `create`, range la réponse telle quelle dans l'historique et s'arrête sur un refus, une réponse tronquée ou un `end_turn`, en recollant alors les blocs de texte en réponse finale ; elle saute un `pause_turn`, détecte une boucle quand les mêmes appels reviennent deux fois de suite, exécute chaque appel d'outil, transforme une exception en résultat marqué `is_error` au lieu de l'avaler, et renvoie tous les résultats dans un seul message. Elle renvoie un dictionnaire avec le statut, la trace des appels, le nombre d'étapes et, si elle a fini, la réponse ; dans `main`, les quatre tâches finissent avec 1, 0, 1 et 2 appels.

**`wilson(succes, n, z)`** — Cette fonction est la fonction canonique du parcours, l'arpenteur prudent qui ne donne jamais un taux sans sa marge d'incertitude : elle reçoit un nombre de réussites, un nombre d'essais et le quantile z, 1,96 par défaut, renvoie `None` si n = 0, lève `ValueError` si les réussites sortent de [0, n], puis calcule le centre et la demi-largeur de l'intervalle de Wilson à 95 %. Elle renvoie le couple (borne basse, borne haute) : (0,7864 ; 0,9565) pour 45 réussites sur 50, ce qui refuse la barrière de 0,90 malgré un taux observé de 0,90, et (0,5625 ; 0,8090) pour le prompt C à 35 sur 50.

**`tva(montant_ht, taux)`** — Celle-ci est la calculette du comptable : elle reçoit un montant hors taxes et un taux, 5 % par défaut, celui de la TVA standard des Émirats, et renvoie simplement leur produit, sans arrondi ni vérification. Pour 12 000 AED HT, elle donne 600 AED de TVA ; `emettre_facture` l'utilise pour remplir chaque facture et `objectif_atteint` pour vérifier que la TVA inscrite est bien celle qu'on attendait, arrondie au centime.

**`Comptabilite.__init__()`** — Le constructeur ouvre un registre de facturation vierge, comme un comptable qui commence un classeur neuf pour chaque mission : il ne reçoit aucun argument et crée seulement une liste `factures` vide. Il ne renvoie rien ; `main` en crée une neuve pour chacune des quatre tâches, afin qu'une facture émise dans une tâche ne fausse pas le verdict de la suivante, et c'est ce registre, l'état du monde, que le correcteur lira à la fin plutôt que la phrase de l'agent.

**`Comptabilite.consulter_client(client)`** — Cette méthode joue le guichet de renseignements de la comptabilité : elle reçoit le code d'un client et renvoie toujours la même fiche simulée, un dictionnaire qui reprend ce code, indique l'émirat Dubaï et un numéro d'enregistrement fiscal valide. Elle ne modifie pas le registre et ne lève aucune exception ; dans `main`, seule la tâche T4 l'appelle avant d'émettre la facture, ce qui montre qu'un agent peut atteindre l'objectif par un autre chemin que celui prévu.

**`Comptabilite.emettre_facture(client, montant_ht)`** — Celle-ci est la seule action qui change vraiment le monde : elle reçoit le client et le montant hors taxes, lève une `ValueError` si ce montant est nul ou négatif, puis construit une facture avec le montant HT, la TVA calculée par `tva` et le TTC à 1,05 fois le HT, tous arrondis au centime, l'ajoute au registre et la renvoie. Pour 12 000 AED HT, elle inscrit 600 de TVA et 12 600 TTC ; pour 12 600 pris à tort comme HT dans la tâche T3, elle inscrit 13 230 TTC, et le correcteur, qui lit ce registre, détecte l'erreur que la phrase de l'agent cachait.

**`goal_accuracy(resultats)`** — Cette fonction est le tableau d'affichage final de l'évaluation : elle reçoit la liste des verdicts du correcteur, un booléen par tâche, et renvoie la part de tâches réussies, ou `None` pour une liste vide, au lieu du 0,0 de l'ancien code qui faisait passer un jeu vide pour un agent nul. Sur les quatre tâches du point 7, elle vaut 0,50 quand on juge l'état final et 0,75 quand on juge la phrase, et 0,90 pour 45 réussites sur 50.

**`n_minimal_barriere(taux, seuil, pas, n_max)`** — Cette fonction est l'intendant qui cherche combien de tâches il faut prévoir pour qu'un bon agent puisse prouver sa valeur : elle reçoit le taux de réussite attendu, le seuil de la barrière, un pas de 20 et une taille maximale de 5 000 par défaut, essaie n = 20, 40, 60 et ainsi de suite, et pour chaque n calcule la borne basse de Wilson d'un agent qui réussirait `round(taux * n)` tâches. Elle renvoie le premier n dont la borne basse dépasse strictement le seuil, ou `None` si aucun ne suffit jusqu'à la taille maximale : pour un agent à 95 % face à une barrière à 90 %, il faut 140 tâches, de borne basse 0,9004, et `main` vérifie que 120 ne suffisent pas.

**`main()`** — C'est le chef d'orchestre des cinq démonstrations : il joue les quatre tâches de facturation, chacune avec un registre neuf et son script, et compare les verdicts de l'état, 0,50, et de la phrase, 0,75, puis montre que 45 réussites sur 50 ne franchissent pas la barrière de 0,90 par la borne basse de Wilson. Il calcule ensuite les tailles d'échantillon 385, 139 et 140, compare pass@k et pass^k pour p = 0,9, vérifie les estimateurs sur 7 réussites sur 10 et leurs espérances exactes en fractions, puis compare trois prompts avec le test de McNemar, avec χ² = 0,900 contre B et 5,786 contre C, et la fiabilité composée 0,97⁵ ; « OK » n'apparaît que si tout concorde.

```python
"""Étape 60 — Agent Goal Accuracy : correcteur sur l'état final, Wilson, taille d'échantillon, pass@k et pass^k, deux prompts."""
import json
import math
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from math import comb

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- port LLM (code canonique, recopié sans changement)
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


def tva(montant_ht: float, taux: float = 0.05) -> float:
    """TVA standard des EAU : 5 %."""
    return montant_ht * taux


# ---------------------------------------------------------------- monde simulé et correcteur
class Comptabilite:
    """État du monde que l'agent modifie ; le correcteur lit cet état, pas la phrase finale."""

    def __init__(self):
        self.factures: list[dict] = []

    def consulter_client(self, client: str) -> dict:
        return {"client": client, "emirat": "Dubaï", "trn_valide": True}

    def emettre_facture(self, client: str, montant_ht: float) -> dict:
        if montant_ht <= 0:
            raise ValueError("montant HT > 0")
        f = {"client": client, "montant_ht": round(montant_ht, 2), "tva": round(tva(montant_ht), 2),
             "ttc": round(montant_ht * 1.05, 2)}
        self.factures.append(f)
        return f


def objectif_atteint(compta: Comptabilite, client: str, montant_ht: float) -> bool:
    """Correcteur par code : exactement une facture pour ce client, au bon montant HT, avec 5 % de TVA."""
    fs = [f for f in compta.factures if f["client"] == client]
    return len(fs) == 1 and fs[0]["montant_ht"] == montant_ht and fs[0]["tva"] == round(tva(montant_ht), 2)


def goal_accuracy(resultats: list[bool]) -> float | None:
    """Part des tâches dont l'objectif est atteint ; None si aucune tâche."""
    return sum(resultats) / len(resultats) if resultats else None


def taille_echantillon(p: float, marge: float, z: float = 1.96) -> int:
    """n >= z² p(1 − p) / e² : demi-largeur au plus e (approximation normale)."""
    if not 0 <= p <= 1 or not 0 < marge < 1:
        raise ValueError("0 <= p <= 1 et 0 < marge < 1")
    return math.ceil(z * z * p * (1 - p) / (marge * marge))


def n_minimal_barriere(taux: float, seuil: float, pas: int = 20, n_max: int = 5000) -> int | None:
    """Plus petit n (multiple de pas) pour lequel un taux observé égal à taux franchit le seuil par sa borne basse."""
    for n in range(pas, n_max + 1, pas):
        if wilson(round(taux * n), n)[0] > seuil:
            return n
    return None


def pass_at_k(m: int, c: int, k: int) -> float:
    """Estimateur sans biais de 1 − (1 − p)^k à partir de c réussites sur m essais d'une même tâche."""
    if not (0 <= c <= m and 1 <= k <= m):
        raise ValueError("il faut 0 <= c <= m et 1 <= k <= m")
    return 1 - comb(m - c, k) / comb(m, k)


def pass_puissance_k(m: int, c: int, k: int) -> float:
    """Estimateur sans biais de p^k."""
    if not (0 <= c <= m and 1 <= k <= m):
        raise ValueError("il faut 0 <= c <= m et 1 <= k <= m")
    return comb(c, k) / comb(m, k)


def mcnemar(a: list[bool], b: list[bool]) -> tuple[int, int, float | None, float | None]:
    """Paires discordantes, χ² avec correction de continuité, et p exacte bilatérale (loi binomiale de paramètre 1/2)."""
    if len(a) != len(b):
        raise ValueError("les deux versions doivent être jouées sur les mêmes tâches")
    perdus = sum(1 for x, y in zip(a, b) if x and not y)
    gagnes = sum(1 for x, y in zip(a, b) if not x and y)
    n = perdus + gagnes
    if n == 0:
        return perdus, gagnes, None, None
    chi2 = (abs(perdus - gagnes) - 1) ** 2 / n
    p_exacte = min(1.0, 2 * sum(comb(n, i) for i in range(max(perdus, gagnes), n + 1)) / 2 ** n)
    return perdus, gagnes, chi2, p_exacte


def main() -> None:
    print("1. Le correcteur lit l'état final, pas la phrase")
    phrase = "Facture émise : 12 600 AED TTC."
    scripts = {
        "T1 direct": [Reponse("tool_use", [appel_outil("emettre_facture", {"client": "BTP-017", "montant_ht": 12000}, "t1")]),
                      Reponse("end_turn", [texte(phrase)])],
        "T2 phrase seule": [Reponse("end_turn", [texte(phrase)])],
        "T3 TTC pris pour HT": [Reponse("tool_use", [appel_outil("emettre_facture", {"client": "BTP-017", "montant_ht": 12600}, "t1")]),
                                Reponse("end_turn", [texte(phrase)])],
        "T4 autre chemin": [Reponse("tool_use", [appel_outil("consulter_client", {"client": "BTP-017"}, "t1")]),
                            Reponse("tool_use", [appel_outil("emettre_facture", {"client": "BTP-017", "montant_ht": 12000.0}, "t2")]),
                            Reponse("end_turn", [texte("C'est fait.")])],
    }
    par_etat, par_phrase = [], []
    for nom, script in scripts.items():
        compta = Comptabilite()
        outils = {"consulter_client": compta.consulter_client, "emettre_facture": compta.emettre_facture}
        res = executer_agent(FakeLLM(script), "Agent de facturation", "Facturez 12 000 AED HT au client BTP-017.", outils, [])
        ok_etat = objectif_atteint(compta, "BTP-017", 12000)
        ok_phrase = "12 600" in res.get("reponse", "")
        par_etat.append(ok_etat)
        par_phrase.append(ok_phrase)
        print(f"   {nom:<20} {res['statut']}, {len(res['trace'])} appel(s), factures {[f['ttc'] for f in compta.factures]}"
              f"   phrase juste : {ok_phrase!s:<5}   objectif atteint : {ok_etat}")
    print(f"   Goal Accuracy par l'état = {goal_accuracy(par_etat):.2f}   par la phrase = {goal_accuracy(par_phrase):.2f}")
    assert par_etat == [True, False, False, True] and par_phrase == [True, True, True, False]
    assert goal_accuracy([]) is None

    print("2. 45 tâches réussies sur 50 : la barrière de 0,90 se juge sur la borne basse")
    resultats = [True] * 45 + [False] * 5
    acc = goal_accuracy(resultats)
    bas, haut = wilson(sum(resultats), len(resultats))
    print(f"   Goal Accuracy = {acc:.2f}   Wilson 95 % = [{bas:.4f} ; {haut:.4f}]   barrière franchie : {bas >= 0.90}")
    assert acc == 0.9 and (round(bas, 4), round(haut, 4)) == (0.7864, 0.9565) and bas < 0.90

    print("3. Combien de tâches évaluer ?")
    n_pire, n_90 = taille_echantillon(0.5, 0.05), taille_echantillon(0.9, 0.05)
    n_bar = n_minimal_barriere(0.95, 0.90)
    print(f"   marge ±5 points : {n_pire} tâches si p = 0,5 ; {n_90} si p = 0,9")
    print(f"   agent à 95 % : borne basse > 0,90 à partir de n = {n_bar} (Wilson {wilson(round(0.95 * n_bar), n_bar)[0]:.4f})")
    assert n_pire == 385 and n_90 == 139
    assert wilson(round(0.95 * (n_bar - 20)), n_bar - 20)[0] <= 0.90 < wilson(round(0.95 * n_bar), n_bar)[0]

    print("4. pass@k contre pass^k (p = 0,9 par essai, essais indépendants)")
    p = 0.9
    for k in (3, 8):
        pa, pk = 1 - (1 - p) ** k, p ** k
        print(f"   k = {k}   pass@k = {pa:.6f}   pass^k = {pk:.4f}")
        assert pk <= p <= pa
    assert round(p ** 8, 4) == 0.4305
    print(f"   estimateurs, 7 réussites sur 10, k = 3 : pass@3 = {pass_at_k(10, 7, 3):.6f}   pass^3 = {pass_puissance_k(10, 7, 3):.6f}")
    assert pass_at_k(10, 7, 3) == 1 - 1 / 120 and pass_puissance_k(10, 7, 3) == 35 / 120
    q, m, k = Fraction(7, 10), 10, 3                                    # espérance exacte sur la loi binomiale
    loi = [comb(m, c) * q ** c * (1 - q) ** (m - c) for c in range(m + 1)]
    assert sum(w * Fraction(comb(m - c, k), comb(m, k)) for c, w in enumerate(loi)) == (1 - q) ** k
    assert sum(w * Fraction(comb(c, k), comb(m, k)) for c, w in enumerate(loi)) == q ** k
    assert sum(w * (1 - (1 - Fraction(c, m)) ** k) for c, w in enumerate(loi)) < 1 - (1 - q) ** k   # le « plug-in » sous-estime
    assert (1.0 ** 3 + 0.6 ** 3) / 2 > 0.8 ** 3                         # tâches hétérogènes : moyenne des p^k >= (moyenne p)^k

    print("5. Deux prompts sur les mêmes 50 tâches")
    a = [True] * 38 + [True] * 7 + [False] * 3 + [False] * 2            # prompt A : 45/50
    b = [True] * 38 + [False] * 7 + [True] * 3 + [False] * 2            # prompt B : 41/50
    c = [True] * 33 + [False] * 12 + [True] * 2 + [False] * 3           # prompt C : 35/50
    a2 = [True] * 33 + [True] * 12 + [False] * 2 + [False] * 3          # A réordonné pour l'appariement avec C
    for nom, x, y in (("A contre B", a, b), ("A contre C", a2, c)):
        perdus, gagnes, chi2, pe = mcnemar(x, y)
        print(f"   {nom} : {sum(x)}/50 contre {sum(y)}/50   perdues {perdus}, gagnées {gagnes}   χ² = {chi2:.3f}   p exacte = {pe:.4f}")
    assert mcnemar(a, b) == (7, 3, 0.9, 0.34375)
    perdus, gagnes, chi2, pe = mcnemar(a2, c)
    assert (perdus, gagnes) == (12, 2) and math.isclose(chi2, 81 / 14) and math.isclose(pe, 212 / 16384) and chi2 > 3.84
    bas_c, haut_c = wilson(35, 50)
    print(f"   Wilson de C : [{bas_c:.4f} ; {haut_c:.4f}] chevauche celui de A, et pourtant l'écart apparié est significatif")
    assert bas_c < bas < haut_c
    assert round(0.97 ** 5, 3) == 0.859                                 # tâche en 5 étapes à 0,97 (étape 1)

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Le correcteur lit l'état final, pas la phrase
   T1 direct            fini, 1 appel(s), factures [12600.0]   phrase juste : True    objectif atteint : True
   T2 phrase seule      fini, 0 appel(s), factures []   phrase juste : True    objectif atteint : False
   T3 TTC pris pour HT  fini, 1 appel(s), factures [13230.0]   phrase juste : True    objectif atteint : False
   T4 autre chemin      fini, 2 appel(s), factures [12600.0]   phrase juste : False   objectif atteint : True
   Goal Accuracy par l'état = 0.50   par la phrase = 0.75
2. 45 tâches réussies sur 50 : la barrière de 0,90 se juge sur la borne basse
   Goal Accuracy = 0.90   Wilson 95 % = [0.7864 ; 0.9565]   barrière franchie : False
3. Combien de tâches évaluer ?
   marge ±5 points : 385 tâches si p = 0,5 ; 139 si p = 0,9
   agent à 95 % : borne basse > 0,90 à partir de n = 140 (Wilson 0.9004)
4. pass@k contre pass^k (p = 0,9 par essai, essais indépendants)
   k = 3   pass@k = 0.999000   pass^k = 0.7290
   k = 8   pass@k = 1.000000   pass^k = 0.4305
   estimateurs, 7 réussites sur 10, k = 3 : pass@3 = 0.991667   pass^3 = 0.291667
5. Deux prompts sur les mêmes 50 tâches
   A contre B : 45/50 contre 41/50   perdues 7, gagnées 3   χ² = 0.900   p exacte = 0.3438
   A contre C : 45/50 contre 35/50   perdues 12, gagnées 2   χ² = 5.786   p exacte = 0.0129
   Wilson de C : [0.5625 ; 0.8090] chevauche celui de A, et pourtant l'écart apparié est significatif
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un taux de réussite d'agent se construit en trois temps. Un correcteur qui lit l'état et non la phrase ; un intervalle et un nombre de tâches suffisant pour que la barrière ait un sens ; une comparaison appariée pour décider entre deux versions. pass@k et pass^k répondent à deux questions différentes, et seule la seconde parle de fiabilité.

## Squelette algorithmique

Quatre algorithmes, un par question du fichier. ÉVALUER_ET_DÉCIDER prend un jeu de tâches, l'agent et un correcteur, joue chaque tâche sur un état du monde neuf, lit l'état final, puis rend le taux, son intervalle de Wilson et la décision de la barrière. N_MINIMAL_BARRIÈRE prend un taux attendu et un seuil, et cherche le plus petit nombre de tâches qui permettrait de franchir le seuil par la borne basse. ESTIMER_PASS prend les m essais d'une tâche et rend les estimateurs sans biais de pass@k et pass^k. COMPARER_DEUX_PROMPTS prend les résultats de deux versions sur les mêmes tâches, ne garde que les paires discordantes et rend le χ² de McNemar et la p-valeur exacte.

```text
ALGORITHME ÉVALUER_ET_DÉCIDER
ENTRÉES : tâches[1..n], chacune avec sa demande et son objectif ; AGENT ; CORRECTEUR(état, objectif) ;
          seuil τ ; z = 1,96
SORTIE  : (taux, intervalle, décision)

  SI n = 0 ALORS RETOURNER (INDÉFINI, INDÉFINI, REFUSER) FIN SI    ▷ aucune donnée : la barrière ne passe pas
  s ← 0
  POUR i de 1 à n FAIRE
      état ← nouvel état du monde, vide
      exécuter AGENT sur la demande de tâches[i], avec des outils qui écrivent dans état
      SI CORRECTEUR(état, objectif de tâches[i]) ALORS s ← s + 1 FIN SI   ▷ on lit l'état, pas la phrase
  FIN POUR
  taux ← s / n
  (bas, haut) ← WILSON(s, n, z)
  SI bas ≥ τ ALORS décision ← DÉPLOYER SINON décision ← REFUSER FIN SI
  RETOURNER (taux, (bas, haut), décision)
```

```text
ALGORITHME N_MINIMAL_BARRIÈRE
ENTRÉES : taux attendu t ; seuil τ ; pas ; n_max
SORTIE  : le plus petit n, multiple de pas, dont la borne basse de Wilson dépasse τ ; ou AUCUN

  n ← pas
  TANT QUE n ≤ n_max FAIRE
      s ← arrondi(t × n)
      SI borne basse de WILSON(s, n) > τ ALORS RETOURNER n FIN SI
      n ← n + pas
  FIN TANT QUE
  RETOURNER AUCUN
```

```text
ALGORITHME ESTIMER_PASS
ENTRÉES : m essais d'une même tâche, dont c réussis ; k
SORTIE  : (pass@k estimé, pass^k estimé)

  SI NON (0 ≤ c ≤ m ET 1 ≤ k ≤ m) ALORS ERREUR FIN SI
  RETOURNER (1 − C(m − c, k) / C(m, k),  C(c, k) / C(m, k))      ▷ C(a, b) : façons de choisir b objets parmi a
```

```text
ALGORITHME COMPARER_DEUX_PROMPTS
ENTRÉES : a[1..n], b[1..n], réussites des versions A et B sur les MÊMES tâches
SORTIE  : (n₁₀, n₀₁, χ², p exacte)

  SI longueur(a) ≠ longueur(b) ALORS ERREUR FIN SI
  n₁₀ ← 0 ; n₀₁ ← 0
  POUR i de 1 à n FAIRE
      SI a[i] ET NON b[i] ALORS n₁₀ ← n₁₀ + 1 FIN SI
      SI NON a[i] ET b[i] ALORS n₀₁ ← n₀₁ + 1 FIN SI
  FIN POUR
  D ← n₁₀ + n₀₁
  SI D = 0 ALORS RETOURNER (0, 0, INDÉFINI, INDÉFINI) FIN SI
  χ² ← (|n₁₀ − n₀₁| − 1)² / D
  queue ← 0
  POUR i de max(n₁₀, n₀₁) à D FAIRE
      queue ← queue + C(D, i)
  FIN POUR
  RETOURNER (n₁₀, n₀₁, χ², min(1, 2 × queue / 2^D))
```

**Complexité :** ÉVALUER_ET_DÉCIDER joue n tâches ; chacune coûte E tours de boucle, un appel au modèle et ses outils par tour, puis un passage du correcteur sur l'état, en O(F) pour filtrer F factures : O(n × (E × c_LLM + c_outils + F)) en temps, où c_LLM et c_outils désignent le coût d'un appel au modèle et celui des outils d'un tour. L'appel au modèle domine tout le reste en production : c'est pourquoi le nombre de tâches donné par N_MINIMAL_BARRIÈRE se traduit directement en budget. La mémoire vaut O(F + E) pour l'état et l'historique d'une seule tâche, recréés à chaque tâche ; WILSON est un nombre fixe d'opérations, en O(1). N_MINIMAL_BARRIÈRE fait au plus n_max / pas tours de boucle, chacun en O(1) : O(n_max / pas) en temps et O(1) en mémoire ; avec un pas de 20, elle s'arrête au septième tour, à n = 140. ESTIMER_PASS calcule trois coefficients binomiaux ; chacun demande O(k) multiplications et divisions entières, sur des entiers dont la taille grandit en O(k log m) bits, et la mémoire reste en O(1) en dehors de ces entiers. COMPARER_DEUX_PROMPTS fait un passage sur les n tâches, en O(n), puis somme au plus D + 1 coefficients binomiaux de rang D, chacun en O(D) opérations : O(n + D²) en temps tel qu'il est écrit, et O(1) en mémoire en dehors des listes reçues. Calculer chaque coefficient à partir du précédent, par C(D, i + 1) = C(D, i) × (D − i) / (i + 1), ramènerait la queue à O(D).

**Du squelette au code :** ÉVALUER_ET_DÉCIDER est réparti entre les blocs 1 et 2 de `main()`. La boucle POUR est la boucle sur `scripts.items()` ; « nouvel état du monde » est `Comptabilite()` ; « exécuter AGENT » est `executer_agent(FakeLLM(script), …, outils, [])`, avec des `outils` qui pointent vers les méthodes de cette `Comptabilite` ; le CORRECTEUR est `objectif_atteint(compta, client, montant_ht)` ; le taux est `goal_accuracy(resultats)`, qui renvoie `None` pour INDÉFINI ; WILSON est la fonction canonique `wilson(succes, n)` ; et la décision est la comparaison `bas >= 0.90` du bloc 2. N_MINIMAL_BARRIÈRE est `n_minimal_barriere(taux, seuil, pas, n_max)`, où `for n in range(pas, n_max + 1, pas)` remplace le TANT QUE et `round(taux * n)` l'arrondi ; la formule voisine `taille_echantillon(p, marge)` n'a pas besoin de squelette, c'est un calcul direct en O(1). ESTIMER_PASS est le couple `pass_at_k(m, c, k)` et `pass_puissance_k(m, c, k)`, dont l'ERREUR est un `ValueError` et C(a, b) l'appel `comb(a, b)` du module `math`. COMPARER_DEUX_PROMPTS est `mcnemar(a, b)` : n₁₀ et n₀₁ y s'appellent `perdus` et `gagnes`, D s'appelle `n`, et la boucle de la queue est `sum(comb(n, i) for i in range(max(perdus, gagnes), n + 1))`.

## Cas d'usage réels aux Émirats

Les volumes, les taux et les seuils ci-dessous sont illustratifs ; seules les règles réglementaires citées sont réelles.

### BTP — une facture qui existe vraiment

Un groupe de construction qui travaille sur de grands chantiers à Dubaï confie à un agent l'émission des factures d'avancement : montant HT tiré du décompte, TVA à 5 %, retenue de garantie du contrat. Le premier banc d'évaluation notait la phrase finale de l'agent, et affichait une réussite de 0,75 sur un échantillon où l'agent, dans un cas sur quatre, annonçait une facture qu'il n'avait jamais émise et, dans un autre, facturait le TTC comme s'il était HT. Le correcteur actuel lit le système comptable après chaque tâche : une seule facture par décompte, le bon montant HT, la TVA à 5 %, la retenue au taux du contrat. La réussite mesurée tombe à 0,50, ce qui est désagréable mais vrai, et l'équipe découvre que les deux pannes viennent de deux causes différentes : un prompt qui laissait l'agent conclure sans appeler l'outil, et une description d'outil qui ne précisait pas « montant hors taxes ». Une facture fausse émise à un client engage le groupe vis-à-vis de l'administration fiscale, et un avoir coûte du temps aux deux parties. L'indicateur suivi est la Goal Accuracy par l'état, publiée avec son intervalle de Wilson, par type de document.

### Banque — refuser à 0,90 quand l'intervalle commence à 0,79

Une banque de détail de Dubaï évalue son agent de pré-instruction des prêts personnels : la tâche est réussie si la décision proposée respecte les règles de la CBUAE (ratio d'endettement total d'au plus 50 % du salaire, toutes mensualités comprises, 30 % pour un retraité ; montant d'au plus 20 fois le salaire ; durée d'au plus 48 mois) et si la mensualité calculée est juste. Sur 50 dossiers de test, l'agent réussit 45 fois : 0,90, exactement le seuil fixé par la conformité. La barrière, qui juge la borne basse de Wilson, refuse pourtant la version, parce que l'intervalle va de 0,786 à 0,957 (démonstration, point 2). L'équipe ne baisse pas le seuil : elle agrandit le jeu, et le point 3 lui dit qu'avec un agent proche de 95 % il faut environ 140 dossiers pour prouver « au moins 90 % ». Le nouveau jeu est construit à partir de dossiers anonymisés de toutes les catégories de clients, retraités compris, pour que la borne basse parle de toute la clientèle. L'indicateur suivi est la borne basse de Wilson de la Goal Accuracy, par catégorie de clients.

### Immobilier — une estimation dans la fourchette, à chaque fois

L'agent d'estimation d'une agence de Dubaï réussit une tâche si l'écart relatif entre son estimation et le prix de transaction finalement constaté est d'au plus 10 % : |estimation − prix réel| / prix réel ≤ 0,10. L'agence joue chaque bien de son jeu de test cinq fois. Sur un bien typique, sept essais sur dix tombent dans la fourchette : pass@3 vaut 0,992, mais pass^3 seulement 0,292, et c'est ce second nombre qui compte, parce qu'un client qui redemande une estimation et obtient un autre prix perd confiance. L'agence calcule pass^3 bien par bien, puis fait la moyenne, au lieu d'élever au cube le taux global : les biens faciles et les biens difficiles ne se compensent pas (point 5). La constance remonte quand le calcul des comparables passe dans un outil déterministe et que l'agent ne fait plus que le commenter. L'enjeu est réel pour l'acheteur, qui paie en plus 4 % de frais de transfert au DLD sur le prix. L'indicateur suivi est la moyenne des pass^3 par bien, publiée avec la Goal Accuracy simple.

### Assurance — deux prompts comparés sur les mêmes sinistres

Un assureur auto et santé veut remplacer le prompt de son agent de pré-décision des sinistres, A, par une version plus courte, C, moins coûteuse en tokens. Sur 50 sinistres de test, A réussit 45 fois et C 35 fois ; les intervalles de Wilson se chevauchent, et une lecture rapide conclurait « pas de différence démontrée ». Joués sur les **mêmes** sinistres, les deux prompts ne divergent que sur 14 dossiers : 12 réussis par A seul, 2 par C seul. McNemar donne χ² ≈ 5,79 et une p-valeur exacte d'environ 0,013 : C est significativement moins bon et le changement est refusé (point 6). Le banc d'évaluation exige désormais, pour tout changement de prompt, la borne basse de Wilson au-dessus du seuil et l'absence de régression significative sur les paires, comme le prévoit l'étape 13 bis. L'assureur est supervisé par la CBUAE et la décision finale reste au gestionnaire. Les indicateurs suivis sont la Goal Accuracy par l'état et le résultat du test apparié à chaque version.

### RH — un onboarding complet, pas cinq étapes « presque » réussies

Un cabinet RH présent dans plusieurs émirats fait conduire par un agent l'arrivée d'un salarié : enregistrement du contrat auprès du MOHRE, inscription au système de protection des salaires (WPS), visite médicale, demande d'Emirates ID, ouverture du dossier de visa. La tâche n'est réussie que si les cinq démarches sont faites et cohérentes entre elles. Chaque étape, mesurée seule, réussit environ 97 % du temps ; la tâche entière ne réussit qu'environ 86 % du temps, parce que 0,97⁵ ≈ 0,859 (fiabilité composée, étape 1). Le cabinet publie donc la Goal Accuracy de la tâche entière, et non la moyenne des réussites par étape, qui faisait croire à un agent fiable à 97 %. Il cherche ensuite l'étape la plus fragile avec la Tool Call F1 de l'étape 59, et c'est en général la cohérence des noms translittérés entre deux formulaires. L'indicateur suivi est la Goal Accuracy des dossiers complets, avec son intervalle, mois par mois.

### Secteur public — la démarche aboutie, du point de vue de l'usager

Un service public en ligne accessible par UAE Pass laisse un agent bilingue conduire des démarches de bout en bout : renouveler un document, payer une amende, prendre un rendez-vous. Le correcteur vérifie dans le système de gestion que la démarche est enregistrée, payée si besoin, et notifiée à l'usager ; un message « votre démarche est terminée » sans enregistrement compte comme un échec. L'équipe distingue deux nombres. pass@3 sert seulement en interne, pour un agent de préparation dont un vérificateur automatique choisit le meilleur brouillon parmi trois ; pour les usagers, qui ne font qu'un essai et reviennent parfois avec la même demande, elle publie la Goal Accuracy simple et pass^3. Les démarches de test utilisent des identités fictives, la PDPL interdisant d'évaluer sur des données d'usagers sans base légale. Les indicateurs suivis sont la Goal Accuracy par démarche et par langue, et pass^3 sur les démarches les plus fréquentes.

## Pièges et limites

- **Noter la phrase au lieu de l'état.** Un correcteur qui lit le texte récompense un agent qui annonce un travail non fait ; on vérifie l'état du monde chaque fois que c'est possible.
- **Mettre la barrière sur le taux mesuré.** 45/50 = 0,90 ne prouve pas 0,90 ; on compare la borne basse de Wilson au seuil, et l'on dimensionne le jeu en conséquence.
- **Présenter pass@k comme une fiabilité.** pass@k suppose qu'un vérificateur choisit le bon essai ; la constance se mesure par pass^k, calculé tâche par tâche.
- **Comparer deux versions par le chevauchement de leurs intervalles.** On les compare sur les mêmes tâches, avec un test apparié.
- **Renvoyer 0 pour un jeu vide.** Aucun cas joué ne prouve rien ; on renvoie `None` et l'on bloque la barrière, qui ne doit pas passer faute de données.

### Exercice feuille blanche

1. Sans regarder le code, écrire `goal_accuracy` et un correcteur qui lit l'état d'une `Comptabilite`, puis vérifier 0,50 sur les quatre tâches du point 7.
2. Prédire, puis vérifier : avec 47 réussites sur 50, la barrière à 0,90 sur la borne basse passe-t-elle ? (Réponse : non, la borne basse vaut environ 0,838.) Pour p = 0,8, que valent pass@3 et pass^3 ? (Réponse : 0,992 et 0,512.)
3. Trouver le bug : `pass_puissance_k` est écrite `return (c / m) ** k`. Que donne-t-elle pour 7 réussites sur 10 et k = 3, et dans quel sens se trompe-t-elle en moyenne ? (Indice : la fonction x ↦ x³ est convexe.)

## Pour aller plus loin

RAGAS propose deux variantes d'Agent Goal Accuracy : avec référence, où un juge LLM compare le résultat de la conversation à un résultat attendu, et sans référence, où le juge déduit lui-même l'objectif de la conversation, ce qui demande de mesurer le juge contre des humains (étape 13 bis). Quand les tâches sont coûteuses, des tests séquentiels permettent d'arrêter l'évaluation dès que la décision est acquise, au lieu de fixer n à l'avance ; et une approche bayésienne, avec une loi bêta sur le taux de réussite, donne directement la probabilité que le taux dépasse le seuil. Enfin, l'échantillonnage stratifié par catégorie de tâches évite qu'une catégorie rare, mais critique, soit sous-représentée dans le jeu.

> Suite : [Loi bêta et petits échantillons](<60b-Loi-Beta-et-Petits-Echantillons.md>) — étape 60 bis.
