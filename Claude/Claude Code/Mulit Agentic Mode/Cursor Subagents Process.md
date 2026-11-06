## 2) Le “multi-agent” dans Claude Code (officiel) : les Subagents

Le vrai mode multi-agent Claude Code, c’est les **subagents** :

- chaque subagent a **son propre contexte**, un **prompt système**, des **outils** et des **permissions** dédiées 
- Claude peut **déléguer** automatiquement ou sur demande (Explore pour explorer, Plan pour préparer, etc.) 

### Step-by-step dans Cursor (avec l’extension Claude Code)

Cursor étant un VS Code-like, tu peux piloter Claude Code pareil.

**Étape 1 — Ouvre Claude Code panel**

- Dans Cursor : ouvre le panneau **Claude Code** (tu l’as déjà, on le voit).

**Étape 2 — Lance le gestionnaire d’agents**
 Dans l’input Claude Code, tape :

- `/agents` 

**Étape 3 — Crée un agent**

- “Create new agent”
- Choisis le scope :
  - **Project-level** → stocké dans `.claude/agents/` (idéal pour VerifactureBTP, versionnable) 
  - **User-level** → `~/.claude/agents/` (perso, réutilisable partout) 

**Étape 4 — “Generate with Claude”**

Décris ton agent (exemples utiles VerifactureBTP) :

- `architect-ddd` : décisions d’archi, découpage modules/services, règles DDD
- `btp-domain-expert` : retenue de garantie, situations, acomptes, Factur-X, etc.
- `test-runner` : exécute tests, corrige, boucle

**Étape 5 — Outils + modèle**

- Un agent d’analyse : Read/Grep/Glob (pas Write/Edit)
- Un agent “builder” : Edit/Write + Bash (si tu veux qu’il exécute Maven) 

**Étape 6 — Utilise-les**

Exemples de commandes naturelles :

- “Utilise `architect-ddd` pour proposer le design des use cases Organisation + invariants, puis `builder` pour implémenter.”
- “Fais tourner `test-runner` en boucle jusqu’à tests verts.”

> Bonus : les subagents peuvent être utilisés pour **recherche parallèle** et tâches en background (selon config). 

### Est-ce que c’est “Max only” ?

Non : **les subagents = feature Claude Code**, pas un privilège Max. Max sert surtout à **ne pas mourir au bout de 10 minutes** si tu es un ogre à tokens. 