Le mec qui a CRÉÉ [**Claude**](https://www.linkedin.com/company/claude/) Code vient de partager comment il bosse.

[**Boris Cherny**](https://www.linkedin.com/in/bcherny/) dirige Claude Code chez [**Anthropic**](https://www.linkedin.com/company/anthropicresearch/). 

Son workflow quotidien ?

Il lance 10 à 15 sessions de Claude Code EN PARALLÈLE. Chaque jour.
5 dans son terminal. 5 à 10 sur [**claude.ai**](https://www.linkedin.com/redir/redirect/?url=http%3A%2F%2Fclaude.ai&urlhash=oLR7&mt=3MiTB1mjTWqS8q0Ac1qlfIpGjsRPJw0Af2R1u0xLrxnfyHEOkqlQ1lHtMpzQbn8suekHdOZRSm3BZIVd3WeNl8DGnm92B5sTpMEGF_ZdBb9kgYvFyg6Ghdb3PA&isSdui=true). Et quelques-unes depuis son iPhone le matin.

Pendant que toi tu galères avec un seul prompt, lui a une armée d'IA qui ship du code en simultané.

Mais le vrai game-changer, c'est pas les sessions parallèles.

C'est son workflow en 𝟲 𝗽𝗶𝗹𝗶𝗲𝗿𝘀.

𝟭. 𝗣𝗹𝗮𝗻 𝗠𝗼𝗱𝗲 𝗽𝗮𝗿 𝗱𝗲́𝗳𝗮𝘂𝘁 
Toute tâche de +3 étapes 
→ Claude planifie AVANT de coder. Si ça déraille ? 
STOP et on re-planifie.
Des specs détaillées en amont pour zéro ambiguïté.

𝟮. 𝗦𝘁𝗿𝗮𝘁𝗲́𝗴𝗶𝗲 𝗦𝘂𝗯-𝗮𝗴𝗲𝗻𝘁𝘀 
Il délègue la recherche, l'exploration et l'analyse à des sous-agents. Le contexte principal reste clean. Un problème complexe ? On balance plus de compute dessus via les sub-agents. 1 tâche = 1 sub-agent. Focus total.

𝟯. 𝗕𝗼𝘂𝗰𝗹𝗲 𝗱'𝗮𝘂𝘁𝗼-𝗮𝗺𝗲́𝗹𝗶𝗼𝗿𝗮𝘁𝗶𝗼𝗻 (𝗹𝗲 𝗴𝗮𝗺𝗲-𝗰𝗵𝗮𝗻𝗴𝗲𝗿) 
À chaque correction de l'utilisateur → Claude met à jour un fichier [**lessons.md**](https://www.linkedin.com/redir/redirect/?url=http%3A%2F%2Flessons.md&urlhash=e-wA&mt=CDdvTxosoHedYibcMJKonMksC3b6aHw0HTx-0fbounpQmXOqJGjLZTYy0ghVOMa1m1tEte8w8yPRcaFzu9z9f8ES1q4hP31oYmxaSlLzRFYPsfNlomM5PWNVIg&isSdui=true). Il écrit ses propres règles pour ne PLUS JAMAIS refaire la même erreur. L'IA itère sur ses leçons jusqu'à ce que le taux d'erreur tombe. Plus tu l'utilises, plus elle devient intelligente sur TON projet.

𝟰. 𝗩𝗲́𝗿𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻 𝗮𝘃𝗮𝗻𝘁 𝘃𝗮𝗹𝗶𝗱𝗮𝘁𝗶𝗼𝗻 
Jamais de tâche marquée "done" sans preuve que ça marche. Le test : "Est-ce qu'un staff engineer validerait ça ?" Si la réponse est non → on recommence.

𝟱. 𝗘𝘅𝗶𝗴𝗲𝗿 𝗹'𝗲́𝗹𝗲́𝗴𝗮𝗻𝗰𝗲 
Pour chaque fix non-triviale : "Il y a une solution plus élégante ?" Si c'est hacky → "Sachant tout ce que je sais maintenant, implémente la solution élégante." Claude se challenge lui-même avant de livrer.

𝟲. 𝗖𝗼𝗿𝗿𝗲𝗰𝘁𝗶𝗼𝗻 𝗮𝘂𝘁𝗼𝗻𝗼𝗺𝗲 𝗱𝗲𝘀 𝗯𝘂𝗴𝘀 
Un bug report ? Claude le fix. Point. Pas de question. Pas de "tu peux m'expliquer ?" Il regarde les logs, les erreurs, les tests qui fail → et il résout. Zéro context-switching pour le dev.

Autre détail de dingue :
Boris n'a pas écrit UNE SEULE ligne de SQL depuis 6 mois. Claude pull les données BigQuery directement via CLI.

Ce qu'il faut retenir :
Il faut utiliser Claude comme une flotte d'ingénieurs seniors.

Tu mets ça en place sur ton projet et Claude devient exponentiellement meilleur à chaque session.

Son [**Claude.md**](https://www.linkedin.com/redir/redirect/?url=http%3A%2F%2FClaude.md&urlhash=4bqu&mt=gXxRjhrLoGk8ZGC6dR-BfwNuNTAOHJIdJToku8kYq3_KPseZmFVqTKsesmm-nDVWdvx1f0KNFnjWyOV4KMhWXBODEGRP8DhqnOl_Aa9sG788EsQehfWXLkCefg&isSdui=true) en image ;)