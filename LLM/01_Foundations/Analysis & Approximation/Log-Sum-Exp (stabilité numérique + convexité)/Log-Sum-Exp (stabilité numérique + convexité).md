## F1) Log-Sum-Exp (stabilité numérique + convexité)

### Définition

$$
\mathrm{LSE}(z)=\log\left(\sum_{i=1}^{V} e^{z_i}\right)
$$

### Propriété clé (stabilité)

Pour éviter overflow :
$$
\log\left(\sum_i e^{z_i}\right)
= m + \log\left(\sum_i e^{z_i-m}\right)
\quad \text{où } m=\max_i z_i
$$

### Rôle LLM

- Softmax = $e^{z_i - \mathrm{LSE}(z)}$
- Dans un arbre de décodage, les scores s’additionnent en log-probas ; LSE apparaît dès que tu “somes” des alternatives (marginalisation).