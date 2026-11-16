```markdown

```

## 8. Théorèmes Spécifiques aux Transformers  

### 8.1. Théorème de l'Attention Universelle  

**Formule de l'attention :**  

\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V  

**Où :**  
- Q : requêtes (queries)  
- K : clés (keys)  
- V : valeurs (values)  
- d_k : dimension des clés  
  

**Application LLM :** 

Cœur des modèles GPT, BERT, etc.  

---