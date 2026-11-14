# Étape 73 bis — Optimisation — Quantification INT8 et INT4

**Dossier :** 12-Production-Couts-Optimisation

> Étape 73 bis du parcours · Prérequis : [Descente de gradient et LoRA](<73-Optimisation-et-Fine-Tuning.md>) · Suite : [Distillation maître-élève](<73c-Distillation-Maitre-Eleve.md>)

## Définition

**Quantifier** un modèle, c'est remplacer ses nombres réels, stockés sur 16 ou 32 bits, par des entiers de 8 bits (INT8) ou de 4 bits (INT4), accompagnés d'une **échelle** s qui permet de revenir aux réels. Chaque valeur x est divisée par s, arrondie à l'entier le plus proche, éventuellement décalée d'un **point zéro** z, puis bornée à la plage des entiers disponibles ; on la reconstruit par x̂ = s(q − z). La version **symétrique** centre la plage sur zéro (z = 0) ; la version **asymétrique** l'adapte à une plage décentrée. On choisit aussi la **granularité** : une échelle pour tout le tenseur, une par canal (ligne de la matrice), ou une par groupe de quelques dizaines de valeurs consécutives. Le gain est direct sur la mémoire (deux fois moins en INT8 qu'en 16 bits, quatre fois moins en INT4) et sur la vitesse de décodage, qui est limitée par la quantité de mémoire lue ; la contrepartie est une erreur d'arrondi qu'il faut borner, puis mesurer sur les tâches de l'agent.

## Rôle dans un agent

La quantification se décide avant le déploiement, et elle change le composant qui **décide** : le modèle qui répond dans la boucle percevoir → décider → agir → observer. Le développeur d'agent la rencontre dans trois situations. Quand il héberge un modèle ouvert, sur site pour des raisons de confidentialité ou sur un appareil hors ligne, la quantification décide si le modèle tient en mémoire, et combien de sessions tiennent à côté (étape 72 bis). Quand il spécialise un modèle, QLoRA permet d'entraîner un adaptateur LoRA (étape 73) sur une base gelée en 4 bits, sur une seule carte. Et quand il compare des modèles, il doit savoir qu'une version quantifiée n'est pas le même modèle : son taux de JSON valides (étape 11), sa justesse en arabe ou sa lecture des montants peuvent baisser, et seule une évaluation sur les tâches de l'agent le dit. Quand l'agent passe par une API, la quantification est un choix du fournisseur ; l'équipe n'en voit que les effets sur la qualité et le prix.

## Équation complète

Quantification et déquantification :

$$
q = \operatorname{clamp}\Bigl(\operatorname{round}\Bigl(\frac{x}{s}\Bigr) + z ,\; q_{min} ,\; q_{max}\Bigr), \qquad \hat{x} = s \, (q - z)
$$

Version symétrique sur n bits (z = 0) :

$$
q_{max} = 2^{\,n_{bits} - 1} - 1, \qquad q_{min} = -q_{max}, \qquad s = \frac{\max_i \lvert x_i \rvert}{q_{max}}
$$

Version asymétrique sur n bits :

$$
q_{min} = 0, \qquad q_{max} = 2^{\,n_{bits}} - 1, \qquad s = \frac{x_{max} - x_{min}}{q_{max} - q_{min}}, \qquad z = q_{min} - \operatorname{round}\Bigl(\frac{x_{min}}{s}\Bigr)
$$

Erreur d'arrondi dans la plage, et erreur quadratique moyenne :

$$
\lvert x - \hat{x} \rvert \le \frac{s}{2}, \qquad \mathbb{E}\bigl[(x - \hat{x})^2\bigr] \approx \frac{s^2}{12}
$$

Mémoire des poids, avec une échelle de o_s octets par groupe de g poids :

$$
\text{octets} = \frac{\Theta \, n_{bits}}{8} + \frac{\Theta}{g} \, o_s
$$

Erreur d'un produit scalaire dont les poids sont quantifiés :

$$
\Bigl\lvert \sum_{i=1}^{d} w_i x_i - \sum_{i=1}^{d} \hat{w}_i x_i \Bigr\rvert \le \frac{s}{2} \lVert x \rVert_1, \qquad \text{écart type} \approx \frac{s \, \lVert x \rVert_2}{\sqrt{12}}
$$

Produit scalaire entier, poids et entrées quantifiés symétriquement :

$$
\sum_{i=1}^{d} \hat{w}_i \hat{x}_i = s_w \, s_x \sum_{i=1}^{d} q_{w,i} \, q_{x,i}
$$

Principe de QLoRA (base gelée en 4 bits, adaptateur de l'étape 73) :

$$
h = \operatorname{deq}\bigl(W_0^{\text{NF4}}\bigr) \, x + \frac{\alpha_{\text{LoRA}}}{r} \, B \, (A \, x)
$$

## Décryptage des symboles

$$
x, \quad \hat{x}
$$

Une valeur réelle à quantifier (poids ou activation), et sa reconstruction après l'aller-retour : des réels ; dans le programme, des listes `x` et `x_hat`.

$$
n_{bits}
$$

Le nombre de bits de chaque entier : 8 ou 4 dans ce fichier ; argument `n_bits`.

$$
q, \quad q_{min}, \quad q_{max}
$$

L'entier stocké, et les bornes de la plage d'entiers : de −127 à 127 en INT8 symétrique, de −7 à 7 en INT4 symétrique, de 0 à 255 en INT8 asymétrique ; valeurs renvoyées par `quantifier` et par `bornes(n_bits, symetrique)`.

$$
s
$$

L'échelle, le pas entre deux valeurs représentables : un réel > 0, dans l'unité de x ; premier élément renvoyé par `params_symetrique` ou `params_asymetrique`.

$$
z
$$

Le point zéro, l'entier qui représente exactement le réel 0 : z = 0 en symétrique, un entier de la plage en asymétrique ; deuxième élément renvoyé par les mêmes fonctions.

$$
\operatorname{round}, \quad \operatorname{clamp}
$$

L'arrondi à l'entier le plus proche (Python, comme PyTorch, arrondit les demis vers l'entier pair), et la mise aux bornes, qui ramène un entier hors plage à q_min ou à q_max : `round(v / s)` et `max(q_min, min(q_max, ...))`.

$$
x_{min}, \quad x_{max}
$$

La plus petite et la plus grande valeur du tenseur ou du groupe, mesurées sur les poids, ou sur des données de calibration pour les activations : `min(x)` et `max(x)`.

$$
g
$$

La taille d'un groupe, le nombre de valeurs consécutives qui partagent une échelle : un entier ≥ 1, souvent 64 ou 128 ; argument `g`.

$$
\Theta
$$

Le nombre de paramètres du modèle : 7 × 10⁹ dans l'exemple ; argument `n_params`.

$$
o_s
$$

Le nombre d'octets d'une échelle stockée : 2 en 16 bits, 4 en 32 bits ; argument `octets_echelle`.

$$
w, \quad \hat{w}, \quad d
$$

Un vecteur de poids, sa version quantifiée, et sa dimension : `wv`, `dequantifier(q_w, s_w)` et 256 dans le programme.

$$
\lVert x \rVert_1, \quad \lVert x \rVert_2
$$

La somme des valeurs absolues des coordonnées de x, et la racine de la somme de leurs carrés : `sum(abs(v) for v in xv)` et `math.sqrt(sum(v * v for v in xv))`.

$$
s_w, \quad s_x, \quad q_{w,i}, \quad q_{x,i}
$$

Les échelles des poids et des entrées, et leurs entiers : `s_w`, `s_x`, `q_w`, `q_x`.

$$
W_0^{\text{NF4}}, \quad \operatorname{deq}
$$

La matrice gelée stockée en NF4, et la déquantification qui la ramène en 16 bits, bloc par bloc, au moment du calcul : `grille_nf4()` et `quantifier_grille(x, grille, g)` dans le programme.

$$
\alpha_{\text{LoRA}}, \quad r, \quad B, \quad A
$$

L'échelle, le rang et les deux matrices étroites de l'adaptateur LoRA, définis à l'étape 73 : `lora = 128 * 16 * (4096 + 4096)` en compte le nombre de paramètres.

## Démonstration

### 1. L'erreur d'arrondi ne dépasse pas s/2 dans la plage

On pose u = x / s. **Pas d'écrêtage dans la plage.** En symétrique, |x| ≤ max|x| = s q_max, donc |u| ≤ q_max et round(u) reste entre −q_max et q_max. En asymétrique, z est un entier, donc round(u + entier) = round(u) + entier ; pour x = x_min, q = round(x_min/s) + q_min − round(x_min/s) = q_min ; pour x = x_max, x_max/s = x_min/s + (q_max − q_min) par définition de s, donc q = q_max ; et q croît avec x entre les deux. **L'erreur.** Sans écrêtage, q − z = round(u), donc x̂ = s · round(u) et

$$
\lvert x - \hat{x} \rvert = s \, \bigl\lvert u - \operatorname{round}(u) \bigr\rvert \le \frac{s}{2}
$$

parce que l'entier le plus proche de u en est à au plus une demi-unité. Le zéro réel est exact : x = 0 donne q = z et x̂ = 0, ce qui compte pour les zéros de remplissage et les sorties nulles d'une activation. **Hors de la plage**, l'écrêtage remplace q par q_max et l'erreur vaut x − s q_max, qui peut être bien plus grande que s/2 : c'est pourquoi la plage des activations se mesure sur des données de calibration représentatives.

Dans l'exemple x = [0,523 ; −1,137 ; 0,047 ; 2,54], l'INT8 symétrique donne s = 2,54/127 = 0,02, u = [26,15 ; −56,85 ; 2,35 ; 127], q = [26 ; −57 ; 2 ; 127] et x̂ = [0,52 ; −1,14 ; 0,04 ; 2,54] : l'erreur maximale vaut 0,007 ≤ 0,01. L'INT4 symétrique donne s = 2,54/7 ≈ 0,362857, q = [1 ; −3 ; 0 ; 7] et x̂ ≈ [0,3629 ; −1,0886 ; 0 ; 2,54] : l'erreur maximale vaut 0,1601 ≤ 0,1814. Passer de 8 à 4 bits a multiplié le pas par 127/7 ≈ 18.

### 2. L'erreur quadratique moyenne vaut s²/12

Quand les valeurs s'étalent sur de nombreux pas, l'erreur e = x − x̂ se répartit à peu près uniformément entre −s/2 et s/2. Sa moyenne est alors nulle et son carré moyen vaut

$$
\mathbb{E}[e^2] = \frac{1}{s} \int_{-s/2}^{s/2} e^2 \, de = \frac{1}{s} \cdot \frac{2}{3} \Bigl(\frac{s}{2}\Bigr)^3 = \frac{s^2}{12}
$$

Sur 10 000 valeurs uniformes entre −1 et 1, le programme mesure une erreur maximale égale à 0,9999 fois s/2 et une erreur quadratique égale à 0,9987 fois s²/12. Conséquence : chaque bit retiré double s, donc multiplie l'erreur quadratique par 4.

### 3. Symétrique ou asymétrique

Sur une plage décentrée comme [−0,51 ; 2,04], la version symétrique prend s = 2,04/127 ≈ 0,016063 et n'utilise jamais les entiers de −127 à −33, puisqu'aucune valeur ne descend sous −0,51. La version asymétrique répartit les 256 entiers sur la seule plage utile : s = 2,55/255 = 0,01 et z = 0 − round(−0,51/0,01) = 51, si bien que x = −0,51 donne q = 0 et x = 2,04 donne q = 255. Le pas est 1,61 fois plus fin. Le prix : un point zéro à stocker, et un terme de plus dans les produits scalaires, puisque s_w q_w · s_x (q_x − z_x) fait apparaître z_x ∑ q_w, que l'on peut précalculer pour chaque ligne de poids. L'usage courant est de quantifier les poids, centrés autour de 0, en symétrique, et les activations, souvent décentrées, en asymétrique.

### 4. Une valeur aberrante gonfle l'échelle ; les groupes et les canaux l'isolent

L'échelle symétrique vaut max|x| / q_max : une seule valeur extrême la fixe pour tout le tenseur. Le programme tire 256 poids d'une loi normale d'écart type 0,02, puis remplace l'un d'eux par 1,0. En INT4 par tenseur, s = 1/7 ≈ 0,143 ; tout poids tel que |w| < s/2 ≈ 0,0714 s'arrondit à 0, ce qui est le cas des 255 poids normaux. Leur reconstruction est nulle et l'erreur relative vaut exactement 1 : le tenseur n'a plus gardé que sa valeur aberrante. Avec une échelle par groupe de 32 poids, seul le groupe qui contient la valeur aberrante subit ce sort ; les sept autres gardent une échelle adaptée, et l'erreur relative tombe à 0,3515, avec 67 poids mis à zéro au lieu de 255. Une échelle par canal règle le même problème entre lignes d'une matrice : une ligne de petits poids [0,012 ; −0,007 ; 0,003 ; 0,009] rangée avec une ligne de grands poids [1,2 ; −2,5 ; 0,4 ; 1,9] subit une erreur relative de 0,8366 en INT8 par tenseur, contre 0,0020 avec sa propre échelle.

### 5. La mémoire : 14, 7 et 3,5 Go, plus les échelles

Un modèle de 7 milliards de paramètres occupe 7 × 10⁹ × 16/8 = 14 × 10⁹ octets en 16 bits, 7 en INT8 et 3,5 Go en INT4 (1 Go = 10⁹ octets ; 14 Go font 13,04 Gio). Les échelles s'ajoutent : une échelle de 2 octets par groupe de 128 poids ajoute 7 × 10⁹ / 128 × 2 = 109 375 000 octets, soit 3,6094 Go en tout et 4 + 16/128 = 4,125 bits par poids. Avec des blocs de 64 et des échelles de 32 bits, comme le NF4 de QLoRA, on ajoute 32/64 = 0,5 bit par poids (3,9375 Go). La **double quantification** de QLoRA quantifie à leur tour ces échelles sur 8 bits, par blocs de 256, avec une échelle de 32 bits par bloc : le surcoût tombe à

$$
\frac{8}{64} + \frac{32}{64 \times 256} \approx 0{,}127 \text{ bit par poids}
$$

et le modèle à 3,6111 Go. Ces gains supposent que les entiers de 4 bits sont réellement **empaquetés** deux par octet : rangés un par octet, ils prendraient la place de l'INT8. Le programme range [−8, 7, 0, −1, 3, −5] dans les 3 octets `f0783b`, en décalant chaque entier de 8 pour le ramener entre 0 et 15, puis les relit à l'identique.

### 6. L'erreur d'un produit scalaire : la borne et l'ordre de grandeur

L'erreur vaut ∑ (wᵢ − ŵᵢ) xᵢ. Par l'inégalité triangulaire, puis par le point 1,

$$
\Bigl\lvert \sum_{i=1}^{d} (w_i - \hat{w}_i) \, x_i \Bigr\rvert \le \sum_{i=1}^{d} \lvert w_i - \hat{w}_i \rvert \, \lvert x_i \rvert \le \frac{s}{2} \sum_{i=1}^{d} \lvert x_i \rvert = \frac{s}{2} \lVert x \rVert_1
$$

Cette borne suppose que toutes les erreurs ont le pire signe en même temps. Si elles sont indépendantes, de moyenne nulle et de variance s²/12 (point 2), la variance d'une somme de termes indépendants est la somme des variances, donc

$$
\operatorname{Var}\Bigl(\sum_{i=1}^{d} (w_i - \hat{w}_i) \, x_i\Bigr) = \frac{s^2}{12} \sum_{i=1}^{d} x_i^2
$$

et l'écart type vaut s ‖x‖₂ / √12. La borne croît comme d, l'écart type comme √d. Sur 256 coordonnées, le programme trouve une borne de 2,73 × 10⁻², un écart type attendu de 1,15 × 10⁻³ et un écart observé de 6,19 × 10⁻⁴ : la borne garantit, l'écart type prédit.

Quand les entrées sont aussi quantifiées (INT8 pour les poids et les activations), le produit scalaire se calcule presque entièrement en entiers :

$$
\sum_{i=1}^{d} s_w q_{w,i} \, s_x q_{x,i} = s_w \, s_x \sum_{i=1}^{d} q_{w,i} \, q_{x,i}
$$

parce que les deux échelles sont communes à toutes les coordonnées et sortent de la somme. La carte accumule les produits d'entiers dans un entier de 32 bits, ici 19 933, puis fait une seule multiplication réelle : 0,067711, contre 0,067745 pour le calcul exact. Quand seuls les poids sont quantifiés, la carte les déquantifie à la volée et calcule en 16 bits : on gagne la mémoire et la bande passante, pas les opérations.

### 7. NF4 : des niveaux placés là où sont les poids

Les poids d'un réseau entraîné suivent souvent une loi proche d'une loi normale centrée : beaucoup de petites valeurs, peu de grandes. Une grille INT4 uniforme place ses niveaux à égale distance et en gaspille dans les queues, où presque aucun poids ne tombe. **NF4** (NormalFloat 4 bits, introduit avec QLoRA) place ses 16 niveaux aux quantiles d'une loi normale, de sorte que chaque niveau couvre à peu près la même probabilité. La construction : 8 niveaux positifs aux quantiles de probabilités régulièrement espacées entre 0,9677083 et 0,5 (0,5 exclu), 7 niveaux négatifs construits de même, et le 0 exact, puis une division par le plus grand niveau pour ramener la grille dans [−1 ; 1]. La grille est asymétrique (8 positifs, 7 négatifs) parce que 16 codes ne peuvent pas contenir le zéro exact et autant de niveaux de chaque côté. Le nombre 0,9677083 vaut, aux arrondis près, la moyenne de 1 − 1/30 et de 1 − 1/32 ; il évite de demander le quantile de probabilité 1, qui est infini. La fonction `NormalDist().inv_cdf` de la bibliothèque standard redonne la table publiée à 10⁻⁶ près. Sur 4 096 poids gaussiens quantifiés par blocs de 64 avec une échelle absmax, l'erreur quadratique vaut 5,086 × 10⁻⁶ avec la grille uniforme et 3,314 × 10⁻⁶ avec NF4, soit 1,53 fois moins pour le même nombre de bits.

### 8. QLoRA : une base gelée en 4 bits, un adaptateur en 16 bits

QLoRA stocke la matrice gelée W₀ en NF4 avec double quantification, la déquantifie bloc par bloc en 16 bits au moment de chaque produit, et n'entraîne que l'adaptateur LoRA, en 16 bits (étape 73). Le gradient traverse W₀ déquantifiée pour atteindre les adaptateurs des couches précédentes, mais W₀ ne reçoit ni gradient ni état d'optimiseur. Avec la convention de l'étape 73 (quatre copies par poids entraîné : le poids, son gradient et les deux moments d'Adam, ici sur 2 octets), et un adaptateur de rang 16 sur 128 matrices 4 096 × 4 096, soit 16 777 216 paramètres :

- fine-tuning complet : 4 × 7 × 10⁹ × 2 = 56 Go ;
- LoRA sur une base en 16 bits : 14 + 4 × 16 777 216 × 2 / 10⁹ ≈ 14,13 Go ;
- QLoRA : 3,6111 + 0,1342 ≈ 3,75 Go.

Ces nombres ne comptent pas les activations, que l'entraînement garde pour la rétropropagation, et les implémentations réelles tiennent souvent les moments d'Adam en 32 bits : les besoins réels sont plus élevés, mais l'écart entre les trois options reste du même ordre. Un point pratique découle de la formule : l'adaptateur a appris à corriger la base **quantifiée**. Si on le fusionne dans une base en 16 bits, puis qu'on requantifie le tout, on obtient un troisième modèle, qu'il faut réévaluer.

### 9. Exemple fait à la main (le code reprend ces nombres)

- INT8 symétrique de [0,523 ; −1,137 ; 0,047 ; 2,54] : s = 0,02, q = [26 ; −57 ; 2 ; 127], x̂ = [0,52 ; −1,14 ; 0,04 ; 2,54], erreur maximale 0,007.
- INT4 symétrique : s = 0,362857, q = [1 ; −3 ; 0 ; 7], erreur maximale 0,1601.
- INT8 asymétrique de [−0,51 ; 0,004 ; 0,7333 ; 2,04] : s = 0,01, z = 51, q = [0 ; 51 ; 124 ; 255], x̂ = [−0,51 ; 0 ; 0,73 ; 2,04].
- Mémoire d'un modèle de 7 milliards de paramètres : 14, 7, 3,5 Go ; 3,6094 Go en INT4 par groupes de 128 avec des échelles de 2 octets.

## Effets et comportement

- **Chaque bit retiré double le pas.** L'erreur quadratique est multipliée par 4 ; de 8 à 4 bits, le pas symétrique est multiplié par 127/7 ≈ 18.
- **Des groupes plus petits isolent mieux les valeurs extrêmes.** Le prix est une échelle de plus par groupe : 16/g bits par poids avec des échelles de 2 octets.
- **La mémoire baisse dans le rapport des bits, le calcul pas toujours.** Une quantification des seuls poids réduit la mémoire et accélère le décodage, limité par la lecture des poids ; seul un calcul en entiers (poids et activations) réduit aussi les opérations.
- **L'erreur se mesure sur la tâche.** Les bornes disent combien chaque nombre bouge, pas si l'agent extrait encore le bon montant ou répond encore bien en arabe.
- **Une version quantifiée est un autre modèle.** Elle se versionne, s'évalue et se déploie comme tel.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| q_min, q_max | `bornes(n_bits, symetrique)` |
| q = clamp(round(x/s) + z, q_min, q_max) | `quantifier(x, s, z, q_min, q_max)` |
| x̂ = s(q − z) | `dequantifier(q, s, z)` |
| s, z symétriques | `params_symetrique(x, n_bits)` |
| s, z asymétriques | `params_asymetrique(x, n_bits)` |
| aller-retour par tenseur, par groupe | `aller_retour(x, n_bits)`, `par_groupes(x, n_bits, g)` |
| ‖x − x̂‖ / ‖x‖ | `erreur_relative(x, x_hat)` |
| Θ n_bits / 8 + (Θ / g) o_s | `octets_poids(n_params, n_bits, g, octets_echelle)` |
| deux entiers de 4 bits par octet | `empaqueter_int4(q)`, `depaqueter_int4(donnees)` |
| grille NF4, quantification sur une grille | `grille_nf4()`, `quantifier_grille(x, grille, g)` |

### Déroulé, ligne par ligne

**`bornes(n_bits, symetrique)`** renvoie `(-127, 127)` pour l'INT8 symétrique, `(-7, 7)` pour l'INT4 symétrique et `(0, 255)` pour l'INT8 asymétrique. La version symétrique renonce à −128 (ou −8) pour que la plage reste centrée sur zéro.

**`quantifier(x, s, z, q_min, q_max)`** est la formule mot pour mot : `round(v / s) + z`, puis `max(q_min, min(q_max, ...))`. Pour `v = 0.523` et `s = 0.02`, `v / s` vaut 26,15 et l'entier vaut 26 ; pour `v = -1.137`, −56,85 donne −57. La garde refuse une échelle nulle ou négative.

**`dequantifier(q, s, z)`** renvoie `s * (v - z)` : 26 × 0,02 = 0,52.

**`params_symetrique(x, n_bits)`** prend `a = max(abs(v) for v in x)`, soit 2,54, et renvoie `a / q_max` : 0,02 en INT8, 0,362857 en INT4. Un tenseur nul lève `ValueError`, puisque l'échelle vaudrait 0.

**`params_asymetrique(x, n_bits)`** prend `lo = -0.51` et `hi = 2.04`, puis `s = (hi - lo) / 255` = 0,01 et `q_min - round(lo / s)` = 0 − (−51) = 51.

**`aller_retour`** enchaîne les deux étapes avec les paramètres de la version choisie. **`par_groupes(x, n_bits, g)`** découpe `x` en tranches `x[debut:debut + g]` et fait un aller-retour par tranche, chacune avec sa propre échelle.

**`erreur_relative(x, x_hat)`** renvoie ‖x − x̂‖ / ‖x‖ : elle vaut 1 quand x̂ est nul, ce qui arrive aux 255 poids normaux en INT4 par tenseur.

**`octets_poids(n_params, n_bits, g, octets_echelle)`** calcule `n_params * n_bits / 8`, puis ajoute `n_params / g * octets_echelle` si un groupe est donné : 3,5 × 10⁹ + 109 375 000 octets pour l'INT4 par groupes de 128.

**`empaqueter_int4(q)`** associe les entiers deux par deux (`zip(q[0::2], q[1::2])`), ajoute 8 à chacun et range le premier dans les 4 bits bas, le second dans les 4 bits hauts : (−8, 7) donne 0 | (15 << 4) = 0xF0. **`depaqueter_int4`** lit `octet & 0xF` et `octet >> 4` et retranche 8.

**`grille_nf4(decalage)`** construit les 8 quantiles positifs avec `nd.inv_cdf(p)` pour 8 probabilités allant de 0,9677083 à 0,5 (exclu), les 7 quantiles négatifs de même, ajoute 0, trie, puis divise par le plus grand niveau. **`quantifier_grille(x, grille, g)`** divise chaque valeur d'un bloc par l'absmax du bloc, prend le niveau le plus proche avec `min(grille, key=...)`, puis remultiplie.

**`main()`**, bloc par bloc.

1. L'exemple à la main en INT8 puis en INT4 ; l'`assert` vérifie l'erreur maximale ≤ s/2 et les entiers [26, −57, 2, 127] et [1, −3, 0, 7] (point 1).
2. La plage décentrée : s = 0,01, z = 51, q = [0, 51, 124, 255], zéro exact ; le pas symétrique est 1,61 fois plus grand (point 3).
3. 10 000 valeurs tirées avec la graine 73 : erreur maximale sous s/2, erreur quadratique à moins de 5 % de s²/12 ; une valeur hors plage, 3,0, est écrêtée à 127 s (points 1 et 2).
4. La valeur aberrante : erreur relative 1 et 255 zéros par tenseur, 0,3515 et 67 zéros par groupes de 32 ; puis la ligne de petits poids, 0,8366 par tenseur contre 0,0020 par canal (point 4).
5. Le tableau de mémoire, la double quantification (0,127 bit, 3,6111 Go) et l'empaquetage de six entiers dans trois octets (point 5).
6. Le produit scalaire sur 256 coordonnées : l'écart observé est sous la borne et sous trois écarts types ; le calcul entier redonne exactement le produit des valeurs déquantifiées (point 6).
7. La grille NF4, comparée à la table publiée, puis le rapport 1,53 d'erreur quadratique contre la grille uniforme (point 7).
8. Les trois budgets de mémoire de fine-tuning : 56, 14,13 et 3,75 Go (point 8).
9. Un tenseur nul et un entier hors de la plage −8..7 lèvent `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`bornes(n_bits, symetrique)`** — Cette fonction est l'architecte qui fixe le nombre de marches de l'escalier sur lequel on va poser les poids : elle reçoit le nombre de bits et un booléen qui dit si la plage doit être centrée sur zéro, et renvoie le couple des entiers extrêmes, de −(2ᵇ⁻¹ − 1) à 2ᵇ⁻¹ − 1 en symétrique, de 0 à 2ᵇ − 1 sinon. Elle donne ainsi −127 et 127 pour l'INT8 symétrique, −7 et 7 pour l'INT4 symétrique, et 0 et 255 pour l'INT8 asymétrique ; la version symétrique renonce volontairement à −128 ou −8 pour garder le zéro au centre.

**`quantifier(x, s, z, q_min, q_max)`** — Celle-ci est le déménageur qui pose chaque valeur réelle sur la marche entière la plus proche : elle reçoit la liste des valeurs, l'échelle s, le point zéro z et les deux bornes, lève une `ValueError` si l'échelle n'est pas strictement positive, puis, pour chaque valeur, divise par s, arrondit, ajoute z et écrête le résultat entre les bornes. Elle renvoie la liste des entiers ; pour l'exemple à la main avec s = 0,02, elle donne 26, −57, 2 et 127, et une valeur hors plage comme 3,0 reste bloquée sur la dernière marche, 127.

**`dequantifier(q, s, z)`** — Cette fonction fait le chemin inverse, comme un interprète qui retraduit le texte compressé dans la langue d'origine : elle reçoit la liste des entiers, l'échelle et le point zéro, 0 par défaut, et renvoie pour chaque entier la valeur s(q − z). L'entier 26 redevient ainsi 0,52 avec s = 0,02, une erreur de 0,003 sur la valeur de départ 0,523, et `main` vérifie que l'erreur de l'aller-retour ne dépasse jamais s/2 tant que la valeur reste dans la plage.

**`params_symetrique(x, n_bits)`** — Celle-ci est le géomètre qui choisit la taille des marches pour une plage centrée : elle reçoit les valeurs d'un tenseur et le nombre de bits, lit les bornes symétriques, prend la plus grande valeur absolue, lève une `ValueError` si elle est nulle, puisque l'échelle vaudrait 0, et renvoie le quadruplet formé de l'échelle max|x| / q_max, du point zéro 0 et des deux bornes. Pour l'exemple dont le maximum vaut 2,54, l'échelle est 0,02 en INT8 et 0,362857 en INT4.

**`params_asymetrique(x, n_bits)`** — Cette fonction règle l'escalier pour une plage décentrée, comme un tailleur qui coupe à la mesure exacte au lieu de prendre une taille symétrique : elle reçoit les valeurs et le nombre de bits, lit les bornes 0 et 2ᵇ − 1, lève une `ValueError` si toutes les valeurs sont égales, puis calcule l'échelle (max − min) / (q_max − q_min) et le point zéro q_min − round(min / s), qui fait tomber le zéro réel exactement sur un entier. Pour la plage de −0,51 à 2,04, elle renvoie s = 0,01 et z = 51, un pas environ 1,61 fois plus fin que le pas symétrique.

**`aller_retour(x, n_bits, symetrique)`** — Celle-ci fait faire aux valeurs le voyage complet, aller en entiers et retour en réels, pour mesurer ce que la compression leur a coûté : elle reçoit les valeurs, le nombre de bits et le mode, symétrique par défaut, choisit `params_symetrique` ou `params_asymetrique`, puis enchaîne `quantifier` et `dequantifier` avec ces paramètres. Elle renvoie le couple formé des valeurs reconstruites et de l'échelle employée ; sur les 256 poids qui contiennent une valeur aberrante de 1,0, l'aller-retour INT4 par tenseur met à zéro les 255 poids normaux.

**`par_groupes(x, n_bits, g)`** — Cette fonction découpe le tenseur en lots, comme un photographe qui règle l'exposition séparément pour chaque zone au lieu d'une seule fois pour toute la scène : elle reçoit les valeurs, le nombre de bits et la taille g d'un groupe, prend des tranches consécutives de g valeurs, fait sur chacune un aller-retour symétrique avec sa propre échelle, puis renvoie la concaténation des valeurs reconstruites. Avec des groupes de 32, la valeur aberrante ne gâte plus que son propre groupe : l'erreur relative des poids normaux tombe de 1 à 0,3515, et seuls 67 d'entre eux sont mis à zéro au lieu de 255.

**`erreur_relative(x, x_hat)`** — Celle-ci est le contrôleur qualité qui rapporte la taille de l'erreur à celle du signal : elle reçoit les valeurs d'origine et leurs reconstructions, et renvoie la racine de la somme des carrés des écarts divisée par la somme des carrés des valeurs, c'est-à-dire ‖x − x̂‖ / ‖x‖. Elle vaut 1 quand tout est mis à zéro, comme pour l'INT4 par tenseur avec une valeur aberrante, et pour une ligne de petits poids elle passe d'environ 0,837 par tenseur à moins de 0,005 par canal.

**`octets_poids(n_params, n_bits, g, octets_echelle)`** — Cette fonction est le déménageur qui calcule la place que prendront les poids dans la mémoire : elle reçoit le nombre de paramètres, le nombre de bits par poids, une taille de groupe facultative, absente par défaut, et la taille d'une échelle en octets, 2 par défaut, calcule Θ × bits / 8 et ajoute, si un groupe est donné, une échelle par groupe. Pour 7 milliards de paramètres, elle donne 14, 7 et 3,5 Go en FP16, INT8 et INT4, puis 3,6094 Go en INT4 par groupes de 128, soit 109 375 000 octets d'échelles et 4,125 bits par poids.

**`depaqueter_int4(donnees)`** — Celle-ci est le facteur qui ouvre chaque enveloppe contenant deux lettres et les rend à leurs destinataires : elle reçoit une suite d'octets produite par `empaqueter_int4`, lit pour chaque octet les 4 bits bas puis les 4 bits hauts, retranche 8 à chacun pour revenir dans la plage de −8 à 7, et renvoie la liste des entiers dans leur ordre d'origine. Dans la section 5, les six entiers −8, 7, 0, −1, 3, −5, rangés dans trois octets, ressortent intacts, ce que vérifie un `assert`.

**`pas(a, b, n)`** — Cette petite fonction interne, qui vit dans `grille_nf4`, est l'arpenteur qui plante n jalons régulièrement espacés entre deux points : elle reçoit le premier point a, le dernier point b et le nombre de jalons, et renvoie la liste a + (b − a) × i / (n − 1) pour i de 0 à n − 1, extrémités comprises. `grille_nf4` l'appelle pour répartir les probabilités entre 0,9677083 et 0,5, neuf jalons pour les niveaux positifs et huit pour les négatifs, dont elle retire chaque fois le dernier, 0,5, qui donnerait le zéro.

**`quantifier_grille(x, grille, g)`** — Celle-ci quantifie sur une grille quelconque, comme un peintre qui ne dispose que de seize tubes de couleur et prend pour chaque touche la teinte la plus proche : elle reçoit les valeurs, la liste des niveaux de la grille et la taille de bloc g, divise chaque valeur d'un bloc par la plus grande valeur absolue du bloc, prend le niveau le plus proche de ce quotient, puis le remultiplie par cette valeur absolue. Elle renvoie les valeurs reconstruites ; sur 4 096 poids gaussiens en blocs de 64, la grille NF4 donne une erreur quadratique 1,53 fois plus petite que la grille INT4 uniforme.

**`eqm(x, x_hat)`** — Cette fonction est la balance qui pèse l'erreur moyenne d'une reconstruction : elle reçoit les valeurs d'origine et leurs reconstructions, additionne les carrés des écarts et renvoie cette somme divisée par le nombre de valeurs, l'erreur quadratique moyenne. Dans la section 7, elle vaut environ 5,086 × 10⁻⁶ pour la grille uniforme et 3,314 × 10⁻⁶ pour la grille NF4, ce qui donne le rapport 1,53 vérifié par `main`.

**`arrondir(v, n)`** — Celle-ci est le typographe qui met les nombres au propre avant l'impression : elle reçoit une liste de flottants et un nombre de décimales, 4 par défaut, arrondit chaque valeur à ce nombre de décimales et lui ajoute 0,0, ce qui transforme un éventuel −0,0 en 0,0 pour que l'affichage ne montre pas de zéro négatif. Elle renvoie la liste arrondie et ne sert qu'aux `print` de `main`, par exemple pour afficher 0,3629 ; −1,0886 ; 0,0 ; 2,54 en INT4.

**`main()`** — C'est le chef de laboratoire qui conduit neuf expériences : il rejoue l'exemple à la main en INT8 puis en INT4, règle la plage décentrée avec s = 0,01 et z = 51, vérifie sur 10 000 valeurs la borne s/2 et l'erreur quadratique s²/12, puis montre comment une valeur aberrante ruine la quantification par tenseur et comment les groupes ou les canaux la contiennent. Il dresse ensuite le tableau de mémoire pour 7 milliards de paramètres avec la double quantification et l'empaquetage INT4, contrôle le produit scalaire quantifié, compare la grille NF4 à la table publiée, chiffre les budgets de fine-tuning, 56, 14,13 et 3,75 Go, et termine en vérifiant que deux entrées invalides lèvent `ValueError`.

```python
"""Étape 73 bis — quantification INT8 et INT4 : symétrique, asymétrique, granularité, mémoire, NF4, QLoRA."""
import math
import random
import sys
from statistics import NormalDist

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- quantifier et déquantifier
def bornes(n_bits: int, symetrique: bool) -> tuple[int, int]:
    """Plage des entiers : [−(2^(b−1) − 1), 2^(b−1) − 1] en symétrique (zéro au centre), [0, 2^b − 1] sinon."""
    if symetrique:
        q_max = 2 ** (n_bits - 1) - 1
        return -q_max, q_max
    return 0, 2 ** n_bits - 1


def quantifier(x: list[float], s: float, z: int, q_min: int, q_max: int) -> list[int]:
    """q = clamp(round(x/s) + z, q_min, q_max)."""
    if s <= 0:
        raise ValueError("l'échelle s doit être > 0")
    return [max(q_min, min(q_max, round(v / s) + z)) for v in x]


def dequantifier(q: list[int], s: float, z: int = 0) -> list[float]:
    """x̂ = s (q − z)."""
    return [s * (v - z) for v in q]


def params_symetrique(x: list[float], n_bits: int) -> tuple[float, int, int, int]:
    """s = max|x| / q_max, z = 0."""
    q_min, q_max = bornes(n_bits, True)
    a = max(abs(v) for v in x)
    if a == 0:
        raise ValueError("tenseur nul : l'échelle n'est pas définie")
    return a / q_max, 0, q_min, q_max


def params_asymetrique(x: list[float], n_bits: int) -> tuple[float, int, int, int]:
    """s = (x_max − x_min) / (q_max − q_min), z = q_min − round(x_min / s) : le zéro réel tombe sur un entier."""
    q_min, q_max = bornes(n_bits, False)
    lo, hi = min(x), max(x)
    if hi == lo:
        raise ValueError("plage nulle : l'échelle n'est pas définie")
    s = (hi - lo) / (q_max - q_min)
    return s, q_min - round(lo / s), q_min, q_max


def aller_retour(x: list[float], n_bits: int, symetrique: bool = True) -> tuple[list[float], float]:
    s, z, q_min, q_max = (params_symetrique if symetrique else params_asymetrique)(x, n_bits)
    return dequantifier(quantifier(x, s, z, q_min, q_max), s, z), s


def par_groupes(x: list[float], n_bits: int, g: int) -> list[float]:
    """Une échelle symétrique par groupe de g valeurs consécutives."""
    sortie = []
    for debut in range(0, len(x), g):
        sortie += aller_retour(x[debut:debut + g], n_bits)[0]
    return sortie


def erreur_relative(x: list[float], x_hat: list[float]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(x, x_hat)) / sum(a * a for a in x))


# ---------------------------------------------------------------- mémoire
def octets_poids(n_params: float, n_bits: float, g: int | None = None, octets_echelle: float = 2.0) -> float:
    """Θ × bits / 8, plus une échelle (de octets_echelle octets) par groupe de g poids."""
    total = n_params * n_bits / 8
    if g is not None:
        total += n_params / g * octets_echelle
    return total


def empaqueter_int4(q: list[int]) -> bytes:
    """Deux entiers de −8 à 7 par octet : on les décale de 8 pour les ramener dans 0..15."""
    if len(q) % 2 or any(not -8 <= v <= 7 for v in q):
        raise ValueError("il faut un nombre pair d'entiers entre −8 et 7")
    return bytes(((a + 8) & 0xF) | (((b + 8) & 0xF) << 4) for a, b in zip(q[0::2], q[1::2]))


def depaqueter_int4(donnees: bytes) -> list[int]:
    sortie = []
    for octet in donnees:
        sortie += [(octet & 0xF) - 8, (octet >> 4) - 8]
    return sortie


# ---------------------------------------------------------------- NF4
def grille_nf4(decalage: float = 0.9677083) -> list[float]:
    """16 niveaux pris aux quantiles d'une loi normale (8 positifs, 7 négatifs, 0 exact), ramenés dans [−1, 1]."""
    nd = NormalDist()
    def pas(a: float, b: float, n: int) -> list[float]:
        return [a + (b - a) * i / (n - 1) for i in range(n)]
    positifs = [nd.inv_cdf(p) for p in pas(decalage, 0.5, 9)[:-1]]
    negatifs = [-nd.inv_cdf(p) for p in pas(decalage, 0.5, 8)[:-1]]
    niveaux = sorted(positifs + negatifs + [0.0])
    return [v / niveaux[-1] for v in niveaux]


def quantifier_grille(x: list[float], grille: list[float], g: int) -> list[float]:
    """Par blocs de g : échelle absmax, puis le niveau de la grille le plus proche de x / absmax."""
    sortie = []
    for debut in range(0, len(x), g):
        bloc = x[debut:debut + g]
        a = max(abs(v) for v in bloc)
        sortie += [a * min(grille, key=lambda c: abs(v / a - c)) for v in bloc]
    return sortie


def eqm(x: list[float], x_hat: list[float]) -> float:
    return sum((a - b) ** 2 for a, b in zip(x, x_hat)) / len(x)


def arrondir(v: list[float], n: int = 4) -> list[float]:
    return [round(a, n) + 0.0 for a in v]


def main() -> None:
    print("1. Exemple à la main : x = [0.523, -1.137, 0.047, 2.54], symétrique")
    x = [0.523, -1.137, 0.047, 2.54]
    for n_bits in (8, 4):
        s, z, q_min, q_max = params_symetrique(x, n_bits)
        q = quantifier(x, s, z, q_min, q_max)
        x_hat = dequantifier(q, s, z)
        err = [abs(a - b) for a, b in zip(x, x_hat)]
        print(f"  INT{n_bits} : s = {s:.6f} ; q = {q} ; x̂ = {arrondir(x_hat)} ; erreur max = {max(err):.4f} ≤ s/2 = {s / 2:.4f}")
        assert max(err) <= s / 2 + 1e-12
    assert quantifier(x, 0.02, 0, -127, 127) == [26, -57, 2, 127]
    assert quantifier(x, 2.54 / 7, 0, -7, 7) == [1, -3, 0, 7]

    print("2. Asymétrique : plage [-0.51, 2.04], INT8 sur 0..255")
    xa = [-0.51, 0.004, 0.7333, 2.04]
    s, z, q_min, q_max = params_asymetrique(xa, 8)
    qa = quantifier(xa, s, z, q_min, q_max)
    print(f"  s = {s:.4f} ; z = {z} ; q = {qa} ; x̂ = {arrondir(dequantifier(qa, s, z))}")
    s_sym = params_symetrique(xa, 8)[0]
    print(f"  pas symétrique = {s_sym:.6f} ; pas asymétrique = {s:.6f} : {s_sym / s:.2f} fois plus fin")
    assert z == 51 and qa == [0, 51, 124, 255] and dequantifier([z], s, z) == [0.0]
    assert max(abs(a - b) for a, b in zip(xa, dequantifier(qa, s, z))) <= s / 2 + 1e-12

    print("3. Borne s/2 et erreur quadratique s²/12 sur 10 000 valeurs")
    rng = random.Random(73)
    valeurs = [rng.uniform(-1.0, 1.0) for _ in range(10_000)]
    s, z, q_min, q_max = params_symetrique(valeurs, 8)
    approx = dequantifier(quantifier(valeurs, s, z, q_min, q_max), s, z)
    erreurs = [a - b for a, b in zip(valeurs, approx)]
    rapport = sum(e * e for e in erreurs) / len(erreurs) / (s * s / 12)
    print(f"  erreur max / (s/2) = {max(abs(e) for e in erreurs) / (s / 2):.4f} ; EQM / (s²/12) = {rapport:.4f}")
    assert max(abs(e) for e in erreurs) <= s / 2 + 1e-12 and 0.95 < rapport < 1.05
    hors_plage = quantifier([3.0], s, 0, q_min, q_max)
    assert dequantifier(hors_plage, s)[0] == 127 * s                     # écrêtage : erreur 3 − 127 s, bien > s/2

    print("4. Une valeur aberrante gonfle s ; les groupes l'atténuent (256 poids N(0 ; 0.02), INT4)")
    rng = random.Random(73)
    w = [rng.gauss(0.0, 0.02) for _ in range(256)]
    w[10] = 1.0
    normaux = [i for i in range(256) if i != 10]
    for nom, w_hat in (("par tenseur", aller_retour(w, 4)[0]), ("groupes de 32", par_groupes(w, 4, 32))):
        e = erreur_relative([w[i] for i in normaux], [w_hat[i] for i in normaux])
        zeros = sum(1 for i in normaux if w_hat[i] == 0.0)
        print(f"  {nom:<13} : erreur relative sur les 255 poids normaux = {e:.4f} ; poids mis à zéro = {zeros}")
    assert erreur_relative([w[i] for i in normaux], [aller_retour(w, 4)[0][i] for i in normaux]) == 1.0
    assert round(erreur_relative([w[i] for i in normaux], [par_groupes(w, 4, 32)[i] for i in normaux]), 4) == 0.3515
    lignes = [[0.012, -0.007, 0.003, 0.009], [1.2, -2.5, 0.4, 1.9]]
    plat = lignes[0] + lignes[1]
    tenseur = aller_retour(plat, 8)[0]
    canal = aller_retour(lignes[0], 8)[0] + aller_retour(lignes[1], 8)[0]
    e_t, e_c = erreur_relative(lignes[0], tenseur[:4]), erreur_relative(lignes[0], canal[:4])
    print(f"  ligne de petits poids, INT8 : erreur relative {e_t:.4f} par tenseur, {e_c:.4f} par canal")
    assert round(e_t, 3) == 0.837 and e_c < 0.005

    print("5. Mémoire des poids d'un modèle de 7 milliards de paramètres")
    n = 7e9
    for nom, octets in (("FP16", octets_poids(n, 16)), ("INT8", octets_poids(n, 8)), ("INT4", octets_poids(n, 4)),
                        ("INT4, groupes de 128", octets_poids(n, 4, g=128)),
                        ("NF4, blocs de 64, échelles FP32", octets_poids(n, 4, g=64, octets_echelle=4))):
        print(f"  {nom:<31} : {octets / 1e9:.4f} Go ({8 * octets / n:.4f} bits par poids)")
    assert (octets_poids(n, 16), octets_poids(n, 8), octets_poids(n, 4)) == (14e9, 7e9, 3.5e9)
    assert octets_poids(n, 4, g=128) - 3.5e9 == 109_375_000
    bits_dq = 8 / 64 + 32 / (64 * 256)                                    # double quantification de QLoRA
    print(f"  double quantification : {32 / 64} → {bits_dq:.4f} bit d'échelle par poids ;"
          f" NF4 + DQ = {n * (4 + bits_dq) / 8 / 1e9:.4f} Go")
    assert round(bits_dq, 3) == 0.127 and round(n * (4 + bits_dq) / 8 / 1e9, 3) == 3.611
    q = [-8, 7, 0, -1, 3, -5]
    paquet = empaqueter_int4(q)
    print(f"  empaquetage INT4 : {q} → {len(paquet)} octets {paquet.hex()} → {depaqueter_int4(paquet)}")
    assert depaqueter_int4(paquet) == q and len(paquet) == 3

    print("6. Produit scalaire quantifié (256 coordonnées, INT8 symétrique)")
    rng = random.Random(7)
    wv = [rng.gauss(0.0, 0.02) for _ in range(256)]
    xv = [rng.uniform(-1.0, 1.0) for _ in range(256)]
    s_w, _, lo, hi = params_symetrique(wv, 8)
    s_x = params_symetrique(xv, 8)[0]
    q_w, q_x = quantifier(wv, s_w, 0, lo, hi), quantifier(xv, s_x, 0, lo, hi)
    exact = sum(a * b for a, b in zip(wv, xv))
    poids_seuls = sum(a * b for a, b in zip(dequantifier(q_w, s_w), xv))
    borne = s_w / 2 * sum(abs(v) for v in xv)
    ecart_type = s_w * math.sqrt(sum(v * v for v in xv)) / math.sqrt(12)  # erreurs indépendantes, uniformes sur ±s/2
    entier = sum(a * b for a, b in zip(q_w, q_x))                         # accumulation entière, comme un noyau INT8
    w8a8 = s_w * s_x * entier
    print(f"  exact = {exact:.6f} ; poids INT8 = {poids_seuls:.6f} ; écart = {abs(exact - poids_seuls):.2e}")
    print(f"  borne pire cas (s/2)‖x‖₁ = {borne:.2e} ; écart type attendu s‖x‖₂/√12 = {ecart_type:.2e}")
    print(f"  poids et entrées INT8 : Σ q_w q_x = {entier} (entier) ; s_w s_x Σ q_w q_x = {w8a8:.6f}")
    assert abs(exact - poids_seuls) <= borne and abs(exact - poids_seuls) < 3 * ecart_type
    assert abs(w8a8 - sum(a * b for a, b in zip(dequantifier(q_w, s_w), dequantifier(q_x, s_x)))) < 1e-12

    print("7. NF4 : 16 niveaux aux quantiles de la loi normale")
    nf4 = grille_nf4()
    print(f"  niveaux = {arrondir(nf4)}")
    publiee = [-1.0, -0.6961928, -0.5250731, -0.3949175, -0.2844414, -0.1847734, -0.0910500, 0.0,
               0.0795803, 0.1609302, 0.2461123, 0.3379152, 0.4407098, 0.5626170, 0.7229568, 1.0]
    assert len(nf4) == 16 and max(abs(a - b) for a, b in zip(nf4, publiee)) < 1e-6
    rng = random.Random(73)
    poids = [rng.gauss(0.0, 0.02) for _ in range(4096)]
    uniforme = [i / 7 for i in range(-7, 8)]
    e_uni = eqm(poids, quantifier_grille(poids, uniforme, 64))
    e_nf4 = eqm(poids, quantifier_grille(poids, nf4, 64))
    print(f"  4 096 poids gaussiens, blocs de 64 : EQM INT4 uniforme = {e_uni:.3e} ; EQM NF4 = {e_nf4:.3e} ; rapport = {e_uni / e_nf4:.2f}")
    assert e_nf4 < e_uni and round(e_uni / e_nf4, 2) == 1.53

    print("8. QLoRA : mémoire d'un fine-tuning de 7 milliards de paramètres (4 copies par poids entraîné, 2 octets)")
    lora = 128 * 16 * (4096 + 4096)                                       # rang 16 sur 128 matrices 4096 × 4096 (étape 73)
    complet = 4 * n * 2
    lora_fp16 = n * 2 + 4 * lora * 2
    qlora = n * (4 + bits_dq) / 8 + 4 * lora * 2
    print(f"  complet = {complet / 1e9:.1f} Go ; LoRA sur base FP16 = {lora_fp16 / 1e9:.2f} Go ; QLoRA = {qlora / 1e9:.2f} Go (hors activations)")
    assert lora == 16_777_216 and complet == 56e9 and round(lora_fp16 / 1e9, 2) == 14.13 and round(qlora / 1e9, 2) == 3.75

    print("9. Entrées invalides refusées")
    for appel in (lambda: params_symetrique([0.0, 0.0], 8), lambda: empaqueter_int4([9, 0])):
        try:
            appel()
        except ValueError as e:
            print(f"  ValueError : {e}")
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Exemple à la main : x = [0.523, -1.137, 0.047, 2.54], symétrique
  INT8 : s = 0.020000 ; q = [26, -57, 2, 127] ; x̂ = [0.52, -1.14, 0.04, 2.54] ; erreur max = 0.0070 ≤ s/2 = 0.0100
  INT4 : s = 0.362857 ; q = [1, -3, 0, 7] ; x̂ = [0.3629, -1.0886, 0.0, 2.54] ; erreur max = 0.1601 ≤ s/2 = 0.1814
…
  erreur max / (s/2) = 0.9999 ; EQM / (s²/12) = 0.9987
…
  par tenseur   : erreur relative sur les 255 poids normaux = 1.0000 ; poids mis à zéro = 255
  groupes de 32 : erreur relative sur les 255 poids normaux = 0.3515 ; poids mis à zéro = 67
…
  INT4, groupes de 128            : 3.6094 Go (4.1250 bits par poids)
  double quantification : 0.5 → 0.1270 bit d'échelle par poids ; NF4 + DQ = 3.6111 Go
…
  borne pire cas (s/2)‖x‖₁ = 2.73e-02 ; écart type attendu s‖x‖₂/√12 = 1.15e-03
  poids et entrées INT8 : Σ q_w q_x = 19933 (entier) ; s_w s_x Σ q_w q_x = 0.067711
…
  4 096 poids gaussiens, blocs de 64 : EQM INT4 uniforme = 5.086e-06 ; EQM NF4 = 3.314e-06 ; rapport = 1.53
…
  complet = 56.0 Go ; LoRA sur base FP16 = 14.13 Go ; QLoRA = 3.75 Go (hors activations)
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : quantifier tient en deux lignes, une division arrondie et une multiplication. Tout le travail est dans le choix de l'échelle : sa granularité, sa plage et sa grille décident de ce que le modèle perd.

### Avec une bibliothèque (extrait)

Les bibliothèques du marché appliquent ces formules à des modèles entiers. Avec Hugging Face transformers et bitsandbytes, par exemple, le chargement en NF4 qui sert de base à QLoRA se règle ainsi ; les noms des paramètres sont ceux de la documentation et doivent être vérifiés pour la version installée.

```python
# [extrait] — chargement en 4 bits avec transformers + bitsandbytes, non exécuté par le harnais (carte graphique requise)
import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",               # la grille NF4 du point 7
    bnb_4bit_use_double_quant=True,          # la double quantification des échelles (point 5)
    bnb_4bit_compute_dtype=torch.bfloat16,   # chaque bloc est déquantifié en 16 bits au moment du calcul
)
modele = AutoModelForCausalLM.from_pretrained("<modèle ouvert retenu>", quantization_config=config)
```

`load_in_4bit` et `bnb_4bit_quant_type="nf4"` choisissent la grille du point 7 ; `bnb_4bit_use_double_quant` ramène le surcoût des échelles de 0,5 à environ 0,127 bit par poids ; `bnb_4bit_compute_dtype` fixe le format dans lequel les blocs sont déquantifiés avant chaque produit, ce qui rappelle qu'une quantification des seuls poids économise la mémoire, pas les opérations. Un adaptateur LoRA s'ajoute ensuite sur ce modèle, comme à l'étape 73. Les formules de ce fichier suffisent pour prévoir la mémoire et l'erreur avant de télécharger quoi que ce soit, et pour vérifier ce que fait une bibliothèque au lieu de le croire.

## Squelette algorithmique

Trois algorithmes. Le premier quantifie un tenseur par groupes, en symétrique ou en asymétrique : en entrée, les valeurs réelles, le nombre de bits et la taille de groupe ; en sortie, les entiers et une échelle (et un point zéro) par groupe. Le deuxième déquantifie. Le troisième calcule un produit scalaire en entiers.

```text
ALGORITHME QuantifierParGroupes
ENTRÉES : valeurs x₁ … x_N, nombre de bits n, taille de groupe g, mode ∈ {symétrique, asymétrique}
SORTIE  : entiers q₁ … q_N, et pour chaque groupe : échelle s, point zéro z

  POUR CHAQUE groupe G de g valeurs consécutives FAIRE
      SI mode = symétrique ALORS
          q_max ← 2^(n−1) − 1 ; q_min ← −q_max ; a ← max |xᵢ| sur G
          SI a = 0 ALORS ERREUR « groupe nul » FIN SI
          s ← a / q_max ; z ← 0
      SINON
          q_min ← 0 ; q_max ← 2^n − 1 ; lo ← min G ; hi ← max G
          SI hi = lo ALORS ERREUR « plage nulle » FIN SI
          s ← (hi − lo) / (q_max − q_min) ; z ← q_min − arrondi(lo / s)
      FIN SI
      POUR CHAQUE xᵢ DANS G FAIRE
          qᵢ ← min(q_max, max(q_min, arrondi(xᵢ / s) + z))
      FIN POUR
      mémoriser (s, z) pour G
  FIN POUR
  SI n = 4 ALORS ranger les entiers deux par octet FIN SI
  RETOURNER q, échelles

ALGORITHME Déquantifier
  POUR CHAQUE entier qᵢ, du groupe d'échelle s et de point zéro z FAIRE
      x̂ᵢ ← s × (qᵢ − z)                              (|xᵢ − x̂ᵢ| ≤ s/2 dans la plage)
  FIN POUR

ALGORITHME ProduitScalaireEntier
ENTRÉES : entiers q_w et q_x (symétriques), échelles s_w et s_x
  acc ← 0                                           (entier de 32 bits)
  POUR i DE 1 À d FAIRE acc ← acc + q_w,i × q_x,i FIN POUR
  RETOURNER s_w × s_x × acc                          (une seule multiplication réelle)
```

**Complexité :** quantifier N valeurs coûte O(N) en temps, deux passes par groupe (le maximum, puis l'arrondi) ; la mémoire de sortie vaut N × n bits pour les entiers, plus N / g échelles. Déquantifier coûte O(N). Le produit scalaire entier coûte O(d) multiplications d'entiers et une seule multiplication réelle. La quantification par une grille comme NF4 cherche le niveau le plus proche parmi 16 : O(16 N) avec la recherche naïve du programme, O(N log 16) par dichotomie dans la grille triée. Le coût qui compte en production n'est pas celui de la quantification, faite une fois, mais celui de la lecture des poids à chaque token : il baisse dans le rapport des bits.

**Du squelette au code :** la branche symétrique est `params_symetrique`, la branche asymétrique `params_asymetrique`, l'arrondi suivi de la mise aux bornes est `quantifier`, et la boucle sur les groupes est `par_groupes`. Le rangement deux par octet est `empaqueter_int4`. Déquantifier est `dequantifier`. Le produit scalaire entier est la ligne `entier = sum(a * b for a, b in zip(q_w, q_x))` suivie de `w8a8 = s_w * s_x * entier` dans le bloc 6 de `main`. La variante par grille est `quantifier_grille`, avec `grille_nf4` pour la grille.

## Cas d'usage réels aux Émirats

Les tailles de modèles, les budgets de mémoire, les bandes passantes et les volumes ci-dessous sont illustratifs ; les nombres qui en découlent sont vérifiés par le programme quand ils y figurent. L'effet d'une quantification sur la qualité se mesure toujours sur les tâches réelles de l'agent.

### Banque — INT8 ou INT4 pour un modèle hébergé sur site

Une banque de détail de Dubaï héberge un modèle ouvert de 7 milliards de paramètres pour extraire, des relevés et des attestations de salaire, le JSON qui alimente l'outil de ratio d'endettement de la CBUAE (toutes les mensualités, la nouvelle comprise, sous 50 % du revenu). En 16 bits, les poids occupent 14 Go ; en INT8, 7 Go ; en INT4 par groupes de 128, 3,61 Go, ce qui libère de la place pour le cache des sessions (étape 72 bis). L'équipe ne choisit pas sur la mémoire seule : elle passe les trois versions sur 500 dossiers anonymisés de référence et mesure le taux de JSON valides (étape 11) et la correspondance exacte du salaire extrait (étape 64). Le point 6 lui dit où regarder : l'erreur d'un produit scalaire croît avec le pas s, multiplié par environ 18 entre INT8 et INT4, et ce sont les chiffres, les montants et les dates qui souffrent les premiers d'une petite déformation des sorties. Si l'INT4 fait baisser la correspondance exacte du salaire, la banque garde l'INT8, parce qu'un salaire mal lu fausse directement le ratio d'endettement. Sans cette évaluation, la version la plus compacte serait déployée sur la seule foi de sa taille. Les indicateurs suivis sont la correspondance exacte du salaire et le taux de dossiers renvoyés à un analyste, comparés entre versions.

### Secteur public — vérifier l'arabe après quantification

Une entité de services publics en ligne accessible par UAE Pass sert un modèle arabe ouvert, comme Jais ou Falcon, quantifié pour tenir sur ses serveurs. L'équipe avait évalué la version quantifiée sur un jeu de questions majoritairement anglais, et la moyenne n'avait presque pas bougé. Or rien ne garantit que l'erreur d'arrondi se répartisse également entre les langues : les poids qui servent surtout aux tokens arabes, moins fréquents dans certaines données d'entraînement, peuvent avoir des plages différentes, et une échelle par tenseur les traite comme les autres (point 4). L'équipe refait donc l'évaluation séparément en arabe standard, en dialecte émirien et en anglais, et compare les versions en 16 bits, en INT8 et en INT4 par groupes. Elle vérifie aussi la translittération des noms propres et la lecture des numéros d'Emirates ID (15 chiffres commençant par 784), où une erreur d'un caractère suffit à bloquer une démarche. Sans cette évaluation par langue, une baisse de qualité en arabe passerait inaperçue derrière une moyenne dominée par l'anglais. L'indicateur suivi est le taux de démarches abouties sans transfert, par langue et par version du modèle.

### BTP — un modèle qui tient sur une tablette de chantier

Un groupe de construction qui mène de grands chantiers à Dubaï veut classer hors ligne, sur des tablettes, les bons de livraison et les comptes rendus de chantier, avec un petit modèle dense de 3 milliards de paramètres. En 16 bits, il demande 6 Go de poids, trop pour les tablettes du parc ; en INT4 par groupes de 128 avec des échelles de 2 octets, 3 × 10⁹ × 4,125 / 8 ≈ 1,55 Go, ce qui laisse de la place au système et au cache. L'équipe vérifie que le format de fichier range réellement deux entiers par octet (point 5) : une première exportation maison les stockait un par octet et occupait autant de place qu'en INT8. Elle compare ensuite le classement des documents, en 16 bits sur un serveur et en INT4 sur la tablette, sur un lot de bons de livraison réels, et elle vérifie que les montants HT, la TVA à 5 % et les retenues de garantie sont extraits à l'identique. Sans le calcul de mémoire, le déploiement échoue au premier appareil ; sans la comparaison, une baisse de qualité retarderait le règlement des fournisseurs. L'indicateur suivi est la justesse du classement sur tablette, mesurée chaque mois sur un échantillon vérifié à la main.

### Crypto — la quantification accélère le décodage

Une plateforme d'actifs virtuels agréée par la VARA fait tourner sur ses propres cartes un agent de surveillance qui commente chaque alerte de liquidité. Pour une seule séquence, chaque token généré oblige la carte à relire tous les poids : le décodage est limité par la bande passante mémoire, pas par le calcul (étape 72 bis). Avec une bande passante illustrative de 2 000 Go/s, un modèle de 7 milliards de paramètres en 16 bits (14 Go) plafonne à 2 000 / 14 ≈ 143 tokens par seconde, et la version INT4 par groupes de 128 (3,61 Go) à 2 000 / 3,61 ≈ 554 tokens par seconde : c'est une borne haute, que le calcul de déquantification et l'attention réduisent en pratique. L'équipe mesure donc la latence réelle sur ses alertes, et elle garde la version en 16 bits pour le rapport détaillé qui part à la conformité, où la qualité prime sur la vitesse. Sans cette distinction, elle aurait cru que la quantification divise le calcul par quatre, alors qu'elle divise surtout la mémoire à lire. L'indicateur suivi est le p95 du délai entre l'alerte et le premier commentaire de l'agent.

### RH — un adaptateur entraîné sur une seule carte

Un cabinet RH multi-émirats veut un adaptateur LoRA par grande entreprise cliente, pour rédiger lettres d'offre et avenants dans le ton de chacune (étape 73). Un fine-tuning complet du modèle de 7 milliards de paramètres demanderait, avec la convention de quatre copies par poids sur 2 octets, 56 Go avant les activations ; un LoRA sur une base en 16 bits, 14,13 Go ; QLoRA, avec la base en NF4 et la double quantification, environ 3,75 Go. Le cabinet peut ainsi entraîner ses adaptateurs sur une carte de taille courante plutôt que de louer une grappe de serveurs, et il garde les lettres de ses clients dans son propre environnement, ce qui simplifie le respect de la PDPL. L'équipe retient une règle tirée du point 8 : l'adaptateur a appris à corriger la base quantifiée, donc on le sert avec cette même base, et toute fusion suivie d'une nouvelle quantification donne un modèle à réévaluer. Les montants, comme l'indemnité de fin de service, restent calculés par l'outil `gratuite_fin_de_service`. Sans QLoRA, le projet aurait été abandonné pour son coût matériel. L'indicateur suivi est le taux de lettres validées par le juriste sans correction, par client et par version d'adaptateur.

### Assurance — une valeur aberrante qui éteint toute une couche

Un assureur auto et santé quantifie lui-même, avec un script maison, un petit modèle de tri des déclarations de sinistre, en INT4 avec une seule échelle par matrice pour faire simple. En recette, le modèle classe presque tous les dossiers dans la même catégorie. Le point 4 donne l'explication : dans une des matrices, un poids vaut 1,0 alors que les autres tournent autour de 0,02 ; l'échelle par tenseur vaut alors 1/7, et tous les poids normaux s'arrondissent à zéro, avec une erreur relative de 100 %. Une échelle par groupe de 32 ramène l'erreur à 35 % sur cet exemple, et une échelle par groupe plus petit ou par canal la réduit encore. L'équipe adopte une quantification par groupes, ajoute au script un contrôle qui signale toute matrice dont plus de 90 % des poids quantifiés valent zéro, et compare chaque couche quantifiée à l'originale sur des entrées fixes, comme un test d'oracle. Sans ce contrôle, des sinistres frauduleux auraient pu passer en traitement automatique, alors que l'assureur, supervisé par la CBUAE, doit pouvoir expliquer ses décisions. L'indicateur suivi est la part de poids mis à zéro par couche, avec l'écart de classement entre le modèle quantifié et l'original sur un jeu de référence.

## Pièges et limites

- **Oublier l'empaquetage.** Des entiers de 4 bits rangés un par octet prennent la place de l'INT8 ; la mémoire annoncée suppose deux valeurs par octet.
- **Une seule échelle pour un tenseur qui contient une valeur aberrante.** Tous les autres poids s'arrondissent à zéro ; on quantifie par groupes ou par canaux.
- **Mesurer la plage des activations sur des données non représentatives.** Les valeurs hors plage sont écrêtées et l'erreur n'est plus bornée par s/2.
- **Croire que quantifier les poids réduit le calcul.** Sans calcul en entiers, on gagne la mémoire et la bande passante, pas les opérations.
- **Évaluer sur une moyenne.** La perte se concentre parfois sur une langue, sur les chiffres ou sur un format ; on évalue par segment.

### Exercice feuille blanche

1. Sans regarder le code, écrire `params_symetrique`, `quantifier` et `dequantifier`, puis retrouver q = [26, −57, 2, 127] et l'erreur maximale de 0,007 pour l'exemple.
2. Prédire, puis vérifier : en INT4 asymétrique (entiers de 0 à 15) sur la plage [−0,51 ; 2,04], que valent s et z ? (Réponse : s = 2,55 / 15 = 0,17 et z = 0 − round(−0,51 / 0,17) = 3, puisque −0,51 / 0,17 = −3.)
3. Trouver le bug : dans `quantifier`, `round(v / s) + z` est remplacé par `round(v / s) * z`. Que devient l'aller-retour en symétrique, et pourquoi ? (Réponse : z vaut 0 en symétrique, donc tous les entiers valent 0 et toute la matrice est reconstruite à zéro ; l'`assert` sur l'erreur maximale ≤ s/2 échoue dès le premier exemple.)

## Pour aller plus loin

GPTQ quantifie les poids couche par couche en corrigeant, poids après poids, l'erreur déjà commise grâce à une approximation du second ordre ; AWQ protège les canaux de poids qui multiplient les plus grandes activations en les remettant à l'échelle avant la quantification. LLM.int8() traite à part, en 16 bits, les rares dimensions d'activation aux valeurs extrêmes et quantifie le reste en INT8. Les formats de fichiers des moteurs embarqués, comme GGUF, combinent des groupes et des échelles à plusieurs niveaux. Les formats flottants de 8 bits (FP8), pris en charge par les cartes récentes, gardent un exposant et conviennent mieux aux activations dont la plage varie beaucoup. La quantification du cache KV (étape 72 bis) applique les mêmes formules aux clés et aux valeurs pour loger plus de sessions.

> Étape 73 bis du parcours · Prérequis : [Descente de gradient et LoRA](<73-Optimisation-et-Fine-Tuning.md>) · Suite : [Distillation maître-élève](<73c-Distillation-Maitre-Eleve.md>)
