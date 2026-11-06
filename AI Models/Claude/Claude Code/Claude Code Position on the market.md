```
Tu penses pas que claude code ont un monopole de marché sur du long terme car ils ne vont jamais livré en open source leur code algos de llm 

Sinon l concurrents peuvent plagié et améliorer sur de l'existant le modèle llm pour eux je pense pas que leur llm algos soit accessible en open source ?
```

Non : **le fait de ne pas open-sourcer le “cœur” (poids du modèle / pipeline d’entraînement) n’implique pas un monopole long terme**. Ça crée un **moat** (avantage défensif), mais pas un “one ring to rule them all”.

### 1) Déjà, il faut séparer 3 choses (sinon on mélange tout)

- **Open source (code)** : tu publies le code de l’outil (ex: un CLI, une UI, un orchestrateur d’agents).
- **Open weights (poids du modèle)** : tu publies les paramètres du LLM (ce qui permet de l’exécuter/finetune ailleurs).
- **Closed weights (API)** : tu ne publies pas les poids, tu vends l’accès via API/produit.

**Claude (le LLM) est typiquement “closed weights”** et Anthropic explique explicitement qu’ils protègent les **model weights** comme un actif critique (risque d’exfiltration, usage sans garde-fous, etc.). ([anthropic.com](https://www.anthropic.com/news/activating-asl3-protections?utm_source=chatgpt.com))
En parallèle, Anthropic **open-source des outils autour** (évals, frameworks, tooling de recherche), par exemple Bloom (évaluations comportementales) ([anthropic.com](https://www.anthropic.com/research/bloom?utm_source=chatgpt.com)), ou des outils de circuit tracing ([anthropic.com](https://www.anthropic.com/research/open-source-circuit-tracing?utm_source=chatgpt.com)), et même une partie “runtime sandbox” mentionnée comme dispo en preview open source. ([anthropic.com](https://www.anthropic.com/engineering/claude-code-sandboxing))

Et **Claude Code (le produit dev)** : il y a une doc officielle ([code.claude.com](https://code.claude.com/docs/en/overview)) et un repo public “anthropics/claude-code”. ([GitHub](https://github.com/anthropics/claude-code))
Mais même si l’outil est visible, **le cerveau (le modèle) reste côté serveur**.

### 2) “S’ils open-sourcent, les concurrents copient” : vrai… mais incomplet

Oui : publier les poids + recettes d’entraînement **réduit fortement** la barrière à l’entrée.

Mais :

- Les **algos de base** (Transformers, RLHF/RLAIF, tool-use, etc.) ne sont pas un secret ésotérique : la différenciation est surtout dans **les données**, **le compute**, **le training pipeline**, **l’alignement**, **l’infra**, **les évaluations**, **les post-train**.
- Même sans open source, il existe des attaques de **distillation / imitation** (copier le comportement via sorties) et une pression concurrentielle énorme. Donc “closed” ≠ “incopiable”, juste “plus dur et plus cher”.

### 3) Pourquoi ça ne donne pas un monopole (même s’ils gardent tout fermé)

Un monopole durable demande des barrières qui bloquent tout le monde. Or sur les assistants de code :

- **Multi-homing** : les devs utilisent plusieurs outils (IDE + CLI + agents CI). Changer de modèle est souvent “un switch de config”.
- **Concurrence frontale** : d’autres acteurs ont leurs propres modèles + produits (et certains ont des modèles open-weights très solides). Ton graphe montrait déjà plusieurs compétiteurs sérieux.
- **Le moat “produit” > le moat “secret”** : l’avantage durable vient de *l’intégration* (workflow IDE/terminal/CI, qualité d’agent, sécurité sandbox, vitesse, coût), pas juste “j’ai caché mon code”.

### 4) Le vrai avantage long terme de Claude Code, si je devais le parier

Pas “monopole”, plutôt **top-tier durable** s’ils restent excellents sur :

- **Agentic reliability** (planification + exécution + correction)
- **Sécurité** (sandboxing, permissions, limitation d’exfiltration) ([anthropic.com](https://www.anthropic.com/engineering/claude-code-sandboxing))
- **DX** (developer experience) + intégrations (IDE, GitHub, CI)
- **Coût/latence** compétitifs

Donc ton intuition est bonne sur un point : **leurs poids de modèle ne seront (probablement) pas open source** et c’est rationnel business + sécurité. ([anthropic.com](https://www.anthropic.com/news/activating-asl3-protections?utm_source=chatgpt.com))
Mais conclure “donc monopole” est un saut logique : le marché du “coding copilots/agents” ressemble plus à un **oligopole très compétitif** avec du multi-modèle qu’à un royaume avec un seul roi.