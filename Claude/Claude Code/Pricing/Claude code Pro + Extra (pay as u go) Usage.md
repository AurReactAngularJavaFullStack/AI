```
Là ce problème entouré en rouge ds claude code avec claude code pro qui n'est pas max 

Cmt régler ce problème ce que je vais faire pcq j'ose pas passer max à en payant en plus 61€ puisque l'on passe à 90€ ds le mois par rapport au 21€ de pro plus tva 20% 

Je pense dc 79€ je pense en france je vais payer si j'ai le courage car c'est chère et l'alternative que j'ai trouvé c tu prend écris rédige ds l'arborescence du projet un max de contexte files context back up j'appelle pour qu'une ia moins chère et moins performante s'inspire d travaux d'opus 4.5 et reprend de a à z l'implémentation de c workflows
```

## Ce que tu peux faire **sans** passer à Max (le plan à ~100$/mois et +) 

### 1) Le meilleur hack “rationnel” : **Pro + Extra Usage (pay-as-you-go quand tu dépasses)**

Anthropic permet maintenant d’activer **Extra Usage** sur les plans payants : quand tu hits le cap, tu peux **continuer en payant à la conso** (tarifs API standards) au lieu d’être bloqué. 

**Pourquoi c’est intéressant pour toi :**

- Tu gardes **Pro** (coût fixe raisonnable).
- Tu n’achètes pas un “Max à 100$” juste pour 2–3 jours où tu bourrines.
- Tu peux te mettre un **budget plafond** (genre “ok je dépasse max de 15€ ce mois-ci, pas plus”).

> C’est littéralement le mode “je paye seulement quand je suis en sprint”.

### 2) Variante “sprint only” : basculer sur l’API via **ANTHROPIC_API_KEY** (au besoin)

Claude Code **priorise une clé API** si elle est présente dans tes variables d’environnement. Donc tu peux faire :

- en temps normal : **plan Pro**
- en période de blocage : tu mets une clé API → tu passes en **pay-as-you-go** 

Et tu contrôles ça avec `/status` dans Claude Code. 

**Windows (PowerShell) – activer temporairement :**

```
$env:ANTHROPIC_API_KEY="sk-...ton_api_key..."
```

**Revenir au plan Pro (désactiver) :**

```
Remove-Item Env:ANTHROPIC_API_KEY
```

⚠️ Important : si tu laisses la clé en permanence, tu risques de **payer sans t’en rendre compte**, même si tu es “loggé Pro”. 

### 3) Réduire la conso : **Sonnet par défaut, Opus seulement pour les moments “boss fight”**

Plus tu utilises un modèle “compute-heavy” (Opus), plus tu tapes vite les limites. 
 Stratégie qui marche très bien :

- **Sonnet** : génération de code, refactors, wiring, CRUD, tests “normaux”
- **Opus** : design/architecture, bugs tordus, review final, points critiques (facturation BTP, invariants, edge cases)

Dans Claude Code, tu peux switcher au besoin (`/model`). 

### 4) Optimiser ton usage “agent” (ça compte beaucoup)

Claude Code explique lui-même que :

- la taille du repo,
- les fichiers attachés,
- la longueur des conversations,
- et des options comme l’auto-accept
   …font exploser la conso. 

**Concrètement :**

- Évite de lui faire relire 30 fichiers à chaque tour.
- Demande d’abord : **plan + liste de fichiers à toucher**, puis **un seul gros patch**.
- Travaille par “tranches” (1 workflow = 1 session) au lieu d’un méga-thread infini.