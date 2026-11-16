## D1) Inégalité de Kraft–McMillan (codes préfixes)

### Contexte

Un code binaire préfixe (représentable par un arbre binaire) associe à chaque symbole un mot binaire de longueur $\ell_i$.

### Théorème (Kraft)

Pour un code préfixe binaire :
$$
\sum_i 2^{-\ell_i} \le 1
$$
Et réciproquement, si une famille de longueurs $(\ell_i)$ vérifie cette inégalité, **il existe** un code préfixe avec ces longueurs.

### Intuition (preuve “arbre”)

Dans un arbre binaire :

- Un mot de longueur $\ell$ correspond à une feuille à profondeur $\ell$.
- Il “occupe” une fraction $2^{-\ell}$ de l’espace des feuilles possibles.
   Les feuilles étant disjointes (préfixe), la somme des fractions ne dépasse pas 1.

### Rôle LLM

- Les vocabulaires/tokenisations sont souvent gérés via structures “préfixes” (tries).
- Donne des limites théoriques sur la compression / représentation par codes.