```
non claude cowork ça consiste en quoi? 
```

Claude **Cowork**, c’est le mode “agent” de Claude pensé pour bosser **comme un collègue de bureau**, pas comme un chatbot. L’idée est simple : tu lui donnes **accès à un dossier** de ton ordi, tu lui files une mission, et il **planifie + exécute** une série d’actions tout seul (avec des points de contrôle). ([Claude](https://claude.com/blog/cowork-research-preview))

### Ce que ça “consiste” à faire (le cœur du truc)

- **Tu choisis un dossier** (genre “Cowork-Sandbox”) auquel Claude a accès.
- Dans Cowork, Claude peut **lire / créer / modifier** des fichiers *dans ce dossier*.
- Tu lui donnes une tâche du style :
  “Prends ces captures, fais-moi un tableau de dépenses”,
  “Organise mes téléchargements en renommant et classant”,
  “Transforme ces notes en rapport structuré”. ([Claude](https://claude.com/blog/cowork-research-preview))
- Claude **propose un plan**, puis **avance étape par étape** en te montrant l’avancement et en te laissant corriger le tir en cours de route. ([Centre d'Aide Claude](https://support.claude.com/en/articles/13345190-getting-started-with-cowork))

### Différence avec “Claude Code”

Pense “Claude Code” = dev/terminal/repo, et “Cowork” = **même moteur agentique**, mais emballé pour les **tâches de bureau** (documents, fichiers, extraction depuis screenshots, rapports, etc.), plus accessible aux non-devs. ([Claude](https://claude.com/blog/cowork-research-preview))

### Bonus : connecteurs + skills

Cowork peut aussi s’appuyer sur des **connecteurs** (services externes compatibles) et des **skills** orientés création de documents / présentations, et il peut bosser avec l’accès navigateur via “Claude in Chrome” pour certaines tâches web. ([Claude](https://claude.com/blog/cowork-research-preview))

### Où ça marche / prérequis (important)

- **Uniquement via l’app Claude Desktop sur macOS** (pas web/mobile).
- Disponible (en “research preview”) pour les abonnés **Pro ou Max**.
- L’app doit **rester ouverte** pendant l’exécution. ([Centre d'Aide Claude](https://support.claude.com/en/articles/13345190-getting-started-with-cowork))

### Le côté “attention, ça peut casser des trucs”

Comme il peut agir sur des fichiers, il faut le traiter comme un junior très rapide :

- consignes ultra claires (surtout sur suppression/renommage),
- bosser dans un dossier “sandbox”,
- et garder en tête les risques type **actions destructrices** ou **prompt injection** (surtout si navigation). ([Claude](https://claude.com/blog/cowork-research-preview))

En résumé : **Cowork = Claude qui exécute des tâches multi-étapes sur ton ordi (dans un dossier autorisé), avec une posture “je fais le boulot et je te tiens au courant”**. ([Claude](https://claude.com/blog/cowork-research-preview))