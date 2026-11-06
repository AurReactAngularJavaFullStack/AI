```
Apparemment récemment a été introduit l skills notamment l claude skills qui peuvent en contexte doc folders d'un projet 

À quoi ça sert vraiment c new md file skills puisque claude code a introduit ds sa new version une ui dc quels st l intérêts d skills configurable la prisma skills context7 skills apex skills 

Pq avoir créé ça quels st l intérêts ? 

pros and cons
```

Tu as bien flairé le truc : les **Skills** (dans Claude Code) ne sont pas “juste un nouveau markdown à la mode”. C’est une **brique d’industrialisation** pour transformer un agent généraliste en **agent spécialisé**, *sans recoller 200 lignes de prompt à chaque fois*.

## 1) C’est quoi exactement un “Skill” dans Claude Code ?

Un **Skill = un dossier** contenant au minimum un fichier **`SKILL.md`**.
Ce `SKILL.md` a **2 parties** :

- **Frontmatter YAML** (entre `---`) : *métadonnées + règles d’activation*
  - `name` → devient la commande `/name`
  - `description` → sert à aider Claude à décider *quand* l’utiliser automatiquement
  - options : contrôle d’invocation, restrictions d’outils, etc.
- **Corps Markdown** : *les instructions exécutées quand le skill est activé*

Claude peut :

- soit **l’invoquer automatiquement** quand c’est pertinent,
- soit tu l’invoques **explicitement** via `/skill-name`. ([Claude Code](https://code.claude.com/docs/fr/skills))

Et point important : **Claude n’a pas tout le contenu de tous les skills tout le temps**. En session normale, il charge surtout les *descriptions* pour savoir ce qui existe, et ne charge le contenu complet **que quand un skill est invoqué** → logique “progressive disclosure” (économie de contexte/tokens). ([Claude Code](https://code.claude.com/docs/fr/skills))

## 2) Pourquoi ils ont créé ça ? (le “pourquoi” produit)

Anthropic a posé le constat : les agents deviennent capables d’agir (fichiers, shell, outils externes), mais pour bosser “en vrai” il faut :

- du **savoir procédural** (workflows, checklists, conventions d’équipe)
- du **contexte organisationnel** (standards, contraintes, sécurité)
- une façon **composable, partageable, portable** d’équiper l’agent

Donc ils ont créé les **Agent Skills** : des “packs” d’instructions + scripts + ressources, **découvrables et chargeables dynamiquement**, comme un **guide d’onboarding pour un nouveau dev**, mais lisible par l’agent. ([Anthropic](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills))
Et ils ont même publié un **standard ouvert** pour la portabilité multi-outils (agentskills.io). ([agentskills.io](https://agentskills.io/what-are-skills?utm_source=chatgpt.com))

En clair : **au lieu d’avoir 1 méga-prompt infâme**, tu as des briques modulaires versionnées.

## 3) “Skills configurable” : c’est configurable en quoi ?

Claude Code a ajouté des contrôles très concrets :

### a) Où vivent les skills (scopes + monorepo)

- `~/.claude/skills/...` : perso, tous tes projets
- `.claude/skills/...` : spécifique au repo
- et il découvre aussi des `.claude/skills` **imbriqués** (monorepo par package). ([Claude Code](https://code.claude.com/docs/fr/skills))

### b) Qui a le droit de les déclencher (éviter le “Claude déploie en prod pour te faire plaisir”)

Dans le frontmatter :

- `disable-model-invocation: true` → **Claude ne peut pas auto-lancer**, toi oui (utile pour `/deploy`, `/commit`, etc.) ([Claude Code](https://code.claude.com/docs/fr/skills))
- `user-invocable: false` → **pas affiché comme commande utilisateur**, mais Claude peut l’utiliser comme “connaissance interne” ([Claude Code](https://code.claude.com/docs/fr/skills))

### c) Restreindre les outils utilisables (mode “lecture seule”, etc.)

`allowed-tools` permet de limiter ce que Claude peut faire quand le skill est actif (ex: lire sans écrire). ([Claude Code](https://code.claude.com/docs/fr/skills))

### d) Passer des arguments et faire des substitutions

- `$ARGUMENTS` récupère ce que tu passes après `/skill`
- `${CLAUDE_SESSION_ID}` utile pour logguer / tracer ([Claude Code](https://code.claude.com/docs/fr/skills))

### e) Injecter du contexte dynamique

Tu peux exécuter des commandes shell avant envoi au modèle (`!`…``) et injecter la sortie (ex : `gh pr diff`). ([Claude Code](https://code.claude.com/docs/fr/skills))

### f) Exécuter dans un sous-agent isolé (fork)

`context: fork` + `agent: Explore/Plan/...` → tu lances un sous-agent avec un environnement/outils adaptés, puis il te résume. ([Claude Code](https://code.claude.com/docs/fr/skills))

## 4) Pourquoi tu vois “Prisma skills”, “Context7 skills”, “APEX skills” ?

Parce que “Skill” est devenu le **format packaging** standard pour distribuer des expertises, un peu façon **“npm du prompting”**.

### Prisma skills

Souvent : des skills orientés **schéma/migrations/transactions/bonnes pratiques Prisma**. Exemple réel : un skill qui enseigne comment régler l’isolation transactionnelle pour éviter des race conditions. ([GitHub](https://github.com/djankies/claude-configs/blob/main/prisma-6/skills/configuring-transaction-isolation/SKILL.md?utm_source=chatgpt.com))
Ce n’est pas forcément “officiel Prisma”, mais c’est typiquement le genre de brique qu’une équipe va mutualiser.

### Context7 skills

**Context7** est plutôt un **serveur MCP** qui fournit de la doc à jour (API/library). On le branche, et on ajoute souvent une règle/skill pour que l’agent pense à l’utiliser automatiquement plutôt que d’halluciner une API de 2022. ([GitHub](https://github.com/upstash/context7))

### APEX skills

Deux usages fréquents :

- **APEX “méthodologie”** : un meta-skill orchestrateur “Analyse → Plan → Execute → Ship” (discipline de delivery). ([MCP Market](https://mcpmarket.com/tools/skills/apex-full-workflow-orchestrator?utm_source=chatgpt.com))
- **Apex (Salesforce)** : skills spécialisés pour dev Salesforce (Apex, SOQL, Lightning, etc.). ([GitHub](https://github.com/Jeffallan/claude-skills/issues/79?utm_source=chatgpt.com))

## 5) Intérêts concrets (ce que ça t’apporte *vraiment*)

- **Réutilisabilité** : tu écris ton workflow une fois, tu l’appelles en `/review`, `/migrate-db`, `/release-notes`, etc.
- **Cohérence** : mêmes standards à chaque exécution (format de PR, conventions, DDD rules, etc.)
- **Contrôle & sécurité** : tu empêches l’auto-déclenchement des actions dangereuses et tu limites les outils
- **Scalabilité** : tu peux versionner, review, partager dans un repo (comme du code)
- **Efficacité de contexte** : gros contenus déplacés en fichiers de support, chargés seulement si besoin ([Claude Code](https://code.claude.com/docs/fr/skills))
- **Portabilité** : le format Agent Skills est cross-outils, et même d’autres plateformes (ex: Codex) documentent un modèle similaire ([OpenAI développeurs](https://developers.openai.com/codex/skills/?utm_source=chatgpt.com))

Et côté “écosystème” : il existe maintenant des CLIs + annuaires pour installer des packs de skills dans plusieurs agents (Claude Code, Cursor, Codex, etc.). ([Vercel](https://vercel.com/changelog/introducing-skills-the-open-agent-skills-ecosystem))

## 6) Pros / Cons (sans sucre ajouté)

### ✅ Pros

- **Industrialisation** de l’agent (moins “chat”, plus “outil”)
- **Moins de prompt spaghetti**, plus de modularité
- **Auditabilité** (un skill se code review)
- **Onboarding** d’équipe accéléré (le savoir-faire devient exécutable)
- **Réduction des erreurs** via checklists + outils autorisés
- **Monorepo-friendly** (skills par package)

### ⚠️ Cons / risques

- **Supply chain risk** : installer un skill tiers = comme installer un package npm. Ça peut être malveillant ou juste mauvais.
- **Over-trigger / under-trigger** : si `description` est mal écrite, Claude l’utilise trop… ou jamais.
- **Drift** : un skill non maintenu devient un “senior de 2017” → confiant, obsolète, dangereux.
- **Conflits de responsabilités** : trop de skills = bruit, et l’agent hésite / charge les mauvais.
- **Fausse sécurité** : limiter les tools aide, mais si tu autorises Bash + réseau + écriture, tu dois assumer la surface d’attaque.
- **Complexité d’architecture** : tu ajoutes une couche “runtime comportemental” à debugger.

## 7) Règle pragmatique (quand ça vaut le coup)

Un skill vaut le coup quand :

- tu répètes un workflow **au moins** chaque semaine,
- ou que l’erreur coûte cher (deploy, migrations, sécurité, PR standards),
- ou que tu veux verrouiller un style (DDD, tests, conventions).

Sinon, c’est juste un nouveau dossier qui te donne l’illusion d’être organisé (comme les gens qui créent `/archive_2026_final_v3_reel_final/`).

------

Si tu veux une approche vraiment “pro” pour ton contexte (projet lourd, DDD/CQRS, monorepo, contraintes de sécurité), la combinaison qui marche bien est :
**CLAUDE.md = règles globales stables**, et **Skills = workflows activables** (review PR, migration, génération de slice vertical, etc.), avec `disable-model-invocation: true` sur tout ce qui touche au “shipping”.