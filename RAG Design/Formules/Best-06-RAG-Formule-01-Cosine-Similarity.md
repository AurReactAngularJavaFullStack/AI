# 06-RAG — Formule 01 — Similarité Cosinus

**Dossier :** 06-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers, Product Engineers  

**Nom du fichier :** 06-RAG-Formule-01-Cosine-Similarity.md

## Définition complète de chaque élément de la formule

La similarité cosinus est la métrique centrale du retrieval sémantique dans les systèmes RAG. Elle mesure uniquement la direction des vecteurs d’embeddings, pas leur longueur.

$$
\cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \|\mathbf{b}\|} = \frac{\sum_{i=1}^{n} a_i b_i}{\sqrt{\sum_{i=1}^{n} a_i^2} \cdot \sqrt{\sum_{i=1}^{n} b_i^2}}
$$


### Définition de chaque symbole

- \(
  $$
  \theta
  $$
  \) : l’angle entre les deux vecteurs. Plus il est petit, plus les textes sont proches sémantiquement.

- \(
  $$
  \mathbf{a}, \mathbf{b}
  $$
  \) : vecteurs d’embeddings (requête et document).

- Produit scalaire \(
  $$
  \mathbf{a} \cdot \mathbf{b}
  $$
  \) : mesure l’alignement brut.

- Normes \(
  $$
  \|\mathbf{a}\|, \|\mathbf{b}\|
  $$
  \) : longueurs des vecteurs. La division les neutralise.

- \(n\) : dimension de l’espace.

### Comportement

Plus le produit scalaire augmente relativement aux normes, plus le score se rapproche de 1 (très pertinent).  
Plus les vecteurs divergent, plus le score baisse vers 0.

## Démonstration et interprétation

(Voir calculs précédents : score ≈ 0.985 → documents extrêmement proches.)

## Code Python

```python
import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))
```

## Cas d’usage métier maximum

**Finance / Banque** : Retrieval de clauses réglementaires ou de rapports de risque à partir d’une description de position. Un score élevé permet de remonter automatiquement la bonne politique de conformité.

**Immobilier** : Recherche de comparables de marché ou de diagnostics techniques à partir d’une description de bien (« appartement 3 pièces avec DPE C à Lyon »).

**Crypto** : Retrieval de passages de whitepapers ou de documentation de protocoles DeFi à partir d’une question sur les risques de liquidité.

**Bancaire / Crédit** : Trouver les règles internes d’octroi à partir d’un profil client.

**Assurance** : Clauses de contrat à partir d’une description de sinistre.

**RH** : Politiques de conformité multi-pays.

**BTP** : Guides de facturation électronique.

Dans tous ces domaines, un seuil de similarité cosinus (ex. > 0.82) sert de filtre avant de passer le contexte au LLM.
