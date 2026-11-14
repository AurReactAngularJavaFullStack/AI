# Étape 35 — Positional Encoding — Injection de l'Ordre Séquentiel

> Étape 35 du parcours · Prérequis : [Attention multi-têtes](<34-Attention-Multi-Tetes.md>) · Suite : [Normalisation de couche](<36-Normalisation-de-Couche.md>)

## Définition

L'encodage de position est le mécanisme qui écrit dans chaque vecteur de token **où** ce token se trouve dans la séquence. Il est nécessaire parce que l'attention seule est insensible à l'ordre : permuter les tokens ne fait que permuter les sorties (étape 31, point 4). La version sinusoïdale de l'article d'origine associe à chaque position un vecteur de sinus et de cosinus de fréquences géométriquement décroissantes : la première paire de coordonnées tourne vite, la dernière très lentement. Ce vecteur est **ajouté** à l'embedding du token avant la première couche. Sa propriété centrale est démontrée ici : décaler la position de k revient à multiplier le vecteur par une matrice Tₖ qui ne dépend que de k, une rotation par paire de coordonnées.

## Rôle dans un agent

L'encodage de position agit à l'entrée du LLM, avant toute attention, pendant l'étape **décider** de la boucle percevoir → décider → agir → observer. Le développeur d'agent ne le code pas, mais il en dépend chaque fois qu'il fabrique un prompt : le modèle ne connaît l'ordre des mots que par lui (et, dans un décodeur, par le masque causal), il ne voit ni l'alignement visuel d'un tableau, ni l'ordre chronologique des événements, ni le sens de lecture d'un PDF arabe, seulement l'ordre des tokens. Il en dépend aussi quand il choisit un modèle : au-delà des longueurs vues à l'entraînement, les vecteurs de position prennent des valeurs que le modèle n'a jamais rencontrées, et rien ne garantit la qualité des réponses.

## Équation complète

Fréquence de la paire i (de i = 0 à i = d/2 − 1), en radians par token :

$$
\omega_i = 10000^{-2i/d}
$$

Coordonnées paires et impaires du vecteur de position :

$$
PE_{(pos,\, 2i)} = \sin(pos \cdot \omega_i)
$$

$$
PE_{(pos,\, 2i+1)} = \cos(pos \cdot \omega_i)
$$

L'ancienne écriture

$$
\sin\left(pos / 10000^{2i/d}\right)
$$

est la même, puisque diviser par

$$
10000^{2i/d}
$$

revient à multiplier par ωᵢ. Entrée de la première couche, pour le token wₚₒₛ placé en position pos :

$$
X_{pos} = E_{w_{pos}} + PE_{pos}
$$

Bloc de rotation d'angle θ, puis matrice de translation, diagonale par blocs :

$$
R(\theta) = \begin{bmatrix} \cos\theta & \sin\theta \\ -\sin\theta & \cos\theta \end{bmatrix}
$$

$$
T_k = \operatorname{diag}\big( R(k\,\omega_0),\; R(k\,\omega_1),\; \ldots,\; R(k\,\omega_{d/2-1}) \big)
$$

Propriété de translation, pour toute position pos :

$$
PE_{pos+k} = T_k \cdot PE_{pos}
$$

Produit scalaire de deux positions séparées de k :

$$
PE_{p} \cdot PE_{p+k} = \sum_{i=0}^{d/2-1} \cos(k\,\omega_i)
$$

## Décryptage des symboles

$$
pos
$$

**Sens :** position du token dans la séquence, à partir de 0 · **Type / plage :** entier ≥ 0 · **Variable Python :** `pos`

$$
d
$$

**Sens :** largeur des vecteurs, notée (formule ci-dessous) aux étapes 33 et 34 · **Type / plage :** entier ≥ 1, pair en pratique · **Variable Python :** `d`

$$
d_{model}
$$

$$
i
$$

**Sens :** numéro de la paire (sinus, cosinus) · **Type / plage :** entier de 0 à d/2 − 1 · **Variable Python :** `i`, ou `j // 2`

$$
\omega_i
$$

**Sens :** fréquence angulaire de la paire i : 1 radian par token pour i = 0, de plus en plus petite ensuite · **Type / plage :** réel dans ]0 ; 1] · **Variable Python :** `omega(i, d)`

$$
\lambda_i
$$

**Sens :** longueur d'onde : 2π / ωᵢ tokens par tour complet · **Type / plage :** réel ≥ 2π · **Variable Python :** `longueur_onde(i, d)`

$$
PE_{pos}
$$

**Sens :** vecteur de position · **Type / plage :** vecteur de taille d, coordonnées dans [−1, 1] · **Variable Python :** `encodage_position(pos, d)`

$$
E_{w}
$$

**Sens :** embedding du token w · **Type / plage :** vecteur de taille d · **Variable Python :** `chien`, `mord`…

$$
X_{pos}
$$

**Sens :** entrée de la première couche : embedding plus position · **Type / plage :** vecteur de taille d · **Variable Python :** `ajouter_pe(X)`

$$
k
$$

**Sens :** décalage, en tokens · **Type / plage :** entier · **Variable Python :** `k`

$$
R(\theta)
$$

**Sens :** rotation 2 × 2 d'angle θ · **Type / plage :** matrice 2 × 2 · **Variable Python :** blocs de `matrice_translation`

$$
T_k
$$

**Sens :** matrice de translation : un bloc R(k ωᵢ) par paire · **Type / plage :** matrice d × d · **Variable Python :** `matrice_translation(k, d)`

L'ancienne version utilisait Tₖ sans jamais le définir ; il l'est désormais ci-dessus.

## Démonstration

### 1. La forme exponentielle du code est la même formule

Le code PyTorch d'origine calcule `exp((2i) * (-log(10000) / d))`. Comme aˣ = eˣˡⁿᵃ pour tout a > 0 :

$$
e^{-2i \ln(10000) / d} = 10000^{-2i/d} = \omega_i
$$

Multiplier la position par ce facteur revient donc à la diviser par

$$
10000^{2i/d}
$$

Sinus sur les colonnes paires et cosinus sur les colonnes impaires sont exactement les deux formules. L'ancienne version affirmait que cette forme servait à éviter un sous-débordement ; c'est faux. Le plus petit facteur, pour d = 512, vaut

$$
\omega_{255} = 10000^{-510/512} \approx 1{,}0366 \times 10^{-4} ,
$$

très loin de la plus petite valeur représentable en double précision (environ 2,2 × 10⁻³⁰⁸), et les deux écritures donnent le même nombre à 10⁻¹² près en valeur relative. La forme `exp`/`log` n'est qu'un procédé de calcul commode : elle produit toutes les fréquences d'un coup à partir d'un `arange`.

### 2. Un décalage de k est une rotation par paire : PEₚₒₛ₊ₖ = Tₖ · PEₚₒₛ

On fixe une paire i et l'on pose a = pos ωᵢ et b = k ωᵢ. Les formules d'addition donnent :

$$
\sin(a + b) = \cos b \, \sin a + \sin b \, \cos a
$$

$$
\cos(a + b) = -\sin b \, \sin a + \cos b \, \cos a
$$

Comme (pos + k) ωᵢ = a + b, ces deux lignes s'écrivent en une seule multiplication matricielle :

$$
\begin{bmatrix} \sin((pos+k)\,\omega_i) \\ \cos((pos+k)\,\omega_i) \end{bmatrix} = \begin{bmatrix} \cos(k\,\omega_i) & \sin(k\,\omega_i) \\ -\sin(k\,\omega_i) & \cos(k\,\omega_i) \end{bmatrix} \begin{bmatrix} \sin(pos\,\omega_i) \\ \cos(pos\,\omega_i) \end{bmatrix}
$$

La matrice du milieu est R(k ωᵢ). En plaçant ces blocs sur la diagonale, une paire après l'autre, on obtient Tₖ, et PEₚₒₛ₊ₖ = Tₖ · PEₚₒₛ. Le point essentiel est que Tₖ ne dépend que de k et de d, **pas de pos** : la même matrice décale n'importe quelle position de k tokens. Trois propriétés en découlent. R(θ)ᵀ R(θ) = I, parce que cos²θ + sin²θ = 1 : Tₖ est une rotation et conserve les normes. R(α) R(β) = R(α + β), par les mêmes formules d'addition : Tₖ Tₘ = Tₖ₊ₘ. Et T₋ₖ = Tₖᵀ : reculer de k est la transposée d'avancer de k.

Vérification à la main, avec d = 4, donc ω₀ = 1 et

$$
\omega_1 = 10000^{-1/2} = 0{,}01
$$

$$
PE_2 = [\sin 2 ; \cos 2 ; \sin 0{,}02 ; \cos 0{,}02] = [0{,}909297 ; -0{,}416147 ; 0{,}019999 ; 0{,}999800] .
$$

La première ligne de T₃ vaut

$$
[\cos 3 ; \sin 3 ; 0 ; 0] = [-0{,}989992 ; 0{,}141120 ; 0 ; 0] ,
$$

d'où une première coordonnée

$$
-0{,}989992 \times 0{,}909297 + 0{,}141120 \times (-0{,}416147) = -0{,}900197 - 0{,}058727 = -0{,}958924 ,
$$

qui est bien sin 5. Le programme vérifie les quatre coordonnées, puis 12 couples (pos, k) en dimension 16.

### 3. Toutes les positions ont la même norme

Pour d pair, chaque paire contribue sin²(pos ωᵢ) + cos²(pos ωᵢ) = 1, donc :

$$
\lVert PE_{pos} \rVert^2 = \frac{d}{2}
$$

Aucune position ne « parle plus fort » qu'une autre : pour d = 16, le programme trouve exactement 8 pour les positions 0 à 200. C'est la réponse au problème qu'évoquait l'ancienne version : écrire l'indice 8 000 dans une case ferait dominer la position sur toutes les autres coordonnées, alors qu'ici chaque coordonnée reste entre −1 et 1.

### 4. Le produit scalaire de deux positions ne dépend que de leur écart

Avec

$$
\cos(a - b) = \cos a \cos b + \sin a \sin b ,
$$

appliqué à a = (p + k) ωᵢ et b = p ωᵢ :

$$
PE_p \cdot PE_{p+k} = \sum_{i} \big[ \sin(p\,\omega_i) \sin((p+k)\,\omega_i) + \cos(p\,\omega_i) \cos((p+k)\,\omega_i) \big] = \sum_{i} \cos(k\,\omega_i)
$$

Le résultat ne dépend pas de p et ne change pas si l'on remplace k par −k. Pour d = 4 et k = 3, il vaut cos 3 + cos 0,03 ≈ 0,009558, que l'on parte de p = 0, 2, 10 ou 500. C'est cette propriété qui permet, en principe, à des projections apprises de reconnaître un écart (« trois tokens plus loin ») où qu'il se trouve dans le texte.

### 5. La paire i = 0 est la plus rapide, la dernière la plus lente

$$
\omega_i = 10000^{-2i/d}
$$

décroît quand i augmente, parce que l'exposant −2i/d diminue. La longueur d'onde λᵢ = 2π/ωᵢ croît donc avec i :

- pour i = 0, ω₀ = 1 et λ₀ = 2π ≈ 6,28 tokens : c'est l'onde la plus **rapide**, qui fait un tour complet en un peu plus de six tokens ;
- pour d = 512 et la dernière paire, i = 255,

$$
\lambda_{255} = 2\pi \cdot 10000^{510/512} \approx 60\,611
$$

tokens : c'est l'onde la plus **lente**.

L'ancienne version disait l'inverse (« i = 0 oscille lentement, la dernière paire oscille vite ») ; c'est corrigé. Deux positions voisines diffèrent nettement sur les ondes rapides (petits i) et se ressemblent sur les ondes lentes (grands i) ; deux positions éloignées diffèrent aussi sur les ondes lentes. Le modèle peut ainsi lire « juste à côté » et « beaucoup plus loin » sans table de toutes les distances.

### 6. Aucune garantie au-delà des longueurs vues à l'entraînement

Les formules donnent un vecteur pour n'importe quelle position, et la propriété du point 2 vaut pour toutes. Mais ce sont des propriétés des **vecteurs**, pas du **modèle** : ses poids ont été appris sur les positions qu'il a vues. Pour d = 512, la coordonnée la plus lente, sin(pos · ω₂₅₅), ne dépasse jamais 0,4120 sur les positions 0 à 4 096 ; à la position 16 384, elle vaut 0,9919, une valeur qu'un modèle entraîné sur 4 096 tokens n'a jamais rencontrée. L'ancienne phrase « les sinus ont cette garantie dès la première étape, même pour une position plus longue que celles vues à l'entraînement » est donc exagérée : en pratique, les modèles à encodage sinusoïdal se dégradent nettement au-delà de leur longueur d'entraînement (constat expérimental de Press et al., 2022), et l'extrapolation se mesure, elle ne se suppose pas.

### 7. Pourquoi il faut un encodage de position

Le programme fait passer deux phrases de mêmes mots, « chien mord homme » et « homme mord chien », dans une attention sans projection ni masque (Q = K = V = X). Sans encodage de position, la sortie de « chien » est exactement la même, qu'il soit sujet (position 0) ou objet (position 2), parce que l'attention ne dépend pas de l'ordre des couples clé-valeur (étape 31, point 4). Avec l'encodage ajouté, les deux sorties diffèrent de 0,9371 sur leur plus grande coordonnée : le modèle peut distinguer qui mord qui. Dans un décodeur, le masque causal apporte à lui seul un peu d'information d'ordre — un token ne voit que ce qui le précède (étape 33) —, mais pas de mesure explicite des distances.

### 8. Le cas d'une dimension impaire

Si d est impair, la dernière colonne vaut

$$
\sin(pos \cdot \omega_{(d-1)/2})
$$

et n'a pas de cosinus partenaire. Le vecteur se calcule sans difficulté — `encodage_position` le fait —, mais la propriété de translation n'est plus exacte sur cette coordonnée, puisque sin((pos+k) ω) demande cos(pos ω), absent du vecteur ; `matrice_translation` refuse donc un d impair. Le code PyTorch d'origine, lui, plantait : `pe[:, 1::2]` a ⌊ d/2 ⌋ colonnes, mais `div_term` en a ⌈ d/2 ⌉. L'extrait corrigé ne garde que les ⌊ d/2 ⌋ premières fréquences pour les cosinus. En pratique, on choisit d pair.

## Effets et comportement

- **Paires rapides, paires lentes.** Les premières coordonnées distinguent les voisins immédiats, les dernières les grandes distances (point 5).
- **Une norme constante.** La position ne domine jamais le sens du mot par sa taille (point 3).
- **Un écart, une signature.** Le produit scalaire de deux positions ne dépend que de leur écart (point 4).
- **L'addition mélange les deux informations.**

$$
X_{pos} = E_w + PE_{pos}
$$

n'est pas réversible au sens strict ; elle fonctionne parce que les projections

$$
W_Q
$$

et

$$
W_K
$$

qui suivent peuvent apprendre à lire plutôt les directions du sens ou plutôt celles de la position. L'article d'origine multiplie aussi les embeddings par

$$
\sqrt{d_{model}}
$$

avant l'addition, pour que les deux termes aient des tailles comparables.
- **Au-delà de la longueur d'entraînement, des valeurs inédites.** Le modèle n'est plus en terrain connu (point 6).

## Du symbole au code Python

$$
\omega_i
$$

**Variable ou fonction :** `omega(i, d)`

$$
PE_{pos}
$$

**Variable ou fonction :** `encodage_position(pos, d)`

$$
T_k
$$

**Variable ou fonction :** `matrice_translation(k, d)`

$$
T_k \cdot PE_{pos}
$$

**Variable ou fonction :** `appliquer(T, v)`

$$
\lambda_i
$$

**Variable ou fonction :** `longueur_onde(i, d)`

$$
E_w + PE_{pos}
$$

**Variable ou fonction :** `ajouter_pe(X)`, dans `main`

### Déroulé, ligne par ligne

**`omega(i, d)`** renvoie `10000.0 ** (-2 * i / d)`. Pour `d = 4` : `omega(0, 4) = 1.0` et `omega(1, 4) = 0.01`. Pour `d = 512` : `omega(255, 512)` vaut `1.0366e-04`.

**`encodage_position(pos, d)`**. La garde refuse `d < 1` et une position négative (`ValueError`). La compréhension parcourt les colonnes `j` : la paire est `j // 2` ; une colonne paire reçoit le sinus, une colonne impaire le cosinus. Pour `pos = 2` et `d = 4`, on obtient `[0.909297, -0.416147, 0.019999, 0.9998]`. Si `d` est impair, la dernière colonne est un sinus seul, et rien ne plante (point 8).

**`matrice_translation(k, d)`**.

- `if d % 2 != 0` : pour un `d` impair, la dernière colonne n'a pas de partenaire et Tₖ n'existe pas ; `ValueError`.
- Pour chaque paire `i`, `c` et `s` valent cos(k ωᵢ) et sin(k ωᵢ) ; pour `k = 3` et `i = 0`, `c = -0.989992` et `s = 0.14112`.
- Les quatre affectations remplissent le bloc R(k ωᵢ) aux lignes et colonnes `2i` et `2i + 1` ; les commentaires rappellent la formule d'addition que chaque ligne encode. Tout le reste de la matrice vaut 0.

**`appliquer(T, v)`** fait le produit matrice-vecteur ; **`produit_matrices(A, B)`** le produit de deux matrices, pour tester Tₖᵀ Tₖ = I et T₂ T₃ = T₅ ; **`ecart_max(u, v)`** renvoie le plus grand écart entre deux vecteurs.

**`longueur_onde(i, d)`** renvoie `2 * math.pi / omega(i, d)` : 6,2832 tokens pour `i = 0`, 60 611,5 pour `i = 255` en dimension 512.

**`auto_attention(X)`**. L'attention de l'étape 31 sans projection ni masque : scores 𝐱ᵢ · 𝐱ⱼ / √d, softmax stable, moyenne pondérée des lignes de `X`. Elle ne sert qu'à l'expérience du point 7.

**`main()`**, bloc par bloc.

1. d = 4 : `appliquer(T3, pe2)` redonne `PE(5) = [-0.958924, 0.283662, 0.049979, 0.99875]` à 10⁻¹² près, et la première ligne de T₃ vaut `[-0.989992, 0.14112, …]` (point 2).
2. d = 16 : 4 positions fois 3 décalages, chaque fois à 10⁻⁹ près ; puis T₂ᵀ T₂ = I et T₂ T₃ = T₅ à 10⁻¹² près.
3. Les normes au carré des positions 0 à 200 valent toutes 8, soit 16/2 (point 3).
4. `PE(p) · PE(p + 3)` vaut 0,009558 pour `p = 0`, 2, 10 et 500 (point 4).
5. Les 256 longueurs d'onde de d = 512 croissent strictement, de 2π à 60 611,5 tokens ; la forme `exp`/`log` redonne ω₂₅₅ (points 1 et 5).
6. Le maximum de la coordonnée la plus lente sur les positions 0 à 4 096 vaut 0,4120 ; à 16 384, elle vaut 0,9919 (point 6).
7. `ajouter_pe` additionne à chaque embedding le vecteur de sa position ; l'écart entre les deux sorties de « chien » est nul sans encodage et vaut 0,9371 avec (point 7). Les `assert` suivants vérifient les nombres des cas d'usage.
8. `encodage_position(3, 5)` renvoie cinq valeurs dont la dernière est un sinus seul ; `matrice_translation(1, 5)` et `encodage_position(0, 0)` lèvent `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`omega(i, d)`** — Cette fonction est l'horloger qui règle la vitesse de chacune des aiguilles de l'encodage : elle reçoit le numéro i d'une paire de colonnes et la dimension d, et renvoie la fréquence angulaire ωᵢ = 10000 puissance (−2i / d), exprimée en radians par token. La première aiguille tourne le plus vite, avec ω₀ = 1, et chaque paire suivante tourne plus lentement : pour d = 4, `omega(1, 4)` vaut 0,01, et pour d = 512 la paire 255 ne fait plus qu'environ 1,0366 × 10⁻⁴ radian par token. Toutes les autres fonctions du programme s'appuient sur elle.

**`matrice_translation(k, d)`** — Imaginons un mécanicien qui fabrique la clé capable d'avancer toutes les aiguilles d'une horloge de k crans d'un seul geste : la fonction reçoit le décalage k et la dimension d, lève une `ValueError` si d est impair, puisque la dernière colonne n'aurait pas de cosinus partenaire, puis remplit une matrice nulle d × d d'un bloc de rotation 2 × 2 par paire, avec cos(k ωᵢ) et sin(k ωᵢ) aux places dictées par les formules d'addition. Elle renvoie cette matrice Tₖ, qui ne dépend que de k et non de la position de départ ; pour k = 3 et d = 4, sa première ligne commence par −0,989992 et 0,14112.

**`appliquer(T, v)`** — Cette fonction est le geste qui tourne la clé dans la serrure : elle reçoit une matrice T et un vecteur v, calcule pour chaque ligne de T son produit scalaire avec v, et renvoie le vecteur obtenu, c'est-à-dire le produit T v. `main` s'en sert pour vérifier la propriété centrale du fichier : appliquer T₃ à l'encodage de la position 2 redonne, à 10⁻¹² près, l'encodage de la position 5, `[-0.958924, 0.283662, 0.049979, 0.99875]`, puis le même résultat pour douze couples position-décalage en dimension 16.

**`produit_matrices(A, B)`** — C'est l'assembleur qui enchaîne deux mécanismes pour en faire un seul : la fonction reçoit deux matrices A et B et renvoie leur produit A B, chaque case étant la somme des produits d'une ligne de A par une colonne de B. Elle ne vérifie pas les dimensions et ne sert qu'aux tests du bloc 2 de `main`, qui montrent que Tₖ est une rotation, puisque T₂ᵀ T₂ redonne l'identité à 10⁻¹² près, et que deux décalages se composent, puisque T₂ T₃ est égal à T₅.

**`ecart_max(u, v)`** — Cette petite fonction est l'inspecteur qui cherche la plus grosse différence entre deux copies d'un même document : elle reçoit deux vecteurs u et v, calcule la valeur absolue de l'écart coordonnée par coordonnée et renvoie le plus grand. Elle sert de juge dans presque tous les `assert` : elle doit rester sous 10⁻¹² entre T₃ · PE(2) et PE(5), sous 10⁻⁹ pour les douze couples du bloc 2, et vaut 0,9371 entre les deux sorties de « chien » une fois l'encodage de position ajouté.

**`longueur_onde(i, d)`** — On peut la voir comme le chronomètre qui dit combien de tokens il faut à l'aiguille i pour faire un tour complet : la fonction reçoit le numéro de paire i et la dimension d, et renvoie 2π / ωᵢ, en s'appuyant sur `omega`. La paire 0 boucle en 6,2832 tokens, soit 2π, tandis que la paire 255 de la dimension 512 ne fait un tour qu'en 60 611,5 tokens ; `main` vérifie que les 256 longueurs d'onde croissent strictement et que la paire 128 donne 628,3 tokens, un nombre repris dans les cas d'usage.

**`auto_attention(X)`** — Cette fonction rejoue une salle de réunion où chaque mot écoute tous les autres sans filtre ni masque : elle reçoit la matrice X des embeddings, qui sert à la fois de requêtes, de clés et de valeurs, calcule pour chaque ligne les scores xᵢ · xⱼ / √d, les passe dans une softmax stable et renvoie, ligne par ligne, la moyenne pondérée des lignes de X. Elle ne sert qu'à l'expérience du point 7 : sans encodage de position, « chien » sujet et « chien » objet obtiennent exactement la même sortie, ce qui montre que l'attention seule ignore l'ordre des mots.

**`main()`** — Le chef d'orchestre déroule les huit tableaux du fichier : il vérifie en dimension 4 que T₃ fait passer de la position 2 à la position 5, généralise en dimension 16 et contrôle rotation et composition, constate que la norme au carré des positions 0 à 200 vaut toujours 8, puis que PE(p) · PE(p + 3) vaut 0,009558 quelle que soit p. Il examine ensuite les longueurs d'onde de la dimension 512 et la forme `exp`/`log`, mesure 0,4120 contre 0,9919 au-delà de la longueur d'entraînement, compare « chien mord homme » et « homme mord chien », vérifie les nombres des cas d'usage et les refus d'entrées invalides ; il ne renvoie rien et n'annonce le succès que si tous les `assert` passent.

**`ajouter_pe(X)`** — Cette fonction interne vit dans `main`, au bloc 7, comme un placier qui épingle sur chaque invité le numéro de sa chaise : elle reçoit une matrice X d'embeddings, un par mot, et additionne à chaque ligne, coordonnée par coordonnée, l'encodage de position de son rang dans la phrase, calculé par `encodage_position` à la dimension de l'embedding. Elle renvoie la nouvelle matrice, embedding plus PE(pos) ligne par ligne ; passée à `auto_attention`, elle fait apparaître un écart de 0,9371 entre « chien » sujet et « chien » objet, là où l'écart était nul sans elle.

```python
"""Étape 35 — encodage de position sinusoïdal, matrice de translation T_k et ses propriétés, en Python pur."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

Matrice = list[list[float]]


def omega(i: int, d: int) -> float:
    """Fréquence angulaire de la paire i : ω_i = 10000^(−2i/d), en radians par token."""
    return 10000.0 ** (-2 * i / d)


def encodage_position(pos: int, d: int) -> list[float]:
    """PE(pos, 2i) = sin(pos·ω_i), PE(pos, 2i+1) = cos(pos·ω_i). d impair : la dernière colonne est un sinus seul."""
    if d < 1 or pos < 0:
        raise ValueError("il faut d >= 1 et pos >= 0")
    return [math.sin(pos * omega(j // 2, d)) if j % 2 == 0 else math.cos(pos * omega(j // 2, d)) for j in range(d)]


def matrice_translation(k: int, d: int) -> Matrice:
    """T_k : diagonale par blocs, un bloc de rotation 2×2 d'angle k·ω_i par paire (sin, cos)."""
    if d % 2 != 0:
        raise ValueError("T_k n'existe que pour d pair : la dernière colonne n'a pas de cosinus partenaire")
    T = [[0.0] * d for _ in range(d)]
    for i in range(d // 2):
        c, s = math.cos(k * omega(i, d)), math.sin(k * omega(i, d))
        a = 2 * i
        T[a][a], T[a][a + 1] = c, s        # sin((p+k)ω) =  cos(kω)·sin(pω) + sin(kω)·cos(pω)
        T[a + 1][a], T[a + 1][a + 1] = -s, c  # cos((p+k)ω) = −sin(kω)·sin(pω) + cos(kω)·cos(pω)
    return T


def appliquer(T: Matrice, v: list[float]) -> list[float]:
    return [sum(t * x for t, x in zip(ligne, v)) for ligne in T]


def produit_matrices(A: Matrice, B: Matrice) -> Matrice:
    return [[sum(A[i][l] * B[l][j] for l in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def ecart_max(u: list[float], v: list[float]) -> float:
    return max(abs(a - b) for a, b in zip(u, v))


def longueur_onde(i: int, d: int) -> float:
    """Nombre de tokens pour que la paire i fasse un tour complet : 2π / ω_i."""
    return 2 * math.pi / omega(i, d)


def auto_attention(X: Matrice) -> Matrice:
    """Attention sans projection ni masque (Q = K = V = X), pour l'expérience « chien mord homme »."""
    d = len(X[0])
    sortie = []
    for q in X:
        s = [sum(a * b for a, b in zip(q, k)) / math.sqrt(d) for k in X]
        m = max(s)
        e = [math.exp(x - m) for x in s]
        total = sum(e)
        sortie.append([sum(e[j] / total * X[j][c] for j in range(len(X))) for c in range(d)])
    return sortie


def main() -> None:
    print("1. Exemple d = 4 : T_3 · PE(2) = PE(5)")
    pe2, pe5 = encodage_position(2, 4), encodage_position(5, 4)
    T3 = matrice_translation(3, 4)
    image = appliquer(T3, pe2)
    print(f"  ω = [{omega(0, 4)}, {omega(1, 4)}] ; PE(2) = {[round(x, 6) for x in pe2]}")
    print(f"  T_3 · PE(2) = {[round(x, 6) for x in image]}")
    print(f"  PE(5)       = {[round(x, 6) for x in pe5]}   (écart max < 1e-12)")
    assert omega(0, 4) == 1.0 and abs(omega(1, 4) - 0.01) < 1e-15
    assert [round(x, 6) for x in pe2] == [0.909297, -0.416147, 0.019999, 0.9998]
    assert [round(x, 6) for x in pe5] == [-0.958924, 0.283662, 0.049979, 0.99875]
    assert [round(x, 6) for x in T3[0][:2]] == [-0.989992, 0.14112] and ecart_max(image, pe5) < 1e-12

    print("2. d = 16 : la même T_k décale toute position ; rotation et composition")
    pire = 0.0
    for pos in (0, 7, 100, 1000):
        for k in (1, 5, 50):
            pire = max(pire, ecart_max(appliquer(matrice_translation(k, 16), encodage_position(pos, 16)),
                                       encodage_position(pos + k, 16)))
    T2, T5 = matrice_translation(2, 16), matrice_translation(5, 16)
    TtT = produit_matrices([list(c) for c in zip(*T2)], T2)
    ecart_orth = max(abs(TtT[i][j] - (1.0 if i == j else 0.0)) for i in range(16) for j in range(16))
    ecart_comp = max(abs(a - b) for la, lb in zip(produit_matrices(T2, matrice_translation(3, 16)), T5)
                     for a, b in zip(la, lb))
    print("  T_k·PE(pos) = PE(pos+k) à 1e-9 près pour 12 couples (pos, k) ; T_2ᵀT_2 = I et T_2·T_3 = T_5 à 1e-12 près")
    assert pire < 1e-9 and ecart_orth < 1e-12 and ecart_comp < 1e-12

    print("3. Norme constante : ‖PE(pos)‖² = d/2")
    normes = [sum(x * x for x in encodage_position(pos, 16)) for pos in range(201)]
    print(f"  d = 16, pos = 0…200 : min = {min(normes):.12f}, max = {max(normes):.12f}")
    assert all(abs(n - 8.0) < 1e-12 for n in normes)

    print("4. PE(p) · PE(p + 3) ne dépend pas de p (d = 4)")
    produits = [sum(a * b for a, b in zip(encodage_position(p, 4), encodage_position(p + 3, 4))) for p in (0, 2, 10, 500)]
    print(f"  p = 0, 2, 10, 500 : {[round(x, 6) for x in produits]} ; cos 3 + cos 0.03 = {math.cos(3) + math.cos(0.03):.6f}")
    assert all(abs(x - (math.cos(3) + math.cos(0.03))) < 1e-12 for x in produits) and round(produits[0], 6) == 0.009558

    print("5. Longueurs d'onde pour d = 512 : la paire i = 0 est la plus RAPIDE")
    ondes = [longueur_onde(i, 512) for i in range(256)]
    print(f"  i = 0 : {ondes[0]:.4f} tokens ; i = 1 : {ondes[1]:.4f} ; i = 255 : {ondes[255]:.1f} tokens")
    assert abs(ondes[0] - 2 * math.pi) < 1e-12 and all(a < b for a, b in zip(ondes, ondes[1:]))
    assert round(ondes[255]) == 60611
    w_min = omega(255, 512)
    forme_exp = math.exp(-2 * 255 * math.log(10000.0) / 512)
    print(f"  plus petit facteur ω_255 = {w_min:.4e} ; forme exp/log = {forme_exp:.4e} (aucun sous-débordement)")
    assert abs(forme_exp - w_min) / w_min < 1e-12 and w_min > 1e-4 > sys.float_info.min

    print("6. Au-delà des longueurs d'entraînement : des valeurs jamais vues")
    vu_max = max(math.sin(pos * w_min) for pos in range(4097))
    nouveau = math.sin(16_384 * w_min)
    print(f"  coordonnée la plus lente : max sur pos ≤ 4096 = {vu_max:.4f} ; à pos = 16 384 : {nouveau:.4f}")
    assert round(vu_max, 4) == 0.412 and round(nouveau, 4) == 0.9919 and nouveau > vu_max

    print("7. « chien mord homme » contre « homme mord chien » (attention sans projection)")
    chien, mord, homme = [1.0, 0.0, 0.0, 0.5], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.5]
    A, B = [chien, mord, homme], [homme, mord, chien]

    def ajouter_pe(X: Matrice) -> Matrice:
        return [[x + y for x, y in zip(v, encodage_position(p, len(v)))] for p, v in enumerate(X)]

    sans = ecart_max(auto_attention(A)[0], auto_attention(B)[2])
    avec = ecart_max(auto_attention(ajouter_pe(A))[0], auto_attention(ajouter_pe(B))[2])
    print(f"  sortie de « chien », sujet contre objet : écart nul (< 1e-12) sans PE, {avec:.4f} avec PE")
    assert sans < 1e-12 and round(avec, 4) == 0.9371

    # Nombres des cas d'usage : 50 lignes de 40 tokens ; fin de service, 7 ans, base 10 000 AED (21 j puis 30 j par an)
    assert 50 * 40 == 2_000 and 5 * 21 * 10_000 / 30 + 2 * 30 * 10_000 / 30 == 55_000
    assert round(longueur_onde(128, 512), 1) == 628.3

    print("8. d impair et entrées invalides")
    pe_impair = encodage_position(3, 5)
    print(f"  d = 5 : PE(3) = {[round(x, 6) for x in pe_impair]} (dernière colonne : un sinus seul)")
    assert len(pe_impair) == 5 and abs(pe_impair[4] - math.sin(3 * omega(2, 5))) < 1e-15
    for appel in (lambda: matrice_translation(1, 5), lambda: encodage_position(0, 0)):
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
1. Exemple d = 4 : T_3 · PE(2) = PE(5)
  ω = [1.0, 0.01] ; PE(2) = [0.909297, -0.416147, 0.019999, 0.9998]
  T_3 · PE(2) = [-0.958924, 0.283662, 0.049979, 0.99875]
  PE(5)       = [-0.958924, 0.283662, 0.049979, 0.99875]   (écart max < 1e-12)
…
  d = 16, pos = 0…200 : min = 8.000000000000, max = 8.000000000000
…
  p = 0, 2, 10, 500 : [0.009558, 0.009558, 0.009558, 0.009558] ; cos 3 + cos 0.03 = 0.009558
5. Longueurs d'onde pour d = 512 : la paire i = 0 est la plus RAPIDE
  i = 0 : 6.2832 tokens ; i = 1 : 6.5134 ; i = 255 : 60611.5 tokens
  plus petit facteur ω_255 = 1.0366e-04 ; forme exp/log = 1.0366e-04 (aucun sous-débordement)
…
  coordonnée la plus lente : max sur pos ≤ 4096 = 0.4120 ; à pos = 16 384 : 0.9919
…
  sortie de « chien », sujet contre objet : écart nul (< 1e-12) sans PE, 0.9371 avec PE
…
  d = 5 : PE(3) = [0.14112, -0.989992, 0.075285, 0.997162, 0.001893] (dernière colonne : un sinus seul)
  ValueError : T_k n'existe que pour d pair : la dernière colonne n'a pas de cosinus partenaire
…
OK — toutes les vérifications sont passées.
```

### La version PyTorch (extrait corrigé)

L'ancien bloc dépendait de PyTorch et plantait pour un `d_model` impair. Le voici en extrait, corrigé :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`positional_encoding(max_len, d_model)`** — Cette fonction imprime d'un seul coup tout le registre des numéros de place, comme un imprimeur qui tire en une passe les étiquettes de toutes les chaises d'une salle : elle reçoit le nombre maximal de positions et la dimension du modèle, crée un tableau nul de `max_len` lignes et `d_model` colonnes, une colonne des positions 0, 1, 2…, puis les fréquences ωᵢ par la forme exponentielle exp(−2i ln 10000 / d), qui évite toute puissance démesurée. Elle remplit les colonnes paires de sinus et les colonnes impaires de cosinus, en ne gardant que les `d_model // 2` premières fréquences pour ces dernières, ce qui corrige le plantage de l'ancien bloc quand la dimension est impaire, et renvoie le tableau complet, l'équivalent vectorisé de `encodage_position` du programme précédent.

```python
# [extrait] — version PyTorch corrigée (d_model impair accepté), non exécutée par le harnais
import math

import torch


def positional_encoding(max_len, d_model):
    pe = torch.zeros(max_len, d_model)
    position = torch.arange(0, max_len).unsqueeze(1).float()
    div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))  # les ω_i
    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term[: d_model // 2])  # d impair : une colonne cosinus de moins
    return pe
```

`position` est la colonne 0, 1, 2, … ; `arange(0, d_model, 2)` donne les indices pairs 0, 2, 4, …, c'est-à-dire 2i ; `div_term` contient les ωᵢ (point 1). Le découpage `0::2` sélectionne les colonnes paires, `1::2` les impaires.

## Squelette algorithmique

L'encodage sinusoïdal attribue à chaque position un vecteur fait de paires (sinus, cosinus) de fréquences décroissantes. Le programme vérifie aussi la propriété clé : décaler toutes les positions de k revient à appliquer une rotation fixe, qui ne dépend que de k.

```text
ALGORITHME EncodagePosition
ENTRÉES : position pos, dimension d (paire)
SORTIE  : le vecteur PE(pos) de dimension d

  POUR i DE 0 À d/2 − 1 FAIRE
      ωᵢ ← 10000^(−2i / d)                          (fréquence de la paire i)
      PE[2i]     ← sin(pos × ωᵢ)
      PE[2i + 1] ← cos(pos × ωᵢ)
  FIN POUR
  RETOURNER PE

ALGORITHME TranslationParRotation
ENTRÉES : décalage k, dimension d
  T ← matrice nulle d × d
  POUR i DE 0 À d/2 − 1 FAIRE
      bloc 2 × 2 de la paire i ← [[cos(k ωᵢ), sin(k ωᵢ)], [−sin(k ωᵢ), cos(k ωᵢ)]]
  FIN POUR
  PROPRIÉTÉ : T × PE(pos) = PE(pos + k) pour toute position pos
```

**Complexité.** Un encodage coûte O(d) ; une table de L positions O(L × d), calculée une fois et ajoutée aux embeddings. La matrice de translation est diagonale par blocs : l'appliquer coûte O(d) si l'on exploite les blocs, O(d²) si on la traite comme une matrice pleine, comme le fait le programme pour rester lisible.

**Du squelette au code.** `omega` donne ωᵢ, `encodage_position` la première boucle, `longueur_onde` la période 2π / ωᵢ de chaque paire, `matrice_translation` la seconde boucle, `appliquer` et `produit_matrices` la vérification de la propriété, et `ecart_max` mesure l'écart entre T × PE(pos) et PE(pos + k). `auto_attention` montre qu'en l'absence de position, l'attention ne distingue pas deux ordres de mots. La fonction NumPy `positional_encoding`, plus bas, construit la table entière.

## Cas d'usage réels aux Émirats

Les volumes de tokens sont des ordres de grandeur illustratifs ; les nombres issus d'une formule sont vérifiés par le programme.

### Assurance — « le tiers a heurté l'assuré » n'est pas « l'assuré a heurté le tiers »

Un assureur auto et santé fait analyser par un agent les déclarations d'accident, rédigées en arabe ou en anglais. Un premier prototype réduisait chaque déclaration à une liste de mots-clés triés et dédoublonnés avant de l'envoyer au modèle, pour économiser des tokens : « assuré, heurté, tiers, rond-point ». Cette liste est la même que la déclaration dise « le tiers a heurté l'assuré » ou « l'assuré a heurté le tiers ». Or l'ordre n'atteint le modèle que par l'encodage de position : dans l'expérience du point 7, la représentation de « chien » est exactement la même qu'il soit sujet ou objet quand on retire l'encodage, et ne diffère (de 0,9371) qu'avec lui. Trier les mots revient à jeter cette information avant même que le modèle la reçoive. L'agent envoie donc les phrases complètes, dans leur ordre, et demande une extraction structurée des rôles (`conducteur_qui_heurte`, `conducteur_heurte`, `phrase_source`), vérifiée par un gestionnaire quand elle décide de la responsabilité. Sans cette correction, l'agent peut inverser les responsabilités et proposer une indemnisation au mauvais conducteur, alors que l'assureur, supervisé par la CBUAE, doit justifier chaque décision. L'indicateur suivi est le taux d'attributions de responsabilité confirmées par les gestionnaires.

### Immobilier — un tableau de 60 transactions envoyé comme du texte aligné

Une agence et un promoteur à Dubaï et Abu Dhabi font comparer par un agent 60 transactions récentes enregistrées au DLD : tour, étage, surface en sqft, prix en AED/sqft. Exporté tel quel, le tableau devient du texte aligné par des espaces : avec des lignes d'environ 40 tokens, la valeur de prix de la 50e ligne se trouve à environ 2 000 tokens de l'en-tête « prix AED/sqft ». Le modèle ne voit pas l'alignement visuel, seulement des positions ; et comme le produit scalaire de deux positions ne dépend que de leur écart (point 4), l'écart entre l'en-tête et la valeur change à chaque ligne : « même colonne » n'est pas un motif simple à reconnaître. L'agent sérialise donc chaque transaction avec des noms de champs explicites, une ligne par transaction, du type `{"tour": "T2", "etage": 31, "surface_sqft": 1180, "prix_aed_sqft": 1450}` : le sens de chaque nombre ne dépend plus de sa position. Il ajoute ensuite par un outil, et non de tête, les frais de transfert DLD de 4 % de la valeur du bien. Sans cette sérialisation, l'agent peut prendre une surface pour un prix et produire une estimation absurde, sans aucun message d'erreur. L'indicateur suivi est la part des valeurs correctement relues sur un jeu de tableaux de test.

### Secteur public — l'ordre logique d'un formulaire arabe

Une entité de services publics en ligne accessible par UAE Pass reçoit des formulaires PDF bilingues et fait extraire leurs champs par un agent : nom, Emirates ID (15 chiffres commençant par 784), adresse. Certains extracteurs de texte PDF restituent l'arabe dans l'ordre **visuel**, de gauche à droite à l'écran, et non dans l'ordre **logique** de lecture : les mots, voire les lettres, arrivent inversés. Pour le modèle, une séquence inversée est une autre phrase, puisque l'ordre ne lui parvient que par les positions des tokens (point 7). L'équipe ajoute donc une étape déterministe avant le modèle : remise du texte dans l'ordre logique, puis normalisation de l'arabe (alef, ta marbuta, diacritiques), et un test qui compare l'extraction de formulaires de référence au texte attendu. Les numéros d'Emirates ID sont contrôlés par du code (format seulement), jamais confiés au modèle. Sans cette étape, l'agent lit des noms à l'envers, crée des doublons de dossiers et oblige les usagers à recommencer leur démarche ; comme ces formulaires contiennent des données personnelles, chaque nouvelle tentative les fait aussi circuler davantage, à l'encontre de la minimisation voulue par la PDPL. L'indicateur suivi est la part des champs correctement extraits sur les formulaires de référence, en arabe et en anglais.

### Banque — un dossier plus long que ce que le modèle a vu à l'entraînement

Une banque de détail de Dubaï fait analyser par un agent des dossiers de crédit complets, qui atteignent parfois 16 000 tokens, avec un modèle dont la documentation indique un entraînement sur des contextes de 4 096 tokens (chiffres illustratifs). Les vecteurs de position existent pour les 16 000 positions, mais le point 6 montre ce que cela cache : pour d = 512, la coordonnée la plus lente ne dépasse pas 0,4120 sur les 4 096 premières positions et atteint 0,9919 à la position 16 384, une valeur que le modèle n'a jamais vue pendant son entraînement. L'équipe ne suppose donc pas que le modèle « extrapolera » : elle respecte la fenêtre documentée, découpe le dossier en sections cohérentes (identité, revenus, engagements), fait calculer par un outil le ratio d'endettement — toutes les mensualités, y compris la nouvelle, rapportées au salaire, sous le plafond de 50 % de la CBUAE — et ne transmet au modèle que les résultats. Si elle veut un contexte plus long, elle choisit un modèle entraîné sur de longs contextes et mesure la qualité par tranche de longueur avant de l'adopter. Sans cette discipline, la qualité des réponses peut chuter sur les dossiers les plus longs sans que rien ne le signale. L'indicateur suivi est la justesse des champs extraits, ventilée par tranche de longueur de dossier.

### RH — l'ordre des tokens n'est pas l'ordre des événements

Un cabinet RH multi-émirats fait reconstituer par un agent la carrière d'un salarié avant son départ, à partir d'e-mails, d'avenants et de lettres collés dans le prompt dans l'ordre où ils ont été trouvés. L'encodage de position renseigne le modèle sur l'ordre des tokens dans le prompt, pas sur l'ordre chronologique des événements : un avenant de 2019 placé après une lettre de 2023 apparaît « plus loin », sans être plus récent. Or le calcul de l'indemnité de fin de service en dépend : avec un salaire de base de 10 000 AED et 7 ans de service, 21 jours par an les cinq premières années puis 30 jours au-delà donnent 55 000 AED, et une date d'entrée mal lue change le résultat. L'agent extrait donc d'abord, par un outil, chaque document avec sa date, trie les événements chronologiquement et présente au modèle une frise numérotée avec des dates explicites ; le calcul de l'indemnité est fait par une fonction déterministe, à partir de la date d'entrée et du salaire de base. Sans ce tri, le modèle peut retenir comme date d'entrée celle du dernier document lu et sous-estimer l'ancienneté. L'indicateur suivi est l'écart entre les indemnités proposées par l'agent et celles validées par le service paie.

## Pièges et limites

- **Inverser rapide et lent.** La paire i = 0 est la plus rapide (6,28 tokens par tour) ; la dernière est la plus lente (environ 60 611 tokens pour d = 512).
- **Croire à une extrapolation garantie.** Les vecteurs existent pour toute position ; le modèle, lui, n'a appris que les positions qu'il a vues (point 6).
- **Oublier le cas d'une dimension impaire.** Le code PyTorch d'origine planterait ; la propriété de translation n'existe que par paires.
- **Confondre l'ordre des tokens avec un autre ordre.** L'encodage ne voit ni l'alignement visuel, ni la chronologie, ni le sens de lecture d'un PDF : ces ordres-là doivent être rendus explicites dans le texte.
- **Détruire l'ordre avant le modèle.** Trier, dédoublonner ou réduire un texte à des mots-clés supprime l'information que l'encodage aurait transmise.

### Exercice feuille blanche

1. Sans regarder le code, écrire `encodage_position` et `matrice_translation`, puis vérifier que T₃ · PE₂ = PE₅ pour d = 4.
2. Prédire, puis vérifier : pour d = 512, quelle est la longueur d'onde de la paire i = 128 ? (Réponse :

$$
2\pi \times 10000^{256/512} = 2\pi \times 100 \approx 628{,}3
$$

tokens.)
3. Trouver le bug : `return 10000.0 ** (2 * i / d)` dans `omega`. Que vaut alors ω₂₅₅ pour d = 512, et que devient la notion d'onde lente ? (Réponse : environ 9 647 radians par token ; d'une position entière à la suivante, l'angle fait des milliers de tours et les valeurs paraissent aléatoires : il n'y a plus d'onde lente pour mesurer les grandes distances.)

## Pour aller plus loin

L'encodage rotatif (RoPE), utilisé par beaucoup de modèles récents, applique directement la rotation R(pos · ωᵢ) du point 2 aux requêtes et aux clés, paire par paire, au lieu d'ajouter un vecteur aux embeddings ; par la même identité qu'au point 4, le produit 𝐪 · 𝐤 ne dépend alors que de l'écart entre les deux positions. ALiBi ajoute aux scores une pénalité proportionnelle à la distance. Les encodages appris, optimisés comme des poids, ne sont définis que jusqu'à la longueur maximale prévue à l'entraînement.

> Suite : [Normalisation de couche](<36-Normalisation-de-Couche.md>) — étape 36.
