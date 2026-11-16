## 7. **Théorème d'Universalité de l'Approximation (de Hornik-Stinchcombe-White)**

*Fondement théorique des réseaux de neurones et des modèles de deep learning.*

- **Énoncé formel** : 

  Soit σ une fonction d'activation continue, non constante et bornée. Alors pour toute fonction continue f:[0,1]n→Ret tout ε > 0, il existe un réseau de neurones à une couche cachée avec un nombre fini N de neurones, des poids wij*w*, des biais bj et une fonction d'activation σ tel que :

  sup⁡ x∈[0,1]n ∣f(x)−∑j=1->N vjσ  (∑i=1->n   wijxi+bj)∣<ϵ 

- **Définition** : 

  Ce théorème établit qu'un réseau de neurones à une seule couche cachée peut approximer avec une précision arbitraire toute fonction continue sur un compact, pourvu qu'il ait suffisamment de neurones dans cette couche cachée.

- **Démonstration (esquisse)** : 

  La preuve utilise la théorie de l'analyse fonctionnelle et le théorème de Stone-Weierstrass. Elle montre que l'ensemble des combinaisons linéaires de translations de la fonction d'activation forme un sous-algèbre dense dans l'espace des fonctions continues.

- **Exemple** : 

  Un réseau avec une seule couche cachée de 100 neurones utilisant la sigmoïde comme fonction d'activation peut approximer n'importe quelle fonction continue de deux variables sur [0,1]² avec une erreur inférieure à 0.01.

- **Rôle dans les LLMs / Deep Learning** :

  - **LLMs** : 

    Ce théorème justifie théoriquement l'utilisation des réseaux de neurones feed-forward dans les transformeurs. Bien que les LLMs utilisent une architecture spécifique (transformeurs avec attention), leurs composants fondamentaux sont des réseaux de neurones qui bénéficient de cette propriété d'universalité.

  - **Général** : 

    Il explique pourquoi les réseaux de neurones peuvent modéliser des relations complexes dans les données, qu'elles soient linéaires ou non.