## 13. **Théorème de la Décomposition Biais-Variance**

*Cadre fondamental pour comprendre les sources d'erreur des modèles.*

- **Énoncé formel** : Pour un estimateur f^(x)*f*^(*x*) d'une fonction f(x)*f*(*x*) et une perte quadratique, l'erreur de généralisation se décompose en :

  E[(Y−f(X))²]=E[(f(X)−E[f(X)])²]+(E[f(X)]−f(X))²+Var(ϵ)

                               Variance                      Biais²         Erreur irreductible

- **Définition** : 

  Cette décomposition sépare l'erreur de prédiction en trois composantes : variance (sensibilité aux fluctuations d'échantillonnage), biais (erreur systématique) et bruit inhérent aux données.

- **Démonstration** : 

  Développement direct de l'espérance du carré de l'erreur, utilisant Y=f(X)+ϵ avec E[ϵ]=0.

- **Exemple** : 

  Un arbre de décision profond a un biais faible (il peut ajuster parfaitement les données d'entraînement) mais une variance élevée (il est très sensible au bruit). Une forêt aléatoire réduit la variance par moyennage.

- **Rôle dans les LLMs / Arbres** :

  - **Design d'architectures** : 

    Les LLMs doivent naviguer le compromis biais-variance : trop peu de paramètres → biais élevé ; trop de paramètres → variance élevée.

  - **Méthodes ensemblistes** : 

    Le bagging réduit principalement la variance, le boosting réduit principalement le biais.

  - **Régularisation** : 

    Dropout, weight decay, et early stopping contrôlent la variance dans les LLMs.