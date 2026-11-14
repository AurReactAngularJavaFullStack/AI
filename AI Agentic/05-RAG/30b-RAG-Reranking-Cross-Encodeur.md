# Étape 30 bis — RAG — Reranking par cross-encodeur

> Étape 30 bis du parcours · Prérequis : [Applications du RAG par domaine](<30-RAG-Applications-Domaines.md>) · Suite : [Transformations de requête](<30c-RAG-Transformations-de-Requete.md>)

**Dossier :** 05-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  
**Nom du fichier :** 30b-RAG-Reranking-Cross-Encodeur.md

## Définition

Le reranking, ou reclassement, organise la recherche en **deux étapes**. La première étape, le retriever, parcourt tout le corpus avec une fonction de score bon marché, BM25 (étape 22), un cosinus entre embeddings (étape 19) ou leur fusion (étapes 23 et 24), et ne garde qu'une liste de N candidats, de quelques dizaines à quelques centaines : elle vise le **rappel**. La seconde étape, le reranker, relit chaque paire (question, candidat) avec un modèle plus coûteux et plus fin, le **cross-encodeur**, et ne garde que les k meilleurs, typiquement de 3 à 10 : elle vise la **précision**. Un bi-encodeur, celui de l'étape 19, encode la question et le document séparément ; le vecteur du document est calculé une fois pour toutes, hors ligne, sans connaître la question. Un cross-encodeur lit la question et le document **ensemble**, dans la même entrée, et renvoie un score de pertinence pour cette paire ; rien ne peut donc être précalculé, et il faut N passages du modèle à chaque requête. Le principe est simple : un calcul bon marché sur tout le corpus, un calcul cher sur peu de documents.

## Rôle dans un agent

Le reranker vit **à l'intérieur de l'outil de recherche**. L'agent perçoit une question, décide d'appeler son outil `chercher`, et l'outil enchaîne les deux étapes avant de renvoyer son résultat : seuls les k passages retenus entrent dans le message que le modèle observe au tour suivant. C'est donc le reranker qui décide de ce qui occupe la place, limitée et payée au token, du contexte (étape 13 ter). Son score sert aussi à une seconde décision : comme il juge chaque paire dans l'absolu, il peut être calibré et comparé à un seuil, ce que RRF interdit (étape 24, point 2) ; sous ce seuil, l'agent s'abstient ou demande une précision au lieu de répondre à partir de passages faibles. En architecture hexagonale, le reranker est un **port**, une fonction `scorer(question, texte) -> float`, et chaque implémentation est un adaptateur : le cross-encodeur jouet de ce fichier, un modèle local, ou un service distant. Le pipeline ne change pas quand on change d'adaptateur, ce qui garde l'agent indépendant de tout fournisseur.

## Équation complète

Étape 1, les N candidats du retriever sur le corpus 𝒟 :

$$
C_N(q) = \underset{d \in \mathcal{D}}{\text{top-}N}\; s_1(q, d)
$$

Score séparable d'un bi-encodeur (étape 19) :

$$
s_1(q, d) = \cos\big(E(q),\, E(d)\big)
$$

Score d'un cross-encodeur : un réseau qui lit la paire concaténée.

$$
s_2(q, d) = f_\theta\big([\text{CLS}]\; q\; [\text{SEP}]\; d\big)
$$

Le cross-encodeur jouet de ce fichier remplace le réseau par une combinaison de traits d'interaction :

$$
s_2(q, d) = \sum_{j} w_j\, \varphi_j(q, d)
$$

Étape 2, la liste finale des k documents :

$$
L_k(q) = \underset{d \in C_N(q)}{\text{top-}k}\; s_2(q, d) \qquad \text{donc} \qquad L_k(q) \subseteq C_N(q)
$$

Borne démontrée au point 1 :

$$
\text{Recall@}k\big(L_k(q)\big) \le \text{Recall@}N\big(C_N(q)\big)
$$

Latence d'une requête quand les N paires passent dans le modèle par lots de B :

$$
T(N) = T_1 + \left\lceil \frac{N}{B} \right\rceil t_{lot}
$$

Plus grand N compatible avec un budget de latence :

$$
N_{max} = B \left\lfloor \frac{T_{budget} - T_1}{t_{lot}} \right\rfloor
$$

## Décryptage des symboles

$$
q,\; d
$$

**Sens :** la question et un document (un morceau de texte) · **Type / plage :** chaînes · **Variable Python :** `question`, `doc` ou `texte`

$$
\mathcal{D}
$$

**Sens :** le corpus entier · **Type / plage :** ensemble de documents, de taille |𝒟| · **Variable Python :** `CORPUS`

$$
s_1(q, d)
$$

**Sens :** score de l'étape 1, bon marché et calculable sur tout le corpus · **Type / plage :** réel ≥ 0 pour BM25, dans [−1, 1] pour un cosinus · **Variable Python :** `bm25_score(...)`

$$
E(\cdot)
$$

**Sens :** l'encodeur d'un bi-encodeur, qui transforme un texte en vecteur sans voir l'autre texte · **Type / plage :** vecteur de dimension fixe · **Variable Python :** absent ici, l'étape 1 est BM25

$$
s_2(q, d)
$$

**Sens :** score de l'étape 2, calculé sur la paire · **Type / plage :** réel, sans borne a priori · **Variable Python :** `cross_encodeur_jouet(question, doc)`

$$
f_\theta
$$

**Sens :** un vrai cross-encodeur, réseau de paramètres θ entraîné sur des paires étiquetées · **Type / plage :** fonction de la paire vers un réel · **Variable Python :** l'adaptateur `RerankerLocal` de l'extrait

$$
\varphi_j(q, d)
$$

**Sens :** le j-ième trait d'interaction du jouet : recouvrement, expression, nombres, entités, conflit · **Type / plage :** réel dans [0, 1] · **Variable Python :** `traits(question, doc)[nom]`

$$
w_j
$$

**Sens :** poids du trait j, fixé à la main ici, appris dans un vrai modèle · **Type / plage :** réel, négatif pour le conflit · **Variable Python :** `POIDS[nom]`

$$
N,\; k
$$

**Sens :** nombre de candidats de l'étape 1, et nombre de documents gardés · **Type / plage :** entiers, k ≤ N · **Variable Python :** `n`, `k`

$$
C_N(q)
$$

**Sens :** les candidats de l'étape 1, dans leur ordre · **Type / plage :** liste d'au plus N identifiants · **Variable Python :** `etape1(question, n)`

$$
L_k(q)
$$

**Sens :** la liste finale, qui entre dans le prompt · **Type / plage :** liste d'au plus k identifiants · **Variable Python :** `pipeline(question, n, k, scorer)[1]`

$$
B,\; t_{lot},\; T_1
$$

**Sens :** taille d'un lot de paires, temps de calcul d'un lot, temps de l'étape 1 · **Type / plage :** entier ≥ 1, millisecondes, millisecondes · **Variable Python :** `taille_lot`, `t_lot_ms`, `t_etape1_ms`

$$
T(N),\; N_{max}
$$

**Sens :** latence de la requête, et plus grand nombre de candidats qui tient dans le budget · **Type / plage :** millisecondes, entier · **Variable Python :** `latence_ms(...)`, `n_max(...)`

## Démonstration

### 1. Le reranker choisit parmi les candidats, il n'en ajoute aucun

Par construction, le reranker trie les candidats de l'étape 1 puis en garde k. La liste finale est donc une partie de la liste des candidats :

$$
L_k(q) \subseteq C_N(q)
$$

Si Rel désigne l'ensemble des documents pertinents, on en déduit, parce que l'intersection respecte l'inclusion,

$$
\text{Rel} \cap L_k(q) \subseteq \text{Rel} \cap C_N(q) ,
$$

donc, en comptant les éléments puis en divisant par |Rel| > 0 :

$$
\text{Recall@}k\big(L_k\big) = \frac{|\text{Rel} \cap L_k|}{|\text{Rel}|} \le \frac{|\text{Rel} \cap C_N|}{|\text{Rel}|} = \text{Recall@}N\big(C_N\big)
$$

Avec la borne de l'étape 25, on obtient même

$$
\text{Recall@}k\big(L_k\big) \le \min\Big(\text{Recall@}N\big(C_N\big),\; \frac{k}{|\text{Rel}|}\Big) ,
$$

et, de la même façon, P@k ≤ |Rel ∩ Cₙ| / k. L'égalité n'a lieu que si le reranker place en tête **tous** les pertinents présents parmi les candidats. La conséquence pratique est brutale : **un document manqué par l'étape 1 est perdu**, quel que soit le reranker. Sur la question Q1 du programme, le document `pension-justif`, pertinent, n'arrive qu'au sixième rang de BM25. Avec N = 5, le Recall@5 de l'étape 1 vaut 0,5, et même un reranker parfait plafonne à un Recall@3 de 0,5 ; avec N = 8, le document entre dans les candidats et le cross-encodeur jouet atteint 1. La question Q4, « documents d'identité », ne partage aucun mot avec le document `kyc-pieces` (« Emirates ID », « attestation ») : BM25 ne le renvoie jamais, et aucun N ne le sauve. Le remède est à l'étape 1 : embeddings, fusion hybride ou réécriture de la requête (étape 30 ter). Le programme vérifie l'inclusion et la borne sur 72 combinaisons : 6 questions, 3 valeurs de N, 4 rerankers.

### 2. L'oracle est le plafond, et l'étape 1 fixe ce plafond

Appelons oracle le reranker qui connaît les notes des experts et trie les candidats par note décroissante. L'inégalité de réarrangement démontrée à l'étape 28 (point 2) dit que, parmi toutes les listes de k documents tirées des candidats, celle qui maximise le DCG@k prend les k meilleures notes et les range par ordre décroissant : c'est exactement la liste de l'oracle. Pour tout reranker R, on a donc

$$
\text{NDCG@}k(R) \le \text{NDCG@}k(\text{oracle sur } C_N) \le 1 ,
$$

et la seconde inégalité est une égalité seulement si les k documents les mieux notés de **tout** le corpus figurent parmi les candidats, parce que l'IDCG se calcule sur tous les documents jugés (étape 28, point 1). Sur les six questions, l'oracle n'obtient que 0,7972 en moyenne : 0 sur Q4, dont le seul pertinent est absent ; 0,8657 sur Q1, à cause de `pension-justif` ; 0,9173 sur Q6, où le document `dbr-general`, noté 1, n'a aucun mot commun avec la question. Ce plafond se lit avant d'acheter ou d'entraîner un reranker : si l'oracle lui-même gagne peu, l'effort doit porter sur l'étape 1.

### 3. Le gain dépend de la qualité du reranker, et il peut être négatif

Un reranker n'est qu'une fonction de score ; rien ne garantit qu'elle soit meilleure que celle de l'étape 1. Le programme compare quatre configurations sur les six questions, avec N = 5 et k = 3 :

| Configuration | NDCG@3 moyen | MRR@3 | NDCG@3 par question (Q1 à Q6) |
|---|---|---|---|
| étape 1 seule (BM25) | 0,6230 | 0,5556 | 0,55 · 1,00 · 0,63 · 0,00 · 0,98 · 0,58 |
| reranker biaisé vers les documents longs | 0,2701 | 0,1667 | 0,12 · 0,39 · 0,11 · 0,00 · 0,54 · 0,46 |
| cross-encodeur jouet | 0,6517 | 0,8333 | 0,87 · 0,34 · 0,79 · 0,00 · 1,00 · 0,92 |
| oracle | 0,7972 | 0,8333 | 0,87 · 1,00 · 1,00 · 0,00 · 1,00 · 0,92 |

Le reranker biaisé divise le NDCG par plus de deux : un modèle qui préfère les passages longs, défaut fréquent d'un modèle mal adapté au domaine, fait pire que de ne rien faire. Le cross-encodeur jouet gagne sur Q1, Q3, Q5 et Q6, mais il **perd** sur Q2, de 1 à 0,3374. La question est « la banque achète le bien et le loue au client : est-ce une Murabaha ? ». Le trait de conflit voit « Murabaha » dans la question et « Ijara » dans le bon document, et le pénalise de 1,5 : la fiche Ijara, qui répond pourtant « non, c'est une Ijara », sort du top-3. Un trait lexical ne lit pas l'intention d'une question ; un vrai cross-encodeur, entraîné sur des paires de ce type, peut l'apprendre, mais cela se mesure. Deux leçons en découlent. D'abord, le gain moyen de NDCG n'est que de 0,6517 − 0,6230 = 0,0287, alors qu'il cache une régression sévère : on lit les résultats question par question. Ensuite, le MRR monte de 0,5556 à 0,8333 et ne voit pas la régression de Q2, parce que la fiche Murabaha, notée 2, compte comme pertinente : seule une métrique graduée la révèle.

### 4. Calcul à la main sur Q1 (le code reprend ces nombres)

Après retrait des mots vides, la question « Quel ratio d'endettement maximal pour un client retraité ? » garde cinq termes, ratio, endettement, maximal, client et retraité, et quatre paires de mots consécutifs. Le seul terme reconnu comme entité est « retraité », de type statut. BM25 renvoie cinq candidats :

| Rang BM25 | Document | Note | BM25 | recouvrement | expression | entités | s₂ |
|---|---|---|---|---|---|---|---|
| 1 | `faq-dbr` | 1 | 4,4678 | 3/5 = 0,60 | 1/4 = 0,25 | 0 | 0,85 |
| 2 | `dbr-general` | 1 | 3,1281 | 2/5 = 0,40 | 1/4 = 0,25 | 0 | 0,65 |
| 3 | `dbr-retraite` | 3 | 2,7684 | 2/5 = 0,40 | 1/4 = 0,25 | 1 | 2,15 |
| 4 | `carte-frais` | 0 | 2,3062 | 2/5 = 0,40 | 0 | 0 | 0,40 |
| 5 | `pp-plafond` | 0 | 2,1273 | 1/5 = 0,20 | 0 | 0 | 0,20 |

Pour `dbr-retraite`, les termes communs sont « client » et « retraité », la paire « client retraité » apparaît telle quelle, et l'entité « retraité » est présente ; avec les poids 1, 1 et 1,5, on obtient 0,40 + 0,25 + 1,5 × 1 = 2,15. Pour `faq-dbr`, 0,60 + 0,25 = 0,85. La liste finale est `dbr-retraite`, `faq-dbr`, `dbr-general`, de notes [3, 1, 1]. Les jugements de Q1 sont [3, 2, 1, 1], donc

$$
\text{IDCG@}3 = 7 + 3 \times 0{,}6309 + 1 \times 0{,}5 = 9{,}3928
$$

Avant reranking, les notes [1, 1, 3] donnent

$$
\text{DCG@}3 = 1 + 1 \times 0{,}6309 + 7 \times 0{,}5 = 5{,}1309 , \qquad \text{NDCG@}3 = 5{,}1309 / 9{,}3928 = 0{,}5463
$$

Après reranking, les notes [3, 1, 1] donnent

$$
\text{DCG@}3 = 7 + 0{,}6309 + 0{,}5 = 8{,}1309 , \qquad \text{NDCG@}3 = 8{,}1309 / 9{,}3928 = 0{,}8657
$$

Le rang réciproque passe de 1/3 à 1. Le Recall@3 reste à 0,5, parce que `pension-justif` n'est pas parmi les candidats : c'est le point 1.

### 5. Pourquoi deux étapes : le coût

Le score du bi-encodeur est **séparable** : il ne dépend de d qu'à travers E(d), calculé une fois, hors ligne, pour les |𝒟| documents. À la requête, il ne reste qu'un encodage de la question et une recherche de plus proches voisins (étape 30 quinquies pour les index approchés). Le score du cross-encodeur dépend de la paire : rien n'est précalculable, et chaque candidat coûte un passage du modèle. Le programme le compte : sur les six questions, 26 appels, exactement la somme des tailles des listes de candidats. Les passages se font par lots de B paires sur un accélérateur, d'où la latence T(N) de l'équation complète. Avec des valeurs illustratives, T₁ = 20 ms, B = 16 et 25 ms par lot, on obtient 70 ms pour N = 20, 120 ms pour N = 50 et 195 ms pour N = 100 : la latence monte par paliers de 16 candidats. Pour un budget de 150 ms, la condition T(N) ≤ 150 s'écrit

$$
\left\lceil \frac{N}{16} \right\rceil \le \frac{150 - 20}{25} = 5{,}2
$$

Comme le membre de gauche est un entier, elle équivaut à ⌈N/16⌉ ≤ 5, c'est-à-dire N ≤ 80, parce que ⌈x⌉ ≤ m équivaut à x ≤ m pour tout entier m : c'est la formule de N_max. Appliqué à tout un corpus de 200 000 morceaux, le même cross-encodeur demanderait 12 500 lots, soit 312,5 s par requête ; pour 10 000 requêtes par jour, cela ferait 2 milliards de passages, contre 500 000 avec N = 50, et 200 000 encodages hors ligne plus 10 000 en ligne pour un bi-encodeur seul. Les deux étapes ne sont pas un raffinement : ce sont elles qui rendent le cross-encodeur utilisable.

### 6. Ce que voit un cross-encodeur et pas un bi-encodeur

Les traits du jouet sont des traits d'**interaction** : « expression » cherche dans d les paires de mots consécutifs de q, « conflit » regarde si d cite une autre entité du même type que celle de q. Ils dépendent de q et de d **ensemble**, alors qu'un bi-encodeur doit résumer d dans un vecteur fixe avant d'avoir vu q. Un vrai cross-encodeur concatène la question et le document, et l'attention (étape 31) laisse chaque mot de la question peser chaque mot du document : il peut ainsi voir que « 30 % » est rattaché à « retraité » et non à « carte ». Les traits écrits à la main ne sont qu'une caricature de ce mécanisme ; un vrai modèle apprend ses paramètres θ sur des paires (question, document, étiquette), et l'étape 36 ter reviendra sur l'encodeur et sur ce coût comparé du bi-encodeur et du cross-encodeur.

### 7. Une transformation croissante du score ne change pas l'ordre

Beaucoup de cross-encodeurs renvoient un logit, que l'on passe dans la sigmoïde σ(x) = 1/(1 + e⁻ˣ) pour obtenir un nombre entre 0 et 1. Comme σ est strictement croissante, sᵢ > sⱼ équivaut à σ(sᵢ) > σ(sⱼ), et l'ordre des candidats ne change pas : c'est l'argument de l'étape 24, point 3. Le programme le vérifie sur les six questions. Pour `dbr-retraite`, σ(2,15) = 0,8957. Ce nombre n'est une probabilité que si le modèle a été calibré sur des données du domaine ; sinon, il ne sert qu'à trier, et un seuil posé dessus est arbitraire.

## Effets et comportement

- **Augmenter N** fait monter le rappel de l'étape 1, qui ne baisse jamais quand N grandit (étape 25), donc le plafond du reranker ; la latence monte par paliers d'un lot. Le coût du reranker dépend de N, jamais de la taille du corpus.
- **Diminuer k** améliore la précision et allège le prompt, mais le plafond k/|Rel| du rappel baisse : avec k = 1, une question qui a besoin de deux règles ne peut plus être bien servie.
- **La qualité du reranker décide du signe du gain** (point 3) : un bon modèle remonte les bons documents en tête, un modèle biaisé fait pire que l'étape 1.
- **Le reranker ne corrige pas un décalage de vocabulaire** : il ne voit que ce que l'étape 1 lui donne (point 1).
- **Le score s₂ se compare entre candidats d'une même requête** ; une fois calibré, il peut aussi porter un seuil d'abstention, ce qui est impossible avec un score RRF.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| s₁(q, d) | `bm25_score(tokeniser(question), TOKENS[d], CORPUS_TOK)`, code canonique de l'étape 22 |
| Cₙ(q) | `etape1(question, n)` |
| φⱼ(q, d) | `traits(question, doc)` |
| wⱼ | `POIDS` |
| s₂(q, d) | `cross_encodeur_jouet(question, doc)` |
| Lₖ(q) | `pipeline(question, n, k, scorer)[1]` |
| reranker parfait | `oracle(jugements)` |
| reranker biaisé | `biais_longueur` |
| NDCG@k, RR, Recall@k | `mesures(final, jugements, k)` |
| T(N) | `latence_ms(n, taille_lot, t_lot_ms, t_etape1_ms)` |
| N_max | `n_max(budget_ms, taille_lot, t_lot_ms, t_etape1_ms)` |

### Déroulé, ligne par ligne

**`idf_bm25` et `bm25_score`** sont le code canonique de l'étape 22, recopié tel quel. **`recall_at_k`**, **`reciprocal_rank`**, **`dcg_at_k`** et **`ndcg_at_k`** reprennent les étapes 25, 27 et 28 ; `ndcg_at_k` calcule l'IDCG sur **tous** les documents jugés, ce qui permet de voir qu'un pertinent manque.

**`tokeniser(texte)`** met en minuscules, découpe en suites de lettres et de chiffres avec `\w+`, puis retire les mots vides. Le même traitement sert aux deux étapes : « Quel ratio d'endettement maximal pour un client retraité ? » devient `['ratio', 'endettement', 'maximal', 'client', 'retraité']`.

**`traits(question, doc)`** calcule les cinq traits d'interaction.

- `sq & sd` donne les termes communs. Pour Q1 et `dbr-retraite`, `{'client', 'retraité'}`, d'où un recouvrement de 2/5 = 0,40.
- `bq` et `bd` sont les ensembles de paires consécutives, construits par `zip(tq, tq[1:])`. La paire `('client', 'retraité')` est commune, d'où une expression de 1/4 = 0,25.
- `nq` garde les termes de la question faits de chiffres. Pour Q6, « Plafond de 30 % pour quel client ? », `nq` vaut `{'30'}`, présent dans `dbr-retraite` : le trait vaut 1.
- `eq` et `ed` sont les entités de la question et du document, lues dans le dictionnaire `ENTITES`. Un conflit existe pour un type quand le document cite au moins une entité de ce type et aucune de celles de la question : pour Q5, la question cite « dhabi » et la fiche de Dubaï cite « dubaï », d'où un conflit de 1 et une pénalité de 1,5.
- Chaque trait renvoie 0.0 quand son dénominateur est vide, par exemple quand la question ne contient aucun nombre : le trait ne départage alors personne.

**`cross_encodeur_jouet(question, doc)`** fait la somme pondérée par `POIDS`. Pour Q1 et `dbr-retraite`, `1.0 * 0.40 + 1.0 * 0.25 + 1.5 * 1.0 = 2.15`.

**`etape1(question, n)`** calcule BM25 pour tous les documents, ne garde que les scores strictement positifs, trie par score décroissant puis par identifiant, et coupe à `n`. Pour Q4, seul `carte-frais` partage un mot, « crédit », avec la question : la liste vaut `['carte-frais']`.

**`reclasser(question, candidats, scorer)`** trie les candidats par `-scorer(question, CORPUS[d])`. Le tri de Python est stable : à score égal, l'ordre de l'étape 1 est conservé, ce qui rend la sortie déterministe.

**`pipeline(question, n, k, scorer)`** enchaîne les deux étapes et renvoie le couple (candidats, liste finale) ; avec `scorer=None`, la liste finale est le top-k de BM25.

**`oracle(jugements)`** construit un reranker qui lit la note des experts, et **`biais_longueur`** un reranker qui préfère les documents longs. Les deux ont la même signature que le cross-encodeur jouet : ce sont trois adaptateurs du même port.

**`mesures(final, jugements, k)`** renvoie le NDCG@k gradué, puis le RR et le Recall@k binaires, avec « pertinent » au sens « note ≥ 2 ».

**`latence_ms`** applique T₁ + ⌈N/B⌉ × t_lot avec `math.ceil`, et **`n_max`** la formule de N_max avec `math.floor`.

**`main()`**, bloc par bloc.

1. Q1 à la main : les cinq candidats, leurs traits et leur score s₂, comparés aux valeurs du point 4 ; puis la liste finale et les métriques avant et après, avec les DCG intermédiaires 5,1309 et 9,3928.
2. La double boucle parcourt les 6 questions, les tailles N = 3, 5 et 8 et les 4 rerankers : 72 contrôles de l'inclusion et de la borne du point 1. Viennent ensuite le plafond de Q1 à N = 5, le rattrapage à N = 8 et la question Q4 perdue.
3. Le tableau du point 3 : moyennes et valeurs par question pour les quatre rerankers ; la boucle finale vérifie que l'oracle majore chaque reranker sur chaque question, puis la régression de Q2 est mesurée.
4. La fonction `compteur` enveloppe le cross-encodeur pour compter ses appels : 26, autant que de candidats. Suivent les latences, le N_max de 80 (avec la vérification que N = 81 dépasse le budget) et le décompte des passages par jour.
5. La sigmoïde ne change aucun ordre, sur les six questions et avec N = k = 8.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`idf_bm25(n_t, n_docs)`** — C'est le crieur canonique de l'étape 22, qui annonce le poids d'un mot d'après sa rareté dans la bibliothèque : la fonction reçoit le nombre de documents qui contiennent le terme et le nombre total de documents, puis renvoie le logarithme de 1 + (N − n + 0,5) / (n + 0,5), une valeur toujours positive qui grandit à mesure que le mot se fait rare. Recopiée telle quelle, elle n'est appelée que par `bm25_score`, pour que « retraité » ou « murabaha » pèsent plus lourd que « client » ou « banque », présents dans beaucoup de fiches.

**`bm25_score(requete, doc, corpus, k1, b)`** — C'est le juge lexical canonique de l'étape 22, chargé ici de l'étape 1 du pipeline, celle qui ratisse large pour le rappel : la fonction reçoit la question et un document sous forme de listes de mots, le corpus entier et les réglages k1 = 1,5 et b = 0,75 par défaut, puis additionne, pour chaque mot de la question présent dans le document, son IDF multiplié par une partie fréquence saturée et corrigée par la longueur. Elle renvoie ce score ; pour Q1 et la fiche `dbr-retraite`, il vaut 2,7684, ce qui ne suffit pourtant pas à la mettre en tête, puisqu'elle n'arrive qu'en troisième position de l'étape 1.

**`recall_at_k(retrouves, pertinents, k)`** — C'est le pêcheur de l'étape 25, qui compte la part des poissons connus remontés dans ses k premiers casiers : la fonction reçoit la liste ordonnée, l'ensemble des pertinents et k, lève `ValueError` si k est inférieur à 1, renvoie `None` s'il n'y a aucun pertinent, et sinon divise le nombre de pertinents trouvés parmi les k premiers par le nombre total de pertinents. Le programme s'en sert pour prouver qu'un reranker ne crée pas de rappel : pour Q1 avec N = 5, BM25 n'atteint que 0,5, et même l'oracle plafonne alors à un Recall@3 de 0,5.

**`reciprocal_rank(retrouves, pertinents, k)`** — Cette variante du barème de l'étape 27 prend directement la liste au lieu d'un rang déjà calculé, comme un lecteur qui descend lui-même la page plutôt que de lire un chiffre noté par un autre : la fonction reçoit la liste ordonnée, l'ensemble des pertinents et k, parcourt les k premiers documents en numérotant les rangs à partir de 1, et renvoie 1 divisé par le rang du premier pertinent, ou 0,0 si aucun n'apparaît. Pour Q1, elle passe de 1/3 avant reranking à 1 après, puisque `dbr-retraite` remonte du troisième au premier rang.

**`remise(i)`** — Cette petite fonction est le barème de dépréciation de l'étape 28, qui dit combien vaut encore un document selon la marche du podium où il se tient : elle reçoit un rang i compté à partir de 1 et renvoie 1 / log₂(i + 1), soit 1 au premier rang, environ 0,63 au deuxième et 0,5 au troisième. Elle ne vérifie rien et n'est appelée que par `dcg_at_k`, qui multiplie par elle le gain de chaque document pour que les places de tête comptent davantage que les suivantes.

**`dcg_at_k(rels, k)`** — C'est le caissier de l'étape 28, qui additionne la valeur des documents servis en appliquant à chacun la remise de son rang : la fonction reçoit la liste des notes dans l'ordre du classement et la profondeur k, lève `ValueError` si k est inférieur à 1, puis additionne, pour chacun des k premiers rangs, le gain 2 élevé à la note, moins 1, multiplié par `remise(i)`. Elle renvoie ce total ; pour Q1, les notes [1, 1, 3] de l'étape 1 donnent 5,1309, et les meilleures notes possibles [3, 2, 1, 1] donnent un idéal de 9,3928 sur trois rangs.

**`ndcg_at_k(rels_retrouves, rels_tous_juges, k)`** — Elle compare le repas servi au meilleur repas possible avec tous les plats jugés en cuisine : la fonction reçoit les notes des documents retrouvés, celles de tous les documents jugés et k, lève `ValueError` si la liste retrouvée contient plus de notes pertinentes que les jugements n'en prévoient, calcule l'IDCG sur toutes les notes jugées triées par ordre décroissant, renvoie `None` si cet idéal est nul et sinon le rapport du DCG retrouvé à l'IDCG. Comme l'idéal inclut les pertinents oubliés par l'étape 1, elle montre qu'il en manque un : pour Q1, le NDCG@3 passe de 0,5463 à 0,8657 après reranking, sans atteindre 1.

**`tokeniser(texte)`** — C'est le découpeur commun aux deux étapes, qui transforme une phrase en liste de mots significatifs : la fonction reçoit un texte, le met en minuscules, en extrait toutes les suites de lettres et de chiffres avec l'expression `\w+`, puis retire les mots vides de la liste `MOTS_VIDES`. Elle renvoie la liste ordonnée des mots restants, et c'est ce même traitement que reçoivent la question, les documents de l'étape 1 et les paires lues par le cross-encodeur ; « Quel ratio d'endettement maximal pour un client retraité ? » devient ainsi ratio, endettement, maximal, client, retraité.

**`traits(question, doc)`** — Cette fonction est l'examinateur qui lit la question et le document côte à côte, ce qu'un bi-encodeur ne fait jamais, et note cinq aspects de leur rencontre : elle reçoit les deux textes, les découpe, puis calcule la part des mots de la question présents dans le document, la part de ses paires de mots consécutifs retrouvées telles quelles, la part de ses nombres présents, la part de ses entités présentes, et la part des types d'entité pour lesquels le document cite une autre entité du même type, ce qui signale un conflit. Chaque trait vaut 0 quand son dénominateur est vide, et la fonction renvoie un dictionnaire de cinq nombres ; pour Q1 et `dbr-retraite`, le recouvrement vaut 0,40, l'expression 0,25 et les entités 1.

**`cross_encodeur_jouet(question, doc)`** — Il tient la place d'un vrai modèle entraîné qui lirait la question et le document ensemble : la fonction reçoit les deux textes, demande ses cinq traits à `traits`, multiplie chacun par son poids dans `POIDS`, 1 pour le recouvrement et l'expression, 0,5 pour les nombres, 1,5 pour les entités et −1,5 pour un conflit, et renvoie la somme. Sur les cinq candidats de Q1, elle donne 2,15 à `dbr-retraite`, 0,85 à `faq-dbr`, 0,65 à `dbr-general`, 0,40 à `carte-frais` et 0,20 à `pp-plafond`, ce qui remonte la bonne fiche en tête.

**`reclasser(question, candidats, scorer)`** — C'est le second jury, celui de la précision, qui reprend les finalistes retenus par le premier et les remet dans l'ordre selon son propre barème : la fonction reçoit la question, la liste des candidats de l'étape 1 et une fonction de score qui prend une question et un texte, calcule le score de chaque candidat sur son texte complet et renvoie les candidats triés par score décroissant. Comme le tri de Python est stable, deux candidats à égalité gardent l'ordre de l'étape 1, ce qui rend la sortie identique d'une exécution à l'autre.

**`pipeline(question, n, k, scorer)`** — Cette fonction enchaîne les deux étapes comme une chaîne de tri postal, un premier tamis grossier puis une main experte : elle reçoit la question, la taille N du premier tamis, la taille k de la liste finale et le reranker, demande à `etape1` les N meilleurs candidats de BM25, les fait reclasser par `reclasser` si un reranker est fourni, et garde les k premiers. Elle renvoie le couple (candidats, liste finale) ; avec un reranker absent, la liste finale est simplement le top-k de BM25, ce qui fournit le repère « étape 1 seule » du tableau.

**`oracle(jugements)`** — C'est un juge qui triche en connaissant d'avance la grille des experts, gardé comme plafond de mesure et jamais comme composant de production : la fonction reçoit le dictionnaire des notes d'une question, construit une table qui associe à chaque texte de document sa note, et renvoie une fonction de même signature que le cross-encodeur, qui donne à toute paire (question, texte) la note du texte, ou 0 s'il n'est pas jugé. Le programme vérifie qu'aucun reranker ne la dépasse sur aucune question, et sa moyenne NDCG@3 de 0,7972 sert de borne haute.

**`biais_longueur(question, doc)`** — Voici le mauvais juge, celui qui préfère les plaidoiries les plus longues quel qu'en soit le sujet : la fonction reçoit une question, qu'elle ignore complètement, et un texte, et renvoie le nombre de mots de ce texte après découpage par `tokeniser`. Elle sert de repère bas : avec elle, le NDCG@3 moyen tombe à 0,2701 et le MRR@3 à 0,1667, bien en dessous de l'étape 1 seule, ce qui montre qu'un reranker peut aussi dégrader les résultats.

**`mesures(final, jugements, k)`** — C'est le bulletin de notes d'une liste finale : la fonction reçoit les documents retenus, le dictionnaire des notes d'expert et k, définit les pertinents comme les documents notés au moins 2, lit la note de chaque document retenu, et renvoie un triplet formé du NDCG@k gradué, du rang réciproque et du Recall@k binaires. Pour Q1, elle rend environ (0,5463 ; 0,3333 ; 0,5) avant reranking et (0,8657 ; 1 ; 0,5) après, et c'est elle qui alimente les moyennes du tableau du point 3.

**`latence_ms(n, taille_lot, t_lot_ms, t_etape1_ms)`** — Cette fonction joue le chef de quai qui calcule combien de temps prendra le chargement des paires dans le modèle, par camions de taille fixe : elle reçoit le nombre N de candidats, la taille B d'un lot, la durée d'un lot et la durée de l'étape 1, et renvoie T₁ + ⌈N / B⌉ × t_lot, en arrondissant le nombre de lots au-dessus avec `math.ceil`, puisqu'un lot incomplet coûte autant qu'un lot plein. Avec des lots de 16 paires traités en 25 ms et une étape 1 de 20 ms, elle donne 70, 120 et 195 ms pour N = 20, 50 et 100, et 312 500 ms, étape 1 non comptée, pour un corpus entier de 200 000 morceaux.

**`n_max(budget_ms, taille_lot, t_lot_ms, t_etape1_ms)`** — Elle répond à la question inverse, celle du responsable qui dispose d'un budget de latence et veut savoir jusqu'où il peut pousser N : la fonction reçoit le budget, la taille d'un lot, la durée d'un lot et la durée de l'étape 1, retranche l'étape 1 du budget, compte combien de lots entiers tiennent dans le reste avec `math.floor`, et renvoie ce nombre multiplié par la taille d'un lot. Pour un budget de 150 ms, elle donne 16 × 5 = 80 candidats, et `main` vérifie que 81 dépasserait le budget.

**`main()`** — Le chef d'orchestre déroule cinq démonstrations : il refait Q1 à la main, avec les cinq candidats, leurs traits et leurs scores, la liste finale et les métriques avant et après, puis mène 72 contrôles sur six questions, trois tailles de N et quatre rerankers pour prouver que la liste finale reste incluse dans les candidats et que le rappel ne peut pas monter, avant de montrer le rattrapage de Q1 à N = 8 et la question Q4 perdue d'avance. Il dresse ensuite le tableau des quatre rerankers, vérifie que l'oracle majore tout et mesure la régression de Q2 (1 → 0,34), compte les 26 appels au modèle, calcule latences, N max et passages par jour, et vérifie qu'une sigmoïde ne change aucun ordre. Chaque nombre est gardé par un `assert`, et la ligne finale n'annonce le succès que si tous ont tenu.

**`compteur(q, texte)`** — Cette fonction interne, définie dans `main`, est un mouchard glissé dans la chaîne, qui note chaque passage avant de laisser faire le vrai travail : elle reçoit une question et un texte, ajoute ce texte à la liste `appels`, puis renvoie exactement le score de `cross_encodeur_jouet` pour la même paire. Branchée à la place du cross-encodeur dans `pipeline`, elle permet de vérifier que les six questions déclenchent 26 appels au modèle, autant que de candidats fournis par l'étape 1, ce qui rend concret le coût de N passages par requête.

**`sigmoide(q, texte)`** — Cette autre fonction interne de `main` est un traducteur qui convertit le score brut du cross-encodeur en un nombre entre 0 et 1, comme on convertirait des points en pourcentage : elle reçoit une question et un texte, calcule le score jouet de la paire et renvoie 1 / (1 + exp(−score)), soit environ 0,8957 pour les 2,15 de `dbr-retraite`. Comme cette transformation est strictement croissante, `main` vérifie qu'en la branchant à la place du cross-encodeur, avec N = k = 8, les six questions gardent exactement le même ordre.

```python
"""Étape 30 bis — reranking en deux étapes : BM25 sur un top-N pour le rappel, cross-encodeur jouet sur un top-k pour la précision."""
import math
import re
import sys
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- étape 1 : BM25 (code canonique, étape 22)
def idf_bm25(n_t: int, n_docs: int) -> float:
    """Variante utilisée par Lucene et la plupart des moteurs : toujours positive."""
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


# ---------------------------------------------------------------- métriques (étapes 25, 27 et 28)
def recall_at_k(retrouves: list[str], pertinents: set[str], k: int) -> float | None:
    """|Rel ∩ Top_k| / |Rel| ; None si aucun document n'est pertinent (la métrique n'est pas définie)."""
    if k < 1:
        raise ValueError("k doit valoir au moins 1")
    if not pertinents:
        return None
    return len(set(retrouves[:k]) & pertinents) / len(pertinents)


def reciprocal_rank(retrouves: list[str], pertinents: set[str], k: int) -> float:
    """1 / rang du premier pertinent parmi les k premiers ; 0 s'il n'y en a aucun (rang infini, étape 27)."""
    for rang, doc in enumerate(retrouves[:k], start=1):
        if doc in pertinents:
            return 1.0 / rang
    return 0.0


def remise(i: int) -> float:
    return 1.0 / math.log2(i + 1)


def dcg_at_k(rels: list[int], k: int) -> float:
    if k < 1:
        raise ValueError("k doit être un entier >= 1")
    return sum((2 ** rel - 1) * remise(i) for i, rel in enumerate(rels[:k], start=1))


def ndcg_at_k(rels_retrouves: list[int], rels_tous_juges: list[int], k: int) -> float | None:
    """NDCG@k ; l'IDCG vient de TOUS les documents jugés (étape 28) ; None si aucun pertinent jugé."""
    manque = Counter(r for r in rels_retrouves if r > 0) - Counter(r for r in rels_tous_juges if r > 0)
    if manque:
        raise ValueError(f"notes retrouvées absentes des jugements : {dict(manque)}")
    idcg = dcg_at_k(sorted(rels_tous_juges, reverse=True), k)
    if idcg == 0.0:
        return None
    return dcg_at_k(rels_retrouves, k) / idcg


# ---------------------------------------------------------------- texte
MOTS_VIDES = {"le", "la", "les", "l", "d", "de", "du", "des", "un", "une", "et", "ou", "pour", "au", "aux",
              "à", "a", "en", "par", "sur", "sa", "son", "ses", "ne", "pas", "qui", "que", "quel", "quelle",
              "quels", "quelles", "est", "on", "il", "t", "s", "se", "ce", "avec", "dans", "puis", "plus",
              "si", "je", "mon", "ma", "mes", "faut", "peut"}


def tokeniser(texte: str) -> list[str]:
    """Minuscules, suites de lettres et de chiffres, mots vides retirés (même traitement aux deux étapes)."""
    return [t for t in re.findall(r"\w+", texte.lower()) if t not in MOTS_VIDES]


# Entités reconnues par le cross-encodeur jouet ; le type sert à repérer un conflit (Abu Dhabi demandé, Dubaï servi).
ENTITES = {"retraité": "statut", "murabaha": "produit", "ijara": "produit",
           "dubaï": "émirat", "dhabi": "émirat", "sharjah": "émirat"}


# ---------------------------------------------------------------- étape 2 : cross-encodeur jouet
POIDS = {"recouvrement": 1.0, "expression": 1.0, "nombres": 0.5, "entites": 1.5, "conflit": -1.5}


def traits(question: str, doc: str) -> dict[str, float]:
    """Traits d'INTERACTION : chacun dépend à la fois de q et de d, ce qu'un bi-encodeur ne calcule jamais."""
    tq, td = tokeniser(question), tokeniser(doc)
    sq, sd = set(tq), set(td)
    bq, bd = set(zip(tq, tq[1:])), set(zip(td, td[1:]))
    nq = {t for t in sq if t.isdigit()}
    eq, ed = {t for t in sq if t in ENTITES}, {t for t in sd if t in ENTITES}
    types_q = {ENTITES[e] for e in eq}
    conflits = [ty for ty in types_q
                if {e for e in ed if ENTITES[e] == ty} and not ({e for e in ed if ENTITES[e] == ty} & eq)]
    return {
        "recouvrement": len(sq & sd) / len(sq) if sq else 0.0,         # part des termes de q présents dans d
        "expression": len(bq & bd) / len(bq) if bq else 0.0,           # part des paires de mots de q retrouvées telles quelles
        "nombres": len(nq & sd) / len(nq) if nq else 0.0,              # part des nombres de q présents dans d
        "entites": len(eq & ed) / len(eq) if eq else 0.0,              # part des entités de q présentes dans d
        "conflit": len(conflits) / len(types_q) if types_q else 0.0,   # d cite une AUTRE entité du même type
    }


def cross_encodeur_jouet(question: str, doc: str) -> float:
    """s₂(q, d) = Σ w_j φ_j(q, d) : tient la place d'un modèle entraîné qui lit q et d ensemble."""
    return sum(POIDS[nom] * v for nom, v in traits(question, doc).items())


# ---------------------------------------------------------------- corpus et jeu d'évaluation (fictifs)
CORPUS = {
    "pp-plafond": "Prêt personnel : le montant maximal ne dépasse pas 20 fois le salaire mensuel, sur une durée de 48 mois au plus.",
    "dbr-general": "Ratio d'endettement : le total des mensualités, nouvelle mensualité comprise, ne dépasse pas 50 % du salaire mensuel.",
    "dbr-retraite": "Client retraité : le total des mensualités ne dépasse pas 30 % du revenu mensuel de retraite.",
    "faq-dbr": "FAQ ratio d'endettement : comment le calculer pour un client ? On additionne toutes les mensualités du client.",
    "carte-frais": "Carte de crédit : plafond de la carte, ratio du paiement minimal et plafond de retrait du client.",
    "murabaha": "Murabaha : la banque achète le bien puis le revend au client avec une marge fixée à l'avance.",
    "ijara": "Ijara : la banque achète le bien et le loue au client ; le loyer remplace les intérêts.",
    "kyc-pieces": "KYC : copie de l'Emirates ID, attestation de salaire et relevés bancaires des trois derniers mois.",
    "hypo-apport": "Prêt hypothécaire : apport minimal et durée maximale selon le statut du client et le prix du bien.",
    "hypo-frais-dubai": "Prêt hypothécaire à Dubaï : frais de transfert DLD de 4 % de la valeur du bien, et frais d'enregistrement de l'hypothèque.",
    "hypo-frais-ad": "Prêt hypothécaire à Abu Dhabi : frais d'enregistrement du bien fixés par le barème de l'émirat.",
    "remb-anticipe": "Remboursement anticipé d'un prêt personnel : frais plafonnés selon la politique interne de la banque.",
    "domiciliation": "Domiciliation du salaire : condition habituelle pour obtenir un prêt personnel auprès de la banque.",
    "pension-justif": "Retraité : justificatif de pension exigé, et revenu de retraite pris en compte pour le calcul.",
}
IDS = sorted(CORPUS)
TOKENS = {i: tokeniser(CORPUS[i]) for i in IDS}
CORPUS_TOK = [TOKENS[i] for i in IDS]

# Notes de 0 à 3 données par des experts ; un document non listé vaut 0 ; « pertinent » signifie note ≥ 2.
QUESTIONS = [
    ("Q1", "Quel ratio d'endettement maximal pour un client retraité ?",
     {"dbr-retraite": 3, "pension-justif": 2, "dbr-general": 1, "faq-dbr": 1}),
    ("Q2", "La banque achète le bien et le loue au client : est-ce une Murabaha ?",
     {"ijara": 3, "murabaha": 2}),
    ("Q3", "Un client retraité peut-il obtenir un prêt personnel avec sa pension ?",
     {"pension-justif": 3, "dbr-retraite": 2, "pp-plafond": 1}),
    ("Q4", "Quels documents d'identité fournir pour le dossier de crédit ?",
     {"kyc-pieces": 3}),
    ("Q5", "Frais d'enregistrement du bien pour un prêt hypothécaire à Abu Dhabi ?",
     {"hypo-frais-ad": 3, "hypo-apport": 1}),
    ("Q6", "Plafond de 30 % pour quel client ?",
     {"dbr-retraite": 3, "dbr-general": 1}),
]


# ---------------------------------------------------------------- pipeline en deux étapes
def etape1(question: str, n: int) -> list[str]:
    """Top-N de BM25 : documents de score > 0, triés par score décroissant puis par identifiant."""
    tq = tokeniser(question)
    scores = [(i, bm25_score(tq, TOKENS[i], CORPUS_TOK)) for i in IDS]
    return [i for i, s in sorted(scores, key=lambda kv: (-kv[1], kv[0])) if s > 0][:n]


def reclasser(question: str, candidats: list[str], scorer) -> list[str]:
    """Tri par score décroissant ; à égalité, l'ordre de l'étape 1 est conservé (le tri de Python est stable)."""
    return sorted(candidats, key=lambda d: -scorer(question, CORPUS[d]))


def pipeline(question: str, n: int, k: int, scorer) -> tuple[list[str], list[str]]:
    """Renvoie (candidats de l'étape 1, liste finale de k documents). scorer = None : étape 1 seule."""
    candidats = etape1(question, n)
    ordre = reclasser(question, candidats, scorer) if scorer else candidats
    return candidats, ordre[:k]


def oracle(jugements: dict[str, int]):
    """Reranker parfait : il connaît les notes des experts. C'est un plafond de mesure, jamais un composant de production."""
    notes = {CORPUS[d]: r for d, r in jugements.items()}
    return lambda question, texte: float(notes.get(texte, 0))


def biais_longueur(question: str, doc: str) -> float:
    """Mauvais reranker : il préfère les documents longs, quel que soit leur sujet."""
    return float(len(tokeniser(doc)))


def mesures(final: list[str], jugements: dict[str, int], k: int) -> tuple[float, float, float]:
    """(NDCG@k gradué, RR@k et Recall@k avec « pertinent » = note ≥ 2)."""
    pertinents = {d for d, r in jugements.items() if r >= 2}
    rels = [jugements.get(d, 0) for d in final]
    return (ndcg_at_k(rels, list(jugements.values()), k), reciprocal_rank(final, pertinents, k),
            recall_at_k(final, pertinents, k))


# ---------------------------------------------------------------- coûts
def latence_ms(n: int, taille_lot: int, t_lot_ms: float, t_etape1_ms: float) -> float:
    """T = T₁ + ⌈N / B⌉ × t_lot : les N paires (q, d) passent dans le modèle par lots de B."""
    return t_etape1_ms + math.ceil(n / taille_lot) * t_lot_ms


def n_max(budget_ms: float, taille_lot: int, t_lot_ms: float, t_etape1_ms: float) -> int:
    """Le plus grand N, multiple de B, dont la latence tient dans le budget."""
    return taille_lot * math.floor((budget_ms - t_etape1_ms) / t_lot_ms)


def main() -> None:
    n, k = 5, 3
    print("1. Q1 à la main : BM25 donne le top-5, le cross-encodeur jouet garde un top-3")
    _, q1, jug1 = QUESTIONS[0]
    candidats = etape1(q1, n)
    tq1 = tokeniser(q1)
    attendus = {"faq-dbr": 0.85, "dbr-general": 0.65, "dbr-retraite": 2.15, "carte-frais": 0.40, "pp-plafond": 0.20}
    for rang, d in enumerate(candidats, start=1):
        tr = traits(q1, CORPUS[d])
        s2 = cross_encodeur_jouet(q1, CORPUS[d])
        print(f"  {rang}. {d:<13} note {jug1.get(d, 0)}  BM25 {bm25_score(tq1, TOKENS[d], CORPUS_TOK):.4f}"
              f"  rec {tr['recouvrement']:.2f}  expr {tr['expression']:.2f}  ent {tr['entites']:.0f}  s2 = {s2:.2f}")
        assert abs(s2 - attendus[d]) < 1e-12
    _, final1 = pipeline(q1, n, k, cross_encodeur_jouet)
    av, ap = mesures(candidats[:k], jug1, k), mesures(final1, jug1, k)
    print(f"  étape 1 seule {candidats[:k]} → reranking {final1}")
    print(f"  NDCG@3 {av[0]:.4f} → {ap[0]:.4f}   RR {av[1]:.4f} → {ap[1]:.4f}   Recall@3 {av[2]:.2f} → {ap[2]:.2f}")
    assert final1 == ["dbr-retraite", "faq-dbr", "dbr-general"]
    assert (round(av[0], 4), round(ap[0], 4)) == (0.5463, 0.8657) and (av[1], ap[1]) == (1 / 3, 1.0)
    assert round(dcg_at_k([1, 1, 3], 3), 4) == 5.1309 and round(dcg_at_k([3, 2, 1, 1], 3), 4) == 9.3928

    print("2. Le reranking ne rattrape pas un document manqué par l'étape 1")
    controles = 0
    for _, q, jug in QUESTIONS:
        pertinents = {d for d, r in jug.items() if r >= 2}
        for taille in (3, 5, 8):
            cands = etape1(q, taille)
            for scorer in (None, cross_encodeur_jouet, oracle(jug), biais_longueur):
                _, fin = pipeline(q, taille, k, scorer)
                assert set(fin) <= set(cands)                                          # L_k ⊆ C_N
                assert recall_at_k(fin, pertinents, k) <= recall_at_k(cands, pertinents, taille)
                controles += 1
    r5 = recall_at_k(etape1(q1, 5), {"dbr-retraite", "pension-justif"}, 5)
    _, fin_o = pipeline(q1, 5, k, oracle(jug1))
    _, fin_8 = pipeline(q1, 8, k, cross_encodeur_jouet)
    print(f"  {controles} contrôles : L_k ⊆ C_N et Recall@3 final ≤ Recall@N de BM25, pour tout reranker")
    print(f"  Q1, N = 5 : Recall@5 de BM25 = {r5:.2f} ; même l'oracle plafonne à Recall@3 = {mesures(fin_o, jug1, k)[2]:.2f}")
    print(f"  Q1, N = 8 : pension-justif entre dans les candidats ; jouet → {fin_8}, Recall@3 = {mesures(fin_8, jug1, k)[2]:.2f}")
    assert controles == 72 and r5 == 0.5 and mesures(fin_o, jug1, k)[2] == 0.5
    assert fin_8 == ["dbr-retraite", "pension-justif", "faq-dbr"] and mesures(fin_8, jug1, k)[:3] == (1.0, 1.0, 1.0)
    _, q4, _ = QUESTIONS[3]
    print(f"  Q4 : candidats de BM25 = {etape1(q4, 8)} ; kyc-pieces ne partage aucun mot avec la question")
    assert etape1(q4, 8) == ["carte-frais"]

    print("3. Le gain dépend de la qualité du reranker (moyennes sur 6 questions, N = 5, k = 3)")
    rerankers = {"étape 1 seule": None, "biais longueur": biais_longueur,
                 "cross-encodeur jouet": cross_encodeur_jouet, "oracle": oracle}
    moyennes, par_q = {}, {}
    for nom, scorer in rerankers.items():
        vals = []
        for _, q, jug in QUESTIONS:
            s = scorer(jug) if scorer is oracle else scorer
            vals.append(mesures(pipeline(q, n, k, s)[1], jug, k))
        par_q[nom] = vals
        moyennes[nom] = (sum(v[0] for v in vals) / len(vals), sum(v[1] for v in vals) / len(vals))
        print(f"  {nom:<21} NDCG@3 {moyennes[nom][0]:.4f}  MRR@3 {moyennes[nom][1]:.4f}   par question "
              + " ".join(f"{v[0]:.2f}" for v in vals))
    assert [round(moyennes[x][0], 4) for x in rerankers] == [0.6230, 0.2701, 0.6517, 0.7972]
    assert [round(moyennes[x][1], 4) for x in rerankers] == [0.5556, 0.1667, 0.8333, 0.8333]
    for i in range(len(QUESTIONS)):                         # l'oracle majore tout reranker (réarrangement, étape 28)
        assert all(par_q["oracle"][i][0] >= par_q[x][i][0] - 1e-12 for x in rerankers)
    q2_av, q2_ap = par_q["étape 1 seule"][1][0], par_q["cross-encodeur jouet"][1][0]
    print(f"  Q2 « est-ce une Murabaha ? » : le trait de conflit écarte ijara, NDCG@3 {q2_av:.2f} → {q2_ap:.2f}")
    assert q2_av == 1.0 and round(q2_ap, 4) == 0.3374

    print("4. Coût : N passages du modèle par requête, et une latence par lots")
    appels = []

    def compteur(q: str, texte: str) -> float:                     # même score, mais chaque appel est compté
        appels.append(texte)
        return cross_encodeur_jouet(q, texte)

    for _, q, _ in QUESTIONS:
        pipeline(q, n, k, compteur)
    nb_candidats = sum(len(etape1(q, n)) for _, q, _ in QUESTIONS)
    print(f"  6 questions : {len(appels)} appels au cross-encodeur = somme des tailles de C_N ({nb_candidats})")
    assert len(appels) == nb_candidats == 26
    for taille in (20, 50, 100):
        print(f"  N = {taille:>3} : T = 20 + ⌈{taille}/16⌉ × 25 = {latence_ms(taille, 16, 25, 20):.0f} ms")
    assert [latence_ms(t, 16, 25, 20) for t in (20, 50, 100)] == [70, 120, 195]
    nm = n_max(150, 16, 25, 20)
    print(f"  budget 150 ms : N max = 16 × ⌊130/25⌋ = {nm} ; corpus entier de 200 000 morceaux : "
          f"{latence_ms(200_000, 16, 25, 0) / 1000:.1f} s par requête")
    assert nm == 80 and latence_ms(80, 16, 25, 20) <= 150 < latence_ms(81, 16, 25, 20)
    assert latence_ms(200_000, 16, 25, 0) == 312_500
    par_jour, corpus_total = 10_000, 200_000
    passages = {"bi-encodeur, hors ligne": corpus_total, "bi-encodeur, en ligne": par_jour,
                "cross-encodeur, N = 50": par_jour * 50, "cross-encodeur, tout le corpus": par_jour * corpus_total}
    for nom, v in passages.items():
        print(f"  passages par jour, {nom:<31} : {v:>13_}".replace("_", " "))
    assert passages["cross-encodeur, N = 50"] == 500_000 and passages["cross-encodeur, tout le corpus"] == 2 * 10 ** 9

    print("5. Une transformation croissante du score (sigmoïde) ne change pas l'ordre")

    def sigmoide(q: str, texte: str) -> float:
        return 1 / (1 + math.exp(-cross_encodeur_jouet(q, texte)))

    assert all(pipeline(q, 8, 8, sigmoide)[1] == pipeline(q, 8, 8, cross_encodeur_jouet)[1] for _, q, _ in QUESTIONS)
    print(f"  ordres identiques pour les 6 questions ; σ(2.15) = {1 / (1 + math.exp(-2.15)):.4f} pour dbr-retraite")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Q1 à la main : BM25 donne le top-5, le cross-encodeur jouet garde un top-3
  3. dbr-retraite  note 3  BM25 2.7684  rec 0.40  expr 0.25  ent 1  s2 = 2.15
  étape 1 seule ['faq-dbr', 'dbr-general', 'dbr-retraite'] → reranking ['dbr-retraite', 'faq-dbr', 'dbr-general']
  NDCG@3 0.5463 → 0.8657   RR 0.3333 → 1.0000   Recall@3 0.50 → 0.50
2. Le reranking ne rattrape pas un document manqué par l'étape 1
  72 contrôles : L_k ⊆ C_N et Recall@3 final ≤ Recall@N de BM25, pour tout reranker
  Q1, N = 5 : Recall@5 de BM25 = 0.50 ; même l'oracle plafonne à Recall@3 = 0.50
  Q1, N = 8 : pension-justif entre dans les candidats ; jouet → ['dbr-retraite', 'pension-justif', 'faq-dbr'], Recall@3 = 1.00
3. Le gain dépend de la qualité du reranker (moyennes sur 6 questions, N = 5, k = 3)
  étape 1 seule         NDCG@3 0.6230  MRR@3 0.5556   par question 0.55 1.00 0.63 0.00 0.98 0.58
  biais longueur        NDCG@3 0.2701  MRR@3 0.1667   par question 0.12 0.39 0.11 0.00 0.54 0.46
  cross-encodeur jouet  NDCG@3 0.6517  MRR@3 0.8333   par question 0.87 0.34 0.79 0.00 1.00 0.92
  oracle                NDCG@3 0.7972  MRR@3 0.8333   par question 0.87 1.00 1.00 0.00 1.00 0.92
  Q2 « est-ce une Murabaha ? » : le trait de conflit écarte ijara, NDCG@3 1.00 → 0.34
4. Coût : N passages du modèle par requête, et une latence par lots
  6 questions : 26 appels au cross-encodeur = somme des tailles de C_N (26)
  budget 150 ms : N max = 16 × ⌊130/25⌋ = 80 ; corpus entier de 200 000 morceaux : 312.5 s par requête
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un reranker ne fabrique pas de rappel, il le trie. Sa valeur se mesure contre deux repères, l'étape 1 seule en dessous et l'oracle au-dessus, question par question, avec une métrique graduée.

### Remplacer le jouet par un vrai modèle, sans changer le pipeline

Le cross-encodeur jouet a la signature d'un vrai : une paire de textes en entrée, un réel en sortie. Un adaptateur local se branche à sa place ; le modèle cité n'est qu'un exemple du marché, entraîné sur des requêtes web en anglais, qu'il faut donc mesurer sur des textes français et arabes avant de lui faire confiance.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`RerankerLocal.__init__(nom)`** — Le constructeur installe dans l'atelier un vrai lecteur entraîné, à la place du jouet : il reçoit le nom d'un modèle cross-encodeur, par défaut un petit modèle MiniLM entraîné sur des requêtes web, le charge avec la classe `CrossEncoder` de sentence-transformers en fixant une longueur maximale de 512 jetons, au-delà de laquelle chaque paire est tronquée, et le range dans l'attribut `modele`. Il ne renvoie rien ; ce bloc est un extrait que le harnais n'exécute pas, puisqu'il demande une bibliothèque externe et le téléchargement du modèle.

**`RerankerLocal.scorer(question, textes)`** — Cette méthode fait lire au modèle chaque paire (question, passage), comme un examinateur qui corrige toute une pile de copies d'un même sujet : elle reçoit la question et une liste de textes, forme une paire avec chacun d'eux, envoie ces paires au modèle par lots de 16 grâce à `predict`, et renvoie la liste des scores convertis en `float` ordinaires, un par texte. Elle travaille donc sur une liste entière de candidats à la fois, alors que `cross_encodeur_jouet` et la fonction `reclasser` du programme manipulent un seul texte par appel : pour la brancher telle quelle dans `pipeline`, il faudrait l'appeler sur une liste d'un seul élément ou adapter `reclasser`.

```python
# [extrait] — adaptateur pour un cross-encodeur local (pip install sentence-transformers), non exécuté par le harnais
from sentence_transformers import CrossEncoder


class RerankerLocal:
    """Même port que cross_encodeur_jouet : un score par paire (question, texte)."""

    def __init__(self, nom: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.modele = CrossEncoder(nom, max_length=512)     # au-delà, le passage est tronqué

    def scorer(self, question: str, textes: list[str]) -> list[float]:
        paires = [(question, t) for t in textes]
        return [float(s) for s in self.modele.predict(paires, batch_size=16)]
```

Pour rester indépendant d'un fournisseur, on peut aussi partir d'une feuille blanche : les traits du jouet deviennent les entrées d'une régression logistique, dont les poids sont appris sur quelques centaines de paires (question, passage, étiquette) annotées par le métier, puis on remplace les traits par un petit encodeur quand le volume d'annotations le permet. Le port reste le même, et le jeu d'évaluation de ce fichier départage les adaptateurs.

## Squelette algorithmique

Le premier algorithme est le pipeline en deux étapes : en entrée, une question, le corpus, N et k ; en sortie, les k passages qui entrent dans le prompt. Le second choisit N : il prend le plus petit N qui atteint l'objectif de rappel de l'étape 1, à condition qu'il tienne dans le budget de latence.

```text
ALGORITHME RerankingDeuxÉtapes
ENTRÉES : question q, corpus 𝒟, score bon marché s₁, reranker s₂, N, k (k ≤ N)
SORTIE  : liste finale L de k documents au plus

  scores ← liste vide
  POUR CHAQUE d DE 𝒟 FAIRE
      SI s₁(q, d) > 0 ALORS ajouter (d, s₁(q, d)) à scores
  FIN POUR
  C ← les N premiers de scores, triés par s₁ décroissant (égalités : identifiant)
  POUR CHAQUE d DE C FAIRE
      v[d] ← s₂(q, d)                           (un passage du modèle par candidat)
  FIN POUR
  L ← C trié par v décroissant (tri stable : à égalité, l'ordre de l'étape 1)
  RETOURNER les k premiers de L                  (toujours L ⊆ C)

ALGORITHME ChoisirN
ENTRÉES : jeu de questions annotées, objectif de rappel ρ, budget T_budget, B, t_lot, T₁
SORTIE  : N, ou « impossible »

  N_max ← B × ⌊(T_budget − T₁) / t_lot⌋
  POUR N DE 1 À N_max FAIRE
      SI Recall@N moyen de l'étape 1 ≥ ρ ALORS RETOURNER N
  FIN POUR
  RETOURNER « impossible : améliorer l'étape 1 ou le budget »
```

**Complexité.** L'étape 1 coûte O(|𝒟| · |q|) avec la fonction BM25 naïve du parcours, qui parcourt tous les documents ; un index inversé ou un index approché la ramène à une fraction du corpus. Le tri des candidats coûte O(|𝒟| log |𝒟|) ici, O(|𝒟| log N) avec un tas. L'étape 2 coûte N passages du modèle, soit ⌈N/B⌉ lots, et un tri en O(N log N) ; la mémoire est O(N). Le point qui compte : le coût du reranker ne dépend que de N, pas de la taille du corpus. `ChoisirN` évalue au plus N_max rappels moyens, chacun en O(Q) pour Q questions si les classements de l'étape 1 sont calculés une fois.

**Du squelette au code.** La première boucle et la coupe à N sont `etape1`, la boucle sur les candidats et le tri stable sont `reclasser`, l'ensemble est `pipeline`. Le score s₂ est `cross_encodeur_jouet`, ou n'importe quel adaptateur de même signature (`oracle`, `biais_longueur`, `RerankerLocal`). La formule de N_max est `n_max`, la latence d'un N donné `latence_ms`, et le test « Recall@N ≥ ρ » s'écrit avec `recall_at_k`, comme la fonction `plus_petit_k` de l'étape 25.

## Cas d'usage réels aux Émirats

Les tailles N et k, les latences, les volumes et les gains ci-dessous sont illustratifs ; seuls les chiffres réglementaires reprennent la liste vérifiée du parcours.

### Banque — le plafond du retraité remonté en tête

Une banque de détail de Dubaï a branché un assistant sur sa politique de crédit, découpée en environ 8 000 morceaux : règles d'endettement, prêts personnels, hypothèques, Murabaha et Ijara, pièces du dossier KYC. L'étape 1 fusionne BM25 et un bi-encodeur par RRF et garde N = 50 candidats ; un cross-encodeur en garde k = 4. Sur la question « quel ratio d'endettement maximal pour un client retraité ? », BM25 seul place la FAQ générale et la règle générale avant la règle des retraités, exactement comme la question Q1 de ce fichier, où le NDCG@3 passe de 0,5463 à 0,8657 après reranking. L'agent cite alors la bonne règle : le total des mensualités, nouvelle mensualité comprise, ne dépasse pas 30 % du revenu pour un retraité, contre 50 % dans le cas général, selon les règles de la CBUAE. Sans reranking, le premier passage lu par le modèle est la règle des 50 %, et l'agent risque de l'appliquer à un retraité, ce qui reviendrait à accepter un dossier que la règle interdit. L'équipe mesure aussi le plafond de l'oracle : sur son jeu de 400 questions annotées, il révèle une vingtaine de questions dont la bonne règle n'est jamais parmi les 50 candidats, et c'est l'étape 1 qu'elle corrige pour celles-là, pas le reranker. En production, on suit le NDCG@4 par famille de produits et la part des réponses « retraité » qui citent la règle des 30 %.

### Assurance — la clause d'exclusion qui change la décision

Un assureur auto et santé instruit les sinistres avec un agent qui lit les clauses du contrat de l'assuré. Pour « dégâts des eaux dans le moteur après une traversée de rue inondée », BM25 ramène surtout la garantie « catastrophes naturelles », riche en mots communs, alors que la clause décisive est une exclusion pour conduite volontaire dans une zone inondée, rédigée avec un vocabulaire différent. Le cross-encodeur, qui lit la question et la clause ensemble, remonte l'exclusion du 9ᵉ au 2ᵉ rang ; avec k = 3, elle entre dans le contexte et l'agent propose au gestionnaire un refus motivé au lieu d'une indemnisation. Sans reranking, l'agent conclut à la couverture sur la foi de la garantie générale, et l'erreur coûte une indemnisation indue ou, à l'inverse, un litige si un gestionnaire la corrige tard. L'assurance est supervisée par la CBUAE, et chaque décision doit être justifiée par la clause applicable, d'où l'obligation de citer l'exclusion elle-même. L'équipe ne laisse jamais le reranker décider seul : un refus part toujours en revue humaine. On suit le NDCG@3 sur 300 sinistres annotés et la part des refus dont la clause citée est confirmée par le gestionnaire.

### Immobilier — des nombres que seul un modèle de paire rapproche

Une agence qui opère à Dubaï et à Abu Dhabi fait répondre un agent aux acheteurs à partir de ses fiches d'annonces et de ses fiches de procédure. Pour « deux chambres d'environ 1 100 sqft à JVC sous 1,2 million d'AED », le bi-encodeur ramène des fiches proches par le sens, mais il écrase les nombres dans un vecteur et confond volontiers un deux-chambres de 1 100 sqft avec un trois-chambres de 1 600 sqft. Le reranker, comme le trait « nombres » du jouet sur la question Q6, compare les nombres de la question à ceux de chaque fiche : sur 40 candidats, il garde les 5 fiches dont la surface, le nombre de chambres et le prix tombent dans les bornes. L'agent ajoute au prix de chaque bien les frais de transfert du DLD, 4 % de la valeur, soit 48 000 AED pour 1 200 000 AED, afin que l'acheteur compare des coûts complets. Sans reranking, l'agent propose des biens hors budget et l'acheteur cesse de répondre. On suit le taux de visites programmées après une proposition et le NDCG@5 sur des demandes annotées par les agents.

### RH — un régime voisin qui ressemble trop au bon

Un cabinet RH présent dans plusieurs émirats répond aux questions des salariés sur leur indemnité de fin de service. Les règles du secteur privé fédéral (décret-loi fédéral 33/2021 : 21 jours de salaire de base par année pour les cinq premières années, 30 jours au-delà, plafond de 24 mois) et celles du DIFC, qui a son propre régime d'épargne, partagent presque tout leur vocabulaire. Pour un salarié dont le dossier indique le DIFC, BM25 classe la règle fédérale en tête ; le reranker reçoit la question enrichie du régime et pénalise les passages de l'autre régime, comme le trait de conflit du jouet sur la question Q5. L'agent cite alors la règle du DIFC et ne calcule pas une indemnité fédérale qui ne s'applique pas. La leçon de la question Q2 s'applique aussi : un salarié qui demande « est-ce que la règle des 21 jours s'applique au DIFC ? » attend la règle du DIFC, alors même qu'il nomme le régime fédéral ; l'équipe a ajouté ce type de question à son jeu d'évaluation après une régression observée. Toute réponse reste à confirmer avec le texte en vigueur avant un versement. On suit le NDCG@3 par régime et la part des réponses qui citent une règle d'un autre régime, avec un objectif de zéro.

### BTP — la clause du bon lot

Un groupe de construction qui mène de grands chantiers à Dubaï fait contrôler les factures de ses sous-traitants par un agent qui lit la clause de retenue de garantie du contrat concerné. Les contrats de sous-traitance des différents lots sont presque identiques, et BM25 renvoie souvent la clause d'un lot voisin en tête. Le reranker reçoit la question avec l'identifiant du lot et le numéro de contrat, et il vérifie la présence exacte de ces identifiants dans la clause, à la manière des traits « nombres » et « entités » du jouet : sur 30 candidats, la clause du bon lot remonte au premier rang. L'agent applique alors la bonne retenue et calcule la TVA de 5 % sur le montant net facturé. Sans reranking, une retenue mal appliquée fausse le versement et la régularisation coûte plus cher qu'une revue préalable. Le budget de latence est large, puisque le contrôle se fait en lot pendant la nuit : l'équipe prend N = 100, et la latence de 195 ms par facture dans le modèle du point 5 ne gêne personne. On suit la part des factures dont la clause citée appartient au bon lot.

### Secteur public — choisir N sous un budget de latence

Une entité de services publics en ligne, accessible par UAE Pass, répond en arabe et en anglais sur ses démarches, avec une exigence de réponse rapide affichée à l'usager. L'équipe s'est fixé un budget de 150 ms pour la recherche ; avec 20 ms pour l'étape 1, des lots de 16 paires et 25 ms par lot, la formule du point 5 donne N_max = 80. Sur son jeu d'évaluation, le Recall@N de l'étape 1 atteint l'objectif de 0,95 dès N = 64, que l'équipe retient ; la latence vaut alors 20 + 4 × 25 = 120 ms. Le score calibré du cross-encodeur sert aussi de seuil d'abstention : si le meilleur passage est sous le seuil, l'agent renvoie vers la page de contact au lieu d'improviser une procédure. Le modèle de reranking choisi est multilingue, et le NDCG est mesuré séparément en arabe et en anglais, parce qu'un modèle entraîné surtout sur l'anglais peut dégrader l'arabe sans que la moyenne le montre. Pour respecter la PDPL, les journaux gardent les identifiants des passages et leurs scores, pas le texte libre saisi par l'usager. On suit la latence au 95ᵉ percentile, le NDCG@3 par langue et le taux d'abstention.

## Pièges et limites

- **Attendre du reranker qu'il rattrape l'étape 1.** Il ne trie que les candidats qu'on lui donne (point 1) ; on mesure le rappel de l'étape 1 et le plafond de l'oracle avant de régler le reranker.
- **Juger sur la moyenne.** Le jouet gagne 0,0287 de NDCG moyen tout en cassant Q2 ; le MRR ne voit même pas la régression (point 3). On lit les résultats par question et avec une métrique graduée.
- **Oublier la longueur maximale d'entrée.** Un cross-encodeur de la famille BERT lit souvent 512 tokens au plus : un passage plus long est tronqué en silence, et la phrase décisive peut tomber dans la partie coupée. Le découpage (étape 30 quater) doit en tenir compte.
- **Poser un seuil sur un score non calibré.** Un logit ou une sigmoïde non calibrée ne sont pas des probabilités (point 7) ; le seuil se règle sur des données du domaine.
- **Brancher un modèle entraîné ailleurs.** Un reranker entraîné sur des requêtes web anglaises peut se comporter comme `biais_longueur` sur des règlements en français ou en arabe : on le mesure sur son propre jeu annoté avant de le déployer.

### Exercice feuille blanche

1. Sans regarder le code, écrire `traits` et `cross_encodeur_jouet` à partir de l'équation du jouet, puis retrouver s₂ = 0,85 pour `faq-dbr` et s₂ = 2,15 pour `dbr-retraite` sur la question Q1.
2. Prédire, puis vérifier : sur Q1 avec N = 3, quelle liste renvoie le jouet, et quel est son Recall@3 ? (Réponse : les trois candidats sont `faq-dbr`, `dbr-general` et `dbr-retraite`, la liste finale est la même qu'avec N = 5, et le Recall@3 reste 0,5.) Que vaut la latence pour N = 64 avec les paramètres du point 5 ? (Réponse : 20 + 4 × 25 = 120 ms.)
3. Trouver le bug : `return sorted(candidats, key=lambda d: scorer(question, CORPUS[d]))`, sans le signe moins. Que devient le NDCG@3 de Q1 ? (Réponse : la liste devient `pp-plafond`, `carte-frais`, `dbr-general`, de notes [0, 0, 1], et le NDCG@3 tombe à 0,5/9,3928 ≈ 0,0532.)

## Pour aller plus loin

- **monoBERT** (Nogueira et Cho, 2019) a popularisé le cross-encodeur BERT comme reranker de passages ; **ColBERT** (Khattab et Zaharia, 2020) est un compromis à « interaction tardive » : les vecteurs de chaque token du document sont précalculés, et le score de la paire est une somme de maxima de produits scalaires, moins cher qu'un cross-encodeur et plus fin qu'un bi-encodeur.
- **Un LLM comme reranker** : on peut demander à un modèle de langage de classer une liste de passages (approche dite listwise, par exemple RankGPT, Sun et al., 2023). C'est plus cher par requête, et il faut surveiller les biais de position, mais cela se branche sur le même port.
- **Apprentissage du classement** : les méthodes qui optimisent directement le NDCG, comme LambdaMART, servent à apprendre les poids d'un reranker à traits, la version sérieuse du jouet de ce fichier.

> Étape 30 bis du parcours · Prérequis : [Applications du RAG par domaine](<30-RAG-Applications-Domaines.md>) · Suite : [Transformations de requête](<30c-RAG-Transformations-de-Requete.md>)
