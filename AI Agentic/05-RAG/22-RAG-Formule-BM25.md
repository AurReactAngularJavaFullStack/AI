# Étape 22 — RAG — BM25

> Étape 22 du parcours · Prérequis : [Distance cosinus](<21-RAG-Formule-Distance-Cosinus.md>) · Suite : [Score hybride](<23-RAG-Formule-Score-Hybride.md>)

**Dossier :** 05-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  
**Nom du fichier :** 22-RAG-Formule-BM25.md

## Définition

BM25 (« Best Matching 25 ») est la fonction de classement lexicale de référence en recherche d'information, mise au point par Stephen Robertson et ses collègues dans le système Okapi au cours des années 1990. Elle note un document d'après les mots de la requête qu'il contient réellement, en combinant trois idées : un terme rare dans la collection pèse plus qu'un terme courant (c'est l'IDF) ; répéter un terme dans un document augmente le score, mais de moins en moins (c'est la saturation) ; à nombre d'occurrences égal, un document long est pénalisé, parce qu'il est moins concentré sur ce terme. Le score d'un document est la **somme** des contributions des termes de la requête. Contrairement au cosinus sur des embeddings (étapes 19 à 21), BM25 ignore les synonymes et les reformulations, mais il ne rate jamais une correspondance exacte : un code produit, un nom propre, une référence réglementaire. C'est pourquoi on le combine avec la recherche sémantique (étapes 23 et 24).

## Rôle dans un agent

Quand l'agent perçoit une question qui contient des termes exacts (un numéro de lot, le nom d'un produit de finance islamique, l'intitulé arabe d'une procédure), le **retriever lexical** interroge un index inversé et calcule BM25 pour les seuls documents qui contiennent au moins un de ces termes. Pour décider quoi injecter dans le prompt, l'agent fusionne cette liste avec celle de la recherche sémantique, par un score hybride (étape 23) ou par RRF (étape 24). BM25 a trois qualités opérationnelles : il ne demande ni GPU ni modèle, il est déterministe, et il est explicable, puisque l'on sait quels mots ont produit le score. Il sert aussi à la **mémoire**, pour retrouver une conversation passée par un identifiant exact, comme un numéro de facture ou de dossier.

## Équation complète

Score d'un document D pour une requête Q :

$$
\text{score}(D, Q) = \sum_{t \in Q} \text{IDF}(t) \cdot \frac{f(t, D)\,(k_1 + 1)}{f(t, D) + k_1 \left(1 - b + b\,\dfrac{|D|}{\text{avgdl}}\right)}
$$

IDF variante, toujours positive (celle du code, utilisée par Lucene et la plupart des moteurs) :

$$
\text{IDF}(t) = \ln\left(1 + \frac{N - n(t) + 0{,}5}{n(t) + 0{,}5}\right)
$$

IDF classique de Robertson-Spärck Jones, négative pour les termes très fréquents :

$$
\text{IDF}_{classique}(t) = \ln \frac{N - n(t) + 0{,}5}{n(t) + 0{,}5}
$$

Longueur moyenne des documents :

$$
\text{avgdl} = \frac{1}{N} \sum_{j=1}^{N} |D_j|
$$

Partie fréquence d'un terme, avec le dénominateur de saturation K propre au document :

$$
g(f) = \frac{f\,(k_1 + 1)}{f + K}
$$

$$
K = k_1 \left(1 - b + b\,\frac{|D|}{\text{avgdl}}\right)
$$

## Décryptage des symboles

$$
Q
$$

**Sens :** la requête, découpée en termes · **Type / plage :** liste de chaînes · **Variable Python :** `requete`

$$
D
$$

**Sens :** un document, découpé en termes · **Type / plage :** liste de chaînes · **Variable Python :** `doc`

$$
t
$$

**Sens :** un terme de la requête · **Type / plage :** chaîne · **Variable Python :** `t`

$$
f(t, D)
$$

**Sens :** nombre d'occurrences de t dans D · **Type / plage :** entier ≥ 0 · **Variable Python :** `f = doc.count(t)`

$$
\lvert D \rvert
$$

**Sens :** longueur du document, en termes · **Type / plage :** entier ≥ 1 · **Variable Python :** `len(doc)`

$$
N
$$

**Sens :** nombre de documents de la collection · **Type / plage :** entier ≥ 1 · **Variable Python :** `n_docs = len(corpus)`

$$
n(t)
$$

**Sens :** nombre de documents qui contiennent t · **Type / plage :** entier de 0 à N · **Variable Python :** `n_t`

**Symbole :** avgdl · **Sens :** longueur moyenne des documents · **Type / plage :** réel > 0 · **Variable Python :** `avgdl`

$$
k_1
$$

**Sens :** paramètre de saturation de la fréquence · **Type / plage :** réel ≥ 0, usuel de 1,2 à 2,0 · **Variable Python :** `k1` (1,5 dans ce parcours)

$$
b
$$

**Sens :** paramètre de normalisation par la longueur · **Type / plage :** réel dans [0 ; 1], usuel 0,75 · **Variable Python :** `b`

$$
K
$$

**Sens :** dénominateur de saturation du document · **Type / plage :** réel ≥ 0 · **Variable Python :** `k1 * (1 - b + b * len(doc) / avgdl)`

$$
g(f)
$$

**Sens :** partie fréquence : ce que le terme rapporte, en multiple de son IDF · **Type / plage :** réel dans [0, k₁ + 1[ · **Variable Python :** `partie_frequence(f, longueur, avgdl)`

$$
\text{IDF}(t)
$$

**Sens :** poids de rareté du terme · **Type / plage :** réel > 0 · **Variable Python :** `idf_bm25(n_t, n_docs)`

Le k du top-k et le k₁ de BM25 sont deux paramètres différents, et l'étape 24 introduira encore un

$$
k_{RRF}
$$

On garde toujours l'indice.

## Démonstration

### 1. Le score est une somme sur les termes de la requête

L'ancienne version de ce fichier ne le disait qu'en mots, et son code s'arrêtait à une fonction `bm25_term` qui renvoyait la seule partie fréquence g(f) : sans facteur IDF et sans somme sur la requête. Avec cette fonction, le mot courant « taux » dans un document et le mot rare « hypothecaire » dans un autre rapportent tous deux 1,0 : la rareté, qui est l'idée centrale de BM25, disparaît. La formule complète multiplie la partie fréquence de chaque terme par son IDF, puis additionne sur les termes de la requête. Un terme de la requête absent du document a f = 0, donc g(0) = 0 : il ne contribue pas, et le code le saute (`continue`).

### 2. Calcul à la main sur un corpus de cinq documents (le code reprend ces nombres)

| Document | Termes | \| D \| |
|---|---|---|
| D1 | taux, hypothecaire, fixe, dubai | 4 |
| D2 | taux, change, aed, usd | 4 |
| D3 | pret, hypothecaire, taux, variable, eibor, taux | 6 |
| D4 | carte, credit, plafond | 3 |
| D5 | frais, pret, personnel | 3 |

La requête est Q = (taux, hypothecaire). Les statistiques de la collection se lisent sur le tableau : N = 5, la longueur totale vaut 4 + 4 + 6 + 3 + 3 = 20, donc avgdl = 20/5 = 4 ; « taux » apparaît dans D1, D2 et D3, donc n(taux) = 3 ; « hypothecaire » apparaît dans D1 et D3, donc n(hypothecaire) = 2. On compte des **documents**, pas des occurrences : les deux « taux » de D3 ne comptent qu'une fois dans n(t).

Les IDF valent

$$
\ln(1 + 2{,}5/3{,}5) = \ln 1{,}7143 = 0{,}5390
$$

pour « taux » et ln(1 + 3,5/2,5) = ln 2,4 = 0,8755 pour « hypothecaire ». Pour D1 et D2, dont la longueur est égale à la moyenne,

$$
K = 1{,}5 \times (1 - 0{,}75 + 0{,}75 \times 4/4) = 1{,}5 ,
$$

et un terme présent une fois rapporte g(1) = 1 × 2,5 / (1 + 1,5) = 1 : exactement son IDF. Pour D3, plus long,

$$
K = 1{,}5 \times (0{,}25 + 0{,}75 \times 6/4) = 2{,}0625 ;
$$

« taux », présent deux fois, rapporte g(2) = 5 / 4,0625 = 1,2308, et « hypothecaire » g(1) = 2,5 / 3,0625 = 0,8163. D'où :

$$
\text{D1} = 0{,}5390 \times 1 + 0{,}8755 \times 1 = 1{,}4145
$$

$$
\text{D3} = 0{,}5390 \times 1{,}2308 + 0{,}8755 \times 0{,}8163 \approx 0{,}6634 + 0{,}7147
$$

La somme exacte vaut 1,3780 (les deux termes arrondis donneraient 1,3781). D2 ne contient que « taux » et obtient 0,5390 ; D4 et D5 ne contiennent aucun terme de la requête et obtiennent 0. Le classement est D1 > D3 > D2 > D4 = D5. D3 contient « taux » deux fois, mais il est une fois et demie plus long que la moyenne : sa normalisation par la longueur le fait passer juste derrière D1.

### 3. Deux IDF : la formule classique et la variante toujours positive

L'ancienne version écrivait la formule classique dans le texte et codait la variante, avec un +1 dans le logarithme, sans le signaler. Les deux ne donnent pas le même nombre : pour N = 10 et n = 6, la formule classique donne ln(4,5/6,5) = ln 0,6923 = −0,3677, et la variante

$$
\ln(1 + 0{,}6923) = \ln 1{,}6923 = 0{,}5261 .
$$

**L'IDF classique est négatif si et seulement si n(t) > N/2.** Comme n + 0,5 > 0, on peut raisonner sur le quotient :

$$
\ln\frac{N - n + 0{,}5}{n + 0{,}5} < 0 \iff \frac{N - n + 0{,}5}{n + 0{,}5} < 1 \iff N - n + 0{,}5 < n + 0{,}5 \iff N < 2n
$$

La première équivalence vient de ce que ln est croissante et vaut 0 en 1 ; la deuxième, de ce que l'on multiplie les deux membres par n + 0,5 > 0, ce qui ne change pas le sens de l'inégalité ; la troisième, de ce que l'on ajoute n − 0,5 des deux côtés. Le même calcul avec des égalités montre que l'IDF classique est nul exactement quand n = N/2. Dans le corpus du point 2, n(taux) = 3 > 5/2, donc l'IDF classique de « taux » vaut ln(2,5/3,5) = −0,3365.

**La variante est toujours strictement positive.** Posons x = (N − n + 0,5)/(n + 0,5). Comme n ≤ N, le numérateur vaut au moins 0,5, donc x > 0, donc 1 + x > 1 et ln(1 + x) > 0.

**Les deux décroissent quand n augmente** : quand n grandit, le numérateur de x diminue et son dénominateur augmente, donc x diminue, et ln est croissante. Plus un terme est rare, plus il pèse. Enfin, la base du logarithme ne change pas le classement : passer de ln à log₁₀ multiplie tous les IDF par la même constante positive 1/ln 10, donc tous les scores par cette constante.

### 4. Pourquoi un IDF négatif casse le classement : contre-exemple

Avec l'IDF classique, le corpus du point 2 donne D2 = −0,3365 : D2, qui contient un terme de la requête, passe **derrière** D4 et D5, qui n'en contiennent aucun (score 0). Pire, D1 obtient −0,3365 + 0,3365 = 0 : le meilleur document est à égalité avec des documents hors sujet, et D3 tombe à −0,1394. Un score qui baisse quand on ajoute un mot de la requête au document n'a plus de sens. La variante corrige le défaut : chaque terme présent ajoute une quantité strictement positive.

### 5. La saturation : la partie fréquence tend vers k₁ + 1

On réécrit la partie fréquence :

$$
g(f) = \frac{f\,(k_1 + 1)}{f + K} = (k_1 + 1)\left(1 - \frac{K}{f + K}\right)
$$

Quand f tend vers l'infini, K/(f + K) tend vers 0, donc g(f) tend vers k₁ + 1, sans jamais l'atteindre tant que K > 0. La fonction est croissante, parce que sa dérivée g'(f) = (k₁ + 1) K / (f + K)² est positive. Elle atteint la moitié de son plafond en f = K, puisque g(K) = (k₁ + 1)/2. Avec k₁ = 1,5 et un document de longueur moyenne (K = 1,5) :

| f | 1 | 2 | 5 | 10 | 100 | → ∞ |
|---|---|---|---|---|---|---|
| g(f) | 1,00 | 1,43 | 1,92 | 2,17 | 2,46 | 2,5 |

La contribution d'un terme est donc bornée par IDF(t) × (k₁ + 1) : bourrer un document d'un mot ne lui fait pas dépasser ce plafond.

### 6. Les cas particuliers de k₁ et de b

- k₁ = 0 donne le **modèle binaire**. Alors K = 0 et g(f) = f/f = 1 pour tout f ≥ 1 : seule la présence du terme compte, et le score est la somme des IDF des termes présents. Dans le corpus, D1 et D3 obtiennent tous deux 0,5390 + 0,8755 = 1,4145 : la répétition et la longueur n'ont plus d'effet.
- b = 0 **supprime la normalisation par la longueur**. Alors K = k₁ pour tous les documents. D3 obtient

$$
0{,}5390 \times (2 \times 2{,}5/3{,}5) + 0{,}8755 \times 1 = 0{,}7700 + 0{,}8755 = 1{,}6455
$$

et passe devant D1 (1,4145), parce que ses deux occurrences de « taux » ne sont plus réduites par sa longueur.
- b = 1 **normalise complètement**. Alors K = k₁ | D | / avgdl, et en divisant numérateur et dénominateur par | D |,

$$
g = (k_1 + 1)\,(f/\lvert D \rvert) \,/\, (f/\lvert D \rvert + k_1/\text{avgdl})
$$

La partie fréquence ne dépend plus que de la fréquence relative f / | D |. Avec avgdl = 4, deux occurrences dans un document de 8 termes et une occurrence dans un document de 4 termes donnent toutes deux 1,0000 ; avec b = 0,75, la première donne 1,0811.

Entre ces extrêmes, b = 0,75 est le compromis usuel, et augmenter k₁ ralentit la saturation, donc donne plus de poids aux répétitions.

### 7. Normaliser l'arabe avant d'indexer

BM25 compare les termes caractère par caractère : « ضريبة » (impôt, écrit avec un ة final) et « ضريبه » (écrit avec un ه) sont deux termes différents, avec deux n(t) différents, et la requête qui utilise l'un ne trouve pas le document qui utilise l'autre. Or ces variantes sont courantes dans les requêtes tapées en arabe : la hamza des alefs (أ، إ، آ) est souvent omise, le ة final est souvent tapé ه, les voyelles brèves (fatha, damma, kasra, soukoun, chadda, tanwin) figurent dans certains textes officiels mais pas dans les requêtes, et le tatweel (ـ) sert à allonger les mots dans les titres. Une normalisation minimale ramène ces variantes à une forme unique : أ، إ et آ deviennent ا ; ة devient ه ; diacritiques et tatweel sont supprimés. La règle d'or est de l'appliquer **à l'identique** aux documents, au moment de l'indexation, et aux requêtes, au moment de la recherche.

L'ordre des opérations compte. On normalise **avant** de découper, parce que le `\w` des expressions régulières de Python ne reconnaît pas les signes combinants : sans normalisation, « تَجْدِيد » (renouvellement, voyellé) est coupé en quatre morceaux, ت، ج، د et يد. On applique aussi la forme normale NFC en premier, parce qu'un même أ peut être codé en un caractère ou en deux (un alef suivi d'une hamza combinante) ; NFC recompose la forme en deux caractères pour que la table la reconnaisse.

Sur trois fiches de procédure (A1 : enregistrement à la TVA des entreprises ; A2 : remboursement de la TVA aux touristes ; A3 : renouvellement du permis de conduire à Abu Dhabi), la requête « استرداد ضريبه القيمه المضافه », tapée avec des ه, ne retrouve sans normalisation qu'un mot sur quatre dans A2, pour un score de 0,9808. Normalisée, elle en retrouve quatre dans A2 et trois dans A1. Comme chaque fiche compte 5 termes, avgdl = 5 et un terme présent une fois rapporte exactement son IDF ; avec N = 3, un terme présent dans une seule fiche a un IDF de ln(1 + 2,5/1,5) = 0,9808 et un terme présent dans deux fiches ln(1 + 1,5/2,5) = 0,4700. A2 obtient donc 0,9808 + 3 × 0,4700 = 2,3908 et A1 3 × 0,4700 = 1,4100. La seconde requête, voyellée, allongée par un tatweel et sans hamza, passe de 2 termes trouvés (1,9617) à 5 (4,9041).

Cette normalisation ne retire pas l'article ال : « الضريبة » et « ضريبة » restent deux termes différents, ce que traitent un racinement léger (*light stemming*) ou des n-grammes de caractères. D'autres règles courantes, comme ى (alef maqsura) → ي, ne sont pas appliquées ici.

## Effets et comportement

- **Un terme rare et présent fait monter le score** : son IDF est grand (point 3).
- **La répétition aide, puis sature** : la contribution d'un terme reste sous IDF(t) × (k₁ + 1) (point 5).
- **Un document long est pénalisé dès que b > 0**, et un document plus court que la moyenne est avantagé, puisque son K est inférieur à k₁ (point 6).
- **Augmenter k₁ ralentit la saturation** : les répétitions comptent davantage, ce que disait déjà l'ancienne version.
- **Un score BM25 n'a pas d'échelle fixe.** Il dépend de la collection, par N, n(t) et avgdl, et du nombre de termes de la requête. On ne fixe donc pas de seuil absolu sur BM25, et on le normalise avant de le combiner avec un cosinus (étape 23).
- **Correction de forme** : l'ancienne version écrivait que BM25 est « excellents pour les termes réglementaires exacts » ; il faut lire « excellent ».

## Du symbole au code Python

$$
\text{score}(D, Q)
$$

**Variable ou fonction :** `bm25_score(requete, doc, corpus, k1, b)`, fonction canonique du parcours

$$
\text{IDF}(t),\quad \text{IDF}_{classique}(t)
$$

**Variable ou fonction :** `idf_bm25(n_t, n_docs)`, `idf_classique(n_t, n_docs)`

$$
g(f)
$$

**Variable ou fonction :** `partie_frequence(f, longueur, avgdl, k1, b)`

**Symbole :** N, n(t), avgdl · **Variable ou fonction :** `n_docs`, `n_t`, `avgdl`, recalculés à chaque appel

**Symbole :** classement · **Variable ou fonction :** `classer(requete, corpus, noms, k1, b, score)`

**Symbole :** normalisation et découpage · **Variable ou fonction :** `normaliser_arabe(texte)`, `tokeniser(texte, normaliser)`

### Déroulé, ligne par ligne

**`idf_classique(n_t, n_docs)`** et **`idf_bm25(n_t, n_docs)`** sont les fonctions canoniques. Pour `n_t = 6` et `n_docs = 10`, le quotient vaut `4.5 / 6.5 = 0.6923` ; la première renvoie `math.log(0.6923) = -0.3677`, la seconde `math.log(1.6923) = 0.5261`. En Python, `math.log` est le logarithme naturel ln.

**`bm25_score(requete, doc, corpus, k1, b)`** est la fonction canonique, recopiée telle quelle.

- `n_docs = len(corpus)` et `avgdl = sum(len(d) for d in corpus) / n_docs` : N = 5 et avgdl = 20/5 = 4.0.
- `for t in requete` parcourt la requête **terme par terme** : c'est la somme

$$
\sum_{t \in Q} .
$$

- `f = doc.count(t)` : pour D3 et `t = "taux"`, `f = 2`. Si `f == 0`, `continue` passe au terme suivant, puisque la contribution serait nulle.
- `n_t = sum(1 for d in corpus if t in d)` compte les documents qui contiennent `t`, pas les occurrences : 3 pour « taux ».
- La dernière ligne ajoute `idf_bm25(n_t, n_docs) * f * (k1 + 1) / (f + k1 * (1 - b + b * len(doc) / avgdl))`. Pour D3 et « taux » : `0.5390 * 2 * 2.5 / (2 + 1.5 * (0.25 + 0.75 * 6 / 4))`, soit `0.5390 * 5 / 4.0625 = 0.6634`.

**`bm25_score_classique`** est la même boucle avec `idf_classique` ; elle ne sert qu'au contre-exemple du point 4.

**`partie_frequence(f, longueur, avgdl, k1, b)`** isole g(f). `partie_frequence(1, 4, 4.0)` vaut exactement `1.0`, et `partie_frequence(1.5, 4, 4.0)` vaut `1.25`, la moitié du plafond 2,5.

**`classer(requete, corpus, noms, k1, b, score)`** calcule un score par document, puis trie par `(-score, nom)` : score décroissant, nom en cas d'égalité, pour que la sortie soit reproductible. Le paramètre `score` permet de passer `bm25_score_classique` à la place de `bm25_score`.

**`TABLE_ARABE`** est une table de traduction construite par `str.maketrans` avec des noms Unicode explicites, `\N{ARABIC LETTER ALEF WITH HAMZA ABOVE}` par exemple, plutôt qu'avec des caractères invisibles à l'œil. Une valeur `None` supprime le caractère : c'est le cas du tatweel et des huit diacritiques de `range(0x064B, 0x0653)`, du fathatan au soukoun.

**`normaliser_arabe(texte)`** applique `unicodedata.normalize("NFC", texte)`, puis `.translate(TABLE_ARABE)`. « أبوظبي » devient « ابوظبي », « إعادة » devient « اعاده ».

**`tokeniser(texte, normaliser)`** normalise si on le lui demande, met en minuscules, puis découpe avec `re.findall(r"\w+", …)`. Le paramètre `normaliser=False` sert à montrer ce qui se passe sans normalisation.

**`main()`**, bloc par bloc.

1. Les statistiques du point 2 : `N = 5`, `avgdl = 4.0`, `n(taux) = 3`, `n(hypothecaire) = 2`.
2. Les IDF : 0,5390 et 0,8755 pour la variante ; −0,3365 et +0,3365 pour la formule classique.
3. Le classement complet : D1 = 1,4145, D3 = 1,3780, D2 = 0,5390, D4 = D5 = 0. L'`assert` vérifie l'ordre et les cinq valeurs.
4. Le détail de D3 : `grand_k = 2.0625`, puis 1,2308 et 0,8163, et l'on vérifie que la somme pondérée par les IDF redonne bien le score de D3.
5. L'IDF pour `N = 10` : −0,3677 contre 0,5261. La boucle sur `n` de 0 à 10 vérifie le théorème du point 3 : négatif si et seulement si `n > 5`, nul si et seulement si `n == 5`, variante toujours positive et décroissante. Puis les scores avec l'IDF classique : D2 = −0,3365 sous D4 = 0, et D1 = 0.
6. Le tableau de saturation du point 5 : 1,00, 1,43, 1,92, 2,17, 2,46, toujours sous 2,5, et une valeur à `1e-8` près de 2,5 pour `f = 10 ** 9`.
7. Les cas particuliers du point 6 : `k1=0.0` donne D1 = D3 = 1,4145 ; `b=0.0` met D3 (1,6455) devant D1 ; `b=1.0` donne 1,0000 pour les deux documents de même fréquence relative, et 1,0811 avec `b = 0.75`.
8. L'arabe. Le premier `assert` vérifie, par leurs noms Unicode, que `range(0x064B, 0x0653)` contient bien les huit diacritiques annoncés. Le mot voyellé `tajdid` est coupé en quatre sans normalisation et reste entier avec. Suivent les tests de la table, la forme en deux caractères recomposée par NFC, et la phrase « مكافأة نهاية الخدمة » (indemnité de fin de service), qui ne partage aucun terme avec sa saisie courante « مكافاه نهايه الخدمه » avant normalisation, et tous après. La double boucle calcule enfin les scores des deux requêtes, brutes puis normalisées : les termes trouvés passent de `[0, 1, 0]` à `[3, 4, 0]` et de `[0, 0, 2]` à `[0, 0, 5]`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`idf_classique(n_t, n_docs)`** — On peut imaginer un crieur public qui annonce la valeur d'un mot selon sa rareté dans le village : la fonction reçoit le nombre de documents qui contiennent le terme et le nombre total de documents, puis renvoie le logarithme naturel de (N − n + 0,5) / (n + 0,5), la formule de Robertson et Spärck Jones. Ce crieur a un défaut que le programme met en lumière : dès que le mot apparaît dans plus de la moitié des documents, le quotient passe sous 1 et la valeur devient négative, −0,3365 pour « taux » présent dans 3 documents sur 5, −0,3677 pour un terme présent dans 6 documents sur 10. Elle ne sert qu'au contre-exemple, à travers `bm25_score_classique`.

**`idf_bm25(n_t, n_docs)`** — C'est le même crieur, corrigé par Lucene et la plupart des moteurs pour ne jamais annoncer de valeur négative : la fonction reçoit les mêmes deux nombres et renvoie le logarithme de 1 + (N − n + 0,5) / (n + 0,5), qui reste strictement positif puisque son argument dépasse toujours 1. Elle donne 0,5390 à « taux » (3 documents sur 5), 0,8755 à « hypothecaire » (2 sur 5) et 0,5261 au terme présent dans 6 documents sur 10 ; `main` vérifie en outre, pour N = 10, qu'elle décroît strictement quand le terme devient plus fréquent, si bien que les mots rares pèsent toujours davantage.

**`bm25_score(requete, doc, corpus, k1, b)`** — Cette fonction est le juge principal du concours : pour un document donné, elle passe en revue chaque mot de la requête et lui attribue des points selon sa rareté, sa fréquence dans le document et la longueur de ce document. Elle reçoit la requête et le document sous forme de listes de mots, le corpus entier et les deux réglages k1 et b, 1,5 et 0,75 par défaut ; elle calcule le nombre de documents et leur longueur moyenne, ici 5 et 4,0, puis, pour chaque terme présent, multiplie son `idf_bm25` par la partie fréquence saturée et corrigée par la longueur, et additionne. Elle renvoie le score total, 1,4145 pour D1, 1,3780 pour D3, 0,5390 pour D2 et 0 pour D4 et D5.

**`bm25_score_classique(requete, doc, corpus, k1, b)`** — Voici le juge du concours précédent, rappelé pour qu'on voie ses erreurs : la fonction reçoit exactement les mêmes arguments que `bm25_score` et suit la même boucle, terme par terme, à une seule différence près, elle multiplie la partie fréquence par `idf_classique` au lieu de `idf_bm25`. Elle renvoie donc un score qui peut devenir négatif ; avec la requête « taux hypothecaire », D2, qui ne contient que « taux », obtient −0,3365 et passe sous D4, qui ne contient aucun terme de la requête et reste à 0, tandis que D1, qui contient les deux termes, tombe à 0, les deux IDF opposés s'annulant.

**`partie_frequence(f, longueur, avgdl, k1, b)`** — Cette fonction isole le multiplicateur de l'IDF, comme un mécanicien qui démonte une seule pièce du moteur pour la mesurer au banc : elle reçoit la fréquence f du terme dans le document, la longueur du document, la longueur moyenne du corpus et les réglages k1 et b, puis renvoie f (k1 + 1) / (f + k1 (1 − b + b |d| / avgdl)). Pour un document de longueur moyenne, un terme vu une fois rapporte exactement 1, et la valeur croît ensuite en ralentissant, 1,43, 1,92, 2,17 puis 2,46 pour f = 2, 5, 10 et 100, sans jamais franchir le plafond k1 + 1 = 2,5 : c'est la saturation que `main` vérifie.

**`classer(requete, corpus, noms, k1, b, score)`** — C'est le maître de cérémonie qui proclame le palmarès : la fonction reçoit la requête, le corpus, les noms des documents, les réglages k1 et b, et la fonction de score à utiliser, `bm25_score` par défaut. Elle calcule le score de chaque document, puis trie les couples (nom, score) par score décroissant en départageant les égalités par le nom pour que la sortie soit reproductible, et renvoie cette liste ordonnée. Avec les réglages par défaut, l'ordre est D1, D3, D2, D4, D5 ; avec k1 = 0, D1 et D3 font jeu égal à 1,4145, et avec b = 0, D3 passe devant à 1,6455.

**`normaliser_arabe(texte)`** — Cette fonction joue le scribe qui recopie chaque mot arabe dans une graphie unique avant de l'indexer, pour que l'utilisateur pressé et le rédacteur soigneux écrivent enfin la même chose : elle reçoit un texte, le met d'abord sous la forme Unicode NFC, ce qui recompose un alef suivi d'une hamza combinante en un seul caractère, puis lui applique la table `TABLE_ARABE`, qui ramène les trois alefs à hamza ou à madda vers l'alef nu, remplace le tā' marbūṭa par le hā' et supprime le tatweel et les huit diacritiques. Elle renvoie le texte normalisé ; « أبوظبي » devient ainsi « ابوظبي ».

**`tokeniser(texte, normaliser)`** — Elle est le découpeur qui transforme une phrase en liste de mots prêts à être comptés : la fonction reçoit un texte et un drapeau `normaliser`, vrai par défaut, passe le texte par `normaliser_arabe` si le drapeau le demande, le met en minuscules, puis renvoie toutes les suites de caractères de mot trouvées par l'expression `\w+`. Le drapeau faux sert à montrer le désastre évité : sans normalisation, le mot voyellé « tajdid » est coupé en quatre morceaux, parce que les diacritiques ne sont pas des caractères de mot, alors qu'avec normalisation il reste entier.

**`main()`** — Le chef d'orchestre déroule huit actes sur un petit corpus de cinq documents bancaires et la requête « taux hypothecaire » : il calcule les statistiques N = 5 et avgdl = 4,0, les deux familles d'IDF, le classement complet, puis le détail de D3 avec K = 2,0625 et les contributions 1,2308 et 0,8163. Il vérifie ensuite sur N = 10 que l'IDF classique devient négatif exactement au-delà de la moitié des documents, mesure la saturation de la partie fréquence, éprouve les cas extrêmes de k1 et de b, et termine par l'arabe, où la normalisation fait passer les termes trouvés de [0, 1, 0] à [3, 4, 0] pour la première requête et de [0, 0, 2] à [0, 0, 5] pour la seconde. Chaque nombre est gardé par un `assert`, et la dernière ligne n'annonce le succès que si tous ont tenu.

```python
"""Étape 22 — BM25 : score complet, deux IDF, saturation, longueur, requêtes arabes normalisées."""
import math
import re
import sys
import unicodedata

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def idf_classique(n_t: int, n_docs: int) -> float:
    """IDF de Robertson-Spärck Jones : négatif quand le terme est dans plus de la moitié des documents."""
    return math.log((n_docs - n_t + 0.5) / (n_t + 0.5))


def idf_bm25(n_t: int, n_docs: int) -> float:
    """Variante utilisée par Lucene et la plupart des moteurs : toujours positive."""
    return math.log(1 + (n_docs - n_t + 0.5) / (n_t + 0.5))


def bm25_score(requete: list[str], doc: list[str], corpus: list[list[str]], k1: float = 1.5, b: float = 0.75) -> float:
    n_docs = len(corpus)
    avgdl = sum(len(d) for d in corpus) / n_docs
    score = 0.0
    for t in requete:
        f = doc.count(t)
        if f == 0:
            continue
        n_t = sum(1 for d in corpus if t in d)
        score += idf_bm25(n_t, n_docs) * f * (k1 + 1) / (f + k1 * (1 - b + b * len(doc) / avgdl))
    return score


def bm25_score_classique(requete: list[str], doc: list[str], corpus: list[list[str]],
                         k1: float = 1.5, b: float = 0.75) -> float:
    """La même somme avec l'IDF classique : sert seulement à montrer son défaut."""
    n_docs = len(corpus)
    avgdl = sum(len(d) for d in corpus) / n_docs
    score = 0.0
    for t in requete:
        f = doc.count(t)
        if f == 0:
            continue
        n_t = sum(1 for d in corpus if t in d)
        score += idf_classique(n_t, n_docs) * f * (k1 + 1) / (f + k1 * (1 - b + b * len(doc) / avgdl))
    return score


def partie_frequence(f: float, longueur: int, avgdl: float, k1: float = 1.5, b: float = 0.75) -> float:
    """f (k1 + 1) / (f + k1 (1 − b + b |d| / avgdl)) : le multiplicateur de l'IDF pour un terme."""
    return f * (k1 + 1) / (f + k1 * (1 - b + b * longueur / avgdl))


def classer(requete: list[str], corpus: list[list[str]], noms: list[str], k1: float = 1.5, b: float = 0.75,
            score=bm25_score) -> list[tuple[str, float]]:
    """Classement décroissant ; égalités départagées par le nom."""
    scores = [(nom, score(requete, doc, corpus, k1, b)) for nom, doc in zip(noms, corpus)]
    return sorted(scores, key=lambda kv: (-kv[1], kv[0]))


ALEF = "\N{ARABIC LETTER ALEF}"
TABLE_ARABE = str.maketrans({
    "\N{ARABIC LETTER ALEF WITH HAMZA ABOVE}": ALEF,                   # أ → ا
    "\N{ARABIC LETTER ALEF WITH HAMZA BELOW}": ALEF,                   # إ → ا
    "\N{ARABIC LETTER ALEF WITH MADDA ABOVE}": ALEF,                   # آ → ا
    "\N{ARABIC LETTER TEH MARBUTA}": "\N{ARABIC LETTER HEH}",          # ة → ه
    "\N{ARABIC TATWEEL}": None,                                        # ـ (trait d'allongement) supprimé
    **{chr(c): None for c in range(0x064B, 0x0653)},                   # diacritiques, du fathatan au soukoun
})


def normaliser_arabe(texte: str) -> str:
    """NFC d'abord, pour recomposer un alef suivi d'une hamza combinante ; puis la table."""
    return unicodedata.normalize("NFC", texte).translate(TABLE_ARABE)


def tokeniser(texte: str, normaliser: bool = True) -> list[str]:
    if normaliser:
        texte = normaliser_arabe(texte)
    return re.findall(r"\w+", texte.lower())


def main() -> None:
    noms = ["D1", "D2", "D3", "D4", "D5"]
    corpus = [
        ["taux", "hypothecaire", "fixe", "dubai"],
        ["taux", "change", "aed", "usd"],
        ["pret", "hypothecaire", "taux", "variable", "eibor", "taux"],
        ["carte", "credit", "plafond"],
        ["frais", "pret", "personnel"],
    ]
    requete = ["taux", "hypothecaire"]

    print("1. Statistiques du corpus")
    n_docs = len(corpus)
    avgdl = sum(len(d) for d in corpus) / n_docs
    n_t = {t: sum(1 for d in corpus if t in d) for t in requete}
    print(f"  N = {n_docs}   avgdl = 20 / 5 = {avgdl}   n(taux) = {n_t['taux']}   n(hypothecaire) = {n_t['hypothecaire']}")
    assert (n_docs, avgdl, n_t) == (5, 4.0, {"taux": 3, "hypothecaire": 2})

    print("2. IDF des termes de la requête")
    for t in requete:
        print(f"  {t:<13} variante = {idf_bm25(n_t[t], n_docs):.4f}   classique = {idf_classique(n_t[t], n_docs):+.4f}")
    assert round(idf_bm25(3, 5), 4) == 0.5390 and round(idf_bm25(2, 5), 4) == 0.8755
    assert round(idf_classique(3, 5), 4) == -0.3365 and round(idf_classique(2, 5), 4) == 0.3365

    print("3. Score complet = somme sur les termes de la requête (k1 = 1.5, b = 0.75)")
    classement = classer(requete, corpus, noms)
    print("  " + "   ".join(f"{nom} = {s:.4f}" for nom, s in classement))
    scores = dict(classement)
    assert [nom for nom, _ in classement] == ["D1", "D3", "D2", "D4", "D5"]
    assert [round(scores[n], 4) for n in noms] == [1.4145, 0.5390, 1.3780, 0.0, 0.0]

    print("4. Détail de D3 (|D| = 6, plus long que la moyenne)")
    grand_k = 1.5 * (1 - 0.75 + 0.75 * 6 / 4)
    g_taux, g_hyp = partie_frequence(2, 6, 4.0), partie_frequence(1, 6, 4.0)
    print(f"  K = 1.5 × (0.25 + 0.75 × 6/4) = {grand_k}   taux (f = 2) → {g_taux:.4f}   hypothecaire (f = 1) → {g_hyp:.4f}")
    assert grand_k == 2.0625 and round(g_taux, 4) == 1.2308 and round(g_hyp, 4) == 0.8163
    assert abs(scores["D3"] - (idf_bm25(3, 5) * g_taux + idf_bm25(2, 5) * g_hyp)) < 1e-12
    assert partie_frequence(1, 4, 4.0) == 1.0     # |d| = avgdl et f = 1 : le terme rapporte exactement son IDF

    print("5. IDF classique négatif si et seulement si n(t) > N/2")
    print(f"  N = 10, n = 6 : classique = {idf_classique(6, 10):.4f}   variante = {idf_bm25(6, 10):.4f}")
    assert round(idf_classique(6, 10), 4) == -0.3677 and round(idf_bm25(6, 10), 4) == 0.5261
    for n in range(0, 11):
        assert (idf_classique(n, 10) < 0) == (n > 5) and (abs(idf_classique(n, 10)) < 1e-12) == (n == 5)
        assert idf_bm25(n, 10) > 0
        if n > 0:
            assert idf_bm25(n, 10) < idf_bm25(n - 1, 10)    # plus le terme est rare, plus il pèse
    classiques = {nom: bm25_score_classique(requete, doc, corpus) for nom, doc in zip(noms, corpus)}
    print("  avec l'IDF classique : " + "   ".join(f"{nom} = {round(s, 4) + 0.0:+.4f}" for nom, s in classiques.items()))
    assert classiques["D2"] < classiques["D4"] == 0.0 and abs(classiques["D1"]) < 1e-12

    print("6. Saturation (|d| = avgdl, k1 = 1.5) : la partie fréquence tend vers k1 + 1 = 2.5")
    valeurs = [partie_frequence(f, 4, 4.0) for f in (1, 2, 5, 10, 100)]
    print("  f = 1, 2, 5, 10, 100 → " + ", ".join(f"{v:.2f}" for v in valeurs))
    assert [round(v, 2) for v in valeurs] == [1.00, 1.43, 1.92, 2.17, 2.46]
    assert all(x < y < 2.5 for x, y in zip(valeurs, valeurs[1:]))
    assert abs(partie_frequence(10 ** 9, 4, 4.0) - 2.5) < 1e-8 and partie_frequence(1.5, 4, 4.0) == 1.25

    print("7. Cas particuliers de k1 et de b")
    binaire = dict(classer(requete, corpus, noms, k1=0.0))
    print(f"  k1 = 0 : D1 = {binaire['D1']:.4f} = D3 = {binaire['D3']:.4f} = IDF(taux) + IDF(hypothecaire)")
    assert binaire["D1"] == binaire["D3"] == idf_bm25(3, 5) + idf_bm25(2, 5)
    sans_longueur = classer(requete, corpus, noms, b=0.0)
    print(f"  b = 0 : {sans_longueur[0][0]} = {sans_longueur[0][1]:.4f} passe devant {sans_longueur[1][0]} = {sans_longueur[1][1]:.4f}")
    assert [nom for nom, _ in sans_longueur[:2]] == ["D3", "D1"] and round(sans_longueur[0][1], 4) == 1.6455
    long8, court4 = partie_frequence(2, 8, 4.0, b=1.0), partie_frequence(1, 4, 4.0, b=1.0)
    print(f"  b = 1 : f = 2 sur |d| = 8 → {long8:.4f}   f = 1 sur |d| = 4 → {court4:.4f}   (même fréquence relative)")
    assert long8 == court4 == 1.0 and round(partie_frequence(2, 8, 4.0), 4) == 1.0811

    print("8. Arabe : normaliser, puis découper")
    assert [unicodedata.name(chr(c)) for c in range(0x064B, 0x0653)] == [
        "ARABIC FATHATAN", "ARABIC DAMMATAN", "ARABIC KASRATAN", "ARABIC FATHA",
        "ARABIC DAMMA", "ARABIC KASRA", "ARABIC SHADDA", "ARABIC SUKUN"]
    tajdid = "ت\N{ARABIC FATHA}ج\N{ARABIC SUKUN}د\N{ARABIC KASRA}يد"    # « tajdid » (renouvellement), voyellé
    print(f"  sans normalisation, \\w+ coupe le mot voyellé : {tokeniser(tajdid, normaliser=False)}")
    assert tokeniser(tajdid, normaliser=False) == ["ت", "ج", "د", "يد"] and tokeniser(tajdid) == ["تجديد"]
    assert normaliser_arabe("أبوظبي") == "ابوظبي" and normaliser_arabe("إعادة") == "اعاده"
    assert normaliser_arabe("آل") == "ال" and normaliser_arabe("رخص\N{ARABIC TATWEEL}ة") == "رخصه"
    assert normaliser_arabe(ALEF + "\N{ARABIC HAMZA ABOVE}") == ALEF     # alef + hamza combinante, recomposé par NFC
    politique, saisie = "مكافأة نهاية الخدمة", "مكافاه نهايه الخدمه"   # indemnité de fin de service
    assert not set(tokeniser(politique, False)) & set(tokeniser(saisie, False))
    assert tokeniser(politique) == tokeniser(saisie) == ["مكافاه", "نهايه", "الخدمه"]
    docs_ar = ["تسجيل ضريبة القيمة المضافة للشركات",       # A1 : enregistrement à la TVA des entreprises
               "استرداد ضريبة القيمة المضافة للسياح",        # A2 : remboursement de TVA aux touristes
               "تجديد رخصة القيادة في أبوظبي"]               # A3 : renouvellement du permis à Abu Dhabi
    requetes_ar = ["استرداد ضريبه القيمه المضافه",            # ه au lieu de ة, comme on tape souvent
                   tajdid + " رخص\N{ARABIC TATWEEL}ة القيادة في ابوظبي"]   # voyelles, tatweel, alef sans hamza
    resultats = {}
    for normaliser in (False, True):
        corpus_ar = [tokeniser(t, normaliser) for t in docs_ar]
        for i, q in enumerate(requetes_ar, start=1):
            qt = tokeniser(q, normaliser)
            s = [bm25_score(qt, d, corpus_ar) for d in corpus_ar]
            trouves = [sum(1 for t in qt if t in d) for d in corpus_ar]
            resultats[(normaliser, i)] = (s, trouves)
            etat = "normalisé  " if normaliser else "brut       "
            print(f"  {etat} requête {i} : scores A1, A2, A3 = {[round(x, 4) for x in s]}   termes trouvés = {trouves}")
    assert resultats[(False, 1)][1] == [0, 1, 0] and resultats[(True, 1)][1] == [3, 4, 0]
    assert resultats[(False, 2)][1] == [0, 0, 2] and resultats[(True, 2)][1] == [0, 0, 5]
    s_brut, s_norm = resultats[(False, 1)][0], resultats[(True, 1)][0]
    assert [round(x, 4) for x in s_norm] == [1.41, 2.3908, 0.0] and round(s_brut[1], 4) == 0.9808
    assert round(resultats[(True, 2)][0][2], 4) == 4.9041 and round(resultats[(False, 2)][0][2], 4) == 1.9617

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Statistiques du corpus
  N = 5   avgdl = 20 / 5 = 4.0   n(taux) = 3   n(hypothecaire) = 2
2. IDF des termes de la requête
  taux          variante = 0.5390   classique = -0.3365
  hypothecaire  variante = 0.8755   classique = +0.3365
3. Score complet = somme sur les termes de la requête (k1 = 1.5, b = 0.75)
  D1 = 1.4145   D3 = 1.3780   D2 = 0.5390   D4 = 0.0000   D5 = 0.0000
…
  avec l'IDF classique : D1 = +0.0000   D2 = -0.3365   D3 = -0.1394   D4 = +0.0000   D5 = +0.0000
…
  f = 1, 2, 5, 10, 100 → 1.00, 1.43, 1.92, 2.17, 2.46
…
  b = 0 : D3 = 1.6455 passe devant D1 = 1.4145
…
  brut        requête 1 : scores A1, A2, A3 = [0.0, 0.9808, 0.0]   termes trouvés = [0, 1, 0]
…
  normalisé   requête 1 : scores A1, A2, A3 = [1.41, 2.3908, 0.0]   termes trouvés = [3, 4, 0]
  normalisé   requête 2 : scores A1, A2, A3 = [0.0, 0.0, 4.9041]   termes trouvés = [0, 0, 5]
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : BM25 n'est pas une boîte noire. C'est une somme d'IDF pondérés par une fréquence qui sature, calculée sur des statistiques que l'on peut recompter à la main ; et, sur de l'arabe réel, sa qualité dépend d'abord de la normalisation appliquée avant le découpage.

## Squelette algorithmique

BM25 se calcule en deux temps : une préparation du corpus (longueur moyenne, fréquence documentaire de chaque terme), puis le score de chaque document pour une requête. Pour l'arabe, une normalisation des caractères vient avant le découpage en mots.

```text
ALGORITHME BM25
ENTRÉES : requête Q (liste de termes), corpus D₁ … D_N (listes de termes), k₁, b
SORTIE  : les documents classés par score décroissant

  avgdl ← (Σⱼ |Dⱼ|) / N
  POUR CHAQUE terme t de Q FAIRE
      n(t) ← nombre de documents qui contiennent t
      IDF(t) ← ln(1 + (N − n(t) + 0,5) / (n(t) + 0,5))
  FIN POUR
  POUR CHAQUE document D FAIRE
      score(D) ← 0
      POUR CHAQUE terme t de Q FAIRE
          f ← nombre d'occurrences de t dans D
          SI f > 0 ALORS
              score(D) ← score(D) + IDF(t) × f × (k₁ + 1) / (f + k₁ × (1 − b + b × |D| / avgdl))
      FIN POUR
  FIN POUR
  trier par score décroissant (égalités par nom) ; RETOURNER le classement

PRÉTRAITEMENT : texte → normalisation Unicode NFC → table de remplacement (variantes d'alef, ta marbuta…) → mots
```

**Complexité.** Le programme recalcule avgdl et n(t) à chaque appel de `bm25_score`, ce qui coûte O(N) par terme et par document, soit O(N² × |Q|) pour classer tout le corpus : c'est volontaire, pour que chaque fonction se lise seule. Un vrai moteur prépare une fois un index inversé (pour chaque terme, la liste des documents et des fréquences), en O(taille totale du corpus), puis ne parcourt, pour une requête, que les listes des termes de Q : O(somme des n(t) pour t ∈ Q). La mémoire de l'index est proportionnelle au nombre total d'occurrences.

**Du squelette au code.** L'IDF correspond à `idf_bm25` (et à `idf_classique` pour la version qui peut devenir négative), le score à `bm25_score` (et `bm25_score_classique`), la fraction de saturation à `partie_frequence`, le classement à `classer`, et le prétraitement à `normaliser_arabe` puis `tokeniser`.

## Cas d'usage réels aux Émirats

Les volumes et les fréquences ci-dessous sont illustratifs ; les calculs, eux, suivent exactement les formules de la démonstration.

### Secteur public — des requêtes arabes tapées comme on parle

Un service public en ligne, accessible par UAE Pass, publie ses fiches de procédure en arabe et en anglais, et son agent répond aux usagers en combinant une recherche sémantique et un index BM25 sur les titres et les textes des fiches. Les usagers tapent souvent « ضريبه » avec un ه final au lieu du ة, omettent la hamza de « أبوظبي », ou collent un intitulé officiel voyellé et allongé par des tatweel. Sans normalisation, la requête « استرداد ضريبه القيمه المضافه » (remboursement de la TVA) ne retrouve qu'un mot sur quatre dans la bonne fiche, pour un score de 0,98 ; avec la même normalisation appliquée à l'index et à la requête, elle en retrouve quatre, et la fiche obtient 2,39, nettement devant la fiche voisine sur l'enregistrement à la TVA (1,41). L'agent cite alors la bonne procédure et son lien, au lieu de répondre à côté ou de renvoyer l'usager vers le centre d'appels. La règle opérationnelle est stricte : la même fonction de normalisation tourne à l'indexation et à la recherche, sinon les deux côtés ne comparent plus les mêmes formes. Les requêtes journalisées pouvant contenir des données personnelles, l'équipe les masque avant de les conserver, conformément à la PDPL. L'indicateur suivi est la part des requêtes arabes qui ne trouvent aucun terme dans l'index, comparée à la même part pour l'anglais.

### Banque — la Murabaha n'est pas l'Ijara

Une banque de détail de Dubaï propose des financements islamiques, et son assistant doit distinguer des produits proches comme la Murabaha (vente avec marge bénéficiaire convenue) et l'Ijara (location, souvent assortie d'un transfert de propriété en fin de contrat). Dans l'espace des embeddings, les fiches de ces deux produits sont très proches, parce qu'elles partagent tout le vocabulaire du financement immobilier. BM25 tranche par le mot exact : dans une base de 2 000 documents où « murabaha » apparaît dans 40 documents et « prêt » dans 1 200, l'IDF vaut ln(1 + 1 960,5/40,5) ≈ 3,90 pour le premier et ln(1 + 800,5/1 200,5) ≈ 0,51 pour le second, un poids près de huit fois plus grand. Avec l'IDF classique, « prêt » recevrait même un poids négatif, ln(800,5/1 200,5) ≈ −0,41, puisqu'il figure dans plus de la moitié des documents (démonstration, point 3). L'agent remonte donc la fiche Murabaha quand le client écrit « murabaha », sans la confondre avec l'Ijara. Une confusion entre deux contrats aux mécanismes juridiques différents serait une faute d'information, et les produits de finance islamique relèvent de l'avis du comité charia de la banque. L'indicateur suivi est le Recall@5 (étape 25) sur un jeu de questions étiquetées par produit.

### Immobilier — un numéro de lot n'a pas de synonyme

Une agence et un promoteur de Dubaï et d'Abu Dhabi gèrent des dizaines de milliers d'unités, désignées par des codes comme « B-1204 » (tour B, lot 1204) et rattachées à un contrat Ejari ou à un dossier de transfert au DLD. Un embedding ne sait pas que « B-1204 » et « B-1205 » sont deux biens différents : leurs vecteurs sont presque identiques. BM25 les distingue, à une condition qui tient au découpage. Avec `\w+`, « B-1204 » devient deux termes, « b » et « 1204 », et « 1204 », présent dans 300 annonces sur 50 000, n'a qu'un IDF de 5,11, alors qu'un terme entier « b-1204 », présent dans 3 annonces, aurait un IDF de 9,57. L'équipe ajoute donc au découpage une règle qui garde les codes d'unité entiers, et l'agent affiche l'unité exacte, ou dit clairement qu'elle n'existe pas, au lieu de proposer une voisine comme si c'était la même. L'erreur coûterait cher : les frais de transfert du DLD valent 4 % du prix, soit 80 000 AED pour un bien de 2 000 000 AED, et un devis établi sur le mauvais lot fausse tout le dossier. L'indicateur suivi est le taux de réponses exactes sur les requêtes qui contiennent un code d'unité.

### Crypto — un code d'erreur noyé dans les journaux

Une plateforme d'actifs virtuels agréée par la VARA donne à son agent d'astreinte un index BM25 sur ses procédures d'incident et, par commodité, sur ses fichiers de journaux. Quand une alerte cite un code d'erreur, l'agent cherche la procédure qui le traite. Le code apparaît 2 fois dans la procédure, un document de longueur moyenne, et 300 fois dans un journal cinquante fois plus long que la moyenne. La saturation limite les dégâts sans les supprimer : la partie fréquence vaut 1,43 pour la procédure et 2,10 pour le journal, qui ne peut pas dépasser k₁ + 1 = 2,5 (point 5) mais reste devant ; même avec b = 1, le journal obtient encore 2,00. L'équipe en tire la conclusion qui s'impose : on n'indexe pas les journaux avec les procédures, ou l'on filtre par type de document avant de classer. L'agent affiche alors la procédure en tête, avec les termes qui ont déclenché la correspondance, ce qui permet à l'opérateur de vérifier son choix. La VARA attend des plateformes agréées une gestion des incidents documentée (à confirmer avec le règlement en vigueur), et une procédure introuvable allonge chaque incident. L'indicateur suivi est le temps moyen de résolution des incidents.

### RH — « مكافأة نهاية الخدمة » écrit de plusieurs façons

Un cabinet RH présent dans plusieurs émirats met à la disposition des salariés de ses clients un assistant qui répond, en arabe et en anglais, aux questions de fin de contrat. La politique interne est rédigée en arabe soigné, « مكافأة نهاية الخدمة » (indemnité de fin de service), mais les salariés tapent souvent « مكافاه نهايه الخدمه », sans hamza et avec des ه. Sans normalisation, aucun des trois mots ne correspond ; après normalisation, les deux formes deviennent « مكافاه نهايه الخدمه » et BM25 retrouve la bonne section, ce que vérifie le programme. L'agent appelle ensuite un outil de calcul fondé sur le décret-loi fédéral 33/2021 : avec un salaire de base de 10 000 AED et sept ans de service, à raison de 21 jours par an les cinq premières années et de 30 jours au-delà, sur un salaire journalier égal à la base divisée par 30, l'indemnité vaut 55 000 AED. Il rappelle que ce régime concerne le secteur privé, hors ressortissants émiriens, qui relèvent de la GPSSA, et hors DIFC, qui a son propre régime d'épargne, et que le résultat est à confirmer avec le texte en vigueur. Sans normalisation, l'agent répondrait à partir d'une section voisine, par exemple sur les congés, et le calcul partirait d'une mauvaise règle. L'indicateur suivi est la part des questions de fin de service résolues sans escalade vers un gestionnaire RH.

### BTP — une classe de béton ne se devine pas

Un groupe de construction qui mène de grands chantiers à Dubaï contrôle chaque facture de sous-traitant contre le cahier des charges et le bordereau de prix du marché. Les lignes portent des références exactes : classe de béton « C40/50 », nuance d'acier « B500B », numéro d'article du bordereau. Pour un modèle d'embedding, « béton C40/50 » et « béton C30/37 » sont presque la même phrase ; pour BM25, « c40 » est un terme rare, donc à IDF élevé, que la ligne de facture contient ou ne contient pas. L'agent retrouve l'article exact du cahier des charges, compare la classe facturée à la classe prescrite et place la ligne en revue si elles diffèrent, avant de vérifier le montant et la TVA de 5 %. Sans cette correspondance exacte, une livraison de béton d'une classe inférieure pourrait être payée au prix de la classe supérieure, et l'écart ne serait découvert qu'au contrôle de l'ouvrage. Les retenues de garantie prévues au contrat ne se libèrent qu'une fois les non-conformités levées, ce qui impose de les repérer tôt. L'indicateur suivi est le nombre d'écarts de classe détectés avant paiement, rapporté au nombre relevé lors des audits.

## Pièges et limites

- **L'IDF classique devient négatif** pour les termes présents dans plus de la moitié des documents (point 3) ; on utilise la variante ln(1 + …), comme le code.
- **La normalisation doit être identique à l'indexation et à la recherche** : arabe, accents, majuscules. Une normalisation ajoutée d'un seul côté fait chuter les correspondances au lieu de les augmenter.
- **Le découpage décide de tout** : un code coupé en morceaux perd sa rareté, un article ال non retiré dédouble les termes.
- **Les statistiques vivent avec la collection** : N, n(t) et avgdl changent à chaque ajout de documents, et un score calculé hier n'est pas comparable à un score calculé aujourd'hui sur une autre collection.
- **Un terme répété dans la requête compte deux fois** dans la fonction canonique, qui parcourt la liste `requete` ; on déduplique la requête si l'on ne veut pas ce comportement.

### Exercice feuille blanche

1. Sans regarder le code, écrire `bm25_score` à partir de l'équation complète, puis vérifier que D1 vaut 1,4145 sur le corpus du point 2.
2. Prédire, puis vérifier avec `partie_frequence` : pour k₁ = 1,5 et f = 3 dans un document de longueur moyenne ; puis pour f = 1 dans un document deux fois plus long que la moyenne, avec b = 0 et avec b = 1. (Réponses : 7,5/4,5 = 1,6667 ; 1, puisque b = 0 ignore la longueur ; 2,5/(1 + 3) = 0,625.)
3. Trouver le bug : `... / (f + k1 * (1 - b + b * avgdl / len(doc)))`. Quels documents cette version avantage-t-elle, et pourquoi ?

## Pour aller plus loin

BM25F pondère différemment les champs d'un document (un titre compte plus que le corps). BM25+ ajoute une petite constante à la partie fréquence pour que les très longs documents ne soient pas écrasés. Lucene, depuis sa version 8, n'inclut plus le facteur (k₁ + 1) au numérateur : il multiplie tous les scores par la même constante et ne change donc pas le classement, exactement comme le changement de base du logarithme au point 3. Enfin, les modèles de recherche « creux appris » prédisent eux-mêmes un poids par terme, mais gardent la structure d'un index inversé, et donc l'explicabilité de BM25.

> Suite : [Score hybride](<23-RAG-Formule-Score-Hybride.md>) — étape 23.
