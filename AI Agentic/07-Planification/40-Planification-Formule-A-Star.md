# Étape 40 — Planification — Coût dans A* (heuristique)

> Étape 40 du parcours · Prérequis : [Bellman et contraction, seconde moitié des fondements](<../02-LLM-Softmax-et-Prompts/03-Fondements-Softmax-et-LLM.md>) · Suite : [Orchestration : définitions fondamentales](<../08-Orchestration/40b-Orchestration-Definitions-Fondamentaux.md>)

**Dossier :** 07-Planification  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, Product Engineers  
**Nom du fichier :** 40-Planification-Formule-A-Star.md

## Définition

A\* (prononcé « A étoile ») cherche le chemin le moins cher entre un nœud de départ et un nœud but, dans un graphe dont les arcs ont des coûts strictement positifs. Pour chaque nœud n atteint, il connaît g(n), le coût réel du meilleur chemin trouvé jusqu'à n, et il estime h(n), le coût qui reste pour aller de n au but ; il développe toujours en premier le nœud de plus petite somme f(n) = g(n) + h(n). La fonction h s'appelle l'**heuristique**. Elle est **admissible** si elle ne surestime jamais le coût restant, et **consistante** si elle ne baisse jamais, le long d'un arc, de plus que le coût de cet arc. L'optimalité du chemin renvoyé dépend de ces propriétés et de la façon dont l'algorithme traite les nœuds déjà développés : « h admissible, donc A\* est optimal » n'est vrai que sous conditions, démontrées plus bas. Avec h = 0, A\* est l'algorithme de Dijkstra.

## Rôle dans un agent

A\* sert au moment de **décider**, dans le planificateur, quand le problème se pose comme un graphe connu : des états du plan (ce qui est déjà fait), des actions (des appels d'outils) et un coût par action (une latence en secondes, des frais en AED, des minutes de trajet). Comme le dit l'étape 37 bis, le modèle de langage ne lance pas lui-même A\* : le plan appelle un outil déterministe qui le fait et renvoie la suite d'actions la moins chère. Là où Bellman (étape 38) traite des conséquences incertaines, A\* traite des transitions sûres, et il le fait vite parce que l'heuristique lui évite d'explorer les branches qui ne peuvent pas battre la meilleure. Quand un outil tombe en panne, on retire son arc et l'on relance la recherche : c'est une replanification au sens de l'étape 37 bis.

## Équation complète

Coût estimé d'un chemin qui passe par n :

$$
f(n) = g(n) + h(n)
$$

Mise à jour quand on développe n et qu'on atteint un voisin n′ par un arc de coût c(n, n′) :

$$
g(n') \leftarrow \min\big( g(n'),\; g(n) + c(n, n') \big)
$$

Heuristique admissible :

$$
0 \le h(n) \le h^{*}(n) \quad \text{pour tout nœud } n
$$

Heuristique consistante (on dit aussi monotone) :

$$
h(n) \le c(n, n') + h(n') \quad \text{pour tout arc } (n, n') , \qquad h(\text{but}) = 0
$$

Cas particulier, Dijkstra :

$$
h \equiv 0 \;\Longrightarrow\; f(n) = g(n)
$$

## Décryptage des symboles

$$
n,\; n'
$$

**Sens :** un nœud du graphe et l'un de ses voisins ; ici un état du plan, c'est-à-dire l'ensemble des contrôles déjà faits (« ∅ », « I », « I+E »…) · **Type / plage :** élément d'un ensemble fini · **Variable Python :** `n`, `voisin` (chaînes)

$$
c(n, n')
$$

**Sens :** coût de l'arc de n vers n′, ici la latence de l'outil appelé · **Type / plage :** réel strictement positif · **Variable Python :** `cout`

$$
g(n)
$$

**Sens :** coût réel du meilleur chemin trouvé jusqu'ici du départ à n ; il ne peut que baisser au fil de la recherche · **Type / plage :** réel ≥ 0 · **Variable Python :** `g[n]`

$$
g^{*}(n)
$$

**Sens :** coût du meilleur chemin possible du départ à n ; à tout instant g(n) ≥ g\*(n) · **Type / plage :** réel ≥ 0 · **Variable Python :** non calculé (sert à la preuve)

$$
h(n)
$$

**Sens :** estimation du coût restant de n jusqu'au but · **Type / plage :** réel ≥ 0 · **Variable Python :** `h(n)`, l'une des fonctions `h_nulle`, `h_par_controle`, `h_somme_minima`

$$
h^{*}(n)
$$

**Sens :** vrai coût restant : le coût du meilleur chemin de n au but · **Type / plage :** réel ≥ 0 · **Variable Python :** `min(tous_les_couts(G, n, but))`

$$
f(n)
$$

**Sens :** estimation du coût total d'un chemin qui passe par n ; c'est la priorité de n dans la liste ouverte · **Type / plage :** réel ≥ 0 · **Variable Python :** premier élément du tuple `(f, h, n)` rangé dans le tas `ouverts`

$$
C^{*}
$$

**Sens :** coût du chemin optimal du départ au but, égal à h\*(départ) · **Type / plage :** réel ≥ 0 · **Variable Python :** `c_etoile`

Deux structures portent l'algorithme. La **liste ouverte** contient les nœuds atteints mais pas encore développés, rangés par f croissant dans un tas (`heapq`). L'**ensemble fermé** contient les nœuds déjà développés (`fermes`).

## Démonstration

On suppose un graphe fini, des coûts c(n, n′) > 0 et h ≥ 0. Le but est testé quand il **sort** de la liste ouverte, pas quand il y entre.

### 1. Lemme : un nœud du chemin optimal attend toujours dans la liste ouverte

Soit P\* = (n₀ = départ, n₁, …, nₖ = but) un chemin optimal. Tant que le but n'est pas sorti, et à condition qu'un nœud dont g baisse retourne dans la liste ouverte (recherche arborescente, ou recherche avec réouverture), la liste ouverte contient un nœud nⱼ de P\* tel que g(nⱼ) = g\*(nⱼ).

Preuve : on prend le premier nœud nⱼ de P\* qui n'a pas encore été développé avec son coût optimal. Si j = 0, c'est le départ, qui est dans la liste ouverte avec g = 0 = g\*(départ). Si j > 0, le nœud précédent nⱼ₋₁ a été développé avec g = g\*(nⱼ₋₁) ; à ce moment-là, nⱼ a reçu g(nⱼ) ≤ g\*(nⱼ₋₁) + c(nⱼ₋₁, nⱼ) = g\*(nⱼ), parce que P\* est optimal et que tout sous-chemin d'un chemin optimal est optimal. Comme g(nⱼ) ne peut pas descendre sous g\*(nⱼ), on a égalité. Et comme nⱼ n'a pas été développé avec ce coût, il est encore dans la liste ouverte avec ce coût.

### 2. Admissible ⇒ optimal, en recherche arborescente ou avec réouverture

Supposons que A\* sorte le but avec un coût g(but) > C\*. Le nœud nⱼ du lemme vérifie, parce que h est admissible :

$$
f(n_j) = g^{*}(n_j) + h(n_j) \le g^{*}(n_j) + h^{*}(n_j) = C^{*} < g(\text{but}) = f(\text{but})
$$

La dernière égalité vient de h(but) = 0, conséquence de 0 ≤ h(but) ≤ h\*(but) = 0. Le nœud nⱼ a donc une priorité strictement meilleure que le but : il serait sorti avant lui. C'est une contradiction, donc le coût renvoyé vaut C\*. La recherche se termine parce que le graphe est fini et que les coûts sont strictement positifs : un nœud ne peut voir son g baisser qu'un nombre fini de fois.

### 3. Pourquoi l'ensemble fermé sans réouverture casse cette preuve

Dans la version la plus courante d'A\*, un nœud développé entre dans l'ensemble fermé et n'en sort plus. Le lemme peut alors tomber : un nœud nⱼ du chemin optimal a pu être développé plus tôt **avec un mauvais g**, par un autre chemin, puis ignoré quand le bon chemin l'atteint. Contre-exemple chiffré, avec des latences en secondes : S est la demande, A un appel d'API rapide, B une lecture OCR, C le revenu vérifié et G l'offre émise. Les arcs sont S→A (1), S→B (1), A→C (1), B→C (3) et C→G (3). Le meilleur chemin est S→A→C→G, de coût 5. L'heuristique vaut h(A) = 4 et 0 ailleurs.

- Elle est **admissible** : h\*(S) = 5, h\*(A) = 4, h\*(B) = 6, h\*(C) = 3, h\*(G) = 0, et chaque h(n) est inférieur ou égal.
- Elle n'est **pas consistante** : h(A) = 4 > c(A, C) + h(C) = 1 + 0.

Déroulé avec ensemble fermé, sans réouverture :

1. On développe S (f = 0). La liste ouverte reçoit B (g = 1, f = 1) et A (g = 1, f = 1 + 4 = 5).
2. On développe B (f = 1). C entre avec g = 1 + 3 = 4, f = 4.
3. On développe C (f = 4), qui passe dans l'ensemble fermé avec un g faux, 4 au lieu de 2. G entre avec g = 7.
4. On développe A (f = 5). Le chemin S→A→C donne g(C) = 2 < 4, mais C est fermé : l'arc est ignoré.
5. G sort avec f = 7. A\* renvoie S→B→C→G, de coût 7 au lieu de 5.

Avec réouverture, l'étape 4 remet C dans la liste ouverte avec g = 2 ; C est redéveloppé, G reçoit g = 5 et sort avec le coût optimal 5. Le programme rejoue les trois versions.

### 4. Consistante ⇒ admissible

Soit n un nœud et (n = m₀, m₁, …, mₚ = but) un chemin optimal de n au but. On applique la consistance arc par arc, puis on utilise h(but) = 0 :

$$
h(n) \le c(m_0, m_1) + h(m_1) \le c(m_0, m_1) + c(m_1, m_2) + h(m_2) \le \dots \le \sum_{i=0}^{p-1} c(m_i, m_{i+1}) + h(\text{but}) = h^{*}(n)
$$

La consistance est donc plus forte que l'admissibilité. L'inverse est faux, comme le montre le contre-exemple du point 3.

### 5. Consistante ⇒ f ne décroît jamais le long d'un chemin

Si n′ est atteint depuis n, alors g(n′) = g(n) + c(n, n′), et la consistance donne :

$$
f(n') = g(n) + c(n, n') + h(n') \ge g(n) + h(n) = f(n)
$$

Les valeurs de f des nœuds développés forment donc une suite croissante au fil de la recherche, et le but sort avec f = C\*.

### 6. Consistante ⇒ un nœud sort avec son coût optimal, donc l'ensemble fermé est sûr

On raisonne par récurrence sur l'ordre des développements : on suppose que tous les nœuds développés avant n l'ont été avec leur coût optimal, et l'on suppose par l'absurde que n sort avec g(n) > g\*(n). Sur un chemin optimal du départ à n, le raisonnement du lemme (valable grâce à l'hypothèse de récurrence) fournit un nœud m dans la liste ouverte avec g(m) = g\*(m). En appliquant la consistance le long de ce chemin de m à n, comme au point 4, on obtient h(m) ≤ coût(m → n) + h(n), d'où :

$$
f(m) = g^{*}(m) + h(m) \le g^{*}(m) + \text{coût}(m \to n) + h(n) = g^{*}(n) + h(n) < g(n) + h(n) = f(n)
$$

Le nœud m serait donc sorti avant n : contradiction. Chaque nœud sort une seule fois, avec son coût optimal ; ne jamais le rouvrir ne perd rien, et chaque nœud est développé au plus une fois. Avec un tas, la complexité est O((V + E) log V) pour V nœuds et E arcs.

### 7. Pourquoi les coûts doivent être strictement positifs

Avec un coût négatif, un chemin peut redevenir moins cher après qu'un nœud a été fermé, et toutes les preuves ci-dessus tombent : le point 6 utilise que g(n′) ≥ g(n) le long d'un arc. Avec des coûts nuls, l'algorithme reste correct sur un graphe fini, mais un plan peut s'allonger d'actions gratuites et inutiles. Le code refuse donc tout coût inférieur ou égal à 0 par une `ValueError`.

### 8. Une heuristique dominante développe moins de nœuds

On dit que h₂ **domine** h₁ si h₂(n) ≥ h₁(n) pour tout n. Ce n'est pas qu'elle est « plus précise » au sens vague : deux heuristiques admissibles sont toutes deux sous h\*, et la dominante est simplement plus proche de h\* par en dessous, donc mieux informée. Avec une heuristique consistante, A\* développe tous les nœuds tels que g\*(n) + h(n) < C\* (leur f est sous celui du but, qui sort en dernier puisque f croît, point 5) et aucun nœud tel que g\*(n) + h(n) > C\*. Si h₂ domine h₁, l'ensemble des nœuds vérifiant g\*(n) + h₂(n) < C\* est inclus dans celui des nœuds vérifiant g\*(n) + h₁(n) < C\*. La recherche guidée par h₂ ne développe donc pas plus de nœuds, aux égalités f = C\* près, qui dépendent du départage.

### 9. Les trois heuristiques du plan KYC sont consistantes

Le graphe du code représente l'ouverture d'un dossier de crédit qui exige trois contrôles : identité (I), revenus (R) et évaluation du bien (E). Un état est l'ensemble des contrôles faits ; le départ est ∅, le but I+R+E. Les outils sont `uae_pass_identite` (couvre I, 2 s), `kyc_complet` (couvre I et R, 7 s), `ocr_bulletins` (R, 6 s), `api_salaire_wps` (R, 3 s, exige I), `evaluation_auto` (E, 4 s) et `expertise_sur_site` (E, 9 s).

- **h₀ = 0** est consistante de façon évidente : 0 ≤ c + 0.
- **h₁ = 2 s par contrôle manquant.** Le long d'un arc, h₁ baisse de 2 fois le nombre de contrôles nouvellement couverts. Chaque outil coûte au moins 2 s par contrôle qu'il couvre (2/1, 7/2 = 3,5, 6, 3, 4, 9), donc la baisse ne dépasse jamais le coût de l'arc.
- **h₂ = somme, sur les contrôles manquants, du moins cher des outils qui le couvrent** : 2 pour I, 3 pour R, 4 pour E, donc h₂(∅) = 9. Le long d'un arc, h₂ baisse de la somme des minima des contrôles nouvellement couverts. Un outil qui couvre un seul contrôle coûte au moins ce minimum, par définition. Le seul outil qui en couvre deux, `kyc_complet`, coûte 7 ≥ 2 + 3. La consistance tient donc, mais **seulement parce que l'outil groupé n'est pas moins cher que la somme des minima** ; l'exercice 2 casse cette condition.

Comme 2 ≤ 2, 2 ≤ 3 et 2 ≤ 4, on a h₀ ≤ h₁ ≤ h₂ ≤ h\* : h₂ domine h₁, qui domine h₀.

### 10. Exemple fait à la main (le code reprend ces nombres)

A\* avec h₂ et un ensemble fermé, égalités départagées par le plus petit h puis par le nom.

1. On développe ∅ (g = 0, h = 9, f = 9). Entrent : I (g = 2, h = 7, f = 9), E (g = 4, h = 5, f = 9), I+R par `kyc_complet` (g = 7, h = 4, f = 11), R par `ocr_bulletins` (g = 6, h = 6, f = 12). L'expertise donne E avec g = 9, moins bien que 4 : elle est ignorée.
2. I et E sont à égalité, f = 9 ; E a le plus petit h, il sort. Entrent : I+E (g = 4 + 2 = 6, h = 3, f = 9), I+R+E par `kyc_complet` (g = 11, f = 11), R+E (g = 10, h = 2, f = 12).
3. I et I+E sont à égalité, f = 9 ; I+E sort (h = 3 < 7). L'appel `api_salaire_wps`, permis puisque I est fait, donne au but g = 6 + 3 = 9 < 11 : le but est mis à jour, f = 9.
4. I et le but sont à égalité, f = 9 ; le but sort (h = 0). Le plan est `evaluation_auto` → `uae_pass_identite` → `api_salaire_wps`, coût 4 + 2 + 3 = 9 s, avec 3 nœuds développés.

La force brute sur tous les plans complets confirme C\* = 9. Dijkstra (h₀) trouve le même coût en développant 6 nœuds, h₁ en développe 5 et h₂ seulement 3 : tous des nœuds du chemin optimal.

## Effets et comportement

- **h = 0 : A\* devient Dijkstra.** Il explore par cercles de coût croissant, dans toutes les directions, et reste optimal.
- **Une h dominante, toujours admissible, réduit le nombre de nœuds développés** : 6, 5 puis 3 dans l'exemple. Le chemin renvoyé garde le même coût.
- **h = h\* exactement : A\* ne développe que des nœuds d'un chemin optimal** (aux égalités près). C'est presque le cas de h₂ ici.
- **Une h qui surestime perd la garantie d'optimalité**, même si elle accélère la recherche ; une h admissible mais inconsistante la perd aussi quand on ne rouvre pas les nœuds fermés.
- **Le coût de l'arc est l'unité de tout** : si g additionne des secondes et h des AED, f ne veut rien dire.

## Du symbole au code Python

| Symbole | Variable ou fonction Python |
|---|---|
| graphe, arcs (n, n′) et c(n, n′) | `graphe_kyc()`, dictionnaire `état -> [(voisin, cout, outil)]` |
| g(n) | `g[n]` |
| h(n) | `h_nulle`, `h_par_controle`, `h_somme_minima` |
| f(n) = g(n) + h(n) | `g_nouveau + h(voisin)`, priorité dans le tas `ouverts` |
| liste ouverte, ensemble fermé | `ouverts` (tas `heapq`), `fermes` (ensemble) |
| h\*(n), C\* | `min(tous_les_couts(G, n, but))`, `c_etoile` |
| test de consistance | `consistante(graphe, h, but)` |

Copiez le bloc dans `a_etoile_kyc.py` et lancez `python a_etoile_kyc.py`.

### Déroulé, ligne par ligne

**`graphe_kyc()`** construit les 8 états, tous les sous-ensembles de {I, R, E}. Pour chaque état et chaque outil, la condition `prerequis <= faits and not couvre <= faits` crée un arc si les prérequis sont faits et si l'outil apporte au moins un contrôle nouveau. Depuis ∅, `api_salaire_wps` ne crée pas d'arc, parce qu'il exige I.

**`h_nulle`, `h_par_controle`, `h_somme_minima`** sont les trois heuristiques du point 9. `MIN_PAR_CONTROLE` vaut `{"I": 2, "R": 3, "E": 4}`, calculé en prenant pour chaque contrôle le moins cher des outils qui le couvrent. `h_somme_minima("∅")` vaut 9, `h_somme_minima("E")` vaut 5.

**`a_etoile(graphe, depart, but, h, rouvrir, trace)`**, la fonction centrale.

- `ouverts = [(h(depart), h(depart), depart)]` : chaque entrée du tas est un triplet `(f, h, nœud)`. `heapq` sort le plus petit triplet : le plus petit f, puis le plus petit h, puis le nom. Le départage est ainsi déterministe.
- `f, _, n = heapq.heappop(ouverts)` sort la meilleure entrée. Le test `n in fermes or f != g[n] + h(n)` saute les entrées périmées : un nœud peut être poussé plusieurs fois, et seule l'entrée qui correspond à son meilleur g compte.
- `if n == but` : le but est testé **à la sortie**. C'est ce qui rend le coût optimal (point 2). Au tour 2 de l'exemple, le but entre dans la liste avec g = 11 : un test à l'entrée l'aurait renvoyé.
- `fermes.add(n)` puis `developpes += 1` : on compte les nœuds développés, but exclu.
- Pour chaque arc, `if cout <= 0: raise ValueError(...)` applique le point 7. Puis `if voisin in fermes and not rouvrir: continue` : sans réouverture, un nœud fermé est ignoré, même si l'on trouve mieux (point 3).
- `if g_nouveau < g.get(voisin, math.inf)` : on ne garde que les améliorations. `fermes.discard(voisin)` rouvre le voisin s'il était fermé, ce qui n'arrive qu'avec `rouvrir=True`. Puis `heapq.heappush` le remet dans le tas avec sa nouvelle priorité.
- `trace` reçoit, après chaque développement, le nœud développé, son f et la liste ouverte encore valide, triée.

**`tous_les_couts(graphe, depart, but)`** énumère tous les chemins complets ; c'est possible parce que chaque arc ajoute un contrôle, donc le graphe n'a pas de cycle. Le minimum donne C\* = 9.

**`consistante(graphe, h, but)`** vérifie h(but) = 0 et h(n) ≤ c + h(n′) sur tous les arcs.

**`main()`**, bloc par bloc.

1. C\* = 9 par force brute.
2. A\* avec h₂ et un ensemble fermé : la trace reproduit l'exemple fait à la main, et deux `assert` vérifient le chemin et les trois nœuds développés ∅, E, I+E.
3. Les trois heuristiques : chacune est consistante, chacune trouve 9, et les nombres de nœuds développés décroissent (6, 5, 3). Deux `assert` vérifient que h₂ domine h₁ et que h₂ est admissible sur tous les états.
4. Le contre-exemple du point 3 : l'heuristique est admissible mais inconsistante ; sans réouverture, A\* renvoie 7, avec réouverture 5, et Dijkstra 5.
5. Un arc de coût 0 provoque une `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`nom_etat(faits)`** — Cette petite fonction est le préposé aux étiquettes qui donne à chaque dossier un nom lisible et toujours écrit de la même façon : elle reçoit l'ensemble figé des contrôles déjà faits, garde dans l'ordre fixe I, R, E ceux qui y figurent et les joint par des signes plus, ou renvoie le symbole ∅ si l'ensemble est vide. Elle renvoie ainsi des chaînes comme `I+E` ou `I+R+E`, qui servent de clés au graphe ; parce que l'ordre ne dépend pas de la façon dont l'ensemble a été construit, deux chemins qui aboutissent aux mêmes contrôles tombent bien sur le même état.

**`h_nulle(etat)`** — Voici l'éclaireur le plus modeste possible, qui refuse de deviner quoi que ce soit sur la route restante : la fonction reçoit un état et renvoie toujours 0, quel qu'il soit. Avec cette heuristique, f = g et A\* devient exactement l'algorithme de Dijkstra, qui explore par coût accumulé croissant ; `main` s'en sert comme point de comparaison, avec 6 nœuds développés pour trouver le coût optimal de 9 secondes, et comme référence dans le contre-exemple, où elle retrouve le coût 5.

**`h_par_controle(etat)`** — Cet éclaireur-là compte les étapes qu'il reste à franchir et les facture au tarif le plus bas imaginable : la fonction reçoit le nom d'un état, compte parmi I, R et E les contrôles qui n'y figurent pas, et renvoie 2 secondes par contrôle manquant, 2 étant le plus petit coût par contrôle couvert, tous outils confondus. Elle donne 6 au départ et 0 au but ; consistante, elle trouve elle aussi le coût 9, avec 5 nœuds développés au lieu de 6, et `main` vérifie qu'elle ne dépasse jamais h₂ dans aucun état.

**`h_somme_minima(etat)`** — C'est l'éclaireur le mieux renseigné, qui connaît le prix du moins cher des outils pour chaque contrôle : la fonction reçoit le nom d'un état et additionne, pour chaque contrôle manquant, la valeur lue dans `MIN_PAR_CONTROLE`, soit 2 pour I, 3 pour R et 4 pour E. Elle renvoie 9 au départ, 5 depuis l'état E et 0 au but ; comme elle ne surestime jamais le coût restant et domine h₁, A\* ne développe avec elle que 3 nœuds, ∅, E puis I+E, tous sur le chemin optimal.

**`a_etoile(graphe, depart, but, h, rouvrir, trace)`** — C'est le navigateur qui sort toujours de sa pile la piste la plus prometteuse : la fonction reçoit le graphe, le départ, le but, une heuristique h, un drapeau `rouvrir`, vrai par défaut, et une liste `trace` facultative, puis gère un tas d'entrées (f, h, nœud), ignore les entrées périmées, teste le but au moment où il sort du tas et non quand il y entre, ferme chaque nœud développé et pousse chaque voisin dont le coût g s'améliore. Elle lève une `ValueError` sur un arc de coût nul ou négatif, et renvoie le chemin d'outils, son coût et le nombre de nœuds développés, ou `None` et l'infini si le but est inaccessible ; dans le contre-exemple, sans réouverture, elle se trompe et rend 7 au lieu de 5.

**`tous_les_couts(graphe, depart, but)`** — Cette fonction est l'inspecteur obstiné qui parcourt toutes les routes possibles, sans exception, pour en noter le prix : elle reçoit le graphe, un état de départ et le but, renvoie la liste `[0]` si l'on est déjà arrivé, et sinon, pour chaque arc sortant, ajoute son coût à chacun des coûts complets obtenus récursivement depuis le voisin. Elle renvoie la liste des coûts de tous les chemins complets, ce qui n'est possible que parce que chaque arc ajoute un contrôle et que le graphe n'a pas de cycle ; son minimum donne C\* = 9, et `main` s'en sert aussi pour calculer h\* et vérifier l'admissibilité des heuristiques.

**`consistante(graphe, h, but)`** — On peut la voir comme un contrôleur qui vérifie qu'un guide ne promet jamais plus de raccourci qu'un seul pas n'en permet : la fonction reçoit le graphe, une heuristique h et le but, et renvoie vrai seulement si h vaut 0 au but et si, pour chaque arc de n vers n′ de coût c, h(n) ne dépasse pas c + h(n′). `main` exige que les trois heuristiques du KYC passent ce test, et montre que l'heuristique du contre-exemple, avec h(A) = 4 alors que l'arc vers C coûte 1 et que h(C) vaut 0, est admissible mais échoue ici, ce qui piège A\* sans réouverture.

**`main()`** — Le chef d'orchestre déroule les cinq tableaux du chapitre : il construit le graphe KYC à 8 états et trouve par force brute C\* = 9, fait tourner A\* avec h₂ en imprimant la liste ouverte à chaque itération, puis compare les trois heuristiques, toutes consistantes et toutes optimales, qui développent 6, 5 et 3 nœuds. Il rejoue ensuite le petit graphe du contre-exemple, où A\* sans réouverture rend 7 alors qu'avec réouverture et avec Dijkstra on obtient 5, et vérifie qu'un arc de coût nul lève une `ValueError` ; il ne renvoie rien et n'imprime le message final que si tous les `assert` passent.

```python
"""Étape 40 — A* sur un plan d'outils (KYC bancaire), contre Dijkstra, et le piège de l'heuristique inconsistante."""
import heapq
import itertools
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ------------------------------------------------------------------ le plan d'outils
# Un état = l'ensemble des contrôles déjà faits : I (identité), R (revenus), E (évaluation du bien).
# Un outil couvre des contrôles, peut exiger des contrôles préalables, et coûte une latence en secondes.
CONTROLES = ("I", "R", "E")
OUTILS = [
    # (nom, contrôles couverts, prérequis, coût en secondes)
    ("uae_pass_identite", {"I"}, set(), 2),
    ("kyc_complet", {"I", "R"}, set(), 7),
    ("ocr_bulletins", {"R"}, set(), 6),
    ("api_salaire_wps", {"R"}, {"I"}, 3),
    ("evaluation_auto", {"E"}, set(), 4),
    ("expertise_sur_site", {"E"}, set(), 9),
]


def nom_etat(faits: frozenset) -> str:
    return "+".join(c for c in CONTROLES if c in faits) or "∅"


def graphe_kyc() -> dict[str, list[tuple[str, int, str]]]:
    """Liste d'adjacence : état -> [(état suivant, coût, outil)]. Les outils inutiles ne créent pas d'arc."""
    graphe = {}
    for k in range(len(CONTROLES) + 1):
        for faits in itertools.combinations(CONTROLES, k):
            faits = frozenset(faits)
            arcs = []
            for nom, couvre, prerequis, cout in OUTILS:
                if prerequis <= faits and not couvre <= faits:
                    arcs.append((nom_etat(faits | couvre), cout, nom))
            graphe[nom_etat(faits)] = arcs
    return graphe


def h_nulle(etat: str) -> int:
    return 0                                               # A* avec h = 0 : c'est Dijkstra


def h_par_controle(etat: str) -> int:
    """h1 : 2 s par contrôle manquant (2 s = plus petit coût par contrôle couvert, tous outils confondus)."""
    return 2 * sum(1 for c in CONTROLES if c not in etat)


MIN_PAR_CONTROLE = {c: min(cout for _, couvre, _, cout in OUTILS if c in couvre) for c in CONTROLES}


def h_somme_minima(etat: str) -> int:
    """h2 : somme, sur les contrôles manquants, du moins cher des outils qui le couvrent (2 + 3 + 4 au départ)."""
    return sum(MIN_PAR_CONTROLE[c] for c in CONTROLES if c not in etat)


# ------------------------------------------------------------------ A*
def a_etoile(graphe, depart, but, h, rouvrir=True, trace=None):
    """f(n) = g(n) + h(n). Renvoie (chemin d'outils, coût, nombre de nœuds développés).

    - le but est testé quand il SORT de la liste ouverte, pas quand il y entre ;
    - rouvrir=False : un nœud fermé n'est plus jamais rouvert (sûr seulement si h est consistante) ;
    - égalités départagées par (f, h, nom) : déterministe.
    """
    g = {depart: 0}
    parent = {depart: None}
    ouverts = [(h(depart), h(depart), depart)]
    fermes = set()
    developpes = 0
    while ouverts:
        f, _, n = heapq.heappop(ouverts)
        if n in fermes or f != g[n] + h(n):
            continue                                       # entrée périmée : n a déjà mieux
        if n == but:
            chemin = []
            while parent[n] is not None:
                n, outil = parent[n]
                chemin.append(outil)
            return chemin[::-1], g[but], developpes
        fermes.add(n)
        developpes += 1
        for voisin, cout, outil in graphe[n]:
            if cout <= 0:
                raise ValueError("A* suppose des coûts strictement positifs")
            if voisin in fermes and not rouvrir:
                continue
            g_nouveau = g[n] + cout
            if g_nouveau < g.get(voisin, math.inf):
                g[voisin] = g_nouveau
                parent[voisin] = (n, outil)
                fermes.discard(voisin)                     # réouverture (n'arrive que si rouvrir=True)
                heapq.heappush(ouverts, (g_nouveau + h(voisin), h(voisin), voisin))
        if trace is not None:
            vivants = sorted((ff, v) for ff, _, v in ouverts if v not in fermes and ff == g[v] + h(v))
            trace.append((n, f, vivants))
    return None, math.inf, developpes


def tous_les_couts(graphe, depart, but):
    """Force brute : coût de chaque chemin complet (le graphe est sans cycle : chaque arc ajoute un contrôle)."""
    if depart == but:
        return [0]
    return [c + reste for v, c, _ in graphe[depart] for reste in tous_les_couts(graphe, v, but)]


def consistante(graphe, h, but) -> bool:
    return h(but) == 0 and all(h(n) <= c + h(v) for n, arcs in graphe.items() for v, c, _ in arcs)


def main() -> None:
    G = graphe_kyc()
    depart, but = "∅", "I+R+E"
    c_etoile = min(tous_les_couts(G, depart, but))
    print(f"1. Plan KYC : {len(G)} états ; meilleur coût par force brute C* = {c_etoile} s")
    assert c_etoile == 9

    print("2. A* avec h2 (somme des minima) : la liste ouverte à chaque itération")
    trace = []
    chemin, cout, dev_h2 = a_etoile(G, depart, but, h_somme_minima, rouvrir=False, trace=trace)
    for i, (n, f, vivants) in enumerate(trace, start=1):
        ouverte = ", ".join(f"{v}:{ff}" for ff, v in vivants)
        print(f"  it {i} : développe {n:6s} f = {f:2d}   ouverte = [{ouverte}]")
    print(f"  chemin = {chemin} ; coût = {cout} s ; nœuds développés = {dev_h2}")
    assert chemin == ["evaluation_auto", "uae_pass_identite", "api_salaire_wps"] and cout == 9
    assert [n for n, _, _ in trace] == ["∅", "E", "I+E"]   # seuls des nœuds du chemin optimal sont développés

    print("3. Même problème, trois heuristiques consistantes, h0 ≤ h1 ≤ h2 ≤ h*")
    resultats = {}
    for nom, h in (("h0 = 0 (Dijkstra)", h_nulle), ("h1 = 2 s par contrôle", h_par_controle),
                   ("h2 = somme des minima", h_somme_minima)):
        assert consistante(G, h, but)
        ch, c, d = a_etoile(G, depart, but, h, rouvrir=False)
        resultats[nom] = (c, d)
        print(f"  {nom:22s} coût = {c} s   nœuds développés = {d}")
        assert c == c_etoile                               # optimal à chaque fois
    devs = [d for _, d in resultats.values()]
    assert devs == sorted(devs, reverse=True) and devs[0] > devs[-1]   # plus h domine, moins on développe
    assert all(h_par_controle(n) <= h_somme_minima(n) for n in G)      # h2 domine h1
    assert all(h_somme_minima(n) <= min(tous_les_couts(G, n, but)) for n in G)   # h2 admissible

    print("4. Contre-exemple : h admissible mais inconsistante, ensemble fermé sans réouverture")
    # S = demande, A = appel API rapide, B = lecture OCR, C = revenu vérifié, G = offre émise.
    petit = {"S": [("A", 1, "S→A"), ("B", 1, "S→B")], "A": [("C", 1, "A→C")],
             "B": [("C", 3, "B→C")], "C": [("G", 3, "C→G")], "G": []}
    h_mal = {"S": 0, "A": 4, "B": 0, "C": 0, "G": 0}.get
    h_vrai = {n: min(tous_les_couts(petit, n, "G")) for n in petit}
    assert all(h_mal(n) <= h_vrai[n] for n in petit)                   # admissible...
    assert not consistante(petit, h_mal, "G")                          # ...mais h(A) = 4 > 1 + h(C)
    trace_mal = []
    ch1, c1, _ = a_etoile(petit, "S", "G", h_mal, rouvrir=False, trace=trace_mal)
    for i, (n, f, vivants) in enumerate(trace_mal, start=1):
        print(f"  it {i} : développe {n} f = {f}   ouverte = [{', '.join(f'{v}:{ff}' for ff, v in vivants)}]")
    ch2, c2, _ = a_etoile(petit, "S", "G", h_mal, rouvrir=True)
    ch3, c3, _ = a_etoile(petit, "S", "G", h_nulle, rouvrir=False)
    print(f"  sans réouverture : {ch1} coût {c1}   (sous-optimal)")
    print(f"  avec réouverture : {ch2} coût {c2}")
    print(f"  Dijkstra (h = 0) : {ch3} coût {c3}")
    assert (c1, c2, c3) == (7, 5, 5)

    print("5. Coût nul ou négatif refusé")
    try:
        a_etoile({"X": [("Y", 0, "gratuit")], "Y": []}, "X", "Y", h_nulle)
    except ValueError as e:
        print(f"  ValueError : {e}")
    else:
        raise AssertionError("un coût nul aurait dû être refusé")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Plan KYC : 8 états ; meilleur coût par force brute C* = 9 s
2. A* avec h2 (somme des minima) : la liste ouverte à chaque itération
  it 1 : développe ∅      f =  9   ouverte = [E:9, I:9, I+R:11, R:12]
  it 2 : développe E      f =  9   ouverte = [I:9, I+E:9, I+R:11, I+R+E:11, R:12, R+E:12]
  it 3 : développe I+E    f =  9   ouverte = [I:9, I+R+E:9, I+R:11, R:12, R+E:12]
  chemin = ['evaluation_auto', 'uae_pass_identite', 'api_salaire_wps'] ; coût = 9 s ; nœuds développés = 3
3. Même problème, trois heuristiques consistantes, h0 ≤ h1 ≤ h2 ≤ h*
  h0 = 0 (Dijkstra)      coût = 9 s   nœuds développés = 6
  h1 = 2 s par contrôle  coût = 9 s   nœuds développés = 5
  h2 = somme des minima  coût = 9 s   nœuds développés = 3
4. Contre-exemple : h admissible mais inconsistante, ensemble fermé sans réouverture
  it 1 : développe S f = 0   ouverte = [B:1, A:5]
  it 2 : développe B f = 1   ouverte = [C:4, A:5]
  it 3 : développe C f = 4   ouverte = [A:5, G:7]
  it 4 : développe A f = 5   ouverte = [G:7]
  sans réouverture : ['S→B', 'B→C', 'C→G'] coût 7   (sous-optimal)
  avec réouverture : ['S→A', 'A→C', 'C→G'] coût 5
  Dijkstra (h = 0) : ['S→A', 'A→C', 'C→G'] coût 5
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : f = g + h n'est pas une formule à appliquer à l'aveugle. L'heuristique doit être consistante si l'on ferme les nœuds sans les rouvrir, le but doit être testé à la sortie de la liste ouverte, et une heuristique dominante fait gagner des nœuds sans changer le coût.

## Squelette algorithmique

A\* prend en entrée un graphe donné par ses listes de voisins, avec un coût strictement positif sur chaque arc, un nœud de départ, un nœud but, une heuristique h et un choix : rouvrir ou non les nœuds déjà développés. Il renvoie la suite d'actions du meilleur chemin trouvé, son coût et le nombre de nœuds développés. L'idée est de tenir une liste ouverte rangée par f = g + h, de toujours développer le nœud le plus prometteur, de ne garder pour chaque nœud que le meilleur g connu, et de ne s'arrêter que lorsque le but **sort** de la liste ouverte. Avec h = 0, le même squelette est l'algorithme de Dijkstra.

```text
ALGORITHME AEtoile
ENTRÉES : voisins(n) = liste de (n′, c, action) avec c > 0, départ, but, heuristique h, rouvrir
SORTIE : chemin (liste d'actions), coût, nombre de nœuds développés

g(départ) ← 0
parent(départ) ← aucun
ouverts ← tas contenant (h(départ), h(départ), départ)
fermés ← ensemble vide
développés ← 0
TANT QUE ouverts n'est pas vide FAIRE
    (f, _, n) ← extraire le plus petit triplet de ouverts
    SI n ∈ fermés OU f ≠ g(n) + h(n) ALORS
        passer à l'itération suivante                 (entrée périmée)
    FIN SI
    SI n = but ALORS
        RETOURNER le chemin reconstruit en remontant parent, g(but), développés
    FIN SI
    fermés ← fermés ∪ {n}
    développés ← développés + 1
    POUR chaque (n′, c, action) de voisins(n) FAIRE
        SI c ≤ 0 ALORS
            échouer : coût invalide
        FIN SI
        SI n′ ∈ fermés ET non rouvrir ALORS
            passer au voisin suivant
        FIN SI
        SI g(n) + c < g(n′), avec g(n′) = ∞ si n′ est inconnu, ALORS
            g(n′) ← g(n) + c
            parent(n′) ← (n, action)
            retirer n′ de fermés                       (réouverture, si rouvrir)
            insérer (g(n′) + h(n′), h(n′), n′) dans ouverts
        FIN SI
    FIN POUR
FIN TANT QUE
RETOURNER aucun chemin, ∞, développés
```

**Complexité :** on note V le nombre de nœuds et E le nombre d'arcs. Avec une heuristique consistante et un ensemble fermé, chaque nœud est développé au plus une fois (point 6), donc chaque arc est examiné au plus une fois : il y a au plus E améliorations de g, donc au plus E + 1 insertions dans le tas et autant d'extractions, chacune en O(log E) = O(log V) puisque E ≤ V². Le temps total vaut O((V + E) log V), plus le coût des appels à h, ici O(1) chacun. La mémoire vaut O(V) pour g, parent et l'ensemble fermé, et O(E) pour le tas, qui peut contenir plusieurs entrées périmées d'un même nœud : O(V + E) en tout. Avec une heuristique admissible mais inconsistante et la réouverture, un nœud peut être redéveloppé plusieurs fois, et il existe des graphes où le nombre de redéveloppements croît de façon exponentielle avec V : la consistance est aussi une garantie de coût. Enfin, dans le plan KYC, V vaut 2ᵏ pour k contrôles : c'est la taille du graphe d'états, pas l'algorithme, qui explose.

**Du squelette au code :** tout le pseudo-code est la fonction `a_etoile`. L'initialisation correspond aux lignes `g = {depart: 0}`, `parent = {depart: None}`, `ouverts = [(h(depart), h(depart), depart)]` et `fermes = set()`. « Extraire le plus petit triplet » est `heapq.heappop(ouverts)`, et le test d'entrée périmée est `if n in fermes or f != g[n] + h(n): continue`. Le retour sur le but est le bloc `if n == but`, qui remonte `parent` jusqu'au départ puis inverse la liste avec `chemin[::-1]`. La boucle sur les voisins lit les triplets produits par `graphe_kyc()` ; « échouer : coût invalide » est le `raise ValueError`, le saut des nœuds fermés est `if voisin in fermes and not rouvrir: continue`, et l'amélioration de g se termine par `fermes.discard(voisin)` puis `heapq.heappush(...)`. L'heuristique h est l'une des fonctions `h_nulle`, `h_par_controle` ou `h_somme_minima`. Les fonctions `tous_les_couts` et `consistante` ne font pas partie d'A\* : ce sont les outils de vérification qui calculent C\* par force brute et testent la condition de consistance sur tous les arcs.

## Cas d'usage réels aux Émirats

Les coûts, latences, durées et seuils ci-dessous sont illustratifs. Les tarifs et règles cités par leur nom sont à confirmer avec les textes en vigueur.

### Banque — le plan d'outils d'un dossier de crédit

Une banque de détail de Dubaï fait préparer ses dossiers de crédit par un agent qui doit obtenir trois contrôles avant toute offre : identité, revenus et évaluation du bien. C'est exactement le graphe du programme : les outils sont des appels à des services internes, avec leur latence mesurée dans les journaux. A\* avec h₂ trouve en 3 nœuds développés le plan de 9 s (évaluation automatique, identité par UAE Pass, salaire par une API de paie), contre 11 s pour le contrôle KYC groupé suivi de l'évaluation. Quand l'API de salaire tombe en panne, l'agent retire son arc et relance la recherche : le meilleur plan devient le KYC groupé et l'évaluation, 11 s, plutôt que l'OCR des bulletins, 12 s. Sans A\*, un plan figé appellerait l'outil en panne, ou un plan écrit par le modèle oublierait qu'un outil exige l'identité vérifiée. Les obligations KYC et anti-blanchiment ne se négocient pas : le but exige les trois contrôles, aucune heuristique ne permet d'en sauter un, et la liste des outils autorisés est fermée. On suit la latence p95 du parcours et le taux de dossiers complets du premier coup.

### BTP — l'itinéraire d'une toupie de béton

Un groupe de construction qui mène de grands chantiers à Dubaï planifie les trajets de ses camions malaxeurs sur un graphe de tronçons routiers, dont le coût est un temps de parcours en minutes. L'heuristique est la distance à vol d'oiseau jusqu'au chantier, divisée par la vitesse maximale du modèle, ici 80 km/h. Elle est consistante : un tronçon ne se parcourt pas plus vite qu'à 80 km/h, et la distance à vol d'oiseau vérifie l'inégalité triangulaire, donc h(n) − h(n′) ≤ d(n, n′) / 80 ≤ c(n, n′). Pour une centrale à 24 km à vol d'oiseau, h vaut 18 minutes ; A\* trouve un trajet de 31 minutes en n'explorant que les tronçons orientés vers le chantier. L'erreur classique est de diviser par une vitesse moyenne, 50 km/h par exemple : h vaut alors 28,8 minutes et peut dépasser le vrai temps sur une autoroute dégagée, ce qui la rend inadmissible. Les restrictions horaires de circulation des poids lourds fixées par les autorités se codent en retirant des arcs selon le créneau, et la fenêtre de coulage du béton (90 minutes après le chargement, dans cet exemple) devient une contrainte sur le coût total. On suit la part des livraisons arrivées dans la fenêtre de coulage.

### Immobilier — ordonner les démarches d'un transfert de propriété

Une agence de Dubaï prépare le transfert d'un appartement vendu 2 000 000 AED. L'agent cherche la suite de démarches la moins chère en AED (certificat de non-objection du promoteur, mainlevée de l'hypothèque, rendez-vous de transfert), parmi plusieurs variantes dont certaines entraînent des frais de report. L'heuristique vaut les frais obligatoires qui restent à payer : les frais de transfert du DLD, 4 % de la valeur, soit 80 000 AED, tant qu'ils ne sont pas réglés. Elle est admissible, parce que tout plan complet les paie, et consistante, parce que le seul arc qui fait baisser h de 80 000 est celui qui règle ces frais. Sans elle, Dijkstra trouve les nœuds d'avant le paiement 80 000 AED moins chers que ceux d'après, et il explore tous les petits détours possibles avant de regarder un seul plan qui paie le transfert ; avec elle, f compare des plans à coût complet. La répartition des frais entre acheteur et vendeur se fixe au contrat, et l'agent ne la suppose pas. On suit l'écart entre les frais estimés par l'agent et les frais réellement payés, et le nombre de rendez-vous reportés.

### Crypto — router une conversion au moindre coût

Une plateforme d'actifs virtuels agréée par la VARA reçoit un ordre de conversion d'un montant équivalent à 1 000 000 AED d'un stablecoin vers des AED. Le graphe a pour nœuds les actifs et pour arcs les paires de marché de la plateforme. Les frais se multiplient d'un saut à l'autre ; pour les rendre additifs, on prend comme coût d'un saut c = −ln(1 − frais), qui est strictement positif. La paire directe à 0,30 % coûte −ln 0,997 ≈ 0,0030, soit 3 000 AED ; deux sauts à 0,10 % chacun coûtent 2 × (−ln 0,999) ≈ 0,0020, soit environ 1 999 AED. L'heuristique vaut le nombre minimal de sauts restants multiplié par le plus petit coût d'un saut : chaque arc fait baisser ce nombre d'au plus 1 et coûte au moins ce minimum, donc elle est consistante. L'agent propose la route en deux sauts, à condition que l'impact estimé sur le carnet d'ordres intermédiaire ne mange pas l'économie. La route et son coût attendu sont montrés au client avant exécution, seuls les marchés de la plateforme sont utilisés, et au-delà d'un seuil un opérateur valide. On suit l'écart entre le coût prévu et le coût réalisé.

### Secteur public — le parcours le plus court dans une démarche en ligne

Une entité de services publics en ligne guide les usagers, en arabe et en anglais, dans une demande qui exige quatre pièces. Un état est l'ensemble des pièces fournies, et le coût est le temps de l'usager en minutes : se connecter par UAE Pass fournit deux pièces préremplies en 1 minute, saisir une pièce à la main prend 5 minutes, téléverser un document 2 minutes. Le plus petit coût par pièce est 0,5 minute (UAE Pass, 1 minute pour deux pièces), et l'heuristique vaut 0,5 minute par pièce manquante, consistante pour la même raison que h₁ dans le programme. Au départ, h vaut 2 minutes ; A\* trouve le parcours UAE Pass puis deux téléversements, 5 minutes, contre 14 minutes pour quatre pièces saisies ou téléversées à la main. Si l'on avait pris 2 minutes par pièce, le coût d'un téléversement, l'heuristique aurait dépassé le coût de l'arc UAE Pass et perdu sa consistance. L'agent ne demande jamais une pièce que la démarche n'exige pas, comme le veut la minimisation des données de la PDPL, et le préremplissage suppose le consentement de l'usager. On suit le temps médian de complétion et le taux d'abandon.

### Assurance — choisir le garage agréé et le dépannage

Un assureur auto organise le dépannage d'un véhicule accidenté sur l'autoroute entre Dubaï et Abu Dhabi. Le graphe contient les tronçons routiers, les garages agréés du réseau et un nœud but virtuel relié à chaque garage par un arc dont le coût est le délai avant prise en charge. Le garage le plus proche est à 35 minutes de remorquage mais ne peut pas prendre le véhicule avant 120 minutes, soit 155 minutes au total ; un garage à 50 minutes peut le prendre en 20 minutes, soit 70 minutes. L'heuristique vaut la distance à vol d'oiseau jusqu'au garage le plus proche, divisée par la vitesse maximale du modèle : elle ignore les délais d'attente, ce qui la laisse admissible. A\* choisit le second garage ; une règle « le plus proche d'abord » ferait attendre l'assuré deux heures de plus. L'assurance est supervisée par la CBUAE, et le garage doit appartenir au réseau prévu par le contrat : les autres garages ne sont simplement pas dans le graphe. On suit le délai total entre l'appel de l'assuré et la prise en charge.

## Pièges et limites

- **Croire que « admissible » suffit toujours.** Avec un ensemble fermé sans réouverture, il faut une heuristique consistante ; sinon, le contre-exemple du point 3 renvoie 7 au lieu de 5.
- **Tester le but quand il entre dans la liste ouverte.** Dans le plan KYC, le but entre au tour 2 avec g = 11 : un test à l'entrée renvoie 11 au lieu de 9.
- **Surestimer h pour aller plus vite.** On perd la garantie d'optimalité. Si l'on veut vraiment échanger l'optimalité contre la vitesse, A\* pondéré borne la perte (voir « Pour aller plus loin »).
- **Additionner des unités différentes.** Secondes et AED ne s'additionnent pas : on convertit tout dans une seule unité (par exemple un coût en AED de la seconde d'attente), ou l'on traite l'une comme une contrainte.
- **Oublier la taille de l'espace d'états.** Avec k contrôles, il y a 2ᵏ états : 8 ici, plus d'un million pour 20 contrôles. L'heuristique compte alors bien plus que l'algorithme.

### Exercice feuille blanche

1. Sans regarder le code, écrire `a_etoile` avec `heapq`, un ensemble fermé et le test du but à la sortie, puis retrouver le plan de 9 s et les 3 nœuds développés.
2. Prédire, puis vérifier : `kyc_complet` passe à 4 s. Que vaut C\* ? h₂ reste-t-elle admissible, consistante ? (Réponse : C\* = 8, avec `kyc_complet` puis `evaluation_auto`. h₂(∅) = 9 > 8 : elle n'est plus admissible, ni consistante, puisque h₂(∅) = 9 > 4 + h₂(I+R) = 8. Sur ce graphe, A\* trouve encore 8, par chance : plus rien ne le garantit. La correction consiste à prendre pour chaque contrôle le plus petit coût par contrôle couvert, min(2, 4/2) = 2 pour I et min(4/2, 6, 3) = 2 pour R, ce qui donne h(∅) = 2 + 2 + 4 = 8, consistante.)
3. Trouver le bug : une variante renvoie `g[n] + cout` dès que `voisin == but`, au moment où elle génère le voisin. Que renvoie-t-elle sur le plan KYC ? (Réponse : 11, le premier chemin qui atteint le but, au lieu de 9.)

## Pour aller plus loin

**A\* pondéré.** On développe selon f = g + w h avec w ≥ 1, pour aller plus vite au prix de l'optimalité. Avec h admissible et réouverture, le coût renvoyé vérifie g(but) ≤ w C\*. Preuve : quand le but sort, le nœud nⱼ du lemme est dans la liste ouverte avec g(nⱼ) = g\*(nⱼ), et

$$
g(\text{but}) = f_w(\text{but}) \le f_w(n_j) = g^{*}(n_j) + w\, h(n_j) \le w \big( g^{*}(n_j) + h^{*}(n_j) \big) = w\, C^{*}
$$

parce que w ≥ 1 et h ≤ h\*. Sur le plan KYC avec h₂ et w = 2, A\* pondéré développe 2 nœuds et renvoie 11 s, sous la borne 2 × 9 = 18 s.

**Autres variantes.** IDA\* (A\* en profondeur itérée) économise la mémoire. La recherche bidirectionnelle part des deux bouts. D\* Lite replanifie sans tout recommencer quand des coûts changent en cours de route, comme quand un outil tombe en panne.

> Suite : [Orchestration : définitions fondamentales](<../08-Orchestration/40b-Orchestration-Definitions-Fondamentaux.md>) — étape 40 bis.
