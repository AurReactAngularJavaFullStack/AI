### Brancher **Bolt** ou **Lovable** dans **Cursor AI** via MCP ?



| Plate‑forme         | Existe‑t‑il un MCP Server « clé en main » ?                  | Statut & mise en place dans Cursor                           |
| ------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Lovable.dev**     | **Oui – Loveable MCP Server** (open‑source)                  | 1. Récupère ta clé API Lovable → 2. Ajoute le server dans *Settings → MCP* de Cursor (STDIO ou SSE) → 3. Tu disposes des outils `create_project`, `check_project_status`, `get_project_details`. Utilise‑les dans des prompts Composer pour demander « génère le squelette UI pour la vue Kanban », etc. [MCP](https://mcp.so/server/loveable-mcp-server/iamseancorcoran) |
| **Bolt / Bolt.new** | **Pas encore d’implémentation officielle**. Des devs bricolent des servers communautaires, mais rien de stable pour la prod (discussions “MCP Integration” côté Bolt et tuto YouTube « generate your own MCP »). Pour l’instant, Bolt se comporte plutôt comme **client** : il peut **importer** tes MCP configs Cursor, pas l’inverse. [Overview \| BoltAI Documentation](https://docs.boltai.com/docs/plugins/mcp-servers?utm_source=chatgpt.com)[Reddit](https://www.reddit.com/r/boltnewbuilders/comments/1jvlh17/boltnew_n8n_and_mcps/?utm_source=chatgpt.com) |                                                              |

**Alternative pratique**
 Pour générer tes wireframes directement dans Cursor AI, la voie la plus mature reste :

1. **Figma MCP Server** → expose tes frames Android Material depuis Figma. [Cursor Directory](https://cursor.directory/mcp/figma?utm_source=chatgpt.com)

2. Dans Cursor, appelle l’outil `get_frame_layout` (ou équivalent) puis demande à l’IA :

   ```
   // Composer
   Utilise le layout Figma 'TaskList-Mobile' et produis le composant React‑Native + style‑sheet.
   ```

3. Optionnel : enchaîne avec **Lovable MCP** pour spin‑up un projet frontend et voir le résultat dans un preview live.

#### Points clés à retenir

- **Cursor** est déjà **client MCP** (support “tools only”). Tu peux donc brancher n’importe quel server listé sur mcp.so ou cursor.directory. [modelcontextprotocol.io](https://modelcontextprotocol.io/clients)
- **Lovable** → ok today, **Bolt** → surveille les releases ou monte ton propre server (template TypeScript MCP SDK + REST wrapper autour de l’API Bolt).
- Pour un flux pure‑design, **Figma MCP** donne le meilleur rendement wireframe → code ; tu peux chaîner avec Lovable si tu veux un déploiement rapide.

Bon prototypage !