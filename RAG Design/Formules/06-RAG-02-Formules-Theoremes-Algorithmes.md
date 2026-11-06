# 06-RAG — 02-Formules, Théorèmes et Algorithmes

**Leçon longue pour AI Software Engineer — Aurélien Hamzaoui**

## Introduction narrative : pourquoi ces formules changent la donne dans un vrai projet

Imagine que tu travailles sur le projet d’assurance automobile dont tu parles dans ton CV. Un assuré décrit un sinistre en quelques phrases : « J’ai percuté un poteau en reculant sur un parking souterrain à Lyon, mon pare-chocs avant est enfoncé et la caméra de recul ne fonctionne plus. » L’agent IA doit retrouver, parmi des milliers de clauses de contrat, de procédures internes et de jurisprudences, les éléments exacts qui permettent de décider si le sinistre est couvert, quel est le plafond, et quelles pièces justificatives demander. Sans une bonne mesure de similarité sémantique, l’agent va soit rater la clause pertinente, soit noyer la réponse dans du bruit. C’est précisément ici que la similarité cosinus et les métriques de retrieval deviennent des outils quotidiens, pas des abstractions académiques.

Dans le contexte de StaffMind, le même problème se pose pour les règles d’onboarding RH multi-pays : un recruteur demande « quelles sont les obligations de déclaration pour un contrat temporaire au Royaume-Uni pour un salarié déjà résident fiscal français ? ». L’agent doit récupérer les bons fragments de documentation conformité avant de proposer la suite. Les formules que nous allons détailler sont le socle de cette capacité.

## Définition du rôle de la similarité dans le RAG

Le Retrieval-Augmented Generation repose sur trois étapes fondamentales : l’indexation (transformation des documents en vecteurs), la récupération (trouver les vecteurs les plus proches de la requête) et la génération (le LLM utilise les passages récupérés). La qualité de la récupération dépend quasi entièrement de la fonction de similarité choisie. Pour le texte, la similarité cosinus s’est imposée parce qu’elle ignore la magnitude (la longueur du vecteur) et ne regarde que la direction, ce qui est pertinent lorsque des chunks de longueurs très différentes parlent du même sujet.

## Formule centrale : similarité cosinus

Soit deux vecteurs d’embeddings \(\mathbf{a}, \mathbf{b} \in \mathbb{R}^n\). La similarité cosinus est définie par :

$$
\cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \|\mathbf{b}\|} = \frac{\sum_{i=1}^{n} a_i b_i}{\sqrt{\sum_{i=1}^{n} a_i^2} \cdot \sqrt{\sum_{i=1}^{n} b_i^2}}
$$
où \(\theta\) est l’angle entre les deux vecteurs, \(\cdot\) désigne le produit scalaire, et \(\|\cdot\|\) la norme euclidienne. Le résultat appartient toujours à l’intervalle \([-1, 1]\). En pratique, avec les embeddings de texte modernes, les valeurs négatives sont rares ; on observe plutôt des scores entre 0 et 1.

### Lettres grecques et notations importantes

- \(\theta\) (thêta) : l’angle entre les vecteurs.
- \(\mathbf{a}, \mathbf{b}\) : vecteurs en gras.
- \(\|\mathbf{a}\|\) : norme L2 de \(\mathbf{a}\).
- Parfois on note \(\operatorname{sim}(\mathbf{a}, \mathbf{b})\) pour désigner cette similarité.

### Démonstration pas à pas avec des nombres

Prenons un exemple simplifié à trois dimensions, comme on le ferait lors d’un debug ou d’un atelier technique.

Vecteur requête \(\mathbf{q} = [0.8, 0.3, 0.5]\)  
Vecteur document \(\mathbf{d} = [0.7, 0.4, 0.6]\)

1. Produit scalaire :  
   $$
   \mathbf{q} \cdot \mathbf{d} = 0.8 \times 0.7 + 0.3 \times 0.4 + 0.5 \times 0.6 = 0.56 + 0.12 + 0.30 = 0.98
   $$
   
   
2. Norme de \(\mathbf{q}\) :  
   $$
   \|\mathbf{q}\| = \sqrt{0.8^2 + 0.3^2 + 0.5^2} = \sqrt{0.64 + 0.09 + 0.25} = \sqrt{0.98} \approx 0.990
   $$
   
   
3. Norme de \(\mathbf{d}\) :  
   $$
   \|\mathbf{d}\| = \sqrt{0.7^2 + 0.4^2 + 0.6^2} = \sqrt{0.49 + 0.16 + 0.36} = \sqrt{1.01} \approx 1.005
   $$
   
   
4. Similarité :  
   $$
   \cos(\theta) = \frac{0.98}{0.990 \times 1.005} \approx \frac{0.98}{0.995} \approx 0.985
   $$
   

Un score de 0.985 indique une très forte proximité sémantique. Dans un vrai système d’assurance, cela pourrait correspondre à une clause « dommages matériels sur parking » parfaitement alignée avec la description du sinistre.

## Algorithmes de retrieval détaillés

### Algorithme 1 : Recherche par similarité cosinus (naïve)

1. Encoder la requête utilisateur en vecteur \(\mathbf{q}\).
2. Pour chaque document (ou chunk) de la base, encoder en \(\mathbf{d}_i\).
3. Calculer \(\operatorname{sim}(\mathbf{q}, \mathbf{d}_i)\) pour tous les \(i\).
4. Trier les documents par score décroissant.
5. Retourner les top-\(k\) (souvent \(k = 3\) à \(10\)).

Complexité : \(
$$
O(N \cdot d)
$$
\) où \(N\) est le nombre de chunks et \(d\) la dimension. En production on utilise des index approximatifs (HNSW, IVF) pour réduire cela à du quasi-logarithmique.

### Algorithme 2 : Hybrid search (BM25 + cosine)

Beaucoup de systèmes réels combinent recherche lexicale et sémantique :

1. Calculer un score BM25 (ou TF-IDF) pour chaque document.

2. Calculer le score cosinus.

3. Normaliser les deux scores (souvent min-max ou z-score).

4. Combiner avec un poids \(\alpha\) :  
   $$
   \text{score final} = \alpha \cdot \text{score}_{\text{cosine}} + (1 - \alpha) \cdot \text{score}_{\text{BM25}}
   $$
   
   
5. Reranker éventuel (cross-encoder) sur les top-50.

Dans un contexte BTP (VerifactureBTP), le BM25 est excellent pour les termes techniques précis (« facturation électronique », « Chorus Pro »), tandis que le cosinus capture les reformulations.

## Métriques d’évaluation du retrieval

### Recall@k

$$
\text{Recall@}k = \frac{|\{\text{documents pertinents}\} \cap \{\text{top-}k\}|}{|\{\text{documents pertinents}\}|}
$$



### Precision@k

$$
\text{Precision@}k = \frac{|\{\text{documents pertinents}\} \cap \{\text{top-}k\}|}{k}
$$



### Mean Reciprocal Rank (MRR)

Pour un ensemble de requêtes \(Q\) :

$$
\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\operatorname{rank}_i}
$$
où \(\operatorname{rank}_i\) est le rang du premier document pertinent pour la requête \(i\).

Ces métriques se calculent sur un jeu de tests construit à partir de cas réels : sinistres annotés, tickets RH, devis BTP, etc.

## Cas d’usage réels racontés en détail

### Cas 1 — Sinistre automobile (projet assurance)

Un assuré appelle ou remplit un formulaire. L’agent doit décider en quelques secondes s’il peut proposer une indemnisation automatique ou s’il faut escalader vers un gestionnaire. Le RAG interroge la base de clauses. Si le score cosinus du meilleur chunk est supérieur à 0.85 et que la Faithfulness de la réponse générée dépasse 0.9, l’agent peut avancer. Sinon, il demande des précisions ou passe la main. Dans ton architecture hexagonale, le port de retrieval est isolé ; le domaine (règles de couverture) reste pur.

### Cas 2 — Onboarding RH multi-pays (StaffMind)

Un collaborateur en Australie pose une question sur les congés payés et la déclaration fiscale. Le système récupère les procédures locales, les calcule avec les règles du domaine (DDD), et laisse une trace. La similarité cosinus permet de retrouver la bonne procédure même si l’utilisateur emploie des synonymes (« annual leave » vs « congés annuels »).

### Cas 3 — Facturation électronique BTP

Un artisan demande comment émettre une facture conforme pour un marché public. Le RAG cherche dans les guides officiels et les exemples de factures passées. Un bon Recall@5 garantit que le bon modèle de facture est parmi les cinq premiers résultats présentés à l’agent.

### Cas 4 — Contexte sensible (Banque de France / Ministère de l’Intérieur)

Ici la similarité seule ne suffit pas. On ajoute des filtres de sécurité (garde-fous) avant même le calcul de similarité : seuls les documents autorisés pour le profil de l’utilisateur sont indexés ou filtrés. Le score cosinus est ensuite calculé uniquement sur ce sous-ensemble.

## Implémentation Java (extrait réaliste)

```java
public final class CosineSimilarity {
    public static double compute(double[] a, double[] b) {
        if (a.length != b.length) {
            throw new IllegalArgumentException("Dimensions must match");
        }
        double dot = 0.0;
        double normA = 0.0;
        double normB = 0.0;
        for (int i = 0; i < a.length; i++) {
            dot += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }
        double denom = Math.sqrt(normA) * Math.sqrt(normB);
        return denom == 0.0 ? 0.0 : dot / denom;
    }
}
```

Dans une architecture hexagonale, cette classe vit dans un adapter d’infrastructure ; le domaine ne connaît que le port `RetrievalPort`.

## À retenir pour la suite

La similarité cosinus est le cœur mathématique du RAG pratique. Maîtriser sa formule, ses propriétés (invariance à la magnitude) et ses métriques d’évaluation (Recall@k, MRR) te permet de diagnostiquer rapidement pourquoi un agent « ne trouve pas » la bonne information. Les cas métier que tu connais déjà (assurance, RH, BTP, secteur public) sont les meilleurs terrains d’expérimentation.

Prochaine leçon recommandée : démonstrations d’implémentation complète ou métriques RAGAS dans le dossier Evaluation.
