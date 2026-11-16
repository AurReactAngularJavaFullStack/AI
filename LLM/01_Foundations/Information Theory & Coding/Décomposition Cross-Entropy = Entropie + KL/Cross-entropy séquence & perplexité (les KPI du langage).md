# 2) Cross-entropy séquence & perplexité (les KPI du langage)

## 2.1) Log-vraisemblance séquence (NLL)
Pour une séquence $x_{1:T}$ :
$$
\log p_\theta(x_{1:T})=\sum_{t=1}^{T}\log p_\theta(x_t\mid x_{<t})
$$

La **negative log-likelihood** (perte NLL) :
$$
\mathcal{L}_{\mathrm{NLL}}(x_{1:T}) = -\sum_{t=1}^{T}\log p_\theta(x_t\mid x_{<t})
$$

### Rôle
- En entraînement “next-token”, tu minimises exactement cette quantité.

---

## 2.2) Cross-entropy séquence (moyenne par token)
Sur un dataset totalisant $M$ tokens (somme des $T_n$) :
$$
\mathrm{CE}(\theta)= -\frac{1}{M}\sum_{n=1}^{N}\sum_{t=1}^{T_n}\log p_\theta(x_t^{(n)}\mid x_{<t}^{(n)})
$$

### Rôle
- C’est la “loss” standard en LLM (en pratique avec masques, padding, etc.).

---

## 2.3) Perplexité
### Définition
Si la cross-entropy est en log naturel :
$$
\mathrm{PPL}=\exp(\mathrm{CE})
$$

Si en base 2 :
$$
\mathrm{PPL}=2^{\mathrm{CE}_{\log_2}}
$$

### Intuition
- PPL ≈ “nombre moyen de choix équivalents” à chaque token.
- PPL = 10 signifie : le modèle est aussi incertain que s’il avait ~10 options plausibles en moyenne.

### Rôle
- KPI classique, mais attention : PPL peut être trompeuse (meilleure PPL ≠ meilleure vérité, sécurité, utilité).

---