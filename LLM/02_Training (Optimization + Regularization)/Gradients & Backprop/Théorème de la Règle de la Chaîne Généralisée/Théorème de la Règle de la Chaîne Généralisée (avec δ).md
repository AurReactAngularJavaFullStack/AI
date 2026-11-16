### 1.3 Théorème de la Règle de la Chaîne Généralisée (avec *δ*)

**Définition** : 

Pour une fonction composée f(g(x)), la dérivée est : 

∂f∂x=(∂f/∂g)⋅(∂g/∂x)

Dans les réseaux de neurones profonds, on définit l'erreur δ(l) à la couche l comme : 

δ(l)= (∂J/∂z^(l))

où z(l) est l'entrée activée à la couche l.

**Démonstration pour un réseau à 3 couches** : 

δ(3)=(∂J/∂z^(3))=(a^(3)−y)⊙σ′(z^(3)) 

δ(2)= (∂J/∂z^(2)) = ((W^(3)T) δ^(3))⊙σ′(z^(2))

 δ(1)= (∂J/∂z^(1)) = ((W^(2)T) δ^(2))⊙σ′(z^(1))

**Exemple de calcul** : 

Pour une fonction d'activation sigmoïde σ(z)=1/(1+e^(−z)), sa dérivée est σ′(z)=σ(z)(1−σ(z)).

Si z(3)=0.5, alors σ′(0.5)=σ(0.5)(1−σ(0.5))≈0.622×0.378≈0.235.

**Rôle dans les LLMs** : 

Le terme δ (delta) représente l'erreur propagée en arrière. 

Dans les Transformers, δ est calculé pour chaque couche d'attention et de feed-forward, permettant l'apprentissage de millions de paramètres.