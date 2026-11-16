## **Théorème de Représentation de Kolmogorov-Arnold**

*Précurseur théorique des réseaux de neurones.*

- **Énoncé formel** : Toute fonction continue f:[0,1]n→R peut s'écrire comme composition finie de fonctions continues d'une seule variable et de l'addition :

  f(x1,...,xn)=∑q=1 vers 2n+1 Φq (∑ p=1 vers n ϕq,p(xp))

  où ϕq,p:[0,1]→R et Φq:R→R sont des fonctions continues.

- **Définition** : 

  Ce théorème montre que toute fonction multivariée peut être décomposée en une somme de fonctions d'une seule variable, anticipant l'idée des réseaux de neurones.

- **Démonstration (esquisse)** : 

  La preuve originale est constructive mais complexe, utilisant des partitions de l'unité et des fonctions d'interpolation.

- **Exemple** : 

  Une fonction de deux variables f(x,y)*f*(*x*,*y*) peut être représentée comme f(x,y)=Φ1(ϕ1,1(x)+ϕ1,2(y))+Φ2(ϕ2,1(x)+ϕ2,2(y))+Φ3(ϕ3,1(x)+ϕ3,2(y))*f*(*x*,*y*).

- **Rôle dans les LLMs** :

  - **Perspective historique** : 

    Bien que non directement utilisée dans les LLMs modernes, ce théorème a inspiré le développement précoce des réseaux de neurones en montrant que des fonctions complexes peuvent être construites à partir de fonctions simples.

  - **Compréhension théorique** : 

    Il offre une perspective alternative sur la représentation des fonctions, complémentaire au théorème d'universalité.