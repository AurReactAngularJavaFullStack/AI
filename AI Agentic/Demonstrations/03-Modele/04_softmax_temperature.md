# 04 — Softmax et température : démonstrations

> Fiche : [04 — Softmax et température](<../../Images/03-Modele/04_softmax_temperature.md>) · Image : `04_softmax_temperature.jpg` · Leçon : [Étape 2 — Softmax et température](<../../02-LLM-Softmax-et-Prompts/02-Softmax-Temperature-Prochain-Token.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
p_i = \frac{\exp(z_i / T)}{\sum_{j} \exp(z_j / T)}
$$

zᵢ est le score brut (logit) du token i, T > 0 la température, pᵢ la probabilité de tirer ce token.

## Les symboles, un par un

$$
z_i
$$

zᵢ est le logit du choix i (un token du vocabulaire, un outil, une classe) : un réel quelconque, positif ou négatif, sans borne et sans unité ; en Python, `z[i]`.

$$
K
$$

K est le nombre de choix possibles, un entier ≥ 2 (la leçon l'écrit |V| quand ce sont les tokens du vocabulaire) ; en Python, `len(z)`.

$$
T
$$

T est la température, un réel strictement positif qui divise les logits avant l'exponentielle ; en Python, le paramètre `T` de `softmax(z, T)`.

$$
m = \max_j z_j
$$

m est le plus grand logit, retranché avant l'exponentielle pour la stabilité ; en Python, `m = max(z)`.

$$
\exp(x) = e^x
$$

exp est l'exponentielle, toujours strictement positive, avec e ≈ 2,71828 ; en Python, `math.exp`.

$$
\sum_{j}
$$

∑ⱼ est la somme sur les K choix ; elle sert de dénominateur commun et force le total à 1 ; en Python, `s = sum(e)`.

$$
p_i
$$

pᵢ est la probabilité du choix i, dans ]0, 1[ dès que K ≥ 2, et les pᵢ somment à 1 ; en Python, `softmax(z, T)[i]`.

$$
\delta_{ij}
$$

δᵢⱼ est le symbole de Kronecker, 1 si i = j et 0 sinon (démonstration 6) ; il n'a pas de variable propre dans le programme.

$$
\Delta
$$

Δ est l'écart de logits entre le bon token et son concurrent le plus fort (cas 2) ; en Python, `ecart`.

## Le mécanisme, avant les preuves

Ce qui entre, ce sont K logits, des réels quelconques, et une température T > 0. La première opération divise chaque logit par T : elle ne change pas l'ordre des logits, mais elle étire leurs écarts quand T < 1 et les écrase quand T > 1. La deuxième retranche le plus grand logit : elle ne change pas le résultat (démonstration 2), mais elle garantit qu'aucune exponentielle ne dépasse 1. La troisième, l'exponentielle, rend tout strictement positif et transforme les **différences** de logits en **rapports** : un écart de 1 devient un facteur e ≈ 2,718 entre deux probabilités (démonstration 3). La quatrième fait la somme, et la cinquième divise chaque terme par cette somme : ce qui sort est une loi de probabilité, K nombres positifs de somme 1.

Pourquoi l'exponentielle et pas le carré ou la valeur absolue : il faut une fonction positive pour tout réel (un logit peut être négatif), croissante (un meilleur score doit donner une meilleure probabilité), et qui ne dépende que des écarts entre logits ; seules les exponentielles (de base quelconque, ce qui revient à changer T) transforment une somme en produit, e^(a + b) = eᵃ × eᵇ, ce qui donne exactement cette dépendance aux seuls écarts. Pourquoi diviser par la somme : c'est la seule façon de ramener des poids positifs à une loi de probabilité sans changer leurs rapports. La température ne fait qu'une chose : elle multiplie tous les écarts par 1/T avant l'exponentielle.

Petit film chiffré, avec les logits (2 ; 1 ; 0). À T = 1 : on retranche le maximum, (0 ; −1 ; −2) ; exponentielles (1 ; 0,36788 ; 0,13534) ; somme 1,50321 ; division : (0,66524 ; 0,24473 ; 0,09003). À T = 0,5 : division par 0,5, (4 ; 2 ; 0) ; on retranche 4, (0 ; −2 ; −4) ; exponentielles (1 ; 0,13534 ; 0,01832) ; somme 1,15365 ; division : (0,86681 ; 0,11731 ; 0,01588). Diviser par 0,5 a doublé les écarts, et le premier token passe de 66,5 % à 86,7 %.

Analogie Java/Spring : un répartiteur de charge pondéré envoie chaque requête à un serveur au hasard, proportionnellement à son poids. La softmax fabrique ces poids à partir de scores, et la température règle à quel point le meilleur serveur est privilégié ; tant que T > 0, aucun serveur ne reçoit un poids exactement nul.

## Démonstration 1 — C'est bien une loi de probabilité

**Ce qu'on démontre.** Pour K ≥ 2 logits réels et T > 0, chaque pᵢ est strictement compris entre 0 et 1, et

$$
\sum_{i=1}^{K} p_i = 1
$$

**L'idée.** Tous les termes sont des exponentielles, donc strictement positifs ; chaque probabilité est un terme divisé par la somme de tous les termes, qui le contient lui-même plus d'autres termes positifs.

**La preuve, pas à pas.** Trois étapes.

**Étape 1.** Pour tout réel x, eˣ > 0, donc chaque numérateur exp(zᵢ/T) est strictement positif, et le dénominateur S = ∑ⱼ exp(zⱼ/T) aussi.

**Étape 2.** S contient exp(zᵢ/T) plus au moins un autre terme strictement positif, parce que K ≥ 2 ; donc 0 < exp(zᵢ/T) < S, et en divisant par S > 0 : 0 < pᵢ < 1.

**Étape 3.** Tous les pᵢ ont le même dénominateur S, et la somme des numérateurs est S elle-même :

$$
\sum_i p_i = \frac{\sum_i \exp(z_i/T)}{S} = \frac{S}{S} = 1
$$

∎

**Vérification chiffrée.** Pour (2 ; 1 ; 0) à T = 1 : 0,66524 + 0,24473 + 0,09003 = 1. Pour les logits (0,7 ; −1,2 ; 2,5) à T = 0,8, la somme vaut 1 et la plus petite probabilité reste strictement positive. Avec K = 1, l'hypothèse manque : l'unique choix a la probabilité 1, et l'inégalité stricte pᵢ < 1 tombe.

**Ce que la preuve révèle du mécanisme.** La positivité stricte vient de l'exponentielle, qui ne vaut jamais 0 : aucun choix n'est jamais impossible tant que T > 0. La somme égale à 1 vient du dénominateur commun.

**Conséquence pour un agent.** Une action sensible (rembourser, virer, supprimer) garde une probabilité non nulle d'être tirée, quelle que soit la température : elle se protège par une autorisation dans le code, jamais par la température (cas 1).

## Démonstration 2 — Retrancher le maximum ne change rien

**Ce qu'on démontre.** Pour toute constante a et tout T > 0 :

$$
\frac{\exp((z_i - a)/T)}{\sum_j \exp((z_j - a)/T)} = p_i
$$

En particulier avec a = m = maxⱼ zⱼ, tous les exposants sont ≤ 0.

**L'idée.** Retrancher a à chaque logit multiplie chaque exponentielle par le même facteur e^(−a/T) ; ce facteur commun apparaît en haut et dans chaque terme du bas, et se simplifie.

**La preuve, pas à pas.** Trois étapes.

**Étape 1.** Par la propriété e^(u + v) = eᵘ × eᵛ, on sort le facteur constant :

$$
\exp\left(\frac{z_i - a}{T}\right) = e^{-a/T} \exp\left(\frac{z_i}{T}\right)
$$

**Étape 2.** Le même facteur sort de chaque terme du dénominateur, donc de la somme :

$$
\frac{e^{-a/T} \exp(z_i/T)}{e^{-a/T} \sum_j \exp(z_j/T)} = \frac{\exp(z_i/T)}{\sum_j \exp(z_j/T)} = p_i
$$

**Étape 3.** Avec a = m, chaque exposant (zᵢ − m)/T est ≤ 0, parce que zᵢ ≤ m et T > 0 ; chaque exponentielle vaut donc au plus e⁰ = 1, et le dénominateur contient le terme e⁰ = 1, donc il vaut au moins 1. ∎

**Vérification chiffrée.** Les logits (1 000 ; 999) : la formule directe demande e¹⁰⁰⁰, qui dépasse le plus grand flottant (environ 1,8 × 10³⁰⁸ = e⁷⁰⁹,⁷⁸) et fait lever `OverflowError` à `math.exp`. En retranchant 1 000, on calcule la softmax de (0 ; −1) : (1/(1 + e⁻¹) ; e⁻¹/(1 + e⁻¹)) = (0,73106 ; 0,26894). Ces valeurs arrivent vite : un logit de 14,2 à T = 0,01 donne un exposant de 1 420. À l'inverse, e²⁰ ≈ 4,85 × 10⁸ ne pose aucun problème (leçon, point 2).

**Ce que la preuve révèle du mécanisme.** La softmax ne dépend que des écarts entre logits, jamais de leur niveau : ajouter 100 à tous les logits ne change aucune probabilité.

**Conséquence pour un agent.** Tout code de softmax retranche le maximum (`m = max(z)`) et vérifie que les logits sont finis : un logit infini ou indéfini en amont donnerait `inf - inf`, que le retrait du maximum ne sauve pas.

## Démonstration 3 — Le rapport de deux probabilités

**Ce qu'on démontre.** Pour deux choix i et j :

$$
\frac{p_i}{p_j} = \exp\left( \frac{z_i - z_j}{T} \right)
$$

Le rapport ne dépend que de l'écart entre leurs deux logits et de T, pas des autres choix.

**L'idée.** pᵢ et pⱼ ont le même dénominateur : il disparaît dans le quotient, et il ne reste que le rapport de deux exponentielles.

**La preuve, pas à pas.** Deux étapes.

**Étape 1.** On écrit le quotient ; le dénominateur commun S se simplifie :

$$
\frac{p_i}{p_j} = \frac{\exp(z_i/T) / S}{\exp(z_j/T) / S} = \frac{\exp(z_i/T)}{\exp(z_j/T)}
$$

**Étape 2.** Par eᵘ / eᵛ = e^(u − v), le quotient vaut exp((zᵢ − zⱼ)/T). ∎

**Vérification chiffrée.** Pour (2 ; 1 ; 0) : 0,66524 / 0,24473 = 2,71828 = e¹ à T = 1, et 0,86681 / 0,11731 = 7,38906 = e² à T = 0,5. Si l'on ajoute un quatrième choix de logit 1,5, les probabilités deviennent (0,47399 ; 0,17437 ; 0,06415 ; 0,28749), mais le rapport des deux premières reste 2,71828.

**Ce que la preuve révèle du mécanisme.** La température agit comme une loupe sur les écarts : diviser T par deux élève chaque rapport au carré. Comme 1/T est positif, l'ordre des probabilités est toujours celui des logits : la température ne change jamais le choix le plus probable.

**Conséquence pour un agent.** Un écart de logits se lit directement comme une « cote » : 6,1 points d'écart à T = 0,7 donnent une cote de e^8,7143 = 6 089 contre 1 (cas 2). Et calibrer un classifieur par la température ne change pas sa réponse, seulement la confiance qu'il affiche (cas 4).

## Démonstration 4 — Les deux limites de la température, et ce qui se passe entre les deux

**Ce qu'on démontre.** Si le logit maximal est atteint par un seul choix k, alors pₖ → 1 quand T → 0⁺, chaque pᵢ → 1/K quand T → +∞, et entre les deux pₖ(T) décroît strictement. Symétriquement, la probabilité du logit minimal unique croît strictement avec T.

**L'idée.** On divise tout par l'exponentielle du plus grand logit : pₖ s'écrit 1 / (1 + somme de termes e^(−écart/T)). Chaque écart est positif, donc chaque terme tend vers 0 quand T → 0 et vers 1 quand T → ∞, en croissant avec T.

**La preuve, pas à pas.** Trois étapes.

**Étape 1.** Par la démonstration 2 avec a = zₖ, et en notant dⱼ = zₖ − zⱼ > 0 pour j ≠ k :

$$
p_k(T) = \frac{1}{1 + \sum_{j \ne k} e^{-d_j / T}}
$$

**Étape 2.** Limites. Quand T → 0⁺, −dⱼ/T → −∞ et chaque terme tend vers 0, donc pₖ → 1/(1 + 0) = 1 (l'argmax, le décodage glouton). Quand T → +∞, −dⱼ/T → 0, chaque terme tend vers 1, donc pₖ → 1/K ; le même calcul appliqué à n'importe quel i donne pᵢ → 1/K (loi uniforme).

**Étape 3.** Monotonie. Si T augmente, −dⱼ/T augmente (il se rapproche de 0), donc chaque e^(−dⱼ/T) augmente, le dénominateur augmente et pₖ diminue strictement. Pour le logit minimal unique, on écrit de même p = 1 / (1 + ∑ e^(+dⱼ/T)) avec des exposants positifs qui diminuent quand T augmente : p augmente. ∎

**Vérification chiffrée.** Pour le routeur du cas 1, la probabilité du meilleur outil vaut 0,98199 à T = 0,2, puis 0,93418 à T = 0,3, 0,81973 à T = 0,5, 0,61470 à T = 1 et 0,44349 à T = 2 : elle décroît. Avec (1 ; 3 ; 2), T = 0,01 donne plus de 0,999 au deuxième choix, et T = 10⁶ ne laisse plus que 0,334 au maximum. Contre-exemple quand le maximum n'est pas unique : (3 ; 3 ; 1) à T = 0,01 donne (0,5 ; 0,5 ; 0), pas un argmax unique.

**Ce que la preuve révèle du mécanisme.** La température déplace la masse de façon monotone : on peut donc chercher par dichotomie la température exacte où une probabilité franchit un seuil, ce que font les cas 1, 3 et 4.

**Conséquence pour un agent.** T bas pour les appels d'outils, le JSON et les chiffres, quand l'API le permet ; T plus haut seulement pour la variété du texte. Comme la queue (le logit minimal) grossit quand T monte, un texte plus varié contient aussi plus de tokens absurdes (cas 3).

## Démonstration 5 — À deux classes, la softmax est une sigmoïde

**Ce qu'on démontre.** Pour K = 2 :

$$
p_1 = \frac{e^{z_1/T}}{e^{z_1/T} + e^{z_2/T}} = \frac{1}{1 + e^{-(z_1 - z_2)/T}}
$$

**L'idée.** Avec deux choix, seul compte l'écart z₁ − z₂ (démonstration 2) ; on divise en haut et en bas par le terme du choix 1.

**La preuve, pas à pas.** Deux étapes.

**Étape 1.** On divise numérateur et dénominateur par e^(z₁/T) > 0, ce qui ne change pas le quotient.

**Étape 2.** Le numérateur devient 1 et le second terme du dénominateur devient e^((z₂ − z₁)/T) = e^(−(z₁ − z₂)/T). ∎

**Vérification chiffrée.** Logits (1 ; 0) à T = 1 : 1/(1 + e⁻¹) = 1/1,36788 = 0,73106. Logits (2 ; 0) : à T = 0,5, 1/(1 + e⁻⁴) = 0,98201 ; à T = 2, 1/(1 + e⁻¹) = 0,73106.

**Ce que la preuve révèle du mécanisme.** La régression logistique et la décision binaire d'un garde-fou sont des cas particuliers de la softmax : la sigmoïde est la softmax de deux choix, avec l'écart comme seule entrée.

**Conséquence pour un agent.** Pour estimer le risque qu'un token soit remplacé par son concurrent le plus fort, on calcule 1/(1 + e^(Δ/T)) ; c'est une borne basse du risque réel, puisque les autres concurrents ajoutent leur part (cas 2).

## Démonstration 6 — La dérivée, et la sensibilité aux logits

**Ce qu'on démontre.** Pour tous i et j :

$$
\frac{\partial p_i}{\partial z_j} = \frac{1}{T}\, p_i \left( \delta_{ij} - p_j \right)
$$

Chaque ligne de ces dérivées somme à 0, et la sensibilité est multipliée par 1/T.

**L'idée.** pᵢ est un quotient u/v où u ne dépend que de zᵢ et v de tous les logits ; la règle du quotient donne le résultat, et le facteur 1/T vient de la dérivée de zⱼ/T.

**La preuve, pas à pas.** Trois étapes.

**Étape 1.** On note u = exp(zᵢ/T) et v = ∑ₗ exp(zₗ/T). La dérivée d'une fonction composée donne ∂u/∂zⱼ = u δᵢⱼ / T, parce que u ne dépend que de zᵢ, et ∂v/∂zⱼ = exp(zⱼ/T) / T, parce que seul le terme l = j dépend de zⱼ.

**Étape 2.** La règle du quotient (u/v)′ = (u′v − uv′)/v² donne, en factorisant u/v = pᵢ et en reconnaissant exp(zⱼ/T)/v = pⱼ :

$$
\frac{\partial p_i}{\partial z_j} = \frac{\frac{u\, \delta_{ij}}{T}\, v - u\, \frac{e^{z_j/T}}{T}}{v^2} = \frac{1}{T}\, p_i \left( \delta_{ij} - p_j \right)
$$

**Étape 3.** En sommant sur j, ∑ⱼ (δᵢⱼ − pⱼ) = 1 − 1 = 0 : pousser tous les logits ensemble ne change rien, comme le dit la démonstration 2. ∎

**Vérification chiffrée.** Pour (2 ; 1 ; 0) à T = 1 : ∂p₁/∂z₁ = 0,66524 × 0,33476 = 0,22270 et ∂p₁/∂z₂ = −0,66524 × 0,24473 = −0,16280. Si z₁ monte de 0,1, l'approximation linéaire annonce 0,66524 + 0,1 × 0,22270 = 0,68751, et le calcul exact donne 0,68713. À T = 0,5, la même dérivée vaut 0,86681 × 0,13319 / 0,5 = 0,23090, avec une probabilité de départ déjà plus haute. La dérivée numérique, calculée par le programme avec un pas de 10⁻⁶, coïncide avec la formule.

**Ce que la preuve révèle du mécanisme.** La dérivée est maximale quand pᵢ = 1/2, où pᵢ(1 − pᵢ) = 1/4, et quasi nulle quand le choix est déjà presque certain ou presque impossible. Le signe moins hors de la diagonale traduit une masse fixe : ce qu'un choix gagne, les autres le perdent.

**Conséquence pour un agent.** À basse température, la sensibilité est multipliée par 1/T : un petit changement de prompt peut faire basculer un routeur d'un outil à l'autre. On teste donc un routeur à température basse sur des reformulations de la même demande avant de le mettre en production. Cette dérivée sert aussi à l'entraînement (fiche 06).

## Exemple simple, à la main

Logits (2 ; 1 ; 0) à T = 1. Exponentielles : e² = 7,38906, e¹ = 2,71828, e⁰ = 1 ; somme 7,38906 + 2,71828 + 1 = 11,10734. Divisions :

$$
p = \left(\frac{7{,}38906}{11{,}10734}\ ;\ \frac{2{,}71828}{11{,}10734}\ ;\ \frac{1}{11{,}10734}\right) = (0{,}66524\ ;\ 0{,}24473\ ;\ 0{,}09003)
$$

À T = 0,5, les logits divisés valent (4 ; 2 ; 0) ; exponentielles 54,59815, 7,38906 et 1, de somme 62,98721 :

$$
p = (0{,}86681\ ;\ 0{,}11731\ ;\ 0{,}01588)
$$

À T = 2, les logits divisés valent (1 ; 0,5 ; 0) ; exponentielles 2,71828, 1,64872 et 1, de somme 5,36700 :

$$
p = (0{,}50648\ ;\ 0{,}30720\ ;\ 0{,}18632)
$$

| T | p₁ | p₂ | p₃ | rapport p₁ / p₂ |
| --- | --- | --- | --- | --- |
| 0,5 | 0,86681 | 0,11731 | 0,01588 | e² = 7,38906 |
| 1 | 0,66524 | 0,24473 | 0,09003 | e¹ = 2,71828 |
| 2 | 0,50648 | 0,30720 | 0,18632 | e⁰,⁵ = 1,64872 |

## Cas d'usage complexes, démontrés

### Cas 1 — Assureur auto et santé : un routeur d'outils et une action sensible

**Contexte.** Un assureur auto et santé fait traiter les messages de ses assurés, en arabe et en anglais, par un agent qui choisit à chaque tour un outil parmi quatre : chercher le dossier, rembourser, escalader vers un gestionnaire, répondre directement. Pour un type de message ambigu fréquent, le modèle hébergé en interne produit toujours les mêmes logits, et l'outil `rembourser` n'est jamais le bon choix. L'équipe veut savoir combien de fois par jour cet outil serait tiré selon la température, et comment le protéger. Les logits, le volume et les coûts sont illustratifs.

**Données.**

| Outil | chercher_dossier | rembourser | escalader | repondre |
| --- | --- | --- | --- | --- |
| Logit | 3,2 | 1,1 | 2,4 | 0,3 |

Autres données : 10 000 messages de ce type par jour ; températures candidates 1 ; 0,3 et 2 ; un remboursement indu coûte en moyenne 2 500 AED ; une validation humaine d'un remboursement coûte 15 AED.

**Calcul pas à pas.** Probabilités arrondies à 5 décimales.

**Étape 1.** T = 1 : on retranche 3,2, ce qui donne (0 ; −2,1 ; −0,8 ; −2,9) ; exponentielles (1 ; 0,122456 ; 0,449329 ; 0,055023), de somme 1,626809 :

$$
p = (0{,}61470\ ;\ 0{,}07527\ ;\ 0{,}27620\ ;\ 0{,}03382)
$$

**Étape 2.** Tirages de `rembourser` à T = 1 :

$$
10\,000 \times 0{,}07527 = 752{,}7 \approx 753 \text{ par jour}
$$

**Étape 3.** T = 0,3 : les écarts divisés valent (0 ; −7 ; −2,666667 ; −9,666667), les exponentielles (1 ; 0,000912 ; 0,069483 ; 0,000063), de somme 1,070459 :

$$
p = (0{,}93418\ ;\ 0{,}00085\ ;\ 0{,}06491\ ;\ 0{,}00006), \qquad 10\,000 \times 0{,}00085 \approx 8{,}5 \approx 9 \text{ par jour}
$$

**Étape 4.** T = 2 : p = (0,44349 ; 0,15519 ; 0,29728 ; 0,10403), soit environ 1 552 tirages par jour.

**Décision de l'agent.** Le routeur tourne à T = 0,3, et l'outil `rembourser` ne paie jamais directement : il crée une demande que valide un gestionnaire. Avec 9 demandes par jour, la validation coûte 9 × 15 = 135 AED par jour, contre 9 × 2 500 = 22 500 AED par jour de remboursements indus si l'outil payait seul.

**Contre-calcul.** L'idée « à T = 0,3, `rembourser` devient impossible » est fausse (démonstration 1) : 8,5 tirages par jour, c'est 8,5 × 365 = 3 109 tirages par an. Sans garde-fou dans le code, chacun serait un remboursement indu.

**Sensibilité.** Par dichotomie sur T (démonstration 4), on trouve la température qui ramène `rembourser` à 1 tirage par jour : T = 0,22875. Même là, il reste 365 tirages par an : aucune température strictement positive n'atteint zéro, et seul le garde-fou supprime le risque. À l'inverse, passer de T = 1 à T = 2 double presque le nombre de tirages (753 → 1 552).

**En production.** On suit le nombre de demandes de remboursement créées par le routeur et refusées par le gestionnaire (attendu autour de 9 par jour pour ce type de message, alerte au-delà de 20, signe que les logits ont dérivé). L'assurance est supervisée par la CBUAE ; la traçabilité des décisions de remboursement est à confirmer avec le texte en vigueur.

### Cas 2 — Banque de détail à Dubaï : un JSON de 300 tokens sans token parasite

**Contexte.** L'agent de pré-instruction de crédit d'une banque de détail de Dubaï produit pour chaque dossier un document JSON d'environ 300 tokens (identifiant, mensualité, ratio d'endettement, recommandation), avec un modèle ouvert hébergé en interne, de type Jais ou Falcon, dont la banque règle la température. Elle traite 2 000 dossiers par jour. On suppose qu'à chaque token, le bon token devance son concurrent le plus fort de Δ = 6,1 logits, et l'on néglige les autres concurrents, ce qui donne une borne basse du risque. La question : quelle température pour le JSON ? Les volumes et l'écart de logits sont illustratifs.

**Données.**

| Donnée | Valeur |
| --- | --- |
| Tokens par document | 300 |
| Écart de logits Δ | 6,1 |
| Températures comparées | 0,7 et 0,2 |
| Dossiers par jour | 2 000 |
| Objectif | au plus 0,1 % de documents avec un token faux |

**Calcul pas à pas.** Arrondis annoncés à chaque étape.

**Étape 1.** Risque par token à T = 0,7, par la sigmoïde (démonstration 5) : Δ/T = 6,1 / 0,7 = 8,7143 et e^8,7143 = 6 089,3, donc

$$
P(\text{token faux}) = \frac{1}{1 + e^{\Delta/T}} = \frac{1}{1 + 6\,089{,}3} = 0{,}000164
$$

**Étape 2.** Risque par document, par la fiabilité en série (fiche 29), arrondi à 4 décimales :

$$
1 - (1 - 0{,}0001642)^{300} = 0{,}0481
$$

**Étape 3.** Documents touchés par jour : 2 000 × 0,0481 = 96.

**Étape 4.** À T = 0,2 : Δ/T = 30,5, et le risque par token tombe à e⁻³⁰,⁵ ≈ 5,7 × 10⁻¹⁴, soit 1,7 × 10⁻¹¹ par document.

**Décision de l'agent.** Les appels d'outils et le JSON sont décodés à T = 0,2 (ou en glouton), et un validateur recalcule le ratio d'endettement à partir des mensualités et du salaire avant toute écriture. Le texte libre destiné au client peut garder une température plus haute. Sur une API qui n'accepte pas de réglage de température, la banque s'appuie sur les sorties structurées et le même validateur (leçon, étape 2).

**Contre-calcul.** « 0,0164 % par token, c'est négligeable » : sur 300 tokens, cela fait 4,81 % des documents, soit 96 pré-décisions fausses ou rejetées par jour. Le cas grave est le champ corrompu accepté : un ratio réel de 52,4 % recopié « 42,4 » ferait passer un dossier sous le plafond de 50 % du ratio d'endettement total fixé par la CBUAE.

**Sensibilité.** Valeur de bascule de T pour l'objectif de 0,1 % : il faut un risque par token d'au plus 1 − 0,999^(1/300) = 3,335 × 10⁻⁶, donc Δ/T ≥ ln((1 − 3,335 × 10⁻⁶) / 3,335 × 10⁻⁶) = 12,611, soit

$$
T \le \frac{6{,}1}{12{,}611} = 0{,}48370
$$

À T = 0,5, juste au-dessus, on obtient 0,151 % de documents touchés. Si l'écart Δ tombe à 4 (tokens moins sûrs), la bascule descend à 4 / 12,611 = 0,31718 (exercice 7).

**En production.** On suit le taux de documents rejetés par le validateur (alerte au-dessus de 0,1 %) et le nombre de relances par dossier. La banque doit pouvoir rejouer chaque pré-décision ; le plafond de 50 % (30 % pour un retraité) et les autres règles de la CBUAE sont vérifiés par du code, jamais par le modèle.

### Cas 3 — Promoteur à Dubaï et Abu Dhabi : des annonces variées sans mot absurde

**Contexte.** Un promoteur fait rédiger par un agent, en anglais et en arabe, les descriptions des 400 lots d'une tour vendue sur plan. Le premier adjectif de chaque description sort d'une softmax sur cinq candidats. Le promoteur veut deux choses : de la variété (le même adjectif d'ouverture dans au plus la moitié des annonces, soit p₁ ≤ 0,5) et aucun adjectif absurde (en moyenne moins d'une annonce sur les 400 avec le cinquième candidat). Les prix en AED et les surfaces en sqft ne sont jamais générés : le code les insère depuis la base du projet. Les logits et les objectifs sont illustratifs.

**Données.**

| Candidat | 1 « lumineux » | 2 « spacieux » | 3 « élégant » | 4 « calme » | 5 « bleue » (absurde) |
| --- | --- | --- | --- | --- | --- |
| Logit | 2,2 | 1,6 | 1,4 | 0,2 | −1,5 |

Objectifs : p₁ ≤ 0,5 et 400 × p₅ < 1. Troncature possible : garder les k = 3 meilleurs candidats et renormaliser (leçon, point 6).

**Calcul pas à pas.** Probabilités arrondies à 4 décimales.

**Étape 1.** Sans troncature, selon T :

| T | p₁ | p₅ | 400 × p₅ |
| --- | --- | --- | --- |
| 0,6 | 0,5991 | 0,0013 | 0,50 |
| 0,85 | 0,5021 | 0,0065 | 2,58 |
| 1 | 0,4633 | 0,0115 | 4,58 |
| 1,2 | 0,4247 | 0,0195 | 7,78 |

**Étape 2.** Les deux bascules, par dichotomie (démonstration 4 : p₁ décroît et p₅ croît avec T) : p₁ = 0,5 pour T = 0,85702, et 400 × p₅ = 1 pour T = 0,68360. La variété exige T ≥ 0,85702, l'absence d'absurde T ≤ 0,68360 : aucune température ne tient les deux objectifs.

**Étape 3.** Troncature à T = 1,2 : les trois premiers candidats gardent la masse M = 0,4247 + 0,2576 + 0,2180 = 0,9003, et l'on divise par M :

$$
q = \left(\frac{0{,}4247}{0{,}9003}\ ;\ \frac{0{,}2576}{0{,}9003}\ ;\ \frac{0{,}2180}{0{,}9003}\right) = (0{,}4717\ ;\ 0{,}2861\ ;\ 0{,}2422)
$$

**Étape 4.** Contrôle : q₁ = 0,4717 ≤ 0,5, soit environ 400 × 0,4717 = 189 annonces avec « lumineux » ; le candidat absurde a une probabilité nulle. Les rapports entre candidats gardés ne changent pas (démonstration 3).

**Décision de l'agent.** T = 1,2 avec troncature aux 3 meilleurs candidats : la variété est tenue et la queue absurde disparaît. La température seule ne suffit pas, parce que les deux objectifs tirent T dans des sens opposés.

**Contre-calcul.** « Baisser T supprime les mots absurdes » : à T = 0,6, il reste 0,50 annonce absurde en moyenne (jamais zéro, démonstration 1) et 400 × 0,5991 = 240 annonces commencent par le même mot. « Monter T pour varier » : à T = 1,5, sans troncature, 13 annonces sur 400 contiennent « bleue » ; à 60 AED de relecture et de réécriture par annonce, cela fait 780 AED, sans compter l'image du promoteur.

**Sensibilité.** Avec la troncature, la contrainte de variété devient q₁ ≤ 0,5 ; la bascule est T = 1,00270, et à T = 1 on obtiendrait q₁ = 0,5005, juste au-dessus. Le choix T = 1,2 laisse donc une marge de 0,2 sur la température.

**En production.** On suit la part d'annonces dont un token est hors des 3 premiers candidats (attendue nulle) et la fréquence du premier mot le plus courant (alerte au-dessus de 50 %). On contrôle aussi que chaque prix en AED et chaque surface en sqft de l'annonce sont identiques à la base ; les règles de publicité de la RERA et les références du DLD sont à confirmer avec le texte en vigueur.

### Cas 4 — Cabinet RH multi-émirats : calibrer le routeur par la température

**Contexte.** Un cabinet RH présent dans plusieurs émirats oriente les demandes des salariés, en arabe ou en anglais, vers quatre outils : fin de service, salaire versé par le WPS, visa, autres. Le routeur décide seul quand il est assez sûr, sinon il pose une question de clarification. L'historique montre que le modèle est trop sûr de lui ; l'équipe de données a ajusté sur un jeu de validation une température de calibration T = 1,5 (« temperature scaling »). La question : pour la demande « calcul de mon indemnité de fin de service après 7 ans », faut-il router automatiquement ? Logits, coûts et volume sont illustratifs.

**Données.**

| Outil | fin de service | WPS | visa | autres |
| --- | --- | --- | --- | --- |
| Logit | 5,0 | 1,0 | 0,5 | 0,0 |

Autres données : une erreur de routage coûte 40 AED (reprise par un consultant), une question de clarification 2 AED ; température calibrée T = 1,5 ; 1 800 demandes de ce profil par mois.

**Calcul pas à pas.** Probabilités arrondies à 5 décimales, coûts à 2 décimales.

**Étape 1.** Seuil de décision. Router coûte en moyenne (1 − p) × 40 et clarifier 2 : router est préférable si (1 − p) × 40 < 2, soit

$$
p > 1 - \frac{2}{40} = 0{,}95
$$

**Étape 2.** Probabilité non calibrée (T = 1) : écarts (0 ; −4 ; −4,5 ; −5), exponentielles (1 ; 0,018316 ; 0,011109 ; 0,006738), somme 1,036163 :

$$
p_{\text{fin}} = \frac{1}{1{,}036163} = 0{,}96510
$$

**Étape 3.** Probabilité calibrée (T = 1,5) : écarts (0 ; −2,666667 ; −3 ; −3,333333), exponentielles (1 ; 0,069483 ; 0,049787 ; 0,035674), somme 1,154945 (1,154944 si l'on additionne les termes déjà arrondis) :

$$
p_{\text{fin}} = \frac{1}{1{,}154945} = 0{,}86584
$$

**Étape 4.** L'ordre ne change pas (démonstration 3) : le rapport fin de service / WPS vaut e⁴ = 54,598 à T = 1 et e^(4/1,5) = 14,392 à T = 1,5, toujours très supérieur à 1.

**Décision de l'agent.** Avec la probabilité calibrée, 0,86584 < 0,95 : le routeur pose une question de clarification (« s'agit-il de votre indemnité de fin de service ou de votre dernier salaire ? »). L'outil le plus probable reste « fin de service » ; la calibration change la décision de router seul, pas le choix de l'outil.

**Contre-calcul.** Avec la probabilité non calibrée, 0,96510 > 0,95 : le routeur croit que router coûte (1 − 0,96510) × 40 = 1,40 AED et route seul. Mais si la calibration est juste, il se trompe 1 − 0,86584 = 13,4 % du temps, d'où un coût réel de 5,37 AED par demande au lieu des 2 AED de la clarification, soit 3,37 AED perdus par demande et 1 800 × 3,37 = 6 066 AED par mois.

**Sensibilité.** Par dichotomie, la probabilité de « fin de service » vaut exactement 0,95 pour T = 1,09451 : si la vraie température de calibration était sous cette valeur, router seul serait le bon choix. Si le coût d'une erreur passait de 40 à 100 AED, le seuil monterait à 1 − 2/100 = 0,98, et la clarification resterait préférable même sans calibration.

**En production.** On suit chaque mois l'erreur de calibration (l'écart entre probabilité annoncée et taux de bon routage, par tranche) et le taux de clarifications. Une demande de fin de service mal routée produit un montant faux : l'outil applique le barème du décret-loi fédéral 33/2021, et le paiement passe par le WPS après validation humaine.

## Entraînement sur feuille A4

**Exercice 1.** Calculer la softmax de (0 ; 0 ; 0).

**Exercice 2.** Logits (1 ; 0), T = 1. Calculer p₁ avec la formule de la sigmoïde.

**Exercice 3.** Deux tokens ont des logits qui diffèrent de 2. Quel est le rapport de leurs probabilités à T = 1, puis à T = 2 ?

**Exercice 4.** Montrer que la softmax de (1000 ; 999) se calcule sans débordement avec la démonstration 2, et donner le résultat.

**Exercice 5.** Calculer ∂p₁/∂z₁ pour les logits (2 ; 1 ; 0) à T = 1.

**Exercice 6.** Calculer la softmax de (2 ; 0) à T = 0,5 et à T = 2.

**Exercice 7.** Dans le cas 2, un nouveau schéma de JSON contient des champs moins prévisibles : l'écart Δ tombe à 4. Calculer le risque par document à T = 0,7, puis la température maximale qui tient l'objectif de 0,1 %, et dire si la décision change.

**Exercice 8.** Trouver l'erreur. Un collègue écrit : « avec T = 0,5, on divise les logits par 0,5, donc les écarts sont divisés par deux et la distribution s'aplatit. » Corriger, avec les logits (2 ; 1 ; 0).

**Exercice 9.** Redémontrer de mémoire que la softmax ne change pas quand on retranche une même constante à tous les logits (démonstration 2), puis l'appliquer aux logits (101 ; 100 ; 99).

## Corrigé

**Exercice 1.** Tous les logits sont égaux : chaque exponentielle vaut e⁰ = 1, la somme vaut 3, et chaque probabilité 1/3 = 0,33333.

**Exercice 2.** p₁ = 1/(1 + e⁻¹) = 1/(1 + 0,36788) = 1/1,36788 = 0,73106.

**Exercice 3.** Par la démonstration 3, le rapport vaut e^(2/T) : e² = 7,389 à T = 1, et e¹ = 2,718 à T = 2.

**Exercice 4.** On retranche 1 000 : softmax(0 ; −1), dont les exponentielles 1 et e⁻¹ = 0,36788 ne débordent pas ; somme 1,36788 ; résultat (1/1,36788 ; 0,36788/1,36788) = (0,73106 ; 0,26894).

**Exercice 5.** Par la démonstration 6 avec i = j = 1 et T = 1 : p₁(1 − p₁) = 0,66524 × 0,33476 = 0,22270.

**Exercice 6.** Par la sigmoïde : à T = 0,5, l'écart divisé vaut 4, p₁ = 1/(1 + e⁻⁴) = 0,98201 ; à T = 2, il vaut 1, p₁ = 0,73106. Le second token reçoit 0,01799 puis 0,26894.

**Exercice 7.** Δ/T = 4 / 0,7 = 5,7143 ; e^5,7143 = 303,17 ; risque par token 1/(1 + 303,17) = 0,003288 ; par document 1 − (1 − 0,003288)³⁰⁰ = 0,6277, soit 62,8 % des documents touchés. La température maximale est 4 / 12,611 = 0,31718 : la décision du cas 2 (T = 0,2) reste valable, mais T = 0,7 devient inacceptable et même T = 0,45 ne suffit plus.

**Exercice 8.** Diviser par 0,5, c'est multiplier par 2 : les logits deviennent (4 ; 2 ; 0), les écarts **doublent** et la distribution se **concentre**, (0,86681 ; 0,11731 ; 0,01588) contre (0,66524 ; 0,24473 ; 0,09003) à T = 1. C'est T > 1 qui aplatit.

**Exercice 9.** Étape 1 : exp((zᵢ − a)/T) = e^(−a/T) exp(zᵢ/T). Étape 2 : le même facteur sort de chaque terme du dénominateur. Étape 3 : il se simplifie. Application : on retranche 101, softmax(0 ; −1 ; −2) = (0,66524 ; 0,24473 ; 0,09003), les mêmes probabilités que pour (2 ; 1 ; 0).

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(z, T)`** — Cette fonction est le jury qui transforme des notes brutes, les logits, en parts d'un même gâteau dont la somme fait exactement 1, la température T réglant la sévérité du jury : elle reçoit la liste des logits et une température, refuse par une `ValueError` une température nulle ou négative, puisque T = 0 serait un simple argmax, ainsi qu'une liste vide ou contenant un infini ou un NaN. Elle retranche d'abord le plus grand logit pour qu'aucune exponentielle ne déborde, calcule exp((zᵢ − max)/T) pour chaque choix, divise chacune par leur somme et renvoie la liste des probabilités, par exemple 0,66524, 0,24473 et 0,09003 pour (2, 1, 0) à T = 1, et la même chose pour (1000, 999) que pour (1, 0).

**`arrondi(p, n)`** — Ce petit utilitaire est le greffier qui recopie au propre des nombres trop longs pour la page : il reçoit une liste de nombres et un nombre de décimales, cinq par défaut, arrondit chaque élément avec `round` et renvoie la nouvelle liste, sans toucher à la liste d'origine. Il ne calcule rien de nouveau, mais il permet d'imprimer des lois lisibles comme [0.86681, 0.11731, 0.01588] et, surtout, d'écrire des `assert` qui comparent les résultats du programme aux valeurs à cinq décimales, ou à quatre quand on lui passe `4`, qui figurent dans le texte de la fiche.

**`sigmoide(ecart, T)`** — Celle-ci raconte le duel à deux candidats, le cas où la softmax se réduit à une seule courbe en S : elle reçoit l'écart de logits entre les deux choix et la température, divise l'écart par T, puis renvoie la probabilité du premier choix, 1 / (1 + e^(−écart/T)). Pour ne jamais faire déborder l'exponentielle, elle choisit entre deux écritures équivalentes selon le signe de l'écart divisé, et elle donne 0,73106 pour un écart de 1, 0,98201 pour un écart de 2 à T = 0,5 ; le cas 2 l'appelle avec un écart négatif pour obtenir le risque qu'un token faux l'emporte.

**`risque_document(ecart, T, n_tokens)`** — Cette fonction est l'actuaire qui sait qu'une petite faute par mot finit par toucher presque tous les longs textes : elle reçoit l'écart de logits entre le bon token et son concurrent, la température et le nombre de tokens du document, calcule avec `sigmoide` le risque ε qu'un seul token soit faux, puis renvoie la probabilité qu'au moins un des n tokens le soit, 1 − (1 − ε)ⁿ, la fiabilité en série de la fiche 29. Elle passe par `log1p` et `expm1` pour rester exacte quand ε est minuscule, et donne 0,0481 pour 300 tokens, un écart de 6,1 et T = 0,7, contre environ 1,7 × 10⁻¹¹ à T = 0,2.

**`dichotomie(f, cible, bas, haut, croissante, tours)`** — Ici l'on suit un chercheur d'or qui coupe sans cesse la rivière en deux pour retrouver la pépite : la fonction reçoit une fonction monotone f de la température, la valeur cible à atteindre, un intervalle [bas, haut], le sens de variation de f et un nombre de tours, quatre-vingts par défaut. À chaque tour elle évalue f au milieu de l'intervalle, garde la moitié où se trouve forcément la solution selon que f est croissante ou décroissante, et renvoie à la fin le milieu de l'intervalle restant ; c'est elle qui trouve les températures de bascule 0,22875 du cas 1, 0,85702 et 0,6836 du cas 3, 1,09451 du cas 4.

**`tronquer(p, k)`** — Cette fonction est le sélectionneur qui ne garde que les k meilleurs joueurs et leur redistribue tout le temps de jeu : elle reçoit une loi de probabilité et le nombre k de candidats à conserver, trie les indices par probabilité décroissante, garde les k premiers, calcule leur masse M, puis met à zéro tous les autres et divise les gardés par M. Elle renvoie à la fois la nouvelle loi et cette masse, par exemple M = 0,9003 et (0,4717, 0,2861, 0,2422) pour les trois meilleurs adjectifs du cas 3 à T = 1,2, ce qui supprime l'adjectif absurde sans changer les rapports entre les candidats retenus.

**`cas_1_routeur_assurance()`** — Cette fonction met en scène le routeur d'outils d'un assureur auto et santé, qui choisit à chaque message entre quatre outils de logits 3,2, 1,1, 2,4 et 0,3, l'outil « rembourser » n'étant jamais le bon : sur 10 000 messages par jour, elle calcule la loi à T = 1, 0,3 et 2 et en déduit environ 752,7, 8,5 puis 1 551,9 tirages de « rembourser ». Elle cherche par `dichotomie` la température 0,22875 qui ramène ce nombre à un par jour, chiffre à T = 0,3 les 9 validations humaines à 15 AED, soit 135 AED par jour, contre 22 500 AED de remboursements indus sans garde-fou, et les 3 109 tirages par an, puis renvoie lois et montants dans un dictionnaire.

**`cas_2_json_banque()`** — On y voit l'agent de pré-instruction de crédit d'une banque de détail qui écrit pour chaque dossier un JSON de 300 tokens, avec un écart de logits de 6,1 entre le bon token et son rival et 2 000 dossiers par jour : la fonction calcule à T = 0,7 un risque par token de 0,000164 et par document de 0,0481, soit 96 dossiers touchés par jour, puis à T = 0,2 un risque devenu négligeable. Elle remonte ensuite de l'objectif de 0,1 % au risque maximal par token, 3,335 × 10⁻⁶, au rapport minimal Δ/T de 12,611 et à la température maximale 0,4837, vérifie qu'à T = 0,5 on dépasse déjà l'objectif avec 0,151 %, retient « T = 0.2 + validateur » et renvoie ces valeurs.

**`cas_3_annonces_immobilier()`** — Cette fonction raconte le rédacteur des 400 annonces d'une tour vendue sur plan, qui veut à la fois de la variété, le premier adjectif à au plus 0,5, et aucune annonce absurde, moins d'une sur 400 avec le cinquième candidat : avec les logits 2,2, 1,6, 1,4, 0,2 et −1,5, elle dresse la table des lois de T = 0,6 à T = 1,5 et trouve par `dichotomie` que la variété exige T ≥ 0,85702 alors que l'absence d'absurde exige T ≤ 0,6836, deux contraintes incompatibles. Elle tronque alors la loi de T = 1,2 aux trois meilleurs candidats, obtient q₁ = 0,4717, soit 189 annonces « lumineux », calcule la bascule 1,0027 avec troncature, choisit « T = 1.2 + top-3 » et renvoie le tout.

**`cas_4_routeur_rh()`** — Ici l'on suit le routeur d'un cabinet RH qui hésite entre envoyer seul une demande vers l'outil de fin de service ou poser une question de clarification : avec 40 AED par erreur et 2 AED par clarification, la fonction fixe le seuil 1 − 2/40 = 0,95, puis compare la probabilité brute 0,9651 à T = 1, qui ferait « router », à la probabilité calibrée 0,86584 à T = 1,5, qui impose « clarifier ». Elle chiffre le coût cru de 1,40 AED, le coût réel de 5,37 AED, la perte de 3,37 AED par demande, soit 6 066 AED par mois sur 1 800 demandes, trouve la température de bascule 1,09451 et renvoie ces grandeurs avec les deux décisions.

**`main()`** — C'est l'examinateur qui fait repasser à la softmax chacune des épreuves de la fiche, chaque résultat contre-signé par un `assert` : il commence par la loi de (2, 1, 0) à trois températures, constate que `math.exp(1000)` déborde alors que la forme stable s'en sort, vérifie que les rapports de probabilités valent e^((zᵢ − zⱼ)/T) même quand on ajoute un quatrième choix, que la loi se concentre quand T baisse, que la sigmoïde est la softmax à deux choix et que la dérivée analytique concorde avec une dérivée numérique. Il appelle ensuite les quatre cas et contrôle leurs dictionnaires, rejoue les exercices du corrigé, vérifie que les logits vides, infinis ou NaN et la température nulle sont refusés, et n'imprime « OK — toutes les vérifications sont passées. » qu'en l'absence de toute erreur.

```python
"""Démonstration 04 — softmax et température : loi, stabilité, rapports, limites, sigmoïde, dérivée, quatre cas aux EAU."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def softmax(z, T=1.0):
    """pᵢ = exp(zᵢ / T) / Σⱼ exp(zⱼ / T), forme stable : on retranche d'abord le maximum."""
    if T <= 0:
        raise ValueError("T doit être strictement positive (T = 0 est un argmax)")
    if not z or any(not math.isfinite(x) for x in z):
        raise ValueError("logits vides ou non finis")
    m = max(z)
    e = [math.exp((x - m) / T) for x in z]
    s = sum(e)
    return [x / s for x in e]


def arrondi(p, n=5):
    return [round(x, n) for x in p]


def sigmoide(ecart, T=1.0):
    """Softmax de deux choix : 1 / (1 + e^(-écart/T)), calculée sans débordement."""
    x = ecart / T
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    return math.exp(x) / (1.0 + math.exp(x))


def risque_document(ecart, T, n_tokens):
    """1 − (1 − ε)^n avec ε = 1 / (1 + e^(écart/T)) : au moins un token faux sur n (fiche 29)."""
    eps = sigmoide(-ecart, T)
    return -math.expm1(n_tokens * math.log1p(-eps))


def dichotomie(f, cible, bas, haut, croissante=True, tours=80):
    """Température T dans [bas, haut] où f(T) = cible, pour f monotone (démonstration 4)."""
    for _ in range(tours):
        milieu = (bas + haut) / 2
        if (f(milieu) < cible) == croissante:
            bas = milieu
        else:
            haut = milieu
    return (bas + haut) / 2


def tronquer(p, k):
    """Garde les k plus grandes probabilités et renormalise par leur masse M (leçon, point 6)."""
    gardes = sorted(range(len(p)), key=lambda i: p[i], reverse=True)[:k]
    masse = sum(p[i] for i in gardes)
    return [p[i] / masse if i in gardes else 0.0 for i in range(len(p))], masse


def cas_1_routeur_assurance() -> dict:
    """[ASSUR] routeur de 4 outils : tirages de « rembourser » selon T, garde-fou humain."""
    outils = [3.2, 1.1, 2.4, 0.3]
    volume, cout_indu, cout_validation = 10_000, 2_500, 15
    lois = {}
    for T in (1, 0.3, 2):
        p = softmax(outils, T)
        lois[T] = p
        print(f"Cas 1 ASSUR : routeur à T = {T} : {arrondi(p)} ; rembourser ≈ {volume * p[1]:.1f} fois par jour")
    t_un = dichotomie(lambda T: volume * softmax(outils, T)[1], 1.0, 0.05, 1.0)
    par_jour = volume * lois[0.3][1]
    print(f"  à T = 0.3 : {round(par_jour)} validations = {round(par_jour) * cout_validation} AED/jour au lieu de"
          f" {round(par_jour) * cout_indu} AED ; {par_jour * 365:.0f} tirages/an ; 1 tirage/jour à T = {t_un:.5f}")
    return {"outils": outils, "lois": lois, "par_jour": par_jour, "t_un": t_un,
            "validation": round(par_jour) * cout_validation, "indus": round(par_jour) * cout_indu}


def cas_2_json_banque() -> dict:
    """[BANQUE] JSON de 300 tokens : risque par token (sigmoïde), par document (série), bascule de T."""
    ecart, n_tokens, dossiers, objectif = 6.1, 300, 2_000, 0.001
    eps_07 = sigmoide(-ecart, 0.7)
    doc_07 = risque_document(ecart, 0.7, n_tokens)
    eps_02 = sigmoide(-ecart, 0.2)
    doc_02 = risque_document(ecart, 0.2, n_tokens)
    eps_max = -math.expm1(math.log1p(-objectif) / n_tokens)
    seuil_ecart_sur_t = math.log((1 - eps_max) / eps_max)
    t_max = ecart / seuil_ecart_sur_t
    decision = "T = 0.2 + validateur" if doc_02 <= objectif < doc_07 else "revoir"
    print(f"Cas 2 BANQUE : T = 0.7 : Δ/T = {ecart / 0.7:.4f}, e^(Δ/T) = {math.exp(ecart / 0.7):.1f}, token {eps_07:.6f},"
          f" document {doc_07:.4f} -> {round(dossiers * doc_07)} dossiers/jour")
    print(f"  T = 0.2 : token {eps_02:.1e}, document {doc_02:.1e} -> {decision} ; bascule : ε ≤ {eps_max:.3e},"
          f" Δ/T ≥ {seuil_ecart_sur_t:.3f}, T ≤ {t_max:.5f} ; à T = 0.5 : {risque_document(ecart, 0.5, n_tokens):.5f}")
    return {"eps_07": eps_07, "doc_07": doc_07, "eps_02": eps_02, "doc_02": doc_02, "eps_max": eps_max,
            "seuil": seuil_ecart_sur_t, "t_max": t_max, "decision": decision,
            "doc_05": risque_document(ecart, 0.5, n_tokens), "touches": round(dossiers * doc_07)}


def cas_3_annonces_immobilier() -> dict:
    """[IMMO] premier adjectif de 400 annonces : variété (p1 <= 0.5) contre queue absurde (400 p5 < 1)."""
    z = [2.2, 1.6, 1.4, 0.2, -1.5]
    lots = 400
    table = {T: softmax(z, T) for T in (0.6, 0.85, 1, 1.2, 1.5)}
    t_variete = dichotomie(lambda T: softmax(z, T)[0], 0.5, 0.3, 3.0, croissante=False)
    t_queue = dichotomie(lambda T: lots * softmax(z, T)[4], 1.0, 0.3, 3.0)
    q, masse = tronquer(table[1.2], 3)
    t_variete_k3 = dichotomie(lambda T: tronquer(softmax(z, T), 3)[0][0], 0.5, 0.3, 3.0, croissante=False)
    q_t1 = tronquer(table[1], 3)[0][0]
    decision = "T = 1.2 + top-3" if q[0] <= 0.5 and q[4] == 0 and t_variete > t_queue else "revoir"
    for T in (0.6, 0.85, 1, 1.2):
        print(f"Cas 3 IMMO : T = {T} : p1 {table[T][0]:.4f}, p5 {table[T][4]:.4f}, 400 x p5 = {lots * table[T][4]:.2f}")
    print(f"  bascules : variété T >= {t_variete:.5f}, queue T <= {t_queue:.5f} ; top-3 à T = 1.2 : M = {masse:.4f},"
          f" q = {arrondi(q[:3], 4)} -> {decision}")
    print(f"  {lots * q[0]:.0f} annonces « lumineux » ; T = 0.6 : {lots * table[0.6][0]:.0f} identiques ; T = 1.5 :"
          f" {lots * table[1.5][4]:.0f} absurdes ; bascule top-3 {t_variete_k3:.5f}, q1 à T = 1 : {q_t1:.4f}")
    return {"table": table, "t_variete": t_variete, "t_queue": t_queue, "q": q, "masse": masse,
            "t_variete_k3": t_variete_k3, "q_t1": q_t1, "decision": decision}


def cas_4_routeur_rh() -> dict:
    """[RH] routeur calibré par la température : seuil 1 − 2/40, décision avant et après calibration."""
    z = [5.0, 1.0, 0.5, 0.0]
    cout_erreur, cout_clarif, t_calib, volume = 40, 2, 1.5, 1_800
    seuil = 1 - cout_clarif / cout_erreur
    p_brut, p_calib = softmax(z, 1.0), softmax(z, t_calib)
    decision = "router" if p_calib[0] > seuil else "clarifier"
    decision_brute = "router" if p_brut[0] > seuil else "clarifier"
    cout_cru = (1 - p_brut[0]) * cout_erreur
    cout_reel = (1 - p_calib[0]) * cout_erreur
    perte = round(cout_reel - cout_clarif, 2)
    t_bascule = dichotomie(lambda T: softmax(z, T)[0], seuil, 0.5, 3.0, croissante=False)
    print(f"Cas 4 RH : seuil {seuil:.2f} ; T = 1 : {arrondi(p_brut)} -> {decision_brute} ; T = 1.5 : {arrondi(p_calib)} -> {decision}")
    print(f"  coût cru {cout_cru:.2f} AED, réel {cout_reel:.2f} AED, perte {perte:.2f} x {volume} = {perte * volume:.0f} AED/mois ;"
          f" bascule T = {t_bascule:.5f} ; rapports {p_brut[0] / p_brut[1]:.3f} et {p_calib[0] / p_calib[1]:.3f}")
    return {"z": z, "seuil": seuil, "p_brut": p_brut, "p_calib": p_calib, "decision": decision,
            "decision_brute": decision_brute, "cout_cru": cout_cru, "cout_reel": cout_reel, "perte": perte,
            "mois": perte * volume, "t_bascule": t_bascule}


def main() -> None:
    # Mécanisme et exemple simple
    for T in (1, 0.5, 2):
        print(f"(2,1,0) à T = {T} : {arrondi(softmax([2, 1, 0], T))}")
    assert arrondi(softmax([2, 1, 0], 1)) == [0.66524, 0.24473, 0.09003]
    assert arrondi(softmax([2, 1, 0], 0.5)) == [0.86681, 0.11731, 0.01588]
    assert arrondi(softmax([2, 1, 0], 2)) == [0.50648, 0.3072, 0.18632]
    assert math.isclose(softmax([2, 1, 0], 2)[0] / softmax([2, 1, 0], 2)[1], math.exp(0.5))   # tableau : e^0,5
    assert [round(math.exp(-k), 5) for k in (1, 2, 4)] == [0.36788, 0.13534, 0.01832]
    assert round(1 + math.exp(-1) + math.exp(-2), 5) == 1.50321 and round(1 + math.exp(-2) + math.exp(-4), 5) == 1.15365
    assert round(math.exp(2), 5) == 7.38906 and round(math.exp(1), 5) == 2.71828 and round(math.exp(2) + math.exp(1) + 1, 5) == 11.10734
    assert round(math.exp(4), 5) == 54.59815 and round(math.exp(4) + math.exp(2) + 1, 5) == 62.98721
    assert round(math.exp(0.5), 5) == 1.64872 and round(math.exp(1) + math.exp(0.5) + 1, 5) == 5.367
    assert round(softmax([2, 1, 0])[0], 3) == 0.665 and round(softmax([2, 1, 0], 0.5)[0], 3) == 0.867

    # Démonstration 1
    z, T = [0.7, -1.2, 2.5], 0.8
    p = softmax(z, T)
    assert math.isclose(sum(p), 1) and min(p) > 0 and math.isclose(sum(softmax([2, 1, 0])), 1)
    assert softmax([4.2]) == [1.0]

    # Démonstration 2
    try:
        math.exp(1000)
    except OverflowError:
        deborde = True
    else:
        deborde = False
    print(f"D2 : exp(1000) déborde : {deborde} ; limite ln(max float) = {math.log(sys.float_info.max):.2f} ;"
          f" (1000, 999) -> {arrondi(softmax([1000, 999]))} ; 14.2 / 0.01 = {14.2 / 0.01:.0f} ; e^20 = {math.exp(20):.2e}")
    assert deborde and round(math.log(sys.float_info.max), 2) == 709.78 and round(14.2 / 0.01) == 1420
    assert arrondi(softmax([1000, 999])) == [0.73106, 0.26894] and round(math.exp(20) / 1e8, 2) == 4.85
    assert all(math.isclose(a, b) for a, b in zip(p, softmax([x - 100 for x in z], T)))
    assert all(math.isclose(a, b) for a, b in zip(p, softmax([x + 100 for x in z], T)))

    # Démonstration 3
    p210, p210_05 = softmax([2, 1, 0]), softmax([2, 1, 0], 0.5)
    p4 = softmax([2, 1, 0, 1.5])
    print(f"D3 : rapports {p210[0] / p210[1]:.5f} (T = 1) et {p210_05[0] / p210_05[1]:.5f} (T = 0.5) ;"
          f" avec un 4e choix {arrondi(p4)}, rapport {p4[0] / p4[1]:.5f} ; cote e^8.7143 = {math.exp(6.1 / 0.7):.0f}")
    assert round(p210[0] / p210[1], 5) == 2.71828 and round(p210_05[0] / p210_05[1], 5) == 7.38906
    assert arrondi(p4) == [0.47399, 0.17437, 0.06415, 0.28749] and round(p4[0] / p4[1], 5) == 2.71828
    assert math.isclose(p[2] / p[0], math.exp((2.5 - 0.7) / T)) and round(math.exp(6.1 / 0.7)) == 6089

    # Démonstration 4
    outils = [3.2, 1.1, 2.4, 0.3]
    pmax = [softmax(outils, t)[0] for t in (0.2, 0.3, 0.5, 1, 2)]
    print(f"D4 : p_max du routeur à T = 0.2 / 0.3 / 0.5 / 1 / 2 : {arrondi(pmax)} ; (3,3,1) à T = 0.01 :"
          f" {arrondi(softmax([3, 3, 1], 0.01), 1)}")
    assert arrondi(pmax) == [0.98199, 0.93418, 0.81973, 0.6147, 0.44349] and all(a > b for a, b in zip(pmax, pmax[1:]))
    assert softmax([1, 3, 2], 0.01)[1] > 0.999 and max(softmax([1, 3, 2], 1e6)) < 0.334
    assert arrondi(softmax([3, 3, 1], 0.01), 1) == [0.5, 0.5, 0.0]
    pmin = [softmax(outils, t)[3] for t in (0.2, 0.5, 1, 2, 10)]
    assert all(a < b for a, b in zip(pmin, pmin[1:]))

    # Démonstration 5
    print(f"D5 : sigmoïde (1,0) {sigmoide(1):.5f} ; (2,0) à T = 0.5 : {sigmoide(2, 0.5):.5f}, à T = 2 : {sigmoide(2, 2):.5f}")
    assert round(sigmoide(1), 5) == 0.73106 and math.isclose(sigmoide(1), softmax([1, 0])[0])
    assert round(1 + math.exp(-1), 5) == 1.36788 and round(sigmoide(2, 0.5), 5) == 0.98201 and round(sigmoide(2, 2), 5) == 0.73106
    assert math.isclose(sigmoide(2, 0.5), softmax([2, 0], 0.5)[0])

    # Démonstration 6
    d11 = p210[0] * (1 - p210[0])
    d12 = -p210[0] * p210[1]
    lineaire = p210[0] + 0.1 * d11
    exact = softmax([2.1, 1, 0])[0]
    d11_05 = p210_05[0] * (1 - p210_05[0]) / 0.5
    print(f"D6 : ∂p1/∂z1 = {d11:.5f}, ∂p1/∂z2 = {d12:.5f} ; z1 + 0.1 : linéaire {lineaire:.5f}, exact {exact:.5f} ;"
          f" à T = 0.5 : {d11_05:.5f}")
    assert round(d11, 5) == 0.2227 and round(1 - p210[0], 5) == 0.33476 and round(d12, 5) == -0.1628
    assert round(lineaire, 5) == 0.68751 and round(exact, 5) == 0.68713
    assert round(1 - p210_05[0], 5) == 0.13319 and round(d11_05, 5) == 0.2309
    h, i, j = 1e-6, 0, 2
    zj = list(z)
    zj[j] += h
    numerique = (softmax(zj, T)[i] - p[i]) / h
    assert math.isclose(numerique, p[i] * (0 - p[j]) / T, rel_tol=1e-4)      # dérivée, i ≠ j
    zi = list(z)
    zi[i] += h
    assert math.isclose((softmax(zi, T)[i] - p[i]) / h, p[i] * (1 - p[i]) / T, rel_tol=1e-4)
    assert abs(sum(p[i] * ((1 if i == k else 0) - p[k]) / T for k in range(3))) < 1e-12

    # Cas 1 — assurance
    c1 = cas_1_routeur_assurance()
    l1 = c1["lois"]
    assert [round(x - 3.2, 1) for x in outils] == [0.0, -2.1, -0.8, -2.9]
    assert [round(math.exp(x - 3.2), 6) for x in outils] == [1.0, 0.122456, 0.449329, 0.055023]
    assert round(sum(math.exp(x - 3.2) for x in outils), 6) == 1.626809
    assert arrondi(l1[1]) == [0.6147, 0.07527, 0.2762, 0.03382] and round(10_000 * l1[1][1], 1) == 752.7 and round(10_000 * l1[1][1]) == 753
    assert [round((x - 3.2) / 0.3, 6) for x in outils] == [0.0, -7.0, -2.666667, -9.666667]
    assert [round(math.exp((x - 3.2) / 0.3), 6) for x in outils] == [1.0, 0.000912, 0.069483, 0.000063]
    assert round(sum(math.exp((x - 3.2) / 0.3) for x in outils), 6) == 1.070459
    assert arrondi(l1[0.3]) == [0.93418, 0.00085, 0.06491, 6e-05] and round(c1["par_jour"], 1) == 8.5 and round(c1["par_jour"]) == 9
    assert arrondi(l1[2]) == [0.44349, 0.15519, 0.29728, 0.10403] and round(10_000 * l1[2][1]) == 1552
    assert c1["validation"] == 135 and c1["indus"] == 22_500 and round(c1["par_jour"] * 365) == 3109
    assert round(c1["t_un"], 5) == 0.22875 and math.isclose(10_000 * softmax(outils, c1["t_un"])[1], 1, rel_tol=1e-9)

    # Cas 2 — banque
    c2 = cas_2_json_banque()
    assert round(6.1 / 0.7, 4) == 8.7143 and round(math.exp(6.1 / 0.7), 1) == 6089.3 and round(c2["eps_07"], 6) == 0.000164
    assert round(c2["doc_07"], 4) == 0.0481 and round(1 - (1 - 0.0001642) ** 300, 4) == 0.0481 and round(c2["eps_07"], 7) == 0.0001642 and c2["touches"] == 96
    assert round(6.1 / 0.2, 1) == 30.5 and round(c2["eps_02"], 15) == 5.7e-14 and round(c2["doc_02"] * 1e11, 1) == 1.7
    assert c2["decision"] == "T = 0.2 + validateur" and round(c2["eps_max"] * 1e6, 3) == 3.335
    assert round(c2["seuil"], 3) == 12.611 and round(c2["t_max"], 5) == 0.4837 and round(c2["doc_05"] * 100, 3) == 0.151
    assert round(4 / c2["seuil"], 5) == 0.31718

    # Cas 3 — immobilier
    c3 = cas_3_annonces_immobilier()
    tb = c3["table"]
    assert [round(tb[t][0], 4) for t in (0.6, 0.85, 1, 1.2)] == [0.5991, 0.5021, 0.4633, 0.4247]
    assert [round(tb[t][4], 4) for t in (0.6, 0.85, 1, 1.2)] == [0.0013, 0.0065, 0.0115, 0.0195]
    assert [round(400 * tb[t][4], 2) for t in (0.6, 0.85, 1, 1.2)] == [0.5, 2.58, 4.58, 7.78]
    assert round(c3["t_variete"], 5) == 0.85702 and round(c3["t_queue"], 5) == 0.6836 and c3["t_queue"] < c3["t_variete"]
    assert arrondi(tb[1.2][:3], 4) == [0.4247, 0.2576, 0.218] and round(c3["masse"], 4) == 0.9003
    assert arrondi(c3["q"][:3], 4) == [0.4717, 0.2861, 0.2422] and c3["q"][3] == c3["q"][4] == 0.0
    assert round(400 * c3["q"][0]) == 189 and c3["decision"] == "T = 1.2 + top-3"
    assert math.isclose(c3["q"][0] / c3["q"][1], tb[1.2][0] / tb[1.2][1])
    assert round(400 * tb[0.6][4], 2) == 0.5 and round(400 * tb[0.6][0]) == 240
    assert round(400 * tb[1.5][4]) == 13 and 13 * 60 == 780
    assert round(c3["t_variete_k3"], 5) == 1.0027 and round(c3["q_t1"], 4) == 0.5005

    # Cas 4 — RH
    c4 = cas_4_routeur_rh()
    assert c4["seuil"] == 0.95
    assert [round(math.exp(x - 5.0), 6) for x in c4["z"]] == [1.0, 0.018316, 0.011109, 0.006738]
    assert round(sum(math.exp(x - 5.0) for x in c4["z"]), 6) == 1.036163 and round(c4["p_brut"][0], 5) == 0.9651
    assert [round((x - 5.0) / 1.5, 6) for x in c4["z"]] == [0.0, -2.666667, -3.0, -3.333333]
    assert [round(math.exp((x - 5.0) / 1.5), 6) for x in c4["z"]] == [1.0, 0.069483, 0.049787, 0.035674]
    assert round(sum(math.exp((x - 5.0) / 1.5) for x in c4["z"]), 6) == 1.154945 and round(c4["p_calib"][0], 5) == 0.86584
    assert round(1.0 + 0.069483 + 0.049787 + 0.035674, 6) == 1.154944
    assert round(c4["p_brut"][0] / c4["p_brut"][1], 3) == 54.598 and round(c4["p_calib"][0] / c4["p_calib"][1], 3) == 14.392
    assert c4["decision"] == "clarifier" and c4["decision_brute"] == "router"
    assert round(c4["cout_cru"], 2) == 1.40 and round(1 - c4["p_calib"][0], 3) == 0.134 and round(c4["cout_reel"], 2) == 5.37
    assert c4["perte"] == 3.37 and round(c4["mois"]) == 6_066 and round(c4["t_bascule"], 5) == 1.09451
    assert 1 - 2 / 100 == 0.98 and c4["p_brut"][0] < 0.98

    # Corrigé
    print("Corrigé")
    d_ex5 = softmax([2, 1, 0])[0] * (1 - softmax([2, 1, 0])[0])
    print(f"  ex1 {arrondi(softmax([0, 0, 0]))} ; ex2 {sigmoide(1):.5f} ; ex3 {math.exp(2):.3f} et {math.exp(1):.3f} ;"
          f" ex4 {arrondi(softmax([1000, 999]))} ; ex5 {d_ex5:.5f}")
    assert arrondi(softmax([0, 0, 0])) == [0.33333] * 3 and round(1 / (1 + math.exp(-1)), 5) == 0.73106
    assert round(math.exp(2), 3) == 7.389 and round(math.exp(1), 3) == 2.718 and round(d_ex5, 5) == 0.2227
    ex6 = (softmax([2, 0], 0.5), softmax([2, 0], 2))
    eps7 = sigmoide(-4, 0.7)
    doc7 = risque_document(4, 0.7, 300)
    print(f"  ex6 {arrondi(ex6[0])} et {arrondi(ex6[1])} ; ex7 Δ/T = {4 / 0.7:.4f}, e^(Δ/T) = {math.exp(4 / 0.7):.2f},"
          f" token {eps7:.6f}, document {doc7:.4f}, T max {4 / c2['seuil']:.5f}")
    assert arrondi(ex6[0]) == [0.98201, 0.01799] and arrondi(ex6[1]) == [0.73106, 0.26894]
    assert round(4 / 0.7, 4) == 5.7143 and round(math.exp(4 / 0.7), 2) == 303.17 and round(eps7, 6) == 0.003288
    assert round(doc7, 4) == 0.6277 and round(doc7, 3) == 0.628 and risque_document(4, 0.45, 300) > 0.001 >= risque_document(4, 0.2, 300)
    print(f"  ex8 (4, 2, 0) -> {arrondi(softmax([4, 2, 0]))} ; ex9 (101, 100, 99) -> {arrondi(softmax([101, 100, 99]))}")
    assert arrondi(softmax([4, 2, 0])) == arrondi(softmax([2, 1, 0], 0.5))
    assert arrondi(softmax([101, 100, 99])) == [0.66524, 0.24473, 0.09003]
    for invalide in ([], [1.0, float("inf")], [1.0, float("nan")]):
        try:
            softmax(invalide)
        except ValueError:
            continue
        raise AssertionError("logits invalides acceptés")
    try:
        softmax([1, 2], 0)
    except ValueError:
        pass
    else:
        raise AssertionError("T = 0 accepté")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
(2,1,0) à T = 1 : [0.66524, 0.24473, 0.09003]
(2,1,0) à T = 0.5 : [0.86681, 0.11731, 0.01588]
(2,1,0) à T = 2 : [0.50648, 0.3072, 0.18632]
D2 : exp(1000) déborde : True ; limite ln(max float) = 709.78 ; (1000, 999) -> [0.73106, 0.26894] ; 14.2 / 0.01 = 1420 ; e^20 = 4.85e+08
D3 : rapports 2.71828 (T = 1) et 7.38906 (T = 0.5) ; avec un 4e choix [0.47399, 0.17437, 0.06415, 0.28749], rapport 2.71828 ; cote e^8.7143 = 6089
D4 : p_max du routeur à T = 0.2 / 0.3 / 0.5 / 1 / 2 : [0.98199, 0.93418, 0.81973, 0.6147, 0.44349] ; (3,3,1) à T = 0.01 : [0.5, 0.5, 0.0]
D5 : sigmoïde (1,0) 0.73106 ; (2,0) à T = 0.5 : 0.98201, à T = 2 : 0.73106
D6 : ∂p1/∂z1 = 0.22270, ∂p1/∂z2 = -0.16280 ; z1 + 0.1 : linéaire 0.68751, exact 0.68713 ; à T = 0.5 : 0.23090
Cas 1 ASSUR : routeur à T = 1 : [0.6147, 0.07527, 0.2762, 0.03382] ; rembourser ≈ 752.7 fois par jour
Cas 1 ASSUR : routeur à T = 0.3 : [0.93418, 0.00085, 0.06491, 6e-05] ; rembourser ≈ 8.5 fois par jour
Cas 1 ASSUR : routeur à T = 2 : [0.44349, 0.15519, 0.29728, 0.10403] ; rembourser ≈ 1551.9 fois par jour
  à T = 0.3 : 9 validations = 135 AED/jour au lieu de 22500 AED ; 3109 tirages/an ; 1 tirage/jour à T = 0.22875
Cas 2 BANQUE : T = 0.7 : Δ/T = 8.7143, e^(Δ/T) = 6089.3, token 0.000164, document 0.0481 -> 96 dossiers/jour
  T = 0.2 : token 5.7e-14, document 1.7e-11 -> T = 0.2 + validateur ; bascule : ε ≤ 3.335e-06, Δ/T ≥ 12.611, T ≤ 0.48370 ; à T = 0.5 : 0.00151
Cas 3 IMMO : T = 0.6 : p1 0.5991, p5 0.0013, 400 x p5 = 0.50
Cas 3 IMMO : T = 0.85 : p1 0.5021, p5 0.0065, 400 x p5 = 2.58
Cas 3 IMMO : T = 1 : p1 0.4633, p5 0.0115, 400 x p5 = 4.58
Cas 3 IMMO : T = 1.2 : p1 0.4247, p5 0.0195, 400 x p5 = 7.78
  bascules : variété T >= 0.85702, queue T <= 0.68360 ; top-3 à T = 1.2 : M = 0.9003, q = [0.4717, 0.2861, 0.2422] -> T = 1.2 + top-3
  189 annonces « lumineux » ; T = 0.6 : 240 identiques ; T = 1.5 : 13 absurdes ; bascule top-3 1.00270, q1 à T = 1 : 0.5005
Cas 4 RH : seuil 0.95 ; T = 1 : [0.9651, 0.01768, 0.01072, 0.0065] -> router ; T = 1.5 : [0.86584, 0.06016, 0.04311, 0.03089] -> clarifier
  coût cru 1.40 AED, réel 5.37 AED, perte 3.37 x 1800 = 6066 AED/mois ; bascule T = 1.09451 ; rapports 54.598 et 14.392
Corrigé
  ex1 [0.33333, 0.33333, 0.33333] ; ex2 0.73106 ; ex3 7.389 et 2.718 ; ex4 [0.73106, 0.26894] ; ex5 0.22270
  ex6 [0.98201, 0.01799] et [0.73106, 0.26894] ; ex7 Δ/T = 5.7143, e^(Δ/T) = 303.17, token 0.003288, document 0.6277, T max 0.31718
  ex8 (4, 2, 0) -> [0.86681, 0.11731, 0.01588] ; ex9 (101, 100, 99) -> [0.66524, 0.24473, 0.09003]
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme transforme des scores bruts en probabilités, avec une température, de façon numériquement stable ; une variante cherche par dichotomie la température où une probabilité franchit un seuil métier.

```text
ALGORITHME Softmax
ENTRÉES : logits z₁ … z_K, température T > 0
SORTIE  : probabilités p₁ … p_K

  SI T ≤ 0 OU un zᵢ non fini ALORS ERREUR « entrée invalide »
  m ← max(z₁ … z_K)
  S ← 0
  POUR i DE 1 À K FAIRE
      eᵢ ← exp((zᵢ − m) / T)
      S ← S + eᵢ
  FIN POUR
  POUR i DE 1 À K FAIRE
      pᵢ ← eᵢ / S
  FIN POUR
  RETOURNER p

ALGORITHME TempératureDeBascule
ENTRÉES : f(T) monotone (une probabilité ou un nombre de tirages), cible, intervalle [bas, haut]
SORTIE  : la température où f(T) = cible
  RÉPÉTER 80 FOIS
      milieu ← (bas + haut) / 2
      SI f(milieu) est du même côté de la cible que f(bas) ALORS bas ← milieu SINON haut ← milieu
  FIN RÉPÉTER
  RETOURNER (bas + haut) / 2
```

**Complexité.** O(K) en temps (trois passages : maximum, exponentielles, division) et O(K) en mémoire. Sur un vocabulaire de 100 000 tokens, c'est 100 000 exponentielles par token généré. La dichotomie fait 80 évaluations de f, chacune en O(K), et divise l'intervalle par 2⁸⁰ : la précision est celle des flottants.

**Du squelette au code.** Tout l'algorithme Softmax est la fonction `softmax(z, T)`. Le retrait du maximum (démonstration 2) est la ligne `m = max(z)`. Le routeur d'outils du cas 1 appelle `softmax(outils, T)` pour trois températures, puis multiplie p[1] par 10 000 pour obtenir le nombre de tirages de `rembourser` ; la fonction se trouve dans `cas_1_routeur_assurance`. TempératureDeBascule est la fonction `dichotomie`, utilisée dans les cas 1, 3 et 4. La sigmoïde de deux choix est `sigmoide`, le risque d'au moins un token faux `risque_document`, la troncature renormalisée `tronquer`. Les trois autres cas sont `cas_2_json_banque`, `cas_3_annonces_immobilier` et `cas_4_routeur_rh`.
