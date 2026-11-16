### 2.2 Rétropropagation (Backpropagation)

**Définition** : 

La rétropropagation est un algorithme efficace pour calculer le gradient d'une fonction composée en utilisant la règle de la chaîne (chain rule). Pour un réseau de neurones avec L*L* couches :

δ(l)={(a(L)−y)⊙g′(z(L)) si l=L 

((W^(l+1)T) * (δ^(l+1))⊙g′(z(l)) sinon

où δ(l) est l'erreur à la couche l, g′ est la dérivée de la fonction d'activation, et ⊙ représente le produit de Hadamard.

**Démonstration mathématique** (règle de la chaîne) : 

Pour une fonction composée f*(*g*(*x*)) : ∂f/∂x=(∂f/∂g⋅(∂g/∂x)  *

Par extension à plusieurs variables et couches : (∂J/∂W(l))=δ(l) a(l−1)T

**Exemple** : 

Pour un réseau à une seule couche cachée avec activation sigmoïde g(z)=1/(1+e^(−z)) : 

g′(z)=g(z)(1−g(z))

**Rôle dans les LLMs** : 

La rétropropagation permet l'entraînement efficace des réseaux de neurones profonds comme les Transformers, en calculant les gradients pour des millions (voire milliards) de paramètres de manière computationnellement viable.