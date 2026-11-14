# 28 — Valeur de l'information : démonstrations

> Fiche : [28 — Valeur de l'information](<../../Images/06-Decision/28_valeur_information.md>) · Image : `28_valeur_information.jpg` · Leçon : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
\operatorname{VOI} = \mathbb{E}\left[ \max_{a} U(a \mid E) \right] - \max_{a} U(a)
$$

On compare deux façons de décider : tout de suite, avec ce qu'on sait (max U(a)), ou après avoir observé une information E, en choisissant la meilleure action pour chaque résultat possible de E. La différence est ce que vaut cette information. On ne la paie que si elle coûte moins que sa valeur.

## Les symboles, un par un

$$
\operatorname{VOI}
$$

**VOI** : la valeur de l'information E, exprimée dans l'unité de l'utilité (ici des AED par dossier) ; c'est un nombre ≥ 0 (démonstration 1) ; en Python, `voi(prior, sensibilite, fausse_alerte)[0]` pour un test à deux issues et `voi_generale(probas, utilites, vraisemblances)[0]` dans le cas général.

$$
a \in A
$$

**a** : une action possible, prise dans l'ensemble fini A des actions (valider ou refuser un dossier, approuver un prêt, lancer à tel prix) ; en Python, le tuple `ACTIONS` ou les clés du dictionnaire `utilites`.

$$
\omega
$$

**ω** : l'état réel du monde, que l'agent ne connaît pas au moment de décider (demande saine ou frauduleuse, client solvable ou en défaut) ; en Python, l'indice `j` de `probas[j]`.

$$
U(a, \omega)
$$

**U(a, ω)** : l'utilité de l'action a si l'état est ω, en AED (positive pour un gain, négative pour une perte) ; c'est une table écrite par l'équipe métier ; en Python, `utilites[a][j]`, et dans l'exemple de base les deux formules de `utilite(p_fraude, action)`.

$$
U(a) = \sum_{\omega} P(\omega)\, U(a, \omega)
$$

**U(a)** : l'utilité attendue de a avec ce que l'on sait déjà, c'est-à-dire la moyenne de sa ligne de la table pondérée par les probabilités des états (fiche 10) ; en Python, `utilite(prior, action)`.

$$
E,\ e
$$

**E** : l'information pas encore observée (le résultat d'un outil, d'un document, d'une étude) ; **e** désigne l'un de ses résultats possibles (« signal » ou « rien ») ; en Python, l'indice `e` de `vraisemblances[j][e]`.

$$
U(a \mid e) = \sum_{\omega} P(\omega \mid e)\, U(a, \omega)
$$

**U(a | e)** : l'utilité attendue de a une fois le résultat e connu, avec les probabilités des états mises à jour par Bayes (fiche 07) ; en Python, `utilite(p_f_s, action)` après un signal et `utilite(p_f_n, action)` sans signal.

$$
\max_{a}
$$

**max** : la meilleure action ; max U(a) est la valeur de la décision prise tout de suite, max U(a | e) celle de la décision prise après avoir vu e ; en Python, `meilleure(p_fraude)`.

$$
\mathbb{E}_e[\ \cdot\ ] = \sum_e P(e)\,[\ \cdot\ ]
$$

**𝔼** : la moyenne sur les résultats possibles de E, pondérée par leurs probabilités P(e) ; en Python, `p_s` et `1 - p_s` pour un test à deux issues.

$$
\pi,\ Se,\ \alpha
$$

**π** : la probabilité a priori de l'état défavorable (fraude, défaut), dans [0 ; 1], variable `prior` ; **Se** : la sensibilité du test, part des cas défavorables qu'il signale, variable `sensibilite` ; **α** : son taux de fausses alertes, part des cas favorables qu'il signale à tort, variable `fausse_alerte` (α = 1 − Sp, avec les notations de la leçon 51).

$$
c
$$

**c** : le coût de l'information (appel d'API, temps d'un analyste, délai), en AED, à comparer à la VOI ; en Python, le nombre `30` du cas 1 ou la variable `cout2` du cas 4.

## Le mécanisme, avant les preuves

Ce qui entre : une table d'utilités U(a, ω), avec une ligne par action et une colonne par état, les probabilités des états, et la façon dont le résultat de l'information dépend de l'état (Se et α pour un test à deux issues). Le terme max U(a) fait deux opérations dans cet ordre : d'abord une moyenne pondérée sur chaque ligne, ce qui donne U(a), puis un maximum sur les lignes. L'agent s'engage alors sur une seule action, la même pour tous les états. Le terme 𝔼[max U(a | E)] fait les mêmes opérations dans l'ordre inverse : pour chaque résultat e, Bayes met à jour les probabilités, on prend le maximum des utilités, puis on fait la moyenne de ces maxima pondérée par P(e). Toute la formule tient dans cet ordre : « moyenne puis maximum », c'est décider à l'aveugle ; « maximum puis moyenne », c'est décider en sachant. Un maximum de moyennes ne dépasse jamais une moyenne de maxima (démonstration 1) : la différence est donc toujours positive ou nulle. Le maximum, et non une moyenne sur les actions, traduit le fait que l'agent choisit sa meilleure action au lieu de la tirer au sort. Pour la même raison, une information ne rapporte que si elle peut changer ce choix (démonstration 2). La soustraction, et non un rapport, laisse la VOI dans l'unité des utilités, en AED, pour la comparer directement au coût c, en AED aussi. Ce qui sort : un montant par décision, au plus égal à la VOI de l'information parfaite (démonstration 3).

Petit film chiffré, avec 80 % de demandes saines et 20 % de fraudes. Ligne « valider » : 0,8 × 100 = 80 et 0,2 × (−400) = −80, moyenne 0. Ligne « refuser » : 0,8 × (−50) = −40 et 0,2 × 0 = 0, moyenne −40. Le maximum des moyennes vaut 0 : sans information, on valide. Dans l'autre ordre, colonne « saine » : max(100 ; −50) = 100 ; colonne « fraude » : max(−400 ; 0) = 0 ; moyenne 0,8 × 100 + 0,2 × 0 = 80. La différence 80 − 0 = 80 est la VOI de l'information parfaite. Pour un développeur Spring : c'est un appel à un service externe dans un orchestrateur, qui ne vaut la peine que si sa réponse peut faire prendre une autre branche du `if` qui suit.

## Démonstration 1 — Une information ne peut pas faire baisser l'utilité attendue

**Ce qu'on démontre.** Si l'information E est gratuite, si l'agent calcule ses probabilités P(ω | e) par la règle de Bayes et s'il choisit la meilleure action dans chaque branche, alors :

$$
\operatorname{VOI} = \mathbb{E}_e\left[ \max_a U(a \mid e) \right] - \max_a U(a) \ge 0
$$

**L'idée.** Avec l'information, l'agent garde toujours la possibilité de l'ignorer et de jouer l'action a* qu'il aurait jouée sans elle. Cette stratégie « ignorer » rapporte exactement l'utilité sans information. Choisir au mieux dans chaque branche ne peut donc pas faire moins bien que l'ignorer.

**La preuve, pas à pas.**

**Étape 1.** On note a* une action qui réalise max U(a). Pour chaque résultat e, le maximum sur les actions est au moins égal à la valeur de l'action particulière a*, parce qu'un maximum majore chacun de ses termes :

$$
\max_a U(a \mid e) \ge U(a^* \mid e)
$$

**Étape 2.** On multiplie chaque inégalité par P(e) ≥ 0 et on additionne sur e, parce qu'une somme d'inégalités de même sens à coefficients positifs reste vraie :

$$
\sum_e P(e) \max_a U(a \mid e) \ge \sum_e P(e)\, U(a^* \mid e)
$$

**Étape 3.** On remplace U(a* | e) par sa définition et on utilise P(e) × P(ω | e) = P(ω, e), parce que c'est la définition d'une probabilité conditionnelle :

$$
\sum_e P(e)\, U(a^* \mid e) = \sum_e \sum_\omega P(\omega, e)\, U(a^*, \omega)
$$

**Étape 4.** On échange les deux sommes ; la somme de P(ω, e) sur tous les résultats e vaut P(ω), parce que les résultats possibles sont disjoints et couvrent tous les cas (probabilités totales) :

$$
\sum_\omega \Big( \sum_e P(\omega, e) \Big) U(a^*, \omega) = \sum_\omega P(\omega)\, U(a^*, \omega) = U(a^*) = \max_a U(a)
$$

**Étape 5.** En enchaînant les étapes 2, 3 et 4, la moyenne des maxima est au moins max U(a), donc VOI ≥ 0. ∎

**Vérification chiffrée.** Avec π = 0,2, Se = 0,9 et α = 0,05 (cas 1), a* = valider. La moyenne de U(valider | e) sur les deux branches vaut 0,22 × (−309,09) + 0,78 × 87,18 = −68,00 + 68,00 = 0,00 : on retrouve U(valider) = 0, comme l'annoncent les étapes 3 et 4. Le meilleur choix par branche donne 66, qui est bien ≥ 0. Contre-exemple quand l'hypothèse « choisir au mieux » manque : un signal de pur bruit sonne une fois sur deux, quel que soit l'état ; un agent qui lui obéit refuse quand il sonne et obtient 0,5 × (−40) + 0,5 × 0 = −20. Cette information mal utilisée lui coûte 20 AED par dossier.

**Ce que la preuve révèle du mécanisme.** L'étape 1 est la seule inégalité de la preuve ; elle devient une égalité dans chaque branche où a* reste le meilleur choix. Toute la valeur de l'information vient donc des branches où la décision change. La garantie VOI ≥ 0 porte sur un agent qui exploite correctement l'information : une règle mal écrite ou une probabilité a posteriori fausse peut faire perdre de l'argent.

**Conséquence pour un agent.** On n'écrit pas une règle « si l'outil dit X, faire Y » sans vérifier que Y est le meilleur choix sachant X : on calcule P(ω | e) par Bayes et on prend le maximum dans chaque branche. La VOI ne compte pas le coût de l'appel : la décision finale compare la VOI au coût c.

## Démonstration 2 — Une information qui ne change aucune décision ne vaut rien

**Ce qu'on démontre.** Si une même action a* est optimale après chaque résultat e de probabilité non nulle, alors VOI = 0. Réciproquement, s'il existe un résultat e₀ de probabilité > 0 après lequel une autre action fait strictement mieux que a*, alors VOI > 0 :

$$
\Big( \forall e,\ \max_a U(a \mid e) = U(a^* \mid e) \Big) \Longrightarrow \operatorname{VOI} = 0
$$

**L'idée.** La seule inégalité de la démonstration 1 est celle de l'étape 1. Si a* gagne dans chaque branche, elle devient une égalité partout, et toute la chaîne devient une chaîne d'égalités. Si a* perd dans une branche probable, l'écart de cette branche s'ajoute à la VOI.

**La preuve, pas à pas.**

**Étape 1.** On réécrit la VOI comme une somme d'écarts, en utilisant max U(a) = Σₑ P(e) U(a* | e) (étapes 3 et 4 de la démonstration 1) :

$$
\operatorname{VOI} = \sum_e P(e) \Big( \max_a U(a \mid e) - U(a^* \mid e) \Big)
$$

**Étape 2.** Chaque parenthèse est ≥ 0, parce qu'un maximum majore U(a* | e). Si a* est optimale après chaque e, chaque parenthèse est nulle, donc la somme aussi :

$$
\operatorname{VOI} = \sum_e P(e) \times 0 = 0
$$

**Étape 3.** Réciproque : si P(e₀) > 0 et si la parenthèse de e₀ est strictement positive, la somme de termes ≥ 0 est au moins égale à ce terme, parce qu'on ne retire rien en ajoutant des termes positifs :

$$
\operatorname{VOI} \ge P(e_0) \Big( \max_a U(a \mid e_0) - U(a^* \mid e_0) \Big) > 0
$$

∎

**Vérification chiffrée.** Un détecteur faible a Se = 0,12 et α = 0,10 (rapport de vraisemblance 0,12 / 0,10 = 1,2), avec π = 0,2. Probabilité d'un signal : 0,12 × 0,2 + 0,10 × 0,8 = 0,024 + 0,080 = 0,104. Après un signal, P(fraude | s) = 0,024 / 0,104 ≈ 0,23077 ; sans signal, P(fraude | rien) = 0,88 × 0,2 / 0,896 = 0,176 / 0,896 ≈ 0,19643. Refuser ne devient meilleur qu'au-dessus du seuil 150 / 550 ≈ 0,27273 (démonstration 5). Les deux probabilités a posteriori sont sous ce seuil : on valide dans les deux branches et VOI = 0. Le détecteur est pourtant informatif, puisqu'il fait passer la fraude de 20 % à 23 % ; il ne vaut rien ici parce qu'il ne fait franchir le seuil à aucune croyance.

**Ce que la preuve révèle du mécanisme.** La VOI ne mesure pas la précision d'une information, mais combien elle change les décisions. Elle dépend de la distance entre la croyance actuelle et le seuil de décision : une preuve modeste vaut beaucoup près du seuil et rien loin de lui.

**Conséquence pour un agent.** Avant d'appeler un outil, l'agent se demande : « existe-t-il un résultat possible qui me ferait changer d'action ? ». Si aucun résultat ne fait franchir le seuil, l'appel est retiré du plan : c'est le garde-fou qui arrête les boucles d'agent qui cherchent sans fin (fiche 28).

## Démonstration 3 — L'information parfaite est un plafond

**Ce qu'on démontre.** Pour toute information E utilisée au mieux :

$$
0 \le \operatorname{VOI}(E) \le \operatorname{VOI}_{\text{parfaite}} = \sum_\omega P(\omega) \max_a U(a, \omega) - \max_a U(a)
$$

**L'idée.** Avec E, l'agent choisit une action par résultat. Quel que soit ce choix, dans chaque état ω il obtient au plus la meilleure utilité de cet état, max U(a, ω). C'est exactement ce qu'obtient un agent qui connaît l'état avant de décider.

**La preuve, pas à pas.**

**Étape 1.** On note δ(e) l'action choisie après le résultat e. L'utilité attendue avec E se réécrit comme une somme sur les cases (ω, e), parce que P(e) U(a | e) = Σ P(ω, e) U(a, ω) (étape 3 de la démonstration 1) :

$$
\mathbb{E}_e\left[ \max_a U(a \mid e) \right] = \sum_e \sum_\omega P(\omega, e)\, U(\delta(e), \omega)
$$

**Étape 2.** Dans chaque case, U(δ(e), ω) ≤ max U(a, ω), parce qu'un maximum sur les actions majore la valeur de n'importe quelle action ; les poids P(ω, e) sont ≥ 0 :

$$
\sum_e \sum_\omega P(\omega, e)\, U(\delta(e), \omega) \le \sum_e \sum_\omega P(\omega, e) \max_a U(a, \omega)
$$

**Étape 3.** Le maximum de droite ne dépend plus de e ; on additionne P(ω, e) sur e, ce qui donne P(ω) (probabilités totales) :

$$
\sum_\omega \Big( \sum_e P(\omega, e) \Big) \max_a U(a, \omega) = \sum_\omega P(\omega) \max_a U(a, \omega)
$$

**Étape 4.** C'est l'utilité attendue de l'agent qui connaît l'état. On retranche max U(a) des deux côtés : VOI(E) ≤ VOI parfaite ; la borne 0 vient de la démonstration 1. ∎

**Vérification chiffrée.** Avec π = 0,2, la VOI parfaite vaut 80 (exemple simple) et celle de l'outil réel (Se = 0,9, α = 0,05) vaut 66 : 0 ≤ 66 ≤ 80. Le programme vérifie aussi la double inégalité sur 101 valeurs de π et trois détecteurs différents.

**Ce que la preuve révèle du mécanisme.** L'écart entre la VOI parfaite et la VOI réelle vient des cases où δ(e) n'est pas la meilleure action de l'état : les fraudes que le test laisse passer et les demandes saines qu'il signale à tort. La démonstration 4 chiffre exactement ces deux cases.

**Conséquence pour un agent.** La VOI parfaite se calcule avec la seule table d'utilités, sans rien savoir du test. Si elle est déjà inférieure au coût d'une vérification, aucune vérification de ce prix ne peut valoir le coup, et l'agent arrête l'analyse sans calculer Bayes (cas 3 et 4).

## Démonstration 4 — Forme fermée : fraudes rattrapées moins fausses alertes

**Ce qu'on démontre.** Deux états (saine, fraude), deux actions. Sans information, on valide ; avec le test, on refuse quand il sonne et on valide sinon. On note g = U(refuser, fraude) − U(valider, fraude) le regret évité sur une fraude rattrapée, et k = U(valider, saine) − U(refuser, saine) le regret créé par une demande saine refusée. Alors :

$$
\operatorname{VOI} = \pi \, Se \, g - (1 - \pi)\, \alpha \, k
$$

**L'idée.** Avec ou sans test, l'agent fait la même chose partout, sauf quand le test sonne : il refuse au lieu de valider. Le test sonne dans deux sortes de cases, une fraude (on gagne g) ou une demande saine (on perd k). La VOI est le solde de ces deux cases.

**La preuve, pas à pas.**

**Étape 1.** On écrit U(valider) comme une somme sur les cases (ω, e), parce que la somme de P(ω, e) sur e vaut P(ω) ; on retranche case par case :

$$
\operatorname{VOI} = \sum_{\omega, e} P(\omega, e) \Big( U(\delta(e), \omega) - U(\text{valider}, \omega) \Big)
$$

**Étape 2.** Dans les deux cases « rien », δ(e) = valider : la parenthèse est nulle, parce qu'on retranche une utilité d'elle-même.

**Étape 3.** Case (fraude, signal) : sa probabilité est P(fraude) × P(signal | fraude) = π Se, et la parenthèse vaut U(refuser, fraude) − U(valider, fraude) = g.

**Étape 4.** Case (saine, signal) : sa probabilité est (1 − π) α, et la parenthèse vaut U(refuser, saine) − U(valider, saine) = −k. On additionne les deux cases restantes :

$$
\operatorname{VOI} = \pi \, Se \, g + (1 - \pi)\, \alpha \, (-k) = \pi \, Se \, g - (1 - \pi)\, \alpha \, k
$$

∎

**Vérification chiffrée.** Ici g = 0 − (−400) = 400 et k = 100 − (−50) = 150. Cas 1 : 0,2 × 0,9 × 400 = 72 et 0,8 × 0,05 × 150 = 6, donc VOI = 72 − 6 = 66, le même nombre que par Bayes, sans calculer une seule probabilité conditionnelle. Information parfaite (Se = 1, α = 0) : 0,2 × 1 × 400 = 80. Contre-exemple quand l'hypothèse « le test fait basculer la décision » manque : pour le détecteur faible de la démonstration 2, la formule donne 0,2 × 0,12 × 400 − 0,8 × 0,10 × 150 = 9,6 − 12 = −2,4. Ce nombre négatif est la valeur de la règle « refuser quand il sonne », qui n'est pas la meilleure ; la vraie VOI de ce détecteur vaut 0.

**Ce que la preuve révèle du mécanisme.** La VOI est linéaire en Se et en α. Dans le cas 1, chaque point de sensibilité (0,01) rapporte π g / 100 = 0,8 AED et chaque point de fausses alertes coûte (1 − π) k / 100 = 1,2 AED. Les fausses alertes coûtent plus cher par point, parce que les demandes saines sont quatre fois plus nombreuses que les fraudes.

**Conséquence pour un agent.** Pour comparer deux détecteurs, ou deux seuils d'un même détecteur qui échangent Se contre α, on compare π Se g − (1 − π) α k avec les vrais coûts métier g et k, après avoir vérifié que chaque réglage fait bien basculer la décision.

## Démonstration 5 — L'information vaut le plus quand l'agent hésite

**Ce qu'on démontre.** Avec g = 400 et k = 150, la VOI parfaite en fonction du taux de fraude π a la forme d'un toit, maximal au seuil π* où elle vaut 1 200/11 ≈ 109,09 :

$$
\operatorname{VOI}_{\text{parfaite}}(\pi) = \begin{cases} 400\, \pi & \text{si } \pi \le \pi^* \\ 150\,(1 - \pi) & \text{si } \pi \ge \pi^* \end{cases} \qquad \pi^* = \frac{150}{550}
$$

**L'idée.** La VOI parfaite est le regret attendu de l'action choisie à l'aveugle. Quand π est petit, on valide et l'on ne regrette que les fraudes ; quand π est grand, on refuse et l'on ne regrette que les demandes saines. Au seuil, les deux regrets sont égaux, et c'est là qu'ils sont les plus grands.

**La preuve, pas à pas.**

**Étape 1.** Le seuil est la valeur de π où les deux actions se valent ; on développe et on regroupe les termes en π :

$$
100(1 - \pi) - 400\pi = -50(1 - \pi) \iff 150(1 - \pi) = 400\pi \iff \pi^* = \frac{150}{550} = \frac{3}{11} \approx 0{,}27273
$$

**Étape 2.** Pour π ≤ π*, a* = valider. Le regret de valider vaut 0 sur une demande saine et 400 sur une fraude, parce que c'est g ; la démonstration 4 avec Se = 1 et α = 0 donne :

$$
\operatorname{VOI}_{\text{parfaite}} = \pi \times 1 \times 400 - (1 - \pi) \times 0 \times 150 = 400\, \pi
$$

**Étape 3.** Pour π ≥ π*, a* = refuser. Le regret de refuser vaut 100 − (−50) = 150 sur une demande saine et 0 sur une fraude, parce que refuser est déjà le meilleur choix face à une fraude :

$$
\operatorname{VOI}_{\text{parfaite}} = (1 - \pi) \times 150
$$

**Étape 4.** La première branche croît avec π, la seconde décroît ; elles se rejoignent en π*, où 400 × 3/11 = 1 200/11 = 150 × 8/11. Le maximum du toit est donc atteint en π*. ∎

**Vérification chiffrée.** π = 0,2 : 400 × 0,2 = 80. π = 0,5 : 150 × 0,5 = 75 (exercice 1). π = 3/11 : 109,09. Sensibilité : sous le seuil, un point de fraude de plus (0,2 → 0,21) ajoute 400 × 0,01 = 4 AED de VOI parfaite.

**Ce que la preuve révèle du mécanisme.** La VOI n'est pas une propriété du test seul : elle dépend de la croyance de départ. Une croyance proche de 0 ou de 1 rend toute vérification presque inutile, une croyance proche du seuil la rend précieuse. Les pentes 400 et 150 sont les deux regrets : plus une erreur coûte cher, plus le toit monte vite de son côté.

**Conséquence pour un agent.** L'agent n'applique ni « toujours vérifier » ni « jamais » : il calcule sa croyance et ne paie la vérification que dans une bande autour de π*. Pour une vérification parfaite à 30 AED, la bande est 400π > 30 et 150(1 − π) > 30, soit 0,075 < π < 0,8.

## Exemple simple, à la main

Un agent doit valider ou refuser un remboursement. 20 % des demandes sont frauduleuses. Valider une demande saine rapporte 100, valider une fraude coûte 400, refuser une demande saine coûte 50, refuser une fraude rapporte 0.

**Sans information.** On fait la moyenne de chaque ligne de la table :

$$
U(\text{valider}) = 0{,}8 \times 100 - 0{,}2 \times 400 = 80 - 80 = 0
$$

$$
U(\text{refuser}) = -0{,}8 \times 50 + 0{,}2 \times 0 = -40 + 0 = -40
$$

Le maximum vaut 0 : sans information, on valide.

**Avec une vérification parfaite.** On prend le maximum de chaque colonne, puis la moyenne : on valide les saines (max(100 ; −50) = 100) et on refuse les fraudes (max(−400 ; 0) = 0).

$$
\mathbb{E}[\max] = 0{,}8 \times 100 + 0{,}2 \times 0 = 80 \quad\Longrightarrow\quad \operatorname{VOI}_{\text{parfaite}} = 80 - 0 = 80
$$

| | saine (0,8) | fraude (0,2) | moyenne de la ligne |
| --- | --- | --- | --- |
| valider | 100 | −400 | 0 |
| refuser | −50 | 0 | −40 |
| maximum de la colonne | 100 | 0 | 80 |

Si la vérification coûte 30, elle laisse un gain net de 80 − 30 = 50 par demande : on la paie. Si elle coûte 120, on décide sans elle.

## Cas d'usage complexes, démontrés

### Cas 1 — Assureur auto et santé : vérifier un dossier de remboursement « à risque »

**Contexte.** Un assureur auto et santé de Dubaï fait trier par un agent les demandes de remboursement santé qu'un premier filtre a classées « à risque » : 2 000 dossiers par mois, dont 20 % de fraudes (chiffres illustratifs). Avant de décider, l'agent peut lancer un outil de vérification croisée (factures de la clinique, historique de l'assuré, ordonnances), facturé 30 AED par appel en temps d'API et de revue. « Refuser » signifie ici suspendre le paiement et transmettre le dossier au service fraude. Question : l'appel vaut-il son coût, dossier par dossier ?

**Données.**

- π = 0,2 ; utilités en AED : valider une saine +100, valider une fraude −400, refuser une saine −50, refuser une fraude 0.
- Outil : Se = 0,9 (il signale 90 % des fraudes), α = 0,05 (il signale à tort 5 % des saines).
- Coût c = 30 AED par appel ; volume 2 000 dossiers par mois.

**Calcul pas à pas.**

**Étape 1.** Sans information : U(valider) = 0 et U(refuser) = −40 (exemple simple), donc on valide et la valeur vaut 0.

**Étape 2.** Probabilité d'un signal, par les probabilités totales :

$$
P(s) = 0{,}9 \times 0{,}2 + 0{,}05 \times 0{,}8 = 0{,}18 + 0{,}04 = 0{,}22
$$

**Étape 3.** Probabilités a posteriori par Bayes (fiche 07), arrondies à 5 décimales :

$$
P(\text{fraude} \mid s) = \frac{0{,}18}{0{,}22} \approx 0{,}81818 \qquad P(\text{fraude} \mid \text{rien}) = \frac{0{,}1 \times 0{,}2}{1 - 0{,}22} = \frac{0{,}02}{0{,}78} \approx 0{,}02564
$$

**Étape 4.** Utilités dans chaque branche, arrondies au centime. Après un signal, valider vaut 0,18182 × 100 − 0,81818 × 400 ≈ 18,18 − 327,27 = −309,09 et refuser vaut −0,18182 × 50 ≈ −9,09 : on refuse. Sans signal, valider vaut 0,97436 × 100 − 0,02564 × 400 ≈ 97,44 − 10,26 = 87,18 et refuser vaut −0,97436 × 50 ≈ −48,72 : on valide.

$$
U(\text{valider} \mid s) \approx -309{,}09 \qquad U(\text{refuser} \mid s) \approx -9{,}09 \qquad U(\text{valider} \mid \text{rien}) \approx 87{,}18
$$

**Étape 5.** Moyenne des maxima, pondérée par P(e) :

$$
\mathbb{E}[\max] = 0{,}22 \times (-9{,}09) + 0{,}78 \times 87{,}18 \approx -2{,}00 + 68{,}00 = 66{,}00 \quad\Longrightarrow\quad \operatorname{VOI} = 66 - 0 = 66
$$

**Étape 6.** Contrôle par la forme fermée (démonstration 4) : 0,2 × 0,9 × 400 − 0,8 × 0,05 × 150 = 72 − 6 = 66. Gain net : 66 − 30 = 36 AED par dossier, soit 2 000 × 36 = 72 000 AED par mois.

**Décision de l'agent.** VOI = 66 > c = 30 : l'agent lance la vérification sur chaque dossier « à risque ». Si l'outil sonne, P(fraude | s) ≈ 0,818 dépasse le seuil π* ≈ 0,273 et le dossier part au service fraude ; sinon, P(fraude | rien) ≈ 0,026 est sous le seuil et le paiement est validé.

**Contre-calcul.** Un agent qui ne vérifie jamais obtient 0 par dossier au lieu de 36 : il laisse 72 000 AED par mois. Un agent qui raisonne avec la VOI parfaite (80) au lieu de la vraie (66) se trompe dès que l'outil coûte entre 66 et 80 AED : à 70 AED, il achète la vérification (« 80 > 70 ») et perd 70 − 66 = 4 AED par dossier, soit 2 000 × 4 = 8 000 AED par mois (chiffres illustratifs).

**Sensibilité.** La valeur de bascule sur le coût est c = 66 AED. Par la forme fermée, VOI = 72 − 120α à Se fixé : la VOI tombe à 30 quand α = 42 / 120 = 0,35. À α fixé, VOI = 80 Se − 6 : elle tombe à 30 quand Se = 36 / 80 = 0,45. Une baisse de 10 % de la sensibilité (0,9 → 0,81) donne VOI = 80 × 0,81 − 6 = 64,8 − 6 = 58,8 : la décision ne change pas.

**En production.** On suit chaque mois Se et α mesurés sur les dossiers clos ; l'alerte part si α dépasse 0,35 ou si Se passe sous 0,45, car l'outil coûterait alors plus qu'il ne rapporte. L'assurance est supervisée par la CBUAE et les données de santé relèvent de la PDPL (décret-loi fédéral 45/2021) hors DIFC et ADGM ; les exigences précises sur la motivation d'une suspension de paiement sont à confirmer avec le texte en vigueur.

### Cas 2 — Banque de détail de Dubaï : demander six mois de relevés avant un prêt personnel

**Contexte.** L'agent de pré-instruction des prêts personnels d'une banque de détail de Dubaï peut demander au client six mois de relevés d'un autre compte, en plus du certificat de salaire obligatoire. Le dossier type est un prêt de 60 000 AED sur 48 mois pour un salaire de 15 000 AED par mois, avec 1 500 dossiers par mois (chiffres illustratifs). La demande coûte 200 AED d'analyse et fait abandonner 12 % des clients sollicités, qui partent ailleurs. Question : demander les relevés à tous ?

**Données.**

- États : solvable (0,95) ou défaut (0,05).
- Utilités en AED : approuver un solvable +4 800 (marge nette), approuver un défaut −30 000 (perte après recouvrement), refuser 0.
- Relevés : Se = 0,70 (ils révèlent 70 % des futurs défauts), α = 0,10 (ils inquiètent à tort sur 10 % des solvables).
- Coût c = 200 AED ; taux d'abandon β = 0,12 ; volume 1 500 dossiers par mois.
- Conformité CBUAE du dossier : mensualités totales 6 200 AED ≤ 50 % × 15 000 = 7 500 AED ; 60 000 ≤ 20 × 15 000 = 300 000 AED ; durée 48 mois ≤ 48.

**Calcul pas à pas.**

**Étape 1.** Sans information : U(approuver) = 0,95 × 4 800 − 0,05 × 30 000 = 4 560 − 1 500 = 3 060 et U(refuser) = 0. On approuve. Le seuil de refus vaut 4 800 / (4 800 + 30 000) = 4 800 / 34 800 ≈ 0,13793.

$$
U(\text{approuver}) = 0{,}95 \times 4\,800 - 0{,}05 \times 30\,000 = 3\,060
$$

**Étape 2.** P(alerte) = 0,05 × 0,70 + 0,95 × 0,10 = 0,035 + 0,095 = 0,13. Bayes : P(défaut | alerte) = 0,035 / 0,13 ≈ 0,26923, au-dessus du seuil, donc on refuserait ; P(défaut | rien) = 0,015 / 0,87 ≈ 0,01724, en dessous, donc on approuverait. Le test fait bien basculer la décision.

**Étape 3.** Forme fermée (démonstration 4) avec g = 30 000 (défaut évité) et k = 4 800 (marge perdue sur un solvable refusé) :

$$
\operatorname{VOI} = 0{,}05 \times 0{,}70 \times 30\,000 - 0{,}95 \times 0{,}10 \times 4\,800 = 1\,050 - 456 = 594
$$

L'utilité attendue d'un dossier qui fournit ses relevés vaut donc 3 060 + 594 = 3 654 AED.

**Étape 4.** Coût caché : un client sollicité sur huit environ abandonne, et un abandon rapporte 0. Valeur de la demande, frais d'analyse déduits :

$$
(1 - 0{,}12) \times 3\,654 - 200 = 3\,215{,}52 - 200 = 3\,015{,}52
$$

**Étape 5.** On compare : 3 015,52 AED en demandant les relevés, contre 3 060 AED sans les demander.

**Décision de l'agent.** Ne pas demander les relevés systématiquement : l'agent approuve sur la base du certificat de salaire et des règles CBUAE. La VOI est réelle (594 AED), mais l'abandon qu'elle provoque coûte plus qu'elle ne rapporte.

**Contre-calcul.** La règle naïve « VOI 594 > coût 200, donc demander » ignore l'abandon. Elle donne 3 015,52 au lieu de 3 060 AED, soit une perte de 44,48 AED par dossier et de 1 500 × 44,48 = 66 720 AED par mois (illustratif).

**Sensibilité.** Valeur de bascule du taux d'abandon : (1 − β) × 3 654 − 200 = 3 060 ⟺ β = (594 − 200) / 3 654 = 394 / 3 654 ≈ 0,10783. Au-dessus de 10,8 % d'abandon, on ne demande pas ; en dessous, on demande. Si une collecte numérique des relevés, avec le consentement du client, ramène l'abandon à 5 % (illustratif), la demande vaut 0,95 × 3 654 − 200 = 3 471,3 − 200 = 3 271,3 > 3 060 : la décision s'inverse.

**En production.** On suit le taux d'abandon des clients sollicités, avec une alerte à 10,8 %, et le taux de défaut à 12 mois des dossiers approuvés sans relevés. Les règles CBUAE (ratio d'endettement total ≤ 50 % du salaire, prêt ≤ 20 fois le salaire, durée ≤ 48 mois) s'appliquent à chaque dossier, quelle que soit la VOI : le calcul ne porte que sur un document facultatif.

### Cas 3 — Promoteur à Dubaï : commander une étude de marché avant de fixer le prix d'une tour off-plan

**Contexte.** Un promoteur de Dubaï prépare le lancement d'une tour off-plan de 400 lots. L'agent de pricing doit choisir entre trois actions : lancer à 2 000 AED/sqft (« haut »), à 1 800 AED/sqft (« bas »), ou reporter le lancement de six mois. Un cabinet propose une étude de marché à 0,5 M AED. Les profits, en millions d'AED, et les probabilités sont illustratifs.

**Données.** Probabilités de la demande : forte 0,3 ; moyenne 0,5 ; faible 0,2.

| action | forte | moyenne | faible |
| --- | --- | --- | --- |
| haut (2 000 AED/sqft) | 30 | 12 | −10 |
| bas (1 800 AED/sqft) | 22 | 16 | −2 |
| reporter | 8 | 8 | 8 |

Vraisemblances de l'étude, P(résultat | demande) :

| demande | optimiste | neutre | pessimiste |
| --- | --- | --- | --- |
| forte | 0,7 | 0,2 | 0,1 |
| moyenne | 0,2 | 0,6 | 0,2 |
| faible | 0,1 | 0,2 | 0,7 |

**Calcul pas à pas.**

**Étape 1.** Sans information, moyenne de chaque ligne : haut 0,3 × 30 + 0,5 × 12 − 0,2 × 10 = 9 + 6 − 2 = 13 ; bas 0,3 × 22 + 0,5 × 16 − 0,2 × 2 = 6,6 + 8 − 0,4 = 14,2 ; reporter 8. On lancerait au prix bas, pour 14,2 M AED.

$$
\max_a U(a) = \max(13\ ;\ 14{,}2\ ;\ 8) = 14{,}2
$$

**Étape 2.** Plafond (démonstration 3) : maximum de chaque colonne, 30, 16 et 8, puis moyenne 0,3 × 30 + 0,5 × 16 + 0,2 × 8 = 9 + 8 + 1,6 = 18,6. VOI parfaite = 18,6 − 14,2 = 4,4 M AED, ce que confirme le regret : 0,3 × (30 − 22) + 0,2 × (8 − (−2)) = 2,4 + 2 = 4,4. Le plafond dépasse le prix de l'étude : elle mérite d'être examinée.

**Étape 3.** Probabilités jointes P(demande, résultat) = P(demande) × P(résultat | demande). Optimiste : 0,21 ; 0,10 ; 0,02, donc P(optimiste) = 0,33. Neutre : 0,06 ; 0,30 ; 0,04, donc P(neutre) = 0,40. Pessimiste : 0,03 ; 0,10 ; 0,14, donc P(pessimiste) = 0,27. Le total vaut 1.

**Étape 4.** Pour chaque résultat e, on calcule P(e) × U(a | e) = Σ P(ω, e) U(a, ω) sans diviser par P(e), puisqu'on remultiplierait par P(e) à l'étape suivante.

| résultat | haut | bas | reporter | choix |
| --- | --- | --- | --- | --- |
| optimiste | 6,3 + 1,2 − 0,2 = 7,3 | 4,62 + 1,6 − 0,04 = 6,18 | 0,33 × 8 = 2,64 | haut |
| neutre | 1,8 + 3,6 − 0,4 = 5,0 | 1,32 + 4,8 − 0,08 = 6,04 | 0,40 × 8 = 3,2 | bas |
| pessimiste | 0,9 + 1,2 − 1,4 = 0,7 | 0,66 + 1,6 − 0,28 = 1,98 | 0,27 × 8 = 2,16 | reporter |

**Étape 5.** On additionne les maxima de chaque ligne :

$$
\mathbb{E}[\max] = 7{,}3 + 6{,}04 + 2{,}16 = 15{,}5 \quad\Longrightarrow\quad \operatorname{VOI} = 15{,}5 - 14{,}2 = 1{,}3
$$

**Étape 6.** Gain net : 1,3 − 0,5 = 0,8 M AED.

**Décision de l'agent.** Commander l'étude, puis lancer au prix haut si elle est optimiste, au prix bas si elle est neutre, et reporter si elle est pessimiste : chaque résultat mène à une action différente, ce qui explique sa valeur.

**Contre-calcul.** Sans étude, le promoteur obtient 14,2 M AED au lieu de 15,5 − 0,5 = 15,0 M AED : 0,8 M AED de valeur attendue perdue. Un agent qui oublie l'option « reporter » trouve une VOI de 1,12 M AED (après un résultat pessimiste, il garderait le prix bas, 1,98 au lieu de 2,16) : il sous-estime l'étude de 0,18 M AED. Une étude « parfaite » proposée à 5 M AED se refuse sans calcul : aucune information ne vaut plus que le plafond de 4,4 M AED.

**Sensibilité.** La valeur de bascule sur le prix de l'étude est 1,3 M AED. Si la marge du prix haut en demande forte baisse de 10 % (30 → 27), la ligne optimiste devient 5,67 + 1,2 − 0,2 = 6,67 (toujours « haut »), la valeur sans information reste 14,2 (le prix haut vaut 8,1 + 6 − 2 = 12,1) et la VOI tombe à 0,67 M AED, soit −48 %. Elle reste au-dessus de 0,5 : la décision tient, mais de peu. La VOI est bien plus sensible que les profits eux-mêmes.

**En production.** On suit l'écart entre la demande annoncée par l'étude et les réservations des huit premières semaines, et l'on recalcule les vraisemblances de l'étude après chaque lancement. Les ventes off-plan à Dubaï sont enregistrées auprès du DLD, sous la régulation de la RERA, avec des fonds d'acheteurs placés sur des comptes séquestres ; les modalités précises sont à confirmer avec le texte en vigueur. L'agent fixe un prix de lancement, il ne conseille pas les acheteurs.

### Cas 4 — Cabinet RH multi-émirats : vérifier un diplôme avant de présenter un candidat

**Contexte.** Un cabinet RH présent à Dubaï, Abu Dhabi et Sharjah présente 300 candidats par mois à des employeurs, qui déposent ensuite la demande de permis de travail auprès du MOHRE (chiffres illustratifs). Avant de présenter un candidat, l'agent peut lancer une vérification automatique en ligne du diplôme et des expériences, puis, s'il le juge utile, une attestation officielle du diplôme. 6 % des dossiers sont non conformes. Question : quels contrôles lancer, et pour qui ?

**Données.**

- π = 0,06 (non conforme). Utilités en AED : présenter un conforme +9 000 (honoraires nets), présenter un non conforme −25 000 (remboursement, pénalité, permis perdu), écarter un conforme −1 500 (sourcing perdu), écarter un non conforme 0.
- Contrôle 1, vérification en ligne : Se = 0,80, α = 0,03, coût 120 AED.
- Contrôle 2, attestation : Se = 0,99, α = 0,01, coût 600 AED de frais plus 15 jours de délai valorisés à 40 AED par jour, soit 600 + 15 × 40 = 1 200 AED.

**Calcul pas à pas.**

**Étape 1.** Sans information : présenter vaut 0,94 × 9 000 − 0,06 × 25 000 = 8 460 − 1 500 = 6 960 et écarter vaut −0,94 × 1 500 = −1 410 : on présente. Les regrets valent g = 25 000 et k = 9 000 + 1 500 = 10 500, d'où le seuil π* = 10 500 / 35 500 ≈ 0,29577.

**Étape 2.** Contrôle 1. P(suspect) = 0,06 × 0,80 + 0,94 × 0,03 = 0,048 + 0,0282 = 0,0762. Après « suspect », π = 0,048 / 0,0762 ≈ 0,62992 > π* : on écarterait. Après « rien », π = 0,06 × 0,20 / 0,9238 = 0,012 / 0,9238 ≈ 0,01299 : on présente. Forme fermée :

$$
\operatorname{VOI}_1 = 0{,}06 \times 0{,}80 \times 25\,000 - 0{,}94 \times 0{,}03 \times 10\,500 = 1\,200 - 296{,}1 = 903{,}9
$$

903,9 > 120 : on lance le contrôle 1 pour tous.

**Étape 3.** Attestation après « rien » (π ≈ 0,01299, décision par défaut : présenter). Plafond (démonstration 5, branche gauche) : 25 000 × 0,01299 ≈ 324,75 AED, très en dessous de 1 200 : on s'arrête là, sans calculer Bayes. Pour mémoire, la VOI exacte vaut 0,01299 × 0,99 × 25 000 − 0,98701 × 0,01 × 10 500 ≈ 321,5 − 103,6 = 217,9 AED.

**Étape 4.** Attestation après « suspect » (π ≈ 0,62992, décision par défaut : écarter). Plafond : 10 500 × (1 − 0,62992) ≈ 3 885,8 AED > 1 200 : on calcule. Si l'attestation revient propre, la probabilité de non-conformité tombe à 0,0063 / 0,3727 ≈ 0,0169 < π* : on présenterait. La forme fermée s'écrit ici en sens inverse, car le test fait passer d'« écarter » à « présenter » :

$$
\operatorname{VOI}_2 = (1 - \pi)(1 - \alpha)\, k - \pi\,(1 - Se)\, g = 0{,}37008 \times 0{,}99 \times 10\,500 - 0{,}62992 \times 0{,}01 \times 25\,000 \approx 3\,847{,}0 - 157{,}5 = 3\,689{,}5
$$

**Décision de l'agent.** Contrôle 1 pour tous les candidats ; attestation seulement pour ceux que le contrôle 1 a signalés ; un candidat signalé dont l'attestation revient propre est présenté. La même attestation vaut 217,9 AED après un « rien » et 3 689,5 AED après un « suspect » : sa valeur dépend de la croyance de départ (démonstration 5).

**Contre-calcul.** Attestation pour tous : sur les 300 × 0,9238 candidats « rien » du mois, chacun coûte 1 200 − 217,9 ≈ 982,1 AED de plus qu'il ne rapporte, soit environ 272 190 AED par mois. Aucune attestation, avec rejet direct des suspects : on perd 3 689,5 − 1 200 = 2 489,5 AED sur chacun des 300 × 0,0762 = 22,86 suspects mensuels, soit environ 56 910 AED par mois (illustratif).

**Sensibilité.** Pour un candidat « rien », l'attestation deviendrait rentable si son risque résiduel π atteignait la valeur où π × 0,99 × 25 000 − (1 − π) × 0,01 × 10 500 = 1 200, soit π = 1 305 / 24 855 ≈ 0,05250 : environ quatre fois le risque actuel de 1,3 %. Un contrôle 1 qui se dégrade, et laisse passer plus de non-conformes, rapproche de cette bascule.

**En production.** On suit le taux de non-conformité découvert après placement, à comparer au risque résiduel prévu de 1,3 % ; l'alerte part au-dessus de 5,25 %, valeur où la politique d'attestation doit changer. Les exigences du MOHRE sur les permis de travail et sur l'attestation des diplômes selon le poste sont à confirmer avec le texte en vigueur ; les données des candidats relèvent de la PDPL hors DIFC et ADGM.

## Entraînement sur feuille A4

**Exercice 1.** Refaire l'exemple simple avec 50 % de fraudes. Quelle décision sans information ? Quelle VOI parfaite ?

**Exercice 2.** Retrouver le seuil de 27,3 % en résolvant U(valider) = U(refuser).

**Exercice 3.** Une vérification signale toujours « suspect », quelle que soit la demande. Que vaut-elle ? Pourquoi ?

**Exercice 4.** Dans le cas 1, vérifier P(fraude | s) = 0,81818 avec la formule de Bayes.

**Exercice 5.** Démontrer la démonstration 1 dans le cas de deux actions et deux résultats, sans regarder.

**Exercice 6 (cas modifié).** Dans le cas 2, la banque réduit le taux d'abandon à 8 %. Recalculer la valeur de la demande de relevés et donner la nouvelle décision.

**Exercice 7 (trouver l'erreur).** Un collègue écrit : « Sans information, l'agent vaut la moyenne de ses deux actions, (0 + (−40)) / 2 = −20. Avec l'information parfaite, il vaut 80. Donc VOI = 80 − (−20) = 100. » Trouver l'erreur et corriger.

**Exercice 8 (redémontrer de mémoire).** Démontrer que la VOI d'une information imparfaite ne dépasse jamais celle de l'information parfaite, puis calculer ce plafond pour l'attestation du cas 4 après un « rien ».

## Corrigé

**Exercice 1.** Sans information : U(valider) = 0,5 × 100 − 0,5 × 400 = 50 − 200 = −150 et U(refuser) = −0,5 × 50 = −25 : on refuse, valeur −25. Information parfaite : 0,5 × max(100 ; −50) + 0,5 × max(−400 ; 0) = 50 + 0 = 50. VOI = 50 − (−25) = 75. Contrôle par la démonstration 5 : π = 0,5 > π*, donc VOI = 150 × (1 − 0,5) = 75.

**Exercice 2.** 100(1 − f) − 400f = −50(1 − f). On passe tout à gauche : 150(1 − f) − 400f = 0, soit 150 − 550f = 0, d'où f = 150 / 550 ≈ 0,273.

**Exercice 3.** Elle ne vaut rien. Avec Se = 1 et α = 1, P(s) = 1 × π + 1 × (1 − π) = 1, et P(fraude | s) = π / 1 = π : la croyance ne bouge pas, la décision non plus, donc VOI = 0 (démonstration 2).

**Exercice 4.** Numérateur : 0,9 × 0,2 = 0,18. Dénominateur : 0,9 × 0,2 + 0,05 × 0,8 = 0,18 + 0,04 = 0,22. P(fraude | s) = 0,18 / 0,22 ≈ 0,81818.

**Exercice 5.** Pour chacun des deux résultats e₁ et e₂, le maximum des deux utilités dépasse celle de a*. On multiplie la première inégalité par P(e₁), la seconde par P(e₂), on additionne, et la somme de droite P(e₁) U(a* | e₁) + P(e₂) U(a* | e₂) vaut U(a*) par les probabilités totales. Donc 𝔼[max] ≥ U(a*) = max U(a).

**Exercice 6.** Valeur de la demande : (1 − 0,08) × 3 654 − 200 = 3 361,68 − 200 = 3 161,68 AED, contre 3 060 AED sans relevés. On demande désormais les relevés : gain de 101,68 AED par dossier. C'est cohérent avec la bascule : 8 % < 10,78 %.

**Exercice 7.** Sans information, l'agent ne tire pas son action au hasard : il choisit la meilleure, donc sa valeur est max(0 ; −40) = 0 et non −20. La bonne VOI parfaite vaut 80 − 0 = 80. L'erreur gonfle la VOI de 20 et ferait acheter une vérification à 90 AED qui n'en vaut que 80.

**Exercice 8.** On note δ(e) l'action choisie après e. 𝔼[max U(a | e)] = Σ P(ω, e) U(δ(e), ω) ≤ Σ P(ω, e) max U(a, ω) = Σ P(ω) max U(a, ω), parce que chaque terme est majoré par le maximum de son état et que la somme de P(ω, e) sur e vaut P(ω). On retranche max U(a). Application : après « rien », la décision par défaut est « présenter », donc le seul regret est sur un non conforme : plafond = 25 000 × 0,01299 ≈ 324,75 AED < 1 200 AED, on n'attestera pas.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`utilite(p_fraude, action)`** — Cette fonction est le gestionnaire de sinistres qui chiffre, en dirhams, ce que rapporte chaque décision selon le soupçon de fraude : elle reçoit la probabilité de fraude et le nom de l'action, refuse par une `ValueError` une probabilité hors de l'intervalle de 0 à 1, puis renvoie (1 − p) × 100 − p × 400 pour « valider », puisqu'un dossier honnête rapporte 100 et une fraude payée en coûte 400, ou −(1 − p) × 50 pour « refuser », qui fait perdre 50 sur un client honnête. Toute autre action lève une `ValueError` ; à p = 0,2, valider vaut 0 et refuser −40.

**`meilleure(p_fraude)`** — Cette petite fonction est le décideur pressé qui ne garde que la meilleure option : elle reçoit la probabilité de fraude, calcule l'utilité de chacune des deux actions de `ACTIONS`, valider et refuser, par `utilite`, et renvoie la plus grande des deux. Elle vaut 0 au départ, quand p = 0,2, puisque valider l'emporte sur les −40 du refus, et `voi` l'appelle pour chaque croyance mise à jour, avant et après le test, afin de mesurer ce que l'information fait gagner.

**`posterieurs(prior, sensibilite, fausse_alerte)`** — On la voit en détective qui révise son soupçon après avoir entendu le témoin : elle reçoit la probabilité de fraude a priori, la sensibilité du test et son taux de fausse alerte, refuse toute valeur hors de l'intervalle de 0 à 1 par une `ValueError`, puis calcule la probabilité d'un signal, Se × π + α × (1 − π), et les deux croyances révisées par la formule de Bayes. Elle renvoie ces trois nombres, en mettant `None` pour une branche impossible ; avec 0,2, 0,9 et 0,05, elle donne 0,22, 0,81818 et 0,02564.

**`voi(prior, sensibilite, fausse_alerte)`** — Cette fonction est le conseiller qui dit combien vaut une vérification avant même de la lancer : elle reçoit les mêmes trois probabilités, demande à `posterieurs` les croyances révisées, additionne pour chaque issue possible sa probabilité multipliée par la meilleure utilité qu'on obtient alors, puis retranche la meilleure utilité sans le test. Elle renvoie la valeur de l'information avec la probabilité du signal et les deux croyances : 66 AED pour le test du cas 1, 80 pour un test parfait, et 0 pour un détecteur trop faible pour faire changer d'avis.

**`voi_generale(probas, utilites, vraisemblances)`** — Celle-ci généralise le calcul à un monde de m états, k actions et r résultats, comme un stratège qui dresse le tableau de toutes les situations : elle reçoit les probabilités des états, les utilités de chaque action dans chaque état et les vraisemblances de chaque résultat sachant l'état, refuse des lignes de probabilités qui ne somment pas à 1, puis calcule la meilleure valeur sans test. Pour chaque résultat, elle forme les probabilités jointes, note `None` si le résultat est impossible, sinon calcule la valeur non normalisée de chaque action et garde la meilleure ; elle renvoie la VOI, les valeurs sans et avec test, les choix et le tableau des valeurs, soit 594 AED pour le cas 2 et 1,3 M AED pour le cas 3.

**`voi_parfaite(probas, utilites)`** — Cette fonction imagine un oracle qui révélerait l'état exact du monde : elle reçoit les probabilités des états et les utilités, construit une matrice de vraisemblances identité, où chaque état produit avec certitude son propre résultat, et la confie à `voi_generale`. Elle renvoie donc le même quintuplet, dont la première valeur est le plafond de toute information possible, 4,4 M AED dans le cas 3, que l'étude de marché, qui ne vaut que 1,3 M AED, ne peut pas dépasser.

**`proche(x, attendu, decimales)`** — Ce petit contrôleur compare deux nombres comme on compare deux lignes d'un registre arrondi : il reçoit une valeur calculée, la valeur attendue et un nombre de décimales, arrondit les deux à ce nombre de chiffres et renvoie vrai s'ils coïncident. Un nombre de décimales négatif arrondit aux dizaines, ce qui sert à vérifier les pertes de 272 190 et 56 910 AED du cas 4 ; tous les `assert` de `main` l'emploient pour confronter les résultats aux valeurs écrites dans la fiche.

**`demonstrations()`** — Cette fonction rejoue les cinq démonstrations de la fiche sur le cas du test de fraude : elle ne reçoit rien et vérifie d'abord la loi des espérances totales, les deux branches de « valider » valant −68 et 68, soit 0 au total, et le fait qu'obéir à un signal de pur bruit coûterait −20. Elle montre ensuite qu'un détecteur faible, de sensibilité 0,12 et de fausse alerte 0,10, ne fait basculer aucune décision et vaut 0, que la VOI de 66 reste sous le plafond parfait de 80, que la forme fermée donne 72 − 6 = 66, et que la VOI parfaite dessine un toit qui culmine à 109,09 au seuil 0,27273, avec une bande d'achat de 0,075 à 0,8 pour un test à 30 AED ; elle imprime et renvoie ces nombres.

**`exemple_simple()`** — Celle-ci raconte la scène de base, un dossier suspect à 20 % qu'un oracle parfait pourrait éclairer : elle ne reçoit rien, calcule les utilités sans information, 0 pour valider et −40 pour refuser, puis l'utilité avec l'oracle, 0,8 × 100 + 0,2 × 0 = 80, puisqu'on validerait les honnêtes et refuserait les fraudes. Elle en tire une VOI de 80 AED, un gain net de 50 AED si l'oracle coûte 30, imprime ces nombres et renvoie le quadruplet que `main` vérifie.

**`cas_1_assureur_sinistres()`** — Cette fonction met en scène un assureur dont l'agent trie 2 000 demandes de remboursement par mois, dont 20 % de fraudes, et peut lancer un outil de vérification croisée facturé 30 AED : elle ne reçoit rien, calcule un signal dans 22 % des cas, une croyance de 0,81818 après signal et de 0,02564 sans signal, et une VOI de 66 AED, soit 36 AED nets par dossier et 72 000 AED par mois. Elle détaille les utilités de chaque branche, refuser à −9,09 après un signal et valider à 87,18 sinon, calcule les bascules, un coût de 66 AED, une fausse alerte de 0,35 et une sensibilité de 0,45, la VOI de 58,8 si la sensibilité baisse de 10 % et la perte de 8 000 AED par mois d'un outil à 70 AED, puis renvoie le tout.

**`cas_2_banque_releves()`** — On y suit l'agent de pré-instruction d'une banque qui peut demander six mois de relevés d'un autre compte avant d'accorder un prêt : la fonction ne reçoit rien, pose 5 % de défauts, un gain de 4 800 AED sur un bon client et une perte de 30 000 sur un défaut, et des relevés qui donnent l'alerte pour 70 % des défauts et 10 % des clients solvables. Elle trouve une valeur sans relevés de 3 060 AED, une VOI de 594, des croyances de 0,26923 après alerte et de 0,01724 sinon, mais montre qu'avec 200 AED d'analyse et 12 % de clients qui abandonnent, demander les relevés à tous ne vaut que 3 015,52, soit 66 720 AED perdus par mois sur 1 500 dossiers ; elle calcule la bascule de 0,10783 sur l'abandon et la valeur 3 271,30 à 5 %, puis renvoie ces résultats.

**`cas_3_promoteur_etude()`** — Cette fonction raconte un promoteur qui prépare le lancement d'une tour et hésite entre un prix haut, un prix bas et un report, face à une demande forte, moyenne ou faible avec les probabilités 0,3, 0,5 et 0,2 : elle ne reçoit rien, calcule les valeurs sans étude, 13, 14,2 et 8 millions d'AED, donc le prix bas, puis la VOI parfaite de 4,4 M et celle d'une étude de marché imparfaite, 1,3 M, qui ferait choisir haut, bas ou report selon qu'elle est optimiste, neutre ou pessimiste. Elle en tire un gain net de 0,8 M pour une étude à 0,5 M, montre que la VOI tombe à 1,12 M sans l'option de report et à 0,67 M si la marge en demande forte baisse de 10 %, imprime et renvoie ces nombres.

**`cas_4_rh_diplomes()`** — Ici, un cabinet de recrutement présente 300 candidats par mois, dont 6 % de dossiers non conformes, et peut lancer une vérification automatique, puis une attestation officielle du diplôme à 1 200 AED : la fonction ne reçoit rien, calcule 6 960 AED pour présenter sans contrôle contre −1 410 pour écarter, puis une VOI de 903,9 pour la vérification automatique, qui signale 7,62 % des dossiers. Après un signal, la croyance monte à 0,62992 et l'attestation vaut 3 689,5 AED, plus que son coût ; sans signal, la croyance tombe à 0,01299 et l'attestation ne vaut que 217,9 AED, sous un plafond de 324,75. Elle chiffre les pertes évitées, 272 190 AED par mois face à l'attestation pour tous et 56 910 face à aucune, calcule la bascule 0,0525 et renvoie ces résultats.

**`valeurs(prior, se, alpha)`** — Cette fonction interne vit dans `cas_4_rh_diplomes`, comme le formulaire que l'agent remplit pour chaque contrôle envisagé : elle reçoit la probabilité qu'un dossier soit non conforme, la sensibilité du contrôle et son taux de fausse alerte, construit les utilités de présenter, 9 000 AED pour un dossier conforme et −25 000 pour un dossier non conforme, et d'écarter, −1 500 et 0, puis la matrice des vraisemblances des résultats « suspect » et « rien ». Elle renvoie le quintuplet de `voi_generale`, soit une VOI de 903,9 pour le premier contrôle et de 1 200 exactement pour l'attestation quand la croyance vaut 0,0525.

**`corrige()`** — Celle-ci est le correcteur qui refait au propre les exercices chiffrés : elle ne reçoit rien et calcule, pour un dossier suspect à 50 %, les utilités −150 et −25 et la VOI parfaite 75, puis le seuil 150/550 ≈ 0,273, la VOI nulle d'un test qui sonne toujours, la croyance 0,81818 après signal, la valeur 3 161,68 AED de la demande de relevés quand l'abandon tombe à 8 %, et la VOI fautive de 100 de l'exercice 7, qui fait la moyenne des actions au lieu de garder la meilleure. Elle imprime ces six résultats et les renvoie pour que `main` les vérifie.

**`main()`** — C'est le chef d'orchestre de la fiche : il appelle `demonstrations` et vérifie chacun de ses nombres, puis parcourt 101 croyances a priori de 0 à 1 pour contrôler que la VOI parfaite suit bien la forme en toit et que la VOI de trois détecteurs différents reste toujours entre 0 et ce plafond. Il enchaîne avec l'exemple simple, les quatre cas et le corrigé, puis s'assure qu'une probabilité de 1,2, une sensibilité de 1,5 ou une action « attendre » lèvent bien une `ValueError` ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tout concorde.

```python
"""Démonstration 28 — valeur de l'information : positivité, plafond parfait, forme fermée, quatre cas aux EAU."""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ACTIONS = ("valider", "refuser")


def utilite(p_fraude, action):
    """Utilité attendue (AED) d'une action quand la probabilité de fraude vaut p_fraude."""
    if not 0 <= p_fraude <= 1:
        raise ValueError("p_fraude doit être dans [0, 1]")
    if action == "valider":
        return (1 - p_fraude) * 100 - p_fraude * 400
    if action == "refuser":
        return -(1 - p_fraude) * 50
    raise ValueError("action inconnue : " + str(action))


def meilleure(p_fraude):
    return max(utilite(p_fraude, a) for a in ACTIONS)


def posterieurs(prior, sensibilite, fausse_alerte):
    """P(signal), P(fraude | signal), P(fraude | pas de signal) ; None si la branche est impossible."""
    for x in (prior, sensibilite, fausse_alerte):
        if not 0 <= x <= 1:
            raise ValueError("probabilité hors de [0, 1]")
    p_s = sensibilite * prior + fausse_alerte * (1 - prior)
    p_f_s = sensibilite * prior / p_s if p_s > 0 else None
    p_f_n = (1 - sensibilite) * prior / (1 - p_s) if p_s < 1 else None
    return p_s, p_f_s, p_f_n


def voi(prior, sensibilite, fausse_alerte):
    """VOI d'un test à deux issues (signal, pas de signal) pour la décision valider / refuser."""
    p_s, p_f_s, p_f_n = posterieurs(prior, sensibilite, fausse_alerte)
    avec = 0.0
    if p_f_s is not None:
        avec += p_s * meilleure(p_f_s)
    if p_f_n is not None:
        avec += (1 - p_s) * meilleure(p_f_n)
    return avec - meilleure(prior), p_s, p_f_s, p_f_n


def voi_generale(probas, utilites, vraisemblances):
    """VOI pour m états, k actions et r résultats du test.

    probas[j] = P(état j) ; utilites[a][j] = U(a, état j) ; vraisemblances[j][e] = P(résultat e | état j).
    Renvoie (voi, sans, avec, choix, valeurs) : choix[e] est l'action retenue après le résultat e
    (None si P(e) = 0) et valeurs[e][a] = P(e) × U(a | e), la somme non normalisée.
    """
    if abs(sum(probas) - 1) > 1e-9 or any(abs(sum(v) - 1) > 1e-9 for v in vraisemblances):
        raise ValueError("les probabilités doivent sommer à 1")
    actions = list(utilites)
    sans = max(sum(p * utilites[a][j] for j, p in enumerate(probas)) for a in actions)
    avec, choix, tableau = 0.0, [], []
    for e in range(len(vraisemblances[0])):
        jointes = [probas[j] * vraisemblances[j][e] for j in range(len(probas))]
        if sum(jointes) == 0:
            choix.append(None)
            tableau.append({})
            continue
        valeurs = {a: sum(q * utilites[a][j] for j, q in enumerate(jointes)) for a in actions}
        meilleur = max(actions, key=lambda a: valeurs[a])
        avec += valeurs[meilleur]
        choix.append(meilleur)
        tableau.append(valeurs)
    return avec - sans, sans, avec, choix, tableau


def voi_parfaite(probas, utilites):
    n = len(probas)
    identite = [[1.0 if e == j else 0.0 for e in range(n)] for j in range(n)]
    return voi_generale(probas, utilites, identite)


def proche(x, attendu, decimales):
    return round(x, decimales) == round(attendu, decimales)


def demonstrations():
    print("Démonstrations")
    v, p_s, p_f_s, p_f_n = voi(0.2, 0.9, 0.05)
    branche_s, branche_n = p_s * utilite(p_f_s, "valider"), (1 - p_s) * utilite(p_f_n, "valider")
    bruit = 0.5 * utilite(0.2, "refuser") + 0.5 * utilite(0.2, "valider")      # obéir à un signal pur bruit
    print(f"  D1 E_e[U(valider|e)] = {branche_s:.2f} + {branche_n:.2f} = {branche_s + branche_n:.2f} ;"
          f" suivre un bruit : {bruit:.1f}")
    v2, p_s2, p_f_s2, p_f_n2 = voi(0.2, 0.12, 0.10)
    print(f"  D2 détecteur faible : P(s) {p_s2:.3f} ; P(f|s) {p_f_s2:.5f} ; P(f|non s) {p_f_n2:.5f} ;"
          f" VOI {abs(v2):.1f}")
    parfaite = voi(0.2, 1.0, 0.0)[0]
    print(f"  D3 VOI imparfaite {v:.1f} <= VOI parfaite {parfaite:.1f}")
    gain, perte = 0.2 * 0.9 * 400, 0.8 * 0.05 * 150
    politique_faible = 0.2 * 0.12 * 400 - 0.8 * 0.10 * 150
    print(f"  D4 forme fermée : {gain:.1f} - {perte:.1f} = {gain - perte:.1f} ;"
          f" détecteur faible forcé : {politique_faible:.1f}")
    seuil = 150 / 550
    sommet = voi(seuil, 1.0, 0.0)[0]
    bande = (30 / 400, 1 - 30 / 150)
    print(f"  D5 VOI parfaite : 0.2 -> {parfaite:.1f} ; 0.5 -> {voi(0.5, 1.0, 0.0)[0]:.1f} ;"
          f" seuil {seuil:.5f} -> {sommet:.2f} ; bande d'achat à 30 AED [{bande[0]:.3f} ; {bande[1]:.1f}]")
    return {"v": v, "p_s": p_s, "p_f_s": p_f_s, "p_f_n": p_f_n, "branche_s": branche_s, "branche_n": branche_n,
            "bruit": bruit, "v2": v2, "p_s2": p_s2, "p_f_s2": p_f_s2, "p_f_n2": p_f_n2, "parfaite": parfaite,
            "gain": gain, "perte": perte, "faible": politique_faible, "seuil": seuil, "sommet": sommet,
            "bande": bande}


def exemple_simple():
    sans_v, sans_r = utilite(0.2, "valider"), utilite(0.2, "refuser")
    avec = 0.8 * max(100, -50) + 0.2 * max(-400, 0)
    valeur = avec - max(sans_v, sans_r)
    print(f"Exemple simple : valider {sans_v:.1f}, refuser {sans_r:.1f} ; E[max] {avec:.1f} ;"
          f" VOI {valeur:.1f} ; net à 30 AED : {valeur - 30:.1f}")
    return sans_v, sans_r, avec, valeur


def cas_1_assureur_sinistres():
    v, p_s, p_f_s, p_f_n = voi(0.2, 0.9, 0.05)
    u = {(b, a): utilite(p, a) for b, p in (("s", p_f_s), ("n", p_f_n)) for a in ACTIONS}
    morceaux = ((1 - p_f_s) * 100, p_f_s * 400, (1 - p_f_n) * 100, p_f_n * 400)
    par_dossier = v - 30
    mensuel = 2000 * par_dossier
    perte_70 = 2000 * (70 - v)
    bascule_alpha = (0.2 * 0.9 * 400 - 30) / (0.8 * 150)
    bascule_se = (30 + 0.8 * 0.05 * 150) / (0.2 * 400)
    v_se_moins10 = voi(0.2, 0.81, 0.05)[0]
    print(f"Cas 1 : P(s) {p_s:.2f} ; P(f|s) {p_f_s:.5f} ; P(f|n) {p_f_n:.5f} ; VOI {v:.2f} ;"
          f" net {par_dossier:.2f} AED/dossier, {mensuel:.0f} AED/mois")
    print(f"  si signal : valider {u['s', 'valider']:.2f}, refuser {u['s', 'refuser']:.2f} ;"
          f" sinon : valider {u['n', 'valider']:.2f}, refuser {u['n', 'refuser']:.2f}")
    print(f"  bascules : coût {v:.0f} AED, alpha {bascule_alpha:.2f}, Se {bascule_se:.2f} ;"
          f" Se -10 % -> VOI {v_se_moins10:.1f} ; perte à 70 AED : {perte_70:.0f} AED/mois")
    return {"v": v, "p_s": p_s, "p_f_s": p_f_s, "p_f_n": p_f_n, "u": u, "morceaux": morceaux,
            "net": par_dossier, "mensuel": mensuel, "perte_70": perte_70, "bascule_alpha": bascule_alpha,
            "bascule_se": bascule_se, "v_se": v_se_moins10}


def cas_2_banque_releves():
    probas = [0.95, 0.05]                                 # solvable, défaut
    u = {"approuver": [4800, -30000], "refuser": [0, 0]}
    vrais = [[0.10, 0.90], [0.70, 0.30]]                  # P(alerte), P(rien) sachant l'état
    v, sans, avec, choix, _ = voi_generale(probas, u, vrais)
    seuil = 4800 / (4800 + 30000)
    p_alerte = 0.05 * 0.70 + 0.95 * 0.10
    p_d_alerte = 0.05 * 0.70 / p_alerte
    p_d_rien = 0.05 * 0.30 / (1 - p_alerte)
    valeur_demande = (1 - 0.12) * avec - 200
    bascule_abandon = (v - 200) / avec
    valeur_5 = (1 - 0.05) * avec - 200
    perte_mensuelle = 1500 * (sans - valeur_demande)
    print(f"Cas 2 : sans {sans:.0f} ; seuil {seuil:.5f} ; P(alerte) {p_alerte:.2f} ; P(d|alerte) {p_d_alerte:.5f} ;"
          f" P(d|rien) {p_d_rien:.5f} ; VOI {v:.0f} ; choix {choix}")
    print(f"  demander (abandon 12 %) : {valeur_demande:.2f} contre {sans:.0f} ; bascule abandon {bascule_abandon:.5f} ;"
          f" abandon 5 % : {valeur_5:.2f} ; perte naïve {perte_mensuelle:.0f} AED/mois")
    return {"v": v, "sans": sans, "avec": avec, "choix": choix, "seuil": seuil, "p_alerte": p_alerte,
            "p_d_alerte": p_d_alerte, "p_d_rien": p_d_rien, "valeur_demande": valeur_demande,
            "bascule": bascule_abandon, "valeur_5": valeur_5, "perte": perte_mensuelle}


def cas_3_promoteur_etude():
    probas = [0.3, 0.5, 0.2]                              # demande forte, moyenne, faible
    u = {"haut": [30, 12, -10], "bas": [22, 16, -2], "reporter": [8, 8, 8]}   # millions d'AED
    vrais = [[0.7, 0.2, 0.1], [0.2, 0.6, 0.2], [0.1, 0.2, 0.7]]               # optimiste, neutre, pessimiste
    v, sans, avec, choix, tableau = voi_generale(probas, u, vrais)
    vp, _, avec_p, choix_p, _ = voi_parfaite(probas, u)
    sans_par_action = {a: sum(p * u[a][j] for j, p in enumerate(probas)) for a in u}
    jointes = [[probas[j] * vrais[j][e] for j in range(3)] for e in range(3)]
    p_res = [sum(ligne) for ligne in jointes]
    sans_reporter = voi_generale(probas, {k: u[k] for k in ("haut", "bas")}, vrais)[0]
    u_moins = {"haut": [27, 12, -10], "bas": [22, 16, -2], "reporter": [8, 8, 8]}
    v_moins = voi_generale(probas, u_moins, vrais)[0]
    print(f"Cas 3 : sans {sans:.1f} M ; VOI parfaite {vp:.1f} M ; P(résultats) {[round(x, 2) for x in p_res]} ;"
          f" E[max] {avec:.1f} M ; VOI {v:.1f} M ; choix {choix}")
    print(f"  net {v - 0.5:.1f} M ; sans l'option reporter : VOI {sans_reporter:.2f} M ;"
          f" marge forte -10 % : VOI {v_moins:.2f} M ({(v_moins - v) / v:.0%})")
    return {"v": v, "sans": sans, "avec": avec, "choix": choix, "vp": vp, "avec_p": avec_p, "choix_p": choix_p,
            "sans_par_action": sans_par_action, "jointes": jointes, "p_res": p_res, "tableau": tableau,
            "sans_reporter": sans_reporter, "v_moins": v_moins}


def cas_4_rh_diplomes():
    def valeurs(prior, se, alpha):
        u = {"presenter": [9000, -25000], "ecarter": [-1500, 0]}            # conforme, non conforme
        return voi_generale([1 - prior, prior], u, [[alpha, 1 - alpha], [se, 1 - se]])

    prior = 0.06
    sans_p = 0.94 * 9000 - 0.06 * 25000
    sans_e = -0.94 * 1500
    seuil = 10500 / 35500
    v1, _, _, choix1, _ = valeurs(prior, 0.80, 0.03)
    p_s1 = 0.06 * 0.80 + 0.94 * 0.03
    pi_suspect = 0.06 * 0.80 / p_s1
    pi_rien = 0.06 * 0.20 / (1 - p_s1)
    plafond_rien = 25000 * pi_rien
    plafond_suspect = 10500 * (1 - pi_suspect)
    v2_rien, _, _, choix_rien, _ = valeurs(pi_rien, 0.99, 0.01)
    v2_suspect, _, _, choix_suspect, _ = valeurs(pi_suspect, 0.99, 0.01)
    morceaux_rien = (pi_rien * 0.99 * 25000, (1 - pi_rien) * 0.01 * 10500)
    morceaux_suspect = ((1 - pi_suspect) * 0.99 * 10500, pi_suspect * 0.01 * 25000)
    pi_propre = pi_suspect * 0.01 / (pi_suspect * 0.01 + (1 - pi_suspect) * 0.99)
    cout2 = 600 + 15 * 40
    perte_tous = 300 * (1 - p_s1) * (cout2 - v2_rien)
    perte_aucun = 300 * p_s1 * (v2_suspect - cout2)
    bascule_pi = (cout2 + 0.01 * 10500) / (0.99 * 25000 + 0.01 * 10500)
    print(f"Cas 4 : présenter {sans_p:.0f}, écarter {sans_e:.0f} ; seuil {seuil:.5f} ; VOI contrôle 1 {v1:.1f} ;"
          f" P(suspect) {p_s1:.4f} ; pi suspect {pi_suspect:.5f} ; pi rien {pi_rien:.5f}")
    print(f"  attestation ({cout2} AED) : après rien plafond {plafond_rien:.2f}, VOI {v2_rien:.1f} ;"
          f" après suspect plafond {plafond_suspect:.1f}, VOI {v2_suspect:.1f}, pi si propre {pi_propre:.5f}")
    print(f"  pertes évitées : attestation pour tous {perte_tous:.0f} AED/mois ; aucune attestation"
          f" {perte_aucun:.0f} AED/mois ; bascule après rien pi = {bascule_pi:.5f}")
    return {"sans_p": sans_p, "sans_e": sans_e, "seuil": seuil, "v1": v1, "choix1": choix1, "p_s1": p_s1,
            "pi_suspect": pi_suspect, "pi_rien": pi_rien, "plafond_rien": plafond_rien,
            "plafond_suspect": plafond_suspect, "v2_rien": v2_rien, "v2_suspect": v2_suspect,
            "choix_rien": choix_rien, "choix_suspect": choix_suspect, "cout2": cout2,
            "morceaux_rien": morceaux_rien, "morceaux_suspect": morceaux_suspect, "pi_propre": pi_propre,
            "perte_tous": perte_tous, "perte_aucun": perte_aucun, "bascule_pi": bascule_pi,
            "valeurs": valeurs}


def corrige():
    e1 = (utilite(0.5, "valider"), utilite(0.5, "refuser"), voi(0.5, 1.0, 0.0)[0])
    e2 = 150 / 550
    e3 = voi(0.2, 1.0, 1.0)[0]
    e4 = 0.9 * 0.2 / (0.9 * 0.2 + 0.05 * 0.8)
    e6 = (1 - 0.08) * 3654 - 200
    e7_faux = 80 - (0 + -40) / 2
    print(f"Corrigé : ex1 {e1[0]:.0f} / {e1[1]:.0f} / VOI {e1[2]:.0f} ; ex2 {e2:.3f} ; ex3 {e3:.1f} ; ex4 {e4:.5f} ;"
          f" ex6 {e6:.2f} ; ex7 faux {e7_faux:.0f}")
    return e1, e2, e3, e4, e6, e7_faux


def main() -> None:
    d = demonstrations()
    assert proche(d["p_s"], 0.22, 2) and proche(d["p_f_s"], 0.81818, 5) and proche(d["p_f_n"], 0.02564, 5)
    assert proche(d["branche_s"], -68.0, 6) and proche(d["branche_n"], 68.0, 6)
    assert abs(d["branche_s"] + d["branche_n"] - utilite(0.2, "valider")) < 1e-9          # D1 : tour de l'espérance
    assert d["bruit"] == -20 and d["v"] >= 0                                                # D1 : contre-exemple
    assert proche(0.12 * 0.2, 0.024, 9) and proche(0.10 * 0.8, 0.080, 9) and proche(0.88 * 0.2, 0.176, 9)
    assert proche(1 - 0.104, 0.896, 9) and proche(0.12 / 0.10, 1.2, 9)
    assert proche(d["p_s2"], 0.104, 3) and proche(d["p_f_s2"], 0.23077, 5) and proche(d["p_f_n2"], 0.19643, 5)
    assert abs(d["v2"]) < 1e-9 and d["p_f_s2"] < d["seuil"]                                 # D2 : rien ne bascule
    assert proche(d["parfaite"], 80, 6) and proche(d["v"], 66, 6) and 0 <= d["v"] <= d["parfaite"]   # D3
    assert proche(d["gain"], 72, 6) and proche(d["perte"], 6, 6) and proche(d["gain"] - d["perte"], d["v"], 9)
    assert proche(d["faible"], -2.4, 9) and proche(0.2 * 0.12 * 400, 9.6, 9)               # D4 : hypothèse
    assert proche(0.2 * 400 / 100, 0.8, 9) and proche(0.8 * 150 / 100, 1.2, 9)             # D4 : pentes
    assert proche(d["seuil"], 0.27273, 5) and proche(d["sommet"], 109.09, 2) and proche(d["sommet"], 1200 / 11, 9)
    assert proche(400 * 3 / 11, 150 * 8 / 11, 9) and proche(voi(0.5, 1.0, 0.0)[0], 75, 9)
    assert proche(voi(0.21, 1.0, 0.0)[0] - voi(0.2, 1.0, 0.0)[0], 4, 9)                   # D5 : +1 point -> +4
    assert proche(d["bande"][0], 0.075, 9) and proche(d["bande"][1], 0.8, 9)
    for pi in [k / 100 for k in range(101)]:                                                # D5 : forme en toit
        attendu = 400 * pi if pi <= d["seuil"] else 150 * (1 - pi)
        assert abs(voi(pi, 1.0, 0.0)[0] - attendu) < 1e-9
        for se, alpha in ((0.9, 0.05), (0.6, 0.3), (0.12, 0.1)):
            assert -1e-9 <= voi(pi, se, alpha)[0] <= voi(pi, 1.0, 0.0)[0] + 1e-9           # D1 et D3

    sv, sr, avec, valeur = exemple_simple()
    assert sv == 0 and sr == -40 and avec == 80 and valeur == 80 and valeur - 30 == 50
    assert 0.8 * 100 == 80 and 0.2 * 400 == 80 and 0.8 * 50 == 40

    c1 = cas_1_assureur_sinistres()
    assert proche(0.9 * 0.2, 0.18, 9) and proche(0.05 * 0.8, 0.04, 9) and proche(0.1 * 0.2, 0.02, 9)
    assert proche(1 - c1["p_s"], 0.78, 9) and proche(1 - c1["p_f_s"], 0.18182, 5) and proche(1 - c1["p_f_n"], 0.97436, 5)
    assert [round(x, 2) for x in c1["morceaux"]] == [18.18, 327.27, 97.44, 10.26]
    assert proche(c1["u"]["s", "valider"], -309.09, 2) and proche(c1["u"]["s", "refuser"], -9.09, 2)
    assert proche(c1["u"]["n", "valider"], 87.18, 2) and proche(c1["u"]["n", "refuser"], -48.72, 2)
    assert proche(0.22 * c1["u"]["s", "refuser"], -2.0, 6) and proche(0.78 * c1["u"]["n", "valider"], 68.0, 6)
    assert proche(c1["net"], 36, 6) and proche(c1["mensuel"], 72000, 3) and proche(c1["perte_70"], 8000, 3)
    assert proche(70 - c1["v"], 4, 6)
    assert proche(c1["bascule_alpha"], 0.35, 9) and proche(c1["bascule_se"], 0.45, 9)
    assert proche(42 / 120, 0.35, 9) and proche(72 - 120 * 0.05, 66, 9) and proche(80 * 0.9 - 6, 66, 9)
    assert proche(voi(0.2, 0.9, 0.35)[0], 30, 9) and proche(voi(0.2, 0.45, 0.05)[0], 30, 9)  # bascules exactes
    assert proche(c1["v_se"], 58.8, 6) and proche(80 * 0.81, 64.8, 9)

    c2 = cas_2_banque_releves()
    assert proche(0.95 * 4800, 4560, 9) and proche(0.05 * 30000, 1500, 9) and 4800 + 30000 == 34800
    assert proche(c2["sans"], 3060, 6) and proche(c2["seuil"], 0.13793, 5) and proche(c2["p_alerte"], 0.13, 9)
    assert proche(0.05 * 0.70, 0.035, 9) and proche(0.95 * 0.10, 0.095, 9) and proche(0.05 * 0.30, 0.015, 9)
    assert proche(1 - c2["p_alerte"], 0.87, 9)
    assert proche(c2["p_d_alerte"], 0.26923, 5) and proche(c2["p_d_rien"], 0.01724, 5)
    assert c2["p_d_alerte"] > c2["seuil"] > c2["p_d_rien"]
    assert proche(c2["v"], 594, 6) and proche(c2["avec"], 3654, 6) and c2["choix"] == ["refuser", "approuver"]
    assert proche(0.05 * 0.70 * 30000, 1050, 6) and proche(0.95 * 0.10 * 4800, 456, 6)
    assert proche(0.88 * 3654, 3215.52, 6) and proche(c2["v"] - 200, 394, 6)
    assert proche(c2["valeur_demande"], 3015.52, 2) and c2["valeur_demande"] < c2["sans"]
    assert proche(c2["sans"] - c2["valeur_demande"], 44.48, 2) and proche(c2["perte"], 66720, 2)
    assert proche(c2["bascule"], 0.10783, 5) and proche(0.95 * 3654, 3471.3, 6)
    assert proche(c2["valeur_5"], 3271.3, 2) and c2["valeur_5"] > c2["sans"]
    assert 6200 <= 0.5 * 15000 == 7500 and 60000 <= 20 * 15000 == 300000                   # règles CBUAE du dossier

    c3 = cas_3_promoteur_etude()
    assert {a: round(x, 9) for a, x in c3["sans_par_action"].items()} == {"haut": 13, "bas": 14.2, "reporter": 8}
    assert [round(x, 9) for x in (0.3 * 30, 0.5 * 12, 0.2 * 10, 0.3 * 22, 0.5 * 16, 0.2 * 2)] == [9, 6, 2, 6.6, 8, 0.4]
    assert proche(c3["sans"], 14.2, 9) and proche(c3["vp"], 4.4, 9) and proche(c3["avec_p"], 18.6, 9)
    assert c3["choix_p"] == ["haut", "bas", "reporter"] and proche(0.2 * 8, 1.6, 9)
    assert proche(0.3 * (30 - 22) + 0.2 * (8 - -2), 4.4, 9)                                  # plafond par le regret
    assert [[round(x, 9) for x in ligne] for ligne in c3["jointes"]] == [[0.21, 0.10, 0.02], [0.06, 0.30, 0.04],
                                                                        [0.03, 0.10, 0.14]]
    assert [round(x, 2) for x in c3["p_res"]] == [0.33, 0.40, 0.27]
    attendu = [{"haut": 7.3, "bas": 6.18, "reporter": 2.64}, {"haut": 5.0, "bas": 6.04, "reporter": 3.2},
               {"haut": 0.7, "bas": 1.98, "reporter": 2.16}]
    assert [{a: round(x, 9) for a, x in t.items()} for t in c3["tableau"]] == attendu
    produits = (0.21 * 30, 0.10 * 12, 0.02 * 10, 0.21 * 22, 0.10 * 16, 0.02 * 2, 0.06 * 30, 0.30 * 12, 0.04 * 10,
                0.06 * 22, 0.30 * 16, 0.04 * 2, 0.03 * 30, 0.10 * 12, 0.14 * 10, 0.03 * 22, 0.10 * 16, 0.14 * 2)
    assert [round(x, 9) for x in produits] == [6.3, 1.2, 0.2, 4.62, 1.6, 0.04, 1.8, 3.6, 0.4, 1.32, 4.8, 0.08,
                                               0.9, 1.2, 1.4, 0.66, 1.6, 0.28]
    assert proche(c3["avec"], 15.5, 9) and proche(c3["v"], 1.3, 9) and c3["choix"] == ["haut", "bas", "reporter"]
    assert proche(c3["v"] - 0.5, 0.8, 9) and proche(c3["sans_reporter"], 1.12, 9)
    assert proche(c3["v"] - c3["sans_reporter"], 0.18, 9) and proche(c3["avec"] - 0.5, 15.0, 9)
    assert proche(c3["v_moins"], 0.67, 9) and round((c3["v_moins"] - c3["v"]) / c3["v"] * 100) == -48
    assert proche(0.21 * 27, 5.67, 9) and proche(0.3 * 27 + 6 - 2, 12.1, 9) and proche(5.67 + 1.2 - 0.2, 6.67, 9)

    c4 = cas_4_rh_diplomes()
    assert proche(0.94 * 9000, 8460, 9) and proche(0.94 * 1500, 1410, 9) and 9000 + 1500 == 10500
    assert proche(c4["sans_p"], 6960, 6) and proche(c4["sans_e"], -1410, 6) and proche(c4["seuil"], 0.29577, 5)
    assert proche(0.06 * 0.8 * 25000, 1200, 9) and proche(0.94 * 0.03 * 10500, 296.1, 9)
    assert proche(c4["v1"], 903.9, 6) and c4["choix1"] == ["ecarter", "presenter"]
    assert proche(0.06 * 0.80, 0.048, 9) and proche(0.94 * 0.03, 0.0282, 9) and proche(1 - c4["p_s1"], 0.9238, 9)
    assert proche(c4["p_s1"], 0.0762, 9) and proche(c4["pi_suspect"], 0.62992, 5) and proche(c4["pi_rien"], 0.01299, 5)
    assert proche(0.06 * 0.20, 0.012, 9)
    assert c4["cout2"] == 1200 and proche(c4["plafond_rien"], 324.75, 2) and proche(c4["v2_rien"], 217.9, 1)
    assert [round(x, 1) for x in c4["morceaux_rien"]] == [321.5, 103.6] and proche(1 - c4["pi_rien"], 0.98701, 5)
    assert proche(c4["plafond_suspect"], 3885.8, 1) and proche(c4["v2_suspect"], 3689.5, 1)
    assert [round(x, 1) for x in c4["morceaux_suspect"]] == [3847.0, 157.5] and proche(1 - c4["pi_suspect"], 0.37008, 5)
    assert proche(c4["pi_propre"], 0.0169, 4) and c4["pi_propre"] < c4["seuil"]
    numerateur = c4["pi_suspect"] * 0.01
    assert proche(numerateur, 0.0063, 4) and proche(numerateur + (1 - c4["pi_suspect"]) * 0.99, 0.3727, 4)
    assert proche(c4["cout2"] - c4["v2_rien"], 982.1, 1) and proche(c4["v2_suspect"] - c4["cout2"], 2489.5, 1)
    assert proche(300 * c4["p_s1"], 22.86, 9) and proche(c4["bascule_pi"], 1305 / 24855, 12)
    assert c4["v2_rien"] < c4["cout2"] < c4["v2_suspect"] and c4["choix_suspect"] == ["ecarter", "presenter"]
    assert proche(c4["perte_tous"], 272190, -1) and proche(c4["perte_aucun"], 56910, -1)
    assert proche(c4["bascule_pi"], 0.05250, 5) and proche(c4["valeurs"](c4["bascule_pi"], 0.99, 0.01)[0], 1200, 6)
    assert proche(c4["bascule_pi"] / c4["pi_rien"], 4, 0)

    e1, e2, e3, e4, e6, e7 = corrige()
    assert e1 == (-150, -25, 75) and proche(e2, 0.273, 3) and abs(e3) < 1e-12 and proche(e4, 0.81818, 5)
    assert proche(0.92 * 3654, 3361.68, 6) and proche(e6, 3161.68, 2) and e6 > c2["sans"] and e7 == 100
    assert proche(e6 - c2["sans"], 101.68, 2)
    for mauvais in (lambda: utilite(1.2, "valider"), lambda: voi(0.2, 1.5, 0.1), lambda: utilite(0.2, "attendre")):
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
  D1 E_e[U(valider|e)] = -68.00 + 68.00 = 0.00 ; suivre un bruit : -20.0
  D2 détecteur faible : P(s) 0.104 ; P(f|s) 0.23077 ; P(f|non s) 0.19643 ; VOI 0.0
  D3 VOI imparfaite 66.0 <= VOI parfaite 80.0
  D4 forme fermée : 72.0 - 6.0 = 66.0 ; détecteur faible forcé : -2.4
  D5 VOI parfaite : 0.2 -> 80.0 ; 0.5 -> 75.0 ; seuil 0.27273 -> 109.09 ; bande d'achat à 30 AED [0.075 ; 0.8]
Exemple simple : valider 0.0, refuser -40.0 ; E[max] 80.0 ; VOI 80.0 ; net à 30 AED : 50.0
Cas 1 : P(s) 0.22 ; P(f|s) 0.81818 ; P(f|n) 0.02564 ; VOI 66.00 ; net 36.00 AED/dossier, 72000 AED/mois
  si signal : valider -309.09, refuser -9.09 ; sinon : valider 87.18, refuser -48.72
  bascules : coût 66 AED, alpha 0.35, Se 0.45 ; Se -10 % -> VOI 58.8 ; perte à 70 AED : 8000 AED/mois
Cas 2 : sans 3060 ; seuil 0.13793 ; P(alerte) 0.13 ; P(d|alerte) 0.26923 ; P(d|rien) 0.01724 ; VOI 594 ; choix ['refuser', 'approuver']
  demander (abandon 12 %) : 3015.52 contre 3060 ; bascule abandon 0.10783 ; abandon 5 % : 3271.30 ; perte naïve 66720 AED/mois
Cas 3 : sans 14.2 M ; VOI parfaite 4.4 M ; P(résultats) [0.33, 0.4, 0.27] ; E[max] 15.5 M ; VOI 1.3 M ; choix ['haut', 'bas', 'reporter']
  net 0.8 M ; sans l'option reporter : VOI 1.12 M ; marge forte -10 % : VOI 0.67 M (-48%)
Cas 4 : présenter 6960, écarter -1410 ; seuil 0.29577 ; VOI contrôle 1 903.9 ; P(suspect) 0.0762 ; pi suspect 0.62992 ; pi rien 0.01299
  attestation (1200 AED) : après rien plafond 324.75, VOI 217.9 ; après suspect plafond 3885.8, VOI 3689.5, pi si propre 0.01690
  pertes évitées : attestation pour tous 272190 AED/mois ; aucune attestation 56910 AED/mois ; bascule après rien pi = 0.05250
Corrigé : ex1 -150 / -25 / VOI 75 ; ex2 0.273 ; ex3 0.0 ; ex4 0.81818 ; ex6 3161.68 ; ex7 faux 100
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme calcule ce que vaut une vérification avant de décider : l'utilité attendue avec l'information, moins l'utilité sans elle, puis la compare au coût de la vérification.

```text
ALGORITHME ValeurDeLInformation
ENTRÉES : probabilités P(ω) des m états, utilités U(a, ω) des k actions,
          vraisemblances P(e | ω) des r résultats du test, coût c
SORTIE  : VOI ≥ 0, et « vérifier » ou l'action à jouer tout de suite

  sans ← max sur a de Σ_ω P(ω) × U(a, ω)
  avec ← 0
  POUR chaque résultat e FAIRE
      jointe(ω) ← P(ω) × P(e | ω)                 (Bayes non normalisé)
      SI Σ_ω jointe(ω) = 0 ALORS passer au résultat suivant
      avec ← avec + max sur a de Σ_ω jointe(ω) × U(a, ω)
  FIN POUR
  VOI ← avec − sans
  SI VOI > c ALORS RETOURNER VOI, « vérifier »
  RETOURNER VOI, argmax sur a de Σ_ω P(ω) × U(a, ω)

CAS PARTICULIER (deux états, deux actions, le test fait basculer la décision)
  VOI ← π × Se × g − (1 − π) × α × k
```

**Complexité.** O(m × k) pour la valeur sans information et O(r × m × k) pour la valeur avec information : pour un test à deux issues sur deux états et deux actions, une dizaine d'opérations. Le plafond de l'information parfaite coûte O(m × k) et permet souvent d'arrêter avant le calcul complet.

**Du squelette au code.** Les utilités de l'exemple de base sont `utilite(p_fraude, action)`, le maximum est `meilleure(p_fraude)` et l'algorithme à deux issues est `voi(prior, sensibilite, fausse_alerte)`, qui appelle `posterieurs(prior, sensibilite, fausse_alerte)` pour Bayes. L'information parfaite est l'appel `voi(0.2, 1.0, 0.0)`, la vérification réelle `voi(0.2, 0.9, 0.05)`. La boucle sur les résultats, avec ses sommes non normalisées, est `voi_generale(probas, utilites, vraisemblances)`, et le plafond est `voi_parfaite(probas, utilites)`. Les quatre cas sont `cas_1_assureur_sinistres()`, `cas_2_banque_releves()`, `cas_3_promoteur_etude()` et `cas_4_rh_diplomes()`.
