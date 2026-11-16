### 15.2. Théorème de Vapnik-Chervonenkis (VC Dimension)  

**Définition :** 

La VC dimension d_{VC} est la taille maximale d'un ensemble de points pouvant être "shatteré" par l'hypothèse.  

**Bornes de généralisation :** Avec probabilité 1-\delta :  

R(f) \leq R_{emp}(f) + \sqrt{\frac{d_{VC} \log(2n/d_{VC}) + \log(2/\delta)}{n}}  

**Application LLM :** 

Estimation de la capacité des modèles et risque de sur-apprentissage.  