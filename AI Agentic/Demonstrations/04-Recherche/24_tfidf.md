# 24 — TF-IDF : démonstrations

> Fiche : [24 — TF-IDF](<../../Images/04-Recherche/24_tfidf.md>) · Image : `24_tfidf.jpg` · Leçon : [Étape 22 — BM25](<../../05-RAG/22-RAG-Formule-BM25.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4. Le logarithme est le logarithme naturel ln.

## La formule

$$
\operatorname{TF\text{-}IDF}(t, d) = \operatorname{TF}(t, d) \times \log\left( \frac{N}{\operatorname{DF}(t)} \right)
$$

TF(t, d) compte le terme t dans le document d, DF(t) le nombre de documents qui le contiennent, N le nombre de documents. Le poids est grand pour un terme fréquent dans le document mais rare dans le corpus.

Pour comparer une requête à un document, on range les poids de tous les termes dans un vecteur, puis on calcule le cosinus des deux vecteurs (fichier 03). La leçon liée, l'étape 22, présente BM25, qui garde l'idée « fréquent ici, rare ailleurs » mais remplace le TF brut par une fréquence qui sature et l'IDF par une variante toujours positive (fichier 11).

## Les symboles, un par un

$$
t
$$

Un terme du vocabulaire, une chaîne comme « facture » ; variable `t`.

$$
d
$$

Un document, représenté par le comptage de ses termes, un dictionnaire terme → nombre (argument `tf` de `vectoriser`).

$$
\operatorname{TF}(t, d)
$$

Le nombre d'occurrences de t dans d, entier ≥ 0 ; c'est la valeur `c` associée à `t` dans ce dictionnaire.

$$
N
$$

Le nombre de documents du corpus, entier ≥ 1 ; argument `N` de `poids_idf`.

$$
\operatorname{DF}(t)
$$

Le nombre de documents qui contiennent t au moins une fois, entier de 1 à N pour un terme du corpus ; argument `df_t` de `poids_idf`, et `Counter` `df` dans le cas 1. On compte des documents, pas des occurrences.

$$
\operatorname{IDF}(t)
$$

Le poids de rareté, IDF(t) = ln(N/DF(t)), réel dans [0 ; ln N] ; fonction `poids_idf(N, df_t)`. Un DF nul ou supérieur à N est une entrée invalide et lève `ValueError`.

$$
\operatorname{TF\text{-}IDF}(t, d)
$$

Le poids du terme t dans le document d, réel ≥ 0 ; une coordonnée du vecteur renvoyé par `vectoriser(tf, idfs)`.

$$
\vec{q}, \ \vec{d}
$$

Les vecteurs TF-IDF de la requête et du document, un poids par terme ; dictionnaires creux (seuls les termes présents ont une clé).

$$
\lVert \vec{d} \rVert
$$

La norme euclidienne du vecteur, √(somme des carrés des poids), réel ≥ 0 ; fonction `norme(v)`.

$$
\cos(\vec{q}, \vec{d})
$$

Le cosinus entre requête et document, réel dans [0 ; 1] puisque tous les poids sont positifs ; fonction `cosinus(a, b)`, qui renvoie `None` quand un des deux vecteurs est nul.

$$
w
$$

Dans la démonstration 6, le poids TF-IDF d'un terme du document absent de la requête ; réel > 0.

## Le mécanisme, avant les preuves

TF-IDF reçoit deux comptages : combien de fois le terme apparaît dans le document (TF), et dans combien de documents du corpus il apparaît (DF), rapporté au nombre total N. La division N/DF transforme la fréquence documentaire en rapport de rareté : il vaut 1 pour un terme présent partout et N pour un terme présent une seule fois. Le logarithme comprime ce rapport, qui peut aller de 1 à des millions, en un poids compris entre 0 et ln N ; il a aussi un sens précis, puisque ln(N/DF) = −ln P(t ∈ d), l'information apportée par le fait de trouver t dans un document tiré au hasard (démonstration 2). Le produit TF × IDF combine les deux signaux de façon multiplicative : un terme n'a de poids que s'il est à la fois présent dans le document et rare dans le corpus, et si l'un des deux facteurs est nul, le poids est nul. Un produit plutôt qu'une somme, parce qu'une somme donnerait du poids à un mot vide répété (TF grand, IDF nul) ou à un mot rare absent (TF nul, IDF grand). Le poids est linéaire en TF : dix occurrences pèsent dix fois une seule, ce que BM25 corrige par la saturation (démonstration 4). Pour comparer une requête à un document, on calcule le cosinus de leurs vecteurs de poids : le produit scalaire additionne les poids des termes communs, et la division par les normes neutralise la longueur des textes. Cette division a un revers : tout terme du document absent de la requête grossit la norme du document sans rien ajouter au produit scalaire, donc fait baisser le cosinus, d'autant plus que ce terme est rare (démonstration 6). Le classement final ne dépend ni de la base du logarithme ni de l'unité des poids, seulement de leurs rapports (démonstration 3).

Petit film chiffré, pour N = 1 000 documents :

| Terme | TF | DF | N/DF | ln(N/DF) | TF × IDF |
|---|---|---|---|---|---|
| « splendide » | 3 | 10 | 100 | 4,60517 | 13,81551 |
| un terme courant | 3 | 500 | 2 | 0,69315 | 2,07944 |
| « le » | 5 | 1 000 | 1 | 0 | 0 |

À fréquence égale (TF = 3), le terme présent dans 10 documents pèse 6,6 fois plus que celui présent dans 500 ; le mot vide, même répété 5 fois, ne pèse rien.

## Démonstration 1 — Un mot présent partout ne pèse rien

**Ce qu'on démontre.** Pour tout terme du corpus (1 ≤ DF(t) ≤ N), l'IDF est encadré, nul exactement pour un terme présent partout et maximal pour un terme présent une seule fois :

$$
0 \le \ln\frac{N}{\operatorname{DF}(t)} \le \ln N, \qquad \operatorname{DF}(t) = N \iff \operatorname{IDF}(t) = 0
$$

**L'idée.** Le rapport N/DF est au moins 1, puisqu'on ne peut pas trouver un terme dans plus de documents qu'il n'y en a, et au plus N, puisqu'un terme du corpus est au moins dans un document. Le logarithme, croissant, transporte cet encadrement.

**La preuve, pas à pas.**

**Étape 1.** On encadre DF, parce qu'un terme du corpus figure dans au moins un document et au plus dans tous :

$$
1 \le \operatorname{DF}(t) \le N \quad\Longrightarrow\quad 1 \le \frac{N}{\operatorname{DF}(t)} \le N
$$

**Étape 2.** On applique ln, parce que ln est strictement croissante sur ]0 ; +∞[ et vaut 0 en 1 :

$$
0 = \ln 1 \le \ln\frac{N}{\operatorname{DF}(t)} \le \ln N
$$

**Étape 3.** Le cas d'égalité à gauche : ln x = 0 si et seulement si x = 1, c'est-à-dire N/DF = 1, soit DF = N. ∎

**Vérification chiffrée.** Pour N = 1 000 : un terme présent une fois reçoit ln 1 000 ≈ 6,90776 ; « le », présent dans les 1 000 documents, reçoit ln 1 = 0. Le programme vérifie l'encadrement pour DF de 1 à 1 000. Contre-exemple quand l'hypothèse 1 ≤ DF manque : un terme de la requête absent du corpus (DF = 0) donnerait N/0, une division par zéro ; la fonction `poids_idf` refuse ce cas par `ValueError`, et la vectorisation ignore les termes inconnus du corpus.

**Ce que la preuve révèle du mécanisme.** L'IDF est un filtre automatique des mots vides : aucune liste de mots à exclure n'est nécessaire, le corpus lui-même dit quels mots ne discriminent rien. La borne ln N croît très lentement avec la taille du corpus : passer de 1 000 à 1 000 000 de documents ne fait que doubler le poids maximal.

**Conséquence pour un agent.** Un agent qui indexe un corpus bilingue n'a pas besoin de deux listes de mots vides : « le », « de » et « في » (dans) reçoivent un IDF proche de 0 dès qu'ils sont presque partout (cas 3 : ln(500/490) ≈ 0,02020). En revanche, l'IDF d'un mot inconnu du corpus n'existe pas : la requête doit ignorer ce terme ou passer à une recherche sémantique, pas inventer un poids.

## Démonstration 2 — L'IDF est une mesure de surprise

**Ce qu'on démontre.** En tirant un document au hasard dans le corpus, l'IDF est l'information (fichier 21) de l'événement « le document contient t » ; diviser DF par 2 ajoute exactement ln 2 au poids ; pour deux termes indépendants, l'IDF de leur présence conjointe est la somme des deux IDF :

$$
\ln \frac{N}{\operatorname{DF}(t)} = -\ln P(t \in d), \qquad P(t_1 \wedge t_2) = P(t_1)\,P(t_2) \;\Longrightarrow\; -\ln P(t_1 \wedge t_2) = \operatorname{IDF}(t_1) + \operatorname{IDF}(t_2)
$$

**L'idée.** La probabilité de tomber sur un document qui contient t est DF/N ; un événement rare est surprenant, et la surprise se mesure par l'opposé du logarithme de la probabilité. Le logarithme transforme les produits de probabilités en sommes d'informations.

**La preuve, pas à pas.**

**Étape 1.** Sous un tirage uniforme parmi N documents, la probabilité d'un événement est le nombre de cas favorables divisé par N :

$$
P(t \in d) = \frac{\operatorname{DF}(t)}{N}
$$

**Étape 2.** On prend −ln de cette probabilité, parce que −ln(a/b) = ln(b/a) :

$$
-\ln P(t \in d) = -\ln\frac{\operatorname{DF}(t)}{N} = \ln\frac{N}{\operatorname{DF}(t)}
$$

**Étape 3.** Diviser DF par 2 multiplie N/DF par 2, et ln(2x) = ln 2 + ln x :

$$
\ln\frac{N}{\operatorname{DF}/2} = \ln 2 + \ln\frac{N}{\operatorname{DF}}
$$

**Étape 4.** Pour deux termes indépendants, la probabilité conjointe est le produit, et −ln(ab) = −ln a − ln b, d'où la somme des IDF. ∎

**Vérification chiffrée.** Pour DF = 10 sur N = 1 000, P = 0,01 et −ln 0,01 ≈ 4,60517 = ln 100. Passer de DF = 10 à DF = 5 ajoute ln 200 − ln 100 ≈ 0,69315 = ln 2. Pour deux termes indépendants de probabilités 0,1 et 0,05, la présence conjointe a la probabilité 0,005 et l'information −ln 0,005 ≈ 5,29832 = 2,30259 + 2,99573. Contre-exemple quand l'indépendance manque : « Dubai » et « Marina » apparaissent presque toujours ensemble dans un corpus immobilier, si bien que leur présence conjointe est à peine plus rare que celle de « Marina » seul ; additionner leurs deux IDF compte deux fois la même information.

**Ce que la preuve révèle du mécanisme.** Un vecteur TF-IDF additionne des informations terme par terme, comme si les termes étaient indépendants. C'est faux pour les expressions figées et les noms composés, qui sont donc surpondérés ; c'est le prix de la simplicité.

**Conséquence pour un agent.** Pour les noms composés fréquents (« Dubai Marina », « Abu Dhabi », « fin de service »), on peut indexer l'expression comme un seul terme, ce qui supprime le double comptage. L'interprétation en surprise permet aussi de fixer un seuil lisible : un terme dont l'IDF est inférieur à 0,1 apparaît dans plus de 90 % des documents (e⁻⁰ᐧ¹ ≈ 0,905).

## Démonstration 3 — Changer de base de logarithme ne change pas le classement

**Ce qu'on démontre.** Pour toute base B > 1, les poids en base B sont les poids en base e multipliés par la constante 1/ln B ; les scores de somme sont multipliés par cette constante, et les cosinus restent identiques :

$$
\log_B x = \frac{\ln x}{\ln B}, \qquad \cos\!\left(\frac{\vec{q}}{\ln B}, \frac{\vec{d}}{\ln B}\right) = \cos(\vec{q}, \vec{d})
$$

**L'idée.** Changer de base, c'est changer d'unité de mesure, comme passer des mètres aux pieds : toutes les longueurs sont multipliées par le même nombre, et l'ordre des objets ne bouge pas. Le cosinus ne regarde que la direction des vecteurs, pas leur longueur.

**La preuve, pas à pas.**

**Étape 1.** Par définition du logarithme en base B, B^(log_B x) = x ; en prenant ln des deux membres, log_B x × ln B = ln x, d'où la formule de changement de base.

**Étape 2.** Chaque poids TF × log_B(N/DF) vaut donc (TF × ln(N/DF))/ln B : tous les poids sont multipliés par c = 1/ln B > 0.

**Étape 3.** Une somme de poids est multipliée par c, ce qui ne change pas l'ordre des documents, parce que c > 0. Pour le cosinus, le produit scalaire est multiplié par c² et chaque norme par c :

$$
\frac{c^2\, \vec{q} \cdot \vec{d}}{c\,\lVert \vec{q} \rVert \times c\,\lVert \vec{d} \rVert} = \frac{\vec{q} \cdot \vec{d}}{\lVert \vec{q} \rVert\,\lVert \vec{d} \rVert}
$$

∎

**Vérification chiffrée.** En base 10, c = 1/ln 10 ≈ 0,43429 : le poids ln 100 ≈ 4,60517 devient log₁₀ 100 = 2. Sur les quatre tickets du cas 1, le programme recalcule les cosinus en base 10 : ils sont égaux, à l'arrondi machine près, à ceux de la base e, et le classement est le même. Contre-exemple si la constante n'est pas la même pour tous les poids : mélanger des IDF en base 10 pour certains termes et en base e pour d'autres change les rapports entre poids, donc les cosinus.

**Ce que la preuve révèle du mécanisme.** Seuls les rapports entre poids comptent. La base du logarithme est une convention sans effet ; ce qui a un effet, c'est la forme de la fonction (logarithme plutôt que racine ou rapport brut) et le choix de ce que l'on compte.

**Conséquence pour un agent.** Deux bibliothèques qui n'utilisent pas la même base donnent des scores différents mais le même classement : on peut comparer leurs classements, jamais leurs scores bruts. Un seuil posé sur un score de somme doit être recalculé si l'on change de bibliothèque ; un seuil posé sur un cosinus, non.

## Démonstration 4 — Pourquoi BM25 remplace le TF brut

**Ce qu'on démontre.** Le poids TF-IDF est linéaire en TF, sans plafond ; en revanche, multiplier tous les comptages d'un document par le même facteur ne change pas son cosinus :

$$
\operatorname{TF\text{-}IDF}(t, d) = \operatorname{TF}(t, d) \times \operatorname{IDF}(t), \qquad \cos(\vec{q}, \lambda \vec{d}) = \cos(\vec{q}, \vec{d}) \quad (\lambda > 0)
$$

**L'idée.** Répéter un mot dix fois multiplie son poids par dix ; si ce mot est dans la requête, le document s'en rapproche sans limite, ce qui ouvre la porte au bourrage de mots-clés. Copier le document entier deux fois ne change rien au cosinus, qui ne voit que les proportions.

**La preuve, pas à pas.**

**Étape 1.** IDF(t) ne dépend pas du document, donc le poids est le produit de TF par une constante : il est linéaire en TF, et tend vers l'infini avec TF dès que IDF > 0.

**Étape 2.** Si l'on multiplie tous les comptages par λ > 0, chaque poids est multiplié par λ, parce que le poids est linéaire en TF ; le vecteur devient λ d.

**Étape 3.** Le produit scalaire et la norme du document sont alors multipliés par λ, qui se simplifie :

$$
\cos(\vec{q}, \lambda\vec{d}) = \frac{\lambda\, \vec{q} \cdot \vec{d}}{\lVert \vec{q} \rVert \, \lambda \lVert \vec{d} \rVert} = \cos(\vec{q}, \vec{d})
$$

∎

**Vérification chiffrée.** Le ticket d₁ = « remboursement facture retard » a un cosinus de 0,28160 avec la requête « remboursement facture » ; doublé (« remboursement remboursement facture facture retard retard »), il garde 0,28160. Mais si l'on répète seulement « remboursement », le cosinus passe à 0,39932 pour 2 occurrences et à 0,69788 pour 10 : répéter un mot de la requête rapproche le document, sans saturation. Contre-exemple quand l'hypothèse « même facteur pour tous les termes » manque : c'est justement ce dernier calcul, où un seul comptage est multiplié.

**Ce que la preuve révèle du mécanisme.** La normalisation par le cosinus protège contre les documents simplement plus longs, pas contre la répétition ciblée d'un terme. BM25 (fichier 11) traite les deux problèmes séparément : une saturation en f, bornée par k₁ + 1, et une correction explicite de la longueur.

**Conséquence pour un agent.** Pour des textes écrits par des tiers (annonces, avis, documents fournis par des clients), on préfère BM25 ou un TF sous-linéaire comme 1 + ln TF ; le TF-IDF brut reste un bon outil pour des textes courts et homogènes, comme des tickets ou des titres, et c'est la base du raisonnement « fréquent ici, rare ailleurs ».

## Démonstration 5 — Sensibilité : 10 % de documents en plus coûtent ln 1,1 au poids

**Ce qu'on démontre.** Si DF(t) est multiplié par un facteur α > 0 (à N fixé et tant que α DF ≤ N), l'IDF perd exactement ln α, quelle que soit la rareté du terme ; la perte relative vaut donc ln α/IDF, plus forte pour les termes courants :

$$
\ln\frac{N}{\alpha\,\operatorname{DF}} = \ln\frac{N}{\operatorname{DF}} - \ln \alpha, \qquad \frac{\Delta \operatorname{IDF}}{\operatorname{IDF}} = -\frac{\ln \alpha}{\operatorname{IDF}}
$$

**L'idée.** Le logarithme transforme les facteurs en écarts constants : une variation relative de DF devient une variation absolue de l'IDF, la même pour tous les termes. Rapportée à un petit IDF, cette même variation absolue est une grosse variation relative.

**La preuve, pas à pas.**

**Étape 1.** On écrit le nouveau rapport, parce que N/(α DF) = (N/DF) × (1/α) :

$$
\ln\frac{N}{\alpha\,\operatorname{DF}} = \ln\frac{N}{\operatorname{DF}} + \ln\frac{1}{\alpha} = \ln\frac{N}{\operatorname{DF}} - \ln \alpha
$$

**Étape 2.** La variation relative est la variation absolue −ln α divisée par l'IDF de départ, qui est positif dès que DF < N. ∎

**Vérification chiffrée.** Pour α = 1,1 (10 % de documents en plus contiennent le terme), la perte vaut ln 1,1 ≈ 0,09531. Pour « splendide » (DF = 10 sur 1 000, IDF ≈ 4,60517), c'est −2,07 % ; pour un terme présent dans la moitié des documents (IDF ≈ 0,69315), c'est −13,75 %. Le passage de DF = 1 à DF = 2 (α = 2) coûte ln 2 ≈ 0,69315 partout : sur un corpus de N = 4 documents, le poids passe de 1,38629 à 0,69315, il est divisé par 2 ; sur N = 1 000, il passe de 6,90776 à 6,21461, une baisse de 10 % seulement. Contre-exemple quand l'hypothèse α DF ≤ N manque : on ne peut pas trouver un terme dans plus de documents qu'il n'y en a, et la formule donnerait un IDF négatif, hors de la démonstration 1.

**Ce que la preuve révèle du mécanisme.** Les termes rares sont stables : quelques documents de plus ne changent presque pas leur poids relatif. Les petits corpus sont instables : un seul document ajouté qui contient un terme rare peut diviser son poids par deux, ce que dit la fiche (« un corpus trop petit rend DF instable »).

**Conséquence pour un agent.** Sur un petit corpus, comme les tickets d'une semaine ou une base de quelques dizaines de fiches, on calcule les DF sur un corpus de référence plus large et stable, puis on les fige. On recalcule les DF à intervalle fixe, pas à chaque ajout, pour que les scores d'aujourd'hui restent comparables à ceux d'hier.

## Démonstration 6 — Un terme rare hors de la requête éloigne le document

**Ce qu'on démontre.** Si l'on ajoute à un document un terme absent de la requête, de poids w > 0, le cosinus est multiplié par un facteur strictement inférieur à 1, qui diminue quand w augmente :

$$
\cos(\vec{q}, \vec{d}\,') = \cos(\vec{q}, \vec{d}) \times \frac{\lVert \vec{d} \rVert}{\sqrt{\lVert \vec{d} \rVert^2 + w^2}}
$$

**L'idée.** Le nouveau terme n'a pas de coordonnée dans la requête : il ne change pas le produit scalaire, mais il allonge le vecteur du document. Plus il est rare, plus son poids est grand et plus il allonge le vecteur.

**La preuve, pas à pas.**

**Étape 1.** Le produit scalaire est inchangé, parce que la coordonnée du nouveau terme dans la requête est nulle :

$$
\vec{q} \cdot \vec{d}\,' = \vec{q} \cdot \vec{d} + 0 \times w = \vec{q} \cdot \vec{d}
$$

**Étape 2.** La norme au carré gagne w², parce que le nouveau terme ajoute une coordonnée orthogonale aux autres :

$$
\lVert \vec{d}\,' \rVert^2 = \lVert \vec{d} \rVert^2 + w^2
$$

**Étape 3.** On divise : le cosinus de d′ est celui de d multiplié par ‖d‖/√(‖d‖² + w²), qui est < 1 parce que w² > 0, et décroît quand w augmente. ∎

**Vérification chiffrée.** Le document d₀ = « remboursement facture » a le cosinus 1 avec la requête, et ‖d₀‖ = √(2 × 0,28768²) ≈ 0,40684, soit ‖d₀‖² ≈ 0,16552. Ajouter « retard », de poids w = ln 4 ≈ 1,38629 (w² ≈ 1,92181), donne le facteur 0,40684/√(0,16552 + 1,92181) = 0,40684/1,44476 ≈ 0,28160 : c'est exactement le cosinus du ticket d₁ du cas 1. Contre-exemple quand l'hypothèse « terme absent de la requête » manque : si le terme ajouté est dans la requête, le produit scalaire augmente aussi, et le cosinus peut monter (démonstration 4).

**Ce que la preuve révèle du mécanisme.** Le cosinus TF-IDF récompense les documents qui ne parlent que de la requête et pénalise ceux qui parlent aussi d'autre chose, surtout si cet « autre chose » est rare. Un mot rare hors sujet pèse beaucoup, ce qui est une limite réelle : le ticket d₁, qui parle peut-être d'un remboursement en retard, est écrasé par un ticket plus pauvre.

**Conséquence pour un agent.** Pour des documents longs qui traitent plusieurs sujets, le cosinus TF-IDF sous-estime leur pertinence ; on découpe les documents en passages courts avant de calculer les cosinus, ou l'on combine avec un moteur sémantique par RRF (fichier 25).

## Exemple simple, à la main

Corpus de 1 000 documents. « splendide » apparaît 3 fois dans le document et dans 10 documents du corpus. « le » apparaît dans les 1 000.

**Étape 1.** Le rapport de rareté de « splendide » vaut 1 000/10 = 100, et ln 100 ≈ 4,60517.

**Étape 2.** On multiplie par TF = 3 :

$$
\operatorname{TF\text{-}IDF}(\text{splendide}) = 3 \times \ln\frac{1\,000}{10} = 3 \times \ln 100 \approx 3 \times 4{,}60517 \approx 13{,}81551
$$

**Étape 3.** Pour « le », le rapport vaut 1 000/1 000 = 1, et ln 1 = 0, quel que soit TF :

$$
\operatorname{TF\text{-}IDF}(\text{le}) = \operatorname{TF} \times \ln 1 = 0
$$

## Cas d'usage complexes, démontrés

### Cas 1 — [ASSUR] : retrouver le bon ticket de remboursement

**Contexte.** Un assureur auto et santé fait traiter ses demandes de remboursement de frais par un agent qui cherche, dans les tickets déjà résolus, le plus proche de la nouvelle demande, pour proposer au gestionnaire la même résolution. La nouvelle demande se résume à « remboursement facture ». L'agent compare la requête à quatre tickets résolus par cosinus TF-IDF. Le service reçoit 1 200 tickets par mois ; ce volume et les durées du cas sont illustratifs.

**Données.**

- d₁ : « remboursement facture retard » ;
- d₂ : « facture TVA montant » ;
- d₃ : « remboursement délai banque » ;
- d₄ : « facture facture remboursement ».
- N = 4 ; requête q = « remboursement facture » ; seuil de reprise automatique d'une résolution : cosinus ≥ 0,8 (illustratif).
- Un ticket mal orienté coûte 20 minutes de gestionnaire ; 5 % des tickets seraient mal orientés sans le seuil (illustratif).

**Calcul pas à pas.**

**Étape 1, les DF et les IDF.** « remboursement » et « facture » apparaissent chacun dans 3 tickets, tous les autres mots dans un seul :

$$
a = \ln\frac{4}{3} \approx 0{,}28768, \qquad w = \ln 4 \approx 1{,}38629
$$

**Étape 2, les vecteurs et les normes.** q = (remboursement a, facture a), donc ‖q‖ = a√2 ≈ 0,40684. d₁ = (a, a, retard w), ‖d₁‖ = √(2a² + w²) ≈ 1,44476. d₂ = (facture a, TVA w, montant w), ‖d₂‖ = √(a² + 2w²) ≈ 1,98151, et d₃ a la même structure. d₄ = (facture 2a, remboursement a), ‖d₄‖ = a√5 ≈ 0,64328.

**Étape 3, les produits scalaires.** q · d₁ = a² + a² ≈ 0,16552 ; q · d₂ = a² ≈ 0,08276 ; q · d₄ = 2a² + a² = 3a² ≈ 0,24828.

**Étape 4, les cosinus :**

$$
\cos(q, d_1) = \frac{0{,}16552}{0{,}40684 \times 1{,}44476} \approx 0{,}28160, \qquad \cos(q, d_2) = \cos(q, d_3) = \frac{0{,}08276}{0{,}40684 \times 1{,}98151} \approx 0{,}10266
$$

$$
\cos(q, d_4) = \frac{3a^2}{a\sqrt{2} \times a\sqrt{5}} = \frac{3}{\sqrt{10}} \approx 0{,}94868
$$

**Décision de l'agent.** Seul d₄ dépasse le seuil de 0,8 : l'agent propose au gestionnaire la résolution de d₄, avec le ticket en référence. d₄ gagne largement parce qu'il ne contient que les mots de la requête. Le compromis : d₁, qui parle peut-être d'un remboursement en retard, est écarté parce que le mot rare « retard » l'éloigne de la requête (démonstration 6) ; si la nouvelle demande mentionnait un retard, d₁ serait le bon modèle, et l'agent ne le verrait pas.

**Contre-calcul.** Sans IDF, avec des vecteurs de comptages bruts, d₁ = (1, 1, 1) et q = (1, 1) donnent 2/(√2 × √3) ≈ 0,81650, d₄ = (2, 1) donne 3/(√2 × √5) ≈ 0,94868, et d₂, d₃ donnent 1/(√2 × √3) ≈ 0,40825. Deux tickets dépassent alors le seuil, avec deux résolutions différentes, et l'agent n'a plus de choix net. À 5 % de tickets mal orientés sur 1 200 par mois et 20 minutes par erreur, cela représente 1 200 × 0,05 × 20 = 1 200 minutes, soit 20 heures de gestionnaire par mois.

**Sensibilité.** La décision dépend du poids de « retard ». Le cosinus de d₁ vaut √2 a/√(2a² + w²) ; il atteint le seuil 0,8 quand w² = 2a²(1/0,64 − 1) = 1,125 a², soit w ≈ 0,30513. La valeur de bascule est donc IDF(retard) ≤ 0,30513, c'est-à-dire DF(retard) ≥ 4/e⁰ᐧ³⁰⁵¹³ ≈ 2,948 : si « retard » figurait dans 3 tickets sur 4, d₁ passerait le seuil (exercice 6).

**En production.** L'indicateur suivi est le taux de tickets rouverts après une résolution proposée par l'agent, avec une alerte au-dessus de 5 % (illustratif). L'assurance est supervisée par la CBUAE, et une décision de remboursement doit pouvoir être justifiée ; les tickets contiennent des données personnelles, que l'on masque avant l'indexation, conformément à la PDPL hors DIFC et ADGM, qui ont leurs propres lois de protection des données.

### Cas 2 — [RH] : quelle section de politique transmettre à l'outil de calcul

**Contexte.** Un cabinet RH présent dans plusieurs émirats met à la disposition des salariés de ses clients un assistant qui répond aux questions de fin de contrat. Un salarié demande : « indemnité fin service démission ». L'agent cherche parmi 200 sections de politique interne celle qui traite la question, puis appelle un outil de calcul de l'indemnité de fin de service. Le corpus et ses comptages sont illustratifs.

**Données.**

- N = 200 sections ; DF : indemnité 40, fin 120, service 150, démission 8, calcul 50, salaire 90, congé 30, préavis 25.
- S1, « Indemnité de fin de service » : indemnité 3, fin 4, service 5, démission 1, calcul 2, salaire 2.
- S2, « Congés annuels » : service 9, fin 4, indemnité 1, congé 5, salaire 1.
- S3, « Démission et préavis » : démission 4, fin 1, service 1, préavis 4.
- Salarié du secteur privé : salaire de base 10 000 AED, 7 ans de service, démission.

**Calcul pas à pas.**

**Étape 1, les IDF.** indemnité ln 5 ≈ 1,60944 ; fin ln(200/120) ≈ 0,51083 ; service ln(200/150) ≈ 0,28768 ; démission ln 25 ≈ 3,21888 ; calcul ln 4 ≈ 1,38629 ; salaire ln(200/90) ≈ 0,79851.

**Étape 2, le cosinus de S1.** Le vecteur de S1 vaut (4,82831 ; 2,04330 ; 1,43841 ; 3,21888 ; 2,77259 ; 1,59702) ; celui de la requête (1,60944 ; 0,51083 ; 0,28768 ; 3,21888) :

$$
\cos(q, S_1) = \frac{19{,}58961}{3{,}64625 \times 7{,}08206} \approx 0{,}75861
$$

**Étape 3, les autres sections.** Le même calcul donne cos(q, S2) ≈ 0,11771 et cos(q, S3) ≈ 0,74712. S1 passe devant S3 de 0,01149 seulement.

**Étape 4, l'indemnité.** L'outil applique le décret-loi fédéral 33/2021 : 21 jours par an les 5 premières années, 30 jours au-delà, sur un salaire journalier égal à la base divisée par 30, sans réduction en cas de démission :

$$
\text{jours} = 21 \times 5 + 30 \times 2 = 165, \qquad \text{indemnité} = 165 \times \frac{10\,000}{30} = 55\,000 \ \text{AED}
$$

Le plafond de 24 mois de salaire de base (240 000 AED) n'est pas atteint.

**Décision de l'agent.** L'agent transmet S1 à l'outil et répond 55 000 AED. Comme l'écart avec S3 est inférieur à 0,05 (seuil illustratif), il cite aussi S3 en complément, pour rappeler les règles de préavis, sans en tirer le montant. Le compromis : citer deux sections allonge la réponse, mais évite de cacher au salarié une condition qui le concerne.

**Contre-calcul.** Un comptage brut des mots de la requête donne S1 = 13, S2 = 14, S3 = 6 : la section « Congés annuels » gagnerait, à cause de ses 9 « service ». Une somme de poids TF-IDF sans normalisation donne S1 = 11,52890, S2 = 6,24188, S3 = 13,67401 : la section « Démission et préavis » gagnerait, parce que ses 4 « démission » de poids 3,21888 pèsent linéairement (démonstration 4). Dans les deux cas, l'agent répondrait sur les congés ou sur le préavis, sans le montant de 55 000 AED que le salarié demandait.

**Sensibilité.** La valeur de bascule est le nombre d'occurrences de « démission » dans S3 : avec 4, S3 reste derrière (0,74712 < 0,75861) ; avec 5, S3 passe devant S1. Une simple reformulation de la section S3 suffirait à changer la réponse, ce qui justifie la règle de l'écart minimal.

**En production.** L'indicateur suivi est la part des questions de fin de service résolues sans escalade vers un gestionnaire RH, avec une alerte sous 85 % (illustratif). Le calcul ne vaut que pour le secteur privé : les ressortissants émiriens relèvent de la GPSSA, et le DIFC a son propre régime d'épargne (DEWS) ; le résultat est à confirmer avec le texte en vigueur.

### Cas 3 — [PUBLIC] : une requête arabe tapée avec ه au lieu de ة

**Contexte.** Une entité de services publics en ligne, accessible par UAE Pass, publie 500 fiches en arabe et en anglais. Un usager tape « تجديد رخصه القياده » (renouvellement du permis de conduire), avec un ه final au lieu du ة, comme beaucoup de requêtes saisies au clavier. L'agent affiche en haut de page une carte réponse, la fiche dont le cosinus TF-IDF est le plus haut. Les DF et les comptages sont illustratifs.

**Données.**

- N = 500 fiches. DF bruts : تجديد (renouvellement) 60 ; رخصة (permis, avec ة) 30 ; رخصه (avec ه) 10 ; القيادة (la conduite, avec ة) 25 ; القياده (avec ه) 8 ; فقدان (perte) 15 ; أبوظبي (Abu Dhabi) 120 ; في (dans) 490.
- P1, fiche officielle de renouvellement : تجديد 2, رخصة 3, القيادة 3, أبوظبي 1, في 2.
- P2, ancienne page sur la perte du permis, écrite avec ه : رخصه 1, القياده 1, فقدان 3, في 1.
- Normalisation : ة → ه, appliquée aux documents et à la requête ; les DF fusionnent : رخصه 30 + 10 = 40, القياده 25 + 8 = 33.

**Calcul pas à pas.**

**Étape 1, les IDF bruts.** في reçoit ln(500/490) ≈ 0,02020, presque rien (démonstration 1). La variante rare رخصه reçoit ln 50 ≈ 3,91202, plus que la forme correcte رخصة, ln(500/30) ≈ 2,81341 ; de même القياده reçoit ln(500/8) ≈ 4,13517 contre ln 20 ≈ 2,99573 pour القيادة.

**Étape 2, les cosinus sans normalisation.** La requête ne partage avec P1 que تجديد, et avec P2 les deux mots écrits avec ه :

$$
\cos_{\text{brut}}(q, P_1) \approx 0{,}11285, \qquad \cos_{\text{brut}}(q, P_2) \approx 0{,}44598
$$

**Étape 3, les IDF normalisés.** رخصه : ln(500/40) ≈ 2,52573 ; القياده : ln(500/33) ≈ 2,71810.

**Étape 4, les cosinus après normalisation.** Les trois mots de la requête sont maintenant dans P1 :

$$
\cos_{\text{norm}}(q, P_1) \approx 0{,}98096, \qquad \cos_{\text{norm}}(q, P_2) \approx 0{,}28880
$$

**Décision de l'agent.** L'agent normalise toujours la requête et l'index avec la même fonction, puis affiche P1 en carte réponse, puisque son cosinus dépasse le seuil d'affichage de 0,5 (illustratif). Le compromis : la normalisation fusionne aussi des mots qui ne diffèrent que par la lettre finale et qui n'ont pas le même sens ; sur ce corpus de démarches, le gain l'emporte, mais on vérifie les fusions les plus fréquentes.

**Contre-calcul.** Sans normalisation, la carte réponse montrerait P2, la page sur la perte du permis, avec un cosinus de 0,44598 contre 0,11285 : l'usager qui veut renouveler son permis serait envoyé vers une démarche de déclaration de perte. Le défaut vient des DF : la variante fautive, rare, reçoit un IDF plus élevé que la forme correcte, si bien que la faute de frappe pèse plus que le bon mot.

**Sensibilité.** La valeur de bascule est le nombre de mots tapés avec ه : sans variante, P1 gagne (0,98362 contre 0) ; avec une variante, P1 gagne encore (0,51047 contre 0,23852 si la variante est رخصه) ; avec deux variantes, P2 passe devant (0,44598 contre 0,11285). Une seule lettre de plus dans la requête renverse la carte réponse.

**En production.** L'indicateur suivi est la part des usagers qui trouvent leur démarche dès la carte réponse, mesurée séparément en arabe et en anglais, avec une alerte dès que l'écart entre les deux langues dépasse 0,05 (illustratif). Les requêtes conservées pour l'évaluation sont expurgées de tout numéro d'Emirates ID et de toute donnée personnelle, conformément à la PDPL.

### Cas 4 — [BTP] : apparier une ligne de facture au bordereau de prix

**Contexte.** Un groupe de construction qui mène de grands chantiers à Dubaï contrôle les factures de ses sous-traitants contre le bordereau de prix du marché, qui compte 800 articles. Une ligne de facture porte « béton C40 coulage fondations », 120 m³ facturés à 450 AED/m³. L'agent doit retrouver l'article du bordereau, vérifier le prix unitaire et la TVA, ou renvoyer la ligne en revue humaine. Les DF, les prix et les volumes sont illustratifs.

**Données.**

- N = 800 articles ; DF : béton 120, c40 6, c30 8, coulage 60, fondations 40, pompe 30, dalle 50.
- I1, béton C40 pour fondations, coulé à la pompe, 450 AED/m³ : béton 2, c40 1, fondations 1, coulage 1, pompe 1.
- I2, béton C30 pour fondations, 390 AED/m³ : béton 2, c30 1, fondations 1, coulage 1.
- I3, béton C40 pour dalle, 460 AED/m³ : béton 1, c40 1, dalle 2, coulage 1.
- Règle d'appariement automatique (illustrative) : cosinus ≥ 0,8 et écart ≥ 0,2 avec le deuxième article.

**Calcul pas à pas.**

**Étape 1, les IDF.** c40 : ln(800/6) ≈ 4,89285 ; c30 : ln 100 ≈ 4,60517 ; béton : ln(800/120) ≈ 1,89712 ; coulage ≈ 2,59027 ; fondations ≈ 2,99573 ; pompe ≈ 3,28341 ; dalle ≈ 2,77259.

**Étape 2, les cosinus TF-IDF :**

$$
\cos(q, I_1) \approx 0{,}88471, \qquad \cos(q, I_2) \approx 0{,}48599, \qquad \cos(q, I_3) \approx 0{,}64615
$$

**Étape 3, l'écart.** 0,88471 − 0,64615 = 0,23856 ≥ 0,2.

**Étape 4, le contrôle de la facture.**

$$
120 \times 450 = 54\,000 \ \text{AED HT}, \qquad 0{,}05 \times 54\,000 = 2\,700 \ \text{AED de TVA}, \qquad 56\,700 \ \text{AED TTC}
$$

**Décision de l'agent.** I1 passe les deux conditions : l'agent apparie la ligne à I1, constate que le prix facturé (450 AED/m³) est celui du bordereau et que la TVA vaut 5 % du hors taxe, et valide la ligne. C'est le terme rare « c40 » qui décide : il sépare les deux bétons, alors que tous les autres mots sont communs. Le compromis : I3 partage aussi « c40 » ; l'écart de 0,23856 est suffisant, mais un bordereau où les articles C40 seraient plus nombreux réduirait cet écart (sensibilité).

**Contre-calcul.** Avec des comptages bruts, sans IDF, I1 obtient 0,88388 et I2, le béton C30, 0,75593 : l'écart n'est plus que de 0,12795 et la ligne part en revue humaine, comme toutes les lignes semblables. Pire, si le bordereau ne contenait pas d'article C40 pour fondations (un béton non prévu au marché), les comptages bruts placeraient I2 en tête à 0,75593, assez près du seuil pour qu'un réglage plus souple l'accepte : l'agent comparerait la facture au prix C30 et signalerait à tort un surcoût de 120 × (450 − 390) = 7 200 AED HT. Avec TF-IDF, le meilleur article restant serait I3 à 0,64615, sous le seuil : la ligne part en revue, ce qui est le bon traitement d'un article hors bordereau.

**Sensibilité.** La valeur de bascule est le DF de « c40 » : si 73 articles ou plus du bordereau mentionnent C40, l'IDF de « c40 » baisse assez pour que l'écart entre I1 et le deuxième article tombe sous 0,2, et la règle envoie la ligne en revue. La règle se resserre donc d'elle-même quand le terme décisif devient courant.

**En production.** L'indicateur suivi est la part des lignes appariées automatiquement puis corrigées par le métreur, avec une alerte au-dessus de 1 % (illustratif). Chaque facture validée doit faire apparaître la TVA de 5 % ; les retenues de garantie prévues au contrat se calculent ensuite sur le montant validé.

## Entraînement sur feuille A4

**Exercice 1.** N = 500, un terme est dans 5 documents et 2 fois dans d. Calculer TF-IDF. (ln 100 ≈ 4,605.)

**Exercice 2.** Quel est le poids maximal possible d'un terme présent une fois dans un corpus de N = 1 000 ?

**Exercice 3.** Refaire l'exemple simple avec le logarithme décimal. Le classement change-t-il ?

**Exercice 4.** Montrer qu'un terme présent dans la moitié des documents a un IDF de ln 2.

**Exercice 5.** Pourquoi le ticket d₂ et le ticket d₃ ont-ils exactement le même cosinus avec la requête ?

**Exercice 6 (modifier un cas).** Dans le cas 1, on suppose que le mot « retard » figure dans 3 tickets sur 4 au lieu d'un seul, les autres poids restant ceux du cas. Calculer le nouveau cosinus de d₁ et dire ce que fait l'agent avec son seuil de 0,8.

**Exercice 7 (trouver l'erreur).** Un collègue compte les occurrences de « facture » au lieu des documents : il trouve 4 occurrences (d₁, d₂ et deux fois d₄), écrit IDF(facture) = ln(4/4) = 0, puis obtient cos(q, d₄) = 1,0 et cos(q, d₁) ≈ 0,20319. Trouver l'erreur et donner les bonnes valeurs.

**Exercice 8 (redémontrer de mémoire).** Sans regarder la démonstration 6, montrer qu'ajouter à un document un terme absent de la requête, de poids w > 0, multiplie son cosinus par ‖d‖/√(‖d‖² + w²), et vérifier le résultat sur d₁.

## Corrigé

**Exercice 1.** IDF = ln(500/5) = ln 100 ≈ 4,605 ; TF-IDF = 2 × 4,605 ≈ 9,21.

**Exercice 2.** Le poids maximal correspond à DF = 1 et TF = 1 : 1 × ln(1 000/1) = ln 1 000 ≈ 6,908 (démonstration 1).

**Exercice 3.** 3 × log₁₀ 100 = 3 × 2 = 6. Tous les poids sont divisés par ln 10 (multipliés par 0,43429) : le classement ne change pas (démonstration 3).

**Exercice 4.** DF = N/2 donne N/DF = N/(N/2) = 2, donc IDF = ln 2 ≈ 0,693.

**Exercice 5.** Chacun partage un seul mot de la requête, de même IDF a (« facture » pour d₂, « remboursement » pour d₃), et contient deux mots rares de même poids w. Leurs produits scalaires valent tous deux a², et leurs normes √(a² + 2w²) : leurs cosinus sont égaux, à 0,10266.

**Exercice 6.** Si DF(retard) = 3, IDF(retard) = ln(4/3) = a, et d₁ = (a, a, a). Alors q · d₁ = 2a², ‖q‖ = a√2, ‖d₁‖ = a√3, et cos = 2a²/(a√2 × a√3) = 2/√6 ≈ 0,81650 ≥ 0,8. d₁ passe le seuil avec d₄ : l'agent a deux résolutions candidates et demande au gestionnaire de choisir, ou demande au client s'il s'agit d'un retard. C'est la bascule annoncée (DF ≥ 2,948).

**Exercice 7.** DF compte des documents, pas des occurrences : « facture » est dans d₁, d₂ et d₄, soit DF = 3, et IDF = ln(4/3) ≈ 0,28768, pas 0. Avec l'erreur, la requête se réduit à (remboursement a) et d₄ à (remboursement a), d'où un cosinus de 1,0 trop flatteur, et d₁ obtient a/√(a² + w²) = 0,28768/1,41583 ≈ 0,20319. Les bonnes valeurs sont celles du cas 1 : 0,94868 pour d₄ et 0,28160 pour d₁.

**Exercice 8.** Étape 1 : le terme ajouté a une coordonnée nulle dans la requête, donc q · d′ = q · d + 0 × w = q · d. Étape 2 : il ajoute une coordonnée, donc ‖d′‖² = ‖d‖² + w². Étape 3 : cos(q, d′) = q · d/(‖q‖ √(‖d‖² + w²)) = cos(q, d) × ‖d‖/√(‖d‖² + w²). Vérification : avec d₀ = (a, a), ‖d₀‖ ≈ 0,40684 et w = ln 4, le facteur vaut 0,40684/1,44476 ≈ 0,28160 = cos(q, d₁).

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`poids_idf(N, df_t, base)`** — Cette fonction est le peseur de rareté du programme, un archiviste qui compte dans combien de dossiers apparaît un mot avant de lui donner son poids : elle reçoit la taille du corpus `N`, le nombre `df_t` de documents qui contiennent le terme et une base de logarithme, e par défaut. Elle lève une `ValueError` si N vaut moins de 1 ou si DF sort de l'intervalle de 1 à N, puis renvoie log(N / DF) divisé par le logarithme de la base, soit 4,60517 pour un mot présent dans 10 documents sur 1 000, ln 1 000 ≈ 6,90776 pour un mot unique et exactement 0 pour un mot présent partout.

**`vectoriser(tf, idfs)`** — Celle-ci transforme un texte déjà compté en fiche de poids, comme un commis qui recopie chaque ligne d'inventaire en multipliant la quantité par son prix unitaire : elle reçoit le dictionnaire `tf` des occurrences de chaque terme et le dictionnaire `idfs` des poids de rareté, et construit, pour chaque terme connu du corpus, le produit TF × IDF. Les termes absents de `idfs` sont simplement écartés, et elle renvoie un vecteur creux sous forme de dictionnaire, que les quatre cas et `main` passent ensuite à `cosinus` pour comparer requête et documents.

**`norme(v)`** — Cette petite fonction mesure la longueur d'une flèche tracée dans l'espace des mots, comme un arpenteur qui applique Pythagore à toutes les coordonnées à la fois : elle reçoit un vecteur creux `v`, additionne le carré de chacune de ses valeurs puis prend la racine carrée de cette somme. Elle renvoie ce nombre positif, 0 pour un vecteur vide, et sert au dénominateur du cosinus ainsi qu'aux vérifications de `main`, par exemple la norme 0,40684 du document « remboursement facture » dans la démonstration 6.

**`cosinus(a, b)`** — Voici le juge des ressemblances, qui ne regarde que l'angle entre deux flèches et jamais leur longueur : la fonction reçoit deux vecteurs creux `a` et `b`, calcule leurs normes et renvoie `None` si l'une est nulle, faute de dénominateur. Sinon, elle parcourt les termes de `a`, multiplie chaque poids par celui du même terme dans `b`, ou par 0 s'il y manque, additionne ces produits et divise par le produit des deux normes ; elle renvoie ainsi 0,94868 pour le ticket « facture facture remboursement » face à la requête « remboursement facture », la valeur qui fait gagner ce ticket dans le cas 1.

**`r(x, n)`** — Ce minuscule outil est le greffier qui recopie les nombres au propre avant de les comparer au texte : il reçoit un nombre `x` et un nombre de décimales `n`, arrondit `x` à `n` décimales avec `round`, puis ajoute 0.0, ce qui transforme un éventuel zéro négatif en zéro ordinaire. Il renvoie ce nombre arrondi, et presque tous les `assert` de `main` passent par lui pour confronter les calculs aux valeurs écrites à cinq décimales dans la fiche, comme 0,2816 pour le cosinus du ticket d₁.

**`cas_1_tickets_assur()`** — Cette fonction rejoue la scène d'un gestionnaire d'assurance qui cherche, parmi quatre tickets résolus, celui qui ressemble le plus à la demande « remboursement facture » : sans paramètre, elle découpe les tickets en mots, compte les DF avec un `Counter`, calcule les IDF (environ 0,28768 pour « facture », 1,38629 pour « retard ») et compare la requête à chaque ticket par cosinus TF-IDF, en base e puis en base 10, puis avec les seuls comptages bruts. Elle retient les tickets dont le cosinus atteint 0,8, soit le seul d₄, calcule le poids de bascule de « retard », 0,30513, et le DF correspondant, environ 2,948, imprime deux lignes et renvoie un dictionnaire avec les DF, les IDF, les cosinus, les normes et les produits scalaires.

**`vecteur(m, base)`** — Cette fonction interne vit dans `cas_1_tickets_assur`, où elle sert de traducteur maison : elle reçoit une liste de mots `m` et une base de logarithme, e par défaut, compte les occurrences de chaque mot, puis multiplie chaque compte par l'IDF calculé plus haut dans le cas et divise par le logarithme de la base. Elle renvoie le vecteur creux du texte, et son paramètre `base` permet de refaire tout le classement en base 10 avec `vecteur(q, 10)`, pour vérifier que changer de base ne change aucun cosinus, comme l'annonce la démonstration 3.

**`cas_2_sections_rh()`** — Ici, la fonction joue le documentaliste d'un cabinet RH qui doit choisir, parmi trois sections de politique interne, celle à transmettre à l'outil de calcul de fin de service : sans paramètre, elle part de N = 200 sections et des DF du texte, vectorise la requête « indemnité fin service démission » et les sections S1, S2 et S3, et obtient les cosinus 0,75861, 0,11771 et 0,74712. Elle calcule aussi le comptage brut et la somme TF-IDF non normalisée, qui désigneraient la mauvaise section, cherche qu'à partir de 5 « démission » S3 passerait devant S1, calcule l'indemnité, 21 × 5 + 30 × 2 = 165 jours et 55 000 AED pour 10 000 AED de base et 7 ans, sous le plafond de 24 mois, imprime deux lignes et renvoie un dictionnaire de tous ces résultats.

**`cas_3_permis_public()`** — Cette fonction se met à la place d'un usager qui tape sa demande de renouvellement de permis en arabe avec un ه final au lieu du ة, et d'un guichet en ligne qui doit pourtant lui montrer la bonne fiche : sans paramètre, elle fixe N = 500, les DF bruts et les deux pages P1 et P2, calcule les IDF bruts puis les IDF normalisés, et compare trois requêtes qui contiennent zéro, une ou deux variantes. Sans normalisation, la requête à deux variantes donne 0,11285 pour P1 contre 0,44598 pour P2, la mauvaise page, alors qu'après normalisation P1 l'emporte à 0,98096 contre 0,28880 ; la fonction imprime ces résultats et renvoie un dictionnaire des IDF, des cosinus, des DF fusionnés et des mots arabes utilisés.

**`normaliser(tf)`** — Cette fonction interne, logée dans `cas_3_permis_public`, est le correcteur d'orthographe le plus modeste qui soit : elle reçoit un dictionnaire de comptes `tf`, remplace dans chaque mot le ة (ta marbuta) par ه, et additionne les comptes des mots qui deviennent identiques. Elle renvoie le nouveau dictionnaire, si bien qu'appliquée aux DF elle fusionne رخصة et رخصه en un seul mot de DF 30 + 10 = 40, et appliquée à la requête comme aux pages, elle garantit que tout le monde est écrit de la même manière avant le calcul des cosinus.

**`cas_4_bordereau_btp()`** — Cette fonction joue le métreur d'un groupe de construction qui doit rattacher la ligne de facture « béton C40 coulage fondations » à l'un des articles du bordereau de prix : sans paramètre, elle fixe N = 800, la requête et les trois articles I1, I2 et I3, calcule les cosinus TF-IDF 0,88471, 0,48599 et 0,64615, puis les cosinus sur comptages bruts, et l'écart entre les deux premiers, 0,23856 contre 0,12795 sans IDF. Elle cherche ensuite le DF de « c40 » à partir duquel la règle d'appariement échoue, 73, contrôle la facture, 120 × 450 = 54 000 AED hors taxes et 2 700 AED de TVA à 5 %, imprime deux lignes et renvoie un dictionnaire de tous ces éléments.

**`dfs(df_c40)`** — Cette fonction interne vit dans `cas_4_bordereau_btp` et y tient le registre des fréquences documentaires du bordereau : elle reçoit le seul nombre qu'on veut faire varier, le DF du terme « c40 », et renvoie le dictionnaire complet des DF, où tous les autres termes gardent leurs valeurs fixes, 120 pour « béton », 8 pour « c30 », 60 pour « coulage », 40 pour « fondations », 30 pour « pompe » et 50 pour « dalle ». C'est grâce à elle que le cas peut balayer les DF de « c40 » de 6 à 800 sans réécrire tout le corpus.

**`classer(df_c40)`** — Deuxième fonction interne de `cas_4_bordereau_btp`, elle refait tout le travail d'appariement pour un DF donné du terme « c40 », comme un contrôleur qui relance son tri chaque fois qu'on change une donnée du bordereau : elle reçoit ce DF, demande à `dfs` le dictionnaire complet, calcule les IDF avec `poids_idf` pour N = 800, puis le cosinus entre la requête et chacun des trois articles. Elle renvoie le dictionnaire des trois cosinus, 0,88471, 0,48599 et 0,64615 pour un DF de 6, et c'est elle que le balayage appelle pour trouver la bascule.

**`marge(c)`** — Troisième fonction interne de `cas_4_bordereau_btp`, elle est l'arbitre qui mesure l'avance du vainqueur sur son poursuivant : elle reçoit un dictionnaire de cosinus `c`, trie les valeurs dans l'ordre décroissant et renvoie la différence entre la première et la deuxième. Elle donne 0,23856 avec TF-IDF et 0,12795 avec les comptages bruts, et la règle d'appariement automatique exige que cette marge atteigne 0,2 en plus d'un meilleur cosinus d'au moins 0,8, faute de quoi la ligne de facture part en revue humaine.

**`main()`** — C'est le chef d'orchestre qui fait défiler toute la fiche : il suit d'abord trois termes à travers la formule (13,81551, 2,07944 et 0 pour N = 1 000), vérifie les bornes de l'IDF et le refus des DF 0 et 1 001, l'interprétation par la surprise et l'additivité pour des termes indépendants, l'indifférence à la base, la linéarité en TF et l'invariance du cosinus quand on double tout le document, la sensibilité de l'IDF à DF, avec une perte de ln 1,1 ≈ 0,09531, puis la dilution par un terme hors requête, d'un facteur 0,28160. Il appelle ensuite les quatre cas, confronte chaque nombre renvoyé par un `assert` aux valeurs du texte, recalcule les exercices du corrigé et n'imprime le message final de réussite que si tout concorde.

```python
"""Démonstration 24 — TF-IDF : mots vides, surprise, base, linéarité, sensibilité, dilution, quatre cas aux EAU."""
import math
import sys
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def poids_idf(N: int, df_t: int, base: float = math.e) -> float:
    """IDF(t) = log_base(N / DF(t)) ; DF hors de [1 ; N] : entrée invalide."""
    if N < 1 or not 1 <= df_t <= N:
        raise ValueError("il faut N >= 1 et 1 <= DF(t) <= N")
    return math.log(N / df_t) / math.log(base)


def vectoriser(tf: dict[str, int], idfs: dict[str, float]) -> dict[str, float]:
    """Vecteur TF-IDF creux : TF(t, d) × IDF(t) pour chaque terme connu du corpus."""
    return {t: c * idfs[t] for t, c in tf.items() if t in idfs}


def norme(v: dict[str, float]) -> float:
    return math.sqrt(sum(x * x for x in v.values()))


def cosinus(a: dict[str, float], b: dict[str, float]) -> float | None:
    """Cosinus de deux vecteurs creux ; None si l'un est nul (pas de dénominateur)."""
    na, nb = norme(a), norme(b)
    if na == 0 or nb == 0:
        return None
    return sum(x * b.get(t, 0.0) for t, x in a.items()) / (na * nb)


def r(x: float, n: int) -> float:
    """Arrondi à n décimales, comme dans le texte."""
    return round(x, n) + 0.0


def cas_1_tickets_assur() -> dict:
    """[ASSUR] Retrouver, parmi quatre tickets résolus, celui qui ressemble à « remboursement facture »."""
    tickets = {"d1": "remboursement facture retard", "d2": "facture TVA montant",
               "d3": "remboursement délai banque", "d4": "facture facture remboursement"}
    mots = {k: v.split() for k, v in tickets.items()}
    N = len(tickets)
    df = Counter(t for m in mots.values() for t in set(m))
    idf = {t: poids_idf(N, d) for t, d in df.items()}

    def vecteur(m: list[str], base: float = math.e) -> dict[str, float]:
        return {t: c * idf[t] / math.log(base) for t, c in Counter(m).items() if t in idf}

    q = "remboursement facture".split()
    cos = {k: cosinus(vecteur(q), vecteur(m)) for k, m in mots.items()}
    cos10 = {k: cosinus(vecteur(q, 10), vecteur(m, 10)) for k, m in mots.items()}
    tf_seul = {k: cosinus(dict(Counter(q)), dict(Counter(m))) for k, m in mots.items()}
    a, w = idf["facture"], idf["retard"]
    w_bascule = a * math.sqrt(2 * (1 / 0.8 ** 2 - 1))          # cos(q, d1) = 0.8
    df_bascule = N / math.exp(w_bascule)
    retenus = [k for k, v in cos.items() if v >= 0.8]
    print("Cas 1 — ASSUR : IDF facture {:.5f}, retard {:.5f} ; cosinus ".format(a, w)
          + " ; ".join(f"{k} {v:.5f}" for k, v in cos.items()) + f" ; retenus (>= 0.8) {retenus}")
    print("  TF seul : " + " ; ".join(f"{k} {v:.5f}" for k, v in tf_seul.items())
          + f" ; bascule : IDF(retard) <= {w_bascule:.5f}, soit DF >= {df_bascule:.3f}")
    return {"df": df, "idf": idf, "cos": cos, "cos10": cos10, "tf_seul": tf_seul, "retenus": retenus,
            "w_bascule": w_bascule, "df_bascule": df_bascule,
            "normes": (norme(vecteur(q)), norme(vecteur(mots["d1"])), norme(vecteur(mots["d2"])),
                       norme(vecteur(mots["d4"]))),
            "produits": tuple(sum(x * vecteur(mots[k]).get(t, 0) for t, x in vecteur(q).items()) for k in ("d1", "d2", "d4"))}


def cas_2_sections_rh() -> dict:
    """[RH] Choisir la section de politique RH à transmettre à l'outil de calcul de fin de service."""
    N = 200
    df = {"indemnité": 40, "fin": 120, "service": 150, "démission": 8, "congé": 30, "préavis": 25,
          "calcul": 50, "salaire": 90}
    idfs = {t: poids_idf(N, d) for t, d in df.items()}
    q = {"indemnité": 1, "fin": 1, "service": 1, "démission": 1}
    sections = {"S1": {"indemnité": 3, "fin": 4, "service": 5, "démission": 1, "calcul": 2, "salaire": 2},
                "S2": {"service": 9, "fin": 4, "indemnité": 1, "congé": 5, "salaire": 1},
                "S3": {"démission": 4, "fin": 1, "service": 1, "préavis": 4}}
    vq = vectoriser(q, idfs)
    cos = {k: cosinus(vq, vectoriser(s, idfs)) for k, s in sections.items()}
    comptage = {k: sum(s.get(t, 0) for t in q) for k, s in sections.items()}
    somme = {k: sum(s.get(t, 0) * idfs[t] for t in q) for k, s in sections.items()}
    v1 = vectoriser(sections["S1"], idfs)
    bascule = next(n for n in range(0, 50)
                   if cosinus(vq, vectoriser(dict(sections["S3"], démission=n), idfs)) > cos["S1"])
    base, annees = 10000, 7
    jours = 21 * min(annees, 5) + 30 * max(annees - 5, 0)
    indemnite = min(jours * base / 30, 24 * base)
    print("Cas 2 — RH : IDF " + " ; ".join(f"{t} {idfs[t]:.5f}" for t in q) + " ; cosinus "
          + " ; ".join(f"{k} {v:.5f}" for k, v in cos.items()))
    print(f"  comptage {comptage} ; somme TF-IDF " + " ; ".join(f"{k} {v:.5f}" for k, v in somme.items())
          + f" ; S3 passe devant dès {bascule} « démission » ; indemnité {indemnite:.0f} AED ({jours} jours)")
    return {"idfs": idfs, "cos": cos, "comptage": comptage, "somme": somme, "bascule": bascule,
            "jours": jours, "indemnite": indemnite, "norme_q": norme(vq), "norme_s1": norme(v1),
            "produit_s1": sum(x * v1.get(t, 0) for t, x in vq.items()), "v1": v1}


def cas_3_permis_public() -> dict:
    """[PUBLIC] Requête arabe tapée avec ه au lieu de ة : normaliser avant de compter les DF."""
    N = 500
    tajdid, rukhsa_t, rukhsa_h = "تجديد", "رخصة", "رخصه"            # renouvellement, permis (ة puis ه)
    qiyada_t, qiyada_h, fuqdan, abou_dhabi, fi = "القيادة", "القياده", "فقدان", "أبوظبي", "في"
    df_brut = {tajdid: 60, rukhsa_t: 30, rukhsa_h: 10, qiyada_t: 25, qiyada_h: 8, fuqdan: 15, abou_dhabi: 120, fi: 490}
    p1 = {tajdid: 2, rukhsa_t: 3, qiyada_t: 3, abou_dhabi: 1, fi: 2}   # page officielle de renouvellement
    p2 = {rukhsa_h: 1, qiyada_h: 1, fuqdan: 3, fi: 1}                  # ancienne page sur la perte du permis

    def normaliser(tf: dict[str, int]) -> dict[str, int]:
        sortie: dict[str, int] = {}
        for t, c in tf.items():
            t2 = t.replace(chr(0x0629), chr(0x0647))                    # ة (ta marbuta) → ه
            sortie[t2] = sortie.get(t2, 0) + c
        return sortie

    df_norm = normaliser(df_brut)
    i_brut = {t: poids_idf(N, d) for t, d in df_brut.items()}
    i_norm = {t: poids_idf(N, d) for t, d in df_norm.items()}
    requetes = {0: {tajdid: 1, rukhsa_t: 1, qiyada_t: 1}, 1: {tajdid: 1, rukhsa_h: 1, qiyada_t: 1},
                2: {tajdid: 1, rukhsa_h: 1, qiyada_h: 1}}
    brut = {n: (cosinus(vectoriser(q, i_brut), vectoriser(p1, i_brut)),
                cosinus(vectoriser(q, i_brut), vectoriser(p2, i_brut))) for n, q in requetes.items()}
    qn = normaliser(requetes[2])
    norm = (cosinus(vectoriser(qn, i_norm), vectoriser(normaliser(p1), i_norm)),
            cosinus(vectoriser(qn, i_norm), vectoriser(normaliser(p2), i_norm)))
    print(f"Cas 3 — PUBLIC : IDF في {i_brut[fi]:.5f} ; رخصه {i_brut[rukhsa_h]:.5f} brut, {i_norm[rukhsa_h]:.5f} normalisé ;"
          f" brut P1 {brut[2][0]:.5f} < P2 {brut[2][1]:.5f} ; normalisé P1 {norm[0]:.5f} > P2 {norm[1]:.5f}")
    print("  variantes ه dans la requête : " + " ; ".join(f"{n} → P1 {v[0]:.5f}, P2 {v[1]:.5f}" for n, v in brut.items()))
    return {"i_brut": i_brut, "i_norm": i_norm, "brut": brut, "norm": norm, "df_norm": df_norm,
            "mots": (tajdid, rukhsa_t, rukhsa_h, qiyada_t, qiyada_h, fuqdan, abou_dhabi, fi)}


def cas_4_bordereau_btp() -> dict:
    """[BTP] Apparier une ligne de facture « béton C40 coulage fondations » au bordereau de prix."""
    N = 800

    def dfs(df_c40: int) -> dict[str, int]:
        return {"béton": 120, "c40": df_c40, "c30": 8, "coulage": 60, "fondations": 40, "pompe": 30, "dalle": 50}

    q = {"béton": 1, "c40": 1, "coulage": 1, "fondations": 1}
    items = {"I1": {"béton": 2, "c40": 1, "fondations": 1, "coulage": 1, "pompe": 1},   # C40 fondations, 450 AED/m³
             "I2": {"béton": 2, "c30": 1, "fondations": 1, "coulage": 1},              # C30 fondations, 390 AED/m³
             "I3": {"béton": 1, "c40": 1, "dalle": 2, "coulage": 1}}                    # C40 dalle, 460 AED/m³

    def classer(df_c40: int) -> dict[str, float]:
        idfs = {t: poids_idf(N, d) for t, d in dfs(df_c40).items()}
        return {k: cosinus(vectoriser(q, idfs), vectoriser(v, idfs)) for k, v in items.items()}

    cos = classer(6)
    tf_seul = {k: cosinus(dict(q), dict(v)) for k, v in items.items()}

    def marge(c: dict[str, float]) -> float:
        s = sorted(c.values(), reverse=True)
        return s[0] - s[1]

    df_bascule = next(d for d in range(6, N + 1) if marge(classer(d)) < 0.2 or max(classer(d).values()) < 0.8)
    sans_i1 = {k: v for k, v in cos.items() if k != "I1"}
    ht = 120 * 450
    tva = 0.05 * ht
    print("Cas 4 — BTP : IDF c40 {:.5f}, béton {:.5f} ; cosinus ".format(poids_idf(N, 6), poids_idf(N, 120))
          + " ; ".join(f"{k} {v:.5f}" for k, v in cos.items()) + f" ; marge {marge(cos):.5f}")
    print("  TF seul " + " ; ".join(f"{k} {v:.5f}" for k, v in tf_seul.items())
          + f" ; marge {marge(tf_seul):.5f} ; bascule DF(c40) = {df_bascule} ; facture {ht} + TVA {tva:.0f} = {ht + tva:.0f} AED")
    return {"cos": cos, "tf_seul": tf_seul, "marge": marge(cos), "marge_tf": marge(tf_seul),
            "df_bascule": df_bascule, "ht": ht, "tva": tva, "sans_i1": sans_i1,
            "idfs": {t: poids_idf(N, d) for t, d in dfs(6).items()}}


def main() -> None:
    # Le mécanisme : trois termes suivis à travers la formule (N = 1 000)
    film = [(tf, d, 1000 / d, math.log(1000 / d), tf * math.log(1000 / d)) for tf, d in ((3, 10), (3, 500), (5, 1000))]
    print("Mécanisme : " + " ; ".join(f"TF {tf}, DF {d} → {p:.5f}" for tf, d, _, _, p in film))
    assert [(r(x, 0), r(l, 5), r(p, 5)) for _, _, x, l, p in film] == [(100.0, 4.60517, 13.81551), (2.0, 0.69315, 2.07944), (1.0, 0.0, 0.0)]
    assert r(film[0][4] / film[1][4], 1) == 6.6

    # Démonstration 1 : bornes de l'IDF
    assert r(poids_idf(1000, 1), 5) == 6.90776 and poids_idf(1000, 1000) == 0.0
    assert all(0 <= poids_idf(1000, d) <= math.log(1000) for d in range(1, 1001))
    erreurs = 0
    for d in (0, 1001):
        try:
            poids_idf(1000, d)
        except ValueError:
            erreurs += 1
    assert erreurs == 2
    assert r(math.log(10 ** 6) / math.log(10 ** 3), 10) == 2.0

    # Démonstration 2 : surprise ; diviser DF par 2 ajoute ln 2 ; termes indépendants : les IDF s'additionnent
    print(f"Démo 2 : -ln(0.01) = {-math.log(0.01):.5f} ; DF / 2 → + {poids_idf(1000, 5) - poids_idf(1000, 10):.5f} ;"
          f" indépendants : {-math.log(0.1 * 0.05):.5f} = {-math.log(0.1):.5f} + {-math.log(0.05):.5f}")
    assert r(-math.log(0.01), 5) == 4.60517 and r(poids_idf(1000, 5) - poids_idf(1000, 10), 5) == 0.69315
    assert r(-math.log(0.1 * 0.05), 5) == 5.29832 and [r(-math.log(p), 5) for p in (0.1, 0.05)] == [2.30259, 2.99573]
    assert r(math.exp(-0.1), 3) == 0.905 and r(math.log(200) - math.log(100), 5) == 0.69315
    assert all(math.isclose(poids_idf(1000, d), -math.log(d / 1000), abs_tol=1e-12) for d in range(1, 1001))

    # Démonstration 3 : la base ne change pas le classement (vérifié aussi sur le cas 1)
    print(f"Démo 3 : 1 / ln 10 = {1 / math.log(10):.5f} ; ln 100 = {math.log(100):.5f} → log10 100 = {poids_idf(1000, 10, 10):.0f}")
    assert r(1 / math.log(10), 5) == 0.43429 and r(poids_idf(1000, 10, 10), 10) == 2.0

    # Démonstration 4 : linéarité en TF ; répéter tout le document ne change pas le cosinus
    idf_q = {"remboursement": math.log(4 / 3), "facture": math.log(4 / 3), "retard": math.log(4)}
    q = vectoriser({"remboursement": 1, "facture": 1}, idf_q)
    d1 = {"remboursement": 1, "facture": 1, "retard": 1}
    c_double = cosinus(q, vectoriser({t: 2 * c for t, c in d1.items()}, idf_q))
    c_rep = [cosinus(q, vectoriser(dict(d1, remboursement=k), idf_q)) for k in (1, 2, 10)]
    print(f"Démo 4 : d1 doublé {c_double:.5f} ; « remboursement » ×1, ×2, ×10 → " + ", ".join(f"{v:.5f}" for v in c_rep))
    assert r(c_double, 5) == 0.2816 and [r(v, 5) for v in c_rep] == [0.2816, 0.39932, 0.69788]

    # Démonstration 5 : sensibilité de l'IDF à DF
    perte = math.log(1.1)
    rel = (perte / math.log(100), perte / math.log(2))
    print(f"Démo 5 : +10 % de DF → -{perte:.5f} ; relatif {100 * rel[0]:.2f} % (DF = 10) et {100 * rel[1]:.2f} % (DF = 500) ;"
          f" DF 1 → 2 : N = 4 {math.log(4):.5f} → {math.log(2):.5f}, N = 1000 {math.log(1000):.5f} → {math.log(500):.5f}")
    assert r(perte, 5) == 0.09531 and [r(100 * x, 2) for x in rel] == [2.07, 13.75]
    assert r(poids_idf(1000, 10) - math.log(1000 / 11), 5) == 0.09531
    assert [r(math.log(x), 5) for x in (4, 2, 1000, 500)] == [1.38629, 0.69315, 6.90776, 6.21461]
    assert r(100 * (math.log(1000) - math.log(500)) / math.log(1000), 0) == 10

    # Démonstration 6 : un terme hors requête dilue le cosinus d'un facteur ‖d‖ / √(‖d‖² + w²)
    d0 = vectoriser({"remboursement": 1, "facture": 1}, idf_q)
    w = idf_q["retard"]
    facteur = norme(d0) / math.sqrt(norme(d0) ** 2 + w ** 2)
    print(f"Démo 6 : ‖d0‖ = {norme(d0):.5f} ; facteur {facteur:.5f} ; cos(q, d0) = {cosinus(q, d0):.0f} → {cosinus(q, d0) * facteur:.5f}")
    assert r(norme(d0), 5) == 0.40684 and r(facteur, 5) == 0.2816 and math.isclose(cosinus(q, d0), 1.0)
    assert r(norme(d0) ** 2, 5) == 0.16552 and r(w ** 2, 5) == 1.92181 and r(math.sqrt(0.16552 + 1.92181), 5) == 1.44476
    assert cosinus(q, {}) is None and cosinus({}, {}) is None

    # Exemple simple
    print(f"Exemple simple : splendide {3 * math.log(1000 / 10):.5f} ; le {5 * math.log(1000 / 1000)}")
    assert r(3 * math.log(100), 5) == 13.81551 and math.log(1000 / 1000) == 0

    # Cas 1 — ASSUR
    c1 = cas_1_tickets_assur()
    assert r(c1["idf"]["facture"], 5) == 0.28768 and r(c1["idf"]["retard"], 5) == 1.38629
    assert dict(c1["df"]) == {"remboursement": 3, "facture": 3, "retard": 1, "TVA": 1, "montant": 1, "délai": 1, "banque": 1}
    assert [r(v, 5) for v in c1["cos"].values()] == [0.2816, 0.10266, 0.10266, 0.94868]
    assert sorted(c1["cos"], key=c1["cos"].get) == sorted(c1["cos10"], key=c1["cos10"].get)    # démonstration 3
    assert all(math.isclose(c1["cos"][k], c1["cos10"][k]) for k in c1["cos"])
    assert c1["retenus"] == ["d4"] and r(c1["cos"]["d4"], 10) == r(3 / math.sqrt(10), 10)
    assert [r(v, 5) for v in c1["normes"]] == [0.40684, 1.44476, 1.98151, 0.64328]
    assert [r(v, 5) for v in c1["produits"]] == [0.16552, 0.08276, 0.24828]
    assert [r(v, 5) for v in c1["tf_seul"].values()] == [0.8165, 0.40825, 0.40825, 0.94868]
    assert r(c1["w_bascule"], 5) == 0.30513 and r(c1["df_bascule"], 3) == 2.948
    assert r(2 / math.sqrt(6), 5) == 0.8165 and 1200 * 0.05 * 20 / 60 == 20
    assert r(1 / 0.64 - 1, 4) == 0.5625 and r(2 * (1 / 0.64 - 1), 3) == 1.125 and 1200 * 0.05 * 20 == 1200

    # Cas 2 — RH
    c2 = cas_2_sections_rh()
    assert [r(c2["idfs"][t], 5) for t in ("indemnité", "fin", "service", "démission")] == [1.60944, 0.51083, 0.28768, 3.21888]
    assert [r(c2["idfs"][t], 5) for t in ("calcul", "salaire")] == [1.38629, 0.79851]
    assert [r(v, 5) for v in c2["cos"].values()] == [0.75861, 0.11771, 0.74712]
    assert r(c2["cos"]["S1"] - c2["cos"]["S3"], 5) == 0.01149
    assert c2["comptage"] == {"S1": 13, "S2": 14, "S3": 6}
    assert [r(v, 5) for v in c2["somme"].values()] == [11.5289, 6.24188, 13.67401]
    assert r(c2["norme_q"], 5) == 3.64625 and r(c2["norme_s1"], 5) == 7.08206 and r(c2["produit_s1"], 5) == 19.58961
    assert [r(c2["v1"][t], 5) for t in ("indemnité", "fin", "service", "démission", "calcul", "salaire")] == [
        4.82831, 2.04330, 1.43841, 3.21888, 2.77259, 1.59702]
    assert c2["bascule"] == 5 and c2["jours"] == 165 and c2["indemnite"] == 55000
    assert 24 * 10000 == 240000 and c2["indemnite"] < 240000 and 21 * 5 + 30 * 2 == 165

    # Cas 3 — PUBLIC
    c3 = cas_3_permis_public()
    t_, rt, rh, qt, qh, fq, ab, fi = c3["mots"]
    assert r(c3["i_brut"][fi], 5) == 0.0202 and r(c3["i_brut"][rh], 5) == 3.91202 and r(c3["i_norm"][rh], 5) == 2.52573
    assert [r(c3["i_brut"][x], 5) for x in (t_, rt, qt, qh, fq, ab)] == [2.12026, 2.81341, 2.99573, 4.13517, 3.50656, 1.42712]
    assert r(c3["i_norm"][qh], 5) == 2.7181 and c3["df_norm"][rh] == 40 and c3["df_norm"][qh] == 33
    assert [r(v, 5) for v in c3["brut"][2]] == [0.11285, 0.44598] and [r(v, 5) for v in c3["norm"]] == [0.98096, 0.2888]
    assert [r(v, 5) for v in c3["brut"][0]] == [0.98362, 0.0] and [r(v, 5) for v in c3["brut"][1]] == [0.51047, 0.23852]
    assert c3["brut"][1][0] > c3["brut"][1][1] and c3["brut"][2][0] < c3["brut"][2][1]

    # Cas 4 — BTP
    c4 = cas_4_bordereau_btp()
    assert [r(c4["idfs"][t], 5) for t in ("béton", "c40", "c30", "coulage", "fondations", "pompe", "dalle")] == [
        1.89712, 4.89285, 4.60517, 2.59027, 2.99573, 3.28341, 2.77259]
    assert [r(v, 5) for v in c4["cos"].values()] == [0.88471, 0.48599, 0.64615] and r(c4["marge"], 5) == 0.23856
    assert [r(v, 5) for v in c4["tf_seul"].values()] == [0.88388, 0.75593, 0.56695] and r(c4["marge_tf"], 5) == 0.12795
    assert c4["df_bascule"] == 73 and (c4["ht"], c4["tva"]) == (54000, 2700.0)
    assert max(c4["sans_i1"].values()) < 0.8 and 120 * (450 - 390) == 7200 and 120 * 390 == 46800
    assert c4["ht"] + c4["tva"] == 56700 and r(c4["cos"]["I1"] - c4["cos"]["I3"], 5) == 0.23856

    print("Corrigé")
    a = math.log(4 / 3)
    ex6 = 2 * a * a / (a * math.sqrt(2) * a * math.sqrt(3))
    faux = (cosinus({"remboursement": a}, {"remboursement": a, "facture": 0.0}),
            cosinus({"remboursement": a}, {"remboursement": a, "facture": 0.0, "retard": math.log(4)}))
    print(f"  ex1 {2 * math.log(500 / 5):.2f} ; ex2 {math.log(1000):.3f} ; ex3 {3 * math.log10(100):.0f} ;"
          f" ex4 {math.log(2):.3f} ; ex6 {ex6:.5f} ; ex7 {faux[0]:.1f} et {faux[1]:.5f}")
    assert r(2 * math.log(100), 2) == 9.21 and r(math.log(1000), 3) == 6.908 and 3 * math.log10(100) == 6
    assert r(math.log(100), 3) == 4.605 and r(math.log(2), 3) == 0.693
    assert r(ex6, 5) == 0.8165 and ex6 >= 0.8 and r(faux[0], 10) == 1.0 and r(faux[1], 5) == 0.20319
    assert r(math.sqrt(a * a + math.log(4) ** 2), 5) == 1.41583
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Mécanisme : TF 3, DF 10 → 13.81551 ; TF 3, DF 500 → 2.07944 ; TF 5, DF 1000 → 0.00000
Démo 2 : -ln(0.01) = 4.60517 ; DF / 2 → + 0.69315 ; indépendants : 5.29832 = 2.30259 + 2.99573
Démo 3 : 1 / ln 10 = 0.43429 ; ln 100 = 4.60517 → log10 100 = 2
Démo 4 : d1 doublé 0.28160 ; « remboursement » ×1, ×2, ×10 → 0.28160, 0.39932, 0.69788
Démo 5 : +10 % de DF → -0.09531 ; relatif 2.07 % (DF = 10) et 13.75 % (DF = 500) ; DF 1 → 2 : N = 4 1.38629 → 0.69315, N = 1000 6.90776 → 6.21461
Démo 6 : ‖d0‖ = 0.40684 ; facteur 0.28160 ; cos(q, d0) = 1 → 0.28160
Exemple simple : splendide 13.81551 ; le 0.0
Cas 1 — ASSUR : IDF facture 0.28768, retard 1.38629 ; cosinus d1 0.28160 ; d2 0.10266 ; d3 0.10266 ; d4 0.94868 ; retenus (>= 0.8) ['d4']
  TF seul : d1 0.81650 ; d2 0.40825 ; d3 0.40825 ; d4 0.94868 ; bascule : IDF(retard) <= 0.30513, soit DF >= 2.948
Cas 2 — RH : IDF indemnité 1.60944 ; fin 0.51083 ; service 0.28768 ; démission 3.21888 ; cosinus S1 0.75861 ; S2 0.11771 ; S3 0.74712
  comptage {'S1': 13, 'S2': 14, 'S3': 6} ; somme TF-IDF S1 11.52890 ; S2 6.24188 ; S3 13.67401 ; S3 passe devant dès 5 « démission » ; indemnité 55000 AED (165 jours)
Cas 3 — PUBLIC : IDF في 0.02020 ; رخصه 3.91202 brut, 2.52573 normalisé ; brut P1 0.11285 < P2 0.44598 ; normalisé P1 0.98096 > P2 0.28880
  variantes ه dans la requête : 0 → P1 0.98362, P2 0.00000 ; 1 → P1 0.51047, P2 0.23852 ; 2 → P1 0.11285, P2 0.44598
Cas 4 — BTP : IDF c40 4.89285, béton 1.89712 ; cosinus I1 0.88471 ; I2 0.48599 ; I3 0.64615 ; marge 0.23856
  TF seul I1 0.88388 ; I2 0.75593 ; I3 0.56695 ; marge 0.12795 ; bascule DF(c40) = 73 ; facture 54000 + TVA 2700 = 56700 AED
Corrigé
  ex1 9.21 ; ex2 6.908 ; ex3 6 ; ex4 0.693 ; ex6 0.81650 ; ex7 1.0 et 0.20319
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme pondère les mots d'un corpus par TF-IDF, construit un vecteur creux par document et par requête, puis classe les documents par cosinus. Les cas ajoutent une normalisation des textes avant le comptage (cas 3) et une règle de décision sur le meilleur cosinus et son écart avec le deuxième (cas 1 et 4).

```text
ALGORITHME TFIDFEtClassement
ENTRÉES : documents tokenisés d₁ … d_N, requête q, normalisation (facultative), seuil s, écart minimal e
SORTIE  : documents triés par cosinus décroissant, et la décision (apparier ou revue)

  appliquer la même normalisation aux documents et à la requête
  POUR CHAQUE mot t du vocabulaire FAIRE
      DF[t] ← nombre de documents qui contiennent t
      IDF[t] ← ln(N / DF[t])                       (1 ≤ DF[t] ≤ N, sinon erreur)
  FIN POUR
  POUR CHAQUE texte x parmi (q, d₁ … d_N) FAIRE
      vecteur[x][t] ← (nombre de t dans x) × IDF[t], pour chaque mot t connu du corpus
  FIN POUR
  POUR CHAQUE document d FAIRE
      score[d] ← Cosinus(vecteur[q], vecteur[d])  (indéfini si un vecteur est nul)
  FIN POUR
  trier par score décroissant
  SI meilleur ≥ s ET meilleur − deuxième ≥ e ALORS apparier SINON revue humaine
  RETOURNER le classement et la décision
```

**Complexité.** O(total des mots du corpus) pour les DF ; avec des vecteurs creux, O(total des mots) pour les vecteurs et O(longueur de la requête × N) pour les cosinus, au lieu de O(N × V) avec des vecteurs denses sur un vocabulaire de V mots. La recherche d'une bascule par balayage (cas 2 et 4) refait le classement une fois par valeur essayée.

**Du squelette au code.** IDF[t] est la fonction `poids_idf(N, df_t)` ; le vecteur creux est `vectoriser(tf, idfs)`, la norme `norme(v)` et le cosinus `cosinus(a, b)`, qui renvoie `None` pour un vecteur nul. Dans `cas_1_tickets_assur`, les DF sont le `Counter` `df`, les IDF le dictionnaire `idf`, les vecteurs la fonction interne `vecteur(m, base)` et le classement le dictionnaire `cos` ; l'appel `vecteur(q, 10)` refait le classement en base 10 pour vérifier la démonstration 3. Les autres cas sont `cas_2_sections_rh`, `cas_3_permis_public` (avec la fonction interne `normaliser(tf)`) et `cas_4_bordereau_btp` (avec `classer(df_c40)` et `marge(c)`).
