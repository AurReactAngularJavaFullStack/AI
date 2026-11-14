# Étape 30 quater — RAG — Découpage avancé, contextual retrieval et compression

> Étape 30 quater du parcours · Prérequis : [Transformations de requête](<30c-RAG-Transformations-de-Requete.md>) · Suite : [Index ANN : HNSW, IVF, PQ](<30e-RAG-Index-ANN-HNSW-IVF-PQ.md>)

**Dossier :** 05-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  
**Nom du fichier :** 30d-RAG-Decoupage-Avance-et-Compression.md

## Définition

Le découpage (chunking) coupe chaque document en morceaux, qui sont à la fois l'unité que l'on indexe et l'unité que l'on renvoie au modèle : une règle coupée en deux n'est entière dans aucun morceau, et le modèle ne la lira jamais en entier (étape 18). Quatre stratégies dominent. Le découpage à **taille fixe** prend des fenêtres de c mots (ou tokens), chacune reprenant les o derniers mots de la précédente, c'est le recouvrement. Le découpage **récursif** coupe d'abord aux séparateurs les plus forts (paragraphes), puis, seulement pour les pièces trop longues, aux plus faibles (lignes, phrases, mots), et regroupe les pièces voisines tant qu'elles tiennent dans c mots. Le découpage **sémantique** coupe entre deux phrases voisines quand le cosinus de leurs vecteurs passe sous un seuil τ. Le découpage **parent-enfant** indexe de petits morceaux, précis à retrouver, et renvoie au modèle le grand morceau, l'article ou la section, qui les contient. Deux techniques complètent le découpage : le **contextual retrieval**, qui préfixe chaque morceau par le contexte de son document (titre, section, ou résumé écrit par un modèle) avant de l'indexer, et la **compression contextuelle**, qui, après la recherche, ne garde des passages retrouvés que les phrases utiles à la question.

## Rôle dans un agent

Le découpage et le préfixe de contexte se font **hors ligne**, dans le pipeline d'ingestion qui construit l'index : ils décident une fois pour toutes de ce que la recherche pourra trouver. Le passage de l'enfant au parent et la compression se font **en ligne**, dans l'outil de recherche, entre l'action « chercher » et l'observation que l'agent reçoit. Ils décident de la place que les sources occupent dans le contexte, ressource limitée et payée au token (étape 13 ter, [budget de contexte](<../04-Contexte-Similarite-et-Memoire/13c-Contexte-Definitions-Fondamentaux.md>)). Un mauvais découpage se voit rarement dans le code : la recherche « marche », mais la phrase qui porte la réponse est coupée, ou elle arrive sans le sujet qui lui donne son sens, et l'agent répond à côté. En architecture hexagonale, le découpeur est un port (texte → liste de morceaux avec leurs métadonnées) et le compresseur un autre (question, passages → passages réduits) ; on les change sans toucher au moteur de recherche ni à la boucle de l'agent, et on les compare sur le même jeu de questions.

## Équation complète

Taille fixe : c mots par morceau, recouvrement o, pas p = c − o, texte de L mots ; nombre de morceaux, démontré au point 1 :

$$
n = \max\left(1,\; \left\lceil \frac{L - o}{c - o} \right\rceil\right) \qquad 0 \le o < c,\quad L \ge 1
$$

Mots indexés et surcoût du recouvrement (point 2) :

$$
W = L + (n - 1)\, o \qquad \frac{W}{L} \xrightarrow[L \to \infty]{} \frac{c}{c - o}
$$

Garantie du recouvrement (point 3) : toute suite de ℓ mots consécutifs est entière dans au moins un morceau dès que

$$
\ell \le o + 1
$$

et aucune suite de plus de c mots ne peut l'être.

Découpage sémantique : coupure entre les phrases i et i + 1, et nombre de morceaux (point 5) :

$$
\text{coupure}(i) \iff \cos(v_i, v_{i+1}) < \tau \qquad n(\tau) = 1 + \big|\{\, i : \cos(v_i, v_{i+1}) < \tau \,\}\big|
$$

Parent-enfant : on retrouve k enfants, on renvoie leurs parents distincts ; mots envoyés au modèle :

$$
M_{PE} = \sum_{P \in \text{parents}(e_1, \dots, e_k)} |P| \;\le\; k \cdot \max_P |P|
$$

Contextual retrieval : on indexe le contexte concaténé au morceau, ce qui ajoute à l'index la longueur des préfixes :

$$
\text{index}(m) = \text{contexte}(m) \oplus m \qquad W_{ctx} = W + \sum_{m} |\text{contexte}(m)|
$$

Compression extractive : on garde les phrases s d'un passage P qui partagent au moins θ termes avec la question, et l'on note le taux de compression :

$$
C_\theta(q, P) = \{\, s \in P : |T(q) \cap T(s)| \ge \theta \,\} \qquad \rho = \frac{|C_\theta(q, P)|}{|P|}
$$

## Décryptage des symboles

$$
L
$$

**Sens :** longueur du texte à découper, en mots (un proxy des tokens) · **Type / plage :** entier ≥ 1 · **Variable Python :** `L = len(mots(texte))`

$$
c,\; o,\; p
$$

**Sens :** taille d'un morceau, recouvrement entre deux morceaux voisins, pas entre deux débuts de morceau · **Type / plage :** entiers, 0 ≤ o < c, p = c − o ≥ 1 · **Variable Python :** `taille`, `recouvrement`, `pas`

$$
n
$$

**Sens :** nombre de morceaux produits · **Type / plage :** entier ≥ 1 · **Variable Python :** `nombre_morceaux(L, c, o)`

$$
W
$$

**Sens :** nombre total de mots stockés dans l'index, recouvrements compris · **Type / plage :** entier ≥ L · **Variable Python :** `sum(len(x) for x in morceaux)`

$$
\ell
$$

**Sens :** longueur d'une suite de mots qui doit rester entière, par exemple une règle · **Type / plage :** entier ≥ 1 · **Variable Python :** `len(mots(fait))`

$$
v_i,\; \tau
$$

**Sens :** vecteur de la phrase i, et seuil de coupure du découpage sémantique · **Type / plage :** vecteur ; réel dans [0, 1] · **Variable Python :** `vecteur(phrase, vocabulaire)`, `seuil`

$$
e_1, \dots, e_k,\; P
$$

**Sens :** les k enfants retrouvés, et un parent, l'article qui les contient · **Type / plage :** phrases ; texte · **Variable Python :** `index_phrases.chercher(q, k)`, `vers_parents(...)`

$$
M_{PE}
$$

**Sens :** nombre de mots envoyés au modèle par le parent-enfant · **Type / plage :** entier · **Variable Python :** second élément renvoyé par `evaluer`

$$
\text{contexte}(m),\; \oplus
$$

**Sens :** le préfixe de contexte du morceau m (document et article), et la concaténation · **Type / plage :** chaîne · **Variable Python :** `prefixe` dans `morceaux_recursifs(..., contexte=True)`

$$
T(\cdot),\; \theta,\; \rho
$$

**Sens :** ensemble des termes d'un texte (mots vides retirés), seuil de la compression, taux de compression · **Type / plage :** ensemble ; entier ≥ 1 ; réel dans [0, 1] · **Variable Python :** `set(termes(...))`, `seuil`, mots gardés / mots du parent

## Démonstration

Le programme découpe un règlement intérieur fictif de 259 mots, en cinq articles : période d'essai, salaires, indemnité de fin de service, congés, visa et permis de travail. L'article 3 reprend les règles du décret-loi fédéral 33/2021 pour le secteur privé (au moins un an de service, 21 jours de salaire de base par année pendant cinq ans, 30 jours au-delà, plafond de 24 mois, salaire journalier égal au salaire de base divisé par 30) ; le reste est inventé pour l'exemple. Huit questions ont chacune une phrase réponse, qui doit arriver **entière** dans le contexte renvoyé au modèle ; c'est le critère de réussite.

### 1. Le nombre de morceaux d'un découpage à taille fixe

Les morceaux commencent aux positions 0, p, 2p, …, et le j-ième (en comptant à partir de 0) couvre les mots de jp à jp + c − 1. Le découpage s'arrête au premier morceau qui atteint la fin du texte, c'est-à-dire au plus petit j tel que jp + c ≥ L. Si L ≤ c, c'est j = 0 et il y a un seul morceau. Sinon,

$$
jp + c \ge L \iff j \ge \frac{L - c}{p} ,
$$

donc le plus petit j vaut ⌈(L − c)/p⌉, et le nombre de morceaux vaut ce j plus 1 :

$$
n = \left\lceil \frac{L - c}{p} \right\rceil + 1 = \left\lceil \frac{L - c + p}{p} \right\rceil = \left\lceil \frac{L - o}{c - o} \right\rceil
$$

La deuxième égalité vient de ce que ⌈x⌉ + 1 = ⌈x + 1⌉, la troisième de ce que c − p = o. Dans le cas L ≤ c, la formule donne encore 1 quand o < L, et une valeur nulle ou négative quand L ≤ o ; le max(1, ·) couvre ces deux cas. Pour le règlement, avec c = 20 et o = 5 : ⌈(259 − 5)/15⌉ = ⌈16,93⌉ = 17 morceaux. Le programme vérifie la formule sur toutes les combinaisons L ≤ 60, c ≤ 12 et o < c.

### 2. Le coût du recouvrement

Tous les morceaux sauf le dernier ont c mots ; le dernier couvre ce qui reste après les n − 1 premiers débuts, soit L − (n − 1)p mots. En additionnant :

$$
W = (n - 1)\,c + L - (n - 1)\,p = L + (n - 1)(c - p) = L + (n - 1)\,o
$$

Chaque frontière entre deux morceaux stocke o mots en double, et il y a n − 1 frontières. Avec c = 20 et o = 5, l'index stocke 259 + 16 × 5 = 339 mots, soit 30,9 % de plus que le texte. Quand L grandit, n − 1 ≈ L/p et W/L tend vers 1 + o/(c − o) = c/(c − o) : 20/15 ≈ 1,333, soit un surcoût asymptotique de 33,3 %. On paie ce surcoût trois fois : en stockage, en calcul d'embeddings à l'indexation, et en doublons possibles dans le contexte quand deux morceaux voisins sont renvoyés ensemble.

### 3. Ce que le recouvrement garantit, et ce qu'il ne garantit pas

Prenons une suite de ℓ mots qui commence à la position a, avec ℓ ≤ o + 1, et le morceau j = ⌊a/p⌋, qui commence au plus tard en a puisque jp ≤ a. Ce morceau se termine en jp + c = (j + 1)p + o. Comme a < (j + 1)p, on a a + ℓ − 1 ≤ a + o < (j + 1)p + o : le dernier mot de la suite tombe avant la fin du morceau, qui la contient donc entière. Le dernier morceau va jusqu'à la fin du texte, ce qui couvre le cas où ce j n'existe pas. Avec c = 20 et o = 5, toute suite de 6 mots tient dans un morceau, et le programme le vérifie sur les 254 suites de 6 mots du règlement ; 16 suites de 7 mots, en revanche, sont coupées. À l'autre extrême, une suite de plus de c mots ne tient jamais dans un morceau de c mots : la phrase des 21 jours compte 22 mots, et aucun découpage de taille 20, fixe ou récursif, ne peut la renvoyer entière. Deux règles pratiques en découlent : c doit dépasser la plus longue unité qui doit rester entière, et le recouvrement ne protège que les unités courtes ; pour le reste, il faut couper aux frontières naturelles du texte.

### 4. Le récursif respecte la structure, dans la limite de c

Le découpeur récursif coupe d'abord aux paragraphes, puis aux lignes, aux fins de phrase et enfin aux espaces. Chaque morceau renvoyé tient dans c mots, parce qu'une pièce n'est ajoutée telle quelle que si elle tient, et qu'une pièce trop longue est redécoupée avec un séparateur plus fin, jusqu'à l'espace, qui donne des pièces d'un mot ; le programme le vérifie pour c = 5, 10, 20, 30 et 40. Sur l'article 3, dont les phrases font 19, 22, 15, 13 et 13 mots, c = 20 donne des morceaux de [19, 20, 2, 15, 13, 13] mots : la phrase de 22 mots est coupée en 20 + 2, et le morceau de 2 mots ne sert à rien. Avec c = 30, on obtient [19, 22, 28, 13] : chaque phrase reste entière, et les deux phrases de 15 et 13 mots sont regroupées.

### 5. Le découpage sémantique : plus de coupures quand τ monte

L'ensemble des coupures est {i : cos(vᵢ, vᵢ₊₁) < τ}. Si τ ≤ τ′, toute frontière qui vérifie cos < τ vérifie aussi cos < τ′ : l'ensemble des coupures ne peut que grandir, et n(τ) est croissante. Sur le règlement, les seuils 0,05, 0,1, 0,2, 0,3 et 0,5 donnent 8, 8, 11, 12 et 15 morceaux. Le programme utilise un embedding jouet, un sac de racines de cinq lettres, et ce jouet montre deux défauts réels de la méthode. Entre la dernière phrase de l'article 2 (« Le salaire de base sert au calcul de l'indemnité de fin de service ») et la première de l'article 3, le cosinus vaut 0,46 : le découpeur réunit deux articles. À l'intérieur de l'article 3, entre « Le salarié a droit à une indemnité de fin de service… » et « Elle est calculée… », il vaut 0 : la reprise par « Elle » ne partage aucun mot, et le découpeur coupe au milieu de la règle. Un vrai modèle d'embedding gère mieux les reprises, mais le principe demeure : le découpage sémantique ignore la structure explicite du document, qu'un règlement fournit pourtant gratuitement.

### 6. Le parent-enfant : la précision du petit, le contexte du grand

On indexe les 17 phrases du règlement (227 mots) et l'on renvoie l'article entier qui contient la phrase retrouvée. La question « Quel est le plafond de l'indemnité de fin de service ? » montre pourquoi. La phrase qui répond, « Le plafond de ce montant est de 24 mois de salaire de base », ne nomme pas l'indemnité : en index de phrases seules, les deux premières phrases retrouvées sont celles qui contiennent « indemnité de fin de service », et la réponse n'arrive pas. En parent-enfant, la meilleure phrase appartient à l'article 3, que l'on renvoie entier : la réponse y est. Les 8 questions réussissent, contre 7 avec les phrases seules. Le prix se lit dans la formule de M_PE : 71,8 mots envoyés en moyenne par question, contre 30,9 pour deux phrases, parce que l'article 3 compte 89 mots avec son titre.

### 7. Le contextual retrieval : rendre au morceau le sujet qui lui manque

Au lieu de renvoyer le parent, on peut réparer le morceau lui-même : chaque morceau récursif est préfixé, avant indexation, par « Règlement intérieur du personnel — Article 3 — Indemnité de fin de service : ». Pour la question du plafond, le morceau qui contient la phrase passe du 3ᵉ au 1ᵉʳ rang de BM25, parce qu'il contient maintenant « indemnité », « fin » et « service » en plus de « plafond ». Les 8 questions réussissent, avec 61,1 mots envoyés en moyenne, et l'index passe de 227 à 341 mots, soit 50 % de plus : c'est la somme des préfixes de la formule de W_ctx. La technique a été proposée sous ce nom par Anthropic en 2024, avec un contexte de quelques dizaines de tokens écrit par un modèle pour chaque morceau ; l'éditeur annonce une baisse de 49 % des échecs de récupération en combinant embeddings et BM25 contextuels, et de 67 % en ajoutant un reranker (chiffres annoncés par l'éditeur, sur ses propres jeux de test). Ici, le contexte est écrit par une règle à partir des titres, sans aucun modèle.

### 8. La compression : moins de mots, un risque pour la phrase qui ne ressemble pas à la question

Après le parent-enfant, la compression extractive ne garde, dans l'article renvoyé, que les phrases qui partagent au moins θ termes avec la question. Pour la question du plafond, θ = 1 garde 39 mots sur 89 (ρ ≈ 0,44), dont la phrase du plafond, qui partage « plafond » avec la question ; θ = 2 n'en garde que 26 et perd cette phrase, qui ne partage qu'un terme. Sur les 8 questions, θ = 1 réussit tout avec 43,4 mots par question, θ = 2 tombe à 7 sur 8 avec 23,8 mots. La compression est donc monotone dans le mauvais sens pour la réponse : quand θ monte, C_θ ne peut que rétrécir, puisque toute phrase qui partage au moins θ + 1 termes en partage au moins θ, et les phrases qui reprennent un sujet sans le nommer sont les premières à partir. On l'atténue en gardant aussi les phrases voisines d'une phrase gardée, ou en jugeant les phrases avec un cross-encodeur (étape 30 bis) plutôt qu'avec des mots communs.

### 9. Le tableau d'ensemble (le code reprend ces nombres)

| Stratégie | Réussite | Morceaux | Mots indexés | Mots envoyés par question |
|---|---|---|---|---|
| fixe, c = 20, o = 0 | 2/8 | 13 | 259 | 39,9 |
| fixe, c = 20, o = 5 | 4/8 | 17 | 339 | 39,9 |
| fixe, c = 40, o = 10 | 6/8 | 9 | 339 | 77,4 |
| récursif, c = 30 | 7/8 | 12 | 227 | 41,1 |
| sémantique, τ = 0,2 | 8/8 | 11 | 227 | 63,1 |
| phrases seules | 7/8 | 17 | 227 | 30,9 |
| contexte + récursif, c = 30 | 8/8 | 12 | 341 | 61,1 |
| parent-enfant | 8/8 | 17 | 227 | 71,8 |
| parent-enfant + compression, θ = 1 | 8/8 | 17 | 227 | 43,4 |
| parent-enfant + compression, θ = 2 | 7/8 | 17 | 227 | 23,8 |

Les découpages fixes indexent aussi les titres, d'où 259 mots sans recouvrement ; les autres ne découpent que le corps des articles (227 mots). Les fenêtres fixes de 20 mots coupent presque toutes les règles ; le recouvrement en sauve deux, au prix de 30,9 % d'index en plus ; des fenêtres de 40 mots en sauvent davantage mais envoient deux fois plus de texte. Le découpage qui suit la structure (récursif, phrases, parent-enfant) fait mieux pour moins cher, et ses échecs viennent tous de la même phrase, celle qui ne nomme pas son sujet, que le contexte ou le parent réparent. Le 8 sur 8 du découpage sémantique tient en partie à la chance sur un texte aussi court : le point 5 a montré qu'il coupe au milieu de l'article 3.

## Effets et comportement

- **Augmenter c** réduit le nombre de morceaux et le risque de couper une règle, mais chaque morceau renvoyé coûte plus de tokens et mélange davantage de sujets, ce qui dilue le score de pertinence.
- **Augmenter o** protège les suites de moins de o + 1 mots et fait grossir l'index d'environ o/(c − o) (point 2) ; il ne protège jamais une règle plus longue que o + 1 mots.
- **Monter τ** multiplie les coupures sémantiques (point 5) : des morceaux plus purs, plus petits, plus nombreux.
- **Le parent-enfant échange des tokens contre du contexte** : la précision de recherche des petits morceaux, la complétude des grands.
- **Le préfixe de contexte** répare les morceaux qui ne nomment pas leur sujet, pour le prix d'un index plus gros, et il se calcule une seule fois, hors ligne.
- **Monter θ** compresse davantage et perd d'abord les phrases qui reprennent un sujet sans le nommer (point 8).

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| L | `len(mots(texte))` |
| c, o | `taille`, `recouvrement` |
| n | `nombre_morceaux(L, c, o)` |
| découpage fixe | `decouper_fixe(liste, taille, recouvrement)`, `morceaux_fixes` |
| découpage récursif | `decouper_recursif(texte, taille, separateurs)`, `morceaux_recursifs` |
| vᵢ, cos, τ | `vecteur`, `cosinus` (code canonique), `seuil` dans `decouper_semantique` |
| enfants, parents | `morceaux_phrases`, `vers_parents` |
| contexte(m) ⊕ m | `morceaux_recursifs(texte, taille, contexte=True)` |
| C_θ(q, P) | `compresser(contextes, question, seuil)` |
| réussite, M | `evaluer(contexte_de)` |

### Déroulé, ligne par ligne

**`cosinus`, `idf_bm25` et `bm25_score`** sont le code canonique des étapes 19 et 22, recopié tel quel. **`mots`** découpe en suites de lettres et de chiffres, en minuscules : c'est l'unité de longueur du fichier. **`termes`** retire les mots vides, pour la recherche et la compression. **`contient`** est la fonction de l'étape 18 : elle dit si une phrase figure entière, et dans l'ordre, dans un morceau.

**`REGLEMENT`** est le texte fictif, avec des paragraphes séparés par une ligne vide et un titre par article. **`QUESTIONS`** associe à chaque question la phrase qui doit arriver entière.

**`articles(texte)`** sépare les paragraphes sur `"\n\n"` et garde ceux qui commencent par « Article », sous la forme (titre, corps). **`phrases(corps)`** coupe après un point, un point d'exclamation ou un point d'interrogation suivi d'un espace.

**`nombre_morceaux(longueur, taille, recouvrement)`** applique la formule du point 1, avec ses gardes : `0 <= o < c` et `L >= 1`. Pour `(259, 20, 5)`, `math.ceil(254 / 15)` vaut 17.

**`decouper_fixe(liste, taille, recouvrement)`** est le découpeur de l'étape 18, appliqué à une liste de mots. `pas = taille - recouvrement` vaut 15 pour c = 20 et o = 5 ; la boucle s'arrête dès qu'un morceau atteint la fin du texte, exactement la condition jp + c ≥ L de la démonstration.

**`decouper_recursif(texte, taille, separateurs)`**.

- Si le texte tient dans `taille` mots, il est renvoyé tel quel.
- Sinon, on le coupe au premier séparateur de la liste ; s'il n'en contient aucun, on passe au suivant.
- La boucle accumule les pièces dans `courant` tant que `candidat` tient dans `taille` mots. Quand une pièce ne rentre plus, `courant` est émis ; la pièce devient le nouveau `courant` si elle tient seule, sinon elle est redécoupée récursivement avec les séparateurs suivants.
- Sur l'article 3 avec `taille = 20`, la phrase de 22 mots est trop longue même seule : elle est redécoupée aux espaces, en 20 et 2 mots.

**`vecteur(phrase, vocabulaire)`** compte les racines de cinq lettres de la phrase : « salaire » et « salaires » donnent la même racine `salai`. **`decouper_semantique(texte, seuil)`** calcule les vecteurs de toutes les phrases, le cosinus de chaque paire voisine avec la fonction canonique, puis ouvre un nouveau morceau chaque fois que le cosinus passe sous le seuil. Elle renvoie aussi les cosinus, pour les afficher.

**`Morceau`** distingue le texte renvoyé au modèle (`texte`), le texte indexé (`index`, qui peut contenir le préfixe) et le numéro de l'article d'origine (`parent`). **`morceaux_fixes`**, **`morceaux_recursifs`**, **`morceaux_semantiques`** et **`morceaux_phrases`** emballent chaque découpeur ; `morceaux_recursifs(..., contexte=True)` ajoute le préfixe « Règlement intérieur du personnel — titre de l'article : » au texte indexé et au texte renvoyé.

**`Index`** calcule BM25 sur le champ `index` des morceaux et renvoie les k meilleurs ; à score égal, l'ordre du document départage, ce qui rend la sortie déterministe.

**`vers_parents(trouves, texte)`** remplace chaque enfant retrouvé par son article entier, sans doublon. **`compresser(contextes, question, seuil)`** garde les phrases qui partagent au moins `seuil` termes avec la question.

**`evaluer(contexte_de)`** prend une fonction qui, pour une question, renvoie la liste des textes envoyés au modèle ; elle compte les questions dont la phrase attendue figure entière dans un de ces textes, et la moyenne des mots envoyés.

**`main()`**, bloc par bloc.

1. Pour trois couples (c, o), le nombre de morceaux est comparé à la formule, et les mots indexés à L + (n − 1)o ; la formule est vérifiée sur les 4 620 combinaisons de petites tailles (L ≤ 60, c ≤ 12, o < c). La fonction locale `fenetres` énumère toutes les suites de 6 mots, puis de 7 mots, du règlement : les premières sont toujours entières dans un morceau, 16 des secondes sont coupées.
2. Les tailles des morceaux récursifs de l'article 3 pour c = 20 et c = 30, et la vérification que tout morceau tient dans c mots.
3. Les cosinus voisins autour de l'article 3 et le nombre de morceaux sémantiques pour cinq seuils, qui doit être croissant.
4. Le tableau du point 9 : chaque découpage est indexé, interrogé avec k = 2 et évalué ; le parent-enfant et la compression utilisent l'index des phrases avec k = 1. Les dix réussites, les tailles d'index et les mots envoyés sont vérifiés.
5. La question du plafond, détaillée : l'échec des phrases seules, le rang du bon morceau sans et avec contexte (3 puis 1), et les deux seuils de compression.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cosinus(a, b)`** — C'est la boussole canonique de l'étape 19, recopiée telle quelle, qui compare la direction de deux vecteurs sans se soucier de leur longueur : la fonction reçoit deux vecteurs, lève `ValueError` si leurs dimensions diffèrent ou si l'un d'eux est nul, et renvoie le produit scalaire divisé par le produit des normes, rabattu dans [−1, 1]. Ici, elle ne sert qu'au découpage sémantique, pour mesurer la ressemblance de deux phrases voisines ; à la fin de l'article 2 et dans l'article 3, elle donne par exemple 0,46, 0,0, 0,55, 0,14 et 0,39.

**`idf_bm25(n_t, n_docs)`** — C'est le crieur canonique de l'étape 22, qui annonce le poids d'un mot d'après sa rareté parmi les morceaux indexés : la fonction reçoit le nombre de morceaux qui contiennent le terme et le nombre total de morceaux, puis renvoie le logarithme de 1 + (N − n + 0,5) / (n + 0,5), toujours positif. Elle n'est appelée que par `bm25_score` ; comme le nombre de morceaux change d'un découpage à l'autre, de 9 à 17 dans le tableau du point 4, le poids d'un même mot change aussi selon la stratégie.

**`bm25_score(requete, doc, corpus, k1, b)`** — C'est le juge lexical canonique de l'étape 22, chargé de retrouver les morceaux pour chacune des huit questions : la fonction reçoit la question et un morceau sous forme de listes de termes, l'ensemble des morceaux de l'index et les réglages k1 = 1,5 et b = 0,75 par défaut, puis additionne, pour chaque terme présent, son IDF multiplié par une partie fréquence saturée et corrigée par la longueur du morceau. Elle renvoie ce score, que `Index.chercher` utilise pour trier ; c'est lui qui explique qu'une phrase qui ne nomme pas son sujet, comme celle du plafond, soit mal classée.

**`mots(texte)`** — Cette fonction est la règle graduée de tout le fichier, celle qui définit ce qu'on appelle un mot : elle reçoit un texte, le met en minuscules et renvoie la liste de toutes les suites de lettres et de chiffres trouvées par l'expression `\w+`. C'est avec elle qu'on mesure la longueur du règlement, L = 259 mots, la taille de chaque morceau, les mots indexés et les mots envoyés au modèle, et c'est elle encore qui prépare les listes que `contient` compare pour savoir si une phrase est arrivée entière.

**`termes(texte)`** — Elle passe le texte au tamis pour n'en garder que les mots porteurs de sens : la fonction reçoit un texte, le découpe avec `mots`, puis retire tous ceux qui figurent dans `MOTS_VIDES`, articles, prépositions, pronoms et mots interrogatifs comme « combien » ou « comment ». Elle renvoie la liste des termes restants ; c'est ce que comparent BM25, le découpage sémantique, par l'intermédiaire de `vecteur`, et la compression, qui compte les termes communs entre une phrase et la question.

**`contient(morceau, phrase)`** — C'est le relecteur de l'étape 18 qui vérifie, doigt sur la ligne, qu'une phrase figure d'un seul tenant dans un morceau : la fonction reçoit deux listes de mots, fait glisser une fenêtre de la longueur de la phrase sur toutes les positions du morceau, et renvoie `True` dès qu'une fenêtre coïncide mot pour mot, `False` sinon. Elle définit le critère de réussite du fichier, la phrase attendue doit arriver entière dans le contexte, et sert aussi au point 1, où toute suite de 6 mots est retrouvée entière alors que 16 suites de 7 mots sont coupées.

**`articles(texte)`** — Cette fonction joue l'archiviste qui sépare le règlement en dossiers, un par article : elle reçoit le texte complet, le coupe à chaque ligne vide, ne garde que les paragraphes dont la première ligne commence par « Article », et renvoie pour chacun un couple (titre, corps), le corps réunissant les lignes suivantes en une seule. Le titre du règlement, qui ne commence pas par « Article », est donc écarté ; les cinq articles obtenus servent au découpage récursif article par article, aux phrases, au parent-enfant et au préfixe de contexte.

**`phrases(corps)`** — Elle est le ciseau qui coupe un article en phrases : la fonction reçoit le corps d'un article, le coupe juste après chaque point, point d'exclamation ou point d'interrogation suivi d'un blanc, retire les espaces superflus et écarte les morceaux vides. Elle renvoie la liste des phrases ; sur le règlement, elle en produit 17 en tout, qui deviennent les enfants indexés par `morceaux_phrases` et les unités que `compresser` garde ou supprime.

**`nombre_morceaux(longueur, taille, recouvrement)`** — Cette fonction est le métreur qui annonce, avant tout découpage, combien de fiches on va remplir : elle reçoit la longueur L du texte en mots, la taille c d'un morceau et le recouvrement o, lève `ValueError` si l'on n'a pas 0 ≤ o < c et L ≥ 1, puis renvoie max(1, ⌈(L − o) / (c − o)⌉), la formule démontrée au point 1. Pour L = 259, c = 20 et o = 5, elle donne 17 morceaux, et `main` la confronte à `decouper_fixe` sur les 4 620 combinaisons de petites tailles.

**`decouper_recursif(texte, taille, separateurs)`** — C'est un tailleur méthodique qui coupe d'abord aux coutures les plus fortes avant de toucher au tissu : la fonction reçoit un texte, une taille maximale en mots et une liste de séparateurs, du paragraphe à l'espace ; si le texte tient dans la taille, elle le renvoie tel quel, sinon elle le coupe au premier séparateur, passe au suivant s'il ne coupe rien, regroupe les pièces voisines tant qu'elles tiennent ensemble, et redécoupe avec les séparateurs suivants toute pièce trop longue seule. Elle renvoie la liste des morceaux, et lève `ValueError` si aucun séparateur ne permet de respecter la taille ; sur l'article 3, elle produit des morceaux de 19, 20, 2, 15, 13 et 13 mots pour une taille de 20.

**`vecteur(phrase, vocabulaire)`** — Cette fonction fabrique un plongement jouet, comme un comptable qui tiendrait un registre des racines de mots plutôt que des mots eux-mêmes : elle reçoit une phrase et un vocabulaire de racines, prend les cinq premières lettres de chaque terme de la phrase, et renvoie, pour chaque racine du vocabulaire, le nombre de fois qu'elle apparaît. Ainsi « salaire » et « salaires » donnent la même racine `salai` et rapprochent les phrases qui en parlent, assez pour que `decouper_semantique` juge si deux phrases voisines traitent du même sujet.

**`decouper_semantique(texte, seuil)`** — Elle découpe le texte là où le sujet change, comme un monteur de film qui coupe entre deux scènes plutôt qu'au milieu d'une réplique : la fonction reçoit le texte et un seuil τ, rassemble toutes les phrases des articles, construit un vocabulaire de racines et le vecteur de chaque phrase, calcule le cosinus de chaque paire de phrases voisines, puis ouvre un nouveau morceau chaque fois que ce cosinus passe sous le seuil. Elle renvoie un couple formé de la liste des morceaux et de la liste des cosinus ; pour τ = 0,05, 0,1, 0,2, 0,3 et 0,5, elle produit 8, 8, 11, 12 et 15 morceaux, un nombre qui ne décroît jamais quand le seuil monte.

**`morceaux_fixes(texte, taille, recouvrement)`** — Cette fonction emballe le découpeur à taille fixe pour qu'il parle la même langue que les autres stratégies : elle reçoit le texte, la taille et le recouvrement, découpe la liste des mots avec `decouper_fixe`, et renvoie un `Morceau` par fenêtre, dont le texte renvoyé et le texte indexé sont identiques et dont le parent vaut −1, puisqu'une fenêtre fixe n'appartient à aucun article précis. Avec c = 20 et o = 5, elle produit 17 morceaux et 339 mots indexés, mais seulement 4 réussites sur 8.

**`morceaux_recursifs(texte, taille, contexte)`** — Celle-ci emballe le découpeur récursif, article par article, et peut coller sur chaque morceau une étiquette qui dit d'où il vient : elle reçoit le texte, la taille et un drapeau `contexte`, faux par défaut, applique `decouper_recursif` au corps de chaque article, et renvoie un `Morceau` par pièce, avec le numéro de l'article pour parent. Si le drapeau est vrai, chaque morceau est préfixé par « Règlement intérieur du personnel », suivi du titre de l'article ; ce préfixe porte les mots indexés de 227 à 341 et fait passer la réussite de 7 à 8 sur 8 pour une taille de 30.

**`morceaux_semantiques(texte, seuil)`** — Cette fonction emballe le découpeur sémantique : elle reçoit le texte et le seuil τ, appelle `decouper_semantique`, n'en garde que la liste des morceaux et renvoie un `Morceau` par élément, avec le même texte renvoyé et indexé et un parent à −1, puisqu'un morceau sémantique peut chevaucher deux articles. Avec τ = 0,2, cette stratégie réussit les 8 questions sur 8 du tableau, parce que les coupures tombent là où le sujet change et ne tranchent aucune des phrases attendues.

**`morceaux_phrases(texte)`** — Elle produit les plus petites unités possibles, une phrase par morceau, comme on découperait un livre en fiches d'une seule ligne : la fonction reçoit le texte, parcourt les articles et leurs phrases, et renvoie un `Morceau` par phrase, avec le numéro de son article pour parent. Ces 17 enfants, qui totalisent 227 mots indexés, servent deux fois : seuls, ils réussissent 7 questions sur 8, et, ramenés à leur article par `vers_parents`, ils donnent la stratégie parent-enfant.

**`Index.__init__(morceaux)`** — Le constructeur prépare le fichier de la bibliothèque : il reçoit la liste des morceaux d'une stratégie, la garde dans l'attribut `morceaux`, et calcule une fois pour toutes la liste des termes du champ `index` de chacun, celui qui peut contenir le préfixe de contexte, pour ne pas les recalculer à chaque question. Il ne renvoie rien ; chaque stratégie du tableau reçoit son propre `Index`, si bien que les statistiques de BM25 dépendent du découpage choisi.

**`Index.chercher(question, k)`** — Cette méthode est le bibliothécaire qui répond à une question en posant sur le comptoir les k fiches les plus prometteuses : elle reçoit la question et le nombre k de morceaux voulus, découpe la question en termes, calcule le score BM25 de chaque morceau sur ses termes indexés, trie les morceaux par score décroissant en départageant les égalités par leur ordre dans le document, et renvoie les k premiers objets `Morceau`. C'est elle qui place le morceau du plafond au rang 3 sans contexte et au rang 1 avec contexte.

**`vers_parents(trouves, texte)`** — C'est le magasinier qui, à partir d'une fiche trouvée, va chercher le classeur entier dont elle provient : la fonction reçoit la liste des morceaux retrouvés et le texte du règlement, note les numéros de leurs articles parents dans l'ordre d'arrivée et sans doublon, et renvoie pour chacun l'article entier, sous la forme « titre : corps ». On cherche ainsi sur des phrases précises, mais on envoie au modèle un contexte complet : la stratégie parent-enfant réussit 8 questions sur 8, au prix de 71,8 mots envoyés en moyenne.

**`compresser(contextes, question, seuil)`** — Cette fonction joue l'éditeur qui raye, dans chaque contexte, les phrases sans rapport avec la question : elle reçoit la liste des contextes, la question et un seuil entier, découpe chaque contexte en phrases, ne garde que celles qui partagent au moins `seuil` termes avec la question, et renvoie la liste des contextes ainsi réduits, en écartant ceux dont il ne reste rien. Avec un seuil de 1, les mots envoyés tombent de 71,8 à 43,4 sans perdre de réussite ; avec un seuil de 2, ils tombent à 23,8, mais la phrase du plafond est rayée et la réussite redescend à 7 sur 8.

**`evaluer(contexte_de)`** — C'est l'examinateur qui fait passer les huit questions à chaque stratégie et note le résultat : la fonction reçoit une fonction qui, pour une question, renvoie la liste des textes envoyés au modèle, l'appelle sur chaque question, compte les mots envoyés, et note 1 si la phrase attendue figure entière dans l'un des textes, 0 sinon. Elle renvoie un couple formé de la liste des huit notes et de la moyenne des mots envoyés par question, les deux grandeurs que le tableau du point 4 met en regard.

**`main()`** — Le chef d'orchestre déroule cinq démonstrations : il vérifie pour trois couples (c, o) le nombre de morceaux et le surcoût du recouvrement, 30,9 % pour c = 20 et o = 5, puis la formule sur 4 620 combinaisons, et montre que toute suite de 6 mots tient dans un morceau alors que 16 suites de 7 mots sont coupées. Il mesure ensuite les morceaux récursifs de l'article 3, les cosinus voisins et le nombre de morceaux sémantiques pour cinq seuils, dresse le tableau des dix stratégies avec leurs réussites, leurs tailles d'index et leurs mots envoyés, et détaille enfin la question du plafond, son échec avec les phrases seules, son rang 3 puis 1, et ses deux seuils de compression. Chaque nombre est gardé par un `assert`, et la ligne finale n'annonce le succès que si tous ont tenu.

**`fenetres(lg)`** — Cette fonction interne, définie dans `main`, énumère toutes les suites consécutives de lg mots du règlement, comme une loupe qu'on fait glisser d'un mot à la fois sur toute la page : elle reçoit la longueur lg, et renvoie la liste des tranches de la liste `tout` qui commencent à chaque position possible. `main` s'en sert pour vérifier la propriété démontrée au point 1 : avec un recouvrement o = 5, toute suite de o + 1 = 6 mots tient entière dans un morceau, alors que 16 des suites de 7 mots sont coupées.

**`rang(idx)`** — Cette autre fonction interne de `main` mesure à quelle place un index range le bon morceau pour la question du plafond, comme un juge qui chercherait le nom d'un candidat dans la liste des résultats : elle reçoit un `Index`, lui demande un classement de 99 morceaux pour cette question, et renvoie le rang, compté à partir de 1, du premier morceau qui contient la phrase attendue en entier. Elle donne 3 pour l'index récursif sans contexte et 1 pour l'index avec contexte, ce qui montre l'effet du préfixe de titre.

```python
"""Étape 30 quater — découpage avancé (fixe, récursif, sémantique, parent-enfant), contextual retrieval, compression."""
import math
import re
import sys
from dataclasses import dataclass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- code canonique (étapes 19 et 22)
def cosinus(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("dimensions différentes")
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        raise ValueError("vecteur nul : le cosinus n'est pas défini")
    return max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b)) / (na * nb)))


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


# ---------------------------------------------------------------- texte
MOTS_VIDES = {"le", "la", "les", "l", "d", "de", "du", "des", "un", "une", "et", "ou", "pour", "au", "aux",
              "à", "a", "en", "par", "sur", "sa", "son", "ses", "ne", "pas", "qui", "que", "quel", "quelle",
              "quels", "quelles", "est", "il", "elle", "t", "s", "se", "ce", "cette", "dans", "on", "peut",
              "peuvent", "ils", "elles", "être", "sont", "chaque", "combien", "comment", "après", "avec"}


def mots(texte: str) -> list[str]:
    """Minuscules, suites de lettres et de chiffres : l'unité de longueur de ce fichier (un « mot »)."""
    return re.findall(r"\w+", texte.lower())


def termes(texte: str) -> list[str]:
    """Mots sans les mots vides : ce que BM25 et la compression comparent."""
    return [m for m in mots(texte) if m not in MOTS_VIDES]


def contient(morceau: list[str], phrase: list[str]) -> bool:
    """La phrase figure-t-elle, entière et dans l'ordre, dans le morceau ? (étape 18)"""
    n = len(phrase)
    return any(morceau[i:i + n] == phrase for i in range(len(morceau) - n + 1))


REGLEMENT = """Règlement intérieur du personnel (texte fictif)

Article 1 — Période d'essai
La période d'essai est fixée dans le contrat de travail. Pendant cette période, chaque partie peut mettre fin au contrat avec le préavis prévu par le contrat. La période d'essai n'est pas renouvelée.

Article 2 — Salaires
Les salaires sont versés chaque mois par le système de protection des salaires (WPS). Le bulletin indique le salaire de base et les indemnités. Le salaire de base sert au calcul de l'indemnité de fin de service.

Article 3 — Indemnité de fin de service
Le salarié a droit à une indemnité de fin de service après au moins un an de service continu. Elle est calculée sur le salaire de base, à raison de 21 jours de salaire par année pour les cinq premières années. Au-delà de cinq ans, elle est de 30 jours de salaire par année supplémentaire. Le plafond de ce montant est de 24 mois de salaire de base. Le salaire journalier est égal au salaire de base mensuel divisé par 30.

Article 4 — Congés annuels
Le salarié a droit à un congé annuel payé selon son contrat. Les dates de congé sont validées par le responsable. Les jours non pris sont reportés selon la politique interne.

Article 5 — Visa et permis de travail
Le cabinet prend en charge le visa de résidence et le permis de travail enregistré auprès du MOHRE. Le salarié remet son passeport et sa photo dans les délais demandés. Les frais de visa ne sont jamais déduits du salaire."""

QUESTIONS = [  # (question, phrase qui doit arriver ENTIÈRE dans le contexte du modèle)
    ("Après combien de temps a-t-on droit à l'indemnité de fin de service ?",
     "Le salarié a droit à une indemnité de fin de service après au moins un an de service continu."),
    ("Combien de jours de salaire par année pour les cinq premières années ?",
     "Elle est calculée sur le salaire de base, à raison de 21 jours de salaire par année pour les cinq premières années."),
    ("Quel est le plafond de l'indemnité de fin de service ?",
     "Le plafond de ce montant est de 24 mois de salaire de base."),
    ("Comment est calculé le salaire journalier ?",
     "Le salaire journalier est égal au salaire de base mensuel divisé par 30."),
    ("Par quel système les salaires sont-ils versés ?",
     "Les salaires sont versés chaque mois par le système de protection des salaires (WPS)."),
    ("Les frais de visa peuvent-ils être déduits du salaire ?",
     "Les frais de visa ne sont jamais déduits du salaire."),
    ("Au-delà de cinq ans de service, combien de jours par année ?",
     "Au-delà de cinq ans, elle est de 30 jours de salaire par année supplémentaire."),
    ("La période d'essai peut-elle être renouvelée ?",
     "La période d'essai n'est pas renouvelée."),
]


# ---------------------------------------------------------------- structure : articles et phrases
def articles(texte: str) -> list[tuple[str, str]]:
    """(titre, corps) de chaque article : un paragraphe qui commence par « Article »."""
    sortie = []
    for bloc in texte.split("\n\n"):
        lignes = bloc.split("\n")
        if lignes[0].startswith("Article"):
            sortie.append((lignes[0], " ".join(lignes[1:])))
    return sortie


def phrases(corps: str) -> list[str]:
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", corps) if p.strip()]


# ---------------------------------------------------------------- 1. taille fixe
def nombre_morceaux(longueur: int, taille: int, recouvrement: int) -> int:
    """n = max(1, ⌈(L − o) / (c − o)⌉), démontré au point 1."""
    if not 0 <= recouvrement < taille or longueur < 1:
        raise ValueError("il faut 0 <= o < c et L >= 1")
    return max(1, math.ceil((longueur - recouvrement) / (taille - recouvrement)))


def decouper_fixe(liste: list[str], taille: int, recouvrement: int) -> list[list[str]]:
    """Fenêtres de c mots ; chaque fenêtre reprend les o derniers mots de la précédente (étape 18)."""
    if not 0 <= recouvrement < taille:
        raise ValueError("il faut 0 <= recouvrement < taille")
    pas = taille - recouvrement
    morceaux = []
    for debut in range(0, len(liste), pas):
        morceaux.append(liste[debut:debut + taille])
        if debut + taille >= len(liste):
            break
    return morceaux


# ---------------------------------------------------------------- 2. récursif
SEPARATEURS = ["\n\n", "\n", ". ", " "]


def decouper_recursif(texte: str, taille: int, separateurs: list[str] = SEPARATEURS) -> list[str]:
    """Coupe au séparateur le plus fort ; regroupe les pièces voisines tant qu'elles tiennent dans c mots ;
    redécoupe avec le séparateur suivant toute pièce trop longue."""
    if len(mots(texte)) <= taille:
        return [texte.strip()] if texte.strip() else []
    if not separateurs:
        raise ValueError("aucun séparateur ne permet de respecter la taille")
    sep, suite = separateurs[0], separateurs[1:]
    pieces = [p for p in texte.split(sep) if p.strip()]
    if len(pieces) == 1:
        return decouper_recursif(texte, taille, suite)
    sortie, courant = [], ""
    for piece in pieces:
        candidat = piece if not courant else courant + sep + piece
        if len(mots(candidat)) <= taille:
            courant = candidat
            continue
        if courant:
            sortie.append(courant.strip())
        if len(mots(piece)) <= taille:
            courant = piece
        else:
            sortie.extend(decouper_recursif(piece, taille, suite))
            courant = ""
    if courant.strip():
        sortie.append(courant.strip())
    return sortie


# ---------------------------------------------------------------- 3. sémantique
def vecteur(phrase: str, vocabulaire: list[str]) -> list[float]:
    """Sac de racines (5 premières lettres) : un embedding jouet, assez pour comparer deux phrases voisines."""
    racines = [t[:5] for t in termes(phrase)]
    return [float(racines.count(v)) for v in vocabulaire]


def decouper_semantique(texte: str, seuil: float) -> tuple[list[str], list[float]]:
    """Coupe entre deux phrases voisines quand leur cosinus passe sous le seuil."""
    toutes = [p for _, corps in articles(texte) for p in phrases(corps)]
    vocabulaire = sorted({t[:5] for p in toutes for t in termes(p)})
    vecs = [vecteur(p, vocabulaire) for p in toutes]
    sims = [cosinus(vecs[i], vecs[i + 1]) for i in range(len(vecs) - 1)]
    morceaux, courant = [], [toutes[0]]
    for i, s in enumerate(sims):
        if s < seuil:
            morceaux.append(" ".join(courant))
            courant = []
        courant.append(toutes[i + 1])
    morceaux.append(" ".join(courant))
    return morceaux, sims


# ---------------------------------------------------------------- 4. parent-enfant, contexte, compression
@dataclass
class Morceau:
    texte: str          # ce que l'on renvoie au modèle
    index: str          # ce que l'on indexe (peut contenir un préfixe de contexte)
    parent: int         # numéro de l'article d'origine


def morceaux_fixes(texte: str, taille: int, recouvrement: int) -> list[Morceau]:
    return [Morceau(" ".join(m), " ".join(m), -1) for m in decouper_fixe(mots(texte), taille, recouvrement)]


def morceaux_recursifs(texte: str, taille: int, contexte: bool = False) -> list[Morceau]:
    """Récursif article par article ; avec contexte, chaque morceau est préfixé par le titre du document et de l'article."""
    sortie = []
    for a, (titre, corps) in enumerate(articles(texte)):
        for m in decouper_recursif(corps, taille):
            prefixe = f"Règlement intérieur du personnel — {titre} : " if contexte else ""
            sortie.append(Morceau(prefixe + m, prefixe + m, a))
    return sortie


def morceaux_semantiques(texte: str, seuil: float) -> list[Morceau]:
    return [Morceau(m, m, -1) for m in decouper_semantique(texte, seuil)[0]]


def morceaux_phrases(texte: str) -> list[Morceau]:
    return [Morceau(p, p, a) for a, (_, corps) in enumerate(articles(texte)) for p in phrases(corps)]


class Index:
    """BM25 sur le champ « index » des morceaux ; renvoie les k meilleurs (égalités : ordre du document)."""

    def __init__(self, morceaux: list[Morceau]):
        self.morceaux = morceaux
        self.toks = [termes(m.index) for m in morceaux]

    def chercher(self, question: str, k: int) -> list[Morceau]:
        tq = termes(question)
        ordre = sorted(range(len(self.morceaux)), key=lambda i: (-bm25_score(tq, self.toks[i], self.toks), i))
        return [self.morceaux[i] for i in ordre[:k]]


def vers_parents(trouves: list[Morceau], texte: str) -> list[str]:
    """Parent-enfant : on a cherché sur les phrases, on renvoie les articles entiers, sans doublon."""
    arts, vus = articles(texte), []
    for m in trouves:
        if m.parent not in vus:
            vus.append(m.parent)
    return [f"{arts[a][0]} : {arts[a][1]}" for a in vus]


def compresser(contextes: list[str], question: str, seuil: int) -> list[str]:
    """Compression contextuelle extractive : on ne garde que les phrases qui partagent au moins `seuil` termes avec la question."""
    tq = set(termes(question))
    sortie = []
    for c in contextes:
        gardees = [p for p in phrases(c) if len(tq & set(termes(p))) >= seuil]
        if gardees:
            sortie.append(" ".join(gardees))
    return sortie


def evaluer(contexte_de) -> tuple[list[int], float]:
    """Pour chaque question : 1 si la phrase attendue arrive ENTIÈRE dans un des contextes ; mots envoyés en moyenne."""
    succes, envoyes = [], 0
    for question, fait in QUESTIONS:
        contextes = contexte_de(question)
        envoyes += sum(len(mots(c)) for c in contextes)
        succes.append(int(any(contient(mots(c), mots(fait)) for c in contextes)))
    return succes, envoyes / len(QUESTIONS)


def main() -> None:
    texte = REGLEMENT
    tout = mots(texte)
    L, k = len(tout), 2
    print(f"1. Taille fixe : nombre de morceaux et coût du recouvrement (L = {L} mots)")
    for c, o in ((20, 0), (20, 5), (40, 10)):
        m = decouper_fixe(tout, c, o)
        indexes = sum(len(x) for x in m)
        print(f"  c = {c}, o = {o:>2} : n = ⌈({L} − {o})/({c} − {o})⌉ = {nombre_morceaux(L, c, o):>2} ;"
              f" mots indexés = L + (n − 1)·o = {indexes} ; surcoût {indexes / L - 1:.1%}")
        assert len(m) == nombre_morceaux(L, c, o) and indexes == L + (len(m) - 1) * o
    assert all(len(decouper_fixe(list(range(n)), c, o)) == nombre_morceaux(n, c, o)
               for n in range(1, 61) for c in range(2, 13) for o in range(c))
    m = decouper_fixe(tout, 20, 5)

    def fenetres(lg: int) -> list[list[str]]:                                 # toutes les suites de lg mots du texte
        return [tout[i:i + lg] for i in range(L - lg + 1)]

    assert all(any(contient(x, f) for x in m) for f in fenetres(6))              # o + 1 = 6 mots : toujours entiers
    coupees = sum(not any(contient(x, f) for x in m) for f in fenetres(7))
    print(f"  c = 20, o = 5 : toute suite de 6 mots tient dans un morceau ; {coupees} suites de 7 mots sont coupées")
    assert coupees > 0

    print("2. Récursif : on coupe d'abord aux paragraphes, puis aux phrases, puis aux mots")
    art3 = articles(texte)[2][1]
    for c in (20, 30):
        print(f"  article 3, c = {c} : tailles {[len(mots(x)) for x in decouper_recursif(art3, c)]}")
    assert [len(mots(x)) for x in decouper_recursif(art3, 20)] == [19, 20, 2, 15, 13, 13]
    assert [len(mots(x)) for x in decouper_recursif(art3, 30)] == [19, 22, 28, 13]
    assert all(len(mots(x)) <= c for c in (5, 10, 20, 30, 40) for x in decouper_recursif(texte, c))

    print("3. Sémantique : une coupure quand le cosinus entre phrases voisines passe sous τ")
    comptes = [len(decouper_semantique(texte, s)[0]) for s in (0.05, 0.1, 0.2, 0.3, 0.5)]
    sims = decouper_semantique(texte, 0.2)[1]
    print(f"  cosinus voisins (fin de l'article 2, article 3) {[round(x, 2) for x in sims[5:10]]} ; morceaux pour τ = 0.05 … 0.5 : {comptes}")
    assert comptes == sorted(comptes)                                            # τ plus haut : jamais moins de coupures

    print(f"4. Réussite : la phrase attendue arrive-t-elle entière dans le contexte ? (8 questions, k = {k})")
    index_phrases = Index(morceaux_phrases(texte))
    strategies = {
        "fixe c=20 o=0": morceaux_fixes(texte, 20, 0),
        "fixe c=20 o=5": morceaux_fixes(texte, 20, 5),
        "fixe c=40 o=10": morceaux_fixes(texte, 40, 10),
        "récursif c=30": morceaux_recursifs(texte, 30),
        "sémantique τ=0.2": morceaux_semantiques(texte, 0.2),
        "phrases seules": morceaux_phrases(texte),
        "contexte + récursif": morceaux_recursifs(texte, 30, contexte=True),
    }
    resultats = {}
    for nom, morceaux in strategies.items():
        idx = Index(morceaux)
        succes, envoyes = evaluer(lambda q: [x.texte for x in idx.chercher(q, k)])
        resultats[nom] = (sum(succes), len(morceaux), sum(len(mots(x.index)) for x in morceaux), envoyes)
    n_ph, mots_ph = resultats["phrases seules"][1], resultats["phrases seules"][2]   # mêmes enfants indexés
    succes, envoyes = evaluer(lambda q: vers_parents(index_phrases.chercher(q, 1), texte))
    resultats["parent-enfant"] = (sum(succes), n_ph, mots_ph, envoyes)
    for seuil in (1, 2):
        succes, envoyes = evaluer(lambda q: compresser(vers_parents(index_phrases.chercher(q, 1), texte), q, seuil))
        resultats[f"parent + compression {seuil}"] = (sum(succes), n_ph, mots_ph, envoyes)
    for nom, (ok, n, idx_mots, env) in resultats.items():
        print(f"  {nom:<24} réussite {ok}/8   morceaux {n:>2}   mots indexés {idx_mots}   mots envoyés {env:5.1f}")
    assert {nom: v[0] for nom, v in resultats.items()} == {
        "fixe c=20 o=0": 2, "fixe c=20 o=5": 4, "fixe c=40 o=10": 6, "récursif c=30": 7, "sémantique τ=0.2": 8,
        "phrases seules": 7, "contexte + récursif": 8, "parent-enfant": 8, "parent + compression 1": 8,
        "parent + compression 2": 7}
    assert (n_ph, mots_ph, resultats["contexte + récursif"][2]) == (17, 227, 341)
    envoyes_pe = [round(resultats[x][3], 1) for x in ("parent-enfant", "parent + compression 1", "parent + compression 2")]
    assert envoyes_pe == [71.8, 43.4, 23.8]

    print("5. La question du plafond : une phrase qui ne nomme pas son sujet")
    q3, fait3 = QUESTIONS[2]
    seules = [x.texte[:40] for x in index_phrases.chercher(q3, k)]
    print(f"  phrases seules, top-2 : {seules}")
    assert not any(contient(mots(x.texte), mots(fait3)) for x in index_phrases.chercher(q3, k))
    sans_ctx, avec_ctx = Index(morceaux_recursifs(texte, 30)), Index(morceaux_recursifs(texte, 30, contexte=True))

    def rang(idx: Index) -> int:                                              # rang du morceau qui contient la phrase
        return next(i for i, x in enumerate(idx.chercher(q3, 99), start=1) if contient(mots(x.texte), mots(fait3)))

    print(f"  rang du morceau qui contient la phrase : {rang(sans_ctx)} sans contexte, {rang(avec_ctx)} avec contexte")
    assert (rang(sans_ctx), rang(avec_ctx)) == (3, 1)
    parent3 = vers_parents(index_phrases.chercher(q3, 1), texte)
    for seuil in (1, 2):
        comp = compresser(parent3, q3, seuil)
        garde = any(contient(mots(c), mots(fait3)) for c in comp)
        print(f"  parent-enfant puis compression, seuil {seuil} : {sum(len(mots(c)) for c in comp)} mots gardés sur "
              f"{len(mots(parent3[0]))} ; phrase du plafond gardée : {garde}")
        assert garde == (seuil == 1)

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Taille fixe : nombre de morceaux et coût du recouvrement (L = 259 mots)
  c = 20, o =  5 : n = ⌈(259 − 5)/(20 − 5)⌉ = 17 ; mots indexés = L + (n − 1)·o = 339 ; surcoût 30.9%
  c = 20, o = 5 : toute suite de 6 mots tient dans un morceau ; 16 suites de 7 mots sont coupées
2. Récursif : on coupe d'abord aux paragraphes, puis aux phrases, puis aux mots
  article 3, c = 20 : tailles [19, 20, 2, 15, 13, 13]
  article 3, c = 30 : tailles [19, 22, 28, 13]
3. Sémantique : une coupure quand le cosinus entre phrases voisines passe sous τ
  cosinus voisins (fin de l'article 2, article 3) [0.46, 0.0, 0.55, 0.14, 0.39] ; morceaux pour τ = 0.05 … 0.5 : [8, 8, 11, 12, 15]
4. Réussite : la phrase attendue arrive-t-elle entière dans le contexte ? (8 questions, k = 2)
  fixe c=20 o=0            réussite 2/8   morceaux 13   mots indexés 259   mots envoyés  39.9
  fixe c=20 o=5            réussite 4/8   morceaux 17   mots indexés 339   mots envoyés  39.9
  récursif c=30            réussite 7/8   morceaux 12   mots indexés 227   mots envoyés  41.1
  contexte + récursif      réussite 8/8   morceaux 12   mots indexés 341   mots envoyés  61.1
  parent-enfant            réussite 8/8   morceaux 17   mots indexés 227   mots envoyés  71.8
  parent + compression 1   réussite 8/8   morceaux 17   mots indexés 227   mots envoyés  43.4
  parent + compression 2   réussite 7/8   morceaux 17   mots indexés 227   mots envoyés  23.8
5. La question du plafond : une phrase qui ne nomme pas son sujet
  rang du morceau qui contient la phrase : 3 sans contexte, 1 avec contexte
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : le découpage n'est pas un réglage cosmétique. Il décide de ce qui peut arriver entier dans le contexte, et chaque stratégie se paie en mots indexés ou en mots envoyés, ce que l'on mesure avant de choisir.

### Écrire le contexte avec un modèle, sans changer l'index

Quand les titres ne suffisent pas, par exemple pour un contrat dont les clauses renvoient à d'autres clauses, le préfixe peut être écrit par un LLM, une fois par morceau, à l'indexation. Le texte complet du document est le même pour tous ses morceaux : c'est le cas d'usage type du cache de prompt, qui évite de le repayer à chaque appel.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`prefixe_par_llm(llm, document, morceau)`** — Cette fonction confie à un modèle le travail d'un bibliothécaire qui rédige, pour chaque fiche, une courte note de situation : elle reçoit l'adaptateur LLM, le texte complet du document et le texte d'un morceau, envoie au modèle la consigne `CONSIGNE` sans aucun outil, avec un message qui contient le document entre balises `<document>` puis le morceau entre balises `<morceau>`, et renvoie le texte de la réponse, blocs texte concaténés et espaces de bord retirés. Ce contexte d'une ou deux phrases est ensuite placé devant le morceau dans le champ indexé, comme le montre la ligne commentée ; l'extrait n'est pas exécuté par le harnais, puisqu'il demande un vrai modèle.

```python
# [extrait] — préfixe de contexte écrit par un LLM, une fois par morceau, hors ligne (adaptateur Claude du parcours)
CONSIGNE = ("Voici un document, puis l'un de ses morceaux. Écris en une ou deux phrases le contexte qui situe ce "
            "morceau dans le document (titre, section, sujet), pour améliorer sa recherche. Réponds par ce contexte seul.")


def prefixe_par_llm(llm, document: str, morceau: str) -> str:
    reponse = llm.create(system=CONSIGNE, tools=[],
                         messages=[{"role": "user", "content": f"<document>{document}</document>\n<morceau>{morceau}</morceau>"}])
    return "".join(b.text for b in reponse.content if b.type == "text").strip()

# index = [Morceau(m, prefixe_par_llm(llm, doc, m) + " " + m, parent) for m in decouper_recursif(doc, 300)]
```

Pour rester indépendant d'un fournisseur, la version par règles du programme (titre du document et de l'article) couvre déjà les documents bien structurés ; le modèle ne sert qu'aux documents dont la structure ne dit pas le sujet.

## Squelette algorithmique

Le premier algorithme est le découpeur récursif : en entrée un texte, une taille maximale et une liste de séparateurs du plus fort au plus faible ; en sortie, des morceaux de c mots au plus. Le second assemble les techniques de ce fichier dans une recherche : indexer des enfants préfixés de leur contexte, retrouver, remonter aux parents, compresser.

```text
ALGORITHME DécouperRécursif(texte, c, séparateurs)
ENTRÉES : texte, taille maximale c (en mots), séparateurs du plus fort au plus faible
SORTIE  : liste de morceaux de c mots au plus

  SI mots(texte) ≤ c ALORS RETOURNER [texte]
  SI séparateurs est vide ALORS ERREUR « taille impossible à respecter »
  sep ← premier séparateur ; pièces ← texte coupé sur sep
  SI une seule pièce ALORS RETOURNER DécouperRécursif(texte, c, séparateurs sans sep)
  sortie ← liste vide ; courant ← vide
  POUR CHAQUE pièce FAIRE
      SI mots(courant + sep + pièce) ≤ c ALORS courant ← courant + sep + pièce
      SINON
          SI courant non vide ALORS ajouter courant à sortie
          SI mots(pièce) ≤ c ALORS courant ← pièce
          SINON ajouter DécouperRécursif(pièce, c, séparateurs sans sep) à sortie ; courant ← vide
      FIN SI
  FIN POUR
  SI courant non vide ALORS ajouter courant à sortie
  RETOURNER sortie

ALGORITHME RechercheParentEnfantCompressée
ENTRÉES : documents structurés (titre, sections), question q, k, seuil θ
SORTIE  : passages à envoyer au modèle

  HORS LIGNE : POUR CHAQUE section S de chaque document D FAIRE
      POUR CHAQUE enfant e DE DécouperRécursif(S, c, séparateurs) FAIRE
          indexer contexte(D, S) ⊕ e, avec parent(e) ← S
  EN LIGNE :
      E ← les k enfants de meilleur score pour q
      P ← parents distincts de E, dans l'ordre des scores
      RETOURNER, pour chaque P, les phrases s de P telles que |T(q) ∩ T(s)| ≥ θ
```

**Complexité.** Le découpage fixe coûte O(L + W) : un passage sur le texte et une copie de chaque morceau, recouvrements compris. Le récursif reparcourt une pièce à chaque niveau de séparateur, soit O(L × nombre de séparateurs) au pire, avec un recomptage des mots du morceau courant à chaque ajout dans cette version simple, qui la rend quadratique dans la taille d'une section ; un compteur incrémental la ramène au linéaire. Le sémantique coûte O(S × d) pour S phrases et des vecteurs de dimension d, plus le coût du modèle d'embedding. Le préfixe de contexte multiplie le coût d'indexation par la longueur relative des préfixes (point 7), ou par un appel au LLM par morceau s'il est écrit par un modèle. En ligne, le parent-enfant ajoute O(k) recherches de parent dans une table, et la compression O(|P|) comparaisons d'ensembles par parent.

**Du squelette au code.** `DécouperRécursif` est `decouper_recursif`. Dans `RechercheParentEnfantCompressée`, la partie hors ligne correspond à `morceaux_recursifs(texte, taille, contexte=True)` pour les enfants préfixés et à `morceaux_phrases` pour des enfants d'une phrase, avec le champ `parent` ; la recherche des k enfants est `Index.chercher`, la remontée `vers_parents` et la dernière ligne `compresser`. Le découpage fixe de la démonstration est `decouper_fixe`, et son nombre de morceaux `nombre_morceaux`.

## Cas d'usage réels aux Émirats

Les tailles de morceaux, les volumes et les gains ci-dessous sont illustratifs ; seuls les chiffres réglementaires reprennent la liste vérifiée du parcours.

### RH — le règlement du personnel, article par article

Un cabinet RH présent dans plusieurs émirats indexe le règlement du personnel de chacun de ses clients, plusieurs dizaines de pages par client, pour répondre aux salariés. La première version découpait en fenêtres de 300 tokens sans tenir compte des articles : la règle des 21 jours de salaire de base par année pendant cinq ans, puis 30 jours au-delà, se retrouvait coupée entre deux morceaux, exactement comme dans la démonstration où les fenêtres de 20 mots ne réussissent que 2 questions sur 8. L'équipe est passée à un découpage récursif aligné sur les articles, avec un préfixe « client — règlement — article » sur chaque morceau, et renvoie l'article entier quand la phrase retrouvée commence par une reprise (« elle », « ce montant »). Le plafond de 24 mois de salaire de base, qui est souvent écrit dans une phrase à part, arrive désormais avec la règle qu'il borne. Les règles reprises du décret-loi fédéral 33/2021 ne valent que pour le secteur privé hors DIFC, et le préfixe porte aussi le régime, pour que l'agent ne mélange pas les règlements. On suit la part des réponses dont la règle citée est complète, vérifiée par sondage par un juriste.

### Banque — des politiques de crédit dont les tableaux ne se coupent pas

Une banque de détail de Dubaï indexe sa politique de crédit, qui mêle des paragraphes et des tableaux de plafonds par produit. Un découpage fixe coupait les tableaux au milieu, et une ligne « prêt personnel : 20 fois le salaire, 48 mois au plus » se retrouvait séparée de son en-tête de colonnes, si bien que le modèle ne savait plus quel nombre était la durée. L'équipe découpe désormais une ligne de tableau par morceau, et préfixe chaque ligne par le titre de la section et par l'en-tête du tableau : c'est le contextual retrieval appliqué à des données structurées. Le ratio d'endettement total, 50 % du revenu (30 % pour un retraité) selon les règles de la CBUAE, est écrit dans un paragraphe qui renvoie au tableau ; le parent-enfant renvoie la section entière quand la question porte sur l'éligibilité, pour que la règle et le plafond arrivent ensemble. Sans ce découpage, l'agent pouvait annoncer une durée de 20 mois en lisant le mauvais nombre de la ligne. On suit la part des réponses de plafonds jugées exactes sur un jeu de questions annotées par le service conformité.

### BTP — des contrats de cent pages et un budget de contexte serré

Un groupe de construction qui mène de grands chantiers à Dubaï fait lire ses contrats de sous-traitance, d'une centaine de pages, par un agent qui contrôle les factures. Les clauses renvoient les unes aux autres (« la retenue prévue à l'article 14.2 »), et une clause isolée ne dit pas de quel lot elle relève. L'équipe indexe des enfants d'une ou deux phrases, préfixés par le lot et le numéro d'article, et renvoie la clause parente ; la compression ne garde ensuite de la clause que les phrases qui partagent des termes avec la facture contrôlée, ce qui divise environ par deux les tokens envoyés, comme le passage de 71,8 à 43,4 mots dans la démonstration. Le seuil de compression a été réglé prudemment, θ = 1, après qu'un seuil plus strict a supprimé la phrase qui fixait le taux de la retenue, comme la phrase du plafond au point 8. L'agent applique la retenue de garantie et calcule la TVA de 5 % sur le montant net. On suit la part des factures dont la clause citée contient bien le taux appliqué.

### Assurance — des clauses qui disent « cette garantie » sans la nommer

Un assureur auto et santé indexe ses conditions générales, où beaucoup de phrases commencent par « cette garantie », « ce plafond » ou « dans ce cas ». En index de phrases seules, ces phrases ne sont jamais retrouvées pour une question qui nomme la garantie, exactement comme la phrase du plafond de la démonstration, passée du 3ᵉ au 1ᵉʳ rang grâce au préfixe de contexte. L'équipe préfixe chaque morceau par le produit, la garantie et la section, ce qui a fait grossir l'index d'environ la moitié, comme les 227 mots passés à 341 du point 7 ; le coût est payé une fois, à l'indexation, et il est sans commune mesure avec celui d'un sinistre mal instruit. L'assurance est supervisée par la CBUAE, et une décision de refus doit citer la clause applicable entière, d'où la règle : l'agent ne cite jamais une phrase de reprise sans la phrase qui nomme la garantie. On suit le taux de clauses citées complètes et le nombre moyen de tokens de contexte par dossier.

### Secteur public — des pages bilingues et une ponctuation arabe

Une entité de services publics en ligne, accessible par UAE Pass, indexe ses pages de démarches en arabe et en anglais. Le découpeur récursif d'origine ne connaissait que la ponctuation latine : en arabe, il ne trouvait ni le point d'interrogation « ؟ » ni la virgule « ، », coupait donc aux espaces, et produisait des morceaux qui s'arrêtaient au milieu d'une phrase. L'équipe a ajouté la ponctuation arabe à la liste des séparateurs, applique la normalisation de l'étape 22 avant de compter les mots, et découpe chaque page séparément par langue, avec le titre de la démarche en préfixe dans la langue du morceau. Le nombre de tokens par mot n'est pas le même dans les deux langues, et la taille c est donc réglée par langue, en tokens, et non en mots. Pour respecter la PDPL, l'index ne contient que les pages publiques, jamais les données d'un usager. On suit la part des réponses dont la procédure citée est complète, mesurée séparément en arabe et en anglais.

### Immobilier — des fiches de projet où le nom porte tout

Une agence qui opère à Dubaï et à Abu Dhabi indexe des fiches de projets immobiliers : prix au sqft, échéancier de paiement, date de livraison, frais. Dans une fiche, seul le titre nomme le projet ; les paragraphes suivants disent « le projet » ou « la tour ». Sans préfixe, une question sur l'échéancier d'un projet précis ramène l'échéancier d'un autre projet, aussi bien rédigé. Le préfixe « projet — promoteur — émirat » sur chaque morceau règle ce problème ; le parent-enfant renvoie la fiche entière quand la question porte sur le coût total, pour que les frais de transfert du DLD, 4 % de la valeur, figurent à côté du prix. On suit la part des réponses dont toutes les sources citées appartiennent au bon projet.

## Pièges et limites

- **Choisir c sans regarder la longueur des règles.** Une unité plus longue que c ne tient jamais dans un morceau (point 3) ; on mesure la distribution des longueurs avant de fixer c.
- **Compter sur le recouvrement pour sauver des règles longues.** Il ne garantit que les suites de o + 1 mots et fait grossir l'index d'environ o/(c − o) (point 2).
- **Ignorer la structure que le document fournit.** Titres, articles, lignes de tableau et ponctuation, arabe comprise, sont des séparateurs gratuits et plus fiables qu'un seuil sémantique (point 5).
- **Indexer des phrases de reprise sans leur sujet.** « Ce montant », « cette garantie » : un préfixe de contexte ou le parent doit l'accompagner (points 6 et 7).
- **Compresser trop fort.** Le seuil qui économise le plus de tokens est aussi celui qui perd la phrase décisive (point 8) ; on le règle sur le jeu d'évaluation, pas sur la facture.
- **Changer le découpage sans réindexer et sans remesurer.** Les identifiants des morceaux, leurs embeddings et le jeu d'évaluation dépendent du découpage : un changement de c est une nouvelle version de l'index.

### Exercice feuille blanche

1. Sans regarder le code, démontrer la formule du nombre de morceaux, puis la vérifier pour L = 259, c = 40 et o = 10. (Réponse : ⌈249/30⌉ = 9 morceaux, et 259 + 8 × 10 = 339 mots indexés.)
2. Prédire, puis vérifier : avec c = 30 et o = 10, quelle est la plus longue suite de mots consécutifs garantie entière, et quel est le surcoût asymptotique de l'index ? (Réponse : 11 mots ; 30/20 = 1,5, soit 50 % de plus.)
3. Trouver le bug : dans `compresser`, la condition devient `len(tq & set(termes(p))) > seuil`. Que devient la réussite avec `seuil = 1` sur la question du plafond, et pourquoi ? (Réponse : la phrase du plafond, qui ne partage qu'un terme, est retirée : le seuil effectif est passé à 2, comme au point 8.)

## Pour aller plus loin

- **Late chunking** : on encode d'abord le document entier avec un modèle à long contexte, puis on fait la moyenne des vecteurs de tokens de chaque morceau ; chaque vecteur de morceau « voit » ainsi le reste du document, ce qui traite les reprises sans préfixe.
- **Résumés hiérarchiques** : on indexe aussi des résumés de sections et de documents, et la recherche descend du résumé vers les morceaux (méthode RAPTOR, Sarthi et al., 2024), un parent-enfant à plusieurs niveaux.
- **Compression par un modèle** : des méthodes comme LLMLingua retirent les tokens les moins informatifs selon un petit modèle de langue, au lieu de garder des phrases entières ; on y gagne en taux de compression, on y perd en lisibilité et en citations exactes.

> Étape 30 quater du parcours · Prérequis : [Transformations de requête](<30c-RAG-Transformations-de-Requete.md>) · Suite : [Index ANN : HNSW, IVF, PQ](<30e-RAG-Index-ANN-HNSW-IVF-PQ.md>)
