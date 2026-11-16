### 2.1 Descente de Gradient (Gradient Descent)

**Définition** : Soit J(θ)*J*(*θ*) une fonction de coût différentiable où θ∈Rn*θ*∈R*n* sont les paramètres. L'algorithme de descente de gradient met à jour les paramètres selon :

θt+1=θt−η∇θJ(θt)

où η>0*η*>0 est le taux d'apprentissage et ∇θJ(θt) est le gradient de la fonction de coût.

**Démonstration de convergence** (cas simplifié) : Pour une fonction L*L*-lipschitzienne et β*β*-lisse : 

J(θt+1)≤J(θt)−η∥∇J(θt)∥²+ ((βη²)/2)∥∇J(θt)∥²

 Si η<2/β alors J(θt+1)<J(θt), garantissant la décroissance de la fonction de coût.

**Exemple** : 

Pour une régression linéaire J(θ)=(1/2m)∑i=1-> m (hθ(x(^i))−y(^i))² : 

∂J/∂θj=(1/m) ∑i=1 ->m (hθ(x(^i))−y(^i))x j -> (i)

**Rôle dans les LLMs** : 

La descente de gradient est l'algorithme fondamental pour l'entraînement des réseaux de neurones, y compris les Transformers. Les variantes comme Adam, RMSProp, etc., sont des extensions de ce principe de base.

## 6. Applications Pratiques pour un Développeur Freelance

### 6.1 Implémentation en Java/Angular

Les concepts mathématiques ci-dessus se traduisent en code :

**Application dans les LLMs** : Comprendre ces bases mathématiques permet de :

- Optimiser les hyperparamètres des modèles
- Comprendre les limitations et biais des systèmes d'IA
- Développer des solutions hybrides (règles métier + ML)
- Communiquer efficacement avec les data scientists

**Exemple de descente de gradient en Java** :

```java
public class GradientDescent {
    private double learningRate;
    
    public void train(double[][] X, double[] y, int iterations) {
        double[] theta = new double[X[0].length];
        
        for (int i = 0; i < iterations; i++) {
            double[] gradient = computeGradient(X, y, theta);
            // θ := θ - η∇J(θ)
            for (int j = 0; j < theta.length; j++) {
                theta[j] -= learningRate * gradient[j];
            }
        }
    }
    
    private double[] computeGradient(double[][] X, double[] y, double[] theta) {
        // Calcul du gradient ∇J(θ)
        double[] gradient = new double[theta.length];
        // ... implémentation mathématique
        return gradient;
    }
}
```

