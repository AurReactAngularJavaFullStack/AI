## 10. Théorèmes de Calcul Stochastique  

### 10.1. Théorème d'Itô  

**Pour un processus $X_t$ différentiable :**  

df(t, X_t) = \left(\frac{\partial f}{\partial t} + \mu \frac{\partial f}{\partial x} + \frac{1}{2}\sigma^2 \frac{\partial^2 f}{\partial x^2}\right)dt + \sigma \frac{\partial f}{\partial x} dW_t$$  

**Application LLM :** Modélisation de la dynamique des gradients pendant l'entraînement (*diffusion models*).  

---