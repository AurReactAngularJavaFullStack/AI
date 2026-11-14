# Étape 62 — Évaluation — Perplexité (et lien avec la confiance)

> Étape 62 du parcours · Prérequis : [Mean Average Precision](<61-Evaluation-Formule-MAP.md>) · Suite : [Answer Correctness](<63-Evaluation-Formule-Answer-Correctness.md>)

**Dossier :** 10-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  
**Nom du fichier :** 62-Evaluation-Formule-Perplexite.md

## Définition

La perplexité d'une séquence de N tokens mesure à quel point un modèle de langage est « surpris » par les tokens qui sont effectivement là. On prend, pour chaque token, la probabilité que le modèle lui donnait sachant les tokens précédents ; on fait la moyenne de leurs logarithmes naturels changés de signe ; la perplexité est l'exponentielle de cette moyenne. C'est l'inverse de la moyenne géométrique des probabilités : une perplexité de 4 veut dire que le modèle était, en moyenne, aussi hésitant que s'il avait choisi au hasard entre 4 tokens également probables. L'étape 52 l'a présentée comme mesure d'un modèle sur un texte de référence. Ici, on l'applique à la sortie de l'agent : c'est un **signal de confiance** du modèle sur sa propre réponse. Ce signal est faible : il dit si le modèle était sûr de lui, pas s'il avait raison.

## Rôle dans un agent

Hors ligne, la perplexité sur un texte de référence du métier compare deux modèles ou deux versions affinées (étape 73), à condition qu'ils partagent le même tokenizer. En ligne, elle intervient à l'étape « observer » de la boucle : une fois la réponse générée, un garde-fou ou un juge calcule la perplexité de cette réponse à partir des log-probabilités des tokens, si le fournisseur les expose, et l'utilise comme **un** signal parmi d'autres pour décider d'une revue humaine, à côté de la fidélité (étape 54) et de la justesse (étape 63). Elle sert aussi à surveiller les entrées : la perplexité des messages entrants sous un modèle de référence monte quand un nouveau type de demande apparaît. Selon le fournisseur et le modèle, les log-probabilités des tokens générés ne sont pas toujours disponibles ; dans ce cas, on ne peut pas calculer ce signal et l'on s'appuie sur d'autres (cohérence entre essais, juge).

## Équation complète

Probabilité du i-ème token sachant ceux qui le précèdent :

$$
p_i = p(w_i \mid w_{<i})
$$

Perplexité, forme logarithmique (logarithme naturel, **moyenne** et non somme) :

$$
\text{PPL} = \exp\!\left( -\frac{1}{N} \sum_{i=1}^{N} \ln p_i \right)
$$

Forme produit, équivalente :

$$
\text{PPL} = \left( \prod_{i=1}^{N} p_i \right)^{-1/N}
$$

Log-vraisemblance négative moyenne, en nats, et lien avec la perplexité :

$$
H = -\frac{1}{N} \sum_{i=1}^{N} \ln p_i, \qquad \text{PPL} = e^{H} = 2^{H / \ln 2}
$$

Perplexité d'un corpus de séquences s, chacune de longueur N_s (rapport des sommes) :

$$
\text{PPL}_{\text{corpus}} = \exp\!\left( \frac{\sum_{s} \sum_{i=1}^{N_s} -\ln p_{s,i}}{\sum_{s} N_s} \right)
$$

Bits par caractère, indépendants du tokenizer, pour un texte de C caractères :

$$
\text{BPC} = \frac{\sum_{i=1}^{N} -\ln p_i}{C \,\ln 2}
$$

Perplexité attendue d'un texte tiré à la température T sous le modèle p :

$$
q_T(x) = \frac{p(x)^{1/T}}{\sum_{y} p(y)^{1/T}}, \qquad \text{PPL}_T = \exp\!\Big( \mathbb{E}_{x \sim q_T}\big[ -\ln p(x) \big] \Big)
$$

## Décryptage des symboles

$$
N
$$

**Sens :** nombre de tokens de la séquence évaluée (la réponse seule, sans le prompt) · **Type / plage :** entier ≥ 1 ; pour N = 0 la perplexité n'est pas définie · **Variable Python :** `len(probas)`

$$
w_i,\; w_{<i}
$$

**Sens :** le i-ème token, et les tokens qui le précèdent (le contexte) · **Type / plage :** tokens du vocabulaire du modèle · **Variable Python :** implicites, le modèle a déjà fait le calcul

$$
p_i
$$

**Sens :** probabilité que le modèle donnait au token réellement présent · **Type / plage :** réel dans ]0, 1] ; 0 n'arrive pas avec une softmax, et un 0 trahit une liste tronquée · **Variable Python :** `probas[i]`, ou `math.exp(logprobs[i])`

$$
\ln p_i
$$

**Sens :** log-probabilité naturelle, celle que renvoient les API qui exposent les logprobs · **Type / plage :** réel ≤ 0 · **Variable Python :** `logprobs[i]`

$$
H
$$

**Sens :** log-vraisemblance négative moyenne par token, en nats (entropie croisée empirique) · **Type / plage :** réel ≥ 0 · **Variable Python :** `-sum(logprobs) / len(logprobs)`

$$
\text{PPL}
$$

**Sens :** perplexité, nombre effectif de choix équiprobables par token · **Type / plage :** réel ≥ 1, sans borne supérieure · **Variable Python :** `perplexite(probas)` ou `perplexite_logprobs(logprobs)`

$$
C
$$

**Sens :** nombre de caractères du texte, pour la normalisation par caractère · **Type / plage :** entier ≥ 1 · **Variable Python :** `n_caracteres`

$$
T,\; q_T
$$

**Sens :** température de décodage, et distribution dans laquelle on tire réellement les tokens à cette température · **Type / plage :** T > 0 ; T → 0 correspond au décodage glouton · **Variable Python :** `temperature`, `q`

## Démonstration

### 1. La forme logarithmique et la forme produit sont la même formule

Parce que la somme des logarithmes est le logarithme du produit, puis parce que exp(a ln x) = xᵃ :

$$
\exp\!\left( -\frac{1}{N} \sum_{i=1}^{N} \ln p_i \right)
= \exp\!\left( -\frac{1}{N} \ln \prod_{i=1}^{N} p_i \right)
= \left( \prod_{i=1}^{N} p_i \right)^{-1/N}
$$

Avec [0,5 ; 0,25 ; 0,125], le produit vaut 1/64 et la perplexité vaut 64^(1/3) = 4. La perplexité est donc l'inverse de la moyenne géométrique des probabilités.

### 2. Les deux erreurs de l'ancienne version : la somme et la base

Prendre l'exponentielle de la **somme** au lieu de la moyenne donne

$$
\exp\!\Big( -\sum_{i} \ln p_i \Big) = \text{PPL}^{N}
$$

soit 4³ = 64 sur l'exemple. Ce nombre grandit avec la longueur : une réponse deux fois plus longue paraîtrait beaucoup plus « surprenante » sans l'être. Mélanger les bases est l'autre erreur : la moyenne des log₁₀ vaut −0,60206 et e⁰,⁶⁰²⁰⁶ ≈ 1,8259, au lieu de 4. La règle : la base de l'exponentielle est celle du logarithme, ce qui donne la même perplexité dans toutes les bases, e^(H en nats) = 2^(H en bits). En bits, l'exemple donne 1, 2 et 3 bits, une moyenne de 2, et 2² = 4.

### 3. PPL ≥ 1, et pas de borne supérieure

Chaque pᵢ vaut au plus 1, donc ln pᵢ ≤ 0, donc H ≥ 0 et PPL = eᴴ ≥ e⁰ = 1. L'égalité PPL = 1 a lieu si et seulement si chaque ln pᵢ vaut 0, c'est-à-dire si le modèle donnait une probabilité 1 à chaque token. Il n'y a pas de borne supérieure : quand un pᵢ tend vers 0, ln pᵢ tend vers −∞ et la perplexité explose. En particulier, l'affirmation « PPL ≤ |V| », où |V| est la taille du vocabulaire, est fausse en général : un token à 0,01 dans un vocabulaire de 4 tokens donne une perplexité de 100. L'étape 52 démontre ce qui est vrai : l'exponentielle de l'entropie propre d'une distribution est au plus |V|, et un modèle uniforme a une perplexité exactement égale à |V|.

### 4. Un seul token improbable tire toute la perplexité

La fonction ln est concave. Par l'inégalité de Jensen, la moyenne des logarithmes est au plus le logarithme de la moyenne :

$$
\frac{1}{N} \sum_{i=1}^{N} \ln p_i \;\le\; \ln\!\left( \frac{1}{N} \sum_{i=1}^{N} p_i \right)
\qquad\Longrightarrow\qquad
\text{PPL} \;\ge\; \frac{1}{\bar p}
$$

où p̄ est la moyenne arithmétique des probabilités. C'est l'inégalité entre moyennes géométrique et arithmétique. Sur l'exemple, 1/p̄ = 1/0,29167 ≈ 3,43 ≤ 4. La conséquence pratique : la perplexité est dominée par les tokens les moins probables. Dix tokens à 0,9 donnent 1/0,9 ≈ 1,1111 ; remplacer un seul d'entre eux par un token à 0,001 donne 2,1937. Ce token unique pèse ln(0,001) ≈ −6,91, autant qu'environ 66 tokens à 0,9 (chacun pèse ln 0,9 ≈ −0,105, et 6,91 / 0,105 ≈ 65,6).

### 5. Pourquoi le code passe par les logarithmes

La forme produit est juste en théorie mais fausse sur machine. Avec 1 100 tokens à 0,5, le produit vaut 2⁻¹¹⁰⁰, plus petit que le plus petit flottant positif, 2⁻¹⁰⁷⁴ ≈ 4,9 × 10⁻³²⁴ : Python l'arrondit à 0, et 0 élevé à une puissance négative lève `ZeroDivisionError`. La somme des logarithmes vaut −1 100 ln 2 ≈ −762,5, un nombre ordinaire, et la perplexité se calcule sans peine : 2.

### 6. Perplexité d'un corpus : rapport des sommes, pas moyenne des perplexités

Prenons une séquence A de 2 tokens à −0,1 nat chacun et une séquence B de 8 tokens à −2 nats chacun. La perplexité du corpus divise la NLL totale, 0,2 + 16 = 16,2, par le nombre total de tokens, 10 :

$$
\text{PPL}_{\text{corpus}} = e^{16{,}2/10} = e^{1{,}62} \approx 5{,}0531
$$

La moyenne des deux perplexités vaut (e⁰,¹ + e²)/2 = (1,10517 + 7,38906)/2 ≈ 4,2471. Les deux nombres diffèrent parce que, dans le premier, chaque **token** pèse autant, alors que dans le second chaque **séquence** pèse autant, et que la courte séquence facile tire la moyenne vers le bas. C'est le même piège que la moyenne des ratios et le ratio des sommes de l'étape 54 : on choisit une convention et on la publie avec le chiffre.

### 7. Changer de tokenizer change la perplexité, pas la probabilité du texte

La probabilité du texte entier vaut ∏ pᵢ = e^(−NLL totale). Si deux modèles donnent au même texte la même probabilité, ils ont la même NLL totale, quelle que soit la façon dont ils le découpent. Mais la perplexité divise par N, le nombre de tokens, qui dépend du tokenizer. Avec une NLL totale de 6 nats sur un texte de 32 caractères, un tokenizer qui coupe en 4 tokens donne e^(6/4) = e^1,5 ≈ 4,4817, un autre qui coupe en 6 tokens donne e^(6/6) = e ≈ 2,7183. Le texte est aussi probable dans les deux cas. Les bits par caractère, 6 / (32 × ln 2) ≈ 0,2705, sont identiques : c'est la mesure à utiliser pour comparer deux modèles qui ne partagent pas le même tokenizer.

### 8. La perplexité de la sortie dépend de la température

À la température T, l'agent tire chaque token dans q_T, proportionnelle à p^(1/T). La NLL moyenne de ce qu'il produit, mesurée sous le modèle p, est l'espérance de −ln p(x) quand x suit q_T. Avec la même distribution p = [0,7 ; 0,2 ; 0,1] à chaque pas :

- en glouton (T → 0), le token choisi est toujours le plus probable : PPL = 1/0,7 ≈ 1,4286 ;
- à T = 1, q = p et l'espérance est l'entropie de p : 0,7 × 0,3567 + 0,2 × 1,6094 + 0,1 × 2,3026 ≈ 0,8018, d'où PPL ≈ 2,2296 ;
- à T = 2, q ∝ [√0,7 ; √0,2 ; √0,1] = [0,5229 ; 0,2795 ; 0,1976] après normalisation, et PPL ≈ 2,9784.

La croissance avec T est générale. Posons f(x) = −ln p(x) et β = 1/T, de sorte que q_T est proportionnelle à e^(−βf). La dérivée de l'espérance de f par rapport à β vaut moins la variance de f sous q_T, donc elle est négative ou nulle : l'espérance décroît avec β, c'est-à-dire qu'elle **croît** avec T. Le même modèle, aussi compétent, produit des réponses deux fois plus « perplexes » quand on monte la température. Un seuil calibré à une température ne vaut donc pas pour une autre.

### 9. Une perplexité basse ne veut pas dire une réponse vraie

L'ancienne version écrivait « plus la perplexité est basse, plus le modèle est confiant et cohérent » et « perplexité élevée → réponses moins fiables ». C'est exagéré, et le contre-exemple est simple. Une réponse fausse mais sûre d'elle (« le plafond d'endettement est de 60 % »), avec des probabilités [0,97 ; 0,95 ; 0,96 ; 0,98], a une perplexité de 1,0363. Une réponse juste qui contient un nom translittéré rare, avec [0,97 ; 0,95 ; 0,30 ; 0,98], a une perplexité de 1,3861, plus haute. La perplexité mesure la surprise du modèle devant ses propres tokens, pas leur accord avec les faits : c'est le rôle de la fidélité (étape 54) et de la justesse (étape 63). Enfin, une boucle de répétition, où le modèle recopie la même phrase, a une perplexité très **basse**, parce que chaque répétition devient plus prévisible : pour détecter les sorties dégénérées, il faut surveiller les deux extrémités, ou ajouter un détecteur de répétitions.

### 10. Exemple fait à la main : un seuil calibré, puis une décision

On calibre le seuil sur 20 réponses validées par un humain, produites avec le même modèle et la même température. Leurs perplexités, triées, vont de 1,18 à 1,95 ; le percentile 95 au rang le plus proche est la valeur de rang ⌈0,95 × 20⌉ = 19, soit 1,51. La réponse A a pour log-probabilités [−0,2 ; −0,3 ; −0,25 ; −0,1] : la NLL moyenne vaut 0,85/4 = 0,2125 et la perplexité e⁰,²¹²⁵ ≈ 1,2368, sous le seuil, donc pas de revue. La réponse B a [−0,2 ; −1,9 ; −0,8 ; −0,6] : la NLL moyenne vaut 3,5/4 = 0,875 et la perplexité e⁰,⁸⁷⁵ ≈ 2,3989, au-dessus du seuil : revue humaine.

## Effets et comportement

- **Une perplexité haute est une raison de regarder, pas une preuve d'erreur.** Elle monte avec un vocabulaire rare (noms propres, translittérations de l'arabe, références de dossiers), une température élevée, une entrée bruitée (OCR) ou une question hors du domaine.
- **Une perplexité basse peut cacher trois situations différentes.** Une réponse juste et banale, une hallucination sûre d'elle, ou une boucle de répétition.
- **La moyenne par token rend la mesure indépendante de la longueur**, mais une réponse de 5 tokens donne une estimation très bruitée : un seul token rare la fait doubler.
- **La perplexité ne se compare qu'à conditions égales.** Même modèle et même version, même tokenizer, même température, et les tokens de la réponse seulement, sans ceux du prompt.

## Du symbole au code Python

$$
p_i,\; \ln p_i
$$

**Variable ou fonction :** `probas`, `logprobs`

$$
\exp\!\left(-\frac{1}{N}\sum_i \ln p_i\right)
$$

**Variable ou fonction :** `perplexite(probas)`, `perplexite_logprobs(logprobs)`

$$
\left(\prod_i p_i\right)^{-1/N}
$$

**Variable ou fonction :** `perplexite_produit(probas)`, gardée pour montrer le sous-dépassement

$$
\text{PPL}_{\text{corpus}}
$$

**Variable ou fonction :** `perplexite_corpus(sequences)`

$$
\text{BPC}
$$

**Variable ou fonction :** `bits_par_caractere(nll_totale_nats, n_caracteres)`

$$
\text{PPL}_T
$$

**Variable ou fonction :** `ppl_attendue_temperature(p, temperature)`

$$
\tau
$$

**Variable ou fonction :** `seuil = p95(reference)`, le seuil de revue humaine

### Déroulé, ligne par ligne

**`verifier_probas(probas)`** lève `ValueError` dès qu'une probabilité sort de ]0, 1]. Un 0 n'est pas « une perplexité infinie » à renvoyer en silence : avec une softmax, aucune probabilité n'est nulle, donc un 0 signale une liste de logprobs tronquée ou mal convertie.

**`perplexite(probas)`** renvoie `None` pour une liste vide, la convention du parcours pour une métrique sans dénominateur (l'ancienne version renvoyait l'infini). Puis `math.exp(-sum(math.log(p) for p in probas) / len(probas))` : `math.log` est le logarithme naturel. Pour `[0.5, 0.25, 0.125]`, les logarithmes valent −0,6931, −1,3863 et −2,0794 ; leur somme vaut −4,1589, divisée par 3 elle donne −1,3863, et `math.exp(1.3863)` vaut 4.

**`perplexite_logprobs(logprobs)`** fait le même calcul à partir des log-probabilités, telles que les renvoient les API qui les exposent. `math.isfinite(lp)` refuse `nan` et `-inf`, et `lp > 0.0` refuse une log-probabilité positive, qui correspondrait à une probabilité supérieure à 1.

**`perplexite_produit(probas)`** calcule `math.prod(probas) ** (-1.0 / len(probas))`. Sur l'exemple, `math.prod` vaut 0,015625 = 1/64, et la puissance −1/3 redonne 4. Sur 1 100 tokens à 0,5, `math.prod` vaut `0.0` et la puissance négative lève `ZeroDivisionError`.

**`perplexite_corpus(sequences)`** additionne d'abord le nombre total de tokens `n`, renvoie `None` s'il est nul, puis accumule `nll -= lp` sur toutes les séquences. Pour A et B, `nll` vaut 16,2 et `n` vaut 10 : le résultat est `math.exp(1.62)`, soit 5,0531.

**`bits_par_caractere(nll_totale_nats, n_caracteres)`** divise la NLL totale par `n_caracteres * math.log(2)` : 6 / (32 × 0,6931) = 0,2705.

**`ppl_attendue_temperature(p, temperature)`** élève chaque probabilité à la puissance `1.0 / temperature`, normalise pour obtenir `q`, puis calcule `math.exp(sum(qi * -math.log(pi) ...))`. À T = 2, `poids` vaut [0,8367 ; 0,4472 ; 0,3162], `z` vaut 1,6001, `q` vaut [0,5229 ; 0,2795 ; 0,1976], et le résultat 2,9784.

**`p95(valeurs)`** est la fonction canonique du parcours : la valeur de rang ⌈0,95 × N⌉ dans la liste triée. Pour 20 valeurs, c'est la 19e, soit 1,51.

**`main()`**, bloc par bloc.

1. La perplexité de `[0.5, 0.25, 0.125]` vaut 4 par les trois chemins (logarithme naturel, produit, bits). Les deux erreurs donnent 64 (exponentielle de la somme) et 1,8259 (moyenne des log₁₀ passée à l'exponentielle).
2. On vérifie l'inégalité de Jensen, 1/p̄ = 3,4286 ≤ 4, et que des probabilités toutes égales à 1 donnent exactement 1.
3. Un token à 0,001 parmi dix fait passer la perplexité de 1,1111 à 2,1937.
4. `math.prod([0.5] * 1100)` vaut `0.0`, alors que la somme des logarithmes donne bien 2. La forme produit lève `ZeroDivisionError`, que le programme attrape et vérifie.
5. La perplexité du corpus, 5,0531, diffère de la moyenne des deux perplexités, 4,2471.
6. Deux découpages du même texte de NLL totale 6 donnent 4,4817 et 2,7183, mais les mêmes 0,2705 bits par caractère.
7. Glouton 1,4286, T = 1 : 2,2296 (que l'on vérifie égal à l'exponentielle de l'entropie de p), T = 2 : 2,9784.
8. La réponse fausse et sûre a une perplexité plus basse (1,0363) que la réponse juste avec un token rare (1,3861).
9. Le seuil p95 vaut 1,51 ; la réponse A (1,2368) passe, la réponse B (2,3989) part en revue humaine.
10. Une liste vide donne `None`. Une probabilité nulle, supérieure à 1 ou négative, et une log-probabilité positive lèvent `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`perplexite_logprobs(logprobs)`** — Cette fonction est la version de `perplexite` qui parle directement la langue des API : comme un traducteur qui reçoit le texte déjà en logarithmes, elle prend la liste des log-probabilités naturelles des tokens, renvoie `None` si elle est vide, lève `ValueError` pour une valeur non finie, comme `nan` ou −∞, ou positive, qui correspondrait à une probabilité supérieure à 1. Sinon, elle renvoie l'exponentielle de l'opposé de leur moyenne : 4,4817 pour quatre tokens à −1,5, 2,7183 pour six tokens à −1, 1,2368 pour la réponse A et 2,3989 pour la réponse B, que le seuil p95 envoie en revue humaine.

**`perplexite_produit(probas)`** — Celle-ci est la formule du manuel, juste sur le papier et fragile dans la machine : elle reçoit la liste des probabilités, les fait contrôler par `verifier_probas`, puis élève leur produit à la puissance −1/N. Pour [0,5 ; 0,25 ; 0,125], le produit vaut 1/64 et la fonction renvoie 4, comme les deux autres chemins ; mais pour 1 100 tokens à 0,5, le produit sous-déborde en 0.0 et la puissance négative de zéro lève `ZeroDivisionError`, que `main` attrape pour montrer pourquoi on additionne des logarithmes au lieu de multiplier des probabilités.

**`perplexite_corpus(sequences)`** — Cette fonction est le comptable qui tient un seul grand livre pour tout le corpus au lieu de faire la moyenne des bilans de chaque séquence : elle reçoit une liste de séquences de log-probabilités, compte d'abord le nombre total de tokens et renvoie `None` s'il est nul, puis parcourt toutes les valeurs, lève `ValueError` pour une log-probabilité non finie ou positive, et accumule la log-vraisemblance négative. Elle renvoie l'exponentielle de cette somme divisée par le nombre total de tokens : pour la séquence A de deux tokens et la séquence B de huit, 16,2 ÷ 10 donne 5,0531, alors que la moyenne des deux perplexités séparées vaudrait 4,2471.

**`bits_par_caractere(nll_totale_nats, n_caracteres)`** — Celle-ci est l'étalon qui permet de comparer deux modèles dont les tokenizers ne découpent pas le texte de la même façon, comme on compare deux voitures au litre aux cent kilomètres plutôt qu'au plein : elle reçoit la log-vraisemblance négative totale en nats et le nombre de caractères du texte, lève `ValueError` si ce nombre n'est pas strictement positif, et renvoie la NLL convertie en bits puis divisée par le nombre de caractères. Pour le même texte de NLL totale 6 et de 32 caractères, elle donne 0,2705 bit par caractère, que le découpage soit en quatre tokens, de perplexité 4,4817, ou en six, de perplexité 2,7183.

**`p95(valeurs)`** — Cette fonction est la fonction canonique du parcours, le juge de ligne qui place la barre là où 95 % des réponses validées passent sans encombre : elle reçoit une liste de valeurs, lève `ValueError` si elle est vide, la trie, et renvoie la valeur de rang ⌈0,95 × N⌉, le percentile 95 au rang le plus proche. Sur les 20 perplexités de référence, c'est la 19e valeur, 1,51, la plus haute exclue étant 1,95 ; ce seuil laisse passer la réponse A à 1,2368 et envoie la réponse B à 2,3989 en revue humaine.

**`main()`** — C'est le chef d'orchestre des dix démonstrations : il calcule la perplexité 4 de [0,5 ; 0,25 ; 0,125] par le logarithme naturel, le produit et les bits, montre les deux erreurs classiques qui donnent 64 et 1,8259, vérifie que la perplexité est au moins 1 et au moins l'inverse de la moyenne, puis montre qu'un seul token à 0,001 fait passer 1,1111 à 2,1937 et que le produit de 1 100 probabilités sous-déborde. Il compare ensuite la perplexité du corpus, 5,0531, à la moyenne 4,2471, les deux tokenizers et leurs 0,2705 bit par caractère, l'effet de la température, 1,4286, 2,2296 et 2,9784, puis la réponse fausse et sûre à 1,0363 contre la réponse juste à 1,3861, applique le seuil p95 et termine par les entrées vides ou invalides, avant le « OK ».

```python
"""Étape 62 — perplexité d'une réponse : log naturel, moyenne, corpus, tokenizer, température, seuil calibré."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def verifier_probas(probas: list[float]) -> None:
    for p in probas:
        if not 0.0 < p <= 1.0:
            raise ValueError(f"probabilité hors de ]0, 1] : {p}")


def perplexite(probas: list[float]) -> float | None:
    """PPL = exp(−(1/N) · somme des ln p_i) ; None si la séquence est vide."""
    if not probas:
        return None
    verifier_probas(probas)
    return math.exp(-sum(math.log(p) for p in probas) / len(probas))


def perplexite_logprobs(logprobs: list[float]) -> float | None:
    """Même calcul à partir des log-probabilités naturelles renvoyées par un modèle."""
    if not logprobs:
        return None
    for lp in logprobs:
        if not math.isfinite(lp) or lp > 0.0:
            raise ValueError(f"log-probabilité invalide : {lp}")
    return math.exp(-sum(logprobs) / len(logprobs))


def perplexite_produit(probas: list[float]) -> float:
    """Forme produit (∏ p_i)^(−1/N) : juste en théorie, fragile en pratique (sous-dépassement)."""
    verifier_probas(probas)
    return math.prod(probas) ** (-1.0 / len(probas))


def perplexite_corpus(sequences: list[list[float]]) -> float | None:
    """Perplexité d'un corpus : somme des NLL divisée par le nombre TOTAL de tokens."""
    n = sum(len(s) for s in sequences)
    if n == 0:
        return None
    nll = 0.0
    for s in sequences:
        for lp in s:
            if not math.isfinite(lp) or lp > 0.0:
                raise ValueError(f"log-probabilité invalide : {lp}")
            nll -= lp
    return math.exp(nll / n)


def bits_par_caractere(nll_totale_nats: float, n_caracteres: int) -> float:
    """Normalisation indépendante du tokenizer : NLL totale en bits, divisée par le nombre de caractères."""
    if n_caracteres <= 0:
        raise ValueError("n_caracteres > 0")
    return nll_totale_nats / (n_caracteres * math.log(2))


def ppl_attendue_temperature(p: list[float], temperature: float) -> float:
    """Perplexité moyenne, sous le modèle p, d'un texte tiré à la température T : exp(E_q[−ln p]), q ∝ p^(1/T)."""
    verifier_probas(p)
    if temperature <= 0:
        raise ValueError("T > 0 (T → 0 correspond au décodage glouton)")
    poids = [x ** (1.0 / temperature) for x in p]
    z = sum(poids)
    q = [w / z for w in poids]
    return math.exp(sum(qi * -math.log(pi) for qi, pi in zip(q, p)))


def p95(valeurs: list[float]) -> float:
    """Percentile 95 au rang le plus proche : la valeur de rang ceil(0,95 × N) dans la liste triée."""
    if not valeurs:
        raise ValueError("liste vide")
    s = sorted(valeurs)
    return s[math.ceil(0.95 * len(s)) - 1]


def main() -> None:
    print("1. Log naturel et moyenne : [0.5, 0.25, 0.125]")
    probas = [0.5, 0.25, 0.125]
    ppl = perplexite(probas)
    faux_somme = math.exp(-sum(math.log(p) for p in probas))
    faux_log10 = math.exp(-sum(math.log10(p) for p in probas) / 3)
    base2 = 2 ** (-sum(math.log2(p) for p in probas) / 3)
    print(f"  PPL = {ppl:.4f}   forme produit = {perplexite_produit(probas):.4f}   en bits : 2^2 = {base2:.4f}")
    print(f"  faux : exp de la somme = {faux_somme:.4f}   exp d'une moyenne en log10 = {faux_log10:.4f}")
    assert math.isclose(ppl, 4.0) and math.isclose(perplexite_produit(probas), 4.0) and math.isclose(base2, 4.0)
    assert math.isclose(faux_somme, 64.0) and round(faux_log10, 4) == 1.8259

    print("2. PPL >= 1, et PPL >= 1 / moyenne arithmétique des p")
    moyenne = sum(probas) / 3
    print(f"  1 / moyenne = 1 / {moyenne:.5f} = {1 / moyenne:.4f} <= {ppl:.4f}")
    assert 1 / moyenne <= ppl and perplexite([1.0, 1.0]) == 1.0

    print("3. Un seul token très improbable domine")
    sure = perplexite([0.9] * 10)
    surprise = perplexite([0.9] * 9 + [0.001])
    print(f"  10 tokens à 0.9 : {sure:.4f}   9 à 0.9 et un à 0.001 : {surprise:.4f}")
    assert round(sure, 4) == 1.1111 and round(surprise, 4) == 2.1937

    print("4. 1100 tokens à 0.5 : le produit sous-déborde, la somme des logs non")
    longue = [0.5] * 1100
    print(f"  produit des p = {math.prod(longue)}   PPL par les logs = {perplexite(longue):.4f}")
    assert math.prod(longue) == 0.0 and math.isclose(perplexite(longue), 2.0)
    try:
        perplexite_produit(longue)
    except ZeroDivisionError:
        print("  forme produit → ZeroDivisionError")
    else:
        raise AssertionError("le produit aurait dû sous-déborder")

    print("5. Corpus : ratio des sommes, pas moyenne des perplexités")
    seq_a, seq_b = [-0.1, -0.1], [-2.0] * 8
    corpus = perplexite_corpus([seq_a, seq_b])
    moyenne_ppl = (perplexite_logprobs(seq_a) + perplexite_logprobs(seq_b)) / 2
    print(f"  corpus = exp(16.2 / 10) = {corpus:.4f}   moyenne des deux PPL = {moyenne_ppl:.4f}")
    assert round(corpus, 4) == 5.0531 and round(moyenne_ppl, 4) == 4.2471

    print("6. Même texte, même probabilité, deux tokenizers")
    nll_totale, n_car = 6.0, 32
    ppl_x = perplexite_logprobs([-1.5] * 4)
    ppl_y = perplexite_logprobs([-1.0] * 6)
    bpc = bits_par_caractere(nll_totale, n_car)
    print(f"  4 tokens : PPL = {ppl_x:.4f}   6 tokens : PPL = {ppl_y:.4f}   bits par caractère = {bpc:.4f} dans les deux cas")
    assert round(ppl_x, 4) == 4.4817 and round(ppl_y, 4) == 2.7183 and round(bpc, 4) == 0.2705

    print("7. Même modèle, température différente : p = [0.7, 0.2, 0.1] à chaque pas")
    p = [0.7, 0.2, 0.1]
    glouton = 1 / max(p)
    t1 = ppl_attendue_temperature(p, 1.0)
    t2 = ppl_attendue_temperature(p, 2.0)
    print(f"  glouton = {glouton:.4f}   T = 1 : {t1:.4f}   T = 2 : {t2:.4f}")
    assert round(glouton, 4) == 1.4286 and round(t1, 4) == 2.2296 and round(t2, 4) == 2.9784
    assert math.isclose(t1, math.exp(-sum(x * math.log(x) for x in p)))   # T = 1 : exp(entropie)

    print("8. Basse perplexité ne veut pas dire vrai")
    fausse_sure = perplexite([0.97, 0.95, 0.96, 0.98])      # « plafond d'endettement : 60 % » (faux)
    juste_rare = perplexite([0.97, 0.95, 0.30, 0.98])       # bonne réponse avec un nom translittéré rare
    print(f"  réponse fausse et sûre : {fausse_sure:.4f}   réponse juste avec un token rare : {juste_rare:.4f}")
    assert round(fausse_sure, 4) == 1.0363 and round(juste_rare, 4) == 1.3861 and fausse_sure < juste_rare

    print("9. Seuil calibré sur des réponses validées (p95), puis décision")
    reference = [1.21, 1.35, 1.18, 1.42, 1.27, 1.30, 1.25, 1.51, 1.33, 1.22,
                 1.29, 1.38, 1.24, 1.47, 1.31, 1.26, 1.36, 1.28, 1.40, 1.95]
    seuil = p95(reference)
    for nom, lps in (("réponse A", [-0.2, -0.3, -0.25, -0.1]), ("réponse B", [-0.2, -1.9, -0.8, -0.6])):
        v = perplexite_logprobs(lps)
        print(f"  {nom} : PPL = {v:.4f} → {'revue humaine' if v > seuil else 'pas de revue'} (seuil p95 = {seuil:.2f})")
    ppl_a = perplexite_logprobs([-0.2, -0.3, -0.25, -0.1])
    ppl_b = perplexite_logprobs([-0.2, -1.9, -0.8, -0.6])
    assert seuil == 1.51 and round(ppl_a, 4) == 1.2368 and round(ppl_b, 4) == 2.3989
    assert ppl_a <= seuil < ppl_b

    print("10. Entrées vides ou invalides")
    assert perplexite([]) is None and perplexite_corpus([[], []]) is None
    for mauvais in ([0.5, 0.0], [1.2], [0.5, -0.1]):
        try:
            perplexite(mauvais)
        except ValueError as e:
            print(f"  {mauvais} → ValueError ({e})")
        else:
            raise AssertionError("une probabilité invalide aurait dû être refusée")
    try:
        perplexite_logprobs([-0.5, 0.3])
    except ValueError:
        print("  log-probabilité positive → ValueError")
    else:
        raise AssertionError("une log-probabilité positive aurait dû être refusée")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Log naturel et moyenne : [0.5, 0.25, 0.125]
  PPL = 4.0000   forme produit = 4.0000   en bits : 2^2 = 4.0000
  faux : exp de la somme = 64.0000   exp d'une moyenne en log10 = 1.8259
…
4. 1100 tokens à 0.5 : le produit sous-déborde, la somme des logs non
  produit des p = 0.0   PPL par les logs = 2.0000
5. Corpus : ratio des sommes, pas moyenne des perplexités
  corpus = exp(16.2 / 10) = 5.0531   moyenne des deux PPL = 4.2471
6. Même texte, même probabilité, deux tokenizers
  4 tokens : PPL = 4.4817   6 tokens : PPL = 2.7183   bits par caractère = 0.2705 dans les deux cas
7. Même modèle, température différente : p = [0.7, 0.2, 0.1] à chaque pas
  glouton = 1.4286   T = 1 : 2.2296   T = 2 : 2.9784
8. Basse perplexité ne veut pas dire vrai
  réponse fausse et sûre : 1.0363   réponse juste avec un token rare : 1.3861
9. Seuil calibré sur des réponses validées (p95), puis décision
  réponse A : PPL = 1.2368 → pas de revue (seuil p95 = 1.51)
  réponse B : PPL = 2.3989 → revue humaine (seuil p95 = 1.51)
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : la perplexité se calcule en une ligne, mais chaque détail compte (logarithme naturel, moyenne, sommes de logarithmes, unité de comptage). Et même bien calculée, elle mesure l'assurance du modèle, pas la vérité de sa réponse.

## Squelette algorithmique

L'entrée est la liste des log-probabilités naturelles des tokens de la réponse, telles que les renvoie le modèle ; pour un corpus, c'est une liste de telles listes ; pour la décision, s'ajoutent les perplexités de réponses déjà validées. La sortie est une perplexité au moins égale à 1, ou INDÉFINI pour une séquence vide, puis une décision de revue. L'idée : additionner des logarithmes (jamais multiplier des probabilités), diviser par le nombre de tokens, prendre l'exponentielle, et comparer à un seuil calibré dans les mêmes conditions.

```text
ALGORITHME Perplexité
ENTRÉES : log-probabilités ℓ₁ … ℓ_N des tokens de la réponse (logarithme naturel)
SORTIE  : PPL ≥ 1, ou INDÉFINI si N = 0
    SI N = 0 ALORS
        RETOURNER INDÉFINI
    FIN SI
    nll ← 0
    POUR i DE 1 À N FAIRE
        SI ℓᵢ > 0 OU ℓᵢ = −∞ OU ℓᵢ n'est pas un nombre ALORS
            ÉCHOUER « log-probabilité invalide »
        FIN SI
        nll ← nll − ℓᵢ                           ▹ somme de logarithmes : pas de sous-dépassement
    FIN POUR
    RETOURNER exp(nll / N)                       ▹ la MOYENNE, pas la somme

ALGORITHME PerplexitéCorpus
ENTRÉES : séquences s₁ … s_S, chacune une liste de log-probabilités
SORTIE  : PPL du corpus, ou INDÉFINI
    nll ← 0 ; n ← 0
    POUR chaque séquence s FAIRE
        POUR chaque ℓ de s FAIRE
            nll ← nll − ℓ ; n ← n + 1
        FIN POUR
    FIN POUR
    SI n = 0 ALORS
        RETOURNER INDÉFINI
    FIN SI
    RETOURNER exp(nll / n)                       ▹ rapport des sommes, pas moyenne des PPL

ALGORITHME PerplexitéÀLaTempérature
ENTRÉES : distribution p sur les tokens possibles d'un pas, température T > 0
SORTIE  : perplexité attendue de ce que l'agent produit à la température T
    POUR chaque token x FAIRE
        w[x] ← p[x] ^ (1 / T)
    FIN POUR
    Z ← Σ w[x]
    RETOURNER exp( Σ (w[x] / Z) × (−ln p[x]) )

ALGORITHME DécisionDeRevue
ENTRÉES : perplexités v₁ … v_M de réponses validées (même modèle, même température), réponse à juger
SORTIE  : « revue humaine » ou « pas de revue »
    trier v
    seuil ← v[⌈0,95 × M⌉]                        ▹ percentile 95 au rang le plus proche
    SI Perplexité(réponse) > seuil ALORS
        RETOURNER « revue humaine »
    SINON
        RETOURNER « pas de revue »
    FIN SI
```

**Complexité :** Perplexité fait un seul passage sur les N log-probabilités, avec un nombre fixe d'opérations par token, puis une exponentielle : O(N) en temps et O(1) en mémoire supplémentaire, puisque seule la somme `nll` est gardée. La forme produit aurait la même complexité, O(N), mais elle est numériquement fausse dès quelques centaines de tokens : le problème est la précision des flottants, pas le temps de calcul. PerplexitéCorpus coûte O(n) pour n tokens au total, avec deux compteurs en mémoire. PerplexitéÀLaTempérature coûte O(|V|) pour un vocabulaire de |V| tokens possibles à ce pas : une puissance et un logarithme par token, puis deux sommes. DécisionDeRevue trie une fois les M valeurs de calibration, en O(M log M), puis chaque nouvelle réponse ne coûte que O(N) : le seuil se calcule une fois, pas à chaque réponse.

**Du squelette au code :** Perplexité est `perplexite_logprobs`, dont la boucle de garde utilise `math.isfinite(lp)` (qui écarte −∞ et les valeurs non numériques) et `lp > 0.0`, et dont la dernière ligne est `math.exp(-sum(logprobs) / len(logprobs))` ; `perplexite` fait le même calcul à partir des probabilités, avec `math.log`. Le test « N = 0 » est `if not logprobs: return None`. PerplexitéCorpus est `perplexite_corpus`, avec ses deux boucles imbriquées et `nll -= lp`. PerplexitéÀLaTempérature est `ppl_attendue_temperature`, où `poids` est w, `z` est Z et `q` est la liste des w[x]/Z. DécisionDeRevue se lit dans le bloc 9 de `main()` : `seuil = p95(reference)`, puis la comparaison `v > seuil`. La fonction `perplexite_produit` n'a pas de ligne dans le squelette : elle n'est là que pour montrer le sous-dépassement.

## Cas d'usage réels aux Émirats

Les seuils, perplexités et volumes ci-dessous sont illustratifs ; en production, on les calibre sur des réponses validées, pour un modèle, une version et une température donnés.

### Banque — un signal de revue, pas un détecteur de vérité

Une banque de détail de Dubaï fait rédiger par un agent le résumé de chaque dossier de prêt personnel avant le passage en comité : revenu, mensualités existantes, ratio d'endettement total et durée demandée. Le modèle tourne à une température basse et expose ses log-probabilités ; l'équipe a calibré un seuil de revue au percentile 95 de 500 résumés validés, soit 1,51 dans notre exemple. Un résumé dont la perplexité dépasse ce seuil, comme la réponse B à 2,40, part en relecture chez un analyste avant le comité. Mais un résumé qui affirme avec assurance « plafond d'endettement : 60 % », avec une perplexité de 1,04, passerait ce filtre : c'est la vérification de fidélité contre la règle de la CBUAE (50 % du revenu, toutes mensualités comprises) qui l'arrête. La banque garde donc la perplexité comme signal d'appoint et non comme barrière. Elle suit deux indicateurs : le taux de résumés envoyés en revue, et la part des erreurs trouvées en comité qui avaient été signalées par la perplexité.

### Secteur public — comparer deux modèles arabes sans se faire piéger par le tokenizer

Une entité de services publics en ligne, accessible par UAE Pass, doit choisir le modèle qui rédige ses réponses en arabe. Elle compare un modèle généraliste et un modèle spécialisé dans l'arabe, comme Jais ou Falcon, sur 2 000 messages d'usagers anonymisés, conformément à la PDPL. Les deux tokenizers ne coupent pas le texte de la même façon : un modèle qui découpe l'arabe en plus de tokens affiche mécaniquement une perplexité par token plus basse. Dans l'exemple du programme, un même texte de NLL totale 6 nats a une perplexité de 4,48 en 4 tokens et de 2,72 en 6 tokens, pour la même probabilité du texte. L'équipe compare donc les bits par caractère (0,27 dans les deux cas de l'exemple) et non la perplexité. Sans cette précaution, elle aurait choisi le modèle sur un artefact de découpage. L'indicateur suivi est le nombre de bits par caractère sur un jeu de messages tenu à part, mis à jour chaque trimestre.

### Assurance — repérer une pièce de sinistre illisible avant l'extraction

Un assureur auto et santé reçoit des photos de factures de garage et de comptes rendus médicaux, que l'OCR transforme en texte avant qu'un agent n'en extraie montant, date et prestataire. Une photo floue produit un texte haché : la perplexité de ce texte sous un modèle de référence devient très supérieure à celle des factures lisibles. L'assureur fixe un seuil sur la distribution observée des pièces lisibles, et toute pièce au-dessus déclenche une demande de nouvelle photo, au lieu d'une extraction. Sans ce filtre, l'agent extrairait un montant à partir de caractères mal lus, et le gestionnaire découvrirait l'erreur au moment du paiement. Ici, la perplexité porte sur l'**entrée** de l'agent, pas sur sa réponse : c'est son usage le plus robuste. L'indicateur suivi est le taux de pièces redemandées et le taux d'erreurs d'extraction sur les pièces acceptées.

### Crypto — surveiller la dérive des messages entrants

Une plateforme d'actifs virtuels agréée par la VARA fait trier les messages de son support par un agent. Chaque semaine, elle calcule la perplexité du corpus des messages entrants sous un modèle de référence figé, par le rapport des sommes, c'est-à-dire la NLL totale divisée par le nombre total de tokens. Si elle faisait la moyenne des perplexités des messages, les messages très courts (« ok », « merci ») pèseraient autant que les longues réclamations, et la courbe serait faussée, comme dans l'exemple où 5,05 devient 4,25. Une hausse nette d'une semaine à l'autre signale un nouveau type de demande, par exemple une vague de messages sur une arnaque qui imite la plateforme. L'équipe ajoute alors ces cas au jeu d'évaluation (étape 13 bis) et vérifie que l'agent sait les escalader. On suit la perplexité hebdomadaire du corpus et le délai entre l'apparition d'un nouveau motif et son ajout au jeu d'évaluation.

### RH — une boucle de répétition qui passe sous le radar

Un cabinet RH présent dans plusieurs émirats fait générer par un agent des projets de lettres d'offre, avec salaire de base, allocations et durée de la période d'essai. Un jour, une version du prompt fait recopier trois fois la même clause d'allocation logement. Cette lettre a une perplexité **très basse**, parce que chaque répétition est plus prévisible que la précédente : un filtre qui ne regarde que les perplexités hautes la laisse passer. Le cabinet ajoute deux contrôles : une alerte quand la perplexité tombe sous le percentile 1 des lettres validées, et un détecteur de n-grammes répétés. Sans eux, une lettre incohérente serait partie vers un candidat, avec un montant d'allocation apparemment compté trois fois. L'indicateur suivi est le nombre de lettres bloquées par chacun des deux contrôles.

### Immobilier — un seuil par température

Une agence de Dubaï et d'Abu Dhabi utilise le même modèle pour deux tâches : des descriptions d'annonces, générées à une température élevée pour varier le style, et des réponses factuelles sur les frais de transfert DLD (4 % de la valeur), générées à une température basse. L'équipe avait d'abord appliqué un seul seuil de perplexité aux deux. Les descriptions partaient presque toutes en revue, alors qu'elles étaient correctes, simplement parce que la perplexité de la sortie croît avec la température : avec la distribution de l'exemple, 1,43 en glouton, 2,23 à T = 1, 2,98 à T = 2. Elle calibre désormais un seuil par tâche, et donc par température, sur des sorties validées de cette tâche. Le taux de revue des descriptions redescend à un niveau gérable, sans relâcher la surveillance des réponses factuelles. L'indicateur suivi est le taux de revue par tâche et la part des revues qui trouvent une vraie erreur.

## Pièges et limites

- **Prendre l'exponentielle de la somme, ou mélanger les bases.** La somme donne PPLᴺ, qui croît avec la longueur ; un log₁₀ passé à `math.exp` donne un nombre sans signification.
- **Comparer des perplexités entre tokenizers différents.** On compare des bits par caractère, ou par octet.
- **Faire la moyenne des perplexités de plusieurs séquences.** La perplexité d'un corpus est le rapport des sommes ; si l'on choisit l'autre convention, on la déclare.
- **Lire une perplexité basse comme une réponse vraie.** Les hallucinations sûres d'elles et les boucles de répétition ont une perplexité basse. On combine avec la fidélité et la justesse.
- **Garder un seuil quand on change de modèle, de version ou de température.** Le seuil se recalibre à chaque changement, sur des sorties validées.

### Exercice feuille blanche

1. Sans regarder le code, écrire `perplexite(probas)` avec la garde `None` et la vérification des probabilités, puis vérifier qu'elle renvoie 4 pour [0,5 ; 0,25 ; 0,125].
2. Prédire, puis vérifier : on ajoute un quatrième token de probabilité 1 à [0,5 ; 0,25 ; 0,125]. Que devient la perplexité ? (Réponse : le produit reste 1/64, mais N vaut 4 : 64^(1/4) ≈ 2,828. Ajouter des tokens certains fait baisser la perplexité, ce qui avantage les réponses remplies de formules toutes faites.)
3. Trouver le bug : `return math.exp(-sum(logprobs))`. Que vaut cette fonction sur une réponse de 10 tokens tous à 0,5 ? (Réponse : 2¹⁰ = 1 024 au lieu de 2.)

## Pour aller plus loin

La perplexité d'une réponse se calcule sur les tokens de la réponse seulement, en excluant ceux du prompt. Pour détecter les hallucinations, des signaux plus fiables que la perplexité par token existent, comme l'entropie sémantique (Farquhar et al., 2024), qui génère plusieurs réponses, les regroupe par sens et mesure la dispersion entre groupes. La calibration d'un modèle, c'est-à-dire l'accord entre la probabilité annoncée et la fréquence réelle de réussite, se mesure par un diagramme de fiabilité et l'erreur de calibration attendue (ECE).

> Suite : [Answer Correctness](<63-Evaluation-Formule-Answer-Correctness.md>) — étape 63.
