# 02-Formules-Theoremes-Algorithmes.md

**Dossier : 06-RAG**  
**Priorité : Haute (mathématiques essentielles pour un AI Software Engineer)**

## 1. Similarité cosinus (formule centrale)

La similarité cosinus mesure l'angle entre deux vecteurs d'embeddings, indépendamment de leur magnitude. C'est la métrique standard pour le retrieval sémantique.

$$
\cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \|\mathbf{b}\|} = \frac{\sum_{i=1}^{n} a_i b_i}{\sqrt{\sum_{i=1}^{n} a_i^2} \cdot \sqrt{\sum_{i=1}^{n} b_i^2}}
$$

- Résultat ∈ [-1, 1]
- 1 = identiques (même direction)
- 0 = orthogonaux (pas de relation)
- -1 = opposés (rare en pratique avec les embeddings de texte)

### Exemple numérique simple

Vecteur requête 
$$
\mathbf{q} = [0.8, 0.3, 0.5]
$$

Vecteur document \(
$$
\mathbf{d}
$$
 = [0.7, 0.4, 0.6]\)

1. $$
   Dot product : (0.8 \times 0.7 + 0.3 \times 0.4 + 0.5 \times 0.6 = 0.56 + 0.12 + 0.30 = 0.98)
   $$

   

2. $$
   \|\mathbf{q}\| = \sqrt{0.64 + 0.09 + 0.25} = \sqrt{0.98} \approx 0.990
   $$

   

3. $$
   \|\mathbf{d}\| = \sqrt{0.49 + 0.16 + 0.36} = \sqrt{1.01} \approx 1.005
   $$

   

4. $$
   \cos(\theta) = 0.98 / (0.990 \times 1.005) \approx 0.985
   $$

   

→ Document très pertinent.

## 2. Autres métriques de retrieval

### Recall@k

Proportion des documents pertinents récupérés parmi les k premiers :

$$
\text{Recall@k} = \frac{|\text{pertinents} \cap \text{top-k}|}{|\text{pertinents}|}
$$

### Precision@k

$$
\text{Precision@k} = \frac{|\text{pertinents} \cap \text{top-k}|}{k}
$$

### Mean Reciprocal Rank (MRR)

$$
\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}
$$

où \(\text{rank}_i\) est le rang du premier document pertinent pour la requête \(i\).

## 3. Faithfulness (pour l'évaluation RAG)

$$
\text{Faithfulness} = \frac{\text{nombre de claims supportées par le contexte}}{\text{nombre total de claims dans la réponse}}
$$

Utilisé dans RAGAS et les frameworks d'évaluation.

## 4. Implémentation minimale (pseudo-code / Java-friendly)

```java
public double cosineSimilarity(double[] a, double[] b) {
    double dot = 0.0, normA = 0.0, normB = 0.0;
    for (int i = 0; i < a.length; i++) {
        dot += a[i] * b[i];
        normA += a[i] * a[i];
        normB += b[i] * b[i];
    }
    return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}
```

## 5. Cas d'usage métier (tirés de ton profil)

- **Assurance auto** : Retrieval de clauses de contrat / procédures de sinistre à partir d'une description de l'assuré.
- **Facturation BTP (VerifactureBTP)** : Recherche de règles de facturation électronique ou de modèles de devis.
- **RH multi-pays (StaffMind)** : Retrieval de règles de conformité, de templates d'onboarding, de politiques locales.
- **Secteur public / Banque de France** : Recherche dans des référentiels réglementaires sensibles (avec garde-fous).

## À retenir

- La similarité cosinus est **invariante à la magnitude** → idéale pour des chunks de longueurs différentes.
- Toujours combiner avec un bon chunking et un reranker pour la production.
- Mesurer Recall@k et Faithfulness avant de déployer.

---

*Prochaine lecture recommandée : 03-Demonstrations-Implementations.md ou 04-Exemples-Cas-Usage.md*
