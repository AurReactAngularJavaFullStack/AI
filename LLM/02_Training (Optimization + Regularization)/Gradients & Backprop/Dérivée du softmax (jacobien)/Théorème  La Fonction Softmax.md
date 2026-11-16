###  Théorème : La Fonction Softmax (.\sigma.)

Si la "Règle de la Chaîne" est le moteur logique, le **Softmax** est le convertisseur qui rend les données exploitables.

Dans ton code Java, imagine que ton réseau de neurones te renvoie un `float[]` avec des valeurs brutes bizarres, parfois négatives (appelées **logits**). Tu ne peux pas utiliser ça pour choisir un mot. Tu as besoin de pourcentages dont la somme fait 100% (ou 1.0).

#### 📐 Définition

La fonction Softmax est une fonction qui prend en entrée un vecteur de .K. nombres réels et le normalise en une distribution de probabilités composée de .K. probabilités.

#### 📜 La Formule

Soit un vecteur d'entrée .z = (z_1, \dots, z_K). (les logits).

La fonction Softmax .\sigma(z). pour le composant .i. est définie par :

sigma(z)_i = e^(zi)/sum de (j=1) vers K de e^(zj))

- **.z_i.** : Le score brut pour le mot .i..
- **.e^{z_i}.** : L'exponentielle du score (pour rendre tout positif).
- **.\sum e^{z_j}.** : La somme de toutes les exponentielles (le dénominateur commun pour normaliser).

#### 🎓 Démonstration (Intuition Algébrique)

Pourquoi cette formule spécifique ? Elle remplit deux conditions critiques pour un arbre de probabilités :

1. **Positivité stricte :** Une probabilité ne peut pas être négative.

   - La fonction exponentielle .f(x) = e^x. est toujours positive (.>0.), peu importe si l'entrée .z. est négative (ex: .-5.) ou positive.

2. **Somme égale à 1 :** La somme de toutes les branches doit faire 1.

   - En divisant chaque élément par la somme totale de tous les éléments, on garantit mathématiquement que :

   sum de {i=1} vers (K) de sigma(z)i = sum e^{zi}/sum e^{zj}} = 1.

#### 🏫 Exemple Concret (Calcul)

Imaginons que le LLM hésite entre 3 mots pour compléter la phrase "Je code en...".

Les logits (scores bruts sortant du réseau) sont :

- Java : .2.0.
- Python : .1.0.
- C++ : .0.1.

Appliquons le Softmax :

1. **Exponentielles :**
   - e^{2.0} = 7.39.
   - e^{1.0} = 2.72.
   - e^{0.1} = 1.10.
2. **Somme (Dénominateur) :**
   - .Sum = 7.39 + 2.72 + 1.10 = 11.21.
3. **Probabilités finales :**
   - .P(Java) = 7.39 / 11.21 = 0.66. (66%)
   - .P(Python) = 2.72 / 11.21 = 0.24. (24%)
   - .P(C++) = 1.10 / 11.21 = 0.10  (10%)

#### 🧠 Rôle dans les LLMs

C'est la toute dernière couche (Layer) du réseau de neurones.

- **Le sélecteur :** Sans Softmax, le modèle ne sort que du bruit numérique. Softmax transforme ce bruit en un classement clair.
- **La température :** C'est ici qu'on applique le paramètre "Température". On divise les logits z par T avant l'exponentielle (.e^{zi/T}.). Si T est élevé, cela lisse les différences (plus créatif/aléatoire). Si T est bas, cela accentue le leader (plus déterministe).