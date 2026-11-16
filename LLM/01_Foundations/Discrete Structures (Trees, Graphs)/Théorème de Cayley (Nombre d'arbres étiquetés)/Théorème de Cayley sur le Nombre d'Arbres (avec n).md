### 2.1 Théorème de Cayley sur le Nombre d'Arbres (avec *n*)

**Définition** : Le nombre d'arbres étiquetés avec n sommets est égal à n^(n−2).

**Démonstration par double comptage** :

- Soit Tn le nombre d'arbres étiquetés à n sommets.
- Chaque arbre a n−1 arêtes.
- On peut construire une bijection entre les arbres étiquetés et les suites de Prüfer de longueur n−2.
- Chaque position dans la suite de Prüfer peut prendre n valeurs (les étiquettes des sommets).
- Donc le nombre total de suites est n^(n−2).
- Par bijection, Tn=n^(n−2).

**Exemple** : 

Pour n=4 sommets : 

T4=4^(4−2)=4²=16 arbres differents

Pour n=5: 

T5=5^(5−2)=5^3=125 arbres differents

**Application aux algorithmes** : 

Ce théorème est crucial pour comprendre la complexité des algorithmes de recherche exhaustive dans les arbres, comme les algorithmes de branch-and-bound pour l'optimisation combinatoire.