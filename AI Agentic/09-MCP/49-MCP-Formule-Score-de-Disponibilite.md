# Étape 49 — MCP — Score de disponibilité d'un serveur MCP

> Étape 49 du parcours · Prérequis : [MCP par domaine](<48-MCP-Applications-Domaines.md>) · Suite : [A2A et édition par diff](<49b-A2A-et-Edition-par-Diff.md>)

**Dossier :** 09-MCP  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Agent Ops, Forward-Deployed Engineers, AI Platform Team  

**Nom du fichier :** 49-MCP-Formule-Score-de-Disponibilite.md

Ce fichier se lit deux fois. La première, après l'étape 48, pour la formule elle-même et ses compositions. La seconde, après l'étape 71 : on y retrouve la section 7 de la démonstration, qui relie la disponibilité à la charge du serveur.

## Définition

La disponibilité d'un serveur MCP est la part du service qu'il rend correctement. Elle se mesure de deux façons. **Par requêtes**, c'est la proportion de requêtes qui ont reçu une réponse valide avant le timeout du client, sur l'ensemble des requêtes envoyées pendant une fenêtre. **Dans le temps**, c'est la proportion du temps pendant laquelle le serveur fonctionne, qui s'exprime avec la durée moyenne de bon fonctionnement entre deux pannes (MTBF) et la durée moyenne de réparation (MTTR). L'ancienne version de ce fichier multipliait le taux de succès par (1 − taux de timeout), ce qui compte deux fois chaque timeout ; la formule correcte est un simple rapport, indéfini quand il n'y a eu aucune requête.

## Rôle dans un agent

La disponibilité sert avant que l'agent n'agisse, et pendant. Avant, le host choisit à quels serveurs se brancher et vers quelle réplique envoyer un `tools/call` : un serveur souvent en panne ne doit pas être choisi, ou doit être doublé. Pendant la boucle percevoir → décider → agir → observer, chaque appel d'outil est une étape de plus qui peut échouer : la disponibilité de la chaîne de serveurs traversés par une requête se compose par produit (étapes 1 et 12), et c'est elle qui fixe la fiabilité de l'étape « agir ». Après, en production, la disponibilité mesurée se compare à un objectif (SLO) et à un budget d'erreur, qui décident s'il faut alerter, geler les déploiements ou ajouter des instances.

## Équation complète

Disponibilité par requêtes, définie seulement s'il y a eu du trafic :

$$
A_{req} = \frac{N_{ok}}{N} \qquad \text{pour} \qquad N > 0
$$

Cohérence des compteurs, vérifiée avant tout calcul :

$$
N_{ok} + N_{to} \le N
$$

Disponibilité dans le temps :

$$
A_{temps} = \frac{\mathrm{MTBF}}{\mathrm{MTBF} + \mathrm{MTTR}}
$$

Composition en série (démontrée à l'étape 12) et en parallèle (démontrée ici) :

$$
A_{serie} = \prod_{i=1}^{m} A_i
$$

$$
A_{par} = 1 - \prod_{i=1}^{m} \left(1 - A_i\right)
$$

Budget d'erreur d'un objectif A* sur une durée D, et vitesse de consommation de ce budget :

$$
D_{arret} = \left(1 - A^{*}\right) D
$$

$$
v = \frac{1 - A_{obs}}{1 - A^{*}}
$$

Sous charge, pour une file M/M/1 servie dans l'ordre d'arrivée (résultat admis ici, étapes 70 et 71) :

$$
P\left(\text{séjour} > t_{max}\right) = e^{-\mu (1 - \rho)\, t_{max}}
$$

## Décryptage des symboles

$$
N
$$

Le nombre total de requêtes envoyées au serveur pendant la fenêtre de mesure, un entier ≥ 0 ; variable Python `total`.

$$
N_{ok}
$$

Le nombre de requêtes réussies au sens de la disponibilité : une réponse valide reçue avant le timeout, y compris un échec métier (`isError` « compte inconnu ») ou une erreur due au client (−32602), parce que le serveur a fait son travail. Entier entre 0 et N ; variable `succes`.

$$
N_{to}
$$

Le nombre de requêtes expirées côté client, un entier ≥ 0 ; variable `timeouts`. Il sert à vérifier la cohérence des compteurs et au diagnostic, jamais à multiplier A une seconde fois.

$$
A_{req}
$$

La disponibilité par requêtes, un réel dans [0 ; 1], ou `None` si N = 0 ; valeur renvoyée par `disponibilite_requetes`.

$$
\mathrm{MTBF}
$$

La durée moyenne de bon fonctionnement entre deux pannes, un réel > 0, dans une unité de temps (ici des minutes) ; variable `mtbf`. Certains textes appellent cette durée MTTF et réservent MTBF à la somme MTTF + MTTR : la formule s'écrit alors MTTF / MTBF, et le résultat est le même.

$$
\mathrm{MTTR}
$$

La durée moyenne d'une panne, de la détection au retour du service, un réel ≥ 0 dans la même unité ; variable `mttr`.

$$
A_{temps}
$$

La disponibilité dans le temps, un réel dans ]0 ; 1] ; valeur renvoyée par `disponibilite_temporelle`.

$$
A_i
$$

La disponibilité du composant i (serveur, réplique, base de données), un réel dans [0 ; 1] ; un élément de la liste `dispos`.

$$
m
$$

Le nombre de composants composés, un entier ≥ 1 ; `len(dispos)`.

$$
A^{*}
$$

L'objectif de disponibilité (SLO), par exemple 0,999 ; variable `slo`.

$$
D
$$

La durée de la période de l'objectif, par exemple 30 jours, soit 43 200 minutes ; variable `jours`, convertie en minutes.

$$
D_{arret}
$$

La durée d'arrêt autorisée par l'objectif sur la période, en minutes ; valeur renvoyée par `budget_erreur_minutes`.

$$
v
$$

La vitesse de consommation du budget d'erreur : 1 si l'on échoue exactement au rythme permis, 5 si l'on consomme le budget cinq fois trop vite ; valeur renvoyée par `taux_de_consommation`.

$$
A_{obs}
$$

La disponibilité observée sur une fenêtre récente, par exemple la dernière heure ; on passe à la fonction le taux d'échec 1 − A_obs, variable `taux_echec_observe`.

$$
\lambda,\quad \mu,\quad \rho = \lambda / \mu
$$

Le taux d'arrivée des requêtes, le taux de service d'une instance (en requêtes par seconde) et leur rapport, la charge, dans [0 ; 1[ pour une file stable ; variables `lam`, `mu`, `rho`. Ici λ désigne un taux d'arrivée, comme aux étapes 69 à 71, et non un taux de décroissance.

$$
t_{max}
$$

Le timeout du client, en secondes ; variable `t_max`.

## Démonstration

### 1. Le défaut de l'ancienne formule : un contre-exemple chiffré

L'ancienne version de ce fichier calculait :

$$
A_{ancienne} = \frac{N_{ok}}{N} \times \left(1 - \frac{N_{to}}{N}\right)
$$

Prenons 100 requêtes : 90 réussissent et 10 expirent. La disponibilité vaut 90 / 100 = 0,90, puisque 90 requêtes sur 100 ont été servies. L'ancienne formule donne 0,90 × (1 − 0,10) = 0,81. L'erreur vient de ce que les 10 timeouts sont **déjà** dans les 10 requêtes non réussies, qui font passer le rapport de 1 à 0,90 ; le facteur (1 − 0,10) les retire une seconde fois. En général, l'ancienne formule vaut A_req × (1 − N_to / N), et l'écart avec la vraie valeur est :

$$
A_{req} - A_{ancienne} = A_{req} \cdot \frac{N_{to}}{N}
$$

ici 0,90 × 0,10 = 0,09. Avec 50 succès et 50 timeouts, elle donne 0,25 au lieu de 0,50. Pire, elle classe différemment deux serveurs qui rendent le même service : un serveur dont les 10 échecs sont des timeouts obtient 0,81, un serveur dont les 10 échecs sont des erreurs −32603 obtient 0,90. Le type de l'échec est un diagnostic, il ne doit pas changer la mesure du service rendu.

### 2. La disponibilité par requêtes est dans [0 ; 1], et indéfinie sans trafic

Comme 0 ≤ N_ok ≤ N, le quotient est entre 0 et 1 dès que N > 0. Quand N = 0, le quotient 0 / 0 n'a pas de sens : aucune requête n'a été envoyée, on ne sait donc rien du serveur. L'ancien code renvoyait 0,0 dans ce cas, ce qui déclarait « totalement en panne » un serveur simplement inutilisé, la nuit ou juste après un déploiement, et pouvait déclencher une alerte ou détourner le trafic à tort. Renvoyer 1,0 serait l'erreur inverse. La convention du parcours est de renvoyer `None`, que l'on exclut des moyennes. Enfin, si N_ok + N_to > N, les compteurs sont incohérents (un double comptage dans la collecte) : la fonction lève `ValueError` au lieu de calculer un nombre faux.

### 3. MTBF / (MTBF + MTTR) est une identité sur le journal des pannes

Sur une période de durée D, le journal enregistre K pannes, de durées d₁, …, d_K. Le temps de bon fonctionnement vaut U = D − (d₁ + … + d_K), et la disponibilité mesurée vaut U / D. Les moyennes empiriques sont MTBF = U / K et MTTR = (d₁ + … + d_K) / K. On remplace et on simplifie par K :

$$
\frac{\mathrm{MTBF}}{\mathrm{MTBF} + \mathrm{MTTR}} = \frac{U / K}{\left(U + \sum_{k} d_k\right) / K} = \frac{U}{D}
$$

La formule n'est donc pas une approximation : sur un journal, c'est exactement la part du temps en fonctionnement. Sur une longue durée, la loi des grands nombres donne le même résultat avec les espérances. Avec trois pannes de 14,4 minutes sur 30 jours (43 200 minutes), U = 43 200 − 43,2 = 43 156,8 minutes, MTBF = 14 385,6 minutes, MTTR = 14,4 minutes et la disponibilité vaut 0,999.

La forme de l'indisponibilité montre où agir :

$$
1 - A_{temps} = \frac{\mathrm{MTTR}}{\mathrm{MTBF} + \mathrm{MTTR}} \approx \frac{\mathrm{MTTR}}{\mathrm{MTBF}}
$$

quand MTTR est petit devant MTBF. Diviser MTTR par deux divise presque l'indisponibilité par deux : avec un MTTR de 7,2 minutes, on obtient 0,9995. Réparer plus vite (redémarrage automatique, procédure écrite, bascule) est souvent plus facile que tomber moins souvent en panne.

### 4. En série, les disponibilités se multiplient

Une requête qui traverse plusieurs serveurs ne réussit que si chacun répond. Si les pannes sont indépendantes, la règle de multiplication de l'étape 1 donne le produit ; la démonstration complète, avec les bornes valables sans indépendance, est à l'[étape 12](<../03-Schemas-Outils-et-Premiere-Evaluation/12-Outils-Definitions-Fondamentaux.md>). Trois serveurs à 0,99 donnent 0,99³ = 0,970299 : chaque composant ajouté en série fait baisser la disponibilité, parce que chaque facteur est au plus 1.

### 5. En parallèle : 1 − ∏(1 − Aᵢ), et deux répliques à 0,95 donnent 0,9975

Plaçons m répliques identiques derrière un répartiteur qui envoie la requête à une réplique vivante. Le service est indisponible seulement si **toutes** les répliques sont en panne en même temps. Notons Bᵢ l'événement « la réplique i est en panne », de probabilité 1 − Aᵢ. Si les pannes sont indépendantes, la probabilité que toutes soient en panne est le produit, parce que la probabilité d'une intersection d'événements indépendants est le produit de leurs probabilités :

$$
P\left(B_1 \cap \dots \cap B_m\right) = \prod_{i=1}^{m} \left(1 - A_i\right)
$$

Le service est disponible dans l'événement contraire, d'où la formule en passant au complément. Pour deux répliques à 0,95 :

$$
A_{par} = 1 - 0{,}05 \times 0{,}05 = 1 - 0{,}0025 = 0{,}9975
$$

Une troisième réplique donne 1 − 0,05³ = 0,999875 : chaque réplique multiplie l'indisponibilité par 0,05. Deux propriétés restent vraies **sans** l'hypothèse d'indépendance. Ajouter une réplique ne peut que faire monter la disponibilité, et le montage est au moins aussi disponible que sa meilleure réplique, parce que l'événement « au moins une réplique répond » contient l'événement « la réplique j répond » :

$$
A_{par} \ge \max_i A_i
$$

Avec deux répliques à 0,6 et 0,3, on obtient 1 − 0,4 × 0,7 = 0,72 ≥ 0,6. L'hypothèse d'indépendance, elle, est fragile : deux répliques qui partagent la même base de données tombent ensemble quand la base tombe. On modélise alors la base en série avec le bloc parallèle : 0,9975 × 0,999 = 0,9965025. Le maillon commun plafonne le gain des répliques.

### 6. Le budget d'erreur : 99,9 % sur 30 jours font 43,2 minutes

Un objectif A* sur une durée D autorise une durée d'arrêt (1 − A*) D. Sur 30 jours, D = 30 × 24 × 60 = 43 200 minutes, et pour A* = 0,999 :

$$
D_{arret} = 0{,}001 \times 43\,200 = 43{,}2 \text{ minutes}
$$

Mesuré en requêtes, le même objectif autorise 0,001 × 1 000 000 = 1 000 échecs sur un million de requêtes. Le budget se dépense : si l'on observe 0,5 % d'échecs sur la dernière heure, la vitesse de consommation vaut v = 0,005 / 0,001 = 5, et à ce rythme le budget de 30 jours est épuisé en 30 / 5 = 6 jours. C'est ce nombre qui décide : v proche de 1, on continue ; v nettement au-dessus de 1, on alerte et l'on gèle les déploiements risqués jusqu'au retour à la normale.

### 7. Sous charge, un serveur « en marche » peut être indisponible

Les sections précédentes supposent qu'un serveur en marche répond à temps. Ce n'est plus vrai quand il est chargé. Pour une instance modélisée par une file M/M/1 servie dans l'ordre d'arrivée, de taux d'arrivée λ et de taux de service μ, le temps de séjour d'une requête suit une loi exponentielle de paramètre μ − λ = μ(1 − ρ) ; ce résultat, admis ici, se rattache aux étapes [70](<../12-Production-Couts-Optimisation/70-File-MM1.md>) et [71](<../12-Production-Couts-Optimisation/71-Erlang-C.md>), et le programme le vérifie par simulation. La probabilité qu'une requête dépasse le timeout du client vaut donc e^(−μ(1−ρ)t_max), et elle borne la disponibilité par requêtes même si le serveur ne tombe jamais :

$$
A_{req} \le 1 - e^{-\mu (1 - \rho)\, t_{max}}
$$

Avec μ = 10 requêtes par seconde et un timeout de 2 s, une charge ρ = 0,5 donne e⁻¹⁰ ≈ 4,5 × 10⁻⁵ : le timeout est négligeable. À ρ = 0,9, on obtient e⁻² ≈ 0,1353, et la disponibilité par requêtes ne peut pas dépasser 0,8647 ; à ρ = 0,95, e⁻¹ ≈ 0,3679. La simulation de 200 000 requêtes à ρ = 0,9 mesure 0,1368, à 0,0015 de la théorie. La disponibilité dans le temps et la disponibilité par requêtes ne disent donc pas la même chose : la première mesure les pannes, la seconde le service réellement rendu, charge comprise. C'est pourquoi un `ping` qui répond ne prouve pas que les `tools/call` arrivent à temps.

### 8. Exemple fait à la main (le code reprend ces nombres)

| Grandeur | Calcul | Résultat |
|---|---|---|
| A, 90 succès et 10 timeouts sur 100 | 90 / 100 | 0,90 |
| ancienne formule, mêmes nombres | 0,90 × 0,90 | 0,81 (fausse) |
| A, journal de 12 issues | 10 / 12 | 0,8333 |
| A dans le temps, 3 pannes de 14,4 min sur 30 jours | 14 385,6 / 14 400 | 0,999 |
| même chose avec un MTTR de 7,2 min | 14 385,6 / 14 392,8 | 0,9995 |
| série, 3 × 0,99 | 0,99³ | 0,970299 |
| parallèle, 2 × 0,95 | 1 − 0,05² | 0,9975 |
| parallèle, 3 × 0,95 | 1 − 0,05³ | 0,999875 |
| 2 répliques à 0,95, puis une base à 0,999 | 0,9975 × 0,999 | 0,9965025 |
| budget d'arrêt, 99,9 % sur 30 jours | 0,001 × 43 200 | 43,2 min |
| vitesse de consommation à 0,5 % d'échecs | 0,005 / 0,001 | 5 |
| P(timeout), μ = 10, ρ = 0,9, t_max = 2 s | e⁻² | 0,1353 |

Dans le journal de 12 issues, huit appels ont réussi, un a renvoyé un `isError` métier, un a reçu −32602 parce que le client avait envoyé de mauvais arguments, un a reçu −32603 et un a expiré : le serveur a fait son travail dans 10 cas sur 12.

## Effets et comportement

- **Chaque échec retire 1/N.** Sur une fenêtre de 1 000 requêtes, un échec coûte 0,001 : un seul incident suffit à consommer tout le budget d'un objectif de 99,9 % sur cette fenêtre.
- **Une réplique en parallèle ne peut qu'aider, un composant en série ne peut que nuire.** Le gain d'une réplique est plafonné par les composants communs qu'elle partage.
- **Le MTTR compte autant que le MTBF.** L'indisponibilité est proche de MTTR / MTBF : diviser le temps de réparation par deux vaut presque autant que doubler le temps entre les pannes.
- **Sous charge, la disponibilité par requêtes s'effondre avant toute panne.** Quand ρ s'approche de 1, la part des requêtes qui expirent tend vers 1, alors que le serveur n'a jamais cessé de fonctionner.
- **Relancer augmente la probabilité de succès d'une requête, mais aussi la charge.** Avec des tentatives indépendantes, R relances donnent 1 − (1 − A)ᴿ⁺¹ (étape 11) ; sous charge, les tentatives ne sont plus indépendantes, et chaque relance augmente ρ.

## Du symbole au code Python

$$
A_{req} = N_{ok} / N
$$

**Variable ou fonction :** `disponibilite_requetes(succes, timeouts, total)`, qui renvoie `None` si `total == 0`

$$
\left(N_{ok} / N\right)\left(1 - N_{to} / N\right)
$$

**Variable ou fonction :** `disponibilite_ancienne(succes, total, taux_timeout)`, gardée pour le contre-exemple

$$
N_{ok}
$$

**Variable ou fonction :** `classer(issue)`, qui décide si une issue compte comme `"succes"`, `"timeout"` ou `"echec"`

$$
\mathrm{MTBF} / \left(\mathrm{MTBF} + \mathrm{MTTR}\right)
$$

**Variable ou fonction :** `disponibilite_temporelle(mtbf, mttr)`, et `depuis_journal(duree_totale, pannes)` pour mesurer les trois grandeurs

$$
\prod_i A_i, \qquad 1 - \prod_i \left(1 - A_i\right)
$$

**Variable ou fonction :** `disponibilite_serie(dispos)`, `disponibilite_parallele(dispos)` (code canonique du parcours)

$$
\left(1 - A^{*}\right) D, \qquad v
$$

**Variable ou fonction :** `budget_erreur_minutes(slo, jours)`, `taux_de_consommation(taux_echec_observe, slo)`

$$
e^{-\mu (1 - \rho)\, t_{max}}
$$

**Variable ou fonction :** `p_timeout_mm1(mu, rho, t_max)`, vérifiée par `simuler_mm1(lam, mu, t_max, n, graine)`

### Déroulé, ligne par ligne

**`disponibilite_requetes(succes, timeouts, total)`.** C'est la formule corrigée, avec ses deux gardes.

- `if min(succes, timeouts, total) < 0 or succes + timeouts > total` : un compteur négatif ou des compteurs qui dépassent le total trahissent une erreur de collecte. Avec `(95, 10, 100)`, on aurait 105 requêtes classées pour 100 envoyées : la fonction lève `ValueError` au lieu de renvoyer 0,95.
- `if total == 0: return None` : sans trafic, la disponibilité n'est pas définie.
- `return succes / total` : avec `(90, 10, 100)`, on obtient 0,90. Le paramètre `timeouts` ne sert qu'à la garde : il n'entre pas dans le calcul, c'est précisément la correction.

**`disponibilite_ancienne(succes, total, taux_timeout)`** reproduit l'ancienne formule, `(succes / total) * (1 - taux_timeout)`, pour la montrer fausse : 0,9 × 0,9 = 0,81.

**`classer(issue)`** applique la règle de la démonstration, point 8. Un `timeout` est un timeout. Une erreur JSON-RPC n'est un échec du serveur que si son code est −32603 ; −32602 signale des arguments invalides envoyés par le client, et le serveur a correctement répondu. Un résultat `isError` n'est un échec du serveur que si sa cause est technique (un service en aval indisponible) ; un `isError` métier, comme « compte inconnu », est une réponse correcte. Tout le reste est un succès.

**`disponibilite_temporelle(mtbf, mttr)`** renvoie `mtbf / (mtbf + mttr)` après avoir refusé un MTBF nul ou un MTTR négatif.

**`depuis_journal(duree_totale, pannes)`** reçoit des paires `(début, fin)` en minutes. Avec trois pannes de 14,4 minutes, `arrets = [14.4, 14.4, 14.4]` (à l'arrondi flottant près), `bon_fonctionnement = 43200 - 43.2 = 43156.8`, et la fonction renvoie la disponibilité mesurée 0,999, le MTBF 14 385,6 et le MTTR 14,4. Le programme vérifie que `disponibilite_temporelle` appliquée à ces moyennes redonne exactement la disponibilité mesurée (point 3).

**`disponibilite_serie` et `disponibilite_parallele`** sont les fonctions canoniques : `math.prod(dispos)` et `1 - math.prod(1 - a for a in dispos)`. Pour `[0.95, 0.95]`, le produit des indisponibilités vaut 0,0025 et la fonction renvoie 0,9975.

**`budget_erreur_minutes(slo, jours)`** calcule `(1 - slo) * jours * 24 * 60` : 0,001 × 43 200 = 43,2. **`taux_de_consommation(taux_echec_observe, slo)`** calcule `taux / (1 - slo)` : 0,005 / 0,001 = 5.

**`p_timeout_mm1(mu, rho, t_max)`** refuse `rho >= 1`, où la file n'est plus stable, puis renvoie `math.exp(-mu * (1 - rho) * t_max)` : pour `mu = 10`, `rho = 0.9`, `t_max = 2.0`, l'exposant vaut −2 et le résultat 0,1353.

**`simuler_mm1(lam, mu, t_max, n, graine)`** vérifie ce résultat sans l'admettre. Elle tire, avec un générateur à graine fixe, la durée de service de chaque requête (`rng.expovariate(mu)`, de moyenne 0,1 s) et l'intervalle avant la suivante (`rng.expovariate(lam)`, de moyenne 1/9 s). La récurrence de Lindley donne l'attente de la requête suivante : `attente = max(0.0, attente + service - inter_arrivee)`, parce que la suivante attend ce qui reste du travail en cours, ou rien si la file s'est vidée entre-temps. Le séjour d'une requête vaut `attente + service`, et l'on compte les séjours qui dépassent 2 s. Sur 200 000 requêtes, la fraction vaut 0,1368. L'horloge est entièrement simulée : rien n'attend réellement.

**`main()`**, section par section.

1. Le contre-exemple : 0,90 contre 0,81, l'écart égal à A × taux de timeout, le cas 50/50 (0,50 contre 0,25), `None` sans trafic et deux entrées incohérentes refusées.
2. Le journal de 12 issues donne 10 succès, 1 timeout, 1 échec serveur et A = 0,8333.
3. Le journal de pannes donne 43,2 minutes d'arrêt, MTBF = 14 385,6 minutes, MTTR = 14,4 minutes et A = 0,999 par les deux calculs ; avec un MTTR divisé par deux, 0,9995.
4. Série, parallèle à deux et trois répliques, montage mixte, et la borne `A_par >= max(A_i)` sur un exemple non symétrique.
5. Le budget : 43,2 minutes, 1 000 échecs par million, vitesse 5, épuisement en 6 jours.
6. La probabilité de timeout pour ρ = 0,5, 0,9 et 0,95, puis la simulation à ρ = 0,9, qui doit tomber à moins de 0,01 de e⁻².

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`disponibilite_requetes(succes, timeouts, total)`** — Cette fonction est le guichetier honnête qui tient le registre des requêtes reçues par le serveur MCP : elle reçoit le nombre de succès, le nombre de timeouts et le total des requêtes envoyées, et commence par vérifier que ces compteurs se tiennent, en levant `ValueError` si l'un d'eux est négatif ou si succès et timeouts réunis dépassent le total, comme dans le cas (95, 10, 100) où 105 requêtes seraient classées pour 100 envoyées. Si le total vaut zéro, elle renvoie `None`, car une fenêtre sans trafic ne dit rien de la santé du serveur ; sinon elle renvoie simplement succès ÷ total, soit 0,90 pour 90 succès sur 100. Le paramètre `timeouts` ne sert qu'à la garde et n'entre jamais dans la division : c'est précisément la correction de la formule, que `main` met à l'épreuve dans ses sections 1 et 2.

**`disponibilite_ancienne(succes, total, taux_timeout)`** — Celle-ci est conservée comme une pièce à conviction dans un dossier d'enquête : elle reproduit l'ancienne formule du fichier, qui multipliait le taux de succès par (1 − taux de timeout), sans aucune vérification sur ses trois arguments. Elle renvoie ce produit, faux parce que les requêtes perdues en timeout sont déjà absentes des succès et se retrouvent pénalisées une seconde fois : avec 90 succès sur 100 et un taux de timeout de 0,1, elle annonce 0,81 au lieu de 0,90, et 0,25 au lieu de 0,50 dans le cas 50/50. `main` ne s'en sert que pour mesurer l'écart avec la bonne formule, écart qui vaut exactement A × taux de timeout.

**`disponibilite_temporelle(mtbf, mttr)`** — Cette fonction regarde le serveur comme un veilleur de nuit qui note, sur un mois entier, les heures où la machine tourne et celles où elle est en réparation : elle reçoit la durée moyenne de bon fonctionnement entre deux pannes (MTBF) et la durée moyenne de réparation (MTTR), refuse par une `ValueError` un MTBF nul ou négatif et un MTTR négatif, puis renvoie MTBF ÷ (MTBF + MTTR), la part du temps où le service est debout. Dans `main`, appliquée aux moyennes tirées du journal de pannes, elle redonne exactement la disponibilité mesurée 0,999, et elle passe à 0,9995 quand on divise le MTTR par deux, ce qui montre le poids de la vitesse de réparation.

**`disponibilite_serie(dispos)`** — C'est la fonction de la chaîne de montage, où chaque poste doit fonctionner pour que le produit sorte au bout : elle reçoit la liste des disponibilités de composants placés les uns derrière les autres et renvoie leur produit, calculé par `math.prod`, puisqu'une requête ne réussit que si tous les maillons répondent à la fois. Elle ne fait aucun contrôle et renvoie un nombre qui ne dépasse jamais celui du maillon le plus faible : trois composants à 0,99 donnent 0,970299, et `main` l'emploie aussi pour placer deux répliques en parallèle devant une base à 0,999, montage mixte qui donne 0,9965025.

**`disponibilite_parallele(dispos)`** — Celle-ci raisonne comme un capitaine qui embarque plusieurs canots de secours : il suffit qu'un seul tienne la mer pour sauver l'équipage. Elle reçoit donc la liste des disponibilités de répliques indépendantes, multiplie leurs indisponibilités 1 − Aᵢ avec `math.prod` pour obtenir la probabilité que toutes tombent en même temps, et renvoie le complément à 1 de ce produit. Deux répliques à 0,95 laissent une indisponibilité commune de 0,0025 et donnent 0,9975, trois répliques donnent 0,999875 ; `main` vérifie aussi, sur l'exemple non symétrique 0,6 et 0,3, que le résultat ne descend jamais sous la meilleure des répliques.

**`budget_erreur_minutes(slo, jours)`** — Cette fonction est le comptable qui, au premier jour du mois, ouvre l'enveloppe des pannes permises : elle reçoit l'objectif de disponibilité, le SLO, et la longueur de la période en jours, convertit cette période en minutes en la multipliant par 24 puis par 60, et renvoie la part (1 − SLO) de ce total, c'est-à-dire la durée d'arrêt que l'on peut se permettre sans manquer à l'engagement. Pour un SLO de 0,999 sur 30 jours, elle renvoie 43,2 minutes, exactement la durée cumulée des trois pannes de 14,4 minutes du journal de la section 3.

**`taux_de_consommation(taux_echec_observe, slo)`** — Celle-ci est l'aiguille du compteur de vitesse posé sur ce budget : elle reçoit le taux d'échec réellement observé et le SLO, divise le premier par la part d'échecs autorisée 1 − SLO, et renvoie un rapport sans unité, qui vaut 1 quand on dépense le budget exactement au rythme prévu et davantage quand on le brûle trop vite. Avec 0,5 % d'échecs observés pour un SLO de 99,9 %, elle renvoie 5, et `main` en déduit que le budget de 30 jours sera épuisé en 30 ÷ 5 = 6 jours, l'alerte qu'une équipe d'astreinte veut recevoir bien avant la fin du mois.

**`p_timeout_mm1(mu, rho, t_max)`** — Cette fonction imagine le serveur comme un guichet unique devant lequel les requêtes font la queue dans leur ordre d'arrivée, une file M/M/1 : elle reçoit le débit de service μ, le taux d'occupation ρ et le délai maximal t_max, lève `ValueError` si ρ sort de l'intervalle [0 ; 1[, car au-delà la file grandit sans limite, puis renvoie exp(−μ(1 − ρ)t_max), la probabilité qu'une requête passe plus de t_max secondes dans le système. Avec μ = 10 requêtes par seconde et un timeout de 2 secondes, elle donne 0,1353 à ρ = 0,9, soit e⁻², alors que le serveur n'est jamais en panne : c'est la charge seule qui fait échouer ces requêtes, et `simuler_mm1` confirme ce chiffre sans l'admettre.

**`main()`** — C'est le chef d'orchestre qui fait jouer les six sections du programme, chacune suivie de ses `assert` : il oppose d'abord la formule corrigée à l'ancienne (0,90 contre 0,81, puis 0,50 contre 0,25), vérifie le `None` sans trafic et le refus de deux entrées incohérentes, puis classe avec `classer` un journal de 12 issues pour obtenir 10 succès, 1 timeout, 1 échec serveur et A = 0,8333. Il tire ensuite du journal de trois pannes un MTBF de 14 385,6 minutes et A = 0,999, compose série, parallèle et montage mixte, calcule le budget de 43,2 minutes et la vitesse 5, enfin confronte la probabilité théorique de timeout e⁻² à la simulation de 200 000 requêtes, 0,1368, qui doit tomber à moins de 0,01 de la théorie ; la ligne finale « OK » n'apparaît que si tout concorde.

```python
"""Étape 49 — disponibilité d'un serveur MCP : par requêtes, dans le temps, en série, en parallèle, sous charge."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def disponibilite_requetes(succes: int, timeouts: int, total: int) -> float | None:
    """A = succès / total. None si total = 0 : sans trafic, on ne sait rien (ce n'est pas une panne)."""
    if min(succes, timeouts, total) < 0 or succes + timeouts > total:
        raise ValueError("il faut succes >= 0, timeouts >= 0 et succes + timeouts <= total")
    if total == 0:
        return None
    return succes / total


def disponibilite_ancienne(succes: int, total: int, taux_timeout: float) -> float:
    """Ancienne formule du fichier, FAUSSE : les timeouts sont comptés deux fois."""
    return (succes / total) * (1 - taux_timeout)


def classer(issue: dict) -> str:
    """Ce qui compte comme succès pour la DISPONIBILITÉ du serveur (et non pour la réussite de la tâche)."""
    if issue.get("timeout"):
        return "timeout"
    if "error" in issue:
        return "echec" if issue["error"] in (-32603,) else "succes"          # -32602 : faute du client
    if issue.get("isError"):
        return "echec" if issue.get("cause") == "technique" else "succes"    # « compte inconnu » : le serveur a répondu
    return "succes"


def disponibilite_temporelle(mtbf: float, mttr: float) -> float:
    """A = MTBF / (MTBF + MTTR) ; MTBF = durée moyenne de bon fonctionnement entre deux pannes."""
    if mtbf <= 0 or mttr < 0:
        raise ValueError("il faut mtbf > 0 et mttr >= 0")
    return mtbf / (mtbf + mttr)


def depuis_journal(duree_totale: float, pannes: list[tuple[float, float]]) -> tuple[float, float, float]:
    """À partir des pannes (début, fin) d'une période : (disponibilité mesurée, MTBF, MTTR)."""
    arrets = [fin - debut for debut, fin in pannes]
    if not pannes or any(a <= 0 for a in arrets):
        raise ValueError("au moins une panne, de durée > 0")
    bon_fonctionnement = duree_totale - sum(arrets)
    return bon_fonctionnement / duree_totale, bon_fonctionnement / len(pannes), sum(arrets) / len(pannes)


def disponibilite_serie(dispos: list[float]) -> float:
    return math.prod(dispos)


def disponibilite_parallele(dispos: list[float]) -> float:
    return 1 - math.prod(1 - a for a in dispos)


def budget_erreur_minutes(slo: float, jours: float) -> float:
    """Durée d'arrêt autorisée sur la période : (1 − SLO) × durée."""
    return (1 - slo) * jours * 24 * 60


def taux_de_consommation(taux_echec_observe: float, slo: float) -> float:
    """1 = on consomme le budget exactement au rythme prévu ; 5 = cinq fois trop vite."""
    return taux_echec_observe / (1 - slo)


def p_timeout_mm1(mu: float, rho: float, t_max: float) -> float:
    """File M/M/1 servie dans l'ordre d'arrivée : P(séjour > t_max) = exp(−μ (1 − ρ) t_max). Admis ici (étapes 70-71)."""
    if not 0 <= rho < 1:
        raise ValueError("il faut 0 <= rho < 1 : au-delà, la file grandit sans limite")
    return math.exp(-mu * (1 - rho) * t_max)


def simuler_mm1(lam: float, mu: float, t_max: float, n: int, graine: int) -> float:
    """Récurrence de Lindley : attente(k+1) = max(0, attente(k) + service(k) − inter-arrivée). Horloge simulée."""
    rng = random.Random(graine)
    attente, depassements = 0.0, 0
    for _ in range(n):
        service = rng.expovariate(mu)
        if attente + service > t_max:
            depassements += 1
        attente = max(0.0, attente + service - rng.expovariate(lam))
    return depassements / n


def main() -> None:
    print("1. Disponibilité par requêtes : l'ancienne formule compte les timeouts deux fois")
    a = disponibilite_requetes(90, 10, 100)
    ancienne = disponibilite_ancienne(90, 100, 10 / 100)
    print(f"  90 succès, 10 timeouts sur 100 : A = {a:.2f} ; ancienne formule = {ancienne:.2f}")
    assert a == 0.90 and round(ancienne, 2) == 0.81
    assert round(a - ancienne, 10) == round(a * 10 / 100, 10)              # l'écart vaut A × taux de timeout
    print(f"  50 succès, 50 timeouts sur 100 : A = {disponibilite_requetes(50, 50, 100):.2f} ; "
          f"ancienne = {disponibilite_ancienne(50, 100, 0.5):.2f}")
    assert disponibilite_requetes(0, 0, 0) is None
    for args in ((95, 10, 100), (-1, 0, 10)):
        try:
            disponibilite_requetes(*args)
        except ValueError:
            print(f"  {args} → ValueError")
        else:
            raise AssertionError("entrée incohérente acceptée")

    print("2. Ce qui compte comme succès pour la disponibilité")
    journal = ([{"isError": False}] * 8 + [{"isError": True, "cause": "metier"}, {"error": -32602},
                                           {"error": -32603}, {"timeout": True}])
    classes = [classer(i) for i in journal]
    succes, timeouts = classes.count("succes"), classes.count("timeout")
    a2 = disponibilite_requetes(succes, timeouts, len(journal))
    print(f"  {len(journal)} issues : {succes} succès, {timeouts} timeout, {classes.count('echec')} échec serveur → A = {a2:.4f}")
    assert (succes, timeouts, classes.count("echec")) == (10, 1, 1) and round(a2, 4) == 0.8333

    print("3. Disponibilité dans le temps : 3 pannes de 14.4 min sur 30 jours")
    duree = 30 * 24 * 60.0
    pannes = [(1000.0, 1014.4), (20000.0, 20014.4), (35000.0, 35014.4)]
    a3, mtbf, mttr = depuis_journal(duree, pannes)
    print(f"  arrêt total = {duree * (1 - a3):.1f} min ; MTBF = {mtbf:.1f} min ; MTTR = {mttr:.1f} min ; "
          f"A = {a3:.4f} ; MTBF / (MTBF + MTTR) = {disponibilite_temporelle(mtbf, mttr):.4f}")
    assert round(a3, 10) == 0.999 and abs(disponibilite_temporelle(mtbf, mttr) - a3) < 1e-12
    assert round(disponibilite_temporelle(mtbf, mttr / 2), 6) == 0.9995

    print("4. Composer : série, parallèle, et les deux")
    serie = disponibilite_serie([0.99, 0.99, 0.99])
    par2 = disponibilite_parallele([0.95, 0.95])
    par3 = disponibilite_parallele([0.95, 0.95, 0.95])
    mixte = disponibilite_serie([disponibilite_parallele([0.95, 0.95]), 0.999])
    print(f"  série 3 × 0.99 = {serie:.6f} ; parallèle 2 × 0.95 = {par2:.4f} ; 3 × 0.95 = {par3:.6f}")
    print(f"  deux répliques à 0.95 devant une base à 0.999 : {mixte:.7f}")
    assert round(serie, 6) == 0.970299 and round(par2, 4) == 0.9975 and round(par3, 6) == 0.999875
    assert round(mixte, 7) == 0.9965025
    assert par2 >= max(0.95, 0.95) and disponibilite_parallele([0.6, 0.3]) >= 0.6

    print("5. Budget d'erreur d'un SLO de 99.9 %")
    budget = budget_erreur_minutes(0.999, 30)
    vitesse = taux_de_consommation(0.005, 0.999)
    print(f"  30 jours : {budget:.1f} min d'arrêt autorisées ; 1 000 000 requêtes : {round((1 - 0.999) * 1_000_000)} échecs")
    print(f"  0.5 % d'échecs observés : consommation × {vitesse:.1f}, budget épuisé en {30 / vitesse:.0f} jours")
    assert round(budget, 1) == 43.2 and round(vitesse, 6) == 5.0 and round(30 / vitesse, 6) == 6.0

    print("6. Sous charge : le serveur répond, mais trop tard (M/M/1, μ = 10 req/s, timeout 2 s)")
    for rho in (0.5, 0.9, 0.95):
        p = p_timeout_mm1(10, rho, 2.0)
        print(f"  ρ = {rho:.2f} : P(timeout) = {p:.4g} ; disponibilité par requêtes ≤ {1 - p:.5f}")
    assert abs(p_timeout_mm1(10, 0.9, 2.0) - math.exp(-2)) < 1e-12
    simule = simuler_mm1(9.0, 10.0, 2.0, 200_000, graine=49)
    print(f"  simulation ρ = 0.9, 200 000 requêtes : {simule:.4f} (théorie {math.exp(-2):.4f})")
    assert abs(simule - math.exp(-2)) < 0.01
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Disponibilité par requêtes : l'ancienne formule compte les timeouts deux fois
  90 succès, 10 timeouts sur 100 : A = 0.90 ; ancienne formule = 0.81
  50 succès, 50 timeouts sur 100 : A = 0.50 ; ancienne = 0.25
  (95, 10, 100) → ValueError
…
2. Ce qui compte comme succès pour la disponibilité
  12 issues : 10 succès, 1 timeout, 1 échec serveur → A = 0.8333
3. Disponibilité dans le temps : 3 pannes de 14.4 min sur 30 jours
  arrêt total = 43.2 min ; MTBF = 14385.6 min ; MTTR = 14.4 min ; A = 0.9990 ; MTBF / (MTBF + MTTR) = 0.9990
4. Composer : série, parallèle, et les deux
  série 3 × 0.99 = 0.970299 ; parallèle 2 × 0.95 = 0.9975 ; 3 × 0.95 = 0.999875
  deux répliques à 0.95 devant une base à 0.999 : 0.9965025
5. Budget d'erreur d'un SLO de 99.9 %
  30 jours : 43.2 min d'arrêt autorisées ; 1 000 000 requêtes : 1000 échecs
  0.5 % d'échecs observés : consommation × 5.0, budget épuisé en 6 jours
6. Sous charge : le serveur répond, mais trop tard (M/M/1, μ = 10 req/s, timeout 2 s)
  ρ = 0.90 : P(timeout) = 0.1353 ; disponibilité par requêtes ≤ 0.86466
  simulation ρ = 0.9, 200 000 requêtes : 0.1368 (théorie 0.1353)
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : la disponibilité est un rapport simple, à condition de compter chaque échec une seule fois, de savoir ce qu'est un échec du serveur, et de ne pas confondre « le serveur tourne » avec « le serveur répond à temps ».

## Squelette algorithmique

Le fichier contient quatre algorithmes : mesurer la disponibilité par requêtes sur une fenêtre d'issues, mesurer la disponibilité dans le temps à partir d'un journal de pannes, composer une architecture en série et en parallèle, et simuler une instance chargée pour estimer la part de timeouts. Les entrées sont des issues de requêtes, des intervalles de panne, des disponibilités de composants et des taux λ et μ ; les sorties sont des réels dans [0 ; 1], ou « indéfini » quand il n'y a pas eu de trafic.

### Mesurer la disponibilité par requêtes

```text
ALGORITHME DisponibiliteParRequetes
ENTRÉES : issues, liste des issues des requêtes de la fenêtre
SORTIE  : A dans [0 ; 1], ou INDÉFINI
  N ← longueur(issues)
  SI N = 0 ALORS
    RETOURNER INDÉFINI                      ▷ pas de trafic : on ne sait rien
  FIN SI
  ok ← 0 ; to ← 0
  POUR chaque issue e DANS issues FAIRE
    SI e est un timeout ALORS
      to ← to + 1
    SINON SI e est une erreur −32603 OU un isError de cause technique ALORS
      rien                                  ▷ échec du serveur
    SINON
      ok ← ok + 1                           ▷ réponse correcte, y compris −32602 et isError métier
    FIN SI
  FIN POUR
  SI ok + to > N ALORS ERREUR "compteurs incohérents" FIN SI
  RETOURNER ok / N                          ▷ jamais multiplié par (1 − to / N)
```

**Complexité :** O(N) en temps, parce que chaque issue est examinée une fois et que chaque test est en temps constant ; O(1) en mémoire supplémentaire, parce que seuls deux compteurs sont conservés (le programme garde la liste des classes pour l'affichage, ce qui coûte O(N) mais n'est pas nécessaire au calcul).

**Du squelette au code :** la boucle de classement correspond à la liste `classes = [classer(i) for i in journal]` et à la fonction `classer`, les deux compteurs à `classes.count("succes")` et `classes.count("timeout")`, les deux gardes et la division à `disponibilite_requetes`.

### Mesurer la disponibilité dans le temps

```text
ALGORITHME DisponibiliteTemporelle
ENTRÉES : D, durée de la période ; pannes, liste de K intervalles (début, fin)
SORTIE  : (A, MTBF, MTTR)
  SI K = 0 ALORS ERREUR "au moins une panne pour définir MTBF et MTTR" FIN SI
  arrêt ← 0
  POUR chaque (début, fin) DANS pannes FAIRE
    SI fin ≤ début ALORS ERREUR "panne de durée nulle" FIN SI
    arrêt ← arrêt + (fin − début)
  FIN POUR
  U ← D − arrêt                             ▷ temps de bon fonctionnement
  MTBF ← U / K ; MTTR ← arrêt / K
  RETOURNER (U / D, MTBF, MTTR)             ▷ et U / D = MTBF / (MTBF + MTTR) exactement
```

**Complexité :** O(K) en temps, une addition par panne ; O(1) en mémoire en plus de la liste lue (le programme construit la liste `arrets`, en O(K)).

**Du squelette au code :** la boucle et les tests correspondent à `arrets = [fin - debut for debut, fin in pannes]` et à la garde `any(a <= 0 for a in arrets)` de `depuis_journal` ; le retour, au triplet `(bon_fonctionnement / duree_totale, bon_fonctionnement / len(pannes), sum(arrets) / len(pannes))` ; l'identité finale, à l'`assert` qui compare avec `disponibilite_temporelle(mtbf, mttr)`.

### Composer une architecture

```text
ALGORITHME DisponibiliteMontage
ENTRÉES : un montage, qui est soit un composant de disponibilité a,
          soit SÉRIE(m₁, …, m_k), soit PARALLÈLE(m₁, …, m_k)
SORTIE  : la disponibilité du montage
  SI le montage est un composant ALORS
    RETOURNER a
  SINON SI le montage est SÉRIE(m₁, …, m_k) ALORS
    p ← 1
    POUR i DE 1 À k FAIRE p ← p × DisponibiliteMontage(mᵢ) FIN POUR
    RETOURNER p                             ▷ Π Aᵢ
  SINON                                     ▷ PARALLÈLE
    q ← 1
    POUR i DE 1 À k FAIRE q ← q × (1 − DisponibiliteMontage(mᵢ)) FIN POUR
    RETOURNER 1 − q                         ▷ 1 − Π (1 − Aᵢ)
  FIN SI
```

**Complexité :** O(c) en temps, où c est le nombre total de composants et de blocs du montage, parce que chaque nœud est visité une fois et coûte une multiplication ; O(h) en mémoire, où h est la profondeur d'imbrication, pour la pile des appels.

**Du squelette au code :** les deux branches correspondent à `disponibilite_serie` (`math.prod`) et `disponibilite_parallele` (`1 - math.prod(1 - a ...)`) ; l'imbrication, au calcul `disponibilite_serie([disponibilite_parallele([0.95, 0.95]), 0.999])` de la section 4 de `main()`.

### Estimer la part de timeouts d'une instance chargée

```text
ALGORITHME TimeoutsSousCharge
ENTRÉES : λ, μ (λ < μ), t_max, n requêtes, graine
SORTIE  : fraction des requêtes dont le séjour dépasse t_max
  initialiser le générateur avec la graine
  attente ← 0 ; dépassements ← 0
  POUR k DE 1 À n FAIRE
    service ← tirage exponentiel de moyenne 1/μ
    SI attente + service > t_max ALORS dépassements ← dépassements + 1 FIN SI
    écart ← tirage exponentiel de moyenne 1/λ        ▷ temps jusqu'à la requête suivante
    attente ← max(0, attente + service − écart)        ▷ récurrence de Lindley
  FIN POUR
  RETOURNER dépassements / n                           ▷ ≈ exp(−μ (1 − ρ) t_max)
```

**Complexité :** O(n) en temps, deux tirages et quelques opérations par requête ; O(1) en mémoire, parce que la récurrence n'a besoin que de l'attente de la requête précédente, et non de l'historique de la file.

**Du squelette au code :** l'algorithme correspond ligne pour ligne à `simuler_mm1` ; la valeur théorique, à `p_timeout_mm1` ; la comparaison des deux, à l'`assert abs(simule - math.exp(-2)) < 0.01` de la section 6.

## Cas d'usage réels aux Émirats

Les volumes, durées de panne, objectifs et charges ci-dessous sont illustratifs ; on les fixe sur l'historique réel de chaque service.

### Banque — un objectif de 99,9 % et un budget de 1 000 échecs

Une banque de détail de Dubaï expose son serveur `banque-paiements` à l'assistant client, qui envoie environ un million de requêtes MCP par mois. L'équipe fixe un objectif de 99,9 % par requêtes : le budget est de 1 000 échecs par mois, ou 43,2 minutes d'arrêt complet. Un échec, c'est un timeout, une erreur −32603 ou un `isError` dû à l'indisponibilité du cœur bancaire ; un « compte inconnu » ou un −32602 causé par l'agent ne compte pas contre le serveur, mais contre l'agent, dans une autre métrique. La nuit, certaines fenêtres de cinq minutes ne voient passer aucune requête : la mesure renvoie `None`, et l'alerte ne se déclenche pas, alors que l'ancien code aurait signalé une disponibilité de 0. Un mardi, le taux d'échec monte à 0,5 % pendant une heure : la vitesse de consommation vaut 5, l'équipe gèle le déploiement prévu et ouvre un incident. On suit la disponibilité glissante sur 30 jours et la vitesse de consommation sur une heure.

### Immobilier — deux répliques bon marché, une base partagée

Une agence et un promoteur de Dubaï et d'Abu Dhabi font tourner le serveur `immo-transactions` sur des instances peu coûteuses, chacune disponible à 95 %. Deux répliques derrière un répartiteur donnent 1 − 0,05² = 0,9975, trois donnent 0,999875. Mais les répliques lisent toutes la même base des comparables DLD, disponible à 99,9 % : le montage réel vaut 0,9975 × 0,999 = 0,9965, et une troisième réplique n'apporterait presque rien tant que la base reste un point unique. L'équipe décide donc de doubler d'abord la base, puis de garder deux répliques. Sans ce calcul, elle aurait payé une troisième instance pour un gain invisible. On suit la disponibilité de bout en bout, mesurée par le client, et non celle de chaque réplique.

### Crypto — en marche, mais pas à l'heure

Une plateforme d'actifs virtuels agréée par la VARA mesure son serveur `crypto-surveillance` de deux façons. La sonde `ping` répond 100 % du temps. Pourtant, pendant un pic de volatilité, la charge d'une instance passe de 0,5 à 0,9 : avec un service moyen de 0,1 s et un timeout client de 2 s, la part des `tools/call` qui expirent passe de 0,005 % à 13,5 % (démonstration, point 7), et les alertes de liquidité arrivent en retard ou pas du tout. La décision est d'ajouter des instances quand la charge mesurée dépasse 0,7, et non quand le `ping` échoue, et de réserver une instance aux outils critiques. La plateforme doit pouvoir montrer au régulateur que ses alertes reposaient sur des données à jour : la disponibilité par requêtes est archivée avec chaque alerte. On suit la charge par instance et la part de timeouts par minute.

### Assurance — réparer plus vite plutôt que tomber moins souvent

Un assureur auto et santé a placé son système de sinistres hérité derrière un adaptateur MCP (étape 47). Le journal du mois montre trois pannes de 14,4 minutes : MTBF = 14 385,6 minutes, MTTR = 14,4 minutes, disponibilité 0,999. L'objectif est de 99,95 %. Allonger le temps entre les pannes demanderait de modifier le système hérité, ce qui n'est pas possible à court terme ; diviser le temps de réparation par deux, grâce à un redémarrage automatique de l'adaptateur et à une procédure écrite, donne 0,9995 sans toucher au système (démonstration, point 3). Supervisé par la CBUAE, l'assureur conserve le journal des pannes et des réparations avec leur durée. On suit le MTTR mois par mois, à côté de la disponibilité.

### RH — la fin de mois consomme le budget

Un cabinet RH multi-émirats suit le serveur `rh-paie` sur un objectif de 99,5 % par mois. Les trois derniers jours du mois, pendant la préparation des fichiers WPS, le taux d'échec atteint 2 %, à cause des lectures de contrat sur le système de paie ancien : la vitesse de consommation vaut 0,02 / 0,005 = 4, et le budget mensuel serait épuisé en une semaine à ce rythme. L'équipe met en cache les lectures de contrat, qui changent rarement, et fait passer le taux d'échec sous 0,5 %. Sans budget d'erreur, la moyenne mensuelle aurait masqué ces trois jours, qui sont précisément ceux où un échec retarde le paiement des salaires. On suit la vitesse de consommation par jour, avec une alerte au-delà de 2.

### Secteur public — ne pas faire payer au serveur les erreurs de l'agent

Une entité de services publics en ligne, accessible par UAE Pass, mesure la disponibilité de son serveur `services-publics` sur 100 000 requêtes par jour. Après une mise à jour du prompt de l'assistant, le nombre de réponses −32602 triple : l'agent remplit mal un champ de date. Si ces réponses comptaient comme des échecs, la disponibilité du serveur tomberait sous son objectif et l'équipe d'infrastructure chercherait une panne qui n'existe pas. La règle de `classer` les compte comme des succès pour la disponibilité, et une métrique séparée, la part de −32602 par version du prompt, signale le vrai problème à l'équipe de l'agent. On suit donc deux indicateurs distincts : la disponibilité du serveur et le taux d'appels invalides de l'agent.

## Pièges et limites

- **Compter deux fois les timeouts.** Multiplier le taux de succès par (1 − taux de timeout) pénalise chaque timeout deux fois : 0,81 au lieu de 0,90 dans l'exemple. Les timeouts sont déjà des non-succès.
- **Renvoyer 0 quand il n'y a pas de trafic.** Pas de requête n'est pas une panne. On renvoie `None` et l'on exclut la fenêtre des moyennes.
- **Mesurer la disponibilité avec un `ping`.** Un `ping` vérifie que le processus vit ; il ne dit rien du temps de réponse d'un `tools/call` sous charge (démonstration, point 7). On mesure côté client, sur les vrais appels.
- **Supposer les répliques indépendantes.** Une base, un réseau ou un déploiement communs les font tomber ensemble. On place les composants communs en série avec le bloc parallèle.
- **Conclure sur un petit échantillon.** 45 succès sur 50 donnent 0,90, mais l'intervalle de Wilson à 95 % va de 0,786 à 0,957 (étape 7) : on ne compare pas un objectif de 99,9 % à quelques dizaines de requêtes.

### Exercice feuille blanche

1. Sans regarder le code, écrire `disponibilite_requetes(succes, timeouts, total)` avec ses deux gardes, puis vérifier `(90, 10, 100)`, `(0, 0, 0)` et `(95, 10, 100)`.
2. Prédire, puis vérifier : trois répliques à 0,90 derrière un répartiteur, puis une base commune à 0,995. (Réponse : 1 − 0,1³ = 0,999, puis 0,999 × 0,995 = 0,994005.)
3. Trouver le bug : une variante écrit `if total == 0: return 0.0`. Que devient la disponibilité moyenne de 24 fenêtres d'une heure, dont 6 sans trafic et 18 à 1,0 ? (Réponse : 18 / 24 = 0,75 au lieu de 1,0.)
4. Calculer le budget d'arrêt d'un objectif de 99,95 % sur 30 jours, puis la vitesse de consommation à 0,2 % d'échecs. (Réponse : 0,0005 × 43 200 = 21,6 minutes ; 0,002 / 0,0005 = 4.)

## Pour aller plus loin

Plusieurs instances derrière une même file relèvent de la formule d'Erlang C (étape 71), qui donne la probabilité d'attendre et la part de requêtes au-delà d'un délai ; c'est elle qui dimensionne le nombre de répliques d'un serveur MCP chargé. Les alertes de production combinent souvent deux fenêtres de vitesse de consommation, une courte pour réagir vite et une longue pour éviter les fausses alertes. Enfin, la disponibilité d'un agent entier combine celle de ses serveurs, du modèle et de la boucle : c'est la fiabilité composée de l'étape 1, avec des facteurs mesurés ici.

> Suite : [A2A et édition par diff](<49b-A2A-et-Edition-par-Diff.md>) — étape 49 bis.
