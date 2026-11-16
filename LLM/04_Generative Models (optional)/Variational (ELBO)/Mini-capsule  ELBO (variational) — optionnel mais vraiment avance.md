# 9) Mini-capsule : ELBO (variational) — optionnel mais “vraiment avancé”
> Je te le mets parce que Jensen + log-sum-exp + latent variables = combo fréquent dès qu’on veut “tricher intelligemment”.

Supposons une variable latente $z$ :
$$
p_\theta(x)=\sum_z p_\theta(x,z)
$$
Le log est dur :
$$
\log p_\theta(x)=\log \sum_z p_\theta(x,z)
$$

On introduit une distribution auxiliaire $q(z\mid x)$ :
$$
\log p_\theta(x)
=
\log \sum_z q(z\mid x)\frac{p_\theta(x,z)}{q(z\mid x)}
$$

Par Jensen (log concave) :
$$
\log p_\theta(x) \ge \sum_z q(z\mid x)\log \frac{p_\theta(x,z)}{q(z\mid x)}
$$

Définis l’ELBO :
$$
\mathrm{ELBO}(\theta,q)
=
\mathbb{E}_{q(z\mid x)}[\log p_\theta(x,z)] - \mathbb{E}_{q(z\mid x)}[\log q(z\mid x)]
$$

### Rôle
- Base de variational inference.
- Utile pour comprendre certains modèles génératifs et méthodes d’entraînement.