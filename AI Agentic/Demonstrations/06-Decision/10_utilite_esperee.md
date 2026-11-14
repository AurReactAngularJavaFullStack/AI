# 10 — Utilité espérée d'une action : démonstrations

> Fiche : [10 — Utilité espérée d'une action](<../../Images/06-Decision/10_utilite_esperee.md>) · Image : `10_utilite_esperee.jpg` · Leçon : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
U(a) = \mathbb{E}[B(a)] - \lambda_c\, C(a) - \lambda_t\, T(a) - \lambda_r\, R(a)
$$

Pour chaque action a, on part du bénéfice attendu 𝔼[B(a)], puis on retire son coût C, son temps T et son risque R, chacun converti en points par un poids λ fixé par le métier. L'agent choisit l'action d'utilité maximale parmi les actions **autorisées**. Dans le texte, les trois poids s'écrivent λc, λt et λr (λ indicé par c pour le coût, t pour le temps, r pour le risque).

## Les symboles, un par un

$$
a
$$

L'action candidate : appeler un outil, chercher un document, escalader à un humain, payer une facture ; un élément d'un ensemble fini d'actions **autorisées** ; dans le programme, une clé du dictionnaire passé à `choisir`.

$$
\mathbb{E}[B(a)]
$$

Le bénéfice moyen attendu de l'action, en points (1 point ≈ 1 AED quand le cas le précise, illustratif) ; un réel, négatif si l'action perd en moyenne ; calculé par `benefice_attendu(p, gain, perte)` et passé à `utilite` comme argument `benefice`.

$$
C(a)
$$

Le coût direct de l'action : tokens, appel payant, temps d'un expert, frais ; en AED (ou en USD, voir la démonstration 5) ; un réel ≥ 0 ; l'argument `cout` de `utilite`.

$$
T(a)
$$

Le délai de l'action, en secondes, en heures ou en jours selon le cas ; un réel ≥ 0 ; l'argument `temps` de `utilite`.

$$
R(a)
$$

Le risque : ici la probabilité d'un effet indésirable (erreur, plainte, reprogrammation) ; un nombre de [0 ; 1] ; l'argument `risque` de `utilite`.

$$
\lambda_c
$$

Le poids du coût : combien de points coûte une unité de coût (par exemple 1 point par AED) ; un réel ≥ 0 ; l'argument `lc` (1.0 par défaut).

$$
\lambda_t
$$

Le poids du temps : combien de points coûte une unité de délai (2 points par seconde dans l'exemple simple, 450 AED par jour dans le cas 3) ; un réel ≥ 0 ; l'argument `lt` (2.0 par défaut).

$$
\lambda_r
$$

Le poids du risque : combien de points coûte un risque certain, R = 1 (50 points dans l'exemple simple) ; un réel ≥ 0 ; l'argument `lr` (50.0 par défaut).

$$
U(a)
$$

L'utilité de l'action, en points : ce que l'action rapporte net de ses pénalités ; un réel, sans borne a priori ; la valeur renvoyée par `utilite(benefice, cout, temps, risque, lc, lt, lr)`.

$$
p, \; g, \; \ell
$$

Pour une action à deux issues : p est la probabilité de succès (dans [0 ; 1]), g le gain en cas de succès et ℓ la perte en cas d'échec (réels ≥ 0, en points) ; les arguments `p`, `gain` et `perte` de `benefice_attendu`.

## Le mécanisme, avant les preuves

La formule reçoit, pour chaque action, quatre nombres mesurés dans quatre unités différentes (un bénéfice espéré en points, un coût en AED, un délai en secondes, un risque en probabilité) et trois poids fixés par le métier. Le bénéfice espéré est déjà une moyenne : p × g − (1 − p) × ℓ, le gain de chaque issue pondéré par sa probabilité (fiche 22). Chaque produit λ × critère est une conversion d'unité : λt = 2 points par seconde transforme 8 secondes en 16 points, et après les trois produits tout est exprimé en points, ce qui permet enfin de soustraire. La soustraction retire les pénalités du bénéfice, et elle est linéaire : chaque unité de coût, de temps ou de risque coûte toujours le même nombre de points, la trentième seconde autant que la première. Les termes sont séparés, sans produit entre critères : on lit l'effet de chaque critère isolément, et la différence U(a) − U(b) se calcule critère par critère (démonstrations 2 et 6). On prend une différence plutôt qu'un ratio bénéfice/coût parce que le ratio ignore l'échelle : au cas 4, il préfère un message à 2 880 AED de bénéfice pour 20 AED de coût (ratio 144) à une visite à 5 400 AED pour 400 AED (ratio 13,5), alors que l'utilité nette de la visite est bien plus grande. On prend l'espérance du bénéfice parce que l'agent répète la même décision des milliers de fois, et que la moyenne des gains réalisés se rapproche alors de l'espérance ; le risque est pénalisé à part parce qu'une moyenne ne voit pas la gravité d'un mauvais cas rare. Le maximum ne se prend que sur les actions autorisées : le filtre des contraintes passe avant le calcul (démonstration 4), et si la meilleure utilité n'est pas positive, l'agent ne fait rien. Ce qui sort est un nombre par action et une seule décision. Pour un développeur Java, c'est la différence entre un `Comparator` en cascade (coût d'abord, puis délai), où aucune seconde ne peut compenser un AED, et un `comparingDouble` sur une seule clé calculée, où les compensations sont permises au taux fixé par les λ.

**Petit film chiffré** (exemple simple : λc = 1, λt = 2 points par seconde, λr = 50). On suit les deux outils opération par opération.

| Opération | Outil A | Outil B |
|---|---|---|
| bénéfice attendu | 100 | 120 |
| − λc × C | 100 − 1 × 5 = 95 | 120 − 1 × 20 = 100 |
| − λt × T | 95 − 2 × 2 = 91 | 100 − 2 × 8 = 84 |
| − λr × R | 91 − 50 × 0,1 = 86 | 84 − 50 × 0,3 = 69 |
| maximum | 86, choisi | 69 |

B part avec 20 points d'avance, en perd 15 sur le coût, 12 sur le temps et 10 sur le risque : il finit 17 points derrière.

## Démonstration 1 — Le bénéfice attendu d'une action incertaine

**Ce qu'on démontre.** Si l'action réussit avec la probabilité p (gain g ≥ 0) et échoue sinon (perte ℓ ≥ 0), son bénéfice attendu est une fonction affine de p, positive exactement au-dessus du seuil de rentabilité ℓ/(g + ℓ) :

$$
\mathbb{E}[B(a)] = p\, g - (1 - p)\, \ell = (g + \ell)\, p - \ell, \qquad \mathbb{E}[B(a)] \ge 0 \iff p \ge \frac{\ell}{g + \ell}
$$

**L'idée.** L'espérance est la moyenne pondérée de deux valeurs, +g et −ℓ. Chaque point de probabilité qui passe de l'échec au succès fait gagner g et éviter ℓ : il rapporte g + ℓ. C'est pourquoi la courbe est une droite de pente g + ℓ.

**La preuve, pas à pas.**

**Étape 1.** On applique la définition de l'espérance à deux issues (fiche 22), parce que l'action n'a que deux résultats possibles :

$$
\mathbb{E}[B(a)] = p \times g + (1 - p) \times (-\ell)
$$

**Étape 2.** On développe le second produit, parce que la multiplication se distribue sur la soustraction, puis on regroupe les termes en p :

$$
p\, g - \ell + p\, \ell = (g + \ell)\, p - \ell
$$

**Étape 3.** On résout (g + ℓ)p − ℓ ≥ 0 ; on divise par g + ℓ, ce qui garde le sens de l'inégalité parce que g + ℓ > 0 :

$$
(g + \ell)\, p \ge \ell \iff p \ge \frac{\ell}{g + \ell}
$$

∎

**Vérification chiffrée.** Avec g = 50 et ℓ = 200 (une bonne réponse rapporte 50 points, une mauvaise en coûte 200) : 𝔼[B] = 250p − 200. À p = 0,8 : 250 × 0,8 − 200 = 0. À p = 0,95 : 237,5 − 200 = 37,5. Le seuil de rentabilité vaut 200/250 = 0,8, et chaque centième de probabilité au-dessus rapporte 2,5 points (à p = 0,81, 𝔼[B] = 2,5). **Contre-exemple quand les issues ne sont pas deux :** une action réussit pleinement avec la probabilité 0,7 (+50), à moitié avec 0,2 (+10) et échoue avec 0,1 (−200). La vraie espérance vaut 0,7 × 50 + 0,2 × 10 + 0,1 × (−200) = 35 + 2 − 20 = 17. Compter la demi-réussite comme un succès (p = 0,9) donne 0,9 × 50 − 0,1 × 200 = 25 : une surestimation de 8 points.

**Ce que la preuve révèle du mécanisme.** Quand la perte domine le gain (ℓ ≫ g), la pente g + ℓ est surtout faite de la perte, et le seuil ℓ/(g + ℓ) monte : avec ℓ = 4g, il faut déjà 80 % de réussite pour ne rien perdre en moyenne. Le gain, lui, ne fait que tirer le seuil vers le bas.

**Conséquence pour un agent.** Une action dont l'échec coûte cher (rembourser à tort, payer une facture fausse) exige une confiance élevée et calibrée. Si les issues ne sont pas binaires, on écrit toutes les issues avec la formule générale de l'espérance au lieu de forcer deux cas.

## Démonstration 2 — La dominance

**Ce qu'on démontre.** Si une action a a un bénéfice au moins égal à celui de b, et un coût, un temps et un risque au plus égaux, alors U(a) ≥ U(b) pour **tous** les poids λc, λt, λr ≥ 0 :

$$
U(a) - U(b) = \big(\mathbb{E}[B(a)] - \mathbb{E}[B(b)]\big) + \lambda_c (C_b - C_a) + \lambda_t (T_b - T_a) + \lambda_r (R_b - R_a) \ge 0
$$

**L'idée.** Chaque terme de la différence est un poids positif multiplié par un écart favorable à a. Une somme de nombres positifs ou nuls est positive ou nulle, quels que soient les poids.

**La preuve, pas à pas.**

**Étape 1.** On écrit U(a) − U(b) avec la formule et on regroupe les termes critère par critère, parce que chaque critère n'apparaît que dans un terme : on obtient l'égalité ci-dessus.

**Étape 2.** On étudie le signe de chaque terme : le premier est ≥ 0 par hypothèse ; dans les trois autres, λ ≥ 0 et l'écart (Cᵦ − Cₐ, Tᵦ − Tₐ, Rᵦ − Rₐ) est ≥ 0 par hypothèse, donc chaque produit est ≥ 0.

**Étape 3.** Une somme de quatre nombres ≥ 0 est ≥ 0, donc U(a) ≥ U(b). ∎

**Vérification chiffrée.** x = (bénéfice 60 ; coût 2 ; temps 1 s ; risque 0) et y = (55 ; 4 ; 3 s ; 0,05) : U(x) − U(y) = 5 + 2λc + 2λt + 0,05λr ≥ 5. Avec λc = 1, sur la grille λt ∈ {0 ; 1 ; 10} et λr ∈ {0 ; 50 ; 500} testée par le programme, le plus petit écart vaut 5 + 2 = 7. **Contre-exemple sans dominance :** les outils A et B de l'exemple simple. B a un plus grand bénéfice (120 > 100) mais il est pire sur les trois autres critères : aucun ne domine l'autre. Sans poids (λ = 0), U(B) − U(A) = 120 − 100 = 20 > 0 ; avec les poids de l'exemple, A gagne de 17 points. La décision dépend donc des poids.

**Ce que la preuve révèle du mécanisme.** La dominance est la seule comparaison qui ne dépend d'aucun poids. Les actions qu'aucune autre ne domine forment le front de Pareto : ce sont les vrais compromis, et ce sont les seules que les poids départagent.

**Conséquence pour un agent.** On retire les actions dominées avant de discuter des poids : la discussion avec le métier ne porte plus que sur de vrais compromis. Au cas 3, l'option d'Abu Dhabi disparaît ainsi avant tout calcul.

## Démonstration 3 — Le seuil de confiance qui fait changer de décision

**Ce qu'on démontre.** On compare deux actions : répondre tout de suite, d'utilité Uᵣ(p) = αp − β affine en la confiance p avec une pente α > 0, et vérifier d'abord, d'utilité fixe Uᵥ. L'agent doit répondre directement si et seulement si p dépasse un seuil calculable :

$$
\alpha\, p - \beta > U_v \iff p > p^{*} = \frac{U_v + \beta}{\alpha}
$$

**L'idée.** Une droite croissante ne coupe une constante qu'en un point. Sous ce point, vérifier est meilleur ; au-dessus, répondre l'est. Il suffit donc de calculer ce point une fois.

**La preuve, pas à pas.**

**Étape 1.** Uᵣ(p) est affine en p, parce que c'est une somme de fonctions affines : le bénéfice (g + ℓ)p − ℓ (démonstration 1), le risque −λr(1 − p) quand le risque est la probabilité d'erreur, et des pénalités de coût et de temps constantes.

**Étape 2.** On ajoute β aux deux membres de αp − β > Uᵥ, ce qui ne change pas le sens de l'inégalité : αp > Uᵥ + β.

**Étape 3.** On divise par α, ce qui garde le sens parce que α > 0 : p > (Uᵥ + β)/α. ∎

**Vérification chiffrée.** Au cas 1 (gain 50, perte 200, λr = 50, coût 1, temps 2 s à 0,5 point par seconde) : Uᵣ(p) = 50p − 200(1 − p) − 1 − 0,5 × 2 − 50(1 − p) = 300p − 252, donc α = 300 et β = 252. Avec Uᵥ = 29, p* = 281/300 = 0,93667. Contrôle de part et d'autre : à p = 0,93, Uᵣ = 279 − 252 = 27 < 29 ; à p = 0,94, Uᵣ = 282 − 252 = 30 > 29. **Contre-exemple quand la confiance n'est pas calibrée :** le modèle annonce 0,95, donc Uᵣ annoncé = 285 − 252 = 33 > 29 et l'agent répond ; mais sa précision réelle n'est que 0,85, et l'utilité réelle vaut 255 − 252 = 3, soit 26 points de moins que la vérification.

**Ce que la preuve révèle du mécanisme.** La pente α additionne tout ce qu'un point de confiance fait gagner : le gain, la perte évitée et le risque évité (50 + 200 + 50 = 300). La constante β additionne la perte, le poids du risque et les pénalités fixes (200 + 50 + 1 + 1 = 252). Plus la perte est lourde, plus le seuil est haut.

**Conséquence pour un agent.** Le seuil est un paramètre calculé et versionné, pas deviné ; on le recalcule dès qu'un poids ou un coût change. Il n'a de sens que si la confiance est calibrée (fiche 20) : on mesure la précision réelle par tranche de confiance sur un échantillon audité.

## Démonstration 4 — Une action interdite ne se compense pas

**Ce qu'on démontre.** Modéliser une interdiction par une pénalité de risque ne suffit pas : pour tout poids λr fini et toute action autorisée b, une action interdite z dont le bénéfice est assez grand finit par avoir une utilité plus haute :

$$
\mathbb{E}[B(z)] > U(b) + \lambda_c\, C(z) + \lambda_t\, T(z) + \lambda_r\, R(z) \quad\Longrightarrow\quad U(z) > U(b)
$$

On exclut donc les actions interdites de l'ensemble des choix **avant** de calculer U : c'est une contrainte, pas une pénalité.

**L'idée.** Dans U, le bénéfice entre avec le coefficient +1 et n'est pas borné, alors que la pénalité de risque est bornée par λr, puisque R ≤ 1. Une quantité non bornée finit toujours par dépasser une quantité bornée.

**La preuve, pas à pas.**

**Étape 1.** On écrit U(z) = 𝔼[B(z)] − (λc C(z) + λt T(z) + λr R(z)), par définition ; la parenthèse est un nombre fini, au plus λc C(z) + λt T(z) + λr parce que R(z) ≤ 1.

**Étape 2.** Si 𝔼[B(z)] dépasse U(b) plus cette parenthèse, on soustrait la parenthèse des deux côtés, ce qui garde le sens de l'inégalité : U(z) > U(b).

**Étape 3.** Comme l'étape 2 vaut pour tout λr fini, aucune valeur de λr n'exclut z pour tous les bénéfices possibles ; seule la règle « z n'est pas dans l'ensemble des actions autorisées » le fait. ∎

**Vérification chiffrée.** Une action interdite Z (exécuter un virement sans validation) : bénéfice 500, coût 1, temps 1 s, risque 1. Avec λr = 50 : U(Z) = 500 − 1 − 2 − 50 = 447 > U(A) = 86. Avec λr = 400 : U(Z) = 97, encore au-dessus de 86. Pour l'exclure, il faudrait λr > 500 − 1 − 2 − 86 = 411 ; mais une variante Z′ de bénéfice 1 000 vaut alors, à λr = 412, 1 000 − 3 − 412 = 585 > 86. Avec la contrainte, `choisir` renvoie A quel que soit le bénéfice de Z.

**Ce que la preuve révèle du mécanisme.** Une somme pondérée est un marché : tout s'y achète, à un taux fixé. Une interdiction n'a pas de prix, donc elle ne peut pas vivre dans la somme.

**Conséquence pour un agent.** Les interdictions (dépasser 50 % de ratio d'endettement total fixé par la CBUAE, confier des documents d'identité à un tiers non habilité, agir sans la validation requise) sont codées comme un filtre, testé par des tests unitaires, avant tout calcul d'utilité.

## Démonstration 5 — Changer d'échelle ou d'unité sans changer la décision

**Ce qu'on démontre.** (a) Pour tout k > 0 et toute constante c, les utilités kU + c rangent les actions dans le même ordre que U. (b) Si un critère X est exprimé dans une nouvelle unité, X′ = X/u (par exemple des AED en USD, u = 3,6725), et si l'on prend λ′ = u × λ, alors chaque pénalité est inchangée :

$$
\lambda' X' = (u\, \lambda) \times \frac{X}{u} = \lambda X
$$

(c) Si l'on change l'unité sans changer le poids, la décision peut changer.

**L'idée.** Seuls les produits λ × critère entrent dans U. Changer d'unité multiplie le critère par un facteur ; il faut multiplier le poids par l'inverse pour garder le produit. Multiplier toutes les utilités par un même nombre positif, ou leur ajouter une même constante, ne change pas qui est en tête.

**La preuve, pas à pas.**

**Étape 1.** Pour (a) : comme k > 0, multiplier une inégalité par k garde son sens, et ajouter c aux deux membres aussi :

$$
U(a) > U(b) \iff k\, U(a) > k\, U(b) \iff k\, U(a) + c > k\, U(b) + c
$$

**Étape 2.** Pour (b) : on remplace X′ et λ′ dans le produit, et u se simplifie, comme écrit ci-dessus ; chaque U est donc inchangée, et la décision aussi.

**Étape 3.** Pour (c) : si λ ne change pas, la pénalité devient λX/u au lieu de λX ; elle est multipliée par 1/u, ce qui déplace les utilités de façon inégale selon les actions. ∎

**Vérification chiffrée.** Exemple simple, k = 3 et c = −40 : 3 × 86 − 40 = 218 > 3 × 69 − 40 = 167, même ordre. Coûts en USD : 5/3,6725 = 1,3615 USD et 20/3,6725 = 5,4459 USD ; avec λc′ = 3,6725 points par USD, les pénalités redeviennent 5 et 20, et les utilités 86 et 69. **Contre-exemple (c) :** on écrit les temps en millisecondes (2 000 et 8 000) en gardant λt = 2 : U(A) = 100 − 5 − 4 000 − 5 = −3 910 et U(B) = 120 − 20 − 16 000 − 15 = −15 915. Toutes les utilités sont négatives, et l'agent « ne fait rien » au lieu d'appeler A : la décision a changé.

**Ce que la preuve révèle du mécanisme.** Un poids λ est un taux de change entre un critère et les points : λt = 2 points par seconde veut dire qu'une seconde vaut 2 points. Seul ce taux, unité comprise, a un sens ; un λ sans unité est une source de bugs.

**Conséquence pour un agent.** On stocke chaque λ avec son unité (points par AED, par seconde, par jour) dans la configuration, et un test vérifie qu'un changement d'unité ne change aucune décision. Pour les montants en USD, on convertit au taux fixe de 3,6725 AED par USD avant de comparer.

## Démonstration 6 — La valeur de bascule d'un poids

**Ce qu'on démontre.** Pour deux actions a et b, la différence D(λt) = U(a) − U(b) est une fonction affine du poids du temps ; si T(a) ≠ T(b), elle change de signe une seule fois, en λt* :

$$
D(\lambda_t) = D_0 - \lambda_t \big( T(a) - T(b) \big), \qquad \lambda_t^{*} = \frac{D_0}{T(a) - T(b)}
$$

où D₀ regroupe tous les termes sans λt. Une hausse de 10 % de λt déplace D de −0,1 λt (T(a) − T(b)). Parmi n actions, le choix change au plus n − 1 fois quand λt augmente.

**L'idée.** Le poids multiplie un écart de temps fixe : la différence se déplace le long d'une droite, qui ne coupe zéro qu'une fois. Le point de coupure est le prix du temps auquel le surcoût de l'action rapide est exactement payé par le temps gagné.

**La preuve, pas à pas.**

**Étape 1.** On écrit U(a) − U(b) et l'on met à part les deux termes en λt, parce que ce sont les seuls qui dépendent de λt : D(λt) = D₀ − λt T(a) + λt T(b) = D₀ − λt (T(a) − T(b)).

**Étape 2.** Une fonction affine de pente non nulle s'annule en un seul point : D(λt*) = 0 donne λt* = D₀/(T(a) − T(b)).

**Étape 3.** La dérivée de D par rapport à λt est la pente −(T(a) − T(b)) ; une variation Δλt = 0,1 λt déplace donc D de −0,1 λt (T(a) − T(b)).

**Étape 4.** Pour n actions, chaque utilité est une droite en λt de pente −T(a), et la meilleure utilité est le maximum de ces droites, une fonction convexe. Sa pente ne peut qu'augmenter, donc le délai T de l'action choisie ne peut que diminuer quand λt augmente : chaque action est choisie sur un seul intervalle, d'où au plus n − 1 changements. ∎

**Vérification chiffrée.** Au cas 3, option express (750 AED, 0,25 jour, risque 0,01) contre Sharjah (280 AED, 1,5 jour, risque 0,10), avec λr = 1 550 : D₀ = (−750 − 15,5) − (−280 − 155) = −330,5 et T(a) − T(b) = 0,25 − 1,5 = −1,25, donc D(λt) = −330,5 + 1,25 λt et λt* = 330,5/1,25 = 264,4 AED par jour. À λt = 450, D = 232 ; une hausse de 10 % (495) ajoute 1,25 × 45 = 56,25. Avec trois options autorisées non dominées, le choix change deux fois : Dubaï standard sous λt = 75, Sharjah entre 75 et 264,4, express au-delà (le programme le vérifie à 50, 150 et 300). La droite express coupe aussi celle de Dubaï standard en λt = (765,5 − 397,5)/1,75 = 210,29, mais Sharjah est alors en tête : ce croisement ne change pas le choix.

**Ce que la preuve révèle du mécanisme.** Le seuil 264,4 se lit directement : l'option express coûte 470 AED de plus et économise 139,5 AED de risque, soit un surcoût net de 330,5 AED, et elle fait gagner 1,25 jour ; elle devient rentable quand un jour vaut plus que 330,5/1,25 AED.

**Conséquence pour un agent.** Avec chaque décision, on publie les valeurs de bascule des poids. Si le poids configuré est proche d'une bascule, la décision est fragile et part en revue humaine. Au cas 3, λt dépend du salaire : la même règle donne des choix différents pour un cadre et pour un junior.

## Exemple simple, à la main

Poids λc = 1, λt = 2 points par seconde, λr = 50. Outil A : bénéfice attendu 100, coût 5, temps 2 s, risque 0,1. Outil B : bénéfice 120, coût 20, temps 8 s, risque 0,3.

**Étape 1.** Pénalités de A : coût 1 × 5 = 5 ; temps 2 × 2 = 4 ; risque 50 × 0,1 = 5.

**Étape 2.** Pénalités de B : coût 1 × 20 = 20 ; temps 2 × 8 = 16 ; risque 50 × 0,3 = 15.

**Étape 3.** Utilités : U(A) = 100 − 5 − 4 − 5 = 86 et U(B) = 120 − 20 − 16 − 15 = 69.

$$
U(A) = 100 - 5 - 4 - 5 = 86, \qquad U(B) = 120 - 20 - 16 - 15 = 69
$$

**Étape 4.** La meilleure utilité, 86, est positive : l'agent appelle A.

| | Bénéfice | − coût | − temps | − risque | U |
|---|---|---|---|---|---|
| A | 100 | 5 | 4 | 5 | 86 |
| B | 120 | 20 | 16 | 15 | 69 |

A gagne : B rapporte plus, mais pas assez pour payer son coût, sa lenteur et son risque (51 points de pénalités contre 14).

## Cas d'usage complexes, démontrés

Les probabilités, poids, coûts et volumes des quatre cas sont illustratifs. Les poids λ sont fixés et validés par l'équipe métier, avec leur unité.

### Cas 1 — Assureur auto et santé [ASSUR] : répondre, chercher la clause ou escalader une demande de remboursement

**Contexte.** Un assureur santé de Dubaï reçoit, par un assistant bilingue arabe et anglais, des questions de remboursement : taux de prise en charge d'une consultation, plafond restant, pièces à fournir. Pour chaque question, l'agent peut répondre tout de suite, chercher d'abord la clause de la police dans la base documentaire puis répondre, ou escalader à un gestionnaire. Tout refus de prise en charge est décidé par un humain. Volume illustratif : 3 000 questions par mois ; 1 point ≈ 1 AED.

**Données.**

- Une bonne réponse rapporte 50 points (client servi) ; une mauvaise en coûte 200 (remboursement à tort ou réclamation).
- Poids : λc = 1 par AED, λt = 0,5 point par seconde, λr = 50 ; le risque est la probabilité d'erreur.
- Répondre : confiance p = 0,8, coût 1 AED, temps 2 s.
- Chercher puis répondre : p = 0,95, coût 3 AED, temps 6 s.
- Escalader : bénéfice 45 (réponse juste mais plus tardive), coût 15 AED, temps 30 s, risque 0.
- Volume : 3 000 questions par mois.

**Calcul pas à pas.**

**Étape 1.** Bénéfices attendus (démonstration 1) : répondre, 0,8 × 50 − 0,2 × 200 = 40 − 40 = 0 ; chercher, 0,95 × 50 − 0,05 × 200 = 47,5 − 10 = 37,5 ; escalader, 45.

**Étape 2.** Utilités, pénalités comprises :

$$
U(\text{répondre}) = 0 - 1 - 0{,}5 \times 2 - 50 \times 0{,}2 = -12
$$

$$
U(\text{chercher}) = 37{,}5 - 3 - 0{,}5 \times 6 - 50 \times 0{,}05 = 37{,}5 - 3 - 3 - 2{,}5 = 29
$$

$$
U(\text{escalader}) = 45 - 15 - 0{,}5 \times 30 - 0 = 15
$$

**Étape 3.** Seuil de confiance pour répondre directement (démonstration 3) : Uᵣ(p) = 300p − 252 et Uᵥ = 29, d'où p* = 281/300 ≈ 0,93667.

**Décision de l'agent.** La meilleure utilité est 29, positive : l'agent cherche la clause puis répond. Il ne répondrait directement que si sa confiance calibrée dépassait 0,93667.

**Contre-calcul.** Une règle naïve qui ne regarde que le bénéfice attendu (0 ; 37,5 ; 45) escaladerait tout : elle perd 29 − 15 = 14 points par question, soit 3 000 × 14 = 42 000 AED par mois (illustratif), et elle envoie 3 000 questions par mois aux gestionnaires.

**Sensibilité.** L'escalade ne passerait devant que si son coût tombait sous 45 − 15 − 29 = 1 AED. La recherche reste meilleure que l'escalade tant que sa propre précision pc vérifie 300pc − 256 > 15, soit pc > 271/300 = 0,90333 (300pc − 256 est l'utilité de « chercher » en fonction de sa précision). Une hausse de 10 % de λr (55) donne U(chercher) = 37,5 − 3 − 3 − 2,75 = 28,75, U(répondre) = −13 et U(escalader) = 15 : la décision tient.

**En production.** Indicateur : la précision de « chercher puis répondre », mesurée chaque mois sur un échantillon audité ; alerte sous 0,92, au-dessus de la bascule 0,90333. On suit aussi la calibration de la confiance de réponse directe. Contrainte : l'assurance est supervisée par la CBUAE, qui attend un traitement équitable des sinistres ; l'agent informe et prépare, mais ne refuse jamais seul une prise en charge.

### Cas 2 — Groupe de construction [BTP] : payer, faire contrôler ou bloquer une facture de sous-traitant

**Contexte.** Un groupe de construction qui mène un grand chantier à Dubaï reçoit chaque mois des centaines de factures de sous-traitants. Un agent prépare la décision pour chacune : la payer automatiquement, la faire contrôler par un métreur, ou la bloquer en attendant des justificatifs. Payer sous 3 jours donne droit à un escompte de 1 % du montant hors taxes ; payer une facture fausse coûte cher à récupérer. Volume illustratif : 150 factures par mois au-dessus du montant de bascule calculé plus bas.

**Données.**

- Facture : 240 000 AED hors taxes (HT) ; TVA 5 %.
- Escompte : 1 % du HT si la facture est payée sous 3 jours.
- Poids : λc = 1 par AED ; λt = 150 AED par jour de délai (friction avec le sous-traitant) ; λr = 12 % du HT, le coût moyen d'une erreur non détectée, soit 28 800 AED ici.
- Payer automatiquement : coût 5 AED, délai 0,5 jour, risque d'erreur 0,03.
- Faire contrôler : coût 350 AED, délai 2 jours, risque 0,004.
- Bloquer : coût 120 AED, délai 8 jours (escompte perdu), risque 0,001.

**Calcul pas à pas.**

**Étape 1.** Contrôle déterministe de la TVA, avant toute décision : 0,05 × 240 000 = 12 000 AED, donc un total TTC de 252 000 AED.

**Étape 2.** Bénéfices : payer et contrôler restent sous 3 jours et gagnent l'escompte, 0,01 × 240 000 = 2 400 AED ; bloquer le perd (0).

**Étape 3.** Pénalités et utilités : payer, 5 + 150 × 0,5 + 0,03 × 28 800 = 5 + 75 + 864 = 944 ; contrôler, 350 + 300 + 115,2 = 765,2 ; bloquer, 120 + 1 200 + 28,8 = 1 348,8.

$$
U(\text{payer}) = 2\,400 - 944 = 1\,456, \qquad U(\text{contrôler}) = 2\,400 - 765{,}2 = 1\,634{,}8, \qquad U(\text{bloquer}) = -1\,348{,}8
$$

**Étape 4.** Règle générale en fonction du montant HT M, puisque l'escompte et λr sont proportionnels à M :

$$
U(\text{payer}) = 0{,}01\,M - 80 - 0{,}0036\,M = 0{,}0064\,M - 80, \qquad U(\text{contrôler}) = 0{,}00952\,M - 650
$$

Les deux s'égalent pour 0,00312 M = 570, soit M* = 182 692,31 AED.

**Décision de l'agent.** Le seuil est M* : on paie automatiquement sous 182 692 AED HT et l'on fait contrôler au-dessus. Ici M = 240 000 AED > M*, et 1 634,8 > 1 456 : l'agent envoie la facture au métreur.

**Contre-calcul.** La règle « toujours payer pour gagner l'escompte » perd 1 634,8 − 1 456 = 178,8 AED sur cette facture, soit 150 × 178,8 = 26 820 AED par mois sur les grosses factures (illustratif). La règle inverse, « toujours contrôler », détruit de la valeur sur les petites : pour une facture de 60 000 AED, payer vaut 0,0064 × 60 000 − 80 = 304 et contrôler 0,00952 × 60 000 − 650 = −78,8, une perte de 382,8 AED par facture.

**Sensibilité.** Outre le montant de bascule M*, le risque d'erreur du paiement automatique a sa propre bascule : à 240 000 AED, payer égale contrôler quand 2 400 − 80 − 28 800 r = 1 634,8, soit r = 685,2/28 800 = 0,02379. Si la qualité des factures s'améliore et que le taux d'erreur tombe sous 2,38 %, le paiement automatique redevient le bon choix pour ce montant.

**En production.** Indicateur : le taux d'erreur trouvé par les métreurs sur les factures contrôlées, qui estime r ; alerte sous 0,025, proche de la bascule 0,02379, pour réviser M*. Contraintes : chaque facture porte une TVA de 5 % vérifiée par un outil déterministe ; les retenues de garantie et les conditions d'escompte sont celles du contrat de sous-traitance (montants à confirmer avec le contrat).

### Cas 3 — Cabinet RH multi-émirats [RH] : choisir la visite médicale d'un nouveau salarié

**Contexte.** Un cabinet RH présent dans plusieurs émirats organise l'arrivée de salariés venus de l'étranger. Avant le visa de résidence, chaque salarié passe une visite médicale ; tant qu'elle n'est pas faite, il est payé sans pouvoir travailler. L'agent choisit entre plusieurs options de rendez-vous, dont une interdite par la politique du cabinet. Volume illustratif : 120 recrutements par mois.

**Données.**

- Salaire de base mensuel du salarié : 13 500 AED ; λt = salaire de base / 30 = 450 AED par jour d'attente (la même règle du salaire journalier que pour la fin de service).
- λr = 1 550 AED par reprogrammation certaine (3 jours perdus × 450 + 200 AED de frais) ; λc = 1 par AED.
- Bénéfice commun à toutes les options : 2 000 points (le recrutement aboutit).
- Options (coût en AED ; délai en jours ; risque de reprogrammation) : Dubaï standard (320 ; 2 ; 0,05) ; Sharjah (280 ; 1,5 trajet compris ; 0,10) ; Dubaï express (750 ; 0,25 ; 0,01) ; Abu Dhabi (350 ; 2,5 ; 0,06) ; coursier non agréé qui emporte les documents d'identité (100 ; 0,5 ; 0,02), interdit.
- Volume : 120 recrutements par mois.

**Calcul pas à pas.**

**Étape 1.** Contrainte (démonstration 4) : le coursier non agréé est retiré avant tout calcul. Sans ce filtre, il aurait la meilleure utilité, 2 000 − 100 − 225 − 31 = 1 644.

**Étape 2.** Dominance (démonstration 2) : Dubaï standard (320 ; 2 ; 0,05) est moins cher, plus rapide et moins risqué qu'Abu Dhabi (350 ; 2,5 ; 0,06) ; Abu Dhabi est retiré (son utilité, 2 000 − 350 − 1 125 − 93 = 432, le confirme).

**Étape 3.** Utilités des trois options restantes :

$$
U(\text{Dubaï standard}) = 2\,000 - 320 - 450 \times 2 - 1\,550 \times 0{,}05 = 2\,000 - 320 - 900 - 77{,}5 = 702{,}5
$$

$$
U(\text{Sharjah}) = 2\,000 - 280 - 450 \times 1{,}5 - 1\,550 \times 0{,}10 = 2\,000 - 280 - 675 - 155 = 890
$$

$$
U(\text{express}) = 2\,000 - 750 - 450 \times 0{,}25 - 1\,550 \times 0{,}01 = 2\,000 - 750 - 112{,}5 - 15{,}5 = 1\,122
$$

**Étape 4.** Le bénéfice commun 2 000 ne change aucune comparaison (démonstration 5, translation) : il ne sert qu'à garder des utilités positives.

**Décision de l'agent.** La meilleure utilité autorisée est 1 122 : l'agent réserve la visite express à Dubaï, parce qu'une journée d'attente de ce salarié coûte 450 AED, bien au-dessus de la bascule 264,4 AED calculée dans la démonstration 6.

**Contre-calcul.** La règle naïve « l'option autorisée la moins chère » choisit Sharjah (280 AED) : elle perd 1 122 − 890 = 232 AED par recrutement, soit 120 × 232 = 27 840 AED par mois (illustratif). Et une utilité qui traiterait l'interdiction comme un simple risque choisirait le coursier (1 644).

**Sensibilité.** La bascule λt* = 264,4 AED par jour correspond à un salaire de base de 264,4 × 30 = 7 932 AED. Pour un junior payé 6 000 AED (λt = 200), les utilités deviennent 1 202,5 (Dubaï standard), 1 265 (Sharjah) et 1 184,5 (express) : l'agent choisit Sharjah. Pour le salarié du cas, l'express reste en tête tant que son risque de reprogrammation reste sous 0,01 + 232/1 550 = 0,1597.

**En production.** Indicateur : le taux de reprogrammation des visites express, par mois ; alerte au-dessus de 0,10, loin sous la bascule 0,1597 mais déjà anormal. On suit aussi le délai entre l'offre acceptée et la visite. Contraintes : les copies de passeport et d'Emirates ID sont des données personnelles, protégées par la PDPL, sauf en zone DIFC ou ADGM, qui ont leurs propres lois ; le contrat et le permis de travail passent par le MOHRE, et la paie par le WPS ; les règles précises de visa sont à confirmer avec le texte en vigueur.

### Cas 4 — Agence immobilière [IMMO] : relancer un prospect sur plan par appel, message ou visite du show-room

**Contexte.** Une agence de Dubaï et d'Abu Dhabi commercialise des appartements sur plan. Pour chaque prospect entrant, un agent choisit le premier contact : appel immédiat d'un négociateur senior, message bilingue arabe et anglais suivi d'un appel junior, ou invitation à visiter le show-room. Les probabilités de vente viennent de l'historique de l'agence. Volume illustratif : 300 prospects par mois.

**Données.**

- Prix moyen : 1 800 000 AED ; commission de l'agence : 2 % (illustratif) ; frais de transfert DLD de 4 %, payés par l'acheteur et affichés dans le récapitulatif.
- Appel : probabilité de vente 0,12 ; coût 150 AED (temps du senior) ; délai 0 h ; risque de plainte 0,02.
- Message : probabilité 0,08 ; coût 20 AED ; délai 4 h ; risque 0,01.
- Show-room : probabilité 0,15 ; coût 400 AED (navette, accueil) ; délai 72 h ; risque 0,005.
- Poids : λc = 1 par AED ; λt = 8 AED par heure (le prospect refroidit) ; λr = 20 000 AED par plainte.
- Volume : 300 prospects par mois.

**Calcul pas à pas.**

**Étape 1.** Montants : commission 0,02 × 1 800 000 = 36 000 AED ; frais DLD 0,04 × 1 800 000 = 72 000 AED, à la charge de l'acheteur.

**Étape 2.** Bénéfices attendus (démonstration 1 avec ℓ = 0) : appel 0,12 × 36 000 = 4 320 ; message 0,08 × 36 000 = 2 880 ; show-room 0,15 × 36 000 = 5 400.

**Étape 3.** Pénalités : appel 150 + 0 + 0,02 × 20 000 = 550 ; message 20 + 8 × 4 + 0,01 × 20 000 = 20 + 32 + 200 = 252 ; show-room 400 + 8 × 72 + 0,005 × 20 000 = 400 + 576 + 100 = 1 076.

$$
U(\text{appel}) = 4\,320 - 550 = 3\,770, \qquad U(\text{message}) = 2\,880 - 252 = 2\,628, \qquad U(\text{show-room}) = 5\,400 - 1\,076 = 4\,324
$$

**Décision de l'agent.** La meilleure utilité est 4 324 : l'agent invite au show-room, avec un message de confirmation dans la langue du prospect.

**Contre-calcul.** Le ratio bénéfice/coût donne 4 320/150 = 28,8 pour l'appel, 2 880/20 = 144 pour le message et 5 400/400 = 13,5 pour le show-room : il choisit le message et perd 4 324 − 2 628 = 1 696 AED par prospect, soit 300 × 1 696 = 508 800 AED par mois (illustratif). La règle « appeler le plus vite possible » perd 4 324 − 3 770 = 554 AED par prospect, soit 166 200 AED par mois.

**Sensibilité.** Show-room et appel s'égalent quand 5 400 − 400 − 72 λt − 100 = 3 770, soit λt* = 1 130/72 = 15,694 AED par heure : si le prospect refroidit deux fois plus vite que prévu, l'appel immédiat gagne. Sur la conversion du show-room : 36 000 p − 1 076 = 3 770 donne p* = 4 846/36 000 = 0,13461. Une hausse de 10 % de λt (8,8) donne U(show-room) = 5 400 − 400 − 633,6 − 100 = 4 266,4, encore devant.

**En production.** Indicateur : le taux de conversion de chaque canal, par trimestre ; alerte si celui du show-room passe sous 0,14, proche de la bascule 0,13461. Contraintes : les frais DLD de 4 % sont affichés à l'acheteur ; la publicité sur plan et les messages commerciaux suivent les règles du DLD et de la RERA et le consentement prévu par la PDPL (à confirmer avec le texte en vigueur) ; l'agent priorise le travail de l'agence, il ne pousse pas l'acheteur.

## Entraînement sur feuille A4

**Exercice 1.** Un outil réussit avec p = 0,9 (gain 20) et échoue sinon (perte 30). Calculer 𝔼[B].

**Exercice 2.** Dans l'exemple simple, quel λt rendrait A et B égaux ?

**Exercice 3.** Dans le cas 1, si l'escalade coûte 5 au lieu de 15, change-t-elle la décision ?

**Exercice 4.** Montrer qu'une action de bénéfice 60, coût 2, temps 1 s, risque 0 domine une action de bénéfice 55, coût 4, temps 3 s, risque 0,05.

**Exercice 5.** Retrouver le seuil 281/300 en résolvant 300p − 252 = 29.

**Exercice 6 (modifier une donnée).** Dans le cas 2, la facture ne fait plus que 150 000 AED HT. Recalculer U(payer) et U(contrôler) et donner la décision.

**Exercice 7 (trouver l'erreur).** Un collègue calcule le seuil du cas 1 ainsi : « p > (Uᵥ − β)/α = (29 − 252)/300 = −0,743, donc l'agent doit toujours répondre directement. » Trouver l'erreur et la corriger.

**Exercice 8 (redémontrer de mémoire).** Redémontrer la démonstration 6 (une seule bascule par paire d'actions), puis l'appliquer au cas 3 pour un junior payé 6 000 AED de salaire de base : quelle option l'agent choisit-il ?

## Corrigé

**Exercice 1.** Démonstration 1 : 0,9 × 20 − 0,1 × 30 = 18 − 3 = 15.

**Exercice 2.** 100 − 5 − 2λ − 5 = 120 − 20 − 8λ − 15 ⟺ 90 − 2λ = 85 − 8λ ⟺ 6λ = −5 : aucun λ positif. Quel que soit le poids du temps, A reste devant, parce que A est aussi plus rapide : un λt plus grand ne fait qu'augmenter son avance.

**Exercice 3.** U = 45 − 5 − 0,5 × 30 = 45 − 5 − 15 = 25 < 29 : non, chercher puis répondre reste meilleur ; il faudrait un coût d'escalade sous 1 AED (cas 1, sensibilité).

**Exercice 4.** Bénéfice plus grand (60 ≥ 55), coût, temps et risque plus petits (2 ≤ 4, 1 ≤ 3, 0 ≤ 0,05) : dominance (démonstration 2). U(x) − U(y) = 5 + 2λc + 2λt + 0,05λr ≥ 5 > 0 pour tous les poids positifs.

**Exercice 5.** 300p − 252 = 29 ⟺ 300p = 281 ⟺ p = 281/300 ≈ 0,93667.

**Exercice 6.** Étape 4 du cas 2 avec M = 150 000 : U(payer) = 0,0064 × 150 000 − 80 = 960 − 80 = 880 et U(contrôler) = 0,00952 × 150 000 − 650 = 1 428 − 650 = 778. 880 > 778 : l'agent paie automatiquement, ce qui est cohérent avec M = 150 000 < M* = 182 692.

**Exercice 7.** L'erreur est un signe : on passe de αp − β > Uᵥ à αp > Uᵥ + β en ajoutant β aux deux membres, pas en le retranchant. Correct : p > (29 + 252)/300 = 281/300 ≈ 0,93667. Test de bon sens : à p = 0,8, Uᵣ = 300 × 0,8 − 252 = −12 < 29 ; répondre n'est donc pas « toujours » meilleur, et un seuil négatif est impossible pour une probabilité.

**Exercice 8.** Preuve : D(λt) = U(a) − U(b) = D₀ − λt (T(a) − T(b)) est affine, de pente non nulle si les délais diffèrent, donc s'annule une seule fois, en λt* = D₀/(T(a) − T(b)). Application : λt = 6 000/30 = 200 AED par jour. U(Dubaï standard) = 2 000 − 320 − 400 − 77,5 = 1 202,5 ; U(Sharjah) = 2 000 − 280 − 300 − 155 = 1 265 ; U(express) = 2 000 − 750 − 50 − 15,5 = 1 184,5. L'agent choisit Sharjah, ce qui est cohérent avec 75 < 200 < 264,4.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`proche(x, y, tol)`** — Cette petite fonction est le contrôleur des poids et mesures qui accepte une poussière sur le plateau de la balance : elle reçoit deux nombres et une tolérance, un milliardième par défaut, mesure la valeur absolue de leur écart et renvoie vrai s'il ne dépasse pas cette tolérance, faux sinon. Elle ne porte aucune théorie, mais elle permet aux `assert` de `main` et du cas 1 de comparer des flottants sans se laisser piéger par les arrondis, par exemple pour constater que le bénéfice attendu à p = 0,8 vaut bien 0 ou que le seuil vaut bien 281/300.

**`utilite(benefice, cout, temps, risque, lc, lt, lr)`** — On l'imagine en comptable qui tient une balance à quatre plateaux : elle reçoit le bénéfice attendu d'une action, son coût, son délai et son risque, ainsi que les trois prix λc, λt et λr qui convertissent coût, délai et risque dans la même monnaie que le bénéfice, avec 1, 2 et 50 par défaut. Elle retranche du bénéfice chacune des trois pénalités pondérées et renvoie l'utilité U(a) = E[B] − λc C − λt T − λr R, soit 86 pour l'outil A et 69 pour l'outil B de l'exemple simple ; toutes les démonstrations et tous les cas passent par elle.

**`benefice_attendu(p, gain, perte)`** — Cette fonction est le parieur prudent qui pèse ce qu'il gagne s'il a raison contre ce qu'il perd s'il se trompe : elle reçoit la probabilité de succès p, le gain en cas de succès et la perte en cas d'échec, refuse par une `ValueError` une probabilité hors de l'intervalle de 0 à 1, puis renvoie p × gain − (1 − p) × perte. Ce bénéfice est affine en p, comme le montre la démonstration 1 : il vaut 0 pour p = 0,8 et 37,5 pour p = 0,95 avec un gain de 50 et une perte de 200, et il alimente ensuite `utilite` dans les cas 1 et 4.

**`domine(x, y)`** — Celle-ci joue l'arbitre qui déclare un vainqueur sans même consulter les poids : elle reçoit deux actions décrites par le quadruplet bénéfice, coût, temps et risque, vérifie que x a un bénéfice au moins aussi grand que y et un coût, un temps et un risque au plus aussi grands, puis que les deux quadruplets diffèrent, donc que x est strictement meilleur quelque part. Elle renvoie vrai dans ce cas, et la démonstration 2 montre que le quadruplet 60, 2, 1, 0 domine 55, 4, 3, 0,05, tandis que les outils A et B ne se dominent pas ; le cas 3 s'en sert pour écarter Abu Dhabi.

**`choisir(utilites, interdites)`** — Cette fonction est le préposé à la décision qui applique d'abord le règlement, puis le calcul : elle reçoit un dictionnaire qui associe à chaque action son utilité et un ensemble facultatif d'actions interdites, retire celles-ci, puis renvoie « ne rien faire » s'il ne reste rien. Sinon, elle prend l'action autorisée de plus grande utilité et la renvoie si cette utilité est strictement positive, ou « ne rien faire » dans le cas contraire, ce qui explique que des temps saisis en millisecondes dans la démonstration 5 conduisent à ne rien faire ; tous les cas lui confient leur verdict.

**`seuil_confiance(pente, constante, u_v)`** — On la voit en géomètre qui cherche le point où une droite montante dépasse une hauteur donnée : elle reçoit la pente et la constante d'une utilité affine en p, de la forme pente × p − constante, ainsi que l'utilité u_v de l'action rivale, refuse une pente nulle ou négative par une `ValueError`, et renvoie la confiance minimale (u_v + constante)/pente au-delà de laquelle répondre devient préférable. Dans le cas 1, avec une pente de 300, une constante de 252 et une recherche qui vaut 29, elle donne 281/300, soit 0,93667, le seuil de la démonstration 3.

**`demo_1_affine()`** — Cette fonction est l'expérimentateur qui vérifie que le bénéfice attendu suit bien une droite : elle ne reçoit rien, calcule ce bénéfice à p = 0,8 et à p = 0,95 avec un gain de 50 et une perte de 200, soit 0 et 37,5, la pente 250 et le point mort p₀ = 200/250 = 0,8. Elle compare aussi une action à trois issues, 0,7 × 50 + 0,2 × 10 − 0,1 × 200 = 17, à la version binaire à p = 0,9, qui vaut 25, pour rappeler qu'aplatir les issues intermédiaires change le résultat ; elle imprime ces nombres et les renvoie dans un dictionnaire.

**`demo_2_dominance()`** — Celle-ci met la dominance à l'épreuve d'une batterie de réglages : elle ne reçoit rien, prend l'action x, de bénéfice 60, coût 2, temps 1 et risque 0, et l'action y, de bénéfice 55, coût 4, temps 3 et risque 0,05, puis calcule l'écart d'utilité pour neuf combinaisons de poids, λt valant 0, 1 ou 10 et λr 0, 50 ou 500. Le plus petit écart, 7, reste positif, comme le promet la dominance ; elle constate aussi que les outils A et B ne se dominent pas et que, sans aucun poids, B devance A de 20, imprime ces résultats et les renvoie.

**`demo_4_interdite()`** — Cette fonction raconte la tentation d'une action Z très lucrative mais interdite, qu'on voudrait écarter en gonflant le prix du risque : elle ne reçoit rien, calcule U(A) = 86 et U(Z), 447 avec λr = 50 et encore 97 avec λr = 400, puis le λr minimal de 411 qu'il faudrait pour que Z passe sous A. Elle montre ensuite qu'une variante Z′ au bénéfice de 1 000 repasse devant A, à 585, même avec ce λr relevé, et que seule une contrainte explicite, l'interdiction de Z dans `choisir`, ramène durablement le choix vers A ; elle imprime et renvoie ces nombres.

**`demo_5_invariance()`** — On y voit un traducteur qui change les unités sans changer le sens de la phrase : la fonction ne reçoit rien, vérifie qu'une transformation affine croissante, trois fois l'utilité moins 40, garde l'ordre entre A et B, puis exprime les coûts en dollars, 1,3615 et 5,4459, avec un λc ajusté à 3,6725, et retrouve exactement les utilités 86 et 69. Elle montre enfin l'erreur inverse : des temps saisis en millisecondes sans corriger λt donnent −3 910 et −15 915, et `choisir` conclut à ne rien faire ; elle imprime ces résultats et les renvoie.

**`utilites_rh(lt, lr, benefice)`** — Cette fonction est le tableau des options d'un service de ressources humaines qui doit faire passer la visite médicale d'un nouveau salarié : elle reçoit le prix du jour de délai λt, 450 par défaut, celui du risque de reprogrammation λr, 1 550 par défaut, et le bénéfice de la visite, 2 000 AED. Elle décrit cinq options par leur coût, leur délai en jours et leur risque, Dubaï standard, Sharjah, Dubaï express, Abu Dhabi et un coursier non agréé, applique `utilite` à chacune avec λc = 1 et renvoie le dictionnaire des utilités, soit 702,5, 890, 1 122, 432 et 1 644 avec les valeurs par défaut.

**`demo_6_bascule_poids()`** — Celle-ci suit le moment où un seul poids fait basculer la décision : elle ne reçoit rien, définit l'écart d'utilité entre Dubaï express et Sharjah en fonction de λt, trouve qu'il vaut −330,5 + 1,25 λt et s'annule à λt = 264,4, puis calcule la première bascule, à 75, où Dubaï standard et Sharjah s'égalent. Elle fait choisir l'option autorisée pour λt valant 50, 150 et 300, et obtient successivement Dubaï standard, Sharjah et Dubaï express ; elle renvoie aussi l'écart de 232 à λt = 450 et l'effet de 56,25 d'une hausse de 10 % de ce poids.

**`cas_1_remboursement_assur()`** — Cette fonction met en scène l'agent d'un assureur qui reçoit une demande de remboursement et doit répondre tout de suite, chercher d'abord la clause, ou escalader vers un gestionnaire, chaque seconde coûtant 0,5 point : elle ne reçoit rien, calcule les utilités −12, 29 et 15 et choisit de chercher, puis vérifie par un `assert` que le seuil de confiance de 0,93667 égalise bien répondre et chercher, avec 27 à 0,93 et 30 à 0,94. Elle montre qu'un choix fondé sur le seul bénéfice escaladerait et coûterait 42 000 AED par mois sur 3 000 demandes, calcule les bascules, une précision de 0,90333 pour la recherche, la recherche à 28,75 quand λr passe à 55 et la réponse à 3 avec une confiance de 0,85, puis renvoie le tout.

**`repondre(p)`** — Cette fonction interne vit dans `cas_1_remboursement_assur`, comme le brouillon où l'agent simule une réponse donnée sur-le-champ : elle reçoit la confiance p de l'agent dans sa réponse, calcule le bénéfice attendu avec un gain de 50 et une perte de 200, puis l'utilité avec un coût de 1, un délai de 2 secondes à 0,5 point la seconde et un risque égal à 1 − p. Elle renvoie cette utilité, qui vaut exactement 300p − 252, soit −12 à 0,8, 3 à 0,85, 27 à 0,93 et 30 à 0,94, et sert à la fois au choix du cas et à la vérification du seuil.

**`cas_2_facture_btp(montant, afficher)`** — On y suit l'agent comptable d'une entreprise de construction devant la facture d'un sous-traitant, qu'il peut payer automatiquement, faire contrôler par un métreur ou bloquer : la fonction reçoit le montant hors taxe, 240 000 AED par défaut, et un drapeau d'affichage, refuse un montant nul ou négatif par une `ValueError`, puis calcule un escompte de 1 %, une TVA de 5 % et un prix du risque égal à 12 % du montant, soit 28 800 AED. Avec λt = 150 par jour, elle obtient 1 456,0, 1 634,8 et −1 348,8 et choisit le contrôle, calcule le montant de bascule de 182 692,31 AED et le risque de bascule 0,02379, et renvoie ces résultats ; à 60 000 ou 150 000 AED, le paiement automatique l'emporte.

**`cas_3_visite_rh()`** — Cette fonction raconte le choix d'une visite médicale pour un nouveau salarié dont le jour d'absence vaut 13 500/30 = 450 AED : elle ne reçoit rien, calcule les cinq utilités avec `utilites_rh`, interdit le coursier non agréé, constate que Dubaï standard domine Abu Dhabi et que, sans contrainte, le coursier gagnerait à 1 644. Avec la contrainte, elle choisit Dubaï express, à 1 122, et chiffre à 27 840 AED par mois, sur 120 recrutements, la perte de la règle naïve qui retiendrait Sharjah, l'option autorisée la moins chère ; elle calcule le risque de bascule 0,1597, montre qu'un salarié junior, à λt = 200, irait à Sharjah, relie la bascule de 264,4 à un salaire de base de 7 932 AED, puis renvoie le tout.

**`cas_4_prospect_immo(lt, afficher)`** — Ici, une agence qui vend des appartements sur plan à 1 800 000 AED doit choisir le premier contact avec chaque prospect : un appel immédiat, un message, ou une invitation au show-room. La fonction reçoit le prix d'une heure de délai, 8 AED par défaut, et un drapeau d'affichage, calcule la commission de 2 %, 36 000 AED, les bénéfices attendus 4 320, 2 880 et 5 400, puis les utilités 3 770, 2 628 et 4 324, et choisit le show-room. Elle montre qu'un choix au ratio bénéfice sur coût prendrait le message et perdrait 508 800 AED par mois sur 300 prospects, qu'une règle de vitesse prendrait l'appel et en perdrait 166 200, calcule les bascules 15,694 AED par heure et 0,13461 pour la conversion du show-room, et renvoie ces résultats.

**`main()`** — C'est le chef d'orchestre de la fiche : il vérifie d'abord l'exemple simple, où l'outil A, à 86, l'emporte sur l'outil B, à 69, en recalculant chaque pénalité, puis appelle les démonstrations 1, 2, 4, 5 et 6 et contrôle leurs nombres, comme le point mort 0,8, l'écart minimal 7, le λr de 411 et la bascule 264,4. Il joue ensuite les quatre cas, vérifie que la décision du cas 2 bascule bien autour de 182 692 AED, puis recalcule le corrigé des exercices ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tout concorde.

```python
"""Démonstration 10 — utilité espérée : bénéfice affine, dominance, seuil de confiance, contrainte, invariance, bascule d'un poids, quatre cas aux Émirats."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def proche(x: float, y: float, tol: float = 1e-9) -> bool:
    return abs(x - y) <= tol


def utilite(benefice, cout, temps, risque, lc=1.0, lt=2.0, lr=50.0):
    """U(a) = E[B(a)] − λc C(a) − λt T(a) − λr R(a)."""
    return benefice - lc * cout - lt * temps - lr * risque


def benefice_attendu(p, gain, perte):
    """E[B] = p × gain − (1 − p) × perte (démonstration 1)."""
    if not 0.0 <= p <= 1.0:
        raise ValueError("probabilité hors de [0, 1]")
    return p * gain - (1 - p) * perte


def domine(x: tuple, y: tuple) -> bool:
    """x = (bénéfice, coût, temps, risque) domine y : au moins aussi bon partout, strictement quelque part."""
    au_moins = x[0] >= y[0] and all(a <= b for a, b in zip(x[1:], y[1:]))
    return au_moins and x != y


def choisir(utilites: dict[str, float], interdites: set[str] | None = None) -> str:
    """Action autorisée de plus grande utilité ; « ne rien faire » si elle n'est pas positive."""
    permises = {a: u for a, u in utilites.items() if a not in (interdites or set())}
    if not permises:
        return "ne rien faire"
    meilleure = max(permises, key=permises.get)
    return meilleure if permises[meilleure] > 0 else "ne rien faire"


def seuil_confiance(pente: float, constante: float, u_v: float) -> float:
    """Uᵣ(p) = pente × p − constante > u_v  ⟺  p > (u_v + constante) / pente (démonstration 3)."""
    if pente <= 0:
        raise ValueError("la pente doit être positive")
    return (u_v + constante) / pente


def demo_1_affine() -> dict:
    e80, e95 = benefice_attendu(0.8, 50, 200), benefice_attendu(0.95, 50, 200)
    p0 = 200 / (50 + 200)
    trois_issues = 0.7 * 50 + 0.2 * 10 + 0.1 * (-200)
    binaire = benefice_attendu(0.9, 50, 200)
    print(f"démo 1 : E[B](0.8) = {e80:.1f} ; E[B](0.95) = {e95:.1f} ; pente {50 + 200} ; p0 = {p0:.2f} ;"
          f" 3 issues {trois_issues:.0f} contre binaire {binaire:.0f}")
    return {"e80": e80, "e95": e95, "p0": p0, "trois": trois_issues, "binaire": binaire}


def demo_2_dominance() -> dict:
    x, y = (60, 2, 1, 0), (55, 4, 3, 0.05)
    ecarts = [utilite(*x, lt=lt, lr=lr) - utilite(*y, lt=lt, lr=lr)
              for lt in (0.0, 1.0, 10.0) for lr in (0.0, 50.0, 500.0)]
    b_sans_poids = utilite(120, 20, 8, 0.3, lc=0, lt=0, lr=0) - utilite(100, 5, 2, 0.1, lc=0, lt=0, lr=0)
    print(f"démo 2 : x domine y = {domine(x, y)} ; plus petit écart U(x) − U(y) = {min(ecarts):.0f} ;"
          f" A domine B = {domine((100, 5, 2, 0.1), (120, 20, 8, 0.3))} ; sans poids, B − A = {b_sans_poids:.0f}")
    return {"domine": domine(x, y), "ecart_min": min(ecarts), "b_sans_poids": b_sans_poids}


def demo_4_interdite() -> dict:
    u_a = utilite(100, 5, 2, 0.1)
    u_z = utilite(500, 1, 1, 1.0)
    u_z400 = utilite(500, 1, 1, 1.0, lr=400)
    lr_min = 500 - 1 - 2 - u_a
    u_z2 = utilite(1000, 1, 1, 1.0, lr=lr_min + 1)
    choix = choisir({"A": u_a, "Z": u_z}, interdites={"Z"})
    print(f"démo 4 : U(Z) = {u_z:.0f} (λr = 50), {u_z400:.0f} (λr = 400) contre U(A) = {u_a:.0f} ; λr minimal {lr_min:.0f} ;"
          f" Z′ (bénéfice 1000) {u_z2:.0f} ; choix avec contrainte : {choix}")
    return {"u_z": u_z, "u_z400": u_z400, "lr_min": lr_min, "u_z2": u_z2, "choix": choix}


def demo_5_invariance() -> dict:
    ua, ub = utilite(100, 5, 2, 0.1), utilite(120, 20, 8, 0.3)
    k, c = 3.0, -40.0
    meme_ordre = (k * ua + c > k * ub + c) == (ua > ub)
    usd = 3.6725
    ua_usd = utilite(100, 5 / usd, 2, 0.1, lc=usd)
    ub_usd = utilite(120, 20 / usd, 8, 0.3, lc=usd)
    ua_ms, ub_ms = utilite(100, 5, 2000, 0.1), utilite(120, 20, 8000, 0.3)
    choix_ms = choisir({"A": ua_ms, "B": ub_ms})
    print(f"démo 5 : coûts en USD {5 / usd:.4f} et {20 / usd:.4f}, λc = {usd} → U = {ua_usd:.0f} et {ub_usd:.0f} ;"
          f" temps en ms sans changer λt → {ua_ms:.0f} et {ub_ms:.0f} → {choix_ms}")
    return {"meme_ordre": meme_ordre, "ua_usd": ua_usd, "ub_usd": ub_usd, "ua_ms": ua_ms, "ub_ms": ub_ms,
            "choix_ms": choix_ms}


def utilites_rh(lt: float = 450.0, lr: float = 1550.0, benefice: float = 2000.0) -> dict[str, float]:
    """Cas 3 : (coût AED, délai en jours, risque de reprogrammation) de chaque option de visite médicale."""
    options = {"Dubaï standard": (320, 2.0, 0.05), "Sharjah": (280, 1.5, 0.10), "Dubaï express": (750, 0.25, 0.01),
               "Abu Dhabi": (350, 2.5, 0.06), "coursier non agréé": (100, 0.5, 0.02)}
    return {nom: utilite(benefice, c, t, r, lc=1.0, lt=lt, lr=lr) for nom, (c, t, r) in options.items()}


def demo_6_bascule_poids() -> dict:
    diff = lambda lt: utilites_rh(lt)["Dubaï express"] - utilites_rh(lt)["Sharjah"]
    d0 = diff(0.0)
    pente = diff(1.0) - diff(0.0)
    lt_bascule = -d0 / pente
    choix = {lt: choisir(utilites_rh(lt), {"coursier non agréé"}) for lt in (50.0, 150.0, 300.0)}
    b1 = (-320 - 77.5 + 280 + 155) / (2.0 - 1.5)          # Dubaï standard = Sharjah
    print(f"démo 6 : U(express) − U(Sharjah) = {d0:.1f} + {pente:.2f} λt ; bascule λt = {lt_bascule:.1f} ;"
          f" première bascule {b1:.0f} ; choix à 50, 150, 300 : {', '.join(choix.values())}")
    return {"d0": d0, "pente": pente, "lt_bascule": lt_bascule, "b1": b1, "choix": choix,
            "diff450": diff(450.0), "effet_10": diff(495.0) - diff(450.0)}


def cas_1_remboursement_assur() -> dict:
    """[ASSUR] répondre, chercher la clause puis répondre, ou escalader (λt = 0,5 point par seconde)."""

    def repondre(p):
        return utilite(benefice_attendu(p, 50, 200), 1, 2, 1 - p, lt=0.5)

    chercher = utilite(benefice_attendu(0.95, 50, 200), 3, 6, 0.05, lt=0.5)
    escalader = utilite(45, 15, 30, 0, lt=0.5)
    u = {"répondre": repondre(0.8), "chercher": chercher, "escalader": escalader}
    choix = choisir(u)
    seuil = seuil_confiance(300, 252, chercher)
    assert abs(repondre(seuil) - chercher) < 1e-9 and proche(seuil, 281 / 300)
    naif = max({"répondre": benefice_attendu(0.8, 50, 200), "chercher": benefice_attendu(0.95, 50, 200),
                "escalader": 45}.items(), key=lambda kv: kv[1])[0]
    perte_naive = (u[choix] - u[naif]) * 3000
    p_chercher = 271 / 300                                   # 300 p − 256 = 15
    lr55 = {"répondre": utilite(0, 1, 2, 0.2, lt=0.5, lr=55), "chercher": utilite(37.5, 3, 6, 0.05, lt=0.5, lr=55),
            "escalader": utilite(45, 15, 30, 0, lt=0.5, lr=55)}
    print(f"cas 1 : répondre {u['répondre']:.0f} ; chercher {chercher:.0f} ; escalader {escalader:.0f} → {choix} ;"
          f" seuil {seuil:.5f} ; U(0.93) = {repondre(0.93):.0f}, U(0.94) = {repondre(0.94):.0f}")
    print(f"        naïf (bénéfice seul) → {naif} : {perte_naive:,.0f} AED/mois ; bascule coût escalade {45 - 15 - chercher:.0f} ;"
          f" précision de « chercher » {p_chercher:.5f} ; λr = 55 → {lr55['chercher']:.2f} ; calibration 0.85 → {repondre(0.85):.0f}")
    return {"u": u, "choix": choix, "seuil": seuil, "u093": repondre(0.93), "u094": repondre(0.94), "naif": naif,
            "perte_naive": perte_naive, "p_chercher": p_chercher, "lr55": lr55, "u085": repondre(0.85),
            "pente": repondre(1.0) - repondre(0.0), "constante": -repondre(0.0)}


def cas_2_facture_btp(montant: float = 240000.0, afficher: bool = True) -> dict:
    """[BTP] payer automatiquement, faire contrôler par un métreur, ou bloquer une facture de sous-traitant."""
    if montant <= 0:
        raise ValueError("montant positif attendu")
    escompte, tva = 0.01 * montant, 0.05 * montant
    lr = 0.12 * montant                                       # coût moyen d'une erreur non détectée
    u = {"payer": utilite(escompte, 5, 0.5, 0.03, lt=150, lr=lr),
         "contrôler": utilite(escompte, 350, 2.0, 0.004, lt=150, lr=lr),
         "bloquer": utilite(0, 120, 8.0, 0.001, lt=150, lr=lr)}
    choix = choisir(u)
    m_bascule = (650 - 80) / (0.00952 - 0.0064)
    r_bascule = (escompte - 5 - 75 - u["contrôler"]) / lr
    if afficher:
        print(f"cas 2 : HT {montant:,.0f} ; TVA {tva:,.0f} ; TTC {montant + tva:,.0f} ; escompte {escompte:,.0f} ;"
              f" λr {lr:,.0f}")
        print(f"        payer {u['payer']:.1f} ; contrôler {u['contrôler']:.1f} ; bloquer {u['bloquer']:.1f} → {choix} ;"
              f" bascule HT {m_bascule:,.2f} ; risque de bascule {r_bascule:.5f}")
    return {"u": u, "choix": choix, "tva": tva, "escompte": escompte, "lr": lr, "m_bascule": m_bascule,
            "r_bascule": r_bascule}


def cas_3_visite_rh() -> dict:
    """[RH] visite médicale d'un nouveau salarié : contrainte, dominance, puis utilité."""
    lt = 13500 / 30
    u = utilites_rh(lt)
    interdites = {"coursier non agréé"}
    options = {"Dubaï standard": (2000, 320, 2.0, 0.05), "Abu Dhabi": (2000, 350, 2.5, 0.06)}
    domine_ad = domine(options["Dubaï standard"], options["Abu Dhabi"])
    choix = choisir(u, interdites)
    choix_sans_contrainte = choisir(u)
    moins_cher = "Sharjah"
    perte_naive = (u[choix] - u[moins_cher]) * 120
    r_bascule = (u["Dubaï express"] - u["Sharjah"]) / 1550 + 0.01
    u_junior = utilites_rh(6000 / 30)
    print(f"cas 3 : λt = {lt:.0f} ; " + " ; ".join(f"{k} {v:.1f}" for k, v in u.items()))
    print(f"        Dubaï standard domine Abu Dhabi = {domine_ad} ; sans contrainte → {choix_sans_contrainte} ;"
          f" avec → {choix} ; naïf « moins cher » {perte_naive:,.0f} AED/mois ; risque de bascule {r_bascule:.4f}")
    print(f"        junior (base 6000, λt = 200) → {choisir(u_junior, interdites)} ;"
          f" bascule λt 264.4 ↔ salaire de base {264.4 * 30:,.0f} AED")
    return {"lt": lt, "u": u, "domine_ad": domine_ad, "choix": choix, "choix_sc": choix_sans_contrainte,
            "perte_naive": perte_naive, "r_bascule": r_bascule, "u_junior": u_junior,
            "choix_junior": choisir(u_junior, interdites)}


def cas_4_prospect_immo(lt: float = 8.0, afficher: bool = True) -> dict:
    """[IMMO] prospect sur plan : appel immédiat, message automatique, ou invitation au show-room."""
    prix = 1800000
    commission, frais_dld = 0.02 * prix, 0.04 * prix
    canaux = {"appel": (0.12, 150, 0, 0.02), "message": (0.08, 20, 4, 0.01), "show-room": (0.15, 400, 72, 0.005)}
    eb = {k: benefice_attendu(p, commission, 0) for k, (p, _, _, _) in canaux.items()}
    u = {k: utilite(eb[k], c, t, r, lc=1.0, lt=lt, lr=20000) for k, (_, c, t, r) in canaux.items()}
    choix = choisir(u)
    ratio = {k: eb[k] / canaux[k][1] for k in canaux}
    choix_ratio = max(ratio, key=ratio.get)
    perte_ratio = (u[choix] - u[choix_ratio]) * 300
    perte_vitesse = (u[choix] - u["appel"]) * 300
    lt_bascule = (eb["show-room"] - 400 - 100 - u["appel"]) / 72
    p_bascule = (u["appel"] + 400 + 576 + 100) / commission
    if afficher:
        print(f"cas 4 : commission {commission:,.0f} ; frais DLD {frais_dld:,.0f} ; E[B] "
              + " ; ".join(f"{k} {v:,.0f}" for k, v in eb.items()))
        print(f"        U : " + " ; ".join(f"{k} {v:,.0f}" for k, v in u.items()) + f" → {choix} ;"
              f" ratio → {choix_ratio} ({perte_ratio:,.0f} AED/mois) ; vitesse → appel ({perte_vitesse:,.0f} AED/mois)")
        print(f"        bascules λt = {lt_bascule:.3f} AED/h, p(show-room) = {p_bascule:.5f}")
    return {"eb": eb, "u": u, "choix": choix, "ratio": ratio, "choix_ratio": choix_ratio, "perte_ratio": perte_ratio,
            "perte_vitesse": perte_vitesse, "lt_bascule": lt_bascule, "p_bascule": p_bascule,
            "commission": commission, "frais_dld": frais_dld}


def main() -> None:
    # Exemple simple
    ua, ub = utilite(100, 5, 2, 0.1), utilite(120, 20, 8, 0.3)
    print(f"outil A {ua:.0f} ; outil B {ub:.0f} ; choix : {choisir({'A': ua, 'B': ub})}")
    assert (round(ua), round(ub)) == (86, 69) and choisir({"A": ua, "B": ub}) == "A"
    assert [1 * 5, 2 * 2, 50 * 0.1] == [5, 4, 5] and [1 * 20, 2 * 8, round(50 * 0.3)] == [20, 16, 15]
    assert 100 - 5 == 95 and 95 - 4 == 91 and 120 - 20 == 100 and 100 - 16 == 84
    assert (120 - 100, 20 - 5, 16 - 4, 15 - 5, round(ua - ub)) == (20, 15, 12, 10, 17) and (20 + 16 + 15, 5 + 4 + 5) == (51, 14)

    d1 = demo_1_affine()
    assert proche(d1["e80"], 0) and proche(d1["e95"], 37.5) and proche(d1["p0"], 0.8)
    assert proche(d1["trois"], 17) and proche(d1["binaire"], 25) and proche(benefice_attendu(0.81, 50, 200), 2.5)
    assert proche(d1["binaire"] - d1["trois"], 8) and proche(0.95 * 250, 237.5)
    d2 = demo_2_dominance()
    assert d2["domine"] and d2["ecart_min"] == 7 and d2["b_sans_poids"] == 20
    assert not domine((100, 5, 2, 0.1), (120, 20, 8, 0.3)) and not domine((120, 20, 8, 0.3), (100, 5, 2, 0.1))
    d4 = demo_4_interdite()
    assert round(d4["u_z"]) == 447 and round(d4["u_z400"]) == 97 and round(d4["lr_min"]) == 411
    assert d4["u_z2"] > ua and round(d4["u_z2"]) == 585 and d4["choix"] == "A"
    d5 = demo_5_invariance()
    assert d5["meme_ordre"] and proche(d5["ua_usd"], ua) and proche(d5["ub_usd"], ub)
    assert round(5 / 3.6725, 4) == 1.3615 and round(20 / 3.6725, 4) == 5.4459
    assert round(d5["ua_ms"]) == -3910 and round(d5["ub_ms"]) == -15915 and d5["choix_ms"] == "ne rien faire"
    assert proche(3 * ua - 40, 218) and proche(3 * ub - 40, 167)
    d6 = demo_6_bascule_poids()
    assert round(d6["d0"], 1) == -330.5 and round(d6["pente"], 2) == 1.25 and round(d6["lt_bascule"], 1) == 264.4
    assert round(d6["b1"]) == 75 and list(d6["choix"].values()) == ["Dubaï standard", "Sharjah", "Dubaï express"]
    assert 750 - 280 == 470 and proche(155 - 15.5, 139.5) and proche(470 - 139.5, 330.5) and proche(330.5 / 1.25, 264.4)
    assert round(d6["diff450"]) == 232 and round(d6["effet_10"], 2) == 56.25
    assert round((765.5 - 397.5) / 1.75, 2) == 210.29

    c1 = cas_1_remboursement_assur()
    u1 = c1["u"]
    assert (round(u1["répondre"]), round(u1["chercher"]), round(u1["escalader"])) == (-12, 29, 15)
    assert c1["choix"] == "chercher" and round(c1["seuil"], 5) == 0.93667
    assert round(c1["pente"]) == 300 and round(c1["constante"]) == 252
    assert round(c1["u093"]) == 27 and round(c1["u094"]) == 30 and c1["naif"] == "escalader"
    assert round(c1["perte_naive"]) == 42000 and round(c1["p_chercher"], 5) == 0.90333
    assert round(c1["lr55"]["chercher"], 2) == 28.75 and round(c1["lr55"]["répondre"]) == -13
    assert choisir(c1["lr55"]) == "chercher" and round(c1["u085"]) == 3
    assert round(300 * 0.95 - 252) == 33 and round(29 - c1["u085"]) == 26 and round(300 * 0.95 - 256) == 29
    assert (50 + 200 + 50, 200 + 50 + 1 + 1) == (300, 252) and round(279 - 252) == 27
    assert proche(0.95 * 50 - 0.05 * 200, 37.5) and proche(0.8 * 50 - 0.2 * 200, 0)
    c2 = cas_2_facture_btp()
    u2 = c2["u"]
    assert c2["tva"] == 12000 and c2["escompte"] == 2400 and round(c2["lr"]) == 28800
    assert (round(u2["payer"], 1), round(u2["contrôler"], 1), round(u2["bloquer"], 1)) == (1456.0, 1634.8, -1348.8)
    assert c2["choix"] == "contrôler" and round(c2["m_bascule"], 2) == 182692.31 and round(c2["r_bascule"], 5) == 0.02379
    assert proche(0.03 * 28800, 864) and proche(0.004 * 28800, 115.2) and proche(0.001 * 28800, 28.8)
    assert round((u2["contrôler"] - u2["payer"]) * 150) == 26820 and round(u2["contrôler"] - u2["payer"], 1) == 178.8
    assert round(2400 - u2["payer"], 1) == 944.0 and round(2400 - u2["contrôler"], 1) == 765.2
    assert round(0.00952 - 0.0064, 5) == 0.00312 and round(2400 - 80 - u2["contrôler"], 1) == 685.2
    petit = cas_2_facture_btp(60000, afficher=False)
    assert round(petit["u"]["payer"], 1) == 304.0 and round(petit["u"]["contrôler"], 1) == -78.8
    assert petit["choix"] == "payer" and round(petit["u"]["payer"] - petit["u"]["contrôler"], 1) == 382.8
    for m in (150000.0, 182000.0, 183000.0, 240000.0):   # la décision bascule à 182 692 AED
        attendu = "payer" if m < c2["m_bascule"] else "contrôler"
        assert cas_2_facture_btp(m, afficher=False)["choix"] == attendu
    c3 = cas_3_visite_rh()
    u3 = c3["u"]
    assert c3["lt"] == 450 and [round(u3[k], 1) for k in u3] == [702.5, 890.0, 1122.0, 432.0, 1644.0]
    assert c3["domine_ad"] and c3["choix"] == "Dubaï express" and c3["choix_sc"] == "coursier non agréé"
    assert round(c3["perte_naive"]) == 27840 and round(c3["r_bascule"], 4) == 0.1597 and proche(c3["r_bascule"], 247.5 / 1550)
    assert [round(c3["u_junior"][k], 1) for k in ("Dubaï standard", "Sharjah", "Dubaï express")] == [1202.5, 1265.0, 1184.5]
    assert c3["choix_junior"] == "Sharjah" and round(264.4 * 30) == 7932 and 3 * 450 + 200 == 1550
    assert (450 * 0.5, 1550 * 0.02, 450 * 2.5, round(1550 * 0.06)) == (225, 31, 1125, 93) and 1122 - 890 == 232
    assert (2 * 200, 1.5 * 200, 0.25 * 200) == (400, 300, 50) and (450 * 0.25, 1550 * 0.01) == (112.5, 15.5)
    c4 = cas_4_prospect_immo()
    assert c4["commission"] == 36000 and c4["frais_dld"] == 72000
    assert [round(c4["eb"][k]) for k in c4["eb"]] == [4320, 2880, 5400]
    assert [round(c4["u"][k]) for k in c4["u"]] == [3770, 2628, 4324] and c4["choix"] == "show-room"
    assert [round(c4["ratio"][k], 1) for k in c4["ratio"]] == [28.8, 144.0, 13.5] and c4["choix_ratio"] == "message"
    assert round(c4["perte_ratio"]) == 508800 and round(c4["perte_vitesse"]) == 166200
    assert round(c4["lt_bascule"], 3) == 15.694 and round(c4["p_bascule"], 5) == 0.13461
    c4b = cas_4_prospect_immo(lt=8.8, afficher=False)
    assert round(c4b["u"]["show-room"], 1) == 4266.4 and c4b["choix"] == "show-room" and round(8.8 * 72, 1) == 633.6
    assert round(1130 / 72, 3) == 15.694 and round(4846 / 36000, 5) == 0.13461 and 4324 - 2628 == 1696 and 4324 - 3770 == 554
    assert (150 + 400, 20 + 32 + 200, 400 + 576 + 100) == (550, 252, 1076)

    print("Corrigé")
    ex2 = (120 - 20 - 15) - (100 - 5 - 5)                    # 6λ = −5 : pas de λt positif
    ex3 = utilite(45, 5, 30, 0, lt=0.5)
    ex6 = cas_2_facture_btp(150000, afficher=False)
    faux = (u1["chercher"] - 252) / 300
    ex8 = {k: round(v, 1) for k, v in c3["u_junior"].items() if k in ("Dubaï standard", "Sharjah", "Dubaï express")}
    print(f"  ex1 {benefice_attendu(0.9, 20, 30):.0f} ; ex2 6λ = {ex2} ; ex3 {ex3:.0f} < {u1['chercher']:.0f} ;"
          f" ex5 p = {281 / 300:.5f}")
    print(f"  ex6 payer {ex6['u']['payer']:.0f}, contrôler {ex6['u']['contrôler']:.0f} → {ex6['choix']} ;"
          f" ex7 faux seuil {faux:.3f} ; ex8 {ex8}")
    assert round(benefice_attendu(0.9, 20, 30)) == 15 and ex2 == -5 and round(ex3) == 25 and ex3 < u1["chercher"]
    assert all(utilite(100, 5, 2, 0.1, lt=lt) > utilite(120, 20, 8, 0.3, lt=lt) for lt in (0, 1, 5, 50))
    assert round(ex6["u"]["payer"]) == 880 and round(ex6["u"]["contrôler"]) == 778 and ex6["choix"] == "payer"
    assert round(0.0064 * 150000) == 960 and round(0.00952 * 150000) == 1428 and round(300 * 0.8 - 252) == -12
    assert round(faux, 3) == -0.743 and c1["u"]["répondre"] < u1["chercher"]
    for lt in (0.0, 1.0, 10.0):                                                      # dominance, ex. 4
        for lr in (0.0, 50.0, 500.0):
            assert utilite(60, 2, 1, 0, lt=lt, lr=lr) >= utilite(55, 4, 3, 0.05, lt=lt, lr=lr)
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
outil A 86 ; outil B 69 ; choix : A
démo 1 : E[B](0.8) = 0.0 ; E[B](0.95) = 37.5 ; pente 250 ; p0 = 0.80 ; 3 issues 17 contre binaire 25
démo 2 : x domine y = True ; plus petit écart U(x) − U(y) = 7 ; A domine B = False ; sans poids, B − A = 20
démo 4 : U(Z) = 447 (λr = 50), 97 (λr = 400) contre U(A) = 86 ; λr minimal 411 ; Z′ (bénéfice 1000) 585 ; choix avec contrainte : A
démo 5 : coûts en USD 1.3615 et 5.4459, λc = 3.6725 → U = 86 et 69 ; temps en ms sans changer λt → -3910 et -15915 → ne rien faire
démo 6 : U(express) − U(Sharjah) = -330.5 + 1.25 λt ; bascule λt = 264.4 ; première bascule 75 ; choix à 50, 150, 300 : Dubaï standard, Sharjah, Dubaï express
cas 1 : répondre -12 ; chercher 29 ; escalader 15 → chercher ; seuil 0.93667 ; U(0.93) = 27, U(0.94) = 30
        naïf (bénéfice seul) → escalader : 42,000 AED/mois ; bascule coût escalade 1 ; précision de « chercher » 0.90333 ; λr = 55 → 28.75 ; calibration 0.85 → 3
cas 2 : HT 240,000 ; TVA 12,000 ; TTC 252,000 ; escompte 2,400 ; λr 28,800
        payer 1456.0 ; contrôler 1634.8 ; bloquer -1348.8 → contrôler ; bascule HT 182,692.31 ; risque de bascule 0.02379
cas 3 : λt = 450 ; Dubaï standard 702.5 ; Sharjah 890.0 ; Dubaï express 1122.0 ; Abu Dhabi 432.0 ; coursier non agréé 1644.0
        Dubaï standard domine Abu Dhabi = True ; sans contrainte → coursier non agréé ; avec → Dubaï express ; naïf « moins cher » 27,840 AED/mois ; risque de bascule 0.1597
        junior (base 6000, λt = 200) → Sharjah ; bascule λt 264.4 ↔ salaire de base 7,932 AED
cas 4 : commission 36,000 ; frais DLD 72,000 ; E[B] appel 4,320 ; message 2,880 ; show-room 5,400
        U : appel 3,770 ; message 2,628 ; show-room 4,324 → show-room ; ratio → message (508,800 AED/mois) ; vitesse → appel (166,200 AED/mois)
        bascules λt = 15.694 AED/h, p(show-room) = 0.13461
Corrigé
  ex1 15 ; ex2 6λ = -5 ; ex3 25 < 29 ; ex5 p = 0.93667
  ex6 payer 880, contrôler 778 → payer ; ex7 faux seuil -0.743 ; ex8 {'Dubaï standard': 1202.5, 'Sharjah': 1265.0, 'Dubaï express': 1184.5}
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme filtre les actions interdites, retire les actions dominées, choisit parmi les autres celle d'utilité maximale (ou ne fait rien si elle n'est pas positive), puis calcule les seuils où la décision change.

```text
ALGORITHME ChoisirAction
ENTRÉES : actions a₁ … aₙ avec (p, gain, perte, coût, temps, risque), poids λc, λt, λr, ensemble des actions interdites
SORTIE  : action choisie, ou « ne rien faire »

  retirer les actions interdites                 (contrainte, démonstration 4)
  retirer les actions dominées par une autre      (démonstration 2, facultatif)
  POUR CHAQUE action a restante FAIRE
      bénéfice ← p × gain − (1 − p) × perte
      U[a] ← bénéfice − λc × coût − λt × temps − λr × risque
  FIN POUR
  a* ← l'action de plus grand U
  SI U[a*] ≤ 0 ALORS RETOURNER « ne rien faire »
  RETOURNER a*

ALGORITHME SeuilDeConfiance
ENTRÉES : Uᵣ(p) = α × p − β avec α > 0, utilité fixe Uᵥ
  SI α ≤ 0 ALORS ERREUR
  RETOURNER (Uᵥ + β) / α

ALGORITHME BasculeDUnPoids
ENTRÉES : deux actions a et b, D₀ = U(a) − U(b) sans les termes en λt, délais T(a) ≠ T(b)
  RETOURNER D₀ / (T(a) − T(b))
```

**Complexité.** O(n) pour les n utilités et le maximum ; le filtre des interdictions coûte O(n) et passe avant la boucle : c'est une contrainte, pas un terme de l'utilité (démonstration 4). Le retrait des actions dominées compare toutes les paires, O(n²) avec 4 critères, ce qui reste négligeable pour quelques dizaines d'outils. Le seuil de confiance et chaque valeur de bascule coûtent O(1).

**Du squelette au code.** Le bénéfice est `benefice_attendu(p, gain, perte)`, qui lève `ValueError` si p sort de [0 ; 1], et l'utilité `utilite(benefice, cout, temps, risque, lc, lt, lr)`. Le filtre des interdictions et le maximum sont `choisir(utilites, interdites)`, la dominance `domine(x, y)` et le seuil `seuil_confiance(pente, constante, u_v)`. Les trois options du cas 1 sont `repondre(p)`, `chercher` et `escalader` ; le seuil vaut `281 / 300`, vérifié par `abs(repondre(seuil) - chercher) < 1e-9`. Les démonstrations sont rejouées par `demo_1_affine`, `demo_2_dominance`, `demo_4_interdite`, `demo_5_invariance` et `demo_6_bascule_poids` ; les quatre cas par `cas_1_remboursement_assur`, `cas_2_facture_btp`, `cas_3_visite_rh` (avec `utilites_rh(lt, lr, benefice)` pour les options de visite) et `cas_4_prospect_immo`.
