# Mathématiques Fondamentales des LLMs et Transformers
## Guide Complet pour Développeurs - Du Théorème à l'Implémentation

---

## Table des Matières
1. [Algèbre Linéaire](#algèbre-linéaire)
2. [Calcul Différentiel & Optimisation](#calcul-différentiel--optimisation)
3. [Probabilités & Entropie](#probabilités--entropie)
4. [Attention Mechanism](#attention-mechanism)
5. [Complexité Algorithmique](#complexité-algorithmique)
6. [Eigenvalues et Eigenvectors](#eigenvalues-et-eigenvectors)

---

# 1. ALGÈBRE LINÉAIRE

## 1.1 Multiplication de Matrices - Fondation des LLMs

### Théorème : Transformation Linéaire par Multiplication Matricielle

**Énoncé :**
Soit $A \in \mathbb{R}^{m \times n}$ et $B \in \mathbb{R}^{n \times p}$, le produit $C = A \cdot B$ est une matrice $C \in \mathbb{R}^{m \times p}$ où chaque élément $c_{ij}$ est défini par :

$$c_{ij} = \sum_{k=1}^{n} a_{ik} \cdot b_{kj}$$

**Interprétation pour les LLMs :**
Chaque couche de transformation dans un réseau de neurones (including transformers) réalise une multiplication matricielle. C'est la brique fondamentale de tous les LLMs.

### Démonstration

Considérons $A = \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}$ et $B = \begin{pmatrix} 5 & 6 \\ 7 & 8 \end{pmatrix}$

Pour $c_{11}$ (ligne 1 de A, colonne 1 de B) :
$$c_{11} = (1)(5) + (2)(7) = 5 + 14 = 19$$

Pour $c_{12}$ (ligne 1 de A, colonne 2 de B) :
$$c_{12} = (1)(6) + (2)(8) = 6 + 16 = 22$$

Pour $c_{21}$ (ligne 2 de A, colonne 1 de B) :
$$c_{21} = (3)(5) + (4)(7) = 15 + 28 = 43$$

Pour $c_{22}$ (ligne 2 de A, colonne 2 de B) :
$$c_{22} = (3)(6) + (4)(8) = 18 + 32 = 50$$

**Résultat :** $C = \begin{pmatrix} 19 & 22 \\ 43 & 50 \end{pmatrix}$

### Rôle dans les LLMs

- **Embedding**: Convertit les tokens en vecteurs numériques via $\mathbf{x}_{embedding} = W_{embed} \cdot \mathbf{x}_{token}$
- **Couches Linéaires**: Chaque neurone calcule $\mathbf{z} = W \cdot \mathbf{x} + \mathbf{b}$
- **Complexité**: Pour deux matrices $n \times n$, le coût computationnel est $O(n^3)$

### Exemple Code Java (Partie d'une couche linéaire)
```java
public class MatrixMultiplication {
    // Multiplie deux matrices A (m x n) et B (n x p) -> C (m x p)
    public static double[][] multiply(double[][] A, double[][] B) {
        int m = A.length;
        int n = A[0].length;
        int p = B[0].length;
        
        double[][] C = new double[m][p];
        
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < p; j++) {
                C[i][j] = 0;
                for (int k = 0; k < n; k++) {
                    C[i][j] += A[i][k] * B[k][j];  // Dot product
                }
            }
        }
        return C;
    }
}
```

---

## 1.2 Vecteurs et Dot Product

### Théorème : Produit Scalaire (Dot Product)

**Énoncé :**
Soit $\mathbf{u}, \mathbf{v} \in \mathbb{R}^{n}$ deux vecteurs, leur produit scalaire est :

$$\mathbf{u} \cdot \mathbf{v} = \sum_{i=1}^{n} u_i v_i = \|\mathbf{u}\| \|\mathbf{v}\| \cos(\theta)$$

où $\theta$ est l'angle entre les vecteurs.

**Interprétation :**
- Mesure la *similitude* entre deux vecteurs
- Valeur maximale quand vecteurs parallèles ($\theta = 0°$)
- Valeur minimale quand orthogonaux ($\theta = 90°$)
- Valeur nulle quand perpendiculaires

### Démonstration

Soit $\mathbf{u} = \begin{pmatrix} 1 \\ 2 \\ 3 \end{pmatrix}$ et $\mathbf{v} = \begin{pmatrix} 4 \\ 5 \\ 6 \end{pmatrix}$

$$\mathbf{u} \cdot \mathbf{v} = (1)(4) + (2)(5) + (3)(6) = 4 + 10 + 18 = 32$$

Magnitude : $\|\mathbf{u}\| = \sqrt{1^2 + 2^2 + 3^2} = \sqrt{14}$

Magnitude : $\|\mathbf{v}\| = \sqrt{4^2 + 5^2 + 6^2} = \sqrt{77}$

Cosinus angle : $\cos(\theta) = \frac{32}{\sqrt{14} \cdot \sqrt{77}} \approx 0.974$

### Rôle dans les LLMs

**Critiquement important pour l'Attention Mechanism :**
- Calcul des scores d'attention : $scores = Q \cdot K^T$ (dot products)
- Similarité sémantique entre tokens
- Base mathématique du mécanisme d'attention

---

# 2. CALCUL DIFFÉRENTIEL & OPTIMISATION

## 2.1 Dérivée Partielle et Gradient

### Théorème : Gradient d'une Fonction Multivariée

**Énoncé :**
Soit $f: \mathbb{R}^n \to \mathbb{R}$ une fonction à $n$ variables, le gradient est le vecteur :

$$\nabla f = \begin{pmatrix} \frac{\partial f}{\partial x_1} \\ \frac{\partial f}{\partial x_2} \\ \vdots \\ \frac{\partial f}{\partial x_n} \end{pmatrix}$$

Le gradient pointe dans la direction de plus forte augmentation de $f$.

### Démonstration

Soit $f(x, y) = x^2 + 3xy + 2y^2$

**Dérivée partielle par rapport à x :**
$$\frac{\partial f}{\partial x} = 2x + 3y$$

**Dérivée partielle par rapport à y :**
$$\frac{\partial f}{\partial y} = 3x + 4y$$

**Gradient :**
$$\nabla f(x,y) = \begin{pmatrix} 2x + 3y \\ 3x + 4y \end{pmatrix}$$

Au point $(1, 2)$ :
$$\nabla f(1,2) = \begin{pmatrix} 2(1) + 3(2) \\ 3(1) + 4(2) \end{pmatrix} = \begin{pmatrix} 8 \\ 11 \end{pmatrix}$$

### Rôle dans les LLMs

- Guide la mise à jour des poids : $W_{new} = W_{old} - \alpha \nabla L$
- $\nabla L$ = direction vers minimum de la loss
- $\alpha$ = taux d'apprentissage (learning rate)

---

## 2.2 Chaîne (Chain Rule) - Cœur de la Backpropagation

### Théorème : Chaîne de Dérivation

**Énoncé :**
Si $y = f(u)$ et $u = g(x)$, alors :

$$\frac{dy}{dx} = \frac{dy}{du} \cdot \frac{du}{dx}$$

Pour une chaîne longue : $z = f(y)$, $y = g(x)$, $x = h(w)$

$$\frac{dz}{dw} = \frac{dz}{dy} \cdot \frac{dy}{dx} \cdot \frac{dx}{dw}$$

### Démonstration

Composée : $z = (x^2 + 1)^3$

Posons $u = x^2 + 1$, alors $z = u^3$

$\frac{dz}{du} = 3u^2 = 3(x^2 + 1)^2$

$\frac{du}{dx} = 2x$

Par chain rule :
$$\frac{dz}{dx} = 3(x^2 + 1)^2 \cdot 2x = 6x(x^2 + 1)^2$$

Vérification en $x = 1$ :
$$\frac{dz}{dx}\bigg|_{x=1} = 6(1)(1^2 + 1)^2 = 6 \cdot 4 = 24$$

### Rôle dans les LLMs : Backpropagation

La backpropagation est une application du chain rule à travers les couches :

Pour une perte $L$ dépendant d'un poids $w_1$ via plusieurs couches :

$$\frac{\partial L}{\partial w_1} = \frac{\partial L}{\partial y} \cdot \frac{\partial y}{\partial z_2} \cdot \frac{\partial z_2}{\partial h} \cdot \frac{\partial h}{\partial z_1} \cdot \frac{\partial z_1}{\partial w_1}$$

**Chaque terme représente une transformation à travers une couche.**

---

## 2.3 Descente de Gradient (Gradient Descent)

### Théorème : Algorithme d'Optimisation Itérative

**Énoncé :**
Pour minimiser une fonction de perte $L(W)$, l'algorithme de descente de gradient met à jour les paramètres :

$$W_{t+1} = W_t - \alpha \nabla L(W_t)$$

où $\alpha$ est le taux d'apprentissage et $\nabla L$ est le gradient.

### Démonstration Graphique (1D)

Soit $L(w) = (w - 3)^2$ (minimum à $w = 3$)

$\frac{dL}{dw} = 2(w - 3)$

Itérations avec $\alpha = 0.1$, $w_0 = 0$ :

| Itération | $w_t$ | $\nabla L(w_t)$ | $w_{t+1}$ |
|-----------|-------|-----------------|-----------|
| 0 | 0 | 2(0-3) = -6 | 0 - 0.1(-6) = 0.6 |
| 1 | 0.6 | 2(0.6-3) = -4.8 | 0.6 - 0.1(-4.8) = 1.08 |
| 2 | 1.08 | 2(1.08-3) = -3.84 | 1.08 - 0.1(-3.84) = 1.464 |
| 3 | 1.464 | 2(1.464-3) = -3.072 | 1.464 - 0.1(-3.072) = 1.771 |
| ... | ... | ... | → 3 |

**Converge vers le minimum !**

### Variantes pour LLMs

1. **SGD (Stochastic Gradient Descent)** : Utilise des mini-batches
2. **Adam** : Adapte le taux d'apprentissage par paramètre
3. **RMSprop** : Normalise par les gradients historiques

---

# 3. PROBABILITÉS & ENTROPIE

## 3.1 Softmax - Conversion en Probabilités

### Théorème : Fonction Softmax

**Énoncé :**
Pour un vecteur de logits $\mathbf{z} = (z_1, z_2, ..., z_n)$, la softmax produit des probabilités :

$$\sigma(z_i) = \frac{e^{z_i}}{\sum_{j=1}^{n} e^{z_j}}$$

**Propriétés :**
- Chaque sortie : $0 < \sigma(z_i) < 1$
- Somme : $\sum_i \sigma(z_i) = 1$
- Différentiable : crucial pour la backpropagation

### Démonstration

Soit $\mathbf{z} = \begin{pmatrix} 1.0 \\ 2.0 \\ 3.0 \end{pmatrix}$

Exponentielles : $e^{1.0} \approx 2.718$, $e^{2.0} \approx 7.389$, $e^{3.0} \approx 20.086$

Somme : $S = 2.718 + 7.389 + 20.086 = 30.193$

Softmax :
$$\sigma(z_1) = \frac{2.718}{30.193} \approx 0.090$$
$$\sigma(z_2) = \frac{7.389}{30.193} \approx 0.245$$
$$\sigma(z_3) = \frac{20.086}{30.193} \approx 0.665$$

Vérification : $0.090 + 0.245 + 0.665 = 1.000$ ✓

### Rôle dans les LLMs

- **Couche de sortie** : Convertit logits en distribution de probabilité sur le vocabulaire
- **Attention mechanism** : Normalise les scores d'attention en poids
- **Décodage** : Sélection du prochain token basée sur probabilités

### Exemple Code Java
```java
public class Softmax {
    public static double[] softmax(double[] logits) {
        // Stabilité numérique : soustrait le max
        double max = java.util.Arrays.stream(logits).max().orElse(0);
        
        double[] exp = new double[logits.length];
        double sum = 0;
        
        for (int i = 0; i < logits.length; i++) {
            exp[i] = Math.exp(logits[i] - max);
            sum += exp[i];
        }
        
        double[] probs = new double[logits.length];
        for (int i = 0; i < logits.length; i++) {
            probs[i] = exp[i] / sum;
        }
        return probs;
    }
}
```

---

## 3.2 Cross-Entropy Loss - Mesure d'Erreur

### Théorème : Entropie Croisée Catégorique

**Énoncé :**
Pour une vraie distribution (one-hot encoded) $\mathbf{y}$ et prédiction $\hat{\mathbf{y}}$, la cross-entropy est :

$$L_{CE} = -\sum_{i=1}^{n} y_i \log(\hat{y}_i)$$

**Interprétation :**
- Mesure la distance entre distribution vraie et prédite
- Minimum = 0 quand prédiction parfaite ($\hat{y}_i = y_i$)
- Augmente avec la certitude d'une mauvaise prédiction

### Démonstration

Cas classique : 3 classes, vraie classe = classe 1

Vraie distribution : $\mathbf{y} = \begin{pmatrix} 1 \\ 0 \\ 0 \end{pmatrix}$ (one-hot)

Prédiction 1 (mauvaise) : $\hat{\mathbf{y}}_1 = \begin{pmatrix} 0.1 \\ 0.6 \\ 0.3 \end{pmatrix}$

$$L_{CE} = -(1 \cdot \log(0.1) + 0 \cdot \log(0.6) + 0 \cdot \log(0.3)) = -\log(0.1) \approx 2.303$$

Prédiction 2 (bonne) : $\hat{\mathbf{y}}_2 = \begin{pmatrix} 0.8 \\ 0.15 \\ 0.05 \end{pmatrix}$

$$L_{CE} = -(1 \cdot \log(0.8) + 0 + 0) = -\log(0.8) \approx 0.223$$

**La bonne prédiction a une perte bien plus faible !**

### Dérivée de Cross-Entropy pour Softmax

Résultat clé (dérivation omise) :

$$\frac{\partial L_{CE}}{\partial z_i} = \hat{y}_i - y_i$$

**Incroyablement simple ! C'est une raison pour laquelle softmax + cross-entropy est l'standard.**

### Rôle dans les LLMs

- **Fonction de perte** : Entraîne le réseau à prédire le bon token suivant
- **Optimisation** : Gradient simple guide les mises à jour
- **Généralisation** : Pénalise sévèrement les mauvaises prédictions confiantes

---

## 3.3 Théorème de Bayes - Inférence Probabiliste

### Théorème : Bayes

**Énoncé :**
$$P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)}$$

où :
- $P(A|B)$ = *Posterior* (probabilité de A sachant B)
- $P(B|A)$ = *Likelihood* (probabilité de B sachant A)
- $P(A)$ = *Prior* (probabilité a priori de A)
- $P(B)$ = *Evidence* (probabilité de B, normalisation)

### Démonstration

**Cas médical :**
- $A$ = Patient a la maladie
- $B$ = Test positif

Données :
- $P(A) = 0.01$ (1% des gens ont la maladie)
- $P(B|A) = 0.99$ (test détecte 99% des malades)
- $P(B|\neg A) = 0.05$ (faux positifs : 5%)

Calcul du posterior :

$P(B) = P(B|A)P(A) + P(B|\neg A)P(\neg A)$
$P(B) = 0.99 \cdot 0.01 + 0.05 \cdot 0.99 = 0.0099 + 0.0495 = 0.0594$

$$P(A|B) = \frac{0.99 \cdot 0.01}{0.0594} = \frac{0.0099}{0.0594} \approx 0.167$$

**Même avec un test positif, probabilité d'avoir la maladie = 16.7% !** (car maladie rare)

### Rôle dans les LLMs

- **Réseaux Bayésiens** : Modélisent l'incertitude sur les poids
- **Few-shot learning** : Intègre la connaissance préalable
- **Calibration des prédictions** : Exprime l'incertitude du modèle

---

# 4. ATTENTION MECHANISM

## 4.1 Scaled Dot-Product Attention

### Théorème : Attention Mechanism Mathematique

**Énoncé :**
Donnés les matrices Query, Key, Value :

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V$$

où :
- $Q \in \mathbb{R}^{n \times d_k}$ = Queries (n tokens, d_k dimensions)
- $K \in \mathbb{R}^{m \times d_k}$ = Keys (m tokens, d_k dimensions)
- $V \in \mathbb{R}^{m \times d_v}$ = Values (m tokens, d_v dimensions)
- $d_k$ = dimension des keys (utilisé pour scaling)

**Étapes :**
1. Calcule similarité : $QK^T$ → matrice $(n \times m)$
2. Scale par $\sqrt{d_k}$ pour stabilité
3. Softmax par ligne pour normaliser en poids
4. Pondère les values : résultat $(n \times d_v)$

### Démonstration Pas-à-Pas

Exemple simplifié : 2 mots, 2 dimensions clé, 3 dimensions valeur

**Étape 1 : Définir Q, K, V**

$$Q = \begin{pmatrix} 1 & 0 \\ 0 & 1 \end{pmatrix}, \quad K = \begin{pmatrix} 1 & 0 \\ 1 & 1 \end{pmatrix}, \quad V = \begin{pmatrix} 1 & 0 & 1 \\ 0 & 1 & 0 \end{pmatrix}$$

**Étape 2 : Calcule $QK^T$ (scores)**

$$QK^T = \begin{pmatrix} 1 & 0 \\ 0 & 1 \end{pmatrix} \begin{pmatrix} 1 & 1 \\ 0 & 1 \end{pmatrix} = \begin{pmatrix} 1 & 1 \\ 0 & 1 \end{pmatrix}$$

**Étape 3 : Scale par $\sqrt{d_k} = \sqrt{2}$**

$$\frac{QK^T}{\sqrt{2}} = \begin{pmatrix} 0.707 & 0.707 \\ 0 & 0.707 \end{pmatrix}$$

**Étape 4 : Softmax par ligne**

Ligne 1 : $e^{0.707} \approx 2.028$, somme = $2 \times 2.028 = 4.056$
- $\sigma_1 = 2.028/4.056 = 0.500$
- $\sigma_2 = 2.028/4.056 = 0.500$

Ligne 2 : $e^0 = 1$, $e^{0.707} = 2.028$, somme = $3.028$
- $\sigma_1 = 1/3.028 = 0.330$
- $\sigma_2 = 2.028/3.028 = 0.670$

$$\text{Attention Weights} = \begin{pmatrix} 0.500 & 0.500 \\ 0.330 & 0.670 \end{pmatrix}$$

**Étape 5 : Pondérer Values**

$$\text{Output} = \begin{pmatrix} 0.500 & 0.500 \\ 0.330 & 0.670 \end{pmatrix} \begin{pmatrix} 1 & 0 & 1 \\ 0 & 1 & 0 \end{pmatrix}$$

Ligne 1 : $[0.500 \cdot 1 + 0.500 \cdot 0, 0.500 \cdot 0 + 0.500 \cdot 1, 0.500 \cdot 1 + 0.500 \cdot 0] = [0.5, 0.5, 0.5]$

Ligne 2 : $[0.330 \cdot 1 + 0.670 \cdot 0, 0.330 \cdot 0 + 0.670 \cdot 1, 0.330 \cdot 1 + 0.670 \cdot 0] = [0.330, 0.670, 0.330]$

$$\text{Output} = \begin{pmatrix} 0.5 & 0.5 & 0.5 \\ 0.330 & 0.670 & 0.330 \end{pmatrix}$$

### Rôle dans les LLMs

- **Contexte global** : Chaque token "voit" tous les autres tokens
- **Dépendances longue-distance** : Captive les relations lointaines
- **Multi-head attention** : Plusieurs attention mechanisms en parallèle

---

## 4.2 Multi-Head Attention

### Théorème : Attention Multi-Têtes

**Énoncé :**
Pour $h$ heads distincts avec poids séparés $W_i^Q$, $W_i^K$, $W_i^V$, $W_i^O$ :

$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, ..., \text{head}_h) W^O$$

où chaque head est :
$$\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$$

**Avantage :** Chaque head apprend des patterns d'attention différents

### Exemple Conceptuel

Si 8 heads :
- Head 1 : Fait attention aux sujets et verbes
- Head 2 : Capture les pronoms et antécédents
- Head 3 : Détecte les relations sémantiques
- ... etc

Le modèle apprend ces spécialisations automatiquement.

---

# 5. COMPLEXITÉ ALGORITHMIQUE

## 5.1 Notations Big-O et Cas Binaires

### Théorème : Classes de Complexité Courantes

| Notation | Nom | Croissance | Exemple |
|----------|-----|-----------|---------|
| $O(1)$ | Constant | Plat | Accès tableau |
| $O(\log n)$ | Logarithmique | Très lent | Recherche binaire |
| $O(n)$ | Linéaire | Proportionnel | Parcours liste |
| $O(n \log n)$ | Linéarithmique | Rapide-bon | Merge sort, tri rapide |
| $O(n^2)$ | Quadratique | Carré du nombre | Tri bulle, nested loops |
| $O(2^n)$ | Exponentiel | Doublage à chaque n | Forcer tous les subsets |
| $O(n!)$ | Factoriel | Explosif | Permutations |

---

## 5.2 Arbres Binaires de Recherche

### Théorème : Complexité Temporelle des BST Équilibrés

**Énoncé :**
Pour un arbre binaire de recherche *équilibré* avec $n$ nœuds, la profondeur est $O(\log n)$.
Donc les opérations (recherche, insertion, suppression) prennent $O(\log n)$.

**Preuve Intuitive :**
À chaque niveau, on divise l'espace de recherche par 2.
Nombre de divisions avant d'avoir 1 nœud = $\log_2(n)$.

### Démonstration Numérique

| Nombre de nœuds | Profondeur équilibrée | Étapes max |
|-----------------|----------------------|-----------|
| 1 | 0 | 1 |
| 3 | 1 | 2 |
| 7 | 2 | 3 |
| 15 | 3 | 4 |
| 31 | 4 | 5 |
| 1,000,000 | ~20 | ~21 |

Pour **1 million** de nœuds, seulement ~21 étapes ! (vs 1M pour liste)

### Cas de Dégénérescence

Si l'arbre n'est PAS équilibré (insérer en ordre croissant) :

```
    1
     \
      2
       \
        3
         \
          4  <- devient une liste !
```

Profondeur = $n$, complexité = $O(n)$ (pas mieux qu'une liste)

### Rôle dans les LLMs

Pas d'utilisation directe, MAIS :
- **Complexity awareness** : LLMs d'attention sont $O(n^2)$ en longueur de séquence
- **Approximations** : Sparse attention réduit à $O(n \log n)$
- **KV-cache** : Trade-off mémoire vs latence

---

## 5.3 Complexité de Transformer

### Théorème : Analyse Temporelle du Transformer

**Énoncé :**
Pour une séquence de longueur $n$, dimension modèle $d$, nombre de heads $h$ :

| Composant | Complexité |
|-----------|-----------|
| Attention (un head) | $O(n^2 d)$ pour calcul $QK^T$, puis $O(n^2 d)$ pour sortie |
| Multi-head attention ($h$ heads) | $O(n^2 d)$ (heads en parallèle) |
| Feed-forward (MLP) | $O(n d^2)$ (dense layers internes) |
| **Total par couche** | $O(n^2 d + n d^2)$ |
| **N couches transformer** | $O(N(n^2 d + n d^2))$ |

**Conséquence :** L'attention $O(n^2)$ domine quand $n$ grandit !

### Démonstration Empirique

Pour un modèle avec $d = 768$, $h = 12$, $N = 12$ couches :

| Longueur $n$ | Opérations Attention | Opérations FFN | Total |
|--------------|---------------------|----------------|--------|
| 10 | 92,160 | 92,160 | 184,320 |
| 100 | 9,216,000 | 921,600 | 10,137,600 |
| 1,000 | 921,600,000 | 9,216,000 | 930,816,000 |
| 2,048 | 3.8B | 18.8B | 22.6B |

**Attention croît en $n^2$ : passe de 92K à 3.8B opérations !**

---

# 6. EIGENVALUES ET EIGENVECTORS

## 6.1 Définition et Propriétés Fondamentales

### Théorème : Eigenvalues et Eigenvectors

**Énoncé :**
Pour une matrice carrée $A \in \mathbb{R}^{n \times n}$, un *eigenvector* $\mathbf{v}$ et son *eigenvalue* $\lambda$ satisfont :

$$A\mathbf{v} = \lambda \mathbf{v}$$

**Interprétation géométrique :**
- La transformation $A$ appliquée à $\mathbf{v}$ ne change que sa magnitude
- La direction reste inchangée (ou s'inverse si $\lambda < 0$)
- $\lambda$ est le facteur d'échelle

### Démonstration

Considérons $A = \begin{pmatrix} 4 & 1 \\ 2 & 3 \end{pmatrix}$ et vérifions que $\mathbf{v} = \begin{pmatrix} 1 \\ 1 \end{pmatrix}$ est eigenvector :

$$A\mathbf{v} = \begin{pmatrix} 4 & 1 \\ 2 & 3 \end{pmatrix} \begin{pmatrix} 1 \\ 1 \end{pmatrix} = \begin{pmatrix} 5 \\ 5 \end{pmatrix}$$

Si $\lambda = 5$ :
$$\lambda \mathbf{v} = 5 \begin{pmatrix} 1 \\ 1 \end{pmatrix} = \begin{pmatrix} 5 \\ 5 \end{pmatrix}$$

**Égal ! Donc $\mathbf{v}$ est eigenvector avec eigenvalue $\lambda = 5$.**

---

## 6.2 Équation Caractéristique

### Théorème : Trouver Eigenvalues

**Énoncé :**
Les eigenvalues sont solutions de l'équation caractéristique :

$$\det(A - \lambda I) = 0$$

où $I$ est la matrice identité.

### Démonstration

Pour $A = \begin{pmatrix} 4 & 1 \\ 2 & 3 \end{pmatrix}$ :

$$A - \lambda I = \begin{pmatrix} 4-\lambda & 1 \\ 2 & 3-\lambda \end{pmatrix}$$

Déterminant :
$$\det(A - \lambda I) = (4-\lambda)(3-\lambda) - (1)(2)$$
$$= 12 - 4\lambda - 3\lambda + \lambda^2 - 2$$
$$= \lambda^2 - 7\lambda + 10$$

Résoudre $\lambda^2 - 7\lambda + 10 = 0$ :
$$\lambda = \frac{7 \pm \sqrt{49 - 40}}{2} = \frac{7 \pm 3}{2}$$

$$\lambda_1 = 5, \quad \lambda_2 = 2$$

Pour $\lambda_1 = 5$, trouver eigenvector résout $(A - 5I)\mathbf{v} = 0$ :

$$\begin{pmatrix} -1 & 1 \\ 2 & -2 \end{pmatrix} \begin{pmatrix} v_1 \\ v_2 \end{pmatrix} = 0$$

$-v_1 + v_2 = 0 \Rightarrow v_1 = v_2$, donc $\mathbf{v}_1 = \begin{pmatrix} 1 \\ 1 \end{pmatrix}$ ✓

---

## 6.3 Rôle dans les LLMs : Réduction Dimensionnelle

### Théorème : Principal Component Analysis (PCA)

**Concept :**
Les eigenvectors de la matrice de covariance pointent dans les directions de plus grande variance.

$$\text{Covariance} = \frac{1}{n-1} X^T X$$

Les eigenvectors sont les *principal components*.

### Exemple

Données 2D de 100 points avec variance :
- Direction 1 (eigenvector avec $\lambda_1 = 10$) : Capture 90% variance
- Direction 2 (eigenvector avec $\lambda_2 = 1$) : Capture 10% variance

**Réduction :** Projetter sur Direction 1 seulement → 1D avec 90% info conservée.

### Rôle dans les LLMs

- **Embeddings visualization** : Réduit de 768D à 2D via PCA pour visualiser
- **Compression** : Élimine dimensions non-critiques
- **Initialisation poids** : Eigenvalues de covariance d'entrée guident l'initialisation

---

# RÉSUMÉ RÉCAPITULATIF

## Connexions Mathématiques dans les LLMs

```
Données d'entrée
    ↓
[Multiplication Matricielle] → Transformation linéaire
    ↓
[Activation ReLU/Softmax] → Non-linéarité
    ↓
[Attention: Dot Product] → Similarité (vecteurs)
    ↓
[Cross-Entropy Loss] → Mesure d'erreur (probabilités)
    ↓
[Backpropagation: Chain Rule] → Calcul gradients
    ↓
[Gradient Descent] → Mise à jour poids
    ↓
Modèle entraîné
```

---

## Fiche Rapide : Lettres Grecques Importantes

| Lettre | Utilisation | Exemple |
|--------|------------|---------|
| α (alpha) | Taux d'apprentissage | $W_{new} = W - \alpha \nabla L$ |
| β (bêta) | Paramètre momentum | $v_t = \beta v_{t-1} + (1-\beta) g_t$ |
| γ (gamma) | Normalisation | LayerNorm avec γ et β |
| δ (delta) | Erreur locale | $\delta_l = (W^{l+1})^T \delta_{l+1} \odot \sigma'(z^l)$ |
| ε (epsilon) | Petit nombre (stabilité) | $\text{softmax}_i = \frac{e^{z_i}}{\sum_j e^{z_j} + \epsilon}$ |
| η (êta) | Taux d'apprentissage | Synonyme de α |
| θ (thêta) | Paramètres modèle | $L(\theta)$ = perte en fonction θ |
| λ (lambda) | Eigenvalue ou régularisation | $L = L_{CE} + \lambda \|W\|^2$ |
| σ (sigma) | Fonction softmax/sigmoid | $\sigma(x) = \frac{1}{1 + e^{-x}}$ |
| ∇ (nabla) | Gradient | $\nabla L = [\frac{\partial L}{\partial w_1}, ..., \frac{\partial L}{\partial w_n}]$ |
| Σ (sigma cap) | Somme | $\Sigma_i a_i = a_1 + a_2 + ...$ |
| Π (pi cap) | Produit | $\Pi_i a_i = a_1 \times a_2 \times ...$ |

---

## Pour Aller Plus Loin

**Concepts Avancés à Étudier :**
1. Reparameterization Trick (Variational Autoencoders)
2. KL Divergence et Information Theory
3. Optimization Dynamics (Hessian, Newton's Method)
4. Sparse Attention et Linear Attention
5. Position Embeddings (RoPE, ALiBi)
6. Normalization Layers (LayerNorm, BatchNorm)

---

**Document créé pour développeurs cherchant fondamentaux mathématiques des LLMs.**
**Format Typora-compatible avec LaTeX natif pour tous les symboles grecs et mathématiques.**
