# Étape 42 — Théorie des Graphes Orientés Acycliques (DAG) et Matrices d'Adjacence

> Étape 42 du parcours · Prérequis : [Score de priorité de tâche](<41-Orchestration-Formule-Score-de-Priorite.md>) · Suite : [Fondements : DAG, nilpotence et tri topologique](<43-Fondements-Orchestration-et-DAG.md>)

**Dossier :** 08-Orchestration  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Platform Team, AI Agent Ops  
**Nom du fichier :** 42-Orchestration-Graphes.md

## Définition

Un graphe orienté est un ensemble de nœuds (des tâches ou des agents) reliés par des arcs orientés (des dépendances ou des flux de données). Une **marche** de longueur k est une suite de k arcs qui s'enchaînent, où l'on a le droit de repasser par un même nœud ; un **chemin** est une marche qui ne repasse jamais par un nœud ; un **cycle** est un chemin qui revient à son point de départ. Un graphe orienté acyclique, ou **DAG** (Directed Acyclic Graph), est un graphe sans cycle : il est impossible de suivre les arcs pour revenir à son point de départ. La **matrice d'adjacence** A d'un graphe à n nœuds est le tableau n × n qui contient 1 en ligne i et colonne j quand un arc va de i vers j, et 0 sinon. Ses puissances comptent les marches, sa trace compte les marches qui reviennent à leur départ, et ses colonnes donnent les degrés entrants : trois outils pour vérifier un graphe de tâches avant de l'exécuter.

## Rôle dans un agent

Un orchestrateur multi-agents manipule deux graphes qu'il ne faut pas confondre. Le **graphe de contrôle** dit quel agent parle après quel autre ; il peut contenir des boucles voulues (agir, observer, recommencer ; rédiger, relire, corriger), et des frameworks comme LangGraph les autorisent, en les bornant par une limite de récursion (`recursion_limit`) qui arrête le graphe au-delà d'un nombre d'étapes. Le **graphe de dépendances** dit quelle tâche a besoin du résultat de quelle autre ; lui doit être un DAG, sinon certaines tâches ne peuvent jamais démarrer. Au chargement d'un workflow, avant d'agir, l'orchestrateur vérifie que le graphe de dépendances est acyclique, calcule les **vagues** de tâches qui peuvent partir en parallèle, puis le **chemin critique**, qui donne la latence minimale du workflow et dit où optimiser. Ces calculs sont du code déterministe, sans modèle.

## Équation complète

Matrice d'adjacence :

$$
A_{i,j} = \begin{cases} 1 & \text{si un arc va du nœud } i \text{ au nœud } j \\ 0 & \text{sinon} \end{cases}
$$

Puissances et marches :

$$
(A^k)_{i,j} = \sum_{l=1}^{n} (A^{k-1})_{i,l}\, A_{l,j} = \text{nombre de marches de longueur } k \text{ de } i \text{ à } j
$$

Trace et marches fermées :

$$
\mathrm{Tr}(A^k) = \sum_{i=1}^{n} (A^k)_{i,i} = \text{nombre de marches fermées de longueur } k
$$

Caractérisation d'un DAG :

$$
G \text{ est un DAG} \iff A^n = 0 \iff \mathrm{Tr}(A^k) = 0 \;\; \text{pour } k = 1, \dots, n
$$

Degré entrant :

$$
d_{\mathrm{in}}(j) = \sum_{i=1}^{n} A_{i,j}
$$

Chemin critique, avec une durée d(v) par tâche et des ouvriers en nombre suffisant :

$$
\mathrm{fin}(v) = d(v) + \max_{u \to v} \mathrm{fin}(u) , \qquad T_{\mathrm{CP}} = \max_v \mathrm{fin}(v)
$$

Durée d'un calendrier synchronisé par vagues, qui n'est qu'une borne supérieure :

$$
T_{\mathrm{vagues}} = \sum_{\text{vagues } W} \max_{v \in W} d(v) \;\ge\; T_{\mathrm{CP}}
$$

## Décryptage des symboles

$$
n,\; i,\; j,\; l
$$

**Sens :** nombre de nœuds ; indices d'un nœud de départ, d'arrivée et d'un nœud intermédiaire · **Type / plage :** entiers de 0 à n − 1 dans le code · **Variable Python :** `len(A)`, `i`, `j`, `l`

$$
A_{i,j}
$$

**Sens :** 1 si la tâche i alimente la tâche j (j doit attendre i), 0 sinon · **Type / plage :** 0 ou 1 · **Variable Python :** `A[i][j]`

$$
(A^k)_{i,j}
$$

**Sens :** nombre de marches de longueur k de i à j · **Type / plage :** entier ≥ 0 · **Variable Python :** `matpow(A, k)[i][j]`

$$
\mathrm{Tr}(M)
$$

**Sens :** trace : somme des éléments de la diagonale ; sur Aᵏ, nombre de marches fermées de longueur k, et non nombre de cycles · **Type / plage :** entier ≥ 0 · **Variable Python :** `trace(M)`

$$
d_{\mathrm{in}}(j)
$$

**Sens :** degré entrant : nombre de tâches dont j dépend directement, somme de la colonne j · **Type / plage :** entier ≥ 0 · **Variable Python :** `degres_entrants(A)[j]`, `entrant[j]` dans Kahn

$$
d(v),\; \mathrm{fin}(v)
$$

**Sens :** durée de la tâche v, et instant où elle se termine au plus tôt quand elle démarre dès que tous ses prérequis sont finis · **Type / plage :** réels ≥ 0, en secondes · **Variable Python :** `durees[v]`, `fin[v]`

$$
T_{\mathrm{CP}},\; T_{\mathrm{vagues}}
$$

**Sens :** durée du chemin critique (la vraie latence minimale) et durée d'un calendrier où chaque vague attend la plus lente de la vague précédente · **Type / plage :** réels ≥ 0, avec T_vagues ≥ T_CP · **Variable Python :** `max(fin)`, `duree_par_vagues(vagues, durees)`

## Démonstration

### 1. (Aᵏ)ᵢ,ⱼ compte les marches de longueur k

Par récurrence sur k. Pour k = 1, (A¹)ᵢ,ⱼ = Aᵢ,ⱼ vaut 1 exactement quand l'arc i → j existe, c'est-à-dire quand il existe une marche de longueur 1 de i à j. Supposons le résultat vrai au rang k − 1. Une marche de longueur k de i à j se coupe de façon unique en une marche de longueur k − 1 de i vers un nœud l, suivie du dernier arc l → j. Pour chaque l, le nombre de telles marches vaut (Aᵏ⁻¹)ᵢ,ₗ × Aₗ,ⱼ : le nombre de débuts possibles, multiplié par 1 si le dernier arc existe et par 0 sinon. En additionnant sur tous les l, on obtient exactement le produit matriciel :

$$
(A^k)_{i,j} = \sum_{l=1}^{n} (A^{k-1})_{i,l}\, A_{l,j}
$$

Sur le pipeline du code, (A²)₀,₃ = A₀,₁ A₁,₃ + A₀,₂ A₂,₃ = 1 × 1 + 1 × 1 = 2 : deux marches du scraper au rédacteur, l'une par l'analyste réglementaire, l'autre par l'analyste de sentiment.

### 2. La trace compte des marches fermées, pas des cycles

Par le point 1, (Aᵏ)ᵢ,ᵢ est le nombre de marches de longueur k qui partent de i et y reviennent ; la trace les additionne sur tous les points de départ. Une marche fermée peut repasser plusieurs fois par le même nœud, ce n'est donc pas forcément un cycle. Avec un seul cycle 0 → 1 → 0 :

$$
\mathrm{Tr}(A^2) = 2 , \qquad \mathrm{Tr}(A^3) = 0 , \qquad \mathrm{Tr}(A^4) = 2
$$

Le graphe n'a aucun cycle de longueur 4, mais il a deux marches fermées de longueur 4 : 0 → 1 → 0 → 1 → 0 et 1 → 0 → 1 → 0 → 1. Même un vrai cycle est compté plusieurs fois : un triangle 0 → 1 → 2 → 0 donne Tr(A³) = 3, une marche fermée par point de départ. L'ancienne phrase « Tr(Aᵏ) est le nombre de cycles de longueur k » est donc fausse ; ce qui est vrai, c'est que la trace est nulle ou non selon qu'il existe ou non une marche fermée.

### 3. DAG ⇔ Tr(Aᵏ) = 0 pour k = 1, …, n

- **Si G a un cycle**, prenons un cycle de longueur L. Comme un cycle ne repasse par aucun nœud, il en visite L distincts, donc L ≤ n. En partant de n'importe lequel de ses nœuds, on obtient une marche fermée de longueur L : (Aᴸ)ᵢ,ᵢ ≥ 1, donc Tr(Aᴸ) > 0 avec L ≤ n.
- **Si G est un DAG**, il n'a aucune marche fermée de longueur k ≥ 1. En effet, une marche fermée contient un cycle : on suit la marche jusqu'au premier nœud qui se répète, et le morceau entre ses deux passages est un chemin qui revient à son départ. Toutes les traces sont donc nulles.

Il suffit de tester k = 1, …, n, et non « toutes les puissances k > 0 » comme le disait l'ancienne version : au-delà de n, la trace n'apporte aucune information nouvelle.

### 4. DAG ⇔ Aⁿ = 0 (A est nilpotente)

- **Si G est un DAG**, une marche de longueur n visite n + 1 nœuds. Il n'y a que n nœuds, donc l'un d'eux se répète (principe des tiroirs), et la marche contient une marche fermée, donc un cycle (point 3) : c'est impossible. Il n'existe aucune marche de longueur n, et par le point 1, tous les coefficients de Aⁿ sont nuls.
- **Si G a un cycle de longueur L**, on peut le parcourir autant de fois que l'on veut : il existe des marches fermées de longueur L, 2L, 3L, …, donc Aᵏ ≠ 0 pour une infinité de k, et A n'est nilpotente pour aucune puissance.

Conséquence spectrale : si Av = λv avec v ≠ 0, alors Aⁿv = λⁿv = 0, donc λ = 0. Toutes les valeurs propres d'une matrice de DAG sont nulles. Sur le pipeline, n = 4 et l'on a même A³ = 0, parce que le plus long chemin n'a que 2 arcs : en général, A^(L+1) = 0 où L est la longueur du plus long chemin.

### 5. Les degrés entrants sont les sommes de colonnes

La colonne j de A contient un 1 pour chaque nœud i tel que i → j : sa somme est le nombre de prérequis directs de j. Sur le pipeline, les sommes des colonnes valent [0, 1, 1, 2] : le scraper n'attend personne, chaque analyste attend le scraper, le rédacteur attend les deux analystes. C'est exactement le tableau `entrant` que Kahn construit en lisant les arcs. Un DAG fini a toujours au moins une colonne nulle, une **source** : l'étape 44 le démontre et en tire la preuve de Kahn.

### 6. Les vagues de Kahn, et pourquoi leur somme n'est qu'une borne

Kahn produit des **vagues** : la vague 0 contient les sources, et une tâche entre dans la vague suivante dès que le dernier de ses prérequis est traité. Par récurrence, la vague d'une tâche v vaut 1 + le maximum des vagues de ses prérequis, c'est-à-dire la longueur, en nombre d'arcs, du plus long chemin d'une source jusqu'à v. En particulier, le long d'un arc u → v, la vague de v est strictement plus grande que celle de u.

L'ancienne fonction `temps_chemin_critique` additionnait le maximum de chaque vague. C'est la durée d'un calendrier **synchronisé**, où aucune tâche d'une vague ne démarre avant la fin de la plus lente de la vague précédente. Soit v₁ → v₂ → … → vₚ un chemin de durée maximale. Ses nœuds sont dans des vagues toutes différentes, puisque la vague croît strictement le long d'un arc ; et la vague qui contient vᵢ a un maximum au moins égal à d(vᵢ). En additionnant :

$$
T_{\mathrm{vagues}} = \sum_{W} \max_{v \in W} d(v) \;\ge\; \sum_{i=1}^{p} d(v_i) = T_{\mathrm{CP}}
$$

C'est une borne supérieure, pas le chemin critique. Contre-exemple : A (1 s) → C (10 s) et B (10 s) → D (1 s). Les vagues sont {A, B} puis {C, D}, et leur somme vaut 10 + 10 = 20 s : C attend la fin de B, dont il n'a pas besoin. Le vrai chemin critique vaut 11 s, A puis C ou B puis D. Sur le pipeline de l'exemple, les deux calculs donnent 13,4 s, et ce n'est pas un hasard : la plus lente de chaque vague (scraper, l'analyste réglementaire, rédacteur) se trouve sur un même chemin, ce qui est exactement le cas d'égalité de l'inégalité ci-dessus.

### 7. Le vrai chemin critique, par programmation dynamique

On prend les tâches dans un ordre topologique (celui de Kahn), si bien que tous les prérequis d'une tâche sont calculés avant elle, et l'on pose fin(v) = d(v) + max fin(u) sur ses prérequis u, ou fin(v) = d(v) si elle n'en a pas. Par récurrence dans cet ordre, fin(v) est la plus grande durée totale d'un chemin qui se termine par v : soit v n'a pas de prérequis, soit tout chemin qui finit en v passe par un prérequis u juste avant, et le meilleur d'entre eux vaut fin(u) + d(v). Avec des ouvriers en nombre suffisant, chaque tâche peut démarrer à l'instant max fin(u), et le workflow se termine à T_CP = max fin(v). On ne peut pas faire mieux, parce que les tâches d'un même chemin s'exécutent forcément l'une après l'autre. Le calcul lit chaque arc une fois : O(n + m) après le tri.

### 8. Exemple fait à la main (le code reprend ces nombres)

Pipeline à quatre agents, durées 4,2 s, 6,1 s, 5,8 s et 3,1 s.

| Quantité | Calcul | Valeur |
|---|---|---|
| (A²)[scraper, rédacteur] | 1 × 1 + 1 × 1 | 2 |
| A³ | aucune marche de longueur 3 | matrice nulle |
| degrés entrants | sommes des colonnes | [0, 1, 1, 2] |
| durée séquentielle | 4,2 + 6,1 + 5,8 + 3,1 | 19,2 s |
| durée par vagues | 4,2 + max(6,1 ; 5,8) + 3,1 | 13,4 s |
| chemin critique | scraper → sec_rag → rédacteur | 13,4 s |
| gain | (19,2 − 13,4) / 19,2 | 30,2 % |

Cycle à deux nœuds : Tr(A), Tr(A²), Tr(A³), Tr(A⁴) valent 0, 2, 0, 2. Contre-exemple des vagues : 20 s par vagues, 11 s en vrai.

## Effets et comportement

- **Ajouter un arc i → j retarde j** jusqu'à la fin de i. Si l'arc tombe sur le chemin critique, la latence du workflow augmente de la durée correspondante ; sinon, elle ne bouge pas tant que la marge de j suffit.
- **Ajouter un cycle dans le graphe de dépendances bloque l'exécution** : les tâches du cycle ne deviennent jamais prêtes, et Kahn le signale. Dans le graphe de contrôle, en revanche, une boucle est permise si elle est bornée (nombre d'itérations, limite de récursion) et qu'une condition de sortie existe.
- **Le parallélisme ne fait gagner que hors du chemin critique.** Accélérer l'analyste de sentiment (5,8 s) ne change rien ; accélérer l'analyste réglementaire (6,1 s) fait gagner jusqu'à 0,3 s, après quoi c'est le sentiment qui devient critique.
- **Coût des tests.** Calculer A, A², …, Aⁿ coûte O(n⁴) avec des produits naïfs ; Kahn répond à la même question en O(n + m). La matrice sert à raisonner et à démontrer ; Kahn sert en production.

## Du symbole au code Python

| Symbole | Variable ou fonction Python |
|---|---|
| A | `matrice(aretes, n)`, liste de listes de 0 et de 1 |
| produit, Aᵏ | `matmul(A, B)`, `matpow(A, k)` |
| Tr(Aᵏ) et le test du point 3 | `trace(M)`, `est_acyclique_par_trace(A)` |
| Aⁿ = 0 | `est_nulle(matpow(A, n))` |
| d_in(j) | `degres_entrants(A)` |
| vagues | `tri_kahn(aretes, n)` |
| T_vagues | `duree_par_vagues(vagues, durees)` |
| fin(v), T_CP, chemin critique | `calendrier_au_plus_tot(aretes, durees)` |

Copiez le bloc dans `dag_agents.py` et lancez `python dag_agents.py`.

### Déroulé, ligne par ligne

Les nœuds sont dans l'ordre `scraper=0`, `sec_rag=1`, `sentiment=2`, `redacteur=3`. `matrice(aretes, 4)` part d'une matrice de zéros et met un 1 pour chaque arc : ligne 0, colonnes 1 et 2 (le scraper alimente les deux analystes) ; colonne 3 des lignes 1 et 2 (les deux analystes alimentent le rédacteur).

**`matmul(A, B)`**, le produit de matrices, qui compte des marches quand A et B sont des matrices d'adjacence.

- Trois boucles : `i` choisit la ligne de départ, `j` la colonne d'arrivée, `l` le nœud intermédiaire.
- `C[i][j] += A[i][l] * B[l][j]` ajoute 1 seulement si une marche va de `i` à `l` dans A et une marche va de `l` à `j` dans B. Pour i = 0 et j = 3, le terme `l = 1` vaut 1 × 1 = 1, le terme `l = 2` vaut 1 × 1 = 1, les autres valent 0 : la case vaut 2.

**`matpow(A, k)`** répète cette multiplication. `resultat = A` (A¹ est A elle-même), puis la boucle tourne `k - 1` fois. Pour `k = 3`, A³ sort entièrement nulle : aucune marche de longueur 3 n'existe, parce que le plus long chemin du pipeline n'a que 2 arcs. Un `k` inférieur à 1 lève une `ValueError`.

**`trace(M)`** additionne `M[i][i]`, la diagonale seulement. **`est_nulle(M)`** vérifie que tous les coefficients valent 0.

**`degres_entrants(A)`** additionne chaque colonne : `[0, 1, 1, 2]`, le même tableau que celui que Kahn construit à partir des arcs.

**`est_acyclique_par_trace(A)`** calcule `trace(matpow(A, k))` pour `k` de 1 jusqu'à `n` inclus, comme le justifie le point 3. Au premier `k` dont la trace est positive, elle renvoie `(False, k)` ; sinon `(True, None)`. Sur le cycle à deux nœuds, elle s'arrête à `k = 2`.

**`tri_kahn(aretes, n)`** construit l'ordre et les vagues sans passer par les puissances de matrice.

- En lisant les arcs `(0, 1), (0, 2), (1, 3), (2, 3)`, `entrant` devient `[0, 1, 1, 2]` et `suivants[0]` vaut `[1, 2]`.
- `vague = [i for i in range(n) if restant[i] == 0]` : au départ, seulement `[0]`.
- Tant que `vague` n'est pas vide, on la range dans `vagues`, on ajoute ses nœuds à `ordre` et, pour chaque successeur, on fait `restant[v] -= 1`. Quand un successeur tombe à 0, il entre dans `suivante`. Le traitement du scraper fait tomber les deux analystes à 0 ; leur traitement fait tomber le rédacteur de 2 à 0.
- `if len(ordre) != n` : des nœuds n'ont jamais atteint un degré nul, il y a un cycle, et la fonction renvoie `(None, None)`. Sur les arcs `(0, 1), (1, 0)`, les deux degrés valent 1, la première vague est vide et la boucle ne démarre même pas.

**`duree_par_vagues(vagues, durees)`** additionne `max(durees[i] for i in vague)` sur les vagues : 4,2 + 6,1 + 3,1 = 13,4 s sur le pipeline. Le nom dit ce qu'elle calcule : la durée du calendrier synchronisé, une borne supérieure (point 6).

**`calendrier_au_plus_tot(aretes, durees)`** est le vrai calcul du point 7, sur une horloge simulée : aucune attente réelle, aucune heure réelle imprimée.

- `ordre, _ = tri_kahn(aretes, n)` donne un ordre topologique ; un cycle lève une `ValueError`.
- `preds[j]` liste les prérequis de chaque tâche.
- Pour chaque `v` dans l'ordre : s'il a des prérequis, `u = max(preds[v], key=lambda p: (fin[p], -p))` choisit celui qui finit le plus tard (à égalité, le plus petit indice), `debut[v] = fin[u]` et `venu_de[v] = u` retient d'où vient le chemin. Puis `fin[v] = debut[v] + durees[v]`.
- `dernier` est la tâche qui finit le plus tard ; en remontant `venu_de`, on reconstruit le chemin critique, puis on l'inverse.
- Sur le pipeline : le rédacteur démarre à `fin[sec_rag] = 4.2 + 6.1 = 10.3` et finit à 13,4 ; le chemin critique est `[0, 1, 3]`.

**`calendrier_par_vagues(vagues, durees)`** fait démarrer toute une vague à l'instant `t` où la plus lente de la précédente a fini. Sur le contre-exemple, C démarre à 10 au lieu de 1.

**`main()`**, bloc par bloc.

1. A² a un 2 en haut à droite ; A³ et A⁴ sont nulles ; les traces valent 0 ; les degrés entrants valent `[0, 1, 1, 2]`.
2. Le cycle à deux nœuds donne les traces `[0, 2, 0, 2]`, le triangle donne Tr(A³) = 3, et Kahn refuse le cycle.
3. Les vagues du pipeline, puis 19,2 s en séquentiel, 13,4 s par vagues, 13,4 s de chemin critique, un gain de 30,2 %.
4. Le contre-exemple : les deux calendriers tâche par tâche, 20 s contre 11 s. Le dernier `assert` vérifie la borne T_vagues ≥ T_CP sur trois graphes.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`matmul(A, B)`** — Cette fonction est le recenseur des itinéraires qui, pour chaque ville de départ et chaque ville d'arrivée, compte toutes les façons de passer par une ville intermédiaire : elle reçoit deux matrices A et B, crée une matrice de zéros, puis, avec trois boucles imbriquées, ajoute à chaque case (i, j) les produits A[i][l] × B[l][j] pour tous les intermédiaires l. Elle renvoie le produit A B ; sur des matrices d'adjacence, chaque case compte des marches, si bien que A² vaut 2 en haut à droite, pour les deux marches du scraper au rédacteur, l'une par chaque analyste.

**`trace(M)`** — Ce petit utilitaire est le gardien de nuit qui ne regarde que les allers-retours, les marches qui reviennent à leur point de départ : il reçoit une matrice carrée M et renvoie la somme de ses coefficients diagonaux. Appliqué à Aᵏ, il compte les marches fermées de longueur k, et non les cycles : il vaut 0 pour toutes les puissances du pipeline, 2 pour A² et A⁴ du cycle à deux nœuds, et 3 pour A³ du triangle, une marche fermée par point de départ.

**`est_nulle(M)`** — Cette fonction est l'inspecteur qui vérifie qu'une salle est vraiment vide, sans une seule chaise occupée : elle reçoit une matrice M et renvoie vrai si et seulement si tous ses coefficients valent 0. `main` s'en sert pour constater la nilpotence du pipeline, puisque A³ et A⁴ sont nulles, faute de chemin de plus de 2 arcs, et pour montrer qu'au contraire A² du cycle à deux nœuds ne l'est pas, ce qui trahit le cycle.

**`matrice(aretes, n)`** — Voici le cartographe qui transforme une liste de routes en tableau à double entrée : la fonction reçoit la liste des arcs, des couples (i, j), et le nombre n de nœuds, crée une matrice n × n remplie de zéros, puis met un 1 à la ligne i et à la colonne j pour chaque arc. Elle renvoie la matrice d'adjacence ; pour le pipeline à 4 nœuds, la ligne du scraper a des 1 dans les colonnes des deux analystes, et la colonne du rédacteur a des 1 dans leurs deux lignes.

**`degres_entrants(A)`** — Cette fonction joue le portier qui compte combien de flèches arrivent à chaque porte : elle reçoit une matrice d'adjacence carrée A et renvoie, pour chaque colonne j, la somme des coefficients de cette colonne, c'est-à-dire le nombre de prérequis de la tâche j. Sur le pipeline, elle renvoie `[0, 1, 1, 2]` : le scraper n'attend personne, chaque analyste attend le scraper et le rédacteur attend les deux analystes, le même tableau que celui que Kahn construit directement à partir des arcs.

**`est_acyclique_par_trace(A)`** — C'est le détective qui cherche un cycle en comptant les allers-retours de toutes les longueurs possibles : la fonction reçoit une matrice d'adjacence de taille n, calcule la trace de Aᵏ pour k allant de 1 à n et renvoie `(False, k)` au premier k dont la trace est positive, la preuve qu'une marche fermée existe. Si aucune trace n'est positive jusqu'à n, elle renvoie `(True, None)`, car un cycle a forcément une longueur au plus n ; le pipeline passe le test, alors que le cycle à deux nœuds est démasqué dès k = 2.

**`tri_kahn(aretes, n)`** — On peut la voir comme un chef de chantier qui fait entrer les équipes par vagues, chaque équipe dès que toutes celles dont elle dépend ont fini : la fonction reçoit la liste des arcs et le nombre de nœuds, compte les degrés entrants, forme la première vague des nœuds à 0, puis, vague après vague, range les nœuds dans l'ordre, décrémente le compteur de leurs successeurs et place dans la vague suivante ceux qui tombent à 0. Elle renvoie l'ordre topologique et la liste des vagues, `[[0], [1, 2], [3]]` sur le pipeline, ou `(None, None)` si des nœuds n'atteignent jamais un degré nul, signe d'un cycle.

**`duree_par_vagues(vagues, durees)`** — Cette fonction est le planificateur prudent qui fait attendre toute une vague jusqu'à ce que la plus lente de la précédente ait fini : elle reçoit la liste des vagues et la durée de chaque tâche, prend dans chaque vague la plus grande durée et additionne ces maxima. Elle renvoie la durée du calendrier synchronisé, une borne supérieure du vrai délai : 4,2 + 6,1 + 3,1 = 13,4 secondes sur le pipeline, où elle coïncide avec le chemin critique, mais 20 secondes dans le contre-exemple, où le vrai délai n'est que de 11.

**`calendrier_au_plus_tot(aretes, durees)`** — C'est le régisseur qui fait démarrer chaque tâche à la seconde même où son dernier prérequis se termine, sur une horloge simulée et avec autant d'ouvriers qu'il en faut : la fonction reçoit les arcs et les durées, obtient un ordre topologique par `tri_kahn` et lève une `ValueError` en cas de cycle, puis, dans cet ordre, fait commencer chaque tâche à la fin du prédécesseur qui finit le plus tard et mémorise ce prédécesseur. Elle renvoie les débuts, les fins et le chemin critique reconstruit depuis la tâche qui finit la dernière ; sur le pipeline, le rédacteur démarre à 10,3 et finit à 13,4, par le chemin `[0, 1, 3]`.

**`calendrier_par_vagues(vagues, durees)`** — Cette fonction met en scène le planificateur prudent tâche par tâche : elle reçoit la liste des vagues et les durées, part de l'instant 0, fait commencer toutes les tâches d'une vague au même instant t, puis avance t jusqu'à la fin de la plus lente d'entre elles avant de lancer la vague suivante. Elle renvoie deux dictionnaires, les débuts et les fins ; dans le contre-exemple, C ne démarre qu'à 10 au lieu de 1, parce qu'il attend B, qui n'est pourtant pas son prérequis, et le calendrier finit à 20 secondes au lieu de 11.

**`afficher(M)`** — Ce petit utilitaire est le greffier qui recopie une matrice au tableau, une ligne sous l'autre : il reçoit une matrice M et imprime chacune de ses lignes, précédée d'un retrait de quelques espaces, sans rien calculer ni rien renvoyer. `main` ne s'en sert qu'au bloc 1, pour montrer A², dont la première ligne se termine par le 2 qui compte les deux marches de longueur 2 du scraper vers le rédacteur ; tout le reste de l'affichage passe par des chaînes formatées.

**`main()`** — Le chef d'orchestre déroule les quatre tableaux du chapitre sur le pipeline de quatre agents : il calcule A², A³ et A⁴, les traces et les degrés entrants, puis montre sur le cycle à deux nœuds et sur le triangle que la trace compte des marches fermées et non des cycles, et que Kahn refuse le cycle. Il forme ensuite les vagues du pipeline et compare 19,2 secondes en séquentiel à 13,4 secondes par vagues et par chemin critique, soit un gain de 30,2 %, avant de rejouer le contre-exemple, 20 secondes contre 11, et de vérifier la borne sur trois graphes ; il ne renvoie rien et n'imprime le message final que si tout concorde.

```python
"""Étape 42 — matrice d'adjacence, marches fermées, nilpotence, vagues de Kahn et vrai chemin critique."""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def matmul(A: list[list[int]], B: list[list[int]]) -> list[list[int]]:
    """C_ij = Σ_l A_il B_lj. Pour des matrices d'adjacence, C_ij compte des marches."""
    n, m, p = len(A), len(B), len(B[0])
    C = [[0 for _ in range(p)] for _ in range(n)]
    for i in range(n):
        for j in range(p):
            for l in range(m):
                C[i][j] += A[i][l] * B[l][j]
    return C


def matpow(A: list[list[int]], k: int) -> list[list[int]]:
    """A^k pour k >= 1. (A^k)_ij = nombre de MARCHES de longueur k de i à j."""
    if k < 1:
        raise ValueError("k >= 1")
    resultat = A
    for _ in range(k - 1):
        resultat = matmul(resultat, A)
    return resultat


def trace(M: list[list[int]]) -> int:
    """Tr(M) = Σ_i M_ii. Sur A^k : nombre de marches FERMÉES de longueur k (pas de cycles)."""
    return sum(M[i][i] for i in range(len(M)))


def est_nulle(M: list[list[int]]) -> bool:
    return all(v == 0 for ligne in M for v in ligne)


def matrice(aretes: list[tuple[int, int]], n: int) -> list[list[int]]:
    A = [[0] * n for _ in range(n)]
    for i, j in aretes:
        A[i][j] = 1
    return A


def degres_entrants(A: list[list[int]]) -> list[int]:
    """d_in(j) = Σ_i A_ij : la somme de la colonne j."""
    return [sum(A[i][j] for i in range(len(A))) for j in range(len(A))]


def est_acyclique_par_trace(A: list[list[int]]) -> tuple[bool, int | None]:
    """DAG ⇔ Tr(A^k) = 0 pour k = 1..n. Renvoie (False, k) au premier k qui trouve une marche fermée."""
    for k in range(1, len(A) + 1):
        if trace(matpow(A, k)) > 0:
            return False, k
    return True, None


def tri_kahn(aretes: list[tuple[int, int]], n: int):
    """Degrés entrants, puis vagues de nœuds à 0. Renvoie (ordre, vagues), ou (None, None) s'il y a un cycle."""
    entrant = [0] * n
    suivants = [[] for _ in range(n)]
    for i, j in aretes:
        suivants[i].append(j)
        entrant[j] += 1
    restant = entrant[:]
    vague = [i for i in range(n) if restant[i] == 0]
    ordre, vagues = [], []
    while vague:
        vagues.append(vague[:])
        suivante = []
        for u in vague:
            ordre.append(u)
            for v in suivants[u]:
                restant[v] -= 1
                if restant[v] == 0:
                    suivante.append(v)
        vague = suivante
    if len(ordre) != n:
        return None, None
    return ordre, vagues


def duree_par_vagues(vagues: list[list[int]], durees: list[float]) -> float:
    """Calendrier SYNCHRONISÉ : une vague attend la fin de toute la précédente. Borne supérieure seulement."""
    return sum(max(durees[i] for i in vague) for vague in vagues)


def calendrier_au_plus_tot(aretes: list[tuple[int, int]], durees: list[float]):
    """Horloge simulée : chaque tâche démarre dès que TOUS ses prérequis sont finis (ouvriers illimités).
    fin(v) = durée(v) + max(fin(u) pour u → v). Renvoie (debut, fin, chemin critique)."""
    n = len(durees)
    ordre, _ = tri_kahn(aretes, n)
    if ordre is None:
        raise ValueError("cycle : pas de calendrier possible")
    preds = [[] for _ in range(n)]
    for i, j in aretes:
        preds[j].append(i)
    debut, fin, venu_de = [0.0] * n, [0.0] * n, [None] * n
    for v in ordre:                                       # ordre topologique : les prédécesseurs sont déjà calculés
        if preds[v]:
            u = max(preds[v], key=lambda p: (fin[p], -p))  # le prédécesseur qui finit le plus tard
            debut[v], venu_de[v] = fin[u], u
        fin[v] = debut[v] + durees[v]
    dernier = max(range(n), key=lambda v: (fin[v], -v))
    chemin = [dernier]
    while venu_de[chemin[-1]] is not None:
        chemin.append(venu_de[chemin[-1]])
    return debut, fin, chemin[::-1]


def calendrier_par_vagues(vagues: list[list[int]], durees: list[float]):
    """Toutes les tâches d'une vague démarrent quand la PLUS LENTE de la vague précédente a fini."""
    debut, fin, t = {}, {}, 0.0
    for vague in vagues:
        for v in vague:
            debut[v], fin[v] = t, t + durees[v]
        t = max(fin[v] for v in vague)
    return debut, fin


def afficher(M: list[list[int]]) -> None:
    for ligne in M:
        print("   ", ligne)


def main() -> None:
    noms = ["scraper", "sec_rag", "sentiment", "redacteur"]
    aretes = [(0, 1), (0, 2), (1, 3), (2, 3)]   # le scraper alimente les deux analystes, qui alimentent le rédacteur
    A = matrice(aretes, 4)
    durees = [4.2, 6.1, 5.8, 3.1]

    print("=== 1. A, A², A³ : compter les marches ===")
    A2, A3, A4 = matpow(A, 2), matpow(A, 3), matpow(A, 4)
    print("  A² =  (le 2 en haut à droite : deux marches scraper → redacteur de longueur 2)")
    afficher(A2)
    print(f"  A³ nulle : {est_nulle(A3)} ; A⁴ = Aⁿ nulle : {est_nulle(A4)}")
    print(f"  traces k = 1..4 : {[trace(matpow(A, k)) for k in range(1, 5)]}")
    print(f"  degrés entrants (sommes des colonnes) : {degres_entrants(A)}")
    assert A2[0][3] == 2 and est_nulle(A3) and est_nulle(A4)
    assert est_acyclique_par_trace(A) == (True, None)
    assert degres_entrants(A) == [0, 1, 1, 2]

    print("\n=== 2. La trace compte des marches fermées, pas des cycles ===")
    deux_cycle = matrice([(0, 1), (1, 0)], 2)
    traces = [trace(matpow(deux_cycle, k)) for k in range(1, 5)]
    print(f"  un seul cycle 0 → 1 → 0 : Tr(A^k), k = 1..4 = {traces}")
    print("  Tr(A⁴) = 2 alors qu'il n'existe aucun cycle de longueur 4 : 0→1→0→1→0 et 1→0→1→0→1")
    assert traces == [0, 2, 0, 2]
    triangle = matrice([(0, 1), (1, 2), (2, 0)], 3)
    print(f"  un seul triangle : Tr(A³) = {trace(matpow(triangle, 3))} (une marche fermée par point de départ)")
    assert trace(matpow(triangle, 3)) == 3
    assert est_acyclique_par_trace(deux_cycle) == (False, 2)
    assert not est_nulle(matpow(deux_cycle, 2)) and tri_kahn([(0, 1), (1, 0)], 2) == (None, None)
    print("  Kahn refuse le cycle : les deux degrés entrants valent 1 et ne tombent jamais à 0")

    print("\n=== 3. Kahn par vagues sur le pipeline, et vrai chemin critique ===")
    ordre, vagues = tri_kahn(aretes, 4)
    for numero, vague in enumerate(vagues):
        print(f"  vague {numero} : {[noms[i] for i in vague]}")
    t_seq = sum(durees)
    t_vagues = duree_par_vagues(vagues, durees)
    debut, fin, chemin = calendrier_au_plus_tot(aretes, durees)
    print(f"  séquentiel = {t_seq:.1f} s ; par vagues = {t_vagues:.1f} s ; chemin critique = {max(fin):.1f} s")
    print(f"  chemin critique : {' → '.join(noms[i] for i in chemin)} ; gain = {(t_seq - max(fin)) / t_seq * 100:.1f} %")
    assert abs(t_seq - 19.2) < 1e-9 and abs(t_vagues - 13.4) < 1e-9 and abs(max(fin) - 13.4) < 1e-9
    assert chemin == [0, 1, 3]

    print("\n=== 4. Contre-exemple : A(1) → C(10) et B(10) → D(1) ===")
    lettres = ["A", "B", "C", "D"]
    aretes2, durees2 = [(0, 2), (1, 3)], [1.0, 10.0, 10.0, 1.0]
    _, vagues2 = tri_kahn(aretes2, 4)
    deb_v, fin_v = calendrier_par_vagues(vagues2, durees2)
    deb_t, fin_t, chemin2 = calendrier_au_plus_tot(aretes2, durees2)
    for v in range(4):
        print(f"  {lettres[v]} : par vagues {deb_v[v]:4.1f} → {fin_v[v]:4.1f}   au plus tôt {deb_t[v]:4.1f} → {fin_t[v]:4.1f}")
    print(f"  par vagues = {duree_par_vagues(vagues2, durees2):.0f} ; vrai chemin critique = {max(fin_t):.0f}"
          f" ({' → '.join(lettres[i] for i in chemin2)})")
    assert duree_par_vagues(vagues2, durees2) == 20.0 and max(fin_t) == 11.0
    assert max(fin_v.values()) == duree_par_vagues(vagues2, durees2)

    # La somme des maxima des vagues majore toujours le chemin critique.
    essais = [(aretes, durees), (aretes2, durees2),
              ([(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 5)], [2.0, 9.0, 1.0, 1.0, 8.0, 3.0])]
    for ar, du in essais:
        _, vg = tri_kahn(ar, len(du))
        assert duree_par_vagues(vg, du) >= max(calendrier_au_plus_tot(ar, du)[1]) - 1e-12
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
=== 1. A, A², A³ : compter les marches ===
    [0, 0, 0, 2]
  A³ nulle : True ; A⁴ = Aⁿ nulle : True
  traces k = 1..4 : [0, 0, 0, 0]
  degrés entrants (sommes des colonnes) : [0, 1, 1, 2]
…
  un seul cycle 0 → 1 → 0 : Tr(A^k), k = 1..4 = [0, 2, 0, 2]
  un seul triangle : Tr(A³) = 3 (une marche fermée par point de départ)
…
  séquentiel = 19.2 s ; par vagues = 13.4 s ; chemin critique = 13.4 s
  chemin critique : scraper → sec_rag → redacteur ; gain = 30.2 %
…
  A : par vagues  0.0 →  1.0   au plus tôt  0.0 →  1.0
  B : par vagues  0.0 → 10.0   au plus tôt  0.0 → 10.0
  C : par vagues 10.0 → 20.0   au plus tôt  1.0 → 11.0
  D : par vagues 10.0 → 11.0   au plus tôt 10.0 → 11.0
  par vagues = 20 ; vrai chemin critique = 11 (A → C)
OK — toutes les vérifications sont passées.
```

La trace répond à « une marche peut-elle revenir à son départ ? ». Kahn répond à « dans quel ordre, et qui peut partir en même temps ? ». Le chemin critique répond à « combien de temps au minimum, et où optimiser ? ». Les trois tests passent avant qu'un workflow d'agents parte en production : le premier protège la facture, les deux autres protègent la latence.

## Squelette algorithmique

Le fichier contient trois algorithmes. Le **test d'acyclicité par les puissances** prend la matrice d'adjacence et renvoie « DAG » ou le premier k qui révèle une marche fermée ; l'idée est de calculer A, A², …, Aⁿ et de regarder leurs traces (point 3). Le **tri de Kahn par vagues** prend la liste des arcs et le nombre de nœuds, et renvoie un ordre topologique découpé en vagues, ou un échec s'il y a un cycle ; l'idée est de retirer à chaque tour toutes les tâches dont plus aucun prérequis n'est en attente. Le **chemin critique** prend les arcs et les durées, et renvoie l'instant de fin de chaque tâche et le chemin le plus long ; l'idée est de propager « fin = durée + plus tard des prérequis » dans l'ordre topologique (point 7).

```text
ALGORITHME AcycliqueParTraces
ENTRÉES : matrice d'adjacence A de taille n × n
SORTIE : (vrai, aucun) si le graphe est un DAG, sinon (faux, k)

P ← A
POUR k DE 1 À n FAIRE
    SI Σ sur i de P[i][i] > 0 ALORS
        RETOURNER (faux, k)                    (une marche fermée de longueur k existe)
    FIN SI
    P ← P × A
FIN POUR
RETOURNER (vrai, aucun)
```

```text
ALGORITHME KahnParVagues
ENTRÉES : arcs (i, j), nombre de nœuds n
SORTIE : ordre et vagues, ou échec si cycle

POUR chaque nœud v FAIRE entrant(v) ← 0 ; suivants(v) ← liste vide FIN POUR
POUR chaque arc (i, j) FAIRE
    ajouter j à suivants(i)
    entrant(j) ← entrant(j) + 1
FIN POUR
vague ← { v : entrant(v) = 0 }
ordre ← liste vide ; vagues ← liste vide
TANT QUE vague n'est pas vide FAIRE
    ajouter vague à vagues
    suivante ← liste vide
    POUR chaque u de vague FAIRE
        ajouter u à ordre
        POUR chaque v de suivants(u) FAIRE
            entrant(v) ← entrant(v) − 1
            SI entrant(v) = 0 ALORS ajouter v à suivante FIN SI
        FIN POUR
    FIN POUR
    vague ← suivante
FIN TANT QUE
SI longueur(ordre) < n ALORS RETOURNER échec (cycle) FIN SI
RETOURNER ordre, vagues
```

```text
ALGORITHME CheminCritique
ENTRÉES : arcs (i, j), durées d(v)
SORTIE : début(v), fin(v), chemin critique

ordre ← KahnParVagues(arcs, n).ordre        (échec si cycle)
POUR chaque v DANS ordre FAIRE
    SI v a des prérequis ALORS
        u ← le prérequis de plus grande fin(u)
        début(v) ← fin(u) ; venu_de(v) ← u
    SINON
        début(v) ← 0 ; venu_de(v) ← aucun
    FIN SI
    fin(v) ← début(v) + d(v)
FIN POUR
dernier ← le nœud de plus grande fin
chemin ← remonter venu_de depuis dernier, puis inverser
RETOURNER début, fin, chemin                (T_CP = fin(dernier))
```

**Complexité :** le test par les traces fait au plus n − 1 produits de matrices n × n, chacun en O(n³) avec trois boucles, plus n traces en O(n) : O(n⁴) en temps, et O(n²) en mémoire pour garder P et A. Kahn lit chaque arc deux fois (à la construction, puis à la décrémentation) et chaque nœud une fois : O(n + m) en temps pour n nœuds et m arcs, et O(n + m) en mémoire pour les listes de suivants et les compteurs. Le chemin critique ajoute un passage sur les prérequis de chaque nœud, soit encore O(n + m) arcs lus, et une remontée de longueur au plus n : O(n + m) en temps et en mémoire, Kahn compris. C'est la raison du dernier point des « Effets » : la matrice sert à démontrer, Kahn et la programmation dynamique servent en production.

**Du squelette au code :** `AcycliqueParTraces` est `est_acyclique_par_trace`, qui appelle `trace(matpow(A, k))` à chaque k : le code recalcule Aᵏ depuis A au lieu de multiplier P par A, ce qui est plus lisible mais plus lent (O(n⁵)) ; le pseudo-code donne la version économe. `KahnParVagues` est `tri_kahn` : la première boucle sur les arcs remplit `suivants` et `entrant`, la ligne « vague ← … » est la compréhension `[i for i in range(n) if restant[i] == 0]`, la décrémentation est `restant[v] -= 1`, et le test final est `if len(ordre) != n`. `CheminCritique` est `calendrier_au_plus_tot` : « u ← le prérequis de plus grande fin » s'écrit `max(preds[v], key=lambda p: (fin[p], -p))`, « remonter venu_de » est la boucle `while venu_de[chemin[-1]] is not None`, et `chemin[::-1]` inverse le chemin. La borne T_vagues se calcule à part avec `duree_par_vagues`, et `calendrier_par_vagues` sert seulement à montrer, tâche par tâche, ce que coûte la synchronisation.

## Cas d'usage réels aux Émirats

Les durées, latences et délais ci-dessous sont illustratifs : en production, on les mesure dans les journaux de chaque workflow.

### Banque — un dossier de crédit dont la vague attend pour rien

Une banque de détail de Dubaï orchestre ses dossiers de crédit par un graphe de tâches : le KYC (3 min), puis en parallèle le scoring (2 min) et l'évaluation du bien (15 min), puis le calcul du ratio d'endettement après le scoring (1 min), et enfin l'offre, qui attend le ratio et l'évaluation (2 min). Le séquentiel prend 23 min. Le calendrier par vagues en annonce 21, parce qu'il fait attendre au ratio la fin de l'évaluation, dont il n'a pas besoin : le ratio démarre à la 18e minute au lieu de la 5e. Le chemin critique, KYC puis évaluation puis offre, vaut 20 min : c'est la vraie latence minimale, et c'est l'évaluation qu'il faut accélérer, pas le scoring. Le ratio calculé applique la règle de la CBUAE (toutes les mensualités, y compris la nouvelle, sous 50 % du revenu) : c'est une tâche du graphe, et l'offre ne peut pas partir sans elle, ce que l'arc ratio → offre garantit. On suit la latence p95 du dossier complet et son écart au chemin critique prévu.

### BTP — 70 jours de retard fictif dans un planning de chantier

Un groupe de construction à Dubaï fait tenir le planning d'une tour par un agent, sur un graphe de lots : permis (10 jours), fondations (20) et commande des ascenseurs (90) après le permis, structure (60) après les fondations, façade (30) et réseaux techniques (45) après la structure, aménagements intérieurs (25) après les réseaux, réception (5) après la façade, les intérieurs et les ascenseurs. Le calendrier par vagues annonce 235 jours, parce qu'il fait attendre la structure jusqu'à la livraison des ascenseurs, dans la même vague que les fondations. Le chemin critique, permis, fondations, structure, réseaux, intérieurs et réception, vaut 165 jours : 70 jours d'écart, de quoi fausser un engagement contractuel et les pénalités de retard. La commande des ascenseurs a une marge de 165 − 105 = 60 jours, que l'agent signale au lieu de la traiter comme critique. Les situations de travaux et les factures (TVA à 5 %, retenues de garantie) suivent le même graphe. On suit l'écart entre l'avancement réel et le chemin critique, semaine par semaine.

### Immobilier — paralléliser les démarches d'un transfert

Une agence de Dubaï prépare le transfert d'un appartement : certificat de non-objection du promoteur (5 jours), mainlevée de l'hypothèque du vendeur (7 jours) et évaluation du bien (2 jours) n'ont pas de dépendance entre elles, puis vient le rendez-vous de transfert, où sont réglés les frais du DLD de 4 % de la valeur (1 jour), et enfin la remise des clés (1 jour). Faites l'une après l'autre, les démarches prennent 16 jours ; lancées dans la même vague, 9 jours, avec la mainlevée sur le chemin critique. Ici les vagues et le chemin critique coïncident, parce que la plus lente de chaque vague est sur un même chemin (point 6). L'agent ne relance donc en priorité que la banque du vendeur : relancer le promoteur ne ferait rien gagner. Les étapes et leur ordre dépendent du dossier et des règles du DLD en vigueur, que l'agent ne suppose pas. On suit le délai entre la signature du compromis et le transfert.

### RH — une règle mal écrite qui crée un cycle

Un cabinet RH présent dans plusieurs émirats décrit l'intégration d'un salarié comme un graphe : visite médicale, visa, Emirates ID, puis ouverture du compte de paie compatible WPS. Un nouveau paramétrage ajoute, par erreur, la règle « la demande d'Emirates ID exige un relevé de compte de paie », alors que l'ouverture du compte exige déjà l'Emirates ID : le graphe contient un cycle de longueur 2. Au chargement, Tr(A²) = 2 > 0, et Kahn s'arrête avec deux tâches jamais prêtes ; l'orchestrateur refuse de démarrer le workflow au lieu de laisser le dossier bloqué en silence pendant des semaines. L'étape 45 montre comment nommer les deux tâches prises dans le cycle pour le message d'erreur. Les démarches auprès du MOHRE et le paiement par le WPS ont des dépendances réelles strictes : c'est justement pour cela que chaque modification du graphe est testée avant mise en service. On suit le nombre de workflows refusés au chargement et le délai moyen d'intégration.

### Secteur public — une boucle de contrôle bornée, un graphe de dépendances sans cycle

Une entité de services publics en ligne, accessible par UAE Pass, répond en arabe et en anglais avec un agent dont le graphe de contrôle contient une boucle voulue : rédiger la réponse, la faire vérifier par un relecteur automatique, la corriger, puis la relire. Cette boucle est légitime dans un framework comme LangGraph, à condition d'être bornée : ici trois passages au plus, soit 6 000 tokens dans le pire cas pour des passages de 2 000 tokens, après quoi la demande part vers un agent humain. En revanche, le graphe de dépendances des documents à récupérer (identité, justificatif de domicile, attestation) doit être un DAG, vérifié au chargement. Confondre les deux graphes mène soit à interdire des boucles utiles, soit à accepter des dépendances circulaires. La PDPL impose de ne récupérer que les documents nécessaires : chaque nœud du graphe de dépendances correspond à une pièce exigée par la démarche. On suit le nombre moyen de passages dans la boucle de relecture et la part des demandes qui atteignent la borne.

### Crypto — optimiser le bon détecteur

Une plateforme d'actifs virtuels agréée par la VARA surveille ses transactions par un pipeline d'agents : ingestion (200 ms), puis trois détecteurs en parallèle (volume anormal 120 ms, prix anormal 80 ms, filtrage des adresses sous sanctions 350 ms), un agrégateur (50 ms) et l'envoi de l'alerte (30 ms). En séquentiel, il faudrait 830 ms ; avec le parallélisme, le chemin critique vaut 200 + 350 + 50 + 30 = 630 ms. Il passe par le filtrage des sanctions : accélérer le détecteur de prix ne ferait rien gagner, et c'est le filtrage qu'il faut optimiser, par exemple par un index plus rapide. Il n'est pas question de le sauter pour gagner du temps : le filtrage des adresses fait partie des obligations de lutte contre le blanchiment de la plateforme, et l'arc qui le relie à l'agrégateur ne se retire pas. On suit la latence p95 du pipeline et la part du temps passée sur le chemin critique.

## Pièges et limites

- **Prendre la somme des maxima des vagues pour le chemin critique.** C'est une borne supérieure : 20 s au lieu de 11 dans le contre-exemple, 235 jours au lieu de 165 sur le chantier.
- **Lire la trace comme un nombre de cycles.** Tr(Aᵏ) compte des marches fermées : un seul 2-cycle donne Tr(A²) = Tr(A⁴) = 2.
- **Interdire toute boucle.** Le graphe de dépendances doit être un DAG ; le graphe de contrôle d'un agent peut boucler, à condition d'être borné et d'avoir une sortie.
- **Tester l'acyclicité par les puissances de matrice en production.** O(n⁴) contre O(n + m) pour Kahn : sur 1 000 tâches, l'écart est énorme.
- **Mesurer le parallélisme avec de vraies attentes dans un test.** Des minuteries réelles rendent les tests lents et non reproductibles ; une horloge simulée donne les mêmes calendriers, exactement.

### Exercice feuille blanche

1. Sans regarder le code, écrire `matmul`, `trace` et `est_acyclique_par_trace`, puis vérifier que le cycle à deux nœuds donne les traces 0, 2, 0, 2.
2. Prédire, puis vérifier : dans le pipeline, l'analyste de sentiment passe à 7 s. Que valent la durée par vagues et le chemin critique ? (Réponse : 4,2 + 7 + 3,1 = 14,3 s dans les deux cas, et le chemin critique passe désormais par le sentiment.)
3. Trouver le bug : une variante de `calendrier_au_plus_tot` parcourt les tâches dans l'ordre des indices 0, 1, 2, … au lieu de l'ordre de Kahn. Sur quel graphe se trompe-t-elle ? (Réponse : dès qu'un arc va d'un indice plus grand vers un plus petit, par exemple 1 → 0 : la tâche 0 est calculée avant son prérequis, avec fin(1) encore à 0.)

## Pour aller plus loin

- **Marges et méthode du chemin critique (CPM).** En propageant aussi, à rebours depuis la fin, l'instant de démarrage au plus tard de chaque tâche, on obtient sa marge : c'est la méthode utilisée en gestion de projet.
- **Ouvriers en nombre limité.** Avec k ouvriers seulement, trouver le calendrier le plus court est un problème difficile en général ; les ordonnanceurs utilisent des règles de liste, par exemple la priorité de l'étape 41 appliquée aux tâches prêtes.
- **Fermeture transitive.** I + A + A² + … + Aⁿ⁻¹ indique quelles tâches dépendent, même indirectement, de quelles autres : utile pour savoir ce qu'il faut relancer quand une tâche échoue.

> Suite : [Fondements : DAG, nilpotence et tri topologique](<43-Fondements-Orchestration-et-DAG.md>) — étape 43.
