# 33 — MRR (Mean Reciprocal Rank) : démonstrations

> Fiche : [33 — MRR](<../../Images/04-Recherche/33_mrr.md>) · Image : `33_mrr.jpg` · Leçon : [Étape 27 — MRR](<../../05-RAG/27-RAG-Formule-MRR.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
\operatorname{MRR} = \frac{1}{\lvert Q \rvert} \sum_{q \in Q} \frac{1}{\operatorname{rang}_q}
$$

Pour chaque requête q, rang_q est la position du premier résultat pertinent. Si aucun pertinent n'est trouvé, on compte 0. Le MRR fait la moyenne sur toutes les requêtes.

Précisions de la leçon 27 : « compter 0 » signifie que le **rang réciproque** vaut 0, parce que le rang est infini ; le rang lui-même n'est jamais 0. Le code représente « rien trouvé » par `None`, refuse tout rang inférieur à 1 par `ValueError`, et renvoie `None` pour un jeu de requêtes vide. La version coupée MRR@k ne compte que les premiers pertinents situés dans les k premiers résultats, et le HitRate@k (aussi appelé Success@k) est la part des requêtes résolues dans ces k premiers.

## Les symboles, un par un

$$
Q
$$

Le jeu de requêtes évaluées, ensemble fini ; |Q| est leur nombre. Dans le programme, c'est la liste `rangs`, un rang par requête.

$$
\operatorname{rang}_q
$$

Le rang, compté à partir de 1, du premier document pertinent pour la requête q, dans la liste dédoublonnée ; entier ≥ 1, ou +∞ si rien n'est trouvé ; fonction `first_relevant_rank(retrouves, pertinents)`, qui renvoie `None` pour +∞.

$$
\operatorname{RR}_q
$$

Le rang réciproque, RR = 1/rang, réel dans [0 ; 1], 0 quand rien n'est trouvé ; fonction `reciprocal_rank(rang, k)`.

$$
k
$$

La coupure : le nombre de résultats que l'agent lit, entier ≥ 1, ou pas de coupure ; argument `k`, `None` par défaut.

$$
\operatorname{MRR@}k
$$

La moyenne des rangs réciproques coupés à k, réel dans [0 ; 1], indéfini si Q est vide ; fonction `mrr(rangs, k)`.

$$
\operatorname{HitRate@}k
$$

La part des requêtes dont le premier pertinent est dans les k premiers, réel dans [0 ; 1] ; fonction `hit_rate(rangs, k)`. HitRate@1 est aussi noté Success@1.

$$
\bar{r}
$$

Le rang moyen des requêtes résolues, réel ≥ 1 ; `sum(rangs) / len(rangs)` quand aucun rang n'est `None`.

## Le mécanisme, avant les preuves

Le MRR reçoit, pour chaque requête, une seule information : la position du premier document pertinent dans la liste renvoyée, ou l'absence de document pertinent. Il ignore tout le reste : les autres documents pertinents, leur nombre, leur ordre. Chaque position r est transformée en son inverse 1/r : 1 au rang 1, 0,5 au rang 2, 0,2 au rang 5, et 0 quand rien n'est trouvé, valeur que 1/r atteint à la limite quand r devient infini. L'inverse est une fonction qui décroît très vite au début puis très lentement : passer du rang 2 au rang 1 rapporte 0,5, passer du rang 10 au rang 9 rapporte environ 0,011 (démonstration 2). C'est voulu : le MRR modélise un lecteur qui s'arrête au premier bon résultat, et pour qui la différence entre la première et la deuxième place compte beaucoup plus que celle entre la dixième et la onzième. La moyenne sur les requêtes donne à chaque requête le même poids, quelle que soit sa difficulté. Pourquoi l'inverse et pas le rang lui-même ? Parce qu'une requête non résolue aurait un rang infini, qui rendrait la moyenne des rangs infinie ; l'inverse transforme cet infini en 0 et garde la moyenne entre 0 et 1. Ce choix a une conséquence de lecture : la moyenne des inverses n'est pas l'inverse de la moyenne, et 1/MRR n'est pas un rang moyen, mais une moyenne harmonique, toujours plus optimiste (démonstration 4). Enfin, la coupure k remplace par 0 les premiers pertinents trop lointains, ce qui aligne la mesure sur ce que l'agent lit vraiment.

Petit film chiffré : quatre requêtes, premiers pertinents aux rangs 1, 3, aucun, 2.

| Requête | rang | RR = 1/rang |
|---|---|---|
| q1 | 1 | 1 |
| q2 | 3 | 0,3333 |
| q3 | aucun (+∞) | 0 |
| q4 | 2 | 0,5 |
| somme | | 1,8333 |

Le MRR vaut 1,8333/4 ≈ 0,4583. La requête q3 non résolue pèse autant, à la baisse, qu'une requête parfaite à la hausse.

## Démonstration 1 — Le MRR est entre 0 et 1

**Ce qu'on démontre.** Pour tout jeu de requêtes non vide :

$$
0 \le \operatorname{MRR} \le 1, \qquad \operatorname{MRR} = 1 \iff \text{tous les premiers pertinents sont au rang } 1
$$

**L'idée.** Chaque terme est un nombre entre 0 et 1 ; une moyenne de tels nombres reste entre 0 et 1, et elle ne vaut 1 que si tous les termes valent 1.

**La preuve, pas à pas.**

**Étape 1.** Si un pertinent est trouvé, rang ≥ 1, donc 0 < 1/rang ≤ 1, parce que la fonction inverse est décroissante sur [1 ; +∞[ ; sinon le terme vaut 0. Dans les deux cas :

$$
0 \le \operatorname{RR}_q \le 1
$$

**Étape 2.** En additionnant les |Q| encadrements puis en divisant par |Q| > 0, on obtient 0 ≤ MRR ≤ 1.

**Étape 3.** MRR = 1 signifie ∑(1 − RR_q) = 0, une somme de termes ≥ 0, donc chaque terme est nul : RR_q = 1, c'est-à-dire rang_q = 1 pour toute requête. ∎

**Vérification chiffrée.** Trois requêtes au rang 1 donnent MRR = 1 ; deux requêtes non résolues donnent 0 ; les rangs (1 ; 2) donnent 0,75 < 1. Le programme vérifie l'encadrement sur toutes les combinaisons de deux rangs parmi aucun, 1, 2, 3, 7. Contre-exemple quand l'hypothèse « rang ≥ 1 » manque : un rang −2, accepté par l'ancienne fonction de ce fichier, donne un terme −0,5 et fait sortir le MRR de l'intervalle (démonstration 6).

**Ce que la preuve révèle du mécanisme.** Le MRR est une moyenne de « notes » entre 0 et 1 attribuées à chaque requête ; il se lit comme une moyenne de copies, chaque requête comptant pour 1/|Q|.

**Conséquence pour un agent.** Le MRR se compare d'un système à l'autre sur le même jeu de requêtes, et l'on peut fixer un seuil dessus (par exemple une alerte sous 0,75), ce que l'on ne peut pas faire avec un score BM25 ou RRF.

## Démonstration 2 — Les premiers rangs comptent énormément

**Ce qu'on démontre.** Faire gagner une place au premier pertinent, du rang r + 1 au rang r, augmente son rang réciproque de :

$$
\frac{1}{r} - \frac{1}{r + 1} = \frac{1}{r(r + 1)}
$$

Ce gain décroît comme 1/r² : il est maximal en tête de liste.

**L'idée.** L'inverse descend très vite près de 1 puis s'aplatit ; gagner une place près du sommet déplace donc beaucoup la valeur, gagner une place loin du sommet presque rien.

**La preuve, pas à pas.**

**Étape 1.** On réduit au même dénominateur r(r + 1) :

$$
\frac{1}{r} - \frac{1}{r + 1} = \frac{(r + 1) - r}{r(r + 1)} = \frac{1}{r(r + 1)}
$$

**Étape 2.** r(r + 1) croît avec r et dépasse r², donc le gain décroît et reste inférieur à 1/r². Sur le MRR d'un jeu de |Q| requêtes, ce gain est divisé par |Q|. ∎

**Vérification chiffrée.** Du rang 2 au rang 1 : 1 − 1/2 = 0,5. Du rang 3 au rang 2 : 1/2 − 1/3 ≈ 0,16667. Du rang 10 au rang 9 : 1/9 − 1/10 = 1/90 ≈ 0,01111, quarante-cinq fois moins que le premier gain. Le programme vérifie l'identité pour r de 1 à 199. Contre-exemple quand on lit le MRR comme une moyenne de rangs : pour le rang moyen, chaque place gagnée vaut 1, quel que soit le rang ; le MRR, lui, ne donne presque rien aux places gagnées en bas de liste.

**Ce que la preuve révèle du mécanisme.** Le MRR récompense presque uniquement le haut du classement. C'est la bonne mesure quand l'agent n'utilise que le premier bon passage ; c'est un défaut quand il en lit dix.

**Conséquence pour un agent.** Pour améliorer le MRR, on travaille sur le reranker, qui fait remonter le bon document de la deuxième à la première place, plutôt que sur le rappel profond du retriever.

## Démonstration 3 — Encadrement par les taux de réussite, et croissance en k

**Ce qu'on démontre.** Pour toute coupure k ≥ 1 :

$$
\max\!\left(\operatorname{HitRate@}1, \ \frac{\operatorname{HitRate@}k}{k}\right) \le \operatorname{MRR@}k \le \operatorname{HitRate@}k
$$

et MRR@k est croissant en k, égal au MRR sans coupure dès que k dépasse le plus grand rang trouvé.

**L'idée.** Une requête résolue dans les k premiers compte entre 1/k et 1 ; une requête résolue au rang 1 compte exactement 1 ; une requête non résolue dans les k premiers compte 0. Augmenter k ne peut que faire passer des termes de 0 à une valeur positive.

**La preuve, pas à pas.**

**Étape 1.** Pour une requête q, si 1 ≤ rang_q ≤ k, alors 1/k ≤ RR_q@k ≤ 1, parce que l'inverse est décroissant ; sinon RR_q@k = 0, comme l'indicatrice 𝟏[rang_q ≤ k] :

$$
\frac{1}{k}\,\mathbf{1}[\operatorname{rang}_q \le k] \le \operatorname{RR}_q@k \le \mathbf{1}[\operatorname{rang}_q \le k]
$$

**Étape 2.** Une moyenne conserve les inégalités terme à terme : HitRate@k/k ≤ MRR@k ≤ HitRate@k.

**Étape 3.** Les requêtes résolues au rang 1 apportent chacune exactement 1, et les autres termes sont ≥ 0, donc MRR@k ≥ HitRate@1.

**Étape 4.** Quand k augmente, chaque RR_q@k reste égal ou passe de 0 à 1/rang_q, jamais l'inverse ; la moyenne est donc croissante en k. ∎

**Vérification chiffrée.** Pour les rangs (1 ; 3 ; aucun ; 2) : à k = 1, 0,25 ≤ 0,25 ≤ 0,25 ; à k = 2, MRR@2 = (1 + 0 + 0 + 0,5)/4 = 0,375, entre 0,25 et HitRate@2 = 0,5 ; à k = 3, 0,4583 ≤ 0,75 ; à k = 5, 0,15 ≤ 0,4583 ≤ 0,75. La suite des MRR@k pour k de 1 à 5 est croissante et finit égale au MRR. Contre-exemple pour la monotonie quand on change de métrique : la Precision@k (fichier 12) peut baisser quand k augmente, le MRR@k jamais.

**Ce que la preuve révèle du mécanisme.** Le MRR ne dit jamais plus que la part de requêtes résolues : un MRR de 0,7 avec un HitRate@5 de 0,72 signifie « presque toujours au rang 1 quand c'est trouvé » ; le même MRR avec un HitRate@5 de 1 signifie « toujours trouvé, mais souvent au rang 2 ou 3 ».

**Conséquence pour un agent.** On publie toujours le MRR avec un HitRate@k, et l'on choisit k égal au nombre de résultats que l'agent lit réellement (cas 1). Ajouter des résultats au contexte ne fait jamais baisser le MRR : c'est le coût du contexte, pas la métrique, qui limite k.

## Démonstration 4 — 1/MRR est une moyenne harmonique des rangs

**Ce qu'on démontre.** Si toutes les requêtes sont résolues, avec un rang moyen r̄ :

$$
\frac{1}{\operatorname{MRR}} = \frac{\lvert Q \rvert}{\sum_q 1/\operatorname{rang}_q} \le \bar{r}, \qquad \text{donc} \qquad \operatorname{MRR} \ge \frac{1}{\bar{r}}
$$

avec égalité si et seulement si tous les rangs sont égaux.

**L'idée.** 1/MRR est, par définition, la moyenne harmonique des rangs, et une moyenne harmonique est toujours inférieure ou égale à la moyenne arithmétique : les petits rangs la tirent vers le bas.

**La preuve, pas à pas.**

**Étape 1.** On applique l'inégalité de Cauchy-Schwarz (fichier 01) aux vecteurs (√r₁, …, √rₙ) et (1/√r₁, …, 1/√rₙ), dont le produit scalaire vaut n :

$$
n^2 = \left(\sum_{i=1}^{n} \sqrt{r_i} \cdot \frac{1}{\sqrt{r_i}}\right)^2 \le \left(\sum_{i=1}^{n} r_i\right)\left(\sum_{i=1}^{n} \frac{1}{r_i}\right)
$$

**Étape 2.** On divise les deux membres par n ∑ rᵢ > 0 :

$$
\frac{1}{n}\sum_{i=1}^{n} \frac{1}{r_i} \ge \frac{n}{\sum r_i} = \frac{1}{\bar{r}}
$$

**Étape 3.** L'égalité de Cauchy-Schwarz exige des vecteurs proportionnels, c'est-à-dire √rᵢ = c/√rᵢ pour tout i, soit tous les rᵢ égaux. ∎

**Vérification chiffrée.** Deux requêtes aux rangs 1 et 3 : MRR = (1 + 1/3)/2 ≈ 0,6667, alors que le rang moyen vaut 2 et que 1/2 = 0,5 ; on vérifie (1 + 3)(1 + 1/3) ≈ 5,33 ≥ 4, et 1/MRR = 1,5, la moyenne harmonique. Pour les rangs (1 ; 2 ; 7 ; 3), 1/MRR ≈ 2,0241 ≤ 13/4 = 3,25. Cas d'égalité : (2 ; 2) donne MRR = 0,5 = 1/2. Contre-exemple quand l'hypothèse « toutes résolues » manque : avec une requête non résolue, le rang moyen n'existe pas (rang infini), et l'inégalité n'a plus de sens.

**Ce que la preuve révèle du mécanisme.** Une seule requête mal classée (rang 50) dégrade peu le MRR, alors qu'elle ferait exploser le rang moyen : le MRR est robuste aux mauvaises requêtes isolées, et donc aveugle à elles.

**Conséquence pour un agent.** Un tableau de bord ne doit jamais afficher 1/MRR comme un « rang moyen » (cas 3) : il donnerait une image trop optimiste. On affiche le MRR, le HitRate@k, et la distribution des rangs.

## Démonstration 5 — Un MRR élevé garantit beaucoup de premières places

**Ce qu'on démontre.** Pour tout jeu de requêtes :

$$
\operatorname{Success@}1 \ge 2\,\operatorname{MRR} - 1
$$

La borne est atteinte quand chaque requête est soit au rang 1, soit au rang 2.

**L'idée.** Une requête qui n'est pas au rang 1 a un rang réciproque d'au plus 1/2 : elle fait perdre au moins 1/2 par rapport à une requête parfaite. Beaucoup de telles requêtes feraient forcément baisser le MRR.

**La preuve, pas à pas.**

**Étape 1.** Soit m le nombre de requêtes dont le premier pertinent n'est pas au rang 1 (rang ≥ 2 ou rien trouvé). Pour chacune, RR_q ≤ 1/2, donc 1 − RR_q ≥ 1/2 ; pour les autres, 1 − RR_q = 0.

**Étape 2.** On additionne sur toutes les requêtes :

$$
\lvert Q \rvert\,(1 - \operatorname{MRR}) = \sum_q (1 - \operatorname{RR}_q) \ge \frac{m}{2}
$$

**Étape 3.** Success@1 = 1 − m/|Q| et m/|Q| ≤ 2(1 − MRR), d'où Success@1 ≥ 1 − 2(1 − MRR) = 2 MRR − 1. L'égalité exige 1 − RR_q = 1/2 exactement pour les m requêtes, c'est-à-dire le rang 2. ∎

**Vérification chiffrée.** Huit requêtes au rang 1 et deux au rang 2 : MRR = (8 + 2 × 0,5)/10 = 0,9 et Success@1 = 0,8 = 2 × 0,9 − 1, la borne est atteinte. Le programme vérifie l'inégalité sur tous les jeux de cinq requêtes composés de rangs 1, 2 et « aucun ». Contre-exemple de lecture : un MRR de 0,6 ne garantit que 2 × 0,6 − 1 = 0,2, soit 20 % de premières places ; la borne n'est utile que pour un MRR nettement au-dessus de 0,5.

**Ce que la preuve révèle du mécanisme.** Le MRR ne peut être élevé que si la plupart des requêtes sont résolues au rang 1 : chaque requête au rang 2 « coûte » déjà la moitié d'une requête.

**Conséquence pour un agent.** Pour un agent qui n'ouvre que le premier résultat, on traduit l'exigence métier en seuil de MRR : garantir 90 % de premières places justes demande MRR ≥ 0,95 (cas 4) ; garantir 80 % demande MRR ≥ 0,9 (cas 3).

## Démonstration 6 — « Rien trouvé » vaut 0, un rang invalide est une erreur, et une requête pèse au plus 1/|Q|

**Ce qu'on démontre.** (a) La convention RR = 0 pour « rien trouvé » prolonge 1/r par continuité : 1/r → 0 quand r → +∞. (b) Tout autre codage (rang 0, rang négatif) fausse la moyenne. (c) Changer le résultat d'une seule requête modifie le MRR d'au plus 1/|Q| :

$$
\lim_{r \to +\infty} \frac{1}{r} = 0, \qquad \left\lvert \operatorname{MRR}' - \operatorname{MRR} \right\rvert = \frac{\lvert \operatorname{RR}'_q - \operatorname{RR}_q \rvert}{\lvert Q \rvert} \le \frac{1}{\lvert Q \rvert}
$$

**L'idée.** Un pertinent au rang 100 vaut 0,01, au rang 1 000 il vaut 0,001 ; « pas trouvé du tout » est la limite de ces cas, donc 0. Une seule requête ne change qu'un terme de la moyenne, et ce terme est entre 0 et 1.

**La preuve, pas à pas.**

**Étape 1.** Pour (a), 1/r < ε dès que r > 1/ε : la limite est 0, et poser RR = 0 pour un rang infini ne crée aucun saut.

**Étape 2.** Pour (c), seul le terme de la requête q change ; la différence des moyennes est la différence de ce terme divisée par |Q|, et deux nombres de [0 ; 1] diffèrent d'au plus 1. ∎

**Vérification chiffrée.** L'ancienne fonction de ce fichier, `sum(1 / r if r and … else 0 …) / len(rangs)`, donnait 0,25 pour les rangs (1 ; −2), parce qu'elle calculait 1/(−2) = −0,5 ; elle comptait un rang 0 comme « rien trouvé » sans le signaler, (1 ; 0) donnant 0,5 ; et elle levait une division par zéro sur un jeu vide. La fonction corrigée refuse −2, 0, 1,5 et `True` par `ValueError`, et renvoie `None` pour un jeu vide. Pour (c), sur quatre requêtes, faire passer la quatrième de « aucun » au rang 1 change le MRR de 1/4 exactement, la borne.

**Ce que la preuve révèle du mécanisme.** Un rang inférieur à 1 n'est jamais une absence de résultat : c'est un bug en amont (rangs comptés à partir de 0, indice −1 renvoyé par une recherche ratée), qu'il faut faire remonter au lieu de le diluer dans une moyenne.

**Conséquence pour un agent.** Sur un jeu d'évaluation de 20 requêtes, une seule requête peut faire bouger le MRR de 0,05 ; une barrière de déploiement qui bloque à 0,05 près doit donc reposer sur plusieurs centaines de requêtes, ou tenir compte de cette granularité (cas 2).

## Exemple simple, à la main

Quatre requêtes. Premier passage pertinent aux rangs 1, 2 et 4, et aucun pour la dernière. Les rangs réciproques valent 1, 1/2 = 0,5, 1/4 = 0,25 et 0 ; leur somme vaut 1,75.

$$
\operatorname{MRR} = \frac{1}{4}\left( 1 + \frac{1}{2} + \frac{1}{4} + 0 \right) = \frac{1{,}75}{4} = 0{,}4375
$$

## Cas d'usage complexes, démontrés

### Cas 1 — [PUBLIC] : deux systèmes, deux usages

**Contexte.** Une entité de services publics en ligne, accessible par UAE Pass, doit choisir entre deux systèmes de recherche pour son assistant bilingue. Selon l'écran, l'assistant affiche soit une seule « carte réponse » (le premier résultat), soit un contexte de trois passages dans lequel le modèle rédige sa réponse. Dix requêtes réelles d'usagers, annotées, servent de test ; le service reçoit 1 000 questions par jour. Ces volumes sont illustratifs.

**Données.**

- Système S₁, rangs du premier pertinent : 1, 1, 3, aucun, 2, 1, 5, 1, aucun, 2.
- Système S₂ : 2, 2, 1, 2, 2, 2, 1, 2, 3, 2.
- Écran « carte » : k = 1 ; écran « contexte » : k = 3.

**Calcul pas à pas.**

**Étape 1, les MRR.** S₁ : (1 + 1 + 1/3 + 0 + 0,5 + 1 + 0,2 + 1 + 0 + 0,5)/10 = 5,5333/10 ; S₂ : (7 × 0,5 + 1 + 1 + 1/3)/10 = 5,8333/10 :

$$
\operatorname{MRR}(S_1) \approx 0{,}55333, \qquad \operatorname{MRR}(S_2) \approx 0{,}58333
$$

**Étape 2, les taux de réussite.** S₁ : HitRate@1 = 4/10 = 0,4 et HitRate@3 = 7/10 = 0,7. S₂ : HitRate@1 = 0,2 et HitRate@3 = 1,0.

**Étape 3, les MRR coupés à 3.** S₁ perd la requête au rang 5 : MRR@3 = (5,5333 − 0,2)/10 ≈ 0,53333. S₂ n'a aucun rang au-delà de 3 : MRR@3 ≈ 0,58333.

**Décision de l'agent.** Pour l'écran « contexte », où le modèle lit trois passages, l'entité choisit S₂ : aucune requête ne reste sans source dans le top-3 (HitRate@3 = 1,0 contre 0,7), et son MRR@3 est le meilleur. Pour l'écran « carte », S₁ place le bon résultat en tête deux fois plus souvent (0,4 contre 0,2). Le compromis : faire tourner deux systèmes coûte plus cher ; l'entité retient S₂ partout et lance l'entraînement d'un reranker pour remonter le premier pertinent de S₂, presque toujours au rang 2.

**Contre-calcul.** Choisir sur le seul MRR mène à S₂, ce qui est juste pour le contexte mais faux pour la carte : avec la carte seule, S₁ donnerait la bonne démarche à 400 usagers sur 1 000 par jour, S₂ à 200, soit 200 usagers de moins bien servis, qui risquent d'appeler le centre de contact. Le MRR seul ne le dit pas, d'où l'obligation de publier MRR et HitRate@k ensemble.

**Sensibilité.** La valeur de bascule est le rang auquel S₁ retrouverait une de ses deux requêtes perdues : au rang r, son MRR devient 0,55333 + (1/r)/10, qui dépasse 0,58333 si et seulement si 1/r > 0,3, soit r ≤ 3 ; au rang 3, il vaut 0,58667, au rang 1 il vaudrait 0,65333 (exercice 6 : au rang 2, 0,60333).

**En production.** L'indicateur suivi est le MRR@1 (égal au HitRate@1) par langue, sur un échantillon hebdomadaire, avec une alerte dès que l'écart entre l'arabe et l'anglais dépasse 0,05 (illustratif). Les requêtes conservées pour l'évaluation sont expurgées de tout numéro d'Emirates ID (15 chiffres commençant par 784), conformément à la PDPL.

### Cas 2 — [CRYPTO] : un nouveau découpage fait reculer la bonne section

**Contexte.** Une plateforme d'actifs virtuels agréée par la VARA met à la disposition de ses analystes conformité un agent qui répond en citant le premier résultat de ses procédures internes (KYC, surveillance des transactions). L'équipe veut passer de sections entières à des morceaux de 200 mots. Sa barrière de déploiement : refuser toute version qui fait baisser le MRR de plus de 0,05 sur le jeu d'évaluation. Le jeu de 20 questions et les rangs sont illustratifs.

**Données.**

- Avant (sections entières) : 12 questions au rang 1, 4 au rang 2, 2 au rang 3, 2 sans pertinent dans les dix premiers.
- Après (morceaux de 200 mots) : 6 au rang 1, 6 au rang 2, 4 au rang 3, 2 au rang 4, 2 sans pertinent.
- Barrière : baisse du MRR > 0,05 refusée.

**Calcul pas à pas.**

**Étape 1, le MRR avant :**

$$
\operatorname{MRR}_{avant} = \frac{12 + 4 \times 0{,}5 + 2 \times \frac{1}{3}}{20} = \frac{14{,}6667}{20} \approx 0{,}73333
$$

**Étape 2, le MRR après :**

$$
\operatorname{MRR}_{apres} = \frac{6 + 6 \times 0{,}5 + 4 \times \frac{1}{3} + 2 \times 0{,}25}{20} = \frac{10{,}8333}{20} \approx 0{,}54167
$$

**Étape 3, la baisse.** 0,73333 − 0,54167 = 0,19167 > 0,05.

**Étape 4, le HitRate@10.** 18/20 = 0,9 avant comme après.

**Décision de l'agent.** La barrière bloque le déploiement : la bonne section est toujours trouvée, mais plus bas, parce que les petits morceaux de la partie « définitions » répètent les mots des questions et passent devant. L'équipe garde les sections entières, ou ajoute un reranker avant de retenter. Le compromis : les petits morceaux réduisent la taille du contexte et le coût par question ; ce gain ne vaut rien si l'analyste est renvoyé vers une définition au lieu de la procédure.

**Contre-calcul.** Avec le seul HitRate@10 (ou un Recall@10), rien ne bouge (0,9 avant et après) et la version serait déployée. Le Success@1 passe pourtant de 0,6 à 0,3 : six questions de plus sur vingt, soit 30 % des questions, verraient l'agent citer autre chose que la procédure à suivre.

**Sensibilité.** Chaque question qui passe du rang 1 au rang 2 coûte (1 − 0,5)/20 = 0,025 de MRR. La valeur de bascule est de 3 questions déplacées : deux déplacements font baisser le MRR de 0,05 exactement, ce que la barrière tolère (« plus de 0,05 »), le troisième la déclenche. Avec 20 questions, la barrière est donc grossière (démonstration 6) : l'équipe porte le jeu à plusieurs centaines de questions.

**En production.** L'indicateur suivi est le MRR à chaque version de l'index, à côté du Recall@10, pour distinguer « pas trouvé » de « trouvé trop bas ». Une plateforme agréée doit appliquer ses propres procédures de lutte anti-blanchiment ; le détail des obligations est à confirmer avec le règlement de la VARA en vigueur.

### Cas 3 — [RH] : un rang moyen mal lu sur le tableau de bord

**Contexte.** Un cabinet RH présent dans plusieurs émirats utilise un routeur qui choisit la procédure de visa à suivre (nouvelle embauche, renouvellement, modification de contrat auprès du MOHRE) d'après le premier résultat d'une recherche, dans un top-3. Le tableau de bord affichait un « rang moyen » calculé comme 1/MRR. Dix questions de test et les rangs sont illustratifs.

**Données.**

- Avant : 4 questions au rang 1, 2 au rang 2, 4 au rang 10.
- Après ajout de l'émirat et du type de visa à la requête : 7 au rang 1, 2 au rang 2, 1 au rang 3.
- Exigence métier : au moins 80 % de procédures justes au premier résultat.

**Calcul pas à pas.**

**Étape 1, le MRR avant :**

$$
\operatorname{MRR} = \frac{4 + 2 \times 0{,}5 + 4 \times 0{,}1}{10} = 0{,}54
$$

**Étape 2, les deux « rangs moyens ».** 1/MRR = 1/0,54 ≈ 1,85 ; le vrai rang moyen vaut (4 × 1 + 2 × 2 + 4 × 10)/10 = 48/10 = 4,8.

**Étape 3, ce que lit le routeur.** HitRate@3 = 6/10 = 0,6 et MRR@3 = (4 + 1)/10 = 0,5 : quatre questions sur dix ont la bonne procédure hors du top-3.

**Étape 4, après correction.** MRR = (7 + 2 × 0,5 + 1/3)/10 = 8,3333/10 ≈ 0,83333 ; HitRate@3 = 1,0 ; Success@1 = 0,7, au-dessus de la borne 2 × 0,83333 − 1 ≈ 0,66667.

**Décision de l'agent.** Le cabinet remplace le « rang moyen » du tableau de bord par le HitRate@3 et le MRR@3, et ajoute l'émirat et le type de visa à chaque requête. Après correction, aucune question ne tombe hors du top-3, mais le Success@1 de 0,7 reste sous l'exigence de 80 % : le routeur demande une confirmation à l'utilisateur quand le premier et le deuxième résultat sont deux procédures différentes. Le compromis : une question de confirmation de plus, contre moins de dossiers lancés sur le mauvais circuit.

**Contre-calcul.** Le tableau de bord affichait 1,85, ce qui laissait croire que le bon résultat était presque toujours en tête ; le vrai rang moyen de 4,8 et le HitRate@3 de 0,6 montrent que quatre dossiers sur dix partaient sur le mauvais circuit. L'écart vient de la démonstration 4 : 1/MRR est la moyenne harmonique, tirée vers le bas par les rangs 1.

**Sensibilité.** Par la démonstration 5, garantir 80 % de premières places justes demande MRR ≥ (1 + 0,8)/2 = 0,9 : c'est la valeur de bascule à partir de laquelle le routeur pourrait se passer de la question de confirmation sans autre contrôle.

**En production.** Les indicateurs suivis sont le HitRate@3 et le MRR@3 par émirat et par type de demande, avec une alerte si le HitRate@3 passe sous 0,95 (illustratif). Les démarches auprès du MOHRE sont à confirmer avec le texte en vigueur pour chaque type de visa.

### Cas 4 — [ASSUR] : la clause de la bonne version du contrat

**Contexte.** Un assureur auto et santé révise chaque année le texte de ses contrats, et un sinistre se règle selon la version signée par l'assuré. Pour chaque déclaration, l'agent cite la première clause renvoyée et en tire la franchise ; seule la clause de la bonne version est pertinente. L'assureur traite 1 000 sinistres par mois, et l'écart de franchise entre deux versions vaut 250 AED en moyenne. Le jeu de 20 sinistres de test, les volumes et les montants sont illustratifs.

**Données.**

- Avant : 8 sinistres avec la bonne clause au rang 1, 10 au rang 2 (l'ancienne version passe devant), 2 sans la bonne clause.
- Après un filtre sur la version du contrat, lue dans le dossier avant la recherche : 18 au rang 1, 2 au rang 2.
- Exposition : 1 000 sinistres par mois × part des premières clauses fausses × 250 AED.

**Calcul pas à pas.**

**Étape 1, le MRR avant.** (8 + 10 × 0,5 + 0)/20 = 13/20 = 0,65 ; Success@1 = 8/20 = 0,4.

**Étape 2, le MRR après.** (18 + 2 × 0,5)/20 = 19/20 = 0,95 ; Success@1 = 18/20 = 0,9.

**Étape 3, la borne de la démonstration 5 :**

$$
\operatorname{Success@}1 \ge 2 \times 0{,}95 - 1 = 0{,}9
$$

Elle est atteinte, parce que les seules requêtes imparfaites sont au rang 2.

**Étape 4, l'exposition mensuelle :**

$$
1\,000 \times (1 - 0{,}4) \times 250 = 150\,000 \ \text{AED} \quad\longrightarrow\quad 1\,000 \times (1 - 0{,}9) \times 250 = 25\,000 \ \text{AED}
$$

**Décision de l'agent.** Avec le filtre, l'agent applique automatiquement la franchise quand la clause citée est au rang 1 et porte la version du contrat signé ; sinon, il envoie le dossier au gestionnaire. Le compromis : le filtre dépend d'une métadonnée de version fiable dans chaque dossier ; un dossier sans version part toujours en revue humaine.

**Contre-calcul.** Sans le filtre, avec un MRR de 0,65, la borne ne garantit que 2 × 0,65 − 1 = 0,3, et le Success@1 réel est de 0,4 : six sinistres sur dix seraient réglés avec la franchise d'une version que l'assuré n'a jamais signée, soit 150 000 AED d'écarts par mois à rectifier et autant de contestations possibles.

**Sensibilité.** La valeur de bascule pour garantir 90 % de premières clauses justes est MRR ≥ 0,95 (démonstration 5) : le système filtré est exactement à la limite, et une seule requête de plus au rang 2 sur 20 ferait passer la garantie sous 0,9.

**En production.** L'indicateur suivi est le MRR@1 par ligne de produit et par millésime de contrat, avec une alerte sous 0,9 (illustratif). L'assurance est supervisée par la CBUAE, et chaque décision de sinistre doit citer le texte réellement applicable.

## Entraînement sur feuille A4

**Exercice 1.** Rangs 1, 3, 3, 6. Calculer le MRR.

**Exercice 2.** Une requête passe du rang 4 au rang 2. De combien augmente sa contribution ?

**Exercice 3.** Rangs 1, 1, 1, 50. Calculer le MRR, puis le rang moyen.

**Exercice 4.** Démontrer que MRR@k ≤ HitRate@k.

**Exercice 5.** Un système a HitRate@1 = 0,6. Quel est le plus petit MRR possible ?

**Exercice 6 (modifier un cas).** Dans le cas 1, S₁ retrouve l'une de ses deux requêtes perdues au rang 2. Calculer son nouveau MRR et dire s'il dépasse celui de S₂ ; le choix pour l'écran « contexte » change-t-il ?

**Exercice 7 (trouver l'erreur).** Deux requêtes sont résolues aux rangs 2 et 3. Un collègue calcule MRR = (0,5 + 0,3333)/2 ≈ 0,41667, puis écrit sur le tableau de bord « rang moyen = 1/MRR = 2,4 ». Trouver l'erreur.

**Exercice 8 (redémontrer de mémoire).** Sans regarder la démonstration 5, montrer que Success@1 ≥ 2 MRR − 1, puis l'appliquer à un MRR de 0,9.

## Corrigé

**Exercice 1.** (1 + 1/3 + 1/3 + 1/6)/4 = 1,8333/4 ≈ 0,45833.

**Exercice 2.** 1/2 − 1/4 = 0,25 au niveau de la requête, soit 0,25/|Q| sur le MRR.

**Exercice 3.** MRR = (1 + 1 + 1 + 1/50)/4 = 3,02/4 = 0,755 ; rang moyen = (1 + 1 + 1 + 50)/4 = 53/4 = 13,25. Une seule requête lointaine fait exploser le rang moyen et touche à peine le MRR (démonstration 4).

**Exercice 4.** Chaque terme RR_q@k vaut au plus 1, et vaut 0 pour les requêtes sans pertinent dans le top-k ; donc RR_q@k ≤ 𝟏[rang_q ≤ k], et la moyenne des membres de gauche est au plus la moyenne des indicatrices, HitRate@k (démonstration 3).

**Exercice 5.** 0,6 : les requêtes résolues au rang 1 apportent 0,6 à elles seules (démonstration 3, MRR ≥ HitRate@1), et le minimum est atteint quand toutes les autres requêtes ne sont pas résolues, par exemple six requêtes au rang 1 et quatre sans pertinent.

**Exercice 6.** Le terme de la requête passe de 0 à 0,5 : MRR = (5,5333 + 0,5)/10 ≈ 0,60333 > 0,58333. S₁ dépasse S₂ en MRR, mais son HitRate@3 ne vaut que 0,8 (une requête reste perdue, une autre est au rang 5) contre 1,0 pour S₂ : pour l'écran « contexte », S₂ reste préférable, puisqu'aucune de ses requêtes ne reste sans source.

**Exercice 7.** 1/MRR = 1/0,41667 = 2,4 est la moyenne harmonique des rangs, pas leur moyenne : le rang moyen vaut (2 + 3)/2 = 2,5. L'écart est faible ici parce que les deux rangs sont proches ; il devient énorme quand les rangs sont dispersés (cas 3 : 1,85 contre 4,8).

**Exercice 8.** Étape 1 : soit m le nombre de requêtes qui ne sont pas au rang 1 ; chacune a RR ≤ 1/2, donc 1 − RR ≥ 1/2. Étape 2 : |Q|(1 − MRR) = ∑(1 − RR_q) ≥ m/2. Étape 3 : Success@1 = 1 − m/|Q| ≥ 1 − 2(1 − MRR) = 2 MRR − 1. Pour MRR = 0,9 : au moins 0,8, soit 80 % de premières places justes, borne atteinte par huit requêtes au rang 1 et deux au rang 2.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`dedupliquer(retrouves)`** — Cette fonction se tient à l'entrée de la salle comme un huissier qui fait l'appel et ne laisse passer chaque invité qu'une seule fois : elle reçoit la liste des identifiants renvoyés par le moteur de recherche, dans l'ordre du classement, et la verse dans un dictionnaire construit par `dict.fromkeys`, qui ne garde que la première apparition de chaque clé tout en respectant l'ordre d'arrivée. Elle renvoie la liste de ces clés, débarrassée de ses doublons, si bien qu'un document répété ne peut plus décaler le rang de ceux qui le suivent ; c'est la même convention qu'à l'étape 26, et `first_relevant_rank` s'en sert avant de compter.

**`first_relevant_rank(retrouves, pertinents)`** — On l'imagine en lectrice qui descend la liste des résultats du bout du doigt : elle reçoit la liste brute des identifiants et l'ensemble des documents jugés pertinents, la fait d'abord dédoublonner par `dedupliquer`, puis compte les positions à partir de 1 et s'arrête au premier identifiant qui appartient à l'ensemble des pertinents. Elle renvoie ce rang, ou `None` quand la liste s'épuise sans le moindre bon document ; c'est le pont entre ce que renvoie un moteur et les rangs que consomment `reciprocal_rank` et `mrr`, même si `main` ne l'appelle pas, puisque ses jeux d'essai donnent directement les rangs.

**`reciprocal_rank(rang, k)`** — Cette fonction tient le guichet où chaque rang s'échange contre des points : elle reçoit un rang, entier ou `None`, et une coupure k facultative, rend 0 quand rien n'a été trouvé, puis refuse par une `ValueError` tout rang qui serait un booléen, un nombre non entier ou un entier inférieur à 1. Si la coupure est fixée et que le rang la dépasse, elle rend encore 0, faute de quoi elle rend 1/rang : le rang 1 vaut 1, le rang 2 vaut 0,5 et le rang 3 vaut 0,3333, exactement les valeurs du mécanisme de `main`, et c'est elle qui rejette les rangs −2, 0, 1,5 et `True` dans la démonstration 6.

**`mrr(rangs, k)`** — C'est le comptable qui fait la moyenne des points de toutes les questions : il reçoit la liste des rangs, un par question, et une coupure k facultative, lève une `ValueError` si cette coupure est inférieure à 1, renvoie `None` pour un jeu vide plutôt que de diviser par zéro, puis additionne les rangs réciproques fournis par `reciprocal_rank` et divise par le nombre de questions. Le résultat est le MRR, ou le MRR@k quand la coupure est donnée : 0,4583 pour les rangs 1, 3, aucun, 2, et 0,4375 pour l'exemple simple 1, 2, 4, aucun ; toutes les démonstrations et les quatre cas reposent sur lui.

**`hit_rate(rangs, k)`** — Celle-ci fait le pointage d'un contrôleur qui ne regarde pas la place exacte, mais seulement si le bon document est monté dans le wagon des k premiers : elle reçoit la liste des rangs et la coupure k, refuse une coupure inférieure à 1 par une `ValueError`, renvoie `None` pour un jeu vide, puis compte les questions dont le rang réciproque coupé à k est strictement positif et divise ce compte par le nombre de questions. Elle renvoie le HitRate@k, soit 0,25, 0,5, 0,75 et 0,75 pour k = 1, 2, 3 et 5 sur le jeu 1, 3, aucun, 2 ; avec k = 1, elle sert de Success@1 dans la démonstration 5 et dans le cas 4.

**`ancien_mrr(rangs, k)`** — Cette fonction est une pièce de musée, l'ancienne version du calcul conservée sous vitrine pour montrer ses défauts : elle reçoit les rangs et une coupure facultative, ajoute 1/x pour chaque rang qui est « vrai » au sens de Python et qui respecte la coupure, compte 0 pour les autres, puis divise par la longueur de la liste sans aucune garde. Un rang 0 passe donc pour « rien trouvé », un rang négatif est accepté, si bien que 1 et −2 donnent 0,25 et que 1 et 0 donnent 0,5, et un jeu vide provoque une `ZeroDivisionError` ; la démonstration 6 s'en sert de contre-exemple.

**`r(x, n)`** — Ce petit outil d'atelier joue le rôle d'un régleur qui passe chaque nombre au gabarit avant de le comparer : il reçoit un nombre x et un nombre de décimales n, l'arrondit avec `round` à n chiffres, puis lui ajoute 0.0, ce qui garantit un nombre à virgule flottante et transforme un éventuel zéro négatif en zéro ordinaire. Il renvoie ce nombre arrondi, et presque tous les `assert` de `main` l'emploient pour confronter un résultat de calcul à la valeur écrite à la main dans la fiche, sans se laisser piéger par les dernières décimales d'un flottant.

**`cas_1_assistant_public()`** — Cette fonction met en scène un service public qui hésite entre deux moteurs pour son assistant, l'un destiné à une carte réponse unique, l'autre à un contexte de trois passages : elle ne reçoit rien, fixe les rangs de dix questions pour S1 et pour S2, et calcule pour chacun le MRR, le MRR@3, le HitRate@1 et le HitRate@3, soit 0,55333, 0,53333, 0,4 et 0,7 pour S1 contre 0,58333, 0,58333, 0,2 et 1,0 pour S2. Elle cherche ensuite le plus grand rang, entre 1 et 10, auquel S1 devrait retrouver sa première question perdue pour dépasser S2 en MRR, trouve 3, imprime le tout avec les 200 usagers sur 1 000 que S1 sert de plus sur la carte seule, et renvoie ces résultats dans un dictionnaire.

**`cas_2_decoupage_crypto()`** — Ici, une équipe a redécoupé l'index d'une plateforme de cryptoactifs et la bonne section recule dans les classements : la fonction ne reçoit rien, compare les rangs de vingt questions avant le changement, douze au rang 1, quatre au rang 2, deux au rang 3 et deux perdues, puis après, et trouve un MRR qui tombe de 0,73333 à 0,54167 alors que le HitRate@10 reste à 0,9. La barrière de déploiement se ferme dès que la baisse dépasse 0,05, ce qui est le cas ; la fonction cherche aussi à partir de combien de questions passées du rang 1 au rang 2 elle se déclencherait, trouve 3, imprime ce verdict et renvoie un dictionnaire où figure aussi le Success@1, passé de 0,6 à 0,3.

**`cas_3_routeur_rh()`** — Cette fonction raconte l'erreur d'un tableau de bord qui affichait 1/MRR en guise de rang moyen pour un routeur de procédures de visa : elle ne reçoit rien, prend dix questions dont quatre au rang 1, deux au rang 2 et quatre au rang 10, calcule un MRR de 0,54, un faux « rang moyen » de 1,85 et le vrai rang moyen, 4,8, ainsi qu'un HitRate@3 de 0,6 et un MRR@3 de 0,5. Elle mesure ensuite le système corrigé, sept questions au rang 1, deux au rang 2 et une au rang 3, qui atteint un MRR de 0,83333, un HitRate@3 de 1,0 et un Success@1 de 0,7, imprime la comparaison et renvoie tous ces nombres dans un dictionnaire.

**`cas_4_versions_assur()`** — On y suit un assureur dont l'agent doit citer la clause de la version du contrat réellement signée : la fonction ne reçoit rien, compare vingt sinistres avant le filtre par version, huit au rang 1, dix au rang 2 et deux perdus, puis après, dix-huit au rang 1 et deux au rang 2, et obtient un MRR qui passe de 0,65 à 0,95 et un Success@1 qui passe de 0,4 à 0,9, exactement la borne 2 × 0,95 − 1. Elle traduit enfin les erreurs en argent, mille sinistres par mois et 250 AED d'écart de franchise chacun, soit une exposition qui tombe de 150 000 à 25 000 AED par mois, imprime ce bilan et le renvoie dans un dictionnaire.

**`main()`** — C'est le chef d'orchestre qui fait défiler toute la fiche : il suit d'abord quatre rangs jusqu'au MRR de 0,4583, vérifie les bornes entre 0 et 1, le gain de 0,5, 0,16667 puis 0,01111 quand on gagne une place, l'encadrement du MRR@k par les HitRate, l'inégalité de Jensen sur la moyenne harmonique et la borne Success@1 ≥ 2 MRR − 1 sur toutes les petites combinaisons de cinq questions. Il fait ensuite refuser les rangs invalides, met l'ancienne fonction en défaut, joue l'exemple simple et les quatre cas, puis recalcule le corrigé des exercices ; chaque nombre imprimé est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tous concordent.

```python
"""Démonstration 33 — MRR : bornes, poids des premiers rangs, encadrement par HitRate@k, Jensen, Success@1, conventions, quatre cas."""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def dedupliquer(retrouves: list[str]) -> list[str]:
    """Première occurrence de chaque identifiant, dans l'ordre (même convention qu'à l'étape 26)."""
    return list(dict.fromkeys(retrouves))


def first_relevant_rank(retrouves: list[str], pertinents: set[str]) -> int | None:
    """Rang (à partir de 1) du premier document pertinent de la liste dédoublonnée ; None s'il n'y en a aucun."""
    for rang, doc in enumerate(dedupliquer(retrouves), start=1):
        if doc in pertinents:
            return rang
    return None


def reciprocal_rank(rang: int | None, k: int | None = None) -> float:
    """RR = 1/rang si un pertinent est trouvé (dans les k premiers pour MRR@k) ; 0 sinon (rang = +inf)."""
    if rang is None:
        return 0.0
    if isinstance(rang, bool) or not isinstance(rang, int) or rang < 1:
        raise ValueError(f"rang invalide : {rang!r} (il faut un entier >= 1, ou None si rien n'est trouvé)")
    if k is not None and rang > k:
        return 0.0
    return 1.0 / rang


def mrr(rangs: list[int | None], k: int | None = None) -> float | None:
    """MRR (MRR@k si k est donné) = moyenne des rangs réciproques ; None sur un jeu vide."""
    if k is not None and k < 1:
        raise ValueError("k doit être un entier >= 1")
    if not rangs:
        return None
    return sum(reciprocal_rank(x, k) for x in rangs) / len(rangs)


def hit_rate(rangs: list[int | None], k: int) -> float | None:
    """HitRate@k = part des questions qui ont un document pertinent dans leurs k premiers résultats."""
    if k < 1:
        raise ValueError("k doit être un entier >= 1")
    if not rangs:
        return None
    return sum(1 for x in rangs if reciprocal_rank(x, k) > 0) / len(rangs)


def ancien_mrr(rangs: list, k: int | None = None) -> float:
    """L'ancienne fonction de ce fichier : un rang 0 compté comme « rien », un rang négatif accepté, pas de garde."""
    return sum(1 / x if x and (k is None or x <= k) else 0 for x in rangs) / len(rangs)


def r(x: float, n: int) -> float:
    return round(x, n) + 0.0


def cas_1_assistant_public() -> dict:
    """[PUBLIC] Deux systèmes pour l'assistant d'un service public : carte réponse (top-1) ou contexte de trois passages."""
    s1 = [1, 1, 3, None, 2, 1, 5, 1, None, 2]
    s2 = [2, 2, 1, 2, 2, 2, 1, 2, 3, 2]
    res = {nom: {"mrr": mrr(s), "mrr3": mrr(s, 3), "h1": hit_rate(s, 1), "h3": hit_rate(s, 3)} for nom, s in (("S1", s1), ("S2", s2))}
    bascule = max(x for x in range(1, 11) if mrr([1, 1, 3, x, 2, 1, 5, 1, None, 2]) > res["S2"]["mrr"])
    for nom, v in res.items():
        print(f"Cas 1 — PUBLIC {nom} : MRR {v['mrr']:.5f} ; MRR@3 {v['mrr3']:.5f} ; HitRate@1 {v['h1']} ; HitRate@3 {v['h3']}")
    print(f"  S1 dépasse S2 en MRR si une question perdue est retrouvée au rang {bascule} au plus ;"
          f" carte seule : {1000 * (res['S1']['h1'] - res['S2']['h1']):.0f} usagers de plus sur 1 000 avec S1")
    return {"res": res, "bascule": bascule, "s1": s1, "s2": s2}


def cas_2_decoupage_crypto() -> dict:
    """[CRYPTO] Un nouveau découpage de l'index fait reculer la bonne section : barrière sur le MRR."""
    avant = [1] * 12 + [2] * 4 + [3] * 2 + [None] * 2
    apres = [1] * 6 + [2] * 6 + [3] * 4 + [4] * 2 + [None] * 2
    m_av, m_ap = mrr(avant), mrr(apres)
    h10 = (hit_rate(avant, 10), hit_rate(apres, 10))
    bloque = m_av - m_ap > 0.05
    deplacements = [n for n in range(0, 13) if mrr([1] * (12 - n) + [2] * (4 + n) + [3] * 2 + [None] * 2) < m_av - 0.05 - 1e-12]
    print(f"Cas 2 — CRYPTO : MRR {m_av:.5f} → {m_ap:.5f} (baisse {m_av - m_ap:.5f}) ; HitRate@10 {h10[0]} → {h10[1]} ; bloqué {bloque} ;"
          f" la barrière se déclenche à {deplacements[0]} questions passées du rang 1 au rang 2")
    return {"avant": m_av, "apres": m_ap, "h10": h10, "bloque": bloque, "n_bascule": deplacements[0],
            "s1": (hit_rate(avant, 1), hit_rate(apres, 1))}


def cas_3_routeur_rh() -> dict:
    """[RH] Un routeur de procédures de visa ; le tableau de bord affichait 1/MRR comme un rang moyen."""
    rangs = [1] * 4 + [2] * 2 + [10] * 4
    apres = [1] * 7 + [2] * 2 + [3]
    m = mrr(rangs)
    res = {"mrr": m, "faux_rang": 1 / m, "vrai_rang": sum(rangs) / len(rangs), "h3": hit_rate(rangs, 3), "mrr3": mrr(rangs, 3),
           "apres": mrr(apres), "h3_apres": hit_rate(apres, 3), "s1_apres": hit_rate(apres, 1)}
    print(f"Cas 3 — RH : MRR {m:.2f} ; « rang moyen » 1/MRR {1 / m:.2f} contre vrai rang moyen {res['vrai_rang']} ;"
          f" HitRate@3 {res['h3']} ; MRR@3 {res['mrr3']} ; après correction MRR {res['apres']:.5f}, Success@1 {res['s1_apres']}")
    return res


def cas_4_versions_assur() -> dict:
    """[ASSUR] La clause de la bonne version du contrat : filtre par version, borne Success@1 >= 2 MRR − 1."""
    avant = [1] * 8 + [2] * 10 + [None] * 2
    apres = [1] * 18 + [2] * 2
    m = (mrr(avant), mrr(apres))
    s1 = (hit_rate(avant, 1), hit_rate(apres, 1))
    exposition = tuple(1000 * (1 - s) * 250 for s in s1)               # 1 000 sinistres par mois, 250 AED d'écart de franchise
    print(f"Cas 4 — ASSUR : MRR {m[0]:.2f} → {m[1]:.2f} ; Success@1 {s1[0]} → {s1[1]} (borne {2 * m[1] - 1:.2f}) ;"
          f" exposition {exposition[0]:.0f} → {exposition[1]:.0f} AED par mois")
    return {"mrr": m, "s1": s1, "exposition": exposition}


def main() -> None:
    # Le mécanisme : quatre rangs suivis jusqu'au MRR
    film = [1, 3, None, 2]
    rr = [reciprocal_rank(x) for x in film]
    print("Mécanisme : rangs 1, 3, aucun, 2 → RR " + ", ".join(f"{v:.4f}" for v in rr) + f" ; MRR {mrr(film):.4f}")
    assert [r(v, 4) for v in rr] == [1.0, 0.3333, 0.0, 0.5] and r(mrr(film), 4) == 0.4583 and r(sum(rr), 4) == 1.8333

    # Démonstration 1 : bornes
    assert mrr([1, 1, 1]) == 1.0 and mrr([None, None]) == 0.0 and mrr([1, 2]) < 1
    assert all(0 <= mrr([x, y]) <= 1 for x in (None, 1, 2, 7) for y in (None, 1, 3))

    # Démonstration 2 : gagner une place rapporte 1/(r(r + 1))
    gains = {x: 1 / x - 1 / (x + 1) for x in (1, 2, 9)}
    print(f"Démo 2 : 2 → 1 : +{gains[1]:.5f} ; 3 → 2 : +{gains[2]:.5f} ; 10 → 9 : +{gains[9]:.5f}")
    assert [r(v, 5) for v in gains.values()] == [0.5, 0.16667, 0.01111]
    assert all(abs(1 / x - 1 / (x + 1) - 1 / (x * (x + 1))) < 1e-15 for x in range(1, 200))

    # Démonstration 3 : max(HitRate@1, HitRate@k / k) <= MRR@k <= HitRate@k, et MRR@k croît avec k
    jeu = [1, 3, None, 2]
    lignes = []
    for k in (1, 2, 3, 5):
        m, h = mrr(jeu, k), hit_rate(jeu, k)
        assert max(hit_rate(jeu, 1), h / k) <= m + 1e-12 and m <= h
        lignes.append(f"k = {k} : {h / k:.4f} <= {m:.4f} <= {h:.4f}")
    print("Démo 3 : " + " ; ".join(lignes))
    assert [r(mrr(jeu, k), 4) for k in (1, 2, 3, 5)] == [0.25, 0.375, 0.4583, 0.4583]
    assert [hit_rate(jeu, k) for k in (1, 2, 3, 5)] == [0.25, 0.5, 0.75, 0.75]
    suite = [mrr(jeu, k) for k in range(1, 6)]
    assert all(a <= b for a, b in zip(suite, suite[1:])) and suite[-1] == mrr(jeu)

    # Démonstration 4 : 1/MRR est la moyenne harmonique ; MRR >= 1 / rang moyen (Jensen)
    m13 = mrr([1, 3])
    m4 = mrr([1, 2, 7, 3])
    print(f"Démo 4 : [1, 3] : MRR {m13:.4f} >= 1/2 ; 1/MRR {1 / m13:.4f} ; [1, 2, 7, 3] : 1/MRR {1 / m4:.4f} <= moyenne {13 / 4}")
    assert r(m13, 4) == 0.6667 and r(1 / m13, 10) == 1.5 and mrr([2, 2]) == 0.5 and (1 + 3) * (1 + 1 / 3) >= 4
    assert r((1 + 3) * (1 + 1 / 3), 2) == 5.33 and r(1 / m4, 4) == 2.0241 and 1 / m4 <= 13 / 4

    # Démonstration 5 : Success@1 >= 2 MRR − 1
    bon = [1] * 8 + [2, 2]
    print(f"Démo 5 : [1 × 8, 2, 2] : MRR {mrr(bon):.2f}, Success@1 {hit_rate(bon, 1)} = 2 × MRR − 1")
    assert abs(mrr(bon) - 0.9) < 1e-12 and hit_rate(bon, 1) == 0.8 and abs(2 * mrr(bon) - 1 - 0.8) < 1e-12
    for a in range(0, 6):
        for b in range(0, 6 - a):
            jeu5 = [1] * a + [2] * b + [None] * (5 - a - b)
            assert hit_rate(jeu5, 1) >= 2 * mrr(jeu5) - 1 - 1e-12

    # Démonstration 6 : conventions ; une question change le MRR d'au plus 1/|Q|
    refus = 0
    for invalide in (-2, 0, 1.5, True):
        try:
            mrr([1, invalide])
        except ValueError:
            refus += 1
    vide_ancien = 0
    try:
        ancien_mrr([])
    except ZeroDivisionError:
        vide_ancien = 1
    print(f"Démo 6 : rangs -2, 0, 1.5, True refusés ({refus}/4) ; jeu vide → {mrr([])} ;"
          f" ancienne fonction : [1, -2] → {ancien_mrr([1, -2])}, [1, 0] → {ancien_mrr([1, 0])}, jeu vide → ZeroDivisionError")
    assert refus == 4 and mrr([]) is None and ancien_mrr([1, -2]) == 0.25 and ancien_mrr([1, 0]) == 0.5 and vide_ancien == 1
    assert [r(reciprocal_rank(x), 3) for x in (100, 1000)] == [0.01, 0.001]
    assert all(abs(mrr([1, 2, None] + [x]) - mrr([1, 2, None] + [None])) <= 1 / 4 for x in (1, 2, 50))

    # Exemple simple
    print(f"Exemple simple : MRR = {mrr([1, 2, 4, None])}")
    assert mrr([1, 2, 4, None]) == 0.4375 and 1 + 0.5 + 0.25 + 0 == 1.75

    # Cas 1 — PUBLIC
    c1 = cas_1_assistant_public()
    s1, s2 = c1["res"]["S1"], c1["res"]["S2"]
    assert (r(s1["mrr"], 5), r(s2["mrr"], 5)) == (0.55333, 0.58333) and (r(s1["mrr3"], 5), r(s2["mrr3"], 5)) == (0.53333, 0.58333)
    assert (s1["h1"], s1["h3"], s2["h1"], s2["h3"]) == (0.4, 0.7, 0.2, 1.0)
    assert c1["bascule"] == 3 and r(mrr([1, 1, 3, 1, 2, 1, 5, 1, None, 2]), 5) == 0.65333
    assert hit_rate(c1["s1"], 1) <= mrr(c1["s1"], 5) <= hit_rate(c1["s1"], 5) and hit_rate(c1["s2"], 1) <= mrr(c1["s2"], 5)
    assert r(1 + 1 + 1 / 3 + 0.5 + 1 + 1 / 5 + 1 + 0.5, 4) == 5.5333 and r(sum(1 / x for x in c1["s2"]), 4) == 5.8333
    assert r(mrr([1, 1, 3, 2, 2, 1, 5, 1, None, 2]), 5) == 0.60333 and 1000 * (0.4 - 0.2) == 200
    assert r(mrr([1, 1, 3, 3, 2, 1, 5, 1, None, 2]), 5) == 0.58667 and hit_rate([1, 1, 3, 2, 2, 1, 5, 1, None, 2], 3) == 0.8
    assert r(5.5333 - 0.2, 4) == 5.3333 and r(0.5 / (1 / 90), 6) == 45 and mrr([1, 2]) == 0.75

    # Cas 2 — CRYPTO
    c2 = cas_2_decoupage_crypto()
    assert (r(c2["avant"], 5), r(c2["apres"], 5)) == (0.73333, 0.54167) and r(c2["avant"] - c2["apres"], 5) == 0.19167
    assert c2["h10"] == (0.9, 0.9) and c2["bloque"] and c2["n_bascule"] == 3 and c2["s1"] == (0.6, 0.3)
    assert r((1 - 0.5) / 20, 3) == 0.025
    assert r(12 + 4 * 0.5 + 2 / 3, 4) == 14.6667 and r(6 + 6 * 0.5 + 4 / 3 + 2 * 0.25, 4) == 10.8333
    assert r(4 + 2 * 0.5 + 4 * 0.1, 10) == 5.4 and (4 + 4 + 40) / 10 == 4.8 and r(7 + 1 + 1 / 3, 4) == 8.3333
    assert (8 + 10 * 0.5) / 20 == 0.65 and (18 + 2 * 0.5) / 20 == 0.95

    # Cas 3 — RH
    c3 = cas_3_routeur_rh()
    assert r(c3["mrr"], 10) == 0.54 and r(c3["faux_rang"], 2) == 1.85 and c3["vrai_rang"] == 4.8
    assert c3["h3"] == 0.6 and c3["mrr3"] == 0.5 and r(c3["apres"], 5) == 0.83333 and c3["h3_apres"] == 1.0
    assert c3["s1_apres"] == 0.7 and c3["s1_apres"] >= 2 * c3["apres"] - 1 and r(2 * c3["apres"] - 1, 5) == 0.66667
    assert r((1 + 0.8) / 2, 2) == 0.9

    # Cas 4 — ASSUR
    c4 = cas_4_versions_assur()
    assert (r(c4["mrr"][0], 2), r(c4["mrr"][1], 2)) == (0.65, 0.95) and c4["s1"] == (0.4, 0.9)
    assert r(2 * c4["mrr"][1] - 1, 10) == 0.9 and r(2 * c4["mrr"][0] - 1, 10) == 0.3
    assert [r(v, 0) for v in c4["exposition"]] == [150000, 25000] and 1 - 0.4 == 0.6

    print("Corrigé")
    print(f"  ex1 {mrr([1, 3, 3, 6]):.5f} ; ex2 {1 / 2 - 1 / 4} ; ex3 MRR {mrr([1, 1, 1, 50]):.3f}, rang moyen {53 / 4} ;"
          f" ex6 {mrr([1, 1, 3, 2, 2, 1, 5, 1, None, 2]):.5f}")
    assert r(mrr([1, 3, 3, 6]), 5) == 0.45833 and r(1 + 1 / 3 + 1 / 3 + 1 / 6, 4) == 1.8333 and mrr([1, 1, 1, 50]) == 0.755
    assert mrr([1] * 6 + [None] * 4) == 0.6 and hit_rate([1] * 6 + [None] * 4, 1) == 0.6
    assert r(1 / mrr([2, 3]), 1) == 2.4 and (2 + 3) / 2 == 2.5
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Mécanisme : rangs 1, 3, aucun, 2 → RR 1.0000, 0.3333, 0.0000, 0.5000 ; MRR 0.4583
Démo 2 : 2 → 1 : +0.50000 ; 3 → 2 : +0.16667 ; 10 → 9 : +0.01111
Démo 3 : k = 1 : 0.2500 <= 0.2500 <= 0.2500 ; k = 2 : 0.2500 <= 0.3750 <= 0.5000 ; k = 3 : 0.2500 <= 0.4583 <= 0.7500 ; k = 5 : 0.1500 <= 0.4583 <= 0.7500
Démo 4 : [1, 3] : MRR 0.6667 >= 1/2 ; 1/MRR 1.5000 ; [1, 2, 7, 3] : 1/MRR 2.0241 <= moyenne 3.25
Démo 5 : [1 × 8, 2, 2] : MRR 0.90, Success@1 0.8 = 2 × MRR − 1
Démo 6 : rangs -2, 0, 1.5, True refusés (4/4) ; jeu vide → None ; ancienne fonction : [1, -2] → 0.25, [1, 0] → 0.5, jeu vide → ZeroDivisionError
Exemple simple : MRR = 0.4375
Cas 1 — PUBLIC S1 : MRR 0.55333 ; MRR@3 0.53333 ; HitRate@1 0.4 ; HitRate@3 0.7
Cas 1 — PUBLIC S2 : MRR 0.58333 ; MRR@3 0.58333 ; HitRate@1 0.2 ; HitRate@3 1.0
  S1 dépasse S2 en MRR si une question perdue est retrouvée au rang 3 au plus ; carte seule : 200 usagers de plus sur 1 000 avec S1
Cas 2 — CRYPTO : MRR 0.73333 → 0.54167 (baisse 0.19167) ; HitRate@10 0.9 → 0.9 ; bloqué True ; la barrière se déclenche à 3 questions passées du rang 1 au rang 2
Cas 3 — RH : MRR 0.54 ; « rang moyen » 1/MRR 1.85 contre vrai rang moyen 4.8 ; HitRate@3 0.6 ; MRR@3 0.5 ; après correction MRR 0.83333, Success@1 0.7
Cas 4 — ASSUR : MRR 0.65 → 0.95 ; Success@1 0.4 → 0.9 (borne 0.90) ; exposition 150000 → 25000 AED par mois
Corrigé
  ex1 0.45833 ; ex2 0.25 ; ex3 MRR 0.755, rang moyen 13.25 ; ex6 0.60333
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme mesure à quel rang un système place le premier résultat pertinent, en moyenne sur un ensemble de requêtes, avec le taux de réussite au top-k. Les cas ajoutent une barrière de déploiement sur la baisse du MRR (cas 2) et la traduction d'une exigence de premières places en seuil de MRR par la borne Success@1 ≥ 2 MRR − 1 (cas 3 et 4).

```text
ALGORITHME MRRetHitRate
ENTRÉES : pour chaque requête : classement retrouvé et ensemble des pertinents ; coupure k (facultative)
SORTIE  : (MRR@k, HitRate@k), ou « indéfini » pour un jeu vide

  rangs ← liste vide
  POUR CHAQUE requête q FAIRE
      classement ← Dédoublonner(classement)
      rang_q ← position (à partir de 1) du premier pertinent, ou « aucun »
      ajouter rang_q à rangs
  FIN POUR
  SI rangs est vide ALORS RETOURNER « indéfini »
  somme ← 0 ; trouvées ← 0
  POUR CHAQUE rang_q de rangs FAIRE
      SI rang_q n'est pas « aucun » ET rang_q n'est pas un entier ≥ 1 ALORS ERREUR
      SI rang_q existe ET (pas de coupure OU rang_q ≤ k) ALORS
          somme ← somme + 1 / rang_q
          trouvées ← trouvées + 1
      FIN SI
  FIN POUR
  RETOURNER somme / |Q|, trouvées / |Q|
```

**Complexité.** Trouver le premier pertinent coûte, pour chaque requête, au plus la longueur de la liste renvoyée, et s'arrête dès qu'il est trouvé : O(|Q| × n) au pire pour des listes de longueur n, puis O(|Q|) en temps et O(1) en mémoire pour les deux moyennes.

**Du squelette au code.** Le dédoublonnage est `dedupliquer(retrouves)` et le rang `first_relevant_rank(retrouves, pertinents)`, qui renvoie `None` pour « aucun » ; `reciprocal_rank(rang, k)` applique la coupure et refuse les rangs invalides ; le MRR est la fonction `mrr(rangs, k)` et le HitRate@k la fonction `hit_rate(rangs, k)`, qui renvoient `None` pour un jeu vide. `ancien_mrr(rangs, k)` reproduit l'ancienne fonction de ce fichier, gardée pour le contre-exemple de la démonstration 6. Les quatre cas sont `cas_1_assistant_public`, `cas_2_decoupage_crypto`, `cas_3_routeur_rh` et `cas_4_versions_assur`.
