# 06-RAG — 04-Exemples-Cas-Usage

**Dossier :** 06-RAG  
**Métiers :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers, Product Engineers

## Exemples concrets de RAG en production

### Finance / Banque
Un analyste demande : « Quelles sont les obligations de reporting pour une position en dérivés de taux au-dessus de 10 M€ ? »  
Le RAG récupère les extraits réglementaires pertinents (cosine + BM25) et l’agent génère une réponse sourcée. Faithfulness et Context Recall sont surveillés.

### Immobilier
« Estime un appartement 65 m² DPE C dans le 3e arrondissement de Lyon. »  
Retrieval de comparables récents + diagnostics. Le ranking (NDCG, MRR) est critique pour la qualité de l’estimation.

### Crypto
« Quels sont les risques de liquidité du protocole X ? »  
Retrieval dans le whitepaper et la documentation technique. Hybrid search pour capturer à la fois les termes exacts et les reformulations.

### Assurance (projet auto)
Description de sinistre → retrieval des clauses de couverture et de franchise.

### RH (StaffMind)
Question de conformité multi-pays → retrieval des politiques locales.

### BTP (VerifactureBTP)
Question sur la facturation électronique → retrieval des guides et modèles.
