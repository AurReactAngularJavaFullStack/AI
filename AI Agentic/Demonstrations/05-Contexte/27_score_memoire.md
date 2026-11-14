# 27 — Score de mémoire : démonstrations

> Fiche : [27 — Score de mémoire](<../../Images/05-Contexte/27_score_memoire.md>) · Image : `27_score_memoire.jpg` · Leçon : [Étape 16 — Décroissance d'un souvenir](<../../04-Contexte-Similarite-et-Memoire/16-Memoire-Formule-Decroissance-Temporelle.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
\operatorname{score}(m) = \alpha \times \operatorname{récence}(m) + \beta \times \operatorname{importance}(m) + \gamma \times \operatorname{pertinence}(m, q)
$$

Pour choisir quels souvenirs injecter dans le contexte, on combine trois signaux : depuis quand on n'a pas utilisé le souvenir, son importance, et sa proximité avec la question q (souvent un cosinus, fiche 03). La récence la plus courante est une décroissance exponentielle :

$$
\operatorname{récence}(m) = \delta^{\,\Delta t}, \qquad 0 < \delta < 1
$$

Δt est le temps écoulé, en heures ici, et δ le facteur d'oubli par heure.

## Les symboles, un par un

$$
m, \quad q
$$

m est un souvenir de la mémoire longue de l'agent (un fait, une préférence, un statut) ; q est la question ou la tâche en cours. Variables Python : les clés du dictionnaire `souvenirs`, et la question implicite dans les pertinences.

$$
\alpha, \quad \beta, \quad \gamma
$$

Les poids de la récence, de l'importance et de la pertinence. Réels ≥ 0, de somme 1 dans ce fichier (par exemple 0,3, 0,3 et 0,4). La leçon de l'étape 17 les appelle poids de récence, d'importance et de similarité. Variable Python : le triplet `POIDS`, ou l'argument `poids`.

$$
\operatorname{récence}(m)
$$

La fraîcheur du souvenir, δ^Δt. Réel dans ]0 ; 1], qui vaut 1 au moment du dernier accès et ne s'annule jamais. Variable Python : la valeur renvoyée par `recence(heures, delta)`.

$$
\operatorname{importance}(m)
$$

Le poids propre du souvenir, fixé quand il est écrit (un refus ferme compte plus qu'une question d'horaire). Réel ramené dans [0 ; 1]. Variable Python : `importance`.

$$
\operatorname{pertinence}(m, q)
$$

La proximité entre le souvenir et la question, souvent la similarité cosinus de leurs vecteurs. Réel dans [0 ; 1] une fois ramené à cette échelle. Variable Python : `pertinence`.

$$
\delta
$$

Le facteur d'oubli : la fraction de récence conservée par unité de temps. Réel dans ]0 ; 1[, par exemple 0,995 par heure. La leçon de l'étape 16 l'écrit q, lettre réservée ici à la question. Variable Python : `delta`.

$$
\Delta t
$$

Le temps écoulé depuis le dernier accès au souvenir, dans l'unité de δ. Réel ≥ 0. Variable Python : `heures` (ou `jours` dans les cas).

$$
\lambda = -\ln \delta, \qquad t_{1/2}
$$

λ est le taux de décroissance de la forme continue e^(−λΔt) de l'étape 16, et t½ la demi-vie, le temps au bout duquel la récence vaut 1/2. Réels > 0. Variable Python : `demi_vie`.

$$
\operatorname{score}(m)
$$

Le résultat : un réel dans [0 ; 1] quand les trois signaux y sont et que les poids somment à 1. L'agent injecte les k souvenirs de plus grand score. Variable Python : le dictionnaire `s`, qui associe un score à chaque souvenir.

## Le mécanisme, avant les preuves

La formule reçoit trois nombres par souvenir, chacun dans [0 ; 1], et les mélange en une moyenne pondérée. La récence est elle-même calculée à partir du temps : à chaque heure sans accès, elle est multipliée par δ, donc elle perd toujours la même fraction de ce qui lui reste (0,5 % par heure pour δ = 0,995). C'est pourquoi on prend une puissance δ^Δt et non une pente : la perte est rapide au début et de plus en plus lente, et la récence n'atteint jamais zéro. L'importance est fixée à l'écriture du souvenir et ne bouge pas ; la pertinence dépend de la question du moment et change à chaque tour. Chaque signal est multiplié par son poids, qui dit combien il compte ; la somme des trois produits donne le score. On additionne au lieu de multiplier parce qu'un produit annulerait le score dès qu'un signal est faible : un refus ferme exprimé il y a trois semaines aurait une récence de 0,08 et disparaîtrait, alors qu'il reste décisif. Avec une somme, un signal fort compense un signal faible, mais seulement dans la limite de son poids : la récence ne peut jamais apporter plus que α. Les poids de somme 1 gardent le score dans [0 ; 1], ce qui rend un seuil comparable d'une question à l'autre. Enfin, le score ne supprime rien : il classe.

Petit film chiffré, avec α = 0,3, β = 0,3, γ = 0,4 et δ = 0,995 par heure. Souvenir m₁, vu il y a 2 heures, importance 0,3, cosinus 0,6 : récence 0,995² ≈ 0,99003, pondérée 0,3 × 0,99003 ≈ 0,29701 ; importance pondérée 0,3 × 0,3 = 0,09 ; pertinence pondérée 0,4 × 0,6 = 0,24 ; score 0,29701 + 0,09 + 0,24 = 0,62701. Souvenir m₃, vu il y a 500 heures, importance 1, cosinus 0,95 : récence 0,995⁵⁰⁰ ≈ 0,08157, pondérée 0,02447 ; importance pondérée 0,3 ; pertinence pondérée 0,38 ; score 0,70447. Le souvenir ancien passe devant le récent, parce que ses deux signaux stables pèsent 0,68 contre 0,33. En Java, c'est le tri d'un cache par une note composite (âge, priorité, correspondance à la requête) plutôt que par la seule date d'accès d'un cache LRU.

## Démonstration 1 — Avec des poids qui somment à 1, le score reste entre 0 et 1

**Ce qu'on démontre.** Si les trois composantes r, i, p sont dans [0 ; 1] et si α, β, γ ≥ 0 avec α + β + γ = 1, alors le score est une moyenne pondérée et :

$$
\min(r, i, p) \le \alpha r + \beta i + \gamma p \le \max(r, i, p), \qquad 0 \le \alpha r + \beta i + \gamma p \le 1
$$

**L'idée.** Une moyenne pondérée à poids positifs reste entre la plus petite et la plus grande des valeurs moyennées.

**La preuve, pas à pas.**

**Étape 1.** On note M = max(r, i, p). Chaque composante est ≤ M, et les poids sont positifs, donc chaque produit est majoré : αr ≤ αM, βi ≤ βM, γp ≤ γM.

**Étape 2.** On additionne les trois inégalités et l'on met M en facteur, parce que α + β + γ = 1 :

$$
\alpha r + \beta i + \gamma p \le (\alpha + \beta + \gamma) M = M \le 1
$$

**Étape 3.** Le même raisonnement avec le minimum donne la borne basse, et le minimum est ≥ 0. ∎

**Vérification chiffrée.** Pour m₁ : composantes 0,99003, 0,3 et 0,6 ; score 0,62701, bien entre 0,3 et 0,99003. Le programme essaie les 27 combinaisons de composantes dans {0 ; 0,5 ; 1} et vérifie 0 ≤ score ≤ 1. Contre-exemple quand les poids ne somment pas à 1 : avec α = β = γ = 0,5, un souvenir (1 ; 1 ; 1) obtient 1,5, et un seuil de 0,6 n'a plus le même sens selon le réglage des poids.

**Ce que la preuve révèle du mécanisme.** Le score ne peut pas dépasser le meilleur des trois signaux : un souvenir n'est jamais « plus pertinent que pertinent ». Chaque poids est le plafond de la contribution de son signal : la récence apporte au plus α.

**Conséquence pour un agent.** Avec des poids de somme 1 et des signaux dans [0 ; 1], un seuil (par exemple « n'injecter qu'au-dessus de 0,6 ») garde un sens stable d'une question à l'autre ; on vérifie ces deux conditions dans le code par des gardes.

## Démonstration 2 — La demi-vie, et ce que coûte une heure de plus

**Ce qu'on démontre.** La demi-vie t½, durée qui divise la récence par deux, vaut

$$
t_{1/2} = \frac{\ln 2}{\ln(1/\delta)} = \frac{\ln 2}{\lambda}, \qquad \lambda = -\ln \delta
$$

et, après k demi-vies, la récence vaut (1/2)ᵏ.

**L'idée.** δ^Δt = 1/2 est une équation exponentielle ; le logarithme la transforme en équation du premier degré.

**La preuve, pas à pas.**

**Étape 1.** On écrit la condition de demi-vie, δ^t½ = 1/2, et l'on prend le logarithme népérien des deux membres, parce que ln(aˣ) = x ln a :

$$
t_{1/2} \ln \delta = \ln \frac{1}{2} = -\ln 2
$$

**Étape 2.** On divise par ln δ, qui est négatif puisque 0 < δ < 1 ; le signe moins disparaît avec ln δ = −ln(1/δ) :

$$
t_{1/2} = \frac{-\ln 2}{\ln \delta} = \frac{\ln 2}{\ln(1/\delta)}
$$

**Étape 3.** Après k demi-vies, δ^(k t½) = (δ^t½)ᵏ = (1/2)ᵏ, parce que les exposants se multiplient. ∎

**Vérification chiffrée.** δ = 0,995 par heure : λ = −ln 0,995 ≈ 0,0050125, et t½ = 0,69315/0,0050125 ≈ 138,3 heures, soit environ 5,8 jours. Le programme vérifie que 0,995^138,28 vaut bien 0,5. Après deux demi-vies, la récence vaut 1/4.

**Ce que la preuve révèle du mécanisme.** La dérivée de αδ^Δt par rapport au temps vaut −αλδ^Δt : une heure de plus coûte au score environ α × λ × récence. Pour un souvenir frais, c'est 0,3 × 0,0050125 ≈ 0,0015 par heure ; pour le souvenir de 500 heures, 0,3 × 0,0050125 × 0,08157 ≈ 0,00012 par heure. La récence pèse surtout sur les souvenirs récents ; elle ne départage presque plus les souvenirs anciens.

**Conséquence pour un agent.** On règle δ à partir d'une demi-vie qui a un sens métier (« une préférence vaut moitié moins au bout d'un mois »), puis δ = 2^(−1/t½). C'est plus lisible pour l'équipe qu'un facteur comme 0,995.

## Démonstration 3 — Quand un vieux souvenir important bat un souvenir récent, et à quel âge le classement bascule

**Ce qu'on démontre.** Soit A un souvenir d'âge Δt (importance i(A), pertinence p(A)) et B un souvenir de score S(B). Si

$$
\beta\, i_A + \gamma\, p_A > S_B
$$

alors A bat B quel que soit son âge. Sinon, A bat B si et seulement si

$$
\Delta t < \frac{\ln\left(\dfrac{S_B - \beta i_A - \gamma p_A}{\alpha}\right)}{\ln \delta}
$$

(quand la fraction est dans ]0 ; 1[ ; si elle est ≥ 1, A ne bat jamais B).

**L'idée.** La récence de A ne peut que baisser, vers 0 : la partie fixe β i(A) + γ p(A) est le score plancher de A. S'il dépasse déjà S(B), l'âge n'y peut rien ; sinon, il existe un âge exact où A passe derrière B.

**La preuve, pas à pas.**

**Étape 1.** Le score de A vaut α δ^Δt + β i(A) + γ p(A), et α δ^Δt > 0, donc score(A) > β i(A) + γ p(A). Si ce plancher dépasse S(B), A gagne à tout âge.

**Étape 2.** Sinon, A gagne si et seulement si α δ^Δt > S(B) − β i(A) − γ p(A). On divise par α > 0 :

$$
\delta^{\Delta t} > \frac{S_B - \beta i_A - \gamma p_A}{\alpha}
$$

**Étape 3.** On prend le logarithme, fonction croissante, puis l'on divise par ln δ < 0, ce qui renverse l'inégalité et donne la condition annoncée. ∎

**Vérification chiffrée.** Avec les poids 0,3 ; 0,3 ; 0,4, le souvenir m₃ (importance 1, cosinus 0,95) a pour plancher 0,3 + 0,38 = 0,68, au-dessus du score de m₁ (0,62701) : m₃ bat m₁ à tout âge. C'est la forme de l'ancienne version de ce fichier, β × 0,7 + γ × 0,35 = 0,21 + 0,14 = 0,35 > α × 0,99 ≈ 0,297, qui compare les écarts d'importance et de pertinence à la récence de m₁. Le programme vérifie m₃ contre m₁ à 500, 5 000 et 50 000 heures. Contre-exemple quand le plancher est trop bas : m₂ (importance 0,9, cosinus 0,8) a un plancher de 0,27 + 0,32 = 0,59, sous le score de m₃ (0,70447) ; son avance dépend donc de son âge, et la démonstration chiffre la bascule au cas 1.

**Ce que la preuve révèle du mécanisme.** Le temps ne peut retirer à un souvenir que sa part de récence, au plus α. Les souvenirs dont le plancher est haut sont protégés de l'oubli dans le classement ; les autres ont une date de péremption calculable.

**Conséquence pour un agent.** Pour qu'une contrainte critique (un refus, une allergie, une interdiction réglementaire) ne sorte jamais du top-k, on lui donne une importance qui place son plancher au-dessus des scores habituels, ou on la sort du classement et on l'injecte toujours.

## Démonstration 4 — Les échelles doivent être comparables

**Ce qu'on démontre.** Si l'une des composantes est exprimée sur [0 ; c] au lieu de [0 ; 1], son terme est multiplié par c, et pour c assez grand le classement ne dépend plus que de cette composante. La normalisation min-max de l'étape 17 ramène chaque composante dans [0 ; 1] :

$$
\widetilde{x}_j = \frac{x_j - \min_i x_i}{\max_i x_i - \min_i x_i}
$$

avec la convention x̃ⱼ = 0 pour tous les j quand toutes les valeurs sont égales.

**L'idée.** Dans une somme, le terme qui varie le plus décide de l'ordre. Une composante dix fois plus étalée que les autres écrase les deux autres, quels que soient les poids choisis.

**La preuve, pas à pas.**

**Étape 1.** Pour deux souvenirs j et k, l'écart de score est la somme des écarts pondérés : α(rⱼ − rₖ) + β(iⱼ − iₖ) + γ(pⱼ − pₖ).

**Étape 2.** Les écarts de récence et de pertinence sont au plus 1 en valeur absolue, parce que ces composantes sont dans [0 ; 1] ; leur contribution est donc au plus α + γ. Si l'importance est sur [0 ; c], l'écart d'importance pondéré vaut c β (ĩⱼ − ĩₖ), où ĩ est l'importance ramenée sur [0 ; 1].

**Étape 3.** Dès que c β |ĩⱼ − ĩₖ| > α + γ, le signe de l'écart de score est celui de l'écart d'importance : l'importance seule décide. ∎

**Vérification chiffrée.** Dans le cas 4, deux souvenirs ont des importances 0,9 et 0,3 sur [0 ; 1] ; notées 9 et 3 sur [0 ; 10], l'écart pondéré passe de 0,3 × 0,6 = 0,18 à 0,3 × 6 = 1,8, plus que α + γ = 0,7 : le souvenir le plus pertinent pour la question tombe en dernière position. La normalisation min-max de (2 ; 5 ; 8) donne (0 ; 0,5 ; 1). Contre-exemple de la convention : sans elle, (4 ; 4 ; 4) donnerait 0/0 ; la convention de l'étape 17 donne (0 ; 0 ; 0), ce qui retire honnêtement une composante qui ne départage personne.

**Ce que la preuve révèle du mécanisme.** Les poids n'ont de sens qu'entre composantes de même échelle : changer l'échelle d'une composante revient à multiplier son poids en cachette.

**Conséquence pour un agent.** On normalise chaque composante avant de pondérer, et l'on refuse (ValueError) une importance hors de [0 ; 1] au lieu de la laisser fausser le classement ; une importance notée de 1 à 10 par le modèle se divise par 10.

## Démonstration 5 — Changer d'unité de temps oblige à changer δ

**Ce qu'on démontre.** Si δₕ est le facteur d'oubli par heure, le facteur par jour qui donne la même courbe est

$$
\delta_j = \delta_h^{24}
$$

et la demi-vie, exprimée en jours, est la même. Utiliser δₕ comme s'il était journalier multiplie la demi-vie par 24.

**L'idée.** Un jour, c'est 24 multiplications successives par δₕ ; la courbe ne doit pas dépendre de l'unité choisie pour l'écrire.

**La preuve, pas à pas.**

**Étape 1.** Un âge de Δt heures vaut Δt/24 jours. On veut δⱼ^(Δt/24) = δₕ^Δt pour tout Δt.

**Étape 2.** On écrit δₕ^Δt = (δₕ²⁴)^(Δt/24), parce que les exposants se multiplient : 24 × Δt/24 = Δt. Donc δⱼ = δₕ²⁴ convient.

**Étape 3.** La demi-vie en jours vaut ln 2/(−ln δⱼ) = ln 2/(−24 ln δₕ), c'est-à-dire la demi-vie en heures divisée par 24 : la même durée. ∎

**Vérification chiffrée.** δₕ = 0,995 donne δⱼ = 0,995²⁴ ≈ 0,88665 par jour, et une demi-vie de 5,76 jours, soit 138,3 heures. Contre-exemple de l'erreur d'unité : appliquer 0,995 « par jour » donne une demi-vie de 138,3 jours, plus de quatre mois, et un vieux critère abandonné reste en tête du classement 24 fois trop longtemps.

**Ce que la preuve révèle du mécanisme.** δ n'a pas de sens sans son unité : c'est un couple (valeur, unité). La demi-vie, elle, est une durée, compréhensible quelle que soit l'unité.

**Conséquence pour un agent.** On stocke la demi-vie dans la configuration, avec son unité dans le nom (`demi_vie_heures`), et l'on calcule δ au chargement ; l'horloge de la mémoire utilise une seule unité.

## Exemple simple, à la main

Poids α = 0,3, β = 0,3, γ = 0,4. Souvenir A, récent mais peu utile : récence 0,95, importance 0,2, pertinence 0,3. Souvenir B, ancien mais important et pertinent : récence 0,4, importance 0,9, pertinence 0,85.

| Terme | Souvenir A | Souvenir B |
| --- | --- | --- |
| α × récence | 0,3 × 0,95 = 0,285 | 0,3 × 0,4 = 0,12 |
| β × importance | 0,3 × 0,2 = 0,06 | 0,3 × 0,9 = 0,27 |
| γ × pertinence | 0,4 × 0,3 = 0,12 | 0,4 × 0,85 = 0,34 |
| score | 0,285 + 0,06 + 0,12 = 0,465 | 0,12 + 0,27 + 0,34 = 0,73 |

$$
\operatorname{score}(A) = 0{,}285 + 0{,}06 + 0{,}12 = 0{,}465, \qquad \operatorname{score}(B) = 0{,}12 + 0{,}27 + 0{,}34 = 0{,}73
$$

B passe devant malgré son âge : son plancher β × 0,9 + γ × 0,85 = 0,27 + 0,34 = 0,61 dépasse déjà le score de A (démonstration 3). La fiche prend d'autres valeurs (A : 0,9 ; 0,3 ; 0,5, score 0,56 ; B : 0,2 ; 0,9 ; 0,85, score 0,67) et conclut de même.

## Cas d'usage complexes, démontrés

### Cas 1 — [IMMO] Une agence à Dubaï : trois souvenirs d'un client acheteur

**Contexte.** Une agence immobilière de Dubaï accompagne ses acheteurs avec un agent qui garde en mémoire chaque critère exprimé. Pour la question du jour, « quels biens proposer cette semaine ? », trois souvenirs sont candidats et l'agent n'en injecte que k = 2 dans le prompt. Les valeurs d'importance et de pertinence sont illustratives.

**Données.**

- poids : α = 0,3, β = 0,3, γ = 0,4 ; facteur d'oubli : δ = 0,995 par heure ; souvenirs injectés : k = 2 ;
- m₁ : vu il y a 2 h, importance 0,3, cosinus 0,6 (« le client a demandé l'horaire d'une visite ») ;
- m₂ : vu il y a 72 h, importance 0,9, cosinus 0,8 (« budget relevé à 2,4 M AED ») ;
- m₃ : vu il y a 500 h, importance 1, cosinus 0,95 (« refuse tout bien au rez-de-chaussée »).

**Calcul pas à pas.**

**Étape 1.** Les récences, arrondies à cinq décimales :

$$
0{,}995^{2} \approx 0{,}99003, \qquad 0{,}995^{72} \approx 0{,}69705, \qquad 0{,}995^{500} \approx 0{,}08157
$$

**Étape 2.** Les scores, par la formule :

$$
\operatorname{score}(m_1) \approx 0{,}62701, \qquad \operatorname{score}(m_2) \approx 0{,}79911, \qquad \operatorname{score}(m_3) \approx 0{,}70447
$$

par exemple pour m₂ : 0,3 × 0,69705 + 0,3 × 0,9 + 0,4 × 0,8 ≈ 0,20911 + 0,27 + 0,32 = 0,79911.

**Étape 3.** Le classement : m₂, m₃, m₁. Les deux injectés sont m₂ et m₃.

**Étape 4.** La garantie de la démonstration 3 : le plancher de m₃, 0,68, dépasse le score de m₁ : m₃ reste devant m₁ quel que soit son âge.

**Décision de l'agent.** L'agent injecte le budget relevé et le refus du rez-de-chaussée, et propose des biens en étage dans le nouveau budget. Le refus, vieux de trois semaines, reste devant la question d'horaire d'il y a deux heures.

**Contre-calcul.** Un agent qui ne garderait que les deux souvenirs les plus récents (une fenêtre glissante de mémoire) injecterait m₁ et m₂ et perdrait le refus : il proposerait des rez-de-chaussée, le client refuserait les visites, et l'agence perdrait une semaine de suivi. À l'inverse, la pertinence seule donnerait ici le même top-2 que le score, mais elle ne verrait pas qu'un souvenir non relu depuis longtemps doit finir par céder sa place.

**Sensibilité.** Si aucun des trois souvenirs n'est relu, m₃ finit par dépasser m₂. Après τ heures supplémentaires, l'écart vaut 0,3 δ^τ (0,69705 − 0,08157) + (0,27 + 0,32) − (0,3 + 0,38) ≈ 0,18464 δ^τ − 0,09, positif tant que δ^τ > 0,09/0,18464 ≈ 0,4874, c'est-à-dire τ < ln(0,4874)/ln(0,995) ≈ 143,4 heures. La valeur de bascule est donc d'environ 6 jours : au-delà, le refus passe devant le budget.

**En production.** On suit la part des souvenirs injectés qui sont repris dans la réponse de l'agent, et le taux de visites refusées pour un critère déjà exprimé (alerte au-dessus de 5 %, valeur illustrative). Le score n'efface rien : une demande d'effacement d'un client relève de la PDPL hors zones franches financières et demande une vraie suppression, à confirmer avec le texte en vigueur.

### Cas 2 — [BANQUE] Une banque de détail de Dubaï : un profil de risque qui vieillit

**Contexte.** L'assistant d'investissement d'une banque de détail de Dubaï garde en mémoire l'appétit pour le risque déclaré par le client au dernier entretien (« prudent »). La politique interne veut qu'un profil ancien ne serve plus à recommander un produit sans nouvelle vérification. L'équipe a d'abord voulu traduire cette règle par le seul score de mémoire, avec un seuil d'injection de 0,6. Les réglages sont illustratifs.

**Données.**

- temps en jours ; demi-vie du profil : 180 jours ; poids : α = 0,3, β = 0,3, γ = 0,4 ;
- souvenir « profil prudent » : importance 1, pertinence 0,9 pour la question « quel fonds proposer ? » ;
- règle de fraîcheur : récence ≥ 0,3, sinon les questions d'adéquation sont reposées ; seuil d'injection du score : 0,6 ;
- âge du profil au moment de la question : 365 jours.

**Calcul pas à pas.**

**Étape 1.** Le facteur journalier, par la démonstration 2 :

$$
\delta = 2^{-1/180} \approx 0{,}99616
$$

**Étape 2.** La récence après un an :

$$
2^{-365/180} \approx 0{,}24523 < 0{,}3
$$

**Étape 3.** Le jour où la récence passe sous 0,3 : 180 × log₂(1/0,3) ≈ 312,65, donc au 313e jour.

**Étape 4.** Le score après un an :

$$
0{,}3 \times 0{,}24523 + 0{,}3 \times 1 + 0{,}4 \times 0{,}9 \approx 0{,}07357 + 0{,}3 + 0{,}36 = 0{,}73357
$$

**Décision de l'agent.** La règle de fraîcheur l'emporte : à 365 jours, la récence (0,24523) est sous 0,3, et l'agent repose les questions d'adéquation avant toute recommandation, bien que le score (0,73357) dépasse le seuil d'injection.

**Contre-calcul.** Avec le seul seuil de score à 0,6, le profil ne serait jamais remis en cause : son plancher vaut β × 1 + γ × 0,9 = 0,3 + 0,36 = 0,66 > 0,6 (démonstration 3), donc il reste injecté à tout âge, même après dix ans. Un fonds risqué pourrait être recommandé sur une déclaration périmée, ce qui exposerait la banque à une plainte et à une remarque de conformité. Une somme pondérée laisse l'importance compenser l'âge : pour une donnée réglementée, il faut une règle dure à part.

**Sensibilité.** Avec une demi-vie de 90 jours au lieu de 180, la récence à un an tomberait à 2^(−365/90) ≈ 0,06014, et la bascule sous 0,3 arriverait vers le 157e jour (90 × log₂(1/0,3) ≈ 156,33). La valeur de bascule de la règle actuelle est le 313e jour.

**En production.** On suit la part des recommandations émises avec un profil de moins de douze mois, avec un objectif de 100 %, et le nombre de profils relus chaque mois. Les exigences d'adéquation des produits d'investissement sont à confirmer avec le texte en vigueur de la CBUAE.

### Cas 3 — [CRYPTO] Une plateforme agréée VARA : la file d'astreinte des alertes de liquidité

**Contexte.** Une plateforme d'actifs virtuels agréée par la VARA fait mémoriser chaque alerte de liquidité par un agent de surveillance, qui présente à l'astreinte une file triée par score. Ici, la récence compte davantage que dans les autres cas, parce qu'un incident en cours prime sur l'historique : les poids sont α = 0,5, β = 0,3, γ = 0,2. Une alerte n'entre dans la file « à traiter maintenant » que si son score atteint 0,6. Les valeurs sont illustratives.

**Données.**

- facteur d'oubli : δ = 0,98 par heure ; poids : 0,5 ; 0,3 ; 0,2 ; seuil de la file : 0,6 ;
- a₁ : il y a 1 h, gravité (importance) 0,5, pertinence 0,4 ;
- a₂ : il y a 72 h, gravité 1, pertinence 0,9 (même pool que l'incident en cours, déjà résolu) ;
- a₃ : il y a 10 h, gravité 0,7, pertinence 0,2.

**Calcul pas à pas.**

**Étape 1.** La demi-vie : ln 2/(−ln 0,98) ≈ 34,31 heures.

**Étape 2.** Les récences : 0,98 ; 0,98⁷² ≈ 0,23349 ; 0,98¹⁰ ≈ 0,81707.

**Étape 3.** Les scores :

$$
a_1 : 0{,}49 + 0{,}15 + 0{,}08 = 0{,}72, \qquad a_2 : 0{,}11675 + 0{,}3 + 0{,}18 \approx 0{,}59675, \qquad a_3 : 0{,}40854 + 0{,}21 + 0{,}04 \approx 0{,}65854
$$

**Étape 4.** Le classement : a₁, a₃, a₂. Les alertes au-dessus de 0,6 sont a₁ et a₃.

**Décision de l'agent.** L'astreinte voit a₁ puis a₃ ; a₂, résolue il y a trois jours, passe dans l'historique, consultable mais hors de la file.

**Contre-calcul.** Sans décroissance (récence 1 pour toutes), les scores deviennent 0,73, 0,98 et 0,75 : a₂ passe en tête, et la file se remplit d'événements résolus. Les opérateurs finissent par ignorer les notifications, exactement le risque que la surveillance devait réduire.

**Sensibilité.** a₂ reste dans la file tant que 0,5 × 0,98^Δt + 0,48 ≥ 0,6, soit 0,98^Δt ≥ 0,24, c'est-à-dire Δt ≤ ln 0,24/ln 0,98 ≈ 70,64 heures : à 72 heures, elle vient de sortir de la file. La valeur de bascule, 70,6 heures, est proche de l'âge réel : une petite erreur d'horodatage suffirait à la remettre dans la file, d'où l'intérêt d'une horloge unique (démonstration 5).

**En production.** On suit le délai moyen de prise en charge d'une alerte critique et le nombre d'alertes résolues encore présentes dans la file. Les délais de traitement attendus d'une plateforme agréée sont à confirmer avec le règlement VARA en vigueur.

### Cas 4 — [RH] Un cabinet RH multi-émirats : une importance notée sur 10 qui fausse le classement

**Contexte.** Un cabinet RH présent dans plusieurs émirats fait suivre par un agent le dossier de chaque nouvel employé. Le modèle note l'importance de chaque souvenir de 1 à 10 au moment où il l'écrit. Pour la question « comment joindre le candidat pour fixer sa visite médicale ? », trois souvenirs sont candidats et l'agent en injecte k = 2. Les valeurs sont illustratives.

**Données.**

- temps en jours ; δ = 0,95 par jour ; poids : 0,3 ; 0,3 ; 0,4 ;
- s₁ : « statut de la visite médicale », vu il y a 12 jours, importance 9/10, pertinence 0,5 ;
- s₂ : « préfère être contacté par message », vu il y a 1 jour, importance 3/10, pertinence 0,95 ;
- s₃ : « contrat enregistré auprès du MOHRE », vu il y a 20 jours, importance 8/10, pertinence 0,3.

**Calcul pas à pas.**

**Étape 1.** La demi-vie et les récences : ln 2/(−ln 0,95) ≈ 13,51 jours ; 0,95¹² ≈ 0,54036 ; 0,95 ; 0,95²⁰ ≈ 0,35849.

**Étape 2.** Les scores avec l'importance ramenée sur [0 ; 1] (9/10 = 0,9, etc.) :

$$
s_1 \approx 0{,}16211 + 0{,}27 + 0{,}2 = 0{,}63211, \qquad s_2 = 0{,}285 + 0{,}09 + 0{,}38 = 0{,}755, \qquad s_3 \approx 0{,}10755 + 0{,}24 + 0{,}12 = 0{,}46755
$$

**Étape 3.** Les scores avec l'importance brute sur 10, sans normalisation :

$$
s_1 \approx 3{,}06211, \qquad s_2 = 1{,}565, \qquad s_3 \approx 2{,}62755
$$

**Étape 4.** Les deux top-2 : normalisé, s₂ puis s₁ ; brut, s₁ puis s₃.

**Décision de l'agent.** Avec la normalisation, l'agent injecte la préférence de contact et le statut de la visite, et répond correctement. Le cabinet ajoute une garde : une importance hors de [0 ; 1] lève une erreur.

**Contre-calcul.** Sans normalisation, la préférence de contact, le souvenir le plus pertinent (0,95), tombe en dernière position et n'est pas injectée : l'agent appelle le candidat au lieu de lui écrire, et le rendez-vous médical prend du retard, ce qui retarde le permis de travail. C'est la démonstration 4 : l'écart d'importance pondéré (0,3 × 6 = 1,8) dépasse α + γ = 0,7.

**Sensibilité.** Si l'importance est notée sur [0 ; c], s₂ passe devant s₁ tant que (0,285 − 0,16211) + (0,38 − 0,2) − 0,3 × 0,6 × c > 0, soit c < 0,30289/0,18 ≈ 1,68273. La valeur de bascule de l'échelle est donc 1,68 : toute échelle plus large que [0 ; 1,68] renverse ce classement, et [0 ; 10] le renverse largement.

**En production.** On suit la part des souvenirs dont l'importance est hors de [0 ; 1] (objectif zéro) et, pour les statuts administratifs, l'âge du dernier contrôle par l'outil officiel, avec une règle dure : au-delà de 30 jours, l'agent revérifie avant de répondre. Les démarches MOHRE et les durées de conservation des données des salariés sont à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Avec α = β = γ = 1/3, calculer le score d'un souvenir de récence 0,6, importance 0,9 et pertinence 0,3.

**Exercice 2.** Calculer la demi-vie pour δ = 0,99 par heure. (ln 2 ≈ 0,6931, ln(1/0,99) ≈ 0,01005.)

**Exercice 3.** Quel δ donne une demi-vie de 24 heures ?

**Exercice 4.** Démontrer que la récence est divisée par 4 après deux demi-vies.

**Exercice 5.** Avec les poids de l'exemple, un souvenir a importance 1 et pertinence 1. Quel score minimal a-t-il, quel que soit son âge ?

**Exercice 6 (cas modifié).** Dans le cas 1, le souvenir m₃ (refus du rez-de-chaussée) vient d'être relu il y a 10 heures. Recalculer son score et le nouveau classement.

**Exercice 7 (trouver l'erreur).** Un collègue configure δ = 0,995 en croyant régler une demi-vie d'environ six jours, mais son horloge compte en jours. Quelle demi-vie obtient-il réellement, et quel δ aurait-il dû mettre ?

**Exercice 8 (redémontrer de mémoire).** Redémontrer la formule de la demi-vie, puis la condition sous laquelle un vieux souvenir bat un souvenir récent à tout âge.

## Corrigé

**Exercice 1.** Avec des poids égaux, le score est la moyenne simple : (0,6 + 0,9 + 0,3)/3 = 1,8/3 = 0,6.

**Exercice 2.** t½ = ln 2/ln(1/0,99) = 0,6931/0,01005 ≈ 69 heures, un peu moins de trois jours.

**Exercice 3.** On veut δ²⁴ = 1/2. On élève à la puissance 1/24 : δ = (1/2)^(1/24) = 2^(−1/24) ≈ 0,97153 par heure.

**Exercice 4.** δ^(2t½) = (δ^t½)² = (1/2)² = 1/4, parce que les exposants se multiplient.

**Exercice 5.** Le score vaut 0,3 × δ^Δt + 0,3 × 1 + 0,4 × 1 = 0,7 + 0,3 δ^Δt. Comme δ^Δt > 0 et tend vers 0, le score reste strictement au-dessus de 0,7 et s'en approche : 0,7 est la borne inférieure, jamais atteinte (le plancher de la démonstration 3).

**Exercice 6.** La récence de m₃ vaut 0,995¹⁰ ≈ 0,95111, d'où un score de 0,3 × 0,95111 + 0,3 + 0,38 ≈ 0,28533 + 0,68 = 0,96533. Le classement devient m₃ (0,96533), m₂ (0,79911), m₁ (0,62701) : relire un souvenir remet son horloge à zéro et le ramène en tête.

**Exercice 7.** Avec Δt en jours, δ = 0,995 par jour donne t½ = 0,69315/0,0050125 ≈ 138,3 jours, plus de quatre mois au lieu de six jours (démonstration 5). Il fallait δⱼ = 0,995²⁴ ≈ 0,88665 par jour, qui redonne 5,76 jours.

**Exercice 8.** Demi-vie : δ^t½ = 1/2, donc t½ ln δ = −ln 2, donc t½ = ln 2/ln(1/δ). Condition : score(A) = α δ^Δt + β i(A) + γ p(A) > β i(A) + γ p(A), parce que α δ^Δt > 0 ; si β i(A) + γ p(A) dépasse le score de B, A gagne quel que soit Δt.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`score(recence, importance, pertinence, poids, verifier)`** — Cette fonction est le jury qui note chaque souvenir sur trois critères avant de décider lequel entre dans le prompt : elle reçoit la récence, l'importance et la pertinence d'un souvenir, un triplet de poids α, β et γ, qui vaut par défaut 0,3, 0,3 et 0,4, et un drapeau `verifier`. Quand ce drapeau est levé, elle refuse par une `ValueError` des poids négatifs ou dont la somme s'écarte de 1, puis des composantes sorties de l'intervalle de 0 à 1 ; elle renvoie ensuite la moyenne pondérée α × récence + β × importance + γ × pertinence, soit 0,465 pour le souvenir A de l'exemple et 0,73 pour le souvenir B.

**`recence(heures, delta)`** — On la voit en sablier qui se vide à rythme constant : elle reçoit l'âge d'un souvenir, en heures ou dans l'unité choisie, et le facteur d'oubli δ, 0,995 par défaut, vérifie que δ est strictement compris entre 0 et 1 et que l'âge n'est pas négatif, faute de quoi elle lève une `ValueError`. Elle renvoie δ élevé à la puissance de l'âge, soit 0,99003 à deux heures, 0,69705 à 72 heures et 0,08157 à 500 heures, et c'est elle qui fournit au jury de `score` sa première composante, avec une demi-vie de 138,3 heures pour le réglage par défaut.

**`normaliser(valeurs)`** — Cette fonction est le géomètre qui ramène des mesures prises avec des règles différentes sur une même échelle de 0 à 1 : elle reçoit une liste de valeurs, repère la plus petite et la plus grande, et renvoie une liste de zéros quand elles sont toutes égales, puisqu'une composante identique pour tous ne départage personne. Sinon, elle renvoie pour chaque valeur son écart au minimum divisé par l'étendue, la normalisation min-max de l'étape 17, si bien que 2, 5 et 8 deviennent 0, 0,5 et 1 dans la démonstration 4, qui montre qu'une importance notée sur dix écraserait les deux autres critères.

**`age_bascule(score_b, importance, pertinence, delta, poids)`** — Celle-ci joue l'oracle qui prédit à quel âge un souvenir A, de grande valeur mais vieillissant, finira par céder sa place à un rival B de score donné : elle reçoit ce score, l'importance et la pertinence de A, le facteur δ et les poids, calcule le plancher β i + γ p que A garde à tout âge, puis le seuil que doit dépasser δ à la puissance de l'âge. Elle renvoie `None` si ce seuil est négatif ou nul, car A bat alors B à tout âge, 0 s'il atteint 1, car A ne le bat jamais, et sinon l'âge ln(seuil)/ln(δ) ; dans la démonstration 3, le refus m₃ ne passe jamais derrière m₁, d'où `None`.

**`cas_1_immo_client()`** — Cette fonction raconte l'agent d'une agence immobilière qui doit choisir deux souvenirs sur trois pour proposer des biens à un acheteur : une question d'horaire vieille de 2 heures, un budget relevé il y a 72 heures et un refus du rez-de-chaussée vieux de 500 heures. Elle ne reçoit rien, calcule les scores 0,62701, 0,79911 et 0,70447, injecte donc le budget et le refus, là où une fenêtre des deux souvenirs les plus récents aurait perdu le refus, puis chiffre l'avance de récence du budget, 0,18464, et l'horizon de 143,4 heures au-delà duquel, faute de relecture, le refus passe devant le budget ; elle imprime ces résultats et les renvoie dans un dictionnaire.

**`cas_2_banque_profil()`** — On y suit l'assistant d'investissement d'une banque de détail qui garde en mémoire le profil « prudent » déclaré par un client un an plus tôt : la fonction ne reçoit rien, tire d'une demi-vie de 180 jours un facteur δ de 0,99616 par jour, puis une récence de 0,24523 au bout de 365 jours, passée sous la règle de 0,3 depuis le 313ᵉ jour. Elle montre surtout que le score du profil, 0,73357, reste au-dessus du seuil d'injection de 0,6, parce que son plancher vaut déjà 0,66 : le score seul ne retirerait jamais ce profil, d'où la décision de reposer les questions ; elle calcule aussi la variante à 90 jours de demi-vie et renvoie le tout.

**`cas_3_crypto_alertes()`** — Ici, l'agent de surveillance d'une plateforme d'actifs virtuels trie les alertes de liquidité pour l'équipe d'astreinte, avec des poids 0,5, 0,3 et 0,2 qui donnent la priorité au présent et un facteur de 0,98 par heure : la fonction ne reçoit rien, calcule une demi-vie de 34,31 heures et les scores des trois alertes, 0,72, 0,59675 et 0,65854. Seules a₁ et a₃ atteignent le seuil de 0,6 et entrent dans la file, alors que, sans décroissance, l'alerte a₂ de 72 heures serait la première avec 0,98 ; la fonction calcule enfin qu'a₂ est sortie de la file au bout de 70,64 heures, imprime ces résultats et les renvoie.

**`cas_4_rh_echelles()`** — Cette fonction met en scène un cabinet de ressources humaines dont le modèle note l'importance des souvenirs de 1 à 10 au lieu de 0 à 1 : elle ne reçoit rien, prend trois souvenirs d'un nouvel employé avec un facteur de 0,95 par jour, une demi-vie de 13,51 jours, et les classe deux fois. Avec l'importance ramenée sur 1, les scores 0,63211, 0,755 et 0,46755 placent s₂ et s₁ en tête ; avec l'importance brute, sans vérification, les scores 3,06211, 1,565 et 2,62755 placent s₁ et s₃, et le souvenir le plus pertinent pour la question, s₂, passe à la trappe. Elle calcule enfin l'échelle de bascule, 1,68273, au-delà de laquelle le classement se renverse, et renvoie ces résultats.

**`main()`** — C'est le chef d'orchestre de la fiche : il vérifie d'abord l'exemple simple, 0,465 contre 0,73, puis la démonstration 1 sur une grille de vingt-sept triplets où le score reste entre la plus petite et la plus grande composante, et s'assure que des poids de somme 1,5 ou une importance de 9 sont refusés. Il enchaîne avec la demi-vie de 138,3 heures, le plancher qui protège m₃, l'effet d'une échelle mal choisie, la conversion d'un facteur horaire en facteur journalier de 0,88665, puis les quatre cas et le corrigé ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tout concorde.

```python
"""Démonstration 27 — score de mémoire : moyenne pondérée, demi-vie, vieux souvenir important, échelles, unités, quatre cas."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

POIDS = (0.3, 0.3, 0.4)


def score(recence: float, importance: float, pertinence: float, poids: tuple[float, float, float] = POIDS,
          verifier: bool = True) -> float:
    """α × récence + β × importance + γ × pertinence ; composantes dans [0, 1] et poids de somme 1."""
    a, b, g = poids
    if verifier:
        if min(poids) < 0 or abs(a + b + g - 1) > 1e-9:
            raise ValueError("poids positifs de somme 1")
        if not all(0 <= x <= 1 for x in (recence, importance, pertinence)):
            raise ValueError("composantes dans [0, 1]")
    return a * recence + b * importance + g * pertinence


def recence(heures: float, delta: float = 0.995) -> float:
    """δ^Δt, avec 0 < δ < 1 et Δt >= 0."""
    if not 0 < delta < 1 or heures < 0:
        raise ValueError("il faut 0 < delta < 1 et un âge >= 0")
    return delta ** heures


def normaliser(valeurs: list[float]) -> list[float]:
    """Min-max de l'étape 17 ; toutes égales → tous à 0 (la composante ne départage personne)."""
    bas, haut = min(valeurs), max(valeurs)
    if haut == bas:
        return [0.0 for _ in valeurs]
    return [(v - bas) / (haut - bas) for v in valeurs]


def age_bascule(score_b: float, importance: float, pertinence: float, delta: float,
                poids: tuple[float, float, float] = POIDS) -> float | None:
    """Âge au-delà duquel A (importance, pertinence) passe derrière un souvenir de score score_b ; None si jamais."""
    a, b, g = poids
    plancher = b * importance + g * pertinence
    seuil = (score_b - plancher) / a
    if seuil <= 0:
        return None                       # A bat B à tout âge
    if seuil >= 1:
        return 0.0                        # A ne bat jamais B
    return math.log(seuil) / math.log(delta)


def cas_1_immo_client() -> dict:
    """[IMMO] m1 (2 h ; 0,3 ; 0,6), m2 (72 h ; 0,9 ; 0,8), m3 (500 h ; 1 ; 0,95) ; k = 2."""
    souvenirs = {"m1": (2, 0.3, 0.6), "m2": (72, 0.9, 0.8), "m3": (500, 1.0, 0.95)}
    s = {k: score(recence(h), i, p) for k, (h, i, p) in souvenirs.items()}
    classement = sorted(s, key=s.get, reverse=True)
    recents = sorted(souvenirs, key=lambda k: souvenirs[k][0])[:2]
    ecart = 0.3 * (recence(72) - recence(500))
    seuil_tau = 0.09 / ecart
    tau = math.log(seuil_tau) / math.log(0.995)
    print("Cas 1 [IMMO] récences " + " ; ".join(f"{k} {recence(h):.5f}" for k, (h, _, _) in souvenirs.items())
          + " ; scores " + " ; ".join(f"{k} {v:.5f}" for k, v in s.items()))
    print(f"  injectés {classement[:2]} ; fenêtre des récents {recents} ; m3 dépasse m2 après {tau:.1f} h"
          f" (δ^τ > {seuil_tau:.4f})")
    return {"s": s, "classement": classement, "recents": recents, "ecart": ecart, "seuil_tau": seuil_tau, "tau": tau}


def cas_2_banque_profil() -> dict:
    """[BANQUE] demi-vie 180 jours ; profil importance 1, pertinence 0,9 ; règle récence >= 0,3 ; seuil de score 0,6."""
    delta = 2 ** (-1 / 180)
    r365 = recence(365, delta)
    jour = 180 * math.log2(1 / 0.3)
    s365 = score(r365, 1.0, 0.9)
    plancher = 0.3 * 1.0 + 0.4 * 0.9
    r90, jour90 = 2 ** (-365 / 90), 90 * math.log2(1 / 0.3)
    decision = "reposer les questions" if r365 < 0.3 else "utiliser le profil"
    print(f"Cas 2 [BANQUE] δ = {delta:.5f} ; récence à 365 j {r365:.5f} ; bascule jour {jour:.2f} ; score {s365:.5f} ;"
          f" plancher {plancher:.2f} ; décision : {decision}")
    print(f"  demi-vie 90 j : récence {r90:.5f}, bascule jour {jour90:.2f}")
    return {"delta": delta, "r365": r365, "jour": jour, "s365": s365, "plancher": plancher, "r90": r90,
            "jour90": jour90, "decision": decision}


def cas_3_crypto_alertes() -> dict:
    """[CRYPTO] δ = 0,98 par heure ; poids (0,5 ; 0,3 ; 0,2) ; seuil 0,6."""
    poids = (0.5, 0.3, 0.2)
    alertes = {"a1": (1, 0.5, 0.4), "a2": (72, 1.0, 0.9), "a3": (10, 0.7, 0.2)}
    t12 = math.log(2) / -math.log(0.98)
    sc = {k: score(recence(h, 0.98), i, p, poids) for k, (h, i, p) in alertes.items()}
    sans = {k: score(1.0, i, p, poids) for k, (_, i, p) in alertes.items()}
    file = [k for k in sorted(sc, key=sc.get, reverse=True) if sc[k] >= 0.6]
    bascule = math.log(0.24) / math.log(0.98)
    print(f"Cas 3 [CRYPTO] demi-vie {t12:.2f} h ; scores " + " ; ".join(f"{k} {v:.5f}" for k, v in sc.items())
          + f" ; file {file}")
    print("  sans décroissance " + " ; ".join(f"{k} {v:.2f}" for k, v in sans.items()) + f" ; a2 sort de la file après {bascule:.2f} h")
    return {"t12": t12, "sc": sc, "sans": sans, "file": file, "bascule": bascule}


def cas_4_rh_echelles() -> dict:
    """[RH] δ = 0,95 par jour ; s1 (12 j ; 9/10 ; 0,5), s2 (1 j ; 3/10 ; 0,95), s3 (20 j ; 8/10 ; 0,3) ; k = 2."""
    souvenirs = {"s1": (12, 9, 0.5), "s2": (1, 3, 0.95), "s3": (20, 8, 0.3)}
    t12 = math.log(2) / -math.log(0.95)
    norm = {k: score(recence(j, 0.95), imp / 10, p) for k, (j, imp, p) in souvenirs.items()}
    brut = {k: score(recence(j, 0.95), imp, p, verifier=False) for k, (j, imp, p) in souvenirs.items()}
    top_norm = sorted(norm, key=norm.get, reverse=True)[:2]
    top_brut = sorted(brut, key=brut.get, reverse=True)[:2]
    avance = (0.3 * recence(1, 0.95) - 0.3 * recence(12, 0.95)) + (0.4 * 0.95 - 0.4 * 0.5)
    c_bascule = avance / (0.3 * 0.6)
    print(f"Cas 4 [RH] demi-vie {t12:.2f} j ; normalisé " + " ; ".join(f"{k} {v:.5f}" for k, v in norm.items())
          + f" → {top_norm}")
    print("  brut " + " ; ".join(f"{k} {v:.5f}" for k, v in brut.items()) + f" → {top_brut} ; échelle de bascule {c_bascule:.5f}")
    return {"t12": t12, "norm": norm, "brut": brut, "top_norm": top_norm, "top_brut": top_brut,
            "avance": avance, "c_bascule": c_bascule}


def main() -> None:
    # Exemple simple et mécanisme
    print(f"Exemple : A {score(0.95, 0.2, 0.3):.3f} ; B {score(0.4, 0.9, 0.85):.2f} ; plancher de B {0.3 * 0.9 + 0.4 * 0.85:.2f} ;"
          f" fiche : A {score(0.9, 0.3, 0.5):.2f}, B {score(0.2, 0.9, 0.85):.2f}")
    assert round(score(0.95, 0.2, 0.3), 3) == 0.465 and round(score(0.4, 0.9, 0.85), 2) == 0.73
    assert (round(0.3 * 0.95, 3), round(0.3 * 0.2, 2), round(0.4 * 0.3, 2)) == (0.285, 0.06, 0.12)
    assert (round(0.3 * 0.4, 2), round(0.3 * 0.9, 2), round(0.4 * 0.85, 2)) == (0.12, 0.27, 0.34)
    assert round(0.3 * 0.9 + 0.4 * 0.85, 2) == 0.61 and round(score(0.9, 0.3, 0.5), 2) == 0.56 and round(score(0.2, 0.9, 0.85), 2) == 0.67
    assert round(0.3 * recence(2), 5) == 0.29701 and round(0.3 * recence(500), 5) == 0.02447
    assert round(0.3 * 1.0 + 0.4 * 0.95, 2) == 0.68 and round(0.3 * 0.3 + 0.4 * 0.6, 2) == 0.33

    # Démonstration 1
    for r in (0, 0.5, 1):
        for i in (0, 0.5, 1):
            for p in (0, 0.5, 1):
                v = score(r, i, p)
                assert 0 <= v <= 1 and min(r, i, p) - 1e-12 <= v <= max(r, i, p) + 1e-12
    assert score(1, 1, 1, (0.5, 0.5, 0.5), verifier=False) == 1.5
    for mauvais in (lambda: score(1, 1, 1, (0.5, 0.5, 0.5)), lambda: score(0.5, 9, 0.5)):
        try:
            mauvais()
        except ValueError:
            pass
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")

    # Démonstration 2
    demi_vie = math.log(2) / math.log(1 / 0.995)
    lam = -math.log(0.995)
    print(f"Démonstration 2 : λ = {lam:.7f} ; demi-vie pour δ = 0,995 : {demi_vie:.1f} h ({demi_vie / 24:.1f} jours) ;"
          f" coût d'une heure : {0.3 * lam:.4f} à neuf, {0.3 * lam * recence(500):.5f} à 500 h")
    assert round(demi_vie, 1) == 138.3 and math.isclose(recence(demi_vie), 0.5) and round(lam, 7) == 0.0050125
    assert round(math.log(2), 5) == 0.69315 and round(demi_vie / 24, 1) == 5.8 and math.isclose(recence(2 * demi_vie), 0.25)
    assert round(0.3 * lam, 4) == 0.0015 and round(0.3 * lam * recence(500), 5) == 0.00012

    # Démonstration 3
    plancher_m3 = 0.3 * 1.0 + 0.4 * 0.95
    s_m1 = score(recence(2), 0.3, 0.6)
    print(f"Démonstration 3 : plancher de m3 {plancher_m3:.2f} > score de m1 {s_m1:.5f} ;"
          f" ancienne forme {0.3 * 0.7 + 0.4 * 0.35:.2f} > {0.3 * recence(2):.3f} ; m3 contre m1 : {age_bascule(s_m1, 1.0, 0.95, 0.995)}")
    assert plancher_m3 > s_m1 and age_bascule(s_m1, 1.0, 0.95, 0.995) is None
    assert round(0.3 * 0.7, 2) == 0.21 and round(0.4 * 0.35, 2) == 0.14 and round(0.3 * 0.7 + 0.4 * 0.35, 2) == 0.35
    assert round(0.3 * recence(2), 3) == 0.297 and round(0.3 * 0.9 + 0.4 * 0.8, 2) == 0.59
    for heures in (500, 5_000, 50_000):
        assert score(recence(heures), 1.0, 0.95) > s_m1
    assert age_bascule(0.9, 0.0, 0.0, 0.995) == 0.0
    a = age_bascule(0.70447, 0.9, 0.8, 0.995)
    assert abs(score(recence(a), 0.9, 0.8) - 0.70447) < 1e-9

    # Démonstration 4
    print(f"Démonstration 4 : écart pondéré {0.3 * 0.6:.2f} → {0.3 * 6:.1f} > α + γ = {0.3 + 0.4} ;"
          f" min-max (2 ; 5 ; 8) → {normaliser([2, 5, 8])} ; (4 ; 4 ; 4) → {normaliser([4, 4, 4])}")
    assert round(0.3 * 0.6, 2) == 0.18 and round(0.3 * 6, 1) == 1.8 and 0.3 + 0.4 == 0.7
    assert normaliser([2, 5, 8]) == [0.0, 0.5, 1.0] and normaliser([4, 4, 4]) == [0.0, 0.0, 0.0]

    # Démonstration 5
    dj = 0.995 ** 24
    t_jours = math.log(2) / -math.log(dj)
    print(f"Démonstration 5 : δ_jour = {dj:.5f} ; demi-vie {t_jours:.2f} jours = {24 * t_jours:.1f} h ;"
          f" 0,995 par jour → {demi_vie:.1f} jours")
    assert round(dj, 5) == 0.88665 and round(t_jours, 2) == 5.76 and abs(24 * t_jours - demi_vie) < 1e-9
    for h in (1, 24, 100, 500):
        assert math.isclose(recence(h), dj ** (h / 24))

    # Cas
    c1 = cas_1_immo_client()
    s = c1["s"]
    assert [round(v, 5) for v in s.values()] == [0.62701, 0.79911, 0.70447]
    assert [round(recence(h), 5) for h in (2, 72, 500)] == [0.99003, 0.69705, 0.08157]
    assert round(0.3 * recence(72), 5) == 0.20911 and c1["classement"] == ["m2", "m3", "m1"]
    assert sorted(s, key=s.get, reverse=True)[:2] == ["m2", "m3"] and c1["recents"] == ["m1", "m2"]
    assert round(0.3 * (0.69705 - 0.08157), 5) == round(c1["ecart"], 5) == 0.18464 and round(0.27 + 0.32 - 0.68, 2) == -0.09
    assert round(c1["seuil_tau"], 4) == round(0.09 / 0.18464, 4) == 0.4874 and round(c1["tau"], 1) == 143.4
    assert round(math.log(0.4874) / math.log(0.995), 1) == 143.4 and round(c1["tau"] / 24) == 6

    c2 = cas_2_banque_profil()
    assert round(c2["delta"], 5) == 0.99616 and round(c2["r365"], 5) == 0.24523 and round(c2["jour"], 2) == 312.65
    assert math.ceil(c2["jour"]) == 313 and round(c2["s365"], 5) == 0.73357 and round(0.3 * c2["r365"], 5) == 0.07357
    assert round(c2["plancher"], 2) == 0.66 and c2["plancher"] > 0.6 and c2["decision"] == "reposer les questions"
    assert round(c2["r90"], 5) == 0.06014 and round(c2["jour90"], 2) == 156.33 and math.ceil(c2["jour90"]) == 157
    assert score(recence(3_650, c2["delta"]), 1.0, 0.9) > 0.6

    c3 = cas_3_crypto_alertes()
    sc = c3["sc"]
    assert round(c3["t12"], 2) == 34.31 and round(recence(72, 0.98), 5) == 0.23349 and round(recence(10, 0.98), 5) == 0.81707
    assert round(sc["a1"], 5) == 0.72 and round(sc["a2"], 5) == 0.59675 and round(sc["a3"], 5) == 0.65854
    assert round(0.5 * 0.98, 2) == 0.49 and round(0.5 * recence(72, 0.98), 5) == 0.11675 and round(0.5 * recence(10, 0.98), 5) == 0.40854
    assert c3["file"] == ["a1", "a3"] and [round(v, 2) for v in c3["sans"].values()] == [0.73, 0.98, 0.75]
    assert round(c3["bascule"], 2) == 70.64 and round(0.3 * 1.0 + 0.2 * 0.9, 2) == 0.48

    c4 = cas_4_rh_echelles()
    n, b = c4["norm"], c4["brut"]
    assert round(c4["t12"], 2) == 13.51 and round(recence(12, 0.95), 5) == 0.54036 and round(recence(20, 0.95), 5) == 0.35849
    assert [round(n[k], 5) for k in ("s1", "s2", "s3")] == [0.63211, 0.755, 0.46755]
    assert [round(b[k], 5) for k in ("s1", "s2", "s3")] == [3.06211, 1.565, 2.62755]
    assert round(0.3 * recence(12, 0.95), 5) == 0.16211 and round(0.3 * recence(20, 0.95), 5) == 0.10755
    assert c4["top_norm"] == ["s2", "s1"] and c4["top_brut"] == ["s1", "s3"]
    assert round(c4["avance"], 5) == 0.30289 and round(c4["c_bascule"], 5) == 1.68273

    # Corrigé
    print("Corrigé")
    d24 = 2 ** (-1 / 24)
    s6 = score(recence(10), 1.0, 0.95)
    print(f"  ex1 {score(0.6, 0.9, 0.3, (1 / 3, 1 / 3, 1 / 3)):.1f} ; ex2 {math.log(2) / math.log(1 / 0.99):.0f} h ;"
          f" ex3 δ = {d24:.5f} ; ex5 {score(0, 1, 1):.1f} ; ex6 m3 {s6:.5f} ; ex7 {demi_vie:.1f} jours, δ = {dj:.5f}")
    assert round(score(0.6, 0.9, 0.3, (1 / 3, 1 / 3, 1 / 3)), 1) == 0.6 and round(math.log(2) / math.log(1 / 0.99)) == 69
    assert round(0.6931 / 0.01005) == 69 and round(math.log(1 / 0.99), 5) == 0.01005
    assert round(d24, 5) == 0.97153 and math.isclose(d24 ** 48, 0.25) and round(score(0, 1, 1), 1) == 0.7
    assert round(recence(10), 5) == 0.95111 and round(0.3 * recence(10), 5) == 0.28533 and round(s6, 5) == 0.96533
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Exemple : A 0.465 ; B 0.73 ; plancher de B 0.61 ; fiche : A 0.56, B 0.67
Démonstration 2 : λ = 0.0050125 ; demi-vie pour δ = 0,995 : 138.3 h (5.8 jours) ; coût d'une heure : 0.0015 à neuf, 0.00012 à 500 h
Démonstration 3 : plancher de m3 0.68 > score de m1 0.62701 ; ancienne forme 0.35 > 0.297 ; m3 contre m1 : None
Démonstration 4 : écart pondéré 0.18 → 1.8 > α + γ = 0.7 ; min-max (2 ; 5 ; 8) → [0.0, 0.5, 1.0] ; (4 ; 4 ; 4) → [0.0, 0.0, 0.0]
Démonstration 5 : δ_jour = 0.88665 ; demi-vie 5.76 jours = 138.3 h ; 0,995 par jour → 138.3 jours
Cas 1 [IMMO] récences m1 0.99003 ; m2 0.69705 ; m3 0.08157 ; scores m1 0.62701 ; m2 0.79911 ; m3 0.70447
  injectés ['m2', 'm3'] ; fenêtre des récents ['m1', 'm2'] ; m3 dépasse m2 après 143.4 h (δ^τ > 0.4874)
Cas 2 [BANQUE] δ = 0.99616 ; récence à 365 j 0.24523 ; bascule jour 312.65 ; score 0.73357 ; plancher 0.66 ; décision : reposer les questions
  demi-vie 90 j : récence 0.06014, bascule jour 156.33
Cas 3 [CRYPTO] demi-vie 34.31 h ; scores a1 0.72000 ; a2 0.59675 ; a3 0.65854 ; file ['a1', 'a3']
  sans décroissance a1 0.73 ; a2 0.98 ; a3 0.75 ; a2 sort de la file après 70.64 h
Cas 4 [RH] demi-vie 13.51 j ; normalisé s1 0.63211 ; s2 0.75500 ; s3 0.46755 → ['s2', 's1']
  brut s1 3.06211 ; s2 1.56500 ; s3 2.62755 → ['s1', 's3'] ; échelle de bascule 1.68273
Corrigé
  ex1 0.6 ; ex2 69 h ; ex3 δ = 0.97153 ; ex5 0.7 ; ex6 m3 0.96533 ; ex7 138.3 jours, δ = 0.88665
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme classe des souvenirs pour une question en combinant récence, importance et pertinence, après avoir vérifié que les trois composantes sont sur la même échelle, puis applique les règles dures qui ne passent pas par le score.

```text
ALGORITHME ClasserSouvenirs
ENTRÉES : souvenirs (âge Δt, importance i, pertinence p), poids α, β, γ, demi-vie t½, nombre k
SORTIE  : les k souvenirs de meilleur score

  SI les poids ne sont pas positifs de somme 1 ALORS ERREUR
  δ ← 2 puissance (−1 / t½)                     (même unité de temps que Δt)
  POUR CHAQUE souvenir m FAIRE
      SI i ou p hors de [0 ; 1] ALORS ERREUR « normaliser d'abord »
      récence ← δ puissance Δt
      score[m] ← α × récence + β × i + γ × p
  FIN POUR
  RETOURNER les k souvenirs de plus grand score

ALGORITHME DemiVie
  RETOURNER ln 2 / ln(1/δ)

ALGORITHME ÂgeDeBascule(A contre un score S_B)
  plancher ← β × i_A + γ × p_A
  SI plancher > S_B ALORS RETOURNER « jamais : A gagne à tout âge »
  RETOURNER ln((S_B − plancher) / α) / ln δ
```

**Complexité.** O(M) pour noter M souvenirs, plus O(M log M) pour les trier (ou O(M log k) avec un tas). La pertinence vient souvent d'un cosinus, en O(d) par souvenir pour des vecteurs de dimension d. La normalisation min-max ajoute deux passes en O(M). L'âge de bascule coûte O(1).

**Du squelette au code.** La récence est la fonction `recence(heures, delta)`, le score la fonction `score(recence, importance, pertinence, poids)`, qui lève `ValueError` quand une composante sort de [0 ; 1] ; le classement est le dictionnaire `s` et le `sorted` de `main`, dans le cas immobilier. La demi-vie est la variable `demi_vie`. La normalisation de l'étape 17 est `normaliser(valeurs)`, et ÂgeDeBascule est `age_bascule`. Les cas sont `cas_1_immo_client`, `cas_2_banque_profil`, `cas_3_crypto_alertes` et `cas_4_rh_echelles`.
