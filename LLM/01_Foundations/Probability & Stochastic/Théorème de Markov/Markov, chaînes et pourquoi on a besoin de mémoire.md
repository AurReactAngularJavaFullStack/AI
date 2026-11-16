## 0) Notations (rappel)
- Séquence : $x_{1:T} = (x_1,\dots,x_T)$.
- Modèle : $p_\theta(x_t\mid x_{<t})$.
- Logits : $z \in \mathbb{R}^V$.
- Softmax : $p_i = \dfrac{e^{z_i}}{\sum_j e^{z_j}}$.
- Dataset : $\mathcal{D}=\{x^{(n)}_{1:T_n}\}_{n=1}^N$.

---

# 1) Markov, chaînes et “pourquoi on a besoin de mémoire”

## 1.1) Propriété de Markov (ordre $k$)
### Définition
Une séquence $(X_t)$ est **Markov d’ordre $k$** si :
$$
\mathbb{P}(X_t \mid X_{1:t-1}) = \mathbb{P}(X_t \mid X_{t-k:t-1})
$$

### Exemple
- Markov ordre 1 :
$$
p(x_t \mid x_{<t}) = p(x_t \mid x_{t-1})
$$

### Rôle vs LLM
- Les **n-grams** sont Markov d’ordre $k$ (limité à une fenêtre).
- Les Transformers ne sont pas explicitement Markov : ils approximent $p(x_t\mid x_{<t})$ avec une **mémoire paramétrée** (attention) sur tout le contexte.

---

## 1.2) Factorisation Markov (chaîne)
Si Markov ordre $k$, la règle de chaîne devient :
$$
p(x_{1:T}) = p(x_{1:k})\prod_{t=k+1}^{T} p(x_t\mid x_{t-k:t-1})
$$

### Rôle
- Montre la différence entre :
  - modéliser “localement” (Markov)  
  - vs modéliser “globalement” (LLM).