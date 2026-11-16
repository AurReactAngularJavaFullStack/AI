### 1. Théorème : La Règle de la Chaîne (Chain Rule)

C'est le mécanisme de base de l'auto-régression (le fait de prédire le mot suivant basé sur les précédents).

#### 📐 Définition

En probabilités, la règle de la chaîne permet de calculer la probabilité conjointe d'une séquence d'événements en la décomposant en une série de probabilités conditionnelles.

Dans le contexte d'un LLM, cela signifie que la probabilité d'une phrase entière est le produit de la probabilité de chaque mot, sachant tous les mots qui l'ont précédé.

#### 📜 Le Théorème (Formule)

Soit une séquence d'événements (ou de mots) notée X1, X2, ..., Xn.

La probabilité conjointe P(X1, X2, ..., Xn) est donnée par :

P(X.1, \..., X.n) = P(X1) . P(X2 | X1) . P(X3 | X1, X2) . \... . P(Xn | X1, \..., X.{n-1}).

On peut l'écrire de façon compacte avec le symbole Pi majuscule (.\Pi.) qui signifie "produit" :

P(X.1, \..., X.n) = s Sigma{i=1}^{n} P(X.i | X.1, \..., X.{i-1}).

```math
$$P(X_1, \dots, X_n) = \prod_{i=1}^{n} P(X_i | X_1, \dots, X_{i-1})$$
```

```math
$$P(X_1, \dots, X_n) = \prod_{i=1}^{n} P(X_i | X_1, \dots, X_{i-1})$$
```



#### 🎓 Démonstration (Intuition Logique)

Imaginons que nous voulons vérifier la probabilité que les événements .A. et .B. se produisent ensemble (.A \cap B.).

D'après la définition de la probabilité conditionnelle :



..P(B | A) = \frac{P(A \cap B)}{P(A)}..

En multipliant les deux côtés par .P(A)., on obtient :



..P(A \cap B) = P(A) . P(B | A)..

Si on ajoute un troisième événement .C., on applique la même logique en considérant .(A \cap B). comme un seul bloc historique :



..P(A \cap B \cap C) = P(A \cap B) . P(C | A, B)..

En remplaçant .P(A \cap B). par ce qu'on a trouvé plus haut, on obtient la chaîne :



..P(A \cap B \cap C) = P(A) . P(B | A) . P(C | A, B)..

C'est récursif, comme une boucle en Java.

![Tree DIagram Proba](D:\Users\aur95\Documents\Clean_Architecture_2\LLM\Softmax, gradients et backprop (le moteur sous le capot)\Règle de la chaîne (version dérivées) = fondation du backprop\Tree DIagram Proba.jfif)

#### 🏫 Exemple Concret

Calculons la probabilité que le modèle génère la phrase : **"L'IA est le futur"**.

1. Probabilité de commencer par "L'IA" : .P(\text{"L'IA"}).
2. Probabilité d'avoir "est" sachant qu'on a "L'IA" : .P(\text{"est"} | \text{"L'IA"}).
3. Probabilité d'avoir "le" sachant "L'IA est" : .P(\text{"le"} | \text{"L'IA est"}).
4. Probabilité d'avoir "futur" sachant "L'IA est le" : .P(\text{"futur"} | \text{"L'IA est le"}).

La probabilité totale de la phrase est la multiplication de ces 4 nombres.

#### 🧠 Rôle dans les LLMs

Ce théorème est la raison d'être de l'architecture "Decoder-only" (comme GPT).

- **L'arbre algorithmique :** À chaque étape (chaque mot), le modèle fait face à un embranchement (un nœud dans un arbre) avec des milliers de choix possibles (le vocabulaire).
- **La sélection :** Le modèle calcule .P(X.i | \text{contexte}). pour toutes les branches possibles et choisit la branche la plus probable (ou en tire une au sort).