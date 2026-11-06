# 11-Evaluation — 02-Formules, Théorèmes et Algorithmes

**Leçon longue — Métriques mathématiques pour évaluer agents et RAG**

## Introduction narrative : pourquoi mesurer avec des formules précises

Tu as déjà construit des agents qui qualifient une demande, proposent une suite et laissent une trace (StaffMind). En production, la question n’est plus « est-ce que ça marche sur mon ordinateur ? » mais « est-ce que ça reste fiable après 10 000 requêtes, avec des utilisateurs qui reformulent, des documents qui changent, et des règles métier qui évoluent ? ». Les formules d’évaluation (Faithfulness, Answer Relevancy, Precision, Recall, F1, ToolCallAccuracy) donnent des chiffres objectifs que tu peux mettre dans une pipeline CI/CD, exactement comme tu le faisais avec les tests Selenium ou GitLab CI à la Banque de France ou chez GE.

Sans ces métriques, on se contente de « ça a l’air bien ». Avec elles, on peut dire : « le Faithfulness est tombé de 0.92 à 0.71 après le dernier changement de prompt ; on bloque le déploiement ».

## Définitions des rôles des métriques

- **Faithfulness** : la réponse invente-t-elle des faits non présents dans le contexte récupéré ?
- **Answer Relevancy** : la réponse répond-elle vraiment à la question posée ?
- **Context Precision / Recall** : le retriever a-t-il ramené les bons morceaux, et bien classés ?
- **ToolCallAccuracy / F1** : l’agent a-t-il appelé les bons outils avec les bons paramètres ?
- **AgentGoalAccuracy** : l’objectif métier a-t-il été atteint (binaire) ?

Ces métriques se combinent pour diagnostiquer si le problème vient du retrieval, de la génération, ou du choix d’outils.

## Formules mathématiques détaillées (RAGAS et au-delà)

### 1. Faithfulness

On extrait un ensemble de claims (affirmations atomiques) \(S\) de la réponse générée. Un juge (souvent un LLM) détermine le sous-ensemble \(V \subseteq S\) de claims supportées par le contexte récupéré.

$$
\text{Faithfulness} = \frac{|V|}{|S|}
$$
Si \(|S| = 0\), le score est indéfini (on évite la division par zéro). Un score de 1.0 signifie que chaque affirmation est déductible du contexte ; 0.0 signifie que rien n’est supporté (hallucination pure).

**Exemple concret** :  
Réponse : « Le plafond de garantie pour un choc sur parking est de 1 500 € et la franchise est de 300 €. »  
Claims :  
- « plafond = 1 500 € » → supporté  
- « franchise = 300 € » → non supporté (hallucination)  

Faithfulness = 1/2 = 0.5

### 2. Answer Relevancy

On génère \(n\) questions hypothétiques à partir de la réponse, on calcule leur embedding, puis la similarité cosinus moyenne avec l’embedding de la question originale.

$$
\text{Answer Relevancy} = \frac{1}{n} \sum_{i=1}^{n} \cos(E_{g_i}, E_o) = \frac{1}{n} \sum_{i=1}^{n} \frac{E_{g_i} \cdot E_o}{\|E_{g_i}\| \|E_o\|}
$$
où \(E_{g_i}\) est l’embedding de la i-ème question générée et \(E_o\) celui de la question originale. On utilise souvent \(n = 3\) à 5.

### 3. Precision, Recall et F1 classiques

Pour un ensemble de prédictions :

$$
\text{Precision} = \frac{TP}{TP + FP}, \quad
\text{Recall} = \frac{TP}{TP + FN}, \quad
F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}
$$
Appliqué aux appels d’outils : un appel est un True Positive s’il correspond exactement (nom + paramètres) à un appel attendu.

### 4. Context Precision (version RAGAS simplifiée)

On ordonne les chunks récupérés. Pour chaque rang \(k\), on calcule Precision@k multipliée par un indicateur de pertinence \(v_k \in \{0,1\}\), puis on moyenne :

$$
\text{Context Precision} = \frac{\sum_{k=1}^{K} (\text{Precision@}k \cdot v_k)}{\sum_{k=1}^{K} v_k}
$$


### 5. ToolCall F1

Similarité ensembliste entre appels attendus et appels réels (ordre ignoré) :

$$
\text{Precision}_{\text{tools}} = \frac{|\text{appels corrects}|}{|\text{appels corrects}| + |\text{appels en trop}|}
$$

$$
\text{Recall}_{\text{tools}} = \frac{|\text{appels corrects}|}{|\text{appels corrects}| + |\text{appels manquants}|}
$$

Puis F1 classique.

## Algorithmes d’évaluation pas à pas

### Algorithme Faithfulness

1. Recevoir question, contexte récupéré, réponse générée.
2. Demander à un LLM d’extraire les claims atomiques de la réponse (liste de phrases courtes).
3. Pour chaque claim, demander au même (ou un autre) LLM : « Ce claim est-il déductible du contexte ? Oui/Non + justification ».
4. Compter le nombre de Oui → \(|V|\).
5. Calculer \(|V| / |S|\).
6. Logger les claims non supportés pour analyse humaine.

### Algorithme Answer Relevancy

1. À partir de la réponse, générer \(n\) questions possibles.
2. Encoder ces questions et la question originale avec le même modèle d’embedding.
3. Calculer les \(n\) similarités cosinus.
4. Faire la moyenne.

Ces algorithmes sont déterministes une fois le juge fixé, ce qui permet des tests de régression.

## Cas d’usage réels racontés

### Cas StaffMind — Qualification d’une demande RH

Un utilisateur écrit : « Je veux savoir si mon contrat australien me permet de prendre des congés avant la fin de la période d’essai. »  
L’agent appelle un outil de recherche de politique, récupère le bon document, et répond.  
On mesure :
- ToolCallAccuracy : a-t-il appelé le bon outil avec le bon pays ?
- Faithfulness : la réponse ne contient-elle que des règles présentes dans le document récupéré ?
- AgentGoalAccuracy : l’utilisateur a-t-il obtenu une réponse actionnable (oui/non + conditions) ?

Si le Faithfulness chute après un changement de prompt système, on refuse le déploiement.

### Cas VerifactureBTP — Génération de facture

L’agent doit produire une facture électronique conforme. On évalue si tous les champs obligatoires (mentions légales, TVA, références marché public) sont présents et corrects. On peut définir une métrique custom « Completeness » en plus des métriques RAGAS.

### Cas Assurance — Décision de couverture

On construit un golden set de 50 sinistres annotés. Pour chaque sinistre, on connaît la décision attendue et les clauses pertinentes. On calcule Recall@5 du retrieval et Faithfulness de la justification générée. Un seuil de 0.90 sur les deux métriques est exigé avant mise en production.

### Cas Banque de France / Ministère

Dans ces contextes, on ajoute des métriques de sécurité : taux de fuite d’information sensible, respect des politiques d’accès. La Faithfulness reste critique pour éviter les hallucinations sur des sujets réglementaires.

## Implémentation de la formule Faithfulness (pseudo-code)

```java
public double faithfulness(List<String> claims, Predicate<String> isSupported) {
    if (claims.isEmpty()) return Double.NaN;
    long supported = claims.stream().filter(isSupported).count();
    return (double) supported / claims.size();
}
```

Le prédicat `isSupported` encapsule l’appel au juge LLM.

## À retenir

Les formules d’évaluation transforment des impressions qualitatives en chiffres actionnables. Faithfulness et Answer Relevancy sont les deux métriques les plus utiles au quotidien pour un agent en production. Combinées à ToolCallAccuracy, elles permettent de localiser rapidement le maillon faible (retrieval, génération, ou choix d’outil). Dans ton expérience de livraison en équipe (Banque de France, Ministère), ces métriques jouent le même rôle que les tests d’intégration : elles protègent la qualité avant le passage en production.

Prochaine étape : construire un petit golden set à partir de cas réels de tes projets et calculer ces scores.
