# Étape 70 — File d'Attente M/M/1 — Dimensionnement d'un Agent Unique

> Étape 70 du parcours · Prérequis : [Files d'attente et loi de Little](<69-Files-Attente-et-Goulot.md>) · Suite : [Erlang C et file M/M/c](<71-Erlang-C.md>)

**Dossier :** 12-Production-Couts-Optimisation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, AI Platform Team  
**Nom du fichier :** 70-File-MM1.md

## Définition

La file M/M/1 est le modèle le plus simple d'un service rendu par un seul agent. Les requêtes arrivent selon un processus de Poisson de taux λ : beaucoup d'utilisateurs indépendants, et un temps entre deux arrivées qui suit une loi exponentielle. Chaque traitement dure un temps exponentiel de moyenne 1/μ, et un seul serveur traite les requêtes dans leur ordre d'arrivée, sans limite de place. Le « M » veut dire que ces deux durées sont sans mémoire : le temps déjà passé à attendre ne rend pas la fin plus proche. Grâce à cette propriété, tout le système se résume au nombre de requêtes présentes, et l'on peut calculer exactement sa loi, ses moyennes et même la loi complète du temps de réponse.

## Rôle dans un agent

Un seul agent répond, par exemple parce qu'il tient un verrou sur une ressource (un compte, une licence d'outil, un ordre de traitement à respecter) ou parce que c'est la première instance qu'on déploie. Dans la boucle percevoir → décider → agir → observer, l'appel au LLM et aux outils forme le service ; la file se constitue devant lui. M/M/1 donne à l'**ordonnanceur** la charge maximale admissible pour un SLA, au **garde-fou de débit** le moment où il faut refuser ou différer des requêtes, et à l'interface le temps d'attente à afficher. C'est aussi la brique de base : Erlang C (étape 71) généralise la même chaîne à plusieurs instances.

## Équation complète

Utilisation, et condition de stabilité :

$$
\rho = \frac{\lambda}{\mu} \qquad (\rho < 1 \text{ obligatoire})
$$

Loi stationnaire du nombre de requêtes présentes :

$$
\pi_n = (1 - \rho)\,\rho^n, \qquad n = 0, 1, 2, \dots
$$

$$
P_0 = 1 - \rho
\qquad\qquad
P(N \ge n) = \rho^n
$$

Nombres moyens dans le système et dans la file :

$$
L = \frac{\rho}{1 - \rho} = \frac{\lambda}{\mu - \lambda}
$$

$$
L_q = \frac{\rho^2}{1 - \rho}
$$

Temps moyens de séjour et d'attente :

$$
W = \frac{1}{\mu - \lambda}
$$

$$
W_q = \frac{\rho}{\mu - \lambda}
$$

Loi de Little :

$$
L = \lambda W, \qquad L_q = \lambda W_q
$$

Loi du temps de réponse R (séjour d'une requête, FIFO), et son quantile d'ordre p :

$$
P(R > t) = e^{-(\mu - \lambda)\,t}
\qquad\qquad
t_p = \frac{-\ln(1 - p)}{\mu - \lambda}
$$

## Décryptage des symboles

$$
\lambda
$$

Taux d'arrivée des requêtes, en requêtes par seconde, réel > 0 · variable Python : `lam` ou `lambda_rate`.

$$
\mu
$$

Taux de service de l'agent unique, en requêtes par seconde ; 1/μ est la durée moyenne d'un traitement · variable Python : `mu` ou `mu_rate`.

$$
\rho
$$

Utilisation, λ/μ : fraction du temps où l'agent travaille, dans [0 ; 1[ pour une file stable · variable Python : `rho`.

$$
N
$$

Nombre de requêtes présentes (en attente et en service) à un instant pris au hasard, entier ≥ 0 · variable Python : `n` dans `simuler_chaine`.

$$
\pi_n
$$

Probabilité, en régime stationnaire, que N vaille exactement n · variable Python : `pi_n(n, rho)`.

$$
P_0
$$

Probabilité que l'agent soit libre, égale à π₀ = 1 − ρ · variable Python : `m["P0"]`.

$$
L
$$

Nombre moyen de requêtes présentes, E[N] · variable Python : `m["L"]`.

$$
L_q
$$

Nombre moyen de requêtes qui attendent, sans celle en service · variable Python : `m["Lq"]`.

$$
W
$$

Temps de séjour moyen, attente plus service, en secondes · variable Python : `m["W"]`.

$$
W_q
$$

Temps d'attente moyen avant le début du service, en secondes · variable Python : `m["Wq"]`.

$$
R
$$

Temps de réponse d'une requête particulière, variable aléatoire dont W est la moyenne · pas de variable : on en calcule les quantiles.

$$
t_p
$$

Quantile d'ordre p du temps de réponse : une fraction p des requêtes ressort en moins de tₚ secondes (t₀,₉₅ est le p95) · variable Python : `quantile_sejour(lam, mu, p)`.

## Démonstration

### 1. La chaîne de Markov du nombre de requêtes

On note n le nombre de requêtes présentes. Pendant un court instant dt, une arrivée se produit avec probabilité λ dt, parce que les arrivées forment un processus de Poisson. Si n ≥ 1, le service en cours se termine avec probabilité μ dt, parce qu'une durée exponentielle est sans mémoire : quel que soit le temps déjà écoulé, le reste du service suit encore une loi exponentielle de taux μ, ce qui s'écrit

$$
P(S > s + t \mid S > s) = \frac{e^{-\mu (s+t)}}{e^{-\mu s}} = e^{-\mu t}
$$

Le futur ne dépend donc que de n, pas de l'histoire : c'est une chaîne de Markov qui monte de n à n + 1 au taux λ et descend de n à n − 1 au taux μ (une chaîne de naissance et de mort). Sans cette propriété, il faudrait aussi connaître l'âge du service en cours, et rien de ce qui suit ne marcherait.

### 2. Les équations d'équilibre

En régime stationnaire, pour chaque état, le flux de probabilité qui en sort égale celui qui y entre. On quitte l'état 0 seulement par une arrivée, et l'on y entre seulement par un départ depuis l'état 1. On quitte un état n ≥ 1 par une arrivée ou un départ, et l'on y entre depuis n − 1 (arrivée) ou depuis n + 1 (départ) :

$$
\lambda\, \pi_0 = \mu\, \pi_1
$$

$$
(\lambda + \mu)\, \pi_n = \lambda\, \pi_{n-1} + \mu\, \pi_{n+1} \qquad (n \ge 1)
$$

### 3. Résolution : πₙ = ρⁿ π₀

On montre par récurrence que λ πₙ₋₁ = μ πₙ pour tout n ≥ 1. Pour n = 1, c'est l'équation de l'état 0. Si c'est vrai au rang n, on remplace λ πₙ₋₁ par μ πₙ dans l'équation de l'état n :

$$
(\lambda + \mu)\, \pi_n = \mu\, \pi_n + \mu\, \pi_{n+1}
\;\Longleftrightarrow\;
\lambda\, \pi_n = \mu\, \pi_{n+1}
$$

ce qui est la propriété au rang n + 1. Cette égalité a un sens simple : autant de probabilité franchit par seconde la « coupure » entre les états {0, …, n} et {n + 1, n + 2, …} dans un sens que dans l'autre. On en tire πₙ = (λ/μ) πₙ₋₁ = ρ πₙ₋₁, donc πₙ = ρⁿ π₀.

### 4. Normalisation : π₀ = 1 − ρ, et pourquoi ρ < 1

Les probabilités doivent sommer à 1. La somme partielle d'une série géométrique vaut

$$
\sum_{n=0}^{M} \rho^n = \frac{1 - \rho^{M+1}}{1 - \rho}
$$

parce qu'en multipliant la somme par 1 − ρ, tous les termes se télescopent sauf le premier et le dernier. Si ρ < 1, ρᴹ⁺¹ tend vers 0 et la somme tend vers 1/(1 − ρ). Donc

$$
\pi_0 \sum_{n=0}^{\infty} \rho^n = 1
\;\Longrightarrow\;
\pi_0 = 1 - \rho
\;\Longrightarrow\;
\pi_n = (1-\rho)\,\rho^n
$$

Si ρ ≥ 1, la série diverge : aucune valeur de π₀ ne fait sommer les πₙ à 1, il n'existe pas de loi stationnaire, et la file n'a pas de régime stable. C'est ce que vérifie `if lambda_rate >= mu_rate`. On en tire aussi la queue de la loi : la probabilité d'au moins n requêtes présentes vaut (1 − ρ)(ρⁿ + ρⁿ⁺¹ + …) = ρⁿ.

P₀ = 0,25 pour λ = 3 et μ = 4 n'est pas « 1/4 par symétrie » : il sort du bilan de la chaîne. Il coïncide avec la fraction du temps libre que donne Little appliquée au seul serveur (étape 69, point 2), qui elle vaut pour n'importe quelle file à un serveur.

### 5. Le nombre moyen L

$$
L = \sum_{n=0}^{\infty} n\, \pi_n = (1-\rho) \sum_{n=0}^{\infty} n\, \rho^n
$$

On calcule S = ∑ n ρⁿ sans dériver : en soustrayant ρS à S, terme à terme, il reste la série géométrique sans son premier terme.

$$
S - \rho S = \sum_{n=1}^{\infty} \rho^n = \frac{\rho}{1-\rho}
\;\Longrightarrow\;
S = \frac{\rho}{(1-\rho)^2}
$$

(on obtient la même chose en dérivant 1/(1 − ρ) puis en multipliant par ρ). Donc

$$
L = (1-\rho) \cdot \frac{\rho}{(1-\rho)^2} = \frac{\rho}{1-\rho}
$$

### 6. Little donne W, puis Lq et Wq

La loi de Little (étape 69) donne

$$
W = \frac{L}{\lambda} = \frac{\rho}{\lambda (1-\rho)} = \frac{1}{\mu (1-\rho)} = \frac{1}{\mu - \lambda}
$$

parce que ρ/λ = 1/μ et que μ(1 − ρ) = μ − λ. Dans la file, il y a n − 1 requêtes quand il y en a n ≥ 1 dans le système :

$$
L_q = \sum_{n=1}^{\infty} (n-1)\, \pi_n = L - (1 - \pi_0) = \frac{\rho}{1-\rho} - \rho = \frac{\rho^2}{1-\rho}
$$

parce que la somme des πₙ pour n ≥ 1 vaut 1 − π₀ = ρ. Little sur la file donne enfin Wq = Lq/λ = ρ/(μ − λ), et l'on vérifie que Wq = W − 1/μ : l'attente est le séjour moins le service.

### 7. Le temps de réponse suit une loi exponentielle

Une arrivée de Poisson voit le système dans son état stationnaire (propriété PASTA, étape 68) : elle trouve n requêtes avec probabilité πₙ. En FIFO, elle ressort après la fin de n + 1 services : le reste du service en cours, qui suit encore une loi exponentielle de taux μ par absence de mémoire, les n − 1 services complets en attente devant elle, et le sien. Le nombre d'étapes k = n + 1 vaut k avec probabilité (1 − ρ)ρᵏ⁻¹ : c'est une loi géométrique, comme si l'on jetait à chaque fin d'étape une pièce indépendante qui dit « c'était la dernière » avec probabilité 1 − ρ. Les fins d'étapes forment un processus de Poisson de taux μ ; n'en garder que celles où la pièce dit « dernière » donne un processus de Poisson de taux μ(1 − ρ) (amincissement d'un processus de Poisson). La sortie est le premier de ces événements, donc

$$
P(R > t) = e^{-\mu (1-\rho)\, t} = e^{-(\mu - \lambda)\, t}
$$

Pour le quantile, on résout P(R ≤ tₚ) = p, c'est-à-dire

$$
e^{-(\mu - \lambda)\, t_p} = 1 - p
$$

et l'on prend le logarithme naturel des deux côtés : tₚ = −ln(1 − p)/(μ − λ). Le p95 vaut ln 20/(μ − λ) ≈ 3 W, et la médiane ln 2 × W ≈ 0,69 W. Un SLA écrit sur le p95 est donc environ trois fois plus exigeant qu'un SLA écrit sur la moyenne.

### 8. Exemple fait à la main (le code reprend ces nombres)

Avec λ = 3 et μ = 4 :

- ρ = 3/4 = 0,75 et P₀ = 0,25 ;
- π₁ = 0,25 × 0,75 = 0,1875, π₂ = 0,1875 × 0,75 = 0,140625, et P(N ≥ 4) = 0,75⁴ = 0,3164 ;
- L = 0,75/0,25 = 3, et l'on retrouve la forme λ/(μ − λ) = 3/1 = 3 ;
- W = 1/(4 − 3) = 1 s, et Little donne 3 = 3 × 1 ;
- Lq = 0,5625/0,25 = 2,25, la même valeur que λ²/(μ(μ − λ)) = 9/4 ; Wq = 0,75 s = 1 − 0,25 ;
- p95 = ln 20/1 = 2,996 s.

Le dénominateur μ − λ est la vitesse à laquelle on rattrape le retard : 4 services moins 3 arrivées, une requête de marge par seconde. Si λ passe à 3,8, la marge tombe à 0,2 et W passe à 5 secondes, alors que le service dure toujours 0,25 s : ce qui a explosé, c'est la file. À ρ = 0,8, W = 0,25/0,2 = 1,25 s ; à ρ = 0,95, W = 0,25/0,05 = 5 s. Le rapport vaut 4, pour le même agent, le même modèle et le même temps de génération.

## Effets et comportement

- **Le séjour croît comme 1/(1 − ρ)**, à μ fixé. Passer de ρ = 0,8 à ρ = 0,95 multiplie le temps passé dans le système par 4.
- **La file grossit plus vite que la charge.** P(N ≥ n) = ρⁿ : à ρ = 0,75, il y a 32 % de chances de trouver au moins 4 requêtes présentes ; à ρ = 0,9, 66 %.
- **La queue de la loi compte autant que la moyenne.** Le p95 vaut environ 3 fois W ; dimensionner sur la moyenne laisse une requête sur vingt attendre plus du triple.
- **Accélérer l'agent agit deux fois.** Augmenter μ réduit le service et la charge en même temps : de μ = 4 à μ = 5 à λ = 3, W passe de 1 s à 0,5 s.
- **Un seul agent rapide contre plusieurs lents.** Un agent unique de taux 16 répond plus vite (W = 0,25 s à λ = 12) que quatre agents de taux 4 (0,377 s, étape 71), mais il n'a aucune redondance : une panne arrête tout.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| λ, μ | `lam`, `mu` (ou `lambda_rate`, `mu_rate`) |
| ρ, P₀, L, Lq, W, Wq | clés du dictionnaire renvoyé par `file_mm1(lambda_rate, mu_rate)` |
| πₙ = (1 − ρ)ρⁿ | `pi_n(n, rho)` |
| équations d'équilibre | `residu_equilibre(lam, mu, n_max)` |
| tₚ = −ln(1 − p)/(μ − λ) | `quantile_sejour(lam, mu, p)` |
| μ minimal pour un SLA | `mu_minimal(lam, W_cible, t95_cible)` |
| la chaîne elle-même | `simuler_chaine(lam, mu, n_sauts, graine)` |

### Déroulé, ligne par ligne

**`file_mm1(lambda_rate, mu_rate)`**, la fonction d'origine, conservée.

- `if lambda_rate >= mu_rate` refuse le calcul. À λ = 4 et μ = 4, chaque seconde apporte autant qu'on peut servir ; la moindre rafale ne se rattrape jamais, et il n'y a pas de moyenne finie à renvoyer (démonstration, point 4). Lever une erreur est plus honnête qu'un nombre énorme.
- `rho = lambda_rate / mu_rate` vaut 3/4, soit 0,75 : l'agent est occupé les trois quarts du temps. `P0 = 1 - rho` vaut 0,25.
- `L = rho / (1 - rho)` vaut 0,75/0,25 = 3. L'ancienne version écrivait `lambda_rate / (mu_rate - lambda_rate)`, soit 3/1 : c'est le même nombre (point 5).
- `Lq = rho ** 2 / (1 - rho)` vaut 0,5625/0,25 = 2,25. L'ancienne version écrivait `lambda_rate**2 / (mu_rate * (mu_rate - lambda_rate))`, soit 9/4 : même nombre.
- `W = L / lambda_rate` et `Wq = Lq / lambda_rate` : on applique Little au lieu de recopier deux formules de plus, ce qui garde les quatre mesures cohérentes par construction. W = 3/3 = 1 s, Wq = 2,25/3 = 0,75 s.

**`pi_n(n, rho)`** renvoie `(1 - rho) * rho ** n`. Pour `n = 2` : 0,25 × 0,5625 = 0,140625.

**`residu_equilibre(lam, mu, n_max)`** vérifie les équations du point 2 au lieu de les croire.

- État 0 : `abs(lam * pi_n(0, rho) - mu * pi_n(1, rho))`, soit |3 × 0,25 − 4 × 0,1875| = |0,75 − 0,75| = 0.
- États 1 à `n_max` : `sortant = (lam + mu) * pi_n(n, rho)` et `entrant = lam * pi_n(n - 1, rho) + mu * pi_n(n + 1, rho)`. Pour n = 1 : 7 × 0,1875 = 1,3125 et 3 × 0,25 + 4 × 0,140625 = 0,75 + 0,5625 = 1,3125.
- La fonction renvoie le plus grand écart ; il vaut 2,7 × 10⁻²⁰, c'est-à-dire zéro aux arrondis près.

**`quantile_sejour(lam, mu, p)`** renvoie `-math.log(1 - p) / (mu - lam)`. `math.log` est le logarithme naturel. Pour p = 0,95 : −ln 0,05 = ln 20 = 2,996, divisé par 1.

**`mu_minimal(lam, W_cible, t95_cible)`** retourne le point 6 et le point 7.

- 1/(μ − λ) ≤ W équivaut à μ ≥ λ + 1/W : pour W ≤ 0,5 s, μ ≥ 3 + 2 = 5.
- ln 20/(μ − λ) ≤ t₉₅ équivaut à μ ≥ λ + ln 20/t₉₅ : pour un p95 ≤ 1 s, μ ≥ 3 + 2,996 = 5,996.
- `max(besoins)` garde la contrainte la plus forte : le SLA sur le p95 l'emporte.

**`simuler_chaine(lam, mu, n_sauts, graine)`** fait tourner la chaîne du point 1, sur une horloge simulée.

- `taux = lam + (mu if n > 0 else 0.0)` : dans l'état 0, seule une arrivée est possible.
- `duree = rng.expovariate(taux)` : le temps passé dans l'état n avant le prochain saut. On l'ajoute à `temps_par_etat[n]`.
- `n = n + 1 if rng.random() < lam / taux else n - 1` : le saut suivant est une arrivée avec probabilité λ/(λ + μ), un départ sinon. Dans l'état 0, λ/taux vaut 1 : on monte forcément.
- Les fractions du temps passé dans les états 0, 1 et 2 estiment π₀, π₁ et π₂ ; la moyenne de n pondérée par le temps estime L.

**`main()`**, bloc par bloc.

1. Les six mesures pour λ = 3 et μ = 4, vérifiées par `assert` contre 0,75 / 0,25 / 3 / 2,25 / 1 / 0,75, plus W = 1/(μ − λ), Wq = W − 1/μ et L = Lq + ρ.
2. La loi πₙ : π₁ = 0,1875, π₂ = 0,140625. On somme les 400 premiers termes : 1 pour la masse totale, 3 pour la moyenne (ρ⁴⁰⁰ est négligeable). La queue au-delà de 4 vaut ρ⁴ = 0,3164.
3. Sur 400 000 sauts avec la graine 70, le temps passé dans les états 0, 1 et 2 vaut 0,2494, 0,1876 et 0,1408, contre 0,25, 0,1875 et 0,1406 en théorie ; L simulé vaut 3,020.
4. Les quantiles du temps de réponse : 0,693 s (médiane), 2,303 s, 2,996 s (p95) et 4,605 s (p99).
5. Le dimensionnement : μ ≥ 5 pour la moyenne, μ ≥ 5,9957 pour le p95, soit un service moyen d'au plus 0,1668 s.
6. De ρ = 0,8 à ρ = 0,95, W passe de 1,25 s à 5 s, un rapport de 4 ; λ = μ est refusé.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`file_mm1(lambda_rate, mu_rate)`** — Cette fonction est le métreur qui relève d'un seul passage toutes les mesures d'un guichet M/M/1 : elle reçoit le débit d'arrivée λ et le débit de service μ, lève une `ValueError` si l'un d'eux n'est pas strictement positif, puis une autre si λ ≥ μ, car le système serait instable, et calcule ensuite ρ = λ/μ, la probabilité P₀ = 1 − ρ que le guichet soit vide, L = ρ/(1 − ρ) et Lq = ρ²/(1 − ρ), avant de tirer W et Wq de la loi de Little en divisant par λ. Elle renvoie ces six valeurs dans un dictionnaire : pour λ = 3 et μ = 4, ρ = 0,75, P₀ = 0,25, L = 3, Lq = 2,25, W = 1 s et Wq = 0,75 s.

**`pi_n(n, rho)`** — Celle-ci répond à la question qu'un gérant poserait en jetant un coup d'œil à la salle à un instant pris au hasard : quelle est la probabilité d'y trouver exactement n requêtes ? Elle reçoit n et la charge ρ, et renvoie (1 − ρ)ρⁿ, la loi géométrique stationnaire de la file, sans aucun contrôle sur ρ. Pour ρ = 0,75, elle donne 0,25 pour une salle vide, 0,1875 pour une requête et 0,140625 pour deux, et `main` vérifie que ses 400 premiers termes somment à 1 et que leur moyenne pondérée vaut 3.

**`residu_equilibre(lam, mu, n_max)`** — Cette fonction est le vérificateur des comptes qui contrôle, état par état, que ce qui sort égale ce qui entre au lieu de le croire : elle reçoit λ, μ et le dernier état à examiner, compare pour l'état 0 le flux sortant λπ₀ au flux entrant μπ₁, puis, pour chaque état n de 1 à n_max, le flux sortant (λ + μ)πₙ au flux entrant λπₙ₋₁ + μπₙ₊₁. Elle renvoie le plus grand écart rencontré, qui vaut 2,7 × 10⁻²⁰ sur les cinquante premiers états, autrement dit zéro aux arrondis près, ce qui prouve que la loi de `pi_n` résout bien les équations d'équilibre.

**`quantile_sejour(lam, mu, p)`** — Celle-ci est l'horloger qui promet un délai à un client inquiet : elle reçoit λ, μ et une proportion p, refuse par une `ValueError` toute proportion qui n'est pas strictement comprise entre 0 et 1, puis renvoie −ln(1 − p)/(μ − λ), le temps sous lequel ressortent une fraction p des requêtes, puisque le séjour d'une M/M/1 servie dans l'ordre d'arrivée suit une loi exponentielle de taux μ − λ. Avec un taux de 1 par seconde, la médiane vaut 0,693 s, le p95 2,996 s, soit ln 20, et le p99 4,605 s ; elle ne vérifie pas elle-même que λ < μ.

**`mu_minimal(lam, W_cible, t95_cible)`** — Cette fonction est l'ingénieur de dimensionnement qui cherche la cadence de service minimale pour tenir une promesse : elle reçoit λ et, au choix, une cible de séjour moyen, une cible de p95, ou les deux, toutes deux absentes par défaut. Elle part de λ, ajoute à la liste des besoins λ + 1/W pour la moyenne et λ + ln 20/t₉₅ pour le p95, puis renvoie le plus grand de ces seuils, celui de la contrainte la plus forte ; à λ = 3, la moyenne de 0,5 s exige μ ≥ 5, le p95 d'une seconde μ ≥ 5,9957, et c'est ce second seuil qui l'emporte quand on fournit les deux.

**`simuler_chaine(lam, mu, n_sauts, graine)`** — Celle-ci fait vivre la chaîne de naissance et de mort comme un pion qui monte ou descend d'une marche sur un escalier sans fin : elle reçoit λ, μ, un nombre de sauts et une graine, reste dans chaque état un temps exponentiel de taux λ + μ, ou λ seul dans l'état 0 où aucun départ n'est possible, cumule ce temps par état, puis monte avec la probabilité λ divisée par ce taux et descend sinon. Elle renvoie la fraction du temps passée dans les états 0, 1 et 2, et le nombre moyen de présents pondéré par le temps ; avec la graine 70 et 400 000 sauts, elle trouve 0,2494 pour l'état vide et un L simulé de 3,020, contre 0,25 et 3 en théorie.

**`main()`** — C'est le directeur d'études qui fait passer la file par six épreuves : il vérifie d'abord les six mesures de `file_mm1` à λ = 3 et μ = 4, ainsi que les liens W = 1/(μ − λ), Wq = W − 1/μ et L = Lq + ρ, puis la loi πₙ, sa masse totale 1, sa moyenne 3, le résidu d'équilibre et la queue ρ⁴ = 0,3164. Il compare ensuite la chaîne simulée à la théorie à 0,01 près pour chaque état et à 0,15 près pour L, affiche les quantiles du séjour, dimensionne μ pour les deux SLA, et termine en montrant que W passe de 1,25 s à 5 s quand ρ va de 0,8 à 0,95, avant de vérifier que λ = μ = 4 est refusé.

```python
"""Étape 70 — file M/M/1 : équilibre de la chaîne, πₙ = (1−ρ)ρⁿ, L, Little, W, et dimensionnement sur un SLA."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def file_mm1(lambda_rate: float, mu_rate: float) -> dict[str, float]:
    """Les six mesures d'une file M/M/1 stable."""
    if lambda_rate <= 0 or mu_rate <= 0:
        raise ValueError("il faut λ > 0 et μ > 0")
    if lambda_rate >= mu_rate:
        raise ValueError("Système instable : λ ≥ μ")
    rho = lambda_rate / mu_rate
    P0 = 1 - rho
    L = rho / (1 - rho)                  # = Σ n πₙ
    Lq = rho ** 2 / (1 - rho)            # = Σ (n − 1) πₙ pour n ≥ 1
    W = L / lambda_rate                  # Little
    Wq = Lq / lambda_rate                # Little sur la file
    return {"rho": rho, "P0": P0, "L": L, "Lq": Lq, "W": W, "Wq": Wq}


def pi_n(n: int, rho: float) -> float:
    """Probabilité stationnaire d'avoir n requêtes dans le système : (1 − ρ) ρⁿ."""
    return (1 - rho) * rho ** n


def residu_equilibre(lam: float, mu: float, n_max: int) -> float:
    """Plus grand écart entre flux sortant et flux entrant, pour les états 0 … n_max."""
    rho = lam / mu
    pire = abs(lam * pi_n(0, rho) - mu * pi_n(1, rho))                      # état 0
    for n in range(1, n_max + 1):
        sortant = (lam + mu) * pi_n(n, rho)
        entrant = lam * pi_n(n - 1, rho) + mu * pi_n(n + 1, rho)
        pire = max(pire, abs(sortant - entrant))
    return pire


def quantile_sejour(lam: float, mu: float, p: float) -> float:
    """Le séjour d'une M/M/1 FIFO suit une loi exponentielle de taux μ − λ : t_p = −ln(1 − p) / (μ − λ)."""
    if not 0 < p < 1:
        raise ValueError("il faut 0 < p < 1")
    return -math.log(1 - p) / (mu - lam)


def mu_minimal(lam: float, W_cible: float | None = None, t95_cible: float | None = None) -> float:
    """Plus petit μ qui tient un SLA sur la moyenne (W ≤ W_cible) et/ou sur le p95 du séjour."""
    besoins = [lam]
    if W_cible is not None:
        besoins.append(lam + 1 / W_cible)                  # 1/(μ − λ) ≤ W  ⇔  μ ≥ λ + 1/W
    if t95_cible is not None:
        besoins.append(lam + math.log(20) / t95_cible)     # ln(20)/(μ − λ) ≤ t95
    return max(besoins)


def simuler_chaine(lam: float, mu: float, n_sauts: int, graine: int) -> tuple[list[float], float]:
    """Chaîne de naissance et de mort, horloge simulée. Renvoie la fraction du temps passée dans 0, 1, 2 et L."""
    rng = random.Random(graine)
    n, temps_total = 0, 0.0
    temps_par_etat: dict[int, float] = {}
    for _ in range(n_sauts):
        taux = lam + (mu if n > 0 else 0.0)
        duree = rng.expovariate(taux)              # temps passé dans l'état n avant le prochain saut
        temps_par_etat[n] = temps_par_etat.get(n, 0.0) + duree
        temps_total += duree
        n = n + 1 if rng.random() < lam / taux else n - 1
    fractions = [temps_par_etat.get(k, 0.0) / temps_total for k in range(3)]
    L = sum(k * t for k, t in temps_par_etat.items()) / temps_total
    return fractions, L


def main() -> None:
    lam, mu = 3.0, 4.0
    print("1. Les six mesures pour λ = 3 req/s, μ = 4 req/s")
    m = file_mm1(lam, mu)
    for cle in ("rho", "P0", "L", "Lq", "W", "Wq"):
        print(f"  {cle:<3} = {m[cle]:.4f}")
    attendu = {"rho": 0.75, "P0": 0.25, "L": 3.0, "Lq": 2.25, "W": 1.0, "Wq": 0.75}
    for cle, valeur in attendu.items():
        assert abs(m[cle] - valeur) < 1e-12, cle
    assert abs(m["W"] - 1 / (mu - lam)) < 1e-12 and abs(m["Wq"] - (m["W"] - 1 / mu)) < 1e-12
    assert abs(m["L"] - (m["Lq"] + m["rho"])) < 1e-12

    print("2. La loi stationnaire πₙ = (1 − ρ) ρⁿ")
    rho = m["rho"]
    for n in range(4):
        print(f"  π{n} = {pi_n(n, rho):.6f}")
    print(f"  P(N ≥ 4) = ρ⁴ = {rho ** 4:.4f}")
    total = sum(pi_n(n, rho) for n in range(400))
    moyenne = sum(n * pi_n(n, rho) for n in range(400))
    print(f"  Σ πₙ = {total:.6f}   Σ n πₙ = {moyenne:.6f}   résidu d'équilibre max = {residu_equilibre(lam, mu, 50):.1e}")
    assert abs(pi_n(1, rho) - 0.1875) < 1e-12 and abs(pi_n(2, rho) - 0.140625) < 1e-12
    assert abs(total - 1) < 1e-12 and abs(moyenne - m["L"]) < 1e-9
    assert residu_equilibre(lam, mu, 50) < 1e-15
    assert abs(sum(pi_n(n, rho) for n in range(4, 400)) - rho ** 4) < 1e-12

    print("3. La chaîne simulée (graine 70, 400 000 sauts, horloge simulée)")
    fractions, L_sim = simuler_chaine(lam, mu, 400_000, graine=70)
    for n, f in enumerate(fractions):
        print(f"  temps passé dans l'état {n} : {f:.4f}   (théorie {pi_n(n, rho):.4f})")
        assert abs(f - pi_n(n, rho)) < 0.01
    print(f"  L simulé = {L_sim:.3f}   (théorie 3)")
    assert abs(L_sim - 3.0) < 0.15

    print("4. Le séjour est exponentiel de taux μ − λ = 1 par seconde")
    for p in (0.50, 0.90, 0.95, 0.99):
        print(f"  {p:.0%} des requêtes ressortent en moins de {quantile_sejour(lam, mu, p):.3f} s")
    assert abs(quantile_sejour(lam, mu, 0.95) - math.log(20)) < 1e-12
    assert abs(quantile_sejour(lam, mu, 0.50) - math.log(2)) < 1e-12

    print("5. Dimensionner μ pour un SLA, à λ = 3 req/s")
    mu_moy = mu_minimal(lam, W_cible=0.5)
    mu_p95 = mu_minimal(lam, t95_cible=1.0)
    print(f"  W ≤ 0.5 s      → μ ≥ {mu_moy:.4f} req/s   (service moyen ≤ {1 / mu_moy:.4f} s)")
    print(f"  p95 ≤ 1.0 s    → μ ≥ {mu_p95:.4f} req/s   (service moyen ≤ {1 / mu_p95:.4f} s)")
    assert mu_moy == 5.0 and abs(mu_p95 - (3 + math.log(20))) < 1e-12
    assert mu_minimal(lam, W_cible=0.5, t95_cible=1.0) == mu_p95

    print("6. De ρ = 0.8 à ρ = 0.95, μ = 4 fixé")
    w80, w95 = file_mm1(3.2, 4.0)["W"], file_mm1(3.8, 4.0)["W"]
    print(f"  W(0.80) = {w80:.2f} s   W(0.95) = {w95:.2f} s   rapport = {w95 / w80:.1f}")
    assert abs(w80 - 1.25) < 1e-9 and abs(w95 - 5.0) < 1e-9 and abs(w95 / w80 - 4.0) < 1e-9
    try:
        file_mm1(4.0, 4.0)
    except ValueError as e:
        print(f"  λ = μ = 4 → {e}")
    else:
        raise AssertionError("λ = μ aurait dû être refusé")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Les six mesures pour λ = 3 req/s, μ = 4 req/s
  rho = 0.7500
…
  Wq  = 0.7500
2. La loi stationnaire πₙ = (1 − ρ) ρⁿ
  π1 = 0.187500
  π2 = 0.140625
  P(N ≥ 4) = ρ⁴ = 0.3164
  Σ πₙ = 1.000000   Σ n πₙ = 3.000000   résidu d'équilibre max = 2.7e-20
3. La chaîne simulée (graine 70, 400 000 sauts, horloge simulée)
  temps passé dans l'état 0 : 0.2494   (théorie 0.2500)
  L simulé = 3.020   (théorie 3)
4. Le séjour est exponentiel de taux μ − λ = 1 par seconde
  95% des requêtes ressortent en moins de 2.996 s
5. Dimensionner μ pour un SLA, à λ = 3 req/s
  W ≤ 0.5 s      → μ ≥ 5.0000 req/s   (service moyen ≤ 0.2000 s)
  p95 ≤ 1.0 s    → μ ≥ 5.9957 req/s   (service moyen ≤ 0.1668 s)
6. De ρ = 0.8 à ρ = 0.95, μ = 4 fixé
  W(0.80) = 1.25 s   W(0.95) = 5.00 s   rapport = 4.0
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : les formules de M/M/1 ne sont pas à apprendre par cœur. Elles sortent de deux équations d'équilibre et d'une série géométrique, et une chaîne simulée sans aucune formule retombe sur les mêmes nombres.

## Squelette algorithmique

Deux familles d'algorithmes se partagent ce fichier. Le calcul analytique reçoit λ et μ (et, pour le dimensionnement, un objectif de séjour moyen ou de p95) ; il rend les six mesures, les quantiles du temps de réponse et le plus petit μ qui tient le SLA. L'idée est de tout tirer de ρ = λ/μ et de la loi de Little, sans recopier une formule par mesure. La simulation à événements discrets reçoit λ, μ, un nombre de sauts et une graine ; elle rend la fraction du temps passée dans chaque état et le nombre moyen de présents. Son idée est de faire vivre la chaîne de naissance et de mort elle-même : rester dans l'état n un temps exponentiel, puis monter ou descendre d'une marche.

```text
ALGORITHME MesuresMM1                 (calcul analytique)
ENTRÉES : λ > 0, μ > 0
SORTIE : ρ, P0, L, Lq, W, Wq
  SI λ ≥ μ ALORS
    ÉCHOUER « système instable »               // la série Σ ρⁿ diverge
  FIN SI
  ρ ← λ / μ
  P0 ← 1 − ρ
  L ← ρ / (1 − ρ)                              // Σ n (1 − ρ) ρⁿ
  Lq ← ρ² / (1 − ρ)                            // L − (1 − P0)
  RETOURNER (ρ, P0, L, Lq, L / λ, Lq / λ)      // Little donne W et Wq

ALGORITHME QuantileSéjour
ENTRÉES : λ < μ, une probabilité p avec 0 < p < 1
SORTIE : t tel qu'une fraction p des requêtes ressorte en moins de t
  RETOURNER −ln(1 − p) / (μ − λ)

ALGORITHME MuMinimal                  (dimensionnement)
ENTRÉES : λ, éventuellement W_cible et t95_cible
SORTIE : le plus petit μ qui respecte toutes les cibles données
  besoins ← [λ]
  SI W_cible est donné ALORS
    ajouter λ + 1 / W_cible à besoins
  FIN SI
  SI t95_cible est donné ALORS
    ajouter λ + ln(20) / t95_cible à besoins
  FIN SI
  RETOURNER le maximum de besoins

ALGORITHME SimulerChaîne              (simulation à événements discrets)
ENTRÉES : λ, μ, nombre de sauts m, graine
SORTIE : fraction du temps passée dans chaque état, L simulé
  n ← 0 ; temps_total ← 0 ; temps_par_état ← table vide
  POUR k DE 1 À m FAIRE
    SI n > 0 ALORS taux ← λ + μ SINON taux ← λ FIN SI
    durée ← tirage exponentiel de taux « taux »
    temps_par_état[n] ← temps_par_état[n] + durée
    temps_total ← temps_total + durée
    SI tirage uniforme < λ / taux ALORS
      n ← n + 1                                // une arrivée
    SINON
      n ← n − 1                                // une fin de service
    FIN SI
  FIN POUR
  RETOURNER (temps_par_état[i] / temps_total pour chaque i, Σ i × temps_par_état[i] / temps_total)
```

**Complexité :** `MesuresMM1`, `QuantileSéjour` et `MuMinimal` font un nombre fixe d'opérations : O(1) en temps et en mémoire. Les vérifications du programme somment les 400 premiers πₙ et contrôlent les équations d'équilibre sur 50 états : O(N) pour N états, ce qui est négligeable. `SimulerChaîne` fait deux tirages et quelques additions par saut, soit O(m) en temps ; sa table ne garde qu'une case par état visité, donc O(n_max) en mémoire, où n_max est la plus longue file atteinte pendant la simulation (quelques dizaines à ρ = 0,75, bien moins que les 400 000 sauts).

**Du squelette au code :** `MesuresMM1` est `file_mm1`, qui calcule L et Lq à partir de ρ puis divise par `lambda_rate` pour W et Wq ; la loi πₙ qui justifie L et Lq est `pi_n`, et `residu_equilibre` vérifie qu'elle satisfait les équations d'équilibre. `QuantileSéjour` est `quantile_sejour`. `MuMinimal` est `mu_minimal`, dont la liste `besoins` et le `max(besoins)` sont les lignes du pseudo-code. `SimulerChaîne` est `simuler_chaine` : le `SI n > 0` est l'expression `lam + (mu if n > 0 else 0.0)`, le tirage exponentiel est `rng.expovariate(taux)`, le choix « arrivée ou départ » est la ligne `n = n + 1 if rng.random() < lam / taux else n - 1`, et les deux moyennes finales sont `fractions` et `L`.

## Cas d'usage réels aux Émirats

Les débits, durées et seuils ci-dessous sont illustratifs : en production, on les mesure sur les journaux de chaque service, et l'on vérifie d'abord que les durées de service sont proches d'une exponentielle (sinon, étape 68).

### Banque — un agent unique de contrôle des virements, dimensionné sur le p95

Une banque de détail de Dubaï fait passer les virements entrants de ses clients professionnels par un agent qui vérifie l'IBAN AE (contrôle mod 97), rapproche le nom du bénéficiaire et signale les écarts. Pour garantir l'ordre de traitement des opérations d'un même compte, un seul agent les traite, l'un après l'autre : la file est M/M/1. Il reçoit 2 virements par seconde au pic et en traite 2,5 : ρ = 0,8, W = 1/0,5 = 2 s, mais le p95 vaut ln 20/0,5 ≈ 6 s. L'engagement de service porte sur le p95, à 3 s : il faut μ ≥ 2 + 2,996/3 ≈ 3 virements par seconde, soit un traitement moyen d'au plus 0,333 s au lieu de 0,4 s. L'équipe obtient ce gain en sortant le contrôle mod 97 du prompt (un outil déterministe le fait en quelques microsecondes) et en ne gardant au modèle que le rapprochement des noms, souvent translittérés de plusieurs façons depuis l'arabe. Dimensionner sur la moyenne aurait laissé un virement sur vingt dépasser 6 s. L'indicateur suivi est le p95 du temps de réponse par tranche de cinq minutes.

### Immobilier — combien de prospects attendent l'agent de qualification

Une agence immobilière de Dubaï fait qualifier les demandes de son site par un agent unique, branché sur le CRM, qui demande le budget en AED, la zone et le type de bien avant de transmettre à un conseiller. Il arrive en moyenne une demande toutes les 10 s, et l'agent en traite une en 8 s : λ = 0,1, μ = 0,125, ρ = 0,8. En moyenne, L = 4 prospects sont présents et Lq = 3,2 attendent, pour un séjour de 1/(0,125 − 0,1) = 40 s, dont 32 s d'attente. La probabilité qu'un nouveau prospect trouve au moins 6 personnes devant lui vaut 0,8⁶ ≈ 0,26 : une fois sur quatre, l'attente dépasse largement la moyenne. La décision est d'afficher un message d'attente dès que 4 prospects sont présents, et de basculer vers un formulaire de rappel au-delà de 6. Sans ce garde-fou, les prospects des heures de pointe, souvent ceux qui comparent plusieurs projets off-plan, ferment la page. L'indicateur suivi est le taux d'abandon en fonction du nombre de personnes présentes à l'arrivée.

### Assurance — la part du temps libre pour les tâches de fond

Un assureur auto et santé fait instruire les déclarations de sinistre par un agent unique pendant la journée : 40 déclarations par heure, 50 traitées par heure, donc ρ = 0,8. P₀ = 0,2 veut dire que l'agent est libre 12 minutes par heure en moyenne, et l'équipe voulait y glisser un recalcul des scores de fraude qui demande 15 minutes de calcul par heure. Le bilan du travail règle la question sans simulation : 48 minutes de sinistres plus 15 minutes de fraude font 63 minutes de travail par heure, plus que les 60 disponibles, et la file deviendrait instable. La décision est de déplacer le recalcul la nuit, quand λ tombe, ou de lui donner une instance dédiée. Sans ce calcul, la tâche de fond aurait pris la capacité des sinistres, et les déclarations urgentes se seraient accumulées en fin de journée. Les décisions de sinistre restent traçables, comme l'attend la supervision de la CBUAE ; l'indicateur suivi est P₀ mesuré, comparé à 1 − ρ.

### RH — un calcul de fin de service qui doit rester sous la minute

Un cabinet RH présent dans plusieurs émirats fait calculer par un agent l'indemnité de fin de service des salariés qui quittent leurs entreprises clientes : 21 jours de salaire de base par an les cinq premières années, 30 jours au-delà, au prorata, avec le plafond de 24 mois. L'agent reçoit une demande par minute et met 40 s à rassembler le dossier et rédiger la lettre : μ = 1,5 par minute, ρ = 0,67 et W = 1/(1,5 − 1) = 2 minutes. Le service client veut une réponse en moins d'une minute en moyenne : il faut μ ≥ 1 + 1/1 = 2 par minute, donc un traitement de 30 s au plus. L'équipe y parvient en faisant calculer le montant par l'outil déterministe du parcours, et en ne demandant au modèle que la lettre, sur un gabarit fixe. Sans ce calcul, elle aurait accepté 40 s « parce que c'est moins d'une minute », sans voir que l'attente ajoute 80 s. Le montant est vérifié contre le texte en vigueur avant tout envoi ; l'indicateur suivi est W, avec le taux de lettres corrigées par un humain.

### BTP — une licence d'outil de métrés partagée par tous les devis

Un groupe de construction de Dubaï fait préparer ses devis par un agent qui appelle un logiciel de métrés, dont l'entreprise n'a qu'une licence : un seul devis peut être calculé à la fois. Les équipes demandent 6 devis par heure, et l'outil en produit 8 : ρ = 0,75, W = 1/(8 − 6) = 0,5 h, soit 30 minutes, dont 22,5 minutes d'attente. Un nouveau directeur de projet ajoute 1,5 devis par heure : ρ = 0,94 et W = 1/(8 − 7,5) = 2 heures, quatre fois plus pour 25 % de demandes en plus. La décision chiffrée est de comparer le prix d'une deuxième licence au coût de deux heures d'attente par devis, plutôt que d'en débattre. Les devis portent la TVA à 5 % et les retenues de garantie du contrat, que l'agent calcule par outil et non par le modèle. L'indicateur suivi est le séjour moyen d'un devis et le ρ de la licence.

### Secteur public — une attente affichée honnêtement

Une entité de services publics en ligne, accessible par UAE Pass, fait traiter les demandes d'attestation par un agent unique, qui interroge un registre en arabe et en anglais puis rédige le document. Le portail affiche à l'usager le nombre de demandes devant lui et un temps d'attente estimé. Comme le service est sans mémoire, une demande qui en trouve n devant elle attend en moyenne n/μ : le reste du service en cours compte comme un service complet. Avec un traitement de 2 s (μ = 0,5) et 5 demandes devant, l'estimation honnête est de 10 s, et l'on peut annoncer « 95 % des demandes sont servies en moins de » ln 20/(μ − λ) secondes. La PDPL s'applique : l'affichage ne montre ni nom ni numéro d'Emirates ID, seulement une position dans la file. Sans cette estimation, le portail affichait un délai fixe de 30 s, faux dans les deux sens, et les usagers relançaient leur demande, ce qui augmentait λ. L'indicateur suivi est l'écart entre l'attente affichée et l'attente réelle.

## Pièges et limites

- **Appliquer M/M/1 à un service qui n'est pas exponentiel.** La moyenne change (Pollaczek-Khinchine, étape 68), et la loi exponentielle du temps de réponse ne tient plus : le p95 n'est plus ln 20 × W.
- **Dimensionner sur la moyenne.** Le p95 vaut environ trois fois W ; un SLA sur le p95 demande bien plus de marge μ − λ.
- **Calculer W quand ρ ≥ 1.** Il n'y a pas de régime stable : la fonction doit refuser, pas renvoyer un nombre négatif (1/(μ − λ) < 0 si λ > μ).
- **Confondre W et Wq, L et Lq.** Wq = W − 1/μ et Lq = L − ρ : la différence est le service lui-même.
- **Oublier que l'agent unique est un point de panne.** M/M/1 décrit la latence, pas la disponibilité : voir l'étape 49 pour la disponibilité et l'étape 71 pour plusieurs instances.

### Exercice feuille blanche

1. Sans regarder le code, écrire `file_mm1` à partir des équations d'équilibre : poser πₙ = ρⁿπ₀, normaliser, calculer L, puis W et Wq par Little. Vérifier avec λ = 3 et μ = 4.
2. Prédire, puis vérifier : avec λ = 3,5 et μ = 4, que valent ρ, L, W, Wq et le p95 ? (Réponse : 0,875 ; 7 ; 2 s ; 1,75 s ; ln 20/0,5 ≈ 5,99 s.)
3. Trouver le bug : `Wq = Lq / mu_rate`. Quelle valeur obtient-on pour λ = 3 et μ = 4, et quelle loi a été mal appliquée ?

## Pour aller plus loin

Avec une capacité K finie (M/M/1/K), la même chaîne s'arrête à l'état K : πₙ est proportionnel à ρⁿ pour n ≤ K, ρ peut alors dépasser 1, et πₖ est la probabilité de refus. La durée moyenne d'une période d'activité vaut 1/(μ − λ). Le théorème de Burke dit que les départs d'une M/M/1 stable forment encore un processus de Poisson de taux λ, ce qui permet d'enchaîner des files M/M/1 en réseau (réseaux de Jackson), comme une chaîne d'agents spécialisés.

> Suite : [Erlang C et file M/M/c](<71-Erlang-C.md>) — étape 71.
