# Étape 68 — Notation de Kendall — Langage Universel des Files d'Attente

> Étape 68 du parcours · Prérequis : [Sandbox d'exécution](<../11-GardeFous/67b-Sandbox-d-Execution.md>) · Suite : [Files d'attente et loi de Little](<69-Files-Attente-et-Goulot.md>)

**Dossier :** 12-Production-Couts-Optimisation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, AI Platform Team, Forward-Deployed Engineers  
**Nom du fichier :** 68-Notation-de-Kendall.md

## Définition

La notation de Kendall décrit une file d'attente en six cases, A/S/c/K/N/D. Elle a été proposée par David G. Kendall en 1953 avec trois cases, puis étendue à six. Les cases donnent, dans l'ordre : la loi des temps entre deux arrivées, la loi des durées de service, le nombre de serveurs, la capacité totale du système (places en service comprises), la taille de la population qui peut appeler, et la discipline de service (qui l'on sert en premier). Quand on n'écrit que trois cases, les trois dernières valent ∞, ∞ et FIFO : M/M/1 se lit M/M/1/∞/∞/FIFO. La notation n'est pas une formule. C'est une clé qui dit quelles formules ont le droit de s'appliquer à un système, et lesquelles n'existent pas.

| Case | Signification | Valeurs courantes |
|---|---|---|
| A | loi des temps entre deux arrivées | M, D, Eₖ, G (ou GI) |
| S | loi des durées de service | M, D, Eₖ, G |
| c | nombre de serveurs identiques | 1, 2, …, ∞ |
| K | capacité totale (file + service) | entier ≥ c, ou ∞ |
| N | taille de la population appelante | entier, ou ∞ |
| D | discipline de service | FIFO, LIFO, SIRO, PR, PS, RR |

Les lettres des deux premières cases se lisent ainsi :

- **M** (Markov) : durées exponentielles, donc sans mémoire. Pour les arrivées, cela veut dire un processus de Poisson : beaucoup de clients indépendants qui arrivent quand ils veulent.
- **D** (déterministe) : durée constante. Une arrivée toutes les 200 ms, pile, ou un service qui dure toujours 0,25 s.
- **Eₖ** (Erlang d'ordre k) : somme de k exponentielles de même moyenne. Plus k est grand, plus la durée est régulière.
- **G** (générale) : on ne suppose rien d'autre qu'une moyenne et une variance finies. GI précise que les temps entre arrivées sont indépendants.

Pour la discipline : FIFO sert le plus ancien, LIFO le plus récent, SIRO au hasard, PR (priorité) fait passer une classe devant les autres, PS (partage du processeur) fait avancer toutes les requêtes présentes en même temps, RR (tourniquet) les sert à tour de rôle par tranches.

## Rôle dans un agent

Dans la boucle percevoir → décider → agir → observer, chaque « agir » est un service rendu dans une file partagée avec les autres utilisateurs : un appel au LLM, un appel d'outil, une requête à un serveur MCP. Avant de calculer un temps d'attente, l'équipe qui exploite l'agent doit écrire la notation de chaque file, parce que c'est elle qui choisit la formule. Les arrivées des utilisateurs d'une application sont proches de M, celles d'une tâche planifiée (cron) sont D, celles d'alertes en rafales sont G. La durée d'un appel au LLM dépend du nombre de tokens générés : elle n'est presque jamais exponentielle, c'est une loi G, souvent à longue traîne. Le nombre c est le nombre de répliques que lance l'**ordonnanceur** ou l'autoscaler, K est la taille du tampon que fixe le **garde-fou de débit** (rate limiter), N est le nombre d'appelants quand ce sont d'autres agents internes, et D est la règle du **routeur** (FIFO, ou priorité pour une alerte). Une erreur de lettre donne une formule fausse, donc un SLA promis qu'on ne tiendra pas.

## Équation complète

La notation :

$$
A \,/\, S \,/\, c \,/\, K \,/\, N \,/\, D
$$

L'utilisation, c'est-à-dire la fraction de la capacité occupée :

$$
\rho = \frac{\lambda}{c\,\mu} = \frac{\lambda\, E[S]}{c}
$$

La loi de Little, valable pour toute file stable, quelles que soient les lettres (démontrée à l'étape 69) :

$$
L = \lambda\, W
$$

La formule de Pollaczek-Khinchine, pour une file M/G/1 (arrivées de Poisson, un serveur, service quelconque, FIFO) avec ρ = λE[S] < 1 :

$$
W_q = \frac{\lambda\, E[S^2]}{2\,(1-\rho)}
$$

La même formule écrite avec le coefficient de variation du service :

$$
W_q = \frac{1 + C_s^2}{2} \cdot \frac{\rho}{1-\rho} \cdot E[S]
\qquad \text{avec} \qquad
C_s^2 = \frac{\operatorname{Var}(S)}{E[S]^2}
$$

Ses deux cas particuliers les plus utiles :

$$
W_q^{M/M/1} = \frac{\rho}{1-\rho}\, E[S]
\qquad\qquad
W_q^{M/D/1} = \frac{1}{2} \cdot \frac{\rho}{1-\rho}\, E[S]
$$

Pour une file G/G/1, il n'existe pas de formule fermée. On dispose de l'approximation de Kingman :

$$
W_q \approx \frac{C_a^2 + C_s^2}{2} \cdot \frac{\rho}{1-\rho} \cdot E[S]
$$

et de la récurrence de Lindley, exacte pour chaque requête d'une file FIFO à un serveur, quelles que soient les lois :

$$
W_{q,n+1} = \max\left(0,\; W_{q,n} + S_n - A_{n+1}\right)
$$

## Décryptage des symboles

$$
A
$$

Loi des temps entre deux arrivées successives (M, D, Eₖ, G) · variable Python : champ `Kendall.A`.

$$
S
$$

Dans la notation, loi des durées de service ; dans les formules, la durée de service elle-même, une variable aléatoire en secondes · variable Python : champ `Kendall.S`, et la liste `services` dans la simulation.

$$
c
$$

Nombre de serveurs identiques (instances de l'agent, répliques du modèle), entier ≥ 1 ou ∞ · variable Python : champ `Kendall.c`.

$$
K
$$

Capacité totale du système, places en service comprises : une requête qui arrive quand K requêtes sont déjà présentes est refusée · entier ≥ c ou ∞ · variable Python : champ `Kendall.K`.

$$
N
$$

Taille de la population qui peut envoyer des requêtes ; finie, elle fait baisser le taux d'arrivée quand beaucoup d'appelants attendent déjà · variable Python : champ `Kendall.N`.

$$
D
$$

Discipline de service (FIFO par défaut) · variable Python : champ `Kendall.D`. Ce D n'a rien à voir avec la lettre D « déterministe » des deux premières cases : c'est la même lettre, à une autre place.

$$
\lambda
$$

Taux d'arrivée moyen, en requêtes par seconde, réel > 0. Dans les fichiers de files d'attente, λ désigne toujours ce taux (et non un taux de décroissance comme à l'étape 16) · variable Python : `lam`.

$$
\mu
$$

Taux de service d'un serveur, en requêtes par seconde, égal à 1/E[S] · variable Python : `1 / es`.

$$
E[S]
$$

Durée moyenne d'un service, en secondes, réel > 0 · variable Python : `es`.

$$
E[S^2]
$$

Moment d'ordre 2 de la durée de service, en secondes au carré : la moyenne des carrés des durées. Il vaut Var(S) + E[S]², donc il est toujours ≥ E[S]² · variable Python : `es2`.

$$
\rho
$$

Utilisation : fraction du temps où un serveur est occupé ; une file n'a de régime stable que si ρ < 1 · variable Python : `rho`.

$$
C_s^2
$$

Carré du coefficient de variation du service, sans unité, ≥ 0 : 0 pour un service constant, 1 pour un service exponentiel, plus de 1 pour une loi à longue traîne · variable Python : `cs2`.

$$
C_a^2
$$

Même grandeur pour les temps entre arrivées : 1 pour des arrivées de Poisson, 0 pour une cron régulière, plus de 1 pour des rafales · variable Python : `ca2`.

$$
W_q
$$

Temps moyen d'attente dans la file, avant le début du service, en secondes · variable Python : valeur renvoyée par `wq_pollaczek_khinchine` et `simuler_lindley`.

$$
W
$$

Temps moyen de séjour dans le système, attente plus service : W = Wq + E[S] · variable Python : `wq[nom] + es`.

$$
L
$$

Nombre moyen de requêtes présentes dans le système, en attente ou en service · pas de variable dans le code de cette étape (voir l'étape 69).

$$
W_{q,n}
$$

Attente de la n-ième requête dans la récurrence de Lindley · variable Python : `w` dans la boucle de `simuler_lindley`.

$$
A_{n+1}
$$

Temps écoulé entre l'arrivée de la requête n et celle de la requête n + 1 · variable Python : `inter_arrivees[n]`.

## Démonstration

### 1. Les cases absentes et ce qu'elles cachent

Écrire M/M/1 au lieu de M/M/1/∞/∞/FIFO n'est pas un détail d'écriture. K = ∞ veut dire qu'aucune requête n'est jamais refusée : toute la surcharge se transforme en attente. N = ∞ veut dire que les arrivées ne se tarissent pas parce que tous les appelants sont déjà dans la file. FIFO veut dire que tout le monde attend dans le même ordre. Dès qu'un rate limiter refuse au-delà de K requêtes, une partie de la surcharge n'apparaît plus dans W mais dans une probabilité de refus, qui vaut 0 dans tous les fichiers où K est infini. Dès que les appelants sont 20 tâches planifiées, N vaut 20 et λ baisse quand beaucoup d'entre elles attendent déjà.

### 2. Une file n'est stable que si ρ < 1

Chaque seconde, il arrive en moyenne λ requêtes, et chacune apporte E[S] secondes de travail : le système reçoit donc λE[S] secondes de travail par seconde. Les c serveurs en abattent au plus c par seconde. Si λE[S] > c, c'est-à-dire ρ > 1, le travail en retard grossit d'environ (λE[S] − c) secondes à chaque seconde, parce que ce qui entre dépasse ce qui peut sortir : la file croît sans limite. À ρ = 1 exactement, il n'y a plus de dérive, mais les écarts aléatoires ne se rattrapent jamais et l'attente moyenne est infinie. Toutes les formules qui suivent supposent donc ρ < 1, et le code lève `ValueError` sinon.

### 3. La formule de Pollaczek-Khinchine (M/G/1)

On suit une requête qui arrive dans une file FIFO à un serveur. Son attente est la somme de deux morceaux : les services complets de toutes les requêtes déjà en file devant elle, et le reste du service de la requête en cours, s'il y en a une.

**Étape a — ce que voit une arrivée.** Les arrivées sont poissoniennes. Une propriété des processus de Poisson, appelée PASTA (Poisson Arrivals See Time Averages, Wolff, 1982), dit qu'une arrivée de Poisson voit le système dans son état moyen dans le temps. On l'admet ici ; l'intuition est que des arrivées sans mémoire ne peuvent pas « choisir » leur moment. La requête trouve donc en moyenne Lq requêtes en file, et le serveur occupé avec probabilité ρ.

**Étape b — le reste du service en cours, par un argument d'aire.** Notons r(t) le temps qu'il reste au service en cours à l'instant t, et 0 si le serveur est libre. Pendant un service de durée Sᵢ, r(t) descend en ligne droite de Sᵢ à 0 : sa courbe est un triangle d'aire Sᵢ²/2. Sur une longue durée T, il y a environ λT services, donc la moyenne de r dans le temps vaut

$$
\bar r = \frac{1}{T} \sum_{i=1}^{\lambda T} \frac{S_i^2}{2} \;\longrightarrow\; \frac{\lambda\, E[S^2]}{2}
$$

parce que la moyenne des Sᵢ² tend vers E[S²]. Par PASTA, c'est aussi le reste moyen que trouve une arrivée.

**Étape c — l'équation.** Chacune des requêtes en file devant elle demande en moyenne E[S] (les durées sont indépendantes du nombre de requêtes présentes). Donc

$$
W_q = L_q\, E[S] + \frac{\lambda\, E[S^2]}{2}
$$

**Étape d — Little sur la file seule.** La loi de Little, appliquée à la seule file d'attente (sans le serveur), donne Lq = λ Wq. On remplace :

$$
W_q = \lambda\, W_q\, E[S] + \frac{\lambda\, E[S^2]}{2}
\;\Longleftrightarrow\;
W_q\,(1 - \rho) = \frac{\lambda\, E[S^2]}{2}
\;\Longleftrightarrow\;
W_q = \frac{\lambda\, E[S^2]}{2\,(1-\rho)}
$$

On passe à la deuxième égalité en regroupant les termes en Wq et en posant ρ = λE[S] ; on divise ensuite par 1 − ρ, qui est strictement positif parce que ρ < 1.

### 4. Les cas particuliers, et pourquoi M/D/1 attend deux fois moins

On écrit E[S²] = Var(S) + E[S]² = (1 + Cₛ²) E[S]², par définition de Cₛ². En remplaçant, et parce que λE[S] = ρ :

$$
W_q = \frac{\lambda\,(1 + C_s^2)\,E[S]^2}{2\,(1-\rho)} = \frac{1 + C_s^2}{2} \cdot \frac{\rho}{1-\rho} \cdot E[S]
$$

- **Service exponentiel** : Var(S) = E[S]², donc Cₛ² = 1 et le facteur (1 + Cₛ²)/2 vaut 1. On retrouve Wq = ρ/(μ − λ), la formule M/M/1 que l'étape 70 démontre d'une autre façon, par les équations d'équilibre.
- **Service constant** : Var(S) = 0, donc Cₛ² = 0 et le facteur vaut 1/2. À même λ et même μ, M/D/1 attend exactement deux fois moins que M/M/1.
- **Service à longue traîne** : Cₛ² > 1, le facteur dépasse 1 et M/M/1 **sous-estime** l'attente.

L'intuition est le paradoxe de l'inspection : une arrivée tombe plus souvent pendant un service long que pendant un service court, parce qu'un service long occupe plus de temps. Plus les durées sont dispersées, plus le reste qu'elle trouve est grand. Rendre le temps de génération régulier, par exemple en bornant le nombre de tokens de sortie, ne change pas μ : cela réduit Cₛ², et l'attente avec lui.

Attention : c'est l'attente **en file** Wq qui est divisée par deux, pas le séjour W = Wq + E[S]. L'ancienne version de ce fichier disait que les formules M/M/1 « surestiment l'attente d'un facteur deux » quand le service est presque constant : c'est vrai pour Wq, mais pour W le facteur n'est que 1/0,625 = 1,6 dans l'exemple ci-dessous.

### 5. Pourquoi G/G/1 n'a pas de formule fermée

L'étape a utilise PASTA, qui n'est vraie que pour des arrivées de Poisson. Si les arrivées ne sont pas poissoniennes, une arrivée ne voit plus l'état moyen et toute la dérivation tombe. **Contre-exemple chiffré** : une cron envoie une requête toutes les 1/3 s, et chaque service dure exactement 0,25 s (file D/D/1, ρ = 0,75). Chaque requête trouve le serveur libre, puisqu'il a fini depuis 0,083 s : l'attente vaut exactement 0. Appliquer Pollaczek-Khinchine à tort donnerait 0,375 s. La récurrence de Lindley, elle, reste exacte : la requête n + 1 arrive Aₙ₊₁ secondes après la requête n, qui libère le serveur Wq,ₙ + Sₙ secondes après son arrivée, donc la nouvelle attente est l'écart s'il est positif, et 0 sinon. Mais la moyenne de long terme de cette récurrence dépend de toute la loi de Sₙ − Aₙ₊₁, pas seulement de deux moments : il n'existe pas de formule générale. L'approximation de Kingman la remplace ; elle redonne exactement Pollaczek-Khinchine quand Cₐ² = 1, et elle devient exacte quand ρ tend vers 1.

L'ancienne version de ce fichier disait qu'avec un service G « les formules fermées disparaissent ». C'est faux pour M/G/1 : l'attente moyenne y a la forme fermée ci-dessus. Ce qui disparaît en M/G/1, c'est la loi géométrique du nombre de clients et la loi exponentielle du temps d'attente, propres à M/M/1. Les formules fermées pour la moyenne disparaissent seulement quand les **arrivées** ne sont plus poissoniennes.

### 6. Exemple fait à la main (le code reprend ces nombres)

On prend λ = 3 requêtes par seconde et E[S] = 0,25 s, donc ρ = 0,75 et ρ/(1 − ρ) = 3.

| Loi du service | E[S²] | Cₛ² | Wq | W = Wq + 0,25 |
|---|---|---|---|---|
| M, exponentielle | 2 × 0,25² = 0,125 | 1 | 3 × 0,125 / 0,5 = 0,75 s | 1,00 s |
| D, constante | 0,25² = 0,0625 | 0 | 3 × 0,0625 / 0,5 = 0,375 s | 0,625 s |
| G, 90 % à 0,1 s et 10 % à 1,6 s | 0,9 × 0,01 + 0,1 × 2,56 = 0,265 | 3,24 | 3 × 0,265 / 0,5 = 1,59 s | 1,84 s |

La loi G a la même moyenne que les deux autres (0,9 × 0,1 + 0,1 × 1,6 = 0,25 s). Elle représente un agent qui répond vite neuf fois sur dix, et produit une longue explication la dixième fois. Son attente est plus de deux fois celle que promettait le modèle M/M/1.

## Effets et comportement

- **La variabilité coûte, à moyenne égale.** Wq est proportionnel à 1 + Cₛ². Passer d'un service exponentiel (Cₛ² = 1) à un service constant divise l'attente par deux ; une longue traîne (Cₛ² = 3,24) la multiplie par 2,12.
- **La charge coûte toujours, quelle que soit la loi.** Le facteur ρ/(1 − ρ) est commun à toutes les formules : il vaut 1 à ρ = 0,5, 3 à ρ = 0,75, 9 à ρ = 0,9 et 19 à ρ = 0,95.
- **Little ne dépend d'aucune lettre.** L = λW vaut pour M/M/1 comme pour G/G/c, pour FIFO comme pour une priorité. C'est la seule relation qu'on garde quand toutes les autres tombent, et on mesure alors W.
- **La discipline change surtout qui attend.** FIFO, LIFO non préemptif et service au hasard donnent la même attente moyenne, parce qu'aucun ne regarde la durée des requêtes. Une priorité peut laisser la moyenne presque inchangée pendant qu'une classe attend dix fois plus. En PS, le séjour moyen d'une M/G/1 vaut E[S]/(1 − ρ) quelle que soit la loi du service.
- **Un K fini transforme l'attente en refus.** Un rate limiter fait baisser W en apparence ; il faut suivre la probabilité de refus à côté.
- **Un N fini s'autorégule.** Quand beaucoup d'appelants attendent, il en reste moins pour arriver, et la file reste bornée par N.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| A, S, c, K, N, D | champs de la dataclass `Kendall` |
| λ | `lam` |
| E[S] | `es` |
| E[S²] | `es2` |
| ρ = λE[S] | `rho` |
| Cₛ², Cₐ² | `cs2`, `ca2` |
| Wq de Pollaczek-Khinchine | `wq_pollaczek_khinchine(lam, es, es2)` |
| Wq de Kingman | `wq_kingman(rho, ca2, cs2, es)` |
| récurrence de Lindley | `simuler_lindley(inter_arrivees, services)` |

### Déroulé, ligne par ligne

**`lire_loi(x)`** accepte M, D, G, GI, ou E suivi d'un entier ≥ 1 (`"E3"`). Toute autre lettre lève `ValueError` : `"X"` est refusé.

**`lire_nombre(x)`** renvoie `math.inf` pour `"∞"` ou `"inf"`, et un entier ≥ 1 sinon. `"0"` est refusé : une file sans serveur n'a pas de sens.

**`analyser(notation)`**, la fonction qui lit la notation.

- `cases = notation.replace(" ", "").split("/")` : pour `"M/M/1"`, on obtient `["M", "M", "1"]`.
- `cases += ["∞", "∞", "FIFO"][len(cases) - 3:]` : avec 3 cases, `len(cases) - 3` vaut 0 et l'on ajoute les trois valeurs par défaut ; avec 4 cases (`"M/M/4/10"`), on n'ajoute que `["∞", "FIFO"]`. C'est la règle « les cases absentes valent ∞, ∞, FIFO », écrite en une ligne.
- `if k.K < k.c` : K compte les places en service, donc `"M/M/4/2"` (4 serveurs mais 2 places) est refusé.
- `if k.D not in DISCIPLINES` : `"VIP"` n'est pas une discipline.

**`formules(k)`** renvoie la liste des résultats utilisables, toujours en commençant par `"little"`.

- `ouvert = k.K == math.inf and k.N == math.inf` : les formules fermées M/M/1, Erlang C et Pollaczek-Khinchine supposent qu'aucune requête n'est refusée et que la population est infinie.
- Si les arrivées sont M, la file ouverte et la discipline FIFO, LIFO ou SIRO : un service M donne `"mm1"` (un serveur) ou `"erlang_c"` (plusieurs) ; un seul serveur donne en plus `"pollaczek_khinchine"`, valable pour toute loi de service. Pour M/M/1, les deux s'appliquent et donnent le même nombre (démonstration, point 4).
- `if k.A != "M"` : sans arrivées de Poisson, il n'y a pas de forme fermée, d'où `"kingman_lindley"`. G/G/1 n'obtient donc jamais `"pollaczek_khinchine"`.

**`wq_pollaczek_khinchine(lam, es, es2)`**.

- `rho = lam * es` : avec `lam = 3.0` et `es = 0.25`, `rho` vaut 0,75.
- `es2 < es * es` est refusé : un moment d'ordre 2 inférieur au carré de la moyenne voudrait dire une variance négative.
- `return lam * es2 / (2 * (1 - rho))` : pour le service exponentiel, `es2 = 2 * 0.25 * 0.25 = 0.125`, et le résultat vaut 3 × 0,125 / 0,5 = 0,75 s.

**`wq_kingman(rho, ca2, cs2, es)`** applique l'approximation. Avec `ca2 = 1.0`, elle redonne exactement Pollaczek-Khinchine : le `main()` le vérifie pour les trois lois.

**`simuler_lindley(inter_arrivees, services)`**.

- `w = max(0.0, w + services[n - 1] - inter_arrivees[n])` : c'est la récurrence. Si la requête précédente libère le serveur après l'arrivée de la suivante, l'écart est une attente ; sinon l'attente vaut 0.
- La première requête trouve le système vide : son attente vaut 0 et n'est pas ajoutée. On divise par `len(services)` pour obtenir la moyenne sur toutes les requêtes.

**`main()`**, bloc par bloc.

1. Neuf notations sont lues, puis cinq notations fausses doivent lever `ValueError`. Les `assert` vérifient les cases par défaut de M/M/1 et les formules attendues.
2. Les trois lois du tableau de la démonstration : E[S²] vaut 0,125, 0,0625 et 0,265 ; Wq vaut 0,75, 0,375 et 1,59 s. Le rapport M/D/1 sur M/M/1 vaut 0,50 pour Wq et 0,625 pour W.
3. La simulation tire 200 000 temps entre arrivées avec `random.Random(68)`, une graine fixe : deux exécutions donnent les mêmes nombres. Les trois services sont simulés **avec les mêmes arrivées**, ce qui rend leur comparaison bien plus précise que trois tirages séparés. La tolérance est de 5 % pour M et D, et de 12 % pour la loi à longue traîne, dont la moyenne converge plus lentement : sur douze graines essayées, son écart est allé jusqu'à 9 %. Le rapport simulé M/D/1 sur M/M/1 vaut 0,512, contre 0,5 en théorie.
4. Des arrivées toutes les 1/3 s avec un service de 0,25 s donnent une attente simulée de exactement 0, alors que Pollaczek-Khinchine appliquée à tort annonce 0,375 s. Kingman avec Cₐ² = Cₛ² = 0 donne bien 0.
5. À λ = 4 et E[S] = 0,25, ρ = 1 : la fonction refuse le calcul.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`lire_loi(x)`** — Cette fonction est le contrôleur qui vérifie la première ou la deuxième case d'une notation, comme un guichetier qui ne reconnaît qu'une poignée de tampons officiels : elle reçoit une lettre et la renvoie telle quelle si c'est M, D, G ou GI, ou bien un E suivi d'un entier au moins égal à 1, comme « E3 » pour une loi d'Erlang à trois phases. Toute autre écriture lève une `ValueError` « loi inconnue », et c'est ainsi que `analyser` refuse la notation « X/M/1 » dans la première section de `main`.

**`lire_nombre(x)`** — Celle-ci lit les cases numériques c, K et N, comme un huissier qui compte les chaises d'une salle d'attente : elle reçoit une chaîne, renvoie `math.inf` si l'on a écrit « ∞ » ou « inf », renvoie l'entier correspondant s'il s'agit de chiffres valant au moins 1, et lève une `ValueError` « nombre invalide » dans tous les autres cas. Elle refuse en particulier « 0 », car une file sans aucun serveur n'a pas de sens, ce qui fait échouer la notation « M/M/0 » testée par `main`.

**`analyser(notation)`** — C'est le lecteur principal de la notation de Kendall, un archiviste qui complète une fiche incomplète avant de la classer : il reçoit une chaîne comme « M/M/4/10 », retire les espaces, la découpe sur les barres obliques, refuse par une `ValueError` moins de 3 ou plus de 6 cases, puis ajoute les valeurs par défaut ∞, ∞ et FIFO aux cases manquantes. Il fait ensuite lire les deux lois par `lire_loi` et les trois nombres par `lire_nombre`, met la discipline en majuscules, refuse une capacité K inférieure au nombre de serveurs c et une discipline absente de `DISCIPLINES`, et renvoie une instance de `Kendall` ; pour « M/M/1 », ses six cases valent M, M, 1, ∞, ∞ et FIFO.

**`formules(k)`** — Cette fonction est l'aiguilleur qui, devant une file décrite par ses six cases, dit quelles voies de calcul lui sont ouvertes : elle reçoit un objet `Kendall`, commence toujours sa liste par « little », valable pour toute file stable, ajoute « sans_attente » si les serveurs sont en nombre infini, et, pour des arrivées de Poisson, une file ouverte et une discipline FIFO, LIFO ou SIRO, ajoute « mm1 » ou « erlang_c » quand le service est exponentiel et « pollaczek_khinchine » dès qu'il n'y a qu'un serveur. Elle ajoute enfin « blocage » si K est fini, « population_finie » si N l'est, « kingman_lindley » pour des arrivées qui ne sont pas M, et « par_classe » pour une priorité, puis renvoie la liste ; M/M/1 obtient ainsi little, mm1 et pollaczek_khinchine, et G/G/1 little et kingman_lindley.

**`wq_pollaczek_khinchine(lam, es, es2)`** — Cette fonction est le calculateur exact du guichet unique alimenté par des arrivées de Poisson : elle reçoit le débit λ, la durée moyenne de service E[S] et le moment d'ordre deux E[S²], calcule la charge ρ = λE[S], refuse par une `ValueError` un débit ou une durée non positifs, un E[S²] inférieur à E[S]² qui supposerait une variance négative, puis une charge au moins égale à 1, qui n'a pas de régime stable. Elle renvoie sinon l'attente moyenne en file λE[S²] / (2(1 − ρ)) : à λ = 3 et E[S] = 0,25, cela donne 0,75 s pour un service exponentiel, 0,375 s pour un service constant et 1,59 s pour la loi à longue traîne.

**`wq_kingman(rho, ca2, cs2, es)`** — Celle-ci est l'estimatrice pragmatique des files sans formule fermée, qui chiffre l'attente à partir de trois ingrédients seulement : elle reçoit la charge ρ, les carrés des coefficients de variation des arrivées et du service, Cₐ² et Cₛ², et la durée moyenne E[S], et renvoie ρ/(1 − ρ) × (Cₐ² + Cₛ²)/2 × E[S], sans aucun contrôle de domaine. Avec Cₐ² = 1, elle redonne exactement Pollaczek-Khinchine, ce que `main` vérifie pour les trois lois, et avec Cₐ² = Cₛ² = 0 elle annonce bien une attente nulle pour les arrivées régulières de la section 4.

**`simuler_lindley(inter_arrivees, services)`** — Cette fonction rejoue la vie d'un guichet unique, client après client, comme un chronométreur qui note l'attente de chacun : elle reçoit la liste des temps entre arrivées et celle des durées de service, part d'une attente nulle pour le premier client, qui trouve le guichet vide, puis applique la récurrence de Lindley, où chaque attente vaut l'attente précédente augmentée du service précédent et diminuée du temps écoulé depuis l'arrivée précédente, ramenée à 0 si elle devient négative. Elle cumule ces attentes et renvoie leur moyenne sur toutes les requêtes ; sur 200 000 arrivées, elle trouve par exemple 0,726 s pour le service exponentiel, contre 0,75 s annoncé par la formule, et exactement 0 pour des arrivées régulières toutes les 1/3 s.

**`main()`** — C'est le chef de travaux pratiques qui enchaîne cinq démonstrations : il lit neuf notations et affiche leurs formules applicables, puis vérifie que cinq notations fausses, de « M/M » à « M/M/1/∞/∞/VIP », sont refusées ; il calcule ensuite, à λ = 3 req/s et E[S] = 0,25 s, l'attente de Pollaczek-Khinchine pour les trois lois et le rapport 0,50 entre M/D/1 et M/M/1. Il simule après cela 200 000 requêtes avec la graine 68, les mêmes arrivées servant aux trois services, et accepte des écarts de 5 % pour M et D et de 12 % pour la longue traîne, puis montre qu'avec des arrivées régulières l'attente simulée vaut 0 alors que la formule appliquée à tort annonce 0,375 s, et termine en vérifiant qu'une charge ρ = 1 est refusée.

```python
"""Étape 68 — notation de Kendall : lire A/S/c/K/N/D, savoir quelles formules s'appliquent, vérifier M/D/1 contre M/M/1."""
import math
import random
import sys
from dataclasses import dataclass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DISCIPLINES = {"FIFO", "LIFO", "SIRO", "PR", "PS", "RR"}
DESCRIPTIONS = {
    "little": "Little L = λW (toutes les files stables)",
    "mm1": "M/M/1 fermée : W = 1/(μ−λ) (étape 70)",
    "erlang_c": "M/M/c fermée : Erlang C (étape 71)",
    "pollaczek_khinchine": "Wq = λE[S²]/(2(1−ρ)) (Pollaczek-Khinchine)",
    "sans_attente": "infinité de serveurs : Wq = 0, L = λ/μ",
    "blocage": "K fini : probabilité de refus à calculer",
    "population_finie": "N fini : λ baisse quand la file se remplit",
    "kingman_lindley": "pas de forme fermée : approximation de Kingman, simulation de Lindley",
    "par_classe": "discipline à priorité : attente calculée classe par classe",
}


@dataclass
class Kendall:
    A: str
    S: str
    c: float      # entier ≥ 1, ou math.inf
    K: float      # capacité totale (file + service), ≥ c
    N: float      # taille de la population qui peut appeler
    D: str        # discipline de service


def lire_loi(x: str) -> str:
    """M, D, G, GI ou Ek (k entier ≥ 1)."""
    if x in ("M", "D", "G", "GI"):
        return x
    if x.startswith("E") and x[1:].isdigit() and int(x[1:]) >= 1:
        return x
    raise ValueError(f"loi inconnue : {x!r}")


def lire_nombre(x: str) -> float:
    """Entier ≥ 1, ou ∞ (écrit « ∞ » ou « inf »)."""
    if x in ("∞", "inf"):
        return math.inf
    if x.isdigit() and int(x) >= 1:
        return int(x)
    raise ValueError(f"nombre invalide : {x!r}")


def analyser(notation: str) -> Kendall:
    """Complète les cases absentes par ∞, ∞, FIFO, puis valide chaque case."""
    cases = notation.replace(" ", "").split("/")
    if not 3 <= len(cases) <= 6:
        raise ValueError("il faut de 3 à 6 cases séparées par /")
    cases += ["∞", "∞", "FIFO"][len(cases) - 3:]
    k = Kendall(lire_loi(cases[0]), lire_loi(cases[1]), lire_nombre(cases[2]),
                lire_nombre(cases[3]), lire_nombre(cases[4]), cases[5].upper())
    if k.K < k.c:
        raise ValueError("K compte les places en service : il faut K ≥ c")
    if k.D not in DISCIPLINES:
        raise ValueError(f"discipline inconnue : {k.D}")
    return k


def formules(k: Kendall) -> list[str]:
    """Liste des résultats utilisables pour cette file, du plus général au plus précis."""
    res = ["little"]
    ouvert = k.K == math.inf and k.N == math.inf
    if k.c == math.inf:
        res.append("sans_attente")
    elif k.A == "M" and ouvert and k.D in ("FIFO", "LIFO", "SIRO"):
        if k.S == "M":
            res.append("mm1" if k.c == 1 else "erlang_c")
        if k.c == 1:
            res.append("pollaczek_khinchine")   # vrai pour toute loi de service, M comprise
    if k.K != math.inf:
        res.append("blocage")
    if k.N != math.inf:
        res.append("population_finie")
    if k.A != "M" and k.c != math.inf:
        res.append("kingman_lindley")
    if k.D == "PR":
        res.append("par_classe")
    return res


def wq_pollaczek_khinchine(lam: float, es: float, es2: float) -> float:
    """Wq = λ E[S²] / (2 (1 − ρ)), avec ρ = λ E[S] < 1 (arrivées de Poisson, un serveur)."""
    rho = lam * es
    if lam <= 0 or es <= 0 or es2 < es * es:
        raise ValueError("il faut λ > 0, E[S] > 0 et E[S²] ≥ E[S]²")
    if rho >= 1:
        raise ValueError(f"ρ = {rho:.2f} ≥ 1 : pas de régime stable")
    return lam * es2 / (2 * (1 - rho))


def wq_kingman(rho: float, ca2: float, cs2: float, es: float) -> float:
    """Approximation G/G/1 : Wq ≈ ρ/(1−ρ) · (Ca² + Cs²)/2 · E[S]. Exacte quand Ca² = 1 (arrivées M)."""
    return rho / (1 - rho) * (ca2 + cs2) / 2 * es


def simuler_lindley(inter_arrivees: list[float], services: list[float]) -> float:
    """Attente moyenne en file d'un serveur FIFO : W(n+1) = max(0, W(n) + S(n) − A(n+1)). Vaut pour tout G/G/1."""
    w, total = 0.0, 0.0
    for n in range(1, len(services)):
        w = max(0.0, w + services[n - 1] - inter_arrivees[n])
        total += w
    return total / len(services)


def main() -> None:
    print("1. Lire une notation et savoir quelles formules s'appliquent")
    for notation in ("M/M/1", "M/D/1", "M/G/1", "M/M/4", "M/M/4/10", "G/G/1", "M/M/1/∞/20", "M/G/∞", "M/M/1/∞/∞/PR"):
        k = analyser(notation)
        print(f"  {notation:<13} → {', '.join(formules(k))}")
    assert analyser("M/M/1") == Kendall("M", "M", 1, math.inf, math.inf, "FIFO")
    assert formules(analyser("M/M/1")) == ["little", "mm1", "pollaczek_khinchine"]
    assert formules(analyser("M/G/1")) == ["little", "pollaczek_khinchine"]
    assert formules(analyser("M/M/4")) == ["little", "erlang_c"]
    assert "kingman_lindley" in formules(analyser("G/G/1")) and "pollaczek_khinchine" not in formules(analyser("G/G/1"))
    assert "blocage" in formules(analyser("M/M/4/10")) and "population_finie" in formules(analyser("M/M/1/∞/20"))
    for fausse in ("M/M", "X/M/1", "M/M/0", "M/M/4/2", "M/M/1/∞/∞/VIP"):
        try:
            analyser(fausse)
        except ValueError as e:
            print(f"  {fausse:<13} → refusée ({e})")
        else:
            raise AssertionError("notation invalide acceptée")

    print("2. Pollaczek-Khinchine à λ = 3 req/s, E[S] = 0.25 s (ρ = 0.75)")
    lam, es = 3.0, 0.25
    lois = {
        "M (exponentiel)": 2 * es * es,              # E[S²] = 2/μ²
        "D (constant)": es * es,                      # E[S²] = E[S]²
        "G (90 % 0.1 s, 10 % 1.6 s)": 0.9 * 0.1 ** 2 + 0.1 * 1.6 ** 2,
    }
    wq = {}
    for nom, es2 in lois.items():
        cs2 = es2 / es ** 2 - 1
        wq[nom] = wq_pollaczek_khinchine(lam, es, es2)
        print(f"  {nom:<27} E[S²] = {es2:.4f}  Cs² = {cs2:.2f}  Wq = {wq[nom]:.4f} s  W = {wq[nom] + es:.4f} s")
        assert abs(wq[nom] - wq_kingman(0.75, 1.0, cs2, es)) < 1e-12   # Kingman exact quand Ca² = 1
    assert abs(wq["M (exponentiel)"] - 0.75) < 1e-12 and abs(wq["D (constant)"] - 0.375) < 1e-12
    assert abs(wq["G (90 % 0.1 s, 10 % 1.6 s)"] - 1.59) < 1e-12
    print(f"  rapport Wq(M/D/1) / Wq(M/M/1) = {wq['D (constant)'] / wq['M (exponentiel)']:.2f} ;"
          f" rapport W = {(wq['D (constant)'] + es) / (wq['M (exponentiel)'] + es):.3f}")

    print("3. Simulation (graine 68, 200 000 requêtes, mêmes arrivées pour les trois services)")
    rng = random.Random(68)
    n = 200_000
    arrivees = [rng.expovariate(lam) for _ in range(n)]
    services = {
        "M (exponentiel)": [rng.expovariate(1 / es) for _ in range(n)],
        "D (constant)": [es] * n,
        "G (90 % 0.1 s, 10 % 1.6 s)": [0.1 if rng.random() < 0.9 else 1.6 for _ in range(n)],
    }
    tolerance = {"M (exponentiel)": 0.05, "D (constant)": 0.05, "G (90 % 0.1 s, 10 % 1.6 s)": 0.12}
    sim = {nom: simuler_lindley(arrivees, s) for nom, s in services.items()}
    for nom, w in sim.items():
        ecart = (w - wq[nom]) / wq[nom]
        print(f"  {nom:<27} Wq simulée = {w:.3f} s   formule = {wq[nom]:.3f} s   écart = {ecart:+.1%}")
        assert abs(ecart) < tolerance[nom]
    ratio = sim["D (constant)"] / sim["M (exponentiel)"]
    print(f"  rapport simulé M/D/1 / M/M/1 = {ratio:.3f}")
    assert 0.47 < ratio < 0.53

    print("4. Arrivées régulières (cron) : D/D/1, la formule P-K ne s'applique plus")
    regulieres = [1 / lam] * n
    reel = simuler_lindley(regulieres, services["D (constant)"])
    print(f"  D/D/1 simulée = {reel:.3f} s ; P-K appliquée à tort = {wq['D (constant)']:.3f} s ;"
          f" Kingman (Ca² = 0, Cs² = 0) = {wq_kingman(0.75, 0.0, 0.0, es):.3f} s")
    assert reel == 0.0 and wq_kingman(0.75, 0.0, 0.0, es) == 0.0

    print("5. Charge trop forte refusée")
    try:
        wq_pollaczek_khinchine(4.0, 0.25, 0.0625)
    except ValueError as e:
        print(f"  λ = 4, E[S] = 0.25 → {e}")
    else:
        raise AssertionError("ρ = 1 aurait dû être refusé")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Lire une notation et savoir quelles formules s'appliquent
  M/M/1         → little, mm1, pollaczek_khinchine
  M/G/1         → little, pollaczek_khinchine
  G/G/1         → little, kingman_lindley
…
2. Pollaczek-Khinchine à λ = 3 req/s, E[S] = 0.25 s (ρ = 0.75)
  M (exponentiel)             E[S²] = 0.1250  Cs² = 1.00  Wq = 0.7500 s  W = 1.0000 s
  D (constant)                E[S²] = 0.0625  Cs² = 0.00  Wq = 0.3750 s  W = 0.6250 s
  G (90 % 0.1 s, 10 % 1.6 s)  E[S²] = 0.2650  Cs² = 3.24  Wq = 1.5900 s  W = 1.8400 s
  rapport Wq(M/D/1) / Wq(M/M/1) = 0.50 ; rapport W = 0.625
3. Simulation (graine 68, 200 000 requêtes, mêmes arrivées pour les trois services)
  M (exponentiel)             Wq simulée = 0.726 s   formule = 0.750 s   écart = -3.2%
  D (constant)                Wq simulée = 0.372 s   formule = 0.375 s   écart = -0.8%
  G (90 % 0.1 s, 10 % 1.6 s)  Wq simulée = 1.731 s   formule = 1.590 s   écart = +8.8%
  rapport simulé M/D/1 / M/M/1 = 0.512
4. Arrivées régulières (cron) : D/D/1, la formule P-K ne s'applique plus
  D/D/1 simulée = 0.000 s ; P-K appliquée à tort = 0.375 s ; Kingman (Ca² = 0, Cs² = 0) = 0.000 s
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : la notation n'est pas du vocabulaire. Elle décide si une formule existe, et la variabilité du service, invisible dans μ, change l'attente du simple au quadruple à charge égale.

## Squelette algorithmique

Le fichier repose sur trois algorithmes. Le premier lit une notation de Kendall : il reçoit une chaîne de trois à six cases et rend les six cases complétées, plus la liste des résultats qui ont le droit de s'appliquer. L'idée est de compléter les cases absentes par les valeurs par défaut, de valider chaque case, puis de descendre une liste de conditions, de la plus générale à la plus précise. Le deuxième est le calcul analytique de Pollaczek-Khinchine : il reçoit λ et les deux premiers moments du service et rend l'attente moyenne en file. Le troisième est la simulation à événements discrets d'un guichet FIFO, réduite à la récurrence de Lindley : il reçoit les temps entre arrivées et les durées de service et rend l'attente moyenne observée, sans aucune hypothèse de loi.

```text
ALGORITHME AnalyserKendall
ENTRÉES : notation, chaîne « A/S/c/K/N/D » de 3 à 6 cases
SORTIE : les six cases, et la liste des formules applicables
  cases ← découper notation sur « / »
  SI nombre de cases < 3 OU nombre de cases > 6 ALORS
    ÉCHOUER « il faut de 3 à 6 cases »
  FIN SI
  défauts ← (∞, ∞, FIFO)
  TANT QUE nombre de cases < 6 FAIRE
    ajouter à cases la valeur par défaut de la case suivante
  FIN TANT QUE
  vérifier A et S dans {M, D, G, GI, Ek} ; c, K, N entiers ≥ 1 ou ∞ ; K ≥ c ; D connue
  formules ← [Little]
  SI c = ∞ ALORS
    ajouter « sans attente » à formules
  SINON SI A = M ET K = ∞ ET N = ∞ ET D dans {FIFO, LIFO, SIRO} ALORS
    SI S = M ALORS
      ajouter (M/M/1 si c = 1, Erlang C sinon) à formules
    FIN SI
    SI c = 1 ALORS
      ajouter Pollaczek-Khinchine à formules
    FIN SI
  FIN SI
  SI K < ∞ ALORS ajouter « blocage » FIN SI
  SI N < ∞ ALORS ajouter « population finie » FIN SI
  SI A ≠ M ET c < ∞ ALORS ajouter « Kingman, Lindley » FIN SI
  SI D = PR ALORS ajouter « par classe » FIN SI
  RETOURNER (cases, formules)

ALGORITHME AttentePollaczekKhinchine   (calcul analytique, M/G/1)
ENTRÉES : λ > 0, E[S] > 0, E[S²] ≥ E[S]²
SORTIE : Wq
  ρ ← λ × E[S]
  SI ρ ≥ 1 ALORS
    ÉCHOUER « pas de régime stable »
  SINON
    RETOURNER λ × E[S²] / (2 × (1 − ρ))
  FIN SI

ALGORITHME SimulerLindley              (simulation à événements discrets, un guichet FIFO)
ENTRÉES : temps entre arrivées A[1..n], durées de service S[1..n]
SORTIE : attente moyenne en file observée
  w ← 0 ; total ← 0                          // la première requête trouve le guichet libre
  POUR i DE 2 À n FAIRE
    w ← max(0, w + S[i − 1] − A[i])          // le guichet se libère w + S[i−1] après l'arrivée i−1
    total ← total + w
  FIN POUR
  RETOURNER total / n
```

**Complexité :** `AnalyserKendall` traite au plus six cases et teste un nombre fixe de conditions : son temps et sa mémoire sont en O(1), ou en O(m) si l'on compte la longueur m de la chaîne lue. `AttentePollaczekKhinchine` fait quatre opérations : O(1). `SimulerLindley` fait une mise à jour en temps constant par requête : O(n) en temps. Le code garde les listes d'arrivées et de services en mémoire, O(n), pour réutiliser les mêmes arrivées avec trois lois de service ; tirer chaque nombre au moment où l'on s'en sert ramènerait la mémoire à O(1). Le programme complet simule trois lois plus le cas régulier sur 200 000 requêtes, soit environ 800 000 mises à jour, en moins d'une seconde.

**Du squelette au code :** le découpage, le test du nombre de cases et la boucle de complétion de `AnalyserKendall` sont les trois premières lignes de `analyser` (en Python, la boucle `TANT QUE` s'écrit en une seule tranche, `cases += ["∞", "∞", "FIFO"][len(cases) - 3:]`) ; la ligne « vérifier » est répartie entre `lire_loi`, `lire_nombre` et les deux tests `k.K < k.c` et `k.D not in DISCIPLINES` ; la cascade de `SI` qui construit la liste est la fonction `formules`. `AttentePollaczekKhinchine` est `wq_pollaczek_khinchine`, et l'approximation de Kingman, qui remplace ce calcul quand les arrivées ne sont pas M, est `wq_kingman`. `SimulerLindley` est `simuler_lindley` ; les listes A et S sont fabriquées au bloc 3 de `main()` par `rng.expovariate` et `rng.random`, avec la graine fixe 68, et le bloc 4 lui passe des arrivées régulières.

## Cas d'usage réels aux Émirats

Les débits, durées et seuils ci-dessous sont illustratifs : en production, on les mesure sur les journaux de chaque service.

### Banque — un agent de pré-qualification dont les réponses ont une longue traîne

Une banque de détail de Dubaï propose dans son application un agent de pré-qualification de prêt personnel : le client donne son salaire et ses mensualités en cours, l'agent appelle l'outil de mensualité puis l'outil de ratio d'endettement, qui applique le plafond de la CBUAE (toutes les mensualités, la nouvelle comprise, au plus 50 % du revenu). Les demandes viennent de milliers de clients indépendants, donc les arrivées sont bien M ; mais la durée de service ne l'est pas, parce que neuf réponses sur dix sont un simple « recevable » et la dixième une longue explication avec tableau d'amortissement. L'équipe avait dimensionné avec M/M/1 : à 3 requêtes par seconde et par instance pour un service moyen de 0,25 s, elle annonçait 0,75 s d'attente. La notation correcte est M/G/1, et Pollaczek-Khinchine avec le E[S²] mesuré donne 1,59 s, plus du double, ce qui explique les plaintes des jours de paie. Plutôt que de doubler les instances, l'agent borne la longueur de sa réponse et ne produit le tableau détaillé que si le client le demande : Cₛ² baisse, et l'attente de tous les clients avec lui. La contrainte est que le ratio d'endettement doit toujours venir de l'outil, jamais d'une estimation du modèle : on raccourcit le texte, pas le calcul. L'indicateur suivi est le couple E[S] et E[S²] chaque semaine, donc Cₛ², à côté du p95 de l'attente.

### Immobilier — des évaluations nocturnes déclenchées par une cron

Une agence et promoteur de Dubaï et d'Abu Dhabi fait réévaluer chaque nuit les annonces de son catalogue : toutes les 20 secondes, une tâche planifiée envoie une annonce à un agent qui compare son prix en AED/sqft aux transactions récentes enregistrées au DLD. Le prompt a toujours la même forme, et l'évaluation dure presque toujours 12 secondes : la file est D/D/1, avec ρ = 12/20 = 0,6. Comme dans le contre-exemple de la démonstration, chaque annonce trouve l'agent libre et l'attente vaut 0. Un ingénieur qui aurait appliqué M/M/1 aurait prévu 0,6/0,4 × 12 = 18 s d'attente par annonce et lancé des instances inutiles. Le vrai danger est ailleurs : si l'on passe la cadence à une annonce toutes les 10 secondes, ρ = 1,2 et le retard grossit de 0,1 − 1/12 ≈ 0,0167 annonce par seconde, soit 60 annonces de plus chaque heure, sans aucune rafale aléatoire pour l'expliquer. La décision est donc de garder une seule instance tant que ρ < 1 en régime de cron, et d'ajouter une instance avant d'augmenter la cadence. L'indicateur suivi est l'heure de fin du lot, qui doit précéder l'ouverture de l'agence, et la date de la dernière transaction DLD utilisée pour chaque prix affiché.

### Crypto — des alertes de liquidité qui arrivent en rafales

Une plateforme d'actifs virtuels agréée par la VARA fait trier par un agent les alertes de liquidité de ses carnets d'ordres. Un mouvement de prix déclenche des dizaines d'alertes en quelques secondes, puis plus rien pendant des minutes : les temps entre arrivées sont très dispersés (Cₐ² = 4 dans les journaux, valeur illustrative), et la file est G/G/1. Pollaczek-Khinchine n'a plus le droit de s'appliquer, et M/M/1 promettrait, à ρ = 0,5 et 2 s par alerte, une attente de 2 s. L'approximation de Kingman donne (4 + 1)/2 × 1 × 2 = 5 s, deux fois et demie plus, et l'équipe la confirme en rejouant les traces réelles d'arrivées dans la récurrence de Lindley. La décision est double : une discipline à priorité (PR) pour les alertes critiques, qui passent devant les informationnelles, et une instance de réserve qui démarre dès qu'une rafale commence. Sans cela, l'alerte qui compte attend derrière quarante alertes sans conséquence, ce qui est exactement le risque que la surveillance devait réduire, et que les obligations de surveillance de la VARA demandent de maîtriser (à confirmer avec le texte en vigueur). L'indicateur suivi n'est pas l'attente moyenne mais le p95 du délai de prise en charge des alertes critiques.

### RH — une population finie à la veille de la date limite WPS

Un cabinet RH présent dans plusieurs émirats valide chaque mois les fichiers de salaires de 40 entreprises clientes avant leur envoi dans le WPS : l'agent vérifie chaque IBAN AE par le contrôle mod 97, les montants et les identifiants de contrat MOHRE. Les fichiers arrivent tous dans les deux jours qui précèdent la date limite. La population est finie : quand 30 fichiers attendent déjà, il ne reste que 10 entreprises susceptibles d'en envoyer, et le taux d'arrivée baisse de lui-même. La notation est M/G/1/∞/40, et une formule M/M/1 à λ fixe, poussée au-delà de ρ = 1 au pic, annoncerait une file infinie qui n'existera jamais. La bonne question est autre : en combien de temps l'agent vide-t-il au pire 40 fichiers ? Avec 45 secondes par fichier (valeur illustrative), il lui faut 40 × 45 s = 30 minutes, ce que l'on compare à l'heure limite. L'agent planifie donc le pic plutôt que de dimensionner une moyenne, et relance les entreprises en retard la veille. Un salaire versé en retard expose l'employeur aux sanctions prévues par le MOHRE (à confirmer avec le texte en vigueur) ; l'indicateur suivi est l'heure de validation du dernier fichier et le nombre de fichiers rejetés pour IBAN invalide.

### Secteur public — un plafond de requêtes simultanées

Une entité de services publics en ligne, accessible par UAE Pass, fait répondre un agent bilingue arabe et anglais aux questions sur les démarches. Pour protéger le système dorsal, la plateforme limite à 10 le nombre de requêtes présentes dans le système pour 4 instances : la notation est M/M/4/10. La case K = 10 dit tout de suite ce que M/M/4 cachait : au-delà de 10, une requête n'attend pas, elle est refusée. Un tableau de bord qui ne montre que W affiche alors un service rapide pendant qu'une partie des usagers est renvoyée ; si le refus touche 8 % des demandes au pic (valeur illustrative), la loi de Little ne s'applique qu'au trafic accepté, λ(1 − 0,08). La décision est de mesurer et publier le taux de refus à côté de W, et de répondre à chaque refus par un message bilingue qui donne un délai pour réessayer plutôt que par une erreur muette. Comme la PDPL demande de ne conserver les données personnelles que le temps nécessaire, la file ne garde pas le texte des requêtes refusées. Les indicateurs suivis sont le taux de refus et le W des requêtes acceptées.

### Assurance — un serveur de modèle qui sert plusieurs requêtes à la fois

Un assureur auto et santé héberge son propre modèle pour un agent de tri des sinistres. Son serveur d'inférence fait avancer plusieurs générations en même temps (traitement par lots continu) : il se comporte, en première approximation, comme une discipline PS plutôt que FIFO. La notation M/G/1/∞/∞/PS change la formule : le séjour moyen vaut E[S]/(1 − ρ) quelle que soit la loi du service, et une requête courte n'attend plus derrière une longue. Avec la loi bimodale de la démonstration (E[S] = 0,25 s, ρ = 0,75), PS donne 1 s de séjour moyen, contre 1,84 s en FIFO. La décision est de laisser sur le même serveur les questions courtes (« où en est mon dossier ? ») et les analyses longues (photos du véhicule, franchise, vétusté), sans file FIFO devant le modèle. Sans cette lecture, l'équipe aurait séparé les deux flux sur deux serveurs, en payant une instance de plus pour un gain nul. L'assurance est supervisée par la CBUAE et chaque décision de sinistre doit rester traçable ; l'indicateur suivi est le séjour moyen des requêtes courtes, qui doit rester proche de leur propre durée divisée par 1 − ρ.

## Pièges et limites

- **Prendre M pour une hypothèse prudente.** Avec une longue traîne (Cₛ² > 1), M/M/1 sous-estime l'attente : 0,75 s annoncées pour 1,59 s réelles dans l'exemple.
- **Appliquer Pollaczek-Khinchine à des arrivées qui ne sont pas poissoniennes.** Une cron régulière attend moins que prévu (0 au lieu de 0,375 s), des rafales attendent plus. La formule repose sur PASTA.
- **Oublier les cases par défaut.** M/M/1 suppose K = ∞. Un rate limiter transforme l'attente en refus, et un W qui baisse peut cacher un service qui se dégrade.
- **Confondre Wq et W.** Un service constant divise l'attente en file par deux, pas le temps de réponse (0,625 s contre 1 s ici).
- **Ne surveiller que la moyenne.** Une priorité, ou un N fini, change qui attend sans forcément changer la moyenne : on suit aussi le p95 par classe.

### Exercice feuille blanche

1. Sans regarder le code, écrire `analyser` pour des notations de 3 à 6 cases, avec les valeurs par défaut ∞, ∞, FIFO, puis vérifier que `"M/M/1"` donne `Kendall("M", "M", 1, math.inf, math.inf, "FIFO")`.
2. Prédire, puis vérifier : un service Erlang-2 a Cₛ² = 1/2. À λ = 3 et E[S] = 0,25 s, que vaut Wq ? (Réponse : (1 + 0,5)/2 × 3 × 0,25 = 0,5625 s ; vérifier avec `wq_pollaczek_khinchine(3.0, 0.25, 1.5 * 0.25 ** 2)`.)
3. Trouver le bug : `return lam * es ** 2 / (2 * (1 - rho))`. Pour quelle loi de service le résultat reste-t-il juste, et que devient l'attente d'un service à longue traîne ?

## Pour aller plus loin

La file M/M/c/K a une forme fermée (loi tronquée de naissance et de mort, voir l'étape 71) ; le cas c = K donne la formule d'Erlang B, la probabilité de refus sans aucune file. La population finie conduit au modèle d'Engset et au modèle de réparation de machines. Pour G/G/1, Kingman a aussi démontré une borne supérieure, Wq ≤ λ(σₐ² + σₛ²)/(2(1 − ρ)), où σₐ² et σₛ² sont les variances des temps entre arrivées et des services. Les files à priorité se calculent classe par classe (formule de Cobham), et l'insensibilité de PS se démontre par les réseaux de files de Kelly et de BCMP.

> Suite : [Files d'attente et loi de Little](<69-Files-Attente-et-Goulot.md>) — étape 69.
