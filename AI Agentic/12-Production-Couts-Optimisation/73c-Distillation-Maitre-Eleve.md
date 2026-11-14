# Étape 73 ter — Optimisation — Distillation maître-élève

**Dossier :** 12-Production-Couts-Optimisation

> Étape 73 ter du parcours · Prérequis : [Quantification INT8 et INT4](<73b-Quantification-INT8-INT4.md>) · Suite : [Optimiseur Adam](<74-Optimiseur-Adam.md>)

## Définition

La **distillation** entraîne un petit modèle, l'**élève**, à imiter un grand modèle déjà entraîné, le **maître**. Au lieu d'apprendre seulement la bonne réponse (une étiquette « dure », un seul 1 et des 0), l'élève apprend la distribution complète que le maître donne sur toutes les réponses : ces **cibles douces** disent aussi quelles mauvaises réponses sont presque bonnes, une information que les étiquettes n'ont pas. Pour rendre cette information visible, on adoucit les deux softmax avec une température T > 1 (étape 2), puis on mesure l'écart entre maître et élève par la divergence de Kullback-Leibler (étape 50). La perte mélange ce terme doux, multiplié par T², et l'entropie croisée habituelle sur les vraies étiquettes. Pour les LLM, on distille souvent **au niveau des séquences** : le maître écrit des réponses, et l'élève s'entraîne simplement à les reproduire.

## Rôle dans un agent

La distillation se fait hors ligne, comme le fine-tuning de l'étape 73, mais elle change ce que coûte chaque tour de la boucle percevoir → décider → agir → observer. Un agent appelle souvent un modèle pour des décisions étroites et répétitives : router une demande, classer un ticket, extraire un JSON, juger une réponse. Un grand modèle généraliste le fait bien, mais il est lent, cher, et parfois hébergé hors du pays. On le garde comme maître, on lui fait annoter des milliers de cas, et on distille un élève dix fois plus petit qui prend la décision en production. L'élève tourne dans le centre de données de l'entreprise, ce qui règle la question de la résidence des données, et il ne dépend plus de la disponibilité ni des changements de version d'un fournisseur : c'est le chemin le plus direct vers l'indépendance que vise ce parcours. Le maître ne disparaît pas : il reste l'étalon qui sert à évaluer l'élève, et le recours pour les cas que l'élève juge incertains.

## Équation complète

Cibles douces du maître (logits v) et de l'élève (logits z) à la température T :

$$
p_i^{(T)} = \frac{e^{v_i / T}}{\sum_{k=1}^{N} e^{v_k / T}}, \qquad q_i^{(T)} = \frac{e^{z_i / T}}{\sum_{k=1}^{N} e^{z_k / T}}
$$

Perte de distillation (Hinton, Vinyals et Dean, 2015) :

$$
\mathcal{L} = \alpha \, T^2 \, D_{KL}\bigl(p^{(T)} \,\Vert\, q^{(T)}\bigr) + (1 - \alpha) \, \mathrm{CE}\bigl(y, q^{(1)}\bigr)
$$

Les deux termes, avec la KL de l'étape 50 et l'entropie croisée de l'étape 2 :

$$
D_{KL}\bigl(p^{(T)} \,\Vert\, q^{(T)}\bigr) = \sum_{i=1}^{N} p_i^{(T)} \ln \frac{p_i^{(T)}}{q_i^{(T)}}, \qquad \mathrm{CE}\bigl(y, q^{(1)}\bigr) = -\ln q_y^{(1)}
$$

Gradient par rapport aux logits de l'élève :

$$
\frac{\partial \mathcal{L}}{\partial z_j} = \alpha \, T \bigl(q_j^{(T)} - p_j^{(T)}\bigr) + (1 - \alpha)\bigl(q_j^{(1)} - y_j\bigr)
$$

Limites à haute température, avec les écarts de logits centrés Δⱼ = (zⱼ − z̄) − (vⱼ − v̄) :

$$
T \bigl(q_j^{(T)} - p_j^{(T)}\bigr) \xrightarrow[T \to \infty]{} \frac{\Delta_j}{N}, \qquad T^2 \, D_{KL}\bigl(p^{(T)} \,\Vert\, q^{(T)}\bigr) \xrightarrow[T \to \infty]{} \frac{1}{2N} \sum_{j=1}^{N} \Delta_j^2
$$

Distillation au niveau des séquences (Kim et Rush, 2016), où ŷ est la réponse écrite par le maître :

$$
\mathcal{L}_{\text{séq}} = -\sum_{y \in \mathcal{Y}} p(y \mid x) \ln q(y \mid x) \;\approx\; -\ln q(\hat{y} \mid x) = -\sum_{t=1}^{L} \ln q\bigl(\hat{y}_t \mid \hat{y}_{<t}, x\bigr)
$$

## Décryptage des symboles

$$
v, \; z
$$

Les logits du maître et ceux de l'élève pour une même entrée : deux vecteurs de N réels ; `v` et `z`, ou `logits(W_maitre, x)` et `logits(W, x)`.

$$
N
$$

Le nombre de classes (intentions, catégories, tokens du vocabulaire) : un entier ≥ 2 ; 3 dans l'exemple à la main, 4 dans l'entraînement du programme.

$$
T
$$

La température, la même qu'à l'étape 2 : un réel > 0, souvent entre 2 et 10 pendant la distillation, et toujours T = 1 quand l'élève sert en production ; `T`.

$$
p^{(T)}, \; q^{(T)}
$$

Les distributions du maître et de l'élève à la température T ; à T = 1, ce sont les probabilités ordinaires du modèle ; `softmax(v, T)`, `softmax(z, T)`.

$$
y
$$

La bonne réponse, indice d'une classe ; yⱼ vaut 1 pour cette classe et 0 pour les autres ; `y`.

$$
\alpha
$$

Le poids du terme doux, dans [0 ; 1] : α = 0 redonne l'entraînement ordinaire, α = 1 ignore les étiquettes ; `alpha`. C'est un poids, comme à l'étape 23 ; le taux d'apprentissage reste η.

$$
D_{KL}
$$

La divergence de Kullback-Leibler de l'étape 50, positive, nulle seulement si les deux distributions sont égales ; `kl(p, q)`.

$$
\mathrm{CE}
$$

L'entropie croisée avec l'étiquette dure, −ln q⁽¹⁾ᵧ ; calculée dans `perte_distillation`.

$$
\Delta_j
$$

L'écart entre les logits centrés de l'élève et ceux du maître pour la classe j : centrer, c'est retrancher la moyenne des logits, ce qui ne change pas la softmax ; `delta`.

$$
\eta
$$

Le taux d'apprentissage de la descente de gradient (étape 73) : un réel > 0, 2 dans le programme ; `eta`.

$$
W, \; W_{\text{maître}}
$$

Les poids de l'élève, une matrice N × D entraînée à partir de zéro, et ceux du maître, tirés une fois puis figés ; `W`, `W_maitre`.

$$
x, \; \hat{y}, \; \mathcal{Y}, \; L
$$

Une entrée ; la réponse que le maître écrit pour elle ; l'ensemble de toutes les réponses possibles ; la longueur de la réponse en tokens.

$$
P
$$

Le nombre de paramètres d'un modèle, qui fixe son coût d'inférence ; argument `parametres` de `cout_inference`.

## Démonstration

### 1. La température révèle les ressemblances entre classes

Le rapport de deux probabilités vaut

$$
\frac{p_i^{(T)}}{p_k^{(T)}} = e^{(v_i - v_k)/T}
$$

parce que les deux dénominateurs sont identiques et se simplifient. Pour le maître de l'exemple, v = (4 ; 2 ; 0), le rapport entre la deuxième et la troisième classe vaut e² = 7,389 à T = 1, e = 2,718 à T = 2 et exp(0,5) = 1,649 à T = 4. À T = 1, les deux mauvaises classes reçoivent 0,1173 et 0,0159 : presque rien, et une étiquette dure en dirait autant. À T = 4, elles reçoivent 0,3072 et 0,1863 : l'élève voit clairement que la deuxième classe est « presque » la bonne, et la troisième beaucoup moins.

L'entropie, elle, croît avec T. Posons β = 1/T. Comme ln pᵢ = βvᵢ − ln Z avec Z = ∑ₖ e^(βvₖ), l'entropie vaut H = ln Z − β·E[v], où E désigne la moyenne sous p. La dérivée de ln Z par rapport à β est E[v], et celle de E[v] est la variance Var(v) ; d'où

$$
\frac{dH}{d\beta} = \mathbb{E}[v] - \mathbb{E}[v] - \beta \operatorname{Var}(v) = -\beta \operatorname{Var}(v), \qquad \frac{dH}{dT} = \frac{dH}{d\beta} \cdot \frac{d\beta}{dT} = \frac{\operatorname{Var}(v)}{T^3} \ge 0
$$

avec égalité seulement si tous les logits sont égaux. Sur l'exemple, l'entropie vaut 0,4411, puis 0,8324, puis 1,0202, et tend vers ln 3 = 1,0986, celle de la loi uniforme.

### 2. Le gradient du terme doux

La KL s'écrit −∑ pᵢ ln qᵢ + ∑ pᵢ ln pᵢ (étape 50, point 6). Le second morceau ne dépend pas de l'élève : seule l'entropie croisée avec les cibles douces compte. L'étape 2 a montré que ∂ ln qᵢ / ∂zⱼ = (δᵢⱼ − qⱼ)/T pour une softmax à la température T. Donc

$$
\frac{\partial}{\partial z_j}\Bigl(-\sum_{i} p_i \ln q_i\Bigr) = -\frac{1}{T} \sum_{i} p_i \,(\delta_{ij} - q_j) = \frac{1}{T}\Bigl(q_j \sum_i p_i - p_j\Bigr) = \frac{q_j - p_j}{T}
$$

La dernière égalité tient parce que les pᵢ somment à 1. C'est le gradient p − y de l'étape 2, avec une cible douce à la place de l'étiquette dure. Sur l'exemple, avec l'élève z = (1 ; 1 ; 0) à T = 1, il vaut (0,4223 − 0,8668 ; 0,4223 − 0,1173 ; 0,1554 − 0,0159) = (−0,4445 ; 0,3050 ; 0,1395) : la descente fait monter la classe 1, que le maître préfère, et descendre les deux autres.

### 3. Pourquoi le facteur T²

On centre les logits, ce qui ne change pas la softmax : ∑ vₖ = ∑ zₖ = 0. Pour T grand, exp(a/T) = 1 + a/T + O(1/T²), donc la somme des exponentielles vaut N + O(1/T²), parce que la somme des vₖ / T est nulle. Il vient

$$
p_j^{(T)} = \frac{1}{N} + \frac{v_j}{N T} + O\!\left(\frac{1}{T^2}\right), \qquad q_j^{(T)} - p_j^{(T)} = \frac{z_j - v_j}{N T} + O\!\left(\frac{1}{T^2}\right)
$$

Avec le point 2, le gradient du terme doux vaut donc

$$
\frac{q_j^{(T)} - p_j^{(T)}}{T} = \frac{z_j - v_j}{N T^2} + O\!\left(\frac{1}{T^3}\right)
$$

Il décroît comme 1/T², alors que le gradient du terme dur, q⁽¹⁾ − y, ne dépend pas de T. Sans correction, monter la température pour révéler les ressemblances éteindrait le signal même qu'on veut transmettre, et changerait l'équilibre entre les deux termes à chaque réglage de T. Multiplier le terme doux par T² rend son gradient égal à T(q⁽ᵀ⁾ − p⁽ᵀ⁾), qui tend vers (zⱼ − vⱼ)/N : une grandeur indépendante de T. On peut alors changer T sans retoucher α ni η. Le programme le vérifie : la norme du gradient doux passe de 0,557 à T = 1 à 7,2 × 10⁻⁷ à T = 1 000, alors que T² fois cette norme reste entre 0,557 et 0,730, et tend vers ‖Δ‖/N = 0,7201. Dans l'entraînement de la partie 4, oublier T² à T = 4 fait tomber l'accord avec le maître de 0,990 à 0,843 pour le même nombre de pas.

### 4. À haute température, distiller revient à régresser les logits

On écrit q = p + δ avec ∑ δᵢ = 0 et δ = O(1/T). Le développement ln(1 + u) = u − u²/2 + O(u³) donne

$$
D_{KL}(p \,\Vert\, q) = -\sum_i p_i \ln\Bigl(1 + \frac{\delta_i}{p_i}\Bigr) = -\sum_i \delta_i + \sum_i \frac{\delta_i^2}{2 p_i} + O(\delta^3) = \sum_i \frac{\delta_i^2}{2 p_i} + O\!\left(\frac{1}{T^3}\right)
$$

parce que la somme des δᵢ est nulle. Avec pᵢ ≈ 1/N et δᵢ ≈ Δᵢ/(NT), on obtient T²·KL → (1/2N) ∑ Δᵢ². À haute température, la distillation devient une **régression aux moindres carrés** des logits centrés de l'élève sur ceux du maître. Sur l'exemple, v centré vaut (2 ; 0 ; −2), z centré vaut (1/3 ; 1/3 ; −2/3), donc Δ = (−5/3 ; 1/3 ; 4/3), et la limite vaut (25 + 1 + 16) / (9 × 6) = 42/54 = 0,7778. Le programme trouve 0,7780 à T = 1 000. À température modérée, la perte se situe entre deux extrêmes : copier l'étiquette du maître (T petit) et copier tous ses logits (T grand).

### 5. Le gradient total, et la température en production

Le terme doux donne α·T²·(q⁽ᵀ⁾ − p⁽ᵀ⁾)/T = αT(q⁽ᵀ⁾ − p⁽ᵀ⁾), le terme dur (1 − α)(q⁽¹⁾ − y) : c'est le gradient de l'équation complète. La température ne sert qu'à l'entraînement : en production, l'élève calcule sa softmax à T = 1, comme le maître auquel on le compare. Garder T = 4 à l'inférence ne change pas la classe choisie, puisque l'ordre des logits est conservé, mais aplatit toutes les probabilités : un seuil de confiance de 0,9 réglé à T = 1 ne serait presque jamais franchi.

### 6. Distillation au niveau des séquences

Pour un LLM, une réponse est une suite de L tokens. La distillation « mot à mot » applique la perte précédente à chaque position, ce qui exige les logits du maître sur tout le vocabulaire à chaque token : c'est possible avec un maître ouvert qu'on fait tourner soi-même, pas avec une API qui ne renvoie que du texte. La version « séquence » vise directement la loi du maître sur les réponses entières, −∑ p(y|x) ln q(y|x). Cette somme a |V|ᴸ termes : pour 30 000 tokens et L = 20, environ 3,49 × 10⁸⁹, ce qu'aucun calcul ne parcourt. On la remplace par la réponse la plus probable du maître, ŷ, obtenue par décodage glouton ou par faisceau, ou par quelques réponses tirées au hasard. Enfin, la règle de la chaîne des probabilités écrit q(ŷ | x) comme le produit, sur t = 1, …, L, des probabilités de chaque token ŷₜ sachant x et les tokens qui le précèdent, donc

$$
-\ln q(\hat{y} \mid x) = -\sum_{t=1}^{L} \ln q\bigl(\hat{y}_t \mid \hat{y}_{<t}, x\bigr)
$$

C'est exactement la perte d'un fine-tuning supervisé ordinaire sur le texte du maître (étape 73, et étape 74 bis pour le gabarit de conversation). Distiller par séquences, c'est donc **générer un jeu d'entraînement avec le maître, puis faire un fine-tuning dessus**. Le prix de l'approximation se lit sur un exemple : si le maître répartit sa masse en (0,6 ; 0,25 ; 0,1 ; 0,05) sur quatre réponses, d'entropie 1,0331, l'élève entraîné sur le seul mode ne voit que 60 % de cette masse et apprend à répondre la première réponse avec certitude. C'est souvent ce qu'on veut pour une extraction ou un routage, mais l'élève devient plus tranché que son maître. Faute de logits, on compense par le **volume** : dans la partie 5 du programme, l'élève qui n'apprend que les décisions du maître passe de 0,563 d'accord avec 8 exemples à 0,787 avec 32 et 0,910 avec 96. Attention : les conditions d'utilisation de nombreux fournisseurs interdisent d'entraîner un modèle concurrent sur les sorties de leurs modèles, et certaines licences de modèles ouverts encadrent cet usage ; c'est à vérifier avant tout projet.

### 7. Ce que l'élève fait gagner

Une approximation usuelle compte environ 2 opérations par paramètre et par token généré, et 2 octets par paramètre en FP16. Un maître de 70 milliards de paramètres coûte alors 1,4 × 10¹¹ opérations par token et 140 Go de poids ; un élève de 8 milliards, 1,6 × 10¹⁰ opérations et 16 Go, soit 8,75 fois moins de calcul et un modèle qui tient sur un seul accélérateur. Ces tailles sont illustratives. Pour un ordre de grandeur publié, les auteurs de DistilBERT (Sanh et al., 2019) annoncent un modèle 40 % plus petit et 60 % plus rapide que BERT, qui conserve 97 % de ses performances de compréhension du langage sur leur banc d'essai. La distillation se combine avec la quantification de l'étape 73 bis : on distille d'abord, puis on quantifie l'élève.

### 8. Exemple fait à la main (le code reprend ces nombres)

Maître v = (4 ; 2 ; 0), élève z = (1 ; 1 ; 0), bonne classe 0.

- **T = 1.** p = (0,8668 ; 0,1173 ; 0,0159) et q = (e ; e ; 1)/(2e + 1) = (0,4223 ; 0,4223 ; 0,1554). KL = 0,8668 ln(0,8668/0,4223) + 0,1173 ln(0,1173/0,4223) + 0,0159 ln(0,0159/0,1554) = 0,6233 − 0,1503 − 0,0362 = 0,4368.
- **T = 2.** p = (0,6652 ; 0,2447 ; 0,0900) et q = (0,3837 ; 0,3837 ; 0,2327) ; KL = 0,1706 ; gradient (q − p)/2 = (−0,1408 ; 0,0695 ; 0,0713).
- **T = 4, α = 0,7.** p⁽⁴⁾ = (0,5065 ; 0,3072 ; 0,1863) et q⁽⁴⁾ = (0,3599 ; 0,3599 ; 0,2803), d'où KL ≈ 0,0484 et T²·KL ≈ 0,7747. Le terme dur vaut −ln 0,4223 = 0,8620. La perte vaut 0,7 × 0,7747 + 0,3 × 0,8620 = 0,8008. Le gradient vaut 2,8 × (−0,1466 ; 0,0527 ; 0,0940) + 0,3 × (−0,5777 ; 0,4223 ; 0,1554) = (−0,5838 ; 0,2742 ; 0,3096).

## Effets et comportement

- **T petit, l'élève copie la décision ; T grand, il copie les logits.** Entre les deux, il apprend la décision et les ressemblances entre classes.
- **Les cibles douces valent beaucoup d'exemples.** Avec 8 exemples, l'élève qui n'a que les étiquettes s'accorde avec le maître sur 56,3 % des cas de test ; avec les cibles à T = 4, sur 99,0 %.
- **Le facteur T² rend T indépendant de η.** Sans lui, le terme doux s'éteint en 1/T² et l'entraînement ralentit dès qu'on augmente T.
- **α arbitre entre le maître et la vérité.** Si le maître se trompe sur une partie des données, un α plus faible laisse les vraies étiquettes corriger l'élève.
- **Sans logits, le volume remplace la douceur.** Un maître qui ne donne que du texte s'utilise par séquences : il faut alors beaucoup plus de sorties pour le même accord.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| p⁽ᵀ⁾, q⁽ᵀ⁾ | `softmax(v, T)`, `softmax(z, T)` |
| H(p) | `entropie(p)` |
| D_KL(p ‖ q) | `kl(p, q)` |
| ℒ = αT²·KL + (1 − α)·CE | `perte_distillation(z, v, y, T, alpha)` |
| ∂ℒ/∂z | `gradient_distillation(z, v, y, T, alpha, avec_t2, p_T)` |
| Δ (logits centrés) | `centrer(z)`, `centrer(v)`, `delta` |
| z = W x | `logits(W, x)` |
| descente de gradient sur l'élève | `entrainer_eleve(X, V, Y, T, alpha, eta, epoques, avec_t2)` |
| accord et KL avec le maître | `accord(W, W_maitre, X_test)` |
| 2P opérations, 2P octets | `cout_inference(parametres)` |

### Déroulé, ligne par ligne

**`softmax(z, T)`** refuse T ≤ 0, retranche le plus grand logit avant de diviser par T et de prendre l'exponentielle, puis normalise. Pour v = (4 ; 2 ; 0) et T = 4, les exposants valent 0, −0,5 et −1, et le résultat (0,5065 ; 0,3072 ; 0,1863).

**`entropie(p)`** et **`kl(p, q)`** suivent l'étape 50 : les termes où p vaut 0 sont omis, et `kl` renvoie `math.inf` si q s'annule là où p ne s'annule pas.

**`verifier(T, alpha)`** lève `ValueError` si T ≤ 0 ou si α sort de [0 ; 1].

**`perte_distillation(z, v, y, T, alpha)`.** `douce` est la KL entre les deux softmax à la température T ; `dure` est −ln de la probabilité que l'élève donne à la bonne classe, à T = 1. La fonction renvoie α·T²·douce + (1 − α)·dure : 0,8008 sur l'exemple.

**`gradient_distillation(z, v, y, T, alpha, avec_t2, p_T)`.**

- Si `p_T` est fourni, on réutilise les cibles douces déjà calculées : le maître est figé, inutile de refaire sa softmax à chaque pas.
- `q_T = q if T == 1.0 else softmax(z, T)` évite une softmax en double quand T = 1.
- `poids` vaut α·T avec le facteur T², α/T sans lui : c'est la seule différence entre les deux versions comparées en partie 4.
- La compréhension renvoie, pour chaque classe j, `poids * (q_T[j] - p_T[j]) + (1 - alpha) * (q[j] - y_j)`.

**`centrer(v)`** retranche la moyenne : (4 ; 2 ; 0) devient (2 ; 0 ; −2).

**`logits(W, x)`** calcule un produit scalaire par classe avec `sum(map(operator.mul, ligne, x))`, la forme la plus rapide en Python pur. **`argmax(v)`** départage une égalité par le plus petit indice.

**`entrainer_eleve(X, V, Y, T, alpha, eta, epoques, avec_t2)`.**

- `cibles_douces` : les softmax du maître à la température T, calculées une fois.
- À chaque époque, `G` accumule, pour chaque exemple, le gradient par rapport aux logits multiplié par l'entrée : ∂ℒ/∂Wₖⱼ = (∂ℒ/∂zₖ)·xⱼ, divisé par le nombre d'exemples pour obtenir la moyenne.
- La dernière ligne de la boucle applique W ← W − ηG à toute la matrice, après avoir parcouru tous les exemples.

**`accord(W, W_maitre, X_test)`** compte la part des 300 entrées de test où l'élève choisit la même classe que le maître, et la KL moyenne à T = 1 entre leurs distributions.

**`cout_inference(parametres)`** renvoie 2P opérations par token et 2P / 10⁹ Go.

**`main()`, bloc par bloc.**

1. Le maître v = (4 ; 2 ; 0) à T = 1, 2 et 4 : l'entropie croît strictement et reste sous ln 3, et le rapport p₂/p₃ vaut e², e, puis exp(0,5) (point 1).
2. L'élève z = (1 ; 1 ; 0) : KL à T = 1 et T = 2, gradient (q − p)/T vérifié coordonnée par coordonnée par différences finies (point 2). Puis la perte complète et son gradient à T = 4, α = 0,7, eux aussi vérifiés par différences finies (point 8).
3. Le facteur T² : de T = 1 à T = 1 000, la norme du gradient doux s'effondre, T² fois cette norme se stabilise, T(q⁽ᵀ⁾ − p⁽ᵀ⁾) tend vers Δ/N et T²·KL vers 0,7778 (points 3 et 4).
4. Le maître est une matrice 4 × 6 tirée avec la graine 73, multipliée par 3 pour qu'il soit très sûr de lui, puis figée. Seuls 8 exemples sont étiquetés. Quatre élèves partent de W = 0 et font 300 pas de descente de gradient avec η = 2 : étiquettes seules, T = 1, T = 4, et T = 4 sans le facteur T². Les `assert` vérifient l'ordre 0,563 < 0,760 < 0,990, que la version sans T² fait moins bien que la version avec, et que la KL au maître décroît dans le même ordre.
5. Un maître qui ne donne que ses décisions : on lui fait étiqueter 24, puis 88 entrées de plus, et l'élève entraîné sur ces pseudo-étiquettes passe de 0,563 à 0,787 puis 0,910 d'accord. Puis les nombres du point 6 : |V|ᴸ et l'entropie 1,0331.
6. Le coût d'inférence du point 7, puis deux entrées invalides : T = 0 et α = 1,5.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`entropie(p)`** — Cette fonction mesure l'hésitation d'un maître, comme un examinateur qui note à quel point un oracle répartit ses paris au lieu de tout miser sur une seule réponse : elle reçoit une distribution de probabilités et renvoie −Σ p ln p, en omettant les termes où p vaut 0, dont la contribution limite est nulle. Pour le maître de logits 4, 2 et 0, elle vaut 0,4411 à T = 1 et 1,0202 à T = 4, toujours sous ln 3, ce qui montre que la température rend les cibles plus douces et donc plus bavardes.

**`kl(p, q)`** — Celle-ci est le traducteur sévère qui compte ce que la distribution de l'élève perd par rapport à celle du maître : elle reçoit deux distributions, additionne p ln(p/q) sur les classes où p n'est pas nulle et renvoie l'infini dès qu'une classe possible sous p est déclarée impossible sous q. Entre le maître de logits 4, 2, 0 et l'élève de logits 1, 1, 0 à T = 1, elle vaut 0,4368 ; elle forme la partie douce de `perte_distillation` et la mesure de proximité de `accord`.

**`verifier(T, alpha)`** — Cette fonction est le contrôleur des réglages, posté à l'entrée de la perte et de son gradient : elle reçoit la température T et le poids α, ne renvoie rien si T est strictement positive et si α est compris entre 0 et 1 inclus, et lève une `ValueError` sinon. `perte_distillation` et `gradient_distillation` l'appellent en premier, si bien que les deux appels de la fin de `main`, avec T = 0 puis avec α = 1,5, sont refusés avant tout calcul.

**`gradient_distillation(z, v, y, T, alpha, avec_t2, p_T)`** — Celle-ci est le moniteur qui dit à l'élève dans quel sens corriger chacun de ses logits : elle reçoit les logits de l'élève et du maître, la bonne classe, T, α, un drapeau qui garde ou retire le facteur T², vrai par défaut, et les cibles douces du maître si elles sont déjà calculées, puis vérifie les réglages, calcule les softmax de l'élève à T = 1 et à T, et renvoie pour chaque classe α T (qⱼᵀ − pⱼᵀ) + (1 − α)(qⱼ − yⱼ), ou α (qⱼᵀ − pⱼᵀ)/T sans le facteur T². Pour l'élève de logits 1, 1, 0 avec T = 4 et α = 0,7, elle renvoie environ −0,5838, 0,2742 et 0,3096, ce que `main` contrôle par différences finies sur la perte.

**`centrer(v)`** — Cette petite fonction est le niveleur qui ramène une liste de logits autour de zéro : elle reçoit une liste de nombres, calcule leur moyenne et renvoie la liste de leurs écarts à cette moyenne, si bien que 4, 2 et 0 deviennent 2, 0 et −2. Elle sert à former l'écart Δ entre les logits centrés de l'élève et du maître, −5/3, 1/3 et 4/3, d'où `main` tire les limites à haute température, Δ/N pour le gradient et Σ Δ² / 2N = 0,7778 pour T² fois la KL.

**`logits(W, x)`** — Celle-ci est le guichet de l'élève linéaire, qui note chaque classe d'un score : elle reçoit une matrice de poids, une ligne par classe, et une entrée x, et renvoie pour chaque ligne le produit scalaire de cette ligne avec x, calculé par `sum(map(operator.mul, ligne, x))`, la forme la plus rapide en Python pur. Elle sert aussi bien au maître, une matrice 4 × 6 tirée avec la graine 73 puis multipliée par 3, qu'à l'élève en cours d'entraînement.

**`argmax(v)`** — Cette fonction est l'arbitre qui désigne le vainqueur d'une liste de scores : elle reçoit une liste et renvoie l'indice du plus grand score, en départageant une égalité au profit du plus petit indice grâce à la clé (v[k], −k). Elle transforme les logits du maître en étiquettes dures pour les exemples d'entraînement et pour les pseudo-étiquettes de la section 5, et permet à `accord` de comparer la décision de l'élève à celle du maître.

**`entrainer_eleve(X, V, Y, T, alpha, eta, epoques, avec_t2)`** — Celle-ci est l'école de l'élève, où il apprend en imitant un maître figé : elle reçoit les entrées, les logits du maître, les étiquettes, T, α, le pas η, le nombre d'époques et le drapeau du facteur T², vrai par défaut, calcule une seule fois les cibles douces du maître, part de poids nuls, puis, à chaque époque, accumule pour chaque exemple le gradient de `gradient_distillation` multiplié par l'entrée, divisé par le nombre d'exemples, et applique W ← W − ηG à toute la matrice. Elle renvoie la matrice apprise ; avec 8 exemples, 300 époques et η = 2, l'élève à T = 4 retrouve la décision du maître sur 99 % des entrées de test.

**`accord(W, W_maitre, X_test)`** — Cette fonction est le jury de fin d'année qui compare l'élève au maître sur des copies qu'aucun des deux n'a vues : elle reçoit les poids de l'élève, ceux du maître et les entrées de test, calcule pour chaque entrée les logits des deux, compte les cas où leurs argmax coïncident et additionne la KL à T = 1 entre leurs distributions. Elle renvoie la part d'accord et la KL moyenne sur les 300 entrées : 0,563 et 1,5386 avec les étiquettes seules, 0,990 et 0,0003 avec les cibles douces à T = 4, et 0,843 et 0,1499 quand on retire le facteur T².

**`cout_inference(parametres)`** — Celle-ci est le comptable qui chiffre ce que coûte chaque token produit par un modèle : elle reçoit un nombre de paramètres et renvoie, selon l'approximation usuelle, deux opérations par paramètre et par token, puis la taille des poids en Go à 2 octets par paramètre en FP16. Pour le maître illustratif de 70 milliards de paramètres, elle donne 1,4 × 10¹¹ opérations par token et 140 Go, 8,75 fois plus que pour l'élève de 8 milliards.

**`main()`** — C'est le directeur d'études qui fait passer six épreuves au programme : il montre d'abord que l'entropie du maître croît avec T sans dépasser ln 3, puis calcule sur l'exemple à la main la KL, la perte de 0,8008 et le gradient, tous vérifiés par différences finies, et suit le gradient doux de T = 1 à T = 1 000 pour montrer que seul T² fois ce gradient se stabilise. Il entraîne ensuite quatre élèves sur 8 exemples et vérifie l'ordre 0,563 < 0,760 < 0,990, fait monter l'accord de 0,563 à 0,910 avec des pseudo-étiquettes, chiffre le coût d'inférence, et termine en vérifiant que T = 0 et α = 1,5 sont refusés.

```python
"""Étape 73 ter — distillation maître-élève : cibles douces, facteur T², limite « régression des logits »,
élève softmax linéaire entraîné en Python pur, pseudo-étiquettes du maître, coût d'inférence."""
import math
import operator
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- softmax, entropie, KL (étapes 2 et 50)
def softmax(z: list[float], T: float = 1.0) -> list[float]:
    """p_i = e^(z_i/T) / Σ_j e^(z_j/T), en retranchant le maximum avant l'exponentielle."""
    if T <= 0:
        raise ValueError("la température doit être > 0")
    pic = max(z)
    e = [math.exp((v - pic) / T) for v in z]
    s = sum(e)
    return [v / s for v in e]


def entropie(p: list[float]) -> float:
    return -sum(a * math.log(a) for a in p if a > 0)


def kl(p: list[float], q: list[float]) -> float:
    """D_KL(p ‖ q) = Σ p ln(p/q) ; +∞ si q(x) = 0 là où p(x) > 0 (étape 50)."""
    total = 0.0
    for a, b in zip(p, q):
        if a > 0:
            if b == 0:
                return math.inf
            total += a * math.log(a / b)
    return total


def verifier(T: float, alpha: float) -> None:
    if T <= 0 or not 0.0 <= alpha <= 1.0:
        raise ValueError("il faut T > 0 et 0 <= α <= 1")


def perte_distillation(z: list[float], v: list[float], y: int, T: float, alpha: float) -> float:
    """ℒ = α T² KL(p_maître,T ‖ p_élève,T) + (1 − α) CE(y, p_élève)."""
    verifier(T, alpha)
    douce = kl(softmax(v, T), softmax(z, T))
    dure = -math.log(softmax(z)[y])
    return alpha * T * T * douce + (1 - alpha) * dure


def gradient_distillation(z: list[float], v: list[float], y: int, T: float, alpha: float,
                          avec_t2: bool = True, p_T: list[float] | None = None) -> list[float]:
    """∂ℒ/∂z_j = α T (q_j^T − p_j^T) + (1 − α)(q_j − y_j) ; sans T², le premier terme vaut α (q^T − p^T) / T.
    p_T, les cibles douces du maître, peut être fourni déjà calculé : le maître ne change pas."""
    verifier(T, alpha)
    p_T = softmax(v, T) if p_T is None else p_T
    q = softmax(z)
    q_T = q if T == 1.0 else softmax(z, T)
    poids = alpha * T if avec_t2 else alpha / T
    return [poids * (b - a) + (1 - alpha) * (c - (1.0 if j == y else 0.0))
            for j, (a, b, c) in enumerate(zip(p_T, q_T, q))]


def centrer(v: list[float]) -> list[float]:
    m = sum(v) / len(v)
    return [a - m for a in v]


# ---------------------------------------------------------------- élève softmax linéaire, maître à logits fixes
def logits(W: list[list[float]], x: list[float]) -> list[float]:
    """z = W x : un produit scalaire par classe."""
    return [sum(map(operator.mul, ligne, x)) for ligne in W]


def argmax(v: list[float]) -> int:
    return max(range(len(v)), key=lambda k: (v[k], -k))


def entrainer_eleve(X, V, Y, T: float, alpha: float, eta: float, epoques: int, avec_t2: bool = True):
    """Descente de gradient sur le lot complet ; l'élève part de W = 0. V : logits du maître, Y : étiquettes."""
    n_classes, dim = len(V[0]), len(X[0])
    cibles_douces = [softmax(v, T) for v in V]          # calculées une fois : le maître est figé
    W = [[0.0] * dim for _ in range(n_classes)]
    for _ in range(epoques):
        G = [[0.0] * dim for _ in range(n_classes)]
        for x, v, y, p_T in zip(X, V, Y, cibles_douces):
            g = gradient_distillation(logits(W, x), v, y, T, alpha, avec_t2, p_T)
            for k in range(n_classes):
                gk = g[k] / len(X)
                G[k] = [a + gk * b for a, b in zip(G[k], x)]          # ∂ℒ/∂W = (∂ℒ/∂z) xᵀ
        W = [[w - eta * g for w, g in zip(ligne, gl)] for ligne, gl in zip(W, G)]
    return W


def accord(W, W_maitre, X_test) -> tuple[float, float]:
    """Part des entrées où l'élève choisit la même classe que le maître, et KL moyenne à T = 1."""
    meme = 0
    divergence = 0.0
    for x in X_test:
        v, z = logits(W_maitre, x), logits(W, x)
        meme += argmax(v) == argmax(z)
        divergence += kl(softmax(v), softmax(z))
    return meme / len(X_test), divergence / len(X_test)


def cout_inference(parametres: float) -> tuple[float, float]:
    """Approximation usuelle : 2 opérations par paramètre et par token ; 2 octets par paramètre en FP16."""
    return 2 * parametres, 2 * parametres / 1e9


def main() -> None:
    print("1. Cibles douces : le maître (logits 4, 2, 0) à plusieurs températures")
    v = [4.0, 2.0, 0.0]
    entropies = []
    for T in (1.0, 2.0, 4.0):
        p = softmax(v, T)
        entropies.append(entropie(p))
        print(f"  T = {T} : p = {[round(a, 4) for a in p]}   entropie = {entropies[-1]:.4f}   p₂/p₃ = {p[1] / p[2]:.3f}")
    assert entropies[0] < entropies[1] < entropies[2] < math.log(3)
    assert [round(a, 4) for a in softmax(v)] == [0.8668, 0.1173, 0.0159]

    print("2. Exemple à la main : élève (1, 1, 0), bonne classe 0")
    z, y = [1.0, 1.0, 0.0], 0
    for T in (1.0, 2.0):
        p_T, q_T = softmax(v, T), softmax(z, T)
        g = [(b - a) / T for a, b in zip(p_T, q_T)]
        print(f"  T = {T} : q = {[round(a, 4) for a in q_T]}   KL = {kl(p_T, q_T):.4f}   ∂KL/∂z = {[round(a, 4) for a in g]}")
        for j in range(3):                               # ∂KL/∂z_j = (q_j − p_j)/T, vérifié par différence finie
            zp, zm = z[:], z[:]
            zp[j] += 1e-6
            zm[j] -= 1e-6
            assert abs((kl(p_T, softmax(zp, T)) - kl(p_T, softmax(zm, T))) / 2e-6 - g[j]) < 1e-8
    assert round(kl(softmax(v), softmax(z)), 4) == 0.4368
    perte = perte_distillation(z, v, y, 4.0, 0.7)
    grad = gradient_distillation(z, v, y, 4.0, 0.7)
    for j in range(3):
        zp, zm = z[:], z[:]
        zp[j] += 1e-6
        zm[j] -= 1e-6
        num = (perte_distillation(zp, v, y, 4.0, 0.7) - perte_distillation(zm, v, y, 4.0, 0.7)) / 2e-6
        assert abs(num - grad[j]) < 1e-7
    print(f"  T = 4, α = 0.7 : ℒ = {perte:.4f}   ∂ℒ/∂z = {[round(a, 4) for a in grad]} (vérifié par différences finies)")

    print("3. Le facteur T² : sans lui, le gradient doux s'éteint en 1/T²")
    delta = [a - b for a, b in zip(centrer(z), centrer(v))]   # (−5/3, 1/3, 4/3)
    limite_kl = sum(d * d for d in delta) / (2 * len(v))
    for T in (1.0, 2.0, 10.0, 100.0, 1000.0):
        p_T, q_T = softmax(v, T), softmax(z, T)
        g = [(b - a) / T for a, b in zip(p_T, q_T)]
        norme = math.sqrt(sum(a * a for a in g))
        print(f"  T = {T:>6} : ‖∂KL/∂z‖ = {norme:.2e}   T²·‖∂KL/∂z‖ = {T * T * norme:.4f}   T²·KL = {T * T * kl(p_T, q_T):.4f}")
    p_T, q_T = softmax(v, 1000.0), softmax(z, 1000.0)
    assert all(abs(1000.0 * (b - a) - d / 3) < 1e-3 for a, b, d in zip(p_T, q_T, delta))
    assert abs(1000.0 ** 2 * kl(p_T, q_T) - limite_kl) < 1e-3 and round(limite_kl, 4) == 0.7778
    print(f"  limite : T(q^T − p^T) → Δ/N = {[round(d / 3, 4) for d in delta]} ; T²·KL → Σ Δ² / 2N = {limite_kl:.4f}")

    print("4. Élève linéaire, 8 exemples étiquetés, maître à logits fixes (4 intentions, 6 traits)")
    rng = random.Random(73)
    W_maitre = [[3.0 * rng.gauss(0, 1) for _ in range(6)] for _ in range(4)]   # jamais entraîné : logits fixés
    X = [[rng.gauss(0, 1) for _ in range(6)] for _ in range(8)]
    X_test = [[rng.gauss(0, 1) for _ in range(6)] for _ in range(300)]
    V = [logits(W_maitre, x) for x in X]
    Y = [argmax(lv) for lv in V]
    resultats = {}
    for nom, T, alpha, avec_t2 in (("étiquettes seules", 1.0, 0.0, True), ("T = 1, α = 0.9", 1.0, 0.9, True),
                                   ("T = 4, α = 0.9", 4.0, 0.9, True), ("T = 4 sans T²", 4.0, 0.9, False)):
        W = entrainer_eleve(X, V, Y, T, alpha, eta=2.0, epoques=300, avec_t2=avec_t2)
        resultats[nom] = accord(W, W_maitre, X_test)
        print(f"  {nom:<18} : accord avec le maître = {resultats[nom][0]:.3f}   KL moyenne = {resultats[nom][1]:.4f}")
    a_dur, a_t1, a_t4, a_sans = (resultats[k][0] for k in resultats)
    assert a_dur < a_t1 < a_t4 and a_t4 >= 0.98 and a_sans < a_t4
    assert resultats["T = 4, α = 0.9"][1] < resultats["T = 1, α = 0.9"][1] < resultats["étiquettes seules"][1]

    print("5. Sans logits (maître accessible par son texte seulement) : beaucoup de pseudo-étiquettes")
    reserve = [[rng.gauss(0, 1) for _ in range(6)] for _ in range(88)]
    accords = []
    for m in (8, 32, 96):
        Xm = X + reserve[:m - 8]
        Vm = [logits(W_maitre, x) for x in Xm]
        Wm = entrainer_eleve(Xm, Vm, [argmax(lv) for lv in Vm], 1.0, 0.0, eta=2.0, epoques=300)
        accords.append(accord(Wm, W_maitre, X_test)[0])
        print(f"  {m:>2} sorties du maître : accord = {accords[-1]:.3f}")
    assert accords[0] < accords[1] < accords[2]
    reponses = [0.6, 0.25, 0.1, 0.05]                    # loi du maître sur 4 réponses possibles à une même entrée
    print(f"  séquences : |V|^L = 30000^20 = {float(30000 ** 20):.2e} ; le mode garde {reponses[0] * 100:.0f} % de la masse,"
          f" H(p) = {entropie(reponses):.4f}")
    assert round(entropie(reponses), 4) == 1.0331 and 3.4e89 < 30000 ** 20 < 3.5e89

    print("6. Coût d'inférence : maître de 70 milliards de paramètres, élève de 8 milliards (illustratif)")
    for nom, taille in (("maître", 70e9), ("élève", 8e9)):
        flops, go = cout_inference(taille)
        print(f"  {nom:<6} : {flops:.2e} opérations par token ; {go:.0f} Go de poids en FP16")
    assert cout_inference(70e9)[0] / cout_inference(8e9)[0] == 8.75 and cout_inference(70e9)[1] == 140

    for appel in (lambda: perte_distillation(z, v, y, 0.0, 0.5), lambda: gradient_distillation(z, v, y, 2.0, 1.5)):
        try:
            appel()
        except ValueError:
            pass
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")
    print("  T = 0 ou α hors de [0, 1] → ValueError")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Cibles douces : le maître (logits 4, 2, 0) à plusieurs températures
  T = 1.0 : p = [0.8668, 0.1173, 0.0159]   entropie = 0.4411   p₂/p₃ = 7.389
  T = 4.0 : p = [0.5065, 0.3072, 0.1863]   entropie = 1.0202   p₂/p₃ = 1.649
2. Exemple à la main : élève (1, 1, 0), bonne classe 0
  T = 1.0 : q = [0.4223, 0.4223, 0.1554]   KL = 0.4368   ∂KL/∂z = [-0.4445, 0.305, 0.1395]
  T = 4, α = 0.7 : ℒ = 0.8008   ∂ℒ/∂z = [-0.5838, 0.2742, 0.3096] (vérifié par différences finies)
…
  T =    1.0 : ‖∂KL/∂z‖ = 5.57e-01   T²·‖∂KL/∂z‖ = 0.5568   T²·KL = 0.4368
  T = 1000.0 : ‖∂KL/∂z‖ = 7.20e-07   T²·‖∂KL/∂z‖ = 0.7202   T²·KL = 0.7780
  limite : T(q^T − p^T) → Δ/N = [-0.5556, 0.1111, 0.4444] ; T²·KL → Σ Δ² / 2N = 0.7778
4. Élève linéaire, 8 exemples étiquetés, maître à logits fixes (4 intentions, 6 traits)
  étiquettes seules  : accord avec le maître = 0.563   KL moyenne = 1.5386
  T = 1, α = 0.9     : accord avec le maître = 0.760   KL moyenne = 0.3313
  T = 4, α = 0.9     : accord avec le maître = 0.990   KL moyenne = 0.0003
  T = 4 sans T²      : accord avec le maître = 0.843   KL moyenne = 0.1499
…
  96 sorties du maître : accord = 0.910
  séquences : |V|^L = 30000^20 = 3.49e+89 ; le mode garde 60 % de la masse, H(p) = 1.0331
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : avec huit exemples, l'élève qui ne voit que les étiquettes ne retrouve le choix du maître qu'une fois sur deux ; avec les cibles douces à T = 4 et le facteur T², il le retrouve 99 fois sur 100.

### La même perte en PyTorch (extrait)

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`perte_distillation(z_eleve, z_maitre, y, T, alpha)`** — C'est la même perte que dans le programme précédent, confiée cette fois à PyTorch, qui travaille sur des lots entiers comme une chaîne de montage au lieu d'un artisan qui façonne un exemple à la fois : elle reçoit les logits de l'élève et du maître pour tout un lot, les étiquettes, T = 4 et α = 0,7 par défaut, calcule la partie douce avec `F.kl_div` entre le logarithme de la softmax de l'élève à la température T et la softmax du maître à la même température, moyennée sur le lot puis multipliée par T², et la partie dure avec `F.cross_entropy` à T = 1. Elle renvoie α fois la partie douce plus (1 − α) fois la partie dure, un tenseur que PyTorch sait dériver tout seul ; contrairement à la version en Python pur, elle ne vérifie pas elle-même les réglages, et le maître doit être calculé hors du graphe de gradient.

```python
# [extrait] — perte de distillation en PyTorch, non exécutée par le harnais (PyTorch hors bibliothèque standard)
import torch.nn.functional as F


def perte_distillation(z_eleve, z_maitre, y, T=4.0, alpha=0.7):
    douce = F.kl_div(F.log_softmax(z_eleve / T, dim=-1),      # log q^(T) de l'élève
                     F.softmax(z_maitre / T, dim=-1),         # p^(T) du maître
                     reduction="batchmean") * (T * T)
    dure = F.cross_entropy(z_eleve, y)                        # étiquettes dures, à T = 1
    return alpha * douce + (1 - alpha) * dure
```

`F.kl_div(entree, cible)` calcule ∑ cible·(ln cible − entree) : l'entrée doit être le **logarithme** des probabilités de l'élève, et la cible les probabilités du maître. Inverser les deux, ou passer des probabilités au lieu de leur logarithme, donne une perte fausse sans aucune erreur. `reduction="batchmean"` divise par la taille du lot, ce qui correspond à la définition de la KL ; le défaut, `"mean"`, divise aussi par le nombre de classes. Le maître se calcule sous `torch.no_grad()` pour ne pas rétropropager à travers lui. Sans PyTorch, `perte_distillation` et `gradient_distillation` du programme font le même calcul, gradient écrit à la main et vérifié par différences finies.

## Squelette algorithmique

Deux algorithmes couvrent le fichier. Le premier distille à partir des logits : en entrée, un maître dont on peut lire les logits, des exemples (étiquetés ou non), T, α et η ; en sortie, un élève. Le second distille à partir du seul texte du maître : on génère un jeu d'entraînement, puis on fait un fine-tuning ordinaire.

```text
ALGORITHME DistillationParLogits
ENTRÉES : maître M (figé), élève E (poids W), exemples (x, y), température T, poids α, pas η, époques K
SORTIE  : W entraîné

  POUR CHAQUE exemple x FAIRE
      p_T(x) ← softmax(M(x) / T)                         une fois : le maître ne change pas
  FIN POUR
  POUR k DE 1 À K FAIRE
      G ← 0
      POUR CHAQUE exemple (x, y) FAIRE
          z ← E(x)
          g ← α · T · (softmax(z / T) − p_T(x)) + (1 − α) · (softmax(z) − un_parmi_N(y))
          G ← G + rétropropagation de g dans E           pour un élève linéaire : g · xᵀ
      FIN POUR
      W ← W − η · G / nombre d'exemples
  FIN POUR
  RETOURNER W                                            en production, l'élève répond à T = 1

ALGORITHME DistillationParSéquences
ENTRÉES : maître M (accessible par son texte), entrées x₁ … x_m, élève E
SORTIE  : élève E affiné

  jeu ← liste vide
  POUR i DE 1 À m FAIRE
      ŷᵢ ← décoder(M, xᵢ)                                glouton, faisceau, ou plusieurs tirages
      SI ŷᵢ passe les contrôles (schéma, règles métier) ALORS ajouter (xᵢ, ŷᵢ) à jeu
  FIN POUR
  affiner E sur jeu en minimisant − Σₜ ln q(ŷₜ | ŷ₁ … ŷₜ₋₁, x)    fine-tuning supervisé ordinaire (étape 73)
  RETOURNER E
```

**Complexité :** DistillationParLogits fait m passages du maître une seule fois, puis, à chaque époque, m passages avant et arrière de l'élève : O(m·C_M + K·m·C_E), où C_M et C_E sont les coûts d'un passage du maître et de l'élève. Pour l'élève linéaire du programme, C_E = O(N·D), soit O(K·m·N·D) en tout. Garder les cibles douces coûte O(m·N) en mémoire ; pour un LLM, c'est m × L × |V| nombres, souvent trop, d'où le stockage des seuls k plus grands logits par position. DistillationParSéquences coûte m générations du maître, chacune de L tokens à environ 2P_M opérations, puis un fine-tuning de l'élève : c'est la génération qui domine la facture quand le maître est un grand modèle facturé au token (étape 72).

**Du squelette au code :** la boucle « POUR CHAQUE exemple x : p_T(x) » est la ligne `cibles_douces = [softmax(v, T) for v in V]` de `entrainer_eleve`. La ligne g est `gradient_distillation(..., p_T)` ; la rétropropagation dans l'élève linéaire est la compréhension `G[k] = [a + gk * b ...]`, et la mise à jour la ligne `W = [[w - eta * g ...]]`. DistillationParSéquences est jouée, en version classification, par la partie 5 de `main` : le maître « écrit » ses décisions `argmax(lv)` sur des entrées nouvelles, et l'élève s'entraîne dessus avec α = 0, c'est-à-dire avec l'entropie croisée seule.

## Cas d'usage réels aux Émirats

Les tailles de modèle, les volumes, les seuils et les taux d'accord ci-dessous sont illustratifs ; les nombres qui sortent d'une formule sont ceux du programme.

### Banque — un routeur d'intentions distillé, hébergé sur place

Une banque de détail de Dubaï route chaque message de son assistant entre une douzaine d'intentions : solde, virement, carte bloquée, réclamation, demande de prêt personnel, finance islamique. Un grand modèle ouvert le fait très bien, mais il occupe plusieurs accélérateurs et ajoute plusieurs centaines de millisecondes à chaque tour. L'équipe le garde comme maître, lui fait produire ses logits sur 50 000 messages historiques pseudonymisés, et distille un petit encodeur à T = 4 et α = 0,7, qui tient sur un seul serveur du centre de données de la banque. Le point 3 lui évite un piège classique : sans le facteur T², son premier essai à T = 4 apprenait à peine du maître, comme l'élève « sans T² » du programme, qui plafonne à 0,843 d'accord au lieu de 0,990. En production, l'élève décide seul quand sa probabilité maximale, calculée à T = 1, dépasse 0,9 ; en dessous, le message remonte au maître. L'outil de virement garde son approbation humaine à l'intérieur de l'outil, si bien qu'une erreur de routage ne peut pas déclencher de paiement. L'indicateur suivi est l'accord élève-maître par intention, mesuré chaque semaine sur un échantillon relu, et la part des messages renvoyés au maître.

### Secteur public — un petit modèle arabe distillé par séquences

Une entité de services publics en ligne accessible par UAE Pass veut une application mobile qui réponde hors connexion aux questions les plus fréquentes, en arabe et en anglais. Elle part d'un grand modèle arabe ouvert, de la famille de Jais ou de Falcon, comme maître, et d'un modèle de quelques milliards de paramètres comme élève. Faute de pouvoir stocker les logits sur tout le vocabulaire pour des centaines de milliers de réponses, elle distille par séquences (point 6) : le maître rédige une réponse pour chacune de 40 000 questions réelles pseudonymisées, chaque réponse est contrôlée par des règles (citations des fiches officielles, absence de numéro d'Emirates ID), puis l'élève est affiné sur ces paires avec un adaptateur LoRA (étape 73). Avant de lancer le projet, l'équipe vérifie la licence du maître, qui encadre la réutilisation de ses sorties : c'est le genre de point qu'on confirme avec le texte en vigueur, pas de mémoire. Elle sait aussi que l'élève hérite de toutes les erreurs du maître : les réponses rejetées par les contrôles n'entrent pas dans le jeu. Sans ce filtre, l'application répéterait avec assurance une démarche administrative périmée. L'indicateur suivi est le taux de réponses jugées exactes par les agents du service sur un échantillon mensuel, par langue.

### Assurance — des cibles douces entre sinistres voisins

Un assureur auto et santé, supervisé par la CBUAE, classe les déclarations de sinistres auto en catégories : bris de glace, carrosserie, mécanique, vol, corporel. Certaines catégories se ressemblent : une déclaration « pare-brise fissuré après un choc » est à la frontière entre bris de glace et carrosserie, ce que le maître exprime en donnant, par exemple, 0,55 à l'une et 0,40 à l'autre à T = 4. Une étiquette dure dirait seulement « bris de glace » ; la cible douce apprend à l'élève que l'erreur « carrosserie » est bien moins grave que l'erreur « vol », exactement l'information du point 1. L'équipe distille un élève rapide à partir d'un ensemble de trois grands modèles, dont elle moyenne les distributions pour former un maître plus stable, puis vérifie que l'élève répond à T = 1 : à T = 4, le seuil de passage en traitement automatique, fixé à 0,85, ne serait presque jamais atteint (point 5). Sans distillation, l'assureur devrait appeler l'ensemble complet pour chaque déclaration, trois fois plus cher. L'indicateur suivi est la matrice de confusion par catégorie, avec une attention particulière aux confusions graves, comme « vol » classé en « carrosserie ».

### Crypto — la classe rare que l'élève oublie

Une plateforme d'actifs virtuels agréée par la VARA trie les messages de son support : question générale, retrait en attente, réclamation, et tentative d'hameçonnage, qui ne représente qu'un message sur cent. Un élève distillé affiche 0,97 d'accord global avec le maître, ce qui semble excellent, mais cet accord est dominé par les classes fréquentes : sur la seule classe « hameçonnage », il descend nettement plus bas. Le terme doux mesure l'écart moyen sur tous les exemples, et une classe rare y pèse peu ; l'élève, plus petit, sacrifie d'abord ce qui compte le moins dans la moyenne. L'équipe suréchantillonne donc les messages d'hameçonnage dans le jeu de distillation, garde α = 0,5 pour que les vraies étiquettes pèsent davantage, et fixe un critère d'acceptation par classe plutôt qu'un critère global. Sans ce critère, l'élève passerait la recette et laisserait filer précisément les messages qui exposent les clients à une perte de fonds. L'indicateur suivi est le rappel sur la classe « hameçonnage » (étape 56), avec un plancher fixé avant la mise en production.

### RH — extraire un JSON comme le grand modèle, pour un coût dix fois moindre

Un cabinet RH présent dans plusieurs émirats extrait des contrats et des attestations de salaire un JSON strict : employeur, salaire de base, date d'entrée, type de contrat. Un grand modèle facturé au token le fait correctement, mais à raison de 30 000 documents par mois la facture pèse. Le cabinet distille par séquences : le grand modèle produit le JSON de 10 000 documents passés, chaque sortie passe le validateur de schéma de l'étape 11 et des contrôles métier (un salaire de base positif, une date d'entrée antérieure à la date du document), et un élève ouvert de 8 milliards de paramètres est affiné sur les paires retenues. Avec l'approximation du point 7, l'élève coûte 8,75 fois moins d'opérations par token qu'un maître de 70 milliards ; il tourne sur un serveur interne, si bien que les documents ne quittent plus le cabinet. L'indemnité de fin de service reste calculée par l'outil `gratuite_fin_de_service` à partir du salaire de base extrait, jamais par l'un ou l'autre modèle. Sans les contrôles du jeu, l'élève apprendrait aussi les erreurs du maître, puisqu'il n'a aucun moyen de faire mieux que ce qu'on lui montre. L'indicateur suivi est le taux de validation du schéma et l'exactitude champ par champ (étape 64) sur un échantillon relu.

### BTP — un classifieur de lignes de facture qui tourne sur le chantier

Un groupe de construction sur de grands chantiers à Dubaï affecte chaque ligne de facture de ses sous-traitants à un code analytique : béton, acier, location d'engins, main-d'œuvre, retenue de garantie. Les bureaux de chantier ont une connexion instable, et le groupe veut un modèle qui tourne sur un poste local. Le maître, un grand modèle, a d'abord étiqueté 20 000 lignes passées ; comme il n'expose que ses décisions, le groupe s'appuie sur le volume, comme dans la partie 5 du programme, où l'accord passe de 0,563 à 0,910 quand le nombre de sorties du maître passe de 8 à 96. L'élève, un petit classifieur, est ensuite comparé au maître sur un jeu de lignes récentes jamais vues. Les montants eux-mêmes ne passent jamais par le modèle : la TVA de 5 % et les retenues de garantie sont recalculées par des outils à partir des montants hors taxe. Sans élève local, chaque ligne attendrait le retour de la connexion, et la saisie de fin de mois glisserait de plusieurs jours. L'indicateur suivi est l'accord élève-maître sur les nouvelles lignes, par code analytique, et le nombre de corrections manuelles par mois.

## Pièges et limites

- **Oublier le facteur T².** Le terme doux s'éteint en 1/T², et l'élève apprend surtout des étiquettes dures ; changer T oblige alors à retoucher α et η.
- **Garder T > 1 en production.** La classe choisie ne change pas, mais toutes les probabilités s'aplatissent et les seuils de confiance ne veulent plus rien dire.
- **Inverser les arguments de la KL.** `F.kl_div` attend le logarithme des probabilités de l'élève en premier ; l'erreur ne lève aucune exception. Dans le programme, `kl(p, q)` prend toujours le maître en premier.
- **Croire que l'élève dépassera le maître.** Il hérite de ses erreurs et de ses biais ; on filtre les sorties du maître et on garde une part de vraies étiquettes (α < 1).
- **Distiller des logits entre deux vocabulaires différents.** Si le maître et l'élève n'ont pas le même tokenizer (étape 2 bis), leurs logits ne portent pas sur les mêmes tokens ; on distille alors par séquences.
- **Négliger les conditions d'utilisation.** Entraîner un modèle sur les sorties d'un modèle tiers peut être interdit par ses conditions ou encadré par sa licence ; c'est à vérifier avant de commencer.

### Exercice feuille blanche

1. Sans regarder le code, écrire `perte_distillation` et `gradient_distillation` à partir de l'équation complète, puis retrouver ℒ = 0,8008 et le gradient (−0,5838 ; 0,2742 ; 0,3096) pour v = (4 ; 2 ; 0), z = (1 ; 1 ; 0), T = 4 et α = 0,7.
2. Prédire, puis vérifier : pour le maître v = (4 ; 2 ; 0) à T = 8, que vaut le rapport p₂/p₃, et vers quoi tend-il quand T grandit ? (Réponse : exp(0,25) ≈ 1,284, et il tend vers 1.)
3. Trouver le bug : dans `gradient_distillation`, la ligne devient `poids = alpha / T` pour tous les appels. Que devient l'accord de l'élève à T = 4 dans la partie 4, et pourquoi l'entraînement ne lève-t-il aucune erreur ?

## Pour aller plus loin

La KL « avant » utilisée ici, D(p_maître ‖ q_élève), pousse l'élève à couvrir toute la masse du maître ; certains travaux sur les LLM, comme MiniLLM, préfèrent la KL « inverse », qui pousse l'élève à se concentrer sur les modes du maître. La distillation **sur politique** fait générer les réponses par l'élève et les fait noter, token par token, par le maître, ce qui corrige les erreurs que l'élève commet vraiment. On distille aussi des représentations internes (TinyBERT), un cross-encodeur vers un bi-encodeur (étape 36 ter), ou un modèle vers lui-même (auto-distillation). Enfin, distillation et quantification se cumulent : un élève distillé puis quantifié en INT4 (étape 73 bis) divise encore sa mémoire par quatre.

> Étape 73 ter du parcours · Prérequis : [Quantification INT8 et INT4](<73b-Quantification-INT8-INT4.md>) · Suite : [Optimiseur Adam](<74-Optimiseur-Adam.md>)
