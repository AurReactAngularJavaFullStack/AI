# Étape 72 quinquies — Production — Budget de raisonnement

**Dossier :** 12-Production-Couts-Optimisation

> Étape 72 quinquies du parcours · Prérequis : [Observabilité : traces, coûts et dérive](<72d-Observabilite-Traces-Couts-et-Derive.md>) · Suite : [Descente de gradient et LoRA](<73-Optimisation-et-Fine-Tuning.md>)

**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, AI Platform Team, Forward-Deployed Engineers  
**Nom du fichier :** 72e-Budget-de-Raisonnement.md

## Définition

Le budget de raisonnement est la quantité de calcul qu'un agent accepte de dépenser **au moment de répondre** pour augmenter ses chances d'avoir juste, sans toucher aux poids du modèle. On parle aussi de calcul à l'inférence (*test-time compute*). Trois leviers le règlent :

- **L'effort de réflexion** allonge une seule trajectoire : le modèle écrit plus de tokens de raisonnement avant sa réponse.
- **Le best-of-N avec vérificateur** élargit la recherche. L'agent produit N réponses indépendantes, et un vérificateur (un test, un schéma, un outil de calcul, un juge) livre la première qu'il accepte. Si aucune ne passe, l'agent escalade.
- **Le vote majoritaire** (*self-consistency*) se passe de vérificateur : l'agent produit N réponses et garde la plus fréquente.

Chaque levier coûte des tokens de sortie, donc des AED et des secondes. Choisir le budget, c'est trouver le point où une unité de calcul de plus rapporte moins qu'elle ne coûte.

## Rôle dans un agent

Le budget se décide pendant le temps « décider » de la boucle percevoir → décider → agir → observer, par un composant que l'on appellera le **contrôleur de budget**.

1. À l'arrivée d'une tâche, un **routeur** (une règle, ou un petit classifieur entraîné comme à l'étape 73) la classe facile ou difficile.
2. Le contrôleur choisit alors le niveau d'effort et le nombre d'essais N, puis lance N fois la boucle `executer_agent` (code canonique de l'étape 1).
3. Il fait passer chaque essai dans un **vérificateur** : validation de schéma (étape 8), outil de calcul, tests, ou juge (étapes 54 à 63).
4. Il livre la réponse acceptée, ou escalade.

Le contrôleur a besoin de deux nombres par classe de tâches : la probabilité de succès p d'un essai, et le coût d'un essai. Ils viennent de l'évaluation (étape 60) et des traces de production (étape 72 quater). Le **garde-fou de budget** de l'étape 72 borne le tout, car un budget de raisonnement sans plafond est une facture sans plafond.

## Équation complète

Best-of-N avec un vérificateur parfait, c'est-à-dire le pass@N de l'étape 60 :

$$
P_N = 1 - (1 - p)^N
$$

Gain apporté par le N-ième essai :

$$
\Delta(N) = P_N - P_{N-1} = p\,(1 - p)^{N-1}
$$

Avec un vérificateur imparfait qui livre le premier essai accepté, a est la probabilité qu'un essai soit rejeté :

$$
a = 1 - p\,v_+ - (1 - p)\,v_-
$$

$$
P_{juste}(N) = p\,v_+\,\frac{1 - a^N}{1 - a}, \qquad P_{faux}(N) = (1 - p)\,v_-\,\frac{1 - a^N}{1 - a}, \qquad P_{esc}(N) = a^N
$$

$$
\text{précision des réponses livrées} = \frac{p\,v_+}{p\,v_+ + (1 - p)\,v_-}
$$

Vote majoritaire sur N votes, N impair :

$$
P_{maj}(N) = \sum_{k=(N+1)/2}^{N} \binom{N}{k}\, p^k\, (1 - p)^{N-k}
$$

Effet de deux votes de plus, avec N = 2m + 1 :

$$
P_{maj}(2m+3) - P_{maj}(2m+1) = \binom{2m+1}{m}\, \bigl(p\,(1 - p)\bigr)^{m+1}\, (2p - 1)
$$

Coût d'un essai, puis de N essais lancés en parallèle :

$$
C_1 = N_{in}\,P_{in} + N_{out}\,P_{out}, \qquad C(N) = N\,C_1
$$

Gain net, puis nombre optimal d'essais :

$$
G(N) = V\,P_N - N\,C_1
$$

$$
N^* = \begin{cases} 0 & \text{si } V p < C_1 \\ 1 + \left\lfloor \dfrac{\ln\bigl(C_1 / (V p)\bigr)}{\ln(1 - p)} \right\rfloor & \text{sinon} \end{cases}
$$

Routage adaptatif entre tâches faciles (f) et difficiles (d), les difficiles formant la part π_d du trafic :

$$
\max_{N_f,\,N_d} \Bigl[(1 - \pi_d)\,G_f(N_f) + \pi_d\,G_d(N_d)\Bigr] \;\ge\; \max_{N} \Bigl[(1 - \pi_d)\,G_f(N) + \pi_d\,G_d(N)\Bigr]
$$

## Décryptage des symboles

$$
p
$$

**Sens :** probabilité qu'un essai seul soit juste, pour une classe de tâches donnée · **Type / plage :** réel dans [0, 1] · **Variable Python :** `p`

$$
N
$$

**Sens :** nombre d'essais indépendants. Il joue le rôle du k de pass@k (étape 60). N seul compte des essais ; N_in et N_out, hérités de l'étape 72, comptent des tokens · **Type / plage :** entier ≥ 0 · **Variable Python :** `n`

$$
P_N
$$

**Sens :** probabilité qu'au moins un des N essais soit juste, donc qu'un vérificateur parfait livre une bonne réponse · **Type / plage :** réel dans [0, 1] · **Variable Python :** `best_of_n(p, n)`

$$
\Delta(N)
$$

**Sens :** gain de probabilité apporté par le N-ième essai · **Type / plage :** réel dans [0, 1] · **Variable Python :** la liste `gains`

$$
v_+
$$

**Sens :** probabilité que le vérificateur accepte une réponse juste, c'est-à-dire son rappel sur les réponses justes · **Type / plage :** réel dans [0, 1] · **Variable Python :** `v_plus`

$$
v_-
$$

**Sens :** probabilité que le vérificateur accepte une réponse fausse, c'est-à-dire son taux de faux positifs · **Type / plage :** réel dans [0, 1] · **Variable Python :** `v_moins`

$$
a
$$

**Sens :** probabilité qu'un essai soit rejeté par le vérificateur · **Type / plage :** réel dans [0, 1] · **Variable Python :** `rejet`

$$
P_{juste}(N),\; P_{faux}(N),\; P_{esc}(N)
$$

**Sens :** probabilités de livrer une réponse juste, de livrer une réponse fausse, et d'escalader faute d'essai accepté ; leur somme vaut 1 · **Type / plage :** réels dans [0, 1] · **Variable Python :** le triplet renvoyé par `best_of_n_verifie(p, n, v_plus, v_moins)`

$$
P_{maj}(N)
$$

**Sens :** probabilité que plus de la moitié des N votes soient justes · **Type / plage :** réel dans [0, 1], N impair · **Variable Python :** `vote_majoritaire(p, n)`

$$
m
$$

**Sens :** demi-nombre de votes, avec N = 2m + 1 · **Type / plage :** entier ≥ 0 · **Variable Python :** `m`

$$
N_{in},\; N_{out},\; P_{in},\; P_{out}
$$

**Sens :** tokens d'entrée et de sortie d'un essai, et leurs prix par token, comme à l'étape 72. La sortie comprend les tokens de réflexion · **Type / plage :** entiers ≥ 0 ; prix en USD par token, illustratifs (3 USD et 15 USD par million) · **Variable Python :** arguments de `cout_essai_aed`, constantes `PRIX_IN` et `PRIX_OUT`

$$
C_1
$$

**Sens :** coût d'un essai, converti en AED à 3,6725 AED par USD · **Type / plage :** réel > 0 · **Variable Python :** `c1 = cout_essai_aed(2000, 1500)`

$$
V
$$

**Sens :** valeur d'une tâche réussie, en AED : ce qu'elle rapporte, ou l'intervention humaine qu'elle évite. Une tâche ratée vaut 0 dans ce modèle · **Type / plage :** réel ≥ 0 · **Variable Python :** `valeur`

$$
G(N)
$$

**Sens :** gain net de N essais parallèles, en AED par tâche · **Type / plage :** réel · **Variable Python :** `gain_net(p, n, valeur, cout)`

$$
N^*
$$

**Sens :** nombre d'essais qui maximise G(N) · **Type / plage :** entier ≥ 0 · **Variable Python :** `n_etoile(...)` (par la boucle) et `n_etoile_formule(...)` (par la forme fermée)

$$
\pi_d,\; G_f,\; G_d
$$

**Sens :** part des tâches difficiles dans le trafic, et gains nets des classes facile et difficile · **Type / plage :** π_d dans [0, 1] ; gains réels · **Variable Python :** `0.3` dans `melange`, et `gain_net` appelé par classe

## Démonstration

### 1. Avec un vérificateur parfait, best-of-N vaut pass@N

On suppose que les N essais sont indépendants et que chacun est juste avec la probabilité p. Un vérificateur parfait accepte toute réponse juste et refuse toute réponse fausse. L'agent n'échoue donc que si les N essais sont faux, et, par indépendance, la probabilité de N échecs est le produit des N probabilités d'échec :

$$
P_N = 1 - P(\text{N échecs}) = 1 - (1 - p)^N
$$

C'est exactement le pass@N démontré à l'[étape 60](<../10-Evaluation/60-Evaluation-Formule-Agent-Goal-Accuracy.md>). Le vérificateur est ce qui transforme cette mesure (« au moins un des N essais est juste ») en stratégie de production. Sans vérificateur, pass@N reste une mesure : personne ne sait lequel des N essais est le bon. Avec p = 0,4, on obtient P₁ = 0,4, P₂ = 0,64, P₃ = 0,784, P₄ = 0,8704 et P₅ = 0,92224.

### 2. Les rendements sont décroissants : la courbe est concave

Le gain du N-ième essai vaut

$$
\Delta(N) = \bigl(1 - (1-p)^N\bigr) - \bigl(1 - (1-p)^{N-1}\bigr) = (1-p)^{N-1}\bigl(1 - (1-p)\bigr) = p\,(1-p)^{N-1}
$$

On a mis (1 − p)ᴺ⁻¹ en facteur. Chaque gain vaut le précédent multiplié par 1 − p < 1 : les gains décroissent de façon géométrique. Avec p = 0,4, ils valent 0,4 ; 0,24 ; 0,144 ; 0,0864 ; 0,05184. Une suite dont les accroissements diminuent est concave.

Comme chaque essai coûte le même nombre de tokens, les tokens croissent linéairement avec N. La courbe de la justesse en fonction des tokens est donc concave elle aussi : chaque millier de tokens supplémentaire achète moins de justesse que le précédent.

### 3. Vérificateur imparfait : la précision ne bouge pas, seule la couverture monte

Un vrai vérificateur se trompe. On note v₊ la probabilité qu'il accepte une réponse juste, et v₋ la probabilité qu'il accepte une réponse fausse. L'agent examine les essais dans l'ordre et livre le premier accepté ; si aucun ne l'est, il escalade vers un humain. Chaque essai a trois issues, indépendantes d'un essai à l'autre :

- accepté et juste, avec la probabilité p v₊ ;
- accepté et faux, avec la probabilité (1 − p) v₋ ;
- rejeté, avec la probabilité a = 1 − p v₊ − (1 − p) v₋.

L'agent livre une réponse juste à l'essai i si les i − 1 premiers essais ont été rejetés et que le i-ième est accepté et juste :

$$
P_{juste}(N) = \sum_{i=1}^{N} a^{i-1}\, p\, v_+ = p\, v_+\, \frac{1 - a^N}{1 - a}
$$

La somme est une série géométrique de raison a (étape 11). En effet, (1 + a + ⋯ + aᴺ⁻¹)(1 − a) = 1 − aᴺ, parce que les termes intermédiaires s'annulent deux à deux. Le même calcul donne P_faux(N). L'escalade a lieu si les N essais sont rejetés, ce qui arrive avec la probabilité aᴺ. Les trois probabilités somment à 1, puisque p v₊ + (1 − p) v₋ = 1 − a.

**Première conséquence : la précision ne dépend pas de N.** La part des réponses livrées qui sont justes vaut

$$
\frac{P_{juste}(N)}{P_{juste}(N) + P_{faux}(N)} = \frac{p\,v_+}{p\,v_+ + (1-p)\,v_-}
$$

Ajouter des essais ne rend donc pas les réponses livrées plus sûres : l'agent en livre seulement davantage, au lieu d'escalader.

**Seconde conséquence : il y a un plafond.** Quand N grandit, aᴺ tend vers 0 dès que a < 1, et P_juste(N) tend vers cette même précision.

**Exemple chiffré.** Avec p = 0,4, v₊ = 0,9 et v₋ = 0,1, on a p v₊ = 0,36, (1 − p) v₋ = 0,06 et a = 0,58. À N = 3, 1 − a³ = 0,804888 et (1 − a³)/(1 − a) = 1,9164. On obtient donc P_juste = 0,689904, P_faux = 0,114984 et P_esc = 0,195112. La précision vaut 0,36 / 0,42 = 6/7 ≈ 0,8571, à N = 3 comme à N = 10, et aucun N ne dépassera 85,7 % de réponses justes.

Avec un vérificateur parfait (v₊ = 1 et v₋ = 0), on a a = 1 − p, et la formule redonne 1 − (1 − p)ᴺ. Les deux taux d'un vérificateur se mesurent comme ceux de n'importe quel classifieur : v₊ est son rappel sur les réponses justes, v₋ son taux de faux positifs (étapes 50 et 51).

### 4. Le vote majoritaire suit la loi binomiale

Sans vérificateur, l'agent compte les réponses. On commence par le cas binaire : la réponse est juste ou fausse, et l'on dispose d'un nombre N impair de votes indépendants, chacun juste avec la probabilité p.

Le nombre K de votes justes suit la loi binomiale, déjà rencontrée aux étapes 7 et 60. Pour obtenir exactement k votes justes, il faut choisir lesquels, ce qui se fait de C(N, k) façons. Par indépendance, chacun de ces choix a la probabilité pᵏ(1 − p)ᴺ⁻ᵏ. La majorité est juste quand K ≥ (N + 1)/2, d'où la formule de P_maj(N). Avec p = 0,7 :

$$
P_{maj}(3) = 3 \times 0{,}7^2 \times 0{,}3 + 0{,}7^3 = 0{,}441 + 0{,}343 = 0{,}784
$$

$$
P_{maj}(5) = 10 \times 0{,}7^3 \times 0{,}3^2 + 5 \times 0{,}7^4 \times 0{,}3 + 0{,}7^5 = 0{,}3087 + 0{,}36015 + 0{,}16807 = 0{,}83692
$$

Avec p = 0,4, le vote fait pire qu'un seul essai : P_maj(3) = 3 × 0,16 × 0,6 + 0,064 = 0,352, et P_maj(5) = 0,31744.

### 5. Deux votes de plus : l'incrément exact et le théorème du jury

On passe de N = 2m + 1 à N + 2 votes. On note K le nombre de votes justes parmi les N premiers. Les deux nouveaux votes ne changent l'issue que dans deux cas :

- **K = m** : la majorité était fausse, et deux nouveaux votes justes la rendent juste. Probabilité : C(2m + 1, m) pᵐ(1 − p)ᵐ⁺¹ × p².
- **K = m + 1** : la majorité était juste, et deux nouveaux votes faux la renversent. Probabilité : C(2m + 1, m + 1) pᵐ⁺¹(1 − p)ᵐ × (1 − p)².

Dans tous les autres cas, l'issue ne change pas. Avec K ≤ m − 1, même deux votes justes laissent au plus m + 1 voix sur 2m + 3. Avec K ≥ m + 2, la majorité reste acquise. Enfin, deux nouveaux votes partagés ajoutent une voix de chaque côté, sans changer l'écart.

Or C(2m + 1, m) = C(2m + 1, m + 1), puisque choisir m votes revient à choisir les m + 1 autres. La différence des deux cas vaut donc :

$$
P_{maj}(2m+3) - P_{maj}(2m+1) = \binom{2m+1}{m}\, p^{m+1}(1-p)^{m+1}\,\bigl(p - (1 - p)\bigr) = \binom{2m+1}{m}\,\bigl(p\,(1-p)\bigr)^{m+1}\,(2p - 1)
$$

Le signe de l'incrément est celui de 2p − 1 :

- **Si p > 1/2**, chaque paire de votes ajoutée améliore la majorité, qui tend vers 1 : c'est le théorème du jury de Condorcet.
- **Si p < 1/2**, chaque paire la dégrade, et la majorité tend vers 0 : le vote amplifie l'erreur.
- **Si p = 1/2**, rien ne bouge, et P_maj(N) = 1/2 pour tout N, par symétrie.

Avec p = 0,7 et m = 0, l'incrément vaut 1 × 0,21 × 0,4 = 0,084, et 0,7 + 0,084 = 0,784. Avec m = 1, il vaut 3 × 0,21² × 0,4 = 0,05292, et 0,784 + 0,05292 = 0,83692.

Les incréments décroissent, eux aussi. Le rapport de deux incréments successifs vaut

$$
\frac{\binom{2m+3}{m+1}}{\binom{2m+1}{m}}\, p\,(1-p) = \frac{2(2m+3)}{m+2}\, p\,(1-p) < 4\,p\,(1-p) \le 1
$$

parce que 2(2m + 3) = 4m + 6 < 4m + 8 = 4(m + 2), et que 4p(1 − p) = 1 − (2p − 1)² ≤ 1. Avec p = 0,7 et m = 0, ce rapport vaut 3 × 0,21 = 0,63, et l'on retrouve 0,084 × 0,63 = 0,05292.

Le vote a donc lui aussi des rendements décroissants, et il part de plus bas : à p = 0,7 et N = 5, il atteint 0,837, quand le best-of-5 avec vérificateur parfait atteint 1 − 0,3⁵ = 0,998.

### 6. Avec des réponses fausses variées, la pluralité fait au moins aussi bien

En pratique, les réponses fausses se dispersent : trois essais faux donnent souvent trois montants différents. L'agent garde alors la réponse la plus fréquente (la pluralité), qui peut l'emporter sans majorité absolue.

Si la réponse juste a strictement plus de N/2 voix, les autres réponses se partagent moins de N/2 voix, donc chacune en a moins qu'elle. La majorité stricte entraîne ainsi la victoire à la pluralité :

$$
P(\text{pluralité juste}) \;\ge\; P_{maj}(N)
$$

La formule binomiale est donc une borne basse. Elle est atteinte quand il n'existe qu'une seule réponse fausse possible, comme pour un oui ou un non.

La simulation le confirme. Sur 2 000 tâches et à N = 15, le vote binaire donne 0,758 et la pluralité 0,851. Sur les tâches difficiles, les erreurs se répartissent entre trois valeurs et ne s'accordent pas entre elles.

### 7. Le coût est linéaire en N

Chaque essai renvoie le même prompt (N_in tokens) et génère sa propre réponse (N_out tokens). Les tokens de réflexion font partie de N_out : ils sont facturés comme des tokens de sortie, même quand l'API ne les affiche pas.

Avec les prix illustratifs de l'étape 72 (P_in = 3 USD et P_out = 15 USD par million de tokens) et un essai de 2 000 tokens d'entrée et 1 500 de sortie :

$$
C_1 = 2\,000 \times 3 \cdot 10^{-6} + 1\,500 \times 15 \cdot 10^{-6} = 0{,}006 + 0{,}0225 = 0{,}0285 \text{ USD} = 0{,}10466625 \text{ AED}
$$

**En parallèle**, les N essais coûtent C(N) = N C₁, soit 0,5233 AED pour N = 5. Le cache du préfixe (étape 72) fait payer l'entrée des N − 1 essais suivants au facteur de lecture, mais il ne touche pas la sortie : le coût reste linéaire en N, avec une pente un peu plus faible.

**En séquentiel**, avec arrêt au premier essai accepté, le coût moyen est plus faible, parce que l'essai i n'est payé que si les i − 1 premiers ont été rejetés :

$$
\mathbb{E}[\text{essais payés}] = \sum_{i=1}^{N} a^{i-1} = \frac{1 - a^N}{1 - a}
$$

Avec un vérificateur parfait, p = 0,4 et N = 5, on a a = 0,6. Cela fait 1 + 0,6 + 0,36 + 0,216 + 0,1296 = 2,3056 essais en moyenne, soit 0,2413 AED au lieu de 0,5233. Le séquentiel échange du coût contre de la latence : jusqu'à cinq appels l'un après l'autre, au lieu d'un seul tour d'appels parallèles.

Dans ce mode, autoriser un N-ième essai rapporte V p aᴺ⁻¹ et coûte en moyenne C₁ aᴺ⁻¹. Le rapport entre gain et coût ne dépend plus de N : si V p ≥ C₁, c'est la latence acceptable qui fixe N, et non le coût.

La suite raisonne sur le mode parallèle. C'est le plus courant quand le temps de réponse compte, et c'est celui d'un vote, qui a besoin de tous ses bulletins (sauf arrêt anticipé, voir « Pour aller plus loin »).

### 8. Le N* qui maximise la valeur moins le coût

Le gain net de N essais parallèles vaut G(N) = V P_N − N C₁, avec G(0) = 0. Son accroissement est :

$$
G(N) - G(N-1) = V\,\Delta(N) - C_1 = V\,p\,(1-p)^{N-1} - C_1
$$

D'après le point 2, cet accroissement décroît avec N. G monte donc tant que l'accroissement est positif, puis descend à chaque pas. La suite est unimodale, et son maximum est atteint au dernier N dont l'accroissement est encore positif ou nul.

Pour trouver ce N, on prend le logarithme, qui est croissant, puis on divise par ln(1 − p), qui est négatif, ce qui retourne le sens de l'inégalité :

$$
V p (1-p)^{N-1} \ge C_1 \iff (N-1)\ln(1-p) \ge \ln\frac{C_1}{V p} \iff N - 1 \le \frac{\ln\bigl(C_1/(V p)\bigr)}{\ln(1-p)}
$$

Le plus grand entier N qui vérifie cette condition est la formule de N*. Si V p < C₁, même le premier essai coûte plus qu'il ne rapporte : N* = 0, et la tâche part directement vers un humain ou vers une règle.

Avec V = 3 AED et C₁ = 0,10466625 AED :

- **Tâche difficile, p = 0,4.** On calcule ln(0,10466625 / 1,2) / ln 0,6 = (−2,4393)/(−0,5108) = 4,775, donc N* = 1 + 4 = 5. Le 5ᵉ essai rapporte 3 × 0,4 × 0,6⁴ = 0,1555 AED, mais le 6ᵉ seulement 0,0933 AED, moins que son coût.
- **Tâche facile, p = 0,95.** On calcule ln(0,10466625 / 2,85) / ln 0,05 = (−3,3043)/(−2,9957) = 1,103, donc N* = 2. Le 2ᵉ essai rapporte 3 × 0,95 × 0,05 = 0,1425 AED, mais le 3ᵉ seulement 0,0071 AED.

La forme fermée montre aussi comment N* réagit à la valeur. Doubler V ajoute ln 2 / (−ln(1 − p)) essais, soit environ 1,36 essai pour p = 0,4 : N* croît comme le logarithme de V/C₁.

### 9. Le routage adaptatif ne peut pas faire moins bien qu'un budget uniforme

Le trafic contient une part π_d de tâches difficiles. Une politique uniforme donne le même N à toutes les tâches ; une politique adaptative choisit un N_f pour les faciles et un N_d pour les difficiles. La politique uniforme est le cas particulier N_f = N_d. Or le maximum sur un ensemble plus grand est au moins aussi grand : c'est l'inégalité de l'équation complète.

De plus, le gain mélangé est une somme pondérée d'un terme qui ne dépend que de N_f et d'un terme qui ne dépend que de N_d. On le maximise donc terme à terme : chaque classe reçoit son propre N*. Avec π_d = 0,3 :

| Politique | N facile | N difficile | Essais par tâche | Justesse | Gain net (AED par tâche) |
|---|---|---|---|---|---|
| uniforme | 3 | 3 | 3,0 | 0,9351 | 2,4913 |
| adaptative | 2 | 5 | 2,9 | 0,9749 | 2,6212 |

La politique adaptative fait moins d'essais en moyenne et gagne quatre points de justesse. Elle retire aux tâches faciles un troisième essai inutile et en donne deux de plus aux difficiles.

Encore faut-il que le routeur se trompe peu :

- une tâche facile envoyée en « difficile » paie trois essais superflus ;
- une tâche difficile envoyée en « facile » perd P₅ − P₂ = 0,28224 de probabilité de succès.

La matrice de confusion du routeur (étape 51) entre donc dans le calcul du gain.

### 10. Le p moyen surestime le gain (Jensen)

La fonction x ↦ 1 − (1 − x)ᴺ est concave sur [0, 1], puisque sa dérivée seconde, −N(N − 1)(1 − x)ᴺ⁻², est négative ou nulle. L'inégalité de Jensen dit qu'une moyenne de valeurs d'une fonction concave est inférieure à la valeur de la fonction en la moyenne. Calculer P_N avec le p moyen surestime donc la justesse.

Ici, le p moyen vaut 0,7 × 0,95 + 0,3 × 0,4 = 0,785. Le pass@3 prédit vaut alors 1 − 0,215³ = 0,9901, alors que la vraie valeur est 0,9351. C'est la même raison qu'au point 5 de l'étape 60 pour pass^k : on calcule tâche par tâche, ou classe par classe, puis on fait la moyenne. La colonne « théorie » de la simulation est calculée ainsi, et la mesure la rejoint : 0,9010 mesuré contre 0,9077 prédit à N = 3.

### 11. Profondeur ou largeur : l'effort de réflexion

L'effort de réflexion n'a pas de formule universelle : le lien entre tokens de réflexion et p se mesure sur ses propres tâches. Le tableau suivant porte sur une autre famille de tâches (l'analyse de clauses), avec les mêmes 2 000 tokens d'entrée. Les chiffres sont illustratifs.

| Effort | Tokens de sortie | p | Coût d'un essai (AED) | Gain net (AED) |
|---|---|---|---|---|
| low | 600 | 0,52 | 0,0551 | 1,5049 |
| medium | 1 500 | 0,64 | 0,1047 | 1,8153 |
| high | 4 000 | 0,72 | 0,2424 | 1,9176 |
| xhigh | 9 000 | 0,76 | 0,5178 | 1,7622 |
| max | 20 000 | 0,78 | 1,1238 | 1,2162 |

Le gain de justesse par token supplémentaire vaut 0,12 / 900 ≈ 1,33 × 10⁻⁴, puis 3,2 × 10⁻⁵, puis 8 × 10⁻⁶, puis 1,8 × 10⁻⁶. Il décroît : la courbe est concave, et le meilleur effort seul est high.

Mais trois essais en low, avec un vérificateur parfait, donnent 1 − 0,48³ = 0,8894 pour 3 × 600 = 1 800 tokens de sortie, et un gain net de 2,5030 AED : mieux que high seul. Sans vérificateur, un vote de trois essais en medium donne 0,7045 et 1,7995 AED : moins bien que high.

La leçon tient en une phrase. Avec un vérificateur fiable, la largeur bat la profondeur ; sans vérificateur, c'est la profondeur qui gagne, et le vote n'aide que si p > 1/2. Les nombres sont illustratifs ; c'est la méthode de calcul qui se réutilise.

### 12. Exemple fait à la main (le code reprend ces nombres)

Tâche difficile, avec p = 0,4, V = 3 AED et C₁ = 0,1047 AED :

| N | P_N | Gain du N-ième essai | Valeur de ce gain (AED) | Gain net G(N) (AED) |
|---|---|---|---|---|
| 1 | 0,4 | 0,4 | 1,2 | 1,0953 |
| 2 | 0,64 | 0,24 | 0,72 | 1,7107 |
| 3 | 0,784 | 0,144 | 0,432 | 2,0380 |
| 4 | 0,8704 | 0,0864 | 0,2592 | 2,1925 |
| 5 | 0,92224 | 0,05184 | 0,15552 | 2,2434 |
| 6 | 0,953344 | 0,031104 | 0,093312 | 2,2320 |

La valeur du 6ᵉ gain (0,0933 AED) est inférieure à C₁ (0,1047 AED) : G redescend de 2,2434 à 2,2320, et N* = 5.

## Effets et comportement

- **Plus p est grand, plus N* est petit.** Une tâche facile se règle en un ou deux essais : à p = 0,95, le troisième essai rapporte 0,007 AED pour 0,105 AED de coût.
- **N* croît comme le logarithme de V/C₁.** Doubler la valeur d'une tâche ajoute environ 1,36 essai à p = 0,4. Diviser le coût d'un essai par 10 (cache, modèle plus petit) en ajoute environ ln 10 / 0,511 ≈ 4,5.
- **Le vote n'aide que si p > 1/2.** Sur les tâches difficiles, il amplifie l'erreur. Dans la simulation, le vote binaire baisse de 0,7725 à N = 3 à 0,7580 à N = 15, tandis que le best-of-N avec vérificateur passe de 0,9010 à 0,9985.
- **Un vérificateur imparfait fait monter la couverture, pas la précision.** Le plafond de la justesse est la précision du vérificateur : pour monter plus haut, il faut améliorer le vérificateur, pas ajouter des essais.
- **L'effort a lui aussi des rendements décroissants.** Sur `claude-opus-5-5`, il prend cinq niveaux, de `low` à `max`, avec `medium` par défaut. Un effort élevé allonge aussi le temps avant le premier token (étape 33 bis).
- **Parallèle ou séquentiel, c'est un choix de latence.** Le parallèle garde la latence d'un seul appel mais consomme N fois le débit autorisé. Le séquentiel coûte moins en moyenne mais additionne les temps de réponse.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| p | `p` |
| N | `n` |
| P_N (pass@N) | `best_of_n(p, n)` |
| Δ(N) | la liste `gains` |
| v₊, v₋, a | `v_plus`, `v_moins`, `rejet` |
| P_juste, P_faux, P_esc | `best_of_n_verifie(p, n, v_plus, v_moins)` |
| P_maj(N) | `vote_majoritaire(p, n)` |
| incrément de N à N + 2 | `increment_vote(p, m)` |
| pluralité | `pluralite(reponses)` |
| C₁ | `cout_essai_aed(tokens_in, tokens_out)` |
| V | `valeur` |
| G(N) | `gain_net(p, n, valeur, cout)` |
| N* | `n_etoile(...)`, `n_etoile_formule(...)` |
| tâches simulées | `tirer_taches(...)`, `simuler(...)` |

### Déroulé, ligne par ligne

**Les constantes.** `USD_EN_AED = 3.6725` est la parité fixe de l'AED. `PRIX_IN = 3.00 / 1_000_000` et `PRIX_OUT = 15.00 / 1_000_000` sont les prix illustratifs de l'étape 72, en USD par token. La sortie coûte cinq fois l'entrée, et c'est là que tombent les tokens de réflexion.

**`verifier_proba(x)`** lève `ValueError` si une probabilité sort de [0, 1]. Une probabilité de 1,2 viendrait d'une erreur de calcul en amont. Mieux vaut l'arrêter que la propager.

**`cout_essai_aed(tokens_in, tokens_out)`** calcule C₁ = N_in P_in + N_out P_out, puis le convertit en AED. Avec `(2000, 1500)`, on a 2 000 × 3 × 10⁻⁶ = 0,006 USD et 1 500 × 15 × 10⁻⁶ = 0,0225 USD. Le total, 0,0285 USD, multiplié par 3,6725, donne 0,10466625 AED.

**`best_of_n(p, n)`** renvoie `1.0 - (1.0 - p) ** n`. Pour `p = 0.4` et `n = 3`, on a `0.6 ** 3 = 0.216` et le résultat vaut 0,784. Pour `n = 0`, il vaut 0 : sans essai, aucune réponse.

**`best_of_n_verifie(p, n, v_plus, v_moins)`** suit le point 3.

- `accepte_juste = p * v_plus` vaut 0,36. `accepte_faux = (1 - p) * v_moins` vaut 0,06. `rejet = 1 - 0.36 - 0.06` vaut 0,58.
- La garde `if rejet == 1.0` traite le vérificateur qui n'accepte jamais rien. Sans elle, la ligne suivante diviserait par zéro. Dans ce cas, la fonction renvoie `(0.0, 0.0, 1.0)` : tout part en escalade.
- `somme = (1 - rejet ** n) / (1 - rejet)` est la série géométrique 1 + a + ⋯ + aᴺ⁻¹. Pour `n = 3`, elle vaut 0,804888 / 0,42 = 1,9164.
- La fonction renvoie `(0.36 × 1.9164, 0.06 × 1.9164, 0.58 ** 3)`, soit 0,689904, 0,114984 et 0,195112.

**`vote_majoritaire(p, n)`** refuse un `n` pair : avec un nombre pair de votes, une égalité n'aurait pas de vainqueur. La somme parcourt `range((n + 1) // 2, n + 1)`. Pour `n = 3`, elle prend k = 2 puis k = 3, avec `math.comb(3, 2) = 3`, ce qui donne 3 × 0,49 × 0,3 + 0,343 = 0,784.

**`increment_vote(p, m)`** écrit la formule du point 5. Pour `p = 0.7` et `m = 1`, on a `math.comb(3, 1) = 3` et `(0.21) ** 2 = 0.0441`. Avec le facteur 2p − 1 = 0,4, l'incrément vaut 0,05292.

**`gain_net(p, n, valeur, cout)`** renvoie `valeur * best_of_n(p, n) - n * cout`. Le coût est multiplié par `n`, puisqu'en parallèle on paie chaque essai.

**`n_etoile(p, valeur, cout)`** part de `n = 0`. À chaque tour, il compare le gain marginal de l'essai `n + 1`, `valeur * p * (1 - p) ** n`, au coût d'un essai. Pour p = 0,4, on obtient 1,2, puis 0,72, puis 0,432, puis 0,2592, puis 0,1555, toutes valeurs ≥ 0,1047 : n monte jusqu'à 5. Le gain suivant, 0,0933, est trop petit, et la fonction renvoie 5. La garde `cout <= 0` refuse un essai gratuit, qui rendrait la boucle infinie.

**`n_etoile_formule(p, valeur, cout)`** écrit la forme fermée.

- Elle renvoie 0 si V p < C₁.
- Elle renvoie 1 si p = 1, puisque ln 0 n'existe pas et qu'un essai suffit.
- Sinon, elle renvoie `1 + math.floor(math.log(cout / (valeur * p)) / math.log(1 - p))`.

Pour p = 0,4, le rapport vaut 4,775, et la fonction renvoie 1 + 4 = 5.

**`tirer_taches(n_taches, part_difficile, graine)`** crée son propre générateur, `random.Random(graine)`, qui ne touche pas à l'état global du module `random`. Chaque tâche est difficile avec la probabilité 0,3 ; son p est alors tiré entre 0,15 et 0,55. Les autres tâches sont faciles, avec un p entre 0,85 et 0,99.

**`pluralite(reponses)`** compte les réponses dans un dictionnaire, puis prend le maximum selon la clé `(comptes[r], -reponses.index(r))`.

- En cas d'égalité, la réponse apparue la première l'emporte. Avec `[2, 0, 2, 0]`, la fonction renvoie 2.
- Cette règle est neutre : elle ne favorise pas la bonne réponse, qui vaut 0 dans la simulation.

**`simuler(taches, n_liste, graine)`** tire une seule fois, pour chaque tâche, `n_max = 15` réponses : 0 si l'essai est juste, sinon une des trois valeurs fausses 1, 2 ou 3. Pour chaque N, elle ne regarde que les N premières réponses (`reponses[:n]`). Ce sont donc les mêmes essais qui servent à tous les N, comme pour un agent qui se serait arrêté plus tôt. Elle compte trois succès par tâche : au moins un essai juste (best-of-N), plus de la moitié de justes (vote binaire), et la pluralité égale à 0.

**`main()`**, bloc par bloc.

1. Le programme calcule `best_of_n(0.4, n)` pour n de 1 à 5 et vérifie les valeurs du point 1. Les `gains` (0,4 ; 0,24 ; 0,144…) sont comparés à `0.4 * 0.6 ** k`, et l'on vérifie qu'ils décroissent (point 2).
2. Le vérificateur imparfait est appelé à N = 3 puis à N = 10. Le programme vérifie que les trois probabilités somment à 1, que la précision vaut exactement 6/7 dans les deux cas, et que les trois valeurs à N = 3 sont celles du point 3. Avec `v_plus = 1.0` et `v_moins = 0.0`, on retrouve `best_of_n(0.4, 3)`.
3. Le vote est calculé pour p = 0,7 et p = 0,4. Pour quatre valeurs de p et six valeurs de m, la différence réelle `vote_majoritaire(p, 2m + 3) - vote_majoritaire(p, 2m + 1)` doit égaler `increment_vote(p, m)` à 10⁻¹² près, et les incréments doivent décroître en valeur absolue. À p = 0,5, le vote vaut 0,5 pour tout N.
4. `c1` vaut 0,10466625 AED. On calcule ensuite le nombre moyen d'essais payés en séquentiel, avec a = 0,6 et N = 5. La somme directe `1 + 0.6 + 0.36 + 0.216 + 0.1296` doit égaler la forme fermée, soit 2,3056.
5. Pour chaque classe, trois calculs de N* doivent coïncider : la boucle de `n_etoile`, la forme fermée, et une recherche exhaustive du maximum de `gain_net` sur N de 0 à 29. On obtient 2 et 5. À p = 0,03, V p = 0,09 < 0,1047 : N* = 0.
6. La fonction locale `melange(n_f, n_d)` calcule la justesse et le gain du trafic mélangé. Le meilleur N uniforme est 3, avec un gain de 2,4913 AED. La politique (2, 5) donne 2,6212 AED, et une recherche exhaustive sur toutes les paires de 1 à 11 confirme qu'aucune autre ne fait mieux. La dernière ligne compare le pass@3 du p moyen (0,9901) à la vraie valeur (0,9351).
7. La simulation porte sur 2 000 tâches. Pour chaque N, le programme affiche les trois taux mesurés, la valeur théorique moyenne et le gain net. Il vérifie que la pluralité gagne au moins aussi souvent que le vote binaire (point 6), et que la mesure s'écarte de moins de 0,03 de la théorie, pour le best-of-N comme pour le vote. Il cherche enfin le meilleur N uniforme (3) et le meilleur N par classe (2 et 6).
8. Le tableau des efforts est vérifié concave, puis le programme compare le meilleur effort seul (high), la largeur avec vérificateur (2,5030) et le vote en medium (1,7995).
9. Deux entrées invalides, p = 1,2 et n = −1, doivent lever `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`verifier_proba(x)`** — Cette fonction est le contrôleur à l'entrée du laboratoire, qui refuse toute éprouvette mal étiquetée : elle reçoit un nombre, ne renvoie rien s'il est compris entre 0 et 1 inclus, et lève une `ValueError` dans le cas contraire, car une probabilité de 1,2 trahirait une erreur de calcul en amont qu'il vaut mieux arrêter que propager. `best_of_n`, `best_of_n_verifie` et `vote_majoritaire` l'appellent avant tout calcul, et c'est elle qui fait échouer, dans la dernière section de `main`, l'appel avec p = 1,2.

**`best_of_n(p, n)`** — Celle-ci répond à la question d'un chercheur d'or qui creuse n trous indépendants, chacun avec la chance p de trouver un filon : elle reçoit p et n, fait vérifier p par `verifier_proba`, lève une `ValueError` si n est négatif, puis renvoie 1 − (1 − p)ⁿ, la probabilité qu'au moins un essai soit juste quand un vérificateur parfait reconnaît la bonne réponse, autrement dit le pass@N. Pour p = 0,4, elle donne 0,4, 0,64, 0,784, 0,8704 puis 0,92224 pour N = 1 à 5, et 0 quand n = 0, puisque sans essai il n'y a aucune réponse.

**`best_of_n_verifie(p, n, v_plus, v_moins)`** — Cette fonction remplace le vérificateur parfait par un contrôleur faillible, comme un jury qui accepte parfois une copie fausse et rejette parfois une juste : elle reçoit p, n, la probabilité d'accepter un essai juste et celle d'accepter un essai faux, les vérifie, calcule la probabilité qu'un essai soit accepté juste, accepté faux ou rejeté, renvoie (0, 0, 1) si le vérificateur n'accepte jamais rien, et sinon multiplie les deux premières par la série géométrique 1 + a + ⋯ + aⁿ⁻¹ des rejets successifs. Elle renvoie le triplet des probabilités de livrer juste, de livrer faux et d'escalader ; pour p = 0,4, v⁺ = 0,9, v⁻ = 0,1 et N = 3, ce sont 0,689904, 0,114984 et 0,195112, avec une précision de 6/7 qui ne dépend pas de N.

**`increment_vote(p, m)`** — Celle-ci mesure ce que rapportent deux votants de plus dans une assemblée qui décide à la majorité : elle reçoit la probabilité p qu'un vote soit juste et l'indice m, et renvoie C(2m + 1, m) × (p(1 − p))ᵐ⁺¹ × (2p − 1), l'écart exact entre la probabilité de majorité juste avec 2m + 3 votes et avec 2m + 1 votes. Le facteur 2p − 1 dit tout : l'incrément est positif si p > 1/2, nul si p = 1/2 et négatif sinon ; pour p = 0,7 et m = 1, il vaut 0,05292, et `main` vérifie l'égalité à 10⁻¹² près pour quatre valeurs de p et six valeurs de m.

**`gain_net(p, n, valeur, cout)`** — Cette fonction est le contrôleur de gestion qui met en balance ce que rapportent les essais et ce qu'ils coûtent : elle reçoit p, le nombre d'essais n, la valeur d'une tâche réussie et le coût d'un essai, et renvoie la valeur multipliée par `best_of_n(p, n)`, moins n fois le coût, puisqu'en parallèle on paie chaque essai. Avec une valeur de 3 AED et un essai à 0,10466625 AED, elle donne 2,7832 AED pour une tâche facile à p = 0,95 avec 2 essais, et 2,2434 AED pour une tâche difficile à p = 0,4 avec 5 essais ; `main` la maximise par recherche exhaustive pour contrôler N*.

**`n_etoile_formule(p, valeur, cout)`** — Celle-ci donne d'un seul coup de règle le nombre d'essais que `n_etoile` trouve pas à pas : elle reçoit p, la valeur et le coût d'un essai, renvoie 0 si V × p est inférieur au coût, car même le premier essai ne se paie pas, renvoie 1 si p vaut 1, car le logarithme de 0 n'existe pas et un essai suffit, et sinon 1 plus la partie entière de ln(C₁/(Vp)) / ln(1 − p). Pour p = 0,4, ce rapport vaut 4,775, d'où N* = 5 ; pour p = 0,95, elle renvoie 2, et pour p = 0,03, où V × p = 0,09 reste sous 0,1047, elle renvoie 0.

**`pluralite(reponses)`** — Cette fonction est le scrutateur d'un vote à la pluralité, où gagne la réponse la plus citée même sans majorité absolue : elle reçoit la liste des réponses, compte chacune dans un dictionnaire, puis renvoie celle qui a le plus de voix, en départageant une égalité par l'ordre de première apparition, une règle neutre qui ne favorise pas la bonne réponse. Avec 2, 0, 2, 0, elle renvoie 2 ; dans la simulation, où 0 est la bonne réponse et 1, 2 et 3 les fausses, elle gagne au moins aussi souvent que le vote binaire, car les erreurs se dispersent.

**`main()`** — C'est le directeur financier qui instruit le dossier du budget de raisonnement en neuf temps : il vérifie d'abord les valeurs de pass@N à p = 0,4 et la décroissance de leurs gains, puis le vérificateur imparfait à N = 3 et N = 10, le vote majoritaire et son incrément exact, et le coût d'un essai, 0,10466625 AED, avec les 2,3056 essais payés en moyenne en séquentiel. Il calcule ensuite N*, 2 pour les tâches faciles et 5 pour les difficiles, compare le routage adaptatif (2, 5) au meilleur N uniforme, simule 2 000 tâches avec une graine fixe, compare profondeur et largeur de réflexion, et termine en vérifiant que p = 1,2 et n = −1 sont refusés ; chaque résultat est verrouillé par un `assert`.

**`melange(n_f, n_d)`** — Cette fonction interne, qui vit dans `main`, est le planificateur qui chiffre une politique de routage où les tâches faciles et difficiles ne reçoivent pas le même nombre d'essais : elle reçoit le nombre d'essais accordé aux faciles et aux difficiles, calcule la justesse moyenne d'un trafic composé de 70 % de tâches faciles à p = 0,95 et de 30 % de difficiles à p = 0,40, puis le gain net, trois fois cette justesse moins le coût moyen des essais. Elle renvoie ce couple ; le meilleur N uniforme, 3, donne 2,4913 AED, et la politique (2, 5) donne 2,6212 AED, qu'aucune autre paire de 1 à 11 ne dépasse.

```python
"""Étape 72 quinquies — budget de raisonnement : best-of-N, vote majoritaire, coût linéaire, N*, routage."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

USD_EN_AED = 3.6725            # parité fixe de l'AED
PRIX_IN = 3.00 / 1_000_000     # USD par token d'entrée (illustratif, comme à l'étape 72)
PRIX_OUT = 15.00 / 1_000_000   # USD par token de sortie, réflexion comprise (illustratif)


def verifier_proba(x: float) -> None:
    if not 0.0 <= x <= 1.0:
        raise ValueError("une probabilité doit être dans [0, 1]")


def cout_essai_aed(tokens_in: int, tokens_out: int) -> float:
    """C1 = N_in·P_in + N_out·P_out, en AED. Les tokens de réflexion sont facturés comme sortie."""
    if tokens_in < 0 or tokens_out < 0:
        raise ValueError("un nombre de tokens ne peut pas être négatif")
    return (tokens_in * PRIX_IN + tokens_out * PRIX_OUT) * USD_EN_AED


def best_of_n(p: float, n: int) -> float:
    """Vérificateur parfait : P(au moins un essai juste sur n) = 1 − (1 − p)^n, c'est-à-dire pass@n."""
    verifier_proba(p)
    if n < 0:
        raise ValueError("il faut n >= 0")
    return 1.0 - (1.0 - p) ** n


def best_of_n_verifie(p: float, n: int, v_plus: float, v_moins: float) -> tuple[float, float, float]:
    """Vérificateur imparfait : on livre le premier essai accepté, sinon on escalade.
    Renvoie (P(juste livré), P(faux livré), P(escalade))."""
    for x in (p, v_plus, v_moins):
        verifier_proba(x)
    accepte_juste = p * v_plus
    accepte_faux = (1 - p) * v_moins
    rejet = 1 - accepte_juste - accepte_faux
    if rejet == 1.0:                              # le vérificateur n'accepte jamais rien
        return 0.0, 0.0, 1.0
    somme = (1 - rejet ** n) / (1 - rejet)        # 1 + a + a² + … + a^(n−1)
    return accepte_juste * somme, accepte_faux * somme, rejet ** n


def vote_majoritaire(p: float, n: int) -> float:
    """P(plus de la moitié des n votes sont justes), loi binomiale ; n impair."""
    verifier_proba(p)
    if n < 1 or n % 2 == 0:
        raise ValueError("il faut un nombre de votes impair >= 1")
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range((n + 1) // 2, n + 1))


def increment_vote(p: float, m: int) -> float:
    """P_maj(2m + 3) − P_maj(2m + 1) = C(2m+1, m)·(p(1 − p))^(m+1)·(2p − 1)."""
    return math.comb(2 * m + 1, m) * (p * (1 - p)) ** (m + 1) * (2 * p - 1)


def gain_net(p: float, n: int, valeur: float, cout: float) -> float:
    """G(N) = V·P_N − N·C1 : valeur attendue moins coût, en AED par tâche."""
    return valeur * best_of_n(p, n) - n * cout


def n_etoile(p: float, valeur: float, cout: float, n_max: int = 64) -> int:
    """Ajoute des essais tant que le gain marginal V·p(1 − p)^N couvre le coût d'un essai de plus."""
    if cout <= 0:
        raise ValueError("un essai gratuit rendrait N* infini")
    n = 0
    while n < n_max and valeur * p * (1 - p) ** n >= cout:
        n += 1
    return n


def n_etoile_formule(p: float, valeur: float, cout: float) -> int:
    """N* = 0 si V·p < C1, sinon 1 + ⌊ln(C1 / (V·p)) / ln(1 − p)⌋."""
    if valeur * p < cout:
        return 0
    if p == 1.0:
        return 1
    return 1 + math.floor(math.log(cout / (valeur * p)) / math.log(1 - p))


def tirer_taches(n_taches: int, part_difficile: float, graine: int) -> list[tuple[str, float]]:
    """Chaque tâche a sa propre probabilité de succès p ; les difficiles sont sous 1/2 la plupart du temps."""
    rng = random.Random(graine)
    taches = []
    for _ in range(n_taches):
        if rng.random() < part_difficile:
            taches.append(("difficile", rng.uniform(0.15, 0.55)))
        else:
            taches.append(("facile", rng.uniform(0.85, 0.99)))
    return taches


def pluralite(reponses: list[int]) -> int:
    """Réponse la plus fréquente ; une égalité est départagée par la première apparition (règle neutre)."""
    comptes: dict[int, int] = {}
    for r in reponses:
        comptes[r] = comptes.get(r, 0) + 1
    return max(comptes, key=lambda r: (comptes[r], -reponses.index(r)))


def simuler(taches: list[tuple[str, float]], n_liste: list[int], graine: int, n_faux: int = 3) -> dict[int, list[int]]:
    """Tire n_max réponses par tâche (0 = juste, 1..n_faux = fausses) et compte les succès des trois stratégies."""
    rng = random.Random(graine)
    n_max = max(n_liste)
    succes = {n: [0, 0, 0] for n in n_liste}      # best-of-N, vote binaire, pluralité
    for _, p in taches:
        reponses = [0 if rng.random() < p else rng.randrange(1, n_faux + 1) for _ in range(n_max)]
        for n in n_liste:
            premiers = reponses[:n]                  # les mêmes essais servent à tous les N
            justes = premiers.count(0)
            succes[n][0] += justes > 0
            succes[n][1] += justes > n / 2
            succes[n][2] += pluralite(premiers) == 0
    return succes


def main() -> None:
    print("1. Best-of-N avec vérificateur parfait = pass@N (p = 0.4)")
    bo = [best_of_n(0.4, n) for n in range(1, 6)]
    print("  N = 1..5 : " + "  ".join(f"{x:.4f}" for x in bo))
    assert [round(x, 5) for x in bo] == [0.4, 0.64, 0.784, 0.8704, 0.92224]
    gains = [b - a for a, b in zip([0.0] + bo, bo)]
    assert all(abs(g - 0.4 * 0.6 ** k) < 1e-12 for k, g in enumerate(gains))   # Δ(N) = p(1 − p)^(N−1)
    assert all(g1 > g2 for g1, g2 in zip(gains, gains[1:]))                      # concave

    print("2. Vérificateur imparfait (p = 0.4, v+ = 0.9, v- = 0.1)")
    for n in (3, 10):
        juste, faux, escalade = best_of_n_verifie(0.4, n, 0.9, 0.1)
        print(f"  N = {n:>2} : juste {juste:.4f}  faux {faux:.4f}  escalade {escalade:.4f}"
              f"  précision {juste / (juste + faux):.4f}")
        assert abs(juste + faux + escalade - 1) < 1e-12
        assert abs(juste / (juste + faux) - 6 / 7) < 1e-12                       # ne dépend pas de N
    juste3, faux3, esc3 = best_of_n_verifie(0.4, 3, 0.9, 0.1)
    assert (round(juste3, 6), round(faux3, 6), round(esc3, 6)) == (0.689904, 0.114984, 0.195112)
    assert best_of_n_verifie(0.4, 3, 1.0, 0.0)[0] == best_of_n(0.4, 3)          # cas parfait retrouvé
    print(f"  plafond de la part juste quand N grandit : {0.36 / 0.42:.4f}")

    print("3. Vote majoritaire (loi binomiale)")
    for p in (0.7, 0.4):
        v = [vote_majoritaire(p, n) for n in (1, 3, 5)]
        print(f"  p = {p} : N = 1, 3, 5 -> " + "  ".join(f"{x:.4f}" for x in v))
    assert round(vote_majoritaire(0.7, 3), 6) == 0.784 and round(vote_majoritaire(0.7, 5), 5) == 0.83692
    assert round(vote_majoritaire(0.4, 3), 6) == 0.352 and round(vote_majoritaire(0.4, 5), 5) == 0.31744
    for p in (0.7, 0.4, 0.5, 0.52):
        for m in range(6):
            reel = vote_majoritaire(p, 2 * m + 3) - vote_majoritaire(p, 2 * m + 1)
            assert abs(reel - increment_vote(p, m)) < 1e-12
            if m:
                assert abs(increment_vote(p, m)) <= abs(increment_vote(p, m - 1))   # rendements décroissants
    assert all(abs(vote_majoritaire(0.5, n) - 0.5) < 1e-12 for n in (1, 3, 5, 7, 9))
    print("  incrément exact N -> N + 2 vérifié pour p = 0.7, 0.4, 0.5, 0.52 et m = 0..5")

    print("4. Le coût est linéaire en N")
    c1 = cout_essai_aed(2000, 1500)
    print(f"  un essai : 2000 tokens d'entrée + 1500 de sortie = {c1 / USD_EN_AED:.4f} USD = {c1:.4f} AED"
          f" ; N = 5 -> {5 * c1:.4f} AED")
    assert abs(c1 - 0.10466625) < 1e-12
    a = 1 - 0.4                                     # vérificateur parfait : un essai est rejeté s'il est faux
    essais_moyens = sum(a ** (i - 1) for i in range(1, 6))
    print(f"  séquentiel, arrêt au premier succès (p = 0.4, N = 5) : {essais_moyens:.4f} essais en moyenne,"
          f" {essais_moyens * c1:.4f} AED")
    assert abs(essais_moyens - (1 - a ** 5) / (1 - a)) < 1e-12 and round(essais_moyens, 4) == 2.3056

    print("5. N* : ajouter des essais tant que le gain marginal couvre leur coût (V = 3 AED)")
    valeur = 3.0
    for nom, p in (("facile", 0.95), ("difficile", 0.40)):
        n_opt = n_etoile(p, valeur, c1)
        meilleur = max(range(0, 30), key=lambda n: gain_net(p, n, valeur, c1))
        print(f"  {nom:<9} p = {p:.2f} : N* = {n_opt} (formule {n_etoile_formule(p, valeur, c1)})"
              f"  gain net {gain_net(p, n_opt, valeur, c1):.4f} AED")
        assert n_opt == meilleur == n_etoile_formule(p, valeur, c1)
    assert n_etoile(0.95, valeur, c1) == 2 and n_etoile(0.40, valeur, c1) == 5
    assert n_etoile(0.03, valeur, c1) == 0                                       # V·p < C1 : ne pas appeler

    print("6. Routage adaptatif (70 % de tâches faciles, 30 % de difficiles)")
    def melange(n_f: int, n_d: int) -> tuple[float, float]:
        justesse = 0.7 * best_of_n(0.95, n_f) + 0.3 * best_of_n(0.40, n_d)
        return justesse, valeur * justesse - (0.7 * n_f + 0.3 * n_d) * c1
    n_unif = max(range(1, 16), key=lambda n: melange(n, n)[1])
    j_u, g_u = melange(n_unif, n_unif)
    j_a, g_a = melange(2, 5)
    print(f"  uniforme N = {n_unif} : justesse {j_u:.4f}, {n_unif:.1f} essais par tâche, gain net {g_u:.4f} AED")
    print(f"  adaptatif (2, 5) : justesse {j_a:.4f}, {0.7 * 2 + 0.3 * 5:.1f} essais par tâche, gain net {g_a:.4f} AED")
    assert n_unif == 3 and round(g_u, 4) == 2.4913 and round(g_a, 4) == 2.6212 and g_a > g_u
    assert max(melange(a, b)[1] for a in range(1, 12) for b in range(1, 12)) == g_a
    p_moyen = 0.7 * 0.95 + 0.3 * 0.40
    print(f"  p moyen {p_moyen:.3f} -> pass@3 prédit {best_of_n(p_moyen, 3):.4f} au lieu de {j_u:.4f} (Jensen)")
    assert best_of_n(p_moyen, 3) > j_u

    print("7. Simulation : 2000 tâches tirées avec une graine fixe")
    taches = tirer_taches(2000, 0.30, graine=725)
    n_liste = [1, 3, 5, 9, 15]
    succes = simuler(taches, n_liste, graine=7250)
    print("   N  tokens  best-of-N  vote  pluralité  théorie  gain net")
    for n in n_liste:
        bo_s, vote_s, plur_s = (s / len(taches) for s in succes[n])
        theorie = sum(best_of_n(p, n) for _, p in taches) / len(taches)
        theorie_vote = sum(vote_majoritaire(p, n) for _, p in taches) / len(taches)
        net = valeur * theorie - n * c1
        print(f"  {n:>2}  {n * 3500:>6}  {bo_s:>9.4f}  {vote_s:.4f}  {plur_s:>9.4f}  {theorie:>7.4f}  {net:>8.4f}")
        assert succes[n][2] >= succes[n][1]                  # majorité stricte => gagnant de la pluralité
        assert abs(bo_s - theorie) < 0.03 and abs(vote_s - theorie_vote) < 0.03
    nets = {n: valeur * sum(best_of_n(p, n) for _, p in taches) / len(taches) - n * c1 for n in range(1, 31)}
    n_sim = max(nets, key=nets.get)
    par_classe = {}
    for classe in ("facile", "difficile"):
        ps = [p for c, p in taches if c == classe]
        par_classe[classe] = max(range(1, 31), key=lambda n: valeur * sum(best_of_n(p, n) for p in ps) / len(ps) - n * c1)
    print(f"  N* uniforme = {n_sim} ; N* par classe : facile {par_classe['facile']}, difficile {par_classe['difficile']}")
    assert par_classe["facile"] < n_sim < par_classe["difficile"]

    print("8. Effort de réflexion : profondeur ou largeur (chiffres illustratifs)")
    efforts = [("low", 600, 0.52), ("medium", 1500, 0.64), ("high", 4000, 0.72), ("xhigh", 9000, 0.76), ("max", 20000, 0.78)]
    pentes = [(p2 - p1) / (t2 - t1) for (_, t1, p1), (_, t2, p2) in zip(efforts, efforts[1:])]
    assert all(a > b for a, b in zip(pentes, pentes[1:]))                         # courbe concave
    nets_effort = {nom: valeur * p - cout_essai_aed(2000, t) for nom, t, p in efforts}
    meilleur_effort = max(nets_effort, key=nets_effort.get)
    print("  gain net par effort : " + "  ".join(f"{k} {v:.4f}" for k, v in nets_effort.items()))
    largeur_verif = valeur * best_of_n(0.52, 3) - 3 * cout_essai_aed(2000, 600)
    largeur_vote = valeur * vote_majoritaire(0.64, 3) - 3 * cout_essai_aed(2000, 1500)
    print(f"  meilleur effort seul : {meilleur_effort} ; 3 essais low + vérificateur : {largeur_verif:.4f}"
          f" ; vote de 3 en medium : {largeur_vote:.4f}")
    assert meilleur_effort == "high" and largeur_verif > nets_effort["high"] > largeur_vote

    for args in ((1.2, 3), (0.5, -1)):
        try:
            best_of_n(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
…
  un essai : 2000 tokens d'entrée + 1500 de sortie = 0.0285 USD = 0.1047 AED ; N = 5 -> 0.5233 AED
  séquentiel, arrêt au premier succès (p = 0.4, N = 5) : 2.3056 essais en moyenne, 0.2413 AED
5. N* : ajouter des essais tant que le gain marginal couvre leur coût (V = 3 AED)
  facile    p = 0.95 : N* = 2 (formule 2)  gain net 2.7832 AED
  difficile p = 0.40 : N* = 5 (formule 5)  gain net 2.2434 AED
6. Routage adaptatif (70 % de tâches faciles, 30 % de difficiles)
  uniforme N = 3 : justesse 0.9351, 3.0 essais par tâche, gain net 2.4913 AED
  adaptatif (2, 5) : justesse 0.9749, 2.9 essais par tâche, gain net 2.6212 AED
  p moyen 0.785 -> pass@3 prédit 0.9901 au lieu de 0.9351 (Jensen)
7. Simulation : 2000 tâches tirées avec une graine fixe
   N  tokens  best-of-N  vote  pluralité  théorie  gain net
   1    3500     0.7455  0.7455     0.7455   0.7486    2.1411
   3   10500     0.9010  0.7725     0.8000   0.9077    2.4092
   5   17500     0.9515  0.7705     0.8220   0.9523    2.3335
   9   31500     0.9840  0.7675     0.8430   0.9842    2.0105
  15   52500     0.9985  0.7580     0.8510   0.9961    1.4183
  N* uniforme = 3 ; N* par classe : facile 2, difficile 6
…
OK — toutes les vérifications sont passées.
```

Le programme montre que le budget de raisonnement se calcule. Le best-of-N avec vérificateur a des rendements décroissants exactement prévisibles. Le vote ne vaut que si p > 1/2, et la pluralité fait mieux que la majorité stricte quand les erreurs se dispersent. Enfin, router les tâches selon leur difficulté donne plus de justesse avec moins d'essais. Dans la simulation, le vote binaire baisse avec N parce que 30 % des tâches ont un p souvent inférieur à 1/2, et le N* des tâches difficiles (6) dépasse celui de l'exemple à la main (5) parce que leur p varie d'une tâche à l'autre.

### Avec l'API Claude : l'effort est un paramètre de l'adaptateur

Le best-of-N et le vote n'exigent rien du fournisseur : il suffit d'appeler N fois le port LLM (`create(...)`) et d'avoir un vérificateur écrit dans le domaine. L'effort de réflexion, lui, est un réglage propre à chaque fournisseur. Comme dans une architecture hexagonale, on le confine dans l'adaptateur. Le domaine demande un niveau (faible, moyen, élevé) ; l'adaptateur Claude le traduit en `output_config={"effort": …}`. L'adaptateur d'un modèle ouvert hébergé chez soi (Jais, Falcon) peut le traduire en nombre maximal de tokens de raisonnement et en température, puisque là, T est entre vos mains (étape 2).

L'adaptateur du parcours, recopié tel quel :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`ClaudeLLM.__init__(model, effort)`** — Le constructeur installe l'interprète qui traduira les demandes du domaine dans la langue de l'API : il reçoit le nom du modèle, « claude-opus-5-5 » par défaut, et le niveau d'effort, « medium » par défaut, crée un client `anthropic.Anthropic()`, qui lit la clé d'API ou le profil d'authentification comme l'indique le commentaire, puis range le modèle et l'effort. Il ne renvoie rien ; c'est le seul endroit où l'effort de réflexion entre dans le programme, si bien que le domaine demande un niveau sans jamais connaître le réglage propre au fournisseur.

**`ClaudeLLM.create(system, messages, tools)`** — Cette méthode est le guichet qui envoie la requête au vrai modèle avec exactement la même interface que `FakeLLM.create` : elle reçoit, par mots-clés seulement, le prompt système, l'historique et les schémas d'outils, appelle `self.client.beta.messages.create` avec le modèle choisi, un plafond de 16 000 tokens de sortie, ces trois éléments, l'effort placé dans `output_config`, ainsi que l'option bêta et le paramètre `fallbacks` qui prévoient un modèle de repli en cas de refus. Si la réponse est un refus accompagné de détails, elle en imprime la catégorie et l'explication ; dans tous les cas, elle renvoie la réponse telle quelle, que `executer_agent` lit sans qu'une seule ligne de la boucle change.

```python
# [extrait] — adaptateur Claude, non exécuté par le harnais (pip install anthropic + clé API ou `ant auth login`)
import anthropic


class ClaudeLLM:
    """Même interface que FakeLLM : create(system=..., messages=..., tools=...) renvoie une réponse
    qui a .stop_reason et .content (blocs .type, .text, .id, .name, .input). executer_agent() ne change pas."""

    def __init__(self, model: str = "claude-opus-5-5", effort: str = "medium"):
        self.client = anthropic.Anthropic()   # lit ANTHROPIC_API_KEY ou le profil créé par `ant auth login`
        self.model = model
        self.effort = effort

    def create(self, *, system: str, messages: list, tools: list):
        reponse = self.client.beta.messages.create(
            model=self.model,
            max_tokens=16000,
            system=system,
            messages=messages,
            tools=tools,                             # [{"name", "description", "input_schema", "strict": True}]
            output_config={"effort": self.effort},   # réflexion adaptative active par défaut sur ce modèle
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",                     # en cas de refus, l'API relance la requête sur un modèle de repli
        )
        if reponse.stop_reason == "refusal" and reponse.stop_details:
            print(f"refus : {reponse.stop_details.category} — {reponse.stop_details.explanation}")
        return reponse


# Schéma d'outil au format de l'API (strict : les arguments respectent exactement le schéma)
SCHEMA_MENSUALITE = {
    "name": "mensualite",
    "description": "Calcule la mensualité d'un prêt amortissable en AED.",
    "input_schema": {
        "type": "object",
        "properties": {
            "principal": {"type": "number"},
            "taux_annuel": {"type": "number"},
            "n_mois": {"type": "integer"},
        },
        "required": ["principal", "taux_annuel", "n_mois"],
        "additionalProperties": False,
    },
    "strict": True,
}

# resultat = executer_agent(ClaudeLLM(), system, question, outils, [SCHEMA_MENSUALITE])
```

Voici ce qu'il faut savoir sur `claude-opus-5-5`, selon l'état de l'API en novembre 2026 (à vérifier dans la documentation de l'éditeur avant tout déploiement) :

- **Niveaux d'effort.** `output_config={"effort": …}` accepte `"low"`, `"medium"`, `"high"`, `"xhigh"` et `"max"`. Sur ce modèle, la valeur par défaut est `"medium"`, d'où le paramètre explicite de l'adaptateur.
- **Réflexion toujours active.** La réflexion adaptative ne se désactive pas : `thinking={"type": "disabled"}` est refusé, tout comme l'ancien budget fixe de tokens de réflexion (`budget_tokens`). L'effort est le seul réglage de profondeur.
- **Facturation de la réflexion.** Les tokens de réflexion sont facturés comme des tokens de sortie, qu'ils soient affichés ou non (ils sont masqués par défaut). Ils comptent dans `reponse.usage.output_tokens`, que le traceur de l'étape 72 quater additionne pour mesurer le coût réel d'un essai.
- **Plafond de sortie.** `max_tokens` plafonne toute la sortie, réflexion comprise. Un plafond trop bas renvoie `stop_reason == "max_tokens"`, que `executer_agent` traduit en statut `"tronque"`.
- **Diversité des essais.** `temperature`, `top_p` et `top_k` sont refusés (étape 2). Les N essais diffèrent parce que le modèle échantillonne, mais on ne règle pas cette diversité.
- **Règles de l'adaptateur.** Les notes de l'adaptateur valent toujours : pas de `tool_choice` forcé ; tous les `tool_result` dans un seul message ; `reponse.content` recopié tel quel, blocs de réflexion compris ; un refus traité avant de lire le contenu.

Le contrôleur de budget se pose au-dessus de ce port. Seule sa première ligne utile connaît l'adaptateur Claude : pour changer de fournisseur, on change cette ligne, pas la stratégie.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`repondre(question, classe, verifier, system, outils, schemas)`** — Cette fonction est le contrôleur de budget, le régisseur qui décide combien de temps et combien d'essais une question mérite avant de la confier au modèle : elle reçoit la question, sa classe de difficulté, une fonction de vérification écrite dans le domaine, le prompt système, les outils et leurs schémas, lit dans `BUDGETS` l'effort et le nombre d'essais de la classe, « low » et 1 essai pour une tâche facile, « medium » et 2 pour une standard, « high » et 5 pour une difficile, puis crée l'adaptateur `ClaudeLLM` avec cet effort. Elle lance ensuite `executer_agent` essai après essai, en séquentiel, et renvoie au premier essai fini et accepté par le vérificateur un dictionnaire de statut « livre » avec le numéro de l'essai et la réponse ; si aucun ne passe, elle renvoie le statut « escalade » avec le nombre d'essais consommés.

```python
# [extrait] — contrôleur de budget au-dessus du port LLM (non exécuté : il appelle l'API)
BUDGETS = {                       # classe -> (effort, nombre d'essais) ; valeurs à mesurer, pas à deviner
    "facile": ("low", 1),
    "standard": ("medium", 2),
    "difficile": ("high", 5),
}


def repondre(question: str, classe: str, verifier, system: str, outils: dict, schemas: list) -> dict:
    effort, n_essais = BUDGETS[classe]
    llm = ClaudeLLM(effort=effort)                  # seul l'adaptateur connaît output_config
    for essai in range(1, n_essais + 1):            # séquentiel, arrêt au premier essai accepté
        resultat = executer_agent(llm, system, question, outils, schemas)
        if resultat["statut"] == "fini" and verifier(resultat["reponse"]):
            return {"statut": "livre", "essais": essai, "reponse": resultat["reponse"]}
    return {"statut": "escalade", "essais": n_essais}
```

## Squelette algorithmique

Le fichier présente trois algorithmes :

- le **best-of-N vérifié**, qui livre le premier essai accepté ou escalade ;
- le **vote par pluralité**, qui garde la réponse la plus fréquente ;
- le **choix du budget**, qui calcule N* pour chaque classe de tâches, hors ligne, à partir des p mesurés.

### Best-of-N vérifié

Entrées : une tâche, un nombre maximal d'essais, un vérificateur et un mode. Sortie : une réponse acceptée, ou une escalade.

```text
ALGORITHME BestOfNVérifié
ENTRÉES : tâche, nombre maximal d'essais N, fonction vérifier(·), mode (parallèle ou séquentiel)
SORTIE  : réponse livrée, ou « escalade »

  SI mode = parallèle ALORS
      candidats ← N essais lancés en même temps
  FIN SI
  POUR i DE 1 À N FAIRE
      SI mode = séquentiel ALORS
          candidat ← un nouvel essai          (payé seulement si les i − 1 premiers ont échoué)
      SINON
          candidat ← candidats[i]
      FIN SI
      SI vérifier(candidat) = accepté ALORS RETOURNER candidat
  FIN POUR
  RETOURNER « escalade »
```

**Complexité :** O(N) appels du modèle et O(N) vérifications, dans le pire cas. Le coût est dominé par les appels : N × C₁ en parallèle, et en moyenne (1 − aᴺ)/(1 − a) × C₁ en séquentiel. La mémoire vaut O(N) candidats en parallèle, O(1) en séquentiel.

**Du squelette au code :** la probabilité de livrer juste, faux ou d'escalader se calcule dans `best_of_n_verifie`, et le cas parfait dans `best_of_n`. La boucle elle-même est la fonction `repondre` de l'extrait, au-dessus d'`executer_agent`. Le nombre moyen d'essais payés en séquentiel est la somme `essais_moyens` du bloc 4 de `main`.

### Vote par pluralité

Entrées : N réponses déjà produites. Sortie : la réponse retenue, avec un signal quand aucune réponse n'a la majorité.

```text
ALGORITHME VoteParPluralité
ENTRÉES : réponses r₁ … rₙ
SORTIE  : réponse retenue, et signal « pas de majorité »

  comptes ← dictionnaire vide ; premier ← dictionnaire vide
  POUR i DE 1 À N FAIRE
      comptes[rᵢ] ← comptes[rᵢ] + 1          (0 si rᵢ est nouvelle)
      SI rᵢ n'est pas dans premier ALORS premier[rᵢ] ← i
  FIN POUR
  gagnant ← la réponse au plus grand compte ; en cas d'égalité, celle au plus petit premier[·]
  SI comptes[gagnant] ≤ N / 2 ALORS signaler « pas de majorité » (escalade possible)
  RETOURNER gagnant
```

**Complexité :** O(N) en temps avec un dictionnaire, et O(R) en mémoire, où R est le nombre de réponses distinctes. La fonction `pluralite` du code appelle `reponses.index(r)` pour chaque réponse distincte : elle est en O(N·R), ce qui suffit pour quelques dizaines de votes. Le squelette, qui mémorise `premier`, reste en O(N).

**Du squelette au code :** les comptes et le départage correspondent à `pluralite`. La probabilité que la majorité stricte soit juste est `vote_majoritaire`, et l'effet de deux votes de plus est `increment_vote`. Le signal « pas de majorité » est la règle d'escalade du cas Crypto ci-dessous.

### Choix du budget

Entrées : les classes de tâches, avec leur p mesuré, la valeur V d'une tâche réussie et le coût C₁ d'un essai. Sortie : le N* de chaque classe.

```text
ALGORITHME ChoisirBudget
ENTRÉES : classes c, avec leur p(c) mesuré ; valeur V d'une tâche réussie ; coût C₁ d'un essai
SORTIE  : N*(c) pour chaque classe

  POUR CHAQUE classe c FAIRE
      SI V × p(c) < C₁ ALORS
          N*(c) ← 0                          (pas d'appel : humain ou règle)
      SINON
          N ← 0
          TANT QUE V × p(c) × (1 − p(c))^N ≥ C₁ FAIRE
              N ← N + 1
          FIN TANT QUE
          N*(c) ← N
      FIN SI
  FIN POUR
  À L'EXÉCUTION : classe ← routeur(tâche) ; lancer BestOfNVérifié avec N*(classe)
```

**Complexité :** O(N*) par classe avec la boucle, O(1) avec la forme fermée. Le calcul se fait hors ligne, à chaque mise à jour des p mesurés, et non à chaque requête. Au moment de la requête, seul le routeur s'exécute.

**Du squelette au code :** la boucle TANT QUE est `n_etoile`, et la forme fermée est `n_etoile_formule`. Le mélange des classes et la comparaison avec un budget uniforme forment le bloc 6 de `main` (fonction `melange`). Le dictionnaire `BUDGETS` de l'extrait est la table N*(c) qu'utilise le routeur.

## Cas d'usage réels aux Émirats

Les probabilités, valeurs et coûts ci-dessous sont illustratifs. En production, on les mesure par classe de tâches sur un jeu d'évaluation (étape 60) et dans les traces (étape 72 quater).

### Banque — extraire un relevé de salaire pour un dossier de prêt

Une banque de détail de Dubaï fait extraire par un agent les champs d'un relevé de salaire scanné : employeur, salaire de base, indemnités, IBAN. Ces champs alimentent ensuite le calcul du ratio d'endettement de la CBUAE, qui doit rester sous 50 % du revenu, toutes mensualités comprises.

Le vérificateur est presque parfait sur une partie des champs. L'IBAN passe le contrôle mod 97 (`iban_ae_valide` du code canonique), la somme des lignes doit égaler le total, et le schéma strict refuse tout champ manquant.

Sur les relevés difficiles (photos de travers, mélange d'arabe et d'anglais), l'équipe mesure p = 0,6 par essai. Trois essais parallèles extraient 1 − 0,4³ = 0,936 des dossiers sans humain, contre 0,6 pour un seul essai.

Une extraction ratée coûte une saisie manuelle estimée à 12 AED, et un essai environ 0,10 AED. Le calcul donne N* = 1 + ⌊ln(0,10 / 7,2) / ln 0,4⌋ = 1 + ⌊4,67⌋ = 5. L'équipe s'arrête pourtant à trois essais, pour tenir le temps de réponse au guichet.

Sans vérificateur, multiplier les essais ne servirait à rien, puisque l'agent ne saurait pas lequel garder. Le contrôle mod 97 ne garantit pas non plus que le montant du salaire est juste : ce champ est recoupé avec les virements de salaire reçus sur le compte. L'indicateur suivi est le taux d'extraction sans saisie manuelle, accompagné du taux d'erreurs trouvées en contrôle a posteriori.

### Immobilier — router les questions des acheteurs

Une agence présente à Dubaï et à Abu Dhabi reçoit chaque jour deux sortes de demandes d'acheteurs :

- des questions simples : horaires, pièces à fournir pour un contrat Ejari, montant des frais de transfert du DLD (4 % de la valeur du bien) ;
- des analyses de contrats off-plan de quarante pages.

Un petit classifieur range 80 % des demandes parmi les simples et 20 % parmi les analyses. Les questions simples partent avec l'effort `low` et un seul essai, pour un p mesuré à 0,97. Les analyses partent avec l'effort `high`. Pour l'extraction du calendrier de paiement, elles reçoivent trois essais, vérifiés par un contrôle de cohérence : les échéances doivent sommer à 100 % du prix.

C'est le routage du point 9. Un budget uniforme calé sur les analyses ferait payer à chaque question d'horaires des milliers de tokens de réflexion inutiles. Un budget uniforme calé sur les questions simples laisserait passer des échéances erronées dans les contrats.

Les 4 % du DLD se calculent par un outil, jamais par réflexion : aucune profondeur de raisonnement ne rend un calcul plus sûr qu'une fonction testée. L'indicateur suivi est le coût moyen par demande et par classe, avec le taux de demandes reclassées par un humain.

### Crypto — classer les alertes de liquidité par un vote

Une plateforme d'actifs virtuels agréée par la VARA reçoit des alertes de liquidité sur ses pools et demande à un agent : « incident réel ou bruit ? ». Il n'existe pas de vérificateur automatique au moment de la décision. L'équipe fait donc voter cinq avis produits à l'effort `low`.

Sur les alertes ordinaires, p = 0,8 : la majorité est juste avec la probabilité 0,94208, contre 0,8 pour un avis seul. Mais sur un type d'alerte apparu récemment, l'évaluation a mesuré p = 0,45, et la majorité tombe à 0,4069 : le vote amplifie l'erreur, comme l'annonce le point 5.

L'agent se sert donc du désaccord comme d'un signal. Un vote à 3 contre 2 part à l'astreinte humaine au lieu d'être exécuté ; seul un vote unanime, ou à 4 contre 1, déclenche l'action automatique. Sans cette règle, un vote sur une question que le modèle ne sait pas résoudre donnerait une fausse assurance, celle de cinq avis concordants en apparence.

La surveillance de la liquidité est une obligation opérationnelle de la plateforme : une alerte réelle classée « bruit » est l'incident le plus coûteux. L'indicateur suivi est le taux d'alertes escaladées, avec la justesse des décisions automatiques mesurée a posteriori, par type d'alerte.

### Assurance — un juge imparfait ne rend pas les décisions plus sûres

Un assureur auto et santé fait proposer par un agent la classification d'un sinistre : couvert, non couvert ou à instruire. Un juge LLM relit ensuite la proposition et vérifie sa cohérence avec la police. Mesuré sur un jeu étiqueté, ce juge accepte 90 % des bonnes propositions et 10 % des mauvaises : v₊ = 0,9 et v₋ = 0,1.

L'équipe pensait qu'avec cinq propositions au lieu d'une, l'agent deviendrait plus fiable. Le point 3 montre le contraire. Avec p = 0,4 sur les dossiers complexes, la précision des décisions livrées reste à 0,857 quel que soit N ; seul le taux de dossiers traités sans humain monte, de 0,42 à N = 1 à 0,934 à N = 5.

Or une décision fausse livrée coûte bien plus cher qu'une escalade. Un refus de prise en charge injustifié entraîne une réclamation, et un risque de conformité vis-à-vis de la CBUAE, qui supervise l'assurance. L'assureur garde donc N = 2, et investit plutôt dans un meilleur juge : faire baisser v₋ de 0,1 à 0,03 fait monter la précision de 0,857 à 0,952.

L'indicateur suivi est la précision des décisions automatiques, mesurée par échantillonnage humain, avec le taux d'escalade.

### BTP — vérifier une facture avec des tests, comme du code

Un groupe de construction à Dubaï fait contrôler par un agent les factures de ses sous-traitants : quantités contre bon de commande, TVA à 5 %, retenue de garantie. Le vérificateur est un programme. Il recalcule la TVA (`tva(montant_ht)` du code canonique), compare chaque ligne au bon de commande et refuse toute sortie qui ne respecte pas le schéma.

On est dans le cas du point 1, avec un vérificateur presque parfait. Sur les factures longues, p = 0,5 par essai, et cinq essais donnent 1 − 0,5⁵ = 0,96875 de contrôles complets sans humain.

Une erreur de paiement évitée vaut beaucoup (V = 200 AED), et un essai coûte 0,30 AED, parce que les factures longues pèsent lourd en entrée. Le calcul donne N* = 1 + ⌊ln(0,30 / 100) / ln 0,5⌋ = 1 + ⌊8,38⌋ = 9.

Les contrôles tournent la nuit, en lot, donc la latence ne compte pas. L'équipe lance les essais en séquentiel, avec arrêt au premier contrôle validé, ce qui coûte en moyenne (1 − 0,5⁹)/0,5 ≈ 2 essais au lieu de 9. Sans vérificateur programmé, il faudrait un contrôleur humain pour chaque facture longue. L'indicateur suivi est la part des factures contrôlées sans humain, avec le montant des écarts détectés.

### Secteur public — un budget par session, sous contrainte de latence

Une entité de services publics en ligne, accessible par UAE Pass, répond en arabe et en anglais.

- Pour une question de FAQ, une seule réponse à l'effort `low` suffit.
- Pour une démarche qui engage l'usager (un renouvellement, un paiement), l'agent lance trois essais en parallèle. Ils sont vérifiés par un outil qui interroge le statut officiel du dossier.

Le parallèle garde la latence d'un seul appel, mais il triple le débit consommé. Aux heures de pointe, le plafond de requêtes par minute du fournisseur devient la contrainte. Le contrôleur réduit alors N à 2 sur les démarches les moins sensibles, plutôt que de faire attendre tout le monde.

Chaque session a un budget plafonné, par exemple 0,50 AED. Au-delà, l'agent cesse d'échantillonner et propose un rendez-vous humain, ce qui empêche une conversation longue et confuse de consommer sans fin.

La politique de minimisation des données de l'entité s'applique aussi aux essais : ils reçoivent le même contexte minimal, et les essais non retenus ne sont pas conservés au-delà de la durée prévue. Le cadre légal applicable à une entité publique est à confirmer avec le texte en vigueur. L'indicateur suivi est le coût moyen par démarche aboutie, avec le p95 du temps de réponse (fonction `p95` du code canonique).

## Pièges et limites

- **Supposer les essais indépendants.** Le même modèle, le même prompt et les mêmes documents produisent des erreurs corrélées. Sur une tâche que le modèle ne sait pas faire, les N essais échouent ensemble. La formule 1 − (1 − p)ᴺ est donc un plafond : on mesure le vrai pass@N sur ses propres tâches, avec l'estimateur de l'étape 60.
- **Calculer N* avec le p moyen.** L'inégalité de Jensen (point 10) le rend trop optimiste. On calcule par classe de tâches, puis on agrège.
- **Faire voter un modèle sur une question où p < 1/2.** Le vote amplifie l'erreur. Le désaccord entre votes est un signal d'escalade, pas un détail.
- **Prendre un juge LLM pour un vérificateur parfait.** La précision reste plafonnée (point 3). Pire encore : avec beaucoup d'essais, le best-of-N finit par trouver les réponses qui exploitent les failles du juge. C'est la loi de Goodhart, le même phénomène que le détournement de récompense de l'étape 74 bis.
- **Oublier que la réflexion se facture en sortie et se tronque.** Un effort élevé avec un `max_tokens` bas produit des sorties tronquées (statut `"tronque"`). Ces essais comptent comme des échecs dans p, et il ne faut pas les relancer à l'aveugle avec le même plafond.

### Exercice feuille blanche

1. Sans regarder le code, écrire `best_of_n_verifie`. Vérifier qu'avec v₊ = 1 et v₋ = 0 on retrouve 1 − (1 − p)ᴺ, et que la précision des réponses livrées ne dépend pas de N.
2. Prédire, puis vérifier : avec V = 3 AED et C₁ = 0,1047 AED, quel est le N* pour p = 0,7 ? (Réponse : ln(0,1047 / 2,1) / ln 0,3 = (−2,999)/(−1,204) ≈ 2,49, donc N* = 3. Le 4ᵉ essai ne rapporterait que 3 × 0,7 × 0,3³ ≈ 0,057 AED.)
3. Trouver le bug : un collègue écrit `return valeur * best_of_n(p, n) - cout` dans `gain_net`. Quel N la recherche du maximum renvoie-t-elle, et pourquoi ? (Réponse : le plus grand N testé, parce que le coût ne dépend plus de N alors que P_N croît toujours.)

## Pour aller plus loin

- **Arrêt anticipé du vote.** On tire les votes un par un, et l'on s'arrête dès qu'une réponse a (N + 1)/2 voix : le coût moyen descend sous N, sans changer le résultat.
- **Recherche guidée par un vérificateur.** Un vérificateur de processus (*process reward model*) note chaque étape du raisonnement, et non la seule réponse finale. Il permet une recherche en faisceau ou en arbre (Tree of Thoughts, cité à l'étape 72).
- **Lectures de référence.** L'auto-cohérence a été proposée par Wang et al. (2022). L'allocation du calcul selon la difficulté de la question, qui généralise le point 9, est étudiée dans « Scaling LLM Test-Time Compute Optimally Can Be More Effective Than Scaling Model Parameters » (Snell et al., 2024).
- **Budget de tâche de l'API Claude.** Une fonction en bêta donne au modèle un budget de tokens pour toute une boucle d'agent, qu'il voit décroître. Sa forme est `output_config={"effort": "high", "task_budget": {"type": "tokens", "total": 64000}}`, avec la bêta `task-budgets-2026-03-13`. C'est un budget indicatif, distinct du plafond `max_tokens` (état de l'API en novembre 2026, à vérifier).
- **Les mêmes N essais servent à l'entraînement.** GRPO (étape 74 bis) tire N réponses par question, exactement comme le best-of-N, mais se sert de leurs récompenses relatives pour entraîner le modèle au lieu de choisir une réponse.

> Étape 72 quinquies du parcours · Prérequis : [Observabilité : traces, coûts et dérive](<72d-Observabilite-Traces-Couts-et-Derive.md>) · Suite : [Descente de gradient et LoRA](<73-Optimisation-et-Fine-Tuning.md>)
