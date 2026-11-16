## F2) Longueurs et scores dans l’arbre de décodage (log-probabilité)

Si tu scores un chemin :
$$
\log p(x_{1:T}) = \sum_{t=1}^{T} \log p(x_t \mid x_{<t})
$$
Ça transforme le produit en somme → indispensable pour :

- beam search (garder les meilleurs chemins),
- comparaisons numériques stables.