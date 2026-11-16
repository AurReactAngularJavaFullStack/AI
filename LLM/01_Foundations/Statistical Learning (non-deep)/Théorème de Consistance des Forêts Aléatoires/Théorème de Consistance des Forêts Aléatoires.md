## 6. **Théorème de Consistance des Forêts Aléatoires**

*Garantit la convergence des forêts aléatoires vers la vraie fonction de régression.*

- **Énoncé informel** : 

  Sous certaines conditions concernant la construction des arbres (e.g., profondeur croissante, fraction des variables testées), l'estimateur de forêt aléatoire r^n(x)*r*^*n*(*x*) converge en moyenne quadratique (consistance L2*L*2) vers la fonction de régression vraie r(x)*r*(*x*) lorsque la taille de l'échantillon n*n* tend vers l'infini.

- **Définition** : 

  La consistance est la propriété la plus fondamentale attendue d'un algorithme d'apprentissage. Ce théorème assure que, avec suffisamment de données, la prédiction d'une forêt aléatoire se rapproche arbitrairement de la valeur théorique optimale.

- **Démonstration (esquisse)** : 

  Les preuves décomposent généralement l'erreur en un terme de biais et un terme de variance. On montre que le biais diminue grâce à la richesse des partitions créées par les arbres, et que la variance diminue grâce à l'agrégation (moyennage) de nombreux estimateurs faiblement corrélés.

- **Exemple** : 

  Pour prédire le prix d'une maison en fonction de ses caractéristiques, une forêt aléatoire entraînée sur un très grand nombre d'exemples verra son erreur de prédiction se stabiliser et approcher l'erreur minimale théorique.

- **Rôle dans les Arbres Algorithmiques** : 

  Ce théorème est la **pierre angulaire théorique** justifiant l'utilisation pratique et massive des forêts aléatoires. 

  Il explique pourquoi l'agrégation de nombreux arbres de décision peu profonds ou bruités peut produire un estimateur puissant et stable, comblant ainsi le fossé entre la pratique et la théorie.