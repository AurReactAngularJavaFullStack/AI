# 23 — Vraisemblance autorégressive : démonstrations

> Fiche : [23 — Vraisemblance autorégressive](<../../Images/03-Modele/23_vraisemblance_autoregressive.md>) · Image : `23_vraisemblance_autoregressive.jpg` · Leçon : [Étape 3 — Fondements de la softmax](<../../02-LLM-Softmax-et-Prompts/03-Fondements-Softmax-et-LLM.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
P(x_{1:n} \mid c) = \prod_{t=1}^{n} P(x_t \mid x_{<t}, c)
$$

Un modèle de langage écrit un token à la fois. La probabilité d'une phrase entière est le produit des probabilités de chaque token, sachant le contexte c et les tokens déjà écrits.

## Les symboles, un par un

$$
c
$$

Le contexte donné au modèle : prompt système, documents récupérés, historique, résultats d'outils. C'est du texte déjà tokenisé, fixé avant la génération ; le programme ne le représente pas, il travaille directement sur les probabilités qu'il induit.

$$
x_t
$$

Le token écrit à l'étape t, un élément du vocabulaire |V| (de l'ordre de 100 000 tokens pour un LLM, leçon section 1). Dans le programme, les tokens des arbres de décodage sont des chaînes comme `"fiche_bien"`.

$$
x_{<t}
$$

Tous les tokens déjà écrits avant t, c'est-à-dire x₁ … xₜ₋₁ ; pour t = 1, cette suite est vide. Dans les fonctions `glouton` et `faisceau`, c'est le tuple `prefixe`.

$$
x_{1:n}
$$

La séquence complète des n tokens écrits, de x₁ à xₙ.

$$
n
$$

La longueur de la séquence en tokens, un entier ≥ 1 ; elle dépend du tokenizer. Variable `len(probas)`.

$$
P(x_t \mid x_{<t}, c)
$$

La probabilité conditionnelle que le modèle donne au token xₜ, sachant tout ce qui précède : un réel de ]0 ; 1], sortie d'une softmax (leçon, section 2). Chaque élément de la liste `probas`.

$$
\prod_{t=1}^{n}
$$

Le produit des n facteurs, de t = 1 à t = n. Fonction `vraisemblance(probas)`, qui appelle `math.prod`.

$$
\ln P(x_{1:n} \mid c)
$$

La log-vraisemblance de la séquence, un réel ≤ 0, en nats. Fonction `log_vraisemblance(probas)` ; sa moyenne par token est `moyenne_log(probas)`.

## Le mécanisme, avant les preuves

Ce qui entre : le contexte c et la suite de tokens que le modèle a écrits. À chaque pas t, le modèle produit une distribution sur tout le vocabulaire, conditionnée par c et par les tokens déjà écrits, et on lit la probabilité du token réellement choisi. Le produit enchaîne ces probabilités : chaque facteur est au plus 1, donc chaque token ajouté ne peut que garder ou réduire la probabilité de la séquence. Le conditionnement est la partie importante : le facteur du pas t dépend de tous les tokens d'avant, si bien qu'un token écrit tôt change tous les facteurs suivants ; c'est pourquoi une erreur au début d'une réponse se propage. Pourquoi un produit plutôt qu'une somme ? Parce que « écrire x₁ puis x₂ » est l'intersection de deux événements, et que la probabilité d'une intersection est un produit (démonstration 1). Pourquoi passer au logarithme ? Parce qu'un produit de centaines de facteurs plus petits que 1 devient trop petit pour un nombre flottant, alors qu'une somme de logarithmes reste un nombre ordinaire (démonstration 5), et parce qu'une somme se dérive terme à terme pour l'entraînement. Pourquoi diviser par n, enfin, pour comparer deux réponses ? Parce que le produit brut favorise toujours la réponse la plus courte (démonstration 3). Ce qui sort : un nombre entre 0 et 1, ou son logarithme, qui dit à quel point le modèle trouvait cette séquence plausible ; pas si elle est vraie.

Le petit film chiffré : trois tokens de probabilités conditionnelles 0,9 ; 0,5 ; 0,8.

| Après le token | Produit | Somme des logarithmes |
|---|---|---|
| 1 (0,9) | 0,9 | −0,10536 |
| 2 (0,5) | 0,9 × 0,5 = 0,45 | −0,10536 − 0,69315 = −0,79851 |
| 3 (0,8) | 0,45 × 0,8 = 0,36 | −0,79851 − 0,22314 = −1,02165 |

L'exponentielle de la dernière somme, e^(−1,02165), redonne 0,36. Le produit ne fait que baisser ; la somme des logarithmes ne fait que descendre ; et c'est le token à 0,5 qui coûte le plus. Pour un développeur Java, c'est un `reduce` : `probas.stream().reduce(1.0, (a, b) -> a * b)` pour le produit, ou une somme de `Math.log` pour la version qui ne sous-déborde pas.

## Démonstration 1 — La règle de la chaîne des probabilités

**Ce qu'on démontre.** Pour toute séquence x₁ … xₙ telle que chaque préfixe a une probabilité non nulle sachant c :

$$
P(x_{1:n} \mid c) = \prod_{t=1}^{n} P(x_t \mid x_{<t}, c)
$$

Aucune hypothèse d'indépendance n'est nécessaire.

**L'idée.** La probabilité conditionnelle est définie par P(B | A) = P(A ∩ B) / P(A). En la retournant, la probabilité de « A puis B » vaut P(A) × P(B | A) ; on répète ce découpage token après token.

**La preuve, pas à pas.**

**Étape 1.** Par définition de la probabilité conditionnelle, P(A ∩ B) = P(A) × P(B | A) dès que P(A) > 0. Avec A = « le premier token est x₁ » et B = « le second est x₂ », tout étant conditionné par c :

$$
P(x_1, x_2 \mid c) = P(x_1 \mid c) \times P(x_2 \mid x_1, c)
$$

**Étape 2.** On suppose la formule vraie pour t − 1 tokens (hypothèse de récurrence). On applique la même définition avec A = « les t − 1 premiers tokens sont x₁ … xₜ₋₁ » et B = « le token t est xₜ » :

$$
P(x_{1:t} \mid c) = P(x_{1:t-1} \mid c) \times P(x_t \mid x_{<t}, c)
$$

**Étape 3.** On remplace P(x₁:ₜ₋₁ | c) par le produit des t − 1 premiers facteurs, grâce à l'hypothèse de récurrence ; on obtient le produit des t premiers facteurs. La formule est vraie pour t = 1 (un seul facteur), donc pour tout n. ∎

**Vérification chiffrée.** Une loi jointe sur deux tokens : P(a, x) = 0,54 ; P(a, y) = 0,06 ; P(b, x) = 0,12 ; P(b, y) = 0,28. Alors P(a) = 0,54 + 0,06 = 0,6 et P(x | a) = 0,54 / 0,6 = 0,9, d'où P(a) × P(x | a) = 0,6 × 0,9 = 0,54 = P(a, x). Contre-exemple quand on remplace le conditionnement par une indépendance supposée : P(x) = 0,54 + 0,12 = 0,66, et P(a) × P(x) = 0,6 × 0,66 = 0,396, faux de 0,144.

**Ce que la preuve révèle du mécanisme.** Chaque facteur porte toute l'histoire : P(xₜ | x₍<ₜ₎, c) change dès qu'un token précédent change. Un modèle autorégressif n'a jamais besoin de supposer que les tokens sont indépendants ; il a besoin, en revanche, de recalculer chaque facteur avec le bon passé, ce que fait le masque causal de l'attention (fiche 05, démonstration 6).

**Conséquence pour un agent.** Une erreur au début d'une réponse (un mauvais nom de fonction, un mauvais montant) conditionne tout ce qui suit : le modèle écrit ensuite une suite cohérente avec son erreur. D'où l'intérêt de valider tôt (schéma, outil) plutôt que de corriger à la fin.

## Démonstration 2 — Passer aux logarithmes

**Ce qu'on démontre.** Si chaque facteur est dans ]0 ; 1], alors

$$
\ln P(x_{1:n} \mid c) = \sum_{t=1}^{n} \ln P(x_t \mid x_{<t}, c) \le 0
$$

**L'idée.** Le logarithme change les produits en sommes ; et le logarithme d'un nombre de ]0 ; 1] est négatif ou nul.

**La preuve, pas à pas.**

**Étape 1.** Pour deux réels a, b > 0, ln(a × b) = ln a + ln b, par la propriété fondamentale du logarithme. Par récurrence sur le nombre de facteurs, le logarithme d'un produit de n facteurs positifs est la somme de leurs logarithmes.

**Étape 2.** On applique ce résultat au produit de la règle de la chaîne, ce qui est permis parce que chaque facteur est strictement positif.

**Étape 3.** Chaque facteur est au plus 1, donc chaque logarithme est au plus ln 1 = 0, parce que ln est croissante ; une somme de nombres ≤ 0 est ≤ 0. ∎

**Vérification chiffrée.** Pour 0,9 ; 0,8 ; 0,7 : le produit vaut 0,504 et ln 0,9 + ln 0,8 + ln 0,7 ≈ −0,68518 (les trois termes valent environ −0,10536, −0,22314 et −0,35667), dont l'exponentielle redonne 0,504.

**Ce que la preuve révèle du mécanisme.** En échelle logarithmique, chaque token apporte une contribution additive, sa « surprise » −ln p (fiche 06) : la log-vraisemblance d'une phrase est l'opposé de la somme des pertes d'entropie croisée de ses tokens.

**Conséquence pour un agent.** Les API qui exposent des « logprobs » donnent directement ces termes : pour noter une réponse, on les additionne, on ne les multiplie jamais. Le programme refuse une probabilité nulle (`ValueError`), dont le logarithme serait −∞.

## Démonstration 3 — Une séquence plus longue est toujours moins probable

**Ce qu'on démontre.** Pour toute séquence et tout token ajouté :

$$
P(x_{1:n+1} \mid c) = P(x_{1:n} \mid c) \times P(x_{n+1} \mid x_{1:n}, c) \le P(x_{1:n} \mid c)
$$

**L'idée.** Ajouter un token multiplie la probabilité par un nombre au plus égal à 1 : elle ne peut pas monter.

**La preuve, pas à pas.**

**Étape 1.** La règle de la chaîne (démonstration 1) écrit la séquence allongée comme la séquence d'origine fois un facteur.

**Étape 2.** Ce facteur est une probabilité, donc ≤ 1 ; multiplier un nombre positif par un nombre ≤ 1 ne l'augmente pas. ∎

**Vérification chiffrée.** 0,9 × 0,8 = 0,72 ; avec un troisième token à 0,7, on tombe à 0,504 ; même un quatrième token très sûr, à 0,99, fait encore baisser : 0,504 × 0,99 = 0,49896. Conséquence chiffrée : un appel d'outil A de 5 tokens bien sûrs (0,95 ; 0,9 ; 0,85 ; 0,9 ; 0,8) a une probabilité brute de 0,52326, à peine au-dessus d'un appel B de 3 tokens (0,95 ; 0,6 ; 0,9) qui vaut 0,513, alors que B contient un token douteux (cas 1).

**Ce que la preuve révèle du mécanisme.** La probabilité brute mélange deux choses : la confiance par token et la longueur. Pour comparer deux réponses de longueurs différentes, il faut séparer les deux : on divise la log-vraisemblance par n, ce qui donne la moyenne par token (démonstration 6).

**Conséquence pour un agent.** Un agent qui choisirait entre plusieurs réponses candidates par probabilité brute préférerait systématiquement les plus courtes, y compris des réponses tronquées. On note donc par la moyenne par token, ou avec une pénalité de longueur réglée (cas 3).

## Démonstration 4 — Choisir le meilleur token à chaque pas ne donne pas la meilleure phrase

**Ce qu'on démontre.** Le décodage glouton, qui choisit à chaque pas le token le plus probable, ne trouve pas toujours la séquence la plus probable. Il suffit d'un contre-exemple :

$$
P(a, \cdot) = 0{,}6 \times 0{,}4 = 0{,}24 \;<\; P(b, \cdot) = 0{,}4 \times 0{,}9 = 0{,}36
$$

**L'idée.** Le glouton juge le premier token sur sa seule probabilité, sans regarder ce qu'il rend possible ensuite ; un premier token un peu moins probable peut ouvrir une suite beaucoup plus sûre.

**La preuve, pas à pas.**

**Étape 1.** Premier token : a a la probabilité 0,6 et b la probabilité 0,4 ; le glouton choisit a, parce que 0,6 > 0,4.

**Étape 2.** Après a, la meilleure suite a la probabilité 0,4 ; la règle de la chaîne donne 0,6 × 0,4 = 0,24 pour la séquence gloutonne.

**Étape 3.** Après b, la meilleure suite a la probabilité 0,9 ; la séquence vaut 0,4 × 0,9 = 0,36 > 0,24. Le glouton a donc manqué une séquence 0,36 / 0,24 = 1,5 fois plus probable. ∎

**Vérification chiffrée.** Le programme compare `0.6 * 0.4` et `0.4 * 0.9` et vérifie le rapport 1,5. Les fonctions `glouton` et `faisceau` retrouvent le même phénomène sur l'arbre du cas 2 : le glouton obtient 0,24, la recherche en faisceau de largeur 2 trouve 0,36.

**Ce que la preuve révèle du mécanisme.** Le glouton maximise chaque facteur séparément, alors que la formule demande de maximiser leur produit ; les deux coïncident seulement si le premier choix ne change pas la qualité des suites. La limite T → 0 de la leçon (section 4) donne l'argmax de chaque pas, c'est-à-dire exactement le glouton, et non l'argmax de la phrase entière : baisser la température ne corrige pas ce défaut.

**Conséquence pour un agent.** Pour un appel d'outil court et très contraint, le glouton suffit ; pour un plan en plusieurs étapes, garder plusieurs débuts candidats (recherche en faisceau, plusieurs tirages notés) coûte quelques appels de plus et peut trouver un plan nettement plus probable (cas 2).

## Démonstration 5 — Le zéro machine : le produit direct s'effondre, la somme des logarithmes non

**Ce qu'on démontre.** En double précision IEEE 754, le plus petit nombre positif représentable est 2⁻¹⁰⁷⁴ ≈ 4,94 × 10⁻³²⁴. Donc le produit de n facteurs égaux à 0,5 vaut exactement 2⁻ⁿ pour n ≤ 1 074 et s'arrondit à 0 dès n = 1 075, alors que sa log-vraisemblance reste un nombre ordinaire :

$$
0{,}5^{1075} \;\longrightarrow\; 0 \text{ en flottant}, \qquad 1075 \times \ln 0{,}5 \approx -745{,}13
$$

**L'idée.** Un flottant stocke un exposant borné : en dessous d'un certain seuil, il n'existe plus de nombre à représenter. Le logarithme, lui, transforme un nombre minuscule en un nombre négatif de taille modeste, loin de toute limite.

**La preuve, pas à pas.**

**Étape 1.** 0,5ⁿ = 2⁻ⁿ, parce que 0,5 = 2⁻¹ ; ces nombres sont des puissances de 2, donc exactement représentables tant que leur exposant n'est pas trop petit.

**Étape 2.** Les nombres dénormalisés de la double précision descendent jusqu'à 2⁻¹⁰⁷⁴, le plus petit nombre positif ; donc 2⁻ⁿ est représentable exactement pour n ≤ 1 074.

**Étape 3.** 2⁻¹⁰⁷⁵ est exactement à mi-chemin entre 0 et 2⁻¹⁰⁷⁴ ; l'arrondi au plus proche, à égalité vers le pair, choisit 0, parce que 0 a une mantisse paire. Au-delà, 2⁻ⁿ est encore plus près de 0. Le produit vaut donc 0 dès n = 1 075.

**Étape 4.** La somme des logarithmes vaut n × ln 0,5 = −0,69315 n : pour n = 1 075, environ −745,13, un nombre parfaitement représentable. ∎

**Vérification chiffrée.** Le programme trouve que 0,5¹⁰⁷⁴ ≈ 4,94 × 10⁻³²⁴ et que 0,5¹⁰⁷⁵ vaut 0.0, avec 1 075 comme premier n nul. Une réponse de 1 000 tokens à 0,5 a une probabilité de 0,5¹⁰⁰⁰ ≈ 9,3 × 10⁻³⁰², encore représentable ; à 2 000 tokens, le produit en flottants vaut exactement 0, alors que la somme des logarithmes vaut −1 386,29.

**Ce que la preuve révèle du mécanisme.** La probabilité d'un texte long n'est pas « petite », elle est astronomiquement petite : ce n'est pas un défaut du modèle, c'est la règle de la chaîne. Seule l'échelle logarithmique la rend manipulable. Le cas 3 montre un piège de plus : avec des facteurs qui ne sont pas des puissances de 2, le produit peut rester bloqué sur 4,94 × 10⁻³²⁴ au lieu de tomber à 0, et donner un nombre faux sans aucune erreur.

**Conséquence pour un agent.** Tout code qui note des réponses doit additionner des logprobs ; un test unitaire avec une réponse de 2 000 tokens attrape la version qui multiplie.

## Démonstration 6 — Le token le plus faible plafonne la séquence, et la moyenne par token donne la perplexité

**Ce qu'on démontre.** Pour toute séquence :

$$
P(x_{1:n} \mid c) \le \min_t P(x_t \mid x_{<t}, c), \qquad \exp\Big( \frac{1}{n} \sum_{t=1}^{n} \ln P(x_t \mid x_{<t}, c) \Big) = P(x_{1:n} \mid c)^{1/n} = \frac{1}{\operatorname{PPL}}
$$

et si un facteur est multiplié par (1 − ε), la moyenne des logarithmes baisse de exactement −ln(1 − ε) / n.

**L'idée.** Dans un produit de facteurs ≤ 1, chacun des autres facteurs ne peut que baisser le résultat : il ne dépasse donc jamais le plus petit facteur. La moyenne des logarithmes est le logarithme de la moyenne géométrique, et la perplexité de la fiche 32 en est l'inverse.

**La preuve, pas à pas.**

**Étape 1.** On isole le plus petit facteur m ; les autres sont ≤ 1, donc leur produit est ≤ 1, et le produit total est ≤ m × 1 = m.

**Étape 2.** (1/n) ∑ ln pₜ = (1/n) ln ∏ pₜ = ln((∏ pₜ)^(1/n)), parce que le logarithme change le produit en somme et le facteur 1/n en exposant ; l'exponentielle donne la moyenne géométrique.

**Étape 3.** La perplexité est exp(−(1/n) ∑ ln pₜ) (fiche 32), c'est-à-dire l'inverse de cette moyenne géométrique.

**Étape 4.** Si un facteur devient (1 − ε) pₜ, son logarithme devient ln pₜ + ln(1 − ε), donc la somme gagne ln(1 − ε) et la moyenne ln(1 − ε) / n. ∎

**Vérification chiffrée.** Appel A : le plus petit facteur vaut 0,8 et P = 0,52326 ≤ 0,8 ; appel B : 0,6 et 0,513 ≤ 0,6. Moyennes géométriques : e^(−0,12954) ≈ 0,87850 et e^(−0,22249) ≈ 0,80052 ; perplexités 1 / 0,87850 ≈ 1,13830 et 1 / 0,80052 ≈ 1,24919. Si le dernier token de A baisse de 1 %, la moyenne des logarithmes de A baisse de ln(0,99) / 5 ≈ −0,00201.

**Ce que la preuve révèle du mécanisme.** Un seul token douteux plafonne toute la séquence, quelle que soit la sûreté des autres : B ne peut pas dépasser 0,6. La moyenne par token, elle, dilue ce token parmi les autres : il faut donc regarder les deux, la moyenne pour comparer, le minimum pour refuser.

**Conséquence pour un agent.** Une bonne règle de production combine les deux lectures : choisir la réponse dont la moyenne par token est la meilleure, et refuser un appel d'outil dont un token d'argument tombe sous un seuil (cas 1).

## Exemple simple, à la main

Dix tokens, chacun de probabilité conditionnelle 0,5. Par la règle de la chaîne, la probabilité de la séquence est le produit des dix facteurs :

$$
0{,}5^{10} = \frac{1}{2^{10}} = \frac{1}{1\,024} \approx 0{,}000977
$$

En logarithme, chaque facteur apporte ln 0,5 ≈ −0,69315, et la somme vaut :

$$
\ln P = 10 \times \ln 0{,}5 \approx 10 \times (-0{,}69315) = -6{,}93147
$$

On vérifie que e^(−6,93147) redonne bien 1 / 1 024. La moyenne par token vaut −0,69315, donc la perplexité vaut e^0,69315 = 2 : le modèle hésitait comme entre deux choix à chaque pas.

## Cas d'usage complexes, démontrés

Les probabilités de tokens, les volumes et les montants de ces cas sont illustratifs ; seules les règles citées (IBAN, indemnité de fin de service, autorités) viennent du guide du cours.

### Cas 1 — Banque de détail à Dubaï : deux appels d'outil de virement générés

**Contexte.** Une banque de détail de Dubaï laisse son assistant préparer des virements, que le client confirme ensuite dans l'application. Pour une demande, le modèle a généré deux appels candidats de l'outil `virement` ; on dispose des probabilités des tokens de chaque appel. A a 5 tokens (fonction, IBAN, montant, devise, motif) ; B en a 3, avec un montant dont le token a été écrit avec hésitation. L'équipe doit choisir quel appel présenter au client, ou n'en présenter aucun. Montant concerné : 12 500 AED (illustratif).

**Données.** Probabilités des tokens de A : 0,95 ; 0,9 ; 0,85 ; 0,9 ; 0,8. Probabilités des tokens de B : 0,95 ; 0,6 ; 0,9. Règle de production (illustrative) : refuser un appel dont un token d'argument est sous 0,7.

**Calcul pas à pas.**

**Étape 1.** Probabilités brutes, par la règle de la chaîne :

$$
P(A) = 0{,}95 \times 0{,}9 \times 0{,}85 \times 0{,}9 \times 0{,}8 \approx 0{,}52326, \qquad P(B) = 0{,}95 \times 0{,}6 \times 0{,}9 = 0{,}513
$$

**Étape 2.** Log-vraisemblances, avec ln 0,95 ≈ −0,05129, ln 0,9 ≈ −0,10536, ln 0,85 ≈ −0,16252, ln 0,8 ≈ −0,22314, ln 0,6 ≈ −0,51083 :

$$
\ln P(A) \approx -0{,}64768, \qquad \ln P(B) \approx -0{,}66748
$$

**Étape 3.** Moyennes par token, puis moyennes géométriques :

$$
\frac{-0{,}64768}{5} \approx -0{,}12954 \;\to\; e^{-0{,}12954} \approx 0{,}87850, \qquad \frac{-0{,}66748}{3} \approx -0{,}22249 \;\to\; e^{-0{,}22249} \approx 0{,}80052
$$

**Étape 4.** Règle du token minimal : le plus petit token de A vaut 0,8 ≥ 0,7 ; celui de B vaut 0,6 < 0,7.

**Décision de l'agent.** L'agent présente A au client : sa moyenne par token est la meilleure (−0,12954 > −0,22249) et aucun de ses tokens n'est sous 0,7. B est écarté, parce que son token à 0,6 porte sur le montant ; si A n'existait pas, l'agent reposerait la question au client au lieu de préparer un virement douteux.

**Contre-calcul.** Avec la probabilité brute, A ne gagne que de peu (0,52326 contre 0,513), et il suffit que A soit plus long pour perdre : avec trois tokens de plus à 0,9 (un motif plus détaillé), P(A) tombe à 0,52326 × 0,9³ = 0,52326 × 0,729 ≈ 0,38146 < 0,513, alors que sa moyenne par token reste bien meilleure (−0,12047). Un agent qui choisirait au produit brut présenterait B, l'appel au montant douteux ; si le client confirme sans relire, la banque doit ensuite traiter un virement erroné de 12 500 AED.

**Sensibilité.** La valeur de bascule est la probabilité q du token douteux de B pour laquelle B égale A par token : il faut ln 0,95 + ln q + ln 0,9 = 3 × (−0,12954) ≈ −0,38861, donc ln q ≈ −0,38861 + 0,05129 + 0,10536 = −0,23196 et q = e^(−0,23196) ≈ 0,79298. Sous 0,79298, A reste meilleur par token ; et entre 0,7 et 0,79298, B passerait la règle du token minimal sans gagner la comparaison.

**En production.** L'indicateur suivi est la part des appels d'outil refusés par la règle du token minimal, et parmi les appels présentés, la part que les clients corrigent avant confirmation (alerte si elle dépasse 1 %, seuil illustratif). Quelle que soit la probabilité, l'outil vérifie lui-même l'IBAN : 23 caractères commençant par AE et contrôle mod 97 = 1 (par exemple `AE07 0331 2345 6789 0123 456`) ; la probabilité d'un token ne remplace jamais cette validation. Les obligations de la banque envers ses clients relèvent de la CBUAE et sont à confirmer avec le texte en vigueur.

### Cas 2 — Agence immobilière à Dubaï : planifier une estimation en deux appels d'outil

**Contexte.** Une agence et un promoteur actifs à Dubaï et Abu Dhabi utilisent un agent qui estime le prix d'un appartement avant de rédiger une offre. L'agent planifie deux appels d'outil ; le modèle donne, pour chaque pas, une probabilité à chaque outil possible. L'équipe compare le décodage glouton (un appel au modèle par pas) et une recherche en faisceau de largeur 2 (plusieurs débuts gardés). Les probabilités sont illustratives.

**Données.** Premier pas : `transactions_DLD` 0,6 ; `fiche_bien` 0,4. Après `transactions_DLD` : `estimer` 0,4 ; `tendance` 0,35 ; `photos` 0,25. Après `fiche_bien` : `comparer_5_ventes` 0,9 ; `estimer` 0,1. Coût : un appel au modèle par préfixe développé.

**Calcul pas à pas.**

**Étape 1.** Glouton : `transactions_DLD` (0,6 > 0,4), puis `estimer` (0,4, le plus probable après lui). Probabilité du plan et appels :

$$
P_{\text{glouton}} = 0{,}6 \times 0{,}4 = 0{,}24, \qquad \ln 0{,}24 \approx -1{,}42712, \qquad 2 \text{ appels}
$$

**Étape 2.** Faisceau de largeur 2 : on garde les deux débuts, puis on développe chacun : 0,6 × 0,4 = 0,24 ; 0,6 × 0,35 = 0,21 ; 0,6 × 0,25 = 0,15 ; 0,4 × 0,9 = 0,36 ; 0,4 × 0,1 = 0,04. Le meilleur plan est `fiche_bien` puis `comparer_5_ventes` :

$$
P_{\text{faisceau}} = 0{,}4 \times 0{,}9 = 0{,}36, \qquad \ln 0{,}36 \approx -1{,}02165, \qquad 1 + 2 = 3 \text{ appels}
$$

**Étape 3.** Rapport des deux plans : 0,36 / 0,24 = 1,5, pour 3 / 2 = 1,5 fois plus d'appels au modèle.

**Décision de l'agent.** L'agent planifie par faisceau de largeur 2 : un appel de plus au modèle (latence et coût de planification multipliés par 1,5) donne un plan 1,5 fois plus probable, qui part de la fiche du bien et compare cinq ventes enregistrées au DLD au lieu d'estimer directement à partir de transactions brutes.

**Contre-calcul.** Le glouton exécute `transactions_DLD` puis `estimer`, un plan de probabilité 0,24 seulement : l'estimation s'appuie sur des transactions du quartier non triées (autres tours, autres étages), et une estimation éloignée du marché coûte une offre refusée ou un mandat perdu. Les frais de transfert DLD de 4 % de la valeur du bien s'ajoutent de toute façon au budget de l'acheteur : une estimation fausse fausse aussi ce montant.

**Sensibilité.** Notons π la probabilité du premier outil `transactions_DLD`. Le glouton le choisit dès que π > 0,5, mais il n'est le meilleur choix que si 0,4 π ≥ 0,9 (1 − π), c'est-à-dire π ≥ 0,9 / 1,3 ≈ 0,69231 : entre 0,5 et 0,69231, le glouton se trompe. De même, la suite après `transactions_DLD` devrait atteindre 0,36 / 0,6 = 0,6 pour égaler le faisceau. Si la suite après `fiche_bien` baisse de 10 % (0,81), le faisceau trouve encore 0,4 × 0,81 = 0,324 > 0,24 : la décision tient.

**En production.** On suit la part des demandes où le plan du faisceau diffère du plan glouton, et l'écart médian entre l'estimation de l'agent et le prix final des transactions conclues (prix en AED/sqft), revu chaque mois. Les données de transactions viennent du DLD ; leur usage et leur mise à jour sont à confirmer avec les conditions en vigueur.

### Cas 3 — Plateforme d'actifs virtuels agréée VARA : choisir entre trois rapports d'incident

**Contexte.** Une plateforme d'actifs virtuels agréée par la VARA fait rédiger par son agent un rapport d'incident de liquidité pour l'équipe de conformité. Le modèle a produit trois rapports candidats de longueurs très différentes, et l'agent doit en retenir un en le notant par sa log-vraisemblance. Les longueurs et les moyennes sont illustratives.

**Données.** R1 : 300 tokens, moyenne des logarithmes −0,25 par token. R2 : 450 tokens, moyenne −0,20. R3 : 1 200 tokens, moyenne −0,65. Pénalité de longueur classique : score = (somme des logarithmes) / n^α, avec α entre 0 (somme brute) et 1 (moyenne par token).

**Calcul pas à pas.**

**Étape 1.** Sommes des logarithmes, n × moyenne :

$$
300 \times (-0{,}25) = -75, \qquad 450 \times (-0{,}20) = -90, \qquad 1\,200 \times (-0{,}65) = -780
$$

**Étape 2.** Produits calculés directement en flottants : R1 ≈ 2,679 × 10⁻³³ et R2 ≈ 8,194 × 10⁻⁴⁰, encore représentables ; R3 donne 4,94 × 10⁻³²⁴, le plus petit flottant positif, alors que sa vraie valeur est e^(−780) ≈ 10^(−338,75) ≈ 1,78 × 10⁻³³⁹. Le produit s'est bloqué sur le plus petit dénormalisé, parce que chaque multiplication par e^(−0,65) ≈ 0,522 s'y arrondit de nouveau.

**Étape 3.** Classement : par la somme (α = 0), R1 gagne (−75 > −90) ; par la moyenne (α = 1), R2 gagne (−0,20 > −0,25). Valeur de bascule entre R1 et R2 : −75 / 300^α = −90 / 450^α, soit (450 / 300)^α = 90 / 75, donc

$$
\alpha^{*} = \frac{\ln 1{,}2}{\ln 1{,}5} \approx 0{,}44966
$$

**Décision de l'agent.** L'agent note les rapports par la moyenne des logarithmes par token (α = 1) et retient R2 ; R3, très long et moins sûr par token, est écarté. Le produit direct n'est jamais utilisé.

**Contre-calcul.** La somme brute choisit R1 parce qu'il est court, pas parce qu'il est meilleur : R1 est moins sûr par token que R2. Le produit direct est pire encore : il attribue à R3 une « probabilité » environ 2,8 × 10¹⁵ fois trop grande (4,94 × 10⁻³²⁴ au lieu d'environ 1,78 × 10⁻³³⁹, soit un écart de 15,44 en puissances de 10), sans aucune erreur ni avertissement, et un code qui comparerait des produits trouverait des égalités fictives dès que plusieurs rapports touchent ce plancher. Un rapport de conformité mal choisi oblige l'équipe à le réécrire, sous la contrainte de délai de la procédure interne.

**Sensibilité.** Toute pénalité α au-dessus de 0,44966 donne R2, toute pénalité en dessous donne R1 : la décision dépend donc d'un réglage qu'il faut fixer et documenter. Si la moyenne de R1 s'améliorait de 0,25 à 0,20, R1 et R2 auraient la même qualité par token et la somme favoriserait toujours R1, le plus court.

**En production.** On suit la part des rapports retenus que l'équipe de conformité réécrit, et la longueur moyenne des rapports retenus (une baisse brutale signale une préférence pour les rapports courts). Les obligations de déclaration d'une plateforme agréée par la VARA sont à confirmer avec le texte en vigueur ; l'agent prépare un brouillon, un humain signe.

### Cas 4 — Cabinet RH multi-émirats : une phrase d'indemnité de fin de service

**Contexte.** Un cabinet RH multi-émirats laisse son agent expliquer aux salariés du secteur privé le calcul de leur indemnité de fin de service. Pour un salarié de 3 ans d'ancienneté au salaire de base de 9 000 AED, le modèle hésite au premier token entre « 21 » et « 30 » jours par année. La règle du guide : 21 jours de salaire de base par année pour les 5 premières années, salaire journalier = base / 30. Le cabinet traite environ 250 dossiers de ce type par an (illustratif).

**Données.** Phrase juste (« 21 jours … ») : probabilités 0,55 ; 0,9 ; 0,95. Phrase fausse (« 30 jours … ») : 0,45 ; 0,92 ; 0,97. Salaire de base : 9 000 AED. Ancienneté : 3 ans. Volume : 250 dossiers par an.

**Calcul pas à pas.**

**Étape 1.** Probabilités des deux phrases, par la règle de la chaîne :

$$
P(\text{juste}) = 0{,}55 \times 0{,}9 \times 0{,}95 \approx 0{,}47025, \qquad P(\text{fausse}) = 0{,}45 \times 0{,}92 \times 0{,}97 \approx 0{,}40158
$$

Parmi ces deux phrases, la fausse représente 0,40158 / (0,47025 + 0,40158) ≈ 0,46062 de la masse.

**Étape 2.** Montants : salaire journalier 9 000 / 30 = 300 AED ; indemnité due 300 × 21 × 3 = 18 900 AED ; indemnité de la phrase fausse 300 × 30 × 3 = 27 000 AED ; écart 8 100 AED.

**Étape 3.** En tirage à température 1, la phrase fausse sort avec la probabilité 0,40158 : le surcoût moyen annoncé vaut 0,40158 × 8 100 ≈ 3 252,80 AED par réponse, et sur 250 dossiers environ 0,40158 × 250 ≈ 100,4 réponses fausses.

**Décision de l'agent.** Le nombre de jours et le montant ne sont jamais générés par le modèle : un outil `indemnite_fin_service(base, annees)` applique la règle (21 jours par an les 5 premières années, au prorata, plafond de 24 mois de salaire de base) et renvoie 18 900 AED ; le modèle rédige seulement l'explication autour de ce résultat.

**Contre-calcul.** Le décodage glouton choisirait ici « 21 » (0,55 > 0,45) et produirait la phrase juste ; un développeur pourrait en conclure que le problème est réglé. Mais le glouton ne protège que tant que le premier facteur reste au-dessus de 0,5, et le tirage, utilisé par défaut dans beaucoup d'assistants conversationnels, sort la phrase fausse quatre fois sur dix. Annoncer 27 000 AED au lieu de 18 900 AED crée une attente que l'employeur ne paiera pas, et un litige possible devant le MOHRE.

**Sensibilité.** La valeur de bascule du glouton est P(« 21 ») = 0,5. Une baisse de 10 % de ce premier facteur, de 0,55 à 0,495, suffit à faire basculer le glouton sur « 30 jours » : une légère dérive du modèle ou du prompt change la réponse affichée. C'est l'argument chiffré pour sortir le calcul du modèle.

**En production.** L'indicateur suivi est le nombre de réponses où le montant écrit diffère de celui de l'outil (objectif : zéro), contrôlé automatiquement sur chaque réponse. Le régime cité est celui du secteur privé (décret-loi fédéral 33/2021) ; les ressortissants émiriens relèvent de la GPSSA et le DIFC a son propre régime : l'outil vérifie le régime applicable avant de calculer, et les cas particuliers sont à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Trois tokens de probabilités 0,5 ; 0,8 ; 0,25. Calculer la probabilité de la séquence et son logarithme.

**Exercice 2.** Écrire la règle de la chaîne pour quatre tokens.

**Exercice 3.** Une phrase de 6 tokens à 0,9 et une phrase de 3 tokens à 0,7. Laquelle est la plus probable ? Laquelle est la plus sûre par token ?

**Exercice 4.** Construire un autre contre-exemple au décodage glouton, avec trois choix au premier token.

**Exercice 5.** Combien de tokens à 0,5 faut-il pour descendre sous 10⁻⁶ ? (log₂ 10⁶ ≈ 19,93.)

**Exercice 6 (cas modifié).** Dans le cas 1, le token douteux de B monte de 0,6 à 0,75. Recalculer la log-vraisemblance de B, sa moyenne par token, et dire quel appel l'agent présente.

**Exercice 7 (trouver l'erreur).** Un collègue écrit : « Avec la loi jointe de la démonstration 1, P(a, x) = P(a) × P(x) = 0,6 × 0,66. » Trouver l'erreur et la chiffrer.

**Exercice 8 (redémontrer de mémoire).** Redémontrer, sans regarder, la règle de la chaîne par récurrence, en citant à chaque étape la définition utilisée.

## Corrigé

**Exercice 1.** Produit : 0,5 × 0,8 = 0,4, puis 0,4 × 0,25 = 0,1. Logarithme : ln 0,1 ≈ −2,303, qu'on retrouve aussi par ln 0,5 + ln 0,8 + ln 0,25 ≈ −0,69315 − 0,22314 − 1,38629 = −2,30258.

**Exercice 2.** On applique la définition P(A ∩ B) = P(A) P(B | A) trois fois : P(x₁, x₂, x₃, x₄ | c) = P(x₁ | c) × P(x₂ | x₁, c) × P(x₃ | x₁, x₂, c) × P(x₄ | x₁, x₂, x₃, c).

**Exercice 3.** 0,9⁶ = 0,81 × 0,81 × 0,81 = 0,531441 et 0,7³ = 0,343 : la première est plus probable malgré sa longueur double, et aussi plus sûre par token (0,9 contre 0,7, soit des moyennes de logarithmes −0,10536 et −0,35667).

**Exercice 4.** Par exemple a (0,5) puis au mieux 0,3 ; b (0,3) puis au mieux 0,95 ; c (0,2) puis au mieux 0,5. Glouton : a, soit 0,5 × 0,3 = 0,15. Meilleur : b, soit 0,3 × 0,95 = 0,285 ; c donne 0,2 × 0,5 = 0,1.

**Exercice 5.** 0,5ⁿ < 10⁻⁶ équivaut à 2ⁿ > 10⁶, soit n > log₂ 10⁶ ≈ 19,93 ; le plus petit entier est 20 tokens.

**Exercice 6.** ln 0,95 + ln 0,75 + ln 0,9 ≈ −0,05129 − 0,28768 − 0,10536 = −0,44434 (le programme garde les décimales suivantes) ; moyenne −0,44434 / 3 ≈ −0,14811. B passe désormais la règle du token minimal (0,75 ≥ 0,7), mais sa moyenne reste sous celle de A (−0,14811 < −0,12954), puisque 0,75 est sous la bascule 0,79298. L'agent présente toujours A.

**Exercice 7.** L'erreur : P(a) × P(x) suppose l'indépendance des deux tokens, alors que la règle de la chaîne demande P(x | a). Valeur fausse : 0,6 × 0,66 = 0,396. Valeur juste : P(a) × P(x | a) = 0,6 × (0,54 / 0,6) = 0,6 × 0,9 = 0,54. L'écart vaut 0,144 : le second token dépend fortement du premier.

**Exercice 8.** Étape 1 (cas n = 1) : P(x₁ | c) est un produit d'un seul facteur. Étape 2 (hérédité) : on suppose P(x₁:ₜ₋₁ | c) = ∏ₛ₌₁ᵗ⁻¹ P(xₛ | x₍<ₛ₎, c). Étape 3 : par définition de la probabilité conditionnelle, P(x₁:ₜ | c) = P(x₁:ₜ₋₁ | c) × P(xₜ | x₁:ₜ₋₁, c). Étape 4 : on remplace le premier facteur par l'hypothèse de récurrence, ce qui donne le produit des t facteurs. ∎ Aucune indépendance n'a été supposée.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`vraisemblance(probas)`** — Cette fonction est le notaire naïf qui multiplie, sans se méfier, toutes les probabilités conditionnelles d'une phrase : elle reçoit la liste des P(xₜ | x₍<ₜ₎, c) token après token et renvoie leur produit, calculé par `math.prod`, c'est-à-dire la vraisemblance exacte de la séquence selon la règle de la chaîne. Le résultat est juste en mathématiques, 0,36 pour (0,9 ; 0,5 ; 0,8), mais fragile en nombres flottants : pour 2 000 tokens de probabilité 0,5, il tombe à 0,0, et le programme s'en sert précisément pour montrer ce zéro machine et pour comparer les phrases courtes des cas.

**`log_vraisemblance(probas)`** — Celle-ci est le comptable prudent qui, au lieu de multiplier des nombres de plus en plus petits, additionne leurs logarithmes : elle reçoit la même liste de probabilités, vérifie que chacune est strictement positive et au plus égale à 1, sinon elle lève une `ValueError`, puis elle renvoie la somme des ln P(xₜ | x₍<ₜ₎, c). On obtient ainsi −1,02165 pour le film (0,9 ; 0,5 ; 0,8), dont l'exponentielle redonne 0,36, et −1 386,29 pour 2 000 tokens à 0,5, là où le produit direct s'effondre à zéro ; c'est la mesure stable sur laquelle reposent `moyenne_log` et les comparaisons des cas.

**`moyenne_log(probas)`** — Cette fonction fait le travail d'un arbitre qui veut comparer des coureurs ayant parcouru des distances différentes : elle reçoit une liste de probabilités, renvoie `None` si elle est vide, puisqu'une moyenne sur zéro token n'a pas de sens, et sinon divise la log-vraisemblance de `log_vraisemblance` par le nombre de tokens. Elle renvoie la log-vraisemblance moyenne par token, −0,12954 pour l'appel d'outil A du cas 1 contre −0,22249 pour B, dont l'exponentielle est la moyenne géométrique des probabilités et l'inverse de cette exponentielle la perplexité ; elle permet de juger une réponse sans pénaliser sa seule longueur.

**`glouton(arbre, prefixe)`** — On peut se figurer un promeneur pressé qui, à chaque carrefour, prend la route la plus fréquentée sans regarder plus loin : la fonction reçoit un arbre, dictionnaire qui associe à chaque préfixe (un tuple de tokens) les probabilités de ses suites possibles, et un préfixe de départ, vide par défaut. Tant que le préfixe courant figure dans l'arbre, elle compte un appel au modèle, choisit le token de plus forte probabilité, l'ajoute au préfixe et multiplie la probabilité accumulée ; elle renvoie le triplet (séquence, probabilité, appels), par exemple une séquence de probabilité 0,24 en 2 appels dans le cas 2, ce qui illustre la démonstration 4 : le choix localement le meilleur ne donne pas toujours la meilleure séquence.

**`faisceau(arbre, largeur)`** — Cette fonction remplace le promeneur pressé par une petite équipe d'éclaireurs qui explorent plusieurs chemins à la fois : elle part du seul préfixe vide de probabilité 1 et, tant qu'au moins un candidat peut encore être prolongé, elle garde tels quels les candidats terminés, compte un appel au modèle pour chaque candidat prolongeable et le remplace par toutes ses suites, chacune avec la probabilité du préfixe multipliée par celle du token ajouté. Après chaque tour, elle trie les candidats par probabilité décroissante et n'en garde que `largeur` ; elle renvoie la séquence, la probabilité et le nombre d'appels du meilleur survivant, soit 0,36 en 3 appels avec une largeur 2 dans le cas 2, contre 0,24 pour le glouton.

**`r5(xs)`** — Cette petite fonction est le greffier qui recopie les nombres au propre : elle reçoit une liste et renvoie une nouvelle liste où chaque élément est arrondi à cinq décimales. Elle ne calcule rien de nouveau, mais elle permet aux `assert` de `main` de comparer les produits partiels [0,9 ; 0,45 ; 0,36], les logarithmes [−0,10536 ; −0,79851 ; −1,02165] ou les logarithmes des probabilités du cas 1 aux valeurs écrites dans la fiche, sans être gênés par les derniers chiffres flottants.

**`cas_1_appels_outil_banque()`** — Un agent bancaire hésite entre deux appels d'outil de virement, A de cinq tokens (0,95 ; 0,9 ; 0,85 ; 0,9 ; 0,8) et B de trois tokens (0,95 ; 0,6 ; 0,9), où le 0,6 porte sur le montant : la fonction calcule leurs vraisemblances brutes, 0,52326 et 0,513, puis leurs moyennes de logarithmes, −0,12954 et −0,22249, et leurs moyennes géométriques, 0,8785 et 0,80052. Elle montre qu'en allongeant A de trois tokens à 0,9 sa probabilité brute tombe à 0,38146, sous celle de B, alors que sa moyenne reste meilleure, et calcule la bascule 0,79298 que le token faible de B devrait atteindre pour égaler A en moyenne ; elle retient A parce que sa moyenne est meilleure et qu'aucun de ses tokens ne descend sous le seuil 0,7, et renvoie les deux listes, les deux moyennes, la bascule, la version allongée de A et le choix.

**`cas_2_plan_immo()`** — Cette fonction met en scène un agent immobilier qui planifie deux appels d'outils dans un petit arbre de probabilités : le premier pas propose l'outil des transactions avec 0,6 ou la fiche du bien avec 0,4, mais la fiche du bien mène ensuite à la comparaison de cinq ventes avec 0,9. Elle confronte `glouton`, qui prend l'outil des transactions puis l'estimation pour une probabilité de 0,24 en 2 appels, à `faisceau` de largeur 2, qui trouve la fiche du bien suivie de la comparaison pour 0,36 en 3 appels ; elle calcule aussi la probabilité de premier pas, 0,69231, à partir de laquelle le glouton aurait raison, la suite, 0,6, qu'il faudrait après le premier choix glouton pour égaler 0,36, et la variante 0,4 × 0,81 = 0,324, avec une suite moins sûre de 10 %, qui bat encore 0,24. Elle renvoie ces neuf résultats avec la décision « faisceau de largeur 2 », pour un appel de plus et une probabilité multipliée par 1,5.

**`cas_3_rapports_crypto()`** — Un analyste doit choisir parmi trois rapports d'incident générés de longueurs très différentes, R1 de 300 tokens à −0,25 de log-probabilité moyenne, R2 de 450 tokens à −0,20 et R3 de 1 200 tokens à −0,65 : la fonction calcule leurs sommes de logarithmes, −75, −90 et −780, et constate que la somme préfère R1 alors que la moyenne par token préfère R2. Elle refait le produit direct en nombres flottants, qui donne 2,679 × 10⁻³³ pour R1, 8,194 × 10⁻⁴⁰ pour R2 et reste bloqué à 5 × 10⁻³²⁴ pour R3 au lieu de la vraie valeur 10 puissance −338,75, puis calcule l'exposant de pénalité de longueur, α ≈ 0,44966, au-delà duquel R2 l'emporte sur R1 ; elle renvoie les sommes, les produits, les deux choix, α et ce logarithme décimal, et conclut qu'on retient R2 sans jamais se fier au produit.

**`cas_4_fin_de_service_rh()`** — Cette fonction suit un agent des ressources humaines qui doit rédiger la phrase sur l'indemnité de fin de service d'un salarié au salaire de base de 9 000 AED après 3 ans : la phrase juste, « 21 jours », a pour probabilités (0,55 ; 0,9 ; 0,95), la phrase fausse, « 30 jours », (0,45 ; 0,92 ; 0,97). Elle calcule le salaire journalier de 300 AED, l'indemnité due de 18 900 AED contre 27 000 AED pour la phrase fausse, les vraisemblances 0,47025 et 0,40158, la part 0,46062 de la phrase fausse entre les deux, le surcoût moyen par tirage, 3 252,80 AED, et les 100,4 dossiers sur 250 qui recevraient la mauvaise phrase. Elle note enfin que le glouton choisit « 21 » parce que 0,55 dépasse 0,45, mais basculerait vers « 30 » si cette probabilité baissait de 10 % à 0,495, et renvoie ces huit grandeurs, la décision étant de faire calculer les jours par un outil.

**`main()`** — C'est le banc d'essai qui rejoue la fiche dans l'ordre de lecture : il reprend le film des produits partiels 0,9, 0,45 et 0,36 et de leurs logarithmes, vérifie la règle de la chaîne sur une loi jointe de deux tokens, où P(a) × P(x | a) redonne 0,54 alors que l'indépendance supposée donnerait 0,396, puis montre qu'ajouter un token ne peut que faire baisser la vraisemblance, de 0,72 à 0,504. Il compare le glouton à 0,24 et la meilleure séquence à 0,36, cherche le premier n pour lequel 0,5ⁿ vaut zéro en machine, 1 075, vérifie que la séquence ne peut pas dépasser son token le plus faible, retrouve les moyennes géométriques 0,8785 et 0,80052 et les perplexités 1,1383 et 1,24919, et s'assure qu'une probabilité nulle est refusée ; il lance ensuite les quatre cas et refait le corrigé, chaque nombre étant confronté par un `assert` à la fiche avant la ligne finale de succès.

```python
"""Démonstration 23 — vraisemblance autorégressive : règle de la chaîne, logs, longueur, glouton, zéro machine, quatre cas aux EAU."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def vraisemblance(probas):
    """Produit direct Π P(x_t | x_<t, c) : exact en mathématiques, fragile en flottants."""
    return math.prod(probas)


def log_vraisemblance(probas):
    """Σ ln P(x_t | x_<t, c) ; chaque probabilité doit être dans ]0 ; 1]."""
    if any(not 0 < p <= 1 for p in probas):
        raise ValueError("chaque probabilité doit être dans ]0 ; 1]")
    return sum(math.log(p) for p in probas)


def moyenne_log(probas) -> float | None:
    """Log-vraisemblance moyenne par token ; None pour une séquence vide."""
    if not probas:
        return None
    return log_vraisemblance(probas) / len(probas)


def glouton(arbre, prefixe=()):
    """Choisit à chaque pas le token le plus probable ; renvoie (séquence, probabilité, appels au modèle)."""
    proba, appels = 1.0, 0
    while prefixe in arbre:
        appels += 1
        token, p = max(arbre[prefixe].items(), key=lambda kv: kv[1])
        prefixe, proba = prefixe + (token,), proba * p
    return prefixe, proba, appels


def faisceau(arbre, largeur):
    """Recherche en faisceau : garde les `largeur` meilleurs préfixes à chaque pas."""
    candidats, appels = [((), 1.0)], 0
    while any(c in arbre for c, _ in candidats):
        suivants = []
        for c, p in candidats:
            if c not in arbre:
                suivants.append((c, p))
                continue
            appels += 1
            suivants += [(c + (t,), p * q) for t, q in arbre[c].items()]
        candidats = sorted(suivants, key=lambda cp: -cp[1])[:largeur]
    return candidats[0][0], candidats[0][1], appels


def r5(xs):
    return [round(x, 5) for x in xs]


def cas_1_appels_outil_banque():
    """Banque : deux appels d'outil de virement, comparés brut, par token, et par la règle du token minimal."""
    a, b = [0.95, 0.9, 0.85, 0.9, 0.8], [0.95, 0.6, 0.9]
    seuil_token = 0.7
    ma, mb = moyenne_log(a), moyenne_log(b)
    q_bascule = math.exp(len(b) * ma - (math.log(0.95) + math.log(0.9)))
    a_long = a + [0.9] * 3
    retenu = "A" if ma > mb and min(a) >= seuil_token else "B"
    print(f"cas 1 BANQUE : P(A) = {vraisemblance(a):.5f} ; P(B) = {vraisemblance(b):.3f} ;"
          f" moyenne ln A {ma:.5f} ; B {mb:.5f}")
    print(f"  moyennes géométriques {math.exp(ma):.5f} et {math.exp(mb):.5f} ; min B {min(b)} < {seuil_token} ;"
          f" A allongé : P = {vraisemblance(a_long):.5f} ; bascule du token faible {q_bascule:.5f} ; retenu : {retenu}")
    print(f"  décision : présenter {retenu} ; B écarté (token {min(b)} sur le montant)")
    return a, b, ma, mb, q_bascule, a_long, retenu


def cas_2_plan_immo():
    """Immobilier : plan d'outils en deux pas ; glouton contre faisceau de largeur 2."""
    arbre = {(): {"transactions_DLD": 0.6, "fiche_bien": 0.4},
             ("transactions_DLD",): {"estimer": 0.4, "tendance": 0.35, "photos": 0.25},
             ("fiche_bien",): {"comparer_5_ventes": 0.9, "estimer": 0.1}}
    sg, pg, ag = glouton(arbre)
    sf, pf, af = faisceau(arbre, 2)
    pi_bascule = 0.9 / (0.9 + 0.4)                    # 0.4 π >= 0.9 (1 − π)
    q_bascule = pf / 0.6                               # suite après le premier choix glouton pour égaler 0.36
    print(f"cas 2 IMMO : glouton {sg} -> {pg:.2f} ({ag} appels) ; faisceau {sf} -> {pf:.2f} ({af} appels)")
    print(f"  ln {math.log(pg):.5f} contre {math.log(pf):.5f} ; bascule π {pi_bascule:.5f} ; bascule suite {q_bascule:.2f} ;"
          f" suite − 10 % : {0.4 * 0.81:.3f}")
    decision = "faisceau de largeur 2" if pf > pg else "glouton"
    print(f"  décision : {decision} (+{af - ag} appel, probabilité x{pf / pg:.1f})")
    return sg, pg, ag, sf, pf, af, pi_bascule, q_bascule, decision


def cas_3_rapports_crypto():
    """Crypto : trois rapports d'incident de longueurs différentes ; produit, somme, moyenne, pénalité de longueur."""
    rapports = {"R1": (300, -0.25), "R2": (450, -0.20), "R3": (1200, -0.65)}
    sommes = {k: n * m for k, (n, m) in rapports.items()}
    produits = {k: math.prod([math.exp(m)] * n) for k, (n, m) in rapports.items()}
    par_somme = max(sommes, key=sommes.get)
    par_moyenne = max(rapports, key=lambda k: rapports[k][1])
    alpha = math.log(90 / 75) / math.log(450 / 300)
    log10_r3 = sommes["R3"] / math.log(10)
    print(f"cas 3 CRYPTO : sommes {sommes} ; choix par somme {par_somme}, par moyenne {par_moyenne}")
    print(f"  produits flottants : R1 {produits['R1']:.3e}, R2 {produits['R2']:.3e}, R3 {produits['R3']:.0e}"
          f" (vrai : 10^{log10_r3:.2f}) ; α de bascule {alpha:.5f}")
    print(f"  décision : rapport {par_moyenne} (moyenne par token {rapports[par_moyenne][1]}), jamais le produit")
    return sommes, produits, par_somme, par_moyenne, alpha, log10_r3


def cas_4_fin_de_service_rh():
    """RH : deux phrases candidates pour l'indemnité de fin de service ; tirage, glouton, coût d'une erreur."""
    juste, fausse = [0.55, 0.9, 0.95], [0.45, 0.92, 0.97]   # « 21 jours … » contre « 30 jours … »
    base, annees = 9000, 3
    jour = base / 30
    du, faux = jour * 21 * annees, jour * 30 * annees
    p_juste, p_fausse = vraisemblance(juste), vraisemblance(fausse)
    surcout_moyen = p_fausse * (faux - du)
    dossiers = 250
    print(f"cas 4 RH : P(juste) = {p_juste:.5f} ; P(fausse) = {p_fausse:.5f} ; part de la fausse {p_fausse / (p_juste + p_fausse):.5f}")
    print(f"  dû {du:.0f} AED, faux {faux:.0f} AED, écart {faux - du:.0f} AED ; surcoût moyen par tirage {surcout_moyen:.2f} AED ;"
          f" {p_fausse * dossiers:.1f} dossiers sur {dossiers}")
    premier_glouton = "21" if juste[0] > fausse[0] else "30"
    premier_moins10 = "21" if 0.9 * juste[0] > 1 - 0.9 * juste[0] else "30"
    print(f"  glouton : « {premier_glouton} jours » ; si P(21) baisse de 10 % ({0.9 * juste[0]:.3f}) : « {premier_moins10} jours »"
          f" ; décision : jours calculés par outil")
    return p_juste, p_fausse, du, faux, surcout_moyen, dossiers, premier_glouton, premier_moins10


def main() -> None:
    # Film et exemple simple
    film = [0.9, 0.5, 0.8]
    produits = [math.prod(film[:k]) for k in (1, 2, 3)]
    logs = [log_vraisemblance(film[:k]) for k in (1, 2, 3)]
    print(f"film : produits {r5(produits)} ; logs {r5(logs)} ; exp {math.exp(logs[-1]):.5f}")
    assert r5(produits) == [0.9, 0.45, 0.36] and r5(logs) == [-0.10536, -0.79851, -1.02165]
    assert round(math.exp(logs[-1]), 5) == 0.36 and round(math.log(0.5), 5) == -0.69315 and round(math.log(0.8), 5) == -0.22314
    print(f"0,5^10 = {0.5 ** 10:.6f} ; ln = {log_vraisemblance([0.5] * 10):.5f}")
    assert round(0.5 ** 10, 6) == 0.000977 and round(log_vraisemblance([0.5] * 10), 5) == -6.93147 and 2 ** 10 == 1024

    # Démonstration 1 : règle de la chaîne sur une loi jointe explicite, et contre-exemple « indépendance »
    jointe = {("a", "x"): 0.54, ("a", "y"): 0.06, ("b", "x"): 0.12, ("b", "y"): 0.28}
    p_a = sum(v for (t1, _), v in jointe.items() if t1 == "a")
    p_x_sachant_a = jointe[("a", "x")] / p_a
    p_x = sum(v for (_, t2), v in jointe.items() if t2 == "x")
    print(f"démo 1 : P(a) = {p_a:.2f}, P(x | a) = {p_x_sachant_a:.2f}, produit {p_a * p_x_sachant_a:.2f} ;"
          f" indépendance supposée : {p_a * p_x:.3f}")
    assert math.isclose(p_a * p_x_sachant_a, jointe[("a", "x")]) and round(p_a, 2) == 0.6 and round(p_x_sachant_a, 2) == 0.9
    assert round(p_x, 2) == 0.66 and round(p_a * p_x, 3) == 0.396

    # Démonstration 2 et 3 : logs, longueur
    assert math.isclose(math.exp(log_vraisemblance([0.9, 0.8, 0.7])), 0.9 * 0.8 * 0.7)
    assert vraisemblance([0.9, 0.8, 0.7]) <= vraisemblance([0.9, 0.8])           # plus long, moins probable
    assert round(vraisemblance([0.9, 0.8]), 2) == 0.72 and round(vraisemblance([0.9, 0.8, 0.7]), 3) == 0.504
    assert round(vraisemblance([0.9, 0.8, 0.7, 0.99]), 5) == 0.49896
    print(f"démo 2-3 : 0,9 × 0,8 = {vraisemblance([0.9, 0.8]):.2f} ; × 0,7 = {vraisemblance([0.9, 0.8, 0.7]):.3f} ;"
          f" × 0,99 = {vraisemblance([0.9, 0.8, 0.7, 0.99]):.5f} ; ln(0,9 × 0,8 × 0,7) = {log_vraisemblance([0.9, 0.8, 0.7]):.5f}")

    # Démonstration 4 : glouton
    glouton_p, meilleur = 0.6 * 0.4, 0.4 * 0.9
    print(f"démo 4 : glouton {glouton_p:.2f} contre meilleure séquence {meilleur:.2f}")
    assert glouton_p < meilleur and math.isclose(meilleur / glouton_p, 1.5)

    # Démonstration 5 : zéro machine
    n0 = next(k for k in range(1, 3000) if 0.5 ** k == 0.0)
    print(f"démo 5 : 0,5^1074 = {0.5 ** 1074:.2e} ; 0,5^1075 = {0.5 ** 1075} ; premier n nul : {n0} ;"
          f" 0,5^1000 = {0.5 ** 1000:.1e} ; somme des ln pour 2000 : {log_vraisemblance([0.5] * 2000):.2f}")
    assert n0 == 1075 and 0.5 ** 1074 == 2 ** -1074 > 0 and round(-1075 * math.log(2), 2) == -745.13
    assert vraisemblance([0.5] * 2000) == 0.0 and round(log_vraisemblance([0.5] * 2000), 2) == -1386.29
    assert f"{0.5 ** 1000:.1e}" == "9.3e-302" and f"{2 ** -1074:.2e}" == "4.94e-324"

    # Démonstration 6 : le token le plus faible plafonne la séquence ; moyenne géométrique et perplexité
    a, b = [0.95, 0.9, 0.85, 0.9, 0.8], [0.95, 0.6, 0.9]
    for x in (a, b):
        assert vraisemblance(x) <= min(x)
        assert math.isclose(math.exp(moyenne_log(x)), vraisemblance(x) ** (1 / len(x)))
    ga, gb = math.exp(moyenne_log(a)), math.exp(moyenne_log(b))
    print(f"démo 6 : min {min(a)} et {min(b)} ; moyennes géométriques {ga:.5f} et {gb:.5f} ;"
          f" perplexités {1 / ga:.5f} et {1 / gb:.5f}")
    assert round(ga, 5) == 0.8785 and round(gb, 5) == 0.80052 and round(1 / ga, 5) == 1.1383 and round(1 / gb, 5) == 1.24919
    a99 = list(a)
    a99[4] *= 0.99
    assert math.isclose(moyenne_log(a99) - moyenne_log(a), math.log(0.99) / 5) and round(math.log(0.99) / 5, 5) == -0.00201
    assert moyenne_log([]) is None
    try:
        log_vraisemblance([0.5, 0.0])
    except ValueError:
        pass
    else:
        raise AssertionError("une probabilité nulle aurait dû être refusée")

    # Cas
    a1, b1, ma, mb, qb, a_long, retenu = cas_1_appels_outil_banque()
    assert round(vraisemblance(a1), 5) == 0.52326 and round(vraisemblance(b1), 3) == 0.513
    assert round(ma, 5) == -0.12954 and round(mb, 5) == -0.22249 and retenu == "A"
    assert round(log_vraisemblance(a1), 5) == -0.64768 and round(log_vraisemblance(b1), 5) == -0.66748
    assert round(vraisemblance(a_long), 5) == 0.38146 and vraisemblance(a_long) < vraisemblance(b1)
    assert round(moyenne_log(a_long), 5) == -0.12047 and round(qb, 5) == 0.79298 and round(3 * ma, 5) == -0.38861
    assert r5([math.log(p) for p in (0.95, 0.9, 0.85, 0.6)]) == [-0.05129, -0.10536, -0.16252, -0.51083]
    assert round(0.9 ** 3, 3) == 0.729

    sg, pg, ag, sf, pf, af, pib, qb2, dec2 = cas_2_plan_immo()
    assert dec2 == "faisceau de largeur 2"
    assert sg == ("transactions_DLD", "estimer") and round(pg, 2) == 0.24 and ag == 2
    assert sf == ("fiche_bien", "comparer_5_ventes") and round(pf, 2) == 0.36 and af == 3 and af / ag == 1.5
    assert round(math.log(pg), 5) == -1.42712 and round(math.log(pf), 5) == -1.02165
    assert round(pib, 5) == 0.69231 and round(qb2, 2) == 0.6 and round(0.4 * 0.81, 3) == 0.324 > 0.24
    assert round(0.6 * 0.35, 2) == 0.21 and round(0.6 * 0.25, 2) == 0.15 and round(0.4 * 0.1, 2) == 0.04

    sommes, prods, ps, pm, alpha, l10 = cas_3_rapports_crypto()
    assert sommes == {"R1": -75.0, "R2": -90.0, "R3": -780.0} and ps == "R1" and pm == "R2"
    assert f"{prods['R1']:.3e}" == "2.679e-33" and f"{prods['R2']:.3e}" == "8.194e-40" and prods["R3"] == 5e-324
    assert math.exp(-780.0) == 0.0 and round(alpha, 5) == 0.44966 and round(l10, 2) == -338.75
    assert round(10 ** (l10 + 339), 2) == 1.78 and -75 / 300 < -90 / 450       # R2 meilleur par token
    for al, gagnant in ((0.0, "R1"), (0.44, "R1"), (0.46, "R2"), (1.0, "R2")):
        assert max(("R1", "R2"), key=lambda k: sommes[k] / {"R1": 300, "R2": 450}[k] ** al) == gagnant

    pj, pfau, du, faux, surcout, dossiers, g4, g4m10 = cas_4_fin_de_service_rh()
    assert g4 == "21" and g4m10 == "30" and round(0.9 * 0.55, 3) == 0.495
    assert round(pj, 5) == 0.47025 and round(pfau, 5) == 0.40158 and round(pfau / (pj + pfau), 5) == 0.46062
    assert du == 18900 and faux == 27000 and faux - du == 8100 and round(surcout, 2) == 3252.8
    assert round(pfau * dossiers, 1) == 100.4 and 9000 / 30 == 300 and max(0.55, 0.45) == 0.55

    print("Corrigé")
    e1 = vraisemblance([0.5, 0.8, 0.25])
    n = next(k for k in range(1, 100) if 0.5 ** k < 1e-6)
    print(f"  ex1 {e1:.1f}, ln {math.log(e1):.3f} ; ex3 {0.9 ** 6:.6f} contre {0.7 ** 3:.3f} ;"
          f" ex4 glouton {0.5 * 0.3:.2f}, meilleur {0.3 * 0.95:.3f} ; ex5 {n} tokens")
    b6 = [0.95, 0.75, 0.9]
    print(f"  ex6 B : somme {log_vraisemblance(b6):.5f}, moyenne {moyenne_log(b6):.5f} < {ma:.5f} ;"
          f" ex7 {0.6 * 0.66:.3f} au lieu de {0.6 * 0.9:.2f}")
    assert math.isclose(e1, 0.1) and round(0.9 ** 6, 6) == 0.531441 and 0.5 * 0.3 < 0.3 * 0.95 and n == 20
    assert round(math.log(0.1), 3) == -2.303 and round(0.5 * 0.2, 2) == 0.1
    assert round(log_vraisemblance(b6), 5) == -0.44434 and round(moyenne_log(b6), 5) == -0.14811 and moyenne_log(b6) < ma
    assert min(b6) >= 0.7 and round(math.log(0.75), 5) == -0.28768 and round(math.log(10 ** 6, 2), 2) == 19.93
    # nombres cités dans le texte
    assert round(math.log(0.9) + math.log(0.8) + math.log(0.7), 5) == -0.68518 and round(math.log(0.7), 5) == -0.35667
    assert round(-0.69315 - 0.22314 - 1.38629, 5) == -2.30258 and round(math.log(0.25), 5) == -1.38629
    assert round(-0.38861 + 0.05129 + 0.10536, 5) == -0.23196 and round(math.exp(-0.23196), 5) == 0.79298
    assert round(math.exp(-0.65), 3) == 0.522 and math.isclose(math.exp(-log_vraisemblance([0.5] * 10) / 10), 2)
    ecart = math.log10(prods["R3"]) - l10
    assert round(ecart, 2) == 15.44 and round(10 ** (ecart - 15), 1) == 2.8
    assert round(0.81 ** 3, 6) == 0.531441 and round(math.log(0.9), 5) == -0.10536
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
film : produits [0.9, 0.45, 0.36] ; logs [-0.10536, -0.79851, -1.02165] ; exp 0.36000
0,5^10 = 0.000977 ; ln = -6.93147
démo 1 : P(a) = 0.60, P(x | a) = 0.90, produit 0.54 ; indépendance supposée : 0.396
démo 2-3 : 0,9 × 0,8 = 0.72 ; × 0,7 = 0.504 ; × 0,99 = 0.49896 ; ln(0,9 × 0,8 × 0,7) = -0.68518
démo 4 : glouton 0.24 contre meilleure séquence 0.36
démo 5 : 0,5^1074 = 4.94e-324 ; 0,5^1075 = 0.0 ; premier n nul : 1075 ; 0,5^1000 = 9.3e-302 ; somme des ln pour 2000 : -1386.29
démo 6 : min 0.8 et 0.6 ; moyennes géométriques 0.87850 et 0.80052 ; perplexités 1.13830 et 1.24919
cas 1 BANQUE : P(A) = 0.52326 ; P(B) = 0.513 ; moyenne ln A -0.12954 ; B -0.22249
  moyennes géométriques 0.87850 et 0.80052 ; min B 0.6 < 0.7 ; A allongé : P = 0.38146 ; bascule du token faible 0.79298 ; retenu : A
  décision : présenter A ; B écarté (token 0.6 sur le montant)
cas 2 IMMO : glouton ('transactions_DLD', 'estimer') -> 0.24 (2 appels) ; faisceau ('fiche_bien', 'comparer_5_ventes') -> 0.36 (3 appels)
  ln -1.42712 contre -1.02165 ; bascule π 0.69231 ; bascule suite 0.60 ; suite − 10 % : 0.324
  décision : faisceau de largeur 2 (+1 appel, probabilité x1.5)
cas 3 CRYPTO : sommes {'R1': -75.0, 'R2': -90.0, 'R3': -780.0} ; choix par somme R1, par moyenne R2
  produits flottants : R1 2.679e-33, R2 8.194e-40, R3 5e-324 (vrai : 10^-338.75) ; α de bascule 0.44966
  décision : rapport R2 (moyenne par token -0.2), jamais le produit
cas 4 RH : P(juste) = 0.47025 ; P(fausse) = 0.40158 ; part de la fausse 0.46062
  dû 18900 AED, faux 27000 AED, écart 8100 AED ; surcoût moyen par tirage 3252.80 AED ; 100.4 dossiers sur 250
  glouton : « 21 jours » ; si P(21) baisse de 10 % (0.495) : « 30 jours » ; décision : jours calculés par outil
Corrigé
  ex1 0.1, ln -2.303 ; ex3 0.531441 contre 0.343 ; ex4 glouton 0.15, meilleur 0.285 ; ex5 20 tokens
  ex6 B : somme -0.44434, moyenne -0.14811 < -0.12954 ; ex7 0.396 au lieu de 0.54
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme calcule la probabilité d'une séquence produite token par token, de préférence en logarithmes, et la normalise par la longueur pour comparer deux réponses. Une variante compare le décodage glouton et la recherche en faisceau sur un arbre de probabilités conditionnelles.

```text
ALGORITHME LogVraisemblance
ENTRÉE  : probabilités conditionnelles p₁ … pₙ des tokens produits
SORTIE  : (log-vraisemblance, moyenne par token), ou INDÉFINI si n = 0

  SI n = 0 ALORS RETOURNER INDÉFINI
  total ← 0
  POUR t DE 1 À n FAIRE
      SI pₜ ≤ 0 OU pₜ > 1 ALORS ERREUR
      total ← total + ln pₜ
  FIN POUR
  RETOURNER total, total / n

ALGORITHME ComparerDeuxRéponses
ENTRÉES : réponses A et B avec leurs probabilités par token, seuil s du token minimal
  écarter toute réponse dont un token est sous s
  SI moyenne(A) > moyenne(B) ALORS RETOURNER A SINON RETOURNER B

ALGORITHME Faisceau
ENTRÉES : arbre des probabilités conditionnelles, largeur k
  candidats ← [(séquence vide, 1)]
  TANT QUE un candidat peut être prolongé FAIRE
      remplacer chaque candidat prolongeable par tous ses prolongements (probabilité × facteur)
      garder les k candidats les plus probables
  FIN TANT QUE
  RETOURNER le meilleur candidat
```

**Complexité.** LogVraisemblance coûte O(n) en temps et O(1) en mémoire. Le calcul en logarithmes ne déborde jamais, alors que le produit direct devient 0 au-delà d'environ 1 075 tokens à 0,5. Le faisceau de largeur k fait au plus k appels au modèle par pas, contre un seul pour le glouton ; sur n pas et un vocabulaire V, il trie au plus k × V prolongements par pas.

**Du squelette au code.** LogVraisemblance est `log_vraisemblance(probas)`, et `moyenne_log(probas)` renvoie la moyenne ou `None` ; le produit direct, qui montre le zéro machine, est `vraisemblance`. La comparaison des deux appels d'outil divise ces sommes par 5 et par 3 dans `cas_1_appels_outil_banque`. Le contre-exemple au décodage glouton compare `0.6 * 0.4` et `0.4 * 0.9` ; Faisceau est la fonction `faisceau`, comparée à `glouton` dans `cas_2_plan_immo`. Les deux autres cas sont `cas_3_rapports_crypto` et `cas_4_fin_de_service_rh`.
