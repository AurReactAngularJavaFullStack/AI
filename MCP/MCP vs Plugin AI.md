```basic
là j'ai regardé une vidéo mcp client server entre cursor ai client et figma mcp server 

je voulais savoir par exemple tu lui demande de faire un auto-layout il ne peut pas le faire plein de bugs de choses 

enfin c limité en terme de capacité tu crois pas qu'n jour y aura un plugin figma ai ds cursor ai et cette idée de mcp qui est révolutionnaire avec l apis ça va être abandonné 

car c juste que pour l'instant y a pas de plugins figma ai ds cursor ai en tant qu'agent mais ça va arrivé 
```

### Où on en est aujourd’hui ?

| Sujet                                       | Situation actuelle                                           |
| ------------------------------------------- | ------------------------------------------------------------ |
| **MCP ↔ Figma**                             | Un serveur open‑source « Figma‑Context‑MCP » existe déjà ; il expose vos fichiers Figma à Cursor (ou à n’importe quel autre “MCP client”) via l’API REST de Figma. Vous devez le lancer vous‑même, puis connecter Cursor en local ou via URL. citeturn0search0 |
| **Cursor**                                  | Cursor gère nativement le rôle d’“MCP client” ; il peut donc consommer n’importe quel serveur MCP sans qu’il faille installer un “plug‑in” interne à l’IDE. Toute la logique d’extension vit côté serveur. |
| **Auto‑layout & autres actions d’écriture** | Le gros frein vient de l’API REST de Figma : elle est (pour l’instant) quasi exclusivement *en lecture seule*. Modifier la mise en page, appliquer un auto‑layout, créer des frames, etc. n’est possible **qu’à l’intérieur d’un plug‑in Figma** (API plugin JS embarquée), pas via REST. Donc le serveur MCP ne peut qu’envoyer la *structure* du design à Cursor ; il ne peut pas demander à Figma de le modifier. |

### Est‑ce qu’un « plug‑in Figma AI » natif dans Cursor va apparaître ?

*Probablement oui, mais sous une autre forme :*

1. **Deux briques à combiner**

   - un *plug‑in* Figma (côté design) pour exécuter les commandes d’écriture ;
   - un *serveur MCP* qui expose ces commandes à Cursor/Claude/etc.

   Dès qu’un·e dév. emballe ces deux parties dans un repo open‑source (ou un package “one‑click deploy”), Cursor saura s’y connecter comme aujourd’hui, sans modification côté IDE.

2. **Signal faible mais encourageant**
    Le « MCP Directory » de Cursor liste déjà des serveurs “Twilio”, “Upstash”, “Paddle”… La communauté porte très vite les intégrations lorsqu’il y a un besoin clair. 

3. **Côté Figma**
    Depuis l’annonce de *Figma AI* et les mises à jour continues de l’API (variables, webhooks, etc.), Figma montre qu’il ouvre de plus en plus son écosystème. Un SDK “write‑enabled” hors plugin n’est pas officialisé, mais la pression des intégrateurs augmente. 

### MCP : feu de paille ou standard durable ?

Le protocole a été lancé par Anthropic fin 2024, et vient de recevoir une mise à jour majeure mi‑avril 2025. Axios souligne son adoption “en forte traction” ; des acteurs comme Replit ou Sourcegraph l’utilisent déjà. Tant que les grands LLM (Claude, GPT, etc.) le supportent, il y a peu de chances qu’il soit « abandonné » ; au pire, il évoluera (v2, extensions de sécurité), mais l’idée de *socket universel* pour agents restera.

### Pourquoi ça “bug” quand tu demandes un auto‑layout ?

- **Limite structurelle** : le serveur MCP ne peut qu’envoyer le *JSON* du design à l’agent ; il ne peut pas pousser un patch en retour.
- **Contours flous des nœuds** : l’API n’expose pas toujours la hiérarchie complète (instances détachées, descriptions manquantes, etc.), donc le modèle hallucine ou se trompe.
- **Stratégie brute** : le LLM essaie de « raisonner » le layout au lieu d’appeler une fonction native, faute d’API écriture.

### Ce qu’on peut attendre à court / moyen terme

| Horizon        | Ce qui pourrait arriver                                      |
| -------------- | ------------------------------------------------------------ |
| **2‑6 mois**   | Plug‑in Figma “headless” (WebAssembly ou Worker + Plugin API) qui accepte des commandes JSON RPC ; serveur MCP “figma‑action” publié dans le *Directory*. |
| **6‑12 mois**  | Extension officielle de l’API Figma (GraphQL ou REST v2) autorisant certaines mutations simples (variables, propriétés d’auto‑layout). |
| **12‑24 mois** | Workflow quasi‑no‑code : tu ouvres Cursor, tu connectes ton fichier Figma via OAuth, et l’agent refactorise la maquette comme il refactorise déjà du code. |

### Conseils pratiques d’ici là

1. **Surveille les repos MCP‑Figma sur GitHub** ; quand les *issues* “write support” bougent, c’est que ça arrive.
2. **Teste le serveur Figma‑Context‑MCP** : même “lecture seule”, il accélère la génération de code ; tu n’as qu’à piloter l’auto‑layout à la main ensuite.
3. **Participe aux channels Discord/Slack de Cursor** : beaucoup de “mini‑adapters” naissent d’une simple discussion.
4. **Si tu es à l’aise en TypeScript** : un petit proof‑of‑concept de plug‑in Figma + bridge MCP est un side‑project très visible en ce moment.

------

Bref : le blocage actuel vient plus des **API de Figma** que de Cursor ou de MCP. Le protocole MCP, lui, s’installe durablement ; dès que Figma (ou un plug‑in tiers) ouvre des opérations d’écriture, un « vrai » agent Figma‑AI dans Cursor apparaîtra presque immédiatement. En attendant, la voie la plus simple reste d’utiliser le serveur MCP existant pour **lire** tes designs et laisser l’humain — toi — cliquer sur “Auto‑layout”.

*(Si tu comptes te lancer dans un prototype, je peux t’aider à esquisser l’architecture ou le manifeste du plug‑in, dis‑moi !)*