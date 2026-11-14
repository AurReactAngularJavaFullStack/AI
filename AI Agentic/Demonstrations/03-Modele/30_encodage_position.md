# 30 — Encodage de position : démonstrations

> Fiche : [30 — Encodage de position](<../../Images/03-Modele/30_encodage_position.md>) · Image : `30_encodage_position.jpg` · Leçon : [Étape 35 — Encodage de position](<../../06-Attention-et-Transformer/35-Encodage-de-Position.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
PE(pos, 2i) = \sin\left( \frac{pos}{10000^{2i/d}} \right), \qquad PE(pos, 2i+1) = \cos\left( \frac{pos}{10000^{2i/d}} \right)
$$

Chaque position reçoit un vecteur de dimension d. Les coordonnées vont par paires (sinus ; cosinus) qui tournent chacune à sa propre vitesse.

On note ωᵢ la fréquence de la paire i :

$$
\omega_i = 10000^{-2i/d}
$$

Le vecteur de position est ajouté à l'embedding du token avant la première couche (leçon, équation complète) :

$$
X_{pos} = E_{w_{pos}} + PE_{pos}
$$

## Les symboles, un par un

$$
pos
$$

La position du token dans la séquence, un entier ≥ 0 (le premier token est en position 0). Variable `pos`.

$$
d
$$

La largeur des vecteurs du modèle, un entier pair (512 dans l'article d'origine, 4 ou 8 dans les exemples à la main). Variable `d` ; `pe` refuse un d impair.

$$
i
$$

Le numéro de la paire (sinus ; cosinus), un entier de 0 à d/2 − 1. Variable `i` dans `omega(i, d)` et dans la boucle de `pe`.

$$
\omega_i
$$

La fréquence angulaire de la paire i, en radians par token, dans ]0 ; 1] : 1 pour i = 0, puis de plus en plus petite. Fonction `omega(i, d)`, ou la variable locale `w` de `pe`.

$$
\lambda_i = \frac{2\pi}{\omega_i}
$$

La longueur d'onde de la paire i : le nombre de tokens pour un tour complet, de 2π ≈ 6,28 à environ 60 611 tokens pour d = 512. Liste `ondes` dans `main`.

$$
PE_{pos}
$$

Le vecteur de position, de taille d, dont chaque coordonnée est dans [−1 ; 1]. Fonction `pe(pos, d)`.

$$
E_{w}
$$

L'embedding du token w, un vecteur de taille d appris par le modèle ; il n'est pas calculé ici, seul `rope` et la démonstration 6 utilisent des vecteurs d'exemple `q` et `kv` à sa place.

$$
k
$$

Un décalage en tokens, un entier (positif vers la droite, négatif vers la gauche). Variable `k`.

$$
R(\theta)
$$

La rotation 2 × 2 d'angle θ, [[cos θ ; sin θ] ; [−sin θ ; cos θ]], comme dans la leçon. Fonction `tourner(paire, theta)`.

$$
T_k
$$

La matrice de translation, diagonale par blocs, qui applique R(k ωᵢ) à chaque paire i ; elle décale n'importe quel vecteur de position de k tokens. Dans le programme, elle est appliquée paire par paire avec `tourner`, et sur une paire par le calcul de `rot`.

$$
S(k) = \sum_{i=0}^{d/2-1} \cos(k\,\omega_i)
$$

La similarité de position de deux tokens séparés de k : le produit scalaire PE(p) · PE(p + k), qui vaut d/2 pour k = 0. Fonction `similarite_ecart(k, d)`.

$$
A(k) = \sum_{i=0}^{d/2-1} \sin(k\,\omega_i)
$$

L'orientation de l'écart k : une quantité qui change de signe quand on échange « avant » et « après » (cas 3). Fonction `orientation_ecart(k, d)`.

## Le mécanisme, avant les preuves

Ce qui entre : une position entière pos et une dimension d. Pour chaque paire i, la formule multiplie la position par la fréquence ωᵢ, ce qui donne un angle en radians : la position devient une aiguille qui tourne sur un cadran. Le sinus et le cosinus de cet angle sont les deux coordonnées de la pointe de l'aiguille sur le cercle unité : elles restent toujours entre −1 et 1, quelle que soit la position, ce qu'un simple compteur pos ne ferait pas. La division par 10000^(2i/d) donne à chaque paire sa vitesse : la paire 0 tourne d'un radian par token et fait un tour en 6,28 tokens, la dernière tourne si lentement qu'elle met des dizaines de milliers de tokens à faire un tour. Pourquoi un sinus et un cosinus, plutôt qu'un sinus seul ? Parce que les deux ensemble donnent la position exacte de l'aiguille, et qu'avancer de k tokens revient alors à tourner l'aiguille d'un angle fixe, une opération linéaire que le modèle peut apprendre (démonstration 2) ; un sinus seul ne le permet pas. Pourquoi des vitesses en progression géométrique ? Pour que chaque échelle de distance (voisin, phrase, paragraphe, document) soit lue par au moins une paire (démonstration 4). Pourquoi 10000 ? Pour que la paire la plus lente ait une longueur d'onde (2π × 10000 ≈ 62 832 tokens à la limite) plus grande que les textes visés. Ce qui sort : un vecteur de taille d, ajouté à l'embedding du token, qui porte « où » sans écraser « quoi ».

Le petit film chiffré, avec d = 4 (fréquences ω₀ = 1 et ω₁ = 0,01) et les positions 0, 1, 2 :

| Position | Angle paire 0 | sin ; cos paire 0 | Angle paire 1 | sin ; cos paire 1 |
|---|---|---|---|---|
| 0 | 0 | 0 ; 1 | 0 | 0 ; 1 |
| 1 | 1 | 0,84147 ; 0,54030 | 0,01 | 0,01000 ; 0,99995 |
| 2 | 2 | 0,90930 ; −0,41615 | 0,02 | 0,02000 ; 0,99980 |

D'une position à la suivante, la paire 0 change beaucoup (son cosinus passe de 0,54030 à −0,41615), la paire 1 presque pas : la première distingue les voisins immédiats, la seconde les grandes distances. Pour un développeur Java, c'est comme une horloge à plusieurs aiguilles : la trotteuse distingue les secondes, l'aiguille des heures distingue les heures, et l'ensemble donne une heure unique sur un grand intervalle.

## Démonstration 1 — Chaque paire est sur le cercle unité

**Ce qu'on démontre.** Pour d pair et toute position pos :

$$
\lVert PE(pos) \rVert = \sqrt{d/2}
$$

**L'idée.** Chaque paire (sinus ; cosinus) est un point du cercle unité, donc de longueur 1 ; le vecteur contient d/2 paires, et les carrés des longueurs s'additionnent.

**La preuve, pas à pas.**

**Étape 1.** Pour chaque paire i, sin²(pos ωᵢ) + cos²(pos ωᵢ) = 1, parce que c'est l'identité de Pythagore sur le cercle unité.

**Étape 2.** Le carré de la norme est la somme des carrés de toutes les coordonnées ; on les regroupe par paires :

$$
\lVert PE(pos) \rVert^2 = \sum_{i=0}^{d/2-1} \big( \sin^2(pos\,\omega_i) + \cos^2(pos\,\omega_i) \big) = \sum_{i=0}^{d/2-1} 1 = \frac{d}{2}
$$

**Étape 3.** On prend la racine carrée, parce qu'une norme est positive. ∎

**Vérification chiffrée.** Pour d = 8, la norme vaut √4 = 2 aux positions 0, 7, 512 et 4 096 (le programme le vérifie). Contre-exemple quand l'hypothèse « d pair » manque : avec d = 5, la dernière coordonnée sin(pos ω₂), avec ω₂ = 10000^(−4/5) ≈ 0,000631, n'a pas de cosinus partenaire ; le carré de la norme vaut 2 + sin²(pos ω₂), soit 2 en position 0 mais environ 2,9076 en position 2 000 : la norme dépend alors de la position.

**Ce que la preuve révèle du mécanisme.** Aucune position ne « parle plus fort » qu'une autre : l'encodage ajoute la même quantité d'énergie à chaque token, que le token soit le premier ou le dix-millième. Un simple compteur pos ajouté à l'embedding ferait au contraire dominer la position sur le sens dès les premières centaines de tokens.

**Conséquence pour un agent.** L'encodage n'écrase pas l'embedding du token, quelle que soit sa place dans le prompt ; ce qui change avec la place, c'est la direction du vecteur de position, pas sa taille. En pratique, on choisit toujours d pair (la leçon, point 8, montre ce que coûte un d impair).

## Démonstration 2 — Décaler de k positions revient à tourner chaque paire

**Ce qu'on démontre.** Pour toute paire i, toute position pos et tout décalage k :

$$
\begin{pmatrix} \sin((pos+k)\,\omega_i) \\ \cos((pos+k)\,\omega_i) \end{pmatrix} = \begin{pmatrix} \cos(k\,\omega_i) & \sin(k\,\omega_i) \\ -\sin(k\,\omega_i) & \cos(k\,\omega_i) \end{pmatrix} \begin{pmatrix} \sin(pos\,\omega_i) \\ \cos(pos\,\omega_i) \end{pmatrix}
$$

donc PE(pos + k) = Tₖ · PE(pos), où Tₖ ne dépend que de k et de d, pas de pos.

**L'idée.** Avancer de k tokens ajoute le même angle kωᵢ à l'aiguille de la paire i, quelle que soit sa position de départ ; ajouter un angle, c'est tourner, et une rotation est une opération linéaire.

**La preuve, pas à pas.**

**Étape 1.** On pose a = pos ωᵢ et b = k ωᵢ, de sorte que (pos + k) ωᵢ = a + b.

**Étape 2.** On écrit les formules d'addition, vraies pour tous réels a et b :

$$
\sin(a + b) = \cos b \,\sin a + \sin b \,\cos a, \qquad \cos(a + b) = -\sin b \,\sin a + \cos b \,\cos a
$$

**Étape 3.** Ces deux lignes sont exactement le produit de la matrice R(b) par le vecteur (sin a ; cos a), parce que chaque ligne de la matrice multiplie (sin a ; cos a) terme à terme.

**Étape 4.** b = k ωᵢ ne contient pas pos ; en plaçant les blocs R(k ωᵢ) sur la diagonale, paire après paire, on obtient Tₖ, indépendante de pos. ∎

**Vérification chiffrée.** Avec d = 4, PE(2) = (sin 2 ; cos 2 ; sin 0,02 ; cos 0,02) ≈ (0,909297 ; −0,416147 ; 0,019999 ; 0,999800). La première ligne de T₃ est (cos 3 ; sin 3 ; 0 ; 0) ≈ (−0,989992 ; 0,141120 ; 0 ; 0), d'où la première coordonnée −0,989992 × 0,909297 + 0,141120 × (−0,416147) ≈ −0,900197 − 0,058727 = −0,958924, qui est bien sin 5. Le programme vérifie les quatre coordonnées, et la paire 1 de d = 8 pour pos = 17 et k = 5 par le calcul de `rot`. Contre-exemple quand on garde le sinus seul : sin 1 et sin(π − 1) valent tous deux 0,84147, mais un token plus loin, sin 2 ≈ 0,90930 alors que sin(π) = 0 ; aucune fonction du sinus seul ne peut donc donner le sinus de la position suivante.

**Ce que la preuve révèle du mécanisme.** « Trois tokens plus loin » est la même transformation T₃ partout dans le texte : c'est ce qui permet à des projections apprises de reconnaître une relation de distance, où qu'elle se trouve. Les rotations se composent (Tₖ Tₘ = Tₖ₊ₘ) et s'inversent par transposition (T₋ₖ = Tₖᵀ), comme le rappelle la leçon.

**Conséquence pour un agent.** Une relation fixe entre deux tokens (« le montant suit l'étiquette Montant : ») est plus facile à exploiter quand l'écart entre eux est toujours le même : un format constant « champ : valeur » sert le modèle mieux qu'une mise en page visuelle (cas 1).

## Démonstration 3 — Le produit scalaire de deux positions ne dépend que de leur écart

**Ce qu'on démontre.** Pour toutes positions p et q :

$$
PE(p) \cdot PE(q) = \sum_{i=0}^{d/2 - 1} \cos\big((p - q)\,\omega_i\big) = S(p - q)
$$

**L'idée.** Le produit scalaire de deux points du cercle unité est le cosinus de l'angle qui les sépare ; cet angle, pour la paire i, vaut (p − q) ωᵢ.

**La preuve, pas à pas.**

**Étape 1.** On regroupe le produit scalaire par paires, parce qu'il est la somme des produits coordonnée par coordonnée.

**Étape 2.** Pour une paire i, on applique la formule cos(a − b) = cos a cos b + sin a sin b avec a = p ωᵢ et b = q ωᵢ :

$$
\sin(p\,\omega_i)\sin(q\,\omega_i) + \cos(p\,\omega_i)\cos(q\,\omega_i) = \cos\big((p - q)\,\omega_i\big)
$$

**Étape 3.** On additionne sur les d/2 paires. Le résultat ne dépend que de p − q, et pas du signe de p − q, parce que le cosinus est pair. ∎

**Vérification chiffrée.** Avec d = 8, les fréquences valent 1 ; 0,1 ; 0,01 ; 0,001, et pour un écart de 3 : cos 3 + cos 0,3 + cos 0,03 + cos 0,003 ≈ −0,98999 + 0,95534 + 0,99955 + 1,00000 ≈ 1,96489. Le programme trouve PE(10) · PE(13) = PE(100) · PE(103) = 1,96489. Contre-exemple avec les sinus seuls : sin 10 × sin 13 ≈ −0,22858, mais sin 100 × sin 103 ≈ −0,31546 ; le même écart de 3 donne deux valeurs différentes.

**Ce que la preuve révèle du mécanisme.** Les positions 10 et 13 sont aussi « proches » que 100 et 103 : l'encodage porte des distances relatives, pas seulement des positions absolues. Mais la similarité S(k) est paire en k : elle ne dit pas qui est avant qui ; c'est l'orientation A(k) qui le dit (cas 3).

**Conséquence pour un agent.** Le modèle voit des écarts en tokens, pas des écarts en lignes, en colonnes ou en jours : tout autre ordre (alignement d'un tableau, chronologie) doit être écrit explicitement dans le texte (cas 1 et 4).

## Démonstration 4 — Les longueurs d'onde forment une progression géométrique

**Ce qu'on démontre.** La paire i fait un tour complet en λᵢ tokens, et le rapport entre deux paires voisines est constant :

$$
\lambda_i = \frac{2\pi}{\omega_i} = 2\pi \times 10000^{2i/d}, \qquad \frac{\lambda_{i+1}}{\lambda_i} = 10000^{2/d}
$$

**L'idée.** Les fréquences sont des puissances successives d'un même nombre ; leurs inverses aussi, donc leurs rapports sont tous égaux.

**La preuve, pas à pas.**

**Étape 1.** La paire i revient à son point de départ quand l'angle pos ωᵢ vaut 2π, parce que sin et cos sont 2π-périodiques ; d'où pos = 2π / ωᵢ = λᵢ.

**Étape 2.** On remplace ωᵢ par 10000^(−2i/d) : 1/ωᵢ = 10000^(2i/d), parce que 1/a⁻ˣ = aˣ.

**Étape 3.** On divise λᵢ₊₁ par λᵢ : les 2π se simplifient et les exposants se soustraient, parce que aˣ / aʸ = aˣ⁻ʸ :

$$
\frac{\lambda_{i+1}}{\lambda_i} = 10000^{2(i+1)/d - 2i/d} = 10000^{2/d}
$$

∎

**Vérification chiffrée.** Pour d = 8, le rapport vaut 10000^(1/4) = 10 : longueurs d'onde ≈ 6,28 ; 62,83 ; 628,32 ; 6 283,19 tokens. Pour d = 512, le rapport vaut 10000^(2/512) ≈ 1,03663, et la dernière paire (i = 255) a une longueur d'onde 2π × 10000^(510/512) ≈ 60 611 tokens.

**Ce que la preuve révèle du mécanisme.** La paire 0 est la plus rapide (un tour en un peu plus de six tokens), la dernière la plus lente : chaque échelle de distance, en progression géométrique, est lue par une paire dont la longueur d'onde lui correspond. Au-delà de la plus grande longueur d'onde, plus aucune paire n'est « lente » à l'échelle du texte.

**Conséquence pour un agent.** La plus grande longueur d'onde donne un ordre de grandeur de la distance au-delà de laquelle l'encodage se replie ; avec d = 8, c'est 6 283 tokens, ce qui fixe la valeur de bascule du cas 1.

## Démonstration 5 — La distance entre deux positions ne dépend que de l'écart, et une seule paire la replie

**Ce qu'on démontre.** Pour toutes positions p et q, avec g = p − q :

$$
\lVert PE(p) - PE(q) \rVert^2 = d - 2\,S(g) = \sum_{i=0}^{d/2-1} 4 \sin^2\!\Big( \frac{g\,\omega_i}{2} \Big)
$$

En particulier, avec une seule paire (d = 2, ω = 1), la distance vaut 2 |sin(g/2)| : elle revient près de 0 chaque fois que g est proche d'un multiple de 2π.

**L'idée.** La distance entre deux points du cercle est la corde qui les relie, 2 sin(angle/2) ; une seule aiguille ne distingue pas deux positions qui ont fait un nombre entier de tours d'écart. Plusieurs aiguilles de vitesses différentes ne se replient pas toutes en même temps.

**La preuve, pas à pas.**

**Étape 1.** On développe le carré de la différence, parce que ‖u − v‖² = ‖u‖² + ‖v‖² − 2 u · v :

$$
\lVert PE(p) - PE(q) \rVert^2 = \frac{d}{2} + \frac{d}{2} - 2\,PE(p) \cdot PE(q) = d - 2\,S(g)
$$

en utilisant les démonstrations 1 et 3.

**Étape 2.** Paire par paire, 2 − 2 cos(g ωᵢ) = 4 sin²(g ωᵢ / 2), parce que cos(2x) = 1 − 2 sin² x ; on additionne sur les paires.

**Étape 3.** Avec une seule paire de fréquence 1, la distance vaut √(4 sin²(g/2)) = 2 |sin(g/2)|, qui s'annule quand g/2 est un multiple de π, c'est-à-dire quand g est un multiple de 2π. ∎

**Vérification chiffrée.** Avec d = 8 et g = 3 : 8 − 2 × 1,96489 = 4,07022, qui est bien le carré de la distance entre PE(10) et PE(13). Avec une seule paire (d = 2) : écart 1 → 0,95885 ; écart 6 → 0,28224 ; écart 44 → 0,0177, presque une collision, parce que 44 est proche de 7 × 2π ≈ 43,98. Avec deux paires (d = 4), l'écart 44 donne déjà 0,43682, et avec quatre paires (d = 8), 1,67553.

**Ce que la preuve révèle du mécanisme.** La paire rapide sépare bien les voisins mais confond des positions éloignées ; les paires lentes, inutiles pour les voisins, lèvent ces confusions. C'est la raison d'être des d/2 fréquences différentes : aucune paire seule ne suffit.

**Conséquence pour un agent.** Une petite dimension (modèle compact, tête de petite largeur) replie plus vite les grandes distances : sur de longs prompts, on vérifie la qualité des réponses par tranche de longueur plutôt que de supposer qu'elle reste constante.

## Démonstration 6 — Avec des rotations des requêtes et des clés, le score ne dépend que de l'écart

**Ce qu'on démontre.** L'encodage rotatif (RoPE), cité dans la leçon, fait tourner chaque paire de la requête de l'angle p ω et chaque paire de la clé de l'angle p′ ω, au lieu d'ajouter PE. Alors, pour chaque paire :

$$
\big( R(p\,\omega)\,\mathbf{q} \big) \cdot \big( R(p'\,\omega)\,\mathbf{k} \big) = \mathbf{q} \cdot R\big((p' - p)\,\omega\big)\,\mathbf{k}
$$

Le score d'attention (fiche 05) ne dépend donc que de l'écart p′ − p.

**L'idée.** Tourner les deux vecteurs d'un même angle ne change pas leur produit scalaire ; seule compte la différence des deux rotations, c'est-à-dire l'écart des positions.

**La preuve, pas à pas.**

**Étape 1.** Le produit scalaire s'écrit avec une transposée : (R(α)q) · (R(β)k) = qᵀ R(α)ᵀ R(β) k, parce que u · v = uᵀ v et (A u)ᵀ = uᵀ Aᵀ.

**Étape 2.** R(α)ᵀ = R(−α), parce que transposer échange les deux sinus de signes opposés ; et R(−α) R(β) = R(β − α), par les formules d'addition de la démonstration 2.

**Étape 3.** Avec α = p ω et β = p′ ω, on obtient qᵀ R((p′ − p) ω) k, qui ne contient que l'écart. ∎

**Vérification chiffrée.** Avec une paire de fréquence 1, 𝐪 = (1 ; 0) et 𝐤 = (0,6 ; 0,8) : aux positions (2 ; 5) comme (10 ; 13), le score vaut 𝐪 · R(3) 𝐤 = 0,6 cos 3 + 0,8 sin 3 ≈ −0,594 + 0,1129 = −0,48110. Contre-exemple avec l'addition au lieu de la rotation : (𝐪 + PE(2)) · (𝐤 + PE(5)) ≈ −1,13626, mais (𝐪 + PE(10)) · (𝐤 + PE(13)) ≈ −0,96750 : avec l'encodage additif, les termes croisés 𝐪 · PE et PE · 𝐤 dépendent de la position absolue.

**Ce que la preuve révèle du mécanisme.** La rotation sépare proprement « quoi » (le vecteur) et « où » (l'angle) : le score garde le produit des contenus et ne retient que la distance. C'est la même identité que la démonstration 3, appliquée aux requêtes et aux clés.

**Conséquence pour un agent.** Avec un modèle à encodage rotatif, un motif « étiquette puis valeur deux tokens plus loin » donne le même score au début ou à la fin d'un long dossier ; le développeur n'a pas à choisir l'encodage d'un modèle existant, mais il en tient compte pour choisir le modèle et pour tester ses réponses à plusieurs positions du prompt.

## Exemple simple, à la main

Dimension d = 4, position 1. Il y a d/2 = 2 paires. Paire 0 : ω₀ = 10000^(−0/4) = 10000⁰ = 1. Paire 1 : ω₁ = 10000^(−2/4) = 10000^(−1/2) = 1/√10000 = 1/100 = 0,01. Les angles valent donc 1 × 1 = 1 radian et 1 × 0,01 = 0,01 radian.

$$
PE(1) = (\sin 1\ ;\ \cos 1\ ;\ \sin 0{,}01\ ;\ \cos 0{,}01) \approx (0{,}84147\ ;\ 0{,}54030\ ;\ 0{,}01000\ ;\ 0{,}99995)
$$

Pour le petit angle, sin 0,01 ≈ 0,01 et cos 0,01 ≈ 1 − 0,01²/2 = 0,99995. On vérifie la démonstration 1 : 0,84147² + 0,54030² ≈ 0,70807 + 0,29192 ≈ 1 et 0,01² + 0,99995² ≈ 0,0001 + 0,9999 = 1, donc la norme vaut √2.

## Cas d'usage complexes, démontrés

Les dimensions réduites (d = 8) sont des modèles jouets pour calculer à la main ; d = 512 est la valeur de l'article d'origine. Les volumes de tokens, les longueurs d'entraînement et les montants non réglementaires sont illustratifs.

### Cas 1 — Agence immobilière à Dubaï : un tableau de 60 transactions ou une ligne JSON par transaction

**Contexte.** Une agence et un promoteur actifs à Dubaï et Abu Dhabi font comparer par un agent 60 transactions récentes enregistrées au DLD : tour, étage, surface en sqft, prix en AED/sqft. Exporté tel quel, le tableau devient du texte aligné par des espaces, d'environ 40 tokens par ligne (volumes illustratifs) ; le modèle ne voit pas les colonnes, seulement des positions. L'équipe se demande si la relation « en-tête prix → valeur de la ligne » est un motif positionnel stable, ou s'il faut changer de format.

**Données.** Dimension jouet d = 8 (fréquences 1 ; 0,1 ; 0,01 ; 0,001). 60 lignes de 40 tokens ; la valeur de prix de la ligne r est à l'écart 40 r + 35 de l'en-tête. Format JSON : la valeur suit la clé `prix_aed_sqft` à un écart constant de 3 tokens. Exemple de bien : 1 180 sqft à 1 450 AED/sqft. Frais de transfert DLD : 4 % de la valeur du bien.

**Calcul pas à pas.**

**Étape 1.** Écarts en-tête → valeur : ligne 1, 40 + 35 = 75 tokens ; ligne 50, 40 × 50 + 35 = 2 035 tokens. Similarités de position (démonstration 3) :

$$
S(75) \approx 2{,}99726, \qquad S(2\,035) \approx -0{,}40969
$$

Sur les 60 lignes, S varie de −2,6953 à 3,50954, soit une amplitude de 6,2048.

**Étape 2.** Format JSON : l'écart clé → valeur vaut 3 sur chaque ligne, donc la similarité vaut toujours

$$
S(3) = \cos 3 + \cos 0{,}3 + \cos 0{,}03 + \cos 0{,}003 \approx 1{,}96489
$$

la même valeur que PE(10) · PE(13) et PE(100) · PE(103), quelle que soit la ligne.

**Étape 3.** Valeur du bien et frais DLD : 1 180 × 1 450 = 1 711 000 AED, et 4 % de ce montant font 68 440 AED.

**Décision de l'agent.** Le tableau aligné donne à la même relation « en-tête → valeur » une signature de position qui change à chaque ligne (amplitude 6,2048), alors que le JSON la fixe (amplitude 0) : l'agent sérialise chaque transaction en une ligne JSON avec des noms de champs explicites, du type `{"tour": "T2", "etage": 31, "surface_sqft": 1180, "prix_aed_sqft": 1450}`. Les frais DLD sont ensuite calculés par un outil, jamais de tête.

**Contre-calcul.** Si le modèle, perdu dans l'alignement, prend la surface pour le prix au sqft, il calcule 1 180 × 1 180 = 1 392 400 AED au lieu de 1 711 000 AED : une erreur de 318 600 AED sur la valeur, et des frais DLD annoncés à 55 696 AED au lieu de 68 440 AED, soit 12 744 AED d'écart sur le budget de l'acheteur, sans aucun message d'erreur.

**Sensibilité.** La plus grande longueur d'onde vaut 2π / 0,001 ≈ 6 283,19 tokens : au-delà de (6 283,19 − 35) / 40 ≈ 156,2, soit 156 lignes, l'écart en-tête → valeur dépasse un tour complet de la paire la plus lente et des lignes éloignées prennent des signatures proches de lignes du haut du tableau. Si les lignes font 44 tokens (+10 %), la bascule tombe à 142 lignes, et la ligne 50 passe à l'écart 44 × 50 + 35 = 2 235, de similarité −2,6953 : la signature change du tout au tout pour une simple variation de mise en page. Le JSON, lui, garde S(3) = 1,96489.

**En production.** L'indicateur suivi est la part des valeurs correctement relues sur un jeu de tableaux de test (alerte sous 99 %, seuil illustratif). Les frais de transfert DLD de 4 % de la valeur du bien sont paramétrés dans l'outil ; les autres frais éventuels sont à confirmer avec le texte en vigueur.

### Cas 2 — Groupe de construction à Dubaï : un contrat de sous-traitance plus long que la fenêtre d'entraînement

**Contexte.** Un groupe de construction qui mène de grands chantiers à Dubaï fait contrôler par un agent les factures de ses sous-traitants contre le contrat de sous-traitance : retenue de garantie, révision des prix, TVA à 5 %. Le contrat fait 80 pages, environ 40 000 tokens (500 par page), alors que le modèle choisi a été entraîné sur des contextes de 8 192 tokens (chiffres illustratifs). L'équipe doit décider si elle envoie le contrat entier ou des morceaux.

**Données.** d = 512 ; contrat de 40 000 tokens ; fenêtre d'entraînement de 8 192 tokens ; chevauchement entre morceaux de 512 tokens (pas de 7 680) ; fréquence la plus lente ω₂₅₅ = 10000^(−510/512) ≈ 1,0366 × 10⁻⁴.

**Calcul pas à pas.**

**Étape 1.** Coordonnée la plus lente, sin(pos ω₂₅₅) : sur les positions 0 à 8 192, elle ne dépasse pas 0,7508 ; en position 16 384 elle vaut 0,9919, et en position 40 000, −0,8441. Elle s'annule vers π / ω₂₅₅ ≈ 30 306 puis devient négative, des valeurs que l'entraînement n'a jamais produites.

**Étape 2.** Paires dont la longueur d'onde tient dans la fenêtre d'entraînement, λᵢ ≤ 8 192 : 200 sur 256. Les 56 autres n'ont jamais fait un tour complet pendant l'entraînement. Part des positions du contrat hors de la fenêtre :

$$
\frac{40\,000 - 8\,192}{40\,000} \approx 79{,}52\ \%
$$

**Étape 3.** Découpage en morceaux de 8 192 tokens qui se chevauchent de 512 :

$$
\left\lceil \frac{40\,000 - 8\,192}{7\,680} \right\rceil + 1 = 5 + 1 = 6 \text{ morceaux}, \qquad 6 \times 8\,192 = 49\,152 \text{ tokens traités}
$$

soit 22,88 % de tokens en plus, mais un calcul d'attention divisé par 40 000² / (6 × 8 192²) ≈ 3,974 (fiche 05, démonstration 4).

**Décision de l'agent.** Comme 40 000 > 8 192, l'agent découpe le contrat en 6 morceaux qui restent dans la fenêtre d'entraînement ; pour chaque ligne de facture, il retrouve par recherche les clauses citées (retenue, révision, TVA) et les place à côté de la ligne contrôlée, au lieu d'envoyer le contrat entier.

**Contre-calcul.** Envoyer le contrat entier place près de 80 % des clauses à des positions où la coordonnée lente prend des valeurs jamais vues ; rien ne garantit alors la qualité de lecture, et le calcul d'attention est près de 4 fois plus lourd. Une clause de retenue de garantie mal lue (par exemple 10 % sur une facture de 600 000 AED, montants illustratifs) fait payer 60 000 AED qui auraient dû être retenus, à récupérer ensuite auprès du sous-traitant.

**Sensibilité.** Si le contrat grossit de 10 % (44 000 tokens), il faut toujours 6 morceaux ; la valeur de bascule vers 7 morceaux est 8 192 + 5 × 7 680 = 46 592 tokens. Le compromis réel : un chevauchement plus grand protège les clauses coupées entre deux morceaux, mais augmente les tokens traités.

**En production.** L'indicateur suivi est la part des écarts signalés par l'agent puis confirmés par l'audit interne, ventilée par position de la clause dans le contrat (début, milieu, fin). La TVA à 5 % est paramétrée dans l'outil de calcul ; le régime de la retenue de garantie relève du contrat et est à confirmer avec le texte en vigueur.

### Cas 3 — Entité de services publics en ligne : un formulaire arabe extrait dans l'ordre visuel

**Contexte.** Une entité de services publics en ligne, accessible par UAE Pass, fait extraire par un agent les champs de formulaires PDF bilingues : nom, Emirates ID, adresse. Certains extracteurs restituent l'arabe dans l'ordre visuel, de gauche à droite, et non dans l'ordre logique de lecture : les tokens arrivent inversés. L'équipe veut savoir ce que l'inversion change pour le modèle, et comment la détecter. Volume : environ 3 000 formulaires par jour (illustratif).

**Données.** Dimension jouet d = 8. Écarts étudiés : k = 1 (tokens voisins, par exemple prénom puis nom du père) et k = 3. Emirates ID d'exemple (format seulement) : 784199012345671, 15 chiffres commençant par 784. Une tête qui « oriente » fait tourner chaque paire d'un quart de tour, J(s ; c) = (c ; −s), et calcule PE(p + k) · J PE(p) = A(k).

**Calcul pas à pas.**

**Étape 1.** Similarités, paires en k (démonstration 3) :

$$
S(1) = S(-1) \approx 3{,}53526, \qquad S(3) = S(-3) \approx 1{,}96489
$$

**Étape 2.** Orientations, impaires en k, parce que sin(−x) = −sin x :

$$
A(1) = \sin 1 + \sin 0{,}1 + \sin 0{,}01 + \sin 0{,}001 \approx 0{,}95230, \qquad A(-1) \approx -0{,}95230, \qquad A(\pm 3) \approx \pm 0{,}46964
$$

**Étape 3.** Contrôle de format : l'ID inversé devient 176543210991487 ; il ne commence plus par 784 et finit par 487.

**Décision de l'agent.** L'inversion ne change rien à la similarité, mais retourne le signe de l'orientation : pour le modèle, « A puis B » devient « B puis A », un texte qu'il n'a pas vu sous cette forme. L'agent remet donc le texte dans l'ordre logique par une étape déterministe avant le modèle, normalise l'arabe (alef, ta marbuta, diacritiques), et lève une alerte quand un champ ID ne commence pas par 784 mais finit par 487.

**Contre-calcul.** Un contrôle fondé sur la similarité de position conclurait que l'inversion est sans effet, puisque S(1) et S(3) sont identiques avant et après : il laisserait passer des noms lus à l'envers, des doublons de dossiers et des usagers obligés de recommencer leur démarche, ce qui fait aussi circuler davantage leurs données personnelles.

**Sensibilité.** La paire rapide seule ne porte le sens de l'écart que tant que sin k > 0, c'est-à-dire pour k < π ≈ 3,14159 : k = 1, 2, 3. Dès k = 4, sin 4 ≈ −0,7568 et, dans ce modèle jouet, A(4) ≈ −0,32339 est déjà négatif dans l'ordre logique : au-delà de quelques tokens, ce sont les paires lentes, nombreuses dans un vrai modèle, qui portent l'orientation.

**En production.** On suit la part des formulaires où le détecteur d'inversion se déclenche, et la part des champs correctement extraits sur des formulaires de référence en arabe et en anglais. Les numéros d'Emirates ID sont contrôlés par du code (format seulement), jamais confiés au modèle ; le traitement de ces données personnelles relève de la PDPL, dont l'application au cas de l'entité est à confirmer avec le texte en vigueur.

### Cas 4 — Cabinet RH multi-émirats : l'ordre des tokens n'est pas l'ordre des événements

**Contexte.** Un cabinet RH multi-émirats fait préparer par un agent l'indemnité de fin de service d'un salarié du secteur privé, à partir de trois documents collés dans le prompt dans l'ordre où ils ont été trouvés : la lettre de fin de contrat de 2023, l'avenant de 2019, puis le contrat initial de 2016, juste avant la question. Le salaire de base a changé en 2019. Le cabinet traite environ 400 départs par an (illustratif).

**Données.** d = 512. Écarts entre la question et chaque document : lettre 2023 à 9 500 tokens, avenant 2019 à 4 000 tokens, contrat 2016 à 500 tokens. Salaire de base : 8 000 AED dans le contrat de 2016, 10 000 AED depuis l'avenant de 2019. Service : du 1er mars 2016 au 1er mars 2023, soit 7 ans. Règle du guide : 21 jours de salaire de base par an les 5 premières années, 30 jours au-delà, salaire journalier = base / 30, au moins 1 an de service, plafond de 24 mois.

**Calcul pas à pas.**

**Étape 1.** Similarités de position entre la question et chaque document (démonstration 3) :

$$
S(9\,500) \approx -7{,}441, \qquad S(4\,000) \approx 11{,}602, \qquad S(500) \approx 67{,}233
$$

Le document le plus « proche » en tokens est le contrat de 2016, le plus ancien.

**Étape 2.** Indemnité due, avec le salaire de base de 10 000 AED :

$$
\frac{10\,000}{30} \times (21 \times 5 + 30 \times 2) = \frac{10\,000}{30} \times 165 = 55\,000 \text{ AED}
$$

**Étape 3.** Deux lectures fausses : avec la base de 2016, 8 000 / 30 × 165 = 44 000 AED ; avec une date d'entrée lue dans l'avenant (2019, donc 4 ans), 10 000 / 30 × 21 × 4 = 28 000 AED.

**Décision de l'agent.** L'encodage ne donne au modèle que des distances en tokens, et la plus courte désigne ici le document le plus ancien : rien dans l'encodage ne dit que l'avenant de 2019 est plus récent que le contrat. L'agent extrait donc d'abord chaque document avec sa date par un outil, trie les événements, et présente au modèle une frise numérotée et datée ; le calcul est fait par une fonction déterministe à partir de la date d'entrée et du salaire de base en vigueur au départ.

**Contre-calcul.** Avec la base de 2016, l'indemnité annoncée serait de 44 000 AED, 11 000 AED de moins que le dû ; avec la date de l'avenant, 28 000 AED, 27 000 AED de moins. Une indemnité sous-évaluée expose l'employeur à une réclamation du salarié devant le MOHRE.

**Sensibilité.** La valeur de bascule de la règle est 5 ans de service : à 5 ans, l'indemnité vaut 10 000 / 30 × 105 = 35 000 AED ; chaque année au-delà ajoute 30 jours, soit 10 000 AED (45 000 AED à 6 ans, 55 000 AED à 7 ans). Sous 1 an de service, il n'y a pas d'indemnité. Le plafond de 24 mois de salaire de base (240 000 AED) n'est pas atteint.

**En production.** L'indicateur suivi est l'écart entre les indemnités proposées par l'agent et celles validées par le service paie (objectif : zéro). Le régime cité est celui du secteur privé (décret-loi fédéral 33/2021) ; les ressortissants émiriens relèvent de la GPSSA et le DIFC a son propre régime : l'outil vérifie le régime avant de calculer, et la base à retenir dans les cas particuliers est à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Avec d = 4, écrire PE(0).

**Exercice 2.** Avec d = 8, calculer ω₁ et la longueur d'onde de la paire 1.

**Exercice 3.** Démontrer que PE(p) · PE(p) = d/2 avec la démonstration 3.

**Exercice 4.** Avec d = 2 (une seule paire, ω = 1), calculer PE(2) · PE(5).

**Exercice 5.** Pourquoi deux mêmes tokens, à des positions différentes, n'ont-ils plus la même entrée dans le Transformer ?

**Exercice 6 (cas modifié).** Dans le cas 2, le modèle n'a été entraîné que sur 4 096 tokens (chevauchement toujours de 512). Combien de morceaux faut-il pour le contrat de 40 000 tokens, combien de tokens sont traités, par combien le calcul d'attention est-il divisé, et combien de paires sur 256 ont fait un tour complet pendant l'entraînement ?

**Exercice 7 (trouver l'erreur).** Un collègue calcule PE(1) pour d = 4 et trouve (sin 1 ; cos 1 ; sin 100 ; cos 100) ≈ (0,84147 ; 0,54030 ; −0,50637 ; 0,86232). Trouver l'erreur et donner la bonne valeur.

**Exercice 8 (redémontrer de mémoire).** Redémontrer, sans regarder, que décaler une position de k revient à multiplier chaque paire par une rotation qui ne dépend pas de la position.

## Corrigé

**Exercice 1.** Toutes les phases valent 0 × ωᵢ = 0, donc PE(0) = (sin 0 ; cos 0 ; sin 0 ; cos 0) = (0 ; 1 ; 0 ; 1).

**Exercice 2.** ω₁ = 10000^(−2/8) = 10000^(−1/4) = 1/10 = 0,1 ; longueur d'onde 2π / 0,1 = 20π ≈ 62,83 tokens.

**Exercice 3.** Avec p = q, l'écart vaut 0 ; chaque terme de la somme de la démonstration 3 vaut cos 0 = 1, et il y a d/2 termes : PE(p) · PE(p) = d/2. Pour d = 8, cela fait 4 (le programme trouve 4,0 pour p = 9).

**Exercice 4.** La démonstration 3 donne cos((2 − 5) × 1) = cos(−3) = cos 3 ≈ −0,98999. On le retrouve directement : sin 2 sin 5 + cos 2 cos 5 = cos(5 − 2).

**Exercice 5.** L'entrée de la première couche est X = E_w + PE(pos) : l'embedding du token est le même, mais PE dépend de la position, donc la somme diffère. Sans ce terme, l'attention ne verrait pas l'ordre (fiche 05, démonstration 3).

**Exercice 6.** Pas : 4 096 − 512 = 3 584. Morceaux : ⌈(40 000 − 4 096) / 3 584⌉ + 1 = ⌈10,02⌉ + 1 = 11 + 1 = 12. Tokens traités : 12 × 4 096 = 49 152. Attention divisée par 40 000² / (12 × 4 096²) ≈ 7,95. Paires de longueur d'onde ≤ 4 096 : 181 sur 256 (le programme les compte). Le découpage est plus fin, moins coûteux en attention, mais coupe plus de clauses en deux.

**Exercice 7.** L'erreur est le signe de l'exposant : le collègue a utilisé 10000^(+2i/d), soit 10000^(2/4) = 100, au lieu de ω₁ = 10000^(−2/4) = 0,01. La paire 1, qui devait être lente, devient 100 fois plus rapide que la paire 0, et il n'y a plus d'onde lente. Bonne valeur : (sin 1 ; cos 1 ; sin 0,01 ; cos 0,01) ≈ (0,84147 ; 0,54030 ; 0,01000 ; 0,99995).

**Exercice 8.** Étape 1 : on pose a = pos ωᵢ et b = k ωᵢ. Étape 2 : sin(a + b) = cos b sin a + sin b cos a et cos(a + b) = −sin b sin a + cos b cos a. Étape 3 : ces deux lignes sont le produit de la matrice [[cos b ; sin b] ; [−sin b ; cos b]] par (sin a ; cos a). Étape 4 : b = k ωᵢ ne dépend pas de pos, donc la même matrice R(k ωᵢ) décale toutes les positions ; empilée sur les paires, elle donne Tₖ. ∎

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`omega(i, d)`** — Cette fonction est l'horloger qui règle la vitesse de chacune des aiguilles de l'encodage : elle reçoit le numéro `i` d'une paire de coordonnées et la dimension `d` du vecteur, et renvoie la fréquence ωᵢ = 10000 puissance (−2i/d), exprimée en radians par token. La paire 0 tourne toujours à 1 radian par token, et chaque paire suivante tourne plus lentement : en dimension 8, les fréquences valent 1, 0,1, 0,01 et 0,001, et en dimension 4 la seconde vaut 0,01 ; `similarite_ecart`, `orientation_ecart`, `rope` et les quatre cas en dépendent tous.

**`pe(pos, d)`** — Celle-ci fabrique le badge de position qu'on agrafe à chaque token avant qu'il entre dans le Transformer : elle reçoit la position `pos` et la dimension `d`, refuse par une `ValueError` toute dimension impaire ou inférieure à 2, puisque les coordonnées vont par paires, puis, pour chaque paire i, calcule la même fréquence que `omega` et ajoute au vecteur le sinus et le cosinus de pos × ωᵢ. Elle renvoie la liste des d coordonnées, par exemple (0 ; 1 ; 0 ; 1) pour la position 0 et (0,84147 ; 0,5403 ; 0,01 ; 0,99995) pour la position 1 en dimension 4 ; chaque paire est un point du cercle unité, ce qui donne la norme constante √(d/2) de la démonstration 1.

**`dot(a, b)`** — Cette petite fonction est la règle à calcul du programme : elle reçoit deux vecteurs de même longueur, multiplie leurs coordonnées deux à deux et renvoie la somme de ces produits, c'est-à-dire leur produit scalaire. Elle sert à vérifier que la norme de PE vaut 2 en dimension 8, que PE(10) · PE(13) et PE(100) · PE(103) valent tous deux 1,96489 parce que seul l'écart compte, et à calculer les scores d'attention de la démonstration 6, avec et sans encodage rotatif.

**`similarite_ecart(k, d)`** — Cette fonction répond, sans même connaître les positions, à la question qu'un géomètre poserait à deux badges distants de `k` tokens : elle reçoit l'écart `k` et la dimension `d` et renvoie la somme des cos(k ωᵢ) sur toutes les paires, qui est exactement le produit scalaire PE(p) · PE(p + k) pour n'importe quelle position p, comme le prouve la démonstration 3. Elle donne 1,96489 pour un écart de 3 en dimension 8 et 3,53526 pour un écart de 1, et sa valeur est la même pour k et −k ; les cas 1, 3 et 4 l'utilisent pour mesurer à quel point l'en-tête et la valeur d'un tableau, ou la question et un document, se « ressemblent » en position.

**`orientation_ecart(k, d)`** — Là où la fonction précédente ne voit qu'une distance, celle-ci est la girouette qui indique aussi le sens : elle reçoit l'écart `k` et la dimension `d` et renvoie la somme des sin(k ωᵢ), qui est le produit scalaire PE(p + k) · J PE(p) lorsque J fait tourner chaque paire d'un quart de tour. Comme le sinus est impair, le résultat change de signe avec k : 0,9523 pour k = 1 et −0,9523 pour k = −1, 0,46964 pour k = 3 en dimension 8 ; le cas 3 s'en sert pour montrer qu'un texte arabe restitué à l'envers est vu par le modèle avec l'orientation inversée.

**`tourner(paire, theta)`** — On peut l'imaginer comme un aiguilleur qui fait pivoter un levier d'un angle donné : elle reçoit une paire (x ; y) et un angle `theta`, applique la matrice de rotation R(θ), de lignes (cos θ ; sin θ) et (−sin θ ; cos θ), et renvoie la nouvelle paire (cos θ x + sin θ y ; −sin θ x + cos θ y). Elle illustre la démonstration 2, où faire tourner chaque paire de PE(2) de 3 ωᵢ redonne exactement PE(5), et elle sert de brique à `rope` ainsi qu'au calcul direct q · R(3) k de la démonstration 6.

**`rope(v, pos, d)`** — Cette fonction remplace le badge agrafé par une boussole qu'on fait tourner : au lieu d'ajouter PE au vecteur, elle reçoit un vecteur `v`, sa position `pos` et la dimension `d`, découpe `v` en paires et fait tourner la paire i de l'angle pos × ωᵢ grâce à `tourner`. Elle renvoie le vecteur ainsi tourné, l'encodage rotatif dit RoPE ; dans la démonstration 6, le score entre une requête tournée de 2 et une clé tournée de 5 vaut −0,4811, exactement comme entre 10 et 13, alors que l'addition de PE donne −1,13626 puis −0,9675, ce qui montre qu'avec la rotation seul l'écart compte.

**`r5(xs)`** — Cette petite fonction est le greffier qui recopie les coordonnées au propre : elle reçoit une liste de nombres et renvoie une nouvelle liste où chacun est arrondi à cinq décimales. Elle ne calcule rien de nouveau, mais elle permet aux `assert` de `main` de comparer des vecteurs comme PE(2) = [0,9093 ; −0,41615 ; 0,02 ; 0,9998] ou des cosinus comme [−0,98999 ; 0,95534 ; 0,99955 ; 1,0] aux valeurs de la fiche sans être gênés par les derniers chiffres flottants.

**`cas_1_tableau_immo()`** — Une agence immobilière hésite entre envoyer au modèle un tableau de 60 transactions, où le prix de la ligne r se trouve à 40 r + 35 tokens de l'en-tête, et une ligne JSON par transaction, où la valeur suit sa clé à 3 tokens : la fonction calcule, en dimension 8, la similarité de position de chacun des 60 écarts, qui va de −2,6953 à 3,50954, alors qu'en JSON elle reste fixée à 1,96489. Elle calcule aussi la plus grande longueur d'onde, 6 283,19 tokens, et le nombre de lignes au-delà duquel le tableau la dépasse, 156 lignes de 40 tokens ou 142 de 44, puis chiffre le risque d'une confusion entre la surface et le prix pour un bien de 1 180 sqft à 1 450 AED/sqft : la vraie valeur de 1 711 000 AED tomberait à 1 392 400 AED si le modèle lisait la surface à la place du prix, et les frais de transfert de 4 % passeraient de 68 440 à 55 696 AED. Elle renvoie ces grandeurs et la décision « une ligne JSON par transaction », car la similarité varie de 6,2048 sur le tableau.

**`cas_2_contrat_btp()`** — Cette fonction suit un groupe de construction qui veut faire lire un contrat de 40 000 tokens à un modèle entraîné sur 8 192 : en dimension 512, elle calcule la fréquence de la paire la plus lente, montre que sa coordonnée sinus n'a jamais dépassé 0,7508 pendant l'entraînement alors qu'elle vaut −0,8441 à la position 40 000, et compte les paires dont la longueur d'onde tient dans la fenêtre d'entraînement, 200 sur 256. Avec un chevauchement de 512 tokens, donc un pas de 7 680, sa fonction interne `morceaux` donne 6 morceaux, soit 49 152 tokens traités, 22,88 % de plus que le contrat, pour un calcul d'attention divisé par 3,974 ; elle calcule aussi la longueur de bascule, 46 592 tokens, au-delà de laquelle il faudrait 7 morceaux, et vérifie qu'un contrat plus long de 10 % tient encore en 6. Elle renvoie ces résultats, la fonction `morceaux` elle-même et la décision « découper en 6 morceaux ».

**`morceaux(n, fenetre, pas_)`** — Cette fonction interne vit dans `cas_2_contrat_btp` et y joue le rôle d'un relieur qui découpe un long registre en cahiers qui se chevauchent : elle reçoit la longueur `n` du document, la taille de la `fenetre`, 8 192 tokens par défaut, et le pas `pas_` entre deux débuts de morceau, 7 680 par défaut, et renvoie le nombre de morceaux, l'arrondi supérieur de (n − fenêtre) / pas, augmenté de 1. Elle donne 6 pour 40 000 tokens et pour 44 000, 7 dès 46 593, et le corrigé de l'exercice 6 la rappelle avec une fenêtre de 4 096 et un pas de 3 584 pour trouver 12 morceaux.

**`cas_3_formulaire_public()`** — Un service public en ligne fait extraire des formulaires bilingues dont l'arabe arrive parfois dans l'ordre visuel, donc inversé : la fonction calcule, en dimension 8, la similarité et l'orientation de position pour les écarts 1, 3, −1, −3 et 4, et montre que la similarité est la même dans les deux sens, 3,53526 pour k = ±1, tandis que l'orientation change de signe, 0,9523 contre −0,9523. Elle relève aussi les écarts de 1 à 7 où la paire rapide a un sinus positif, dont les trois premiers sont 1, 2 et 3, puis prend un numéro d'identité fictif de 15 chiffres commençant par 784, le renverse et constate que la version inversée ne commence plus par 784 ; elle renvoie ces résultats et la décision « remise en ordre logique avant le modèle », avec une alerte sur tout numéro qui finit par 487.

**`cas_4_frise_rh()`** — Cette fonction raconte un cabinet RH qui a collé dans le prompt, dans l'ordre où il les a trouvés, la lettre de fin de contrat de 2023, l'avenant de 2019 et le contrat initial de 2016, ce dernier juste avant la question : en dimension 512, elle calcule la similarité de position entre la question et chaque document, à 9 500, 4 000 et 500 tokens, soit −7,441, 11,602 et 67,233, si bien que le document le plus proche en tokens est le plus ancien. Sa fonction interne `indemnite` chiffre alors l'indemnité de fin de service due pour 7 ans à 10 000 AED, 55 000 AED, contre 44 000 AED si l'on retient l'ancienne base de 8 000 AED et 28 000 AED si l'on prend 2019 comme date d'entrée ; elle renvoie les similarités, le document le plus proche, la fonction `indemnite`, ces trois montants et la décision « frise datée triée par outil ».

**`indemnite(base, annees)`** — Cette fonction interne vit dans `cas_4_frise_rh` et y joue le rôle du calculateur de paie qui applique la règle du guide : elle reçoit le salaire de base mensuel et le nombre d'années de service, renvoie 0 si le salarié a moins d'un an d'ancienneté, et sinon multiplie le salaire journalier, base / 30, par 21 jours pour chacune des 5 premières années et par 30 jours pour chaque année au-delà. Elle donne 35 000 AED pour 5 ans et 45 000 AED pour 6 ans à 10 000 AED, et 55 000 AED pour 7 ans ; le plafond de 24 mois n'est pas appliqué dans la fonction, il est vérifié à part par un `assert` de `main`.

**`main()`** — C'est le banc d'essai qui rejoue la fiche dans l'ordre de lecture : il affiche le film des badges PE(0), PE(1) et PE(2) en dimension 4, vérifie que la norme reste égale à 2 en dimension 8 quelle que soit la position, alors qu'une dimension impaire ferait varier le carré de la norme de 2 à 2,9076 et est refusée par `pe`, puis que décaler de 3 revient à faire tourner chaque paire. Il montre que PE(10) · PE(13) = PE(100) · PE(103) = 1,96489 alors que les sinus seuls ne le permettent pas, retrouve les longueurs d'onde de 6,28 à 6 283,19 tokens en progression de raison 10, mesure les distances entre positions grâce à sa fonction interne `dist` et compare RoPE à l'addition ; il lance ensuite les quatre cas et refait le corrigé, chaque nombre étant confronté par un `assert` à la fiche, et la dernière ligne n'annonce le succès que si tous concordent.

**`dist(g, d)`** — Cette fonction interne vit dans `main`, dans la partie de la démonstration 5, et y sert d'arpenteur qui mesure l'écart entre deux badges de position sans avoir besoin de les fabriquer : elle reçoit l'écart `g` en tokens et la dimension `d`, additionne sur toutes les paires 4 sin²(g ωᵢ / 2), qui est le carré de la corde entre deux points du cercle unité séparés de l'angle g ωᵢ, et renvoie la racine carrée de cette somme. Son carré vaut 8 − 2 × 1,96489 = 4,07022 pour un écart de 3 en dimension 8, la même valeur que `math.dist` entre PE(10) et PE(13) ; en dimension 2, elle révèle le repliement d'une seule paire, puisqu'un écart de 44, presque 7 tours complets, ne donne qu'une distance de 0,0177.

```python
"""Démonstration 30 — encodage de position : cercle unité, rotation, écart relatif, longueurs d'onde, distance, RoPE, quatre cas aux EAU."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def omega(i: int, d: int) -> float:
    """Fréquence de la paire i : ω_i = 10000^(−2i/d), en radians par token."""
    return 10000 ** (-2 * i / d)


def pe(pos, d):
    """PE(pos) = (sin(pos ω_0), cos(pos ω_0), sin(pos ω_1), cos(pos ω_1), …) ; d doit être pair."""
    if d < 2 or d % 2:
        raise ValueError("d doit être un entier pair ≥ 2")
    v = []
    for i in range(d // 2):
        w = 10000 ** (-2 * i / d)
        v += [math.sin(pos * w), math.cos(pos * w)]
    return v


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def similarite_ecart(k: float, d: int) -> float:
    """PE(p) · PE(p + k) = Σ cos(k ω_i) : ne dépend que de l'écart k."""
    return sum(math.cos(k * omega(i, d)) for i in range(d // 2))


def orientation_ecart(k: float, d: int) -> float:
    """PE(p + k) · J PE(p) = Σ sin(k ω_i), où J fait tourner chaque paire d'un quart de tour : change de signe avec k."""
    return sum(math.sin(k * omega(i, d)) for i in range(d // 2))


def tourner(paire, theta):
    """R(θ) = [[cos θ, sin θ], [−sin θ, cos θ]] appliquée à une paire (x ; y)."""
    x, y = paire
    return (math.cos(theta) * x + math.sin(theta) * y, -math.sin(theta) * x + math.cos(theta) * y)


def rope(v, pos, d):
    """Encodage rotatif : chaque paire de v tourne de l'angle pos × ω_i (au lieu d'ajouter PE)."""
    out = []
    for i in range(d // 2):
        out += list(tourner((v[2 * i], v[2 * i + 1]), pos * omega(i, d)))
    return out


def r5(xs):
    return [round(x, 5) for x in xs]


def cas_1_tableau_immo():
    """Immobilier : en-tête « prix » et valeur de la ligne r d'un tableau aligné (écart 40 r + 35) contre un JSON (écart 3)."""
    d, lignes, par_ligne, decalage, ecart_json = 8, 60, 40, 35, 3
    ecarts = [par_ligne * r + decalage for r in range(1, lignes + 1)]
    sims = [similarite_ecart(g, d) for g in ecarts]
    lam_max = 2 * math.pi / omega(d // 2 - 1, d)
    lignes_bascule = math.floor((lam_max - decalage) / par_ligne)
    lignes_bascule_44 = math.floor((lam_max - decalage) / 44)
    surface, prix_sqft = 1180, 1450
    valeur, valeur_confondue = surface * prix_sqft, surface * surface
    print(f"cas 1 IMMO : S(75) = {sims[0]:.5f} ; S(2035) = {sims[49]:.5f} ; sur 60 lignes S dans [{min(sims):.4f} ; {max(sims):.5f}] ;"
          f" JSON S(3) = {similarite_ecart(ecart_json, d):.5f}")
    print(f"  λ max {lam_max:.2f} tokens -> bascule {lignes_bascule} lignes ({lignes_bascule_44} à 44 tokens) ;"
          f" valeur {valeur:,} AED, confondue {valeur_confondue:,} AED, frais DLD {0.04 * valeur:,.0f} contre {0.04 * valeur_confondue:,.0f}")
    decision = "une ligne JSON par transaction" if max(sims) - min(sims) > 0.1 else "tableau aligné"
    print(f"  décision : {decision} (S varie de {max(sims) - min(sims):.4f} sur le tableau, 0 en JSON)")
    return sims, lam_max, lignes_bascule, lignes_bascule_44, valeur, valeur_confondue, decision


def cas_2_contrat_btp():
    """BTP : contrat de 40 000 tokens, modèle entraîné sur 8 192 ; coordonnée lente, paires vues, découpage."""
    d, n_contrat, n_entr, chevauchement = 512, 40000, 8192, 512
    w_lent = omega(d // 2 - 1, d)
    max_entr = max(math.sin(p * w_lent) for p in range(n_entr + 1))
    paires_vues = sum(2 * math.pi / omega(i, d) <= n_entr for i in range(d // 2))
    pas = n_entr - chevauchement

    def morceaux(n, fenetre=n_entr, pas_=pas):
        return math.ceil((n - fenetre) / pas_) + 1

    nb = morceaux(n_contrat)
    traites = nb * n_entr
    rapport_attention = n_contrat ** 2 / (nb * n_entr ** 2)
    bascule = n_entr + (nb - 1) * pas
    print(f"cas 2 BTP : coordonnée lente max {max_entr:.4f} sur [0 ; 8192], {math.sin(n_contrat * w_lent):.4f} en 40 000 ;"
          f" paires vues en entier {paires_vues}/256 ; part des positions hors entraînement {(n_contrat - n_entr) / n_contrat:.2%}")
    print(f"  {nb} morceaux, {traites:,} tokens traités (+{traites / n_contrat - 1:.2%}) ; attention ÷ {rapport_attention:.3f} ;"
          f" bascule à 7 morceaux : {bascule:,} tokens ; contrat + 10 % : {morceaux(44000)} morceaux")
    decision = f"découper en {nb} morceaux" if n_contrat > n_entr else "contrat entier"
    print(f"  décision : {n_contrat} > {n_entr} -> {decision}, clauses citées récupérées par recherche")
    return max_entr, w_lent, paires_vues, nb, traites, rapport_attention, bascule, morceaux, decision


def cas_3_formulaire_public():
    """Secteur public : texte arabe inversé ; la similarité est paire en k, l'orientation est impaire."""
    d = 8
    res = {k: (similarite_ecart(k, d), orientation_ecart(k, d)) for k in (1, 3, -1, -3, 4)}
    signe_rapide = [k for k in range(1, 8) if math.sin(k) > 0]
    eid = "784199012345671"
    inverse = eid[::-1]
    print(f"cas 3 PUBLIC : k = 1 : S {res[1][0]:.5f}, A {res[1][1]:.5f} ; k = −1 : S {res[-1][0]:.5f}, A {res[-1][1]:.5f} ;"
          f" k = ±3 : S {res[3][0]:.5f}, A ±{res[3][1]:.5f}")
    print(f"  paire rapide de signe positif pour k = {signe_rapide[:3]} ; A(4) = {res[4][1]:.5f} ;"
          f" ID {eid} ({len(eid)} chiffres) inversé {inverse} : commence par 784 ? {inverse.startswith('784')}")
    decision = "remise en ordre logique avant le modèle" if not inverse.startswith("784") else "aucune"
    print(f"  décision : {decision} ; alerte si l'ID ne commence pas par 784 et finit par 487")
    return res, signe_rapide, eid, inverse, decision


def cas_4_frise_rh():
    """RH : documents collés dans l'ordre de découverte ; proximité en tokens contre chronologie ; indemnité."""
    d = 512
    ecarts = {"lettre 2023": 9500, "avenant 2019": 4000, "contrat 2016": 500}
    sims = {nom: similarite_ecart(g, d) for nom, g in ecarts.items()}
    plus_proche = max(sims, key=sims.get)

    def indemnite(base, annees):
        if annees < 1:
            return 0.0
        return base / 30 * (21 * min(annees, 5) + 30 * max(annees - 5, 0))

    due = indemnite(10000, 7)
    base_ancienne = indemnite(8000, 7)
    date_avenant = indemnite(10000, 4)
    print(f"cas 4 RH : S(9500) = {sims['lettre 2023']:.3f}, S(4000) = {sims['avenant 2019']:.3f}, S(500) = {sims['contrat 2016']:.3f}"
          f" ; plus proche en tokens : {plus_proche}")
    print(f"  indemnité due {due:,.0f} AED ; base 2016 : {base_ancienne:,.0f} ; entrée lue en 2019 : {date_avenant:,.0f} ;"
          f" 5 ans {indemnite(10000, 5):,.0f}, 6 ans {indemnite(10000, 6):,.0f}")
    decision = "frise datée triée par outil" if plus_proche != "lettre 2023" else "ordre de découverte"
    print(f"  décision : {decision} ; écart évité {due - base_ancienne:,.0f} AED (base) ou {due - date_avenant:,.0f} AED (date)")
    return sims, plus_proche, indemnite, due, base_ancienne, date_avenant, decision


def main() -> None:
    # Film et exemple simple
    film = [pe(p, 4) for p in (0, 1, 2)]
    print(f"film d = 4 : PE(0) {r5(film[0])} ; PE(1) {r5(film[1])} ; PE(2) {r5(film[2])}")
    assert r5(film[0]) == [0.0, 1.0, 0.0, 1.0] and r5(film[2]) == [0.9093, -0.41615, 0.02, 0.9998]
    p1 = pe(1, 4)
    print(f"PE(1), d = 4 : {[round(x, 5) for x in p1]}")
    assert [round(x, 5) for x in p1] == [0.84147, 0.5403, 0.01, 0.99995] and omega(1, 4) == 0.01

    # Démonstration 1 : cercle unité, norme √(d/2) ; contre-exemple d impair
    for pos in (0, 7, 512, 4096):
        assert math.isclose(math.sqrt(dot(pe(pos, 8), pe(pos, 8))), 2.0)       # ‖PE‖ = √(d/2)
    w_imp = 10000 ** (-4 / 5)
    n2_impair = [2 + math.sin(pos * w_imp) ** 2 for pos in (0, 2000)]
    print(f"démo 1 : ‖PE‖ = 2 pour d = 8 ; d = 5 : ‖PE‖² = {n2_impair[0]:.4f} en 0, {n2_impair[1]:.4f} en 2000")
    assert n2_impair[0] == 2.0 and round(n2_impair[1], 4) == 2.9076 and round(w_imp, 6) == 0.000631
    try:
        pe(3, 5)
    except ValueError:
        pass
    else:
        raise AssertionError("une dimension impaire aurait dû être refusée")

    # Démonstration 2 : un décalage de k est une rotation de chaque paire
    oms = [10000 ** (-2 * i / 8) for i in range(4)]
    w, pos, k = oms[1], 17, 5                                                    # rotation de la paire 1
    s, c = math.sin(pos * w), math.cos(pos * w)
    rot = (math.cos(k * w) * s + math.sin(k * w) * c, -math.sin(k * w) * s + math.cos(k * w) * c)
    assert math.isclose(rot[0], math.sin((pos + k) * w)) and math.isclose(rot[1], math.cos((pos + k) * w))
    pe2, pe5 = pe(2, 4), pe(5, 4)
    t3pe2 = list(tourner(pe2[:2], 3 * omega(0, 4))) + list(tourner(pe2[2:], 3 * omega(1, 4)))
    print(f"démo 2 : PE(2) {[round(x, 6) for x in pe2]} ; T3·PE(2) = {[round(x, 6) for x in t3pe2]} = PE(5)")
    assert all(math.isclose(a, b, abs_tol=1e-12) for a, b in zip(t3pe2, pe5))
    assert [round(x, 6) for x in pe2] == [0.909297, -0.416147, 0.019999, 0.9998] and round(math.sin(5), 6) == -0.958924
    assert round(math.cos(3), 6) == -0.989992 and round(math.sin(3), 6) == 0.14112
    assert round(-0.989992 * 0.909297, 6) == -0.900197 and round(0.141120 * -0.416147, 6) == -0.058727
    assert round(math.sin(1), 5) == round(math.sin(math.pi - 1), 5) == 0.84147
    assert round(math.sin(2), 5) == 0.9093 and round(math.sin(math.pi), 5) == 0.0          # sin seul ne suffit pas

    # Démonstration 3 : produit scalaire et écart ; contre-exemple « sinus seuls »
    a, b = dot(pe(10, 8), pe(13, 8)), dot(pe(100, 8), pe(103, 8))
    print(f"PE(10)·PE(13) = {a:.5f} ; PE(100)·PE(103) = {b:.5f}")
    assert round(a, 5) == 1.96489 and abs(a - b) < 1e-6
    assert math.isclose(a, sum(math.cos(3 * w) for w in oms))
    s1, s2 = math.sin(10) * math.sin(13), math.sin(100) * math.sin(103)
    print(f"démo 3 : sinus seuls : sin 10 · sin 13 = {s1:.5f} ; sin 100 · sin 103 = {s2:.5f}")
    assert round(s1, 5) == -0.22858 and round(s2, 5) == -0.31546
    assert r5([math.cos(3), math.cos(0.3), math.cos(0.03), math.cos(0.003)]) == [-0.98999, 0.95534, 0.99955, 1.0]

    # Démonstration 4 : longueurs d'onde en progression géométrique
    ondes = [2 * math.pi / w for w in oms]
    print(f"fréquences {[round(w, 3) for w in oms]} ; longueurs d'onde {[round(x, 2) for x in ondes]}")
    assert [round(w, 3) for w in oms] == [1.0, 0.1, 0.01, 0.001]
    assert [round(x, 2) for x in ondes] == [6.28, 62.83, 628.32, 6283.19]
    assert all(math.isclose(ondes[i + 1] / ondes[i], 10) for i in range(3))
    assert round(10000 ** (2 / 512), 5) == 1.03663 and round(2 * math.pi * 10000 ** (510 / 512)) == 60611

    # Démonstration 5 : distance entre positions ; repliement d'une seule paire
    def dist(g, d):
        return math.sqrt(sum(4 * math.sin(g * omega(i, d) / 2) ** 2 for i in range(d // 2)))

    assert math.isclose(dist(3, 8) ** 2, 8 - 2 * a) and round(8 - 2 * a, 5) == 4.07022
    assert math.isclose(dist(3, 8), math.dist(pe(10, 8), pe(13, 8)))
    tab = {(g, d): dist(g, d) for g in (1, 6, 44) for d in (2, 4, 8)}
    print(f"démo 5 : d = 2 : écart 1 -> {tab[(1, 2)]:.5f}, 6 -> {tab[(6, 2)]:.5f}, 44 -> {tab[(44, 2)]:.4f} ;"
          f" écart 44 : d = 4 -> {tab[(44, 4)]:.5f}, d = 8 -> {tab[(44, 8)]:.5f}")
    assert round(tab[(1, 2)], 5) == 0.95885 and round(tab[(6, 2)], 5) == 0.28224 and round(tab[(44, 2)], 4) == 0.0177
    assert round(tab[(44, 4)], 5) == 0.43682 and round(tab[(44, 8)], 5) == 1.67553 and round(7 * 2 * math.pi, 2) == 43.98

    # Démonstration 6 : avec des rotations (RoPE), le score ne dépend que de l'écart
    q, kv = [1.0, 0.0], [0.6, 0.8]
    sc_a = dot(rope(q, 2, 2), rope(kv, 5, 2))
    sc_b = dot(rope(q, 10, 2), rope(kv, 13, 2))
    direct = dot(q, tourner(kv, 3.0))
    add_a = dot([x + y for x, y in zip(q, pe(2, 2))], [x + y for x, y in zip(kv, pe(5, 2))])
    add_b = dot([x + y for x, y in zip(q, pe(10, 2))], [x + y for x, y in zip(kv, pe(13, 2))])
    print(f"démo 6 : RoPE (2, 5) {sc_a:.5f}, (10, 13) {sc_b:.5f}, q·R(3)k {direct:.5f} ; addition (2, 5) {add_a:.5f}, (10, 13) {add_b:.5f}")
    assert math.isclose(sc_a, sc_b) and math.isclose(sc_a, direct) and round(direct, 5) == -0.4811
    assert round(add_a, 5) == -1.13626 and round(add_b, 5) == -0.9675
    assert round(0.6 * math.cos(3), 5) == -0.594 and round(0.8 * math.sin(3), 5) == 0.1129

    # Cas
    sims1, lam_max, lb, lb44, valeur, confondue, dec1 = cas_1_tableau_immo()
    assert dec1 == "une ligne JSON par transaction" and round(max(sims1) - min(sims1), 4) == 6.2048
    assert round(sims1[0], 5) == 2.99726 and round(sims1[49], 5) == -0.40969
    assert round(min(sims1), 4) == -2.6953 and round(max(sims1), 5) == 3.50954 and round(lam_max, 2) == 6283.19
    assert lb == 156 and lb44 == 142 and 40 * 50 + 35 == 2035 and 40 + 35 == 75
    assert valeur == 1_711_000 and confondue == 1_392_400 and valeur - confondue == 318_600
    assert round(0.04 * valeur) == 68_440 and round(0.04 * confondue) == 55_696 and round(0.04 * (valeur - confondue)) == 12_744
    assert 44 * 50 + 35 == 2235 and round(similarite_ecart(2235, 8), 4) == -2.6953

    max_entr, w_lent, pv, nb, traites, rapp, bascule, morceaux, dec2 = cas_2_contrat_btp()
    assert dec2 == "découper en 6 morceaux"
    assert round(max_entr, 4) == 0.7508 and round(math.sin(40000 * w_lent), 4) == -0.8441 and pv == 200
    assert round((40000 - 8192) / 40000, 4) == 0.7952 and nb == 6 and traites == 49152 and round(traites / 40000 - 1, 4) == 0.2288
    assert round(rapp, 3) == 3.974 and bascule == 46592 and morceaux(44000) == 6 and morceaux(46593) == 7
    assert round(math.sin(16384 * w_lent), 4) == 0.9919 and round(math.pi / w_lent) == 30306 and 80 * 500 == 40000

    res3, sr, eid, inv, dec3 = cas_3_formulaire_public()
    assert dec3 == "remise en ordre logique avant le modèle"
    assert round(res3[1][0], 5) == round(res3[-1][0], 5) == 3.53526 and round(res3[1][1], 5) == 0.9523 == -round(res3[-1][1], 5)
    assert round(res3[3][0], 5) == 1.96489 and round(res3[3][1], 5) == 0.46964 and round(res3[-3][1], 5) == -0.46964
    assert sr[:3] == [1, 2, 3] and round(res3[4][1], 5) == -0.32339 and round(math.sin(4), 5) == -0.7568
    assert len(eid) == 15 and eid.startswith("784") and not inv.startswith("784") and inv.endswith("487")
    assert round(math.pi, 5) == 3.14159 and r5([math.sin(1), math.sin(0.1), math.sin(0.01)]) == [0.84147, 0.09983, 0.01]

    sims4, proche, indemnite, due, base_anc, date_av, dec4 = cas_4_frise_rh()
    assert dec4 == "frise datée triée par outil"
    assert round(sims4["lettre 2023"], 3) == -7.441 and round(sims4["avenant 2019"], 3) == 11.602
    assert round(sims4["contrat 2016"], 3) == 67.233 and proche == "contrat 2016"
    assert due == 55000 and base_anc == 44000 and date_av == 28000 and due - base_anc == 11000 and due - date_av == 27000
    assert indemnite(10000, 5) == 35000 and indemnite(10000, 6) == 45000 and indemnite(10000, 0.5) == 0.0
    assert 24 * 10000 == 240000 > due and 21 * 5 + 30 * 2 == 165

    print("Corrigé")
    print(f"  ex1 {pe(0, 4)} ; ex2 ω1 = {oms[1]:.1f}, onde {ondes[1]:.2f} ; ex3 {dot(pe(9, 8), pe(9, 8)):.1f} ;"
          f" ex4 {dot(pe(2, 2), pe(5, 2)):.5f}")
    assert pe(0, 4) == [0.0, 1.0, 0.0, 1.0] and math.isclose(dot(pe(9, 8), pe(9, 8)), 4.0)
    assert round(dot(pe(2, 2), pe(5, 2)), 5) == -0.98999
    nb6 = morceaux(40000, 4096, 4096 - 512)
    pv6 = sum(2 * math.pi / omega(i, 512) <= 4096 for i in range(256))
    faux = [math.sin(1), math.cos(1), math.sin(100), math.cos(100)]
    print(f"  ex6 {nb6} morceaux, {nb6 * 4096:,} tokens, attention ÷ {40000 ** 2 / (nb6 * 4096 ** 2):.2f}, paires vues {pv6}/256 ;"
          f" ex7 PE(1) faux {r5(faux)}")
    assert nb6 == 12 and nb6 * 4096 == 49152 and round(40000 ** 2 / (nb6 * 4096 ** 2), 2) == 7.95 and pv6 == 181
    assert r5(faux) == [0.84147, 0.5403, -0.50637, 0.86232] and 10000 ** (2 / 4) == 100
    # nombres cités dans le texte
    assert round(0.84147 ** 2, 5) == 0.70807 and round(0.5403 ** 2, 5) == 0.29192 and round(1 - 0.01 ** 2 / 2, 5) == 0.99995
    assert round(2 * math.pi * 10000) == 62832 and round(2 * math.pi, 2) == 6.28 and round(omega(255, 512) * 1e4, 4) == 1.0366
    assert round(10000 ** (1 / 4), 10) == 10 and round(20 * math.pi, 2) == 62.83 and round((6283.19 - 35) / 40, 1) == 156.2
    assert round((40000 - 4096) / 3584, 2) == 10.02 and 0.10 * 600000 == 60000 and 10000 / 30 * 105 == 35000
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
film d = 4 : PE(0) [0.0, 1.0, 0.0, 1.0] ; PE(1) [0.84147, 0.5403, 0.01, 0.99995] ; PE(2) [0.9093, -0.41615, 0.02, 0.9998]
PE(1), d = 4 : [0.84147, 0.5403, 0.01, 0.99995]
démo 1 : ‖PE‖ = 2 pour d = 8 ; d = 5 : ‖PE‖² = 2.0000 en 0, 2.9076 en 2000
démo 2 : PE(2) [0.909297, -0.416147, 0.019999, 0.9998] ; T3·PE(2) = [-0.958924, 0.283662, 0.049979, 0.99875] = PE(5)
PE(10)·PE(13) = 1.96489 ; PE(100)·PE(103) = 1.96489
démo 3 : sinus seuls : sin 10 · sin 13 = -0.22858 ; sin 100 · sin 103 = -0.31546
fréquences [1.0, 0.1, 0.01, 0.001] ; longueurs d'onde [6.28, 62.83, 628.32, 6283.19]
démo 5 : d = 2 : écart 1 -> 0.95885, 6 -> 0.28224, 44 -> 0.0177 ; écart 44 : d = 4 -> 0.43682, d = 8 -> 1.67553
démo 6 : RoPE (2, 5) -0.48110, (10, 13) -0.48110, q·R(3)k -0.48110 ; addition (2, 5) -1.13626, (10, 13) -0.96750
cas 1 IMMO : S(75) = 2.99726 ; S(2035) = -0.40969 ; sur 60 lignes S dans [-2.6953 ; 3.50954] ; JSON S(3) = 1.96489
  λ max 6283.19 tokens -> bascule 156 lignes (142 à 44 tokens) ; valeur 1,711,000 AED, confondue 1,392,400 AED, frais DLD 68,440 contre 55,696
  décision : une ligne JSON par transaction (S varie de 6.2048 sur le tableau, 0 en JSON)
cas 2 BTP : coordonnée lente max 0.7508 sur [0 ; 8192], -0.8441 en 40 000 ; paires vues en entier 200/256 ; part des positions hors entraînement 79.52%
  6 morceaux, 49,152 tokens traités (+22.88%) ; attention ÷ 3.974 ; bascule à 7 morceaux : 46,592 tokens ; contrat + 10 % : 6 morceaux
  décision : 40000 > 8192 -> découper en 6 morceaux, clauses citées récupérées par recherche
cas 3 PUBLIC : k = 1 : S 3.53526, A 0.95230 ; k = −1 : S 3.53526, A -0.95230 ; k = ±3 : S 1.96489, A ±0.46964
  paire rapide de signe positif pour k = [1, 2, 3] ; A(4) = -0.32339 ; ID 784199012345671 (15 chiffres) inversé 176543210991487 : commence par 784 ? False
  décision : remise en ordre logique avant le modèle ; alerte si l'ID ne commence pas par 784 et finit par 487
cas 4 RH : S(9500) = -7.441, S(4000) = 11.602, S(500) = 67.233 ; plus proche en tokens : contrat 2016
  indemnité due 55,000 AED ; base 2016 : 44,000 ; entrée lue en 2019 : 28,000 ; 5 ans 35,000, 6 ans 45,000
  décision : frise datée triée par outil ; écart évité 11,000 AED (base) ou 27,000 AED (date)
Corrigé
  ex1 [0.0, 1.0, 0.0, 1.0] ; ex2 ω1 = 0.1, onde 62.83 ; ex3 4.0 ; ex4 -0.98999
  ex6 12 morceaux, 49,152 tokens, attention ÷ 7.95, paires vues 181/256 ; ex7 PE(1) faux [0.84147, 0.5403, -0.50637, 0.86232]
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme construit le vecteur d'encodage d'une position, paire par paire, avec une fréquence propre à chaque paire. Une variante, l'encodage rotatif, fait tourner les paires d'un vecteur au lieu d'ajouter l'encodage.

```text
ALGORITHME EncodageDePosition
ENTRÉES : position pos, dimension d (paire)
SORTIE  : vecteur PE de dimension d

  SI d impair OU d < 2 ALORS ERREUR
  POUR i DE 0 À d/2 − 1 FAIRE
      ω ← 10000 puissance (−2i/d)
      PE[2i]     ← sin(pos × ω)
      PE[2i + 1] ← cos(pos × ω)
  FIN POUR
  RETOURNER PE

ALGORITHME EncodageRotatif
ENTRÉES : vecteur v de dimension d, position pos
SORTIE  : vecteur v tourné
  POUR i DE 0 À d/2 − 1 FAIRE
      θ ← pos × 10000 puissance (−2i/d)
      (v[2i] ; v[2i + 1]) ← R(θ) × (v[2i] ; v[2i + 1])
  FIN POUR
  RETOURNER v
```

**Complexité.** O(d) par position ; O(n × d) pour une séquence de n tokens, calculé une fois et réutilisé. Le produit scalaire de deux encodages coûte O(d), et l'encodage rotatif O(d) par vecteur.

**Du squelette au code.** EncodageDePosition est la fonction `pe(pos, d)`, qui ajoute à chaque tour la paire `math.sin(pos * w), math.cos(pos * w)` et refuse un d impair ; `omega(i, d)` donne la fréquence. La propriété « le produit scalaire ne dépend que de l'écart » est vérifiée par `dot(pe(10, 8), pe(13, 8))` contre `dot(pe(100, 8), pe(103, 8))`, et la rotation de la démonstration 2 par le calcul de `rot`. EncodageRotatif est `rope`, qui applique `tourner` à chaque paire. Les similarités et orientations des cas sont `similarite_ecart` et `orientation_ecart`, et les quatre cas sont `cas_1_tableau_immo`, `cas_2_contrat_btp`, `cas_3_formulaire_public` et `cas_4_frise_rh`.
