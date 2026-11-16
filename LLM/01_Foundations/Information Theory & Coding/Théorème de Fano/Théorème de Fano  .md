## 17. Théorèmes de la Théorie de l'Information  

### 17.1. Théorème de Fano  

**Définition :** Lie l'entropie mutuelle à la probabilité d'erreur.  

**Formule :**  

H(X|Y) \leq H_b(P_e) + P_e \log(|\mathcal{X}| - 1)

**Où :**  
- H_b(p) = -p \log_2 p - (1-p) \log_2(1-p) est l'entropie binaire  
- P_e : probabilité d'erreur de classification  
  

**Application LLM :** 

Bornes inférieures sur la perplexité des modèles de langage.  