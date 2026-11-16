# Carte mentale — pourquoi cet ordre

> Image : `05_carte_mentale_justifications.jpg` · Détail chiffré : [sommaire](<00_Sommaire.md>).

## Ce que montre l'image

Huit dépendances. Chacune dit ce qui casse si l'on inverse les deux formules.

1. **Softmax avant le prompt.** Un taux de conformité juge des tokens. Ces tokens sortent de la softmax. À température nulle, ce n'est plus une softmax, c'est un argmax.
2. **Cosinus avant la mémoire.** Le score de pertinence prend le cosinus comme similarité. Sans lui, la récence n'a rien à pondérer. Le RAG s'en sert pour la même raison.
3. **BM25 après le sens.** Deux vecteurs proches peuvent rater le mot exact `REG-2` ou un IBAN. La recherche lexicale répare ce trou, elle ne remplace pas le cosinus.
4. **RRF après deux listes.** Un cosinus est dans \([-1,1]\), un score BM25 n'y est pas. Les additionner directement mélange des unités. RRF n'additionne que \(1/(60+\mathrm{rang})\).
5. **Juger avant de croire.** Rappel, précision, MRR et NDCG disent si le top-k est injectable. S'en passer, c'est remplir la fenêtre avec un classement non jugé.
6. **Attention après le contexte.** Elle répond à « quels tokens de ce prompt pèsent ». La question n'existe pas tant que le budget, la mémoire et le RAG n'ont rien mis dans la fenêtre. La division par \(\sqrt{d_k}\) vient avec elle.
7. **Bellman avant A\*.** \(f = g + h\) classe des étapes par un coût. Il ne dit pas si l'étape vaut le coup quand l'issue est aléatoire. Bellman le dit, parce qu'il prend l'espérance du gain futur actualisé.
8. **Garde-fou après le jugement.** Le score de risque consomme la fidélité, la perplexité et la KL. Les calculer après le veto, c'est bloquer sans signal. Adam vient encore plus tard : spécialiser un modèle dont la boucle n'existe pas n'a pas de perte à descendre.

## Ce que cette carte ne dit pas

Elle ne décrit pas le trajet d'une requête. Ce trajet, une fois l'agent écrit, reste : prompt, schéma, outil, boucle, mémoire et RAG, attention, plan, orchestration, MCP, évaluation, garde-fou. La carte dit dans quel ordre on *écrit* les formules.
