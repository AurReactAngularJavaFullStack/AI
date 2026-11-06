# 06-RAG — Formule 05 — Score Hybride (Cosine + BM25)

**Dossier :** 06-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  

**Nom du fichier :** 06-RAG-Formule-05-Hybrid-Score.md

## Définition complète de chaque élément

Le score hybride combine recherche sémantique (cosine) et recherche lexicale (BM25) pour profiter des forces des deux approches.

$$
\text{score final} = \alpha \cdot \text{score}_{\text{cosine}} + (1 - \alpha) \cdot \text{score}_{\text{BM25 normalisé}}
$$


### Définition de chaque symbole

- $$
  \alpha
  $$

   : poids donné à la similarité cosinus (entre 0 et 1). Plus \(\alpha\) est proche de 1, plus on favorise le sémantique ; plus il est proche de 0, plus on favorise le lexical.

- $$
  \text{score}_{\text{cosine}}
  $$

   : similarité cosinus normalisée (souvent entre 0 et 1).

- $$
  \text{score}_{\text{BM25 normalisé}}
  $$

   : score BM25 ramené dans le même intervalle (min-max ou autre normalisation).

- Le score final permet de classer les documents.

### Comportement

- Augmenter \(
  $$
  \alpha
  $$
  \) améliore la capture des synonymes et reformulations, mais peut perdre les correspondances exactes de termes techniques.

- Diminuer \(
  $$
  \alpha
  $$
  \) favorise les mots-clés précis (utile en droit, finance, normes).

## Code Python

```python
def hybrid_score(cosine: float, bm25_norm: float, alpha: float = 0.7) -> float:
    return alpha * cosine + (1 - alpha) * bm25_norm
```

## Cas d’usage métier maximum

**Finance / Banque** : termes réglementaires précis (BM25) + reformulations métier (cosine).

**Immobilier** : « DPE C » exact + descriptions sémantiques de biens similaires.

**Crypto** : noms de fonctions de smart contracts (lexical) + explications de risques (sémantique).

**Assurance, RH, BTP** : même combinaison pour clauses techniques et langage naturel.

Le score hybride est souvent supérieur à l’un ou l’autre seul en production.
