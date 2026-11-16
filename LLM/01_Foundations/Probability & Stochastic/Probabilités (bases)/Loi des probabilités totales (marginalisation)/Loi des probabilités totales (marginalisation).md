## A2) Loi des probabilités totales (marginalisation)

### Énoncé

Si $(B_k)_k$ est une partition (événements disjoints dont l’union couvre tout) :
$$
p(A) = \sum_k p(A \mid B_k)\,p(B_k)
$$

### Démonstration

On écrit :
$$
A = \bigcup_k (A \cap B_k)
$$
Comme les $B_k$ sont disjoints, les $A\cap B_k$ sont disjoints :
$$
p(A)=\sum_k p(A\cap B_k)
$$
Et $p(A\cap B_k)=p(A\mid B_k)p(B_k)$.

### Exemple (mini-arbre)

Tu veux $p(\text{token}=\text{"chat"})$ mais ça dépend d’un “mode” latent $B \in {\text{formel},\text{familier}}$ :
$$
p(\text{"chat"}) = p(\text{"chat"}\mid \text{formel})p(\text{formel}) + p(\text{"chat"}\mid \text{familier})p(\text{familier})
$$

### Rôle LLM

- Sert à comprendre **marginalisation** (quand tu “intègres”/sommes des branches non observées).
- Hyper important dès que tu touches à des modèles latents (mixtures, alignement, RLHF, etc.).