# Étape 30 quinquies — RAG — Index ANN : HNSW, IVF et PQ

**Dossier :** 05-RAG

> Étape 30 quinquies du parcours · Prérequis : [Découpage avancé et compression](<30d-RAG-Decoupage-Avance-et-Compression.md>) · Suite : [Corrective RAG et Agentic RAG](<30f-RAG-Corrective-et-Agentic-RAG.md>)

## Définition

Une recherche **exacte** des plus proches voisins compare la question à chacun des N vecteurs de la base : c'est l'index « plat » des étapes 14 et 18, dont le coût croît comme N × d. Une recherche **approchée**, ou ANN (Approximate Nearest Neighbor), accepte de manquer quelques vrais voisins pour aller beaucoup plus vite, ou pour occuper beaucoup moins de mémoire. Trois idées couvrent l'essentiel des index du marché. L'**IVF** (inverted file, fichier inversé) partitionne la base en C groupes appris par k-means et ne fouille que les nprobe groupes dont le centre est le plus proche de la question. La **PQ** (product quantization, quantification par produit) compresse chaque vecteur en m octets et calcule des distances approchées par simple lecture de tables. Le **HNSW** (Hierarchical Navigable Small World) relie les vecteurs en un graphe à plusieurs couches et y cherche en se déplaçant de voisin en voisin. La qualité d'un index approché se mesure par son **Recall@k contre la recherche exacte** : la part des k vrais plus proches voisins qu'il renvoie, comme dans le cas du secteur public de l'étape 25.

## Rôle dans un agent

L'index sert à l'étape **percevoir** : l'outil de recherche documentaire de l'agent (`chercher_base` à l'étape 30 sexies), comme la mémoire à long terme de l'étape 15 bis, l'appelle à chaque question, parfois plusieurs fois par tour quand l'agent reformule ou décompose sa requête (étape 30 ter). Sa latence entre donc dans le budget de chaque tour, et son p95 compte plus que sa moyenne. Son rappel plafonne tout ce qui suit : le reranker de l'étape 30 bis ne reclasse que ce que l'index lui a donné, si bien qu'un document que l'index n'a pas renvoyé est perdu pour la réponse, quel que soit le modèle placé derrière. Dans une architecture hexagonale, l'index est un port, avec deux opérations, `ajouter(id, vecteur)` et `chercher(vecteur, k)`. L'index plat de ce fichier, une bibliothèque comme FAISS ou hnswlib, une extension comme pgvector ou une base vectorielle ne sont que des adaptateurs, cités ici comme exemples du marché. La règle d'indépendance est simple : on conserve les vecteurs bruts et l'identifiant du modèle d'embedding qui les a produits. L'index devient alors un cache que l'on peut reconstruire, comparer à la recherche exacte et changer de fournisseur sans rien perdre.

## Équation complète

Coût de la recherche exacte, en multiplications par requête :

$$
\text{Coût}_{\text{exact}}(N, d) = N \, d
$$

Objectif du k-means et ses deux demi-étapes (algorithme de Lloyd) :

$$
J(c, \mu) = \sum_{i=1}^{N} \lVert x_i - \mu_{c(i)} \rVert^2
$$

$$
c(i) \leftarrow \arg\min_{1 \le j \le C} \lVert x_i - \mu_j \rVert^2 \qquad \text{(affectation)}
$$

$$
\mu_j \leftarrow \frac{1}{\lvert S_j \rvert} \sum_{i \in S_j} x_i , \qquad S_j = \{\, i : c(i) = j \,\} \qquad \text{(mise à jour)}
$$

Recherche IVF : candidats, coût, nombre de listes optimal à nprobe fixé, rappel :

$$
S(q) = \bigcup_{j \in \mathcal{L}(q)} S_j , \qquad \mathcal{L}(q) = \text{les nprobe indices } j \text{ de plus petit } \lVert q - \mu_j \rVert
$$

$$
\text{Coût}_{\text{IVF}} \approx \left( C + \text{nprobe} \cdot \frac{N}{C} \right) d
$$

$$
C^{*} = \sqrt{N \cdot \text{nprobe}} , \qquad \text{Coût}_{\text{IVF}}(C^{*}) \approx 2 \sqrt{N \cdot \text{nprobe}} \; d
$$

$$
\text{Recall@}k(q) = \frac{\lvert V_k(q) \cap S(q) \rvert}{k}
$$

Quantification par produit, distance asymétrique (ADC), borne d'erreur et mémoire :

$$
x = \big( x^{(1)}, \dots, x^{(m)} \big) , \qquad x^{(j)} \in \mathbb{R}^{d/m}
$$

$$
u_j(x) = \arg\min_{0 \le s < K^{*}} \lVert x^{(j)} - c_{j,s} \rVert^2 , \qquad \hat{x} = \big( c_{1,u_1(x)}, \dots, c_{m,u_m(x)} \big)
$$

$$
T_j[s] = \lVert q^{(j)} - c_{j,s} \rVert^2 , \qquad \tilde{d}(q, x) = \sum_{j=1}^{m} T_j\big[u_j(x)\big] = \lVert q - \hat{x} \rVert^2
$$

$$
\big|\, \lVert q - x \rVert - \lVert q - \hat{x} \rVert \,\big| \le \lVert x - \hat{x} \rVert
$$

$$
4d \text{ octets (float32)} \;\longrightarrow\; \frac{m \log_2 K^{*}}{8} \text{ octets} = m \text{ octets si } K^{*} = 256
$$

HNSW : tirage du niveau d'un nœud et sa loi :

$$
L = \big\lfloor -\ln(U) \, m_L \big\rfloor , \qquad U \text{ uniforme sur } ]0 \,;\, 1] , \qquad m_L = \frac{1}{\ln M}
$$

$$
P(L \ge l) = M^{-l} , \qquad \mathbb{E}\big[ N_{\ge l} \big] = N \, M^{-l} , \qquad L_{\max} \approx \log_M N , \qquad \mathbb{E}[L] = \frac{1}{M - 1}
$$

## Décryptage des symboles

$$
N,\; d
$$

Nombre de vecteurs de la base et dimension de chacun (la dimension était notée n à l'étape 18) ; entiers ≥ 1 ; variables `N` et `D`.

$$
q,\; x_i
$$

Le vecteur de la question et le i-ème vecteur de la base, normés comme à l'étape 14 ; listes de d réels ; variables `q` et `base[i]`.

$$
k,\; V_k(q)
$$

Le nombre de voisins demandés (le k du top-k, étape 25) et l'ensemble des k vrais plus proches voisins, donnés par la recherche exacte ; variables `K` et `vrais`.

$$
C,\; \mu_j,\; c(i),\; S_j
$$

Le nombre de listes de l'IVF (appelé nlist dans FAISS), le centre de la liste j, la liste à laquelle le vecteur i est affecté et l'ensemble des vecteurs de la liste j ; variables `n_listes`, `centres[j]`, `plus_proche(p, centres)` et `listes[j]`.

$$
J(c, \mu)
$$

L'objectif du k-means, somme des distances au carré de chaque vecteur à son centre ; réel ≥ 0 ; fonction `objectif(points, centres, affect)`, dont la suite des valeurs est `historique`.

$$
\text{nprobe},\; \mathcal{L}(q),\; S(q)
$$

Le nombre de listes visitées (de 1 à C), les indices de ces listes et l'ensemble des vecteurs candidats qu'elles contiennent ; variables `nprobe` et `candidats(q, nprobe)`. L'étape 18 notait p ce nombre, mais p désigne une probabilité dans le parcours.

$$
m,\; K^{*},\; x^{(j)}
$$

Le nombre de sous-vecteurs, le nombre de centres par sous-espace (au plus 256 pour tenir dans un octet) et le j-ème sous-vecteur de x, de dimension d/m ; variables `m`, `k_etoile` et `morceau(x, j)`.

$$
c_{j,s},\; u_j(x),\; \hat{x}
$$

Le centre numéro s du dictionnaire j, le code de x dans le sous-espace j (un entier de 0 à K* − 1) et la reconstruction de x à partir de ses m codes ; variables `dicos[j][s]`, `encoder(x)[j]` et `decoder(code)`.

$$
T_j[s],\; \tilde{d}(q, x)
$$

La table des distances de la question à chaque centre, calculée une fois par requête, et la distance asymétrique de q à x, somme de m lectures de table ; variables `table(q)[j][s]` et `adc(table, code)`.

$$
M,\; M_0,\; m_L
$$

Le nombre de liens créés par insertion dans le HNSW (M), le plafond de liens par nœud sur la couche 0 (2M) et le facteur de niveau 1/ln M ; variables `M`, `M0` et `mL`. Ce M n'est pas le nombre de souvenirs de l'étape 15 : c'est le nom du paramètre dans les bibliothèques.

$$
L,\; U,\; \text{ef}
$$

Le niveau le plus haut d'un nœud, le nombre uniforme qui sert à le tirer et la largeur du faisceau de recherche (ef ≥ k ; ef_construction à l'insertion) ; variables `niv`, `1.0 - rng.random()`, `ef` et `efc`.

## Démonstration

### 1. L'algorithme de Lloyd ne fait jamais monter J

**L'affectation ne fait pas monter J.** À centres fixés, chaque vecteur xᵢ passe dans la liste du centre le plus proche. Ce centre minimise ‖xᵢ − μⱼ‖² parmi tous les j, donc en particulier sa distance est au plus celle de l'ancien centre de xᵢ. En sommant sur i, le nouvel objectif est au plus l'ancien.

**La mise à jour ne fait pas monter J.** À affectation fixée, chaque liste Sⱼ contribue au terme Σ ‖xᵢ − μ‖², et l'on montre que la moyenne x̄ⱼ de la liste est le meilleur choix de μ. On écrit xᵢ − μ = (xᵢ − x̄ⱼ) + (x̄ⱼ − μ) et l'on développe le carré :

$$
\sum_{i \in S_j} \lVert x_i - \mu \rVert^2 = \sum_{i \in S_j} \lVert x_i - \bar{x}_j \rVert^2 + 2 \, (\bar{x}_j - \mu) \cdot \sum_{i \in S_j} (x_i - \bar{x}_j) + \lvert S_j \rvert \, \lVert \bar{x}_j - \mu \rVert^2
$$

Le terme du milieu est nul, parce que la somme des écarts à la moyenne vaut zéro par définition de la moyenne. Il reste un premier terme qui ne dépend pas de μ et un dernier terme positif, nul seulement si μ = x̄ⱼ. La moyenne est donc l'unique minimum, et remplacer μⱼ par la moyenne de sa liste ne peut que faire baisser J ou le laisser égal. Un centre dont la liste est vide garde sa position, ce qui ne change pas J.

**Conséquences.** J est positif et ne monte jamais, donc la suite de ses valeurs converge. Si l'on ne change l'affectation d'un vecteur qu'en cas d'amélioration stricte, chaque changement fait baisser J strictement ; comme il n'existe qu'un nombre fini de partitions (au plus Cᴺ), aucune ne peut revenir et l'algorithme s'arrête en un nombre fini d'itérations. Le code départage les égalités par le plus petit indice et ajoute un plafond d'itérations, ce que font aussi les bibliothèques. L'arrêt se fait sur un **minimum local** : un autre choix de centres initiaux peut donner un J plus bas.

**Exemple fait à la main.** Six points sur une droite, 1, 2, 3, 10, 11 et 12, et deux centres initiaux, 1 et 2 :

| Demi-étape | Centres | Affectation | J |
|---|---|---|---|
| affectation 1 | 1 et 2 | {1} et {2, 3, 10, 11, 12} | 0 + 0 + 1 + 64 + 81 + 100 = 246 |
| mise à jour 1 | 1 et 7,6 | inchangée | 0 + 31,36 + 21,16 + 5,76 + 11,56 + 19,36 = 89,2 |
| affectation 2 | 1 et 7,6 | {1, 2, 3} et {10, 11, 12} | 0 + 1 + 4 + 5,76 + 11,56 + 19,36 = 41,68 |
| mise à jour 2 | 2 et 11 | inchangée | 1 + 0 + 1 + 1 + 0 + 1 = 4 |
| affectation 3 | 2 et 11 | inchangée : arrêt | 4 |

Le code retrouve la suite 246 → 89,2 → 41,68 → 4. Sur la base de 500 vecteurs du programme, J passe de 389,40 à 224,57 et l'affectation ne bouge plus après 18 itérations.

### 2. Le coût de l'IVF et le nombre de listes optimal

Une requête IVF compare d'abord q aux C centres, puis aux vecteurs des nprobe listes choisies. Si les listes sont de taille égale, chacune contient N/C vecteurs, et le nombre de distances vaut

$$
f(C) = C + \frac{\text{nprobe} \cdot N}{C} , \qquad f'(C) = 1 - \frac{\text{nprobe} \cdot N}{C^2} , \qquad f''(C) = \frac{2 \, \text{nprobe} \cdot N}{C^3} > 0
$$

La dérivée s'annule pour C* = √(N · nprobe), et la dérivée seconde positive dit que c'est un minimum. En ce point, les deux termes valent chacun √(N · nprobe), d'où le coût 2√(N · nprobe) distances. Avec N = 10⁶, d = 768, C = 1 024 et nprobe = 8, on compare q à (1 024 + 8 × 10⁶/1 024) = 8 836,5 vecteurs, soit 6 786 048 multiplications au lieu de 768 000 000 : 113 fois moins. Pour ce nprobe, C* vaudrait √(8 × 10⁶) ≈ 2 828.

Deux réserves. D'abord, C* minimise le coût **à nprobe fixé**, pas le compromis entre coût et rappel : avec 2 828 listes, 8 listes visitées ne couvrent plus que 0,28 % de la base au lieu de 0,78 %, et le rappel baisse. En pratique, on choisit C de l'ordre de √N (règle empirique), puis on augmente nprobe jusqu'au rappel visé, mesuré. Ensuite, le k-means ne produit pas des listes égales : dans le programme, elles vont de 22 à 47 vecteurs. Le coût réel dépend de la taille des listes visitées, et une requête qui tombe dans une région dense en paie le prix. Le modèle reste pourtant bon en moyenne : avec C = 16 et N = 500, il prévoit 16 + 500/16 = 47,25 distances pour nprobe = 1, et le programme en mesure 45,7 ; pour nprobe = 4, il prévoit 141 et le programme mesure 140,8.

### 3. Le rappel de l'IVF est la part des vrais voisins tombés dans les listes visitées

**Lemme du reclassement.** Soit S une partie de la base, et R le résultat d'une recherche exacte limitée à S : les k éléments de S de plus petite distance à q, égalités départagées par l'identifiant. Alors tout vrai voisin présent dans S est dans R. En effet, si x appartient à Vₖ(q) ∩ S, les éléments de S qui le précèdent dans l'ordre (distance, identifiant) le précèdent aussi dans la base entière, et ils sont au plus k − 1 parce que x est parmi les k premiers de la base ; x figure donc parmi les k premiers de S. On en déduit Vₖ(q) ∩ R = Vₖ(q) ∩ S, d'où la formule du rappel donnée plus haut.

Trois conséquences, que le programme vérifie requête par requête :

- **Le rappel ne baisse jamais quand nprobe augmente.** Pour une requête donnée, les listes sont visitées dans l'ordre des distances aux centres : les nprobe premières font partie des nprobe + 1 premières, donc S(q) grandit et Vₖ(q) ∩ S(q) aussi. Avec nprobe = C, S(q) est la base entière et le rappel vaut 1. Le programme mesure 0,510 ; 0,695 ; 0,900 ; 0,985 et 1,000 pour nprobe = 1, 2, 4, 8 et 16.
- **La seule perte vient de la frontière.** Un vrai voisin manqué est un vecteur rangé dans une liste dont le centre n'est pas parmi les nprobe plus proches de q, typiquement une question posée entre deux thèmes.
- **Le reclassement après PQ rattrape tout ce qui est parmi les candidats.** Avec S égal aux R meilleurs vecteurs selon la distance ADC, le rappel après reclassement exact vaut |Vₖ ∩ S|/k. Comme les k meilleurs selon l'ADC font partie des R meilleurs, il est au moins égal au rappel de l'ADC seule : 0,990 contre 0,685 dans le programme, avec R = 40.

C'est le même raisonnement qu'à l'étape 30 bis : une étape de précision placée derrière une étape de rappel ne peut pas dépasser le rappel de celle-ci.

### 4. La distance ADC est exactement la distance à la reconstruction

Le carré de la distance euclidienne est une somme sur les coordonnées. On regroupe ces coordonnées par blocs de d/m, puis on remplace chaque bloc de x̂ par le centre qu'il désigne :

$$
\lVert q - \hat{x} \rVert^2 = \sum_{t=1}^{d} (q_t - \hat{x}_t)^2 = \sum_{j=1}^{m} \lVert q^{(j)} - \hat{x}^{(j)} \rVert^2 = \sum_{j=1}^{m} \lVert q^{(j)} - c_{j,u_j(x)} \rVert^2 = \sum_{j=1}^{m} T_j\big[u_j(x)\big]
$$

La distance est dite **asymétrique** parce que q reste exacte : seul x est quantifié. La variante symétrique (SDC) quantifie aussi la question et ajoute une erreur de plus. Le coût par requête se calcule directement. La table demande m × K* × (d/m) = K* × d multiplications, une seule fois ; ensuite, chaque vecteur de la base ne coûte plus que m lectures et m − 1 additions, au lieu de d multiplications. Pour N = 10⁶, d = 768, m = 96 et K* = 256, cela fait 196 608 multiplications et 96 millions de lectures, au lieu de 768 millions de multiplications. La mémoire passe de 4d = 3 072 octets par vecteur à m = 96 octets, soit 32 fois moins : 3,072 Go deviennent 96 Mo, plus des dictionnaires de 4 × K* × d = 786 432 octets, partagés par toute la base.

**Borne d'erreur.** Par l'inégalité triangulaire, ‖q − x‖ ≤ ‖q − x̂‖ + ‖x̂ − x‖ et ‖q − x̂‖ ≤ ‖q − x‖ + ‖x − x̂‖, d'où la borne de l'équation complète. Deux vecteurs ne peuvent donc être inversés par la PQ que si leurs vraies distances à q diffèrent de moins que la somme de leurs deux erreurs de quantification. C'est pourquoi un reclassement exact de quelques dizaines de candidats suffit à rattraper presque tout (point 3).

**Exemple fait à la main.** En dimension 4, avec m = 2 sous-vecteurs et deux centres par sous-espace : (0, 0) et (1, 1) pour le premier, (0, 0) et (2, 0) pour le second. Le vecteur x = (0,9 ; 1,2 ; 1,8 ; 0,1) a pour premier sous-vecteur (0,9 ; 1,2), à distance au carré 2,25 de (0, 0) et 0,05 de (1, 1) : code 1. Son second sous-vecteur (1,8 ; 0,1) est à 3,25 de (0, 0) et à 0,05 de (2, 0) : code 1. Sa reconstruction est x̂ = (1 ; 1 ; 2 ; 0). Pour la question q = (1 ; 0,2 ; 2 ; 1), la table vaut T₁ = [1,04 ; 0,64] et T₂ = [5 ; 1]. La distance ADC lit T₁[1] + T₂[1] = 0,64 + 1 = 1,64, qui est bien ‖q − x̂‖² = 0 + 0,64 + 0 + 1. La vraie distance au carré vaut 0,01 + 1 + 0,04 + 0,81 = 1,86. L'erreur de quantification vaut ‖x − x̂‖ = √0,10 ≈ 0,3162, et l'écart des distances, |√1,86 − √1,64| ≈ 1,3638 − 1,2806 = 0,0832, est bien en dessous.

### 5. Les niveaux du HNSW suivent une loi géométrique

Chaque nœud reçoit un niveau L tiré une fois pour toutes, et il est présent dans toutes les couches de 0 à L. Pour un entier l ≥ 0 :

$$
P(L \ge l) = P\big( -\ln(U)\, m_L \ge l \big) = P\big( U \le e^{-l/m_L} \big) = e^{-l \ln M} = M^{-l}
$$

La première égalité vient de ce que la partie entière d'un réel y est au moins l exactement quand y ≥ l, puisque l est entier. La deuxième vient de ce que −ln(U) m_L ≥ l équivaut à ln U ≤ −l/m_L, puis à U ≤ e⁻ˡᐟᵐᴸ, parce que m_L > 0 et que l'exponentielle est croissante. La troisième utilise P(U ≤ a) = a pour une loi uniforme sur ]0 ; 1], puis l/m_L = l ln M. Chaque couche contient donc en moyenne M fois moins de nœuds que celle du dessous, comme les étages d'une skip list. Par linéarité de l'espérance, le nombre attendu de nœuds de niveau au moins l vaut N M⁻ˡ : pour N = 500 et M = 8, cela donne 62,5, 7,8 et 1,0 pour l = 1, 2 et 3 ; le programme en compte 56, 6 et 1. La couche la plus haute est celle où l'on attend environ un nœud, N M⁻ˡ ≈ 1, soit l ≈ ln N / ln M = log_M N : 2,99 pour N = 500 et M = 8 (le programme obtient 3), 4,98 pour N = 10⁶ et M = 16.

Pour un entier positif, l'espérance est la somme des probabilités de queue. C'est une série géométrique, déjà sommée à l'étape 11 :

$$
\mathbb{E}[L] = \sum_{l=1}^{\infty} P(L \ge l) = \sum_{l=1}^{\infty} M^{-l} = \frac{1/M}{1 - 1/M} = \frac{1}{M - 1}
$$

Les couches hautes coûtent donc peu de mémoire. Chaque nœud a au plus M₀ = 2M liens sur la couche 0, et en moyenne 1/(M − 1) niveau supplémentaire à M liens. Pour M = 16 et des identifiants de 4 octets, cela fait au plus 128 octets par nœud, plus environ 4,3 octets en moyenne pour les couches hautes, à côté des 3 072 octets d'un vecteur de 768 float32.

### 6. La recherche gloutonne s'arrête, mais sur un minimum local

Sur une couche, la recherche gloutonne part d'un point d'entrée et passe au voisin le plus proche de q tant qu'il est **strictement** plus proche que le nœud courant. La distance à q diminue strictement à chaque saut, donc aucun nœud n'est visité deux fois, et la recherche s'arrête après au plus N − 1 sauts. Elle s'arrête sur un nœud dont tous les voisins sont plus loin de q que lui : c'est un minimum local de la distance sur le graphe, qui n'est pas forcément le plus proche voisin. Le programme le constate : la recherche gloutonne (ef = 1) ne trouve le vrai plus proche voisin que pour 15 requêtes sur 20, contre 19 sur 20 avec un faisceau ef = 10. Le faisceau garde les ef meilleurs nœuds rencontrés et explore les voisins de tout candidat plus proche que le pire d'entre eux : il échappe à beaucoup de minima locaux, au prix de plus de distances calculées. Sur la base du programme, ef = 10, 20, 40 et 80 donnent un Recall@10 de 0,950, 0,995, 1 et 1, pour 92,8, 132,2, 188,8 et 279,5 distances par requête, contre 500 pour la recherche exacte. Les couches hautes servent à arriver vite dans la bonne région : peu de nœuds, des liens qui traversent l'espace. Sur des données favorables, le nombre de sauts croît comme log N : c'est un comportement **observé**, pas une garantie (étape 18), et aucun résultat ne promet un rappel donné pour un ef donné. On le mesure.

## Effets et comportement

- **Augmenter nprobe** fait monter le rappel de l'IVF sans jamais le faire baisser (point 3) et fait croître le coût linéairement : de 45,7 à 516 distances par requête dans le programme, pour un rappel qui passe de 0,51 à 1.
- **Augmenter C** rétrécit les listes mais ajoute des centres à comparer et, à nprobe égal, fait baisser le rappel : on règle C une fois, de l'ordre de √N, puis nprobe en fonction du rappel mesuré.
- **Augmenter m ou K*** améliore la précision de la PQ et coûte de la mémoire (m log₂ K* / 8 octets par vecteur) ; K* fait aussi croître la table, K* × d multiplications par requête.
- **Reclasser R candidats** avec les vecteurs exacts rattrape les erreurs de la PQ (point 3) pour R × d multiplications de plus ; il faut alors garder les vecteurs exacts quelque part, souvent sur disque.
- **Augmenter ef** fait monter le rappel du HNSW en pratique (0,95 → 1) et le coût (92,8 → 279,5 distances). La monotonie n'est pas garantie en théorie, et ef doit rester au moins égal à k.
- **Augmenter M ou ef_construction** donne un meilleur graphe, donc un meilleur rappel au même ef, mais plus de mémoire et une construction plus lente.
- **La forme des données compte.** Des vecteurs groupés par thèmes, comme ceux du programme (24 thèmes), se prêtent bien à l'IVF. Des vecteurs uniformes en grande dimension rendent toutes les méthodes approchées plus difficiles, parce que les distances au plus proche et au plus loin y deviennent voisines.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| N, d, k | `N`, `D`, `K` |
| ‖a − b‖² | `dist2(a, b)` |
| Vₖ(q) | `recherche_exacte(base, q, k)`, ou `vrais` |
| Recall@k contre l'exact | `rappel(trouves, vrais)` |
| J(c, μ) | `objectif(points, centres, affect)` |
| c(i) | `plus_proche(p, centres)` |
| Lloyd | `kmeans(points, centres_init, iterations)` |
| μⱼ, Sⱼ | `ivf.centres[j]`, `ivf.listes[j]` |
| S(q) | `ivf.candidats(q, nprobe)` |
| x⁽ʲ⁾ | `pq.morceau(x, j)` |
| cⱼ,ₛ | `pq.dicos[j][s]` |
| uⱼ(x), x̂ | `pq.encoder(x)[j]`, `pq.decoder(code)` |
| Tⱼ[s], d̃(q, x) | `pq.table(q)[j][s]`, `CodeurPQ.adc(table, code)` |
| M, M₀, m_L | `g.M`, `g.M0`, `g.mL` |
| L | `niv` dans `ajouter`, conservé dans `g.niveaux` |
| ef, ef_construction | `ef`, `g.efc` |

### Déroulé, ligne par ligne

**`dist2(a, b)`** renvoie `math.dist(a, b) ** 2`. `math.dist` calcule √Σ(aᵢ − bᵢ)² en C, plusieurs fois plus vite qu'une boucle en Python pur ; on remet au carré pour avoir exactement la quantité des formules. Sur des vecteurs normés, elle vaut 2 − 2 cos, donc elle classe comme le cosinus (étape 14).

**`normer(v)`** divise par la norme et lève `ValueError` sur un vecteur nul, convention du parcours.

**`donnees(n, d, n_themes, ecart, rng)`** tire 24 directions de thème, puis chaque vecteur comme un thème plus un bruit gaussien d'écart `0.35`, renormé. On imite ainsi des embeddings de documents groupés par sujet. Tout passe par un `random.Random` à graine fixe : la base et les requêtes sont les mêmes à chaque exécution.

**`recherche_exacte(base, q, k)`** calcule les N distances et garde les k plus petites avec `heapq.nsmallest`, sur des couples `(distance, identifiant)` : à distance égale, le plus petit identifiant gagne, ce qui rend le lemme du point 3 exact. **`rappel(trouves, vrais)`** compte les vrais voisins retrouvés et divise par k.

**`objectif`** fait la somme de `dist2(p, centres[a])`. **`plus_proche(p, centres)`** calcule les distances (sans le carré, qui ne change pas l'ordre) et renvoie l'indice du premier minimum, grâce à `list.index`.

**`kmeans(points, centres_init, iterations)`**.

- `nouvelle = [plus_proche(p, centres) for p in points]` est l'affectation. Sur l'exemple à la main, avec les centres 1 et 2, elle vaut `[0, 1, 1, 1, 1, 1]`, et `objectif` donne 246.
- La boucle `for p, a in zip(points, nouvelle)` additionne les vecteurs de chaque liste en une seule passe ; `centres[c] = [x / n for x in sommes[c]]` est la moyenne, et le second centre devient 7,6, d'où J = 89,2.
- `if nouvelle == affect: break` arrête dès que l'affectation ne bouge plus : à la troisième affectation sur l'exemple, après les centres 2 et 11. La fonction renvoie aussi `historique`, la valeur de J après chaque demi-étape, que `main` vérifie décroissante.

**`IndexIVF`**.

- Le constructeur choisit C vecteurs de la base comme centres initiaux (`rng.sample`), lance `kmeans` puis range chaque identifiant dans la liste de son centre.
- `candidats(q, nprobe)` refuse un nprobe hors de [1 ; C], trie les centres par distance à q et concatène les nprobe listes les plus proches.
- `chercher(q, k, nprobe)` fait une recherche exacte limitée aux candidats et renvoie aussi le nombre de distances calculées, C plus le nombre de candidats. Pour nprobe = 1, la moyenne est de 45,7.

**`CodeurPQ`**.

- Le constructeur vérifie que d est divisible par m et que K* tient dans un octet. Il apprend ensuite un dictionnaire par sous-espace avec `kmeans`, sur les 250 premiers vecteurs seulement : comme les bibliothèques, on apprend sur un échantillon et on encode toute la base.
- `encoder(x)` renvoie un objet `bytes` de m octets, le code du centre le plus proche dans chaque sous-espace : pour m = 4, 4 octets au lieu de 32 en float32. `decoder(code)` recolle les centres désignés.
- `table(q)` calcule les m × K* distances de la question aux centres. `adc(table, code)` additionne m cases de cette table : c'est toute la distance d'un vecteur de la base.
- `candidats(q, r)` renvoie les r vecteurs de plus petite distance ADC. `chercher` les renvoie tels quels, ou, si `reclasser` vaut R, les reclasse par distance exacte et garde les k premiers.

**`HNSW`**.

- Le constructeur fixe `M0 = 2 * M` et `mL = 1 / ln M`, soit 0,4809 pour M = 8.
- `_couche(q, entrees, ef, niveau)` est la recherche en faisceau. `candidats` est un tas « min » des nœuds à explorer ; `meilleurs` est un tas « max », obtenu en stockant `-d`, des ef meilleurs nœuds trouvés, dont le pire est en tête. La boucle sort quand le plus proche des candidats est plus loin que le pire des retenus : `if d > -meilleurs[0][0]: break`. Un voisin n'entre dans les tas que s'il améliore les retenus, ou s'il en manque encore. `visites` empêche de calculer deux fois la même distance, et `self.calculs` compte les distances.
- `ajouter(v)` tire `niv` par `int(-math.log(1.0 - self.rng.random()) * self.mL)`. `random()` renvoie un nombre de [0 ; 1[, donc `1.0 - random()` est dans ]0 ; 1] et le logarithme est toujours défini. La méthode descend ensuite de façon gloutonne (ef = 1) depuis le point d'entrée jusqu'au niveau `niv`. Sur chaque couche de `niv` à 0, elle cherche les ef_construction plus proches, se relie aux M premiers et ajoute le lien inverse. Si un voisin dépasse son plafond, sa liste est triée par distance et tronquée : c'est la sélection simple, sans l'heuristique de diversité du HNSW complet. Un nouveau nœud plus haut que tous les autres devient le point d'entrée.
- `chercher(q, k, ef)` descend de façon gloutonne jusqu'à la couche 1, puis lance le faisceau de largeur max(ef, k) sur la couche 0.

**`main()`**, bloc par bloc.

1. L'exemple à la main du k-means : la suite 246, 89,2, 41,68, 4, 4, 4, l'affectation finale et les centres 2 et 11 sont vérifiés.
2. La base : 500 vecteurs normés de dimension 8, 20 requêtes tirées avec une autre graine, et les vrais 10 plus proches voisins de chacune par recherche exacte.
3. L'IVF à 16 listes : `assert` vérifie que J ne monte jamais. Pour chaque nprobe et chaque requête, un `assert` vérifie le point 3 : le rappel est exactement la part des vrais voisins parmi les candidats. La courbe doit être croissante et finir à 1.
4. La PQ : sur 4 requêtes × 500 vecteurs, soit 2 000 couples, l'écart entre l'ADC et la distance à la reconstruction reste sous 10⁻¹², et la borne triangulaire tient. Le rappel de l'ADC seule et celui du reclassement des 40 premiers sont vérifiés, ainsi que l'égalité du point 3 pour le reclassement.
5. L'ADC à la main : les dictionnaires sont écrits directement (`CodeurPQ.__new__` crée l'objet sans lancer l'apprentissage). On vérifie le code `[1, 1]`, la distance 1,64 et la vraie distance 1,86.
6. Le HNSW : on compte les nœuds de niveau ≥ 1, 2 et 3 et l'on mesure le rappel et le nombre de distances pour chaque ef. Le nombre de distances doit croître et rester sous N. On compare enfin la recherche gloutonne et le faisceau pour le plus proche voisin.
7. Les ordres de grandeur des points 2 et 4 pour 10⁶ vecteurs de dimension 768, puis le refus d'un nprobe de 0 ou de 17.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`normer(v)`** — Cette fonction joue le tailleur qui ramène chaque flèche à la longueur 1 sans changer sa direction, pour que la distance au carré classe exactement comme le cosinus : elle reçoit un vecteur, calcule sa norme, lève `ValueError` si elle est nulle, selon la convention du parcours, et renvoie la liste des coordonnées divisées par cette norme. Elle sert à fabriquer les directions de thème et chaque vecteur de la base et des requêtes dans `donnees`, si bien que les 500 vecteurs de dimension 8 sont tous de longueur 1.

**`rappel(trouves, vrais)`** — C'est l'inspecteur qui compare la réponse d'un index approché à celle de la recherche exacte, considérée comme la vérité : la fonction reçoit la liste des identifiants renvoyés par l'index et la liste des k vrais plus proches voisins, compte ceux qui figurent dans les deux et divise par le nombre de vrais voisins. Elle renvoie ce Recall@k, un nombre entre 0 et 1 ; c'est la note de toutes les courbes du programme, par exemple 0,51 pour l'IVF qui ne sonde qu'une liste et 1 pour celui qui les sonde toutes.

**`objectif(points, centres, affect)`** — Cette fonction mesure le désordre d'un rangement, comme un intendant qui additionnerait la distance que chaque objet doit parcourir pour rejoindre son étagère : elle reçoit les points, les centres et l'affectation de chaque point à un centre, et renvoie la somme des distances au carré de chaque point à son centre, la quantité J que le k-means fait décroître. Sur l'exemple à la main, elle vaut 246 avec les centres de départ 1 et 2, puis 89,2 après la première mise à jour, et 4 une fois les centres installés en 2 et 11.

**`plus_proche(p, centres)`** — C'est l'aiguilleur qui envoie un point vers la gare la plus proche : la fonction reçoit un point et la liste des centres, calcule la distance du point à chaque centre, sans le carré puisque la racine ne change pas l'ordre, et renvoie l'indice du centre le plus proche, le plus petit indice en cas d'égalité grâce à `list.index`, qui rend la première occurrence du minimum. Elle sert à l'étape d'affectation du k-means, et le codeur PQ s'en sert aussi pour choisir, dans chaque sous-espace, le centre qui donnera l'octet du code.

**`kmeans(points, centres_init, iterations)`** — Cette fonction est l'algorithme de Lloyd, un va-et-vient patient entre deux gestes : ranger chaque point près du centre le plus proche, puis déplacer chaque centre au milieu de ses membres. Elle reçoit les points, les centres de départ et un nombre maximal d'itérations, alterne l'affectation par `plus_proche` et la mise à jour par moyenne en une seule passe sur les points, laisse en place un centre resté vide, note J après chaque demi-étape et s'arrête dès que l'affectation ne bouge plus. Elle renvoie les centres, l'affectation et l'historique de J ; sur l'exemple à la main, cet historique vaut 246, 89,2, 41,68, 4, 4 et 4, et les centres finissent en 2 et 11.

**`IndexIVF.__init__(base, n_listes, rng, iterations)`** — Le constructeur organise la bibliothèque en rayons thématiques : il reçoit la base de vecteurs, le nombre C de listes, un générateur aléatoire à graine fixe et un nombre d'itérations, 20 par défaut, tire C vecteurs de la base comme centres de départ, lance `kmeans` pour apprendre les centres et garder l'historique de J, puis range chaque identifiant dans la liste de son centre. Il ne renvoie rien ; avec 16 listes, `main` vérifie que J n'a jamais augmenté pendant l'apprentissage.

**`IndexIVF.candidats(q, nprobe)`** — Cette méthode est le bibliothécaire qui, au lieu de parcourir toute la bibliothèque, ne visite que les rayons les plus proches du sujet demandé : elle reçoit la requête et le nombre nprobe de listes à sonder, lève `ValueError` si nprobe n'est pas compris entre 1 et C, trouve les nprobe centres les plus proches de la requête et renvoie la concaténation de leurs listes d'identifiants. `main` vérifie avec elle la propriété du point 3 : le rappel de l'IVF est exactement la part des vrais voisins présents parmi ces candidats, et un nprobe de 0 ou de 17 est bien refusé.

**`IndexIVF.chercher(q, k, nprobe)`** — Elle termine le travail du bibliothécaire en mesurant précisément les seuls livres des rayons visités : la méthode reçoit la requête, k et nprobe, obtient les candidats par `candidats`, calcule la distance exacte de la requête à chacun et garde les k plus proches. Elle renvoie un couple formé de la liste des identifiants et du nombre de distances calculées, C plus le nombre de candidats ; pour nprobe = 1, 2, 4, 8 et 16, le Recall@10 vaut 0,51, 0,695, 0,9, 0,985 et 1, et le coût grandit avec lui.

**`CodeurPQ.__init__(base, m, k_etoile, rng, iterations, n_apprentissage)`** — Le constructeur prépare un sténographe qui résumera chaque vecteur en quelques octets : il reçoit la base, le nombre m de sous-vecteurs, le nombre K* de centres par sous-espace, un générateur aléatoire, un nombre d'itérations et une taille d'échantillon, 250 par défaut, lève `ValueError` si la dimension n'est pas divisible par m ou si K* sort de [2, 256], puis apprend avec `kmeans` un dictionnaire de K* centres par sous-espace sur les 250 premiers vecteurs seulement, et encode enfin toute la base. Il ne renvoie rien ; avec m = 4 et K* = 16, chaque vecteur passe de 32 octets en float32 à 4 octets de code.

**`CodeurPQ.morceau(v, j)`** — Cette petite méthode est le découpeur qui tranche un vecteur en parts égales, comme on partage une baguette en m tronçons de même longueur : elle reçoit un vecteur et un numéro de sous-espace j, et renvoie la tranche des coordonnées de j × ds à (j + 1) × ds exclus, ds étant la dimension d'un sous-vecteur. Toutes les autres méthodes du codeur passent par elle pour travailler sous-espace par sous-espace : l'apprentissage, l'encodage et la table des distances.

**`CodeurPQ.encoder(v)`** — C'est le sténographe au travail : la méthode reçoit un vecteur, le découpe en m sous-vecteurs avec `morceau`, cherche pour chacun le centre le plus proche dans le dictionnaire de son sous-espace avec `plus_proche`, et renvoie un objet `bytes` dont chaque octet est l'indice de ce centre. Le vecteur de la base n'est plus conservé que sous cette forme, 4 octets pour m = 4 ; sur l'exemple à la main en dimension 4 avec m = 2, le vecteur [0,9 ; 1,2 ; 1,8 ; 0,1] reçoit le code [1, 1].

**`CodeurPQ.decoder(code)`** — Elle fait le chemin inverse, comme un restaurateur qui reconstitue un tableau à partir de pièces de catalogue : la méthode reçoit un code de m octets, va chercher pour chaque octet le centre correspondant dans le dictionnaire de son sous-espace, et renvoie la concaténation de ces centres, la reconstruction x̂ du vecteur. Le programme s'en sert pour vérifier que la distance ADC est exactement la distance à cette reconstruction, à moins de 10⁻¹² près sur 2 000 couples, et pour contrôler la borne triangulaire qui encadre l'erreur commise.

**`CodeurPQ.table(q)`** — Cette méthode prépare, une seule fois par requête, la grille de tarifs que l'on consultera ensuite pour chaque vecteur de la base : elle reçoit la requête, la découpe en m sous-vecteurs et renvoie une table qui donne, pour chaque sous-espace j et chaque centre c, la distance au carré entre le sous-vecteur de la requête et ce centre, soit m × K* nombres. Grâce à elle, mesurer la distance à un vecteur de la base ne demandera plus aucune multiplication, seulement des lectures de cette table.

**`CodeurPQ.adc(table, code)`** — C'est le caissier qui additionne des prix lus sur une grille plutôt que de recalculer chaque article : cette méthode statique reçoit la table de la requête et le code d'un vecteur, lit pour chaque sous-espace la case désignée par l'octet du code, et renvoie la somme de ces m cases, la distance asymétrique entre la requête et la reconstruction du vecteur. Sur l'exemple à la main, elle donne 1,64, alors que la vraie distance au carré entre la requête et le vecteur d'origine vaut 1,86.

**`CodeurPQ.candidats(q, r)`** — Elle passe toute la base au crible de la distance approchée, comme un recruteur qui trie les candidatures sur leur résumé avant d'en lire certaines en entier : la méthode reçoit la requête et un nombre r, construit la table de la requête, calcule la distance ADC de chaque code de la base et renvoie les identifiants des r vecteurs les plus proches selon cette distance. `main` vérifie avec elle que le rappel après reclassement est exactement la part des vrais voisins présents parmi ces r candidats.

**`CodeurPQ.chercher(q, k, base, reclasser)`** — Cette méthode offre deux modes de recherche : si `reclasser` vaut 0, elle se contente des k meilleurs candidats selon la distance ADC ; sinon, elle prend les max(k, reclasser) meilleurs candidats ADC, recalcule pour eux seuls la distance exacte à partir des vecteurs complets de `base`, et garde les k plus proches. Elle renvoie la liste des identifiants ; sur les 20 requêtes, l'ADC seule obtient un Recall@10 de 0,685, et le reclassement exact des 40 premiers candidats le fait monter à 0,99.

**`HNSW.__init__(M, ef_construction, rng)`** — Le constructeur prépare un réseau de routes à plusieurs étages, autoroutes en haut et rues de quartier en bas : il reçoit le nombre M de liens par nœud, la largeur ef_construction du faisceau d'insertion et un générateur aléatoire, lève `ValueError` si M est inférieur à 2, fixe M₀ = 2M liens sur la couche 0 et le facteur de niveau mL = 1 / ln M, soit environ 0,4809 pour M = 8, puis crée des listes vides pour les vecteurs, les voisins et les niveaux, sans point d'entrée et avec un compteur de distances à zéro. Il ne renvoie rien.

**`HNSW._d(q, i)`** — Cette petite méthode est le compteur kilométrique du graphe : elle reçoit une requête et l'identifiant d'un nœud, ajoute 1 au compteur `calculs`, puis renvoie la distance au carré entre la requête et le vecteur de ce nœud. Toutes les distances de la recherche en faisceau passent par elle, ce qui permet à `main` de mesurer combien de distances chaque largeur ef coûte réellement par requête, et de vérifier que ce coût croît avec ef tout en restant sous les 500 de la recherche exacte.

**`HNSW._couche(q, entrees, ef, niveau)`** — C'est l'explorateur qui parcourt un étage du réseau en gardant toujours sous la main les ef meilleures adresses trouvées : la méthode reçoit la requête, les nœuds de départ, la largeur ef du faisceau et le numéro de la couche, entretient un tas des candidats à explorer, du plus proche au plus loin, et un tas des meilleurs retenus, dont le pire est en tête, puis explore les voisins de chaque candidat en ne gardant que ceux qui améliorent les retenus, sans jamais calculer deux fois la même distance. Elle s'arrête quand le plus proche des candidats est plus loin que le pire des retenus, et renvoie les ef meilleurs couples (distance, identifiant), triés du plus proche au plus loin.

**`HNSW.ajouter(v)`** — Cette méthode est l'urbaniste qui construit une nouvelle maison et la raccorde au réseau existant : elle reçoit un vecteur, lui attribue un identifiant, tire son niveau par −ln(1 − u) × mL, ce qui rend chaque étage M fois plus rare que le précédent, et en fait le point d'entrée si le graphe est vide. Sinon, elle descend de façon gloutonne depuis le sommet jusqu'à l'étage du nouveau nœud, puis, de cet étage jusqu'à la couche 0, cherche les ef_construction plus proches voisins, se relie aux M premiers, ajoute les liens inverses et élague les listes devenues trop longues ; un nœud plus haut que tous les autres devient le nouveau point d'entrée. Sur 500 vecteurs avec M = 8, on obtient 56 nœuds de niveau au moins 1, 6 de niveau au moins 2 et 1 de niveau 3.

**`HNSW.chercher(q, k, ef)`** — C'est le voyageur qui prend d'abord l'autoroute, puis les rues de quartier : la méthode reçoit la requête, k et la largeur ef, descend de façon gloutonne depuis le point d'entrée jusqu'à la couche 1, en ne gardant à chaque étage que le nœud le plus proche, puis lance sur la couche 0 un faisceau de largeur max(ef, k) et renvoie les k identifiants les plus proches. Avec ef = 10, 20, 40 et 80, le Recall@10 vaut 0,95, 0,995, 1 et 1 ; pour le seul plus proche voisin, la recherche gloutonne le trouve 15 fois sur 20, et le faisceau de largeur 10, 19 fois.

**`main()`** — Le chef d'orchestre déroule sept démonstrations : il vérifie d'abord le k-means à la main en une dimension, puis construit une base de 500 vecteurs normés de dimension 8 et 20 requêtes, avec leurs 10 vrais voisins par recherche exacte. Il mesure ensuite l'IVF à 16 listes, sa courbe de rappel de 0,51 à 1 et la propriété des candidats, puis la PQ, avec l'égalité entre ADC et distance à la reconstruction, la borne triangulaire, et les rappels 0,685 et 0,99, refait l'ADC à la main avec un codeur dont les dictionnaires sont écrits directement, évalue le HNSW, ses niveaux et sa courbe de rappel, compare recherche gloutonne et faisceau, puis calcule les ordres de grandeur pour un million de vecteurs, un IVF 113 fois moins coûteux que la recherche exacte, et vérifie le refus d'un nprobe de 0 ou de 17. La dernière ligne n'annonce le succès que si chaque `assert` a tenu.

```python
"""Étape 30 quinquies — Index ANN : recherche exacte, IVF (k-means de Lloyd), PQ (distances ADC), HNSW simplifié."""
import heapq
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- distances et données
def dist2(a: list[float], b: list[float]) -> float:
    """Distance euclidienne au carré ; sur des vecteurs normés, elle vaut 2 − 2 cos (étape 14)."""
    return math.dist(a, b) ** 2                      # math.dist : √Σ(aᵢ − bᵢ)², calculée en C


def normer(v: list[float]) -> list[float]:
    n = math.sqrt(sum(x * x for x in v))
    if n == 0.0:
        raise ValueError("vecteur nul : impossible à normer")
    return [x / n for x in v]


def donnees(n: int, d: int, n_themes: int, ecart: float, rng: random.Random) -> list[list[float]]:
    """Vecteurs normés groupés autour de n_themes directions, comme des embeddings de documents par thème."""
    themes = [normer([rng.gauss(0.0, 1.0) for _ in range(d)]) for _ in range(n_themes)]
    return [normer([x + rng.gauss(0.0, ecart) for x in themes[rng.randrange(n_themes)]]) for _ in range(n)]


def recherche_exacte(base: list[list[float]], q: list[float], k: int) -> list[int]:
    """Index plat : N distances de d coordonnées, puis les k plus petites (égalités : plus petit identifiant)."""
    return [i for _, i in heapq.nsmallest(k, ((dist2(q, v), i) for i, v in enumerate(base)))]


def rappel(trouves: list[int], vrais: list[int]) -> float:
    """Recall@k contre la recherche exacte : part des k vrais voisins que l'index renvoie (étape 25)."""
    return len(set(trouves) & set(vrais)) / len(vrais)


# ---------------------------------------------------------------- k-means de Lloyd
def objectif(points: list[list[float]], centres: list[list[float]], affect: list[int]) -> float:
    """J = Σ ‖xᵢ − μ_c(i)‖² : la somme des distances au carré de chaque point à son centre."""
    return sum(dist2(p, centres[a]) for p, a in zip(points, affect))


def plus_proche(p: list[float], centres: list[list[float]]) -> int:
    """Indice du centre le plus proche ; à égalité, le plus petit indice (index renvoie la première occurrence)."""
    d = [math.dist(p, c) for c in centres]           # la racine ne change pas l'ordre : même gagnant qu'avec ‖·‖²
    return d.index(min(d))


def kmeans(points: list[list[float]], centres_init: list[list[float]], iterations: int):
    """Alterne affectation (centre le plus proche) et mise à jour (moyenne des membres). Renvoie J après chaque demi-étape."""
    centres = [list(c) for c in centres_init]
    d = len(centres[0])
    affect: list[int] | None = None
    historique: list[float] = []
    for _ in range(iterations):
        nouvelle = [plus_proche(p, centres) for p in points]
        historique.append(objectif(points, centres, nouvelle))
        sommes = [[0.0] * d for _ in centres]
        effectifs = [0] * len(centres)
        for p, a in zip(points, nouvelle):                # une seule passe : somme et effectif par centre
            effectifs[a] += 1
            s = sommes[a]
            for t in range(d):
                s[t] += p[t]
        for c, n in enumerate(effectifs):
            if n:                                         # un centre vide garde sa position
                centres[c] = [x / n for x in sommes[c]]
        historique.append(objectif(points, centres, nouvelle))
        if nouvelle == affect:
            break
        affect = nouvelle
    return centres, affect, historique


# ---------------------------------------------------------------- IVF
class IndexIVF:
    """Fichier inversé : C centres appris par k-means, une liste d'identifiants par centre."""

    def __init__(self, base: list[list[float]], n_listes: int, rng: random.Random, iterations: int = 20):
        self.base = base
        init = [base[i] for i in rng.sample(range(len(base)), n_listes)]
        self.centres, affect, self.historique = kmeans(base, init, iterations)
        self.listes: list[list[int]] = [[] for _ in range(n_listes)]
        for i, a in enumerate(affect):
            self.listes[a].append(i)

    def candidats(self, q: list[float], nprobe: int) -> list[int]:
        """Les identifiants rangés dans les nprobe listes dont le centre est le plus proche de q."""
        if not 1 <= nprobe <= len(self.centres):
            raise ValueError("il faut 1 <= nprobe <= C")
        proches = heapq.nsmallest(nprobe, ((dist2(q, c), j) for j, c in enumerate(self.centres)))
        return [i for _, j in proches for i in self.listes[j]]

    def chercher(self, q: list[float], k: int, nprobe: int) -> tuple[list[int], int]:
        cand = self.candidats(q, nprobe)
        meilleurs = heapq.nsmallest(k, ((dist2(q, self.base[i]), i) for i in cand))
        return [i for _, i in meilleurs], len(self.centres) + len(cand)


# ---------------------------------------------------------------- PQ
class CodeurPQ:
    """Quantification par produit : m sous-vecteurs, un dictionnaire de K* centres par sous-espace, un octet par sous-vecteur."""

    def __init__(self, base: list[list[float]], m: int, k_etoile: int, rng: random.Random,
                 iterations: int = 10, n_apprentissage: int = 250):
        d = len(base[0])
        if d % m != 0 or not 2 <= k_etoile <= 256:
            raise ValueError("il faut d divisible par m et 2 <= K* <= 256 (un octet par code)")
        self.m, self.ds = m, d // m
        self.dicos: list[list[list[float]]] = []
        for j in range(m):
            sous = [self.morceau(v, j) for v in base[:n_apprentissage]]   # dictionnaires appris sur un échantillon
            init = [sous[i] for i in rng.sample(range(len(sous)), k_etoile)]
            self.dicos.append(kmeans(sous, init, iterations)[0])
        self.codes = [self.encoder(v) for v in base]

    def morceau(self, v: list[float], j: int) -> list[float]:
        return v[j * self.ds:(j + 1) * self.ds]

    def encoder(self, v: list[float]) -> bytes:
        return bytes(plus_proche(self.morceau(v, j), dico) for j, dico in enumerate(self.dicos))

    def decoder(self, code: bytes) -> list[float]:
        return [x for j, c in enumerate(code) for x in self.dicos[j][c]]

    def table(self, q: list[float]) -> list[list[float]]:
        """T[j][c] = ‖qⱼ − cⱼ,c‖² : K* × d opérations, une seule fois par requête."""
        return [[dist2(self.morceau(q, j), c) for c in dico] for j, dico in enumerate(self.dicos)]

    @staticmethod
    def adc(table: list[list[float]], code: bytes) -> float:
        """Distance asymétrique : m lectures de table et m − 1 additions par vecteur de la base."""
        return sum(table[j][c] for j, c in enumerate(code))

    def candidats(self, q: list[float], r: int) -> list[int]:
        """Les r vecteurs de plus petite distance ADC."""
        t = self.table(q)
        return [i for _, i in heapq.nsmallest(r, ((self.adc(t, c), i) for i, c in enumerate(self.codes)))]

    def chercher(self, q: list[float], k: int, base: list[list[float]] | None = None, reclasser: int = 0) -> list[int]:
        if not reclasser:
            return self.candidats(q, k)
        cand = self.candidats(q, max(k, reclasser))      # puis distances exactes sur ces seuls candidats
        return [i for _, i in heapq.nsmallest(k, ((dist2(q, base[i]), i) for i in cand))]


# ---------------------------------------------------------------- HNSW simplifié
class HNSW:
    """Graphe en couches ; sélection simple des M plus proches voisins (sans l'heuristique de diversité)."""

    def __init__(self, M: int, ef_construction: int, rng: random.Random):
        if M < 2:
            raise ValueError("il faut M >= 2")
        self.M, self.M0, self.efc = M, 2 * M, ef_construction
        self.mL = 1.0 / math.log(M)
        self.rng = rng
        self.vecteurs: list[list[float]] = []
        self.voisins: list[list[list[int]]] = []      # voisins[i][niveau] : liste d'identifiants
        self.niveaux: list[int] = []
        self.entree: int | None = None
        self.niveau_max = -1
        self.calculs = 0

    def _d(self, q: list[float], i: int) -> float:
        self.calculs += 1
        return dist2(q, self.vecteurs[i])

    def _couche(self, q: list[float], entrees: list[int], ef: int, niveau: int) -> list[tuple[float, int]]:
        """Recherche en faisceau de largeur ef sur une couche ; renvoie les ef meilleurs trouvés, du plus proche au plus loin."""
        visites = set(entrees)
        candidats = [(self._d(q, e), e) for e in entrees]
        heapq.heapify(candidats)
        meilleurs = [(-d, e) for d, e in candidats]       # tas « max » : le plus loin des retenus en tête
        heapq.heapify(meilleurs)
        while len(meilleurs) > ef:
            heapq.heappop(meilleurs)
        while candidats:
            d, c = heapq.heappop(candidats)
            if d > -meilleurs[0][0]:
                break                                     # le plus proche des candidats est plus loin que le pire retenu
            for v in self.voisins[c][niveau]:
                if v in visites:
                    continue
                visites.add(v)
                dv = self._d(q, v)
                if len(meilleurs) < ef or dv < -meilleurs[0][0]:
                    heapq.heappush(candidats, (dv, v))
                    heapq.heappush(meilleurs, (-dv, v))
                    if len(meilleurs) > ef:
                        heapq.heappop(meilleurs)
        return sorted((-d, e) for d, e in meilleurs)

    def ajouter(self, v: list[float]) -> None:
        i = len(self.vecteurs)
        self.vecteurs.append(v)
        niv = int(-math.log(1.0 - self.rng.random()) * self.mL)   # P(niveau >= l) = M^(-l)
        self.niveaux.append(niv)
        self.voisins.append([[] for _ in range(niv + 1)])
        if self.entree is None:
            self.entree, self.niveau_max = i, niv
            return
        ep = [self.entree]
        for l in range(self.niveau_max, niv, -1):                  # descente gloutonne (ef = 1) au-dessus de niv
            ep = [self._couche(v, ep, 1, l)[0][1]]
        for l in range(min(niv, self.niveau_max), -1, -1):
            trouves = self._couche(v, ep, self.efc, l)
            m_max = self.M0 if l == 0 else self.M
            self.voisins[i][l] = [e for _, e in trouves[:self.M]]
            for e in self.voisins[i][l]:                           # liens dans les deux sens, puis élagage
                liste = self.voisins[e][l]
                liste.append(i)
                if len(liste) > m_max:
                    liste.sort(key=lambda x: (dist2(self.vecteurs[e], self.vecteurs[x]), x))
                    del liste[m_max:]
            ep = [e for _, e in trouves]
        if niv > self.niveau_max:
            self.entree, self.niveau_max = i, niv

    def chercher(self, q: list[float], k: int, ef: int) -> list[int]:
        ep = [self.entree]
        for l in range(self.niveau_max, 0, -1):
            ep = [self._couche(q, ep, 1, l)[0][1]]
        return [e for _, e in self._couche(q, ep, max(ef, k), 0)[:k]]


def main() -> None:
    print("1. k-means à la main, en une dimension")
    pts = [[1.0], [2.0], [3.0], [10.0], [11.0], [12.0]]
    centres, affect, hist = kmeans(pts, [[1.0], [2.0]], 10)
    print("  J après chaque demi-étape : " + " → ".join(f"{j:.2f}" for j in hist)
          + f" ; centres {centres[0][0]:.1f} et {centres[1][0]:.1f}")
    assert [round(j, 2) for j in hist] == [246.0, 89.2, 41.68, 4.0, 4.0, 4.0]
    assert affect == [0, 0, 0, 1, 1, 1] and centres == [[2.0], [11.0]]

    N, D, Q, K = 500, 8, 20, 10
    base = donnees(N, D, 24, 0.35, random.Random(30))
    requetes = donnees(Q, D, 24, 0.35, random.Random(5))
    vrais = [recherche_exacte(base, q, K) for q in requetes]
    print(f"2. Base : N = {N} vecteurs normés, d = {D} ; {Q} requêtes, k = {K} ; index exact : {N} distances par requête")

    print("3. IVF avec C = 16 listes")
    ivf = IndexIVF(base, 16, random.Random(7))
    h = ivf.historique
    assert all(b <= a + 1e-9 for a, b in zip(h, h[1:]))            # J ne fait que décroître (point 1)
    tailles = sorted(len(l) for l in ivf.listes)
    print(f"  k-means : J = {h[0]:.2f} → {h[-1]:.2f}, stable après {len(h) // 2} itérations ;"
          f" listes de {tailles[0]} à {tailles[-1]} vecteurs")
    courbe = []
    for nprobe in (1, 2, 4, 8, 16):
        r, cout = 0.0, 0
        for q, v in zip(requetes, vrais):
            trouves, c = ivf.chercher(q, K, nprobe)
            assert rappel(trouves, v) == len(set(v) & set(ivf.candidats(q, nprobe))) / K   # point 3
            r += rappel(trouves, v)
            cout += c
        courbe.append(r / Q)
        print(f"  nprobe = {nprobe:>2} : Recall@10 = {r / Q:.3f}   distances par requête = {cout / Q:.1f}")
    assert all(b >= a for a, b in zip(courbe, courbe[1:])) and courbe[-1] == 1.0
    assert [round(r, 3) for r in courbe] == [0.51, 0.695, 0.9, 0.985, 1.0]

    print("4. PQ avec m = 4 sous-vecteurs et K* = 16 centres par sous-espace")
    pq = CodeurPQ(base, 4, 16, random.Random(11))
    print(f"  mémoire par vecteur : {D * 4} octets en float32 → {len(pq.codes[0])} octets de code (×{D * 4 // len(pq.codes[0])})")
    ecart_max, couples = 0.0, 0
    for q in requetes[:4]:
        t = pq.table(q)
        for x, code in zip(base, pq.codes):
            xh = pq.decoder(code)
            ecart_max = max(ecart_max, abs(pq.adc(t, code) - dist2(q, xh)))
            assert abs(math.sqrt(dist2(q, x)) - math.sqrt(dist2(q, xh))) <= math.sqrt(dist2(x, xh)) + 1e-12
            couples += 1
    print(f"  ADC = distance exacte à la reconstruction (écart max {ecart_max:.1e}) ; borne triangulaire vérifiée sur {couples} couples")
    assert ecart_max < 1e-12
    r_pq = sum(rappel(pq.chercher(q, K), v) for q, v in zip(requetes, vrais)) / Q
    r_re = 0.0
    for q, v in zip(requetes, vrais):
        r_q = rappel(pq.chercher(q, K, base, 40), v)
        assert r_q == len(set(v) & set(pq.candidats(q, 40))) / K
        r_re += r_q / Q
    print(f"  Recall@10 : ADC seule = {r_pq:.3f} ; ADC puis reclassement exact des 40 premiers = {r_re:.3f}")
    assert r_re >= r_pq and (round(r_pq, 3), round(r_re, 3)) == (0.685, 0.99)

    print("5. ADC à la main (d = 4, m = 2)")
    main_pq = CodeurPQ.__new__(CodeurPQ)                            # dictionnaires écrits à la main, sans apprentissage
    main_pq.m, main_pq.ds = 2, 2
    main_pq.dicos = [[[0.0, 0.0], [1.0, 1.0]], [[0.0, 0.0], [2.0, 0.0]]]
    x, q = [0.9, 1.2, 1.8, 0.1], [1.0, 0.2, 2.0, 1.0]
    code = main_pq.encoder(x)
    t = main_pq.table(q)
    xh = main_pq.decoder(code)
    print(f"  code = {list(code)} ; x̂ = {xh} ; table = {[[round(v, 2) for v in ligne] for ligne in t]}")
    print(f"  ADC = {main_pq.adc(t, code):.2f} = ‖q − x̂‖² ; vraie ‖q − x‖² = {dist2(q, x):.2f} ; ‖x − x̂‖ = {math.sqrt(dist2(x, xh)):.4f}")
    assert list(code) == [1, 1] and abs(main_pq.adc(t, code) - 1.64) < 1e-12 and abs(dist2(q, x) - 1.86) < 1e-12

    print("6. HNSW simplifié, M = 8, ef_construction = 24")
    g = HNSW(8, 24, random.Random(3))
    for v in base:
        g.ajouter(v)
    au_moins = [sum(1 for n in g.niveaux if n >= l) for l in (1, 2, 3)]
    attendus = ", ".join(f"{N / 8 ** l:.1f}" for l in (1, 2, 3))
    print(f"  nœuds de niveau ≥ 1, 2, 3 : {au_moins} (attendu N/M^l = {attendus}) ; niveau max {g.niveau_max}")
    assert au_moins == [56, 6, 1] and g.niveau_max == 3
    courbe_h, couts = [], []
    for ef in (10, 20, 40, 80):
        g.calculs = 0
        r = sum(rappel(g.chercher(q, K, ef), v) for q, v in zip(requetes, vrais)) / Q
        courbe_h.append(r)
        couts.append(g.calculs / Q)
        print(f"  ef = {ef:>3} : Recall@10 = {r:.3f}   distances par requête = {g.calculs / Q:.1f}")
    assert all(b > a for a, b in zip(couts, couts[1:])) and couts[-1] < N
    assert [round(r, 3) for r in courbe_h] == [0.95, 0.995, 1.0, 1.0]
    top1 = [v[0] for v in vrais]
    glouton = sum(g.chercher(q, 1, 1) == [t1] for q, t1 in zip(requetes, top1))
    faisceau = sum(g.chercher(q, 1, 10) == [t1] for q, t1 in zip(requetes, top1))
    print(f"  plus proche voisin exact trouvé : recherche gloutonne (ef = 1) {glouton}/{Q} ; faisceau ef = 10 : {faisceau}/{Q}")
    assert (glouton, faisceau) == (15, 19)

    print("7. Ordres de grandeur pour N = 10^6 vecteurs de d = 768 (illustratif)")
    n6, d6 = 10 ** 6, 768
    exact = n6 * d6
    ivf6 = (1024 + 8 * n6 / 1024) * d6
    print(f"  exact {exact:.3e} multiplications ; IVF (C = 1024, nprobe = 8) {ivf6:.3e}, soit {exact / ivf6:.0f}× moins ;"
          f" C* = √(N·nprobe) = {math.sqrt(n6 * 8):.0f}")
    print(f"  mémoire : float32 {n6 * d6 * 4 / 1e9:.3f} Go ; PQ m = 96 : {n6 * 96 / 1e6:.0f} Mo + dictionnaires {256 * d6 * 4 / 1e3:.0f} ko")
    assert round(exact / ivf6) == 113 and round(math.sqrt(n6 * 8)) == 2828

    for mauvais in (0, 17):
        try:
            ivf.chercher(requetes[0], K, mauvais)
        except ValueError:
            pass
        else:
            raise AssertionError("un nprobe hors de [1 ; C] aurait dû être refusé")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. k-means à la main, en une dimension
  J après chaque demi-étape : 246.00 → 89.20 → 41.68 → 4.00 → 4.00 → 4.00 ; centres 2.0 et 11.0
…
  k-means : J = 389.40 → 224.57, stable après 18 itérations ; listes de 22 à 47 vecteurs
  nprobe =  1 : Recall@10 = 0.510   distances par requête = 45.7
  nprobe =  4 : Recall@10 = 0.900   distances par requête = 140.8
  nprobe = 16 : Recall@10 = 1.000   distances par requête = 516.0
…
  ADC = distance exacte à la reconstruction (écart max 8.9e-16) ; borne triangulaire vérifiée sur 2000 couples
  Recall@10 : ADC seule = 0.685 ; ADC puis reclassement exact des 40 premiers = 0.990
…
  ADC = 1.64 = ‖q − x̂‖² ; vraie ‖q − x‖² = 1.86 ; ‖x − x̂‖ = 0.3162
…
  nœuds de niveau ≥ 1, 2, 3 : [56, 6, 1] (attendu N/M^l = 62.5, 7.8, 1.0) ; niveau max 3
  ef =  10 : Recall@10 = 0.950   distances par requête = 92.8
  ef =  40 : Recall@10 = 1.000   distances par requête = 188.8
  plus proche voisin exact trouvé : recherche gloutonne (ef = 1) 15/20 ; faisceau ef = 10 : 19/20
…
  exact 7.680e+08 multiplications ; IVF (C = 1024, nprobe = 8) 6.786e+06, soit 113× moins ; C* = √(N·nprobe) = 2828
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un index approché n'est pas une boîte noire. L'IVF est un k-means suivi d'une recherche exacte sur quelques listes, la PQ une table de distances lue m fois, le HNSW une recherche en faisceau dans un graphe. Dans les trois cas, le rappel se mesure contre la recherche exacte, et il se règle par un seul paramètre : nprobe, le nombre de candidats reclassés ou ef.

## Squelette algorithmique

Trois algorithmes, chacun en deux phases : une construction faite une fois, hors ligne, puis une recherche faite à chaque requête. Les entrées sont une base de N vecteurs de dimension d et une question q ; la sortie est une liste de k identifiants, que l'on compare à la recherche exacte.

```text
ALGORITHME ConstruireIVF
ENTRÉES : base (N vecteurs), C listes, plafond d'itérations
SORTIE  : centres μ₁ … μC, listes S₁ … SC

  μ ← C vecteurs de la base tirés au hasard (graine fixe)
  RÉPÉTER
      POUR CHAQUE vecteur xᵢ FAIRE  c(i) ← indice du centre le plus proche  FIN POUR      (J ne monte pas)
      POUR j DE 1 À C FAIRE
          SI Sⱼ n'est pas vide ALORS μⱼ ← moyenne des xᵢ de Sⱼ                            (J ne monte pas)
      FIN POUR
  JUSQU'À affectation inchangée OU plafond atteint
  RETOURNER μ, S

ALGORITHME ChercherIVF
ENTRÉES : q, k, nprobe (1 ≤ nprobe ≤ C)
  listes ← les nprobe indices j de plus petit ‖q − μⱼ‖
  candidats ← réunion des Sⱼ de ces listes
  RETOURNER les k candidats de plus petit ‖q − x‖² (égalités : plus petit identifiant)
```

**Complexité.** La construction coûte O(I × N × C × d) pour I itérations, parce que chaque affectation compare les N vecteurs aux C centres ; la mémoire ajoute O(C × d) pour les centres et O(N) pour les identifiants. La recherche coûte O(C × d) pour classer les centres, puis O(nprobe × N/C × d) pour les candidats si les listes sont égales, et O(candidats × log k) pour le tas des k meilleurs.

**Du squelette au code.** La boucle RÉPÉTER est `kmeans`, avec `plus_proche` pour l'affectation et la passe `sommes`/`effectifs` pour la moyenne. `IndexIVF.__init__` tire les centres et remplit `listes`. `ChercherIVF` correspond à `candidats` (la garde sur nprobe comprise), puis à `chercher`.

```text
ALGORITHME ConstruirePQ
ENTRÉES : base, m (diviseur de d), K* ≤ 256, échantillon d'apprentissage
SORTIE  : m dictionnaires de K* centres, un code de m octets par vecteur

  POUR j DE 1 À m FAIRE
      dictionnaire j ← k-means à K* centres sur les sous-vecteurs j de l'échantillon
  FIN POUR
  POUR CHAQUE vecteur x FAIRE
      code(x) ← (indice du centre le plus proche de x⁽¹⁾, …, indice du centre le plus proche de x⁽ᵐ⁾)
  FIN POUR

ALGORITHME ChercherPQ
ENTRÉES : q, k, R (candidats à reclasser, 0 pour aucun)
  POUR j DE 1 À m FAIRE  POUR s DE 0 À K* − 1 FAIRE  T[j][s] ← ‖q⁽ʲ⁾ − cⱼ,ₛ‖²  FIN POUR  FIN POUR
  POUR CHAQUE vecteur x FAIRE  d̃(x) ← T[1][code₁(x)] + … + T[m][codeₘ(x)]  FIN POUR
  SI R = 0 ALORS RETOURNER les k vecteurs de plus petit d̃
  candidats ← les R vecteurs de plus petit d̃
  RETOURNER les k candidats de plus petite distance exacte
```

**Complexité.** L'apprentissage coûte O(m × I × n × K* × d/m) = O(I × n × K* × d) sur un échantillon de n vecteurs, et l'encodage O(N × K* × d). La mémoire vaut N × m octets pour les codes, plus 4 × K* × d octets pour les dictionnaires. La recherche coûte O(K* × d) pour la table, O(N × m) pour les distances ADC, puis O(R × d) pour le reclassement.

**Du squelette au code.** `ConstruirePQ` correspond au constructeur de `CodeurPQ` (avec `morceau` et `kmeans`) puis à `encoder`. `ChercherPQ` correspond à `table`, `adc` et `candidats`, puis au reclassement de `chercher` quand `reclasser` vaut R. `decoder` sert seulement à vérifier l'identité du point 4.

```text
ALGORITHME InsérerHNSW
ENTRÉES : vecteur v, M, ef_construction, m_L = 1 / ln M
  L ← partie entière de (− ln U × m_L), avec U uniforme sur ]0 ; 1]
  SI le graphe est vide ALORS point d'entrée ← v ; RETOURNER
  e ← point d'entrée
  POUR l DU niveau max DESCENDANT JUSQU'À L + 1 FAIRE  e ← Faisceau(v, {e}, 1, l)  FIN POUR
  POUR l DE min(L, niveau max) DESCENDANT JUSQU'À 0 FAIRE
      trouvés ← Faisceau(v, entrées, ef_construction, l)
      relier v aux M premiers de trouvés, dans les deux sens
      SI un voisin dépasse son plafond (2M en couche 0, M au-dessus) ALORS garder ses liens les plus courts
      entrées ← trouvés
  FIN POUR
  SI L > niveau max ALORS point d'entrée ← v

ALGORITHME Faisceau(q, entrées, ef, couche)
  candidats ← entrées ; retenus ← entrées (au plus ef) ; visités ← entrées
  TANT QUE candidats n'est pas vide FAIRE
      c ← le candidat le plus proche de q, retiré de la file
      SI ‖q − c‖ > ‖q − (pire des retenus)‖ ALORS sortir
      POUR CHAQUE voisin v de c dans la couche, non visité FAIRE
          marquer v visité
          SI moins de ef retenus OU v plus proche que le pire ALORS ajouter v aux candidats et aux retenus ; garder les ef meilleurs
      FIN POUR
  FIN TANT QUE
  RETOURNER retenus, du plus proche au plus loin

ALGORITHME ChercherHNSW(q, k, ef)
  e ← point d'entrée
  POUR l DU niveau max DESCENDANT JUSQU'À 1 FAIRE  e ← Faisceau(q, {e}, 1, l)  FIN POUR
  RETOURNER les k premiers de Faisceau(q, {e}, max(ef, k), 0)
```

**Complexité.** Une recherche visite les voisins des nœuds explorés, au plus 2M par nœud sur la couche 0 : son coût est de l'ordre de (nœuds explorés) × 2M × d, et le nombre de nœuds explorés croît avec ef. Sur des données favorables, la descente demande de l'ordre de log N sauts ; c'est observé, pas garanti. Une insertion coûte une recherche de largeur ef_construction, plus l'élagage des listes voisines. La mémoire vaut N × 4d octets pour les vecteurs, plus au plus N × 2M identifiants pour la couche 0 et en moyenne N × M/(M − 1) pour les couches hautes (point 5).

**Du squelette au code.** `InsérerHNSW` est `HNSW.ajouter` : le tirage de `niv`, la descente gloutonne, puis la boucle sur les couches avec `voisins`, le lien inverse et le tri d'élagage. `Faisceau` est `_couche`, avec ses deux tas `candidats` et `meilleurs` et l'ensemble `visites`. `ChercherHNSW` est `HNSW.chercher`.

## Cas d'usage réels aux Émirats

Les volumes, les dimensions, les paramètres et les objectifs ci-dessous sont illustratifs ; chaque équipe les mesure sur ses propres vecteurs, avec son propre modèle d'embedding. Les bibliothèques et les bases citées le sont comme exemples du marché.

### Secteur public — régler ef pour deux millions de passages bilingues

Une entité de services publics en ligne, accessible par UAE Pass, indexe deux millions de passages de pages de démarches, moitié en arabe, moitié en anglais, avec un modèle d'embedding multilingue de dimension 768. En float32, les vecteurs occupent 2 × 10⁶ × 3 072 octets = 6,144 Go. Un graphe HNSW à M = 16 y ajoute au plus 256 Mo de liens sur la couche 0 et environ 8,5 Mo pour les couches hautes, puisque chaque nœud n'a en moyenne que 1/15 de niveau supplémentaire (point 5) : le tout tient dans la mémoire d'un seul serveur. L'équipe tire 1 000 questions réelles, calcule leurs 10 vrais plus proches voisins par recherche exacte, puis augmente ef jusqu'à ce que le Recall@10 de l'index dépasse 0,98 dans chaque langue, sans sortir de son budget de latence au 95e percentile. À chaque reconstruction de l'index, ce test tourne dans la chaîne d'intégration continue : si le rappel passe sous l'objectif, la nouvelle version n'est pas déployée, comme à l'étape 25. Sans ce réglage mesuré, on choisit ef au hasard : trop petit, l'outil de recherche manque la page de la bonne démarche et l'agent oriente l'usager vers le mauvais guichet ; trop grand, la latence explose aux heures de pointe. Les pages et leurs vecteurs restent hébergés dans le pays, conformément aux exigences de la PDPL et de l'entité (à confirmer avec le texte en vigueur). On suit le Recall@10 contre l'exact par langue et la latence p95 de l'outil.

### Banque — IVF-PQ pour garder vingt millions de passages sur ses propres serveurs

Une banque de détail de Dubaï veut que son assistant de conformité cherche dans vingt millions de passages : politiques internes, circulaires, correspondances archivées. En float32 et en dimension 768, il faudrait 61,44 Go de mémoire vive, au-delà de ce que ses serveurs approuvés peuvent consacrer à l'index ; or la banque ne veut pas envoyer ces textes chez un hébergeur extérieur. L'équipe combine IVF et PQ : 16 384 listes, une puissance de deux proche de C* = √(2 × 10⁷ × 16) ≈ 17 889 pour nprobe = 16 (point 2), et des codes PQ de 96 octets, soit 1,92 Go pour toute la base. Une requête compare q aux 16 384 centres, lit les codes d'environ 19 531 candidats, puis reclasse les 100 meilleurs avec leurs vecteurs exacts conservés sur disque. Cela fait environ 1,47 × 10⁷ opérations, contre 1,536 × 10¹⁰ multiplications pour la recherche exacte, soit environ 1 000 fois moins. Le point 3 dit exactement ce que coûte la compression : après reclassement, le rappel est la part des vrais voisins présents parmi les 100 candidats, et l'équipe le mesure contre la recherche exacte sur un échantillon de questions de conseillers. Sans PQ, l'index ne tiendrait pas sur l'infrastructure interne ; sans reclassement, un passage de politique pourrait être doublé par un passage voisin moins précis. On suit le Recall@10 après reclassement, la mémoire de l'index et la latence p95, à chaque mise à jour des politiques.

### Assurance — repérer des déclarations presque identiques sans seuil faussé

Un assureur auto et santé indexe cinq millions de déclarations de sinistre, chacune représentée par l'embedding de sa description, soit 15,36 Go en float32. Pour chaque nouvelle déclaration, l'agent de détection cherche les cinq plus proches déclarations passées. Si l'une d'elles est à une distance inférieure à un seuil calibré, il signale une possible déclaration en double, par exemple la même description et le même garage pour deux véhicules différents. Le rappel de l'index devient ici un taux de fraude non détectée : une déclaration jumelle que l'index ne renvoie pas ne sera jamais comparée. L'équipe mesure donc le Recall@5 de son HNSW contre la recherche exacte, sur un échantillon de déclarations dont les jumelles sont connues. Elle applique le seuil après un reclassement par distance exacte, jamais sur une distance PQ : la borne du point 4 montre qu'une distance compressée peut s'écarter de la vraie de toute l'erreur de quantification, ce qui fausserait un seuil absolu calibré sur des distances exactes (étape 19). L'assurance est supervisée par la CBUAE : l'agent ne refuse rien, il transmet le dossier à un enquêteur humain, qui décide. On suit le Recall@5 contre l'exact et la part des signalements confirmés par les enquêteurs.

### Immobilier — des listes IVF qui vieillissent

Une agence immobilière de Dubaï et d'Abu Dhabi indexe 400 000 annonces, avec l'embedding de leur description, la communauté et le prix en AED/sqft. Son index IVF compte 512 listes, de l'ordre de √N ≈ 632, soit 781 annonces par liste en moyenne. Les centres ont été appris en janvier. En juin, plusieurs projets off-plan d'une nouvelle communauté ont ajouté des milliers d'annonces très semblables, toutes rangées dans les deux ou trois listes dont le centre est le moins éloigné, si bien que la plus grosse liste dépasse 4 000 annonces. Le point 2 explique la suite : le coût d'une requête dépend de la taille des listes visitées, et les questions sur la nouvelle communauté deviennent cinq fois plus lentes. Comme leurs vrais voisins se répartissent mal entre listes, leur rappel baisse aussi. L'équipe surveille le rapport entre la plus grosse liste et la taille moyenne, ainsi que l'objectif J du k-means recalculé sur les annonces récentes, et réapprend les centres quand ce rapport dépasse 3 (seuil illustratif). Elle réindexe ensuite toutes les annonces. Sans cette surveillance, l'agent de recommandation proposerait aux acheteurs des biens d'une autre communauté pour les questions sur la nouvelle, sans que personne s'en aperçoive. On suit le Recall@10 par communauté et le rapport des tailles de listes.

### Crypto — insérer en continu, supprimer proprement

Une plateforme d'actifs virtuels agréée par la VARA garde une mémoire des incidents de liquidité et des alertes traitées. Chaque rapport d'incident, dès qu'il est clos, est vectorisé et inséré dans un HNSW, et l'agent de surveillance appelle l'outil « incidents similaires » pour proposer à l'astreinte la procédure qui avait marché la dernière fois. Le HNSW accepte l'insertion au fil de l'eau : chaque ajout coûte une recherche de largeur ef_construction, sans reconstruction. La suppression est plus délicate : la plupart des implémentations marquent le nœud comme supprimé et le filtrent à la recherche, sans retirer ses liens. Quand les nœuds marqués atteignent une part importante du graphe, par exemple 20 % (seuil illustratif), le faisceau perd du temps sur des nœuds inutiles et le rappel baisse, si bien que l'équipe reconstruit l'index chaque semaine à partir des vecteurs bruts conservés. Retirer un vecteur de l'index n'efface pas le rapport lui-même : la conservation des enregistrements suit les règles de la plateforme et de la VARA (à confirmer avec le règlement en vigueur), comme l'étape 16 le rappelait pour la mémoire. On suit la part de nœuds marqués et le Recall@5 contre l'exact après chaque reconstruction.

### RH — le filtre par émirat qui vide les résultats

Un cabinet RH présent dans plusieurs émirats indexe 300 000 profils de candidats. Un recruteur demande dix profils proches d'une fiche de poste, mais seulement parmi les candidats basés à Abu Dhabi et titulaires d'un visa en cours de validité, ce qui ne garde que 2 % de la base. Si l'agent demande les 100 plus proches voisins à l'index puis applique le filtre, il ne lui reste en moyenne que 100 × 0,02 = 2 profils au lieu des 10 demandés : l'index a classé toute la base, puis le filtre a jeté presque tout. L'équipe inverse l'ordre quand le sous-ensemble filtré est petit. Les 2 % représentent 6 000 profils, dont la recherche exacte ne coûte que 6 000 × 768 ≈ 4,6 millions de multiplications : on filtre d'abord, puis on cherche exactement, comme le service public de l'étape 18 qui filtre les droits avant de calculer la similarité. Pour les filtres larges, elle garde l'index approché, ou des index séparés par émirat. Les filtres eux-mêmes doivent être licites et justifiés par le poste, et les profils relèvent de la PDPL. On suit le nombre de résultats renvoyés rapporté au nombre demandé, et le rappel sur les requêtes filtrées.

## Pièges et limites

- **Faire confiance aux réglages par défaut.** Le rappel d'un index dépend des données et des paramètres : on le mesure contre la recherche exacte sur un échantillon de vraies questions, et on le remesure à chaque reconstruction.
- **Appliquer un seuil absolu sur une distance approchée.** Une distance PQ s'écarte de la vraie de toute l'erreur de quantification (point 4) : on reclasse avec les vecteurs exacts avant de comparer à un seuil.
- **Oublier que l'IVF vieillit.** Des centres appris sur d'anciennes données donnent des listes déséquilibrées : coût et rappel se dégradent sans aucune erreur visible. On surveille la taille des listes et on réapprend.
- **Filtrer après la recherche approchée.** Un filtre qui garde une fraction f de la base laisse en moyenne k × f résultats : on filtre avant, ou l'on passe à la recherche exacte sur le sous-ensemble.
- **Utiliser un index approché sans en avoir besoin.** Pour quelques dizaines de milliers de vecteurs (ordre de grandeur illustratif), la recherche exacte est souvent assez rapide, et son rappel vaut toujours 1.

### Exercice feuille blanche

1. Sans regarder le code, écrire `kmeans` à partir des deux demi-étapes, puis retrouver la suite 246 → 89,2 → 41,68 → 4 de l'exemple à la main.
2. Prédire, puis vérifier : pour N = 10⁶ et nprobe = 16, que vaut C* ? (Réponse : √(1,6 × 10⁷) = 4 000.) Pour d = 1 024 et m = 64, combien d'octets prend un code PQ et quel est le taux de compression ? (Réponse : 64 octets contre 4 096, soit 64 fois moins.)
3. Trouver le bug : dans `_couche`, la sortie s'écrit `if d > meilleurs[0][0]: break`, sans le signe moins. Que devient la recherche ? (Réponse : `meilleurs` contient des distances changées de signe, donc négatives ; la condition est vraie dès que la distance du candidat est positive, et la boucle s'arrête avant d'explorer le moindre voisin : la recherche ne renvoie plus que les points d'entrée.) Autre variante : `niv = int(-math.log(self.rng.random()) * self.mL)`. Que se passe-t-il le jour où `random()` renvoie 0 ? (Réponse : `math.log(0)` lève `ValueError` ; c'est pourquoi le code utilise `1.0 - random()`.)

## Pour aller plus loin

L'**IVF-PQ** encode le résidu x − μ_c(x) plutôt que x, ce qui réduit l'erreur de quantification ; l'**OPQ** applique d'abord une rotation apprise pour équilibrer l'information entre sous-vecteurs. L'initialisation **k-means++** choisit des centres éloignés les uns des autres et réduit le risque d'un mauvais minimum local. Le HNSW complet sélectionne ses voisins avec une heuristique de diversité, qui garde des liens vers plusieurs directions au lieu des M plus proches. Les index en graphe sur disque, comme DiskANN (graphe Vamana), servent quand les vecteurs ne tiennent pas en mémoire. La quantification scalaire (int8) et binaire sont des alternatives plus simples à la PQ ; la quantification des poids des modèles est étudiée à l'étape 73 bis. Articles fondateurs : Lloyd (1982) pour le k-means, Jégou, Douze et Schmid (2011) pour la quantification par produit, Malkov et Yashunin (2018) pour le HNSW.

> Étape 30 quinquies du parcours · Prérequis : [Découpage avancé et compression](<30d-RAG-Decoupage-Avance-et-Compression.md>) · Suite : [Corrective RAG et Agentic RAG](<30f-RAG-Corrective-et-Agentic-RAG.md>)
