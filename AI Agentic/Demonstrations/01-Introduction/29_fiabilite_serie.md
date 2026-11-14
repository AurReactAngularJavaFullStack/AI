# 29 — Fiabilité en série : démonstrations

> Fiche : [29 — Fiabilité en série](<../../Images/01-Introduction/29_fiabilite_serie.md>) · Image : `29_fiabilite_serie.jpg` · Leçon : [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4, sans calculatrice sauf mention contraire.

## La formule

$$
P(\text{succès}) = p_1 \times p_2 \times \dots \times p_n = \prod_{i=1}^{n} p_i
$$

Un agent qui enchaîne n étapes indépendantes ne réussit que si toutes réussissent. pᵢ est la probabilité que l'étape i réussisse.

## Les symboles, un par un

$$
n
$$

n est le nombre d'étapes qui doivent toutes réussir pour que l'agent aille au bout sans erreur ; c'est un entier ≥ 1, porté en Python par `len(probas)`.

$$
p_i
$$

pᵢ est la probabilité que l'étape i réussisse, mesurée sur un jeu de cas ; c'est un réel sans unité dans [0, 1], porté par `probas[i]` (la liste s'appelle `etapes` dans les cas).

$$
\prod_{i=1}^{n}
$$

∏ se lit « multiplie ce qui suit pour i allant de 1 à n », comme ∑ additionne ; en Python, c'est `math.prod`.

$$
P(\text{succès})
$$

P(succès) est la probabilité que toute la chaîne réussisse ; c'est un réel dans [0, 1], renvoyé par `fiabilite(probas)`.

$$
\varepsilon_i = 1 - p_i
$$

εᵢ est le taux d'erreur de l'étape i, la probabilité qu'elle échoue ; c'est un réel dans [0, 1], calculé par `1.0 - p` dans `borne`.

$$
c
$$

c est la fiabilité visée pour l'agent entier, fixée par le métier (par exemple 0,90) ; c'est un réel dans ]0, 1[, porté par `cible`.

$$
n_{\max}
$$

nₘₐₓ est le plus grand nombre d'étapes de même fiabilité p compatible avec la cible c ; c'est un entier ≥ 0, renvoyé par `etapes_max(p, cible)` et rangé dans la variable `n_max`.

$$
p_{\min}
$$

pₘᵢₙ est la plus petite fiabilité commune par étape qui permet de tenir la cible avec n étapes ; c'est un réel dans ]0, 1[, renvoyé par `p_min_par_etape(n, cible)` et rangé dans la variable `p_min`.

$$
R
$$

R est le nombre de relances autorisées pour une étape après un échec détecté ; c'est un entier ≥ 0, porté par le paramètre `relances` de `avec_relances(p, relances)`.

$$
A_i, \qquad B_k = A_1 \cap A_2 \cap \dots \cap A_k
$$

Aᵢ est l'événement « l'étape i réussit » et Bₖ l'événement « les k premières étapes réussissent » ; ce sont des événements, pas des nombres, et le programme ne les représente pas.

## Le mécanisme, avant les preuves

Ce qui entre dans la formule, ce sont n nombres pᵢ compris entre 0 et 1, un par étape. La seule opération est la multiplication : on part de 1, parce qu'une chaîne vide ne peut pas échouer, et chaque étape multiplie ce qui reste par sa fiabilité. Multiplier par un nombre au plus égal à 1 ne peut que réduire : chaque étape retire la fraction εᵢ de la fiabilité **déjà acquise**, pas de la fiabilité de départ. Ce qui sort est un seul nombre, la probabilité que tout se passe bien, toujours plus petit que la plus faible des pᵢ.

Pourquoi un produit et pas une somme : la réussite exige l'étape 1 **et** l'étape 2 **et** toutes les suivantes, et la probabilité d'un « et » d'événements indépendants est le produit de leurs probabilités (démonstration 1). Une somme de probabilités dépasserait 1 dès deux étapes à 0,9 et ne répondrait à aucune question utile. Le logarithme éclaire la forme du résultat : ln P = ln p₁ + … + ln pₙ, le produit devient une somme de termes négatifs, et comme ln(1 − ε) ≈ −ε quand ε est petit, ln P ≈ −(ε₁ + … + εₙ) : les taux d'erreur s'additionnent (démonstration 3). L'ordre des étapes ne change pas P, parce que la multiplication est commutative, mais il change le coût : une vérification placée tôt arrête une chaîne condamnée avant de payer les étapes suivantes.

Petit film chiffré, avec trois étapes à 0,99, 0,98 et 0,97. On part de 1. Après l'étape 1 : 1 × 0,99 = 0,99, perte 0,01. Après l'étape 2 : 0,99 × 0,98 = 0,9702, perte 0,0198, soit 2 % de 0,99. Après l'étape 3 : 0,9702 × 0,97 = 0,941094, perte 0,029106, soit 3 % de 0,9702. La perte totale vaut 1 − 0,941094 = 0,058906, juste sous la somme des erreurs 0,01 + 0,02 + 0,03 = 0,06. Côté logarithmes : ln 0,99 = −0,010050, ln 0,98 = −0,020203, ln 0,97 = −0,030459, de somme −0,060712, et e⁻⁰,⁰⁶⁰⁷¹² redonne 0,941094.

Analogie Java/Spring : une requête n'atteint le contrôleur que si chaque filtre de la chaîne de Spring Security la laisse passer. Si chaque filtre rejetait à tort 1 % des requêtes, indépendamment des autres, dix filtres en rejetteraient à tort près de 10 % ; chaque filtre ajouté est un risque de plus, jamais un risque de moins.

## Démonstration 1 — Du cas à deux étapes au cas à n étapes

**Ce qu'on démontre.** Si les événements A₁, …, Aₙ sont mutuellement indépendants, la probabilité qu'ils se réalisent tous est le produit de leurs probabilités :

$$
P(A_1 \cap A_2 \cap \dots \cap A_n) = p_1 \times p_2 \times \dots \times p_n
$$

**L'idée.** Réussir deux étapes, c'est réussir la première, puis réussir la seconde sachant que la première a réussi. L'indépendance dit que ce « sachant que » ne change rien : on multiplie donc simplement par p₂. Une récurrence répète ce raisonnement étape par étape.

**La preuve, pas à pas.** Quatre étapes.

**Étape 1.** Par définition de la probabilité conditionnelle, P(A₂ | A₁) = P(A₁ ∩ A₂) / P(A₁) quand P(A₁) > 0. On multiplie les deux membres par P(A₁), parce qu'on veut isoler la probabilité de l'intersection :

$$
P(A_1 \cap A_2) = P(A_1) \times P(A_2 \mid A_1)
$$

Cette égalité reste vraie si P(A₁) = 0, parce que ses deux membres valent alors 0.

**Étape 2.** L'indépendance dit P(A₂ | A₁) = P(A₂) = p₂, parce que savoir que l'étape 1 a réussi ne change pas la chance de réussir l'étape 2. On remplace le facteur conditionnel :

$$
P(A_1 \cap A_2) = p_1 \times p_2
$$

**Étape 3.** On note Bₖ = A₁ ∩ … ∩ Aₖ. Alors Bₖ₊₁ = Bₖ ∩ Aₖ₊₁, et la règle de l'étape 1 donne la première égalité ci-dessous ; la seconde vient de ce que l'étape k + 1 est indépendante de l'**ensemble** des k premières (indépendance mutuelle, plus forte que l'indépendance deux à deux) :

$$
P(B_{k+1}) = P(B_k) \times P(A_{k+1} \mid B_k) = P(B_k) \times p_{k+1}
$$

**Étape 4.** On part de P(B₁) = p₁ et l'on applique l'étape 3 pour k = 1, 2, …, n − 1 : P(B₂) = p₁p₂, puis P(B₃) = p₁p₂p₃, et ainsi de suite jusqu'à P(Bₙ) = p₁p₂…pₙ. ∎

**Vérification chiffrée.** Deux étapes indépendantes fiables à 0,9 : 0,9 × 0,9 = 0,81. Contre-exemple quand l'indépendance manque : si les deux étapes échouent toujours ensemble, sur les mêmes 10 % de demandes (une question mal comprise fausse les deux), la chaîne réussit sur les 90 % restants et P = 0,90, pas 0,81. Si au contraire elles n'échouent jamais en même temps, la chaîne échoue sur 10 % + 10 % des demandes et P = 1 − 0,2 = 0,80. Les trois valeurs 0,80, 0,81 et 0,90 ont les mêmes p₁ et p₂ : seule la dépendance change.

**Ce que la preuve révèle du mécanisme.** Le produit n'est pas une règle générale : il vient de l'hypothèse d'indépendance, utilisée une fois à chaque étape de la récurrence. Sans elle, la formule exacte reste P(A₁) × P(A₂ | A₁) × P(A₃ | A₁ ∩ A₂) × …, avec des facteurs conditionnels qu'on ne connaît qu'en mesurant.

**Conséquence pour un agent.** Le produit sert à prévoir et à comparer des architectures avant de les construire. La fiabilité réelle se mesure de bout en bout, sur un jeu de cas, parce que les erreurs d'un agent sont souvent corrélées : une même question ambiguë fausse plusieurs étapes à la fois.

## Démonstration 2 — Une étape de plus ne peut que faire baisser la fiabilité

**Ce qu'on démontre.** Pour une chaîne de fiabilité P(Bₙ) et une étape supplémentaire indépendante de fiabilité pₙ₊₁ ∈ [0, 1] :

$$
P(B_{n+1}) = P(B_n) \times p_{n+1} \le P(B_n)
$$

avec égalité seulement si pₙ₊₁ = 1 ou P(Bₙ) = 0.

**L'idée.** Multiplier un nombre positif par un facteur au plus égal à 1 ne peut pas l'agrandir. Chaque étape retire la fraction εₙ₊₁ de ce qui restait.

**La preuve, pas à pas.** Trois étapes.

**Étape 1.** Par la démonstration 1, P(Bₙ₊₁) = P(Bₙ) × pₙ₊₁.

**Étape 2.** On calcule la perte, parce que comparer deux nombres revient à étudier le signe de leur différence ; on factorise par P(Bₙ) :

$$
P(B_n) - P(B_{n+1}) = P(B_n)\,(1 - p_{n+1}) = P(B_n)\,\varepsilon_{n+1}
$$

**Étape 3.** Les deux facteurs sont positifs ou nuls, parce que P(Bₙ) est une probabilité et que pₙ₊₁ ≤ 1. La perte est donc ≥ 0, et elle est nulle seulement si l'un des deux facteurs est nul. ∎

**Vérification chiffrée.** Après cinq étapes à 0,9, P = 0,59049 ; une sixième étape à 0,9 donne 0,59049 × 0,9 = 0,531441, soit une perte de 0,59049 × 0,1 = 0,059049. Une étape écrite en code pur et réellement sûre (pₙ₊₁ = 1) laisse 0,59049 inchangé : c'est le cas d'égalité.

**Ce que la preuve révèle du mécanisme.** La perte due à une étape vaut P(Bₙ) × εₙ₊₁ : elle est proportionnelle à ce qui reste. Une même étape coûte donc moins en valeur absolue en fin de chaîne qu'en début, mais elle coûte toujours la même fraction εₙ₊₁ de ce qui reste.

**Conséquence pour un agent.** Aucune étape où le modèle peut se tromper n'est gratuite. Fusionner deux outils en un, ou calculer en code ce qui n'a pas besoin du modèle, augmente la fiabilité sans changer de modèle (cas 3).

## Démonstration 3 — L'approximation « 1 moins la somme des erreurs »

**Ce qu'on démontre.** Pour des taux d'erreur εᵢ ∈ [0, 1] et n ≥ 1 :

$$
\prod_{i=1}^{n} (1 - \varepsilon_i) \ge 1 - \sum_{i=1}^{n} \varepsilon_i
$$

**L'idée.** En développant le produit de deux facteurs, on retrouve 1 − ε₁ − ε₂ plus un terme croisé ε₁ε₂ positif : le produit est au-dessus. On propage par récurrence en multipliant par des facteurs positifs, qui ne retournent pas l'inégalité.

**La preuve, pas à pas.** On note Sₖ = ε₁ + … + εₖ et l'on raisonne par récurrence sur k.

**Étape 1.** Pour k = 1, les deux membres valent 1 − ε₁ : l'inégalité est une égalité.

**Étape 2.** Pour k = 2, on développe, parce que le produit de deux binômes se distribue, puis on retire le terme ε₁ε₂ ≥ 0 :

$$
(1 - \varepsilon_1)(1 - \varepsilon_2) = 1 - \varepsilon_1 - \varepsilon_2 + \varepsilon_1 \varepsilon_2 \ge 1 - \varepsilon_1 - \varepsilon_2
$$

**Étape 3.** Hérédité. On suppose l'inégalité vraie au rang k. On multiplie ses deux membres par 1 − εₖ₊₁ ≥ 0, ce qui conserve le sens de l'inégalité parce que ce facteur est positif ou nul :

$$
\prod_{i=1}^{k+1} (1 - \varepsilon_i) \ge (1 - S_k)(1 - \varepsilon_{k+1}) = 1 - S_k - \varepsilon_{k+1} + S_k \, \varepsilon_{k+1}
$$

**Étape 4.** Le terme Sₖ εₖ₊₁ est positif ou nul, parce que c'est un produit de nombres positifs ; on le retire sans changer le sens de l'inégalité :

$$
1 - S_k - \varepsilon_{k+1} + S_k \, \varepsilon_{k+1} \ge 1 - S_{k+1}
$$

L'inégalité est donc vraie au rang k + 1, et par récurrence à tout rang. ∎

**Vérification chiffrée.** Deux étapes à 4 % et 3 % d'erreur : 0,96 × 0,97 = 0,9312 = 1 − 0,07 + 0,0012, au-dessus de la borne 0,93 d'exactement ε₁ε₂ = 0,0012. Pour l'agent KYC du cas 1, la somme des erreurs vaut 0,115 : la borne 0,885 est sous le produit exact 0,88994. Contre-exemple d'usage : avec 20 étapes à 0,9, la somme des erreurs vaut 2 et la borne vaut 1 − 2 = −1, vraie mais inutile, alors que le produit vaut 0,12158 ; c'est pourquoi le programme renvoie max(0, 1 − ∑εᵢ).

**Ce que la preuve révèle du mécanisme.** L'écart entre le produit et la borne est fait des termes croisés, de l'ordre du carré des erreurs : tant que les erreurs sont petites, ils sont négligeables et « les taux d'erreur s'additionnent ». Quand la somme des erreurs approche 1, la borne s'effondre et seul le produit renseigne. La leçon (point 6) démontre en plus, par l'inégalité de la réunion, que la borne max(0, 1 − ∑εᵢ) reste vraie même quand les étapes ne sont pas indépendantes.

**Conséquence pour un agent.** Pour estimer de tête une chaîne, on additionne les taux d'erreur : les six étapes du cas 1, de 0,5 % à 4 % d'erreur, font environ 11,5 % d'échecs. Comme la borne reste vraie quand les erreurs sont corrélées, c'est le plancher garanti qu'on peut annoncer au métier.

## Démonstration 4 — Combien d'étapes au plus, quelle fiabilité au moins

**Ce qu'on démontre.** Pour n étapes de même fiabilité p ∈ ]0, 1[ et une cible c ∈ ]0, 1[ :

$$
p^n \ge c \iff n \le \frac{\ln c}{\ln p}
$$

d'où le nombre maximal d'étapes et, à n fixé, la fiabilité minimale par étape :

$$
n_{\max} = \left\lfloor \frac{\ln c}{\ln p} \right\rfloor, \qquad p_{\min} = c^{1/n}
$$

**L'idée.** Le logarithme transforme la puissance pⁿ en produit n ln p, dans lequel on peut isoler n. Le seul piège est le signe : ln p est négatif, et diviser par un nombre négatif retourne l'inégalité.

**La preuve, pas à pas.** Quatre étapes.

**Étape 1.** La fonction ln est strictement croissante sur ]0, +∞[, donc elle conserve l'ordre ; et ln(pⁿ) = n ln p, parce que le logarithme d'une puissance est l'exposant fois le logarithme :

$$
p^n \ge c \iff n \ln p \ge \ln c
$$

**Étape 2.** Comme 0 < p < 1, ln p < 0. On divise par ln p, ce qui retourne le sens de l'inégalité parce que le diviseur est négatif :

$$
n \ln p \ge \ln c \iff n \le \frac{\ln c}{\ln p}
$$

Le quotient est positif, parce que ln c et ln p sont tous deux négatifs.

**Étape 3.** n est un entier : le plus grand entier inférieur ou égal au quotient est sa partie entière ⌊·⌋, d'où nₘₐₓ.

**Étape 4.** À n fixé, x ↦ xⁿ est strictement croissante sur [0, +∞[ et sa réciproque est la racine n-ième : pⁿ ≥ c équivaut à p ≥ c^(1/n), d'où pₘᵢₙ. ∎

**Vérification chiffrée.** Avec p = 0,98 et c = 0,9 : ln 0,9 = −0,10536 et ln 0,98 = −0,02020, quotient 5,215, donc nₘₐₓ = 5. Contrôle direct : 0,98⁵ = 0,90392 ≥ 0,9 et 0,98⁶ = 0,88584 < 0,9. Avec n = 10 et c = 0,95, pₘᵢₙ vaut :

$$
p_{\min} = 0{,}95^{1/10} = 0{,}99488
$$

Contre-exemple de l'étape 2 : qui oublie de retourner l'inégalité écrit n ≥ 5,215 et conclut qu'il faut « au moins 6 étapes », ce que 0,98⁶ = 0,88584 < 0,9 réfute (exercice 8).

**Ce que la preuve révèle du mécanisme.** Quand c et p sont proches de 1, ln c ≈ −(1 − c) et ln p ≈ −(1 − p), donc nₘₐₓ ≈ (1 − c)/(1 − p) : le budget d'erreur 1 − c se partage entre les étapes. Avec c = 0,9 et p = 0,98, (1 − 0,9)/(1 − 0,98) = 0,1/0,02 = 5, comme la formule exacte.

**Conséquence pour un agent.** Avant d'ajouter un outil, on vérifie qu'il reste du budget d'erreur : avec des étapes à 98 % et une cible de 90 %, la cinquième étape consomme le dernier crédit. Si le métier impose plus d'étapes, chacune doit atteindre pₘᵢₙ, par un schéma strict ou une validation avec relance.

## Démonstration 5 — Relancer une étape : 1 − (1 − p)ᴿ⁺¹

**Ce qu'on démontre.** Une étape de fiabilité p, dont l'échec est détecté par un contrôle sûr, relancée jusqu'à R fois avec des tentatives indépendantes, réussit avec la probabilité

$$
q = 1 - (1 - p)^{R+1}
$$

et q augmente strictement avec R quand 0 < p < 1.

**L'idée.** Avec les relances, l'étape n'échoue plus que si toutes ses tentatives échouent. On passe au complément : la probabilité d'un échec total est un produit de R + 1 facteurs égaux à 1 − p.

**La preuve, pas à pas.** Quatre étapes.

**Étape 1.** L'étape relancée échoue si et seulement si ses R + 1 tentatives échouent toutes, parce que le contrôle relance tant qu'il détecte un échec et qu'il reste des relances, et s'arrête au premier succès.

**Étape 2.** Les tentatives sont indépendantes et chacune échoue avec la probabilité 1 − p ; la démonstration 1, appliquée aux événements « la tentative t échoue », donne :

$$
P(\text{échec total}) = (1 - p)^{R+1}
$$

**Étape 3.** « L'étape réussit » est le complément de « échec total », et la probabilité d'un complément vaut 1 moins la probabilité de l'événement : q = 1 − (1 − p)ᴿ⁺¹.

**Étape 4.** Comme 0 < 1 − p < 1, la puissance (1 − p)ᴿ⁺¹ décroît strictement quand R augmente, parce qu'on la multiplie à chaque relance par un nombre < 1 ; donc q croît strictement et tend vers 1. ∎

**Vérification chiffrée.** La rédaction KYC à 0,96 relancée une fois : 1 − 0,04² = 1 − 0,0016 = 0,9984. Une étape à 0,9 relancée deux fois : 1 − 0,1³ = 0,999. Contre-exemple quand l'indépendance des tentatives manque : si la moitié des échecs de la rédaction sont permanents (un dossier incomplet échoue à chaque tentative), soit 0,02 d'échecs permanents et 0,02 d'échecs passagers, une relance laisse 0,02 + 0,02 × 0,04 = 0,0208 d'échecs et q = 0,9792 au lieu de 0,9984.

**Ce que la preuve révèle du mécanisme.** Une relance élève le taux d'erreur à la puissance R + 1 : 4 % devient 0,16 % avec une relance, puis 0,0064 % avec deux. Le gain le plus fort vient de la première relance ; les suivantes coûtent un appel de plus pour un gain de plus en plus petit.

**Conséquence pour un agent.** On ne relance une étape que si son échec est détectable par un contrôle automatique (schéma JSON, format d'Emirates ID, somme de contrôle d'un IBAN) et si ses échecs sont surtout passagers. Un échec permanent part en revue humaine, pas dans une boucle de relances (étape 11 du cours).

## Démonstration 6 — Sensibilité : 1 % sur une étape donne 1 % sur la chaîne

**Ce qu'on démontre.** Si la fiabilité pⱼ d'une étape est multipliée par 1 + r, la fiabilité de la chaîne est multipliée par 1 + r. Si l'on divise par deux le taux d'erreur εⱼ de cette étape, la chaîne est multipliée par

$$
\frac{1 - \varepsilon_j / 2}{1 - \varepsilon_j} = 1 + \frac{\varepsilon_j / 2}{1 - \varepsilon_j}
$$

facteur d'autant plus grand que εⱼ est grand.

**L'idée.** Dans un produit, chaque facteur agit en proportion : changer un facteur de r % change le produit de r %. Le gain d'une amélioration ne dépend que du facteur de changement de l'étape visée, et ce facteur est le plus grand sur l'étape la plus faible.

**La preuve, pas à pas.** Quatre étapes.

**Étape 1.** On isole l'étape j, parce que la multiplication est commutative et associative ; Qⱼ, produit des autres fiabilités, ne dépend pas de pⱼ :

$$
P = p_j \times Q_j, \qquad Q_j = \prod_{i \ne j} p_i
$$

**Étape 2.** On remplace pⱼ par pⱼ(1 + r) : la nouvelle fiabilité vaut pⱼ(1 + r)Qⱼ = P(1 + r), parce que le facteur 1 + r sort du produit.

**Étape 3.** On divise l'erreur par deux : pⱼ = 1 − εⱼ devient 1 − εⱼ/2. Le rapport des fiabilités est le rapport des deux facteurs de l'étape j, parce que Qⱼ se simplifie :

$$
\frac{P'}{P} = \frac{1 - \varepsilon_j/2}{1 - \varepsilon_j} = \frac{(1 - \varepsilon_j) + \varepsilon_j/2}{1 - \varepsilon_j} = 1 + \frac{\varepsilon_j/2}{1 - \varepsilon_j}
$$

**Étape 4.** Quand εⱼ augmente, le numérateur εⱼ/2 augmente et le dénominateur 1 − εⱼ diminue, donc la fraction augmente : le gain est maximal sur l'étape de plus grande erreur. ∎

**Vérification chiffrée.** Dans le cas 1, P = 0,88994. Si la rédaction passe de 0,96 à 0,96 × 1,01 = 0,9696, P devient 0,88994 × 1,01 = 0,89884. Diviser par deux l'erreur de la rédaction (4 % → 2 %) multiplie P par 1 + 0,02/0,96 = 1,02083 et donne 0,90848 ; diviser par deux l'erreur de la liste de sanctions (0,5 % → 0,25 %) multiplie P par 1 + 0,0025/0,995 = 1,00251 et ne donne que 0,89218.

**Ce que la preuve révèle du mécanisme.** La dérivée de P par rapport à pⱼ vaut Qⱼ = P/pⱼ : un point de fiabilité gagné vaut presque la même chose sur n'importe quelle étape, mais il y a beaucoup plus de points à gagner sur une étape à 96 % que sur une étape à 99,5 %.

**Conséquence pour un agent.** On investit d'abord sur le maillon le plus faible (prompt plus précis, schéma strict, relance) : c'est ce que fait le cas 1 en relançant la rédaction plutôt qu'en améliorant la liste de sanctions.

## Exemple simple, à la main

Cinq étapes fiables à 90 %. On calcule la puissance par carrés successifs, ce qui se fait au crayon :

$$
0{,}9^2 = 0{,}81, \qquad 0{,}9^4 = 0{,}81^2 = 0{,}6561
$$

$$
0{,}9^5 = 0{,}9^4 \times 0{,}9 = 0{,}6561 \times 0{,}9 = 0{,}59049
$$

L'agent échoue donc dans 1 − 0,59049 = 0,40951 des cas, environ 41 demandes sur 100. La borne de la démonstration 3 donne 1 − 5 × 0,1 = 0,5, bien sous 0,59049 : les erreurs sont trop grandes pour que « les erreurs s'additionnent » soit précis.

Cinq étapes fiables à 99 % :

$$
0{,}99^2 = 0{,}9801, \qquad 0{,}99^4 = 0{,}9801^2 = 0{,}96059601
$$

$$
0{,}99^5 = 0{,}96059601 \times 0{,}99 = 0{,}9509900499 \approx 0{,}95099
$$

La borne vaut 1 − 5 × 0,01 = 0,95, à 0,00099 du produit : quand les erreurs sont petites, la règle de tête colle au calcul exact. Passer de 90 % à 99 % par étape fait passer l'agent de 59 % à 95 %.

## Cas d'usage complexes, démontrés

### Cas 1 — Banque de détail à Dubaï : un agent KYC en six étapes

**Contexte.** Une banque de détail de Dubaï confie à un agent la pré-vérification KYC des demandes d'ouverture de compte déposées dans son application, en arabe ou en anglais. L'agent enchaîne six étapes : lire la pièce d'identité, extraire le numéro d'Emirates ID, vérifier son format (15 chiffres commençant par 784), interroger la liste de sanctions, comparer le nom translittéré à celui de la pièce, rédiger l'avis pour l'analyste. La question : l'agent tient-il la cible de 90 % de dossiers justes de bout en bout, et sinon quelle étape renforcer ? Le volume, les fiabilités et les coûts sont illustratifs.

**Données.**

| Donnée | Valeur |
| --- | --- |
| Fiabilités des six étapes | 0,99 ; 0,98 ; 0,97 ; 0,995 ; 0,99 ; 0,96 |
| Volume mensuel | 10 000 dossiers |
| Cible de bout en bout | 0,90 |
| Coût d'un dossier faux repris par un analyste | 45 AED |
| Coût d'une relance de la rédaction (un appel au modèle) | 0,12 AED |

**Calcul pas à pas.** Fiabilités arrondies à 8 puis 5 décimales, dossiers à l'unité.

**Étape 1.** Produits partiels, étape après étape :

$$
0{,}99 \times 0{,}98 = 0{,}9702, \qquad 0{,}9702 \times 0{,}97 = 0{,}941094, \qquad 0{,}941094 \times 0{,}995 = 0{,}93638853
$$

$$
0{,}93638853 \times 0{,}99 = 0{,}92702464, \qquad 0{,}92702464 \times 0{,}96 = 0{,}88994366 \approx 0{,}88994
$$

**Étape 2.** Borne de contrôle : la somme des erreurs vaut 0,01 + 0,02 + 0,03 + 0,005 + 0,01 + 0,04 = 0,115, donc

$$
1 - 0{,}115 = 0{,}885 \le 0{,}88994
$$

**Étape 3.** Dossiers faux et coût mensuel :

$$
10\,000 \times (1 - 0{,}88994) = 1\,100{,}6 \approx 1\,101, \qquad 1\,101 \times 45 = 49\,545 \text{ AED}
$$

**Étape 4.** 0,88994 < 0,90 : la cible n'est pas tenue. L'étape la plus faible est la rédaction (démonstration 6). Une relance quand le contrôle automatique rejette l'avis donne 1 − 0,04² = 0,9984 (démonstration 5), et :

$$
0{,}92702464 \times 0{,}9984 = 0{,}92554141 \approx 0{,}92554
$$

**Étape 5.** Nouveaux dossiers faux et coût, relances comprises ; il y a au plus 10 000 × 0,04 = 400 relances par mois :

$$
10\,000 \times (1 - 0{,}92554) = 744{,}6 \approx 745, \qquad 745 \times 45 = 33\,525 \text{ AED}, \qquad 400 \times 0{,}12 = 48 \text{ AED}
$$

**Décision de l'agent.** Avec la relance, 0,92554 ≥ 0,90 : la configuration est acceptée. Elle retire 1 101 − 745 = 356 dossiers faux par mois et économise 49 545 − 33 525 − 48 = 15 972 AED par mois, pour 48 AED de relances.

**Contre-calcul.** La variante naïve prend la moyenne des fiabilités, (0,99 + 0,98 + 0,97 + 0,995 + 0,99 + 0,96) / 6 = 5,885 / 6 = 0,98083, et annonce environ 10 000 × (1 − 0,98083) = 192 dossiers faux. La réalité en compte 1 101 : l'équipe sous-dimensionnerait la revue humaine de 1 101 − 192 = 909 dossiers par mois, soit 909 × 45 = 40 905 AED de travail non prévu chaque mois.

**Sensibilité.** Sans relance, quelle fiabilité de rédaction tiendrait la cible ? Il faut 0,92702464 × p₆ ≥ 0,90, donc :

$$
p_6 \ge \frac{0{,}90}{0{,}92702464} = 0{,}97085
$$

La valeur de bascule est 97,085 % : si un meilleur prompt fait passer la rédaction au-dessus, la relance devient superflue ; en dessous, elle est indispensable.

**En production.** On suit le taux de dossiers repris par l'analyste, mesuré de bout en bout et non étape par étape : valeur attendue 1 − 0,92554 = 7,4 %, alerte au-dessus de 10 %, le seuil où la cible de 90 % n'est plus tenue. On suit à part le taux de relances, attendu à 4 % : s'il monte, la rédaction se dégrade avant que le taux final ne bouge. La décision d'ouvrir le compte reste à l'analyste ; les exigences KYC et de lutte anti-blanchiment relèvent de la CBUAE, à confirmer avec le texte en vigueur.

### Cas 2 — Plateforme d'actifs virtuels agréée VARA : 288 cycles de surveillance par jour

**Contexte.** Une plateforme d'actifs virtuels agréée par la VARA fait tourner un agent de surveillance de liquidité toutes les 5 minutes, soit 288 cycles par jour. Chaque cycle enchaîne trois étapes : lire la profondeur du carnet d'ordres, la comparer au seuil fixé par l'équipe risques, décider d'alerter ou non. L'équipe risques fixe l'objectif d'au plus 1 cycle raté par semaine, parce qu'un cycle raté est un trou de 5 minutes dans la surveillance. Les fiabilités, la durée d'une relance et l'objectif sont illustratifs.

**Données.**

| Donnée | Valeur |
| --- | --- |
| Étapes par cycle | 3 |
| Fiabilité de chaque étape | 0,995 |
| Cycles par jour | 288 (un toutes les 5 minutes) |
| Cycles par semaine | 288 × 7 = 2 016 |
| Objectif | au plus 1 cycle raté par semaine |
| Relance autorisée | 1 par étape, en moins de 20 secondes |

**Calcul pas à pas.** Fiabilités arrondies à 6 décimales, nombres de cycles à 2 décimales.

**Étape 1.** Fiabilité d'un cycle sans relance :

$$
0{,}995^3 = 0{,}990025 \times 0{,}995 = 0{,}985075
$$

**Étape 2.** Cycles ratés attendus ; l'espérance d'un nombre d'échecs est le nombre d'essais fois la probabilité d'échec :

$$
288 \times (1 - 0{,}985075) = 4{,}30 \text{ par jour}, \qquad 2\,016 \times 0{,}014925 = 30{,}09 \text{ par semaine}
$$

La probabilité qu'une journée entière se passe sans aucun cycle raté vaut 0,985075²⁸⁸ = 0,995⁸⁶⁴ = 0,0132, soit 1,32 % : un trou de surveillance est quasi certain chaque jour.

**Étape 3.** Avec une relance par étape (démonstration 5) :

$$
q = 1 - 0{,}005^2 = 0{,}999975, \qquad q^3 = 0{,}999925
$$

**Étape 4.** Cycles ratés attendus avec relance :

$$
2\,016 \times (1 - 0{,}999925) = 0{,}15 \text{ par semaine}, \qquad 288 \times (1 - 0{,}999925) = 0{,}02 \text{ par jour}
$$

**Décision de l'agent.** Sans relance, 30,09 cycles ratés par semaine pour un objectif de 1 : configuration refusée. Avec une relance par étape, 0,15 par semaine : configuration retenue. La relance ajoute au plus 20 secondes à un cycle de 300 secondes et ne décale jamais le cycle suivant.

**Contre-calcul.** L'erreur classique lit « fiable à 99,5 % » comme la fiabilité du cycle : elle annonce 288 × 0,005 = 1,44 cycle raté par jour, trois fois moins que les 4,30 réels, parce qu'elle oublie que le cycle a trois étapes. Pire, l'équipe qui croit « 99,5 %, donc presque jamais » ne prévoit aucune alerte sur l'agent lui-même et découvre les trous de surveillance pendant un incident de liquidité.

**Sensibilité.** Valeur de bascule sans relance : il faudrait 2 016 × (1 − p³) ≤ 1, donc

$$
p \ge \left(1 - \frac{1}{2\,016}\right)^{1/3} = 0{,}999835
$$

soit 99,98 % par étape, irréaliste pour une étape qui appelle un service externe. Avec une relance, il faut seulement 1 − (1 − p)² ≥ 0,999835, donc

$$
p \ge 1 - \sqrt{1 - 0{,}999835} = 0{,}98714
$$

La configuration avec relance tient l'objectif tant que chaque étape reste au-dessus de 98,71 %, une marge confortable sous les 99,5 % mesurés.

**En production.** On compte chaque jour les cycles terminés autrement qu'en statut « fini » : valeur attendue 0,02 par jour, alerte dès 1 cycle raté dans la journée, parce qu'à ce niveau l'hypothèse d'échecs passagers ne tient plus et la relance ne joue plus son rôle. On suit aussi le délai entre une chute de profondeur et l'alerte. Les obligations de surveillance et de journalisation de la plateforme relèvent de la VARA, à confirmer avec le texte en vigueur.

### Cas 3 — Cabinet RH multi-émirats : combien d'étapes confier au modèle pour la fin de service

**Contexte.** Un cabinet RH présent dans plusieurs émirats prépare chaque mois 1 200 soldes de tout compte de salariés du secteur privé (volume illustratif). La première version de l'agent confie cinq étapes au modèle : lire le contrat, vérifier le périmètre (un ressortissant émirien relève de la GPSSA, un salarié du DIFC du régime DEWS), calculer l'ancienneté, appliquer le barème de fin de service, rédiger le solde. Le cabinet vise 95 % de soldes justes de bout en bout. La question : combien d'étapes le modèle peut-il garder, et lesquelles passer en code ?

**Données.**

| Donnée | Valeur |
| --- | --- |
| Fiabilité d'une étape faite par le modèle | 0,98 (illustratif) |
| Fiabilité d'une étape faite par du code testé | 0,9999 (illustratif) |
| Cible de bout en bout | 0,95 |
| Volume | 1 200 soldes par mois |
| Dossier exemple | salaire de base 12 000 AED, 7 ans de service, démission |
| Barème (décret-loi fédéral 33/2021) | 21 jours de salaire de base par an les 5 premières années, 30 jours au-delà ; salaire journalier = base / 30 ; plafond 24 mois de salaire de base ; pas de réduction pour démission |

**Calcul pas à pas.** Fiabilités arrondies à 5 décimales, soldes à l'unité.

**Étape 1.** Le montant juste du dossier exemple, pour savoir ce que coûte une erreur. Le salaire journalier vaut 12 000 / 30 = 400 AED et les jours dus 5 × 21 + 2 × 30 = 105 + 60 = 165 :

$$
\text{indemnité} = 165 \times 400 = 66\,000 \text{ AED} \le 24 \times 12\,000 = 288\,000 \text{ AED}
$$

**Étape 2.** Fiabilité de la première version, cinq étapes du modèle :

$$
0{,}98^5 = 0{,}90392, \qquad 1\,200 \times (1 - 0{,}90392) = 115{,}3 \approx 115 \text{ soldes faux par mois}
$$

**Étape 3.** Budget d'étapes (démonstration 4) :

$$
n_{\max} = \left\lfloor \frac{\ln 0{,}95}{\ln 0{,}98} \right\rfloor = \left\lfloor \frac{-0{,}051293}{-0{,}020203} \right\rfloor = \lfloor 2{,}5389 \rfloor = 2
$$

**Étape 4.** Deuxième version : le modèle garde les deux étapes de langage (lire le contrat, rédiger le solde) et les trois étapes de règles (périmètre, ancienneté, barème) passent dans un outil en code :

$$
0{,}98^2 \times 0{,}9999^3 = 0{,}9604 \times 0{,}99970003 = 0{,}96011, \qquad 1\,200 \times (1 - 0{,}96011) = 47{,}9 \approx 48
$$

**Décision de l'agent.** 0,96011 ≥ 0,95 : la deuxième version est retenue, avec 115 − 48 = 67 soldes faux de moins par mois. La première version, à 0,90392, est refusée.

**Contre-calcul.** L'intuition « chaque étape est fiable à 98 %, donc l'agent aussi » annonce 1 200 × 0,02 = 24 soldes faux, environ cinq fois moins que les 115 réels. Une erreur typique d'un modèle qui « calcule » le barème : appliquer 30 jours dès la première année, soit 7 × 30 = 210 jours × 400 = 84 000 AED au lieu de 66 000 AED, donc 18 000 AED versés en trop sur un seul dossier, difficiles à récupérer une fois payés.

**Sensibilité.** Pour rendre au modèle une troisième étape (l'ancienneté), avec les deux étapes de règles restantes en code, il faudrait p³ × 0,9999² ≥ 0,95, donc :

$$
p \ge \left(\frac{0{,}95}{0{,}9998}\right)^{1/3} = 0{,}98311
$$

La valeur de bascule est 98,311 %, à peine au-dessus du pₘᵢₙ sans étape en code, 0,95^(1/3) = 0,98305. Tant que la fiabilité mesurée du modèle reste sous ce seuil, l'ancienneté reste en code.

**En production.** On suit la part des soldes corrigés par le service paie avant paiement : valeur attendue 1 − 0,96011 = 4 %, alerte au-dessus de 5 %, c'est-à-dire dès que la cible n'est plus tenue. Le paiement passe par le WPS après validation humaine, jamais par l'agent ; l'outil applique le barème du décret-loi fédéral 33/2021 et refuse lui-même les dossiers hors périmètre (GPSSA, DEWS du DIFC).

### Cas 4 — Entité de services publics en ligne : faut-il ajouter une étape de confirmation ?

**Contexte.** Une entité de services publics en ligne, accessible par UAE Pass, traite 50 000 demandes par mois en arabe, en anglais ou dans un mélange des deux. Son agent enchaîne cinq étapes : normaliser le texte arabe (formes de l'alef, ta marbuta, diacritiques), identifier la procédure demandée, extraire les champs du formulaire, vérifier la pièce jointe, rédiger la réponse bilingue. L'équipe produit propose d'ajouter une étape : l'agent affiche la procédure identifiée et l'usager la confirme d'un clic. La démonstration 2 dit qu'une étape de plus fait baisser la fiabilité, sauf si elle en améliore une autre : c'est ce qu'il faut chiffrer. Volumes, fiabilités et coûts sont illustratifs.

**Données.**

| Étape | Version A (sans confirmation) | Version B (avec confirmation) |
| --- | --- | --- |
| Normaliser l'arabe | 0,99 | 0,99 |
| Identifier la procédure | 0,96 | 0,995 (confirmée par l'usager) |
| Afficher la confirmation | absente | 0,999 |
| Extraire les champs | 0,97 | 0,97 |
| Vérifier la pièce | 0,98 | 0,98 |
| Rédiger la réponse | 0,985 | 0,985 |
| Usagers qui abandonnent à la confirmation | 0 % | 3 % |

Une demande échouée coûte 25 AED (rappel par le centre de contact) et un abandon 15 AED (l'usager revient par un autre canal).

**Calcul pas à pas.** Fiabilités arrondies à 6 décimales, coûts par demande à 4 décimales, coûts mensuels à l'unité.

**Étape 1.** Version A, produits partiels :

$$
0{,}99 \times 0{,}96 = 0{,}9504, \quad \times 0{,}97 = 0{,}921888, \quad \times 0{,}98 = 0{,}90345, \quad \times 0{,}985 = 0{,}889898
$$

**Étape 2.** Version B, produits partiels :

$$
0{,}99 \times 0{,}995 = 0{,}98505, \quad \times 0{,}999 = 0{,}984065, \quad \times 0{,}97 = 0{,}954543, \quad \times 0{,}98 = 0{,}935452, \quad \times 0{,}985 = 0{,}92142
$$

**Étape 3.** Coût moyen par demande. En A, toutes les demandes passent la chaîne :

$$
c_A = (1 - 0{,}889898) \times 25 = 2{,}7525 \text{ AED}
$$

En B, 3 % des usagers abandonnent et les 97 % restants passent la chaîne :

$$
c_B = 0{,}03 \times 15 + 0{,}97 \times (1 - 0{,}92142) \times 25 = 0{,}45 + 1{,}9056 = 2{,}3556 \text{ AED}
$$

**Étape 4.** Sur le mois, avec les valeurs non arrondies : 50 000 × cₐ = 137 627 AED en A et 50 000 × c_B = 117 778 AED en B. Demandes abouties : 50 000 × 0,889898 = 44 495 en A, et 48 500 × 0,92142 = 44 689 en B, abandons déduits.

**Décision de l'agent.** c_B < cₐ et B fait aboutir plus de demandes, même après les abandons : la confirmation est ajoutée.

**Contre-calcul.** Le raisonnement naïf « une étape de plus fait toujours baisser la fiabilité » ne regarde que l'étape ajoutée : 0,889898 × 0,999 = 0,889009 < 0,889898, et il rejette la confirmation. Il oublie que la confirmation fait passer l'identification de 0,96 à 0,995 ; ce refus coûterait à l'entité 137 627 − 117 778 = 19 849 AED par mois.

**Sensibilité.** Valeur de bascule du taux d'abandon a : B reste préférable tant que

$$
15\,a + 25\,(1 - a)(1 - 0{,}92142) < 2{,}7525
$$

On pose k = 25 × (1 − 0,92142) = 1,9645 ; l'inégalité devient 15a + k − ka < 2,7525, donc :

$$
a < \frac{2{,}7525 - 1{,}9645}{15 - 1{,}9645} = 0{,}0605
$$

Jusqu'à 6,05 % d'abandons, la confirmation reste gagnante ; au-delà, il faut la réserver aux demandes où l'identification hésite.

**En production.** On suit le taux d'abandon à l'écran de confirmation (attendu 3 %, alerte au-dessus de 5 %, avant la bascule de 6,05 %) et la part des demandes abouties sans appel au centre de contact. Les journaux de l'agent ne gardent que les données nécessaires ; le régime de protection des données applicable à l'entité (PDPL, décret-loi fédéral 45/2021, ou texte propre au secteur public) est à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Calculer à la main 0,95⁴.

**Exercice 2.** Un agent a des étapes fiables à 98 %. Combien d'étapes au plus peut-il enchaîner en gardant 90 % de réussite ? (On donne ln 0,9 ≈ −0,10536 et ln 0,98 ≈ −0,02020.)

**Exercice 3.** Quelle fiabilité minimale par étape faut-il pour réussir 95 % du temps avec 10 étapes ? (On donne ln 0,95 ≈ −0,051293.)

**Exercice 4.** Trois étapes ont des taux d'erreur 2 %, 3 % et 5 %. Comparer la fiabilité exacte et la borne « 1 moins la somme ».

**Exercice 5.** Une étape fiable à 90 % est tentée jusqu'à 3 fois (une tentative puis 2 relances), avec des tentatives indépendantes. Quelle est sa fiabilité ?

**Exercice 6.** Démontrer, sans regarder la démonstration 3, l'inégalité pour trois étapes.

**Exercice 7.** Dans le cas 1, un nouveau modèle de cartes d'identité fait tomber l'extraction de l'Emirates ID de 0,98 à 0,95. La rédaction reste relancée une fois (0,9984). Calculer la nouvelle fiabilité, dire si la cible de 0,90 est tenue, puis calculer l'effet d'une relance de l'extraction.

**Exercice 8.** Trouver l'erreur. Un collègue écrit : « 0,98ⁿ ≥ 0,9 ⟺ n ln 0,98 ≥ ln 0,9 ⟺ n ≥ ln 0,9 / ln 0,98 = 5,215, donc il faut au moins 6 étapes pour tenir 90 %. » Corriger la conclusion et la vérifier par un calcul direct.

**Exercice 9.** Redémontrer de mémoire la démonstration 5 : une étape de fiabilité p relancée jusqu'à R fois réussit avec la probabilité 1 − (1 − p)ᴿ⁺¹. L'appliquer à p = 0,8 et R = 2, puis dire quelle hypothèse le cas 2 doit vérifier pour pouvoir l'utiliser.

## Corrigé

**Exercice 1.** On élève au carré deux fois. 0,95² = 0,9025. Puis 0,9025² = 0,9025 × 0,9 + 0,9025 × 0,0025 = 0,81225 + 0,00225625 = 0,81450625.

**Exercice 2.** On veut 0,98ⁿ ≥ 0,9, donc n ln 0,98 ≥ ln 0,9. On divise par ln 0,98 < 0, ce qui retourne l'inégalité : n ≤ −0,10536 / −0,02020 ≈ 5,215. La partie entière donne nₘₐₓ = 5. Contrôle : 0,98⁵ = 0,90392 ≥ 0,9 et 0,98⁶ = 0,88584 < 0,9.

**Exercice 3.** pₘᵢₙ = 0,95^(1/10). On passe par le logarithme : ln 0,95 / 10 = −0,0051293, puis e⁻⁰,⁰⁰⁵¹²⁹³ = 0,99488. Il faut 99,49 % par étape.

**Exercice 4.** Exact : 0,98 × 0,97 = 0,9506, puis 0,9506 × 0,95 = 0,90307. Borne : 1 − (0,02 + 0,03 + 0,05) = 1 − 0,10 = 0,90. La borne est en dessous, comme prévu, avec un écart de 0,00307 fait des termes croisés.

**Exercice 5.** Trois tentatives, c'est R = 2 relances. L'étape échoue seulement si les trois tentatives échouent : 0,1³ = 0,001, donc 1 − 0,001 = 0,999.

**Exercice 6.** On note a, b, c les trois taux d'erreur, dans [0, 1]. Étape 1 : (1 − a)(1 − b) = 1 − a − b + ab ≥ 1 − a − b, parce que ab ≥ 0. Étape 2 : on multiplie par 1 − c ≥ 0, ce qui garde le sens : (1 − a)(1 − b)(1 − c) ≥ (1 − a − b)(1 − c). Étape 3 : on développe, (1 − a − b)(1 − c) = 1 − a − b − c + (a + b)c. Étape 4 : (a + b)c ≥ 0, donc le tout est ≥ 1 − a − b − c. Contrôle avec l'exercice 4 : 0,90307 ≥ 0,90.

**Exercice 7.** Produits partiels : 0,99 × 0,95 = 0,9405 ; × 0,97 = 0,912285 ; × 0,995 = 0,907724 ; × 0,99 = 0,898646 ; × 0,9984 = 0,897209. La fiabilité vaut 0,89721 < 0,90 : la décision change, la configuration n'est plus acceptée. On relance aussi l'extraction, dont l'échec se détecte par le contrôle de format (15 chiffres commençant par 784) : 1 − 0,05² = 0,9975, et la fiabilité devient 0,897209 × 0,9975 / 0,95 = 0,94207 ≥ 0,90. La cible est de nouveau tenue.

**Exercice 8.** L'erreur est à la deuxième équivalence : ln 0,98 est négatif, et diviser par un nombre négatif retourne l'inégalité. La bonne conclusion est n ≤ 5,215, donc au plus 5 étapes. Calcul direct : 0,98⁵ = 0,90392 tient la cible, alors que 0,98⁶ = 0,88584 ne la tient pas, ce qui contredit « au moins 6 ».

**Exercice 9.** Étape 1 : l'étape échoue seulement si ses R + 1 tentatives échouent, parce que le contrôle relance tant qu'il détecte un échec. Étape 2 : les tentatives étant indépendantes, la probabilité de ces R + 1 échecs est (1 − p)ᴿ⁺¹. Étape 3 : on prend le complément. Application : 1 − 0,2³ = 1 − 0,008 = 0,992. Le cas 2 doit vérifier que les échecs d'une étape sont détectés (statut autre que « fini ») et surtout passagers (un service momentanément indisponible), sinon la relance échoue de la même façon et la formule surestime q.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`fiabilite(probas)`** — Cette fonction est le contrôleur qualité posté au bout d'une chaîne de montage, qui sait qu'une pièce ne sort bonne que si chaque poste l'a bien traitée : elle reçoit la liste des fiabilités des étapes, vérifie d'abord que la liste n'est pas vide et que chaque valeur tient dans l'intervalle [0, 1], et lève sinon une `ValueError` avec le message « au moins une étape, chaque p dans [0, 1] ». Si tout est en règle, elle multiplie toutes les fiabilités entre elles avec `math.prod` et renvoie ce produit p₁ × p₂ × … × pₙ, la probabilité que l'agent réussisse de bout en bout, par exemple 0,59049 pour cinq étapes à 0,9 ; les autres fonctions l'appellent aussi comme simple garde, pour valider leurs entrées.

**`borne(probas)`** — Celle-ci joue le rôle du comptable prudent qui, faute de savoir si les pannes arrivent ensemble ou séparément, additionne simplement tous les risques : elle reçoit la même liste de fiabilités, la fait valider par `fiabilite` sans garder le résultat, puis calcule 1 moins la somme des taux d'erreur 1 − pᵢ. Comme cette somme peut dépasser 1 quand les étapes sont nombreuses, elle coupe le résultat à 0 avec `max`, et elle renvoie ce plancher garanti, vrai même quand les erreurs sont corrélées : 0,885 pour les six étapes du cas 1, sous le produit exact de 0,88994, et 0 pour vingt étapes à 0,9, là où la formule brute donnerait −1.

**`produits_partiels(probas)`** — Cette fonction tourne le film de la chaîne image par image, comme un greffier qui note après chaque guichet la part des dossiers encore intacts : après avoir validé la liste par `fiabilite`, elle part d'un accumulateur égal à 1, le multiplie successivement par chaque fiabilité et range chaque résultat intermédiaire dans une liste. Elle renvoie cette liste des fiabilités acquises après chaque étape, par exemple 0,99 puis 0,9702 puis 0,941094 pour trois étapes à 0,99, 0,98 et 0,97, et c'est elle qui permet au cas 1 de récupérer la fiabilité des cinq premières étapes, 0,92702464, avant de remplacer la sixième par sa version relancée.

**`avec_relances(p, relances)`** — Ici l'on suit un livreur têtu qui sonne à nouveau tant que personne n'a ouvert, dans la limite du nombre de passages permis : la fonction reçoit la fiabilité p d'une seule tentative et le nombre R de relances autorisées, refuse par une `ValueError` une probabilité hors de [0, 1] ou un nombre de relances négatif, puis calcule la probabilité que les R + 1 tentatives n'échouent pas toutes, soit 1 − (1 − p)ᴿ⁺¹. Elle renvoie la fiabilité de l'étape relancée, 0,9984 pour 0,96 relancée une fois, 0,999 pour 0,9 relancée deux fois et 0,992 pour 0,8 relancée deux fois, et sert à chiffrer le remède proposé dans les cas 1 et 2 ainsi que dans les exercices.

**`etapes_max(p, cible)`** — Cette fonction est l'architecte qui demande combien d'étages on peut empiler avant que la tour ne passe sous la hauteur minimale de sécurité : elle reçoit une fiabilité commune p et une cible, toutes deux strictement entre 0 et 1 sous peine de `ValueError`, et prend d'abord la partie entière du quotient ln(cible) / ln(p). Comme ce quotient calculé en flottants peut tomber juste sous un entier, deux boucles de garde corrigent ensuite le résultat par un contrôle direct, en montant tant que pⁿ⁺¹ tient encore la cible et en descendant tant que pⁿ ne la tient plus ; elle renvoie ce plus grand nombre d'étapes, 5 pour p = 0,98 et une cible de 0,9, puis 2 pour une cible de 0,95 dans le cas 3.

**`p_min_par_etape(n, cible)`** — Celle-ci prend le problème à l'envers, comme un chef de chantier qui connaît le nombre de corps de métier et veut savoir quel niveau exiger de chacun : elle reçoit le nombre d'étapes n, au moins 1, et la cible, strictement entre 0 et 1, lève une `ValueError` sinon, et renvoie la racine n-ième de la cible, cible^(1/n). Cette valeur est la plus petite fiabilité commune qui garantit encore pⁿ ≥ cible : 0,99488 pour dix étapes et une cible de 0,95, et 0,98305 pour trois étapes à la même cible, le seuil que le cas 3 compare à sa valeur de bascule.

**`cas_1_kyc_banque()`** — Cette fonction met en scène la banque de détail dont l'agent pré-vérifie les ouvertures de compte en six étapes de fiabilités 0,99, 0,98, 0,97, 0,995, 0,99 et 0,96, sur 10 000 dossiers par mois, avec une cible de 0,90, 45 AED par dossier faux et 0,12 AED par relance. Elle calcule les produits partiels, trouve une fiabilité finale de 0,88994 et 1 101 dossiers faux, relance une fois la rédaction pour la porter à 0,9984, ce qui donne 0,92554 et 745 dossiers faux pour 400 relances, puis compare avec la moyenne naïve de 0,98083 qui n'annoncerait que 192 erreurs et calcule la bascule 0,90 / 0,92702464 = 0,97085. Elle imprime deux lignes de bilan, retient la décision « accepter avec relance » et renvoie un dictionnaire de toutes ces grandeurs, dont l'économie de 15 972 AED, que `main` vérifie ensuite une à une.

**`cas_2_surveillance_crypto()`** — On y suit une sentinelle qui fait sa ronde 288 fois par jour sur une plateforme d'actifs virtuels, chaque ronde comptant trois étapes fiables à 0,995, avec pour consigne de ne pas manquer plus d'une ronde par semaine de 2 016 cycles. La fonction calcule la fiabilité d'un cycle, 0,985075, les 4,30 cycles ratés par jour et 30,09 par semaine, la probabilité 0,0132 d'une journée parfaite, puis la même chose avec une relance par étape, qui porte chaque étape à 0,999975 et le cycle à 0,999925, soit 0,15 raté par semaine. Elle ajoute la lecture naïve à 1,44 raté par jour et les deux valeurs de bascule, 0,999835 sans relance et 0,98714 avec, imprime trois lignes, choisit « 1 relance par étape » et renvoie le dictionnaire de ces valeurs.

**`cas_3_fin_de_service_rh()`** — Cette fonction raconte le cabinet RH qui hésite entre confier cinq étapes au modèle, fiable à 0,98, ou en basculer trois dans du code testé, fiable à 0,9999, pour 1 200 soldes de tout compte par mois et une cible de 0,95. Elle calcule d'abord l'indemnité juste du dossier exemple, 400 AED par jour sur 165 jours, soit 66 000 AED sous le plafond de 24 mois, puis la fiabilité de la première version, 0,90392 et 115 soldes faux, le budget d'étapes n_max = 2 tiré du quotient 2,5389, et la deuxième version, 0,96011 et 48 soldes faux. Elle chiffre encore l'intuition naïve de 24 erreurs, l'erreur de barème de 18 000 AED et la bascule 0,98311 face au pₘᵢₙ de 0,98305, imprime trois lignes, choisit « version 2 » et renvoie le dictionnaire complet.

**`cas_4_guichet_public()`** — Ici l'on assiste au débat d'une équipe produit d'un guichet public en ligne qui se demande si l'ajout d'un clic de confirmation vaut l'abandon de 3 % des usagers : la fonction compare la version A à cinq étapes et la version B à six, où l'identification passe de 0,96 à 0,995, sur 50 000 demandes, avec 25 AED par échec et 15 AED par abandon. Elle obtient 0,889898 contre 0,92142 de fiabilité, un coût par demande de 2,7525 contre 2,3556 AED, soit 137 627 contre 117 778 AED par mois, et 44 495 contre 44 689 demandes abouties, puis calcule le raisonnement naïf 0,889009, la constante k = 1,9645 et le taux d'abandon de bascule 0,0605. Elle imprime trois lignes, conclut « ajouter la confirmation » et renvoie toutes ces grandeurs dans un dictionnaire.

**`main()`** — C'est l'inspecteur général qui repasse derrière chaque démonstration de la fiche, une calculette à la main : il tourne d'abord le film de trois étapes, avec ses pertes et la somme des logarithmes −0,060712, refait l'exemple simple 0,9⁵ = 0,59049 et 0,99⁵ = 0,95099, puis vérifie une à une les démonstrations 1 à 6, de la borne coupée à 0 pour vingt étapes jusqu'à la sensibilité de la rédaction. Il appelle ensuite les quatre cas et confronte chaque valeur de leurs dictionnaires à des `assert`, rejoue les neuf exercices du corrigé, y compris une triple boucle sur a, b et c qui teste l'inégalité de l'exercice 6, et s'assure que `fiabilite` refuse bien les listes `[]`, `[1.2]` et `[-0.1]`. Il n'imprime « OK — toutes les vérifications sont passées. » que si aucune assertion n'a échoué.

```python
"""Démonstration 29 — fiabilité en série : produit, bornes, n_max, p_min, relances, sensibilité, quatre cas aux EAU."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def fiabilite(probas: list[float]) -> float:
    """P(succès) = p₁ × p₂ × … × pₙ, pour des étapes indépendantes et toutes nécessaires."""
    if not probas or any(not 0.0 <= p <= 1.0 for p in probas):
        raise ValueError("au moins une étape, chaque p dans [0, 1]")
    return math.prod(probas)


def borne(probas: list[float]) -> float:
    """Borne basse max(0, 1 − Σ εᵢ), vraie même quand les erreurs sont corrélées."""
    fiabilite(probas)
    return max(0.0, 1.0 - sum(1.0 - p for p in probas))


def produits_partiels(probas: list[float]) -> list[float]:
    """Fiabilité acquise après chaque étape : p₁, p₁p₂, p₁p₂p₃…"""
    fiabilite(probas)
    partiels, acc = [], 1.0
    for p in probas:
        acc *= p
        partiels.append(acc)
    return partiels


def avec_relances(p: float, relances: int) -> float:
    """Étape relancée jusqu'à R fois, tentatives indépendantes : 1 − (1 − p)^(R + 1)."""
    if not 0.0 <= p <= 1.0 or relances < 0:
        raise ValueError("p dans [0, 1] et relances >= 0")
    return 1.0 - (1.0 - p) ** (relances + 1)


def etapes_max(p: float, cible: float) -> int:
    """Plus grand n tel que p^n >= cible : partie entière de ln c / ln p, contrôlée directement."""
    if not (0.0 < p < 1.0 and 0.0 < cible < 1.0):
        raise ValueError("p et cible dans ]0, 1[")
    n = math.floor(math.log(cible) / math.log(p))
    while p ** (n + 1) >= cible:          # garde contre un quotient arrondi juste sous un entier
        n += 1
    while n > 0 and p ** n < cible:
        n -= 1
    return n


def p_min_par_etape(n: int, cible: float) -> float:
    """Plus petite fiabilité commune qui garantit p^n >= cible : c^(1/n)."""
    if n < 1 or not 0.0 < cible < 1.0:
        raise ValueError("n >= 1 et cible dans ]0, 1[")
    return cible ** (1.0 / n)


def cas_1_kyc_banque() -> dict:
    """[BANQUE] KYC à Dubaï : six étapes, cible 0.90, relance de l'étape la plus faible."""
    etapes = [0.99, 0.98, 0.97, 0.995, 0.99, 0.96]
    volume, cible, cout_faux, cout_relance = 10_000, 0.90, 45, 0.12
    partiels = produits_partiels(etapes)
    p = partiels[-1]
    faux = round(volume * (1 - p))
    q = avec_relances(etapes[-1], 1)
    p2 = partiels[4] * q
    faux2 = round(volume * (1 - p2))
    relances_mois = round(volume * (1 - etapes[-1]))
    moyenne = sum(etapes) / len(etapes)
    faux_naif = round(volume * (1 - moyenne))
    bascule = cible / partiels[4]
    decision = "accepter avec relance" if p < cible <= p2 else "revoir"
    economie = faux * cout_faux - faux2 * cout_faux - round(relances_mois * cout_relance)
    print(f"Cas 1 KYC : P = {p:.5f} (borne {borne(etapes):.3f}), {faux} faux/mois ;"
          f" relance -> {p2:.5f}, {faux2} faux -> {decision}")
    print(f"  coût {faux * cout_faux} -> {faux2 * cout_faux} AED + {relances_mois * cout_relance:.0f} AED"
          f" de relances ; naïf {moyenne:.5f} -> {faux_naif} faux ; bascule rédaction {bascule:.5f}")
    return {"etapes": etapes, "partiels": partiels, "p": p, "faux": faux, "q": q, "p2": p2,
            "faux2": faux2, "relances": relances_mois, "moyenne": moyenne, "faux_naif": faux_naif,
            "bascule": bascule, "decision": decision, "economie": economie}


def cas_2_surveillance_crypto() -> dict:
    """[CRYPTO] plateforme agréée VARA : 3 étapes par cycle, 288 cycles par jour, 1 raté par semaine au plus."""
    p, etapes, par_jour, jours, objectif = 0.995, 3, 288, 7, 1.0
    par_semaine = par_jour * jours
    cycle = p ** etapes
    jour_rates = par_jour * (1 - cycle)
    semaine_rates = par_semaine * (1 - cycle)
    journee_parfaite = cycle ** par_jour
    q = avec_relances(p, 1)
    cycle_r = q ** etapes
    semaine_r = par_semaine * (1 - cycle_r)
    jour_r = par_jour * (1 - cycle_r)
    naif = par_jour * (1 - p)
    bascule = (1 - objectif / par_semaine) ** (1 / etapes)
    bascule_r = 1 - math.sqrt(1 - bascule)
    decision = "1 relance par étape" if semaine_rates > objectif >= semaine_r else "revoir"
    print(f"Cas 2 VARA : cycle {cycle:.6f}, {jour_rates:.2f} ratés/jour, {semaine_rates:.2f}/semaine,"
          f" journée parfaite {journee_parfaite:.4f}")
    print(f"  relance : q = {q:.6f}, cycle {cycle_r:.6f}, {semaine_r:.2f}/semaine, {jour_r:.2f}/jour -> {decision}")
    print(f"  naïf {naif:.2f}/jour ; bascule sans relance {bascule:.6f}, avec relance {bascule_r:.5f}")
    return {"cycle": cycle, "jour": jour_rates, "semaine": semaine_rates, "parfaite": journee_parfaite,
            "q": q, "cycle_r": cycle_r, "semaine_r": semaine_r, "jour_r": jour_r, "naif": naif,
            "bascule": bascule, "bascule_r": bascule_r, "decision": decision, "par_semaine": par_semaine}


def cas_3_fin_de_service_rh() -> dict:
    """[RH] fin de service : combien d'étapes laisser au modèle pour une cible de 0.95."""
    p_modele, p_code, cible, volume = 0.98, 0.9999, 0.95, 1_200
    base, annees = 12_000, 7
    journalier = base / 30
    jours = 21 * min(annees, 5) + 30 * max(annees - 5, 0)
    indemnite = min(jours * journalier, 24 * base)
    v1 = fiabilite([p_modele] * 5)
    faux1 = round(volume * (1 - v1))
    quotient = math.log(cible) / math.log(p_modele)
    n_max = etapes_max(p_modele, cible)
    v2 = fiabilite([p_modele] * 2 + [p_code] * 3)
    faux2 = round(volume * (1 - v2))
    naif = round(volume * (1 - p_modele))
    erreur_bareme = 30 * annees * journalier - indemnite
    p3 = p_min_par_etape(3, cible)
    bascule = (cible / p_code ** 2) ** (1 / 3)
    decision = "version 2" if v1 < cible <= v2 else "revoir"
    print(f"Cas 3 RH : indemnité {indemnite:.0f} AED ({jours} jours à {journalier:.0f}) ; 5 étapes modèle"
          f" {v1:.5f} -> {faux1} faux ; n_max = {n_max} (quotient {quotient:.4f})")
    print(f"  version 2 : {v2:.5f} -> {faux2} faux -> {decision} ; naïf {naif} faux")
    print(f"  erreur de barème +{erreur_bareme:.0f} AED ; bascule {bascule:.5f} (p_min {p3:.5f})")
    return {"journalier": journalier, "jours": jours, "indemnite": indemnite, "v1": v1, "faux1": faux1,
            "quotient": quotient, "n_max": n_max, "v2": v2, "faux2": faux2, "naif": naif,
            "erreur": erreur_bareme, "p3": p3, "bascule": bascule, "decision": decision}


def cas_4_guichet_public() -> dict:
    """[PUBLIC] guichet UAE Pass : une étape de confirmation qui fiabilise l'identification."""
    version_a = [0.99, 0.96, 0.97, 0.98, 0.985]
    version_b = [0.99, 0.995, 0.999, 0.97, 0.98, 0.985]
    volume, abandon, cout_echec, cout_abandon = 50_000, 0.03, 25, 15
    part_a, part_b = produits_partiels(version_a), produits_partiels(version_b)
    pa, pb = part_a[-1], part_b[-1]
    c_a = (1 - pa) * cout_echec
    c_b = abandon * cout_abandon + (1 - abandon) * (1 - pb) * cout_echec
    mois_a, mois_b = round(volume * c_a), round(volume * c_b)
    reussies_a = round(volume * pa)
    reussies_b = round(volume * (1 - abandon) * pb)
    naif = pa * 0.999
    k = (1 - pb) * cout_echec
    bascule = (c_a - k) / (cout_abandon - k)
    decision = "ajouter la confirmation" if c_b < c_a and reussies_b > reussies_a else "ne pas ajouter"
    print(f"Cas 4 UAE Pass : A {pa:.6f}, B {pb:.6f} ; coût/demande {c_a:.4f} -> {c_b:.4f} AED")
    print(f"  mois {mois_a} -> {mois_b} AED -> {decision}")
    print(f"  abouties {reussies_a} -> {reussies_b} ; naïf {naif:.6f} ; bascule abandon {bascule:.4f}")
    return {"part_a": part_a, "part_b": part_b, "pa": pa, "pb": pb, "c_a": c_a, "c_b": c_b,
            "mois_a": mois_a, "mois_b": mois_b, "reussies_a": reussies_a, "reussies_b": reussies_b,
            "naif": naif, "k": k, "bascule": bascule, "decision": decision}


def main() -> None:
    # Le mécanisme : film de trois étapes et logarithmes
    film = produits_partiels([0.99, 0.98, 0.97])
    pertes = [1.0 - film[0], film[0] - film[1], film[1] - film[2]]
    logs = [math.log(p) for p in (0.99, 0.98, 0.97)]
    print(f"Mécanisme : 1 -> {film[0]:.2f} -> {film[1]:.4f} -> {film[2]:.6f} ;"
          f" pertes {pertes[0]:.2f}, {pertes[1]:.4f}, {pertes[2]:.6f} ; somme des ln {sum(logs):.6f}")
    assert [round(x, 6) for x in film] == [0.99, 0.9702, 0.941094]
    assert [round(x, 6) for x in pertes] == [0.01, 0.0198, 0.029106]
    assert [round(x, 6) for x in logs] == [-0.01005, -0.020203, -0.030459]
    assert round(sum(logs), 6) == -0.060712 and round(math.exp(sum(logs)), 6) == 0.941094
    assert round(1 - film[2], 6) == 0.058906 and round(0.01 + 0.02 + 0.03, 2) == 0.06
    assert round(1 - 0.99 ** 10, 3) == 0.096                 # analogie : dix filtres, près de 10 % de rejets

    # Exemple simple
    e5, e99 = fiabilite([0.9] * 5), fiabilite([0.99] * 5)
    print(f"Exemple : 0,9^5 = {e5:.5f} (0.81 puis 0.6561), échecs {1 - e5:.5f}, borne {borne([0.9] * 5):.2f} ;"
          f" 0,99^5 = {e99:.5f}, borne {borne([0.99] * 5):.2f}")
    assert round(0.9 ** 2, 2) == 0.81 and round(0.81 ** 2, 4) == 0.6561 and round(e5, 5) == 0.59049
    assert round(1 - e5, 5) == 0.40951 and round(borne([0.9] * 5), 2) == 0.5
    assert round(0.99 ** 2, 4) == 0.9801 and round(0.9801 ** 2, 8) == 0.96059601
    assert round(e99, 10) == 0.9509900499 and round(e99, 5) == 0.95099
    assert round(borne([0.99] * 5), 2) == 0.95 and round(e99 - 0.95, 5) == 0.00099

    # Démonstrations 1 à 6
    print(f"D1 : indépendantes {0.9 * 0.9:.2f} ; échec commun 0.90 ; échecs disjoints {1 - 0.1 - 0.1:.2f}")
    assert round(0.9 * 0.9, 2) == 0.81 and round(1 - 0.1 - 0.1, 2) == 0.8
    six = e5 * 0.9
    print(f"D2 : {e5:.5f} x 0.9 = {six:.6f}, perte {e5 * 0.1:.6f}")
    assert round(six, 6) == 0.531441 and round(e5 * 0.1, 6) == 0.059049 and fiabilite([0.9] * 5 + [1.0]) == e5
    deux = 0.96 * 0.97
    vingt = fiabilite([0.9] * 20)
    print(f"D3 : 0.96 x 0.97 = {deux:.4f} >= {borne([0.96, 0.97]):.2f} ; 20 étapes à 0.9 : borne"
          f" {1 - 20 * 0.1:.0f} -> {borne([0.9] * 20):.0f}, produit {vingt:.5f}")
    assert round(deux, 4) == 0.9312 and round(borne([0.96, 0.97]), 2) == 0.93 and round(deux - 0.93, 4) == 0.0012
    assert round(1 - 20 * 0.1) == -1 and borne([0.9] * 20) == 0.0 and round(vingt, 5) == 0.12158
    quotient = math.log(0.9) / math.log(0.98)
    print(f"D4 : ln 0.9 = {math.log(0.9):.5f}, ln 0.98 = {math.log(0.98):.5f}, quotient {quotient:.3f},"
          f" n_max {etapes_max(0.98, 0.9)}")
    print(f"  0.98^5 = {0.98 ** 5:.5f}, 0.98^6 = {0.98 ** 6:.5f} ; p_min(10, 0.95) = {p_min_par_etape(10, 0.95):.5f}")
    assert round(math.log(0.9), 5) == -0.10536 and round(math.log(0.98), 5) == -0.0202
    assert round(quotient, 3) == 5.215 and etapes_max(0.98, 0.9) == 5
    assert round(0.98 ** 5, 5) == 0.90392 and round(0.98 ** 6, 5) == 0.88584
    assert round(p_min_par_etape(10, 0.95), 5) == 0.99488 and round((1 - 0.9) / (1 - 0.98), 6) == 5
    permanent = 0.02 + 0.02 * 0.04
    print(f"D5 : 0.96 relancée 1 fois {avec_relances(0.96, 1):.4f} ; 0.9 relancée 2 fois"
          f" {avec_relances(0.9, 2):.3f} ; moitié d'échecs permanents {1 - permanent:.4f}")
    assert round(avec_relances(0.96, 1), 4) == 0.9984 and round(0.04 ** 2, 4) == 0.0016
    assert round(avec_relances(0.9, 2), 3) == 0.999 and round(permanent, 4) == 0.0208
    assert round(1 - permanent, 4) == 0.9792 and round(0.04 ** 3, 6) == 0.000064
    assert avec_relances(0.96, 2) > avec_relances(0.96, 1) > avec_relances(0.96, 0) == 0.96
    kyc = [0.99, 0.98, 0.97, 0.995, 0.99, 0.96]
    p_kyc = fiabilite(kyc)
    f_red, f_san = 1 + 0.02 / 0.96, 1 + 0.0025 / 0.995
    print(f"D6 : +1 % sur la rédaction -> {fiabilite(kyc[:5] + [0.96 * 1.01]):.5f} ; erreur divisée par 2 :"
          f" rédaction x{f_red:.5f} -> {p_kyc * f_red:.5f}, sanctions x{f_san:.5f} -> {p_kyc * f_san:.5f}")
    assert math.isclose(fiabilite(kyc[:5] + [0.96 * 1.01]), p_kyc * 1.01)
    assert round(0.96 * 1.01, 4) == 0.9696 and round(p_kyc * 1.01, 5) == 0.89884
    assert round(f_red, 5) == 1.02083 and round(p_kyc * f_red, 5) == 0.90848
    assert math.isclose(fiabilite(kyc[:5] + [0.98]), p_kyc * f_red)
    assert round(f_san, 5) == 1.00251 and round(p_kyc * f_san, 5) == 0.89218

    # Cas 1 — banque
    c1 = cas_1_kyc_banque()
    assert [round(x, 8) for x in c1["partiels"]] == [0.99, 0.9702, 0.941094, 0.93638853, 0.92702464, 0.88994366]
    assert round(c1["p"], 5) == 0.88994 and round(borne(c1["etapes"]), 3) == 0.885 and borne(c1["etapes"]) <= c1["p"]
    assert round(sum(1 - p for p in c1["etapes"]), 3) == 0.115
    assert round(10_000 * (1 - c1["p"]), 1) == 1100.6 and c1["faux"] == 1101 and c1["faux"] * 45 == 49_545
    assert round(c1["q"], 4) == 0.9984 and round(c1["partiels"][4] * 0.9984, 8) == 0.92554141
    assert round(c1["p2"], 5) == 0.92554 and round(10_000 * (1 - c1["p2"]), 1) == 744.6
    assert c1["faux2"] == 745 and c1["faux2"] * 45 == 33_525 and c1["relances"] == 400 and round(400 * 0.12) == 48
    assert c1["decision"] == "accepter avec relance" and c1["faux"] - c1["faux2"] == 356 and c1["economie"] == 15_972
    assert round(sum(c1["etapes"]), 3) == 5.885 and round(c1["moyenne"], 5) == 0.98083 and c1["faux_naif"] == 192
    assert c1["faux"] - c1["faux_naif"] == 909 and 909 * 45 == 40_905
    assert round(c1["bascule"], 5) == 0.97085 and round(1 - c1["p2"], 3) == 0.074

    # Cas 2 — crypto
    c2 = cas_2_surveillance_crypto()
    assert c2["par_semaine"] == 2016 and round(0.995 ** 2, 6) == 0.990025 and round(c2["cycle"], 6) == 0.985075
    assert round(c2["jour"], 2) == 4.30 and round(c2["semaine"], 2) == 30.09 and round(1 - c2["cycle"], 6) == 0.014925
    assert math.isclose(c2["parfaite"], 0.995 ** 864) and round(c2["parfaite"], 4) == 0.0132
    assert round(c2["q"], 6) == 0.999975 and round(c2["cycle_r"], 6) == 0.999925
    assert round(c2["semaine_r"], 2) == 0.15 and round(c2["jour_r"], 2) == 0.02 and c2["decision"] == "1 relance par étape"
    assert round(c2["naif"], 2) == 1.44 and round(c2["jour"] / c2["naif"]) == 3
    assert round(c2["bascule"], 6) == 0.999835 and round(c2["bascule"], 4) == 0.9998
    assert round(c2["bascule_r"], 5) == 0.98714 and round(c2["bascule_r"], 4) == 0.9871
    assert c2["parfaite"] < 0.02 and 300 > 20

    # Cas 3 — RH
    c3 = cas_3_fin_de_service_rh()
    assert c3["journalier"] == 400 and c3["jours"] == 165 and 5 * 21 == 105 and 2 * 30 == 60
    assert c3["indemnite"] == 66_000 and 24 * 12_000 == 288_000
    assert round(c3["v1"], 5) == 0.90392 and round(1_200 * (1 - c3["v1"]), 1) == 115.3 and c3["faux1"] == 115
    assert round(math.log(0.95), 6) == -0.051293 and round(math.log(0.98), 6) == -0.020203
    assert round(c3["quotient"], 4) == 2.5389 and c3["n_max"] == 2
    assert round(0.98 ** 2, 4) == 0.9604 and round(0.9999 ** 3, 8) == 0.99970003 and round(c3["v2"], 5) == 0.96011
    assert round(1_200 * (1 - c3["v2"]), 1) == 47.9 and c3["faux2"] == 48 and c3["faux1"] - c3["faux2"] == 67
    assert c3["decision"] == "version 2" and c3["naif"] == 24 and round(c3["faux1"] / c3["naif"]) == 5
    assert 7 * 30 == 210 and 210 * 400 == 84_000 and c3["erreur"] == 18_000
    assert round(0.9999 ** 2, 4) == 0.9998 and round(c3["bascule"], 5) == 0.98311 and round(c3["p3"], 5) == 0.98305
    assert round(1 - c3["v2"], 2) == 0.04

    # Cas 4 — secteur public
    c4 = cas_4_guichet_public()
    assert [round(x, 6) for x in c4["part_a"]] == [0.99, 0.9504, 0.921888, 0.90345, 0.889898]
    assert [round(x, 6) for x in c4["part_b"]] == [0.99, 0.98505, 0.984065, 0.954543, 0.935452, 0.92142]
    assert round(c4["c_a"], 4) == 2.7525 and round(0.03 * 15, 2) == 0.45
    assert round(0.97 * (1 - c4["pb"]) * 25, 4) == 1.9056 and round(c4["c_b"], 4) == 2.3556
    assert c4["mois_a"] == 137_627 and c4["mois_b"] == 117_778 and c4["mois_a"] - c4["mois_b"] == 19_849
    assert c4["reussies_a"] == 44_495 and c4["reussies_b"] == 44_689 and 50_000 * 0.97 == 48_500
    assert c4["decision"] == "ajouter la confirmation" and round(c4["naif"], 6) == 0.889009 and c4["naif"] < c4["pa"]
    assert round(c4["k"], 4) == 1.9645 and round(c4["bascule"], 4) == 0.0605
    assert 0.03 < 0.05 < c4["bascule"]

    # Corrigé
    print("Corrigé")
    n_max = etapes_max(0.98, 0.9)
    p_min = p_min_par_etape(10, 0.95)
    exact = fiabilite([0.98, 0.97, 0.95])
    print(f"  ex1 0,95^4 = {0.95 ** 4:.8f} ; ex2 n_max = {n_max} ; ex3 p_min = {p_min:.5f}")
    print(f"  ex4 exact {exact:.5f} >= borne {borne([0.98, 0.97, 0.95]):.2f} ; ex5 {avec_relances(0.9, 2):.3f}")
    assert round(0.95 ** 2, 4) == 0.9025 and round(0.9025 * 0.9, 5) == 0.81225 and round(0.9025 * 0.0025, 8) == 0.00225625
    assert round(0.95 ** 4, 8) == 0.81450625 and n_max == 5 and round(p_min, 5) == 0.99488 and round(p_min, 4) == 0.9949
    assert round(math.log(0.95) / 10, 7) == -0.0051293 and math.isclose(math.exp(math.log(0.95) / 10), p_min)
    assert round(0.98 * 0.97, 4) == 0.9506 and round(exact, 5) == 0.90307 and round(exact - 0.90, 5) == 0.00307
    assert exact >= borne([0.98, 0.97, 0.95]) and round(borne([0.98, 0.97, 0.95]), 2) == 0.90 and round(0.1 ** 3, 3) == 0.001
    for a in (0.0, 0.1, 0.5):
        for b in (0.0, 0.2, 0.9):
            for c in (0.0, 0.3, 1.0):
                assert (1 - a) * (1 - b) * (1 - c) >= 1 - a - b - c - 1e-12     # exercice 6
    ex7 = produits_partiels([0.99, 0.95, 0.97, 0.995, 0.99, 0.9984])
    ex7_bis = ex7[-1] * avec_relances(0.95, 1) / 0.95
    print(f"  ex7 {ex7[-1]:.5f} < 0.90 -> relance de l'extraction {avec_relances(0.95, 1):.4f} -> {ex7_bis:.5f} ;"
          f" ex8 au plus {n_max} étapes ; ex9 {avec_relances(0.8, 2):.3f}")
    assert [round(x, 6) for x in ex7] == [0.99, 0.9405, 0.912285, 0.907724, 0.898646, 0.897209]
    assert round(ex7[-1], 5) == 0.89721 and ex7[-1] < 0.90 and round(avec_relances(0.95, 1), 4) == 0.9975
    assert round(ex7_bis, 5) == 0.94207 and ex7_bis >= 0.90
    assert round(avec_relances(0.8, 2), 3) == 0.992 and round(0.2 ** 3, 3) == 0.008
    for invalide in ([], [1.2], [-0.1]):
        try:
            fiabilite(invalide)
        except ValueError:
            continue
        raise AssertionError("entrée invalide acceptée")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Mécanisme : 1 -> 0.99 -> 0.9702 -> 0.941094 ; pertes 0.01, 0.0198, 0.029106 ; somme des ln -0.060712
Exemple : 0,9^5 = 0.59049 (0.81 puis 0.6561), échecs 0.40951, borne 0.50 ; 0,99^5 = 0.95099, borne 0.95
D1 : indépendantes 0.81 ; échec commun 0.90 ; échecs disjoints 0.80
D2 : 0.59049 x 0.9 = 0.531441, perte 0.059049
D3 : 0.96 x 0.97 = 0.9312 >= 0.93 ; 20 étapes à 0.9 : borne -1 -> 0, produit 0.12158
D4 : ln 0.9 = -0.10536, ln 0.98 = -0.02020, quotient 5.215, n_max 5
  0.98^5 = 0.90392, 0.98^6 = 0.88584 ; p_min(10, 0.95) = 0.99488
D5 : 0.96 relancée 1 fois 0.9984 ; 0.9 relancée 2 fois 0.999 ; moitié d'échecs permanents 0.9792
D6 : +1 % sur la rédaction -> 0.89884 ; erreur divisée par 2 : rédaction x1.02083 -> 0.90848, sanctions x1.00251 -> 0.89218
Cas 1 KYC : P = 0.88994 (borne 0.885), 1101 faux/mois ; relance -> 0.92554, 745 faux -> accepter avec relance
  coût 49545 -> 33525 AED + 48 AED de relances ; naïf 0.98083 -> 192 faux ; bascule rédaction 0.97085
Cas 2 VARA : cycle 0.985075, 4.30 ratés/jour, 30.09/semaine, journée parfaite 0.0132
  relance : q = 0.999975, cycle 0.999925, 0.15/semaine, 0.02/jour -> 1 relance par étape
  naïf 1.44/jour ; bascule sans relance 0.999835, avec relance 0.98714
Cas 3 RH : indemnité 66000 AED (165 jours à 400) ; 5 étapes modèle 0.90392 -> 115 faux ; n_max = 2 (quotient 2.5389)
  version 2 : 0.96011 -> 48 faux -> version 2 ; naïf 24 faux
  erreur de barème +18000 AED ; bascule 0.98311 (p_min 0.98305)
Cas 4 UAE Pass : A 0.889898, B 0.921420 ; coût/demande 2.7525 -> 2.3556 AED
  mois 137627 -> 117778 AED -> ajouter la confirmation
  abouties 44495 -> 44689 ; naïf 0.889009 ; bascule abandon 0.0605
Corrigé
  ex1 0,95^4 = 0.81450625 ; ex2 n_max = 5 ; ex3 p_min = 0.99488
  ex4 exact 0.90307 >= borne 0.90 ; ex5 0.999
  ex7 0.89721 < 0.90 -> relance de l'extraction 0.9975 -> 0.94207 ; ex8 au plus 5 étapes ; ex9 0.992
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme prend les fiabilités des étapes d'un agent, avec les relances autorisées pour chacune, et renvoie sa fiabilité globale, la borne « 1 moins la somme des erreurs », le nombre maximal d'étapes pour une cible donnée, la fiabilité minimale par étape et la décision d'accepter la chaîne ou de renforcer son maillon le plus faible.

```text
ALGORITHME FiabilitéEnSérie
ENTRÉES : fiabilités p₁ … pₙ, relances R₁ … Rₙ, cible c, fiabilité commune p
SORTIE  : (P, borne, n_max, p_min, décision)

  SI n = 0 OU un pᵢ hors de [0, 1] ALORS ERREUR « entrée invalide »
  P ← 1
  erreurs ← 0
  POUR i DE 1 À n FAIRE
      qᵢ ← 1 − (1 − pᵢ)^(Rᵢ + 1)            (étape avec ses relances)
      P ← P × qᵢ
      erreurs ← erreurs + (1 − qᵢ)
  FIN POUR
  borne ← max(0, 1 − erreurs)
  n_max ← partie entière de ln c / ln p     (puis contrôle direct : p^n_max ≥ c > p^(n_max + 1))
  p_min ← c puissance (1/n)
  SI P ≥ c ALORS décision ← « accepter »
  SINON décision ← « renforcer l'étape de plus petite qᵢ »
  RETOURNER P, borne, n_max, p_min, décision
```

**Complexité.** O(n) en temps pour le produit, la somme des erreurs et la recherche de l'étape la plus faible ; O(1) pour le nombre maximal d'étapes (plus une ou deux puissances de contrôle) et pour la fiabilité minimale. Mémoire O(1) si les fiabilités arrivent en flux, O(n) si l'on garde les produits partiels.

**Du squelette au code.** Le produit correspond à `fiabilite` (qui utilise `math.prod`), la somme des erreurs à `borne`, la ligne de qᵢ à `avec_relances`, la recherche de nₘₐₓ à `etapes_max` (variable `n_max` de `main`) et la racine n-ième à `p_min_par_etape` (variable `p_min`). Les produits partiels des cas 1 et 4 viennent de `produits_partiels`. Les quatre cas sont `cas_1_kyc_banque`, `cas_2_surveillance_crypto`, `cas_3_fin_de_service_rh` et `cas_4_guichet_public` ; la décision d'accepter ou de renforcer est la variable `decision` de chacun.
