# Étape 28 bis — Similarité cosinus et métriques de classement en RAG — Théorèmes et démonstrations

> Étape 28 bis du parcours · Précédent : [NDCG](<28-RAG-Formule-NDCG.md>) · Suite : [Exemples de RAG](<29-RAG-Exemples-Cas-Usage.md>)

**Ce que contient ce fichier :** le cosinus (pourquoi il mesure un angle, pourquoi il reste entre −1 et 1, pourquoi il classe comme la distance euclidienne sur des vecteurs normalisés), puis les métriques qui jugent un classement (Recall@k, Precision@k, MRR) et le score hybride qui mélange sens et mots. Chaque formule a son rôle, ses symboles définis un par un, un théorème démontré, un calcul à la main et un programme qui vérifie le calcul.

---

## 0. Notations communes

Ces symboles reviennent dans tout le fichier.

$$
\mathbf{a},\ \mathbf{b} \in \mathbb{R}^n
$$

**a, b** : deux vecteurs d'embedding. En gras, parce que ce sont des vecteurs (des listes de nombres), pas des nombres. En RAG, l'un est la question encodée, l'autre un chunk de document encodé.

$$
\mathbb{R}^n
$$

**ℝⁿ** : l'espace des listes de n nombres réels. n est la dimension de l'embedding (384, 768, 1536, 3072 selon le modèle).

$$
a_i
$$

**aᵢ** : la i-ème coordonnée du vecteur a. L'indice i va de 1 à n.

$$
\sum_{i=1}^{n}
$$

**Σ (sigma majuscule)** : « somme pour i allant de 1 à n ». On additionne le terme écrit à droite pour chaque valeur de i.

$$
\theta
$$

**θ (thêta)** : l'angle entre les deux vecteurs, vus comme des flèches partant de l'origine. 0° : même direction. 90° : aucun rapport. 180° : sens opposés.

---

## 1. Le produit scalaire

### Rôle

C'est la brique de base de tout le RAG et de l'attention (étape 32 bis). Il mesure à quel point deux vecteurs « vont dans le même sens », mais il est gonflé par leur longueur. Le cosinus corrigera ce défaut.

### Formule

$$
\mathbf{a} \cdot \mathbf{b} = \sum_{i=1}^{n} a_i \, b_i = a_1 b_1 + a_2 b_2 + \dots + a_n b_n
$$

### Définition de chaque élément

$$
\mathbf{a} \cdot \mathbf{b}
$$

**a · b** : le produit scalaire. Le résultat est un seul nombre, pas un vecteur.

$$
a_i \, b_i
$$

**aᵢ bᵢ** : le produit des coordonnées de même rang. Il est positif quand les deux coordonnées ont le même signe (les deux vecteurs « tirent » dans la même direction sur cet axe), négatif sinon.

### La norme

$$
\lVert \mathbf{a} \rVert = \sqrt{\mathbf{a} \cdot \mathbf{a}} = \sqrt{\sum_{i=1}^{n} a_i^2}
$$

**‖a‖** : la norme (ou longueur) euclidienne du vecteur. C'est le théorème de Pythagore généralisé à n dimensions. Elle est toujours ≥ 0, et nulle seulement pour le vecteur nul.

$$
a_i^2
$$

**aᵢ²** : le carré de la coordonnée. Il efface le signe : une coordonnée négative allonge le vecteur autant qu'une positive.

---

## 2. Théorème — Le produit scalaire mesure un angle

### Énoncé

$$
\mathbf{a} \cdot \mathbf{b} = \lVert \mathbf{a} \rVert \, \lVert \mathbf{b} \rVert \cos\theta
$$

### Rôle

Ce théorème relie la formule algébrique (une somme de produits) à une idée géométrique (un angle). C'est lui qui justifie le nom « similarité cosinus ».

### Démonstration (par la loi des cosinus, dite d'Al-Kashi)

Dans le triangle formé par les flèches **a**, **b** et le segment qui joint leurs pointes, ce segment vaut **a − b**. La loi des cosinus (Pythagore corrigé pour un angle quelconque) dit :

$$
\lVert \mathbf{a} - \mathbf{b} \rVert^2 = \lVert \mathbf{a} \rVert^2 + \lVert \mathbf{b} \rVert^2 - 2 \lVert \mathbf{a} \rVert \lVert \mathbf{b} \rVert \cos\theta
$$

On développe maintenant le membre de gauche avec la définition algébrique :

$$
\lVert \mathbf{a} - \mathbf{b} \rVert^2 = \sum_{i=1}^{n} (a_i - b_i)^2 = \sum_{i=1}^{n} a_i^2 - 2\sum_{i=1}^{n} a_i b_i + \sum_{i=1}^{n} b_i^2 = \lVert \mathbf{a} \rVert^2 - 2\,\mathbf{a}\cdot\mathbf{b} + \lVert \mathbf{b} \rVert^2
$$

On égale les deux expressions. Les termes ‖a‖² et ‖b‖² s'annulent des deux côtés :

$$
-2\,\mathbf{a}\cdot\mathbf{b} = -2 \lVert \mathbf{a} \rVert \lVert \mathbf{b} \rVert \cos\theta
$$

On divise par −2 et on obtient l'énoncé. ∎

---

## 3. La similarité cosinus

### Rôle

Dans un RAG, on encode la question et chaque chunk, puis on garde les k chunks les plus proches. Le cosinus est la mesure de proximité par défaut : il ne regarde que la direction, donc un chunk long (vecteur plus « grand » chez certains modèles) n'est pas favorisé par sa seule longueur.

### Formule

On isole cos θ dans le théorème précédent :

$$
\cos(\mathbf{a}, \mathbf{b}) = \cos\theta = \frac{\mathbf{a} \cdot \mathbf{b}}{\lVert \mathbf{a} \rVert \, \lVert \mathbf{b} \rVert} = \frac{\displaystyle\sum_{i=1}^{n} a_i b_i}{\sqrt{\displaystyle\sum_{i=1}^{n} a_i^2} \cdot \sqrt{\displaystyle\sum_{i=1}^{n} b_i^2}}
$$

### Définition de chaque élément

$$
\cos(\mathbf{a}, \mathbf{b})
$$

**cos(a, b)** : la similarité cosinus. Un nombre entre −1 et 1 (théorème 4). 1 : même direction. 0 : orthogonaux, aucun lien sémantique. −1 : directions opposées.

$$
\lVert \mathbf{a} \rVert \, \lVert \mathbf{b} \rVert
$$

**Le dénominateur** : le produit des longueurs. Diviser par lui « retire » la longueur et ne laisse que l'angle.

$$
\lVert \mathbf{a} \rVert = 0 \ \text{ou} \ \lVert \mathbf{b} \rVert = 0
$$

**Cas interdit** : un vecteur nul n'a pas de direction. Le cosinus n'est pas défini. Le code doit le traiter à part (renvoyer 0 ou lever une erreur).

---

## 4. Théorème — Inégalité de Cauchy–Schwarz : le cosinus est borné

### Énoncé

$$
\lvert \mathbf{a} \cdot \mathbf{b} \rvert \le \lVert \mathbf{a} \rVert \, \lVert \mathbf{b} \rVert
\qquad\Longrightarrow\qquad
-1 \le \cos(\mathbf{a}, \mathbf{b}) \le 1
$$

**|x| (valeur absolue)** : x sans son signe.

### Rôle

Sans ce théorème, rien ne garantit qu'un seuil comme « cos ≥ 0,8 » ait un sens. Il garantit aussi que la formule d'Answer Relevancy (étape 64 bis), une moyenne de cosinus, reste entre −1 et 1.

### Démonstration (par le discriminant)

Si **b** est nul, les deux membres valent 0 et l'inégalité est vraie. Sinon, on prend un nombre réel quelconque, noté t, et on regarde la longueur au carré du vecteur **a** − t**b**. Une longueur au carré n'est jamais négative :

$$
P(t) = \lVert \mathbf{a} - t\,\mathbf{b} \rVert^2 \ge 0 \quad \text{pour tout } t \in \mathbb{R}
$$

**t** : un nombre réel libre. On ne le choisit pas, on exige que l'inégalité tienne pour tous les t.

**P(t)** : un polynôme en t. On le développe comme dans la démonstration du §2 :

$$
P(t) = \lVert \mathbf{b} \rVert^2\, t^2 - 2\,(\mathbf{a}\cdot\mathbf{b})\, t + \lVert \mathbf{a} \rVert^2
$$

C'est un trinôme du second degré de la forme A t² + B t + C, avec :

$$
A = \lVert \mathbf{b} \rVert^2 > 0, \qquad B = -2\,(\mathbf{a}\cdot\mathbf{b}), \qquad C = \lVert \mathbf{a} \rVert^2
$$

Un trinôme avec A > 0 qui ne devient jamais négatif a au plus une racine. Son discriminant Δ (delta majuscule) est donc négatif ou nul :

$$
\Delta = B^2 - 4AC = 4\,(\mathbf{a}\cdot\mathbf{b})^2 - 4\,\lVert \mathbf{a} \rVert^2 \lVert \mathbf{b} \rVert^2 \le 0
$$

**Δ (delta)** : le discriminant. Positif : deux racines, le polynôme passe sous zéro entre elles. Nul : une racine double. Négatif : aucune racine.

On divise par 4 et on prend la racine carrée (les deux membres sont positifs) :

$$
(\mathbf{a}\cdot\mathbf{b})^2 \le \lVert \mathbf{a} \rVert^2 \lVert \mathbf{b} \rVert^2 \quad\Longrightarrow\quad \lvert \mathbf{a}\cdot\mathbf{b} \rvert \le \lVert \mathbf{a} \rVert \lVert \mathbf{b} \rVert
$$

On divise enfin par ‖a‖ ‖b‖ > 0 et on obtient −1 ≤ cos ≤ 1. ∎

### Cas d'égalité

L'égalité |cos| = 1 a lieu quand Δ = 0, c'est-à-dire quand il existe un t tel que **a** = t**b** : les vecteurs sont colinéaires. En RAG, un cosinus de 1 signifie « même direction », pas forcément « même texte ».

---

## 5. Théorème — Le cosinus ignore la longueur

### Énoncé

$$
\cos(\lambda\,\mathbf{a},\ \mu\,\mathbf{b}) = \cos(\mathbf{a}, \mathbf{b}) \qquad \text{pour tous } \lambda > 0,\ \mu > 0
$$

**λ (lambda), μ (mu)** : deux nombres strictement positifs qui étirent ou rétrécissent chaque vecteur.

### Rôle

C'est la raison pour laquelle on préfère le cosinus au produit scalaire brut : un document dont l'embedding est deux fois plus long ne gagne aucun point.

### Démonstration

Le produit scalaire et la norme sont linéaires par rapport à chaque facteur positif :

$$
(\lambda\mathbf{a})\cdot(\mu\mathbf{b}) = \lambda\mu\,(\mathbf{a}\cdot\mathbf{b}), \qquad \lVert \lambda\mathbf{a} \rVert = \lambda\lVert \mathbf{a} \rVert, \qquad \lVert \mu\mathbf{b} \rVert = \mu\lVert \mathbf{b} \rVert
$$

Donc :

$$
\cos(\lambda\mathbf{a}, \mu\mathbf{b}) = \frac{\lambda\mu\,(\mathbf{a}\cdot\mathbf{b})}{\lambda\lVert \mathbf{a} \rVert \cdot \mu\lVert \mathbf{b} \rVert} = \frac{\mathbf{a}\cdot\mathbf{b}}{\lVert \mathbf{a} \rVert\lVert \mathbf{b} \rVert}
$$

Le facteur λμ se simplifie. ∎ (Si λ < 0, le signe du cosinus s'inverse : retourner un vecteur retourne l'angle.)

---

## 6. Théorème — Sur des vecteurs normalisés, cosinus et distance euclidienne donnent le même classement

### Énoncé

Si les deux vecteurs sont de longueur 1 :

$$
\lVert \mathbf{a} \rVert = \lVert \mathbf{b} \rVert = 1 \quad\Longrightarrow\quad \lVert \mathbf{a} - \mathbf{b} \rVert^2 = 2 - 2\cos(\mathbf{a}, \mathbf{b}) \quad \text{et} \quad \cos(\mathbf{a}, \mathbf{b}) = \mathbf{a}\cdot\mathbf{b}
$$

**‖a − b‖** : la distance euclidienne, la longueur du segment entre les deux pointes.

### Rôle

Les bases vectorielles (FAISS, pgvector, Qdrant) proposent souvent trois métriques : produit scalaire, cosinus, L2. Ce théorème dit que, si on normalise les embeddings à l'indexation, les trois rendent **le même top-k**. On peut donc choisir la plus rapide (le produit scalaire) sans changer les résultats.

### Démonstration

On reprend le développement du §2 et on remplace les normes par 1 :

$$
\lVert \mathbf{a} - \mathbf{b} \rVert^2 = \lVert \mathbf{a} \rVert^2 - 2\,\mathbf{a}\cdot\mathbf{b} + \lVert \mathbf{b} \rVert^2 = 1 - 2\,\mathbf{a}\cdot\mathbf{b} + 1 = 2 - 2\,\mathbf{a}\cdot\mathbf{b}
$$

Et le dénominateur du cosinus vaut 1 × 1 = 1, donc cos = a · b. Ainsi :

$$
\lVert \mathbf{a} - \mathbf{b} \rVert^2 = 2 - 2\cos(\mathbf{a}, \mathbf{b})
$$

La fonction x ↦ 2 − 2x est strictement décroissante, et la racine carrée est croissante. Donc trier les documents par cosinus décroissant revient exactement à les trier par distance croissante. ∎

### Normaliser un vecteur

$$
\hat{\mathbf{a}} = \frac{\mathbf{a}}{\lVert \mathbf{a} \rVert}
$$

**â (a chapeau)** : le vecteur unitaire de même direction que a. D'après le théorème 5, cos(â, b̂) = cos(a, b).

---

## 7. Démonstrations numériques

### Exemple 1 — vecteurs 3D

$$
\mathbf{q} = [0{,}8;\ 0{,}3;\ 0{,}5], \qquad \mathbf{d} = [0{,}7;\ 0{,}4;\ 0{,}6]
$$

**q** : l'embedding de la question. **d** : l'embedding d'un chunk.

Produit scalaire :

$$
\mathbf{q}\cdot\mathbf{d} = 0{,}8\times0{,}7 + 0{,}3\times0{,}4 + 0{,}5\times0{,}6 = 0{,}56 + 0{,}12 + 0{,}30 = 0{,}98
$$

Normes :

$$
\lVert \mathbf{q} \rVert = \sqrt{0{,}64 + 0{,}09 + 0{,}25} = \sqrt{0{,}98} \approx 0{,}98995
$$

$$
\lVert \mathbf{d} \rVert = \sqrt{0{,}49 + 0{,}16 + 0{,}36} = \sqrt{1{,}01} \approx 1{,}00499
$$

Cosinus :

$$
\cos(\mathbf{q}, \mathbf{d}) = \frac{0{,}98}{0{,}98995 \times 1{,}00499} = \frac{0{,}98}{0{,}99489} \approx 0{,}98504
$$

Vérification du théorème 6 sur ces vecteurs une fois normalisés :

$$
\lVert \hat{\mathbf{q}} - \hat{\mathbf{d}} \rVert^2 = 2 - 2 \times 0{,}98504 \approx 0{,}02993
$$

### Exemple 2 — vecteurs 4D

$$
\mathbf{q} = [0{,}6;\ 0{,}2;\ 0{,}8;\ 0{,}1], \qquad \mathbf{d} = [0{,}5;\ 0{,}3;\ 0{,}7;\ 0{,}2]
$$

$$
\mathbf{q}\cdot\mathbf{d} = 0{,}30 + 0{,}06 + 0{,}56 + 0{,}02 = 0{,}94
$$

$$
\lVert \mathbf{q} \rVert = \sqrt{0{,}36 + 0{,}04 + 0{,}64 + 0{,}01} = \sqrt{1{,}05} \approx 1{,}02470
$$

$$
\lVert \mathbf{d} \rVert = \sqrt{0{,}25 + 0{,}09 + 0{,}49 + 0{,}04} = \sqrt{0{,}87} \approx 0{,}93274
$$

$$
\cos(\mathbf{q}, \mathbf{d}) = \frac{0{,}94}{1{,}02470 \times 0{,}93274} = \frac{0{,}94}{0{,}95577} \approx 0{,}98350
$$

---

## 8. Recall@k et Precision@k

### Rôle

Le retriever renvoie une liste classée. Ces deux taux disent si le haut de la liste est bon. Recall@k répond à « ai-je tout trouvé ? », Precision@k à « ai-je ramené du bruit ? ». Le LLM ne voit que le top-k : un document utile au rang k + 1 n'existe pas pour lui.

### Formules

$$
\text{Recall@}k = \frac{\lvert R \cap T_k \rvert}{\lvert R \rvert}
\qquad\qquad
\text{Precision@}k = \frac{\lvert R \cap T_k \rvert}{k}
$$

### Définition de chaque élément

$$
R
$$

**R** : l'ensemble des documents réellement pertinents pour la question (la vérité terrain, annotée à la main ou par un juge).

$$
T_k
$$

**Tₖ** : l'ensemble des k premiers documents renvoyés par le retriever (le top-k).

$$
k \in \mathbb{N}^*
$$

**k** : le nombre de documents qu'on garde. ℕ* désigne les entiers strictement positifs (1, 2, 3…).

$$
R \cap T_k
$$

**∩ (intersection)** : les documents qui sont à la fois pertinents et dans le top-k. Ce sont les « touchés ».

$$
\lvert X \rvert
$$

**|X| (cardinal)** : le nombre d'éléments de l'ensemble X. Mêmes barres que la valeur absolue, mais appliquées à un ensemble.

### Théorème — Bornes, monotonie et lien entre les deux taux

**(a) Bornes.**

$$
0 \le \text{Recall@}k \le 1, \qquad 0 \le \text{Precision@}k \le \min\!\left(1,\ \frac{\lvert R \rvert}{k}\right)
$$

**(b) Le rappel ne baisse jamais quand k augmente.**

$$
k \le k' \ \Longrightarrow\ \text{Recall@}k \le \text{Recall@}k'
$$

**(c) Les deux taux comptent les mêmes touchés.**

$$
k \cdot \text{Precision@}k = \lvert R \rvert \cdot \text{Recall@}k = \lvert R \cap T_k \rvert
$$

### Démonstration

(a) Une intersection est contenue dans chacun des deux ensembles, donc |R ∩ Tₖ| ≤ |R| et |R ∩ Tₖ| ≤ |Tₖ| = k. En divisant la première par |R|, on obtient Recall@k ≤ 1. En divisant les deux par k, on obtient Precision@k ≤ 1 et Precision@k ≤ |R| / k. Les deux taux sont des quotients de nombres positifs, donc ≥ 0.

Conséquence pratique : avec 2 documents pertinents et k = 5, Precision@5 ne peut pas dépasser 0,4, même avec un retriever parfait. On ne compare donc des Precision@k qu'à |R| égal.

(b) Si k ≤ k′, le top-k est le début du top-k′, donc Tₖ ⊆ Tₖ′ (⊆ : « est inclus dans »). Alors R ∩ Tₖ ⊆ R ∩ Tₖ′, donc |R ∩ Tₖ| ≤ |R ∩ Tₖ′|. On divise par |R|, qui ne dépend pas de k.

La précision, elle, n'est pas monotone : son dénominateur k grandit, son numérateur pas toujours.

(c) On multiplie chaque définition par son dénominateur. ∎

### Exemple

Le retriever renvoie [docA, docB, docC, docD]. Les pertinents sont R = {docB, docE}. Avec k = 3, T₃ = {docA, docB, docC}, donc R ∩ T₃ = {docB}.

$$
\text{Recall@}3 = \frac{1}{2} = 0{,}5 \qquad\qquad \text{Precision@}3 = \frac{1}{3} \approx 0{,}333
$$

Vérification de (c) : 3 × 1/3 = 2 × 1/2 = 1 touché. docE n'est jamais retrouvé : aucun k ≤ 4 ne fait monter le rappel au-dessus de 0,5.

---

## 9. MRR (Mean Reciprocal Rank)

### Rôle

Pour une question qui n'a besoin que d'un seul bon document (un numéro de clause, une fiche produit), seul compte le rang du premier pertinent. Le MRR résume ce rang sur un jeu de questions.

### Formule

$$
\text{MRR} = \frac{1}{\lvert Q \rvert} \sum_{i=1}^{\lvert Q \rvert} \frac{1}{\text{rang}_i}
$$

### Définition de chaque élément

$$
Q
$$

**Q** : l'ensemble des questions de test. |Q| est leur nombre.

$$
\text{rang}_i
$$

**rangᵢ** : la position (1, 2, 3…) du premier document pertinent pour la question i. Si aucun pertinent n'est renvoyé, on pose 1/rangᵢ = 0.

$$
\frac{1}{\text{rang}_i}
$$

**Rang réciproque (RR)** : 1 au rang 1, 0,5 au rang 2, 0,2 au rang 5. La pénalité est forte dès le rang 2, puis s'aplatit.

### Théorème — Bornes et sens du MRR

$$
0 \le \text{MRR} \le 1, \qquad \text{MRR} = 1 \iff \text{rang}_i = 1 \ \text{pour toute question } i
$$

### Démonstration

Chaque terme 1/rangᵢ est dans [0, 1], car rangᵢ ≥ 1 (ou le terme vaut 0). La moyenne de nombres compris entre 0 et 1 est entre 0 et 1. Une moyenne de nombres ≤ 1 vaut 1 seulement si chaque nombre vaut 1, c'est-à-dire si chaque rang vaut 1. ∎

Remarque : l'inverse du MRR n'est **pas** le rang moyen. C'est la moyenne harmonique des rangs (sur les questions où un pertinent a été trouvé). La moyenne harmonique est tirée vers les petits rangs : un seul échec au rang 50 abîme peu le MRR, alors qu'il ferait exploser un rang moyen.

### Exemple

Trois questions, premiers pertinents aux rangs 2, 1 et 5 :

$$
\text{MRR} = \frac{1}{3}\left(\frac{1}{2} + \frac{1}{1} + \frac{1}{5}\right) = \frac{0{,}5 + 1 + 0{,}2}{3} = \frac{1{,}7}{3} \approx 0{,}5667
$$

---

## 10. Score hybride

### Rôle

Le cosinus capte le sens (« congé maternité » ≈ « parental leave »). BM25 capte les mots exacts (« article L1225-17 », un identifiant de contrat). Le score hybride les additionne avec un poids pour ne rater ni l'un ni l'autre.

### Formules

$$
s(d) = \alpha \cdot \cos(\mathbf{q}, \mathbf{d}) + (1 - \alpha) \cdot \widetilde{\text{BM25}}(q, d)
$$

$$
\widetilde{\text{BM25}}(q, d) = \frac{\text{BM25}(q, d) - \min_{d'} \text{BM25}(q, d')}{\max_{d'} \text{BM25}(q, d') - \min_{d'} \text{BM25}(q, d')}
$$

### Définition de chaque élément

$$
s(d)
$$

**s(d)** : le score final du document d. On trie les candidats par s décroissant.

$$
\alpha \in [0, 1]
$$

**α (alpha)** : le poids du sens. α = 1 : recherche purement vectorielle. α = 0 : recherche purement lexicale. Valeur courante : 0,5 à 0,7, réglée sur un jeu de test avec Recall@k.

$$
1 - \alpha
$$

**1 − α** : le poids des mots exacts. Les deux poids somment à 1.

$$
\text{BM25}(q, d)
$$

**BM25(q, d)** : le score lexical brut (voir `05-RAG/22-RAG-Formule-BM25.md`). Il n'a pas de plafond : 4, 12 ou 30 selon la longueur de la requête.

$$
\widetilde{\text{BM25}}
$$

**BM25 tilde** : le BM25 ramené entre 0 et 1 par normalisation min-max sur les candidats de cette requête.

$$
\min_{d'},\ \max_{d'}
$$

**min et max sur d′** : la plus petite et la plus grande valeur parmi tous les candidats d′ de la même requête. d′ (d prime) est une variable qui parcourt les candidats.

### Théorème — Le score hybride est une moyenne pondérée, donc borné

Si les deux scores sont dans [0, 1] :

$$
\min\!\big(c,\ b\big) \le \alpha\,c + (1-\alpha)\,b \le \max\!\big(c,\ b\big)
$$

**c** : le cosinus du document. **b** : son BM25 normalisé.

### Démonstration

Posons m = min(c, b) et M = max(c, b). Comme α ≥ 0 et 1 − α ≥ 0, on peut minorer chaque terme sans changer le sens de l'inégalité :

$$
\alpha\,c + (1-\alpha)\,b \ \ge\ \alpha\,m + (1-\alpha)\,m = m
$$

De même avec M pour la majoration. Comme m ≥ 0 et M ≤ 1, le score reste dans [0, 1]. ∎

**Pourquoi normaliser d'abord.** Sans normalisation, avec c ≤ 1 et BM25 = 12, le second terme écrase le premier pour tout α < 0,9 : le réglage de α ne veut plus rien dire. C'est aussi la raison d'être de RRF (`05-RAG/24-RAG-Formule-RRF.md`), qui fusionne des rangs au lieu de scores.

### Exemple — α change le gagnant

Trois documents. BM25 bruts : 4,1 ; 12,3 ; 7,0. Min = 4,1, max = 12,3, écart = 8,2.

$$
\widetilde{\text{BM25}}(D_1) = \frac{4{,}1 - 4{,}1}{8{,}2} = 0, \qquad \widetilde{\text{BM25}}(D_2) = \frac{12{,}3 - 4{,}1}{8{,}2} = 1, \qquad \widetilde{\text{BM25}}(D_3) = \frac{7{,}0 - 4{,}1}{8{,}2} \approx 0{,}3537
$$

Cosinus : D₁ = 0,82 ; D₂ = 0,60 ; D₃ = 0,75. Avec α = 0,7 :

$$
s(D_1) = 0{,}7 \times 0{,}82 + 0{,}3 \times 0 = 0{,}574
$$

$$
s(D_2) = 0{,}7 \times 0{,}60 + 0{,}3 \times 1 = 0{,}720
$$

$$
s(D_3) = 0{,}7 \times 0{,}75 + 0{,}3 \times 0{,}3537 \approx 0{,}6311
$$

Classement hybride : D₂, D₃, D₁. Avec α = 1 (vectoriel seul), le classement serait D₁, D₃, D₂. Le document qui contient le mot exact passe de la dernière à la première place.

---

## 11. Code — tout vérifier

Bibliothèque standard uniquement. Chaque `assert` reprend un nombre calculé à la main plus haut.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`dot(a, b)`** — On peut l'imaginer comme un comptable qui aligne deux colonnes de chiffres ligne à ligne et additionne les produits de chaque paire : la fonction reçoit deux vecteurs, lève `ValueError` si leurs dimensions diffèrent, puis renvoie la somme des produits de leurs coordonnées de même rang, ce qui est exactement la définition du produit scalaire du paragraphe 1. Pour q = [0,8 ; 0,3 ; 0,5] et d = [0,7 ; 0,4 ; 0,6], elle donne 0,98, et pour les vecteurs de dimension 4 de l'exemple 2, 0,94 ; toutes les autres fonctions géométriques du programme passent par elle.

**`norm(a)`** — Cette fonction mesure la longueur d'une flèche en la comparant à elle-même, comme un arpenteur qui reporterait sa chaîne le long de son propre tracé : elle reçoit un vecteur, demande à `dot` son produit scalaire avec lui-même, c'est-à-dire la somme des carrés de ses coordonnées, et renvoie la racine carrée de ce nombre. Elle évite ainsi d'écrire une seconde fois la somme des carrés ; pour q, elle rend environ 0,98995, et pour d, environ 1,00499, les deux normes dont le produit sert de dénominateur au cosinus de l'exemple 1.

**`cosine_similarity(a, b)`** — C'est la boussole qui compare la direction de deux flèches sans se soucier de leur longueur : la fonction reçoit deux vecteurs, calcule leurs normes avec `norm`, lève `ValueError` si l'une est nulle, puisque le cosinus n'est alors pas défini, puis renvoie le produit scalaire divisé par le produit des normes. Elle donne 0,98504 en dimension 3 et 0,98350 en dimension 4, et le programme s'en sert aussi pour vérifier le théorème 5, en constatant qu'étirer q par 3 et d par 0,5 ne change rien au résultat.

**`normalize(a)`** — Cette fonction joue le tailleur qui ramène chaque flèche à la longueur 1 sans toucher à sa direction : elle reçoit un vecteur, calcule sa norme avec `norm` et renvoie la liste de ses coordonnées divisées par cette norme, c'est-à-dire le vecteur unitaire â du théorème 6. Elle ne contrôle pas le vecteur nul, qui provoquerait ici une division par zéro ; dans le programme, elle ne sert pas au classement mais à vérifier que, sur des vecteurs normalisés, le produit scalaire redonne le cosinus et que la distance au carré vaut 2 − 2 cos.

**`euclidean_sq(a, b)`** — C'est la corde d'arpenteur tendue entre deux points, dont on note la longueur au carré sans prendre la racine : la fonction reçoit deux vecteurs et renvoie la somme des carrés des écarts entre leurs coordonnées de même rang, sans vérifier leurs dimensions. Appliquée aux versions normalisées de q et d, elle donne environ 0,02993, et le programme vérifie que ce nombre égale 2 − 2 cos(q, d), aux arrondis près, ce qui prouve sur un cas concret l'égalité ‖â − b̂‖² = 2 − 2 cos(a, b) du théorème 6.

**`recall_at_k(retrieved, relevant, k)`** — Elle pose la question du chercheur de trésor qui fouille les k premiers coffres : quelle part des trésors connus a-t-il trouvée ? La fonction reçoit la liste ordonnée des documents retrouvés, l'ensemble des pertinents et k, lève `ValueError` s'il n'y a aucun pertinent, car le rappel n'a alors pas de dénominateur, puis transforme les k premiers résultats en ensemble, compte ceux qui sont pertinents et divise par le nombre de pertinents. Sur docA à docD avec les pertinents docB et docE, elle renvoie 0,5 à k = 3, et le programme vérifie qu'elle ne baisse jamais quand k augmente.

**`precision_at_k(retrieved, relevant, k)`** — Cette fonction regarde la même fouille du point de vue opposé : parmi les k coffres ouverts, combien contenaient vraiment un trésor ? Elle reçoit les mêmes arguments, lève `ValueError` si k est nul ou négatif, puis compte les pertinents parmi les k premiers résultats et divise ce nombre par k, et non par le nombre de pertinents. Sur l'exemple, elle renvoie 1/3 à k = 3, soit 0,333 à l'affichage, et le programme vérifie pour k de 1 à 4 que k fois la précision égale toujours le nombre de pertinents fois le rappel, puisque les deux comptent les mêmes documents touchés.

**`mrr(first_relevant_ranks)`** — Elle note la patience demandée à l'utilisateur, question après question, comme un professeur qui donnerait 1 à qui trouve du premier coup, 1/2 au second essai, et ainsi de suite : la fonction reçoit la liste des rangs du premier document pertinent de chaque question, comptés à partir de 1, convertit chaque rang positif en son inverse et chaque rang 0, qui code une question sans pertinent trouvé, en 0, puis renvoie la moyenne. Pour les rangs 2, 1 et 5, elle donne 1,7 / 3, soit 0,5667, et pour trois rangs égaux à 1, exactement 1.

**`min_max(scores)`** — Cette fonction est le traducteur qui ramène les scores BM25, exprimés dans une monnaie sans plafond, sur la même échelle de 0 à 1 que les cosinus : elle reçoit une liste de scores, repère le minimum et le maximum, renvoie des zéros si tous les scores sont égaux, puisqu'un signal plat ne départage personne, et sinon renvoie pour chaque score sa position relative (s − min) / (max − min). Sur les BM25 bruts 4,1, 12,3 et 7,0, elle donne 0, 1 et environ 0,3537, les valeurs calculées à la main au paragraphe 10.

**`hybrid_scores(cosines, bm25_raw, alpha)`** — C'est le chef qui marie deux ingrédients selon un dosage fixé d'avance : la fonction reçoit la liste des cosinus, celle des BM25 bruts et le poids α, lève `ValueError` si α sort de [0, 1], normalise les BM25 avec `min_max`, puis renvoie, document par document, α × cosinus + (1 − α) × BM25 normalisé. Avec α = 0,7, elle produit 0,574, 0,720 et environ 0,6311 pour D₁, D₂ et D₃, si bien que le classement hybride devient D₂, D₃, D₁ alors que le cosinus seul aurait donné D₁, D₃, D₂ : le document qui contient le mot exact passe de la dernière à la première place.

**`main()`** — Le chef d'orchestre reprend, dans l'ordre du chapitre, chaque nombre calculé à la main : le produit scalaire 0,98, les normes et le cosinus 0,98504 de l'exemple en dimension 3, l'inégalité de Cauchy-Schwarz, l'invariance par étirement positif et l'égalité entre distance et cosinus sur les vecteurs normalisés, puis le cosinus 0,98350 en dimension 4. Il vérifie ensuite le Recall@3 de 0,5 et la Precision@3 de 1/3, la monotonie du rappel et l'identité entre précision et rappel, le MRR de 0,5667, les trois scores hybrides et l'inversion du classement entre score vectoriel et score hybride. Il n'imprime les résultats qu'une fois tous les `assert` passés, puis termine par la ligne de succès.

```python
import math


def dot(a, b):
    if len(a) != len(b):
        raise ValueError("Les vecteurs doivent avoir la même dimension")
    return sum(x * y for x, y in zip(a, b))


def norm(a):
    return math.sqrt(dot(a, a))


def cosine_similarity(a, b):
    na, nb = norm(a), norm(b)
    if na == 0 or nb == 0:
        raise ValueError("Cosinus non défini pour un vecteur nul")
    return dot(a, b) / (na * nb)


def normalize(a):
    n = norm(a)
    return [x / n for x in a]


def euclidean_sq(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def recall_at_k(retrieved, relevant, k):
    if not relevant:
        raise ValueError("Recall@k non défini sans document pertinent")
    return len(set(retrieved[:k]) & relevant) / len(relevant)


def precision_at_k(retrieved, relevant, k):
    if k <= 0:
        raise ValueError("k doit être >= 1")
    return len(set(retrieved[:k]) & relevant) / k


def mrr(first_relevant_ranks):
    """Rangs commençant à 1. 0 = aucun pertinent trouvé (RR = 0)."""
    rr = [1.0 / r if r > 0 else 0.0 for r in first_relevant_ranks]
    return sum(rr) / len(rr)


def min_max(scores):
    lo, hi = min(scores), max(scores)
    if hi == lo:
        return [0.0 for _ in scores]
    return [(s - lo) / (hi - lo) for s in scores]


def hybrid_scores(cosines, bm25_raw, alpha):
    if not 0 <= alpha <= 1:
        raise ValueError("alpha doit être dans [0, 1]")
    bm25_n = min_max(bm25_raw)
    return [alpha * c + (1 - alpha) * b for c, b in zip(cosines, bm25_n)]


def main() -> None:
    # §7 Exemple 1 — 3D
    q, d = [0.8, 0.3, 0.5], [0.7, 0.4, 0.6]
    assert math.isclose(dot(q, d), 0.98)
    assert math.isclose(norm(q), 0.98995, abs_tol=1e-5)
    assert math.isclose(norm(d), 1.00499, abs_tol=1e-5)
    assert math.isclose(cosine_similarity(q, d), 0.98504, abs_tol=1e-5)

    # Théorème 4 — Cauchy–Schwarz
    assert abs(dot(q, d)) <= norm(q) * norm(d)

    # Théorème 5 — invariance par étirement positif
    assert math.isclose(cosine_similarity([3 * x for x in q], [0.5 * x for x in d]),
                        cosine_similarity(q, d))

    # Théorème 6 — vecteurs normalisés
    qh, dh = normalize(q), normalize(d)
    assert math.isclose(euclidean_sq(qh, dh), 2 - 2 * cosine_similarity(q, d))
    assert math.isclose(dot(qh, dh), cosine_similarity(q, d))
    assert math.isclose(euclidean_sq(qh, dh), 0.02993, abs_tol=1e-5)

    # §7 Exemple 2 — 4D
    q2, d2 = [0.6, 0.2, 0.8, 0.1], [0.5, 0.3, 0.7, 0.2]
    assert math.isclose(dot(q2, d2), 0.94)
    assert math.isclose(cosine_similarity(q2, d2), 0.98350, abs_tol=1e-5)

    # §8 Recall@k / Precision@k
    retrieved = ["docA", "docB", "docC", "docD"]
    relevant = {"docB", "docE"}
    assert recall_at_k(retrieved, relevant, 3) == 0.5
    assert math.isclose(precision_at_k(retrieved, relevant, 3), 1 / 3)
    # (b) monotonie du rappel
    recalls = [recall_at_k(retrieved, relevant, k) for k in range(1, 5)]
    assert all(r1 <= r2 for r1, r2 in zip(recalls, recalls[1:]))
    # (c) même nombre de touchés
    for k in range(1, 5):
        assert math.isclose(k * precision_at_k(retrieved, relevant, k),
                            len(relevant) * recall_at_k(retrieved, relevant, k))

    # §9 MRR
    assert math.isclose(mrr([2, 1, 5]), 1.7 / 3)
    assert mrr([1, 1, 1]) == 1.0

    # §10 Score hybride
    s = hybrid_scores([0.82, 0.60, 0.75], [4.1, 12.3, 7.0], alpha=0.7)
    assert math.isclose(s[0], 0.574)
    assert math.isclose(s[1], 0.720)
    assert math.isclose(s[2], 0.6311, abs_tol=1e-4)
    order_hybrid = sorted(range(3), key=lambda i: -s[i])
    order_vector = sorted(range(3), key=lambda i: -[0.82, 0.60, 0.75][i])
    assert order_hybrid == [1, 2, 0]   # D2, D3, D1
    assert order_vector == [0, 2, 1]   # D1, D3, D2

    print(f"cos 3D = {cosine_similarity(q, d):.5f}")
    print(f"cos 4D = {cosine_similarity(q2, d2):.5f}")
    print(f"Recall@3 = {recall_at_k(retrieved, relevant, 3):.3f}, Precision@3 = {precision_at_k(retrieved, relevant, 3):.3f}")
    print(f"MRR = {mrr([2, 1, 5]):.4f}")
    print("Hybride :", [round(x, 4) for x in s])
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
cos 3D = 0.98504
cos 4D = 0.98350
Recall@3 = 0.500, Precision@3 = 0.333
MRR = 0.5667
Hybride : [0.574, 0.72, 0.6311]
OK — toutes les vérifications sont passées.
```

---

### Déroulé, ligne par ligne

`dot` vérifie d'abord que les deux vecteurs ont la même dimension, puis additionne les produits des coordonnées de même rang avec `zip` : c'est la définition du produit scalaire du paragraphe 1. `norm` est la racine carrée du produit scalaire d'un vecteur avec lui-même, ce qui évite d'écrire deux fois la somme des carrés. `cosine_similarity` refuse un vecteur nul en levant une erreur, puisque le cosinus n'y est pas défini, puis divise le produit scalaire par le produit des normes. `normalize` divise chaque coordonnée par la norme, ce qui donne le vecteur unitaire â du théorème 6, et `euclidean_sq` calcule le carré de la distance euclidienne, qui sert à vérifier l'égalité ‖â − b̂‖² = 2 − 2 cos(a, b).

`recall_at_k` transforme les k premiers documents en ensemble et compte son intersection avec les pertinents, puis divise par le nombre de pertinents ; elle lève une erreur s'il n'y a aucun pertinent, car le rappel n'est alors pas défini. `precision_at_k` fait le même comptage mais divise par k. `mrr` transforme chaque rang en rang réciproque (0 si aucun pertinent n'a été trouvé, codé par un rang 0) et fait la moyenne. `min_max` ramène des scores dans [0 ; 1], avec 0 partout si tous les scores sont égaux, et `hybrid_scores` applique la combinaison convexe α × cosinus + (1 − α) × BM25 normalisé.

Le programme principal reprend, dans l'ordre du fichier, chaque nombre calculé à la main : le cosinus 0,98504 en dimension 3, Cauchy–Schwarz, l'invariance par étirement positif, l'égalité entre distance et cosinus sur les vecteurs normalisés, le cosinus 0,98350 en dimension 4, les valeurs de Recall@3 et Precision@3, la monotonie du rappel, l'identité k × P@k = |Rel| × R@k, le MRR et les trois scores hybrides, puis vérifie que le classement hybride diffère du classement vectoriel.

## Squelette algorithmique

```text
ALGORITHME ÉvaluerUnRetriever
ENTRÉES : questions avec leur vecteur, documents avec leur vecteur et leur score BM25, pertinents par question, k, α
SORTIE  : pour chaque question : classement hybride ; sur le jeu : Recall@k, Precision@k, MRR

  POUR CHAQUE question q FAIRE
      POUR CHAQUE document d FAIRE  cos(d) ← (q · d) / (‖q‖ ‖d‖)  FIN POUR
      b̃ ← MinMax(BM25 des documents)
      POUR CHAQUE document d FAIRE  s(d) ← α cos(d) + (1 − α) b̃(d)  FIN POUR
      classement ← documents triés par s décroissant
      R@k(q) ← |Rel(q) ∩ Top_k| / |Rel(q)|        P@k(q) ← |Rel(q) ∩ Top_k| / k
      rang(q) ← position du premier pertinent, ou 0
  FIN POUR
  RETOURNER moyenne des R@k, moyenne des P@k, moyenne des 1 / rang (0 si rang = 0)
```

**Complexité.** Pour Q questions, n documents de dimension d : O(Q × n × d) pour les cosinus, O(Q × n) pour les normalisations et les scores, O(Q × n log n) pour les tris, puis O(Q × k) pour les métriques. La mémoire est O(n × d) pour les vecteurs.

**Du squelette au code.** `cosine_similarity` (avec `dot` et `norm`) donne cos(d), `min_max` et `hybrid_scores` la ligne du score, `recall_at_k` et `precision_at_k` les deux métriques et `mrr` la moyenne des rangs réciproques. `normalize` et `euclidean_sq` ne servent pas au classement : ils vérifient le théorème 6.

## 12. Pièges

- **Comparer des cosinus de deux modèles d'embedding différents.** Chaque modèle a sa propre distribution : 0,75 est excellent chez l'un, banal chez l'autre. Un seuil se règle par modèle.
- **Choisir L2 dans la base vectorielle sans normaliser.** Le théorème 6 ne s'applique plus : un chunk court et un chunk long ne sont plus comparés sur la seule direction.
- **Lire une Precision@k basse comme un mauvais retriever** alors que |R| < k (théorème 8 a).
- **Mélanger cosinus et BM25 brut** dans un score hybride. Normaliser d'abord, ou passer à RRF.

## 13. Exercice feuille blanche

1. Redémontrer Cauchy–Schwarz avec le polynôme P(t) sans regarder.
2. Montrer que ‖â − b̂‖² = 2 − 2 cos(a, b) et en déduire que FAISS en produit scalaire et en L2 renvoie le même top-k sur des vecteurs normalisés.
3. Pour retrieved = [B, A, E, C] et R = {B, E}, calculer Recall@k et Precision@k pour k = 1…4, et vérifier k · P@k = 2 · R@k.
4. Dans l'exemple du §10, trouver la valeur de α à partir de laquelle D₁ repasse devant D₂.
