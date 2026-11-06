# Organisation des Leçons Markdown pour le Parcours AI Agentic

**Pour Aurélien Hamzaoui — AI Software Engineer (Java, Spring, Angular, React, Agents IA, Architecture Hexagonale, DDD, CQRS)**

Basé sur le parcours numéroté :  
`01-Prompts` → `02-Schemas` → `03-Outils` → `04-Agents` → `05-Memoire` → `06-RAG` → `07-Contexte` → `08-Planification` → `09-Orchestration` → `10-MCP` → `11-Evaluation` → `12-GardeFous`

## Principes d'organisation

1. **Ordre global** : Suivre strictement la numérotation (dépendances naturelles).
2. **Priorité au sein de chaque dossier** : Du plus important/prioritaire au moins prioritaire.
   - 01 : Définitions + Concepts fondamentaux (must-know)
   - 02 : Formules mathématiques / Théorèmes / Algorithmes clés
   - 03 : Démonstrations / Preuves / Implémentations code
   - 04 : Exemples concrets + Cas d'usage réels
   - 05 : Applications par domaine métier (assurance, RH, BTP, finance, etc.)
   - 06 : Avancé / Optionnel / Pièges courants
3. **Style** : Pratique pour un développeur logiciel. Math uniquement là où elle est nécessaire (RAG, Évaluation, Mémoire, Contexte). Code en Java/Spring ou pseudo-code clair. Liens avec architecture hexagonale / DDD / CQRS.
4. **Format Markdown** : KaTeX pour formules (`$$...$$` ou `$...$`), sections claires, exemples de code, diagrammes mermaid si utile.

---

## Structure des fichiers recommandée

Pour chaque dossier `XX-Nom/` :

```
XX-Nom/
├── 01-Definitions-Fondamentaux.md          ← Priorité max
├── 02-Formules-Theoremes-Algorithmes.md    ← Math essentielle
├── 03-Demonstrations-Implementations.md
├── 04-Exemples-Cas-Usage.md
├── 05-Applications-Domaines.md
└── 06-Avance-Pieges-Optionnel.md
```

---

## Détail par dossier (priorité décroissante)

### 01-Prompts
1. Définitions : System / User / Assistant, few-shot, chain-of-thought, structured output
2. Formules : Token counting, coût, température (softmax léger)
3. Implémentations : Patterns ReAct, structured JSON
4. Cas d'usage : Agents RH (onboarding), assurance (devis)
5. Domaines : Finance, BTP, public
6. Avancé : Prompt injection defense (préfigure GardeFous)

### 02-Schemas
1. Définitions : JSON Schema, Pydantic / Zod, structured outputs
2. Formules : Validation formelle (peu de math)
3. Implémentations : Ports hexagonaux pour schémas
4. Cas d'usage : Contrats d'outils, réponses agents
5. Domaines : Facturation BTP, conformité RH
6. Avancé : Schema evolution, versioning

### 03-Outils (Tools / Function Calling)
1. Définitions : Tool calling, function schemas, side-effects
2. Formules : Coût / latence d'appels
3. Implémentations : Adapters hexagonaux
4. Cas d'usage : Appel API métier, calculs
5. Domaines : Banque, assurance, RH
6. Avancé : Idempotence, retries, budgets

### 04-Agents
1. Définitions : Boucle perception-raisonnement-action, ReAct, Plan-and-Execute
2. Formules : Boucle de contrôle simple
3. Implémentations : Agent runtime avec Spring / LangGraph-like
4. Cas d'usage : Agent de qualification de demandes
5. Domaines : StaffMind-like (RH multi-pays)
6. Avancé : Multi-agents préliminaires

### 05-Memoire
1. Définitions : Short-term, episodic, semantic, procedural
2. Formules : Similarité (prépare RAG), decay / scoring
3. Implémentations : Vector store + summaries
4. Cas d'usage : Mémoire de conversation longue
5. Domaines : Clients récurrents (assurance)
6. Avancé : Mémoire partagée multi-agents

### 06-RAG ⭐ (Math importante)
1. Définitions : Retrieval-Augmented Generation, chunking, embeddings
2. **Formules** :
   - Cosine similarity :
     $$ \cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \|\mathbf{b}\|} = \frac{\sum a_i b_i}{\sqrt{\sum a_i^2} \sqrt{\sum b_i^2}} $$
   - Dot product, normes euclidiennes
   - Recall@k, Precision@k, MRR
3. Démonstrations : Calcul manuel + code Java/Python
4. Cas d'usage : Base documentaire métier (contrats, procédures)
5. Domaines : Assurance auto, facturation BTP, conformité
6. Avancé : Hybrid search, reranking, GraphRAG

### 07-Contexte
1. Définitions : Context window, attention, compaction
2. Formules : Attention scaled dot-product (léger) :
   $$ \text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V $$
3. Implémentations : Gestion de contexte long
4. Cas d'usage : Agents avec historique long
5. Domaines : Processus métier multi-étapes
6. Avancé : Context engineering, compression

### 08-Planification
1. Définitions : Planning vs reactive, goal decomposition
2. Formules / Algorithmes : A*, BFS/DFS légers, cost functions
3. Implémentations : Planner + executor
4. Cas d'usage : Workflows complexes (onboarding RH)
5. Domaines : Processus réglementés
6. Avancé : Hierarchical planning

### 09-Orchestration
1. Définitions : Workflows, multi-agents, supervisor
2. Formules : Peu (graphes, états)
3. Implémentations : State machines, LangGraph-like
4. Cas d'usage : Agents spécialisés collaboratifs
5. Domaines : Plateforme IA interne
6. Avancé : Durable execution, human-in-the-loop

### 10-MCP (Model Context Protocol)
1. Définitions : Hosts, clients, servers, tools/resources/prompts
2. Formules : Aucune (protocole)
3. Implémentations : Serveur MCP métier
4. Cas d'usage : Exposition d'outils d'entreprise
5. Domaines : Intégration systems of record
6. Avancé : Auth, elicitation, gateways

### 11-Evaluation ⭐ (Math importante)
1. Définitions : Task success, tool accuracy, traces
2. **Formules** :
   - Precision / Recall / F1
   - Faithfulness = claims supportées / claims totales
   - Answer Relevancy (cosine sur questions générées)
   - ToolCallAccuracy, AgentGoalAccuracy
   - RAGAS metrics
3. Démonstrations : Calculs + suites de tests
4. Cas d'usage : CI/CD pour agents
5. Domaines : Conformité, audit
6. Avancé : LLM-as-judge, adversarial evals

### 12-GardeFous (Guardrails)
1. Définitions : Safety, permissions, human approval, prompt injection
2. Formules : Scoring de risque, thresholds
3. Implémentations : Policy gates, validation
4. Cas d'usage : Agents en production (finance, RH)
5. Domaines : Contextes sensibles (Ministère, Banque de France)
6. Avancé : Formal verification légère, red teaming

---

## Mapping vers les métiers du schéma

| Métier | Dossiers prioritaires AI Agentic |
|--------|----------------------------------|
| **Product Engineers** | Prompts, Schemas, Agents, Planification, Evaluation |
| **AI Engineers** | Tout, surtout RAG, Contexte, Orchestration, Evaluation |
| **AI Agent Ops** | Outils, Memoire, MCP, Evaluation, GardeFous |
| **Forward-Deployed Engineers** | Tout le parcours + focus déploiement client, intégration, adoption |
| **AI Platform Team** | Orchestration, MCP, Evaluation, GardeFous + Ops |

---

## Recommandation de lecture

Commencer par **06-RAG** et **11-Evaluation** pour les formules mathématiques, puis revenir au début pour la pratique.

Chaque fichier Markdown doit contenir :
- Définitions claires
- Formules en KaTeX
- Exemples de code (Java/Spring préféré)
- Cas d'usage tirés de ton expérience (assurance, RH, BTP, secteur public)
- Sections "À retenir" et "Exercices"

---

*Document généré pour structurer un parcours d'apprentissage personnel et professionnel.*
