# Étape 30 septies — RAG — GraphRAG et mémoire en graphe

**Dossier :** 05-RAG

> Étape 30 septies du parcours · Prérequis : [Corrective RAG et Agentic RAG](<30f-RAG-Corrective-et-Agentic-RAG.md>) · Suite : [Attention par produit scalaire](<../06-Attention-et-Transformer/31-Attention-Formule-Produit-Scalaire-Normalise.md>)

## Définition

Un RAG vectoriel range des morceaux de texte ; un **GraphRAG** range des **faits**. Chaque fait est un triplet (sujet, relation, objet), par exemple (Alpha Courtage, détient, L-101). On lui ajoute sa **source** (le document et la phrase dont il vient) et ses **dates de validité**, du jour où il devient vrai au jour où il cesse de l'être. Les triplets forment un graphe : les entités sont les nœuds, les relations les arêtes. Ce graphe se prête à quatre opérations qu'une liste de passages fait mal. La **recherche locale** prend le voisinage à h sauts des entités nommées dans la question. La recherche **multi-sauts** suit un chemin de relations entre deux entités, trouvé par un parcours en largeur (BFS). Les **communautés** sont des groupes de nœuds plus liés entre eux qu'avec le reste ; on les mesure par la **modularité** Q et on les trouve, par exemple, avec l'algorithme de Louvain. La **recherche globale** résume chaque communauté puis combine les résumés (map-reduce), pour les questions qui portent sur tout le corpus. Une **mémoire en graphe** est le même objet tenu par un agent : un nouveau fait daté ferme l'ancien au lieu de l'effacer, si bien que l'agent peut répondre « à la date du contrat » aussi bien qu'« aujourd'hui ».

## Rôle dans un agent

Le graphe intervient à l'étape **percevoir**, comme un outil de recherche de plus, à côté de l'index vectoriel (étape 30 quinquies) et du repli correctif (étape 30 sexies). L'agent l'appelle quand la question nomme des entités (« la licence de la filiale de Gamma Holding »), quand la réponse dépend d'une date (« au moment de la transaction ») ou quand elle porte sur un ensemble (« combien de licences chaque autorité a-t-elle délivrées ? »). La construction du graphe a lieu hors ligne, à l'ingestion. Un extracteur, ici des règles déterministes et souvent un LLM en production, transforme chaque phrase en triplets, et chaque triplet garde sa source pour être cité. La mémoire en graphe sert aussi après **observer** : quand l'agent apprend un fait nouveau (« le siège a déménagé »), il l'ajoute daté, et l'ancien fait est fermé, comme le fait sémantique remplacé de l'étape 15 bis. Pour rester indépendant d'une base de graphes, il suffit de listes d'adjacence en mémoire pour quelques millions de faits, ou d'une table relationnelle (sujet, relation, objet, début, fin) avec des index. Une base de graphes du marché n'est qu'un adaptateur de plus derrière le même port.

## Équation complète

Un fait daté et sa validité (fin exclue ; un début vide veut dire « depuis toujours », une fin vide « toujours valable ») :

$$
f = \big(s,\, r,\, o,\, \text{source},\, [t_d \,;\, t_f[\,\big) , \qquad f \text{ valide à } t \iff t_d \le t < t_f
$$

Le graphe à la date t, sans les attributs (relations dont l'objet est une valeur, comme le statut) :

$$
G_t = \{\, f \;:\; f \text{ valide à } t ,\; r \notin \text{Attributs} \,\}
$$

Voisinage à h sauts et sa taille maximale, pour un degré maximal Δ :

$$
B_h(x) = \{\, y \;:\; \text{dist}_t(x, y) \le h \,\} , \qquad \lvert B_h(x) \rvert \le 1 + \Delta \sum_{j=0}^{h-1} (\Delta - 1)^j
$$

Distance dans un graphe non pondéré, calculée par BFS :

$$
\text{dist}(x, x) = 0 , \qquad \text{dist}(x, y) = 1 + \min_{z \in N(y)} \text{dist}(x, z) \quad \text{pour } y \ne x
$$

Modularité d'une partition en communautés, sous ses deux formes :

$$
Q = \frac{1}{2m} \sum_{i,j} \left( A_{ij} - \frac{k_i k_j}{2m} \right) \delta(c_i, c_j)
$$

$$
Q = \sum_{c} \left[ \frac{L_c}{m} - \left( \frac{d_c}{2m} \right)^2 \right]
$$

Gain de modularité quand un nœud isolé i rejoint une communauté C (Louvain) :

$$
G(i, C) = \frac{k_{i,C}}{m} - \frac{d_C \, k_i}{2m^2}
$$

Recherche globale d'un compte additif, par map-reduce sur une partition :

$$
N(a) = \sum_{c} N_c(a)
$$

## Décryptage des symboles

$$
s,\; r,\; o
$$

Le sujet, la relation et l'objet d'un triplet ; chaînes ; champs `sujet`, `relation`, `objet` de la classe `Fait`.

$$
t_d,\; t_f,\; t
$$

Le début et la fin de validité d'un fait (`None` pour « depuis toujours » ou « toujours valable ») et la date de la question ; objets `datetime.date` ; champs `debut` et `fin`, paramètre `t`.

$$
G_t,\; N(y)
$$

Le graphe des faits valides à la date t, vu sans orientation, et l'ensemble des voisins du nœud y ; méthode `voisins(t)`, qui renvoie pour chaque nœud la liste triée de ses voisins avec le fait qui les relie.

$$
h,\; B_h(x),\; \Delta
$$

Le nombre de sauts, l'ensemble des nœuds à au plus h sauts de x, et le degré maximal du graphe ; paramètre `h`, fonction `boule(voisins, graines, h)`, variable `deg_max`.

$$
\text{dist}(x, y)
$$

Le plus petit nombre d'arêtes entre x et y ; longueur de `plus_court_chemin(voisins, x, y)` moins un, vérifiée par `distances_par_relaxation`.

$$
A_{ij},\; k_i,\; m
$$

Le nombre de faits entre les nœuds i et j, le degré de i (somme de sa ligne) et le nombre total d'arêtes ; dictionnaire `A` construit par `poids(voisins)`, et variables `k` et `m` dans `modularite_matrice` et `louvain_local`.

$$
c_i,\; \delta(c_i, c_j)
$$

La communauté du nœud i, et le symbole qui vaut 1 si i et j sont dans la même communauté, 0 sinon ; dictionnaire `comm`.

$$
L_c,\; d_c,\; Q
$$

Le nombre d'arêtes internes à la communauté c, la somme des degrés de ses nœuds, et la modularité, un réel compris entre −1/2 et 1 ; variables `L`, `D` et fonction `modularite(A, comm)`.

$$
k_{i,C},\; d_C,\; G(i, C)
$$

Le nombre d'arêtes entre i et la communauté C, la somme des degrés de C (sans i), et le gain de modularité de l'insertion ; variables `liens[c]`, `d_tot[c]` et fonction interne `gain(c)`.

$$
N(a),\; N_c(a)
$$

Le nombre de licences délivrées par l'autorité a dans tout le graphe, et dans la seule communauté c ; résultat de `map_reduce(resumes)`, et champ `licences_par_autorite` de `resume`.

## Démonstration

### 1. La mémoire datée garde une seule valeur à la fois

Pour une relation **fonctionnelle**, qui n'a qu'une valeur à la fois, comme le siège d'une entreprise ou le statut d'une licence, la méthode `ajouter` applique une règle. Si un fait ouvert (sans fin) existe pour le même sujet et la même relation avec une autre valeur, il est fermé à la date de début du nouveau fait. Un fait plus ancien que le fait ouvert est refusé par `ValueError`, parce qu'il faudrait réécrire l'historique.

**Invariant : à toute date t, au plus un fait valide par couple (sujet, relation fonctionnelle).** Preuve par récurrence sur les insertions. Au départ, il n'y a aucun fait. Supposons l'invariant vrai, et insérons un fait de début t₀ pour un couple donné. Avant l'insertion, au plus un fait de ce couple est ouvert, puisque deux faits ouverts seraient tous deux valides aux dates postérieures à leurs débuts. Les faits déjà fermés ont des intervalles disjoints, par l'hypothèse de récurrence. Si un fait est ouvert, son début est au plus t₀ (sinon l'insertion est refusée) et sa fin devient t₀ : son intervalle [t_d ; t₀[ et celui du nouveau fait, [t₀ ; ∞[, ne se recouvrent pas. Les faits fermés plus tôt finissent avant le début du fait ouvert, donc avant t₀. L'invariant reste vrai. Le programme le vérifie à chaque date où un fait commence ou finit : l'ensemble des faits valides ne change qu'à ces dates, il suffit donc de les tester.

**Exemple fait à la main.** Delta Immobilier a son siège à Sharjah depuis le 1er mai 2019, puis à Dubaï depuis le 1er janvier 2023. Le second fait ferme le premier, qui devient valide sur [2019-05-01 ; 2023-01-01[. Le 1er juin 2022, le siège est donc Sharjah, et le 1er janvier 2026, Dubaï. La licence L-101 est active à partir du 1er mars 2024, suspendue du 1er juin au 1er septembre 2025, puis de nouveau active. Le 15 juillet 2025, son statut est « suspendue », et le 1er janvier 2024 il n'est pas défini, car la licence n'existe pas encore.

### 2. Un voisinage grossit vite autour des nœuds très connectés

Partons de x. Au premier saut, on trouve au plus Δ voisins. Chaque nœud atteint au saut j ≥ 1 a au plus Δ − 1 voisins autres que celui par lequel on l'a atteint, donc au plus Δ (Δ − 1)ʲ⁻¹ nœuds nouveaux apparaissent au saut j. En sommant de j = 1 à h et en ajoutant x lui-même, on obtient la borne de l'équation complète. Dans le graphe du programme, le nœud le plus connecté est Dubaï, de degré Δ = 4 (Alpha Courtage, Delta Immobilier, la RERA et la VARA). La borne vaut 5 pour h = 1 et 1 + 4 × (1 + 3) = 17 pour h = 2. Autour d'Alpha Courtage, on observe 4 puis 9 nœuds, soit déjà plus de la moitié des 16 nœuds du graphe à deux sauts. La croissance est géométrique en (Δ − 1), et ce sont les nœuds « carrefours » (un émirat, une grande autorité) qui la font exploser. En pratique, on garde h = 1 ou 2, on filtre les relations suivies et on ne développe pas les carrefours. Le programme vérifie la borne pour chaque nœud et pour h = 1, 2 et 3.

### 3. Le BFS trouve le plus court chemin

Le BFS sort les nœuds d'une file dans l'ordre où il les y a mis, et ne marque un nœud qu'à sa première découverte. Montrons par récurrence sur ℓ que tout nœud à distance ℓ de x est découvert avec l'étiquette ℓ, et qu'il entre dans la file après tous les nœuds de distance ℓ − 1. Pour ℓ = 0, c'est x lui-même. Supposons le résultat vrai jusqu'à ℓ, et soit y à distance ℓ + 1. Il a un voisin z à distance ℓ, sorti de la file avant tout nœud de distance ℓ + 1 par l'hypothèse de récurrence. Quand z est traité, y est découvert avec l'étiquette ℓ + 1, s'il ne l'a pas été avant. Il ne peut pas l'avoir été avec une étiquette plus petite : il faudrait qu'il ait un voisin à distance ℓ − 1 ou moins, et sa distance serait alors au plus ℓ. Remonter les parents depuis l'arrivée donne donc un chemin de longueur minimale. Chaque nœud entre une fois dans la file et chaque liste de voisins est lue une fois : le coût est O(V + E). Le programme compare le BFS à un calcul indépendant des distances, par relaxation de Bellman-Ford, sur les 16 × 16 = 256 couples de nœuds.

**Le sens du chemin compte autant que sa longueur.** Entre Alpha Courtage et la CBUAE, le plus court chemin sans filtre fait 4 sauts et passe par Gamma Holding, l'ADGM et Abu Dhabi : c'est un lien géographique, qui ne dit rien de la supervision. En ne suivant que les relations filiale_de, détient et délivrée_par, le plus court chemin fait aussi 4 sauts, mais il raconte autre chose : Alpha Courtage est filiale de Gamma Holding, dont l'autre filiale Bêta Paiements détient la licence L-202, délivrée par la CBUAE. Une question multi-sauts se traduit donc par un filtre de relations avant le BFS.

### 4. La modularité, sous ses deux formes

La première forme compare, pour chaque paire de nœuds d'une même communauté, l'arête observée Aᵢⱼ à kᵢkⱼ/2m. Ce terme est le nombre d'arêtes attendu entre i et j si l'on rebranchait les 2m extrémités d'arêtes au hasard en gardant les degrés : une extrémité prise au hasard appartient à i avec la probabilité kᵢ/2m. On passe à la seconde forme en regroupant les termes par communauté. D'une part, Σ Aᵢⱼ sur les couples (i, j) d'une même communauté c compte chaque arête interne deux fois, une fois par sens, et vaut 2L_c. D'autre part, Σ kᵢkⱼ sur ces mêmes couples vaut (Σ kᵢ)², soit d_c². D'où

$$
Q = \sum_{c} \left[ \frac{2 L_c}{2m} - \frac{d_c^2}{(2m)^2} \right] = \sum_{c} \left[ \frac{L_c}{m} - \left( \frac{d_c}{2m} \right)^2 \right]
$$

Deux conséquences. Si tout le graphe forme une seule communauté, L = m et d = 2m, donc Q = 1 − 1 = 0 : ne rien découper ne rapporte rien. Et comme le terme soustrait est strictement positif dès qu'il y a une arête, Q < 1.

**Exemple fait à la main.** Deux triangles a-b-c et d-e-f sont reliés par le pont c-d, soit m = 7 arêtes. Les degrés valent 2, 2, 3, 3, 2 et 2. Avec les deux triangles pour communautés, chacun a L = 3 arêtes internes et d = 7 :

$$
Q = 2 \times \left[ \frac{3}{7} - \left( \frac{7}{14} \right)^2 \right] = 2 \times (0{,}428571 - 0{,}25) = \frac{5}{14} \approx 0{,}3571
$$

Une seule communauté donne 0. Chaque nœud seul donne −(4 + 4 + 9 + 9 + 4 + 4)/196 = −34/196 ≈ −0,1735. Les trois paires {a, b}, {c, d}, {e, f} donnent 3/7 − (16 + 36 + 16)/196 ≈ 0,0816. Le programme calcule ces quatre valeurs avec les deux formes et vérifie qu'elles coïncident.

### 5. Louvain fait monter Q à chaque déplacement, donc il s'arrête

Retirons le nœud i de sa communauté : il devient isolé. Insérons-le dans une communauté C. Les liens internes et le degré total de C augmentent :

$$
L_C \to L_C + k_{i,C}, \qquad d_C \to d_C + k_i
$$

Et la communauté isolée de i, qui contribuait −(kᵢ/2m)², disparaît. La variation de Q vaut

$$
\left[ \frac{L_C + k_{i,C}}{m} - \left( \frac{d_C + k_i}{2m} \right)^2 \right] - \left[ \frac{L_C}{m} - \left( \frac{d_C}{2m} \right)^2 \right] + \left( \frac{k_i}{2m} \right)^2 = \frac{k_{i,C}}{m} - \frac{2 \, d_C \, k_i}{4m^2}
$$

C'est la formule G(i, C). Déplacer i de sa communauté A vers C fait varier Q de G(i, C) − G(i, A), toutes deux calculées avec i retiré. La phase locale de Louvain ne fait un déplacement que si cette différence est strictement positive : Q augmente strictement à chaque déplacement. Comme il n'existe qu'un nombre fini de partitions et qu'aucune ne peut revenir (Q serait revenu à une valeur déjà dépassée), l'algorithme s'arrête. La valeur finale vaut exactement la valeur de départ plus la somme des gains, ce que le programme vérifie. L'arrêt se fait sur un optimum **local** : aucun déplacement d'un seul nœud n'améliore Q, mais une autre partition peut faire mieux.

Sur les deux triangles, en partant des singletons (Q = −0,1735), a rejoint b (gain 1/7 − 2 × 2/98 ≈ 0,102, contre 0,0816 pour rejoindre c), puis c rejoint {a, b} (0,1633), d rejoint e (0,0816), e passe chez f (0,0204), et au second passage d rejoint {e, f} (0,1633). La somme des cinq gains, 0,5306, mène à 0,3571 : les deux triangles. Sur le graphe des entreprises au 1er janvier 2026 (16 nœuds, 19 arêtes), Q passe de −0,0679 à 0,4626 en 16 déplacements, avec cinq communautés :

| Communauté | Membres | Arêtes internes | Somme des degrés | Contribution à Q |
|---|---|---|---|---|
| C0 | ADGM, Abu Dhabi, Bêta Paiements, Gamma Holding | 4 | 11 | 0,1267 |
| C1 | Alpha Courtage, L-101, VARA | 2 | 7 | 0,0713 |
| C2 | CBUAE, L-202 | 1 | 5 | 0,0353 |
| C3 | Delta Immobilier, Dubaï, L-303, RERA | 4 | 10 | 0,1413 |
| C4 | Epsilon Assurances, L-404, Sharjah | 2 | 5 | 0,0880 |
| Total | 16 nœuds | 13 sur 19 | 38 = 2m | 0,4626 |

Chaque contribution se calcule à la main : pour C0, 4/19 − (11/38)² = 0,2105 − 0,0838 = 0,1267.

### 6. Le map-reduce est exact pour un compte additif

La question « combien de licences chaque autorité a-t-elle délivrées ? » ne nomme aucune entité : la recherche locale ne trouve aucune graine et renvoie un contexte vide. Elle porte sur tout le graphe. La recherche globale demande à chaque communauté son compte partiel N_c(a) (map), puis additionne (reduce). Les communautés forment une **partition** des nœuds : chaque licence appartient à exactement une communauté, donc chaque fait « délivrée par » est compté une fois et une seule, et la somme des comptes partiels est le compte total. Le programme obtient CBUAE 2, RERA 1 et VARA 1 par les deux chemins. L'exactitude tient à l'additivité. Pour une question qui ne se décompose pas en somme, comme « quel est le thème dominant ? » ou une médiane, le reduce de résumés n'est qu'une approximation. Elle l'est d'autant plus que, dans un GraphRAG réel, les résumés de communautés sont rédigés par un LLM et perdent de l'information. Le gain est un coût borné : on lit un résumé par communauté au lieu de tout le corpus, alors qu'un top-k de passages ne verrait qu'une petite partie des licences.

## Effets et comportement

- **Augmenter h** élargit le contexte de façon géométrique (point 2) : plus de faits pertinents, mais aussi beaucoup de bruit autour des carrefours.
- **Filtrer les relations** change le sens et parfois la longueur des chemins (point 3) : c'est la façon de traduire « supervisé par » ou « contrôlé par » en requête.
- **Interroger à une date** change la réponse sans rien effacer : la mémoire garde l'historique, et chaque réponse dit à quelle date elle vaut.
- **La partition en communautés** dépend de l'ordre de parcours et de l'algorithme : Louvain donne un optimum local, que l'on stabilise en fixant l'ordre et en relançant après chaque grosse mise à jour.
- **Une extraction plus large** (un LLM au lieu de règles) trouve plus de faits mais en invente aussi. La phrase « Le groupe prévoit de s'étendre à Ras Al Khaimah » montre ce que les règles refusent : une intention n'est pas un fait, et elle est rendue, pas devinée.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| f = (s, r, o, source, [t_d ; t_f[) | `Fait(sujet, relation, objet, source, debut, fin)` |
| f valide à t | `Fait.valide_le(t)` |
| relations fonctionnelles, attributs | `FONCTIONNELLES`, `ATTRIBUTS` |
| extraction | `extraire(doc_id, quand, texte)` avec `REGLES` |
| ajout daté et fermeture | `Graphe.ajouter(f)` |
| valeur à la date t | `Graphe.valeur(sujet, relation, t)` |
| G_t, N(y) | `Graphe.voisins(t, relations)` |
| B_h(x) | `boule(voisins, graines, h)` |
| contexte local | `contexte_local(g, t, question, h)` |
| plus court chemin | `plus_court_chemin(voisins, depart, arrivee)` |
| A, kᵢ, m | `poids(voisins)`, `k`, `m` |
| Q | `modularite(A, comm)` et `modularite_matrice(A, comm)` |
| G(i, C) | `gain(c)` dans `louvain_local(A)` |
| N_c(a), N(a) | `resume(g, t, membres)`, `map_reduce(resumes)` |

### Déroulé, ligne par ligne

**`Fait`** est une `dataclass` à six champs. `valide_le(t)` teste `debut <= t < fin`, en traitant `None` comme « sans limite » de chaque côté.

**`Graphe.ajouter(f)`**.

- Si la relation est fonctionnelle, la boucle cherche un fait ouvert de même sujet et de même relation.
- `if ancien.objet == f.objet: return` ignore un fait répété à l'identique. `if f.debut is None or ... f.debut < ancien.debut` refuse un fait plus ancien que celui en cours.
- `ancien.fin = f.debut` ferme l'ancien fait. Pour Delta Immobilier, le fait « Sharjah » reçoit la fin 2023-01-01 quand arrive le fait « Dubaï ».
- Le fait est enfin ajouté à la liste.

**`faits_le(t)`** filtre les faits valides. **`valeur(sujet, relation, t)`** renvoie l'objet du fait valide, ou `None` : `valeur("L-101", "statut", date(2025, 7, 15))` vaut `"suspendue"`.

**`voisins(t, relations)`** construit la vue non orientée de G_t. Chaque fait valide qui n'est pas un attribut, et dont la relation passe le filtre, ajoute le voisin dans les deux sens. Les listes sont triées par nom de voisin, ce qui rend le BFS déterministe. Au 1er janvier 2026, on obtient 16 nœuds et 19 arêtes.

**`REGLES` et `extraire`**. Chaque règle est une expression régulière et une liste de gabarits (sujet, relation, objet) qui nomment ses groupes. « Alpha Courtage détient la licence L-101, délivrée par la VARA » produit deux faits : (Alpha Courtage, detient, L-101) et (L-101, delivree_par, VARA). `extraire` coupe le texte en phrases sur « . », essaie les règles dans l'ordre, et range dans `rejets` toute phrase qu'aucune règle ne reconnaît. Chaque fait reçoit la source `doc#phrase` et la date du document. Les huit documents du `REGISTRE` donnent 23 faits et un rejet.

**`boule(voisins, graines, h)`** est un BFS qui ne développe plus un nœud arrivé à la distance h (`if dist[u] == h: continue`). **`contexte_local`** prend pour graines les nœuds dont le nom figure dans la question. Il garde les faits valides dont le sujet est dans la boule et dont l'objet y est aussi, ou qui sont des attributs. Pour « La société Alpha Courtage peut-elle opérer ? » au 15 juillet 2025 et h = 1, il renvoie quatre lignes, dont « L-101 —statut→ suspendue [reg-06#1] ».

**`plus_court_chemin(voisins, depart, arrivee)`** lève `ValueError` pour une entité absente. Il fait un BFS complet en notant pour chaque nœud son parent et le fait emprunté, s'arrête quand il sort l'arrivée de la file, puis remonte les parents. Il renvoie `None` si l'arrivée n'est pas atteignable. **`distances_par_relaxation`** recalcule toutes les distances par une méthode indépendante : on relâche d(u, v) ← d(u, w) + 1 pour chaque arête (w, v) tant que quelque chose change.

**`poids(voisins)`** compte les faits entre deux nœuds. **`modularite(A, comm)`** accumule pour chaque communauté la somme des degrés et le poids interne. Chaque arête interne est vue deux fois, d'où le `w / 2`. La fonction applique ensuite la seconde forme. **`modularite_matrice`** applique la première forme, double somme sur tous les couples, pour la vérification.

**`louvain_local(A)`**.

- Chaque nœud commence seul dans sa communauté ; `d_tot` tient la somme des degrés de chaque communauté.
- Pour chaque nœud u, on le retire (`d_tot[ancienne] -= k[u]`), on compte ses liens vers chaque communauté voisine (`liens`), puis on calcule le gain d'insertion avec la formule G(i, C).
- `max(..., key=lambda c: (gain(c), c == ancienne))` choisit le meilleur gain ; à gain égal, il préfère rester, puis la communauté de plus petit numéro.
- Un déplacement n'a lieu que si le gain dépasse celui de rester. Il est alors noté dans `gains`, et la boucle extérieure recommence tant qu'au moins un nœud a bougé.
- Les communautés sont renumérotées par ordre de leur premier membre.

**`resume(g, t, membres)`** produit le résumé d'une communauté : ses entreprises et ses licences comptées par autorité. Un LLM rédigerait ce résumé en phrases ; ici, il est calculé, donc vérifiable. **`map_reduce(resumes)`** additionne les comptes partiels.

**`main()`**, bloc par bloc.

1. L'extraction : 23 faits, une phrase rendue, et un exemple de fait avec sa source et sa date.
2. Les faits datés : les valeurs à trois dates, la fermeture du fait « Sharjah », l'invariant vérifié à toutes les dates où quelque chose change, et le refus d'un fait antérieur.
3. La recherche locale : les tailles 4 et 9 des boules, la borne du point 2 pour tous les nœuds, et le contexte daté.
4. Le multi-sauts : le chemin réglementaire, le chemin sans filtre, et la comparaison du BFS à la relaxation sur 256 couples.
5. La modularité à la main sur les deux triangles : les quatre partitions, les deux formes, et Louvain qui retrouve les triangles.
6. Louvain sur le graphe des entreprises : cinq communautés, Q = 0,4626, et la somme des gains qui relie Q initial et Q final.
7. La recherche globale : le contexte local vide, les résumés, le reduce, et la comparaison au calcul direct.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Fait.valide_le(t)`** — Cette méthode est le greffier qui vérifie qu'un acte était bien en vigueur à la date demandée : elle reçoit une date t et renvoie `True` si le fait a commencé au plus tard à cette date et n'a pas encore pris fin, c'est-à-dire si début ≤ t < fin, un début ou une fin valant `None` étant traités comme « sans limite » de ce côté. Toutes les questions datées du programme passent par elle ; c'est grâce à elle que le même graphe répond « suspendue » pour la licence L-101 le 15 juillet 2025 et « active » le 1er janvier 2026.

**`Graphe.__init__()`** — Le constructeur ouvre un registre vide, comme un archiviste qui pose sur son bureau un classeur neuf : il ne reçoit aucun argument et crée seulement la liste `faits`, où seront rangés tous les triplets datés, sans rien renvoyer. Le graphe n'est jamais stocké ailleurs que dans cette liste : les voisins, les chemins et les communautés sont recalculés à la demande, pour une date donnée, à partir des seuls faits valides à cette date.

**`Graphe.ajouter(f)`** — Cette méthode est l'archiviste qui inscrit un nouveau fait sans jamais effacer l'ancien : elle reçoit un `Fait` et, si sa relation est fonctionnelle, comme le siège ou le statut, elle cherche le fait encore ouvert de même sujet et de même relation ; si c'est le même objet, elle ignore la répétition, si le nouveau fait est plus ancien que celui en cours, elle lève `ValueError`, et sinon elle ferme l'ancien en lui donnant pour fin la date de début du nouveau. Elle ajoute enfin le fait à la liste, sans rien renvoyer ; ainsi le siège « Sharjah » de Delta Immobilier reçoit la fin du 1er janvier 2023 quand arrive le siège « Dubaï », et un siège à Ajman daté de 2020 est refusé.

**`Graphe.faits_le(t)`** — C'est le photographe qui prend un instantané du registre à une date précise : la méthode reçoit une date t et renvoie la liste des faits valides à cette date, ceux pour lesquels `valide_le` répond oui. Elle est la base de toutes les autres lectures du graphe, valeurs, voisins, contexte local et résumés, et `main` s'en sert aussi pour vérifier, à chaque date où quelque chose change, qu'une relation fonctionnelle n'a jamais deux valeurs en même temps pour le même sujet.

**`Graphe.valeur(sujet, relation, t)`** — Elle répond à une question précise, comme un employé de mairie qui consulte une fiche à la date demandée : la méthode reçoit un sujet, une relation et une date, cherche parmi les faits valides à cette date ceux qui portent ce sujet et cette relation, et renvoie l'objet du premier, ou `None` s'il n'y en a aucun. Le siège de Delta Immobilier vaut ainsi « Sharjah » le 1er juin 2022 et « Dubaï » le 1er janvier 2026, et le statut de la licence L-101 vaut « suspendue » le 15 juillet 2025 mais `None` le 1er janvier 2024, avant sa première annonce.

**`extraire(doc_id, quand, texte)`** — Cette fonction remplace un LLM d'extraction par un greffier qui ne connaît que quelques formules et n'invente rien : elle reçoit l'identifiant d'un document, sa date et son texte, coupe le texte en phrases sur « . », confronte chaque phrase aux expressions régulières de `REGLES` dans l'ordre, et, à la première qui reconnaît la phrase, fabrique un ou deux faits avec la source `doc#numéro` et la date du document. Elle renvoie la liste des faits et la liste des phrases qu'aucune règle n'a reconnues ; les huit documents du registre donnent ainsi 23 faits et un seul rejet, la phrase sur l'extension à Ras Al Khaimah.

**`contexte_local(g, t, question, h)`** — C'est l'enquêteur qui part des noms cités dans la question et fouille le voisinage proche : la fonction reçoit le graphe, une date, la question et un nombre de sauts h, construit les voisins à cette date, prend pour graines les nœuds dont le nom figure dans la question, calcule leur boule de rayon h avec `boule`, puis renvoie, sous forme de lignes lisibles avec leur source, les faits valides dont le sujet est dans la boule et dont l'objet y est aussi ou est un simple attribut. Pour Alpha Courtage au 15 juillet 2025 avec h = 1, elle renvoie quatre lignes, dont celle de la licence suspendue ; pour une question globale qui ne nomme aucune entité, elle ne renvoie rien.

**`distances_par_relaxation(voisins)`** — Cette fonction est le contre-expert qui refait tous les calculs de distance par une méthode indépendante, pour vérifier le BFS : elle reçoit la vue des voisins, part d'une table où chaque nœud est à distance 0 de lui-même, puis, tant que quelque chose change, améliore d(u, v) en d(u, w) + 1 pour chaque arête (w, v), à la manière de Bellman-Ford avec des poids égaux à 1. Elle renvoie le dictionnaire des distances entre tous les couples reliés ; `main` vérifie qu'il coïncide avec la longueur des plus courts chemins sur les 256 couples des 16 nœuds.

**`poids(voisins)`** — C'est le comptable qui transforme la liste des voisins en tableau à double entrée : la fonction reçoit la vue des voisins et renvoie, pour chaque nœud, un dictionnaire qui associe à chaque voisin le nombre de faits qui les relient, la matrice d'adjacence pondérée A. Deux entités reliées par deux faits différents reçoivent ainsi un poids de 2 ; c'est sur cette matrice que travaillent `modularite`, `modularite_matrice` et `louvain_local`.

**`modularite(A, comm)`** — Elle mesure si un découpage en communautés regroupe vraiment des nœuds plus liés entre eux que le hasard ne le voudrait, comme un sociologue qui compare les amitiés internes à un club avec celles qu'on attendrait au hasard : la fonction reçoit la matrice A et l'affectation de chaque nœud à une communauté, calcule le poids total m, lève `ValueError` si le graphe n'a aucune arête, accumule pour chaque communauté son poids interne et sa somme des degrés, et renvoie Q, la somme, sur les communautés, du poids interne divisé par m moins le carré de la somme des degrés divisée par 2m. Sur les deux triangles reliés par un pont, elle donne 5/14 ≈ 0,3571 pour le bon découpage et −34/196 pour les singletons.

**`modularite_matrice(A, comm)`** — Cette fonction calcule la même modularité par sa forme d'origine, comme un vérificateur qui refait l'addition colonne par colonne : elle reçoit la matrice et l'affectation, calcule le degré de chaque nœud et le poids total, puis fait la double somme, sur tous les couples de nœuds d'une même communauté, de Aᵢⱼ − kᵢ kⱼ / 2m, avant de diviser par 2m. Elle renvoie le même nombre que `modularite`, et `main` vérifie l'égalité des deux formes à 10⁻¹² près pour les quatre partitions des deux triangles.

**`louvain_local(A)`** — C'est un organisateur de banquet qui déplace les convives un à un vers la table où ils ont le plus d'amis, tant que l'ambiance générale s'améliore : la fonction reçoit la matrice A, place chaque nœud seul dans sa communauté, puis, pour chaque nœud, le retire de sa communauté, compte ses liens vers chaque communauté voisine, calcule le gain d'insertion avec la fonction interne `gain`, et le déplace vers la meilleure communauté si le gain dépasse celui de rester. Elle recommence tant qu'un nœud a bougé, renumérote les communautés par leur premier membre, et renvoie l'affectation et la liste des gains ; elle retrouve les deux triangles en 5 déplacements, et sur le graphe des entreprises cinq communautés en 16 déplacements, avec Q = 0,4626.

**`gain(c)`** — Cette fonction interne, définie dans `louvain_local` à chaque nœud examiné, calcule ce que gagnerait la modularité si le nœud isolé u rejoignait la communauté c : elle reçoit le numéro de la communauté et renvoie le poids de ses liens vers cette communauté divisé par m, moins la somme des degrés de la communauté multipliée par le degré de u et divisée par 2m². Elle s'appuie sur les tables `liens` et `d_tot` du moment ; c'est la formule G(i, C) de la démonstration, et la somme des gains retenus relie exactement la modularité des singletons à la modularité finale.

**`resume(g, t, membres)`** — Elle remplace le résumé qu'un LLM rédigerait pour chaque communauté par un compte rendu calculé, donc vérifiable : la fonction reçoit le graphe, une date et l'ensemble des membres d'une communauté, prend les faits valides dont le sujet appartient à la communauté, liste les entreprises, c'est-à-dire les sujets d'un siège, d'une licence détenue ou d'une filiation, et compte les licences de la communauté par autorité de délivrance. Elle renvoie un dictionnaire avec la liste triée des entreprises et ces comptes par autorité, la part « map » de la recherche globale.

**`map_reduce(resumes)`** — C'est le secrétaire général qui additionne les rapports de toutes les sections pour répondre à une question que personne ne peut traiter seul : la fonction reçoit la liste des résumés de communauté, additionne pour chaque autorité les comptes de licences de tous les résumés, et renvoie le total trié par nom d'autorité. À la question « Combien de licences chaque autorité a-t-elle délivrées ? », elle répond CBUAE 2, RERA 1 et VARA 1, exactement ce que donne un calcul direct sur tout le graphe.

**`main()`** — Le chef d'orchestre déroule sept démonstrations : l'extraction des 23 faits et du rejet unique, puis les faits datés, avec les valeurs à trois dates, la fermeture du siège « Sharjah », l'invariant d'une valeur à la fois et le refus d'un fait antérieur. Il passe ensuite à la recherche locale, avec des boules de 4 puis 9 nœuds autour d'Alpha Courtage, la borne du point 2 et le contexte daté, puis au multi-sauts, avec le chemin réglementaire jusqu'à la CBUAE, le chemin sans filtre et la comparaison du BFS à la relaxation, à la modularité à la main sur les deux triangles, à Louvain sur le graphe des entreprises, et enfin à la recherche globale par map-reduce, comparée au calcul direct. La dernière ligne n'annonce le succès que si chaque `assert` a tenu.

```python
"""Étape 30 septies — GraphRAG et mémoire en graphe : triplets datés, recherche locale, BFS multi-sauts, modularité, Louvain, map-reduce."""
import re
import sys
from collections import deque
from dataclasses import dataclass
from datetime import date

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- faits datés et graphe
FONCTIONNELLES = {"siege_a", "statut"}       # une seule valeur valide à la fois pour un sujet donné
ATTRIBUTS = {"statut"}                       # l'objet est une valeur, pas une entité : on ne traverse pas


@dataclass
class Fait:
    sujet: str
    relation: str
    objet: str
    source: str
    debut: date | None                       # None : valable depuis toujours
    fin: date | None = None                  # None : toujours valable ; sinon valable jusqu'à fin exclue

    def valide_le(self, t: date) -> bool:
        return (self.debut is None or self.debut <= t) and (self.fin is None or t < self.fin)


class Graphe:
    def __init__(self):
        self.faits: list[Fait] = []

    def ajouter(self, f: Fait) -> None:
        """Pour une relation fonctionnelle, le nouveau fait ferme l'ancien : fin de l'ancien = début du nouveau."""
        if f.relation in FONCTIONNELLES:
            for ancien in self.faits:
                if (ancien.sujet, ancien.relation) == (f.sujet, f.relation) and ancien.fin is None:
                    if ancien.objet == f.objet:
                        return                                   # même fait répété : rien à changer
                    if f.debut is None or (ancien.debut is not None and f.debut < ancien.debut):
                        raise ValueError("fait antérieur au fait en cours : réécrire l'historique n'est pas géré ici")
                    ancien.fin = f.debut
        self.faits.append(f)

    def faits_le(self, t: date) -> list[Fait]:
        return [f for f in self.faits if f.valide_le(t)]

    def valeur(self, sujet: str, relation: str, t: date) -> str | None:
        valeurs = [f.objet for f in self.faits_le(t) if (f.sujet, f.relation) == (sujet, relation)]
        return valeurs[0] if valeurs else None

    def voisins(self, t: date, relations: set[str] | None = None) -> dict[str, list[tuple[str, Fait]]]:
        """Vue non orientée du graphe à la date t : nœud → liste triée de (voisin, fait qui les relie)."""
        v: dict[str, list[tuple[str, Fait]]] = {}
        for f in self.faits_le(t):
            if f.relation in ATTRIBUTS or (relations is not None and f.relation not in relations):
                continue
            v.setdefault(f.sujet, []).append((f.objet, f))
            v.setdefault(f.objet, []).append((f.sujet, f))
        return {n: sorted(l, key=lambda x: (x[0], x[1].relation)) for n, l in sorted(v.items())}


# ---------------------------------------------------------------- extraction par règles (à la place d'un LLM)
REGLES = [
    (re.compile(r"^(?P<s>.+?) a son siège (?:à |au |dans l'|dans le )(?P<o>.+)$"), [("s", "siege_a", "o")]),
    (re.compile(r"^(?P<s>.+?) est une filiale de (?P<o>.+)$"), [("s", "filiale_de", "o")]),
    (re.compile(r"^(?P<s>.+?) détient la licence (?P<l>L-\d+), délivrée par (?:la |le |l')(?P<a>.+)$"),
     [("s", "detient", "l"), ("l", "delivree_par", "a")]),
    (re.compile(r"^(?:La |Le |L')(?P<s>.+?) est située? à (?P<o>.+)$"), [("s", "situee_a", "o")]),
    (re.compile(r"^La licence (?P<s>L-\d+) est (?P<o>active|suspendue|révoquée)$"), [("s", "statut", "o")]),
]


def extraire(doc_id: str, quand: date | None, texte: str) -> tuple[list[Fait], list[str]]:
    """Chaque phrase est confrontée aux règles dans l'ordre ; une phrase sans règle est rendue, pas devinée."""
    faits, rejets = [], []
    for i, phrase in enumerate(p.strip().rstrip(".") for p in texte.split(". ") if p.strip()):
        for motif, gabarits in REGLES:
            m = motif.match(phrase)
            if m:
                faits += [Fait(m[s], r, m[o], f"{doc_id}#{i + 1}", quand) for s, r, o in gabarits]
                break
        else:
            rejets.append(f"{doc_id}#{i + 1} « {phrase} »")
    return faits, rejets


REGISTRE = [   # annonces fictives d'un registre ; entreprises et licences inventées, autorités et lieux réels
    ("ref-00", None, "La VARA est située à Dubaï. La RERA est située à Dubaï. La CBUAE est située à Abu Dhabi. "
                     "L'ADGM est située à Abu Dhabi."),
    ("reg-01", date(2019, 5, 1), "Delta Immobilier a son siège à Sharjah."),
    ("reg-02", date(2021, 7, 1), "Epsilon Assurances a son siège à Sharjah. "
                                 "Epsilon Assurances détient la licence L-404, délivrée par la CBUAE."),
    ("reg-03", date(2022, 1, 10), "Gamma Holding a son siège dans l'ADGM. Bêta Paiements est une filiale de Gamma Holding. "
                                  "Bêta Paiements a son siège à Abu Dhabi. "
                                  "Bêta Paiements détient la licence L-202, délivrée par la CBUAE."),
    ("reg-04", date(2023, 1, 1), "Delta Immobilier a son siège à Dubaï. "
                                 "Delta Immobilier détient la licence L-303, délivrée par la RERA."),
    ("reg-05", date(2024, 3, 1), "Alpha Courtage est une filiale de Gamma Holding. Alpha Courtage a son siège à Dubaï. "
                                 "Alpha Courtage détient la licence L-101, délivrée par la VARA. La licence L-101 est active. "
                                 "Le groupe prévoit de s'étendre à Ras Al Khaimah."),
    ("reg-06", date(2025, 6, 1), "La licence L-101 est suspendue."),
    ("reg-07", date(2025, 9, 1), "La licence L-101 est active."),
]


# ---------------------------------------------------------------- recherche locale et chemins
def boule(voisins: dict, graines: list[str], h: int) -> dict[str, int]:
    """BFS limité à h sauts : nœud → distance aux graines."""
    dist = {g: 0 for g in graines if g in voisins}
    file = deque(dist)
    while file:
        u = file.popleft()
        if dist[u] == h:
            continue
        for v, _ in voisins[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                file.append(v)
    return dist


def contexte_local(g: Graphe, t: date, question: str, h: int) -> list[str]:
    """Entités nommées dans la question, puis les faits valides dont les deux bouts sont à au plus h sauts."""
    v = g.voisins(t)
    graines = [n for n in v if n.lower() in question.lower()]
    b = boule(v, graines, h)
    lignes = [f"{f.sujet} —{f.relation}→ {f.objet} [{f.source}]" for f in g.faits_le(t)
              if f.sujet in b and (f.objet in b or f.relation in ATTRIBUTS)]
    return lignes


def plus_court_chemin(voisins: dict, depart: str, arrivee: str) -> list[tuple[str, Fait | None]] | None:
    """BFS complet : le premier passage sur un nœud se fait à sa distance minimale ; on remonte les parents."""
    if depart not in voisins or arrivee not in voisins:
        raise ValueError("entité absente du graphe")
    parent: dict[str, tuple[str, Fait] | None] = {depart: None}
    file = deque([depart])
    while file:
        u = file.popleft()
        if u == arrivee:
            break
        for v, f in voisins[u]:
            if v not in parent:
                parent[v] = (u, f)
                file.append(v)
    if arrivee not in parent:
        return None
    chemin, n = [], arrivee
    while parent[n] is not None:
        u, f = parent[n]
        chemin.append((n, f))
        n = u
    return [(depart, None)] + chemin[::-1]


def distances_par_relaxation(voisins: dict) -> dict[tuple[str, str], int]:
    """Vérification indépendante : d(u, v) ← min(d(u, v), d(u, w) + 1) jusqu'à stabilité (Bellman-Ford, poids 1)."""
    noeuds = list(voisins)
    d = {(u, u): 0 for u in noeuds}
    change = True
    while change:
        change = False
        for u in noeuds:
            for w in noeuds:
                if (u, w) not in d:
                    continue
                for v, _ in voisins[w]:
                    if d.get((u, v), 10 ** 9) > d[(u, w)] + 1:
                        d[(u, v)] = d[(u, w)] + 1
                        change = True
    return d


# ---------------------------------------------------------------- modularité et Louvain simplifié
def poids(voisins: dict) -> dict[str, dict[str, int]]:
    """Matrice d'adjacence pondérée A : nombre de faits entre deux nœuds."""
    A: dict[str, dict[str, int]] = {n: {} for n in voisins}
    for u, l in voisins.items():
        for v, _ in l:
            A[u][v] = A[u].get(v, 0) + 1
    return A


def modularite(A: dict[str, dict[str, int]], comm: dict[str, int]) -> float:
    """Q = Σ_c [ L_c / m − (d_c / 2m)² ] ; L_c poids interne de c, d_c somme des degrés de c."""
    m = sum(sum(l.values()) for l in A.values()) / 2
    if m == 0:
        raise ValueError("graphe sans arête : modularité indéfinie")
    L: dict[int, float] = {}
    D: dict[int, float] = {}
    for u, l in A.items():
        D[comm[u]] = D.get(comm[u], 0) + sum(l.values())
        for v, w in l.items():
            if comm[u] == comm[v]:
                L[comm[u]] = L.get(comm[u], 0) + w / 2          # chaque arête interne est vue deux fois
    return sum(L.get(c, 0) / m - (D[c] / (2 * m)) ** 2 for c in D)


def modularite_matrice(A: dict[str, dict[str, int]], comm: dict[str, int]) -> float:
    """Forme d'origine : (1/2m) Σ_ij [A_ij − k_i k_j / 2m] δ(c_i, c_j)."""
    k = {u: sum(l.values()) for u, l in A.items()}
    m = sum(k.values()) / 2
    return sum(A[i].get(j, 0) - k[i] * k[j] / (2 * m) for i in A for j in A if comm[i] == comm[j]) / (2 * m)


def louvain_local(A: dict[str, dict[str, int]]) -> tuple[dict[str, int], list[float]]:
    """Phase 1 de Louvain : chaque nœud rejoint la communauté voisine de gain ΔQ maximal, tant que Q augmente."""
    k = {u: sum(l.values()) for u, l in A.items()}
    m = sum(k.values()) / 2
    comm = {u: i for i, u in enumerate(A)}
    d_tot = {i: k[u] for u, i in comm.items()}
    gains: list[float] = []
    ameliore = True
    while ameliore:
        ameliore = False
        for u in A:
            ancienne = comm[u]
            d_tot[ancienne] -= k[u]                              # on retire u : il devient isolé
            liens: dict[int, float] = {}
            for v, w in A[u].items():
                if v != u:
                    liens[comm[v]] = liens.get(comm[v], 0) + w
            def gain(c: int) -> float:                           # ΔQ d'insertion de u isolé dans c
                return liens.get(c, 0) / m - d_tot.get(c, 0) * k[u] / (2 * m * m)
            meilleure = max(sorted(set(liens) | {ancienne}), key=lambda c: (gain(c), c == ancienne))
            if gain(meilleure) > gain(ancienne) + 1e-12:
                gains.append(gain(meilleure) - gain(ancienne))
                comm[u] = meilleure
                ameliore = True
            d_tot[comm[u]] = d_tot.get(comm[u], 0) + k[u]
    renum = {c: i for i, c in enumerate(sorted(set(comm.values()), key=lambda c: min(u for u in A if comm[u] == c)))}
    return {u: renum[c] for u, c in comm.items()}, gains


# ---------------------------------------------------------------- recherche globale : résumés puis map-reduce
def resume(g: Graphe, t: date, membres: set[str]) -> dict:
    """Résumé déterministe d'une communauté (un LLM le rédigerait en texte) : entreprises et licences par autorité."""
    faits = [f for f in g.faits_le(t) if f.sujet in membres]
    licences = {f.sujet: f.objet for f in faits if f.relation == "delivree_par"}
    return {"entreprises": sorted({f.sujet for f in faits if f.relation in ("siege_a", "detient", "filiale_de")}),
            "licences_par_autorite": {a: sum(1 for x in licences.values() if x == a) for a in sorted(set(licences.values()))}}


def map_reduce(resumes: list[dict]) -> dict[str, int]:
    """Map : chaque résumé donne ses comptes partiels ; reduce : on additionne."""
    total: dict[str, int] = {}
    for r in resumes:
        for a, n in r["licences_par_autorite"].items():
            total[a] = total.get(a, 0) + n
    return dict(sorted(total.items()))


def main() -> None:
    print("1. Extraction par règles")
    g = Graphe()
    rejets = []
    for doc_id, quand, texte in sorted(REGISTRE, key=lambda d: (d[1] is not None, d[1] or date.min)):
        faits, rej = extraire(doc_id, quand, texte)
        for f in faits:
            g.ajouter(f)
        rejets += rej
    print(f"  {len(REGISTRE)} documents → {len(g.faits)} faits ; phrase sans règle : {rejets}")
    assert len(g.faits) == 23 and rejets == ["reg-05#5 « Le groupe prévoit de s'étendre à Ras Al Khaimah »"]
    exemple = next(f for f in g.faits if f.relation == "delivree_par" and f.sujet == "L-101")
    print(f"  exemple : ({exemple.sujet}, {exemple.relation}, {exemple.objet}), source {exemple.source}, depuis {exemple.debut}")

    print("2. Faits datés : interroger le graphe à une date")
    for t in (date(2022, 6, 1), date(2025, 7, 15), date(2026, 1, 1)):
        print(f"  {t} : siège de Delta Immobilier = {g.valeur('Delta Immobilier', 'siege_a', t)} ;"
              f" statut de L-101 = {g.valeur('L-101', 'statut', t)}")
    assert g.valeur("Delta Immobilier", "siege_a", date(2022, 6, 1)) == "Sharjah"
    assert g.valeur("Delta Immobilier", "siege_a", date(2026, 1, 1)) == "Dubaï"
    assert g.valeur("L-101", "statut", date(2025, 7, 15)) == "suspendue" and g.valeur("L-101", "statut", date(2024, 1, 1)) is None
    ferme = next(f for f in g.faits if f.sujet == "Delta Immobilier" and f.objet == "Sharjah")
    assert ferme.fin == date(2023, 1, 1)
    bornes = sorted({f.debut for f in g.faits if f.debut} | {f.fin for f in g.faits if f.fin})
    for t in bornes:                                                    # invariant : une seule valeur à la fois
        for s, r in {(f.sujet, f.relation) for f in g.faits if f.relation in FONCTIONNELLES}:
            assert sum(1 for f in g.faits_le(t) if (f.sujet, f.relation) == (s, r)) <= 1
    try:
        g.ajouter(Fait("Delta Immobilier", "siege_a", "Ajman", "test", date(2020, 1, 1)))
    except ValueError:
        pass
    else:
        raise AssertionError("un fait antérieur au fait en cours aurait dû être refusé")

    T = date(2026, 1, 1)
    v = g.voisins(T)
    print(f"3. Recherche locale au {T} : {len(v)} nœuds, {sum(len(l) for l in v.values()) // 2} arêtes")
    for h in (1, 2):
        b = boule(v, ["Alpha Courtage"], h)
        print(f"  {h} saut(s) autour d'Alpha Courtage : {len(b)} nœuds")
    ctx = contexte_local(g, date(2025, 7, 15), "La société Alpha Courtage peut-elle opérer ?", 1)
    for ligne in ctx:
        print(f"    {ligne}")
    assert [len(boule(v, ["Alpha Courtage"], h)) for h in (1, 2)] == [4, 9]
    deg_max = max(len(l) for l in v.values())
    assert all(len(boule(v, [x], h)) <= 1 + deg_max * sum((deg_max - 1) ** j for j in range(h)) for x in v for h in (1, 2, 3))
    assert "L-101 —statut→ suspendue [reg-06#1]" in ctx

    print("4. Multi-sauts : plus court chemin par BFS")
    regl = g.voisins(T, {"filiale_de", "detient", "delivree_par"})
    chemin = plus_court_chemin(regl, "Alpha Courtage", "CBUAE")
    print("  " + " ; ".join(n if f is None else f"{f.relation} → {n}" for n, f in chemin))
    assert [n for n, _ in chemin] == ["Alpha Courtage", "Gamma Holding", "Bêta Paiements", "L-202", "CBUAE"]
    tout = plus_court_chemin(v, "Alpha Courtage", "CBUAE")
    print(f"  sans filtre de relations : {len(tout) - 1} sauts par {', '.join(n for n, _ in tout[1:-1])}")
    d = distances_par_relaxation(v)
    for u in v:
        for w in v:
            c = plus_court_chemin(v, u, w)
            assert (c is None and (u, w) not in d) or (c is not None and len(c) - 1 == d[(u, w)])
    print(f"  BFS = relaxation sur les {len(v) ** 2} couples de nœuds")

    print("5. Modularité à la main : deux triangles reliés par un pont")
    tri = {"a": {"b": 1, "c": 1}, "b": {"a": 1, "c": 1}, "c": {"a": 1, "b": 1, "d": 1},
           "d": {"c": 1, "e": 1, "f": 1}, "e": {"d": 1, "f": 1}, "f": {"d": 1, "e": 1}}
    partitions = {"deux triangles": dict(a=0, b=0, c=0, d=1, e=1, f=1), "une seule": dict.fromkeys(tri, 0),
                  "singletons": {u: i for i, u in enumerate(tri)}, "trois paires": dict(a=0, b=0, c=1, d=1, e=2, f=2)}
    for nom, p in partitions.items():
        q1, q2 = modularite(tri, p), modularite_matrice(tri, p)
        print(f"  {nom:<15} Q = {q1:.4f}")
        assert abs(q1 - q2) < 1e-12
    assert round(modularite(tri, partitions["deux triangles"]), 4) == round(5 / 14, 4) == 0.3571
    assert round(modularite(tri, partitions["singletons"]), 4) == round(-34 / 196, 4)
    comm_tri, gains_tri = louvain_local(tri)
    assert comm_tri == partitions["deux triangles"]
    assert abs(modularite(tri, partitions["singletons"]) + sum(gains_tri) - modularite(tri, comm_tri)) < 1e-12
    print(f"  Louvain retrouve les deux triangles en {len(gains_tri)} déplacements, chacun de gain > 0")

    print(f"6. Communautés du graphe au {T} (Louvain, phase locale)")
    A = poids(v)
    comm, gains = louvain_local(A)
    q = modularite(A, comm)
    groupes = [sorted(u for u in A if comm[u] == c) for c in sorted(set(comm.values()))]
    for i, gr in enumerate(groupes):
        print(f"  C{i} : {', '.join(gr)}")
    print(f"  Q = {q:.4f} après {len(gains)} déplacements")
    assert all(x > 0 for x in gains) and abs(modularite(A, {u: i for i, u in enumerate(A)}) + sum(gains) - q) < 1e-12
    assert len(groupes) == 5 and round(q, 4) == 0.4626

    question_globale = "Combien de licences chaque autorité a-t-elle délivrées ?"
    print(f"7. Recherche globale : « {question_globale} »")
    locale = contexte_local(g, T, question_globale, 2)
    print(f"  recherche locale : {len(locale)} fait (aucune entité nommée dans la question)")
    assert locale == []
    resumes = [resume(g, T, set(gr)) for gr in groupes]
    for i, r in enumerate(resumes):
        print(f"  map C{i} : entreprises {r['entreprises']} ; licences {r['licences_par_autorite']}")
    total = map_reduce(resumes)
    direct: dict[str, int] = {}
    for f in g.faits_le(T):
        if f.relation == "delivree_par":
            direct[f.objet] = direct.get(f.objet, 0) + 1
    print(f"  reduce : {total} ; calcul direct sur tout le graphe : {dict(sorted(direct.items()))}")
    assert total == dict(sorted(direct.items())) == {"CBUAE": 2, "RERA": 1, "VARA": 1}
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Extraction par règles
  8 documents → 23 faits ; phrase sans règle : ["reg-05#5 « Le groupe prévoit de s'étendre à Ras Al Khaimah »"]
…
  2022-06-01 : siège de Delta Immobilier = Sharjah ; statut de L-101 = None
  2025-07-15 : siège de Delta Immobilier = Dubaï ; statut de L-101 = suspendue
…
  2 saut(s) autour d'Alpha Courtage : 9 nœuds
…
    L-101 —statut→ suspendue [reg-06#1]
…
  Alpha Courtage ; filiale_de → Gamma Holding ; filiale_de → Bêta Paiements ; detient → L-202 ; delivree_par → CBUAE
  sans filtre de relations : 4 sauts par Gamma Holding, ADGM, Abu Dhabi
…
  deux triangles  Q = 0.3571
  Louvain retrouve les deux triangles en 5 déplacements, chacun de gain > 0
…
  Q = 0.4626 après 16 déplacements
…
  reduce : {'CBUAE': 2, 'RERA': 1, 'VARA': 1} ; calcul direct sur tout le graphe : {'CBUAE': 2, 'RERA': 1, 'VARA': 1}
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un GraphRAG se construit sans base spécialisée ni modèle, avec des triplets datés, des listes d'adjacence et trois algorithmes classiques, BFS, Louvain et map-reduce. La date fait partie de la question : le même graphe répond « suspendue » le 15 juillet 2025 et « active » le 1er janvier 2026.

## Squelette algorithmique

Quatre algorithmes : tenir la mémoire datée, chercher localement ou par chemin, découper en communautés, répondre globalement. Le parcours en largeur reviendra, pour les graphes de tâches, aux [étapes 42 à 45](<../08-Orchestration/42-Orchestration-Graphes.md>).

```text
ALGORITHME AjouterFaitDaté
ENTRÉES : graphe, fait f = (s, r, o, source, début)
  SI r est fonctionnelle ALORS
      ancien ← le fait ouvert (sans fin) de même s et même r, s'il existe
      SI ancien existe ET ancien.o = o ALORS RETOURNER                    (fait répété)
      SI ancien existe ET f.début < ancien.début ALORS ERREUR « historique à réécrire »
      SI ancien existe ALORS ancien.fin ← f.début                         (on ferme, on n'efface pas)
  ajouter f au graphe

ALGORITHME ValeurÀLaDate(s, r, t)
  RETOURNER l'objet du fait de sujet s et de relation r tel que début ≤ t < fin, ou « aucun »
```

**Complexité.** L'ajout parcourt les faits existants : O(F) pour F faits, ramené à O(1) avec un index sur (sujet, relation). La valeur à une date coûte O(F) sans index, O(log F) avec les faits d'un couple triés par date. La mémoire vaut O(F), parce que rien n'est effacé.

**Du squelette au code.** `AjouterFaitDaté` est `Graphe.ajouter`, et `ValeurÀLaDate` est `Graphe.valeur`, qui s'appuie sur `faits_le` et `Fait.valide_le`.

```text
ALGORITHME RechercheLocale(question, t, h)
  graines ← entités du graphe à la date t dont le nom figure dans la question
  distance ← BFS depuis les graines, sans développer les nœuds à distance h
  RETOURNER les faits valides à t entre nœuds de distance ≤ h, et les attributs de ces nœuds, avec leur source

ALGORITHME PlusCourtChemin(x, y, relations autorisées)
  parent[x] ← aucun ; file ← (x)
  TANT QUE la file n'est pas vide FAIRE
      u ← retirer la tête de la file
      SI u = y ALORS sortir
      POUR CHAQUE voisin v de u par une relation autorisée FAIRE
          SI v n'a pas de parent ALORS parent[v] ← (u, fait) ; ajouter v à la file
      FIN POUR
  FIN TANT QUE
  SI y n'a pas de parent ALORS RETOURNER « pas de chemin »
  RETOURNER le chemin obtenu en remontant les parents depuis y
```

**Complexité.** Les deux parcours coûtent O(V + E) au pire. La recherche locale ne visite que la boule, dont la taille est bornée par 1 + Δ Σ (Δ − 1)ʲ (point 2). La mémoire vaut O(V) pour les distances, les parents et la file.

**Du squelette au code.** `RechercheLocale` est `contexte_local`, qui appelle `boule`. `PlusCourtChemin` est `plus_court_chemin`, appliqué à `voisins(t, relations)` pour le filtre. `distances_par_relaxation` sert seulement à vérifier les distances.

```text
ALGORITHME LouvainPhaseLocale(A)
  chaque nœud forme sa propre communauté
  RÉPÉTER
      POUR CHAQUE nœud i FAIRE
          retirer i de sa communauté a
          POUR CHAQUE communauté C voisine de i, et a FAIRE
              gain(C) ← k(i, C) / m − d(C) × k(i) / (2m²)
          FIN POUR
          SI max gain(C) > gain(a) ALORS mettre i dans la meilleure C   (Q augmente strictement)
          SINON remettre i dans a
      FIN POUR
  JUSQU'À ce qu'aucun nœud ne bouge
  RETOURNER les communautés

ALGORITHME RechercheGlobale(question additive)
  POUR CHAQUE communauté c FAIRE  partiel(c) ← compte de la question dans c   (map, sur le résumé de c)  FIN POUR
  RETOURNER la somme des partiels                                             (reduce)
```

**Complexité.** Un passage de Louvain coûte O(E), parce que chaque nœud lit ses liens une fois et que chaque gain se calcule en O(1) grâce à `d_tot`. Le nombre de passages est petit en pratique, mais il n'a pas de borne simple. La modularité se calcule en O(V + E). Le map-reduce coûte un appel par communauté plus une addition : O(nombre de communautés) appels au lieu d'une lecture de tout le corpus.

**Du squelette au code.** `LouvainPhaseLocale` est `louvain_local`, avec `liens`, `d_tot` et la fonction interne `gain`. `modularite` mesure le résultat, et `modularite_matrice` le vérifie. `RechercheGlobale` correspond à `resume` (map) puis `map_reduce` (reduce).

## Cas d'usage réels aux Émirats

Les entreprises, les licences, les montants et les seuils ci-dessous sont illustratifs ; seules les autorités et les règles citées sont réelles.

### Banque — l'exposition d'un groupe, chemin par chemin

Une banque de détail de Dubaï reçoit une demande de crédit d'une société cliente. Son équipe KYC a construit un graphe à partir des licences commerciales, des statuts et des registres d'actionnaires fournis par les clients, avec les relations filiale_de, détenue_par et administrée_par. Avant d'instruire la demande, l'agent cherche par BFS, en ne suivant que ces trois relations, les autres emprunteurs reliés à la société en au plus trois sauts. Il trouve deux sociétés sœurs, déjà débitrices de 6 et 5 millions d'AED, alors que la demande porte sur 4 millions : l'exposition du groupe atteindrait 15 millions, au-delà d'une limite interne de 12 millions (chiffres illustratifs). Il ne refuse pas : il transmet le dossier au comité de crédit avec le chemin trouvé et la source de chaque lien. Les liens sont datés. Une filiale cédée en mars 2025 sort du groupe à cette date, et l'agent interroge le graphe à la date de la décision, pas à la date de la dernière mise à jour. Sans le graphe, chaque crédit serait vu isolément, et la concentration sur un même groupe passerait inaperçue jusqu'au premier défaut. La lutte contre le blanchiment impose de connaître la structure de propriété des clients (à confirmer avec les règles de la CBUAE en vigueur). On suit la part des liens de groupe confirmés par les analystes et le nombre de liens rejetés comme erronés.

### Immobilier — la licence du courtier à la date de la transaction

Une agence immobilière de Dubaï travaille avec des courtiers indépendants, dont chacun doit détenir une licence de la RERA. Son graphe relie chaque transaction au courtier qui l'a menée, et chaque courtier à sa licence, dont le statut est un fait daté, tiré des annonces du registre. Un acheteur conteste aujourd'hui une commission versée pour une vente du 15 juillet 2025. L'agent ne demande pas « la licence est-elle active ? », mais « l'était-elle le 15 juillet 2025 ? ». C'est exactement la différence entre « active » le 1er janvier 2026 et « suspendue » le 15 juillet 2025 dans le programme (point 1). Une mémoire qui écrase le statut à chaque mise à jour donnerait la mauvaise réponse avec assurance. Le graphe garde aussi l'historique des transferts du bien auprès du DLD, avec les frais de 4 % de la valeur payés à chaque vente, et les contrats de location enregistrés sur Ejari. L'agent peut ainsi reconstituer la chaîne d'un bien de vente en vente, en citant chaque source. On suit la part des transactions dont la licence du courtier est vérifiée à la date de la transaction, avec un objectif de 100 %.

### Crypto — des communautés de portefeuilles qui tournent en rond

Une plateforme d'actifs virtuels agréée par la VARA tient un graphe des transferts entre portefeuilles, et des portefeuilles vers les entités identifiées par le KYC. L'équipe de surveillance lance Louvain chaque nuit sur la fenêtre des trente derniers jours. Une communauté de 14 portefeuilles se détache avec une contribution à Q élevée : presque tous ses transferts restent à l'intérieur, alors que leurs titulaires déclarent des activités sans lien. C'est le motif des allers-retours destinés à gonfler artificiellement des volumes, que la détection de cycles de l'étape 45 aide ensuite à confirmer (chiffres illustratifs). Pour expliquer l'alerte, l'agent prend le voisinage à deux sauts du portefeuille le plus actif. Il ne développe pas les nœuds « carrefours », comme les grandes plateformes d'échange, dont le degré ferait exploser la boule (point 2) et noierait l'analyste sous des milliers de transferts sans rapport. L'alerte reste un signal : un analyste examine la communauté avant toute déclaration, conformément aux obligations de lutte contre le blanchiment de la plateforme (à confirmer avec le règlement de la VARA). On suit la part des communautés signalées que les analystes confirment, et le temps d'examen par alerte.

### RH — le régime qui dépend de l'employeur et de la date

Un cabinet RH présent dans plusieurs émirats tient la mémoire de carrière de chaque salarié sous forme de faits datés : emploi chez un employeur, du début à la fin du contrat, et siège de l'employeur, dans une zone franche ou non. Pour une demande d'indemnité de fin de service, l'agent suit le chemin salarié → employeur → siège → régime. Si le siège est hors des zones franches financières, le décret-loi fédéral 33/2021 s'applique. S'il est au DIFC, le régime d'épargne DEWS remplace l'indemnité, comme à l'étape 30 sexies. Pour un contrat du 1er mars 2018 au 1er mars 2025 chez un employeur basé à Dubaï, hors zone franche, et un salaire de base de 10 000 AED, les dates donnent 7 années de service. La formule canonique donne alors 5 × 21 × 10 000/30 + 2 × 30 × 10 000/30 = 55 000 AED, sous le plafond de 24 mois de salaire. Le calcul passe par l'outil déterministe du parcours, jamais par le texte généré. Si l'employeur a changé de siège pendant le contrat, le graphe le montre par deux faits successifs, et l'agent transmet le dossier à un juriste au lieu de trancher. Toute réponse reste à confirmer avec le texte en vigueur. On suit la part des dossiers où le régime retenu par l'agent est confirmé par le juriste.

### Secteur public — compter les démarches qui exigent l'Emirates ID

Une entité de services publics en ligne, accessible par UAE Pass, décrit ses démarches sous forme de faits : démarche → exige → document, document → délivré_par → autorité, démarche → disponible_dans → émirat. Un responsable demande : « Combien de démarches exigent l'Emirates ID, par émirat ? ». La question ne nomme aucune démarche, et une recherche par passages n'en verrait que les dix premières. La recherche globale répond par map-reduce sur les communautés de démarches : chaque communauté compte ses démarches qui exigent le document, et l'on additionne. Comme le compte est additif et que les communautés forment une partition, le résultat est exact (point 6). Une condition est indispensable : la **résolution d'entités**. « Emirates ID », la carte d'identité émiratie et son nom arabe doivent être un seul nœud, grâce à une table d'alias et à la normalisation de l'arabe (alef, ta marbuta, diacritiques). Sinon, le compte se répartit entre trois nœuds et chaque sous-total paraît trop faible. Le graphe ne contient que des métadonnées de démarches, aucune donnée personnelle d'usager, ce qui le tient hors du champ de la PDPL pour les usagers. On suit l'écart entre les comptes du graphe et le catalogue officiel des démarches, revu chaque trimestre.

### Assurance — un garage, trois numéros de téléphone, vingt sinistres

Un assureur auto et santé relie chaque sinistre au garage qui a fait la réparation, au numéro de téléphone déclaré et à l'assuré. Louvain fait apparaître une communauté inhabituellement dense : vingt sinistres en six mois, un seul garage, trois numéros de téléphone partagés entre onze assurés qui ne se connaissent pas officiellement (chiffres illustratifs). Sa contribution à Q dépasse largement celle des autres communautés de même taille, parce que ses arêtes restent presque toutes internes, comme les triangles du point 4. L'agent prépare pour l'enquêteur le voisinage à un saut du garage, chaque lien avec sa source (déclaration, facture, appel), et le chemin le plus court entre deux assurés qui disent ne pas se connaître. L'enquêteur décide ; l'agent ne refuse aucun paiement. Le graphe contient des données personnelles : il ne garde que les liens nécessaires à la lutte contre la fraude, avec une durée de conservation définie, conformément à la PDPL, et l'assurance est supervisée par la CBUAE. On suit la part des communautés signalées qui mènent à une fraude confirmée, et la part des liens contestés par les assurés.

## Pièges et limites

- **Prendre un triplet extrait pour un fait vérifié.** Un extracteur à LLM invente des relations avec aplomb ; les règles sont précises mais manquent ce qu'elles ne prévoient pas. On garde la source de chaque fait, on valide les relations critiques et on mesure la précision et le rappel de l'extraction sur un échantillon annoté.
- **Oublier la résolution d'entités.** « Dubaï », « Dubai » et le nom arabe doivent être un seul nœud, sinon le graphe se fragmente et les comptes globaux sont faux.
- **Développer les carrefours.** Un émirat ou une grande autorité relie presque tout : sans filtre de relations, plafond de degré ou h petit, la recherche locale renvoie le graphe entier (point 2).
- **Écraser au lieu de dater.** Une mise à jour qui remplace le statut perd la réponse à « à la date du contrat ». À l'inverse, fermer un fait n'est pas l'effacer : une demande d'effacement au titre de la PDPL demande une vraie suppression.
- **Croire que la modularité dit la vérité.** Louvain s'arrête sur un optimum local et peut produire des communautés mal connexes ; la modularité a aussi une limite de résolution, qui fusionne de petites communautés dans un grand graphe. Une communauté est un indice à examiner, pas une conclusion.

### Exercice feuille blanche

1. Sans regarder le code, écrire `modularite` à partir de la seconde forme, puis retrouver 5/14 ≈ 0,3571 pour les deux triangles et 0 pour une seule communauté.
2. Prédire, puis vérifier : dans le graphe des deux triangles, que vaut le gain d'insérer a, isolé, dans {b} ? Et dans {c} ? (Réponse : 1/7 − 2 × 2/98 ≈ 0,102, et 1/7 − 3 × 2/98 ≈ 0,0816 ; Louvain choisit b.) Quelle borne la formule du point 2 donne-t-elle pour h = 3 et Δ = 4 ? (Réponse : 1 + 4 × (1 + 3 + 9) = 53.)
3. Trouver le bug : dans `Graphe.ajouter`, on supprime la ligne `ancien.fin = f.debut`. Que répond `valeur("Delta Immobilier", "siege_a", date(2026, 1, 1))`, et que devient le statut de L-101 le 15 juillet 2025 ? (Réponse : les deux sièges sont valides en même temps et `valeur` renvoie le premier inséré, « Sharjah ». Pour L-101, le fait « active » de 2024 reste ouvert, le retour à « active » de septembre 2025 est pris pour un doublon, et le 15 juillet 2025 la réponse est « active » au lieu de « suspendue ». L'invariant du point 1 est violé.)

## Pour aller plus loin

L'algorithme de Leiden (Traag et al., 2019) corrige les communautés mal connexes de Louvain. La seconde phase de Louvain, que ce fichier n'implémente pas, agrège chaque communauté en un super-nœud et recommence, ce qui donne une hiérarchie de communautés. Le GraphRAG décrit par Edge et al. (2024) construit ces communautés à plusieurs niveaux, fait rédiger leurs résumés par un LLM, puis répond aux questions globales par un map-reduce qui note l'utilité de chaque réponse partielle. D'autres approches combinent le graphe et les vecteurs : on cherche d'abord des nœuds par similarité, puis on propage la pertinence dans le graphe, par exemple avec un PageRank personnalisé. Les graphes de connaissances **bitemporels** distinguent le temps de validité d'un fait du temps où l'agent l'a appris, ce qui permet de répondre à « que croyais-tu le 1er mars ? ». Côté stockage, le modèle RDF et son langage SPARQL, les bases de graphes du marché ou une simple table relationnelle avec une requête récursive implémentent tous les mêmes opérations que ce fichier.

> Étape 30 septies du parcours · Prérequis : [Corrective RAG et Agentic RAG](<30f-RAG-Corrective-et-Agentic-RAG.md>) · Suite : [Attention par produit scalaire](<../06-Attention-et-Transformer/31-Attention-Formule-Produit-Scalaire-Normalise.md>)
