# Étape 14 — Similarité Cosinus et Produit Scalaire (Le cœur du RAG et de la Mémoire)

> Étape 14 du parcours · Prérequis : [Ingénierie du contexte : définitions](<13c-Contexte-Definitions-Fondamentaux.md>) · Suite : [Fondements du RAG et de la mémoire](<15-Fondements-RAG-et-Memoire.md>)

## Définition

La similarité cosinus mesure l'angle entre deux vecteurs d'un espace à n dimensions : elle vaut le cosinus de cet angle. En IA, un vecteur (ou *embedding*) est une liste de nombres qu'un modèle d'embedding associe à un mot, à une phrase ou à un document pour en représenter le sens. Deux textes qui parlent du même sujet reçoivent des vecteurs qui pointent dans des directions voisines : au lieu de comparer des mots, on compare des directions. Le résultat est toujours compris entre −1 et 1, ce que la démonstration prouve : 1 pour deux vecteurs de même direction, 0 pour deux vecteurs perpendiculaires, −1 pour deux vecteurs de directions opposées.

## Rôle dans un agent

C'est l'une des formules qu'un AI Agentic Developer utilise le plus. Elle intervient quand l'agent *perçoit* une question et doit *décider* quoi placer dans son prompt avant d'*agir*. Le **retriever** d'un RAG (*Retrieval-Augmented Generation*) vectorise la question, calcule son cosinus avec chaque passage de la base documentaire et garde les k meilleurs (le top-k). La **mémoire à long terme** de l'agent fait la même chose avec ses souvenirs ; l'étape 17 combinera ce cosinus avec la récence et l'importance. On retrouve la même mesure dans un **garde-fou** qui repère une question proche d'une demande interdite, et dans un cache sémantique qui réutilise une réponse déjà produite pour une question presque identique. Sans mesure de similarité, l'agent ne pourrait chercher que des mots identiques : la recherche lexicale BM25 (étape 22) le fait très bien, mais elle ne voit pas que « j'ai oublié mon code » et « réinitialiser le mot de passe » parlent de la même chose.

## Équation complète

La similarité cosinus :

$$
\text{Similarité}(A, B) = \cos\theta = \frac{A \cdot B}{\lVert A \rVert \, \lVert B \rVert}
$$

Le produit scalaire, au numérateur :

$$
A \cdot B = \sum_{i=1}^{n} A_i B_i
$$

La norme (longueur) d'un vecteur, au dénominateur :

$$
\lVert A \rVert = \sqrt{\sum_{i=1}^{n} A_i^2}
$$

Pour des vecteurs normalisés Â = A / ‖ A ‖ et B̂ = B / ‖ B ‖ (démontré plus bas) :

$$
\lVert \hat{A} - \hat{B} \rVert^2 = 2 - 2\cos\theta
$$

## Décryptage des symboles

$$
A,\quad B
$$

**Sens :** les deux vecteurs comparés, par exemple A pour la question de l'utilisateur et B pour un passage de la base · **Type / plage :** listes de n réels · **Variable Python :** `A`, `B` ; `requete`, `vecteur` dans `top_k`

$$
n
$$

**Sens :** dimension : nombre de coordonnées de chaque vecteur (souvent 384, 768, 1536 ou 3072 selon le modèle d'embedding) · **Type / plage :** entier ≥ 1 · **Variable Python :** `len(A)`

$$
i,\quad A_i,\quad B_i
$$

**Sens :** indice d'une coordonnée, et les coordonnées correspondantes ; i va de 1 à n en maths, de 0 à n−1 en Python · **Type / plage :** entier ; réels · **Variable Python :** `i`, `a`, `b` dans les boucles

$$
\sum_{i=1}^{n}
$$

**Sens :** « additionne ce qui suit pour i allant de 1 à n » · **Type / plage :** opérateur · **Variable Python :** une boucle `for` et un accumulateur (`total`)

$$
A \cdot B
$$

**Sens :** produit scalaire : somme des produits coordonnée par coordonnée · **Type / plage :** réel · **Variable Python :** `produit_scalaire(A, B)`

$$
\lVert A \rVert
$$

**Sens :** norme L2 : longueur de la flèche, racine carrée de la somme des carrés · **Type / plage :** réel ≥ 0, nul seulement pour le vecteur nul · **Variable Python :** `norme_l2(A)`

$$
\theta
$$

**Sens :** angle entre les deux flèches · **Type / plage :** de 0° à 180° · **Variable Python :** `theta_deg`

$$
\cos\theta
$$

**Sens :** similarité cosinus · **Type / plage :** réel dans [−1, 1] · **Variable Python :** `similarite_cosinus(A, B)`

$$
\hat{A}
$$

**Sens :** vecteur normalisé A / ‖ A ‖, de norme 1 · **Type / plage :** liste de n réels · **Variable Python :** `normaliser(A)`

$$
t,\quad \lambda
$$

**Sens :** nombres réels auxiliaires de la démonstration ; λ multiplie un vecteur, ce n'est pas le taux de décroissance de l'étape 16 · **Type / plage :** réels · **Variable Python :** `t`, `3`, `-2` dans le bloc 7 du code

**La division par les normes** neutralise la norme des vecteurs, pas la longueur du texte. L'ancienne version de ce fichier disait qu'elle sert « pour que la longueur du texte n'influence pas le résultat » : c'est faux en général. Un modèle d'embedding neuronal ne produit pas un vecteur plus long pour un texte plus long, et beaucoup de modèles renvoient même des vecteurs déjà de norme 1. Le lien entre longueur du texte et norme n'existe que pour des vecteurs de comptage, comme le sac de mots de l'étape 18, où répéter un mot allonge le vecteur. Ce que la division garantit vraiment, c'est l'invariance d'échelle démontrée plus bas : multiplier un vecteur par un nombre positif ne change pas le score.

## Démonstration

Les trois résultats ci-dessous sont démontrés ici une fois pour toutes ; les étapes 19, 20, 21 et 55 y renvoient.

### 1. Le cosinus est toujours entre −1 et 1 (inégalité de Cauchy-Schwarz)

On suppose B ≠ 0 (si B = 0, les deux membres de l'inégalité ci-dessous valent 0 et elle est vraie). Pour tout réel t, on pose P(t) = ‖ A − tB ‖². C'est une somme de carrés, donc P(t) ≥ 0 pour tout t. On le développe, parce que le produit scalaire est bilinéaire (on peut développer comme un produit ordinaire) et symétrique (A · B = B · A) :

$$
P(t) = (A - tB) \cdot (A - tB) = \lVert B \rVert^2 \, t^2 - 2\,(A \cdot B)\, t + \lVert A \rVert^2
$$

C'est un trinôme du second degré en t, de coefficient dominant ‖ B ‖² > 0. Un tel trinôme qui ne devient jamais négatif a au plus une racine réelle, parce que s'il en avait deux distinctes, il serait strictement négatif entre elles. Son discriminant est donc négatif ou nul :

$$
\Delta = 4\,(A \cdot B)^2 - 4\,\lVert A \rVert^2 \, \lVert B \rVert^2 \le 0
$$

On divise par 4, puis on prend la racine carrée des deux membres, qui sont positifs : c'est l'inégalité de Cauchy-Schwarz.

$$
\lvert A \cdot B \rvert \le \lVert A \rVert \, \lVert B \rVert
$$

Si A et B sont tous deux non nuls, on divise par ‖ A ‖ ‖ B ‖ > 0 et l'on obtient −1 ≤ cosθ ≤ 1. C'est ce qui donne un sens à l'angle : `math.acos` n'accepte que des nombres de [−1, 1], et Cauchy-Schwarz garantit que la vraie valeur y est ; seul un arrondi peut en sortir de quelques 10⁻¹⁶, d'où le `max(-1.0, min(1.0, …))` du code.

En chiffres, avec A = (3, 4) et B = (4, 3) : ‖ A ‖² = ‖ B ‖² = 25 et A · B = 12 + 12 = 24, donc P(t) = 25t² − 48t + 25 et Δ = 4 × 576 − 4 × 625 = −196 < 0. La dérivée P'(t) = 50t − 48 s'annule en t\* = (A · B) / ‖ B ‖² = 0,96, où le trinôme atteint son minimum P(t\*) = 25 − 24²/25 = 1,96, qui vaut aussi −Δ / (4 ‖ B ‖²) = 196/100. Géométriquement, t\* B est la projection de A sur la droite portée par B, et 1,96 est le carré de la distance de A à cette droite. On retrouve

$$
(A \cdot B)^2 = 576 \le 625 = \lVert A \rVert^2 \lVert B \rVert^2 ,
$$

et cosθ = 24/25 = 0,96, soit θ ≈ 16,26°.

### 2. Cas d'égalité : le cosinus vaut ±1 si et seulement si les vecteurs sont colinéaires

Si | A · B | = ‖ A ‖ ‖ B ‖, le discriminant est nul et le trinôme a une racine double t₀ = (A · B) / ‖ B ‖². Alors ‖ A − t₀ B ‖² = 0 ; or un vecteur de norme nulle est le vecteur nul, parce qu'une somme de carrés nulle impose que chaque carré soit nul. Donc A = t₀ B : les vecteurs sont colinéaires. Réciproquement, si A = t₀ B avec t₀ ≠ 0, alors A · B = t₀ ‖ B ‖² et ‖ A ‖ = | t₀ | ‖ B ‖, donc cosθ = t₀ / | t₀ |, qui vaut +1 si t₀ > 0 (même sens) et −1 si t₀ < 0 (sens opposés).

Les exemples du code : A = (1, 2, 3) et B = (2, 4, 6) donnent ‖ A ‖² = 14, ‖ B ‖² = 56, A · B = 28, Δ = 4 × 784 − 4 × 14 × 56 = 0, t₀ = 28/56 = 0,5 et A − 0,5 B = (0, 0, 0) : cosinus 1. A = (1, 0) et B = (−2, 0) donnent Δ = 4 × 4 − 4 × 1 × 4 = 0 et t₀ = −2/4 = −0,5 : cosinus −1.

### 3. Invariance d'échelle

Pour tout réel λ ≠ 0 :

$$
\cos(\lambda A, B) = \frac{(\lambda A) \cdot B}{\lVert \lambda A \rVert \, \lVert B \rVert} = \frac{\lambda \, (A \cdot B)}{\lvert \lambda \rvert \, \lVert A \rVert \, \lVert B \rVert} = \frac{\lambda}{\lvert \lambda \rvert} \cos(A, B)
$$

La deuxième égalité vient de deux faits : le produit scalaire est linéaire, donc (λ A) · B = λ (A · B) ; et

$$
\lVert \lambda A \rVert = \sqrt{\sum \lambda^2 A_i^2} = \lvert \lambda \rvert \, \lVert A \rVert ,
$$

parce que

$$
\sqrt{\lambda^2} = \lvert \lambda \rvert .
$$

Le quotient λ / | λ | vaut +1 si λ > 0 et −1 si λ < 0. Multiplier un vecteur par un nombre positif ne change donc pas le cosinus ; par un nombre négatif, seul le signe change ; par 0, on obtient le vecteur nul, pour lequel le cosinus n'est pas défini et le code lève `ValueError`. Avec A = (3, 4) et B = (4, 3) : cos(3A, B) = 0,96 et cos(−2A, B) = −0,96. C'est cette propriété, et elle seule, qui justifie la phrase « le cosinus ignore la norme » : il ignore la norme des vecteurs, pas la longueur des textes.

### 4. Sur la sphère unité, distance euclidienne et cosinus donnent le même classement

On développe le carré de la distance, toujours par bilinéarité et symétrie :

$$
\lVert A - B \rVert^2 = (A - B) \cdot (A - B) = \lVert A \rVert^2 + \lVert B \rVert^2 - 2\, A \cdot B
$$

Si les deux vecteurs ont été normalisés, leurs normes valent 1 et leur produit scalaire est leur cosinus : Â · B̂ = cos(Â, B̂) parce que le dénominateur vaut 1 × 1, et cos(Â, B̂) = cos(A, B) par le point 3, puisque normaliser revient à multiplier par 1 / ‖ A ‖ > 0. D'où :

$$
\lVert \hat{A} - \hat{B} \rVert^2 = 1 + 1 - 2\cos\theta = 2 - 2\cos\theta
$$

La fonction c ↦ 2 − 2c est strictement décroissante, et la racine carrée est strictement croissante : plus le cosinus est grand, plus la distance est petite. Trier des documents par distance croissante ou par cosinus décroissant donne donc exactement le même ordre, à condition d'avoir normalisé. Avec Â = (0,6 ; 0,8) et B̂ = (0,8 ; 0,6), les versions normalisées de (3, 4) et (4, 3) :

$$
\lVert \hat{A} - \hat{B} \rVert^2 = 0{,}2^2 + 0{,}2^2 = 0{,}08 = 2 - 2 \times 0{,}96 .
$$

Sans normalisation, l'identité est fausse : (3, 0) et (0,6 ; 0,8) ont un cosinus de 0,6, donc 2 − 2cosθ = 0,80, mais ‖ A − B ‖² = 2,4² + 0,8² = 6,40 (l'étape 15 rejoue ce contre-exemple).

### 5. Exemple fait à la main (le code reprend ces nombres)

La question « comment changer mon mot de passe ? » est représentée par q = (0,90 ; 0,10 ; 0,00 ; 0,20), de norme

$$
\lVert q \rVert = \sqrt{0{,}81 + 0{,}01 + 0 + 0{,}04} = \sqrt{0{,}86} = 0{,}9274 .
$$

Les quatre passages de la mémoire donnent :

| Passage | q · d | ‖ d ‖ | cosθ | ‖ q̂ − d̂ ‖² = 2 − 2cosθ |
|---|---|---|---|---|
| faq_reinitialiser_mot_de_passe | 0,792 + 0,012 + 0 + 0,05 = 0,854 | √0,8517 = 0,9229 | 0,854 / 0,8558 = 0,9979 | 0,0043 |
| faq_mot_de_passe_oublie | 0,72 + 0,005 + 0 + 0,08 = 0,805 | √0,8025 = 0,8958 | 0,805 / 0,8308 = 0,9690 | 0,0620 |
| souvenir_prefere_le_the | 0 + 0,095 + 0 + 0,01 = 0,105 | √0,915 = 0,9566 | 0,105 / 0,8871 = 0,1184 | 1,7633 |
| faq_lire_ma_facture | 0,045 + 0,01 + 0 + 0 = 0,055 | √0,915 = 0,9566 | 0,055 / 0,8871 = 0,0620 | 1,8760 |

Les cosinus décroissent pendant que les distances croissent : le point 4 se vérifie ligne à ligne. Le top-3 garde les trois premières lignes, y compris le souvenir « préfère le thé », qui n'a rien à voir avec la question : le top-k prend toujours k passages, la pertinence demande un seuil en plus (étape 19).

## Effets et comportement

- **Un angle proche de 0** donne un cosinus proche de 1 : les deux vecteurs pointent dans la même direction et l'agent considère le passage comme très pertinent.
- **Un angle de 90°** donne un cosinus nul : les vecteurs sont perpendiculaires (orthogonaux). Dans l'exemple jouet, cela veut dire « aucun rapport » ; avec un vrai modèle d'embedding, deux textes sans rapport donnent rarement exactement 0 (l'étape 15 explique pourquoi), d'où la nécessité de calibrer un seuil (étape 19).
- **Un angle supérieur à 90°** donne un cosinus négatif, jusqu'à −1 pour des directions opposées. C'est rare avec des embeddings de texte.
- **Multiplier un vecteur par un nombre positif** ne change rien (point 3) ; par un nombre négatif, le signe s'inverse.
- **Augmenter la dimension n** rend chaque cosinus plus cher, mais seulement proportionnellement : environ 2n opérations pour le produit scalaire, autant pour chaque norme. Ce qui coûte vraiment, c'est le nombre N de vecteurs comparés, d'où les N × 2n opérations de la recherche exhaustive (bloc 6 du code). L'ancienne version laissait entendre que l'index HNSW répond à la croissance de n : un index approximatif (HNSW, IVF) réduit N, le nombre de vecteurs comparés, pas n.

## Du symbole au code Python

$$
A \cdot B = \sum A_i B_i
$$

**Variable ou fonction :** `produit_scalaire(A, B)`

$$
\lVert A \rVert
$$

**Variable ou fonction :** `norme_l2(A)`

$$
\cos\theta,\quad \theta
$$

**Variable ou fonction :** `similarite_cosinus(A, B)`, `theta_deg`

$$
\hat{A}
$$

**Variable ou fonction :** `normaliser(A)`

**Symbole :** top-k · **Variable ou fonction :** `top_k(requete, documents, k)`

$$
P(t),\quad \Delta,\quad t^*,\quad t_0
$$

**Variable ou fonction :** `aa`, `bb`, `ab`, `delta`, `t_min`, `t0` dans le bloc 7

Les indices mathématiques vont de 1 à n. En Python ils vont de 0 à n−1. C'est la même somme : on visite chaque coordonnée une fois. Le déroulé ci-dessous suit les lignes dans l'ordre où elles s'exécutent. Copiez ensuite le bloc dans `cosine_rag.py`.

### Déroulé, ligne par ligne

Les `assert` ne font pas partie du calcul. Ils comparent le nombre sorti de la fonction au nombre qu'on a obtenu à la main. Si une ligne change de sens, le programme s'arrête.

**`produit_scalaire(A, B)`** — c'est le numérateur

$$
A \cdot B = \sum A_i B_i .
$$

On l'appelle d'abord avec A = [1, 2, 3] et B = [2, 4, 6].

- `if len(A) != len(B)` : les deux listes doivent avoir le même nombre de cases. Sinon le produit Aᵢ Bᵢ n'a pas de partenaire et la somme n'existe pas.
- `total = 0.0` : l'accumulateur de ∑. Il vaut 0 tant qu'aucun terme n'a été ajouté.
- `for i, (a, b) in enumerate(zip(A, B))` : `zip` met face à face la case i de A et la case i de B. `enumerate` donne i, à partir de 0.
- `terme = a * b` : un seul produit. Tour 0 : 1 × 2 = 2. Tour 1 : 2 × 4 = 8. Tour 2 : 3 × 6 = 18.
- `total += terme` : on ajoute ce produit au total. Après les trois tours : 0 + 2 + 8 + 18 = 28.
- `return total` : on renvoie 28. On ne divise pas ici. 28 n'est pas encore une similarité.

**`norme_l2(A)`** — c'est

$$
\lVert A \rVert = \sqrt{\sum A_i^2} ,
$$

la longueur du vecteur.

- `somme_carres = 0.0` : même idée d'accumulateur, mais on additionne des carrés, pas des produits croisés.
- Dans la boucle, `somme_carres += a * a`. Pour [1, 2, 3] : 1 + 4 + 9 = 14.
- `carre = …` ne sert qu'à l'affichage : un nombre négatif est imprimé entre parenthèses, `(-2.0000)² = 4.0000`, parce que −2² se lirait −(2²) = −4.
- `return math.sqrt(somme_carres)` : la racine.

$$
\sqrt{14} \approx 3{,}7417 .
$$

Pour B = [2, 4, 6], la somme des carrés vaut 56 et la racine vaut ≈ 7,4833, soit exactement le double, parce que B est le double de A.

**`similarite_cosinus(A, B)`** — assemble les trois morceaux : cosθ = (A · B) / (‖ A ‖ ‖ B ‖).

- Elle appelle `produit_scalaire`, puis `norme_l2` sur A, puis `norme_l2` sur B. Trois résultats : 28, 3,7417 et 7,4833.
- `if na == 0.0 or nb == 0.0` : un vecteur dont toutes les cases sont 0 n'a pas de direction. Diviser par sa longueur, qui est 0, n'a pas de sens. On refuse.
- `cosinus = dot / (na * nb)` :

$$
28 / (3{,}7417 \times 7{,}4833) = 28 / 28 = 1 .
$$

La division est là pour annuler la longueur. B est deux fois plus long que A, mais il pointe au même endroit, donc le cosinus vaut 1, pas 2.
- `cosinus = max(-1.0, min(1.0, cosinus))` : un arrondi peut donner 1,0000000000000002. `acos` refuserait. On rabat le nombre dans [−1, 1], où Cauchy-Schwarz garantit que se trouve la vraie valeur.
- `theta_deg = math.degrees(math.acos(cosinus))` : `acos(1)` vaut 0 radian, donc 0 degré. C'est l'angle entre les deux flèches.

Les deux appels suivants vérifient les deux autres cas géométriques. [1, 0, 0] et [0, 1, 0] : chaque produit Aᵢ Bᵢ vaut 0, la somme vaut 0, le cosinus vaut 0, l'angle vaut 90°. [1, 0] et [−2, 0] : le seul produit vaut −2, les normes valent 1 et 2, le quotient vaut −1, l'angle vaut 180°.

**`normaliser`** puis le bloc « sphère unité ».

- `n = math.sqrt(sum(a * a for a in A))` : la même norme, écrite en une ligne parce qu'on n'a plus besoin d'imprimer chaque carré.
- `return [a / n for a in A]` : chaque case est divisée par la longueur. Après ça, la longueur vaut 1.
- Sur A = [1, 0] et B = [0,6 ; 0,8] (déjà de longueur 1, car 0,6² + 0,8² = 1), le produit scalaire vaut 0,6 et le cosinus vaut aussi 0,6. La division par les normes ne change plus rien : elles valent 1.
- `ecart = [a - b ...]` puis `distance_carree = sum(x * x ...)` : on calcule

$$
\lVert A - B \rVert^2 = (1 - 0{,}6)^2 + (0 - 0{,}8)^2 = 0{,}16 + 0{,}64 = 0{,}80 .
$$

- `2 * (1 - cos)` vaut aussi 0,80. Classer les documents par distance euclidienne ou par cosinus donne donc le même ordre, à condition d'avoir normalisé avant (démonstration, point 4).

**`top_k(requete, documents, k)`** — c'est le retrieval.

- La question est la liste `[0.90, 0.10, 0.00, 0.20]`. Chaque document est une autre liste de 4 nombres, rangée dans le dictionnaire `memoire`.
- La boucle `for nom, vecteur in documents.items()` appelle `similarite_cosinus` une fois par document, avec `verbeux=False` pour ne pas réimprimer les sommes.
- `scores.append((score, nom))` puis `scores.sort(reverse=True)` : on trie du plus grand cosinus au plus petit. `return scores[:k]` ne garde que les 3 premiers. Ce sont les seuls passages qu'on collera dans le prompt.
- Le premier vaut 0,9979 : « réinitialiser le mot de passe ». Le deuxième vaut 0,9690. Le troisième, « préfère le thé », ne vaut que 0,1184 : il entre dans le top-3 seulement parce qu'il en faut trois. « Facture » tombe à 0,062 et n'est pas dans les 3. Le seuil n'est pas dans la formule : c'est le tri, puis la coupe à `k`.

**Le compte de FLOPs**, bloc 6.

- `M * (2 * d)` : pour chacun des 10 000 000 vecteurs, on fait 1536 multiplications et 1535 additions, qu'on arrondit à 2 × 1536 opérations. Total : 30,72 milliards.
- On divise par 100 × 10⁹ opérations par seconde (une vitesse de machine illustrative), on multiplie par 1000 pour avoir des millisecondes : 307 ms pour une seule question. D'où l'index : il ne change pas `similarite_cosinus`, il réduit le nombre de vecteurs sur lesquels on l'appelle.

**Le bloc 7, « Les trois démonstrations »**, reprend les nombres de la section Démonstration.

- `aa`, `bb` et `ab` valent 25, 25 et 24 pour a = (3, 4) et b = (4, 3). La boucle sur `t` vérifie, pour quatre valeurs de t, que ‖ a − tb ‖² calculé directement est bien le trinôme `bb * t * t - 2 * ab * t + aa` : c'est le développement du point 1.
- `delta = 4 * ab * ab - 4 * aa * bb` vaut 2304 − 2500 = −196. `t_min = ab / bb` vaut 0,96 et `p_min` vaut 1,96, qui est aussi −Δ / (4 ‖ b ‖²) = 196 / 100.
- Pour (1, 2, 3) et (2, 4, 6), le discriminant vaut 0, la racine double `t0` vaut 0,5 et `reste`, le vecteur a − t₀ b, vaut `[0.0, 0.0, 0.0]` : c'est le cas d'égalité du point 2. Pour (1, 0) et (−2, 0), `t0_neg` vaut −0,5 et le cosinus −1.
- `c_pos` et `c_neg` vérifient l'invariance d'échelle du point 3 : 0,96 pour 3a, −0,96 pour −2a, et l'angle de (3, 4) avec (4, 3) vaut 16,26°. Le vecteur 0 · a est nul : `similarite_cosinus` lève `ValueError`, et le `try / except / else` vérifie que l'erreur a bien lieu.
- `a_hat` et `b_hat` valent (0,6 ; 0,8) et (0,8 ; 0,6) ; `d2` vaut 0,08, soit 2 − 2 × 0,96 (point 4). `brut` refait le calcul sans normaliser, avec (3, 0) : 6,40 au lieu de 0,80.
- `par_distance` trie les quatre passages du bloc 5 par distance croissante après normalisation, `par_cosinus` les trie par cosinus décroissant : les deux listes sont identiques. Les deux derniers `assert` vérifient les distances 0,0043 ; 0,0620 ; 1,7633 ; 1,8760 et les cosinus 0,9979 ; 0,9690 ; 0,1184 ; 0,0620 du tableau de l'exemple.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`produit_scalaire(A, B)`** — Cette fonction est le comptable qui aligne deux colonnes de chiffres et additionne les produits ligne à ligne, à voix haute : elle reçoit deux listes de nombres, lève `ValueError` si elles n'ont pas la même longueur, puis multiplie chaque case de A par la case de même rang de B, ajoute ce produit à un total parti de 0 et imprime à chaque tour le terme et la somme partielle. Elle renvoie ce total, le Σ AᵢBᵢ de la formule, sans rien diviser : pour (1, 2, 3) et (2, 4, 6), elle imprime 2, 8 puis 18 et renvoie 28, qui n'est pas encore une similarité.

**`norme_l2(A)`** — Celle-ci est l'arpenteur qui mesure la longueur d'une flèche à partir de ses coordonnées : elle reçoit une liste de nombres, additionne leurs carrés en imprimant chaque carré et la somme courante, un nombre négatif étant écrit entre parenthèses pour que (−2)² ne se lise pas −2², puis renvoie la racine carrée de cette somme. Elle ne lève rien, et renvoie 0 pour le vecteur nul. Pour (1, 2, 3), la somme des carrés vaut 14 et la norme environ 3,7417 ; pour (2, 4, 6), elle vaut 56 et la norme environ 7,4833, exactement le double.

**`similarite_cosinus(A, B, verbeux)`** — C'est l'arbitre qui ne juge que la direction de deux flèches et jamais leur longueur : la fonction reçoit deux vecteurs et un drapeau `verbeux`, vrai par défaut, calcule le produit scalaire et les deux normes, en passant par les deux fonctions bavardes en mode verbeux ou par des sommes silencieuses sinon, lève `ValueError` si l'un des vecteurs est nul, puis divise le produit par le produit des normes, rabat le résultat dans [−1, 1] contre les arrondis et calcule l'angle en degrés. Elle renvoie le cosinus : 1 pour (1, 2, 3) et (2, 4, 6), 0 pour deux axes perpendiculaires, −1 pour des directions opposées, et 0,96 pour (3, 4) et (4, 3), soit un angle de 16,26°. En mode silencieux, elle ne vérifie pas que les deux vecteurs ont la même dimension.

**`normaliser(A)`** — Cette fonction ramène toute flèche à la même longueur, comme un cartographe qui ne garde que le cap : elle reçoit un vecteur, calcule sa norme, lève `ValueError` avec le message « impossible de normaliser le vecteur nul » si elle vaut 0, et renvoie la liste des coordonnées divisées par cette norme, dont la longueur vaut alors 1. Sur la sphère unité, le cosinus se réduit au produit scalaire et la distance au carré vaut 2 − 2 cos : (3, 4) devient (0,6 ; 0,8), (4, 3) devient (0,8 ; 0,6), et la distance au carré entre les deux vaut 0,08, soit 2 − 2 × 0,96.

**`top_k(requete, documents, k)`** — C'est le bibliothécaire du RAG qui, devant une question, sort de ses rayonnages les k fiches les plus proches : la fonction reçoit le vecteur de la question, un dictionnaire qui associe à chaque nom de document son vecteur, et le nombre k de passages à garder, calcule le cosinus de la question avec chaque document en mode silencieux, range les couples (score, nom) du plus grand au plus petit et renvoie les k premiers. Pour la question sur le mot de passe et k = 3, elle garde 0,9979 pour « réinitialiser le mot de passe », 0,9690 pour « mot de passe oublié » et 0,1184 pour « préfère le thé », qui n'entre que parce qu'il en faut trois.

**`main()`** — C'est le professeur de géométrie qui fait défiler sept tableaux : il montre d'abord, en détail, les cosinus 1, 0 et −1 des trois cas géométriques, puis l'égalité entre cosinus et produit scalaire sur deux vecteurs unitaires et l'identité ‖A − B‖² = 2(1 − cos). Il fait ensuite tourner le mini RAG à quatre coordonnées et son top-3, chiffre la force brute sur 10 millions de vecteurs de dimension 1 536, 30,72 milliards d'opérations et 307 ms à 100 GFLOPs par seconde, et rejoue enfin les démonstrations : discriminant −196 pour (3, 4) et (4, 3), racine double des vecteurs colinéaires, invariance d'échelle, refus du vecteur nul et même classement par distance et par cosinus.

```python
"""Chapitre 1 — similarité cosinus, du symbole Σ jusqu'au top-k d'un RAG."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def produit_scalaire(A, B):
    """A · B = Σ_{i=1}^{n} A_i B_i"""
    if len(A) != len(B):
        raise ValueError("A et B doivent avoir la même dimension n")
    total = 0.0
    for i, (a, b) in enumerate(zip(A, B)):
        terme = a * b
        total += terme
        print(f"    i={i}   {a:.4f} × {b:.4f} = {terme:.4f}    somme partielle = {total:.4f}")
    return total


def norme_l2(A):
    """||A|| = sqrt(Σ_{i=1}^{n} A_i²)"""
    somme_carres = 0.0
    for i, a in enumerate(A):
        somme_carres += a * a
        carre = f"({a:.4f})²" if a < 0 else f"{a:.4f}²"   # (-2)² = 4, alors que -2² se lirait -4
        print(f"    i={i}   {carre} = {a * a:.4f}    somme des carrés = {somme_carres:.4f}")
    return math.sqrt(somme_carres)


def similarite_cosinus(A, B, verbeux=True):
    """cos(θ) = (A · B) / (||A|| ||B||)"""
    if verbeux:
        print("  produit scalaire A · B")
    dot = produit_scalaire(A, B) if verbeux else sum(a * b for a, b in zip(A, B))
    if verbeux:
        print("  norme ||A||")
    na = norme_l2(A) if verbeux else math.sqrt(sum(a * a for a in A))
    if verbeux:
        print("  norme ||B||")
    nb = norme_l2(B) if verbeux else math.sqrt(sum(b * b for b in B))
    if na == 0.0 or nb == 0.0:
        raise ValueError("un vecteur nul n'a pas de direction : le cosinus n'est pas défini")
    cosinus = dot / (na * nb)
    # Le cosinus peut sortir très légèrement de [-1, 1] à cause des arrondis.
    cosinus = max(-1.0, min(1.0, cosinus))
    theta_deg = math.degrees(math.acos(cosinus))
    if verbeux:
        print(f"  cos(θ) = {dot:.4f} / ({na:.4f} × {nb:.4f}) = {cosinus:.4f}")
        print(f"  θ = {theta_deg:.2f}°")
    return cosinus


def normaliser(A):
    """v_hat = v / ||v||. Après ça, ||v_hat|| = 1 et le cosinus se réduit au produit scalaire."""
    n = math.sqrt(sum(a * a for a in A))
    if n == 0.0:
        raise ValueError("impossible de normaliser le vecteur nul")
    return [a / n for a in A]


def top_k(requete, documents, k):
    """L'agent classe sa mémoire par cosinus décroissant et ne garde que k passages."""
    scores = []
    for nom, vecteur in documents.items():
        score = similarite_cosinus(requete, vecteur, verbeux=False)
        scores.append((score, nom))
    scores.sort(reverse=True)
    return scores[:k]


def main():
    print("=== 1. Même direction, angle 0, cosinus 1 ===")
    # [2, 4, 6] est exactement 2 × [1, 2, 3] : même direction, longueur double.
    # La division par les normes annule cette longueur. Seule la direction reste.
    c = similarite_cosinus([1.0, 2.0, 3.0], [2.0, 4.0, 6.0])
    assert abs(c - 1.0) < 1e-9

    print("\n=== 2. Directions perpendiculaires, angle 90°, cosinus 0 ===")
    c = similarite_cosinus([1.0, 0.0, 0.0], [0.0, 1.0, 0.0])
    assert abs(c - 0.0) < 1e-9

    print("\n=== 3. Directions opposées, angle 180°, cosinus -1 ===")
    c = similarite_cosinus([1.0, 0.0], [-2.0, 0.0])
    assert abs(c - (-1.0)) < 1e-9

    print("\n=== 4. Vecteurs déjà de longueur 1 : cosinus = produit scalaire ===")
    A = [1.0, 0.0]
    B = [0.6, 0.8]  # 0.6² + 0.8² = 1
    print("  sans le détail des sommes :")
    dot = sum(a * b for a, b in zip(A, B))
    cos = similarite_cosinus(A, B, verbeux=False)
    ecart = [a - b for a, b in zip(A, B)]
    distance_carree = sum(x * x for x in ecart)
    print(f"  A · B = {dot:.4f}")
    print(f"  cos(θ) = {cos:.4f}")
    print(f"  ||A - B||² = {distance_carree:.4f}")
    print(f"  2 × (1 - cos(θ)) = {2 * (1 - cos):.4f}")
    print("  Sur la sphère unité, classer par distance euclidienne ou par cosinus donne le même ordre.")
    assert abs(dot - cos) < 1e-9
    assert abs(distance_carree - 2 * (1 - cos)) < 1e-9

    print("\n=== 5. Mini RAG : « comment changer mon mot de passe ? » ===")
    # Quatre coordonnées seulement, pour voir chaque multiplication.
    # Dans un vrai embedding, n vaut 1536 ou 3072 : la boucle est la même, plus longue.
    question = [0.90, 0.10, 0.00, 0.20]
    memoire = {
        "faq_reinitialiser_mot_de_passe": [0.88, 0.12, 0.02, 0.25],
        "faq_mot_de_passe_oublie": [0.80, 0.05, 0.00, 0.40],
        "faq_lire_ma_facture": [0.05, 0.10, 0.95, 0.00],
        "souvenir_prefere_le_the": [0.00, 0.95, 0.10, 0.05],
    }
    print("  détail du meilleur voisin :")
    similarite_cosinus(question, memoire["faq_reinitialiser_mot_de_passe"])
    classement = top_k(question, memoire, k=3)
    print("  top-3 injecté dans le prompt :")
    for rang, (score, nom) in enumerate(classement, start=1):
        print(f"    {rang}. {nom:32s}  cos = {score:.4f}")
    assert classement[0][1] == "faq_reinitialiser_mot_de_passe"
    assert classement[0][0] > 0.95
    assert all(score < 0.3 for score, nom in classement if "facture" in nom or "the" in nom)

    print("\n=== 6. Pourquoi on ne balaie pas 10 millions de vecteurs à la main ===")
    M = 10_000_000
    d = 1536
    # Un produit scalaire coûte d multiplications et d-1 additions, environ 2d flops.
    flops = M * (2 * d)
    gflops_par_seconde = 100e9
    latence_ms = flops / gflops_par_seconde * 1000
    print(f"  opérations = {M:.0e} vecteurs × (2 × {d}) = {flops / 1e9:.2f} GFLOPs")
    print(f"  à 100 GFLOPs/s : {latence_ms:.0f} ms pour UNE recherche en force brute")
    print("  Un index (HNSW, IVF) ne change pas la formule du cosinus.")
    print("  Il choisit quelques centaines de candidats, puis cette même fonction score les candidats.")

    print("\n=== 7. Les trois démonstrations, vérifiées sur leurs nombres ===")
    # 7a. Cauchy-Schwarz par le discriminant, avec a = (3, 4) et b = (4, 3).
    a, b = [3.0, 4.0], [4.0, 3.0]
    aa = sum(x * x for x in a)                 # ||a||² = 25
    bb = sum(y * y for y in b)                 # ||b||² = 25
    ab = sum(x * y for x, y in zip(a, b))      # a · b = 24
    for t in (-1.0, 0.0, 0.5, 2.0):            # P(t) = ||a − t b||² est bien le trinôme bb t² − 2 ab t + aa
        direct = sum((x - t * y) ** 2 for x, y in zip(a, b))
        assert abs(direct - (bb * t * t - 2 * ab * t + aa)) < 1e-9
    delta = 4 * ab * ab - 4 * aa * bb
    t_min = ab / bb
    p_min = sum((x - t_min * y) ** 2 for x, y in zip(a, b))
    print(f"  P(t) = ||a − t·b||² = {bb:.0f} t² − {2 * ab:.0f} t + {aa:.0f}")
    print(f"  discriminant = 4 × {ab:.0f}² − 4 × {aa:.0f} × {bb:.0f} = {delta:.0f}")
    print(f"  minimum en t = {t_min:.2f} : P = {p_min:.2f} ; (a·b)² = {ab * ab:.0f} <= {aa * bb:.0f} = ||a||²·||b||²")
    assert (aa, bb, ab, delta) == (25.0, 25.0, 24.0, -196.0)
    assert abs(t_min - 0.96) < 1e-12 and abs(p_min - 1.96) < 1e-12
    assert abs(p_min - (-delta / (4 * bb))) < 1e-12

    # 7b. Cas d'égalité : vecteurs colinéaires, discriminant nul, racine double.
    a2, b2 = [1.0, 2.0, 3.0], [2.0, 4.0, 6.0]
    aa2 = sum(x * x for x in a2)
    bb2 = sum(y * y for y in b2)
    ab2 = sum(x * y for x, y in zip(a2, b2))
    delta2 = 4 * ab2 * ab2 - 4 * aa2 * bb2
    t0 = ab2 / bb2
    reste = [x - t0 * y for x, y in zip(a2, b2)]
    print(f"  (1, 2, 3) et (2, 4, 6) : discriminant = {delta2:.0f}, racine double t = {t0}, a − t·b = {reste}")
    assert (aa2, bb2, ab2, delta2, t0) == (14.0, 56.0, 28.0, 0.0, 0.5) and reste == [0.0, 0.0, 0.0]
    a3, b3 = [1.0, 0.0], [-2.0, 0.0]
    t0_neg = sum(x * y for x, y in zip(a3, b3)) / sum(y * y for y in b3)
    print(f"  (1, 0) et (−2, 0) : racine double t = {t0_neg}, cosinus = {similarite_cosinus(a3, b3, verbeux=False):.0f}")
    assert t0_neg == -0.5 and [x - t0_neg * y for x, y in zip(a3, b3)] == [0.0, 0.0]

    # 7c. Invariance d'échelle : λ > 0 ne change rien, λ < 0 change le signe, λ = 0 est refusé.
    c = similarite_cosinus(a, b, verbeux=False)
    c_pos = similarite_cosinus([3 * x for x in a], b, verbeux=False)
    c_neg = similarite_cosinus([-2 * x for x in a], b, verbeux=False)
    print(f"  cos(a, b) = {c:.2f}   cos(3a, b) = {c_pos:.2f}   cos(−2a, b) = {c_neg:.2f}   θ = {math.degrees(math.acos(c)):.2f}°")
    assert abs(c - 0.96) < 1e-12 and abs(c_pos - 0.96) < 1e-12 and abs(c_neg + 0.96) < 1e-12
    assert round(math.degrees(math.acos(c)), 2) == 16.26
    try:
        similarite_cosinus([0.0 * x for x in a], b, verbeux=False)
    except ValueError:
        print("  cos(0·a, b) → ValueError : le vecteur nul n'a pas de direction")
    else:
        raise AssertionError("le vecteur nul aurait dû être refusé")

    # 7d. Sphère unité : ||â − b̂||² = 2 − 2 cos, donc même classement.
    a_hat, b_hat = normaliser(a), normaliser(b)
    d2 = sum((x - y) ** 2 for x, y in zip(a_hat, b_hat))
    print(f"  â = ({a_hat[0]:.1f}, {a_hat[1]:.1f})   b̂ = ({b_hat[0]:.1f}, {b_hat[1]:.1f})   ||â − b̂||² = {d2:.2f} = 2 − 2 × {c:.2f}")
    assert abs(d2 - 0.08) < 1e-12 and abs(d2 - (2 - 2 * c)) < 1e-12
    brut = sum((x - y) ** 2 for x, y in zip([3.0, 0.0], [0.6, 0.8]))   # sans normaliser : identité fausse
    print(f"  sans normaliser, (3, 0) et (0.6, 0.8) : ||a − b||² = {brut:.2f} ≠ 2 − 2 cos = {2 - 2 * 0.6:.2f}")
    assert abs(brut - 6.40) < 1e-12
    q_hat = normaliser(question)
    par_distance = sorted(memoire, key=lambda nom: sum((x - y) ** 2 for x, y in zip(q_hat, normaliser(memoire[nom]))))
    par_cosinus = [nom for _, nom in top_k(question, memoire, k=len(memoire))]
    distances = [round(sum((x - y) ** 2 for x, y in zip(q_hat, normaliser(memoire[nom]))), 4) for nom in par_distance]
    print(f"  mini RAG, ||q̂ − d̂||² dans l'ordre : {distances}")
    print(f"  ordre par distance croissante = ordre par cosinus décroissant : {par_distance == par_cosinus}")
    assert par_distance == par_cosinus and distances == [0.0043, 0.0620, 1.7633, 1.8760]
    assert [round(s, 4) for s, _ in top_k(question, memoire, k=4)] == [0.9979, 0.9690, 0.1184, 0.0620]
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
…
  cos(θ) = 28.0000 / (3.7417 × 7.4833) = 1.0000
…
  top-3 injecté dans le prompt :
    1. faq_reinitialiser_mot_de_passe    cos = 0.9979
    2. faq_mot_de_passe_oublie           cos = 0.9690
    3. souvenir_prefere_le_the           cos = 0.1184
…
  à 100 GFLOPs/s : 307 ms pour UNE recherche en force brute
…
  discriminant = 4 × 24² − 4 × 25 × 25 = -196
  minimum en t = 0.96 : P = 1.96 ; (a·b)² = 576 <= 625 = ||a||²·||b||²
  (1, 2, 3) et (2, 4, 6) : discriminant = 0, racine double t = 0.5, a − t·b = [0.0, 0.0, 0.0]
  cos(a, b) = 0.96   cos(3a, b) = 0.96   cos(−2a, b) = -0.96   θ = 16.26°
  cos(0·a, b) → ValueError : le vecteur nul n'a pas de direction
  â = (0.6, 0.8)   b̂ = (0.8, 0.6)   ||â − b̂||² = 0.08 = 2 − 2 × 0.96
  sans normaliser, (3, 0) et (0.6, 0.8) : ||a − b||² = 6.40 ≠ 2 − 2 cos = 0.80
  mini RAG, ||q̂ − d̂||² dans l'ordre : [0.0043, 0.062, 1.7633, 1.876]
OK — toutes les vérifications sont passées.
```

Ce que le programme vous force à voir : la similarité n'est pas un appel magique à une base vectorielle. C'est une somme, deux racines carrées, une division, puis un tri. Le seuil « proche de 1 » et le top-k sont des décisions d'ingénierie posées après ce calcul, pas à la place du calcul.

## Squelette algorithmique

Le programme de ce fichier construit la recherche par similarité la plus simple qui soit : encoder la question, calculer son cosinus avec chaque document, et garder les k meilleurs. C'est le cœur d'un RAG et d'une mémoire sémantique avant tout index spécialisé.

```text
ALGORITHME TopKCosinus
ENTRÉES : vecteur q de la question, documents D = (v₁ … vₙ), k
SORTIE  : les k documents les plus proches de q, avec leur score

  ‖q‖ ← √(Σᵢ qᵢ²)
  SI ‖q‖ = 0 ALORS ERREUR « question vide »
  POUR CHAQUE document vⱼ FAIRE
      produit ← Σᵢ qᵢ × vⱼ,ᵢ
      ‖vⱼ‖ ← √(Σᵢ vⱼ,ᵢ²)
      scoreⱼ ← produit / (‖q‖ × ‖vⱼ‖)
  FIN POUR
  trier les documents par score décroissant
  RETOURNER les k premiers

VARIANTE NormaliserUneFois
  à l'indexation : vⱼ ← vⱼ / ‖vⱼ‖ pour chaque document
  à la requête   : q ← q / ‖q‖ ; scoreⱼ ← q · vⱼ        (le cosinus devient un simple produit scalaire)
```

**Complexité.** Pour n documents de dimension d, le calcul des scores coûte O(n × d), et le tri complet O(n log n) ; garder seulement les k meilleurs avec un tas ramène le tri à O(n log k). La variante normalisée retire la racine carrée et la division du calcul de chaque requête, sans changer l'ordre de grandeur. Au-delà de quelques centaines de milliers de documents, ce parcours exhaustif devient trop lent, et l'on passe à un index approximatif (HNSW, IVF) qui évite de comparer la question à tous les documents.

**Du squelette au code.** `produit_scalaire` calcule la somme des produits, `norme_l2` la racine de la somme des carrés, `similarite_cosinus` le quotient (avec, en mode verbeux, l'affichage de chaque étape), `normaliser` la variante « normaliser une fois », et `top_k` la boucle sur les documents suivie du tri.

## Cas d'usage réels aux Émirats

Les tailles de corpus, les seuils et les scores ci-dessous sont illustratifs : en production, on les mesure sur ses propres données et avec son propre modèle d'embedding.

### Banque — la FAQ du support, en arabe et en anglais

Une banque de détail de Dubaï déploie dans son application mobile un agent de support qui répond en arabe et en anglais à partir de quelques milliers d'articles de FAQ, découpés en passages et vectorisés par un modèle d'embedding multilingue. Un client écrit « I forgot my password, how do I reset it? » : l'agent vectorise la phrase, calcule son cosinus avec chaque passage exactement comme le bloc 5 du code le fait sur quatre passages jouets, et obtient par exemple 0,9979 pour « réinitialiser le mot de passe », 0,9690 pour « mot de passe oublié » et 0,0620 pour « lire ma facture ». Il colle les deux meilleurs passages dans le prompt, répond avec la procédure officielle et cite l'article d'où elle vient. Sans recherche par le sens, une recherche par mots exacts raterait la même question posée en arabe ou avec un autre verbe (« changer », « récupérer »), et le modèle de langage risquerait d'inventer une procédure, ce qui est grave dans une banque où une procédure fausse peut pousser un client vers un faux site. La contrainte opérationnelle est que l'agent ne demande jamais un mot de passe ni un code reçu par SMS : cette règle ne vient pas du cosinus, elle est portée par un garde-fou séparé qui relit chaque réponse avant envoi. L'indicateur suivi en production est le taux de questions résolues sans transfert vers un conseiller, mesuré séparément pour l'arabe et pour l'anglais.

### Assurance — une préférence mémorisée, et le piège de la négation

Un assureur auto et santé fait tourner un agent de suivi des sinistres qui garde en mémoire, pour chaque assuré, les préférences exprimées au fil des échanges. Trois semaines plus tôt, un assuré de Sharjah a écrit : « Je ne veux plus que ma voiture retourne au garage de la dernière fois. » Quand il déclare un nouveau sinistre et demande « où faire réparer ma voiture ? », le cosinus entre sa question et ce souvenir est élevé parce que les deux parlent de garage et de réparation ; le souvenir entre dans le top-k et le modèle de langage, en le lisant, propose un autre garage agréé. L'ancienne version de ce fichier racontait la même scène avec « je n'aime pas le café » et prétendait que l'agent retrouve la préférence « via une autre dimension vectorielle » : c'est faux, aucune coordonnée ne stocke une préférence, le cosinus retrouve le souvenir parce qu'il porte sur le même sujet, et c'est le modèle de langage qui en tire la décision. Le piège est la négation : « je veux ce garage » et « je ne veux plus ce garage » ont des vecteurs très proches, car un embedding capte le sujet bien mieux que la polarité, si bien que l'agent ne décide jamais sur le seul score et lit toujours le texte du souvenir. L'indicateur suivi est le nombre de réclamations du type « on m'a renvoyé là où j'avais refusé d'aller », avec un objectif de zéro.

### Immobilier — recommander des biens à partir d'un profil

Une agence immobilière de Dubaï et d'Abu Dhabi représente chaque annonce active par un vecteur, calculé à partir du texte de l'annonce, du quartier, du nombre de chambres et du prix en AED/sqft, et chaque client par la moyenne des vecteurs des annonces qu'il a longuement consultées. L'agent de recommandation calcule le cosinus entre le profil du client et chacune des quelque 15 000 annonces actives, puis propose les cinq meilleures. L'invariance d'échelle (démonstration, point 3) a ici une conséquence pratique : si l'on additionnait les vecteurs au lieu d'en faire la moyenne, un client qui a consulté 40 villas semblables aurait un profil environ dix fois plus long qu'un client qui en a consulté 4 du même type, et le cosinus les traiterait pourtant exactement de la même façon, parce que multiplier un vecteur par 10 ne change pas son cosinus. Un produit scalaire brut, lui, donnerait au premier client des scores dix fois plus grands et favoriserait les annonces dont le vecteur est le plus long, ce qui n'a rien à voir avec l'adéquation au besoin. Avant tout calcul, l'agent écarte les annonces qui ne respectent pas les règles de publicité immobilière de la RERA (à confirmer avec le texte en vigueur), puis applique le cosinus aux seules annonces publiables. L'indicateur suivi est le taux de demandes de visite par recommandation affichée.

### Secteur public — un guichet bilingue qui reconnaît les reformulations

Une entité de services publics en ligne, accessible par UAE Pass, reçoit des questions en arabe, en anglais et souvent dans un mélange des deux, écrites par des usagers qui ne connaissent pas le nom administratif des procédures. Son agent compare chaque question aux fiches de procédure vectorisées : avec un modèle d'embedding multilingue, une question en arabe sur le renouvellement d'une carte et la fiche anglaise « Renew your card » obtiennent un cosinus élevé alors qu'elles ne partagent aucun mot. Avant de vectoriser, l'équipe normalise l'arabe (formes de l'alef unifiées, ta marbuta, suppression des diacritiques), parce que deux écritures du même mot donneraient sinon des vecteurs inutilement éloignés, et elle prévoit plusieurs translittérations des noms propres. Si le meilleur cosinus reste bas, l'agent ne devine pas : il demande à l'usager de préciser le service concerné, et le réglage de ce seuil est le sujet de l'étape 19. Sans cette recherche par le sens, l'usager devrait taper le nom exact de la procédure, ce qui est précisément ce qu'il ignore, et le centre de contact recevrait les questions que le portail aurait dû résoudre. Par minimisation des données, seules les fiches publiques entrent dans l'index : aucune donnée personnelle de l'usager n'est vectorisée. L'indicateur suivi est la part des sessions qui aboutissent à la bonne procédure sans appel au centre de contact.

### BTP — rapprocher les lignes de facture des postes du devis

Un groupe de construction qui mène de grands chantiers à Dubaï reçoit chaque mois des centaines de factures de sous-traitants soumises à la TVA de 5 %, dont les libellés reprennent rarement mot pour mot ceux du devis signé (« coulage dalle niveau 3 » d'un côté, « béton armé, plancher R+3 » de l'autre). Son agent vectorise chaque ligne de facture et chaque poste du devis, puis propose de rattacher la ligne au poste de plus grand cosinus, comme le top-1 du bloc 5. Il ne rattache automatiquement que si le meilleur poste dépasse un seuil et devance nettement le deuxième : un meilleur poste à 0,91 suivi d'un deuxième à 0,89 laisse un écart trop faible, et la ligne part chez le contrôleur de gestion avec les deux candidats affichés. Sans ce rapprochement, chaque facture passe en contrôle manuel et les dépassements de quantité par rapport au devis sont découverts après paiement, quand il est difficile de récupérer l'argent. La contrainte est comptable : le montant hors taxe, la TVA de 5 % et la retenue de garantie se calculent ensuite par des règles exactes, jamais par le modèle ; le cosinus sert seulement à trouver le bon poste. L'indicateur suivi est la part des rattachements automatiques que le contrôleur ne corrige pas.

### Crypto — relier une alerte à la bonne procédure d'astreinte

Une plateforme d'actifs virtuels agréée par la VARA a rédigé une centaine de procédures d'astreinte, une par type d'incident : retrait bloqué, pool de liquidité déséquilibré, écart de prix anormal entre deux sources de cotation. Quand une alerte tombe, l'agent d'exploitation vectorise son message, calcule le cosinus avec chaque procédure et propose à l'opérateur la plus proche, avec son score. À cette échelle, la recherche exhaustive suffit largement : 100 procédures en dimension 1024 coûtent environ 100 × 2 × 1024 = 204 800 opérations, contre 30,72 milliards pour les 10 millions de vecteurs du bloc 6, si bien qu'aucun index approximatif n'est nécessaire et que le résultat est exact. Le même cosinus sert à regrouper les alertes : deux alertes dont les vecteurs ont un cosinus très proche de 1 décrivent presque toujours le même incident, et l'opérateur n'en reçoit qu'une. Sans cette mise en correspondance, l'opérateur cherche la procédure à la main en pleine nuit, ou en applique une mauvaise. La contrainte est la traçabilité : chaque procédure proposée, son score et la décision de l'opérateur sont journalisés pour pouvoir être expliqués lors d'un contrôle. L'indicateur suivi est le délai entre l'alerte et sa prise en charge.

## Pièges et limites

- **Le vecteur nul n'a pas de cosinus.** Renvoyer 0 ou ajouter un epsilon au dénominateur masque une panne d'embedding (texte vide, appel au modèle échoué) ; le code lève `ValueError`.
- **Le cosinus capte le sujet, pas le sens exact.** « Je veux ce garage » et « je ne veux plus ce garage », ou « 2 chambres » et « 3 chambres », ont des vecteurs très proches : la décision se prend en lisant le texte, pas sur le seul score.
- **Deux modèles d'embedding ne sont pas comparables.** Un cosinus entre un vecteur du modèle A et un vecteur du modèle B n'a aucun sens, même à dimension égale : quand on change de modèle, on revectorise toute la base et on recalibre les seuils (étape 19).
- **Remplacer le cosinus par un produit scalaire sans normaliser** fausse le classement : les vecteurs de grande norme gagnent (démonstration, point 4, et contre-exemple de l'étape 15).
- **Le top-k n'est pas un filtre de pertinence.** Il renvoie toujours k passages, même hors sujet, comme le souvenir « préfère le thé » à 0,1184 : il faut un seuil minimal en plus.

### Exercice feuille blanche

1. Sans regarder le code, écrire `similarite_cosinus(A, B)` à partir des trois équations, avec le refus du vecteur nul, puis vérifier que cos((3, 4), (4, 3)) = 0,96.
2. Prédire, puis vérifier : que valent cos((3, 4), (−4, 3)), cos((3, 4), (6, 8)) et cos((−6, −8), (4, 3)) ? (Réponses : 0, parce que le produit scalaire vaut −12 + 12 = 0 ; 1, parce que (6, 8) = 2 × (3, 4) ; −0,96, parce que (−6, −8) = −2 × (3, 4).)
3. Trouver le bug : `cosinus = dot / na * nb`. Que renvoie cette ligne pour (3, 4) et (4, 3) ? (Réponse : 24 / 5 × 5 = 24, parce que Python divise avant de multiplier ; un « cosinus » de 24 viole Cauchy-Schwarz, ce qui trahit le bug, et la ligne `max(-1.0, min(1.0, …))` le masquerait en renvoyant 1.)

## Pour aller plus loin

- La distance angulaire θ / π, avec θ en radians, est une vraie distance : elle vérifie l'inégalité triangulaire, ce que 1 − cosθ ne fait pas (étape 21).
- L'inégalité de Cauchy-Schwarz vaut dans tout espace muni d'un produit scalaire, y compris en dimension infinie (espaces de Hilbert), avec la même preuve par le discriminant.
- Chercher le plus grand produit scalaire sans normaliser s'appelle MIPS (*Maximum Inner Product Search*) ; on peut la ramener à une recherche par cosinus en ajoutant une coordonnée à chaque vecteur.

> Suite : [Fondements du RAG et de la mémoire](<15-Fondements-RAG-et-Memoire.md>) — étape 15.
