# 32 — Perplexité : démonstrations

> Fiche : [32 — Perplexité](<../../Images/03-Modele/32_perplexite.md>) · Image : `32_perplexite.jpg` · Leçon : [Étape 52 — Perplexité](<../../10-Evaluation/52-Perplexite-LLM.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
PPL = \exp\left( -\frac{1}{n} \times \sum_{t=1}^{n} \ln P(x_t \mid x_{<t}, c) \right)
$$

La perplexité dit entre combien de tokens équiprobables le modèle hésite en moyenne. Plus elle est basse, moins le texte surprend le modèle.

## Les symboles, un par un

$$
PPL
$$

La perplexité, un réel ≥ 1, ou +∞ si un token réel avait la probabilité 0 ; elle se lit comme un « nombre de choix équiprobables ». Valeur renvoyée par `perplexite(probas)`.

$$
n
$$

Le nombre de tokens notés, un entier ≥ 1 ; il dépend du tokenizer (démonstration 6). Variable `len(probas)` ; sans token, la perplexité n'est pas définie et la fonction renvoie `None`.

$$
P(x_t \mid x_{<t}, c)
$$

La probabilité que le modèle donnait au token réellement présent en position t, sachant les tokens d'avant et le contexte c (fiche 23) : un réel de ]0 ; 1]. Chaque élément de la liste `probas`.

$$
\ln
$$

Le logarithme naturel ; il transforme chaque probabilité en une surprise −ln p ≥ 0, mesurée en nats. Dans le programme, `math.log`.

$$
\exp
$$

L'exponentielle ; elle remet la moyenne des logarithmes à l'échelle d'un nombre de choix. Dans le programme, `math.exp`.

$$
\bar{L}
$$

La perte moyenne d'entropie croisée, en nats par token (fiche 06) : l'exposant de la formule, changé de signe. Argument de `perplexite_depuis_perte`.

$$
H_2
$$

La même perte mesurée en bits, H₂ = L̄ / ln 2 ; on a alors PPL = 2^H₂ (démonstration 4). Variable `h2` dans `main`.

$$
|V|
$$

La taille du vocabulaire du tokenizer, de quelques dizaines de milliers à plus de cent mille tokens pour un LLM ; c'est la perplexité d'un modèle uniforme (démonstration 2).

## Le mécanisme, avant les preuves

Ce qui entre : les n probabilités que le modèle donnait aux tokens réellement écrits. Le logarithme transforme chacune en surprise : 0 pour une probabilité de 1, ln 2 ≈ 0,69 pour une chance sur deux, beaucoup plus pour un token inattendu. La somme additionne ces surprises, comme la vraisemblance multiplie les probabilités (fiche 23). La division par n en fait une surprise moyenne par token, qui ne dépend plus de la longueur du texte : on peut comparer un texte de 10 tokens et un texte de 10 000. Le signe moins rend cette moyenne positive, et l'exponentielle la ramène à une échelle intuitive : un modèle qui donne 1/k à chaque token réel a une perplexité exactement k. Pourquoi l'exponentielle d'une moyenne de logarithmes, plutôt que l'inverse de la moyenne des probabilités ? Parce que la première est l'inverse de la moyenne géométrique (démonstration 1), qui reste fidèle à la probabilité du texte entier, alors que la moyenne arithmétique masque les surprises isolées (démonstration 5). Pourquoi des logarithmes plutôt que le produit direct ? Parce que le produit de milliers de probabilités tombe à 0 en flottants (fiche 23, démonstration 5). Ce qui sort : un nombre ≥ 1, d'autant plus bas que le modèle attendait le texte ; jamais une mesure de vérité.

Le petit film chiffré : trois tokens vus avec les probabilités 1/2, 1/4 et 1/8.

| Opération | Token 1 | Token 2 | Token 3 | Résultat |
|---|---|---|---|---|
| logarithme | −0,69315 | −1,38629 | −2,07944 | |
| somme | | | | −4,15888 |
| division par n = 3 | | | | −1,38629 |
| changement de signe | | | | 1,38629 |
| exponentielle | | | | 4 |

La perplexité 4 est la moyenne géométrique des inverses 2, 4 et 8 : ∛(2 × 4 × 8) = ∛64 = 4. Pour un développeur Java, c'est un indicateur de « surprise moyenne » qu'on calcule comme une moyenne de temps de réponse en échelle logarithmique : une seule valeur extrême pèse beaucoup plus que dans une moyenne simple.

## Démonstration 1 — C'est l'inverse de la moyenne géométrique

**Ce qu'on démontre.** Pour n probabilités strictement positives pₜ = P(xₜ | x₍<ₜ₎, c) :

$$
PPL = \prod_{t=1}^{n} p_t^{-1/n} = \left( \prod_{t=1}^{n} p_t \right)^{-1/n}
$$

**L'idée.** L'exponentielle transforme une somme en produit, et un facteur 1/n en exposant 1/n : la moyenne des logarithmes devient une racine n-ième du produit.

**La preuve, pas à pas.**

**Étape 1.** On sort la somme de l'exponentielle, parce que exp(a + b) = exp(a) × exp(b) :

$$
\exp\Big( -\frac{1}{n} \sum_{t} \ln p_t \Big) = \prod_{t} \exp\Big( -\frac{1}{n} \ln p_t \Big)
$$

**Étape 2.** Chaque facteur vaut pₜ^(−1/n), parce que exp(c ln p) = p^c.

**Étape 3.** Un produit de puissances de même exposant est la puissance du produit, parce que aᶜ bᶜ = (ab)ᶜ. ∎

**Vérification chiffrée.** Pour les probabilités 0,6 ; 0,5 ; 0,4 ; 0,5 (modèle A du cas 1), le produit vaut 0,06 et 0,06^(−1/4) ≈ 2,02052, la même valeur que la forme logarithmique ; le programme vérifie aussi le modèle B.

**Ce que la preuve révèle du mécanisme.** La perplexité ne dépend que du produit des probabilités et de n : c'est la probabilité du texte entier, ramenée à une probabilité « moyenne » par token, puis inversée. Deux textes de même probabilité totale et de même longueur ont la même perplexité, quelle que soit la répartition des surprises.

**Conséquence pour un agent.** On calcule toujours la forme logarithmique (somme de logprobs), jamais la forme produit, qui sous-déborde sur un document long ; les deux sont égales en mathématiques, pas en flottants (leçon, point 6).

## Démonstration 2 — Un modèle uniforme sur |V| tokens a une perplexité |V|

**Ce qu'on démontre.** Si chaque token reçoit la probabilité 1/|V|, alors PPL = |V| ; plus généralement, si le token réel reçoit 1/k à chaque position, PPL = k :

$$
\exp\Big( -\frac{1}{n} \sum_{t=1}^{n} \ln \frac{1}{k} \Big) = \exp(\ln k) = k
$$

**L'idée.** Toutes les surprises valent ln k ; leur moyenne aussi, et l'exponentielle de ln k redonne k.

**La preuve, pas à pas.**

**Étape 1.** Chaque terme vaut ln(1/k) = −ln k, parce que ln(1/x) = −ln x.

**Étape 2.** La somme de n termes égaux vaut n × (−ln k), et sa moyenne −ln k.

**Étape 3.** On change le signe et on prend l'exponentielle : exp(ln k) = k. ∎

**Vérification chiffrée.** Sept tokens à 0,25 donnent 4 ; dix tokens à 1/50 000 donnent 50 000 : un modèle qui tirerait au hasard dans un vocabulaire de 50 000 tokens a une perplexité de 50 000.

**Ce que la preuve révèle du mécanisme.** D'où la lecture « facteur de branchement effectif » : une perplexité de k veut dire que le modèle hésite comme s'il choisissait au hasard entre k tokens à chaque pas. Un bon modèle de langue descend à quelques unités sur un texte courant.

**Conséquence pour un agent.** La perplexité d'un modèle uniforme donne une borne de référence : un modèle qui dépasse |V| sur un texte fait pire que le hasard (démonstration 3), signe d'un texte hors domaine ou d'un modèle sûr de lui et faux.

## Démonstration 3 — Bornes : au moins 1, et pas de plafond

**Ce qu'on démontre.** Si chaque pₜ est dans ]0 ; 1], alors

$$
PPL \ge e^{0} = 1, \qquad PPL = 1 \iff p_t = 1 \text{ pour tout } t
$$

et la perplexité n'a pas de borne supérieure : elle peut dépasser |V|.

**L'idée.** Chaque surprise −ln pₜ est positive ou nulle ; leur moyenne aussi ; l'exponentielle d'un nombre positif est au moins 1. Rien n'empêche, en revanche, une surprise d'être énorme.

**La preuve, pas à pas.**

**Étape 1.** pₜ ≤ 1 donne ln pₜ ≤ 0, parce que ln est croissante et ln 1 = 0 ; donc −ln pₜ ≥ 0.

**Étape 2.** Une moyenne de nombres positifs ou nuls est positive ou nulle, donc l'exposant est ≥ 0, et exp est croissante : PPL ≥ e⁰ = 1.

**Étape 3.** L'égalité exige que la moyenne soit nulle, donc chaque surprise nulle, donc chaque pₜ = 1, parce qu'une somme de termes positifs n'est nulle que si chacun l'est.

**Étape 4.** Quand un pₜ tend vers 0, sa surprise tend vers +∞, donc la perplexité aussi : il n'y a pas de plafond. ∎

**Vérification chiffrée.** Trois tokens de probabilité 1 donnent exactement 1. Contre-exemple à l'idée « PPL ≤ |V| » (leçon, point 5) : vocabulaire de 4 tokens, le modèle met 0,97 sur le token 0 et 0,01 sur chacun des autres, mais le texte réel est toujours le token 1 ; la perplexité vaut 1 / 0,01 = 100, soit 25 fois |V|. L'entropie propre de cette distribution vaut pourtant H(Q) ≈ 0,1677, et exp(H(Q)) ≈ 1,1826 : le modèle se croit presque certain.

**Ce que la preuve révèle du mécanisme.** La borne basse est atteinte seulement par un modèle parfait ; la borne haute n'existe pas, parce qu'un modèle peut se tromper avec une certitude arbitraire. Ce qui est borné par |V|, c'est l'entropie propre exp(H(Q)) d'une distribution, pas la perplexité sur un texte.

**Conséquence pour un agent.** Le programme renvoie +∞ si un token réel avait la probabilité 0, et refuse une « probabilité » de 1,2 (`ValueError`) : une perplexité infinie ou inférieure à 1 dans un tableau de bord est une alerte de qualité des données, pas une mesure du modèle.

## Démonstration 4 — Lien avec l'entropie croisée et avec les bits

**Ce qu'on démontre.** Si L̄ est la perte moyenne d'entropie croisée en nats et H₂ = L̄ / ln 2 la même perte en bits, alors

$$
PPL = e^{\bar{L}} = 2^{H_2}
$$

**L'idée.** L'exposant de la formule est exactement la perte moyenne (fiche 06) ; changer la base du logarithme change l'unité de la perte, mais pas le nombre de choix qu'elle représente.

**La preuve, pas à pas.**

**Étape 1.** Avec une cible one-hot, la perte d'un token vaut −ln pₜ (fiche 06, démonstration 1) ; la moyenne sur n tokens est L̄, donc PPL = e^L̄ par définition.

**Étape 2.** On écrit 2^H₂ = e^(H₂ ln 2), parce que aˣ = e^(x ln a).

**Étape 3.** On remplace H₂ par L̄ / ln 2 : e^((L̄ / ln 2) × ln 2) = e^L̄. ∎

**Vérification chiffrée.** Une perte de 1,00781 nat vaut 1,00781 / 0,69315 ≈ 1,45396 bit ; e^1,00781 ≈ 2,73959 et 2^1,45396 ≈ 2,73959. Une perte de 1,5 bit donne 2^1,5 = 2√2 ≈ 2,828.

**Ce que la preuve révèle du mécanisme.** Baisser la perte de 1 bit divise la perplexité par 2 ; baisser la perte de 1 nat la divise par e ≈ 2,718. Une petite différence de perte est donc une différence multiplicative de perplexité.

**Conséquence pour un agent.** Quand un rapport donne une perte, on vérifie son unité avant de la convertir : appliquer 2^x à une perte en nats est une erreur classique (exercice 7).

## Démonstration 5 — Une seule grosse surprise pèse lourd

**Ce qu'on démontre.** La moyenne géométrique est au plus la moyenne arithmétique (inégalité des moyennes), donc

$$
PPL = \frac{1}{\text{moyenne géométrique}} \ge \frac{1}{\text{moyenne arithmétique}}
$$

et remplacer une seule probabilité p par p′ multiplie la perplexité par (p / p′)^(1/n).

**L'idée.** La moyenne géométrique est tirée vers le bas par la plus petite valeur, bien plus que la moyenne arithmétique ; et un seul facteur du produit change le produit dans le même rapport.

**La preuve, pas à pas.**

**Étape 1.** Le logarithme est concave : la moyenne des logarithmes est au plus le logarithme de la moyenne (inégalité de Jensen), soit (1/n) ∑ ln pₜ ≤ ln((1/n) ∑ pₜ).

**Étape 2.** On applique l'exponentielle, croissante : moyenne géométrique ≤ moyenne arithmétique ; on prend l'inverse, ce qui renverse l'inégalité, parce que x ↦ 1/x est décroissante sur ]0 ; +∞[.

**Étape 3.** Si un seul pₜ = p devient p′, le produit est multiplié par p′ / p ; par la démonstration 1, la perplexité, produit à la puissance −1/n, est multipliée par (p′/p)^(−1/n) = (p/p′)^(1/n). ∎

**Vérification chiffrée.** Modèle A : 1 / moyenne arithmétique = 1 / 0,5 = 2 ≤ 2,02052 ; modèle B : 1 / 0,6875 ≈ 1,45455 ≤ 2,28863. Remplacer un token à 0,5 par un token à 0,005 parmi 4 multiplie la perplexité par (0,5 / 0,005)^(1/4) = 100^(1/4) = √10 ≈ 3,16228. Neuf tokens à 0,9 et un dixième à 0,001 donnent une perplexité de 2,194, alors que neuf tokens à 0,9 seuls donneraient 1 / 0,9 ≈ 1,11111.

**Ce que la preuve révèle du mécanisme.** La perplexité punit les surprises isolées : un seul token très improbable, souvent un montant, un nom propre ou un identifiant, suffit à doubler le score d'un texte par ailleurs très prévisible.

**Conséquence pour un agent.** Pour comparer deux modèles, on ne regarde pas la confiance moyenne sur les bons tokens mais la perplexité (cas 1) ; et pour diagnostiquer, on regarde quels tokens portent la surprise.

## Démonstration 6 — À probabilité de phrase égale, la perplexité dépend du découpage

**Ce qu'on démontre.** Si deux tokenizers donnent au même texte la même probabilité totale P, avec n₁ et n₂ tokens, alors

$$
PPL_1 = P^{-1/n_1}, \qquad PPL_2 = P^{-1/n_2}, \qquad n_2 > n_1 \;\Longrightarrow\; PPL_2 < PPL_1
$$

**L'idée.** La même surprise totale est répartie sur plus de tokens : la surprise moyenne par token baisse, sans que le modèle soit meilleur.

**La preuve, pas à pas.**

**Étape 1.** Par la démonstration 1, PPL = P^(−1/n), où P est la probabilité du texte entier.

**Étape 2.** On écrit P^(−1/n) = exp(−ln P / n) ; comme P < 1, −ln P > 0, et −ln P / n décroît quand n augmente.

**Étape 3.** L'exponentielle est croissante, donc PPL décroît quand n augmente, à P fixé. ∎

**Vérification chiffrée.** La phrase « le vol est annulé » de la leçon (point 8) : par mots, les probabilités 0,5 ; 0,5 ; 0,2 donnent P = 0,05 et PPL = 20^(1/3) ≈ 2,7144 ; découpée en sous-mots (« annul » à 0,25 puis « é » à 0,8, de produit 0,2), P vaut toujours 0,05, mais PPL = 20^(1/4) ≈ 2,1147.

**Ce que la preuve révèle du mécanisme.** La perplexité par token mélange la qualité du modèle et la finesse du tokenizer. Seule la log-vraisemblance totale du même texte, ou une perplexité ramenée au mot ou au caractère, compare deux modèles aux tokenizers différents.

**Conséquence pour un agent.** Avant de choisir entre deux modèles, on calcule la log-vraisemblance totale de chacun sur le même jeu de textes et on la divise par le même nombre de mots (cas 2).

## Exemple simple, à la main

Trois tokens vus avec les probabilités 1/2, 1/4 et 1/8. Produit : 1/2 × 1/4 × 1/8 = 1/64.

$$
PPL = \left( \frac{1}{64} \right)^{-1/3} = 64^{1/3} = 4
$$

On le retrouve par la forme logarithmique : ln(1/2) + ln(1/4) + ln(1/8) ≈ −0,69315 − 1,38629 − 2,07944 = −4,15888 ; divisé par 3 : −1,38629 ; changé de signe : 1,38629 = ln 4 ; exponentielle : 4. Le modèle a hésité comme entre 4 choix équiprobables, la moyenne géométrique de 2, 4 et 8.

## Cas d'usage complexes, démontrés

Les probabilités, pertes, volumes et seuils de ces cas sont illustratifs : ils dépendent du modèle, du tokenizer et du jeu de test.

### Cas 1 — Assureur auto et santé : deux modèles, deux classements contraires

**Contexte.** Un assureur auto et santé, supervisé par la CBUAE, choisit le modèle de son agent de suivi des sinistres. Deux modèles candidats sont évalués sur la même réponse de référence de 4 tokens, dont le dernier est le montant de la franchise. L'équipe dispose de la probabilité que chaque modèle donnait à chaque token réel. Sur le jeu complet, environ 2 000 réponses de référence (illustratif), le même calcul se répète.

**Données.** Modèle A : 0,6 ; 0,5 ; 0,4 ; 0,5. Modèle B : 0,9 ; 0,9 ; 0,9 ; 0,05 (le token à 0,05 est le montant).

**Calcul pas à pas.**

**Étape 1.** Moyennes arithmétiques : A, (0,6 + 0,5 + 0,4 + 0,5) / 4 = 0,5 ; B, (0,9 × 3 + 0,05) / 4 = 0,6875.

**Étape 2.** Surprises par token : A, 0,51083 ; 0,69315 ; 0,91629 ; 0,69315, de moyenne 0,70335 ; B, 0,10536 trois fois et 2,99573, de moyenne 0,82795.

**Étape 3.** Perplexités, par la forme produit (démonstration 1) :

$$
PPL_A = 0{,}06^{-1/4} \approx 2{,}02052, \qquad PPL_B = 0{,}03645^{-1/4} \approx 2{,}28863
$$

**Décision de l'agent.** L'équipe retient le modèle A, de perplexité plus basse (2,02052 < 2,28863), et ajoute une règle : tout montant écrit par l'agent est relu dans le dossier par un outil, puisque c'est sur ce type de token que la surprise se concentre.

**Contre-calcul.** Avec la moyenne arithmétique, B semble meilleur (0,6875 > 0,5) : il est très sûr sur les trois mots courants, mais ne donnait que 5 % au montant réellement écrit. Choisir B, c'est choisir le modèle qui se trompe sur la seule information qui coûte : une franchise mal annoncée engage une réponse écrite au client qu'il faudra corriger.

**Sensibilité.** La valeur de bascule est la probabilité p du montant pour laquelle B égale A : 0,9³ × p = 0,729 p = 0,06, donc p = 0,06 / 0,729 ≈ 0,0823. Si B passe de 0,05 à 0,055 (+10 %), sa perplexité ne descend qu'à 2,23474, toujours au-dessus de 2,02052 : la décision tient.

**En production.** On suit la perplexité par catégorie de token (montants, noms propres, texte courant) sur le jeu de référence figé, à chaque nouvelle version du modèle ; une hausse sur les montants déclenche une revue avant déploiement. Pour comparer, le repère du hasard est la taille du vocabulaire : un modèle uniforme sur 50 000 tokens aurait une perplexité de 50 000. Les obligations de l'assureur envers ses clients relèvent de la CBUAE et sont à confirmer avec le texte en vigueur.

### Cas 2 — Entité de services publics en ligne : comparer deux modèles arabes aux tokenizers différents

**Contexte.** Une entité de services publics en ligne, accessible par UAE Pass, choisit le modèle de son assistant bilingue arabe et anglais entre deux modèles arabes ouverts. Leurs tokenizers découpent l'arabe très différemment. L'équipe évalue les deux modèles sur le même jeu de 1 000 mots de demandes réelles anonymisées. Les chiffres des deux modèles sont illustratifs et ne décrivent aucun modèle réel.

**Données.** Modèle A : 1 600 tokens pour les 1 000 mots, log-vraisemblance totale −2 900 nats. Modèle B : 2 300 tokens, log-vraisemblance totale −3 100 nats. Nombre de mots : 1 000.

**Calcul pas à pas.**

**Étape 1.** Perplexité par token :

$$
PPL_A = e^{2\,900 / 1\,600} = e^{1{,}8125} \approx 6{,}126, \qquad PPL_B = e^{3\,100 / 2\,300} \approx e^{1{,}34783} \approx 3{,}849
$$

**Étape 2.** Perplexité par mot, même dénominateur pour les deux :

$$
PPL_A^{\text{mot}} = e^{2\,900 / 1\,000} = e^{2{,}9} \approx 18{,}174, \qquad PPL_B^{\text{mot}} = e^{3{,}1} \approx 22{,}198
$$

**Étape 3.** Comparaison directe des log-vraisemblances totales du même texte : −2 900 > −3 100, donc A donne au texte une probabilité e^200 fois plus grande.

**Décision de l'agent.** L'équipe retient le modèle A : sur le même texte, il est moins surpris (perplexité par mot 18,174 contre 22,198), même si sa perplexité par token est plus haute. Le choix final combine cette mesure et un jeu d'évaluation de tâches.

**Contre-calcul.** Par token, B semble nettement meilleur (3,849 contre 6,126), mais seulement parce que son tokenizer produit 2 300 / 1 600 = 1,4375 fois plus de tokens (démonstration 6). Choisir B sur ce critère, c'est choisir le tokenizer le plus fin, pas le meilleur modèle, et dégrader les réponses aux usagers.

**Sensibilité.** Si le tokenizer de B produisait 10 % de tokens en moins (2 070), sa perplexité par token monterait à e^(3 100 / 2 070) ≈ 4,471, sans que le modèle change ; sa perplexité par mot, elle, resterait 22,198. La valeur de bascule est une log-vraisemblance totale de −2 900 nats pour B : au-dessus, B passerait devant A.

**En production.** On suit la perplexité par mot sur un jeu figé de demandes anonymisées, en arabe et en anglais séparément, à chaque changement de version. Le traitement de ces demandes relève de la PDPL, dont l'application au cas de l'entité est à confirmer avec le texte en vigueur.

### Cas 3 — Banque de détail à Dubaï : adapter un modèle à la finance islamique sans abîmer le reste

**Contexte.** Une banque de détail de Dubaï adapte un modèle ouvert à ses documents de finance islamique (contrats de Murabaha et d'Ijara, fiches produits) pour son assistant de conseillers. L'équipe mesure la perte moyenne (valeurs illustratives) sur deux jeux tenus à part : un jeu du domaine et un jeu de textes généraux (courriers, réponses clients), pour vérifier que le modèle n'a pas « oublié » le reste. Règle d'adoption (illustrative) : gain sur le domaine, et hausse de la perplexité générale d'au plus 10 %.

**Données.** Pertes moyennes en nats par token. Domaine : 2,9 avant, 2,1 après. Général : 2,3 avant, 2,45 après. Seuil de hausse générale : 10 %.

**Calcul pas à pas.**

**Étape 1.** Perplexités du domaine et gain (ΔPPL = avant − après, positif quand le modèle s'améliore, leçon point 7) :

$$
e^{2{,}9} \approx 18{,}174 \;\to\; e^{2{,}1} \approx 8{,}166, \qquad \Delta PPL \approx 10{,}008 > 0
$$

**Étape 2.** Perplexités générales et hausse relative :

$$
e^{2{,}3} \approx 9{,}974 \;\to\; e^{2{,}45} \approx 11{,}588, \qquad \frac{11{,}588}{9{,}974} - 1 \approx 16{,}18\ \%
$$

**Étape 3.** Perte générale maximale admise : une hausse de 10 % de la perplexité correspond à une hausse de ln 1,1 ≈ 0,09531 nat de la perte, donc 2,3 + 0,09531 = 2,39531 nats, soit une perplexité de 10,972.

**Décision de l'agent.** La version n'est pas adoptée : le gain sur le domaine est réel (ΔPPL ≈ 10,008), mais la perplexité générale monte de 16,18 %, au-delà du seuil de 10 %. L'équipe réentraîne en mélangeant des textes généraux aux documents du domaine, puis remesure.

**Contre-calcul.** Deux raccourcis mènent à la mauvaise décision. Premier raccourci : ne regarder que le jeu du domaine. La perplexité y est divisée par 18,174 / 8,166 ≈ 2,226, et la version serait adoptée sans voir que la perplexité générale monte de 16,18 %, soit 6,18 points au-delà du seuil. L'équipe aurait déployé un modèle excellent pour citer une Murabaha et moins bon pour rédiger un courrier au client. Second raccourci : appliquer le seuil de 10 % à la perte au lieu de la perplexité. La perte générale ne monte que de (2,45 − 2,3) / 2,3 ≈ 6,52 %, sous les 10 %, et la version passerait aussi. L'écart vient de ce que la perplexité est l'exponentielle de la perte : une hausse de 0,15 nat de la perte multiplie la perplexité par

$$
e^{0{,}15} \approx 1{,}1618 ,
$$

c'est-à-dire + 16,18 %. La perplexité ne suffit d'ailleurs pas à décider la mise en production : les métriques de tâche (fidélité, justesse) restent le juge final.

**Sensibilité.** La valeur de bascule est une perte générale de 2,39531 nats : la hausse observée de 0,15 nat (2,45 − 2,3) dépasse la marge de 0,09531 nat. Une marge de 10 % en perplexité est donc une marge de moins d'un dixième de nat en perte : les deux échelles doivent être converties avant de fixer un seuil.

**En production.** On suit les deux perplexités à chaque nouvelle version, sur des jeux de test figés, avec la règle d'adoption ci-dessus. Les contenus de finance islamique doivent par ailleurs être validés par les instances compétentes de la banque ; leur cadre est à confirmer avec le texte en vigueur.

### Cas 4 — Cabinet RH multi-émirats : écarter les pages d'OCR illisibles avant l'indexation

**Contexte.** Un cabinet RH multi-émirats indexe dans un RAG les documents des candidats : contrats, attestations, diplômes scannés, environ 1 200 pages par mois (illustratif). Certaines pages passent par un OCR qui produit du charabia (colonnes mélangées, arabe lu de gauche à droite). Un petit modèle de référence calcule la perplexité de chaque page ; une page au-dessus du 99e percentile des pages saines du mois précédent part en revue humaine au lieu d'être indexée.

**Données.** Surprise moyenne d'un token sain : 2,8 nats (perplexité e^2,8 ≈ 16,44). Surprise d'un token illisible : 9,0 nats (perplexité e⁹ ≈ 8 103). Seuil mesuré au 99e percentile : 40. Pages étudiées : 5 %, 12 % et 30 % de tokens illisibles.

**Calcul pas à pas.**

**Étape 1.** Perte moyenne d'une page dont une part f des tokens est illisible : (1 − f) × 2,8 + f × 9,0. Pour f = 5 % : 0,95 × 2,8 + 0,05 × 9 = 3,11 ; pour f = 30 % : 0,7 × 2,8 + 0,3 × 9 = 4,66.

**Étape 2.** Perplexités de page :

$$
e^{3{,}11} \approx 22{,}42, \qquad e^{4{,}66} \approx 105{,}64
$$

et pour f = 12 %, e^3,544 ≈ 34,61.

**Étape 3.** Part de bascule f*, où la perplexité atteint exactement le seuil : (1 − f) × 2,8 + 9 f = ln 40 ≈ 3,68888, donc

$$
f^{*} = \frac{\ln 40 - 2{,}8}{9{,}0 - 2{,}8} \approx 0{,}14337
$$

**Décision de l'agent.** La page à 30 % de tokens illisibles (perplexité 105,64 > 40) part en revue humaine ; les pages à 5 % et 12 % (22,42 et 34,61) sont indexées. Toute page dont plus de 14,34 % des tokens sont illisibles est écartée.

**Contre-calcul.** Avec l'inverse de la moyenne arithmétique des probabilités, la page à 30 % passerait : les probabilités valent e^(−2,8) ≈ 0,06081 et e^(−9) ≈ 0,0001234, de moyenne 0,7 × 0,06081 + 0,3 × 0,0001234 ≈ 0,0426, d'inverse 23,47 < 40 (démonstration 5). Indexée, cette page de charabia ferait halluciner l'agent sur la date d'expiration d'un visa ou le montant d'un salaire, et la correction coûterait un échange de plus avec le candidat.

**Sensibilité.** Si le seuil monte de 10 % (44, ln 44 ≈ 3,78419), la part de bascule passe à 0,15874, soit 15,87 % de tokens illisibles. Le seuil est un percentile mesuré, pas une constante : il se recalcule quand l'OCR ou le modèle de référence change.

**En production.** On suit la part de pages écartées chaque mois et le taux de réponses de l'agent corrigées par l'équipe sur les dossiers concernés. Les documents des candidats contiennent des données personnelles : leur conservation et leur revue humaine suivent les règles de protection des données applicables (PDPL, ou les lois propres au DIFC et à l'ADGM selon le lieu), à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Calculer la perplexité de quatre tokens tous à 0,25.

**Exercice 2.** Deux tokens à 0,5 et 0,125. Calculer la perplexité.

**Exercice 3.** Une perte moyenne vaut 1,5 bit par token. Quelle est la perplexité ?

**Exercice 4.** Montrer que remplacer un token à 0,5 par un token à 0,005 multiplie la perplexité de 4 tokens par √10.

**Exercice 5.** La perte moyenne d'entropie croisée vaut 1,00781 nat. Quelle est la perplexité ?

**Exercice 6 (cas modifié).** Dans le cas 4, une page contient 12 % de tokens illisibles. Calculer sa perte moyenne et sa perplexité, et dire si elle part en revue.

**Exercice 7 (trouver l'erreur).** Un collègue convertit une perte moyenne de 1,00781 nat en perplexité en calculant 2^1,00781 ≈ 2,01086. Trouver l'erreur et donner la bonne valeur de deux façons.

**Exercice 8 (redémontrer de mémoire).** Redémontrer, sans regarder, que la perplexité est l'inverse de la moyenne géométrique des probabilités, puis qu'elle est au moins l'inverse de leur moyenne arithmétique.

## Corrigé

**Exercice 1.** Chaque surprise vaut ln 4 ; leur moyenne aussi ; PPL = e^(ln 4) = 4. C'est un modèle uniforme sur 4 choix (démonstration 2).

**Exercice 2.** Produit 0,5 × 0,125 = 1/16 ; PPL = (1/16)^(−1/2) = 16^(1/2) = 4.

**Exercice 3.** PPL = 2^1,5 = 2 × 2^0,5 = 2√2 ≈ 2,828 (démonstration 4).

**Exercice 4.** Le produit est multiplié par 0,005 / 0,5 = 1/100 ; la perplexité, produit à la puissance −1/4, est multipliée par 100^(1/4) = √10 ≈ 3,162 (démonstration 5).

**Exercice 5.** PPL = e^1,00781 ≈ 2,73959 : c'est le lot de la fiche 06.

**Exercice 6.** Perte : 0,88 × 2,8 + 0,12 × 9 = 2,464 + 1,08 = 3,544 nats ; perplexité e^3,544 ≈ 34,61 < 40. La page est indexée, ce qui est cohérent avec 12 % < 14,34 %, la part de bascule.

**Exercice 7.** L'erreur : la base 2 ne s'applique qu'à une perte en bits, et 1,00781 est en nats. Première façon : PPL = e^1,00781 ≈ 2,73959. Seconde façon : convertir en bits, H₂ = 1,00781 / ln 2 ≈ 1,45396, puis 2^1,45396 ≈ 2,73959. Le calcul fautif sous-estime la perplexité d'environ 27 % (2,01086 / 2,73959 ≈ 0,734).

**Exercice 8.** Étape 1 : exp(−(1/n) ∑ ln pₜ) = ∏ exp(−(1/n) ln pₜ) = ∏ pₜ^(−1/n) = (∏ pₜ)^(−1/n), l'inverse de la moyenne géométrique. Étape 2 : ln est concave, donc (1/n) ∑ ln pₜ ≤ ln((1/n) ∑ pₜ), et en appliquant exp, moyenne géométrique ≤ moyenne arithmétique. Étape 3 : x ↦ 1/x est décroissante, donc PPL = 1 / moyenne géométrique ≥ 1 / moyenne arithmétique. ∎

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`perplexite(probas)`** — Cette fonction se comporte comme un examinateur qui relit, token après token, la copie d'un modèle de langue et note chaque fois la probabilité que le modèle avait accordée au bon choix : elle reçoit cette liste de probabilités, renvoie `None` si la liste est vide, puis parcourt chaque valeur en levant une `ValueError` si l'une sort de l'intervalle de 0 à 1, et renvoie aussitôt l'infini, `math.inf`, dès qu'un token réel avait reçu une probabilité nulle. Sinon, elle additionne les logarithmes népériens, divise cette somme par le nombre de tokens, change le signe et passe à l'exponentielle, ce qui donne PPL = exp(−(1/n) Σ ln pₜ) ; pour les probabilités 1/2, 1/4 et 1/8, elle renvoie 4. C'est la pièce centrale du programme, que `main` appelle dans toutes les démonstrations et que le cas de l'assurance emploie pour départager ses deux modèles.

**`perplexite_depuis_perte(perte_moyenne_nats)`** — Celle-ci est le traducteur de bureau qui fait passer un nombre d'une langue dans une autre : on lui tend une perte moyenne d'entropie croisée par token, exprimée en nats, et elle se contente d'en prendre l'exponentielle, puisque la perplexité n'est rien d'autre que exp(L̄). Elle renvoie ce nombre réel sans aucune vérification et sert dans le cas bancaire, où les quatre pertes 2,9, 2,1, 2,3 et 2,45 nats deviennent les perplexités 18,174, 8,166, 9,974 et 11,588 ; elle rappelle aussi, en creux, qu'une perte en nats appelle la base e et non la base 2, ce qui est précisément l'erreur de l'exercice 7.

**`r5(xs)`** — Cette petite fonction est le greffier qui recopie au propre une liste de mesures en ne gardant que cinq chiffres après la virgule : elle reçoit une liste de nombres et renvoie une nouvelle liste où chacun est arrondi à cinq décimales par `round(x, 5)`, sans toucher à la liste d'origine. Elle ne calcule rien de mathématique, mais elle permet à `main` d'afficher les logarithmes du film, −0,69315, −1,38629 et −2,07944, et de comparer des listes de surprises par des `assert` d'égalité exacte, là où des flottants bruts différeraient au quinzième chiffre.

**`cas_1_deux_modeles_assurance()`** — Cette fonction met en scène un assureur qui doit choisir entre deux modèles ayant répondu à la même question en quatre tokens : le modèle A donne aux bons tokens 0,6, 0,5, 0,4 et 0,5, le modèle B donne trois fois 0,9 puis un piteux 0,05. Elle calcule leurs perplexités, 2,02052 pour A et 2,28863 pour B, puis leurs moyennes arithmétiques, 0,5 contre 0,6875, et montre ainsi que la moyenne préfère B quand la perplexité, sensible à la seule grosse surprise, préfère A ; elle calcule aussi la probabilité de bascule, 0,0823, que le quatrième token de B devrait atteindre pour égaler A (le produit 0,06 de A divisé par 0,729), et la perplexité 2,23474 obtenue en remplaçant 0,05 par 0,055, encore au-dessus de celle de A. Elle affiche ces résultats et renvoie un tuple de dix valeurs, que `main` vérifie une à une.

**`cas_2_tokenizers_public()`** — Ici, une administration compare deux modèles arabes qui découpent le même texte de 1 000 mots en des nombres de tokens différents : A totalise une log-vraisemblance négative de 2 900 nats sur 1 600 tokens, B de 3 100 nats sur 2 300 tokens. La fonction calcule la perplexité par token de chacun, 6,126 pour A et 3,849 pour B, puis la perplexité par mot en divisant par les 1 000 mots communs, 18,174 contre 22,198, et montre que B, vainqueur par token, perd par mot ; elle vérifie aussi que retirer 10 % des tokens de B ferait tomber sa perplexité par token à 4,471 sans rien changer à sa perplexité par mot. Elle affiche la décision, le modèle A, qui a la meilleure log-vraisemblance totale sur le même texte, et renvoie les deux dictionnaires, la valeur 4,471 et les deux choix, B par token et A par mot.

**`cas_3_adaptation_banque()`** — Cette fonction raconte la visite d'un contrôleur qui inspecte une banque après qu'on a spécialisé son modèle en finance islamique : elle part de quatre pertes moyennes, 2,9 nats avant et 2,1 après sur le domaine, 2,3 avant et 2,45 après sur le texte général, les convertit en perplexités par `perplexite_depuis_perte`, puis mesure le gain sur le domaine, 10,008, et la hausse relative sur le texte général, 16,18 %. Elle compare cette hausse au seuil toléré de 10 %, calcule la perte générale maximale admissible, 2,39531 nats, soit une perplexité de 10,972, et conclut au rejet, car la perte a monté de 0,15 nat quand la marge n'était que de 0,09531 ; quatre `assert` internes montrent que les deux raccourcis, regarder le domaine seul ou appliquer le seuil à la perte (6,52 %), auraient fait adopter la version à tort. Elle renvoie le dictionnaire des perplexités, le gain, la hausse, la perte maximale et le booléen `adopte`, qui vaut `False`.

**`cas_4_ocr_rh()`** — Cette fonction se place dans un service des ressources humaines qui numérise des dossiers papier par OCR : chaque token sain y coûte une surprise de 2,8 nats, chaque token illisible 9 nats, et une page part en revue humaine si sa perplexité dépasse 40. Elle définit la fonction interne `ppl_page`, l'applique aux parts de tokens illisibles 5 %, 12 % et 30 %, ce qui donne 22,42, 34,61 et 105,64, puis résout l'équation de bascule pour trouver la part critique 0,14337, ou 0,15874 si le seuil passait à 44 ; elle fait enfin le contre-calcul trompeur par l'inverse de la moyenne arithmétique des probabilités, qui ne donnerait que 23,47 à 30 %, sous le seuil. Elle affiche que seule la page à 30 % part en revue et renvoie le dictionnaire des pages, les deux parts de bascule et la moyenne arithmétique `am`.

**`ppl_page(f)`** — Fonction interne qui vit dans `cas_4_ocr_rh`, elle est le contremaître qui juge d'un coup d'œil une page scannée : elle reçoit la part f de tokens illisibles, forme la surprise moyenne de la page comme un mélange pondéré, (1 − f) × 2,8 + f × 9 nats, en lisant les deux surprises dans la fonction qui l'entoure, et renvoie l'exponentielle de ce mélange, c'est-à-dire la perplexité de la page. Avec f = 0,05, la surprise moyenne vaut 3,11 nats et la perplexité 22,42 ; avec f = 0,30, elle vaut 4,66 nats et la perplexité 105,64, ce qui fait franchir le seuil de 40.

**`main()`** — C'est le chef d'orchestre qui fait défiler toute la fiche dans l'ordre du cours : il refait d'abord le film des logarithmes de 1/2, 1/4 et 1/8 jusqu'à la perplexité 4, puis vérifie les six démonstrations, à savoir l'inverse de la moyenne géométrique, la loi uniforme (4 sur quatre choix, 50 000 sur 50 000), les bornes avec le refus d'une probabilité 1,2 et l'infini pour un zéro, le passage des nats aux bits (1,00781 nat = 1,45396 bit), l'effet d'une seule surprise (facteur √10 ≈ 3,16228) et le piège du tokenizer (2,7144 par mot contre 2,1147 par sous-mot pour la même phrase). Il appelle ensuite les quatre cas, confronte chacune de leurs valeurs renvoyées à des `assert`, recalcule le corrigé des exercices et n'imprime « OK — toutes les vérifications sont passées. » que si tout concorde ; il ne renvoie rien.

```python
"""Démonstration 32 — perplexité : moyenne géométrique, uniforme, bornes, bits, surprise isolée, tokenizer, quatre cas aux EAU."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def perplexite(probas):
    """PPL = exp(−(1/n) Σ ln p). None si aucun token ; +inf si un token réel avait la probabilité 0."""
    if not probas:
        return None
    somme_log = 0.0
    for p in probas:
        if not 0.0 <= p <= 1.0:
            raise ValueError("une probabilité est entre 0 et 1")
        if p == 0.0:
            return math.inf
        somme_log += math.log(p)
    return math.exp(-somme_log / len(probas))


def perplexite_depuis_perte(perte_moyenne_nats: float) -> float:
    """PPL = e^L̄ quand la perte moyenne par token L̄ est en nats."""
    return math.exp(perte_moyenne_nats)


def r5(xs):
    return [round(x, 5) for x in xs]


def cas_1_deux_modeles_assurance():
    """Assurance : deux modèles sur la même réponse de 4 tokens ; moyenne arithmétique contre perplexité."""
    a, b = [0.6, 0.5, 0.4, 0.5], [0.9, 0.9, 0.9, 0.05]
    ppl_a, ppl_b = perplexite(a), perplexite(b)
    moy_a, moy_b = sum(a) / 4, sum(b) / 4
    p_bascule = math.prod(a) / math.prod(b[:3])          # PPL_B = PPL_A  <=>  0.729 p = 0.06
    ppl_b_plus10 = perplexite(b[:3] + [0.055])
    choix_ppl = "A" if ppl_a < ppl_b else "B"
    choix_moy = "A" if moy_a > moy_b else "B"
    print(f"cas 1 ASSUR : A : PPL {ppl_a:.5f}, moyenne {moy_a} ; B : PPL {ppl_b:.5f}, moyenne {moy_b} ;"
          f" produits {math.prod(a):.2f} et {math.prod(b):.5f}")
    print(f"  bascule du 4e token de B : {p_bascule:.5f} ; avec 0.055 : PPL {ppl_b_plus10:.5f} ;"
          f" choix par la perplexité : {choix_ppl}, par la moyenne : {choix_moy}")
    return a, b, ppl_a, ppl_b, moy_a, moy_b, p_bascule, ppl_b_plus10, choix_ppl, choix_moy


def cas_2_tokenizers_public():
    """Secteur public : deux modèles arabes aux tokenizers différents, même texte de 1 000 mots."""
    mots = 1000
    modeles = {"A": (2900.0, 1600), "B": (3100.0, 2300)}   # (−log-vraisemblance totale en nats, nombre de tokens)
    par_token = {k: math.exp(nll / n) for k, (nll, n) in modeles.items()}
    par_mot = {k: math.exp(nll / mots) for k, (nll, _) in modeles.items()}
    b_moins10 = math.exp(3100.0 / (0.9 * 2300))
    choix_token = min(par_token, key=par_token.get)
    choix_mot = min(par_mot, key=par_mot.get)
    print(f"cas 2 PUBLIC : par token A {par_token['A']:.3f}, B {par_token['B']:.3f} ; par mot A {par_mot['A']:.3f},"
          f" B {par_mot['B']:.3f} ; choix par token {choix_token}, par mot {choix_mot}")
    print(f"  B avec 10 % de tokens en moins : par token {b_moins10:.3f}, par mot inchangé {par_mot['B']:.3f}")
    print(f"  décision : modèle {choix_mot} (log-vraisemblance totale −{modeles[choix_mot][0]:.0f} contre"
          f" −{max(nll for nll, _ in modeles.values()):.0f} nats sur le même texte)")
    return par_token, par_mot, b_moins10, choix_token, choix_mot


def cas_3_adaptation_banque():
    """Banque : adaptation à la finance islamique ; gain sur le domaine, perte sur le texte général."""
    dom_av, dom_ap, gen_av, gen_ap = 2.9, 2.1, 2.3, 2.45    # pertes moyennes en nats par token
    seuil = 0.10                                             # hausse tolérée de la PPL générale
    ppl = {k: perplexite_depuis_perte(v) for k, v in (("dom_av", dom_av), ("dom_ap", dom_ap),
                                                         ("gen_av", gen_av), ("gen_ap", gen_ap))}
    delta_dom = ppl["dom_av"] - ppl["dom_ap"]
    hausse_gen = ppl["gen_ap"] / ppl["gen_av"] - 1
    perte_gen_max = gen_av + math.log(1 + seuil)
    adopte = delta_dom > 0 and hausse_gen <= seuil
    print(f"cas 3 BANQUE : domaine {ppl['dom_av']:.3f} -> {ppl['dom_ap']:.3f} (ΔPPL {delta_dom:.3f}) ;"
          f" général {ppl['gen_av']:.3f} -> {ppl['gen_ap']:.3f} (+{hausse_gen:.2%})")
    print(f"  perte générale max {perte_gen_max:.5f} nat (PPL {math.exp(perte_gen_max):.3f}) ; adoptée : {adopte}")
    print(f"  décision : {'adopter' if adopte else 'rejeter et réentraîner avec du texte général'}"
          f" (hausse {gen_ap - gen_av:.2f} nat > marge {math.log(1 + seuil):.5f})")
    # Contre-calcul : les deux raccourcis qui feraient adopter la version à tort
    assert round(ppl["dom_av"] / ppl["dom_ap"], 3) == 2.226                 # domaine seul : PPL divisée par 2,226
    assert round((hausse_gen - seuil) * 100, 2) == 6.18                     # 6,18 points au-delà du seuil
    assert round((gen_ap - gen_av) / gen_av, 4) == 0.0652 < seuil            # seuil appliqué à la perte : 6,52 % « passe »
    assert round(math.exp(gen_ap - gen_av), 4) == 1.1618                     # e^0,15 : + 16,18 % de perplexité
    return ppl, delta_dom, hausse_gen, perte_gen_max, adopte


def cas_4_ocr_rh():
    """RH : pages d'OCR ; part f de tokens illisibles, perplexité de page, seuil au 99e percentile."""
    sain, illisible, seuil = 2.8, 9.0, 40.0                  # surprises en nats ; seuil de PPL

    def ppl_page(f):
        return math.exp((1 - f) * sain + f * illisible)

    pages = {f: ppl_page(f) for f in (0.05, 0.12, 0.30)}
    f_bascule = (math.log(seuil) - sain) / (illisible - sain)
    f_bascule_44 = (math.log(1.1 * seuil) - sain) / (illisible - sain)
    am = 0.7 * math.exp(-sain) + 0.3 * math.exp(-illisible)
    print(f"cas 4 RH : PPL de page f = 5 % : {pages[0.05]:.2f} ; 12 % : {pages[0.12]:.2f} ; 30 % : {pages[0.30]:.2f} ;"
          f" bascule f* = {f_bascule:.5f} (seuil 44 : {f_bascule_44:.5f})")
    print(f"  contre-calcul 1 / moyenne arithmétique à 30 % : {1 / am:.2f} < {seuil:.0f} ; revue : "
          f"{[f for f, v in pages.items() if v > seuil]}")
    print(f"  décision : revue humaine dès {f_bascule:.2%} de tokens illisibles ; pages à 5 % et 12 % indexées")
    return pages, f_bascule, f_bascule_44, am


def main() -> None:
    # Film et exemple simple
    logs = [math.log(x) for x in (1 / 2, 1 / 4, 1 / 8)]
    print(f"film : ln {r5(logs)} ; somme {sum(logs):.5f} ; moyenne {sum(logs) / 3:.5f} ; PPL {math.exp(-sum(logs) / 3):.5f}")
    assert r5(logs) == [-0.69315, -1.38629, -2.07944] and round(sum(logs), 5) == -4.15888
    assert round(-sum(logs) / 3, 5) == 1.38629 and math.isclose(math.exp(-sum(logs) / 3), 4)
    print(f"(1/2, 1/4, 1/8) : PPL = {perplexite([1 / 2, 1 / 4, 1 / 8]):.4f}")
    assert math.isclose(perplexite([1 / 2, 1 / 4, 1 / 8]), 4) and math.isclose(64 ** (1 / 3), 4)

    # Démonstration 1 : inverse de la moyenne géométrique
    a, b = [0.6, 0.5, 0.4, 0.5], [0.9, 0.9, 0.9, 0.05]
    for x in (a, b):
        assert math.isclose(perplexite(x), math.prod(x) ** (-1 / len(x)))
    print(f"démo 1 : A : produit {math.prod(a):.2f}, produit^(−1/4) = {math.prod(a) ** -0.25:.5f} = forme log {perplexite(a):.5f}")

    # Démonstration 2 : uniforme sur V
    assert math.isclose(perplexite([1 / 50_000] * 10), 50_000) and math.isclose(perplexite([0.25] * 7), 4)
    print(f"démo 2 : uniforme sur 4 : {perplexite([0.25] * 7):.4f} ; sur 50 000 : {perplexite([1 / 50_000] * 10):.1f}")

    # Démonstration 3 : bornes ; contre-exemple « PPL ≤ |V| »
    assert perplexite([1.0, 1.0, 1.0]) == 1.0 and perplexite([]) is None and perplexite([0.5, 0.0]) == math.inf
    Q = [0.97, 0.01, 0.01, 0.01]
    h_q = -sum(q * math.log(q) for q in Q)
    print(f"démo 3 : PPL ≥ 1 ; token réel à 0.01 sur |V| = 4 : PPL {perplexite([0.01] * 6):.1f} ; exp(H(Q)) {math.exp(h_q):.4f}")
    assert round(perplexite([0.01] * 6), 6) == 100 and round(math.exp(h_q), 4) == 1.1826 and round(h_q, 4) == 0.1677
    try:
        perplexite([1.2])
    except ValueError:
        pass
    else:
        raise AssertionError("une probabilité > 1 aurait dû être refusée")

    # Démonstration 4 : nats et bits
    L = 1.2
    assert math.isclose(perplexite([math.exp(-L)] * 3), math.exp(L))
    assert math.isclose(math.exp(L), 2 ** (L / math.log(2)))
    h2 = 1.00781 / math.log(2)
    print(f"démo 4 : 1.00781 nat = {h2:.5f} bit ; e^L = {math.exp(1.00781):.5f} = 2^H2 = {2 ** h2:.5f} ; 2^1,5 = {2 ** 1.5:.3f}")
    assert round(h2, 5) == 1.45396 and round(2 ** h2, 5) == 2.73959 and round(2 ** 1.5, 3) == 2.828

    # Démonstration 5 : une seule grosse surprise ; moyenne géométrique ≤ arithmétique ; facteur (p/p')^(1/n)
    for x in (a, b):
        assert perplexite(x) >= 1 / (sum(x) / len(x))
    r = perplexite([0.5, 0.005, 0.5, 0.5]) / perplexite([0.5] * 4)
    neuf = perplexite([0.9] * 9 + [0.001])
    print(f"démo 5 : 1 / moyenne arithmétique A {1 / (sum(a) / 4):.5f}, B {1 / (sum(b) / 4):.5f} ;"
          f" 0.5 -> 0.005 : facteur {r:.5f} ; 9 × 0.9 + 0.001 : PPL {neuf:.3f}")
    assert math.isclose(r, 100 ** 0.25) and round(r, 5) == 3.16228 and round(neuf, 3) == 2.194
    assert round(1 / 0.5, 5) == 2.0 and round(1 / 0.6875, 5) == 1.45455 and round(1 / 0.9, 5) == 1.11111

    # Démonstration 6 : même probabilité de phrase, n différent
    par_mot, par_sous_mot = [0.5, 0.5, 0.2], [0.5, 0.5, 0.25, 0.8]
    print(f"démo 6 : P = {math.prod(par_mot):.2f} dans les deux cas ; PPL par mot {perplexite(par_mot):.4f},"
          f" par sous-mot {perplexite(par_sous_mot):.4f}")
    assert math.isclose(math.prod(par_mot), math.prod(par_sous_mot)) and round(perplexite(par_mot), 4) == 2.7144
    assert round(perplexite(par_sous_mot), 4) == 2.1147 and math.isclose(perplexite(par_sous_mot), 20 ** 0.25)

    # Cas
    a1, b1, pa, pb, ma, mb, pbasc, pb10, cppl, cmoy = cas_1_deux_modeles_assurance()
    assert round(pa, 5) == 2.02052 and round(pb, 5) == 2.28863 and ma == 0.5 and mb == 0.6875
    assert round(math.prod(a1), 10) == 0.06 and round(math.prod(b1), 5) == 0.03645 and cppl == "A" and cmoy == "B"
    assert round(pbasc, 5) == 0.0823 and round(pb10, 5) == 2.23474 and pb10 > pa and round(0.9 ** 3, 3) == 0.729
    assert r5([-math.log(p) for p in a1]) == [0.51083, 0.69315, 0.91629, 0.69315]
    assert r5([-math.log(p) for p in b1]) == [0.10536, 0.10536, 0.10536, 2.99573]
    assert round(-sum(math.log(p) for p in a1) / 4, 5) == 0.70335 and round(-sum(math.log(p) for p in b1) / 4, 5) == 0.82795

    pt, pm, bm10, ct, cm = cas_2_tokenizers_public()
    assert round(pt["A"], 3) == 6.126 and round(pt["B"], 3) == 3.849 and round(pm["A"], 3) == 18.174
    assert round(pm["B"], 3) == 22.198 and ct == "B" and cm == "A" and round(bm10, 3) == 4.471
    assert round(2900 / 1600, 5) == 1.8125 and round(3100 / 2300, 5) == 1.34783 and round(2300 / 1600, 4) == 1.4375

    ppl3, dd, hg, pgm, adopte = cas_3_adaptation_banque()
    assert round(ppl3["dom_av"], 3) == 18.174 and round(ppl3["dom_ap"], 3) == 8.166 and round(dd, 3) == 10.008
    assert round(ppl3["gen_av"], 3) == 9.974 and round(ppl3["gen_ap"], 3) == 11.588 and round(hg, 4) == 0.1618
    assert round(pgm, 5) == 2.39531 and round(math.exp(pgm), 3) == 10.972 and not adopte
    assert round(math.log(1.1), 5) == 0.09531 and round(2.45 - 2.3, 2) == 0.15

    pages, fb, fb44, am = cas_4_ocr_rh()
    assert round(pages[0.05], 2) == 22.42 and round(pages[0.12], 2) == 34.61 and round(pages[0.30], 2) == 105.64
    assert round(fb, 5) == 0.14337 and round(fb44, 5) == 0.15874 and round(1 / am, 2) == 23.47
    assert round(math.exp(2.8), 2) == 16.44 and round(math.exp(9)) == 8103 and round(math.log(40), 5) == 3.68888
    assert round(0.95 * 2.8 + 0.05 * 9, 5) == 3.11 and round(0.7 * 2.8 + 0.3 * 9, 5) == 4.66
    assert round(math.exp(-2.8), 5) == 0.06081 and round(math.exp(-9), 7) == 0.0001234 and round(math.log(44), 5) == 3.78419

    print("Corrigé")
    r4 = perplexite([0.5, 0.005, 0.5, 0.5]) / perplexite([0.5] * 4)
    print(f"  ex1 {perplexite([0.25] * 4):.0f} ; ex2 {perplexite([0.5, 0.125]):.0f} ; ex3 {2 ** 1.5:.3f} ;"
          f" ex4 rapport {r4:.3f} ; ex5 {math.exp(1.00781):.5f}")
    e6 = 0.88 * 2.8 + 0.12 * 9
    print(f"  ex6 perte {e6:.3f}, PPL {math.exp(e6):.2f} < 40 ; ex7 2^1.00781 = {2 ** 1.00781:.5f} au lieu de {math.exp(1.00781):.5f}")
    assert math.isclose(perplexite([0.25] * 4), 4) and math.isclose(perplexite([0.5, 0.125]), 4)
    assert round(2 ** 1.5, 3) == 2.828 and math.isclose(r4, math.sqrt(10)) and round(math.exp(1.00781), 5) == 2.73959
    assert round(e6, 3) == 3.544 and round(math.exp(e6), 2) == 34.61 and round(2 ** 1.00781, 5) == 2.01086
    assert round(math.sqrt(10), 3) == 3.162 and 0.5 * 0.125 == 1 / 16
    # nombres cités dans le texte
    assert round(am, 4) == 0.0426 and 3100 - 2900 == 200 and round(2.01086 / 2.73959, 3) == 0.734
    assert round(0.88 * 2.8, 3) == 2.464 and round(0.12 * 9, 2) == 1.08 and round(math.e, 3) == 2.718
    assert round(1.00781 / 0.69315, 5) == 1.45396 and round(math.log(4), 5) == 1.38629 and round(64 ** (1 / 3), 10) == 4
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
film : ln [-0.69315, -1.38629, -2.07944] ; somme -4.15888 ; moyenne -1.38629 ; PPL 4.00000
(1/2, 1/4, 1/8) : PPL = 4.0000
démo 1 : A : produit 0.06, produit^(−1/4) = 2.02052 = forme log 2.02052
démo 2 : uniforme sur 4 : 4.0000 ; sur 50 000 : 50000.0
démo 3 : PPL ≥ 1 ; token réel à 0.01 sur |V| = 4 : PPL 100.0 ; exp(H(Q)) 1.1826
démo 4 : 1.00781 nat = 1.45396 bit ; e^L = 2.73959 = 2^H2 = 2.73959 ; 2^1,5 = 2.828
démo 5 : 1 / moyenne arithmétique A 2.00000, B 1.45455 ; 0.5 -> 0.005 : facteur 3.16228 ; 9 × 0.9 + 0.001 : PPL 2.194
démo 6 : P = 0.05 dans les deux cas ; PPL par mot 2.7144, par sous-mot 2.1147
cas 1 ASSUR : A : PPL 2.02052, moyenne 0.5 ; B : PPL 2.28863, moyenne 0.6875 ; produits 0.06 et 0.03645
  bascule du 4e token de B : 0.08230 ; avec 0.055 : PPL 2.23474 ; choix par la perplexité : A, par la moyenne : B
cas 2 PUBLIC : par token A 6.126, B 3.849 ; par mot A 18.174, B 22.198 ; choix par token B, par mot A
  B avec 10 % de tokens en moins : par token 4.471, par mot inchangé 22.198
  décision : modèle A (log-vraisemblance totale −2900 contre −3100 nats sur le même texte)
cas 3 BANQUE : domaine 18.174 -> 8.166 (ΔPPL 10.008) ; général 9.974 -> 11.588 (+16.18%)
  perte générale max 2.39531 nat (PPL 10.972) ; adoptée : False
  décision : rejeter et réentraîner avec du texte général (hausse 0.15 nat > marge 0.09531)
cas 4 RH : PPL de page f = 5 % : 22.42 ; 12 % : 34.61 ; 30 % : 105.64 ; bascule f* = 0.14337 (seuil 44 : 0.15874)
  contre-calcul 1 / moyenne arithmétique à 30 % : 23.47 < 40 ; revue : [0.3]
  décision : revue humaine dès 14.34% de tokens illisibles ; pages à 5 % et 12 % indexées
Corrigé
  ex1 4 ; ex2 4 ; ex3 2.828 ; ex4 rapport 3.162 ; ex5 2.73959
  ex6 perte 3.544, PPL 34.61 < 40 ; ex7 2^1.00781 = 2.01086 au lieu de 2.73959
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme calcule la perplexité d'un modèle sur une séquence : l'exponentielle de la perte moyenne par token. Pour comparer deux modèles aux tokenizers différents, on divise la même log-vraisemblance totale par le même nombre de mots.

```text
ALGORITHME Perplexité
ENTRÉE  : probabilités données aux bons tokens p₁ … pₙ
SORTIE  : PPL ≥ 1, ou +∞, ou INDÉFINI si n = 0

  SI n = 0 ALORS RETOURNER INDÉFINI
  somme ← 0
  POUR t DE 1 À n FAIRE
      SI pₜ < 0 OU pₜ > 1 ALORS ERREUR
      SI pₜ = 0 ALORS RETOURNER +∞
      somme ← somme − ln pₜ
  FIN POUR
  RETOURNER exp(somme / n)

ALGORITHME ComparerDeuxModèles
ENTRÉES : log-vraisemblances totales ℓA et ℓB du même texte, nombre de mots m
  RETOURNER le modèle de plus petite exp(−ℓ / m)
```

**Complexité.** O(n) en temps et O(1) en mémoire. Travailler avec la somme des logarithmes évite le zéro machine du produit (fiche 23).

**Du squelette au code.** L'algorithme est la fonction `perplexite(probas)`, et `perplexite_depuis_perte` passe d'une perte moyenne en nats à la perplexité. La comparaison des modèles A et B l'appelle sur deux listes ; les vérifications de `main` relient le résultat à la moyenne géométrique (démonstration 1), à la loi uniforme (démonstration 2) et aux bits (démonstration 4). ComparerDeuxModèles est le calcul `par_mot` de `cas_2_tokenizers_public` ; les autres cas sont `cas_1_deux_modeles_assurance`, `cas_3_adaptation_banque` et `cas_4_ocr_rh`.
