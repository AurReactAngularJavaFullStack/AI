# Étape 2 — Softmax, température et choix du prochain token

> Étape 2 du parcours · Prérequis : [Définitions d'un agent](<../01-Agent/01-Agent-Definitions-Fondamentaux.md>) · Suite : [Tokenisation BPE](<02b-Tokenisation-BPE.md>)

## Définition

La dernière couche d'un LLM ne choisit pas un mot. Elle produit un score brut par token du vocabulaire : le **logit** zᵢ, un réel quelconque, positif ou négatif, sans borne. La fonction softmax transforme ces scores en probabilités strictement positives qui somment à 1, et la température T règle à quel point cette distribution se concentre sur les meilleurs logits. Le décodeur choisit ensuite le prochain token : soit le plus probable (décodage glouton), soit un tirage au hasard dans la distribution, souvent après en avoir coupé la queue (top-k, top-p). Le token choisi est ajouté au texte, et l'on recommence pour le suivant.

## Rôle dans un agent

Dans la boucle percevoir → décider → agir → observer de l'étape 1, cette formule est le cœur du temps « décider » : chaque token de la réponse du modèle, y compris le nom de l'outil appelé et chaque caractère de ses arguments JSON, sort d'une softmax. La température, le décodage glouton, le top-k et le top-p sont tous des réglages de cette unique formule. On s'en sert aussi hors du modèle : un **routeur** qui choisit entre plusieurs agents fait une softmax sur leurs scores, un **garde-fou** lit l'entropie de la distribution comme un signal d'incertitude, et l'**entraînement** ou l'ajustement fin (fine-tuning) d'un modèle repose sur le gradient de l'entropie croisée démontré plus bas.

Ces réglages ne sont pas toujours entre vos mains. Avec un modèle ouvert hébergé chez vous (Jais, Falcon), vous choisissez T, k et pₜₒₚ. Sur les modèles Claude actuels (par exemple `claude-opus-5-5`, état de l'API en novembre 2026), l'API refuse les paramètres `temperature`, `top_p` et `top_k` : la fiabilité d'une sortie structurée vient alors des schémas stricts et des sorties structurées (étape 8), pas d'une température nulle. Comprendre la formule reste indispensable dans les deux cas : c'est elle qui explique pourquoi un modèle peut encore produire un token improbable.

## Équation complète

Softmax avec température, pour un vocabulaire de |V| tokens :

$$
p_i = \frac{e^{z_i / T}}{\sum_{j=1}^{|V|} e^{z_j / T}}
$$

Forme stable, celle que l'on programme, avec m = maxⱼ zⱼ :

$$
p_i = \frac{e^{(z_i - m) / T}}{\sum_{j=1}^{|V|} e^{(z_j - m) / T}}
$$

L'ancienne version de ce fichier écrivait la forme stable sans la température (

$$
e^{z_i + c}
$$

avec c = −maxⱼ zⱼ). Elle est corrigée ci-dessus : on retranche le maximum, puis on divise par T. C'est équivalent à retrancher maxⱼ (zⱼ / T) après la division, parce que (zᵢ − m)/T = zᵢ/T − m/T et que m/T est le plus grand des zⱼ/T quand T > 0.

Jacobien de la softmax, c'est-à-dire la dérivée de chaque probabilité par rapport à chaque logit :

$$
\frac{\partial p_i}{\partial z_j} = \frac{1}{T}\, p_i \,(\delta_{ij} - p_j)
$$

Entropie croisée quand la bonne réponse est le token c, et son gradient :

$$
L = -\ln p_c = -\sum_{i=1}^{|V|} y_i \ln p_i
$$

$$
\frac{\partial L}{\partial z_j} = \frac{p_j - y_j}{T}
$$

Entropie de la distribution :

$$
H(p) = -\sum_{i=1}^{|V|} p_i \ln p_i
$$

Troncature top-k ou top-p suivie d'une renormalisation, où K est l'ensemble des tokens gardés :

$$
q_i = \frac{p_i}{\sum_{j \in K} p_j} \;\; \text{si } i \in K, \qquad q_i = 0 \;\; \text{sinon}
$$

## Décryptage des symboles

$$
z_i
$$

**Sens :** logit du token i : score brut, avant toute probabilité · **Type / plage :** réel quelconque, non borné · **Variable Python :** `logits[i]`

$$
\lvert V \rvert
$$

**Sens :** taille du vocabulaire, souvent de l'ordre de 100 000 tokens · **Type / plage :** entier ≥ 1 · **Variable Python :** `len(logits)`

$$
T
$$

**Sens :** température : diviseur des logits avant l'exponentielle · **Type / plage :** réel > 0 · **Variable Python :** `temperature`

$$
m
$$

**Sens :** plus grand logit, retranché pour la stabilité · **Type / plage :** réel · **Variable Python :** `pic`

$$
p_i
$$

**Sens :** probabilité du token i après la softmax · **Type / plage :** réel dans ]0, 1[ si | V | ≥ 2 · **Variable Python :** `p[i]`

$$
\delta_{ij}
$$

**Sens :** symbole de Kronecker : 1 si i = j, 0 sinon · **Type / plage :** 0 ou 1 · **Variable Python :** `delta`

$$
c
$$

**Sens :** indice de la bonne réponse pendant l'entraînement · **Type / plage :** entier · **Variable Python :** `cible`

$$
y_i
$$

**Sens :** vecteur « one-hot » de la bonne réponse : (formule ci-dessous), les autres 0 · **Type / plage :** 0 ou 1 · **Variable Python :** `1.0 if j == cible else 0.0`

$$
y_c = 1
$$

$$
L
$$

**Sens :** entropie croisée : (formule ci-dessous) · **Type / plage :** réel ≥ 0 · **Variable Python :** `entropie_croisee(logits, cible)`

$$
-\ln p_c
$$

$$
H(p)
$$

**Sens :** entropie de la distribution : 0 si certaine, ln | V | si uniforme · **Type / plage :** réel dans [0, ln | V |] · **Variable Python :** `entropie(p)`

$$
k
$$

**Sens :** nombre de tokens gardés par le top-k · **Type / plage :** entier dans [1, | V |] · **Variable Python :** `k`

$$
p_{\text{top}}
$$

**Sens :** masse cumulée visée par le top-p · **Type / plage :** réel dans ]0, 1] · **Variable Python :** `p_top`

$$
K
$$

**Sens :** ensemble des tokens gardés après troncature · **Type / plage :** sous-ensemble du vocabulaire · **Variable Python :** `gardes`

$$
q_i
$$

**Sens :** probabilité après troncature et renormalisation · **Type / plage :** réel dans [0, 1] · **Variable Python :** `tronquee[i]`

L'exponentielle rend chaque terme strictement positif et agrandit beaucoup les écarts entre scores : un écart de 1 entre deux logits devient un rapport de e ≈ 2,72 entre leurs probabilités. Diviser les logits par T < 1 agrandit encore ces écarts, et l'agent devient plus sûr de lui ; T > 1 les écrase, et l'agent hésite. Le symbole δᵢⱼ distingue deux dérivées différentes : celle de la probabilité d'un token par rapport à son propre logit, et celle par rapport au logit d'un autre token.

## Démonstration

Cette section adapte, en les corrigeant et en les complétant, les sections « 3. Démonstration Mathématique : Gradient de la Softmax et Perte Cross-Entropy » et « 4. Analyse de la Température » du fichier de l'étape suivante.

### 1. Des probabilités valides : chaque pᵢ est dans ]0, 1[ et leur somme vaut 1

Pour tout réel x, eˣ > 0. Le numérateur

$$
e^{z_i/T}
$$

est donc strictement positif, et le dénominateur, qui contient ce même terme plus au moins un autre terme strictement positif dès que |V| ≥ 2, est strictement plus grand que lui : 0 < pᵢ < 1. La somme vaut 1, parce que la somme des numérateurs est exactement le dénominateur :

$$
\sum_{i=1}^{|V|} p_i = \frac{\sum_{i} e^{z_i/T}}{\sum_{j} e^{z_j/T}} = 1
$$

Conséquence pratique : aucun token n'a une probabilité exactement nulle. Même un token absurde garde une chance minuscule d'être tiré, ce qui justifie le top-k et le top-p (point 6).

### 2. Invariance par translation, d'où « retrancher le max »

Ajoutons la même constante a à tous les logits. Le facteur

$$
e^{a/T}
$$

sort de chaque exponentielle, parce que

$$
e^{(z_i + a)/T} = e^{a/T}\, e^{z_i/T} ,
$$

et il se simplifie entre le numérateur et le dénominateur :

$$
\frac{e^{(z_i + a)/T}}{\sum_{j} e^{(z_j + a)/T}} = \frac{e^{a/T}\, e^{z_i/T}}{e^{a/T} \sum_{j} e^{z_j/T}} = p_i
$$

On choisit a = −m. Le plus grand exposant devient 0 et tous les autres sont négatifs, d'où deux garanties : chaque exponentielle vaut au plus e⁰ = 1, donc aucune ne peut déborder ; et le dénominateur contient le terme e⁰ = 1, donc il vaut au moins 1 et l'on ne divise jamais par zéro.

L'ancienne version de ce fichier disait que retrancher le maximum « empêche e²⁰ de dépasser ce qu'un flottant peut stocker ». **C'est faux** : e²⁰ ≈ 4,85 × 10⁸, très loin de la limite. Un `float` Python (64 bits) monte jusqu'à environ 1,80 × 10³⁰⁸ = e⁷⁰⁹,⁷⁸, et c'est au-delà que `math.exp` lève `OverflowError` : `math.exp(1000)` échoue, alors que la version stable traite sans difficulté les logits [1000, 999, 998]. Ces valeurs arrivent plus vite qu'on ne le croit : un logit de 14,2 divisé par une température de 0,01 donne un exposant de 1 420. Dans l'autre sens, des logits très négatifs ont des exponentielles qui s'arrondissent toutes à 0,0, et la formule naïve divise alors 0 par 0. En calcul flottant sur 32 bits, fréquent sur carte graphique, la limite tombe même vers e⁸⁸,⁷.

### 3. Le jacobien, par la règle du quotient

Notons sⱼ = zⱼ / T,

$$
u_i = e^{s_i}
$$

et

$$
v = \sum_{l} e^{s_l} ,
$$

de sorte que pᵢ = uᵢ / v. Deux dérivées préparent le calcul :

- ∂ uᵢ / ∂ zⱼ = uᵢ δᵢⱼ / T, parce que uᵢ ne dépend que de zᵢ et que la dérivée de

$$
e^{z_i/T}
$$

par rapport à zᵢ vaut

$$
e^{z_i/T} \times 1/T
$$

(dérivée d'une fonction composée) ;
- ∂ v / ∂ zⱼ = uⱼ / T, parce que dans la somme v, seul le terme l = j dépend de zⱼ.

La règle du quotient (u/v)' = (u'v − uv')/v² donne alors :

$$
\frac{\partial p_i}{\partial z_j} = \frac{\frac{u_i \delta_{ij}}{T}\, v - u_i\, \frac{u_j}{T}}{v^2} = \frac{1}{T}\cdot\frac{u_i}{v}\left(\delta_{ij} - \frac{u_j}{v}\right) = \frac{1}{T}\, p_i\, (\delta_{ij} - p_j)
$$

Pour i = j, on obtient 1/T pᵢ (1 − pᵢ) ; pour i ≠ j, −1/T pᵢ pⱼ. À T = 1, c'est la formule de l'ancienne version ; la température multiplie toutes les dérivées par 1/T, ce qui veut dire qu'à basse température la distribution réagit plus fort au moindre changement de logit. Le signe moins hors de la diagonale traduit le fait que la masse totale est fixe : si un autre token gagne, celui-ci perd.

Deux propriétés servent de contrôle dans le code. Chaque **ligne** somme à 0 :

$$
\sum_j \frac{\partial p_i}{\partial z_j} = \frac{1}{T} p_i (1 - \sum_j p_j) = 0 ,
$$

parce que pousser tous les logits ensemble ne change rien (point 2). Chaque **colonne** somme à 0 :

$$
\sum_i \frac{\partial p_i}{\partial z_j} = \frac{1}{T}(p_j - p_j \sum_i p_i) = 0 ,
$$

parce que la somme des probabilités reste égale à 1. Enfin, le terme diagonal p(1−p) est maximal en p = 1/2, où il vaut 1/4 : sa dérivée 1 − 2p s'annule en p = 1/2.

En chiffres, avec z = [1 ; 0,5 ; −0,3] et T = 1 :

$$
u = [2{,}718282 ;\ 1{,}648721 ;\ 0{,}740818] ,
$$

v = 5,107821,

$$
p = [0{,}532180 ;\ 0{,}322784 ;\ 0{,}145036] .
$$

Le terme diagonal vaut 0,532180 × 0,467820 = 0,248964, le terme (0, 1) vaut −0,532180 × 0,322784 = −0,171779. À T = 0,5, p = [0,6934 ; 0,2551 ; 0,0515] et le terme diagonal devient 0,6934 × 0,3066 / 0,5 = 0,4252.

### 4. Le gradient de l'entropie croisée vaut p − y

Pendant l'entraînement, on connaît le bon token c et l'on minimise

$$
L = -\ln p_c .
$$

Par dérivation d'une fonction composée, puis en remplaçant

$$
\partial p_c / \partial z_j
$$

par le jacobien du point 3 :

$$
\frac{\partial L}{\partial z_j} = -\frac{1}{p_c}\,\frac{\partial p_c}{\partial z_j} = -\frac{1}{p_c}\cdot\frac{1}{T}\, p_c\,(\delta_{cj} - p_j) = \frac{p_j - y_j}{T}
$$

À T = 1, le gradient vaut simplement p − y. Le facteur

$$
1/p_c
$$

qui vient du logarithme annule exactement le facteur

$$
p_c
$$

du jacobien : c'est pour cela que le signal ne disparaît pas quand le modèle se trompe lourdement. Les composantes somment à 0, parce que ∑ⱼ pⱼ = ∑ⱼ yⱼ = 1.

L'ancienne version de ce fichier disait : « un logit très grand devant les autres fait saturer l'exponentielle, le gradient p(1−p) vaut presque 0, et le modèle n'apprend plus sur cet exemple, parce qu'il est déjà certain ». C'est vrai pour la dérivée de la softmax **seule**, mais **trompeur** pour l'apprentissage par entropie croisée : le gradient p − y ne s'annule que si p ≈ y, c'est-à-dire si le modèle est sûr **et** juste. Avec z = [8 ; 0 ; 0], on a

$$
p = [0{,}99933 ;\ 0{,}000335 ;\ 0{,}000335] .
$$

Si la bonne réponse est le token 0, le gradient vaut [−0,00067 ; 0,00034 ; 0,00034] : presque rien à apprendre. Si la bonne réponse est le token 1, il vaut [0,99933 ; −0,99966 ; 0,00034] : un signal fort, alors même que p₁(1 − p₁) = 0,00034 est minuscule. La saturation redevient un vrai problème si l'on entraîne avec une erreur quadratique sur les probabilités,

$$
(1 - p_c)^2 ,
$$

dont la dérivée par rapport à

$$
z_c
$$

vaut

$$
-2\,p_c (1 - p_c)^2
$$

et s'écrase quand

$$
p_c \approx 0
$$

C'est la raison pour laquelle les classifieurs s'entraînent à l'entropie croisée.

### 5. Les limites en température, et ce qui se passe entre les deux

**Quand T → 0⁺**, supposons le maximum m atteint par un seul token i\*. En divisant numérateur et dénominateur par

$$
e^{m/T}
$$

(point 2) :

$$
p_i(T) = \frac{e^{(z_i - m)/T}}{1 + \sum_{j \ne i^\star} e^{(z_j - m)/T}}
$$

Pour j ≠ i\*, zⱼ − m < 0, donc (zⱼ − m)/T → −∞ et

$$
e^{(z_j - m)/T} \to 0 .
$$

Il reste

$$
p_{i^\star} \to 1/(1 + 0) = 1
$$

et pᵢ → 0 pour tous les autres : la softmax tend vers le vecteur one-hot de l'argmax, le décodage glouton. Si le maximum est partagé par r tokens, le même calcul donne 1/r à chacun : avec [3 ; 3 ; 1] et T = 0,01, on obtient [0,5 ; 0,5 ; 0]. La fonction `argmax` du code prend alors le premier indice : c'est une convention de décodage, pas la limite.

**Quand T → ∞**, zᵢ / T → 0 pour chaque i, donc chaque exponentielle tend vers e⁰ = 1 et le dénominateur tend vers |V| : pᵢ → 1/|V|, la distribution uniforme. L'agent tire alors au hasard dans tout le vocabulaire.

**Entre les deux**, la probabilité du meilleur token décroît strictement quand T augmente :

$$
p_{i^\star}(T) = 1 / \left(1 + \sum_{j \ne i^\star} e^{-(m - z_j)/T}\right) ,
$$

et chaque exposant −(m − zⱼ)/T augmente avec T parce que m − zⱼ > 0, donc le dénominateur augmente. L'entropie, elle, croît avec T. Avec β = 1/T, on peut écrire

$$
H = \ln \sum_j e^{\beta z_j} - \beta\, \mathbb{E}_p[z] ;
$$

en dérivant, et parce que la dérivée de 𝔼ₚ[z] par rapport à β est la variance Varₚ(z), on trouve dH/dβ = −β Varₚ(z) ≤ 0. L'entropie diminue donc quand β augmente, c'est-à-dire qu'elle augmente avec T, strictement dès que les logits ne sont pas tous égaux. Sur les logits d'outils [3,0 ; 2,4 ; 0,5], la probabilité de « chercher » passe de 0,9526 à T = 0,2 à 0,3676 à T = 10 (limite 1/3), et l'entropie de 0,1909 à 1,0932 (limite ln 3 = 1,0986).

### 6. Top-k et top-p : tronquer, puis renormaliser

On garde un ensemble K de tokens, on met les autres à 0, et l'on divise les gardés par leur masse

$$
M = \sum_{j \in K} p_j .
$$

Trois propriétés en découlent. La somme vaut 1, parce que

$$
\sum_{i \in K} p_i / M = M / M
$$

C'est de nouveau une distribution, dans laquelle on peut tirer. Les rapports entre tokens gardés ne changent pas, parce que

$$
q_i / q_j = (p_i / M)/(p_j / M) = p_i / p_j
$$

La troncature ne réordonne rien. Et chaque token gardé gagne de la masse, parce que M ≤ 1 donne qᵢ ≥ pᵢ.

Le **top-k** garde les k tokens les plus probables, quelle que soit la forme de la distribution. Le **top-p** garde le plus petit début de la liste triée par probabilité décroissante dont la masse cumulée atteint pₜₒₚ ; ce début existe toujours, parce que la masse totale vaut 1 ≥ pₜₒₚ. Sa taille s'adapte : quand le modèle est sûr, un ou deux tokens suffisent ; quand il hésite, le noyau s'élargit. Sur la distribution pointue de logits [5 ; 1 ; 0,5 ; 0 ; −1], où pₘₐₓ = 0,9628, le top-p à 0,9 ne garde qu'un token, alors que le top-k à 3 en garde trois.

Exemple, à T = 0,85 sur les logits [2,2 ; 1,6 ; 1,4 ; 0,2 ; −1,5] :

$$
p = [0{,}5021 ;\ 0{,}2479 ;\ 0{,}1959 ;\ 0{,}0477 ;\ 0{,}0065] .
$$

Les masses cumulées valent 0,5021, puis 0,7500, puis 0,9459 : on s'arrête au troisième token, M = 0,9459, et les gardés deviennent 0,5308, 0,2621 et 0,2071. Le top-k à 2 garde une masse de 0,7500 et donne 0,6695 et 0,3305. Sans la division par M, les poids sommeraient à 0,9459 : un tirage u ≥ 0,9459 ne tomberait sur aucun token, et l'échantillonneur fausserait les fréquences (exercice 3).

### 7. Exemple fait à la main (le code reprend ces nombres)

Avec les logits [2 ; 1 ; 0 ; −1] et T = 1 : m = 2, les exposants valent 0, −1, −2 et −3, les exponentielles 1, 0,367879, 0,135335 et 0,049787, leur somme 1,553002. Les probabilités valent donc 1 / 1,553002 = 0,643914, puis 0,236883, 0,087144 et 0,032059, et leur somme vaut 1.

Pour l'agent SQL, les logits 14,2 (`SELECT`) et 8,1 (`INSERT`) à T = 0,7 ont un écart réduit de 6,1 / 0,7 = 8,7143 ; e⁸,⁷¹⁴³ = 6 089,3, donc

$$
P(\texttt{INSERT}) = 1/(1 + 6\,089{,}3) = 0{,}000164 ,
$$

soit 0,0164 %. Sur 100 000 tirages, on attend 16,4 `INSERT` ; le tirage avec la graine 42 en donne 15.

## Effets et comportement

- **Une température basse concentre, une température haute étale.** T < 1 agrandit les écarts entre logits, T > 1 les écrase ; T → 0 donne l'argmax (si le maximum est unique), le bon réglage pour du JSON, du SQL et des arguments d'outils quand l'API le permet ; T → ∞ donne l'uniforme.
- **La sensibilité croît comme 1/T.** À basse température, un petit changement de logits peut faire basculer le choix d'un outil à l'autre.
- **Le gradient d'entropie croisée, p − y, ne s'annule que si le modèle est sûr et juste.** Un modèle sûr et faux reçoit le gradient le plus fort ; l'ancienne affirmation « il n'apprend plus parce qu'il est certain » ne valait que pour la softmax seule.
- **Le top-p s'adapte à la forme de la distribution, le top-k non.** Le top-k garde des tokens improbables quand le modèle est sûr, et en coupe de plausibles quand il hésite.
- **Les petites probabilités s'additionnent sur une longue sortie.** C'est la fiabilité composée de l'étape 1 appliquée aux tokens : si chacun des 300 tokens d'un JSON laissait 0,0164 % au mauvais token, la probabilité d'au moins une erreur vaudrait 1 − (1 − 0,000164)³⁰⁰ ≈ 4,8 %.

## Du symbole au code Python

$$
z,\quad T,\quad m
$$

**Variable ou fonction :** `logits`, `temperature`, `pic`

$$
p = \mathrm{softmax}(z / T)
$$

**Variable ou fonction :** `softmax(logits, temperature)`

**Symbole :** la même formule sans retrancher m · **Variable ou fonction :** `softmax_naive(logits, temperature)`

**Symbole :** limite T → 0 · **Variable ou fonction :** `argmax(logits)`

$$
\partial p_i / \partial z_j
$$

**Variable ou fonction :** `jacobien_theorique(p, temperature)`, contrôlé par `jacobien_differences_finies`

$$
L = -\ln p_c,\quad (p - y)/T
$$

**Variable ou fonction :** `entropie_croisee(logits, cible, temperature)`, `gradient_entropie_croisee(...)`

$$
H(p)
$$

**Variable ou fonction :** `entropie(p)`

**Symbole :** troncature top-k, top-p · **Variable ou fonction :** `top_k(p, k)`, `top_p(p, p_top)`

**Symbole :** tirage d'un token · **Variable ou fonction :** `echantillonner(p, rng)` avec `rng = random.Random(42)`

Le déroulé suit les fonctions dans l'ordre où `main` les appelle. Les nombres cités sont ceux que le programme affiche. Copiez le bloc dans `softmax_agent.py`.

### Déroulé, ligne par ligne

**`softmax(logits, temperature)`** transforme des scores bruts en probabilités. Premier appel : `logits = [2.0, 1.0, 0.0, -1.0]`, température 1.

- `if temperature <= 0.0` : on refuse. Diviser par T = 0 n'est pas défini ; le cas « température zéro » n'appelle pas cette fonction, il appelle `argmax`.
- `pic = max(logits)` : le plus grand score, ici 2. C'est le m de la forme stable.
- `math.exp((z - pic) / temperature)` : les exposants valent 0, −1, −2 et −3, les exponentielles 1, 0,367879, 0,135335 et 0,049787. Le plus grand terme vaut toujours e⁰ = 1 : aucune exponentielle ne peut déborder (démonstration, point 2, qui corrige l'ancienne phrase sur e²⁰).
- `total = sum(exponentielles)` : le dénominateur, 1,553002 ici. Il vaut au moins 1, puisqu'il contient e⁰.
- `return [e / total for e in exponentielles]` : 0,643914, 0,236883, 0,087144 et 0,032059. Leur somme vaut 1, et aucune n'est négative, parce que l'exponentielle ne l'est jamais.

**`softmax_naive(logits, temperature)`** est la formule recopiée sans retrancher le maximum. Sur `[2.0, 1.0, 0.0, -1.0]`, elle donne les mêmes nombres. Sur `[1000.0, 999.0, 998.0]`, `math.exp(1000)` lève `OverflowError`, alors que `softmax` renvoie `[0.665241, 0.244728, 0.090031]`, exactement la softmax de `[2, 1, 0]`. Sur `[-1000.0, -1001.0]`, les deux exponentielles valent `0.0`, `total` vaut `0.0`, et la division lève `ZeroDivisionError` ; `softmax` renvoie `[0.731059, 0.268941]`.

Le test `softmax([z + 5.0 for z in logits])` refait les mêmes étapes. `pic` vaut alors 7 au lieu de 2, les écarts `z - pic` sont identiques, donc les probabilités aussi.

**La boucle sur la température**, logits des outils `[3.0, 2.4, 0.5]`.

- À chaque tour, `softmax(z_outils, temperature=T)` divise les logits par `T` avant l'exponentielle. `T = 0.2` agrandit les écarts : « chercher » passe à 0,9526. `T = 10` les écrase : « chercher » retombe à 0,3676, proche de 1/3.
- `confiances` et `entropies` gardent la probabilité de « chercher » et l'entropie à chaque température. Les deux `assert` vérifient la démonstration (point 5) : la première liste décroît strictement, la seconde croît strictement. L'ancienne vérification enchaînait trois conditions par des « ou », dont la première était redondante avec la troisième ; elle est remplacée par ces deux tests nets.
- `softmax([3.0, 3.0, 1.0], temperature=0.01)` vaut `[0.5, 0.5, 0.0]` : avec deux maxima égaux, la limite partage la masse.

**`entropie(probabilites)`** ajoute `-p * math.log(p)` pour chaque probabilité non nulle. À T = 0,2 elle vaut 0,1909 (l'agent est presque sûr) ; à T = 10, 1,0932 (il hésite, la limite est ln 3 = 1,0986). Le `if p > 0.0` évite `math.log(0)`, qui lève une erreur ; on peut omettre ces termes parce que p ln p → 0 quand p → 0.

**`argmax(logits)`**, la limite T → 0 écrite à part.

- `max(range(len(logits)), key=lambda i: logits[i])` parcourt les indices et garde celui dont le logit est le plus grand, ici l'indice 0, « chercher ». En cas d'égalité, `max` garde le premier.
- La liste renvoyée vaut `[1.0, 0.0, 0.0]`. On ne calcule aucune exponentielle.

**L'agent SQL.** `softmax([14.2, 8.1], temperature=0.7)` donne P(SELECT) = 0,999836 et P(INSERT) = 0,000164, soit 0,0164 %. L'ancien titre de cette section annonçait « 0,03 % » : c'était faux, le programme a toujours imprimé 0,0164 % (et l'ancien déroulé disait déjà 0,016 %). Le titre est corrigé. Puis 100 000 appels à `echantillonner` tirent `INSERT` 15 fois, pour une espérance de 16,4 : rare, mais pas impossible.

**`echantillonner(probabilites, rng)`** tire un token par la méthode de la fonction de répartition inverse.

- `u = rng.random()` : un nombre uniforme dans [0, 1[. `rng` est un `random.Random(42)` : la graine fixe rend la suite de tirages identique à chaque exécution.
- La boucle additionne les probabilités dans `cumul` et renvoie le premier indice tel que `u < cumul`. Avec `[0.999836, 0.000164]`, on ne tire `INSERT` que si `u >= 0.999836`, ce qui arrive avec la probabilité 0,000164.
- La dernière ligne protège contre l'arrondi : si les cumuls s'arrêtent à 0,9999999999999999 et que `u` les dépasse, on renvoie le dernier token de probabilité non nulle.

**`top_p(probabilites, p_top=0.9)`** coupe la queue, puis renormalise. Les probabilités d'entrée, passées par la softmax à T = 0,85, valent 0,5021, 0,2479, 0,1959, 0,0477 et 0,0065.

- `sorted(enumerate(probabilites), key=lambda item: item[1], reverse=True)` trie les couples `(indice, probabilité)` du plus grand au plus petit. L'ordre du vocabulaire ne compte plus, seule la masse compte.
- La boucle ajoute un token à `gardes`, ajoute sa probabilité à `cumule`, et s'arrête dès que `cumule >= p_top`. Ici : 0,5021, puis 0,7500, puis 0,9459. « bleue » et « xqz » ne sont pas gardés.
- `masse = sum(probabilites[i] for i in gardes)` vaut 0,9459, qui n'est pas 1.
- `sortie[i] = probabilites[i] / masse` : les trois gardés deviennent 0,5308, 0,2621 et 0,2071, et somment à 1. Un `assert` vérifie aussi que le rapport entre « innovante » et « fiable » n'a pas changé.

**`top_k(probabilites, k)`** trie les indices par probabilité décroissante, garde les `k` premiers et divise par leur masse. Avec `k = 2`, la masse vaut 0,7500 et les gardés deviennent 0,6695 et 0,3305. Sur la distribution pointue des logits `[5.0, 1.0, 0.5, 0.0, -1.0]` (pₘₐₓ = 0,9628), le top-p à 0,9 ne garde qu'un token, le top-k à 3 en garde trois.

**L'échantillonnage avec graine.** 10 000 tirages dans la distribution tronquée donnent des fréquences de 0,5281, 0,2677 et 0,2042, à moins de 0,02 des probabilités 0,5308, 0,2621 et 0,2071 ; « bleue » et « xqz » ne sortent jamais. Deux générateurs créés avec la même graine (7) produisent les mêmes 20 tokens : c'est ce qui rend un test d'agent reproductible.

**`jacobien_theorique(probabilites, temperature)`** calcule pᵢ(δᵢⱼ − pⱼ)/T. Sur p ≈ [0,5322 ; 0,3228 ; 0,1450] et T = 1 :

- Deux boucles, `i` puis `j`. `delta` vaut 1 seulement quand `i == j`.
- Sur la diagonale (i = j = 0) :

$$
0{,}532180 \times (1 - 0{,}532180) = 0{,}248964 .
$$

Hors diagonale (i = 0, j = 1) :

$$
0{,}532180 \times (0 - 0{,}322784) = -0{,}171779 .
$$

À T = 0,5, les mêmes cases valent 0,425187 et −0,353763.
- Les `assert` vérifient que chaque ligne et chaque colonne somment à 0 (démonstration, point 3).

**`jacobien_differences_finies(logits, temperature, eps)`** mesure la même dérivée sans la formule : pour chaque colonne `j`, on ajoute puis on retranche 10⁻⁶ au logit `j`, on recalcule les deux softmax, et `(p_plus[i] - p_moins[i]) / (2 * eps)` donne la pente. Elle retombe sur le tableau théorique à 10⁻⁶ près, à T = 1 comme à T = 0,5.

**`entropie_croisee(logits, cible, temperature)`** calcule

$$
L = \ln \sum_j e^{z_j/T} - z_c/T
$$

sans jamais former

$$
p_c
$$

`pic / temperature + math.log(sum(...))` est le « log-sum-exp » stable, avec le maximum retranché à l'intérieur du logarithme et rajouté à l'extérieur.

**`gradient_entropie_croisee(logits, cible, temperature)`** renvoie (pⱼ − yⱼ)/T. Sur `[1.0, 0.5, -0.3]` avec la bonne classe 0 : `[-0.46782, 0.322784, 0.145036]`. **`gradient_differences_finies`** le confirme à 10⁻⁶ près, à T = 1 et à T = 0,5, et les composantes somment à 0.

**La section 8 de `main`** rejoue la correction du point 4 : sur `[8.0, 0.0, 0.0]`, p₀ = 0,99933. Sûr et juste, le gradient vaut `[-0.00067, 0.00034, 0.00034]` ; sûr et faux, il vaut `[0.99933, -0.99966, 0.00034]`, alors que la dérivée de la softmax seule, p₁(1 − p₁), ne vaut que 0,00034.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(logits, temperature)`** — Cette fonction est l'arbitre qui transforme des notes brutes en parts d'un même gâteau : elle reçoit une liste de logits et une température, 1 par défaut, et lève `ValueError` si la température n'est pas strictement positive, puisque le cas T = 0 relève d'`argmax`. Elle retranche ensuite le plus grand logit à tous les autres, de sorte que le plus grand exposant vaut 0 et qu'aucune exponentielle ne déborde, divise chaque écart par T, prend les exponentielles et les divise par leur somme, qui vaut au moins 1. Elle renvoie une liste de probabilités positives qui somment à 1 : 0,643914, 0,236883, 0,087144 et 0,032059 pour les logits 2, 1, 0 et −1, et encore des nombres sages, 0,665241, 0,244728 et 0,090031, sur des logits de 1 000, 999 et 998 qui font déborder la version naïve.

**`argmax(logits)`** — Celle-ci joue le juge qui ne connaît pas la demi-mesure, la limite T → 0 écrite à part : elle reçoit une liste de logits, parcourt leurs indices avec `max` pour garder celui dont le score est le plus grand (le premier en cas d'égalité), puis renvoie un vecteur one-hot qui met 1,0 sur cet indice et 0,0 partout ailleurs, sans calculer la moindre exponentielle ni lever d'exception sur une liste non vide. Sur les outils « chercher », « calculer » et « repondre », de logits 3, 2,4 et 0,5, elle renvoie `[1.0, 0.0, 0.0]`, et pour l'agent SQL elle donne toute la masse à SELECT.

**`top_p(probabilites, p_top)`** — Cette fonction est un videur qui laisse entrer les clients du plus riche au plus modeste jusqu'à ce que la salle soit pleine aux neuf dixièmes : elle reçoit une distribution et un seuil, 0,9 par défaut, lève `ValueError` si ce seuil n'est pas dans ]0, 1], trie les couples (indice, probabilité) par probabilité décroissante et ajoute des tokens tant que leur masse cumulée reste sous le seuil, en s'arrêtant au premier qui l'atteint. Elle divise ensuite les gardés par leur masse, met les autres à 0 et renvoie le couple formé de la nouvelle distribution et de la liste des indices gardés : sur les cinq mots de l'exemple, elle garde « innovante », « fiable » et « rapide », qui deviennent 0,5308, 0,2621 et 0,2071, et sur la distribution pointue elle ne garde qu'un seul token.

**`echantillonner(probabilites, rng)`** — C'est la roue de loterie du programme : elle reçoit une distribution et un générateur `random.Random` déjà semé, tire un nombre u uniforme dans [0, 1[, puis avance le long des probabilités en les additionnant et renvoie le premier indice dont le cumul dépasse u, si bien que chaque token sort avec exactement sa probabilité. Si les arrondis flottants laissent le cumul final un peu sous 1 et que u le dépasse, elle renvoie le dernier indice de probabilité non nulle au lieu de ne rien rendre. Dans `main`, elle tire 100 000 fois entre SELECT et INSERT et fait sortir INSERT 15 fois, pour une espérance de 16,4, puis reproduit les mêmes 20 tokens avec deux générateurs de même graine.

**`jacobien_theorique(probabilites, temperature)`** — Cette fonction dresse, comme un cartographe, le tableau complet des pentes de la softmax : elle reçoit une distribution déjà calculée et la température, 1 par défaut, parcourt toutes les cases (i, j) avec deux boucles imbriquées et y écrit pᵢ(δᵢⱼ − pⱼ)/T, où δᵢⱼ vaut 1 sur la diagonale et 0 ailleurs. Elle renvoie cette matrice carrée sous forme de liste de lignes, sans lever d'exception ; sur p ≈ (0,5322 ; 0,3228 ; 0,1450) et T = 1, la première ligne commence par 0,248964 et −0,171779, et `main` vérifie que chaque ligne et chaque colonne somment à 0 et que le tableau rejoint la mesure par différences finies à 10⁻⁶ près.

**`entropie_croisee(logits, cible, temperature)`** — Celle-ci est le correcteur qui note la copie d'après la seule probabilité donnée à la bonne réponse : elle reçoit les logits, l'indice de la classe correcte et la température, 1 par défaut, puis calcule −ln p de la cible sans jamais former cette probabilité, par l'astuce du log-sum-exp, en retranchant le plus grand logit à l'intérieur du logarithme et en le rajoutant, divisé par T, à l'extérieur. Elle renvoie ce nombre, la perte L, qui vaut environ 0,6308 sur les logits 1, 0,5 et −0,3 avec la classe 0 ; dans `main`, elle n'est pas affichée, mais elle sert de fonction à dériver pour `gradient_differences_finies`.

**`gradient_entropie_croisee(logits, cible, temperature)`** — Cette fonction dit au modèle dans quelle direction pousser chaque logit, comme un entraîneur qui indique à chaque joueur de combien il doit reculer ou avancer : elle reçoit les logits, la classe correcte et la température, calcule la softmax, retranche 1 à la composante de la bonne classe et divise le tout par T, ce qui donne (pⱼ − yⱼ)/T. Elle renvoie cette liste, dont les composantes somment à 0 : `[-0.46782, 0.322784, 0.145036]` sur les logits 1, 0,5 et −0,3 avec la classe 0 ; sur un modèle sûr à 0,99933, le gradient est presque nul quand il a raison et vaut −0,99966 sur la bonne classe quand il se trompe.

**`gradient_differences_finies(fonction, logits, eps)`** — C'est l'arpenteur qui vérifie la carte sur le terrain : elle reçoit une fonction quelconque des logits, un point et un pas, 10⁻⁶ par défaut, puis, pour chaque direction j, copie deux fois les logits, ajoute le pas à l'une et le retranche à l'autre, et mesure la pente centrale (f(z + ε) − f(z − ε)) / 2ε. Elle renvoie la liste de ces pentes, une par logit, sans rien savoir de la formule théorique ; dans la section 8 de `main`, on lui passe une `lambda` qui appelle `entropie_croisee` pour la classe 0, et ses mesures rejoignent `gradient_entropie_croisee` à 10⁻⁶ près, à T = 1 comme à T = 0,5.

**`main()`** — C'est le chef d'orchestre des huit mouvements du chapitre : il compare d'abord la softmax stable et la version naïve sur les logits 2, 1, 0 et −1, puis montre l'invariance par translation, le plafond 709,78 du logarithme du plus grand float64, l'`OverflowError` sur 1 000, 999 et 998 et la `ZeroDivisionError` sur −1 000 et −1 001. Il fait ensuite varier la température de 0,2 à 10 sur le choix d'outil, calcule les 0,0164 % de l'agent SQL et ses 100 000 tirages, applique top-p et top-k, échantillonne 10 000 fois avec graine, confronte le jacobien théorique aux différences finies et termine par le gradient p − y du modèle sûr, juste ou faux. Chaque résultat est vérifié par un `assert`, et la ligne finale « OK — toutes les vérifications sont passées. » ne s'imprime que si tous tiennent.

```python
"""Chapitre 2 — softmax, température, top-k, top-p, échantillonnage, jacobien, gradient p − y. Bibliothèque standard seulement."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def softmax(logits, temperature=1.0):
    """p_i = exp((z_i − m) / T) / Σ_j exp((z_j − m) / T), avec m = max(z) : la forme stable."""
    if temperature <= 0.0:
        raise ValueError("T doit être > 0. Le cas T = 0 est le argmax, traité à part.")
    # Invariance par translation : retrancher la même constante à tous les logits ne change pas p.
    # On retranche le plus grand : le plus grand exposant vaut 0, donc exp() ne peut pas déborder,
    # et le dénominateur vaut au moins 1, donc on ne divise jamais par 0.
    pic = max(logits)
    exponentielles = [math.exp((z - pic) / temperature) for z in logits]
    total = sum(exponentielles)
    return [e / total for e in exponentielles]


def softmax_naive(logits, temperature=1.0):
    """La formule recopiée telle quelle, sans retrancher le max : juste en maths, fragile en flottants."""
    exponentielles = [math.exp(z / temperature) for z in logits]
    total = sum(exponentielles)
    return [e / total for e in exponentielles]


def argmax(logits):
    """Limite T → 0 (si le maximum est unique) : un vecteur one-hot sur le plus grand logit."""
    meilleur = max(range(len(logits)), key=lambda i: logits[i])
    return [1.0 if i == meilleur else 0.0 for i in range(len(logits))]


def top_k(probabilites, k):
    """Garde les k tokens les plus probables, met les autres à 0, puis renormalise."""
    if not 1 <= k <= len(probabilites):
        raise ValueError("il faut 1 <= k <= taille du vocabulaire")
    tries = sorted(range(len(probabilites)), key=lambda i: probabilites[i], reverse=True)
    gardes = tries[:k]
    masse = sum(probabilites[i] for i in gardes)
    sortie = [0.0] * len(probabilites)
    for i in gardes:
        sortie[i] = probabilites[i] / masse
    return sortie, gardes


def top_p(probabilites, p_top=0.9):
    """Nucleus sampling : plus petit ensemble dont la masse cumulée atteint p_top, puis on renormalise."""
    if not 0.0 < p_top <= 1.0:
        raise ValueError("il faut 0 < p_top <= 1")
    tries = sorted(enumerate(probabilites), key=lambda item: item[1], reverse=True)
    gardes = []
    cumule = 0.0
    for index, proba in tries:
        gardes.append(index)
        cumule += proba
        if cumule >= p_top:
            break
    masse = sum(probabilites[i] for i in gardes)
    sortie = [0.0] * len(probabilites)
    for i in gardes:
        sortie[i] = probabilites[i] / masse
    return sortie, gardes


def echantillonner(probabilites, rng):
    """Tire un indice : u uniforme dans [0, 1[, puis le premier indice dont le cumul dépasse u."""
    u = rng.random()
    cumul = 0.0
    for i, p in enumerate(probabilites):
        cumul += p
        if u < cumul:
            return i
    # Arrondi flottant : si les cumuls s'arrêtent à 0.9999999999999999 et que u les dépasse,
    # on rend le dernier token de probabilité non nulle.
    return max(i for i, p in enumerate(probabilites) if p > 0.0)


def entropie(probabilites):
    """H(p) = − Σ p_i ln p_i. Haute : l'agent hésite. Nulle : l'agent est certain."""
    total = 0.0
    for p in probabilites:
        if p > 0.0:
            total -= p * math.log(p)
    return total


def jacobien_theorique(probabilites, temperature=1.0):
    """∂p_i / ∂z_j = p_i (δ_ij − p_j) / T."""
    n = len(probabilites)
    J = []
    for i in range(n):
        ligne = []
        for j in range(n):
            delta = 1.0 if i == j else 0.0
            ligne.append(probabilites[i] * (delta - probabilites[j]) / temperature)
        J.append(ligne)
    return J


def jacobien_differences_finies(logits, temperature=1.0, eps=1e-6):
    """La même dérivée, mesurée par (p(z + ε) − p(z − ε)) / (2ε), pour contrôler la formule."""
    n = len(logits)
    colonnes = []
    for j in range(n):
        plus = logits[:]
        moins = logits[:]
        plus[j] += eps
        moins[j] -= eps
        p_plus = softmax(plus, temperature)
        p_moins = softmax(moins, temperature)
        colonnes.append([(p_plus[i] - p_moins[i]) / (2 * eps) for i in range(n)])
    # colonnes[j][i] vaut ∂p_i/∂z_j ; on transpose pour retrouver les lignes i.
    return [[colonnes[j][i] for j in range(n)] for i in range(n)]


def entropie_croisee(logits, cible, temperature=1.0):
    """L = − ln p_cible = ln Σ_j exp(z_j / T) − z_cible / T, calculée sans débordement (log-sum-exp)."""
    pic = max(logits)
    log_somme = pic / temperature + math.log(sum(math.exp((z - pic) / temperature) for z in logits))
    return log_somme - logits[cible] / temperature


def gradient_entropie_croisee(logits, cible, temperature=1.0):
    """∂L/∂z_j = (p_j − y_j) / T, où y est le vecteur one-hot de la bonne classe."""
    p = softmax(logits, temperature)
    return [(p[j] - (1.0 if j == cible else 0.0)) / temperature for j in range(len(logits))]


def gradient_differences_finies(fonction, logits, eps=1e-6):
    """Pente mesurée de fonction(z) dans chaque direction z_j."""
    pentes = []
    for j in range(len(logits)):
        plus = logits[:]
        moins = logits[:]
        plus[j] += eps
        moins[j] -= eps
        pentes.append((fonction(plus) - fonction(moins)) / (2 * eps))
    return pentes


def main():
    vocabulaire = ["SELECT", "INSERT", "DELETE", "WHERE"]

    print("=== 1. Softmax stable, et preuve que retrancher le max ne change rien ===")
    logits = [2.0, 1.0, 0.0, -1.0]
    p = softmax(logits)
    p_naif = softmax_naive(logits)       # sans retrancher le max : possible sur des logits modestes
    print("  logits :", logits)
    for mot, pi, qi in zip(vocabulaire, p, p_naif):
        print(f"    {mot:8s}  stable = {pi:.6f}   naïf = {qi:.6f}")
    assert abs(sum(p) - 1.0) < 1e-12
    assert all(abs(a - b) < 1e-12 for a, b in zip(p, p_naif))
    assert all(0.0 < pi < 1.0 for pi in p)
    assert [round(pi, 6) for pi in p] == [0.643914, 0.236883, 0.087144, 0.032059]

    print("\n=== 2. Invariance par translation, et pourquoi retrancher le max ===")
    p_decale = softmax([z + 5.0 for z in logits])
    assert all(abs(a - b) < 1e-12 for a, b in zip(p, p_decale))
    print("  z et z + 5 donnent la même distribution (écart < 1e-12)")
    print(f"  e^20 = {math.exp(20):.4e} : un float64 le stocke sans difficulté")
    print(f"  plus grand float64 = {sys.float_info.max:.4e} = e^{math.log(sys.float_info.max):.2f}")
    assert round(math.log(sys.float_info.max), 2) == 709.78
    try:
        math.exp(1000)
    except OverflowError:
        print("  math.exp(1000) -> OverflowError")
    else:
        raise AssertionError("exp(1000) aurait dû déborder")
    grands = [1000.0, 999.0, 998.0]
    try:
        softmax_naive(grands)
    except OverflowError:
        print("  softmax naïve sur [1000, 999, 998] -> OverflowError")
    else:
        raise AssertionError("la version naïve aurait dû déborder")
    stable = softmax(grands)
    print("  softmax stable sur [1000, 999, 998] :", [round(v, 6) for v in stable])
    assert [round(v, 6) for v in stable] == [0.665241, 0.244728, 0.090031]
    petits = [-1000.0, -1001.0]
    try:
        softmax_naive(petits)
    except ZeroDivisionError:
        print("  softmax naïve sur [-1000, -1001] -> ZeroDivisionError (les deux exp valent 0.0)")
    else:
        raise AssertionError("la version naïve aurait dû diviser par zéro")
    assert [round(v, 6) for v in softmax(petits)] == [0.731059, 0.268941]

    print("\n=== 3. Température sur un choix d'outil d'agent ===")
    # Chercher est le meilleur logit, mais calculer n'est pas loin.
    outils = ["chercher", "calculer", "repondre"]
    z_outils = [3.0, 2.4, 0.5]
    print(f"  {'T':>6}  {'chercher':>10}  {'calculer':>10}  {'repondre':>10}  {'entropie':>10}")
    confiances, entropies = [], []
    for T in (0.2, 0.7, 1.0, 2.0, 10.0):
        distribution = softmax(z_outils, temperature=T)
        print(
            f"  {T:6.1f}  {distribution[0]:10.4f}  {distribution[1]:10.4f}  "
            f"{distribution[2]:10.4f}  {entropie(distribution):10.4f}"
        )
        confiances.append(distribution[0])
        entropies.append(entropie(distribution))
    # Quand T monte, le meilleur logit perd de la masse et l'entropie monte (démonstration, point 5).
    assert all(a > b for a, b in zip(confiances, confiances[1:]))
    assert all(a < b for a, b in zip(entropies, entropies[1:]))
    glouton = argmax(z_outils)
    print("  T → 0 (argmax) :", dict(zip(outils, glouton)))
    assert glouton == [1.0, 0.0, 0.0]
    assert softmax(z_outils, temperature=0.01)[0] > 1.0 - 1e-12
    assert all(abs(pi - 1.0 / 3.0) < 1e-3 for pi in softmax(z_outils, temperature=1000.0))
    ex_aequo = softmax([3.0, 3.0, 1.0], temperature=0.01)
    print("  deux maxima égaux, T = 0.01 :", [round(v, 4) for v in ex_aequo])
    assert abs(ex_aequo[0] - 0.5) < 1e-12 and abs(ex_aequo[1] - 0.5) < 1e-12

    print("\n=== 4. Agent SQL : d'où vient le 0.016 % d'erreur ===")
    # On ne met pas les 100 000 autres tokens : deux logits suffisent à voir le mécanisme.
    z_select, z_insert = 14.2, 8.1
    p_sql = softmax([z_select, z_insert], temperature=0.7)
    print(f"  T = 0.7   P(SELECT) = {p_sql[0]:.6f}   P(INSERT) = {p_sql[1]:.6f}")
    print(f"  soit {p_sql[1] * 100:.4f} % de chances de commencer par le mauvais verbe")
    assert round(p_sql[1] * 100, 4) == 0.0164
    rng = random.Random(42)
    tirages = 100_000
    insert = sum(1 for _ in range(tirages) if echantillonner(p_sql, rng) == 1)
    print(f"  {tirages} tirages à T = 0.7 : INSERT sort {insert} fois (espérance {tirages * p_sql[1]:.1f})")
    assert 0 < insert < 40
    print("  T → 0     P(SELECT) = 1, P(INSERT) = 0")
    assert argmax([z_select, z_insert]) == [1.0, 0.0]

    print("\n=== 5. Top-k et top-p : on coupe la queue, puis on renormalise ===")
    tokens = ["innovante", "fiable", "rapide", "bleue", "xqz"]
    masse = softmax([2.2, 1.6, 1.4, 0.2, -1.5], temperature=0.85)
    tronquee, gardes = top_p(masse, p_top=0.9)
    print("  token        avant   après top-p 0.9")
    for mot, avant, apres in zip(tokens, masse, tronquee):
        print(f"    {mot:12s} {avant:.4f}  {apres:.4f}")
    print("  top-p = 0.9 garde :", [tokens[i] for i in gardes])
    assert gardes == [0, 1, 2] and abs(sum(tronquee) - 1.0) < 1e-12
    assert tronquee[tokens.index("bleue")] == 0.0 and tronquee[tokens.index("xqz")] == 0.0
    assert sum(masse[i] for i in gardes) >= 0.9 > masse[0] + masse[1]
    # Les rapports entre tokens gardés ne changent pas : on les divise tous par la même masse.
    assert abs(tronquee[0] / tronquee[1] - masse[0] / masse[1]) < 1e-12
    k2, gardes_k = top_k(masse, k=2)
    print("  top-k = 2 garde :", [tokens[i] for i in gardes_k], [round(k2[i], 4) for i in gardes_k])
    assert gardes_k == [0, 1] and abs(sum(k2) - 1.0) < 1e-12
    pointue = softmax([5.0, 1.0, 0.5, 0.0, -1.0])
    _, g_p = top_p(pointue, p_top=0.9)
    _, g_k = top_k(pointue, k=3)
    print(f"  distribution pointue (p_max = {pointue[0]:.4f}) : top-p garde {len(g_p)} token, top-k = 3 en garde {len(g_k)}")
    assert len(g_p) == 1 and len(g_k) == 3

    print("\n=== 6. Échantillonnage avec graine : les fréquences rejoignent les probabilités ===")
    rng = random.Random(42)
    n = 10_000
    comptes = [0] * len(tokens)
    for _ in range(n):
        comptes[echantillonner(tronquee, rng)] += 1
    for mot, c, q in zip(tokens, comptes, tronquee):
        print(f"    {mot:12s} tiré {c:5d} fois   fréquence {c / n:.4f}   probabilité {q:.4f}")
    assert comptes[3] == comptes[4] == 0            # coupés par top-p : jamais tirés
    assert sum(comptes) == n and all(abs(c / n - q) < 0.02 for c, q in zip(comptes, tronquee))
    r1, r2 = random.Random(7), random.Random(7)     # même graine, même suite de tokens
    assert [echantillonner(tronquee, r1) for _ in range(20)] == [echantillonner(tronquee, r2) for _ in range(20)]

    print("\n=== 7. Jacobien : la formule et la différence finie disent la même chose ===")
    z = [1.0, 0.5, -0.3]
    for T in (1.0, 0.5):
        p = softmax(z, temperature=T)
        theorique = jacobien_theorique(p, temperature=T)
        mesure = jacobien_differences_finies(z, temperature=T)
        assert all(abs(theorique[i][j] - mesure[i][j]) < 1e-6 for i in range(3) for j in range(3))
        assert abs(theorique[0][0] - p[0] * (1 - p[0]) / T) < 1e-12
        assert abs(theorique[0][1] + p[0] * p[1] / T) < 1e-12
        # Lignes et colonnes somment à 0 : translation de tous les logits, et Σ p = 1.
        assert all(abs(sum(ligne)) < 1e-12 for ligne in theorique)
        assert all(abs(sum(theorique[i][j] for i in range(3))) < 1e-12 for j in range(3))
        print(f"  T = {T} : p = {[round(v, 4) for v in p]}   ∂p_0/∂z_0 = {theorique[0][0]:.6f}"
              f"   ∂p_0/∂z_1 = {theorique[0][1]:.6f}   (différence finie à moins de 1e-6)")
    p1 = softmax(z)
    assert [round(v, 6) for v in jacobien_theorique(p1)[0][:2]] == [0.248964, -0.171779]

    print("\n=== 8. Entropie croisée : le gradient par rapport aux logits vaut p − y ===")
    g = gradient_entropie_croisee(z, cible=0)
    print(f"  z = {z}, bonne classe 0 : p − y = {[round(v, 4) for v in g]}")
    for T in (1.0, 0.5):
        g_T = gradient_entropie_croisee(z, cible=0, temperature=T)
        g_mesure = gradient_differences_finies(lambda v: entropie_croisee(v, 0, T), z)
        assert all(abs(a - b) < 1e-6 for a, b in zip(g_T, g_mesure))
    assert abs(sum(g)) < 1e-12 and [round(v, 6) for v in g] == [-0.46782, 0.322784, 0.145036]
    sur = [8.0, 0.0, 0.0]
    p_sur = softmax(sur)
    juste = gradient_entropie_croisee(sur, cible=0)
    faux = gradient_entropie_croisee(sur, cible=1)
    print(f"  modèle sûr (p_0 = {p_sur[0]:.5f}) et juste : gradient = {[round(v, 5) for v in juste]}")
    print(f"  modèle sûr et faux (bonne classe 1)    : gradient = {[round(v, 5) for v in faux]}")
    print(f"  dérivée de la softmax seule, p_1 (1 − p_1) = {p_sur[1] * (1 - p_sur[1]):.5f}")
    assert max(abs(v) for v in juste) < 1e-3       # sûr ET juste : presque rien à apprendre
    assert faux[1] < -0.99                         # sûr mais faux : gradient fort, il apprend
    assert p_sur[1] * (1 - p_sur[1]) < 1e-3        # la softmax seule, elle, saturerait

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
    SELECT    stable = 0.643914   naïf = 0.643914
…
  e^20 = 4.8517e+08 : un float64 le stocke sans difficulté
  plus grand float64 = 1.7977e+308 = e^709.78
  softmax naïve sur [1000, 999, 998] -> OverflowError
  softmax stable sur [1000, 999, 998] : [0.665241, 0.244728, 0.090031]
…
     0.2      0.9526      0.0474      0.0000      0.1909
    10.0      0.3676      0.3462      0.2863      1.0932
…
  soit 0.0164 % de chances de commencer par le mauvais verbe
  100000 tirages à T = 0.7 : INSERT sort 15 fois (espérance 16.4)
…
  top-p = 0.9 garde : ['innovante', 'fiable', 'rapide']
  top-k = 2 garde : ['innovante', 'fiable'] [0.6695, 0.3305]
…
  modèle sûr (p_0 = 0.99933) et juste : gradient = [-0.00067, 0.00034, 0.00034]
  modèle sûr et faux (bonne classe 1)    : gradient = [0.99933, -0.99966, 0.00034]
OK — toutes les vérifications sont passées.
```

À retenir pour un agent en production : la température n'est pas une métaphore de créativité. C'est le diviseur des logits, juste avant l'exponentielle. `T = 0` n'est pas une softmax, c'est un `argmax`. Le top-p jette des tokens puis divise par la masse restante, sinon les probabilités ne somment plus à 1 et l'échantillonnage est faux. Et retrancher le maximum ne sert pas à stocker e²⁰ : cela sert à ne jamais calculer e¹⁰⁰⁰, ni diviser 0 par 0.

## Squelette algorithmique

Le programme de ce fichier suit le chemin d'un token : des logits bruts à une distribution de probabilité stable, puis au tirage du prochain token, avec ou sans troncature. L'algorithme ci-dessous en garde la logique, sans les vérifications de la démonstration.

```text
ALGORITHME ChoisirProchainToken
ENTRÉES : logits z₁ … z_|V|, température T, mode ∈ {argmax, top-k, top-p, plein}, k, p_top, générateur aléatoire
SORTIE  : l'indice du token choisi

  SI T = 0 ALORS RETOURNER argmaxᵢ zᵢ                  (ce n'est pas une softmax)
  m ← max(z)                                           (stabilité numérique)
  POUR i DE 1 À |V| FAIRE  eᵢ ← exp((zᵢ − m) / T)  FIN POUR
  S ← Σ eᵢ
  POUR i DE 1 À |V| FAIRE  pᵢ ← eᵢ / S  FIN POUR
  SI mode = top-k ALORS garder les k plus grands pᵢ, mettre les autres à 0, renormaliser
  SI mode = top-p ALORS trier par pᵢ décroissant, garder le plus petit préfixe de masse ≥ p_top, renormaliser
  u ← nombre uniforme dans [0 ; 1[
  cumul ← 0
  POUR i dans l'ordre des tokens FAIRE
      cumul ← cumul + pᵢ
      SI u < cumul ALORS RETOURNER i
  FIN POUR
```

**Complexité.** Le calcul de la softmax est linéaire : O(|V|) exponentielles et une somme, où |V| est la taille du vocabulaire (des dizaines de milliers de tokens). Le top-k coûte O(|V| log |V|) avec un tri complet, ou O(|V| log k) avec un tas ; le top-p demande un tri, donc O(|V| log |V|). Le tirage final par cumul est O(|V|). La mémoire est O(|V|) pour le vecteur de probabilités. Le jacobien théorique, calculé dans la démonstration, est une matrice |V| × |V| : O(|V|²), ce qui explique qu'on ne le forme jamais en entier dans un vrai modèle.

**Du squelette au code.** La première ligne correspond à `argmax`, le bloc « m, eᵢ, S, pᵢ » à `softmax` (la version `softmax_naive` omet la soustraction de m et déborde, ce que le programme montre), les deux troncatures à `top_k` et `top_p`, et la boucle de tirage à `echantillonner`. `entropie`, `jacobien_theorique` et `entropie_croisee` ne font pas partie du choix du token : ils mesurent la distribution obtenue, et le programme les compare à des différences finies pour vérifier les formules.

## Cas d'usage réels aux Émirats

Les logits, seuils et volumes ci-dessous sont illustratifs. Les réglages de décodage supposent un modèle dont on contrôle les paramètres (modèle ouvert hébergé en interne, ou API qui les accepte) ; sur les modèles Claude actuels, ces paramètres ne sont pas acceptés, et la fiabilité vient des schémas et des validations.

### Banque — des appels d'outils et du JSON sans token parasite

L'agent de pré-instruction de crédit d'une banque de détail de Dubaï renvoie sa pré-décision sous forme d'un document JSON d'environ 300 tokens (identifiant du dossier, mensualité, ratio d'endettement, recommandation), que le système central de la banque refuse s'il est mal formé. La softmax explique le risque : à T = 0,7, un token dont le logit devance le suivant de 6,1 points laisse encore 0,0164 % de chances au mauvais token, et si chacun des 300 tokens avait une telle marge, la probabilité d'au moins un token faux atteindrait 1 − (1 − 0,000164)³⁰⁰ ≈ 4,8 %, soit une pré-décision sur vingt. La banque décode donc les appels d'outils et le JSON en glouton (T → 0) sur ses modèles hébergés en interne ; sur un modèle d'API qui n'accepte pas la température, elle s'appuie sur des schémas d'outils stricts et des sorties structurées (étape 8), plus un validateur JSON avant toute écriture. Sans ces protections, une partie des pré-décisions serait rejetée par le système central, ou pire acceptée avec un champ corrompu, par exemple un ratio d'endettement altéré qui ferait passer un dossier au-dessus du plafond de 50 % de la CBUAE. La banque doit pouvoir rejouer et justifier chaque pré-décision devant ses équipes de conformité, ce qui exclut tout tirage aléatoire dans les champs chiffrés. On suit le taux de documents rejetés par le validateur et le nombre de relances automatiques par dossier.

### Immobilier — des annonces bilingues variées, mais des chiffres exacts

Un promoteur de Dubaï et d'Abu Dhabi fait rédiger par un agent, en anglais et en arabe, les descriptions des 400 lots d'une tour vendue sur plan, qui ne doivent pas toutes se ressembler. La partie rédactionnelle est échantillonnée à T = 0,85 avec un top-p de 0,9 : sur la distribution du code, le noyau garde trois adjectifs (masse 0,9459) et les renormalise en 0,5308, 0,2621 et 0,2071, si bien que la queue absurde (« bleue », « xqz ») n'est jamais tirée alors que le texte varie d'un lot à l'autre. Les données réglementées de l'annonce (prix en AED, surface en sqft, date de livraison, références d'enregistrement du projet auprès du DLD) ne sont jamais générées : le code les insère depuis la base du projet, parce qu'un token tiré au hasard peut changer un chiffre. Sans cette séparation, une surface de 1 450 sqft peut devenir 1 540 sqft dans une annonce sur plusieurs centaines, ce qui expose le promoteur à une réclamation de l'acheteur et à une remarque du régulateur. Le même principe vaut pour l'arabe, où les nombres et les noms propres doivent être recopiés, pas reformulés. On suit le taux d'annonces dont un chiffre diffère de la base (objectif : zéro) et la part de phrases distinctes sur l'ensemble des 400 annonces.

### Crypto — l'entropie comme signal d'incertitude

Une plateforme d'actifs virtuels agréée par la VARA classe les événements de liquidité avec un petit modèle hébergé en interne, dont elle lit les logits, entre trois actions : « alerter », « surveiller » et « ignorer ». Pour un événement ambigu, les logits [3,0 ; 2,4 ; 0,5] donnent à T = 1 les probabilités [0,6132 ; 0,3365 ; 0,0503] et une entropie de 0,8169, soit 74 % du maximum ln 3 = 1,0986 ; pour un événement net, les logits [4,5 ; 1,0 ; 0,2] donnent [0,9581 ; 0,0289 ; 0,0130] et une entropie normalisée de 0,18. La règle retenue est simple : l'action est toujours choisie en glouton, jamais tirée, et toute entropie normalisée supérieure à 0,5 envoie l'événement à un analyste, quelle que soit la classe en tête. Un tirage à T = 1 choisirait « surveiller » pour l'événement ambigu dans 34 % des cas, et l'astreinte verrait des décisions différentes pour des situations identiques. Sans le signal d'entropie, l'agent agirait avec la même assurance apparente sur les cas nets et sur les cas douteux, ce que la politique de conformité de la plateforme, qui exige une revue humaine des cas ambigus, ne permet pas. On suit la part d'événements escaladés et la proportion de vrais incidents parmi les événements escaladés et non escaladés.

### Assurance — calibrer les probabilités par la température

Un assureur auto et santé trie les déclarations de sinistre avec un classifieur à trois classes, « recevable », « à vérifier » et « fraude probable », et approuve automatiquement les dossiers dont la probabilité « recevable » dépasse 0,9. L'équipe de données constate sur l'historique que le modèle est trop sûr de lui : les dossiers qu'il note autour de 0,93 ne sont recevables qu'environ trois fois sur quatre (chiffre illustratif). Elle applique la calibration par la température (« temperature scaling ») : diviser tous les logits par un T > 1 choisi pour minimiser l'entropie croisée sur un jeu de validation, grâce au gradient du point 4. Avec les logits [4,0 ; 1,0 ; 0,0], la probabilité « recevable » vaut 0,9362 à T = 1, donc approbation automatique, mais 0,7361 à la température calibrée T = 2, donc passage chez un gestionnaire. Diviser par un T > 0 ne change pas l'ordre des logits, donc ni l'argmax ni l'exactitude du classifieur : seule la confiance affichée change, et le seuil de 0,9 retrouve un sens. L'assurance étant supervisée par la CBUAE, le seuil et la méthode de calibration sont documentés et revus à chaque nouvelle version du modèle. On suit chaque mois l'erreur de calibration et le taux de fraude parmi les dossiers approuvés automatiquement.

### RH — affiner un routeur de demandes avec l'entropie croisée

Un cabinet RH présent dans plusieurs émirats affine un petit modèle ouvert, hébergé chez lui, pour orienter les demandes des salariés, en arabe ou en anglais, vers quatre outils : visas, salaires versés par le WPS, fin de service, autres. Après une mise à jour, le routeur envoie des questions de fin de service vers l'outil WPS ; l'analyse montre que quelques centaines d'exemples d'entraînement avaient leurs étiquettes inversées entre ces deux classes. Le gradient p − y explique l'incident : sur un exemple que le modèle classait avec assurance (p = 0,99933), une étiquette fausse produit un gradient de l'ordre de 1, comme [0,99933 ; −0,99966 ; 0,00034], alors qu'un exemple juste et sûr n'apporte que 0,00067 : les erreurs d'étiquetage dominent la mise à jour. Le cabinet audite désormais, avant chaque entraînement, les exemples dont la perte

$$
L = -\ln p_c
$$

est la plus élevée, ceux où le modèle est sûr et en désaccord avec l'étiquette (L = −ln 0,000335 ≈ 8,0). Sans cet audit, des réponses sur la fin de service, calculée selon le décret-loi fédéral 33/2021, seraient produites par le mauvais outil, avec des montants faux. On suit l'exactitude du routage par classe sur un jeu de test revu par un expert RH, et le nombre d'étiquettes corrigées à chaque cycle.

### BTP — top-p plutôt que top-k pour les comptes rendus de chantier

Un groupe de construction qui mène de grands chantiers à Dubaï fait rédiger par un agent les comptes rendus journaliers de chantier, à partir des relevés structurés de la journée (effectifs, livraisons de béton, incidents). Ces documents peuvent servir de preuve contractuelle lors d'une réclamation pour retard : la prose doit rester fidèle, et les quantités (mètres cubes, effectifs, montants HT et TVA de 5 %) sont insérées par le code, jamais générées. Pour la prose, l'équipe a comparé les deux troncatures : sur une distribution pointue, où le modèle est sûr du terme technique (pₘₐₓ = 0,9628), le top-k à 3 garde trois candidats et laisse une chance à des synonymes approximatifs, alors que le top-p à 0,9 n'en garde qu'un. Elle retient donc un top-p de 0,9 : pas de hasard là où le vocabulaire du métier est fixé, de la variété là où plusieurs formulations se valent. Sans ce choix, un terme comme « dalle post-tendue » peut devenir une approximation dans un compte rendu, et un sous-traitant lire autre chose que ce qui a été constaté. On suit le taux de comptes rendus corrigés par l'ingénieur de chantier avant envoi.

## Pièges et limites

- **Confondre « T = 0 » et « déterministe ».** Même en glouton, un service de modèle peut produire des sorties légèrement différentes d'un appel à l'autre (calculs parallèles en virgule flottante), et beaucoup d'API ne laissent pas régler T. La reproductibilité se teste, elle ne se décrète pas.
- **Oublier de renormaliser après le top-k ou le top-p.** Les poids ne somment plus à 1 et l'échantillonneur fausse les fréquences (exercice 3).
- **Croire que retrancher le maximum règle tout.** Un logit `inf` ou `nan` (bug en amont) donne `inf - inf = nan` ; on vérifie `math.isfinite` sur les entrées.
- **Lire pₘₐₓ comme une probabilité d'avoir raison.** La confiance d'une softmax n'est pas calibrée par défaut : on la calibre (cas Assurance) avant de lui appliquer un seuil.
- **Oublier le facteur 1/T.** Entraîner ou calibrer à T ≠ 1 multiplie le gradient par 1/T ; un pas d'apprentissage réglé à T = 1 devient trop grand à T = 0,5.

### Exercice feuille blanche

1. Sans regarder le code, écrire `softmax(logits, temperature)` sous sa forme stable, puis vérifier qu'elle renvoie `[0.731059, 0.268941]` sur `[-1000.0, -1001.0]`, là où la version naïve lève `ZeroDivisionError`.
2. Prédire, puis vérifier : avec les logits [2 ; 0], que vaut la probabilité du premier token à T = 0,5 et à T = 2 ? (Réponses : 1/(1 + e⁻⁴) = 0,9820 et 1/(1 + e⁻¹) = 0,7311.)
3. Trouver le bug : une variante de `top_p` renvoie `probabilites[i]` sans diviser par `masse`. Avec `echantillonner`, quelle est la fréquence de « rapide » sur la distribution du code ? (Réponse : 0,25 au lieu de 0,2071. Les tirages u ≥ 0,9459 ne tombent sur aucun cumul et la garde finale renvoie « rapide », dernier token non nul : 0,1959 + 0,0541 = 0,25.)

## Pour aller plus loin

Le **min-p** garde les tokens dont la probabilité dépasse une fraction de pₘₐₓ, ce qui s'adapte aussi à la forme de la distribution. Le **décodage contraint** (une grammaire qui interdit les tokens rendant le JSON invalide) remplace la température nulle pour les sorties structurées. La calibration par la température est décrite par Guo et al. (2017), « On Calibration of Modern Neural Networks ». Le lissage des étiquettes (« label smoothing ») remplace y par un vecteur moins tranché pour limiter l'excès de confiance.

> Suite : [Tokenisation BPE](<02b-Tokenisation-BPE.md>) — étape 2 bis.
