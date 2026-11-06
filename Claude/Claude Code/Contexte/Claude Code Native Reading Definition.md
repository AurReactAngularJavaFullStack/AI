```
Nativement ça signifie que quelque soit le prompte que ej fasi tu scannes ou lit tt l fiels qu'il y a des le dossier caché .claude on est d'accord?: 
Nous on l'utilise déjà nativement dans Claude Code.
```

Oui, exactement. Voici comment ça marche concrètement :

## Ce que Claude Code charge automatiquement au démarrage

| Fichier/Dossier             | Chargé quand                                                 |
| --------------------------- | ------------------------------------------------------------ |
| `.claude/CLAUDE.md`         | **Toujours**, à chaque conversation — c'est dans mon contexte système |
| `.claude/rules/*.md`        | **Toujours**, injecté comme instructions projet              |
| `.claude/settings.json`     | **Toujours**, config (permissions, hooks)                    |
| `.claude/skills/*/SKILL.md` | **Metadata seulement** (nom + description) — le contenu complet est chargé uniquement quand tu invoques `/setup`, `/pre-ship`, etc. |
| `.claude/agents/`           | Idem, metadata d'abord                                       |

C'est exactement le **"chargement progressif"** de ta slide :

- **Niveau 1** : metadata ~100 tokens (nom + description de chaque skill) — **toujours en mémoire**
- **Niveau 2** : contenu complet du SKILL.md — **chargé à la demande** quand le skill est déclenché
- **Niveau 3** : les fichiers du projet que le skill me demande de lire — **lu en temps réel**

Donc oui, le dossier `.claude/` entier est mon "cerveau projet". Je ne scanne pas tout le filesystem à chaque prompt, mais je connais **toujours** l'existence et la description de tout ce qui est dans `.claude/`, et je charge le détail quand c'est pertinent.