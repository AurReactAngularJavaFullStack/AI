## 5. Mathématiques des Transformers

### 5.1 Attention Mechanism

**Définition mathématique** : Le mécanisme d'attention scaled dot-product est défini par :

Attention(Q,K,V)=softmax((Q*K^T)/squareroot(dk))*V

où Q∈Rn×dk, K∈Rm×dk, V∈Rm×dv sont respectivement les matrices de requêtes (queries), clés (keys) et valeurs (values).

**Démonstration de l'échelle squareroot(dk) : Pour de grandes dimensions dk*, le produit scalaire q⋅k a une variance proportionnelle à dk*, ce qui pousse les valeurs de softmax vers des régions extrêmes (0 ou 1). La division par squareroot(dk*d)** stabilise les gradients : 

Var(q⋅k/squareroot(dk))=Var(q⋅k)/dk=(dk⋅σ²)/dk=σ² où σ² est la variance unitaire.

**Exemple numérique** : 

Pour dk=64, q=[1,0,…,0], k=[1,0,…,0] : (q⋅k)/squareroot(64)=1/8=0.125 

Sans l'échelle, le score serait 1, ce qui donnerait softmax ≈1.0 (saturation).

**Rôle dans les LLMs** : 

L'attention est le composant fondamental des Transformers. Elle permet au modèle de se concentrer sur les parties pertinentes du contexte lors de la génération de chaque token, capturant ainsi les dépendances à long terme dans le texte.