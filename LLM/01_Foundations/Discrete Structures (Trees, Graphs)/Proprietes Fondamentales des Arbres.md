### 4.1 Propriétés Fondamentales des Arbres

**Définition** : Un arbre est un graphe connexe acyclique. Formellement, un graphe G=(V,E) est un arbre si :

1. G est connexe
2. G ne contient aucun cycle
3. ∣E∣=∣V∣−1 (relation fondamentale)

**Théorème** : Tout arbre binaire avec n*n* nœuds possède exactement n+1 feuilles (branches externes) et n−1 branches internes.

**Démonstration par récurrence** :

- **Base** : 

  Pour n=1 (seulement la racine), il y a 2 feuilles et 0 branches internes. Vérifié.

- **Hypothèse** : 

  Supposons vrai pour tout arbre avec k<n nœuds.

- Étape : 

  Considérons un arbre avec n nœuds. En supprimant une feuille, on obtient un arbre avec n−1 nœuds qui, par hypothèse, a (n−1)+1=n feuilles et (n−1)−1=n−2

   branches internes. En rajoutant la feuille supprimée, on remplace une feuille par un nœud interne et deux nouvelles feuilles, donc :

  - Nouveau nombre de feuilles : n−1+2=n+1
  - Nouveau nombre de branches internes : (n−2)+1=n−1

**Exemple** : 

Un arbre de décision pour classifier des emails (spam/non-spam) basé sur des caractéristiques comme la présence de certains mots-clés, la longueur du message, etc.

**Rôle dans les LLMs et l'IA** :

- Les arbres de décision (Random Forests, Gradient Boosting) pour les tâches de classification
- L'analyse syntaxique (parsing) dans le traitement du langage naturel
- La recherche dans les espaces d'états (algorithmes A*, minimax)
- Les structures de données pour l'indexation et la recherche efficace