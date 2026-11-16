# 5) Dropout vu comme espérance (et pourquoi c’est une régularisation)

## 5.1) Définition (masque)
Dropout sur un vecteur d’activations $h$ :
$$
m_i \sim \mathrm{Bernoulli}(p)
\quad,\quad
\tilde{h} = \frac{m \odot h}{p}
$$

Le facteur $\frac{1}{p}$ est l’**inverted dropout**.

### Propriété (espérance)
$$
\mathbb{E}[\tilde{h}_i] = h_i
$$

### Démonstration
$$
\mathbb{E}[\tilde{h}_i] = \mathbb{E}\left[\frac{m_i h_i}{p}\right]
=\frac{h_i}{p}\mathbb{E}[m_i]
=\frac{h_i}{p}\cdot p = h_i
$$

### Rôle
- En moyenne, tu gardes la même activation, mais tu ajoutes du bruit multiplicatif.
- Effet : empêche des co-adaptations, améliore généralisation.

---

## 5.2) Dropout ~ ensemble implicite (intuition)
Chaque masque $m$ définit un “sous-modèle”.  
En entraînement, tu optimises une espérance :
$$
\min_\theta \mathbb{E}_{m}\left[\mathcal{L}(\theta; m)\right]
$$

### Rôle
- Le modèle apprend à être robuste à l’absence de certaines features.