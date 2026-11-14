# Étape 17 — Mémoire — Score de pertinence mémoire

> Étape 17 du parcours · Prérequis : [Décroissance temporelle d'un souvenir](<16-Memoire-Formule-Decroissance-Temporelle.md>) · Suite : [Formules et algorithmes du RAG](<../05-RAG/18-RAG-Formules-Theoremes-Algorithmes.md>)

**Dossier :** 04-Contexte-Similarite-et-Memoire  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  
**Nom du fichier :** 17-Memoire-Formule-Score-de-Pertinence.md

## Définition

Le score de pertinence décide quels souvenirs un agent rappelle à un instant donné, et dans quel ordre. Il combine trois signaux mesurés sur chaque souvenir candidat : sa **similarité** avec la question courante (le cosinus de l'étape 14), sa **récence** (la décroissance exponentielle de l'étape 16) et son **importance** (une note fixée quand le souvenir est écrit). Chaque signal est d'abord ramené dans l'intervalle [0, 1] sur l'ensemble des candidats, puis les trois sont additionnés avec des poids positifs de somme 1. Le résultat est un nombre entre 0 et 1 ; l'agent garde les k souvenirs de plus grand score et les place dans son prompt. Ce score a été popularisé par l'article « Generative Agents » (Park et al., 2023).

## Rôle dans un agent

À chaque tour, l'agent *perçoit* une question et doit *décider* quels souvenirs placer dans son contexte avant d'*agir*. Le composant **mémoire** commence par une présélection rapide, par exemple les 50 souvenirs les plus similaires renvoyés par la base vectorielle, puis calcule sur ces candidats le score de pertinence et n'en garde que k, souvent entre 3 et 10. Sans ce score, l'agent choisirait sur la seule similarité et rappellerait un vieux critère abandonné aussi volontiers qu'une préférence exprimée la veille ; ou bien, sur la seule récence, il oublierait une contrainte critique parce qu'elle est ancienne. Le score sert aussi après la réponse, au moment d'*observer* : les souvenirs injectés voient leur date de dernier accès remise à jour (étape 16, point 6), et ceux dont le score reste durablement bas deviennent candidats au résumé ou à l'archivage.

## Équation complète

Le score du souvenir j, parmi les candidats :

$$
\text{score}_j = w_{sim}\,\widetilde{sim}_j + w_{rec}\,\widetilde{rec}_j + w_{imp}\,\widetilde{imp}_j
$$

Les poids :

$$
w_{sim} \ge 0, \quad w_{rec} \ge 0, \quad w_{imp} \ge 0, \qquad w_{sim} + w_{rec} + w_{imp} = 1
$$

Chaque composante x (similarité, récence, importance) est ramenée dans [0, 1] par min-max sur les candidats :

$$
\widetilde{x}_j = \frac{x_j - \min_i x_i}{\max_i x_i - \min_i x_i}
$$

avec la convention x̃ⱼ = 0 pour tous les j quand toutes les valeurs sont égales. Les composantes brutes sont la similarité cosinus de l'étape 14 :

$$
sim_j = \cos(q, v_j)
$$

et la récence de l'étape 16, mesurée depuis le dernier accès :

$$
rec_j = e^{-\lambda\,\Delta t_j} = 2^{-\Delta t_j / t_{1/2}} \qquad \text{avec} \qquad \lambda = \frac{\ln 2}{t_{1/2}}
$$

L'importance impⱼ est une note de 1 à 10. L'agent injecte les k souvenirs de plus grand score.

## Décryptage des symboles

$$
j
$$

**Sens :** indice d'un souvenir candidat · **Type / plage :** entier · **Variable Python :** position dans `souvenirs`

$$
q
$$

**Sens :** vecteur de la question courante · **Type / plage :** liste de réels · **Variable Python :** `question`

$$
v_j
$$

**Sens :** vecteur (embedding) du souvenir j · **Type / plage :** liste de réels · **Variable Python :** `Souvenir.vecteur`

$$
sim_j
$$

**Sens :** similarité cosinus entre q et vⱼ (étape 14) · **Type / plage :** réel dans [−1, 1] · **Variable Python :** `cosinus(question, s.vecteur)`

$$
\Delta t_j
$$

**Sens :** âge du souvenir : temps écoulé depuis son dernier accès · **Type / plage :** jours ≥ 0 · **Variable Python :** `maintenant - s.dernier_acces`

$$
t_{1/2},\quad \lambda
$$

**Sens :** demi-vie et taux de décroissance, reliés par (formule ci-dessous) (étape 16) · **Type / plage :** jours > 0 ; jours⁻¹ · **Variable Python :** `demi_vie`, `lam`

$$
\lambda = \ln 2 / t_{1/2}
$$

$$
rec_j
$$

**Sens :** récence (formule ci-dessous) · **Type / plage :** réel dans ]0 ; 1] · **Variable Python :** `recence(age, demi_vie)`

$$
e^{-\lambda \Delta t_j}
$$

$$
imp_j
$$

**Sens :** importance, de 1 (banal) à 10 (crucial), notée à l'écriture du souvenir · **Type / plage :** entier de 1 à 10 · **Variable Python :** `Souvenir.importance`

$$
\widetilde{x}_j
$$

**Sens :** composante x ramenée dans [0, 1] par min-max sur les candidats · **Type / plage :** réel dans [0, 1] · **Variable Python :** `min_max(valeurs)[j]`

$$
w_{sim},\quad w_{rec},\quad w_{imp}
$$

**Sens :** poids des trois composantes · **Type / plage :** réels ≥ 0, de somme 1 · **Variable Python :** `poids = (0.5, 0.3, 0.2)`

$$
\text{score}_j
$$

**Sens :** score de pertinence du souvenir j · **Type / plage :** réel dans [0, 1] · **Variable Python :** `score_pertinence(sim, rec, imp, poids)`

$$
k
$$

**Sens :** nombre de souvenirs injectés dans le prompt · **Type / plage :** entier ≥ 1 · **Variable Python :** `k`

L'ancienne version de ce fichier notait les poids α, β et γ. L'article d'origine, « Generative Agents » (Park et al., 2023), les écrit

$$
\alpha_{recency} ,
$$

$$
\alpha_{importance}
$$

et

$$
\alpha_{relevance} ,
$$

les fixe tous à 1, et normalise chaque composante par min-max avant de les additionner. On écrit ici wₛᵢₘ,

$$
w_{rec}
$$

et wᵢₘₚ, parce que dans ce parcours γ désigne le facteur d'actualisation (étape 38) et α le poids du score hybride (étape 23) : un même symbole ne doit pas avoir deux sens.

## Démonstration

### 1. Le défaut : l'influence d'une composante dépend de son étendue, pas seulement de son poids

L'écart de score entre deux souvenirs A et B se décompose composante par composante, parce que la somme pondérée est linéaire :

$$
\text{score}_A - \text{score}_B = w_{sim}\,(sim_A - sim_B) + w_{rec}\,(rec_A - rec_B) + w_{imp}\,(imp_A - imp_B)
$$

Chaque terme est borné, en valeur absolue, par le poids multiplié par l'étendue de la composante sur les candidats, c'est-à-dire l'écart entre sa plus grande et sa plus petite valeur. Si la similarité et la récence restent dans [0, 1] mais que l'importance va de 1 à 10, le terme d'importance peut peser jusqu'à 0,2 × 9 = 1,8, alors que la similarité, pourtant de poids 0,5, ne pèse jamais plus de 0,5 × 1 = 0,5 : le plus petit poids devient la plus grande influence.

Contre-exemple chiffré, avec les poids (0,5 ; 0,3 ; 0,2) et l'importance laissée sur l'échelle 1-10 :

| Souvenir | sim | rec | imp | Score brut |
|---|---|---|---|---|
| A, hors sujet et ancien | 0,2 | 0,1 | 9 | 0,1 + 0,03 + 1,8 = 1,93 |
| B, pertinent et récent | 0,9 | 0,9 | 2 | 0,45 + 0,27 + 0,4 = 1,12 |

A gagne, alors qu'il est moins similaire et moins récent. La décomposition dit pourquoi :

$$
\text{score}_A - \text{score}_B = 0{,}5 \times (-0{,}7) + 0{,}3 \times (-0{,}8) + 0{,}2 \times 7 = -0{,}35 - 0{,}24 + 1{,}40 = 0{,}81 .
$$

Le seul terme d'importance (+1,40) l'emporte sur la similarité et la récence réunies (−0,59). Ramener l'importance dans [0, 1], ici en la divisant par 10, rétablit l'ordre : A vaut 0,1 + 0,03 + 0,18 = 0,31 et B vaut 0,45 + 0,27 + 0,04 = 0,76.

### 2. La normalisation min-max : bornes, ordre, indépendance de l'unité

Sur les N candidats, on note lo = minᵢ xᵢ et hi = maxᵢ xᵢ, et l'on suppose hi > lo.

**Bornes.** Parce que lo ≤ xⱼ ≤ hi, on a 0 ≤ xⱼ − lo ≤ hi − lo ; en divisant par hi − lo > 0, ce qui ne change pas le sens des inégalités, on obtient 0 ≤ x̃ⱼ ≤ 1. Le plus petit candidat reçoit 0, le plus grand reçoit 1.

**Ordre conservé.** L'application x ↦ (x − lo)/(hi − lo) est affine de pente 1/(hi − lo) > 0, donc strictement croissante : si

$$
x_A > x_B ,
$$

alors

$$
\widetilde{x}_A > \widetilde{x}_B .
$$

La normalisation ne change le classement d'aucune composante prise seule.

**Indépendance de l'unité.** Si l'on remplace chaque xᵢ par yᵢ = a xᵢ + b avec a > 0 (une note sur 100 au lieu de 10, des heures au lieu de jours), alors minᵢ yᵢ = a lo + b et maxᵢ yᵢ = a hi + b, d'où :

$$
\widetilde{y}_j = \frac{(a x_j + b) - (a\,lo + b)}{(a\,hi + b) - (a\,lo + b)} = \frac{a\,(x_j - lo)}{a\,(hi - lo)} = \widetilde{x}_j
$$

Le résultat ne dépend ni de a ni de b : la composante normalisée ne dépend pas de l'unité choisie. C'est ce qui permet de mélanger une note sur 10, un cosinus et une exponentielle.

**Cas dégénéré.** Si toutes les valeurs sont égales (hi = lo), la formule diviserait par zéro. Une composante constante ne départage aucun candidat ; la fonction canonique `min_max` renvoie alors 0 partout, ce qui la retire du classement sans le fausser.

Exemple : les importances (8, 9, 9, 6, 3) ont lo = 3 et hi = 9, donc

$$
\widetilde{imp} = (5/6 ;\ 1 ;\ 1 ;\ 1/2 ;\ 0) = (0{,}8333 ;\ 1 ;\ 1 ;\ 0{,}5 ;\ 0) .
$$

Les mêmes notes exprimées sur 100, (80, 90, 90, 60, 30), donnent exactement la même liste.

### 3. Poids positifs de somme 1 : le score reste dans [0, 1]

Si

$$
w_c \ge 0
$$

pour chaque composante c, si

$$
\sum_c w_c = 1
$$

et si chaque

$$
\widetilde{x}_c
$$

est dans [0, 1], alors :

$$
0 = \sum_c w_c \times 0 \;\le\; \sum_c w_c\,\widetilde{x}_c \;\le\; \sum_c w_c \times 1 = 1
$$

Les deux inégalités tiennent terme à terme, parce que multiplier

$$
0 \le \widetilde{x}_c \le 1
$$

par un nombre

$$
w_c \ge 0
$$

donne

$$
0 \le w_c \widetilde{x}_c \le w_c .
$$

On dit que le score est une **combinaison convexe** des composantes : c'est leur moyenne pondérée, donc il est toujours compris entre la plus petite et la plus grande d'entre elles. Il vaut 1 si et seulement si toutes les composantes de poids non nul valent 1, et 0 si et seulement si elles valent toutes 0. Les deux hypothèses sont nécessaires : avec des poids (0,5 ; 0,5 ; 0,5), de somme 1,5, le souvenir parfait (1, 1, 1) vaut 1,5 ; avec (0,6 ; 0,6 ; −0,2), de somme 1 mais avec un poids négatif, le souvenir (0, 0, 1) vaut −0,2. La fonction `score_pertinence` refuse donc ces entrées par `ValueError`.

### 4. Multiplier tous les poids par un même nombre positif ne change pas le classement

Si l'on remplace chaque

$$
w_c
$$

par

$$
m\,w_c
$$

avec m > 0, chaque score est multiplié par m, et

$$
m\,\text{score}_A > m\,\text{score}_B
$$

équivaut à

$$
\text{score}_A > \text{score}_B ,
$$

parce que multiplier par un nombre positif conserve le sens des inégalités. Les poids de Park et al., tous égaux à 1 (score entre 0 et 3), classent donc exactement comme (1/3 ; 1/3 ; 1/3). Ramener la somme des poids à 1 ne change pas l'ordre : cela rend le score lisible, entre 0 et 1, et permet de lui appliquer un seuil.

### 5. Composition avec les étapes 14 et 16

La similarité est le cosinus de l'étape 14 : simⱼ = cos(q, vⱼ), dans [−1, 1] par Cauchy-Schwarz. La récence est la décroissance de l'étape 16 mesurée depuis le dernier accès, avec

$$
\lambda = \ln 2 / t_{1/2}
$$

$$
e^{-\lambda \Delta t} = e^{-\frac{\ln 2}{t_{1/2}} \Delta t} = \left(e^{\ln 2}\right)^{-\Delta t / t_{1/2}} = 2^{-\Delta t / t_{1/2}}
$$

La deuxième égalité vient de eᵃᵇ = (eᵃ)ᵇ, la troisième de eˡⁿ² = 2. Avec

$$
t_{1/2} = 30
$$

jours, des âges de 0, 15, 30, 60 et 90 jours donnent une récence de 1 ;

$$
2^{-1/2} = 0{,}7071 ;
$$

0,5 ; 0,25 et 0,125. Ces deux composantes sont déjà bornées, mais on les normalise quand même : sur les candidats, leur étendue réelle (ici 0,8 pour le cosinus et 0,875 pour la récence) diffère de celle de l'importance brute (6), et le min-max ramène les trois à une étendue de 1, si bien que les poids redeviennent les vraies influences.

### 6. Exemple fait à la main (le code reprend ces nombres)

Un acheteur immobilier demande, au jour 90 : « une villa avec jardin, près d'une bonne école ? ». Dans un espace jouet à cinq axes (villa et jardin, appartement et Marina, budget, famille et école, contact), sa question vaut q = (0,8 ; 0 ; 0 ; 0,6 ; 0). La question et les souvenirs sont de norme 1, donc chaque cosinus est un simple produit scalaire. Les poids valent (0,5 ; 0,3 ; 0,2) et la demi-vie 30 jours.

| Souvenir | vⱼ | sim | Δ t | rec | imp | s̃ĩm̃ | r̃ẽc̃ | ĩm̃p̃ | score |
|---|---|---|---|---|---|---|---|---|---|
| Cherche une villa avec jardin | (1 ; 0 ; 0 ; 0 ; 0) | 0,8 | 0 | 1 | 8 | 1 | 1 | 0,8333 | 0,9667 |
| Budget maximum 3,5 M AED | (0,6 ; 0 ; 0,8 ; 0 ; 0) | 0,48 | 15 | 0,7071 | 9 | 0,6 | 0,6653 | 1 | 0,6996 |
| Deux enfants scolarisés à Mirdif | (0 ; 0 ; 0 ; 1 ; 0) | 0,6 | 30 | 0,5 | 6 | 0,75 | 0,4286 | 0,5 | 0,6036 |
| Cherchait un deux-pièces à Dubai Marina | (0,28 ; 0,96 ; 0 ; 0 ; 0) | 0,224 | 90 | 0,125 | 9 | 0,28 | 0 | 1 | 0,3400 |
| Préfère être appelé le soir | (0 ; 0 ; 0 ; 0 ; 1) | 0 | 60 | 0,25 | 3 | 0 | 0,1429 | 0 | 0,0429 |

Le détail d'une ligne : pour le budget, s̃ĩm̃ = 0,48 / 0,8 = 0,6 (le plus petit cosinus vaut 0),

$$
\widetilde{rec} = (0{,}7071 - 0{,}125) / 0{,}875 = 0{,}6653 ,
$$

ĩm̃p̃ = (9 − 3)/6 = 1, et le score vaut

$$
0{,}5 \times 0{,}6 + 0{,}3 \times 0{,}6653 + 0{,}2 \times 1 = 0{,}3 + 0{,}1996 + 0{,}2 = 0{,}6996 .
$$

Le top-3 garde la villa, le budget et les enfants. Sans normalisation, avec l'importance sur 1-10, les scores bruts valent 2,3 (villa) ; 2,2521 (budget) ; 1,9495 (Marina) ; 1,65 (enfants) et 0,675 (soir) : le vieux critère Marina, hors sujet, prend la place des enfants, exactement le défaut du point 1.

## Effets et comportement

- **Augmenter wₛᵢₘ** privilégie les souvenirs qui parlent du sujet de la question.
- **Augmenter**

$$
w_{rec}
$$

privilégie les souvenirs récents ou relus récemment.
- **Augmenter wᵢₘₚ** fait remonter les informations critiques même anciennes. C'est voulu pour une contrainte de conformité, dangereux si l'importance est mal notée : avec des poids (0,2 ; 0,3 ; 0,5), le critère Marina repasse devant les enfants (exercice 2).
- **Le score croît avec chaque composante normalisée** : sa dérivée par rapport à

$$
\widetilde{x}_c
$$

vaut

$$
w_c \ge 0 .
$$

Améliorer un signal ne peut jamais faire reculer un souvenir.
- **Une composante constante sur les candidats ne compte pas** : le min-max la met à 0 partout.
- **Le score est relatif au lot de candidats** : le même souvenir n'a pas le même score selon les autres candidats présents (voir les pièges).
- **La demi-vie règle la vitesse d'oubli** : avec 30 jours, un souvenir de 90 jours garde 1/8 de sa récence ; avec 90 jours, il en garderait 1/2.

## Du symbole au code Python

$$
sim_j = \cos(q, v_j)
$$

**Variable ou fonction :** `cosinus(question, s.vecteur)`

$$
rec_j = e^{-\lambda \Delta t_j}
$$

**Variable ou fonction :** `recence(maintenant - s.dernier_acces, demi_vie)`

$$
imp_j
$$

**Variable ou fonction :** `s.importance`

$$
\widetilde{x}_j
$$

**Variable ou fonction :** `min_max(valeurs)`

$$
w_{sim},\quad w_{rec},\quad w_{imp}
$$

**Variable ou fonction :** `poids = (0.5, 0.3, 0.2)`

$$
\text{score}_j
$$

**Variable ou fonction :** `score_pertinence(sim, rec, imp, poids)` ; `somme_ponderee(composantes, poids)` sans contrôle

**Symbole :** top-k · **Variable ou fonction :** `classer(question, souvenirs, maintenant, demi_vie, poids, k)`

### Déroulé, ligne par ligne

**`cosinus(a, b)`** est la fonction canonique du parcours (étape 14). Elle refuse deux listes de tailles différentes et le vecteur nul par `ValueError`, puis rabat le résultat dans [−1, 1] contre les arrondis. Pour la question `[0.8, 0.0, 0.0, 0.6, 0.0]` et le souvenir « villa » `[1.0, 0.0, 0.0, 0.0, 0.0]`, le produit scalaire vaut 0,8 et les deux normes valent 1 : le cosinus vaut 0,8.

**`min_max(valeurs)`**, c'est x̃ⱼ.

- `lo, hi = min(valeurs), max(valeurs)` : pour les importances `[8.0, 9.0, 9.0, 6.0, 3.0]`, `lo = 3.0` et `hi = 9.0`.
- `if hi == lo` : une composante constante ne départage rien. On renvoie `0.0` partout au lieu de diviser par zéro.
- `return [(v - lo) / (hi - lo) for v in valeurs]` : (8 − 3)/6 = 0,8333, puis 1, 1, 0,5 et 0.

**`recence(age, demi_vie)`**, c'est

$$
e^{-\lambda \Delta t} .
$$

- La garde refuse un âge négatif ou une demi-vie nulle.
- `lam = math.log(2) / demi_vie` : avec 30 jours, λ = 0,6931 / 30 = 0,0231 par jour.
- `return math.exp(-lam * age)` : à 15 jours, e⁻⁰,³⁴⁶⁶ = 0,7071 ; à 90 jours, 0,125.

**`somme_ponderee(composantes, poids)`** calcule `sum(w * x for w, x in zip(poids, composantes))` sans aucun contrôle. Elle sert à montrer le défaut : 1,93 contre 1,12, puis 1,5 et −0,2 avec de mauvais poids.

**`score_pertinence(sim, rec, imp, poids)`** fait la même somme, après avoir vérifié les deux hypothèses du point 3.

- `if min(poids) < 0 or abs(sum(poids) - 1.0) > 1e-9` : un poids négatif ou une somme différente de 1 casse la borne [0, 1]. La tolérance `1e-9` absorbe les arrondis, par exemple `1/3 + 1/3 + 1/3`.
- `if not all(0.0 <= x <= 1.0 for x in (sim, rec, imp))` : une composante non normalisée, comme une importance de 9, est refusée avec le message « normaliser d'abord ».

**`Souvenir`** est une `dataclass` à quatre champs : le texte, le vecteur, `dernier_acces` (en jours, sur une horloge simulée) et `importance` (de 1 à 10, notée une fois, à l'écriture).

**`classer(question, souvenirs, maintenant, demi_vie, poids, k)`** enchaîne les étapes de l'équation.

- `sims` vaut `[0.8, 0.48, 0.224, 0.6, 0.0]` dans l'ordre de la liste (villa, budget, Marina, enfants, soir).
- `recs` part des âges `maintenant - s.dernier_acces`, soit 0, 15, 90, 30 et 60 jours, et vaut `[1.0, 0.7071, 0.125, 0.5, 0.25]`.
- `imps` vaut `[8.0, 9.0, 9.0, 6.0, 3.0]`.
- Les trois appels à `min_max` donnent `[1.0, 0.6, 0.28, 0.75, 0.0]`, `[1.0, 0.6653, 0.0, 0.4286, 0.1429]` et `[0.8333, 1.0, 1.0, 0.5, 0.0]`.
- La boucle appelle `score_pertinence` pour chaque souvenir et garde aussi les composantes, pour l'affichage.
- `lignes.sort(key=lambda ligne: (-ligne[0], ligne[1].texte))` trie par score décroissant ; à score égal, l'ordre alphabétique du texte départage, ce qui rend la sortie identique d'une exécution à l'autre.
- `return lignes[:k]` garde les `k` premiers.

**`main()`**, bloc par bloc.

1. Le contre-exemple : `a_brut` vaut 1,93, `b_brut` 1,12, et `ecart` recalcule l'écart 0,81 terme à terme, dont +1,40 pour l'importance. Avec l'importance divisée par 10, `score_pertinence` accepte les entrées et rend 0,31 et 0,76 : B repasse devant.
2. `min_max` sur les importances donne `[5/6, 1.0, 1.0, 0.5, 0.0]`. Les mêmes notes multipliées par 10, puis transformées en `2.5 * x + 7`, donnent la même liste à `1e-12` près : c'est l'indépendance de l'unité. Une liste constante donne des zéros.
3. Les bornes 0 et 1 sont atteintes. `somme_ponderee` montre 1,5 et −0,2 avec de mauvais poids, et le `try / except / else` vérifie que `score_pertinence` refuse les trois entrées fautives.
4. Le tableau de l'exemple fait à la main est imprimé, puis vérifié : cosinus, récences et scores, arrondis à 3 ou 4 décimales. Le top-3 contient bien les enfants. La liste `brut`, calculée sans normalisation, vaut `[2.3, 2.2521, 1.9495, 1.65, 0.675]` et met Marina en troisième position.
5. Les mêmes composantes normalisées, pondérées par (1, 1, 1) puis par (1/3, 1/3, 1/3), donnent le même ordre.
6. Les deux pièges du min-max, décrits plus bas, sont vérifiés sur leurs nombres ; les deux derniers `assert` vérifient la réponse de l'exercice 2.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`min_max(valeurs)`** — Cette fonction se comporte comme un arbitre qui ramène des athlètes de tailles très différentes sur une même toise graduée de 0 à 1 : elle reçoit une liste de nombres bruts, repère le plus petit et le plus grand, puis remplace chaque valeur par sa position relative entre ces deux bornes, (v − min) / (max − min). Si toutes les valeurs sont égales, la toise n'a plus de sens et, plutôt que de diviser par zéro, elle renvoie une liste de zéros, car un signal constant ne départage personne ; sinon elle renvoie la liste normalisée, par exemple 0,8333, 1, 1, 0,5 et 0 pour les importances 8, 9, 9, 6 et 3. C'est elle qui met la similarité, la récence et l'importance sur la même échelle avant toute addition.

**`recence(age, demi_vie)`** — On y retrouve le sablier de l'étape 16, réglé cette fois par une demi-vie plutôt que par un taux : la fonction reçoit l'âge du souvenir et la demi-vie, refuse par `ValueError` un âge négatif ou une demi-vie nulle ou négative, convertit la demi-vie en taux λ = ln 2 / demi-vie, puis renvoie exp(−λ × âge). Le souvenir neuf vaut 1, celui qui a exactement une demi-vie vaut 0,5, et avec 30 jours de demi-vie un souvenir de 15 jours garde 0,7071 tandis qu'un souvenir de 90 jours tombe à 0,125. Elle fournit la deuxième des trois composantes du score.

**`somme_ponderee(composantes, poids)`** — C'est un caissier sans scrupules qui additionne ce qu'on lui tend sans jamais vérifier les billets : elle reçoit un triplet de composantes et un triplet de poids, multiplie chaque composante par son poids et renvoie la somme, sans aucun contrôle d'échelle ni de signe. Le programme l'utilise précisément pour exhiber le défaut d'une somme naïve : l'importance laissée sur l'échelle de 1 à 10 donne 1,93 au souvenir A contre 1,12 au souvenir B, et de mauvais poids produisent 1,5 ou −0,2, des scores qui sortent de l'intervalle [0, 1].

**`score_pertinence(sim, rec, imp, poids)`** — Voici le même caissier, devenu prudent : la fonction reçoit les trois composantes déjà normalisées et le triplet de poids, et commence par lever `ValueError` si un poids est négatif ou si leur somme s'écarte de 1 de plus de `1e-9`, puis une seconde `ValueError`, avec le conseil de normaliser d'abord, si l'une des composantes sort de [0, 1]. Une fois ces deux gardes franchies, elle délègue le calcul à `somme_ponderee` et renvoie un score qui, par construction, reste entre 0 et 1 ; avec l'importance divisée par 10, elle rend 0,31 pour A et 0,76 pour B, si bien que B repasse devant.

**`classer(question, souvenirs, maintenant, demi_vie, poids, k)`** — Cette fonction est le documentaliste qui, avant chaque réponse de l'agent, choisit quelles fiches poser sur le bureau : elle reçoit le vecteur de la question, la liste des `Souvenir`, l'instant présent, la demi-vie, les poids et le nombre k de fiches voulues. Elle calcule pour chaque souvenir le cosinus avec la question, la récence d'après son dernier accès et son importance, passe chacune des trois listes par `min_max`, appelle `score_pertinence` sur les valeurs normalisées en gardant les composantes pour l'affichage, trie par score décroissant en départageant les égalités par le texte, et renvoie les k premiers triplets (score, souvenir, composantes). Sur les cinq souvenirs de l'acheteur, au jour 90 avec une demi-vie de 30 jours, les scores valent 0,9667, 0,6996, 0,6036, 0,34 et 0,0429, et le souvenir des enfants entre dans le top 3.

**`deux_composantes(lot)`** — Cette fonction interne, définie à l'intérieur de `main`, sert de petite expérience de laboratoire pour montrer qu'un min-max dépend des candidats présents dans la salle : elle reçoit un dictionnaire qui associe à chaque nom un couple (similarité, récence), trie les noms, normalise séparément les deux composantes sur ce lot, puis renvoie un dictionnaire des scores 0,5 × similarité + 0,3 × récence arrondis à quatre décimales. Sans le candidat Z, Y obtient 0,3 ; dès que Z entre avec une récence intermédiaire, Y monte à 0,55 alors que rien n'a changé pour lui, et Z reçoit 0,15.

**`main()`** — Le chef d'orchestre joue six actes, tous avec les poids 0,5, 0,3 et 0,2 : le contre-exemple de l'importance non normalisée (1,93 contre 1,12, écart de 0,81 dont 1,40 dû à l'importance), puis les propriétés de `min_max`, bornes, indépendance de l'unité et liste constante ramenée à zéro, puis la borne [0, 1] du score et le refus des trois entrées fautives par `score_pertinence`. Viennent ensuite le classement des cinq souvenirs de l'acheteur, comparé au classement sans normalisation qui fait remonter Marina en troisième position, la preuve que multiplier tous les poids par la même constante ne change pas l'ordre, et enfin les deux pièges du min-max mesurés avec `deux_composantes`, suivis de la vérification de l'exercice 2. Chaque valeur est gardée par un `assert` et la dernière ligne n'annonce le succès que si tous ont tenu.

```python
"""Étape 17 — score de pertinence d'un souvenir : similarité, récence, importance, normalisées puis pondérées."""
import math
import sys
from dataclasses import dataclass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def cosinus(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("dimensions différentes")
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        raise ValueError("vecteur nul : le cosinus n'est pas défini")
    return max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b)) / (na * nb)))


def min_max(valeurs: list[float]) -> list[float]:
    """Ramène dans [0, 1] ; si toutes les valeurs sont égales, le signal ne départage rien : 0.0 partout."""
    lo, hi = min(valeurs), max(valeurs)
    if hi == lo:
        return [0.0 for _ in valeurs]
    return [(v - lo) / (hi - lo) for v in valeurs]


def recence(age: float, demi_vie: float) -> float:
    """rec = e^(−λ·âge) avec λ = ln 2 / demi-vie (étape 16) : 1 à l'âge 0, 1/2 à la demi-vie."""
    if age < 0 or demi_vie <= 0:
        raise ValueError("il faut age >= 0 et demi_vie > 0")
    lam = math.log(2) / demi_vie
    return math.exp(-lam * age)


def somme_ponderee(composantes: tuple[float, float, float], poids: tuple[float, float, float]) -> float:
    """w_sim·sim + w_rec·rec + w_imp·imp, sans aucun contrôle (sert à montrer le défaut)."""
    return sum(w * x for w, x in zip(poids, composantes))


def score_pertinence(sim: float, rec: float, imp: float, poids: tuple[float, float, float]) -> float:
    """Même somme, mais refuse ce qui casse la borne [0, 1] : poids négatifs, somme ≠ 1, composante hors [0, 1]."""
    if min(poids) < 0 or abs(sum(poids) - 1.0) > 1e-9:
        raise ValueError("les poids doivent être >= 0 et de somme 1")
    if not all(0.0 <= x <= 1.0 for x in (sim, rec, imp)):
        raise ValueError("chaque composante doit être dans [0, 1] : normaliser d'abord")
    return somme_ponderee((sim, rec, imp), poids)


@dataclass
class Souvenir:
    texte: str
    vecteur: list[float]
    dernier_acces: float   # en jours, sur une horloge simulée
    importance: int        # de 1 (banal) à 10 (crucial), notée à l'écriture du souvenir


def classer(question: list[float], souvenirs: list[Souvenir], maintenant: float,
            demi_vie: float, poids: tuple[float, float, float], k: int) -> list[tuple[float, Souvenir, tuple]]:
    """Composantes brutes → min-max sur les candidats → score → tri décroissant → k premiers."""
    sims = [cosinus(question, s.vecteur) for s in souvenirs]
    recs = [recence(maintenant - s.dernier_acces, demi_vie) for s in souvenirs]
    imps = [float(s.importance) for s in souvenirs]
    sims_n, recs_n, imps_n = min_max(sims), min_max(recs), min_max(imps)
    lignes = []
    for j, s in enumerate(souvenirs):
        score = score_pertinence(sims_n[j], recs_n[j], imps_n[j], poids)
        lignes.append((score, s, (sims[j], recs[j], sims_n[j], recs_n[j], imps_n[j])))
    lignes.sort(key=lambda ligne: (-ligne[0], ligne[1].texte))   # égalités départagées par le texte
    return lignes[:k]


def main() -> None:
    poids = (0.5, 0.3, 0.2)   # w_sim, w_rec, w_imp

    print("1. Contre-exemple : importance laissée sur l'échelle 1-10")
    a_brut = somme_ponderee((0.2, 0.1, 9), poids)
    b_brut = somme_ponderee((0.9, 0.9, 2), poids)
    ecart = 0.5 * (0.2 - 0.9) + 0.3 * (0.1 - 0.9) + 0.2 * (9 - 2)
    print(f"  A (0.2, 0.1, 9) = {a_brut:.2f}   B (0.9, 0.9, 2) = {b_brut:.2f}   A − B = {ecart:.2f} dont importance +{0.2 * 7:.2f}")
    assert round(a_brut, 2) == 1.93 and round(b_brut, 2) == 1.12 and a_brut > b_brut
    assert abs((a_brut - b_brut) - ecart) < 1e-12 and round(ecart, 2) == 0.81
    a_div = score_pertinence(0.2, 0.1, 9 / 10, poids)
    b_div = score_pertinence(0.9, 0.9, 2 / 10, poids)
    print(f"  importance divisée par 10 : A = {a_div:.2f}   B = {b_div:.2f}")
    assert round(a_div, 2) == 0.31 and round(b_div, 2) == 0.76 and b_div > a_div

    print("2. min_max : bornes, ordre, indépendance de l'unité, cas dégénéré")
    imp = [8.0, 9.0, 9.0, 6.0, 3.0]
    imp_n = min_max(imp)
    print(f"  importances {[int(x) for x in imp]} → {[round(x, 4) for x in imp_n]}")
    assert imp_n == [5 / 6, 1.0, 1.0, 0.5, 0.0]
    sur_100 = min_max([10 * x for x in imp])          # même information, autre unité
    decale = min_max([2.5 * x + 7 for x in imp])      # transformation affine de pente > 0
    assert all(abs(x - y) < 1e-12 and abs(x - z) < 1e-12 for x, y, z in zip(imp_n, sur_100, decale))
    assert min_max([0.7, 0.7, 0.7]) == [0.0, 0.0, 0.0]

    print("3. Combinaison convexe : le score reste dans [0, 1]")
    assert score_pertinence(0.0, 0.0, 0.0, poids) == 0.0
    assert abs(score_pertinence(1.0, 1.0, 1.0, poids) - 1.0) < 1e-12
    assert 0.0 <= score_pertinence(1.0, 0.0, 0.5, poids) <= 1.0
    print(f"  poids (0.5, 0.5, 0.5) sur (1, 1, 1) : {somme_ponderee((1, 1, 1), (0.5, 0.5, 0.5)):.1f}"
          f"   poids (0.6, 0.6, −0.2) sur (0, 0, 1) : {somme_ponderee((0, 0, 1), (0.6, 0.6, -0.2)):.1f}")
    for composantes, w in (((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)), ((0.0, 0.0, 1.0), (0.6, 0.6, -0.2)), ((0.2, 0.1, 9.0), poids)):
        try:
            score_pertinence(*composantes, w)
        except ValueError as e:
            print(f"  {composantes} avec {w} → ValueError : {e}")
        else:
            raise AssertionError("cette entrée aurait dû être refusée")

    print("4. Top-3 des souvenirs d'un acheteur immobilier, jour 90, demi-vie 30 jours")
    question = [0.8, 0.0, 0.0, 0.6, 0.0]   # « une villa avec jardin, près d'une bonne école ? »
    souvenirs = [
        Souvenir("Cherche une villa avec jardin", [1.0, 0.0, 0.0, 0.0, 0.0], dernier_acces=90.0, importance=8),
        Souvenir("Budget maximum 3,5 M AED", [0.6, 0.0, 0.8, 0.0, 0.0], dernier_acces=75.0, importance=9),
        Souvenir("Cherchait un deux-pièces à Dubai Marina", [0.28, 0.96, 0.0, 0.0, 0.0], dernier_acces=0.0, importance=9),
        Souvenir("Deux enfants scolarisés à Mirdif", [0.0, 0.0, 0.0, 1.0, 0.0], dernier_acces=60.0, importance=6),
        Souvenir("Préfère être appelé le soir", [0.0, 0.0, 0.0, 0.0, 1.0], dernier_acces=30.0, importance=3),
    ]
    tous = classer(question, souvenirs, maintenant=90.0, demi_vie=30.0, poids=poids, k=len(souvenirs))
    print("  souvenir                                   sim    rec    sim~   rec~   imp~   score")
    for score, s, (sim, rec, sim_n, rec_n, imp_n_j) in tous:
        print(f"  {s.texte:40s} {sim:6.3f} {rec:6.4f} {sim_n:6.4f} {rec_n:6.4f} {imp_n_j:6.4f} {score:7.4f}")
    assert [round(score, 4) for score, _, _ in tous] == [0.9667, 0.6996, 0.6036, 0.34, 0.0429]
    assert [round(d[0], 3) for _, _, d in tous] == [0.8, 0.48, 0.6, 0.224, 0.0]
    assert [round(d[1], 4) for _, _, d in tous] == [1.0, 0.7071, 0.5, 0.125, 0.25]
    top3 = classer(question, souvenirs, maintenant=90.0, demi_vie=30.0, poids=poids, k=3)
    print("  top-3 injecté :", " | ".join(s.texte for _, s, _ in top3))
    assert [s.texte for _, s, _ in top3] == [s.texte for _, s, _ in tous[:3]]
    assert "Deux enfants scolarisés à Mirdif" in [s.texte for _, s, _ in top3]

    brut = sorted(((somme_ponderee((cosinus(question, s.vecteur), recence(90.0 - s.dernier_acces, 30.0), s.importance), poids), s.texte)
                   for s in souvenirs), key=lambda x: (-x[0], x[1]))
    print(f"  sans normaliser, scores : {[round(v, 4) for v, _ in brut]}")
    print(f"  sans normaliser, top-3 : {' | '.join(t for _, t in brut[:3])}")
    assert [round(v, 4) for v, _ in brut] == [2.3, 2.2521, 1.9495, 1.65, 0.675]
    assert brut[2][1] == "Cherchait un deux-pièces à Dubai Marina"

    print("5. Multiplier tous les poids par c > 0 ne change pas l'ordre")
    comp = {s.texte: d[2:] for _, s, d in tous}
    ordre_1 = sorted(comp, key=lambda t: (-somme_ponderee(comp[t], (1.0, 1.0, 1.0)), t))
    ordre_tiers = sorted(comp, key=lambda t: (-somme_ponderee(comp[t], (1 / 3, 1 / 3, 1 / 3)), t))
    print(f"  poids (1, 1, 1) et (1/3, 1/3, 1/3) : même ordre = {ordre_1 == ordre_tiers}")
    assert ordre_1 == ordre_tiers

    print("6. Pièges du min-max : il est relatif aux candidats")
    mauvais = min_max([0.30, 0.25, 0.10])
    print(f"  cosinus bruts (0.30, 0.25, 0.10) → {mauvais} : le meilleur d'un lot médiocre reçoit 1")
    assert [round(x, 12) for x in mauvais] == [1.0, 0.75, 0.0]

    def deux_composantes(lot: dict[str, tuple[float, float]]) -> dict[str, float]:
        noms = sorted(lot)
        s_n = min_max([lot[n][0] for n in noms])
        r_n = min_max([lot[n][1] for n in noms])
        return {n: round(0.5 * s_n[i] + 0.3 * r_n[i], 4) for i, n in enumerate(noms)}

    sans_z = deux_composantes({"X": (0.9, 0.2), "Y": (0.5, 1.0)})
    avec_z = deux_composantes({"X": (0.9, 0.2), "Y": (0.5, 1.0), "Z": (0.1, 0.6)})
    print(f"  sans Z : {sans_z}   avec Z : {avec_z}")
    assert sans_z == {"X": 0.5, "Y": 0.3} and avec_z == {"X": 0.5, "Y": 0.55, "Z": 0.15}

    # Réponse de l'exercice 2 : avec les poids (0.2, 0.3, 0.5), le souvenir « Marina » repasse devant « enfants ».
    autre = {s.texte: score_pertinence(*d[2:], (0.2, 0.3, 0.5)) for _, s, d in tous}
    assert round(autre["Cherchait un deux-pièces à Dubai Marina"], 4) == 0.556
    assert round(autre["Deux enfants scolarisés à Mirdif"], 4) == 0.5286
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Contre-exemple : importance laissée sur l'échelle 1-10
  A (0.2, 0.1, 9) = 1.93   B (0.9, 0.9, 2) = 1.12   A − B = 0.81 dont importance +1.40
  importance divisée par 10 : A = 0.31   B = 0.76
…
  importances [8, 9, 9, 6, 3] → [0.8333, 1.0, 1.0, 0.5, 0.0]
…
  poids (0.5, 0.5, 0.5) sur (1, 1, 1) : 1.5   poids (0.6, 0.6, −0.2) sur (0, 0, 1) : -0.2
…
  souvenir                                   sim    rec    sim~   rec~   imp~   score
  Cherche une villa avec jardin             0.800 1.0000 1.0000 1.0000 0.8333  0.9667
  Budget maximum 3,5 M AED                  0.480 0.7071 0.6000 0.6653 1.0000  0.6996
  Deux enfants scolarisés à Mirdif          0.600 0.5000 0.7500 0.4286 0.5000  0.6036
  Cherchait un deux-pièces à Dubai Marina   0.224 0.1250 0.2800 0.0000 1.0000  0.3400
  Préfère être appelé le soir               0.000 0.2500 0.0000 0.1429 0.0000  0.0429
  top-3 injecté : Cherche une villa avec jardin | Budget maximum 3,5 M AED | Deux enfants scolarisés à Mirdif
  sans normaliser, scores : [2.3, 2.2521, 1.9495, 1.65, 0.675]
  sans normaliser, top-3 : Cherche une villa avec jardin | Budget maximum 3,5 M AED | Cherchait un deux-pièces à Dubai Marina
…
  sans Z : {'X': 0.5, 'Y': 0.3}   avec Z : {'X': 0.5, 'Y': 0.55, 'Z': 0.15}
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un score de pertinence n'est pas une somme pondérée de nombres pris tels quels. On ramène d'abord chaque signal sur la même échelle, on vérifie que les poids sont positifs et de somme 1, et ce n'est qu'ensuite que les poids disent vraiment ce qu'ils veulent dire.

## Squelette algorithmique

L'algorithme classe les souvenirs candidats en mélangeant trois signaux mis à la même échelle : la similarité avec la question, la récence et l'importance. La normalisation min-max vient avant la somme pondérée, sinon un signal à grande échelle écrase les autres.

```text
ALGORITHME ClasserLesSouvenirs
ENTRÉES : vecteur q de la question, souvenirs (vecteur v, âge, importance),
          demi-vie h, poids w_sim, w_rec, w_imp (positifs, de somme 1), k
SORTIE  : les k souvenirs les mieux notés

  POUR CHAQUE souvenir j FAIRE
      simⱼ ← Cosinus(q, vⱼ)
      recⱼ ← 0,5^(âgeⱼ / h)
      impⱼ ← importanceⱼ
  FIN POUR
  POUR CHAQUE signal x DANS {sim, rec, imp} FAIRE
      SI max(x) = min(x) ALORS x̃ⱼ ← 0 pour tous     (signal constant : il ne départage rien)
      SINON x̃ⱼ ← (xⱼ − min x) / (max x − min x)
  FIN POUR
  POUR CHAQUE souvenir j FAIRE
      scoreⱼ ← w_sim × s̃imⱼ + w_rec × r̃ecⱼ + w_imp × ĩmpⱼ
  FIN POUR
  RETOURNER les k plus grands scores
```

**Complexité.** Pour n souvenirs de dimension d : O(n × d) pour les cosinus, O(n) pour les récences et pour chaque normalisation (une passe pour trouver le minimum et le maximum, une passe pour normaliser), O(n) pour les scores, et O(n log k) pour garder les k meilleurs. La mémoire est O(n) pour les trois listes de signaux. La normalisation min-max dépend de l'ensemble des candidats : ajouter ou retirer un candidat peut changer le score des autres, ce qu'il faut savoir avant de comparer des scores d'une requête à l'autre.

**Du squelette au code.** `cosinus` donne simⱼ, `recence` donne recⱼ (sous la forme équivalente e^(−λ × âge) avec λ = ln 2 / h), `min_max` est la deuxième boucle, `somme_ponderee` et `score_pertinence` la troisième, et `classer` enchaîne les trois avant de trier. `score_pertinence` refuse des poids négatifs, des poids dont la somme n'est pas 1 et une composante hors de [0, 1] : c'est la garde qui empêche d'oublier la normalisation. `classer` départage les scores égaux par le texte du souvenir, pour que le classement soit reproductible.

## Cas d'usage réels aux Émirats

Les poids, les demi-vies et les seuils ci-dessous sont illustratifs : en production, on les règle sur un jeu de questions étiquetées propre à chaque métier.

### Immobilier — l'acheteur qui a changé de projet

Une agence immobilière de Dubaï suit ses acheteurs pendant des mois avec un agent qui mémorise chaque critère exprimé, avec une importance notée de 1 à 10 par le modèle au moment où le critère est écrit. Au jour 90, un client demande « une villa avec jardin, près d'une bonne école ? » ; les cinq souvenirs de l'exemple fait à la main sont candidats, avec une demi-vie de 30 jours. Le score normalisé place en tête la villa (0,9667), le budget (0,6996) et les enfants scolarisés à Mirdif (0,6036), et laisse dehors le deux-pièces à Dubai Marina (0,3400), un critère vieux de trois mois qui ne correspond plus au projet. Si l'équipe avait laissé l'importance sur l'échelle 1-10 sans la normaliser, le critère Marina (1,9495) aurait pris la place des enfants (1,65), et l'agent aurait proposé des appartements près de la Marina à une famille qui cherche une villa près d'une école. La contrainte est la minimisation des données de la PDPL : un critère que le score ne fait plus remonter depuis longtemps est supprimé, pas seulement déclassé. L'indicateur suivi est le taux de visites programmées après une proposition de l'agent.

### Banque — une contrainte ancienne mais critique

L'assistant d'investissement d'une banque de détail de Dubaï garde en mémoire ce que chaque client a dit lors de ses entretiens, y compris des refus explicites comme « jamais de produit à effet de levier », noté 10 en importance. Quatorze mois plus tard, soit environ 425 jours, le client demande des informations sur un produit structuré : la similarité de ce vieux refus avec la question est moyenne et sa récence très basse (avec une demi-vie de 180 jours,

$$
2^{-425/180} \approx 0{,}19
$$

), mais son importance normalisée vaut 1. Avec des poids qui laissent assez de place à l'importance pour ce type de souvenir, le refus entre dans le top-k et l'agent rappelle la contrainte au conseiller au lieu de pousser le produit. Sans le terme d'importance, le refus serait noyé sous des souvenirs plus récents et plus bavards, et la banque recommanderait un produit que le client avait exclu, ce qui l'exposerait à une plainte et à une remarque de conformité. La banque choisit donc ses poids par type de souvenir et les valide sur des cas étiquetés plutôt qu'à l'œil. L'indicateur suivi est le nombre de recommandations émises contre une contrainte mémorisée, avec un objectif de zéro.

### Assurance — équilibrer l'historique et l'actualité d'un dossier

Un assureur auto et santé confie à un agent l'historique de chaque assuré : sinistres passés, garages contestés, pièces manquantes, préférences de contact. Pour un dossier de sinistre en cours, les échanges de la semaine ont une récence proche de 1, tandis qu'un signalement de fraude présumée vieux de deux ans a une récence faible mais une importance maximale. Le score normalisé donne à chacun sa place : les derniers échanges remontent par la récence, le signalement ancien par l'importance, et un échange banal d'il y a deux ans ne remonte plus du tout. Sans normalisation, la note d'importance sur 1 à 10 écraserait le reste, chaque dossier afficherait les mêmes vieilles alertes en tête, et le gestionnaire finirait par ne plus les lire. La contrainte est l'équité de traitement : un signalement ancien et non confirmé ne doit pas décider seul, si bien que l'agent le présente comme un élément à vérifier et jamais comme une conclusion. Les indicateurs suivis sont le temps moyen de traitement d'un dossier et la part des souvenirs rappelés que le gestionnaire juge utiles.

### RH — un dossier d'embauche suivi sur plusieurs émirats

Un cabinet RH présent dans plusieurs émirats fait suivre par un agent chaque dossier d'embauche : offre signée, contrat enregistré auprès du MOHRE, visite médicale, demande d'Emirates ID, inscription au WPS pour le versement des salaires. Quand le candidat demande « où en est mon visa ? », la présélection vectorielle ramène une trentaine de souvenirs, dont beaucoup de messages de politesse presque identiques. Le score les fait reculer, parce que leur importance est basse (2 ou 3), alors que le souvenir « visite médicale faite », noté 8, remonte avec le dernier statut connu ; comme le score ne supprime pas les doublons, l'équipe ajoute un dédoublonnage qui fusionne deux souvenirs dont le cosinus dépasse 0,95. Sans score combiné, l'agent remplirait son contexte de messages similaires mais inutiles et pourrait rater le statut qui compte. Un statut administratif périmé étant dangereux, le cabinet ajoute une règle dure en plus du score : un statut de plus de 30 jours ne peut pas être affirmé de mémoire, et l'agent rappelle l'outil qui interroge le système officiel (étape 16). L'indicateur suivi est la part des réponses de statut confirmées par l'outil le jour même.

### Crypto — des alertes dont la gravité sert d'importance

Une plateforme d'actifs virtuels agréée par la VARA mémorise chaque alerte de surveillance avec une gravité de 1 à 10, qui joue le rôle d'importance, et compte le temps en heures, avec une demi-vie d'environ 34 heures (l'exemple de l'étape 16). Quand un opérateur demande « que se passe-t-il sur le pool de liquidité BTC/AED ? », l'agent score les alertes candidates : la similarité dit lesquelles concernent ce pool, la récence lesquelles sont en cours, la gravité lesquelles sont graves. Une alerte critique (gravité 9) d'il y a trois jours garde une récence de

$$
2^{-72/34} \approx 0{,}23
$$

et peut encore entrer dans le top-k si elle concerne ce pool, alors qu'une alerte mineure d'il y a une heure sur un autre pool n'y entre pas, faute de similarité. Sans le terme de similarité, l'opérateur verrait toutes les alertes récentes de la plateforme, sans rapport avec sa question ; sans la gravité, un incident grave encore ouvert disparaîtrait derrière le bruit de l'heure. La plateforme doit pouvoir justifier chaque décision devant son régulateur : l'agent journalise, pour chaque alerte montrée, ses trois composantes et son score. L'indicateur suivi est le délai de prise en charge des alertes critiques.

### Secteur public — la mémoire d'une session bilingue

Une entité de services publics en ligne, accessible par UAE Pass, garde pendant une session les informations données par l'usager : la langue préférée, le service visé, les pièces déjà fournies. Le temps se compte en échanges, et la langue préférée reçoit une importance de 10, parce qu'une réponse dans la mauvaise langue fait échouer toute la suite. À chaque tour, l'agent score les souvenirs de la session : une pièce fournie au deuxième échange reste en tête dès que la question porte sur les justificatifs, grâce à sa similarité, même dix échanges plus tard. Sans ce score, l'agent recopierait toute la session dans le prompt, ce qui fait croître le coût en tokens à chaque échange (étape 72), ou bien il redemanderait des pièces déjà fournies, ce qui exaspère l'usager et le pousse à abandonner sa démarche. Par minimisation des données, les souvenirs de session sont effacés à la fin de la démarche ; seuls restent les éléments que l'usager a accepté de conserver dans son profil. L'indicateur suivi est le nombre de demandes redondantes de pièces par session, avec un objectif de zéro.

## Pièges et limites

- **Additionner des échelles différentes.** Une importance sur 1-10 à côté d'un cosinus dans [0, 1] donne au plus petit poids la plus grande influence (point 1) : on normalise toujours avant de pondérer.
- **Oublier que le min-max est relatif au lot.** Le meilleur d'un lot médiocre reçoit 1 : des cosinus bruts de 0,30 ; 0,25 et 0,10 deviennent 1 ; 0,75 et 0, si bien qu'on garde un plancher absolu sur le cosinus brut avant de normaliser. Ajouter un candidat peut même inverser deux autres : avec des poids 0,5 et 0,3 sur la similarité et la récence, X (0,9 ; 0,2) bat Y (0,5 ; 1,0) par 0,5 contre 0,3, mais l'arrivée de Z (0,1 ; 0,6) fait passer Y à 0,55, devant X qui reste à 0,5 (bloc 6 du code).
- **Laisser varier une importance notée par un LLM.** La note change d'un appel à l'autre et d'une version de modèle à l'autre : on la calcule une fois, à l'écriture du souvenir, avec un prompt et une version de modèle fixés, et on la stocke.
- **La boucle de renforcement.** Un souvenir injecté voit son horloge remise à zéro (étape 16) ; il gagne en récence et sera rappelé encore. Pour qu'un souvenir moyen ne s'auto-entretienne pas, on ne remet l'horloge à zéro que si le souvenir a réellement servi à la réponse, ou l'on plafonne le nombre de rappels.
- **Régler les poids à l'œil.** On les choisit sur un jeu de questions étiquetées avec leurs souvenirs utiles, en mesurant le Recall@k (étape 25), et l'on refait la mesure à chaque changement de modèle d'embedding.

### Exercice feuille blanche

1. Sans regarder le code, écrire `min_max` et `score_pertinence` à partir des équations, puis vérifier que le souvenir « villa » vaut 0,9667.
2. Prédire, puis vérifier : avec les poids (0,2 ; 0,3 ; 0,5), le souvenir « deux-pièces à Dubai Marina » entre-t-il dans le top-3 ? (Réponse : oui. Il vaut

$$
0{,}2 \times 0{,}28 + 0{,}3 \times 0 + 0{,}5 \times 1 = 0{,}556 ,
$$

contre

$$
0{,}2 \times 0{,}75 + 0{,}3 \times 0{,}4286 + 0{,}5 \times 0{,}5 = 0{,}5286
$$

pour les enfants : une importance trop lourde ramène les vieux critères, même normalisés.)
3. Trouver le bug : `return [(v - lo) / (hi - lo) for v in valeurs]` sans la ligne `if hi == lo`. Que se passe-t-il quand tous les candidats ont la même importance ? (Réponse : `ZeroDivisionError`. Avec la garde, la composante vaut 0 partout, parce qu'un signal constant ne départage personne.)

## Pour aller plus loin

Park et al. ajoutent la *réflexion* : l'agent résume régulièrement ses souvenirs importants en conclusions plus générales, qui deviennent à leur tour des souvenirs. D'autres normalisations existent : le z-score (moyenne 0, écart-type 1), moins sensible à un candidat extrême mais non borné, ou une fusion par rangs comme RRF (étape 24), qui ignore les valeurs et ne garde que l'ordre. Enfin, les poids peuvent s'apprendre à partir de jugements de pertinence (apprentissage du classement, *learning to rank*).

> Suite : [Formules et algorithmes du RAG](<../05-RAG/18-RAG-Formules-Theoremes-Algorithmes.md>) — étape 18.
