# 05 — Attention par produit scalaire normalisé : démonstrations

> Fiche : [05 — Attention](<../../Images/03-Modele/05_attention_scaled_dot_product.md>) · Image : `05_attention_scaled_dot_product.jpg` · Leçon : [Étape 31 — Attention par produit scalaire normalisé](<../../06-Attention-et-Transformer/31-Attention-Formule-Produit-Scalaire-Normalise.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
\operatorname{Attention}(Q, K, V) = \operatorname{softmax}\left( \frac{Q K^\top}{\sqrt{d_k}} \right) V
$$

Chaque requête (ligne de Q) compare sa direction à toutes les clés (lignes de K), transforme ces scores en poids, puis mélange les valeurs (lignes de V) avec ces poids.

Pour une seule requête 𝐪ᵢ, la formule se lit en trois lignes, avec les notations de la leçon (étape 31) :

$$
s_{ij} = \frac{\mathbf{q}_i \cdot \mathbf{k}_j}{\sqrt{d_k}} + M_{ij}, \qquad a_{ij} = \frac{e^{s_{ij}}}{\sum_{r=1}^{n_k} e^{s_{ir}}}, \qquad \mathbf{o}_i = \sum_{j=1}^{n_k} a_{ij}\, \mathbf{v}_j
$$

Le masque M vaut 0 partout quand rien n'est interdit ; la formule de la fiche est ce cas particulier.

## Les symboles, un par un

$$
Q
$$

La matrice des requêtes : une ligne 𝐪ᵢ par position qui cherche de l'information, chacune de longueur dₖ, en nombres réels. Le programme traite une requête à la fois : la variable `q`.

$$
K
$$

La matrice des clés : une ligne 𝐤ⱼ par position du contexte, de longueur dₖ (la même que les requêtes, sinon le produit scalaire n'existe pas). Variable `K`, une liste de tuples.

$$
V
$$

La matrice des valeurs : la ligne 𝐯ⱼ est le contenu que la position j transmet si on la lit, de longueur dᵥ. Variable `V` ; elle a autant de lignes que `K`.

$$
K^\top
$$

La transposée de K : la ligne j devient la colonne j, si bien que le produit Q Kᵀ range dans sa case (i, j) le produit scalaire 𝐪ᵢ · 𝐤ⱼ. Le programme n'écrit pas Kᵀ : il parcourt directement les lignes de `K`.

$$
d_k
$$

La largeur des requêtes et des clés, un entier ≥ 1 (128 est une valeur courante par tête). Variable `dk`.

$$
d_v
$$

La largeur des valeurs, un entier ≥ 1 ; c'est aussi la largeur de la sortie. Variable `len(V[0])`.

$$
n_k
$$

Le nombre de clés, c'est-à-dire de positions du contexte que la requête peut lire, un entier ≥ 1. En auto-attention, il y a autant de requêtes que de clés, et ce nombre commun est la longueur n du contexte en tokens. Variable `len(K)`.

$$
\sqrt{d_k}
$$

Le facteur d'échelle, un réel > 0 : √128 ≈ 11,31. Il ramène la variance des scores à 1 (démonstration 2). Variable `math.sqrt(dk)`.

$$
s_{ij}
$$

Le score mis à l'échelle de la requête i pour la clé j : un réel quelconque, ou −∞ si la clé est masquée. Variable `scores[j]` dans la fonction `attention`.

$$
a_{ij}
$$

Le poids d'attention : un réel de [0 ; 1], et chaque ligne de poids somme à 1. Variable `poids[j]`.

$$
\mathbf{o}_i
$$

La sortie de la requête i : un vecteur de longueur dᵥ, moyenne des valeurs pondérée par les aᵢⱼ. Variable `sortie`.

$$
M_{ij}
$$

Le masque additif : 0 si la clé j est autorisée pour la requête i, −∞ si elle est interdite. Variable `masque[j]` ; `masque_causal(n)` construit le masque d'un modèle qui écrit de gauche à droite.

## Le mécanisme, avant les preuves

Ce qui entre : une requête, nₖ clés et nₖ valeurs. Le produit scalaire 𝐪 · 𝐤ⱼ multiplie les coordonnées deux à deux puis les additionne : il est grand quand la requête et la clé pointent dans la même direction, nul quand elles sont orthogonales, négatif quand elles s'opposent. La division par √dₖ ne change pas l'ordre des scores ; elle les ramène à une taille qui ne dépend pas de la dimension, parce qu'une somme de dₖ produits grandit avec dₖ (démonstration 2). L'exponentielle rend chaque score strictement positif et transforme les écarts additifs en rapports multiplicatifs : une avance de 1 sur le score multiplie le poids relatif par e ≈ 2,718. La division par la somme des exponentielles fixe le total des poids à 1 : la requête dispose d'un budget de lecture égal à 1, qu'elle partage entre toutes les clés. La dernière somme mélange les valeurs avec ces poids : la sortie est une moyenne pondérée, jamais une valeur nouvelle. Pourquoi une exponentielle plutôt que les scores eux-mêmes ? Parce que les scores peuvent être négatifs et qu'un poids doit être positif ; et parce que la dérivée de cette normalisation est simple (fiche 04). Pourquoi un produit scalaire plutôt qu'une distance ? Parce que tous les scores d'une ligne s'obtiennent d'un coup par un produit matriciel, ce que les processeurs graphiques font très vite. Le prix de cette forme se lit aussi dans la formule : chaque requête rencontre chaque clé, donc le calcul croît comme le carré de la longueur du contexte (démonstration 4).

Le petit film chiffré, sur l'exemple de la fiche et de la leçon : 𝐪 = (1 ; 0), 𝐤₁ = (0,9 ; 0,1), 𝐤₂ = (0,1 ; 0,9), 𝐤₃ = (0,5 ; 0,5), les valeurs égales aux clés et dₖ = 2.

| Opération | Clé 1 | Clé 2 | Clé 3 |
|---|---|---|---|
| produit scalaire 𝐪 · 𝐤ⱼ | 0,9 | 0,1 | 0,5 |
| division par √2 ≈ 1,41421 | 0,63640 | 0,07071 | 0,35355 |
| exponentielle | 1,88966 | 1,07327 | 1,42412 |
| division par la somme 4,38705 | 0,43074 | 0,24465 | 0,32462 |

La clé 1, la plus alignée avec la requête, reçoit le plus grand poids, mais pas tout : la clé 2, presque orthogonale, garde près d'un quart du budget. La sortie mélange les trois valeurs : sa première coordonnée vaut 0,43074 × 0,9 + 0,24465 × 0,1 + 0,32462 × 0,5 ≈ 0,57444, la seconde vaut 1 − 0,57444 = 0,42556, parce que chaque valeur a des coordonnées de somme 1 (démonstration 1). Un développeur Java peut voir la ligne de poids comme une `Map<Clé, Double>` dont les valeurs somment toujours à 1 : ajouter une entrée oblige à reprendre de la masse aux autres.

## Démonstration 1 — Les dimensions, et une moyenne pondérée

**Ce qu'on démontre.** Si Q a des lignes de longueur dₖ, K a nₖ lignes de longueur dₖ et V a nₖ lignes de longueur dᵥ, alors la sortie a une ligne par requête et dᵥ colonnes, et chaque sortie est une moyenne pondérée des valeurs : pour chaque coordonnée c,

$$
\min_{j} v_{jc} \;\le\; o_{ic} = \sum_{j=1}^{n_k} a_{ij}\, v_{jc} \;\le\; \max_{j} v_{jc}
$$

L'hypothèse est que chaque ligne de poids est positive et somme à 1, ce que garantit la softmax (fiche 04, démonstration 1).

**L'idée.** Une moyenne de notes ne peut pas dépasser la meilleure note ni descendre sous la plus mauvaise. Les poids d'attention jouent le rôle de coefficients de moyenne : ils sont positifs et totalisent 1, donc le résultat reste dans l'enveloppe des valeurs.

**La preuve, pas à pas.**

**Étape 1.** Le produit Q Kᵀ multiplie une matrice à dₖ colonnes par une matrice à dₖ lignes ; il est défini parce que les deux largeurs sont égales, et il a une ligne par requête et nₖ colonnes. Sa case (i, j) vaut :

$$
(Q K^\top)_{ij} = \sum_{l=1}^{d_k} q_{il}\, k_{jl} = \mathbf{q}_i \cdot \mathbf{k}_j
$$

**Étape 2.** La division par √dₖ et la softmax agissent case par case puis ligne par ligne : elles ne changent pas la forme. La matrice des poids A a donc une ligne par requête et nₖ colonnes, parce que la softmax d'une ligne de nₖ scores donne nₖ poids.

**Étape 3.** Le produit A V multiplie une matrice à nₖ colonnes par une matrice à nₖ lignes ; il a une ligne par requête et dᵥ colonnes, et sa case (i, c) vaut :

$$
o_{ic} = \sum_{j=1}^{n_k} a_{ij}\, v_{jc}
$$

**Étape 4.** On majore chaque terme, parce que aᵢⱼ ≥ 0 et que la coordonnée c de 𝐯ⱼ, notée v(j, c), ne dépasse pas le maximum de la colonne c :

$$
a_{ij}\, v_{jc} \le a_{ij} \max_{r} v_{rc}
$$

**Étape 5.** On additionne ces inégalités sur j, puis on utilise la somme des poids égale à 1 :

$$
o_{ic} \le \Big( \sum_{j} a_{ij} \Big) \max_{r} v_{rc} = \max_{r} v_{rc}
$$

**Étape 6.** Le même raisonnement avec le minimum, parce que aᵢⱼ × v(j, c) ≥ aᵢⱼ × minᵣ v(r, c), donne la borne inférieure. ∎

**Vérification chiffrée.** On prend 𝐪 = (0,3 ; −0,7), les clés (1 ; 2), (0 ; 1), (−1 ; 0,5) et les valeurs (3 ; −1), (0,5 ; 4), (−2 ; 2). Produits scalaires : 0,3 × 1 − 0,7 × 2 = −1,1 ; 0,3 × 0 − 0,7 × 1 = −0,7 ; 0,3 × (−1) − 0,7 × 0,5 = −0,65. Divisés par √2 : −0,77782 ; −0,49497 ; −0,45962. On retire le maximum −0,45962 : −0,31820 ; −0,03536 ; 0. Exponentielles : 0,72746 ; 0,96526 ; 1, de somme 2,69272. Poids : 0,27016 ; 0,35847 ; 0,37137. Sortie : 0,27016 × 3 + 0,35847 × 0,5 + 0,37137 × (−2) ≈ 0,24696, et −0,27016 + 0,35847 × 4 + 0,37137 × 2 ≈ 1,90647. La première coordonnée est bien dans [−2 ; 3], la seconde dans [−1 ; 4].

**Ce que la preuve révèle du mécanisme.** L'attention ne crée aucune information : elle choisit où lire et dans quelle proportion. Si les scores sont tous égaux, chaque poids vaut 1/nₖ et la sortie est la moyenne simple ; si un score domine, la sortie recopie presque une seule valeur. Entre les deux, la sortie est un mélange, et un faible poids sur une valeur très grande peut peser plus qu'un fort poids sur une petite (cas 1).

**Conséquence pour un agent.** Une information absente du contexte ne peut pas sortir de l'attention : le retriever et les outils doivent l'y mettre. Et une information présente mais noyée parmi des valeurs voisines sort mélangée : on donne au modèle des blocs nets (un champ, une valeur) plutôt qu'un texte où tout se ressemble.

## Démonstration 2 — Pourquoi diviser par √dₖ

**Ce qu'on démontre.** Si les coordonnées de 𝐪 et de 𝐤 sont indépendantes, de moyenne 0 et de variance 1, alors le score brut a une variance dₖ et le score divisé par √dₖ a une variance 1 :

$$
\operatorname{Var}(\mathbf{q} \cdot \mathbf{k}) = d_k, \qquad \operatorname{Var}\!\left( \frac{\mathbf{q} \cdot \mathbf{k}}{\sqrt{d_k}} \right) = 1
$$

**L'idée.** Une somme de dₖ termes indépendants voit ses variances s'additionner : plus la dimension est grande, plus les scores s'étalent. Diviser par l'écart-type √dₖ annule exactement cet étalement, quelle que soit la dimension.

**La preuve, pas à pas.**

**Étape 1.** Pour une coordonnée l, l'espérance du produit vaut le produit des espérances, parce que qₗ et kₗ sont indépendants :

$$
\mathbb{E}[q_l k_l] = \mathbb{E}[q_l]\, \mathbb{E}[k_l] = 0 \times 0 = 0
$$

**Étape 2.** Sa variance est donc l'espérance de son carré, qui se factorise pour la même raison d'indépendance ; et 𝔼[qₗ²] = Var(qₗ) + 𝔼[qₗ]² = 1 :

$$
\operatorname{Var}(q_l k_l) = \mathbb{E}[q_l^2 k_l^2] - 0^2 = \mathbb{E}[q_l^2]\, \mathbb{E}[k_l^2] = 1 \times 1 = 1
$$

**Étape 3.** Les dₖ produits qₗkₗ sont indépendants entre eux, parce qu'ils portent sur des coordonnées différentes ; la variance d'une somme de termes indépendants est la somme des variances :

$$
\operatorname{Var}(\mathbf{q} \cdot \mathbf{k}) = \sum_{l=1}^{d_k} \operatorname{Var}(q_l k_l) = d_k
$$

**Étape 4.** Diviser une variable par une constante c divise sa variance par c², parce que la variance est une moyenne de carrés d'écarts. Avec c = √dₖ :

$$
\operatorname{Var}\!\left( \frac{\mathbf{q} \cdot \mathbf{k}}{\sqrt{d_k}} \right) = \frac{d_k}{(\sqrt{d_k})^2} = 1
$$

∎

**Vérification chiffrée.** Avec des coordonnées valant −1 ou +1 à chances égales (moyenne 0, variance 1) et dₖ = 4, les 2⁸ = 256 combinaisons possibles de 𝐪 et 𝐤 donnent une variance du score exactement égale à 4 ; le programme les énumère toutes. Avec des coordonnées gaussiennes en dₖ = 16, 20 000 tirages donnent une variance simulée de 16,04, proche de la théorie 16. Contre-exemple quand l'hypothèse « moyenne 0 » manque : avec des coordonnées valant 0 ou 1 (moyenne 0,5, variance 0,25) et dₖ = 4, chaque produit a pour moyenne 0,25 et pour variance 0,25 − 0,25² = 0,1875 ; le score a donc pour moyenne 4 × 0,25 = 1 et pour variance 4 × 0,1875 = 0,75. La division par √dₖ ne stabilise plus rien : en dₖ = 64, la moyenne du score divisé vaut 0,25 × 64 / 8 = 2, et elle continue de croître comme 0,25 √dₖ.

**Ce que la preuve révèle du mécanisme.** Le facteur √dₖ est une température fixée par l'architecture (leçon, point 6) : il garde les scores dans la zone où la softmax n'est ni plate ni saturée. Sans lui, en dₖ = 128, les scores bruts auraient un écart-type de √128 ≈ 11,31 ; la softmax deviendrait presque un argmax, et sa dérivée a(1 − a) s'écraserait vers 0, ce qui arrête l'apprentissage.

**Conséquence pour un agent.** Le développeur d'agent ne règle pas ce facteur : il est figé dans le modèle. Il en tire une leçon de lecture : un poids d'attention élevé n'est pas une « certitude » réglable ; c'est le résultat d'un calibrage fait à l'entraînement, et la seule prise de l'agent reste le contenu du contexte.

## Démonstration 3 — L'attention ignore l'ordre

**Ce qu'on démontre.** Si l'on applique la même permutation σ aux lignes de K et aux lignes de V, chaque sortie 𝐨ᵢ reste identique :

$$
\sum_{j=1}^{n_k} a_{i\sigma(j)}\, \mathbf{v}_{\sigma(j)} = \sum_{j=1}^{n_k} a_{ij}\, \mathbf{v}_j
$$

L'hypothèse est qu'aucun encodage de position ni aucun masque ne dépend de l'ordre des lignes.

**L'idée.** Le poids d'une clé ne dépend que de cette clé, de la requête et d'une somme sur toutes les clés ; or une somme ne dépend pas de l'ordre de ses termes. Déplacer un couple (clé ; valeur) déplace seulement un terme de la somme finale.

**La preuve, pas à pas.**

**Étape 1.** Le score de la clé σ(j) ne dépend que de 𝐪ᵢ et de 𝐤σ₍ⱼ₎, parce que c'est un produit scalaire entre ces deux seuls vecteurs.

**Étape 2.** Le dénominateur de la softmax est la somme des exponentielles de tous les scores ; parcourir les clés dans l'ordre σ additionne les mêmes termes dans un autre ordre, et l'addition est commutative :

$$
\sum_{j=1}^{n_k} e^{s_{i\sigma(j)}} = \sum_{j=1}^{n_k} e^{s_{ij}}
$$

**Étape 3.** Chaque poids aᵢσ₍ⱼ₎ est donc le même nombre qu'avant, simplement rangé à une autre place, parce que son numérateur et son dénominateur n'ont pas changé.

**Étape 4.** La sortie additionne les mêmes produits poids × valeur, parce que la valeur 𝐯σ₍ⱼ₎ a suivi sa clé ; par commutativité de l'addition, la somme est inchangée. ∎

**Vérification chiffrée.** Avec la requête et les trois couples de la démonstration 1, l'ordre (3, 1, 2) donne encore la sortie (0,24696 ; 1,90647). Contre-exemple quand l'hypothèse « même permutation » manque : si l'on permute seulement les clés et pas les valeurs, chaque valeur reçoit le poids d'une autre clé, et la sortie devient (0,53225 ; 1,4262).

**Ce que la preuve révèle du mécanisme.** Pour la formule seule, un contexte est un sac de couples (clé ; valeur), pas une suite. « Le client paie le fournisseur » et « le fournisseur paie le client » donneraient les mêmes sorties pour les mêmes tokens : l'ordre n'entre que par l'encodage de position (fiche 30) et par le masque causal (démonstration 6).

**Conséquence pour un agent.** Placer la clause importante « juste avant la question » n'est pas dicté par l'équation : c'est un choix empirique, qu'on valide en mesurant la justesse des réponses sur le modèle visé, et qu'on revérifie à chaque changement de modèle.

## Démonstration 4 — Le coût quadratique

**Ce qu'on démontre.** Une tête d'auto-attention sur n tokens fait exactement n²(dₖ + dᵥ) multiplications et garde n² scores en mémoire :

$$
\text{multiplications} = n^2\, d_k + n^2\, d_v = n^2 (d_k + d_v)
$$

**L'idée.** Chaque token est à la fois une requête et une clé : il y a n × n rencontres, chacune coûte un produit scalaire de longueur dₖ, puis chaque requête refait n produits pour chacune des dᵥ coordonnées de sa sortie.

**La preuve, pas à pas.**

**Étape 1.** La matrice des scores a n lignes (les requêtes) et n colonnes (les clés), parce qu'en auto-attention il y a autant de requêtes que de clés ; elle compte n² cases.

**Étape 2.** Chaque case est un produit scalaire de longueur dₖ, donc coûte dₖ multiplications ; le total est n² dₖ.

**Étape 3.** La sortie a n lignes et dᵥ colonnes ; chaque case est une somme de n produits poids × valeur, donc coûte n multiplications ; le total est n × dᵥ × n = n² dᵥ.

**Étape 4.** En additionnant les deux étages, on obtient n²(dₖ + dᵥ). Doubler n multiplie ce nombre par 4, parce que :

$$
(2n)^2 (d_k + d_v) = 4\, n^2 (d_k + d_v)
$$

∎

**Vérification chiffrée.** Le programme compte une à une les multiplications faites dans ses boucles : avec dₖ = dᵥ = 2, il trouve 36 multiplications pour n = 3 (9 × 4) et 144 pour n = 6 (36 × 4), soit 4 fois plus pour un contexte 2 fois plus long. Pour n = 4 096 et dₖ = dᵥ = 128 : 4 096² × 256 = 4 294 967 296 multiplications, environ 4,3 milliards, pour une seule tête d'une seule couche.

**Ce que la preuve révèle du mécanisme.** C'est le nombre de tokens n, pas la taille du modèle, qui pilote ce coût, et il le pilote au carré. Diviser le contexte par r divise cette partie du calcul et de la mémoire par r², alors que la facture d'une API est souvent proportionnelle aux tokens seulement.

**Conséquence pour un agent.** La compaction (résumé, résultat d'outil de trois lignes au lieu d'un document brut) paie au carré en latence : c'est l'argument chiffré pour mettre un outil déterministe avant le modèle (cas 3 et 4).

## Démonstration 5 — La dilution : une clé utile parmi nₖ clés

**Ce qu'on démontre.** Si une clé utile a une avance Δ sur nₖ − 1 autres clés qui ont toutes le même score, son poids vaut

$$
a_{\text{utile}} = \frac{e^{\Delta}}{e^{\Delta} + n_k - 1}
$$

il atteint au moins 1/2 si et seulement si nₖ − 1 ≤ e^Δ, et pour garder le même poids en passant de nₖ à n′ clés, il faut l'avance

$$
\Delta' = \Delta + \ln \frac{n' - 1}{n_k - 1}
$$

**L'idée.** Le budget total reste 1 ; chaque concurrent ajouté prend sa part. Comme le poids dépend du rapport e^Δ / (nₖ − 1), compenser une multiplication des concurrents demande une avance qui croît seulement comme leur logarithme.

**La preuve, pas à pas.**

**Étape 1.** On retire à tous les scores le score commun des concurrents ; la softmax ne change pas, parce qu'un facteur commun se simplifie entre numérateur et dénominateur (fiche 04). La clé utile a alors le score Δ et les autres le score 0, d'exponentielle e⁰ = 1 ; d'où la formule de a utile.

**Étape 2.** On divise numérateur et dénominateur par e^Δ :

$$
a_{\text{utile}} = \frac{1}{1 + (n_k - 1)\, e^{-\Delta}}
$$

**Étape 3.** Ce poids vaut au moins 1/2 si et seulement si (nₖ − 1) e^(−Δ) ≤ 1, parce que 1/(1 + x) ≥ 1/2 équivaut à x ≤ 1 ; autrement dit nₖ − 1 ≤ e^Δ.

**Étape 4.** Le poids reste le même si (nₖ − 1) e^(−Δ) reste le même. On écrit cette égalité pour n′ et Δ′, puis on prend le logarithme :

$$
(n' - 1)\, e^{-\Delta'} = (n_k - 1)\, e^{-\Delta} \iff \Delta' = \Delta + \ln \frac{n' - 1}{n_k - 1}
$$

**Étape 5.** Sensibilité : la dérivée du poids par rapport à l'avance est a(1 − a), parce que a est une sigmoïde de Δ − ln(nₖ − 1). ∎

**Vérification chiffrée.** Avec Δ = 2, e² ≈ 7,38906. Pour nₖ = 4 : 7,38906 / 10,38906 ≈ 0,71123. Pour nₖ = 40 : 7,38906 / 46,38906 ≈ 0,15928. Pour retrouver 0,71123 avec 40 clés : Δ′ = 2 + ln(39 / 3) = 2 + ln 13 ≈ 2 + 2,56495 = 4,56495. Sensibilité à nₖ = 4 : a(1 − a) ≈ 0,20538, donc une hausse de 1 % de Δ (de 2 à 2,02) devrait ajouter environ 0,20538 × 0,02 ≈ 0,00411 au poids ; le calcul exact donne 0,00409.

**Ce que la preuve révèle du mécanisme.** Le poids d'une information dépend de ce qui l'entoure, pas seulement d'elle : la même clause pèse 0,71 parmi 4 blocs et 0,16 parmi 40. La frontière nₖ − 1 = e^Δ dit combien de concurrents une information peut supporter avant de perdre la majorité du budget.

**Conséquence pour un agent.** Avant d'ajouter des passages au contexte, on se demande s'ils sont des concurrents de l'information utile ; un retriever qui renvoie 5 passages triés vaut mieux qu'un retriever qui en renvoie 60. Cette formule est un modèle simplifié : l'« oubli du milieu » observé sur de vrais modèles est un autre phénomène, qui ne se déduit pas de l'équation (leçon, point 1).

## Démonstration 6 — Un masque −∞ donne un poids exactement nul

**Ce qu'on démontre.** Si Mᵢⱼ = −∞, alors aᵢⱼ = 0 exactement, et les poids des clés autorisées sont la softmax de leurs seuls scores :

$$
M_{ij} = -\infty \;\Longrightarrow\; a_{ij} = 0, \qquad a_{ir} = \frac{e^{s_{ir}}}{\sum_{t \text{ autorisée}} e^{s_{it}}} \text{ pour } r \text{ autorisée}
$$

L'hypothèse est qu'au moins une clé de la ligne est autorisée.

**L'idée.** L'exponentielle de −∞ vaut 0 : une clé masquée disparaît du numérateur et du dénominateur, comme si elle n'était pas dans le contexte. Il faut qu'il reste au moins un terme, sinon on divise 0 par 0.

**La preuve, pas à pas.**

**Étape 1.** Le score masqué vaut sᵢⱼ = (𝐪ᵢ · 𝐤ⱼ)/√dₖ − ∞ = −∞, parce qu'un réel fini plus −∞ donne −∞.

**Étape 2.** Son exponentielle vaut 0, parce que eˣ tend vers 0 quand x tend vers −∞ ; en arithmétique flottante, `math.exp(-math.inf)` renvoie exactement `0.0`.

**Étape 3.** Le dénominateur ne contient donc plus que les exponentielles des clés autorisées ; il est strictement positif s'il en reste au moins une, parce qu'une exponentielle finie est strictement positive.

**Étape 4.** Le poids masqué vaut 0 divisé par un nombre strictement positif, donc 0 ; les autres poids gardent leur numérateur et partagent le dénominateur réduit, donc somment encore à 1. ∎

**Vérification chiffrée.** Masque causal sur les trois tokens 𝐱₁ = (0,9 ; 0,1), 𝐱₂ = (0,1 ; 0,9), 𝐱₃ = (0,5 ; 0,5), avec Q = K = V = X. Le token 2 voit les tokens 1 et 2 : produits 0,1 × 0,9 + 0,9 × 0,1 = 0,18 et 0,1² + 0,9² = 0,82 ; divisés par √2 : 0,12728 et 0,57983 ; le troisième score vaut −∞. On retire le maximum : 0,12728 − 0,57983 = −0,45255, d'exponentielle 0,63601. Poids : 0,63601 / 1,63601 ≈ 0,38876 et 1 / 1,63601 ≈ 0,61124, et 0 exactement pour le token 3. Sortie : 0,3888 × 0,9 + 0,6112 × 0,1 ≈ 0,411 et 0,3888 × 0,1 + 0,6112 × 0,9 ≈ 0,589. Le token 1 ne voit que lui-même : poids (1 ; 0 ; 0). Contre-exemple quand l'hypothèse manque : si l'on écrit le masque avec j < i au lieu de j ≤ i, la ligne du token 1 ne contient que des −∞, le dénominateur vaut 0 et le poids 0/0 n'est pas défini ; le programme lève `ValueError`.

**Ce que la preuve révèle du mécanisme.** Le masque n'atténue pas une clé : il la supprime, et la softmax redistribue tout le budget entre les clés restantes. C'est ainsi qu'un modèle qui écrit de gauche à droite ne lit jamais le futur, et c'est ce qui fait entrer l'ordre dans le calcul (démonstration 3).

**Conséquence pour un agent.** Un modèle génératif n'utilise, pour écrire un token, que ce qui le précède : une consigne placée après la question n'a pas pu servir à écrire le début de la réponse. Dans un code d'inférence maison, on teste le masque sur la première ligne, celle qui casse en premier.

## Exemple simple, à la main

Une requête 𝐪 = (1 ; 1), trois clés 𝐤₁ = (1 ; 0), 𝐤₂ = (0 ; 1), 𝐤₃ = (1 ; 1), et des valeurs égales aux clés. dₖ = 2, donc √dₖ = √2 ≈ 1,41421.

Scores bruts : 𝐪 · 𝐤₁ = 1 × 1 + 1 × 0 = 1 ; 𝐪 · 𝐤₂ = 1 × 0 + 1 × 1 = 1 ; 𝐪 · 𝐤₃ = 1 × 1 + 1 × 1 = 2.

Scores mis à l'échelle : 1 / 1,41421 = 0,70711 ; 0,70711 ; 2 / 1,41421 = 1,41421.

On retire le maximum 1,41421 (la softmax n'en est pas changée) : −0,70711 ; −0,70711 ; 0. Exponentielles : e^(−0,70711) ≈ 0,49307 ; 0,49307 ; e⁰ = 1. Somme : 0,49307 + 0,49307 + 1 = 1,98614.

$$
a = \left( \frac{0{,}49307}{1{,}98614}\ ;\ \frac{0{,}49307}{1{,}98614}\ ;\ \frac{1}{1{,}98614} \right) \approx (0{,}24826\ ;\ 0{,}24826\ ;\ 0{,}50349)
$$

La sortie est la moyenne pondérée des valeurs. Sa première coordonnée vaut a₁ × 1 + a₂ × 0 + a₃ × 1 = a₁ + a₃ = 1 − a₂ ≈ 1 − 0,24826 = 0,75174 ; la seconde vaut a₁ × 0 + a₂ × 1 + a₃ × 1 = a₂ + a₃ = 1 − a₁ ≈ 0,75174.

$$
\mathbf{o} = 0{,}24826\,(1 ; 0) + 0{,}24826\,(0 ; 1) + 0{,}50349\,(1 ; 1) \approx (0{,}75174\ ;\ 0{,}75174)
$$

La clé la plus alignée reçoit la moitié du poids, mais les deux autres gardent un quart chacune : avec un écart de score de seulement 0,70711, la softmax reste loin d'un choix unique.

## Cas d'usage complexes, démontrés

Dans ces quatre cas, l'équipe ne règle aucun poids d'attention : elle choisit ce qui entre dans le contexte, sous quelle forme et dans quel ordre. Les clés, les avances de score et les volumes sont des modèles simplifiés et illustratifs ; les règles citées (TVA, CBUAE) sont celles du guide du cours.

### Cas 1 — Groupe de construction à Dubaï : retrouver la TVA dans une facture de sous-traitant

**Contexte.** Un groupe de construction qui mène de grands chantiers à Dubaï fait contrôler par un agent les factures de ses sous-traitants avant paiement, environ 1 500 factures par mois (volume illustratif). La question du contrôle est : la TVA facturée vaut-elle bien 5 % du montant hors taxes ? On étudie une tête d'attention jouet qui lit quatre tokens de la facture, et on se demande si l'agent peut se fier à ce que cette tête « lit » pour le montant de TVA. Chaque valeur est le montant porté par le token, en AED.

**Données.** Clés en dimension dₖ = 4, donc √dₖ = 2 :

| Token | Clé | Valeur (AED) |
|---|---|---|
| TVA | (1 ; 0 ; 1 ; 0) | 600 |
| HT | (1 ; 0 ; 0 ; 0) | 12 000 |
| date | (0 ; 1 ; 0 ; 0) | 0 |
| client | (0 ; 0 ; 0 ; 1) | 0 |

Requête « montant de la TVA » : 𝐪 = λ × (1 ; 0 ; 1 ; 0), avec λ = 1 au départ ; λ mesure à quel point l'entraînement a rendu la requête marquée. Contexte complet de la facture : 8 000 tokens, 32 têtes de largeur 128.

**Calcul pas à pas.**

**Étape 1.** Scores bruts pour λ = 1 : 𝐪 · 𝐤 = 2 pour TVA, 1 pour HT, 0 pour la date et le client. Divisés par 2 :

$$
s = (1\ ;\ 0{,}5\ ;\ 0\ ;\ 0)
$$

**Étape 2.** Exponentielles 2,71828 ; 1,64872 ; 1 ; 1, de somme 6,36700, d'où les poids (arrondis à 5 décimales) :

$$
a = \left( \frac{2{,}71828}{6{,}367}\ ;\ \frac{1{,}64872}{6{,}367}\ ;\ \frac{1}{6{,}367}\ ;\ \frac{1}{6{,}367} \right) \approx (0{,}42693\ ;\ 0{,}25895\ ;\ 0{,}15706\ ;\ 0{,}15706)
$$

**Étape 3.** Lecture de la tête, moyenne pondérée des montants (arrondie à l'AED) :

$$
o = 0{,}42693 \times 600 + 0{,}25895 \times 12\,000 + 0 + 0 \approx 256{,}16 + 3\,107{,}37 = 3\,363{,}53 \approx 3\,364 \text{ AED}
$$

**Étape 4.** Requête 4 fois plus marquée (λ = 4) : les scores divisés par 2 deviennent (4 ; 2 ; 0 ; 0), d'exponentielles 54,59815 ; 7,38906 ; 1 ; 1, de somme 63,98721 :

$$
a \approx (0{,}85327\ ;\ 0{,}11548\ ;\ 0{,}01563\ ;\ 0{,}01563), \qquad o \approx 511{,}96 + 1\,385{,}73 = 1\,897{,}69 \approx 1\,898 \text{ AED}
$$

**Étape 5.** Coût du produit Q Kᵀ sur la facture complète : 8 000² × 128 = 8 192 000 000 multiplications par tête, et 32 fois plus pour 32 têtes : 262 144 000 000. À 16 000 tokens, c'est 4 fois plus.

**Décision de l'agent.** Avec λ = 1, le token TVA n'a même pas la majorité du budget (0,42693 < 0,5) ; avec λ = 4, il l'a largement (0,85327), et pourtant la lecture vaut encore 1 898 AED au lieu de 600 AED, parce que 11,5 % du poids posé sur une valeur 20 fois plus grande suffit à tout fausser (démonstration 1). L'agent ne contrôle donc jamais un montant « lu » par le modèle : il appelle un outil d'extraction qui renvoie les champs HT et TVA, puis calcule 0,05 × 12 000 = 600 AED et compare à la TVA facturée ; tout écart de plus de 1 AED bloque la facture et l'envoie à un contrôleur.

**Contre-calcul.** La lecture naïve « le token le plus pondéré gagne » annoncerait 600 AED, alors que la moyenne pondérée vaut 3 364 AED : une erreur de 3 364 − 600 = 2 764 AED, soit 4,6 fois la TVA réelle. Un contrôle fondé sur cette lecture bloquerait à tort une facture juste, ou laisserait passer une facture fausse dont la TVA tomberait par hasard près du mélange.

**Sensibilité.** La valeur de bascule où le token TVA prend exactement la moitié du budget s'obtient en posant u = e^(λ/2) : la condition e^λ = e^(λ/2) + 2 devient u² − u − 2 = 0, de racine positive u = 2, donc λ* = 2 ln 2 ≈ 1,38629. À cette valeur, les poids valent exactement (0,5 ; 0,25 ; 0,125 ; 0,125) et la lecture vaut 0,5 × 600 + 0,25 × 12 000 = 3 300 AED. Une hausse de 10 % de λ* (λ = 1,52492) ne porte le poids de la TVA qu'à 0,52582. Pour que la lecture tombe à 5 % près de 600 AED (au plus 630 AED), il faudrait λ ≈ 11,87 : une requête presque 12 fois plus marquée, qu'aucun réglage de l'agent ne garantit.

**En production.** L'indicateur suivi est la part des factures où l'écart entre la TVA facturée et 5 % du HT recalculé par l'outil dépasse 1 AED ; une hausse soudaine de cette part (seuil d'alerte illustratif : le double de la moyenne des trois derniers mois) signale un modèle de facture nouveau ou un extracteur cassé. La TVA aux Émirats est de 5 % ; la qualification de chaque ligne (taux normal, taux zéro, exonération) reste à confirmer avec le texte en vigueur. Côté coût, on n'envoie au modèle que la facture et les clauses utiles, puisque doubler le contexte quadruple le calcul d'attention.

### Cas 2 — Assureur auto et santé : une franchise noyée parmi 40 messages

**Contexte.** Un assureur auto et santé, supervisé par la CBUAE, confie à un agent le suivi des sinistres. Au 41e message d'un dossier, l'assuré demande combien il sera remboursé pour son pare-brise ; la réponse dépend d'une franchise de 500 AED mentionnée une seule fois, au troisième message. L'équipe traite environ 120 dossiers de pare-brise par mois (volume illustratif). On modélise chaque message par une clé : la clause de franchise a une avance de score Δ = 2 sur les autres messages.

**Données.** Avance de la clause : Δ = 2. Contexte brut : nₖ = 40 messages. Contexte compacté : 4 blocs (faits établis du contrat, résumé de dix lignes des 37 messages intermédiaires, dernier message, question). Franchise : 500 AED. Devis du pare-brise : 2 300 AED (illustratif). Seuil de conception : la clause doit garder au moins la moitié du budget, a ≥ 0,5.

**Calcul pas à pas.**

**Étape 1.** Poids de la clause dans le contexte brut (démonstration 5), avec e² ≈ 7,38906 :

$$
a_{40} = \frac{7{,}38906}{7{,}38906 + 39} = \frac{7{,}38906}{46{,}38906} \approx 0{,}15928
$$

**Étape 2.** Poids dans le contexte compacté :

$$
a_{4} = \frac{7{,}38906}{7{,}38906 + 3} = \frac{7{,}38906}{10{,}38906} \approx 0{,}71123
$$

**Étape 3.** Nombre maximal de blocs qui garde a ≥ 0,5 : nₖ − 1 ≤ e², soit nₖ ≤ 1 + 7,38906 = 8,389, donc 8 blocs au plus. Vérification : 8 blocs donnent 0,51352 et 9 blocs 0,48015.

**Étape 4.** Montant dû à l'assuré :

$$
\text{remboursement} = 2\,300 - 500 = 1\,800 \text{ AED}
$$

**Décision de l'agent.** 40 messages dépassent largement la limite de 8 blocs : l'équipe compacte le contexte. Un outil `conditions_contrat` renvoie la franchise, le plafond et la règle de vétusté dans un bloc « Faits établis du dossier », réinjecté à chaque tour ; la clause retrouve un poids de 0,71123, et l'agent répond 1 800 AED en citant la franchise.

**Contre-calcul.** Pour garder la clause à 0,71123 au milieu des 40 messages, il faudrait une avance Δ′ = 2 + ln 13 ≈ 4,56495, soit 2,28 fois l'avance réelle : rien dans le prompt ne la garantit. Une réponse qui oublie la franchise promet 2 300 AED au lieu de 1 800 AED, soit 500 AED de trop par dossier ; si 10 % des 120 dossiers mensuels étaient touchés, cela ferait 12 × 500 = 6 000 AED par mois (illustratif), sans compter la reprise de la réponse auprès du client.

**Sensibilité.** Si la clause est mieux rédigée et son avance monte de 10 % (Δ = 2,2, e^2,2 ≈ 9,02501), son poids parmi 40 messages ne monte qu'à 0,18792, et la limite passe de 8 à 10 blocs (10 blocs donnent 0,50069, 11 blocs 0,47438). La décision ne change pas : seule la compaction ramène le contexte sous la limite.

**En production.** L'indicateur suivi est la part des réponses qui citent la bonne franchise, mesurée sur 200 dossiers rejoués à chaque modification du prompt ou du modèle ; alerte sous 98 % (seuil illustratif). Un garde-fou compte les blocs envoyés et refuse d'en envoyer plus de 8 sans compaction. Les obligations de l'assureur envers l'assuré relèvent de la supervision de la CBUAE ; leur détail est à confirmer avec le texte en vigueur.

### Cas 3 — Banque de détail à Dubaï : six mois de relevés ou un résultat d'outil

**Contexte.** Une banque de détail de Dubaï utilise un agent qui prépare, pour ses conseillers, la recevabilité des demandes de prêt personnel. Le prototype collait dans le prompt six mois de relevés, environ 30 000 tokens et 3 000 lignes de transactions, et demandait au modèle de repérer lui-même les mensualités en cours. La règle à appliquer est celle de la CBUAE : toutes les mensualités, y compris la nouvelle, ne dépassent pas 50 % du salaire ; le prêt personnel ne dépasse pas 20 fois le salaire ni 48 mois. Les montants du dossier sont illustratifs.

**Données.** Salaire : 20 000 AED par mois. Mensualités bien visibles : 4 200 AED. Crédit auto prélevé chaque mois, noyé dans les relevés : 2 100 AED. Nouvelle mensualité demandée : 4 500 AED, pour 180 000 AED sur 48 mois. Avance de score de la ligne du crédit auto : Δ = 3. Contexte brut : 30 000 tokens, 3 000 lignes ; résultat d'outil : 300 tokens, 3 lignes. Têtes de largeur dₖ = dᵥ = 128.

**Calcul pas à pas.**

**Étape 1.** Poids de la ligne du crédit auto parmi les 3 000 lignes, puis parmi les 3 lignes du résultat d'outil, avec e³ ≈ 20,08554 :

$$
a_{3\,000} = \frac{20{,}08554}{20{,}08554 + 2\,999} \approx 0{,}00665, \qquad a_{3} = \frac{20{,}08554}{20{,}08554 + 2} \approx 0{,}90944
$$

**Étape 2.** Ratio d'endettement total, toutes mensualités comprises :

$$
\frac{4\,200 + 2\,100 + 4\,500}{20\,000} = \frac{10\,800}{20\,000} = 54\ \%
$$

**Étape 3.** Mensualité nouvelle maximale permise par la règle des 50 %, puis montant maximal au même taux et sur la même durée (la mensualité est proportionnelle au montant emprunté) :

$$
0{,}5 \times 20\,000 - (4\,200 + 2\,100) = 3\,700 \text{ AED}, \qquad 180\,000 \times \frac{3\,700}{4\,500} = 148\,000 \text{ AED}
$$

**Étape 4.** Plafonds de montant et de durée : 20 × 20 000 = 400 000 AED ≥ 180 000 AED, et 48 mois ≤ 48 mois : ils sont respectés.

**Étape 5.** Coût de l'attention, une tête et une couche (démonstration 4) : 30 000² × 256 = 230 400 000 000 multiplications pour les relevés, 300² × 256 = 23 040 000 pour le résultat d'outil, soit un calcul divisé par (30 000 / 300)² = 10 000.

**Décision de l'agent.** Le ratio de 54 % dépasse 50 % : la demande telle quelle n'est pas recevable. L'agent propose au conseiller une contre-offre de 148 000 AED sur 48 mois, à 3 700 AED par mois, qui ramène le ratio à exactement 50 %. Le calcul est fait par un outil hors du modèle ; le prompt ne reçoit que trois lignes : le ratio, le plafond et la conclusion.

**Contre-calcul.** Si le modèle manque le crédit auto, ce que rend plausible son poids de 0,00665 parmi 3 000 lignes, il calcule (4 200 + 4 500) / 20 000 = 43,5 % et déclare recevable un dossier qui dépasse la règle : le client s'engagerait sur 54 % de son salaire, et la banque accorderait un crédit non conforme qu'un contrôle de conformité devra ensuite reprendre.

**Sensibilité.** La valeur de bascule du salaire, au-dessus de laquelle la demande de 4 500 AED devient recevable, vaut (4 200 + 2 100 + 4 500) / 0,5 = 21 600 AED. Si le salaire baisse de 10 % (18 000 AED), la mensualité nouvelle maximale tombe à 0,5 × 18 000 − 6 300 = 2 700 AED.

**En production.** L'indicateur suivi est le nombre d'écarts entre le ratio écrit par l'agent et celui que recalcule le contrôle de conformité, avec un objectif de zéro ; tout écart déclenche une revue du dossier. Les seuils (50 % du salaire, 30 % pour un retraité, 20 fois le salaire, 48 mois) sont ceux de la CBUAE et se paramètrent dans l'outil, jamais dans le prompt.

### Cas 4 — Plateforme d'actifs virtuels agréée VARA : condenser les journaux de liquidité

**Contexte.** Une plateforme d'actifs virtuels agréée par la VARA fait analyser par un agent les alertes de liquidité de ses pools ; l'agent doit proposer une action à l'astreinte en quelques minutes. Les journaux bruts des dernières 24 heures font environ 120 000 tokens, dont 12 lignes seulement décrivent des anomalies. L'équipe hésite entre trois options : tout envoyer, découper en 30 fenêtres de 4 000 tokens, ou agréger les journaux par pool et par tranche de cinq minutes en 4 000 tokens. Les volumes et le seuil sont illustratifs.

**Données.** Lignes anormales : 12, chacune avec une avance de score Δ = 4 sur les lignes normales. Contexte brut : 120 000 tokens. Contexte agrégé : 4 000 tokens. Fenêtres : 30 × 4 000 tokens. Largeurs : dₖ = dᵥ = 128. Seuil de conception : la part totale du budget posée sur les anomalies doit atteindre au moins 0,10.

**Calcul pas à pas.**

**Étape 1.** Coût d'une tête sur une couche, n²(dₖ + dᵥ) :

$$
120\,000^2 \times 256 = 3{,}6864 \times 10^{12}, \qquad 4\,000^2 \times 256 = 4{,}096 \times 10^{9}
$$

Le rapport vaut (120 000 / 4 000)² = 900. Les 30 fenêtres coûtent 30 × 4,096 × 10⁹ = 1,2288 × 10¹¹, soit 30 fois moins que le brut seulement.

**Étape 2.** Part du budget sur les 12 anomalies, avec 12 e⁴ ≈ 12 × 54,59815 = 655,18 (les n − 12 autres lignes ont l'exponentielle 1) :

$$
\text{part}(n) = \frac{655{,}18}{655{,}18 + n - 12}, \qquad \text{part}(120\,000) \approx 0{,}00543, \qquad \text{part}(4\,000) \approx 0{,}14111
$$

**Étape 3.** Taille de contexte de bascule, où la part vaut exactement 0,10 : 655,18 / (655,18 + n − 12) = 0,1 donne n − 12 = 9 × 655,18, donc

$$
n^{*} = 12 + 9 \times 655{,}18 \approx 5\,908{,}6 \text{ tokens}
$$

**Décision de l'agent.** Le contexte agrégé de 4 000 tokens reste sous la bascule de 5 908 tokens : sa part sur les anomalies (0,14111) dépasse le seuil de 0,10, et son calcul d'attention est 900 fois plus petit que celui des journaux bruts. L'équipe retient l'agrégation, faite par un outil déterministe avant l'appel au modèle.

**Contre-calcul.** Les journaux bruts ne posent que 0,00543 du budget sur les anomalies, et coûtent 900 fois plus. Les fenêtres ne divisent le coût que par 30, et une fenêtre qui ne contient qu'une anomalie ne lui donne que e⁴ / (e⁴ + 3 999) ≈ 0,01347 du budget ; de plus, une anomalie qui s'étale sur deux fenêtres n'est vue en entier par aucune. Une analyse qui arrive après la fenêtre de réaction de l'astreinte laisse un pool en tension sans action.

**Sensibilité.** Si les anomalies ressortent 10 % moins (Δ = 3,6, e^3,6 ≈ 36,59823, 12 × 36,59823 ≈ 439,18), la bascule tombe à 12 + 9 × 439,18 ≈ 3 964,6 tokens, sous les 4 000 tokens retenus : la part devient 0,09920 < 0,10 et la décision bascule. L'équipe passe alors à des tranches de dix minutes pour descendre sous 3 964 tokens.

**En production.** On suit deux indicateurs : le 95e percentile de la latence d'analyse et la part des incidents réels correctement remontés à l'astreinte (alerte si elle baisse d'un mois sur l'autre). La taille du contexte agrégé est mesurée à chaque appel et comparée à la bascule recalculée. Les obligations de surveillance d'une plateforme agréée par la VARA sont à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Donner la taille de la sortie pour Q de taille 5 × 64, K de taille 7 × 64 et V de taille 7 × 32.

**Exercice 2.** Une requête a des scores bruts (2 ; 2) sur deux clés. Quels sont les poids ? Que vaut la sortie si 𝐯₁ = (10 ; 0) et 𝐯₂ = (0 ; 10) ?

**Exercice 3.** En dimension dₖ = 64, quel est l'écart-type d'un score non normalisé, sous les hypothèses de la démonstration 2 ? Et après division ?

**Exercice 4.** Le contexte passe de 4 000 à 12 000 tokens. Par combien le coût de Q Kᵀ est-il multiplié ?

**Exercice 5.** Montrer avec deux clés et deux valeurs que permuter les paires (clé ; valeur) ne change pas la sortie.

**Exercice 6 (cas modifié).** Dans le cas 2, la clause de franchise a désormais une avance Δ = 3. Combien de blocs le contexte peut-il compter au plus pour qu'elle garde au moins la moitié du budget ? Que vaut son poids parmi 40 messages ? La compaction reste-t-elle nécessaire ?

**Exercice 7 (trouver l'erreur).** Un collègue écrit : « La variance du score brut vaut dₖ, donc on divise le score par dₖ. » Trouver l'erreur, puis la chiffrer avec dₖ = 64 et deux clés de scores bruts 16 et 0 : poids de la première clé avec la bonne division et avec la mauvaise, et variance obtenue après la mauvaise division.

**Exercice 8 (redémontrer de mémoire).** Sans regarder la démonstration 1, démontrer que chaque coordonnée de la sortie de l'attention est comprise entre le minimum et le maximum de la colonne correspondante de V.

## Corrigé

**Exercice 1.** Q Kᵀ a 5 lignes et 7 colonnes (5 requêtes, 7 clés) ; la softmax garde cette forme ; le produit par V (7 × 32) donne 5 lignes et 32 colonnes. La sortie est de taille 5 × 32 : une ligne par requête, dᵥ colonnes.

**Exercice 2.** Les scores sont égaux, donc leurs exponentielles aussi, et chaque poids vaut e^s / (2 e^s) = 0,5 ; la division par √dₖ ne change rien à cette égalité. Sortie : 0,5 × (10 ; 0) + 0,5 × (0 ; 10) = (5 ; 5), la moyenne simple.

**Exercice 3.** La variance du score brut vaut dₖ = 64, donc son écart-type vaut √64 = 8. Après division par √64 = 8, la variance vaut 64 / 64 = 1 et l'écart-type 1.

**Exercice 4.** Le coût est proportionnel à n². Le rapport vaut (12 000 / 4 000)² = 3² = 9.

**Exercice 5.** Avec deux couples, la sortie vaut a₁𝐯₁ + a₂𝐯₂, où a₁ et a₂ ne dépendent que de leurs clés et de la somme e^(s₁) + e^(s₂). Après permutation, la somme devient e^(s₂) + e^(s₁), le même nombre ; chaque valeur garde le poids de sa clé, et la sortie vaut a₂𝐯₂ + a₁𝐯₁ = a₁𝐯₁ + a₂𝐯₂, parce que l'addition est commutative.

**Exercice 6.** La condition a ≥ 0,5 s'écrit nₖ − 1 ≤ e³ ≈ 20,08554, donc nₖ ≤ 21,08554 : 21 blocs au plus. Parmi 40 messages, le poids vaut 20,08554 / (20,08554 + 39) = 20,08554 / 59,08554 ≈ 0,33994. Comme 40 > 21, la compaction reste nécessaire, même si la clause est mieux marquée.

**Exercice 7.** L'erreur : on divise par l'écart-type, pas par la variance. La variance vaut dₖ, l'écart-type √dₖ ; diviser par dₖ divise la variance par dₖ², ce qui donne dₖ / dₖ² = 1 / dₖ = 1/64 = 0,015625 au lieu de 1. Chiffrage : avec la bonne division par √64 = 8, les scores deviennent (2 ; 0) et le premier poids vaut e² / (e² + 1) = 7,38906 / 8,38906 ≈ 0,88080 ; avec la mauvaise division par 64, ils deviennent (0,25 ; 0) et le premier poids vaut e^0,25 / (e^0,25 + 1) ≈ 1,28403 / 2,28403 ≈ 0,56218. Les scores sont écrasés et les poids presque uniformes : l'attention ne distingue plus les clés.

**Exercice 8.** Étape 1 : la softmax donne des poids aⱼ ≥ 0 de somme 1. Étape 2 : pour une coordonnée c, chaque terme vérifie aⱼ × v(j, c) ≤ aⱼ × maxᵣ v(r, c), où v(j, c) est la coordonnée c de 𝐯ⱼ, parce que aⱼ ≥ 0. Étape 3 : on additionne sur j ; le membre de droite vaut (∑ⱼ aⱼ) × maxᵣ v(r, c) = maxᵣ v(r, c), parce que la somme des poids vaut 1. Étape 4 : le même raisonnement avec le minimum donne la borne inférieure. ∎

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(z)`** — Cette fonction se comporte comme un répartiteur qui doit distribuer exactement une unité d'attention entre plusieurs candidats selon leurs scores : elle reçoit la liste `z` des scores, repère d'abord le plus grand et, si ce maximum vaut −∞ parce que toutes les clés sont masquées, elle refuse de travailler et lève une `ValueError`, car les poids seraient alors de la forme 0/0. Sinon, elle retire ce maximum à chaque score avant de prendre l'exponentielle, ce qui évite tout débordement sans changer le résultat, additionne ces exponentielles et divise chacune par la somme ; elle renvoie ainsi une liste de poids positifs dont le total vaut 1, et un score −∞ y reçoit un poids exactement nul, ce dont le masque causal a besoin.

**`attention(q, K, V, masque, compteur)`** — C'est le cœur du programme, un lecteur qui, muni d'une question `q`, parcourt un fichier de fiches dont chacune porte une étiquette (la clé) et un contenu (la valeur) : la fonction vérifie d'abord que les clés et les valeurs sont aussi nombreuses, qu'il y en a au moins une et que chaque clé a la dimension dₖ de la requête, sinon elle lève une `ValueError`. Pour chaque clé, elle calcule le produit scalaire avec `q`, le divise par √dₖ, ajoute le terme du `masque` s'il est fourni, puis confie la liste des scores à `softmax` ; elle mélange enfin les valeurs colonne par colonne, chacune pesée par son poids, et, si un dictionnaire `compteur` lui est passé, elle y compte chaque multiplication effectuée. Elle renvoie le couple (poids, sortie), par exemple les poids 0,43074, 0,24465 et 0,32462 et la sortie (0,57444 ; 0,42556) du film du mécanisme.

**`masque_causal(n)`** — Cette fonction fabrique le règlement d'une salle où chaque lecteur n'a le droit de consulter que les pages déjà écrites : elle reçoit la longueur `n` de la séquence et construit un tableau carré de n lignes et n colonnes où la case (i, j) vaut 0 quand j ≤ i, c'est-à-dire pour le passé et le présent, et −∞ quand j > i, pour le futur interdit. Elle renvoie cette matrice, que `main` utilise dans la démonstration 6 : ajoutée aux scores, elle donne au token 2 les poids 0,3888, 0,6112 et un poids exactement nul sur le troisième token.

**`poids_cle_utile(delta, n)`** — Celle-ci mesure combien une fiche utile se fait remarquer dans une foule de fiches banales : elle reçoit l'avance `delta` du score de la bonne clé sur toutes les autres, supposées de score 0, et le nombre total `n` de clés, lève une `ValueError` s'il n'y a pas au moins une clé, puis renvoie le poids e^Δ / (e^Δ + n − 1). C'est la formule de la dilution de la démonstration 5 : avec Δ = 2, la clé utile garde 0,71123 du budget parmi 4 clés mais seulement 0,15928 parmi 40, et les cas de l'assurance, de la banque et de la crypto s'en servent pour décider s'il faut compacter le contexte.

**`cout_attention(n, dk, dv)`** — Cette fonction est le comptable de la tête d'attention : elle reçoit le nombre `n` de tokens, la dimension `dk` des clés et la dimension `dv` des valeurs, et renvoie le nombre exact de multiplications d'une auto-attention, n² × dₖ pour le produit Q Kᵀ plus n² × dᵥ pour le mélange A V, soit n²(dₖ + dᵥ). La démonstration 4 confronte ce décompte au compteur tenu dans `attention`, 36 multiplications pour n = 3 et 144 pour n = 6 en dimension 2, puis l'applique à 4 096 tokens en dimension 128 pour obtenir 4 294 967 296 ; les cas 3 et 4 l'utilisent pour chiffrer le gain d'un contexte réduit.

**`r5(xs)`** — Cette petite fonction est le greffier qui recopie les résultats au propre avant de les comparer : elle reçoit une liste de nombres et renvoie une nouvelle liste où chacun est arrondi à cinq décimales avec `round(x, 5)`. Elle ne calcule rien de nouveau, mais elle permet aux nombreux `assert` de `main` et aux affichages des cas de confronter des listes de poids ou de sorties aux valeurs écrites à la main dans la fiche, comme [0,24826 ; 0,24826 ; 0,50349], sans être gênés par les derniers chiffres flottants.

**`cas_1_facture_btp()`** — On y suit un agent qui cherche le montant de la TVA dans une facture de chantier de quatre tokens (TVA, HT, date, client), dont les valeurs portent 600 AED pour la TVA, 12 000 AED pour le hors-taxe et rien pour les deux autres : la fonction lance `attention` avec la requête (1, 0, 1, 0) multipliée par λ = 1, par λ = 2 ln 2 et par λ = 4, et observe que la lecture vaut 3 364 AED, puis 3 300 AED, puis 1 898 AED, loin des 600 attendus. Elle cherche ensuite par dichotomie, en 60 tours entre 1 et 40, le plus petit λ dont la lecture descend à 630 AED, c'est-à-dire à 5 % près, et trouve 11,87 ; elle affiche aussi le coût de Q Kᵀ pour 8 000 tokens en dimension 128, puis conclut à une « extraction par outil » parce que le poids de la TVA reste sous 0,5 et que la lecture s'écarte de 2 764 AED du contrôle 5 % du HT. Elle renvoie le dictionnaire des résultats par λ, la valeur de bascule, le λ trouvé et la décision.

**`cas_2_franchise_assurance()`** — Cette fonction raconte un gestionnaire de sinistres dont la clause de franchise, avec une avance Δ = 2, se perd parmi 40 messages : à l'aide de `poids_cle_utile`, elle calcule le poids de la clause dans le contexte brut, 0,15928, puis après compaction en 4 blocs, 0,71123, l'avance qu'il faudrait pour retrouver ce poids sans compacter, 4,56495, et le nombre maximal de blocs, 8, qui laisse encore à la clause la moitié du budget. Elle refait le calcul avec une avance augmentée de 10 % (poids 0,18792, au plus 10 blocs), chiffre le remboursement juste, 2 300 − 500 = 1 800 AED, face à la promesse fausse de 2 300 AED, et renvoie ces huit grandeurs avec la décision « compaction en 4 blocs », puisque 40 messages dépassent les 8 blocs tolérés.

**`cas_3_releves_banque()`** — Un analyste de crédit examine une demande de 180 000 AED sur 48 mois pour un salaire de 20 000 AED, avec 4 200 AED de mensualités visibles, un crédit auto de 2 100 AED noyé dans les relevés et une nouvelle mensualité de 4 500 AED : la fonction calcule le ratio d'endettement qu'on obtiendrait en oubliant le crédit auto, 43,5 %, puis le vrai ratio total, 54 %, la mensualité maximale qui respecte le plafond de 50 %, 3 700 AED, le montant maximal correspondant, 148 000 AED, et le salaire de bascule, 21 600 AED. Elle montre aussi, avec `poids_cle_utile` et une avance de 3, que la ligne du crédit auto ne pèse que 0,00665 parmi 3 000 lignes contre 0,90944 parmi 3, et, avec `cout_attention`, que passer de 30 000 à 300 tokens divise le calcul par 10 000. Elle renvoie ces onze résultats, dont la décision « contre-offre 148000 AED sur 48 mois ».

**`cas_4_journaux_crypto()`** — Cette fonction met en scène un veilleur de nuit qui cherche 12 lignes anormales, d'avance Δ = 4, dans des journaux de transactions, et qui veut qu'elles reçoivent au moins 10 % de l'attention : elle compare le coût de l'option brute à 120 000 tokens, 3,6864 × 10¹², à celui de l'option agrégée à 4 000 tokens, 4,096 × 10⁹, soit un rapport de 900, et au coût de 30 fenêtres de 4 000 tokens. Grâce à sa fonction interne `part_anomalies`, elle calcule la part du poids sur les anomalies, 0,00543 en brut contre 0,14111 en agrégé, puis la longueur de bascule, environ 5 908,6 tokens, et sa version avec une avance réduite de 10 %, environ 3 964,6 ; elle renvoie ces grandeurs avec deux décisions, « agrégation retenue » dans le cas nominal et « tranches de dix minutes » quand l'avance faiblit.

**`part_anomalies(n, d)`** — Cette fonction interne vit dans `cas_4_journaux_crypto` et y joue le rôle d'une balance qui pèse toutes les lignes suspectes d'un coup : elle reçoit la longueur `n` du contexte et l'avance `d`, qui vaut par défaut l'avance 4 du cas, et renvoie la part totale de l'attention captée par les 12 anomalies, 12 e^d / (12 e^d + n − 12), en utilisant le nombre d'anomalies fixé par la fonction qui l'entoure. C'est la généralisation de `poids_cle_utile` à plusieurs clés utiles, et c'est elle qui donne 0,14111 pour 4 000 tokens et 0,0992 quand l'avance baisse de 10 %, sous le seuil de 10 %.

**`main()`** — C'est le banc d'essai qui rejoue toute la fiche dans l'ordre où on la lit : il reprend le film du mécanisme et l'exemple simple avec `attention`, vérifie dans la démonstration 1 que chaque coordonnée de la sortie reste entre le minimum et le maximum des valeurs, calcule dans la démonstration 2 la variance exacte 4 d'un produit scalaire à coordonnées ±1 en dimension 4 puis la simule en dimension 16 (16,04), et vérifie dans la démonstration 3 que permuter les couples clé-valeur ne change rien alors que permuter les seules clés change la sortie. Il compte ensuite les multiplications de la démonstration 4, mesure la dilution de la démonstration 5, applique le masque causal de la démonstration 6 en s'assurant qu'une ligne entièrement masquée lève bien une `ValueError`, lance les quatre cas puis le corrigé des exercices ; chaque nombre affiché est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tous concordent.

```python
"""Démonstration 05 — attention : moyenne pondérée, variance d_k, ordre, coût, dilution, masque, quatre cas aux EAU."""
import itertools
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def softmax(z: list[float]) -> list[float]:
    """Softmax stable : on retire le maximum ; un score -inf reçoit un poids exactement nul."""
    m = max(z)
    if m == -math.inf:
        raise ValueError("toutes les clés sont masquées : les poids ne sont pas définis")
    e = [math.exp(x - m) for x in z]
    s = sum(e)
    return [x / s for x in e]


def attention(q, K, V, masque=None, compteur=None):
    """Une requête : poids = softmax(q · kⱼ / √d_k + Mⱼ), sortie = Σⱼ poidsⱼ × vⱼ. Renvoie (poids, sortie)."""
    dk = len(q)
    if not K or len(K) != len(V) or any(len(k) != dk for k in K):
        raise ValueError("q, K et V ont des dimensions incompatibles")
    scores = []
    for j, k in enumerate(K):
        s = 0.0
        for a, b in zip(q, k):
            s += a * b
            if compteur is not None:
                compteur["mult"] += 1
        s = s / math.sqrt(dk)
        if masque is not None:
            s += masque[j]
        scores.append(s)
    poids = softmax(scores)
    sortie = []
    for c in range(len(V[0])):
        o = 0.0
        for w, v in zip(poids, V):
            o += w * v[c]
            if compteur is not None:
                compteur["mult"] += 1
        sortie.append(o)
    return poids, sortie


def masque_causal(n: int) -> list[list[float]]:
    """M[i][j] = 0 si j <= i (passé et présent), -inf si j > i (futur interdit)."""
    return [[0.0 if j <= i else -math.inf for j in range(n)] for i in range(n)]


def poids_cle_utile(delta: float, n: int) -> float:
    """Poids d'une clé d'avance delta face à n - 1 clés de score 0 : e^Δ / (e^Δ + n - 1)."""
    if n < 1:
        raise ValueError("il faut au moins une clé")
    return math.exp(delta) / (math.exp(delta) + n - 1)


def cout_attention(n: int, dk: int, dv: int) -> int:
    """Multiplications d'une tête d'auto-attention : n²·d_k pour Q Kᵀ, n²·d_v pour A V."""
    return n * n * (dk + dv)


def r5(xs):
    return [round(x, 5) for x in xs]


def cas_1_facture_btp():
    """BTP : la requête « montant de la TVA » face à 4 tokens d'une facture, puis requête λ fois plus marquée."""
    K = [(1, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)]   # TVA, HT, date, client
    V = [(600.0,), (12000.0,), (0.0,), (0.0,)]                       # montant porté par chaque token (AED)
    res = {}
    for lam in (1.0, 2 * math.log(2), 4.0):
        p, o = attention([lam * x for x in (1, 0, 1, 0)], K, V)
        res[lam] = (p, o[0])
    lam_bascule = 2 * math.log(2)
    bas, haut = 1.0, 40.0                     # plus petit λ dont la lecture reste à 5 % de 600 AED (630 AED)
    for _ in range(60):
        milieu = (bas + haut) / 2
        if attention([milieu * x for x in (1, 0, 1, 0)], K, V)[1][0] > 630:
            bas = milieu
        else:
            haut = milieu
    print(f"cas 1 BTP : poids λ=1 {r5(res[1.0][0])} ; lecture {res[1.0][1]:.0f} AED")
    print(f"  bascule λ* = 2 ln 2 = {lam_bascule:.5f} : poids {r5(res[lam_bascule][0])}, lecture {res[lam_bascule][1]:.0f} AED ;"
          f" λ=4 : {r5(res[4.0][0])}, lecture {res[4.0][1]:.0f} AED")
    print(f"  lecture à 5 % près dès λ = {haut:.2f} ;"
          f" coût Q Kᵀ : 8 000 tokens, d_k 128 : {8000 ** 2 * 128:,} par tête ; 32 têtes : {8000 ** 2 * 128 * 32:,}")
    tva_attendue = 0.05 * 12000
    ecart = abs(res[1.0][1] - tva_attendue)
    decision = "extraction par outil" if res[1.0][0][0] < 0.5 or ecart > 1 else "lecture du modèle"
    print(f"  décision : {decision} (poids TVA {res[1.0][0][0]:.5f}, écart de lecture {ecart:.0f} AED) ;"
          f" contrôle 5 % du HT = {tva_attendue:.0f} AED")
    return res, lam_bascule, haut, decision


def cas_2_franchise_assurance():
    """Assurance : une clause d'avance Δ = 2 parmi 40 messages, puis après compaction (4 blocs)."""
    delta, n_brut, n_compact = 2.0, 40, 4
    a_brut, a_compact = poids_cle_utile(delta, n_brut), poids_cle_utile(delta, n_compact)
    delta_requis = delta + math.log((n_brut - 1) / (n_compact - 1))
    n_max = math.floor(1 + math.exp(delta))                 # a >= 0.5  <=>  n - 1 <= e^Δ
    a_plus10 = poids_cle_utile(1.1 * delta, n_brut)
    n_max_plus10 = math.floor(1 + math.exp(1.1 * delta))
    devis, franchise = 2300, 500
    print(f"cas 2 ASSUR : poids de la clause {a_brut:.5f} (40 messages) -> {a_compact:.5f} (4 blocs) ;"
          f" Δ requis {delta_requis:.5f} ; n max {n_max}")
    print(f"  Δ + 10 % : poids {a_plus10:.5f}, n max {n_max_plus10} ; remboursement {devis - franchise} AED, promesse fausse {devis} AED")
    decision = "compaction en 4 blocs" if n_brut > n_max else "contexte brut"
    print(f"  décision : {n_brut} messages > {n_max} blocs -> {decision}")
    return a_brut, a_compact, delta_requis, n_max, a_plus10, n_max_plus10, devis - franchise, decision


def cas_3_releves_banque():
    """Banque : ratio d'endettement total CBUAE, dilution d'une ligne parmi 3 000, coût 30 000 -> 300 tokens."""
    salaire, visibles, auto, nouvelle, montant, duree = 20000, 4200, 2100, 4500, 180000, 48
    ratio_oubli = (visibles + nouvelle) / salaire
    ratio_total = (visibles + auto + nouvelle) / salaire
    mensualite_max = 0.5 * salaire - (visibles + auto)
    montant_max = montant * mensualite_max / nouvelle
    salaire_bascule = (visibles + auto + nouvelle) / 0.5
    mensualite_max_moins10 = 0.5 * 0.9 * salaire - (visibles + auto)
    a_releves, a_outil = poids_cle_utile(3.0, 3000), poids_cle_utile(3.0, 3)
    gain = cout_attention(30000, 128, 128) // cout_attention(300, 128, 128)
    plafond_ok = montant <= 20 * salaire and duree <= 48
    print(f"cas 3 BANQUE : ratio sans le crédit auto {ratio_oubli:.1%}, ratio total {ratio_total:.1%} ;"
          f" mensualité max {mensualite_max:.0f} AED ; montant max {montant_max:.0f} AED")
    print(f"  poids de la ligne auto : {a_releves:.5f} (3 000 lignes) contre {a_outil:.5f} (3 lignes) ;"
          f" calcul d'attention divisé par {gain:,} ; salaire de bascule {salaire_bascule:.0f} AED")
    decision = "recevable" if ratio_total <= 0.5 and plafond_ok else f"contre-offre {montant_max:.0f} AED sur {duree} mois"
    print(f"  décision : ratio {ratio_total:.1%} > 50 % -> {decision}")
    return (ratio_oubli, ratio_total, mensualite_max, montant_max, salaire_bascule, mensualite_max_moins10,
            a_releves, a_outil, gain, plafond_ok, decision)


def cas_4_journaux_crypto():
    """Crypto : 12 lignes anormales d'avance Δ = 4 parmi n tokens ; coût et part du poids sur les anomalies."""
    nb_anom, delta, seuil = 12, 4.0, 0.10

    def part_anomalies(n, d=delta):
        return nb_anom * math.exp(d) / (nb_anom * math.exp(d) + n - nb_anom)

    options = {"brut": 120000, "agrégé": 4000}
    couts = {nom: cout_attention(n, 128, 128) for nom, n in options.items()}
    parts = {nom: part_anomalies(n) for nom, n in options.items()}
    cout_fenetres = 30 * cout_attention(4000, 128, 128)
    n_bascule = nb_anom + (1 - seuil) / seuil * nb_anom * math.exp(delta)
    n_bascule_moins10 = nb_anom + (1 - seuil) / seuil * nb_anom * math.exp(0.9 * delta)
    part_moins10 = part_anomalies(4000, 0.9 * delta)
    print(f"cas 4 CRYPTO : coût brut {couts['brut']:.4e}, agrégé {couts['agrégé']:.4e}, fenêtres {cout_fenetres:.4e} ;"
          f" rapport {couts['brut'] // couts['agrégé']}")
    print(f"  part du poids sur les anomalies : brut {parts['brut']:.5f}, agrégé {parts['agrégé']:.5f} ;"
          f" n de bascule {n_bascule:.1f} ; Δ − 10 % : bascule {n_bascule_moins10:.1f}, part {part_moins10:.5f}")
    decision = "agrégation retenue" if options["agrégé"] <= n_bascule else "agréger davantage"
    decision_moins10 = "agrégation retenue" if options["agrégé"] <= n_bascule_moins10 else "tranches de dix minutes"
    print(f"  décision : 4000 <= {math.floor(n_bascule)} -> {decision} ; avec Δ − 10 % : 4000 > {math.floor(n_bascule_moins10)} -> {decision_moins10}")
    return couts, parts, cout_fenetres, n_bascule, n_bascule_moins10, part_moins10, decision, decision_moins10


def main() -> None:
    # Film du mécanisme (exemple de la fiche et de la leçon)
    Kf = [(0.9, 0.1), (0.1, 0.9), (0.5, 0.5)]
    pf, of = attention((1.0, 0.0), Kf, Kf)
    sf = [x / math.sqrt(2) for x in (0.9, 0.1, 0.5)]
    print(f"film : scores/√2 {r5(sf)} ; e^s {r5([math.exp(x) for x in sf])} ; poids {r5(pf)} ; sortie {r5(of)}")
    assert r5(sf) == [0.6364, 0.07071, 0.35355]
    assert r5([math.exp(x) for x in sf]) == [1.88966, 1.07327, 1.42412] and round(sum(math.exp(x) for x in sf), 5) == 4.38705
    assert r5(pf) == [0.43074, 0.24465, 0.32462] and r5(of) == [0.57444, 0.42556]

    # Exemple simple
    K = [(1, 0), (0, 1), (1, 1)]
    poids, sortie = attention((1, 1), K, K)
    s = [x / math.sqrt(2) for x in (1, 1, 2)]
    e = [math.exp(x - max(s)) for x in s]
    print(f"exemple : s {r5(s)} ; e^(s−max) {r5(e)}, somme {sum(e):.5f} ; poids {r5(poids)} ; sortie {r5(sortie)}")
    assert r5(s) == [0.70711, 0.70711, 1.41421] and r5(e) == [0.49307, 0.49307, 1.0] and round(sum(e), 5) == 1.98614
    assert r5(poids) == [0.24826, 0.24826, 0.50349] and r5(sortie) == [0.75174, 0.75174]

    # Démonstration 1 : moyenne pondérée, chaque coordonnée entre min et max
    V = [(3.0, -1.0), (0.5, 4.0), (-2.0, 2.0)]
    Kv = [(1, 2), (0, 1), (-1, 0.5)]
    poids_v, sortie_v = attention((0.3, -0.7), Kv, V)
    for c in range(2):
        assert min(v[c] for v in V) <= sortie_v[c] <= max(v[c] for v in V)
    assert abs(sum(poids_v) - 1) < 1e-12
    print(f"démo 1 : poids {r5(poids_v)} ; sortie {r5(sortie_v)} dans [−2 ; 3] × [−1 ; 4]")
    assert r5(poids_v) == [0.27016, 0.35847, 0.37137] and r5(sortie_v) == [0.24696, 1.90647]
    sv = [x / math.sqrt(2) for x in (-1.1, -0.7, -0.65)]
    ev = [math.exp(x - max(sv)) for x in sv]
    assert r5(sv) == [-0.77782, -0.49497, -0.45962] and r5([x - max(sv) for x in sv]) == [-0.3182, -0.03536, 0.0]
    assert r5(ev) == [0.72746, 0.96526, 1.0] and round(sum(ev), 5) == 2.69272

    # Démonstration 2 : variance d_k, exacte par énumération (coordonnées ±1) puis simulée (gaussiennes)
    dk4 = 4
    produits = [sum(a * b for a, b in zip(c[:dk4], c[dk4:])) for c in itertools.product((-1, 1), repeat=2 * dk4)]
    var_exacte = sum(x * x for x in produits) / len(produits) - (sum(produits) / len(produits)) ** 2
    rng = random.Random(7)
    dk, tirages = 16, 20_000
    scores = [sum(rng.gauss(0, 1) * rng.gauss(0, 1) for _ in range(dk)) for _ in range(tirages)]
    var = sum(s * s for s in scores) / tirages
    biais = [sum(a * b for a, b in zip(c[:dk4], c[dk4:])) for c in itertools.product((0, 1), repeat=2 * dk4)]
    m_b = sum(biais) / len(biais)
    v_b = sum(x * x for x in biais) / len(biais) - m_b ** 2
    print(f"démo 2 : Var exacte (±1, d_k = 4) = {var_exacte:.4f} ; simulée (d_k = 16) = {var:.2f} ;"
          f" contre-exemple {{0 ; 1}} : moyenne {m_b:.2f}, variance {v_b:.4f}")
    assert var_exacte == 4.0 and abs(var - dk) < 0.5 and round(var, 2) == 16.04
    assert m_b == 1.0 and v_b == 0.75 and 0.25 * 64 / 8 == 2.0

    # Démonstration 3 : permuter les couples (clé ; valeur) ne change rien
    _, permutee = attention((0.3, -0.7), [Kv[2], Kv[0], Kv[1]], [V[2], V[0], V[1]])
    assert all(math.isclose(a, b) for a, b in zip(sortie_v, permutee))
    _, desappariee = attention((0.3, -0.7), [Kv[2], Kv[0], Kv[1]], V)
    print(f"démo 3 : permutée {r5(permutee)} ; clés seules permutées {r5(desappariee)}")
    assert r5(desappariee) == [0.53225, 1.4262] and not math.isclose(desappariee[0], sortie_v[0])

    # Démonstration 4 : multiplications comptées dans les boucles
    comptes = []
    for n in (3, 6):
        compteur = {"mult": 0}
        X = [[0.1 * (i + 1), 0.2] for i in range(n)]
        for x in X:
            attention(x, X, X, compteur=compteur)
        comptes.append(compteur["mult"])
        assert compteur["mult"] == cout_attention(n, 2, 2)
    print(f"démo 4 : multiplications comptées n = 3 : {comptes[0]}, n = 6 : {comptes[1]} ;"
          f" n = 4 096, d = 128 : {cout_attention(4096, 128, 128):,}")
    assert comptes == [36, 144] and cout_attention(4096, 128, 128) == 4_294_967_296

    # Démonstration 5 : dilution et avance nécessaire
    a4, a40 = poids_cle_utile(2, 4), poids_cle_utile(2, 40)
    d40 = 2 + math.log(13)
    print(f"démo 5 : poids {a4:.5f} (4 clés), {a40:.5f} (40 clés) ; Δ' = {d40:.5f} -> {poids_cle_utile(d40, 40):.5f} ;"
          f" pente a(1 − a) = {a4 * (1 - a4):.5f}")
    assert round(a4, 5) == 0.71123 and round(a40, 5) == 0.15928 and round(d40, 5) == 4.56495
    assert math.isclose(poids_cle_utile(d40, 40), a4) and round(a4 * (1 - a4), 5) == 0.20538
    h = 1e-6
    assert math.isclose((poids_cle_utile(2 + h, 4) - poids_cle_utile(2 - h, 4)) / (2 * h), a4 * (1 - a4), rel_tol=1e-6)
    assert round(0.20538 * 0.02, 5) == 0.00411 and round(poids_cle_utile(2.02, 4) - a4, 5) == 0.00409
    assert round(math.log(13), 5) == 2.56495 and round(math.exp(2) / 10.38906, 5) == 0.71123

    # Démonstration 6 : masque causal, poids exactement nuls, ligne vide refusée
    X = [(0.9, 0.1), (0.1, 0.9), (0.5, 0.5)]
    M = masque_causal(3)
    lignes = [attention(X[i], X, X, masque=M[i]) for i in range(3)]
    print(f"démo 6 : token 2 poids {[round(p, 4) for p in lignes[1][0]]}, sortie {[round(x, 4) for x in lignes[1][1]]}")
    assert lignes[0][0] == [1.0, 0.0, 0.0] and [round(p, 4) for p in lignes[1][0]] == [0.3888, 0.6112, 0.0]
    assert lignes[1][0][2] == 0.0 and [round(x, 4) for x in lignes[1][1]] == [0.411, 0.589]
    assert all(abs(p - 1 / 3) < 1e-12 for p in lignes[2][0])
    s2 = [sum(a * b for a, b in zip(X[1], x)) for x in X]
    assert [round(x, 10) for x in s2] == [0.18, 0.82, 0.5] and r5([x / math.sqrt(2) for x in s2[:2]]) == [0.12728, 0.57983]
    assert round((0.18 - 0.82) / math.sqrt(2), 5) == -0.45255 and round(math.exp((0.18 - 0.82) / math.sqrt(2)), 5) == 0.63601
    assert r5(lignes[1][0][:2]) == [0.38876, 0.61124]
    try:
        attention(X[0], X, X, masque=[-math.inf] * 3)
    except ValueError:
        pass
    else:
        raise AssertionError("une ligne entièrement masquée aurait dû être refusée")

    # Cas
    res1, lam_b, lam_5, dec1 = cas_1_facture_btp()
    assert dec1 == "extraction par outil"
    assert round(lam_5, 2) == 11.87
    assert r5(res1[1.0][0]) == [0.42693, 0.25895, 0.15706, 0.15706] and round(res1[1.0][1]) == 3364
    assert r5(res1[4.0][0]) == [0.85327, 0.11548, 0.01563, 0.01563] and round(res1[4.0][1]) == 1898
    assert round(lam_b, 5) == 1.38629 and r5(res1[lam_b][0]) == [0.5, 0.25, 0.125, 0.125] and round(res1[lam_b][1]) == 3300
    assert 8000 ** 2 * 128 == 8_192_000_000 and 8000 ** 2 * 128 * 32 == 262_144_000_000 and (16000 / 8000) ** 2 == 4
    assert round(math.exp(1), 5) == 2.71828 and round(math.exp(0.5), 5) == 1.64872 and round(math.exp(1) + math.exp(0.5) + 2, 5) == 6.367
    assert round(1.1 * lam_b, 5) == 1.52492 and round(attention([1.1 * lam_b * x for x in (1, 0, 1, 0)],
                                                                [(1, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)],
                                                                [(1,), (0,), (0,), (0,)])[0][0], 5) == 0.52582
    assert 0.05 * 12000 == 600 and 3364 - 600 == 2764 and round(2764 / 600, 1) == 4.6
    p1 = res1[1.0][0]
    assert round(p1[0] * 600, 2) == 256.16 and round(p1[1] * 12000, 2) == 3107.37 and round(res1[1.0][1], 2) == 3363.53
    p4 = res1[4.0][0]
    assert round(p4[0] * 600, 2) == 511.96 and round(p4[1] * 12000, 2) == 1385.73 and round(res1[4.0][1], 2) == 1897.69
    assert round(math.exp(4), 5) == 54.59815 and round(math.exp(4) + math.exp(2) + 2, 5) == 63.98721

    a_b, a_c, d_req, n_max, a_p10, n_max_p10, rembourse, dec2 = cas_2_franchise_assurance()
    assert dec2 == "compaction en 4 blocs"
    assert round(a_b, 5) == 0.15928 and round(a_c, 5) == 0.71123 and round(d_req, 5) == 4.56495
    assert n_max == 8 and round(math.exp(2), 5) == 7.38906 and round(1 + math.exp(2), 3) == 8.389
    assert round(poids_cle_utile(2, 8), 5) == 0.51352 and round(poids_cle_utile(2, 9), 5) == 0.48015
    assert round(a_p10, 5) == 0.18792 and n_max_p10 == 10 and rembourse == 1800 and round(math.exp(2.2), 5) == 9.02501
    assert 12 * 500 == 6000 and round(d_req / 2, 2) == 2.28
    assert round(poids_cle_utile(2.2, 10), 5) == 0.50069 and round(poids_cle_utile(2.2, 11), 5) == 0.47438

    r3 = cas_3_releves_banque()
    ratio_oubli, ratio_total, m_max, montant_max, sal_b, m_max_m10, a_rel, a_out, gain, plafond_ok, dec3 = r3
    assert dec3 == "contre-offre 148000 AED sur 48 mois"
    assert round(ratio_oubli, 3) == 0.435 and round(ratio_total, 2) == 0.54 and ratio_total > 0.5 >= ratio_oubli
    assert m_max == 3700 and round(montant_max) == 148000 and sal_b == 21600 and m_max_m10 == 2700
    assert round(a_rel, 5) == 0.00665 and round(a_out, 5) == 0.90944 and gain == 10_000 and plafond_ok
    assert round(math.exp(3), 5) == 20.08554 and 30000 ** 2 * 256 == 230_400_000_000 and 300 ** 2 * 256 == 23_040_000
    assert 20 * 20000 == 400_000 and 4500 * 48 == 216_000

    couts, parts, c_fen, n_b, n_b_m10, part_m10, dec4, dec4_m10 = cas_4_journaux_crypto()
    assert dec4 == "agrégation retenue" and dec4_m10 == "tranches de dix minutes"
    assert couts["brut"] == 3_686_400_000_000 and couts["agrégé"] == 4_096_000_000 and couts["brut"] // couts["agrégé"] == 900
    assert c_fen == 122_880_000_000 and couts["brut"] // c_fen == 30
    assert round(parts["brut"], 5) == 0.00543 and round(parts["agrégé"], 5) == 0.14111 and parts["agrégé"] >= 0.10
    assert round(n_b, 1) == 5908.6 and round(n_b_m10, 1) == 3964.6 and round(part_m10, 5) == 0.0992 and part_m10 < 0.10
    assert round(12 * math.exp(4), 2) == 655.18 and round(math.exp(3.6), 5) == 36.59823
    assert round(12 * math.exp(3.6), 2) == 439.18 and round(poids_cle_utile(4, 4000), 5) == 0.01347

    # Corrigé
    p, o = attention((1, 1), [(1, 1), (1, 1)], [(10, 0), (0, 10)])
    e7a, e7b = softmax([16 / 8, 0])[0], softmax([16 / 64, 0])[0]
    print("Corrigé")
    print(f"  ex1 5 × 32 ; ex2 {p} -> {o} ; ex3 {math.sqrt(64):.0f} puis 1 ; ex4 x{(12000 / 4000) ** 2:.0f}")
    print(f"  ex6 n max {math.floor(1 + math.exp(3))}, poids à 40 messages {poids_cle_utile(3, 40):.5f} ;"
          f" ex7 /8 -> {e7a:.5f}, /64 -> {e7b:.5f}")
    assert p == [0.5, 0.5] and o == [5.0, 5.0] and (12000 / 4000) ** 2 == 9
    assert math.floor(1 + math.exp(3)) == 21 and round(poids_cle_utile(3, 40), 5) == 0.33994
    assert round(e7a, 5) == 0.8808 and round(e7b, 5) == 0.56218 and 1 / 64 == 0.015625
    assert round(math.exp(0.25), 5) == 1.28403 and round(1 + math.exp(3), 5) == 21.08554 and round(math.exp(3) + 39, 5) == 59.08554
    # nombres cités dans le texte : √128, e, 2⁸ combinaisons, variance d'un produit {0 ; 1}, part de 11,5 %
    assert round(math.sqrt(128), 2) == 11.31 and round(math.e, 3) == 2.718 and 2 ** 8 == 256
    assert 0.25 - 0.25 ** 2 == 0.1875 and 4 * 0.1875 == 0.75 and round(100 * res1[4.0][0][1], 1) == 11.5 and 12000 / 600 == 20
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
film : scores/√2 [0.6364, 0.07071, 0.35355] ; e^s [1.88966, 1.07327, 1.42412] ; poids [0.43074, 0.24465, 0.32462] ; sortie [0.57444, 0.42556]
exemple : s [0.70711, 0.70711, 1.41421] ; e^(s−max) [0.49307, 0.49307, 1.0], somme 1.98614 ; poids [0.24826, 0.24826, 0.50349] ; sortie [0.75174, 0.75174]
démo 1 : poids [0.27016, 0.35847, 0.37137] ; sortie [0.24696, 1.90647] dans [−2 ; 3] × [−1 ; 4]
démo 2 : Var exacte (±1, d_k = 4) = 4.0000 ; simulée (d_k = 16) = 16.04 ; contre-exemple {0 ; 1} : moyenne 1.00, variance 0.7500
démo 3 : permutée [0.24696, 1.90647] ; clés seules permutées [0.53225, 1.4262]
démo 4 : multiplications comptées n = 3 : 36, n = 6 : 144 ; n = 4 096, d = 128 : 4,294,967,296
démo 5 : poids 0.71123 (4 clés), 0.15928 (40 clés) ; Δ' = 4.56495 -> 0.71123 ; pente a(1 − a) = 0.20538
démo 6 : token 2 poids [0.3888, 0.6112, 0.0], sortie [0.411, 0.589]
cas 1 BTP : poids λ=1 [0.42693, 0.25895, 0.15706, 0.15706] ; lecture 3364 AED
  bascule λ* = 2 ln 2 = 1.38629 : poids [0.5, 0.25, 0.125, 0.125], lecture 3300 AED ; λ=4 : [0.85327, 0.11548, 0.01563, 0.01563], lecture 1898 AED
  lecture à 5 % près dès λ = 11.87 ; coût Q Kᵀ : 8 000 tokens, d_k 128 : 8,192,000,000 par tête ; 32 têtes : 262,144,000,000
  décision : extraction par outil (poids TVA 0.42693, écart de lecture 2764 AED) ; contrôle 5 % du HT = 600 AED
cas 2 ASSUR : poids de la clause 0.15928 (40 messages) -> 0.71123 (4 blocs) ; Δ requis 4.56495 ; n max 8
  Δ + 10 % : poids 0.18792, n max 10 ; remboursement 1800 AED, promesse fausse 2300 AED
  décision : 40 messages > 8 blocs -> compaction en 4 blocs
cas 3 BANQUE : ratio sans le crédit auto 43.5%, ratio total 54.0% ; mensualité max 3700 AED ; montant max 148000 AED
  poids de la ligne auto : 0.00665 (3 000 lignes) contre 0.90944 (3 lignes) ; calcul d'attention divisé par 10,000 ; salaire de bascule 21600 AED
  décision : ratio 54.0% > 50 % -> contre-offre 148000 AED sur 48 mois
cas 4 CRYPTO : coût brut 3.6864e+12, agrégé 4.0960e+09, fenêtres 1.2288e+11 ; rapport 900
  part du poids sur les anomalies : brut 0.00543, agrégé 0.14111 ; n de bascule 5908.6 ; Δ − 10 % : bascule 3964.6, part 0.09920
  décision : 4000 <= 5908 -> agrégation retenue ; avec Δ − 10 % : 4000 > 3964 -> tranches de dix minutes
Corrigé
  ex1 5 × 32 ; ex2 [0.5, 0.5] -> [5.0, 5.0] ; ex3 8 puis 1 ; ex4 x9
  ex6 n max 21, poids à 40 messages 0.33994 ; ex7 /8 -> 0.88080, /64 -> 0.56218
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme calcule la sortie de l'attention pour une requête : scores avec chaque clé, mise à l'échelle, masque éventuel, softmax, puis moyenne pondérée des valeurs. En auto-attention, on le répète pour chacune des n requêtes.

```text
ALGORITHME AttentionUneRequête
ENTRÉES : requête q (dimension dₖ), clés k₁ … kₘ, valeurs v₁ … vₘ (dimension dᵥ),
          masque M₁ … Mₘ facultatif (0 ou −∞)
SORTIE  : (poids a₁ … aₘ, sortie o)

  SI une clé n'a pas la dimension dₖ OU le nombre de clés ≠ nombre de valeurs ALORS ERREUR
  POUR j DE 1 À m FAIRE
      sⱼ ← (q · kⱼ) / √dₖ + Mⱼ
  FIN POUR
  SI max(s) = −∞ ALORS ERREUR                     (aucune clé autorisée : poids 0/0)
  a ← Softmax(s₁ … sₘ)                            (on retire le maximum avant l'exponentielle)
  POUR c DE 1 À dᵥ FAIRE
      o_c ← 0
      POUR j DE 1 À m FAIRE
          o_c ← o_c + aⱼ × vⱼ,c
      FIN POUR
  FIN POUR
  RETOURNER a, o
```

**Complexité.** Pour une requête : O(m × dₖ) pour les scores et O(m × dᵥ) pour le mélange. Pour n requêtes sur n clés (auto-attention) : exactement n²(dₖ + dᵥ) multiplications et n² scores, d'où le facteur 4 quand la longueur double et le facteur r² quand on divise le contexte par r.

**Du squelette au code.** AttentionUneRequête est la fonction `attention(q, K, V)` : la boucle sur `K` calcule les `scores` divisés par `math.sqrt(dk)` et leur ajoute le `masque` s'il est donné, `softmax` donne les poids et lève `ValueError` si tout est masqué, et la dernière boucle fait la moyenne pondérée colonne par colonne en comptant les multiplications dans `compteur`. `masque_causal` construit le masque de la démonstration 6, `poids_cle_utile` la dilution de la démonstration 5 et `cout_attention` le décompte de la démonstration 4. La simulation de la variance (démonstration 2) est la liste `scores` de `main`. Les quatre cas sont `cas_1_facture_btp`, `cas_2_franchise_assurance`, `cas_3_releves_banque` et `cas_4_journaux_crypto`.
