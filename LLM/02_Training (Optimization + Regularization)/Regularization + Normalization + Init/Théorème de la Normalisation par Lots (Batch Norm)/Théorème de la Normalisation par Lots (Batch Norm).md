## 19. Théorèmes de Normalisation  

### 19.1. Théorème de la Normalisation par Lots (Batch Norm)  

**Pour un batch B = \{x_1, \dots, x_m\} :**  

\mu_B = \frac{1}{m} \sum_{i=1}^m x_i  _

_\sigma_B^2 = \frac{1}{m} \sum_{i=1}^m (x_i - \mu_B)^2  

\hat{x}_i = \frac{x_i - \mu_B}{\sqrt{\sigma_B^2 + \epsilon}}  _

_y_i = \gamma \hat{x}_i + \beta  

**Application LLM :** 

Stabilise l'entraînement des transformers profonds.  