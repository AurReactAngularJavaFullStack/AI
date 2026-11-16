## Gradient “magique” : Softmax + Cross-Entropy

### Setup

Cible one-hot $y$ (donc $y_c=1$ pour la classe correcte $c$, sinon 0).
 Perte :
$$
\mathcal{L} = -\sum_i y_i \log p_i = -\log p_c
$$

### Théorème (résultat clé)

$$
\frac{\partial \mathcal{L}}{\partial z_i} = p_i - y_i
$$

### Démonstration (esquisse propre)

On sait que :
$$
\mathcal{L}=-\sum_i y_i\log p_i
$$
Donc :
$$
\frac{\partial \mathcal{L}}{\partial z_j}
= -\sum_i y_i \frac{1}{p_i}\frac{\partial p_i}{\partial z_j}
$$
Remplace $\frac{\partial p_i}{\partial z_j} = p_i(\delta_{ij}-p_j)$ :
$$
\frac{\partial \mathcal{L}}{\partial z_j}
= -\sum_i y_i(\delta_{ij}-p_j)
= -y_j + p_j\sum_i y_i
$$
Or $\sum_i y_i = 1$ (one-hot). Donc :
$$
\frac{\partial \mathcal{L}}{\partial z_j} = p_j - y_j
$$

### Rôle LLM

C’est la raison pour laquelle l’entraînement d’un LLM est “simple” côté gradient : l’erreur locale = proba prédite − cible.