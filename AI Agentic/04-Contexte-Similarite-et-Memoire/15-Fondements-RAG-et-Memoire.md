# Étape 15 — Vector Search, Similarité Cosinus et Espace Hilbertien (Le Cœur du RAG et de la Mémoire Agentique)

> Étape 15 du parcours · Prérequis : [Similarité cosinus et produit scalaire](<14-Similarite-Cosinus-RAG-et-Memoire.md>) · Suite : [La mémoire d'un agent : définitions](<15b-Memoire-Definitions-Fondamentaux.md>)

---

## 1. Contextualisation et Rôle dans le Développement d'Agents IA

Dans les architectures d'agents autonomes modernes (telles que ReAct, AutoGPT, LangGraph ou MemGPT), l'agent possède deux composantes mémoires fondamentales :
1. **La mémoire de travail (Working Memory / Short-Term Memory)** : constituée par la fenêtre de contexte du LLM (

$$
N_{\text{context}}
$$

tokens).
2. **La mémoire épisodique et sémantique (Long-Term Memory / RAG)** : hébergée au sein d'une base de données vectorielle (par exemple PGVector, Qdrant, Milvus ou Chroma, disponibles en open source).

Un **AI Agentic Developer** ne peut pas se contenter de voir la recherche vectorielle comme une boîte noire ("black box"). La sélection de la métrique de distance et la compréhension mathématique de la géométrie des espaces à très haute dimension (d ∈ [384, 4096]) conditionnent directement :
* **La précision du Retrieval** (éviter d'injecter des données hors-sujet dans le prompt de l'agent).
* **Le coût financier des API** (minimiser le nombre de tokens non pertinents passés au LLM).
* **La latence globale du système** (temps de recherche dans des graphes type HNSW ou index IVFFlat).

---

## 2. Définition Mathématique Formelle et Axiomatique

Soit ℝᵈ un espace vectoriel euclidien de dimension d, muni du produit scalaire canonique ⟨ ·, · ⟩.

### A. Définition du Produit Scalaire
Pour deux vecteurs

$$
A = (a_1, a_2, \dots, a_d)^T \in \mathbb{R}^d
$$

et

$$
B = (b_1, b_2, \dots, b_d)^T \in \mathbb{R}^d ,
$$

le produit scalaire est l'application bilinéaire symétrique définie positive :

$$
\langle A, B \rangle = A \cdot B = \sum_{i=1}^{d} a_i b_i
$$

### B. Norme L2 (Norme Euclidienne)
La norme induite sur ℝᵈ par ce produit scalaire, représentant la longueur du vecteur dans l'espace hilbertien, est définie par :

$$
\|A\|_2 = \sqrt{\langle A, A \rangle} = \sqrt{\sum_{i=1}^{d} a_i^2}
$$

### C. Similarité Cosinus
La **similarité cosinus** entre deux vecteurs non nuls A, B ∈ ℝᵈ ∖ {0} correspond au cosinus de l'angle géométrique non orienté

$$
\theta = \widehat{(A, B)}
$$

formé par ces deux vecteurs dans le plan 2D sous-tendu par (A, B) :

$$
S_{\cos}(A, B) = \cos(\theta) = \frac{\langle A, B \rangle}{\|A\|_2 \|B\|_2} = \frac{\sum_{i=1}^{d} a_i b_i}{\sqrt{\sum_{i=1}^{d} a_i^2} \sqrt{\sum_{i=1}^{d} b_i^2}}
$$

### D. Distance Cosinus
Par extension, on définit la **distance cosinus** (qui est une pseudo-distance, ne respectant pas strictement l'inégalité triangulaire mais très utilisée en pratique) par :

$$
D_{\cos}(A, B) = 1 - S_{\cos}(A, B) = 1 - \frac{A \cdot B}{\|A\|_2 \|B\|_2}
$$

---

## 3. Démonstration Mathématique : Équivalence avec la Distance Euclidienne Normalisée

Un concept fondamental pour optimiser la vitesse de calcul d'un agent IA est l'équivalence entre la **similarité cosinus** et la **distance euclidienne** lorsque les vecteurs d'embeddings sont préalablement normalisés sur la sphère unité Sᵈ⁻¹. L'étape 14 reprend cette preuve et démontre aussi les deux résultats sur lesquels elle s'appuie : l'inégalité de Cauchy-Schwarz, qui garantit

$$
-1 \le S_{\cos} \le 1 ,
$$

et l'invariance d'échelle, qui justifie qu'on puisse normaliser sans changer le cosinus.

### Théorème :
Si A et B sont deux vecteurs d'embeddings unitaires (i.e. ‖A‖₂ = 1 et ‖B‖₂ = 1), alors le carré de la distance euclidienne

$$
D_E^2(A, B) = \|A - B\|_2^2
$$

est directement une fonction linéaire affine de la similarité cosinus.

### Démonstration Étape par Étape :

**Étape 1.** Exprimons le carré de la norme de la différence ‖A − B‖₂² via le produit scalaire :

$$
\|A - B\|_2^2 = \langle A - B, A - B \rangle
$$

**Étape 2.** Par bilinéarité et symétrie du produit scalaire :

$$
\|A - B\|_2^2 = \langle A, A \rangle - 2\langle A, B \rangle + \langle B, B \rangle
$$

**Étape 3.** Par définition de la norme L2 :

$$
\|A - B\|_2^2 = \|A\|_2^2 - 2(A \cdot B) + \|B\|_2^2
$$

**Étape 4.** Injectons l'hypothèse de normalisation ‖A‖₂ = 1 et ‖B‖₂ = 1 :

$$
\|A - B\|_2^2 = 1^2 - 2(A \cdot B) + 1^2 = 2 - 2(A \cdot B)
$$

**Étape 5.** Or, puisque ‖A‖₂ = ‖B‖₂ = 1, la similarité cosinus se réduit simplement au produit scalaire

$$
S_{\cos}(A, B) = A \cdot B .
$$

Par conséquent :

$$
\|A - B\|_2^2 = 2(1 - S_{\cos}(A, B)) = 2 D_{\cos}(A, B)
$$

### Corollaire et Résultat Opérationnel :

$$
D_{\cos}(A, B) = \frac{1}{2} \|A - B\|_2^2 \quad \text{pour tout } A, B \in S^{d-1}
$$

*CQFD.*

> **Impact d'ingénierie :** si vous pré-normalisez tous vos embeddings lors de l'ingestion dans la base vectorielle (v̂ = v / ‖v‖₂), le calcul du cosinus

$$
\frac{A \cdot B}{\|A\| \|B\|} ,
$$

> avec ses racines carrées et ses divisions, se résume à un simple produit scalaire Aᵀ B. Le matériel le calcule alors par blocs entiers (instructions SIMD comme AVX-512, cœurs matriciels des GPU), ce qui peut rendre la recherche nettement plus rapide : un facteur de l'ordre de 4 est un ordre de grandeur illustratif, à mesurer sur sa propre machine.

---

## 4. Analyse Géométrique et Effets de Haute Dimension (La Malédiction de la Dimensionnalité)

Dans des espaces vectoriels de petite dimension (ℝ² ou ℝ³), la géométrie est intuitive. Dans un espace d'embeddings d'agents modernes (des modèles courants travaillent en d = 1024 ou d = 3072), plusieurs phénomènes mathématiques modifient radicalement le comportement du RAG :

### A. Concentricité de la Sphère et Orthogonalité Quasi-Certaine
En haute dimension, le volume d'une hyper-sphère est concentré de façon critique au niveau de sa surface fine (sa "croûte"). De plus, deux vecteurs tirés uniformément au hasard sur la sphère unité Sᵈ⁻¹ sont **presque toujours presque orthogonaux** : leur cosinus est proche de 0, avec un écart typique de l'ordre de 1/√d.

La densité de probabilité de l'angle θ entre deux vecteurs aléatoires en dimension d est donnée par :

$$
p(\theta) \propto (\sin \theta)^{d-2}
$$

Lorsque d → ∞, cette densité, une fois normalisée, se concentre autour de

$$
\theta = \frac{\pi}{2}
$$

(soit

$$
90^\circ
$$

) et tend vers une masse de Dirac en ce point.

* **Conséquence pour l'agent IA** : pour des vecteurs tirés au hasard, deux directions sans rapport ont un cosinus très proche de 0, avec un écart typique d'environ

$$
1/\sqrt{1536} \approx 0{,}026
$$

en dimension 1536 ; un cosinus de 0,6 y serait très loin du bruit. Mais les vecteurs d'un vrai modèle d'embedding ne sont pas tirés au hasard : ils occupent un cône étroit de l'espace (on dit que l'espace est anisotrope), si bien que deux textes sans rapport ont souvent un cosinus nettement positif, dans une bande de fond propre à chaque modèle (par exemple entre 0,2 et 0,5, valeurs illustratives). L'ancienne version affirmait à la fois que deux concepts sans lien ont un cosinus « extrêmement proche de 0 » et que les cosinus se concentrent dans [0,2 ; 0,5] (tableau de la section 6) : la première affirmation vaut pour des vecteurs aléatoires, la seconde pour des embeddings réels. Le seuil de décision se calibre donc sur des paires étiquetées, modèle par modèle (étape 19), et le recentrage de la section B réduit ce biais commun.

### B. Le Phénomène des "Hubs" (Hubness Problem)
Dans les espaces d'embeddings d'agents, certains points appelés *hubs* deviennent artificiellement proches d'un nombre anormalement élevé d'autres points, quel que soit le sujet. Mathématiquement, la distribution des occurrences des vecteurs dans les k-plus proches voisins (k-NN) présente des queues épaisses (skewed distribution).
* **Implication pratique** : certains extraits de documents risquent de ressortir systématiquement dans le RAG de votre agent (ex : des disclaimers juridiques, des entêtes de formulaires). L'ingénieur peut appliquer un recentrage par la moyenne, suivi d'une nouvelle normalisation (Centering & Normalization) :

$$
\tilde{A} = A - \mathbb{E}[A]
$$

---

## 5. Cas d'usage chiffrés (chiffres illustratifs)

Les deux cas ci-dessous sont des scénarios d'école : leurs chiffres (latences, rappel, économies, taux d'erreur) sont illustratifs et ne proviennent pas d'un déploiement mesuré. Ils montrent comment raisonner, pas ce qu'on obtiendra.

### Cas A : Agent d'Assistance Technique Télécom à Échelle (10 millions de documents)

#### Contexte :
Un agent autonome de niveau N2 résout des tickets clients en cherchant dans la documentation technique. La base contient M = 10 000 000 de fragments (chunks) vectorisés en dimension d = 1536 par un modèle d'embedding.

#### Analyse quantitative du calcul brut (force brute, index plat) :
* Pour répondre à une seule question d'un utilisateur, l'agent doit calculer le cosinus entre le vecteur requête Q ∈ ℝ¹⁵³⁶ et les 10⁷ vecteurs stockés Vᵢ ∈ ℝ¹⁵³⁶.
* Le nombre d'opérations en virgule flottante (FLOPs) par recherche est :

$$
\text{Ops} = 10^7 \times (2 \times 1536) \approx 30{,}72 \times 10^9 \text{ FLOPs} = 30{,}72 \text{ GFLOPs}
$$

* Sur un serveur CPU multi-cœurs fournissant, par hypothèse, 100 GFLOPs/s, la latence de recherche pure serait de **307 millisecondes par question**, ce qui est inacceptable pour un agent conversationnel en temps réel qui effectue 4 à 5 appels mémoire par décision.

#### Solution d'Ingénierie Agentique (Index HNSW & Normalisation) :
1. **Normalisation à l'ingestion** : les vecteurs Vᵢ sont pré-normalisés (‖Vᵢ‖₂ = 1) ; à la recherche, il n'y a plus ni racine carrée ni division.
2. **Utilisation d'un index HNSW (Hierarchical Navigable Small World)** : le graphe ramène le coût d'une recherche d'environ O(M · d) à environ O(log(M) · d) en pratique (c'est un comportement observé, pas une garantie).
3. **Résultats chiffrés (illustratifs)** :
   * **Latence moyenne de retrieval** : passe de 320 ms à 4,2 ms.
   * **Rappel de l'index (Recall@10)** : 97,8 % des 10 vrais plus proches voisins sont retrouvés. L'ancienne version écrivait « Précision (Recall@10) » : précision et rappel sont deux mesures différentes, et il s'agit ici du rappel de la recherche approchée par rapport à la recherche exacte.
   * **Économie financière** : en passant d'un top-20 peu précis à un top-3 filtré par un seuil cosinus de 0,78, la consommation de tokens d'entrée baisse de 85 %, soit une économie de 14 200 USD par mois sur les appels au LLM dans ce scénario.

### Cas B : Mémoire Épisodique Long-Terme d'un Agent Financier (Personal Wealth Agent)

#### Problème de Contamination Sémantique :
Un agent financier stocke toutes les conversations passées de l'utilisateur.
* Phrase stockée il y a 6 mois : *"Je déteste les actions de la tech, je veux tout vendre."* (Vecteur

$$
V_{\text{passé}}
$$

)
* Nouvelle instruction de l'utilisateur : *"Achète des actions dans le secteur des technologies renouvelables."* (Vecteur

$$
Q_{\text{actuel}}
$$

)

#### Risque Mathématique :
En effectuant une simple similarité cosinus non pondérée, la présence des termes *"actions"*, *"tech"*, *"secteur"* génère un score cosinus élevé (dans ce scénario,

$$
S_{\cos} \approx 0{,}72
$$

) entre la restriction passée et la demande actuelle. L'agent risque de bloquer l'ordre d'achat par erreur (Faux Positif).

#### Résolution par Pondération Temporelle et Sémantique Hybride :
Pour un bon AI Agentic Developer, le score de décision de la mémoire d'un agent ne doit pas être uniquement basé sur la similarité cosinus géométrique, mais sur un score combiné pondéré par une décroissance exponentielle du temps (Désintégration de la mémoire / Memory Decay) :

$$
\text{Score}_{\text{Final}}(Q, V_i, t_{\text{actuel}}, t_i) = S_{\cos}(Q, V_i) \cdot \exp\left( -\lambda \cdot (t_{\text{actuel}} - t_i) \right)
$$

Où λ est le **taux** de décroissance, en jours⁻¹ ; l'ancienne version l'appelait à tort « la demi-vie ». La demi-vie vaut

$$
t_{1/2} = \ln 2 / \lambda
$$

Une demi-vie de 90 jours donne donc λ = ln 2 / 90 ≈ 0,0077 par jour (l'étape 16 démontre cette relation).

* **Résultat chiffré (illustratif)** : dans ce scénario, le taux d'erreurs de décision de l'agent financier passe de 23,4 % à moins de 0,9 %. Une limite demeure : un refus fort exprimé il y a six mois peut rester valable ; l'étape 17 ajoute l'importance du souvenir, pour qu'une contrainte forte ne s'efface pas seulement parce qu'elle est ancienne.

---

## 6. Synthèse des Bonnes Pratiques pour l'Ingénieur IA

**Propriété Mathématique :** **Vecteurs non normalisés** · **Risque si Ignorée :** Calculs superflus de racines carrées et de divisions à chaque requête ; produit scalaire et cosinus ne donnent plus le même classement. · **Implémentation Requise :** Appliquer la norme L2 lors du chunking/embedding (V ← V / ‖ V ‖₂).

**Propriété Mathématique :** **Effet de dimension (d > 1000)** · **Risque si Ignorée :** Vecteurs aléatoires : cosinus concentré autour de 0 (écart typique 1/√d). Embeddings réels : bande de fond positive propre au modèle, par exemple [0,2 ; 0,5] (valeurs illustratives) ; un seuil fixe mal choisi laisse passer du bruit. · **Implémentation Requise :** Calibrer le seuil d'activation de la mémoire sur des paires étiquetées, modèle par modèle (étape 19) ; recentrer si besoin.

**Propriété Mathématique :** **Complexité linéaire O(M · d)** · **Risque si Ignorée :** Latence qui croît avec le volume de mémoire ; au-delà de quelques centaines de milliers de chunks (ordre de grandeur illustratif), le balayage complet devient coûteux. · **Implémentation Requise :** Basculer d'un index plat (PGVector sans index) vers un index **HNSW** ou **IVFFlat**.

**Propriété Mathématique :** **Confiance excessive dans le cosinus seul** · **Risque si Ignorée :** Incapacité à traiter les dépendances temporelles et les annulations d'ordres. · **Implémentation Requise :** Hybrider la recherche : (formule ci-dessous), avec des composantes ramenées à la même échelle (étapes 17 et 23).

$$
\text{Score} = w_{sim} S_{\cos} + w_{lex} S_{\text{BM25}} + w_{rec} f(\Delta t)
$$

---

## 7. Du symbole au code : la démonstration, ligne par ligne

Le bloc rejoue la démonstration de la section 3 sur deux vecteurs fixés, puis la concentration des angles, le score daté, le recentrage et le compte d'opérations. Voici ce que chaque ligne fait à ces nombres. Copiez dans `fondements_rag.py`.

### Déroulé, ligne par ligne

**Les cinq fonctions du haut** sont les briques. `dot` additionne `a * b` case par case. `norme` vaut `sqrt(dot(A, A))`, parce que ‖A‖² = A · A. `cosinus` divise `dot(A, B)` par le produit des deux normes, et lève `ValueError` si l'une d'elles est nulle, parce que le vecteur nul n'a pas de direction. `normaliser` divise chaque case par `norme(A)`, avec le même refus du vecteur nul. `distance_carree` additionne `(a - b) ** 2`.

**`demonstration_sphere_unite`**, avec A = [1 ; 0] et B = [0,6 ; 0,8].

- `norme(A)` vaut 1, `norme(B)` vaut 1, parce que 0,6² + 0,8² = 1.
- `ecart = [a - b ...]` produit [0,4 ; −0,8]. Étape 1 du cours : le vecteur différence.
- `dot(ecart, ecart)` vaut

$$
0{,}4^2 + (-0{,}8)^2 = 0{,}16 + 0{,}64 = 0{,}80 .
$$

C'est ‖A−B‖² écrit comme un produit scalaire, sans passer par une racine puis un carré.
- `developpe = dot(A, A) - 2 * dot(A, B) + dot(B, B)`. On ouvre (A−B) · (A−B). Les trois termes valent 1, −2 × 0,6 et 1. Somme 0,80, la même.
- L'étape 4 remplace les deux normes au carré par 1, parce qu'on est sur la sphère : 1 − 2 × 0,6 + 1 = 0,80.
- `2 * (1 - cosinus(A, B))` vaut aussi 0,80, puisque le cosinus se réduit au produit scalaire 0,6. Les cinq écritures sont le même nombre. L'`assert` vérifie la dernière égalité à 10⁻¹² près.

Le contre-exemple change A en [3 ; 0], qui pointe au même endroit mais a une longueur 3.

- `distance_carree` vaut

$$
(3-0{,}6)^2 + (0-0{,}8)^2 = 5{,}76 + 0{,}64 = 6{,}40 .
$$

- Le cosinus, lui, ne voit pas la longueur : il vaut encore 0,6, donc `2 * (1 - cos)` vaut encore 0,80.
- `assert abs(gauche - droite) > 1.0` : l'identité est fausse de plusieurs unités. C'est pour ça que `normaliser` doit être appelé à l'ingestion, avant de remplacer le cosinus par un produit scalaire.

**`concentration_des_angles`.**

- `rng = random.Random(graine)` : même graine, mêmes vecteurs.
- Pour chacune des 1 000 paires, on tire `dimension` coordonnées gaussiennes pour A et pour B, puis on appelle `cosinus`. Des coordonnées gaussiennes indépendantes donnent une direction uniforme sur la sphère : c'est exactement le cadre de la section 4.A.
- `moyenne` est la moyenne arithmétique de ces cosinus. `typique` est la racine de la moyenne des carrés : l'ordre de grandeur d'un cosinus « au hasard », même si la moyenne est proche de 0 parce que les signes se compensent.
- À d = 4, cet écart vaut 0,508. À d = 1536, il vaut 0,026. Les `assert` vérifient qu'il décroît avec d et qu'il reste à moins de 5 % de 1/√d, qui vaut 0,5 ; 0,088 et 0,0255. Pour des vecteurs aléatoires, un cosinus de 0,70 en dimension 1536 serait donc très au-dessus du bruit. Mais un vrai modèle d'embedding n'est pas aléatoire : son bruit de fond est plus haut (section 4.A), si bien que le seuil de 0,70 utilisé plus bas est illustratif et se calibre sur des paires étiquetées (étape 19).

**`score_memoire(similarite, age_jours, demi_vie_jours)`.**

- `lam = math.log(2.0) / demi_vie_jours`. Avec une demi-vie de 90 jours, λ = ln 2 / 90 ≈ 0,00770 par jour. λ est un taux, pas une durée : c'est la demi-vie qui vaut 90 jours.
- `return similarite * math.exp(-lam * age_jours), lam` : le score, puis λ pour l'affichage. L'exponentielle vaut 1 à l'âge 0, et 1/2 quand l'âge égale la demi-vie. À 180 jours, deux demi-vies, elle vaut 1/4.
- 0,72 × 1 = 0,72, au-dessus du seuil 0,70 : le souvenir du jour déclenche. 0,72 × 0,25 = 0,18, en dessous : le souvenir de six mois ne déclenche pas, alors que son cosinus nu, 0,72, l'aurait fait.

**Le recentrage**, dans `main`.

- Trois chunks de dimension 2. La deuxième coordonnée vaut 0,9 partout : c'est le biais partagé, le « disclaimer ».
- `moyenne` calcule, coordonnée par coordonnée, `sum(c[j] for c in chunks) / len(chunks)`. On obtient [0,633 ; 0,900].
- `recentres` soustrait cette moyenne à chaque chunk. La deuxième case du premier chunk tombe à 0,9 − 0,9 = 0. La première, qui variait, reste à 0,267. Le biais commun a disparu, la coordonnée qui distinguait les textes reste. Les deux `assert` vérifient ces valeurs.

**Les FLOPs.**

- `flops = M * (2 * d)`, avec `M = 10_000_000` et `d = 1536`, vaut 30,72 milliards. Le `2` est une multiplication et une addition par coordonnée, pour chaque chunk.
- `latence_ms = flops / 100e9 * 1000` : 307 ms sur une machine à 100 milliards d'opérations par seconde (vitesse illustrative).
- `math.log(M) * d` : ln(10⁷) × 1536 ≈ 24 757 opérations. C'est une borne très optimiste, qui supposerait une seule comparaison par niveau du graphe ; l'ancienne version en tirait un gain d'environ 1,24 million de fois, ce qui le surestime beaucoup. En pratique, une recherche HNSW compare la question à quelques centaines ou milliers de vecteurs : avec 2 000 vecteurs comparés (valeur illustrative), on fait 2000 × 2 × 1536 = 6 144 000 opérations, soit 5 000 fois moins que le balayage complet. On ne code pas le graphe ici ; l'`assert` vérifie les deux comptes.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`dot(A, B)`** — Cette brique de base est le caissier qui multiplie, rayon par rayon, la quantité par le prix et additionne le tout : elle reçoit deux listes de nombres, les met face à face avec `zip` et renvoie la somme des produits case par case, le produit scalaire A · B. Elle ne vérifie pas que les deux listes ont la même longueur, `zip` s'arrêtant à la plus courte, et ne lève rien. Toutes les autres fonctions du bloc s'appuient sur elle : pour A = (1, 0) et B = (0,6 ; 0,8), elle renvoie 0,6, et le produit de l'écart (0,4 ; −0,8) par lui-même vaut 0,80.

**`norme(A)`** — Celle-ci mesure la longueur d'une flèche en la multipliant par elle-même, comme un géomètre qui sait que ‖A‖² = A · A : elle reçoit une liste de nombres, appelle `dot(A, A)` et renvoie la racine carrée du résultat, sans lever d'exception, 0 pour le vecteur nul. Dans la démonstration, elle confirme que A = (1, 0) et B = (0,6 ; 0,8) ont tous deux une longueur de 1, puisque 0,6² + 0,8² = 1, condition sur laquelle repose l'identité de la sphère unité.

**`cosinus(A, B)`** — C'est l'arbitre qui ne regarde que la direction de deux vecteurs : il reçoit deux listes, calcule leurs deux normes, lève `ValueError` avec le message « vecteur nul : le cosinus n'est pas défini » si l'une vaut 0, et renvoie le produit scalaire divisé par le produit des normes. Contrairement à la version de l'étape 14, il ne rabat pas le résultat dans [−1, 1] et n'imprime rien. Il vaut 0,6 pour A = (1, 0) et B = (0,6 ; 0,8), et encore 0,6 pour (3, 0) et B, puisque la longueur ne compte pas ; c'est lui que `concentration_des_angles` appelle mille fois par dimension.

**`normaliser(A)`** — Cette fonction est le tailleur qui ramène chaque flèche à la même longueur sans toucher à son cap : elle reçoit un vecteur, calcule sa norme, lève `ValueError` avec le message « impossible de normaliser le vecteur nul » si elle vaut 0, et renvoie la liste des coordonnées divisées par cette norme. C'est la règle d'ingestion que démontre le bloc : une fois chaque vecteur stocké sous la forme v / ‖v‖, la distance euclidienne au carré vaut exactement 2(1 − cos), et la recherche peut se faire par simple produit scalaire.

**`distance_carree(A, B)`** — Celle-ci est l'arpenteur qui mesure l'écart entre deux points sans prendre la racine : elle reçoit deux listes et renvoie la somme des carrés des différences case par case, ‖A − B‖², sans contrôle de longueur ni exception. Sur A = (1, 0) et B = (0,6 ; 0,8), elle vaut 0,16 + 0,64 = 0,80, exactement 2(1 − 0,6) ; mais sur (3, 0) et B, elle vaut 6,40, alors que 2(1 − cos) reste à 0,80, ce qui prouve qu'il faut normaliser avant de comparer des distances.

**`demonstration_sphere_unite()`** — C'est le professeur qui écrit au tableau, en cinq lignes, la démonstration de la section 3 sur deux vecteurs fixés : la fonction ne reçoit rien, prend A = (1, 0) et B = (0,6 ; 0,8), imprime leurs normes, puis l'écart et son produit scalaire avec lui-même, le développement ‖A‖² − 2 A · B + ‖B‖², les trois termes, l'hypothèse unité et enfin 2(1 − cos), qui valent tous 0,80. Elle vérifie l'égalité finale à 10⁻¹² près, rejoue le contre-exemple avec A = (3, 0), où 6,40 s'oppose à 0,80, et exige un écart de plus de 1. Elle ne renvoie rien.

**`concentration_des_angles(dimension, n_paires, graine)`** — Cette fonction est un sondeur qui lance des paires de flèches au hasard pour voir à quel point elles se ressemblent : elle reçoit la dimension, le nombre de paires et une graine, 0 par défaut, tire pour chaque paire deux vecteurs à coordonnées gaussiennes, calcule leur cosinus, puis renvoie le couple formé de la moyenne des cosinus et de leur écart quadratique moyen. Avec mille paires et la graine 1, cet écart vaut 0,5081 en dimension 4, 0,0887 en dimension 128 et 0,0256 en dimension 1 536, à moins de 5 % de 1/√d : en grande dimension, deux vecteurs pris au hasard sont presque orthogonaux.

**`score_memoire(similarite, age_jours, demi_vie_jours)`** — C'est l'archiviste qui fait pâlir l'encre des vieux souvenirs : la fonction reçoit une similarité cosinus, l'âge du souvenir en jours et une demi-vie, calcule le taux λ = ln 2 / demi-vie, puis renvoie le couple formé du score, similarité × exp(−λ × âge), et de λ lui-même. Elle ne contrôle pas ses entrées. Avec une demi-vie de 90 jours, λ vaut environ 0,00770 par jour ; un souvenir de similarité 0,72 garde 0,720 le jour même mais tombe à 0,180 après 180 jours, sous le seuil de 0,70, et un score de 1 vaut exactement 0,5 à 90 jours.

**`main()`** — C'est le metteur en scène des cinq tableaux du chapitre : il lance la démonstration de la sphère unité, mesure la concentration des angles en dimension 4, 128 et 1 536 et vérifie la décroissance en 1/√d, puis montre sur la mémoire financière que le cosinus nu de 0,72 déclencherait à tort alors que le score daté de 180 jours, 0,180, ne déclenche pas. Il recentre ensuite trois chunks de dimension 2, dont la moyenne vaut (0,633 ; 0,900) et dont le premier devient (0,267 ; 0), et chiffre la force brute sur 10 millions de chunks, 30,72 milliards d'opérations et 307 ms, contre une recherche réaliste 5 000 fois moins coûteuse.

```python
"""Fondements RAG — équivalence cosinus / euclidien, decay, coût du brute force."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def dot(A, B):
    return sum(a * b for a, b in zip(A, B))


def norme(A):
    return math.sqrt(dot(A, A))


def cosinus(A, B):
    na, nb = norme(A), norme(B)
    if na == 0.0 or nb == 0.0:
        raise ValueError("vecteur nul : le cosinus n'est pas défini")
    return dot(A, B) / (na * nb)


def normaliser(A):
    n = norme(A)
    if n == 0.0:
        raise ValueError("impossible de normaliser le vecteur nul")
    return [a / n for a in A]


def distance_carree(A, B):
    return sum((a - b) ** 2 for a, b in zip(A, B))


def demonstration_sphere_unite():
    """||A−B||² = 2(1 − cos) dès que ||A|| = ||B|| = 1."""
    print("=== Démonstration, avec A = (1, 0) et B = (0,6 ; 0,8) ===")
    A = [1.0, 0.0]
    B = [0.6, 0.8]
    print(f"  ||A|| = {norme(A):.4f}    ||B|| = {norme(B):.4f}")

    ecart = [a - b for a, b in zip(A, B)]
    print(f"1. A − B = {[round(x, 4) for x in ecart]}")
    print(f"   ||A − B||² = (A − B) · (A − B) = {dot(ecart, ecart):.4f}")

    developpe = dot(A, A) - 2 * dot(A, B) + dot(B, B)
    print(f"2. bilinéarité : ||A||² − 2 A·B + ||B||² = {developpe:.4f}")

    print(f"3. ||A||² = {dot(A, A):.4f}    ||B||² = {dot(B, B):.4f}    A·B = {dot(A, B):.4f}")
    print(f"4. hypothèse unité : 1 − 2×{dot(A, B):.4f} + 1 = {2 - 2 * dot(A, B):.4f}")
    print(f"5. 2(1 − cos) = {2 * (1 - cosinus(A, B)):.4f}")
    assert abs(distance_carree(A, B) - 2 * (1 - cosinus(A, B))) < 1e-12

    print("\n=== La même identité est fausse si on oublie de normaliser ===")
    brut_A = [3.0, 0.0]          # même direction que A, longueur 3
    brut_B = [0.6, 0.8]
    gauche = distance_carree(brut_A, brut_B)
    droite = 2 * (1 - cosinus(brut_A, brut_B))
    print(f"  ||A−B||² = {gauche:.4f}    2(1 − cos) = {droite:.4f}")
    assert abs(gauche - droite) > 1.0
    print("  D'où la règle d'ingestion : on stocke v / ||v||, et la recherche devient un produit scalaire.")


def concentration_des_angles(dimension, n_paires, graine=0):
    """En grande dimension, deux vecteurs gaussiens ont un cosinus proche de 0."""
    rng = random.Random(graine)
    cosinus_observes = []
    for _ in range(n_paires):
        A = [rng.gauss(0.0, 1.0) for _ in range(dimension)]
        B = [rng.gauss(0.0, 1.0) for _ in range(dimension)]
        cosinus_observes.append(cosinus(A, B))
    moyenne = sum(cosinus_observes) / n_paires
    typique = math.sqrt(sum(c * c for c in cosinus_observes) / n_paires)
    return moyenne, typique


def score_memoire(similarite, age_jours, demi_vie_jours):
    """Score = cos(Q, V) × exp(−λ Δt), avec λ = ln(2) / demi-vie."""
    lam = math.log(2.0) / demi_vie_jours
    return similarite * math.exp(-lam * age_jours), lam


def main():
    demonstration_sphere_unite()

    print("\n=== Angles en haute dimension (1 000 paires) ===")
    typiques = {}
    for d in (4, 128, 1536):
        moyenne, typique = concentration_des_angles(d, n_paires=1000, graine=1)
        typiques[d] = typique
        print(f"  d = {d:5d}   cosinus moyen = {moyenne:+.4f}   écart quadratique moyen = {typique:.4f}")
    assert typiques[1536] < typiques[128] < typiques[4]
    assert all(abs(typiques[d] * math.sqrt(d) - 1) < 0.05 for d in typiques)  # écart typique ≈ 1/√d
    print("  Vecteurs aléatoires : écart typique ≈ 1/√d, soit 0,026 en dimension 1536.")
    print("  Un vrai modèle d'embedding a un bruit de fond plus haut : le seuil se calibre (étape 19).")

    print("\n=== Mémoire financière : le cosinus seul se trompe, le temps corrige ===")
    # Le cours : S_cos ≈ 0,72 entre « je déteste la tech » (il y a 6 mois) et l'ordre d'achat.
    s_cos = 0.72
    seuil = 0.70
    score_frais, lam = score_memoire(s_cos, age_jours=0, demi_vie_jours=90)
    score_vieux, _ = score_memoire(s_cos, age_jours=180, demi_vie_jours=90)
    print(f"  λ = ln(2)/90 = {lam:.6f} par jour")
    print(f"  souvenir du jour     score = {score_frais:.3f}   déclenche : {score_frais > seuil}")
    print(f"  souvenir de 180 jours score = {score_vieux:.3f}   déclenche : {score_vieux > seuil}")
    a_90, _ = score_memoire(1.0, 90, 90)
    assert abs(a_90 - 0.5) < 1e-12
    assert score_frais > seuil > score_vieux

    print("\n=== Recentrage : enlever le biais partagé par tous les chunks ===")
    chunks = [
        [0.9, 0.9],   # disclaimer + sujet A
        [0.2, 0.9],   # sujet B + le même disclaimer sur la 2e coordonnée
        [0.8, 0.9],
    ]
    moyenne = [sum(c[j] for c in chunks) / len(chunks) for j in range(2)]
    recentres = [[c[j] - moyenne[j] for j in range(2)] for c in chunks]
    print(f"  moyenne = {[round(m, 4) for m in moyenne]}")
    print(f"  chunk 0 recentré = {[round(v, 4) for v in recentres[0]]}")
    assert [round(m, 3) for m in moyenne] == [0.633, 0.9]
    assert [round(v, 3) for v in recentres[0]] == [0.267, 0.0]
    print("  La coordonnée « disclaimer », presque constante, s'effondre. Le sujet reste.")

    print("\n=== 10 millions de chunks, dimension 1536, force brute ===")
    M, d = 10_000_000, 1536
    flops = M * (2 * d)
    latence_ms = flops / 100e9 * 1000
    print(f"  FLOPs = 10^7 × (2 × 1536) = {flops / 1e9:.2f} GFLOPs")
    print(f"  à 100 GFLOPs/s : {latence_ms:.0f} ms")
    candidats_hnsw = math.log(M) * d
    print(f"  borne très optimiste pour HNSW : ln(M) × d ≈ {candidats_hnsw:,.0f} opérations ({flops / candidats_hnsw:,.0f}× moins)")
    realiste = 2000 * (2 * d)   # en pratique, quelques milliers de vecteurs comparés (valeur illustrative)
    print(f"  plus réaliste : 2 000 vecteurs comparés ≈ {realiste:,.0f} opérations ({flops / realiste:,.0f}× moins)")
    assert abs(flops / 1e9 - 30.72) < 1e-9
    assert abs(latence_ms - 307.2) < 1e-6
    assert round(candidats_hnsw) == 24757 and round(flops / realiste) == 5000
    print("Identité vraie sur la sphère, fausse sans normalisation, demi-vie respectée.")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
=== Démonstration, avec A = (1, 0) et B = (0,6 ; 0,8) ===
…
5. 2(1 − cos) = 0.8000
…
  ||A−B||² = 6.4000    2(1 − cos) = 0.8000
…
  d =     4   cosinus moyen = +0.0039   écart quadratique moyen = 0.5081
  d =   128   cosinus moyen = -0.0016   écart quadratique moyen = 0.0887
  d =  1536   cosinus moyen = -0.0003   écart quadratique moyen = 0.0256
  Vecteurs aléatoires : écart typique ≈ 1/√d, soit 0,026 en dimension 1536.
…
  souvenir du jour     score = 0.720   déclenche : True
  souvenir de 180 jours score = 0.180   déclenche : False
…
  chunk 0 recentré = [0.2667, 0.0]
…
  borne très optimiste pour HNSW : ln(M) × d ≈ 24,757 opérations (1,240,841× moins)
  plus réaliste : 2 000 vecteurs comparés ≈ 6,144,000 opérations (5,000× moins)
Identité vraie sur la sphère, fausse sans normalisation, demi-vie respectée.
OK — toutes les vérifications sont passées.
```

Ce que la démonstration change dans le code d'un agent : normaliser à l'ingestion, sinon l'identité qui permet de remplacer le cosinus par un produit scalaire est fausse, comme le contre-exemple chiffré le montre. Le score de mémoire multiplie ensuite ce cosinus par une exponentielle du temps. Un seuil de 0,70 appliqué au cosinus nu et le même seuil appliqué au score daté ne bloquent pas les mêmes souvenirs.

> Suite : [La mémoire d'un agent : définitions](<15b-Memoire-Definitions-Fondamentaux.md>) — étape 15 bis.

## Squelette algorithmique

Ce fichier ajoute deux idées à la recherche par cosinus : sur la sphère unité, cosinus et distance euclidienne donnent le même classement, et un souvenir doit perdre du poids avec son âge. L'algorithme qui en découle note chaque souvenir par sa similarité, multipliée par un facteur de récence.

```text
ALGORITHME RappelerAvecRécence
ENTRÉES : vecteur q de la question, souvenirs (vecteur v, âge en jours), demi-vie h, k
SORTIE  : les k souvenirs les mieux notés

  q ← q / ‖q‖
  POUR CHAQUE souvenir (v, âge) FAIRE
      v ← v / ‖v‖
      sim ← q · v                                  (égal au cosinus, et à 1 − ‖q − v‖² / 2)
      récence ← 0,5^(âge / h)                      (vaut 1/2 quand l'âge égale la demi-vie)
      score ← sim × récence
  FIN POUR
  RETOURNER les k plus grands scores

ALGORITHME ConcentrationDesAngles (expérience du fichier)
ENTRÉES : dimension d, nombre de paires N
  POUR i DE 1 À N FAIRE
      tirer deux vecteurs aléatoires de dimension d ; mesurer leur cosinus
  FIN POUR
  RETOURNER la moyenne et l'écart-type des cosinus     (l'écart-type décroît comme 1/√d)
```

**Complexité.** Le rappel coûte O(n × d) pour n souvenirs de dimension d, plus O(n log k) pour garder les k meilleurs. L'expérience de concentration coûte O(N × d) tirages et produits. La mémoire est O(n × d) pour les vecteurs. L'expérience explique un piège pratique : en grande dimension, des vecteurs sans rapport ont des cosinus tous proches de 0 et très resserrés, si bien que de petites différences de score deviennent significatives.

**Du squelette au code.** `dot`, `norme`, `cosinus` et `normaliser` sont les briques de la première boucle, `distance_carree` et `demonstration_sphere_unite` vérifient l'égalité entre cosinus et distance sur la sphère unité, `concentration_des_angles` est la seconde expérience, et `score_memoire` combine similarité et demi-vie comme dans la troisième ligne de la boucle.

