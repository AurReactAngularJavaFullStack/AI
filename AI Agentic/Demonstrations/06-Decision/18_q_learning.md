# 18 — Q-learning : démonstrations

> Fiche : [18 — Q-learning](<../../Images/06-Decision/18_q_learning.md>) · Image : `18_q_learning.jpg` · Leçon : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
Q(s, a) \leftarrow Q(s, a) + \alpha \left[ r + \gamma \max_{a'} Q(s', a') - Q(s, a) \right]
$$

Q(s, a) estime la valeur de jouer a dans l'état s. Après avoir joué a, reçu r et observé s′, on rapproche Q(s, a) de la « cible » r + γ max Q(s′, ·), d'un pas α ∈ ]0 ; 1]. Le crochet est l'erreur de différence temporelle (erreur TD) : l'écart entre ce que l'on vient d'observer et ce que l'on croyait.

## Les symboles, un par un

$$
Q(s, a)
$$

La valeur estimée de l'action a dans l'état s : la somme actualisée espérée des récompenses si l'on joue a puis au mieux ensuite ; même unité que les récompenses ; une case de la table `Q`, un dictionnaire indexé par le couple (état, action) dans le programme.

$$
s, \; a, \; s'
$$

L'état présent, l'action jouée et l'état observé ensuite ; des éléments d'ensembles finis ; les chaînes `"s0"`, `"s1"`, `"S0"`, `"S1"` et les noms d'actions des clés de `Q`.

$$
r
$$

La récompense reçue pendant la transition, en points ou en milliers d'AED selon le cas ; un réel ; l'argument `r` de `maj`.

$$
\gamma
$$

Le facteur d'actualisation, comme dans l'équation de Bellman (fiche 09) ; un réel de [0 ; 1[, ou 1 si chaque épisode se termine ; l'argument `gamma` de `maj` ; γ = 0 ramène le Q-learning à une simple moyenne de récompenses (cas 2).

$$
\max_{a'} Q(s', a')
$$

La meilleure valeur estimée dans l'état suivant, quelle que soit l'action que l'agent jouera réellement ; 0 si s′ est terminal ; l'argument `max_suivant` de `maj`.

$$
\alpha
$$

Le pas d'apprentissage : la fraction de l'erreur TD que l'on corrige ; un réel de ]0 ; 1] (le programme lève `ValueError` sinon) ; l'argument `alpha` de `maj`, constant ou égal à 1/n.

$$
c = r + \gamma \max_{a'} Q(s', a'), \qquad \delta = c - Q(s, a)
$$

La cible c et l'erreur TD δ ; même unité que Q ; δ > 0 veut dire « mieux que prévu », δ < 0 « moins bien » ; dans `maj`, c'est l'expression `r + gamma * max_suivant - q`.

$$
\leftarrow
$$

« Devient » : une mise à jour qui remplace l'ancienne valeur, pas une égalité ; dans le programme, l'affectation `Q[...] = maj(...)`.

$$
n
$$

Le nombre de mises à jour déjà faites sur une case : avec α = 1/n, la case est la moyenne de ses n cibles (démonstration 3) ; le compteur `n` du cas 4 et de la démonstration 3.

## Le mécanisme, avant les preuves

La formule reçoit une seule expérience, (s, a, r, s′), plus deux nombres réglés à l'avance, γ et α, et elle ne modifie qu'une case de la table. La première opération est le maximum sur les actions de s′ : on suppose que l'agent jouera au mieux ensuite, même s'il explore aujourd'hui, ce qui permet d'apprendre la meilleure politique en en suivant une autre. La deuxième multiplie ce maximum par γ, pour rapetisser l'avenir, et la troisième ajoute la récompense observée : on obtient la cible, une estimation de Q(s, a) fabriquée à partir d'une seule expérience et de la table elle-même. La quatrième opération soustrait l'ancienne valeur : l'erreur TD mesure la surprise. La cinquième multiplie cette surprise par α, et la dernière l'ajoute à l'ancienne valeur. On ne remplace pas directement Q par la cible, parce qu'une cible tirée d'une seule expérience est bruitée : avec α < 1, la case fait une moyenne de ses cibles successives (démonstrations 3 et 5). On n'attend pas non plus la fin de l'épisode pour connaître le vrai retour, parce que la table contient déjà un résumé de l'avenir, max Q(s′, ·) : c'est l'idée de Bellman, appliquée sans connaître les probabilités de transition. Le prix de ce raccourci est double : la cible dépend d'estimations encore fausses, qui se corrigent de proche en proche (cas 1), et le maximum d'estimations bruitées est trop optimiste (démonstration 6). Ce qui sort est la même table, avec une case un peu plus juste. Pour un développeur Java, c'est une mise à jour incrémentale de moyenne, comme un compteur `AtomicLong` de métriques qui tiendrait une moyenne mobile, sauf que la valeur ajoutée est elle-même lue dans la table.

**Petit film chiffré** (exemple simple : Q = 2, r = 1, max Q(s′, ·) = 5, γ = 0,9, α = 0,5).

| Opération | Valeur |
|---|---|
| max Q(s′, ·) | 5 |
| × γ | 0,9 × 5 = 4,5 |
| + r, la cible c | 1 + 4,5 = 5,5 |
| − Q, l'erreur TD δ | 5,5 − 2 = 3,5 |
| × α | 0,5 × 3,5 = 1,75 |
| + Q, la nouvelle valeur | 2 + 1,75 = 3,75 |

La case a fait la moitié du chemin vers la cible, parce que α = 0,5 : elle croit à moitié l'expérience nouvelle et à moitié ce qu'elle savait.

## Démonstration 1 — Une moyenne entre l'ancien et la cible

**Ce qu'on démontre.** Avec la cible c = r + γ max Q(s′, ·), la mise à jour est une moyenne pondérée de l'ancienne valeur et de la cible ; pour α ∈ ]0 ; 1], la nouvelle valeur est toujours entre les deux :

$$
Q + \alpha (c - Q) = (1 - \alpha)\, Q + \alpha\, c
$$

**L'idée.** Corriger une fraction α de l'écart revient à garder une fraction 1 − α de l'ancien et à prendre une fraction α du nouveau. Deux poids positifs de somme 1 donnent une moyenne, qui ne sort jamais de l'intervalle entre ses deux valeurs.

**La preuve, pas à pas.**

**Étape 1.** On développe α(c − Q) = αc − αQ, parce que la multiplication se distribue sur la soustraction.

**Étape 2.** On regroupe les termes en Q : Q − αQ = (1 − α)Q, d'où l'égalité annoncée.

**Étape 3.** Si α ∈ ]0 ; 1], les poids 1 − α et α sont ≥ 0 et de somme 1 ; si Q ≤ c, alors (1 − α)Q + αc ≥ (1 − α)Q + αQ = Q et ≤ (1 − α)c + αc = c, et de même si c ≤ Q. ∎

**Vérification chiffrée.** Exemple simple : 0,5 × 2 + 0,5 × 5,5 = 1 + 2,75 = 3,75, bien entre 2 et 5,5. α = 1 remplace tout par la cible (5,5), α petit ne bouge presque pas. **Contre-exemple avec α > 1 :** α = 1,5 donne 2 + 1,5 × 3,5 = 7,25, au-delà de la cible ; α = 2,5 donne 2 + 2,5 × 3,5 = 10,75, et l'écart passe de 3,5 à −5,25 : il grandit et change de signe à chaque mise à jour. C'est pourquoi `maj` lève `ValueError` hors de ]0 ; 1].

**Ce que la preuve révèle du mécanisme.** α est un curseur de confiance entre la mémoire (la case) et l'expérience (la cible). Comme le résultat reste entre les deux, une mise à jour ne peut jamais créer une valeur aberrante à partir de deux valeurs raisonnables.

**Conséquence pour un agent.** On valide α à la configuration (0 < α ≤ 1), et on borne aussi les récompenses : une cible aberrante, par exemple une récompense saisie en AED au lieu de milliers d'AED, serait recopiée à hauteur de α.

## Démonstration 2 — L'écart à une cible fixe est multiplié par (1 − α)

**Ce qu'on démontre.** Si la cible c ne change pas, après n mises à jour :

$$
Q_n - c = (1 - \alpha)^n \, (Q_0 - c)
$$

Pour diviser l'écart par K > 1, il faut et il suffit de n ≥ ln K / ln(1/(1 − α)) mises à jour.

**L'idée.** Chaque mise à jour garde une fraction 1 − α de l'écart (démonstration 1). Répéter n fois multiplie l'écart par (1 − α)ⁿ, une suite géométrique.

**La preuve, pas à pas.**

**Étape 1.** On soustrait c à la démonstration 1, parce qu'on s'intéresse à l'écart : (1 − α)Q + αc − c = (1 − α)Q − (1 − α)c = (1 − α)(Q − c).

**Étape 2.** Par récurrence sur n : si Qₙ − c = (1 − α)ⁿ(Q₀ − c), l'étape 1 donne Qₙ₊₁ − c = (1 − α)ⁿ⁺¹(Q₀ − c).

**Étape 3.** On veut (1 − α)ⁿ ≤ 1/K ; on prend le logarithme, croissant, puis on divise par ln(1 − α) < 0, ce qui inverse l'inégalité :

$$
n \ln(1 - \alpha) \le -\ln K \iff n \ge \frac{\ln K}{\ln \frac{1}{1 - \alpha}}
$$

∎

**Vérification chiffrée.** Exemple simple, cible 5,5 et α = 0,5 : les écarts valent 3,5 ; 1,75 ; 0,875 ; 0,4375 ; 0,21875, divisés par 2 à chaque fois, et Q vaut 3,75 ; 4,625 ; 5,0625 ; 5,28125. Pour diviser l'écart par 1 000 : n ≥ ln 1 000 / ln 2 ≈ 9,97, soit 10 mises à jour.

**Ce que la preuve révèle du mécanisme.** α règle la vitesse : α = 0,5 divise l'écart par 2 à chaque fois, α = 0,25 par 4/3 seulement. Mais cette démonstration suppose une cible fixe et sans bruit ; avec une cible bruitée, un grand α recopie aussi le bruit (démonstration 5).

**Conséquence pour un agent.** Le nombre d'essais nécessaires se calcule avant de lancer l'apprentissage : il dit si l'environnement fournira assez d'expériences pour que les valeurs soient utilisables.

## Démonstration 3 — Avec α = 1/n, Q est la moyenne des cibles vues

**Ce qu'on démontre.** Si la n-ième mise à jour d'une case utilise αₙ = 1/n, alors Qₙ est la moyenne arithmétique des n premières cibles, quel que soit Q₀. Avec un α constant, Qₙ est une moyenne mobile exponentielle, où la cible d'il y a k mises à jour pèse α(1 − α)ᵏ et la valeur de départ (1 − α)ⁿ.

**L'idée.** Le pas 1/n donne à la nouvelle cible exactement le poids qu'elle aurait dans une moyenne de n nombres. Le premier pas, α₁ = 1, efface la valeur de départ.

**La preuve, pas à pas.**

**Étape 1.** Pour n = 1, α₁ = 1 donne Q₁ = c₁ : la moyenne d'une seule cible, et Q₀ est oublié.

**Étape 2.** On suppose que Qₙ₋₁ est la moyenne des n − 1 premières cibles, donc (n − 1)Qₙ₋₁ est leur somme ; la démonstration 1 avec α = 1/n donne :

$$
Q_n = \left(1 - \frac{1}{n}\right) Q_{n-1} + \frac{1}{n} c_n = \frac{(n - 1)\, Q_{n-1} + c_n}{n}
$$

qui est la somme des n premières cibles divisée par n. Par récurrence, la propriété vaut pour tout n.

**Étape 3.** Avec α constant, on déroule la démonstration 1 : la cible reçue il y a k mises à jour a été multipliée par α le jour où elle est arrivée, puis par (1 − α) à chacune des k mises à jour suivantes, d'où le poids α(1 − α)ᵏ ; la valeur de départ a été multipliée n fois par (1 − α). ∎

**Vérification chiffrée.** Cibles 4, 6, 8 en partant de Q₀ = 123. Avec α = 1/n : Q₃ = (4 + 6 + 8)/3 = 6, et 123 a disparu. Avec α = 0,5 constant : Q₁ = 0,5 × 123 + 0,5 × 4 = 63,5 ; Q₂ = 0,5 × 63,5 + 0,5 × 6 = 34,75 ; Q₃ = 0,5 × 34,75 + 0,5 × 8 = 21,375. Les poids sont 0,5 pour 8, 0,25 pour 6, 0,125 pour 4 et encore 0,125 pour la valeur de départ (0,125 × 123 = 15,375 sur les 21,375).

**Ce que la preuve révèle du mécanisme.** α = 1/n oublie la valeur de départ et n'oublie jamais une cible : c'est la bonne moyenne d'un environnement stable. α constant oublie progressivement le passé : c'est la bonne moyenne d'un environnement qui change, au prix de garder un peu de la valeur de départ et beaucoup de bruit.

**Conséquence pour un agent.** Sur un historique figé (journaux d'une période stable), on prend α = 1/n par case (cas 2 et 4). En ligne, quand les coûts ou les comportements dérivent, on prend un α constant et petit, dont la mémoire effective est d'environ 1/α mises à jour.

## Démonstration 4 — Le point fixe est l'équation de Bellman d'optimalité

**Ce qu'on démontre.** La mise à jour ne change plus rien en moyenne quand l'erreur TD est nulle en espérance pour chaque couple (s, a), c'est-à-dire quand :

$$
Q(s, a) = \mathbb{E}\left[ r + \gamma \max_{a'} Q(s', a') \right]
$$

C'est l'équation de Bellman d'optimalité (fiche 09) écrite pour Q ; sa solution est unique et vaut Q*. La politique qui a produit les expériences n'apparaît pas dans cette équation : le Q-learning apprend Q* en suivant une autre politique, à condition que chaque couple (s, a) soit essayé assez souvent.

**L'idée.** Une moyenne qui ne bouge plus est égale à la moyenne de ce qu'on lui ajoute. Or ce qu'on lui ajoute est la cible de Bellman avec un maximum, qui ne dépend pas de l'action que l'agent jouera vraiment ensuite.

**La preuve, pas à pas.**

**Étape 1.** L'espérance de la variation est α 𝔼[δ] ; elle est nulle pour tout α > 0 si et seulement si 𝔼[r + γ max Q(s′, ·)] = Q(s, a), parce que Q(s, a) est un nombre fixé.

**Étape 2.** On écrit l'espérance avec les probabilités de transition P(s′ ∣ s, a), parce que r et s′ sont tirés par l'environnement : Q(s, a) = Σ P(s′ ∣ s, a) [R(s, a, s′) + γ max Q(s′, ·)], l'équation d'optimalité de la leçon.

**Étape 3.** L'opérateur de droite est une contraction de rapport γ (leçon, point 3) ; il a donc un point fixe unique, Q* (leçon, point 4).

**Étape 4.** Ni l'étape 1 ni l'étape 2 ne font intervenir la politique de collecte : elle décide seulement quels couples (s, a) sont mis à jour et combien de fois. Il faut donc que chaque couple soit visité, sinon sa case garde sa valeur de départ. ∎

**Vérification chiffrée.** Cas 1 au point fixe Q* = (1 ; 4,5 ; 5) : les trois erreurs TD valent 1 + 0 − 1 = 0, 0 + 0,9 × 5 − 4,5 = 0 et 5 − 5 = 0. Cas 4 : les journaux viennent d'une politique qui tire au hasard, et le Q-learning trouve pourtant 10,38 pour Q(S0, visite), proche de Q* = 10,4, alors que la moyenne des retours observés donne 7,43, proche de la valeur 7,3125 de la politique au hasard. **Contre-exemple sans couverture :** si les journaux du cas 4 ne contenaient jamais « offre » après une visite, Q(S1, offre) resterait à 0, le maximum vaudrait 5,5 (la relance), et Q(S0, visite) = −1 + 0,95 × 5,5 = 4,225 < 9 : l'agent renoncerait à tort aux visites.

**Ce que la preuve révèle du mécanisme.** Le maximum dans la cible est ce qui sépare le Q-learning d'une simple évaluation : il apprend la valeur de la meilleure politique, pas celle de la politique qui explore. Toute l'information sur l'environnement entre par les cibles ; la table n'a besoin d'aucun modèle de transition.

**Conséquence pour un agent.** On peut apprendre sur des journaux de production existants, sans expérimenter sur les clients, à condition de vérifier la couverture : chaque couple (s, a) utile doit apparaître un nombre minimal de fois dans les journaux, sinon on ne tire aucune conclusion sur lui.

## Démonstration 5 — Le bruit des cibles et le plancher de variance d'un α constant

**Ce qu'on démontre.** Si les cibles successives sont indépendantes, de même moyenne μ et de même variance σ², et si α est constant, la variance de Q tend vers une limite non nulle :

$$
\operatorname{Var}(Q_\infty) = \frac{\alpha\, \sigma^2}{2 - \alpha}
$$

Avec α = 1/n, la variance de Qₙ vaut σ²/n et tend vers 0.

**L'idée.** Chaque mise à jour réduit l'ancienne incertitude d'un facteur (1 − α)² et ajoute α² fois le bruit de la nouvelle cible. Les deux effets s'équilibrent à un niveau qui dépend de α : un pas grand apprend vite mais tremble beaucoup.

**La preuve, pas à pas.**

**Étape 1.** On écrit la démonstration 1 en écart à μ : Qₙ₊₁ − μ = (1 − α)(Qₙ − μ) + α(cₙ − μ).

**Étape 2.** Qₙ ne dépend que des cibles passées, donc il est indépendant de cₙ, et la variance d'une somme de termes indépendants est la somme des variances ; un facteur constant sort au carré :

$$
\operatorname{Var}(Q_{n+1}) = (1 - \alpha)^2 \operatorname{Var}(Q_n) + \alpha^2 \sigma^2
$$

**Étape 3.** La limite v vérifie v = (1 − α)²v + α²σ², donc v(1 − (1 − α)²) = α²σ², avec 1 − (1 − α)² = α(2 − α) ; on divise par α(2 − α) > 0 :

$$
v = \frac{\alpha^2 \sigma^2}{\alpha (2 - \alpha)} = \frac{\alpha\, \sigma^2}{2 - \alpha}
$$

**Étape 4.** La suite converge vers v parce que l'écart à v est multiplié par (1 − α)² < 1 à chaque pas (même raisonnement que la démonstration 2). Avec α = 1/n, Qₙ est la moyenne de n cibles indépendantes (démonstration 3), de variance σ²/n. ∎

**Vérification chiffrée.** La procédure rapide du cas 2 rapporte +3 avec la probabilité 0,9 et −20 avec 0,1 : μ = 2,7 − 2 = 0,7, 𝔼[r²] = 0,9 × 9 + 0,1 × 400 = 48,1, donc σ² = 48,1 − 0,49 = 47,61. Avec α = 0,5 : v = 0,5 × 47,61/1,5 = 15,87. Le programme simule 20 000 mises à jour (graine fixée) et mesure une variance de 16,15 et une moyenne de 0,654, conformes à la théorie. Avec α = 0,05 : v = 1,2208 (écart-type 1,105) ; avec α = 0,1 : v = 2,5058 (écart-type 1,583).

**Ce que la preuve révèle du mécanisme.** La démonstration 2 et celle-ci tirent α en sens opposés : la vitesse veut α grand, le bruit veut α petit. Le facteur α/(2 − α) vaut 1/3 à α = 0,5 et environ α/2 quand α est petit : diviser α par 10 divise à peu près le bruit par 10, mais multiplie le temps de convergence par environ 10.

**Conséquence pour un agent.** Quand l'écart entre deux actions est plus petit que l'écart-type du plancher, √(ασ²/(2 − α)), un agent à α constant change d'avis au gré du hasard. On choisit alors α = 1/n sur un historique stable, ou un α assez petit pour que le plancher soit nettement sous l'écart à détecter.

## Démonstration 6 — Le maximum d'estimations bruitées surestime

**Ce qu'on démontre.** Pour des estimations aléatoires X₁, …, Xₖ, l'espérance du maximum est au moins le maximum des espérances, et l'inégalité est stricte dès qu'il y a du bruit qui change l'ordre :

$$
\mathbb{E}\left[ \max(X_1, \dots, X_k) \right] \ge \max\big( \mathbb{E}[X_1], \dots, \mathbb{E}[X_k] \big)
$$

Pour k estimations indépendantes valant μ + σ ou μ − σ avec la probabilité 1/2, l'espérance du maximum vaut μ + σ(1 − 2 × 0,5ᵏ).

**L'idée.** Le maximum choisit, à chaque tirage, l'estimation qui a eu de la chance. En moyenne, il récolte donc la chance en plus de la vraie valeur.

**La preuve, pas à pas.**

**Étape 1.** Pour chaque tirage et chaque i, max(X₁, …, Xₖ) ≥ Xᵢ, par définition du maximum.

**Étape 2.** L'espérance conserve les inégalités (fiche 22, linéarité et positivité), donc 𝔼[max] ≥ 𝔼[Xᵢ] pour chaque i, et en particulier pour celui qui a la plus grande espérance.

**Étape 3.** Pour le modèle à deux points, le maximum vaut μ − σ seulement si les k estimations tirent toutes −σ, ce qui arrive avec la probabilité 0,5ᵏ ; sinon il vaut μ + σ. D'où 𝔼[max] = (μ + σ)(1 − 0,5ᵏ) + (μ − σ)0,5ᵏ = μ + σ(1 − 2 × 0,5ᵏ). ∎

**Vérification chiffrée.** Deux estimations d'une valeur vraie nulle, chacune ±1 : les quatre cas équiprobables donnent pour maximum 1, 1, 1 et −1, soit une espérance de 0,5 au lieu de 0. Cinq canaux de taux réel 0,2, estimés à ±0,1 : 1 − 2 × 0,5⁵ = 0,9375, donc 𝔼[max] = 0,2 + 0,1 × 0,9375 = 0,29375 (cas 3). **Contre-exemple sans bruit :** si σ = 0, chaque estimation vaut μ et le maximum aussi ; l'inégalité devient une égalité.

**Ce que la preuve révèle du mécanisme.** La cible du Q-learning contient justement un maximum d'estimations bruitées, max Q(s′, ·) : elle est biaisée vers le haut, et le biais remonte vers les états précédents par γ. Le biais grandit avec le nombre d'actions k et avec le bruit σ.

**Conséquence pour un agent.** Pour éviter de croire trop beau le meilleur choix, on sépare la sélection et l'évaluation : une moitié des données choisit l'action, l'autre moitié mesure sa valeur (c'est l'idée du double Q-learning). La même précaution s'applique quand un juge LLM bruité choisit le meilleur de k brouillons : le score du gagnant surestime sa qualité.

## Exemple simple, à la main

Estimation actuelle Q = 2, récompense r = 1, meilleure valeur suivante 5, γ = 0,9 et α = 0,5.

**Étape 1.** Cible : c = 1 + 0,9 × 5 = 1 + 4,5 = 5,5.

**Étape 2.** Erreur TD : δ = 5,5 − 2 = 3,5.

**Étape 3.** Nouvelle valeur : Q ← 2 + 0,5 × 3,5 = 2 + 1,75 = 3,75.

$$
c = 1 + 0{,}9 \times 5 = 5{,}5, \qquad Q \leftarrow 2 + 0{,}5 \times (5{,}5 - 2) = 3{,}75
$$

**Étape 4.** Avec la même cible, on recommence trois fois.

| Mise à jour | Q avant | Écart à 5,5 | Q après |
|---|---|---|---|
| 1 | 2 | 3,5 | 2 + 0,5 × 3,5 = 3,75 |
| 2 | 3,75 | 1,75 | 3,75 + 0,875 = 4,625 |
| 3 | 4,625 | 0,875 | 4,625 + 0,4375 = 5,0625 |
| 4 | 5,0625 | 0,4375 | 5,0625 + 0,21875 = 5,28125 |

L'écart à 5,5 est divisé par 2 à chaque fois (démonstration 2) : il vaut 0,21875 après quatre mises à jour.

## Cas d'usage complexes, démontrés

Les récompenses, probabilités et volumes des quatre cas sont illustratifs. Les tirages aléatoires du programme utilisent des graines fixées, pour que chaque nombre se retrouve à l'identique.

### Cas 1 — Groupe de construction [BTP] : apprendre à préférer le relevé de quantités au devis par barème

**Contexte.** Un groupe de construction à Dubaï répond chaque mois à environ 800 demandes de devis de travaux de second œuvre (volume illustratif). Pour chaque demande (état s0), son agent peut produire tout de suite un devis par barème (outil A, fin de l'épisode) ou lancer d'abord un relevé de quantités (outil B), qui mène à l'état s1 où un devis détaillé (action C) termine l'épisode. Le barème rapporte peu et provoque des litiges ; le relevé ne rapporte rien tout de suite. L'agent apprend les valeurs par Q-learning, en alternant A et B pendant 20 épisodes d'exploration.

**Données.**

- Récompenses : A, 1 point puis fin ; B, 0 point puis s1 ; C, 5 points puis fin ; 1 point ≈ 100 AED de marge, TVA 5 % comprise dans les devis.
- γ = 0,9 ; α = 0,5 ; toutes les valeurs partent de 0.
- Exploration : A aux épisodes impairs, B puis C aux épisodes pairs.
- Volume : 800 demandes par mois.

**Calcul pas à pas.**

**Étape 1.** Valeurs optimales attendues (fiche 09) : Q*(s0, A) = 1, Q*(s1, C) = 5, Q*(s0, B) = 0 + 0,9 × 5 = 4,5.

**Étape 2.** Épisodes 1 à 4 : Q(s0, A) passe à 0,5 puis 0,75. À l'épisode 2, Q(s0, B) = 0 + 0,5 × (0 + 0,9 × 0 − 0) = 0, car Q(s1, C) vaut encore 0, puis Q(s1, C) = 2,5. À l'épisode 4, Q(s0, B) = 0 + 0,5 × 0,9 × 2,5 = 1,125 et Q(s1, C) = 2,5 + 0,5 × 2,5 = 3,75.

**Étape 3.** Après 10 épisodes : 0,96875 ; 3,65625 ; 4,84375. Après 20 : 0,99902 ; 4,45166 ; 4,99512. Q(s0, B) est encore à 4,5 − 4,45166 = 0,04834 de sa cible, parce que sa cible dépend elle-même de Q(s1, C), qui converge en même temps.

**Étape 4.** Contrôle au point fixe (démonstration 4) : avec Q* = (1 ; 4,5 ; 5), les trois erreurs TD sont nulles.

**Décision de l'agent.** Dès l'épisode 4, Q(s0, B) = 1,125 dépasse Q(s0, A) = 0,75 : l'agent a compris que l'outil B, qui ne rapporte rien tout de suite, mène à mieux. À la fin de l'exploration, la politique gloutonne choisit B puis C pour chaque nouvelle demande.

**Contre-calcul.** Une règle qui ne regarde que la récompense immédiate choisit A (1 > 0) et perd 4,5 − 1 = 3,5 points par demande, soit 3,5 × 100 × 800 = 280 000 AED par mois (illustratif).

**Sensibilité.** Valeur de bascule sur γ : Q*(s0, B) = 5γ dépasse Q*(s0, A) = 1 dès que γ > 0,2 ; avec γ = 0,1, Q*(s0, B) = 0,5 < 1 et l'agent garderait le barème. Sur α : avec α = 0,25, B ne passe devant A qu'à l'épisode 6 au lieu de 4.

**En production.** Indicateur : l'erreur TD moyenne en valeur absolue par couple (s, a), sur les 100 dernières mises à jour ; alerte au-dessus de 0,5 point après convergence, signe que les coûts ou les marges ont changé. Contrainte : chaque devis porte la TVA de 5 %, calculée par un outil déterministe et non par l'agent.

### Cas 2 — Plateforme d'actifs virtuels agréée VARA [CRYPTO] : choisir la procédure de rééquilibrage du portefeuille chaud

**Contexte.** Une plateforme d'actifs virtuels agréée par la VARA rééquilibre chaque jour son portefeuille chaud à partir du stockage à froid, environ 900 opérations par mois (volume illustratif). Deux procédures existent : rapide (R), automatisée, et standard (S), avec double validation humaine. Un agent apprend la valeur de chacune par Q-learning avec γ = 0, puisque chaque opération est un épisode d'un seul pas. Question : quelle procédure, et quel pas α ?

**Données.**

- R : récompense +3 avec la probabilité 0,9 (rapide, sans friction), −20 avec 0,1 (incident à corriger).
- S : récompense +1, certaine.
- Pas configuré au départ : α = 0,5 ; 1 point ≈ 1 000 AED (poids de gravité fixé par l'équipe des risques).
- Volume : 900 opérations par mois.

**Calcul pas à pas.**

**Étape 1.** Moyennes vraies : 𝔼[R] = 0,9 × 3 + 0,1 × (−20) = 2,7 − 2 = 0,7 < 1 = 𝔼[S]. La procédure standard est meilleure de 0,3 point par opération.

**Étape 2.** Bruit de R (démonstration 5) : 𝔼[r²] = 48,1, σ² = 48,1 − 0,49 = 47,61, σ = 6,9.

**Étape 3.** Plancher de bruit de Q(R) avec α = 0,5 : √(0,5 × 47,61/1,5) = √15,87 ≈ 3,98, plus de treize fois l'écart de 0,3 à détecter. Une série de trois succès à partir de 0 suffit à faire croire R meilleur : 1,5 ; 2,25 ; 2,625 > 1.

**Étape 4.** Nombre d'observations pour séparer les deux moyennes à deux écarts-types avec α = 1/n : 2σ/√n ≤ 0,3, soit n ≥ (2 × 6,9/0,3)² = 46² = 2 116.

**Étape 5.** Simulation de 20 000 observations de R (graine fixée), en comptant après les 2 116 premières : Q(R) dépasse Q(S) = 1 pendant 72,4 % du temps avec α = 0,5, et jamais (0,000) avec α = 1/n, dont la moyenne finale vaut 0,706.

**Décision de l'agent.** L'agent garde la procédure standard S. Il n'apprend pas en ligne avec α = 0,5 : il estime Q(R) avec α = 1/n sur l'historique, et ne repasse à R que si le taux d'incident mesuré tombe sous la valeur de bascule.

**Contre-calcul.** Avec α = 0,5, un agent glouton choisirait R pendant 72,4 % du temps : 0,724 × 0,3 × 900 × 1 000 = 195 480 AED de valeur perdue par mois, et 0,724 × 900 × 0,1 = 65,2 incidents par mois.

**Sensibilité.** Valeur de bascule sur le taux d'incident q de R : 3(1 − q) − 20q = 1, soit 3 − 23q = 1 et q = 2/23 = 0,08696. Au-dessus de 8,7 % d'incidents, S gagne ; en dessous, R gagne.

**En production.** Indicateur : le taux d'incident de la procédure R sur une fenêtre glissante de plusieurs milliers d'opérations ; alerte s'il passe sous 0,09, pour réexaminer la décision près de la bascule 0,08696. Contrainte : la VARA attend des contrôles documentés sur la garde des actifs des clients (à confirmer avec le règlement en vigueur) ; tout changement de procédure est validé par un humain et journalisé avec les estimations utilisées.

### Cas 3 — Cabinet RH multi-émirats [RH] : ne pas croire le meilleur canal de recrutement trop beau

**Contexte.** Un cabinet RH présent dans plusieurs émirats doit pourvoir 40 postes pour un client. Son agent estime, par la règle du Q-learning avec γ = 0 et α = 1/n, le taux d'embauche Q(canal) de cinq canaux de sourcing à partir de 10 candidats par canal, puis planifie avec le meilleur canal, max Q. En réalité, les cinq canaux ont le même taux, 0,2, que l'agent ne connaît pas.

**Données.**

- 5 canaux, taux réel 0,2 chacun (inconnu de l'agent).
- Estimation sur 10 candidats par canal ; modèle simplifié du bruit : chaque estimation vaut 0,2 + 0,1 ou 0,2 − 0,1 avec la probabilité 1/2, indépendamment.
- 40 embauches à réaliser ; coût de sourcing : 150 AED par candidat (illustratif).

**Calcul pas à pas.**

**Étape 1.** Biais du maximum (démonstration 6) :

$$
\mathbb{E}\left[\max_{\text{canal}} Q\right] = 0{,}2 + 0{,}1 \times \left( 1 - 2 \times 0{,}5^5 \right) = 0{,}2 + 0{,}1 \times 0{,}9375 = 0{,}29375
$$

soit une surestimation de (0,29375 − 0,2)/0,2 = 46,9 %.

**Étape 2.** Plan de l'agent biaisé : 40/0,29375 = 136,17, arrondi à 137 candidats, pour un budget de 137 × 150 = 20 550 AED.

**Étape 3.** Résultat réel : 137 × 0,2 = 27,4 embauches, soit 40 − 27,4 = 12,6 postes non pourvus.

**Étape 4.** Double estimation : on choisit le canal sur 5 candidats et on mesure son taux sur les 5 autres ; la mesure est indépendante du choix, donc d'espérance 0,2. Plan : 40/0,2 = 200 candidats, budget 200 × 150 = 30 000 AED.

**Décision de l'agent.** L'agent planifie avec l'estimation séparée : 200 candidats et 30 000 AED, et il présente au client le taux 0,2, pas 0,29.

**Contre-calcul.** Le plan biaisé paraît économiser 30 000 − 20 550 = 9 450 AED, mais il manque 12,6 embauches : il faudra relancer 200 − 137 = 63 candidats (63 × 150 = 9 450 AED) et perdre un cycle de sourcing. Avec un modèle binomial exact du bruit (10 candidats, taux 0,2), le maximum des cinq estimations vaut même 0,3514 en moyenne : le modèle simplifié sous-estime le problème.

**Sensibilité.** Le biais grandit avec le nombre de canaux : 0,25 avec 2 canaux, 0,2998 avec 10. Il baisse avec la taille de l'échantillon : avec 20 candidats par canal, le bruit passe à 0,1/√2 ≈ 0,0707 et 𝔼[max] à 0,2663. Le biais dépasse donc 10 % du vrai taux (0,02) dès qu'on compare deux canaux.

**En production.** Indicateur : le rapport entre le taux d'embauche réalisé et le taux prévu, par canal et par campagne ; alerte sous 0,85. Contraintes : les contrats et permis de travail passent par le MOHRE, les objectifs d'Émiratisation du client sont à confirmer avec le texte en vigueur, et les données des candidats relèvent de la PDPL, sauf en zone DIFC ou ADGM, qui ont leurs propres lois.

### Cas 4 — Agence immobilière [IMMO] : apprendre sur des journaux sans répéter la politique qui les a produits

**Contexte.** Une agence de Dubaï et d'Abu Dhabi veut décider, pour chaque prospect contacté (état S0), s'il faut proposer une visite ou faire tout de suite une offre. Après une visite (état S1), on peut faire une offre ou relancer. Elle dispose de 20 000 épisodes journalisés produits par une ancienne règle qui tirait chaque choix à pile ou face. Volume illustratif : 300 prospects par mois ; montants en milliers d'AED (une vente rapporte 30, soit 2 % de 1 500 000 AED, illustratif).

**Données.**

- S0, visite : récompense −1 (coût de la visite), puis S1.
- S0, offre directe : vente avec la probabilité 0,3 (récompense 30), sinon 0 ; fin.
- S1, offre : vente avec la probabilité 0,4 (30) ; fin. S1, relance : coût 0,5 et vente avec la probabilité 0,2 (30) ; fin.
- γ = 0,95 ; journaux : politique 50/50 dans chaque état ; α = 1/n par case.
- Volume : 300 prospects par mois.

**Calcul pas à pas.**

**Étape 1.** Valeurs optimales en S1 : Q*(S1, offre) = 0,4 × 30 = 12 ; Q*(S1, relance) = −0,5 + 0,2 × 30 = 5,5.

**Étape 2.** Valeurs optimales en S0 :

$$
Q^{*}(S_0, \text{visite}) = -1 + 0{,}95 \times \max(12 ; 5{,}5) = -1 + 11{,}4 = 10{,}4, \qquad Q^{*}(S_0, \text{offre}) = 0{,}3 \times 30 = 9
$$

**Étape 3.** Valeur de l'ancienne règle au hasard : V(S1) = 0,5 × 12 + 0,5 × 5,5 = 8,75, donc Q(S0, visite) = −1 + 0,95 × 8,75 = 7,3125 sous cette règle.

**Étape 4.** Apprentissage sur les journaux (graine fixée, chaque case vue plus de 4 000 fois) : le Q-learning trouve Q(S0, visite) = 10,38, Q(S0, offre) = 9,10, Q(S1, offre) = 12,13 et Q(S1, relance) = 5,60 ; la moyenne des retours observés après une visite vaut 7,43.

**Décision de l'agent.** Le Q-learning compare 10,38 à 9,10 : l'agent propose une visite, puis une offre après la visite.

**Contre-calcul.** Une évaluation qui fait la moyenne des retours journalisés mesure la valeur de l'ancienne règle (7,43 contre 9,10) et choisit l'offre directe. Elle perd 10,4 − 9 = 1,4 millier d'AED par prospect, soit 1,4 × 1 000 × 300 = 420 000 AED par mois (illustratif).

**Sensibilité.** L'offre directe passerait devant si sa probabilité de vente dépassait 10,4/30 = 0,34667, ou si la visite coûtait plus de 11,4 − 9 = 2,4 milliers d'AED. Si l'offre après visite ne convertissait plus qu'à 0,36 (−10 %), Q*(S0, visite) = −1 + 0,95 × 10,8 = 9,26 > 9 : la décision tient.

**En production.** Indicateurs : la couverture des journaux (nombre d'occurrences de chaque couple état-action, alerte sous 1 000) et l'erreur TD moyenne sur les nouveaux épisodes. Contraintes : la publicité et les offres sur plan suivent les règles du DLD et de la RERA, et les messages commerciaux le consentement prévu par la PDPL (à confirmer avec le texte en vigueur) ; l'agent priorise le travail des négociateurs, il ne fait pas pression sur l'acheteur.

## Entraînement sur feuille A4

**Exercice 1.** Q = 0, r = 2, max Q(s′) = 10, γ = 0,8, α = 0,25. Calculer la nouvelle valeur.

**Exercice 2.** Même cible, α = 0,25. Combien de mises à jour pour que l'écart soit divisé par 10 ? (ln 10 ≈ 2,303, ln(1/0,75) ≈ 0,2877.)

**Exercice 3.** Avec α = 1/n, cibles successives 4, 6, 8 en partant de Q₀ quelconque. Que vaut Q₃ ?

**Exercice 4.** Avec α = 0,5 constant, quel poids a la cible d'il y a 3 mises à jour ?

**Exercice 5.** Dans le cas 1, quelle serait Q*(s₀, B) avec γ = 0,1 ? Quel outil serait alors préféré ?

**Exercice 6 (modifier une donnée).** Dans le cas 4, l'offre directe vend désormais avec la probabilité 0,36. Recalculer Q*(S0, offre) et donner la décision.

**Exercice 7 (trouver l'erreur).** Un collègue code la mise à jour ainsi : Q ← Q + α (r + γ max Q(s′, ·)). Sur l'exemple simple (Q = 2, r = 1, max 5, γ = 0,9, α = 0,5), calculer les trois premières mises à jour et expliquer ce qui ne va pas.

**Exercice 8 (redémontrer de mémoire).** Redémontrer la formule de la démonstration 5, ασ²/(2 − α), puis calculer le plancher de variance de Q(R) au cas 2 avec α = 0,1.

## Corrigé

**Exercice 1.** Cible 2 + 0,8 × 10 = 2 + 8 = 10, erreur TD 10 − 0 = 10, donc Q = 0 + 0,25 × 10 = 2,5.

**Exercice 2.** Démonstration 2 : 0,75ⁿ ≤ 0,1 ⟺ n ≥ 2,303/0,2877 ≈ 8,0. Comme 0,75⁸ ≈ 0,1001 est encore juste au-dessus de 0,1, il faut 9 mises à jour.

**Exercice 3.** Démonstration 3 : Q₃ est la moyenne, (4 + 6 + 8)/3 = 6. Le Q₀ est oublié dès la première mise à jour, car α₁ = 1.

**Exercice 4.** Démonstration 3 : α(1 − α)³ = 0,5 × 0,5³ = 0,5 × 0,125 = 0,0625.

**Exercice 5.** Q*(s₀, B) = 0 + 0,1 × 5 = 0,5 < Q*(s₀, A) = 1 : l'outil A, car l'agent ne regarde presque plus le futur (γ = 0,1 < 0,2, la bascule du cas 1).

**Exercice 6.** Q*(S0, offre) = 0,36 × 30 = 10,8 > Q*(S0, visite) = 10,4 : l'agent fait l'offre directe. C'est cohérent avec la bascule 0,34667 du cas 4, puisque 0,36 > 0,34667.

**Exercice 7.** Sans le « − Q », chaque mise à jour ajoute 0,5 × (1 + 0,9 × 5) = 2,75 : Q vaut 2 ; 4,75 ; 7,5 ; 10,25… et grandit sans fin, au lieu de s'approcher de 5,5. La formule correcte corrige l'écart à la cible, α(c − Q), qui s'annule quand Q atteint c ; la version fautive n'a pas de point fixe.

**Exercice 8.** Preuve : Qₙ₊₁ − μ = (1 − α)(Qₙ − μ) + α(cₙ − μ), deux termes indépendants, d'où Var(Qₙ₊₁) = (1 − α)²Var(Qₙ) + α²σ² ; à la limite, v(1 − (1 − α)²) = α²σ², et comme 1 − (1 − α)² = α(2 − α), v = ασ²/(2 − α). Application : 0,1 × 47,61/1,9 = 4,761/1,9 ≈ 2,5058, soit un écart-type d'environ 1,583, encore plus de cinq fois l'écart de 0,3 entre R et S.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`proche(x, y, tol)`** — Cette petite fonction est le contrôleur des poids et mesures qui tolère une poussière sur la balance : elle reçoit deux nombres et une tolérance, un milliardième par défaut, mesure la valeur absolue de leur écart et renvoie vrai s'il ne dépasse pas cette tolérance, faux sinon. Elle ne porte aucune théorie, mais elle permet aux `assert` de `main` de comparer des flottants sans se laisser piéger par les arrondis de la machine, par exemple pour vérifier que 0,9 × 5 vaut bien 4,5 ou que la variance de l'exercice 8 donne bien 4,761 avant division.

**`maj(q, r, max_suivant, gamma, alpha)`** — Cette fonction est le cœur du Q-learning, l'élève qui corrige sa note d'un pas mesuré chaque fois que la réalité lui répond : elle reçoit l'estimation actuelle Q, la récompense r observée, la meilleure valeur estimée de l'état suivant, le facteur γ et le pas α, refuse par une `ValueError` un pas hors de l'intervalle ]0 ; 1], puis construit la cible r + γ max et avance Q d'une fraction α de l'écart à cette cible. Elle renvoie la nouvelle estimation : partant de 2 avec r = 1, un maximum suivant de 5, γ = 0,9 et α = 0,5, elle donne 3,75, puis 4,625, 5,0625 et 5,28125, qui se rapprochent de 5,5.

**`variance_stationnaire(alpha, sigma2)`** — On la voit en météorologue qui prédit l'amplitude des oscillations d'une girouette agitée par un vent irrégulier : elle reçoit le pas constant α et la variance σ² des cibles, supposées indépendantes, refuse un pas hors de ]0 ; 1] par une `ValueError`, et renvoie la variance limite ασ²/(2 − α) de la démonstration 5. Avec σ² = 47,61, elle donne 15,87 pour α = 0,5, 2,5058 pour α = 0,1 et 1,2208 pour α = 0,05, ce qui montre qu'un pas trop grand laisse Q trembler bien plus que l'écart qu'il doit trancher.

**`esperance_max_deux_points(mu, sigma, k)`** — Cette fonction raconte la malédiction du meilleur candidat, celui qu'on croit exceptionnel parce qu'on a choisi le plus chanceux d'une série : elle reçoit la vraie valeur μ, l'amplitude σ du bruit et le nombre k d'estimations indépendantes, chacune valant μ + σ ou μ − σ avec la probabilité 1/2, refuse k < 1 par une `ValueError`, puis renvoie l'espérance du maximum, μ + σ(1 − 2 × 0,5ᵏ). Elle vaut 0,5 pour deux estimations de 0 ± 1 et 0,29375 pour cinq estimations de 0,2 ± 0,1, biais que la démonstration 6 et le cas 3 mettent en lumière.

**`demo_1_moyenne()`** — Celle-ci illustre que la mise à jour du Q-learning est une simple moyenne entre l'ancien avis et la cible : elle ne reçoit rien, calcule la cible 1 + 0,9 × 5 = 5,5, puis la nouvelle valeur 3,75 obtenue par `maj` depuis 2 avec α = 0,5, et vérifie qu'elle égale 0,5 × 2 + 0,5 × 5,5. Elle montre ensuite qu'un pas de 1,5 ferait bondir Q à 7,25, au-delà de la cible, et que `maj` refuse ce pas par une exception qu'elle attrape ; elle imprime ces nombres et les renvoie dans un dictionnaire.

**`demo_3_moyennes()`** — Cette fonction compare deux élèves qui reçoivent les mêmes notes 4, 6 et 8 en partant d'une estimation absurde de 123 : elle ne reçoit rien, fait appliquer à l'un un pas α = 1/n, qui oublie le départ dès la première mise à jour et aboutit exactement à la moyenne 6, et à l'autre un pas constant de 0,5, qui garde un poids de 0,125 sur le départ et finit à 21,375. Elle calcule aussi les poids 0,5, 0,25 et 0,125 des trois cibles, du plus récent au plus ancien, imprime la comparaison et renvoie ces résultats.

**`demo_5_bruit()`** — On y suit une estimation ballottée par une récompense qui vaut 3 neuf fois sur dix et −20 le reste du temps : la fonction ne reçoit rien, calcule la variance de cette récompense, 47,61, fixe la graine du hasard à 5, puis applique vingt mille mises à jour de pas 0,5 et garde les valeurs de Q après les mille premières. Elle compare la variance observée, 16,15 autour d'une moyenne de 0,654, à la prédiction 15,87 de `variance_stationnaire`, calcule aussi les variances prévues pour α = 0,05 et α = 0,1, imprime le tout et le renvoie.

**`demo_6_biais_max()`** — Cette fonction est l'enquêtrice qui démontre, par simple énumération, que le maximum de deux estimations sans biais est biaisé : elle ne reçoit rien, demande à `esperance_max_deux_points` l'espérance du maximum de deux estimations de 0 ± 1, soit 0,5, et la retrouve en passant en revue les quatre couples équiprobables, dont trois donnent un maximum de 1 et un seul −1. Elle calcule ensuite le cas de cinq estimations de 0,2 ± 0,1, qui donne 0,29375, imprime ces valeurs et les renvoie, préparant le cas 3 du sourcing.

**`episodes_outils(alpha, n, gamma, trace)`** — Celle-ci fait vivre à un agent n épisodes d'exploration, vingt par défaut, dans un petit monde à trois actions : l'outil A rapporte 1 et termine, l'outil B ne rapporte rien mais mène à l'état s₁, où l'action C rapporte 5. Elle reçoit le pas α, le nombre d'épisodes, γ, 0,9 par défaut, et un drapeau `trace`, alterne A aux épisodes impairs et B suivi de C aux épisodes pairs en mettant à jour la table Q avec `maj`, note le premier épisode où Q(s₀, B) dépasse Q(s₀, A) et imprime la table après 4, 10 et 20 épisodes si `trace` est levé. Elle renvoie la table et ce premier épisode : 4 avec α = 0,5, 6 avec α = 0,25.

**`cas_1_devis_btp()`** — Cette fonction raconte un groupe de construction dont l'agent reçoit environ 800 demandes de devis par mois et hésite entre un devis rapide par barème, l'outil A, et un relevé de quantités suivi d'un devis détaillé, B puis C : elle ne reçoit rien, fait tourner `episodes_outils` avec α = 0,5 puis 0,25, et vérifie qu'au point fixe Q* = (1 ; 4,5 ; 5) les trois erreurs de différence temporelle sont nulles. Elle chiffre à 280 000 AED par mois la perte d'une règle qui ne regarde que la récompense immédiate et choisit A, calcule le γ de bascule 0,2 sous lequel A redevient le bon choix, imprime ces résultats et les renvoie.

**`cas_2_reequilibrage_crypto()`** — Ici, une plateforme d'actifs virtuels rééquilibre son portefeuille chaud environ 900 fois par mois, par une procédure rapide R qui rapporte 3 ou coûte 20, ou par une procédure standard S qui rapporte 1 à coup sûr : la fonction ne reçoit rien, calcule l'espérance 0,7 de R, inférieure à 1, sa variance 47,61, son écart-type 6,9, l'écart-type 3,98 de Q avec α = 0,5 et le nombre minimal de 2 116 essais. Elle simule vingt mille opérations avec la graine 18 et constate qu'avec un pas de 0,5, Q(R) passe pour meilleur 72,4 % du temps, contre jamais avec α = 1/n, chiffre la perte à 195 480 AED et 65,2 incidents par mois, calcule la bascule 0,08696 et renvoie ces résultats.

**`cas_3_sourcing_rh()`** — Cette fonction met en scène un cabinet de recrutement qui doit pourvoir 40 postes et estime cinq canaux de sourcing qui ont tous, en réalité, le même taux d'embauche de 0,2 : elle ne reçoit rien et montre que le meilleur canal estimé promet en moyenne 0,29375, si bien que l'agent prévoit 137 candidats, n'obtient que 27,4 embauches et en manque 12,6, alors qu'un plan sans biais en demanderait 200, pour un budget de 30 000 AED au lieu de 20 550. Elle vérifie le biais avec le modèle binomial exact de dix candidats par canal, 0,3514, le compare à deux et dix canaux, 0,25 et 0,2998, et à vingt candidats par canal, 0,2663, puis renvoie ces nombres.

**`cas_4_prospects_immo(p_offre, afficher, simuler)`** — On y suit une agence immobilière qui veut savoir, pour un prospect, s'il vaut mieux proposer une visite ou faire tout de suite une offre, à partir de 20 000 épisodes enregistrés sous une ancienne règle à pile ou face : la fonction reçoit la probabilité de succès d'une offre directe, 0,3 par défaut, et deux drapeaux, calcule Q*(S₁) = 12 pour l'offre et 5,5 pour la relance, puis Q*(S₀) = 10,4 pour la visite et 9 pour l'offre, ainsi que la valeur 7,3125 de la visite sous la règle à pile ou face, et s'arrête là si `simuler` est faux. Sinon, avec la graine 38, elle apprend la table par Q-learning, qui choisit la visite, alors que la moyenne des retours observés, 7,43, choisirait l'offre, chiffre l'écart à 420 000 AED par mois, calcule les bascules 0,34667 et 2,4, et renvoie le tout.

**`main()`** — C'est le chef d'orchestre de la fiche : il enchaîne d'abord quatre mises à jour depuis 2, qui donnent 3,75, 4,625, 5,0625 et 5,28125, et vérifie que l'écart à 5,5 est divisé par deux à chaque fois, puis appelle les démonstrations 1, 3, 5 et 6 et contrôle leurs nombres. Il joue ensuite les quatre cas, en reconstituant aussi la table après 1, 2, 4 et 10 épisodes, puis recalcule le corrigé des exercices, jusqu'à la version fautive sans « − Q » qui grandit sans fin ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tout concorde.

```python
"""Démonstration 18 — Q-learning : moyenne vers la cible, convergence, moyenne 1/n, point fixe de Bellman, bruit, biais du max, quatre cas aux Émirats."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def proche(x: float, y: float, tol: float = 1e-9) -> bool:
    return abs(x - y) <= tol


def maj(q, r, max_suivant, gamma, alpha):
    """Q ← Q + α [r + γ max Q(s′, ·) − Q] ; α doit être dans ]0 ; 1]."""
    if not 0 < alpha <= 1:
        raise ValueError("α doit être dans ]0 ; 1]")
    return q + alpha * (r + gamma * max_suivant - q)


def variance_stationnaire(alpha: float, sigma2: float) -> float:
    """Variance limite de Q pour des cibles indépendantes de variance σ² et un pas constant α (démonstration 5)."""
    if not 0 < alpha <= 1:
        raise ValueError("α doit être dans ]0 ; 1]")
    return alpha * sigma2 / (2 - alpha)


def esperance_max_deux_points(mu: float, sigma: float, k: int) -> float:
    """E[max] de k estimations indépendantes μ ± σ (probabilité 1/2 chacune) : μ + σ (1 − 2 × 0,5ᵏ)."""
    if k < 1:
        raise ValueError("au moins une estimation")
    return mu + sigma * (1 - 2 * 0.5 ** k)


def demo_1_moyenne() -> dict:
    c = 1 + 0.9 * 5
    q = maj(2, 1, 5, 0.9, 0.5)
    convexe = 0.5 * 2 + 0.5 * c
    trop_grand = 2 + 1.5 * (c - 2)                  # α = 1,5 : on dépasse la cible
    try:
        maj(2, 1, 5, 0.9, 1.5)
        refuse = False
    except ValueError:
        refuse = True
    print(f"démo 1 : cible {c} ; Q = {q} = 0.5 × 2 + 0.5 × {c} ; α = 1.5 donnerait {trop_grand} (refusé : {refuse})")
    return {"c": c, "q": q, "convexe": convexe, "trop_grand": trop_grand, "refuse": refuse}


def demo_3_moyennes() -> dict:
    q, cibles = 123.0, [4, 6, 8]
    for n, c in enumerate(cibles, start=1):
        q = maj(q, c, 0, 0, 1 / n)
    q_cst = 123.0
    for c in cibles:
        q_cst = maj(q_cst, c, 0, 0, 0.5)
    poids = [0.5 * 0.5 ** k for k in range(3)]
    print(f"démo 3 : α = 1/n → {q:.0f} ; α = 0.5 → {q_cst} (poids {poids[0]}, {poids[1]}, {poids[2]}, départ {0.5 ** 3})")
    return {"q": q, "q_cst": q_cst, "poids": poids}


def demo_5_bruit() -> dict:
    sigma2 = 0.9 * 3 ** 2 + 0.1 * 20 ** 2 - 0.7 ** 2
    random.seed(5)
    q, valeurs = 0.0, []
    for t in range(20000):
        r = 3.0 if random.random() < 0.9 else -20.0
        q = maj(q, r, 0, 0, 0.5)
        if t >= 1000:
            valeurs.append(q)
    m = sum(valeurs) / len(valeurs)
    v_emp = sum((x - m) ** 2 for x in valeurs) / len(valeurs)
    v05, v005, v01 = variance_stationnaire(0.5, sigma2), variance_stationnaire(0.05, sigma2), variance_stationnaire(0.1, sigma2)
    print(f"démo 5 : σ² = {sigma2:.2f} ; α = 0.5 → théorie {v05:.2f}, simulé {v_emp:.2f} (moyenne {m:.3f}) ;"
          f" α = 0.05 → {v005:.4f} ; α = 0.1 → {v01:.4f}")
    return {"sigma2": sigma2, "v05": v05, "v_emp": v_emp, "m": m, "v005": v005, "v01": v01}


def demo_6_biais_max() -> dict:
    deux = esperance_max_deux_points(0.0, 1.0, 2)
    exact_deux = 0.25 * 1 + 0.25 * 1 + 0.25 * 1 + 0.25 * (-1)
    cinq = esperance_max_deux_points(0.2, 0.1, 5)
    print(f"démo 6 : 2 estimations 0 ± 1 → E[max] = {deux} (énumération {exact_deux}) ; 5 estimations 0.2 ± 0.1 → {cinq:.5f}")
    return {"deux": deux, "exact_deux": exact_deux, "cinq": cinq}


def episodes_outils(alpha: float, n: int = 20, gamma: float = 0.9, trace: bool = False) -> tuple[dict, int | None]:
    """Cas 1 : A (récompense 1, fin) ou B (0, puis s1 où C rapporte 5) ; exploration alternée A, B, A, B…"""
    Q = {("s0", "A"): 0.0, ("s0", "B"): 0.0, ("s1", "C"): 0.0}
    premier = None
    for episode in range(1, n + 1):
        if episode % 2:
            Q["s0", "A"] = maj(Q["s0", "A"], 1, 0, gamma, alpha)
        else:
            Q["s0", "B"] = maj(Q["s0", "B"], 0, Q["s1", "C"], gamma, alpha)
            Q["s1", "C"] = maj(Q["s1", "C"], 5, 0, gamma, alpha)
        if premier is None and Q["s0", "B"] > Q["s0", "A"]:
            premier = episode
        if trace and episode in (4, 10, 20):
            print(f"  après {episode:>2} épisodes : " + " ; ".join(f"Q{k} = {v:.5f}" for k, v in Q.items()))
    return Q, premier


def cas_1_devis_btp() -> dict:
    """[BTP] devis rapide par barème (A) ou relevé de quantités puis devis détaillé (B puis C)."""
    Q, premier = episodes_outils(0.5, trace=True)
    _, premier_025 = episodes_outils(0.25)
    q_etoile = {"A": 1.0, "B": 0.9 * 5, "C": 5.0}
    erreurs_td = [1 + 0 - q_etoile["A"], 0 + 0.9 * q_etoile["C"] - q_etoile["B"], 5 - q_etoile["C"]]
    perte_myope = (q_etoile["B"] - q_etoile["A"]) * 100 * 800
    g_bascule = 1 / 5
    print(f"cas 1 : Q* = (1, 4.5, 5), erreurs TD au point fixe {erreurs_td} ; B passe devant à l'épisode {premier}"
          f" (α = 0.5), {premier_025} (α = 0.25)")
    print(f"        règle « récompense immédiate » → A : {perte_myope:,.0f} AED/mois ; bascule γ = {g_bascule}")
    return {"Q": Q, "premier": premier, "premier_025": premier_025, "erreurs_td": erreurs_td,
            "perte_myope": perte_myope, "g_bascule": g_bascule}


def cas_2_reequilibrage_crypto() -> dict:
    """[CRYPTO] procédure rapide R (+3 ou −20) ou standard S (+1) : bruit de Q selon α."""
    moy_r = 0.9 * 3 + 0.1 * (-20)
    sigma2 = 0.9 * 9 + 0.1 * 400 - moy_r ** 2
    sigma = math.sqrt(sigma2)
    sd05 = math.sqrt(variance_stationnaire(0.5, sigma2))
    random.seed(18)
    q_cst, q_moy, n, fausses_cst, fausses_moy, comptees = 0.0, 0.0, 0, 0, 0, 0
    for t in range(1, 20001):
        r = 3.0 if random.random() < 0.9 else -20.0
        q_cst = maj(q_cst, r, 0, 0, 0.5)
        n += 1
        q_moy = maj(q_moy, r, 0, 0, 1 / n)
        if t > 2116:
            comptees += 1
            fausses_cst += q_cst > 1.0
            fausses_moy += q_moy > 1.0
    f_cst, f_moy = fausses_cst / comptees, fausses_moy / comptees
    n_min = (2 * sigma / (1.0 - moy_r)) ** 2
    q_bascule = 2 / 23
    perte = f_cst * 0.3 * 900 * 1000
    incidents = f_cst * 900 * 0.1
    print(f"cas 2 : E[R] = {moy_r:.1f} < 1 ; σ² = {sigma2:.2f}, σ = {sigma:.1f} ; écart-type de Q (α = 0.5) {sd05:.2f} ;"
          f" n minimal {n_min:,.0f}")
    print(f"        part du temps où Q(R) > Q(S) : α = 0.5 → {f_cst:.3f}, α = 1/n → {f_moy:.3f} ; perte {perte:,.0f} AED/mois,"
          f" {incidents:.1f} incidents ; bascule incident {q_bascule:.5f} ; moyenne finale {q_moy:.3f}")
    return {"moy_r": moy_r, "sigma2": sigma2, "sigma": sigma, "sd05": sd05, "f_cst": f_cst, "f_moy": f_moy,
            "n_min": n_min, "q_bascule": q_bascule, "perte": perte, "incidents": incidents, "q_moy": q_moy}


def cas_3_sourcing_rh() -> dict:
    """[RH] 5 canaux de même taux réel 0,2 ; estimations bruitées ; le max surestime."""
    biais = esperance_max_deux_points(0.2, 0.1, 5)
    prevu = math.ceil(40 / biais)
    reel = prevu * 0.2
    manque = 40 - reel
    juste = math.ceil(40 / 0.2)
    budget_biais, budget_juste = prevu * 150, juste * 150
    binom = [math.comb(10, k) * 0.2 ** k * 0.8 ** (10 - k) for k in range(11)]
    cumul = [sum(binom[: k + 1]) for k in range(11)]
    e_max_binom = sum(1 - cumul[k] ** 5 for k in range(10)) / 10
    k2, k10 = esperance_max_deux_points(0.2, 0.1, 2), esperance_max_deux_points(0.2, 0.1, 10)
    double = esperance_max_deux_points(0.2, 0.1 / math.sqrt(2), 5)
    print(f"cas 3 : E[max] = {biais:.5f} ; prévu {prevu} candidats → {reel:.1f} embauches (manque {manque:.1f}) ;"
          f" sans biais {juste} candidats ; budgets {budget_biais:,} et {budget_juste:,} AED")
    print(f"        modèle binomial exact : E[max] = {e_max_binom:.4f} ; 2 canaux {k2:.3f}, 10 canaux {k10:.4f} ;"
          f" 20 candidats par canal {double:.4f}")
    return {"biais": biais, "prevu": prevu, "reel": reel, "manque": manque, "juste": juste,
            "budget_biais": budget_biais, "budget_juste": budget_juste, "e_max_binom": e_max_binom,
            "k2": k2, "k10": k10, "double": double}


def cas_4_prospects_immo(p_offre: float = 0.3, afficher: bool = True, simuler: bool = True) -> dict:
    """[IMMO] journaux d'une politique 50/50 ; Q-learning (max) contre moyenne des retours observés."""
    gamma = 0.95
    q_s1 = {"offre": 0.4 * 30, "relance": -0.5 + 0.2 * 30}
    etoile = {"visite": -1 + gamma * max(q_s1.values()), "offre": p_offre * 30}
    v_pi_s1 = 0.5 * q_s1["offre"] + 0.5 * q_s1["relance"]
    q_pi_visite = -1 + gamma * v_pi_s1
    if not simuler:                                                  # valeurs exactes seulement
        return {"q_s1": q_s1, "etoile": etoile, "q_pi_visite": q_pi_visite}
    random.seed(38)
    Q = {("S0", "visite"): 0.0, ("S0", "offre"): 0.0, ("S1", "offre"): 0.0, ("S1", "relance"): 0.0}
    n = dict.fromkeys(Q, 0)
    somme_retours, nb_visites = 0.0, 0
    for _ in range(20000):
        if random.random() < 0.5:                                    # politique des journaux : 50/50
            r = 30.0 if random.random() < p_offre else 0.0
            n["S0", "offre"] += 1
            Q["S0", "offre"] = maj(Q["S0", "offre"], r, 0, gamma, 1 / n["S0", "offre"])
            continue
        n["S0", "visite"] += 1
        Q["S0", "visite"] = maj(Q["S0", "visite"], -1.0, max(Q["S1", "offre"], Q["S1", "relance"]), gamma,
                                1 / n["S0", "visite"])
        a1 = "offre" if random.random() < 0.5 else "relance"
        if a1 == "offre":
            r1 = 30.0 if random.random() < 0.4 else 0.0
        else:
            r1 = -0.5 + (30.0 if random.random() < 0.2 else 0.0)
        n["S1", a1] += 1
        Q["S1", a1] = maj(Q["S1", a1], r1, 0, gamma, 1 / n["S1", a1])
        somme_retours += -1.0 + gamma * r1
        nb_visites += 1
    mc_visite = somme_retours / nb_visites
    choix_q = "visite" if Q["S0", "visite"] > Q["S0", "offre"] else "offre"
    choix_mc = "visite" if mc_visite > Q["S0", "offre"] else "offre"
    perte = (etoile["visite"] - etoile["offre"]) * 1000 * 300
    p_bascule = etoile["visite"] / 30
    c_bascule = -etoile["offre"] + gamma * max(q_s1.values())
    if afficher:
        print(f"cas 4 : Q*(S1) = {q_s1['offre']:.0f} / {q_s1['relance']:.1f} ; Q*(S0) visite {etoile['visite']:.1f},"
              f" offre {etoile['offre']:.0f} ; Q^π(S0, visite) = {q_pi_visite:.4f}")
        print("        appris sur 20 000 épisodes : " + " ; ".join(f"Q{k} = {v:.2f}" for k, v in Q.items()))
        print(f"        Q-learning → {choix_q} ; moyenne des retours {mc_visite:.2f} → {choix_mc} ;"
              f" perte {perte:,.0f} AED/mois ; bascules p = {p_bascule:.5f}, coût de visite {c_bascule:.1f}")
    return {"q_s1": q_s1, "etoile": etoile, "q_pi_visite": q_pi_visite, "Q": Q, "mc_visite": mc_visite,
            "choix_q": choix_q, "choix_mc": choix_mc, "perte": perte, "p_bascule": p_bascule,
            "c_bascule": c_bascule, "n": n}


def main() -> None:
    q, suite = 2.0, []
    for _ in range(4):
        q = maj(q, 1, 5, 0.9, 0.5)
        suite.append(q)
    print(f"mises à jour successives : {suite}")
    assert suite == [3.75, 4.625, 5.0625, 5.28125]
    assert all(math.isclose(5.5 - v, 3.5 * 0.5 ** (n + 1)) for n, v in enumerate(suite))   # démonstration 2
    assert [5.5 - v for v in suite] == [1.75, 0.875, 0.4375, 0.21875] and proche(0.9 * 5, 4.5)

    d1 = demo_1_moyenne()
    assert d1["c"] == 5.5 and d1["q"] == 3.75 and d1["convexe"] == 3.75 and d1["trop_grand"] == 7.25 and d1["refuse"]
    assert 2 <= d1["q"] <= d1["c"] and proche(0.5 * 2, 1) and proche(0.5 * 5.5, 2.75)
    n1000 = math.ceil(math.log(1000) / math.log(2))
    assert n1000 == 10 and round(math.log(1000) / math.log(2), 2) == 9.97
    assert abs(2 + 2.5 * 3.5 - 5.5) > abs(2 - 5.5) and proche(-1.5 * 3.5, -5.25)
    d3 = demo_3_moyennes()
    assert math.isclose(d3["q"], 6) and d3["q_cst"] == 21.375 and d3["poids"] == [0.5, 0.25, 0.125]
    assert 0.125 * 123 == 15.375 and 0.5 * 123 + 0.5 * 4 == 63.5 and 0.5 * 63.5 + 3 == 34.75
    d5 = demo_5_bruit()
    assert round(d5["sigma2"], 2) == 47.61 and round(d5["v05"], 2) == 15.87 and abs(d5["v_emp"] - d5["v05"]) < 1.0
    assert round(d5["v_emp"], 2) == 16.15 and round(d5["m"], 3) == 0.654
    assert round(d5["v005"], 4) == 1.2208 and round(d5["v01"], 4) == 2.5058 and round(math.sqrt(d5["v01"]), 3) == 1.583
    assert round(math.sqrt(d5["v005"]), 3) == 1.105 and round(1 - 0.5 ** 2, 2) == 0.75
    d6 = demo_6_biais_max()
    assert d6["deux"] == 0.5 and d6["exact_deux"] == 0.5 and round(d6["cinq"], 5) == 0.29375
    assert proche(1 - 2 * 0.5 ** 5, 0.9375)

    c1 = cas_1_devis_btp()
    Q = c1["Q"]
    assert [round(v, 5) for v in Q.values()] == [0.99902, 4.45166, 4.99512] and c1["premier"] == 4
    Q4, _ = episodes_outils(0.5, n=4)
    assert (Q4["s0", "A"], Q4["s0", "B"], Q4["s1", "C"]) == (0.75, 1.125, 3.75)
    Q2, _ = episodes_outils(0.5, n=2)
    assert (Q2["s0", "A"], Q2["s0", "B"], Q2["s1", "C"]) == (0.5, 0.0, 2.5) and episodes_outils(0.5, n=1)[0]["s0", "A"] == 0.5
    Q10, _ = episodes_outils(0.5, n=10)
    assert [round(v, 5) for v in Q10.values()] == [0.96875, 3.65625, 4.84375]
    assert c1["premier_025"] == 6 and c1["erreurs_td"] == [0, 0, 0]
    assert round(c1["perte_myope"]) == 280000 and c1["g_bascule"] == 0.2 and proche(0.1 * 5, 0.5)
    assert round(4.5 - 4.45166, 5) == 0.04834 and round(0.9 * 2.5 * 0.5, 3) == 1.125
    c2 = cas_2_reequilibrage_crypto()
    assert round(c2["moy_r"], 1) == 0.7 and round(c2["sigma2"], 2) == 47.61 and round(c2["sigma"], 1) == 6.9
    assert round(c2["sd05"], 2) == 3.98 and round(c2["n_min"]) == 2116
    assert round(c2["f_cst"], 3) == 0.724 and round(c2["f_moy"], 3) == 0.0 and round(c2["q_moy"], 3) == 0.706
    assert round(c2["q_bascule"], 5) == 0.08696 and round(c2["perte"]) == 195480 and round(c2["incidents"], 1) == 65.2
    assert proche(3 * (1 - 2 / 23) - 20 * 2 / 23, 1) and round(48.1 - 0.49, 2) == 47.61 and c2["sd05"] / 0.3 > 13
    assert proche(0.9 * 9 + 0.1 * 400, 48.1) and round((2 * 6.9 / 0.3) ** 2, 6) == 46 ** 2 == 2116
    assert [maj(0, 3, 0, 0, 0.5), maj(1.5, 3, 0, 0, 0.5), maj(2.25, 3, 0, 0, 0.5)] == [1.5, 2.25, 2.625]
    c3 = cas_3_sourcing_rh()
    assert round(c3["biais"], 5) == 0.29375 and c3["prevu"] == 137 and round(c3["reel"], 1) == 27.4
    assert round(c3["manque"], 1) == 12.6 and c3["juste"] == 200 and c3["budget_biais"] == 20550
    assert c3["budget_juste"] == 30000 and round(c3["e_max_binom"], 4) == 0.3514
    assert round(c3["k2"], 3) == 0.25 and round(c3["k10"], 4) == 0.2998 and round(c3["double"], 4) == 0.2663
    assert round(40 / 0.29375, 2) == 136.17 and round(0.1 / math.sqrt(2), 4) == 0.0707
    assert round((c3["biais"] - 0.2) / 0.2, 3) == 0.469 and 200 - 137 == 63 and 63 * 150 == 9450
    c4 = cas_4_prospects_immo()
    assert c4["q_s1"] == {"offre": 12.0, "relance": 5.5} and round(c4["etoile"]["visite"], 1) == 10.4
    assert round(c4["etoile"]["offre"]) == 9 and round(c4["q_pi_visite"], 4) == 7.3125
    assert [round(v, 2) for v in c4["Q"].values()] == [10.38, 9.1, 12.13, 5.6]
    assert c4["choix_q"] == "visite" and c4["choix_mc"] == "offre" and round(c4["mc_visite"], 2) == 7.43
    assert round(c4["perte"]) == 420000 and round(c4["p_bascule"], 5) == 0.34667 and round(c4["c_bascule"], 1) == 2.4
    assert min(c4["n"].values()) > 4000 and proche(0.5 * 12 + 0.5 * 5.5, 8.75)
    assert proche(-1 + 0.95 * 5.5, -1 + 5.225) and round(-1 + 0.95 * 5.5, 3) == 4.225 and round(0.95 * 12, 1) == 11.4
    assert round(-1 + 0.95 * 0.36 * 30, 2) == 9.26 and round(0.36 * 30, 1) == 10.8

    print("Corrigé")
    n = next(k for k in range(1, 50) if 0.75 ** k <= 0.1)
    ex6 = cas_4_prospects_immo(p_offre=0.36, afficher=False, simuler=False)
    faux = [2.0]
    for _ in range(3):
        faux.append(faux[-1] + 0.5 * (1 + 0.9 * 5))      # exercice 7 : le « − Q » oublié
    print(f"  ex1 {maj(0, 2, 10, 0.8, 0.25)} ; ex2 {n} mises à jour ; ex3 {d3['q']:.0f} ; ex4 {0.5 * 0.5 ** 3} ; ex5 {0.1 * 5}")
    print(f"  ex6 Q*(S0, offre) = {ex6['etoile']['offre']:.1f} → {'offre' if ex6['etoile']['offre'] > ex6['etoile']['visite'] else 'visite'} ;"
          f" ex7 sans « − Q » : {faux} ; ex8 α = 0.1 → {d5['v01']:.4f}")
    assert maj(0, 2, 10, 0.8, 0.25) == 2.5 and n == 9 and 0.5 * 0.5 ** 3 == 0.0625 and 0.1 * 5 < 1
    assert round(0.75 ** 8, 4) == 0.1001 and round(math.log(10) / math.log(1 / 0.75), 1) == 8.0
    assert round(ex6["etoile"]["offre"], 1) == 10.8 and ex6["etoile"]["offre"] > ex6["etoile"]["visite"]
    assert faux == [2.0, 4.75, 7.5, 10.25] and proche(0.5 * (1 + 0.9 * 5), 2.75)
    assert proche(0.1 * 47.61, 4.761) and math.sqrt(d5["v01"]) / 0.3 > 5 and proche(0.5 / (2 - 0.5), 1 / 3)
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
mises à jour successives : [3.75, 4.625, 5.0625, 5.28125]
démo 1 : cible 5.5 ; Q = 3.75 = 0.5 × 2 + 0.5 × 5.5 ; α = 1.5 donnerait 7.25 (refusé : True)
démo 3 : α = 1/n → 6 ; α = 0.5 → 21.375 (poids 0.5, 0.25, 0.125, départ 0.125)
démo 5 : σ² = 47.61 ; α = 0.5 → théorie 15.87, simulé 16.15 (moyenne 0.654) ; α = 0.05 → 1.2208 ; α = 0.1 → 2.5058
démo 6 : 2 estimations 0 ± 1 → E[max] = 0.5 (énumération 0.5) ; 5 estimations 0.2 ± 0.1 → 0.29375
  après  4 épisodes : Q('s0', 'A') = 0.75000 ; Q('s0', 'B') = 1.12500 ; Q('s1', 'C') = 3.75000
  après 10 épisodes : Q('s0', 'A') = 0.96875 ; Q('s0', 'B') = 3.65625 ; Q('s1', 'C') = 4.84375
  après 20 épisodes : Q('s0', 'A') = 0.99902 ; Q('s0', 'B') = 4.45166 ; Q('s1', 'C') = 4.99512
cas 1 : Q* = (1, 4.5, 5), erreurs TD au point fixe [0.0, 0.0, 0.0] ; B passe devant à l'épisode 4 (α = 0.5), 6 (α = 0.25)
        règle « récompense immédiate » → A : 280,000 AED/mois ; bascule γ = 0.2
cas 2 : E[R] = 0.7 < 1 ; σ² = 47.61, σ = 6.9 ; écart-type de Q (α = 0.5) 3.98 ; n minimal 2,116
        part du temps où Q(R) > Q(S) : α = 0.5 → 0.724, α = 1/n → 0.000 ; perte 195,480 AED/mois, 65.2 incidents ; bascule incident 0.08696 ; moyenne finale 0.706
cas 3 : E[max] = 0.29375 ; prévu 137 candidats → 27.4 embauches (manque 12.6) ; sans biais 200 candidats ; budgets 20,550 et 30,000 AED
        modèle binomial exact : E[max] = 0.3514 ; 2 canaux 0.250, 10 canaux 0.2998 ; 20 candidats par canal 0.2663
cas 4 : Q*(S1) = 12 / 5.5 ; Q*(S0) visite 10.4, offre 9 ; Q^π(S0, visite) = 7.3125
        appris sur 20 000 épisodes : Q('S0', 'visite') = 10.38 ; Q('S0', 'offre') = 9.10 ; Q('S1', 'offre') = 12.13 ; Q('S1', 'relance') = 5.60
        Q-learning → visite ; moyenne des retours 7.43 → offre ; perte 420,000 AED/mois ; bascules p = 0.34667, coût de visite 2.4
Corrigé
  ex1 2.5 ; ex2 9 mises à jour ; ex3 6 ; ex4 0.0625 ; ex5 0.5
  ex6 Q*(S0, offre) = 10.8 → offre ; ex7 sans « − Q » : [2.0, 4.75, 7.5, 10.25] ; ex8 α = 0.1 → 2.5058
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme apprend les valeurs Q par essais : après chaque action, il rapproche Q(s, a) de la cible r + γ max Q(s′, ·). Il peut tourner en ligne, en explorant, ou sur des journaux d'une autre politique, à condition que chaque couple (s, a) y soit assez présent.

```text
ALGORITHME QLearning
ENTRÉES : environnement ou journaux, γ, α (constant ou 1/n), nombre d'épisodes E, politique d'exploration
SORTIE  : table Q

  Q(s, a) ← 0 et n(s, a) ← 0 pour tout état s et toute action a
  POUR épisode DE 1 À E FAIRE
      s ← état initial
      TANT QUE s n'est pas terminal FAIRE
          choisir a (en explorant) ou lire a dans le journal
          jouer a ; observer r et s′
          n(s, a) ← n(s, a) + 1 ; SI α est « 1/n » ALORS pas ← 1 / n(s, a) SINON pas ← α
          cible ← r + γ × max sur a′ de Q(s′, a′)   (0 si s′ est terminal)
          Q(s, a) ← Q(s, a) + pas × (cible − Q(s, a))
          s ← s′
      FIN TANT QUE
  FIN POUR
  vérifier que chaque n(s, a) dépasse le minimum de couverture
  RETOURNER Q
```

**Complexité.** O(|A|) par mise à jour, pour le maximum sur les actions suivantes ; O(E × L × |A|) pour E épisodes de longueur L. Mémoire O(|S| × |A|) pour la table et autant pour les compteurs. Le nombre d'épisodes utile se lit dans les démonstrations 2 et 5 : il faut assez de mises à jour par case pour que l'écart à la cible et le bruit soient sous l'écart entre actions à départager (2 116 observations au cas 2).

**Du squelette au code.** La mise à jour est la fonction `maj(q, r, max_suivant, gamma, alpha)`, qui lève `ValueError` si α sort de ]0 ; 1]. Les épisodes du cas 1 sont la boucle `for episode in range(1, n + 1)` de `episodes_outils`, qui alterne A (épisodes impairs) et B (épisodes pairs) au lieu d'une exploration aléatoire, pour que la sortie soit reproductible ; la moyenne avec α = 1/n est vérifiée avec les cibles 4, 6, 8 dans `demo_3_moyennes`. Le plancher de bruit est `variance_stationnaire(alpha, sigma2)`, vérifié par simulation dans `demo_5_bruit`, et le biais du maximum est `esperance_max_deux_points(mu, sigma, k)`, utilisé par `demo_6_biais_max`. Les quatre cas sont `cas_1_devis_btp`, `cas_2_reequilibrage_crypto`, `cas_3_sourcing_rh` et `cas_4_prospects_immo`, ce dernier avec les compteurs `n` qui donnent le pas 1/n de chaque case et contrôlent la couverture des journaux.
