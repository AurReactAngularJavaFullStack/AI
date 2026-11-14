# Étape 71 — Formule d'Erlang C et File M/M/c

> Étape 71 du parcours · Prérequis : [File M/M/1](<70-File-MM1.md>) · Suite : [Coûts et gestion des tokens](<72-Couts-et-Gestion-des-Tokens.md>)

**Dossier :** 12-Production-Couts-Optimisation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, AI Platform Team, Forward-Deployed Engineers  
**Nom du fichier :** 71-Erlang-C.md

## Définition

La file M/M/c décrit c agents identiques qui se partagent une seule file : les requêtes arrivent selon un processus de Poisson de taux λ, chaque agent traite une requête en un temps exponentiel de moyenne 1/μ, et une requête n'attend que si les c agents sont tous occupés. La formule d'Erlang C, établie par Agner Krarup Erlang pour dimensionner les standards téléphoniques, donne la probabilité de ce « tous occupés », c'est-à-dire la probabilité qu'une requête qui arrive doive attendre. Elle se note C(c, a), où a = λ/μ est le trafic offert, mesuré en erlangs. De C(c, a) découlent l'attente moyenne, le temps de séjour et la loi complète de l'attente. C'est l'outil standard pour choisir le nombre d'instances d'un agent qui respecte un SLA.

## Rôle dans un agent

Dès qu'un agent tourne en plusieurs répliques derrière une même file (un pool de pods, plusieurs connexions au fournisseur de modèle, plusieurs agents vocaux), M/M/1 ne suffit plus. Dans la boucle percevoir → décider → agir → observer, c'est l'« agir » qui consomme une instance. Erlang C sert à l'**ordonnanceur** et à l'autoscaler pour choisir c avant un pic connu, au **garde-fou de débit** pour savoir à partir de quel débit il faut refuser ou différer, et au tableau de bord d'**observation** pour traduire un SLA (« moins de 5 % des requêtes attendent plus de 0,2 s ») en nombre d'instances. Après cette étape, relire l'étape 49 ([score de disponibilité](<../09-MCP/49-MCP-Formule-Score-de-Disponibilite.md>)) : une instance « disponible » est une instance dont la file n'est pas saturée.

## Équation complète

Trafic offert et utilisation :

$$
a = \frac{\lambda}{\mu}, \qquad \rho = \frac{a}{c} = \frac{\lambda}{c\,\mu} < 1
$$

Loi stationnaire du nombre de requêtes présentes :

$$
\pi_n = \pi_0\, \frac{a^n}{n!} \quad (n \le c),
\qquad
\pi_n = \pi_0\, \frac{a^c}{c!}\, \rho^{\,n-c} \quad (n \ge c)
$$

$$
\pi_0 = \left( \sum_{k=0}^{c-1} \frac{a^k}{k!} + \frac{a^c}{c!} \cdot \frac{1}{1-\rho} \right)^{-1}
$$

Probabilité d'attente (Erlang C) :

$$
C(c, a) = \frac{\frac{a^c}{c!} \cdot \frac{c}{c - a}}{\sum_{k=0}^{c-1} \frac{a^k}{k!} + \frac{a^c}{c!} \cdot \frac{c}{c - a}}
$$

Nombre moyen en file, attente moyenne et séjour moyen :

$$
L_q = C(c, a)\, \frac{\rho}{1-\rho}
\qquad
W_q = \frac{C(c, a)}{c \mu - \lambda}
\qquad
W = W_q + \frac{1}{\mu}
$$

Probabilité d'attendre plus de t secondes :

$$
P(W_q > t) = C(c, a) \cdot e^{-(c\mu - \lambda) t}
$$

Récurrence stable d'Erlang B, puis passage à Erlang C :

$$
B(0, a) = 1, \qquad B(k, a) = \frac{a\, B(k-1, a)}{k + a\, B(k-1, a)}
$$

$$
C(c, a) = \frac{B(c, a)}{1 - \rho\,\bigl(1 - B(c, a)\bigr)}
$$

## Décryptage des symboles

$$
\lambda
$$

Taux d'arrivée des requêtes sur l'ensemble du pool, en requêtes par seconde · variable Python : `lambda_rate` (ou `lam`).

$$
\mu
$$

Taux de service d'**une** instance, en requêtes par seconde ; 1/μ est la durée moyenne d'un traitement · variable Python : `mu_rate` (ou `mu`).

$$
c
$$

Nombre d'instances identiques qui servent la même file, entier ≥ 1 · variable Python : `c`.

$$
a
$$

Trafic offert λ/μ, en erlangs : le nombre moyen d'instances qui seraient occupées s'il n'y avait jamais d'attente. 12 arrivées par seconde qui demandent chacune un quart de seconde font 3 secondes de travail par seconde, donc a = 3. Ce n'est pas un pourcentage · variable Python : `a`.

$$
\rho
$$

Utilisation par instance, a/c, dans [0 ; 1[ pour un système stable · variable Python : `rho`.

$$
\pi_n
$$

Probabilité stationnaire d'avoir n requêtes présentes, en service ou en attente · calculée dans `residu_equilibre`.

$$
\pi_0
$$

Probabilité que tout le système soit vide. Avec plusieurs instances, ce n'est pas 1 − ρ : « vide » est bien plus rare que « pas saturé » · variable Python : `m["P0"]`.

$$
C(c, a)
$$

Probabilité qu'une requête qui arrive trouve les c instances occupées et doive attendre (Erlang C) · variable Python : `m["C"]`.

$$
B(c, a)
$$

Probabilité de refus d'un système à c instances **sans** file (Erlang B) : une requête qui trouve tout occupé est perdue. Ici, elle sert d'intermédiaire de calcul stable · variable Python : `erlang_b(c, a)`, `m["B"]`.

$$
L_q
$$

Nombre moyen de requêtes en attente · variable Python : `m["Lq"]`.

$$
W_q
$$

Attente moyenne avant le début du traitement, en secondes, sur **toutes** les requêtes, y compris celles qui n'attendent pas · variable Python : `m["Wq"]`.

$$
W
$$

Temps de séjour moyen, attente plus traitement · variable Python : `m["W"]`.

$$
t
$$

Seuil de temps d'un SLA, en secondes (par exemple 0,2 s) · variable Python : `t`.

## Démonstration

### 1. La chaîne de naissance et de mort à c serveurs

Comme à l'étape 70, l'absence de mémoire des deux lois exponentielles fait du nombre n de requêtes présentes une chaîne de Markov. Elle monte de n à n + 1 au taux λ. Elle descend de n à n − 1 au taux min(n, c) μ : si n ≤ c, les n requêtes sont toutes en service, chacune sur une instance, et la première fin parmi n durées exponentielles indépendantes de taux μ arrive au taux nμ, parce que la probabilité qu'aucune ne soit finie à l'instant t vaut

$$
\left(e^{-\mu t}\right)^n = e^{-n \mu t}
$$

ce qui est la loi exponentielle de taux nμ ; si n > c, seules c requêtes sont en service et le taux plafonne à cμ.

### 2. Les équations de coupure, et leur solution

Le même raisonnement qu'à l'étape 70 (point 3) donne, pour chaque coupure entre les états {0, …, n − 1} et {n, n + 1, …}, autant de flux dans un sens que dans l'autre :

$$
\lambda\, \pi_{n-1} = \min(n, c)\, \mu\, \pi_n
$$

Pour n ≤ c, on en tire πₙ = (a/n) πₙ₋₁, et en enchaînant les rapports a/1 × a/2 × … × a/n :

$$
\pi_n = \pi_0\, \frac{a^n}{n!} \qquad (n \le c)
$$

Pour n > c, le rapport devient constant, a/c = ρ, donc la loi devient géométrique au-delà de c :

$$
\pi_n = \pi_c\, \rho^{\,n-c} = \pi_0\, \frac{a^c}{c!}\, \rho^{\,n-c} \qquad (n \ge c)
$$

### 3. Normalisation : la file repliée en un seul terme

On somme toutes les probabilités et l'on impose que le total vaille 1. Les états 0 à c − 1 donnent la somme de Poisson tronquée ; les états c, c + 1, … donnent une série géométrique de raison ρ, qui ne converge que si ρ < 1 :

$$
1 = \pi_0 \left( \sum_{k=0}^{c-1} \frac{a^k}{k!} + \frac{a^c}{c!} \sum_{j=0}^{\infty} \rho^j \right)
= \pi_0 \left( \sum_{k=0}^{c-1} \frac{a^k}{k!} + \frac{a^c}{c!} \cdot \frac{1}{1-\rho} \right)
$$

Comme ρ = a/c, on a 1/(1 − ρ) = c/(c − a) : c'est exactement le facteur de la formule d'origine. Il replie toute la file, de longueur c, c + 1, c + 2…, en un seul terme. Si on l'oublie, on ne compte que l'état « la c-ième instance vient d'être prise », sans les requêtes qui attendent derrière, et l'on obtient la formule d'Erlang B, qui vaut 0,2061 pour c = 4 et a = 3, au lieu de 0,5094.

### 4. Erlang C est la probabilité d'attendre

Une requête attend si elle trouve au moins c requêtes présentes. Par PASTA (étape 68), une arrivée de Poisson voit la loi stationnaire, donc

$$
C(c, a) = \sum_{n \ge c} \pi_n = \pi_0\, \frac{a^c}{c!} \cdot \frac{1}{1-\rho}
$$

En remplaçant π₀ par l'inverse de la somme du point 3, on retrouve la formule de l'équation complète.

### 5. Lq, Wq et W

Le nombre de requêtes en attente vaut n − c quand n ≥ c. On pose j = n − c, et l'on réutilise ∑ j ρʲ = ρ/(1 − ρ)², démontré à l'étape 70 (point 5) :

$$
L_q = \sum_{j=0}^{\infty} j\, \pi_c\, \rho^j = \pi_c\, \frac{\rho}{(1-\rho)^2} = C(c, a)\, \frac{\rho}{1-\rho}
$$

parce que πc/(1 − ρ) = C(c, a) d'après le point 4. Little sur la file donne

$$
W_q = \frac{L_q}{\lambda} = \frac{C(c, a)\, \rho}{\lambda (1-\rho)} = \frac{C(c, a)}{c\mu (1-\rho)} = \frac{C(c, a)}{c\mu - \lambda}
$$

parce que ρ/λ = 1/(cμ). Le dénominateur cμ − λ est la marge : la capacité de service qui reste une fois les arrivées servies. On ne fait pas attendre tout le monde pendant cette marge, seulement la fraction C qui a trouvé le système plein ; les autres sont servis tout de suite, avec une attente nulle. C'est pour cela qu'on multiplie par Erlang C, et qu'on ne réutilise pas le Wq de M/M/1. Enfin, toute requête attend puis est servie : W = Wq + 1/μ, et Little donne L = λW = Lq + a.

### 6. La loi de l'attente : P(Wq > t) = C · exp(−(cμ − λ)t)

Sachant qu'elle attend, une requête trouve j = n − c requêtes devant elle avec probabilité πc ρʲ / (πc/(1 − ρ)) = (1 − ρ) ρʲ : une loi géométrique. Elle doit attendre j + 1 fins de service. Tant que les c instances sont occupées, les fins de service forment un processus de Poisson de taux cμ (point 1). C'est la situation de l'étape 70 (point 7), avec cμ à la place de μ : un nombre géométrique d'étapes exponentielles, avec probabilité 1 − ρ que chaque étape soit la dernière, donne une attente exponentielle de taux cμ(1 − ρ) = cμ − λ. Donc

$$
P(W_q > t) = P(\text{attendre}) \cdot P(W_q > t \mid \text{attendre}) = C(c, a)\, e^{-(c\mu - \lambda)\, t}
$$

Vérification : la moyenne d'une exponentielle de taux cμ − λ vaut 1/(cμ − λ), et C × 1/(cμ − λ) redonne le Wq du point 5. La marge cμ − λ est donc aussi le taux auquel la file se vide une fois qu'elle existe.

### 7. Une récurrence qui ne déborde pas

La formule d'origine calcule aᶜ et c! séparément. Pour c = 200 et a = 150, aᶜ vaut environ 10⁴³⁵, bien au-delà du plus grand flottant (environ 1,8 × 10³⁰⁸) : `150.0 ** 200` lève `OverflowError`. On passe par Erlang B. Notons tₖ = aᵏ/k!, Eₖ = t₀ + … + tₖ et B(k) = tₖ/Eₖ. Comme Eₖ = Eₖ₋₁ + tₖ et tₖ = (a/k) tₖ₋₁ :

$$
\frac{1}{B(k)} = \frac{E_{k-1} + t_k}{t_k} = 1 + \frac{k}{a} \cdot \frac{E_{k-1}}{t_{k-1}} = 1 + \frac{k}{a\, B(k-1)}
\;\Longrightarrow\;
B(k) = \frac{a\, B(k-1)}{k + a\, B(k-1)}
$$

Tous les B(k) restent dans [0 ; 1] : aucun calcul intermédiaire ne déborde. Pour revenir à C, on écrit la somme des états 0 à c − 1 comme Ec(1 − B) et le dernier terme de la formule comme Ec B/(1 − ρ) ; le facteur Ec se simplifie :

$$
C = \frac{B/(1-\rho)}{(1 - B) + B/(1-\rho)} = \frac{B}{(1-\rho)(1-B) + B} = \frac{B}{1 - \rho\,(1 - B)}
$$

π₀ = 1/(Ec((1 − B) + B/(1 − ρ))) se calcule de même, en prenant le logarithme de Ec par la méthode « log-somme-exp », parce que π₀ peut être minuscule (7,2 × 10⁻⁶⁶ pour c = 200) sans être nul.

### 8. Exemple fait à la main (le code reprend ces nombres)

L'agent vocal : λ = 12 questions par seconde, μ = 4 par instance, c = 4. Alors a = 3 et ρ = 0,75.

- La somme `sum(a**k / factorial(k) for k in range(c))` additionne k = 0, 1, 2, 3, pas 4, parce que `range(c)` s'arrête avant c : 1 + 3 + 4,5 + 4,5 = 13. Ce sont les façons d'occuper 0, 1, 2 ou 3 instances, quand personne n'attend encore.
- Le dernier terme vaut a⁴/24 × c/(c − a) = 3,375 × 4 = 13,5.
- C = 13,5/(13 + 13,5) = 13,5/26,5 ≈ 0,5094 : un peu plus d'une question sur deux arrive alors que les quatre instances sont occupées. π₀ = 1/26,5 ≈ 0,0377, loin de 1 − ρ = 0,25.
- Par la récurrence : B(1) = 3/4 = 0,75 ; B(2) = 2,25/4,25 ≈ 0,5294 ; B(3) ≈ 1,5882/4,5882 ≈ 0,3462 ; B(4) ≈ 1,0385/5,0385 ≈ 0,2061 ; puis C = 0,2061/(1 − 0,75 × 0,7939) ≈ 0,5094. Même nombre.
- Wq = 0,5094/(16 − 12) ≈ 0,1274 s, W = 0,1274 + 0,25 ≈ 0,3774 s, Lq = 0,5094 × 3 ≈ 1,528.
- P(Wq > 0,2) = 0,5094 × e⁻⁰,⁸ ≈ 0,5094 × 0,4493 ≈ 0,2289.

Avec c = 5 : la somme vaut 13 + 3,375 = 16,375, le dernier terme 3⁵/120 × 5/2 = 5,0625, C = 5,0625/21,4375 ≈ 0,2362, Wq = 0,2362/8 ≈ 0,0295 s, W ≈ 0,2795 s, et P(Wq > 0,2) = 0,2362 × e⁻¹,⁶ ≈ 0,0477, soit 4,77 %.

**Correction d'un chiffre du cours.** Le fichier de fondements (étape 43) affirmait qu'avec 4 instances, « W ≈ 0,33 s, SLA de 0,35 s respecté ». Le calcul donne W = 0,127 + 0,25 = 0,377 s : le SLA de 0,35 s n'est **pas** respecté avec 4 instances. Il l'est avec 5 (0,2795 s), qui tiennent aussi l'objectif « moins de 5 % attendent plus de 0,2 s ».

## Effets et comportement

- **Ajouter une instance agit sur deux leviers à la fois.** C baisse (0,509 → 0,236 → 0,099 de c = 4 à 6) et la marge cμ − λ augmente (4 → 8 → 12), donc P(Wq > t) chute bien plus vite que linéairement : 22,9 %, 4,8 %, 0,9 %.
- **Les gros pools sont plus efficaces à charge égale.** À ρ = 0,75 et pour un service de 0,25 s, Wq vaut 0,75 s avec 1 instance, 0,127 s avec 4 et 0,013 s avec 16 ; avec 200 instances, l'attente tombe à environ un millionième du temps de service (bloc 4 du programme) : mutualiser une file entre beaucoup d'instances absorbe les aléas.
- **Le service ne raccourcit jamais sous 1/μ.** W tend vers 0,25 s quand c grandit ; au-delà d'un certain point, ajouter des instances ne sert plus, il faut accélérer le traitement.
- **ρ < 1 reste le mur.** À c = 3, ρ = 1 et la fonction refuse le calcul.
- **Wq est une moyenne sur tout le monde.** Les requêtes qui attendent attendent en moyenne 1/(cμ − λ) = 0,25 s à c = 4, deux fois le Wq global : le chiffre moyen cache la moitié des requêtes qui attendent vraiment.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| λ, μ, c | `lambda_rate`, `mu_rate`, `c` |
| a = λ/μ, ρ = a/c | `m["a"]`, `m["rho"]` |
| C(c, a), formule d'origine | `erlang_c_naif(c, lambda_rate, mu_rate)` |
| B(c, a) par récurrence | `erlang_b(c, a)` |
| C, π₀, Lq, Wq, W, L | clés du dictionnaire renvoyé par `erlang_c(c, lambda_rate, mu_rate)` |
| ln ∑ aᵏ/k! | `log_somme_poisson(c, a)` |
| P(Wq > t) | `p_attente_sup(c, lambda_rate, mu_rate, t)` |
| plus petit c pour un SLA | `dimensionner(lambda_rate, mu_rate, t, seuil, W_max)` |
| équations de coupure | `residu_equilibre(c, lambda_rate, mu_rate, n_max)` |

### Déroulé, ligne par ligne

**`erlang_c_naif`** est le code d'origine, gardé pour la comparaison.

- `a = lambda_rate / mu_rate` vaut 12/4 = 3.
- `sum(a ** k / math.factorial(k) for k in range(c))` additionne k = 0 à 3 : 13.
- `last_term = (a ** c / math.factorial(c)) * (c / (c - a))` vaut 3,375 × 4 = 13,5.
- Le résultat, 13,5/26,5 ≈ 0,5094, est juste pour un petit c. L'ancienne version calculait aussi `P0 = 1 / (sum_terms + last_term)` sans jamais le renvoyer (code mort) et importait `exp` sans s'en servir : la nouvelle version renvoie π₀ et utilise l'exponentielle dans `p_attente_sup`.

**`erlang_b(c, a)`** applique la récurrence du point 7 : `b = a * b / (k + a * b)`. Pour a = 3 : 0,75, 0,5294, 0,3462, puis 0,2061 à k = 4.

**`log_somme_poisson(c, a)`** calcule ln ∑ aᵏ/k! sans former aucun aᵏ. Chaque terme est remplacé par son logarithme, `k * math.log(a) - math.lgamma(k + 1)` (`math.lgamma(k + 1)` vaut ln k!). On soustrait le plus grand terme `m` avant de reprendre l'exponentielle, ce qui ramène tous les nombres sous 1, puis on rajoute `m`.

**`erlang_c(c, lambda_rate, mu_rate)`**, la fonction principale.

- `if rho >= 1` : le test ρ ≥ 1 est le même mur que λ ≥ cμ. À c = 3, ρ = 12/12 = 1 et l'on lève `ValueError`.
- `B = erlang_b(c, a)` vaut 0,2061, puis `C = B / (1 - rho * (1 - B))` vaut 0,5094.
- `P0 = math.exp(-log_somme_poisson(c, a) - math.log((1 - B) + B / (1 - rho)))` : c'est 1/(Ec((1 − B) + B/(1 − ρ))) écrit en logarithmes. Pour c = 4 : Ec = 13 + 3,375 = 16,375, (1 − B) + B/(1 − ρ) = 0,7939 + 0,8244 = 1,6183, et 1/(16,375 × 1,6183) = 1/26,5 ≈ 0,0377.
- `Lq = C * rho / (1 - rho)` ≈ 1,528, `Wq = C / (c * mu_rate - lambda_rate)` ≈ 0,1274, `W = Wq + 1 / mu_rate` ≈ 0,3774, et `L = lambda_rate * W` ≈ 4,528.

**`p_attente_sup`** multiplie C par `math.exp(-(c * mu_rate - lambda_rate) * t)`. Pour c = 4 et t = 0,2 : 0,5094 × e⁻⁰,⁸ ≈ 0,2289.

**`dimensionner`** est la boucle de dimensionnement.

- `c = math.floor(lambda_rate / mu_rate) + 1` : on démarre au premier c qui donne ρ < 1, ici ⌊3⌋ + 1 = 4.
- La boucle teste P(Wq > t) ≤ seuil, et en option W ≤ W_max, puis augmente c de 1. Pour t = 0,2 et un seuil de 0,05 : c = 4 donne 0,2289, refusé ; c = 5 donne 0,0477, accepté.

**`residu_equilibre`** recalcule chaque πₙ à partir de π₀ et vérifie λπₙ₋₁ = min(n, c) μ πₙ pour n = 1 à 40. Le plus grand écart est sous 10⁻¹⁵.

**`simuler_mmc`** vérifie tout sans aucune formule, sur une horloge simulée.

- `libres = [0.0] * c` est un tas (`heapq`) qui contient, pour chaque instance, l'instant où elle se libère.
- Pour chaque requête : `horloge += rng.expovariate(lambda_rate)` donne son arrivée ; `heapq.heappop(libres)` sort l'instance qui se libère la première ; `debut = max(horloge, premier_libre)` ; l'attente vaut `debut - horloge`.
- `heapq.heappush(libres, debut + rng.expovariate(mu_rate))` remet l'instance dans le tas avec sa nouvelle date de fin. Prendre toujours l'instance la plus tôt libre, dans l'ordre des arrivées, c'est exactement une file FIFO à c serveurs.

**`main()`**, bloc par bloc.

1. c = 4 : les huit mesures, vérifiées contre 13,5/26,5, 1/26,5, la formule naïve, Wq = 0,127358 et W = 0,377358 ; L = Lq + a ; résidu d'équilibre nul. Erlang B(4, 3) = 0,2061 montre ce que donnerait l'oubli du facteur c/(c − a).
2. c = 4, 5, 6 : P(Wq > 0,2) vaut 0,2289, 0,0477 et 0,0090. `dimensionner` renvoie 5, avec ou sans la contrainte W ≤ 0,35 s.
3. La simulation de 200 000 requêtes avec la graine 71 donne une part d'attente de 0,5112 (formule 0,5094), un Wq de 0,1281 s (formule 0,1274) et P(Wq > 0,2) = 0,2336 (formule 0,2289).
4. c = 200 et a = 150 : la formule d'origine lève `OverflowError` ; la récurrence donne C = 6,015 × 10⁻⁵ et π₀ = 7,175 × 10⁻⁶⁶, les mêmes valeurs qu'un calcul exact en fractions rationnelles. Pour c = 30, où la formule naïve tient encore, les deux méthodes coïncident à 10⁻¹² près.
5. À ρ = 0,75, de 1 à 16 instances : W passe de 1 s à 0,377 s puis à 0,263 s. Avec c = 1, Erlang C redonne M/M/1 : C = ρ = 0,75 et W = 1 s.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`erlang_c_naif(c, lambda_rate, mu_rate)`** — Cette fonction est la vieille calculatrice du fichier d'origine, gardée comme témoin, qui fait ses comptes terme à terme avec de vraies puissances et de vraies factorielles : elle reçoit le nombre d'instances c, le débit λ et le débit de service μ, calcule la charge offerte a = λ/μ, additionne les termes aᵏ/k! pour k de 0 à c − 1, forme le dernier terme aᶜ/c! multiplié par c/(c − a), et renvoie la part de ce dernier terme dans le total. Pour c = 4 et a = 3, elle trouve 13,5/26,5 ≈ 0,5094, juste, mais pour c = 200 et a = 150 la puissance déborde et Python lève une `OverflowError`, ce que la section 4 de `main` met en scène.

**`erlang_b(c, a)`** — Celle-ci est l'artisan patient qui monte un escalier marche par marche au lieu de sauter d'un coup au sommet : elle reçoit c et la charge offerte a, part de B = 1 pour zéro serveur, puis, pour k de 1 à c, remplace B par aB/(k + aB), une récurrence dont chaque valeur reste entre 0 et 1 et ne déborde donc jamais. Elle renvoie la probabilité de blocage d'Erlang B ; pour a = 3, les marches successives valent 0,75, 0,5294, 0,3462, puis 0,2061 à c = 4, et `erlang_c` part de ce nombre pour obtenir la probabilité d'attendre.

**`erlang_c(c, lambda_rate, mu_rate)`** — C'est la fonction principale, le bureau d'études qui rend tout le dossier d'une file M/M/c sans jamais former de factorielle géante : elle reçoit c, λ et μ, lève une `ValueError` si c < 1 ou si un débit n'est pas positif, puis une autre si ρ = a/c atteint 1, calcule ensuite B par `erlang_b`, la probabilité d'attendre C = B/(1 − ρ(1 − B)) et π₀ en logarithmes grâce à `log_somme_poisson`, enfin Lq, Wq = C/(cμ − λ), W = Wq + 1/μ et L = λW. Elle renvoie ces neuf valeurs dans un dictionnaire ; pour c = 4, λ = 12 et μ = 4, on y lit C ≈ 0,5094, π₀ = 1/26,5, Wq ≈ 0,1274 s et W ≈ 0,3774 s.

**`p_attente_sup(c, lambda_rate, mu_rate, t)`** — Cette fonction répond à la question que pose un engagement de service, combien de clients patienteront plus de t secondes : elle reçoit c, λ, μ et le délai t, demande à `erlang_c` la probabilité d'attendre C, puis la multiplie par exp(−(cμ − λ)t), la probabilité qu'une attente, une fois commencée, dure plus de t. Elle renvoie ce produit et propage la `ValueError` d'`erlang_c` si la file est instable ; pour t = 0,2 s, elle donne 0,2289 avec 4 instances, 0,0477 avec 5 et 0,0090 avec 6.

**`dimensionner(lambda_rate, mu_rate, t, seuil, W_max)`** — Celle-ci est le chef d'équipe qui ajoute une instance tant que la promesse faite aux clients n'est pas tenue : elle reçoit λ, μ, le délai t, la proportion tolérée de clients qui attendent plus de t, et en option un séjour moyen maximal, absent par défaut. Elle démarre au premier c stable, la partie entière de λ/μ plus un, soit 4 ici, teste si `p_attente_sup` reste sous le seuil et, si on l'a demandé, si W ne dépasse pas la borne, puis augmente c d'une unité jusqu'à réussir ; elle renvoie ce plus petit c, qui vaut 5 pour un seuil de 5 % à 0,2 s, avec ou sans la contrainte W ≤ 0,35 s.

**`residu_equilibre(c, lambda_rate, mu_rate, n_max)`** — Cette fonction est l'auditeur qui refait les comptes de la chaîne M/M/c sans faire confiance aux formules : elle reçoit c, λ, μ et le dernier état à examiner, obtient π₀, a et ρ par `erlang_c`, puis vérifie pour chaque n de 1 à n_max l'équation de coupure λπₙ₋₁ = min(n, c)μπₙ, qui dit qu'on traverse autant de fois la frontière entre deux états dans un sens que dans l'autre. Elle renvoie le plus grand écart constaté, que `main` exige sous 10⁻¹⁵ pour c = 4 et n_max = 40.

**`pi(n)`** — Cette fonction interne, qui vit dans `residu_equilibre`, est le registre des probabilités stationnaires dont l'auditeur a besoin : elle reçoit un état n et renvoie π₀aⁿ/n! tant que n ne dépasse pas c, car chaque client trouve alors un serveur libre, puis, au-delà, π₀aᶜ/c! multiplié par ρ à la puissance n − c, la file se remplissant comme une suite géométrique de raison ρ. Elle lit π₀, a, ρ et c dans la fonction englobante, si bien qu'elle ne prend que n en paramètre.

**`simuler_mmc(lambda_rate, mu_rate, c, n, graine, t)`** — Celle-ci fait vivre un centre d'appels à c postes sans aucune formule, comme un régisseur qui tient sur un tableau l'heure de libération de chaque poste : elle reçoit λ, μ, c, le nombre de requêtes, une graine et un délai t, range dans un tas `heapq` l'instant où chaque serveur se libère, fait arriver les requêtes à des intervalles exponentiels, donne à chacune le serveur libéré le plus tôt, mesure son attente puis remet ce serveur dans le tas avec sa nouvelle date de fin. Elle renvoie la part des requêtes qui attendent, l'attente moyenne et la part qui attend plus de t ; avec la graine 71 et 200 000 requêtes à c = 4, on obtient 0,5112, 0,1281 s et 0,2336, contre 0,5094, 0,1274 s et 0,2289 par les formules.

**`main()`** — C'est le directeur des opérations qui instruit le dossier de l'agent vocal en cinq temps : il calcule d'abord toutes les mesures pour c = 4, λ = 12 et μ = 4 et les confronte à 13,5/26,5, à 1/26,5, à la formule naïve et au résidu d'équilibre, puis compare P(Wq > 0,2) pour 4, 5 et 6 instances et fait choisir 5 instances à `dimensionner`. Il simule ensuite 200 000 requêtes pour retrouver les formules, montre qu'à c = 200 et a = 150 la formule naïve déborde quand la récurrence tient, observe à ρ = 0,75 l'attente qui fond de 1 à 16 instances, et vérifie enfin que c = 3 est refusé, chaque résultat étant verrouillé par un `assert`.

```python
"""Étape 71 — Erlang C : chaîne M/M/c, récurrence stable, P(Wq > t), W = Wq + 1/μ, boucle de dimensionnement."""
import heapq
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def erlang_c_naif(c: int, lambda_rate: float, mu_rate: float) -> float:
    """Formule d'origine, terme à terme : juste pour un petit c, déborde pour un grand c."""
    a = lambda_rate / mu_rate
    sum_terms = sum(a ** k / math.factorial(k) for k in range(c))
    last_term = (a ** c / math.factorial(c)) * (c / (c - a))
    return last_term / (sum_terms + last_term)


def erlang_b(c: int, a: float) -> float:
    """Erlang B par récurrence : B(0) = 1, B(k) = a B(k−1) / (k + a B(k−1)). Tous les termes restent dans [0, 1]."""
    b = 1.0
    for k in range(1, c + 1):
        b = a * b / (k + a * b)
    return b


def log_somme_poisson(c: int, a: float) -> float:
    """ln Σ_{k=0}^{c} a^k / k!, calculé en log-somme-exp pour ne jamais déborder."""
    termes = [k * math.log(a) - math.lgamma(k + 1) for k in range(c + 1)]
    m = max(termes)
    return m + math.log(sum(math.exp(t - m) for t in termes))


def erlang_c(c: int, lambda_rate: float, mu_rate: float) -> dict[str, float]:
    """Toutes les mesures d'une file M/M/c, sans factorielle ni puissance qui déborde."""
    if c < 1 or lambda_rate <= 0 or mu_rate <= 0:
        raise ValueError("il faut c ≥ 1, λ > 0 et μ > 0")
    a = lambda_rate / mu_rate
    rho = a / c
    if rho >= 1:
        raise ValueError(f"Système instable : ρ = {rho:.2f} ≥ 1")
    B = erlang_b(c, a)
    C = B / (1 - rho * (1 - B))                     # probabilité d'attendre
    # P0 = 1 / (E · ((1 − B) + B / (1 − ρ))), avec E = Σ_{k≤c} a^k/k!, en logarithme
    P0 = math.exp(-log_somme_poisson(c, a) - math.log((1 - B) + B / (1 - rho)))
    Lq = C * rho / (1 - rho)
    Wq = C / (c * mu_rate - lambda_rate)
    W = Wq + 1 / mu_rate
    return {"a": a, "rho": rho, "P0": P0, "B": B, "C": C, "Lq": Lq, "Wq": Wq, "W": W, "L": lambda_rate * W}


def p_attente_sup(c: int, lambda_rate: float, mu_rate: float, t: float) -> float:
    """P(Wq > t) = C(c, a) · e^(−(cμ − λ) t)."""
    return erlang_c(c, lambda_rate, mu_rate)["C"] * math.exp(-(c * mu_rate - lambda_rate) * t)


def dimensionner(lambda_rate: float, mu_rate: float, t: float, seuil: float, W_max: float | None = None) -> int:
    """Plus petit c stable tel que P(Wq > t) ≤ seuil (et W ≤ W_max si demandé)."""
    c = math.floor(lambda_rate / mu_rate) + 1          # premier c qui donne ρ < 1
    while True:
        ok = p_attente_sup(c, lambda_rate, mu_rate, t) <= seuil
        if W_max is not None:
            ok = ok and erlang_c(c, lambda_rate, mu_rate)["W"] <= W_max
        if ok:
            return c
        c += 1


def residu_equilibre(c: int, lambda_rate: float, mu_rate: float, n_max: int) -> float:
    """Vérifie λ π(n−1) = min(n, c) μ π(n) avec les πₙ tirés de P0."""
    m = erlang_c(c, lambda_rate, mu_rate)
    a, rho = m["a"], m["rho"]

    def pi(n: int) -> float:
        if n <= c:
            return m["P0"] * a ** n / math.factorial(n)
        return m["P0"] * a ** c / math.factorial(c) * rho ** (n - c)

    return max(abs(lambda_rate * pi(n - 1) - min(n, c) * mu_rate * pi(n)) for n in range(1, n_max + 1))


def simuler_mmc(lambda_rate: float, mu_rate: float, c: int, n: int, graine: int, t: float) -> tuple[float, float, float]:
    """c serveurs FIFO, horloge simulée. Renvoie (part qui attend, Wq moyen, part qui attend plus de t)."""
    rng = random.Random(graine)
    libres = [0.0] * c                     # instant où chaque serveur se libère (tas)
    horloge = 0.0
    attendent = depasse = 0
    total = 0.0
    for _ in range(n):
        horloge += rng.expovariate(lambda_rate)
        premier_libre = heapq.heappop(libres)
        debut = max(horloge, premier_libre)
        attente = debut - horloge
        attendent += attente > 0
        depasse += attente > t
        total += attente
        heapq.heappush(libres, debut + rng.expovariate(mu_rate))
    return attendent / n, total / n, depasse / n


def main() -> None:
    lam, mu = 12.0, 4.0
    print("1. Agent vocal : λ = 12 req/s, μ = 4 req/s par instance, c = 4")
    m = erlang_c(4, lam, mu)
    for cle in ("a", "rho", "P0", "C", "Lq", "Wq", "W", "L"):
        print(f"  {cle:<3} = {m[cle]:.6f}")
    assert m["a"] == 3.0 and m["rho"] == 0.75
    assert abs(m["C"] - 13.5 / 26.5) < 1e-12 and abs(m["P0"] - 1 / 26.5) < 1e-12
    assert abs(m["C"] - erlang_c_naif(4, lam, mu)) < 1e-12
    assert abs(m["Wq"] - 0.127358) < 1e-6 and abs(m["W"] - 0.377358) < 1e-6
    assert abs(m["L"] - (m["Lq"] + m["a"])) < 1e-12           # L = Lq + nombre moyen de serveurs occupés
    assert residu_equilibre(4, lam, mu, 40) < 1e-15
    print(f"  Erlang B(4, 3) = {m['B']:.6f} : ce qu'on obtient si l'on oublie le facteur c/(c − a)")

    print("2. P(Wq > 0.2 s) selon le nombre d'instances")
    for c in (4, 5, 6):
        r = erlang_c(c, lam, mu)
        print(f"  c = {c}   C = {r['C']:.4f}   P(Wq > 0.2) = {p_attente_sup(c, lam, mu, 0.2):.4f}   W = {r['W']:.4f} s")
    assert abs(p_attente_sup(4, lam, mu, 0.2) - 0.2289) < 1e-4
    assert abs(p_attente_sup(5, lam, mu, 0.2) - 0.0477) < 1e-4
    c_sla = dimensionner(lam, mu, t=0.2, seuil=0.05)
    c_sla_w = dimensionner(lam, mu, t=0.2, seuil=0.05, W_max=0.35)
    print(f"  plus petit c pour « moins de 5 % attendent plus de 0.2 s » : {c_sla}")
    print(f"  avec en plus W ≤ 0.35 s : {c_sla_w}   (c = 4 donne W = {m['W']:.3f} s > 0.35)")
    assert c_sla == 5 and c_sla_w == 5 and m["W"] > 0.35

    print("3. Simulation M/M/4 (graine 71, 200 000 requêtes, horloge simulée)")
    part, wq_sim, dep = simuler_mmc(lam, mu, 4, 200_000, graine=71, t=0.2)
    print(f"  part qui attend = {part:.4f} (C = {m['C']:.4f})   Wq = {wq_sim:.4f} s (formule {m['Wq']:.4f})"
          f"   P(Wq > 0.2) = {dep:.4f} (formule {p_attente_sup(4, lam, mu, 0.2):.4f})")
    assert abs(part - m["C"]) < 0.02 and abs(wq_sim - m["Wq"]) / m["Wq"] < 0.06 and abs(dep - 0.2289) < 0.02

    print("4. Grand pool : c = 200, a = 150 (ρ = 0.75)")
    try:
        erlang_c_naif(200, 150.0, 1.0)
    except OverflowError as e:
        print(f"  formule terme à terme : OverflowError ({e})")
    else:
        raise AssertionError("150.0 ** 200 aurait dû déborder")
    g = erlang_c(200, 150.0, 1.0)
    print(f"  récurrence : C = {g['C']:.3e}   Wq = {g['Wq']:.3e} s   P0 = {g['P0']:.3e}")
    # valeurs exactes obtenues en fractions rationnelles (module fractions), hors de ce programme
    assert abs(g["C"] / 6.015192773541632e-05 - 1) < 1e-9 and abs(g["P0"] / 7.175074051693259e-66 - 1) < 1e-9
    assert abs(erlang_c(30, 25.0, 1.0)["C"] - erlang_c_naif(30, 25.0, 1.0)) < 1e-12   # mêmes nombres quand le naïf tient

    print("5. Même ρ = 0.75, plus d'instances : l'attente fond")
    for c, lam_c in ((1, 3.0), (4, 12.0), (16, 48.0)):
        r = erlang_c(c, lam_c, 4.0)
        print(f"  c = {c:>2}   λ = {lam_c:>4.0f}   C = {r['C']:.4f}   Wq = {r['Wq']:.4f} s   W = {r['W']:.4f} s")
    assert abs(erlang_c(1, 3.0, 4.0)["C"] - 0.75) < 1e-12 and abs(erlang_c(1, 3.0, 4.0)["W"] - 1.0) < 1e-12

    try:
        erlang_c(3, lam, mu)
    except ValueError as e:
        print(f"  c = 3 → {e}")
    else:
        raise AssertionError("ρ = 1 aurait dû être refusé")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Agent vocal : λ = 12 req/s, μ = 4 req/s par instance, c = 4
…
  P0  = 0.037736
  C   = 0.509434
  Wq  = 0.127358
  W   = 0.377358
  Erlang B(4, 3) = 0.206107 : ce qu'on obtient si l'on oublie le facteur c/(c − a)
2. P(Wq > 0.2 s) selon le nombre d'instances
  c = 4   C = 0.5094   P(Wq > 0.2) = 0.2289   W = 0.3774 s
  c = 5   C = 0.2362   P(Wq > 0.2) = 0.0477   W = 0.2795 s
  c = 6   C = 0.0991   P(Wq > 0.2) = 0.0090   W = 0.2583 s
  plus petit c pour « moins de 5 % attendent plus de 0.2 s » : 5
3. Simulation M/M/4 (graine 71, 200 000 requêtes, horloge simulée)
  part qui attend = 0.5112 (C = 0.5094)   Wq = 0.1281 s (formule 0.1274)   P(Wq > 0.2) = 0.2336 (formule 0.2289)
4. Grand pool : c = 200, a = 150 (ρ = 0.75)
  formule terme à terme : OverflowError ((34, 'Result too large'))
  récurrence : C = 6.015e-05   Wq = 1.203e-06 s   P0 = 7.175e-66
5. Même ρ = 0.75, plus d'instances : l'attente fond
  c = 16   λ =   48   C = 0.2046   Wq = 0.0128 s   W = 0.2628 s
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : M/M/1 dit ce qui arrive à un guichet ; Erlang C dit ce qui arrive quand une seule file nourrit plusieurs guichets. On ne fait attendre que la fraction C des requêtes qui trouvent tout le monde occupé, et cette fraction se calcule sans jamais former un nombre trop grand.

## Squelette algorithmique

Le calcul analytique reçoit le débit λ, le taux de service μ d'une instance et le nombre d'instances c ; il rend la probabilité d'attente C, π₀, Lq, Wq, W et la probabilité d'attendre plus de t. L'idée est de ne jamais former aᶜ ni c! : on construit Erlang B pas à pas, avec des nombres qui restent entre 0 et 1, puis on passe à Erlang C par une seule division. Le dimensionnement reçoit en plus un seuil de temps t, une proportion tolérée et, si besoin, un séjour maximal ; il rend le plus petit c qui tient l'objectif, en ajoutant des instances une par une. La simulation à événements discrets reçoit λ, μ, c, un nombre de requêtes, une graine et le seuil t ; elle rend les mêmes grandeurs mesurées. Son idée : garder dans un tas l'instant où chaque instance se libère, et donner chaque requête, dans l'ordre d'arrivée, à l'instance libre la plus tôt.

```text
ALGORITHME ErlangB                   (récurrence stable)
ENTRÉES : c entier ≥ 1, trafic a > 0
SORTIE : B(c, a), dans [0 ; 1]
  b ← 1
  POUR k DE 1 À c FAIRE
    b ← a × b / (k + a × b)
  FIN POUR
  RETOURNER b

ALGORITHME ErlangC                   (calcul analytique M/M/c)
ENTRÉES : c ≥ 1, λ > 0, μ > 0
SORTIE : C, π0, Lq, Wq, W
  a ← λ / μ ; ρ ← a / c
  SI ρ ≥ 1 ALORS
    ÉCHOUER « système instable »
  FIN SI
  B ← ErlangB(c, a)
  C ← B / (1 − ρ × (1 − B))
  lnE ← ln Σ aᵏ / k! pour k de 0 à c, calculé en log-somme-exp
  π0 ← exp(−lnE − ln((1 − B) + B / (1 − ρ)))
  Lq ← C × ρ / (1 − ρ)
  Wq ← C / (c × μ − λ)
  RETOURNER (C, π0, Lq, Wq, Wq + 1 / μ)

ALGORITHME Dimensionner
ENTRÉES : λ, μ, seuil de temps t, proportion tolérée s, séjour maximal W_max (facultatif)
SORTIE : le plus petit c tel que P(Wq > t) ≤ s, et W ≤ W_max si W_max est donné
  c ← partie entière de (λ / μ) + 1           // premier c avec ρ < 1
  TANT QUE vrai FAIRE
    (C, π0, Lq, Wq, W) ← ErlangC(c, λ, μ)
    p ← C × exp(−(c × μ − λ) × t)
    SI p ≤ s ET (W_max n'est pas donné OU W ≤ W_max) ALORS
      RETOURNER c
    SINON
      c ← c + 1
    FIN SI
  FIN TANT QUE

ALGORITHME SimulerMMc                (simulation à événements discrets, c instances FIFO)
ENTRÉES : λ, μ, c, nombre de requêtes n, graine, seuil t
SORTIE : part des requêtes qui attendent, Wq moyen, part qui attend plus de t
  libres ← tas contenant c fois l'instant 0
  horloge ← 0 ; attendent ← 0 ; dépassent ← 0 ; total ← 0
  POUR i DE 1 À n FAIRE
    horloge ← horloge + tirage exponentiel de taux λ      // arrivée de la requête i
    premier ← retirer le minimum de libres
    début ← max(horloge, premier)
    attente ← début − horloge
    SI attente > 0 ALORS attendent ← attendent + 1 FIN SI
    SI attente > t ALORS dépassent ← dépassent + 1 FIN SI
    total ← total + attente
    insérer début + tirage exponentiel de taux μ dans libres
  FIN POUR
  RETOURNER (attendent / n, total / n, dépassent / n)
```

**Complexité :** `ErlangB` fait c tours de boucle à coût constant : O(c) en temps, O(1) en mémoire. Dans `ErlangC`, le terme dominant est la somme de Poisson en log-somme-exp, qui parcourt aussi c + 1 termes : O(c) en temps ; le code les range dans une liste, d'où O(c) en mémoire, qu'une somme au fil de l'eau ramènerait à O(1). La formule d'origine avait la même complexité, mais ses termes intermédiaires débordent dès que aᶜ dépasse 1,8 × 10³⁰⁸. `Dimensionner` appelle `ErlangC` une ou deux fois par valeur de c essayée, de c₀ = ⌊a⌋ + 1 jusqu'à la réponse c* : O(c* × (c* − c₀)) au total, et c* − c₀ reste petit, de l'ordre de √a d'après la règle en racine carrée (Pour aller plus loin). On pourrait descendre à O(c*) en prolongeant la récurrence d'Erlang B d'un pas à chaque nouvelle valeur de c au lieu de la recommencer. `SimulerMMc` fait, par requête, deux tirages et un retrait plus une insertion dans un tas de taille c, chacun en O(log c) : O(n log c) en temps et O(c) en mémoire, puisqu'on ne garde que les c instants de libération.

**Du squelette au code :** `ErlangB` est `erlang_b`, mot pour mot. `ErlangC` est `erlang_c` : le test de stabilité, `B = erlang_b(c, a)`, la ligne `C = B / (1 - rho * (1 - B))`, puis `P0` calculé avec `log_somme_poisson` (la ligne « lnE » du pseudo-code), et enfin `Lq`, `Wq` et `W`. Le calcul de p dans la boucle de `Dimensionner` est `p_attente_sup`, et la boucle elle-même est `dimensionner`, dont le `while True` et le `return c` sont le `TANT QUE` et le `RETOURNER`. `SimulerMMc` est `simuler_mmc` : `libres = [0.0] * c` est le tas initial (une liste de valeurs égales est déjà un tas), « retirer le minimum » est `heapq.heappop(libres)`, « insérer » est `heapq.heappush`, et les deux compteurs s'incrémentent avec `attendent += attente > 0` et `depasse += attente > t`, parce qu'en Python un booléen vaut 0 ou 1. Les vérifications indépendantes, `residu_equilibre` (équations de coupure) et `erlang_c_naif` (formule d'origine, pour les petits c), n'ont pas de ligne dans le squelette : elles contrôlent le calcul sans en faire partie.

## Cas d'usage réels aux Émirats

Les débits, durées et objectifs ci-dessous sont illustratifs : en production, on mesure λ et μ par tranche de quinze minutes et l'on vérifie que les durées sont proches d'une exponentielle (sinon, étape 68).

### Secteur public — l'agent vocal d'un service en ligne

Une entité de services publics en ligne, dont les usagers s'identifient par UAE Pass, ouvre un agent vocal bilingue arabe et anglais pour les questions courantes. Au pic, il reçoit 12 questions par seconde, et chaque instance (reconnaissance vocale, modèle, synthèse) en traite 4 par seconde. L'objectif public est double : moins de 5 % des usagers attendent plus de 0,2 s avant que l'agent commence à répondre, et le temps moyen total reste sous 0,35 s pour que la conversation paraisse naturelle. Avec 4 instances, ρ = 0,75 semble confortable, mais Erlang C donne 22,9 % d'usagers qui attendent plus de 0,2 s et W = 0,377 s : les deux objectifs sont manqués. Avec 5 instances, on tombe à 4,77 % et W = 0,280 s, et la boucle de dimensionnement le trouve en deux itérations. Sans ce calcul, l'équipe aurait réglé l'autoscaler sur « ρ < 0,8 » et livré un service qui coupe la parole aux usagers une fois sur cinq. Les enregistrements vocaux sont des données personnelles au sens de la PDPL et ne sont conservés que le temps du traitement ; l'indicateur suivi est P(Wq > 0,2 s) mesuré, comparé à la valeur d'Erlang C.

### Banque — un service de messagerie client dimensionné sur un taux de prise en charge

Une banque de détail de Dubaï fait répondre aux messages de ses clients par un agent qui consulte le solde, les dernières opérations et les conditions des cartes. Il arrive 0,5 conversation par seconde, et une instance consacre en moyenne 20 s à chacune (outils compris) : le trafic offert vaut a = 10 erlangs. L'objectif est que 80 % des conversations soient prises en charge en moins de 2 s, soit P(Wq > 2) ≤ 0,2. Une règle intuitive, « le trafic plus 10 % », donnerait 11 instances, avec lesquelles 61,7 % des clients attendraient plus de 2 s. Erlang C demande 14 instances (13 donnent encore 21,1 %), pour une utilisation de 71 %. La décision est de réserver 14 connexions au fournisseur de modèle aux heures de bureau et de redescendre le soir. Les réponses qui portent sur un crédit appliquent le plafond d'endettement de la CBUAE par l'outil dédié, quelle que soit la charge ; l'indicateur suivi est la part des conversations prises en charge en moins de 2 s.

### Crypto — un jour d'ouverture d'un nouveau jeton

Une plateforme d'actifs virtuels agréée par la VARA fait vérifier par un agent la conformité des nouveaux comptes (documents KYC, cohérence des déclarations). En temps normal, il arrive 0,2 dossier par seconde et chaque vérification prend 10 s : a = 2, et il faut 5 instances pour que moins de 5 % des dossiers attendent plus de 5 s. Le jour de l'ouverture d'un nouveau jeton, le trafic est multiplié par 3 (a = 6). Multiplier aussi les instances par 3 en lancerait 15 ; Erlang C montre que 9 suffisent (P(Wq > 5) = 4,4 %), parce qu'un pool plus grand absorbe mieux les aléas. L'équipe lance donc 9 instances la veille et les retire le lendemain, ce qui évite 6 instances inutiles pendant toute la journée. La vérification n'est jamais allégée pour suivre la cadence : un dossier qui attend reste en attente, il n'est pas validé par défaut. L'indicateur suivi est le p95 de l'attente des dossiers et le nombre de dossiers en file à chaque heure.

### Assurance — combien de répliques pour l'analyse des photos de sinistre

Un assureur auto et santé fait analyser par un modèle de vision les photos jointes aux déclarations de sinistre automobile, pour estimer les dégâts, la franchise et la vétusté. Il arrive 0,6 dossier par seconde au pic, et une réplique du modèle en traite un en 5 s : a = 3. Avec 4 répliques, l'attente moyenne vaut 2,5 s et 6,9 % des dossiers attendent plus de 10 s ; avec 5, l'attente moyenne tombe à 0,59 s et seuls 0,43 % attendent plus de 10 s. La décision se prend en comparant le coût horaire d'une réplique de plus à celui des dossiers qui dépassent 10 s, quand le client est encore au téléphone avec le gestionnaire. Sans Erlang C, l'équipe aurait vu « 75 % d'utilisation » sur le tableau de bord et conclu qu'il restait de la marge. Les estimations restent soumises à un gestionnaire avant toute décision d'indemnisation, sous la supervision de la CBUAE ; l'indicateur suivi est P(Wq > 10 s) par heure.

### Immobilier — le lancement d'un projet off-plan

Un promoteur de Dubaï et d'Abu Dhabi ouvre la commercialisation d'un projet sur plan, et un agent répond aux questions des acheteurs : prix en AED/sqft, échéancier, frais de transfert DLD de 4 %, enregistrement. Le jour du lancement, il arrive 2 questions par seconde, et une instance en traite une en 3 s : a = 6. L'objectif commercial est que moins de 10 % des acheteurs attendent plus d'une seconde. Avec 8 instances (ρ = 0,75), 18,3 % attendent plus d'une seconde ; avec 9, 7,2 % : la boucle de dimensionnement retient 9. L'équipe fixe aussi un plafond de réponses générées par question pour que μ ne baisse pas pendant la journée, parce qu'une réponse plus longue réduirait la capacité de chaque instance. Les montants cités (prix, frais DLD) viennent d'outils et sont datés. L'indicateur suivi est la part d'acheteurs qui attendent plus d'une seconde, heure par heure.

### RH — le jour de la paie

Un cabinet RH présent dans plusieurs émirats fait répondre par un agent aux questions des salariés de ses entreprises clientes le jour de la paie : montant net, virement WPS, solde de congés. Il arrive 0,25 question par seconde, et une instance en traite une en 12 s : a = 3. L'objectif est que moins de 5 % des salariés attendent plus de 30 s ; Erlang C montre que 4 instances suffisent (4,2 %), avec un temps moyen total de 18 s. Une cinquième instance ferait tomber le temps moyen à 13 s, mais sans nécessité au regard de l'objectif : le cabinet la garde en réserve pour le cas où le temps de traitement s'allonge, par exemple si l'outil qui interroge le système de paie ralentit. Sans calcul, la tentation aurait été d'aligner le nombre d'instances sur le nombre d'entreprises clientes. Les réponses ne donnent un montant qu'à partir des données de paie validées ; l'indicateur suivi est P(Wq > 30 s) et le temps de réponse de l'outil de paie.

## Pièges et limites

- **Multiplier les instances au prorata du trafic.** Tripler λ ne demande pas de tripler c : 9 instances au lieu de 15 dans le cas crypto. À l'inverse, diviser le trafic ne permet pas de diviser c d'autant.
- **Calculer aᶜ/c! directement.** `150.0 ** 200` déborde ; même quand il ne déborde pas, le rapport de deux grands nombres perd de la précision. On passe par la récurrence d'Erlang B.
- **Prendre π₀ pour 1 − ρ.** Avec 4 instances à ρ = 0,75, π₀ vaut 0,038, pas 0,25.
- **Lire Wq comme l'attente de ceux qui attendent.** C'est une moyenne sur toutes les requêtes ; celles qui attendent attendent en moyenne 1/(cμ − λ), soit deux fois plus à c = 4.
- **Oublier les hypothèses.** Des instances qui ne sont pas identiques, des durées à longue traîne ou des clients qui abandonnent (modèle d'Erlang A) changent les nombres ; on simule ou l'on mesure.

### Exercice feuille blanche

1. Sans regarder le code, écrire `erlang_b` et le passage à Erlang C, puis vérifier à la main C(4, 3) ≈ 0,5094.
2. Prédire, puis vérifier : avec λ = 12, μ = 4 et c = 6, que valent C, Wq, W et P(Wq > 0,2) ? (Réponse : 0,0991 ; 0,0991/12 ≈ 0,0083 s ; 0,2583 s ; 0,0991 × e⁻²,⁴ ≈ 0,0090.)
3. Trouver le bug : `last_term = a ** c / math.factorial(c)`, sans le facteur `c / (c - a)`. Quelle formule obtient-on, et pourquoi sous-estime-t-elle l'attente ?

## Pour aller plus loin

La règle de dimensionnement en racine carrée (régime de Halfin et Whitt) dit qu'à qualité de service fixée, il faut environ c ≈ a + β√a instances, où β dépend de l'objectif : la marge nécessaire croît comme √a et non comme a, ce qui explique les économies d'échelle observées. Le modèle d'Erlang A ajoute l'abandon des clients qui attendent trop ; le modèle M/M/c/K ajoute une capacité finie, et Erlang B en est le cas K = c.

> Suite : [Coûts et gestion des tokens](<72-Couts-et-Gestion-des-Tokens.md>) — étape 72.
