# Étape 72 ter — Production — Décodage spéculatif

**Dossier :** 12-Production-Couts-Optimisation

> Étape 72 ter du parcours · Prérequis : [Batching continu et PagedAttention](<72b-Batching-Continu-et-PagedAttention.md>) · Suite : [Observabilité : traces, coûts et dérive](<72d-Observabilite-Traces-Couts-et-Derive.md>)

## Définition

Le décodage spéculatif accélère la génération sans changer ce que le modèle produit. Un petit **modèle brouillon**, rapide, propose γ tokens d'avance ; le **modèle cible**, celui dont on veut la réponse, les vérifie tous en une seule passe. Chaque token proposé x est accepté avec la probabilité min(1, p(x)/q(x)), où p est la loi du modèle cible et q celle du brouillon. Au premier rejet, on tire un nouveau token dans la loi normalisée de max(0, p − q), et la passe s'arrête ; si tous les tokens sont acceptés, la passe du modèle cible fournit en prime un token de plus. Le résultat est démontrable : la suite produite suit **exactement** la loi du modèle cible, et l'on obtient en moyenne plusieurs tokens par passe du modèle cible au lieu d'un seul. La variante gloutonne, où l'on garde les tokens tant que le brouillon a deviné l'argmax du cible, produit exactement la sortie gloutonne du modèle cible.

## Rôle dans un agent

Dans la boucle percevoir → décider → agir → observer, l'étape « décider » dure à peu près un pas de décodage par token de sortie (étape 33 bis), et ce pas est limité par la lecture des poids en mémoire, pas par le calcul. Vérifier γ + 1 tokens en une passe coûte donc presque autant que d'en produire un seul : c'est l'espace que le décodage spéculatif occupe. Un agent s'y prête particulièrement bien, parce qu'une grande partie de ce qu'il écrit est prévisible : des arguments JSON aux clés répétées, du code, des documents qu'il recopie en grande partie en les modifiant. Le brouillon devine juste plus souvent, et le gain grandit. La propriété d'exactitude compte autant que la vitesse : changer la méthode de décodage ne change pas la loi des sorties, si bien que les évaluations de l'agent (étapes 50 à 65) restent valables. Ce fichier sert à celui qui héberge son modèle, pour régler γ et décider quand activer la spéculation ; celui qui passe par une API n'a rien à régler, mais il comprend pourquoi le débit observé peut dépendre de la nature du texte.

## Équation complète

Probabilité d'accepter le token x proposé par le brouillon :

$$
\Pr(\text{accepter } x) = \min\!\left(1,\; \frac{p(x)}{q(x)}\right)
$$

Loi du nouveau tirage après un rejet (le résidu) :

$$
r(x) = \frac{\max\bigl(0,\; p(x) - q(x)\bigr)}{\sum_{y} \max\bigl(0,\; p(y) - q(y)\bigr)}
$$

Loi du token émis, qui est exactement p :

$$
\Pr(\text{sortie} = x) = q(x)\,\min\!\left(1, \frac{p(x)}{q(x)}\right) + (1 - \beta)\, r(x) = p(x)
$$

Probabilité d'acceptation à une position, et taux d'acceptation moyen sur les contextes :

$$
\beta = \sum_{x} \min\bigl(p(x), q(x)\bigr) = 1 - \mathrm{TV}(p, q), \qquad \mathrm{TV}(p,q) = \frac{1}{2} \sum_{x} \bigl\lvert p(x) - q(x) \bigr\rvert
$$

$$
\alpha = \mathbb{E}_{\text{contexte}}\bigl[\beta\bigr]
$$

Nombre moyen de tokens émis par passe du modèle cible :

$$
\mathbb{E}[N] = \sum_{i=0}^{\gamma} \alpha^{i} = \frac{1 - \alpha^{\gamma+1}}{1 - \alpha}
$$

Accélération par rapport au décodage classique, quand un pas du brouillon coûte c fois une passe du cible :

$$
S(\alpha, \gamma, c) = \frac{\mathbb{E}[N]}{\gamma\, c + 1} = \frac{1 - \alpha^{\gamma+1}}{(1 - \alpha)(\gamma\, c + 1)}
$$

Condition de gain, et positions évaluées par le modèle cible pour chaque token produit :

$$
\exists\, \gamma \ge 1 \;:\; S(\alpha, \gamma, c) > 1 \iff \alpha > c
$$

$$
W_{\text{cible}} = \frac{\gamma + 1}{\mathbb{E}[N]} \ge 1
$$

Variante gloutonne : on garde le token proposé xᵢ tant qu'il est l'argmax du cible :

$$
\text{accepter } x_i \iff x_i = \arg\max_{y}\, p(y \mid \text{préfixe})
$$

## Décryptage des symboles

$$
p
$$

**Sens :** loi du prochain token selon le modèle cible, réglages d'échantillonnage compris (température, top-p), sachant le préfixe · **Type / plage :** distribution sur le vocabulaire · **Variable Python :** `p(contexte)`, par exemple `p_bigrammes`

$$
q
$$

**Sens :** loi du prochain token selon le brouillon, sur le même vocabulaire · **Type / plage :** distribution sur le vocabulaire · **Variable Python :** `q(contexte)`

$$
x
$$

**Sens :** un token proposé par le brouillon · **Type / plage :** indice dans le vocabulaire · **Variable Python :** `x`

$$
\gamma
$$

**Sens :** nombre de tokens proposés par passe ; on garde la notation de l'article d'origine, sans lien avec le facteur d'actualisation de l'étape 38 · **Type / plage :** entier ≥ 1 · **Variable Python :** `gamma`

$$
\beta
$$

**Sens :** probabilité d'accepter le token proposé à une position donnée · **Type / plage :** réel dans [0 ; 1] · **Variable Python :** `beta(p, q)`

$$
\mathrm{TV}(p, q)
$$

**Sens :** distance en variation totale entre p et q : la plus grande différence de probabilité qu'ils peuvent donner à un même ensemble de tokens · **Type / plage :** réel dans [0 ; 1] · **Variable Python :** `variation_totale(p, q)`

$$
r
$$

**Sens :** le résidu : la loi du nouveau tirage après un rejet, qui ne garde que là où le cible dépasse le brouillon · **Type / plage :** distribution · **Variable Python :** `residu(p, q)`

$$
\alpha
$$

**Sens :** taux d'acceptation moyen, sur les contextes rencontrés ; on garde la notation de l'article d'origine, sans lien avec le poids du score hybride de l'étape 23 · **Type / plage :** réel dans [0 ; 1] · **Variable Python :** `alpha`, `alpha_mesure`

$$
N
$$

**Sens :** nombre de tokens émis par une passe du modèle cible · **Type / plage :** entier de 1 à γ + 1 · **Variable Python :** `len(bloc)`

$$
c
$$

**Sens :** coût d'un pas du brouillon, en fraction du coût d'une passe du cible · **Type / plage :** réel ≥ 0 · **Variable Python :** `c`

$$
S
$$

**Sens :** accélération : tokens produits par unité de temps, rapportés au décodage classique · **Type / plage :** réel > 0 · **Variable Python :** `acceleration(alpha, gamma, c)`, `s_mesuree`

$$
W_{\text{cible}}
$$

**Sens :** positions que le modèle cible évalue pour chaque token produit, au lieu d'une seule · **Type / plage :** réel dans [1 ; γ + 1] · **Variable Python :** `travail`

## Démonstration

### 1. La loi de sortie est exactement p

On fixe une position et son préfixe. Deux événements disjoints mènent à la sortie x.

- **Le brouillon propose x et il est accepté.** Probabilité q(x) × min(1, p(x)/q(x)). Si q(x) > 0, ce produit vaut min(q(x), p(x)) : quand p(x) ≥ q(x), le minimum vaut 1 et il reste q(x) ; sinon il reste q(x) × p(x)/q(x) = p(x). Si q(x) = 0, le brouillon ne propose jamais x, et le terme vaut 0 = min(q(x), p(x)).
- **Le brouillon propose autre chose, qui est rejeté, et le nouveau tirage donne x.** La probabilité de rejet vaut 1 moins la probabilité d'acceptation, soit 1 − Σ min(p, q) = 1 − β ; le nouveau tirage donne x avec la probabilité r(x).

Or max(0, p(x) − q(x)) = p(x) − min(p(x), q(x)), parce que si p(x) ≥ q(x) les deux côtés valent p(x) − q(x), et sinon ils valent 0. En sommant sur x, le dénominateur du résidu vaut Σ p − Σ min(p, q) = 1 − β. Le second terme vaut donc exactement max(0, p(x) − q(x)), et

$$
\Pr(\text{sortie} = x) = \min\bigl(p(x), q(x)\bigr) + \max\bigl(0,\, p(x) - q(x)\bigr) = p(x)
$$

parce que le minimum et le dépassement recomposent p(x). Si β = 1, alors min(p, q) = p partout, donc p = q : aucun rejet ne se produit, et le résidu, qui ne serait pas défini, ne sert jamais. Le programme refait ce calcul en fractions exactes et obtient p au bit près.

**Contre-exemple : rééchantillonner dans p au lieu du résidu.** La variante « en cas de rejet, on tire dans p » paraît naturelle. Elle donne min(p, q) + (1 − β) p, qui n'est pas p : sur l'exemple du point 8, la probabilité du premier token tombe de 1/2 à 3/8, et la loi devient [3/8 ; 5/16 ; 5/32 ; 5/32]. La sortie penche vers les préférences du brouillon, parce que les tokens que q sur-représente ont été acceptés une fois de trop. Le résidu corrige exactement ce surplus.

### 2. La probabilité d'acceptation vaut 1 − TV(p, q)

Pour deux réels a et b, min(a, b) = (a + b − |a − b|)/2. En sommant sur le vocabulaire, et parce que p et q somment chacune à 1 :

$$
\beta = \sum_{x} \min\bigl(p(x), q(x)\bigr) = \frac{1 + 1 - \sum_{x} \lvert p(x) - q(x) \rvert}{2} = 1 - \mathrm{TV}(p, q)
$$

Un brouillon proche du cible, en variation totale, est donc un brouillon souvent accepté. Sur l'exemple, TV = (1/4 + 1/4)/2 = 1/4 et β = 3/4.

### 3. Une suite entière suit la loi du modèle cible

Le point 1 vaut pour une position. Pour une suite, on raisonne token par token. Quand la passe en arrive à la position i, tous les tokens proposés avant elle ont été acceptés : le préfixe émis est exactement celui sur lequel le brouillon a conditionné sa proposition, et le cible calcule p au même préfixe. Le token émis en position i est alors soit une proposition acceptée ou corrigée, de loi p(· | préfixe) par le point 1, soit le token bonus, tiré directement dans p(· | préfixe). Dans tous les cas, sachant le préfixe, le token suivant suit p(· | préfixe). La loi d'une suite étant le produit de ces lois conditionnelles, elle est celle du modèle cible. Le programme le vérifie sans échantillonner : il énumère toutes les issues de toutes les passes pour deux modèles de bigrammes jouets, γ = 2, et obtient en fractions exactes la même loi que le cible sur les 64 suites de trois tokens ; par exemple P(« le loyer AED ») = 1/2 × 5/8 × 1/2 = 5/32 dans les deux cas.

### 4. Le nombre moyen de tokens par passe

Une passe émet N tokens, entre 1 et γ + 1 : les propositions acceptées avant le premier rejet, plus la correction, ou bien les γ propositions plus le bonus. On suppose que chaque proposition est acceptée avec la probabilité α, indépendamment des autres. C'est exact quand p et q ne dépendent pas du contexte, comme dans l'exemple, et c'est une approximation sinon. Pour 0 ≤ i ≤ γ, N ≥ i + 1 exactement quand les i premières propositions sont acceptées, donc P(N ≥ i + 1) = αⁱ. Comme N est un entier positif, N = Σₖ 𝟙{N ≥ k}, et en prenant l'espérance, E[N] = Σₖ P(N ≥ k). D'où

$$
\mathbb{E}[N] = \sum_{i=0}^{\gamma} P(N \ge i+1) = \sum_{i=0}^{\gamma} \alpha^{i} = \frac{1 - \alpha^{\gamma+1}}{1 - \alpha}
$$

par la somme géométrique déjà rencontrée à l'étape 11. On vérifie les cas limites : α = 0 donne 1 token par passe, jamais moins que le décodage classique ; α → 1 donne γ + 1. Avec α = 3/4, l'énumération exacte du programme donne 7/4 pour γ = 1, 175/64 pour γ = 3 et 3 367/1 024 pour γ = 5, les valeurs de la formule, et retrouve P(N ≥ i + 1) = (3/4)ⁱ terme à terme.

### 5. L'accélération et la condition de gain

Une passe du cible coûte environ le même temps T, qu'elle évalue 1 position ou γ + 1, parce que le décodage est limité par la lecture des poids (étape 33 bis). Un pas du brouillon coûte cT. Une itération dure donc (γc + 1)T et produit E[N] tokens en moyenne, alors que le décodage classique produit un token par T. D'où S = E[N]/(γc + 1).

**La spéculation ne peut gagner que si α > c.** Si α ≤ c, chaque terme αⁱ avec i ≥ 1 est au plus α, parce que 0 ≤ α ≤ 1, donc

$$
\sum_{i=0}^{\gamma} \alpha^{i} \le 1 + \gamma\, \alpha \le 1 + \gamma\, c \quad\Longrightarrow\quad S \le 1
$$

pour tout γ. Si au contraire α > c, γ = 1 suffit : S = (1 + α)/(1 + c) > 1. Le meilleur γ croît avec α et décroît avec c, parce qu'un γ trop grand fait payer au brouillon des propositions qui seront rejetées. Le tableau du programme le montre : pour c = 0,05, le meilleur γ vaut 3 (S = 1,63) à α = 0,5, 6 (S = 2,35) à α = 0,7, 8 (S = 3,09) à α = 0,8 et 13 (S = 4,67) à α = 0,9 ; pour c = 0,2 et α = 0,5, il vaut 1, et l'on ne gagne que 1,25.

### 6. Le prix : du calcul en plus pour le modèle cible

Chaque passe fait évaluer γ + 1 positions au modèle cible, pour E[N] tokens gardés : W_cible = (γ + 1)/E[N], qui vaut au moins 1 puisque E[N] ≤ γ + 1. Avec α = 0,75 et γ = 4, la formule donne 5/3,0508 = 1,639 positions par token, et la simulation mesure 1,642 : 64 % de calcul en plus pour le cible, sans compter celui du brouillon. Ce surplus ne coûte presque rien tant que la carte est limitée par la mémoire, c'est-à-dire avec un petit lot. Avec un grand lot (étape 72 bis), la carte devient limitée par le calcul, et les positions rejetées prennent la place de tokens utiles d'autres séquences : le débit total peut baisser. La spéculation est un outil de latence, à régler selon la charge.

### 7. La variante gloutonne, et le brouillon par copie

En décodage glouton, le cible prend toujours son argmax : sa loi est une masse 1 sur un token b, et l'on peut faire proposer au brouillon son propre argmax a. La règle générale donne alors min(1, p(a)/q(a)) = min(1, p(a)), qui vaut 1 si a = b et 0 sinon ; le résidu vaut 1 sur b. On garde donc les propositions tant qu'elles coïncident avec l'argmax du cible, et au premier désaccord on écrit l'argmax du cible : par récurrence sur les positions, la sortie est exactement la sortie gloutonne du cible. Le programme le vérifie sur 12 tokens, obtenus en 4 passes du cible au lieu de 12.

Le même calcul couvre un brouillon **déterministe**, comme la copie d'un passage du prompt (prompt lookup decoding) : q met une masse 1 sur le token proposé x. On l'accepte avec la probabilité min(1, p(x)) = p(x) ; en cas de rejet, le résidu vaut p(y)/(1 − p(x)) pour y ≠ x et 0 pour x. Un tel brouillon ne coûte presque rien (c ≈ 0), et il gagne beaucoup quand la sortie recopie l'entrée.

### 8. Exemple fait à la main (le code reprend ces nombres)

Vocabulaire de quatre tokens, lois sans contexte : p = [1/2 ; 1/4 ; 1/8 ; 1/8] et q = [1/4 ; 1/2 ; 1/8 ; 1/8].

- β = 1/4 + 1/4 + 1/8 + 1/8 = 3/4, et TV = (1/4 + 1/4 + 0 + 0)/2 = 1/4 : on a bien β = 1 − TV.
- Le dépassement max(0, p − q) vaut [1/4 ; 0 ; 0 ; 0], de masse 1/4 = 1 − β ; le résidu vaut donc [1 ; 0 ; 0 ; 0].
- Sortie du premier token : 1/4 × min(1, 2) + 1/4 × 1 = 1/2. Du deuxième : 1/2 × min(1, 1/2) = 1/4. Des deux derniers : 1/8 chacun. On retrouve p.
- Variante fautive : 1/4 + 1/4 × 1/2 = 3/8 pour le premier token, 1/4 + 1/16 = 5/16 pour le deuxième, 1/8 + 1/32 = 5/32 pour les deux derniers.
- Avec γ = 3 : E[N] = 1 + 3/4 + 9/16 + 27/64 = 175/64 ≈ 2,73. Avec γ = 4 et c = 0,05 : E[N] = (1 − (3/4)⁵)/(1/4) ≈ 3,0508 et S = 3,0508/1,2 ≈ 2,542.

## Effets et comportement

- **Un brouillon plus proche du cible accepte davantage.** α = 1 − TV en moyenne : un brouillon de la même famille, entraîné sur les mêmes données, ou une copie du prompt quand la sortie recopie l'entrée.
- **Le meilleur γ dépend de α et de c.** Il grandit quand le brouillon devine bien et coûte peu, et retombe à 1 quand le brouillon est cher ; quand α ≤ c, aucun γ ne fait gagner.
- **Le contenu change le gain.** Des clés JSON répétées, du code, un document recopié avec des retouches donnent un α élevé ; un texte créatif tiré à haute température en donne un plus faible.
- **La loi de sortie ne bouge pas, réglages compris.** La sortie suit la loi d'échantillonnage du cible, avec sa température et son top-p : la variété des textes reste la même.
- **Le gain fond quand la carte est pleine.** Avec de grands lots, le calcul supplémentaire W_cible − 1 n'est plus gratuit.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| p, q | `p_fixe`, `q_fixe`, `p_bigrammes`, `q_bigrammes` (fractions exactes) ; `p_fixe_flottant`, `q_fixe_flottant` (simulation) |
| β = Σ min(p, q), TV(p, q) | `beta(p, q)`, `variation_totale(p, q)` |
| résidu r | `residu(p, q)` |
| loi du token émis | `loi_un_token(p, q, apres_rejet)` |
| issues d'une passe, loi d'une suite | `issues_d_une_passe(contexte, gamma, p, q)`, `loi_speculative(...)`, `loi_cible(...)` |
| E[N], S | `tokens_par_passe(alpha, gamma)`, `acceleration(alpha, gamma, c)` |
| une passe tirée au hasard | `passe_speculative(contexte, gamma, p, q, rng, stats)` |
| décodage complet sur horloge simulée | `decoder_speculatif(n_tokens, gamma, p, q, c, graine)` |
| variante gloutonne | `glouton_cible(...)`, `glouton_speculatif(...)` |

### Déroulé, ligne par ligne

**Les lois.** `P_FIXE` et `Q_FIXE` sont les lois du point 8, en `Fraction`, pour que les égalités soient exactes. `P_BIGRAMMES` et `Q_BIGRAMMES` donnent la loi du token suivant selon le token précédent : après « . », le cible préfère « le » (1/2) et le brouillon « loyer » (1/2) ; après « le », le cible donne 5/8 à « loyer ». Les fonctions `p_fixe`, `p_bigrammes`… reçoivent le contexte, un tuple d'indices, et rendent la loi du token suivant ; c'est la même interface qu'un vrai modèle, qui lit tout le contexte.

**`beta(p, q)`** additionne `min(a, b)` : 3/4 sur l'exemple. **`variation_totale(p, q)`** renvoie la moitié de la somme des écarts absolus : 1/4.

**`residu(p, q)`** garde `max(a - b, 0)`, soit `[1/4, 0, 0, 0]`, et divise par la somme `z`. Si `z` vaut 0, alors p = q, aucun rejet n'est possible, et la fonction lève `ValueError` plutôt que de diviser par zéro.

**`loi_un_token(p, q, apres_rejet)`** écrit la formule du point 1 terme à terme : `qx * min(Fr(1), px / qx)` pour l'acceptation, puis `rejet * nouveau[x]`, où `nouveau` est le résidu, ou bien p dans la variante fautive. Elle renvoie `[1/2, 1/4, 1/8, 1/8]`, et `[3/8, 5/16, 5/32, 5/32]` pour la variante.

**`issues_d_une_passe(contexte, gamma, p, q)`** énumère tout ce qu'une passe peut émettre, avec sa probabilité exacte. La fonction interne `explorer` part du contexte ; pour chaque token x que le brouillon peut proposer, elle suit deux branches : x accepté, avec la probabilité `qx * accepte`, et l'on continue avec une proposition de moins ; x rejeté, avec la probabilité `qx * (1 - accepte)`, et l'on ajoute chaque correction y tirée dans le résidu. Quand il ne reste plus de proposition, elle ajoute le token bonus tiré dans p. Les propositions qui suivraient un rejet ne sont pas énumérées : elles ne changent rien à la sortie, et leurs probabilités somment à 1.

**`loi_speculative(contexte, longueur, gamma, p, q)`** enchaîne les passes : si un bloc émis atteint la longueur demandée, on le tronque ; sinon on relance l'énumération à partir du contexte prolongé et l'on multiplie les probabilités. **`loi_cible`** fait le produit des lois conditionnelles du cible, token par token. Le bloc 2 compare les deux dictionnaires.

**`tokens_par_passe(alpha, gamma)`** et **`acceleration(alpha, gamma, c)`** sont les formules fermées. `tokens_par_passe` traite à part α = 1, où la formule divise par zéro et où la passe émet toujours γ + 1 tokens.

**`tirer(loi, rng)`** tire un indice par la fonction de répartition inverse (étape 2), avec un générateur `random.Random(7)` à graine fixe.

**`passe_speculative(contexte, gamma, p, q, rng, stats)`** fait une vraie passe tirée au hasard : d'abord γ propositions du brouillon, chacune conditionnée sur les précédentes ; puis, pour chacune, `rng.random() < min(1.0, pc[x] / qc[x])` décide de l'acceptation. Au premier rejet, la fonction renvoie les tokens acceptés plus une correction tirée dans le résidu ; si tout passe, elle ajoute le bonus. `stats` compte les propositions évaluées et acceptées : leur rapport mesure α.

**`decoder_speculatif(n_tokens, gamma, p, q, c, graine)`** enchaîne les passes jusqu'à n_tokens, et avance l'horloge simulée de `gamma * c + 1` à chaque passe : γ pas du brouillon et une passe du cible. Le décodage classique coûterait 1 par token, si bien que `n / r["horloge"]` est l'accélération mesurée.

**`glouton_cible`** prend l'argmax du cible à chaque position. **`glouton_speculatif`** fait proposer au brouillon γ argmax, compte une passe du cible, puis écrit l'argmax du cible à chaque position tant qu'il coïncide avec la proposition ; au premier désaccord, il garde le choix du cible et sort de la boucle ; si tout coïncide, la clause `else` de la boucle `for` ajoute le token bonus.

**`main()`**, bloc par bloc.

1. Une position : β = 3/4 = 1 − 1/4, résidu `[1, 0, 0, 0]`, loi de sortie égale à p ; la variante fautive donne `[3/8, 5/16, 5/32, 5/32]` (points 1, 2 et 8).
2. Une suite : 64 suites de trois tokens, loi spéculative égale à la loi cible, P(« le loyer AED ») = 5/32 (point 3).
3. E[N] énuméré égal à 7/4, 175/64 et 3 367/1 024 pour γ = 1, 3 et 5, et P(N ≥ i + 1) = (3/4)ⁱ (point 4).
4. 20 000 tokens en 6 567 passes, soit 3,0455 tokens par passe pour 3,0508 prévus ; α mesuré 0,7485 ; fréquences à moins de 0,01 de p ; accélération 2,538 pour 2,542 prévus ; 1,642 position évaluée par token (points 4 à 6).
5. Le tableau des accélérations et les meilleurs γ, puis la condition α > c, vérifiée sur γ = 1 à 29 (point 5).
6. La variante gloutonne : 12 tokens identiques au cible, en 4 passes (point 7).

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`p_fixe(contexte)`** — Cette fonction est le modèle cible réduit à sa plus simple expression, un oracle qui donne toujours la même réponse quelle que soit la question : elle reçoit un contexte, tuple d'indices de tokens, l'ignore et renvoie la liste `P_FIXE` des probabilités exactes 1/2, 1/4, 1/8 et 1/8 pour « le », « loyer », « AED » et « . ». Elle a pourtant la même interface qu'un vrai modèle qui lit tout le contexte, ce qui permet de la passer à `issues_d_une_passe` pour énumérer exactement les issues d'une passe dans la section 3.

**`q_fixe(contexte)`** — Celle-ci est son pendant côté brouillon, le petit modèle rapide qui devine à la place du grand : elle reçoit elle aussi un contexte qu'elle ignore et renvoie `Q_FIXE`, soit 1/4, 1/2, 1/8 et 1/8, une loi qui surestime « loyer » et sous-estime « le » par rapport au cible. C'est cet écart qui fixe le taux d'acceptation β = 3/4 et le résidu concentré sur « le », et elle accompagne `p_fixe` dans toutes les énumérations exactes du programme.

**`p_fixe_flottant(contexte)`** — Cette fonction est la même loi cible que `p_fixe`, mais traduite en nombres à virgule flottante, comme une partition recopiée en gros caractères pour un musicien pressé : elle reçoit un contexte, l'ignore et renvoie `P_FIXE_F`, la liste 0,5 ; 0,25 ; 0,125 ; 0,125. Les fractions exactes seraient trop lentes pour tirer 20 000 tokens au hasard, si bien que c'est elle que `decoder_speculatif` reçoit dans la section 4, où les fréquences observées doivent tomber à moins de 0,01 de ces valeurs.

**`q_fixe_flottant(contexte)`** — Celle-ci est la version flottante du brouillon fixe : elle reçoit un contexte qu'elle ignore et renvoie `Q_FIXE_F`, soit 0,25 ; 0,5 ; 0,125 ; 0,125, les mêmes nombres que `Q_FIXE` en flottants. Elle sert de modèle brouillon à la simulation à graine de la section 4, où ses propositions sont acceptées ou rejetées par la règle min(1, p/q), et le taux d'acceptation mesuré, 0,7485, retrouve à moins de 0,01 près le β = 0,75 qu'imposent ces deux lois.

**`p_bigrammes(contexte)`** — Cette fonction donne au modèle cible un brin de mémoire, comme un lecteur qui devine le mot suivant d'après le seul mot qui précède : elle reçoit un contexte, en lit le dernier token et renvoie la ligne correspondante de `P_BIGRAMMES`, par exemple 1/2 pour « le » après une fin de phrase, et 5/8 pour « loyer » après « le ». Le contexte ne doit donc jamais être vide, d'où le point de départ `DEBUT` ; elle permet aux sections 2 et 6 de vérifier l'exactitude du décodage spéculatif sur des lois qui changent d'une position à l'autre.

**`q_bigrammes(contexte)`** — Celle-ci est le brouillon à mémoire courte qui accompagne `p_bigrammes` : elle reçoit un contexte, lit son dernier token et renvoie la ligne correspondante de `Q_BIGRAMMES`, une loi volontairement différente de celle du cible, puisqu'après une fin de phrase le brouillon préfère « loyer » avec la probabilité 1/2 là où le cible préfère « le ». Ces désaccords forcent des rejets et des corrections tirées dans le résidu, et c'est précisément ce qui rend probante l'égalité exacte des 64 suites de la section 2.

**`beta(p, q)`** — Cette fonction calcule la probabilité que le brouillon soit cru sur parole, comme un examinateur qui mesure le recouvrement entre deux copies : elle reçoit deux lois sur le même vocabulaire, additionne pour chaque token la plus petite de ses deux probabilités et renvoie cette somme β = Σ min(p, q), une fraction exacte quand les lois le sont. Pour les lois fixes du programme, elle rend 3/4, la probabilité qu'un token proposé par le brouillon soit accepté par le cible.

**`variation_totale(p, q)`** — Celle-ci mesure, à l'inverse, la distance entre les deux lois, comme un géomètre qui arpente la surface de terrain que l'une possède et que l'autre n'a pas : elle reçoit p et q, additionne les écarts absolus de leurs probabilités et renvoie la moitié de cette somme. Sur l'exemple, elle donne 1/4, et `main` vérifie l'identité β = 1 − TV(p, q), qui dit qu'on rejette exactement aussi souvent que les deux lois diffèrent.

**`residu(p, q)`** — Cette fonction prépare la loi de rattrapage qu'on utilise après un rejet, comme un correcteur qui ne garde que ce que le brouillon a oublié : elle reçoit p et q, retient pour chaque token l'excès max(p − q, 0), additionne ces excès et lève une `ValueError` si la somme est nulle, car p = q rend tout rejet impossible et le résidu indéfini. Elle renvoie sinon les excès divisés par leur somme ; pour les lois fixes, seul « le » est sous-estimé par le brouillon, et le résidu vaut 1, 0, 0, 0.

**`loi_un_token(p, q, apres_rejet)`** — Celle-ci calcule exactement la loi du token qui sort d'une position, en additionnant les deux chemins qui y mènent : elle reçoit p, q et le mode de rattrapage, « residu » par défaut, puis, pour chaque token, ajoute la probabilité d'être proposé par le brouillon et accepté, q(x) × min(1, p(x)/q(x)), à la probabilité d'un rejet multipliée par la loi de rattrapage, le résidu ou bien p dans la variante fautive. Elle renvoie la liste des probabilités : avec le résidu, on retrouve exactement p, soit 1/2, 1/4, 1/8, 1/8, tandis que la variante fautive donne 3/8, 5/16, 5/32, 5/32, une loi qui n'est plus celle du cible.

**`ajouter(bloc, proba)`** — Cette petite fonction interne, qui vit dans `issues_d_une_passe`, est le teneur de registre de l'énumération : elle reçoit un bloc de tokens émis, sous forme de tuple, et une probabilité exacte, puis ajoute cette probabilité à celle déjà inscrite pour ce bloc dans le dictionnaire `issues`, ou l'inscrit à partir de zéro. Elle ne renvoie rien ; comme plusieurs chemins distincts peuvent émettre le même bloc, par exemple un token accepté ou le même token tiré en correction, elle garantit que leurs probabilités s'additionnent au lieu de s'écraser.

**`explorer(ctx, emis, proba, restants)`** — Cette autre fonction interne de `issues_d_une_passe` est l'arpenteur qui parcourt tout l'arbre des possibles d'une passe : elle reçoit le contexte courant, les tokens déjà émis, la probabilité du chemin et le nombre de propositions restantes. Quand il n'en reste plus, elle inscrit chaque token bonus tiré dans p ; sinon, pour chaque token x que le brouillon peut proposer, elle descend d'un niveau dans la branche où x est accepté, avec la probabilité q(x) × min(1, p(x)/q(x)), et ferme la branche du rejet en inscrivant chaque correction tirée dans le résidu. Elle ne renvoie rien, tout passant par `ajouter`, et c'est grâce à elle que la section 3 retrouve exactement E[N] = 7/4, 175/64 et 3 367/1 024.

**`loi_cible(contexte, longueur, p)`** — Cette fonction est le témoin de référence, la loi qu'on obtiendrait sans aucune astuce en tirant les tokens un à un dans le grand modèle : elle reçoit un contexte, une longueur et la loi p, part de la suite vide de probabilité 1, puis, à chaque position, prolonge chaque suite par chaque token possible en multipliant sa probabilité par celle que p lui donne dans ce contexte. Elle renvoie le dictionnaire des suites et de leurs probabilités exactes ; pour trois tokens et les lois de bigrammes, il compte 64 suites, et « le loyer AED » y vaut 1/2 × 5/8 × 1/2 = 5/32, exactement comme dans `loi_speculative`.

**`tokens_par_passe(alpha, gamma)`** — Celle-ci est la formule fermée du rendement d'une passe, le nombre moyen de tokens qu'un passage du grand modèle laisse derrière lui : elle reçoit le taux d'acceptation α et le nombre de propositions γ, renvoie γ + 1 quand α vaut 1, cas où la formule diviserait par zéro et où tout est toujours accepté, et sinon 1 moins α à la puissance γ + 1, le tout divisé par 1 − α. Pour α = 3/4, elle donne 7/4, 175/64 et 3 367/1 024 pour γ = 1, 3 et 5, et 3,0508 pour γ = 4, la valeur que la simulation retrouve à 3,0455.

**`acceleration(alpha, gamma, c)`** — Cette fonction transforme ce rendement en gain de temps, comme un chef de chantier qui rapporte le travail accompli au temps de location des machines : elle reçoit α, γ et le coût relatif c d'un pas du brouillon, et renvoie E[N] divisé par γc + 1, le temps d'une passe mesuré en passes du cible. Avec α = 0,75, γ = 4 et c = 0,05, elle annonce 2,542 ; la section 5 s'en sert pour trouver le meilleur γ, 8 pour α = 0,8 et c = 0,05, et pour vérifier qu'aucun γ ne fait gagner quand α ≤ c.

**`tirer(loi, rng)`** — Celle-ci est la roue de loterie du programme, qui tire un indice selon une loi donnée par la méthode de la fonction de répartition inverse : elle reçoit une liste de probabilités et un générateur pseudo-aléatoire, tire un nombre u entre 0 et 1, cumule les probabilités et renvoie le premier indice où le cumul dépasse u. Si les arrondis empêchent le cumul d'atteindre u, elle renvoie par prudence le dernier indice de probabilité non nulle ; elle sert à tirer les propositions du brouillon, les corrections dans le résidu et le token bonus dans `passe_speculative`.

**`decoder_speculatif(n_tokens, gamma, p, q, c, graine)`** — Cette fonction fait tourner le décodeur complet sur une horloge simulée, comme un banc d'essai qui chronomètre une course entière : elle reçoit le nombre de tokens voulu, γ, les deux lois, le coût relatif c et une graine, puis enchaîne les appels à `passe_speculative` à partir du dernier token produit, compte les passes et avance l'horloge de γc + 1 à chaque passe. Elle renvoie un dictionnaire avec la sortie, le nombre de passes, l'horloge et les compteurs de propositions et d'acceptations ; avec γ = 4, c = 0,05 et la graine 7, elle produit 20 000 tokens en 6 567 passes, soit une accélération mesurée de 2,538 pour 2,542 prévus.

**`argmax(loi)`** — Celle-ci est l'électeur qui choisit toujours le candidat le plus probable : elle reçoit une liste de probabilités et renvoie l'indice de la plus grande, le premier en cas d'égalité puisque `max` garde le premier maximum rencontré. Elle est la brique des deux décodeurs gloutons, où le brouillon propose ses argmax et où le cible garde les siens, ce qui rend la sortie entièrement déterministe, sans graine ni tirage.

**`glouton_cible(contexte, n, p)`** — Cette fonction est la référence du décodage glouton, un rédacteur qui écrit toujours le mot le plus probable sans jamais hésiter : elle reçoit un contexte, un nombre de tokens n et la loi p, puis, n fois de suite, ajoute à la sortie l'argmax de p dans le contexte prolongé par ce qui a déjà été écrit. Elle renvoie le tuple des n tokens ; avec les lois de bigrammes, à partir d'une fin de phrase, elle écrit trois fois « le loyer AED . », la phrase que la variante spéculative doit reproduire à l'identique.

**`glouton_speculatif(contexte, n, gamma, p, q)`** — Celle-ci accélère le rédacteur glouton en lui donnant un assistant qui écrit à l'avance : elle reçoit un contexte, n, γ et les deux lois, puis, tant que la sortie est trop courte, fait proposer au brouillon γ argmax, compte une passe du cible et écrit l'argmax du cible à chaque position tant qu'il coïncide avec la proposition, garde le choix du cible au premier désaccord, et ajoute le token bonus quand tout coïncide. Elle renvoie la sortie tronquée à n tokens et le nombre de passes : pour 12 tokens avec γ = 3, la sortie est identique à celle de `glouton_cible`, en 4 passes au lieu de 12.

**`main()`** — C'est le vérificateur en chef qui fait passer au décodage spéculatif six épreuves : il montre d'abord, sur une position, que β = 3/4 = 1 − 1/4, que le résidu vaut 1, 0, 0, 0 et que la loi de sortie égale exactement p, contrairement à la variante fautive, puis il compare les 64 suites de trois tokens de la loi spéculative à la loi cible et retrouve E[N] par énumération pour γ = 1, 3 et 5. Il simule ensuite 20 000 tokens avec la graine 7, dresse le tableau des accélérations et des meilleurs γ, vérifie que rien ne se gagne quand α ≤ c, et termine par la variante gloutonne, identique au cible en 4 passes ; chaque égalité est verrouillée par un `assert`.

```python
"""Étape 72 ter — décodage spéculatif : règle d'acceptation, loi exacte, tokens par passe, accélération."""
import random
import sys
from fractions import Fraction as Fr

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

VOCAB = ["le", "loyer", "AED", "."]
DEBUT = (3,)   # le contexte de départ : une fin de phrase « . »

# Loi cible p et loi du brouillon q, sans contexte (même loi à chaque position)
P_FIXE = [Fr(1, 2), Fr(1, 4), Fr(1, 8), Fr(1, 8)]
Q_FIXE = [Fr(1, 4), Fr(1, 2), Fr(1, 8), Fr(1, 8)]

# Lois qui dépendent du token précédent (modèles de bigrammes jouets), ligne = token précédent
P_BIGRAMMES = {
    0: [Fr(1, 8), Fr(5, 8), Fr(1, 8), Fr(1, 8)],   # après « le »
    1: [Fr(1, 8), Fr(1, 8), Fr(1, 2), Fr(1, 4)],   # après « loyer »
    2: [Fr(1, 4), Fr(1, 8), Fr(1, 8), Fr(1, 2)],   # après « AED »
    3: [Fr(1, 2), Fr(1, 4), Fr(1, 8), Fr(1, 8)],   # après « . »
}
Q_BIGRAMMES = {
    0: [Fr(1, 4), Fr(1, 2), Fr(1, 8), Fr(1, 8)],
    1: [Fr(1, 8), Fr(1, 4), Fr(1, 2), Fr(1, 8)],
    2: [Fr(1, 8), Fr(1, 8), Fr(1, 4), Fr(1, 2)],
    3: [Fr(1, 4), Fr(1, 2), Fr(1, 8), Fr(1, 8)],
}


P_FIXE_F = [float(x) for x in P_FIXE]   # versions flottantes, pour la simulation rapide
Q_FIXE_F = [float(x) for x in Q_FIXE]


def p_fixe(contexte):
    return P_FIXE


def q_fixe(contexte):
    return Q_FIXE


def p_fixe_flottant(contexte):
    return P_FIXE_F


def q_fixe_flottant(contexte):
    return Q_FIXE_F


def p_bigrammes(contexte):
    return P_BIGRAMMES[contexte[-1]]


def q_bigrammes(contexte):
    return Q_BIGRAMMES[contexte[-1]]


# ---------------------------------------------------------------- une position
def beta(p: list, q: list) -> Fr:
    """Probabilité d'accepter le token proposé : β = Σ min(p, q)."""
    return sum(min(a, b) for a, b in zip(p, q))


def variation_totale(p: list, q: list) -> Fr:
    return sum(abs(a - b) for a, b in zip(p, q)) / 2


def residu(p: list, q: list) -> list:
    """Loi normalisée de max(0, p − q). Elle ne sert qu'après un rejet, donc quand p ≠ q."""
    m = [max(a - b, 0) for a, b in zip(p, q)]
    z = sum(m)
    if z == 0:
        raise ValueError("p = q : aucun rejet n'est possible, le résidu n'est pas défini")
    return [x / z for x in m]


def loi_un_token(p: list, q: list, apres_rejet: str = "residu") -> list:
    """Loi exacte du token émis : x ~ q, accepté avec min(1, p(x)/q(x)) ; sinon nouveau tirage."""
    rejet = 1 - beta(p, q)
    nouveau = residu(p, q) if apres_rejet == "residu" else list(p)
    return [(qx * min(Fr(1), px / qx) if qx else Fr(0)) + rejet * nouveau[x]
            for x, (px, qx) in enumerate(zip(p, q))]


# ---------------------------------------------------------------- une passe complète, en loi exacte
def issues_d_une_passe(contexte: tuple, gamma: int, p, q) -> dict:
    """Loi exacte des tokens émis par UNE passe du modèle cible : γ brouillons tirés selon q,
    acceptés un à un ; au premier rejet, un token tiré dans le résidu ; si tout passe, un token bonus tiré dans p."""
    issues: dict = {}

    def ajouter(bloc: tuple, proba: Fr) -> None:
        issues[bloc] = issues.get(bloc, Fr(0)) + proba

    def explorer(ctx: tuple, emis: tuple, proba: Fr, restants: int) -> None:
        pc = p(ctx)
        if restants == 0:
            for x, px in enumerate(pc):
                if px:
                    ajouter(emis + (x,), proba * px)
            return
        qc = q(ctx)
        for x, qx in enumerate(qc):
            if qx == 0:
                continue
            accepte = min(Fr(1), pc[x] / qx)
            if accepte > 0:
                explorer(ctx + (x,), emis + (x,), proba * qx * accepte, restants - 1)
            if accepte < 1:                    # rejet : correction, et la passe s'arrête
                for y, ry in enumerate(residu(pc, qc)):
                    if ry:
                        ajouter(emis + (y,), proba * qx * (1 - accepte) * ry)

    explorer(contexte, (), Fr(1), gamma)
    return issues


def loi_speculative(contexte: tuple, longueur: int, gamma: int, p, q) -> dict:
    """Loi exacte des `longueur` premiers tokens produits par le décodage spéculatif."""
    if longueur == 0:
        return {(): Fr(1)}
    loi: dict = {}
    for bloc, proba in issues_d_une_passe(contexte, gamma, p, q).items():
        if len(bloc) >= longueur:
            loi[bloc[:longueur]] = loi.get(bloc[:longueur], Fr(0)) + proba
        else:
            for suite, pr in loi_speculative(contexte + bloc, longueur - len(bloc), gamma, p, q).items():
                loi[bloc + suite] = loi.get(bloc + suite, Fr(0)) + proba * pr
    return loi


def loi_cible(contexte: tuple, longueur: int, p) -> dict:
    """Loi des `longueur` tokens tirés directement dans p, un par un."""
    loi = {(): Fr(1)}
    for _ in range(longueur):
        suivante: dict = {}
        for seq, proba in loi.items():
            for x, px in enumerate(p(contexte + seq)):
                if px:
                    suivante[seq + (x,)] = proba * px
        loi = suivante
    return loi


def tokens_par_passe(alpha, gamma: int):
    """E[N] = (1 − α^(γ+1)) / (1 − α), et γ + 1 si α = 1."""
    return gamma + 1 if alpha == 1 else (1 - alpha ** (gamma + 1)) / (1 - alpha)


def acceleration(alpha: float, gamma: int, c: float) -> float:
    """S = E[N] / (γ c + 1) : tokens par passe, rapportés au temps d'une passe (γ pas du brouillon + 1 passe cible)."""
    return tokens_par_passe(alpha, gamma) / (gamma * c + 1)


# ---------------------------------------------------------------- simulation avec graine et horloge simulée
def tirer(loi: list, rng: random.Random) -> int:
    u, cumul = rng.random(), 0.0
    for i, pr in enumerate(loi):
        cumul += float(pr)
        if u < cumul:
            return i
    return max(i for i, pr in enumerate(loi) if pr > 0)


def passe_speculative(contexte: tuple, gamma: int, p, q, rng: random.Random, stats: dict) -> tuple:
    """Une passe tirée au hasard : renvoie les tokens émis."""
    brouillons, ctx = [], contexte
    for _ in range(gamma):
        x = tirer(q(ctx), rng)
        brouillons.append(x)
        ctx = ctx + (x,)
    emis, ctx = (), contexte
    for x in brouillons:
        pc, qc = p(ctx), q(ctx)
        stats["proposes"] += 1
        if rng.random() < min(1.0, pc[x] / qc[x]):
            stats["acceptes"] += 1
            emis, ctx = emis + (x,), ctx + (x,)
        else:
            return emis + (tirer(residu(pc, qc), rng),)
    return emis + (tirer(p(ctx), rng),)


def decoder_speculatif(n_tokens: int, gamma: int, p, q, c: float, graine: int) -> dict:
    """Produit au moins n_tokens ; horloge : 1 par passe du modèle cible, c par pas du brouillon."""
    rng = random.Random(graine)
    stats = {"proposes": 0, "acceptes": 0}
    sortie, passes, horloge = [], 0, 0.0
    while len(sortie) < n_tokens:
        sortie.extend(passe_speculative(DEBUT + tuple(sortie[-1:]), gamma, p, q, rng, stats))
        passes += 1
        horloge += gamma * c + 1
    return {"sortie": sortie, "passes": passes, "horloge": horloge, **stats}


# ---------------------------------------------------------------- variante gloutonne
def argmax(loi: list) -> int:
    return max(range(len(loi)), key=lambda i: loi[i])


def glouton_cible(contexte: tuple, n: int, p) -> tuple:
    sortie = ()
    for _ in range(n):
        sortie += (argmax(p(contexte + sortie)),)
    return sortie


def glouton_speculatif(contexte: tuple, n: int, gamma: int, p, q) -> tuple[tuple, int]:
    """Le brouillon propose ses argmax ; le cible garde le plus long début qui coïncide avec ses propres argmax."""
    sortie, passes = (), 0
    while len(sortie) < n:
        ctx, brouillons = contexte + sortie, ()
        for _ in range(gamma):
            brouillons += (argmax(q(ctx + brouillons)),)
        passes += 1                                     # une passe cible évalue les γ + 1 positions
        for x in brouillons:
            choix = argmax(p(ctx))
            sortie, ctx = sortie + (choix,), ctx + (choix,)
            if choix != x:                              # désaccord : on garde le choix du cible et on s'arrête
                break
        else:
            sortie += (argmax(p(ctx)),)                 # tout est accepté : token bonus
    return sortie[:n], passes


def main() -> None:
    print("=== 1. Une position : la sortie suit exactement p ===")
    b, tv = beta(P_FIXE, Q_FIXE), variation_totale(P_FIXE, Q_FIXE)
    print(f"  p = {[str(x) for x in P_FIXE]}   q = {[str(x) for x in Q_FIXE]}")
    print(f"  β = Σ min(p, q) = {b} = 1 − TV(p, q) = 1 − {tv} ; résidu = {[str(x) for x in residu(P_FIXE, Q_FIXE)]}")
    loi = loi_un_token(P_FIXE, Q_FIXE)
    print(f"  loi de sortie = {[str(x) for x in loi]}")
    assert loi == P_FIXE and b == 1 - tv == Fr(3, 4)
    naif = loi_un_token(P_FIXE, Q_FIXE, apres_rejet="p")
    print(f"  variante fautive (nouveau tirage dans p) = {[str(x) for x in naif]}")
    assert naif == [Fr(3, 8), Fr(5, 16), Fr(5, 32), Fr(5, 32)] and sum(naif) == 1

    print("=== 2. Une séquence : loi exacte des 3 premiers tokens, γ = 2, lois de bigrammes ===")
    spec = {s: pr for s, pr in loi_speculative(DEBUT, 3, 2, p_bigrammes, q_bigrammes).items() if pr}
    cible = loi_cible(DEBUT, 3, p_bigrammes)
    print(f"  {len(spec)} suites possibles ; égalité exacte avec la loi cible : {spec == cible}")
    seq = (0, 1, 2)
    print(f"  P(« le loyer AED ») = {spec[seq]} = 1/2 × 5/8 × 1/2")
    assert spec == cible and spec[seq] == Fr(5, 32)

    print("=== 3. Tokens par passe : E[N] = (1 − α^(γ+1)) / (1 − α) ===")
    for gamma in (1, 3, 5):
        loi_n: dict = {}
        for bloc, proba in issues_d_une_passe(DEBUT, gamma, p_fixe, q_fixe).items():
            loi_n[len(bloc)] = loi_n.get(len(bloc), Fr(0)) + proba
        esperance = sum(n * pr for n, pr in loi_n.items())
        print(f"  γ = {gamma} : E[N] énuméré = {esperance} = {float(esperance):.6f} ; formule = {tokens_par_passe(Fr(3, 4), gamma)}")
        assert esperance == tokens_par_passe(Fr(3, 4), gamma)
        assert all(sum(pr for n, pr in loi_n.items() if n >= i + 1) == Fr(3, 4) ** i for i in range(gamma + 1))

    print("=== 4. Simulation avec graine : 20 000 tokens, γ = 4, c = 0.05 ===")
    r = decoder_speculatif(20_000, 4, p_fixe_flottant, q_fixe_flottant, c=0.05, graine=7)
    n = len(r["sortie"])
    freq = [r["sortie"].count(x) / n for x in range(4)]
    alpha_mesure = r["acceptes"] / r["proposes"]
    s_mesuree = n / r["horloge"]                       # le décodage classique coûte 1 par token
    print(f"  {n} tokens en {r['passes']} passes : {n / r['passes']:.4f} tokens par passe"
          f" (formule {float(tokens_par_passe(Fr(3, 4), 4)):.4f})")
    print(f"  taux d'acceptation mesuré = {alpha_mesure:.4f} ; fréquences = {[round(f, 4) for f in freq]}")
    print(f"  accélération mesurée = {s_mesuree:.3f} ; formule = {acceleration(0.75, 4, 0.05):.3f}")
    assert all(abs(f - float(px)) < 0.01 for f, px in zip(freq, P_FIXE)) and abs(alpha_mesure - 0.75) < 0.01
    assert abs(s_mesuree - acceleration(0.75, 4, 0.05)) < 0.05
    travail = 5 * r["passes"] / n
    print(f"  positions évaluées par le modèle cible par token produit = {travail:.3f} (au lieu de 1)")
    assert 1.5 < travail < 1.8

    print("=== 5. Accélération S(α, γ, c) et meilleur γ ===")
    gammas = (1, 2, 3, 4, 6, 8)
    print("  c     α    " + "".join(f"γ={g:<6d}" for g in gammas) + " meilleur γ (1 à 20)")
    meilleurs = {}
    for c in (0.05, 0.2):
        for alpha in (0.5, 0.7, 0.8, 0.9):
            ligne = "".join(f"{acceleration(alpha, g, c):<8.2f}" for g in gammas)
            g_opt = max(range(1, 21), key=lambda g: acceleration(alpha, g, c))
            meilleurs[(c, alpha)] = (g_opt, acceleration(alpha, g_opt, c))
            print(f"  {c:<5} {alpha:<4} {ligne} {g_opt:2d} (S = {acceleration(alpha, g_opt, c):.2f})")
    assert meilleurs[(0.05, 0.8)][0] == 8 and round(meilleurs[(0.05, 0.8)][1], 2) == 3.09
    assert meilleurs[(0.05, 0.9)][0] == 13 and meilleurs[(0.2, 0.5)][0] == 1
    for alpha, c in ((0.3, 0.3), (0.25, 0.4)):            # α ≤ c : aucun γ ne fait gagner
        assert all(acceleration(alpha, g, c) <= 1 for g in range(1, 30))
    assert acceleration(0.31, 1, 0.3) > 1                 # α > c : γ = 1 suffit à gagner

    print("=== 6. Variante gloutonne : la sortie est celle du modèle cible ===")
    cible_g = glouton_cible(DEBUT, 12, p_bigrammes)
    spec_g, passes = glouton_speculatif(DEBUT, 12, 3, p_bigrammes, q_bigrammes)
    print("  cible seul        :", " ".join(VOCAB[x] for x in cible_g))
    print("  spéculatif, γ = 3 :", " ".join(VOCAB[x] for x in spec_g), f"  ({passes} passes au lieu de 12)")
    assert spec_g == cible_g and passes == 4
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
=== 1. Une position : la sortie suit exactement p ===
  β = Σ min(p, q) = 3/4 = 1 − TV(p, q) = 1 − 1/4 ; résidu = ['1', '0', '0', '0']
  loi de sortie = ['1/2', '1/4', '1/8', '1/8']
  variante fautive (nouveau tirage dans p) = ['3/8', '5/16', '5/32', '5/32']
…
  64 suites possibles ; égalité exacte avec la loi cible : True
…
  γ = 3 : E[N] énuméré = 175/64 = 2.734375 ; formule = 175/64
…
  20000 tokens en 6567 passes : 3.0455 tokens par passe (formule 3.0508)
  taux d'acceptation mesuré = 0.7485 ; fréquences = [0.4968, 0.2533, 0.1236, 0.1263]
  accélération mesurée = 2.538 ; formule = 2.542
  positions évaluées par le modèle cible par token produit = 1.642 (au lieu de 1)
…
  0.05  0.8  1.71    2.22    2.57    2.80    3.04    3.09      8 (S = 3.09)
  0.2   0.5  1.25    1.25    1.17    1.08    0.90    0.77      1 (S = 1.25)
…
  spéculatif, γ = 3 : le loyer AED . le loyer AED . le loyer AED .   (4 passes au lieu de 12)
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : l'exactitude du décodage spéculatif n'est pas une affirmation à croire, c'est une égalité de fractions que l'on peut vérifier sur toutes les suites possibles. La vitesse, elle, dépend de deux nombres qu'on mesure en production : le taux d'acceptation α et le coût relatif c du brouillon.

### Avec une bibliothèque (extrait)

Les moteurs d'inférence ouverts proposent cette technique. Avec la bibliothèque `transformers` de Hugging Face, la génération dite « assistée » prend un modèle brouillon, ou une copie de passages du prompt ; les noms des paramètres ci-dessous viennent de la documentation du projet et doivent être vérifiés pour la version installée.

```python
# [extrait] — génération assistée avec Hugging Face transformers, non exécutée par le harnais
from transformers import AutoModelForCausalLM, AutoTokenizer

tok = AutoTokenizer.from_pretrained("<modèle cible>")
cible = AutoModelForCausalLM.from_pretrained("<modèle cible>")
brouillon = AutoModelForCausalLM.from_pretrained("<petit modèle de la même famille>")   # même tokenizer
entrees = tok("Résume ce contrat de bail :", return_tensors="pt")
sortie = cible.generate(**entrees, assistant_model=brouillon, max_new_tokens=300)      # brouillon par modèle
copie = cible.generate(**entrees, prompt_lookup_num_tokens=10, max_new_tokens=300)     # brouillon par copie du prompt
```

Le brouillon doit partager le vocabulaire du cible, puisque p et q doivent porter sur les mêmes tokens. Écrire soi-même `passe_speculative` reste utile : c'est la seule façon de mesurer α sur son propre trafic, de choisir γ avec la formule, et de vérifier qu'une implémentation garde la loi du cible.

## Squelette algorithmique

En entrée : un contexte, les deux modèles p et q, le nombre de propositions γ. En sortie : les tokens émis par une passe du cible ; la boucle extérieure enchaîne les passes. L'idée : proposer vite, vérifier en une fois, corriger au premier désaccord.

```text
ALGORITHME PasseSpéculative(contexte, γ)
SORTIE  : la liste des tokens émis (entre 1 et γ + 1)

  ctx ← contexte ; propositions ← liste vide
  POUR i DE 1 À γ FAIRE                                 (le brouillon, γ pas rapides)
      xᵢ ← tirer dans q(· | ctx) ; ajouter xᵢ à propositions ; ctx ← ctx + xᵢ
  FIN POUR
  calculer p(· | contexte + x₁ … xᵢ) pour i = 0 … γ, en UNE passe du cible
  émis ← liste vide ; ctx ← contexte
  POUR i DE 1 À γ FAIRE
      u ← nombre uniforme dans [0 ; 1[
      SI u < min(1, p(xᵢ | ctx) / q(xᵢ | ctx)) ALORS
          ajouter xᵢ à émis ; ctx ← ctx + xᵢ
      SINON
          y ← tirer dans r ∝ max(0, p(· | ctx) − q(· | ctx))
          ajouter y à émis
          RETOURNER émis                                (on jette les propositions suivantes)
      FIN SI
  FIN POUR
  ajouter un token tiré dans p(· | ctx) à émis          (le token bonus)
  RETOURNER émis

ALGORITHME DécodageSpéculatif(prompt, n, γ)
  sortie ← liste vide
  TANT QUE longueur(sortie) < n FAIRE
      émis ← PasseSpéculative(prompt + sortie, γ)
      ajouter émis à sortie ; retirer des caches KV les positions des propositions rejetées
  FIN TANT QUE
  RETOURNER sortie

VARIANTE Gloutonne : xᵢ ← argmax q ; accepter xᵢ si xᵢ = argmax p(· | ctx), sinon émettre argmax p et arrêter.
```

**Complexité :** une passe coûte γ pas du brouillon, soit γ c T, et une passe du cible sur γ + 1 positions, soit environ T tant que le décodage est limité par la mémoire ; la boucle d'acceptation est en O(γ), et chaque rejet coûte O(|V|) pour construire le résidu. La mémoire s'ajoute à celle du cible : les poids du brouillon et deux caches KV, dont on retire les positions rejetées à chaque passe. Pour n tokens, il faut en moyenne n / E[N] passes, d'où un temps proche de n (γc + 1) T / E[N] = n T / S. L'énumération exacte du programme, elle, explore jusqu'à |V|^γ branches par passe : elle sert à prouver, pas à produire.

**Du squelette au code :** `PasseSpéculative` est `passe_speculative`, avec `tirer` pour les tirages et `residu` pour la loi r ; la passe unique du cible n'est pas simulée, son coût est compté par `horloge += gamma * c + 1` dans `decoder_speculatif`, qui est `DécodageSpéculatif`. Le programme n'a pas de cache KV, d'où l'absence de la ligne de retrait des positions rejetées. La variante gloutonne est `glouton_speculatif`, comparée à `glouton_cible`. La version exacte de la passe, qui donne la loi de chaque issue au lieu de la tirer, est `issues_d_une_passe`.

## Cas d'usage réels aux Émirats

Les taux d'acceptation et les coûts relatifs du brouillon ci-dessous sont illustratifs : en production, on mesure α sur le trafic réel, par le rapport entre propositions acceptées et propositions évaluées, et c par le rapport des temps de passe des deux modèles.

### BTP — réviser un contrat de sous-traitance en recopiant presque tout

Un groupe de construction qui mène de grands chantiers à Dubaï fait produire par un agent, hébergé sur ses serveurs, la version révisée de contrats de sous-traitance d'environ 3 000 tokens : seules quelques clauses changent (retenue de garantie, pénalités de retard, TVA à 5 % sur les situations de travaux), et le reste est recopié. Le brouillon le plus efficace ici n'est pas un modèle, c'est la copie des passages du contrat d'origine (point 7) : son coût est négligeable, c ≈ 0, et sur un texte recopié son taux d'acceptation est élevé. Avec α = 0,9 et γ = 8, la formule donne E[N] = (1 − 0,9⁹)/0,1 ≈ 6,13 tokens par passe du cible, soit environ six fois moins de passes. L'équipe garde cette technique pour les révisions, et elle demande à l'agent, quand c'est possible, de produire seulement les modifications sous forme de diff (étape 49 bis), ce qui réduit encore les tokens de sortie. Comme le décodage spéculatif ne change pas la loi des sorties, la validation juridique faite sur l'agent reste valable. Sans cette accélération, chaque révision bloque l'ingénieur de chantier plusieurs dizaines de secondes. Les indicateurs suivis sont le taux d'acceptation mesuré par type de document et le temps de production d'une révision.

### Banque — des résumés KYC plus rapides, sans réévaluer le modèle

Une banque de détail de Dubaï héberge sur ses propres serveurs un grand modèle ouvert pour résumer les dossiers KYC, et dispose d'un petit modèle de la même famille, qui partage son vocabulaire, comme brouillon. Sur un échantillon de résumés, l'équipe mesure un taux d'acceptation de l'ordre de 0,7, et un pas du brouillon coûte environ 5 % d'une passe du cible (valeurs illustratives). Le tableau du point 5 donne alors γ = 6 et S ≈ 2,35 : la latence de génération est divisée par plus de deux. L'argument décisif pour l'équipe de gestion du risque de modèle est l'exactitude : la loi des sorties étant celle du modèle cible, le changement de méthode de décodage n'oblige pas à refaire l'évaluation de qualité, à condition de prouver que l'implémentation est correcte. La banque ajoute donc un test de non-régression en mode glouton, où la sortie spéculative doit être identique token pour token à la sortie du cible seul (point 7), et documente le changement dans son registre de modèles. Sans ce test, une erreur d'implémentation, comme un rééchantillonnage dans p au lieu du résidu, déformerait les résumés sans que personne ne le voie. Les indicateurs suivis sont le p95 de la latence des résumés et le taux d'identité en mode glouton, qui doit rester à 100 %.

### Crypto — couper la spéculation quand la carte sature

Une plateforme d'actifs virtuels agréée par la VARA héberge le modèle de son agent de support et de surveillance, avec le décodage spéculatif activé pour réduire la latence des réponses. Lors d'un mouvement brusque du marché, les requêtes affluent, les lots du batching continu se remplissent (étape 72 bis), et la carte passe d'un régime limité par la mémoire à un régime limité par le calcul. Le point 6 dit ce qui se passe alors : chaque token produit coûte W_cible = (γ + 1)/E[N] positions au cible, soit 1,64 avec α = 0,75 et γ = 4, et les positions rejetées prennent la place de tokens utiles d'autres clients. L'équipe règle donc la spéculation selon la charge : activée tant que l'occupation des lots reste basse, désactivée au-delà d'un seuil mesuré en recette, où le débit total compte plus que la latence de chaque réponse. Les alertes de surveillance gardent une file prioritaire dans les deux régimes. Sans ce réglage, la spéculation, faite pour accélérer, ralentit le service au moment du pic. Les indicateurs suivis sont le débit en tokens par seconde et par carte et le p95 de latence, par niveau de charge.

### Secteur public — un brouillon qui devine moins bien en arabe

Une entité de services publics en ligne, accessible par UAE Pass, sert un assistant bilingue arabe-anglais sur un modèle hébergé, avec un petit brouillon de la même famille. En mesurant α séparément par langue, l'équipe constate que le brouillon devine bien moins souvent en arabe qu'en anglais, parce qu'il a vu moins de textes arabes à l'entraînement. Avec, par exemple, α = 0,8 en anglais et α = 0,5 en arabe, et c = 0,05, le tableau du point 5 donne γ = 8 et S ≈ 3,09 en anglais, mais γ = 3 et S ≈ 1,63 en arabe : garder γ = 8 pour l'arabe ferait payer au brouillon des propositions presque toujours rejetées, et l'accélération tomberait à 1,43. L'équipe règle donc γ par langue, à partir du α mesuré chaque semaine, et envisage un brouillon mieux entraîné sur l'arabe pour rapprocher les deux expériences d'usagers. La qualité des réponses, elle, ne dépend pas de ce réglage, puisque la loi de sortie reste celle du cible dans les deux langues. Sans mesure par langue, la moyenne masque l'écart et les usagers arabophones attendent plus longtemps. Les indicateurs suivis sont α et le débit en tokens par seconde, par langue.

### Assurance — une extraction JSON gloutonne, identique au bit près

Un assureur auto et santé fait extraire par un agent les champs des déclarations de sinistre (date, lieu, véhicules, montant estimé, garages) dans un JSON au schéma fixe, en décodage glouton sur un modèle hébergé. Les clés du schéma, les guillemets et la ponctuation se répètent à chaque dossier : le brouillon les devine presque toujours, et seules les valeurs propres au dossier provoquent des rejets. La variante gloutonne garantit une sortie identique, token pour token, à celle du modèle cible seul (point 7) ; dans l'exemple du programme, 12 tokens sortent en 4 passes au lieu de 12. L'équipe s'appuie sur cette garantie pour ses tests : le jeu de non-régression compare les JSON octet par octet avant et après l'activation de la spéculation, et tout écart signale un défaut d'implémentation, par exemple un cache KV mal nettoyé après un rejet. L'assurance étant supervisée par la CBUAE, le changement est documenté avec le résultat de ces tests. Sans cette discipline, une différence d'un caractère dans un montant pourrait passer pour un caprice du modèle. Les indicateurs suivis sont le taux de JSON identiques sur le jeu de non-régression et la durée moyenne d'une extraction.

### Immobilier — des descriptions variées, dont la variété ne doit pas changer

Une agence et un promoteur actifs à Dubaï et Abu Dhabi font rédiger par un agent des descriptions de biens tirées à une température modérée, pour que 400 annonces d'une même tour ne se ressemblent pas. L'équipe active le décodage spéculatif pour réduire le temps de rédaction d'un lot d'annonces. Le risque n'est pas la vitesse, c'est la loi : un développeur a « simplifié » la correction en tirant dans p après un rejet, et le point 1 montre l'effet sur l'exemple, où la probabilité du token favori du cible tombe de 1/2 à 3/8 au profit des choix du brouillon. Les annonces glissent alors vers le style plus pauvre du petit modèle, sans erreur visible. L'équipe vérifie donc son implémentation comme le programme : sur des lois jouets, la loi de sortie doit être exactement p, et sur un échantillon réel, les fréquences des mots doivent rester celles du cible seul. Les prix en AED et en AED/sqft restent insérés par le code, jamais générés. Les indicateurs suivis sont la part de phrases distinctes sur un lot de 400 annonces, comparée à celle du cible seul, et le temps de rédaction par annonce.

## Pièges et limites

- **Rééchantillonner dans p après un rejet.** La loi de sortie penche alors vers le brouillon (3/8 au lieu de 1/2 dans l'exemple) ; il faut le résidu normalisé de max(0, p − q).
- **Oublier de retirer les positions rejetées des caches KV.** Les tokens suivants seraient calculés sur un contexte qui contient des propositions jetées ; la sortie se dégrade sans erreur visible.
- **Prendre un brouillon d'un autre vocabulaire.** p et q doivent porter sur les mêmes tokens ; sinon la règle d'acceptation n'a pas de sens.
- **Mesurer le gain à charge nulle seulement.** Avec de grands lots, la carte est limitée par le calcul, et W_cible − 1 positions par token ne sont plus gratuites.
- **Exiger l'égalité au bit près en échantillonnage.** La garantie porte sur la loi ; en flottants, la passe qui évalue γ + 1 positions d'un coup peut arrondir autrement qu'un décodage token par token (étape 33 bis), et un tirage proche d'un seuil peut basculer. On teste l'identité en mode glouton, et la loi sur des fréquences.

### Exercice feuille blanche

1. Sans regarder le code, écrire `residu` et `loi_un_token`, puis vérifier à la main et par le code que p = [0,6 ; 0,4] et q = [0,9 ; 0,1] donnent β = 0,7 et une loi de sortie égale à p. (Réponse : le résidu vaut [0 ; 1] ; le premier token sort avec 0,9 × 0,6/0,9 = 0,6, le second avec 0,1 + 0,3 × 1 = 0,4.)
2. Prédire, puis vérifier : avec α = 0,6 et c = 0,1, que valent E[N] et S pour γ = 3, et quel est le meilleur γ ? (Réponse : E[N] = (1 − 0,6⁴)/0,4 = 2,176 et S = 2,176/1,3 ≈ 1,674 ; le meilleur γ vaut 3.)
3. Trouver le bug : dans une variante de `passe_speculative`, la dernière ligne devient `return emis`, sans token bonus. La loi de sortie change-t-elle ? Que devient E[N] pour α = 0,75 et γ = 4 ? (Réponse : la loi reste p, puisque chaque token émis est une proposition acceptée ou une correction, de loi p par le point 1 ; mais E[N] tombe à Σ αⁱ pour i de 0 à γ − 1, soit 2,734 au lieu de 3,051 : on paie γ pas du brouillon pour le rendement de γ − 1.)

## Pour aller plus loin

La méthode a été publiée presque en même temps par Leviathan et al. (2023), qui annoncent une accélération de 2 à 3 fois sur T5-XXL avec des sorties identiques, et par Chen et al. (2023), qui annoncent 2 à 2,5 fois sur un modèle de 70 milliards de paramètres ; ce sont des résultats annoncés par les auteurs, à vérifier sur son propre matériel. Plusieurs variantes remplacent le brouillon séparé : des têtes de prédiction ajoutées au modèle cible (Medusa), un brouillon qui travaille sur les états internes du cible (EAGLE), ou un arbre de propositions vérifié en une passe au lieu d'une seule chaîne. L'inégalité de Pinsker relie le taux d'acceptation à la divergence de l'étape 50 : TV(p, q) ≤ √(KL(p‖q)/2), donc β ≥ 1 − √(KL(p‖q)/2), et un brouillon distillé pour réduire sa divergence au cible (étape 73 ter) est aussi un brouillon mieux accepté.

> Étape 72 ter du parcours · Prérequis : [Batching continu et PagedAttention](<72b-Batching-Continu-et-PagedAttention.md>) · Suite : [Observabilité : traces, coûts et dérive](<72d-Observabilite-Traces-Couts-et-Derive.md>)
