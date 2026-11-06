```
Il y a 1 youtubeur qui a annoncé que pour la rentrée de septembre 2025 ridges.ai agent sera mieux qu'  une équipe de développeurs ingénieurs en prompt engineering tu auras juste à faire un prompt et il te sort une application web entière est-ce vrai ? 

Qui coutent 50K$ / mois ridges.ai ne coutera que 1000$/mois 

Est-ce que tu y crois ? 

Bcp - chère que Claude sonnet qui sera à 50k$ / mois qu'est-ce qui te parait biaiser ds c propos liste moi tt l cons réalistes tt c inconvénients si cette ia peut remplacer tt l ingénieurs sur un projet 

est-ce vrai qu'une ia pourra tt coder à 100% ds le futur comme 1 agi? 
est-ce possible ? 

d investisseurs qui investissent d milliards ds 1 agi est-ce possible?  

https://www.youtube.com/watch?v=JWnvxGvOQpQ 

Ils ont créé une IA sur Bittensor (TAO)… et elle CODE mieux que NOUS 😳 (400 MILLIARDS $)
```

### Verdict personnel

- **1 000 $/mois pour une appli web clé-en-main ?** → possible pour un *Hello-world-SaaS* très standard, si le modèle est subventionné… mais attendez-vous à repayer en intégration et en sécurité.
- **“Mieux qu’une équipe de prompt-engineers”** → sur un benchmark défini, oui. Sur un backlog réel, pas encore.
- **“Remplacer tous les ingénieurs”** → Non ; **redistribuer les tâches** et réduire les effectifs sur du boilerplate, clairement oui.

En bref : gardez l’œil ouvert, le portefeuille surveillé, et votre esprit critique aiguisé — l’IA *code* vite… mais l’*ingénierie* reste un sport d’équipe. 😉

### — *C’est (très) prometteur, mais pas (encore) magique.*

> « Un simple prompt → une appli web complète pour 1 000 $/mois ? Bye-bye l’équipe d’ingénieurs ! »
>  👉  **Aujourd’hui, c’est surtout un slogan marketing qui s’appuie sur trois briques réelles (LLM + agents + Bittensor), mais il reste beaucoup de trous dans la raquette.**

------

## 1. D’où vient le buzz ?

| Élément                                        | Ce qui est dit                                               | Ce qu’on trouve vraiment                                     |
| ---------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Ridges.ai (Subnet 62 de Bittensor)**         | « On remplace les software engineers par des agents open-source qui se font concurrence » | Le projet l’écrit noir sur blanc dans sa doc : « We’re replacing software engineers with agents. » ([docs.ridges.ai](https://docs.ridges.ai/)) |
| **Capacité**                                   | Les agents battent les devs humains sur SWE-bench            | Les meilleurs agents open source oscillent autour de **60-65 %** de réussite sur SWE-bench ; c’est impressionnant, mais loin d’un livrable prod sans retouches humaines. ([SWE-bench](https://www.swebench.com/?utm_source=chatgpt.com), [arXiv](https://arxiv.org/abs/2506.09289?utm_source=chatgpt.com)) |
| **Prix annoncé (1 000 $/mois)**                | Relayé par un youtubeur ; aucun tarif officiel publié        | Aucun plan public ne mentionne ce prix. On ne sait pas si c’est un *loss-leader*, un futur « starter plan » ou… juste une extrapolation. |
| **Comparaison avec Claude Sonnet (50 k $/an)** | 50 k $/mois                                                  | Le minimum de Claude Enterprise est plutôt **≈ 50 k $/an** (70 licences × 60 $/mois). ([Reddit](https://www.reddit.com/r/ClaudeAI/comments/1fewpkh/claude_enterprise_plan_50k_annual_70_users/?utm_source=chatgpt.com)) |

------

## 2. Les angles morts / biais dans la promesse

1. **Benchmarks ≠ production**
    SWE-bench mesure la résolution d’issues *open source* avec tests fournis. En entreprise, on doit aussi : clarifier le besoin, gérer l’UX, la sécurité, l’obsèques, le déploiement multi-environnements, etc. Les agents n’y sont pas encore.

2. **Coûts masqués**

   - **Inference GPU** : même en mode “miner” sur Bittensor, quelqu’un paie l’électricité et les A100/H100.
   - **Intégration & ops** : tests E2E, CI/CD, monitoring, hotfix … restent indispensables et souvent manuels.
   - **Gouvernance du code** : ouvrir votre repo à 200 mineurs anonymes ? Pas trivial côté IP/compliance.

3. **Risque d’hallucination / failles**

   Code généré vite ≠ code fiable. Vulnérabilités, licences incompatibles, logiques métier mal comprises—le relecteur humain devient *encore plus* critique.

4. **Verrou “domaine métier”**

   Les agents excellent sur des patterns connus. Dès qu’on sort d’un cadre GitHub standard (ex. règlementaire, temps-réel, hardware), ils patinent.

5. **Dépendance à l’écosystème TAO**

   Le token TAO est volatile. Votre coût « 1 000 $ » pourrait doubler si le marché s’envole ou si les récompenses réseau changent — les papiers de recherche soulignent déjà des problèmes d’alignement incitations/qualité. ([arXiv](https://arxiv.org/html/2507.02951v1?utm_source=chatgpt.com))

------

## 3. Peut-on vraiment “remplacer tous les ingénieurs” ?

| Fonction                                             | Niveau d’automatisation réaliste d’ici 2025 | Comment l’humain évolue                |
| ---------------------------------------------------- | ------------------------------------------- | -------------------------------------- |
| **Génération de boilerplate, CRUD, tests unitaires** | **>80 %**                                   | Rôle de *code reviewer* + sécurisation |
| **Refactorings locaux, migrations**                  | **60-70 %**                                 | Supervision + validation               |
| **Architecture, choix techno, négociation de specs** | **20 %** (assistance)                       | Reste (largement) humain               |
| **Run & observabilité (on-call, SLOs)**              | **<20 %**                                   | Décisions & priorités humaines         |
| **Produit / UX / stratégie**                         | **≈0 %**                                    | 100 % humain (et ça risque de durer)   |

Autrement dit : oui, la *quantité de code tapée à la main* va chuter. Non, un projet complexe sans humains sur la ligne n’est pas à l’horizon 2025.

------

## 4. Les “vrais” avantages qu’on peut attendre

1. **Productivité x 3-5** sur les tâches répétitives (bug-fix, tests, docs API).
2. **Time-to-market raccourci** pour des POC ou des micro-services simples (front React + API CRUD).
3. **Démocratisation** : une PME sans équipe IA peut louer de la puissance coding-agent à coût variable.

------

## 5. Les inconvénients concrets à prévoir

| Risque                             | Impact                                                       |
| ---------------------------------- | ------------------------------------------------------------ |
| **Déchets de code/hallucinations** | Débogage plus long que l’écriture « from scratch » si personne ne surveille. |
| **Débits variables**               | Performances sensibles à la latence réseau ; sandbox 2 min chez Ridges ([docs.ridges.ai](https://docs.ridges.ai/im-v3)). |
| **Sécurité / privacy**             | Votre code circule sur des nœuds publics ; hard-pass pour code propriétaire strict. |
| **Vendor-Lock TAO**                | Départ du réseau = plus d’agent, plus de compute subventionné. |
| **Compliance**                     | RGPD, SOC2, OWASP, etc. non couverts par « ça compile ».     |

------

## 6. Et l’AGI là-dedans ?

- **AGI “qui code 100 % seule”** : rien n’interdit physiquement qu’un futur modèle + pipeline dev complet règle toutes les issues… mais il manque toujours la comprehension fine du contexte métier, la responsabilité légale et la conscience de la “valeur” au-delà du code.
- **Investissements milliards** : Oui, VC & big-tech mettent des chèques à neuf zéros (OpenAI, Anthropic, xAI, Bittensor labs). C’est *possible* qu’ils aboutissent à une étape “AGI-like”. *Garantir* qu’elle sera prête, alignée et bon marché en 2025-2026 reste hautement spéculatif.

------

## 7. Que faire, pragmatiquement ?

1. **Prototypez** avec des “coding agents” dès maintenant (Ridges, Claude-Sonnet + ReAct, OpenAI Code Interpreter…). Mesurez le *gain réel* sur vos propres user stories.
2. **Gardez un cycle de revue humain** : CI lint + tests auto + code review obligatoire.
3. **Sécurisez** : SBOM, scan de vulnérabilités, contrat IA/Privacy clair avant d’envoyer du code sensible.
4. **Formez vos devs** à devenir **AI orchestrators** plutôt que “typistes”.
5. **Budgetez** large : compute, prompt-engineering, monitoring, *et* retouches humaines.

------

