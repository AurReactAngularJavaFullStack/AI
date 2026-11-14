# 13 — Rappel : démonstrations

> Fiche : [13 — Rappel](<../../Images/04-Recherche/13_rappel.md>) · Image : `13_rappel.jpg` · Leçon : [Étape 25 — Recall@k](<../../05-RAG/25-RAG-Formule-Recall-at-k.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
\text{Rappel} = \frac{VP}{VP + FN}
$$

VP compte les éléments pertinents que le système a trouvés, FN (faux négatifs) ceux qu'il a manqués. Le rappel répond à : « parmi tout ce qu'il fallait trouver, quelle part ai-je trouvée ? »

## Les symboles, un par un

$$
VP
$$

Nombre de vrais positifs : éléments pertinents que le système a trouvés (clauses retrouvées, fraudes signalées). Entier ≥ 0. Variable Python : `vp`.

$$
FN
$$

Nombre de faux négatifs : éléments pertinents que le système a manqués. Entier ≥ 0. Variable Python : `fn`.

$$
\lvert \text{Rel} \rvert = VP + FN
$$

Nombre total d'éléments pertinents, fixé par la vérité terrain (l'étiquetage d'un expert), et non par le système. Entier ≥ 0 ; s'il vaut 0, le rappel n'existe pas. Variable Python : `len(pertinents)`.

$$
\text{Rappel}
$$

Part des pertinents que le système a trouvés. Réel dans [0 ; 1], ou indéfini (`None`) quand rien n'était à trouver. Variable Python : la valeur renvoyée par `rappel(vp, fn)` ou `recall_at_k(retrouves, pertinents, k)`.

$$
k
$$

Nombre de résultats regardés en tête du classement (top-k). Entier ≥ 1. Variable Python : `k`.

$$
\text{Top}_k
$$

Ensemble des k premiers résultats renvoyés par le moteur. Ensemble d'au plus k éléments. Variable Python : `set(retrouves[:k])`.

$$
r_1, \quad r_2
$$

Rappels de deux moteurs (par exemple un moteur sémantique et BM25) sur la même question. Réels dans [0 ; 1]. Variables Python : `r1`, `r2`.

$$
c
$$

Nombre de pertinents trouvés par les deux moteurs à la fois (le recouvrement). Entier entre 0 et min(VP₁, VP₂). Variable Python : `commun`.

$$
Q^{+}
$$

Questions d'un jeu d'évaluation qui ont au moins un pertinent : les seules dont le rappel est défini. Variable Python : `definies` dans `recall_moyen`.

## Le mécanisme, avant les preuves

La formule reçoit deux comptages, VP et FN, qui se partagent un seul ensemble : celui des éléments pertinents. Leur somme VP + FN reconstitue donc |Rel|, la taille de ce qu'il fallait trouver, et ce nombre est fixé par la question et par son étiquetage, jamais par le système. La division transforme le nombre de trouvés en part de couverture : 7 trouvés sur 10 ou 70 sur 100 donnent le même 0,7. On divise par ce qu'il fallait trouver, et non par ce qui a été renvoyé, parce que la question posée est « qu'est-ce qui manque ? » : un passage absent du contexte n'arrivera jamais au modèle, qui répondra sans lui. Comme le dénominateur ne dépend pas du système, renvoyer plus ne peut que faire monter le rappel : c'est la source de sa monotonie (démonstration 3) et de son piège, puisque renvoyer tout le corpus donne un rappel de 1. Les éléments non pertinents, renvoyés ou non, n'apparaissent nulle part dans la formule : le rappel est aveugle au bruit, que seule la précision (fiche 12) mesure. Une différence comme VP − FN ne conviendrait pas, parce qu'elle dépend du nombre de pertinents de chaque question et ne se compare pas d'une question à l'autre.

Petit film chiffré. La fiche : 10 passages pertinents, 7 dans le top-10, donc VP = 7, FN = 3, somme 10, division 7/10 = 0,7. Une question de conformité à 8 clauses : un moteur en trouve 5, FN = 3, somme 8, division 5/8 = 0,625 ; un second moteur en trouve 4, rappel 4/8 = 0,5 ; l'union des deux en trouve 7, FN = 1, rappel 7/8 = 0,875, et le dénominateur n'a pas bougé. Un détecteur de fraude qui en signale 230 sur 250 : FN = 20, rappel 230/250 = 0,92 ; si l'on ajoute 10 000 dossiers honnêtes au flux, ni VP ni FN ne changent, et le rappel reste 0,92. En Java, c'est la couverture d'une suite de tests : la part des exigences effectivement testées parmi celles du cahier des charges, qui ne dit rien des tests inutiles.

## Démonstration 1 — Une proportion fixée par la vérité terrain, et sa version top-k

**Ce qu'on démontre.** Pour VP ≥ 0 et FN ≥ 0 avec |Rel| = VP + FN ≥ 1 :

$$
0 \le \frac{VP}{VP + FN} \le 1
$$

avec 1 si et seulement si FN = 0, et 0 si et seulement si VP = 0. Pour un moteur qui renvoie un classement, la version top-k s'écrit, avec VP = |Rel ∩ Topₖ| :

$$
\operatorname{Recall@}k = \frac{\lvert \text{Top}_k \cap \text{Rel} \rvert}{\lvert \text{Rel} \rvert}
$$

Si |Rel| = 0, le rappel n'est pas défini : la fonction renvoie None et la question sort des moyennes.

**L'idée.** VP compte une partie des pertinents, |Rel| les compte tous ; une partie ne dépasse jamais le tout. Dans un top-k, les pertinents trouvés sont exactement ceux qui appartiennent aux deux ensembles.

**La preuve, pas à pas.**

**Étape 1.** Parce que FN ≥ 0, on a 0 ≤ VP ≤ VP + FN. On divise par VP + FN > 0, ce qui conserve les inégalités :

$$
0 \le \frac{VP}{VP + FN} \le 1
$$

**Étape 2.** L'égalité à 1 a lieu quand VP = VP + FN, donc FN = 0 : rien n'a été manqué. L'égalité à 0 a lieu quand VP = 0 : rien n'a été trouvé.

**Étape 3.** Dans un top-k, un pertinent est trouvé s'il figure dans Topₖ : VP compte donc les éléments de Topₖ ∩ Rel, et FN ceux de Rel qui n'y figurent pas. Leur somme vaut |Rel|, parce que chaque pertinent est soit dans le top-k, soit hors du top-k, jamais les deux.

**Étape 4.** Si |Rel| = 0, il faudrait calculer 0/0. Donner 0 accuserait le moteur d'avoir raté ce qui n'existait pas ; donner 1 le féliciterait de rien. On renvoie donc None. ∎

**Vérification chiffrée.** Pour 7 trouvés sur 10 pertinents, 7/10 = 0,7. Pour 8 clauses pertinentes dont 5 trouvées, 5/8 = 0,625. Une question sans pertinent donne None. Contre-exemple à l'ancienne convention « 0 quand rien n'est pertinent » : sur quatre questions de rappels 0,5, 1, 0 et une sans pertinent, la moyenne correcte sur trois questions vaut 0,5, mais la convention 0 donne 0,375 (démonstration 6).

**Ce que la preuve révèle du mécanisme.** Le rappel ne regarde que la ligne « réel positif » de la matrice de confusion : VP et FN. Son dénominateur est une propriété de la question, pas du moteur, ce qui permet de comparer deux moteurs sur la même question sans ambiguïté.

**Conséquence pour un agent.** On ne mesure le rappel que sur des questions étiquetées, et l'on publie à part le nombre de questions sans pertinent : ce sont les tests d'abstention, où l'agent doit répondre « je ne sais pas ».

## Démonstration 2 — Une probabilité conditionnelle, qui ne dépend pas du taux de base

**Ce qu'on démontre.** Si l'on tire au hasard un élément pertinent, la probabilité que le système l'ait renvoyé vaut le rappel :

$$
\text{Rappel} = P(\text{renvoyé} \mid \text{pertinent})
$$

Conséquence : ajouter au corpus des éléments non pertinents, renvoyés ou non, ne change pas le rappel. La précision, elle, vaut P(pertinent | renvoyé) et change.

**L'idée.** On conditionne sur la vérité (« pertinent »), pas sur la sortie du système. Tout ce qui se passe chez les non-pertinents est hors du champ de la mesure.

**La preuve, pas à pas.**

**Étape 1.** Par définition, P(renvoyé | pertinent) = P(renvoyé et pertinent) / P(pertinent). Sur N éléments, ces probabilités sont des fréquences :

$$
P(\text{renvoyé} \mid \text{pertinent}) = \frac{VP / N}{(VP + FN) / N} = \frac{VP}{VP + FN}
$$

parce que N se simplifie.

**Étape 2.** Ajouter des non-pertinents change N et peut changer FP (s'ils sont renvoyés), mais ne change ni VP ni FN, qui ne comptent que des pertinents. Le rappel est donc inchangé.

**Étape 3.** La précision VP/(VP + FP) contient FP : si des non-pertinents ajoutés sont renvoyés, elle baisse. ∎

**Vérification chiffrée.** Fiche : top-10 avec 7 pertinents, 3 non pertinents, 10 pertinents au total. Rappel 7/10 = 0,7 et précision 7/10 = 0,7. On ajoute 1 000 documents hors sujet au corpus, dont 50 remontent dans les résultats : le rappel reste 7/10 = 0,7, la précision tombe à 7/(7 + 3 + 50) = 7/60 ≈ 0,11667.

**Ce que la preuve révèle du mécanisme.** Rappel et précision conditionnent dans des sens opposés : l'un part de la vérité, l'autre de la sortie. C'est pourquoi le rappel est stable quand le taux de base change, alors que la précision s'effondre sur un événement rare (fiche 12, démonstration 2).

**Conséquence pour un agent.** Un jeu d'évaluation du rappel n'a pas besoin de reproduire la proportion réelle d'éléments non pertinents : il suffit d'avoir bien étiqueté les pertinents. En revanche, on ne déduit jamais la précision en production d'un rappel mesuré sur un jeu de test.

## Démonstration 3 — Le rappel ne baisse jamais quand k augmente

**Ce qu'on démontre.** Pour un même classement, coupé à k puis à k + 1 :

$$
\operatorname{Recall@}k \le \operatorname{Recall@}(k+1)
$$

avec une hausse stricte si et seulement si le document de rang k + 1 est pertinent (et distinct des précédents). Hypothèse : une seule liste, coupée à différents k.

**L'idée.** Passer de k à k + 1 ajoute un document sans en retirer aucun. Le numérateur ne peut que grandir, le dénominateur ne bouge pas.

**La preuve, pas à pas.**

**Étape 1.** Le top-(k + 1) contient le top-k, parce qu'on coupe la même liste un rang plus loin :

$$
\text{Top}_k \subseteq \text{Top}_{k+1}
$$

**Étape 2.** L'intersection avec un même ensemble Rel conserve l'inclusion, parce qu'un pertinent présent dans Topₖ est aussi présent dans Topₖ₊₁ ; une partie d'un ensemble fini a au plus autant d'éléments que lui :

$$
\lvert \text{Rel} \cap \text{Top}_k \rvert \le \lvert \text{Rel} \cap \text{Top}_{k+1} \rvert
$$

**Étape 3.** On divise par |Rel| > 0, ce qui conserve l'inégalité. L'écart entre les deux numérateurs vaut 1 si le document ajouté est pertinent et nouveau, 0 sinon. ∎

**Vérification chiffrée.** Exemple de l'étape 25 : Rel = {d1, d2, d4, d6} et le classement d3, d7, d1, d9, d4, d2, d8, d6, d5, d10. Pour k = 1 à 10, le rappel vaut 0 ; 0 ; 0,25 ; 0,25 ; 0,5 ; 0,75 ; 0,75 ; 1 ; 1 ; 1 : il ne baisse jamais, et il monte exactement aux rangs 3, 5, 6 et 8, ceux des pertinents. Contre-exemple quand l'hypothèse « une seule liste » manque : un index approché renvoie [d1, d4, x, y, z] à une requête k = 5 (rappel 2/4 = 0,5), puis [x, d4, y, z, w, v] à une requête séparée k = 6 (rappel 1/4 = 0,25). Le « rappel » a baissé parce qu'on compare deux listes différentes.

**Ce que la preuve révèle du mécanisme.** Le rappel en fonction de k est une courbe en escalier qui monte d'une marche de 1/|Rel| à chaque pertinent rencontré. Plus |Rel| est grand, plus les marches sont petites.

**Conséquence pour un agent.** Pour choisir k, on cherche le plus petit k qui atteint l'objectif de rappel : par monotonie, tout k plus grand l'atteint aussi, mais coûte plus de tokens. On mesure toujours la courbe sur une seule liste longue, coupée à différents k.

## Démonstration 4 — Un plafond qui dépend de k

**Ce qu'on démontre.** Pour tout k ≥ 1 et |Rel| ≥ 1 :

$$
\operatorname{Recall@}k \le \min\left(1, \frac{k}{\lvert \text{Rel} \rvert}\right)
$$

et un classement parfait, qui place tous les pertinents en tête, atteint ce plafond.

**L'idée.** Un top-k ne contient que k places : il ne peut pas contenir plus de k pertinents, même si la question en a davantage.

**La preuve, pas à pas.**

**Étape 1.** Le numérateur compte des documents à la fois dans Rel et dans Topₖ, donc au plus |Rel| et au plus |Topₖ| ≤ k :

$$
\lvert \text{Rel} \cap \text{Top}_k \rvert \le \min\left(\lvert \text{Rel} \rvert, k\right)
$$

**Étape 2.** On divise par |Rel| > 0 :

$$
\operatorname{Recall@}k \le \frac{\min\left(\lvert \text{Rel} \rvert, k\right)}{\lvert \text{Rel} \rvert} = \min\left(1, \frac{k}{\lvert \text{Rel} \rvert}\right)
$$

**Étape 3.** Un classement parfait met min(k, |Rel|) pertinents dans ses k premières places, donc atteint l'égalité. ∎

**Vérification chiffrée.** Une question à 8 clauses pertinentes ne dépasse pas 5/8 = 0,625 avec un top-5, même parfait. Une question à 12 passages pertinents a pour plafond min(1 ; 10/12) ≈ 0,833 avec un top-10 : un rappel mesuré de 6/12 = 0,5 représente 0,5/0,833 = 60 % de ce qui était atteignable. Contre-exemple de lecture : comparer le 0,5 de cette question au 0,5 d'une question à 4 pertinents (plafond 1) revient à comparer deux échelles différentes.

**Ce que la preuve révèle du mécanisme.** Le plafond vaut 1 dès que k ≥ |Rel| ; en dessous, il décroît comme k/|Rel|. Le rappel à petit k est donc d'abord limité par la question, pas par le moteur.

**Conséquence pour un agent.** On publie le rappel à côté de son plafond, ou divisé par lui, et l'on choisit k au moins égal au nombre typique de pertinents des questions du métier.

## Démonstration 5 — Deux moteurs : l'union, ses bornes et le cas indépendant

**Ce qu'on démontre.** Deux moteurs trouvent VP₁ et VP₂ pertinents (rappels r₁ et r₂), dont c en commun. Le rappel de leur union vaut

$$
R_{\cup} = r_1 + r_2 - \frac{c}{\lvert \text{Rel} \rvert}
$$

et vérifie toujours

$$
\max(r_1, r_2) \le R_{\cup} \le \min(1, r_1 + r_2)
$$

Si, de plus, chaque pertinent est manqué par le moteur 1 avec probabilité 1 − r₁ et par le moteur 2 avec probabilité 1 − r₂, indépendamment, alors en moyenne :

$$
R_{\cup} = 1 - (1 - r_1)(1 - r_2), \qquad c = r_1\, r_2\, \lvert \text{Rel} \rvert
$$

**L'idée.** L'union trouve tout ce que trouve l'un ou l'autre ; on ne compte qu'une fois ce qu'ils trouvent tous les deux. Un pertinent n'est perdu par l'union que s'il est perdu par les deux moteurs.

**La preuve, pas à pas.**

**Étape 1.** Par inclusion-exclusion, le nombre de pertinents trouvés par l'union vaut VP₁ + VP₂ − c, parce que les c pertinents communs sont comptés deux fois dans la somme. On divise par |Rel| :

$$
R_{\cup} = \frac{VP_1 + VP_2 - c}{\lvert \text{Rel} \rvert} = r_1 + r_2 - \frac{c}{\lvert \text{Rel} \rvert}
$$

**Étape 2.** Parce que c ≤ VP₂, on a VP₁ + VP₂ − c ≥ VP₁, donc R∪ ≥ r₁ ; de même R∪ ≥ r₂. Parce que c ≥ 0, R∪ ≤ r₁ + r₂ ; et R∪ ≤ 1 par la démonstration 1.

**Étape 3.** Sous l'hypothèse d'indépendance, la probabilité qu'un pertinent soit manqué par les deux vaut le produit des probabilités, (1 − r₁)(1 − r₂). Il est trouvé par l'union dans le cas contraire, d'où 1 − (1 − r₁)(1 − r₂).

**Étape 4.** De même, il est trouvé par les deux avec probabilité r₁ r₂, et sur |Rel| pertinents on attend c = r₁ r₂ |Rel| communs. ∎

**Vérification chiffrée.** 8 clauses pertinentes ; le moteur sémantique en trouve 5 (r₁ = 0,625), BM25 en trouve 4 (r₂ = 0,5), dont c = 2 en commun. Union : 0,625 + 0,5 − 2/8 = 0,875, soit 7 clauses. Bornes : 0,625 ≤ 0,875 ≤ min(1 ; 1,125) = 1. L'indépendance prévoyait 1 − 0,375 × 0,5 = 0,8125 et un recouvrement de 8 × 0,625 × 0,5 = 2,5 : le recouvrement réel, 2, est plus petit, donc l'union fait mieux que prévu. Contre-exemple : si les 4 clauses de BM25 étaient toutes parmi les 5 du moteur sémantique (c = 4), l'union vaudrait 0,625 + 0,5 − 0,5 = 0,625, la borne basse : l'union n'apporte rien.

**Ce que la preuve révèle du mécanisme.** Tout se joue sur le recouvrement c : moins les deux moteurs ratent les mêmes choses, plus l'union gagne. L'indépendance est un point de référence ; des moteurs de natures différentes (lexical et sémantique) font souvent mieux, deux variantes du même modèle d'embeddings souvent moins bien.

**Conséquence pour un agent.** C'est l'argument de la recherche hybride (fiche 25) : on combine des moteurs qui se trompent différemment, et l'on mesure leur recouvrement réel avant de payer un second index.

## Démonstration 6 — Moyenner sur un jeu de questions : exclure les None, choisir macro ou micro

**Ce qu'on démontre.** Sur un jeu de questions, le rappel moyen macro est la moyenne des rappels des seules questions de Q⁺ (celles qui ont au moins un pertinent). Le rappel micro divise le total des trouvés par le total des pertinents, et c'est une moyenne pondérée des rappels par question :

$$
R_{micro} = \frac{\sum_{q} VP_q}{\sum_{q} \lvert \text{Rel}_q \rvert} = \sum_{q \in Q^{+}} \frac{\lvert \text{Rel}_q \rvert}{\sum_{q'} \lvert \text{Rel}_{q'} \rvert} \, R_q
$$

**L'idée.** La macro donne une voix à chaque question, la micro une voix à chaque pertinent : une question à quatre pertinents pèse quatre fois plus qu'une question à un seul.

**La preuve, pas à pas.**

**Étape 1.** Une question sans pertinent a un rappel indéfini (démonstration 1) ; elle ne peut entrer ni au numérateur ni au dénominateur de la moyenne macro, qui porte donc sur Q⁺.

**Étape 2.** Pour la micro, on écrit VP(q) = |Rel(q)| × R(q), parce que R(q) = VP(q)/|Rel(q)|. Les questions sans pertinent ont VP = 0 et |Rel| = 0 : elles n'ajoutent rien en haut ni en bas.

**Étape 3.** On remplace dans le numérateur et l'on distribue la division : chaque R(q) est multiplié par la part |Rel(q)|/∑|Rel| de ses pertinents, des poids positifs de somme 1. ∎

**Vérification chiffrée.** Deux questions : l'une a 1 pertinent, trouvé (rappel 1), l'autre 4 pertinents dont 1 trouvé (rappel 0,25). Macro : (1 + 0,25)/2 = 0,625. Micro : (1 + 1)/(1 + 4) = 0,4, et par les poids (1/5) × 1 + (4/5) × 0,25 = 0,2 + 0,2 = 0,4. Pour les None : rappels 0,5, 1, 0 et une question sans pertinent donnent une macro de (0,5 + 1 + 0)/3 = 0,5 ; la convention « 0 » donne 1,5/4 = 0,375, la convention « 1 » donne 2,5/4 = 0,625 : un écart de 0,25 dû au seul choix arbitraire.

**Ce que la preuve révèle du mécanisme.** La micro est dominée par les questions à nombreux pertinents ; la macro par les questions à un ou deux pertinents, où un seul oubli fait perdre 0,5 ou 1. Les deux mesures ne répondent pas à la même question.

**Conséquence pour un agent.** On annonce toujours quelle moyenne on publie, avec le nombre de questions exclues ; la macro répond à « quelle part des questions est bien servie ? », la micro à « quelle part des preuves arrive dans le contexte ? ».

## Exemple simple, à la main

Pour une question, 10 passages sont pertinents. Le top-10 en contient 7. On compte VP = 7, puis FN = 10 − 7 = 3, puis le dénominateur VP + FN = 7 + 3 = 10 :

$$
\operatorname{Recall@}10 = \frac{7}{7 + 3} = \frac{7}{10} = 0{,}7
$$

Le plafond vaut min(1 ; 10/10) = 1 : un moteur parfait aurait pu tout ramener, donc 0,7 mesure bien un défaut du moteur. Les 3 passages manqués n'arriveront jamais au modèle, qui répondra sans eux. Si l'on regardait un top-5, le plafond tomberait à min(1 ; 5/10) = 0,5.

| Quantité | Calcul | Valeur |
| --- | --- | --- |
| VP | passages pertinents dans le top-10 | 7 |
| FN | 10 − 7 | 3 |
| pertinents au total | 7 + 3 | 10 |
| rappel | 7/10 | 0,7 |
| plafond pour k = 10 | min(1 ; 10/10) | 1 |
| plafond pour k = 5 | min(1 ; 5/10) | 0,5 |

## Cas d'usage complexes, démontrés

### Cas 1 — [BTP] Un groupe de construction : recherche hybride sur des contrats de sous-traitance

**Contexte.** Un groupe de construction travaille sur de grands chantiers à Dubaï ; ses gestionnaires interrogent un agent qui lit les contrats de sous-traitance avant d'approuver une facture. Pour la question « quelles clauses limitent ou retardent le paiement d'un sous-traitant ? », l'équipe juridique a étiqueté 8 clauses pertinentes : retenue de garantie, pénalités de retard, conditions de réception, TVA de 5 % à facturer, etc. La question : faut-il ajouter BM25 au moteur sémantique ? Les montants et taux contractuels sont illustratifs.

**Données.**

- clauses pertinentes : |Rel| = 8 ; top-10 du moteur sémantique : 5 trouvées ; top-10 de BM25 : 4 trouvées ; trouvées par les deux : c = 2 ;
- objectif de rappel de l'équipe : 0,85 ;
- contrat témoin : 3 000 000 AED hors taxes, TVA 5 %, retenue de garantie de 5 % du montant hors taxes (taux illustratif) ;
- hypothèse de risque : la clause manquée est l'une des 8, sans préférence.

**Calcul pas à pas.**

**Étape 1.** Les deux rappels :

$$
r_1 = \frac{5}{8} = 0{,}625, \qquad r_2 = \frac{4}{8} = 0{,}5
$$

**Étape 2.** Le rappel de l'union (démonstration 5) :

$$
R_{\cup} = 0{,}625 + 0{,}5 - \frac{2}{8} = 0{,}875 = \frac{7}{8}
$$

**Étape 3.** La prévision sous indépendance et le recouvrement attendu :

$$
1 - 0{,}375 \times 0{,}5 = 0{,}8125, \qquad 8 \times 0{,}625 \times 0{,}5 = 2{,}5
$$

**Étape 4.** L'enjeu de la retenue de garantie sur le contrat témoin, puis l'exposition moyenne si la clause manquée est tirée au hasard parmi les 8 :

$$
0{,}05 \times 3\,000\,000 = 150\,000 \text{ AED}, \qquad \frac{3}{8} \times 150\,000 = 56\,250 \text{ AED}, \qquad \frac{1}{8} \times 150\,000 = 18\,750 \text{ AED}
$$

avec le moteur sémantique seul (3 clauses manquées), puis avec l'union (1 clause manquée). Le montant TTC du contrat est 3 000 000 × 1,05 = 3 150 000 AED.

**Décision de l'agent.** L'union atteint 0,875 ≥ 0,85, chaque moteur seul échoue (0,625 et 0,5) : le groupe passe en recherche hybride, puis fusionne les deux listes (RRF, fiche 25) pour ne garder qu'un contexte raisonnable.

**Contre-calcul.** Le moteur sémantique seul laisse en moyenne 56 250 AED de retenue exposés par contrat de ce type, contre 18 750 AED avec l'union : 37 500 AED d'écart par contrat. Le coût, lui, est en contexte : les deux top-10 contiennent 20 passages dont 2 en double (les clauses communes), soit 18 passages distincts et une précision de 7/18 ≈ 0,38889 avant fusion. Additionner les rappels sans retirer le recouvrement donnerait 1,125, un nombre impossible.

**Sensibilité.** L'objectif 0,85 exige au moins 0,85 × 8 = 6,8, donc 7 clauses. Avec 5 + 4 trouvées, l'union atteint 9 − c clauses : c = 2 donne 7 (objectif atteint), c = 3 donne 6/8 = 0,75 (objectif manqué). La valeur de bascule est un recouvrement de 3 clauses : si les deux moteurs ratent davantage les mêmes clauses, l'hybride ne suffit plus et il faut revoir le découpage des contrats.

**En production.** On suit chaque mois le rappel de l'hybride au rang 10 sur les questions contractuelles étiquetées, avec une alerte sous 0,85, et le recouvrement c des deux moteurs. La TVA de 5 % est un fait du cours ; les taux de retenue et de pénalité dépendent de chaque contrat et sont à confirmer avec le contrat et le texte en vigueur.

### Cas 2 — [ASSUR] Un assureur auto et santé : combien vaut un point de rappel du détecteur de fraude

**Contexte.** Un assureur auto et santé fait signaler par un agent les déclarations de sinistre suspectes, que des gestionnaires examinent ensuite. Sur un mois, 250 fraudes sont confirmées a posteriori (audits, recoupements). L'équipe compare le seuil actuel A et un seuil plus bas B, qui signale davantage. Tous les montants et volumes sont illustratifs.

**Données.**

- fraudes du mois : |Rel| = 250 ; montant moyen d'une fraude non détectée : 1 500 AED ; coût d'examen d'une alerte : 60 AED ;
- seuil A : VP = 230, FP = 70 ;
- seuil B : VP = 240, FP = 160.

**Calcul pas à pas.**

**Étape 1.** Les rappels et les fraudes manquées :

$$
R_A = \frac{230}{250} = 0{,}92 \;(FN = 20), \qquad R_B = \frac{240}{250} = 0{,}96 \;(FN = 10)
$$

**Étape 2.** La valeur d'un point de rappel : un point vaut 0,01 × 250 = 2,5 fraudes, soit 2,5 × 1 500 = 3 750 AED par mois.

**Étape 3.** Le coût total de chaque seuil, fraudes manquées plus examens :

$$
A : 20 \times 1\,500 + 300 \times 60 = 30\,000 + 18\,000 = 48\,000 \text{ AED}
$$

$$
B : 10 \times 1\,500 + 400 \times 60 = 15\,000 + 24\,000 = 39\,000 \text{ AED}
$$

**Étape 4.** Le bilan marginal de B : 100 alertes de plus (6 000 AED d'examen) pour 10 fraudes de plus attrapées (15 000 AED évités).

**Décision de l'agent.** Le seuil B coûte 9 000 AED de moins par mois : l'équipe l'adopte, en dimensionnant les gestionnaires pour 400 alertes au lieu de 300.

**Contre-calcul.** Jugé sur la précision, A semble meilleur : 230/300 ≈ 0,76667 contre 240/400 = 0,6. Choisir sur ce seul chiffre coûterait 9 000 AED par mois, soit 108 000 AED par an. Les 10 fraudes de plus attrapées par B valent 4 points de rappel, donc 4 × 3 750 = 15 000 AED.

**Sensibilité.** Les deux seuils coûtent autant quand 30 000 + 300 c = 15 000 + 400 c, où c est le coût d'examen d'une alerte, soit c = 150 AED : au-delà de 150 AED par examen, A redevient meilleur. Du côté des fraudes, l'égalité 10 m = 100 × 60 donne m = 600 AED : si le montant moyen d'une fraude passait sous 600 AED, le seuil A l'emporterait.

**En production.** L'indicateur est le rappel mensuel, calculé sur les fraudes confirmées avec un décalage (une fraude se découvre parfois des mois plus tard), et le coût total par mois. L'assurance est supervisée par la CBUAE ; les obligations de détection et de déclaration de la fraude sont à confirmer avec le texte en vigueur.

### Cas 3 — [RH] Un cabinet RH multi-émirats : retrouver toutes les règles de fin de service

**Contexte.** Un cabinet RH présent dans plusieurs émirats fait répondre un assistant aux salariés sur leur indemnité de fin de service. Avant la mise en production, l'équipe exige un rappel moyen macro au rang 5 d'au moins 0,9 sur un jeu de questions étiquetées. Le jeu d'essai contient quatre questions ; les salaires sont illustratifs.

**Données.**

| Question | Pertinents | Trouvés dans le top-5 |
| --- | --- | --- |
| q1 : expatrié du secteur privé, 8 ans de service | 3 (21 jours par an les 5 premières années ; 30 jours au-delà ; plafond de 24 mois) | 2 (la règle des 30 jours manque) |
| q2 : démission après 3 ans | 1 (pas de réduction en cas de démission) | 1 |
| q3 : salarié du DIFC | 2 (régime d'épargne DEWS ; exclusion du régime fédéral) | 1 |
| q4 : visa familial, non géré par le cabinet | 0 | — |

Salarié témoin de q1 : salaire de base 15 000 AED par mois, 8 ans de service continu.

**Calcul pas à pas.**

**Étape 1.** Les rappels par question : q1 = 2/3 ≈ 0,66667 ; q2 = 1/1 = 1 ; q3 = 1/2 = 0,5 ; q4 = None (aucun pertinent).

**Étape 2.** Les deux moyennes (démonstration 6), sur Q⁺ = {q1, q2, q3} :

$$
\text{macro} = \frac{0{,}66667 + 1 + 0{,}5}{3} \approx 0{,}72222, \qquad \text{micro} = \frac{2 + 1 + 1}{3 + 1 + 2} = \frac{4}{6} \approx 0{,}66667
$$

**Étape 3.** L'indemnité juste du salarié témoin, avec un salaire journalier de 15 000/30 = 500 AED :

$$
5 \times 21 \times 500 + 3 \times 30 \times 500 = 52\,500 + 45\,000 = 97\,500 \text{ AED}
$$

sous le plafond de 24 × 15 000 = 360 000 AED.

**Étape 4.** L'indemnité annoncée si la règle des 30 jours manque au contexte : 8 × 21 × 500 = 84 000 AED, soit 13 500 AED de moins que le dû.

**Décision de l'agent.** Le rappel macro de 0,72222 est sous l'objectif de 0,9 : pas de mise en production. L'équipe revoit le découpage (la règle des 30 jours était collée au plafond dans un morceau trop long) et augmente k, puis remesure.

**Contre-calcul.** La convention « 0 pour une question sans pertinent » donnerait (0,66667 + 1 + 0,5 + 0)/4 ≈ 0,54167 et accuserait le moteur pour q4, où il n'y avait rien à trouver. À l'inverse, une démonstration « réussie » sur la seule q2 (rappel 1) aurait masqué une erreur de 13 500 AED par salarié de 8 ans.

**Sensibilité.** Corriger q1 seule donnerait une macro de (1 + 1 + 0,5)/3 ≈ 0,83333, encore sous 0,9 : il faut corriger q1 **et** q3. Pour le salarié témoin, l'erreur due à la règle manquante vaut 9 jours de salaire par année au-delà de 5, soit 9 × 500 = 4 500 AED par an ; elle grandit jusqu'au plafond, atteint quand 105 + 30 (n − 5) = 720 jours, c'est-à-dire après n = 25,5 années de service.

**En production.** On suit le rappel macro au rang 5 par segment (secteur privé fédéral, DIFC, ressortissants émiriens relevant de la GPSSA), publié avec le nombre de questions exclues. Les règles citées (décret-loi fédéral 33/2021 : 21 puis 30 jours, salaire de base divisé par 30, plafond de 24 mois, pas de réduction en cas de démission ; régime DEWS au DIFC) sont des faits du cours ; chaque réponse reste à confirmer avec le texte en vigueur avant tout versement.

### Cas 4 — [CRYPTO] Une plateforme agréée VARA : le rappel du filtrage des noms translittérés

**Contexte.** Une plateforme d'actifs virtuels agréée par la VARA compare, à l'ouverture de compte, le nom de chaque client à une liste interne de personnes à surveiller. Les noms arabes s'écrivent de plusieurs façons en caractères latins (Mohammed, Muhammad, Mohamed) et en arabe (alef avec ou sans hamza, ta marbuta, diacritiques). L'équipe conformité a constitué un jeu de 40 correspondances connues, qui doivent toutes déclencher une alerte. Elle compare trois méthodes ; les volumes sont illustratifs.

**Données.**

- correspondances connues : |Rel| = 40 ;
- méthode A, égalité exacte : 22 trouvées, 25 alertes par jour ;
- méthode B, normalisation de l'arabe et des translittérations : 36 trouvées, 40 alertes par jour ;
- méthode C, B plus une distance d'édition ≤ 1 : 39 trouvées, 70 alertes par jour ;
- examen d'une alerte : 5 minutes ; capacité : 8 heures d'analyste par jour, soit 480 minutes ;
- règle interne : rappel ≥ 0,95 sur le jeu de correspondances connues.

**Calcul pas à pas.**

**Étape 1.** Les trois rappels :

$$
R_A = \frac{22}{40} = 0{,}55, \qquad R_B = \frac{36}{40} = 0{,}9, \qquad R_C = \frac{39}{40} = 0{,}975
$$

**Étape 2.** Les correspondances manquées : 40 − 22 = 18, 40 − 36 = 4, 40 − 39 = 1.

**Étape 3.** La charge quotidienne d'examen : 25 × 5 = 125 min, 40 × 5 = 200 min, 70 × 5 = 350 min.

**Étape 4.** La capacité maximale en alertes : 480/5 = 96 alertes par jour.

**Décision de l'agent.** Seule C atteint 0,95 (0,975), et sa charge de 350 minutes tient dans les 480 : la plateforme adopte C.

**Contre-calcul.** La méthode exacte paraît propre, avec peu d'alertes ; mais elle manque 18 correspondances sur 40, soit 45 % des personnes qu'il fallait signaler, parce que « Mohamed » ne s'écrit pas « Muhammad ». Juger les méthodes sur le nombre d'alertes ou sur la précision aurait fait choisir la pire pour la conformité.

**Sensibilité.** L'objectif 0,95 exige au moins 0,95 × 40 = 38 correspondances : C en trouve 39, une seule de marge ; à 37, la décision basculerait. Côté charge, la valeur de bascule est 96 alertes par jour : une hausse de 10 % du volume de C (77 alertes, 385 minutes) reste absorbable.

**En production.** On suit le rappel sur un jeu de correspondances connues, enrichi chaque mois de nouvelles variantes de translittération, avec une alerte sous 0,95, et la charge quotidienne, avec une alerte au-dessus de 96 alertes. La normalisation de l'arabe (alef, ta marbuta, diacritiques) est un fait du cours ; les obligations de filtrage KYC d'une plateforme agréée sont à confirmer avec le règlement VARA en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Une question a 12 passages pertinents. Le top-10 en contient 6. Calculer le rappel et son plafond pour k = 10.

**Exercice 2.** Deux moteurs ont des rappels 0,7 et 0,6, indépendants. Quel rappel pour leur union ?

**Exercice 3.** Démontrer que le rappel d'une union est au moins le plus grand des deux rappels.

**Exercice 4.** Un système renvoie tout le corpus. Que valent son rappel et sa précision ?

**Exercice 5.** Combien de fraudes sont manquées avec un rappel de 0,97 sur 250 ?

**Exercice 6 (cas modifié).** Dans le cas 2, l'examen d'une alerte coûte désormais 200 AED. Recalculer les coûts des seuils A et B et donner la décision.

**Exercice 7 (trouver l'erreur).** Un collègue écrit, pour le cas 1 : « le moteur sémantique a un rappel de 0,625 et BM25 de 0,5, donc l'hybride a un rappel de 0,625 + 0,5 = 1,125, arrondi à 1 : il trouve tout ». Trouver l'erreur et donner le vrai rappel.

**Exercice 8 (redémontrer de mémoire).** Redémontrer que Recall@k ≤ Recall@(k + 1) pour une même liste, puis donner un exemple chiffré où deux listes différentes semblent contredire cette propriété.

## Corrigé

**Exercice 1.** VP = 6 et |Rel| = 12, donc le rappel vaut 6/12 = 0,5. Plafond : min(1 ; 10/12) ≈ 0,833, parce qu'un top-10 ne peut pas contenir 12 pertinents. Rapporté à son plafond, le moteur atteint 0,5/0,833 = 60 % de ce qui était possible.

**Exercice 2.** Les oublis valent 1 − 0,7 = 0,3 et 1 − 0,6 = 0,4. Par indépendance, un pertinent est manqué par les deux avec probabilité 0,3 × 0,4 = 0,12, donc l'union a un rappel 1 − 0,12 = 0,88.

**Exercice 3.** L'union contient tout ce que trouve chaque moteur : l'ensemble des pertinents trouvés par l'union contient celui du moteur 1 et celui du moteur 2, donc VP∪ ≥ VP₁ et VP∪ ≥ VP₂. On divise par le même |Rel| > 0 : R∪ ≥ r₁ et R∪ ≥ r₂, donc R∪ ≥ max(r₁, r₂).

**Exercice 4.** Tous les pertinents sont renvoyés : FN = 0 et le rappel vaut 1. La précision vaut |Rel|/N, où N est la taille du corpus : par exemple 10/100 000 = 0,0001. Un rappel de 1 obtenu ainsi est inutile, le contexte est noyé.

**Exercice 5.** Les fraudes manquées valent 250 × (1 − 0,97) = 250 × 0,03 = 7,5 en moyenne, soit 7 ou 8 selon les mois.

**Exercice 6.** A : 20 × 1 500 + 300 × 200 = 30 000 + 60 000 = 90 000 AED. B : 10 × 1 500 + 400 × 200 = 15 000 + 80 000 = 95 000 AED. Avec un examen à 200 AED, au-dessus de la valeur de bascule de 150 AED, le seuil A devient le moins cher : on le garde, ou l'on réduit le coût d'examen avant de baisser le seuil.

**Exercice 7.** L'erreur est d'additionner les rappels sans retirer le recouvrement : les 2 clauses trouvées par les deux moteurs sont comptées deux fois. Par la démonstration 5, R∪ = 0,625 + 0,5 − 2/8 = 0,875 : l'hybride trouve 7 clauses sur 8, pas 8. Un rappel supérieur à 1 était déjà le signe d'une erreur.

**Exercice 8.** Le top-(k + 1) contient le top-k (même liste coupée plus loin), donc Rel ∩ Topₖ ⊆ Rel ∩ Topₖ₊₁, donc |Rel ∩ Topₖ| ≤ |Rel ∩ Topₖ₊₁| ; on divise par |Rel| > 0. Exemple de deux listes différentes : Rel = {d1, d2, d4, d6}, une requête k = 5 renvoie [d1, d4, x, y, z] (rappel 0,5), une requête séparée k = 6 renvoie [x, d4, y, z, w, v] (rappel 0,25). Ce n'est pas une contradiction : les deux listes ne sont pas le même classement.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`rappel(vp, fn)`** — Cette fonction est le garde-chasse qui compte, à la fin de la battue, combien d'animaux recensés on a réellement retrouvés : elle reçoit le nombre de vrais positifs et le nombre de faux négatifs, c'est-à-dire les pertinents trouvés et les pertinents oubliés, lève une `ValueError` si l'un des deux compteurs est négatif, renvoie `None` quand il n'y avait rien à trouver, et sinon renvoie VP / (VP + FN), un nombre entre 0 et 1. Pour 7 pertinents trouvés et 3 oubliés, elle renvoie 0,7 ; pour 5 trouvés sur 8, 0,625. C'est la brique de base que réutilisent les démonstrations et les quatre cas.

**`recall_at_k(retrouves, pertinents, k)`** — Celle-ci est l'inspecteur qui ne lit que les k premières lignes d'un classement : elle reçoit la liste ordonnée des documents renvoyés, l'ensemble des documents pertinents et la taille k de la fenêtre, lève une `ValueError` si k est inférieur à 1, renvoie `None` si l'ensemble des pertinents est vide, puis compte combien de pertinents figurent parmi les k premiers résultats et divise ce compte par le nombre total de pertinents. Sur le classement de la démonstration 3, avec quatre pertinents, elle trace la courbe 0, 0, 0,25, 0,25, 0,5, 0,75, 0,75, 1, 1, 1 pour k allant de 1 à 10, une courbe qui ne redescend jamais quand on allonge la même liste.

**`rappel_union(r1, r2, commun, n_rel)`** — Cette fonction fait le travail d'un recenseur qui fusionne deux registres sans compter deux fois les mêmes personnes : elle reçoit les rappels de deux moteurs, le nombre de pertinents trouvés par les deux à la fois et le nombre total de pertinents, et renvoie, par inclusion-exclusion, r₁ + r₂ − commun / n_rel, sans aucune vérification. Avec les rappels 0,625 et 0,5, deux clauses communes et huit pertinents, elle renvoie 0,875, soit 7 clauses sur 8 et non 8 comme le croirait celui qui additionne les rappels ; avec quatre clauses communes, l'union retombe à 0,625, le meilleur des deux moteurs. Le cas du bâtiment et l'exercice 7 s'appuient sur elle.

**`union_independante(r1, r2)`** — Celle-ci est le statisticien qui prévoit ce que donnerait l'union de deux moteurs si leurs oublis ne se ressemblaient pas du tout : elle reçoit les deux rappels et renvoie 1 − (1 − r₁)(1 − r₂), la probabilité qu'un pertinent échappe aux deux à la fois retranchée de 1. Elle prévoit 0,8125 pour les rappels 0,625 et 0,5, à comparer au 0,875 réellement observé dans le cas du bâtiment, ce qui montre que les deux moteurs se recouvrent moins que le hasard ne le voudrait, et 0,88 pour les rappels 0,7 et 0,6 de l'exercice 2.

**`recall_moyen(valeurs)`** — Cette fonction joue le rôle d'un professeur qui fait la moyenne de ses notes en écartant les copies blanches au lieu de leur mettre zéro : elle reçoit une liste de rappels, dont certains valent `None` pour des questions sans aucun pertinent, garde les valeurs définies, en fait la moyenne arithmétique, ou `None` s'il n'en reste aucune, et renvoie le couple formé de cette moyenne macro et du nombre de questions écartées. Pour 0,5, 1, 0 et `None`, elle renvoie 0,5 avec une question exclue, là où compter la question vide pour 0 aurait donné 0,375 et la compter pour 1 aurait donné 0,625.

**`recall_micro(comptes)`** — Celle-ci est le comptable qui additionne tout avant de diviser, au lieu de faire la moyenne de moyennes : elle reçoit une liste de couples (pertinents trouvés, pertinents existants), additionne séparément les deux colonnes et renvoie le rapport de ces totaux, ou `None` si le total des pertinents est nul. Pour les couples (1, 1) et (1, 4), elle renvoie 0,4, alors que la moyenne macro des mêmes questions vaut 0,625 : chaque question pèse ici selon son nombre de pertinents, et c'est cet écart que la démonstration 6 et le cas des ressources humaines mettent en lumière.

**`cas_1_btp_hybride()`** — Cette fonction met en scène un ingénieur du bâtiment qui doit retrouver 8 clauses pertinentes dans un contrat de 3 000 000 AED hors taxes, avec un objectif de rappel de 0,85 : le moteur sémantique en trouve 5, le moteur BM25 en trouve 4, et 2 sont trouvées par les deux. Elle calcule les rappels 0,625 et 0,5, le rappel 0,875 de l'union, la prévision 0,8125 et le recouvrement attendu de 2,5 sous l'hypothèse d'indépendance, puis la retenue de garantie de 5 %, 150 000 AED, et l'exposition moyenne de cette retenue quand une clause manque, qui tombe de 56 250 à 18 750 AED quand on passe du seul moteur sémantique à l'hybride. Elle calcule aussi la précision avant fusion, 7 sur 18, soit 0,38889, le minimum de 7 clauses à trouver pour tenir l'objectif, et le recouvrement de bascule, 3, au-delà duquel l'union tomberait à 0,75, puis renvoie un dictionnaire dont la clé `decision` vaut `True` : l'hybride tient l'objectif quand aucun moteur seul ne le tient.

**`cas_2_assur_fraude()`** — Ici, un assureur hésite entre deux seuils de détection de fraude sur 250 fraudes réelles : le seuil A trouve 230 fraudes avec 70 fausses alertes, le seuil B en trouve 240 avec 160 fausses alertes, chaque fraude manquée coûte 1 500 AED et chaque examen 60 AED. Pour chaque seuil, la fonction calcule le rappel (0,92 et 0,96), les fraudes manquées (20 et 10), la précision (0,76667 et 0,6) et le coût total, fraudes manquées plus examens, soit 48 000 AED pour A et 39 000 AED pour B, puis la valeur d'un point de rappel, 3 750 AED. Elle choisit le seuil le moins cher, B, et calcule les deux valeurs de bascule : A redeviendrait préférable si l'examen coûtait plus de 150 AED, ou si une fraude manquée coûtait moins de 600 AED, avant de renvoyer ces résultats dans un dictionnaire.

**`cas_3_rh_fin_de_service()`** — Cette fonction se place dans un service des ressources humaines qui teste un assistant sur quatre questions d'indemnité de fin de service, dont les couples (trouvés, pertinents) valent (2, 3), (1, 1), (1, 2) et (0, 0). Elle calcule les rappels par question, 0,66667, 1, 0,5 et `None`, la moyenne macro 0,72222 avec une question exclue, la moyenne micro 0,66667 et la moyenne fautive 0,54167 qui compterait la question vide pour 0, puis refuse la mise en production, puisque la macro reste sous 0,9. Elle chiffre ensuite l'enjeu pour un salarié à 15 000 AED par mois et 8 ans d'ancienneté, avec un salaire journalier de 500 AED : l'indemnité due est de 97 500 AED (21 jours par an pour les 5 premières années, 30 jours ensuite), alors que l'assistant privé de la règle des 30 jours annoncerait 84 000 AED, soit 13 500 AED d'écart ; elle calcule enfin le plafond de 24 mois, 360 000 AED, atteint après 25,5 ans, et la macro de 0,83333 si la première question était corrigée, et renvoie tout dans un dictionnaire.

**`cas_4_crypto_noms()`** — Cette fonction se place dans une plateforme de cryptoactifs qui filtre les noms translittérés de ses clients pour repérer les personnes à signaler, avec 40 correspondances connues, 5 minutes d'examen par alerte, une capacité de 480 minutes par jour et un objectif de rappel de 0,95. Elle compare trois méthodes : A trouve 22 correspondances en 25 alertes (rappel 0,55, 18 manquées, 125 minutes), B en trouve 36 en 40 alertes (0,9, 4 manquées, 200 minutes) et C en trouve 39 en 70 alertes (0,975, 1 manquée, 350 minutes), et elle ne déclare admissible que C, seule à tenir à la fois l'objectif et la capacité. Elle calcule aussi la capacité de 96 alertes par jour, le minimum de 38 correspondances à trouver et l'effet d'une hausse de 10 % des alertes de C, 77 alertes et 385 minutes, encore sous la capacité, puis renvoie ces résultats dans un dictionnaire.

**`main()`** — C'est le chef d'orchestre de la fiche : il vérifie d'abord les bornes du rappel et le cas `None` sur une grille de 20 par 20 compteurs, puis montre que 1 000 documents hors sujet laissent le rappel à 0,7 alors que la précision s'effondre à 0,11667, trace la courbe de `recall_at_k` et vérifie qu'elle ne redescend jamais et qu'elle reste sous son plafond, contrôle l'union par inclusion-exclusion sur de vrais ensembles de clauses, puis compare les moyennes macro et micro. Il appelle ensuite les quatre cas en confrontant chaque valeur renvoyée à des `assert`, recalcule le corrigé des exercices, dont les coûts 90 000 et 95 000 AED de l'exercice 6, vérifie qu'une fenêtre k = 0 est bien refusée et n'affiche « OK — toutes les vérifications sont passées. » que si tout concorde ; il ne renvoie rien.

```python
"""Démonstration 13 — rappel : proportion, conditionnement, monotonie en k, plafond, union, moyennes, quatre cas aux Émirats."""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def rappel(vp: int, fn: int) -> float | None:
    """VP / (VP + FN) ; None s'il n'y avait rien à trouver (pas de dénominateur)."""
    if vp < 0 or fn < 0:
        raise ValueError("compteurs négatifs")
    if vp + fn == 0:
        return None
    return vp / (vp + fn)


def recall_at_k(retrouves: list[str], pertinents: set[str], k: int) -> float | None:
    """|Top_k ∩ Rel| / |Rel| (étape 25) ; None si aucun pertinent ; ValueError si k < 1."""
    if k < 1:
        raise ValueError("k doit valoir au moins 1")
    if not pertinents:
        return None
    return len(set(retrouves[:k]) & pertinents) / len(pertinents)


def rappel_union(r1: float, r2: float, commun: int, n_rel: int) -> float:
    """Inclusion-exclusion : r1 + r2 − c / |Rel|."""
    return r1 + r2 - commun / n_rel


def union_independante(r1: float, r2: float) -> float:
    """Rappel attendu de l'union si les oublis des deux moteurs sont indépendants."""
    return 1 - (1 - r1) * (1 - r2)


def recall_moyen(valeurs: list[float | None]) -> tuple[float | None, int]:
    """Moyenne macro sur les questions définies, et nombre de questions exclues."""
    definies = [v for v in valeurs if v is not None]
    moyenne = sum(definies) / len(definies) if definies else None
    return moyenne, len(valeurs) - len(definies)


def recall_micro(comptes: list[tuple[int, int]]) -> float | None:
    """Total des trouvés / total des pertinents, à partir de couples (vp, |Rel|)."""
    total = sum(n for _, n in comptes)
    return None if total == 0 else sum(v for v, _ in comptes) / total


def cas_1_btp_hybride() -> dict:
    """[BTP] 8 clauses pertinentes : sémantique 5, BM25 4, communes 2 ; objectif 0,85 ; retenue de 5 % sur 3 000 000 AED."""
    n_rel, vp1, vp2, commun, objectif, montant_ht = 8, 5, 4, 2, 0.85, 3_000_000
    r1, r2 = rappel(vp1, n_rel - vp1), rappel(vp2, n_rel - vp2)
    ru = rappel_union(r1, r2, commun, n_rel)
    prevu, recouvrement_attendu = union_independante(r1, r2), n_rel * r1 * r2
    retenue = 0.05 * montant_ht
    expo_seul, expo_union = (n_rel - vp1) / n_rel * retenue, (1 - ru) * retenue
    precision_union = 7 / (10 + 10 - commun)
    minimum = next(m for m in range(0, n_rel + 1) if m / n_rel >= objectif)
    c_bascule = next(c for c in range(0, 5) if rappel_union(r1, r2, c, n_rel) < objectif)
    print(f"Cas 1 [BTP] r1 = {r1}, r2 = {r2}, union {ru} (indépendance {prevu}, recouvrement attendu {recouvrement_attendu})")
    print(f"  retenue {retenue:,.0f} AED ; exposition {expo_seul:,.0f} → {expo_union:,.0f} AED ;"
          f" précision avant fusion {precision_union:.5f} ; décision : hybride ; bascule c = {c_bascule}")
    return {"r1": r1, "r2": r2, "ru": ru, "prevu": prevu, "recouvrement_attendu": recouvrement_attendu,
            "retenue": retenue, "expo_seul": expo_seul, "expo_union": expo_union, "ttc": montant_ht * 1.05,
            "precision_union": precision_union, "minimum": minimum, "c_bascule": c_bascule,
            "decision": ru >= objectif and max(r1, r2) < objectif}


def cas_2_assur_fraude() -> dict:
    """[ASSUR] 250 fraudes ; seuil A (230, 70) ; seuil B (240, 160) ; fraude 1 500 AED ; examen 60 AED."""
    n_rel, montant, examen = 250, 1_500, 60
    seuils = {"A": (230, 70), "B": (240, 160)}
    res = {}
    for nom, (vp, fp) in seuils.items():
        fn = n_rel - vp
        res[nom] = {"r": rappel(vp, fn), "fn": fn, "p": vp / (vp + fp), "cout": fn * montant + (vp + fp) * examen}
    point = 0.01 * n_rel * montant
    c_bascule = (res["A"]["fn"] - res["B"]["fn"]) * montant / ((240 + 160) - (230 + 70))
    m_bascule = (400 - 300) * examen / (res["A"]["fn"] - res["B"]["fn"])
    choix = min(res, key=lambda k: res[k]["cout"])
    print(f"Cas 2 [ASSUR] A : R {res['A']['r']}, coût {res['A']['cout']:,} AED ; B : R {res['B']['r']}, coût {res['B']['cout']:,} AED ;"
          f" point de rappel {point:,.0f} AED ; décision : {choix}")
    print(f"  précisions A {res['A']['p']:.5f}, B {res['B']['p']} ; bascule examen {c_bascule:.0f} AED, fraude {m_bascule:.0f} AED")
    return {"res": res, "point": point, "c_bascule": c_bascule, "m_bascule": m_bascule, "choix": choix}


def cas_3_rh_fin_de_service() -> dict:
    """[RH] 4 questions : (trouvés, pertinents) = (2, 3), (1, 1), (1, 2), (0, 0) ; salarié à 15 000 AED, 8 ans."""
    comptes = [(2, 3), (1, 1), (1, 2), (0, 0)]
    par_question = [rappel(v, n - v) for v, n in comptes]
    macro, exclues = recall_moyen(par_question)
    micro = recall_micro(comptes)
    ancienne = sum(v if v is not None else 0.0 for v in par_question) / len(par_question)
    base, annees = 15_000, 8
    jour = base / 30
    du = 5 * 21 * jour + (annees - 5) * 30 * jour
    annonce = annees * 21 * jour
    plafond = 24 * base
    macro_q1 = (1 + 1 + 0.5) / 3
    annees_plafond = 5 + (24 * 30 - 5 * 21) / 30
    print(f"Cas 3 [RH] rappels {[None if v is None else round(v, 5) for v in par_question]} ; macro {macro:.5f}"
          f" ({exclues} exclue) ; micro {micro:.5f} ; convention 0 : {ancienne:.5f} ; décision : {'production' if macro >= 0.9 else 'refusée'}")
    print(f"  indemnité due {du:,.0f} AED, annoncée {annonce:,.0f} AED (écart {du - annonce:,.0f}) ; plafond {plafond:,} AED ;"
          f" macro si q1 corrigée {macro_q1:.5f} ; plafond atteint après {annees_plafond} ans")
    return {"par_question": par_question, "macro": macro, "exclues": exclues, "micro": micro, "ancienne": ancienne,
            "jour": jour, "du": du, "annonce": annonce, "plafond": plafond, "macro_q1": macro_q1,
            "annees_plafond": annees_plafond}


def cas_4_crypto_noms() -> dict:
    """[CRYPTO] 40 correspondances connues ; méthodes A, B, C ; 5 min par alerte ; capacité 480 min."""
    n_rel, minutes, capacite, objectif = 40, 5, 480, 0.95
    methodes = {"A": (22, 25), "B": (36, 40), "C": (39, 70)}
    table = {m: (rappel(t, n_rel - t), n_rel - t, a * minutes) for m, (t, a) in methodes.items()}
    admissibles = [m for m in methodes if table[m][0] >= objectif and table[m][2] <= capacite]
    alertes_max = capacite // minutes
    minimum = next(t for t in range(0, n_rel + 1) if t / n_rel >= objectif)
    plus_10 = round(70 * 1.1)
    print("Cas 4 [CRYPTO] " + " ; ".join(f"{m} : R {table[m][0]}, manquées {table[m][1]}, {table[m][2]} min" for m in methodes)
          + f" ; décision : {admissibles}")
    print(f"  minimum {minimum} correspondances ; capacité {alertes_max} alertes par jour ; +10 % : {plus_10} alertes,"
          f" {plus_10 * minutes} min")
    return {"table": table, "admissibles": admissibles, "alertes_max": alertes_max, "minimum": minimum,
            "plus_10": plus_10}


def main() -> None:
    # Démonstration 1
    print(f"Démonstration 1 : 7/10 → {rappel(7, 3)} ; 5/8 → {rappel(5, 3)} ; rien à trouver → {rappel(0, 0)}")
    assert rappel(7, 3) == 0.7 and rappel(5, 3) == 0.625 and rappel(0, 0) is None and rappel(4, 0) == 1.0
    assert rappel(0, 4) == 0.0
    for vp in range(0, 20):
        for fn in range(0, 20):
            r = rappel(vp, fn)
            assert r is None if vp + fn == 0 else 0.0 <= r <= 1.0

    # Démonstration 2 : ajouter des non-pertinents ne change pas le rappel
    print(f"Démonstration 2 : rappel {rappel(7, 3)} avant et après 1 000 documents hors sujet ;"
          f" précision {7 / 10} → {7 / (7 + 3 + 50):.5f}")
    assert round(7 / (7 + 3 + 50), 5) == 0.11667

    # Démonstration 3 : monotonie
    pertinents = {"d1", "d2", "d4", "d6"}
    retrouves = ["d3", "d7", "d1", "d9", "d4", "d2", "d8", "d6", "d5", "d10"]
    courbe = [recall_at_k(retrouves, pertinents, k) for k in range(1, 11)]
    print("Démonstration 3 : Recall@1..10 = " + " ".join(f"{v:.2f}" for v in courbe))
    assert courbe == [0.0, 0.0, 0.25, 0.25, 0.5, 0.75, 0.75, 1.0, 1.0, 1.0]
    assert all(a <= b for a, b in zip(courbe, courbe[1:]))
    hausses = [k + 1 for k in range(1, 10) if courbe[k] > courbe[k - 1]]
    assert hausses == [3, 5, 6, 8] and (courbe[2] > courbe[1]) == (retrouves[2] in pertinents)
    liste_5 = ["d1", "d4", "x", "y", "z"]
    liste_6 = ["x", "d4", "y", "z", "w", "v"]
    print(f"  deux listes différentes : k = 5 → {recall_at_k(liste_5, pertinents, 5)} ; k = 6 → {recall_at_k(liste_6, pertinents, 6)}")
    assert recall_at_k(liste_5, pertinents, 5) == 0.5 and recall_at_k(liste_6, pertinents, 6) == 0.25

    # Démonstration 4 : plafond
    assert all(v <= min(1.0, k / 4) for k, v in enumerate(courbe, start=1))
    parfait = sorted(pertinents) + ["d3", "d7", "d9"]
    assert [recall_at_k(parfait, pertinents, k) for k in range(1, 6)] == [min(1.0, k / 4) for k in range(1, 6)]
    print(f"Démonstration 4 : plafond 8 clauses top-5 = {min(1, 5 / 8)} ; 12 passages top-10 = {min(1, 10 / 12):.3f} ;"
          f" 0,5 rapporté au plafond = {0.5 / round(10 / 12, 3):.2f}")
    assert min(1, 5 / 8) == 0.625 and round(min(1, 10 / 12), 3) == 0.833 and round(0.5 / 0.833, 2) == 0.6

    # Démonstration 5 : union
    ru = rappel_union(0.625, 0.5, 2, 8)
    print(f"Démonstration 5 : union {ru} ; indépendance {union_independante(0.625, 0.5)} ; recouvrement attendu {8 * 0.625 * 0.5} ;"
          f" si c = 4 : {rappel_union(0.625, 0.5, 4, 8)}")
    assert ru == 0.875 and union_independante(0.625, 0.5) == 0.8125 and 8 * 0.625 * 0.5 == 2.5
    assert rappel_union(0.625, 0.5, 4, 8) == 0.625 == max(0.625, 0.5) and min(1, 0.625 + 0.5) == 1
    assert 0.625 + 0.5 == 1.125
    dense = {"c1", "c2", "c3", "c4", "c5"}
    bm25 = {"c4", "c5", "c6", "c7"}
    rel = {f"c{i}" for i in range(1, 9)}
    assert len((dense | bm25) & rel) / len(rel) == ru and len(dense & bm25) == 2

    # Démonstration 6 : moyennes
    macro, _ = recall_moyen([1.0, 0.25])
    micro = recall_micro([(1, 1), (1, 4)])
    m4, exclues = recall_moyen([0.5, 1.0, 0.0, None])
    print(f"Démonstration 6 : macro {macro} ; micro {micro} ; avec None : {m4} ({exclues} exclue),"
          f" convention 0 : {1.5 / 4}, convention 1 : {2.5 / 4}")
    assert macro == 0.625 and micro == 0.4 and abs((1 / 5) * 1 + (4 / 5) * 0.25 - 0.4) < 1e-12
    assert (m4, exclues) == (0.5, 1) and 1.5 / 4 == 0.375 and 2.5 / 4 == 0.625 and recall_moyen([None])[0] is None

    # Exemple simple
    assert rappel(7, 10 - 7) == 0.7 and min(1, 10 / 10) == 1 and min(1, 5 / 10) == 0.5

    # Cas
    c1 = cas_1_btp_hybride()
    assert (c1["r1"], c1["r2"], c1["ru"], c1["prevu"], c1["recouvrement_attendu"]) == (0.625, 0.5, 0.875, 0.8125, 2.5)
    assert c1["retenue"] == 150_000 and c1["expo_seul"] == 56_250 and c1["expo_union"] == 18_750
    assert c1["expo_seul"] - c1["expo_union"] == 37_500 and round(c1["ttc"]) == 3_150_000
    assert round(c1["precision_union"], 5) == 0.38889 and c1["minimum"] == 7 and round(0.85 * 8, 1) == 6.8
    assert c1["c_bascule"] == 3 and rappel_union(0.625, 0.5, 3, 8) == 0.75 and c1["decision"] is True

    c2 = cas_2_assur_fraude()
    a, b = c2["res"]["A"], c2["res"]["B"]
    assert (a["r"], a["fn"], b["r"], b["fn"]) == (0.92, 20, 0.96, 10)
    assert c2["point"] == 3_750 and 0.01 * 250 == 2.5 and a["cout"] == 48_000 and b["cout"] == 39_000
    assert 20 * 1_500 == 30_000 and 300 * 60 == 18_000 and 10 * 1_500 == 15_000 and 400 * 60 == 24_000
    assert 100 * 60 == 6_000 and c2["choix"] == "B" and a["cout"] - b["cout"] == 9_000 and 9_000 * 12 == 108_000
    assert round(a["p"], 5) == 0.76667 and b["p"] == 0.6 and 4 * 3_750 == 15_000
    assert c2["c_bascule"] == 150 and c2["m_bascule"] == 600

    c3 = cas_3_rh_fin_de_service()
    assert [None if v is None else round(v, 5) for v in c3["par_question"]] == [0.66667, 1.0, 0.5, None]
    assert round(c3["macro"], 5) == 0.72222 and c3["exclues"] == 1 and round(c3["micro"], 5) == 0.66667
    assert round(c3["ancienne"], 5) == 0.54167 and c3["jour"] == 500 and c3["du"] == 97_500
    assert 5 * 21 * 500 == 52_500 and 3 * 30 * 500 == 45_000 and c3["annonce"] == 84_000 and c3["plafond"] == 360_000
    assert c3["du"] - c3["annonce"] == 13_500 and round(c3["macro_q1"], 5) == 0.83333 and c3["annees_plafond"] == 25.5
    assert 9 * 500 == 4_500 and 24 * 30 == 720

    c4 = cas_4_crypto_noms()
    t = c4["table"]
    assert (t["A"][0], t["B"][0], t["C"][0]) == (0.55, 0.9, 0.975) and (t["A"][1], t["B"][1], t["C"][1]) == (18, 4, 1)
    assert (t["A"][2], t["B"][2], t["C"][2]) == (125, 200, 350) and c4["admissibles"] == ["C"]
    assert c4["alertes_max"] == 96 and c4["minimum"] == 38 and c4["plus_10"] == 77 and 77 * 5 == 385
    assert round(18 / 40 * 100) == 45

    # Corrigé
    print("Corrigé")
    a6 = 20 * 1_500 + 300 * 200
    b6 = 10 * 1_500 + 400 * 200
    print(f"  ex1 {6 / 12} et plafond {min(1, 10 / 12):.3f} ; ex2 {union_independante(0.7, 0.6):.2f} ; ex4 précision {10 / 100_000} ;"
          f" ex5 {250 * 0.03:.1f} ; ex6 A {a6:,} B {b6:,} ; ex7 {rappel_union(0.625, 0.5, 2, 8)}")
    assert 6 / 12 == 0.5 and round(min(1, 10 / 12), 3) == 0.833 and round(union_independante(0.7, 0.6), 2) == 0.88
    assert round(0.3 * 0.4, 2) == 0.12 and 10 / 100_000 == 0.0001 and round(250 * 0.03, 1) == 7.5
    assert a6 == 90_000 and b6 == 95_000 and 300 * 200 == 60_000 and 400 * 200 == 80_000 and a6 < b6
    try:
        recall_at_k(retrouves, pertinents, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("k = 0 aurait dû être refusé")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Démonstration 1 : 7/10 → 0.7 ; 5/8 → 0.625 ; rien à trouver → None
Démonstration 2 : rappel 0.7 avant et après 1 000 documents hors sujet ; précision 0.7 → 0.11667
Démonstration 3 : Recall@1..10 = 0.00 0.00 0.25 0.25 0.50 0.75 0.75 1.00 1.00 1.00
  deux listes différentes : k = 5 → 0.5 ; k = 6 → 0.25
Démonstration 4 : plafond 8 clauses top-5 = 0.625 ; 12 passages top-10 = 0.833 ; 0,5 rapporté au plafond = 0.60
Démonstration 5 : union 0.875 ; indépendance 0.8125 ; recouvrement attendu 2.5 ; si c = 4 : 0.625
Démonstration 6 : macro 0.625 ; micro 0.4 ; avec None : 0.5 (1 exclue), convention 0 : 0.375, convention 1 : 0.625
Cas 1 [BTP] r1 = 0.625, r2 = 0.5, union 0.875 (indépendance 0.8125, recouvrement attendu 2.5)
  retenue 150,000 AED ; exposition 56,250 → 18,750 AED ; précision avant fusion 0.38889 ; décision : hybride ; bascule c = 3
Cas 2 [ASSUR] A : R 0.92, coût 48,000 AED ; B : R 0.96, coût 39,000 AED ; point de rappel 3,750 AED ; décision : B
  précisions A 0.76667, B 0.6 ; bascule examen 150 AED, fraude 600 AED
Cas 3 [RH] rappels [0.66667, 1.0, 0.5, None] ; macro 0.72222 (1 exclue) ; micro 0.66667 ; convention 0 : 0.54167 ; décision : refusée
  indemnité due 97,500 AED, annoncée 84,000 AED (écart 13,500) ; plafond 360,000 AED ; macro si q1 corrigée 0.83333 ; plafond atteint après 25.5 ans
Cas 4 [CRYPTO] A : R 0.55, manquées 18, 125 min ; B : R 0.9, manquées 4, 200 min ; C : R 0.975, manquées 1, 350 min ; décision : ['C']
  minimum 38 correspondances ; capacité 96 alertes par jour ; +10 % : 77 alertes, 385 min
Corrigé
  ex1 0.5 et plafond 0.833 ; ex2 0.88 ; ex4 précision 0.0001 ; ex5 7.5 ; ex6 A 90,000 B 95,000 ; ex7 0.875
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme mesure le rappel d'un système, la part des éléments pertinents qu'il a retrouvés, pour un moteur ou pour l'union de deux moteurs, puis le moyenne sur un jeu de questions en écartant celles qui n'ont aucun pertinent.

```text
ALGORITHME Rappel
ENTRÉES : éléments trouvés T, éléments pertinents Rel
SORTIE  : rappel dans [0 ; 1], ou INDÉFINI si Rel est vide

  SI Rel est vide ALORS RETOURNER INDÉFINI
  communs ← nombre d'éléments de T qui sont dans Rel
  RETOURNER communs / |Rel|

ALGORITHME RappelDeLUnion
ENTRÉES : rappels r₁ et r₂ de deux moteurs, recouvrement c, |Rel|
  RETOURNER r₁ + r₂ − c / |Rel|                 (au moins max(r₁, r₂), au plus 1)

ALGORITHME RappelMoyen
ENTRÉES : rappels des questions (certains INDÉFINIS)
  définis ← rappels qui ne sont pas INDÉFINIS
  RETOURNER moyenne(définis), nombre d'exclus
```

**Complexité.** Avec des ensembles (tables de hachage), un rappel coûte O(|T| + |Rel|). Le calcul de Recall@k pour tous les k de 1 à n coûte O(n²) tel qu'écrit, ou O(n) en ajoutant un résultat à la fois, puisque le rappel ne monte que d'une marche à chaque pertinent rencontré (démonstration 3). L'union et les moyennes coûtent O(1) par question une fois les comptages faits.

**Du squelette au code.** Rappel est `rappel(vp, fn)`, qui renvoie `None` quand rien n'était à trouver, et sa version classée `recall_at_k(retrouves, pertinents, k)`, qui utilise l'intersection `set(retrouves[:k]) & pertinents`. RappelDeLUnion est `rappel_union(r1, r2, commun, n_rel)`, et sa prévision sous indépendance `union_independante(r1, r2)`. RappelMoyen est `recall_moyen(valeurs)`, et la moyenne micro `recall_micro(comptes)`. La courbe `courbe` de `main` vérifie la monotonie et le plafond k/|Rel|. Les cas sont `cas_1_btp_hybride`, `cas_2_assur_fraude`, `cas_3_rh_fin_de_service` et `cas_4_crypto_noms`.
