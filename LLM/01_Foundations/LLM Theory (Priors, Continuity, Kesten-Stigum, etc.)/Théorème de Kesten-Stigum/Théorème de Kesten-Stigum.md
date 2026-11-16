## 5. **Théorème de Kesten-Stigum**

*Décrit la croissance asymptotique des processus de branchement, pertinent pour les structures arborescentes.*

- **Énoncé informel** : 

  Pour un processus de branchement (arbre de Galton-Watson) sur-critique (espérance de reproduction m>1*m*>1), la suite normalisée Zn/m^n converge presque sûrement vers une variable aléatoire non dégénérée si et seulement si une condition du type E[Z1log⁡+Z1]<∞ est satisfaite.

- **Définition** : 

  Ce théorème donne une condition nécessaire et suffisante précise pour qu'un processus de branchement (modélisant la croissance d'une population ou d'une structure arborescente) croisse à un taux régulier et prévisible.

- **Démonstration (esquisse)** : 

  La preuve utilise des martingales et des théorèmes de convergence. La suite Wn=Zn/m^n est une martingale positive. Le théorème établit quand cette martingale converge vers une limite non nulle.

- **Exemple** : 

  Modélisation de la propagation d'une information dans un réseau social (arbre de diffusion). Le théorème indique sous quelles conditions le nombre de personnes touchées au temps n*n* croît proportionnellement à m^n.

- **Rôle dans les Arbres Algorithmiques** : 

  Bien qu'avancé, ce théorème est fondamental pour l'**analyse probabiliste des structures arborescentes**. 

  Il éclaire le comportement limite des algorithmes qui construisent ou parcourent des arbres de manière aléatoire, et est lié à l'étude des marches aléatoires sur les arbres.