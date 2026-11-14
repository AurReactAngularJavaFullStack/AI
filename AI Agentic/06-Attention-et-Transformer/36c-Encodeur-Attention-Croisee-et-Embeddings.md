# Étape 36 ter — Transformer — Encodeur, attention croisée et embeddings

**Dossier :** 06-Attention-et-Transformer

> Étape 36 ter du parcours · Prérequis : [Mélange d'experts (MoE)](<36b-Melange-d-Experts-MoE.md>) · Suite : [Transformer : formules de liaison](<37-Transformer-Formules-de-Liaison.md>)

## Définition

Les étapes 31 à 36 ont décrit une seule brique, l'attention, et ses accessoires. Avec cette même brique, on construit trois familles de modèles. L'**encodeur** (la famille de BERT) lit tout le texte d'un coup, sans masque : chaque token voit ses voisins de gauche et de droite, ce qui en fait un bon lecteur, mais pas un rédacteur. Le **décodeur causal** (la famille de GPT, celle des LLM qui pilotent les agents) applique le masque causal de l'étape 31 : chaque token ne voit que le passé, ce qui permet d'écrire de gauche à droite. L'**encodeur-décodeur** (le Transformer d'origine, la famille de T5) relie les deux par l'**attention croisée** : les requêtes Q viennent du décodeur, les clés K et les valeurs V viennent de la sortie de l'encodeur. Enfin, un **modèle d'embedding** est un encodeur dont on moyenne les vecteurs de sortie pour obtenir un vecteur par phrase, entraîné par **apprentissage contrastif** (perte InfoNCE) à rapprocher une question de son document et à l'éloigner des autres documents du lot.

## Rôle dans un agent

Un agent utilise souvent les trois familles sans le savoir. Le LLM qui **décide** est un décodeur. Le retriever qui **perçoit** le contexte (étapes 14 à 25) compare des vecteurs produits par un encodeur entraîné en bi-encodeur : les documents sont encodés une fois, hors ligne, la question l'est à chaque requête, et le cosinus de l'étape 19 fait le reste. Le reranker de l'étape 30 bis est un cross-encodeur : un encodeur qui lit la question et le document **ensemble**, et c'est précisément le modèle que l'étape 30 bis remplaçait par un jouet. Les petits classifieurs de garde-fous, de routage ou de détection d'injection sont souvent des encodeurs, parce qu'ils coûtent beaucoup moins cher qu'un appel de LLM. Savoir comment ces modèles sont entraînés permet de régler leurs défauts : pourquoi deux questions sur le même produit se gênent dans un lot, pourquoi un embedding change avec le remplissage du lot, pourquoi changer de modèle d'embedding oblige à réindexer tout le corpus. C'est aussi ce qui rend l'équipe indépendante d'un fournisseur : un modèle d'embedding se réentraîne et s'héberge en interne avec les formules de cette étape.

## Équation complète

Les trois familles utilisent l'attention de l'étape 31 ; seuls changent le masque M et l'origine de K et V. Encodeur et décodeur :

$$
\text{encodeur : } M = 0, \qquad \text{décodeur : } M_{ij} = \begin{cases} 0 & \text{si } j \le i \\ -\infty & \text{si } j > i \end{cases}
$$

Attention croisée : les requêtes viennent des états du décodeur Y, les clés et les valeurs de la sortie H de l'encodeur :

$$
Q = Y W_Q^{c}, \qquad K = H W_K^{c}, \qquad V = H W_V^{c}
$$

Formes des matrices :

$$
Q \in \mathbb{R}^{n_{dec} \times d_k}, \qquad K \in \mathbb{R}^{n_{enc} \times d_k}, \qquad V \in \mathbb{R}^{n_{enc} \times d_v}
$$

$$
A = \operatorname{softmax}\left( \frac{Q K^\top}{\sqrt{d_k}} \right) \in \mathbb{R}^{n_{dec} \times n_{enc}}, \qquad A V \in \mathbb{R}^{n_{dec} \times d_v}
$$

Modèle de langue masqué (MLM), sur l'ensemble ℳ des positions masquées :

$$
\mathcal{L}_{\text{MLM}} = -\frac{1}{\lvert \mathcal{M} \rvert} \sum_{i \in \mathcal{M}} \ln p_\theta\bigl(x_i \mid \tilde{x}\bigr), \qquad \lvert \mathcal{M} \rvert = \operatorname{round}(0{,}15\, n)
$$

Embedding de phrase par moyenne des vrais tokens, puis normalisation :

$$
\mathbf{e} = \frac{\sum_{i=1}^{n} m_i \, \mathbf{h}_i}{\sum_{i=1}^{n} m_i}, \qquad \hat{\mathbf{e}} = \frac{\mathbf{e}}{\lVert \mathbf{e} \rVert}
$$

Similarité dans un lot de B paires (requête, document) :

$$
s_{ij} = \hat{\mathbf{q}}_i \cdot \hat{\mathbf{d}}_j
$$

Perte contrastive InfoNCE, les autres documents du lot servant de négatifs :

$$
\mathcal{L}_{\text{InfoNCE}} = -\frac{1}{B} \sum_{i=1}^{B} \ln \frac{e^{s_{ii}/\tau}}{\sum_{j=1}^{B} e^{s_{ij}/\tau}}
$$

Son gradient par rapport aux similarités :

$$
\frac{\partial \mathcal{L}_{\text{InfoNCE}}}{\partial s_{ij}} = \frac{p_{ij} - \mathbf{1}[j = i]}{B\,\tau}, \qquad p_{ij} = \frac{e^{s_{ij}/\tau}}{\sum_{r=1}^{B} e^{s_{ir}/\tau}}
$$

Coût d'une journée de recherche : bi-encodeur, cross-encodeur seul, et les deux étages enchaînés :

$$
C_{\text{bi}} = N \, c(\ell_d) + R \, c(\ell_q) + R \, N \, d_e
$$

$$
C_{\text{cross}} = R \, N \, c(\ell_q + \ell_d)
$$

$$
C_{\text{2 étages}} = R \, c(\ell_q) + R \, N \, d_e + R \, n_{top} \, c(\ell_q + \ell_d)
$$

## Décryptage des symboles

$$
X, \; H
$$

Les vecteurs des tokens source à l'entrée de l'encodeur, et la sortie de l'encodeur : deux matrices n_enc × d_model ; variables Python `X` et `H`.

$$
Y
$$

Les états des tokens que le décodeur a déjà produits : une matrice n_dec × d_model ; variable Python `Y`.

$$
n_{enc}, \; n_{dec}
$$

Le nombre de tokens de la source et le nombre de tokens déjà générés : des entiers ≥ 1, 5 et 3 dans le programme ; `len(X)` et `len(Y)`.

$$
d_{model}, \; d_k, \; d_v
$$

La largeur des vecteurs du modèle, celle des requêtes et des clés, celle des valeurs (étape 34) : des entiers, 8, 4 et 4 dans le programme ; `d_model`, `d_k`.

$$
W_Q^{c}, \; W_K^{c}, \; W_V^{c}
$$

Les projections propres à l'attention croisée, distinctes de celles de l'auto-attention : des matrices d_model × d_k (ou d_model × d_v) ; `Wc_Q`, `Wc_K`, `Wc_V`.

$$
M
$$

Le masque additif de l'étape 31 : nul pour l'encodeur, causal pour le décodeur, nul aussi pour l'attention croisée (le décodeur peut lire toute la source) ; `masque_causal(n)`.

$$
A
$$

La matrice des poids d'attention croisée : n_dec lignes, n_enc colonnes, chaque ligne positive de somme 1 ; `p_croise`.

$$
\mathcal{M}
$$

L'ensemble des positions masquées dans une phrase de n tokens, environ 15 % d'entre elles ; `positions`.

$$
\tilde{x}
$$

La phrase corrompue que lit l'encodeur : 80 % des positions de ℳ deviennent `[MASK]`, 10 % un token tiré au hasard, 10 % restent inchangées ; `entree`.

$$
p_\theta\bigl(x_i \mid \tilde{x}\bigr)
$$

La probabilité que le modèle, de paramètres θ, attribue au vrai token xᵢ à la position i, en lisant toute la phrase corrompue des deux côtés : un réel dans ]0 ; 1[.

$$
\mathbf{h}_i, \; m_i
$$

Le vecteur de sortie de l'encodeur pour le token i, et l'indicateur qui vaut 1 si ce token est réel, 0 s'il s'agit d'un remplissage ajouté pour aligner les phrases d'un lot ; `vecteurs`, `masque`.

$$
\mathbf{e}, \; \hat{\mathbf{e}}
$$

L'embedding de la phrase, moyenne des vrais tokens, puis sa version de norme 1 : des vecteurs de d_e réels ; `moyenne_masquee(...)`, `normaliser(...)`.

$$
\hat{\mathbf{q}}_i, \; \hat{\mathbf{d}}_j
$$

L'embedding normalisé de la requête i et celui du document j du lot ; dans le programme, le troisième élément renvoyé par `encoder(Eq, ...)` et `encoder(Ed, ...)`.

$$
s_{ij}
$$

Le cosinus entre la requête i et le document j, dans [−1 ; 1] ; la diagonale sᵢᵢ porte les paires positives ; matrice `S`.

$$
B
$$

La taille du lot : le nombre de paires, donc aussi le nombre de classes du petit problème de classification que résout chaque ligne ; `B`.

$$
\tau
$$

La température de l'InfoNCE, un réel > 0, souvent entre 0,01 et 0,1 ; `tau`. Elle joue exactement le rôle de la température T de l'étape 2. Dans ce fichier, τ ne désigne qu'elle ; ailleurs dans le parcours, τ est un seuil de décision.

$$
p_{ij}
$$

La probabilité que la requête i attribue au document j, softmax de la ligne i à la température τ ; calculée dans `gradient_info_nce`.

$$
N, \; R, \; n_{top}
$$

Le nombre de documents de l'index, le nombre de requêtes par jour, et le nombre de candidats que le premier étage passe au cross-encodeur ; arguments `n_docs`, `requetes`, `n_top` de `couts`.

$$
\ell_q, \; \ell_d, \; c(\ell), \; d_e
$$

La longueur en tokens d'une requête et d'un document, le coût d'un passage d'encodeur sur ℓ tokens, et la dimension des embeddings ; `l_q`, `l_d`, et `d` dans la partie 6 du programme.

## Démonstration

### 1. Les trois familles ne diffèrent que par le masque et par l'origine de K et V

Dans l'encodeur, M = 0 : le poids a₁ⱼ de la première position sur la position j est strictement positif pour tout j, parce qu'une exponentielle est toujours positive. La sortie o₁ dépend donc de **tous** les tokens, y compris du dernier. Dans le décodeur, le masque causal met le score à −∞ pour j > 1, donc a₁ⱼ = 0 exactement, puisque exp(−∞) = 0, et o₁ = v₁ : la première sortie ne dépend que du premier token. Le programme le vérifie en modifiant le dernier token : la première sortie de l'encodeur bouge de 0,1352, celle du décodeur de 0,0, au bit près.

Cette différence décide de la façon d'entraîner chaque famille. Un décodeur peut apprendre à prédire le token suivant à **chaque** position, puisqu'aucune position ne voit son successeur. Un encodeur ne le peut pas : à la position i, il voit déjà le token i + 1, et la tâche « prédire la suite » serait triviale. On l'entraîne donc à reconstituer des tokens cachés (point 3).

### 2. Les formes de l'attention croisée

Le décodeur a produit n_dec tokens ; leurs états forment Y, de taille n_dec × d_model. L'encodeur a lu n_enc tokens source ; sa sortie H est de taille n_enc × d_model. On projette :

$$
Q = Y W_Q^{c} \in \mathbb{R}^{n_{dec} \times d_k}, \qquad K = H W_K^{c} \in \mathbb{R}^{n_{enc} \times d_k}, \qquad V = H W_V^{c} \in \mathbb{R}^{n_{enc} \times d_v}
$$

parce qu'une matrice a × b multipliée par une matrice b × c donne une matrice a × c. Le produit QKᵀ multiplie n_dec × d_k par d_k × n_enc : la matrice des scores a **n_dec lignes et n_enc colonnes**, elle n'est plus carrée. Chaque ligne est une softmax sur les positions de la source, donc chaque sortie est une moyenne pondérée des n_enc lignes de V, de taille d_v : le résultat AV est n_dec × d_v. Avec les tailles du programme, Q est 3 × 4, K et V sont 5 × 4, A est 3 × 5 et la sortie 3 × 4.

Deux conséquences pratiques. D'abord, une moyenne pondérée à poids positifs de somme 1 reste entre le minimum et le maximum de chaque colonne de V : le décodeur ne peut rien « inventer » par l'attention croisée, il ne peut que combiner ce que l'encodeur a écrit. Ensuite, H ne dépend que de la source : K et V se calculent **une fois** par texte source, puis servent à chaque token généré, comme le cache KV de l'étape 33 bis. Chaque nouveau token ne paie qu'une ligne de scores, soit n_enc produits scalaires de longueur d_k.

### 3. Le modèle de langue masqué

On choisit ℳ, environ 15 % des positions : pour n = 512 tokens, round(0,15 × 512) = round(76,8) = 77 positions. La perte ne porte que sur ces positions, et chaque prédiction s'appuie sur la phrase corrompue des deux côtés. Elle part de ln |V| pour un modèle qui ne sait rien et prédit uniformément : avec un vocabulaire de 30 000 tokens, ordre de grandeur de celui de BERT, ln 30 000 = 10,309 (la perplexité de l'étape 52 vaut alors exp(10,309) = 30 000). Le partage 80 / 10 / 10 vient de l'article de BERT (Devlin et al., 2018) : le token `[MASK]` n'apparaît jamais après l'entraînement, donc le modèle doit aussi produire de bons vecteurs pour des tokens réels ; et comme 10 % des positions choisies portent un token faux, il ne peut pas faire confiance aveuglément à ce qu'il lit. Contrepartie : une phrase de 512 tokens fournit 77 cibles au MLM, contre 511 pour un décodeur qui prédit chaque token suivant, soit 6,6 fois moins de signal par phrase lue.

### 4. Embedding de phrase : moyenne masquée, puis normalisation

Les phrases d'un lot sont alignées sur la plus longue par des tokens de remplissage. Avec la moyenne masquée, un remplissage a mᵢ = 0 : il n'entre ni au numérateur ni au dénominateur, donc l'embedding d'une phrase **ne dépend pas** du nombre de remplissages, ni donc du lot dans lequel elle passe. Sans masque, il en dépend. Contre-exemple chiffré : deux tokens réels h₁ = (1 ; 2) et h₂ = (3 ; 0), et deux remplissages (0,5 ; −1). La moyenne masquée vaut (2 ; 1) ; la moyenne naïve vaut ((1 + 3 + 0,5 + 0,5) / 4 ; (2 + 0 − 1 − 1) / 4) = (1,25 ; 0). Le cosinus entre les deux vaut 2,5 / (√5 × 1,25) = 2/√5 = 0,8944 : la même phrase a deux embeddings différents selon son voisinage de lot. Après normalisation, ‖ê‖ = 1, donc le produit scalaire de deux embeddings normalisés **est** leur cosinus (étape 19) : un index qui cherche le plus grand produit scalaire cherche le plus grand cosinus.

### 5. InfoNCE est une entropie croisée sur le lot

Fixons la ligne i. Posons zⱼ = sᵢⱼ / τ pour j = 1, …, B. Le terme de la ligne i s'écrit

$$
\mathcal{L}_i = -\ln \frac{e^{z_i}}{\sum_{j=1}^{B} e^{z_j}} = -\ln \operatorname{softmax}(z)_i
$$

C'est exactement l'entropie croisée de l'étape 2, pour un problème à B classes dont la bonne classe est i, avec la température T = τ. La requête i résout une petite classification : « parmi les B documents du lot, lequel est le mien ? ». Les B − 1 autres documents sont les négatifs, et ils ne coûtent rien : ils ont déjà été encodés pour leurs propres requêtes. L'étape 2 a démontré que le gradient de −ln pᶜ par rapport à zⱼ vaut pⱼ − yⱼ ; comme zⱼ = sᵢⱼ / τ, la règle de la chaîne divise par τ, et la moyenne sur les B lignes divise par B :

$$
\frac{\partial \mathcal{L}_{\text{InfoNCE}}}{\partial s_{ij}} = \frac{1}{B} \cdot \frac{1}{\tau} \bigl(p_{ij} - \mathbf{1}[j = i]\bigr)
$$

Lecture : le gradient sur la diagonale vaut (pᵢᵢ − 1)/(Bτ) < 0, donc la descente **augmente** sᵢᵢ et rapproche la requête de son document ; hors diagonale, il vaut pᵢⱼ/(Bτ) > 0, donc la descente **diminue** sᵢⱼ, et d'autant plus que ce négatif est déjà proche. Si toutes les similarités d'une ligne sont égales, pᵢⱼ = 1/B et ℒᵢ = ln B : un modèle qui ne distingue rien part de ln B, soit ln 256 = 5,5452 pour un lot de 256 paires. C'est le point de départ à lire sur une courbe d'entraînement.

### 6. Ce que fait τ

Notons mᵢ = maxⱼ sᵢⱼ, le maximum de la ligne, positif compris. La somme de B exponentielles est comprise entre la plus grande et B fois la plus grande, donc

$$
\frac{m_i - s_{ii}}{\tau} \;\le\; \mathcal{L}_i \;\le\; \frac{m_i - s_{ii}}{\tau} + \ln B
$$

Trois régimes en découlent.

- **τ petit, positif en tête.** Si sᵢᵢ est le maximum, mᵢ − sᵢᵢ = 0 et la perte reste entre 0 et ln B ; plus précisément, ℒᵢ = ln(1 + ∑ⱼ≠ᵢ exp((sᵢⱼ − sᵢᵢ)/τ)) tend vers 0. Le gradient des négatifs se concentre sur le plus dur : la part du négatif le plus proche est la softmax des négatifs à la température τ, qui tend vers 1. Sur la ligne (0,8 ; 0,6 ; 0,1 ; −0,2), elle vaut 0,993 pour τ = 0,1 et 0,637 pour τ = 0,5.
- **τ petit, négatif en tête.** Si un « négatif » dépasse le positif, la borne basse vaut (mᵢ − sᵢᵢ)/τ et explose comme 1/τ. Avec un négatif à 0,9 contre un positif à 0,8, la perte vaut 1,314, 2,127 puis 5,007 pour τ = 0,1, 0,05 et 0,02, soit à peu près 0,1/τ. C'est le danger des **faux négatifs** : un document du lot aussi pertinent que le positif (deux questions sur le même produit) reçoit un gradient énorme qui l'éloigne à tort.
- **τ grand.** Toutes les probabilités tendent vers 1/B, la part du négatif le plus dur vers 1/(B − 1) (0,348 pour τ = 10, la limite étant 1/3 sur cette ligne de 4) et la perte vers ln B (1,3396 pour τ = 10, contre ln 4 = 1,3863). Comme les cosinus restent dans [−1 ; 1], la perte ne peut jamais descendre sous ln(1 + (B − 1)·exp(−2/τ)) : pour B = 256 et τ = 1, ce plancher vaut ln(1 + 255 e⁻²) ≈ 3,57. Une grande température gaspille l'échelle de la perte et pousse peu sur les négatifs difficiles.

### 7. Bi-encodeur contre cross-encodeur : coût et expressivité

Un **bi-encodeur** encode chaque document seul, une fois : N passages hors ligne. À chaque requête, il encode la question (un passage court), puis calcule N produits scalaires de dimension d_e, ou beaucoup moins avec un index approché (étape 30 quinquies). Un **cross-encodeur** lit la concaténation (question, document) : il n'y a rien à précalculer, et chaque requête coûte N passages sur ℓ_q + ℓ_d tokens. Avec N = 200 000 documents, R = 5 000 requêtes par jour, n_top = 50, ℓ_q = 20 et ℓ_d = 300 :

- le cross-encodeur seul demande R × N = 10⁹ passages par jour, soit 3,2 × 10¹¹ tokens lus ;
- les deux étages demandent R × n_top = 250 000 passages de cross-encodeur, 4 000 fois moins (le rapport vaut N / n_top), et 80 100 000 tokens lus ;
- le bi-encodeur seul ne lit que 100 000 tokens de requêtes par jour, plus le produit scalaire.

Pourquoi garder un cross-encodeur, alors ? Parce que le bi-encodeur a une limite de structure. Son score est un produit scalaire : si F range les R embeddings de requêtes et G les N embeddings de documents, la matrice des scores vaut FGᵀ, et son rang est au plus d_e. Une table de pertinence quelconque ne se représente donc pas exactement. Le cross-encodeur n'a pas cette contrainte : dans chaque couche, chaque token de la question peut regarder chaque token du document. D'où l'architecture standard : un bi-encodeur pour le **rappel** sur tout l'index, un cross-encodeur pour la **précision** sur un petit top-N (étape 30 bis).

### 8. Exemple fait à la main (le code reprend ces nombres)

Un lot de B = 3 paires, avec la matrice de similarités

$$
S = \begin{pmatrix} 0{,}9 & 0{,}2 & 0{,}1 \\ 0{,}3 & 0{,}8 & 0{,}4 \\ 0{,}0 & 0{,}5 & 0{,}7 \end{pmatrix}
$$

Avec τ = 0,1, la ligne 1 donne les logits (9 ; 2 ; 1), donc ℒ₁ = ln(1 + e⁻⁷ + e⁻⁸) = ln 1,001247 = 0,0012. La ligne 2 donne (3 ; 8 ; 4), donc ℒ₂ = ln(1 + e⁻⁵ + e⁻⁴) = ln 1,025054 = 0,0247. La ligne 3 donne (0 ; 5 ; 7), donc ℒ₃ = ln(1 + e⁻⁷ + e⁻²) = ln 1,136247 = 0,1277. La moyenne vaut 0,153726 / 3 = 0,0512.

Avec τ = 1, la ligne 1 donne ln(exp(0,9) + exp(0,2) + exp(0,1)) − 0,9 = ln 4,7862 − 0,9 = 0,6657 ; de même ℒ₂ = 0,8228 et ℒ₃ = 0,8395, pour une moyenne de 0,7760. Les mêmes similarités donnent une perte quinze fois plus forte : à τ = 1, des écarts de 0,2 ou 0,4 entre cosinus ne pèsent presque rien.

Gradient de la ligne 3 pour τ = 0,1 : p₃₃ = 1 / 1,136247 = 0,8801 et p₃₂ = e⁻² × 0,8801 = 0,1191. Donc ∂ℒ/∂s₃₃ = (0,8801 − 1) / 0,3 = −0,3997 et ∂ℒ/∂s₃₂ = 0,1191 / 0,3 = 0,3970 : le positif monte, le négatif le plus proche descend presque autant, et le négatif lointain s₃₁ (p₃₁ = e⁻⁷ × 0,8801 ≈ 0,0008) ne bouge presque pas.

## Effets et comportement

- **Le masque fait la famille.** Sans masque, chaque token lit toute la phrase : on obtient un lecteur (classification, embeddings, reranking). Avec le masque causal, on obtient un rédacteur. L'attention croisée ajoute à un rédacteur une source qu'il peut relire en entier.
- **Le lot fabrique les négatifs.** Un lot de B paires fournit B − 1 négatifs par requête sans encodage supplémentaire ; un lot plus grand rend la tâche plus difficile et la perte de départ, ln B, plus haute.
- **τ règle la dureté.** Petit, il concentre le gradient sur le négatif le plus proche et rend l'entraînement sensible aux faux négatifs ; grand, il traite tous les négatifs pareil et laisse la perte bloquée au-dessus d'un plancher.
- **La moyenne doit être masquée.** Un embedding qui dépend du remplissage dépend du lot ; deux encodages du même texte cessent alors d'être identiques.
- **Le bi-encodeur paie hors ligne, le cross-encodeur à chaque requête.** Le premier passe à l'échelle de l'index entier, le second seulement sur quelques dizaines de candidats.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| softmax(QKᵀ/√dₖ + M) V | `attention(Q, K, V, masque)` |
| masque causal M | `masque_causal(n)` |
| Q, K, V de l'attention croisée | `Qc`, `Kc`, `Vc` |
| ℳ et x̃ | `masquer_mlm(tokens, taux, rng, vocab)` |
| e (moyenne masquée), ê | `moyenne_masquee(vecteurs, masque)`, `normaliser(v)` |
| −ln softmax(z)ᶜ | `entropie_croisee(logits, cible)` |
| ℒ InfoNCE | `info_nce(S, tau)` |
| ∂ℒ/∂sᵢⱼ | `gradient_info_nce(S, tau)` |
| q̂ᵢ, d̂ⱼ et leurs gradients | `encoder(E, mots)`, `perte_et_gradients(Eq, Ed, lot, tau)` |
| Recall@1 | `recall_a_1(Eq, Ed, requetes, corpus)` |
| C_bi, C_cross, C_2 étages | `couts(n_docs, requetes, n_top, l_q, l_d)` |

### Déroulé, ligne par ligne

**`matmul`, `transposer`, `forme`, `log_somme_exp`, `softmax`.** Les outils des étapes 2 et 31. `matmul` refuse deux matrices dont les dimensions intérieures diffèrent ; `forme` renvoie une chaîne comme `"3×5"`. `log_somme_exp(z)` calcule ln ∑ exp(zⱼ) en retranchant d'abord le maximum, ce qui évite tout débordement, et `softmax` en déduit pⱼ = exp(zⱼ − lse).

**`masque_causal(n)`** renvoie une matrice n × n qui vaut `0.0` sur et sous la diagonale et `-math.inf` au-dessus.

**`attention(Q, K, V, masque)`.**

- La garde vérifie que Q et K ont la même largeur d_k, et que K et V ont le même nombre de lignes : c'est la condition qui rend l'attention croisée possible, puisque Q peut avoir un autre nombre de lignes.
- `matmul(Q, transposer(K))` donne la matrice des scores, de taille n_q × n_k.
- Pour chaque ligne, on divise par √d_k, on ajoute le masque, puis on applique la softmax. Un score à `-math.inf` devient `math.exp(-inf) = 0.0` : le poids est exactement nul.
- La fonction renvoie les poids et `matmul(poids, V)`.

**`masquer_mlm(tokens, taux, rng, vocab)`.** `rng.sample` tire `round(taux * n)` positions distinctes, triées. Pour chacune, un tirage `u` décide : sous 0,8, `[MASK]` ; entre 0,8 et 0,9, un token au hasard du vocabulaire ; au-delà, le token reste. Avec la graine du programme, les positions 4, 5 et 18 sont choisies : « le » et « contrat » deviennent `[MASK]`, et « et » est remplacé par « de », tiré au hasard. C'est le cas à 10 % qui oblige le modèle à douter de ce qu'il lit.

**`moyenne_masquee(vecteurs, masque)`** additionne coordonnée par coordonnée les vecteurs dont le masque vaut 1, puis divise par leur nombre. Un masque entièrement nul lève `ValueError` : la moyenne de rien n'est pas définie. **`normaliser(v)`** divise par la norme et refuse le vecteur nul.

**`entropie_croisee(logits, cible)`** renvoie `log_somme_exp(logits) - logits[cible]`, c'est-à-dire −ln softmax(z)ᶜ, sans calculer d'exponentielle qui déborde.

**`info_nce(S, tau)`.** Refuse τ ≤ 0. Pour la ligne i, divise chaque sᵢⱼ par τ et calcule l'entropie croisée avec la classe i ; renvoie la moyenne et la liste des pertes par ligne. Sur l'exemple, `[0.0012, 0.0247, 0.1277]` et 0,0512 pour τ = 0,1.

**`gradient_info_nce(S, tau)`** renvoie la matrice (pᵢⱼ − 1[j = i]) / (Bτ), la formule du point 5.

**`encoder(E, mots)`.** La requête ou le document est un sac de mots : x vaut 1 sur les mots présents, 0 ailleurs. E·x est donc la somme des colonnes de E correspondant aux mots présents, calculée par `sum(ligne[w] for w in mots)`. La fonction renvoie ce vecteur brut u, sa norme et sa version normalisée.

**`perte_et_gradients(Eq, Ed, lot, tau)`.**

- Encode les B requêtes avec `Eq` et les B documents avec `Ed` : deux tours d'encodage distincts, comme un bi-encodeur asymétrique.
- Forme la matrice `S` des cosinus, puis la perte avec `info_nce` et la matrice `G` des dérivées avec `gradient_info_nce`.
- La boucle traite les deux côtés avec le même code. Côté requêtes, ∂ℒ/∂q̂ᵢ = ∑ⱼ Gᵢⱼ d̂ⱼ ; côté documents, ∂ℒ/∂d̂ⱼ = ∑ᵢ Gᵢⱼ q̂ᵢ, d'où la clé `G[j][i]`.
- Retour à travers la normalisation : si ê = u/‖u‖, alors ∂ℒ/∂u = (g − (g·ê)ê) / ‖u‖. La composante de g le long de ê disparaît, parce qu'allonger u ne change pas ê.
- Comme u est la somme des colonnes des mots présents, chaque colonne présente reçoit ce même gradient.

**`recall_a_1(Eq, Ed, requetes, corpus)`.** Encode les 66 documents, puis, pour chaque requête, cherche le document de plus grand cosinus ; une égalité se départage par l'indice le plus petit, pour un résultat déterministe. Renvoie la part des requêtes dont ce document est le bon (étape 25, k = 1).

**`couts(...)`** applique les trois formules de coût en comptant des passages d'encodeur et des tokens lus. **`milliers(n)`** affiche 200 000 au lieu de 200000.

**`main()`, bloc par bloc.**

1. Des matrices tirées avec la graine 36. L'encodeur lit 5 tokens et renvoie H, de taille 5 × 8, grâce à la connexion résiduelle ; le décodeur lit 3 tokens avec le masque causal ; l'attention croisée prend Q du décodeur et K, V de H. Les `assert` vérifient les formes du point 2, la somme 1 de chaque ligne de poids, les zéros du masque, puis le fait que chaque sortie croisée reste entre le minimum et le maximum de chaque colonne de V. On modifie ensuite le dernier token : la première sortie de l'encodeur bouge de 0,1352, celle du décodeur pas du tout (point 1).
2. Le masquage MLM sur une phrase de 20 tokens : 3 positions. Puis 77 positions pour 512 tokens, et ln 30 000 = 10,309 (point 3).
3. La moyenne masquée (2 ; 1), la moyenne naïve (1,25 ; 0) et leur cosinus 2/√5 (point 4).
4. L'exemple du point 8 pour τ = 0,1 et τ = 1. Trois dérivées de `gradient_info_nce` sont comparées à des différences finies centrées. Une matrice dont toutes les similarités sont égales donne exactement ln 3.
5. La ligne (0,8 ; 0,6 ; 0,1 ; −0,2) pour six températures : la part du négatif le plus dur décroît strictement et tend vers 1/3, et la perte tend vers ln 4. Puis le faux négatif à 0,9 : la perte suit 0,1/τ (point 6).
6. Le bi-encodeur jouet. Les 12 mots de requête, en anglais, n'ont aucun mot commun avec les 12 mots de document, en français : BM25 (étape 22) donnerait 0 partout. Les 66 couples de mots sont mélangés ; 44 servent à l'entraînement, 22 au test, et le corpus contient les 66 documents. Avant d'entraîner, le gradient analytique est vérifié sur quatre poids par différences finies. Puis 20 époques de descente de gradient, η = 1, en lots de 11 paires, τ = 0,1 : le Recall@1 sur les requêtes de test passe de 0 à 0,727 après une époque et à 1,0 dès la cinquième. Ces 22 couples n'ont jamais été vus ensemble pendant l'entraînement : le modèle a appris l'alignement des mots, pas des paires par cœur.
7. Les coûts du point 7, puis trois entrées invalides : τ = 0, une phrase sans token réel, et des K et V de tailles différentes.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`transposer(a)`** — Cette fonction fait pivoter un tableau d'un quart de tour, comme un archiviste qui retourne un registre pour lire ses colonnes à la place de ses lignes : elle reçoit une matrice a, regroupe par `zip(*a)` les éléments de même rang et transforme chaque groupe en liste. Elle renvoie la transposée, sans toucher à l'original ; `attention` s'en sert pour former Kᵀ avant de calculer la matrice des scores Q Kᵀ, de taille n_q × n_k, qu'il s'agisse d'auto-attention ou d'attention croisée.

**`forme(m)`** — Ce petit utilitaire est l'étiqueteuse qui colle sur chaque caisse ses dimensions : il reçoit une matrice m et renvoie une chaîne qui donne son nombre de lignes et son nombre de colonnes séparés par le signe ×, par exemple `"3×5"`. Il ne calcule rien d'autre ; `main` l'utilise pour afficher les formes des requêtes, des clés, des poids et des sorties, et un `assert` exige les formes `5×5`, `5×8`, `3×3`, `3×5` et `3×4` annoncées par le point 2.

**`log_somme_exp(z)`** — Cette fonction est le comptable prudent qui additionne des exponentielles sans jamais faire exploser sa calculatrice : elle reçoit une liste z de nombres, repère le plus grand, retranche ce maximum à chaque valeur avant l'exponentielle, additionne, prend le logarithme et rajoute le maximum. Elle renvoie ln Σ exp(zⱼ), exactement, mais sans débordement même pour des logits divisés par une petite température ; `softmax` et `entropie_croisee` reposent toutes deux sur elle.

**`softmax(z)`** — On peut la voir comme le répartiteur qui distribue cent pour cent de l'attention à partir du total préparé par le comptable : elle reçoit une liste z de scores, appelle `log_somme_exp` pour obtenir ln Σ exp(zⱼ), puis renvoie pour chaque score exp(zⱼ − ce total), ce qui donne des poids positifs qui somment à 1. Un score à moins l'infini y reçoit un poids exactement nul ; `attention`, `gradient_info_nce` et l'étude de la température au bloc 5 l'utilisent toutes.

**`masque_causal(n)`** — Cette fonction rédige le règlement d'une salle où chacun ne peut regarder que ceux qui sont arrivés avant lui : elle reçoit le nombre n de tokens et renvoie une matrice n × n qui vaut 0 sur et sous la diagonale et moins l'infini au-dessus. Ajoutée aux scores du décodeur, elle rend nuls les poids vers les tokens futurs, ce que `main` vérifie case par case pour les 3 tokens du décodeur, et explique pourquoi changer le dernier token ne modifie pas du tout la première sortie du décodeur.

**`attention(Q, K, V, masque)`** — C'est la même scène d'attention qui sert aux trois familles du chapitre, avec un guichet qui vérifie les papiers : la fonction reçoit les requêtes Q, les clés K, les valeurs V et un masque facultatif, et lève une `ValueError` si Q et K n'ont pas la même largeur ou si K et V n'ont pas le même nombre de lignes, la seule condition qu'exige l'attention croisée. Elle calcule ensuite Q Kᵀ, divise chaque score par √dₖ, ajoute le masque s'il existe, applique `softmax` ligne par ligne et renvoie le couple formé des poids et de la sortie, poids fois V ; dans l'attention croisée, 3 requêtes du décodeur regardent 5 clés de l'encodeur, d'où des poids 3 × 5 et une sortie 3 × 4.

**`produit(a, b)`** — Cette fonction est le geste élémentaire du caissier qui multiplie deux colonnes rang par rang puis fait le total : elle reçoit deux vecteurs a et b et renvoie leur produit scalaire. Quand les deux vecteurs ont été normalisés, ce nombre est leur cosinus ; c'est ainsi que `main` mesure 2/√5 entre la bonne moyenne et la moyenne naïve, que `perte_et_gradients` remplit la matrice S des similarités et que `recall_a_1` classe les 66 documents.

**`entropie_croisee(logits, cible)`** — On peut la voir comme le correcteur qui mesure la surprise du modèle devant la bonne réponse : elle reçoit une liste de logits et l'indice de la classe correcte, et renvoie `log_somme_exp(logits)` moins le logit de cette classe, c'est-à-dire −ln softmax(z) pour la cible, sans calculer la moindre exponentielle qui déborde. Plus le bon logit domine les autres, plus la perte s'approche de 0 ; `info_nce` l'applique à chaque ligne du lot, et le bloc 5 l'utilise pour montrer que la perte tend vers ln 4 quand τ devient très grand.

**`info_nce(S, tau)`** — C'est l'examinateur d'un jeu d'appariement où chaque requête doit reconnaître son document parmi ceux du lot : la fonction reçoit la matrice S des similarités, dont la case (i, i) est la paire correcte, et la température τ, lève une `ValueError` si τ ≤ 0, puis divise chaque ligne par τ et calcule son entropie croisée avec la classe i. Elle renvoie la moyenne de ces pertes et la liste des pertes par ligne : `[0.0012, 0.0247, 0.1277]` et 0,0512 pour τ = 0,1 sur l'exemple, 0,776 pour τ = 1, et exactement ln 3 quand toutes les similarités sont égales.

**`gradient_info_nce(S, tau)`** — Cette fonction est le conseiller qui dit à chaque similarité dans quel sens bouger : elle reçoit la matrice S et la température τ, calcule pour chaque ligne les probabilités de la softmax de S divisée par τ, puis renvoie la matrice des dérivées (pᵢⱼ − 1 si j = i, sinon pᵢⱼ) divisées par B τ. Le positif reçoit une dérivée négative, il doit monter, et les négatifs une dérivée positive, ils doivent descendre : sur l'exemple, ∂ℒ/∂s₃₃ vaut −0,3997 et ∂ℒ/∂s₃₂ vaut 0,3970, et `main` compare trois de ces dérivées à des différences finies centrées.

**`perte_et_gradients(Eq, Ed, lot, tau)`** — C'est le moniteur d'entraînement du bi-encodeur, qui fait passer un lot de paires et note ce qu'il faut corriger : la fonction reçoit la matrice d'encodage `Eq` des requêtes, la matrice `Ed` des documents, un lot de paires (requête, document) et τ, encode chaque côté avec `encoder`, forme la matrice des cosinus, calcule la perte avec `info_nce` et sa dérivée avec `gradient_info_nce`. Elle fait ensuite redescendre ce gradient à travers la normalisation, en retirant sa composante le long du vecteur normalisé, puis l'ajoute à chaque colonne de mot présent ; elle renvoie la perte et les deux matrices de gradients, que `main` vérifie sur quatre poids avant vingt époques de descente.

**`couts(n_docs, requetes, n_top, l_q, l_d)`** — Cette fonction est le contrôleur de gestion qui chiffre trois façons d'organiser la recherche : elle reçoit le nombre de documents, le nombre de requêtes par jour, le nombre de candidats gardés au premier étage, la longueur d'une requête et celle d'un document, et renvoie un dictionnaire de passages d'encodeur et de tokens lus pour le bi-encodeur, le cross-encodeur seul et le montage en deux étages. Avec 200 000 documents, 5 000 requêtes, un top-50, 20 et 300 tokens, le cross-encodeur seul demande 10⁹ passages par jour contre 250 000 pour les deux étages, soit 4 000 fois moins, et ces deux étages lisent 80 100 000 tokens.

**`milliers(n)`** — Ce petit utilitaire est le typographe qui rend les grands nombres lisibles à la française : il reçoit un entier n, le formate avec un séparateur de milliers, puis remplace chaque virgule par une espace. Il renvoie une chaîne comme `200 000` au lieu de `200000`, et `main` ne s'en sert que pour l'affichage des coûts du bloc 7, où l'on lit par exemple un milliard de passages pour le cross-encodeur seul, sans avoir à compter les zéros.

**`main()`** — Le chef d'orchestre déroule les sept blocs du chapitre avec un générateur à graine 36 : il construit un encodeur, un décodeur masqué et une attention croisée, vérifie formes, sommes des poids et effet du masque, puis applique le masquage MLM à une phrase de 20 tokens, compare la moyenne masquée à la moyenne naïve et calcule InfoNCE sur l'exemple, gradient compris. Il étudie ensuite l'effet de τ et du faux négatif, entraîne le bi-encodeur jouet sur 44 paires jusqu'à un Recall@1 de 1 sur les 22 paires de test, chiffre les coûts et s'assure que trois entrées invalides lèvent une `ValueError` ; il ne renvoie rien et n'imprime le message final que si tous les `assert` passent.

**`matrice(l, c)`** — Cette fonction interne vit dans `main`, comme un artisan qui taille à la demande des plaques de nombres dans le même bloc de hasard : elle reçoit un nombre de lignes l et de colonnes c, et remplit chaque case par un tirage uniforme entre −1 et 1 pris dans le générateur `rng` de `main`, à graine 36. Elle renvoie cette matrice, et `main` l'appelle pour toutes les projections du bloc 1, celles de l'auto-attention comme celles de l'attention croisée, ainsi que pour les 5 tokens source et les 3 tokens du décodeur ; la graine fixe rend toute la suite reproductible.

**`encodeur(X_)`** — Cette autre fonction interne vit dans `main`, au bloc 1, et joue un lecteur qui a le droit de parcourir toute la phrase source dans les deux sens : elle reçoit la matrice des tokens source, la projette en requêtes, clés et valeurs, fait l'attention sans aucun masque, projette la sortie par `W_O` et l'ajoute aux tokens d'entrée par la connexion résiduelle. Elle renvoie les poids, de taille 5 × 5, et la matrice H, de taille 5 × 8, que l'attention croisée consulte ensuite ; `main` montre en la rappelant qu'un changement du dernier token source déplace la première sortie de l'encodeur de 0,1352.

```python
"""Étape 36 ter — encodeur, décodeur et attention croisée ; masquage MLM ; embedding par moyenne ;
InfoNCE (entropie croisée sur le lot) et entraînement d'un bi-encodeur jouet ; coûts bi-encodeur et cross-encodeur."""
import itertools
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- algèbre et attention (étapes 31 à 34)
def matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    if len(a[0]) != len(b):
        raise ValueError("dimensions incompatibles pour le produit matriciel")
    colonnes = list(zip(*b))
    return [[sum(x * y for x, y in zip(ligne, col)) for col in colonnes] for ligne in a]


def transposer(a: list[list[float]]) -> list[list[float]]:
    return [list(c) for c in zip(*a)]


def forme(m: list[list[float]]) -> str:
    return f"{len(m)}×{len(m[0])}"


def log_somme_exp(z: list[float]) -> float:
    pic = max(z)
    return pic + math.log(sum(math.exp(v - pic) for v in z))


def softmax(z: list[float]) -> list[float]:
    l = log_somme_exp(z)
    return [math.exp(v - l) for v in z]


def masque_causal(n: int) -> list[list[float]]:
    return [[0.0 if j <= i else -math.inf for j in range(n)] for i in range(n)]


def attention(Q, K, V, masque=None):
    """softmax(QKᵀ/√d_k + M) V ; Q : n_q × d_k, K : n_k × d_k, V : n_k × d_v. Renvoie (poids, sortie)."""
    d_k = len(Q[0])
    if len(K[0]) != d_k or len(K) != len(V):
        raise ValueError("Q et K doivent avoir la même largeur, K et V le même nombre de lignes")
    poids = []
    for i, ligne in enumerate(matmul(Q, transposer(K))):
        poids.append(softmax([s / math.sqrt(d_k) + (masque[i][j] if masque else 0.0) for j, s in enumerate(ligne)]))
    return poids, matmul(poids, V)


# ---------------------------------------------------------------- objectifs d'entraînement
def masquer_mlm(tokens: list[str], taux: float, rng: random.Random, vocab: list[str]):
    """Choisit round(taux × n) positions ; 80 % → [MASK], 10 % → token au hasard, 10 % inchangées."""
    positions = sorted(rng.sample(range(len(tokens)), round(taux * len(tokens))))
    entree = list(tokens)
    for p in positions:
        u = rng.random()
        if u < 0.8:
            entree[p] = "[MASK]"
        elif u < 0.9:
            entree[p] = rng.choice(vocab)
    return entree, positions


def moyenne_masquee(vecteurs: list[list[float]], masque: list[int]) -> list[float]:
    """Embedding de phrase : moyenne des vecteurs des VRAIS tokens (masque = 1), le remplissage est exclu."""
    n = sum(masque)
    if n == 0:
        raise ValueError("aucun token réel : la moyenne n'est pas définie")
    return [sum(v[j] for v, m in zip(vecteurs, masque) if m) / n for j in range(len(vecteurs[0]))]


def normaliser(v: list[float]) -> list[float]:
    n = math.sqrt(sum(x * x for x in v))
    if n == 0.0:
        raise ValueError("vecteur nul : pas de direction")
    return [x / n for x in v]


def produit(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def entropie_croisee(logits: list[float], cible: int) -> float:
    """−ln softmax(z)_c (étape 2), calculée par log-somme-exp."""
    return log_somme_exp(logits) - logits[cible]


def info_nce(S: list[list[float]], tau: float) -> tuple[float, list[float]]:
    """Perte InfoNCE d'un lot : pour la ligne i, entropie croisée des logits S[i][j]/τ avec la classe j = i."""
    if tau <= 0:
        raise ValueError("τ doit être > 0")
    pertes = [entropie_croisee([s / tau for s in ligne], i) for i, ligne in enumerate(S)]
    return sum(pertes) / len(pertes), pertes


def gradient_info_nce(S: list[list[float]], tau: float) -> list[list[float]]:
    """∂L/∂s_ij = (p_ij − 1[j = i]) / (B τ), le gradient p − y de l'étape 2 avec T = τ."""
    B = len(S)
    G = []
    for i, ligne in enumerate(S):
        p = softmax([s / tau for s in ligne])
        G.append([(p[j] - (1.0 if j == i else 0.0)) / (B * tau) for j in range(B)])
    return G


# ---------------------------------------------------------------- bi-encodeur jouet entraîné par InfoNCE
MOTS_Q = ["salary", "rent", "visa", "loan", "claim", "wallet", "deposit", "fine", "permit", "tax", "refund", "transfer"]
MOTS_D = ["salaire", "loyer", "sejour", "credit", "sinistre", "portefeuille", "caution", "amende", "licence", "tva",
          "remboursement", "virement"]


def encoder(E: list[list[float]], mots: list[int]):
    """e = normaliser(E·x) où x est l'indicatrice des mots : E·x est la somme des colonnes des mots présents."""
    u = [sum(ligne[w] for w in mots) for ligne in E]
    n = math.sqrt(sum(x * x for x in u))
    return u, n, [x / n for x in u]


def perte_et_gradients(Eq, Ed, lot, tau):
    """InfoNCE d'un lot de paires (requête, document) ; les autres documents du lot sont les négatifs."""
    B, d = len(lot), len(Eq)
    Q = [encoder(Eq, q) for q, _ in lot]
    D = [encoder(Ed, doc) for _, doc in lot]
    S = [[produit(Q[i][2], D[j][2]) for j in range(B)] for i in range(B)]
    perte, _ = info_nce(S, tau)
    G = gradient_info_nce(S, tau)
    g_q = [[0.0] * len(Eq[0]) for _ in range(d)]
    g_d = [[0.0] * len(Ed[0]) for _ in range(d)]
    for cote, vecteurs, autres, grad, cle in ((0, Q, D, g_q, lambda i, j: G[i][j]), (1, D, Q, g_d, lambda i, j: G[j][i])):
        for i in range(B):
            g_e = [sum(cle(i, j) * autres[j][2][r] for j in range(B)) for r in range(d)]   # ∂L/∂e_i
            _, norme, e = vecteurs[i]
            c = produit(g_e, e)
            g_u = [(g_e[r] - c * e[r]) / norme for r in range(d)]   # retour à travers la normalisation
            for w in lot[i][cote]:
                for r in range(d):
                    grad[r][w] += g_u[r]
    return perte, g_q, g_d


def recall_a_1(Eq, Ed, requetes, corpus) -> float:
    """Part des requêtes dont le document le mieux classé (cosinus) est le bon (étape 25)."""
    docs = [encoder(Ed, doc)[2] for doc in corpus]
    bons = 0
    for q, cible in requetes:
        e = encoder(Eq, q)[2]
        scores = [produit(e, k) for k in docs]
        meilleur = max(range(len(docs)), key=lambda j: (scores[j], -j))
        bons += corpus[meilleur] == cible
    return bons / len(requetes)


# ---------------------------------------------------------------- coûts
def couts(n_docs: int, requetes: int, n_top: int, l_q: int, l_d: int) -> dict:
    """Passages d'encodeur et tokens traités : bi-encodeur, cross-encodeur seul, et les deux étages."""
    return {
        "bi_hors_ligne": n_docs, "bi_par_jour": requetes, "bi_produits": requetes * n_docs,
        "cross_par_jour": requetes * n_docs, "deux_etages_cross": requetes * n_top,
        "tokens_bi": requetes * l_q, "tokens_cross": requetes * n_docs * (l_q + l_d),
        "tokens_deux_etages": requetes * l_q + requetes * n_top * (l_q + l_d),
    }


def milliers(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def main() -> None:
    rng = random.Random(36)

    def matrice(l: int, c: int) -> list[list[float]]:
        return [[rng.uniform(-1.0, 1.0) for _ in range(c)] for _ in range(l)]

    print("1. Trois familles, une seule attention (d_model = 8, d_k = d_v = 4)")
    d_model, d_k = 8, 4
    W_Q, W_K, W_V, W_O = matrice(d_model, d_k), matrice(d_model, d_k), matrice(d_model, d_k), matrice(d_k, d_model)
    Wc_Q, Wc_K, Wc_V = matrice(d_model, d_k), matrice(d_model, d_k), matrice(d_model, d_k)
    X = matrice(5, d_model)                      # 5 tokens source, lus par l'encodeur
    Y = matrice(3, d_model)                      # 3 tokens déjà écrits par le décodeur

    def encodeur(X_):
        p, o = attention(matmul(X_, W_Q), matmul(X_, W_K), matmul(X_, W_V))
        return p, [[a + b for a, b in zip(x, s)] for x, s in zip(X_, matmul(o, W_O))]   # résiduel : 5 × d_model

    p_enc, H = encodeur(X)
    p_dec, o_dec = attention(matmul(Y, W_Q), matmul(Y, W_K), matmul(Y, W_V), masque_causal(3))
    Qc, Kc, Vc = matmul(Y, Wc_Q), matmul(H, Wc_K), matmul(H, Wc_V)
    p_croise, o_croise = attention(Qc, Kc, Vc)
    print(f"  encodeur : Q {forme(matmul(X, W_Q))}, K {forme(matmul(X, W_K))} → poids {forme(p_enc)}, aucun masque → H {forme(H)}")
    print(f"  décodeur : Q {forme(matmul(Y, W_Q))}, K {forme(matmul(Y, W_K))} → poids {forme(p_dec)}, masque causal → sortie {forme(o_dec)}")
    print(f"  croisée  : Q {forme(Qc)} (décodeur), K {forme(Kc)} et V {forme(Vc)} (encodeur) → poids {forme(p_croise)} → sortie {forme(o_croise)}")
    assert (forme(p_enc), forme(H), forme(p_dec), forme(p_croise), forme(o_croise)) == ("5×5", "5×8", "3×3", "3×5", "3×4")
    assert all(abs(sum(l) - 1) < 1e-12 for l in p_enc + p_dec + p_croise)
    assert all(p_dec[i][j] == 0.0 for i in range(3) for j in range(3) if j > i)
    for i in range(3):                           # chaque ligne de sortie est une moyenne pondérée des lignes de V
        for c in range(d_k):
            assert min(v[c] for v in Vc) - 1e-12 <= o_croise[i][c] <= max(v[c] for v in Vc) + 1e-12

    X2 = [ligne[:] for ligne in X]
    X2[4] = [v + 1.0 for v in X2[4]]             # on change le DERNIER token source
    ecart_enc = max(abs(a - b) for a, b in zip(encodeur(X2)[1][0], H[0]))
    Y2 = [ligne[:] for ligne in Y]
    Y2[2] = [v + 1.0 for v in Y2[2]]             # on change le DERNIER token du décodeur
    o_dec2 = attention(matmul(Y2, W_Q), matmul(Y2, W_K), matmul(Y2, W_V), masque_causal(3))[1]
    print(f"  changer le dernier token : sortie 1 de l'encodeur bouge de {ecart_enc:.4f} ; sortie 1 du décodeur de {max(abs(a - b) for a, b in zip(o_dec2[0], o_dec[0]))}")
    assert ecart_enc > 1e-3 and o_dec2[0] == o_dec[0]

    print("2. Modèle de langue masqué : 15 % des positions à prédire")
    phrase = ("le locataire doit enregistrer le contrat de bail auprès de Ejari avant de demander "
              "le raccordement à l'eau et l'électricité").split()
    entree, positions = masquer_mlm(phrase, 0.15, rng, phrase)
    print(f"  {len(phrase)} tokens → {len(positions)} positions {positions} : {' '.join(entree)}")
    print(f"  512 tokens → {round(0.15 * 512)} positions ; perte d'un prédicteur uniforme sur 30 000 tokens : ln 30000 = {math.log(30000):.3f}")
    assert len(phrase) == 20 and len(positions) == 3 and round(0.15 * 512) == 77
    assert all(entree[i] == phrase[i] for i in range(20) if i not in positions)

    print("3. Embedding de phrase : moyenne des vrais tokens, puis normalisation")
    h = [[1.0, 2.0], [3.0, 0.0], [0.5, -1.0], [0.5, -1.0]]          # 2 tokens réels + 2 positions de remplissage
    bon = moyenne_masquee(h, [1, 1, 0, 0])
    naif = moyenne_masquee(h, [1, 1, 1, 1])
    cos_bn = produit(normaliser(bon), normaliser(naif))
    print(f"  avec masque : {bon} ; sans masque : {naif} ; cosinus entre les deux = {cos_bn:.4f}")
    assert bon == [2.0, 1.0] and naif == [1.25, 0.0] and abs(cos_bn - 2 / math.sqrt(5)) < 1e-12

    print("4. InfoNCE = entropie croisée sur le lot (B = 3)")
    S = [[0.9, 0.2, 0.1], [0.3, 0.8, 0.4], [0.0, 0.5, 0.7]]
    for tau in (0.1, 1.0):
        L, pertes = info_nce(S, tau)
        print(f"  τ = {tau} : pertes par ligne {[round(x, 4) for x in pertes]} → InfoNCE = {L:.4f}")
    L01, pertes01 = info_nce(S, 0.1)
    assert [round(x, 4) for x in pertes01] == [0.0012, 0.0247, 0.1277] and round(L01, 4) == 0.0512
    assert round(info_nce(S, 1.0)[0], 4) == 0.776
    G = gradient_info_nce(S, 0.1)
    for i, j in ((0, 0), (1, 2), (2, 1)):
        S_p = [l[:] for l in S]
        S_m = [l[:] for l in S]
        S_p[i][j] += 1e-6
        S_m[i][j] -= 1e-6
        num = (info_nce(S_p, 0.1)[0] - info_nce(S_m, 0.1)[0]) / 2e-6
        assert abs(num - G[i][j]) < 1e-7
    print(f"  ∂L/∂s₃₃ = {G[2][2]:.4f} (le positif monte) ; ∂L/∂s₃₂ = {G[2][1]:.4f} (le négatif dur descend)")
    print(f"  aléatoire : InfoNCE = ln B = {math.log(3):.4f} ; uniforme sur un lot de 256 : ln 256 = {math.log(256):.4f}")
    assert abs(info_nce([[0.3] * 3] * 3, 0.1)[0] - math.log(3)) < 1e-12

    print("5. Effet de τ sur une ligne : positif 0.8, négatifs 0.6 / 0.1 / −0.2")
    ligne = [0.8, 0.6, 0.1, -0.2]
    parts = []
    for tau in (0.02, 0.05, 0.1, 0.5, 1.0, 10.0):
        p = softmax([s / tau for s in ligne])
        part = p[1] / (1 - p[0])
        parts.append(part)
        print(f"  τ = {tau:>5} : perte = {entropie_croisee([s / tau for s in ligne], 0):.4f} ; part du gradient des négatifs sur le plus dur = {part:.3f}")
    assert all(a > b for a, b in zip(parts, parts[1:])) and abs(parts[-1] - 1 / 3) < 0.02   # limite 1/(B − 1)
    assert abs(entropie_croisee([s / 1000 for s in ligne], 0) - math.log(4)) < 1e-3
    faux_negatif = [0.8, 0.9, 0.1, -0.2]
    pertes_fn = [entropie_croisee([s / tau for s in faux_negatif], 0) for tau in (0.1, 0.05, 0.02)]
    print(f"  faux négatif à 0.9 : perte {[round(x, 3) for x in pertes_fn]} pour τ = 0.1, 0.05, 0.02 (≈ 0.1 / τ)")
    assert abs(pertes_fn[2] - 0.1 / 0.02) < 0.01

    print("6. Bi-encodeur jouet entraîné par InfoNCE (requêtes en anglais, documents en français)")
    paires = list(itertools.combinations(range(12), 2))
    rng.shuffle(paires)
    donnees = [(list(p), list(p)) for p in paires]      # requête {mots i, j} ↔ document {traductions de i et j}
    entrainement, test = donnees[:44], donnees[44:]
    corpus = [doc for _, doc in donnees]
    print(f"  mots communs entre requêtes et documents : {len(set(MOTS_Q) & set(MOTS_D))} → BM25 nul partout")
    assert not set(MOTS_Q) & set(MOTS_D)
    d, tau, eta, B = 8, 0.1, 1.0, 11
    Eq = [[rng.uniform(-0.5, 0.5) for _ in range(12)] for _ in range(d)]
    Ed = [[rng.uniform(-0.5, 0.5) for _ in range(12)] for _ in range(d)]
    _, g_q, g_d = perte_et_gradients(Eq, Ed, entrainement[:B], tau)
    for E, g, r, w in ((Eq, g_q, 0, 0), (Eq, g_q, 3, 5), (Ed, g_d, 7, 11), (Ed, g_d, 2, 4)):
        E[r][w] += 1e-6
        plus = perte_et_gradients(Eq, Ed, entrainement[:B], tau)[0]
        E[r][w] -= 2e-6
        moins = perte_et_gradients(Eq, Ed, entrainement[:B], tau)[0]
        E[r][w] += 1e-6
        assert abs((plus - moins) / 2e-6 - g[r][w]) < 1e-6
    rappels = {}
    for epoque in range(21):
        if epoque in (0, 1, 2, 5, 20):
            rappels[epoque] = recall_a_1(Eq, Ed, test, corpus)
            print(f"  époque {epoque:>2} : Recall@1 sur les 22 requêtes de test (66 documents) = {rappels[epoque]:.3f}")
        ordre = entrainement[:]
        rng.shuffle(ordre)
        for debut in range(0, len(ordre), B):
            _, g_q, g_d = perte_et_gradients(Eq, Ed, ordre[debut:debut + B], tau)
            for r in range(d):
                for w in range(12):
                    Eq[r][w] -= eta * g_q[r][w]
                    Ed[r][w] -= eta * g_d[r][w]
    assert rappels[0] < 0.1 and rappels[2] > rappels[0] and rappels[20] == 1.0
    e_visa = encoder(Eq, [MOTS_Q.index("visa"), MOTS_Q.index("rent")])[2]
    e_bon = encoder(Ed, [MOTS_D.index("sejour"), MOTS_D.index("loyer")])[2]
    e_moitie = encoder(Ed, [MOTS_D.index("sejour"), MOTS_D.index("tva")])[2]
    print(f"  cos(« visa rent », « sejour loyer ») = {produit(e_visa, e_bon):.3f} ; avec « sejour tva » = {produit(e_visa, e_moitie):.3f}")
    assert produit(e_visa, e_bon) > produit(e_visa, e_moitie) > 0

    print("7. Coûts : 200 000 documents, 5 000 requêtes par jour, top-50, requête 20 tokens, document 300")
    c = couts(200_000, 5_000, 50, 20, 300)
    print(f"  bi-encodeur : {milliers(c['bi_hors_ligne'])} passages hors ligne, {milliers(c['bi_par_jour'])} par jour"
          f" + {milliers(c['bi_produits'])} produits scalaires")
    print(f"  cross-encodeur seul : {milliers(c['cross_par_jour'])} passages par jour ; deux étages : {milliers(c['deux_etages_cross'])}")
    print(f"  tokens lus par jour : bi {milliers(c['tokens_bi'])} ; deux étages {milliers(c['tokens_deux_etages'])}"
          f" ; cross seul {milliers(c['tokens_cross'])}")
    assert c["cross_par_jour"] == 10 ** 9 and c["deux_etages_cross"] == 250_000
    assert c["cross_par_jour"] // c["deux_etages_cross"] == 4_000 and c["tokens_deux_etages"] == 80_100_000

    for appel in (lambda: info_nce(S, 0.0), lambda: moyenne_masquee(h, [0, 0, 0, 0]), lambda: attention(Qc, Kc, Vc[:2])):
        try:
            appel()
        except ValueError:
            pass
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")
    print("  τ = 0, phrase sans token réel, K et V de tailles différentes → ValueError")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Trois familles, une seule attention (d_model = 8, d_k = d_v = 4)
  encodeur : Q 5×4, K 5×4 → poids 5×5, aucun masque → H 5×8
  croisée  : Q 3×4 (décodeur), K 5×4 et V 5×4 (encodeur) → poids 3×5 → sortie 3×4
  changer le dernier token : sortie 1 de l'encodeur bouge de 0.1352 ; sortie 1 du décodeur de 0.0
…
  avec masque : [2.0, 1.0] ; sans masque : [1.25, 0.0] ; cosinus entre les deux = 0.8944
…
  τ = 0.1 : pertes par ligne [0.0012, 0.0247, 0.1277] → InfoNCE = 0.0512
  τ = 1.0 : pertes par ligne [0.6657, 0.8228, 0.8395] → InfoNCE = 0.7760
  ∂L/∂s₃₃ = -0.3997 (le positif monte) ; ∂L/∂s₃₂ = 0.3970 (le négatif dur descend)
…
  τ =   0.1 : perte = 0.1278 ; part du gradient des négatifs sur le plus dur = 0.993
  faux négatif à 0.9 : perte [1.314, 2.127, 5.007] pour τ = 0.1, 0.05, 0.02 (≈ 0.1 / τ)
…
  époque  0 : Recall@1 sur les 22 requêtes de test (66 documents) = 0.000
  époque  5 : Recall@1 sur les 22 requêtes de test (66 documents) = 1.000
  cos(« visa rent », « sejour loyer ») = 0.992 ; avec « sejour tva » = 0.429
…
  cross-encodeur seul : 1 000 000 000 passages par jour ; deux étages : 250 000
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un modèle d'embedding n'a rien de magique. C'est un encodeur sans masque, une moyenne qui ignore le remplissage, et une entropie croisée sur le lot qui apprend, à partir de paires, à rapprocher des textes qui n'ont aucun mot en commun.

### La même perte en PyTorch (extrait)

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`moyenne_masquee(h, masque)`** — C'est la même moyenne que dans le programme précédent, mais faite d'un coup pour tout un lot, comme un huissier qui compte les présents de plusieurs salles à la fois : la fonction reçoit le tenseur h des états, de forme (B, n, d), et le masque, de forme (B, n), avec 1 pour un vrai token et 0 pour le remplissage, ajoute une dimension au masque, multiplie, additionne le long des positions et divise par le nombre de vrais tokens. Elle renvoie un embedding de phrase par ligne du lot, de forme (B, d) ; à la différence de la version en Python pur, qui lève une `ValueError` sur une ligne vide, elle force ce nombre à au moins 1 par `clamp(min=1.0)` et rend alors un vecteur nul.

**`info_nce(q, d, tau)`** — Voici l'examinateur du jeu d'appariement réduit à quatre lignes : la fonction reçoit le tenseur q des requêtes et le tenseur d des documents, tous deux de forme (B, d_e), où la ligne i de d est le positif de la requête i, ainsi que la température τ, 0,05 par défaut. Elle ramène chaque vecteur à la norme 1, forme la matrice B × B des cosinus divisés par τ, prend pour cibles les indices 0, 1, …, B − 1, et renvoie `F.cross_entropy` de ces logits, c'est-à-dire la moyenne sur le lot de l'entropie croisée de chaque ligne avec sa colonne diagonale, exactement ce que calcule `info_nce` dans le programme précédent à partir d'une matrice S déjà formée.

```python
# [extrait] — InfoNCE en PyTorch, non exécutée par le harnais (PyTorch n'est pas dans la bibliothèque standard)
import torch
import torch.nn.functional as F


def moyenne_masquee(h, masque):                     # h : (B, n, d), masque : (B, n) avec 1 = vrai token
    m = masque.unsqueeze(-1).float()
    return (h * m).sum(dim=1) / m.sum(dim=1).clamp(min=1.0)


def info_nce(q, d, tau=0.05):                       # q, d : (B, d_e), la ligne i de d est le positif de q[i]
    q = F.normalize(q, dim=-1)
    d = F.normalize(d, dim=-1)
    logits = q @ d.T / tau                          # (B, B) : s_ij / τ
    cibles = torch.arange(q.size(0), device=q.device)
    return F.cross_entropy(logits, cibles)          # entropie croisée de chaque ligne, classe i, moyenne sur le lot
```

La dernière ligne dit tout : InfoNCE **est** `F.cross_entropy`, appliquée à une matrice B × B dont la bonne classe de la ligne i est la colonne i. `F.normalize` ramène les vecteurs à la norme 1, donc `q @ d.T` contient les cosinus. Dans `moyenne_masquee`, `clamp(min=1.0)` évite une division par zéro sur une ligne entièrement remplie ; le programme stdlib préfère lever une erreur explicite. Sans PyTorch ni fournisseur, le programme plus haut fait le même calcul, gradient compris : c'est ce qui permet de réentraîner et d'héberger son propre modèle d'embedding plutôt que de dépendre d'une API dont on ne contrôle ni les versions ni la disponibilité.

## Squelette algorithmique

Trois algorithmes résument ce fichier. Le premier calcule l'attention croisée d'un pas de décodage : en entrée, les états du décodeur et la sortie de l'encodeur ; en sortie, une matrice n_dec × d_v. Le deuxième fait un pas d'entraînement contrastif : en entrée, un lot de B paires et τ ; en sortie, des encodeurs mis à jour. Le troisième est la recherche en deux étages qui en découle : un bi-encodeur pour le rappel, un cross-encodeur pour la précision.

```text
ALGORITHME AttentionCroisée
ENTRÉES : Y (n_dec × d_model, états du décodeur), H (n_enc × d_model, sortie de l'encodeur),
          projections Wq, Wk, Wv
SORTIE  : O (n_dec × d_v)

  K ← H × Wk ;  V ← H × Wv                     calculés UNE fois par texte source, puis gardés
  Q ← Y × Wq                                   n_dec × d_k
  POUR i DE 1 À n_dec FAIRE
      POUR j DE 1 À n_enc FAIRE
          sᵢⱼ ← (Qᵢ · Kⱼ) / √d_k                aucun masque : le décodeur lit toute la source
      FIN POUR
      aᵢ ← softmax(sᵢ)                         n_enc poids positifs, de somme 1
      Oᵢ ← Σⱼ aᵢⱼ × Vⱼ
  FIN POUR
  RETOURNER O

ALGORITHME PasInfoNCE
ENTRÉES : lot de B paires (requête qᵢ, document dᵢ), encodeurs Eq et Ed, température τ, pas η
SORTIE  : Eq et Ed mis à jour, perte du lot

  POUR i DE 1 À B FAIRE
      q̂ᵢ ← normaliser(Eq(qᵢ)) ;  d̂ᵢ ← normaliser(Ed(dᵢ))
  FIN POUR
  perte ← 0
  POUR i DE 1 À B FAIRE
      POUR j DE 1 À B FAIRE  sᵢⱼ ← q̂ᵢ · d̂ⱼ  FIN POUR       les B − 1 autres documents sont les négatifs
      perte ← perte + log-somme-exp(sᵢ / τ) − sᵢᵢ / τ
      POUR j DE 1 À B FAIRE
          Gᵢⱼ ← (softmax(sᵢ / τ)ⱼ − [j = i]) / (B × τ)
      FIN POUR
  FIN POUR
  rétropropager G à travers les produits scalaires, la normalisation et les encodeurs
  Eq ← Eq − η × ∇Eq ;  Ed ← Ed − η × ∇Ed
  RETOURNER Eq, Ed, perte / B

ALGORITHME RechercheDeuxÉtages
ENTRÉES : requête q, index des N embeddings de documents (calculés hors ligne), n_top, k
SORTIE  : les k meilleurs documents

  q̂ ← normaliser(Eq(q))                        1 passage court
  candidats ← les n_top documents de plus grand q̂ · d̂ⱼ     N produits scalaires, ou un index approché
  POUR CHAQUE d DANS candidats FAIRE
      score(d) ← CrossEncodeur(q, d)           1 passage sur la concaténation (q, d)
  FIN POUR
  RETOURNER les k candidats de meilleur score
```

**Complexité :** l'attention croisée coûte O(n_enc × d_model × d_k) une fois pour K et V, puis O(n_dec × n_enc × d_k) pour les scores et autant pour la moyenne des valeurs ; à la génération, chaque nouveau token ne coûte que O(n_enc × d_k), puisque K et V sont gardés. En mémoire, K et V occupent O(n_enc × d_k) par couche. Un pas d'InfoNCE coûte B encodages de chaque côté, plus O(B² × d_e) pour la matrice des similarités et son gradient : doubler le lot quadruple ce terme, mais il reste petit devant les encodages tant que B × d_e n'est pas énorme. La recherche en deux étages coûte un encodage de requête, O(N × d_e) pour le premier étage exact (ou bien moins avec un index approché), et n_top passages de cross-encodeur : c'est ce dernier terme qui fixe la latence, d'où un n_top de quelques dizaines.

**Du squelette au code :** AttentionCroisée est la ligne `Qc, Kc, Vc = matmul(Y, Wc_Q), matmul(H, Wc_K), matmul(H, Wc_V)` suivie de `attention(Qc, Kc, Vc)`, sans masque ; la double boucle sur sᵢⱼ et la softmax sont le corps de `attention`. PasInfoNCE est `perte_et_gradients` : les deux encodages sont `encoder(Eq, q)` et `encoder(Ed, doc)`, la ligne « perte » est `info_nce`, la ligne Gᵢⱼ est `gradient_info_nce`, la rétropropagation est la boucle sur `cote`, et la mise à jour est la double boucle `Eq[r][w] -= eta * g_q[r][w]` de `main`. RechercheDeuxÉtages n'est pas exécutée ici : le premier étage est `recall_a_1` (qui ne garde que le meilleur document), et le coût des deux étages est compté par `couts` ; le cross-encodeur lui-même est le sujet de l'étape 30 bis.

## Cas d'usage réels aux Émirats

Les volumes, les tailles de lot, les températures et les seuils ci-dessous sont illustratifs ; les nombres qui sortent d'une formule sont ceux du programme.

### Secteur public — un modèle d'embedding bilingue entraîné en interne

Une entité de services publics en ligne accessible par UAE Pass répond à partir d'environ 3 000 fiches officielles, rédigées en arabe et en anglais. Les usagers écrivent dans les deux langues, souvent mélangées, parfois en arabe translittéré en lettres latines, et un modèle d'embedding générique classe mal ces questions : le mot de l'usager n'est presque jamais celui de la fiche, comme dans le jouet du programme où requêtes et documents n'ont aucun mot commun. L'équipe constitue des paires (question, fiche consultée puis jugée utile) à partir des journaux, pseudonymisés et débarrassés des numéros d'Emirates ID avant tout usage, comme l'exige la PDPL, puis affine un encodeur ouvert avec InfoNCE, en lots de 256 et τ = 0,05. Elle sait lire la courbe : la perte doit partir près de ln 256 = 5,5452 (point 5), et un départ très différent signale un bug de données, par exemple des paires décalées d'une ligne. Le modèle est hébergé en interne : réencoder les 3 000 fiches après chaque réentraînement ne coûte que 3 000 passages hors ligne (point 7), et l'entité ne dépend d'aucun fournisseur pour un service qui doit rester disponible. Sans cet entraînement, l'agent ramène des fiches voisines mais fausses, et l'usager finit par appeler un centre de contact. L'indicateur suivi est le Recall@5 sur un jeu de questions étiquetées, séparé par langue.

### Banque — deux questions sur le même produit dans un lot

Une banque de détail de Dubaï affine son modèle d'embedding sur des paires (question de client, article de la base de connaissances) qui couvrent les cartes, les prêts personnels et la finance islamique. Les questions sur le financement immobilier Murabaha sont très nombreuses : dans un lot de 64 paires, il arrive que deux questions renvoient au même article, ou à deux articles presque identiques. Pour la première question, l'article de la seconde est alors traité comme un négatif, alors qu'il est pertinent. Avec τ = 0,02, la démonstration du point 6 montre ce qui se passe : si ce faux négatif dépasse le positif de 0,1 en cosinus, la ligne coûte environ 0,1 / 0,02 = 5, soit 5,007 dans le programme, et tout le gradient pousse à éloigner deux textes qui disent la même chose. L'équipe construit donc ses lots avec un échantillonneur qui interdit deux paires du même article, et masque dans la matrice des similarités les colonnes qui pointent vers un article jugé équivalent. Sans cette précaution, le modèle apprend à séparer des quasi-doublons, et l'agent hésite entre deux articles qui devraient être confondus. L'indicateur suivi est le Recall@1 par famille de produits, en particulier sur les produits de finance islamique.

### Immobilier — deux étages pour un catalogue de 200 000 annonces

Une agence et un promoteur actifs à Dubaï et à Abu Dhabi indexent 200 000 annonces et clauses de contrats, et leur agent reçoit environ 5 000 requêtes par jour, du type « trois chambres près du métro, moins de 2 000 AED/sqft ». Un cross-encodeur appliqué à tout le catalogue demanderait 10⁹ passages par jour et 3,2 × 10¹¹ tokens lus : c'est hors de portée. L'agent encode donc les annonces une fois, hors ligne, avec un bi-encodeur, récupère les 50 meilleures par cosinus, puis ne passe que ces 50 au cross-encodeur : 250 000 passages par jour, 4 000 fois moins, pour 80 100 000 tokens lus (point 7). Une annonce nouvelle ne coûte qu'un passage d'encodage ; un changement de modèle d'embedding, lui, oblige à réencoder les 200 000 annonces, parce que des vecteurs produits par deux modèles différents ne sont pas comparables. L'équipe versionne donc l'index avec le modèle qui l'a produit et bascule d'un bloc. Sans le second étage, l'agent propose des biens proches en vocabulaire mais faux sur un critère précis, comme le prix ou la station de métro. On suit le NDCG@10 (étape 28) et la latence au 95e centile de la requête complète.

### Assurance — un doublon de sinistre qui échappe au détecteur

Un assureur auto et santé, supervisé par la CBUAE, compare chaque nouvelle déclaration de sinistre aux déclarations des douze derniers mois : un cosinus au-dessus de 0,95 entre deux descriptions signale un doublon possible, et donc une fraude potentielle à examiner. Les embeddings sont calculés par lots, et une réimplémentation interne faisait la moyenne de tous les vecteurs de sortie, remplissage compris. La même description recevait alors un embedding différent selon la longueur de la plus longue déclaration du lot : dans le jouet du point 4, le cosinus entre les deux versions tombe à 0,8944, bien sous le seuil. Deux déclarations identiques passaient ainsi pour différentes, et le détecteur de doublons ratait précisément les cas les plus grossiers. L'équipe a corrigé la moyenne avec le masque des vrais tokens, vérifié que le même masque était transmis à l'attention, et ajouté un test : un texte encodé seul, puis au milieu de 31 autres, doit donner le même vecteur à 10⁻⁶ près. Sans ce test, le défaut ne fait planter aucun service, il dégrade seulement le rappel. L'indicateur suivi est le nombre de doublons confirmés détectés par mois, avec son rappel mesuré sur des doublons injectés volontairement.

### RH — un encodeur pour trier, un décodeur pour rédiger

Un cabinet RH présent dans plusieurs émirats reçoit chaque jour des milliers de messages de candidats et d'employés : visa, contrat enregistré auprès du MOHRE, paie versée par le WPS, indemnité de fin de service. Appeler un LLM pour classer chaque message coûterait cher et ajouterait de la latence ; le cabinet entraîne donc un petit encodeur qui lit le message entier, dans les deux sens, et choisit la file de traitement, puis ne réserve le LLM décodeur qu'à la rédaction des réponses. Avant l'affinage, il adapte l'encodeur à son vocabulaire par le modèle de langue masqué : sur 10 000 messages de 60 tokens, 15 % des positions donnent 90 000 cibles, alors qu'un décodeur entraîné sur les mêmes messages en aurait près de 600 000 (point 3). L'indemnité elle-même n'est jamais calculée par un modèle : l'outil `gratuite_fin_de_service` applique les règles du décret-loi fédéral 33/2021, et le classifieur ne fait qu'orienter le message vers la bonne file. Sans cet encodeur, chaque message coûte un appel de LLM, et les pics de demandes en fin de mois saturent le budget. On suit l'exactitude du routage sur un jeu étiqueté et le coût moyen par message traité.

### BTP — l'attention croisée relit le rapport source

Un groupe de construction sur de grands chantiers à Dubaï fait résumer, chaque soir, les rapports journaliers de ses sous-traitants, rédigés en anglais ou en arabe, en une note française pour la direction de projet. Il utilise un modèle encodeur-décodeur : l'encodeur lit une fois le rapport de 800 tokens, puis chaque token du résumé interroge ces 800 positions par l'attention croisée, avec des clés et des valeurs calculées une seule fois (point 2). Pour un résumé de 150 tokens, chaque couche d'attention croisée calcule ainsi 150 × 800 = 120 000 scores, sans jamais réencoder la source. Le point 2 rappelle aussi une limite : l'attention croisée ne fait que combiner ce que l'encodeur a lu, et un montant peut être mal recopié par le décodeur. Le groupe ajoute donc un garde-fou : chaque montant du résumé, en AED, doit apparaître à l'identique dans le rapport source, et les montants de TVA doivent valoir 5 % de leur base hors taxe, sinon la note part en revue humaine. Sans ce contrôle, une retenue de garantie mal recopiée peut fausser une décision de paiement à un sous-traitant. L'indicateur suivi est la part des notes dont tous les montants correspondent exactement à la source (étape 64).

## Pièges et limites

- **Laisser des faux négatifs dans le lot.** Deux paires sur le même document ou sur deux documents équivalents font éloigner des textes qui disent la même chose, d'autant plus fort que τ est petit ; on filtre les lots ou on masque ces colonnes.
- **Moyenner le remplissage.** L'embedding dépend alors du lot ; la moyenne doit utiliser le masque des vrais tokens, et le même masque doit être passé à l'attention.
- **Mélanger deux modèles dans un même index.** Les embeddings de deux modèles, ou de deux versions d'un même modèle, ne vivent pas dans le même espace ; on versionne l'index et on réencode tout le corpus au changement.
- **Oublier les conventions d'entrée du modèle.** Certains modèles d'embedding du marché attendent un préfixe différent pour les requêtes et pour les passages, et tous tronquent au-delà d'une longueur maximale, souvent 512 tokens pour les encodeurs de type BERT : la fin d'un long document n'est simplement pas encodée, d'où le découpage de l'étape 30 quater. On vérifie ces règles dans la fiche du modèle.
- **Choisir τ au hasard.** Trop petit, l'entraînement devient instable dès qu'un faux négatif apparaît ; trop grand, la perte reste bloquée au-dessus de ln(1 + (B − 1)·exp(−2/τ)) et les négatifs difficiles ne sont presque pas poussés.

### Exercice feuille blanche

1. Sans regarder le code, écrire `info_nce` et `gradient_info_nce`, puis retrouver 0,0512 pour τ = 0,1 et 0,7760 pour τ = 1 sur la matrice S du point 8.
2. Prédire, puis vérifier : pour un lot de B = 4 où sᵢᵢ = 1 et sᵢⱼ = 0 hors diagonale, que vaut la perte pour τ = 0,1 et pour τ = 1 ? (Réponse : ln(1 + 3e⁻¹⁰) ≈ 1,36 × 10⁻⁴, puis ln(1 + 3e⁻¹) = ln 2,1036 ≈ 0,7437.)
3. Trouver le bug : dans `info_nce`, la ligne devient `entropie_croisee([s / tau for s in ligne], 0)`, la classe 0 pour toutes les lignes. Que devient l'objectif, et que vaut le Recall@1 après entraînement ?

## Pour aller plus loin

ColBERT garde un vecteur par token au lieu d'un seul par phrase et note une paire par une « interaction tardive » (pour chaque token de la requête, le maximum de ses cosinus avec les tokens du document) : un compromis entre bi-encodeur et cross-encodeur. CLIP utilise une InfoNCE symétrique, dans les deux sens requête → document et document → requête. Van den Oord et al. (2018) ont montré que ln B − ℒ minore l'information mutuelle entre requête et document, ce qui explique l'intérêt des grands lots. Les négatifs difficiles extraits par BM25 ou par une première version du modèle, et la distillation d'un cross-encodeur vers un bi-encodeur (étape 73 ter), améliorent encore le rappel.

> Étape 36 ter du parcours · Prérequis : [Mélange d'experts (MoE)](<36b-Melange-d-Experts-MoE.md>) · Suite : [Transformer : formules de liaison](<37-Transformer-Formules-de-Liaison.md>)
