# Théorèmes Mathématiques Fondamentaux pour les LLMs et Arbres Algorithmiques - Partie 2  

## 15. Théorèmes d'Apprentissage Statistique  

### 15.1. Théorème d'Approximation Universelle  

**Énoncé :** Un réseau de neurones avec une seule couche cachée de taille suffisante peut approximer n'importe quelle fonction continue sur un compact.  

**Formule :** Pour toute fonction continue f et \epsilon > 0, il existe N et des poids W tels que :  
\|f(x) - \sum_{i=1}^N \alpha_i \sigma(w_i^T x + b_i)\| < \epsilon  

**Où :**  
- \sigma : fonction d'activation (ReLU, tanh, etc.)  
- w_i : poids de la couche cachée  
- \alpha_i : poids de sortie  
  

**Application LLM :** Justifie l'architecture des transformers pour approximer des fonctions de langage complexes.  

---