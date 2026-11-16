## Dérivée du softmax (jacobien)

### Définition

$$
p_i = \frac{e^{z_i}}{\sum_{k} e^{z_k}}
$$

### Théorème (formule)

Pour tout $i,j$ :
$$
\frac{\partial p_i}{\partial z_j} = p_i(\delta_{ij} - p_j)
$$
où $\delta_{ij}=1$ si $i=j$, sinon $0$.

### Démonstration (calcul direct)

Soit $S=\sum_k e^{z_k}$. Alors $p_i=\frac{e^{z_i}}{S}$.

- Si $i=j$ :

$$
\frac{\partial p_i}{\partial z_i}=\frac{e^{z_i}S - e^{z_i}e^{z_i}}{S^2}
=\frac{e^{z_i}}{S}\left(1-\frac{e^{z_i}}{S}\right)=p_i(1-p_i)
$$

- Si $i\ne j$ :

$$
\frac{\partial p_i}{\partial z_j}=\frac{0\cdot S - e^{z_i}e^{z_j}}{S^2}
= -\frac{e^{z_i}}{S}\frac{e^{z_j}}{S} = -p_i p_j
$$

On regroupe avec $\delta_{ij}$ :
$$
\frac{\partial p_i}{\partial z_j} = p_i(\delta_{ij}-p_j)
$$

### Rôle LLM

C’est la base de la rétropropagation : comment une variation de logits change les probabilités.