# Étape 30 ter — RAG — Transformations de requête

> Étape 30 ter du parcours · Prérequis : [Reranking par cross-encodeur](<30b-RAG-Reranking-Cross-Encodeur.md>) · Suite : [Découpage avancé et compression](<30d-RAG-Decoupage-Avance-et-Compression.md>)

**Dossier :** 05-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  
**Nom du fichier :** 30c-RAG-Transformations-de-Requete.md

## Définition

Une transformation de requête réécrit la question de l'utilisateur **avant** la recherche, parce que la question telle qu'elle est tapée est rarement la meilleure requête possible : elle emploie d'autres mots que les documents, contient des acronymes ou un mélange d'arabe, d'anglais et de français, réunit plusieurs besoins en une phrase, ou porte des contraintes implicites comme un émirat ou une date. L'étape 30 bis a montré qu'un reranker ne rattrape jamais un document que la première étape n'a pas trouvé ; la requête est le seul levier sur ce rappel. On distingue six familles. La **réécriture** normalise la question et la traduit dans le vocabulaire des documents. Le **multi-query** produit plusieurs reformulations, lance une recherche pour chacune et fusionne les listes par RRF (c'est la technique dite RAG-Fusion). **HyDE** fait écrire une réponse hypothétique et cherche avec ce texte. Le **step-back** pose la question plus générale dont la question posée est un cas particulier. La **décomposition** découpe une question composée en sous-questions. Le **self-query** sépare le texte à chercher des filtres de métadonnées (émirat, type de document, année). Toutes, sauf la réécriture par règles, coûtent au moins un appel à un LLM.

## Rôle dans un agent

La transformation se place entre la perception et l'action : l'agent a reçu la question, et avant d'appeler son outil `chercher`, il décide quelle requête envoyer, ou quelles requêtes. Dans un agent qui appelle ses outils, le modèle écrit déjà lui-même l'argument `requete` de l'appel d'outil : c'est une réécriture implicite, non mesurée. Ce fichier rend ces transformations explicites, déterministes à tester et mesurables par le Recall@k (étape 25). Le composant concerné est le **réécrivain de requête**, souvent accompagné d'un **routeur** qui choisit la technique selon le type de question : une question vague appelle des reformulations, une comparaison une décomposition, une question qui nomme un émirat et une année un self-query. En architecture hexagonale, une transformation est une fonction pure de la question vers une liste de couples (requête, filtre) et une politique de fusion ; le LLM est derrière le même port que dans tout le parcours, si bien que le faux LLM des tests et l'adaptateur Claude s'échangent sans toucher au reste.

## Équation complète

Multi-query : la question q₀ = q et ses m reformulations q₁ … qₘ donnent chacune un top-k ; on note leur union :

$$
U_k(q) = \bigcup_{i=0}^{m} \text{top-}k(q_i)
$$

Théorème de l'union, démontré au point 2 :

$$
\text{Recall}\big(U_k(q)\big) \ge \max_{0 \le i \le m} \text{Recall@}k(q_i)
$$

Fusion des listes par RRF (étape 24), puis troncature à k :

$$
\text{RRF}(d) = \sum_{i=0}^{m} \frac{1}{k_{RRF} + \text{rang}_i(d)}
$$

HyDE : on cherche avec un document hypothétique h écrit par le LLM ; dans sa version d'origine, avec des embeddings, on moyenne les vecteurs de n hypothèses et celui de la question :

$$
v_{HyDE} = \frac{1}{n + 1}\Big(E(q) + \sum_{j=1}^{n} E(h_j)\Big)
$$

Step-back : la question générale g est cherchée en plus de la question posée, et les deux listes sont fusionnées :

$$
L(q) = \text{top-}k\; \text{RRF}\big(\text{top-}k(q),\; \text{top-}k(g)\big)
$$

Décomposition en J sous-questions, fusionnées par entrelacement ; position, dans la liste entrelacée, du premier document de la liste j (point 4) :

$$
\text{pos}\big(\text{top-}1(q^{(j)})\big) \le j \qquad 1 \le j \le J
$$

Self-query : un filtre φ sur les métadonnées restreint le corpus 𝒟 à S, puis on classe la requête nettoyée q′ :

$$
S = \{\, d \in \mathcal{D} : \varphi(d) \,\} \qquad L(q) = \underset{d \in S}{\text{top-}k}\; s(q', d)
$$

Le rang dans S ne dépasse jamais le rang dans 𝒟 (point 5) :

$$
\text{rang}_S(d) \le \text{rang}_{\mathcal{D}}(d) \qquad \text{pour tout } d \in S
$$

Si le filtre écarte des pertinents, le rappel est plafonné (point 6) :

$$
\text{Recall@}k \le \frac{|\text{Rel} \cap S|}{|\text{Rel}|}
$$

Coût d'une transformation, en série :

$$
T = n_{LLM}\, t_{LLM} + n_{rech}\, t_{rech}
$$

## Décryptage des symboles

$$
q,\; q_0,\; q_1, \dots, q_m
$$

**Sens :** la question posée (q₀ = q) et ses m reformulations · **Type / plage :** chaînes, m ≥ 1 · **Variable Python :** `q`, `variantes`

$$
\text{top-}k(q_i)
$$

**Sens :** les k premiers documents renvoyés par la recherche pour la requête qᵢ · **Type / plage :** liste d'au plus k identifiants · **Variable Python :** `moteur.chercher(requete, K)`

$$
U_k(q)
$$

**Sens :** l'union des listes de toutes les requêtes · **Type / plage :** ensemble d'au plus (m + 1)k identifiants · **Variable Python :** `union`

$$
\text{Rel}
$$

**Sens :** les documents pertinents de la question, fixés par un expert · **Type / plage :** ensemble non vide · **Variable Python :** `rel`

$$
k_{RRF},\; \text{rang}_i(d)
$$

**Sens :** constante de RRF, et rang de d dans la liste i · **Type / plage :** 60 ; entier ≥ 1 · **Variable Python :** `k_rrf`, `rang`

$$
h_j,\; E
$$

**Sens :** j-ième document hypothétique écrit par le LLM, et encodeur d'embeddings · **Type / plage :** chaîne ; fonction texte → vecteur · **Variable Python :** `demander(llm, "hyde", q)["document"]` ; ici BM25 remplace E

$$
g
$$

**Sens :** la question générale du step-back · **Type / plage :** chaîne · **Variable Python :** `generale`

$$
q^{(1)}, \dots, q^{(J)}
$$

**Sens :** les J sous-questions de la décomposition · **Type / plage :** chaînes, J ≥ 2 · **Variable Python :** `sous`

$$
\varphi,\; S
$$

**Sens :** le prédicat de filtre sur les métadonnées, et l'ensemble des documents qu'il garde · **Type / plage :** fonction document → booléen ; partie de 𝒟 · **Variable Python :** `filtre_depuis(filtres)`, documents `d` tels que `garder(d)`

$$
q'
$$

**Sens :** la requête du self-query, débarrassée des contraintes devenues filtres · **Type / plage :** chaîne · **Variable Python :** `objet["requete"]`

$$
\text{rang}_S(d),\; \text{rang}_{\mathcal{D}}(d)
$$

**Sens :** rang de d parmi les documents filtrés, et parmi tout le corpus · **Type / plage :** entiers ≥ 1 · **Variable Python :** position dans `avec` et dans `sans`

$$
n_{LLM},\; n_{rech},\; t_{LLM},\; t_{rech}
$$

**Sens :** nombre d'appels au LLM et de recherches, et leurs durées · **Type / plage :** entiers ; millisecondes · **Variable Python :** `couts[nom]`, `t_llm_ms`, `t_recherche_ms`

## Démonstration

### 1. Exemple fait à la main : une réécriture par règles, sans LLM

La question Q1, « رسوم DLD sur un off-plan », mélange un mot arabe (rusūm, « frais »), un acronyme (DLD, le département foncier de Dubaï) et un anglicisme. Après retrait des mots vides, ses termes sont رسوم, dld, off et plan : aucun document du corpus n'emploie les trois premiers, et seul « plan » correspond, dans les deux fiches d'achat sur plan, celle de Dubaï et celle d'Abu Dhabi. BM25 renvoie donc ces deux fiches et rien d'autre ; sur les deux documents pertinents, la fiche des frais de transfert manque, et le Recall@3 vaut 1/2 = 0,5. Un glossaire métier de quatre entrées remplace « DLD » par « département foncier dubaï », « رسوم » par « frais » et « off-plan » par « achat sur plan ». La requête devient « frais département foncier dubaï sur un achat sur plan », dont les termes figurent tous dans la fiche des frais de transfert : le Recall@3 passe à 1, sans aucun appel à un LLM. La normalisation de l'arabe de l'étape 22 s'applique avant la recherche dans le glossaire, si bien que « أجرة » écrit avec ou sans hamza tombe sur la même entrée. C'est le premier réflexe de la feuille blanche : ce qu'une règle sait faire, on ne le demande pas à un modèle.

### 2. L'union des requêtes domine chaque requête seule

Chaque liste top-k(qᵢ) est contenue dans l'union, par définition de l'union. Donc, parce que l'intersection respecte l'inclusion, Rel ∩ top-k(qᵢ) ⊆ Rel ∩ U, et en comptant les éléments puis en divisant par |Rel| :

$$
\text{Recall@}k(q_i) = \frac{|\text{Rel} \cap \text{top-}k(q_i)|}{|\text{Rel}|} \le \frac{|\text{Rel} \cap U_k|}{|\text{Rel}|} = \text{Recall}(U_k)
$$

L'inégalité vaut pour chaque i, donc pour le maximum. Sur la question Q2, « Combien coûte l'achat d'un appartement à Dubaï ? », la question et ses trois reformulations obtiennent chacune un Recall@3 de 0,33, et leur union un rappel de 1 : chaque reformulation trouve une facette du coût (frais de transfert, commission de l'agent, enregistrement de l'hypothèque). Mais l'union contient 8 documents, pas 3 : le théorème compare des budgets différents, puisque |U| ≤ (m + 1)k. Il dit que le multi-query **élargit** l'ensemble des candidats ; il ne dit rien de ce qui reste après la coupe à k.

### 3. La fusion RRF tronquée à k peut perdre ce que l'union avait trouvé

Après fusion des quatre listes de Q2 par RRF, le top-3 n'a plus qu'un rappel de 0,67. Le calcul se fait à la main. La fiche des frais de transfert est 2ᵉ de la question et 1ʳᵉ de la première reformulation :

$$
\frac{1}{62} + \frac{1}{61} = 0{,}0325
$$

La fiche d'achat sur plan d'Abu Dhabi, hors sujet, est 3ᵉ de deux listes :

$$
\frac{1}{63} + \frac{1}{63} = 0{,}0317
$$

La fiche de l'hypothèque, pertinente, n'est trouvée que par une liste, au 1ᵉʳ rang :

$$
\frac{1}{61} = 0{,}0164
$$

Elle est à égalité avec la commission de l'agent et la fiche d'achat sur plan de Dubaï ; le départage par nom place la commission en 3ᵉ position, et la fiche de l'hypothèque sort du top-3. C'est exactement la propriété de consensus de l'étape 24, point 4 : deux rangs moyens battent un premier rang isolé. Elle est souhaitable quand les listes sont des **reformulations d'un même besoin**, parce que l'accord entre elles signale un bon document ; elle est nuisible quand chaque liste couvre une **facette différente**, parce qu'un document présent dans une seule liste est justement celui qu'on voulait.

### 4. L'entrelacement garantit chaque facette dès que k ≥ J

Pour des sous-questions, on fusionne donc autrement : l'entrelacement prend le 1ᵉʳ document de chaque liste, puis le 2ᵉ de chaque liste, et ainsi de suite, sans doublon. Montrons que le premier document de la liste j occupe une position au plus égale à j. Au premier tour, l'algorithme parcourt les listes 1, 2, …, j dans l'ordre et ajoute au plus un document par liste ; quand il arrive à la liste j, au plus j − 1 documents ont été ajoutés avant. Soit le premier document de la liste j est déjà présent, et sa position est au plus j − 1, soit il est ajouté à la position j. Dans les deux cas, sa position est au plus j. Si k ≥ J, le meilleur document de **chaque** sous-question est donc dans le top-k. Sur Q2, les trois sous-questions (frais de transfert, commission, hypothèque) ont chacune leur document pertinent au premier rang, et la décomposition obtient un Recall@3 de 1 ; sur Q5, la comparaison Dubaï et Abu Dhabi passe de 0,5 à 1. La question Q5 brute échouait pour une raison précise : « abu » et « dhabi » ne figurent que dans quelques documents et ont donc un IDF élevé (étape 22), si bien que les quatre fiches d'Abu Dhabi passent devant la fiche de Dubaï. La décomposition donne à chaque émirat sa propre recherche.

### 5. RRF ne lit que les rangs, et c'est ici indispensable

Les requêtes d'une même transformation produisent des scores d'échelles très différentes. Sur Q4, la question longue et précise (« Mon studio à Dubai Marina à 60 000 AED peut-il passer à 70 000 AED au renouvellement ? ») donne à l'annonce d'un studio un BM25 de 20,40, parce que l'annonce partage avec elle les nombres et les noms de lieu ; la question générale du step-back ne dépasse pas 4,04. En additionnant les scores, l'annonce passe en tête alors qu'elle ne répond pas à la question ; avec RRF, c'est la règle sur la hausse des loyers, trouvée par les deux listes. Sur Q3, le texte HyDE, plus long et écrit dans le vocabulaire des documents, atteint un BM25 de 17,26, contre 3,17 pour la question : un seuil commun sur ces scores n'aurait aucun sens. L'étape 24 (point 3) a démontré que RRF ne dépend que des rangs ; c'est la bonne fusion par défaut quand les requêtes n'ont ni la même longueur ni le même vocabulaire.

### 6. Un filtre correct ne fait perdre aucun pertinent et gagne en précision

Le self-query restreint le corpus à S avant de classer. On suppose deux choses : les statistiques de BM25 (IDF et longueur moyenne) restent celles du corpus entier, ce que fait la classe `Moteur`, et le filtre est **correct**, c'est-à-dire que Rel ⊆ S. Le score d'un document ne change pas quand on filtre, donc l'ordre relatif des documents de S non plus. Le rang de d dans S compte les documents de S classés devant lui, qui sont aussi des documents de 𝒟 classés devant lui :

$$
\text{rang}_S(d) = 1 + |\{ d' \in S : d' \text{ devant } d \}| \le 1 + |\{ d' \in \mathcal{D} : d' \text{ devant } d \}| = \text{rang}_{\mathcal{D}}(d)
$$

Tout pertinent présent dans le top-k sans filtre a donc un rang au plus k dans S, et il reste dans le top-k avec filtre : le nombre de pertinents du top-k ne peut que croître. Comme le Recall@k et la P@k (étape 26) ont le même numérateur et des dénominateurs fixes, |Rel| et k, **les deux** ne peuvent que croître. Sur Q6, « Règlements de 2025 sur la location à Sharjah », le filtre (émirat Sharjah, type règlement, année au moins 2025) fait passer les candidats de 21 à 2 ; pour la requête « location », la P@3 passe de 0 à 0,67 et le Recall@3 de 0 à 1. Le programme vérifie l'inégalité pour tous les k de 1 à 10. Si l'on recalculait l'IDF sur S seulement, les scores changeraient et l'ordre aussi : la garantie tomberait.

### 7. Un filtre faux coûte du rappel, sans prévenir

Si le filtre écarte un pertinent, ce document n'a plus aucune chance d'être renvoyé, et le rappel est plafonné par |Rel ∩ S| / |Rel|, exactement comme l'étape 1 plafonne le reranker. Trois erreurs le montrent. Si le LLM extrait « Dubaï » au lieu de « Sharjah », S ne contient aucun des deux pertinents : Recall@3 = 0. Si l'année minimale est fixée à 2026, S est vide et la liste aussi. Si, sur la comparaison Q5, le filtre ne garde que Dubaï, la fiche d'Abu Dhabi disparaît et le Recall@3 tombe à 0,5. Le danger est que rien ne signale l'erreur : une liste courte ressemble à une question sans réponse. Un filtre se valide donc contre une liste fermée de valeurs (un schéma strict, étape 8), et une liste vide ou très courte déclenche une seconde recherche sans filtre, journalisée.

### 8. Chaque technique gagne là où elle est faite pour gagner

Le programme applique les huit stratégies aux six questions, avec k = 3 :

| Stratégie | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Moyenne | Appels LLM | Recherches |
|---|---|---|---|---|---|---|---|---|---|
| brute | 0,50 | 0,33 | 0,00 | 0,50 | 0,50 | 0,50 | 0,3889 | 0 | 6 |
| règles (glossaire) | 1,00 | 0,33 | 0,00 | 0,50 | 0,50 | 0,50 | 0,4722 | 0 | 6 |
| réécriture par LLM | 1,00 | 0,33 | 0,50 | 0,50 | 0,50 | 0,50 | 0,5556 | 6 | 6 |
| multi-query + RRF | 1,00 | 0,67 | 1,00 | 1,00 | 0,50 | 1,00 | 0,8611 | 6 | 24 |
| HyDE | 1,00 | 0,67 | 1,00 | 1,00 | 1,00 | 0,50 | 0,8611 | 6 | 6 |
| step-back | 0,50 | 0,33 | 0,50 | 1,00 | 0,50 | 0,00 | 0,4722 | 6 | 12 |
| décomposition | 1,00 | 1,00 | 0,50 | 0,50 | 1,00 | 0,50 | 0,7500 | 6 | 13 |
| self-query | 1,00 | 0,33 | 0,00 | 0,50 | 1,00 | 1,00 | 0,6389 | 6 | 6 |

Le tableau se lit colonne par colonne. Q1 (acronyme et arabe) est réglée par le glossaire seul. Q2 (question vague à plusieurs facettes) n'est complètement réglée que par la décomposition. Q3 (« Mon proprio peut-il me faire payer plus cher l'an prochain ? ») n'a aucun mot commun avec les règles sur les loyers : HyDE et le multi-query la règlent, le self-query n'y peut rien puisqu'elle ne porte aucune contrainte de métadonnée. Q4 (cas très particulier) est réglée par le step-back, qui va chercher la règle générale. Q6 (contrainte d'émirat et d'année) est réglée par le self-query ; le step-back y tombe à 0, parce qu'en généralisant la question il a perdu « Sharjah », et HyDE à 0,5, parce que l'hypothèse suit les connaissances générales du modèle et oublie « 2025 ». Une limite doit être dite clairement : les sorties du faux LLM ont été écrites à la main, en connaissant le corpus. Le tableau illustre des mécanismes ; il ne mesure pas la qualité d'un vrai modèle, qui ignore le vocabulaire interne de l'entreprise. Seule une mesure sur son propre jeu annoté décide.

### 9. Le coût : un appel au LLM change l'ordre de grandeur

Chaque stratégie, sauf « brute » et « règles », ajoute un appel au LLM par question, et certaines multiplient les recherches : 4 par question pour le multi-query (la question et trois reformulations), 2 pour le step-back, une par sous-question pour la décomposition. Avec des durées illustratives de 700 ms par appel au LLM et 40 ms par recherche, exécutés en série, on obtient en moyenne 40 ms par question pour la recherche brute, 860 ms pour le multi-query et 787 ms pour la décomposition : le LLM domine. D'où trois pratiques : appliquer d'abord les règles, router vers une transformation seulement les questions qui en ont besoin, et mettre en cache les réécritures des questions fréquentes. Les recherches d'une même transformation sont indépendantes et peuvent partir en parallèle, ce qui ramène leur part au temps d'une seule.

## Effets et comportement

- **Plus de reformulations** élargit l'union (point 2) et coûte une recherche de plus chacune ; au-delà de trois ou quatre, les reformulations se ressemblent et ne fabriquent qu'un faux consensus.
- **RRF favorise l'accord entre listes** (point 3) : bon pour des paraphrases, mauvais pour des facettes, où l'on entrelace (point 4).
- **HyDE aide quand la question et les documents n'ont pas le même registre** (langage courant contre langage réglementaire) ; il échoue quand la question porte une contrainte que le modèle ignore, comme une date.
- **Le step-back aide les questions trop particulières** et nuit à celles dont le détail est la contrainte (Q6).
- **Un filtre juste augmente précision et rappel à k fixé ; un filtre faux les plafonne** (points 6 et 7).
- **Chaque transformation ajoute de la latence** (point 9) ; le routeur décide si elle en vaut la peine.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| top-k(qᵢ) | `moteur.chercher(requete, K)` |
| réécriture par règles | `developper_glossaire(question)`, `normaliser_mot` |
| réécriture par LLM | `reecriture(llm, moteur, q)` |
| q₁ … qₘ | `demander(llm, "multi", q)["variantes"]` |
| Uₖ(q) | `union = set().union(*listes)` |
| RRF(d) | `rrf(classements)`, code canonique de l'étape 24 ; `fusion(listes, k)` |
| hⱼ | `demander(llm, "hyde", q)["document"]` |
| g | `demander(llm, "step_back", q)["question"]` |
| q⁽¹⁾ … q⁽ᴶ⁾ | `demander(llm, "decomposition", q)["sous_questions"]` |
| entrelacement | `entrelacer(listes, k)` |
| φ, S | `filtre_depuis(filtres)` |
| q′ | `demander(llm, "self_query", q)["requete"]` |
| T | `latence_ms(appels_llm, recherches)` |

### Déroulé, ligne par ligne

**`Bloc`, `Reponse` et `texte`** sont le port LLM canonique du parcours : une réponse a un `stop_reason` et une liste de blocs `content`. **`idf_bm25`, `bm25_score` et `rrf`** sont recopiés tels quels des étapes 22 et 24 ; **`recall_at_k`** et **`precision_at_k`** suivent les conventions des étapes 25 et 26, avec un dénominateur toujours égal à k pour la précision.

**`TABLE_ARABE`** est la table de normalisation de l'étape 22 : les alefs avec hamza ou madda deviennent ا, ة devient ه, le tatweel et les diacritiques sont supprimés. **`tokeniser`** applique NFC, la table, les minuscules, découpe par `\w+` et retire les mots vides. **`normaliser_mot`** fait de même pour un seul mot et enlève la ponctuation collée, pour que « off-plan » et « DLD » se cherchent dans le glossaire. **`developper_glossaire`** remplace chaque mot connu : sur Q1, `"رسوم DLD sur un off-plan"` devient `"frais département foncier dubaï sur un achat sur plan"`.

**`Doc`** porte, en plus du texte, les métadonnées que le self-query filtre : émirat, année et type. Les 21 documents sont fictifs ; seuls les 4 % de frais de transfert à Dubaï et la TVA de 5 % reprennent des chiffres vérifiés du parcours.

**`Moteur`** compte ses recherches. `chercher(requete, k, filtre)` calcule BM25 avec les statistiques du corpus **entier** (`TOKENS`), écarte les documents que le filtre refuse, garde les scores strictement positifs, trie par score décroissant puis par identifiant, et coupe à k. `scores(requete)` renvoie tous les scores, pour le point 5.

**`CONSIGNES`** contient la consigne système de chaque technique, telle qu'on l'enverrait à un vrai modèle, avec le format JSON attendu. **`SCRIPT`** associe à chaque couple (technique, question) la sortie du faux LLM.

**`FauxLLM.create`** a la signature de l'adaptateur Claude : il retrouve la technique à partir de la consigne système, lit la sortie prévue et la renvoie sérialisée en JSON dans un bloc texte, avec `stop_reason = "end_turn"`. Il compte ses appels.

**`demander(llm, technique, question)`** envoie la consigne et la question, vérifie le `stop_reason`, concatène les blocs texte, décode le JSON avec `json.loads` et refuse tout ce qui n'est pas un objet : une sortie invalide lève `ValueError` au lieu de produire une requête vide en silence.

**`filtre_depuis(filtres)`** construit le prédicat φ. L'émirat peut être une valeur ou une liste ; `annee_min` garde les documents de cette année et des suivantes ; un dictionnaire vide laisse tout passer.

**`fusion`** applique RRF et coupe à k. **`entrelacer`** parcourt les rangs, puis les listes, et n'ajoute un document que s'il n'est pas déjà présent : c'est l'algorithme du point 4.

**Les huit stratégies** ont toutes la même signature `(llm, moteur, q) -> list[str]`, ce qui permet de les ranger dans le dictionnaire `STRATEGIES` et de les comparer dans une seule boucle. `multi_query` cherche la question et ses variantes, puis fusionne par RRF ; `step_back` fusionne la question et la question générale ; `decomposition` entrelace les listes des sous-questions ; `self_query` cherche la requête nettoyée avec le filtre extrait.

**`latence_ms`** applique le modèle de coût du point 9.

**`main()`**, bloc par bloc.

1. La réécriture par règles de Q1, puis la vérification qu'un mot arabe écrit avec ou sans hamza donne la même forme normalisée.
2. La boucle sur `STRATEGIES` remplit le tableau du point 8 ; les compteurs `llm.appels` et `moteur.recherches`, lus avant et après chaque stratégie, donnent son coût. Le dictionnaire `attendu` vérifie les 48 valeurs de rappel et `couts` les 16 compteurs ; trois latences moyennes sont affichées.
3. Pour chaque question, le programme recalcule les listes du multi-query et vérifie l'inégalité de l'union, la borne de la fusion et la taille de l'union ; pour Q2, il affiche les rappels et les trois scores RRF du point 3.
4. La comparaison somme des scores contre RRF sur Q4, et les échelles de BM25 de Q3 (point 5).
5. Le filtre correct sur la requête « location » : l'ordre relatif est conservé (`avec` est `sans` restreint à S), l'inégalité des touchés est vérifiée pour k de 1 à 10, puis la P@3 et le Recall@3 avant et après ; ensuite les trois filtres faux du point 7.
6. Un faux LLM qui renvoie une liste au lieu d'un objet JSON : `demander` doit lever `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`texte(t)`** — Cette petite fabrique du port LLM canonique se comporte comme un secrétaire qui glisse une phrase dans une enveloppe standard : elle reçoit une chaîne de caractères et renvoie un `Bloc` de type « text » qui la contient, sans rien vérifier ni transformer. Le faux LLM s'en sert pour emballer sa sortie JSON, de sorte que `demander` reçoit exactement la même forme de réponse que celle d'un vrai modèle et n'a pas à savoir à qui il parle.

**`idf_bm25(n_t, n_docs)`** — C'est le crieur canonique de l'étape 22, recopié tel quel, qui annonce le poids d'un mot selon sa rareté dans le corpus : la fonction reçoit le nombre de documents qui contiennent le terme et le nombre total de documents, ici 21, puis renvoie le logarithme de 1 + (N − n + 0,5) / (n + 0,5), une valeur toujours positive qui grandit quand le mot se fait rare. Elle n'est appelée que par `bm25_score`, pour qu'un mot comme « Ejari » pèse bien plus lourd que « frais », présent dans de nombreuses fiches.

**`bm25_score(requete, doc, corpus, k1, b)`** — C'est le juge lexical canonique de l'étape 22, qui note un document pour une requête mot par mot : la fonction reçoit la requête et le document sous forme de listes de mots, le corpus entier et les réglages k1 = 1,5 et b = 0,75 par défaut, puis additionne, pour chaque mot présent, son IDF multiplié par une partie fréquence saturée et corrigée par la longueur du document. Elle renvoie ce score, dont l'échelle dépend fortement de la requête : sur Q4, le meilleur document atteint 20,40 pour la question brute mais seulement 4,04 pour la question step-back, ce qui interdit d'additionner des scores venus de requêtes différentes.

**`rrf(classements, k_rrf)`** — C'est le jury canonique de l'étape 24, qui fusionne plusieurs classements en ne regardant que les places obtenues : la fonction reçoit une liste de classements et la constante k, 60 par défaut, ajoute à chaque document 1 / (k + rang) pour chaque liste où il figure, et renvoie les couples (document, score) triés par score décroissant, les égalités départagées par l'identifiant. Parce qu'elle ignore les échelles de BM25, elle met `hausse-loyer` en tête sur Q4 là où une simple somme des scores aurait choisi l'annonce `annonce-marina`.

**`recall_at_k(retrouves, pertinents, k)`** — C'est le pêcheur de l'étape 25, qui compte la part des poissons connus remontés dans ses k premiers casiers : la fonction reçoit la liste retrouvée, l'ensemble des pertinents et k, lève `ValueError` si k est inférieur à 1, renvoie `None` s'il n'y a aucun pertinent, et sinon divise le nombre de pertinents trouvés dans les k premiers par le nombre total de pertinents. C'est la note principale du tableau du point 2, où la recherche brute obtient en moyenne 0,3889 et le multi-query comme HyDE 0,8611, sur six questions et avec k = 3.

**`precision_at_k(retrouves, pertinents, k)`** — Elle regarde la même pêche par l'autre bout, en se demandant quelle part des k prises est vraiment utile : la fonction reçoit les mêmes trois arguments, compte les pertinents parmi les k premiers résultats et divise toujours par k, même si la liste est plus courte, selon la convention de l'étape 26. Le programme s'en sert au point 5 pour montrer l'effet d'un bon filtre de métadonnées sur la requête « location » : la précision à 3 passe de 0 à 0,67, pendant que le rappel passe de 0 à 1.

**`tokeniser(texte_)`** — C'est le découpeur commun à toutes les stratégies, qui transforme un texte en liste de mots comparables : la fonction reçoit un texte, le met sous la forme Unicode NFC, lui applique `TABLE_ARABE`, qui unifie les alefs, remplace le tā' marbūṭa par le hā' et supprime le tatweel et les diacritiques, le met en minuscules, en extrait les suites de caractères de mot avec `\w+` et retire les mots vides. Elle renvoie la liste des mots restants ; c'est grâce à elle qu'un mot arabe écrit avec ou sans hamza donne la même forme, ce que `main` vérifie au point 1.

**`normaliser_mot(mot)`** — Cette fonction applique le même nettoyage qu'un correcteur scrupuleux, mais à un seul mot, avant de le chercher dans le glossaire : elle reçoit un mot, lui applique la forme NFC, la table arabe et les minuscules, puis retire la ponctuation collée à ses bords, points d'interrogation, d'exclamation, points, virgules et deux-points. Elle renvoie le mot normalisé, si bien que « DLD », « off-plan » ou un mot arabe suivi d'un point d'interrogation retrouvent leur entrée dans `GLOSSAIRE` ; c'est la clé de lecture de `developper_glossaire`.

**`developper_glossaire(question)`** — Voici le traducteur maison qui réécrit une question sans aucun LLM, à la seule aide d'un lexique métier : la fonction reçoit une question, la découpe aux espaces, normalise chaque mot avec `normaliser_mot` et le remplace par sa forme développée s'il figure dans `GLOSSAIRE`, en laissant les autres mots tels quels, puis renvoie la phrase recomposée. Sur Q1, « رسوم DLD sur un off-plan » devient « frais département foncier dubaï sur un achat sur plan », ce qui suffit à faire passer le rappel de Q1 de 0,5 à 1 pour la stratégie par règles.

**`Moteur.__init__()`** — Le constructeur met en service un moteur de recherche muni d'un compteur de passages, comme un portillon qui enregistre chaque entrée : il ne reçoit aucun argument et se contente de créer l'attribut `recherches` à zéro, sans rien renvoyer. Ce compteur, lu avant et après chaque stratégie dans `main`, donne le nombre de recherches qu'elle a coûté, de 6 pour la recherche brute à 24 pour le multi-query sur les six questions.

**`Moteur.chercher(requete, k, filtre)`** — Cette méthode est le bibliothécaire lexical à qui chaque stratégie confie ses requêtes : elle reçoit une requête en texte, le nombre k de documents voulus et un filtre facultatif sur les métadonnées, ajoute 1 au compteur de recherches, découpe la requête, calcule le BM25 de chaque document avec les statistiques du corpus entier, écarte les documents que le filtre refuse, garde les scores strictement positifs, trie par score décroissant puis par identifiant, et renvoie les k premiers identifiants. Comme les statistiques ne dépendent jamais du filtre, un document filtré garde son score et l'ordre relatif des survivants est conservé.

**`Moteur.scores(requete)`** — Cette méthode ouvre le carnet de notes complet du bibliothécaire, sans rien trier ni couper : elle reçoit une requête, la découpe et renvoie un dictionnaire qui associe à chacun des 21 documents son score BM25, y compris les scores nuls, sans incrémenter le compteur de recherches. Le programme l'utilise au point 4 pour comparer les échelles : la question Q4 atteint un maximum de 20,40 et sa version step-back 4,04, et sur Q3 le texte HyDE produit un maximum plus de cinq fois supérieur à celui de la question.

**`FauxLLM.__init__(script)`** — Le constructeur prépare un comédien qui connaît par cœur toutes ses répliques, rangées par technique et par question : il reçoit le dictionnaire `SCRIPT`, qui associe à chaque couple (technique, question) la sortie JSON prévue, le garde tel quel et met à zéro le compteur `appels`, sans rien renvoyer. Ce compteur permet à `main` de mesurer combien d'appels au modèle chaque stratégie a coûtés : aucun pour la recherche brute et les règles, six pour toutes les autres.

**`FauxLLM.create(system, messages, tools)`** — Cette méthode imite la signature de l'adaptateur Claude, avec ses trois arguments nommés, mais se comporte comme un souffleur qui retrouve la bonne réplique dans son cahier : elle ajoute 1 au compteur d'appels, reconnaît la technique demandée en comparant la consigne système à celles de `CONSIGNES`, lit dans le script la sortie prévue pour cette technique et pour le dernier message de l'utilisateur, puis renvoie une `Reponse` « end_turn » dont l'unique bloc texte contient cette sortie sérialisée en JSON. Une consigne inconnue ou une question absente du script ferait échouer la recherche, ce qui signale aussitôt un scénario incomplet.

**`filtre_depuis(filtres)`** — Cette fonction est le greffier qui transforme les critères extraits par le modèle en une règle de tri applicable à chaque fiche : elle reçoit un dictionnaire de filtres, qui peut contenir un émirat ou une liste d'émirats, un type de document et une année minimale, et renvoie la fonction interne `garder`, qui dira pour chaque document s'il passe. Un dictionnaire vide laisse tout passer ; avec l'émirat Sharjah, le type « règlement » et l'année minimale 2025, elle réduit les 21 candidats à 2, exactement les deux documents pertinents de Q6.

**`garder(d)`** — Cette fonction interne, fabriquée par `filtre_depuis` et qui garde en mémoire ses filtres, est le contrôleur posté devant chaque fiche : elle reçoit un `Doc` et renvoie `False` si son émirat n'est pas celui demandé ou ne figure pas dans la liste demandée, si son type diffère du type demandé, ou si son année est antérieure à l'année minimale, et `True` dans tous les autres cas. C'est elle que `Moteur.chercher` consulte pour écarter les documents ; avec un émirat mal extrait ou une année trop stricte, il ne reste aucun document qui parle de location, et la recherche revient vide.

**`fusion(listes, k)`** — Elle réunit les résultats de plusieurs reformulations d'un même besoin, comme un comité qui retient les documents sur lesquels les avis convergent : la fonction reçoit une liste de classements et k, les fusionne avec `rrf` et renvoie les k premiers identifiants. Elle sert au multi-query et au step-back ; sur Q2, l'union des quatre listes couvre les trois pertinents parmi 8 documents, mais la fusion tronquée à 3 n'en garde que deux, soit un rappel de 0,67, ce qui montre qu'une fusion coupée à k peut perdre ce que l'union avait trouvé.

**`entrelacer(listes, k)`** — Cette fonction joue le maître d'hôtel qui sert à tour de rôle chaque table avant de revenir à la première, pour que personne ne reste sans assiette : elle reçoit une liste de classements, un par sous-question, prend le premier document de chaque liste, puis le deuxième de chaque liste, et ainsi de suite, en n'ajoutant un document que s'il n'est pas déjà servi, et renvoie les k premiers. Contrairement à `fusion`, qui récompense le consensus, elle garantit la couverture de sous-questions différentes, ce qui permet à la décomposition d'atteindre un rappel de 1 sur Q2 et sur Q5.

**`brute(llm, moteur, q)`** — C'est la stratégie témoin, celle du lecteur qui tape sa question telle qu'elle lui vient sans rien retoucher : la fonction reçoit le modèle, qu'elle n'utilise pas, le moteur et la question, et renvoie directement les k = 3 premiers documents de `Moteur.chercher` pour la question brute. Elle ne coûte aucun appel au LLM et une seule recherche par question, et fixe le repère bas du tableau, avec un rappel moyen de 0,3889 et un zéro sur Q3, dont le vocabulaire familier ne rencontre pas celui des documents.

**`regles(llm, moteur, q)`** — Cette stratégie est la réécriture la moins chère possible, faite à la main par un lexique : la fonction reçoit le modèle, qu'elle n'utilise pas, le moteur et la question, développe la question avec `developper_glossaire`, puis renvoie les trois premiers documents trouvés pour la version développée. Sans aucun appel au LLM, elle fait passer le rappel de Q1 de 0,5 à 1, puisque les acronymes et le mot arabe deviennent des mots présents dans les documents, mais elle ne change rien aux autres questions, et sa moyenne atteint 0,4722.

**`reecriture(llm, moteur, q)`** — Ici un rédacteur reformule la question dans la langue des documents avant de la transmettre au moteur : la fonction reçoit le modèle, le moteur et la question, demande à `demander` une réécriture au format JSON, développe encore le résultat avec le glossaire, puis renvoie les trois premiers documents trouvés. Elle coûte un appel au modèle et une recherche par question, et améliore Q3, dont le rappel passe de 0 à 0,5 une fois la question familière reformulée dans le vocabulaire des documents ; sa moyenne vaut 0,5556.

**`multi_query(llm, moteur, q)`** — Cette stratégie lance plusieurs filets à la fois, chacun tendu à un endroit différent du même besoin : la fonction reçoit le modèle, le moteur et la question, demande trois reformulations au modèle, cherche la question d'origine puis chacune des variantes, et fusionne les quatre listes par `fusion` avant de garder les trois premiers documents. Elle coûte un appel au modèle et quatre recherches par question, 24 en tout, et porte le rappel moyen à 0,8611, à égalité avec HyDE.

**`hyde(llm, moteur, q)`** — HyDE demande au modèle d'imaginer la page de documentation qui répondrait, puis cherche les vrais documents qui lui ressemblent, comme un enquêteur qui dresse un portrait-robot avant de feuilleter les fiches : la fonction reçoit le modèle, le moteur et la question, obtient de `demander` un court passage hypothétique, et renvoie les trois documents les plus proches de ce passage. Pour un appel et une recherche par question, elle atteint un rappel moyen de 0,8611, avec 1 sur Q1, Q3, Q4 et Q5, mais seulement 0,5 sur Q6.

**`step_back(llm, moteur, q)`** — Cette stratégie fait un pas en arrière, comme un juriste qui remonte de l'affaire particulière au principe général : la fonction reçoit le modèle, le moteur et la question, demande au modèle la question plus générale dont celle-ci est un cas particulier, cherche la question d'origine et la question générale, et fusionne les deux listes par `fusion`. Elle coûte un appel et deux recherches par question ; elle aide Q4, dont le rappel monte à 1, mais nuit à Q6, qui tombe à 0, si bien que sa moyenne ne dépasse pas 0,4722.

**`decomposition(llm, moteur, q)`** — Cette stratégie découpe une question composée en sous-questions indépendantes, comme un chef de projet qui répartit les tâches avant de rassembler les résultats : la fonction reçoit le modèle, le moteur et la question, demande au modèle la liste des sous-questions, lance une recherche pour chacune et entrelace les listes avec `entrelacer` pour garder trois documents. Elle coûte un appel et 13 recherches pour les six questions, puisque Q2 se découpe en trois, et atteint 1 sur Q1, Q2 et Q5, dont les deux dernières réunissent plusieurs besoins distincts ; sa moyenne vaut 0,75.

**`self_query(llm, moteur, q)`** — Ici le modèle joue le documentaliste qui sépare, dans la demande, ce qu'il faut chercher de ce qu'il faut filtrer : la fonction reçoit le modèle, le moteur et la question, obtient de `demander` un objet qui contient une requête nettoyée et un dictionnaire de filtres, puis renvoie les trois premiers documents trouvés pour cette requête avec le filtre construit par `filtre_depuis`. Pour un appel et une recherche par question, elle atteint 1 sur Q1, Q5 et Q6, où les filtres extraits font l'essentiel du travail, mais reste à 0 sur Q3, et sa moyenne vaut 0,6389.

**`latence_ms(appels_llm, recherches, t_llm_ms, t_recherche_ms)`** — Cette fonction est le chronométreur qui additionne les temps d'attente d'une stratégie, en supposant que tout se fait en série : elle reçoit le nombre d'appels au LLM, le nombre de recherches et leurs durées unitaires, 700 ms et 40 ms par défaut dans ce modèle illustratif, et renvoie appels × 700 + recherches × 40. Rapportée à une question, la recherche brute coûte 40 ms, le multi-query 860 ms, soit un appel au modèle et quatre recherches, et la décomposition environ 787 ms.

**`main()`** — Le chef d'orchestre déroule six démonstrations : la réécriture par règles de Q1 et l'unification des formes arabes, puis le tableau du rappel à 3 des huit stratégies sur six questions, avec leur coût en appels et en recherches et trois latences moyennes, le tout confronté aux dictionnaires `attendu` et `couts`. Il vérifie ensuite, question par question, que l'union des listes du multi-query domine chaque requête seule alors que la fusion tronquée peut perdre un pertinent, montre sur Q4 et Q3 que les échelles de BM25 rendent une somme de scores trompeuse, mesure l'effet d'un bon filtre puis de trois filtres faux sur la requête « location », et termine en exigeant que `demander` refuse par `ValueError` une sortie qui n'est pas un objet JSON. La dernière ligne n'annonce le succès que si chaque `assert` a tenu.

```python
"""Étape 30 ter — transformations de requête : réécriture, multi-query + RRF, HyDE, step-back, décomposition, self-query."""
import json
import math
import re
import sys
import unicodedata
from dataclasses import dataclass, field

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- port LLM (code canonique)
@dataclass
class Bloc:
    type: str
    text: str = ""
    id: str = ""
    name: str = ""
    input: dict = field(default_factory=dict)


@dataclass
class Reponse:
    stop_reason: str
    content: list


def texte(t: str) -> Bloc:
    return Bloc(type="text", text=t)


# ---------------------------------------------------------------- recherche (code canonique, étapes 22 et 24)
def idf_bm25(n_t: int, n_docs: int) -> float:
    return math.log(1 + (n_docs - n_t + 0.5) / (n_t + 0.5))


def bm25_score(requete: list[str], doc: list[str], corpus: list[list[str]], k1: float = 1.5, b: float = 0.75) -> float:
    n_docs = len(corpus)
    avgdl = sum(len(d) for d in corpus) / n_docs
    score = 0.0
    for t in requete:
        f = doc.count(t)
        if f == 0:
            continue
        n_t = sum(1 for d in corpus if t in d)
        score += idf_bm25(n_t, n_docs) * f * (k1 + 1) / (f + k1 * (1 - b + b * len(doc) / avgdl))
    return score


def rrf(classements: list[list[str]], k_rrf: int = 60) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for classement in classements:
        for rang, doc in enumerate(classement, start=1):
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (k_rrf + rang)
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))


def recall_at_k(retrouves: list[str], pertinents: set[str], k: int) -> float | None:
    if k < 1:
        raise ValueError("k doit valoir au moins 1")
    if not pertinents:
        return None
    return len(set(retrouves[:k]) & pertinents) / len(pertinents)


def precision_at_k(retrouves: list[str], pertinents: set[str], k: int) -> float:
    """Étape 26 : le dénominateur est toujours k, même si la liste est plus courte."""
    return len(set(retrouves[:k]) & pertinents) / k


# ---------------------------------------------------------------- normalisation (étape 22)
ALEF = "\N{ARABIC LETTER ALEF}"
TABLE_ARABE = str.maketrans({
    "\N{ARABIC LETTER ALEF WITH HAMZA ABOVE}": ALEF,
    "\N{ARABIC LETTER ALEF WITH HAMZA BELOW}": ALEF,
    "\N{ARABIC LETTER ALEF WITH MADDA ABOVE}": ALEF,
    "\N{ARABIC LETTER TEH MARBUTA}": "\N{ARABIC LETTER HEH}",
    "\N{ARABIC TATWEEL}": None,
    **{chr(c): None for c in range(0x064B, 0x0653)},
})
MOTS_VIDES = {"le", "la", "les", "l", "d", "de", "du", "des", "un", "une", "et", "ou", "pour", "au", "aux",
              "à", "a", "en", "par", "sur", "sa", "son", "ses", "ne", "que", "qui", "quel", "quelle", "quels",
              "quelles", "est", "il", "t", "s", "se", "ce", "dans", "mon", "ma", "me", "y", "peut", "comment"}
# Glossaire métier : acronymes, mots arabes fréquents, anglicismes. Une réécriture par règles, sans LLM.
GLOSSAIRE = {"dld": "département foncier dubaï", "rera": "régulation immobilière dubaï",
             "رسوم": "frais", "off-plan": "achat sur plan"}


def tokeniser(texte_: str) -> list[str]:
    t = unicodedata.normalize("NFC", texte_).translate(TABLE_ARABE).lower()
    return [m for m in re.findall(r"\w+", t) if m not in MOTS_VIDES]


def normaliser_mot(mot: str) -> str:
    return unicodedata.normalize("NFC", mot).translate(TABLE_ARABE).lower().strip("?!.,;:")


def developper_glossaire(question: str) -> str:
    """Chaque mot présent dans le glossaire (après normalisation) est remplacé par sa forme développée."""
    return " ".join(GLOSSAIRE.get(normaliser_mot(m), m) for m in question.split())


# ---------------------------------------------------------------- corpus (fictif) avec métadonnées
@dataclass
class Doc:
    ident: str
    emirat: str
    annee: int
    type: str
    texte: str


DOCS = [
    Doc("transfert-dubai", "Dubaï", 2024, "règlement",
        "Achat d'un bien à Dubaï : le département foncier perçoit des frais de transfert de 4 % de la valeur, payés à l'enregistrement de la vente."),
    Doc("commission-agent", "Dubaï", 2024, "fiche",
        "Commission de l'agent immobilier : un pourcentage du prix de vente fixé par le mandat, plus la TVA de 5 %."),
    Doc("hypotheque-enreg", "Dubaï", 2024, "fiche",
        "Enregistrement de l'hypothèque : frais proportionnels au montant du prêt, payés au département foncier à la signature."),
    Doc("charges-copro", "Dubaï", 2025, "fiche",
        "Charges de copropriété : montant annuel par sqft voté pour l'entretien de l'immeuble, payé par le propriétaire."),
    Doc("ejari-enreg", "Dubaï", 2024, "procédure",
        "Ejari : enregistrement du contrat de bail dans le système officiel de Dubaï ; frais d'enregistrement payés en ligne."),
    Doc("ejari-renouv", "Dubaï", 2025, "procédure",
        "Renouvellement du bail : enregistrer le nouveau contrat dans Ejari avant l'échéance ; frais à la charge du locataire."),
    Doc("ejari-annul", "Dubaï", 2024, "procédure",
        "Résiliation du bail : annuler l'enregistrement Ejari après la remise des clés et le solde des factures."),
    Doc("hausse-loyer", "Dubaï", 2025, "règlement",
        "Hausse de loyer : au renouvellement, le bailleur ne peut augmenter le loyer que dans la limite fixée par l'indice officiel des loyers."),
    Doc("preavis-loyer", "Dubaï", 2024, "règlement",
        "Préavis : toute modification des conditions du bail, y compris le montant du loyer, est notifiée par écrit avant l'échéance."),
    Doc("annonce-marina", "Dubaï", 2025, "annonce",
        "Studio à Dubai Marina : loyer annuel de 60 000 AED, vue mer, libre au renouvellement du locataire actuel."),
    Doc("bail-abudhabi", "Abu Dhabi", 2024, "procédure",
        "Abu Dhabi : enregistrement du contrat de bail dans le système officiel de l'émirat ; frais selon le barème municipal."),
    Doc("achat-abudhabi", "Abu Dhabi", 2024, "règlement",
        "Achat d'un bien à Abu Dhabi : frais d'enregistrement de la vente selon le barème de l'émirat."),
    Doc("offplan-abudhabi", "Abu Dhabi", 2025, "fiche",
        "Achat sur plan à Abu Dhabi : frais de dossier et échéancier du promoteur."),
    Doc("hypotheque-abudhabi", "Abu Dhabi", 2024, "fiche",
        "Abu Dhabi : frais d'enregistrement d'une hypothèque sur un bien résidentiel."),
    Doc("charges-abudhabi", "Abu Dhabi", 2025, "fiche",
        "Abu Dhabi : frais de service annuels des immeubles résidentiels, votés par les propriétaires."),
    Doc("location-sharjah-2023", "Sharjah", 2023, "règlement",
        "Location à Sharjah : bail certifié par la municipalité."),
    Doc("location-sharjah-2025", "Sharjah", 2025, "règlement",
        "Location à Sharjah : nouvelles règles de certification des baux résidentiels et commerciaux par la municipalité, "
        "avec dépôt en ligne du contrat signé par les deux parties."),
    Doc("depot-sharjah-2025", "Sharjah", 2025, "règlement",
        "Location à Sharjah : conditions de restitution du dépôt de garantie des baux résidentiels, à la fin du contrat, "
        "après l'état des lieux de sortie."),
    Doc("faq-sharjah", "Sharjah", 2024, "FAQ",
        "FAQ location à Sharjah : payer son loyer en plusieurs chèques."),
    Doc("guide-location-dubai", "Dubaï", 2025, "fiche",
        "Guide de la location à Dubaï : location résidentielle, location meublée, dépôt de garantie et règles de la location."),
    Doc("offplan-dubai", "Dubaï", 2025, "fiche",
        "Achat sur plan à Dubaï : échéancier de paiement du promoteur et enregistrement provisoire de la vente au département foncier."),
]
PAR_ID = {d.ident: d for d in DOCS}
TOKENS = [tokeniser(d.texte) for d in DOCS]


class Moteur:
    """BM25 sur tout le corpus ; les statistiques (IDF, longueur moyenne) ne dépendent jamais du filtre."""

    def __init__(self):
        self.recherches = 0

    def chercher(self, requete: str, k: int, filtre=None) -> list[str]:
        self.recherches += 1
        tq = tokeniser(requete)
        scores = [(d.ident, bm25_score(tq, t, TOKENS)) for d, t in zip(DOCS, TOKENS)
                  if filtre is None or filtre(d)]
        return [i for i, s in sorted(scores, key=lambda kv: (-kv[1], kv[0])) if s > 0][:k]

    def scores(self, requete: str) -> dict[str, float]:
        tq = tokeniser(requete)
        return {d.ident: bm25_score(tq, t, TOKENS) for d, t in zip(DOCS, TOKENS)}


# ---------------------------------------------------------------- faux LLM et consignes
CONSIGNES = {
    "reecriture": "Réécris la question en français, avec le vocabulaire des documents. JSON : {\"requete\": …}",
    "multi": "Propose trois reformulations différentes de la question. JSON : {\"variantes\": […]}",
    "hyde": "Écris le court passage de documentation qui répondrait à la question. JSON : {\"document\": …}",
    "step_back": "Pose la question plus générale dont celle-ci est un cas particulier. JSON : {\"question\": …}",
    "decomposition": "Découpe la question en sous-questions indépendantes. JSON : {\"sous_questions\": […]}",
    "self_query": "Sépare le texte à chercher et les filtres (emirat, type, annee_min). JSON : {\"requete\": …, \"filtres\": {…}}",
}

Q1 = "رسوم DLD sur un off-plan"
Q2 = "Combien coûte l'achat d'un appartement à Dubaï ?"
Q3 = "Mon proprio peut-il me faire payer plus cher l'an prochain ?"
Q4 = "Mon studio à Dubai Marina à 60 000 AED peut-il passer à 70 000 AED au renouvellement ?"
Q5 = "Comparer les frais d'achat d'un bien à Dubaï et à Abu Dhabi"
Q6 = "Règlements de 2025 sur la location à Sharjah"

QUESTIONS = [  # (identifiant, question, documents pertinents)
    ("Q1", Q1, {"transfert-dubai", "offplan-dubai"}),
    ("Q2", Q2, {"transfert-dubai", "commission-agent", "hypotheque-enreg"}),
    ("Q3", Q3, {"hausse-loyer", "preavis-loyer"}),
    ("Q4", Q4, {"hausse-loyer", "preavis-loyer"}),
    ("Q5", Q5, {"transfert-dubai", "achat-abudhabi"}),
    ("Q6", Q6, {"location-sharjah-2025", "depot-sharjah-2025"}),
]

SCRIPT = {  # (technique, question) -> sortie JSON du faux LLM ; déterministe et gratuite
    ("reecriture", Q1): {"requete": "frais DLD achat sur plan"},
    ("reecriture", Q2): {"requete": "coût achat appartement Dubaï"},
    ("reecriture", Q3): {"requete": "le propriétaire peut-il augmenter le prix l'an prochain"},
    ("reecriture", Q4): {"requete": "studio Dubai Marina loyer 60 000 AED passer à 70 000 AED renouvellement"},
    ("reecriture", Q5): {"requete": "comparer frais achat bien Dubaï Abu Dhabi"},
    ("reecriture", Q6): {"requete": "règlements 2025 location Sharjah"},
    ("multi", Q1): {"variantes": ["frais de transfert département foncier achat sur plan", "achat sur plan Dubaï frais",
                                  "département foncier frais vente"]},
    ("multi", Q2): {"variantes": ["frais de transfert Dubaï", "commission agent immobilier",
                                  "frais hypothèque prêt"]},
    ("multi", Q3): {"variantes": ["hausse de loyer propriétaire", "augmenter le loyer renouvellement",
                                  "préavis modification du loyer"]},
    ("multi", Q4): {"variantes": ["hausse loyer renouvellement studio", "limite augmentation loyer indice",
                                  "préavis montant du loyer"]},
    ("multi", Q5): {"variantes": ["frais de transfert achat Dubaï", "frais enregistrement vente Abu Dhabi",
                                  "coût d'achat immobilier par émirat"]},
    ("multi", Q6): {"variantes": ["location Sharjah règles 2025", "baux résidentiels Sharjah",
                                  "certification bail municipalité Sharjah"]},
    ("hyde", Q1): {"document": "À Dubaï, le département foncier perçoit des frais de transfert sur tout achat, "
                               "y compris un achat sur plan, payés à l'enregistrement."},
    ("hyde", Q2): {"document": "L'achat d'un appartement à Dubaï entraîne des frais de transfert au département foncier, "
                               "la commission de l'agent et, avec un prêt, l'enregistrement de l'hypothèque."},
    ("hyde", Q3): {"document": "Le bailleur peut augmenter le loyer au renouvellement du bail, dans la limite de "
                               "l'indice des loyers, après un préavis écrit."},
    ("hyde", Q4): {"document": "Au renouvellement, une hausse de loyer est limitée par l'indice officiel des loyers "
                               "et doit être notifiée par écrit."},
    ("hyde", Q5): {"document": "À Dubaï, l'acheteur paie des frais de transfert au département foncier ; à Abu Dhabi, "
                               "des frais d'enregistrement de la vente selon le barème de l'émirat."},
    ("hyde", Q6): {"document": "À Sharjah, la location d'un logement passe par un bail certifié par la municipalité "
                               "et un loyer payé en plusieurs chèques."},
    ("step_back", Q1): {"question": "Quels frais paie un acheteur de bien à Dubaï ?"},
    ("step_back", Q2): {"question": "Quels frais accompagnent un achat immobilier ?"},
    ("step_back", Q3): {"question": "Quelles règles encadrent la hausse d'un loyer ?"},
    ("step_back", Q4): {"question": "Quel préavis et quelles règles pour modifier un loyer ?"},
    ("step_back", Q5): {"question": "Quels frais paie un acheteur immobilier aux Émirats ?"},
    ("step_back", Q6): {"question": "Quelles règles s'appliquent à la location résidentielle ?"},
    ("decomposition", Q1): {"sous_questions": ["frais du département foncier sur un achat", "achat sur plan à Dubaï"]},
    ("decomposition", Q2): {"sous_questions": ["frais de transfert d'un achat à Dubaï", "commission de l'agent immobilier",
                                               "frais d'enregistrement de l'hypothèque au département foncier"]},
    ("decomposition", Q3): {"sous_questions": ["le propriétaire peut-il augmenter le loyer", "délai pour annoncer une hausse"]},
    ("decomposition", Q4): {"sous_questions": ["loyer d'un studio à Dubai Marina", "limite de hausse de loyer au renouvellement"]},
    ("decomposition", Q5): {"sous_questions": ["frais d'achat d'un bien à Dubaï", "frais d'achat d'un bien à Abu Dhabi"]},
    ("decomposition", Q6): {"sous_questions": ["règles de location à Sharjah", "règlements publiés en 2025"]},
    ("self_query", Q1): {"requete": "frais achat sur plan", "filtres": {"emirat": "Dubaï"}},
    ("self_query", Q2): {"requete": "coût achat appartement", "filtres": {"emirat": "Dubaï"}},
    ("self_query", Q3): {"requete": "payer plus cher l'an prochain", "filtres": {}},
    ("self_query", Q4): {"requete": "studio passer à 70 000 AED au renouvellement", "filtres": {"emirat": "Dubaï"}},
    ("self_query", Q5): {"requete": "frais d'achat d'un bien", "filtres": {"emirat": ["Dubaï", "Abu Dhabi"]}},
    ("self_query", Q6): {"requete": "location", "filtres": {"emirat": "Sharjah", "type": "règlement", "annee_min": 2025}},
}


class FauxLLM:
    """Même interface que l'adaptateur Claude : create(system=…, messages=…, tools=…) renvoie une Reponse."""

    def __init__(self, script: dict):
        self.script = script
        self.appels = 0

    def create(self, *, system: str, messages: list, tools: list) -> Reponse:
        self.appels += 1
        technique = next(t for t, c in CONSIGNES.items() if c == system)
        sortie = self.script[(technique, messages[-1]["content"])]
        return Reponse("end_turn", [texte(json.dumps(sortie, ensure_ascii=False))])


def demander(llm, technique: str, question: str) -> dict:
    """Un appel au LLM ; la réponse doit être un objet JSON, sinon ValueError (pas de repli silencieux)."""
    reponse = llm.create(system=CONSIGNES[technique], messages=[{"role": "user", "content": question}], tools=[])
    if reponse.stop_reason != "end_turn":
        raise ValueError(f"réponse inattendue : {reponse.stop_reason}")
    objet = json.loads("".join(b.text for b in reponse.content if b.type == "text"))
    if not isinstance(objet, dict):
        raise ValueError("le LLM devait renvoyer un objet JSON")
    return objet


# ---------------------------------------------------------------- stratégies
K = 3                         # documents gardés, et profondeur de chaque liste avant la fusion


def filtre_depuis(filtres: dict):
    """Traduit les filtres extraits en prédicat sur les métadonnées ; un filtre vide laisse tout passer."""
    def garder(d: Doc) -> bool:
        emirat = filtres.get("emirat")
        if emirat is not None and d.emirat not in (emirat if isinstance(emirat, list) else [emirat]):
            return False
        if "type" in filtres and d.type != filtres["type"]:
            return False
        if "annee_min" in filtres and d.annee < filtres["annee_min"]:
            return False
        return True
    return garder


def fusion(listes: list[list[str]], k: int) -> list[str]:
    """Consensus : RRF (étape 24). Pour des reformulations d'un MÊME besoin."""
    return [d for d, _ in rrf(listes)][:k]


def entrelacer(listes: list[list[str]], k: int) -> list[str]:
    """Couverture : le 1er de chaque liste, puis le 2e de chaque liste… Pour des sous-questions DIFFÉRENTES."""
    sortie: list[str] = []
    for rang in range(max((len(l) for l in listes), default=0)):
        for liste in listes:
            if rang < len(liste) and liste[rang] not in sortie:
                sortie.append(liste[rang])
    return sortie[:k]


def brute(llm, moteur: Moteur, q: str) -> list[str]:
    return moteur.chercher(q, K)


def regles(llm, moteur: Moteur, q: str) -> list[str]:
    return moteur.chercher(developper_glossaire(q), K)


def reecriture(llm, moteur: Moteur, q: str) -> list[str]:
    requete = developper_glossaire(demander(llm, "reecriture", q)["requete"])
    return moteur.chercher(requete, K)


def multi_query(llm, moteur: Moteur, q: str) -> list[str]:
    variantes = demander(llm, "multi", q)["variantes"]
    return fusion([moteur.chercher(q, K)] + [moteur.chercher(v, K) for v in variantes], K)


def hyde(llm, moteur: Moteur, q: str) -> list[str]:
    return moteur.chercher(demander(llm, "hyde", q)["document"], K)


def step_back(llm, moteur: Moteur, q: str) -> list[str]:
    generale = demander(llm, "step_back", q)["question"]
    return fusion([moteur.chercher(q, K), moteur.chercher(generale, K)], K)


def decomposition(llm, moteur: Moteur, q: str) -> list[str]:
    sous = demander(llm, "decomposition", q)["sous_questions"]
    return entrelacer([moteur.chercher(s, K) for s in sous], K)


def self_query(llm, moteur: Moteur, q: str) -> list[str]:
    objet = demander(llm, "self_query", q)
    return moteur.chercher(objet["requete"], K, filtre_depuis(objet["filtres"]))


STRATEGIES = {"brute": brute, "règles": regles, "réécriture": reecriture, "multi-query": multi_query, "HyDE": hyde,
              "step-back": step_back, "décomposition": decomposition, "self-query": self_query}


def latence_ms(appels_llm: int, recherches: int, t_llm_ms: float = 700.0, t_recherche_ms: float = 40.0) -> float:
    """Modèle illustratif : appels LLM puis recherches, en série."""
    return appels_llm * t_llm_ms + recherches * t_recherche_ms


def main() -> None:
    print("1. Réécriture par règles, sans LLM : glossaire et normalisation de l'arabe")
    regle = developper_glossaire(Q1)
    print(f"  {Q1} → {regle}")
    assert regle == "frais département foncier dubaï sur un achat sur plan"
    hamza, sans_hamza = "\N{ARABIC LETTER ALEF WITH HAMZA ABOVE}" + "جرة", ALEF + "جرة"
    assert normaliser_mot(hamza) == normaliser_mot(sans_hamza) and tokeniser(hamza) == tokeniser(sans_hamza)

    print("2. Recall@3 par stratégie, sur 6 questions (Q1 … Q6), et coût")
    llm, moteur = FauxLLM(SCRIPT), Moteur()
    table, couts = {}, {}
    for nom, strategie in STRATEGIES.items():
        a0, r0 = llm.appels, moteur.recherches
        table[nom] = [recall_at_k(strategie(llm, moteur, q), rel, K) for _, q, rel in QUESTIONS]
        couts[nom] = (llm.appels - a0, moteur.recherches - r0)
        moyenne = sum(table[nom]) / len(table[nom])
        print(f"  {nom:<14} " + " ".join(f"{r:.2f}" for r in table[nom])
              + f"   moyenne {moyenne:.4f}   LLM {couts[nom][0]}  recherches {couts[nom][1]:>2}")
    attendu = {"brute": [0.5, 1 / 3, 0.0, 0.5, 0.5, 0.5], "règles": [1.0, 1 / 3, 0.0, 0.5, 0.5, 0.5],
               "réécriture": [1.0, 1 / 3, 0.5, 0.5, 0.5, 0.5], "multi-query": [1.0, 2 / 3, 1.0, 1.0, 0.5, 1.0],
               "HyDE": [1.0, 2 / 3, 1.0, 1.0, 1.0, 0.5], "step-back": [0.5, 1 / 3, 0.5, 1.0, 0.5, 0.0],
               "décomposition": [1.0, 1.0, 0.5, 0.5, 1.0, 0.5], "self-query": [1.0, 1 / 3, 0.0, 0.5, 1.0, 1.0]}
    assert table == attendu
    assert couts == {"brute": (0, 6), "règles": (0, 6), "réécriture": (6, 6), "multi-query": (6, 24), "HyDE": (6, 6),
                     "step-back": (6, 12), "décomposition": (6, 13), "self-query": (6, 6)}
    for nom in ("brute", "multi-query", "décomposition"):
        a, r = couts[nom]
        print(f"  latence par question ({nom}) : {latence_ms(a, r) / 6:.0f} ms")

    print("3. Multi-query : l'union domine chaque requête seule ; la fusion tronquée à k, non")
    for qid, q, rel in QUESTIONS:
        requetes = [q] + demander(llm, "multi", q)["variantes"]
        listes = [moteur.chercher(r, K) for r in requetes]
        seules = [recall_at_k(liste, rel, K) for liste in listes]
        union = set().union(*listes)
        r_union = len(union & rel) / len(rel)
        r_fusion = recall_at_k(fusion(listes, K), rel, K)
        assert r_union >= max(seules) and r_fusion <= r_union and len(union) <= len(listes) * K
        if qid == "Q2":
            print(f"  Q2 : requêtes seules {[round(r, 2) for r in seules]} ; union {r_union:.2f} sur {len(union)} documents ;"
                  f" RRF top-3 {r_fusion:.2f}")
            scores = dict(rrf(listes))
            print(f"  RRF : transfert-dubai {scores['transfert-dubai']:.4f} (2 listes)  offplan-abudhabi "
                  f"{scores['offplan-abudhabi']:.4f} (2 listes)  hypotheque-enreg {scores['hypotheque-enreg']:.4f} (1 liste)")
            assert (round(r_union, 2), len(union), round(r_fusion, 4)) == (1.0, 8, 0.6667)

    print("4. Pourquoi RRF : les échelles de score des requêtes ne se comparent pas")
    so, ss = moteur.scores(Q4), moteur.scores(SCRIPT[("step_back", Q4)]["question"])
    par_somme = min(PAR_ID, key=lambda d: (-(so[d] + ss[d]), d))
    par_rrf = step_back(llm, moteur, Q4)[0]
    print(f"  Q4 : BM25 max {max(so.values()):.2f} pour la question, {max(ss.values()):.2f} pour le step-back ;"
          f" 1er par somme : {par_somme} ; 1er par RRF : {par_rrf}")
    assert par_somme == "annonce-marina" and par_rrf == "hausse-loyer"
    sh, sq3 = max(moteur.scores(SCRIPT[("hyde", Q3)]["document"]).values()), max(moteur.scores(Q3).values())
    print(f"  Q3 : BM25 max {sq3:.2f} pour la question, {sh:.2f} pour le texte HyDE : un seuil commun n'a pas de sens")
    assert sh > 5 * sq3

    print("5. Filtres de métadonnées : moins de candidats, plus de précision, un risque pour le rappel")
    rel6 = QUESTIONS[5][2]
    bon = filtre_depuis({"emirat": "Sharjah", "type": "règlement", "annee_min": 2025})
    sans, avec = moteur.chercher("location", 100), moteur.chercher("location", 100, bon)
    assert avec == [d for d in sans if bon(PAR_ID[d])]                       # l'ordre relatif est conservé
    assert all(len(set(avec[:k]) & rel6) >= len(set(sans[:k]) & rel6) for k in range(1, 11))
    print(f"  « location » : {len(DOCS)} candidats → {sum(bon(d) for d in DOCS)} ; P@3 {precision_at_k(sans, rel6, 3):.2f} → "
          f"{precision_at_k(avec, rel6, 3):.2f} ; R@3 {recall_at_k(sans, rel6, 3):.2f} → {recall_at_k(avec, rel6, 3):.2f}")
    assert (precision_at_k(avec, rel6, 3), recall_at_k(avec, rel6, 3)) == (2 / 3, 1.0)
    faux = moteur.chercher("location", 3, filtre_depuis({"emirat": "Dubaï", "type": "règlement", "annee_min": 2025}))
    strict = moteur.chercher("location", 3, filtre_depuis({"emirat": "Sharjah", "type": "règlement", "annee_min": 2026}))
    q5 = moteur.chercher("frais d'achat d'un bien", 3, filtre_depuis({"emirat": "Dubaï"}))
    print(f"  émirat mal extrait : R@3 {recall_at_k(faux, rel6, 3):.2f} ; année trop stricte : {strict} ;"
          f" Q5 filtrée sur Dubaï seul : R@3 {recall_at_k(q5, QUESTIONS[4][2], 3):.2f}")
    assert faux == [] and strict == [] and recall_at_k(q5, QUESTIONS[4][2], 3) == 0.5

    print("6. Une sortie de LLM qui n'est pas un objet JSON est refusée")
    try:
        demander(FauxLLM({("hyde", "q"): ["pas", "un", "objet"]}), "hyde", "q")
    except ValueError as e:
        print(f"  ValueError : {e}")
    else:
        raise AssertionError("une sortie invalide aurait dû être refusée")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Réécriture par règles, sans LLM : glossaire et normalisation de l'arabe
  رسوم DLD sur un off-plan → frais département foncier dubaï sur un achat sur plan
2. Recall@3 par stratégie, sur 6 questions (Q1 … Q6), et coût
  brute          0.50 0.33 0.00 0.50 0.50 0.50   moyenne 0.3889   LLM 0  recherches  6
  règles         1.00 0.33 0.00 0.50 0.50 0.50   moyenne 0.4722   LLM 0  recherches  6
  réécriture     1.00 0.33 0.50 0.50 0.50 0.50   moyenne 0.5556   LLM 6  recherches  6
  multi-query    1.00 0.67 1.00 1.00 0.50 1.00   moyenne 0.8611   LLM 6  recherches 24
  HyDE           1.00 0.67 1.00 1.00 1.00 0.50   moyenne 0.8611   LLM 6  recherches  6
  step-back      0.50 0.33 0.50 1.00 0.50 0.00   moyenne 0.4722   LLM 6  recherches 12
  décomposition  1.00 1.00 0.50 0.50 1.00 0.50   moyenne 0.7500   LLM 6  recherches 13
  self-query     1.00 0.33 0.00 0.50 1.00 1.00   moyenne 0.6389   LLM 6  recherches  6
3. Multi-query : l'union domine chaque requête seule ; la fusion tronquée à k, non
  Q2 : requêtes seules [0.33, 0.33, 0.33, 0.33] ; union 1.00 sur 8 documents ; RRF top-3 0.67
  Q4 : BM25 max 20.40 pour la question, 4.04 pour le step-back ; 1er par somme : annonce-marina ; 1er par RRF : hausse-loyer
5. Filtres de métadonnées : moins de candidats, plus de précision, un risque pour le rappel
  « location » : 21 candidats → 2 ; P@3 0.00 → 0.67 ; R@3 0.00 → 1.00
  émirat mal extrait : R@3 0.00 ; année trop stricte : [] ; Q5 filtrée sur Dubaï seul : R@3 0.50
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : aucune transformation n'est la meilleure partout. Chacune règle un défaut précis de la question, se paie en appels et en recherches, et se juge par le rappel qu'elle apporte sur un jeu annoté.

### Brancher un vrai modèle sans toucher aux stratégies

Les stratégies n'appellent le modèle qu'à travers `demander`, qui ne connaît que le port `create(system=…, messages=…, tools=…)`. L'adaptateur Claude du parcours se branche donc à la place du faux LLM ; une réécriture est une tâche courte, pour laquelle un effort de réflexion faible suffit et réduit la latence.

```python
# [extrait] — même code avec un vrai modèle : seul l'adaptateur change (adaptateur Claude du parcours)
llm = ClaudeLLM(effort="low")
moteur = Moteur()
documents = multi_query(llm, moteur, "Combien coûte l'achat d'un appartement à Dubaï ?")
# demander() lève ValueError si la sortie n'est pas un objet JSON : on journalise et on retombe sur brute()
```

Pour se passer de tout fournisseur, on garde la même architecture : un glossaire et des règles de normalisation couvrent déjà une partie des réécritures (point 1), un modèle ouvert hébergé en interne peut tenir le rôle du LLM derrière le même port, et le jeu d'évaluation de ce fichier dit si le remplacement dégrade le rappel.

## Squelette algorithmique

L'algorithme reçoit une question, un moteur de recherche et un LLM ; il renvoie au plus k documents. Un routeur choisit la transformation, puis la branche correspondante produit une ou plusieurs requêtes et les fusionne selon leur nature : RRF pour des reformulations, entrelacement pour des sous-questions.

```text
ALGORITHME TransformerPuisChercher
ENTRÉES : question q, moteur M, LLM, glossaire G, k
SORTIE  : liste de k documents au plus

  q ← remplacer dans q chaque mot de G par sa forme développée    (règles, sans LLM)
  t ← Router(q)                    (vague, comparaison, contrainte de métadonnée, cas particulier…)
  SI t = brute ALORS RETOURNER M.chercher(q, k)
  SI t = multi-query ALORS
      variantes ← LLM(« reformuler », q)
      RETOURNER RRF([M.chercher(q, k)] + [M.chercher(v, k) POUR v DANS variantes]), coupé à k
  SI t = HyDE ALORS RETOURNER M.chercher(LLM(« document hypothétique », q), k)
  SI t = step-back ALORS
      g ← LLM(« question générale », q)
      RETOURNER RRF([M.chercher(q, k), M.chercher(g, k)]), coupé à k
  SI t = décomposition ALORS
      listes ← [M.chercher(s, k) POUR s DANS LLM(« sous-questions », q)]
      RETOURNER Entrelacer(listes, k)
  SI t = self-query ALORS
      (q′, filtres) ← LLM(« texte et filtres », q)
      SI une valeur de filtres n'appartient pas à la liste autorisée ALORS filtres ← vide
      L ← M.chercher(q′, k, filtres)
      SI L est vide ALORS L ← M.chercher(q′, k)          (repli sans filtre, journalisé)
      RETOURNER L

ALGORITHME Entrelacer(listes, k)
  sortie ← liste vide
  POUR rang DE 1 À longueur de la plus longue liste FAIRE
      POUR CHAQUE liste DANS listes FAIRE
          SI liste[rang] existe ET liste[rang] ∉ sortie ALORS ajouter liste[rang] à sortie
      FIN POUR
  FIN POUR
  RETOURNER les k premiers de sortie
```

**Complexité.** Une recherche BM25 naïve coûte O(|𝒟| · |q|) ; une transformation qui lance r recherches coûte r fois plus en calcul, mais seulement le temps d'une recherche si elles partent en parallèle. Le coût dominant est l'appel au LLM, au plus un par question ici, dont la durée croît avec le nombre de tokens produits : HyDE, qui écrit un paragraphe, coûte plus de tokens de sortie qu'une réécriture d'une ligne. La fusion RRF de r listes de k documents coûte O(rk log(rk)) pour le tri, l'entrelacement O(rk) comparaisons d'appartenance avec un ensemble auxiliaire, O(r k²) avec la liste naïve du code, négligeable pour de petits k. La mémoire est O(rk).

**Du squelette au code.** La première ligne est `developper_glossaire`. Le routeur n'est pas codé : le programme applique toutes les branches pour les comparer, ce que fait la boucle sur `STRATEGIES`. Les branches sont `brute`, `multi_query`, `hyde`, `step_back`, `decomposition` et `self_query` ; les appels au LLM passent par `demander`, la fusion par `fusion` (RRF) ou `entrelacer`, et les filtres par `filtre_depuis`. La validation des valeurs de filtres et le repli sans filtre sont décrits au point 7 ; ils s'ajoutent à `self_query` en production.

## Cas d'usage réels aux Émirats

Les volumes, gains et durées ci-dessous sont illustratifs ; seuls les chiffres réglementaires reprennent la liste vérifiée du parcours.

### Immobilier — des acheteurs qui parlent trois langues dans la même phrase

Une agence qui opère à Dubaï et à Abu Dhabi reçoit chaque jour plusieurs centaines de questions d'acheteurs sur son assistant, souvent écrites comme Q1 : un mot arabe, un acronyme, un terme anglais. Son corpus de fiches est rédigé en français et en anglais, avec le vocabulaire du métier. L'équipe commence par un glossaire d'une centaine d'entrées (DLD, RERA, Ejari, off-plan, ready, service charges, et les mots arabes les plus fréquents comme رسوم ou إيجار), appliqué après la normalisation de l'arabe de l'étape 22 : sur son jeu annoté, le Recall@5 des questions mélangées passe de 0,58 à 0,81 sans aucun appel à un LLM, comme Q1 passe de 0,5 à 1. Les comparaisons entre émirats (« frais d'achat à Dubaï et à Abu Dhabi ») sont routées vers la décomposition, parce que les mots rares d'un émirat écrasent ceux de l'autre, exactement comme dans Q5. L'agent affiche les frais de transfert de 4 % de la valeur pour Dubaï et cite la fiche d'Abu Dhabi pour l'autre émirat, sans inventer de taux. Sans ces transformations, l'agent répond sur un seul émirat et l'acheteur compare des coûts incomplets. On suit le Recall@5 par type de question et la part des questions routées vers chaque technique.

### Secteur public — un glossaire avant tout modèle, et des journaux sans texte libre

Une entité de services publics en ligne, accessible par UAE Pass, reçoit des questions en arabe, en anglais et souvent dans un mélange des deux, sur ses démarches. L'équipe applique la même normalisation à l'index et aux questions, puis un glossaire qui relie les noms usuels des démarches à leurs intitulés officiels dans les deux langues. Les questions qui restent sans résultat suffisant sont envoyées vers une réécriture par un modèle multilingue hébergé dans l'environnement de l'entité, derrière le même port que le faux LLM de ce fichier. Le routage limite le surcoût : seules 15 % des questions passent par le modèle, ce qui garde la latence médiane proche de celle de la recherche brute, alors qu'une réécriture systématique ajouterait environ 700 ms à chaque question dans le modèle du point 9. Pour respecter la PDPL, les journaux gardent la technique choisie, les identifiants des pages renvoyées et le rappel mesuré, mais pas le texte libre saisi par l'usager. On suit le Recall@3 par langue et le taux de questions sans résultat.

### Banque — remonter de la question du client à la règle

Une banque de détail de Dubaï voit ses conseillers poser des questions très particulières : « mon client retraité rembourse déjà 9 000 AED par mois sur un revenu de 25 000 AED, puis-je lui proposer un prêt personnel ? ». La recherche brute ramène des fiches produit qui partagent les montants et les mots « prêt personnel », comme l'annonce du studio dans Q4. Le step-back pose la question générale (« quelles règles d'endettement pour un client retraité ? ») et fusionne les deux listes par RRF : la règle de la CBUAE selon laquelle le total des mensualités, nouvelle mensualité comprise, ne dépasse pas 30 % du revenu pour un retraité (50 % dans le cas général) remonte en tête. L'agent calcule alors 9 000 / 25 000 = 36 %, au-dessus de 30 % avant même la nouvelle mensualité, et conclut que le dossier n'est pas recevable. Le glossaire développe aussi les acronymes internes, comme DBR pour le ratio d'endettement, avant toute recherche. Sans le step-back, l'agent aurait comparé des fiches produit sans jamais lire la règle. On suit la part des réponses d'éligibilité qui citent la règle applicable.

### RH — un filtre de régime, validé avant d'être appliqué

Un cabinet RH présent dans plusieurs émirats indexe ses règles avec des métadonnées : régime (secteur privé fédéral, DIFC, ressortissants émiriens relevant de la GPSSA), émirat, date d'effet. Le self-query extrait le régime de la question ou du dossier du salarié : pour « indemnité de fin de service d'une salariée du DIFC », le filtre écarte les règles fédérales du décret-loi 33/2021, qui ne s'appliquent pas à elle, et la précision du contexte monte comme celle de Q6. Le point 7 dicte les garde-fous : la valeur extraite doit appartenir à la liste fermée des régimes, sinon le filtre est ignoré ; une liste vide déclenche une recherche sans filtre, signalée au conseiller. L'équipe a constaté que le modèle confondait parfois « Dubai » et « DIFC » dans des questions mal écrites ; le contrôle croisé avec le dossier du salarié, qui porte le régime réel, a supprimé ces erreurs. Un filtre faux aurait fait répondre l'agent avec la règle d'un autre régime, sans aucun signal. Toute réponse reste à confirmer avec le texte en vigueur. On suit le rappel par régime et le taux de replis sans filtre.

### Crypto — la date d'effet comme filtre, pas comme mot

Une plateforme d'actifs virtuels agréée par la VARA conserve toutes les versions de ses procédures internes, chacune avec sa date d'effet et sa version en métadonnée. Une question comme « limites de retrait en vigueur depuis la mise à jour de mars » échoue en recherche brute, parce que la date n'est pas écrite dans le texte des sections, comme l'année 2025 dans Q6. Le self-query traduit « en vigueur » en filtre sur la version courante et « depuis mars » en date d'effet minimale ; HyDE n'aide pas ici, puisque l'hypothèse écrite par le modèle ignore les versions internes, ce que Q6 montre aussi. Une plateforme agréée doit communiquer des conditions à jour, et une limite d'une version remplacée annoncée à un client est un incident de conformité. L'équipe vérifie chaque semaine que le filtre « version courante » renvoie exactement une version par procédure, et alerte sinon. On suit la part des réponses qui citent une version remplacée, avec un objectif de zéro.

### Assurance — HyDE pour passer du langage de l'assuré à celui du contrat

Un assureur auto et santé reçoit des déclarations écrites comme on parle : « j'ai tapé un poteau en reculant, ma caméra ne marche plus ». Les clauses du contrat, elles, parlent de « dommages par collision avec un objet fixe » et d'« équipements électroniques du véhicule » : la recherche brute ne trouve presque rien, comme Q3. HyDE fait écrire par le modèle le passage de contrat qui répondrait, puis cherche avec ce texte, dont le vocabulaire est celui des clauses ; le multi-query, avec trois reformulations, donne un résultat proche pour un coût de recherche quatre fois plus élevé. Le passage hypothétique n'est jamais montré à l'assuré ni au gestionnaire : il peut contenir une franchise ou une garantie inventée, et seule la clause réelle retrouvée sert à décider. L'assurance est supervisée par la CBUAE, et une décision doit citer la clause applicable, d'où cette séparation stricte entre texte de recherche et source. On suit le Recall@5 des clauses sur des sinistres annotés et la part des dossiers dont la clause citée est confirmée par le gestionnaire.

## Pièges et limites

- **Laisser l'hypothèse de HyDE ou la question générale du step-back atteindre l'utilisateur.** Ce sont des textes de recherche, qui peuvent être faux ; seules les sources retrouvées servent à répondre.
- **Fusionner des facettes par RRF.** Le consensus sacrifie le document trouvé par une seule sous-question (point 3) ; on entrelace (point 4).
- **Appliquer un filtre extrait sans le valider.** Un émirat ou une année mal extraits plafonnent le rappel sans signal (point 7) : liste fermée de valeurs, repli sans filtre, journalisation.
- **Perdre la contrainte en généralisant.** Le step-back et HyDE peuvent effacer le détail qui fait la question (Q6) ; on garde la question d'origine dans la fusion.
- **Laisser le LLM « corriger » un identifiant.** Une réécriture peut changer un numéro de lot, un code de démarche ou un nom propre ; les identifiants exacts se recherchent tels quels, en plus de la requête réécrite.
- **Juger sur des sorties écrites à la main.** Les gains du tableau du point 8 illustrent des mécanismes ; seule une mesure avec le vrai modèle, sur son propre jeu annoté, décide.

### Exercice feuille blanche

1. Sans regarder le code, écrire `entrelacer`, puis démontrer à nouveau que le premier document de la liste j arrive à une position au plus égale à j. Vérifier sur Q2 que la décomposition renvoie `transfert-dubai`, `commission-agent`, `hypotheque-enreg`.
2. Prédire, puis vérifier : avec les quatre listes du multi-query de Q2, que contient le top-2 de la fusion RRF, et quel est son Recall@2 ? (Réponse : `transfert-dubai` et `offplan-abudhabi`, d'après les scores 0,0325 et 0,0317 ; un seul pertinent, donc 1/3 ≈ 0,33.)
3. Trouver le bug : dans `filtre_depuis`, la ligne devient `if "annee_min" in filtres and d.annee <= filtres["annee_min"]`. Que renvoie le self-query de Q6, et pourquoi le rappel tombe-t-il sans aucun message d'erreur ? (Réponse : les règlements de 2025 sont exclus, la liste est vide et le Recall@3 vaut 0 ; c'est le point 7.)

## Pour aller plus loin

- **Sources des techniques** : HyDE (Gao et al., 2022, « Precise Zero-Shot Dense Retrieval without Relevance Labels ») ; le step-back prompting (Zheng et al., 2023) ; RAG-Fusion, qui combine reformulations et RRF, popularisé en 2023 ; query2doc (Wang et al., 2023), proche de HyDE, qui concatène la question et le passage généré.
- **Élargir les documents plutôt que la requête** : doc2query (Nogueira et al., 2019) fait générer, hors ligne, les questions auxquelles chaque document répond, et les ajoute à l'index. Le coût passe de la requête à l'indexation, ce qui supprime l'appel au LLM au moment de la question.
- **Routage appris** : au lieu d'un routeur à règles, un petit classifieur entraîné sur des questions étiquetées par la technique qui les sert le mieux ; on le juge par le rappel obtenu et par le coût moyen.

> Étape 30 ter du parcours · Prérequis : [Reranking par cross-encodeur](<30b-RAG-Reranking-Cross-Encodeur.md>) · Suite : [Découpage avancé et compression](<30d-RAG-Decoupage-Avance-et-Compression.md>)
