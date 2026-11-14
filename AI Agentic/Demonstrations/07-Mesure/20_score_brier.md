# 20 — Score de Brier : démonstrations

> Fiche : [20 — Score de Brier](<../../Images/07-Mesure/20_score_brier.md>) · Image : `20_score_brier.jpg` · Leçon : [Étape 51 — Spécificité, NPV, AUC](<../../10-Evaluation/51-Specificite-NPV-AUC.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
BS = \frac{1}{N} \sum_{i=1}^{N} (p_i - y_i)^2
$$

Pour chaque prédiction i, pᵢ est la confiance annoncée (« je suis sûr à 80 % ») et yᵢ vaut 1 si l'événement s'est produit, 0 sinon. Le score de Brier est l'erreur quadratique moyenne de ces confiances : 0 est parfait.

## Les symboles, un par un

$$
N
$$

**N** : le nombre de prédictions évaluées, un entier ≥ 1 ; sur une liste vide, le score n'est pas défini et le programme renvoie `None` ; en Python, `len(p)`.

$$
p_i \in [0, 1]
$$

**pᵢ** : la probabilité annoncée pour la prédiction i (confiance d'un agent, score d'un modèle) ; en Python, la liste `p`.

$$
y_i \in \{0, 1\}
$$

**yᵢ** : l'issue réelle, 1 si l'événement s'est produit, 0 sinon ; en Python, la liste `y`.

$$
(p_i - y_i)^2
$$

**(pᵢ − yᵢ)²** : l'erreur au carré de la prédiction i, dans [0 ; 1] ; une confiance de 0,9 qui se réalise coûte 0,01, la même qui échoue coûte 0,81.

$$
BS
$$

**BS** : la moyenne de ces erreurs, dans [0 ; 1] ; plus bas est meilleur ; en Python, `brier(p, y)`.

$$
q,\ BS_0 = q\,(1 - q)
$$

**q** : le taux de base, la fréquence réelle de l'événement dans l'échantillon, dans [0 ; 1] ; **BS₀** : le score de référence, celui de l'agent qui annonce toujours q, la référence à battre ; en Python, `brier([0.6] * 10, y)` pour q = 0,6.

$$
BSS = 1 - \frac{BS}{BS_0}
$$

**BSS** : le score de compétence, sans unité : 1 pour un modèle parfait, 0 pour la référence, négatif pour pire ; en Python, `bss(bs, q)`, qui renvoie `None` si q vaut 0 ou 1.

$$
p_k,\ n_k,\ \bar{o}_k
$$

**pₖ, nₖ, ōₖ** : pour un paquet k de prédictions qui annoncent toutes la même valeur pₖ, leur nombre nₖ et la fréquence observée ōₖ de l'événement dans ce paquet ; en Python, les triplets de `decomposition(paquets)`.

## Le mécanisme, avant les preuves

Des couples (pᵢ, yᵢ) entrent : une confiance entre 0 et 1, et une issue qui vaut 0 ou 1. La différence pᵢ − yᵢ est l'erreur signée : positive quand l'agent a trop cru à l'événement, négative quand il n'y a pas assez cru. Le carré enlève le signe et grossit les grosses erreurs bien plus que les petites : 0,1 devient 0,01, mais 0,8 devient 0,64. La moyenne divise par N pour comparer des échantillons de tailles différentes. Le carré n'est pas un choix esthétique : c'est lui qui rend la règle « propre », c'est-à-dire qui fait de l'annonce honnête la meilleure stratégie (démonstration 2). Avec la valeur absolue |p − y|, l'erreur attendue serait linéaire en p, et l'agent aurait intérêt à exagérer jusqu'à 0 ou 1. Le score ne se lit jamais seul : un événement rare donne un petit BS même à un agent inutile, d'où la référence q (1 − q) et le score de compétence BSS (démonstrations 1 et 3). Enfin le score se décompose en un terme de calibration, que l'on peut corriger, et un terme d'affinement, qui mesure la capacité à séparer les cas (démonstration 4). Ce qui sort est un nombre dans [0 ; 1], que l'on compare à la référence avant de décider quoi que ce soit.

Petit film chiffré avec trois prédictions. Confiance 0,9, issue 1 : erreur 0,9 − 1 = −0,1, carré 0,01. Confiance 0,8, issue 0 : erreur 0,8, carré 0,64. Confiance 0,3, issue 0 : erreur 0,3, carré 0,09. Somme 0,01 + 0,64 + 0,09 = 0,74 ; moyenne 0,74 / 3 ≈ 0,24667. La seule prédiction sûre d'elle et fausse fait 0,64 / 0,74 ≈ 86 % du score.

## Démonstration 1 — Bornes et références

**Ce qu'on démontre.** Pour toutes confiances pᵢ dans [0 ; 1] et issues yᵢ dans {0 ; 1}, BS ∈ [0 ; 1]. Un agent qui annonce toujours 0,5 obtient 0,25. Un agent qui annonce toujours le taux de base q obtient :

$$
BS_0 = q\,(1 - q)^2 + (1 - q)\, q^2 = q\,(1 - q)
$$

**L'idée.** Une confiance et une issue sont toutes deux dans [0 ; 1], donc leur écart aussi. Pour la référence, une part q des issues vaut 1 (erreur 1 − q) et une part 1 − q vaut 0 (erreur q) : on fait la moyenne des deux carrés.

**La preuve, pas à pas.**

**Étape 1.** Comme 0 ≤ pᵢ ≤ 1 et yᵢ ∈ {0 ; 1}, l'écart |pᵢ − yᵢ| est entre 0 et 1, donc son carré aussi ; une moyenne de nombres de [0 ; 1] est dans [0 ; 1].

**Étape 2.** Si p = 0,5 partout, chaque erreur vaut ±0,5, donc chaque carré vaut 0,25, et la moyenne aussi.

**Étape 3.** Si p = q partout, une part q des prédictions a l'issue 1 et coûte (q − 1)², la part 1 − q a l'issue 0 et coûte q² :

$$
BS_0 = q\,(1 - q)^2 + (1 - q)\, q^2
$$

**Étape 4.** On met q (1 − q) en facteur, parce qu'il figure dans les deux termes :

$$
q\,(1 - q)\big[(1 - q) + q\big] = q\,(1 - q)
$$

∎

**Vérification chiffrée.** Quatre issues (1 ; 0 ; 1 ; 0) avec l'annonce 0,5 partout donnent 0,25. Avec q = 0,6 : 0,6 × 0,4² + 0,4 × 0,6² = 0,096 + 0,144 = 0,24 = 0,6 × 0,4. Sur les dix décisions du cas 1 (six justes), l'annonce constante 0,6 donne (6 × 0,16 + 4 × 0,36) / 10 = 2,4 / 10 = 0,24.

**Ce que la preuve révèle du mécanisme.** La référence q (1 − q) est maximale, 0,25, pour q = 0,5, et devient minuscule pour un événement rare : 0,0475 pour q = 0,05. Un même BS peut donc être excellent pour un événement fréquent et médiocre pour un événement rare.

**Conséquence pour un agent.** On n'affiche jamais un BS sans sa référence q (1 − q) calculée sur le même échantillon : un tableau de bord montre BS, BS₀ et BSS côte à côte (cas 3, exercice 7).

## Démonstration 2 — Annoncer la vraie probabilité est la meilleure stratégie

**Ce qu'on démontre.** Si l'événement se produit réellement avec la probabilité q et que l'agent annonce p, son erreur attendue vaut :

$$
\mathbb{E}\big[(p - Y)^2\big] = q\,(p - 1)^2 + (1 - q)\, p^2 = (p - q)^2 + q\,(1 - q)
$$

Elle est minimale, et vaut q (1 − q), exactement pour p = q : le score de Brier est une règle de score « propre ».

**L'idée.** L'erreur attendue se coupe en deux morceaux : un écart au carré entre l'annonce et la vérité, que l'agent contrôle, et un bruit q (1 − q) que personne ne contrôle. Le premier morceau est nul seulement si l'on annonce la vérité.

**La preuve, pas à pas.**

**Étape 1.** Y vaut 1 avec la probabilité q et 0 avec la probabilité 1 − q, donc l'espérance est la moyenne pondérée des deux erreurs :

$$
\mathbb{E}\big[(p - Y)^2\big] = q\,(p - 1)^2 + (1 - q)\, p^2
$$

**Étape 2.** On développe : q (p² − 2p + 1) + p² − q p² = q p² − 2qp + q + p² − q p² = p² − 2qp + q.

**Étape 3.** On fait apparaître un carré en ajoutant et retranchant q², parce que p² − 2qp + q² = (p − q)² :

$$
p^2 - 2qp + q = (p - q)^2 + q - q^2 = (p - q)^2 + q\,(1 - q)
$$

**Étape 4.** Le second terme ne dépend pas de p ; le premier est ≥ 0 et nul seulement en p = q. Le minimum est donc atteint en p = q, et seulement là. ∎

**Vérification chiffrée.** Avec q = 0,7 : annoncer 0,7 coûte 0,7 × 0,3 = 0,21 ; annoncer 0,9 coûte 0,2² + 0,21 = 0,25 : exagérer de 0,2 coûte 0,04. Le programme vérifie, pour q = 0,1, 0,3 et 0,7, que le meilleur p de la grille de 101 valeurs est q. Contre-exemple avec une règle qui n'est pas propre : l'écart absolu attendu vaut q (1 − p) + (1 − q) p, linéaire en p ; à q = 0,7, il vaut 0,7 × 0,3 + 0,3 × 0,7 = 0,42 pour l'annonce honnête 0,7 et seulement 0,3 pour l'annonce exagérée 1. Cette règle récompense la triche.

**Ce que la preuve révèle du mécanisme.** C'est le carré qui crée le terme (p − q)² et donc l'incitation à l'honnêteté. Le bruit q (1 − q) est un plancher : même l'agent parfaitement calibré ne descend pas sous ce plancher s'il ne sait pas mieux distinguer les cas.

**Conséquence pour un agent.** Un agent qui exagère sa confiance pour paraître sûr est pénalisé, en moyenne, par le Brier. On peut donc utiliser ce score pour évaluer, comparer ou récompenser des agents sans les pousser à mentir sur leur confiance ; une métrique en valeur absolue, elle, les y pousserait.

## Démonstration 3 — Le score de compétence

**Ce qu'on démontre.** Avec BS₀ = q (1 − q) > 0, le score de compétence

$$
BSS = 1 - \frac{BS}{BS_0}
$$

vaut 1 pour un modèle parfait, 0 pour l'annonce constante du taux de base, et devient négatif dès qu'un modèle fait pire que cette annonce.

**L'idée.** On mesure le chemin parcouru entre la référence (BS = BS₀) et la perfection (BS = 0), en proportion de la distance totale.

**La preuve, pas à pas.**

**Étape 1.** Modèle parfait : BS = 0, donc BSS = 1 − 0 = 1.

**Étape 2.** Annonce constante q : BS = BS₀ par la démonstration 1, donc BSS = 1 − 1 = 0.

**Étape 3.** BSS est une fonction affine décroissante de BS, de pente −1 / BS₀ < 0, parce que BS₀ > 0 ; donc BS > BS₀ ⟺ BSS < 0. ∎

**Vérification chiffrée.** Avec q = 0,6 (BS₀ = 0,24) : BS = 0 donne 1 ; BS = 0,24 donne 0 ; BS = 0,3 donne 1 − 0,3 / 0,24 = −0,25. Si q vaut 0 ou 1, BS₀ = 0 et BSS n'est pas défini : le programme renvoie `None`.

**Ce que la preuve révèle du mécanisme.** BSS normalise par la difficulté de l'échantillon : il rend comparables un agent qui prédit un événement rare et un agent qui prédit un événement fréquent, ce que BS seul ne permet pas.

**Conséquence pour un agent.** Un BSS négatif dit que la confiance de l'agent fait plus de mal que de bien : on cesse de l'utiliser pour décider (seuil d'escalade, approbation automatique) tant qu'elle n'a pas été recalibrée (cas 1 et 4).

## Démonstration 4 — Décomposition : calibration plus affinement

**Ce qu'on démontre.** On regroupe les prédictions en paquets k qui annoncent la même valeur pₖ ; le paquet k compte nₖ prédictions, dont une fréquence ōₖ d'issues 1. Alors :

$$
BS = \underbrace{\frac{1}{N}\sum_k n_k\,(p_k - \bar{o}_k)^2}_{\text{calibration}} + \underbrace{\frac{1}{N}\sum_k n_k\,\bar{o}_k\,(1 - \bar{o}_k)}_{\text{affinement}}
$$

**L'idée.** Dans un paquet, toutes les annonces sont égales : c'est exactement la situation de la démonstration 2, avec la fréquence observée ōₖ à la place de q. L'erreur du paquet se coupe donc en un écart « annonce − fréquence » au carré et un bruit ōₖ (1 − ōₖ).

**La preuve, pas à pas.**

**Étape 1.** Dans le paquet k, nₖ ōₖ prédictions ont l'issue 1 et coûtent (pₖ − 1)², les nₖ (1 − ōₖ) autres ont l'issue 0 et coûtent pₖ² :

$$
\sum_{i \in k} (p_k - y_i)^2 = n_k \big[\bar{o}_k\,(p_k - 1)^2 + (1 - \bar{o}_k)\, p_k^2\big]
$$

**Étape 2.** Le crochet a la forme de la démonstration 2 avec q = ōₖ ; on applique l'identité des étapes 2 et 3 :

$$
\bar{o}_k\,(p_k - 1)^2 + (1 - \bar{o}_k)\, p_k^2 = (p_k - \bar{o}_k)^2 + \bar{o}_k\,(1 - \bar{o}_k)
$$

**Étape 3.** On additionne sur les paquets et on divise par N, parce que BS est la somme de toutes les erreurs divisée par N. ∎

**Vérification chiffrée.** Agent surconfiant du cas 1 : un seul paquet, p = 0,95, n = 10, fréquence 0,6. Calibration (0,95 − 0,6)² = 0,1225, affinement 0,6 × 0,4 = 0,24, total 0,3625 : c'est le BS calculé directement. Le programme vérifie aussi l'égalité sur les 1 000 prédictions du cas 2.

**Ce que la preuve révèle du mécanisme.** Le terme de calibration s'annule si l'on remplace chaque annonce pₖ par la fréquence observée ōₖ : c'est la recalibration. Le terme d'affinement ne bouge pas : il mesure la capacité du modèle à mettre les cas positifs et négatifs dans des paquets différents, et seule une meilleure information peut le baisser.

**Conséquence pour un agent.** Une table « annonce → fréquence observée », mesurée sur un historique assez grand, recalibre un agent sans le réentraîner : elle supprime le terme de calibration (cas 2). On suit les deux termes séparément : une calibration qui monte appelle une recalibration, un affinement qui monte appelle de meilleures données.

## Démonstration 5 — Le poids d'une seule prédiction

**Ce qu'on démontre.** Une prédiction pèse au plus 1/N dans le score. Si sa confiance pᵢ bouge de Δ, le score bouge de :

$$
\Delta BS = \frac{2\,(p_i - y_i)\,\Delta + \Delta^2}{N}
$$

**L'idée.** Le score est une moyenne de termes bornés par 1 ; une identité remarquable donne la variation exacte d'un carré.

**La preuve, pas à pas.**

**Étape 1.** Le terme de la prédiction i est dans [0 ; 1] (démonstration 1) et il est divisé par N : sa contribution est au plus 1/N.

**Étape 2.** Seul le terme i change quand pᵢ devient pᵢ + Δ ; on développe le carré, parce que (a + Δ)² = a² + 2aΔ + Δ² avec a = pᵢ − yᵢ :

$$
(p_i + \Delta - y_i)^2 - (p_i - y_i)^2 = 2\,(p_i - y_i)\,\Delta + \Delta^2
$$

**Étape 3.** On divise par N, parce que BS est la moyenne des termes. ∎

**Vérification chiffrée.** Dans l'exemple simple, baisser la confiance fausse 0,8 à 0,7 (Δ = −0,1, yᵢ = 0) fait varier BS de (2 × 0,8 × (−0,1) + 0,01) / 3 = (−0,16 + 0,01) / 3 = −0,05, soit (0,64 − 0,49) / 3. Pour un mouvement de 0,01, la variation vaut environ 2 × 0,8 × 0,01 / 3 ≈ 0,00533. Comparaison avec la perte logarithmique : une confiance 0,99 qui échoue coûte 0,99² = 0,9801 en Brier, mais −ln 0,01 ≈ 4,605 en log loss, sans borne quand la confiance tend vers 1.

**Ce que la preuve révèle du mécanisme.** La sensibilité est proportionnelle à l'erreur pᵢ − yᵢ : plus une prédiction est fausse avec assurance, plus chaque point de confiance en trop coûte cher. Mais la borne 1/N empêche une seule catastrophe d'écraser tout le score.

**Conséquence pour un agent.** Le Brier convient au suivi en production (borné, lisible, robuste à une erreur isolée) ; la log loss, qui punit sans limite les certitudes fausses, sert plutôt à l'entraînement (fiche 06). Sur un petit échantillon, une seule annonce surconfiante suffit à faire chuter le BSS (cas 1, sensibilité).

## Exemple simple, à la main

Trois prédictions, confiances 0,9 ; 0,8 ; 0,3, issues réelles 1 ; 0 ; 0 :

$$
BS = \frac{(0{,}9 - 1)^2 + (0{,}8 - 0)^2 + (0{,}3 - 0)^2}{3} = \frac{0{,}01 + 0{,}64 + 0{,}09}{3} \approx 0{,}24667
$$

| i | pᵢ | yᵢ | pᵢ − yᵢ | (pᵢ − yᵢ)² |
| --- | --- | --- | --- | --- |
| 1 | 0,9 | 1 | −0,1 | 0,01 |
| 2 | 0,8 | 0 | 0,8 | 0,64 |
| 3 | 0,3 | 0 | 0,3 | 0,09 |
| somme | | | | 0,74 |

La prédiction à 0,8 qui s'est révélée fausse pèse à elle seule 0,64 sur 0,74. Annoncer 0,5 partout aurait donné 0,25 : l'agent fait à peine mieux qu'une pièce de monnaie.

## Cas d'usage complexes, démontrés

### Cas 1 — Banque de détail de Dubaï : l'agent de conformité KYC qui dit « sûr à 95 % »

**Contexte.** Une banque de détail de Dubaï fait pré-instruire ses dossiers KYC par un agent, qui annonce pour chaque dossier sa confiance que la décision proposée (conforme ou non) est juste. Si la confiance atteint 0,85, la décision est appliquée sans relecture ; sinon un analyste relit. Avant de brancher cette règle, l'équipe compare deux versions de l'agent sur un échantillon de 10 dossiers dont la bonne décision est connue ; elle traite 1 000 dossiers par mois (chiffres illustratifs). Une décision fausse appliquée sans relecture coûte 2 000 AED de remédiation, une relecture 60 AED (illustratif).

**Données.**

- Issues des 10 décisions : 6 justes (y = 1), 4 fausses (y = 0), donc q = 0,6 et BS₀ = 0,24.
- Version surconfiante : 0,95 partout.
- Version calibrée : 0,8 ; 0,9 ; 0,7 ; 0,85 ; 0,75 ; 0,9 pour les décisions justes, 0,3 ; 0,2 ; 0,4 ; 0,1 pour les fausses.

**Calcul pas à pas.**

**Étape 1.** Surconfiante : (6 × 0,05² + 4 × 0,95²) / 10 = (6 × 0,0025 + 4 × 0,9025) / 10 = (0,015 + 3,61) / 10 = 0,3625.

$$
BSS_{\text{sur}} = 1 - \frac{0{,}3625}{0{,}24} \approx -0{,}51042
$$

**Étape 2.** Calibrée, termes : 0,04 ; 0,01 ; 0,09 ; 0,0225 ; 0,0625 ; 0,01 pour les justes, 0,09 ; 0,04 ; 0,16 ; 0,01 pour les fausses ; somme 0,535 ; BS = 0,0535.

$$
BSS_{\text{cal}} = 1 - \frac{0{,}0535}{0{,}24} \approx 0{,}77708
$$

**Étape 3.** Décomposition de la version surconfiante (démonstration 4) : calibration 0,1225 + affinement 0,24 = 0,3625. Recalibrée (annonce 0,6), elle tomberait à 0,24 : honnête, mais sans aucune compétence.

**Étape 4.** Application de la règle 0,85 : la version surconfiante approuve seule les 10 dossiers, dont les 4 faux ; la version calibrée approuve seule 3 dossiers (0,9 ; 0,85 ; 0,9), tous justes, et envoie 7 dossiers en relecture.

**Étape 5.** Coût pour 1 000 dossiers, si l'échantillon est représentatif : surconfiante, 400 décisions fausses appliquées × 2 000 = 800 000 AED ; calibrée, 700 relectures × 60 = 42 000 AED.

**Décision de l'agent.** On branche la règle d'approbation automatique sur la version calibrée seulement (BSS ≈ 0,777) ; la version surconfiante (BSS < 0) ne sert à rien pour décider, son « 95 % » ne contient aucune information.

**Contre-calcul.** En jugeant les deux versions à leur seul taux de bonnes décisions, elles sont identiques : 6 sur 10. C'est leur confiance qui diffère, et seul le Brier la mesure. Brancher la version surconfiante coûterait 800 000 − 42 000 = 758 000 AED de plus pour 1 000 dossiers (illustratif).

**Sensibilité.** Une seule annonce de la version calibrée qui passe de 0,4 à 0,9 sur une décision fausse ajoute (0,81 − 0,16) / 10 = 0,065 au score : BS = 0,1185 et BSS = 1 − 0,1185 / 0,24 = 0,50625, soit environ 0,27 de compétence perdue, et cette décision fausse serait approuvée sans relecture. Sur 10 dossiers, l'estimation est fragile : on la confirme sur un échantillon bien plus grand avant la mise en service.

**En production.** On suit chaque mois le BS, le BSS et la décomposition sur les dossiers relus, avec une alerte si le BSS passe sous 0,5 ou si le terme de calibration dépasse 0,02. La règle d'approbation automatique ne dispense pas des obligations KYC et anti-blanchiment de la banque, dont le détail est à confirmer avec le texte en vigueur de la CBUAE.

### Cas 2 — Assureur auto et santé : recalibrer par paquets la probabilité d'approbation d'un sinistre

**Contexte.** Un assureur auto et santé fait estimer par un modèle la probabilité qu'un sinistre auto soit approuvé après expertise. Il envisage un paiement automatique dès que la probabilité annoncée atteint 0,9. Il reçoit 6 000 sinistres par mois ; un paiement automatique injustifié coûte 1 200 AED net, une revue 45 AED (chiffres illustratifs). Question : le modèle est-il assez calibré pour le paiement automatique ?

**Données.** 1 000 sinistres d'historique, regroupés par probabilité annoncée :

| annonce pₖ | nombre nₖ | approuvés | fréquence ōₖ |
| --- | --- | --- | --- |
| 0,1 | 200 | 30 | 0,15 |
| 0,4 | 300 | 105 | 0,35 |
| 0,7 | 300 | 225 | 0,75 |
| 0,95 | 200 | 160 | 0,80 |

**Calcul pas à pas.**

**Étape 1.** Terme de calibration, paquet par paquet : 200 × 0,05² = 0,5 ; 300 × 0,05² = 0,75 ; 300 × 0,05² = 0,75 ; 200 × 0,15² = 4,5 ; somme 6,5, divisée par 1 000 : 0,0065.

**Étape 2.** Terme d'affinement : ōₖ (1 − ōₖ) vaut 0,1275 ; 0,2275 ; 0,1875 ; 0,16 ; pondéré par nₖ : 200 × 0,1275 + 300 × 0,2275 + 300 × 0,1875 + 200 × 0,16 = 25,5 + 68,25 + 56,25 + 32 = 182 ; divisé par 1 000 : 0,182.

$$
BS = 0{,}0065 + 0{,}182 = 0{,}1885
$$

**Étape 3.** Référence : 30 + 105 + 225 + 160 = 520 approuvés, q = 0,52 et BS₀ = 0,52 × 0,48 = 0,2496, donc BSS = 1 − 0,1885 / 0,2496 ≈ 0,24479.

**Étape 4.** Recalibration (démonstration 4) : on remplace chaque annonce par sa fréquence observée (0,1 → 0,15 ; 0,4 → 0,35 ; 0,7 → 0,75 ; 0,95 → 0,80). La calibration tombe à 0, BS = 0,182 et BSS = 1 − 0,182 / 0,2496 ≈ 0,27083.

**Étape 5.** Paquet 0,95 en paiement automatique : il représente 6 000 × 0,2 = 1 200 sinistres par mois, dont 20 % ne devraient pas être approuvés, soit 240 paiements injustifiés × 1 200 = 288 000 AED par mois, contre 1 200 × 45 = 54 000 AED pour les revoir.

**Décision de l'agent.** Pas de paiement automatique pour ce paquet : recalibré, il annonce 0,80, sous le seuil de 0,9. Les sinistres de ce paquet passent en revue, et le modèle recalibré remplace l'ancien pour les autres usages.

**Contre-calcul.** Sans décomposition, un BSS de 0,245 « positif » aurait pu rassurer ; il cache le seul paquet mal calibré, justement celui qui déclenche le paiement automatique, et ses 288 000 AED de pertes mensuelles (illustratif).

**Sensibilité.** Le paiement automatique d'un paquet vaut la peine si sa perte attendue par sinistre, (1 − ōₖ) × 1 200, est inférieure au coût d'une revue, 45 AED, c'est-à-dire si ōₖ > 1 − 45 / 1 200 = 0,9625 : il faudrait que plus de 96,25 % des sinistres du paquet soient réellement approuvés.

**En production.** On recalcule chaque mois la table « annonce → fréquence » par paquet (diagramme de fiabilité), avec une alerte si un paquet s'écarte de plus de 0,05 de son annonce. L'assurance est supervisée par la CBUAE ; les règles de traitement des sinistres sont à confirmer avec le texte en vigueur.

### Cas 3 — Plateforme d'actifs virtuels agréée VARA : prévoir une tension de liquidité dans l'heure

**Contexte.** Une plateforme d'actifs virtuels agréée par la VARA fait estimer chaque heure, par un modèle, la probabilité qu'une tension de liquidité survienne sur ses portefeuilles chauds dans l'heure qui suit. Une probabilité au-dessus d'un seuil réveille l'astreinte ; au-dessus de 0,8, les retraits sont gelés automatiquement. L'équipe compare trois modèles sur 100 heures d'historique, dont 5 avec une tension (chiffres illustratifs). Réveiller l'astreinte coûte 800 AED, une tension non traitée 20 000 AED, un gel injustifié 5 000 AED (illustratif).

**Données.**

- A, « climatologie » : 0,05 à chaque heure.
- B : 0,6 ; 0,5 ; 0,7 ; 0,3 ; 0,8 sur les 5 heures de tension ; 0,02 sur 85 heures calmes et 0,3 sur 10 heures calmes.
- C : 0,9 là où B annonce au moins 0,3, et 0 ailleurs (même ordre que B, donc même AUC, mais confiance exagérée).
- q = 0,05, donc BS₀ = 0,05 × 0,95 = 0,0475.

**Calcul pas à pas.**

**Étape 1.** A : BS = q (1 − q) = 0,0475 (démonstration 1), BSS = 0.

**Étape 2.** B : heures de tension, 0,4² + 0,5² + 0,3² + 0,7² + 0,2² = 0,16 + 0,25 + 0,09 + 0,49 + 0,04 = 1,03 ; heures calmes, 85 × 0,02² + 10 × 0,3² = 0,034 + 0,9.

$$
BS_B = \frac{1{,}03 + 0{,}034 + 0{,}9}{100} = 0{,}01964 \qquad BSS_B = 1 - \frac{0{,}01964}{0{,}0475} \approx 0{,}58653
$$

**Étape 3.** C : 5 × 0,1² + 10 × 0,9² = 0,05 + 8,1 = 8,15, donc BS = 0,0815 et BSS = 1 − 0,0815 / 0,0475 ≈ −0,71579.

**Étape 4.** Seuil d'astreinte : réveiller vaut mieux dès que p × 20 000 > 800, soit p > 0,04. Avec B, on réveille 15 heures (les 5 tensions et les 10 heures calmes à 0,3) et l'on ne manque aucune tension : 15 × 800 = 12 000 AED. Avec A (0,05 > 0,04), on réveille toutes les heures : 100 × 800 = 80 000 AED.

**Étape 5.** Gel automatique au-dessus de 0,8 : C gèle 15 heures, dont 10 injustifiées, soit 10 × 5 000 = 50 000 AED ; B ne gèle qu'à l'heure annoncée 0,8, qui était une vraie tension.

**Décision de l'agent.** On déploie B. C classe les heures exactement comme B, mais son « 0,9 » est faux deux fois sur trois : il déclencherait des gels injustifiés et ferait perdre confiance à l'astreinte.

**Contre-calcul.** Une évaluation par la seule AUC (leçon 51) ne verrait aucune différence entre B et C, puisque seul l'ordre compte ; le Brier les sépare (0,01964 contre 0,0815). Le modèle A a un BS « petit », 0,0475, qui semble bon, mais un BSS nul : il ne contient aucune information, et s'il annonçait 0,03 au lieu de 0,05, il ne réveillerait jamais l'astreinte et laisserait passer les 5 tensions, soit 5 × 20 000 = 100 000 AED.

**Sensibilité.** Les décisions de B ne changent pas tant que le seuil d'astreinte reste entre 0,02 et 0,3, c'est-à-dire tant que le coût estimé d'une tension non traitée reste entre 800 / 0,3 ≈ 2 667 AED et 800 / 0,02 = 40 000 AED : la décision est robuste à une erreur d'un facteur 2 sur ce coût.

**En production.** On suit le BS et le BSS de B sur une fenêtre glissante de 30 jours, avec une alerte si le BSS passe sous 0,3, et le nombre de gels injustifiés. La VARA attend une gestion documentée du risque de liquidité ; les obligations précises sont à confirmer avec le texte en vigueur.

### Cas 4 — Cabinet RH multi-émirats : la confiance de l'agent après un changement de procédure

**Contexte.** Un cabinet RH multi-émirats fait estimer par un agent la probabilité qu'un dossier de permis de travail soit accepté au premier dépôt auprès du MOHRE. Au-dessus de 0,85, le dossier est déposé sans relecture ; sinon un juriste le relit (150 AED). Un rejet au premier dépôt coûte 1 100 AED de frais et de délai, et une relecture laisse encore 10 % de rejets (chiffres illustratifs). En temps normal, 80 % des dossiers passent et l'agent obtient BS = 0,12. La semaine qui suit un changement de procédure, l'équipe recalcule le score sur 50 dossiers.

**Données.**

- 40 dossiers annoncés à 0,9, dont 24 acceptés ; 10 dossiers annoncés à 0,5, dont 6 acceptés.
- Référence habituelle : BS = 0,12 avec q = 0,8.

**Calcul pas à pas.**

**Étape 1.** Décomposition par paquets : paquet 0,9, fréquence 24 / 40 = 0,6, erreur 40 × ((0,9 − 0,6)² + 0,24) = 40 × (0,09 + 0,24) = 13,2 ; paquet 0,5, fréquence 0,6, erreur 10 × ((0,5 − 0,6)² + 0,24) = 10 × (0,01 + 0,24) = 2,5.

$$
BS = \frac{13{,}2 + 2{,}5}{50} = \frac{15{,}7}{50} = 0{,}314
$$

**Étape 2.** Référence de la semaine : q = 30 / 50 = 0,6, BS₀ = 0,24, donc BSS = 1 − 0,314 / 0,24 ≈ −0,30833. En temps normal, BSS = 1 − 0,12 / (0,8 × 0,2) = 1 − 0,12 / 0,16 = 0,25.

**Étape 3.** Le terme de calibration vaut (40 × 0,09 + 10 × 0,01) / 50 = 0,074 : c'est lui qui a explosé.

**Étape 4.** Coût par dossier du paquet 0,9 : dépôt direct, (1 − 0,6) × 1 100 = 440 AED de rejets attendus ; relecture, 150 + 0,1 × 1 100 = 260 AED.

**Étape 5.** L'écart n'est pas du hasard : sur 40 dossiers de fréquence 0,6, l'écart-type de la fréquence vaut √(0,6 × 0,4 / 40) ≈ 0,0775, et l'écart observé 0,9 − 0,6 = 0,3 représente environ 3,87 écarts-types.

**Décision de l'agent.** Suspendre le dépôt sans relecture : tous les dossiers passent par un juriste tant que l'agent n'est pas recalibré sur la nouvelle procédure. Pour les 40 dossiers du paquet, cela coûte 40 × 260 = 10 400 AED au lieu de 40 × 0,4 × 1 100 = 16 × 1 100 = 17 600 AED en dépôt direct.

**Contre-calcul.** Garder la règle « 0,9 > 0,85, donc dépôt direct » ferait déposer ces 40 dossiers sans relecture : 16 rejets attendus, 17 600 AED, et des candidats qui attendent leur permis plus longtemps (illustratif).

**Sensibilité.** Le dépôt direct redevient meilleur dès que la fréquence réelle du paquet dépasse 1 − 260 / 1 100 ≈ 0,76364. Quand la recalibration ramènera la fréquence observée au-dessus de 76,4 %, la règle pourra être rétablie.

**En production.** On calcule chaque semaine le BS, le BSS et le terme de calibration par type de permis, avec une alerte si le BSS devient négatif ; un changement de procédure annoncé déclenche une recalibration préventive. Les exigences du MOHRE pour chaque type de permis sont à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Confiances 0,7 et 0,2, issues 1 et 1. Calculer BS.

**Exercice 2.** Un événement a un taux de base de 0,1. Calculer BS₀.

**Exercice 3.** Un événement a une probabilité réelle de 0,7. Calculer l'erreur attendue si l'on annonce 0,7, puis 0,9.

**Exercice 4.** Démontrer que q(p − 1)² + (1 − q)p² = (p − q)² + q(1 − q).

**Exercice 5.** Un agent a BS = 0,18 sur un événement de taux de base 0,4. Calculer son BSS.

**Exercice 6 (cas modifié).** Dans le cas 2, le paquet annoncé à 0,95 compte en réalité 194 sinistres approuvés sur 200 (fréquence 0,97). Recalculer BS et BSS, puis dire si le paiement automatique de ce paquet est justifié.

**Exercice 7 (trouver l'erreur).** Un collègue écrit : « Mon modèle d'alerte de liquidité a BS = 0,045 : c'est excellent, presque parfait. » Les tensions surviennent 5 % du temps. Trouver l'erreur de raisonnement.

**Exercice 8 (redémontrer de mémoire).** Redémontrer que le Brier est une règle propre (démonstration 2), puis en déduire la décomposition par paquets (démonstration 4).

## Corrigé

**Exercice 1.** Erreurs : 0,7 − 1 = −0,3 et 0,2 − 1 = −0,8 ; carrés 0,09 et 0,64 ; somme 0,73 ; BS = 0,73 / 2 = 0,365.

**Exercice 2.** BS₀ = q (1 − q) = 0,1 × 0,9 = 0,09.

**Exercice 3.** À 0,7 : (0,7 − 0,7)² + 0,7 × 0,3 = 0,21. À 0,9 : 0,2² + 0,21 = 0,04 + 0,21 = 0,25. Exagérer coûte 0,04.

**Exercice 4.** Gauche : qp² − 2qp + q + p² − qp² = p² − 2qp + q. Droite : p² − 2pq + q² + q − q² = p² − 2pq + q. Les deux membres sont égaux.

**Exercice 5.** BS₀ = 0,4 × 0,6 = 0,24, donc BSS = 1 − 0,18 / 0,24 = 1 − 0,75 = 0,25.

**Exercice 6.** Calibration du paquet : 200 × (0,95 − 0,97)² = 200 × 0,0004 = 0,08 ; total (0,5 + 0,75 + 0,75 + 0,08) / 1 000 = 0,00208. Affinement du paquet : 200 × 0,97 × 0,03 = 5,82 ; total (25,5 + 68,25 + 56,25 + 5,82) / 1 000 = 0,15582. BS = 0,00208 + 0,15582 = 0,1579. q = (30 + 105 + 225 + 194) / 1 000 = 0,554, BS₀ = 0,554 × 0,446 = 0,247084, BSS ≈ 0,36095. Et 0,97 > 0,9625 : le paiement automatique de ce paquet devient justifié.

**Exercice 7.** Le collègue oublie la référence : avec q = 0,05, BS₀ = 0,05 × 0,95 = 0,0475, donc BSS = 1 − 0,045 / 0,0475 ≈ 0,0526. Le modèle fait à peine mieux que l'annonce constante 5 % : un BS petit sur un événement rare ne prouve rien (démonstration 1).

**Exercice 8.** On écrit 𝔼[(p − Y)²] = q (p − 1)² + (1 − q) p², on développe en p² − 2qp + q, on complète le carré en (p − q)² + q (1 − q), minimal en p = q. Pour un paquet de nₖ annonces égales à pₖ et de fréquence observée ōₖ, la même identité avec q = ōₖ donne nₖ [(pₖ − ōₖ)² + ōₖ (1 − ōₖ)] ; on additionne sur les paquets et on divise par N.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`brier(p, y)`** — Cette fonction est l'examinateur qui note un prévisionniste sur l'écart entre ce qu'il a annoncé et ce qui est arrivé : elle reçoit la liste des confiances annoncées et la liste des issues observées, lève une `ValueError` si les deux listes n'ont pas la même longueur, si une confiance sort de l'intervalle de 0 à 1 ou si une issue n'est ni 0 ni 1, et renvoie `None` pour des listes vides. Sinon, elle renvoie la moyenne des carrés (p − y)², soit 0,24667 pour les annonces 0,9, 0,8 et 0,3 face aux issues 1, 0 et 0 de l'exemple simple, et tous les cas s'en servent.

**`erreur_attendue(p, q)`** — On la voit en conseiller qui prévient un prévisionniste de ce que lui coûtera, en moyenne, une annonce donnée : elle reçoit la confiance p qu'il annonce et la vraie fréquence q de l'événement, et renvoie q(p − 1)² + (1 − q)p², le score de Brier attendu. Cette quantité est la plus petite quand p = q, ce qui fait du Brier une règle propre : pour q = 0,7, annoncer 0,7 coûte 0,21 et exagérer à 0,9 coûte 0,25 ; `main` vérifie sur une grille de 101 annonces qu'elle égale toujours (p − q)² + q(1 − q).

**`bss(bs, q)`** — Cette fonction est l'arbitre qui compare le prévisionniste à un rival paresseux, celui qui annonce toujours le taux de base : elle reçoit un score de Brier et la fréquence q de l'événement, calcule le score de référence q(1 − q), renvoie `None` s'il est nul, c'est-à-dire si q vaut 0 ou 1, et sinon renvoie 1 − BS/(q(1 − q)). Le résultat vaut 1 pour un prévisionniste parfait, 0 pour le paresseux et devient négatif quand on fait pire que lui : −0,25 pour un score de 0,3 quand q = 0,6, et 0,0526 seulement pour l'événement rare de l'exercice 7.

**`decomposition(paquets)`** — Celle-ci est le comptable qui sépare deux sources d'erreur, mal estimer et ne pas savoir trier : elle reçoit une liste de paquets, chacun décrit par la confiance annoncée, le nombre d'annonces et le nombre de positifs observés, renvoie `None` si le total est nul, puis calcule la calibration, moyenne pondérée des carrés des écarts entre annonce et fréquence observée, et l'affinement, moyenne pondérée de ōₖ(1 − ōₖ). Elle renvoie ces deux termes, leur somme, qui est le score de Brier, et la fréquence globale q : pour un paquet annoncé à 0,95 mais observé à 0,6, elle donne 0,1225 + 0,24 = 0,3625.

**`deplier(paquets)`** — Cette petite fonction défait les paquets pour retrouver les annonces une à une, comme on dépile des cartons pour compter les pièces : elle reçoit la même liste de paquets que `decomposition` et construit, pour chacun, nₖ copies de la confiance annoncée et autant d'issues, avec d'abord les positifs à 1 puis les autres à 0. Elle renvoie les deux listes, que le cas 2 confie à `brier` pour vérifier que le calcul direct redonne exactement le score de 0,1885 obtenu par la décomposition.

**`proche(x, attendu, decimales)`** — Ce petit contrôleur compare deux nombres comme on rapproche deux lignes d'un registre arrondi : il reçoit la valeur calculée, la valeur attendue et un nombre de décimales, arrondit les deux à ce nombre de chiffres et renvoie vrai s'ils coïncident. Presque tous les `assert` de `main` passent par lui, de la calibration 0,1225 de la démonstration 4 jusqu'aux bornes de 2 667 et 40 000 AED du cas 3, pour confronter les résultats aux valeurs écrites dans la fiche.

**`demonstrations()`** — Cette fonction rejoue les cinq démonstrations : elle ne reçoit rien, montre qu'annoncer toujours 0,5 donne un score de 0,25 et qu'annoncer le taux de base 0,6 donne 0,24, puis que, pour q = 0,7, le Brier récompense l'annonce honnête, 0,21 contre 0,25 à 0,9, alors que l'écart absolu, 0,42 à 0,7 et 0,30 à 1, pousse à exagérer. Elle calcule ensuite les scores de compétence 1, 0 et −0,25, la décomposition 0,1225 + 0,24 = 0,3625, la baisse de 0,05 du score quand une annonce fautive passe de 0,8 à 0,7, et compare le Brier, 0,9801, et la perte logarithmique, 4,605, d'une annonce fausse à 0,99 ; elle imprime et renvoie ces nombres.

**`cas_1_banque_kyc(y, base)`** — Cette fonction raconte une banque qui veut appliquer sans relecture les décisions de conformité dont l'agent se dit sûr à 0,85 au moins, et qui compare deux versions sur dix dossiers : elle reçoit les issues de ces dix dossiers, six décisions justes puis quatre fausses, et le score de référence 0,24. La version surconfiante, qui annonce 0,95 partout, obtient 0,3625 et une compétence de −0,51042, et ses dix décisions passeraient sans relecture, dont quatre fausses ; la version calibrée obtient 0,0535 et 0,77708, avec trois décisions automatiques toutes justes. Sur 1 000 dossiers, cela fait 800 000 contre 42 000 AED ; elle mesure aussi l'effet d'une seule annonce dégradée, un score de 0,1185, et renvoie ces résultats.

**`cas_2_assureur_paquets()`** — On y suit un assureur qui envisage de payer automatiquement les sinistres dont la probabilité d'approbation annoncée atteint 0,9, avec 6 000 sinistres par mois : la fonction ne reçoit rien, décrit quatre paquets d'annonces à 0,1, 0,4, 0,7 et 0,95, et trouve une calibration de 0,0065, un affinement de 0,182, un score de 0,1885, retrouvé en dépliant les paquets, une fréquence de 0,52 et une compétence de 0,24479. Recalibré, le modèle atteindrait 0,182 et 0,27083 ; mais le paquet annoncé à 0,95 n'est approuvé qu'à 80 %, si bien que le paiement automatique coûterait 288 000 AED par mois contre 54 000 pour une revue, la bascule étant à 0,9625 ; elle renvoie ces nombres.

**`cas_3_crypto_liquidite()`** — Cette fonction met en scène l'astreinte d'une plateforme d'actifs virtuels qui compare trois modèles de tension de liquidité sur cent heures, dont cinq avec une tension : elle ne reçoit rien, construit le modèle A, qui annonce 5 % à chaque heure, le modèle B, qui distingue les heures à risque, et le modèle C, qui pousse les annonces de B à 0,9 ou à 0, puis obtient des scores de 0,0475, 0,01964 et 0,0815, soit des compétences de 0,58653 pour B et −0,71579 pour C. Avec le seuil de réveil 800/20 000 = 0,04, B réveille l'astreinte 15 heures sans manquer de tension, pour 12 000 AED contre 80 000 pour A, et C gèlerait 10 fois les retraits à tort ; elle calcule les bornes de 2 667 et 40 000 AED du coût de crise et renvoie le tout.

**`cas_4_rh_visas()`** — Ici, un cabinet de recrutement dépose sans relecture les dossiers de permis de travail dont l'agent annonce l'acceptation à plus de 0,85, et recalcule le score sur 50 dossiers après un changement de procédure : la fonction ne reçoit rien, prend 40 dossiers annoncés à 0,9 dont seulement 24 acceptés et 10 annoncés à 0,5 dont 6 acceptés, et trouve un score de 0,314, une fréquence de 0,6 et une compétence de −0,30833, contre 0,25 en temps normal. Elle compare le dépôt direct, 440 AED de rejets attendus par dossier, à la relecture, 260 AED, calcule la fréquence de bascule 0,76364, puis un écart-type de 0,0775 qui place l'écart entre 0,9 et 0,6 à 3,87 écarts-types, donc bien réel, et renvoie ces résultats.

**`corrige()`** — Celle-ci est le correcteur qui refait au propre les exercices chiffrés : elle ne reçoit rien et calcule le score de 0,365 de l'exercice 1, la valeur 0,09 de l'exercice 2, les scores attendus 0,21 et 0,25 de l'exercice 3, la compétence 0,25 de l'exercice 5, la décomposition de l'exercice 6, où le paquet à 0,95 devient approuvé à 97 %, avec un score de 0,1579 et une compétence de 0,36095, et la compétence de 0,0526 de l'exercice 7. Elle imprime ces résultats et renvoie le score de l'exercice 1, la décomposition et la compétence de l'exercice 7.

**`main()`** — C'est le chef d'orchestre de la fiche : il appelle `demonstrations` et vérifie chacun de ses nombres, recalcule l'exemple simple, 0,24667, et le score de référence 0,24 des dix dossiers, puis joue le cas 1. Il vérifie ensuite, pour q valant 0,1, 0,3 et 0,7, que la meilleure annonce sur une grille de 101 valeurs est exactement q, joue les cas 2 à 4 et le corrigé, et s'assure que des listes vides donnent `None`, que q = 1 rend la compétence indéfinie et que des entrées invalides lèvent une `ValueError` ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tout concorde.

```python
"""Démonstration 20 — score de Brier : bornes, règle propre, compétence, décomposition, poids d'une erreur, quatre cas."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def brier(p, y):
    """BS = moyenne des (p - y)² ; None pour une liste vide."""
    if len(p) != len(y):
        raise ValueError("autant de confiances que d'issues")
    if any(not 0 <= a <= 1 for a in p) or any(b not in (0, 1) for b in y):
        raise ValueError("p dans [0, 1] et y dans {0, 1}")
    if not p:
        return None
    return sum((a - b) ** 2 for a, b in zip(p, y)) / len(p)


def erreur_attendue(p, q):
    return q * (p - 1) ** 2 + (1 - q) * p ** 2


def bss(bs, q):
    """Score de compétence 1 - BS / (q (1 - q)) ; None si la référence est nulle (q = 0 ou 1)."""
    base = q * (1 - q)
    return None if base == 0 else 1 - bs / base


def decomposition(paquets):
    """paquets = [(p_k, n_k, positifs_k)] : renvoie (calibration, affinement, BS, q)."""
    n = sum(nk for _, nk, _ in paquets)
    if n == 0:
        return None
    calibration = sum(nk * (pk - pos / nk) ** 2 for pk, nk, pos in paquets) / n
    affinement = sum(nk * (pos / nk) * (1 - pos / nk) for pk, nk, pos in paquets) / n
    q = sum(pos for _, _, pos in paquets) / n
    return calibration, affinement, calibration + affinement, q


def deplier(paquets):
    p, y = [], []
    for pk, nk, pos in paquets:
        p += [pk] * nk
        y += [1] * pos + [0] * (nk - pos)
    return p, y


def proche(x, attendu, decimales):
    return round(x, decimales) == round(attendu, decimales)


def demonstrations():
    print("Démonstrations")
    toujours_moitie = brier([0.5] * 4, [1, 0, 1, 0])
    print(f"  D1 toujours 0.5 : {toujours_moitie} ; taux de base q = 0.6 : {0.6 * 0.4:.2f}")
    absolu = {p: 0.7 * (1 - p) + 0.3 * p for p in (0.7, 1.0)}
    print(f"  D2 q = 0.7 : Brier à 0.7 {erreur_attendue(0.7, 0.7):.2f}, à 0.9 {erreur_attendue(0.9, 0.7):.2f} ;"
          f" écart absolu à 0.7 {absolu[0.7]:.2f}, à 1 {absolu[1.0]:.2f}")
    print(f"  D3 BSS : parfait {bss(0, 0.6):.0f} ; référence {bss(0.24, 0.6):.0f} ; BS 0.3 -> {bss(0.3, 0.6):.2f}")
    cal, aff, bs, q = decomposition([(0.95, 10, 6)])
    print(f"  D4 annonce 0.95, fréquence 0.6 : calibration {cal:.4f} + affinement {aff:.2f} = {bs:.4f}")
    gain = brier([0.9, 0.8, 0.3], [1, 0, 0]) - brier([0.9, 0.7, 0.3], [1, 0, 0])
    print(f"  D5 0.8 -> 0.7 sur l'erreur : BS baisse de {gain:.2f} ; 0.99 faux : Brier {0.99 ** 2:.4f},"
          f" log loss {-math.log(0.01):.3f}")
    return {"moitie": toujours_moitie, "absolu": absolu, "cal": cal, "aff": aff, "bs": bs, "gain": gain}


def cas_1_banque_kyc(y, base):
    sur = [0.95] * 10
    cal = [0.8, 0.9, 0.7, 0.85, 0.75, 0.9, 0.3, 0.2, 0.4, 0.1]
    bs_sur, bs_cal = brier(sur, y), brier(cal, y)
    termes = [round((a - b) ** 2, 4) for a, b in zip(cal, y)]
    auto_sur = sum(1 for a in sur if a >= 0.85)
    erreurs_sur = sum(1 for a, b in zip(sur, y) if a >= 0.85 and b == 0)
    auto_cal = sum(1 for a in cal if a >= 0.85)
    erreurs_cal = sum(1 for a, b in zip(cal, y) if a >= 0.85 and b == 0)
    cout_sur = 1000 * erreurs_sur / 10 * 2000
    cout_cal = 1000 * (10 - auto_cal) / 10 * 60
    degrade = cal[:8] + [0.9] + cal[9:]
    bs_degrade = brier(degrade, y)
    print(f"Cas 1 : surconfiant BS = {bs_sur:.4f}, BSS = {1 - bs_sur / base:.5f} ; calibré BS = {bs_cal:.4f},"
          f" BSS = {1 - bs_cal / base:.5f}")
    print(f"  auto-approuvés : surconfiant {auto_sur} dont {erreurs_sur} faux ; calibré {auto_cal} dont {erreurs_cal} faux ;"
          f" coût pour 1000 dossiers {cout_sur:.0f} contre {cout_cal:.0f} AED")
    print(f"  une annonce 0.4 -> 0.9 : BS {bs_degrade:.4f}, BSS {1 - bs_degrade / base:.5f}")
    return {"bs_sur": bs_sur, "bs_cal": bs_cal, "termes": termes, "auto_sur": auto_sur, "erreurs_sur": erreurs_sur,
            "auto_cal": auto_cal, "erreurs_cal": erreurs_cal, "cout_sur": cout_sur, "cout_cal": cout_cal,
            "bs_degrade": bs_degrade, "bss_degrade": 1 - bs_degrade / base}


def cas_2_assureur_paquets():
    paquets = [(0.1, 200, 30), (0.4, 300, 105), (0.7, 300, 225), (0.95, 200, 160)]
    cal, aff, bs, q = decomposition(paquets)
    p, y = deplier(paquets)
    direct = brier(p, y)
    recal = decomposition([(pos / nk, nk, pos) for _, nk, pos in paquets])
    pertes = 6000 * 0.2 * (1 - 0.80) * 1200
    revue = 6000 * 0.2 * 45
    bascule = 1 - 45 / 1200
    print(f"Cas 2 : calibration {cal:.4f} ; affinement {aff:.3f} ; BS {bs:.4f} (direct {direct:.4f}) ; q {q:.2f} ;"
          f" BSS {bss(bs, q):.5f}")
    print(f"  recalibré : BS {recal[2]:.3f}, BSS {bss(recal[2], q):.5f} ; paquet 0.95 : pertes {pertes:.0f}"
          f" contre revue {revue:.0f} AED/mois ; bascule {bascule:.4f}")
    return {"cal": cal, "aff": aff, "bs": bs, "direct": direct, "q": q, "bss": bss(bs, q), "recal": recal,
            "bss_recal": bss(recal[2], q), "pertes": pertes, "revue": revue, "bascule": bascule}


def cas_3_crypto_liquidite():
    evenements = [0.6, 0.5, 0.7, 0.3, 0.8]
    p_b = evenements + [0.02] * 85 + [0.3] * 10
    y = [1] * 5 + [0] * 95
    p_a = [0.05] * 100
    p_c = [0.9 if x >= 0.3 else 0.0 for x in p_b]
    bs = {"A": brier(p_a, y), "B": brier(p_b, y), "C": brier(p_c, y)}
    q = 0.05
    seuil = 800 / 20000
    escalades_b = sum(1 for x in p_b if x > seuil)
    manques_b = sum(1 for x, o in zip(p_b, y) if x <= seuil and o == 1)
    gels_c = sum(1 for x, o in zip(p_c, y) if x >= 0.8 and o == 0)
    gels_b = sum(1 for x, o in zip(p_b, y) if x >= 0.8 and o == 0)
    bornes = (800 / 0.3, 800 / 0.02)
    print(f"Cas 3 : BS A {bs['A']:.4f}, B {bs['B']:.5f}, C {bs['C']:.4f} ; BSS B {bss(bs['B'], q):.5f},"
          f" C {bss(bs['C'], q):.5f}")
    print(f"  seuil {seuil:.2f} : B escalade {escalades_b} h, en manque {manques_b} ; coût B {escalades_b * 800},"
          f" A {100 * 800} AED ; gels injustifiés C {gels_c}, B {gels_b} ;"
          f" bascule coût de crise [{bornes[0]:.0f} ; {bornes[1]:.0f}] AED")
    return {"bs": bs, "bss_b": bss(bs["B"], q), "bss_c": bss(bs["C"], q), "seuil": seuil, "esc_b": escalades_b,
            "manques_b": manques_b, "gels_c": gels_c, "gels_b": gels_b, "bornes": bornes}


def cas_4_rh_visas():
    paquets = [(0.9, 40, 24), (0.5, 10, 6)]
    cal, aff, bs, q = decomposition(paquets)
    direct_09 = (1 - 0.6) * 1100
    relecture = 150 + 0.1 * 1100
    bascule = 1 - relecture / 1100
    ecart_type = math.sqrt(0.6 * 0.4 / 40)
    z = (0.9 - 0.6) / ecart_type
    print(f"Cas 4 : BS {bs:.3f} ; q {q:.1f} ; BSS {bss(bs, q):.5f} (référence 0.12 -> BSS {bss(0.12, 0.8):.2f}) ;"
          f" calibration {cal:.3f}")
    print(f"  dépôt direct {direct_09:.0f} contre relecture {relecture:.0f} AED par dossier ; bascule {bascule:.5f} ;"
          f" écart-type {ecart_type:.4f}, écart {z:.2f} écarts-types")
    return {"cal": cal, "aff": aff, "bs": bs, "q": q, "bss": bss(bs, q), "direct": direct_09, "relecture": relecture,
            "bascule": bascule, "ecart_type": ecart_type, "z": z}


def corrige():
    e1 = brier([0.7, 0.2], [1, 1])
    e6 = decomposition([(0.1, 200, 30), (0.4, 300, 105), (0.7, 300, 225), (0.95, 200, 194)])
    e7 = bss(0.045, 0.05)
    print(f"Corrigé : ex1 {e1:.3f} ; ex2 {0.1 * 0.9:.2f} ; ex3 {erreur_attendue(0.7, 0.7):.2f} et"
          f" {erreur_attendue(0.9, 0.7):.2f} ; ex5 {1 - 0.18 / 0.24:.2f} ; ex6 BS {e6[2]:.4f}, BSS {bss(e6[2], e6[3]):.5f} ;"
          f" ex7 BSS {e7:.4f}")
    return e1, e6, e7


def main() -> None:
    d = demonstrations()
    assert d["moitie"] == 0.25 and proche(0.6 * 0.4, 0.24, 9)
    assert proche(d["absolu"][0.7], 0.42, 9) and proche(d["absolu"][1.0], 0.3, 9)       # D2 : l'écart absolu triche
    assert proche(erreur_attendue(0.9, 0.7) - erreur_attendue(0.7, 0.7), 0.04, 9)
    assert bss(0, 0.6) == 1 and proche(bss(0.24, 0.6), 0, 9) and proche(bss(0.3, 0.6), -0.25, 9)
    assert proche(d["cal"], 0.1225, 9) and proche(d["aff"], 0.24, 9) and proche(d["bs"], 0.3625, 9)
    assert proche(d["gain"], 0.05, 9) and proche(0.99 ** 2, 0.9801, 9) and proche(-math.log(0.01), 4.605, 3)
    assert proche((0.64 - 0.49) / 3, 0.05, 9) and proche(2 * 0.8 * 0.01 / 3, 0.00533, 5)
    assert proche(0.6 * 0.16, 0.096, 9) and proche(0.4 * 0.36, 0.144, 9) and proche(0.096 + 0.144, 0.24, 9)

    print(f"Exemple simple : BS = {brier([0.9, 0.8, 0.3], [1, 0, 0]):.5f}")
    assert round(brier([0.9, 0.8, 0.3], [1, 0, 0]), 5) == 0.24667 and proche(0.01 + 0.64 + 0.09, 0.74, 9)
    assert proche(0.64 / 0.74, 0.86, 2)
    y = [1] * 6 + [0] * 4
    base = brier([0.6] * 10, y)
    assert round(base, 2) == 0.24 and proche(6 * 0.16 + 4 * 0.36, 2.4, 9)

    c1 = cas_1_banque_kyc(y, base)
    assert round(c1["bs_sur"], 4) == 0.3625 and round(c1["bs_cal"], 4) == 0.0535
    assert round(1 - c1["bs_cal"] / base, 5) == 0.77708 and round(1 - c1["bs_sur"] / base, 5) == -0.51042
    assert proche(6 * 0.05 ** 2 + 4 * 0.95 ** 2, 3.625, 9) and proche(6 * 0.0025, 0.015, 9) and proche(4 * 0.9025, 3.61, 9)
    assert c1["termes"] == [0.04, 0.01, 0.09, 0.0225, 0.0625, 0.01, 0.09, 0.04, 0.16, 0.01]
    assert proche(sum(c1["termes"]), 0.535, 9)
    assert (c1["auto_sur"], c1["erreurs_sur"], c1["auto_cal"], c1["erreurs_cal"]) == (10, 4, 3, 0)
    assert proche(c1["cout_sur"], 800_000, 6) and proche(c1["cout_cal"], 42_000, 6)
    assert proche(c1["bs_degrade"], 0.1185, 9) and proche(c1["bss_degrade"], 0.50625, 9)
    assert proche((0.81 - 0.16) / 10, 0.065, 9) and proche(0.77708 - c1["bss_degrade"], 0.27, 2)
    assert proche(c1["cout_sur"] - c1["cout_cal"], 758_000, 6)

    for q in (0.1, 0.3, 0.7):                                                            # démonstration 2
        grille = [k / 100 for k in range(101)]
        meilleur = min(grille, key=lambda p: erreur_attendue(p, q))
        assert abs(meilleur - q) < 1e-9
        for p in grille:
            assert abs(erreur_attendue(p, q) - ((p - q) ** 2 + q * (1 - q))) < 1e-12        # exercice 4
            assert erreur_attendue(p, q) >= q * (1 - q) - 1e-12

    c2 = cas_2_assureur_paquets()
    assert proche(c2["cal"], 0.0065, 9) and proche(c2["aff"], 0.182, 9) and proche(c2["bs"], 0.1885, 9)
    assert proche(c2["direct"], c2["bs"], 12) and proche(c2["q"], 0.52, 9) and proche(0.52 * 0.48, 0.2496, 9)
    assert proche(c2["bss"], 0.24479, 5) and proche(c2["recal"][2], 0.182, 9) and proche(c2["recal"][0], 0, 12)
    assert proche(c2["bss_recal"], 0.27083, 5)
    assert [round(x, 4) for x in (0.15 * 0.85, 0.35 * 0.65, 0.75 * 0.25, 0.8 * 0.2)] == [0.1275, 0.2275, 0.1875, 0.16]
    assert [round(n * (p - o) ** 2, 2) for p, n, o in ((0.1, 200, 0.15), (0.4, 300, 0.35), (0.7, 300, 0.75),
                                                       (0.95, 200, 0.8))] == [0.5, 0.75, 0.75, 4.5]
    assert proche(200 * 0.1275 + 300 * 0.2275 + 300 * 0.1875 + 200 * 0.16, 182, 9)
    assert proche(c2["pertes"], 288_000, 6) and proche(c2["revue"], 54_000, 6) and proche(c2["bascule"], 0.9625, 9)
    assert proche(6000 * 0.2, 1200, 9) and proche(1200 * 0.2, 240, 9)

    c3 = cas_3_crypto_liquidite()
    assert proche(c3["bs"]["A"], 0.0475, 9) and proche(c3["bs"]["B"], 0.01964, 9) and proche(c3["bs"]["C"], 0.0815, 9)
    assert proche(c3["bss_b"], 0.58653, 5) and proche(c3["bss_c"], -0.71579, 5) and proche(0.05 * 0.95, 0.0475, 9)
    assert proche(0.16 + 0.25 + 0.09 + 0.49 + 0.04, 1.03, 9) and proche(85 * 0.02 ** 2, 0.034, 9) and proche(10 * 0.09, 0.9, 9)
    assert proche(5 * 0.01 + 10 * 0.81, 8.15, 9)
    assert proche(c3["seuil"], 0.04, 9) and c3["esc_b"] == 15 and c3["manques_b"] == 0
    assert 15 * 800 == 12_000 and 100 * 800 == 80_000 and 5 * 20_000 == 100_000
    assert c3["gels_c"] == 10 and c3["gels_b"] == 0 and 10 * 5000 == 50_000
    assert proche(c3["bornes"][0], 2667, 0) and proche(c3["bornes"][1], 40000, 6)

    c4 = cas_4_rh_visas()
    assert proche(c4["bs"], 0.314, 9) and proche(c4["q"], 0.6, 9) and proche(c4["bss"], -0.30833, 5)
    assert proche(40 * (0.09 + 0.24), 13.2, 9) and proche(10 * (0.01 + 0.24), 2.5, 9) and proche(15.7 / 50, 0.314, 9)
    assert proche(bss(0.12, 0.8), 0.25, 9) and proche(0.8 * 0.2, 0.16, 9) and proche(c4["cal"], 0.074, 9)
    assert proche(c4["direct"], 440, 9) and proche(c4["relecture"], 260, 9) and proche(c4["bascule"], 0.76364, 5)
    assert proche(c4["ecart_type"], 0.0775, 4) and proche(c4["z"], 3.87, 2)
    assert proche(40 * 0.4, 16, 9) and proche(16 * 1100, 17_600, 9) and proche(40 * 260, 10_400, 9)

    e1, e6, e7 = corrige()
    assert round(e1, 3) == 0.365 and round(erreur_attendue(0.9, 0.7), 2) == 0.25 and round(1 - 0.18 / 0.24, 2) == 0.25
    assert proche(0.09 + 0.64, 0.73, 9) and proche(0.2 ** 2 + 0.21, 0.25, 9)
    assert proche(e6[0], 0.00208, 9) and proche(e6[1], 0.15582, 9) and proche(e6[2], 0.1579, 9) and proche(e6[3], 0.554, 9)
    assert proche(bss(e6[2], e6[3]), 0.36095, 5) and 0.97 > c2["bascule"] and proche(0.554 * 0.446, 0.247084, 9)
    assert proche(e7, 0.0526, 4) and proche(0.0475, 0.05 * 0.95, 9)
    assert brier([], []) is None and bss(0.1, 1.0) is None
    for mauvais in (lambda: brier([1.2], [1]), lambda: brier([0.5], [2]), lambda: brier([0.5, 0.4], [1])):
        try:
            mauvais()
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError attendue")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Démonstrations
  D1 toujours 0.5 : 0.25 ; taux de base q = 0.6 : 0.24
  D2 q = 0.7 : Brier à 0.7 0.21, à 0.9 0.25 ; écart absolu à 0.7 0.42, à 1 0.30
  D3 BSS : parfait 1 ; référence 0 ; BS 0.3 -> -0.25
  D4 annonce 0.95, fréquence 0.6 : calibration 0.1225 + affinement 0.24 = 0.3625
  D5 0.8 -> 0.7 sur l'erreur : BS baisse de 0.05 ; 0.99 faux : Brier 0.9801, log loss 4.605
Exemple simple : BS = 0.24667
Cas 1 : surconfiant BS = 0.3625, BSS = -0.51042 ; calibré BS = 0.0535, BSS = 0.77708
  auto-approuvés : surconfiant 10 dont 4 faux ; calibré 3 dont 0 faux ; coût pour 1000 dossiers 800000 contre 42000 AED
  une annonce 0.4 -> 0.9 : BS 0.1185, BSS 0.50625
Cas 2 : calibration 0.0065 ; affinement 0.182 ; BS 0.1885 (direct 0.1885) ; q 0.52 ; BSS 0.24479
  recalibré : BS 0.182, BSS 0.27083 ; paquet 0.95 : pertes 288000 contre revue 54000 AED/mois ; bascule 0.9625
Cas 3 : BS A 0.0475, B 0.01964, C 0.0815 ; BSS B 0.58653, C -0.71579
  seuil 0.04 : B escalade 15 h, en manque 0 ; coût B 12000, A 80000 AED ; gels injustifiés C 10, B 0 ; bascule coût de crise [2667 ; 40000] AED
Cas 4 : BS 0.314 ; q 0.6 ; BSS -0.30833 (référence 0.12 -> BSS 0.25) ; calibration 0.074
  dépôt direct 440 contre relecture 260 AED par dossier ; bascule 0.76364 ; écart-type 0.0775, écart 3.87 écarts-types
Corrigé : ex1 0.365 ; ex2 0.09 ; ex3 0.21 et 0.25 ; ex5 0.25 ; ex6 BS 0.1579, BSS 0.36095 ; ex7 BSS 0.0526
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme mesure la qualité des confiances annoncées par un agent, les compare à la référence « taux de base », puis sépare l'erreur de calibration de l'affinement.

```text
ALGORITHME BrierEtCompétence
ENTRÉES : confiances p₁ … pₙ, issues y₁ … yₙ (0 ou 1)
SORTIE  : (BS, BSS, calibration, affinement), ou « indéfini » si n = 0

  SI n = 0 ALORS RETOURNER indéfini
  BS ← 0
  POUR i DE 1 À n FAIRE
      BS ← BS + (pᵢ − yᵢ)²
  FIN POUR
  BS ← BS / n
  q ← moyenne des yᵢ
  BS₀ ← q × (1 − q)
  BSS ← 1 − BS / BS₀, ou indéfini si BS₀ = 0
  POUR chaque paquet k d'annonces égales pₖ FAIRE
      ōₖ ← fréquence des yᵢ = 1 dans le paquet
      calibration ← calibration + nₖ × (pₖ − ōₖ)² / n
      affinement  ← affinement + nₖ × ōₖ × (1 − ōₖ) / n
  FIN POUR
  RETOURNER BS, BSS, calibration, affinement
```

**Complexité.** O(n) en temps pour le score et pour la décomposition (un passage pour regrouper les annonces), O(K) en mémoire pour K paquets. La recherche de la meilleure annonce p sur une grille de 101 valeurs (démonstration 2) coûte O(101) par valeur de q.

**Du squelette au code.** Le score est `brier(p, y)`, la référence est `brier([0.6] * 10, y)` dans `main`, et l'erreur attendue de la démonstration 2 est `erreur_attendue(p, q)`, minimisée sur la grille `grille`. Le score de compétence est `bss(bs, q)`, la décomposition `decomposition(paquets)`, et `deplier(paquets)` reconstruit les listes pour vérifier que les deux calculs coïncident. Les quatre cas sont `cas_1_banque_kyc(y, base)`, `cas_2_assureur_paquets()`, `cas_3_crypto_liquidite()` et `cas_4_rh_visas()`.
