# Étape 32 bis — Attention par produit scalaire normalisé (Scaled Dot-Product Attention) — Théorèmes et démonstrations

> Étape 32 bis du parcours · Précédent : [Formules et rôle de √d_k](<32-Attention-Formules-et-Role-de-Racine-dk.md>) · Suite : [Transformer : déroulé numérique](<33-Transformer-et-Attention-Deroule-Numerique.md>)

**Ce que contient ce fichier :** la formule de l'attention, ses symboles un par un, puis cinq théorèmes démontrés : la softmax produit une distribution de probabilité, elle ne change pas si on décale tous les scores (d'où l'astuce de stabilité du code), la division par √dₖ remet la variance des scores à 1, une softmax saturée n'apprend plus (son gradient s'annule), et la sortie est une moyenne pondérée des valeurs. Le fichier finit par un calcul à la main et un programme qui le vérifie.

**Prérequis :** le produit scalaire et la norme de l'étape 28 bis.

---

## 1. Rôle dans un agent

Le RAG, la mémoire et l'historique remplissent le contexte. L'attention décide, pour chaque token en cours de traitement, **quels tokens du contexte comptent et combien**. Un chunk récupéré mais auquel le modèle « ne fait pas attention » n'aide pas la réponse. Comprendre la formule explique trois faits de production :

- le coût d'un long contexte croît comme le carré de sa longueur (§9) ;
- un document noyé au milieu d'un long contexte reçoit une part de poids plus faible, car les poids d'attention se partagent un total fixe égal à 1 (théorème 1) ;
- l'ordre des tokens ne vient pas de l'attention elle-même, mais de l'encodage de position (§8).

---

## 2. La formule

$$
\operatorname{Attention}(Q, K, V) = \operatorname{softmax}\!\left( \frac{Q K^\top}{\sqrt{d_k}} \right) V
$$

### Définition de chaque élément

$$
X \in \mathbb{R}^{n \times d}
$$

**X** : la matrice d'entrée. Une ligne par token, n lignes, d colonnes (la dimension du modèle). ℝⁿˣᵈ désigne les tableaux de n lignes et d colonnes de nombres réels.

$$
Q = X W_Q, \qquad K = X W_K, \qquad V = X W_V
$$

**W_Q, W_K, W_V** : trois matrices de poids apprises pendant l'entraînement. Elles transforment chaque token en trois vecteurs différents, chacun ayant un rôle.

$$
Q \in \mathbb{R}^{n \times d_k}
$$

**Q (Query, requête)** : une ligne par token qui « cherche ». La ligne qᵢ dit ce que le token i a besoin de savoir.

$$
K \in \mathbb{R}^{m \times d_k}
$$

**K (Key, clé)** : une ligne par token qui « peut être trouvé ». La ligne kⱼ dit ce que le token j contient, sous forme comparable aux requêtes. m est le nombre de tokens consultables (m = n en self-attention).

$$
V \in \mathbb{R}^{m \times d_v}
$$

**V (Value, valeur)** : l'information qu'on récupère réellement quand on fait attention au token j. La clé sert à être trouvé, la valeur sert à être lu.

$$
d_k
$$

**dₖ** : la dimension des requêtes et des clés. Elles doivent avoir la même, sinon leur produit scalaire n'est pas défini.

$$
d_v
$$

**dᵥ** : la dimension des valeurs, donc de la sortie de chaque token.

$$
K^\top
$$

**Kᵀ (transposée)** : K dont on échange lignes et colonnes. Kᵀ a dₖ lignes et m colonnes.

$$
S = Q K^\top \in \mathbb{R}^{n \times m}, \qquad S_{ij} = \mathbf{q}_i \cdot \mathbf{k}_j = \sum_{l=1}^{d_k} q_{il}\, k_{jl}
$$

**S (matrice des scores)** : la case Sᵢⱼ est le produit scalaire entre la requête du token i et la clé du token j. Plus il est grand, plus le token j répond à ce que cherche le token i. C'est le produit scalaire de l'étape 28 bis, calculé pour toutes les paires d'un coup.

$$
\sqrt{d_k}
$$

**√dₖ** : le facteur d'échelle. On divise tous les scores par lui avant la softmax. Le théorème 3 démontre pourquoi c'est exactement √dₖ.

$$
A = \operatorname{softmax}\!\left(\frac{S}{\sqrt{d_k}}\right) \in \mathbb{R}^{n \times m}
$$

**A (matrice d'attention)** : la softmax est appliquée ligne par ligne. La case Aᵢⱼ est la part d'attention que le token i accorde au token j. Chaque ligne somme à 1 (théorème 1).

$$
O = A V \in \mathbb{R}^{n \times d_v}, \qquad \mathbf{o}_i = \sum_{j=1}^{m} A_{ij}\, \mathbf{v}_j
$$

**O (sortie)** : la ligne oᵢ est le mélange des valeurs, pondéré par l'attention du token i. C'est le nouveau vecteur du token i, enrichi par le contexte.

---

## 3. La fonction softmax

$$
\operatorname{softmax}(\mathbf{z})_j = \frac{e^{z_j}}{\displaystyle\sum_{l=1}^{m} e^{z_l}}
$$

### Définition de chaque élément

$$
\mathbf{z} = (z_1, \dots, z_m) \in \mathbb{R}^m
$$

**z** : un vecteur de scores quelconques (positifs, négatifs, grands, petits). On les appelle aussi logits.

$$
e^{z_j}
$$

**e^zⱼ (exponentielle)** : e ≈ 2,71828. L'exponentielle est toujours strictement positive et strictement croissante : un score plus grand donne toujours un poids plus grand.

$$
\sum_{l=1}^{m} e^{z_l}
$$

**Le dénominateur** : la somme de toutes les exponentielles. Diviser par elle force le total à 1. l est un indice de sommation, on aurait pu l'appeler autrement.

---

## 4. Théorème 1 — La softmax produit une distribution de probabilité

### Énoncé

$$
\operatorname{softmax}(\mathbf{z})_j > 0 \quad \text{pour tout } j, \qquad \sum_{j=1}^{m} \operatorname{softmax}(\mathbf{z})_j = 1
$$

### Rôle

Chaque ligne de A est un « budget d'attention » de 1 réparti sur les m tokens. Si un token en reçoit plus, les autres en reçoivent moins. C'est la raison mathématique pour laquelle ajouter des chunks inutiles au contexte dilue l'attention portée aux chunks utiles.

### Démonstration

Positivité : e^zⱼ > 0 et le dénominateur est une somme de termes > 0, donc > 0. Un quotient de deux nombres strictement positifs est strictement positif.

Somme : on met le dénominateur commun en facteur, puisqu'il ne dépend pas de j :

$$
\sum_{j=1}^{m} \frac{e^{z_j}}{\sum_{l} e^{z_l}} = \frac{\sum_{j} e^{z_j}}{\sum_{l} e^{z_l}} = 1
$$

Le numérateur et le dénominateur sont la même somme, seul le nom de l'indice change. ∎

---

## 5. Théorème 2 — Décaler tous les scores ne change rien

### Énoncé

$$
\operatorname{softmax}(\mathbf{z} + c\,\mathbf{1}) = \operatorname{softmax}(\mathbf{z}) \qquad \text{pour tout } c \in \mathbb{R}
$$

**c** : une constante réelle quelconque. **1** : le vecteur dont toutes les coordonnées valent 1. z + c**1** ajoute c à chaque score.

### Rôle

e^1000 dépasse la capacité d'un nombre flottant (environ 1,8 × 10³⁰⁸) : le calcul direct renvoie `inf` puis `nan`. Grâce à ce théorème, on soustrait le score maximal avant d'exponentier (c = −max z). Le plus grand exposant devient 0, donc e⁰ = 1, et plus rien ne déborde. Toutes les implémentations sérieuses font ça, y compris le code du §11.

### Démonstration

On utilise e^(a+b) = e^a · e^b :

$$
\frac{e^{z_j + c}}{\sum_{l} e^{z_l + c}} = \frac{e^{c}\, e^{z_j}}{e^{c} \sum_{l} e^{z_l}} = \frac{e^{z_j}}{\sum_{l} e^{z_l}}
$$

Le facteur e^c, strictement positif, se simplifie. ∎

Ce n'est pas vrai pour une **multiplication** des scores. Multiplier par un facteur change la distribution : c'est exactement l'effet de √dₖ et de la température (théorème 4).

---

## 6. Théorème 3 — Pourquoi diviser par √dₖ

### Énoncé

Supposons que les coordonnées des requêtes et des clés soient des variables aléatoires indépendantes, d'espérance 0 et de variance 1. Alors :

$$
\mathbb{E}[\mathbf{q}\cdot\mathbf{k}] = 0, \qquad \operatorname{Var}(\mathbf{q}\cdot\mathbf{k}) = d_k, \qquad \operatorname{Var}\!\left(\frac{\mathbf{q}\cdot\mathbf{k}}{\sqrt{d_k}}\right) = 1
$$

### Définition de chaque élément

$$
\mathbb{E}[Y]
$$

**𝔼[Y] (espérance)** : la valeur moyenne de Y si on répétait le tirage une infinité de fois.

$$
\operatorname{Var}(Y) = \mathbb{E}\big[(Y - \mathbb{E}[Y])^2\big] = \mathbb{E}[Y^2] - \mathbb{E}[Y]^2
$$

**Var(Y) (variance)** : la dispersion moyenne de Y autour de sa moyenne, au carré.

$$
\sigma = \sqrt{\operatorname{Var}(Y)}
$$

**σ (sigma minuscule, écart-type)** : la dispersion dans la même unité que Y. Environ 95 % des valeurs d'une loi normale tombent à moins de 2σ de la moyenne.

$$
q_l,\ k_l \quad \text{indépendantes}, \quad \mathbb{E}[q_l] = \mathbb{E}[k_l] = 0, \quad \operatorname{Var}(q_l) = \operatorname{Var}(k_l) = 1
$$

**Hypothèse** : c'est à peu près l'état d'un réseau bien initialisé. Elle sert à mesurer l'ordre de grandeur des scores.

### Rôle

Sans division, l'écart-type des scores vaut √dₖ. Avec dₖ = 128 (valeur courante par tête), √128 ≈ 11,3 : les scores s'étalent typiquement entre −22 et +22. Le théorème 4 montrera qu'une softmax nourrie de tels écarts devient presque un « tout ou rien » et cesse d'apprendre. Diviser par √dₖ ramène l'écart-type à 1, quelle que soit la dimension.

### Démonstration

**Espérance d'un terme.** Par indépendance, l'espérance d'un produit est le produit des espérances :

$$
\mathbb{E}[q_l k_l] = \mathbb{E}[q_l]\,\mathbb{E}[k_l] = 0 \times 0 = 0
$$

**Variance d'un terme.** Comme 𝔼[q_l k_l] = 0 :

$$
\operatorname{Var}(q_l k_l) = \mathbb{E}[q_l^2 k_l^2] - 0^2 = \mathbb{E}[q_l^2]\,\mathbb{E}[k_l^2]
$$

Et 𝔼[q_l²] = Var(q_l) + 𝔼[q_l]² = 1 + 0 = 1, idem pour k_l. Donc Var(q_l k_l) = 1.

**Somme des dₖ termes.** Les produits q_l k_l pour l différents sont indépendants. La variance d'une somme de variables indépendantes est la somme des variances :

$$
\operatorname{Var}(\mathbf{q}\cdot\mathbf{k}) = \operatorname{Var}\!\left(\sum_{l=1}^{d_k} q_l k_l\right) = \sum_{l=1}^{d_k} \operatorname{Var}(q_l k_l) = d_k
$$

De même 𝔼[q · k] = Σ 0 = 0.

**Division.** Pour une constante a, Var(aY) = a² Var(Y). Avec a = 1/√dₖ :

$$
\operatorname{Var}\!\left(\frac{\mathbf{q}\cdot\mathbf{k}}{\sqrt{d_k}}\right) = \frac{1}{d_k} \cdot d_k = 1
$$

∎ Diviser par dₖ au lieu de √dₖ donnerait une variance 1/dₖ : des scores tous proches de 0 et une attention presque uniforme, qui ne distingue plus rien.

---

## 7. Théorème 4 — Saturation : une softmax trop « pointue » n'apprend plus

### Énoncé (a) — la dérivée de la softmax

Notons p = softmax(z). Alors :

$$
\frac{\partial p_i}{\partial z_j} = p_i\,(\delta_{ij} - p_j)
$$

### Définition de chaque élément

$$
\frac{\partial p_i}{\partial z_j}
$$

**∂pᵢ/∂zⱼ (dérivée partielle)** : de combien varie le poids pᵢ quand on augmente un peu le score zⱼ, les autres scores restant fixes. C'est ce que la rétropropagation utilise pour corriger W_Q et W_K.

$$
\delta_{ij} = \begin{cases} 1 & \text{si } i = j \\ 0 & \text{si } i \ne j \end{cases}
$$

**δᵢⱼ (delta de Kronecker)** : vaut 1 sur la diagonale, 0 ailleurs.

### Démonstration de (a)

Posons Z = Σₗ e^zₗ, donc pᵢ = e^zᵢ / Z, et la dérivée de Z par rapport à zⱼ vaut e^zⱼ. On dérive un quotient (u/v)′ = (u′v − uv′)/v² :

$$
\frac{\partial p_i}{\partial z_j} = \frac{\delta_{ij}\, e^{z_i}\, Z - e^{z_i}\, e^{z_j}}{Z^2} = \frac{e^{z_i}}{Z}\left(\delta_{ij} - \frac{e^{z_j}}{Z}\right) = p_i\,(\delta_{ij} - p_j)
$$

∎

### Énoncé (b) — limites selon l'échelle

Multiplions tous les scores par un facteur β > 0 (β, bêta, joue le rôle de 1/√dₖ ou de l'inverse de la température). Si un seul score z* est strictement le plus grand :

$$
\lim_{\beta \to +\infty} \operatorname{softmax}(\beta\,\mathbf{z}) = \text{one-hot sur } z^*, \qquad \lim_{\beta \to 0} \operatorname{softmax}(\beta\,\mathbf{z}) = \left(\frac{1}{m}, \dots, \frac{1}{m}\right)
$$

**one-hot** : un vecteur avec un 1 à une position et des 0 partout ailleurs. **lim (limite)** : la valeur dont on s'approche quand β tend vers l'infini ou vers 0.

### Démonstration de (b)

Grand β : on divise numérateur et dénominateur par e^(βz*) (théorème 2 avec c = −βz*) :

$$
\operatorname{softmax}(\beta\mathbf{z})_j = \frac{e^{\beta(z_j - z^*)}}{\sum_{l} e^{\beta(z_l - z^*)}}
$$

Pour j ≠ *, zⱼ − z* < 0, donc e^(β(zⱼ − z*)) → 0. Pour j = *, le terme vaut e⁰ = 1. Le dénominateur tend vers 1, le poids de z* vers 1, tous les autres vers 0.

β → 0 : chaque exposant βzⱼ → 0, donc chaque e^(βzⱼ) → 1, et chaque poids tend vers 1/m. ∎

### Conséquence — le gradient disparaît

Dans le cas one-hot, chaque pᵢ vaut 0 ou 1. Alors pᵢ(δᵢⱼ − pⱼ) vaut 0 dans tous les cas : si pᵢ = 0, le facteur pᵢ est nul ; si pᵢ = 1, alors i = * et δᵢⱼ − pⱼ = 0 pour tout j (1 − 1 si j = *, 0 − 0 sinon). Toutes les dérivées s'annulent : le modèle ne reçoit plus aucun signal pour corriger ses requêtes et ses clés. Le théorème 3 empêche d'arriver là dès l'initialisation.

---

## 8. Théorème 5 — La sortie est une moyenne pondérée, et l'attention ignore l'ordre

### Énoncé (a) — enveloppe convexe

$$
\mathbf{o}_i = \sum_{j=1}^{m} A_{ij}\,\mathbf{v}_j, \quad A_{ij} \ge 0, \quad \sum_{j} A_{ij} = 1 \quad\Longrightarrow\quad \min_j v_{jl} \le o_{il} \le \max_j v_{jl} \ \ \text{pour chaque coordonnée } l
$$

**o_il** : la coordonnée l de la sortie du token i. **v_jl** : la coordonnée l de la valeur du token j.

### Rôle

L'attention ne crée pas d'information nouvelle : elle **mélange** ce qui est déjà dans les valeurs. Si l'information n'est dans aucun token du contexte, l'attention ne peut pas la produire. C'est l'argument mathématique qui justifie le RAG : il faut mettre le fait dans le contexte pour qu'il puisse être lu.

### Démonstration de (a)

Notons mₗ = minⱼ v_jl. Comme chaque Aᵢⱼ ≥ 0, remplacer v_jl par mₗ ne peut que diminuer la somme :

$$
o_{il} = \sum_{j} A_{ij}\, v_{jl} \ \ge\ \sum_{j} A_{ij}\, m_l = m_l \sum_{j} A_{ij} = m_l
$$

La dernière égalité vient du théorème 1. Même raisonnement avec le maximum. ∎

### Énoncé (b) — équivariance par permutation

Si on permute les lignes de X (on mélange l'ordre des tokens), les lignes de la sortie sont permutées de la même façon, sans autre changement.

$$
\operatorname{Attention}(PX W_Q,\ PX W_K,\ PX W_V) = P \cdot \operatorname{Attention}(X W_Q,\ X W_K,\ X W_V)
$$

**P (matrice de permutation)** : une matrice de 0 et de 1 qui réordonne les lignes. Elle vérifie Pᵀ P = I (I : la matrice identité).

### Démonstration de (b)

Les scores deviennent (PQ)(PK)ᵀ = P Q Kᵀ Pᵀ : mêmes nombres, lignes et colonnes réordonnées. La softmax ligne par ligne commute avec ce réordonnancement, donc A devient P A Pᵀ. Enfin :

$$
(P A P^\top)(P V) = P A (P^\top P) V = P A V
$$

∎ Conséquence : « le chien mord l'homme » et « l'homme mord le chien » donnent les mêmes vecteurs, simplement dans un autre ordre. Sans encodage de position (`06-Attention-et-Transformer/35-Encodage-de-Position.md`), le modèle ne connaît pas l'ordre des mots.

---

## 9. Coût de calcul

$$
\underbrace{Q K^\top}_{n \times d_k \ \cdot\ d_k \times m} \ :\ O(n\, m\, d_k) \qquad\qquad \underbrace{A V}_{n \times m \ \cdot\ m \times d_v} \ :\ O(n\, m\, d_v)
$$

**O(·) (grand O)** : l'ordre de grandeur du nombre d'opérations quand les tailles grandissent. **Accolade du dessous** : la taille des matrices multipliées.

En self-attention, m = n : le coût est en O(n² d) et la mémoire de A en O(n²). Doubler la longueur du contexte multiplie par 4 le coût de cette étape. C'est la raison du coût élevé des longs contextes et l'intérêt de ne mettre dans le prompt que les chunks utiles (étape 28 bis).

---

## 10. Démonstration numérique

Une requête, trois clés, dₖ = 2. Pour simplifier, les valeurs sont égales aux clés.

$$
\mathbf{q} = [1{,}0;\ 0{,}0], \qquad \mathbf{k}_1 = [0{,}9;\ 0{,}1], \qquad \mathbf{k}_2 = [0{,}1;\ 0{,}9], \qquad \mathbf{k}_3 = [0{,}5;\ 0{,}5]
$$

**Étape 1 — scores bruts** (produits scalaires) :

$$
\mathbf{q}\cdot\mathbf{k}_1 = 0{,}9, \qquad \mathbf{q}\cdot\mathbf{k}_2 = 0{,}1, \qquad \mathbf{q}\cdot\mathbf{k}_3 = 0{,}5
$$

**Étape 2 — mise à l'échelle** par √2 ≈ 1,41421 :

$$
z_1 = \frac{0{,}9}{\sqrt{2}} \approx 0{,}63640, \qquad z_2 = \frac{0{,}1}{\sqrt{2}} \approx 0{,}07071, \qquad z_3 = \frac{0{,}5}{\sqrt{2}} \approx 0{,}35355
$$

**Étape 3 — exponentielles** :

$$
e^{z_1} \approx 1{,}88966, \qquad e^{z_2} \approx 1{,}07327, \qquad e^{z_3} \approx 1{,}42412, \qquad \sum_l e^{z_l} \approx 4{,}38705
$$

**Étape 4 — poids d'attention** (théorème 1 : ils somment à 1) :

$$
A_1 = \frac{1{,}88966}{4{,}38705} \approx 0{,}43074, \qquad A_2 \approx 0{,}24465, \qquad A_3 \approx 0{,}32462
$$

**Étape 5 — sortie** (mélange des valeurs) :

$$
\mathbf{o} = 0{,}43074 \cdot [0{,}9;\ 0{,}1] + 0{,}24465 \cdot [0{,}1;\ 0{,}9] + 0{,}32462 \cdot [0{,}5;\ 0{,}5] \approx [0{,}57444;\ 0{,}42556]
$$

Vérification du théorème 5 (a) : 0,57444 est bien entre 0,1 et 0,9 (min et max des premières coordonnées). Et comme chaque valeur a des coordonnées qui somment à 1, la sortie aussi : 0,57444 + 0,42556 = 1.

Lecture : la requête [1 ; 0] « ressemble » le plus à k₁, qui reçoit 43 % de l'attention. Mais avec dₖ = 2 et des scores faibles, l'attention reste assez étalée. Si on multiplie les scores par 10 (théorème 4), k₁ prend environ 98 % du poids.

---

## 11. Code — tout vérifier

Bibliothèque standard uniquement. Les `assert` reprennent les nombres du §10 et les théorèmes.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(z)`** — Cette fonction est un trésorier prudent qui partage un budget d'attention entre plusieurs candidats : elle reçoit la liste z des scores, retranche d'abord le plus grand d'entre eux à chacun, comme le permet le théorème 2, puis prend l'exponentielle de chaque score décalé et divise chacune par leur somme. Elle renvoie une liste de poids strictement positifs qui totalisent 1, sans jamais déborder, même pour des scores de l'ordre de 1000 ; c'est elle qu'utilisent l'attention, les tests de saturation du théorème 4 et la vérification du jacobien par dérivée numérique.

**`softmax_naive(z)`** — Voici le frère imprudent du trésorier, gardé exprès pour montrer l'accident : il reçoit la même liste de scores, mais prend l'exponentielle de chacun sans aucun décalage avant de diviser par la somme, ce qui donne les mêmes poids sur des petits nombres et une catastrophe sur les grands. Avec les scores `[1000.0, 999.0]`, `math.exp(1000)` dépasse ce qu'un flottant peut contenir et la fonction lève une `OverflowError` ; `main` attend précisément cette exception pour illustrer le théorème 2, alors que `softmax` rend sans broncher le poids 1 / (1 + e⁻¹) sur les mêmes scores.

**`dot(a, b)`** — Ce petit outil joue le rôle d'un caissier qui fait le compte de deux colonnes alignées : il reçoit deux vecteurs a et b, multiplie leurs coordonnées deux à deux et additionne les produits, puis renvoie ce nombre, le produit scalaire. Il ne vérifie pas que les longueurs sont égales (`zip` s'arrête simplement au plus court des deux) ; il sert à calculer les scores requête-clé dans `attention_one_query` et les 4 000 produits aléatoires en dimension 128 de l'expérience de Monte-Carlo du théorème 3.

**`attention_one_query(q, K, V)`** — Cette fonction raconte une seule question posée à un comité : elle reçoit la requête q, la liste K des clés et la liste V des valeurs, calcule pour chaque clé le score q · k divisé par √dₖ, transforme ces scores en poids avec `softmax`, puis compose la sortie coordonnée par coordonnée en additionnant les valeurs pondérées par ces poids. Elle renvoie les trois étapes à la fois, scores, poids et sortie, et sur l'exemple du §10 on retrouve les scores 0,63640, 0,07071 et 0,35355, les poids 0,43074, 0,24465 et 0,32462, puis la sortie [0,57444 ; 0,42556], que `main` vérifie à 10⁻⁵ près.

**`attention(Q, K, V)`** — C'est le président de séance qui fait passer toutes les questions l'une après l'autre devant le même comité : la fonction reçoit la liste Q des requêtes ainsi que les clés K et les valeurs V communes, appelle `attention_one_query` pour chaque requête et ne garde que le troisième élément du résultat, la sortie. Elle renvoie la liste des sorties, une par requête, et `main` s'en sert pour le théorème 5 (b) : permuter les jetons par l'ordre `[2, 0, 1]` ne fait que permuter les sorties, sans en changer une seule valeur.

**`main()`** — Le chef d'orchestre reprend un à un les nombres du §10 et les cinq théorèmes : il calcule l'attention de la requête [1 ; 0] sur les trois clés et compare scores, poids et sortie aux valeurs écrites à la main, vérifie que les poids sont positifs et somment à 1, qu'un décalage de 1000 ne change rien alors que `softmax_naive` déborde, puis tire avec la graine 0 quatre mille couples en dimension 128 pour constater que la variance brute reste entre 0,85 et 1,15 fois dₖ et que la variance divisée reste proche de 1. Il contrôle ensuite la saturation (poids supérieur à 0,98 quand les scores sont multipliés par 10, poids proches d'un tiers quand ils sont écrasés), le jacobien par différences finies, l'encadrement de la sortie et l'effet d'une permutation, avant d'imprimer les résultats et le message final, qui n'apparaît que si tous les `assert` sont passés.

```python
import math


def softmax(z):
    m = max(z)                          # Théorème 2 : on décale par le max
    e = [math.exp(x - m) for x in z]
    s = sum(e)
    return [x / s for x in e]


def softmax_naive(z):
    e = [math.exp(x) for x in z]
    s = sum(e)
    return [x / s for x in e]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def attention_one_query(q, K, V):
    d_k = len(q)
    scores = [dot(q, k) / math.sqrt(d_k) for k in K]
    weights = softmax(scores)
    d_v = len(V[0])
    out = [sum(weights[j] * V[j][l] for j in range(len(V))) for l in range(d_v)]
    return scores, weights, out


def attention(Q, K, V):
    return [attention_one_query(q, K, V)[2] for q in Q]


def main() -> None:
    # §10 — calcul à la main
    q = [1.0, 0.0]
    K = [[0.9, 0.1], [0.1, 0.9], [0.5, 0.5]]
    V = [row[:] for row in K]
    scores, w, o = attention_one_query(q, K, V)

    assert all(math.isclose(a, b, abs_tol=1e-5) for a, b in zip(scores, [0.63640, 0.07071, 0.35355]))
    assert all(math.isclose(a, b, abs_tol=1e-5) for a, b in zip(w, [0.43074, 0.24465, 0.32462]))
    assert all(math.isclose(a, b, abs_tol=1e-5) for a, b in zip(o, [0.57444, 0.42556]))

    # Théorème 1 — distribution de probabilité
    assert all(x > 0 for x in w) and math.isclose(sum(w), 1.0)

    # Théorème 2 — décalage sans effet, et stabilité numérique
    assert all(math.isclose(a, b) for a, b in zip(softmax([s + 1000 for s in scores]), w))
    try:
        softmax_naive([1000.0, 999.0])
        raise AssertionError("la version naïve aurait dû déborder")
    except OverflowError:
        pass
    assert math.isclose(softmax([1000.0, 999.0])[0], 1 / (1 + math.exp(-1)))

    # Théorème 3 — variance des scores avec et sans √d_k (Monte-Carlo, graine fixe)
    import random
    random.seed(0)
    d_k, trials = 128, 4000
    raw = []
    for _ in range(trials):
        qq = [random.gauss(0, 1) for _ in range(d_k)]
        kk = [random.gauss(0, 1) for _ in range(d_k)]
        raw.append(dot(qq, kk))
    var_raw = sum(x * x for x in raw) / trials
    var_scaled = var_raw / d_k
    assert 0.85 * d_k < var_raw < 1.15 * d_k
    assert 0.85 < var_scaled < 1.15

    # Théorème 4 — saturation : grand facteur -> one-hot, petit -> uniforme
    sharp = softmax([10 * s for s in [0.9, 0.1, 0.5]])
    flat = softmax([0.001 * s for s in [0.9, 0.1, 0.5]])
    assert sharp[0] > 0.98
    assert all(math.isclose(x, 1 / 3, abs_tol=1e-3) for x in flat)
    # Jacobien p_i (δ_ij - p_j), comparé à une dérivée numérique
    z = [0.9, 0.1, 0.5]
    p = softmax(z)
    h = 1e-6
    for i in range(3):
        for j in range(3):
            zp = z[:]
            zp[j] += h
            num = (softmax(zp)[i] - p[i]) / h
            ana = p[i] * ((1 if i == j else 0) - p[j])
            assert math.isclose(num, ana, abs_tol=1e-5)

    # Théorème 5 (a) — la sortie reste entre min et max des valeurs
    for l in range(2):
        col = [v[l] for v in V]
        assert min(col) <= o[l] <= max(col)

    # Théorème 5 (b) — permuter les tokens permute les sorties
    X_Q = [[1.0, 0.0], [0.2, 0.7], [0.4, 0.4]]
    perm = [2, 0, 1]
    out = attention(X_Q, K, V)
    out_perm = attention([X_Q[i] for i in perm], [K[i] for i in perm], [V[i] for i in perm])
    for a, i in zip(out_perm, perm):
        assert all(math.isclose(x, y) for x, y in zip(a, out[i]))

    print("scores  :", [round(x, 5) for x in scores])
    print("poids   :", [round(x, 5) for x in w])
    print("sortie  :", [round(x, 5) for x in o])
    print(f"variance brute ~ {var_raw:.1f} (d_k = {d_k}), apres division par sqrt(d_k) ~ {var_scaled:.2f}")
    print(f"poids de k1 avec scores x10 : {sharp[0]:.3f}")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
scores  : [0.6364, 0.07071, 0.35355]
poids   : [0.43074, 0.24465, 0.32462]
sortie  : [0.57444, 0.42556]
variance brute ~ 130.7 (d_k = 128), apres division par sqrt(d_k) ~ 1.02
poids de k1 avec scores x10 : 0.982
OK — toutes les vérifications sont passées.
```

La ligne de variance vient d'un tirage aléatoire à graine fixe (`random.seed(0)`). Avec une autre graine, elle change un peu mais reste proche de 128 et de 1, ce que les `assert` vérifient.

---

### Déroulé, ligne par ligne

`softmax` calcule d'abord le plus grand score, puis l'exponentielle de chaque score diminué de ce maximum, et divise chacune par leur somme : c'est le théorème 2 appliqué dans le code, puisque retrancher la même constante à tous les scores ne change pas le résultat, mais garantit que le plus grand exposant vaut 0 et qu'aucune exponentielle ne déborde. `softmax_naive` fait le même calcul sans cette soustraction ; elle est gardée uniquement pour montrer qu'elle échoue sur des scores de l'ordre de 1 000, ce que le programme vérifie en attendant une `OverflowError`.

`dot` est le produit scalaire du fichier 28 bis. `attention_one_query` calcule, pour une requête, le score de chaque clé divisé par √dₖ, passe ces scores dans la softmax pour obtenir les poids, puis forme la sortie coordonnée par coordonnée comme la somme des valeurs pondérées par ces poids. `attention` applique simplement `attention_one_query` à chaque requête, ce qui suffit à vérifier l'équivariance par permutation.

Le programme principal reprend le calcul du paragraphe 10 (scores 0,63640 ; 0,07071 ; 0,35355, poids 0,43074 ; 0,24465 ; 0,32462, sortie [0,57444 ; 0,42556]), vérifie les théorèmes un par un, estime par simulation la variance du produit scalaire de deux vecteurs aléatoires de dimension 128 (environ 128 avant division, environ 1 après), compare le jacobien p_i (δ_ij − p_j) à une dérivée numérique, et vérifie que la sortie reste entre le minimum et le maximum des valeurs.

## Squelette algorithmique

```text
ALGORITHME AttentionUneRequête
ENTRÉES : requête q (dimension d_k), clés k₁ … k_n, valeurs v₁ … v_n (dimension d_v)
SORTIE  : la sortie o et les poids a

  POUR j DE 1 À n FAIRE  zⱼ ← (q · kⱼ) / √d_k  FIN POUR
  m ← max z
  POUR j DE 1 À n FAIRE  eⱼ ← exp(zⱼ − m)  FIN POUR       (théorème 2 : sans effet sur le résultat)
  POUR j DE 1 À n FAIRE  aⱼ ← eⱼ / Σ e  FIN POUR           (théorème 1 : aⱼ > 0 et Σ aⱼ = 1)
  POUR c DE 1 À d_v FAIRE  o_c ← Σⱼ aⱼ × vⱼ,c  FIN POUR    (théorème 5 : o_c reste entre min et max des vⱼ,c)
  RETOURNER o, a
```

**Complexité.** Une requête coûte O(n × d_k) pour les scores, O(n) pour la softmax et O(n × d_v) pour la sortie. Pour n requêtes, on retrouve le O(n² d) du paragraphe 9. La simulation de variance du programme coûte O(tirages × d_k) et la vérification du jacobien O(n²) dérivées numériques.

**Du squelette au code.** La première boucle est la compréhension de liste de `attention_one_query` qui appelle `dot`, les trois lignes suivantes sont `softmax`, et la dernière boucle est le calcul de `out`. `attention` répète l'algorithme pour chaque requête.

## 12. Pièges

- **Oublier la soustraction du max** dans une softmax écrite à la main : `inf`, puis `nan` dès que les scores dépassent environ 709 (limite de `math.exp`).
- **Confondre clé et valeur.** La clé décide **qui** est lu, la valeur décide **ce qui** est lu.
- **Croire qu'un long contexte est gratuit.** Le budget d'attention total est 1 par token (théorème 1) et le coût est quadratique (§9).
- **Croire que l'attention comprend l'ordre.** Elle est équivariante par permutation (théorème 5 b) : l'ordre vient de l'encodage de position.

## 13. Exercice feuille blanche

1. Démontrer que la softmax somme à 1 et ne change pas quand on ajoute 5 à tous les scores.
2. Démontrer Var(q · k) = dₖ sous les hypothèses du théorème 3, puis expliquer ce qui se passerait si on divisait par dₖ.
3. Dériver ∂pᵢ/∂zⱼ et montrer que toutes les dérivées s'annulent pour une distribution one-hot.
4. Refaire le calcul du §10 avec q = [0 ; 1] et vérifier que k₂ reçoit maintenant le plus de poids.
