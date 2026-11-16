## Inégalité de Gibbs (non-négativité du KL)

### Énoncé

Pour deux distributions $q$ et $p$ :
$$
D_{\mathrm{KL}}(q\|p) \ge 0
$$
avec égalité ssi $q=p$ (presque partout).

### Démonstration (via Jensen)

On utilise le fait que $\log$ est concave, donc $-\log$ est convexe.
 On part de :
$$
D_{\mathrm{KL}}(q\|p)=\sum_i q_i \log\frac{q_i}{p_i}
$$
Soit $X=\frac{p_i}{q_i}$ sous la loi $q$. Alors :
$$
\mathbb{E}_q[X] = \sum_i q_i \frac{p_i}{q_i}=\sum_i p_i=1
$$
Par Jensen sur $-\log$ (convexe) :
$$
\mathbb{E}_q[-\log X] \ge -\log(\mathbb{E}_q[X]) = -\log(1)=0
$$
Or $\mathbb{E}*q[-\log X]=\sum_i q_i \log\frac{q_i}{p_i}=D*{\mathrm{KL}}(q|p)$.

### Rôle LLM

- La cross-entropy minimisée en entraînement, c’est (à une constante près) minimiser un KL.
- Justifie qu’il y a un **minimum “propre”** : tu ne peux pas faire mieux que coller la vraie distribution.