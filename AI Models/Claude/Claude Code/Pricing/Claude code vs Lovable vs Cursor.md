## Verdict cash

Non, Cursor et Lovable ne “se surendettent” pas en payant des abonnements Anthropic pour te faire plaisir. 

Ils ont des modèles de pricing **adossés au coût réel** (API-rate / crédits / top-ups / routing). Cursor le dit explicitement (“$20 au tarif API + extra at cost”). 

S’ils te donnaient du Claude “plein pot” illimité à €20/mois, ce serait une entreprise caritative… ou une entreprise morte.

Et la morale de l’histoire : **quand un outil est “pas cher”**, c’est rarement parce que la boîte souffre en silence ; c’est parce que **le compteur est planqué quelque part** (crédits, Auto, limites, fair-use).

## 2) “Mais l’API Claude est plus chère que mon Claude Code” — oui… et c’est normal

Deux mondes :

- **Abonnement (Claude Code / Claude app)** : 

  Prix fixe, mais **avec des limites** (caps/rate limits/quotas implicites) et une économie basée sur “la moyenne des usages”.

- **API** : 

  Tu payes **exactement** ce que tu consommes, scalable, production-grade.

Les tarifs API Claude (officiels) donnent une idée du pourquoi tu peux exploser une facture en “gros contexte + gros output” :

- **Sonnet 4.5** : **$3 / MTok input** et **$15 / MTok output**
- **Haiku 4.5** : **$1 / MTok input** et **$5 / MTok output**
- **Opus 4.5** : **$5 / MTok input** et **$25 / MTok output** 

👉 Conséquence directe : 

Un produit comme Cursor/Lovable **ne peut pas** te laisser taper du long contexte + gros agent en illimité sur Sonnet/Opus, à €20–€25/mois, sans te mettre un **compteur**.

## 3) Mini “calcul de coin de table” (pour sentir l’odeur du budget qui brûle)

Imaginons une requête agent un peu velue :

- 100k tokens en entrée (contexte, fichiers, instructions…)
- 10k tokens en sortie

Avec **Sonnet 4.5** (API) :

- input : 0.1 × $3 = **$0.30**
- output : 0.01 × $15 = **$0.15**
   Total ≈ **$0.45** pour *une* action “sérieuse”.

Tu en fais 200 dans le mois = **$90** juste pour ça.

Donc à $20/mois, Cursor/Lovable **doivent** : 

Limiter, router, compresser, facturer en crédits, ou te faire payer du supplément. Et c’est exactement ce qu’ils font. 

## 4) Comment ils tiennent debout sans “se sacrifier”

Sans inventer leur compta interne, les leviers standard (et très utilisés) sont :

- **Model routing** : 

  Haiku/“cheap” pour tâches simples, Sonnet/Opus seulement quand nécessaire.

- **Compression de contexte** : 

  On n’envoie pas tout ton repo à chaque fois.

- **Caching** : 

  Anthropic facture le cache beaucoup moins cher en “cache hits”, donc ça amortit certains patterns répétitifs. 

- **Batch** : 

  -50% sur input/output si certaines tâches peuvent être asynchrones. 

- **Crédits** : 

  Tu payes proportionnellement quand tu “vibe-codes” en mode bulldozer.

