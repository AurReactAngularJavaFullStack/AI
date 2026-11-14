# 31 — Adam : démonstrations

> Fiche : [31 — Adam](<../../Images/08-Entrainement/31_adam.md>) · Image : `31_adam.jpg` · Leçon : [Étape 74 — Optimiseur Adam](<../../12-Production-Couts-Optimisation/74-Optimiseur-Adam.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
\theta_{t+1} = \theta_t - \frac{\alpha \times \hat{m}_t}{\sqrt{\hat{v}_t} + \varepsilon}
$$

Adam garde, pour chaque paramètre, deux moyennes mobiles du gradient g : la moyenne m (la direction) et la moyenne des carrés v (l'ampleur), corrigées de leur biais de départ :

$$
m_t = \beta_1 m_{t-1} + (1 - \beta_1)\, g_t, \qquad v_t = \beta_2 v_{t-1} + (1 - \beta_2)\, g_t^2
$$

$$
\hat m_t = \frac{m_t}{1 - \beta_1^t}, \qquad \hat v_t = \frac{v_t}{1 - \beta_2^t}
$$

Valeurs usuelles : α = 0,001, β₁ = 0,9, β₂ = 0,999, ε = 10⁻⁸, m₀ = v₀ = 0.

## Les symboles, un par un

$$
t
$$

Le numéro du pas, compté à partir de 1 ; la correction de biais en dépend. Variable `t`, troisième composante de l'état (m, v, t) renvoyé par `adam_etat`.

$$
\theta_t
$$

Les paramètres (les poids) après t pas : un réel par paramètre. Le programme ne tient pas θ : il renvoie les pas, que l'on retranche à θ.

$$
g_t
$$

Le gradient de la perte au pas t, pour un paramètre (fiche 34) ; sa taille dépend de l'échelle de l'entrée. Variable `g`, liste `gradients`.

$$
m_t
$$

Le premier moment : moyenne mobile exponentielle des gradients, dans l'unité du gradient ; m₀ = 0. Variable `m`.

$$
v_t
$$

Le second moment : moyenne mobile exponentielle des gradients au carré, toujours ≥ 0, dans l'unité du gradient au carré ; v₀ = 0. Variable `v`.

$$
\beta_1
$$

Le taux d'oubli du premier moment, dans [0 ; 1[, 0,9 par défaut : le gradient d'il y a j pas pèse (1 − β₁)β₁ʲ. Constante `B1`, argument `b1`.

$$
\beta_2
$$

Le taux d'oubli du second moment, dans [0 ; 1[, 0,999 par défaut ; sa mémoire moyenne vaut β₂/(1 − β₂), environ 999 pas. Constante `B2`, argument `b2`.

$$
\hat m_t
$$

Le premier moment corrigé du biais de départ, mₜ/(1 − β₁ᵗ). Variable `m_hat`.

$$
\hat v_t
$$

Le second moment corrigé, vₜ/(1 − β₂ᵗ), toujours ≥ 0. Variable `v_hat`.

$$
\alpha
$$

Le taux d'apprentissage, réel > 0, 0,001 par défaut : chez Adam, c'est presque la longueur du pas de chaque poids. La fiche et ce fichier l'écrivent α ; la leçon 74 l'écrit η, parce que α y désigne aussi l'échelle LoRA. Argument `alpha`.

$$
\varepsilon
$$

Une petite constante ≥ 0, 10⁻⁸ par défaut, qui évite la division par zéro quand v̂ₜ = 0. Constante `EPS`, argument `eps`.

## Le mécanisme, avant les preuves

Adam reçoit à chaque pas un seul nombre par paramètre, le gradient gₜ, et rend un déplacement. La première opération est un mélange : mₜ garde 90 % de l'ancienne moyenne et prend 10 % du gradient neuf, ce qui lisse la direction et amortit les changements de signe. La deuxième fait la même chose sur le carré du gradient, avec une mémoire bien plus longue (99,9 % gardés) : vₜ mesure l'ampleur typique des gradients, sans regarder leur signe. Les deux moyennes partent de zéro, si bien qu'au début elles n'ont reçu qu'une petite part du poids total ; la troisième opération, la division par 1 − βᵗ, rend exactement cette part manquante. Vient ensuite la racine carrée : v est dans l'unité du gradient au carré, √v̂ revient dans l'unité du gradient, et le quotient m̂/√v̂ n'a plus d'unité du tout. C'est pour cela que la formule divise par une racine et non par v lui-même : seul ce quotient sans unité rend le pas indépendant de l'échelle des gradients. Ce quotient vaut ±1 quand les gradients sont constants et tombe vers 0 quand ils changent de signe ; multiplié par α, il donne un pas d'au plus quelques α. Enfin, ε ne compte que lorsque √v̂ est lui-même de l'ordre de 10⁻⁸. En résumé, la descente de gradient (fiche 08) avance de α fois la pente, Adam avance de α fois « la pente rapportée à sa taille habituelle ».

Petit film chiffré, gradients 2 puis −1 puis 3, avec les valeurs usuelles. Pas 1 : m = 0,1 × 2 = 0,2 ; v = 0,001 × 4 = 0,004 ; m̂ = 0,2/0,1 = 2 ; v̂ = 0,004/0,001 = 4 ; pas = 0,001 × 2/2 = 0,001. Pas 2 : m = 0,9 × 0,2 + 0,1 × (−1) = 0,08 ; v = 0,999 × 0,004 + 0,001 × 1 = 0,004996 ; m̂ = 0,08/0,19 ≈ 0,42105 ; v̂ = 0,004996/0,001999 ≈ 2,49925, dont la racine vaut ≈ 1,58090 ; pas ≈ 0,001 × 0,42105/1,58090 ≈ 0,00027. Pas 3 : m = 0,9 × 0,08 + 0,1 × 3 = 0,372 ; v ≈ 0,999 × 0,004996 + 0,009 ≈ 0,013991 ; m̂ = 0,372/0,271 ≈ 1,37269 ; v̂ ≈ 0,013991/0,002997 ≈ 4,66833, racine ≈ 2,16063 ; pas ≈ 0,00064. Le signe hésitant du pas 2 a divisé le pas par près de quatre, puis la direction revenue l'a fait remonter.

## Démonstration 1 — Pourquoi corriger le biais

**Ce qu'on démontre.** En partant de m₀ = 0, le premier moment est une somme pondérée des gradients passés, dont les poids totalisent 1 − β₁ᵗ et non 1 :

$$
m_t = (1 - \beta_1) \sum_{i=1}^{t} \beta_1^{\,t-i}\, g_i, \qquad \sum_{i=1}^{t} (1 - \beta_1)\, \beta_1^{\,t-i} = 1 - \beta_1^t
$$

En conséquence, si les gradients ont tous la même espérance, 𝔼[mₜ] = (1 − β₁ᵗ) 𝔼[g], et m̂ₜ = mₜ/(1 − β₁ᵗ) l'estime sans biais ; si le gradient vaut toujours g, m̂ₜ = g exactement. Même énoncé pour v avec β₂ et g².

**L'idée.** Une moyenne mobile qui part de zéro « croit » que tous les gradients d'avant le pas 1 valaient zéro : une part β₁ᵗ de son poids est restée sur ce zéro fictif. Diviser par 1 − β₁ᵗ redistribue ce poids sur les vrais gradients.

**La preuve, pas à pas.**

**Étape 1.** Pour t = 1 : m₁ = β₁ × 0 + (1 − β₁) g₁, parce que m₀ = 0 ; c'est la formule avec un seul terme.

**Étape 2.** Si la formule vaut au rang t − 1, on la multiplie par β₁, ce qui ajoute 1 à chaque exposant, et l'on ajoute (1 − β₁) gₜ, qui arrive avec l'exposant 0 :

$$
m_t = \beta_1 (1 - \beta_1) \sum_{i=1}^{t-1} \beta_1^{\,t-1-i}\, g_i + (1 - \beta_1)\, g_t = (1 - \beta_1) \sum_{i=1}^{t} \beta_1^{\,t-i}\, g_i
$$

**Étape 3.** La somme des poids est une série géométrique de raison β₁ et de t termes, qui vaut (1 − β₁ᵗ)/(1 − β₁) :

$$
(1 - \beta_1) \sum_{j=0}^{t-1} \beta_1^{\,j} = (1 - \beta_1) \times \frac{1 - \beta_1^t}{1 - \beta_1} = 1 - \beta_1^t
$$

**Étape 4.** Par linéarité de l'espérance (fiche 22), si 𝔼[gᵢ] = 𝔼[g] pour tout i :

$$
\mathbb{E}[m_t] = (1 - \beta_1) \sum_{i=1}^{t} \beta_1^{\,t-i}\, \mathbb{E}[g] = (1 - \beta_1^t)\, \mathbb{E}[g]
$$

Diviser par 1 − β₁ᵗ donne 𝔼[m̂ₜ] = 𝔼[g] ; si gᵢ = g pour tout i, le même calcul sans espérance donne m̂ₜ = g. ∎

**Vérification chiffrée.** Gradient constant g = 7 : m₁ = 0,7 ; m₂ = 0,9 × 0,7 + 0,7 = 1,33 = (1 − 0,81) × 7 ; m₃ = 1,897 = (1 − 0,729) × 7 ; m₅ = (1 − 0,9⁵) × 7 = 0,40951 × 7 ≈ 2,86657 ; chaque fois, m̂ₜ = 7. Gradients 2, −1, 3 du film : la somme déroulée donne m₃ = 0,1 × (0,81 × 2 + 0,9 × (−1) + 3) = 0,1 × 3,72 = 0,372, la valeur trouvée par la récurrence. Au pas 1, les facteurs valent 1 − β₁ = 0,1 et 1 − β₂ = 0,001 : sans correction, m₁ serait dix fois trop petit et v₁ mille fois trop petit.

**Ce que la preuve révèle du mécanisme.** Le poids d'un gradient vieux de j pas décroît comme β₁ʲ : la mémoire moyenne vaut β₁/(1 − β₁) = 9 pas pour m et 999 pas pour v. Le biais disparaît de lui-même quand β₁ᵗ devient négligeable, très vite pour m (0,9³⁰ ≈ 0,04239), très lentement pour v (0,999³⁰ ≈ 0,97043). C'est v, au dénominateur, qui rend la correction indispensable.

**Conséquence pour un agent.** Le compteur t fait partie de l'état de l'optimiseur au même titre que m et v : une reprise d'entraînement qui recharge m et v sans t refait la correction comme au pas 1, et fausse le pas pendant des centaines de pas (démonstration 6, cas 2).

## Démonstration 2 — Le premier pas vaut environ α, quel que soit le gradient

**Ce qu'on démontre.** Au premier pas, avec m₀ = v₀ = 0, le déplacement vaut exactement

$$
\frac{\alpha\, \hat m_1}{\sqrt{\hat v_1} + \varepsilon} = \frac{\alpha\, g_1}{\lvert g_1 \rvert + \varepsilon}
$$

donc environ ±α dès que |g₁| est grand devant ε.

**L'idée.** Au premier pas, la correction rend m̂₁ = g₁ et v̂₁ = g₁² : le quotient vaut g₁/|g₁|, c'est-à-dire le signe du gradient. La taille du gradient a disparu.

**La preuve, pas à pas.**

**Étape 1.** Par la démonstration 1 avec t = 1, parce que m₁ = (1 − β₁)g₁ et que 1 − β₁¹ = 1 − β₁ :

$$
\hat m_1 = \frac{(1 - \beta_1)\, g_1}{1 - \beta_1} = g_1, \qquad \hat v_1 = \frac{(1 - \beta_2)\, g_1^2}{1 - \beta_2} = g_1^2
$$

**Étape 2.** La racine d'un carré est une valeur absolue, parce que √(x²) = |x| pour tout réel x : √v̂₁ = |g₁|.

**Étape 3.** On remplace dans la formule, ce qui donne l'énoncé ; si |g₁| ≫ ε, le quotient g₁/(|g₁| + ε) est très proche de g₁/|g₁| = ±1. ∎

**Vérification chiffrée.** g = 1 000 : 0,001 × 1 000/(1 000 + 10⁻⁸) ≈ 0,001. g = 0,01 : 0,001 × 0,01/(0,01 + 10⁻⁸) ≈ 0,000999999. g = −300 : −0,001. Contre-exemple quand l'hypothèse « |g| ≫ ε » manque : g = 10⁻⁹ donne 0,001 × 10⁻⁹/(1,1 × 10⁻⁸) ≈ 0,0000909, onze fois moins ; et pour |g| = ε le pas tombe exactement à α/2.

**Ce que la preuve révèle du mécanisme.** Le premier pas ne transporte que le signe du gradient : Adam commence comme une descente « au signe », de pas α. ε fixe le seuil sous lequel un gradient est traité comme du bruit : le pas atteint au moins 0,9α si et seulement si |g| ≥ 9ε, soit 9 × 10⁻⁸ avec la valeur usuelle.

**Conséquence pour un agent.** α se règle comme une longueur de pas dans l'unité des poids, pas comme un coefficient à multiplier par une pente. En fine-tuning, on prend souvent α = 10⁻⁴ ou moins pour que les tout premiers pas, qui valent α quel que soit le gradient, ne déplacent pas trop un modèle déjà bon.

## Démonstration 3 — Adam ne dépend pas de l'échelle des gradients

**Ce qu'on démontre.** Si tous les gradients d'un paramètre sont multipliés par une constante c > 0, et si ε = 0, tous les pas d'Adam restent identiques :

$$
g_t \to c\, g_t \quad \Longrightarrow \quad \frac{\hat m_t}{\sqrt{\hat v_t}} \to \frac{c\, \hat m_t}{\sqrt{c^2 \hat v_t}} = \frac{\hat m_t}{\sqrt{\hat v_t}}
$$

Avec ε > 0, l'égalité reste vraie à un écart près tant que √v̂ₜ reste grand devant ε.

**L'idée.** m est linéaire en g, v est quadratique : multiplier g par c multiplie m par c et √v par c. Le quotient ne voit pas c.

**La preuve, pas à pas.**

**Étape 1.** Par la formule déroulée de la démonstration 1, parce que chaque terme de la somme est multiplié par c : mₜ devient c mₜ, et m̂ₜ devient c m̂ₜ (la correction ne dépend que de t).

**Étape 2.** De même, chaque gᵢ² devient c² gᵢ², donc vₜ devient c² vₜ et v̂ₜ devient c² v̂ₜ.

**Étape 3.** Parce que c > 0, √(c² v̂ₜ) = c √v̂ₜ, et le quotient c m̂ₜ/(c √v̂ₜ) se simplifie par c. ∎

**Vérification chiffrée.** Gradients 0,3 ; −1,2 ; 2 ; 0,7, puis les mêmes multipliés par 100 : le programme trouve les mêmes quatre pas à 10⁻⁶ près en relatif, à savoir 0,001 ; −0,00056 ; 0,00032 ; 0,00041 (arrondis). Contre-exemple quand l'hypothèse « √v̂ ≫ ε » manque : multipliés par 10⁻⁸, ces gradients deviennent de l'ordre de ε, et le premier pas tombe de 0,001 à environ 0,00023.

**Ce que la preuve révèle du mécanisme.** Adam ne voit que la forme de la suite des gradients (régularité, signes), pas leur taille. Une entrée exprimée en AED ou en millions d'AED produit les mêmes pas. Le revers est symétrique : un flux de données corrompu qui multiplie les gradients par 100 ne produit aucun pas anormal, donc aucun signal visible dans la trajectoire des poids.

**Conséquence pour un agent.** Adam permet d'entraîner ensemble des paramètres d'échelles très différentes (cas 1). Mais on ne compte pas sur la perte ou sur les pas pour détecter un flux corrompu : on surveille la norme brute des gradients et on valide les données à l'ingestion.

## Démonstration 4 — Un pas effectif par paramètre

**Ce qu'on démontre.** La mise à jour d'Adam est une descente de gradient (fiche 08) sur la direction lissée m̂ₜ, avec un pas propre à chaque paramètre et à chaque instant :

$$
\theta_{t+1} = \theta_t - \eta_{\text{eff}}\, \hat m_t, \qquad \eta_{\text{eff}} = \frac{\alpha}{\sqrt{\hat v_t} + \varepsilon}
$$

Pour des gradients d'ampleur constante |g|, η_eff ≈ α/|g| : il est inversement proportionnel à la taille des gradients du paramètre.

**L'idée.** On sépare le quotient en deux morceaux : une direction m̂ et un coefficient α/(√v̂ + ε). Ce coefficient est petit quand le paramètre reçoit de gros gradients, et grand quand il en reçoit de petits.

**La preuve, pas à pas.**

**Étape 1.** On factorise, parce que α m̂/(√v̂ + ε) = (α/(√v̂ + ε)) × m̂ : c'est la formule de la descente avec le pas η_eff et le gradient remplacé par m̂.

**Étape 2.** Si |gᵢ| = G pour tout i, alors v̂ₜ = G² par la démonstration 1, donc η_eff = α/(G + ε) ≈ α/G, parce que G ≫ ε. ∎

**Vérification chiffrée.** Gradients d'environ 1 000 : v̂ = 10⁶ et η_eff ≈ 0,001/1 000 = 10⁻⁶. Gradients d'environ 0,01 : v̂ = 10⁻⁴ et η_eff ≈ 0,001/0,01 = 0,1. Le rapport des deux pas effectifs vaut 10⁵, l'inverse exact du rapport des gradients : les deux produits η_eff × g valent α.

**Ce que la preuve révèle du mécanisme.** Adam est une descente de gradient qui règle son pas poids par poids, en fonction de l'historique de chaque poids : c'est la correction du défaut « le poids le plus courbé fixe le pas de tous » de la fiche 08 (cas 4). La direction m̂ joue en plus le rôle d'une inertie, qui freine quand le signe hésite.

**Conséquence pour un agent.** Un paramètre rarement nourri a un petit v̂, donc un grand η_eff : il apprend vite quand un signal arrive, mais il peut aussi s'emballer (démonstration 5, cas 3). Les journaux d'entraînement gagnent à suivre η_eff par groupe de poids, pas seulement la perte.

## Démonstration 5 — Le pas est borné par α si β₁ = β₂, et par un facteur plus grand sinon

**Ce qu'on démontre.** On note ρ = β₁²/β₂ (avec ρ ≠ 1) et Sₜ = 1 + ρ + … + ρᵗ⁻¹ = (1 − ρᵗ)/(1 − ρ). Pour toute suite de gradients et ε = 0 :

$$
\frac{\lvert \hat m_t \rvert}{\sqrt{\hat v_t}} \le \frac{1 - \beta_1}{\sqrt{1 - \beta_2}} \times \sqrt{S_t} \times \frac{\sqrt{1 - \beta_2^t}}{1 - \beta_1^t}
$$

Si β₁ = β₂, cette borne vaut exactement 1 : chaque pas est au plus α. Avec les valeurs usuelles, elle tend vers environ 7,27 quand t grandit.

**L'idée.** m est une somme pondérée des gradients, v une somme pondérée de leurs carrés, avec d'autres poids. L'inégalité de Cauchy–Schwarz compare une somme à une somme de carrés ; quand les poids sont les mêmes (β₁ = β₂), elle donne |m| ≤ √v au facteur de normalisation près, d'où |pas| ≤ α.

**La preuve, pas à pas.**

**Étape 1.** On écrit les deux moments avec l'âge j du gradient, par la démonstration 1, où wⱼ = (1 − β₁)β₁ʲ et uⱼ = (1 − β₂)β₂ʲ :

$$
m_t = \sum_{j=0}^{t-1} w_j\, g_{t-j}, \qquad v_t = \sum_{j=0}^{t-1} u_j\, g_{t-j}^2
$$

**Étape 2.** On écrit chaque terme wⱼ g comme le produit (wⱼ/√uⱼ) × (√uⱼ g), puis on applique Cauchy–Schwarz (fiche 01), parce que (Σ aⱼbⱼ)² ≤ (Σ aⱼ²)(Σ bⱼ²) :

$$
m_t^2 \le \left( \sum_{j=0}^{t-1} \frac{w_j^2}{u_j} \right) v_t, \qquad \sum_{j=0}^{t-1} \frac{w_j^2}{u_j} = \frac{(1 - \beta_1)^2}{1 - \beta_2} \sum_{j=0}^{t-1} \left(\frac{\beta_1^2}{\beta_2}\right)^{j} = \frac{(1 - \beta_1)^2}{1 - \beta_2}\, S_t
$$

**Étape 3.** On passe aux moments corrigés, parce que m̂ₜ = mₜ/(1 − β₁ᵗ) et v̂ₜ = vₜ/(1 − β₂ᵗ) :

$$
\frac{\hat m_t^2}{\hat v_t} = \frac{m_t^2}{v_t} \times \frac{1 - \beta_2^t}{(1 - \beta_1^t)^2} \le \frac{(1 - \beta_1)^2}{1 - \beta_2}\, S_t\, \frac{1 - \beta_2^t}{(1 - \beta_1^t)^2}
$$

et l'on prend la racine.

**Étape 4.** Si β₁ = β₂ = β, alors ρ = β, Sₜ = (1 − βᵗ)/(1 − β), et le second membre vaut ((1 − β)²/(1 − β)) × ((1 − βᵗ)/(1 − β)) × (1 − βᵗ)/(1 − βᵗ)² = 1. ∎

**Vérification chiffrée.** Poids rare : 100 pas sans gradient, puis 10 gradients de 1. Avec β₁ = β₂ = 0,9, le dixième pas vaut 0,80705α ≤ α. Avec les valeurs usuelles, il vaut 2,10737α, et la borne à t = 110 vaut 2,34704 : l'inégalité tient. Contre-exemple d'une « borne » souvent citée, (1 − β₁)/√(1 − β₂) : avec β₂ = 0,99 elle vaut 0,1/0,1 = 1, mais le même poids rare fait un pas de 1,72279α ; la vraie borne vaut 1,91817 à t = 110 et tend vers 2,34521. Avec β₂ = 0,999, elle tend vers 3,16228 × 2,29907 ≈ 7,27029.

**Ce que la preuve révèle du mécanisme.** Le facteur √Sₜ mesure le décalage des deux mémoires : quand v oublie plus lentement que m (β₂ > β₁), un gradient qui arrive après un long silence remplit vite m mais à peine v, et le quotient dépasse 1. Plus β₂ s'éloigne de β₁ vers 1, plus le pas d'un poids rare peut dépasser α. L'égalité de Cauchy–Schwarz est atteinte pour des gradients qui croissent géométriquement : c'est le scénario d'un poids qui se réveille.

**Conséquence pour un agent.** Si un modèle a des poids rares dont un saut est coûteux (un quartier, un client, un code d'acte), on choisit β₂ assez proche de β₁, ou l'on borne le pas, par un calcul et non par la formule (1 − β₁)/√(1 − β₂), qui n'est pas une borne (cas 3).

## Démonstration 6 — Un état et un compteur désaccordés faussent le pas

**Ce qu'on démontre.** Avec un gradient constant g, le pas exact d'Adam vaut α (ε négligé). Trois erreurs d'implémentation le multiplient par un facteur qui dépend de t :

$$
\text{sans correction : } \frac{1 - \beta_1^t}{\sqrt{1 - \beta_2^t}}, \qquad \text{m seul corrigé : } \frac{1}{\sqrt{1 - \beta_2^t}}, \qquad \text{compteur remis à 0 : } \frac{\sqrt{1 - \beta_2^t}}{1 - \beta_1^t}
$$

Le troisième cas suppose que m et v ont été rechargés à leur valeur d'équilibre, et que le compteur t redémarre à 1.

**L'idée.** La correction divise m par 1 − β₁ᵗ et v par 1 − β₂ᵗ ; il faut que ces facteurs correspondent au nombre de gradients réellement accumulés. Si l'on oublie la correction, on garde le biais ; si l'on corrige un état qui n'est pas biaisé, on crée un biais inverse.

**La preuve, pas à pas.**

**Étape 1.** Gradient constant depuis le pas 1 : mₜ = (1 − β₁ᵗ)g et vₜ = (1 − β₂ᵗ)g² (démonstration 1).

**Étape 2.** Sans correction, le quotient vaut mₜ/√vₜ = (1 − β₁ᵗ)g/(√(1 − β₂ᵗ)|g|), d'où le premier facteur, parce que g/|g| = ±1.

**Étape 3.** Avec m corrigé seulement, le quotient vaut g/(√(1 − β₂ᵗ)|g|), d'où le deuxième facteur.

**Étape 4.** Compteur remis à 0 avec m = g et v = g², valeurs d'équilibre : le pas suivant divise ces valeurs par 1 − β₁ᵗ et 1 − β₂ᵗ comme si elles étaient biaisées, d'où le quotient (g/(1 − β₁ᵗ))/(|g|/√(1 − β₂ᵗ)), qui est le troisième facteur. ∎

**Vérification chiffrée.** Sans correction : 3,162 à t = 1, 6,528 à t = 10, 3,241 à t = 100, 1,258 à t = 1 000 (les valeurs de la leçon 74). Avec m seul corrigé : 31,623 à t = 1, l'exercice 2. Compteur remis à 0 : 0,31623 à t = 1, 0,1532 à t = 10, 0,3086 à t = 100, 0,7952 à t = 1 000, et le pas ne revient à 90 % de sa valeur normale qu'au pas 1 660.

**Ce que la preuve révèle du mécanisme.** Les trois facteurs viennent de la même cause : β₂ᵗ décroît mille fois plus lentement que β₁ᵗ ne le fait au début, si bien que toute erreur sur la correction de v dure des milliers de pas. Oublier la correction donne des pas trop grands au moment où les poids sont les plus fragiles ; remettre t à zéro donne des pas trop courts pendant longtemps.

**Conséquence pour un agent.** Un point de sauvegarde d'entraînement contient les poids et l'état complet (m, v, t) ; un test de reprise compare une courbe interrompue puis reprise à une courbe continue (cas 2).

## Exemple simple, à la main

Premier pas, gradient g = 2, β₁ = 0,9, β₂ = 0,999, α = 0,001 :

$$
m_1 = 0{,}1 \times 2 = 0{,}2, \qquad v_1 = 0{,}001 \times 4 = 0{,}004
$$

$$
\hat m_1 = \frac{0{,}2}{0{,}1} = 2, \qquad \hat v_1 = \frac{0{,}004}{0{,}001} = 4, \qquad \text{pas} = \frac{0{,}001 \times 2}{\sqrt 4 + 10^{-8}} \approx 0{,}001
$$

Le même gradient pendant trois pas, chaque case calculée à partir de la précédente :

| t | mₜ = 0,9 mₜ₋₁ + 0,1 × 2 | vₜ = 0,999 vₜ₋₁ + 0,001 × 4 | 1 − 0,9ᵗ | 1 − 0,999ᵗ | m̂ₜ | v̂ₜ | pas |
|---|---|---|---|---|---|---|---|
| 1 | 0,2 | 0,004 | 0,1 | 0,001 | 2 | 4 | 0,001 |
| 2 | 0,18 + 0,2 = 0,38 | 0,003996 + 0,004 = 0,007996 | 0,19 | 0,001999 | 2 | 4 | 0,001 |
| 3 | 0,342 + 0,2 = 0,542 | 0,007988004 + 0,004 = 0,011988004 | 0,271 | 0,002997001 | 2 | 4 | 0,001 |

À chaque ligne, m̂ = m/(1 − 0,9ᵗ) = 2 et v̂ = 4, comme le prévoit la démonstration 1 : 0,38/0,19 = 2 et 0,542/0,271 = 2. Le pas exact vaut 0,001 × 2/(2 + 10⁻⁸) ≈ 0,000999999995 : ε ne change rien tant que le gradient n'est pas minuscule.

## Cas d'usage complexes, démontrés

### Cas 1 — Actifs virtuels [CRYPTO] : deux poids d'échelles très différentes

**Contexte.** Une plateforme d'actifs virtuels agréée par la VARA met à jour chaque nuit un petit modèle de score qui aide son agent de surveillance à classer les alertes de liquidité. Deux poids posent problème : w₁ porte le volume échangé, en millions d'AED et non normalisé, et reçoit des gradients d'environ 1 000 ; w₂ est le biais d'une paire d'actifs rarement échangée, avec des gradients d'environ 0,01. Le job dispose de 200 pas par nuit. La question : descente simple ou Adam, et avec quel réglage ? Les ordres de grandeur sont illustratifs.

**Données.**

- Gradients : environ 1 000 pour w₁, environ 0,01 pour w₂, de signe constant sur les premiers pas.
- Tolérance de stabilité : w₁ ne doit pas bouger de plus de 0,01 par pas.
- Déplacement nécessaire pour w₂ : 0,05.
- Pas candidats : descente simple de pas 0,001 ; Adam avec α = 0,001 et les valeurs usuelles.
- Budget : 200 pas par nuit ; une séquence de gradients hésitante pour w₂ : 2, −1, 3 (en centièmes).

**Calcul pas à pas.**

**Étape 1.** Descente simple de pas 0,001 : le déplacement est le pas fois le gradient.

$$
\Delta w_1 = 0{,}001 \times 1\,000 = 1, \qquad \Delta w_2 = 0{,}001 \times 0{,}01 = 10^{-5}
$$

w₁ bouge 100 fois plus que sa tolérance ; w₂ demanderait 0,05/10⁻⁵ = 5 000 pas.

**Étape 2.** Descente simple réglée pour la stabilité de w₁ : il faut un pas ≤ 0,01/1 000 = 10⁻⁵, et alors

$$
\Delta w_2 = 10^{-5} \times 0{,}01 = 10^{-7}, \qquad \frac{0{,}05}{10^{-7}} = 500\,000 \text{ pas}
$$

**Étape 3.** Adam, α = 0,001 : par la démonstration 2, les trois premiers pas valent 0,001 pour les deux poids (le programme trouve 0,001 arrondi à 6 décimales dans les deux cas). w₁ reste dix fois sous sa tolérance, et w₂ atteint 0,05 en 0,05/0,001 = 50 pas.

**Étape 4.** Direction hésitante sur w₂ (gradients 2, −1, 3, quelle que soit l'unité par la démonstration 3) : pas de 0,001 ; 0,00027 ; 0,00064, soit 0,0019 au total contre 0,003 pour trois gradients de même signe : la moyenne m freine quand la direction hésite.

**Décision de l'agent.** Le job passe à Adam avec α = 0,001 : 50 pas suffisent pour w₂, dans le budget de 200, sans menacer la stabilité de w₁. La descente simple est rejetée : aucun pas unique ne convient aux deux poids.

**Contre-calcul.** Avec la descente simple de pas 0,001, w₁ diverge dès le premier pas (déplacement 1, pour une tolérance de 0,01) ; avec le pas stable de 10⁻⁵, w₂ n'apprend pas : 500 000 pas, 2 500 nuits de 200 pas. Pendant ce temps, l'agent sous-estime systématiquement le risque sur la paire rare et laisse passer ses alertes de liquidité.

**Sensibilité.** Deux bascules. Côté ε : le pas d'un poids reste au-dessus de 0,9α tant que |g| ≥ 9ε = 9 × 10⁻⁸ (démonstration 2) ; w₂ en est très loin. Côté données : si un flux corrompu multiplie par 100 les gradients de w₁, Adam fait toujours des pas de 0,001 (démonstration 3), alors que la descente simple de pas 10⁻⁵ ferait des pas de 1 : la corruption ne se voit pas dans les pas d'Adam.

**En production.** L'indicateur est la norme brute des gradients de chaque entrée, comparée à sa médiane mobile, avec une alerte au-delà d'un facteur 10 (illustratif), parce que les pas d'Adam ne trahissent pas un flux corrompu. La plateforme est agréée par la VARA ; les obligations précises de surveillance et de conservation des modèles sont à confirmer avec le texte en vigueur.

### Cas 2 — Banque [BANQUE] : reprendre un entraînement sans casser la correction de biais

**Contexte.** Une banque de détail de Dubaï entraîne avec AdamW un adaptateur qui classe les réclamations de ses clients, en arabe, en anglais ou dans un mélange des deux. L'entraînement dure des heures et doit pouvoir reprendre après une interruption du serveur. L'équipe compare trois scripts de reprise au pas 5 000, sur un poids typique. Les valeurs sont illustratives.

**Données.**

- α = 2 × 10⁻⁴ (la leçon 74 écrit η), β₁ = 0,9, β₂ = 0,999.
- État au pas t = 5 000 : m = 0,02 (gradient moyen) et v = 0,01, donc √v = 0,1 (amplitude typique).
- Gradient suivant : 0,02 (un gradient moyen) ou 0,1 (un gradient bruité typique).
- Durée d'un pas : 1,2 s ; seuil de récupération : 90 % du pas normal.

**Calcul pas à pas.**

**Étape 1.** Pas normal en régime établi, où les corrections valent pratiquement 1 :

$$
\text{pas}_{\text{normal}} = \alpha \times \frac{m}{\sqrt v} = 2 \times 10^{-4} \times \frac{0{,}02}{0{,}1} = 4 \times 10^{-5}
$$

**Étape 2.** Script A, état complet (m, v, t) rechargé, gradient 0,02 : le programme trouve 3,988 × 10⁻⁵, soit 0,997 fois le pas normal.

**Étape 3.** Script B, optimiseur recréé (m = v = 0, t = 0), gradient bruité 0,1 : par la démonstration 2, le pas vaut α × signe = 2 × 10⁻⁴, soit 5 fois le pas normal, et cela pour tous les poids à la fois.

**Étape 4.** Script C, m et v rechargés mais t remis à 0, gradient 0,02 : m₁ = 0,9 × 0,02 + 0,1 × 0,02 = 0,02 et v₁ = 0,999 × 0,01 + 0,001 × 0,0004 = 0,0099904, puis

$$
\hat m_1 = \frac{0{,}02}{0{,}1} = 0{,}2, \qquad \hat v_1 = \frac{0{,}0099904}{0{,}001} = 9{,}9904, \qquad \text{pas} = \frac{2 \times 10^{-4} \times 0{,}2}{\sqrt{9{,}9904}} \approx 1{,}2655 \times 10^{-5}
$$

soit 0,3164 fois le pas normal ; par la démonstration 6, le facteur √(1 − 0,999ᵗ)/(1 − 0,9ᵗ) ne revient à 0,9 qu'au pas 1 660, soit 1 660 × 1,2 s ≈ 33,2 minutes d'entraînement faussé.

**Décision de l'agent.** Le job sauvegarde m, v et t avec les poids (script A), et un test automatique vérifie qu'un entraînement interrompu puis repris suit la courbe d'un entraînement continu.

**Contre-calcul.** Le script B fait faire à chaque poids, d'un coup, un pas 5 fois trop long, y compris aux poids qu'Adam avait ralentis parce que leurs gradients étaient bruités : la perte de validation saute juste après chaque reprise. Le script C sous-entraîne pendant 1 660 pas : sa reprise paraît sans effet sur la courbe à court terme, mais elle allonge l'entraînement et rend impossible de rejouer à l'identique un entraînement, ce qu'un audit interne du modèle peut demander.

**Sensibilité.** Le saut du script B vaut 1/(m/√v) = 0,1/0,02 = 5 : il est d'autant plus grand que le rapport signal/bruit du poids est faible, et il disparaît (facteur 1) pour un poids aux gradients réguliers. Le retard du script C dépend de β₂ : avec β₂ = 0,99, le facteur revient durablement au-dessus de 0,9 au pas 166 au lieu de 1 660.

**En production.** Indicateurs : la présence de m, v et t dans chaque point de sauvegarde, et l'écart de perte de validation entre une reprise et un entraînement continu, à la graine près (alerte au-delà de 0,5 %, illustratif). La gestion du risque de modèle d'une banque relève de la supervision de la CBUAE ; l'exigence précise de reproductibilité est à confirmer avec le texte en vigueur.

### Cas 3 — Immobilier [IMMO] : un quartier rare qui s'emballe

**Contexte.** Une agence active à Dubaï et à Abu Dhabi entraîne avec Adam un reranker qui ordonne les biens proposés par son agent, à partir des visites programmées. Chaque quartier a son propre poids, et certains ne reçoivent presque aucune demande pendant des semaines. Quand une vague de demandes arrive sur l'un d'eux, son poids saute, et le reranker se met à proposer ce quartier à tous les acheteurs. L'équipe fixe une règle : aucun poids ne doit faire un pas de plus de 1,5α. Valeurs illustratives.

**Données.**

- Scénario du poids rare : 100 pas sans gradient, puis 10 gradients de 1.
- β₁ = 0,9 ; β₂ candidats : 0,999 (défaut), 0,99, 0,98, 0,95.
- Seuil : 1,5α par pas.
- 400 propositions par jour, dont 30 % hors critères tant que le poids du quartier est emballé.

**Calcul pas à pas.**

**Étape 1.** Moments après les 110 pas. Les 100 premiers pas laissent m = v = 0 ; les 10 suivants donnent, par la démonstration 1,

$$
m_{110} = 1 - 0{,}9^{10} \approx 0{,}65132, \qquad v_{110} = 1 - 0{,}999^{10} \approx 0{,}0099551
$$

**Étape 2.** Corrections au pas 110 : 1 − 0,9¹¹⁰ ≈ 0,99999 et 1 − 0,999¹¹⁰ ≈ 0,10422. Le second moment est divisé par un petit nombre, mais il était encore plus petit :

$$
\hat m_{110} \approx 0{,}65133, \qquad \hat v_{110} \approx \frac{0{,}0099551}{0{,}10422} \approx 0{,}095525, \qquad \frac{\hat m}{\sqrt{\hat v}} \approx \frac{0{,}65133}{0{,}30907} \approx 2{,}10737
$$

**Étape 3.** Même calcul pour les autres β₂ (programme) : 1,72279 pour 0,99 ; 1,43799 pour 0,98 ; 1,02639 pour 0,95. La valeur de β₂ pour laquelle le pas vaut exactement 1,5α est β₂ ≈ 0,98256.

**Étape 4.** Le prix de la mémoire courte : la mémoire moyenne de v vaut β₂/(1 − β₂), soit 999 pas pour 0,999, 99 pour 0,99, 49 pour 0,98 et 19 pour 0,95.

**Décision de l'agent.** L'équipe passe β₂ à 0,98 pour ce modèle : le poids rare fait au plus 1,438α, sous le seuil, et la mémoire de l'amplitude garde 49 pas, assez pour lisser le bruit des quartiers fréquents. Elle ajoute une décroissance AdamW qui ramène lentement vers 0 les poids peu nourris.

**Contre-calcul.** Le raisonnement « avec β₂ = 0,99, (1 − β₁)/√(1 − β₂) = 1, donc aucun pas ne dépasse α » est faux (démonstration 5) : le poids rare fait 1,72α, au-dessus du seuil. Pendant les jours où le poids est emballé, 30 % de 400 propositions, soit 120 propositions par jour, envoient des acheteurs vers un quartier qui ne correspond pas à leurs critères (illustratif).

**Sensibilité.** La valeur de bascule est β₂ ≈ 0,98256 : au-dessus, le pas du poids rare dépasse 1,5α. Descendre jusqu'à 0,95 ramène le pas à 1,03α, mais la mémoire tombe à 19 pas et v̂ devient bruité sur les quartiers fréquents. Le compromis est réel : sécurité des poids rares contre stabilité des poids fréquents.

**En production.** Indicateur : le plus grand rapport |pas|/α observé sur un pas, par groupe de poids, avec une alerte au-delà de 1,5 ; et la part des propositions concentrées sur un seul quartier. Les annonces proposées restent soumises aux règles de publicité immobilière de la RERA, à confirmer avec le texte en vigueur ; les prix restent en AED/sqft, venant d'un outil et non du modèle.

### Cas 4 — Ressources humaines [RH] : un lot aberrant et l'écrêtage du gradient

**Contexte.** Un cabinet RH présent dans plusieurs émirats entraîne avec Adam un classifieur des documents de ses dossiers (permis de travail, contrats MOHRE, relevés WPS). Un lot contient un scan illisible dont le gradient vaut 100 au lieu d'environ 1. Ce choc gonfle v pour longtemps, et l'entraînement avance ensuite au ralenti. L'équipe envisage d'écrêter chaque gradient à un seuil c (le ramener dans [−c ; c]). Valeurs illustratives.

**Données.**

- Gradients : 1 pendant 5 pas, puis 100 au pas 6, puis 1 ensuite ; α = 0,001, valeurs usuelles.
- Critère de récupération : le pas revient à 0,9α ; budget de récupération : 100 pas.
- Gradients légitimes des classes rares : jusqu'à 3 ; ils ne doivent pas être écrêtés.
- Seuils candidats : c = 3, 4, 5, 6, 10, ou pas d'écrêtage.

**Calcul pas à pas.**

**Étape 1.** Le pas du choc. Avant lui, m₅ = 1 − 0,9⁵ = 0,40951 et v₅ = 1 − 0,999⁵ ≈ 0,0049900. Au pas 6 :

$$
m_6 = 0{,}9 \times 0{,}40951 + 0{,}1 \times 100 \approx 10{,}36856, \qquad v_6 = 0{,}999 \times 0{,}00499 + 0{,}001 \times 10\,000 \approx 10{,}00499
$$

**Étape 2.** Corrections et pas, avec 1 − 0,9⁶ ≈ 0,46856 et 1 − 0,999⁶ ≈ 0,0059850 :

$$
\hat m_6 \approx 22{,}12861, \qquad \hat v_6 \approx 1\,671{,}67, \qquad \text{pas} \approx \frac{0{,}001 \times 22{,}12861}{40{,}886} \approx 0{,}000541
$$

Le choc ne fait pas un grand pas : il fait un pas plus petit qu'avant, puis 0,000478 au pas suivant, et la baisse continue.

**Étape 3.** Récupération sans écrêtage : v garde la trace du carré 10 000 pendant des milliers de pas ; le programme trouve qu'il faut 3 774 pas pour revenir à 0,9α.

**Étape 4.** Récupération avec écrêtage (programme) : 1 pas pour c = 3, 56 pour c = 4, 92 pour c = 5, 134 pour c = 6, 348 pour c = 10. Avec c = 5, le pas du choc vaut 0,000828 et le suivant 0,000802.

**Décision de l'agent.** Deux contraintes encadrent c : c ≥ 3 pour ne pas toucher les gradients légitimes, et une récupération en au plus 100 pas, soit c ≤ 5. Le job retient c = 5, la plus grande valeur qui tient le budget : elle laisse la marge maximale aux gradients légitimes.

**Contre-calcul.** Sans écrêtage, le choc d'un seul document coûte 3 774 pas d'apprentissage ralenti, soit 3 774 − 92 = 3 682 pas de plus qu'avec c = 5. À l'opposé, un seuil trop bas (c = 2) écrêterait les gradients légitimes de 3 à 2, soit un tiers de leur signal en moins sur les classes rares, qui sont justement les plus difficiles.

**Sensibilité.** La valeur de bascule est entre c = 5 (92 pas) et c = 6 (134 pas) : au-delà de 5, le budget de 100 pas est dépassé. Si les gradients légitimes des classes rares montaient au-dessus de 5, les deux contraintes deviendraient incompatibles, et il faudrait plutôt filtrer les scans illisibles avant l'entraînement.

**En production.** Indicateur : la part des lots écrêtés par époque, avec une alerte au-delà de 1 % (illustratif), qui signale un problème de données plutôt qu'un réglage. Les documents des dossiers (permis, contrats, salaires) sont des données personnelles : leur usage pour l'entraînement relève de la PDPL, ou du régime propre au DIFC ou à l'ADGM si le cabinet y est établi, à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Calculer m₂ et m̂₂ pour deux gradients constants g = 4, avec β₁ = 0,9.

**Exercice 2.** Que vaut 1 − β₂ᵗ au premier pas avec β₂ = 0,999 ? Que se passerait-il sans correction de v ?

**Exercice 3.** Démontrer que le premier pas d'Adam vaut α × g/(|g| + ε).

**Exercice 4.** Un gradient vaut 10⁻⁹. Que vaut le premier pas ? À quoi sert ε ?

**Exercice 5.** Pourquoi une descente de gradient simple ne peut-elle pas bien entraîner les deux paramètres du cas 1 ?

**Exercice 6 (modifier une donnée).** Dans le cas 3, l'équipe hésite entre β₂ = 0,99 et β₂ = 0,98. Recalculer à la main v₁₁₀, la correction et le pas du poids rare pour β₂ = 0,99. Le seuil de 1,5α est-il respecté ?

**Exercice 7 (trouver l'erreur).** Un collègue écrit : « Avec β₁ = 0,9 et β₂ = 0,99, on a (1 − β₁)/√(1 − β₂) = 0,1/0,1 = 1 : d'après l'article d'origine, aucun pas d'Adam ne peut dépasser α. » Trouver l'erreur et donner un contre-exemple chiffré.

**Exercice 8 (redémontrer de mémoire).** Sans regarder, redémontrer que pour un gradient constant g, mₜ = (1 − β₁ᵗ)g, et en déduire pourquoi on divise par 1 − β₁ᵗ.

## Corrigé

**Exercice 1.** m₁ = 0,9 × 0 + 0,1 × 4 = 0,4 ; m₂ = 0,9 × 0,4 + 0,1 × 4 = 0,36 + 0,4 = 0,76 ; m̂₂ = 0,76/(1 − 0,81) = 0,76/0,19 = 4, le gradient lui-même.

**Exercice 2.** 1 − 0,999 = 0,001. Sans correction de v (m étant corrigé), v̂ serait 1 000 fois trop petit, √v̂ environ √1 000 ≈ 31,6 fois trop petit, et le premier pas environ 32 fois trop grand (démonstration 6, deuxième facteur : 31,623).

**Exercice 3.** Démonstration 2 : m̂₁ = (1 − β₁)g/(1 − β₁) = g, v̂₁ = g², √v̂₁ = |g|, d'où le pas α g/(|g| + ε).

**Exercice 4.** 0,001 × 10⁻⁹/(10⁻⁹ + 10⁻⁸) = 0,001/11 ≈ 0,0000909 : ε empêche de diviser par un nombre presque nul et réduit le pas des gradients minuscules, qu'il traite comme du bruit.

**Exercice 5.** Un seul pas multiplie des gradients de 1 000 et de 0,01 : un pas de 0,001 fait bouger w₁ de 1, cent fois sa tolérance ; un pas de 10⁻⁵, stable pour w₁, fait bouger w₂ de 10⁻⁷, et il faudrait 500 000 pas.

**Exercice 6.** v₁₁₀ = 1 − 0,99¹⁰ ≈ 0,095618 ; la correction vaut 1 − 0,99¹¹⁰ ≈ 0,66897 ; v̂ ≈ 0,095618/0,66897 ≈ 0,14293, √v̂ ≈ 0,37807 ; m̂ ≈ 0,65133 comme dans le cas 3 ; pas ≈ 0,65133/0,37807 ≈ 1,72279α > 1,5α : le seuil n'est pas respecté avec 0,99, il l'est avec 0,98 (1,43799α).

**Exercice 7.** (1 − β₁)/√(1 − β₂) n'est pas une borne du pas : la démonstration 5 donne la vraie borne, qui contient le facteur √Sₜ et vaut 1,91817 à t = 110 et 2,34521 à la limite. Contre-exemple : le poids rare du cas 3 (100 pas sans gradient puis 10 gradients de 1) fait un pas de 1,72279α avec β₂ = 0,99. Le pas n'est borné par α que si β₁ = β₂.

**Exercice 8.** Étapes 1 à 3 de la démonstration 1 avec gᵢ = g : mₜ = (1 − β₁) g (1 + β₁ + … + β₁ᵗ⁻¹) = (1 − β₁) g (1 − β₁ᵗ)/(1 − β₁) = (1 − β₁ᵗ) g. Le poids manquant β₁ᵗ est celui du départ fictif m₀ = 0 ; diviser par 1 − β₁ᵗ le rend aux vrais gradients et donne m̂ₜ = g.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`adam_etat(gradients, alpha, b1, b2, eps, etat, corriger, ecretage)`** — Cette fonction est le pilote automatique qui règle chaque pas d'un paramètre d'après la mémoire de ses gradients passés : elle reçoit la suite des gradients, le taux α, 0,001 par défaut, les coefficients β₁ = 0,9 et β₂ = 0,999, l'ε de 10⁻⁸, un état de départ (m, v, t), un mode de correction et un seuil d'écrêtage facultatif, et refuse par une `ValueError` un α nul ou négatif, un β hors de [0 ; 1[ ou un ε négatif. Pour chaque gradient, elle l'écrête éventuellement dans [−c ; c], avance le compteur, met à jour les moyennes mobiles m et v, les corrige par 1 − β₁ᵗ et 1 − β₂ᵗ selon le mode choisi, « m » ne corrigeant que m, et calcule le pas α m̂/(√v̂ + ε) ; elle renvoie la liste des pas et l'état final, ce qui permet de reprendre l'entraînement.

**`pas_adam(gradients, alpha)`** — Cette petite fonction est le raccourci du cas courant, quand on part de zéro avec les réglages usuels : elle reçoit les gradients et le taux α, 0,001 par défaut, appelle `adam_etat` et ne garde que la liste des pas. Un premier gradient de 2 donne un pas de 0,001, exactement α, et les gradients 2, −1 et 3 donnent 0,001, 0,00027 et 0,00064 : le pas se rétrécit dès que les gradients se contredisent, comme le montre le film du mécanisme.

**`borne_pas(t, b1, b2)`** — On la voit en ingénieur qui calcule la charge maximale qu'un pont peut supporter avant même d'y faire passer un camion : elle reçoit le numéro du pas et les deux coefficients, calcule ρ = β₁²/β₂, refuse ρ = 1 par une `ValueError`, la formule devant alors être remplacée, puis la somme géométrique Sₜ = (1 − ρᵗ)/(1 − ρ). Elle renvoie la borne (1 − β₁)/√(1 − β₂) × √Sₜ × √(1 − β₂ᵗ)/(1 − β₁ᵗ) du rapport |m̂|/√v̂ de la démonstration 5 : 1 quand β₁ = β₂, 2,34704 au pas 110 avec les réglages usuels, 1,91817 avec β₂ = 0,99, et 7,27029 à la limite.

**`facteur_compteur_remis(t, b1, b2)`** — Cette fonction raconte l'erreur du mécanicien qui remet le compteur à zéro en gardant les réservoirs pleins : elle reçoit le numéro de pas t et les deux coefficients, et renvoie √(1 − β₂ᵗ)/(1 − β₁ᵗ), le rapport entre le pas effectivement fait et le pas normal quand m et v sont déjà à l'équilibre mais que t repart de 1. Ce facteur vaut 0,31623 au premier pas, 0,1532 au dixième, 0,3086 au centième et 0,7952 au millième ; le cas 2 cherche le pas où il remonte à 0,9.

**`pas_poids_rare(b2, b1)`** — Celle-ci met en scène le poids d'un quartier oublié qui ne reçoit aucun gradient pendant 100 pas, puis subit d'un coup 10 gradients de 1 : elle reçoit β₂ et β₁, fait tourner `adam_etat` sur cette suite et renvoie le dernier pas exprimé en unités de α, ainsi que l'état final. Avec β₂ = 0,999, ce pas vaut 2,10737 α, car v a eu le temps de tout oublier ; il descend à 1,72279 avec 0,99, 1,43799 avec 0,98, 1,02639 avec 0,95 et 0,80705 quand β₂ = β₁ = 0,9.

**`recuperation(ecretage, seuil, horizon)`** — Cette fonction mesure combien de temps un entraînement met à se remettre d'un choc, comme on chronomètre un coureur après un faux pas : elle reçoit le seuil d'écrêtage, éventuellement `None`, le pas cible de 0,0009, soit 0,9 α, et un horizon de 6 000 pas, fait passer cinq gradients de 1 puis un gradient de 100, puis continue avec des gradients de 1, un pas à la fois depuis l'état sauvegardé. Elle renvoie le nombre de pas nécessaires pour revenir au seuil, ou `None` si l'horizon ne suffit pas : 3 774 pas sans écrêtage, mais 92 avec un écrêtage à 5.

**`cas_1_echelles_crypto()`** — Cette fonction met en scène une plateforme d'actifs virtuels dont le modèle de score a deux poids aux gradients très différents, environ 1 000 pour le volume non normalisé et 0,01 pour une paire rarement échangée, avec 200 pas par nuit : elle ne reçoit rien et montre qu'en descente simple avec 0,001, le premier poids bondit de 1 tandis que le second bouge de 10⁻⁵, et qu'un pas assez petit pour stabiliser le premier demanderait 500 000 pas au second. Avec Adam, les deux poids font des pas de 0,001, si bien que 50 pas suffisent ; elle montre aussi qu'un gradient corrompu de 100 000 ne fait pas un plus grand pas, et renvoie ces résultats.

**`cas_2_reprise_banque()`** — On y suit une banque qui entraîne un classifieur de réclamations et compare trois scripts de reprise au pas 5 000, sur un poids dont m vaut 0,02 et v 0,01, avec α = 2 × 10⁻⁴ : la fonction ne reçoit rien, calcule le pas normal de 4 × 10⁻⁵, puis le pas du script A, qui restaure m, v et le compteur, 0,997 fois le normal, celui du script B, qui repart de zéro, 5 fois le normal, et celui du script C, qui restaure m et v mais remet le compteur à zéro, 0,3164 fois. Elle calcule que C ne retrouve 90 % du pas normal qu'au pas 1 660, soit 33,2 minutes, et durablement dès le pas 166 avec β₂ = 0,99, puis renvoie ces nombres.

**`cas_3_quartier_rare_immo()`** — Cette fonction raconte une agence dont le reranker ne doit faire faire à aucun poids un pas de plus de 1,5 α, alors que certains quartiers ne reçoivent presque aucune demande pendant des semaines : elle ne reçoit rien, calcule le pas du poids rare pour β₂ valant 0,999, 0,99, 0,98, 0,95 et 0,9, puis cherche par soixante bissections la valeur de bascule, 0,98256, au-delà de laquelle la règle est violée. Elle calcule aussi la mémoire β₂/(1 − β₂) de chaque réglage, 999, 99, 49 et 19 pas, choisit le plus grand β₂ qui respecte la règle, 0,98, et renvoie ces résultats.

**`cas_4_lot_aberrant_rh()`** — Ici, un cabinet de recrutement entraîne un classifieur de documents, et un scan illisible produit un gradient de 100 au milieu de gradients de 1 : la fonction ne reçoit rien, calcule le pas du choc, 0,000541, et le suivant, 0,000478, puis les mêmes avec un écrêtage à 5, 0,000828 et 0,000802. Elle mesure la récupération pour des seuils de 3, 4, 5, 6 et 10, soit 1, 56, 92, 134 et 348 pas, contre 3 774 sans écrêtage, choisit le plus grand seuil qui récupère en 100 pas au plus, c = 5, et renvoie ces résultats.

**`main()`** — C'est le chef d'orchestre de la fiche : il vérifie d'abord le premier pas d'un gradient de 2, puis trois pas à gradient constant, où m̂ vaut toujours 2 et v̂ toujours 4, et le film des gradients 2, −1 et 3. Il rejoue ensuite les six démonstrations, de la correction exacte du biais à la borne du pas et au compteur remis à zéro, en passant par l'invariance d'échelle et le pas effectif de 10⁻⁶ ou 0,1 selon la taille des gradients, puis joue les quatre cas et le corrigé, et s'assure que β₂ = 1 est refusé ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tout concorde.

```python
"""Démonstration 31 — Adam : correction du biais, premier pas, invariance d'échelle, pas effectif, borne du pas, compteur désaccordé, quatre cas aux Émirats."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

B1, B2, EPS = 0.9, 0.999, 1e-8


def adam_etat(gradients, alpha=0.001, b1=B1, b2=B2, eps=EPS, etat=(0.0, 0.0, 0), corriger=True, ecretage=None):
    """Pas successifs α m̂/(√v̂ + ε) d'un paramètre et état final (m, v, t).

    `corriger` = "m", True ou False : corrige m seul, les deux moments, ou aucun.
    `ecretage` = c ramène chaque gradient dans [−c ; c] avant les moments."""
    if alpha <= 0 or not 0 <= b1 < 1 or not 0 <= b2 < 1 or eps < 0:
        raise ValueError("il faut alpha > 0, 0 <= beta < 1 et eps >= 0")
    m, v, t = etat
    pas = []
    for g in gradients:
        if ecretage is not None:
            g = max(-ecretage, min(ecretage, g))
        t += 1
        m = b1 * m + (1 - b1) * g
        v = b2 * v + (1 - b2) * g * g
        c1 = 1 - b1 ** t if corriger else 1.0
        c2 = 1 - b2 ** t if corriger is True else 1.0
        m_hat, v_hat = m / c1, v / c2
        pas.append(alpha * m_hat / (math.sqrt(v_hat) + eps))
    return pas, (m, v, t)


def pas_adam(gradients, alpha=0.001):
    """Les pas successifs d'Adam avec les valeurs usuelles (fiche 31)."""
    return adam_etat(gradients, alpha)[0]


def borne_pas(t, b1=B1, b2=B2):
    """Borne de |m̂|/√v̂ (démonstration 5) ; ρ = β1²/β2 doit différer de 1."""
    rho = b1 * b1 / b2
    if rho == 1:
        raise ValueError("rho = 1 : utiliser S_t = t")
    s_t = (1 - rho ** t) / (1 - rho)
    return (1 - b1) / math.sqrt(1 - b2) * math.sqrt(s_t) * math.sqrt(1 - b2 ** t) / (1 - b1 ** t)


def facteur_compteur_remis(t, b1=B1, b2=B2):
    """Pas / pas normal quand m, v sont à l'équilibre et t repart de 1 (démonstration 6)."""
    return math.sqrt(1 - b2 ** t) / (1 - b1 ** t)


def pas_poids_rare(b2, b1=B1):
    """Dernier pas, en unités de α, après 100 pas sans gradient puis 10 gradients de 1."""
    pas, etat = adam_etat([0.0] * 100 + [1.0] * 10, b1=b1, b2=b2)
    return pas[-1] / 0.001, etat


def recuperation(ecretage, seuil=0.0009, horizon=6_000):
    """Nombre de pas après le choc (gradient 100 au pas 6) pour revenir à 0.9 α ; None si jamais."""
    _, etat = adam_etat([1.0] * 5 + [100.0], ecretage=ecretage)
    for k in range(1, horizon + 1):
        pas, etat = adam_etat([1.0], etat=etat, ecretage=ecretage)
        if pas[0] >= seuil:
            return k
    return None


def cas_1_echelles_crypto():
    """Actifs virtuels : un poids aux gradients de 1 000, un autre aux gradients de 0.01."""
    res = {"sgd_w1": 0.001 * 1000, "sgd_w2": 0.001 * 0.01, "pas_stable": 0.01 / 1000}
    res["sgd_n_w2"] = 0.05 / res["sgd_w2"]
    res["stable_w2"] = res["pas_stable"] * 0.01
    res["stable_n_w2"] = 0.05 / res["stable_w2"]
    res["adam_w1"], res["adam_w2"] = pas_adam([1000] * 3), pas_adam([0.01] * 3)
    res["adam_n_w2"] = 0.05 / 0.001
    res["hesite"] = pas_adam([2, -1, 3])
    res["corrompu"] = pas_adam([100_000] * 3)
    print(f"Cas 1 [CRYPTO] : descente simple Δw1 = {res['sgd_w1']:g}, Δw2 = {res['sgd_w2']:.0e} ;"
          f" pas stable → {res['stable_n_w2']:,.0f} pas pour w2 ; Adam → {res['adam_n_w2']:.0f} pas")
    print(f"  Adam : {[round(p, 6) for p in res['adam_w1']]} et {[round(p, 6) for p in res['adam_w2']]} ;"
          f" gradients 2, -1, 3 : {[round(p, 5) for p in res['hesite']]}")
    return res


def cas_2_reprise_banque():
    """Banque : trois scripts de reprise au pas 5 000, sur un poids m = 0.02, v = 0.01."""
    alpha, m, v = 2e-4, 0.02, 0.01
    normal = alpha * m / math.sqrt(v)
    a = adam_etat([0.02], alpha=alpha, etat=(m, v, 5000))[0][0]
    b = adam_etat([0.1], alpha=alpha)[0][0]
    c, (m1, v1, _) = adam_etat([0.02], alpha=alpha, etat=(m, v, 0))
    recup = next(t for t in range(1, 10_000) if facteur_compteur_remis(t) >= 0.9)
    recup_099 = next(t for t in range(1, 10_000)
                     if all(facteur_compteur_remis(u, b2=0.99) >= 0.9 for u in range(t, t + 200)))
    res = {"normal": normal, "a": a, "b": b, "c": c[0], "m1": m1, "v1": v1, "recup": recup,
           "minutes": recup * 1.2 / 60, "recup_099": recup_099}
    print(f"Cas 2 [BANQUE] : pas normal {normal:.1e} ; A {a / normal:.3f} × ; B {b / normal:.2f} × ;"
          f" C {c[0] / normal:.4f} ×, retour à 90 % au pas {recup} ({res['minutes']:.1f} min)")
    return res


def cas_3_quartier_rare_immo():
    """Immobilier : pas du poids d'un quartier rare selon β2, seuil 1.5 α."""
    res = {b2: pas_poids_rare(b2) for b2 in (0.999, 0.99, 0.98, 0.95, 0.9)}
    bas, haut = 0.95, 0.999
    for _ in range(60):
        milieu = (bas + haut) / 2
        if pas_poids_rare(milieu)[0] > 1.5:
            haut = milieu
        else:
            bas = milieu
    res["bascule"] = bas
    res["memoire"] = {b2: b2 / (1 - b2) for b2 in (0.999, 0.99, 0.98, 0.95)}
    res["choix"] = max(b2 for b2 in (0.999, 0.99, 0.98, 0.95) if res[b2][0] <= 1.5)
    print("Cas 3 [IMMO] : pas du poids rare / α :"
          + "".join(f" β2 = {b2} → {res[b2][0]:.5f} ;" for b2 in (0.999, 0.99, 0.98, 0.95)))
    print(f"  bascule β2 = {res['bascule']:.5f} pour 1.5 α ; choix β2 = {res['choix']}")
    return res


def cas_4_lot_aberrant_rh():
    """RH : un gradient de 100 au milieu de gradients de 1 ; écrêtage à c."""
    pas, _ = adam_etat([1.0] * 5 + [100.0, 1.0])
    pas5, _ = adam_etat([1.0] * 5 + [100.0, 1.0], ecretage=5)
    recup = {c: recuperation(c) for c in (None, 3, 4, 5, 6, 10)}
    choix = max(c for c in range(3, 13) if recuperation(c) <= 100)
    res = {"choc": pas[5], "apres": pas[6], "choc5": pas5[5], "apres5": pas5[6], "recup": recup, "choix": choix}
    print(f"Cas 4 [RH] : pas du choc {pas[5]:.6f}, suivant {pas[6]:.6f} ; récupération sans écrêtage {recup[None]} pas")
    print("  avec écrêtage :" + "".join(f" c = {c} → {recup[c]} ;" for c in (3, 4, 5, 6, 10)) + f" choix c = {choix}")
    return res


def main() -> None:
    m1, v1 = (1 - B1) * 2, (1 - B2) * 4
    print(f"m1 = {m1:.1f} ; v1 = {v1:.3f} ; m̂1 = {m1 / (1 - B1):.1f} ; v̂1 = {v1 / (1 - B2):.1f} ; pas = {pas_adam([2])[0]:.6f}")
    assert math.isclose(m1 / (1 - B1), 2) and math.isclose(v1 / (1 - B2), 4) and round(pas_adam([2])[0], 6) == 0.001
    assert round(pas_adam([2])[0], 12) == 0.000999999995
    # exemple simple : trois pas à gradient constant 2
    m = v = 0.0
    lignes = []
    for t in range(1, 4):
        m, v = B1 * m + (1 - B1) * 2, B2 * v + (1 - B2) * 4
        lignes.append((round(m, 6), round(v, 9), round(1 - B1 ** t, 6), round(1 - B2 ** t, 9),
                       round(m / (1 - B1 ** t), 9), round(v / (1 - B2 ** t), 9)))
    assert lignes == [(0.2, 0.004, 0.1, 0.001, 2.0, 4.0), (0.38, 0.007996, 0.19, 0.001999, 2.0, 4.0),
                      (0.542, 0.011988004, 0.271, 0.002997001, 2.0, 4.0)]
    assert math.isclose(0.9 * 0.2, 0.18) and math.isclose(0.999 * 0.004, 0.003996)
    assert math.isclose(0.9 * 0.38, 0.342) and math.isclose(0.999 * 0.007996, 0.007988004)
    assert all(round(p, 9) == 0.001 for p in pas_adam([2, 2, 2]))
    # film du mécanisme : gradients 2, −1, 3
    _, (m2, v2, _) = adam_etat([2, -1])
    _, (m3, v3, _) = adam_etat([2, -1, 3])
    film = pas_adam([2, -1, 3])
    print(f"film 2, -1, 3 : m = {m2:.2f} puis {m3:.3f} ; pas {[round(p, 5) for p in film]}")
    assert math.isclose(m2, 0.08) and math.isclose(v2, 0.004996) and math.isclose(m3, 0.372)
    assert round(v3, 6) == 0.013991 and round(m2 / 0.19, 5) == 0.42105 and round(v2 / 0.001999, 5) == 2.49925
    assert round(math.sqrt(v2 / 0.001999), 5) == 1.5809 and round(m3 / 0.271, 5) == 1.37269
    assert round(v3 / (1 - B2 ** 3), 5) == 4.66833 and round(math.sqrt(v3 / (1 - B2 ** 3)), 5) == 2.16063
    assert [round(p, 5) for p in film] == [0.001, 0.00027, 0.00064] and round(film[0] / film[1], 1) == 3.8

    # démonstration 1 : somme déroulée, poids 1 − β1^t, correction exacte
    g, m = 7.0, 0.0
    suite = []
    for t in range(1, 6):
        m = B1 * m + (1 - B1) * g
        suite.append(m)
        assert math.isclose(m, (1 - B1 ** t) * g) and math.isclose(m / (1 - B1 ** t), g)
    assert [round(x, 5) for x in suite] == [0.7, 1.33, 1.897, 2.4073, 2.86657] and round(1 - 0.9 ** 5, 5) == 0.40951
    assert math.isclose(0.1 * (0.81 * 2 + 0.9 * (-1) + 3), 0.372) and math.isclose(0.81 * 2 - 0.9 + 3, 3.72)
    assert math.isclose(B1 / (1 - B1), 9) and round(B2 / (1 - B2)) == 999
    assert round(0.9 ** 30, 5) == 0.04239 and round(0.999 ** 30, 5) == 0.97043
    print(f"démonstration 1 : g = 7 → m = {[round(x, 5) for x in suite]}, m̂ = 7 à chaque pas")
    # démonstration 2 : premier pas = α g / (|g| + ε)
    premiers = [pas_adam([g])[0] for g in (1000, 0.01, -300, 1e-9, 1e-8, 9e-8)]
    assert round(premiers[0], 6) == 0.001 and round(premiers[1], 9) == 0.000999999 and round(premiers[2], 6) == -0.001
    assert round(premiers[3], 7) == 0.0000909 and math.isclose(premiers[4], 0.0005) and math.isclose(premiers[5], 0.0009)
    print(f"démonstration 2 : premiers pas {[float(f'{p:.4g}') for p in premiers]}")
    # démonstration 3 : invariance d'échelle
    gs = [0.3, -1.2, 2.0, 0.7]
    base = pas_adam(gs)
    assert all(math.isclose(a, b, rel_tol=1e-6) for a, b in zip(base, pas_adam([100 * x for x in gs])))
    assert [round(p, 5) for p in base] == [0.001, -0.00056, 0.00032, 0.00041]
    minuscule = pas_adam([1e-8 * x for x in gs])
    assert round(minuscule[0], 5) == 0.00023
    print(f"démonstration 3 : pas {[round(p, 5) for p in base]} identiques ×100 ; ×1e-8 : premier pas {minuscule[0]:.5f}")
    # démonstration 4 : pas effectif α / (√v̂ + ε)
    _, (m_g, v_g, t_g) = adam_etat([1000.0] * 3)
    _, (m_p, v_p, t_p) = adam_etat([0.01] * 3)
    eff_g = 0.001 / (math.sqrt(v_g / (1 - B2 ** 3)) + EPS)
    eff_p = 0.001 / (math.sqrt(v_p / (1 - B2 ** 3)) + EPS)
    assert math.isclose(v_g / (1 - B2 ** 3), 1e6) and math.isclose(v_p / (1 - B2 ** 3), 1e-4)
    assert math.isclose(eff_g, 1e-6, rel_tol=1e-6) and math.isclose(eff_p, 0.1, rel_tol=1e-5)
    assert math.isclose(eff_p / eff_g, 1e5, rel_tol=1e-5) and math.isclose(eff_g * 1000, 0.001, rel_tol=1e-6)
    print(f"démonstration 4 : pas effectif {eff_g:.1e} (gradients 1 000) et {eff_p:.4f} (gradients 0,01)")
    # démonstration 5 : borne du pas
    egal, _ = pas_poids_rare(0.9)
    defaut, (m_r, v_r, _) = pas_poids_rare(0.999)
    rare_099, _ = pas_poids_rare(0.99)
    assert round(egal, 5) == 0.80705 and round(defaut, 5) == 2.10737 and round(rare_099, 5) == 1.72279
    assert math.isclose(borne_pas(110, 0.9, 0.9), 1.0) and round(borne_pas(110), 5) == 2.34704
    assert round(borne_pas(110, b2=0.99), 5) == 1.91817 and round(borne_pas(10 ** 6, b2=0.99), 5) == 2.34521
    assert round(0.1 / math.sqrt(1 - 0.999), 5) == 3.16228 and round(1 / math.sqrt(1 - 0.81 / 0.999), 5) == 2.29907
    assert round(borne_pas(10 ** 6), 5) == 7.27029 and round(0.1 / math.sqrt(1 - 0.99), 6) == 1.0
    assert egal <= 1 and defaut <= borne_pas(110) and rare_099 <= borne_pas(110, b2=0.99) and rare_099 > 1
    print(f"démonstration 5 : poids rare {egal:.5f} (β1 = β2), {defaut:.5f} (borne {borne_pas(110):.5f}),"
          f" {rare_099:.5f} avec β2 = 0.99 (borne {borne_pas(110, b2=0.99):.5f})")
    # démonstration 6 : correction absente, partielle, compteur remis à zéro
    sans = [adam_etat([2.0] * t, corriger=False)[0][-1] / 0.001 for t in (1, 10, 100, 1000)]
    m_seul = adam_etat([2.0], corriger="m")[0][0] / 0.001
    remis = [facteur_compteur_remis(t) for t in (1, 10, 100, 1000)]
    assert [round(x, 3) for x in sans] == [3.162, 6.528, 3.241, 1.258] and round(m_seul, 3) == 31.623
    assert [round(x, 4) for x in remis] == [0.3162, 0.1532, 0.3086, 0.7952] and round(remis[0], 5) == 0.31623
    assert round(math.sqrt(1000), 1) == 31.6
    print(f"démonstration 6 : sans correction {[round(x, 3) for x in sans]} ; m seul {m_seul:.3f} ;"
          f" compteur remis {[round(x, 4) for x in remis]}")

    c1 = cas_1_echelles_crypto()
    assert c1["sgd_w1"] == 1 and math.isclose(c1["sgd_w2"], 1e-5) and round(c1["sgd_n_w2"]) == 5_000
    assert math.isclose(c1["pas_stable"], 1e-5) and math.isclose(c1["stable_w2"], 1e-7) and round(c1["stable_n_w2"]) == 500_000
    assert all(round(p, 6) == 0.001 for p in c1["adam_w1"] + c1["adam_w2"]) and c1["adam_n_w2"] == 50
    assert [round(p, 5) for p in c1["hesite"]] == [0.001, 0.00027, 0.00064] and round(sum(c1["hesite"]), 4) == 0.0019
    assert all(round(p, 6) == 0.001 for p in c1["corrompu"]) and math.isclose(1e-5 * 100_000, 1)
    assert round(500_000 / 200) == 2_500 and 50 <= 200 and math.isclose(1 / 0.01, 100)

    c2 = cas_2_reprise_banque()
    assert math.isclose(c2["normal"], 4e-5) and round(c2["a"], 8) == 3.988e-5 and round(c2["a"] / c2["normal"], 3) == 0.997
    assert round(c2["b"], 8) == 2e-4 and round(c2["b"] / c2["normal"], 2) == 5.0
    assert math.isclose(c2["m1"], 0.02) and math.isclose(c2["v1"], 0.0099904) and round(c2["c"], 9) == 1.2655e-5
    assert round(c2["c"] / c2["normal"], 4) == 0.3164 and c2["recup"] == 1_660 and round(c2["minutes"], 1) == 33.2
    assert c2["recup_099"] == 166 and math.isclose(0.1 / 0.02, 5) and math.isclose(0.02 / 0.1, 0.2)
    assert math.isclose(0.0099904 / 0.001, 9.9904)

    c3 = cas_3_quartier_rare_immo()
    assert round(m_r, 5) == 0.65132 and round(v_r, 7) == 0.0099551 and round(1 - 0.9 ** 10, 5) == 0.65132
    assert round(1 - 0.9 ** 110, 5) == 0.99999 and round(1 - 0.999 ** 110, 5) == 0.10422
    assert round(m_r / (1 - 0.9 ** 110), 5) == 0.65133 and round(v_r / (1 - 0.999 ** 110), 6) == 0.095525
    assert round(math.sqrt(v_r / (1 - 0.999 ** 110)), 5) == 0.30907
    assert [round(c3[b][0], 5) for b in (0.999, 0.99, 0.98, 0.95)] == [2.10737, 1.72279, 1.43799, 1.02639]
    assert round(c3["bascule"], 5) == 0.98256 and c3["choix"] == 0.98 and round(c3[0.98][0], 3) == 1.438
    assert [round(x) for x in c3["memoire"].values()] == [999, 99, 49, 19] and round(400 * 0.3) == 120
    assert round(c3[0.95][0], 2) == 1.03 and round(c3[0.99][0], 2) == 1.72

    c4 = cas_4_lot_aberrant_rh()
    assert round(1 - 0.999 ** 5, 7) == 0.00499 and round(0.9 * 0.40951 + 10, 5) == 10.36856
    assert round(0.999 * (1 - 0.999 ** 5) + 10, 5) == 10.00499 and round(1 - 0.9 ** 6, 5) == 0.46856
    assert round(1 - 0.999 ** 6, 7) == 0.005985
    _, (m6, v6, _) = adam_etat([1.0] * 5 + [100.0])
    assert round(m6 / (1 - 0.9 ** 6), 5) == 22.12861 and round(v6 / (1 - 0.999 ** 6), 2) == 1671.67
    assert round(math.sqrt(v6 / (1 - 0.999 ** 6)), 3) == 40.886
    assert round(c4["choc"], 6) == 0.000541 and round(c4["apres"], 6) == 0.000478
    assert round(c4["choc5"], 6) == 0.000828 and round(c4["apres5"], 6) == 0.000802
    assert c4["recup"] == {None: 3_774, 3: 1, 4: 56, 5: 92, 6: 134, 10: 348} and c4["choix"] == 5
    assert 3_774 - 92 == 3_682 and round(1 - 2 / 3, 2) == 0.33

    print("Corrigé")
    m2 = B1 * 0.4 + (1 - B1) * 4
    ex6, (_, v6_099, _) = pas_poids_rare(0.99)
    print(f"  ex1 m2 = {m2:.2f}, m̂2 = {m2 / (1 - B1 ** 2):.0f} ; ex4 pas = {pas_adam([1e-9])[0]:.7f} ; ex6 pas = {ex6:.5f} α")
    assert math.isclose(m2, 0.76) and math.isclose(m2 / (1 - B1 ** 2), 4) and math.isclose(1 - B1 ** 2, 0.19)
    assert round(pas_adam([1e-9])[0], 7) == 0.0000909 and math.isclose(0.001 / 11, pas_adam([1e-9])[0])
    assert round(v6_099, 6) == 0.095618 and round(1 - 0.99 ** 110, 5) == 0.66897
    assert round(v6_099 / (1 - 0.99 ** 110), 5) == 0.14293 and round(math.sqrt(v6_099 / (1 - 0.99 ** 110)), 5) == 0.37807
    try:
        adam_etat([1.0], b2=1.0)
    except ValueError:
        print("  β2 = 1 refusé : la correction diviserait par 1 − 1^t = 0")
    else:
        raise AssertionError("β2 = 1 aurait dû être refusé")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
m1 = 0.2 ; v1 = 0.004 ; m̂1 = 2.0 ; v̂1 = 4.0 ; pas = 0.001000
film 2, -1, 3 : m = 0.08 puis 0.372 ; pas [0.001, 0.00027, 0.00064]
démonstration 1 : g = 7 → m = [0.7, 1.33, 1.897, 2.4073, 2.86657], m̂ = 7 à chaque pas
démonstration 2 : premiers pas [0.001, 0.001, -0.001, 9.091e-05, 0.0005, 0.0009]
démonstration 3 : pas [0.001, -0.00056, 0.00032, 0.00041] identiques ×100 ; ×1e-8 : premier pas 0.00023
démonstration 4 : pas effectif 1.0e-06 (gradients 1 000) et 0.1000 (gradients 0,01)
démonstration 5 : poids rare 0.80705 (β1 = β2), 2.10737 (borne 2.34704), 1.72279 avec β2 = 0.99 (borne 1.91817)
démonstration 6 : sans correction [3.162, 6.528, 3.241, 1.258] ; m seul 31.623 ; compteur remis [0.3162, 0.1532, 0.3086, 0.7952]
Cas 1 [CRYPTO] : descente simple Δw1 = 1, Δw2 = 1e-05 ; pas stable → 500,000 pas pour w2 ; Adam → 50 pas
  Adam : [0.001, 0.001, 0.001] et [0.001, 0.001, 0.001] ; gradients 2, -1, 3 : [0.001, 0.00027, 0.00064]
Cas 2 [BANQUE] : pas normal 4.0e-05 ; A 0.997 × ; B 5.00 × ; C 0.3164 ×, retour à 90 % au pas 1660 (33.2 min)
Cas 3 [IMMO] : pas du poids rare / α : β2 = 0.999 → 2.10737 ; β2 = 0.99 → 1.72279 ; β2 = 0.98 → 1.43799 ; β2 = 0.95 → 1.02639 ;
  bascule β2 = 0.98256 pour 1.5 α ; choix β2 = 0.98
Cas 4 [RH] : pas du choc 0.000541, suivant 0.000478 ; récupération sans écrêtage 3774 pas
  avec écrêtage : c = 3 → 1 ; c = 4 → 56 ; c = 5 → 92 ; c = 6 → 134 ; c = 10 → 348 ; choix c = 5
Corrigé
  ex1 m2 = 0.76, m̂2 = 4 ; ex4 pas = 0.0000909 ; ex6 pas = 1.72279 α
  β2 = 1 refusé : la correction diviserait par 1 − 1^t = 0
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme met à jour un paramètre avec Adam : deux moyennes mobiles du gradient, corrigées de leur biais, puis un pas normalisé ; une option écrête le gradient, et l'état (m, v, t) peut être repris d'un point de sauvegarde.

```text
ALGORITHME Adam
ENTRÉES : gradients g₁ … gₙ d'un paramètre, α > 0, β₁ et β₂ dans [0 ; 1[, ε ≥ 0,
          état de départ (m, v, t), seuil d'écrêtage c ou RIEN
SORTIE  : les pas successifs et l'état final (m, v, t)

  SI α ≤ 0 OU β₁ ∉ [0 ; 1[ OU β₂ ∉ [0 ; 1[ OU ε < 0 ALORS ERREUR « hyperparamètres invalides »
  POUR CHAQUE gradient g FAIRE
      SI c existe ALORS g ← max(−c, min(c, g))
      t ← t + 1
      m ← β₁ × m + (1 − β₁) × g
      v ← β₂ × v + (1 − β₂) × g²
      m̂ ← m / (1 − β₁ puissance t)
      v̂ ← v / (1 − β₂ puissance t)
      pas ← α × m̂ / (√v̂ + ε)
      θ ← θ − pas
  FIN POUR
  RETOURNER les pas, (m, v, t)

ALGORITHME SeuilDÉcrêtage
ENTRÉES : budget de récupération R pas, plus petit seuil admissible c_min
SORTIE  : le plus grand c ≥ c_min dont la récupération après un choc tient en R pas

  POUR c DE c_min À une borne haute FAIRE
      rejouer Adam sur la suite avec choc, écrêtée à c
      compter les pas jusqu'au retour à 0,9 α
  FIN POUR
  RETOURNER le plus grand c dont le compte est ≤ R
```

**Complexité.** O(1) par pas et par paramètre, soit O(n × P) pour n pas sur P paramètres. La mémoire double par rapport à une descente simple : deux nombres (m et v) en plus de chaque paramètre, et un compteur t commun. SeuilDÉcrêtage rejoue au plus H pas pour chacun des seuils essayés, soit O(K × H) pour K seuils et un horizon H ; c'est un calcul hors ligne, fait une fois avant l'entraînement.

**Du squelette au code.** L'algorithme est la fonction `adam_etat(gradients, alpha, b1, b2, eps, etat, corriger, ecretage)`, qui renvoie les pas et l'état final sans tenir de paramètre : la ligne θ ← θ − pas s'ajoute quand on l'utilise dans une vraie descente. `pas_adam(gradients, alpha)` l'appelle avec les valeurs usuelles ; `main` l'applique à des gradients de 1 000 et de 0,01, puis à la suite (2 ; −1 ; 3), et vérifie la correction du biais et l'invariance d'échelle. La borne de la démonstration 5 est `borne_pas(t, b1, b2)`, le facteur du compteur remis à zéro `facteur_compteur_remis(t, b1, b2)`, le scénario du poids rare `pas_poids_rare(b2, b1)`. SeuilDÉcrêtage est `recuperation(ecretage, seuil, horizon)` appelée dans `cas_4_lot_aberrant_rh`. Les autres cas sont `cas_1_echelles_crypto`, `cas_2_reprise_banque` et `cas_3_quartier_rare_immo`.
