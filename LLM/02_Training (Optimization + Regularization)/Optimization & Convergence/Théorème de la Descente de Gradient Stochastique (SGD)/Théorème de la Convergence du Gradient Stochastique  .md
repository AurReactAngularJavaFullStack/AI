### 4.2. Théorème de la Convergence du Gradient Stochastique  

**Condition :** Sous des hypothèses de Lipschitz, le gradient stochastique converge presque sûrement vers un minimum local.  

**Formule :**  

\mathbb{E}\left[\|\theta_t - \theta^*\|^2\right] \leq (1 - \mu\eta)^t \|\theta_0 - \theta^*\|^2  

**Application LLM :** 

Garantit la convergence de l'entraînement des transformers.  

---

## 1. Théorèmes Fondamentaux avec Lettres Grecques pour les LLMs

### 1.1 Théorème de Convergence de la Descente de Gradient (avec paramètre *η*)

**Définition** : 

Soit J(θ) une fonction de coût β-lisse (Lipschitz continue) avec β>0. 

Pour un taux d'apprentissage constant η satisfaisant 0<η≤1/β, la descente de gradient converge vers un minimum local :

θt+1=θt−η∇θJ(θt)

**Démonstration**:

Par la propriété de β*β-lissitude :

J(θt+1)≤J(θt)+∇J(θt)^T(θt+1−θt)+(β/2)∥θt+1−θt∥²

En substituant θt+1−θt=−η∇J(θt) : 

J(θt+1)≤J(θt)−η∥∇J(θt)∥²+()(βη²)/2)∥∇J(θt)∥²

 J(θt+1)≤J(θt)−η(1− ((βη)/2)∥∇J(θt)∥²

Si η≤1/β , alors 1− (βη/2) ≥1/2 donc : 

J(θt+1)≤J(θt)−(η/2)*∥∇J(θt)∥²*

**Exemple numérique** : 

Pour η=0.01 et ∥∇J(θt)∥=10 : 

J(θt+1) ≤ J(θt)− (0.01/2) ×100=J(θt)−0.5

**Rôle dans les LLMs** :

 Le paramètre η (eta) contrôle la vitesse d'apprentissage. 

Un η trop grand cause des oscillations, trop petit ralentit la convergence. 

Dans les Transformers, η est souvent ajusté dynamiquement avec des schedule comme le warm-up.