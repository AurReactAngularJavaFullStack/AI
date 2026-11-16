## C3) Règle de la chaîne (version dérivées) = fondation du backprop

### Énoncé

Si $u=g(x)$ et $v=f(u)$, alors :
$$
\frac{dv}{dx}=\frac{dv}{du}\cdot \frac{du}{dx}
$$

### Généralisation (multi-variables)

Si $v=f(u_1,\dots,u_n)$ et chaque $u_k=g_k(x)$ :
$$
\frac{dv}{dx}=\sum_{k=1}^{n}\frac{\partial v}{\partial u_k}\frac{du_k}{dx}
$$

### Rôle “arbre / graphe”

Dans un graphe de calcul, un nœud influence la sortie via plusieurs chemins : le gradient se **somme** sur les chemins (comme une “somme de branches”). C’est exactement la formule ci-dessus.