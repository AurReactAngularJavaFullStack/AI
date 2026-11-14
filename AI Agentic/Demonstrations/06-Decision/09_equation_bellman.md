# 09 — Équation de Bellman : démonstrations

> Fiche : [09 — Équation de Bellman](<../../Images/06-Decision/09_equation_bellman.md>) · Image : `09_equation_bellman.jpg` · Leçon : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
V(s) = \sum_{a} \pi(a \mid s) \sum_{s'} P(s' \mid s, a) \left[ R + \gamma\, V(s') \right]
$$

V(s) est la valeur de l'état s quand l'agent suit la politique π : la récompense attendue, en comptant le futur avec une remise γ ∈ [0 ; 1[. Plus précisément, c'est la somme actualisée **espérée** des récompenses futures (leçon, étape 38), et R désigne la récompense R(s, a, s′) reçue pendant le passage de s à s′ par l'action a.

## Les symboles, un par un

$$
s
$$

L'état présent : tout ce que l'agent doit savoir pour prévoir la suite (dans les tickets du cas 1 : N « nouveau », A « en attente », R « résolu ») ; un élément d'un ensemble fini d'états ; dans le programme, un état est une position de la liste renvoyée par `evaluer`, et les états N et A sont portés par les arguments `vN` et `vA` de `passe`.

$$
a
$$

Une action possible dans l'état s : appeler l'outil A, relancer, escalader ; un élément d'un ensemble fini d'actions ; dans le programme, chaque action est une branche de calcul, par exemple `q_a` et `q_b` dans l'exemple simple.

$$
s'
$$

L'état suivant, tiré au hasard après l'action ; il appartient au même ensemble que s ; c'est l'indice de colonne de la matrice `P` passée à `evaluer`.

$$
\pi(a \mid s)
$$

La politique : la probabilité que l'agent choisisse a dans l'état s ; un nombre de [0 ; 1], de somme 1 sur les actions ; dans l'exemple simple, ce sont les deux coefficients 0.5 de `v_s = 0.5 * q_a + 0.5 * q_b`.

$$
P(s' \mid s, a)
$$

La probabilité d'arriver en s′ quand on joue a dans s ; un nombre de [0 ; 1], de somme 1 sur s′ pour chaque couple (s, a) ; dans `passe`, ce sont les coefficients 0.6 et 0.4 depuis N, et `p_relance` et `1 - p_relance` depuis A.

$$
R
$$

La récompense R(s, a, s′) reçue pendant la transition, en points (dans les cas 1 et 2, 1 point vaut environ 10 AED, illustratif) ; un réel, borné en valeur absolue par Rₘₐₓ ; dans `passe`, ce sont les nombres 10, −2, 8 et −1.

$$
\gamma
$$

Le facteur d'actualisation : une récompense reçue k pas plus tard compte γᵏ fois ; un réel de [0 ; 1[, la valeur 1 n'étant permise que si chaque épisode se termine ; la constante `GAMMA`, égale à 0.9.

$$
V(s), \; V(s')
$$

La valeur de l'état présent et celle de l'état suivant, sous la politique π ; même unité que R ; toujours |V| ≤ Rₘₐₓ/(1 − γ) (démonstration 5) ; les estimations successives sont `vN` et `vA`, la solution exacte `vN_exact` et `vA_exact`.

$$
G_t
$$

Le retour depuis l'instant t : la somme actualisée des récompenses d'une trajectoire, un nombre aléatoire dont V(s) est la moyenne ; dans `demo_1_retour`, chaque épisode simulé ajoute son retour à `total`.

$$
Q(s, a)
$$

La valeur de l'action a dans l'état s : la somme intérieure de la formule, avant la moyenne sur π ; même unité que V ; les variables `q_a`, `q_b` de l'exemple simple et `q_rel`, `q_ree` du cas 2.

$$
P_\pi, \; r_\pi
$$

Pour une politique fixée : la matrice Pπ donne la probabilité de passer de s à s′ en un pas, actions confondues, et le vecteur rπ la récompense immédiate moyenne de chaque état (définitions exactes dans la démonstration 3) ; coefficients ≥ 0, chaque ligne de Pπ somme à 1 au plus quand on retire les états terminaux ; les arguments `P` et `r` de `evaluer(P, r, gamma)`.

## Le mécanisme, avant les preuves

La formule reçoit des nombres connus (les probabilités π et P, les récompenses R, le facteur γ) et une inconnue, la table des valeurs V, qui apparaît des deux côtés du signe égal. La première opération, γ × V(s′), rapetisse la valeur de l'état d'arrivée : un gain qui n'arrive qu'au pas suivant vaut moins qu'un gain immédiat, parce qu'il est plus incertain et qu'attendre coûte. La deuxième opération, R + γV(s′), colle la récompense du pas à la valeur de tout ce qui suit : le crochet est le retour d'une seule branche. La troisième opération est la somme pondérée par P(s′ ∣ s, a) : elle fait la moyenne des branches que le hasard peut choisir, et le résultat est Q(s, a), la valeur de l'action. La quatrième est la somme pondérée par π(a ∣ s) : elle fait la moyenne des actions que la politique peut choisir, et le résultat est V(s). Les deux sommes sont des moyennes, à poids positifs de somme 1 : le résultat reste toujours entre la plus petite et la plus grande branche, la formule n'invente aucune valeur. On écrit la valeur sous forme récursive plutôt que comme une somme sur tous les chemins parce que le nombre de chemins croît de façon exponentielle avec l'horizon, alors que V(s′) résume en un seul nombre tout l'avenir depuis s′. On multiplie par γ à chaque pas plutôt que de retirer un coût fixe parce que cette multiplication répétée donne le poids γᵏ au pas k : une décroissance géométrique qui rend finie la somme infinie (démonstration 2) et qui fait converger le calcul (démonstration 4). Enfin, V figure à droite parce que la valeur d'aujourd'hui dépend de celle de demain : la formule écrite pour chaque état forme un système d'équations (démonstration 3), que l'on résout d'un coup ou par passes successives. Pour un développeur Java/Spring, V(s′) joue le rôle d'un résultat mis en cache (`@Cacheable`) : calculé une fois par état, il est réutilisé par tous les états qui y mènent, au lieu de recalculer chaque chemin.

**Petit film chiffré** (exemple simple ci-dessous, γ = 0,9). On suit les deux branches à travers les quatre opérations.

| Opération | Branche A (fin) | Branche B (vers s₂) |
|---|---|---|
| valeur de l'état d'arrivée V(s′) | 0 | 5 |
| × γ | 0,9 × 0 = 0 | 0,9 × 5 = 4,5 |
| + R | 1 + 0 = 1 | 0 + 4,5 = 4,5 |
| × P(s′ ∣ s, a) = 1, donc Q | 1 | 4,5 |
| × π(a ∣ s) = 0,5 | 0,5 | 2,25 |
| somme sur les actions | 0,5 + 2,25 = 2,75 | |

La branche B, qui ne rapporte rien tout de suite, apporte 2,25 des 2,75 points : c'est la valeur de l'avenir, rapetissée une fois par γ.

## Démonstration 1 — D'où vient l'équation

**Ce qu'on démontre.** On fixe la politique π, on suppose l'environnement markovien (la loi de l'état suivant ne dépend que de l'état et de l'action présents) et l'on définit V(s) comme l'espérance du retour quand on part de s. Alors V vérifie la formule :

$$
V(s) = \mathbb{E}\left[ G_t \mid S_t = s \right] \quad\Longrightarrow\quad V(s) = \sum_{a} \pi(a \mid s) \sum_{s'} P(s' \mid s, a) \left[ R + \gamma\, V(s') \right]
$$

**L'idée.** Le retour d'aujourd'hui est la première récompense plus γ fois le retour de demain. En moyenne, « le retour de demain quand on se trouve en s′ » est exactement V(s′) : la même définition, un pas plus tard. Il reste à organiser la moyenne en deux étages, d'abord sur l'action, puis sur l'état d'arrivée.

**La preuve, pas à pas.**

**Étape 1.** On met γ en facteur dans tous les termes du retour sauf le premier, parce que chacun de ces termes contient au moins une fois γ ; la parenthèse a la forme du retour, décalée d'un pas :

$$
G_t = R_{t+1} + \gamma R_{t+2} + \gamma^2 R_{t+3} + \dots = R_{t+1} + \gamma \left( R_{t+2} + \gamma R_{t+3} + \dots \right) = R_{t+1} + \gamma\, G_{t+1}
$$

**Étape 2.** On prend l'espérance sachant Sₜ = s, parce que c'est la définition de V(s) ; l'espérance d'une somme est la somme des espérances (linéarité, fiche 22) :

$$
V(s) = \mathbb{E}\left[ R_{t+1} \mid S_t = s \right] + \gamma\, \mathbb{E}\left[ G_{t+1} \mid S_t = s \right]
$$

**Étape 3.** On découpe chaque espérance selon l'action a, tirée avec la probabilité π(a ∣ s), puis selon l'état suivant s′, tiré avec la probabilité P(s′ ∣ s, a), parce que c'est la loi de l'espérance totale : une moyenne globale est la moyenne pondérée des moyennes par cas. Pour toute quantité aléatoire X :

$$
\mathbb{E}\left[ X \mid S_t = s \right] = \sum_{a} \pi(a \mid s) \sum_{s'} P(s' \mid s, a)\; \mathbb{E}\left[ X \mid S_t = s,\, A_t = a,\, S_{t+1} = s' \right]
$$

**Étape 4.** Sachant (s, a, s′), la récompense vaut R(s, a, s′), et le retour futur ne dépend plus que de s′, parce que l'environnement est markovien et que π ne change pas avec le temps :

$$
\mathbb{E}\left[ G_{t+1} \mid S_t = s,\, A_t = a,\, S_{t+1} = s' \right] = \mathbb{E}\left[ G_{t+1} \mid S_{t+1} = s' \right] = V(s')
$$

**Étape 5.** On applique l'étape 3 avec X = Rₜ₊₁ puis X = Gₜ₊₁, on remplace grâce à l'étape 4, et l'on regroupe les deux termes sous les mêmes sommes, parce qu'ils ont les mêmes poids π(a ∣ s) P(s′ ∣ s, a) : on obtient exactement la formule. ∎

**Vérification chiffrée.** Dans l'exemple simple (A : récompense 1 puis fin ; B : 0 puis s₂ qui rapporte 5 ; π = 0,5 ; γ = 0,9), il n'y a que deux trajectoires. Par A, G = 1 ; par B, G = 0 + 0,9 × 5 = 4,5. La moyenne des retours vaut 0,5 × 1 + 0,5 × 4,5 = 2,75, la valeur que donne la formule. Le programme tire 20 000 épisodes, avec une graine fixée, et trouve un retour moyen de 2,7481, à 0,0019 de 2,75. **Contre-exemple quand l'hypothèse de Markov manque.** Supposons que l'étiquette s₂ regroupe deux situations : l'usager arrivé par B, qui rapporte 5, et l'usager arrivé par un autre canal, qui ne rapporte que 1, aussi fréquentes l'une que l'autre. La « valeur » estimée de s₂ est alors la moyenne 3, et la formule donne Q(B) = 0,9 × 3 = 2,7 au lieu du vrai 0,9 × 5 = 4,5 : une erreur de 1,8 point, parce que l'étape 4 est fausse pour cet état.

**Ce que la preuve révèle du mécanisme.** L'équation repose sur deux faits seulement : le retour se replie sur lui-même (étape 1), et l'état présent suffit à prédire la suite (étape 4). La récompense et l'avenir d'une branche sont multipliés par la même probabilité, parce qu'ils appartiennent à la même branche. Quand l'état oublie une information utile, la formule reste calculable, mais elle calcule la valeur d'un mélange de situations, et non celle de la situation réelle.

**Conséquence pour un agent.** Avant d'écrire un MDP, on vérifie que l'état contient tout ce qui change la suite : canal d'arrivée, nombre de relances déjà faites, budget restant. Sinon, on découpe l'état. Le test pratique est celui du contre-exemple : deux dossiers qui ont le même état doivent avoir le même avenir moyen.

## Démonstration 2 — Un seul état qui boucle : une série géométrique

**Ce qu'on démontre.** Un état qui rapporte r à chaque pas et revient sur lui-même avec la probabilité 1 a pour valeur, si 0 ≤ γ < 1 :

$$
V = \frac{r}{1 - \gamma} = r \left( 1 + \gamma + \gamma^2 + \dots \right)
$$

Si γ = 1 et r ≠ 0, aucune valeur finie n'existe.

**L'idée.** L'état est son propre successeur : la formule devient une équation à une seule inconnue. On retrouve la même valeur en additionnant une à une les récompenses remisées, parce que c'est la définition même du retour.

**La preuve, pas à pas.**

**Étape 1.** Il n'y a qu'une action, de probabilité π = 1, et un seul état d'arrivée, de probabilité P = 1 ; chaque somme n'a donc qu'un terme, de poids 1 :

$$
V = 1 \times 1 \times \left[ r + \gamma V \right] = r + \gamma V
$$

**Étape 2.** On regroupe les V à gauche, puis on divise par 1 − γ, ce qui est permis parce que 1 − γ > 0 :

$$
V - \gamma V = r \quad\Longrightarrow\quad V = \frac{r}{1 - \gamma}
$$

**Étape 3.** On contrôle avec la somme Sₙ des n premiers termes : on la multiplie par γ et on soustrait, parce que tous les termes intermédiaires se compensent :

$$
S_n = r \left( 1 + \gamma + \dots + \gamma^{n-1} \right), \qquad S_n - \gamma S_n = r \left( 1 - \gamma^n \right), \qquad S_n = r\, \frac{1 - \gamma^n}{1 - \gamma}
$$

**Étape 4.** Comme 0 ≤ γ < 1, γⁿ tend vers 0, donc Sₙ tend vers r/(1 − γ) : les deux calculs concordent. Si γ = 1, Sₙ = n × r grandit sans limite, et l'équation V = r + V n'a aucune solution finie. ∎

**Vérification chiffrée.** Avec r = 1 et γ = 0,9 : V = 1/0,1 = 10. Sommes partielles : S₁₀ = (1 − 0,9¹⁰)/0,1 = (1 − 0,3487)/0,1 = 6,5132 et S₂₂ = (1 − 0,9²²)/0,1 = (1 − 0,0985)/0,1 = 9,0152. Après 10 pas, on n'a encore que 65 % de la valeur ; après 22 pas, 90 %. **Contre-exemple avec γ = 1 :** S₁₀ = 10, S₁₀₀ = 100, et la somme de 1 000 termes vaut 1 000 ; elle ne s'arrête jamais.

**Ce que la preuve révèle du mécanisme.** Le facteur 1/(1 − γ) est un multiplicateur : il dit combien de « pas pleins » la valeur additionne. C'est l'horizon effectif : 10 pas à γ = 0,9, 100 pas à γ = 0,99. Une récompense placée à 1/(1 − γ) pas ne pèse plus qu'au plus e⁻¹ ≈ 0,3679 de son montant (leçon, point 6) : à γ = 0,9, 0,9¹⁰ = 0,3487.

**Conséquence pour un agent.** On choisit γ pour que 1/(1 − γ) couvre la durée utile de la tâche, et pas beaucoup plus : un horizon trop long gonfle les valeurs et ralentit la convergence. La valeur γ = 1 n'est permise que si chaque épisode se termine (ticket clos, sinistre réglé).

## Démonstration 3 — Un système linéaire à solution unique

**Ce qu'on démontre.** On considère un nombre fini d'états non terminaux (un état terminal vaut 0 et sort du calcul), une politique fixée et γ < 1. On définit la récompense immédiate moyenne et la matrice de transition sous π :

$$
r_\pi(s) = \sum_{a} \pi(a \mid s) \sum_{s'} P(s' \mid s, a)\, R(s, a, s'), \qquad P_\pi(s, s') = \sum_{a} \pi(a \mid s)\, P(s' \mid s, a)
$$

Alors la formule, écrite pour chaque état, est le système suivant, et ce système a une solution unique :

$$
(I - \gamma P_\pi)\, V = r_\pi
$$

**L'idée.** La formule est linéaire en V : V n'y est multiplié que par des nombres connus. Une équation par état et une inconnue par état : c'est un système carré. Il a une solution unique dès que le système sans second membre n'a que la solution nulle, et la remise γ < 1 force exactement cela.

**La preuve, pas à pas.**

**Étape 1.** On distribue les sommes de la formule, parce que la multiplication se distribue sur l'addition : la partie en R donne rπ(s) et la partie en V donne γ fois une somme pondérée par Pπ :

$$
V(s) = r_\pi(s) + \gamma \sum_{s'} P_\pi(s, s')\, V(s')
$$

**Étape 2.** On passe à gauche tout ce qui contient V ; en écriture matricielle, avec I la matrice identité, c'est le système (I − γPπ)V = rπ.

**Étape 3.** On suppose (I − γPπ)x = 0, c'est-à-dire x = γPπx, et l'on note m la plus grande valeur de |x(s)|, atteinte en un état s*. Chaque ligne de Pπ a des coefficients ≥ 0 de somme au plus 1, donc, par l'inégalité triangulaire :

$$
m = \lvert x(s^{*}) \rvert = \gamma \left| \sum_{s'} P_\pi(s^{*}, s')\, x(s') \right| \le \gamma \sum_{s'} P_\pi(s^{*}, s')\, m \le \gamma\, m
$$

**Étape 4.** On en tire (1 − γ) m ≤ 0 ; comme 1 − γ > 0 et m ≥ 0, m = 0, donc x = 0. Une matrice carrée dont le noyau est réduit à 0 est inversible, donc V = (I − γPπ)⁻¹ rπ est l'unique solution. ∎

**Vérification chiffrée.** Les tickets du cas 1 : états non terminaux N et A, l'état résolu R vaut 0. Récompenses immédiates moyennes : rπ(N) = 0,6 × 10 + 0,4 × (−2) = 6 − 0,8 = 5,2 et rπ(A) = 0,7 × 8 + 0,3 × (−1) = 5,6 − 0,3 = 5,3. Transitions entre non-terminaux : Pπ(N, A) = 0,4 et Pπ(A, A) = 0,3, les autres sont nulles. Avec γ = 0,9 : γ × 0,4 = 0,36 et γ × 0,3 = 0,27, d'où le système :

$$
V(N) - 0{,}36\, V(A) = 5{,}2, \qquad (1 - 0{,}27)\, V(A) = 5{,}3
$$

La seconde équation donne V(A) = 5,3/0,73 ≈ 7,26027, puis la première V(N) = 5,2 + 0,36 × 7,26027 = 5,2 + 2,6137 ≈ 7,81370. Le programme résout le même système par élimination de Gauss et retrouve ces valeurs. **Contre-exemple avec γ = 1 :** un état qui boucle sur lui-même avec la probabilité 1 donne la matrice 1 − 1 × 1 = 0, singulière, et le programme lève `ValueError` ; avec r = 1, l'équation 0 × V = 1 n'a aucune solution.

**Ce que la preuve révèle du mécanisme.** L'inverse se développe en une série qui compte les visites :

$$
(I - \gamma P_\pi)^{-1} = I + \gamma P_\pi + \gamma^2 P_\pi^2 + \dots
$$

Le coefficient (s, s′) de cette somme est le nombre moyen de visites de s′ en partant de s, chaque visite remisée par γ autant de fois qu'elle a de pas de retard. V(s) est donc la somme des récompenses moyennes de chaque état, pondérées par ces visites actualisées. Plus une boucle est probable et plus γ est proche de 1, plus la matrice est proche d'être singulière, et plus les valeurs sont grandes et sensibles.

**Conséquence pour un agent.** Pour un MDP de quelques centaines d'états, l'outil déterministe que l'agent appelle résout le système exactement, par élimination de Gauss en O(|S|³), au lieu d'itérer. Pour un MDP plus grand, on itère (démonstration 4). Si l'outil signale une matrice singulière, c'est le signe d'une boucle fermée sans remise : une erreur de modélisation à corriger, pas à contourner par un petit epsilon.

## Démonstration 4 — L'évaluation itérative converge, l'erreur est multipliée par γ à chaque passe

**Ce qu'on démontre.** On part de n'importe quelle estimation V₀ et on applique la formule en boucle, Vₖ₊₁ = rπ + γPπVₖ. Alors, pour tout k :

$$
\max_s \lvert V_k(s) - V(s) \rvert \le \gamma^k \max_s \lvert V_0(s) - V(s) \rvert
$$

**L'idée.** La vraie valeur V vérifie la même formule. En soustrayant, les récompenses s'annulent et il ne reste que l'erreur, multipliée par γPπ. Or Pπ fait des moyennes, qui ne grossissent pas une erreur, et γ la rétrécit.

**La preuve, pas à pas.**

**Étape 1.** On soustrait V = rπ + γPπV (démonstration 3) de Vₖ₊₁ = rπ + γPπVₖ ; rπ disparaît, parce qu'il est le même des deux côtés. Avec l'erreur eₖ = Vₖ − V :

$$
e_{k+1} = \gamma\, P_\pi\, e_k
$$

**Étape 2.** Chaque coordonnée de Pπeₖ est une somme de coordonnées de eₖ à poids ≥ 0 de somme au plus 1, donc, par l'inégalité triangulaire, elle vaut au plus max|eₖ| en valeur absolue :

$$
\max_s \lvert e_{k+1}(s) \rvert \le \gamma \max_s \lvert e_k(s) \rvert
$$

**Étape 3.** On applique l'étape 2 k fois de suite (récurrence) : max|eₖ| ≤ γᵏ max|e₀|. Comme γᵏ tend vers 0, Vₖ tend vers V depuis n'importe quel départ. ∎

**Vérification chiffrée.** Tickets, départ V₀ = 0 : l'erreur initiale vaut max(7,81370 ; 7,26027) = 7,8137. Passe 1 : V₁(N) = 0,6 × 10 + 0,4 × (−2 + 0) = 5,2 et V₁(A) = 0,7 × 8 + 0,3 × (−1 + 0) = 5,3 ; erreur maximale 7,8137 − 5,2 = 2,6137. Passe 2 : 0,9 × 5,3 = 4,77 ; V₂(N) = 6 + 0,4 × (−2 + 4,77) = 6 + 1,108 = 7,108 et V₂(A) = 5,6 + 0,3 × (−1 + 4,77) = 5,6 + 1,131 = 6,731 ; erreur 7,8137 − 7,108 = 0,7057. Passe 3 : erreur 0,19054. Passe 10 : erreur 0,00002. La borne γ¹⁰ × 7,8137 = 0,3487 × 7,8137 = 2,7245 est respectée, mais de très loin. L'explication tient dans l'étape 1 : l'erreur sur A est multipliée à chaque passe par γ × 0,3 = 0,27, et non par 0,9, parce que A ne revient sur lui-même que trois fois sur dix ; l'erreur sur N vaut 0,36 fois l'erreur précédente sur A. Le programme vérifie que, dès la passe 1, chaque erreur vaut exactement 0,27 fois la précédente (2,6137 × 0,27 = 0,7057). **Contre-exemple avec γ = 1 :** sur l'état qui boucle avec r = 1, l'itération donne Vₖ = k, soit 1, 2, 3… et ne converge pas.

**Ce que la preuve révèle du mécanisme.** γ est le facteur du pire cas, atteint quand l'agent ne quitte jamais les états non terminaux. Le vrai facteur est γ multiplié par la probabilité de rester dans le système : une tâche qui se termine souvent converge beaucoup plus vite que la borne. Comme la borne vaut depuis n'importe quel V₀, on peut repartir des valeurs de la veille (démarrage à chaud) : la convergence n'en est que plus rapide.

**Conséquence pour un agent.** Le critère d'arrêt se règle sur la garantie : si deux passes diffèrent d'au plus ε, l'erreur restante vaut au plus γε/(1 − γ) (leçon, point 4). Pour garantir une erreur de 0,01 à γ = 0,9, il faut donc s'arrêter quand l'écart entre deux passes passe sous ε = 0,1 × 0,01/0,9 ≈ 0,0011, et non sous 0,01.

## Démonstration 5 — Bornes et monotonie des valeurs

**Ce qu'on démontre.** (a) Si toutes les récompenses vérifient |R| ≤ Rₘₐₓ, alors pour tout état :

$$
\lvert V(s) \rvert \le \frac{R_{\max}}{1 - \gamma}
$$

(b) Si l'on augmente des récompenses sans toucher ni à π ni aux transitions, aucune valeur ne baisse : r′π ≥ rπ état par état entraîne V′ ≥ V état par état.

**L'idée.** (a) Le retour le plus grand possible est Rₘₐₓ à chaque pas, pour toujours : c'est la série géométrique de la démonstration 2. (b) V est une somme de récompenses à poids positifs (les visites actualisées de la démonstration 3) ; augmenter un terme qui a un poids positif ne peut pas faire baisser la somme.

**La preuve, pas à pas.**

**Étape 1.** On note M = maxₛ |V(s)|. Dans la formule, chaque crochet vérifie |R + γV(s′)| ≤ Rₘₐₓ + γM, et une moyenne de nombres bornés par Rₘₐₓ + γM est bornée de la même façon ; en l'écrivant pour l'état où |V| atteint M, on obtient M ≤ Rₘₐₓ + γM.

**Étape 2.** On regroupe les M à gauche et on divise par 1 − γ > 0 :

$$
M - \gamma M \le R_{\max} \quad\Longrightarrow\quad M \le \frac{R_{\max}}{1 - \gamma}
$$

**Étape 3.** Pour (b), on pose d = V′ − V et on soustrait les deux systèmes de la démonstration 3, qui ont la même matrice parce que π et les transitions sont inchangés :

$$
d = (r'_\pi - r_\pi) + \gamma P_\pi\, d
$$

**Étape 4.** On calcule d par itération depuis d₀ = 0, ce qui converge d'après la démonstration 4. Chaque passe ajoute un vecteur ≥ 0, r′π − rπ, à γPπ fois un vecteur ≥ 0, qui est ≥ 0 parce que les coefficients de Pπ sont ≥ 0 ; chaque itéré est donc ≥ 0, et leur limite d aussi. ∎

**Vérification chiffrée.** (a) Tickets : Rₘₐₓ = 10, la borne vaut 10/(1 − 0,9) = 100, et V(N) = 7,8137 ≤ 100. La borne est lâche parce que les tickets se ferment vite ; elle est atteinte par l'état qui boucle de la démonstration 2 (r = 1, V = 1/0,1 = 10). (b) On porte la récompense d'une relance réussie de 8 à 9 : rπ(A) = 0,7 × 9 + 0,3 × (−1) = 6, V(A) = 6/0,73 = 8,21918 ≥ 7,26027 et V(N) = 5,2 + 0,36 × 8,21918 = 8,15890 ≥ 7,81370. Le gain sur V(N), 0,34521, est la hausse de rπ(A), 0,7 × 1 = 0,7, multipliée par les visites actualisées de A depuis N, 0,36/(1 − 0,27) = 0,36/0,73 = 0,49315 : 0,7 × 0,49315 = 0,34521. **Contre-exemple si les transitions changent :** on monte la récompense d'une réponse réussie depuis N de 10 à 11, mais la réponse, plus expéditive, ne réussit plus qu'une fois sur deux. Alors V(N) = 0,5 × 11 + 0,5 × (−2 + 0,9 × 7,26027) = 5,5 + 2,26712 = 7,76712 < 7,81370 : la valeur baisse malgré une récompense plus haute, parce que Pπ a changé et que (b) ne s'applique plus.

**Ce que la preuve révèle du mécanisme.** V = (I − γPπ)⁻¹ rπ : chaque récompense moyenne d'état est multipliée par le nombre de visites actualisées de cet état. Une récompense dans un état très visité (une boucle) pèse lourd ; une récompense dans un état rare pèse peu. La borne (a) se lit comme « Rₘₐₓ fois l'horizon effectif ».

**Conséquence pour un agent.** Un garde-fou simple en production : toute valeur calculée dont la valeur absolue dépasse Rₘₐₓ/(1 − γ) trahit un bug (probabilités qui ne somment pas à 1, γ mal saisi). Et pour changer le comportement de l'agent par les récompenses, on agit d'abord sur les états très visités, où l'effet est le plus fort, en vérifiant que la retouche ne modifie pas aussi les transitions.

## Démonstration 6 — Sensibilité à γ : de combien bouge V si γ change de 1 %

**Ce qu'on démontre.** Pour l'état qui boucle, V(γ) = r/(1 − γ), sa dérivée et son élasticité (variation relative de V pour une variation relative de γ) valent :

$$
\frac{dV}{d\gamma} = \frac{r}{(1 - \gamma)^2}, \qquad \frac{\gamma}{V}\,\frac{dV}{d\gamma} = \frac{\gamma}{1 - \gamma}
$$

Une petite hausse relative δ de γ fait donc monter V d'environ γ/(1 − γ) × δ en relatif.

**L'idée.** Plus l'horizon est long, plus γ se multiplie par lui-même de fois, et plus une petite retouche de γ se propage loin. L'élasticité vaut exactement l'horizon effectif moins 1, puisque γ/(1 − γ) = 1/(1 − γ) − 1.

**La preuve, pas à pas.**

**Étape 1.** On dérive r × (1 − γ)⁻¹ par rapport à γ ; la dérivée de u⁻¹ est −u⁻² × u′, et ici u = 1 − γ a pour dérivée −1, d'où :

$$
\frac{dV}{d\gamma} = r \times \left( -(1 - \gamma)^{-2} \right) \times (-1) = \frac{r}{(1 - \gamma)^2}
$$

**Étape 2.** On multiplie par γ/V = γ(1 − γ)/r, parce que c'est la définition de l'élasticité, et l'on simplifie par r et par (1 − γ) :

$$
\frac{\gamma}{V}\,\frac{dV}{d\gamma} = \frac{\gamma (1 - \gamma)}{r} \times \frac{r}{(1 - \gamma)^2} = \frac{\gamma}{1 - \gamma}
$$

**Étape 3.** Au premier ordre, ΔV/V ≈ γ/(1 − γ) × Δγ/γ, parce qu'une dérivée est la pente de la meilleure approximation linéaire au voisinage du point. ∎

**Vérification chiffrée.** À γ = 0,9, l'élasticité vaut 0,9/0,1 = 9. Une hausse de 1 % porte γ à 0,909 : V = 1/(1 − 0,909) = 1/0,091 = 10,98901, soit +9,890 % ; l'approximation annonçait +9 %, l'écart vient de la courbure de 1/(1 − γ). Sur les tickets, la même hausse donne V(A) = 5,3/(1 − 0,909 × 0,3) = 5,3/0,7273 = 7,28723 et V(N) = 7,84964, soit +0,460 % seulement : la tâche se termine vite, γ y pèse peu. À γ = 0,99, l'élasticité vaut 99 : une hausse de 0,5 % (0,99 → 0,99495) suffit à faire passer la valeur de la boucle de 100 à 1/0,00505 = 198,02.

**Ce que la preuve révèle du mécanisme.** La sensibilité explose quand γ s'approche de 1, au rythme de l'horizon effectif. Les états d'où l'on sort vite sont presque insensibles à γ ; ceux qui bouclent longtemps y sont très sensibles.

**Conséquence pour un agent.** γ est un paramètre métier écrit et justifié, pas une valeur par défaut. Pour une tâche longue, on vérifie que la décision ne change pas quand γ bouge de ±0,01 ; si elle change, la décision dépend d'un choix de modélisation, et elle remonte à un humain.

## Exemple simple, à la main

Depuis s, la politique joue l'outil A ou l'outil B avec probabilité 0,5. A rapporte 1 et termine. B ne rapporte rien mais mène à un état s₂ dont l'unique action rapporte 5 et termine. γ = 0,9. On calcule d'abord les états les plus proches de la fin, parce que leur valeur ne dépend que d'états terminaux, qui valent 0.

**Étape 1.** V(s₂) = 5 + 0,9 × 0 = 5 : une seule action, une seule issue, terminale.

**Étape 2.** Q(A) = 1 + 0,9 × 0 = 1 : l'outil A termine.

**Étape 3.** Q(B) = 0 + 0,9 × 5 = 4,5 : rien tout de suite, puis la valeur de s₂ rapetissée une fois.

**Étape 4.** V(s) = 0,5 × 1 + 0,5 × 4,5 = 0,5 + 2,25 = 2,75.

$$
V(s_2) = 5, \qquad Q(A) = 1, \qquad Q(B) = 0 + 0{,}9 \times 5 = 4{,}5
$$

$$
V(s) = 0{,}5 \times 1 + 0{,}5 \times 4{,}5 = 2{,}75
$$

| Quantité | Calcul | Valeur |
|---|---|---|
| V(s₂) | 5 + 0,9 × 0 | 5 |
| Q(s, A) | 1 + 0,9 × 0 | 1 |
| Q(s, B) | 0 + 0,9 × 5 | 4,5 |
| part de A | 0,5 × 1 | 0,5 |
| part de B | 0,5 × 4,5 | 2,25 |
| V(s) | 0,5 + 2,25 | 2,75 |

Remarque : une politique gloutonne jouerait toujours B et vaudrait max(1 ; 4,5) = 4,5 > 2,75. Évaluer une politique (cette formule) n'est pas l'optimiser (l'équation d'optimalité de la leçon, point 5, remplace la moyenne sur π par un maximum).

## Cas d'usage complexes, démontrés

Les probabilités, récompenses et volumes des quatre cas sont illustratifs. Les récompenses sont des points fixés et validés par l'équipe métier, parce que l'agent optimisera exactement ce qui est écrit.

### Cas 1 — Entité de services publics en ligne [PUBLIC] : relancer un ticket en attente ou le passer à un humain

**Contexte.** Une entité de services publics en ligne, accessible par UAE Pass, reçoit en arabe et en anglais des demandes de support : renouvellement de documents, paiement de frais. Un agent répond à chaque nouveau ticket ; s'il manque une pièce, le ticket passe « en attente » et l'agent relance l'usager. Question : faut-il continuer à relancer les tickets en attente, ou les transférer à un agent humain ? Volume illustratif : 12 000 tickets par mois, dont 40 % passent en attente.

**Données.**

- États : N (nouveau), A (en attente), R (résolu, terminal, valeur 0) ; γ = 0,9 par échange.
- Depuis N, réponse : résolu avec la probabilité 0,6 (récompense 10) ; sinon passage en A (récompense −2, un aller-retour pour l'usager).
- Depuis A, relance : résolu avec la probabilité 0,7 (récompense 8) ; sinon le ticket reste en A (récompense −1).
- Depuis A, transfert à un humain : résolution certaine, récompense 8 − 1,5 = 6,5 (1,5 point de temps d'agent ; 1 point ≈ 10 AED).
- Volume : 12 000 tickets par mois, 40 % en attente.

**Calcul pas à pas.**

**Étape 1.** On écrit Bellman pour A, qui ne dépend que de lui-même, et on isole V(A) (arrondi à 5 décimales) :

$$
V(A) = 0{,}7 \times 8 + 0{,}3 \times \big(-1 + 0{,}9\, V(A)\big) = 5{,}3 + 0{,}27\, V(A) \quad\Longrightarrow\quad 0{,}73\, V(A) = 5{,}3 \quad\Longrightarrow\quad V(A) \approx 7{,}26027
$$

**Étape 2.** On écrit Bellman pour N, avec V(A) connu (0,9 × 7,26027 − 2 = 4,53425) :

$$
V(N) = 0{,}6 \times 10 + 0{,}4 \times \big(-2 + 0{,}9 \times 7{,}26027\big) = 6 + 0{,}4 \times 4{,}53425 \approx 7{,}81370
$$

**Étape 3.** On vérifie par passes successives depuis V = 0 (démonstration 4) : V(N) vaut 5,2 ; 7,108 ; 7,62316 après 1, 2 et 3 passes, puis 7,81368 après 10 passes, la solution exacte au millième près.

**Étape 4.** On compare les deux actions en A : relancer vaut V(A) = 7,26027, transférer vaut 6,5 ; l'écart est de 7,26027 − 6,5 = 0,76027 point par ticket en attente.

**Décision de l'agent.** Le seuil est la valeur du transfert : on relance tant que V(A) > 6,5. Ici 7,26027 > 6,5, donc l'agent continue de relancer. Un ticket en attente vaut encore 7,26, à peine moins qu'un ticket neuf (7,81) : la relance fonctionne, et ce qui coûte, ce sont les allers-retours (−2 et −1). Si l'entité veut plafonner le nombre de relances, il faut ajouter ce nombre à l'état, sinon l'état n'est plus markovien (démonstration 1).

**Contre-calcul.** Un calcul naïf qui s'arrête à une passe, en traitant l'échec de la relance comme une fin, oublie la valeur future de l'attente : il obtient V(A) = 0,7 × 8 + 0,3 × (−1) = 5,3 < 6,5 et conclut au transfert systématique. Résultat : 12 000 × 0,4 = 4 800 tickets par mois envoyés à un humain sans nécessité, et une valeur perdue de 4 800 × 0,76027 × 10 ≈ 36 493 AED par mois (illustratif).

**Sensibilité.** En fonction du taux de réussite p de la relance, l'étape 1 donne :

$$
V(A) = \frac{8p - (1 - p)}{1 - 0{,}9\,(1 - p)} = \frac{9p - 1}{0{,}1 + 0{,}9\,p}
$$

La valeur de bascule vérifie V(A) = 6,5 : 9p − 1 = 0,65 + 5,85p, soit 3,15p = 1,65 et p = 0,5238. Une baisse de 10 % du taux (0,7 → 0,63) donne V(A) = (5,67 − 1)/(0,1 + 0,567) = 4,67/0,667 = 7,00150 : la décision tient.

**En production.** Indicateur : le taux de réussite des relances, mesuré chaque semaine ; alerte sous 0,55, encore au-dessus de la bascule 0,5238, pour laisser le temps de réagir. On suit aussi le nombre moyen de relances par ticket en attente, 1/0,7 ≈ 1,43 dans ce modèle (fiche 22). Contrainte : la relance ne demande que la pièce manquante, jamais une donnée personnelle inutile (minimisation des données ; le régime applicable, PDPL ou règles propres à l'entité publique, est à confirmer avec le texte en vigueur), et elle part dans la langue choisie par l'usager, arabe ou anglais.

### Cas 2 — Banque de détail [BANQUE] : relancer ou rééchelonner un prêt en retard de 30 jours

**Contexte.** Une banque de détail de Dubaï confie à un agent la préparation des actions de recouvrement amiable sur les prêts personnels en retard de 30 jours (état R30). Deux actions sont possibles : la relance standard, gratuite, ou un rééchelonnement, qui abandonne des intérêts. Un conseiller valide chaque proposition. Volume illustratif : 400 dossiers par mois ; 1 point ≈ 10 AED de marge.

**Données.**

- γ = 0,9 par mois.
- Relance : régularisation avec la probabilité 0,5 (récompense +100, fin) ; sinon passage en retard de 60 jours, R60 (récompense 0).
- Rééchelonnement : coût 30 ; régularisation avec la probabilité 0,85 (récompense 100 − 30 = 70, fin) ; sinon R60 (récompense −30).
- Depuis R60, procédure de recouvrement : régularisation tardive avec la probabilité 0,25 (récompense +40), sinon passage en perte (récompense −280) ; les deux issues sont terminales.
- Client type : salaire 20 000 AED, mensualités existantes 6 500 AED, nouvelle mensualité rééchelonnée 3 200 AED ; durée restante 30 mois, allongée de 12 mois.

**Calcul pas à pas.**

**Étape 1.** Valeur de R60, dont les deux issues sont terminales :

$$
V(R_{60}) = 0{,}25 \times 40 + 0{,}75 \times (-280) = 10 - 210 = -200
$$

**Étape 2.** Valeur de la relance (0,5 × 0,9 × 200 = 90) :

$$
Q(R_{30}, \text{relancer}) = 0{,}5 \times (100 + 0{,}9 \times 0) + 0{,}5 \times \big(0 + 0{,}9 \times (-200)\big) = 50 - 90 = -40
$$

**Étape 3.** Valeur du rééchelonnement :

$$
Q(R_{30}, \text{rééchelonner}) = 0{,}85 \times 70 + 0{,}15 \times \big(-30 + 0{,}9 \times (-200)\big) = 59{,}5 + 0{,}15 \times (-210) = 59{,}5 - 31{,}5 = 28
$$

**Étape 4.** Contrôle réglementaire CBUAE de la proposition : ratio d'endettement total, toutes mensualités comprises, et durée du prêt personnel.

$$
\frac{6\,500 + 3\,200}{20\,000} = \frac{9\,700}{20\,000} = 0{,}485 \le 0{,}50, \qquad 30 + 12 = 42 \le 48
$$

**Décision de l'agent.** On rééchelonne si Q(rééchelonner) > Q(relancer), si le ratio total reste ≤ 50 % du salaire et si la durée reste ≤ 48 mois. Ici 28 > −40 et les deux contrôles passent : l'agent propose le rééchelonnement, que le conseiller valide. L'écart de 68 points par dossier vient presque entièrement de l'état suivant : la relance laisse une chance sur deux de tomber en R60, qui vaut −200.

**Contre-calcul.** La règle naïve « l'action la moins chère aujourd'hui » choisit la relance, qui ne coûte rien, et ignore la valeur −200 de l'état suivant. Elle perd 28 − (−40) = 68 points par dossier, soit 400 × 68 × 10 = 272 000 AED par mois (illustratif).

**Sensibilité.** Si la relance régularise avec la probabilité q, elle vaut 100q + 0,9 × (−200) × (1 − q) = 280q − 180, et elle ne passe devant que si 280q − 180 > 28, soit q > 208/280 = 0,7429. Dans l'autre sens, si le rééchelonnement réussit avec la probabilité s, il vaut 70s + (−210)(1 − s) = 280s − 210, et il reste meilleur tant que s > 170/280 = 0,6071. Enfin, en laissant V(R60) libre, les deux actions valent 50 + 0,45 V(R60) et 55 + 0,135 V(R60) ; elles s'égalent pour V(R60) = 5/0,315 = 15,87 : tant que le retard de 60 jours vaut moins que 15,87 points, le rééchelonnement gagne. Côté client, la mensualité rééchelonnée ne peut pas dépasser 0,5 × 20 000 − 6 500 = 3 500 AED.

**En production.** Indicateurs : le taux de régularisation à 90 jours de chaque action et le taux de passage en R60. Alerte si le taux de régularisation des relances dépasse 0,70 (la bascule 0,7429 approche) ou si celui des rééchelonnements tombe sous 0,65 (bascule 0,6071). Contrainte CBUAE, vérifiée par un outil déterministe avant toute proposition : toutes les mensualités du client, y compris la nouvelle, restent ≤ 50 % de son salaire (30 % pour un retraité), et un prêt personnel ne dépasse pas 48 mois.

### Cas 3 — Plateforme d'actifs virtuels agréée VARA [CRYPTO] : escalader une alerte de liquidité ou attendre une heure

**Contexte.** Une plateforme d'actifs virtuels agréée par la VARA fait surveiller par un agent la liquidité de ses portefeuilles chauds. Quand une alerte se déclenche (état L), l'agent peut escalader tout de suite à l'astreinte, ou attendre une heure et réévaluer. Si l'alerte persiste, l'agent se retrouve dans le même état L, donc devant la même décision : on évalue la politique « attendre tant que l'alerte persiste », qui forme une boucle. Volume illustratif : 600 alertes par mois.

**Données.**

- γ = 0,9 par heure.
- Escalader : récompense −2 (un opérateur mobilisé), fin.
- Attendre une heure : crise avec la probabilité c = 0,035 (récompense −50, retraits bloqués, fin) ; alerte résorbée avec la probabilité 1 − 0,035 − 0,2 = 0,765 (récompense 0, fin) ; alerte persistante avec la probabilité 0,2 (récompense −0,2 de surveillance, retour en L).
- Les poids −50 et −2 sont des poids de gravité fixés par l'équipe des risques, pas des pertes mesurées.
- Volume : 600 alertes par mois.

**Calcul pas à pas.**

**Étape 1.** Partie constante de la formule, la récompense immédiate moyenne de l'attente :

$$
b = 0{,}035 \times (-50) + 0{,}765 \times 0 + 0{,}2 \times (-0{,}2) = -1{,}75 - 0{,}04 = -1{,}79
$$

**Étape 2.** Facteur de boucle : la valeur future de L n'est atteinte que dans la branche « persiste », d'où γ × 0,2 = 0,18 :

$$
V(L) = b + 0{,}18\, V(L)
$$

**Étape 3.** Résolution comme dans la démonstration 2 (arrondi à 5 décimales) :

$$
V(L) = \frac{-1{,}79}{1 - 0{,}18} = \frac{-1{,}79}{0{,}82} \approx -2{,}18293
$$

**Étape 4.** Contrôle par passes (démonstration 4) : V₁ = −1,79 ; V₂ = −1,79 + 0,18 × (−1,79) = −1,79 − 0,3222 = −2,1122 ; V₃ = −1,79 + 0,18 × (−2,1122) = −2,1702. L'erreur est multipliée par 0,18 à chaque passe, et non par 0,9.

**Décision de l'agent.** Le seuil est la valeur de l'escalade, −2. Attendre vaut −2,18293 < −2 : l'agent escalade tout de suite.

**Contre-calcul.** Un agent qui ne fait qu'une passe traite « l'alerte persiste » comme une fin : il obtient V₁ = −1,79 > −2 et attend. Sous cette politique, la probabilité de finir en crise additionne les crises de chaque heure, c + 0,2c + 0,2²c + … = c/(1 − 0,2) = 0,035/0,8 = 0,04375, soit 600 × 0,04375 = 26,25 crises par mois, chacune avec des retraits bloqués.

**Sensibilité.** Valeur de bascule sur c : attendre et escalader s'égalent quand (−50c − 0,04)/0,82 = −2, soit 50c = 1,64 − 0,04 = 1,60 et c = 0,032. La décision est fragile : une baisse de 10 % de c (0,035 → 0,0315) donne b = −1,575 − 0,04 = −1,615 et V(L) = −1,615/0,82 = −1,96951 > −2, et l'agent attendrait. Sur γ, à c = 0,035 : V(L) = −1,79/(1 − 0,2γ) vaut −2 quand 1 − 0,2γ = 0,895, soit γ = 0,525 ; un agent myope, réglé sous 0,525, attendrait.

**En production.** Indicateur : la probabilité de crise par alerte, estimée sur une fenêtre glissante ; alerte dès qu'elle franchit 0,03, puisque la bascule est à 0,032. On suit aussi le délai entre la première alerte et la prise en charge. Contrainte : la VARA attend une gestion documentée du risque de liquidité et de la protection des avoirs des clients (à confirmer avec le règlement en vigueur) ; chaque décision est journalisée avec V(attendre), la valeur de l'escalade et l'estimation de c utilisée.

### Cas 4 — Agence immobilière [IMMO] : garder le loyer ou l'augmenter de 5 % au renouvellement

**Contexte.** Une agence de Dubaï gère pour des investisseurs un parc de 200 appartements loués (illustratif). À chaque renouvellement annuel du bail, enregistré dans Ejari, un agent propose de garder le loyer ou de l'augmenter de 5 %. Une hausse rapporte plus chaque année, mais fait partir plus de locataires, et une année de vacance coûte des mois de loyer et des frais. Les montants sont en milliers d'AED par an ; le loyer résidentiel est exonéré de TVA.

**Données.**

- États : O (occupé) et V (vacant) ; un pas = un an ; γ = 0,9.
- Garder : loyer 100 (100 000 AED par an) ; renouvellement avec la probabilité 0,85.
- Augmenter de 5 % : loyer 105 ; renouvellement avec la probabilité 0,75.
- Année vacante : récompense 60 (environ sept mois de loyer, après la vacance et les frais de remise en location), puis l'appartement est de nouveau occupé.
- Parc : 200 appartements.

**Calcul pas à pas.**

**Étape 1.** Système de la politique « garder » (démonstration 3) :

$$
V(O) = 100 + 0{,}9 \big( 0{,}85\, V(O) + 0{,}15\, V(V) \big), \qquad V(V) = 60 + 0{,}9\, V(O)
$$

**Étape 2.** On remplace V(V) dans la première équation : 0,9 × 0,85 = 0,765 ; 0,9 × 0,15 = 0,135 ; 0,135 × 60 = 8,1 ; 0,135 × 0,9 = 0,1215 ; 0,765 + 0,1215 = 0,8865.

$$
V(O) = 100 + 0{,}765\, V(O) + 8{,}1 + 0{,}1215\, V(O) \quad\Longrightarrow\quad (1 - 0{,}8865)\, V(O) = 108{,}1 \quad\Longrightarrow\quad V(O) = \frac{108{,}1}{0{,}1135} \approx 952{,}4229
$$

Puis V(V) = 60 + 0,9 × 952,4229 = 917,1806.

**Étape 3.** Même calcul pour « augmenter » : 0,9 × 0,75 = 0,675 ; 0,9 × 0,25 = 0,225 ; 0,225 × 60 = 13,5 ; 0,225 × 0,9 = 0,2025.

$$
(1 - 0{,}675 - 0{,}2025)\, V(O) = 105 + 13{,}5 \quad\Longrightarrow\quad V(O) = \frac{118{,}5}{0{,}1225} \approx 967{,}3469
$$

Puis V(V) = 60 + 0,9 × 967,3469 = 930,6122.

**Étape 4.** Écart : 967,3469 − 952,4229 = 14,924 milliers d'AED par appartement, en valeur actuelle ; sur le parc, 200 × 14,924 = 2 984,8 milliers d'AED.

**Décision de l'agent.** On propose la hausse si V(O) avec hausse dépasse V(O) sans hausse. 967,3469 > 952,4229 : l'agent propose la hausse de 5 %, dans la limite permise par l'indice des loyers de la RERA (plafond applicable à confirmer avec le texte en vigueur) ; le propriétaire décide.

**Contre-calcul.** Un calcul qui ignore la vacance compte un loyer perpétuel : 105/0,1 − 100/0,1 = 1 050 − 1 000 = 50 milliers d'AED de gain, plus de trois fois le vrai gain de 14,924. Plus grave, il conclut toujours à la hausse. Si le marché se détend et que le renouvellement après hausse tombe à 0,65, le vrai calcul donne :

$$
V(O) = \frac{105 + 0{,}9 \times 0{,}35 \times 60}{1 - 0{,}9 \times 0{,}65 - 0{,}81 \times 0{,}35} = \frac{123{,}9}{0{,}1315} \approx 942{,}2053 < 952{,}4229
$$

La hausse fait alors perdre 952,4229 − 942,2053 = 10,2176 milliers d'AED par appartement, soit 2 043,5 milliers d'AED (environ 2,04 millions d'AED) sur le parc.

**Sensibilité.** Avec la hausse, en fonction du taux de renouvellement q :

$$
V(O) = \frac{105 + 0{,}9\,(1 - q) \times 60}{1 - 0{,}9\,q - 0{,}81\,(1 - q)}
$$

La valeur de bascule, où cette valeur égale 952,4229, est q = 0,6924 (bissection dans le programme). Une baisse de 10 % du taux (0,75 → 0,675) suffit à renverser la décision : V(O) = (105 + 17,55)/(1 − 0,6075 − 0,26325) = 122,55/0,12925 = 948,1625 < 952,4229.

**En production.** Indicateur : le taux de renouvellement observé après une hausse, par immeuble et par trimestre ; alerte sous 0,72, au-dessus de la bascule 0,6924, pour garder une marge face à l'erreur d'estimation. On suit aussi la durée moyenne de vacance, qui fixe la récompense 60. Contraintes : chaque renouvellement est enregistré dans Ejari ; la hausse respecte l'indice des loyers de la RERA (à confirmer avec le texte en vigueur) ; le loyer résidentiel étant exonéré de TVA, les montants ne contiennent pas de TVA.

## Entraînement sur feuille A4

**Exercice 1.** Un état rapporte 2 à chaque pas et boucle sur lui-même, γ = 0,9. Calculer V.

**Exercice 2.** Reprendre l'exemple simple avec γ = 0,5.

**Exercice 3.** Dans le cas 1, recalculer V(A) si la relance réussit avec probabilité 0,9.

**Exercice 4.** Combien de passes faut-il, avec γ = 0,9, pour diviser l'erreur initiale par 1 000 ? (ln 1 000 ≈ 6,908 ; ln(1/0,9) ≈ 0,1054.)

**Exercice 5.** Démontrer que Gₜ = Rₜ₊₁ + γ Gₜ₊₁ à partir de la somme infinie.

**Exercice 6 (modifier une donnée).** Dans le cas 2, la relance régularise désormais 80 % des dossiers au lieu de 50 %. Recalculer Q(relancer) et donner la nouvelle décision.

**Exercice 7 (trouver l'erreur).** Un collègue écrit : « V(A) = 0,7 × 8 + 0,3 × (−1) + 0,9 V(A), donc 0,1 V(A) = 5,3 et V(A) = 53. » Trouver l'erreur, la corriger, et donner un test de bon sens qui l'aurait détectée.

**Exercice 8 (redémontrer de mémoire).** Redémontrer la démonstration 4 sans regarder, puis en déduire combien de passes il faut, dans le cas 3, pour que l'erreur partie de V₀ = 0 passe sous 0,001. (Facteur de boucle 0,18 ; ln 2 182,93 ≈ 7,688 ; ln(1/0,18) ≈ 1,7148.)

## Corrigé

**Exercice 1.** Démonstration 2 avec r = 2 : V = 2 + 0,9V, donc 0,1V = 2 et V = 2/(1 − 0,9) = 20.

**Exercice 2.** Q(A) = 1 + 0,5 × 0 = 1 ; Q(B) = 0 + 0,5 × 5 = 2,5 ; V(s) = 0,5 × 1 + 0,5 × 2,5 = 0,5 + 1,25 = 1,75. Un γ plus petit écrase la valeur de l'avenir, donc celle de B.

**Exercice 3.** V(A) = 0,9 × 8 + 0,1 × (−1 + 0,9 V(A)) = 7,2 − 0,1 + 0,09 V(A), donc 0,91 V(A) = 7,1 et V(A) ≈ 7,802. La formule de sensibilité du cas 1 donne la même chose : (9 × 0,9 − 1)/(0,1 + 0,81) = 7,1/0,91.

**Exercice 4.** On veut 0,9ᵏ ≤ 0,001. On prend le logarithme, fonction croissante : k ln 0,9 ≤ ln 0,001 ; on divise par ln 0,9 < 0, ce qui inverse l'inégalité : k ≥ ln 1 000 / ln(1/0,9) = 6,908/0,1054 ≈ 65,6, donc 66 passes.

**Exercice 5.** Gₜ = Rₜ₊₁ + γRₜ₊₂ + γ²Rₜ₊₃ + … Tous les termes à partir du deuxième contiennent γ : on le met en facteur, ce qui donne γ(Rₜ₊₂ + γRₜ₊₃ + …). La parenthèse a exactement la forme du retour, décalée d'un pas : c'est Gₜ₊₁ par définition.

**Exercice 6.** Q(relancer) = 0,8 × 100 + 0,2 × (0 + 0,9 × (−200)) = 80 − 36 = 44. Q(rééchelonner) ne dépend pas de q et vaut toujours 28. Comme 44 > 28, l'agent relance. C'est cohérent avec la bascule du cas 2 : 0,8 > 0,7429.

**Exercice 7.** L'erreur : 0,9 V(A) est ajouté hors de la branche « échec », comme si l'avenir était atteint avec la probabilité 1. Or on ne reste en A que dans 30 % des cas : la probabilité multiplie tout le crochet [R + γV(s′)]. Correction : V(A) = 0,7 × 8 + 0,3 × (−1 + 0,9 V(A)) = 5,3 + 0,27 V(A), donc 0,73 V(A) = 5,3 et V(A) ≈ 7,26027. Test de bon sens : V(A) est une moyenne de retours dont aucun ne dépasse 8 (la meilleure issue est une relance réussie tout de suite, et chaque échec retire 1 point) ; 53 est donc impossible, alors que 7,26 ≤ 8.

**Exercice 8.** Preuve : on soustrait V = rπ + γPπV de Vₖ₊₁ = rπ + γPπVₖ, d'où eₖ₊₁ = γPπeₖ ; une ligne de Pπ est une moyenne à poids ≥ 0 de somme au plus 1, donc max|eₖ₊₁| ≤ γ max|eₖ|, et par récurrence max|eₖ| ≤ γᵏ max|e₀|. Dans le cas 3, il n'y a qu'un état, et l'erreur est exactement multipliée par 0,18 : eₖ = 0,18ᵏ × 2,18293. On veut 0,18ᵏ × 2,18293 ≤ 0,001, soit k ≥ ln(2,18293/0,001)/ln(1/0,18) = 7,688/1,7148 ≈ 4,48, donc 5 passes. Contrôle : 0,18⁴ × 2,18293 ≈ 0,0023 > 0,001 et 0,18⁵ × 2,18293 ≈ 0,00041 ≤ 0,001.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`proche(x, y, tol)`** — Cette petite fonction est le vérificateur des poids et mesures qui tolère une poussière sur le plateau de la balance : elle reçoit deux nombres et une tolérance, un milliardième par défaut, mesure la valeur absolue de leur écart et renvoie vrai si cet écart ne dépasse pas la tolérance, faux sinon. Elle ne calcule rien de la théorie, mais elle permet aux `assert` de `main` et de `demo_2_boucle` de comparer deux flottants sans se laisser piéger par les arrondis de la machine, par exemple pour constater que V vaut bien 10 ou que Q(relancer) vaut bien −40.

**`passe(vN, vA, p_relance)`** — On l'imagine en employé du service de tickets qui refait, une fois de plus, ses comptes à partir des estimations de la veille : elle reçoit la valeur supposée d'un ticket nouveau N, celle d'un ticket en attente A, et la probabilité de réussite d'une relance, 0,7 par défaut. Elle applique une seule passe de Bellman, un nouveau ticket étant résolu avec la probabilité 0,6 pour 10 points, ou mis en attente pour −2 points plus γ fois V(A), un ticket en attente étant résolu par la relance pour 8 points ou restant en attente pour −1 point plus γ fois V(A), et renvoie le couple mis à jour : 5,2 et 5,3 au premier passage depuis zéro.

**`valeur_attente(p_relance, gamma)`** — Cette fonction est le notaire qui rédige d'un trait la valeur exacte d'un ticket en attente au lieu de la laisser converger : elle reçoit la probabilité de succès d'une relance et le facteur γ, 0,9 par défaut, refuse par une `ValueError` une probabilité hors de l'intervalle de 0 à 1, puis renvoie la solution de l'équation V = 8p + (1 − p)(−1 + γV), soit (8p − (1 − p))/(1 − γ(1 − p)). Elle vaut 7,26027 pour p = 0,7, 7,0015 pour p = 0,63 et 7,802 pour p = 0,9, et le cas 1 s'en sert pour comparer la relance au transfert vers un agent humain.

**`resoudre(M, b)`** — Celle-ci est le mécanicien patient qui démonte un système d'équations colonne après colonne : elle reçoit une matrice carrée et un second membre, les assemble en une matrice augmentée, puis, pour chaque colonne, choisit comme pivot la ligne de plus grande valeur absolue, lève une `ValueError` si ce pivot est quasi nul, la matrice étant alors singulière, échange les lignes et élimine la colonne dans toutes les autres lignes. Elle renvoie la solution x de M x = b, obtenue en divisant chaque dernier coefficient par le pivot de sa ligne, et c'est le moteur de `evaluer`.

**`evaluer(P, r, gamma)`** — Cette fonction est l'expert-comptable qui évalue une politique fixée d'un seul calcul, au lieu de la faire tourner sans fin : elle reçoit la matrice des transitions P de cette politique, le vecteur r des récompenses moyennes de chaque état et le facteur γ, construit la matrice I − γP en retranchant γ fois P de l'identité, puis demande à `resoudre` la solution du système (I − γP)V = r de la démonstration 3. Elle renvoie la liste des valeurs des états, et elle lève l'exception de `resoudre` quand le système n'a pas de solution unique, comme pour un état qui boucle sur lui-même avec γ = 1.

**`tickets_exact(gamma, gain_relance)`** — On y voit le chef de service qui veut le vrai prix de ses deux files de tickets : la fonction reçoit γ, 0,9 par défaut, et le gain d'une relance réussie, 8 par défaut, calcule les récompenses moyennes 5,2 pour un ticket nouveau et 5,3 pour un ticket en attente avec le gain par défaut, puis fixe les transitions vers l'attente, 0,4 depuis N et 0,3 depuis A, et confie le tout à `evaluer`. Elle renvoie le couple V(N), V(A), soit 7,81370 et 7,26027 dans le réglage de base, et les démonstrations 3, 5 et 6 l'appellent avec des réglages modifiés.

**`demo_1_retour()`** — Cette fonction joue le rôle d'un statisticien qui lance vingt mille fois la même partie pour voir si la moyenne retrouve l'équation : elle ne reçoit rien, fixe la graine du hasard à 9, puis, pour chaque épisode, tire à pile ou face entre l'outil A, qui rapporte 1 et termine, et l'outil B, qui rapporte 0 puis 5 un pas plus tard, soit 4,5 une fois actualisé. Elle imprime le retour moyen simulé, 2,7481 contre 2,75 pour Bellman, et la valeur Q(B), 4,5 d'ordinaire mais 2,7 si l'état s₂ mélange deux situations et n'est plus markovien, puis renvoie ces trois nombres.

**`demo_2_boucle()`** — Celle-ci raconte un état qui rapporte 1 à chaque pas et revient sans cesse sur lui-même, comme un moulin dont l'eau ne s'arrête jamais : elle ne reçoit rien, calcule la valeur exacte 1/(1 − 0,9) = 10, puis les sommes partielles de dix et de vingt-deux termes, 6,5132 et 9,0152, en vérifiant par un `assert` qu'elles égalent la formule de la série géométrique. Elle imprime aussi que 0,9 à la puissance 10, soit 0,3487, reste sous e⁻¹ = 0,3679, montrant qu'un horizon d'environ 1/(1 − γ) pas capte l'essentiel, et renvoie la valeur et les deux sommes.

**`demo_3_systeme()`** — Cette fonction est l'arbitre qui vérifie que le système linéaire donne bien la même valeur que les passes répétées : elle ne reçoit rien, demande à `tickets_exact` les valeurs 7,81370 et 7,26027, puis tente d'évaluer un état qui boucle sur lui-même avec γ = 1, cas où la matrice I − γP vaut zéro. L'exception levée par `resoudre` est attrapée et transformée en constat « matrice singulière = vrai », imprimé avec les deux valeurs ; la fonction renvoie V(N), V(A) et ce drapeau, que `main` compare à la solution calculée à la main.

**`demo_5_bornes()`** — On la voit en inspecteur qui pose des garde-fous autour des valeurs et mesure l'effet d'une amélioration : elle ne reçoit rien, calcule la borne 10/(1 − γ) = 100, qui majore toute valeur puisque aucune récompense ne dépasse 10, puis les valeurs des tickets quand une relance réussie rapporte 9 au lieu de 8, soit 8,21918 pour A et 8,1589 pour N. Elle calcule aussi les visites actualisées de A depuis N, 0,9 × 0,4/(1 − 0,9 × 0,3) = 0,49315, imprime ces résultats et renvoie la borne, les deux nouvelles valeurs, ces visites et la hausse de V(N), 0,34521, égale à 0,7 fois les visites.

**`demo_6_sensibilite()`** — Cette fonction est le sismographe qui mesure combien les valeurs tremblent quand on touche à γ : elle ne reçoit rien, calcule l'élasticité γ/(1 − γ) = 9 de la boucle simple, puis augmente γ de 1 %, à 0,909, et constate que la valeur de la boucle grimpe de 9,890 % alors que celle d'un ticket nouveau ne passe que de 7,81370 à 7,84964, soit 0,460 %. Elle imprime cette comparaison et renvoie l'élasticité, les deux hausses et la nouvelle valeur, montrant qu'un γ proche de 1 rend un état qui boucle très sensible au réglage.

**`cas_1_tickets_public()`** — Cette fonction raconte l'assistant d'un service public qui doit choisir, pour un ticket en attente, entre une relance automatique et un transfert à un agent humain qui vaut 6,5 points : elle ne reçoit rien, calcule V(A) = 7,26027 par `valeur_attente`, en déduit V(N) = 7,81370 et choisit de relancer, alors qu'un calcul naïf d'une seule passe, 5,3, oublie la boucle d'attente et transférerait. Elle chiffre l'erreur sur les 4 800 tickets qui passent en attente chaque mois, 36 493 AED, trouve la probabilité de bascule 0,5238 et la valeur 7,0015 quand la réussite tombe à 0,63, imprime le tout et le renvoie dans un dictionnaire.

**`cas_2_recouvrement_banque(q_relance, afficher)`** — On y suit une banque face à un prêt en retard de trente jours, qui hésite entre une simple relance et un rééchelonnement : la fonction reçoit la probabilité de succès d'une relance, 0,5 par défaut, et un drapeau d'affichage, calcule la valeur −200 d'un retard de soixante jours, puis Q(relancer) = −40 et Q(rééchelonner) = 28. Elle vérifie que le rééchelonnement respecte les règles, un taux d'endettement de 48,5 % sous 50 % et une durée de 42 mois sous 48, choisit de rééchelonner, chiffre à 272 000 AED par mois l'erreur de la règle « le moins cher », calcule les bascules 0,7429, 15,87 et 0,6071 et la mensualité maximale de 3 500 AED, puis renvoie tout cela ; avec 0,8, la relance l'emporte à 44.

**`cas_3_alerte_crypto(c, gamma, afficher)`** — Cette fonction met en scène l'astreinte d'une plateforme de cryptoactifs devant une alerte de liquidité : escalader coûte −2, attendre une heure expose à une crise de −50 avec la probabilité c, 0,035 par défaut, et laisse l'alerte persister avec la probabilité 0,2. Elle reçoit c, γ et un drapeau d'affichage, lève une `ValueError` si les probabilités ne laissent rien à la résorption, calcule le coût immédiat −1,79, le facteur 0,18 et la valeur exacte d'attendre, −2,18293, pire que −2, donc escalader, alors qu'une seule itération, −1,79, conseillerait d'attendre et laisserait passer 26,25 crises par mois sur 600 alertes. Elle calcule enfin les bascules 0,032 pour c et 0,525 pour γ, et renvoie ces nombres.

**`valeur_bail(loyer, q, gamma, vacance)`** — Celle-ci est le gestionnaire de patrimoine qui suit un appartement entre deux états, occupé et vacant : elle reçoit le loyer annuel, la probabilité q que le locataire renouvelle, le facteur γ et la récompense d'une année vacante, 60 par défaut, en milliers d'AED, et refuse par une `ValueError` une probabilité hors de l'intervalle de 0 à 1. Elle confie à `evaluer` la chaîne où l'état occupé rapporte le loyer et reste occupé avec la probabilité q, tandis que l'état vacant rapporte 60 et redevient occupé l'année suivante, et renvoie le couple V(O), V(V), soit 952,4229 et 917,1806 pour un loyer de 100 et q = 0,85.

**`cas_4_loyer_immo()`** — Cette fonction raconte une agence qui gère un parc de 200 appartements et doit décider, à chaque renouvellement, de garder le loyer à 100 ou de l'augmenter de 5 % à 105, au prix d'un renouvellement qui tombe de 0,85 à 0,75 : elle ne reçoit rien et compare V(O) = 952,4229 à 967,3469, d'où la hausse, pour un gain de 14,924 milliers d'AED par appartement et 2 984,8 sur le parc, bien loin des 50 d'un calcul naïf qui ignore la vacance. Elle montre aussi qu'à 0,65 la hausse ferait perdre 2 043,5 milliers d'AED, qu'à 0,675 elle cesse déjà de payer, et trouve par soixante bissections la probabilité de bascule 0,6924, puis renvoie ces résultats.

**`main()`** — C'est le chef d'orchestre de la fiche : il vérifie l'exemple simple, où V(s) vaut 2,75, puis appelle les démonstrations 1 à 3, refait à la main la solution exacte des tickets et déroule trente passes de `passe` depuis zéro, en contrôlant que l'erreur se contracte au moins d'un facteur γ et, en réalité, exactement de 0,27, et que l'écart 0,0011 entre deux passes garantit une erreur d'au plus 0,01. Il appelle ensuite les démonstrations 5 et 6, un contre-exemple, les quatre cas et le corrigé des exercices, jusqu'aux 66 passes de l'exercice 4 et aux 5 passes de l'exercice 8 ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tout concorde.

```python
"""Démonstration 09 — Bellman : retour, série géométrique, système linéaire, évaluation itérative, bornes, sensibilité, quatre cas aux Émirats."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

GAMMA = 0.9


def proche(x: float, y: float, tol: float = 1e-9) -> bool:
    return abs(x - y) <= tol


def passe(vN: float, vA: float, p_relance: float = 0.7) -> tuple[float, float]:
    """Une passe de Bellman sur les tickets : N (nouveau), A (en attente) ; R (résolu) vaut 0."""
    nouveau_N = 0.6 * 10 + 0.4 * (-2 + GAMMA * vA)
    nouveau_A = p_relance * 8 + (1 - p_relance) * (-1 + GAMMA * vA)
    return nouveau_N, nouveau_A


def valeur_attente(p_relance: float, gamma: float = GAMMA) -> float:
    """V(A) exact : V = 8p + (1 − p)(−1 + γV), donc V = (8p − (1 − p)) / (1 − γ(1 − p))."""
    if not 0.0 <= p_relance <= 1.0:
        raise ValueError("probabilité hors de [0, 1]")
    return (8 * p_relance - (1 - p_relance)) / (1 - gamma * (1 - p_relance))


def resoudre(M: list[list[float]], b: list[float]) -> list[float]:
    """Résout M x = b par élimination de Gauss avec pivot partiel ; ValueError si M est singulière."""
    n = len(b)
    A = [[float(x) for x in ligne] + [float(bi)] for ligne, bi in zip(M, b)]
    for col in range(n):
        piv = max(range(col, n), key=lambda i: abs(A[i][col]))
        if abs(A[piv][col]) < 1e-12:
            raise ValueError("matrice singulière : pas de solution unique")
        A[col], A[piv] = A[piv], A[col]
        for i in range(n):
            if i != col:
                f = A[i][col] / A[col][col]
                A[i] = [x - f * y for x, y in zip(A[i], A[col])]
    return [A[i][n] / A[i][i] for i in range(n)]


def evaluer(P: list[list[float]], r: list[float], gamma: float) -> list[float]:
    """V = (I − γ P)⁻¹ r pour une politique fixée (démonstration 3)."""
    n = len(r)
    M = [[(1.0 if i == j else 0.0) - gamma * P[i][j] for j in range(n)] for i in range(n)]
    return resoudre(M, r)


def tickets_exact(gamma: float = GAMMA, gain_relance: float = 8.0) -> tuple[float, float]:
    """V(N), V(A) des tickets par le système linéaire (I − γ P) V = r."""
    r = [0.6 * 10 + 0.4 * (-2), 0.7 * gain_relance + 0.3 * (-1)]
    V = evaluer([[0.0, 0.4], [0.0, 0.3]], r, gamma)
    return V[0], V[1]


def demo_1_retour() -> tuple[float, float, float]:
    """Le retour moyen simulé retrouve V(s) ; un état non markovien fausse Q(B)."""
    random.seed(9)
    n = 20000
    total = 0.0
    for _ in range(n):
        if random.random() < 0.5:
            total += 1.0                     # outil A : récompense 1, puis fin
        else:
            total += 0.0 + GAMMA * 5.0       # outil B : 0, puis 5 un pas plus tard
    moyenne = total / n
    q_b_vrai = 0.0 + GAMMA * 5.0
    q_b_faux = 0.0 + GAMMA * 3.0             # s₂ mélange deux situations : V(s₂) moyenné à 3
    print(f"démo 1 : G moyen simulé ({n} épisodes) = {moyenne:.4f} ; Bellman 2.75 ;"
          f" Q(B) = {q_b_vrai:.2f}, avec s₂ non markovien {q_b_faux:.2f}")
    return moyenne, q_b_vrai, q_b_faux


def demo_2_boucle() -> tuple[float, float, float]:
    v = 1 / (1 - GAMMA)
    s10 = sum(GAMMA ** k for k in range(10))
    s22 = sum(GAMMA ** k for k in range(22))
    assert proche(s10, (1 - GAMMA ** 10) / (1 - GAMMA)) and proche(s22, (1 - GAMMA ** 22) / (1 - GAMMA))
    print(f"démo 2 : V = 1/(1 − 0.9) = {v:.0f} ; somme de 10 termes {s10:.4f}, de 22 termes {s22:.4f} ;"
          f" 0.9^10 = {GAMMA ** 10:.4f} ≤ e^-1 = {math.exp(-1):.4f}")
    return v, s10, s22


def demo_3_systeme() -> tuple[float, float, bool]:
    vN, vA = tickets_exact()
    try:
        evaluer([[1.0]], [1.0], 1.0)         # un état qui boucle, γ = 1 : 1 − 1 × 1 = 0
        singuliere = False
    except ValueError:
        singuliere = True
    print(f"démo 3 : (I − γP)V = r donne V(N) = {vN:.5f}, V(A) = {vA:.5f} ;"
          f" boucle fermée à γ = 1 : matrice singulière = {singuliere}")
    return vN, vA, singuliere


def demo_5_bornes() -> tuple[float, float, float, float, float]:
    vN, vA = tickets_exact()
    borne = 10 / (1 - GAMMA)
    vN9, vA9 = tickets_exact(gain_relance=9.0)
    visites = GAMMA * 0.4 / (1 - GAMMA * 0.3)
    print(f"démo 5 : borne 10/(1 − γ) = {borne:.0f} ≥ V(N) = {vN:.5f} ; gain de relance 9 :"
          f" V(A) = {vA9:.5f}, V(N) = {vN9:.5f} ; visites actualisées de A depuis N = {visites:.5f}")
    return borne, vA9, vN9, visites, vN9 - vN


def demo_6_sensibilite() -> tuple[float, float, float, float]:
    elasticite = GAMMA / (1 - GAMMA)
    g2 = GAMMA * 1.01
    hausse_boucle = (1 / (1 - g2)) / (1 / (1 - GAMMA)) - 1
    vN, _ = tickets_exact()
    vN2, _ = tickets_exact(gamma=g2)
    hausse_tickets = vN2 / vN - 1
    print(f"démo 6 : élasticité γ/(1 − γ) = {elasticite:.0f} ; γ + 1 % → boucle +{hausse_boucle:.3%},"
          f" tickets V(N) = {vN2:.5f} (+{hausse_tickets:.3%})")
    return elasticite, hausse_boucle, vN2, hausse_tickets


def cas_1_tickets_public() -> dict:
    """[PUBLIC] relancer un ticket en attente ou le transférer à un agent humain (valeur 6,5)."""
    vA = valeur_attente(0.7)
    vN = 0.6 * 10 + 0.4 * (-2 + GAMMA * vA)
    humain = 8 - 1.5
    decision = "relancer" if vA > humain else "transférer"
    naif = 0.7 * 8 + 0.3 * (-1)               # une seule passe : la boucle d'attente est oubliée
    decision_naive = "relancer" if naif > humain else "transférer"
    en_attente = 12000 * 0.4                  # tickets qui passent en attente chaque mois
    cout_naif = en_attente * (vA - humain) * 10   # valeur perdue, 1 point = 10 AED
    p_bascule = 1.65 / 3.15                   # (9p − 1) / (0,1 + 0,9p) = 6,5
    v_moins_10 = valeur_attente(0.63)
    print(f"cas 1 : V(A) = {vA:.5f} ; V(N) = {vN:.5f} ; humain {humain} → {decision} ;"
          f" naïf {naif:.1f} → {decision_naive} ({en_attente:,.0f} tickets, {cout_naif:,.0f} AED/mois)")
    print(f"        bascule p = {p_bascule:.4f} ; p = 0.63 → V(A) = {v_moins_10:.5f}")
    return {"vA": vA, "vN": vN, "humain": humain, "decision": decision, "naif": naif,
            "decision_naive": decision_naive, "en_attente": en_attente, "cout_naif": cout_naif,
            "p_bascule": p_bascule, "v_moins_10": v_moins_10}


def cas_2_recouvrement_banque(q_relance: float = 0.5, afficher: bool = True) -> dict:
    """[BANQUE] prêt en retard de 30 jours : relancer ou rééchelonner."""
    v60 = 0.25 * 40 + 0.75 * (-280)
    q_rel = q_relance * (100 + GAMMA * 0) + (1 - q_relance) * (0 + GAMMA * v60)
    q_ree = 0.85 * (100 - 30) + 0.15 * (-30 + GAMMA * v60)
    ratio = (6500 + 3200) / 20000
    duree = 30 + 12
    reglementaire = ratio <= 0.5 and duree <= 48
    action = "rééchelonner" if q_ree > q_rel and reglementaire else "relancer"
    perte_naive = (q_ree - q_rel) * 400 * 10  # 400 dossiers, 1 point = 10 AED
    q_bascule = (q_ree + 180) / 280           # 280 q − 180 = Q(rééchelonner)
    v60_bascule = 5 / 0.315                   # 50 + 0,45 v = 55 + 0,135 v
    s_bascule = (q_rel + 210) / 280           # 280 s − 210 = Q(relancer)
    mensualite_max = 0.5 * 20000 - 6500
    if afficher:
        print(f"cas 2 : V(R60) = {v60:.0f} ; Q(relancer) = {q_rel:.1f} ; Q(rééchelonner) = {q_ree:.1f} ;"
          f" ratio {ratio:.1%}, durée {duree} mois → {action}")
        print(f"        perte de la règle « moins cher » {perte_naive:,.0f} AED/mois ; bascules q = {q_bascule:.4f},"
          f" V(R60) = {v60_bascule:.2f}, s = {s_bascule:.4f} ; mensualité max {mensualite_max:,.0f} AED")
    return {"v60": v60, "q_rel": q_rel, "q_ree": q_ree, "ratio": ratio, "duree": duree, "action": action,
            "perte_naive": perte_naive, "q_bascule": q_bascule, "v60_bascule": v60_bascule,
            "s_bascule": s_bascule, "mensualite_max": mensualite_max}


def cas_3_alerte_crypto(c: float = 0.035, gamma: float = GAMMA, afficher: bool = True) -> dict:
    """[CRYPTO] alerte de liquidité : escalader (−2) ou attendre une heure (boucle si l'alerte persiste)."""
    persiste = 0.2
    resorbe = 1 - c - persiste
    if resorbe < 0:
        raise ValueError("probabilités incohérentes")
    b = c * (-50) + resorbe * 0 + persiste * (-0.2)
    facteur = persiste * gamma
    v_attendre = b / (1 - facteur)
    escalade = -2.0
    iteres, v = [], 0.0
    for _ in range(3):
        v = b + facteur * v
        iteres.append(v)
    action = "escalader" if escalade > v_attendre else "attendre"
    action_naive = "escalader" if escalade > iteres[0] else "attendre"
    p_crise = c / (1 - persiste)
    crises = 600 * p_crise
    c_bascule = (-escalade * (1 - facteur) + persiste * (-0.2)) / 50
    g_bascule = (1 - b / escalade) / persiste
    if afficher:
        print(f"cas 3 : b = {b:.2f} ; facteur {facteur:.2f} ; V(attendre) = {v_attendre:.5f} → {action} ;"
          f" itérés {iteres[0]:.4f} ; {iteres[1]:.4f} ; {iteres[2]:.4f}")
        print(f"        naïf {iteres[0]:.2f} → {action_naive} : {crises:.2f} crises/mois ;"
          f" bascules c = {c_bascule:.3f}, γ = {g_bascule:.3f}")
    return {"b": b, "facteur": facteur, "v_attendre": v_attendre, "action": action, "iteres": iteres,
            "action_naive": action_naive, "p_crise": p_crise, "crises": crises,
            "c_bascule": c_bascule, "g_bascule": g_bascule}


def valeur_bail(loyer: float, q: float, gamma: float = GAMMA, vacance: float = 60.0) -> tuple[float, float]:
    """V(O), V(V) : occupé (loyer, renouvelle avec q) et vacant (vacance, puis occupé)."""
    if not 0.0 <= q <= 1.0:
        raise ValueError("probabilité hors de [0, 1]")
    V = evaluer([[q, 1 - q], [1.0, 0.0]], [loyer, vacance], gamma)
    return V[0], V[1]


def cas_4_loyer_immo() -> dict:
    """[IMMO] renouvellement : garder le loyer (100, q = 0,85) ou l'augmenter de 5 % (105, q = 0,75)."""
    garder_O, garder_V = valeur_bail(100, 0.85)
    aug_O, aug_V = valeur_bail(105, 0.75)
    action = "augmenter" if aug_O > garder_O else "garder"
    gain = aug_O - garder_O
    naif_gain = 105 / (1 - GAMMA) - 100 / (1 - GAMMA)
    gain_parc = gain * 200
    aug_065, _ = valeur_bail(105, 0.65)
    perte_065 = (garder_O - aug_065) * 200
    aug_0675, _ = valeur_bail(105, 0.675)       # q baisse de 10 % : 0,75 → 0,675
    bas, haut = 0.5, 0.75                       # bissection : V_aug(q) = V_garder
    for _ in range(60):
        milieu = (bas + haut) / 2
        if valeur_bail(105, milieu)[0] > garder_O:
            haut = milieu
        else:
            bas = milieu
    q_bascule = (bas + haut) / 2
    print(f"cas 4 : garder V(O) = {garder_O:.4f}, V(V) = {garder_V:.4f} ; augmenter V(O) = {aug_O:.4f},"
          f" V(V) = {aug_V:.4f} → {action} (+{gain:.3f} k AED, parc {gain_parc:,.1f} k AED)")
    print(f"        naïf +{naif_gain:.0f} ; q = 0.65 → {aug_065:.4f}, perte {perte_065:,.1f} k AED ;"
          f" q = 0.675 → {aug_0675:.4f} ; bascule q = {q_bascule:.4f}")
    return {"garder_O": garder_O, "garder_V": garder_V, "aug_O": aug_O, "aug_V": aug_V, "action": action,
            "gain": gain, "gain_parc": gain_parc, "naif_gain": naif_gain, "aug_065": aug_065,
            "perte_065": perte_065, "aug_0675": aug_0675, "q_bascule": q_bascule}


def main() -> None:
    # Exemple simple
    v_s2 = 5 + GAMMA * 0
    q_a, q_b = 1 + GAMMA * 0, 0 + GAMMA * v_s2
    v_s = 0.5 * q_a + 0.5 * q_b
    print(f"exemple simple : V(s₂) = {v_s2} ; Q(A) = {q_a} ; Q(B) = {q_b} ; V(s) = {v_s} ; max = {max(q_a, q_b)}")
    assert v_s == 2.75 and q_b == 4.5 and 0.5 * q_b == 2.25 and max(q_a, q_b) == 4.5

    # Démonstrations 1 à 3
    moyenne, q_b_vrai, q_b_faux = demo_1_retour()
    assert abs(moyenne - 2.75) < 0.05 and round(moyenne, 4) == 2.7481
    assert round(q_b_vrai, 2) == 4.5 and round(q_b_faux, 2) == 2.7 and round(q_b_vrai - q_b_faux, 2) == 1.8
    assert round(2.75 - moyenne, 4) == 0.0019
    v, s10, s22 = demo_2_boucle()
    assert proche(v, 10) and round(s10, 4) == 6.5132 and round(s22, 4) == 9.0152
    assert round(GAMMA ** 22, 4) == 0.0985 and round(s10 / v, 2) == 0.65 and round(s22 / v, 2) == 0.9
    assert round(GAMMA ** 10, 4) == 0.3487 and GAMMA ** 10 <= math.exp(-1) and round(math.exp(-1), 4) == 0.3679
    vA_exact = 5.3 / 0.73
    vN_exact = 0.6 * 10 + 0.4 * (-2 + GAMMA * vA_exact)
    print(f"tickets, solution exacte : V(A) = {vA_exact:.5f} ; V(N) = {vN_exact:.5f}")
    assert round(vA_exact, 5) == 7.26027 and round(vN_exact, 5) == 7.8137
    assert round(0.36 * vA_exact, 5) == 2.6137 and round(-2 + GAMMA * vA_exact, 5) == 4.53425
    assert vA_exact <= 8                       # exercice 7 : jamais plus que la meilleure branche
    vN3, vA3, singuliere = demo_3_systeme()
    assert proche(vN3, vN_exact) and proche(vA3, vA_exact) and singuliere

    # Démonstration 4 : évaluation itérative depuis V = 0
    vN = vA = 0.0
    erreurs = []
    trace = {}
    for k in range(1, 31):
        vN, vA = passe(vN, vA)
        erreurs.append(max(abs(vN - vN_exact), abs(vA - vA_exact)))
        trace[k] = (round(vN, 5), round(vA, 5))
        if k in (1, 2, 3, 10):
            print(f"  passe {k:>2} : V(N) = {vN:.5f} ; V(A) = {vA:.5f} ; erreur max = {erreurs[-1]:.5f}")
    assert round(passe(0, 0)[0], 1) == 5.2 and abs(vN - vN_exact) < 1e-9
    assert trace[2] == (7.108, 6.731) and trace[3][0] == 7.62316 and trace[10] == (7.81368, 7.26026)
    assert all(e2 <= GAMMA * e1 + 1e-12 for e1, e2 in zip(erreurs, erreurs[1:]))   # démonstration 4
    assert all(proche(e2, 0.27 * e1, 1e-12) for e1, e2 in zip(erreurs[:12], erreurs[1:13]))  # vrai facteur 0,27
    e0 = max(vN_exact, vA_exact)
    assert round(e0, 4) == 7.8137 and round(erreurs[0], 4) == 2.6137 and round(erreurs[0] / e0, 4) == 0.3345
    assert round(erreurs[1], 4) == 0.7057 and round(0.27 * 1.96027, 5) == 0.52927 and round(erreurs[2], 5) == 0.19054
    assert round(0.9 * 5.3, 2) == 4.77 and round(0.4 * 2.77, 3) == 1.108 and round(0.3 * 3.77, 3) == 1.131
    assert round(2.6137 * 0.27, 4) == 0.7057
    assert round(GAMMA ** 10 * e0, 4) == 2.7245 and round(erreurs[9], 5) == 0.00002
    assert round(5.3 - vA_exact, 5) == -1.96027 and round(0.9 * 0.3, 2) == 0.27 and round(0.9 * 0.4, 2) == 0.36
    assert math.isclose(1 / (1 - GAMMA), 10) and round(GAMMA ** 10, 3) == 0.349 and round(1 / (1 - 0.99)) == 100
    eps = (1 - GAMMA) * 0.01 / GAMMA
    print(f"  critère d'arrêt : écart ε = {eps:.4f} entre deux passes garantit une erreur ≤ 0.01")
    assert round(eps, 4) == 0.0011

    # Démonstrations 5 et 6
    borne, vA9, vN9, visites, delta = demo_5_bornes()
    assert round(borne, 9) == 100 and round(vA9, 5) == 8.21918 and round(vN9, 5) == 8.1589
    assert round(visites, 5) == 0.49315 and round(delta, 5) == 0.34521 and round(0.7 * visites, 5) == 0.34521
    assert vA9 >= vA_exact and vN9 >= vN_exact and proche(0.7 * 9 + 0.3 * (-1), 6)
    rapide = 0.5 * 11 + 0.5 * (-2 + GAMMA * vA_exact)    # contre-exemple : récompense 11 mais succès 0,5
    assert round(rapide, 5) == 7.76712 and rapide < vN_exact
    elast, hausse_boucle, vN2, hausse_t = demo_6_sensibilite()
    assert round(elast) == 9 and round(hausse_boucle, 5) == 0.0989 and round(vN2, 5) == 7.84964
    assert round(hausse_t, 5) == 0.0046 and round(1 / (1 - 0.909), 5) == 10.98901
    assert round(5.3 / (1 - 0.909 * 0.3), 5) == 7.28723 and round(1 - 0.909 * 0.3, 4) == 0.7273
    assert round(1 / (1 - 0.99 * 1.005), 2) == 198.02 and round(0.99 / 0.01) == 99

    # Quatre cas
    c1 = cas_1_tickets_public()
    assert c1["decision"] == "relancer" and c1["decision_naive"] == "transférer" and c1["humain"] == 6.5
    assert round(c1["naif"], 1) == 5.3 and c1["en_attente"] == 4800 and round(c1["cout_naif"]) == 36493
    assert round(c1["p_bascule"], 4) == 0.5238 and round(c1["vN"], 5) == 7.8137
    assert round(0.6 * 10 + 0.4 * (-2), 1) == 5.2 and round(0.7 * 8 + 0.3 * (-1), 1) == 5.3
    assert proche(valeur_attente(c1["p_bascule"]), 6.5) and round(c1["v_moins_10"], 5) == 7.0015
    assert round(c1["vA"] - c1["humain"], 5) == 0.76027 and round(1 / 0.7, 2) == 1.43
    c2 = cas_2_recouvrement_banque()
    assert c2["v60"] == -200 and proche(c2["q_rel"], -40) and proche(c2["q_ree"], 28)
    assert c2["action"] == "rééchelonner" and round(c2["ratio"], 3) == 0.485 and c2["duree"] == 42
    assert round(c2["perte_naive"]) == 272000 and round(c2["q_bascule"], 4) == 0.7429
    assert round(c2["v60_bascule"], 2) == 15.87 and round(c2["s_bascule"], 4) == 0.6071
    assert c2["mensualite_max"] == 3500 and 6500 + 3200 == 9700
    assert round(208 / 280, 4) == 0.7429 and round(170 / 280, 4) == 0.6071 and round(5 / 0.315, 2) == 15.87
    assert proche(0.15 * (-30 + GAMMA * -200), -31.5) and proche(0.85 * 70, 59.5)
    c3 = cas_3_alerte_crypto()
    assert round(c3["b"], 2) == -1.79 and round(c3["facteur"], 2) == 0.18 and round(c3["v_attendre"], 5) == -2.18293
    assert c3["action"] == "escalader" and c3["action_naive"] == "attendre"
    assert [round(x, 4) for x in c3["iteres"]] == [-1.79, -2.1122, -2.1702]
    assert round(c3["p_crise"], 5) == 0.04375 and round(c3["crises"], 2) == 26.25
    assert round(c3["c_bascule"], 3) == 0.032 and round(c3["g_bascule"], 3) == 0.525
    assert cas_3_alerte_crypto(c=0.031, afficher=False)["action"] == "attendre" and cas_3_alerte_crypto(c=0.033, afficher=False)["action"] == "escalader"
    assert round(cas_3_alerte_crypto(c=0.025, afficher=False)["v_attendre"], 4) == -1.5732
    c3_moins_10 = cas_3_alerte_crypto(c=0.0315, afficher=False)
    assert round(c3_moins_10["b"], 3) == -1.615 and round(c3_moins_10["v_attendre"], 5) == -1.96951
    assert c3_moins_10["action"] == "attendre" and round(c3["iteres"][1] - c3["iteres"][0], 4) == -0.3222
    assert round(1 - 0.035 - 0.2, 3) == 0.765 and round(-1.79 / -2, 3) == 0.895
    c4 = cas_4_loyer_immo()
    assert round(c4["garder_O"], 4) == 952.4229 and round(c4["aug_O"], 4) == 967.3469
    assert round(c4["garder_V"], 4) == 917.1806 and round(c4["aug_V"], 4) == 930.6122
    assert c4["action"] == "augmenter" and round(c4["gain"], 3) == 14.924 and round(c4["naif_gain"]) == 50
    assert round(c4["aug_065"], 4) == 942.2053 and round(c4["perte_065"], 1) == 2043.5
    assert round(c4["q_bascule"], 4) == 0.6924 and round(c4["gain_parc"], 1) == 2984.8
    assert round(c4["aug_0675"], 4) == 948.1625 and c4["aug_0675"] < c4["garder_O"]
    assert round(c4["garder_O"] - c4["aug_065"], 4) == 10.2176
    assert proche(c4["aug_065"], 123.9 / 0.1315) and proche(c4["aug_0675"], 122.55 / 0.12925)
    assert round(c4["gain"] / 1, 3) == 14.924 and c4["naif_gain"] / c4["gain"] > 3
    assert proche(c4["garder_O"], 108.1 / 0.1135) and proche(c4["aug_O"], 118.5 / 0.1225)
    assert round(0.9 * 0.15 * 60, 1) == 8.1 and round(0.135 * 0.9, 4) == 0.1215 and round(0.765 + 0.1215, 4) == 0.8865
    assert round(0.225 * 60, 1) == 13.5 and round(0.225 * 0.9, 4) == 0.2025 and round(1 - 0.675 - 0.2025, 4) == 0.1225
    assert round(0.9 * 0.35 * 60, 1) == 18.9 and round(1 - 0.9 * 0.65 - 0.81 * 0.35, 4) == 0.1315

    print("Corrigé")
    vA9 = 7.1 / 0.91
    k = math.ceil(math.log(1000) / math.log(1 / GAMMA))
    q6 = cas_2_recouvrement_banque(q_relance=0.8, afficher=False)
    faux = 5.3 / (1 - 0.9)                     # exercice 7 : γV(A) sans le poids 0,3
    k8 = math.ceil(math.log(abs(c3["v_attendre"]) / 0.001) / math.log(1 / 0.18))
    print(f"  ex1 {2 / (1 - GAMMA):.0f} ; ex2 {0.5 * 1 + 0.5 * 0.5 * 5} ; ex3 V(A) = {vA9:.3f} ; ex4 {k} passes")
    print(f"  ex6 Q(relancer) = {q6['q_rel']:.0f} → {q6['action']} ; ex7 faux {faux:.0f} au lieu de {vA_exact:.2f} ;"
          f" ex8 {k8} passes")
    assert round(2 / (1 - GAMMA)) == 20 and 0.5 + 0.25 * 5 == 1.75 and round(vA9, 3) == 7.802 and k == 66
    assert round(math.log(1000) / math.log(1 / GAMMA), 1) == 65.6
    assert proche(q6["q_rel"], 44) and q6["action"] == "relancer" and round(faux) == 53
    assert k8 == 5 and 0.18 ** 5 * 2.18293 <= 0.001 < 0.18 ** 4 * 2.18293
    assert round(0.18 ** 4 * 2.18293, 4) == 0.0023 and round(0.18 ** 5 * 2.18293, 5) == 0.00041
    assert round(math.log(2182.93), 3) == 7.688 and round(math.log(1 / 0.18), 4) == 1.7148
    assert round(math.log(1000), 3) == 6.908 and round(math.log(1 / 0.9), 4) == 0.1054
    assert round(math.log(abs(c3["v_attendre"]) / 0.001) / math.log(1 / 0.18), 2) == 4.48
    vN = vA = 0.0
    for _ in range(200):
        vN, vA = passe(vN, vA, 0.9)
    assert math.isclose(vA, vA9)
    assert proche(valeur_attente(0.9), vA9)
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
exemple simple : V(s₂) = 5.0 ; Q(A) = 1.0 ; Q(B) = 4.5 ; V(s) = 2.75 ; max = 4.5
démo 1 : G moyen simulé (20000 épisodes) = 2.7481 ; Bellman 2.75 ; Q(B) = 4.50, avec s₂ non markovien 2.70
démo 2 : V = 1/(1 − 0.9) = 10 ; somme de 10 termes 6.5132, de 22 termes 9.0152 ; 0.9^10 = 0.3487 ≤ e^-1 = 0.3679
tickets, solution exacte : V(A) = 7.26027 ; V(N) = 7.81370
démo 3 : (I − γP)V = r donne V(N) = 7.81370, V(A) = 7.26027 ; boucle fermée à γ = 1 : matrice singulière = True
  passe  1 : V(N) = 5.20000 ; V(A) = 5.30000 ; erreur max = 2.61370
  passe  2 : V(N) = 7.10800 ; V(A) = 6.73100 ; erreur max = 0.70570
  passe  3 : V(N) = 7.62316 ; V(A) = 7.11737 ; erreur max = 0.19054
  passe 10 : V(N) = 7.81368 ; V(A) = 7.26026 ; erreur max = 0.00002
  critère d'arrêt : écart ε = 0.0011 entre deux passes garantit une erreur ≤ 0.01
démo 5 : borne 10/(1 − γ) = 100 ≥ V(N) = 7.81370 ; gain de relance 9 : V(A) = 8.21918, V(N) = 8.15890 ; visites actualisées de A depuis N = 0.49315
démo 6 : élasticité γ/(1 − γ) = 9 ; γ + 1 % → boucle +9.890%, tickets V(N) = 7.84964 (+0.460%)
cas 1 : V(A) = 7.26027 ; V(N) = 7.81370 ; humain 6.5 → relancer ; naïf 5.3 → transférer (4,800 tickets, 36,493 AED/mois)
        bascule p = 0.5238 ; p = 0.63 → V(A) = 7.00150
cas 2 : V(R60) = -200 ; Q(relancer) = -40.0 ; Q(rééchelonner) = 28.0 ; ratio 48.5%, durée 42 mois → rééchelonner
        perte de la règle « moins cher » 272,000 AED/mois ; bascules q = 0.7429, V(R60) = 15.87, s = 0.6071 ; mensualité max 3,500 AED
cas 3 : b = -1.79 ; facteur 0.18 ; V(attendre) = -2.18293 → escalader ; itérés -1.7900 ; -2.1122 ; -2.1702
        naïf -1.79 → attendre : 26.25 crises/mois ; bascules c = 0.032, γ = 0.525
cas 4 : garder V(O) = 952.4229, V(V) = 917.1806 ; augmenter V(O) = 967.3469, V(V) = 930.6122 → augmenter (+14.924 k AED, parc 2,984.8 k AED)
        naïf +50 ; q = 0.65 → 942.2053, perte 2,043.5 k AED ; q = 0.675 → 948.1625 ; bascule q = 0.6924
Corrigé
  ex1 20 ; ex2 1.75 ; ex3 V(A) = 7.802 ; ex4 66 passes
  ex6 Q(relancer) = 44 → relancer ; ex7 faux 53 au lieu de 7.26 ; ex8 5 passes
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

Le fichier contient trois algorithmes. L'évaluation itérative applique la formule à toutes les valeurs, passe après passe, jusqu'à ce qu'elles ne bougent plus (démonstration 4). L'évaluation exacte écrit le système linéaire de la démonstration 3 et le résout par élimination de Gauss. La recherche de bascule cherche, par bissection, la valeur d'une donnée pour laquelle deux politiques se valent (cas 4).

```text
ALGORITHME ÉvaluationDePolitique
ENTRÉES : états S, politique π, transitions P, récompenses R, γ < 1, tolérance ε
SORTIE  : valeurs V(s) pour chaque état

  V(s) ← 0 pour tout s
  RÉPÉTER
      écart ← 0
      POUR CHAQUE état s FAIRE
          nouveau ← Σ sur a de π(a | s) × Σ sur s′ de P(s′ | s, a) × [R + γ × V(s′)]
          écart ← max(écart, |nouveau − V(s)|)
          V(s) ← nouveau
      FIN POUR
  TANT QUE écart > ε          (erreur garantie ≤ γ × ε / (1 − γ))
  RETOURNER V

ALGORITHME ÉvaluationExacte
ENTRÉES : matrice Pπ des états non terminaux, récompenses moyennes rπ, γ < 1
SORTIE  : V, ou une erreur si la matrice est singulière

  M ← I − γ × Pπ
  POUR chaque colonne c FAIRE
      choisir la ligne de plus grand |M[i][c]| (pivot) ; SI |pivot| ≈ 0 ALORS ERREUR « singulière »
      échanger les lignes ; annuler la colonne c dans toutes les autres lignes
  FIN POUR
  RETOURNER la solution V de M × V = rπ

ALGORITHME BasculeParBissection
ENTRÉES : fonction f(q) = V_politique1(q) − V_politique2, intervalle [bas ; haut] où f change de signe
SORTIE  : q où les deux politiques se valent

  RÉPÉTER 60 FOIS
      milieu ← (bas + haut) / 2
      SI f(milieu) > 0 ALORS haut ← milieu SINON bas ← milieu
  RETOURNER (bas + haut) / 2
```

**Complexité.** Une passe d'évaluation itérative coûte O(|S|² × |A|) dans le pire cas, toutes les transitions étant possibles. L'erreur est multipliée par γ à chaque passe au pire (démonstration 4) : il faut environ ln(1/ε) / ln(1/γ) passes, soit 66 passes pour diviser l'erreur par 1 000 avec γ = 0,9 ; quand le système se termine souvent, le vrai facteur est plus petit (0,27 pour les tickets, 0,18 pour l'alerte), et il en faut beaucoup moins. L'évaluation exacte coûte O(|S|³) opérations et O(|S|²) en mémoire, une seule fois, sans tolérance à choisir. La bissection divise l'intervalle par 2 à chaque tour : 60 tours donnent une précision de l'ordre de 0,25 × 2⁻⁶⁰, et chaque tour coûte une évaluation exacte.

**Du squelette au code.** Une passe sur les deux états N et A est la fonction `passe(vN, vA, p_relance)` ; la boucle `for k in range(1, 31)` de `main` est le RÉPÉTER, avec 30 passes fixes au lieu du test sur ε, et la liste `erreurs` vérifie la décroissance par un facteur γ, et même par le facteur exact 0,27. La solution exacte des tickets est calculée à part avec la démonstration 3 (5,3/0,73), et, en général, par `evaluer(P, r, gamma)`, qui construit I − γPπ et appelle `resoudre(M, b)`, l'élimination de Gauss avec pivot qui lève `ValueError` sur une matrice singulière. La formule fermée de V(A) en fonction du taux de relance est `valeur_attente(p_relance, gamma)`, et le système à deux états du bail est `valeur_bail(loyer, q, gamma, vacance)`. Les démonstrations sont rejouées par `demo_1_retour`, `demo_2_boucle`, `demo_3_systeme`, `demo_5_bornes` et `demo_6_sensibilite` ; les quatre cas par `cas_1_tickets_public`, `cas_2_recouvrement_banque`, `cas_3_alerte_crypto` (avec l'argument `afficher` pour les calculs de sensibilité sans trace) et `cas_4_loyer_immo`, dont la boucle `for _ in range(60)` est la bissection.
