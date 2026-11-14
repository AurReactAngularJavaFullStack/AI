# Étape 28 — RAG — NDCG (Normalized Discounted Cumulative Gain)

> Étape 28 du parcours · Prérequis : [MRR](<27-RAG-Formule-MRR.md>) · Suite : [Exemples de RAG de bout en bout](<29-RAG-Exemples-Cas-Usage.md>)

**Dossier :** 05-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  
**Nom du fichier :** 28-RAG-Formule-NDCG.md

## Définition

Le NDCG (Normalized Discounted Cumulative Gain, gain cumulé actualisé et normalisé) évalue un classement quand la pertinence n'est pas seulement « oui ou non » mais **graduée** : un document peut être parfait (note 3), utile (2), marginal (1) ou hors sujet (0). Chaque document rapporte un gain qui croît avec sa note, et ce gain est d'autant plus réduit, ou « actualisé », que le document est classé bas : la somme de ces gains est le DCG. On divise ensuite par l'IDCG, qui est le DCG du **classement idéal de tous les documents jugés pertinents, tronqué à k**, qu'ils aient été retrouvés ou non. Le résultat est compris entre 0 et 1, et il vaut 1 quand le moteur a placé en tête les meilleurs documents qui existent, dans le meilleur ordre. Contrairement au MRR (étape 27), il tient compte de tous les documents pertinents du top-k ; contrairement à la Precision@k (étape 26), il tient compte de leur ordre et de leur note.

## Rôle dans un agent

Quand l'agent a besoin de plusieurs documents de valeur inégale pour décider (plusieurs comparables pour estimer un prix, plusieurs clauses pour instruire un sinistre, plusieurs extraits réglementaires pour une réponse de conformité), il ne suffit pas de savoir si le premier est bon. Il faut que les meilleurs soient en tête, là où le modèle les lit d'abord et là où l'agent les garde quand il doit couper son contexte faute de place. Le NDCG mesure exactement cela, au moment où l'agent observe le résultat de son action de recherche. On l'utilise hors ligne pour régler le **reranker** et la fusion des scores (étapes 23 et 24) sur un jeu de questions dont les documents ont été notés par des experts, et en production pour vérifier qu'une nouvelle version de l'index ne dégrade pas l'ordre. Il aide aussi à choisir combien de documents garder : on regarde à partir de quel rang le DCG n'augmente presque plus.

## Équation complète

Gain d'un document de note rel (forme exponentielle, la plus répandue) :

$$
g(\text{rel}) = 2^{\text{rel}} - 1
$$

Gain cumulé actualisé des k premiers résultats, avec relᵢ la note du document de rang i :

$$
\text{DCG@}k = \sum_{i=1}^{k} \frac{2^{\text{rel}_i} - 1}{\log_2(i + 1)}
$$

Gain idéal : on range par ordre décroissant les notes rel\*₁ ≥ rel\*₂ ≥ … de **tous** les documents jugés pour la question, retrouvés ou non, et on garde les k premières :

$$
\text{IDCG@}k = \sum_{i=1}^{k} \frac{2^{\text{rel}^*_i} - 1}{\log_2(i + 1)}
$$

Normalisation, définie seulement quand au moins un document jugé est pertinent :

$$
\text{NDCG@}k = \frac{\text{DCG@}k}{\text{IDCG@}k} \qquad \text{avec} \qquad \text{IDCG@}k > 0
$$

Variante à gain linéaire, identique à la précédente en pertinence binaire :

$$
\text{DCG}_{lin}@k = \sum_{i=1}^{k} \frac{\text{rel}_i}{\log_2(i + 1)}
$$

## Décryptage des symboles

$$
\text{rel}_i
$$

**Sens :** note du document de rang i dans la liste retrouvée (0 s'il n'a pas été jugé) · **Type / plage :** entier ≥ 0, ici de 0 à 3 · **Variable Python :** `rels_retrouves[i - 1]`

$$
\text{rel}^*_i
$$

**Sens :** i-ième plus grande note parmi tous les documents jugés · **Type / plage :** entier ≥ 0 · **Variable Python :** `sorted(rels_tous_juges, reverse=True)[i - 1]`

$$
g(\text{rel})
$$

**Sens :** gain d'un document · **Type / plage :** 0, 1, 3, 7 pour les notes 0 à 3 · **Variable Python :** `gain_exponentiel(rel)`

$$
w_i = 1/\log_2(i+1)
$$

**Sens :** remise du rang i · **Type / plage :** réel dans ]0, 1], strictement décroissant · **Variable Python :** `remise(i)`

$$
k
$$

**Sens :** nombre de rangs évalués · **Type / plage :** entier ≥ 1 · **Variable Python :** `k`

$$
\text{DCG@}k
$$

**Sens :** gain cumulé actualisé de la liste retrouvée · **Type / plage :** réel ≥ 0 · **Variable Python :** `dcg_at_k(rels_retrouves, k)`

$$
\text{IDCG@}k
$$

**Sens :** DCG du classement idéal de tous les documents jugés, tronqué à k · **Type / plage :** réel ≥ 0 · **Variable Python :** `dcg_at_k(sorted(rels_tous_juges, reverse=True), k)`

$$
\text{NDCG@}k
$$

**Sens :** rapport des deux · **Type / plage :** réel dans [0, 1], indéfini si l'IDCG est nul · **Variable Python :** `ndcg_at_k(rels_retrouves, rels_tous_juges, k)`

## Démonstration

### 1. L'IDCG doit venir de tous les documents jugés, pas de la liste retrouvée

L'ancien code calculait l'idéal en triant la liste **retrouvée** : `ideal = sorted(relevances, reverse=True)`. Il mesurait donc seulement si le moteur avait bien rangé ce qu'il avait trouvé, jamais s'il avait trouvé les bons documents. Deux contre-exemples chiffrés le montrent.

Premier cas : trois documents sont pertinents (note 1), et le moteur n'en trouve qu'un, au rang 1, suivi de deux documents hors sujet, soit [1, 0, 0]. L'ancien code trie [1, 0, 0], retrouve la même liste et annonce NDCG@3 = 1, un score parfait alors que deux pertinents sur trois manquent. Le bon idéal est [1, 1, 1], d'où IDCG@3 = 1 + 0,6309 + 0,5 = 2,1309 et NDCG@3 = 1/2,1309 ≈ 0,469.

Second cas, en pertinence graduée : le moteur renvoie des documents notés [3, 2, 0] alors que les jugements contiennent [3, 3, 2, 1]. L'ancien code annonce encore 1. Le bon calcul donne DCG@3 = 7 + 3 × 0,6309 = 8,8928, puis

$$
\text{IDCG@}3 = 7 + 7 \times 0{,}6309 + 3 \times 0{,}5 = 12{,}9165 ,
$$

et NDCG@3 ≈ 0,689. C'est pourquoi la nouvelle signature prend deux listes : `ndcg_at_k(rels_retrouves, rels_tous_juges, k)`.

### 2. Le classement idéal maximise le DCG (inégalité de réarrangement)

Les remises wᵢ = 1/log₂(i+1) décroissent strictement, **parce que** log₂ est strictement croissante : w₁ = 1, w₂ ≈ 0,6309, w₃ = 0,5, w₄ ≈ 0,4307, w₅ ≈ 0,3869. Supposons qu'une liste place un gain gᵢ au rang i et un gain plus grand, gⱼ > gᵢ, à un rang j > i situé plus bas. Échanger les deux documents fait passer leur contribution de gᵢ wᵢ + gⱼ wⱼ à gⱼ wᵢ + gᵢ wⱼ, soit une variation :

$$
(g_j w_i + g_i w_j) - (g_i w_i + g_j w_j) = (g_j - g_i)(w_i - w_j) > 0
$$

Elle est strictement positive **parce que** ses deux facteurs le sont. Tant qu'une liste contient deux documents mal ordonnés, on peut donc l'améliorer par un échange ; comme il n'y a qu'un nombre fini d'ordres possibles, le maximum est atteint par un ordre sans paire mal ordonnée, c'est-à-dire trié par gain décroissant (c'est le raisonnement du tri à bulles). Reste à choisir **quels** documents occupent les k places : remplacer un document par un document jugé de meilleure note, absent de la liste, ne fait jamais baisser le DCG, **parce que** chaque remise est positive. Le meilleur top-k possible prend donc les k meilleures notes de tous les documents jugés, rangées par ordre décroissant : c'est exactement la définition de l'IDCG.

On en déduit 0 ≤ DCG@k ≤ IDCG@k, donc NDCG@k ∈ [0, 1], à une condition : les notes de la liste retrouvée doivent provenir des jugements. Sinon, la liste « retrouvée » contient un document meilleur que tout ce qui a été jugé, et le rapport peut dépasser 1. Le code le vérifie et lève `ValueError` dans ce cas, ce qui attrape aussi un document pertinent compté deux fois. L'ancienne phrase « la normalisation par IDCG ramène le score entre 0 et 1 » n'avait de sens qu'avec le bon IDCG : avec l'ancien, la borne restait vraie mais ne mesurait plus rien. Sur l'exemple du point 6, l'échange des rangs 2 et 3, de gains 1 et 3, rapporte (3 − 1)(0,6309 − 0,5) ≈ 0,2619, et l'énumération des 2 520 classements de cinq documents pris parmi les sept jugés confirme qu'aucun ne dépasse l'IDCG.

### 3. Gain linéaire et gain exponentiel

En pertinence binaire, rel ∈ {0, 1}, on a 2⁰ − 1 = 0 et 2¹ − 1 = 1 : le gain exponentiel est égal à la note, et les deux formes du DCG coïncident. L'ancien titre « version binaire simplifiée » était donc trompeur : le même code, avec le gain 2ʳᵉˡ − 1, traite aussi bien le cas binaire que le cas gradué. En pertinence graduée, les deux formes divergent : le gain exponentiel donne 1, 3 et 7 aux notes 1, 2 et 3, au lieu de 1, 2 et 3, si bien qu'un document parfait vaut sept documents marginaux au lieu de trois. Ce choix peut inverser le classement de deux moteurs. Avec les jugements [2, 1, 1, 1], comparons un moteur A qui renvoie [2, 0, 0] (un très bon document, puis du bruit) et un moteur B qui renvoie [1, 1, 1] (trois documents moyens). En gain exponentiel, IDCG@3 = 3 + 0,6309 + 0,5 = 4,1309, A obtient 3/4,1309 ≈ 0,7262 et B 2,1309/4,1309 ≈ 0,5158. En gain linéaire, IDCG@3 = 2 + 0,6309 + 0,5 = 3,1309, A obtient 0,6388 et B 0,6806. Le gain est donc un choix métier : exponentiel quand un document excellent suffit à changer la décision, linéaire quand chaque document utile apporte à peu près autant.

### 4. Ce que le NDCG ne garantit pas, et ce qui ne le change pas

Le NDCG@k n'est pas monotone en k, **parce que** son numérateur et son dénominateur grandissent tous les deux, à des rythmes différents. Avec les jugements [3, 3] et la liste [3, 0, 3], on obtient NDCG@1 = 7/7 = 1, puis

$$
\text{NDCG@}2 = 7/(7 + 7 \times 0{,}6309) = 7/11{,}4165 \approx 0{,}6131 ,
$$

puis

$$
\text{NDCG@}3 = (7 + 7 \times 0{,}5)/11{,}4165 \approx 0{,}9197
$$

La valeur baisse puis remonte. On compare donc toujours deux moteurs au même k.

En revanche, la base du logarithme n'a aucun effet. On a

$$
\log_b(i+1) = \ln(i+1)/\ln b ,
$$

donc passer de la base 2 à la base b multiplie toutes les remises, celles du DCG comme celles de l'IDCG, par le même facteur ln b / ln 2, qui se simplifie dans le rapport. Sur l'exemple du point 6, la base 10 donne le même 0,8620. Le choix de log₂(i+1) reste une convention : il laisse le rang 1 sans remise et fait baisser lentement le poids des rangs suivants, jusqu'à w₁₀ = 1/log₂ 11 ≈ 0,289 au dixième rang.

### 5. IDCG nul : NDCG indéfini

Si aucun document jugé n'a de note positive, l'IDCG vaut 0 et le rapport n'est pas défini. L'ancien code renvoyait 0,0, ce qui faisait passer une question sans réponse possible pour un échec du moteur et tirait la moyenne vers le bas. Le code corrigé renvoie `None`, et la question sort de la moyenne, selon la convention du parcours.

### 6. Exemple fait à la main (le code reprend ces nombres)

Une agence immobilière cherche des comparables pour un deux-chambres de 1 100 sqft à Jumeirah Village Circle (JVC). Un expert a noté sept transactions de 0 à 3 : 3 pour le même quartier, le même type, une surface et une date proches ; 2 pour le même quartier et le même type, mais une surface ou une date plus éloignée ; 1 pour un quartier ou un type voisin ; 0 pour un bien non comparable. Le moteur renvoie cinq transactions :

| Rang i | Transaction | Note | Gain 2ʳᵉˡ − 1 | Remise wᵢ | Contribution |
|---|---|---|---|---|---|
| 1 | `jvc-2ch-1120` | 3 | 7 | 1 | 7 |
| 2 | `jvt-2ch-1100` | 1 | 1 | 0,6309 | 0,6309 |
| 3 | `jvc-2ch-980` | 2 | 3 | 0,5 | 1,5 |
| 4 | `villa-jvc` | 0 | 0 | 0,4307 | 0 |
| 5 | `jvc-2ch-1050` | 3 | 7 | 0,3869 | 2,7080 |

On obtient

$$
\text{DCG@}5 = 7 + 0{,}6309 + 1{,}5 + 0 + 2{,}7080 = 11{,}8389 .
$$

Les sept notes jugées sont 3, 3, 2, 1, 1, 0 et 0 ; le comparable `jvc-1ch-760`, noté 1, n'a pas été retrouvé. Le classement idéal prend les cinq meilleures, [3, 3, 2, 1, 1], d'où

$$
\text{IDCG@}5 = 7 + 7 \times 0{,}6309 + 3 \times 0{,}5 + 0{,}4307 + 0{,}3869 = 13{,}7340
$$

et NDCG@5 = 11,8389/13,7340 ≈ 0,8620. L'ancien code, qui triait la liste retrouvée [3, 1, 2, 0, 3] en [3, 3, 2, 1, 0], aurait annoncé 0,887 : il ignorait le comparable manquant.

## Effets et comportement

- **Remonter un document très pertinent** fait monter le NDCG d'autant plus que sa note est haute et qu'il gagne des places en tête : la variation vaut (gⱼ − gᵢ)(wᵢ − wⱼ) (point 2).
- **Un document pertinent manquant fait baisser le NDCG**, même si la liste retrouvée est parfaitement ordonnée, parce qu'il figure dans l'IDCG. C'est la différence essentielle avec l'ancien calcul.
- **La note la plus haute pèse lourd** en gain exponentiel (7 pour la note 3 contre 3 pour la note 2) : un seul document excellent mal classé coûte cher.
- **Le NDCG@k dépend de k sans être monotone** (point 4) : on fixe k au nombre de documents que l'agent garde réellement, et on l'écrit à côté du chiffre.
- **En pertinence binaire**, le NDCG reste plus fin que la Precision@k : à nombre de documents pertinents égal, il préfère ceux qui sont placés en tête.

## Du symbole au code Python

$$
w_i = 1/\log_2(i+1)
$$

**Variable ou fonction :** `remise(i)`

$$
2^{\text{rel}} - 1
$$

**Variable ou fonction :** `gain_exponentiel(rel)` ; variante `gain_lineaire(rel)`

$$
\text{rel}_1, \dots, \text{rel}_k
$$

**Variable ou fonction :** `rels_retrouves`, obtenu par `notes_retrouvees(retrouves, jugements)`

**Symbole :** notes de tous les documents jugés · **Variable ou fonction :** `rels_tous_juges`, par exemple `list(jugements.values())`

$$
\text{DCG@}k
$$

**Variable ou fonction :** `dcg_at_k(rels, k)`

$$
\text{IDCG@}k
$$

**Variable ou fonction :** `dcg_at_k(sorted(rels_tous_juges, reverse=True), k)`

$$
\text{NDCG@}k
$$

**Variable ou fonction :** `ndcg_at_k(rels_retrouves, rels_tous_juges, k)`

### Déroulé, ligne par ligne

**`remise(i)`** renvoie `1.0 / math.log2(i + 1)`. Le rang `i` commence à 1, donc la première remise vaut `1 / log2(2) = 1`. L'ancien code écrivait `math.log2(i + 2)` avec un `i` qui commençait à 0 : la valeur est la même, mais l'écriture à partir de 1 colle à la formule.

**`gain_exponentiel(rel)`** renvoie `2 ** rel - 1`, soit 0, 1, 3 et 7 pour les notes 0 à 3. **`gain_lineaire(rel)`** renvoie la note elle-même.

**`dcg_at_k(rels, k, gain)`**.

- Les deux gardes refusent `k < 1` et toute note négative : une note de -1 donnerait un gain de 2⁻¹ − 1 = −0,5, et la borne DCG ≥ 0 tomberait.
- `sum(gain(rel) * remise(i) for i, rel in enumerate(rels[:k], start=1))` : on garde les `k` premières notes, on numérote les rangs à partir de 1 et on additionne les contributions. Sur `[3, 1, 2, 0, 3]`, les contributions valent 7, 0,6309, 1,5, 0 et 2,7080, et la somme 11,8389.

**`ndcg_at_k(rels_retrouves, rels_tous_juges, k, gain)`**.

- `manque = Counter(...) - Counter(...)` : on compte, note par note, les documents pertinents de la liste retrouvée et ceux des jugements. La soustraction de deux `Counter` ne garde que les différences positives : si la liste retrouvée contient plus de documents notés 3 que les jugements, `manque` vaut par exemple `{3: 1}` et la fonction lève `ValueError`. Sans cette garde, le NDCG pourrait dépasser 1.
- `idcg = dcg_at_k(sorted(rels_tous_juges, reverse=True), k, gain)` : c'est la correction du bug. On trie **toutes** les notes jugées par ordre décroissant, puis `dcg_at_k` ne garde que les `k` premières. Sur l'exemple, le tri donne `[3, 3, 2, 1, 1, 0, 0]` et l'IDCG vaut 13,7340.
- `if idcg == 0.0: return None` : aucun document pertinent n'a été jugé, le NDCG n'est pas défini.
- `return dcg_at_k(rels_retrouves, k, gain) / idcg` : 11,8389 / 13,7340, soit environ 0,8620.

**`notes_retrouvees(retrouves, jugements)`** transforme la liste d'identifiants renvoyée par le moteur en liste de notes : `dict.fromkeys` dédoublonne en gardant l'ordre (convention de l'étape 26), et `jugements.get(d, 0)` donne 0 à un document que personne n'a jugé.

**`ancien_ndcg(relevances, k)`** est l'ancien code du fichier, gardé uniquement pour les contre-exemples.

**`main()`**, bloc par bloc.

1. Les notes de la liste retrouvée sont lues dans le dictionnaire `jugements` : `[3, 1, 2, 0, 3]`. La boucle affiche et vérifie chaque contribution ; on vérifie ensuite DCG@5 = 11,8389, IDCG@5 = 13,7340 et NDCG@5 = 0,8620, ainsi que les remises citées au point 2 et w₁₀ ≈ 0,289.
2. Les deux contre-exemples du point 1 : l'ancien code annonce 1,0 les deux fois, le code corrigé donne 0,4693 et 0,6885. Les DCG et IDCG intermédiaires (2,1309, 8,8928, 12,9165) sont vérifiés, et l'on constate que l'ancien code aurait donné 0,887 sur l'exemple immobilier.
3. `permutations(tous, 5)` énumère les 2 520 façons de ranger cinq des sept documents jugés ; le meilleur DCG trouvé est exactement l'IDCG. Remettre dans l'ordre les rangs 2 et 3 rapporte 0,2619, la valeur (gⱼ − gᵢ)(wᵢ − wⱼ) du point 2, et les remises sont vérifiées strictement décroissantes jusqu'au rang 20.
4. En binaire, les deux gains coïncident. Sur `[2, 0, 0]` contre `[1, 1, 1]`, le gain exponentiel et le gain linéaire ne classent pas les deux moteurs dans le même ordre, avec les IDCG 4,1309 et 3,1309 du point 3.
5. La suite NDCG@1, NDCG@2, NDCG@3 de `[3, 0, 3]` vaut 1,0, puis 0,6131, puis 0,9197. La petite fonction `dcg_base10` recalcule le NDCG de l'exemple avec des logarithmes décimaux : il ne change pas.
6. Une question sans pertinent jugé donne `None`. Une note retrouvée absente des jugements, `k = 0` et une note négative lèvent `ValueError`, et le compteur `refus` vérifie que les trois refus ont bien eu lieu.
7. Les valeurs citées dans les cas d'usage ci-dessous sont recalculées et vérifiées.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`gain_exponentiel(rel)`** — On peut voir cette fonction comme le barème d'un concours de cuisine où chaque étoile supplémentaire vaut bien plus que la précédente : elle reçoit une note de pertinence entière et renvoie 2 élevé à cette note, moins 1, soit 0, 1, 3 et 7 pour les notes 0, 1, 2 et 3. Ce barème récompense lourdement les documents excellents, si bien qu'un document noté 3 en tête vaut à lui seul plus que trois documents notés 1 ; c'est le gain par défaut de `dcg_at_k` et de `ndcg_at_k`, celui que le programme utilise partout sauf au point 4.

**`gain_lineaire(rel)`** — Voici le barème plus modeste d'un jury qui compte chaque étoile pour ce qu'elle est : la fonction reçoit la même note et la renvoie telle quelle, sans aucune transformation, de sorte qu'un document noté 2 vaut exactement deux documents notés 1. Pour les notes 0 et 1, elle coïncide avec `gain_exponentiel` ; au-delà, les deux barèmes divergent, et `main` montre au point 4 qu'ils peuvent inverser le verdict entre deux moteurs, la liste [2, 0, 0] l'emportant avec le gain exponentiel (0,7262 contre 0,5158) mais perdant avec le gain linéaire (0,6388 contre 0,6806).

**`dcg_at_k(rels, k, gain)`** — Cette fonction est le caissier qui additionne la valeur des documents servis, en accordant une remise d'autant plus forte que le document arrive tard dans la liste : elle reçoit la liste des notes dans l'ordre du classement, la profondeur k et la fonction de gain, `gain_exponentiel` par défaut, lève `ValueError` si k est inférieur à 1 ou si une note est négative, puis garde les k premières notes, numérote leurs rangs à partir de 1 et additionne, pour chacune, le gain multiplié par `remise(i)`. Elle renvoie ce total ; sur [3, 1, 2, 0, 3], les contributions 7, 0,6309, 1,5, 0 et 2,7080 donnent un DCG@5 de 11,8389.

**`ndcg_at_k(rels_retrouves, rels_tous_juges, k, gain)`** — Elle compare le repas servi au meilleur repas qu'on aurait pu servir avec tous les plats disponibles en cuisine : la fonction reçoit les notes de la liste retrouvée, les notes de tous les documents jugés, la profondeur k et le gain, vérifie d'abord avec deux `Counter` que la liste retrouvée ne contient pas plus de documents pertinents d'une note donnée que les jugements, sans quoi elle lève `ValueError`, puis calcule l'IDCG en triant toutes les notes jugées par ordre décroissant. Elle renvoie `None` si cet IDCG est nul, faute de document pertinent, et sinon le rapport du DCG de la liste retrouvée à l'IDCG, soit 11,8389 / 13,7340 ≈ 0,8620 sur l'exemple immobilier.

**`notes_retrouvees(retrouves, jugements)`** — C'est le traducteur qui transforme la liste d'identifiants rendue par le moteur en une liste de notes que les autres fonctions savent compter : elle reçoit la liste des identifiants retrouvés et le dictionnaire des jugements, dédoublonne la liste avec `dict.fromkeys` en gardant le premier rang de chaque document, puis remplace chaque identifiant par sa note, en donnant 0 à un document que personne n'a jugé. Elle renvoie la liste des notes, [3, 1, 2, 0, 3] pour les cinq biens retrouvés de l'exemple, qui sert ensuite d'entrée à `dcg_at_k` et à `ndcg_at_k`.

**`ancien_ndcg(relevances, k)`** — Cette fonction est le témoin de l'ancienne erreur, un juge qui comparerait chaque candidat à lui-même : elle reçoit la seule liste des notes retrouvées et k, calcule le DCG avec la remise écrite log₂(i + 2) à partir d'un rang 0, puis tire l'idéal de cette même liste triée, au lieu de le tirer de tous les documents jugés. Elle renvoie leur rapport, ou 0,0 si l'idéal est nul ; comme l'idéal ignore les pertinents oubliés par le moteur, elle annonce 1,0 pour [1, 0, 0] alors que deux pertinents manquent, là où le calcul corrigé donne 0,4693, et 0,887 au lieu de 0,8620 sur l'exemple immobilier.

**`dcg_base10(notes)`** — Cette petite fonction interne, définie à l'intérieur de `main`, sert d'expérience de contrôle : elle reçoit une liste de notes et recalcule le DCG de ses cinq premiers éléments, toujours avec le gain exponentiel, mais en divisant par le logarithme décimal log₁₀(i + 1) au lieu du logarithme de base 2. Elle renvoie ce DCG en base 10 ; comme changer de base multiplie toutes les remises par la même constante, le rapport DCG / IDCG reste identique, et `main` vérifie qu'il redonne exactement le NDCG de l'exemple, à 10⁻¹² près.

**`main()`** — Le chef d'orchestre déroule sept vérifications : il lit les notes des biens retrouvés, affiche chaque contribution et vérifie DCG@5 = 11,8389, IDCG@5 = 13,7340 et NDCG@5 = 0,8620, puis montre sur deux contre-exemples que l'ancien code annonce 1,0 là où le calcul corrigé donne 0,4693 et 0,6885. Il énumère ensuite les 2 520 rangements de cinq des sept documents pour constater qu'aucun ne dépasse l'IDCG, mesure le gain de 0,2619 obtenu en remettant deux rangs dans l'ordre, oppose les gains exponentiel et linéaire, montre que le NDCG n'est pas monotone en k (1,0, puis 0,6131, puis 0,9197), vérifie les cas de bord et recalcule les cinq valeurs des cas d'usage. Chaque nombre est gardé par un `assert`, et la ligne finale n'annonce le succès que si tous ont tenu.

```python
"""Étape 28 — NDCG : IDCG calculé sur TOUS les documents jugés, inégalité de réarrangement, gain 2^rel − 1."""
import math
import sys
from collections import Counter
from itertools import permutations

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def remise(i: int) -> float:
    """Facteur de remise du rang i (compté à partir de 1) : 1 / log2(i + 1)."""
    return 1.0 / math.log2(i + 1)


def gain_exponentiel(rel: int) -> float:
    """Gain 2^rel − 1 : 0 → 0, 1 → 1, 2 → 3, 3 → 7."""
    return 2 ** rel - 1


def gain_lineaire(rel: int) -> float:
    """Gain linéaire : la note elle-même."""
    return rel


def dcg_at_k(rels: list[int], k: int, gain=gain_exponentiel) -> float:
    """DCG@k = somme, pour i de 1 à k, de gain(rel_i) / log2(i + 1)."""
    if k < 1:
        raise ValueError("k doit être un entier >= 1")
    if any(r < 0 for r in rels):
        raise ValueError("une note de pertinence est un entier >= 0")
    return sum(gain(rel) * remise(i) for i, rel in enumerate(rels[:k], start=1))


def ndcg_at_k(rels_retrouves: list[int], rels_tous_juges: list[int], k: int, gain=gain_exponentiel) -> float | None:
    """NDCG@k = DCG@k de la liste retrouvée / IDCG@k ; l'IDCG vient de TOUS les documents jugés, triés."""
    manque = Counter(r for r in rels_retrouves if r > 0) - Counter(r for r in rels_tous_juges if r > 0)
    if manque:
        raise ValueError(f"notes retrouvées absentes des jugements : {dict(manque)}")
    idcg = dcg_at_k(sorted(rels_tous_juges, reverse=True), k, gain)
    if idcg == 0.0:
        return None                                   # aucun document pertinent jugé : NDCG indéfini
    return dcg_at_k(rels_retrouves, k, gain) / idcg


def notes_retrouvees(retrouves: list[str], jugements: dict[str, int]) -> list[int]:
    """Note de chaque document retrouvé, après dédoublonnage ; 0 pour un document non jugé."""
    return [jugements.get(d, 0) for d in dict.fromkeys(retrouves)]


def ancien_ndcg(relevances: list[int], k: int) -> float:
    """Ancienne version du fichier : l'« idéal » est tiré de la liste RETROUVÉE elle-même."""
    dcg = sum((2 ** rel - 1) / math.log2(i + 2) for i, rel in enumerate(relevances[:k]))
    ideal = sorted(relevances, reverse=True)
    idcg = sum((2 ** rel - 1) / math.log2(i + 2) for i, rel in enumerate(ideal[:k]))
    return dcg / idcg if idcg > 0 else 0.0


def main() -> None:
    print("1. Comparables notés de 0 à 3, k = 5")
    jugements = {"jvc-2ch-1120": 3, "jvc-2ch-1050": 3, "jvc-2ch-980": 2, "jvc-1ch-760": 1,
                 "jvt-2ch-1100": 1, "villa-jvc": 0, "bureau-jlt": 0}
    retrouves = ["jvc-2ch-1120", "jvt-2ch-1100", "jvc-2ch-980", "villa-jvc", "jvc-2ch-1050"]
    rels = notes_retrouvees(retrouves, jugements)
    tous = list(jugements.values())
    assert rels == [3, 1, 2, 0, 3]
    attendu = [7.0, 0.6309, 1.5, 0.0, 2.708]
    for i, (doc, rel) in enumerate(zip(retrouves, rels), start=1):
        c = gain_exponentiel(rel) * remise(i)
        print(f"  rang {i}  {doc:<13} note {rel}  gain {gain_exponentiel(rel)}  remise {remise(i):.4f}  contribution {c:.4f}")
        assert round(c, 4) == attendu[i - 1]
    dcg = dcg_at_k(rels, 5)
    idcg = dcg_at_k(sorted(tous, reverse=True), 5)
    ndcg = ndcg_at_k(rels, tous, 5)
    print(f"  DCG@5 = {dcg:.4f} ; IDCG@5 = {idcg:.4f} (idéal {sorted(tous, reverse=True)[:5]}) ; NDCG@5 = {ndcg:.4f}")
    assert (round(dcg, 4), round(idcg, 4), round(ndcg, 4)) == (11.8389, 13.734, 0.862)
    assert [round(remise(i), 4) for i in range(1, 6)] == [1.0, 0.6309, 0.5, 0.4307, 0.3869]
    assert round(remise(10), 3) == 0.289

    print("2. Le bug de l'ancien IDCG, calculé sur la liste retrouvée")
    a1, n1 = ancien_ndcg([1, 0, 0], 3), ndcg_at_k([1, 0, 0], [1, 1, 1], 3)
    a2, n2 = ancien_ndcg([3, 2, 0], 3), ndcg_at_k([3, 2, 0], [3, 3, 2, 1], 3)
    print(f"  [1, 0, 0] avec 3 pertinents : ancien = {a1:.4f} ; corrigé = {n1:.4f}")
    print(f"  [3, 2, 0] face aux jugements [3, 3, 2, 1] : ancien = {a2:.4f} ; corrigé = {n2:.4f}")
    assert a1 == 1.0 and round(n1, 4) == 0.4693 and abs(n1 - 1 / (1 + remise(2) + remise(3))) < 1e-12
    assert a2 == 1.0 and round(n2, 4) == 0.6885 and round(ancien_ndcg(rels, 5), 4) == 0.887
    assert round(dcg_at_k([1, 1, 1], 3), 4) == 2.1309 and round(dcg_at_k([3, 2, 0], 3), 4) == 8.8928
    assert round(dcg_at_k([3, 3, 2, 1], 3), 4) == 12.9165

    print("3. Réarrangement : aucun des 2520 classements de 5 documents jugés ne dépasse l'IDCG")
    meilleur = max(dcg_at_k(list(p), 5) for p in permutations(tous, 5))
    echange = dcg_at_k([3, 2, 1, 0, 3], 5) - dcg                   # rangs 2 et 3 remis dans l'ordre
    print(f"  max DCG@5 = {meilleur:.4f} = IDCG@5 ; échanger les rangs 2 et 3 rapporte {echange:.4f} = (3 - 1)(w2 - w3)")
    assert abs(meilleur - idcg) < 1e-12 and len(list(permutations(tous, 5))) == 2520
    assert abs(echange - (3 - 1) * (remise(2) - remise(3))) < 1e-12 and round(echange, 4) == 0.2619
    assert all(remise(i) > remise(i + 1) for i in range(1, 20))     # remises strictement décroissantes

    print("4. Gain exponentiel ou linéaire")
    assert all(gain_exponentiel(r) == gain_lineaire(r) for r in (0, 1))   # en binaire, c'est le même gain
    juges = [2, 1, 1, 1]
    ea, eb = ndcg_at_k([2, 0, 0], juges, 3), ndcg_at_k([1, 1, 1], juges, 3)
    la, lb = ndcg_at_k([2, 0, 0], juges, 3, gain_lineaire), ndcg_at_k([1, 1, 1], juges, 3, gain_lineaire)
    print(f"  [2, 0, 0] contre [1, 1, 1] : exponentiel {ea:.4f} > {eb:.4f} ; linéaire {la:.4f} < {lb:.4f}")
    assert ea > eb and la < lb
    assert [round(v, 4) for v in (ea, eb, la, lb)] == [0.7262, 0.5158, 0.6388, 0.6806]
    assert round(dcg_at_k([2, 1, 1], 3), 4) == 4.1309 and round(dcg_at_k([2, 1, 1], 3, gain_lineaire), 4) == 3.1309

    print("5. NDCG@k n'est pas monotone en k ; la base du logarithme ne change rien")
    suite = [ndcg_at_k([3, 0, 3], [3, 3], k) for k in (1, 2, 3)]

    def dcg_base10(notes: list[int]) -> float:
        return sum(gain_exponentiel(r) / math.log10(i + 1) for i, r in enumerate(notes[:5], start=1))

    base10 = dcg_base10(rels) / dcg_base10(sorted(tous, reverse=True))
    print(f"  [3, 0, 3] face à [3, 3] : NDCG@1, @2, @3 = {[round(v, 4) for v in suite]} ; en base 10 : {base10:.4f}")
    assert [round(v, 4) for v in suite] == [1.0, 0.6131, 0.9197] and abs(base10 - ndcg) < 1e-12
    assert round(dcg_at_k([3, 3], 3), 4) == 11.4165

    print("6. Cas de bord")
    assert ndcg_at_k([0, 0, 0], [0, 0], 3) is None                    # aucun pertinent jugé : indéfini
    refus = 0
    for args in (([3, 3], [3], 2), ([1], [1], 0), ([-1], [1], 1)):
        try:
            ndcg_at_k(*args)
        except ValueError:
            refus += 1
    print(f"  aucun pertinent jugé → None ; note absente des jugements, k = 0, note négative → ValueError ({refus}/3)")
    assert refus == 3

    cas = {
        "immobilier": ndcg_at_k([3, 0, 0, 0, 0], tous, 5),
        "banque": ndcg_at_k([1, 2, 3, 0], [3, 2, 1], 4),
        "crypto": ndcg_at_k([1, 3, 0], [3, 1], 3),
        "RH": ndcg_at_k([1, 0, 3], [3, 2, 1], 3),
        "BTP": ndcg_at_k([2, 3, 1, 0, 0], [3, 2, 1, 1], 5),
    }
    print("7. Cas d'usage : " + " ; ".join(f"{nom} {v:.4f}" for nom, v in cas.items()))
    assert [round(v, 4) for v in cas.values()] == [0.5097, 0.6806, 0.7098, 0.4791, 0.8059]
    assert ancien_ndcg([3, 0, 0, 0, 0], 5) == 1.0 and ndcg_at_k([1, 1, 0], [1, 1], 3) == 1.0
    assert ndcg_at_k([3, 2, 1, 0], [3, 2, 1], 4) == 1.0 and ndcg_at_k([3, 2, 1], [3, 2, 1], 3) == 1.0
    assert round(ndcg_at_k([3, 2, 1, 0, 0], [3, 2, 1, 1], 5), 4) == 0.9562

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Comparables notés de 0 à 3, k = 5
  rang 1  jvc-2ch-1120  note 3  gain 7  remise 1.0000  contribution 7.0000
  rang 2  jvt-2ch-1100  note 1  gain 1  remise 0.6309  contribution 0.6309
  rang 3  jvc-2ch-980   note 2  gain 3  remise 0.5000  contribution 1.5000
  rang 4  villa-jvc     note 0  gain 0  remise 0.4307  contribution 0.0000
  rang 5  jvc-2ch-1050  note 3  gain 7  remise 0.3869  contribution 2.7080
  DCG@5 = 11.8389 ; IDCG@5 = 13.7340 (idéal [3, 3, 2, 1, 1]) ; NDCG@5 = 0.8620
2. Le bug de l'ancien IDCG, calculé sur la liste retrouvée
  [1, 0, 0] avec 3 pertinents : ancien = 1.0000 ; corrigé = 0.4693
  [3, 2, 0] face aux jugements [3, 3, 2, 1] : ancien = 1.0000 ; corrigé = 0.6885
3. Réarrangement : aucun des 2520 classements de 5 documents jugés ne dépasse l'IDCG
  max DCG@5 = 13.7340 = IDCG@5 ; échanger les rangs 2 et 3 rapporte 0.2619 = (3 - 1)(w2 - w3)
4. Gain exponentiel ou linéaire
  [2, 0, 0] contre [1, 1, 1] : exponentiel 0.7262 > 0.5158 ; linéaire 0.6388 < 0.6806
5. NDCG@k n'est pas monotone en k ; la base du logarithme ne change rien
  [3, 0, 3] face à [3, 3] : NDCG@1, @2, @3 = [1.0, 0.6131, 0.9197] ; en base 10 : 0.8620
6. Cas de bord
  aucun pertinent jugé → None ; note absente des jugements, k = 0, note négative → ValueError (3/3)
7. Cas d'usage : immobilier 0.5097 ; banque 0.6806 ; crypto 0.7098 ; RH 0.4791 ; BTP 0.8059
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un NDCG n'a de sens que si son idéal est construit sur tous les documents jugés. Avec ce bon IDCG, la borne [0, 1] devient un vrai théorème (réarrangement), et le choix du gain et de k devient une décision explicite.

## Squelette algorithmique

Le NDCG compare le gain cumulé du classement obtenu à celui du meilleur classement possible. Le point qui piège le plus souvent est l'IDCG : il se calcule à partir de tous les documents jugés, pas seulement de ceux qui ont été retrouvés.

```text
ALGORITHME NDCG@k
ENTRÉES : notes des documents retrouvés, dans l'ordre (rel₁ … rel_n), notes de TOUS les documents jugés, k
SORTIE  : NDCG@k dans [0 ; 1], ou « indéfini »

  FONCTION DCG(notes, k)
      RETOURNER Σ sur i=1..min(k, longueur) (2^(notes[i]) − 1) / log₂(i + 1)
  SI une note retrouvée n'existe pas dans les jugements ALORS ERREUR
  IDCG ← DCG(notes de tous les jugés triées par ordre décroissant, k)
  SI IDCG = 0 ALORS RETOURNER « indéfini »             (aucun document pertinent jugé)
  RETOURNER DCG(notes retrouvées, k) / IDCG
```

**Complexité.** Le DCG coûte O(k). L'IDCG demande de trier les J notes jugées : O(J log J), ou O(J) avec un comptage, puisque les notes sont de petits entiers. La vérification de cohérence entre notes retrouvées et jugements coûte O(n + J) avec des compteurs.

**Du squelette au code.** `remise` est le facteur 1 / log₂(i + 1), `gain_exponentiel` et `gain_lineaire` les deux formes du gain, `dcg_at_k` la fonction DCG, `ndcg_at_k` l'algorithme complet avec sa garde et son cas indéfini, et `notes_retrouvees` traduit une liste de documents en liste de notes. `ancien_ndcg` reproduit l'ancienne version, qui calculait l'IDCG à partir des seuls documents retrouvés.

## Cas d'usage réels aux Émirats

Les notes, seuils et valeurs de NDCG ci-dessous sont illustratifs : en production, on les mesure sur des jugements d'experts propres à chaque métier.

### Immobilier — des comparables notés de 0 à 3

Une agence immobilière qui opère à Dubaï et à Abu Dhabi fait préparer ses estimations par un agent qui s'appuie sur les cinq meilleurs comparables de son historique de transactions, chacun décrit par son quartier, son type, sa surface en sqft, sa date et son prix en AED/sqft. Les notes de 0 à 3 de la démonstration (même quartier et même type, surface et date proches, et ainsi de suite) se lisent dans les métadonnées : l'agent peut donc noter automatiquement chaque transaction et calculer un NDCG@5 à chaque requête, tandis qu'un expert vérifie les notes par sondage. Sur la requête de la démonstration, le NDCG@5 vaut 0,862 : la liste est bonne, mais un comparable noté 1 manque et un comparable noté 3 n'arrive qu'au cinquième rang. Le cas dangereux est une liste qui commence par un excellent comparable puis enchaîne quatre biens non comparables : l'ancien code lui donnait 1, parce que la liste [3, 0, 0, 0, 0] est déjà triée, alors que le NDCG corrigé vaut 0,5097 face aux sept transactions jugées. L'agent applique une règle simple : sous 0,8, il élargit la recherche dans le même quartier et reclasse ; si cela ne suffit pas, il présente l'estimation comme peu fiable, avec le nombre de comparables utilisés. Une estimation produite par un agent reste indicative et ne remplace pas une évaluation officielle, d'autant que l'acheteur paiera en plus 4 % de frais de transfert au DLD sur le prix. On suit le NDCG@5 moyen par quartier et l'écart médian entre l'estimation et le prix final de vente.

### Banque — la règle avant le résumé

Une banque de détail de Dubaï note les sources de son assistant de conformité selon leur autorité : 3 pour le texte de la règle de la CBUAE, 2 pour la politique interne qui l'applique, 1 pour la FAQ interne qui la résume, 0 pour un passage sans rapport. Pour la question « quel ratio d'endettement maximal pour un client retraité ? », le moteur renvoie la FAQ, puis la politique interne, puis la règle, puis un passage hors sujet, soit les notes [1, 2, 3, 0]. La Precision@4 vaut 0,75 et le Recall@4 vaut 1, exactement comme pour le classement idéal [3, 2, 1, 0] : ces deux métriques ne voient pas que l'ordre est inversé. Le NDCG@4, lui, tombe à 0,6806 contre 1 pour l'ordre idéal, parce que la règle, qui vaut un gain de 7, n'arrive qu'au troisième rang. Or le modèle s'appuie surtout sur le premier passage, et une FAQ peut être en retard sur la règle : l'équipe fait donc remonter les sources primaires par le reranker, et refuse de répondre sans citer la règle elle-même quand la question porte sur un plafond. Le plafond en jeu, 30 % du revenu pour un retraité contre 50 % dans le cas général, est fixé par la CBUAE, et une réponse fondée sur un résumé périmé exposerait la banque à une erreur de conformité. On suit le NDCG@4 hebdomadaire sur un échantillon annoté et la part des réponses qui citent la source primaire.

### Crypto — la version en vigueur avant l'ancienne

Une plateforme d'actifs virtuels agréée par la VARA conserve dans sa base documentaire les versions successives de ses procédures internes, par exemple sa politique de limites de retrait. Les jugements notent 3 la section de la version en vigueur et 1 la section de la version remplacée, encore utile pour comprendre l'historique d'un dossier. Pour une question d'analyste, le moteur renvoie l'ancienne version en tête, la version en vigueur ensuite, puis un passage hors sujet : [1, 3, 0], d'où un NDCG@3 de 0,7098. Avec des jugements binaires, où les deux versions seraient simplement « pertinentes », la même liste [1, 1, 0] obtiendrait 1 et le problème resterait invisible : c'est la pertinence graduée qui révèle l'inversion. L'équipe ajoute un attribut « en vigueur » aux morceaux, l'utilise pour reclasser, et bloque tout déploiement qui fait passer le NDCG@3 sous 0,9 sur le jeu d'évaluation. Une plateforme agréée doit appliquer et communiquer ses règles en vigueur, et une limite périmée annoncée à un client est un incident de conformité. On suit le NDCG@3 par famille de procédures et le nombre de réponses qui citent une version remplacée.

### Assurance — la clause qui décide en tête

Un assureur auto et santé fait instruire les sinistres par un agent qui lit les clauses du contrat de l'assuré. Les gestionnaires ont noté un jeu de 300 sinistres : 3 pour la garantie qui s'applique, 2 pour l'exclusion ou la franchise pertinente, 1 pour une définition générale du contrat, 0 pour une clause d'un autre produit. Quand la description du sinistre est longue, l'agent ne garde que les trois premières clauses pour tenir dans son budget de tokens : une garantie classée cinquième disparaît alors du contexte, et l'agent conclut à tort à une absence de couverture. Le NDCG@5 moyen, de 0,74 avec le cosinus seul, passe à 0,91 après l'ajout d'un reranker entraîné sur les jugements des gestionnaires. Sans pertinence graduée, une définition générale bien classée aurait compté autant que la garantie elle-même, et le problème de coupure serait passé inaperçu. L'assurance est supervisée par la CBUAE, et une décision de refus doit pouvoir être justifiée par la clause applicable. On suit le NDCG@3, qui correspond à ce que l'agent garde vraiment, et le NDCG@5 par ligne de produit.

### BTP — la spécification du projet avant le standard du groupe

Un groupe de construction qui mène de grands chantiers à Dubaï fait répondre ses ingénieurs de site par un agent qui cherche dans les documents techniques. Les jugements notent 3 la section de la spécification approuvée du projet, 2 la spécification standard du groupe, 1 une fiche technique de fabricant, 0 le document d'un autre projet. Pour une question sur l'enrobage minimal des armatures d'un lot de fondations, le moteur renvoie d'abord la spécification standard, puis celle du projet, puis une fiche de fabricant et deux documents hors sujet : [2, 3, 1, 0, 0] face aux jugements [3, 2, 1, 1], soit un NDCG@5 de 0,8059. Remettre la spécification du projet en tête donne 0,9562 ; le score reste sous 1 parce qu'une seconde fiche de fabricant n'a pas été retrouvée. L'enjeu est concret : si la valeur du standard diffère de celle du projet approuvé, l'ingénieur qui suit la première source s'écarte du document contractuel, ce qui crée une non-conformité à reprendre sur le chantier. L'équipe ajoute l'identifiant du projet aux métadonnées et le donne au reranker, puis suit le NDCG@5 par projet et la part des réponses qui citent la spécification du projet.

### RH — la règle légale avant le guide général

Un cabinet RH présent dans plusieurs émirats répond aux questions des salariés sur leurs congés et leur fin de service. Les jugements notent 3 la règle légale applicable au régime du salarié (pour le secteur privé fédéral, le décret-loi fédéral 33/2021), 2 la politique interne de l'employeur, 1 un guide général, 0 un passage d'un autre régime, comme celui du DIFC. Pour une question sur l'indemnité de fin de service, le moteur renvoie le guide général, puis un passage du régime du DIFC, puis la règle légale : [1, 0, 3] face aux jugements [3, 2, 1], soit un NDCG@3 de 0,4791. Après un filtre par régime et un reclassement, la liste devient [3, 2, 1] et le NDCG@3 vaut 1. Sans cette mesure, le cabinet aurait seulement constaté que la règle légale figurait dans le top-3, sans voir qu'elle arrivait derrière un passage d'un autre régime que le modèle pouvait reprendre. Une indemnité mal calculée crée un litige avec le salarié, et toute réponse automatique reste à confirmer avec le texte en vigueur. On suit le NDCG@3 par régime (secteur privé fédéral, DIFC, ressortissants émiriens) et le taux d'écart entre les montants annoncés et ceux de la paie.

## Pièges et limites

- **Calculer l'IDCG sur la liste retrouvée** : c'était le bug de l'ancien code. Un moteur qui ne trouve qu'un pertinent sur trois obtenait 1 (point 1).
- **Oublier les documents non jugés** : comme pour la Precision@k, un document que personne n'a noté compte 0. Un nouveau moteur qui remonte de bons documents jamais jugés paraît moins bon ; on fait noter les nouveaux documents du top-k avant de conclure.
- **Mélanger les conventions** : un NDCG à gain linéaire et un NDCG à gain exponentiel, ou un NDCG@5 et un NDCG@10, ne se comparent pas. On écrit toujours le gain et k à côté du chiffre.
- **Compter 0 pour une question sans pertinent** : l'IDCG est nul, le NDCG est indéfini ; renvoyer 0 fausse la moyenne (point 5).
- **Croire qu'un NDCG élevé suffit** : il dit que l'ordre est bon, pas que la réponse générée est fidèle aux sources ; c'est le rôle de la Faithfulness (étape 54).

### Exercice feuille blanche

1. Sans regarder le code, écrire `dcg_at_k` et `ndcg_at_k` avec un IDCG calculé sur tous les documents jugés, puis retrouver 0,469 pour la liste [1, 0, 0] quand trois documents sont pertinents.
2. Prédire, puis vérifier : avec les jugements binaires [1, 1] et la liste [0, 1], que vaut le NDCG@2 ? (Réponse : 0,6309/1,6309 ≈ 0,387.)
3. Trouver le bug : `idcg = dcg_at_k(sorted(rels_retrouves, reverse=True), k)`. Que renvoie cette version pour la liste [0, 0, 1] face aux jugements [1, 1, 1], et que devrait-elle renvoyer ? (Réponse : 0,5/1 = 0,5 au lieu de 0,5/2,1309 ≈ 0,235.)

## Pour aller plus loin

- **Origine** : le gain cumulé actualisé a été proposé par Järvelin et Kekäläinen (2002), avec un gain linéaire. La forme 2ʳᵉˡ − 1 s'est imposée ensuite avec les travaux d'apprentissage du classement (learning to rank), qui optimisent directement le NDCG pour entraîner des rerankers.
- **ERR** (Expected Reciprocal Rank) : le pendant gradué du MRR de l'étape 27, qui modélise un lecteur qui s'arrête au premier document qui le satisfait.
- **NDCG et MAP** : la précision moyenne (étape 61) traite une pertinence binaire et pénalise chaque pertinent manquant ; le NDCG accepte des notes et une remise choisie.

> Suite : [Exemples de RAG de bout en bout](<29-RAG-Exemples-Cas-Usage.md>) — étape 29.
