# Étape 72 bis — Production — Batching continu et PagedAttention

**Dossier :** 12-Production-Couts-Optimisation

> Étape 72 bis du parcours · Prérequis : [Coûts et gestion des tokens](<72-Couts-et-Gestion-des-Tokens.md>) · Suite : [Décodage spéculatif](<72c-Decodage-Speculatif.md>)

## Définition

Un serveur de LLM ne traite pas les requêtes une par une : à chaque **itération**, il fait avancer d'un token toutes les séquences d'un **lot**, parce qu'une carte graphique lit ses poids une fois pour tout le lot et que le décodage est limité par la mémoire plus que par le calcul. Le **batching statique** forme un lot de B requêtes et le garde jusqu'à ce que la plus longue ait fini : les cases des requêtes terminées restent vides, c'est du remplissage (*padding*). Le **batching continu** (ordonnancement à l'itération) rend chaque case libérée à la requête suivante de la file dès l'itération d'après. **PagedAttention** gère la mémoire du cache clé-valeur (KV) comme un système d'exploitation gère la mémoire virtuelle : le cache de chaque séquence est découpé en **blocs** de b tokens, placés n'importe où dans la mémoire et retrouvés grâce à une **table de blocs**. Une séquence gaspille alors au plus b − 1 places, au lieu de réserver d'avance la longueur maximale.

## Rôle dans un agent

Ces deux techniques vivent dans le moteur d'inférence, sous la boucle percevoir → décider → agir → observer, mais elles fixent ce que la boucle coûte et combien de temps elle attend. Un agent produit des sorties de longueurs très inégales : un appel d'outil tient en quelques dizaines de tokens, un rapport ou un contrat en plusieurs centaines. Avec un lot statique, chaque appel d'outil court attend la fin de la rédaction la plus longue de son lot, et la latence de chaque étape de l'agent s'allonge. Quand l'équipe héberge elle-même un modèle, ce fichier sert à dimensionner le serveur : la mémoire du cache KV, et non celle des poids, borne souvent le nombre de sessions simultanées, et la façon de l'allouer change ce nombre d'un facteur 7 dans l'exemple. Quand l'équipe passe par une API, elle ne règle rien de tout cela, mais elle en observe les effets : une latence qui dépend de la charge du fournisseur, et des prix plus bas pour les traitements en lots différés.

## Équation complète

Utilisation des cases d'un lot statique (B cases, longueurs de sortie ℓᵢ) :

$$
U_{stat} = \frac{\sum_{i \in \text{lot}} \ell_i}{B \cdot \max_{i \in \text{lot}} \ell_i}
$$

Durée totale H du batching continu, quand toutes les requêtes sont en attente au départ :

$$
\max\Bigl(\frac{1}{B} \sum_{i=1}^{R} \ell_i ,\; \ell_{max}\Bigr) \;\le\; H_{cont} \;\le\; \frac{1}{B} \sum_{i=1}^{R} \ell_i + \ell_{max}
$$

Débit, latence moyenne, loi de Little (étape 69) :

$$
X = \frac{1}{H} \sum_{i=1}^{R} \ell_i, \qquad W = \frac{1}{R} \sum_{i=1}^{R} \bigl(\text{fin}_i - \text{arrivée}_i\bigr), \qquad L = \lambda \, W
$$

Charge et taux d'arrivée maximal du batching continu :

$$
\rho = \frac{\lambda \, \mathbb{E}[\ell]}{B}, \qquad \lambda_{max} = \frac{B}{\mathbb{E}[\ell]}
$$

Blocs d'une séquence de n tokens et places perdues dans le dernier bloc :

$$
\text{blocs}(n) = \left\lceil \frac{n}{b} \right\rceil, \qquad \text{gaspillage}(n) = b \left\lceil \frac{n}{b} \right\rceil - n \;\le\; b - 1
$$

Utilisation de la mémoire du cache pour S séquences, paginée ou réservée à la longueur maximale :

$$
U_{pag} = \frac{\sum_{s=1}^{S} n_s}{b \sum_{s=1}^{S} \lceil n_s / b \rceil}, \qquad U_{rés} = \frac{\sum_{s=1}^{S} n_s}{S \cdot n_{max}}
$$

Taille du cache KV par token (étape 34) et blocs économisés par un préfixe partagé :

$$
\text{octets par token} = 2 \, N_c \, h_{kv} \, d_h \, o, \qquad \text{blocs économisés} = (S - 1) \left\lfloor \frac{n_p}{b} \right\rfloor
$$

## Décryptage des symboles

$$
B
$$

Le nombre de cases du serveur, c'est-à-dire le nombre maximal de séquences décodées ensemble à chaque itération : un entier ≥ 1 ; argument `B`.

$$
\ell_i
$$

Le nombre de tokens que la requête i doit générer ; on compte une itération de décodage par token : un entier ≥ 1 ; champ `Requete.longueur`.

$$
R
$$

Le nombre de requêtes de la trace : un entier ≥ 1 ; c'est `len(reqs)`.

$$
U_{stat}
$$

La part des cases d'un lot statique qui produisent un vrai token : un réel dans ]0 ; 1] ; valeur `utilisation` renvoyée par `mesures`.

$$
H
$$

La durée totale de la trace, de l'instant 0 à la fin de la dernière requête, en itérations : un réel > 0 ; champ `"fin"` du résultat d'une simulation.

$$
\ell_{max}
$$

La plus grande longueur de sortie de la trace : un entier ; `max(r.longueur for r in ...)`.

$$
X
$$

Le débit, en tokens générés par itération : un réel ≥ 0 ; valeur `debit`.

$$
W
$$

Le séjour moyen d'une requête, de son arrivée à la fin de sa génération, en itérations : c'est la latence moyenne ; valeur `latence`.

$$
\lambda
$$

Le taux d'arrivée des requêtes, en requêtes par itération : un réel > 0 ; argument `lam` de `generer`.

$$
L
$$

Le nombre moyen de requêtes présentes dans le serveur, en attente ou en cours : un réel ≥ 0 ; `nombre_moyen_present(reqs, horizon)`.

$$
\rho
$$

La charge du serveur à batching continu, la part des cases qu'il faudrait occuper en moyenne pour suivre les arrivées : un réel ≥ 0, qui doit rester < 1 ; affichée comme `charge λ·E[ℓ]/B`.

$$
b
$$

La taille d'un bloc du cache KV, en tokens : un entier ≥ 1, souvent 16 ; argument `taille_bloc`.

$$
n, \quad n_{max}
$$

Le nombre de tokens réellement présents dans le cache d'une séquence (prompt et sortie déjà produite), et la longueur maximale qu'une allocation par réservation retient d'avance : des entiers ; `longueurs` et `n_max`.

$$
S
$$

Le nombre de séquences présentes dans le cache : un entier ≥ 1 ; c'est `len(longueurs)`.

$$
N_c, \quad h_{kv}, \quad d_h, \quad o
$$

Le nombre de couches du modèle, le nombre de têtes de clés-valeurs, la largeur d'une tête et le nombre d'octets par nombre stocké (2 en 16 bits) : des entiers ; arguments de `octets_kv_par_token`.

$$
n_p
$$

La longueur, en tokens, d'un préfixe commun à plusieurs séquences, typiquement le prompt système : un entier ≥ 0 ; variable `prefixe`.

## Démonstration

### 1. Le lot statique attend sa requête la plus longue

Un lot statique occupe ses B cases pendant max ℓᵢ itérations, puisqu'il ne rend la main qu'à la fin de la plus longue génération. Il produit ∑ ℓᵢ tokens utiles sur B · max ℓᵢ cases-itérations, d'où U_stat. La perte vaut ∑ (max ℓ − ℓᵢ) cases-itérations : chaque requête courte bloque sa case pendant que la plus longue termine. Dans le pire cas, un lot contient une requête de longueur ℓ et B − 1 requêtes d'un seul token, et

$$
U_{stat} = \frac{\ell + B - 1}{B \, \ell} \;\xrightarrow[\ell \to \infty]{}\; \frac{1}{B}
$$

parce que le numérateur se comporte comme ℓ et le dénominateur comme B ℓ. Avec 16 cases, un lot statique peut donc tomber à environ 6 % d'utilisation. Dans l'exemple à la main (B = 2, longueurs [2, 8, 3, 3]), le premier lot occupe 2 × 8 = 16 cases pour 10 tokens utiles, le second 2 × 3 = 6 cases pour 6 tokens : U = 16 / 22 ≈ 0,7273.

### 2. Le batching continu reste à moins d'une requête de l'optimum

On suppose les R requêtes en attente à l'instant 0. **Borne basse.** Chaque itération produit au plus B tokens, donc H ≥ (∑ ℓᵢ) / B ; et la requête la plus longue produit un token par itération, donc H ≥ ℓ_max. Aucun ordonnanceur ne fait mieux que le plus grand des deux. **Borne haute** (argument de Graham pour l'ordonnancement de listes). Soit j la dernière requête à finir, et sⱼ l'itération où elle obtient une case. Avant sⱼ, les B cases étaient toutes occupées à chaque itération, sinon j aurait été admise plus tôt, puisqu'elle attendait. Les tokens produits avant sⱼ appartiennent aux autres requêtes, donc

$$
B \, s_j \le \sum_{i \ne j} \ell_i
\quad\Longrightarrow\quad
H = s_j + \ell_j \le \frac{1}{B} \sum_{i=1}^{R} \ell_i + \Bigl(1 - \frac{1}{B}\Bigr) \ell_j \le \frac{1}{B} \sum_{i=1}^{R} \ell_i + \ell_{max}
$$

Le batching continu ne perd donc, au pire, que la durée d'une requête par rapport à l'optimum. Dans l'exemple, ∑ ℓᵢ / B = 8 et ℓ_max = 8 : la borne basse vaut 8, la borne haute 16, et le batching continu finit en 8 itérations, l'optimum. Le lot statique, lui, finit en 11.

### 3. La latence : une requête courte n'attend plus la plus longue

Dans l'exemple, le lot statique sert les deux premières requêtes, finies aux itérations 2 et 8 ; les deux suivantes ne commencent qu'à l'itération 8 et finissent à 11. Les séjours valent [2, 8, 11, 11] et la latence moyenne 8. En batching continu, la troisième requête prend la case libérée par la première à l'itération 2 et finit à 5 ; la quatrième prend la même case à 5 et finit à 8. Les séjours valent [2, 8, 5, 8] et la moyenne 5,75. Le débit passe de 16 / 11 ≈ 1,4545 à 16 / 8 = 2 tokens par itération, et l'utilisation de 0,7273 à 1.

### 4. La loi de Little fixe la capacité

Sur une trace observée de l'instant 0 à H, l'aire sous la courbe N(s), le nombre de requêtes présentes à l'instant s, vaut la somme des séjours, parce que chaque requête ajoute 1 à N pendant exactement son séjour (argument d'aire de l'étape 69). En divisant par H :

$$
L = \frac{1}{H} \int_0^H N(s)\, ds = \frac{1}{H} \sum_{i=1}^{R} W_i = \frac{R}{H} \cdot \frac{1}{R} \sum_{i=1}^{R} W_i = \lambda \, W
$$

où λ = R / H est le taux d'arrivée observé. Le programme calcule l'aire indépendamment, par un balayage des arrivées et des départs, et retrouve λ W à 10⁻⁹ près sur les quatre traces.

La même loi, appliquée aux seules cases, donne la capacité. En batching continu, une requête occupe une case pendant exactement ℓᵢ itérations, et une case occupée produit un token par itération : le nombre moyen de cases occupées vaut λ E[ℓ], et c'est aussi le débit en tokens par itération. Comme il ne peut pas dépasser B, le serveur ne suit les arrivées que si

$$
\rho = \frac{\lambda \, \mathbb{E}[\ell]}{B} < 1 \quad\Longleftrightarrow\quad \lambda < \lambda_{max} = \frac{B}{\mathbb{E}[\ell]}
$$

En batching statique, un lot plein occupe B cases pendant la plus longue de ses B générations : la capacité tombe à B / E[max ℓ du lot], bien plus bas quand les longueurs sont inégales.

Le programme le mesure sur une charge d'agent simulée : 400 requêtes, B = 16, 80 % d'appels d'outils de 10 à 60 tokens et 20 % de rédactions de 200 à 600 tokens, soit une longueur moyenne de 124,13 tokens. À λ = 0,02 requête par itération (ρ = 0,155), les deux serveurs suivent les arrivées et ont presque le même débit, environ 2,4 tokens par itération, imposé par les arrivées ; seule la latence diffère, 341,6 itérations en statique contre 124,6 en continu. À λ = 0,12 (ρ = 0,931), le serveur continu suit encore : latence 129,1 itérations, à peine plus que la longueur moyenne, et débit 12,820. Le serveur statique est saturé : son débit plafonne à 3,849 tokens par itération, soit 3,849 / 124,13 ≈ 0,031 requête par itération, ce qui correspond à des lots de 16 qui durent environ 16 / 0,031 ≈ 516 itérations, la durée de leur plus longue rédaction. Sa file grandit sans cesse et la latence moyenne atteint 4 695,5 itérations.

### 5. La pagination perd au plus b − 1 places par séquence

On écrit n = q b + r avec 0 ≤ r < b. Si r = 0, la séquence remplit exactement q blocs et ne perd rien. Sinon, il faut q + 1 blocs et la perte vaut b(q + 1) − n = b − r, qui est compris entre 1 et b − 1. Dans les deux cas,

$$
0 \le b \left\lceil \frac{n}{b} \right\rceil - n \le b - 1
$$

Si le reste r est équiréparti entre 0 et b − 1, la perte moyenne vaut (0 + (b − 1) + (b − 2) + ⋯ + 1) / b = (b − 1) / 2, soit 7,5 tokens pour b = 16 ; le programme le vérifie sur les longueurs 1 à 1 600. Avec la réservation, chaque séquence perd n_max − n, qui peut valoir presque n_max. Pour les longueurs [37, 120, 5, 64] et b = 16, il faut 3 + 8 + 1 + 4 = 16 blocs, soit 256 places pour 226 tokens : U_pag = 226 / 256 ≈ 0,8828, avec des pertes de [11, 8, 11, 0]. Réserver 512 places par séquence donne U_rés = 226 / 2 048 ≈ 0,1104.

Les blocs ont aussi un autre avantage : ils sont interchangeables. N'importe quel bloc libre peut servir n'importe quelle séquence, si bien que l'allocateur n'échoue que s'il ne reste **aucun** bloc libre. Une réservation contiguë, elle, peut échouer alors que la mémoire libre totale suffirait, parce que celle-ci est découpée en trous trop petits pour n_max (fragmentation externe).

Le choix de b est un compromis. Avec b = 1, aucune place n'est perdue, mais la table compte une entrée par token (226 pour l'exemple) et chaque lecture du cache saute d'un endroit à l'autre de la mémoire. Avec b = 128, la table n'a que 4 entrées, mais l'utilisation tombe à 0,4414. b = 16 garde une table de 16 entrées et une utilisation de 0,8828.

### 6. Combien de sessions tiennent dans la mémoire

Pour un modèle de 32 couches à 8 têtes de clés-valeurs de largeur 128, stockées sur 2 octets, un token occupe 2 × 32 × 8 × 128 × 2 = 131 072 octets de cache (étape 34). Un budget de 20 Go de cache contient donc 152 587 tokens, soit 9 536 blocs de 16. En réservant 8 192 tokens par session, on loge 18 sessions. En paginant, une session dont le contexte réel compte 1 200 tokens occupe ⌈1 200 / 16⌉ = 75 blocs, et l'on en loge 127, sept fois plus. La contrepartie : une session admise sur sa taille actuelle peut grandir et ne plus trouver de bloc libre. L'ordonnanceur doit alors la mettre en pause ou la préempter, c'est-à-dire libérer son cache pour le recalculer ou le recharger plus tard ; le programme montre l'erreur `MemoryError` qui signale ce moment.

### 7. Un préfixe partagé ne se stocke qu'une fois

Quand plusieurs séquences commencent par les mêmes tokens, typiquement le prompt système, leurs blocs pleins de préfixe peuvent pointer vers les mêmes blocs physiques. Un compteur de références indique combien de tables pointent vers chaque bloc, et un bloc ne retourne à la liste des blocs libres que lorsque son compteur tombe à 0. Le dernier bloc du préfixe, s'il est incomplet, est **copié à l'écriture** : la première séquence qui y écrit reçoit sa propre copie. S séquences qui partagent un préfixe de n_p tokens économisent donc (S − 1) ⌊n_p / b⌋ blocs : pour un prompt système de 1 000 tokens et 50 sessions, 49 × 62 = 3 038 blocs, soit 6,37 Go avec 131 072 octets par token. C'est la version « mémoire » du cache de préfixe que l'étape 72 présentait sous l'angle du prix.

### 8. Exemple fait à la main (le code reprend ces nombres)

- Ordonnancement, B = 2, longueurs [2, 8, 3, 3] : statique, fin à 11, séjours [2, 8, 11, 11], latence 8, utilisation 16/22 ; continu, fin à 8, séjours [2, 8, 5, 8], latence 5,75, utilisation 1.
- Pagination, b = 16, longueurs [37, 120, 5, 64] : blocs [3, 8, 1, 4], pertes [11, 8, 11, 0], utilisation 226/256 ; réservation à 512, utilisation 226/2 048.
- Le 37ᵉ token de la séquence A, en position 36 à partir de 0, se trouve dans le bloc logique 36 // 16 = 2, au décalage 36 − 32 = 4.

## Effets et comportement

- **Plus les longueurs sont inégales, plus le batching continu gagne.** Si toutes les requêtes d'un lot ont la même longueur, U_stat = 1 et les deux méthodes se valent.
- **À faible charge, le débit est imposé par les arrivées.** Les deux serveurs produisent ce qu'on leur demande ; la différence porte sur la latence. À forte charge, le lot statique sature bien avant le batching continu.
- **Quand ρ approche 1, l'attente explose.** C'est le facteur 1/(1 − ρ) de la file M/M/1 (étape 70) : on dimensionne avec une marge, pas à la capacité.
- **La mémoire du cache, plus que les poids, borne le nombre de sessions.** La pagination multiplie ce nombre quand les contextes réels sont loin de la longueur maximale.
- **Un petit b gaspille moins mais coûte en gestion.** La table grandit et les lectures se dispersent ; 16 est un compromis courant.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| requête i, ℓᵢ, arrivée, fin | `Requete(ident, arrivee, longueur, fin)` |
| lot statique de B cases | `simuler_statique(requetes, B)` |
| batching continu | `simuler_continu(requetes, B)` |
| H, X, W, p95, U | `mesures(res)` : `fin`, `debit`, `latence`, `p95`, `utilisation` |
| L = (1/H) ∫ N(s) ds | `nombre_moyen_present(reqs, horizon)` |
| arrivées au taux λ | `generer(n, lam, graine)` |
| blocs(n), gaspillage(n) | `blocs_necessaires(n, b)`, `gaspillage(n, b)` |
| U_pag, U_rés | `utilisation_paginee(longueurs, b)`, `utilisation_reservee(longueurs, n_max)` |
| table de blocs, partage de préfixe | `AllocateurPagine` |
| 2 N_c h_kv d_h o | `octets_kv_par_token(couches, tetes_kv, d_tete, octets)` |

### Déroulé, ligne par ligne

**`Requete`** est une `dataclass` : `arrivee` et `fin` se mesurent en itérations sur une horloge simulée, jamais sur l'horloge réelle, et `fin` vaut −1 tant que la requête n'est pas terminée. **`copier`** recopie les requêtes, pour que deux simulations ne partagent pas les mêmes objets.

**`simuler_statique(requetes, B)`**.

- La file est triée par arrivée. Si la prochaine requête n'est pas encore arrivée, `t = math.ceil(file[i].arrivee)` avance l'horloge.
- La boucle intérieure remplit `lot` avec au plus B requêtes déjà arrivées. Dans l'exemple, à `t = 0`, le lot contient les requêtes de longueurs 2 et 8.
- `duree = max(...)` vaut 8. Chaque requête reçoit `fin = t + longueur` (2 et 8), mais `cases_occupees += B * duree` compte 16 cases, parce que les deux cases restent prises pendant 8 itérations.
- `t += duree` passe à 8 ; le second lot (3 et 3) finit à 11, et `cases_occupees` vaut 16 + 6 = 22.

**`simuler_continu(requetes, B)`**.

- En tête de chaque itération, la boucle `while ... len(actives) < B` admet les requêtes arrivées dans les cases libres, et `reste` retient ce qu'il leur reste à produire.
- `t += 1` puis `reste[r.ident] -= 1` pour chaque requête active : une itération, un token par case occupée.
- Dès que `reste` atteint 0, la requête reçoit `fin = t` et quitte `actives` ; la case est réattribuée au tour suivant. Dans l'exemple, la requête de longueur 2 finit à 2, celle de longueur 3 entre à 2 et finit à 5, la dernière entre à 5 et finit à 8, en même temps que celle de longueur 8.
- `cases_occupees += B` à chaque itération active donne 8 × 2 = 16 cases pour 16 tokens : l'utilisation vaut 1.

**`mesures(res)`** calcule les séjours `fin - arrivee`, le débit `tokens / fin`, la latence moyenne, le p95 par la fonction canonique `p95` et l'utilisation `tokens / cases`.

**`nombre_moyen_present(reqs, horizon)`** trie les événements (arrivée : +1, départ : −1), additionne `present * (instant - precedent)` entre deux événements, puis divise l'aire par l'horizon. C'est un calcul indépendant de la latence : l'égalité avec `lam_obs * latence` vérifie la loi de Little.

**`generer(n, lam, graine)`** utilise un générateur `random.Random(graine)` qui lui est propre : `expovariate(lam)` tire les durées entre deux arrivées, d'où des arrivées de Poisson ; `random() < 0.8` choisit une requête courte (`randint(10, 60)`) ou longue (`randint(200, 600)`).

**`AllocateurPagine`**.

- `libres` est une pile de numéros de blocs, préparée pour servir le bloc 0 en premier ; `refs[bloc]` compte les tables qui pointent vers chaque bloc.
- `ajouter_tokens(seq, n)` ajoute les tokens un par un. Si `long % self.b == 0`, le dernier bloc est plein, ou il n'y en a pas : on prend un bloc libre. Pour 37 tokens, cela arrive aux tokens 0, 16 et 32, et la table vaut `[0, 1, 2]`.
- Si le dernier bloc est partagé (`refs > 1`), on prend un nouveau bloc pour la séquence qui écrit : c'est la copie à l'écriture. Un vrai moteur y recopie aussi les 5 entrées K et V déjà présentes ; le programme ne suit que l'occupation.
- `partager_prefixe("A", "B")` recopie la table de A dans celle de B et incrémente les compteurs : `[0, 1, 2]` passe à 2 références chacun. Quand B ajoute un token, le bloc partiel 2 est partagé, donc B reçoit le bloc 3 : sa table vaut `[0, 1, 3]` et les compteurs `[2, 2, 1, 1]`.
- `adresse(seq, position)` renvoie `(table[position // b], position % b)` : pour la position 36, `(2, 4)`.
- `liberer(seq)` décrémente les compteurs et ne rend un bloc à la pile que lorsque son compteur tombe à 0. Après la libération de A et de B, les 64 blocs sont libres.
- `_prendre()` lève `MemoryError` quand la pile est vide : 33 tokens demandent 3 blocs de 16, et l'allocateur n'en a que 2.

**`blocs_necessaires`, `gaspillage`, `utilisation_paginee`, `utilisation_reservee`** appliquent les formules du point 5 ; `octets_kv_par_token(32, 8, 128, 2)` renvoie 131 072.

**`main()`**, bloc par bloc.

1. L'exemple à la main, statique puis continu ; les `assert` vérifient les séjours, les latences, les utilisations et l'encadrement de Graham (points 1 à 3).
2. Les deux charges simulées avec la graine 72 ; pour chaque trace, l'`assert` de la loi de Little compare l'aire balayée à λ W ; à λ = 0,12, le batching continu doit avoir une latence au moins dix fois plus petite et un débit au moins deux fois plus grand (point 4).
3. Les blocs, les pertes et les deux utilisations, la borne b − 1 sur les longueurs 1 à 1 999, la perte moyenne (b − 1)/2, puis le compromis sur b (point 5).
4. L'allocateur : table, adresse, partage avec copie à l'écriture, libération complète, puis `MemoryError` (points 5 à 7).
5. Le dimensionnement : 131 072 octets par token, 18 sessions réservées contre 127 paginées, et les 3 038 blocs économisés par le prompt système partagé (points 6 et 7).

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`p95(valeurs)`** — Cette fonction est le juge de ligne qui ne regarde que les derniers coureurs, ceux qui fâchent les utilisateurs : elle reçoit une liste de durées, lève une `ValueError` si elle est vide, la trie, puis renvoie la valeur de rang ⌈0,95 × N⌉, le percentile 95 au rang le plus proche, c'est-à-dire la plus petite durée sous laquelle tombent au moins 95 % des valeurs. C'est la version canonique du parcours, appelée par `mesures` pour chaque trace simulée ; à λ = 0,12, elle sépare les 8 596,4 itérations du lot statique des 505,0 itérations du batching continu.

**`copier(requetes)`** — Celle-ci est le photocopieur qui garantit que deux expériences ne se marchent pas sur les pieds : elle reçoit une liste de `Requete` et renvoie une nouvelle liste de requêtes neuves, avec le même identifiant, la même arrivée et la même longueur, mais un champ `fin` remis à −1. Sans elle, `simuler_statique` et `simuler_continu`, qui écrivent toutes deux l'instant de fin dans les objets, se partageraient les mêmes requêtes et la seconde simulation écraserait les résultats de la première.

**`simuler_statique(requetes, B)`** — Cette fonction joue le vieux bac de ferry qui ne repart que lorsque tous ses passagers sont débarqués : elle reçoit les requêtes et le nombre de cases B, trie une copie par arrivée, avance l'horloge simulée jusqu'à la prochaine arrivée quand le serveur est vide, remplit un lot d'au plus B requêtes déjà arrivées, puis fait tourner ce lot pendant la durée de la plus longue. Chaque requête reçoit sa fin propre, mais les B cases restent comptées comme occupées pendant tout le lot ; la fonction renvoie un dictionnaire avec les requêtes, l'instant final et le nombre de cases occupées, soit 11 itérations et 22 cases pour l'exemple à la main des longueurs 2, 8, 3 et 3.

**`simuler_continu(requetes, B)`** — Celle-ci joue le téléphérique dont chaque cabine libérée repart aussitôt avec le voyageur suivant : elle reçoit les requêtes et B, trie une copie, puis, à chaque itération, admet dans les cases libres les requêtes déjà arrivées, saute à la prochaine arrivée s'il n'y a rien à faire, avance l'horloge d'une itération en faisant produire un token à chaque requête active et retire celles qui ont fini en notant leur fin. Elle renvoie le même dictionnaire que la version statique ; sur l'exemple, tout est terminé à 8 itérations, avec 16 cases occupées pour 16 tokens, donc une utilisation de 1.

**`mesures(res)`** — Cette fonction est le statisticien qui dépouille le carnet de bord d'une simulation : elle reçoit le dictionnaire rendu par un ordonnanceur, calcule le séjour de chaque requête, fin moins arrivée, et le nombre total de tokens, puis renvoie l'instant final, le débit en tokens par itération, la latence moyenne, le p95 donné par `p95`, l'utilisation des cases, tokens divisés par cases occupées, et la liste des séjours. Pour l'exemple à la main, elle donne un débit de 1,4545 et une latence de 8 en statique, contre 2 et 5,75 en continu.

**`nombre_moyen_present(reqs, horizon)`** — Celle-ci est le gardien de salle qui, sans regarder les tickets, compte les présents à chaque mouvement de porte : elle reçoit des requêtes terminées et la durée d'observation, fabrique un événement +1 à chaque arrivée et −1 à chaque fin, les trie, additionne entre deux événements le nombre de présents multiplié par le temps écoulé, puis divise cette aire par l'horizon. Elle renvoie le nombre moyen de requêtes dans le système, calculé indépendamment des latences, et `main` vérifie à 10⁻⁹ près qu'il égale le débit d'arrivée observé multiplié par la latence moyenne, ce qui est la loi de Little.

**`generer(n, lam, graine)`** — Cette fonction est le scénariste qui écrit la journée d'un serveur d'agents : elle reçoit le nombre de requêtes, le taux d'arrivée λ par itération et une graine, fait tirer à son propre générateur des écarts exponentiels entre arrivées, donc des arrivées de Poisson, et donne à chaque requête une longueur courte, entre 10 et 60 tokens, avec la probabilité 0,8, ou longue, entre 200 et 600 tokens, sinon. Elle renvoie la liste des requêtes ; avec 400 requêtes et la graine 72, la longueur moyenne vaut 124,13 tokens, si bien que λ = 0,12 charge les 16 cases à 0,931.

**`AllocateurPagine.__init__(n_blocs, taille_bloc)`** — Le constructeur ouvre le registre d'un gestionnaire d'entrepôt dont les étagères ont toutes la même taille : il reçoit le nombre de blocs et le nombre de tokens par bloc, range cette taille dans `self.b`, prépare la pile `libres` à l'envers pour que le bloc 0 sorte en premier, met à zéro le compteur de références de chaque bloc et crée deux dictionnaires vides, les tables de blocs et les longueurs des séquences. Il ne renvoie rien ; `main` l'appelle avec 64 blocs de 16 tokens, puis avec 2 blocs seulement pour provoquer le manque de mémoire.

**`AllocateurPagine._prendre()`** — Cette méthode est le magasinier qui sort une étagère vide de la réserve : elle ne reçoit rien, lève une `MemoryError` si la pile des blocs libres est vide, signe qu'il faut faire attendre ou préempter la séquence, et sinon dépile un numéro de bloc, fixe son compteur de références à 1 et le renvoie. Dans la section 4 de `main`, 33 tokens réclament trois blocs de 16 alors que l'allocateur réduit n'en possède que 2, et c'est elle qui lève l'erreur.

**`AllocateurPagine.ajouter_tokens(seq, n)`** — Celle-ci range les nouveaux tokens d'une séquence, un à un, comme un archiviste qui ouvre un nouveau classeur dès que le précédent est plein : elle reçoit le nom de la séquence et le nombre de tokens à ajouter, crée au besoin sa table, prend un bloc neuf par `_prendre` chaque fois que la longueur est un multiple de la taille de bloc, et, si le dernier bloc est partagé avec une autre séquence, le remplace par un bloc neuf en décrémentant l'ancien compteur, ce qui est la copie à l'écriture. Elle ne renvoie rien ; pour 37 tokens, la table de A devient 0, 1, 2, et quand B écrit après avoir partagé ce préfixe, sa table devient 0, 1, 3.

**`AllocateurPagine.partager_prefixe(source, nouvelle)`** — Cette méthode est le bibliothécaire qui prête un même volume à deux lecteurs au lieu d'en imprimer un second exemplaire : elle reçoit le nom de la séquence source et celui de la nouvelle, recopie la table de blocs et la longueur de la source, puis augmente de un le compteur de références de chaque bloc partagé, sans copier aucune donnée du cache. Elle ne renvoie rien ; après le partage de A vers B, les blocs 0, 1 et 2 comptent chacun deux références, et c'est ce mécanisme qui économise 3 038 blocs quand cinquante sessions partagent le même prompt système.

**`AllocateurPagine.adresse(seq, position)`** — Celle-ci traduit une adresse logique en adresse physique, comme un plan de rangement qui indique l'étagère et la place sur l'étagère : elle reçoit le nom de la séquence et la position d'un token, puis renvoie le couple formé par le bloc lu dans la table au rang `position // b` et le décalage `position % b`. Pour la position 36 de la séquence A, avec des blocs de 16, elle renvoie le bloc 2 et le décalage 4, exactement la traduction d'adresse d'une mémoire virtuelle.

**`AllocateurPagine.liberer(seq)`** — Cette méthode est le magasinier qui rend les étagères quand un client s'en va, mais seulement celles que personne d'autre n'utilise : elle reçoit le nom de la séquence, retire sa table, décrémente le compteur de chacun de ses blocs et ne remet un bloc dans la pile libre que lorsque son compteur tombe à zéro, puis efface la longueur de la séquence. Elle ne renvoie rien ; après la libération de A puis de B, `main` vérifie que les 64 blocs sont de nouveau libres et qu'aucun n'est compté deux fois.

**`AllocateurPagine.blocs_utilises()`** — Celle-ci fait l'inventaire de l'entrepôt d'un simple coup d'œil sur les compteurs : elle ne reçoit rien, parcourt la liste des compteurs de références et renvoie le nombre de blocs dont le compteur est strictement positif, c'est-à-dire les blocs physiques réellement occupés, quel que soit le nombre de séquences qui les partagent. Dans la section 4, elle vaut 4 après le partage et la copie à l'écriture, puis 0 après la libération des deux séquences.

**`blocs_necessaires(n, b)`** — Cette fonction répond à la question du déménageur qui doit savoir combien de cartons de taille b il faut pour n objets : elle reçoit le nombre de tokens n et la taille de bloc b, et renvoie ⌈n/b⌉, le plus petit nombre de blocs qui les contient. Pour les longueurs 37, 120, 5 et 64 avec des blocs de 16, elle rend 3, 8, 1 et 4, soit 16 blocs en tout, et elle sert aussi au dimensionnement final, où une session de 1 200 tokens réclame 75 blocs.

**`gaspillage(n, b)`** — Celle-ci mesure la place vide au fond du dernier carton : elle reçoit n et b, et renvoie b⌈n/b⌉ − n, le nombre de places réservées mais inutilisées dans le dernier bloc d'une séquence, toujours au plus b − 1. Pour les quatre longueurs de l'exemple, elle donne 11, 8, 11 et 0, et `main` vérifie la borne b − 1 sur toutes les longueurs de 1 à 1 999, ainsi que la perte moyenne exacte de (b − 1)/2 sur les longueurs de 1 à 1 600.

**`utilisation_paginee(longueurs, b)`** — Cette fonction est l'inspecteur qui calcule le taux de remplissage d'un entrepôt rangé par blocs : elle reçoit la liste des longueurs de séquences et la taille de bloc, et renvoie la somme des tokens divisée par le nombre de places réservées, b fois le total des blocs nécessaires. Pour les longueurs 37, 120, 5 et 64 et des blocs de 16, elle donne 226/256 ≈ 0,8828, et `main` montre ensuite comment cette utilisation varie quand on passe à des blocs de 1 ou de 128 tokens.

**`utilisation_reservee(longueurs, n_max)`** — Celle-ci calcule le même taux pour l'ancienne méthode, celle de l'hôtelier qui réserve à chaque client la suite la plus grande au cas où : elle reçoit les longueurs et la taille maximale n_max réservée par séquence, et renvoie la somme des tokens divisée par le nombre de séquences multiplié par n_max. Avec une réservation de 512 tokens par séquence, les mêmes quatre longueurs n'occupent que 226/2 048 ≈ 0,1104 de la place, huit fois moins bien que la pagination.

**`octets_kv_par_token(couches, tetes_kv, d_tete, octets)`** — Cette fonction pèse ce qu'un seul token laisse dans la mémoire du serveur : elle reçoit le nombre de couches, de têtes de clés-valeurs, la largeur d'une tête et le nombre d'octets par nombre, et renvoie 2 × couches × têtes × largeur × octets, le facteur 2 comptant la clé et la valeur. Pour 32 couches, 8 têtes de 128 et 2 octets, elle rend 131 072 octets par token, ce qui permet à `main` de calculer combien de sessions tiennent dans 20 Go de cache KV.

**`main()`** — C'est l'ingénieur de performance qui conduit cinq essais : il compare d'abord, à la main, le lot statique et le batching continu sur quatre requêtes et vérifie séjours, latences, utilisations et bornes de Graham, puis simule 400 requêtes avec la graine 72 à λ = 0,02 et λ = 0,12, en contrôlant la loi de Little sur chaque trace et en exigeant qu'à forte charge le continu divise la latence par plus de dix et double au moins le débit. Il mesure ensuite les blocs, les pertes et les utilisations du cache paginé, éprouve l'allocateur jusqu'à la `MemoryError`, et termine par le dimensionnement : 18 sessions réservées contre 127 paginées dans 20 Go, et 3 038 blocs, soit 6,37 Go, économisés par le prompt système partagé.

```python
"""Étape 72 bis — batching statique contre continu (horloge simulée), loi de Little, cache KV paginé."""
import math
import random
import sys
from dataclasses import dataclass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def p95(valeurs: list[float]) -> float:
    """Percentile 95 au rang le plus proche : la valeur de rang ceil(0,95 × N) dans la liste triée."""
    if not valeurs:
        raise ValueError("liste vide")
    s = sorted(valeurs)
    return s[math.ceil(0.95 * len(s)) - 1]


# ---------------------------------------------------------------- ordonnanceurs
@dataclass
class Requete:
    ident: int
    arrivee: float          # en itérations, sur l'horloge simulée
    longueur: int           # tokens à générer : une itération de décodage par token
    fin: float = -1.0


def copier(requetes: list[Requete]) -> list[Requete]:
    return [Requete(r.ident, r.arrivee, r.longueur) for r in requetes]


def simuler_statique(requetes: list[Requete], B: int) -> dict:
    """Lot statique : le serveur prend jusqu'à B requêtes en attente et tourne jusqu'à la fin de la plus longue."""
    file = sorted(copier(requetes), key=lambda r: (r.arrivee, r.ident))
    t, i, cases_occupees = 0, 0, 0
    while i < len(file):
        if file[i].arrivee > t:
            t = math.ceil(file[i].arrivee)          # serveur vide : on avance l'horloge jusqu'à la prochaine arrivée
        lot = []
        while i < len(file) and len(lot) < B and file[i].arrivee <= t:
            lot.append(file[i])
            i += 1
        duree = max(r.longueur for r in lot)
        for r in lot:
            r.fin = t + r.longueur                  # le résultat est prêt, mais la case reste bloquée
        cases_occupees += B * duree                 # B cases réservées pendant toute la durée du lot
        t += duree
    return {"requetes": file, "fin": t, "cases": cases_occupees}


def simuler_continu(requetes: list[Requete], B: int) -> dict:
    """Batching continu : à chaque itération, une case libérée est rendue à la requête suivante de la file."""
    file = sorted(copier(requetes), key=lambda r: (r.arrivee, r.ident))
    t, i, actives, reste, cases_occupees = 0, 0, [], {}, 0
    while i < len(file) or actives:
        while i < len(file) and len(actives) < B and file[i].arrivee <= t:
            actives.append(file[i])
            reste[file[i].ident] = file[i].longueur
            i += 1
        if not actives:
            t = math.ceil(file[i].arrivee)
            continue
        t += 1                                      # une itération : chaque requête active produit un token
        cases_occupees += B
        for r in list(actives):
            reste[r.ident] -= 1
            if reste[r.ident] == 0:
                r.fin = t
                actives.remove(r)
    return {"requetes": file, "fin": t, "cases": cases_occupees}


def mesures(res: dict) -> dict:
    reqs = res["requetes"]
    sejours = [r.fin - r.arrivee for r in reqs]
    tokens = sum(r.longueur for r in reqs)
    return {"fin": res["fin"], "debit": tokens / res["fin"], "latence": sum(sejours) / len(sejours),
            "p95": p95(sejours), "utilisation": tokens / res["cases"], "sejours": sejours}


def nombre_moyen_present(reqs: list[Requete], horizon: float) -> float:
    """L = (1/T) ∫ N(s) ds, calculé par balayage des événements (arrivée +1, départ −1)."""
    evenements = sorted([(r.arrivee, 1) for r in reqs] + [(r.fin, -1) for r in reqs])
    aire, present, precedent = 0.0, 0, 0.0
    for instant, delta in evenements:
        aire += present * (instant - precedent)
        present += delta
        precedent = instant
    return aire / horizon


def generer(n: int, lam: float, graine: int) -> list[Requete]:
    """Arrivées de Poisson (taux lam par itération) ; 80 % d'appels d'outils courts, 20 % de rédactions longues."""
    rng = random.Random(graine)
    t, reqs = 0.0, []
    for k in range(n):
        t += rng.expovariate(lam)
        longueur = rng.randint(10, 60) if rng.random() < 0.8 else rng.randint(200, 600)
        reqs.append(Requete(k, t, longueur))
    return reqs


# ---------------------------------------------------------------- cache KV paginé
class AllocateurPagine:
    """Blocs de taille fixe ; une table de blocs par séquence ; compteur de références pour partager un préfixe."""

    def __init__(self, n_blocs: int, taille_bloc: int):
        self.b = taille_bloc
        self.libres = list(range(n_blocs - 1, -1, -1))      # pile : on sert le bloc 0 en premier
        self.refs = [0] * n_blocs
        self.tables: dict[str, list[int]] = {}
        self.longueurs: dict[str, int] = {}

    def _prendre(self) -> int:
        if not self.libres:
            raise MemoryError("plus de bloc libre : la séquence doit attendre ou être préemptée")
        bloc = self.libres.pop()
        self.refs[bloc] = 1
        return bloc

    def ajouter_tokens(self, seq: str, n: int) -> None:
        table = self.tables.setdefault(seq, [])
        for _ in range(n):
            long = self.longueurs.get(seq, 0)
            if long % self.b == 0:                     # le dernier bloc est plein (ou il n'y en a pas)
                table.append(self._prendre())
            elif self.refs[table[-1]] > 1:             # dernier bloc partagé : copie à l'écriture
                self.refs[table[-1]] -= 1
                table[-1] = self._prendre()
            self.longueurs[seq] = long + 1

    def partager_prefixe(self, source: str, nouvelle: str) -> None:
        """La nouvelle séquence reprend les blocs de la source (références +1), sans copier le cache."""
        self.tables[nouvelle] = list(self.tables[source])
        self.longueurs[nouvelle] = self.longueurs[source]
        for bloc in self.tables[nouvelle]:
            self.refs[bloc] += 1

    def adresse(self, seq: str, position: int) -> tuple[int, int]:
        """Position logique → (bloc physique, décalage) : la traduction d'adresse d'une mémoire virtuelle."""
        return self.tables[seq][position // self.b], position % self.b

    def liberer(self, seq: str) -> None:
        for bloc in self.tables.pop(seq):
            self.refs[bloc] -= 1
            if self.refs[bloc] == 0:
                self.libres.append(bloc)
        del self.longueurs[seq]

    def blocs_utilises(self) -> int:
        return sum(1 for r in self.refs if r > 0)


def blocs_necessaires(n: int, b: int) -> int:
    return math.ceil(n / b)


def gaspillage(n: int, b: int) -> int:
    """b⌈n/b⌉ − n : places réservées mais vides dans le dernier bloc ; toujours ≤ b − 1."""
    return b * blocs_necessaires(n, b) - n


def utilisation_paginee(longueurs: list[int], b: int) -> float:
    return sum(longueurs) / (b * sum(blocs_necessaires(n, b) for n in longueurs))


def utilisation_reservee(longueurs: list[int], n_max: int) -> float:
    return sum(longueurs) / (len(longueurs) * n_max)


def octets_kv_par_token(couches: int, tetes_kv: int, d_tete: int, octets: int) -> int:
    """2 (K et V) × couches × têtes de clés-valeurs × largeur de tête × octets par nombre (étape 34)."""
    return 2 * couches * tetes_kv * d_tete * octets


def main() -> None:
    print("1. Exemple à la main : B = 2 cases, longueurs [2, 8, 3, 3], toutes arrivées à t = 0")
    exemple = [Requete(k, 0.0, n) for k, n in enumerate([2, 8, 3, 3])]
    m_s = mesures(simuler_statique(exemple, B=2))
    m_c = mesures(simuler_continu(exemple, B=2))
    for nom, m in (("statique", m_s), ("continu ", m_c)):
        print(f"  {nom} : fin = {m['fin']} it. ; séjours = {m['sejours']} ; latence moyenne = {m['latence']}"
              f" ; débit = {m['debit']:.4f} token/it. ; utilisation = {m['utilisation']:.4f}")
    assert m_s["fin"] == 11 and m_s["sejours"] == [2, 8, 11, 11] and m_s["latence"] == 8.0
    assert m_c["fin"] == 8 and m_c["sejours"] == [2, 8, 5, 8] and m_c["latence"] == 5.75
    assert abs(m_s["utilisation"] - 16 / 22) < 1e-12 and m_c["utilisation"] == 1.0
    total, plus_long = sum([2, 8, 3, 3]), 8
    assert max(total / 2, plus_long) <= m_c["fin"] <= total / 2 + plus_long     # bornes de Graham

    print("2. Charge d'agent simulée : 400 requêtes, B = 16, 80 % courtes (10-60 tokens), 20 % longues (200-600)")
    resultats = {}
    for lam in (0.02, 0.12):
        reqs = generer(400, lam, graine=72)
        moyenne_l = sum(r.longueur for r in reqs) / len(reqs)
        print(f"  λ = {lam} requête/it. ; longueur moyenne = {moyenne_l:.2f} ; charge λ·E[ℓ]/B = {lam * moyenne_l / 16:.3f}")
        for nom, simul in (("statique", simuler_statique), ("continu ", simuler_continu)):
            res = simul(reqs, 16)
            m = mesures(res)
            print(f"    {nom} : débit = {m['debit']:.3f} token/it. ; latence moyenne = {m['latence']:8.1f} it."
                  f" ; p95 = {m['p95']:8.1f} it. ; utilisation des cases = {m['utilisation']:.3f}")
            L = nombre_moyen_present(res["requetes"], res["fin"])
            lam_obs = len(reqs) / res["fin"]
            assert abs(L - lam_obs * m["latence"]) < 1e-9                      # loi de Little sur la trace
            resultats[(lam, nom.strip())] = m
    assert resultats[(0.12, "continu")]["latence"] < resultats[(0.12, "statique")]["latence"] / 10
    assert resultats[(0.12, "continu")]["debit"] > 2 * resultats[(0.12, "statique")]["debit"]
    print("  loi de Little vérifiée sur chaque trace : L = λ·W à 1e-9 près")

    print("3. Cache KV paginé : blocs de b = 16 tokens, longueurs [37, 120, 5, 64]")
    longueurs, b = [37, 120, 5, 64], 16
    print(f"  blocs = {[blocs_necessaires(n, b) for n in longueurs]} ; gaspillage = {[gaspillage(n, b) for n in longueurs]}"
          f" ; utilisation paginée = {utilisation_paginee(longueurs, b):.4f}")
    print(f"  réservation de n_max = 512 par séquence : utilisation = {utilisation_reservee(longueurs, 512):.4f}")
    assert [gaspillage(n, b) for n in longueurs] == [11, 8, 11, 0] and sum(blocs_necessaires(n, b) for n in longueurs) == 16
    assert abs(utilisation_paginee(longueurs, b) - 226 / 256) < 1e-12
    assert abs(utilisation_reservee(longueurs, 512) - 226 / 2048) < 1e-12
    assert all(gaspillage(n, b) <= b - 1 for n in range(1, 2000))
    assert sum(gaspillage(n, b) for n in range(1, 16 * 100 + 1)) / 1600 == (b - 1) / 2
    for taille in (1, 16, 128):
        print(f"    b = {taille:>3} : entrées de table = {sum(blocs_necessaires(n, taille) for n in longueurs):>3}"
              f" ; utilisation = {utilisation_paginee(longueurs, taille):.4f}")

    print("4. L'allocateur : table de blocs, traduction d'adresse, partage de préfixe")
    alloc = AllocateurPagine(n_blocs=64, taille_bloc=16)
    alloc.ajouter_tokens("A", 37)
    print(f"  séquence A (37 tokens) : table = {alloc.tables['A']} ; position 37 → {alloc.adresse('A', 36)} (bloc, décalage)")
    assert alloc.tables["A"] == [0, 1, 2] and alloc.adresse("A", 36) == (2, 4)
    alloc.partager_prefixe("A", "B")
    alloc.ajouter_tokens("B", 1)                       # B écrit dans le bloc partiel partagé : copie à l'écriture
    print(f"  B partage le préfixe de A puis écrit un token : table B = {alloc.tables['B']} ; références = {alloc.refs[:4]}")
    assert alloc.tables["B"] == [0, 1, 3] and alloc.refs[:4] == [2, 2, 1, 1] and alloc.blocs_utilises() == 4
    for seq in ("A", "B"):
        alloc.liberer(seq)
    assert alloc.blocs_utilises() == 0 and len(alloc.libres) == 64
    try:
        AllocateurPagine(n_blocs=2, taille_bloc=16).ajouter_tokens("C", 33)
    except MemoryError as e:
        print(f"  MemoryError : {e}")
    else:
        raise AssertionError("33 tokens ne tiennent pas dans 2 blocs de 16")

    print("5. Combien de sessions tiennent dans 20 Go de cache KV (32 couches, 8 têtes KV de 128, 2 octets)")
    par_token = octets_kv_par_token(32, 8, 128, 2)
    budget_tokens = 20e9 // par_token
    blocs = int(budget_tokens // 16)
    reservees = int(budget_tokens // 8192)
    paginees = blocs // blocs_necessaires(1200, 16)
    print(f"  {par_token:_} octets par token ; {budget_tokens:_.0f} tokens ; {blocs:_} blocs de 16")
    print(f"  réservation de 8 192 tokens : {reservees} sessions ; pagination, 1 200 tokens réels : {paginees} sessions")
    assert par_token == 131_072 and reservees == 18 and paginees == 127
    prefixe, sessions = 1000, 50
    economie = (sessions - 1) * (prefixe // 16)
    print(f"  prompt système de {prefixe} tokens partagé par {sessions} sessions : {economie:_} blocs économisés"
          f" = {economie * 16 * par_token / 1e9:.2f} Go")
    assert economie == 3_038 and round(economie * 16 * par_token / 1e9, 2) == 6.37

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Exemple à la main : B = 2 cases, longueurs [2, 8, 3, 3], toutes arrivées à t = 0
  statique : fin = 11 it. ; séjours = [2.0, 8.0, 11.0, 11.0] ; latence moyenne = 8.0 ; débit = 1.4545 token/it. ; utilisation = 0.7273
  continu  : fin = 8 it. ; séjours = [2.0, 8.0, 5.0, 8.0] ; latence moyenne = 5.75 ; débit = 2.0000 token/it. ; utilisation = 1.0000
2. Charge d'agent simulée : 400 requêtes, B = 16, 80 % courtes (10-60 tokens), 20 % longues (200-600)
  λ = 0.02 requête/it. ; longueur moyenne = 124.13 ; charge λ·E[ℓ]/B = 0.155
    statique : débit = 2.365 token/it. ; latence moyenne =    341.6 it. ; p95 =    824.0 it. ; utilisation des cases = 0.150
    continu  : débit = 2.421 token/it. ; latence moyenne =    124.6 it. ; p95 =    500.4 it. ; utilisation des cases = 0.167
  λ = 0.12 requête/it. ; longueur moyenne = 124.13 ; charge λ·E[ℓ]/B = 0.931
    statique : débit = 3.849 token/it. ; latence moyenne =   4695.5 it. ; p95 =   8596.4 it. ; utilisation des cases = 0.241
    continu  : débit = 12.820 token/it. ; latence moyenne =    129.1 it. ; p95 =    505.0 it. ; utilisation des cases = 0.801
  loi de Little vérifiée sur chaque trace : L = λ·W à 1e-9 près
3. Cache KV paginé : blocs de b = 16 tokens, longueurs [37, 120, 5, 64]
  blocs = [3, 8, 1, 4] ; gaspillage = [11, 8, 11, 0] ; utilisation paginée = 0.8828
  réservation de n_max = 512 par séquence : utilisation = 0.1104
…
  B partage le préfixe de A puis écrit un token : table B = [0, 1, 3] ; références = [2, 2, 1, 1]
…
  réservation de 8 192 tokens : 18 sessions ; pagination, 1 200 tokens réels : 127 sessions
  prompt système de 1000 tokens partagé par 50 sessions : 3_038 blocs économisés = 6.37 Go
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : l'ordonnanceur d'un serveur de LLM tient en une trentaine de lignes et un allocateur paginé en une quarantaine. Leur effet se mesure avec trois nombres déjà vus dans le parcours : la charge ρ, la loi de Little et le p95.

### Avec un moteur d'inférence (extrait)

Les moteurs d'inférence ouverts implémentent ces deux techniques. Avec vLLM, par exemple, on les règle au lancement ; les noms des paramètres ci-dessous sont ceux de la documentation du projet et doivent être vérifiés pour la version installée.

```python
# [extrait] — moteur vLLM, non exécuté par le harnais (pip install vllm, carte graphique requise)
from vllm import LLM, SamplingParams

llm = LLM(
    model="<modèle ouvert retenu>",
    gpu_memory_utilization=0.90,   # part de la mémoire de la carte donnée aux poids et au cache KV paginé
    max_num_seqs=64,               # B : nombre maximal de séquences décodées ensemble à chaque itération
    block_size=16,                 # b : tokens par bloc du cache KV
    enable_prefix_caching=True,    # partage des blocs d'un préfixe commun (point 7)
)
sorties = llm.generate(["Résume ce contrat de bail Ejari : ..."], SamplingParams(max_tokens=300))
```

`gpu_memory_utilization` fixe le budget : ce qui reste après les poids devient le cache KV, découpé en blocs de `block_size` tokens. `max_num_seqs` est le B de ce fichier : au-delà, les requêtes attendent dans la file. Le moteur fait du batching continu sans réglage particulier. Écrire soi-même la simulation de ce fichier sert à prévoir ce que ces réglages donneront avant d'acheter ou de louer la carte, et à lire les métriques du moteur (séquences en cours, séquences en attente, taux d'occupation du cache) sans dépendre d'un fournisseur.

## Squelette algorithmique

Deux algorithmes. Le premier est l'ordonnanceur à batching continu : en entrée, une file de requêtes avec leur arrivée et leur longueur, et B cases ; en sortie, l'instant de fin de chaque requête. Le second est l'allocateur paginé du cache KV : il ajoute des tokens à une séquence, partage un préfixe et libère une séquence. La variante statique ne diffère que par une ligne : elle n'admet de nouvelles requêtes que lorsque toutes les cases sont vides.

```text
ALGORITHME BatchingContinu
ENTRÉES : file de requêtes (arrivée, longueur ℓ), triée par arrivée ; B cases
SORTIE  : fin(r) pour chaque requête r

  t ← 0 ; actives ← ensemble vide
  TANT QUE la file n'est pas vide OU actives n'est pas vide FAIRE
      TANT QUE |actives| < B ET la première requête r de la file vérifie arrivée(r) ≤ t FAIRE
          retirer r de la file ; reste(r) ← ℓ(r) ; ajouter r à actives
      FIN TANT QUE
      SI actives est vide ALORS
          t ← ⌈arrivée de la première requête de la file⌉ ; CONTINUER
      FIN SI
      t ← t + 1                                    (une itération : un token par requête active)
      POUR CHAQUE r DANS actives FAIRE
          reste(r) ← reste(r) − 1
          SI reste(r) = 0 ALORS fin(r) ← t ; retirer r de actives FIN SI
      FIN POUR
  FIN TANT QUE
  RETOURNER fin

VARIANTE Lot statique : on n'admet de requêtes que si actives est vide, et le lot dure max ℓ.

ALGORITHME AjouterToken(seq)                         (allocateur paginé, blocs de b tokens)
  SI longueur(seq) mod b = 0 ALORS
      SI aucun bloc libre ALORS ERREUR « mémoire pleine : attendre ou préempter » FIN SI
      ajouter un bloc libre à table(seq) ; refs(bloc) ← 1
  SINON SI refs(dernier bloc de seq) > 1 ALORS        (bloc partagé : copie à l'écriture)
      refs(dernier bloc) ← refs(dernier bloc) − 1
      remplacer le dernier bloc par un bloc libre, où l'on recopie son contenu
  FIN SI
  longueur(seq) ← longueur(seq) + 1

ALGORITHME PartagerPréfixe(source, nouvelle)
  table(nouvelle) ← copie de table(source) ; longueur(nouvelle) ← longueur(source)
  POUR CHAQUE bloc DANS table(nouvelle) FAIRE refs(bloc) ← refs(bloc) + 1 FIN POUR

ALGORITHME Libérer(seq)
  POUR CHAQUE bloc DANS table(seq) FAIRE
      refs(bloc) ← refs(bloc) − 1
      SI refs(bloc) = 0 ALORS rendre bloc à la liste des blocs libres FIN SI
  FIN POUR

ADRESSE du token en position p : (table(seq)[p div b], p mod b)
```

**Complexité :** l'ordonnanceur fait, à chaque itération active, O(B) mises à jour, et chaque requête n'est admise et retirée qu'une fois : sur une trace de durée H, le temps est O(H × B + R) et la mémoire O(B + R). La simulation statique traite les lots d'un coup et coûte O(R) une fois la file triée en O(R log R). Dans l'allocateur, ajouter un token, traduire une adresse et prendre un bloc coûtent O(1) ; partager un préfixe et libérer une séquence coûtent O(⌈n / b⌉), le nombre d'entrées de sa table. La mémoire des tables vaut O(∑ ⌈nₛ / b⌉) entiers, négligeable devant le cache lui-même ; c'est le terme que b réduit quand il grandit, au prix d'une perte moyenne de (b − 1)/2 places par séquence.

**Du squelette au code :** BatchingContinu est `simuler_continu` : la boucle d'admission est le `while i < len(file) and len(actives) < B and file[i].arrivee <= t`, le saut d'horloge est `t = math.ceil(file[i].arrivee)`, et la boucle sur les actives décrémente `reste`. La variante statique est `simuler_statique`, dont `duree = max(...)` est la durée du lot. AjouterToken est la boucle de `AllocateurPagine.ajouter_tokens`, avec `_prendre` pour l'erreur « mémoire pleine » levée en `MemoryError` ; PartagerPréfixe est `partager_prefixe`, Libérer est `liberer`, et ADRESSE est `adresse`. La recopie du contenu du bloc partagé n'est pas simulée : le programme ne suit que l'occupation de la mémoire.

## Cas d'usage réels aux Émirats

Les tailles de modèles, les budgets de mémoire, les durées d'itération et les volumes ci-dessous sont illustratifs ; les nombres qui en découlent viennent des formules et sont vérifiés par le programme quand ils y figurent.

### Banque — dix-huit sessions ou cent vingt-sept sur la même carte

Une banque de détail de Dubaï héberge sur ses propres serveurs un modèle ouvert pour l'assistant interne de ses conseillers : questions sur les produits de financement islamique, préparation des dossiers KYC, résumé des échanges avec un client. Le modèle retenu compte 32 couches et 8 têtes de clés-valeurs de largeur 128, soit 131 072 octets de cache par token, et il reste 20 Go de mémoire pour le cache une fois les poids chargés. La première version du serveur réservait à chaque session sa longueur maximale de 8 192 tokens : 18 conseillers simultanés au plus, alors que la plupart des conversations réelles comptent environ 1 200 tokens. Avec un cache paginé en blocs de 16, la même carte loge 127 sessions de cette taille, sept fois plus, et la perte par session reste sous 16 tokens. L'équipe garde une marge, parce que les conversations grandissent : quand la mémoire se remplit, l'ordonnanceur met en attente les nouvelles sessions plutôt que de couper une session en cours. Sans ce calcul, la banque aurait acheté sept fois trop de cartes, ou refusé des conseillers le lundi matin. L'indicateur suivi est le taux d'occupation du cache au pic de charge, avec le nombre de sessions mises en attente.

### Secteur public — un prompt système stocké une fois pour cinquante usagers

Une entité de services publics en ligne accessible par UAE Pass sert un assistant bilingue arabe-anglais dont le prompt système, avec les règles de la démarche et les définitions d'outils, fait 1 000 tokens. Chaque session commence par ces mêmes 1 000 tokens. Avec le partage de préfixe, les 62 blocs pleins de ce prompt ne sont stockés qu'une fois et pointés par toutes les sessions grâce à leurs compteurs de références ; seul le dernier bloc, incomplet, est copié quand une session y écrit. Pour 50 sessions simultanées, l'économie vaut 49 × 62 = 3 038 blocs, soit 6,37 Go de cache, qui servent à loger d'autres usagers. Le partage n'opère que si le préfixe est identique au token près : l'équipe place donc la date du jour et le nom de l'usager **après** le prompt système, et non au début. Sans ce soin, chaque session recalcule et stocke son propre prompt, et le service sature aux heures de pointe, quand les échéances de renouvellement approchent. L'indicateur suivi est la part des tokens de prompt servis depuis un bloc partagé.

### Crypto — garder un p95 bas pendant un pic de marché

Une plateforme d'actifs virtuels agréée par la VARA fait tourner un agent de support qui répond aux clients et prépare les alertes de surveillance. Lors d'un mouvement brusque du marché, les requêtes affluent et la charge monte à ρ ≈ 0,93. La simulation de ce fichier montre ce qui arrive : en batching statique, le p95 des séjours atteint 8 596,4 itérations, soit environ 215 secondes avec une itération de 25 millisecondes, parce que chaque lot attend sa rédaction la plus longue et que la file ne se vide plus ; en batching continu, il reste à 505,0 itérations, environ 12,6 secondes, et la latence moyenne à 129,1 itérations, à peine plus que la longueur moyenne d'une réponse. L'équipe choisit un moteur à batching continu et dimensionne le nombre de cartes pour garder ρ sous 0,8 aux pics observés, parce que l'attente croît comme 1/(1 − ρ) quand on approche de la saturation (étape 70). Elle donne aussi une file prioritaire aux alertes de surveillance, pour qu'aucune réponse commerciale ne les retarde. Sans cela, les clients attendent plusieurs minutes au moment où ils ont le plus besoin d'une réponse, et des alertes arrivent en retard. L'indicateur suivi est le p95 de latence par type de requête pendant les pics.

### RH — des appels d'outils courts coincés derrière un contrat

Un cabinet RH multi-émirats fait tourner un agent qui, pour un même dossier, appelle des outils (vérifier un statut MOHRE, calculer une indemnité de fin de service) avec des réponses de quelques dizaines de tokens, et rédige parfois un contrat de plusieurs centaines de tokens. Sur le serveur d'origine, à lot statique, un appel d'outil arrivé derrière une rédaction de contrat attendait la fin de celle-ci : c'est l'effet de l'exemple à la main, où la troisième requête finit à l'itération 11 au lieu de 5. Comme l'agent enchaîne plusieurs appels d'outils par dossier, chaque attente s'ajoute aux suivantes et le dossier entier ralentit. Le passage au batching continu rend la case d'un appel court dès qu'il a fini, et l'agent termine ses étapes à son rythme. L'équipe mesure séparément la latence des appels d'outils et celle des rédactions, puisque leur moyenne commune masquerait le problème. Sans ce découpage, le cabinet aurait conclu que le modèle était « lent » et aurait payé un modèle plus petit, moins précis sur les contrats. L'indicateur suivi est la latence par étape de l'agent, avec la durée totale de traitement d'un dossier.

### Assurance — la nuit, le lot statique suffit

Un assureur auto et santé traite chaque nuit, en lots, les déclarations de sinistre de la journée : pour chacune, l'agent produit une fiche de synthèse de format fixe, d'environ 300 tokens. Ici, les longueurs de sortie sont presque égales, et la formule de U_stat dit ce qu'on y gagne : si toutes les longueurs d'un lot valent 300, U_stat = 1, et si elles varient entre 280 et 320, l'utilisation reste au moins égale à 280 / 320 = 0,875 dans le pire lot. Le batching continu n'apporterait presque rien, et la latence individuelle ne compte pas puisque personne n'attend la réponse la nuit. L'équipe garde donc un traitement par lots simple, et elle passe par l'offre de traitement différé de son fournisseur quand elle utilise une API, généralement moins chère que l'appel interactif, à vérifier sur sa grille. Elle surveille en revanche la longueur des fiches : si un nouveau type de sinistre produit des sorties de 1 500 tokens, les lots statiques recommencent à attendre la plus longue. L'indicateur suivi est l'heure de fin du traitement nocturne, avec la distribution des longueurs de sortie.

### Immobilier — quatre variantes d'annonce à partir du même dossier

Une agence et un promoteur à Dubaï et Abu Dhabi font rédiger par un agent quatre variantes d'annonce pour chaque bien (arabe, anglais, version courte pour les portails, version longue pour les investisseurs), à partir du même dossier de 3 000 tokens : fiche du bien, prix en AED et en AED/sqft, rappel des frais de transfert DLD de 4 %, conditions Ejari. Les quatre générations partent du même préfixe. Avec le partage de blocs, les ⌊3 000 / 16⌋ = 187 blocs pleins du dossier sont stockés une fois au lieu de quatre, ce qui économise 3 × 187 × 16 × 131 072 octets, soit environ 1,18 Go par bien en cours de rédaction. Les quatre variantes avancent ensuite dans le même lot, en batching continu, et la version courte libère sa case bien avant la longue. Les chiffres de prix et de frais viennent toujours d'un outil, pas du texte généré, et un contrôle compare chaque annonce au dossier avant publication. Sans le partage, l'agence aurait dû limiter le nombre de biens rédigés en parallèle à cause du cache. L'indicateur suivi est le nombre de biens traités par heure, avec le taux d'annonces corrigées avant publication.

## Pièges et limites

- **Juger un serveur sur son débit à faible charge.** Tant que ρ est petit, le débit est imposé par les arrivées ; c'est la latence, et surtout le p95, qui révèle le lot statique.
- **Dimensionner à ρ proche de 1.** L'attente explose avant la saturation ; on garde une marge et l'on mesure le p95 aux pics réels.
- **Oublier que la pagination admet sur la taille actuelle.** Une séquence qui grandit peut manquer de blocs ; l'ordonnanceur doit savoir mettre en attente ou préempter.
- **Casser le partage de préfixe.** Un horodatage ou un identifiant placé en tête du prompt rend chaque préfixe unique ; les éléments variables vont après la partie commune.
- **Compter la mémoire des poids et oublier celle du cache.** Le cache KV croît avec le nombre de sessions et la longueur de chaque contexte ; c'est souvent lui qui borne le service.

### Exercice feuille blanche

1. Sans regarder le code, écrire `simuler_continu`, puis retrouver les séjours [2, 8, 5, 8] pour B = 2 et les longueurs [2, 8, 3, 3].
2. Prédire, puis vérifier : avec B = 3 et les mêmes longueurs, quand finit chaque requête en batching continu, et en lot statique ? (Réponse : en continu, les trois premières finissent à 2, 8 et 3, et la quatrième entre à 2 et finit à 5, soit une fin totale à 8 ; en statique, le premier lot finit à 8 et la quatrième requête finit à 11.)
3. Trouver le bug : dans `ajouter_tokens`, la condition `if long % self.b == 0` est remplacée par `if long % self.b == 1`. Combien de blocs reçoit une séquence de 37 tokens, et qu'arrive-t-il au premier token ? (Réponse : le premier token, pour `long = 0`, ne déclenche aucune allocation, et `table[-1]` lève une `IndexError` dans la branche de copie à l'écriture ; il faut toujours allouer un bloc quand la séquence n'en a pas, ou quand le dernier est plein.)

## Pour aller plus loin

Le préremplissage (*prefill*) d'un long prompt occupe la carte plusieurs itérations et retarde les décodages en cours ; le **préremplissage par morceaux** (*chunked prefill*) le découpe et l'intercale avec les décodages. Le **désagrégage** sépare préremplissage et décodage sur des cartes différentes, parce que l'un est limité par le calcul et l'autre par la mémoire. Les techniques de l'étape 72 ter (décodage spéculatif) et de l'étape 73 bis (quantification) augmentent le nombre de tokens produits par itération ou réduisent la mémoire lue à chaque itération. L'article d'origine de PagedAttention (Kwon et al., 2023) et celui d'Orca (Yu et al., 2022), qui a introduit l'ordonnancement à l'itération, détaillent les mesures sur de vrais modèles.

> Étape 72 bis du parcours · Prérequis : [Coûts et gestion des tokens](<72-Couts-et-Gestion-des-Tokens.md>) · Suite : [Décodage spéculatif](<72c-Decodage-Speculatif.md>)
