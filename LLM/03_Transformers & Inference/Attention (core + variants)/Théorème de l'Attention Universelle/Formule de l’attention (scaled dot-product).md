# 6) Attention = produit scalaire + softmax (et théorèmes utiles)

## 6.1) Formule de l’attention (scaled dot-product)
Avec requêtes $Q$, clés $K$, valeurs $V$ :
$$
\mathrm{Attn}(Q,K,V)=\mathrm{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
$$

### Pourquoi $\sqrt{d_k}$ ?
Si composantes i.i.d, le produit scalaire grandit avec $d_k$, ce qui rend softmax trop “sharp”.  
La division stabilise la variance.

---

## 6.2) Softmax = solution d’un problème d’optimisation (entropie maximale)
### Théorème (forme standard)
La distribution :
$$
p_i = \frac{e^{z_i}}{\sum_j e^{z_j}}
$$
est la solution de :
$$
\max_{p\in\Delta} \left( \sum_i p_i z_i + H(p) \right)
$$
où $\Delta=\{p_i\ge 0,\sum_i p_i=1\}$.

### Démonstration (Lagrangien)
On maximise :
$$
\mathcal{F}(p)=\sum_i p_i z_i - \sum_i p_i\log p_i
$$
Sous contrainte $\sum_i p_i=1$. Lagrangien :
$$
\mathcal{L}(p,\alpha)=\sum_i p_i z_i - \sum_i p_i\log p_i + \alpha\left(\sum_i p_i-1\right)
$$
Dérivée par rapport à $p_i$ :
$$
\frac{\partial \mathcal{L}}{\partial p_i}= z_i - (1+\log p_i)+\alpha = 0
$$
Donc :
$$
\log p_i = z_i + (\alpha-1)
\Rightarrow p_i = C e^{z_i}
$$
Normalisation $\sum_i p_i=1$ donne :
$$
p_i = \frac{e^{z_i}}{\sum_j e^{z_j}}
$$

### Rôle LLM
- Attention : softmax agit comme un compromis entre “suivre les meilleurs scores” et “garder de l’entropie”.
- Quand tu modifies la température, tu modifies ce compromis.

---

## 6.3) Température $\tau$
Softmax avec température :
$$
p_i(\tau)=\frac{e^{z_i/\tau}}{\sum_j e^{z_j/\tau}}
$$
- $\tau \to 0$ : distribution se concentre sur l’argmax.
- $\tau \to \infty$ : distribution devient quasi uniforme.

### Rôle
- Sampling, créativité, stabilité, calibrage.

---