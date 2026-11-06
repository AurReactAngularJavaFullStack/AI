```
compare claude pro vs claude max nbre de requêtes possible messages tokens consommés sur 5 heures
```

Voilà la réalité (pas le marketing) des quotas **Claude Pro vs Claude Max**, sur une **fenêtre de 5 heures** : Anthropic parle en **“messages”** (chat Claude) et en **“prompts”** (Claude Code), et **ça varie** selon la longueur des messages, la taille des fichiers, la longueur de la conversation, et le modèle (Opus “mange” plus vite le quota). ([support.claude.com](https://support.claude.com/en/articles/8324991-about-claude-s-pro-plan-usage))

## 1) Combien de “requêtes” (messages) en 5 heures ?

| Plan        | Prix mensuel | Messages Claude / 5h (ordre de grandeur) | Prompts Claude Code / 5h (ordre de grandeur)                 |
| ----------- | ------------ | ---------------------------------------- | ------------------------------------------------------------ |
| **Pro**     | **20$**      | **~45**                                  | **~10–40** ([support.claude.com](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)) |
| **Max 5×**  | **100$**     | **~225**                                 | **~50–200** ([support.claude.com](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)) |
| **Max 20×** | **200$**     | **~900**                                 | **~200–800** ([support.claude.com](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)) |

Points importants :

- Les limites **reset toutes les 5 heures**. ([support.claude.com](https://support.claude.com/en/articles/8324991-about-claude-s-pro-plan-usage))
- **Claude + Claude Code partagent le même quota** : si tu brûles tout dans le terminal, le chat web va te dire “stop”, et inversement. ([support.claude.com](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan))
- Les chiffres ci-dessus sont des **moyennes** sur des conversations plutôt “courtes”. Si tu balances des pavés + gros fichiers, tu tomberas **bien avant**. ([support.claude.com](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan))

## 2) Et en “tokens consommés sur 5 heures” ?

### La vérité : Anthropic ne donne **pas** un quota “X tokens / 5h” public

Leur limite est un mix **message count × longueur de conversation × taille des fichiers × modèle/feature**. Donc tu ne peux pas convertir proprement en “tokens garantis”. ([support.claude.com](https://support.claude.com/en/articles/8324991-about-claude-s-pro-plan-usage))

### Ce qu’on peut dire de façon fiable

- La **fenêtre de contexte** (la “RAM” d’une conversation) est **200K tokens** sur les plans payants (Max n’augmente pas la taille du contexte, il augmente surtout le volume d’usage). ([support.claude.com](https://support.claude.com/en/articles/11647753-understanding-usage-and-length-limits))
- Si ta conversation devient longue, Claude fait de la **gestion automatique du contexte** (résumés internes) sur les plans payants avec exécution de code activée, mais ça n’annule pas les quotas d’usage. ([support.claude.com](https://support.claude.com/en/articles/11647753-understanding-usage-and-length-limits))

### Ordres de grandeur (simulation utile)

Si on modélise un “message” par un coût moyen en tokens (entrée + sortie), voilà ce que ça donne **en volume théorique**, juste pour te donner l’échelle :

| Profil de message                            | Tokens ~ / message | Pro (~45 msg) | Max 5× (~225 msg) | Max 20× (~900 msg) |
| -------------------------------------------- | ------------------ | ------------- | ----------------- | ------------------ |
| **Léger** (question courte + réponse courte) | ~500               | ~22.5K        | ~112.5K           | ~450K              |
| **Moyen** (dev normal : code + explication)  | ~2,000             | ~90K          | ~450K             | ~1.8M              |
| **Lourd** (gros contexte, fichiers, refacto) | ~10,000            | ~450K         | ~2.25M            | ~9M                |

⚠️ À prendre comme **ordre de grandeur**, pas comme une promesse : plus le message est lourd (surtout pièces jointes / gros historique / Opus), plus tu atteins la limite **avec moins de messages**. ([support.claude.com](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan))

## 3) Ce qui fait exploser tes limites (et comment tenir 5h sans te faire couper)

- **Conversations longues** → chaque nouveau message “porte” tout l’historique ⇒ coût monte. (Solution : **nouvelle conversation par sujet**.) ([support.claude.com](https://support.claude.com/en/articles/11014257-about-claude-s-max-plan-usage))
- **Pièces jointes lourdes** (PDF, images, gros fichiers) → ça tape le quota. ([support.claude.com](https://support.claude.com/en/articles/11014257-about-claude-s-max-plan-usage))
- **Modèle plus compute-intensive (ex: Opus)** → tu hits plus vite. ([support.claude.com](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan))
- **Claude Code** sur gros repo + auto-accept + multi-instances → tu te fais raser le quota en douceur (mais sûrement). ([support.claude.com](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan))
- Utilise **Projects** pour “cacher” des docs et éviter de ré-uploader / répéter : les tokens “cachés” comptent moins que les tokens non-cachés. ([support.claude.com](https://support.claude.com/en/articles/8324991-about-claude-s-pro-plan-usage))

En résumé :

- **Pro** ≈ “usage sérieux mais avec ceinture”, ~45 msg / 5h. ([support.claude.com](https://support.claude.com/en/articles/8324991-about-claude-s-pro-plan-usage))
- **Max 5×** ≈ “je bosse toute la journée sans prier”, ~225 msg / 5h. ([support.claude.com](https://support.claude.com/en/articles/11014257-about-claude-s-max-plan-usage))
- **Max 20×** ≈ “power user / usine”, ~900 msg / 5h. ([support.claude.com](https://support.claude.com/en/articles/11014257-about-claude-s-max-plan-usage))

Et oui : en pratique, la vraie variable cachée c’est **la taille de tes prompts + l’historique**. Les tokens, c’est la masse; le “message limit”, c’est juste le compteur de tours que tu fais avant que la salle serveur te jette dehors.