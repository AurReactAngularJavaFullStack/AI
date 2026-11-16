## 5. Théorèmes d'Information  

### 5.1. Théorème de l'Entropie de Shannon  

**Définition :** Mesure l'incertitude d'une variable aléatoire.  

**Formule :**  

H(X) = -\sum_{x \in \mathcal{X}} p(x) \log_2 p(x)  

**Entropie conditionnelle :**  

H(X|Y) = -\sum_{x,y} p(x,y) \log_2 \frac{p(x,y)}{p(y)}  

**Application LLM :**   
- *Tokenization* : optimisation du vocabulaire  
- *Loss function* : cross-entropy pour la prédiction de tokens  
- Compression de modèles  
  

---

## 1. Théorie de l'Information

### 1.1 Entropie de Shannon

**Définition** : 

L'entropie H(X) d'une variable aléatoire discrète X prenant des valeurs dans un ensemble X avec distribution de probabilité p(x) est définie par :

H(X)=−∑x∈Xp(x)log⁡2p(x)

**Démonstration intuitive** : 

L'entropie mesure l'incertitude ou la quantité d'information moyenne contenue dans une variable aléatoire. Plus la distribution est uniforme, plus l'entropie est élevée.

**Exemple** : 

Pour une pièce de monnaie équilibrée (p(pile)=p(face)=0.5) :

H(X)=−(0.5 log⁡2 0.5+ 0.5 log⁡2 0.5)=−(0.5×(−1)+0.5×(−1))=1 bit

**Rôle dans les LLMs** : L'entropie est utilisée pour mesurer la perplexité des modèles linguistiques et pour l'échantillonnage lors de la génération de texte. Elle quantifie l'incertitude du modèle face à la prochaine prédiction.