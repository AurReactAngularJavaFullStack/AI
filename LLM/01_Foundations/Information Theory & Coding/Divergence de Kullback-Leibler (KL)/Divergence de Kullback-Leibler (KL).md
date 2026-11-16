### 5.2. Divergence de Kullback-Leibler (KL)  

**Définition :** Mesure la différence entre deux distributions de probabilité.  

**Formule :**  

D_{KL}(P \| Q) = \sum_{x} P(x) \log \frac{P(x)}{Q(x)} 

**Propriété :** 

D_{KL} \geq 0 avec égalité si et seulement si P = Q.  

**Application LLM :**   
- Distillation de modèles  
- Regularization pendant l'entraînement  
- Évaluation de la qualité des distributions de tokens  
  

---

### 1.2 Divergence de Kullback-Leibler (KL)

**Définition** : La divergence KL entre deux distributions de probabilité P*P* et Q*Q* définies sur le même espace probabilisé est :

DKL(P∥Q)=∑x∈X P(x)log(⁡P(x)/Q(x))

**Propriétés** :

- DKL(P∥Q)≥0 (inégalité de Gibbs)
- DKL(P∥Q)=0 si et seulement si P=Q
- Non-symétrique : DKL(P∥Q)≠DKL(Q∥P)

**Démonstration de l'inégalité de Gibbs** : 

Par l'inégalité de Jensen, pour une fonction concave ϕ : ϕ(E[X])≥E[ϕ(X)] 

Avec ϕ(x)=log⁡(x) et X=Q(x)/P(x) : 

log⁡(∑x P(x) (Q(x)/P(x))≥∑x P(x) log⁡(Q(x)/P(x)) 

log⁡(1)≥−DKL(P∥Q)  ⟹  0≥−DKL(P∥Q)  ⟹  DKL(P∥Q)≥0

**Exemple**: 

Soient P=[0.7,0.3]*P*=[0.7,0.3] et Q=[0.5,0.5]*Q*=[0.5,0.5] : DKL(P∥Q)=0.7log⁡(0.7/0.5)+0.3log(⁡0.3/0.5)≈0.088

**Rôle dans les LLMs** : La divergence KL est utilisée dans :

- La distillation de connaissances (Knowledge Distillation)
- La régularisation des modèles
- L'apprentissage par renforcement avec feedback humain (RLHF)
- La mesure de similarité entre distributions de tokens