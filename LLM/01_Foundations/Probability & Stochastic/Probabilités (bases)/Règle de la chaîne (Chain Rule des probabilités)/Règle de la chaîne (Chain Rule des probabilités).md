## A1) Règle de la chaîne (Chain Rule des probabilités)

### Énoncé

Pour toute séquence $x_{1:T}$ :
$$
p(x_{1:T}) = \prod_{t=1}^{T} p(x_t \mid x_{1:t-1})
$$
(par convention, $p(x_1 \mid x_{1:0}) = p(x_1)$)

### Démonstration (version “école”)

On part de :
$$
p(x_{1:T}) = p(x_T, x_{1:T-1})
$$
Par définition de la proba conditionnelle :
$$
p(x_T, x_{1:T-1}) = p(x_T \mid x_{1:T-1}) \, p(x_{1:T-1})
$$
Puis on réapplique récursivement sur $p(x_{1:T-1})$, etc., jusqu’à $x_1$. On obtient le produit.

### Exemple

Si $T=3$ :
$$
p(x_1,x_2,x_3)=p(x_1)\,p(x_2\mid x_1)\,p(x_3\mid x_1,x_2)
$$

### Rôle dans les LLM

C’est littéralement la définition opérationnelle d’un LLM autoregressif : “je factorise la proba d’une phrase en un produit le long d’un chemin dans l’arbre”.