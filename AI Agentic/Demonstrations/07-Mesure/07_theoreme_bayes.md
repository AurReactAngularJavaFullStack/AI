# 07 — Théorème de Bayes : démonstrations

> Fiche : [07 — Théorème de Bayes](<../../Images/07-Mesure/07_theoreme_bayes.md>) · Image : `07_theoreme_bayes.jpg` · Leçon : [Étape 51 — Spécificité, NPV, AUC](<../../10-Evaluation/51-Specificite-NPV-AUC.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
P(H \mid E) = \frac{P(E \mid H) \times P(H)}{P(E)}
$$

H est une hypothèse (« cette réponse est fausse »), E une observation (« le détecteur a sonné »). Bayes met à jour la probabilité de H après avoir vu E.

## Les symboles, un par un

$$
H,\ \neg H
$$

**H** : l'hypothèse dont on cherche la probabilité (réponse fausse, retrait suspect, sinistre frauduleux, facture irrégulière) ; **¬H** se lit « non H », l'hypothèse contraire ; ce sont deux événements qui s'excluent et couvrent tous les cas.

$$
E
$$

**E** : l'observation, ici l'alerte d'un détecteur ou la présence d'un indice ; elle est vraie ou fausse pour chaque cas examiné.

$$
P(H) = \pi
$$

**P(H)** : le taux de base, ou prévalence, noté π comme dans la leçon 51 : la part des cas où H est vraie avant toute observation, dans [0 ; 1] ; en Python, l'argument `base`.

$$
P(E \mid H) = Se
$$

**P(E | H)** : la sensibilité Se du détecteur, la part des cas H qu'il signale, dans [0 ; 1] ; en Python, l'argument `sensibilite`.

$$
P(E \mid \neg H) = \alpha = 1 - Sp
$$

**P(E | ¬H)** : le taux de fausses alertes α, la part des cas ¬H signalés à tort, égal à 1 − Sp avec la spécificité Sp de la leçon 51 ; en Python, l'argument `fausse_alerte`.

$$
P(E)
$$

**P(E)** : la probabilité de voir l'alerte, tous cas confondus, calculée par les probabilités totales (démonstration 2) ; en Python, la variable `p_e`, second élément renvoyé par `bayes(base, sensibilite, fausse_alerte)`.

$$
P(H \mid E)
$$

**P(H | E)** : la probabilité a posteriori, la croyance après l'observation ; c'est la VPP (précision) de la leçon 51 quand E est une alerte ; en Python, `bayes(base, sensibilite, fausse_alerte)[0]`, qui vaut `None` si E est impossible.

$$
\text{cote}(p) = \frac{p}{1 - p}
$$

**cote** : une autre écriture d'une probabilité p < 1, dans [0 ; +∞[ ; 0,02 devient 0,02 / 0,98 ≈ 0,0204 ; en Python, `cote(p)` et son inverse `proba(c)`.

$$
LR = \frac{P(E \mid H)}{P(E \mid \neg H)} = \frac{Se}{\alpha}
$$

**LR** : le rapport de vraisemblance, la force de la preuve, sans unité ; LR > 1 rend H plus probable, LR = 1 ne change rien ; en Python, les nombres de la liste `rapports` passée à `bayes_cotes(base, rapports)`.

## Le mécanisme, avant les preuves

Trois nombres entrent : le taux de base π, la sensibilité Se et le taux de fausses alertes α. Le numérateur Se × π est la part de toute la population qui est à la fois H et signalée : un produit, parce que deux conditions doivent être vraies en même temps, être H puis sonner sachant H. Le dénominateur P(E) = Se π + α (1 − π) est la part de la population signalée, toutes causes confondues : une somme, parce qu'il y a deux façons disjointes de sonner, à raison ou à tort. La division se restreint au monde où l'alerte a sonné et demande quelle part de ce monde est H : c'est une renormalisation. Le terme des fausses alertes α (1 − π) est multiplié par la grande population des cas sains : quand π est petit, il domine le dénominateur même si α est petit, et la probabilité a posteriori reste basse. La formule n'a donc pas besoin d'une fonction compliquée : tout est produit, somme et division de proportions. La forme en cotes (démonstration 3) sépare les deux ingrédients : la cote de départ, qui ne dépend que de la population, et le rapport Se / α, qui ne dépend que du détecteur. Ce qui sort est une probabilité dans [0 ; 1], que l'agent compare à un seuil de décision.

Petit film chiffré sur 10 000 réponses d'un agent, avec π = 0,02, Se = 0,95 et α = 0,10. Les 10 000 se partagent en 200 réponses fausses et 9 800 justes. Le détecteur signale 0,95 × 200 = 190 fausses et 0,10 × 9 800 = 980 justes. Les alertes sont 190 + 980 = 1 170. La proportion de vraies alertes vaut 190 / 1 170 ≈ 0,16239. Pour un développeur Java, c'est exactement `count(H et E) / count(E)` sur un flux qu'on aurait d'abord filtré par `filter(alerte)` : Bayes est un comptage dans le sous-ensemble filtré.

## Démonstration 1 — Bayes découle de la définition de la probabilité conditionnelle

**Ce qu'on démontre.** Pour deux événements H et E avec P(E) > 0 et P(H) > 0 :

$$
P(H \mid E) = \frac{P(E \mid H)\, P(H)}{P(E)}
$$

**L'idée.** Les deux probabilités conditionnelles P(H | E) et P(E | H) partagent la même probabilité jointe P(H ∩ E) : l'une la divise par P(E), l'autre par P(H). On écrit cette jointe de deux façons et on égale.

**La preuve, pas à pas.**

**Étape 1.** Par définition de la probabilité conditionnelle, possible parce que P(E) > 0 :

$$
P(H \mid E) = \frac{P(H \cap E)}{P(E)}
$$

**Étape 2.** Par la même définition appliquée à E sachant H, possible parce que P(H) > 0, puis en multipliant les deux membres par P(H) :

$$
P(E \mid H) = \frac{P(H \cap E)}{P(H)} \quad\Longrightarrow\quad P(H \cap E) = P(E \mid H)\, P(H)
$$

**Étape 3.** On remplace P(H ∩ E) dans l'étape 1 par l'expression de l'étape 2 :

$$
P(H \mid E) = \frac{P(E \mid H)\, P(H)}{P(E)}
$$

∎

**Vérification chiffrée.** Sur les 10 000 réponses du film : P(H ∩ E) = 190 / 10 000 = 0,019 et P(E) = 1 170 / 10 000 = 0,117, donc P(H | E) = 0,019 / 0,117 ≈ 0,16239, le même nombre que 190 / 1 170. Contre-exemple quand l'hypothèse P(E) > 0 manque : un détecteur qui ne sonne jamais (Se = α = 0) donne P(E) = 0 ; P(H | E) n'est alors pas défini, et le programme renvoie `None` au lieu d'un nombre inventé.

**Ce que la preuve révèle du mécanisme.** Bayes n'est pas une loi physique supplémentaire : c'est une réécriture de la définition, qui permet de calculer P(H | E), difficile à mesurer, à partir de P(E | H), facile à mesurer sur un jeu étiqueté. Le numérateur est la part des vraies alertes, le dénominateur la part de toutes les alertes.

**Conséquence pour un agent.** Quand on dispose d'un échantillon étiqueté, on peut vérifier le calcul de Bayes par un simple comptage ; une métrique sans alerte renvoie `None`, jamais 0 ni 1, pour ne pas fausser les moyennes de suivi.

## Démonstration 2 — Le dénominateur par les probabilités totales

**Ce qu'on démontre.** Avec π = P(H), Se = P(E | H) et α = P(E | ¬H) :

$$
P(E) = P(E \mid H)\, P(H) + P(E \mid \neg H)\, P(\neg H) = Se\, \pi + \alpha\,(1 - \pi)
$$

**L'idée.** E se produit soit avec H, soit avec ¬H, jamais avec les deux. La probabilité de E est la somme des probabilités de ces deux morceaux disjoints.

**La preuve, pas à pas.**

**Étape 1.** On découpe E en deux morceaux, parce que chaque cas est soit H, soit ¬H :

$$
E = (E \cap H) \cup (E \cap \neg H)
$$

**Étape 2.** Les deux morceaux sont disjoints, parce que H et ¬H ne sont jamais vrais ensemble ; une probabilité s'additionne sur des événements disjoints :

$$
P(E) = P(E \cap H) + P(E \cap \neg H)
$$

**Étape 3.** On applique à chaque morceau l'étape 2 de la démonstration 1, et P(¬H) = 1 − π parce que les probabilités de H et ¬H somment à 1 :

$$
P(E) = Se\, \pi + \alpha\,(1 - \pi)
$$

∎

**Vérification chiffrée.** P(E) = 0,95 × 0,02 + 0,10 × 0,98 = 0,019 + 0,098 = 0,117. Pour l'absence d'alerte, le même raisonnement donne P(¬E) = 0,05 × 0,02 + 0,90 × 0,98 = 0,001 + 0,882 = 0,883, et 0,117 + 0,883 = 1. Bayes sur « pas d'alerte » donne P(H | ¬E) = 0,001 / 0,883 ≈ 0,00113 : la VPN vaut 1 − 0,00113 = 0,99887.

**Ce que la preuve révèle du mécanisme.** Le terme des fausses alertes, 0,098, vaut cinq fois celui des vraies alertes, 0,019, alors que α = 0,10 est bien plus petit que Se = 0,95 : il est multiplié par 0,98 au lieu de 0,02. C'est l'effet du taux de base de la leçon 51.

**Conséquence pour un agent.** Trois nombres suffisent pour décrire un détecteur dans une population : π, Se et α. Pour transposer un détecteur à une autre population, on garde Se et α, mesurés une fois, et on change π (cas 2).

## Démonstration 3 — La forme « cotes »

**Ce qu'on démontre.** Pour P(E) > 0 et α > 0, cote après = cote avant × rapport de vraisemblance :

$$
\frac{P(H \mid E)}{P(\neg H \mid E)} = \frac{P(H)}{P(\neg H)} \times \frac{P(E \mid H)}{P(E \mid \neg H)}
$$

**L'idée.** On écrit Bayes deux fois, pour H et pour ¬H. Les deux formules ont le même dénominateur P(E) : en les divisant l'une par l'autre, il disparaît, et il ne reste que des quantités faciles à mesurer.

**La preuve, pas à pas.**

**Étape 1.** Bayes pour H (démonstration 1) :

$$
P(H \mid E) = \frac{P(E \mid H)\, P(H)}{P(E)}
$$

**Étape 2.** Bayes pour ¬H, parce que la démonstration 1 vaut pour n'importe quelle hypothèse de probabilité non nulle :

$$
P(\neg H \mid E) = \frac{P(E \mid \neg H)\, P(\neg H)}{P(E)}
$$

**Étape 3.** On divise l'étape 1 par l'étape 2 ; P(E) se simplifie parce qu'il est non nul et figure aux deux dénominateurs ; on range les facteurs :

$$
\frac{P(H \mid E)}{P(\neg H \mid E)} = \frac{P(H)}{P(\neg H)} \times \frac{P(E \mid H)}{P(E \mid \neg H)}
$$

**Étape 4.** Comme P(¬H | E) = 1 − P(H | E), le membre de gauche est la cote de P(H | E) ; on revient à une probabilité par p = cote / (1 + cote). En prenant le logarithme, le produit devient une somme :

$$
\ln \text{cote}(H \mid E) = \ln \text{cote}(H) + \ln LR
$$

∎

**Vérification chiffrée.** Cote de départ : 0,02 / 0,98 ≈ 0,020408. Rapport de vraisemblance : 0,95 / 0,10 = 9,5. Cote après : 0,020408 × 9,5 ≈ 0,19388. Probabilité : 0,19388 / 1,19388 ≈ 0,16239, le même résultat que la démonstration 1, sans avoir calculé P(E).

**Ce que la preuve révèle du mécanisme.** Le rapport de vraisemblance mesure la force de la preuve, indépendamment du taux de base ; le taux de base n'entre que par la cote de départ. Un LR de 9,5 multiplie la cote par 9,5 dans toutes les populations, mais la probabilité finale dépend de la cote de départ. Un LR de 1 ne change rien (exercice 3).

**Conséquence pour un agent.** On stocke le LR d'un détecteur dans sa configuration, et le taux de base par population et par période ; l'agent multiplie. En logarithme, chaque preuve ajoute un score ln LR, ce qui rend les mises à jour lisibles dans un journal d'audit.

## Démonstration 4 — Deux preuves indépendantes se multiplient

**Ce qu'on démontre.** Si E₁ et E₂ sont indépendantes sachant H et indépendantes sachant ¬H, alors, avec LR₁ = P(E₁ | H) / P(E₁ | ¬H) et LR₂ de même :

$$
\text{cote}(H \mid E_1, E_2) = \text{cote}(H) \times LR_1 \times LR_2
$$

**L'idée.** On applique la démonstration 3 à la preuve jointe « E₁ et E₂ ». L'indépendance conditionnelle permet de couper la probabilité jointe en un produit, donc le rapport joint en deux rapports.

**La preuve, pas à pas.**

**Étape 1.** La démonstration 3 vaut pour n'importe quelle observation, en particulier pour l'observation jointe E₁ ∩ E₂ :

$$
\text{cote}(H \mid E_1, E_2) = \text{cote}(H) \times \frac{P(E_1, E_2 \mid H)}{P(E_1, E_2 \mid \neg H)}
$$

**Étape 2.** Par l'hypothèse d'indépendance conditionnelle, la probabilité jointe sachant H est le produit des deux probabilités sachant H, et de même sachant ¬H :

$$
P(E_1, E_2 \mid H) = P(E_1 \mid H)\, P(E_2 \mid H) \qquad P(E_1, E_2 \mid \neg H) = P(E_1 \mid \neg H)\, P(E_2 \mid \neg H)
$$

**Étape 3.** On remplace et on regroupe les facteurs deux à deux, parce qu'un quotient de produits est le produit des quotients :

$$
\text{cote}(H \mid E_1, E_2) = \text{cote}(H) \times LR_1 \times LR_2
$$

∎

**Vérification chiffrée.** Avec le détecteur (LR₁ = 9,5) et un vérificateur de citations (Se = 0,9, α = 0,05, LR₂ = 18) : 0,020408 × 9,5 × 18 ≈ 3,4898, soit P ≈ 3,4898 / 4,4898 ≈ 0,77727. La mise à jour en deux temps donne la même chose : on part de 0,16239 et on applique Bayes avec le second détecteur. Contre-exemple quand l'indépendance manque : un second détecteur qui est une copie du premier sonne exactement quand le premier sonne ; la preuve jointe vaut P(E₁, E₂ | H) / P(E₁, E₂ | ¬H) = 0,95 / 0,10 = 9,5, et la vraie probabilité reste 0,16239. Le produit naïf donne 0,020408 × 9,5 × 9,5 = 0,020408 × 90,25 ≈ 1,84184, soit P ≈ 0,64811 : quatre fois trop confiant.

**Ce que la preuve révèle du mécanisme.** En log-cotes, chaque preuve indépendante ajoute son ln LR. Quand les preuves sont corrélées, le rapport joint est plus petit que le produit des rapports, parce que la seconde preuve répète en partie la première.

**Conséquence pour un agent.** Deux détecteurs fondés sur le même modèle, ou sur les mêmes variables, ne sont pas indépendants. On mesure leur rapport joint sur un échantillon étiqueté, P(les deux sonnent | H) / P(les deux sonnent | ¬H), au lieu de multiplier leurs rapports (cas 3).

## Démonstration 5 — La probabilité a posteriori croît avec le taux de base

**Ce qu'on démontre.** Pour Se > 0 et α > 0, P(H | E) croît strictement avec π, et son élasticité (la variation relative de P(H | E) pour une variation relative de π) vaut :

$$
\frac{\pi}{P(H \mid E)} \times \frac{dP(H \mid E)}{d\pi} = \frac{\alpha}{P(E)} = \frac{1 - P(H \mid E)}{1 - \pi}
$$

**L'idée.** Plus il y a de cas H dans la population, plus une alerte a de chances d'en être un. Quand H est rare, presque toutes les alertes sont fausses, et la probabilité a posteriori est à peu près proportionnelle au taux de base : l'élasticité est proche de 1.

**La preuve, pas à pas.**

**Étape 1.** On divise numérateur et dénominateur de Bayes par Se π, ce qui est permis parce que Se π > 0 :

$$
P(H \mid E) = \frac{1}{1 + \dfrac{\alpha}{Se} \times \dfrac{1 - \pi}{\pi}}
$$

**Étape 2.** (1 − π) / π = 1/π − 1 décroît strictement quand π augmente ; le dénominateur décroît donc, et la fraction croît, parce que α / Se > 0.

**Étape 3.** Pour l'élasticité, on écrit ln P(H | E) = ln Se + ln π − ln P(E), on dérive par rapport à π, avec dP(E)/dπ = Se − α, puis on multiplie par π :

$$
\pi \times \frac{d \ln P(H \mid E)}{d\pi} = 1 - \frac{\pi\,(Se - \alpha)}{P(E)}
$$

**Étape 4.** On met au même dénominateur : P(E) − π (Se − α) = Se π + α − α π − Se π + α π = α. Et comme 1 − P(H | E) = α (1 − π) / P(E), on obtient aussi la seconde forme :

$$
1 - \frac{\pi\,(Se - \alpha)}{P(E)} = \frac{\alpha}{P(E)} = \frac{1 - P(H \mid E)}{1 - \pi}
$$

∎

**Vérification chiffrée.** α / P(E) = 0,10 / 0,117 ≈ 0,85470. Si π passe de 0,02 à 0,0202 (+1 %), P(H | E) passe de 0,16239 à 0,16378, soit +0,853 %, très proche de l'élasticité. Avec le même détecteur, P(H | E) vaut 0,088 à π = 1 %, 0,514 à π = 10 % et 0,803 à π = 30 %.

**Ce que la preuve révèle du mécanisme.** Quand l'événement est rare, P(H | E) est petit et l'élasticité est proche de 1 − π, donc de 1 : doubler le taux de base double presque la VPP. Quand π s'approche de 1, l'élasticité tend vers 0 : la VPP sature.

**Conséquence pour un agent.** Une erreur sur le taux de base se reporte presque entièrement sur la VPP d'un événement rare. Le taux de base se mesure par population et par période, dans les données de l'entreprise : on ne le recopie pas d'une plaquette ou d'un autre marché.

## Exemple simple, à la main

2 % des réponses d'un agent sont fausses. Un détecteur d'hallucination signale 95 % des réponses fausses, et 10 % des réponses justes.

$$
P(E) = 0{,}95 \times 0{,}02 + 0{,}10 \times 0{,}98 = 0{,}019 + 0{,}098 = 0{,}117
$$

$$
P(\text{fausse} \mid \text{alerte}) = \frac{0{,}019}{0{,}117} \approx 0{,}16239
$$

Le même calcul en comptes, sur 10 000 réponses :

| | alerte | pas d'alerte | total |
| --- | --- | --- | --- |
| réponse fausse | 0,95 × 200 = 190 | 200 − 190 = 10 | 0,02 × 10 000 = 200 |
| réponse juste | 0,10 × 9 800 = 980 | 9 800 − 980 = 8 820 | 10 000 − 200 = 9 800 |
| total | 190 + 980 = 1 170 | 10 + 8 820 = 8 830 | 10 000 |

Seulement 190 / 1 170 ≈ 16 % des alertes concernent une réponse réellement fausse ; les 1 − 0,16239 = 0,83761, soit 84 %, sont de fausses alarmes : le taux de base de 2 % est si bas que les fausses alertes dominent.

## Cas d'usage complexes, démontrés

### Cas 1 — Entité de services publics en ligne : dimensionner l'équipe qui relit les réponses signalées

**Contexte.** Une entité de services publics en ligne, accessible par UAE Pass, fait répondre un assistant bilingue arabe et anglais aux questions des résidents (renouvellements, rendez-vous, pièces à fournir). Il produit 10 000 réponses par jour, dont 2 % sont fausses (chiffres illustratifs). Un détecteur d'hallucination et un vérificateur de citations, supposés indépendants, signalent les réponses douteuses, qu'une équipe humaine relit avant l'envoi. Question : relire toutes les alertes du détecteur (politique A), ou seulement les réponses signalées par les deux (politique B) ?

**Données.**

- n = 10 000 réponses par jour ; π = 0,02.
- Détecteur : Se = 0,95, α = 0,10, donc LR₁ = 9,5. Vérificateur : Se = 0,9, α = 0,05, donc LR₂ = 18.
- Un relecteur traite 120 réponses par jour et coûte 600 AED par jour ; une réponse fausse envoyée sans relecture coûte 150 AED (rappel du résident, correction) ; tous ces montants sont illustratifs.

**Calcul pas à pas.**

**Étape 1.** Politique A : P(E₁) = 0,117 (exemple simple), donc 1 170 relectures par jour, dont 190 vraies erreurs ; 980 / 1 170 ≈ 84 % du temps passe sur de fausses alertes. Erreurs envoyées sans relecture : 200 − 190 = 10.

**Étape 2.** Politique B : probabilité d'une double alerte, par les probabilités totales et l'indépendance conditionnelle :

$$
P(E_1, E_2) = 0{,}02 \times 0{,}95 \times 0{,}9 + 0{,}98 \times 0{,}10 \times 0{,}05 = 0{,}0171 + 0{,}0049 = 0{,}022
$$

Soit 220 relectures par jour, dont 10 000 × 0,0171 = 171 vraies erreurs : 171 / 220 ≈ 0,77727, le même nombre que la forme en cotes 3,4898 / 4,4898. Erreurs envoyées sans relecture : 200 − 171 = 29.

**Étape 3.** Relecteurs nécessaires, arrondis à l'entier supérieur : A, 1 170 / 120 = 9,75, donc 10 ; B, 220 / 120 ≈ 1,83, donc 2.

**Étape 4.** Coût total par jour :

$$
\text{A} : 10 \times 600 + 10 \times 150 = 6\,000 + 1\,500 = 7\,500 \qquad \text{B} : 2 \times 600 + 29 \times 150 = 1\,200 + 4\,350 = 5\,550
$$

**Décision de l'agent.** Politique B, avec deux relecteurs : la file des doubles alertes contient 78 % de vraies erreurs, et le coût total baisse de 7 500 à 5 550 AED par jour. Les réponses signalées par un seul détecteur partent avec une mention invitant à vérifier sur le portail officiel.

**Contre-calcul.** Une lecture naïve de « sensibilité 95 % » comme « une alerte = 95 % de chances d'erreur » ferait bloquer automatiquement les 1 170 réponses signalées : 0,10 × 9 800 = 980 réponses justes retenues chaque jour, à 25 AED de rappel chacune (illustratif), soit 24 500 AED par jour et autant de résidents mal servis.

**Sensibilité.** A et B s'équilibrent quand le coût d'une erreur envoyée vaut (6 000 − 1 200) / (29 − 10) = 4 800 / 19 ≈ 252,63 AED : au-delà, par exemple pour des réponses sur des délais légaux, la politique A redevient meilleure. Si une mise à jour du modèle fait passer le taux d'erreur de 2 % à 5 %, une alerte simple vaut 0,0475 / (0,0475 + 0,095) = 0,0475 / 0,1425 ≈ 0,33333 et une double alerte 0,05 / 0,95 × 171 = 9 en cote, soit P = 0,9.

**En production.** On suit la part des doubles alertes confirmées par les relecteurs, attendue à 0,777, avec une alerte sous 0,70 : elle signale soit un changement du taux d'erreur, soit des détecteurs devenus corrélés. On mesure aussi, sur les réponses fausses relues, la part signalée par les deux détecteurs, attendue à 0,95 × 0,9 = 0,855 si l'indépendance tient. Les données des résidents relèvent de la PDPL (décret-loi fédéral 45/2021) hors DIFC et ADGM.

### Cas 2 — Plateforme d'actifs virtuels agréée VARA : transposer un détecteur de blanchiment à un nouveau segment

**Contexte.** Une plateforme d'actifs virtuels agréée par la VARA fait passer chaque demande de retrait par un modèle de détection de blanchiment, mesuré sur la clientèle générale. Elle ouvre un guichet de gré à gré (OTC) pour les gros montants, où la part de retraits suspects est estimée bien plus haute. Sur alerte, l'agent peut retenir le retrait (gel temporaire en attente d'analyse) ou le laisser partir et l'analyser après coup. Volumes : 50 000 retraits par mois en clientèle générale et 2 000 en OTC (chiffres illustratifs).

**Données.**

- Détecteur : Se = 0,85, Sp = 0,97, donc α = 0,03.
- Prévalence : 0,5 % en clientèle générale, 4 % en OTC (illustratif).
- Retenir un client légitime coûte 400 AED (support, réclamation, client perdu) ; laisser partir un retrait suspect coûte 1 500 AED d'exposition (illustratif).

**Calcul pas à pas.**

**Étape 1.** Seuil de rétention : retenir vaut mieux dès que le coût attendu de laisser partir dépasse celui de retenir :

$$
P \times 1\,500 > (1 - P) \times 400 \iff P > \frac{400}{1\,900} \approx 0{,}21053
$$

**Étape 2.** Clientèle générale : P(alerte) = 0,85 × 0,005 + 0,03 × 0,995 = 0,00425 + 0,02985 = 0,0341, donc VPP = 0,00425 / 0,0341 ≈ 0,12463, sous le seuil. La VPN vaut 0,96515 / (0,96515 + 0,00075) = 0,96515 / 0,9659 ≈ 0,99922.

**Étape 3.** OTC : P(alerte) = 0,85 × 0,04 + 0,03 × 0,96 = 0,034 + 0,0288 = 0,0628, donc :

$$
\text{VPP}_{\text{OTC}} = \frac{0{,}034}{0{,}0628} \approx 0{,}54140
$$

**Étape 4.** Volumes : 50 000 × 0,0341 = 1 705 alertes par mois en clientèle générale, dont 50 000 × 0,005 × 0,85 = 212,5 vraies en moyenne ; 2 000 × 0,0628 = 125,6 alertes en OTC, dont 2 000 × 0,04 × 0,85 = 68 vraies.

**Décision de l'agent.** Deux politiques pour le même détecteur : en clientèle générale (VPP 0,125 < 0,211), le retrait part et l'alerte est analysée dans la journée ; en OTC (VPP 0,541 > 0,211), le retrait est retenu jusqu'à l'analyse.

**Contre-calcul.** Recopier en OTC la VPP de la clientèle générale ferait laisser partir les retraits OTC signalés. Par alerte OTC, le coût attendu serait 0,5414 × 1 500 ≈ 812,1 AED au lieu de 0,4586 × 400 ≈ 183,4 AED en retenant, soit 628,7 AED de trop, et environ 78 960 AED par mois sur 125,6 alertes (illustratif).

**Sensibilité.** Prévalence de bascule : la cote du seuil vaut 0,21053 / 0,78947 ≈ 0,26667 ; par la forme en cotes, la cote de départ nécessaire vaut 0,26667 × α / Se = 0,26667 × 0,035294 ≈ 0,0094118, soit π ≈ 0,00932. Dès 0,93 % de retraits suspects, la rétention s'impose : la clientèle générale (0,5 %) est en dessous, l'OTC (4 %) très au-dessus.

**En production.** On suit la VPP observée par segment (alertes confirmées / alertes) et la prévalence estimée de chaque segment chaque mois ; une prévalence générale qui s'approche de 0,93 % fait changer la politique. La VARA attend des contrôles de lutte anti-blanchiment documentés ; les obligations précises de gel et de déclaration sont à confirmer avec le texte en vigueur.

### Cas 3 — Assureur auto et santé : trois indices de fraude sur un sinistre auto, dont deux corrélés

**Contexte.** Un assureur auto et santé d'Abu Dhabi reçoit 6 000 sinistres auto par mois ; la fraude en touche environ 3 % (ordre de grandeur repris de la leçon 51, illustratif). Trois indices sont relevés par l'agent : (1) déclaration plus de 7 jours après les faits, (2) garage hors réseau, (3) photos dont les métadonnées ne correspondent pas à la date déclarée. Règle : enquête si P > 0,5 ; demande de pièces si 0,15 < P ≤ 0,5 ; paiement sinon.

**Données.**

| indice | P(indice / fraude) | P(indice / honnête) | LR |
| --- | --- | --- | --- |
| (1) déclaration tardive | 0,40 | 0,10 | 4 |
| (2) garage hors réseau | 0,50 | 0,20 | 2,5 |
| (3) métadonnées incohérentes | 0,30 | 0,02 | 15 |
| (1) et (2) ensemble, mesuré | 0,25 | 0,05 | 5 |

800 dossiers par mois présentent les indices (1) et (2) sans le (3) ; une demande de pièces coûte 120 AED de traitement (illustratif). L'indice (3) est supposé indépendant des deux autres.

**Calcul pas à pas.**

**Étape 1.** Cote de départ : 0,03 / 0,97 ≈ 0,030928.

**Étape 2.** Calcul naïf, qui suppose les trois indices indépendants : pour (1) et (2), 0,030928 × 4 × 2,5 = 0,30928, soit P = 0,30928 / 1,30928 ≈ 0,23622, d'où une demande de pièces ; pour les trois, 0,030928 × 150 ≈ 4,6392, soit P ≈ 0,82267, d'où une enquête.

**Étape 3.** Calcul corrigé avec le rapport joint mesuré, 0,25 / 0,05 = 5, au lieu de 4 × 2,5 = 10 :

$$
\text{cote}(1, 2) = 0{,}030928 \times 5 \approx 0{,}15464 \quad\Longrightarrow\quad P \approx \frac{0{,}15464}{1{,}15464} \approx 0{,}13393
$$

**Étape 4.** Pour les trois indices : 0,15464 × 15 ≈ 2,3196, soit P ≈ 0,69876.

**Décision de l'agent.** Un dossier avec (1) et (2) seulement est payé (P ≈ 0,134 < 0,15) ; un dossier avec les trois indices part en enquête (P ≈ 0,699 > 0,5). Le score ne décide jamais seul d'un refus : il oriente le dossier.

**Contre-calcul.** L'hypothèse d'indépendance fait passer les 800 dossiers mensuels « (1) et (2) » au-dessus du seuil de demande de pièces : 800 × 120 = 96 000 AED par mois de traitements et de délais que le risque réel ne justifie pas, pour des assurés en majorité honnêtes.

**Sensibilité.** Rapport joint de bascule : la cote du seuil vaut 0,15 / 0,85 ≈ 0,17647, et il faut 0,17647 / 0,030928 ≈ 5,7059. Le rapport mesuré, 5, n'en est qu'à 12 % : la décision est fragile, et une nouvelle mesure du rapport joint chaque trimestre est indispensable.

**En production.** On suit, parmi les dossiers « (1) et (2) » payés, la part reconnue frauduleuse plus tard, prévue à 13,4 %, avec une alerte au-dessus de 15 %. L'assurance est supervisée par la CBUAE ; les règles de motivation d'une enquête ou d'un refus sont à confirmer avec le texte en vigueur.

### Cas 4 — Groupe de construction à Dubaï : facture de sous-traitant au-dessus du devis, avec une TVA mal calculée

**Contexte.** Un groupe de construction sur de grands chantiers à Dubaï reçoit 4 000 factures de sous-traitants par mois, contrôlées par un agent avant paiement. 1,5 % des factures sont irrégulières (doublon, surfacturation) chez les sous-traitants sans historique, et 6 % chez ceux qui ont déjà eu un incident (chiffres illustratifs). Règle : suspension du paiement et audit si P > 0,5 ; revue par le contrôleur de gestion si 0,1 < P ≤ 0,5 ; paiement sinon.

**Données.**

- E₁ : montant hors taxes supérieur de plus de 15 % au devis ; P(E₁ | irrégulière) = 0,8 et P(E₁ | régulière) = 0,05, donc LR₁ = 16.
- E₂ : ligne de TVA différente de 5 % du hors-taxes ; P(E₂ | irrégulière) = 0,20 et P(E₂ | régulière) = 0,01 (erreurs de saisie honnêtes), donc LR₂ = 20 ; E₂ est supposé indépendant de E₁ sachant l'état de la facture.
- Facture examinée : 480 000 AED hors taxes pour un devis de 400 000 AED, TVA facturée 25 000 AED.
- Une facture honnête suspendue à tort coûte 1 500 AED (pénalités de retard, tension sur le chantier, illustratif).

**Calcul pas à pas.**

**Étape 1.** Indices de la facture : 480 000 / 400 000 − 1 = 20 % > 15 %, donc E₁ ; TVA due 0,05 × 480 000 = 24 000 AED ≠ 25 000 AED facturés, donc E₂.

**Étape 2.** Cotes de départ : 0,015 / 0,985 ≈ 0,015228 sans historique ; 0,06 / 0,94 ≈ 0,06383 avec historique.

**Étape 3.** Facture A, sans historique, E₁ seul : 0,015228 × 16 ≈ 0,24365, soit P ≈ 0,19592, donc revue. Facture B, avec historique, E₁ seul : 0,06383 × 16 ≈ 1,0213, soit P ≈ 0,50526, donc suspension.

**Étape 4.** Facture C, sans historique, E₁ et E₂ (la facture examinée) :

$$
\text{cote} = 0{,}015228 \times 16 \times 20 \approx 4{,}8731 \quad\Longrightarrow\quad P \approx \frac{4{,}8731}{5{,}8731} \approx 0{,}82973
$$

**Décision de l'agent.** La facture examinée est suspendue et auditée ; le même dépassement de devis sans erreur de TVA mènerait à une revue chez un sous-traitant sans historique et à une suspension chez un sous-traitant avec incident. Le contrôle de TVA à 5 % est déterministe : Bayes ne sert qu'à combiner son résultat avec les autres indices.

**Contre-calcul.** Lire P(E₁ | irrégulière) = 0,8 comme « 80 % de chances que la facture soit irrégulière » ferait suspendre toute facture E₁. Sur 4 000 factures de sous-traitants sans historique, P(E₁) = 0,8 × 0,015 + 0,05 × 0,985 = 0,012 + 0,04925 = 0,06125, soit 245 suspensions par mois, dont 4 000 × 0,012 = 48 irrégulières et 197 honnêtes : 197 × 1 500 = 295 500 AED par mois de coûts inutiles.

**Sensibilité.** Taux de base de bascule pour E₁ seul : il faut une cote de départ de 1 / 16 = 0,0625, soit π = 0,0625 / 1,0625 ≈ 0,058824, environ 5,88 %. Le sous-traitant avec historique (6 %) est juste au-dessus : si le LR de E₁ baisse de 10 % (16 → 14,4), sa cote devient 0,06383 × 14,4 ≈ 0,91915, soit P ≈ 0,47894, et la facture B passe en revue au lieu d'être suspendue.

**En production.** On suit la part des suspensions confirmées irrégulières (la VPP observée), avec une alerte sous 0,5, et l'on remesure LR₁ chaque trimestre sur les factures auditées. Les mentions obligatoires d'une facture avec TVA sont à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** 1 % des transactions sont frauduleuses ; un détecteur en signale 90 % et signale 5 % des transactions saines. Probabilité qu'une alerte soit une fraude ?

**Exercice 2.** Même détecteur, taux de base 10 %. Même question avec la forme « cotes ».

**Exercice 3.** Démontrer que si P(E | H) = P(E | ¬H), observer E ne change rien.

**Exercice 4.** Calculer le rapport de vraisemblance d'un détecteur de sensibilité 0,8 et de fausses alertes 0,2.

**Exercice 5.** Pourquoi multiplier les rapports de deux détecteurs fondés sur le même LLM est-il dangereux ?

**Exercice 6 (cas modifié).** Dans le cas 2, la prévalence estimée en OTC tombe à 1 %. Recalculer la VPP et dire si l'agent doit encore retenir les retraits signalés.

**Exercice 7 (trouver l'erreur).** Un collègue écrit : « P(E) = 0,95 × 0,02 + 0,10 × 0,02 = 0,021, donc P(fausse | alerte) = 0,019 / 0,021 ≈ 0,905 : neuf alertes sur dix sont de vraies erreurs. » Trouver l'erreur et corriger.

**Exercice 8 (redémontrer de mémoire).** Redémontrer la forme en cotes (démonstration 3), puis l'appliquer au cas 3 avec les trois indices supposés indépendants.

## Corrigé

**Exercice 1.** Numérateur : 0,9 × 0,01 = 0,009. Fausses alertes : 0,05 × 0,99 = 0,0495. P(E) = 0,009 + 0,0495 = 0,0585. P(fraude | alerte) = 0,009 / 0,0585 ≈ 0,15385.

**Exercice 2.** Cote de départ : 0,1 / 0,9 = 1/9. LR = 0,9 / 0,05 = 18. Cote finale : 18 / 9 = 2. P = 2 / (1 + 2) = 2/3 ≈ 0,667, ce que confirme le calcul direct 0,09 / (0,09 + 0,045).

**Exercice 3.** Le rapport de vraisemblance vaut P(E | H) / P(E | ¬H) = 1 : par la démonstration 3, la cote après est égale à la cote avant, donc la probabilité aussi. Exemple : π = 0,3, Se = α = 0,4 donne P(H | E) = 0,12 / (0,12 + 0,28) = 0,3.

**Exercice 4.** LR = 0,8 / 0,2 = 4 : la cote est multipliée par 4.

**Exercice 5.** Leurs erreurs sont corrélées : quand l'un se trompe, l'autre se trompe souvent sur le même cas. L'hypothèse d'indépendance de la démonstration 4 est fausse, le rapport joint réel est plus petit que le produit, et la confiance calculée est trop haute (le contre-exemple de la copie donne 0,648 au lieu de 0,162).

**Exercice 6.** P(alerte) = 0,85 × 0,01 + 0,03 × 0,99 = 0,0085 + 0,0297 = 0,0382. VPP = 0,0085 / 0,0382 ≈ 0,22251 > 0,21053 : l'agent retient encore, de justesse, ce qui est cohérent avec la prévalence de bascule de 0,93 %.

**Exercice 7.** Le terme des fausses alertes multiplie α par P(H) = 0,02 au lieu de P(¬H) = 0,98 : les fausses alertes viennent des réponses justes. Correct : P(E) = 0,019 + 0,10 × 0,98 = 0,117 et P = 0,019 / 0,117 ≈ 0,162. L'erreur transforme 16 % en 90 % et ferait bloquer des réponses justes.

**Exercice 8.** Bayes pour H et pour ¬H, même dénominateur P(E), division : cote(H | E) = cote(H) × LR. Application : 0,030928 × 4 × 2,5 × 15 = 0,030928 × 150 ≈ 4,6392, soit P ≈ 4,6392 / 5,6392 ≈ 0,82267.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`verifier(probas)`** — Cette fonction est le portier qui contrôle les billets avant de laisser entrer quiconque dans le calcul : elle reçoit un nombre quelconque de probabilités, rassemblées par l'étoile de sa signature, les passe en revue une à une et lève une `ValueError` qui cite la valeur fautive dès que l'une d'elles sort de l'intervalle de 0 à 1. Elle ne renvoie rien quand tout est en ordre, et `bayes` comme `cote` l'appellent d'abord, si bien qu'une base de 1,2 est refusée avant même le premier produit, comme `main` le vérifie à la fin.

**`bayes(base, sensibilite, fausse_alerte)`** — On la voit en greffier qui compte, parmi toutes les alertes, celles qui sont vraies : elle reçoit la probabilité a priori π de l'hypothèse, la sensibilité Se du détecteur et son taux de fausse alerte α, les fait contrôler par `verifier`, puis calcule P(E) = Se × π + α × (1 − π) par les probabilités totales et P(H | E) = Se × π / P(E). Elle renvoie ce couple, avec `None` à la place de P(H | E) si l'alerte est impossible ; pour π = 0,02, Se = 0,95 et α = 0,10, elle donne 0,16239 et 0,117, soit seulement 190 vraies alertes sur 1 170.

**`bayes_negatif(base, sensibilite, fausse_alerte)`** — Cette fonction regarde l'autre face de la pièce, celle où le détecteur reste muet : elle reçoit les mêmes trois probabilités et se contente d'appeler `bayes` avec 1 − Se et 1 − α, puisque l'absence d'alerte survient avec la probabilité 1 − Se si l'hypothèse est vraie et 1 − α sinon. Elle renvoie P(H | non E) et P(non E), soit 0,00113 et 0,883 dans l'exemple de la fiche, et le cas 2 s'en sert pour calculer la valeur prédictive négative de 0,99922.

**`cote(p)`** — Celle-ci est le bookmaker qui traduit une probabilité en cote de pari : elle reçoit une probabilité, la fait contrôler par `verifier`, puis renvoie p/(1 − p), ou `None` si p vaut 1, la cote étant alors infinie. Une probabilité de 0,02 devient une cote de 0,020408 et une probabilité de 0,15 une cote de 0,17647 ; cette écriture permet à `bayes_cotes` de mettre à jour une croyance par simple multiplication.

**`proba(c)`** — Cette fonction fait le chemin inverse du bookmaker et ramène une cote à une probabilité : elle reçoit une cote, refuse par une `ValueError` une cote négative, puis renvoie c/(1 + c). La cote 0,19388 obtenue après une alerte redonne ainsi la probabilité 0,16239, et la cote 3,4898 de deux détecteurs donne 0,77727 ; elle termine chaque mise à jour faite par `bayes_cotes`.

**`bayes_cotes(base, rapports)`** — On l'imagine en enquêteur qui empile les indices un par un, chacun renforçant ou affaiblissant son soupçon d'un facteur fixe : elle reçoit la probabilité a priori et une suite de rapports de vraisemblance, convertit la base en cote, la multiplie par chaque rapport, ce qui suppose des preuves indépendantes, puis reconvertit le résultat. Elle renvoie la probabilité finale et la cote finale ; avec 0,02 et les rapports 9,5 et 18, elle donne 0,77727, et avec 0,03 et les rapports 4, 2,5 et 15 du cas 3, elle donne 0,82267.

**`proche(x, attendu, decimales)`** — Ce petit contrôleur compare deux nombres comme on rapproche deux lignes d'un registre arrondi : il reçoit la valeur calculée, la valeur attendue et un nombre de décimales, arrondit les deux à ce nombre de chiffres et renvoie vrai s'ils coïncident. Un nombre de décimales négatif arrondit aux dizaines, ce qui sert pour la perte de 78 960 AED du cas 2 ; presque tous les `assert` de `main` passent par lui pour confronter les résultats aux valeurs écrites dans la fiche.

**`demonstrations()`** — Cette fonction rejoue les cinq démonstrations sur l'exemple des 10 000 réponses : elle ne reçoit rien et retrouve d'abord la probabilité 0,16239 par les comptes, 190 vraies alertes sur 1 170, en montrant qu'un détecteur muet rend la question impossible. Elle vérifie ensuite que P(E) et P(non E) somment à 1, que la cote 0,020408 multipliée par 9,5 redonne 0,16239, que deux détecteurs indépendants donnent 0,77727, en une fois comme en deux temps, alors qu'une simple copie du même détecteur, comptée deux fois, ferait croire à 0,64811, et que l'élasticité vaut 0,85470 ; elle imprime ces nombres et les renvoie dans un dictionnaire.

**`exemple_simple()`** — Celle-ci raconte la scène de base, un agent qui se trompe dans 2 % des cas et un détecteur de sensibilité 0,95 et de fausse alerte 0,10 : elle ne reçoit rien, appelle `bayes`, puis imprime les deux morceaux du calcul, 0,95 × 0,02 = 0,019 et 0,10 × 0,98 = 0,098, la probabilité d'alerte 0,117 et la probabilité qu'une réponse signalée soit vraiment fausse, 0,16239. Elle renvoie ce couple, que `main` vérifie, montrant qu'avec une erreur rare, la plupart des alertes sont fausses.

**`cas_1_service_public_revue()`** — Cette fonction met en scène l'assistant d'un service public en ligne qui produit 10 000 réponses par jour, dont 2 % fausses, et une équipe humaine qui relit les réponses douteuses : elle ne reçoit rien et compare la politique A, relire les 1 170 alertes du seul détecteur, à la politique B, relire seulement les 220 réponses signalées aussi par le vérificateur de citations, dont 171 vraies, soit une probabilité de 0,77727. Avec des relecteurs à 120 réponses et 600 AED par jour et 150 AED par erreur envoyée, A demande 10 agents et laisse 10 oublis, B 2 agents et 29 oublis, pour 7 500 contre 5 550 AED par jour ; elle calcule la bascule de 252,63 AED par oubli, l'effet d'un taux d'erreur de 5 % et le coût de 24 500 AED par jour d'un blocage naïf, puis renvoie ces résultats.

**`cas_2_crypto_transposition()`** — On y suit une plateforme d'actifs virtuels qui applique à son nouveau guichet de gré à gré un détecteur de blanchiment mesuré sur la clientèle générale, de sensibilité 0,85 et de spécificité 0,97 : la fonction ne reçoit rien, calcule une valeur prédictive positive de 0,12463 sur la clientèle générale, où 0,5 % des retraits sont suspects, et de 0,54140 au guichet, où ils sont 4 %. Le seuil de retenue, 400/(400 + 1 500) = 0,21053, tombe entre les deux : transposer la règle de la clientèle générale coûterait 78 960 AED par mois sur 125,6 alertes, puisqu'une alerte laissée partir coûte 812,1 AED contre 183,4 si on la retient ; elle calcule la base de bascule 0,00932 et renvoie le tout.

**`cas_3_assureur_indices()`** — Cette fonction raconte un assureur auto dont 3 % des sinistres sont frauduleux et dont l'agent relève trois indices, une déclaration tardive, un garage hors réseau et des photos aux métadonnées incohérentes, de rapports de vraisemblance 4, 2,5 et 15 : elle ne reçoit rien et calcule une probabilité de fraude de 0,82267 avec les trois indices et de 0,23622 avec les deux premiers, si on les croit indépendants. Avec le rapport joint réellement mesuré pour les deux premiers, 5, la probabilité tombe à 0,13393, sous le seuil de 0,15 de la demande de pièces, et à 0,69876 avec les trois ; elle calcule la bascule 5,7059 et le surcoût naïf de 96 000 AED par mois, puis renvoie ces nombres.

**`cas_4_btp_factures()`** — Ici, un groupe de construction contrôle 4 000 factures de sous-traitants par mois, dont 1,5 % sont irrégulières chez les nouveaux et 6 % chez ceux qui ont déjà eu un incident : la fonction ne reçoit rien, note une facture de 480 000 AED hors taxe pour un devis de 400 000, soit 20 % d'écart, et une TVA facturée de 25 000 AED au lieu des 24 000 dus, puis calcule les rapports 16 et 20 de ces deux indices. Elle trouve 0,19592 pour un nouveau sous-traitant avec le seul écart, 0,50526 pour un sous-traitant déjà en incident, 0,82973 avec les deux indices, la base de bascule 0,058824 et la valeur 0,47894 si le rapport baisse de 10 %, et chiffre la lecture naïve à 245 suspensions par mois, dont 197 honnêtes, soit 295 500 AED ; elle renvoie ces résultats.

**`corrige()`** — Celle-ci est le correcteur qui refait au propre les exercices chiffrés : elle ne reçoit rien et calcule la probabilité 0,15385 de l'exercice 1, la valeur 0,667 de l'exercice 2 par les cotes, le 0,3 inchangé d'un indice de rapport 1, le rapport 4 de l'exercice 4, la valeur prédictive 0,22251 de l'exercice 6, la valeur fautive de 0,90476 de l'exercice 7, qui multiplie α par la mauvaise probabilité, et le 0,82267 de l'exercice 8. Elle imprime ces résultats et les renvoie pour que `main` les compare à la fiche.

**`main()`** — C'est le chef d'orchestre de la fiche : il appelle `demonstrations` et vérifie chacun de ses nombres, puis parcourt 99 bases de 0,01 à 0,99 pour contrôler que la probabilité après alerte croît avec la base et que l'élasticité suit sa formule, et retrouve 0,088, 0,514 et 0,803 pour trois bases. Il enchaîne avec l'exemple simple, les quatre cas et le corrigé, puis s'assure qu'une base de 1,2, une cote négative ou une probabilité négative lèvent une `ValueError` et que la cote de 1 vaut `None` ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tout concorde.

```python
"""Démonstration 07 — Bayes : définition, probabilités totales, cotes, preuves indépendantes, sensibilité, quatre cas."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def verifier(*probas):
    for x in probas:
        if not 0 <= x <= 1:
            raise ValueError("probabilité hors de [0, 1] : " + str(x))


def bayes(base, sensibilite, fausse_alerte):
    """P(H | E) et P(E) ; P(H | E) vaut None si E est impossible (P(E) = 0)."""
    verifier(base, sensibilite, fausse_alerte)
    p_e = sensibilite * base + fausse_alerte * (1 - base)
    return (sensibilite * base / p_e if p_e > 0 else None), p_e


def bayes_negatif(base, sensibilite, fausse_alerte):
    """P(H | non E) et P(non E) : le même calcul avec 1 - Se et 1 - alpha."""
    return bayes(base, 1 - sensibilite, 1 - fausse_alerte)


def cote(p):
    verifier(p)
    return p / (1 - p) if p < 1 else None


def proba(c):
    if c < 0:
        raise ValueError("une cote est positive")
    return c / (1 + c)


def bayes_cotes(base, rapports):
    """Mise à jour par produit des rapports de vraisemblance (preuves indépendantes)."""
    c = cote(base)
    for lr in rapports:
        c *= lr
    return proba(c), c


def proche(x, attendu, decimales):
    return round(x, decimales) == round(attendu, decimales)


def demonstrations():
    print("Démonstrations")
    vraies, fausses_alertes, alertes = 190, 980, 1170
    d1 = vraies / alertes
    print(f"  D1 comptes : 190 / 1170 = {d1:.5f} ; détecteur muet : {bayes(0.02, 0.0, 0.0)[0]}")
    post, p_e = bayes(0.02, 0.95, 0.10)
    neg, p_non_e = bayes_negatif(0.02, 0.95, 0.10)
    print(f"  D2 P(E) = {p_e:.3f} ; P(non E) = {p_non_e:.3f} ; somme {p_e + p_non_e:.3f}")
    c0 = cote(0.02)
    print(f"  D3 cote {c0:.6f} x 9.5 = {c0 * 9.5:.5f} -> P = {proba(c0 * 9.5):.5f}")
    p2, c2 = bayes_cotes(0.02, (0.95 / 0.10, 0.9 / 0.05))
    sequentiel = bayes(post, 0.9, 0.05)[0]
    copie_naif = bayes_cotes(0.02, (9.5, 9.5))
    print(f"  D4 deux détecteurs : cote {c2:.4f} -> P = {p2:.5f} (en deux temps {sequentiel:.5f}) ;"
          f" copie : naïf {copie_naif[0]:.5f} contre vrai {post:.5f}")
    elasticite = 0.10 / p_e
    hausse = bayes(0.0202, 0.95, 0.10)[0] / post - 1
    print(f"  D5 élasticité alpha / P(E) = {elasticite:.5f} ; +1 % sur la base -> {hausse:+.3%} sur P(H|E)")
    return {"d1": d1, "post": post, "p_e": p_e, "neg": neg, "p_non_e": p_non_e, "c0": c0, "p2": p2, "c2": c2,
            "seq": sequentiel, "copie": copie_naif, "elasticite": elasticite, "hausse": hausse,
            "comptes": (vraies, fausses_alertes, alertes)}


def exemple_simple():
    post, p_e = bayes(0.02, 0.95, 0.10)
    print(f"Exemple simple : 0.95 x 0.02 = {0.95 * 0.02:.3f} ; 0.10 x 0.98 = {0.10 * 0.98:.3f} ; P(E) = {p_e:.3f} ;"
          f" P(fausse | alerte) = {post:.5f}")
    return post, p_e


def cas_1_service_public_revue():
    n, base = 10_000, 0.02
    post1, p_e1 = bayes(base, 0.95, 0.10)
    p_double = base * 0.95 * 0.9 + (1 - base) * 0.10 * 0.05
    vraies_double = n * base * 0.95 * 0.9
    p_d = vraies_double / (n * p_double)
    capacite, salaire, cout_oubli = 120, 600, 150
    revues = {"A": n * p_e1, "B": n * p_double}
    oublis = {"A": n * base - n * base * 0.95, "B": n * base - vraies_double}
    agents = {k: math.ceil(v / capacite) for k, v in revues.items()}
    cout = {k: agents[k] * salaire + oublis[k] * cout_oubli for k in revues}
    bascule = (agents["A"] - agents["B"]) * salaire / (oublis["B"] - oublis["A"])
    p5_un = bayes(0.05, 0.95, 0.10)[0]
    p5_deux = bayes_cotes(0.05, (9.5, 18))[0]
    print(f"Cas 1 : alertes {revues['A']:.0f}/jour dont {n * base * 0.95:.0f} vraies ({980 / 1170:.0%} fausses) ;"
          f" doubles {revues['B']:.0f} dont {vraies_double:.0f} vraies, P = {p_d:.5f}")
    print(f"  agents A {agents['A']} / B {agents['B']} ; oublis A {oublis['A']:.0f} / B {oublis['B']:.0f} ;"
          f" coût A {cout['A']:.0f} / B {cout['B']:.0f} AED/jour ; bascule {bascule:.2f} AED par oubli")
    bloquees = n * (1 - base) * 0.10
    print(f"  taux d'erreur 5 % : un détecteur {p5_un:.5f}, deux détecteurs {p5_deux:.5f} ;"
          f" blocage naïf : {bloquees:.0f} réponses justes, {bloquees * 25:.0f} AED/jour")
    return {"revues": revues, "oublis": oublis, "agents": agents, "cout": cout, "bascule": bascule,
            "p_double": p_double, "vraies_double": vraies_double, "p_d": p_d, "p5_un": p5_un, "p5_deux": p5_deux,
            "bloquees": bloquees}


def cas_2_crypto_transposition():
    se, sp = 0.85, 0.97
    general, p_e_g = bayes(0.005, se, 1 - sp)
    vpn_g, _ = bayes_negatif(0.005, se, 1 - sp)
    otc, p_e_o = bayes(0.04, se, 1 - sp)
    seuil = 400 / (400 + 1500)
    c_seuil = cote(seuil) * (1 - sp) / se
    bascule = proba(c_seuil)
    alertes_g, alertes_o = 50_000 * p_e_g, 2_000 * p_e_o
    passer, retenir = otc * 1500, (1 - otc) * 400
    perte = (passer - retenir) * alertes_o
    otc_1, _ = bayes(0.01, se, 1 - sp)
    print(f"Cas 2 : général P(alerte) {p_e_g:.4f}, VPP {general:.5f}, VPN {1 - vpn_g:.5f} ;"
          f" OTC P(alerte) {p_e_o:.4f}, VPP {otc:.5f} ; seuil {seuil:.5f}")
    print(f"  alertes/mois {alertes_g:.0f} et {alertes_o:.1f} ; par alerte OTC : laisser {passer:.1f}, retenir"
          f" {retenir:.1f} ; perte si transposé {perte:.0f} AED/mois ; bascule base {bascule:.5f}")
    return {"general": general, "p_e_g": p_e_g, "vpn_g": 1 - vpn_g, "otc": otc, "p_e_o": p_e_o, "seuil": seuil,
            "bascule": bascule, "alertes_g": alertes_g, "alertes_o": alertes_o, "passer": passer,
            "retenir": retenir, "perte": perte, "otc_1": otc_1}


def cas_3_assureur_indices():
    base = 0.03
    lr = {"tardive": 0.40 / 0.10, "hors_reseau": 0.50 / 0.20, "photos": 0.30 / 0.02}
    trois, c_trois = bayes_cotes(base, lr.values())
    deux, c_deux = bayes_cotes(base, (lr["tardive"], lr["hors_reseau"]))
    lr_joint = 0.25 / 0.05
    trois_c, c_trois_c = bayes_cotes(base, (lr_joint, lr["photos"]))
    deux_c, c_deux_c = bayes_cotes(base, (lr_joint,))
    bascule_lr = cote(0.15) / cote(base)
    surcout = 800 * 120
    print(f"Cas 3 : cote de départ {cote(base):.6f} ; LR {[round(x, 1) for x in lr.values()]} ;"
          f" 3 indices {trois:.5f}, indices 1+2 {deux:.5f}")
    print(f"  LR joint mesuré {lr_joint:.0f} : 1+2 {deux_c:.5f}, 3 indices {trois_c:.5f} ;"
          f" bascule LR joint {bascule_lr:.4f} ; surcoût naïf {surcout} AED/mois")
    return {"lr": lr, "trois": trois, "c_trois": c_trois, "deux": deux, "c_deux": c_deux, "trois_c": trois_c,
            "c_trois_c": c_trois_c, "deux_c": deux_c, "c_deux_c": c_deux_c, "bascule": bascule_lr,
            "surcout": surcout}


def cas_4_btp_factures():
    lr1, lr2 = 0.8 / 0.05, 0.20 / 0.01
    ht, devis = 480_000, 400_000
    ecart = ht / devis - 1
    tva_due, tva_facturee = 0.05 * ht, 25_000
    a = bayes_cotes(0.015, (lr1,))
    b = bayes_cotes(0.06, (lr1,))
    c = bayes_cotes(0.015, (lr1, lr2))
    bascule_base = proba(1 / lr1)
    b_moins = bayes_cotes(0.06, (lr1 * 0.9,))
    p_e1 = 0.8 * 0.015 + 0.05 * 0.985
    signalees = 4000 * p_e1
    irregulieres = 4000 * 0.8 * 0.015
    honnetes = signalees - irregulieres
    print(f"Cas 4 : écart au devis {ecart:.0%} ; TVA due {tva_due:.0f} contre {tva_facturee} facturés ;"
          f" LR {lr1:.0f} et {lr2:.0f}")
    print(f"  A (1,5 %, E1) {a[0]:.5f} ; B (6 %, E1) {b[0]:.5f} ; C (1,5 %, E1+E2) {c[0]:.5f} ;"
          f" bascule base {bascule_base:.6f} ; B avec LR -10 % {b_moins[0]:.5f}")
    print(f"  lecture naïve : {signalees:.0f} factures suspendues/mois dont {honnetes:.0f} honnêtes ;"
          f" coût {honnetes * 1500:.0f} AED/mois")
    return {"lr1": lr1, "lr2": lr2, "ecart": ecart, "tva_due": tva_due, "a": a, "b": b, "c": c,
            "bascule": bascule_base, "b_moins": b_moins, "p_e1": p_e1, "signalees": signalees,
            "irregulieres": irregulieres, "honnetes": honnetes}


def corrige():
    e1 = bayes(0.01, 0.9, 0.05)[0]
    e2 = proba(cote(0.1) * 0.9 / 0.05)
    e3 = bayes(0.3, 0.4, 0.4)[0]
    e6 = bayes(0.01, 0.85, 0.03)[0]
    e7_faux = 0.019 / (0.95 * 0.02 + 0.10 * 0.02)
    e8 = bayes_cotes(0.03, (4, 2.5, 15))[0]
    print(f"Corrigé : ex1 {e1:.5f} ; ex2 {e2:.3f} ; ex3 {e3:.1f} ; ex4 LR {0.8 / 0.2:.0f} ; ex6 {e6:.5f} ;"
          f" ex7 faux {e7_faux:.5f} ; ex8 {e8:.5f}")
    return e1, e2, e3, e6, e7_faux, e8


def main() -> None:
    d = demonstrations()
    assert d["comptes"] == (190, 980, 1170) and proche(d["d1"], 0.16239, 5) and math.isclose(d["d1"], d["post"])
    assert bayes(0.02, 0.0, 0.0)[0] is None                                                 # D1 : P(E) = 0
    assert proche(190 / 10_000, 0.019, 9) and proche(1170 / 10_000, 0.117, 9)
    assert proche(d["p_e"], 0.117, 9) and proche(d["p_non_e"], 0.883, 9) and math.isclose(d["p_e"] + d["p_non_e"], 1)
    assert proche(0.05 * 0.02, 0.001, 9) and proche(0.90 * 0.98, 0.882, 9)
    assert proche(d["neg"], 0.00113, 5) and proche(1 - d["neg"], 0.99887, 5)
    assert proche(d["c0"], 0.020408, 6) and proche(d["c0"] * 9.5, 0.19388, 5) and proche(proba(d["c0"] * 9.5), 0.16239, 5)
    assert math.isclose(proba(d["c0"] * 9.5), d["post"])                                    # D3 : forme cotes
    assert proche(d["c2"], 3.4898, 4) and proche(d["p2"], 0.77727, 5) and math.isclose(d["seq"], d["p2"])
    assert proche(9.5 * 18, 171, 9) and proche(d["copie"][1], 1.84184, 5) and proche(d["copie"][0], 0.64811, 5)
    assert proche(9.5 * 9.5, 90.25, 9)
    assert proche(d["elasticite"], 0.85470, 5) and proche(d["hausse"], 0.00853, 5)
    assert proche(bayes(0.0202, 0.95, 0.10)[0], 0.16378, 5)
    for base in [k / 100 for k in range(1, 100)]:                                           # D5 : monotonie
        assert bayes(base, 0.95, 0.10)[0] < bayes(base + 0.005, 0.95, 0.10)[0]
        el = 0.10 / bayes(base, 0.95, 0.10)[1]
        assert math.isclose(el, (1 - bayes(base, 0.95, 0.10)[0]) / (1 - base))
    for base, attendu in ((0.01, 0.088), (0.1, 0.514), (0.3, 0.803)):
        assert round(bayes(base, 0.95, 0.10)[0], 3) == attendu

    post, p_e = exemple_simple()
    assert proche(post, 0.16239, 5) and proche(p_e, 0.117, 9) and round(10_000 * p_e) == 1170
    assert proche(0.95 * 0.02, 0.019, 9) and proche(0.10 * 0.98, 0.098, 9) and proche(1 - post, 0.83761, 5)

    c1 = cas_1_service_public_revue()
    assert proche(c1["revues"]["A"], 1170, 6) and proche(10_000 * 0.02 * 0.95, 190, 6) and round(980 / 1170, 2) == 0.84
    assert proche(0.02 * 0.95 * 0.9, 0.0171, 9) and proche(0.98 * 0.10 * 0.05, 0.0049, 9) and proche(c1["p_double"], 0.022, 9)
    assert proche(c1["revues"]["B"], 220, 6) and proche(c1["vraies_double"], 171, 6) and proche(c1["p_d"], 0.77727, 5)
    assert proche(1170 / 120, 9.75, 9) and proche(220 / 120, 1.83, 2)
    assert c1["agents"] == {"A": 10, "B": 2} and proche(c1["oublis"]["A"], 10, 6) and proche(c1["oublis"]["B"], 29, 6)
    assert proche(c1["cout"]["A"], 7500, 6) and proche(c1["cout"]["B"], 5550, 6) and c1["cout"]["B"] < c1["cout"]["A"]
    assert proche(10 * 150, 1500, 9) and proche(29 * 150, 4350, 9) and 6000 - 1200 == 4800 and 29 - 10 == 19
    assert proche(c1["bascule"], 252.63, 2)
    assert proche(c1["p5_un"], 0.33333, 5) and proche(c1["p5_deux"], 0.9, 9) and proche(cote(0.05) * 171, 9, 9)
    assert proche(0.95 * 0.05, 0.0475, 9) and proche(0.10 * 0.95, 0.095, 9) and proche(0.0475 + 0.095, 0.1425, 9)
    assert proche(c1["bloquees"], 980, 6) and proche(c1["bloquees"] * 25, 24_500, 6) and proche(0.95 * 0.9, 0.855, 9)
    assert proche(3.4898 / 4.4898, 0.77727, 5) and proche(171 / 220, c1["p_d"], 12)

    c2 = cas_2_crypto_transposition()
    assert proche(0.85 * 0.005, 0.00425, 9) and proche(0.03 * 0.995, 0.02985, 9) and proche(c2["p_e_g"], 0.0341, 9)
    assert proche(c2["general"], 0.12463, 5) and proche(c2["vpn_g"], 0.99922, 5)
    assert proche(0.97 * 0.995, 0.96515, 9) and proche(0.15 * 0.005, 0.00075, 9) and proche(0.96515 + 0.00075, 0.9659, 9)
    assert proche(0.85 * 0.04, 0.034, 9) and proche(0.03 * 0.96, 0.0288, 9) and proche(c2["p_e_o"], 0.0628, 9)
    assert proche(c2["otc"], 0.54140, 5) and proche(c2["seuil"], 0.21053, 5)
    assert c2["general"] < c2["seuil"] < c2["otc"]
    assert proche(c2["alertes_g"], 1705, 6) and proche(c2["alertes_o"], 125.6, 6) and proche(50_000 * 0.005 * 0.85, 212.5, 9)
    assert proche(2_000 * 0.04 * 0.85, 68, 9)
    assert proche(c2["passer"], 812.1, 1) and proche(c2["retenir"], 183.4, 1) and proche(c2["perte"], 78960, -1)
    assert proche(c2["passer"] - c2["retenir"], 628.7, 1)
    assert proche(c2["bascule"], 0.00932, 5) and proche(bayes(c2["bascule"], 0.85, 0.03)[0], c2["seuil"], 9)
    assert proche(cote(c2["seuil"]), 0.26667, 5) and proche(0.03 / 0.85, 0.035294, 6)
    assert proche(cote(c2["seuil"]) * 0.03 / 0.85, 0.0094118, 7) and proche(1 - c2["otc"], 0.4586, 4)

    c3 = cas_3_assureur_indices()
    assert [round(x, 1) for x in c3["lr"].values()] == [4.0, 2.5, 15.0] and proche(cote(0.03), 0.030928, 6)
    assert proche(c3["c_trois"], 4.6392, 4) and proche(c3["trois"], 0.82267, 5) and proche(4 * 2.5 * 15, 150, 9)
    assert proche(c3["c_deux"], 0.30928, 5) and proche(c3["deux"], 0.23622, 5)
    assert proche(c3["c_deux_c"], 0.15464, 5) and proche(c3["deux_c"], 0.13393, 5)
    assert proche(c3["c_trois_c"], 2.3196, 4) and proche(c3["trois_c"], 0.69876, 5)
    assert c3["deux_c"] < 0.15 < c3["deux"] < 0.5 < c3["trois_c"] < c3["trois"]
    assert proche(cote(0.15), 0.17647, 5) and proche(c3["bascule"], 5.7059, 4) and c3["surcout"] == 96_000

    c4 = cas_4_btp_factures()
    assert proche(c4["ecart"], 0.20, 9) and c4["tva_due"] == 24_000 and c4["lr1"] == 16 and proche(c4["lr2"], 20, 9)
    assert proche(cote(0.015), 0.015228, 6) and proche(cote(0.06), 0.06383, 5)
    assert proche(c4["a"][1], 0.24365, 5) and proche(c4["a"][0], 0.19592, 5)
    assert proche(c4["b"][1], 1.0213, 4) and proche(c4["b"][0], 0.50526, 5)
    assert proche(c4["c"][1], 4.8731, 4) and proche(c4["c"][0], 0.82973, 5)
    assert 0.1 < c4["a"][0] < 0.5 < c4["b"][0] and c4["c"][0] > 0.5
    assert proche(c4["bascule"], 0.058824, 6) and proche(1 / 16, 0.0625, 9)
    assert proche(c4["b_moins"][1], 0.91915, 5) and proche(c4["b_moins"][0], 0.47894, 5) and c4["b_moins"][0] < 0.5
    assert proche(16 * 0.9, 14.4, 9)
    assert proche(0.8 * 0.015, 0.012, 9) and proche(0.05 * 0.985, 0.04925, 9) and proche(c4["p_e1"], 0.06125, 9)
    assert proche(c4["signalees"], 245, 6) and proche(c4["irregulieres"], 48, 6) and proche(c4["honnetes"], 197, 6)
    assert proche(c4["honnetes"] * 1500, 295_500, 3)

    e1, e2, e3, e6, e7, e8 = corrige()
    assert proche(e1, 0.15385, 5) and proche(e2, 0.667, 3) and math.isclose(e3, 0.3)
    assert proche(0.9 * 0.01, 0.009, 9) and proche(0.05 * 0.99, 0.0495, 9) and math.isclose(e2, bayes(0.1, 0.9, 0.05)[0])
    assert proche(cote(0.1), 1 / 9, 12) and proche(cote(0.1) * 18, 2, 12)
    assert proche(e6, 0.22251, 5) and e6 > c2["seuil"] and proche(0.85 * 0.01, 0.0085, 9) and proche(0.03 * 0.99, 0.0297, 9)
    assert proche(e7, 0.90476, 5) and proche(0.95 * 0.02 + 0.10 * 0.02, 0.021, 9) and e8 == c3["trois"]
    assert proche(0.009 + 0.0495, 0.0585, 9) and proche(0.0085 + 0.0297, 0.0382, 9) and proche(0.95 * 0.02, 0.019, 9)
    assert proche(0.05 * 0.9, 0.045, 9) and proche(0.09 / 0.135, e2, 9) and proche(0.4 * 0.3, 0.12, 9)
    assert proche(0.4 * 0.7, 0.28, 9) and proche(4.6392 / 5.6392, 0.82267, 5) and proche(cote(0.03) * 150, 4.6392, 4)
    assert round((c3["bascule"] - 5) / c3["bascule"] * 100) == 12 and proche(c3["deux_c"] * 100, 13.4, 1)
    assert 9800 - 980 == 8820 and 10 + 8820 == 8830 and proche(4.8731 / 5.8731, 0.82973, 5)
    for mauvais in (lambda: bayes(1.2, 0.9, 0.1), lambda: cote(-0.1), lambda: proba(-1)):
        try:
            mauvais()
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError attendue")
    assert cote(1.0) is None
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Démonstrations
  D1 comptes : 190 / 1170 = 0.16239 ; détecteur muet : None
  D2 P(E) = 0.117 ; P(non E) = 0.883 ; somme 1.000
  D3 cote 0.020408 x 9.5 = 0.19388 -> P = 0.16239
  D4 deux détecteurs : cote 3.4898 -> P = 0.77727 (en deux temps 0.77727) ; copie : naïf 0.64811 contre vrai 0.16239
  D5 élasticité alpha / P(E) = 0.85470 ; +1 % sur la base -> +0.853% sur P(H|E)
Exemple simple : 0.95 x 0.02 = 0.019 ; 0.10 x 0.98 = 0.098 ; P(E) = 0.117 ; P(fausse | alerte) = 0.16239
Cas 1 : alertes 1170/jour dont 190 vraies (84% fausses) ; doubles 220 dont 171 vraies, P = 0.77727
  agents A 10 / B 2 ; oublis A 10 / B 29 ; coût A 7500 / B 5550 AED/jour ; bascule 252.63 AED par oubli
  taux d'erreur 5 % : un détecteur 0.33333, deux détecteurs 0.90000 ; blocage naïf : 980 réponses justes, 24500 AED/jour
Cas 2 : général P(alerte) 0.0341, VPP 0.12463, VPN 0.99922 ; OTC P(alerte) 0.0628, VPP 0.54140 ; seuil 0.21053
  alertes/mois 1705 et 125.6 ; par alerte OTC : laisser 812.1, retenir 183.4 ; perte si transposé 78960 AED/mois ; bascule base 0.00932
Cas 3 : cote de départ 0.030928 ; LR [4.0, 2.5, 15.0] ; 3 indices 0.82267, indices 1+2 0.23622
  LR joint mesuré 5 : 1+2 0.13393, 3 indices 0.69876 ; bascule LR joint 5.7059 ; surcoût naïf 96000 AED/mois
Cas 4 : écart au devis 20% ; TVA due 24000 contre 25000 facturés ; LR 16 et 20
  A (1,5 %, E1) 0.19592 ; B (6 %, E1) 0.50526 ; C (1,5 %, E1+E2) 0.82973 ; bascule base 0.058824 ; B avec LR -10 % 0.47894
  lecture naïve : 245 factures suspendues/mois dont 197 honnêtes ; coût 295500 AED/mois
Corrigé : ex1 0.15385 ; ex2 0.667 ; ex3 0.3 ; ex4 LR 4 ; ex6 0.22251 ; ex7 faux 0.90476 ; ex8 0.82267
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme met à jour une probabilité après une ou plusieurs observations, sous forme directe ou sous forme de cotes, puis compare le résultat à un seuil de décision.

```text
ALGORITHME Bayes
ENTRÉES : taux de base π, sensibilité Se, taux de fausses alertes α
SORTIE  : P(H | E), ou « indéfini » si E est impossible

  P_E ← Se × π + α × (1 − π)
  SI P_E = 0 ALORS RETOURNER indéfini
  RETOURNER Se × π / P_E

ALGORITHME BayesEnCotes (plusieurs preuves indépendantes)
ENTRÉES : π, rapports de vraisemblance LR₁ … LRₘ, seuil t
SORTIE  : P(H | E₁ … Eₘ) et la décision

  cote ← π / (1 − π)
  POUR j DE 1 À m FAIRE cote ← cote × LRⱼ FIN POUR
  p ← cote / (1 + cote)
  SI p > t ALORS décision ← « agir » SINON décision ← « ne pas agir »
  RETOURNER p, décision
```

**Complexité.** O(1) pour une observation, O(m) pour m preuves. L'hypothèse d'indépendance des preuves n'est pas vérifiée par l'algorithme : c'est au concepteur de la justifier, ou de remplacer deux rapports par leur rapport joint mesuré.

**Du squelette au code.** Bayes est la fonction `bayes(base, sensibilite, fausse_alerte)`, qui renvoie `None` quand P(E) est nul ; le cas « pas d'alerte » est `bayes_negatif(base, sensibilite, fausse_alerte)`. La forme en cotes utilise `cote(p)` et `proba(c)`, et la boucle sur les preuves est `bayes_cotes(base, rapports)`. `main` vérifie que deux mises à jour successives avec `bayes` donnent la même chose que le produit des rapports de vraisemblance. Les quatre cas sont `cas_1_service_public_revue()`, `cas_2_crypto_transposition()`, `cas_3_assureur_indices()` et `cas_4_btp_factures()`.
