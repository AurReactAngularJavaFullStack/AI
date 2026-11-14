# Étape 36 bis — Transformer — Mélange d'experts (MoE)

**Dossier :** 06-Attention-et-Transformer

> Étape 36 bis du parcours · Prérequis : [Normalisation de couche](<36-Normalisation-de-Couche.md>) · Suite : [Encodeur, attention croisée et embeddings](<36c-Encodeur-Attention-Croisee-et-Embeddings.md>)

## Définition

Un **mélange d'experts** (*Mixture of Experts*, MoE) remplace le bloc feed-forward d'une couche de Transformer par N blocs du même type, appelés **experts**, et par un petit **routeur**. Pour chaque token, le routeur calcule un score par expert, n'en garde que les k meilleurs (souvent k = 1 ou 2), et la sortie de la couche est la moyenne des sorties de ces k experts, pondérée par des poids qui somment à 1. Les N − k autres experts ne calculent rien pour ce token. Le modèle a donc beaucoup de paramètres **au total**, qui doivent tous être chargés en mémoire, mais peu de paramètres **actifs** par token, qui fixent le calcul et donc la latence. Pour que tous les experts servent, l'entraînement ajoute une **perte auxiliaire d'équilibrage de charge** et limite le nombre de tokens qu'un expert peut recevoir dans un lot (sa **capacité**).

## Rôle dans un agent

Le MoE s'exécute dans chaque couche du LLM, pendant l'étape **décider** de la boucle percevoir → décider → agir → observer. Le développeur d'agent ne code presque jamais de MoE, mais il en subit les conséquences à quatre endroits. Quand il dimensionne un serveur pour un modèle ouvert hébergé sur site, la mémoire se calcule sur les paramètres totaux, alors que le débit et le coût par token se calculent sur les paramètres actifs : confondre les deux fait commander la mauvaise machine. Quand il lit une fiche de modèle (« 47 milliards de paramètres dont 13 actifs »), il doit savoir ce que chaque nombre engage. Quand il exige des réponses reproductibles pour un audit, il doit savoir que la capacité des experts rend la sortie d'un token dépendante des autres requêtes du même lot, comme BatchNorm à l'étape 36. Enfin, il ne doit pas confondre ce routeur, qui choisit des experts **par token et par couche**, avec le routeur de l'agent, qui choisit un outil, un modèle ou un adaptateur (étape 73) **pour une requête entière**.

## Équation complète

Logits du routeur, puis probabilités (softmax de l'étape 2) :

$$
h = W_r \, x, \qquad p_i = \frac{e^{h_i}}{\sum_{j=1}^{N} e^{h_j}}
$$

Poids renormalisés sur les k experts retenus :

$$
g_i = \frac{p_i}{\sum_{j \in \operatorname{Top}_k(x)} p_j} \quad \text{si } i \in \operatorname{Top}_k(x), \qquad g_i = 0 \quad \text{sinon}
$$

Sortie de la couche :

$$
y = \sum_{i \in \operatorname{Top}_k(x)} g_i \, E_i(x)
$$

Paramètres totaux et actifs :

$$
\Theta_{tot} = \Theta_{part} + N \, \Theta_{exp}, \qquad \Theta_{act} = \Theta_{part} + k \, \Theta_{exp}
$$

Calcul par token, en opérations flottantes :

$$
\text{FLOP par token} \approx 2 \, \Theta_{act}
$$

Charge et probabilité moyenne de chaque expert sur un lot de n tokens :

$$
f_i = \frac{1}{k \, n} \sum_{t=1}^{n} \mathbb{1}\bigl[i \in \operatorname{Top}_k(x_t)\bigr], \qquad P_i = \frac{1}{n} \sum_{t=1}^{n} p_i(x_t)
$$

Perte auxiliaire d'équilibrage (Switch Transformer) et perte totale :

$$
\mathcal{L}_{aux} = N \sum_{i=1}^{N} f_i \, P_i, \qquad \mathcal{L} = \mathcal{L}_{\text{tâche}} + \alpha_{aux} \, \mathcal{L}_{aux}
$$

Capacité d'un expert et tokens abandonnés :

$$
C = \left\lceil \frac{c \, k \, n}{N} \right\rceil, \qquad \text{abandonnés} = \sum_{i=1}^{N} \max\bigl(0,\; \text{charge}_i - C\bigr)
$$

## Décryptage des symboles

$$
x
$$

Le vecteur d'un token à l'entrée de la couche, déjà normalisé (étape 36) : d nombres réels ; variable Python `x`.

$$
d
$$

La largeur du modèle, notée d_model aux étapes 33 et 34 : un entier ≥ 1 ; c'est `len(x)`.

$$
N
$$

Le nombre d'experts de la couche : un entier ≥ 1 (4 dans le programme, 8 dans Mixtral 8x7B) ; c'est `len(experts)`.

$$
E_i
$$

L'expert numéro i, une fonction qui transforme un vecteur de d nombres en un autre : dans un vrai modèle, un bloc feed-forward complet ; dans le programme, une matrice 2 × 2 appliquée par `matvec(experts[i], x)`.

$$
W_r
$$

La matrice du routeur, de taille N × d, apprise avec le reste du modèle : une ligne par expert ; variable Python `W_r`.

$$
h
$$

Les N logits du routeur, h = W_r x : des réels quelconques ; `matvec(W_r, x)`.

$$
p_i
$$

La probabilité que le routeur donne à l'expert i, softmax des logits : un réel dans ]0 ; 1[, et les N probabilités somment à 1 ; `softmax(logits)[i]`.

$$
k
$$

Le nombre d'experts calculés par token : un entier, 1 ≤ k ≤ N ; argument `k`.

$$
\operatorname{Top}_k(x)
$$

L'ensemble des indices des k plus grandes probabilités pour le token x, égalités départagées par le plus petit indice : `top_k(p, k)`.

$$
g_i
$$

Le poids (la « porte ») de l'expert i dans la sortie : nul hors de Top_k(x), et les poids retenus somment à 1 ; dictionnaire renvoyé par `portes(logits, k)`.

$$
y
$$

La sortie de la couche MoE pour le token x : d réels ; premier élément renvoyé par `couche_moe`. Dans le bloc complet, on l'ajoute à x par la connexion résiduelle.

$$
\Theta_{part}, \quad \Theta_{exp}
$$

Le nombre de paramètres partagés par tous les tokens (attention, embeddings, normes, routeur) et le nombre de paramètres d'un expert, compté sur toutes les couches : des entiers ; arguments `p_partages` et `p_expert`.

$$
\Theta_{tot}, \quad \Theta_{act}
$$

Les paramètres totaux, qui occupent la mémoire, et les paramètres actifs, qui travaillent pour chaque token : des entiers ; valeurs renvoyées par `parametres_moe`.

$$
n
$$

Le nombre de tokens du lot sur lequel on mesure la charge : un entier ≥ 1 ; c'est `len(probas)`.

$$
f_i
$$

La part des affectations du lot reçue par l'expert i : un réel dans [0 ; 1], et les N parts somment à 1 ; liste `f` renvoyée par `perte_auxiliaire`.

$$
P_i
$$

La probabilité moyenne que le routeur donne à l'expert i sur le lot : un réel dans [0 ; 1], et les N moyennes somment à 1 ; liste `P`.

$$
\mathcal{L}_{aux}
$$

La perte auxiliaire d'équilibrage : un réel ≥ 0, qui vaut 1 dès que la charge est uniforme ; premier élément renvoyé par `perte_auxiliaire`.

$$
\alpha_{aux}
$$

Le poids de la perte auxiliaire dans la perte totale : un réel > 0, petit (l'article Switch Transformer retient 10⁻²) ; il n'apparaît pas dans le programme, qui étudie la perte auxiliaire seule.

$$
c, \quad C
$$

Le facteur de capacité, un réel > 0 choisi par l'équipe (1 ou 1,25 sont des réglages courants), et la capacité qui en découle, le nombre de places par expert et par lot : un entier ; argument `c` et valeur renvoyée par `capacite`.

## Démonstration

### 1. Les poids retenus somment à 1, et renormaliser revient à une softmax des seuls logits retenus

On note Z = ∑ⱼ e^(hⱼ) la somme des N exponentielles, de sorte que pᵢ = e^(hᵢ) / Z. On remplace dans la définition de gᵢ :

$$
g_i = \frac{e^{h_i} / Z}{\sum_{j \in \operatorname{Top}_k} e^{h_j} / Z} = \frac{e^{h_i}}{\sum_{j \in \operatorname{Top}_k} e^{h_j}}
$$

Z se simplifie, parce qu'il figure au numérateur et à chaque terme du dénominateur. Les gᵢ sont donc positifs et leur somme sur Top_k vaut 1 : c'est une loi de probabilité sur les experts retenus, exactement la softmax des k logits retenus. Deux conséquences pratiques. D'abord, l'exponentielle est croissante, donc l'ordre des pᵢ est celui des hᵢ : on peut choisir les k meilleurs experts directement sur les logits, sans calculer la softmax sur les N experts. Ensuite, pour k = 2, avec les deux logits retenus h_a ≥ h_b :

$$
g_a = \frac{e^{h_a}}{e^{h_a} + e^{h_b}} = \frac{1}{1 + e^{-(h_a - h_b)}} = \sigma(h_a - h_b)
$$

Le poids ne dépend que de l'écart entre les deux logits. Dans l'exemple, h = [2, 1, 0, −1], donc g = σ(1) ≈ 0,7311 pour le premier expert et 0,2689 pour le second ; le programme vérifie les deux égalités.

### 2. La sortie est une moyenne pondérée des experts retenus

Comme les gᵢ sont positifs et somment à 1, y est une combinaison convexe des k sorties Eᵢ(x) : chaque coordonnée de y reste entre la plus petite et la plus grande coordonnée correspondante des experts retenus. Si tous les experts étaient identiques, y serait égal à leur sortie commune et la couche se comporterait comme un bloc feed-forward dense. Avec k = N, on retrouve un mélange dense (« soft ») où tous les experts calculent : le programme le calcule pour comparaison, avec 24 multiplications au lieu de 16.

### 3. Avec k = 1, renormaliser coupe le gradient du routeur

Pour k = 1, la renormalisation donne gᵢ = pᵢ / pᵢ = 1, donc y = Eᵢ(x). La sortie ne dépend plus de W_r que par le **choix** de l'expert, qui ne change que lorsqu'un logit en dépasse un autre : entre deux changements, la dérivée de y par rapport à W_r est nulle, et la perte de la tâche n'apprend rien au routeur. C'est pourquoi le Switch Transformer garde le poids brut gᵢ = pᵢ quand k = 1. La sortie y = pᵢ Eᵢ(x) a alors pour dérivée, par la jacobienne de la softmax (étape 2) et parce que ∂hᵢ/∂W_r[i][j] = xⱼ :

$$
\frac{\partial y}{\partial W_r[i][j]} = p_i \, (1 - p_i) \, x_j \, E_i(x)
$$

Dans l'exemple, p₁ ≈ 0,6439, x₁ = 1 et la première coordonnée de E₁(x) vaut 2 : la dérivée vaut 2 × 0,6439 × 0,3561 ≈ 0,4586, la valeur que le programme retrouve par différence finie, contre exactement 0 avec renormalisation. Pour k ≥ 2, renormaliser ne pose pas ce problème, puisque g_a = σ(h_a − h_b) dépend continûment des logits (point 1).

### 4. Paramètres totaux, paramètres actifs et calcul

Chaque expert existe en mémoire, qu'il serve ou non : on compte une fois les paramètres partagés et N fois ceux d'un expert, d'où Θ_tot = Θ_part + N Θ_exp. Pour un token, seuls les paramètres partagés et ceux des k experts retenus participent au calcul, d'où Θ_act = Θ_part + k Θ_exp. Le calcul se déduit de Θ_act : un produit matrice-vecteur de taille d_sortie × d_entrée fait d_sortie × d_entrée multiplications et d_sortie × (d_entrée − 1) additions, soit presque deux opérations par paramètre. D'où l'approximation « 2 Θ_act opérations par token », qui laisse de côté le calcul de l'attention sur le contexte, en n² (étapes 31 et 72).

Exemple jouet du programme : un routeur de 4 × 2 = 8 paramètres (les seuls paramètres partagés ici) et 4 experts de 4 paramètres donnent 8 + 4 × 4 = 24 paramètres totaux et 8 + 2 × 4 = 16 actifs pour k = 2.

Exemple réel : la configuration publiée de Mixtral 8x7B (à vérifier dans son fichier de configuration) indique d = 4 096, une largeur intermédiaire de 14 336, 32 couches, 8 experts dont 2 actifs, un vocabulaire de 32 000 tokens et 8 têtes de clés-valeurs de largeur 128. Un expert SwiGLU a trois matrices, soit 3 × 4 096 × 14 336 = 176 160 768 paramètres par couche. L'attention à têtes de clés-valeurs partagées (étape 34) compte 2 × 4 096² + 2 × 4 096 × 1 024 = 41 943 040 paramètres par couche ; s'y ajoutent les embeddings d'entrée et de sortie (2 × 32 000 × 4 096), les normes et le routeur (8 × 4 096 par couche). La formule donne 46 702 792 704 paramètres totaux et 12 879 925 248 actifs, ce qui retrouve les 46,7 et 12,9 milliards annoncés par l'éditeur. Pour DeepSeek-V3, l'éditeur annonce 671 milliards de paramètres au total et 37 milliards actifs par token : 5,51 % des paramètres travaillent pour chaque token, et le calcul, environ 2 × 37 = 74 milliards d'opérations par token, est 18,14 fois plus petit que celui d'un modèle dense de 671 milliards. La mémoire, elle, reste celle des 671 milliards : 671 Go à un octet par paramètre, avant le cache clé-valeur.

### 5. La perte auxiliaire : ce qu'elle vaut, ce qu'elle garantit, ce qu'elle ne garantit pas

**Elle vaut 1 dès que la charge est uniforme.** Si fᵢ = 1/N pour tout i, alors

$$
\mathcal{L}_{aux} = N \sum_{i=1}^{N} \frac{1}{N} P_i = \sum_{i=1}^{N} P_i = 1
$$

quelles que soient les probabilités moyennes Pᵢ, parce qu'elles somment à 1 (moyenne de lois de probabilité). Le programme le vérifie sur deux lots équilibrés, dont l'un a des Pᵢ très inégaux ([0,387 ; 0,15 ; 0,164 ; 0,298]).

**Quand charge et probabilités coïncident, elle est minimale à l'uniforme.** Si fᵢ = Pᵢ, l'inégalité de Cauchy-Schwarz (étape 14) appliquée aux vecteurs (P₁, …, P_N) et (1, …, 1) donne

$$
1 = \Bigl(\sum_{i=1}^{N} P_i \cdot 1\Bigr)^2 \le \Bigl(\sum_{i=1}^{N} P_i^2\Bigr) \cdot N
\quad\Longrightarrow\quad
\mathcal{L}_{aux} = N \sum_{i=1}^{N} P_i^2 \ge 1
$$

avec égalité si et seulement si P est proportionnel à (1, …, 1), c'est-à-dire uniforme. Pour P = [0,4 ; 0,3 ; 0,2 ; 0,1], on trouve 4 × 0,30 = 1,2. Quand tous les tokens partent vers le même expert avec p = [0,7 ; 0,1 ; 0,1 ; 0,1], la perte vaut 4 × 1 × 0,7 = 2,8.

**Sans cette coïncidence, « minimale à l'uniforme » est faux.** Contre-exemple chiffré avec N = 2 et top-1 : trois tokens ont p = (0,55 ; 0,45) et vont à l'expert 1 ; un token a p = (0 ; 1) et va à l'expert 2. Alors f = (0,75 ; 0,25), P = (0,4125 ; 0,5875) et

$$
\mathcal{L}_{aux} = 2 \, (0{,}75 \times 0{,}4125 + 0{,}25 \times 0{,}5875) = 0{,}9125 < 1
$$

alors que la charge est déséquilibrée. La perte n'est donc pas un indicateur d'équilibre qu'on lit au tableau de bord : c'est un **signal de gradient**. Les fᵢ viennent d'un choix top-k, qui n'est pas dérivable : on les tient fixes, et le gradient passe par les Pᵢ seuls, avec ∂ℒ_aux/∂Pᵢ = N fᵢ. Plus un expert est chargé, plus la descente fait baisser la probabilité que le routeur lui donne. L'indicateur d'équilibre à surveiller est la charge elle-même, par exemple max fᵢ / (1/N).

**Le gradient rééquilibre.** Ajoutons aux logits de chaque token un biais b commun, de N coordonnées, et dérivons ℒ_aux par rapport à bⱼ. La jacobienne de la softmax donne ∂p_tᵢ/∂bⱼ = p_tᵢ (δᵢⱼ − p_tⱼ), où δᵢⱼ vaut 1 si i = j et 0 sinon. En sommant sur les tokens t et les experts i :

$$
\frac{\partial \mathcal{L}_{aux}}{\partial b_j} = \frac{N}{n} \sum_{t=1}^{n} p_{tj} \Bigl(f_j - \sum_{i=1}^{N} f_i \, p_{ti}\Bigr)
$$

La parenthèse est positive quand l'expert j est plus chargé que la moyenne des charges pondérée par les probabilités du token : la descente baisse alors bⱼ, donc la part de j. Si la charge est uniforme, fⱼ = 1/N et la somme pondérée vaut aussi 1/N : le gradient est nul, l'équilibre est un point fixe. Sur 16 tokens tirés avec une graine et biaisés vers l'expert 1, le programme part des charges [13, 1, 1, 1] (ℒ_aux = 2,0464) et atteint [4, 4, 4, 4] en quatre pas de taille 1, avec une perte qui baisse à chaque pas : 1,2562, puis 1,1148, puis 1,0117, puis 1.

### 6. La capacité et les tokens abandonnés

Un lot de n tokens produit k n affectations ; réparties uniformément, chaque expert en reçoit k n / N. La capacité C = ⌈c k n / N⌉ laisse une marge réglée par c. Si la charge est uniforme et c ≥ 1, aucun token n'est abandonné, parce que k n / N ≤ c k n / N ≤ ⌈c k n / N⌉ = C. Si la charge est déséquilibrée, les tokens en surnombre sont abandonnés : ils ne reçoivent aucune contribution des experts et ne gardent que la connexion résiduelle x. Avec n = 8, N = 4, k = 1 et des charges [5, 1, 1, 1], on perd 3 tokens pour c = 1 (C = 2), 2 pour c = 1,25 (C = 3) et 1 pour c = 2 (C = 4). Augmenter c réduit les pertes, mais réserve de la mémoire et du calcul pour des places souvent vides. Le déséquilibre coûte aussi du temps : quand les experts sont répartis sur plusieurs cartes, la couche attend la carte la plus chargée, et son temps est proportionnel à la charge maximale, 5 au lieu de 2, soit 2,5 fois plus long (le goulot de l'étape 69).

### 7. Avec une capacité, la sortie d'un token dépend de ses voisins de lot

Le même token x, avec les mêmes poids, ne reçoit pas toujours la même sortie. Dans le lot [1, 2, 3, 4] (un token par expert), x est le premier token de l'expert 1 et il est servi : la sortie du bloc vaut x + p₁ E₁(x) = [1 ; 2] + 0,6439 × [2 ; 2] ≈ [2,2878 ; 3,2878]. Dans le lot [1, 1, 1, 2] avec C = 2, x arrive en troisième position chez l'expert 1, qui est plein : il est abandonné et la sortie vaut x = [1 ; 2]. C'est le même phénomène que BatchNorm en mode entraînement (étape 36, point 7) : un résultat qui dépend de la composition du lot. Un service qui regroupe les requêtes de plusieurs clients dans un même lot peut donc rendre deux réponses différentes à la même question, même à température nulle.

### 8. Exemple fait à la main (le code reprend ces nombres)

On prend x = [1 ; 2] et un routeur dont les lignes valent [1 ; 0,5], [1 ; 0], [0 ; 0] et [−1 ; 0].

- Logits : h = [1 + 1 ; 1 ; 0 ; −1] = [2 ; 1 ; 0 ; −1].
- Exponentielles : 7,3891 ; 2,7183 ; 1 ; 0,3679 ; somme 11,4752 ; p ≈ [0,6439 ; 0,2369 ; 0,0871 ; 0,0321].
- Top-2 : les experts 1 et 2 ; g = [0,6439 / 0,8808 ; 0,2369 / 0,8808] = [0,7311 ; 0,2689].
- Experts : E₁ multiplie la première coordonnée par 2, donc E₁(x) = [2 ; 2] ; E₂ échange les deux coordonnées, donc E₂(x) = [2 ; 1].
- Sortie : y = 0,7311 × [2 ; 2] + 0,2689 × [2 ; 1] = [2 ; 1,7311].
- Calcul : 8 multiplications pour le routeur et 4 par expert, soit 16, contre 24 si les quatre experts calculaient.

## Effets et comportement

- **k règle le calcul, N règle la mémoire.** Passer de 8 à 16 experts à k fixé double presque la mémoire des experts sans changer le calcul par token ; passer de k = 1 à k = 2 double le calcul des experts sans changer la mémoire.
- **Le routeur coûte peu.** Il ajoute N × d paramètres par couche, 32 768 pour Mixtral, contre 176 millions pour un seul expert.
- **Sans équilibrage, le routage s'effondre.** Un expert un peu meilleur au départ reçoit plus de tokens, apprend plus vite et attire encore plus de tokens ; la perte auxiliaire, ou un mécanisme équivalent, casse cette boucle.
- **La capacité arbitre entre perte de tokens et gaspillage.** Un c petit abandonne des tokens dès que la charge varie ; un c grand réserve des places vides.
- **Les sorties dépendent du lot.** Dès qu'une capacité s'applique, une même requête peut recevoir une sortie différente selon les autres requêtes servies en même temps.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| p = softmax(h) | `softmax(logits)` |
| h = W_r x, Eᵢ(x) | `matvec(W_r, x)`, `matvec(experts[i], x)` |
| Top_k(x) | `top_k(p, k)` |
| gᵢ, renormalisé ou brut | `portes(logits, k, renormaliser)` |
| y = ∑ gᵢ Eᵢ(x) | `couche_moe(x, W_r, experts, k)` |
| Θ_tot, Θ_act | `parametres_moe(p_partages, p_expert, n_experts, k)` |
| décompte d'un modèle réel | `parametres_config(d, d_ff, couches, n_experts, k, vocab, d_kv)` |
| fᵢ, Pᵢ, ℒ_aux | `perte_auxiliaire(probas, k)` |
| ∂ℒ_aux/∂bⱼ | `gradient_biais(probas, f)` |
| C = ⌈c k n / N⌉ | `capacite(n_tokens, n_experts, k, c)` |
| tokens gardés ou abandonnés | `repartir_avec_capacite(choix, n_experts, cap)` |

### Déroulé, ligne par ligne

Les indices Python commencent à 0 : l'indice 0 désigne l'expert 1 de la démonstration, l'indice 1 l'expert 2, et ainsi de suite.

**`softmax(z)`** retranche le maximum avant l'exponentielle, ce qui ne change pas le résultat (étape 2) et évite un débordement. Pour `[2.0, 1.0, 0.0, -1.0]`, elle renvoie environ `[0.6439, 0.2369, 0.0871, 0.0321]`.

**`matvec(W, x, compteur)`** calcule le produit matrice-vecteur et ajoute `len(W) * len(x)` au compteur, une multiplication par coefficient de W : 8 pour le routeur 4 × 2, 4 pour un expert 2 × 2.

**`top_k(p, k)`** trie les indices selon la clé `(-p[i], i)` : les plus grandes probabilités d'abord, et à égalité le plus petit indice, pour que le choix soit déterministe. La garde lève `ValueError` si k vaut 0 ou dépasse N.

**`portes(logits, k, renormaliser)`**.

- `choisis = top_k(p, k)` donne `[0, 1]` pour l'exemple.
- `total` vaut 0,6439 + 0,2369 = 0,8808.
- Avec `renormaliser=True`, chaque poids vaut `p[i] / total` : 0,7311 et 0,2689. Avec `renormaliser=False`, il reste `p[i]`, ce que fait le Switch Transformer pour k = 1.

**`couche_moe(x, W_r, experts, k, renormaliser, compteur)`** appelle `portes` sur les logits, puis ne calcule que les experts présents dans le dictionnaire `g` : la boucle `for i, gi in g.items()` ajoute `gi * sortie` à `y`. C'est cette boucle qui rend la couche creuse : les experts absents de `g` ne sont jamais appelés, et le compteur le prouve (16 multiplications contre 24 pour k = 4).

**`parametres_moe`** applique les deux formules du point 4. **`parametres_config`** construit les paramètres partagés d'un décodeur réel : `attention = (2 * d * d + 2 * d * d_kv) * couches`, puis les deux tables d'embeddings `2 * vocab * d`, les `2 * couches + 1` normes de d coefficients et le routeur `n_experts * d * couches` ; un expert compte `3 * d * d_ff * couches`.

**`perte_auxiliaire(probas, k)`** compte les affectations de chaque expert avec `top_k`, divise par `k * n` pour obtenir `f`, moyenne les probabilités pour obtenir `P`, et renvoie `N * sum(f_i * P_i)`. Pour le contre-exemple, `f = [0.75, 0.25]`, `P = [0.4125, 0.5875]` et la perte vaut 0,9125.

**`gradient_biais(probas, f)`** est la formule du point 5 : pour chaque token, `moyenne_t` vaut ∑ fᵢ p_tᵢ, puis chaque coordonnée reçoit `(N / n) * p[j] * (f[j] - moyenne_t)`.

**`capacite`** renvoie `math.ceil(c * k * n_tokens / n_experts)` : 2, 3 et 4 pour c = 1, 1,25 et 2. **`repartir_avec_capacite`** parcourt les choix dans l'ordre du lot et garde un token tant que son expert a une place libre (`places[e] < cap`).

**`main()`**, bloc par bloc.

1. Le token de l'exemple : logits, probabilités, poids, sortie `[2.0, 1.7311]`, 16 multiplications ; les `assert` vérifient Σ g = 1, g = σ(1) et l'égalité avec la softmax des deux logits retenus (point 1).
2. `sortie_k1` remplace le coefficient `W_r[0][0]` par une valeur voisine et recalcule la première coordonnée de y. La différence finie centrée vaut exactement 0 avec renormalisation et 0,458577 sans, ce que l'`assert` compare à 2 p₁ (1 − p₁) (point 3).
3. Les comptes de paramètres : 24 et 16 pour l'exemple jouet ; 46 702 792 704 et 12 879 925 248 pour la configuration de Mixtral, arrondis à 46,7 et 12,9 milliards ; puis le rapport 0,0551 et le facteur 18,14 de DeepSeek-V3 (point 4).
4. La perte auxiliaire : 1 pour deux lots équilibrés, 2,8 pour l'effondrement, 1,2 pour f = P = [0,4 ; 0,3 ; 0,2 ; 0,1], et 0,9125 pour le contre-exemple (point 5).
5. `random.seed(7)` fixe les 16 tokens. À chaque pas, on recalcule les probabilités avec le biais `b`, la charge et la perte, puis `b` recule d'un pas de gradient. Les `assert` vérifient la charge de départ [13, 1, 1, 1], la baisse de la perte et l'arrivée à [4, 4, 4, 4] ; le dernier vérifie que le gradient est nul quand la charge est uniforme.
6. La capacité et les tokens abandonnés pour les deux lots du point 6, puis le facteur 2,5 de la charge maximale.
7. Le même token x dans deux lots : servi dans le premier, abandonné dans le second (point 7).
8. Un k trop grand et un k nul lèvent `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(z)`** — Cette fonction est le standardiste qui transforme les préférences brutes du routeur en parts d'une même tarte : elle reçoit la liste z des logits, retranche d'abord le plus grand à chacun, ce qui ne change pas le résultat et évite tout débordement, prend l'exponentielle de chaque valeur décalée et la divise par leur somme. Elle renvoie une liste de probabilités positives qui totalisent 1, environ `[0.6439, 0.2369, 0.0871, 0.0321]` pour les logits `[2.0, 1.0, 0.0, -1.0]` de l'exemple ; `portes`, la perte auxiliaire et la boucle d'équilibrage du bloc 5 s'appuient toutes sur elle.

**`matvec(W, x, compteur)`** — On peut la voir comme un ouvrier qui fait une multiplication matrice-vecteur et pointe ses heures en même temps : elle reçoit une matrice W, un vecteur x et, facultativement, un compteur en forme de liste à une case, lève une `ValueError` si le nombre de colonnes de W ne correspond pas à la longueur de x, puis ajoute au compteur une multiplication par coefficient de W. Elle renvoie le produit W x, ligne par ligne ; le routeur 4 × 2 coûte ainsi 8 multiplications et chaque expert 2 × 2 en coûte 4, ce qui permet à `main` de prouver que le routage top-2 ne fait que 16 multiplications contre 24 pour le mélange dense.

**`top_k(p, k)`** — Cette fonction est le jury qui proclame les k lauréats d'un concours : elle reçoit la liste p des probabilités et le nombre k de places, lève une `ValueError` si k vaut 0 ou dépasse le nombre d'experts, puis trie les indices par probabilité décroissante et, à égalité, par indice croissant, pour que le choix soit toujours le même. Elle renvoie la liste des k indices retenus, `[0, 1]` pour l'exemple avec k = 2 ; `portes` s'en sert pour choisir les experts, et `perte_auxiliaire` pour compter combien de tokens chaque expert reçoit.

**`portes(logits, k, renormaliser)`** — C'est l'aiguilleur qui décide quelle part du token chaque expert retenu traitera : la fonction reçoit les logits du routeur, le nombre k d'experts à retenir et un drapeau `renormaliser`, vrai par défaut, calcule les probabilités par `softmax`, choisit les k meilleures par `top_k` et additionne leurs probabilités. Elle renvoie un dictionnaire qui associe à chaque expert retenu son poids, soit sa probabilité divisée par ce total, 0,7311 et 0,2689 pour l'exemple, soit, sans renormalisation, sa probabilité brute, comme le fait le Switch Transformer pour k = 1 ; ce choix décide, au bloc 2, si le routeur reçoit encore un gradient.

**`perte_auxiliaire(probas, k)`** — Cette fonction est l'inspecteur du travail qui vérifie qu'aucun expert n'est débordé pendant que les autres se tournent les pouces : elle reçoit les probabilités du routeur pour chacun des n tokens d'un lot et le nombre k d'experts par token, 1 par défaut, compte les affectations de chaque expert grâce à `top_k`, les divise par k × n pour obtenir les parts fᵢ, et moyenne les probabilités pour obtenir les Pᵢ. Elle renvoie le triplet formé de la perte N Σ fᵢ Pᵢ, de f et de P : 1 pour un lot équilibré, 2,8 pour l'effondrement sur l'expert 1, et 0,9125 pour le contre-exemple à deux experts, inférieur à 1 malgré une charge de `[0.75, 0.25]`.

**`gradient_biais(probas, f)`** — C'est le conseiller qui indique dans quel sens corriger les préférences du routeur : la fonction reçoit les probabilités de chaque token et les parts f, tenues fixes, et, pour chaque token, calcule d'abord la moyenne Σ fᵢ pᵢ puis ajoute à chaque coordonnée j la quantité (N / n) × pⱼ × (fⱼ − cette moyenne). Elle renvoie la liste des dérivées de la perte auxiliaire par rapport à un biais ajouté aux logits ; dans la boucle du bloc 5, un pas de gradient de taille 1 fait passer la charge de `[13, 1, 1, 1]` à `[4, 4, 4, 4]`, et la perte de 2,0464 à 1, après quoi le gradient devient nul.

**`capacite(n_tokens, n_experts, k, c)`** — Cette fonction est le régisseur qui fixe le nombre de sièges de chaque salle avant l'ouverture des portes : elle reçoit le nombre de tokens du lot, le nombre d'experts, le nombre k d'experts par token et le facteur de capacité c, puis renvoie l'entier ⌈c × k × n / N⌉, arrondi vers le haut pour ne jamais manquer d'une place par troncature. Pour 8 tokens, 4 experts et k = 1, elle donne 2, 3 et 4 places avec c = 1, 1,25 et 2 ; `repartir_avec_capacite` se sert ensuite de ce nombre pour décider quels tokens sont servis.

**`repartir_avec_capacite(choix, n_experts, cap)`** — C'est le portier d'une salle de spectacle qui applique la règle du premier arrivé, premier servi : la fonction reçoit la liste des experts choisis par chaque token, dans l'ordre du lot, le nombre d'experts et la capacité, puis, pour chaque token, note s'il reste une place chez son expert et occupe cette place. Elle renvoie une liste de booléens, vrai pour un token servi, faux pour un token abandonné qui ne garde que la connexion résiduelle ; avec le lot déséquilibré du point 6, elle abandonne 3, 2 puis 1 tokens pour les capacités 2, 3 et 4, et aucun pour le lot équilibré.

**`arrondir(v, n)`** — Ce petit utilitaire joue le greffier qui recopie les nombres au propre avant de les afficher : il reçoit une liste de flottants et un nombre n de décimales, 4 par défaut, arrondit chaque valeur et lui ajoute `0.0`, ce qui change un éventuel `-0.0` en `0.0`. Il renvoie la liste nettoyée, et `main` s'en sert à la fois pour l'affichage et pour comparer, dans les `assert`, des résultats comme la sortie `[2.0, 1.7311]` du routage top-2 aux valeurs écrites à la main.

**`main()`** — Le chef d'orchestre fait passer le token x = [1, 2] dans quatre experts linéaires et vérifie, bloc après bloc, ce que la démonstration annonce : le routage top-2, ses poids et ses 16 multiplications, l'absence de gradient du routeur en top-1 renormalisé, les comptes de paramètres du jouet, de la configuration de Mixtral et de DeepSeek-V3, puis la perte auxiliaire sur quatre lots. Il fait ensuite rééquilibrer 16 tokens tirés avec la graine 7 par descente de gradient sur un biais, calcule capacités et tokens abandonnés, montre que la sortie de x dépend de ses voisins de lot et s'assure que deux valeurs de k invalides lèvent une `ValueError` ; il ne renvoie rien et n'annonce le succès que si tous les `assert` passent.

**`sortie_k1(w00, renormaliser)`** — Cette fonction interne vit dans `main`, au bloc 2, comme un expérimentateur qui tourne d'un cran une seule molette pour voir si l'aiguille bouge : elle reçoit une nouvelle valeur pour le coefficient `W_r[0][0]` du routeur et le drapeau de renormalisation, recopie le routeur avec ce seul coefficient changé, fait passer x dans la couche en top-1 et renvoie la première coordonnée de la sortie. `main` l'appelle de part et d'autre de 1 pour une différence finie : avec renormalisation, la sortie reste à 2 et la dérivée vaut exactement 0, alors que sans renormalisation elle vaut 1,287829 et sa dérivée 0,458577, soit 2 p₁ (1 − p₁).

```python
"""Étape 36 bis — mélange d'experts (MoE) en Python pur : routage top-k, paramètres, perte auxiliaire, capacité."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- briques
def softmax(z: list[float]) -> list[float]:
    """Softmax stable (étape 2) : on retranche le maximum avant l'exponentielle."""
    m = max(z)
    e = [math.exp(v - m) for v in z]
    s = sum(e)
    return [v / s for v in e]


def matvec(W: list[list[float]], x: list[float], compteur: list[int] | None = None) -> list[float]:
    """y = W x ; compteur[0] reçoit le nombre de multiplications (une par coefficient de W)."""
    if len(W[0]) != len(x):
        raise ValueError("dimensions incompatibles")
    if compteur is not None:
        compteur[0] += len(W) * len(x)
    return [sum(w * v for w, v in zip(ligne, x)) for ligne in W]


def top_k(p: list[float], k: int) -> list[int]:
    """Indices des k plus grandes valeurs ; à égalité, le plus petit indice gagne (déterministe)."""
    if not 1 <= k <= len(p):
        raise ValueError("il faut 1 <= k <= nombre d'experts")
    return sorted(range(len(p)), key=lambda i: (-p[i], i))[:k]


def portes(logits: list[float], k: int, renormaliser: bool = True) -> dict[int, float]:
    """Poids g_i des k experts retenus : p_i / Σ_{j retenus} p_j (renormalisé), ou p_i brut (Switch, k = 1)."""
    p = softmax(logits)
    choisis = top_k(p, k)
    total = sum(p[i] for i in choisis)
    return {i: (p[i] / total if renormaliser else p[i]) for i in choisis}


def couche_moe(x, W_r, experts, k, renormaliser=True, compteur=None):
    """y = Σ_{i ∈ Top-k} g_i E_i(x) : seuls les k experts retenus sont calculés."""
    g = portes(matvec(W_r, x, compteur), k, renormaliser)
    y = [0.0] * len(experts[0])
    for i, gi in g.items():
        sortie = matvec(experts[i], x, compteur)
        y = [a + gi * b for a, b in zip(y, sortie)]
    return y, g


# ---------------------------------------------------------------- paramètres
def parametres_moe(p_partages: int, p_expert: int, n_experts: int, k: int) -> tuple[int, int]:
    """Totaux = partagés + N × expert (tout est en mémoire) ; actifs = partagés + k × expert (calculés par token)."""
    if not 1 <= k <= n_experts:
        raise ValueError("il faut 1 <= k <= N")
    return p_partages + n_experts * p_expert, p_partages + k * p_expert


def parametres_config(d: int, d_ff: int, couches: int, n_experts: int, k: int, vocab: int, d_kv: int):
    """Décompte d'un décodeur MoE : experts SwiGLU (3 matrices), attention à GQA, embeddings non liés, normes, routeur."""
    p_expert = 3 * d * d_ff * couches                       # un expert par couche, compté sur toutes les couches
    attention = (2 * d * d + 2 * d * d_kv) * couches        # W_Q et W_O : d × d ; W_K et W_V : d × d_kv
    partages = attention + 2 * vocab * d + (2 * couches + 1) * d + n_experts * d * couches
    return parametres_moe(partages, p_expert, n_experts, k)


# ---------------------------------------------------------------- équilibrage de charge
def perte_auxiliaire(probas: list[list[float]], k: int = 1) -> tuple[float, list[float], list[float]]:
    """L_aux = N Σ f_i P_i ; f_i = part des affectations reçues par i, P_i = probabilité moyenne du routeur pour i."""
    n, N = len(probas), len(probas[0])
    charges = [0] * N
    for p in probas:
        for i in top_k(p, k):
            charges[i] += 1
    f = [c / (k * n) for c in charges]
    P = [sum(p[i] for p in probas) / n for i in range(N)]
    return N * sum(fi * Pi for fi, Pi in zip(f, P)), f, P


def gradient_biais(probas: list[list[float]], f: list[float]) -> list[float]:
    """∂L_aux/∂b_j = (N/n) Σ_t p_tj (f_j − Σ_i f_i p_ti), pour un biais b ajouté aux logits ; f est tenu fixe."""
    n, N = len(probas), len(f)
    g = [0.0] * N
    for p in probas:
        moyenne_t = sum(fi * pi for fi, pi in zip(f, p))
        for j in range(N):
            g[j] += (N / n) * p[j] * (f[j] - moyenne_t)
    return g


def capacite(n_tokens: int, n_experts: int, k: int, c: float) -> int:
    """C = ⌈c · k · n / N⌉ places par expert."""
    return math.ceil(c * k * n_tokens / n_experts)


def repartir_avec_capacite(choix: list[int], n_experts: int, cap: int) -> list[bool]:
    """Premier arrivé, premier servi : un token dont l'expert est plein est abandonné (il ne garde que le résiduel)."""
    places = [0] * n_experts
    garde = []
    for e in choix:
        garde.append(places[e] < cap)
        places[e] += 1
    return garde


def arrondir(v: list[float], n: int = 4) -> list[float]:
    return [round(a, n) + 0.0 for a in v]


def main() -> None:
    x = [1.0, 2.0]
    W_r = [[1.0, 0.5], [1.0, 0.0], [0.0, 0.0], [-1.0, 0.0]]       # logits = [2, 1, 0, −1]
    experts = [[[2.0, 0.0], [0.0, 1.0]], [[0.0, 1.0], [1.0, 0.0]],
               [[1.0, 1.0], [0.0, 0.0]], [[0.0, 0.0], [1.0, 1.0]]]

    print("1. Routage top-2 d'un token, 4 experts linéaires")
    logits = matvec(W_r, x)
    p = softmax(logits)
    compteur = [0]
    y, g = couche_moe(x, W_r, experts, k=2, compteur=compteur)
    print(f"  logits = {logits} ; p = {arrondir(p)}")
    print(f"  experts retenus = {sorted(g)} ; g = {arrondir([g[i] for i in sorted(g)])} ; Σ g = {sum(g.values()):.6f}")
    print(f"  y = {arrondir(y)} ; multiplications = {compteur[0]}")
    assert logits == [2.0, 1.0, 0.0, -1.0] and sorted(g) == [0, 1]
    assert abs(sum(g.values()) - 1.0) < 1e-12
    assert abs(g[0] - 1 / (1 + math.exp(-1.0))) < 1e-12               # k = 2 : g = σ(h_a − h_b) = σ(1)
    sous_softmax = softmax([logits[0], logits[1]])                     # softmax des seuls logits retenus
    assert all(abs(g[i] - sous_softmax[n]) < 1e-12 for n, i in enumerate([0, 1]))
    assert arrondir(y) == [2.0, 1.7311] and compteur[0] == 8 + 2 * 4
    compteur_dense = [0]
    y_dense, _ = couche_moe(x, W_r, experts, k=4, compteur=compteur_dense)
    print(f"  mélange dense (k = 4) : y = {arrondir(y_dense)} ; multiplications = {compteur_dense[0]}")
    assert compteur_dense[0] == 8 + 4 * 4

    print("2. Top-1 : renormaliser donne g = 1, et le routeur ne reçoit plus de gradient")
    def sortie_k1(w00: float, renormaliser: bool) -> float:
        W = [[w00, 0.5]] + W_r[1:]
        return couche_moe(x, W, experts, k=1, renormaliser=renormaliser)[0][0]
    h = 1e-6
    for renorm in (True, False):
        derivee = (sortie_k1(1.0 + h, renorm) - sortie_k1(1.0 - h, renorm)) / (2 * h)
        nom = "renormalisé (g = 1)" if renorm else "Switch (g = p_i)  "
        print(f"  {nom} : y_1 = {sortie_k1(1.0, renorm):.6f} ; ∂y_1/∂W_r[0][0] = {derivee:.6f}")
    assert sortie_k1(1.0, True) == 2.0 and abs(sortie_k1(1.0 + h, True) - sortie_k1(1.0 - h, True)) == 0.0
    assert abs((sortie_k1(1.0 + h, False) - sortie_k1(1.0 - h, False)) / (2 * h) - 2 * p[0] * (1 - p[0])) < 1e-6

    print("3. Paramètres totaux (en mémoire) et actifs (calculés par token)")
    total, actifs = parametres_moe(p_partages=8, p_expert=4, n_experts=4, k=2)
    print(f"  exemple jouet : totaux = {total} ; actifs = {actifs}")
    assert (total, actifs) == (24, 16)
    total, actifs = parametres_config(d=4096, d_ff=14336, couches=32, n_experts=8, k=2, vocab=32000, d_kv=1024)
    print(f"  configuration publiée de Mixtral 8x7B : totaux = {total:_} ; actifs = {actifs:_}")
    assert round(total / 1e9, 1) == 46.7 and round(actifs / 1e9, 1) == 12.9    # chiffres annoncés par l'éditeur
    tot_ds, act_ds = 671e9, 37e9                                                  # DeepSeek-V3, annoncés par l'éditeur
    print(f"  DeepSeek-V3 : actifs / totaux = {act_ds / tot_ds:.4f} ; poids à 1 octet = {tot_ds / 1e9:.0f} Go ;"
          f" calcul ≈ 2 × actifs = {2 * act_ds / 1e9:.0f} GFLOP par token, {tot_ds / act_ds:.2f} fois moins qu'un dense de même taille")
    assert round(act_ds / tot_ds, 4) == 0.0551 and round(tot_ds / act_ds, 2) == 18.14

    print("4. Perte auxiliaire L_aux = N Σ f_i P_i (top-1, N = 4)")
    rotation = [[2.0, 1.0, 0.0, -1.0], [-1.0, 2.0, 1.0, 0.0], [0.0, -1.0, 2.0, 1.0], [1.0, 0.0, -1.0, 2.0]]
    equilibre = [softmax(l) for l in rotation * 2]
    L_eq, f_eq, _ = perte_auxiliaire(equilibre)
    pointus = [softmax(l) for l in ([[5.0, 0, 0, 0], [0, 0.1, 0, 0], [0, 0, 0.3, 0], [0, 0, 0, 2.0]] * 2)]
    L_pointus, f_pointus, P_pointus = perte_auxiliaire(pointus)
    effondre = [softmax([math.log(7.0), 0.0, 0.0, 0.0]) for _ in range(8)]       # p = [0.7, 0.1, 0.1, 0.1]
    L_eff, f_eff, P_eff = perte_auxiliaire(effondre)
    print(f"  charge uniforme, P uniforme : L = {L_eq:.4f} ; charge uniforme, P = {arrondir(P_pointus, 3)} : L = {L_pointus:.4f}")
    print(f"  effondrement sur l'expert 1 : f = {f_eff} ; P_1 = {P_eff[0]:.1f} ; L = {L_eff:.4f}")
    assert f_eq == [0.25] * 4 and abs(L_eq - 1.0) < 1e-12
    assert f_pointus == [0.25] * 4 and abs(L_pointus - 1.0) < 1e-12 and max(P_pointus) - min(P_pointus) > 0.2
    assert abs(L_eff - 2.8) < 1e-12
    P_test = [0.4, 0.3, 0.2, 0.1]
    assert abs(4 * sum(v * v for v in P_test) - 1.2) < 1e-12                     # si f = P : N Σ P² ≥ 1
    contre = [[0.55, 0.45]] * 3 + [[0.0, 1.0]]
    L_contre, f_contre, P_contre = perte_auxiliaire(contre)
    print(f"  contre-exemple N = 2 : f = {f_contre} ; P = {arrondir(P_contre)} ; L = {L_contre:.4f} < 1 malgré le déséquilibre")
    assert f_contre == [0.75, 0.25] and abs(L_contre - 0.9125) < 1e-12

    print("5. Le gradient de L_aux rééquilibre la charge (biais du routeur, 16 tokens)")
    random.seed(7)
    base = [[random.gauss(0.0, 1.0) + (2.0 if j == 0 else 0.0) for j in range(4)] for _ in range(16)]
    b = [0.0] * 4
    historique = []
    for pas in range(5):
        probas = [softmax([v + bj for v, bj in zip(ligne, b)]) for ligne in base]
        L, f, _ = perte_auxiliaire(probas)
        charges = [round(fi * 16) for fi in f]
        historique.append((charges, L))
        print(f"  pas {pas} : charges = {charges} ; L_aux = {L:.4f}")
        b = [bj - 1.0 * gj for bj, gj in zip(b, gradient_biais(probas, f))]   # pas η = 1, f tenu fixe
    assert historique[0][0] == [13, 1, 1, 1] and historique[-1][0] == [4, 4, 4, 4]
    assert all(historique[i + 1][1] < historique[i][1] for i in range(3))
    assert abs(historique[-1][1] - 1.0) < 1e-12 and round(historique[0][1], 4) == 2.0464
    assert all(abs(v) < 1e-12 for v in gradient_biais(probas, [0.25] * 4))      # charge uniforme : gradient nul

    print("6. Capacité C = ⌈c·k·n/N⌉ et tokens abandonnés (n = 8, N = 4, k = 1)")
    choix_desequilibre = [0, 0, 1, 0, 2, 0, 3, 0]                               # charges [5, 1, 1, 1]
    choix_equilibre = [0, 1, 2, 3, 0, 1, 2, 3]
    for c in (1.0, 1.25, 2.0):
        cap = capacite(8, 4, 1, c)
        perdus = repartir_avec_capacite(choix_desequilibre, 4, cap).count(False)
        print(f"  c = {c:<4} : C = {cap} ; abandonnés = {perdus} sur 8 (déséquilibré) ;"
              f" {repartir_avec_capacite(choix_equilibre, 4, cap).count(False)} (équilibré)")
    assert [capacite(8, 4, 1, c) for c in (1.0, 1.25, 2.0)] == [2, 3, 4]
    assert [repartir_avec_capacite(choix_desequilibre, 4, capacite(8, 4, 1, c)).count(False)
            for c in (1.0, 1.25, 2.0)] == [3, 2, 1]
    assert repartir_avec_capacite(choix_equilibre, 4, 2).count(False) == 0
    charges = [choix_desequilibre.count(e) for e in range(4)]
    print(f"  temps de la couche, experts sur 4 cartes : ∝ charge max = {max(charges)} au lieu de 2 ({max(charges) / 2} fois plus long)")
    assert max(charges) / 2 == 2.5

    print("7. Avec une capacité, la sortie d'un token dépend de ses voisins de lot")
    moe_x = couche_moe(x, W_r, experts, k=1, renormaliser=False)[0]
    sorties = []
    for lot, position_x in (([0, 1, 2, 3], 0), ([0, 0, 0, 1], 2)):            # x est le 1er, puis le 3e token de l'expert 1
        garde = repartir_avec_capacite(lot, 4, cap=2)
        bloc = [a + (b if garde[position_x] else 0.0) for a, b in zip(x, moe_x)]  # résiduel x + MoE(x), ou x seul
        sorties.append(bloc)
        print(f"  lot {lot} : x gardé = {garde[position_x]} ; sortie du bloc = {arrondir(bloc)}")
    assert sorties[0] != sorties[1] and sorties[1] == x

    print("8. Entrées invalides refusées")
    for appel in (lambda: top_k(p, 5), lambda: parametres_moe(8, 4, 4, 0)):
        try:
            appel()
        except ValueError as e:
            print(f"  ValueError : {e}")
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Routage top-2 d'un token, 4 experts linéaires
  logits = [2.0, 1.0, 0.0, -1.0] ; p = [0.6439, 0.2369, 0.0871, 0.0321]
  experts retenus = [0, 1] ; g = [0.7311, 0.2689] ; Σ g = 1.000000
  y = [2.0, 1.7311] ; multiplications = 16
…
  renormalisé (g = 1) : y_1 = 2.000000 ; ∂y_1/∂W_r[0][0] = 0.000000
  Switch (g = p_i)   : y_1 = 1.287829 ; ∂y_1/∂W_r[0][0] = 0.458577
…
  configuration publiée de Mixtral 8x7B : totaux = 46_702_792_704 ; actifs = 12_879_925_248
…
  contre-exemple N = 2 : f = [0.75, 0.25] ; P = [0.4125, 0.5875] ; L = 0.9125 < 1 malgré le déséquilibre
…
  pas 0 : charges = [13, 1, 1, 1] ; L_aux = 2.0464
  pas 4 : charges = [4, 4, 4, 4] ; L_aux = 1.0000
…
  c = 1.0  : C = 2 ; abandonnés = 3 sur 8 (déséquilibré) ; 0 (équilibré)
…
  lot [0, 0, 0, 1] : x gardé = False ; sortie du bloc = [1.0, 2.0]
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un MoE n'est ni magique ni opaque. C'est une softmax, un tri, une moyenne pondérée et un compteur de places. Le nombre de paramètres actifs fixe le calcul, le nombre total fixe la mémoire, et l'équilibrage se lit sur la charge de chaque expert.

### La version PyTorch (extrait)

La même couche avec des tenseurs, pour un lot de tokens. Elle ne gère pas la capacité : chaque expert reçoit tous les tokens qui l'ont choisi.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`CoucheMoE.__init__(d_model, d_ff, n_experts, k)`** — Le constructeur ouvre le cabinet d'experts avant l'arrivée du premier dossier : il reçoit la largeur `d_model` des tokens, la largeur intérieure `d_ff` de chaque expert, le nombre d'experts et le nombre k d'experts consultés par token, garde k, puis crée un routeur linéaire sans biais qui transforme un token en `n_experts` logits. Il construit enfin la liste des experts, chacun formé d'une couche linéaire de `d_model` vers `d_ff`, d'une activation SiLU et d'une couche linéaire de retour vers `d_model`, toutes sans biais ; il ne renvoie rien, mais tout ce qu'il crée est enregistré comme paramètres de la couche.

**`CoucheMoE.forward(x)`** — Cette méthode fait la tournée du cabinet pour tout un lot de tokens à la fois : elle reçoit le tenseur x de forme (n_tokens, d_model), calcule les logits du routeur, garde pour chaque token les k plus grands avec `torch.topk` et leur applique une softmax, ce qui donne exactement les poids renormalisés de `portes` dans le programme en Python pur. Elle part ensuite d'une sortie nulle et, pour chaque expert, retrouve par `torch.where` les tokens qui l'ont choisi et le rang de ce choix, ne fait calculer l'expert que sur ces tokens et ajoute sa sortie pondérée par la bonne porte ; elle renvoie le tenseur y, de même forme que x, sans gérer de capacité.

```python
# [extrait] — couche MoE en PyTorch, non exécutée par le harnais (PyTorch n'est pas dans la bibliothèque standard)
import torch
import torch.nn as nn
import torch.nn.functional as F


class CoucheMoE(nn.Module):
    def __init__(self, d_model: int, d_ff: int, n_experts: int, k: int):
        super().__init__()
        self.k = k
        self.routeur = nn.Linear(d_model, n_experts, bias=False)
        self.experts = nn.ModuleList(
            nn.Sequential(nn.Linear(d_model, d_ff, bias=False), nn.SiLU(), nn.Linear(d_ff, d_model, bias=False))
            for _ in range(n_experts))

    def forward(self, x):                              # x : (n_tokens, d_model)
        logits = self.routeur(x)                       # (n_tokens, n_experts)
        valeurs, indices = torch.topk(logits, self.k, dim=-1)
        portes = F.softmax(valeurs, dim=-1)            # softmax des k logits retenus = renormalisation (point 1)
        y = torch.zeros_like(x)
        for e, expert in enumerate(self.experts):
            lignes, rang = torch.where(indices == e)   # tokens qui ont choisi l'expert e, et à quel rang
            if lignes.numel():
                y[lignes] += portes[lignes, rang, None] * expert(x[lignes])
        return y
```

`torch.topk(logits, self.k, dim=-1)` sélectionne sur les logits, sans softmax préalable : le point 1 montre que l'ordre est le même. `F.softmax(valeurs, dim=-1)` sur les k logits retenus donne exactement les poids renormalisés. `torch.where(indices == e)` renvoie, pour l'expert e, les numéros des tokens qui l'ont choisi et la position de ce choix parmi leurs k, ce qui permet de lire la bonne porte. La boucle ne calcule chaque expert que sur ses tokens : c'est l'économie du MoE. Les vrais moteurs d'inférence remplacent cette boucle par des noyaux groupés, mais le calcul est le même.

## Squelette algorithmique

Trois algorithmes résument le fichier. Le premier calcule la sortie d'une couche MoE pour un token : en entrée, le vecteur du token, la matrice du routeur, les experts et k ; en sortie, le vecteur de sortie. Le deuxième répartit un lot de tokens entre les experts en respectant leur capacité. Le troisième mesure la perte auxiliaire d'un lot et son gradient par rapport au biais du routeur.

```text
ALGORITHME CoucheMoE
ENTRÉES : token x (d nombres), routeur W_r (N × d), experts E₁ … E_N, k avec 1 ≤ k ≤ N
SORTIE  : y (d nombres)

  SI k < 1 OU k > N ALORS ERREUR « k invalide » FIN SI
  h ← W_r × x                                     (N logits)
  p ← softmax(h)
  T ← indices des k plus grandes valeurs de p      (égalité : plus petit indice)
  total ← Σ (i ∈ T) pᵢ
  y ← vecteur nul
  POUR CHAQUE i DANS T FAIRE
      gᵢ ← pᵢ / total                             (pour k = 1, Switch garde gᵢ ← pᵢ)
      y ← y + gᵢ × Eᵢ(x)                          (les experts hors de T ne calculent rien)
  FIN POUR
  RETOURNER y

ALGORITHME RépartitionAvecCapacité
ENTRÉES : choix (l'expert de chaque token, dans l'ordre du lot), N, n, k, facteur c
SORTIE  : pour chaque token : gardé ou abandonné

  C ← ⌈c × k × n / N⌉
  places ← N compteurs à 0
  POUR CHAQUE token t DANS l'ordre du lot FAIRE
      e ← choix(t)
      SI places(e) < C ALORS gardé(t) ← vrai SINON gardé(t) ← faux FIN SI
      places(e) ← places(e) + 1
  FIN POUR
  RETOURNER gardé                                 (un token abandonné ne garde que le résiduel x)

ALGORITHME PerteAuxiliaire
ENTRÉES : probabilités p(t) du routeur pour les n tokens du lot, k
SORTIE  : L_aux et son gradient par rapport au biais b

  POUR i DE 1 À N FAIRE
      fᵢ ← (nombre de tokens t tels que i ∈ Top_k(p(t))) / (k × n)
      Pᵢ ← (Σ (t) pᵢ(t)) / n
  FIN POUR
  L_aux ← N × Σ (i) fᵢ × Pᵢ
  POUR j DE 1 À N FAIRE
      gradⱼ ← (N / n) × Σ (t) pⱼ(t) × (fⱼ − Σ (i) fᵢ × pᵢ(t))      (f tenu fixe)
  FIN POUR
  RETOURNER L_aux, grad
```

**Complexité :** pour un token, le routeur coûte O(N d), le tri des N probabilités O(N log N) (O(N) suffit pour une sélection des k meilleurs), et les experts retenus O(k × coût d'un expert) ; avec un expert feed-forward de largeur intermédiaire d_ff, cela fait O(N d + k d d_ff), et c'est le second terme qui domine. La mémoire des poids est O(N d + N d d_ff), proportionnelle au nombre total d'experts. La répartition avec capacité est O(n) en temps et O(N) en mémoire. La perte auxiliaire et son gradient coûtent O(n N), plus O(n N log N) pour les choix top-k : c'est négligeable devant les experts eux-mêmes.

**Du squelette au code :** dans CoucheMoE, la garde sur k est celle de `top_k`, les lignes « h », « p » et « T » sont `matvec(W_r, x)`, `softmax` et `top_k`, le calcul des gᵢ est `portes(logits, k, renormaliser)`, et la boucle sur T est la boucle `for i, gi in g.items()` de `couche_moe`. RépartitionAvecCapacité correspond à `capacite`, pour C, puis à `repartir_avec_capacite`, dont le test `places[e] < cap` est la ligne « SI places(e) < C ». PerteAuxiliaire correspond à `perte_auxiliaire`, qui renvoie L_aux, f et P, et à `gradient_biais`, dont la variable `moyenne_t` est la somme Σ fᵢ pᵢ(t).

## Cas d'usage réels aux Émirats

Les tailles de modèles citées reprennent les configurations publiées et les chiffres annoncés par les éditeurs ; les tailles de cartes, les volumes et les seuils sont illustratifs. On refait toujours le calcul avec le fichier de configuration du modèle retenu.

### Banque — la mémoire se calcule sur les paramètres totaux

Une banque de détail de Dubaï veut héberger dans son propre centre de données un modèle ouvert pour ses assistants de conformité et de KYC, afin que les relevés et les pièces d'identité de ses clients ne quittent pas son infrastructure. Le modèle envisagé est un MoE de la taille de Mixtral 8x7B : 46,7 milliards de paramètres au total, 12,9 milliards actifs par token. L'équipe infrastructure avait d'abord dimensionné le serveur sur les paramètres actifs, comme pour un modèle dense de 13 milliards, soit environ 26 Go de poids en 16 bits. C'est faux pour la mémoire : les huit experts doivent être chargés, ce qui fait 46,7 × 2 = 93,4 Go en 16 bits, plus que la mémoire d'une carte de 80 Go, avant même le cache clé-valeur des sessions (étape 34). Le calcul, lui, se fait bien sur les actifs, environ 2 × 12,9 = 25,8 milliards d'opérations par token, ce qui donne un débit proche de celui d'un modèle dense de 13 milliards sur le même matériel. L'équipe retient donc deux cartes, ou une quantification en 8 bits qui ramène les poids à 46,7 Go (étape 73 bis), et refait l'évaluation de l'extraction KYC après quantification. Sans ce calcul, le modèle ne démarre pas en recette, ou il démarre sans place pour le cache et refuse les sessions dès la première heure. L'indicateur suivi est la marge de mémoire au pic de charge, avec le taux d'extraction correcte des pièces KYC.

### Secteur public — le routeur du MoE n'est pas le routeur de l'agent

Une entité de services publics en ligne accessible par UAE Pass répond en arabe et en anglais. Un prototype misait sur l'idée qu'un MoE contiendrait « un expert arabe » et « un expert anglais », et qu'il suffirait donc d'un seul modèle pour bien servir les deux langues. Ce fichier montre pourquoi c'est une hypothèse fragile : le routeur choisit des experts par token et par couche, en fonction de ce qui fait baisser la perte d'entraînement, et rien dans la formule ne lui demande de séparer les langues. L'analyse publiée avec Mixtral rapporte d'ailleurs ne pas avoir trouvé de spécialisation nette des experts par thème, mais plutôt des régularités liées à la syntaxe. L'équipe garde donc le choix de langue au niveau de l'agent : son propre routeur détecte la langue de la requête entière et choisit l'adaptateur LoRA adapté (étape 73), puis l'évaluation mesure la justesse séparément en arabe, en anglais et en dialecte. Sans cette séparation, une baisse de qualité en arabe passerait inaperçue dans une moyenne dominée par l'anglais. L'indicateur suivi est le taux de demandes résolues sans transfert, par langue.

### Crypto — une réponse qui ne se régénère pas à l'identique

Une plateforme d'actifs virtuels agréée par la VARA fait rédiger par un agent la justification de chaque alerte de transaction suspecte, à partir d'un modèle MoE servi en lots avec d'autres requêtes. Lors d'un contrôle interne, un auditeur relance la génération d'une justification vieille de trois semaines, avec le même prompt, le même modèle et une température nulle, et obtient un texte différent. Le point 7 explique un mécanisme possible : avec une capacité, un token abandonné dans un lot chargé ne reçoit pas la contribution des experts, et la composition du lot dépend des autres requêtes du moment, ce que personne ne maîtrise. Le même token donne [2,2878 ; 3,2878] dans un lot et [1 ; 2] dans un autre. La plateforme ne cherche donc jamais à « reproduire » une décision passée : elle conserve la justification exacte qui a été produite, avec la version du modèle, le prompt et les données consultées, dans un journal horodaté et non modifiable. Sans cette conservation, l'équipe de conformité ne pourrait pas démontrer ce que l'agent a écrit au moment de l'alerte. L'indicateur suivi est la part des alertes dont la justification d'origine est retrouvée dans le journal, avec un objectif de 100 %.

### Assurance — un expert surchargé ralentit toute la couche

Un assureur auto et santé héberge un modèle MoE dont les experts sont répartis sur quatre cartes graphiques, une technique appelée parallélisme d'experts, pour traiter la nuit, en lots, les déclarations de sinistre de la journée. Les temps de traitement ont doublé après l'ajout d'un nouveau type de dossier, très homogène, sans que le volume total ait beaucoup changé. Le point 6 donne l'explication : la couche attend la carte la plus chargée, et une charge [5, 1, 1, 1] au lieu de [2, 2, 2, 2] rend la couche 2,5 fois plus lente, tout en abandonnant 3 tokens sur 8 si la capacité vaut 2. L'équipe ajoute à son tableau de bord la charge de chaque expert, couche par couche, et regroupe les dossiers de types différents dans les mêmes lots pour diluer le déséquilibre. Elle compare aussi la justesse du tri des sinistres sur les lots homogènes et mélangés, puisque des tokens abandonnés peuvent dégrader la sortie. Sans cette mesure, l'équipe aurait acheté une cinquième carte sans rien régler, le goulot restant sur l'expert surchargé (étape 69). L'indicateur suivi est le rapport entre la charge maximale et la charge moyenne des experts, par lot.

### BTP — un MoE ne tient pas sur une tablette

Un groupe de construction qui mène de grands chantiers à Dubaï veut classer hors ligne, sur des tablettes de chantier, les bons de livraison et les comptes rendus de réunion. Un fournisseur propose un modèle MoE « aussi rapide qu'un petit modèle », parce que ses paramètres actifs sont peu nombreux. C'est vrai pour le calcul, faux pour la mémoire : même quantifié en 4 bits, un modèle de 46,7 milliards de paramètres demande environ 23,4 Go pour ses seuls poids, bien au-delà de la mémoire d'une tablette, alors qu'un modèle dense de 3 milliards de paramètres en 4 bits en demande 1,5. L'équipe retient donc un petit modèle dense pour les tablettes, et réserve le MoE au serveur du siège, où la mémoire abonde et où son calcul réduit sert vraiment. Le critère de choix est écrit dans le cahier des charges : la mémoire disponible borne les paramètres totaux, la latence visée borne les paramètres actifs. Sans cette distinction, le déploiement échoue à l'installation sur le premier appareil. L'indicateur suivi est la justesse du classement des documents, mesurée sur le terrain, avec le temps de réponse sur tablette.

### RH — un fine-tuning qui fait s'effondrer le routage

Un cabinet RH multi-émirats spécialise un modèle MoE ouvert sur ses lettres d'offre, ses avenants et ses réponses aux questions de visa et de WPS. Le jeu d'entraînement est étroit : quelques milliers de documents au vocabulaire très répétitif. Dans une première version, l'équipe a retiré la perte auxiliaire, jugée inutile pour un simple fine-tuning. Le risque que décrit l'effet « sans équilibrage, le routage s'effondre » se mesure alors directement : on suit la charge des experts sur un lot de validation, et l'on vérifie qu'elle ne converge pas vers un ou deux experts, ce qui augmenterait les tokens abandonnés et ferait perdre au modèle une partie de ce qu'il savait faire hors du domaine RH. L'équipe garde donc la perte auxiliaire pendant le fine-tuning, avec le poids d'origine, et ajoute au rapport d'entraînement la charge maximale par couche. Les règles chiffrées, comme l'indemnité de fin de service, restent calculées par l'outil `gratuite_fin_de_service` et jamais apprises par le modèle. L'indicateur suivi est la charge maximale des experts sur le lot de validation, avec le taux de lettres validées par le juriste sans correction.

## Pièges et limites

- **Confondre paramètres totaux et actifs.** La mémoire suit Θ_tot, le calcul suit Θ_act ; « 47 milliards dont 13 actifs » se charge comme 47 et calcule comme 13.
- **Renormaliser avec k = 1.** Le poids vaut alors toujours 1 et le routeur ne reçoit plus de gradient de la tâche (point 3) ; le Switch Transformer garde pᵢ.
- **Lire la perte auxiliaire comme un indicateur d'équilibre.** Elle peut descendre sous 1 avec une charge déséquilibrée (contre-exemple à 0,9125) ; on surveille la charge de chaque expert.
- **Croire que chaque expert est spécialiste d'un domaine.** Rien dans la formule ne l'impose ; le choix d'un outil, d'une langue ou d'un adaptateur se fait au niveau de l'agent.
- **Exiger la reproductibilité d'un modèle servi en lots.** Avec une capacité, la sortie dépend des autres requêtes du lot ; on conserve les réponses produites au lieu de compter sur leur régénération.

### Exercice feuille blanche

1. Sans regarder le code, écrire `portes(logits, k)` et `couche_moe`, puis retrouver g = [0,7311 ; 0,2689] et y = [2 ; 1,7311] pour l'exemple.
2. Prédire, puis vérifier : avec des logits [3, 1, 0, −1] et k = 2, que vaut le poids du premier expert ? (Réponse : σ(3 − 1) = σ(2) ≈ 0,8808, puisque seul l'écart des deux logits retenus compte.)
3. Trouver le bug : dans `portes`, `total = sum(p)` à la place de `total = sum(p[i] for i in choisis)`. Que vaut Σ g pour l'exemple, et quelle vérification du programme échoue ? (Réponse : total vaut 1, donc g = [0,6439 ; 0,2369] et Σ g = 0,8808 ; l'`assert` sur Σ g = 1 échoue, et y est rétréci vers zéro.)

## Pour aller plus loin

Plusieurs variantes modifient le routage. Les **experts partagés** sont calculés pour tous les tokens en plus des experts routés : selon son rapport technique, DeepSeek-V3 combine dans chaque couche MoE un expert partagé et 256 experts routés, dont 8 sont activés par token, et remplace la perte auxiliaire par un biais ajouté aux scores du routeur, ajusté selon la charge observée, l'idée du point 5 sans gradient. La **z-loss** du routeur pénalise les logits trop grands pour stabiliser l'entraînement. Le routage par **choix des experts** inverse le problème : chaque expert choisit ses tokens, ce qui équilibre la charge par construction mais peut laisser des tokens sans expert. Les **Soft MoE** remplacent le choix discret par des mélanges pondérés de tokens.

> Étape 36 bis du parcours · Prérequis : [Normalisation de couche](<36-Normalisation-de-Couche.md>) · Suite : [Encodeur, attention croisée et embeddings](<36c-Encodeur-Attention-Croisee-et-Embeddings.md>)
