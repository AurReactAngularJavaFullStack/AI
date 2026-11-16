## Décomposition Cross-Entropy = Entropie + KL

### Énoncé

$$
H(q,p)=H(q)+D_{\mathrm{KL}}(q\|p)
$$

### Démonstration

$$
H(q,p)=-\sum_i q_i\log p_i
$$

Ajoute et retire $-\sum_i q_i\log q_i$ :
$$
H(q,p)= -\sum_i q_i\log q_i + \sum_i q_i\log\frac{q_i}{p_i}
$$
Donc :
$$
H(q,p)=H(q)+D_{\mathrm{KL}}(q\|p)
$$

### Rôle LLM

- Quand tu minimises la perte (cross-entropy), tu réduis l’écart $q \to p_\theta$ (KL).
- L’entropie $H(q)$ ne dépend pas de ton modèle : c’est “le bruit du monde”.