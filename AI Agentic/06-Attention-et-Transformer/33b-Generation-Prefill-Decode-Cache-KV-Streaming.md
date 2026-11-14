# Étape 33 bis — Transformer — Génération : prefill, décodage, cache KV, TTFT et streaming

**Dossier :** 06-Attention-et-Transformer

> Étape 33 bis du parcours · Prérequis : [Transformer et attention](<33-Transformer-et-Attention-Deroule-Numerique.md>) · Suite : [Attention multi-têtes](<34-Attention-Multi-Tetes.md>)

## Définition

Un LLM génère sa réponse **un token à la fois** : il calcule la distribution du prochain token (étape 2), en choisit un, l'ajoute à la séquence et recommence. Cette génération autorégressive se fait en deux phases. Le **prefill** traite d'un coup toutes les positions du prompt : il calcule, dans chaque couche, les clés K et les valeurs V de tous les tokens en parallèle, et il produit les logits du premier token de la réponse. Le **décodage** traite ensuite chaque nouveau token seul : il calcule sa requête, sa clé et sa valeur, puis relit les clés et les valeurs des tokens précédents dans un **cache KV** au lieu de les recalculer. Le prefill est limité par la puissance de calcul, le décodage par la vitesse de lecture de la mémoire. Trois mesures décrivent ce que l'utilisateur ressent : le **TTFT** (time to first token, délai avant le premier token), la **latence inter-tokens** et le nombre de **tokens par seconde** ; le **streaming** envoie chaque token dès qu'il est prêt.

## Rôle dans un agent

Chaque tour de la boucle percevoir → décider → agir → observer contient un appel au modèle, et la durée de l'étape « décider » se découpe exactement comme dans ce fichier : un prefill sur tout le contexte (prompt système, outils, historique, résultats d'outils), puis un pas de décodage par token de sortie. Un agent de quinze tours paie quinze fois ce délai. Le développeur agit sur les deux termes : le prefill se raccourcit avec un **cache de préfixe** (étape 72), qui n'est rien d'autre qu'un cache KV conservé d'une requête à l'autre, et le décodage avec des réponses plus courtes et structurées. Le streaming, lui, sert l'interface : il montre le texte plus tôt, mais un appel d'outil ne peut s'exécuter que lorsque son JSON est complet, si bien que l'étape « agir » ne commence pas plus tôt. Enfin, quand le modèle est hébergé sur ses propres serveurs (un modèle ouvert comme Jais ou Falcon), la taille du cache KV fixe le nombre de sessions simultanées par carte graphique : c'est un calcul de dimensionnement, pas un détail d'implémentation.

## Équation complète

Prefill, pour une couche l, sur les P positions du prompt à la fois (H est la matrice des états, une ligne par position) :

$$
K^{(l)} = H^{(l)} W_K^{(l)}, \qquad V^{(l)} = H^{(l)} W_V^{(l)}
$$

Décodage de la position n : on ajoute une ligne au cache, puis une seule requête le relit :

$$
K_{1:n} = \begin{bmatrix} K_{1:n-1} \\ h_n W_K \end{bmatrix}, \qquad V_{1:n} = \begin{bmatrix} V_{1:n-1} \\ h_n W_V \end{bmatrix}
$$

$$
o_n = \text{softmax}\!\left( \frac{q_n K_{1:n}^\top}{\sqrt{d}} \right) V_{1:n}, \qquad q_n = h_n W_Q
$$

Multiplications pour produire un token quand la séquence compte n positions, avec le cache puis par recalcul complet :

$$
C_{\text{cache}}(n) = L \bigl( c_{lin} + 2\, n\, d \bigr)
$$

$$
C_{\text{recalcul}}(n) = L \bigl( n\, c_{lin} + d\, n (n+1) \bigr)
$$

Totaux de l'attention (A) et des couches linéaires (Λ) pour P tokens de prompt et G tokens générés :

$$
A_{\text{sans}} = L\, d \sum_{n=P}^{P+G-1} n(n+1), \qquad A_{\text{avec}} = L\, d \left( P(P+1) + 2 \sum_{n=P+1}^{P+G-1} n \right)
$$

$$
\Lambda_{\text{sans}} = L\, c_{lin} \sum_{n=P}^{P+G-1} n, \qquad \Lambda_{\text{avec}} = L\, c_{lin}\, (P + G - 1)
$$

Les deux sommes ont une forme fermée :

$$
\sum_{n=a}^{b} n = \frac{(a+b)(b-a+1)}{2}, \qquad \sum_{n=a}^{b} n(n+1) = F(b) - F(a-1), \quad F(m) = \frac{m(m+1)(m+2)}{3}
$$

Mémoire du cache KV pour n tokens :

$$
M_{KV} = 2 \times L \times h_{kv} \times d_h \times n \times b
$$

Temps d'une passe, sur le modèle du « toit » (roofline) : la passe dure le plus long du calcul et de la lecture mémoire :

$$
t_{\text{prefill}}(P) = \max\!\left( \frac{2\, N_p\, P}{F_c},\; \frac{b\, N_p}{F_m} \right)
$$

$$
t_{\text{decode}}(n) = \max\!\left( \frac{2\, N_p}{F_c},\; \frac{b\, N_p + m_{kv}\, n}{F_m} \right)
$$

Délais vus par l'utilisateur :

$$
\text{TTFT} = t_{\text{réseau}} + t_{\text{attente}} + t_{\text{prefill}}(P)
$$

$$
T_{\text{total}} = \text{TTFT} + \sum_{i=1}^{G-1} t_{\text{decode}}(P + i)
$$

$$
\text{ITL} = \frac{T_{\text{total}} - \text{TTFT}}{G - 1}, \qquad \text{débit d'une séquence} = \frac{1}{\text{ITL}}
$$

## Décryptage des symboles

$$
P
$$

**Sens :** nombre de tokens du prompt, traités par le prefill · **Type / plage :** entier ≥ 1 · **Variable Python :** `P`, `len(prompt)`

$$
G
$$

**Sens :** nombre de tokens générés · **Type / plage :** entier ≥ 1 · **Variable Python :** `G`

$$
n
$$

**Sens :** longueur courante de la séquence, nouveau token compris · **Type / plage :** entier, de P à P + G − 1 · **Variable Python :** `n`, `len(K)`

$$
L
$$

**Sens :** nombre de couches du Transformer · **Type / plage :** entier ≥ 1 · **Variable Python :** `COUCHES`, `couches`

$$
d
$$

**Sens :** largeur du modèle ; c'est aussi la somme des largeurs des têtes, donc le coût de l'attention par paire de positions · **Type / plage :** entier ≥ 1 · **Variable Python :** `D`

$$
c_{lin}
$$

**Sens :** multiplications des couches linéaires pour une position et une couche : 4d² pour les quatre projections de l'attention, environ 12d² avec le bloc feed-forward · **Type / plage :** entier · **Variable Python :** `c_lin`

$$
h_n,\quad q_n
$$

**Sens :** état de la position n à l'entrée d'une couche, et la requête qui en est tirée · **Type / plage :** vecteurs de d nombres · **Variable Python :** `h`, `q` dans `couche_position`

$$
K_{1:n},\quad V_{1:n}
$$

**Sens :** les clés et les valeurs des positions 1 à n d'une couche : le contenu du cache · **Type / plage :** n vecteurs de d nombres chacun · **Variable Python :** `K`, `V`, éléments de `cache`

$$
h_{kv},\quad d_h
$$

**Sens :** nombre de têtes de clés-valeurs et largeur d'une tête (étape 34, variante GQA) · **Type / plage :** entiers ≥ 1 · **Variable Python :** `tetes_kv`, `d_tete`

$$
b
$$

**Sens :** octets par nombre stocké : 2 en fp16, pour les poids comme pour le cache · **Type / plage :** entier · **Variable Python :** `octets`, `octets_param`

$$
M_{KV}
$$

**Sens :** mémoire occupée par le cache KV d'une séquence · **Type / plage :** octets · **Variable Python :** `memoire_cache_kv(...)`

$$
N_p
$$

**Sens :** nombre de paramètres du modèle · **Type / plage :** entier · **Variable Python :** `service.params`

$$
F_c,\quad F_m
$$

**Sens :** débit de calcul de l'accélérateur (opérations par seconde) et bande passante mémoire (octets lus par seconde) · **Type / plage :** réels > 0 · **Variable Python :** `service.flops`, `service.bande`

$$
m_{kv}
$$

**Sens :** octets du cache par token, soit 2 L h_kv d_h b · **Type / plage :** entier · **Variable Python :** `service.kv_par_token`

$$
\text{TTFT},\quad \text{ITL},\quad T_{\text{total}}
$$

**Sens :** délai avant le premier token, latence moyenne entre deux tokens, instant du dernier token · **Type / plage :** secondes · **Variable Python :** `ttft`, `itl`, `fin_flux`

Dans ce fichier, P est la longueur du prompt et non la matrice des positions de l'étape 35 ; la variable Python `modele.P` désigne, elle, les embeddings de position du modèle jouet.

## Démonstration

### 1. Le cache est exact parce que le masque est causal

Notons hᵢ⁽ˡ⁾ l'état de la position i à l'entrée de la couche l. Avec le masque causal (étape 33), hᵢ⁽ˡ⁾ ne dépend que des tokens t₁, …, tᵢ. On le montre par récurrence sur l. À la première couche, hᵢ⁽¹⁾ est la somme de l'embedding du token tᵢ et de l'embedding de la position i : il ne dépend que de tᵢ. Supposons la propriété vraie à la couche l. La couche calcule

$$
h_i^{(l+1)} = h_i^{(l)} + \Bigl( \sum_{j \le i} a_{ij}\, v_j^{(l)} \Bigr) W_O
$$

où les poids aᵢⱼ sont la softmax des scores qᵢ · kⱼ / √d pour j ≤ i. Toutes les quantités de cette formule, qᵢ, kⱼ et vⱼ, sont des fonctions de hⱼ⁽ˡ⁾ pour j ≤ i, qui ne dépendent que de t₁, …, tⱼ par hypothèse, donc de t₁, …, tᵢ. La propriété passe à la couche l + 1.

Conséquence : ajouter le token tₙ₊₁ ne change aucun hᵢ⁽ˡ⁾ pour i ≤ n, donc aucune clé kᵢ⁽ˡ⁾ = hᵢ⁽ˡ⁾ W_K ni aucune valeur. Les garder en mémoire au lieu de les recalculer ne change pas le résultat. Dans le programme, le décodage avec cache appelle les mêmes fonctions sur les mêmes nombres, dans le même ordre, que le recalcul complet : les logits sont égaux au bit près, ce que vérifie un `assert` avec `==`.

Sans masque causal, l'argument tombe. Dans une couche bidirectionnelle, hᵢ⁽²⁾ dépend aussi des tokens qui suivent i : quand tₙ₊₁ arrive, les clés et les valeurs de la deuxième couche calculées avant lui sont périmées. Le programme le mesure sur deux couches : entre le recalcul complet et le décodage qui réutilise ce cache périmé, les logits diffèrent jusqu'à 0,1262. La première couche, elle, reste juste, puisque ses clés ne dépendent que des embeddings : il faut au moins deux couches pour voir l'erreur, d'où les deux couches du modèle jouet. C'est la raison pour laquelle un encodeur sans masque, comme BERT, ne génère pas de texte token par token avec un cache.

### 2. Le coût d'un pas : linéaire en n avec le cache, quadratique sans

Avec le cache, produire le token suivant quand la séquence compte n positions demande, dans chaque couche, les projections de la seule position nouvelle (c_lin multiplications) puis une requête contre n clés : n produits scalaires de d multiplications pour les scores, et n × d multiplications pour la moyenne pondérée des valeurs, soit 2nd. D'où C_cache(n) = L (c_lin + 2nd) : la part attention est en O(n d).

Sans le cache, il faut refaire la passe complète sur les n positions. Les projections coûtent n c_lin par couche, et la position i, qui voit i positions grâce au masque, coûte 2id en attention, d'où

$$
\sum_{i=1}^{n} 2\, i\, d = d\, n(n+1)
$$

par couche, parce que 1 + 2 + … + n = n(n + 1)/2. La part attention est en O(n² d), et les projections sont multipliées par n.

### 3. Le coût total : une somme arithmétique contre une somme de produits

Pour générer G tokens, le chemin avec cache fait un prefill sur P positions, qui produit le premier token, puis G − 1 pas de décodage, aux longueurs n = P + 1, …, P + G − 1 : l'attention totale vaut L d (P(P + 1) + 2 Σ n), une **somme arithmétique** ; les projections traitent chacune des P + G − 1 positions une seule fois. Le chemin sans cache refait G passes complètes, aux longueurs n = P, …, P + G − 1 : l'attention totale vaut L d Σ n(n + 1), et les projections L c_lin Σ n.

La forme fermée de Σ n(n + 1) vient d'une somme télescopique. Pour tout n,

$$
n(n+1) = \frac{n(n+1)(n+2) - (n-1)n(n+1)}{3}
$$

parce que le numérateur vaut n(n + 1) × ((n + 2) − (n − 1)) = 3 n(n + 1). En sommant de n = 1 à m, les termes intermédiaires s'annulent deux à deux et il reste F(m) = m(m + 1)(m + 2)/3 ; la somme de a à b vaut F(b) − F(a − 1). Elle croît comme b³/3 : sans cache, le coût total de l'attention est cubique en la longueur finale.

À l'échelle d'un modèle de largeur 4 096 à 32 couches, avec c_lin = 12 × 4 096², pour P = 2 000 et G = 500, le rapport des couches linéaires vaut Σ n / (P + G − 1) = 1 124 750 / 2 499 ≈ 450,1, et celui de l'attention 406,8. Le produit 32 × 12 × 4 096² ≈ 6,4 milliards est l'ordre de grandeur des paramètres d'un modèle de 7 milliards : chaque token coûte environ une multiplication par paramètre, ce qu'on retrouve au point 5.

### 4. La mémoire du cache

Pour chaque couche, chaque tête de clés-valeurs et chaque token gardé, le cache stocke une clé et une valeur de d_h nombres chacune : 2 L h_kv d_h nombres par token, de b octets. Le modèle jouet (2 couches, une tête de largeur 4, 9 positions, des flottants de 8 octets) stocke 2 × 2 × 1 × 4 × 9 = 144 nombres, soit 1 152 octets, ce que le programme compte un par un. Pour 32 couches, des têtes de 128 et 8 000 tokens en fp16, on retrouve les nombres de l'étape 34 : 4,19 Go avec 32 têtes de clés-valeurs, 1,05 Go avec 8 têtes partagées (GQA), soit 128 Kio par token. Dans 40 Go de mémoire libre (valeur illustrative), cela fait 9 sessions de 8 000 tokens dans le premier cas et 38 dans le second. La mémoire est linéaire en n : une conversation deux fois plus longue occupe deux fois plus de cache.

### 5. Le prefill est limité par le calcul, le décodage par la mémoire

Chaque passe doit lire tous les poids en mémoire au moins une fois, soit b N_p octets. Le prefill de P tokens fait environ 2 N_p P opérations sur ces poids (une multiplication et une addition par paramètre et par token) : il fait P opérations par octet lu quand b = 2. Le décodage fait 2 N_p opérations pour b N_p + m_kv n octets lus : environ une opération par octet. Un accélérateur exécute F_c opérations et lit F_m octets par seconde ; une passe dure donc au moins le plus long des deux temps, d'où les formules en max. Le prefill est limité par le calcul dès que 2 N_p P / F_c ≥ b N_p / F_m, c'est-à-dire P ≥ (b/2)(F_c / F_m) : avec les valeurs illustratives du programme (F_c = 10¹⁵ opérations par seconde, F_m = 3 × 10¹² octets par seconde), au-delà de 333 tokens.

Pour un modèle de 7 milliards de paramètres en fp16, le prefill de 2 000 tokens demande 28 ms de calcul pour 4,67 ms de lecture des poids : il est limité par le calcul. Un pas de décodage à n = 2 001 dure 4,754 ms, alors que son calcul seul n'en demanderait que 0,014 : il passe plus de 300 fois plus de temps à lire qu'à calculer. La vitesse d'une séquence est donc plafonnée par F_m / (b N_p), environ 214 tokens par seconde ici. C'est ce qui rend utiles le traitement par lots (lire les poids une fois pour plusieurs séquences, étape 72 bis) et le décodage spéculatif (vérifier plusieurs tokens en une passe, étape 72 ter). Le modèle de temps néglige les opérations de l'attention elle-même pendant le prefill : avec les comptes de ce fichier, elles valent environ P / (12 d) des opérations linéaires, soit 4 % pour P = 2 000 et d = 4 096.

### 6. TTFT, latence inter-tokens, débit

Le premier token sort à la fin du prefill, dont la dernière ligne donne ses logits ; le client le reçoit après l'attente éventuelle dans la file du serveur (étapes 69 à 71) et le trajet réseau : TTFT = t_réseau + t_attente + t_prefill(P). Certains moteurs traitent le prompt sans son dernier token, puis ce dernier token dans un premier pas de décodage ; on lit alors « TTFT = prefill + premier pas de décodage », ce qui revient au même à un token près. Chaque token suivant coûte un pas de décodage : la latence inter-tokens moyenne est (T_total − TTFT)/(G − 1), et son inverse est le débit d'une séquence.

Avec 40 ms de réseau, pas d'attente et P = 2 000 : TTFT = 40 + 28 = 68 ms. Pour G = 300 tokens, la latence inter-tokens moyenne vaut 4,761 ms (210 tokens par seconde) et le dernier token arrive à 1,4914 s ; pour une réponse courte de 60 tokens, à 0,3486 s. Si 1 800 des 2 000 tokens du prompt sont déjà dans un cache de préfixe, le prefill ne traite que 200 tokens : max(2,8 ms ; 4,745 ms) = 4,745 ms, et le TTFT tombe à 44,7 ms. Le prefill devient alors limité par la lecture des poids : le cache de préfixe a retiré presque tout le calcul.

### 7. Le streaming réduit la latence perçue, pas le temps total

Le serveur produit le token i à l'instant τᵢ, que le client affiche ou non la réponse au fil de l'eau : la génération est la même dans les deux cas. Sans streaming, le client reçoit tout à τ_G = T_total, et le premier texte visible apparaît à T_total. Avec streaming, il reçoit le token i à τᵢ (plus un décalage réseau constant) : le premier texte apparaît à τ₁ = TTFT, et le dernier toujours à T_total. La latence perçue passe donc de T_total à TTFT, ici de 1,4914 s à 68 ms, soit 22 fois moins, et le temps total ne change pas ; en pratique, l'envoi de chaque événement ajoute même un léger surcoût. Pour un agent, un appel d'outil ne s'exécute que lorsque ses arguments JSON sont complets, donc à T_total dans les deux cas : pour accélérer la boucle, on réduit G (0,35 s au lieu de 1,49 s avec 60 tokens au lieu de 300) ou le TTFT (cache de préfixe), pas l'affichage.

### 8. Exemple fait à la main (le code reprend ces nombres)

Modèle jouet : prompt « <debut> le loyer est », donc P = 4, G = 6 tokens générés, d = 4, L = 2 couches, c_lin = 4 d² = 64 (projections Q, K, V et O).

- **Sans cache**, six passes complètes sur n = 4, 5, …, 9 positions. Σ n = 39 et Σ n(n + 1) = 20 + 30 + 42 + 56 + 72 + 90 = 310. Linéaires : 2 × 64 × 39 = 4 992 ; attention : 2 × 4 × 310 = 2 480.
- **Avec cache**, un prefill sur 4 positions puis 5 pas de décodage, aux longueurs 5 à 9. Chacune des 9 positions passe une seule fois dans les projections : 2 × 64 × 9 = 1 152 ; le sixième token généré n'est jamais réinjecté. Attention : 2 × 4 × (4 × 5 + 2 × (5 + 6 + 7 + 8 + 9)) = 8 × 90 = 720.
- La tête de sortie coûte 6 × 10 × 4 = 240 multiplications dans les deux cas : un vecteur de logits sur 10 tokens par token produit.
- Le cache final contient 9 positions par couche : 2 × 2 × 1 × 4 × 9 × 8 = 1 152 octets.

## Effets et comportement

- **Un prompt plus long allonge le TTFT**, linéairement tant que le prefill est limité par le calcul, et ne change presque pas la latence inter-tokens, qui ne lit que m_kv octets de plus par token du contexte.
- **Une réponse plus longue allonge le temps total** d'environ une latence inter-tokens par token : pour un agent, les tokens de sortie dominent souvent la durée d'un tour.
- **Une conversation plus longue remplit la mémoire** : le cache croît linéairement, et le nombre de sessions par carte baisse d'autant.
- **Moins de têtes de clés-valeurs, plus de sessions.** Avec 8 têtes partagées au lieu de 32, le cache est divisé par 4, et le décodage d'un long contexte lit moins d'octets.
- **Un préfixe stable raccourcit le prefill**, et donc le TTFT, à condition d'être identique au token près d'une requête à l'autre.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| prefill sur P positions, cache K et V | `prefill(tokens, modele, compteur)` |
| un pas de décodage à la position n | `pas_de_decodage(token, position, cache, modele, compteur)` |
| une position d'une couche, ajout au cache | `couche_position(h, couche, K, V, compteur)` |
| softmax(q Kᵀ / √d) V | `attention(q, K, V, compteur)` |
| génération par recalcul, avec cache | `generer_sans_cache(...)`, `generer_avec_cache(...)` |
| Σ n, Σ n(n + 1) | `somme_n(a, b)`, `somme_n_n1(a, b)` |
| A et Λ, sans et avec cache | `couts_theoriques(P, G, d, couches, c_lin)` |
| M_KV | `memoire_cache_kv(couches, tetes_kv, d_tete, n, octets)` |
| t_prefill, t_decode | `Service.t_prefill(nouveaux, deja_en_cache)`, `Service.t_decode(n)` |
| flux de tokens sur horloge simulée | `generer_en_flux(P, G, service)` |
| latence perçue, temps total | `client_avec_flux(flux)`, `client_sans_flux(flux)` |

### Déroulé, ligne par ligne

**`creer_modele(graine, positions)`** tire, avec `random.Random(18)`, les embeddings des 10 tokens, 32 embeddings de position et, pour chacune des 2 couches, quatre matrices 4 × 4 de coefficients uniformes entre −0,8 et 0,8. Les poids sont arbitraires : la suite générée n'a pas de sens, seul compte le fait qu'elle soit identique par les deux chemins.

**`vec_mat(x, W, compteur)`** fait le produit d'un vecteur par une matrice et ajoute `len(W) * len(W[0])` multiplications, soit 16 pour une matrice 4 × 4, au compteur `"lineaire"`.

**`attention(q, K, V, compteur)`** ajoute `2 * len(K) * len(q)` au compteur `"attention"` : n scores de d multiplications et la moyenne de n valeurs de d coordonnées. Elle divise les scores par `math.sqrt(len(q))`, retire le maximum avant l'exponentielle (étape 2), puis mélange les valeurs.

**`couche_position(h, couche, K, V, compteur)`** est le cœur du cache. Elle calcule `q`, puis **ajoute** la clé et la valeur de la position à la fin des listes `K` et `V`, puis fait l'attention de `q` sur tout `K` et tout `V`. Comme `K` ne contient que les positions déjà traitées et la position courante, le masque causal est implicite : aucune position future n'est dans la liste. La connexion résiduelle ajoute la sortie projetée par `W_O` à `h`.

**`prefill(tokens, modele, compteur)`** crée un couple de listes vides par couche, calcule les états d'entrée, puis, couche par couche, passe toutes les positions dans `couche_position`. À la fin, `cache` contient P clés et P valeurs par couche, et `logits(h[-1], ...)` donne la distribution du premier token.

**`pas_de_decodage(token, position, cache, modele, compteur)`** ne traite qu'un état : celui du dernier token produit, à sa position. Dans chaque couche, `couche_position` ajoute une ligne au cache puis relit tout le cache. C'est C_cache(n).

**`generer_sans_cache(prompt, G, modele, compteur)`** appelle `prefill` sur toute la séquence à chaque token et jette le cache (`lg, _ = ...`) : c'est le recalcul complet, C_recalcul(n). **`generer_avec_cache`** appelle `prefill` une fois, puis `pas_de_decodage` pour i = 1, …, G − 1, avec la position `len(prompt) + i - 1` : le token produit au tour i − 1 est placé juste après les précédents.

**`logits_bidirectionnels(tokens, modele)`** calcule d'abord toutes les clés et valeurs d'une couche, puis fait regarder à chaque position **toutes** les autres, futur compris. Elle renvoie aussi les clés et valeurs, qui servent de cache périmé au bloc 2.

**`somme_n(a, b)`** et **`somme_n_n1(a, b)`** sont les deux formes fermées ; `F = lambda m: m * (m + 1) * (m + 2) // 3` est la primitive télescopique du point 3. Le programme les compare aux sommes faites terme à terme sur trois intervalles.

**`couts_theoriques(P, G, d, couches, c_lin)`** renvoie les quatre totaux A et Λ. Pour le jouet, `couts_theoriques(4, 6, 4, 2, 64)` vaut 4 992 et 2 480 sans cache, 1 152 et 720 avec cache.

**`memoire_cache_kv(couches, tetes_kv, d_tete, n, octets)`** renvoie `2 * couches * tetes_kv * d_tete * n * octets` : 1 152 octets pour le jouet, 4 194 304 000 pour 32 couches, 32 têtes, 128, 8 000 tokens et 2 octets.

**`Service`** regroupe les valeurs illustratives : 7 × 10⁹ paramètres de 2 octets, 131 072 octets de cache par token, 10¹⁵ opérations et 3 × 10¹² octets par seconde, 40 ms de réseau. `t_prefill(nouveaux, deja_en_cache)` prend le maximum du calcul des tokens nouveaux et de la lecture des poids et du cache existant ; `t_decode(n)` fait de même pour un token, en lisant le cache de n tokens.

**`generer_en_flux(P, G, service)`** est un générateur : `yield horloge, 0` rend la main à l'appelant à l'instant où le premier token est prêt, puis chaque `yield` suivant ajoute un pas de décodage à l'horloge simulée. **`client_sans_flux`** consomme tout avant d'afficher : son premier instant visible est le dernier. **`client_avec_flux`** retient le premier et le dernier instant.

**`main()`**, bloc par bloc.

1. Les deux chemins produisent « est de de . . par », et la liste des logits de chaque pas est la même au bit près.
2. Le recalcul bidirectionnel et le décodage sur cache périmé diffèrent de 0,1262 au plus (point 1).
3. Les compteurs mesurent exactement les formules : 4 992 et 2 480 sans cache, 1 152 et 720 avec (points 2, 3 et 8).
4. À l'échelle, les rapports 450,1 et 406,8 (point 3).
5. Les 144 nombres du cache jouet, puis 4,19 Go contre 1,05 Go et 9 contre 38 sessions (point 4).
6. 28 ms de calcul contre 4,67 ms de lecture pour le prefill, 4,754 ms par pas de décodage, seuil à 333 tokens (point 5).
7. TTFT de 68 ms, fin à 1,4914 s avec ou sans streaming, 44,7 ms avec le cache de préfixe, 0,3486 s pour 60 tokens (points 6 et 7).

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`matrice(lignes, colonnes)`** — Cette fonction interne vit dans `creer_modele`, comme un artisan qui taille à la demande des plaques de chiffres dans le même bloc de hasard : elle reçoit un nombre de lignes et de colonnes, et remplit chaque case avec un tirage uniforme entre −0,8 et 0,8 pris dans le générateur `rng` de la fonction qui l'abrite, à graine 18. Elle renvoie cette liste de listes, et `creer_modele` l'appelle pour les embeddings des 10 tokens, les 32 embeddings de position et les quatre matrices 4 × 4 de chacune des 2 couches ; parce que tout vient du même générateur, le modèle jouet est identique à chaque exécution.

**`vec_mat(x, W, compteur)`** — On peut la voir comme un pointeur d'usine qui fait le travail et note aussitôt l'effort dans son registre : elle reçoit un vecteur x, une matrice W et un dictionnaire de compteurs, ajoute d'abord à la case `"lineaire"` le nombre de multiplications du produit, soit le nombre de lignes fois le nombre de colonnes de W, 16 pour une matrice 4 × 4, puis calcule x · W colonne par colonne. Elle renvoie le vecteur obtenu, et c'est grâce à ce registre que `main` peut confronter, au bloc 3, les multiplications réellement faites aux formules de `couts_theoriques`.

**`attention(q, K, V, compteur)`** — Cette fonction raconte une seule requête qui interroge toutes les clés déjà rangées : elle reçoit la requête q, la liste K des clés, la liste V des valeurs et le registre des compteurs, ajoute à la case `"attention"` deux fois le nombre de clés fois la dimension de q, puis calcule les scores divisés par √d, retranche le plus grand avant l'exponentielle, normalise les poids et mélange les valeurs. Elle renvoie le vecteur de sortie, de même dimension que q ; comme `couche_position` ne lui passe que les positions passées et la présente, elle n'a jamais besoin de masque explicite.

**`entree(modele, token, position)`** — Imaginons un vestiaire où chaque mot reçoit à la fois son costume et son numéro de place : la fonction reçoit le modèle, le numéro d'un token et sa position dans la séquence, puis additionne coordonnée par coordonnée l'embedding du token, lu dans `modele.E`, et l'embedding de la position, lu dans `modele.P`. Elle renvoie ce vecteur de dimension 4, l'état d'entrée de la première couche ; `prefill` l'appelle pour chaque position du prompt, `pas_de_decodage` pour le seul token nouveau, et `logits_bidirectionnels` pour tous les tokens de son contre-exemple.

**`logits(h, modele, compteur)`** — C'est le juge de sortie qui compare l'état final à chacun des 10 mots du vocabulaire : la fonction reçoit l'état h de la dernière position, le modèle et le registre, ajoute à la case `"sortie"` le nombre de tokens fois la dimension de h, soit 40, puis calcule le produit scalaire de h avec l'embedding de chaque token, ces embeddings servant aussi de tête de sortie. Elle renvoie la liste de ces 10 scores, les logits du prochain token ; comme elle est appelée une fois par token généré, chacun des deux chemins totalise 6 × 40 = 240 multiplications de tête de sortie.

**`argmax(valeurs)`** — Cette petite fonction est l'huissier qui proclame le gagnant d'un vote : elle reçoit une liste de nombres et renvoie l'indice du plus grand, en gardant le premier rencontré en cas d'égalité, puisque `max` parcourt les indices dans l'ordre. Elle ne fait aucun tirage au hasard, si bien que le décodage est glouton et parfaitement reproductible ; `generer_sans_cache` et `generer_avec_cache` s'en servent pour choisir chaque token à partir des logits, ce qui permet à `main` d'exiger que les deux chemins produisent exactement la même suite.

**`pas_de_decodage(token, position, cache, modele, compteur)`** — C'est l'ouvrier du soir qui ne fabrique qu'une seule pièce mais consulte tout l'atelier : la fonction reçoit le dernier token produit, sa position, le cache des clés et valeurs de chaque couche, le modèle et le registre, construit l'état d'entrée de ce seul token, puis le fait passer dans chaque couche par `couche_position`, qui ajoute une ligne au cache et relit tout le cache. Elle renvoie les logits du token suivant et modifie le cache sur place ; c'est le coût réduit C_cache(n), et `main` l'utilise aussi, au bloc 2, sur un cache périmé pour montrer l'écart de 0,1262.

**`logits_bidirectionnels(tokens, modele)`** — Voici le contre-exemple, un lecteur qui aurait le droit de lire la fin du livre avant d'en commenter le début : la fonction reçoit une liste de tokens et le modèle, calcule pour chaque couche toutes les clés et toutes les valeurs d'un coup, puis laisse chaque position regarder toutes les autres, futur compris, en comptant dans un registre jetable. Elle renvoie les logits de la dernière position et la liste des clés et valeurs de chaque couche ; `main` s'en sert pour montrer que ces clés deviennent fausses dès qu'un token s'ajoute, puisque le décodage sur ce cache s'écarte du vrai recalcul de 0,1262 au plus.

**`somme_n(a, b)`** — Cette fonction est le calcul de tête du petit Gauss : elle reçoit les bornes a et b et renvoie, en une seule ligne, la somme des entiers de a à b, égale à (a + b)(b − a + 1) / 2, sans jamais parcourir l'intervalle. `couts_theoriques` s'en sert pour compter les multiplications linéaires du recalcul complet et la part arithmétique de l'attention avec cache, et `main` la compare à la somme faite terme à terme sur les intervalles (1, 1), (4, 9) et (7, 30).

**`somme_n_n1(a, b)`** — Sa sœur fait le même tour de magie pour les produits n (n + 1) : elle reçoit les bornes a et b, définit la primitive télescopique F(m) = m (m + 1)(m + 2) / 3, puis renvoie F(b) − F(a − 1), qui vaut exactement la somme des n (n + 1) pour n allant de a à b. Elle sert à compter l'attention du recalcul complet, où la passe de longueur n coûte d × n (n + 1) multiplications ; de 4 à 9, la somme vaut 310, et `main` la vérifie elle aussi sur trois intervalles.

**`couts_theoriques(P, G, d, couches, c_lin)`** — C'est le devis du comptable, établi avant les travaux : la fonction reçoit la longueur P du prompt, le nombre G de tokens générés, la dimension d, le nombre de couches et le coût linéaire c_lin d'une position dans une couche, puis assemble, avec `somme_n` et `somme_n_n1`, les multiplications linéaires et d'attention du chemin sans cache et du chemin avec cache. Elle renvoie un dictionnaire à deux étages ; pour le jouet, `couts_theoriques(4, 6, 4, 2, 64)` annonce 4 992 et 2 480 sans cache, 1 152 et 720 avec, et à grande échelle elle donne un rapport de 450,1 sur les linéaires.

**`memoire_cache_kv(couches, tetes_kv, d_tete, n, octets)`** — Cette fonction joue le gardien d'entrepôt qui calcule la place occupée par les cartons de clés et de valeurs : elle reçoit le nombre de couches, de têtes KV, la dimension d'une tête, le nombre n de tokens et le nombre d'octets par nombre, et renvoie le produit de 2, pour K et V, par tous ces facteurs. Elle donne 1 152 octets pour le cache jouet, 4 194 304 000 octets pour 32 couches, 32 têtes de 128, 8 000 tokens et 2 octets, et 131 072 octets par token avec 8 têtes, la valeur reprise par `Service`.

**`Service.t_prefill(nouveaux, deja_en_cache)`** — Cette méthode est le chronométreur d'un accélérateur fictif qui doit à la fois calculer et lire sa mémoire : elle reçoit le nombre de tokens nouveaux et le nombre de tokens déjà en cache, zéro par défaut, calcule le temps de calcul, deux opérations par paramètre et par token nouveau divisées par 10¹⁵ par seconde, puis le temps de lecture des poids et du cache existant à 3 × 10¹² octets par seconde. Elle renvoie le plus long des deux, car le plus lent impose son rythme : 28 ms de calcul l'emportent sur 4,67 ms de lecture pour 2 000 tokens, et avec 1 800 tokens déjà en cache le TTFT tombe à 44,7 ms.

**`Service.t_decode(n)`** — C'est le même chronométreur, mais pour un seul token produit alors que le cache en contient déjà n : la méthode reçoit n, calcule le temps de calcul d'un token, deux opérations par paramètre, puis le temps de lecture de tous les poids et des n entrées du cache, et renvoie le maximum des deux. Ici la lecture l'emporte toujours largement, si bien qu'un pas de décodage à n = 2 001 coûte 4,754 ms, plus de cent fois son calcul seul ; c'est ce que `main` vérifie au bloc 6 et ce que `generer_en_flux` additionne pour avancer son horloge.

**`main()`** — Le chef d'orchestre déroule les sept blocs du programme sur le prompt « `<debut> le loyer est` » et G = 6 : il fait générer les deux chemins, sans et avec cache, et exige les mêmes tokens et les mêmes logits au bit près, puis montre qu'un cache bâti sans masque causal s'écarte du recalcul. Il confronte ensuite les compteurs de multiplications aux formules, passe à l'échelle d'un prompt de 2 000 tokens, vérifie la taille du cache jouet et des caches réels, compare prefill et décodage sur le service fictif, et termine par le TTFT de 68 ms, la fin à 1,4914 s avec ou sans streaming et la réponse courte de 60 tokens ; il ne renvoie rien et n'imprime le message final que si tous les `assert` sont passés.

```python
"""Étape 33 bis — génération autorégressive : prefill, decode, cache KV, TTFT, streaming. Bibliothèque standard seulement."""
import math
import random
import sys
from dataclasses import dataclass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

VOCAB = ["<debut>", "le", "loyer", "est", "de", "60000", "AED", "par", "an", "."]
D = 4          # largeur du modèle jouet (une seule tête : d_tête = d)
COUCHES = 2
NOMS = {"lineaire": "linéaires", "attention": "attention"}


# ---------------------------------------------------------------- le modèle jouet
@dataclass
class Modele:
    E: list        # embeddings des tokens, |V| × d (réutilisés comme tête de sortie)
    P: list        # embeddings de position, positions × d
    couches: list  # une couche = {"W_Q", "W_K", "W_V", "W_O"}, chacune d × d


def creer_modele(graine: int = 18, positions: int = 32) -> Modele:
    rng = random.Random(graine)

    def matrice(lignes: int, colonnes: int) -> list:
        return [[rng.uniform(-0.8, 0.8) for _ in range(colonnes)] for _ in range(lignes)]

    couches = [{nom: matrice(D, D) for nom in ("W_Q", "W_K", "W_V", "W_O")} for _ in range(COUCHES)]
    return Modele(matrice(len(VOCAB), D), matrice(positions, D), couches)


def vec_mat(x: list, W: list, compteur: dict) -> list:
    """x · W, en comptant les multiplications dans compteur["lineaire"]."""
    compteur["lineaire"] += len(W) * len(W[0])
    return [sum(x[l] * W[l][c] for l in range(len(W))) for c in range(len(W[0]))]


def attention(q: list, K: list, V: list, compteur: dict) -> list:
    """Une requête contre n clés : n·d multiplications pour les scores, n·d pour la moyenne des valeurs."""
    compteur["attention"] += 2 * len(K) * len(q)
    scores = [sum(a * b for a, b in zip(q, k)) / math.sqrt(len(q)) for k in K]
    pic = max(scores)
    expo = [math.exp(s - pic) for s in scores]
    total = sum(expo)
    poids = [e / total for e in expo]
    return [sum(poids[j] * V[j][c] for j in range(len(V))) for c in range(len(q))]


def entree(modele: Modele, token: int, position: int) -> list:
    return [e + p for e, p in zip(modele.E[token], modele.P[position])]


def couche_position(h: list, couche: dict, K: list, V: list, compteur: dict) -> list:
    """Traite UNE position : ajoute k et v à la fin de K et V, puis q regarde K et V (masque causal implicite)."""
    q = vec_mat(h, couche["W_Q"], compteur)
    K.append(vec_mat(h, couche["W_K"], compteur))
    V.append(vec_mat(h, couche["W_V"], compteur))
    sortie = vec_mat(attention(q, K, V, compteur), couche["W_O"], compteur)
    return [a + b for a, b in zip(h, sortie)]          # connexion résiduelle


def logits(h: list, modele: Modele, compteur: dict) -> list:
    compteur["sortie"] += len(modele.E) * len(h)
    return [sum(a * b for a, b in zip(h, e)) for e in modele.E]


def argmax(valeurs: list) -> int:
    return max(range(len(valeurs)), key=lambda i: valeurs[i])


def prefill(tokens: list, modele: Modele, compteur: dict) -> tuple[list, list]:
    """Toutes les positions du prompt, couche par couche ; on garde K et V de chaque couche : c'est le cache."""
    cache = [([], []) for _ in modele.couches]
    h = [entree(modele, t, i) for i, t in enumerate(tokens)]
    for (K, V), couche in zip(cache, modele.couches):
        h = [couche_position(h_i, couche, K, V, compteur) for h_i in h]
    return logits(h[-1], modele, compteur), cache


def pas_de_decodage(token: int, position: int, cache: list, modele: Modele, compteur: dict) -> list:
    """Une seule position : on relit K et V du cache au lieu de les recalculer."""
    h = entree(modele, token, position)
    for (K, V), couche in zip(cache, modele.couches):
        h = couche_position(h, couche, K, V, compteur)
    return logits(h, modele, compteur)


def generer_sans_cache(prompt: list, G: int, modele: Modele, compteur: dict) -> tuple[list, list]:
    """À chaque token, on refait la passe complète sur toute la séquence et on jette K et V."""
    sequence, traces = list(prompt), []
    for _ in range(G):
        lg, _ = prefill(sequence, modele, compteur)
        traces.append(lg)
        sequence.append(argmax(lg))
    return sequence[len(prompt):], traces


def generer_avec_cache(prompt: list, G: int, modele: Modele, compteur: dict) -> tuple[list, list, list]:
    """Prefill une fois (premier token), puis G − 1 pas de décodage qui relisent le cache."""
    lg, cache = prefill(prompt, modele, compteur)
    produits, traces = [], []
    for i in range(G):
        if i > 0:
            lg = pas_de_decodage(produits[-1], len(prompt) + i - 1, cache, modele, compteur)
        traces.append(lg)
        produits.append(argmax(lg))
    return produits, traces, cache


def logits_bidirectionnels(tokens: list, modele: Modele) -> tuple[list, list]:
    """Contre-exemple : sans masque, chaque position voit aussi le futur. Renvoie les logits et le « cache »."""
    poubelle = {"lineaire": 0, "attention": 0, "sortie": 0}
    h = [entree(modele, t, i) for i, t in enumerate(tokens)]
    cache = []
    for couche in modele.couches:
        K = [vec_mat(x, couche["W_K"], poubelle) for x in h]
        V = [vec_mat(x, couche["W_V"], poubelle) for x in h]
        cache.append((K, V))
        h = [[a + b for a, b in zip(x, vec_mat(attention(vec_mat(x, couche["W_Q"], poubelle), K, V, poubelle),
                                              couche["W_O"], poubelle))] for x in h]
    return logits(h[-1], modele, poubelle), cache


# ---------------------------------------------------------------- les formules de coût
def somme_n(a: int, b: int) -> int:
    """Σ_{n=a}^{b} n = (a + b)(b − a + 1)/2 (somme arithmétique)."""
    return (a + b) * (b - a + 1) // 2


def somme_n_n1(a: int, b: int) -> int:
    """Σ_{n=a}^{b} n(n + 1) = F(b) − F(a − 1), avec F(m) = m(m + 1)(m + 2)/3."""
    F = lambda m: m * (m + 1) * (m + 2) // 3
    return F(b) - F(a - 1)


def couts_theoriques(P: int, G: int, d: int, couches: int, c_lin: int) -> dict:
    """Multiplications pour P tokens de prompt et G tokens générés ; c_lin = multiplications linéaires par position et par couche."""
    return {
        "sans cache": {"lineaire": couches * c_lin * somme_n(P, P + G - 1),
                       "attention": couches * d * somme_n_n1(P, P + G - 1)},
        "avec cache": {"lineaire": couches * c_lin * (P + G - 1),
                       "attention": couches * d * (P * (P + 1) + 2 * somme_n(P + 1, P + G - 1))},
    }


def memoire_cache_kv(couches: int, tetes_kv: int, d_tete: int, n: int, octets: int) -> int:
    """2 (K et V) × couches × têtes KV × d_tête × n tokens × octets par nombre."""
    return 2 * couches * tetes_kv * d_tete * n * octets


# ---------------------------------------------------------------- le temps, sur une horloge simulée
@dataclass
class Service:
    """Valeurs illustratives : un modèle de 7 milliards de paramètres sur un accélérateur fictif."""
    params: float = 7e9
    octets_param: int = 2              # fp16
    kv_par_token: int = 131_072        # 2 × 32 couches × 8 têtes KV × 128 × 2 octets
    flops: float = 1e15                # opérations utiles par seconde
    bande: float = 3e12                # octets lus par seconde
    reseau: float = 0.040              # aller-retour réseau, en secondes

    def t_prefill(self, nouveaux: int, deja_en_cache: int = 0) -> float:
        calcul = 2 * self.params * nouveaux / self.flops
        memoire = (self.params * self.octets_param + self.kv_par_token * deja_en_cache) / self.bande
        return max(calcul, memoire)

    def t_decode(self, n: int) -> float:
        calcul = 2 * self.params / self.flops
        memoire = (self.params * self.octets_param + self.kv_par_token * n) / self.bande
        return max(calcul, memoire)


def generer_en_flux(P: int, G: int, service: Service):
    """Générateur : rend (instant, numéro du token) au moment où chaque token est prêt, sur une horloge simulée."""
    horloge = service.reseau + service.t_prefill(P)        # le premier token sort à la fin du prefill
    yield horloge, 0
    for i in range(1, G):
        horloge += service.t_decode(P + i)                 # un pas de décodage par token suivant
        yield horloge, i


def client_sans_flux(flux) -> tuple[float, float]:
    """Attend la réponse complète : le premier texte visible apparaît à la fin."""
    instants = [t for t, _ in flux]
    return instants[-1], instants[-1]


def client_avec_flux(flux) -> tuple[float, float]:
    """Affiche chaque token dès qu'il arrive."""
    premier = dernier = None
    for t, _ in flux:
        if premier is None:
            premier = t
        dernier = t
    return premier, dernier


def main() -> None:
    modele = creer_modele()
    prompt = [VOCAB.index(m) for m in ("<debut>", "le", "loyer", "est")]
    P, G = len(prompt), 6

    print("=== 1. Avec ou sans cache : les mêmes tokens, les mêmes logits ===")
    c_sans = {"lineaire": 0, "attention": 0, "sortie": 0}
    c_avec = {"lineaire": 0, "attention": 0, "sortie": 0}
    sortie_sans, logits_sans = generer_sans_cache(prompt, G, modele, c_sans)
    sortie_avec, logits_avec, cache = generer_avec_cache(prompt, G, modele, c_avec)
    print("  sans cache :", " ".join(VOCAB[t] for t in sortie_sans))
    print("  avec cache :", " ".join(VOCAB[t] for t in sortie_avec))
    assert sortie_sans == sortie_avec and logits_sans == logits_avec      # égalité exacte, au bit près
    print(f"  logits du dernier pas, identiques au bit près : {[round(x, 4) for x in logits_avec[-1][:4]]} …")

    print("=== 2. Sans masque causal, le cache devient faux ===")
    sequence = prompt + sortie_avec[:1]
    vrai, _ = logits_bidirectionnels(sequence, modele)
    _, cache_perime = logits_bidirectionnels(prompt, modele)
    faux = pas_de_decodage(sequence[-1], P, cache_perime, modele, {"lineaire": 0, "attention": 0, "sortie": 0})
    ecart = max(abs(a - b) for a, b in zip(vrai, faux))
    print(f"  écart maximal entre recalcul et cache périmé : {ecart:.4f}")
    assert ecart > 0.01

    print(f"=== 3. Multiplications comptées (P = {P}, G = {G}, d = {D}, {COUCHES} couches) ===")
    theorie = couts_theoriques(P, G, D, COUCHES, c_lin=4 * D * D)
    for nom, mesure in (("sans cache", c_sans), ("avec cache", c_avec)):
        print(f"  {nom} : linéaires = {mesure['lineaire']:5d}   attention = {mesure['attention']:5d}"
              f"   tête de sortie = {mesure['sortie']}")
        assert mesure["lineaire"] == theorie[nom]["lineaire"] and mesure["attention"] == theorie[nom]["attention"]
    assert (c_sans["attention"], c_avec["attention"]) == (2480, 720) and c_sans["sortie"] == c_avec["sortie"] == 240
    assert all(somme_n(a, b) == sum(range(a, b + 1)) and somme_n_n1(a, b) == sum(n * (n + 1) for n in range(a, b + 1))
               for a, b in ((1, 1), (4, 9), (7, 30)))

    print("=== 4. À l'échelle : P = 2 000, G = 500, d_model = 4 096, 32 couches ===")
    grand = couts_theoriques(2_000, 500, 4_096, 32, c_lin=12 * 4_096 ** 2)
    for poste in ("lineaire", "attention"):
        s, a = grand["sans cache"][poste], grand["avec cache"][poste]
        print(f"  {NOMS[poste]:9s} : sans cache {s:.3e}   avec cache {a:.3e}   rapport {s / a:6.1f}")
    assert round(grand["sans cache"]["lineaire"] / grand["avec cache"]["lineaire"], 1) == 450.1

    print("=== 5. Mémoire du cache KV ===")
    nombres = sum(len(K) * len(K[0]) + len(V) * len(V[0]) for K, V in cache)
    jouet = memoire_cache_kv(COUCHES, 1, D, P + G - 1, 8)
    print(f"  jouet : {nombres} nombres de 8 octets = {nombres * 8} octets ; formule = {jouet}")
    assert nombres * 8 == jouet == 1_152
    for tetes_kv in (32, 8):
        octets = memoire_cache_kv(32, tetes_kv, 128, 8_000, 2)
        print(f"  32 couches, {tetes_kv:2d} têtes KV de 128, 8 000 tokens, fp16 : {octets / 1e9:.2f} Go"
              f" ; sessions dans 40 Go : {int(40e9 // octets)}")
    assert memoire_cache_kv(32, 8, 128, 1, 2) == 131_072 and memoire_cache_kv(32, 32, 128, 8_000, 2) == 4_194_304_000

    print("=== 6. Prefill limité par le calcul, décodage limité par la mémoire ===")
    service = Service()
    calcul_p, memoire_p = 2 * service.params * 2_000 / service.flops, service.params * 2 / service.bande
    print(f"  prefill de 2 000 tokens : calcul {calcul_p * 1e3:.2f} ms, lecture des poids {memoire_p * 1e3:.2f} ms")
    print(f"  un pas de décodage à n = 2 001 : {service.t_decode(2_001) * 1e3:.3f} ms"
          f" (calcul seul : {2 * service.params / service.flops * 1e3:.3f} ms)")
    assert calcul_p > memoire_p and service.t_decode(2_001) > 100 * 2 * service.params / service.flops
    print(f"  seuil : le prefill devient limité par le calcul au-delà de {service.flops / service.bande:.0f} tokens")

    print("=== 7. TTFT, latence inter-tokens, streaming (P = 2 000, G = 300) ===")
    ttft = service.reseau + service.t_prefill(2_000)
    premier_flux, fin_flux = client_avec_flux(generer_en_flux(2_000, 300, service))
    premier_bloc, fin_bloc = client_sans_flux(generer_en_flux(2_000, 300, service))
    itl = (fin_flux - premier_flux) / 299
    print(f"  TTFT = {ttft * 1e3:.1f} ms ; latence inter-tokens moyenne = {itl * 1e3:.3f} ms ; {1 / itl:.0f} tokens/s")
    print(f"  avec streaming : premier texte à {premier_flux * 1e3:.1f} ms, fin à {fin_flux:.4f} s")
    print(f"  sans streaming : premier texte à {premier_bloc:.4f} s, fin à {fin_bloc:.4f} s")
    assert premier_flux == ttft and fin_flux == fin_bloc and premier_bloc == fin_bloc
    assert round(ttft * 1e3, 1) == 68.0 and round(fin_flux, 4) == 1.4914
    avec_prefixe = service.reseau + service.t_prefill(200, deja_en_cache=1_800)
    print(f"  1 800 tokens du prompt déjà en cache : TTFT = {avec_prefixe * 1e3:.1f} ms au lieu de {ttft * 1e3:.1f} ms")
    assert round(avec_prefixe * 1e3, 1) == 44.7
    _, fin_courte = client_avec_flux(generer_en_flux(2_000, 60, service))
    print(f"  réponse courte de 60 tokens : fin à {fin_courte:.4f} s au lieu de {fin_flux:.4f} s pour 300 tokens")
    assert round(fin_courte, 4) == 0.3486
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
  sans cache : est de de . . par
  avec cache : est de de . . par
…
  écart maximal entre recalcul et cache périmé : 0.1262
…
  sans cache : linéaires =  4992   attention =  2480   tête de sortie = 240
  avec cache : linéaires =  1152   attention =   720   tête de sortie = 240
…
  linéaires : sans cache 7.246e+15   avec cache 1.610e+13   rapport  450.1
  attention : sans cache 3.331e+14   avec cache 8.189e+11   rapport  406.8
…
  32 couches,  8 têtes KV de 128, 8 000 tokens, fp16 : 1.05 Go ; sessions dans 40 Go : 38
…
  TTFT = 68.0 ms ; latence inter-tokens moyenne = 4.761 ms ; 210 tokens/s
  avec streaming : premier texte à 68.0 ms, fin à 1.4914 s
  sans streaming : premier texte à 1.4914 s, fin à 1.4914 s
  1 800 tokens du prompt déjà en cache : TTFT = 44.7 ms au lieu de 68.0 ms
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : le cache KV n'est pas une approximation. C'est le même calcul, rangé autrement, et il n'est exact que grâce au masque causal. Il transforme une somme de carrés en somme arithmétique, au prix d'une mémoire qui grandit avec chaque token ; et le streaming déplace le premier affichage, pas la fin.

### Le streaming chez un fournisseur (extrait)

Le générateur `generer_en_flux` est ce que fait un client de streaming : il consomme des événements au fil de l'eau. Pour un développeur Spring, c'est l'équivalent d'un `Flux<String>` de WebFlux ou d'un `SseEmitter` : le serveur envoie des événements SSE (server-sent events), et le client les lit un par un. Avec l'API Claude, le SDK expose ce flux et recolle les morceaux de texte ; on y mesure le TTFT tel que l'utilisateur le vit, réseau et file d'attente compris.

```python
# [extrait] — streaming avec l'API Claude, non exécuté par le harnais (pip install anthropic)
import time

import anthropic

client = anthropic.Anthropic()   # lit ANTHROPIC_API_KEY ou le profil créé par `ant auth login`
debut, premier = time.perf_counter(), None
with client.beta.messages.stream(
    model="claude-opus-5-5",
    max_tokens=64000,
    betas=["server-side-fallback-2026-07-01"],    # comme l'adaptateur de l'étape 13
    fallbacks="default",                           # un refus est rejoué sur le modèle de repli, dans le même appel
    output_config={"effort": "medium"},
    messages=[{"role": "user", "content": "Résume ce bail en cinq points."}],
) as flux:
    for morceau in flux.text_stream:              # chaque morceau de texte arrive dès qu'il est prêt
        if premier is None:
            premier = time.perf_counter() - debut  # TTFT vu du client
        print(morceau, end="", flush=True)
    message = flux.get_final_message()            # le message complet, comme sans streaming
if message.stop_reason == "refusal":              # à traiter avant de lire le contenu
    print("refus")
print(f"\nTTFT {premier:.3f} s ; total {time.perf_counter() - debut:.3f} s ; {message.usage.output_tokens} tokens")
```

Les morceaux de `text_stream` sont déjà des chaînes : le SDK s'occupe du décodage incrémental des octets que l'étape 02 bis a montré nécessaire.

## Squelette algorithmique

Les trois algorithmes prennent un modèle et une séquence de tokens. Le prefill rend les logits du premier token et le cache ; le pas de décodage rend les logits du token suivant et agrandit le cache ; la génération en flux rend les tokens au fil de l'eau.

```text
ALGORITHME Prefill(tokens t₁ … t_P)
SORTIE  : logits du token P + 1, cache (Kˡ, Vˡ) pour chaque couche l

  POUR i DE 1 À P FAIRE  hᵢ ← embedding(tᵢ) + position(i)  FIN POUR
  POUR CHAQUE couche l FAIRE
      Kˡ ← liste vide ; Vˡ ← liste vide
      POUR i DE 1 À P FAIRE
          q ← hᵢ × W_Q ; ajouter hᵢ × W_K à Kˡ ; ajouter hᵢ × W_V à Vˡ
          hᵢ ← hᵢ + Attention(q, Kˡ, Vˡ) × W_O          (Kˡ ne contient que les positions ≤ i)
      FIN POUR
  FIN POUR
  RETOURNER logits(h_P), cache

ALGORITHME PasDeDécodage(token t, position n, cache)
  h ← embedding(t) + position(n)
  POUR CHAQUE couche l FAIRE
      q ← h × W_Q ; ajouter h × W_K à Kˡ ; ajouter h × W_V à Vˡ      (le cache grandit d'une ligne)
      h ← h + Attention(q, Kˡ, Vˡ) × W_O                              (n clés relues, aucune recalculée)
  FIN POUR
  RETOURNER logits(h)

ALGORITHME GénérerEnFlux(prompt, G)
  logits, cache ← Prefill(prompt)
  POUR i DE 1 À G FAIRE
      SI i > 1 ALORS logits ← PasDeDécodage(dernier token, P + i − 1, cache) FIN SI
      token ← Choisir(logits)                                          (argmax ou tirage, étape 2)
      ÉMETTRE token                                                    (le client l'affiche aussitôt)
      SI token = fin de séquence ALORS ARRÊTER FIN SI
  FIN POUR
```

**Complexité :** le prefill coûte O(L × (P × c_lin + P² × d)) en temps, et la mémoire du cache O(L × h_kv × d_h × P) en sortie. Un pas de décodage à la longueur n coûte O(L × (c_lin + n × d)) en temps et ajoute O(L × h_kv × d_h) à la mémoire. Générer G tokens coûte donc O(L × (G × c_lin + G × (P + G) × d)) avec le cache, contre O(L × (G × (P + G) × c_lin + (P + G)³ × d)) en recalculant tout. En temps réel, le prefill est limité par le calcul, le décodage par la lecture des poids et du cache : O(b × N_p + m_kv × n) octets lus par token.

**Du squelette au code :** `Prefill` est `prefill`, et la boucle intérieure « q, ajouter à Kˡ et Vˡ, attention » est `couche_position`, partagée avec `PasDeDécodage`, qui est `pas_de_decodage`. `Attention` est `attention`. La génération sans flux est `generer_avec_cache` (avec `argmax` comme `Choisir`), et la version « recalculer tout » qui sert de témoin est `generer_sans_cache`. `GénérerEnFlux` correspond à `generer_en_flux`, où `ÉMETTRE` est le `yield` et où l'horloge simulée de `Service` remplace le vrai calcul ; le modèle jouet n'a pas de token de fin, d'où l'absence de la ligne `ARRÊTER` dans le code.

## Cas d'usage réels aux Émirats

Les valeurs de matériel, de mémoire libre et de délais ci-dessous sont illustratives : elles viennent du modèle de temps du programme. En production, on mesure le TTFT et la latence inter-tokens au 95ᵉ percentile sur le trafic réel.

### Secteur public — un assistant qui répond tout de suite

Une entité de services publics en ligne, accessible par UAE Pass, sert un assistant bilingue arabe-anglais qui explique les démarches et les pièces à fournir. Le prompt système, les règles de la démarche et les définitions d'outils font environ 2 000 tokens, identiques pour tous les usagers. Le calcul du point 6 donne un TTFT de 68 ms et une réponse de 300 tokens terminée à 1,49 s : sans streaming, l'usager regarde un écran vide pendant une seconde et demie ; avec streaming, il lit les premiers mots après 68 ms. L'équipe active donc le streaming dans l'interface, et place en tête du prompt toute la partie stable, sans date ni identifiant de session, pour que le cache de préfixe la retrouve d'une requête à l'autre : avec 1 800 tokens déjà en cache, le TTFT tombe à 44,7 ms. Sans ce soin, une simple date du jour écrite en tête du prompt fait recalculer tout le prefill à chaque requête, et le TTFT remonte aux heures de pointe, quand la file d'attente s'ajoute. Garder les historiques courts sert aussi la minimisation des données personnelles qu'exige la PDPL. Les indicateurs suivis sont le TTFT au 95ᵉ percentile et la part des tokens d'entrée lus dans le cache.

### Banque — dimensionner le cache KV d'un modèle hébergé sur site

Une banque de détail de Dubaï héberge sur ses propres serveurs un modèle ouvert pour ses assistants internes de conformité et de KYC, parce que sa politique interne interdit que les dossiers clients quittent son infrastructure. Un analyste ouvre une session sur un dossier qui atteint vite 8 000 tokens, pièces et échanges compris. Le calcul du point 4 fixe la capacité : 4,19 Go de cache par session si le modèle garde 32 têtes de clés-valeurs, 1,05 Go s'il en partage 8, soit 9 ou 38 sessions simultanées dans 40 Go de mémoire libre. L'équipe retient un modèle à têtes partagées, plafonne la longueur des sessions et résume l'historique au-delà d'un seuil exprimé en tokens, puisque le cache croît linéairement avec chaque token échangé. Sans ce calcul, le service tombe en panne de mémoire le jour où les analystes ouvrent tous un gros dossier, souvent en fin de trimestre, au moment des revues anti-blanchiment. Le moteur d'inférence doit aussi libérer le cache d'une session fermée, faute de quoi la mémoire fuit d'une journée à l'autre. Les indicateurs suivis sont le nombre de sessions simultanées par carte et le nombre d'incidents de mémoire.

### Assurance — un agent de sinistres que le streaming n'accélère pas

Un assureur auto et santé fait instruire les déclarations de sinistre par un agent qui enchaîne cinq outils : lecture de la déclaration, recherche du contrat, calcul de la franchise et de la vétusté, détection de fraude, proposition au gestionnaire. La première version faisait précéder chaque appel d'outil d'un raisonnement visible d'environ 300 tokens. Le point 7 explique pourquoi le streaming n'y changeait rien : l'outil ne s'exécute que lorsque ses arguments JSON sont complets, donc à la fin de la génération, soit environ 1,49 s par tour dans le modèle de temps du programme, et 7,5 s pour cinq tours. L'équipe réduit donc les tokens de sortie : des appels d'outils directs, une justification courte et structurée seulement à l'étape finale, et une limite `max_tokens` adaptée à chaque étape ; à 60 tokens par tour, le tour tombe à 0,35 s. Sans cette mesure, le gestionnaire attend l'agent à chaque dossier, et les heures de pointe saturent le service. La décision finale reste documentée par le gestionnaire, sous la supervision de la CBUAE. Les indicateurs suivis sont la durée moyenne d'un tour d'agent et le nombre de tokens de sortie par tour.

### Immobilier — afficher en flux sans afficher un prix faux

Une agence et un promoteur actifs à Dubaï et Abu Dhabi proposent sur leur site un assistant qui répond aux acheteurs sur les projets off-plan : échéancier, prix en AED par sqft, frais de transfert DLD de 4 %. Le streaming améliore nettement la latence perçue, mais il crée un risque : le texte s'affiche avant que le garde-fou qui vérifie les montants contre la base du projet n'ait vu la réponse complète. Un prix généré faux serait déjà sous les yeux de l'acheteur au moment où le garde-fou le détecte. L'équipe sépare donc les flux : la prose est affichée au fil de l'eau, mais tout segment qui contient un montant ou une date contractuelle est retenu jusqu'à sa validation par l'outil de prix, puis affiché d'un bloc, et les montants eux-mêmes sont insérés depuis la base, jamais générés. Le TTFT perçu reste celui de la prose, et aucun chiffre non vérifié n'apparaît. Sans cette séparation, l'agence doit corriger publiquement des prix déjà lus, ce qui expose à une réclamation de l'acheteur. Les indicateurs suivis sont le TTFT perçu et le nombre de montants retirés après affichage, avec un objectif de zéro.

### RH — un traitement de nuit où compte le débit, pas la latence

Un cabinet RH multi-émirats fait relire chaque nuit plusieurs centaines de contrats et d'avenants par un modèle hébergé en interne, pour extraire les clauses de préavis, les salaires de base et les éléments de calcul de l'indemnité de fin de service. Personne n'attend devant l'écran : le TTFT n'a aucune importance, seul compte le nombre de documents traités avant le matin. Le point 5 indique où chercher le gain : chaque pas de décodage d'une séquence seule passe plus de 300 fois plus de temps à lire les poids qu'à calculer, si bien que traiter plusieurs contrats en même temps, avec une seule lecture des poids par pas, multiplie le débit sans changer le matériel (étape 72 bis). Les contrats longs ont, eux, un prefill limité par le calcul, que l'on peut découper en morceaux pour l'intercaler avec les pas de décodage des autres documents. Sans ce réglage, le traitement déborde sur la matinée et les gestionnaires commencent leur journée sans les extractions. Les montants extraits restent recalculés par l'outil de fin de service conforme au décret-loi fédéral 33/2021, jamais pris tels quels dans le texte généré. Les indicateurs suivis sont le nombre de tokens générés par seconde et par carte, et le coût par contrat.

### Crypto — une alerte qui doit partir en moins d'une seconde

Une plateforme d'actifs virtuels agréée par la VARA fait rédiger par un agent les alertes de liquidité envoyées à l'équipe d'astreinte, à partir d'un contexte d'environ 2 000 tokens : état des pools, seuils, derniers mouvements. L'astreinte veut l'alerte en moins d'une seconde après l'événement. Le modèle de temps du programme montre que le délai se joue presque entièrement sur la longueur de la sortie : une alerte rédigée en 300 tokens arrive à 1,49 s, une alerte structurée en 60 tokens (niveau, pool, montant, action recommandée) à 0,35 s, avec le même TTFT de 68 ms. La plateforme impose donc un format court, avec une limite `max_tokens`, et garde le contexte stable en tête du prompt pour bénéficier du cache de préfixe. Le streaming n'apporte rien ici, puisque l'alerte n'est envoyée qu'une fois complète et validée. Sans ce format, l'alerte part après le moment où l'équipe aurait pu agir sur le pool, ce qui est précisément le risque que la surveillance doit réduire. Les indicateurs suivis sont le délai entre l'événement et l'alerte au 95ᵉ percentile, et le nombre de tokens par alerte.

## Pièges et limites

- **Croire que le streaming accélère l'agent.** Il avance le premier affichage, pas la fin ; un appel d'outil attend son JSON complet. Pour accélérer la boucle, on réduit les tokens de sortie ou le prefill.
- **Exiger l'égalité au bit près sur carte graphique.** Le programme l'obtient parce qu'il refait les mêmes opérations dans le même ordre ; les noyaux GPU changent l'ordre des additions selon la taille du lot, et cache et recalcul peuvent alors différer au dernier chiffre. On compare avec une tolérance.
- **Oublier le cache KV dans le budget mémoire.** Il grandit avec chaque token de chaque session ; c'est souvent lui, et non les poids, qui limite le nombre de sessions.
- **Mesurer le TTFT côté serveur seulement.** L'utilisateur subit aussi la file d'attente et le réseau ; on le mesure côté client.
- **Mettre une donnée variable en tête du prompt.** Une date ou un identifiant de requête en tête empêche le cache de préfixe de servir : chaque requête refait le prefill complet, plus lent et plus cher (étape 72).

### Exercice feuille blanche

1. Sans regarder le code, écrire `couche_position`, `prefill` et `pas_de_decodage`, puis vérifier que la génération avec cache donne les mêmes logits que la génération sans cache.
2. Prédire, puis vérifier avec `couts_theoriques(4, 7, 4, 2, 64)` : combien de multiplications d'attention et de multiplications linéaires sans cache et avec cache pour G = 7 ? (Réponse : attention 3 360 contre 880 ; linéaires 6 272 contre 1 280.)
3. Trouver le bug : dans une variante de `generer_avec_cache`, l'appel devient `pas_de_decodage(produits[-1], len(prompt), cache, modele, compteur)`. Que génère le modèle jouet, et pourquoi l'`assert` du bloc 1 échoue-t-il ? (Réponse : « est de de de de de » au lieu de « est de de . . par » ; tous les tokens générés reçoivent l'embedding de la même position, le calcul n'est plus celui du recalcul complet, où chaque token a sa propre position.)

## Pour aller plus loin

FlashAttention (étape 33) calcule le prefill sans stocker la matrice des scores. PagedAttention range le cache KV en blocs de taille fixe, et le batching continu remplit chaque place libérée d'un lot dès l'itération suivante (étape 72 bis). Le décodage spéculatif vérifie plusieurs tokens proposés en une seule passe, ce qui coûte à peu près un pas de décodage puisque celui-ci est limité par la mémoire (étape 72 ter). Les variantes MQA et GQA (étape 34) réduisent le cache, et sa quantification en 8 ou 4 bits aussi (étape 73 bis). Le prefill découpé en morceaux (chunked prefill) intercale un long prompt avec les pas de décodage des autres requêtes ; certains déploiements séparent même le prefill et le décodage sur des machines différentes, puisque l'un est limité par le calcul et l'autre par la mémoire. Côté API, le streaming des arguments d'outils permet de commencer à lire un long JSON avant sa fin, mais il faut toujours le valider avant d'exécuter l'outil.

> Étape 33 bis du parcours · Prérequis : [Transformer et attention](<33-Transformer-et-Attention-Deroule-Numerique.md>) · Suite : [Attention multi-têtes](<34-Attention-Multi-Tetes.md>)
