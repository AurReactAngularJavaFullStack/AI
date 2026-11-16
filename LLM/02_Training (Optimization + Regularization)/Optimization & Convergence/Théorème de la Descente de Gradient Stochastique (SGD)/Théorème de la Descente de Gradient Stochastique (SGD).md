## 16. Théorèmes de Convergence Avancés  

### 16.1. Théorème de la Descente de Gradient Stochastique (SGD)  

**Condition :** La fonction f est L-convexe et les gradients ont variance bornée \sigma^2.  

**Convergence :**  

\mathbb{E}[f(\theta_t) - f(\theta^*)] \leq \frac{L\|\theta_0 - \theta^*\|^2}{2t} + \frac{\sigma^2}{2L}  

**Application LLM :** Vitesse de convergence de l'entraînement des transformers sur de grands ensembles de données.  
