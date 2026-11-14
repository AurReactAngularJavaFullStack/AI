# Étape 79 — Formules mathématiques essentielles pour devenir un excellent AI Agentic Developer

## Objectif
Ce guide rassemble les équations qui donnent le meilleur retour sur investissement pour concevoir, comprendre, évaluer et fiabiliser des systèmes d’IA agentiques : modèles de langage, Transformers, RAG, appels d’outils, planification, coûts et évaluation.

**À retenir :** il n’est pas nécessaire de redémontrer chaque formule. Il faut savoir lire ses termes, expliquer son intuition, reconnaître quand elle s’applique et mesurer ses conséquences dans un système réel.

## Parcours conseillé
1. Algèbre linéaire et probabilités : comprendre les représentations et l’incertitude.
2. Optimisation et Transformers : comprendre l’apprentissage et la génération.
3. Retrieval/RAG : comprendre comment retrouver des preuves pertinentes.
4. Décision et renforcement : comprendre les boucles observe–décide–agit.
5. Évaluation, coût et fiabilité : transformer un prototype en système exploitable.

## 1. Fondations : algèbre linéaire

### Produit scalaire

**Équation :**

$$
x^\top y=\sum_{i=1}^{d}x_i y_i
$$

**Description :** Mesure l’alignement entre deux vecteurs. Il intervient dans les scores d’attention, les similarités et les projections.

**Pourquoi c’est important :** À maîtriser pour comprendre les embeddings, le ranking et les mécanismes internes des réseaux.

### Norme L2 et distance

**Équation :**

$$
\|x\|_2=\sqrt{\sum_i x_i^2} ,
$$

$$
d(x,y)=\|x-y\|_2
$$

**Description :** La norme mesure la magnitude d’un vecteur ; la distance euclidienne mesure l’écart entre deux représentations.

**Pourquoi c’est important :** Utile pour normaliser des embeddings, détecter des anomalies et raisonner sur les espaces vectoriels.

### Similarité cosinus

**Équation :**

$$
\operatorname{cos}(x,y)=\frac{x^\top y}{\|x\|_2\|y\|_2}
$$

**Description :** Compare l’orientation de deux vecteurs indépendamment de leur échelle.

**Pourquoi c’est important :** Fondamentale pour la recherche sémantique, le RAG et le dédoublonnage de contenus.

### Transformation affine

**Équation :**

$$
z=Wx+b
$$

**Description :** Transforme un vecteur d’entrée par une matrice de poids et un biais.

**Pourquoi c’est important :** C’est le bloc de base des couches denses, des projections Q/K/V et des têtes de sortie.

## 2. Calcul différentiel et optimisation

### Dérivée et gradient

**Équation :**

$$
\nabla_\theta L=\left[\frac{\partial L}{\partial\theta_1},\ldots,\frac{\partial L}{\partial\theta_n}\right]^\top
$$

**Description :** Le gradient indique la direction de plus forte augmentation de la perte.

**Pourquoi c’est important :** Comprendre le gradient permet de comprendre comment un modèle apprend et pourquoi l’entraînement peut diverger.

### Descente de gradient

**Équation :**

$$
\theta_{t+1}=\theta_t-\eta\nabla_\theta L(\theta_t)
$$

**Description :** Met à jour les paramètres dans la direction opposée au gradient ; η est le taux d’apprentissage.

**Pourquoi c’est important :** À connaître pour diagnostiquer sous-apprentissage, oscillations et instabilité d’entraînement.

### Règle de la chaîne

**Équation :**

$$
\frac{\partial L}{\partial x}=\frac{\partial L}{\partial y}\frac{\partial y}{\partial x}
$$

**Description :** Propage les dérivées à travers des opérations composées.

**Pourquoi c’est important :** C’est le principe du backpropagation dans les réseaux neuronaux.

### Régularisation L2

**Équation :**

$$
L_{\text{total}}=L_{\text{data}}+\lambda\|\theta\|_2^2
$$

**Description :** Pénalise les poids trop grands pour limiter la complexité du modèle.

**Pourquoi c’est important :** Relie optimisation, généralisation et contrôle du surapprentissage.

## 3. Probabilités et théorie de l’information

### Règle de Bayes

**Équation :**

$$
P(H\mid E)=\frac{P(E\mid H)P(H)}{P(E)}
$$

**Description :** Met à jour une croyance sur une hypothèse après observation d’une preuve.

**Pourquoi c’est important :** Utile pour raisonner sur l’incertitude, la classification, le diagnostic d’erreurs et la confiance d’un agent.

### Espérance

**Équation :**

$$
\mathbb{E}[X]=\sum_x xP(X=x)
$$

**Description :** Moyenne pondérée par les probabilités.

**Pourquoi c’est important :** Sert à comparer des actions selon leur résultat moyen attendu, notamment coût, latence ou récompense.

### Entropie

**Équation :**

$$
H(X)=-\sum_x P(x)\log P(x)
$$

**Description :** Mesure l’incertitude d’une distribution.

**Pourquoi c’est important :** Aide à comprendre l’incertitude de prédiction, le choix de questions et la diversité des sorties.

### Entropie croisée

**Équation :**

$$
L_{\text{CE}}=-\sum_i y_i\log p_i
$$

**Description :** Pénalise les probabilités attribuées aux mauvaises classes ; y est souvent une cible one-hot.

**Pourquoi c’est important :** Perte standard pour classification et prédiction du prochain token.

### Divergence KL

**Équation :**

$$
D_{\mathrm{KL}}(P\|Q)=\sum_xP(x)\log\frac{P(x)}{Q(x)}
$$

**Description :** Mesure l’écart informationnel entre deux distributions (asymétrique).

**Pourquoi c’est important :** Importante en distillation, alignement, modèles variationnels et comparaison de politiques.

## 4. Réseaux neuronaux et Transformers

### Sigmoïde et softmax

**Équation :**

$$
\sigma(z)=\frac{1}{1+e^{-z}} ,
$$

$$
\operatorname{softmax}(z_i)=\frac{e^{z_i}}{\sum_j e^{z_j}}
$$

**Description :** La sigmoïde donne une sortie entre 0 et 1 ; softmax transforme des scores en distribution.

**Pourquoi c’est important :** Softmax est au cœur de la sélection du prochain token et de l’attention.

### Attention

**Équation :**

$$
\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
$$

**Description :** Q interroge, K mesure la pertinence et V transporte l’information ; la division stabilise les scores.

**Pourquoi c’est important :** Équation centrale des Transformers : elle explique comment le contexte influence chaque token.

### Projection Q/K/V

**Équation :**

$$
Q=XW_Q,\quad K=XW_K,\quad V=XW_V
$$

**Description :** Projette les représentations des tokens dans trois espaces spécialisés.

**Pourquoi c’est important :** Indispensable pour lire un schéma Transformer et comprendre l’attention multi-têtes.

### Paramétrisation d’un token

**Équation :**

$$
h_i=e_i+p_i
$$

**Description :** Additionne embedding du token et information de position (dans les variantes classiques).

**Pourquoi c’est important :** Explique comment un modèle représente à la fois le contenu et l’ordre des tokens.

### Perte autoregressive

**Équation :**

$$
L=-\sum_{t=1}^{T}\log P(x_t\mid x_{<t})
$$

**Description :** Entraîne le modèle à prédire chaque token à partir des précédents.

**Pourquoi c’est important :** C’est l’objectif de base des modèles de langage génératifs.

## 5. Recherche, embeddings et RAG

### Score cosinus pour retrieval

**Équation :**

$$
s(q,d)=\frac{e_q^\top e_d}{\|e_q\|\|e_d\|}
$$

**Description :** Classe les passages selon leur proximité sémantique avec la requête.

**Pourquoi c’est important :** À connaître pour choisir un seuil, un top-k et analyser les faux positifs du retrieval.

### TF-IDF

**Équation :**

$$
\operatorname{tfidf}(t,d)=\operatorname{tf}(t,d)\log\frac{N}{\operatorname{df}(t)}
$$

**Description :** Valorise les termes fréquents dans un document mais rares dans le corpus.

**Pourquoi c’est important :** Base utile pour comprendre la recherche lexicale et pourquoi elle complète les embeddings.

### BM25 (forme simplifiée)

**Équation :**

$$
\operatorname{BM25}(q,d)=\sum_{t\in q}\operatorname{IDF}(t)\frac{f(t,d)(k_1+1)}{f(t,d)+k_1(1-b+b|d|/\overline{|d|})}
$$

**Description :** Combine rareté des termes, fréquence dans le document et normalisation par longueur.

**Pourquoi c’est important :** Très utile en recherche hybride : BM25 capte les mots exacts, les embeddings la proximité sémantique.

### Précision et rappel

**Équation :**

$$
\text{Précision}=\frac{TP}{TP+FP} ,
$$

$$
\text{Rappel}=\frac{TP}{TP+FN}
$$

**Description :** La précision mesure la pertinence des résultats retournés ; le rappel mesure la couverture des éléments pertinents.

**Pourquoi c’est important :** Permet d’évaluer un retriever et d’arbitrer entre résultats propres et couverture.

## 6. Décision agentique et apprentissage par renforcement

### Processus de décision markovien

**Équation :**

$$
\mathcal{M}=(S,A,P,R,\gamma)
$$

**Description :** Décrit états, actions, transitions, récompenses et facteur d’actualisation.

**Pourquoi c’est important :** Cadre conceptuel pour un agent qui observe, choisit un outil, agit et reçoit un résultat.

### Valeur d’une politique

**Équation :**

$$
V^\pi(s)=\mathbb{E}_\pi[\sum_{t=0}^{\infty}\gamma^t r_t\mid s_0=s]
$$

**Description :** Valeur attendue des récompenses futures en suivant la politique π.

**Pourquoi c’est important :** Formalise le compromis entre bénéfice immédiat et conséquences futures d’une action.

### Équation de Bellman

**Équation :**

$$
V^\pi(s)=\sum_a\pi(a\mid s)\sum_{s'}P(s'\mid s,a)[R(s,a,s')+\gamma V^\pi(s')]
$$

**Description :** Relie la valeur d’un état aux récompenses immédiates et aux valeurs des états suivants.

**Pourquoi c’est important :** Aide à comprendre la planification, l’évaluation de politiques et les agents à plusieurs étapes.

### Mise à jour Q-learning

**Équation :**

$$
Q(s,a)\leftarrow Q(s,a)+\alpha[r+\gamma\max_{a'}Q(s',a')-Q(s,a)]
$$

**Description :** Corrige une estimation de valeur d’action à partir d’une récompense et de la meilleure valeur future.

**Pourquoi c’est important :** Utile pour comprendre les bases de l’apprentissage par renforcement et les systèmes décisionnels.

### Gradient de politique (forme REINFORCE)

**Équation :**

$$
\nabla_\theta J(\theta)=\mathbb{E}[\nabla_\theta\log\pi_\theta(a\mid s)R]
$$

**Description :** Augmente la probabilité des actions associées à de bons retours.

**Pourquoi c’est important :** Relie optimisation des modèles et apprentissage de comportements.

## 7. Décision pratique : outils, coût et fiabilité

### Utilité espérée d’un outil

**Équation :**

$$
U(a)=\mathbb{E}[B(a)]-\lambda_c C(a)-\lambda_t T(a)-\lambda_r R(a)
$$

**Description :** Compare bénéfice attendu, coût, délai et risque d’une action.

**Pourquoi c’est important :** Un agent robuste ne choisit pas un outil parce qu’il existe : il le choisit si son utilité attendue est positive.

### Valeur de l’information

**Équation :**

$$
\operatorname{VOI}=\mathbb{E}[\max_a U(a\mid E)]-\max_a U(a)
$$

**Description :** Mesure le gain attendu à obtenir une information avant de décider.

**Pourquoi c’est important :** Aide à décider s’il faut rechercher, demander une précision ou agir immédiatement.

### Fiabilité en série

**Équation :**

$$
P(\text{succès})=\prod_{i=1}^{n}p_i
$$

**Description :** Si toutes les étapes sont nécessaires et indépendantes, la fiabilité globale est le produit des fiabilités.

**Pourquoi c’est important :** Explique pourquoi une longue chaîne d’outils peut être fragile même si chaque étape fonctionne souvent.

### Budget de contexte

**Équation :**

$$
B_{\text{disponible}}=B_{\text{total}}-B_{\text{instructions}}-B_{\text{historique}}-B_{\text{sortie}}
$$

**Description :** Réserve une partie de la fenêtre de contexte à la réponse et aux instructions.

**Pourquoi c’est important :** Essentiel pour le chunking, la mémoire, le résumé et la prévention de la troncature.

### Coût d’inférence

**Équation :**

$$
C_{\text{total}}\approx N_{\text{in}}c_{\text{in}}+N_{\text{out}}c_{\text{out}}+C_{\text{outils}}
$$

**Description :** Estime le coût selon tokens entrants/sortants et appels d’outils.

**Pourquoi c’est important :** Permet d’optimiser les workflows agentiques sans dégrader la qualité.

## 8. Évaluation et qualité

### F1-score

**Équation :**

$$
F_1=2\frac{PR}{P+R}
$$

**Description :** Moyenne harmonique de précision et rappel.

**Pourquoi c’est important :** Utile pour comparer des classifieurs ou des systèmes de retrieval lorsque les deux dimensions comptent.

### Taux de succès

**Équation :**

$$
\text{Success Rate}=\frac{\text{tâches réussies}}{\text{tâches évaluées}}
$$

**Description :** Mesure directement la proportion de tâches menées à bien.

**Pourquoi c’est important :** Métrique centrale pour évaluer un agent sur des scénarios réalistes.

### Taux d’hallucination

**Équation :**

$$
\text{Hallucination Rate}=\frac{\text{affirmations non étayées}}{\text{affirmations vérifiées}}
$$

**Description :** Estime la part d’affirmations non soutenues par les sources ou outils.

**Pourquoi c’est important :** À mesurer avec des critères explicites et des évaluations humaines ou automatiques.

### Calibration (Brier score)

**Équation :**

$$
\operatorname{BS}=\frac{1}{N}\sum_{i=1}^{N}(p_i-y_i)^2
$$

**Description :** Mesure l’erreur quadratique des probabilités annoncées.

**Pourquoi c’est important :** Une confiance calibrée aide l’agent à savoir quand vérifier, s’abstenir ou demander une clarification.

## Du symbole au code Python

Chaque équation des sections 1 à 8 a ici sa fonction Python, dans le même ordre que l'index, et chaque fonction est vérifiée sur un petit exemple chiffré, le même que dans la fiche d'image correspondante du dossier `Images/`. Le programme n'utilise que la bibliothèque standard.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`produit_scalaire(x, y)`** — Cette première fonction est la balance commune à tout le programme : elle reçoit deux vecteurs x et y, comme deux colonnes de chiffres posées côte à côte, et refuse d'aller plus loin en levant une `ValueError` « dimensions différentes » si les colonnes n'ont pas la même hauteur, car `zip` couperait sinon la plus longue sans prévenir. Elle multiplie ensuite chaque composante de x par sa voisine de y, additionne tous ces produits et renvoie ce seul nombre, 0,98 pour [0,8 ; 0,3 ; 0,5] et [0,7 ; 0,4 ; 0,6] ; la norme, le cosinus, la couche affine, l'attention et la projection s'appuient toutes sur elle.

**`norme_l2(x)`** — Celle-ci mesure la longueur d'une flèche comme un arpenteur qui tend sa chaîne de l'origine jusqu'à la pointe : elle reçoit un vecteur x, demande à `produit_scalaire` le produit de x avec lui-même, c'est-à-dire la somme des carrés de ses composantes, puis en prend la racine carrée avec `math.sqrt`. Elle renvoie cette longueur euclidienne, 5 pour le vecteur [3, 4], le triangle 3-4-5 des écoliers, et sert de brique à `distance` et à `cosinus`, qui ont besoin de connaître la taille des vecteurs qu'ils comparent.

**`distance(x, y)`** — Cette fonction répond à la question du voyageur qui veut savoir combien de chemin sépare deux villes posées sur la même carte : elle reçoit deux points x et y, construit composante par composante le vecteur des écarts x − y, puis confie ce vecteur à `norme_l2`, qui en renvoie la longueur. Le résultat est la distance euclidienne, 5 entre l'origine [0, 0] et le point [3, 4] dans le test de `main` ; il faut noter que la différence est fabriquée avec `zip` avant tout contrôle, de sorte qu'un vecteur plus long que l'autre serait tronqué sans erreur au lieu d'être refusé.

**`cosinus(x, y)`** — Voici le juge des directions, qui ne s'intéresse pas à la taille des flèches mais seulement à l'angle qu'elles forment, comme un marin qui compare deux caps sans se soucier de la vitesse des navires : elle reçoit deux vecteurs, calcule leurs deux normes avec `norme_l2` et lève une `ValueError` si l'une d'elles est nulle, puisqu'un vecteur nul n'indique aucune direction. Sinon elle renvoie le produit scalaire divisé par le produit des normes, un nombre compris entre −1 et 1, ici environ 0,98504 pour les deux embeddings x et y de `main`, presque alignés ; c'est la mesure de similarité que le RAG utilise pour classer les documents.

**`affine(W, x, b)`** — Cette fonction joue le rôle d'un atelier de mélange où chaque ouvrier dose les ingrédients d'entrée selon sa propre recette : elle reçoit une matrice W, dont chaque ligne est la recette d'une sortie, un vecteur d'entrée x et un vecteur de biais b. Pour chaque ligne de W, elle calcule le produit scalaire de cette ligne avec x et y ajoute le biais correspondant, puis renvoie la liste de ces sorties, z = W x + b ; avec W = [[1, 2], [0, 1]], x = [1, 1] et b = [0,5 ; −1], on obtient [3,5 ; 0], valeur exacte que `main` contrôle et qui illustre la couche linéaire d'un réseau de neurones.

**`gradient_numerique(L, theta, h)`** — Cette fonction est un explorateur prudent qui, pour savoir de quel côté la pente descend, fait un petit pas en avant puis un petit pas en arrière sur chaque axe : elle reçoit une fonction de perte L, un point theta sous forme de liste et un pas h, qui vaut 10⁻⁶ par défaut. Pour chaque coordonnée i, elle copie theta deux fois, ajoute h à la première copie et retire h à la seconde, puis calcule la différence centrée (L(θ + h eᵢ) − L(θ − h eᵢ)) / 2h ; elle renvoie la liste de ces dérivées partielles, environ (2 ; 6) pour la perte θ₁² + 3 θ₂² au point (1, 1), ce qui permet de vérifier en machine un gradient calculé à la main.

**`descente(grad, theta, eta, pas)`** — Celle-ci raconte un randonneur dans le brouillard qui, à chaque étape, consulte sa boussole de pente et avance d'une longueur fixe dans la direction qui descend : elle reçoit une fonction `grad` qui renvoie le gradient en un point, un point de départ theta, un taux d'apprentissage η et le nombre de pas à faire. À chaque tour de boucle, elle remplace chaque coordonnée θ par θ − η × gradient, puis renvoie le point atteint après le dernier pas ; sur la perte (θ − 3)², dont le gradient vaut 2 (θ − 3), trois pas de 0,1 depuis 0 mènent à 0,6, puis 1,08, puis 1,464, valeur que `main` vérifie et qui montre qu'on s'approche du minimum 3 sans l'atteindre encore.

**`regle_chaine(dL_dy, dy_dx)`** — Cette fonction minuscule incarne un relais où chaque coureur transmet au suivant la vitesse à laquelle il réagit : elle reçoit la dérivée de la perte par rapport à une variable intermédiaire y et la dérivée de y par rapport à x, et renvoie simplement leur produit, dL/dx = dL/dy × dy/dx. C'est le geste élémentaire de la rétropropagation, répété couche après couche dans un réseau de neurones ; dans `main`, une sensibilité de −2 multipliée par une sensibilité de 2 donne exactement −4, le résultat affiché sur la ligne de l'optimisation.

**`perte_regularisee(perte_donnees, theta, lam)`** — Cette fonction se comporte comme un professeur qui, à la note d'erreur d'un élève, ajoute une pénalité pour l'excès de complication de sa copie : elle reçoit la perte déjà calculée sur les données, la liste des paramètres theta et le coefficient de régularisation λ. Elle additionne les carrés de tous les paramètres, multiplie cette somme par λ et l'ajoute à la perte des données, puis renvoie le total, la perte régularisée L2 ; pour une perte de 1, des paramètres [1, 2] et λ = 0,1, cela donne 1 + 0,1 × 5 = 1,5, comme le vérifie `main`.

**`bayes(p_e_si_h, p_h, p_e_si_non_h)`** — Cette fonction est l'enquêtrice qui révise son opinion à la lumière d'un indice : elle reçoit la probabilité d'observer l'indice E si l'hypothèse H est vraie, la probabilité a priori de H et la probabilité d'observer E si H est fausse. Elle calcule d'abord la probabilité totale de l'indice, P(E) = P(E | H) P(H) + P(E | non H) (1 − P(H)), puis renvoie le quotient de Bayes, P(E | H) P(H) / P(E), la probabilité de H une fois l'indice vu ; avec un a priori de 2 %, une sensibilité de 95 % et 10 % de fausses alarmes, P(E) vaut 0,117 et la probabilité révisée seulement 0,162 environ, ce qui rappelle qu'une alerte sur un événement rare reste souvent une fausse alerte.

**`esperance(valeurs, probas)`** — Celle-ci est le comptable qui calcule le gain moyen d'un pari avant qu'on le joue : elle reçoit la liste des valeurs possibles et la liste de leurs probabilités, et commence par vérifier que ces probabilités somment à 1 à 10⁻⁹ près, sans quoi elle lève une `ValueError`. Elle multiplie ensuite chaque valeur par sa probabilité et renvoie la somme de ces produits, l'espérance E[X] ; pour les valeurs 2, 5, 9 et 15 pondérées par 0,2, 0,5, 0,1 et 0,2, le compte donne 0,4 + 2,5 + 0,9 + 3 = 6,8, la valeur que `main` imprime et contrôle.

**`entropie(p)`** — Cette fonction mesure l'incertitude d'une distribution comme un météorologue qui chiffrerait le doute que laisse planer sa prévision : elle reçoit une liste de probabilités p et, pour chaque probabilité strictement positive, ajoute pᵢ × ln pᵢ, en ignorant les zéros selon la convention 0 ln 0 = 0, avant de renvoyer l'opposé de cette somme, exprimé en nats puisque le logarithme est népérien. Une pièce équilibrée, [0,5 ; 0,5], donne ln 2, environ 0,693, l'incertitude maximale pour deux issues, et `main` vérifie précisément cette égalité.

**`entropie_croisee(y, p)`** — Voici l'examinateur qui note une prédiction en regardant la probabilité qu'elle accordait à la bonne réponse : elle reçoit la distribution cible y, souvent un vecteur one-hot, et la distribution prédite p, puis additionne yᵢ × ln pᵢ sur les seules positions où la cible est non nulle et renvoie l'opposé de cette somme. Pour la cible [1, 0] et la prédiction [0,7 ; 0,3], il ne reste qu'un terme, −ln 0,7, environ 0,357 : plus le modèle était confiant dans la bonne classe, plus la perte est faible, et c'est cette quantité que l'entraînement d'un LLM cherche à réduire ; une probabilité prédite nulle sur la bonne classe ferait échouer `math.log`.

**`kl(p, q)`** — Cette fonction mesure combien on se trompe en décrivant le monde réel p avec la carte approximative q, comme un cartographe qui chiffrerait le prix de ses erreurs de tracé : elle reçoit deux distributions et additionne, pour chaque issue où p est strictement positive, pᵢ × ln(pᵢ / qᵢ), puis renvoie cette divergence de Kullback-Leibler, toujours positive ou nulle. Entre [0,5 ; 0,5] et [0,9 ; 0,1] elle vaut environ 0,511, et elle vaut exactement 0 quand les deux distributions sont identiques, deux faits que `main` vérifie ; une valeur qᵢ nulle là où pᵢ est positive provoquerait une division par zéro.

**`sigmoide(z)`** — Cette fonction est un robinet doux qui transforme n'importe quel score réel en un débit compris entre 0 et 1 : elle reçoit un nombre z, calcule 1 / (1 + e⁻ᶻ) et renvoie ce résultat, proche de 0 pour un score très négatif, proche de 1 pour un score très positif, et exactement 0,5 pour z = 0, le point d'équilibre que `main` contrôle. Elle sert de fonction d'activation et de convertisseur d'un logit en probabilité dans les classifieurs binaires ; pour un z très négatif, l'exponentielle pourrait déborder, cas que le programme n'exerce pas.

**`softmax(z)`** — Celle-ci est le répartiteur qui partage un gâteau de probabilité entre plusieurs candidats selon leurs scores : elle reçoit une liste de logits z, retire d'abord à chacun le plus grand d'entre eux pour que l'exponentielle ne déborde jamais, calcule l'exponentielle de chaque écart, puis divise chacune par leur somme. Elle renvoie une liste de probabilités positives qui somment à 1, [0,665 ; 0,245 ; 0,09] pour les logits 2, 1 et 0, et elle est réutilisée par `attention` pour transformer des scores en poids et par `reinforce_un_pas` pour définir la politique ; la somme des exponentielles est recalculée pour chaque élément, ce qui reste correct mais inutilement répétitif.

**`attention(Q, K, V)`** — Cette fonction met en scène un lecteur qui, pour chaque question qu'il se pose, parcourt les étiquettes d'une bibliothèque et décide combien de temps passer devant chaque rayon : elle reçoit la liste des requêtes Q, celle des clés K et celle des valeurs V, et lit la dimension dₖ sur la longueur de la première clé. Pour chaque requête, elle calcule le produit scalaire avec chaque clé divisé par √dₖ, transforme ces scores en poids avec `softmax`, puis forme, colonne par colonne, la moyenne des valeurs pondérée par ces poids ; elle renvoie la liste des sorties, une par requête. Avec la requête [1, 0] et trois clés égales aux valeurs, les poids valent environ 0,431, 0,245 et 0,325 et la sortie [0,574 ; 0,426], tirée vers la première valeur, la plus proche de la requête.

**`projeter(X, W)`** — Cette fonction joue le rôle d'un traducteur qui fait passer chaque token d'un espace de représentation à un autre : elle reçoit une matrice X, une ligne par token, et une matrice de projection W, extrait les colonnes de W en transposant la matrice avec `zip(*W)`, puis calcule pour chaque ligne de X son produit scalaire avec chaque colonne. Elle renvoie le produit matriciel X W, ligne par ligne, c'est-à-dire l'opération qui fabrique les requêtes, les clés et les valeurs d'une couche d'attention ; dans `main`, projeter la ligne [1, 2] par la matrice identité la laisse inchangée, ce qui vérifie que le calcul ne mélange pas les coordonnées.

**`representation_token(e, p)`** — Cette fonction colle sur chaque mot une étiquette de place, comme un placeur de théâtre qui inscrit le numéro du siège sur le billet : elle reçoit le vecteur d'embedding e d'un token et le vecteur d'encodage de position p, et renvoie leur somme composante par composante, la représentation qui entre dans le Transformer et qui dit à la fois quel est le mot et où il se trouve. Pour l'embedding [1, 2] et la position [0,5 ; −1], elle renvoie [1,5 ; 1], le résultat exact que vérifie `main`, sans contrôler que les deux vecteurs ont la même longueur.

**`perte_autoregressive(probas_des_tokens_vus)`** — Celle-ci est la greffière qui tient le registre de toutes les surprises du modèle au fil d'une phrase : elle reçoit la liste des probabilités que le modèle avait attribuées, position après position, au token qui est réellement venu ensuite, additionne leurs logarithmes et renvoie l'opposé de cette somme, la log-vraisemblance négative −Σ ln P. Dix tokens prédits chacun avec la probabilité 0,5 coûtent 10 ln 2, environ 6,931, la valeur que `main` contrôle ; c'est la perte que l'on minimise pendant l'entraînement d'un modèle de langage, et une probabilité nulle la ferait échouer.

**`tfidf(tf, n_docs, df)`** — Cette fonction pèse l'importance d'un mot dans un document comme un bibliothécaire qui se méfie des mots trop communs : elle reçoit la fréquence tf du terme dans le document, le nombre total N de documents et le nombre df de documents qui contiennent ce terme, et renvoie tf × ln(N / df). Un terme présent 3 fois dans un document mais seulement dans 10 documents sur 1 000 obtient 3 × ln 100, environ 13,82, alors qu'un mot présent dans tous les documents aurait un poids nul ; un df nul provoquerait une division par zéro, cas que la fonction ne protège pas.

**`bm25_terme(idf, f, longueur, longueur_moyenne, k1, b)`** — Voici le juge de recherche plein de nuances, qui récompense la répétition d'un mot sans se laisser éblouir par elle : il reçoit l'IDF du terme, sa fréquence f dans le document, la longueur du document, la longueur moyenne du corpus, et les deux réglages k₁ = 1,2 et b = 0,75 par défaut. Il calcule IDF × f × (k₁ + 1) / (f + k₁ × (1 − b + b × longueur / longueur moyenne)), où k₁ fait saturer l'effet des répétitions et b pénalise les documents longs, puis renvoie cette contribution du terme au score BM25. Pour un IDF de 2 et un terme vu 3 fois dans un document de 200 mots quand la moyenne est de 100, le dénominateur vaut 3 + 2,1 = 5,1 et la contribution environ 2,588.

**`precision(tp, fp)`** — Cette fonction est le contrôleur qualité qui regarde le panier de documents rapporté par le moteur et compte la part de bons fruits : elle reçoit le nombre de vrais positifs tp et celui de faux positifs fp, et renvoie le quotient tp / (tp + fp), la proportion des éléments retenus qui sont réellement pertinents. Avec 7 bons documents et 3 intrus, la précision vaut 0,7, valeur que `main` imprime sur la ligne de la recherche ; contrairement à `f1`, elle ne protège pas le cas où rien n'est retenu, qui provoquerait une division par zéro.

**`rappel(tp, fn)`** — Celle-ci est la sœur de la précédente, mais elle se demande cette fois ce que le moteur a oublié sur l'étagère : elle reçoit le nombre de vrais positifs tp et celui de faux négatifs fn, et renvoie tp / (tp + fn), la part des documents pertinents qui ont effectivement été retrouvés. Avec 7 documents trouvés et 3 manqués, le rappel vaut lui aussi 0,7 dans l'exemple de `main` ; comme `precision`, elle lève une `ZeroDivisionError` s'il n'existe aucun document pertinent, ce qui rappelle qu'un rappel n'a de sens que pour une question qui possède au moins une bonne réponse.

**`retour_actualise(recompenses, gamma)`** — Cette fonction remonte le temps comme un comptable qui relit son carnet de la dernière page vers la première : elle reçoit la suite des récompenses d'un épisode et le facteur d'actualisation γ, part d'un retour G nul puis, pour chaque récompense lue à rebours, remplace G par r + γ G. Ce chemin à reculons évite de calculer la moindre puissance de γ, et la fonction renvoie le retour actualisé Σ γᵗ rₜ de tout l'épisode : pour les récompenses 1, 0, 2 et 2 avec γ = 0,9, on obtient 1 + 0 + 0,81 × 2 + 0,729 × 2 = 4,078, la valeur que `main` vérifie.

**`evaluer_politique(etats, pi, P, R, gamma, tours)`** — Cette fonction est l'arpenteur patient d'un petit monde de décision, qui repasse inlassablement sur chaque état pour affiner l'estimation de ce qu'il vaut : elle reçoit la liste des états, une politique pi qui donne pour chaque état la probabilité de chaque action, un dictionnaire de transitions P, un dictionnaire de récompenses R indexé par le triplet état, action, état suivant, le facteur γ et un nombre de tours, 500 par défaut. Partant de valeurs nulles, elle applique à chaque tour l'équation de Bellman, V(s) ← Σ π(a | s) Σ P(s′ | s, a) × (R + γ V(s′)), à tous les états à la fois, puis renvoie le dictionnaire des valeurs obtenues après le dernier tour. Pour un état unique qui boucle sur lui-même avec une récompense 1 et γ = 0,9, elle trouve 10, soit 1 / (1 − 0,9) ; malgré sa docstring, elle ne teste pas la convergence et s'arrête simplement au bout du nombre de tours demandé.

**`q_learning(q, r, gamma, max_q_suivant, alpha)`** — Celle-ci figure un apprenti qui corrige un peu son estimation chaque fois que la réalité le surprend : elle reçoit la valeur Q actuelle d'un couple état-action, la récompense r reçue, le facteur γ, la meilleure valeur Q de l'état suivant et le taux d'apprentissage α. Elle calcule la cible r + γ × max Q′, mesure l'écart entre cette cible et l'ancienne valeur, puis renvoie l'ancienne valeur augmentée de α fois cet écart ; avec Q = 2, r = 1, γ = 0,9, une meilleure valeur suivante de 5 et α = 0,5, la cible vaut 5,5, l'écart 3,5 et la nouvelle valeur 3,75, exactement ce que vérifie `main`.

**`reinforce_un_pas(theta, action, retour, pas)`** — Cette fonction raconte un joueur qui, après une partie, renforce l'habitude qui lui a rapporté : elle reçoit les préférences theta d'une politique softmax, l'action jouée, le retour obtenu et le pas d'apprentissage. Elle calcule la politique π avec `softmax`, forme le gradient du logarithme de la probabilité de l'action jouée, qui vaut 1 − π pour cette action et −π pour les autres, puis renvoie les nouvelles préférences θ + pas × retour × gradient. Partant de préférences nulles, donc de deux actions à 50 %, un retour de 1 et un pas de 0,1 sur la première action la font passer à environ 0,525, et c'est ce petit glissement que `main` vérifie ; la docstring parle de deux actions, mais le calcul vaut pour n'importe quel nombre d'actions.

**`utilite(benefice_moyen, cout, delai, risque, l_c, l_t, l_r)`** — Cette fonction est le conseiller prudent qui, avant qu'un agent appelle un outil, met en balance ce que l'appel rapporte et ce qu'il coûte : elle reçoit le bénéfice moyen attendu, le coût, le délai et le risque de l'action, ainsi que les trois poids λ qui disent combien pèse chaque désagrément. Elle retranche du bénéfice le coût pondéré, le délai pondéré et le risque pondéré, puis renvoie cette utilité ; pour un bénéfice de 90, un coût de 20 pondéré par 1, un délai de 3 pondéré par 2 et un risque de 0,1 pondéré par 50, le calcul donne 90 − 20 − 6 − 5 = 59, la valeur affichée comme U(A).

**`valeur_information(issues, actions, utilite_de)`** — Celle-ci estime combien vaudrait un informateur qui révélerait l'issue avant qu'on décide : elle reçoit un dictionnaire des issues possibles et de leurs probabilités, la liste des actions et une fonction qui donne l'utilité d'une action pour une issue. Elle calcule d'abord la moyenne, sur les issues, de la meilleure utilité qu'on obtiendrait en connaissant l'issue, puis la meilleure des utilités moyennes quand on doit choisir à l'aveugle, et renvoie la différence, la valeur de l'information parfaite. Sur l'exemple du remboursement, avec 80 % de dossiers sains et 20 % de fraudes, on gagne 80 en moyenne avec l'information et 0 sans elle, d'où une VOI de 80 : il vaudrait la peine de payer jusqu'à 80 pour vérifier avant de valider.

**`fiabilite_serie(p)`** — Cette fonction suit une chaîne de montage où chaque poste doit réussir pour que le produit sorte intact : elle reçoit la liste des probabilités de réussite des étapes et renvoie leur produit, calculé par `math.prod`, la probabilité que toutes réussissent si leurs échecs sont indépendants. Cinq étapes fiables chacune à 0,9 ne laissent qu'une chance de 0,59049 que la chaîne entière aboutisse, un peu moins de six sur dix, ce que `main` vérifie pour rappeler qu'enchaîner des étapes individuellement bonnes peut produire un système médiocre.

**`budget_disponible(total, instructions, historique, sortie)`** — Celle-ci est l'intendante de la fenêtre de contexte, qui fait les comptes avant de laisser entrer de nouveaux passages : elle reçoit la taille totale de la fenêtre en tokens, la part réservée aux instructions, celle de l'historique et celle gardée pour la réponse, et renvoie ce qui reste une fois ces trois réservations retranchées. Pour une fenêtre de 200 000 tokens, 6 000 tokens d'instructions, 40 000 d'historique et 8 000 réservés à la sortie, il reste 146 000 tokens pour les documents récupérés ; la fonction ne vérifie pas que le résultat reste positif.

**`cout_inference(n_in, c_in, n_out, c_out, c_outils)`** — Cette fonction est la caissière qui établit la note d'un tour d'agent : elle reçoit le nombre de tokens d'entrée et leur prix unitaire, le nombre de tokens de sortie et leur prix unitaire, et le coût des appels d'outils, puis renvoie la somme des deux produits et de ce coût fixe. Pour 12 000 tokens d'entrée à 3 × 10⁻⁶ l'unité, 800 tokens de sortie à 15 × 10⁻⁶ et 0,005 d'outils, la note s'élève à 0,036 + 0,012 + 0,005 = 0,053 dollar, l'unité qu'affiche le programme ; les prix sont ici donnés par token, et non par million de tokens comme dans d'autres fiches.

**`f1(p, r)`** — Voici le médiateur entre précision et rappel, qui refuse qu'un excellent score sur l'un masque un score désastreux sur l'autre : il reçoit une précision p et un rappel r, et renvoie leur moyenne harmonique, 2 p r / (p + r), ou 0 lorsque les deux valent zéro, ce qui évite la division par zéro. Avec une précision de deux tiers et un rappel parfait de 1, le F1 vaut 0,8, et non 0,833 environ comme le donnerait une simple moyenne arithmétique ; c'est la valeur que `main` affiche sur la ligne de l'évaluation.

**`taux(reussis, evalues)`** — Cette fonction est le greffier le plus simple du programme, qui divise ce qui a marché par ce qui a été tenté : elle reçoit un nombre de cas favorables et un nombre de cas examinés et renvoie leur quotient. `main` l'emploie deux fois, pour le taux de succès, 47 tâches réussies sur 50, soit 0,94, et pour le taux d'hallucination, 3 affirmations non étayées sur 40 vérifiées, soit 0,075, ce qui montre qu'une même formule sert deux métriques différentes ; un dénominateur nul lèverait une `ZeroDivisionError`.

**`brier(probas, issues)`** — Celle-ci note un prévisionniste qui annonce des probabilités et se fait juger sur les faits : elle reçoit la liste des confiances annoncées et la liste des issues réelles, codées 1 pour un succès et 0 pour un échec, calcule le carré de l'écart entre chaque confiance et son issue, puis renvoie la moyenne de ces carrés, le score de Brier, d'autant meilleur qu'il est petit. Pour les confiances 0,9, 0,8 et 0,3 face aux issues 1, 0 et 0, les écarts au carré valent 0,01, 0,64 et 0,09, d'où une moyenne d'environ 0,2467, plombée par la confiance de 0,8 annoncée sur un échec.

**`main()`** — C'est le chef d'orchestre qui fait jouer les huit sections de l'index dans l'ordre, comme un inspecteur qui coche une liste de contrôle : il définit d'abord une petite fonction anonyme `proche` qui tolère par défaut un écart de 10⁻⁴, puis, section par section, imprime une ligne de résultats et vérifie chacun par un `assert`, du produit scalaire 0,98 et de la norme 5 jusqu'au F1 de 0,8 et au score de Brier d'environ 0,2467, en passant par Bayes à 0,162, l'attention [0,574 ; 0,426], le TF-IDF de 13,82, le retour 4,078, la VOI de 80 et le budget de 146 000 tokens. Il fabrique au passage les données des exemples, comme la perte θ₁² + 3 θ₂², le petit processus de décision à un seul état ou la table d'utilités du remboursement, et n'affiche le message final de succès que si toutes les assertions ont tenu.

```python
"""Étape 79 — index des équations : une fonction par équation, chacune vérifiée sur un petit exemple."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- 1. Fondations : algèbre linéaire
def produit_scalaire(x, y):
    if len(x) != len(y):
        raise ValueError("dimensions différentes")
    return sum(a * b for a, b in zip(x, y))


def norme_l2(x):
    return math.sqrt(produit_scalaire(x, x))


def distance(x, y):
    return norme_l2([a - b for a, b in zip(x, y)])


def cosinus(x, y):
    nx, ny = norme_l2(x), norme_l2(y)
    if nx == 0 or ny == 0:
        raise ValueError("cosinus non défini pour un vecteur nul")
    return produit_scalaire(x, y) / (nx * ny)


def affine(W, x, b):
    """z = W x + b : une ligne de W par sortie."""
    return [produit_scalaire(ligne, x) + bi for ligne, bi in zip(W, b)]


# ---------------------------------------------------------------- 2. Calcul différentiel et optimisation
def gradient_numerique(L, theta, h=1e-6):
    """Différences centrées : ∂L/∂θᵢ ≈ (L(θ + h eᵢ) − L(θ − h eᵢ)) / 2h."""
    g = []
    for i in range(len(theta)):
        plus, moins = theta[:], theta[:]
        plus[i] += h
        moins[i] -= h
        g.append((L(plus) - L(moins)) / (2 * h))
    return g


def descente(grad, theta, eta, pas):
    for _ in range(pas):
        theta = [t - eta * g for t, g in zip(theta, grad(theta))]
    return theta


def regle_chaine(dL_dy, dy_dx):
    return dL_dy * dy_dx


def perte_regularisee(perte_donnees, theta, lam):
    return perte_donnees + lam * sum(t * t for t in theta)


# ---------------------------------------------------------------- 3. Probabilités et information
def bayes(p_e_si_h, p_h, p_e_si_non_h):
    p_e = p_e_si_h * p_h + p_e_si_non_h * (1 - p_h)          # probabilités totales
    return p_e_si_h * p_h / p_e


def esperance(valeurs, probas):
    if abs(sum(probas) - 1) > 1e-9:
        raise ValueError("les probabilités doivent sommer à 1")
    return sum(x * p for x, p in zip(valeurs, probas))


def entropie(p):
    return -sum(pi * math.log(pi) for pi in p if pi > 0)          # convention 0 ln 0 = 0


def entropie_croisee(y, p):
    return -sum(yi * math.log(pi) for yi, pi in zip(y, p) if yi > 0)


def kl(p, q):
    return sum(pi * math.log(pi / qi) for pi, qi in zip(p, q) if pi > 0)


# ---------------------------------------------------------------- 4. Réseaux neuronaux et Transformers
def sigmoide(z):
    return 1 / (1 + math.exp(-z))


def softmax(z):
    m = max(z)
    e = [math.exp(x - m) for x in z]
    return [x / sum(e) for x in e]


def attention(Q, K, V):
    d_k = len(K[0])
    sorties = []
    for q in Q:
        poids = softmax([produit_scalaire(q, k) / math.sqrt(d_k) for k in K])
        sorties.append([sum(w * v[c] for w, v in zip(poids, V)) for c in range(len(V[0]))])
    return sorties


def projeter(X, W):
    """X W : chaque ligne de X (un token) multipliée par W."""
    colonnes = list(zip(*W))
    return [[produit_scalaire(ligne, col) for col in colonnes] for ligne in X]


def representation_token(e, p):
    return [a + b for a, b in zip(e, p)]


def perte_autoregressive(probas_des_tokens_vus):
    return -sum(math.log(p) for p in probas_des_tokens_vus)


# ---------------------------------------------------------------- 5. Recherche et RAG
def tfidf(tf, n_docs, df):
    return tf * math.log(n_docs / df)


def bm25_terme(idf, f, longueur, longueur_moyenne, k1=1.2, b=0.75):
    return idf * f * (k1 + 1) / (f + k1 * (1 - b + b * longueur / longueur_moyenne))


def precision(tp, fp):
    return tp / (tp + fp)


def rappel(tp, fn):
    return tp / (tp + fn)


# ---------------------------------------------------------------- 6. Décision et apprentissage par renforcement
def retour_actualise(recompenses, gamma):
    """Σ γᵗ rₜ, calculé depuis la fin : G = r + γ G."""
    G = 0.0
    for r in reversed(recompenses):
        G = r + gamma * G
    return G


def evaluer_politique(etats, pi, P, R, gamma, tours=500):
    """Itère V(s) ← Σ_a π(a|s) Σ_s' P(s'|s,a) [R(s,a,s') + γ V(s')] jusqu'au point fixe."""
    V = {s: 0.0 for s in etats}
    for _ in range(tours):
        V = {s: sum(pa * sum(ps * (R[(s, a, s2)] + gamma * V[s2]) for s2, ps in P[(s, a)].items())
                    for a, pa in pi[s].items())
             for s in etats}
    return V


def q_learning(q, r, gamma, max_q_suivant, alpha):
    return q + alpha * (r + gamma * max_q_suivant - q)


def reinforce_un_pas(theta, action, retour, pas):
    """Politique softmax à deux actions : ∇ log π(a) = one_hot(a) − π."""
    pi = softmax(theta)
    grad = [(1.0 if i == action else 0.0) - pi[i] for i in range(len(theta))]
    return [t + pas * retour * g for t, g in zip(theta, grad)]


# ---------------------------------------------------------------- 7. Décision pratique
def utilite(benefice_moyen, cout, delai, risque, l_c, l_t, l_r):
    return benefice_moyen - l_c * cout - l_t * delai - l_r * risque


def valeur_information(issues, actions, utilite_de):
    """VOI = E[max_a U(a | issue)] − max_a E[U(a)], pour une information parfaite."""
    avec = sum(p * max(utilite_de(a, e) for a in actions) for e, p in issues.items())
    sans = max(sum(p * utilite_de(a, e) for e, p in issues.items()) for a in actions)
    return avec - sans


def fiabilite_serie(p):
    return math.prod(p)


def budget_disponible(total, instructions, historique, sortie):
    return total - instructions - historique - sortie


def cout_inference(n_in, c_in, n_out, c_out, c_outils):
    return n_in * c_in + n_out * c_out + c_outils


# ---------------------------------------------------------------- 8. Évaluation
def f1(p, r):
    return 2 * p * r / (p + r) if p + r else 0.0


def taux(reussis, evalues):
    return reussis / evalues


def brier(probas, issues):
    return sum((p - y) ** 2 for p, y in zip(probas, issues)) / len(probas)


def main():
    proche = lambda a, b, tol=1e-4: abs(a - b) < tol

    print("1. Algèbre linéaire")
    x, y = [0.8, 0.3, 0.5], [0.7, 0.4, 0.6]
    print(f"  x·y = {produit_scalaire(x, y):.2f}   ‖[3,4]‖ = {norme_l2([3, 4]):.0f}   cos = {cosinus(x, y):.5f}")
    assert proche(produit_scalaire(x, y), 0.98) and norme_l2([3, 4]) == 5 and proche(cosinus(x, y), 0.98504, 1e-5)
    assert proche(distance([0, 0], [3, 4]), 5) and affine([[1, 2], [0, 1]], [1, 1], [0.5, -1]) == [3.5, 0]

    print("2. Optimisation")
    L = lambda t: t[0] ** 2 + 3 * t[1] ** 2
    g = gradient_numerique(L, [1.0, 1.0])
    th = descente(lambda t: [2 * (t[0] - 3)], [0.0], 0.1, 3)
    print(f"  ∇L(1,1) ≈ ({g[0]:.3f} ; {g[1]:.3f})   θ après 3 pas = {th[0]:.3f}   règle de la chaîne = {regle_chaine(-2, 2)}")
    assert proche(g[0], 2) and proche(g[1], 6) and proche(th[0], 1.464) and regle_chaine(-2, 2) == -4
    assert proche(perte_regularisee(1.0, [1, 2], 0.1), 1.5)

    print("3. Probabilités et information")
    pb = bayes(0.95, 0.02, 0.10)
    print(f"  Bayes = {pb:.3f}   E[X] = {esperance([2, 5, 9, 15], [0.2, 0.5, 0.1, 0.2]):.1f}   "
          f"H(½,½) = {entropie([0.5, 0.5]):.3f}   CE = {entropie_croisee([1, 0], [0.7, 0.3]):.3f}   "
          f"KL = {kl([0.5, 0.5], [0.9, 0.1]):.3f}")
    assert proche(pb, 0.16239) and proche(esperance([2, 5, 9, 15], [0.2, 0.5, 0.1, 0.2]), 6.8)
    assert proche(entropie([0.5, 0.5]), math.log(2)) and proche(entropie_croisee([1, 0], [0.7, 0.3]), 0.35667)
    assert proche(kl([0.5, 0.5], [0.9, 0.1]), 0.51083) and kl([0.3, 0.7], [0.3, 0.7]) == 0

    print("4. Réseaux et Transformers")
    o = attention([[1.0, 0.0]], [[0.9, 0.1], [0.1, 0.9], [0.5, 0.5]], [[0.9, 0.1], [0.1, 0.9], [0.5, 0.5]])
    print(f"  σ(0) = {sigmoide(0):.1f}   softmax(2,1,0) = {[round(p, 3) for p in softmax([2, 1, 0])]}   "
          f"attention = {[round(v, 3) for v in o[0]]}   perte(10 × 0,5) = {perte_autoregressive([0.5] * 10):.3f}")
    assert sigmoide(0) == 0.5 and [round(p, 3) for p in softmax([2, 1, 0])] == [0.665, 0.245, 0.09]
    assert [round(v, 3) for v in o[0]] == [0.574, 0.426]
    assert projeter([[1, 2]], [[1, 0], [0, 1]]) == [[1, 2]] and representation_token([1, 2], [0.5, -1]) == [1.5, 1]
    assert proche(perte_autoregressive([0.5] * 10), 6.93147)

    print("5. Recherche")
    print(f"  TF-IDF = {tfidf(3, 1000, 10):.2f}   BM25(terme) = {bm25_terme(2.0, 3, 200, 100):.3f}   "
          f"P = {precision(7, 3):.1f}   R = {rappel(7, 3):.1f}")
    assert proche(tfidf(3, 1000, 10), 13.8155) and proche(bm25_terme(2.0, 3, 200, 100), 2.58824)

    print("6. Décision et renforcement")
    G = retour_actualise([1.0, 0.0, 2.0, 2.0], 0.9)
    V = evaluer_politique(["s"], {"s": {"a": 1.0}}, {("s", "a"): {"s": 1.0}}, {("s", "a", "s"): 1.0}, 0.9)
    theta = reinforce_un_pas([0.0, 0.0], 0, 1.0, 0.1)
    print(f"  G = {G:.3f}   V(boucle r = 1, γ = 0,9) = {V['s']:.2f}   Q = {q_learning(2, 1, 0.9, 5, 0.5):.2f}   "
          f"π(a₁) après REINFORCE = {softmax(theta)[0]:.3f}")
    assert proche(G, 4.078) and proche(V["s"], 10.0) and q_learning(2, 1, 0.9, 5, 0.5) == 3.75
    assert proche(softmax(theta)[0], 0.52498)

    print("7. Décision pratique")
    u = lambda a, e: {"valider": {"sain": 100, "fraude": -400}, "refuser": {"sain": -50, "fraude": 0}}[a][e]
    voi = valeur_information({"sain": 0.8, "fraude": 0.2}, ["valider", "refuser"], u)
    print(f"  U(A) = {utilite(90, 20, 3, 0.1, 1, 2, 50):.0f}   VOI = {voi:.0f}   P(chaîne 5 × 0,9) = {fiabilite_serie([0.9] * 5):.3f}   "
          f"budget = {budget_disponible(200_000, 6_000, 40_000, 8_000):,}   coût = {cout_inference(12_000, 3e-6, 800, 15e-6, 0.005):.3f} $")
    assert proche(utilite(90, 20, 3, 0.1, 1, 2, 50), 59) and proche(voi, 80)
    assert proche(fiabilite_serie([0.9] * 5), 0.59049) and budget_disponible(200_000, 6_000, 40_000, 8_000) == 146_000
    assert proche(cout_inference(12_000, 3e-6, 800, 15e-6, 0.005), 0.053)

    print("8. Évaluation")
    print(f"  F1 = {f1(2 / 3, 1):.1f}   succès = {taux(47, 50):.2f}   hallucination = {taux(3, 40):.3f}   "
          f"Brier = {brier([0.9, 0.8, 0.3], [1, 0, 0]):.4f}")
    assert proche(f1(2 / 3, 1), 0.8) and taux(47, 50) == 0.94 and proche(brier([0.9, 0.8, 0.3], [1, 0, 0]), 0.24667)

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Algèbre linéaire
  x·y = 0.98   ‖[3,4]‖ = 5   cos = 0.98504
2. Optimisation
  ∇L(1,1) ≈ (2.000 ; 6.000)   θ après 3 pas = 1.464   règle de la chaîne = -4
3. Probabilités et information
  Bayes = 0.162   E[X] = 6.8   H(½,½) = 0.693   CE = 0.357   KL = 0.511
4. Réseaux et Transformers
  σ(0) = 0.5   softmax(2,1,0) = [0.665, 0.245, 0.09]   attention = [0.574, 0.426]   perte(10 × 0,5) = 6.931
5. Recherche
  TF-IDF = 13.82   BM25(terme) = 2.588   P = 0.7   R = 0.7
6. Décision et renforcement
  G = 4.078   V(boucle r = 1, γ = 0,9) = 10.00   Q = 3.75   π(a₁) après REINFORCE = 0.525
7. Décision pratique
  U(A) = 59   VOI = 80   P(chaîne 5 × 0,9) = 0.590   budget = 146,000   coût = 0.053 $
8. Évaluation
  F1 = 0.8   succès = 0.94   hallucination = 0.075   Brier = 0.2467
OK — toutes les vérifications sont passées.
```

### Comment le code fonctionne

**Algèbre linéaire.** `produit_scalaire` vérifie que les deux vecteurs ont la même dimension avant d'additionner les produits terme à terme, parce que `zip` couperait sinon silencieusement le plus long. `norme_l2` est la racine du produit scalaire d'un vecteur avec lui-même, `distance` la norme de la différence, et `cosinus` le quotient du produit scalaire par le produit des normes, avec une erreur explicite pour un vecteur nul. `affine` calcule une sortie par ligne de W : le produit scalaire de cette ligne avec x, plus le biais correspondant.

**Optimisation.** `gradient_numerique` approche chaque dérivée partielle par une différence centrée, en déplaçant une seule coordonnée de ±h : c'est la définition du gradient appliquée en machine, utile pour vérifier une dérivée calculée à la main. `descente` répète le pas θ ← θ − η ∇L le nombre de fois demandé ; sur la perte (θ − 3)², trois pas de 0,1 depuis 0 mènent à 1,464, comme dans la fiche 08. `regle_chaine` multiplie deux dérivées, et `perte_regularisee` ajoute λ fois la somme des carrés des paramètres.

**Probabilités et information.** `bayes` calcule d'abord P(E) par la formule des probabilités totales, puis le quotient de Bayes ; avec un taux d'erreur de 2 %, une sensibilité de 95 % et 10 % de fausses alarmes, il donne 0,162. `esperance` refuse des probabilités qui ne somment pas à 1. `entropie` et `kl` ignorent les cas de probabilité nulle (la convention 0 ln 0 = 0), et `entropie_croisee` ne garde que les termes où la cible est non nulle.

**Réseaux et Transformers.** `sigmoide` et `softmax` sont les deux fonctions d'activation ; `softmax` soustrait le maximum avant l'exponentielle pour ne jamais déborder. `attention` calcule, pour chaque requête, les scores divisés par √d_k, leurs poids par softmax, puis la moyenne pondérée des valeurs. `projeter` multiplie chaque ligne de X par W en parcourant les colonnes de W, `representation_token` additionne embedding et position, et `perte_autoregressive` additionne les −ln des probabilités des tokens vus.

**Recherche.** `tfidf` multiplie la fréquence du terme par le logarithme de N / df, et `bm25_terme` calcule la contribution d'un terme à BM25, avec saturation par k₁ et normalisation de longueur par b. `precision` et `rappel` sont les deux quotients de la matrice de confusion.

**Décision et renforcement.** `retour_actualise` calcule Σ γᵗ rₜ en remontant depuis la fin avec G ← r + γ G, ce qui évite les puissances. `evaluer_politique` itère l'équation de Bellman jusqu'au point fixe sur un petit processus de décision décrit par des dictionnaires ; sur un état qui boucle sur lui-même avec une récompense 1 et γ = 0,9, elle trouve V = 1 / (1 − 0,9) = 10. `q_learning` applique une mise à jour, et `reinforce_un_pas` un pas de gradient de politique sur une softmax à deux actions, avec le gradient « one-hot de l'action moins π ».

**Décision pratique.** `utilite` retranche du bénéfice moyen les trois pénalités pondérées. `valeur_information` compare la meilleure utilité moyenne quand on connaît l'issue avant de décider à la meilleure utilité moyenne sans la connaître ; sur l'exemple du remboursement (20 % de fraudes), la différence vaut 80. `fiabilite_serie`, `budget_disponible` et `cout_inference` sont un produit, une soustraction et une somme pondérée.

**Évaluation.** `f1` calcule la moyenne harmonique et renvoie 0 si P et R sont tous deux nuls, `taux` sert au taux de succès comme au taux d'hallucination, et `brier` fait la moyenne des carrés des écarts entre la confiance annoncée et l'issue réelle.

## Squelette algorithmique

Les équations de l'index ne sont pas isolées : un tour d'agent bien conçu les enchaîne. Le squelette ci-dessous montre où chacune intervient, de la préparation du contexte à l'évaluation du résultat.

```text
ALGORITHME TourDAgentOutillé
ENTRÉES : question, mémoire, corpus, outils candidats, fenêtre B_total, prix, seuils
SORTIE  : réponse, et les mesures qui permettent de juger ce tour

  B_disponible ← B_total − B_instructions − B_historique − B_sortie            (budget de contexte)
  candidats ← documents classés par Cosinus(question, d) et par BM25(question, d)
  passages ← les meilleurs candidats qui tiennent dans B_disponible
  POUR CHAQUE outil a FAIRE
      U(a) ← E[B(a)] − λ_c C(a) − λ_t T(a) − λ_r R(a)                          (utilité espérée)
  FIN POUR
  SI VOI(chercher davantage) > coût de la recherche ALORS chercher, puis recalculer les U(a)
  SI maxₐ U(a) ≤ 0 ALORS répondre sans outil
  SINON appeler l'outil de plus grande utilité
  P_succès ← Π pᵢ sur les étapes de la chaîne prévue                           (fiabilité en série)
  coût ← N_in c_in + N_out c_out + C_outils                                   (coût d'inférence)
  réponse ← génération token par token (softmax, attention ; perte −Σ ln P à l'entraînement)
  APRÈS COUP, sur un jeu d'évaluation :
      précision, rappel, F1 du retrieval ; taux de succès ; taux d'hallucination ; score de Brier
```

**Complexité.** Le budget, l'utilité, la VOI sur une information binaire, la fiabilité et le coût sont des calculs en O(1) ou en O(nombre d'outils). Le classement des documents coûte O(n × d) pour les cosinus et O(n log n) pour le tri ; la génération coûte, pour chaque token produit, une attention en O(n × d) sur un contexte de n tokens. Les mesures d'évaluation se calculent en une passe sur le jeu d'évaluation.

**Du squelette au code.** Chaque ligne commentée du squelette correspond à une fonction du programme : `budget_disponible`, `cosinus` et `bm25_terme`, `utilite`, `valeur_information`, `fiabilite_serie`, `cout_inference`, `softmax` et `attention`, `perte_autoregressive`, puis `precision`, `rappel`, `f1`, `taux` et `brier`. Les leçons du parcours déroulent chacune de ces fonctions en détail ; le tableau « Où l'algorithme est raconté », plus bas, donne l'étape de chaque équation.

## 9. Priorisation : quoi apprendre en premier ?

| Priorité | Équations | Pourquoi |
|---|---|---|
| Indispensable | Produit scalaire, cosinus, softmax, attention, entropie croisée | Comprendre embeddings, Transformers et génération |
| Très importante | Bayes, gradient, descente de gradient, Bellman, utilité espérée | Comprendre apprentissage, décision et incertitude |
| Très pratique | BM25, précision/rappel, F1, budget de contexte, coût d’inférence | Construire et optimiser un RAG/agent en production |
| Approfondissement | KL, Q-learning, gradient de politique, Brier | Comprendre alignement, RL et calibration |

## 10. Comment les utiliser dans un projet agentique

- **RAG :** mesurer la qualité du retrieval avec précision/rappel, comparer BM25 et cosinus, puis vérifier la fidélité des réponses aux passages récupérés.
- **Agent avec outils :** définir une utilité qui prend en compte le bénéfice, le coût, la latence et le risque ; ne pas appeler un outil sans raison.
- **Planification :** représenter les états, actions, résultats possibles et récompenses ; tenir compte des conséquences à plusieurs étapes.
- **Mémoire et contexte :** budgéter les tokens, résumer l’historique et ne conserver que l’information utile à la tâche.
- **Production :** suivre taux de réussite, taux d’erreur, latence, coût par tâche, appels d’outils et taux d’affirmations non étayées.

## 11. Limites et bonnes pratiques

- Les équations sont des modèles simplifiés : les implémentations réelles peuvent ajouter masques, normalisations, contraintes, heuristiques et approximations.
- La formule de fiabilité en série suppose l’indépendance des étapes et que toutes soient nécessaires ; cette hypothèse est souvent imparfaite.
- Le taux d’hallucination dépend d’une définition opérationnelle claire de l’« affirmation non étayée ».
- Une métrique isolée ne suffit pas : évaluer un agent avec des tâches représentatives, des cas limites, des tests de sécurité et des évaluations humaines.
- En pratique, l’ingénierie logicielle, la qualité des données, l’observabilité, la sécurité et la conception des outils comptent autant que les mathématiques.

## 12. Mini-glossaire

- **Embedding :** vecteur numérique représentant un token, un passage ou un objet.
- **Logit :** score brut avant softmax.
- **Token :** unité de texte traitée par le modèle.
- **Retrieval :** recherche des documents ou passages pertinents.
- **RAG :** génération augmentée par récupération de documents.
- **Politique :** règle qui associe un état à une distribution d’actions.
- **Reward / récompense :** signal numérique qui évalue un résultat.
- **Calibration :** cohérence entre confiance annoncée et fréquence réelle de réussite.

---
*Document pédagogique — les formules sont présentées sous une forme standard et volontairement compacte. Les notations peuvent varier selon les ouvrages et les architectures.*

## Où l'algorithme est raconté

Ce fichier liste les équations. Le calcul, ligne par ligne et avec des nombres, est dans les chapitres suivants.

| Sujet | Fichier |
| --- | --- |
| Cosinus, norme, top-k | `04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md` et `04-Contexte-Similarite-et-Memoire/15-Fondements-RAG-et-Memoire.md` |
| Softmax, température, gradient | `02-LLM-Softmax-et-Prompts/02-Softmax-Temperature-Prochain-Token.md` et `02-LLM-Softmax-et-Prompts/03-Fondements-Softmax-et-LLM.md` |
| Bellman | `07-Planification/38-Agent-et-Planification-MDP-Bellman.md` |
| DAG, Kahn, cycle DFS | `08-Orchestration/42-Orchestration-Graphes.md`, `08-Orchestration/44-Tri-Topologique-Kahn.md`, `08-Orchestration/45-Detection-de-Cycle-DFS.md` |
| Précision, rappel, KL | `10-Evaluation/50-Precision-Rappel-F1-et-KL.md` |
| Spécificité, NPV, AUC, perplexité | `10-Evaluation/51-Specificite-NPV-AUC.md`, `10-Evaluation/52-Perplexite-LLM.md` |
| Attention, multi-têtes, position, LayerNorm | `06-Attention-et-Transformer/33-Transformer-et-Attention-Deroule-Numerique.md`, `06-Attention-et-Transformer/34-Attention-Multi-Tetes.md`, `06-Attention-et-Transformer/35-Encodage-de-Position.md`, `06-Attention-et-Transformer/36-Normalisation-de-Couche.md` |
| Gradient, LoRA, Adam, L1/L2, rétropropagation | `12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md`, `12-Production-Couts-Optimisation/74-Optimiseur-Adam.md`, `12-Production-Couts-Optimisation/76-Regularisation-L1-L2.md`, `12-Production-Couts-Optimisation/75-Optimisation-Formules.md` |
| Files, M/M/1, Erlang C, Kendall | `12-Production-Couts-Optimisation/69-Files-Attente-et-Goulot.md`, `12-Production-Couts-Optimisation/70-File-MM1.md`, `12-Production-Couts-Optimisation/71-Erlang-C.md`, `12-Production-Couts-Optimisation/68-Notation-de-Kendall.md` |
| Coût des tokens | `12-Production-Couts-Optimisation/72-Couts-et-Gestion-des-Tokens.md` |

`78-Synthese-Mathematiques-de-l-Agent-IA.md` est le support en diapositives : une idée par écran, pas le déroulé d'un algorithme. Les pas de calcul sont dans les fichiers du tableau.
