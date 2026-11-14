# Étape 37 — Transformer : formules qui manquaient au chapitre d'attention

> Étape 37 du parcours · Prérequis : [Encodeur, attention croisée et embeddings](<36c-Encodeur-Attention-Croisee-et-Embeddings.md>) · Suite : [Planification : définitions](<../07-Planification/37b-Planification-Definitions-Fondamentaux.md>) (étape 37 bis)

Le chapitre 06 ne contient que l'attention à une tête : QKᵀ / √dₖ, puis softmax, puis mélange des valeurs. Trois mécanismes manquent pour qu'un agent lise vraiment une phrase. Ils sont racontés avec le code, ligne par ligne, dans trois fichiers :

- [34-Attention-Multi-Tetes.md](<34-Attention-Multi-Tetes.md>) — plusieurs questions en parallèle (étape 34)
- [35-Encodage-de-Position.md](<35-Encodage-de-Position.md>) — l'ordre des mots (étape 35)
- [36-Normalisation-de-Couche.md](<36-Normalisation-de-Couche.md>) — l'échelle qui ne doit pas exploser (étape 36)

Ce fichier dit ce que chacun change dans le calcul, et pourquoi l'attention seule ne suffit pas.

## Plusieurs têtes

Une tête répond à « à qui ce token ressemble-t-il ? » et fabrique une seule moyenne. Dans « le contrat expire demain, il est signé », « il » doit retrouver à la fois le contrat et le verbe. Une moyenne unique mélange les deux réponses.

On coupe la largeur `d_model` en h bandes. Avec 512 et 8 têtes, chaque bande fait 64. Chaque tête a ses propres morceaux de `W_Q`, `W_K` et `W_V`, calcule son attention avec √64 et pas √512, puis on recolle les bandes et `W_O` les mélange. Huit têtes de 64 font le même nombre de multiplications, 2·n²·d, qu'une tête de 512, et les quatre matrices comptent toujours 4·d² paramètres. On n'a pas payé huit fois les produits scalaires : on a posé huit questions dans le même budget de calcul. En revanche, il y a huit matrices de scores n × n au lieu d'une, donc huit fois plus d'exponentielles et de mémoire de scores si on les stocke ; et les projections ajoutent 4·n·d² multiplications, qui dominent pour les textes de moins de 2·d tokens (étape 34).

Le masque causal met à −∞ les tokens futurs. Après softmax, leur poids vaut exactement 0. Sans ce masque, un agent qui écrit le token 5 lirait déjà le token 6.

## La position

L'attention ne voit pas l'ordre des lignes. Permuter les tokens permute les lignes du résultat, pas les produits scalaires entre vecteurs. « le chien mord l'homme » et « l'homme mord le chien » se ressembleraient.

On ajoute donc au vecteur du mot un vecteur de position fait de sinus et de cosinus. Les premières coordonnées oscillent **vite** : la paire i = 0 fait un tour complet en 2π ≈ 6,28 tokens. Les dernières oscillent **lentement** : pour d = 512, la dernière paire met environ 60 611 tokens à faire un tour. L'ancienne version de ce fichier disait l'inverse ; c'est corrigé (démonstration à l'étape 35). Deux mots voisins se distinguent sur les ondes rapides. Deux mots loin l'un de l'autre se distinguent déjà sur les ondes lentes. On additionne ce vecteur à l'embedding, on ne le concatène pas : la position et le sens habitent les mêmes cases, et les matrices `W_Q`, `W_K` apprennent lesquelles regarder.

`exp(-log(10000) * 2i / d)` dans le code est exactement 10000^(−2i/d). Ce n'est pas une formule différente : c'est la division du cours, écrite sous une autre forme. L'ancienne version ajoutait « écrite pour ne pas sous-déborder » ; c'est faux. Le plus petit facteur, pour d = 512, vaut environ 1,04 × 10⁻⁴, très loin de tout sous-débordement ; la forme `exp`/`log` est seulement un procédé de calcul commode, qui produit toutes les fréquences d'un coup.

## La normalisation

Chaque couche multiplie. Les coordonnées gonflent, les produits scalaires saturent la softmax, le gradient disparaît. Pour chaque token, on retranche la moyenne de ses coordonnées et on divise par l'écart-type, avec un ε sous la racine pour le cas où toutes les cases sont égales : sans lui, le calcul donnerait 0/0, c'est-à-dire NaN. γ et β, appris, rendent ensuite le droit d'étaler à nouveau. On calcule cette moyenne sur les coordonnées du token, pas sur les phrases du lot : un agent seul, à l'inférence, voit la même normalisation qu'à l'entraînement.

Sur [2 ; 0 ; 4 ; 2], la moyenne vaut 2, la variance (divisée par 4, pas par 3) vaut 2, et le vecteur normalisé vaut environ [0 ; −1,41 ; 1,41 ; 0]. RMSNorm, utilisé par Llama, ne retranche pas la moyenne et n'a pas de β. Il divise par la racine de la moyenne des carrés.

Le détail de chaque ligne PyTorch, le `view`, le `transpose`, le `contiguous`, le `unbiased=False`, est dans les trois fichiers cités plus haut.

> Suite : [Planification : définitions](<../07-Planification/37b-Planification-Definitions-Fondamentaux.md>) — étape 37 bis.
