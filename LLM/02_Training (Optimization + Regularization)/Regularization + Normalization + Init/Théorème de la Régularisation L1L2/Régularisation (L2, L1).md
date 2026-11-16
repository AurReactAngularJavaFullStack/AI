# 4) Régularisation (L2, L1) : empêcher le modèle de devenir un sociopathe numérique

## 4.1) Régularisation L2 (ridge / weight decay)
### Définition
On minimise :
$$
\mathcal{J}(\theta)=\mathcal{L}(\theta)+\lambda \|\theta\|_2^2
$$

### Rôle
- Contraint la norme des poids : réduit overfit, stabilise l’optimisation.
- En deep learning, **weight decay** est souvent la version “propre” côté optimisation.

---

## 4.2) Interprétation Bayésienne (MAP)
Si prior gaussien :
$$
p(\theta)\propto \exp\left(-\frac{\lambda}{2}\|\theta\|_2^2\right)
$$
Alors maximiser le posterior (MAP) :
$$
\hat{\theta}_{\mathrm{MAP}}=\arg\max_\theta \log p(\mathcal{D}\mid \theta)+\log p(\theta)
$$
revient à minimiser :
$$
-\log p(\mathcal{D}\mid\theta)+\lambda \|\theta\|_2^2
$$

### Rôle
- L2 = “tu dis au modèle : je préfère des paramètres petits *a priori*”.