```
c quoi le mode auto-compact avec claude code qu'est-ce que ça représente
```

Le **mode auto-compact** dans Claude Code, c’est le **garbage collector du contexte** : 

Quand ta session devient trop grosse et frôle la limite de “mémoire” (context window), Claude **résume automatiquement** l’historique pour repartir avec une version **compressée** et continuer sans planter. ([code.claude.com](https://code.claude.com/docs/en/vs-code?utm_source=chatgpt.com))

### Bonus “niveau ingénieur maniaque” (très efficace)

Claude Code a des **hooks** liés à la compaction : tu peux déclencher un script *juste avant* un compact (manuel ou auto) pour écrire un snapshot dans un fichier (ex: `docs/ai/session-state.md`). ([code.claude.com](https://code.claude.com/docs/en/hooks?utm_source=chatgpt.com))

En clair : 

Auto-compact = **compression automatique du contexte** pour éviter d’exploser la fenêtre. Sur un gros DDD, tu veux généralement **contrôler** ce que le résumé conserve, donc **/compact + instructions** et un mini “state file” dans le repo, et tu redeviens le boss de la mémoire.

### Ce que ça représente exactement

- Claude Code empile dans le contexte : messages + fichiers “@mention” + diffs + logs, etc.

- Quand tu dépasses ~**95%** de la capacité, **auto-compact** se déclenche : 

  Il produit un **résumé** de ce qui compte, jette une partie du détail, et continue avec ce résumé. ([code.claude.com](https://code.claude.com/docs/fr/costs?utm_source=chatgpt.com))

Donc quand tu vois un indicateur du style **“auto-compact 100% used”** (comme sur ton screenshot), ça veut dire :

- **Tu es à la limite du seuil**,
- Au prochain gros échange, Claude risque de **compacter** (ou il est prêt à le faire),
- Et tu vas potentiellement perdre des détails fins (le résumé garde l’essentiel, mais pas tout).

### Pourquoi ça peut te gêner sur VerifactureBTP (DDD/CQRS/hexago)

Sur un projet comme le tien, les détails “fragiles” sont exactement ceux qui sautent en premier dans un résumé automatique :

- conventions de packages et boundaries hexagonaux,
- règles métier BTP (retenue, situations, révision de prix, TVA multi-taux…),
- décisions d’architecture (CQRS, ports, anti-corruption layers),
- TODOs précis et invariants.

Auto-compact évite la panne… mais peut **dégrader la continuité** si tu laisses faire sans guider.

### Les commandes utiles (à connaître par cœur)

Claude Code te donne 3 options claires : ([code.claude.com](https://code.claude.com/docs/fr/slash-commands?utm_source=chatgpt.com))

- **`/compact [instructions]`** : tu compactes *toi-même* en disant quoi préserver (recommandé sur gros projets) ([code.claude.com](https://code.claude.com/docs/en/costs?utm_source=chatgpt.com))
- **`/clear`** : tu repars de zéro (utile quand tu changes complètement de sujet) ([code.claude.com](https://code.claude.com/docs/en/costs?utm_source=chatgpt.com))
- **`/config`** : tu peux **activer/désactiver auto-compact** (“Auto-compact enabled”) ([code.claude.com](https://code.claude.com/docs/fr/costs?utm_source=chatgpt.com))

### Mon réglage pragmatique (pour ton cas)

1. **Désactive auto-compact**, et **compacte manuellement** quand tu sens que tu vas attaquer une grosse feature. (Tu gardes le contrôle du “résumé”.) ([code.claude.com](https://code.claude.com/docs/fr/costs?utm_source=chatgpt.com))
2. Utilise un **/compact guidé** du style :
   - “Conserve : architecture hexagonale, règles de calcul (TVA multi-taux, remise, retenue, révision), conventions de packages, endpoints OpenAPI, TODO Sprint, points en erreur actuels, décisions d’ADR.”
3. Mets des **instructions de compaction dans `CLAUDE.md`** (Claude Code le supporte) pour que même en auto ça garde tes invariants. ([code.claude.com](https://code.claude.com/docs/en/costs?utm_source=chatgpt.com))

