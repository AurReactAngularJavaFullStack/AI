# Étape 65 bis — Évaluation — Classement par duels : Elo et Bradley-Terry

> Étape 65 bis du parcours · Prérequis : [Exemples d'évaluation](<65-Evaluation-Exemples-Cas-Usage.md>) · Suite : [Complaisance et horizon de tâche](<65c-Complaisance-et-Horizon-de-Tache.md>)

**Dossier :** 10-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Product Engineers, Forward-Deployed Engineers  
**Nom du fichier :** 65b-Classement-par-Duels-Elo-Bradley-Terry.md

Le harnais de l'étape 65 juge chaque cas contre un critère vérifiable. Beaucoup de sorties d'agent n'en ont pas : une lettre de refus de prêt, une description de bien en arabe et en anglais, le résumé d'un incident. On peut dire laquelle de deux réponses est meilleure, beaucoup plus facilement qu'on ne peut leur donner une note absolue. Ce fichier construit, en Python standard, le classement qui sort de ces **duels** : le modèle de Bradley-Terry, son estimation par maximum de vraisemblance, le classement Elo, la preuve que l'un est la version en ligne de l'autre, puis les matchs nuls, le biais du juge et les intervalles par bootstrap.

## Définition

Un **duel** oppose deux versions d'un agent sur la même demande ; un juge, humain ou LLM, dit laquelle a donné la meilleure réponse, ou déclare un match nul. Le **modèle de Bradley-Terry** attribue à chaque version i une force θᵢ et pose que la probabilité que i batte j ne dépend que de l'écart de force : σ(θᵢ − θⱼ), où σ est la fonction logistique. Les forces s'estiment par **maximum de vraisemblance** sur tous les duels observés, par les itérations de Zermelo ou par montée de gradient. Le **classement Elo** est la même loi écrite dans une autre unité, des « points », mise à jour après chaque duel par la règle R ← R + K(S − E) : c'est un pas de gradient stochastique sur la vraisemblance de Bradley-Terry. Un classement publié s'accompagne d'intervalles, obtenus ici par **bootstrap**.

## Rôle dans un agent

Le classement par duels sert à l'étape **observer**, dans le banc d'évaluation (étape 13 bis), quand la qualité ne se vérifie pas par programme. On joue deux versions sur les mêmes demandes, on présente les paires de réponses au juge sans lui dire quelle version a produit quoi, et l'on estime les forces. Le résultat pilote une **décision de déploiement** (la candidate est-elle meilleure que la production ?) ou un **choix entre plusieurs prompts, modèles ou outils**. Elo convient au suivi en continu, duel après duel ; Bradley-Terry, ajusté hors ligne, convient à la décision, parce que son résultat ne dépend pas de l'ordre des duels. Le même modèle réapparaîtra à l'étape 74 bis : le modèle de récompense de l'alignement par préférences humaines est un modèle de Bradley-Terry.

## Équation complète

Modèle de Bradley-Terry, sous ses deux formes :

$$
P(i \succ j) = \sigma(\theta_i - \theta_j) = \frac{e^{\theta_i}}{e^{\theta_i} + e^{\theta_j}} = \frac{\pi_i}{\pi_i + \pi_j}, \qquad \sigma(x) = \frac{1}{1 + e^{-x}}, \qquad \pi_i = e^{\theta_i}
$$

Log-vraisemblance des duels observés et son gradient :

$$
\ell(\theta) = \sum_{i \ne j} W_{ij} \,\ln \sigma(\theta_i - \theta_j), \qquad \frac{\partial \ell}{\partial \theta_i} = \sum_{j \ne i} \Big( W_{ij} - N_{ij}\,\sigma(\theta_i - \theta_j) \Big)
$$

Itération MM de Zermelo, suivie d'un recentrage qui impose une moyenne nulle aux θ :

$$
\pi_i \leftarrow \frac{W_i}{\displaystyle\sum_{j \ne i} \frac{N_{ij}}{\pi_i + \pi_j}}, \qquad W_i = \sum_{j \ne i} W_{ij}
$$

Classement Elo : score attendu, puis mise à jour après un duel de score Sᵢ :

$$
E_i = \frac{1}{1 + 10^{(R_j - R_i)/400}}, \qquad R_i \leftarrow R_i + K\,(S_i - E_i), \qquad R_j \leftarrow R_j - K\,(S_i - E_i)
$$

Passage d'une échelle à l'autre :

$$
R_i = 1500 + c\,\theta_i, \qquad c = \frac{400}{\ln 10} \approx 173{,}72, \qquad K = c\,\eta
$$

Match nul : chaque version reçoit la moitié d'une victoire.

$$
S_i = \tfrac{1}{2} \quad\Longrightarrow\quad W_{ij} \mathrel{+}= \tfrac{1}{2}, \qquad W_{ji} \mathrel{+}= \tfrac{1}{2}, \qquad N_{ij} \mathrel{+}= 1
$$

## Décryptage des symboles

$$
\theta_i
$$

**Sens :** force de la version i, dans l'échelle naturelle (logarithme d'une cote) ; seules les différences ont un sens · **Type / plage :** réel ; le code impose une moyenne nulle · **Variable Python :** `theta[i]`

$$
\pi_i
$$

**Sens :** force de la version i sous forme de rapport, πᵢ = e^θᵢ ; la probabilité de victoire est la part de i dans πᵢ + πⱼ · **Type / plage :** réel > 0 · **Variable Python :** `pi[i]`

$$
\sigma(x)
$$

**Sens :** fonction logistique, qui transforme un écart de force en probabilité · **Type / plage :** réel dans ]0, 1[, σ(0) = 1/2, σ(−x) = 1 − σ(x) · **Variable Python :** `sigma(x)`

$$
W_{ij},\ N_{ij}
$$

**Sens :** victoires de i sur j (un nul compte pour 1/2 de chaque côté), et nombre de duels joués entre i et j · **Type / plage :** réels ≥ 0, Wᵢⱼ + Wⱼᵢ = Nᵢⱼ · **Variable Python :** `w[i][j]`, `n[i][j]`, construits par `tableau(duels, versions)`

$$
W_i
$$

**Sens :** total des victoires de i, tous adversaires confondus · **Type / plage :** réel ≥ 0 · **Variable Python :** `gagnes`

$$
\ell(\theta)
$$

**Sens :** logarithme de la probabilité des duels observés, si les forces valaient θ · **Type / plage :** réel ≤ 0 · **Variable Python :** `log_vraisemblance(theta, w, versions)`

$$
R_i,\ E_i,\ S_i
$$

**Sens :** note Elo de la version i, score qu'elle devait obtenir contre j selon ces notes, et score réellement obtenu (1 victoire, 1/2 nul, 0 défaite) · **Type / plage :** réel ; réel dans ]0, 1[ ; 0, 1/2 ou 1 · **Variable Python :** `notes[i]`, `elo_attendu(r_i, r_j)`, `s`

$$
K
$$

**Sens :** facteur Elo : de combien de points une note bouge au plus après un duel · **Type / plage :** réel > 0, souvent entre 4 et 32 · **Variable Python :** `k`

$$
c,\ \eta
$$

**Sens :** nombre de points Elo par unité de θ, et pas de gradient équivalent dans l'échelle naturelle · **Type / plage :** c = 400/ln 10 ≈ 173,72 ; η = K/c · **Variable Python :** `ECHELLE`, `32 / ECHELLE`

$$
\delta
$$

**Sens :** biais de position du juge : bonus d'écart de force qu'il accorde à la réponse lue en premier · **Type / plage :** réel ; 0 pour un juge sans biais · **Variable Python :** `biais`

$$
M
$$

**Sens :** nombre de rééchantillonnages du bootstrap · **Type / plage :** entier ≥ 1, au moins 1 000 en production · **Variable Python :** `tirages`

## Démonstration

### 1. La forme logistique et la forme en rapport sont la même loi

On divise numérateur et dénominateur de πᵢ/(πᵢ + πⱼ) par πᵢ = e^θᵢ :

$$
\frac{e^{\theta_i}}{e^{\theta_i} + e^{\theta_j}} = \frac{1}{1 + e^{\theta_j - \theta_i}} = \frac{1}{1 + e^{-(\theta_i - \theta_j)}} = \sigma(\theta_i - \theta_j)
$$

Deux conséquences. P(i ≻ j) + P(j ≻ i) = σ(x) + σ(−x) = 1 : il n'y a pas de place pour le nul dans le modèle de base, d'où la convention des demi-victoires. Et ajouter la même constante à tous les θ ne change aucune probabilité : seules les **différences** sont identifiables. Il faut une convention pour fixer le niveau : le code impose Σ θᵢ = 0 ; Elo prend 1 500 comme note de départ. Un classement ne dit jamais « la version A vaut 1 600 » dans l'absolu, seulement « A a 100 points de plus que B ».

### 2. Le gradient vaut victoires observées moins victoires attendues

La dérivée de la logistique vaut σ'(x) = σ(x)(1 − σ(x)), donc celle de ln σ(x) vaut 1 − σ(x). Dans ℓ, deux termes contiennent θᵢ pour un adversaire j donné : Wᵢⱼ ln σ(θᵢ − θⱼ), dont la dérivée vaut Wᵢⱼ(1 − σ(θᵢ − θⱼ)), et Wⱼᵢ ln σ(θⱼ − θᵢ), dont la dérivée vaut −Wⱼᵢ(1 − σ(θⱼ − θᵢ)) = −Wⱼᵢ σ(θᵢ − θⱼ). Leur somme, avec Wᵢⱼ + Wⱼᵢ = Nᵢⱼ, donne

$$
\frac{\partial \ell}{\partial \theta_i} = \sum_{j \ne i} \Big( W_{ij} - N_{ij}\,\sigma(\theta_i - \theta_j) \Big) = W_i - \mathbb{E}_\theta[W_i]
$$

À l'optimum, le gradient est nul : **chaque version gagne exactement autant de duels que le modèle le prévoit**. C'est le contrôle que le programme fait sur l'exemple du point 6, à 10⁻⁹ près.

### 3. La log-vraisemblance est concave : un seul optimum

La dérivée seconde de ln σ(x) vaut −σ(x)(1 − σ(x)) < 0. Pour une direction quelconque x = (x₁, …, xₘ), la forme quadratique de la matrice hessienne s'écrit

$$
x^{\top} H\, x = -\sum_{i < j} N_{ij}\,\sigma(\theta_i - \theta_j)\big(1 - \sigma(\theta_i - \theta_j)\big)\,(x_i - x_j)^2 \le 0
$$

parce que chaque terme est un carré multiplié par un poids positif. ℓ est donc concave : tout point où le gradient s'annule est un maximum global, et une montée de gradient ou les itérations MM ne peuvent pas rester coincées ailleurs. La forme ne s'annule que si xᵢ = xⱼ pour toutes les paires qui se sont affrontées : si le graphe des duels est **connexe**, la seule direction plate est la translation commune du point 1, et l'optimum est unique une fois la moyenne fixée. Si deux groupes de versions ne se sont jamais rencontrés, leurs niveaux relatifs sont indéterminés : aucun calcul ne peut les comparer.

### 4. Existence : la condition de Zermelo, et la version invaincue

Concavité ne veut pas dire existence. Si une version D n'a jamais perdu, chacun de ses termes W_Dj ln σ(θ_D − θⱼ) augmente strictement quand θ_D augmente, et aucun terme ne la freine : ℓ n'a pas de maximum, l'estimateur part à l'infini. La condition exacte, due à Zermelo puis à Ford, est que pour tout découpage des versions en deux groupes, chaque groupe ait au moins une victoire (ou un nul) contre l'autre. Le programme ajoute une version D qui a battu A dix fois sur dix : après 10, 100 et 1 000 itérations, θ_D vaut 2,279, puis 4,093, puis 5,837, et ne s'arrête jamais. Le remède est un **lissage** : un nul virtuel par paire jouée, c'est-à-dire une demi-victoire de chaque côté. La condition de Zermelo est alors satisfaite, et l'estimation converge, ici vers θ_D = 2,679 en 415 itérations. C'est l'équivalent d'un a priori, comme les pseudo-comptes de la loi bêta (étape 60 bis).

### 5. Deux versions : une formule fermée

Avec deux versions seulement, le gradient nul s'écrit W_AB = N_AB σ(θ_A − θ_B), donc σ(θ_A − θ_B) = W_AB / N_AB, la part de victoires observée. En inversant la logistique :

$$
\theta_A - \theta_B = \ln \frac{W_{AB}}{W_{BA}}, \qquad 7 \text{ victoires sur } 10 : \ \ln \frac{7}{3} = 0{,}847298 \ \text{ soit } \ 173{,}72 \times 0{,}847298 \approx 147{,}2 \text{ points}
$$

Repères utiles : 100 points d'écart donnent une probabilité de victoire de 0,640, 200 points 0,760, 400 points 10/11 ≈ 0,909, c'est-à-dire une cote de 10 contre 1, parce que 10^(400/400) = 10.

### 6. Les itérations MM de Zermelo font toujours monter la vraisemblance

On écrit ℓ avec les πᵢ : ℓ(π) = Σᵢ Wᵢ ln πᵢ − Σᵢ<ⱼ Nᵢⱼ ln(πᵢ + πⱼ). La fonction −ln est convexe, donc au-dessus de sa tangente en tout point y > 0 : −ln x ≥ −ln y − (x − y)/y. En posant x = πᵢ + πⱼ et y = πᵢᵏ + πⱼᵏ, les valeurs de l'itération k, on obtient un **minorant** de ℓ :

$$
\ell(\pi) \;\ge\; Q(\pi \mid \pi^k) = \sum_i W_i \ln \pi_i - \sum_{i<j} N_{ij}\,\frac{\pi_i + \pi_j}{\pi_i^k + \pi_j^k} + \text{constante}, \qquad \ell(\pi^k) = Q(\pi^k \mid \pi^k)
$$

Q se sépare en une fonction de chaque πᵢ seul. Sa dérivée en πᵢ, Wᵢ/πᵢ − Σⱼ Nᵢⱼ/(πᵢᵏ + πⱼᵏ), s'annule exactement pour la mise à jour de l'équation complète. D'où la chaîne ℓ(πᵏ⁺¹) ≥ Q(πᵏ⁺¹ | πᵏ) ≥ Q(πᵏ | πᵏ) = ℓ(πᵏ) : la première inégalité est la minoration, la seconde vient de ce que πᵏ⁺¹ maximise Q. Le recentrage multiplie tous les πᵢ par la même constante et ne change pas ℓ (point 1). Le programme vérifie que la suite des ℓ ne décroît jamais.

**Exemple fait à la main (le code reprend ces nombres).** Trois versions d'un agent, 30 duels :

| Paire | Victoires du premier | Victoires du second |
|---|---|---|
| A contre B | 6 | 4 |
| A contre C | 8 | 2 |
| B contre C | 7 | 3 |

Les totaux sont W_A = 14, W_B = 11 et W_C = 5. On part de π = (1, 1, 1), où ℓ = 30 ln(1/2) = −20,7944. Pour chaque version, le dénominateur vaut 10/2 + 10/2 = 10, donc la première itération donne π ∝ (1,4 ; 1,1 ; 0,5), et ℓ monte à −17,9882. Après 36 itérations, θ = (+0,5915 ; +0,1491 ; −0,7406), soit 1 602,7, 1 525,9 et 1 371,3 points, et ℓ = −17,8487. Contrôle du gradient nul pour A : 10 σ(0,4424) + 10 σ(1,3321) = 6,088 + 7,912 = 14, ses 14 victoires. Le modèle donne P(A ≻ B) = 0,609, et non les 6/10 observés : il tient compte aussi des duels contre C, ce qui revient à supposer la **transitivité** des forces.

### 7. Elo est un pas de gradient stochastique sur Bradley-Terry

D'abord, la formule Elo est la logistique en base 10. Comme 10ˣ = e^(x ln 10),

$$
E_i = \frac{1}{1 + 10^{(R_j - R_i)/400}} = \frac{1}{1 + e^{-(R_i - R_j)\ln 10/400}} = \sigma\!\left(\frac{R_i - R_j}{c}\right), \qquad c = \frac{400}{\ln 10}
$$

c'est-à-dire σ(θᵢ − θⱼ) avec θ = R/c. Ensuite, la log-vraisemblance d'**un** duel de score Sᵢ vaut ℓₘ = Sᵢ ln σ(d) + (1 − Sᵢ) ln σ(−d), avec d = θᵢ − θⱼ. Par le point 2,

$$
\frac{\partial \ell_m}{\partial \theta_i} = S_i\,(1 - \sigma(d)) - (1 - S_i)\,\sigma(d) = S_i - \sigma(d) = S_i - E_i, \qquad \frac{\partial \ell_m}{\partial \theta_j} = -(S_i - E_i)
$$

Le calcul vaut aussi pour un nul, Sᵢ = 1/2. Un pas de gradient stochastique de taux η, θᵢ ← θᵢ + η(Sᵢ − Eᵢ), devient en points Rᵢ ← Rᵢ + cη(Sᵢ − Eᵢ) : c'est la mise à jour Elo avec K = cη. K = 32 correspond à η = 32/173,72 ≈ 0,184. Le programme vérifie la dérivée par différences finies pour S = 1, 1/2 et 0. Comme ce que gagne i, j le perd, la somme des notes est conservée : la moyenne reste à 1 500.

**Exemple à la main.** A à 1 500 rencontre B à 1 600 : E_A = 1/(1 + 10^0,25) = 1/2,778279 = 0,359935. A gagne : R_A = 1 500 + 32 × 0,640065 = 1 520,48, et R_B = 1 579,52.

Ce que la preuve explique. Un pas **constant** sur un duel à la fois ne converge pas vers le maximum : il oscille autour, et la note finale dépend de l'**ordre** des duels. Sur les 30 duels du point 6, joués dans l'ordre du tableau avec K = 32, Elo finit à 1 546,7, 1 509,5 et 1 443,8 ; dans l'ordre inverse, à 1 606,9, 1 517,6 et 1 375,6, alors que Bradley-Terry est identique quel que soit l'ordre. Avec un petit pas, K = 2, et la moyenne des notes sur 500 passages mélangés, Elo retrouve 1 602,7, 1 525,8 et 1 371,5 : à moins d'un point de Bradley-Terry, comme le prévoit la théorie du gradient stochastique moyenné.

### 8. Le juge préfère la première réponse : deux ordres et des nuls

Un LLM juge, et souvent un humain pressé, favorise la réponse qu'il lit en premier. On modélise ce biais par un décalage δ : P(la première gagne) = σ(d + δ), où d est l'écart de force réel. Le protocole **naïf** présente toujours la version candidate en premier : son score attendu vaut σ(d + δ), comme si elle avait δ de force en plus. Le protocole **à deux ordres** juge chaque paire deux fois, en inversant l'ordre, et déclare un nul si les deux avis se contredisent. Le score attendu de i devient la moyenne des deux probabilités :

$$
\mathbb{E}[S_i] = g(d) = \frac{\sigma(d + \delta) + \sigma(d - \delta)}{2}, \qquad g(-d) = 1 - g(d)
$$

La seconde égalité vient de σ(−x) = 1 − σ(x) : g(−d) = [1 − σ(d − δ) + 1 − σ(d + δ)] / 2 = 1 − g(d), donc aucune des deux versions n'est favorisée. La fonction croît avec d, donc l'**ordre** des forces est conservé. Sa pente en 0 vaut σ(δ)(1 − σ(δ)), inférieure au 1/4 de σ : les écarts sont un peu **écrasés**, sans être inversés.

Le programme le montre sans bruit, en ajustant le modèle sur les scores attendus, avec quatre versions de forces 0 ; 0,5 ; 1 et 0,8 et un biais δ = 0,5. Les vraies notes centrées valent 1 400,1, 1 487,0, 1 573,8 et 1 539,1. Avec deux ordres, on obtient 1 405,8, 1 487,7, 1 569,6 et 1 536,9 : même ordre, écarts légèrement réduits. En protocole naïf, où la version la plus récente est toujours lue en premier, v4 passe devant v3 : 1 609,3 contre 1 593,9, et v1, toujours lue en second, tombe à 1 331,5. Sur un échantillon de 100 duels par paire, le protocole à deux ordres place v3 devant v4 (1 559,8 contre 1 530,8) et le protocole naïf les inverse (1 594,6 contre 1 563,7). Les deux ordres coûtent deux appels au juge par duel, et produisent ici 283 nuls sur 600 duels : ces nuls ne sont pas du bruit à jeter, ils mesurent les cas où le juge ne tranche que par la position.

### 9. Intervalles par bootstrap

L'estimateur de Bradley-Terry n'a pas d'intervalle simple à la Wilson. Le bootstrap le fabrique par simulation : on tire M échantillons de duels **avec remise**, de la même taille que l'original, on réajuste le modèle sur chacun, et l'on lit les quantiles 2,5 % et 97,5 % des notes obtenues. La même boucle donne P(être premier), la part des échantillons où une version arrive en tête, qui est souvent la quantité utile pour décider. Sur les 600 duels à deux ordres, avec M = 100 et une graine fixe, v3 obtient [1 540,5 ; 1 575,7] et v4 [1 509,7 ; 1 554,4] : les intervalles se chevauchent, et pourtant v3 est première dans 93 % des échantillons. Comme pour les intervalles de Wilson de l'étape 60, le chevauchement ne tranche pas : on décide sur la quantité qui répond à la question, ici « v3 est-elle la meilleure ? ». Le bootstrap suppose les duels indépendants ; si plusieurs duels portent sur la même demande, on rééchantillonne les **demandes**, avec tous leurs duels.

## Effets et comportement

- **K règle la mémoire d'Elo.** Un grand K réagit vite à un changement de qualité mais oscille fort ; un petit K est stable mais lent. Aucun K ne rend Elo indépendant de l'ordre des duels.
- **Bradley-Terry utilise la transitivité.** Le duel A contre C informe sur A contre B : l'estimation de P(A ≻ B), 0,609, n'est pas la fréquence observée 0,6.
- **Les nuls apportent moins d'information qu'une décision.** Un nul compte pour une demi-victoire de chaque côté ; beaucoup de nuls rapprochent les forces et élargissent les intervalles.
- **Les écarts se lisent en probabilités.** 100 points valent 0,64, 200 points 0,76 et 400 points 0,91.
- **Le niveau est arbitraire.** On fixe souvent la version en production à 1 500 pour lire chaque candidate comme un écart à la production.

## Du symbole au code Python

| Notion | Variable ou fonction |
|---|---|
| fonction logistique σ | `sigma(x)` |
| probabilité de victoire de Bradley-Terry | `p_victoire(theta_i, theta_j)` |
| score attendu Eᵢ, mise à jour Elo | `elo_attendu(r_i, r_j)`, `elo_mise_a_jour(r_i, r_j, s_i, k)` |
| Elo sur une suite de duels | `elo_en_ligne(duels, versions, k)` |
| tables Wᵢⱼ et Nᵢⱼ | `tableau(duels, versions)` renvoie `w`, `n` |
| log-vraisemblance ℓ | `log_vraisemblance(theta, w, versions)` |
| victoires attendues | `victoires_attendues(theta, n, versions)` |
| itérations MM, lissage | `bradley_terry_mm(duels, versions, lissage)` |
| échelle c, points Elo | `ECHELLE`, `vers_points_elo(theta)` |
| juge biaisé, décalage δ | `juge_simule(premier, second, forces, biais, rng)` |
| protocole naïf ou à deux ordres | `comparer(...)`, `generer_duels(...)` |
| intervalles et P(être premier) | `bootstrap(duels, versions, tirages, graine)` |

### Déroulé, ligne par ligne

**`sigma(x)`** renvoie `1.0 / (1.0 + math.exp(-x))`. **`p_victoire(theta_i, theta_j)`** applique σ à l'écart. **`elo_attendu(r_i, r_j)`** écrit la formule en base 10 : pour 1 500 contre 1 600, `10 ** 0.25` vaut 1,778279 et le résultat 0,359935.

**`elo_mise_a_jour(r_i, r_j, s_i, k)`** refuse un score autre que 1, 0,5 ou 0, calcule `delta = k * (s_i - elo_attendu(r_i, r_j))`, ajoute `delta` à i et le retire à j : pour une victoire de A à 1 500 contre B à 1 600, `delta` vaut 20,48. **`elo_en_ligne`** part de 1 500 pour tout le monde et applique cette mise à jour duel après duel, **dans l'ordre de la liste** : c'est la source de la dépendance à l'ordre.

**`tableau(duels, versions)`** parcourt les triplets `(i, j, s)`, où `s` est le score de i. Il refuse un duel d'une version contre elle-même, une version inconnue ou un score hors de [0, 1], puis ajoute `s` à `w[i][j]`, `1 - s` à `w[j][i]`, et 1 à `n[i][j]` et `n[j][i]`. Un score fractionnaire est accepté : il sert aux nuls (0,5) et aux scores attendus du point 8.

**`log_vraisemblance`** somme `w[i][j] * math.log(p_victoire(...))` sur les paires ordonnées. **`victoires_attendues`** somme `n[i][j] * p_victoire(...)` : pour A à l'optimum, 6,088 + 7,912 = 14.

**`bradley_terry_mm(duels, versions, lissage, max_iter, tol)`** :

- le bloc `if lissage` ajoute `lissage` victoires virtuelles de chaque côté de chaque paire jouée, et `2 * lissage` duels ; avec 0,5, c'est un nul virtuel ;
- `pi` part de 1 partout, et `historique` reçoit ℓ en θ = 0, soit −20,7944 sur l'exemple ;
- pour chaque version, `gagnes` est Wᵢ et `denom` la somme des `n[i][j] / (pi[i] + pi[j])` ; si `gagnes == 0`, on lève `ValueError`, parce que le θ de cette version partirait vers −∞ ;
- `moyenne_log` est la moyenne des logarithmes des nouveaux π ; la soustraire impose Σ θ = 0, sans changer ℓ ;
- `ecart` mesure le plus grand changement de θ ; la boucle s'arrête sous `tol = 1e-12`, en 36 itérations sur l'exemple, ou après `max_iter` ;
- la fonction renvoie les θ, le nombre d'itérations et la suite des ℓ.

**`vers_points_elo(theta)`** renvoie `1500 + ECHELLE * theta` pour chaque version, avec `ECHELLE = 400 / math.log(10)`, soit 173,7178.

**`juge_simule(premier, second, forces, biais, rng)`** tire la victoire de la réponse lue en premier avec la probabilité σ(θₚ − θₛ + δ). **`comparer(i, j, ...)`** fait juger i en premier ; en protocole à deux ordres, il fait juger j en premier, retourne l'avis avec `1 - ...`, et renvoie la moyenne des deux avis : 1, 0 ou 0,5 s'ils se contredisent. **`generer_duels`** parcourt toutes les paires et place toujours la version la plus récente en position i, donc en premier dans le protocole naïf.

**`bootstrap(duels, versions, tirages, graine)`** crée son propre `random.Random(graine)`, tire `len(duels)` indices avec `rng.randrange`, réajuste, convertit en points, compte la version de tête (à égalité, `max` départage par le nom, pour que la sortie soit stable), trie les notes de chaque version et lit les rangs `int(0.025 * tirages)` et `int(0.975 * tirages) - 1`, soit les rangs 2 et 96 pour 100 tirages.

**`main()`**, bloc par bloc.

1. La forme en rapport contre la forme logistique ; le score attendu 0,359935 et la mise à jour Elo à 1 520,48 et 1 579,52 ; la conservation de la somme ; la même probabilité dans les deux échelles.
2. Deux versions, 7 victoires sur 10 : θ_A − θ_B = ln(7/3) et 147,2 points.
3. Une itération MM, la convergence en 36 itérations, la suite des ℓ croissante, et l'égalité victoires observées = victoires attendues pour chaque version.
4. La dérivée de la log-vraisemblance d'un duel, par différences finies, comparée à S − E pour trois scores ; le pas η = K/c.
5. Elo dans deux ordres, Bradley-Terry invariant après mélange, puis Elo à K = 2 moyenné sur 500 passages, à moins d'un point de Bradley-Terry.
6. Les scores attendus sans bruit des deux protocoles, puis 100 duels par paire, les deux protocoles sur échantillon, et le bootstrap de v3 et v4.
7. La version invaincue, dont θ grandit sans fin, puis le lissage.
8. Deux duels invalides, refusés par `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`sigma(x)`** — Cette fonction est le variateur de lumière qui transforme n'importe quel écart de force, de −∞ à +∞, en une probabilité comprise entre 0 et 1 : elle reçoit un réel x et renvoie la fonction logistique 1 ÷ (1 + e⁻ˣ), qui vaut 0,5 quand l'écart est nul, s'approche de 1 quand il est très positif et de 0 quand il est très négatif. Elle ne vérifie rien ; c'est la brique de toute la page, utilisée par `p_victoire`, par le juge simulé, par le calcul des scores attendus sans bruit et par la vérification de la dérivée dans `main`.

**`p_victoire(theta_i, theta_j)`** — Celle-ci est le bookmaker du modèle de Bradley-Terry, qui donne la cote d'un duel à partir des seules forces des deux adversaires : elle reçoit les forces θᵢ et θⱼ et renvoie σ(θᵢ − θⱼ), la probabilité que i batte j, sans aucune vérification. `main` vérifie qu'elle égale πᵢ ÷ (πᵢ + πⱼ) avec π = exp(θ) pour θ = 0,6 et 0,1, et qu'elle redonne exactement le score attendu Elo de 0,359935 quand on exprime 1 500 et 1 600 points dans l'unité de θ ; à l'optimum des trois versions, elle donne P(A bat B) = 0,609.

**`elo_attendu(r_i, r_j)`** — Cette fonction est le pronostiqueur des échecs, qui annonce avant la partie le score qu'un joueur devrait faire : elle reçoit les notes Elo des deux joueurs et renvoie 1 ÷ (1 + 10 à la puissance (Rⱼ − Rᵢ) ÷ 400), un nombre entre 0 et 1. Pour un joueur à 1 500 face à un joueur à 1 600, elle renvoie 0,359935 : le plus faible n'est pas condamné, il marque en moyenne un peu plus d'un tiers des points. C'est l'écart entre ce pronostic et le résultat réel qui pilote `elo_mise_a_jour`.

**`elo_en_ligne(duels, versions, k, r0)`** — Celle-ci est l'arbitre de tournoi qui met les notes à jour après chaque partie, dans l'ordre exact où les résultats arrivent : elle reçoit la liste des duels, triplets (i, j, score de i), la liste des versions, le facteur K et une note de départ de 1 500 par défaut, attribue cette note à tout le monde, puis applique `elo_mise_a_jour` duel après duel. Elle renvoie le dictionnaire des notes finales, dont la somme reste 4 500 pour trois versions ; mais les mêmes duels lus à l'envers donnent A à 1 606,9 au lieu de 1 546,7, preuve que l'Elo en ligne dépend de l'ordre.

**`log_vraisemblance(theta, w, versions)`** — Cette fonction est le juge de vraisemblance qui demande à un jeu de forces de rendre compte de tous les résultats observés : elle reçoit les forces θ, la table W des victoires et la liste des versions, et additionne, pour chaque paire ordonnée où i a gagné au moins une fois, W[i][j] × ln σ(θᵢ − θⱼ). Elle renvoie ce total ℓ, toujours négatif : −20,7944 quand toutes les forces sont nulles sur l'exemple à trois versions, −17,9882 après une itération et −17,8487 à l'optimum ; `bradley_terry_mm` en garde l'historique, que `main` vérifie croissant.

**`victoires_attendues(theta, n, versions)`** — Celle-ci est le contrôleur qui compare, pour chaque version, le nombre de victoires que le modèle prédit à celui qu'elle a vraiment remporté : elle reçoit les forces, la table N des duels joués et la liste des versions, et renvoie un dictionnaire qui associe à chaque version la somme, sur ses adversaires, de N[i][j] × P(i bat j). À l'optimum, ce nombre égale exactement les victoires observées, 14 pour A, ce qui traduit un gradient nul ; `main` le vérifie pour les trois versions à 10⁻⁹ près.

**`bradley_terry_mm(duels, versions, lissage, max_iter, tol)`** — Cette fonction est le statisticien patient qui cherche, par retouches successives, les forces qui expliquent le mieux tous les duels à la fois : elle reçoit les duels, les versions, un lissage de 0 par défaut, au plus 10 000 itérations et une tolérance de 10⁻¹², construit les tables W et N, ajoute si demandé des victoires virtuelles de chaque côté de chaque paire jouée, puis applique l'itération de Zermelo, πᵢ ← Wᵢ ÷ Σ Nᵢⱼ ÷ (πᵢ + πⱼ), en centrant les logarithmes pour que la somme des θ soit nulle. Elle lève `ValueError` si une version n'a aucune victoire, s'arrête quand le plus grand changement passe sous la tolérance, et renvoie les θ, le nombre d'itérations et l'historique de ℓ : ln(7/3) d'écart pour 7 victoires sur 10, 36 itérations sur l'exemple à trois versions, et un θ de la version invaincue qui grimpe à 2,279, 4,093 puis 5,837, jusqu'à ce qu'un nul virtuel le ramène à 2,679 en 415 itérations.

**`vers_points_elo(theta, base)`** — Celle-ci est le changeur de monnaie qui convertit les forces θ dans l'unité familière des points Elo : elle reçoit le dictionnaire des forces et une base de 1 500 par défaut, et renvoie pour chaque version base + 173,7178 × θ, puisque 400 ÷ ln 10 vaut 173,7178. Le modèle ne change pas, seule l'échelle change : A, de force +0,5915, vaut 1 602,7 points, et l'écart ln(7/3) entre deux versions vaut 147,2 points ; `bootstrap` s'en sert pour exprimer ses intervalles dans cette unité.

**`comparer(i, j, forces, biais, rng, deux_ordres)`** — Cette fonction est l'organisateur d'une dégustation à l'aveugle qui sait que le jury préfère le premier verre servi : elle reçoit les deux versions, leurs forces, le biais du juge, un générateur aléatoire et le choix du protocole, fait juger i lu en premier, et renvoie ce verdict, 1 ou 0, en protocole naïf. En protocole à deux ordres, elle fait aussi juger j lu en premier, retourne cet avis, et renvoie la moyenne des deux, 1, 0 ou 0,5 quand les deux avis se contredisent, ce qui annule en moyenne l'effet de position ; sur 600 duels, 283 finissent ainsi en nul.

**`generer_duels(forces, par_paire, biais, rng, deux_ordres)`** — Celle-ci est le programmateur du tournoi, qui organise toutes les rencontres possibles : elle reçoit les forces des versions, le nombre de duels par paire, le biais, le générateur et le protocole, parcourt chaque paire de versions dans l'ordre du dictionnaire, place toujours la plus récente en position i, donc lue en premier dans le protocole naïf, et ajoute `par_paire` duels notés par `comparer`. Elle renvoie la liste des triplets ; avec 100 duels par paire et quatre versions, cela fait 600 duels, et le protocole naïf finit par placer v4 devant v3, alors que v3 est la plus forte.

**`main()`** — C'est le chef d'orchestre des huit démonstrations : il vérifie le modèle et une mise à jour Elo, 0,359935 puis 1 520,48 et 1 579,52, retrouve ln(7/3) et 147,2 points pour deux versions, suit les itérations de Zermelo sur trois versions jusqu'à la convergence en 36 itérations, et contrôle que la mise à jour Elo est un pas de gradient stochastique, S − E. Il montre ensuite que l'Elo dépend de l'ordre des duels alors que Bradley-Terry n'en dépend pas, et qu'un Elo à petit K moyenné sur 500 passes s'en approche à moins d'un point, compare les deux protocoles avec un juge biaisé et leur bootstrap, fait diverger puis lisse la version invaincue et refuse deux duels invalides, avant d'afficher « OK ».

```python
"""Étape 65 bis — classement par duels : Bradley-Terry (MM de Zermelo), Elo comme gradient stochastique, nuls, bootstrap."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ECHELLE = 400 / math.log(10)        # points Elo par unité de θ : 173,7178


# ---------------------------------------------------------------- modèle et mise à jour Elo
def sigma(x: float) -> float:
    """Fonction logistique σ(x) = 1 / (1 + e^(−x))."""
    return 1.0 / (1.0 + math.exp(-x))


def p_victoire(theta_i: float, theta_j: float) -> float:
    """Bradley-Terry : P(i bat j) = σ(θi − θj)."""
    return sigma(theta_i - theta_j)


def elo_attendu(r_i: float, r_j: float) -> float:
    """Score attendu de i : E = 1 / (1 + 10^((Rj − Ri)/400))."""
    return 1.0 / (1.0 + 10 ** ((r_j - r_i) / 400))


def elo_mise_a_jour(r_i: float, r_j: float, s_i: float, k: float) -> tuple[float, float]:
    """R ← R + K(S − E) pour les deux joueurs ; ce que l'un gagne, l'autre le perd."""
    if s_i not in (0.0, 0.5, 1.0):
        raise ValueError("le score vaut 1 (victoire), 0.5 (nul) ou 0 (défaite)")
    delta = k * (s_i - elo_attendu(r_i, r_j))
    return r_i + delta, r_j - delta


def elo_en_ligne(duels: list, versions: list[str], k: float, r0: float = 1500.0) -> dict[str, float]:
    notes = {v: r0 for v in versions}
    for i, j, s in duels:
        notes[i], notes[j] = elo_mise_a_jour(notes[i], notes[j], s, k)
    return notes


# ---------------------------------------------------------------- Bradley-Terry par maximum de vraisemblance
def tableau(duels: list, versions: list[str]) -> tuple[dict, dict]:
    """W[i][j] : victoires de i sur j (un nul compte 0.5 de chaque côté, un score attendu sa valeur) ; N : duels joués."""
    w = {i: {j: 0.0 for j in versions} for i in versions}
    n = {i: {j: 0.0 for j in versions} for i in versions}
    for i, j, s in duels:
        if i == j or i not in w or j not in w:
            raise ValueError(f"duel invalide : {i} contre {j}")
        if not 0.0 <= s <= 1.0:
            raise ValueError("le score doit être dans [0, 1]")
        w[i][j] += s
        w[j][i] += 1 - s
        n[i][j] += 1
        n[j][i] += 1
    return w, n


def log_vraisemblance(theta: dict[str, float], w: dict, versions: list[str]) -> float:
    """ℓ(θ) = Σ W[i][j] · ln σ(θi − θj)."""
    return sum(w[i][j] * math.log(p_victoire(theta[i], theta[j]))
               for i in versions for j in versions if i != j and w[i][j] > 0)


def victoires_attendues(theta: dict[str, float], n: dict, versions: list[str]) -> dict[str, float]:
    return {i: sum(n[i][j] * p_victoire(theta[i], theta[j]) for j in versions if j != i) for i in versions}


def bradley_terry_mm(duels: list, versions: list[str], lissage: float = 0.0,
                     max_iter: int = 10_000, tol: float = 1e-12) -> tuple[dict[str, float], int, list[float]]:
    """Itérations MM de Zermelo : πi ← Wi / Σj Nij / (πi + πj), puis θ = ln π centré (moyenne nulle)."""
    w, n = tableau(duels, versions)
    if lissage:                                      # lissage victoires virtuelles de chaque côté : 0.5 = un nul virtuel
        for i in versions:
            for j in versions:
                if i != j and n[i][j] > 0:
                    w[i][j] += lissage
                    n[i][j] += 2 * lissage
    pi = {v: 1.0 for v in versions}
    historique = [log_vraisemblance({v: 0.0 for v in versions}, w, versions)]
    for iteration in range(1, max_iter + 1):
        nouveau = {}
        for i in versions:
            gagnes = sum(w[i][j] for j in versions if j != i)
            denom = sum(n[i][j] / (pi[i] + pi[j]) for j in versions if j != i and n[i][j] > 0)
            if gagnes == 0:
                raise ValueError(f"{i} n'a aucune victoire : son θ tend vers −∞ (ajouter un lissage)")
            nouveau[i] = gagnes / denom
        moyenne_log = sum(math.log(x) for x in nouveau.values()) / len(versions)
        theta = {v: math.log(nouveau[v]) - moyenne_log for v in versions}      # Σ θ = 0
        ecart = max(abs(theta[v] - math.log(pi[v])) for v in versions)
        pi = {v: math.exp(theta[v]) for v in versions}
        historique.append(log_vraisemblance(theta, w, versions))
        if ecart < tol:
            break
    return {v: math.log(pi[v]) for v in versions}, iteration, historique


def vers_points_elo(theta: dict[str, float], base: float = 1500.0) -> dict[str, float]:
    """R = base + (400 / ln 10) · θ : même modèle, autre unité."""
    return {v: base + ECHELLE * t for v, t in theta.items()}


# ---------------------------------------------------------------- juge simulé et protocole
def juge_simule(premier: str, second: str, forces: dict[str, float], biais: float, rng: random.Random) -> int:
    """Juge par paires qui préfère la réponse lue en premier : P(premier gagne) = σ(θp − θs + biais)."""
    return 1 if rng.random() < sigma(forces[premier] - forces[second] + biais) else 0


def comparer(i: str, j: str, forces: dict[str, float], biais: float, rng: random.Random, deux_ordres: bool) -> float:
    """Score de i contre j. Deux ordres : i lu en premier, puis j ; avis contraires = nul (0.5)."""
    a = juge_simule(i, j, forces, biais, rng)
    if not deux_ordres:
        return float(a)
    b = 1 - juge_simule(j, i, forces, biais, rng)
    return (a + b) / 2


def generer_duels(forces: dict[str, float], par_paire: int, biais: float, rng: random.Random,
                  deux_ordres: bool) -> list:
    """Toutes les paires de versions ; en protocole naïf, la version la plus récente est toujours lue en premier."""
    versions = list(forces)
    duels = []
    for x in range(len(versions)):
        for y in range(x + 1, len(versions)):
            ancienne, recente = versions[x], versions[y]
            for _ in range(par_paire):
                duels.append((recente, ancienne, comparer(recente, ancienne, forces, biais, rng, deux_ordres)))
    return duels


def bootstrap(duels: list, versions: list[str], tirages: int, graine: int) -> tuple[dict, dict]:
    """Rééchantillonne les duels avec remise ; renvoie l'intervalle à 95 % des points Elo et P(être premier)."""
    rng = random.Random(graine)
    notes = {v: [] for v in versions}
    premier = {v: 0 for v in versions}
    for _ in range(tirages):
        echantillon = [duels[rng.randrange(len(duels))] for _ in range(len(duels))]
        r = vers_points_elo(bradley_terry_mm(echantillon, versions)[0])
        for v in versions:
            notes[v].append(r[v])
        premier[max(versions, key=lambda v: (r[v], v))] += 1
    intervalles = {}
    for v in versions:
        s = sorted(notes[v])
        intervalles[v] = (s[int(0.025 * tirages)], s[int(0.975 * tirages) - 1])
    return intervalles, {v: premier[v] / tirages for v in versions}


def main() -> None:
    print("1. Le modèle et une mise à jour Elo")
    pa, pb = math.exp(0.6), math.exp(0.1)
    assert math.isclose(p_victoire(0.6, 0.1), pa / (pa + pb))               # σ(θi − θj) = πi / (πi + πj)
    e = elo_attendu(1500, 1600)
    ra, rb = elo_mise_a_jour(1500, 1600, 1.0, 32)
    print(f"   E(1500 contre 1600) = {e:.6f}   A gagne, K = 32 : {ra:.2f} et {rb:.2f}")
    assert round(e, 6) == 0.359935 and (round(ra, 2), round(rb, 2)) == (1520.48, 1579.52) and math.isclose(ra + rb, 3100)
    assert math.isclose(e, p_victoire(1500 / ECHELLE, 1600 / ECHELLE))      # même loi, autre échelle

    print("2. Deux versions : 7 victoires sur 10")
    deux = [("A", "B", 1.0)] * 7 + [("A", "B", 0.0)] * 3
    t2, _, _ = bradley_terry_mm(deux, ["A", "B"])
    ecart = t2["A"] - t2["B"]
    print(f"   θA − θB = {ecart:.6f} = ln(7/3)   soit {ECHELLE * ecart:.1f} points Elo")
    assert math.isclose(ecart, math.log(7 / 3), abs_tol=1e-9) and round(ECHELLE * ecart, 1) == 147.2

    print("3. Trois versions : itérations MM de Zermelo")
    versions = ["A", "B", "C"]
    duels = ([("A", "B", 1.0)] * 6 + [("A", "B", 0.0)] * 4 + [("A", "C", 1.0)] * 8 + [("A", "C", 0.0)] * 2
             + [("B", "C", 1.0)] * 7 + [("B", "C", 0.0)] * 3)
    w, n = tableau(duels, versions)
    _, _, h1 = bradley_terry_mm(duels, versions, max_iter=1)
    print(f"   après 1 itération : π ∝ (1.4, 1.1, 0.5)   ℓ passe de {h1[0]:.4f} à {h1[1]:.4f}")
    theta, iterations, hist = bradley_terry_mm(duels, versions)
    assert all(b >= a - 1e-12 for a, b in zip(hist, hist[1:]))               # ℓ ne décroît jamais
    att = victoires_attendues(theta, n, versions)
    elo_bt = vers_points_elo(theta)
    for v in versions:
        gagnes = sum(w[v][x] for x in versions if x != v)
        print(f"   {v} : θ = {theta[v]:+.4f}   {elo_bt[v]:.1f} points   victoires {gagnes:.0f}, attendues {att[v]:.4f}")
        assert abs(att[v] - gagnes) < 1e-9                                  # gradient nul à l'optimum
    print(f"   convergence en {iterations} itérations, ℓ = {hist[-1]:.4f}   P(A bat B) = {p_victoire(theta['A'], theta['B']):.3f}")

    print("4. Elo est un pas de gradient stochastique")
    h = 1e-6
    for s in (1.0, 0.5, 0.0):
        ell = lambda t: s * math.log(sigma(t - 1600 / ECHELLE)) + (1 - s) * math.log(sigma(1600 / ECHELLE - t))
        derivee = (ell(1500 / ECHELLE + h) - ell(1500 / ECHELLE - h)) / (2 * h)
        assert abs(derivee - (s - elo_attendu(1500, 1600))) < 1e-8          # ∂ℓ/∂θi = S − E
    print(f"   ∂ℓ/∂θA = S − E ; K = 32 correspond à un pas η = K / {ECHELLE:.4f} = {32 / ECHELLE:.4f}")

    print("5. Elo dépend de l'ordre des duels, Bradley-Terry non")
    avant, arriere = elo_en_ligne(duels, versions, 32), elo_en_ligne(list(reversed(duels)), versions, 32)
    print("   Elo, ordre du tableau : " + ", ".join(f"{v} {avant[v]:.1f}" for v in versions))
    print("   Elo, ordre inverse    : " + ", ".join(f"{v} {arriere[v]:.1f}" for v in versions))
    assert abs(avant["A"] - arriere["A"]) > 50 and math.isclose(sum(avant.values()), 4500)
    melange = list(duels)
    random.Random(65).shuffle(melange)
    assert all(abs(bradley_terry_mm(melange, versions)[0][v] - theta[v]) < 1e-9 for v in versions)
    rng, notes = random.Random(65), {v: 1500.0 for v in versions}
    cumul, passes = {v: 0.0 for v in versions}, 0
    for p in range(600):                                                     # petit K, moyenne des passes
        rng.shuffle(melange)
        for i, j, s in melange:
            notes[i], notes[j] = elo_mise_a_jour(notes[i], notes[j], s, 2)
        if p >= 100:
            passes += 1
            for v in versions:
                cumul[v] += notes[v]
    moyenne = {v: cumul[v] / passes for v in versions}
    print("   Elo K = 2, moyenne de 500 passes : " + ", ".join(f"{v} {moyenne[v]:.1f}" for v in versions))
    assert all(abs(moyenne[v] - elo_bt[v]) < 1.0 for v in versions)

    print("6. Quatre versions d'agent, juge biaisé vers la première réponse lue")
    forces = {"v1": 0.0, "v2": 0.5, "v3": 1.0, "v4": 0.8}
    biais = 0.5
    attendu_deux, attendu_naif = [], []                                      # scores attendus, sans bruit
    noms = list(forces)
    for x in range(4):
        for y in range(x + 1, 4):
            d = forces[noms[y]] - forces[noms[x]]
            attendu_deux.append((noms[y], noms[x], (sigma(d + biais) + sigma(d - biais)) / 2))
            attendu_naif.append((noms[y], noms[x], sigma(d + biais)))
    pop_deux = vers_points_elo(bradley_terry_mm(attendu_deux, noms)[0])
    pop_naif = vers_points_elo(bradley_terry_mm(attendu_naif, noms)[0])
    print("   sans bruit, deux ordres : " + ", ".join(f"{v} {pop_deux[v]:.1f}" for v in noms))
    print("   sans bruit, naïf        : " + ", ".join(f"{v} {pop_naif[v]:.1f}" for v in noms))
    assert sorted(noms, key=lambda v: -pop_deux[v]) == ["v3", "v4", "v2", "v1"] and pop_naif["v4"] > pop_naif["v3"]
    rng = random.Random(65)
    duels4 = generer_duels(forces, 100, biais, rng, deux_ordres=True)
    nuls = sum(1 for _, _, s in duels4 if s == 0.5)
    r4 = vers_points_elo(bradley_terry_mm(duels4, noms)[0])
    print(f"   100 duels par paire, deux ordres ({nuls} nuls sur {len(duels4)}) : "
          + ", ".join(f"{v} {r4[v]:.1f}" for v in noms))
    naif4 = vers_points_elo(bradley_terry_mm(generer_duels(forces, 100, biais, rng, deux_ordres=False), noms)[0])
    print("   100 duels par paire, naïf : " + ", ".join(f"{v} {naif4[v]:.1f}" for v in noms))
    intervalles, p_premier = bootstrap(duels4, noms, tirages=100, graine=65)
    for v in ("v3", "v4"):
        lo, hi = intervalles[v]
        print(f"   bootstrap {v} : [{lo:.1f} ; {hi:.1f}]   P(premier) = {p_premier[v]:.2f}")
    assert intervalles["v3"][0] < r4["v3"] < intervalles["v3"][1] and math.isclose(sum(p_premier.values()), 1)
    assert intervalles["v4"][1] > intervalles["v3"][0]                       # les intervalles se chevauchent

    print("7. Une version invaincue : l'estimateur diverge, le lissage le ramène")
    invaincue = duels + [("D", "A", 1.0)] * 10
    v5 = versions + ["D"]
    suite = [bradley_terry_mm(invaincue, v5, max_iter=m, tol=0.0)[0]["D"] for m in (10, 100, 1000)]
    print("   θD après 10, 100, 1000 itérations : " + ", ".join(f"{x:.3f}" for x in suite))
    assert suite[0] < suite[1] < suite[2]
    lisse, it_lisse, _ = bradley_terry_mm(invaincue, v5, lissage=0.5)
    print(f"   avec un nul virtuel par paire : θD = {lisse['D']:.3f} en {it_lisse} itérations")
    assert it_lisse < 10_000 and lisse["D"] == max(lisse.values())

    print("8. Entrées invalides")
    for mauvais in ([("A", "A", 1.0)], [("A", "B", 1.5)]):
        try:
            tableau(mauvais, versions)
        except ValueError as err:
            print(f"   {mauvais[0]} → ValueError : {err}")
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Le modèle et une mise à jour Elo
   E(1500 contre 1600) = 0.359935   A gagne, K = 32 : 1520.48 et 1579.52
   θA − θB = 0.847298 = ln(7/3)   soit 147.2 points Elo
…
   après 1 itération : π ∝ (1.4, 1.1, 0.5)   ℓ passe de -20.7944 à -17.9882
   A : θ = +0.5915   1602.7 points   victoires 14, attendues 14.0000
…
   convergence en 36 itérations, ℓ = -17.8487   P(A bat B) = 0.609
…
   Elo, ordre du tableau : A 1546.7, B 1509.5, C 1443.8
   Elo, ordre inverse    : A 1606.9, B 1517.6, C 1375.6
   Elo K = 2, moyenne de 500 passes : A 1602.7, B 1525.8, C 1371.5
…
   sans bruit, deux ordres : v1 1405.8, v2 1487.7, v3 1569.6, v4 1536.9
   sans bruit, naïf        : v1 1331.5, v2 1465.2, v3 1593.9, v4 1609.3
   100 duels par paire, deux ordres (283 nuls sur 600) : v1 1405.4, v2 1504.0, v3 1559.8, v4 1530.8
   100 duels par paire, naïf : v1 1345.5, v2 1496.1, v3 1563.7, v4 1594.6
   bootstrap v3 : [1540.5 ; 1575.7]   P(premier) = 0.93
   bootstrap v4 : [1509.7 ; 1554.4]   P(premier) = 0.07
…
   θD après 10, 100, 1000 itérations : 2.279, 4.093, 5.837
   avec un nul virtuel par paire : θD = 2.679 en 415 itérations
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : Elo et Bradley-Terry sont un seul modèle. Le premier le suit duel par duel, au prix d'une dépendance à l'ordre ; le second l'estime d'un coup, de façon reproductible. Le juge, lui, doit être débiaisé par le protocole, et le classement publié avec son incertitude.

Pour brancher un vrai juge, on garde le port LLM du parcours : le juge est un appel à `llm.create(...)`, avec le faux LLM pendant les tests et l'adaptateur Claude de l'étape 13 en production. Rien d'autre ne change.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`juger_paire(llm, demande, grille, reponse_1, reponse_2)`** — Cette fonction est l'huissier qui porte deux copies au juge, avec la consigne et la grille, et revient avec un seul mot : elle reçoit le modèle, la demande, la grille de notation et les deux réponses à comparer, assemble un message qui les présente dans cet ordre, puis appelle `llm.create` avec la consigne `CONSIGNE_JUGE` et aucun outil. Si le modèle refuse, elle renvoie 0,5, un nul à journaliser ; sinon elle recolle le texte de la réponse, le passe en majuscules et renvoie 1 pour « PREMIERE », 0 pour « SECONDE » et 0,5 pour toute autre réponse, y compris « EGALITE ».

**`duel(llm, demande, grille, rep_i, rep_j)`** — Celle-ci applique au vrai juge le protocole à deux ordres de `comparer`, comme un organisateur qui fait déguster les deux verres dans un sens puis dans l'autre : elle reçoit le modèle, la demande, la grille et les deux réponses, appelle `juger_paire` une première fois avec la réponse i en premier, une seconde fois avec la réponse j en premier, retourne ce second avis, et renvoie la moyenne des deux. Le résultat vaut 1, 0 ou 0,5 quand les deux lectures se contredisent, et c'est ce score qui alimente ensuite `bradley_terry_mm`.

```python
# [extrait] — juge par paires branché sur le port LLM du parcours (non exécuté par le harnais)
CONSIGNE_JUGE = ("Tu compares deux réponses à la même demande, selon la grille fournie. "
                 "Réponds par un seul mot : PREMIERE, SECONDE ou EGALITE.")


def juger_paire(llm, demande: str, grille: str, reponse_1: str, reponse_2: str) -> float:
    """Score de la réponse 1 : 1, 0 ou 0.5. On l'appelle deux fois, en inversant les réponses."""
    contenu = f"Grille : {grille}\n\nDemande : {demande}\n\nRéponse 1 :\n{reponse_1}\n\nRéponse 2 :\n{reponse_2}"
    r = llm.create(system=CONSIGNE_JUGE, messages=[{"role": "user", "content": contenu}], tools=[])
    if r.stop_reason == "refusal":
        return 0.5                                   # pas d'avis : traité comme un nul, et journalisé
    mot = "".join(b.text for b in r.content if b.type == "text").strip().upper()
    return {"PREMIERE": 1.0, "SECONDE": 0.0}.get(mot, 0.5)


def duel(llm, demande, grille, rep_i, rep_j) -> float:
    a = juger_paire(llm, demande, grille, rep_i, rep_j)
    b = 1 - juger_paire(llm, demande, grille, rep_j, rep_i)
    return (a + b) / 2                               # avis contraires : nul
```

## Squelette algorithmique

Trois algorithmes. BRADLEY_TERRY_MM prend une liste de duels et rend les forces par maximum de vraisemblance. ELO_EN_LIGNE prend la même liste, dans l'ordre où les duels arrivent, et rend des notes mises à jour à chaque duel. BOOTSTRAP_CLASSEMENT rend, pour chaque version, un intervalle à 95 % et la probabilité d'être première.

```text
ALGORITHME BRADLEY_TERRY_MM
ENTRÉES : versions v₁ … vₘ ; duels (i, j, s) avec s ∈ [0, 1] le score de i ; lissage λ ≥ 0 ; tolérance ; max_iter
SORTIE  : forces θ₁ … θₘ, de somme nulle

  POUR CHAQUE duel (i, j, s) FAIRE
      SI i = j OU s hors de [0, 1] ALORS ERREUR FIN SI
      W[i][j] ← W[i][j] + s ; W[j][i] ← W[j][i] + 1 − s ; N[i][j] ← N[i][j] + 1 ; N[j][i] ← N[j][i] + 1
  FIN POUR
  SI λ > 0 ALORS ajouter λ à W[i][j] et 2λ à N[i][j] pour chaque paire jouée FIN SI
  π ← (1, …, 1)
  POUR t de 1 à max_iter FAIRE
      POUR CHAQUE version i FAIRE
          Wᵢ ← Σⱼ W[i][j]
          SI Wᵢ = 0 ALORS ERREUR « aucune victoire : ajouter un lissage » FIN SI
          π'ᵢ ← Wᵢ / Σⱼ N[i][j] / (πᵢ + πⱼ)        ▷ maximise le minorant Q(· | π)
      FIN POUR
      μ ← moyenne des ln π'ᵢ ; θᵢ ← ln π'ᵢ − μ    ▷ recentrage : ne change pas ℓ
      écart ← maxᵢ |θᵢ − ln πᵢ| ; πᵢ ← exp(θᵢ)
      SI écart < tolérance ALORS SORTIR DE LA BOUCLE FIN SI
  FIN POUR
  RETOURNER θ
```

```text
ALGORITHME ELO_EN_LIGNE
ENTRÉES : versions ; duels (i, j, s) dans leur ordre d'arrivée, s ∈ {0 ; 0,5 ; 1} ; facteur K ; note initiale R₀
SORTIE  : notes R

  POUR CHAQUE version v FAIRE R[v] ← R₀ FIN POUR
  POUR CHAQUE duel (i, j, s) FAIRE
      E ← 1 / (1 + 10^((R[j] − R[i]) / 400))
      Δ ← K × (s − E)                              ▷ pas de gradient de taux K / c
      R[i] ← R[i] + Δ ; R[j] ← R[j] − Δ            ▷ somme conservée
  FIN POUR
  RETOURNER R
```

```text
ALGORITHME BOOTSTRAP_CLASSEMENT
ENTRÉES : duels d₁ … d_D ; versions ; M tirages ; graine
SORTIE  : pour chaque version : intervalle à 95 % et P(être première)

  générateur ← nouveau générateur initialisé avec graine
  POUR t de 1 à M FAIRE
      échantillon ← D duels tirés AVEC REMISE parmi d₁ … d_D
      R ← 1500 + c × BRADLEY_TERRY_MM(échantillon)
      ranger R[v] dans notes[v] pour chaque version v
      premier[version de plus grande note] ← premier[…] + 1
  FIN POUR
  POUR CHAQUE version v FAIRE
      trier notes[v] ; intervalle[v] ← (valeur au rang 2,5 % ; valeur au rang 97,5 %)
      P_premier[v] ← premier[v] / M
  FIN POUR
  RETOURNER intervalle, P_premier
```

**Complexité :** notons m le nombre de versions, D le nombre de duels et T le nombre d'itérations MM. BRADLEY_TERRY_MM construit les tables en O(D) puis fait T itérations de O(m²) chacune, puisque chaque version parcourt tous ses adversaires : O(D + T m²) en temps et O(m²) en mémoire pour W et N. Sur l'exemple, T = 36 et m = 3 ; quand une version est presque invaincue, la convergence devient très lente, comme le montrent les 415 itérations du cas lissé, et une méthode de Newton sur les θ, qui exploite la concavité, converge en quelques pas. ELO_EN_LIGNE coûte O(1) par duel, soit O(D) en temps et O(m) en mémoire : c'est son avantage en production, où les duels arrivent un par un. BOOTSTRAP_CLASSEMENT répète M fois un tirage en O(D) et un ajustement en O(D + T m²), plus un tri de M notes par version : O(M (D + T m²) + m M log M). Avec M = 100, D = 600 et m = 4, cela fait quelques centaines de milliers d'opérations ; c'est le coût des **appels au juge**, deux par duel, qui domine tout en production.

**Du squelette au code :** BRADLEY_TERRY_MM est `bradley_terry_mm(duels, versions, lissage, max_iter, tol)` ; la première boucle et sa garde ERREUR sont dans `tableau`, le bloc `if lissage` est la ligne du lissage, `gagnes` est Wᵢ, `denom` le dénominateur, `moyenne_log` le μ du recentrage et `ecart` l'écart. ELO_EN_LIGNE est `elo_en_ligne(duels, versions, k, r0)`, dont le corps de boucle est `elo_mise_a_jour` et le calcul de E `elo_attendu`. BOOTSTRAP_CLASSEMENT est `bootstrap(duels, versions, tirages, graine)` : le tirage avec remise est `rng.randrange`, le passage à l'échelle des points `vers_points_elo`, et les rangs 2,5 % et 97,5 % sont `int(0.025 * tirages)` et `int(0.975 * tirages) - 1`.

## Cas d'usage réels aux Émirats

Les volumes, les taux et les écarts ci-dessous sont illustratifs ; seules les règles réglementaires citées sont réelles, à confirmer avec le texte en vigueur.

### Banque — une lettre de refus qui doit rester claire et conforme

Une banque de détail de Dubaï veut remplacer le prompt qui rédige les réponses aux clients dont la demande de prêt personnel est refusée, parce que le ratio d'endettement total dépasse le plafond de 50 % fixé par la CBUAE. Aucun critère automatique ne dit si une lettre est claire, respectueuse et complète ; deux chargés de conformité comparent donc, à l'aveugle, 120 paires de lettres produites par la production et par la candidate sur les mêmes dossiers anonymisés, chaque paire étant présentée dans les deux ordres. La candidate gagne 58 duels, en perd 34 et fait 28 nuls, soit un score de 72 sur 120 : l'écart de force vaut ln(72/48) ≈ 0,405, soit environ 70 points. Un bootstrap de 1 000 tirages donne un écart compris entre environ 14 et 124 points, et une probabilité de 0,99 que la candidate soit meilleure. La banque déploie la candidate, mais garde les vérifications par programme qui ne relèvent pas du goût : mention du ratio, absence de promesse, rappel du droit de réclamation. L'indicateur suivi est l'écart de force à la production, publié avec son intervalle, à chaque changement de prompt.

### Immobilier — un juge qui préfère la première description

Une agence qui opère à Dubaï et à Abu Dhabi fait rédiger par un agent les descriptions bilingues, en arabe et en anglais, de ses biens off-plan, avec le prix en AED et la surface en sqft. Elle confie le classement des versions de prompt à un LLM juge, puis teste ce juge avant de lui faire confiance : elle lui présente 200 paires de descriptions **identiques**. Un juge sans biais devrait choisir la première dans la moitié des cas ; il la choisit 124 fois sur 200, soit 0,62, avec un intervalle de Wilson de [0,551 ; 0,685] qui exclut 0,5. Le biais de position est donc réel, d'environ ln(0,62/0,38) ≈ 0,49 en écart de force, du même ordre que celui de la démonstration (point 8). L'agence adopte le protocole à deux ordres, au prix de deux appels par duel, et fait valider un échantillon par des relecteurs bilingues. Sans ce test, la version présentée en premier dans le pipeline aurait été promue à tort. L'indicateur suivi est le taux de nuls par position inversée, qui mesure les duels où le juge ne tranche que par l'ordre.

### Secteur public — deux langues, deux classements

Un service public en ligne accessible par UAE Pass compare quatre versions de son agent bilingue. Les relecteurs arabophones et anglophones ne jugent pas les mêmes réponses, et l'équipe découvre que les duels arabes n'ont opposé que les versions 1 et 2 d'un côté, 3 et 4 de l'autre : le graphe des duels arabes a deux composantes. La démonstration du point 3 dit ce que cela implique : aucune estimation ne peut comparer la version 1 à la version 3 en arabe, quelle que soit la méthode, et un logiciel qui afficherait quand même un classement unique inventerait la réponse. L'équipe planifie donc des duels « ponts » entre les deux groupes avant de publier, et tient deux classements séparés, un par langue, parce qu'une version peut être meilleure en anglais et moins bonne en arabe. Les réponses utilisées sont tirées de conversations de test avec des identités fictives, pour respecter la PDPL. L'indicateur suivi est l'écart de force par langue, avec un contrôle automatique de la connexité du graphe des duels avant chaque publication.

### RH — Elo pendant la semaine, Bradley-Terry pour décider

Un cabinet RH présent dans plusieurs émirats teste cinq versions de l'assistant qui explique aux salariés leur indemnité de fin de service (21 jours de salaire de base par année les cinq premières années, 30 jours au-delà, plafonnée à 24 mois). Pendant une semaine, les consultants comparent des paires de réponses au fil de l'eau, et un tableau de bord affiche un classement Elo avec K = 32, mis à jour à chaque duel. En fin de semaine, l'équipe remarque que le classement change selon l'ordre dans lequel les duels du lundi ont été saisis : la démonstration (point 7) l'explique, Elo à pas constant n'est pas une estimation, c'est un suivi. La décision de déploiement se prend donc sur un ajustement de Bradley-Terry de tous les duels de la semaine, qui ne dépend pas de l'ordre, avec un bootstrap qui donne la probabilité que chaque version soit première. Le montant lui-même n'entre pas dans le duel : il est calculé par un outil déterministe et vérifié par programme, et seuls la clarté et l'exactitude des explications sont jugées. L'indicateur suivi est la probabilité d'être première de la version retenue, avec un seuil de 0,9.

### Assurance — douze victoires, zéro défaite, et une note infinie

Un assureur auto et santé, supervisé par la CBUAE, compare une nouvelle version de l'agent qui explique les décisions d'indemnisation à la version en production. Après douze duels, la nouvelle les a tous gagnés, et le script d'ajustement ne converge pas : la démonstration (point 4) l'avait prévu, l'estimateur du maximum de vraisemblance n'existe pas tant qu'une version n'a jamais perdu. Avec un nul virtuel par paire, l'écart de force vaut ln(12,5/0,5) = ln 25 ≈ 3,22, soit environ 559 points : un nombre fini, mais qui repose presque entièrement sur douze duels et sur le lissage choisi. L'équipe ne publie donc pas ce chiffre ; elle continue les duels jusqu'à ce que la nouvelle version ait perdu au moins quelques fois, ou jusqu'à ce que le bootstrap donne une probabilité d'être meilleure supérieure à 0,95. La décision d'indemnisation elle-même reste au gestionnaire : seule l'explication est comparée. L'indicateur suivi est le nombre de duels perdus par chaque version, affiché à côté de sa note pour signaler une estimation fragile.

### Crypto — un cycle que le modèle ne peut pas voir

Une plateforme d'actifs virtuels agréée par la VARA compare trois versions de l'agent qui résume les incidents de liquidité pour l'équipe d'astreinte, l'une fondée sur un modèle arabe du marché comme Jais ou Falcon, à titre d'exemple. Les duels donnent un cycle : A bat B 7 fois sur 10, B bat C 7 fois sur 10, et C bat A 7 fois sur 10. Par symétrie, l'ajustement de Bradley-Terry donne trois forces égales, θ = 0 pour tous, et prédit 0,5 pour chaque paire, alors que chaque duel observé est déséquilibré à 0,7. Le modèle n'est pas faux par hasard : il suppose la transitivité, et des forces sur une seule échelle ne peuvent pas représenter un cycle. L'équipe vérifie donc, après chaque ajustement, l'écart entre la fréquence observée et la probabilité prédite paire par paire ; ici, l'écart de 0,2 sur chaque paire signale que les versions diffèrent selon plusieurs critères (rapidité, exactitude des montants en USD, clarté), qu'il faut juger séparément. L'indicateur suivi est l'écart maximal entre observé et prédit sur les paires, avec une alerte au-dessus de 0,1.

## Pièges et limites

- **Juger dans un seul ordre.** Un juge, humain ou LLM, favorise souvent une position ; on présente chaque paire dans les deux ordres, et l'on teste le juge sur des paires identiques.
- **Prendre Elo pour une estimation.** À K constant, Elo dépend de l'ordre des duels ; pour décider, on ajuste Bradley-Terry sur tous les duels, ou l'on moyenne Elo à petit K sur de nombreux ordres.
- **Publier une note sans intervalle.** Quelques dizaines de points d'écart peuvent venir du hasard ; on publie l'intervalle du bootstrap et la probabilité d'être premier.
- **Ignorer les versions invaincues et les graphes non connexes.** L'estimateur diverge dans le premier cas et n'existe pas dans le second ; on lisse et l'on planifie des duels ponts.
- **Croire qu'une note résume tout.** Bradley-Terry suppose la transitivité ; on contrôle les écarts entre observé et prédit, et l'on juge les critères séparément quand ils divergent.

### Exercice feuille blanche

1. Sans regarder le code, écrire `tableau` et `bradley_terry_mm` à partir de la formule de mise à jour, puis retrouver θ = (+0,5915 ; +0,1491 ; −0,7406) sur le tableau de trois versions.
2. Prédire, puis vérifier : deux versions, 9 victoires sur 10. Que vaut l'écart en points ? (Réponse : ln 9 × 173,72 ≈ 381,7.) Deux versions à 1 500 font match nul avec K = 16 : que deviennent leurs notes ? (Réponse : rien ne bouge, car S = E = 1/2.)
3. Trouver le bug : une variante de `elo_mise_a_jour` renvoie `r_i + delta, r_j + delta`. Que devient la somme des notes après un duel, et pourquoi le classement dérive-t-il ? (Réponse : elle change de 2Δ ; les notes ne sont plus comparables d'un mois à l'autre, et les versions qui jouent beaucoup montent ou descendent sans raison.)

## Pour aller plus loin

Le modèle de Davidson traite les nuls comme un résultat à part entière, avec un paramètre ν ≥ 0 qui règle leur fréquence :

$$
P(i \succ j) = \frac{\pi_i}{\pi_i + \pi_j + \nu\sqrt{\pi_i \pi_j}}, \qquad P(\text{nul}) = \frac{\nu\sqrt{\pi_i \pi_j}}{\pi_i + \pi_j + \nu\sqrt{\pi_i \pi_j}}
$$

Glicko et TrueSkill ajoutent à chaque note une incertitude qui se réduit avec le nombre de duels, ce qui rend le K adaptatif. Le modèle de Plackett-Luce généralise Bradley-Terry aux classements complets de plus de deux réponses. Les classements publics de modèles par votes à l'aveugle entre deux réponses, de type « arène », reposent sur Bradley-Terry et sur le bootstrap. Enfin, l'étape 74 bis montre que le modèle de récompense de l'alignement par préférences s'entraîne avec la perte −ln σ(r_gagnante − r_perdante), qui est exactement la log-vraisemblance de Bradley-Terry.

> Étape 65 bis du parcours · Prérequis : [Exemples d'évaluation](<65-Evaluation-Exemples-Cas-Usage.md>) · Suite : [Complaisance et horizon de tâche](<65c-Complaisance-et-Horizon-de-Tache.md>)
