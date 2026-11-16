### 3.1. Théorème de Bayes  

**Définition :** Relation fondamentale entre probabilités conditionnelles.  

**Formule :**  

P(A|B) = \frac{P(B|A) . P(A)}{P(B)}  

**Démonstration :** 

Par définition de l'indépendance conditionnelle :

 P(A \cap B) = P(A|B)P(B) = P(B|A)P(A).  

**Exemple :** 

Dans un LLM, P(\text{"chat"}|\text{"le"}) peut être mis à jour avec P(\text{"le"}|\text{"chat"}).  

**Application LLM :** 

Base des modèles de langage probabilistes et du *fine-tuning*.  

---