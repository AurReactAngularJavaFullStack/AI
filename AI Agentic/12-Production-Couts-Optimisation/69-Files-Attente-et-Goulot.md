# Étape 69 — Théorie des Files d'Attente (Queueing Theory) et Loi de Little

> Étape 69 du parcours · Prérequis : [Notation de Kendall](<68-Notation-de-Kendall.md>) · Suite : [File M/M/1](<70-File-MM1.md>)

**Dossier :** 12-Production-Couts-Optimisation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, AI Platform Team, Forward-Deployed Engineers  
**Nom du fichier :** 69-Files-Attente-et-Goulot.md

## Définition

La théorie des files d'attente modélise la façon dont des requêtes (les questions des utilisateurs, ou les tâches qu'un agent confie à un autre) arrivent dans un système, y attendent, puis y sont traitées. Elle relie trois grandeurs mesurables : le débit d'arrivée λ, le temps moyen W qu'une requête passe dans le système, et le nombre moyen L de requêtes présentes. La loi de Little, L = λW, dit que ces trois grandeurs ne sont pas indépendantes : en connaître deux donne la troisième, quelle que soit la loi des arrivées ou des services. L'utilisation ρ = λ/(cμ) mesure la part de la capacité occupée ; c'est elle qui fait passer un service de fluide à saturé, et le temps de réponse ne croît pas en proportion de la charge mais comme 1/(1 − ρ).

## Rôle dans un agent

Quand on déploie un agent sur un serveur, il faut savoir combien d'instances lancer pour que les utilisateurs n'attendent pas trop longtemps. Dans la boucle percevoir → décider → agir → observer, chaque « agir » (appel au LLM, à un outil, à un serveur MCP) passe par une file. La loi de Little sert d'abord à l'**observation** en production : on compte le nombre de requêtes en cours et le débit, et l'on en déduit le temps de séjour sans chronométrer chaque requête. L'utilisation ρ sert à l'**ordonnanceur** et à l'autoscaler, qui ajoutent une instance avant que ρ n'approche 1. Le facteur 1/(1 − ρ) sert au **garde-fou de débit** (rate limiter), qui refuse ou diffère des requêtes plutôt que de laisser la latence exploser. C'est vital pour les agents exposés derrière une API, une fonction serverless ou un consommateur Kafka.

## Équation complète

La loi de Little (relation fondamentale), valable pour tout système stable :

$$
L = \lambda W
$$

L'utilisation d'un serveur, puis d'un groupe de c serveurs identiques :

$$
\rho = \frac{\lambda}{\mu}
\qquad\qquad
\rho = \frac{\lambda}{c\,\mu}
$$

Little appliquée à la seule file d'attente, et le séjour découpé en attente plus service :

$$
L_q = \lambda W_q
\qquad\qquad
W = W_q + \frac{1}{\mu}
$$

Pour une file M/M/1 (arrivées de Poisson, service exponentiel, un serveur, ρ < 1), les quatre mesures, démontrées à l'étape 70 :

$$
W = \frac{1}{\mu - \lambda} = \frac{T_{service}}{1-\rho}
$$

$$
L = \frac{\rho}{1-\rho}
$$

$$
W_q = \frac{\rho}{\mu - \lambda}
$$

$$
L_q = \frac{\rho^2}{1-\rho}
$$

## Décryptage des symboles

$$
L
$$

Nombre moyen de requêtes présentes dans le système, en attente ou en cours de traitement · réel ≥ 0 · variable Python : `L`, et `L_obs` dans la simulation.

$$
\lambda
$$

Taux d'arrivée : nombre moyen de nouvelles requêtes par seconde · réel > 0 · variable Python : `lambd` (`lambda` est un mot réservé de Python).

$$
W
$$

Temps de séjour moyen : durée qu'une requête passe dans le système, attente plus traitement, en secondes · variable Python : `W`, et `W_obs` dans la simulation.

$$
\mu
$$

Taux de service d'**une** instance : nombre de requêtes qu'elle traite par seconde quand elle ne fait que ça · réel > 0 · variable Python : `mu`.

$$
c
$$

Nombre d'instances identiques qui servent en parallèle · entier ≥ 1 · variable Python : `c`.

$$
\rho
$$

Utilisation : fraction du temps où une instance est occupée. Le rapport λ/(cμ) peut dépasser 1 ; il n'est alors plus une utilisation mais une charge offerte, et la file grandit sans limite · variable Python : `rho`.

$$
T_{service}
$$

Durée moyenne d'un traitement, égale à 1/μ, en secondes · variable Python : `T_service`.

$$
W_q
$$

Attente moyenne dans la file, avant le début du traitement, en secondes · variable Python : `m["Wq"]`.

$$
L_q
$$

Nombre moyen de requêtes qui attendent dans la file, sans compter celle en traitement · variable Python : `m["Lq"]`.

$$
N(t)
$$

Nombre de requêtes présentes à l'instant t : une courbe en escalier qui monte de 1 à chaque arrivée et descend de 1 à chaque départ · variable Python : `present` dans `aire_sous_N`.

$$
W_i
$$

Séjour de la requête i, instant de départ moins instant d'arrivée · variable Python : élément de la liste `sejours`.

## Démonstration

### 1. La loi de Little par l'argument d'aire

On trace la courbe N(t) du nombre de requêtes présentes, sur une durée [0, T]. On suppose le système vide à l'instant 0 et à l'instant T (on choisit T à la fin d'une période d'activité). On calcule l'aire sous cette courbe de deux façons.

**Par tranches de temps.** Entre deux événements, N(t) est constant ; l'aire est la somme des « nombre de présents × durée pendant laquelle ce nombre a tenu ». Divisée par T, c'est par définition le nombre moyen de présents observé :

$$
\hat L = \frac{1}{T} \int_0^T N(t)\, dt
$$

**Par requête.** Chaque requête i compte pour 1 dans N(t) exactement pendant son séjour, de son arrivée à son départ. Son apport à l'aire est donc un rectangle de hauteur 1 et de largeur Wᵢ. Comme le système est vide en 0 et en T, toutes les requêtes arrivées pendant [0, T] sont reparties avant T et leur rectangle est entier :

$$
\int_0^T N(t)\, dt = \sum_{i=1}^{n} W_i
$$

où n est le nombre de requêtes arrivées. On divise les deux membres par T, et l'on fait apparaître n au numérateur et au dénominateur :

$$
\hat L = \frac{1}{T}\sum_{i=1}^{n} W_i = \frac{n}{T} \cdot \frac{1}{n}\sum_{i=1}^{n} W_i = \hat\lambda \cdot \hat W
$$

parce que n/T est le débit observé et que la moyenne des Wᵢ est le séjour moyen observé. Cette égalité est **exacte** sur toute trace qui commence et finit vide, sans aucune hypothèse sur la loi des arrivées, des services, le nombre de serveurs ou l'ordre de service. Dans un système stable, les instants où il se vide reviennent indéfiniment ; en faisant tendre T vers l'infini le long de ces instants, les moyennes observées tendent vers λ, W et L, et l'on obtient L = λW. Si T tombe pendant une période d'activité, l'erreur se limite aux séjours en cours, dont la contribution divisée par T tend vers 0.

**Exemple à la main (le code le refait).** Quatre requêtes arrivent aux instants 0 ; 0,5 ; 1 et 3, et demandent 1 ; 1 ; 0,5 et 0,5 seconde de traitement, servies dans l'ordre par un seul agent.

| Requête | Arrivée | Début du traitement | Départ | Séjour Wᵢ |
|---|---|---|---|---|
| 1 | 0 | 0 | 1 | 1 |
| 2 | 0,5 | 1 | 2 | 1,5 |
| 3 | 1 | 2 | 2,5 | 1,5 |
| 4 | 3 | 3 | 3,5 | 0,5 |

La somme des séjours vaut 4,5. Par tranches, N(t) vaut 1 sur [0 ; 0,5], 2 sur [0,5 ; 2], 1 sur [2 ; 2,5], 0 sur [2,5 ; 3] et 1 sur [3 ; 3,5] : l'aire vaut 0,5 + 3 + 0,5 + 0 + 0,5 = 4,5. Avec T = 3,5, on a L̂ = 4,5/3,5 = 1,2857, λ̂ = 4/3,5 = 1,1429 et Ŵ = 4,5/4 = 1,125, et 1,1429 × 1,125 = 1,2857.

### 2. ρ est la fraction du temps où le serveur travaille

On applique Little au seul serveur, vu comme un « système » dans lequel une requête entre au début de son traitement et sort à la fin. Il y entre λ requêtes par seconde, chacune y reste en moyenne 1/μ. Avec un seul serveur, le nombre de requêtes dans ce système vaut 0 ou 1, donc sa moyenne est la probabilité que le serveur soit occupé. Little donne

$$
P(\text{occupé}) = \lambda \cdot \frac{1}{\mu} = \rho
\qquad\Longrightarrow\qquad
P_0 = 1 - \rho
$$

Cette preuve ne suppose aucune loi particulière : elle vaut pour toute file à un serveur, pas seulement M/M/1. Avec c serveurs, le même argument donne un nombre moyen de serveurs occupés égal à λ/μ, donc une fraction λ/(cμ) par serveur.

### 3. Little sur la file, et L = Lq + ρ

On applique Little à la file seule, de l'arrivée au début du traitement : Lq = λWq. Le séjour est l'attente suivie du traitement, donc W = Wq + 1/μ. On multiplie par λ :

$$
L = \lambda W = \lambda W_q + \frac{\lambda}{\mu} = L_q + \rho
$$

Le nombre de présents est le nombre d'attendants plus le nombre moyen de requêtes en traitement, qui vaut ρ d'après le point 2.

### 4. Les quatre mesures de M/M/1

L'étape 70 démontre, par les équations d'équilibre de la chaîne de Markov, que W = 1/(μ − λ). Les trois autres mesures en découlent par les points 1 et 3 :

$$
L = \lambda W = \frac{\lambda}{\mu-\lambda} = \frac{\rho}{1-\rho}
\qquad
W_q = W - \frac{1}{\mu} = \frac{\mu - (\mu-\lambda)}{\mu(\mu-\lambda)} = \frac{\rho}{\mu-\lambda}
\qquad
L_q = \lambda W_q = \frac{\rho^2}{1-\rho}
$$

On divise numérateur et dénominateur par μ pour passer de λ/(μ − λ) à ρ/(1 − ρ). Vérification de cohérence avec le point 3 :

$$
L_q + \rho = \frac{\rho^2 + \rho(1-\rho)}{1-\rho} = \frac{\rho}{1-\rho} = L
$$

Avec λ = 3 et μ = 4 : ρ = 0,75, W = 1 s, L = 3, Wq = 0,75 s et Lq = 2,25.

### 5. Pourquoi la latence explose, et à quelle vitesse

On écrit W = T_service/(1 − ρ). Le facteur 1/(1 − ρ) vaut 2 à ρ = 0,5, 5 à ρ = 0,8, 10 à ρ = 0,9 et 20 à ρ = 0,95. Sa dérivée vaut 1/(1 − ρ)², donc un même point de charge supplémentaire coûte de plus en plus cher : passer de 0,50 à 0,51 ajoute 0,04 T_service, passer de 0,90 à 0,91 ajoute 1,11 T_service, presque trente fois plus. La croissance n'est pas exponentielle, comme on le lit parfois : c'est une hyperbole, qui tend vers l'infini quand ρ tend vers 1. À ρ ≥ 1, il n'y a plus de régime stable (étape 68, point 2) et la fonction du code renvoie `math.inf`.

### 6. Trois affirmations corrigées

- « Si on augmente le nombre d'agents, le taux de service global μ augmente. » Le μ d'une instance ne change pas ; c'est la capacité totale cμ qui augmente, donc ρ = λ/(cμ) diminue. Le séjour baisse, mais ne descend jamais sous le temps de traitement 1/μ.
- « Si une tâche est bloquante (attendre une API externe), le temps de traitement W augmente. » C'est d'abord le temps de **service** 1/μ qui augmente, donc μ baisse et ρ monte ; W augmente alors plus que le temps ajouté, à cause du facteur 1/(1 − ρ). L augmente ensuite selon Little.
- « ρ est entre 0 et 1. » Le rapport λ/(cμ) peut dépasser 1 : il mesure alors la charge offerte, et l'utilisation réelle plafonne à 100 % pendant que la file grandit.

## Effets et comportement

- **Si λ se rapproche de cμ**, ρ se rapproche de 1 et le temps de séjour tend vers l'infini : c'est la saturation, l'agent ne répond plus dans des délais utiles.
- **Si l'on ajoute des instances**, ρ = λ/(cμ) diminue et le temps de séjour s'effondre vers 1/μ, sans jamais passer en dessous.
- **Si un outil bloquant allonge le service**, μ baisse, ρ monte et le séjour croît plus vite que la durée ajoutée ; le nombre de requêtes présentes L croît selon Little.
- **Si l'on mesure L et λ**, on obtient W = L/λ sans hypothèse de loi et sans chronométrer chaque requête.
- **Le débit de sortie ne dit rien du délai.** En régime stable, il égale λ, que l'attente soit de 1 s ou de 1 min.

## Du symbole au code Python

La loi de Little est un produit. La file M/M/1 est une horloge et une file d'attente. Le déroulé suit les deux : d'abord la trace à quatre requêtes de la démonstration, puis λ = 3 arrivées par seconde et μ = 4 services par seconde. Copiez dans `file_agents.py`.

| Symbole | Variable ou fonction |
|---|---|
| L = λW | `loi_de_little(lambd, W)` |
| ρ = λ/μ | `rho_un_serveur(lambd, mu)` |
| ρ = λ/(cμ) | `rho_pool(lambd, mu, c)` |
| plus petit c tel que ρ ≤ ρ_cible | `instances_minimales(lambd, mu, rho_cible)` |
| W = 1/(μ − λ) | `temps_sejour_mm1(lambd, mu)` |
| W, L, Wq, Lq de M/M/1 | `mesures_mm1(lambd, mu)` |
| ∫ N(t) dt | `aire_sous_N(evenements)` |
| Wᵢ | `sejours` renvoyé par `trace_fifo` |

### Déroulé, ligne par ligne

**Les fonctions courtes**, avant toute simulation.

- `loi_de_little` renvoie `lambd * W`. Rien d'autre. Si une requête reste 1 seconde et qu'il en arrive 3 par seconde, il y en a en moyenne 3 dans le système.
- `rho_un_serveur` renvoie `lambd / mu`. Ici 3/4 = 0,75. C'est la fraction du temps où l'unique agent est occupé (démonstration, point 2).
- `rho_pool` divise en plus par `c`, le nombre d'agents : λ/(cμ).
- `instances_minimales` part de `c = 1` et, tant que `rho_pool(lambd, mu, c)` dépasse la charge visée, ajoute une instance. Pour λ = 12, μ = 4 et une cible de 0,75, la boucle essaie c = 1 (charge 3), c = 2 (1,5), c = 3 (1,0), puis s'arrête à c = 4, où la charge vaut exactement 0,75. La boucle s'arrête toujours, parce que λ/(cμ) décroît vers 0 quand c grandit et finit donc par passer sous toute cible strictement positive ; c'est pour cela qu'une cible nulle ou négative est refusée par `ValueError`.
- `temps_sejour_mm1` : si `lambd >= mu`, on renvoie `math.inf`. La file ne se vide jamais, il n'y a pas de moyenne finie. Sinon `return 1.0 / (mu - lambd)`. Ici 1/(4 − 3) = 1 seconde.
- `mesures_mm1` calcule `Wq = W - 1.0 / mu`, soit 1 − 0,25 = 0,75 s, puis `Lq = lambd * Wq` = 2,25 : c'est Little appliquée à la file seule. Elle lève `ValueError` si λ ≥ μ, parce qu'un dictionnaire de mesures infinies n'aurait pas de sens.
- Le lien avec ρ : le temps de service vaut `T_service = 1.0 / mu`, soit 0,25 s. T_service/(1 − ρ) = 0,25/0,25 = 1. Même nombre, autre écriture. `L = 3 * 1 = 3`, et aussi ρ/(1 − ρ) = 0,75/0,25 = 3.

**`trace_fifo(arrivees, durees)`**, un guichet servi dans l'ordre d'arrivée.

- `libre_a = 0.0` : l'instant où l'agent sera libre.
- `zip(arrivees, durees, strict=True)` : les deux listes doivent avoir la même longueur ; sinon Python lève une erreur au lieu d'ignorer la fin d'une liste.
- `debut_service = max(arrivee, libre_a)` : si l'agent est déjà libre, le service commence tout de suite. S'il est occupé jusqu'à `libre_a`, la requête attend. Le `max` est toute la file d'attente. Pour la requête 2 de l'exemple, `max(0.5, 1.0)` vaut 1,0 : elle attend 0,5 s.
- `fin = debut_service + duree`, puis `libre_a = fin` : l'agent est pris jusqu'à cette fin. La requête suivante le verra.
- `sejours.append(fin - arrivee)` : le temps total de cette requête, attente comprise. Pour la trace à quatre requêtes, on obtient `[1.0, 1.5, 1.5, 0.5]`.
- Deux événements sont enregistrés : `(arrivee, +1)` et `(fin, -1)`. Le `+1` veut dire « une requête de plus est dans le système ».
- `evenements.sort()` : on remet tout dans l'ordre du temps, parce qu'un départ peut tomber après l'arrivée suivante.

**`aire_sous_N(evenements)`** rejoue la courbe « combien de requêtes sont là ».

- `aire += present * (instant - precedent)`, puis `present += delta` : l'aire est le nombre de présents multiplié par la durée pendant laquelle ce nombre a tenu. C'est le calcul « par tranches » de la démonstration. Sur l'exemple, elle vaut 4,5, comme la somme des séjours.
- `assert present == 0` : la trace doit finir vide, sinon l'égalité aire = somme des séjours n'est plus exacte.

**`simuler_mm1`** : on ne branche pas la formule. On fait entrer 20 000 requêtes une par une.

- `rng = random.Random(graine)` : le générateur est fixé. Relancer le programme refait les mêmes tirages.
- `horloge += rng.expovariate(lambd)` : on avance une horloge **simulée** d'un délai aléatoire de moyenne 1/λ. `expovariate(3)` a une moyenne d'un tiers de seconde. Aucune horloge réelle n'est lue.
- `durees.append(rng.expovariate(mu))` : un service de moyenne 1/μ = 0,25 s.
- `T = evenements[-1][0]` : l'instant du dernier départ, où le système est vide.
- La fonction renvoie `W` (moyenne des séjours), `L` (aire divisée par T) et le débit observé `n_clients / T`.

**`main()`**, bloc par bloc.

1. La trace à quatre requêtes : séjours `[1.0, 1.5, 1.5, 0.5]`, aire 4,5, L̂ = 1,2857 = λ̂ × Ŵ. Les `assert` vérifient l'égalité exacte.
2. L'agent unique : ρ = 0,75, W = 1 s, L = 3, Wq = 0,75 s, Lq = 2,25, et L − Lq = 0,75 = ρ (démonstration, point 3).
3. Sur ce tirage, `W` observé vaut 0,944 s (la formule dit 1,00 s) et `L` vaut 2,812. Le produit du débit observé (2,979) par le W observé vaut **exactement** 2,812 : c'est l'argument d'aire, vérifié à 10⁻⁹ près. Avec le λ théorique de 3, on obtient 2,832, proche mais pas égal. L'écart entre 0,944 s et 1,00 s est le hasard de 20 000 tirages, pas une autre formule.
4. **Le tableau 1/(1 − ρ).** Pour ρ = 0,5, 0,8, 0,9, 0,95, on calcule `temps_sejour_mm1(rho_cible * 4.0, 4.0) / 0.25`, c'est-à-dire W divisé par le temps de service. Les facteurs sont 2, 5, 10 et 20, et l'`assert` vérifie qu'ils valent 1/(1 − ρ). Le temps de service, lui, n'a pas changé. Seule la file s'allonge. À ρ = 1, `temps_sejour_mm1(4.0, 4.0)` prend la branche `math.inf`.
5. **Le pool vocal**, λ = 12, μ = 4. `rho_pool(..., c=1)` vaut 12/4 = 3, supérieur à 1 : une instance ne suffit pas, la formule du temps de séjour ne s'applique même pas. `c = 3` donne 12/12 = 1 : frontière, toujours instable. `c = 4` donne 12/16 = 0,75, la même charge que dans la partie 2, et `instances_minimales` retrouve ce 4 pour une cible de 0,75, puis 5 pour une cible de 0,70 (12/20 = 0,6). Mais ce n'est pas le même temps de séjour : quatre instances qui se partagent une seule file attendent beaucoup moins qu'un agent seul à la même charge. Le calcul se fait par Erlang C à l'étape 71, et donne W ≈ 0,377 s au lieu de 1 s. L'ancienne version de ce déroulé disait que c = 4 était « la charge dont on connaît le temps de séjour » : c'était confondre même ρ et même W.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`loi_de_little(lambd, W)`** — Cette fonction est le portier qui compte les invités sans jamais entrer dans la salle : elle reçoit le débit d'arrivée λ et le temps moyen de séjour W, et renvoie leur produit λW, le nombre moyen de requêtes présentes dans le système, selon la loi de Little. Elle ne vérifie rien et ne lève aucune exception, car la loi vaut pour toute file stable ; dans la section 2 de `main`, trois requêtes par seconde qui restent chacune 1 seconde donnent ainsi 3 requêtes présentes en moyenne.

**`rho_un_serveur(lambd, mu)`** — Celle-ci mesure à quel point l'unique agent a les bras chargés, comme un contremaître qui note la part de la journée où l'ouvrier ne lève pas la tête : elle reçoit le débit d'arrivée λ et le débit de service μ, et renvoie leur rapport ρ = λ/μ, la fraction du temps où le serveur est occupé. Elle ne contrôle pas que ρ reste sous 1, condition d'un régime stable que d'autres fonctions surveillent ; avec λ = 3 et μ = 4, elle rend 0,75.

**`rho_pool(lambd, mu, c)`** — Cette fonction généralise la précédente à une équipe de c agents identiques qui se partagent une seule file, comme un chef d'atelier qui répartit la charge entre plusieurs établis : elle reçoit λ, μ et le nombre d'instances c, et renvoie λ/(cμ), la charge de chaque instance. Pour l'agent vocal de la section 5, avec λ = 12 et μ = 4, elle rend 3 pour une seule instance, 1 pour trois instances, frontière encore instable, et 0,75 pour quatre.

**`instances_minimales(lambd, mu, rho_cible)`** — Celle-ci est le recruteur qui embauche un agent de plus tant que l'équipe reste surchargée : elle reçoit λ, μ et la charge visée, lève une `ValueError` si cette cible n'est pas strictement comprise entre 0 et 1, puis part d'une seule instance et en ajoute une tant que `rho_pool` dépasse la cible. La boucle finit toujours, puisque λ/(cμ) décroît vers 0, et la fonction renvoie le plus petit nombre d'instances qui suffit : 4 pour une cible de 0,75 et 5 pour une cible de 0,70, avec λ = 12 et μ = 4.

**`temps_sejour_mm1(lambd, mu)`** — Cette fonction chronomètre le passage moyen d'une requête dans une file M/M/1, du seuil de la porte jusqu'à la sortie : elle reçoit λ et μ, renvoie `math.inf` dès que λ atteint ou dépasse μ, parce que la file ne se vide alors jamais, et renvoie sinon 1/(μ − λ). Avec λ = 3 et μ = 4, elle donne 1 seconde, quatre fois le temps de service de 0,25 s ; c'est elle que `main` appelle pour dresser le tableau du multiplicateur 1/(1 − ρ), qui vaut 2, 5, 10 puis 20 quand ρ passe de 0,5 à 0,95.

**`mesures_mm1(lambd, mu)`** — Celle-ci dresse le bulletin complet de la file M/M/1, comme un inspecteur qui remplit toutes les cases de son rapport d'un coup : elle reçoit λ et μ, lève une `ValueError` si λ ≥ μ, puisqu'un tableau de mesures infinies n'aurait pas de sens, puis calcule ρ, le séjour W = 1/(μ − λ), l'attente en file Wq obtenue en retirant le temps de service 1/μ, et les deux nombres moyens L = λW et Lq = λWq. Elle renvoie ces cinq valeurs dans un dictionnaire ; pour λ = 3 et μ = 4, on lit Wq = 0,75 s et Lq = 2,25, et l'écart L − Lq vaut bien ρ = 0,75.

**`trace_fifo(arrivees, durees)`** — Cette fonction joue le guichet unique servi dans l'ordre d'arrivée, en tenant le registre de chaque client : elle reçoit les instants d'arrivée et les durées de service, deux listes que `zip(..., strict=True)` oblige à avoir la même longueur, puis, pour chaque requête, fait commencer le service au plus tard de son arrivée et de la libération du guichet, note la fin, le séjour et deux événements, une arrivée marquée +1 et un départ marqué −1. Elle trie ces événements dans l'ordre du temps et renvoie les séjours et les événements ; sur la trace à quatre requêtes, les séjours valent 1 ; 1,5 ; 1,5 et 0,5 seconde.

**`aire_sous_N(evenements)`** — Celle-ci rejoue la courbe du nombre de présents, comme un gardien de musée qui multiplie, à chaque changement, le nombre de visiteurs dans la salle par le temps écoulé depuis le changement précédent : elle reçoit la liste triée des événements, accumule ces rectangles, met à jour le nombre de présents avec le +1 ou le −1 de l'événement, puis vérifie par un `assert` que le système finit vide, sans quoi l'égalité avec la somme des séjours ne tiendrait plus. Elle renvoie l'aire sous N(t), qui vaut 4,5 sur l'exemple à quatre requêtes, exactement la somme des séjours, ce qui est l'argument d'aire de la loi de Little.

**`simuler_mm1(lambd, mu, n_clients, graine)`** — Cette fonction fait vivre une vraie file M/M/1 sans brancher la formule, comme un laboratoire qui rejoue vingt mille journées au lieu de croire la théorie sur parole : elle reçoit λ, μ, le nombre de clients et une graine, zéro par défaut, avance une horloge simulée par des délais exponentiels de moyenne 1/λ, tire pour chaque client un service exponentiel de moyenne 1/μ, puis confie le tout à `trace_fifo` et mesure l'aire avec `aire_sous_N` jusqu'au dernier départ T. Elle renvoie le séjour moyen observé, le nombre moyen observé, aire divisée par T, et le débit observé, nombre de clients divisé par T ; avec la graine 1 et 20 000 requêtes, cela donne 0,944 s, 2,812 et 2,979.

**`main()`** — C'est le professeur qui déroule la leçon en cinq tableaux successifs : il vérifie d'abord à la main, sur quatre requêtes, que l'aire 4,5 égale la somme des séjours et que L̂ = 1,2857 = λ̂ × Ŵ, puis calcule pour l'agent unique ρ = 0,75, W = 1 s, L = 3, Wq = 0,75 s et Lq = 2,25. Il simule ensuite la même file sur 20 000 requêtes pour montrer que Little tient exactement sur les grandeurs observées, dresse le tableau du multiplicateur 1/(1 − ρ) jusqu'à l'infini de ρ = 1, et termine par l'agent vocal à λ = 12, pour lequel `instances_minimales` retient 4 instances à la cible de 0,75 et 5 à celle de 0,70 ; chaque étape est verrouillée par des `assert`.

```python
"""Étape 69 — loi de Little par l'argument d'aire, file M/M/1, et le nombre d'instances à lancer."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def loi_de_little(lambd: float, W: float) -> float:
    """L = λ W."""
    return lambd * W


def rho_un_serveur(lambd: float, mu: float) -> float:
    """ρ = λ / μ. Le système n'a un régime stable que si ρ < 1."""
    return lambd / mu


def rho_pool(lambd: float, mu: float, c: int) -> float:
    """ρ = λ / (c μ) quand c agents identiques travaillent en parallèle."""
    return lambd / (c * mu)


def instances_minimales(lambd: float, mu: float, rho_cible: float) -> int:
    """Plus petit c tel que λ / (c μ) ≤ ρ_cible, avec 0 < ρ_cible < 1."""
    if not 0 < rho_cible < 1:
        raise ValueError("il faut 0 < ρ_cible < 1")
    c = 1
    while rho_pool(lambd, mu, c) > rho_cible:
        c += 1
    return c


def temps_sejour_mm1(lambd: float, mu: float) -> float:
    """W = 1 / (μ − λ) = T_service / (1 − ρ). Infini si λ ≥ μ."""
    if lambd >= mu:
        return math.inf
    return 1.0 / (mu - lambd)


def mesures_mm1(lambd: float, mu: float) -> dict[str, float]:
    """W, L, Wq, Lq d'une file M/M/1 (démontrées à l'étape 70)."""
    if lambd >= mu:
        raise ValueError("λ ≥ μ : pas de régime stable")
    rho = lambd / mu
    W = 1.0 / (mu - lambd)
    Wq = W - 1.0 / mu              # on retire le service : il reste l'attente
    return {"rho": rho, "W": W, "L": lambd * W, "Wq": Wq, "Lq": lambd * Wq}


def trace_fifo(arrivees: list[float], durees: list[float]) -> tuple[list[float], list[tuple[float, int]]]:
    """Un guichet FIFO. Renvoie les séjours et les événements (instant, +1 arrivée / −1 départ)."""
    libre_a = 0.0
    sejours = []
    evenements = []
    for arrivee, duree in zip(arrivees, durees, strict=True):
        debut_service = max(arrivee, libre_a)   # le max est toute la file d'attente
        fin = debut_service + duree
        libre_a = fin
        sejours.append(fin - arrivee)
        evenements.append((arrivee, +1))
        evenements.append((fin, -1))
    evenements.sort()
    return sejours, evenements


def aire_sous_N(evenements: list[tuple[float, int]]) -> float:
    """∫ N(t) dt : nombre de présents multiplié par la durée pendant laquelle ce nombre a tenu."""
    present = 0
    precedent = 0.0
    aire = 0.0
    for instant, delta in evenements:
        aire += present * (instant - precedent)
        present += delta
        precedent = instant
    assert present == 0, "le système doit être vide à la fin de la trace"
    return aire


def simuler_mm1(lambd: float, mu: float, n_clients: int, graine: int = 0) -> tuple[float, float, float]:
    """Inter-arrivées et services exponentiels, horloge simulée. Renvoie (W observé, L observé, λ observé)."""
    rng = random.Random(graine)
    horloge = 0.0
    arrivees, durees = [], []
    for _ in range(n_clients):
        horloge += rng.expovariate(lambd)
        arrivees.append(horloge)
        durees.append(rng.expovariate(mu))
    sejours, evenements = trace_fifo(arrivees, durees)
    T = evenements[-1][0]                    # dernier départ : le système est vide
    W = sum(sejours) / n_clients
    L = aire_sous_N(evenements) / T
    return W, L, n_clients / T


def main() -> None:
    print("=== 1. Little à la main : 4 requêtes, aire sous N(t) = somme des séjours ===")
    arrivees = [0.0, 0.5, 1.0, 3.0]
    durees = [1.0, 1.0, 0.5, 0.5]
    sejours, evenements = trace_fifo(arrivees, durees)
    aire = aire_sous_N(evenements)
    T = evenements[-1][0]
    print(f"  séjours = {sejours}   somme = {sum(sejours)}")
    print(f"  aire sous N(t) sur [0 ; {T}] = {aire}")
    print(f"  L = {aire / T:.4f}   λ = {len(arrivees) / T:.4f}   W = {sum(sejours) / len(arrivees):.4f}"
          f"   λ × W = {len(arrivees) / T * sum(sejours) / len(arrivees):.4f}")
    assert sejours == [1.0, 1.5, 1.5, 0.5] and aire == sum(sejours) == 4.5
    assert abs(aire / T - (len(arrivees) / T) * (sum(sejours) / len(arrivees))) < 1e-12

    print("\n=== 2. Un agent, λ = 3 req/s, μ = 4 req/s ===")
    lambd, mu = 3.0, 4.0
    rho = rho_un_serveur(lambd, mu)
    W = temps_sejour_mm1(lambd, mu)
    L = loi_de_little(lambd, W)
    T_service = 1.0 / mu
    m = mesures_mm1(lambd, mu)
    print(f"  ρ = {lambd:.0f}/{mu:.0f} = {rho:.2f}")
    print(f"  T_service = 1/μ = {T_service:.2f} s")
    print(f"  W = T_service / (1 − ρ) = {T_service:.2f} / {1 - rho:.2f} = {W:.2f} s")
    print(f"  L = λ W = {L:.2f} requêtes présentes en moyenne")
    print(f"  Wq = W − 1/μ = {m['Wq']:.2f} s   Lq = λ Wq = {m['Lq']:.2f}   L − Lq = {m['L'] - m['Lq']:.2f} = ρ")
    assert abs(rho - 0.75) < 1e-12 and abs(W - 1.0) < 1e-12 and abs(L - 3.0) < 1e-12
    assert abs(L - rho / (1.0 - rho)) < 1e-12
    assert abs(m["Wq"] - 0.75) < 1e-12 and abs(m["Lq"] - 2.25) < 1e-12
    assert abs(m["Lq"] - rho ** 2 / (1 - rho)) < 1e-12 and abs((m["L"] - m["Lq"]) - rho) < 1e-12

    print("\n=== 3. La même file, simulée (graine 1, horloge simulée) ===")
    W_obs, L_obs, lambd_obs = simuler_mm1(lambd, mu, n_clients=20_000, graine=1)
    print(f"  sur 20 000 requêtes : W observé = {W_obs:.3f} s   L observé = {L_obs:.3f}   λ observé = {lambd_obs:.3f}")
    print(f"  Little sur l'observation : λ observé × W observé = {lambd_obs * W_obs:.3f}   (égal à L observé)")
    print(f"  avec le λ théorique : 3 × W observé = {lambd * W_obs:.3f}")
    assert abs(L_obs - lambd_obs * W_obs) < 1e-9       # identité exacte : aire = somme des séjours
    assert abs(W_obs - W) < 0.08 and abs(L_obs - lambd * W_obs) < 0.08

    print("\n=== 4. Le multiplicateur 1/(1−ρ) : pourquoi 95 % de charge est une panne ===")
    print(f"  {'ρ':>6}  {'W / T_service':>14}")
    for rho_cible in (0.50, 0.80, 0.90, 0.95, 1.00):
        if rho_cible >= 1.0:
            print(f"  {rho_cible:6.2f}  {'infini':>14}")
            continue
        # On fixe μ = 4 et on choisit λ = ρ μ.
        facteur = temps_sejour_mm1(rho_cible * 4.0, 4.0) / 0.25
        print(f"  {rho_cible:6.2f}  {facteur:13.1f}×")
        assert abs(facteur - 1.0 / (1.0 - rho_cible)) < 1e-9
    assert temps_sejour_mm1(4.0, 4.0) == math.inf

    print("\n=== 5. L'agent vocal : λ = 12 req/s, μ = 4 req/s par instance ===")
    lambd, mu = 12.0, 4.0
    print(f"  une instance : ρ = {rho_pool(lambd, mu, c=1):.2f}  (> 1, la file grandit sans limite)")
    for c in (3, 4, 5):
        charge = rho_pool(lambd, mu, c)
        etat = "instable" if charge >= 1.0 else "stable"
        print(f"  c = {c} instances   ρ = 12 / ({c} × 4) = {charge:.2f}   {etat}")
    assert rho_pool(12.0, 4.0, 3) == 1.0
    assert abs(rho_pool(12.0, 4.0, 4) - 0.75) < 1e-12
    c_75, c_70 = instances_minimales(lambd, mu, 0.75), instances_minimales(lambd, mu, 0.70)
    print(f"  plus petit c pour ρ ≤ 0.75 : {c_75}   pour ρ ≤ 0.70 : {c_70}")
    assert c_75 == 4 and c_70 == 5
    print("  c = 3 est la frontière mathématique, pas une cible. On dimensionne vers ρ ≈ 0.75,")
    print("  donc 4 instances ; leur temps de séjour se calcule par Erlang C (étape 71).")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
=== 1. Little à la main : 4 requêtes, aire sous N(t) = somme des séjours ===
  séjours = [1.0, 1.5, 1.5, 0.5]   somme = 4.5
  aire sous N(t) sur [0 ; 3.5] = 4.5
  L = 1.2857   λ = 1.1429   W = 1.1250   λ × W = 1.2857
=== 2. Un agent, λ = 3 req/s, μ = 4 req/s ===
…
  W = T_service / (1 − ρ) = 0.25 / 0.25 = 1.00 s
  L = λ W = 3.00 requêtes présentes en moyenne
  Wq = W − 1/μ = 0.75 s   Lq = λ Wq = 2.25   L − Lq = 0.75 = ρ
=== 3. La même file, simulée (graine 1, horloge simulée) ===
  sur 20 000 requêtes : W observé = 0.944 s   L observé = 2.812   λ observé = 2.979
  Little sur l'observation : λ observé × W observé = 2.812   (égal à L observé)
=== 4. Le multiplicateur 1/(1−ρ) : pourquoi 95 % de charge est une panne ===
…
    0.90           10.0×
    0.95           20.0×
=== 5. L'agent vocal : λ = 12 req/s, μ = 4 req/s par instance ===
…
  c = 4 instances   ρ = 12 / (4 × 4) = 0.75   stable
…
  plus petit c pour ρ ≤ 0.75 : 4   pour ρ ≤ 0.70 : 5
…
OK — toutes les vérifications sont passées.
```

À retenir au moment de fixer un autoscaler : la latence n'est pas proportionnelle à la charge. Entre ρ = 0,5 et ρ = 0,9, le temps passé dans le système est multiplié par 5 pour le même temps de génération. Ajouter une instance baisse ρ = λ/(cμ). Rendre le modèle plus rapide augmente μ. Les deux jouent sur le même dénominateur.

## Squelette algorithmique

Trois algorithmes suffisent pour refaire ce fichier de tête. Le premier est une simulation à événements discrets d'un guichet FIFO : il reçoit les instants d'arrivée et les durées de traitement, et rend le nombre moyen de présents L̂, le débit λ̂ et le séjour moyen Ŵ observés sur la trace. L'idée est de faire passer chaque requête par le guichet avec un simple maximum, puis de rejouer la courbe N(t) dans l'ordre du temps pour mesurer son aire. Le deuxième est le calcul analytique de M/M/1 : il reçoit λ et μ et rend les quatre mesures. Le troisième dimensionne : il reçoit λ, μ et une charge visée, et rend le plus petit nombre d'instances qui la respecte.

```text
ALGORITHME SimulerFileFIFO          (simulation à événements discrets, un guichet)
ENTRÉES : instants d'arrivée a[1..n] croissants, durées de traitement s[1..n]
SORTIE : L̂, λ̂, Ŵ observés sur la trace
  libre ← 0 ; séjours ← liste vide ; événements ← liste vide
  POUR i DE 1 À n FAIRE
    début ← max(a[i], libre)                  // attendre que le guichet se libère
    fin ← début + s[i]
    libre ← fin
    ajouter fin − a[i] à séjours
    ajouter (a[i], +1) et (fin, −1) à événements
  FIN POUR
  trier événements par instant croissant
  présents ← 0 ; précédent ← 0 ; aire ← 0
  POUR CHAQUE (instant, δ) DE événements FAIRE
    aire ← aire + présents × (instant − précédent)
    présents ← présents + δ
    précédent ← instant
  FIN POUR
  SI présents ≠ 0 ALORS
    ÉCHOUER « la trace doit finir vide »
  FIN SI
  T ← instant du dernier événement
  RETOURNER (aire / T, n / T, (Σ séjours) / n)   // L̂ = λ̂ × Ŵ, exactement

ALGORITHME MesuresMM1               (calcul analytique)
ENTRÉES : λ > 0, μ > 0
SORTIE : ρ, W, L, Wq, Lq
  SI λ ≥ μ ALORS
    ÉCHOUER « pas de régime stable »          // le séjour moyen vaut ∞
  SINON
    ρ ← λ / μ
    W ← 1 / (μ − λ)
    Wq ← W − 1 / μ
    RETOURNER (ρ, W, λ × W, Wq, λ × Wq)
  FIN SI

ALGORITHME InstancesMinimales       (dimensionnement par la charge)
ENTRÉES : λ > 0, μ > 0, ρ_cible avec 0 < ρ_cible < 1
SORTIE : le plus petit c tel que λ / (c × μ) ≤ ρ_cible
  c ← 1
  TANT QUE λ / (c × μ) > ρ_cible FAIRE
    c ← c + 1
  FIN TANT QUE
  RETOURNER c
```

**Complexité :** dans `SimulerFileFIFO`, la première boucle fait un nombre constant d'opérations par requête, soit O(n). Le tri des 2n événements coûte O(n log n) et domine le total ; on pourrait le remplacer par une fusion en O(n), parce qu'avec un seul guichet FIFO les arrivées et les départs sont déjà chacun dans l'ordre, mais le tri est plus simple à relire. Le rejeu de la courbe N(t) est une boucle de 2n tours, O(n). La mémoire est O(n) : n séjours et 2n événements. `simuler_mm1` ajoute le tirage de 2n nombres aléatoires, encore O(n). `MesuresMM1` fait cinq opérations : O(1) en temps et en mémoire. `InstancesMinimales` fait un tour par valeur de c essayée, soit c* tours où c* est la réponse (environ λ/(μ × ρ_cible)) : O(c*) en temps et O(1) en mémoire ; on pourrait calculer c* directement par une partie entière supérieure, mais la boucle évite les pièges d'arrondi pile sur la frontière, comme 12/(4 × 0,75) = 4.

**Du squelette au code :** la première boucle de `SimulerFileFIFO` est la boucle `for arrivee, duree in zip(...)` de `trace_fifo`, ligne pour ligne (`debut_service = max(arrivee, libre_a)`, `fin`, `libre_a = fin`, les deux `append`) ; le « trier » est `evenements.sort()`, à la fin de la même fonction. La seconde boucle, le test « présents ≠ 0 » et l'aire sont `aire_sous_N`. Le calcul de T et des trois moyennes est la fin de `simuler_mm1`, qui fabrique aussi les listes a et s avec `rng.expovariate` sur une horloge simulée ; le bloc 1 de `main()` applique les mêmes fonctions à la trace de quatre requêtes. `MesuresMM1` est `mesures_mm1` (et `temps_sejour_mm1`, qui renvoie `math.inf` au lieu d'échouer). `InstancesMinimales` est `instances_minimales`, dont la condition du `while` appelle `rho_pool`.

## Cas d'usage réels aux Émirats

Les débits, durées et seuils ci-dessous sont illustratifs : en production, on les mesure sur les journaux de chaque service. Les calculs de séjour lisent chaque file comme une M/M/1 (étape 70) ; la loi de Little, elle, ne suppose rien.

### BTP — un stock de factures qui dit combien de temps on paie en retard

Un groupe de construction qui mène de grands chantiers à Dubaï fait contrôler par un agent les factures de ses sous-traitants : TVA à 5 %, retenue de garantie conforme au contrat, rattachement au bon de commande. Certaines factures demandent une validation humaine, d'autres passent en une minute : personne ne connaît la loi des durées de traitement. L'équipe mesure seulement deux nombres, le stock moyen de factures en cours (1 800) et le débit d'arrivée (600 par jour ouvré). Little donne directement W = 1 800/600 = 3 jours ouvrés, sans aucune hypothèse de loi. Si le contrat-cadre promet un traitement en 5 jours, le stock ne doit pas dépasser 600 × 5 = 3 000 factures : c'est ce seuil que surveille l'agent, au lieu de chronométrer chaque facture. Sans Little, l'équipe regardait le nombre de factures traitées par jour, qui égale le débit d'arrivée en régime stable et ne dit rien du retard. Les factures doivent rester des factures fiscales valides au sens de la TVA, et les retenues de garantie ne sont libérées qu'aux jalons du contrat ; l'indicateur suivi est le stock quotidien, et W = L/λ chaque semaine.

### Banque — un agent KYC dont la charge passe de 0,6 à 0,9

Une banque de détail de Dubaï fait vérifier par un agent les pièces d'ouverture de compte : format de l'Emirates ID, justificatif d'adresse, cohérence avec le formulaire. Chaque vérification prend en moyenne 20 s par instance, soit μ = 3 dossiers par minute ; en temps normal, chaque instance en reçoit 1,8 par minute, donc ρ = 0,6 et W = 20/(1 − 0,6) = 50 s. Pendant une campagne promotionnelle, le débit monte à 2,7 par minute et par instance : ρ = 0,9 et W = 20/0,1 = 200 s. La charge a augmenté de 50 %, le délai a été multiplié par 4. La décision est de faire démarrer une instance supplémentaire dès que ρ dépasse 0,75 sur une fenêtre d'une minute, ce qui borne W à 80 s. Sans ce seuil, les clients abandonnent l'ouverture en ligne au moment précis où la banque paie pour les attirer. La tentation d'accélérer en sautant des contrôles est exclue : les obligations KYC et de lutte contre le blanchiment suivies par la CBUAE ne se négocient pas contre la latence. Les indicateurs suivis sont ρ par instance, W, et le taux d'abandon du parcours.

### Crypto — un outil de filtrage qui fait basculer la file

Une plateforme d'actifs virtuels agréée par la VARA fait passer chaque demande de retrait au-dessus d'un seuil par un agent de contrôle : filtrage de l'adresse de destination par un outil externe, puis cohérence avec le profil KYC du client. Au pic, il arrive 0,5 demande par seconde ; l'outil externe répond en 1,2 s et l'agent lui-même travaille 0,3 s, soit un service de 1,5 s. Une seule instance est chargée à ρ = 0,5 × 1,5 = 0,75, et son temps de séjour vaut 1,5/0,25 = 6 s. Un jour, l'outil externe ralentit à 2 s : le service passe à 2,3 s et ρ à 1,15. La file n'a plus de régime stable et grossit de minute en minute, parce que c'est le temps de service, donc μ, que le ralentissement a touché. La décision est de passer à trois instances (ρ = 1,15/3 ≈ 0,38), avec un délai maximal sur l'appel à l'outil ; à l'expiration, le retrait reste bloqué et part en revue humaine, il n'est jamais libéré sans contrôle. Les indicateurs suivis sont ρ, le p95 du séjour et la part de retraits bloqués par expiration.

### Secteur public — une date limite qui double le trafic

Une entité de services publics en ligne, accessible par UAE Pass, fait répondre un agent bilingue arabe et anglais aux questions sur le renouvellement d'une démarche. En temps normal, chaque instance tourne à ρ = 0,45. À l'approche de la date limite, le trafic double : sans nouvelle instance, ρ passe à 0,9 et le séjour est multiplié par (1 − 0,45)/(1 − 0,9) = 5,5, pour le même modèle et les mêmes réponses. La date est connue à l'avance : l'équipe double le nombre d'instances la veille, ce qui ramène ρ à 0,45. Little donne un second message, souvent oublié : avec un débit doublé et un séjour inchangé, le nombre de conversations ouvertes L double aussi, et le stockage des sessions doit le suivre. Comme la PDPL demande de ne conserver les données personnelles que le temps nécessaire, ces sessions sont purgées à la fin de chaque conversation et non gardées « au cas où ». Les indicateurs suivis sont ρ, W et le nombre de sessions ouvertes.

### RH — combien de dossiers de visa sont « en cours »

Un cabinet RH présent dans plusieurs émirats fait suivre par un agent chaque dossier de recrutement : permis d'entrée, visite médicale, Emirates ID, contrat enregistré au MOHRE. Il ouvre 120 nouveaux dossiers par jour, et un dossier met en moyenne 9 jours à aboutir. Little donne L = 120 × 9 = 1 080 dossiers en cours en permanence : c'est le nombre de dossiers que la mémoire et l'outil de relance de l'agent doivent suivre en même temps, et le nombre de candidats susceptibles de demander où en est leur visa. Si une étape administrative s'allonge de 3 jours, L monte à 120 × 12 = 1 440, soit 360 dossiers de plus à suivre, sans qu'un seul recrutement supplémentaire ait eu lieu. La décision est de dimensionner les relances et l'équipe humaine sur L, et de déclencher une alerte dès que L/λ dépasse l'objectif de délai. Sans Little, le cabinet aurait cherché la cause de la hausse dans les arrivées, alors qu'elle vient du séjour. L'indicateur suivi est L chaque jour, avec W = L/λ en tendance.

### Immobilier — un outil bloquant dans le service

Une agence immobilière de Dubaï fait répondre un agent aux demandes des acheteurs et des locataires ; pour chaque réponse, il appelle un outil qui vérifie le statut de l'annonce et les informations Ejari, et cet appel dure 2 s. Le service vaut 3 s (1 s de génération et 2 s d'attente de l'outil), soit μ = 1/3 par seconde ; à 0,25 demande par seconde, ρ = 0,75 et le séjour vaut 3/0,25 = 12 s. L'équipe met en cache le statut des annonces, qui change peu, pendant quelques minutes : l'appel tombe à 0,2 s, le service à 1,2 s, ρ à 0,3 et le séjour à 1,2/0,7 ≈ 1,7 s. Raccourcir le service de 60 % a divisé le séjour par 7, parce que le gain passe aussi par le facteur 1/(1 − ρ). Le cache est réservé aux données de consultation : une donnée qui engage une transaction, comme le titulaire d'un bien avant un transfert au DLD, est toujours relue à la source. L'indicateur suivi est la part du temps de service passée à attendre des outils.

## Pièges et limites

- **Mesurer le débit au lieu du délai.** En régime stable, le débit de sortie égale le débit d'arrivée : il ne dit rien de l'attente. C'est L/λ qui la donne.
- **Appliquer Little sur une fenêtre qui n'est pas stationnaire.** Pendant une montée de charge, le stock grossit et L̂/λ̂ sous-estime le séjour des requêtes qui arrivent. On choisit des fenêtres où le stock revient à un niveau comparable, ou l'on compte les séjours en cours.
- **Mélanger les unités.** λ par minute et W en secondes donnent un L faux d'un facteur 60.
- **Lire λ/(cμ) > 1 comme une utilisation.** Au-delà de 1, ce n'est plus une fraction du temps occupé mais une charge offerte, et la file croît sans limite.
- **Croire que 1/(1 − ρ) vaut pour toutes les files.** C'est le facteur exact de M/M/1. Avec plusieurs instances ou d'autres lois, la forme reste (explosion quand ρ tend vers 1), mais les nombres changent : étapes 68 et 71.

### Exercice feuille blanche

1. Sans regarder le code, écrire `trace_fifo` et `aire_sous_N`, puis vérifier sur la trace à quatre requêtes que l'aire vaut 4,5 et que L̂ = λ̂ × Ŵ.
2. Prédire, puis vérifier avec `mesures_mm1(3.6, 4.0)` : que valent ρ, W, L, Wq et Lq ? (Réponse : 0,9 ; 2,5 s ; 9 ; 2,25 s ; 8,1.)
3. Trouver le bug : dans `trace_fifo`, la ligne `debut_service = arrivee` remplace `max(arrivee, libre_a)`. Que devient le séjour moyen, et quel système simule-t-on en réalité ? (Indice : la loi de Little reste vraie sur la trace, mais pour une file où personne n'attend jamais, comme s'il y avait une infinité d'agents.)

## Pour aller plus loin

La loi de Little vaut classe par classe, pour un réseau de files entier et pour toute discipline ; sa preuve « trajectoire par trajectoire » est due à Stidham (1974). Il en existe une version en loi (distributional Little's law), qui relie la loi du nombre de clients à celle du séjour sous des hypothèses plus fortes. Les étapes 70 et 71 démontrent les formules de M/M/1 et de M/M/c ; l'étape 68 donne Pollaczek-Khinchine pour un service quelconque.

> Suite : [File M/M/1](<70-File-MM1.md>) — étape 70.
