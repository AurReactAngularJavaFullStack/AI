# 3) Maximum Likelihood (MLE) & lien direct avec la loss

## 3.1) MLE (estimateur du maximum de vraisemblance)
### Énoncé
L’estimateur MLE :
$$
\hat{\theta}_{\mathrm{MLE}}=\arg\max_\theta \prod_{n=1}^{N} p_\theta(x^{(n)})
$$

### Équivalent log
$$
\hat{\theta}_{\mathrm{MLE}}=\arg\max_\theta \sum_{n=1}^{N}\log p_\theta(x^{(n)})
$$

### Équivalent minimisation NLL
$$
\hat{\theta}_{\mathrm{MLE}}=\arg\min_\theta \sum_{n=1}^{N} \left(-\log p_\theta(x^{(n)})\right)
$$

### Démonstration (simple)
$\log$ est strictement croissante, donc maximiser $\prod$ revient à maximiser $\log(\prod)=\sum\log$.

### Rôle LLM
- “Entraîner un LLM” (pré-entraînement) = faire du MLE sur des milliards de tokens.

---

## 3.2) MLE et KL (pourquoi on converge vers la vraie distribution)
Si les données viennent d’une vraie distribution $q(x)$ et qu’on minimise la cross-entropy empirique, on approxime :
$$
\arg\min_\theta H(q, p_\theta)
$$
Or :
$$
H(q,p_\theta)=H(q)+D_{\mathrm{KL}}(q\|p_\theta)
$$
Donc minimiser la cross-entropy revient à minimiser :
$$
D_{\mathrm{KL}}(q\|p_\theta)
$$

### Rôle
- C’est la justification “propre” du training classique.