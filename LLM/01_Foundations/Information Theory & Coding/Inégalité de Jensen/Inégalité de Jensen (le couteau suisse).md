##  Inégalité de Jensen (le couteau suisse)

### Énoncé

Si $\varphi$ est convexe :
$$
\varphi\left(\mathbb{E}[X]\right) \le \mathbb{E}[\varphi(X)]
$$
Si $\varphi$ est concave, l’inégalité s’inverse.

### Démonstration (idée “segment”)

Pour convexe, le graphe est en dessous de ses cordes. En intégrant (moyennant) la relation linéaire sur les cordes, on obtient Jensen.

### Exemple ultra concret

$\varphi(x)=x^2$ convexe :
$$
(\mathbb{E}[X])^2 \le \mathbb{E}[X^2]
$$

### Rôle LLM

- Sert à prouver Gibbs (donc KL $\ge 0$).
- Sert partout en variational inference (ELBO), et en bornes de log-likelihood.

### 3.2. Inégalité de Jensen  

**Définition :** 

Pour une fonction convexe f et une variable aléatoire X :  

f(\mathbb{E}[X]) \leq \mathbb{E}[f(X)]  

**Application LLM :** 

Utilisée dans la divergence de Kullback-Leibler et l'optimisation des modèles.  

