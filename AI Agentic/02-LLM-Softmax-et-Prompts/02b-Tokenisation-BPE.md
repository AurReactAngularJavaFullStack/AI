# Étape 02 bis — LLM — Tokenisation BPE

**Dossier :** 02-LLM-Softmax-et-Prompts

> Étape 02 bis du parcours · Prérequis : [Softmax et température](<02-Softmax-Temperature-Prochain-Token.md>) · Suite : [Fondements : softmax et Bellman](<03-Fondements-Softmax-et-LLM.md>)

## Définition

Un LLM ne lit pas des caractères ni des mots : il lit des **tokens**, des morceaux de texte pris dans un vocabulaire fixe, chacun désigné par un numéro. La softmax de l'étape 2 tire le prochain token parmi ces |V| entrées, et tout ce que l'on paie, tout ce qui remplit la fenêtre de contexte, se compte en tokens. Le **BPE** (Byte Pair Encoding, « codage par paires d'octets ») construit ce vocabulaire par une règle très simple : on part des symboles de base (les caractères, ou les 256 octets), on compte les paires de symboles voisins dans un corpus, on remplace la paire la plus fréquente par un nouveau symbole, et l'on recommence k fois. L'**encodage** d'un texte rejoue ces fusions dans l'ordre où elles ont été apprises ; le **décodage** recolle simplement les tokens. La version « octets » part des 256 valeurs d'octet : elle peut encoder n'importe quel texte sans jamais rencontrer de symbole inconnu.

## Rôle dans un agent

La tokenisation est la première et la dernière opération de chaque appel au modèle, dans la boucle percevoir → décider → agir → observer de l'étape 1. Au moment de percevoir, le prompt système, les définitions d'outils en JSON, l'historique et les résultats d'outils sont découpés en tokens : c'est ce nombre, et non le nombre de caractères, qui est facturé (étape 72), qui remplit la fenêtre de contexte (étape 13 ter) et qui consomme les limites de débit. Au moment de décider, le modèle produit un token à la fois, y compris le nom de l'outil et chaque morceau de ses arguments ; la latence de la réponse croît avec le nombre de tokens de sortie, à raison d'un pas de calcul par token (étape 33 bis). Trois composants de l'agent ont donc besoin d'un **compteur de tokens** : le garde-fou de budget, qui refuse un appel trop cher ; la mémoire de travail, qui décide quand résumer ; le retriever, qui découpe les documents en morceaux de taille bornée (étape 18). Un quatrième en a besoin sans le savoir : toute tâche « au caractère près » (recopier un IBAN, compter des lettres, comparer deux translittérations) se joue sur des tokens qui ne respectent pas les caractères, et doit être confiée à un outil.

Pour rester indépendant du fournisseur, on traite le comptage comme un **port**, au sens de l'architecture hexagonale : l'agent appelle `compter_tokens(texte)`, et des adaptateurs interchangeables répondent, soit avec le tokenizer local d'un modèle hébergé, soit avec le point de terminaison de comptage d'une API, soit avec une estimation calibrée par langue quand rien d'autre n'est disponible.

## Équation complète

Le texte est d'abord **pré-découpé** en morceaux w (« ▁loyer », « ▁60000 », « ▁. »), puis chaque morceau est écrit comme une suite de symboles de l'ensemble de base B. Fréquence d'une paire adjacente (a, b), où n(w) compte les occurrences du morceau w et c(w) les positions de w où a est immédiatement suivi de b :

$$
f(a,b) = \sum_{w} n(w)\; c(w)
$$

Choix de la fusion, avec un départage déterministe (à fréquence égale, la plus petite paire dans l'ordre lexicographique) :

$$
(a^\star, b^\star) = \arg\max_{(a,b)} f(a,b)
$$

Nombre total de tokens du corpus, où |w| est la longueur de w en tokens :

$$
N = \sum_{w} n(w)\, |w|
$$

Effet d'une fusion, où m(w) est le nombre de remplacements faits dans w :

$$
N_{\text{avant}} - N_{\text{après}} = \sum_{w} n(w)\; m(w)
$$

$$
m(w) = c(w) \quad \text{si } a \neq b, \qquad m(w) = \sum_{\text{séries de } a} \left\lfloor \ell / 2 \right\rfloor \quad \text{si } a = b
$$

Taille du vocabulaire après k fusions :

$$
|V| = |B| + k
$$

Estimation de l'étape 4 et écart au compte réel, où L est le nombre de caractères du texte et ρ = L / N le nombre moyen de caractères par token :

$$
\hat{N} = \left\lceil L / 4 \right\rceil
$$

$$
\frac{N}{\hat{N}} \approx \frac{4}{\rho}
$$

## Décryptage des symboles

$$
w
$$

**Sens :** un morceau du pré-découpage, écrit comme une suite de tokens ; l'espace reste collé au mot qui le suit · **Type / plage :** tuple de chaînes (niveau caractères) ou d'objets `bytes` (niveau octets) · **Variable Python :** `mot`, clé du dictionnaire `mots`

$$
n(w)
$$

**Sens :** nombre d'occurrences du morceau w dans le corpus d'entraînement · **Type / plage :** entier ≥ 1 · **Variable Python :** valeur `mots[mot]`

$$
B
$$

**Sens :** ensemble des symboles de base : les caractères vus dans le corpus, ou les 256 octets · **Type / plage :** ensemble fini · **Variable Python :** `modele.base`

$$
c(w)
$$

**Sens :** nombre de positions de w où a est suivi de b, chevauchements compris (« 0000 » contient trois fois la paire (0, 0)) · **Type / plage :** entier ≥ 0 · **Variable Python :** calculé dans `compter_paires`

$$
f(a,b)
$$

**Sens :** fréquence de la paire adjacente (a, b) dans tout le corpus · **Type / plage :** entier ≥ 0 · **Variable Python :** `compter_paires(mots)[(a, b)]`

$$
(a^\star, b^\star)
$$

**Sens :** la paire retenue pour la fusion : la plus fréquente, la plus petite en cas d'égalité · **Type / plage :** couple de tokens · **Variable Python :** `meilleure`

$$
m(w)
$$

**Sens :** nombre de remplacements que la fusion fait réellement dans w, de gauche à droite et sans chevauchement · **Type / plage :** entier, 0 ≤ m(w) ≤ c(w) · **Variable Python :** deuxième valeur renvoyée par `fusionner`, prévue par `remplacements_prevus`

$$
\ell
$$

**Sens :** longueur d'une série maximale de symboles identiques a, a, …, a dans w · **Type / plage :** entier ≥ 1 · **Variable Python :** `serie`

$$
N
$$

**Sens :** nombre total de tokens du corpus (ou d'un texte encodé) · **Type / plage :** entier ≥ 0 · **Variable Python :** `nombre_de_tokens(mots)`, `len(encoder(texte, modele))`

$$
k
$$

**Sens :** nombre de fusions apprises ; dans ce fichier, k ne désigne pas le top-k de l'étape 2 · **Type / plage :** entier ≥ 0 · **Variable Python :** `k`, `len(modele.fusions)`

$$
V
$$

**Sens :** le vocabulaire : la base suivie des tokens créés par les fusions, dans l'ordre · **Type / plage :** liste de tokens, chacun avec son numéro · **Variable Python :** `modele.vocabulaire()`

$$
L
$$

**Sens :** nombre de caractères d'un texte · **Type / plage :** entier ≥ 0 · **Variable Python :** `len(texte)`

$$
\rho
$$

**Sens :** nombre moyen de caractères par token, pour un texte et un tokenizer donnés (à ne pas confondre avec l'utilisation ρ des files d'attente de l'étape 69) · **Type / plage :** réel > 0 · **Variable Python :** `len(texte) / len(tokens)`

$$
\hat{N}
$$

**Sens :** estimation du nombre de tokens par ⌈L/4⌉, celle qu'utilise la fonction `estimer_tokens` de l'étape 4 · **Type / plage :** entier ≥ 0 · **Variable Python :** `math.ceil(len(texte) / 4)`

## Démonstration

### 1. Le pré-découpage et le passage en symboles ne perdent rien

Le pré-découpage applique une expression régulière à cinq branches : une suite de lettres précédée d'au plus une espace, une suite de chiffres précédée d'au plus une espace, une suite de signes de ponctuation, une suite de soulignés, une suite d'espaces. Ces branches couvrent tous les caractères possibles, parce qu'un caractère est soit une lettre, soit un chiffre, soit le souligné, soit un blanc, soit autre chose (ponctuation, symbole, marque diacritique). La fonction vérifie quand même que la concaténation des morceaux redonne le texte, et lève `ValueError` sinon. Aucune fusion ne traverse la frontière de deux morceaux : « ▁loyer » et « ▁annuel » ne fusionneront jamais en un seul token. Sur « 60000 60000 600 », on obtient les trois morceaux « 60000 », « ▁60000 » et « ▁600 ».

### 2. Une fusion retire exactement m(w) tokens, et m(w) = c(w) quand a ≠ b

La fonction `fusionner` parcourt w de gauche à droite. Quand elle trouve a en position i et b en position i + 1, elle écrit le token a + b et saute en i + 2 ; sinon elle recopie le token et avance d'une position. Chaque remplacement transforme deux tokens en un seul, donc la longueur de w baisse de 1 par remplacement : |w| − |w′| = m(w). En sommant sur tous les morceaux, pondérés par leurs occurrences, on obtient la formule de l'équation complète :

$$
N_{\text{avant}} - N_{\text{après}} = \sum_{w} n(w)\,\bigl(|w| - |w'|\bigr) = \sum_{w} n(w)\; m(w)
$$

Si a ≠ b, deux occurrences de (a, b) ne peuvent pas se chevaucher. En effet, des occurrences en positions i et i + 1 demanderaient que le symbole i + 1 vaille b (fin de la première) et a (début de la seconde), donc a = b. Le parcours ne saute donc jamais par-dessus une occurrence : il ne saute une position que juste après un remplacement, et la position sautée ne peut pas commencer une autre occurrence. Il remplace ainsi toutes les occurrences, m(w) = c(w), et la réduction vaut exactement la fréquence :

$$
N_{\text{avant}} - N_{\text{après}} = \sum_{w} n(w)\; c(w) = f(a,b)
$$

Le programme le vérifie à chacune des 40 fusions du corpus : par exemple, la paire (▁, l), de fréquence 11, fait passer N de 394 à 383.

### 3. Quand a = b, la fréquence surestime le gain : le contre-exemple des zéros

Une série maximale de ℓ symboles a consécutifs contient ℓ − 1 paires (a, a), parce que chaque position sauf la dernière commence une paire. Le parcours de gauche à droite remplace les positions (1, 2), puis (3, 4), et ainsi de suite : il fait ⌊ℓ/2⌋ remplacements. Or ⌊ℓ/2⌋ = ℓ − 1 seulement pour ℓ ≤ 2 : dès qu'une série compte trois symboles ou plus, la fréquence f compte des paires que la fusion ne peut pas toutes remplacer.

Le corpus de ce fichier en donne un exemple sans l'avoir cherché. Le montant « 60000 » y figure trois fois. Chaque occurrence contient une série de quatre zéros, donc trois paires (0, 0) et deux remplacements. La fréquence vaut 3 × 3 = 9, mais N ne baisse que de 3 × ⌊4/2⌋ = 6, de 373 à 367. Le critère glouton du BPE (fusionner la paire la plus fréquente) n'est donc le gain exact que pour les paires de deux symboles différents. Ici, il a même départagé (0, 0) et (h, e), tous deux de fréquence 9, par l'ordre lexicographique (« 0 » vient avant « h ») ; avec le gain exact, 9 contre 6, c'est (h, e) qui serait passée en premier. Les implémentations courantes gardent pourtant la fréquence, plus simple à mettre à jour : c'est une heuristique de compression, pas un optimum.

### 4. Décoder rend exactement le texte encodé

Une fusion remplace deux tokens voisins x et y par leur concaténation x + y. La concaténation de toute la suite ne change donc pas, parce que la concaténation est associative : (… x)(y …) et (… xy …) donnent la même chaîne. Par récurrence sur les fusions, la concaténation des tokens d'un morceau est toujours égale à celle de ses symboles de base, c'est-à-dire au morceau lui-même (niveau caractères) ou à ses octets UTF-8 (niveau octets). Comme le pré-découpage ne perd rien (point 1), recoller tous les tokens redonne le texte, ou ses octets ; et décoder l'UTF-8 inverse l'encodage UTF-8, qui est une bijection entre les chaînes et les suites d'octets valides. D'où decoder(encoder(t)) = t pour tout texte dont les symboles de base sont connus. Le programme le vérifie sur tout le corpus.

### 5. La taille du vocabulaire vaut |B| + k

L'entraînement part du vocabulaire B. Chaque fusion ajoute exactement un token, a + b, avec un numéro nouveau, et n'en retire aucun : a et b restent nécessaires, parce que d'autres morceaux, ou des textes jamais vus, peuvent les contenir séparément. Après k fusions, il y a donc |B| + k numéros de tokens. Si l'entraînement s'arrête avant, parce que chaque morceau tient déjà en un seul token, le compte s'arrête au nombre de fusions faites. Sur le corpus, le niveau caractères donne 48 + 40 = 88 tokens, et le programme vérifie que les 88 chaînes sont distinctes ; le niveau octets donne 256 + 60 = 316 tokens. Chaque token ajouté agrandit d'une ligne la matrice d'embeddings et d'une case la softmax de l'étape 2 : choisir k, c'est arbitrer entre des textes plus courts et un modèle plus gros.

### 6. Le repli par octets : aucun token inconnu, mais un prix

Au niveau des caractères, un caractère absent du corpus n'a pas de symbole de base. On le remplace par un token `<inconnu>`, et l'information est perdue : « Prix : 500 € » donne cinq tokens `<inconnu>` (P, x, :, 5 et €), et le décodage ne peut pas rendre le texte. Au niveau des octets, tout texte Unicode a un encodage UTF-8, qui est une suite d'octets compris entre 0 et 255, donc tous dans B. Les fusions ne font que regrouper ces octets : l'encodage ne rencontre jamais de symbole inconnu, et le point 4 garantit le retour exact. Le programme le vérifie sur l'euro, sur deux caractères chinois suivis d'un émoji, et sur des chiffres arabes-indiens.

Ce filet a un coût. Un caractère qu'aucune fusion ne couvre coûte autant de tokens que d'octets : 1 pour une lettre latine, 2 pour une lettre arabe, 3 pour « € », 4 pour un émoji. Il a aussi une conséquence pour l'affichage en flux : un token peut contenir un caractère incomplet, ou commencer au milieu d'un caractère. Sur la phrase arabe du programme, 38 tokens sur 43 ne sont pas, seuls, de l'UTF-8 valide ; le premier vaut `b'\xd8'`, le premier octet de la lettre alef. Décoder chaque token à part échoue ; un décodeur incrémental, qui garde en attente les octets d'un caractère commencé, reconstitue le texte exact.

### 7. L'estimation ⌈L/4⌉ n'est qu'une heuristique

Par définition de ρ, N = L / ρ. L'estimation de l'étape 4, ⌈L/4⌉, revient à supposer ρ = 4, si bien que le rapport entre le compte réel et l'estimation vaut environ 4/ρ. Or ρ dépend de la langue et des fusions apprises. Deux bornes encadrent N pour un tokenizer à octets : N ne dépasse jamais le nombre d'octets du texte, parce que chaque fusion ne fait que réduire le nombre de tokens ; et N est au moins égal au nombre de morceaux du pré-découpage, parce que chaque morceau donne au moins un token. Pour un texte en lettres arabes sans fusion utile, le nombre d'octets vaut environ 2L, ρ descend vers 1/2, et N peut atteindre huit fois l'estimation.

Le tokenizer jouet du programme, entraîné sur un corpus de quelques phrases, le montre. La phrase française de 43 caractères donne 16 tokens pour 11 estimés, soit 1,45 fois l'estimation ; la phrase arabe de 35 caractères (61 octets) donne 43 tokens pour 9 estimés, soit 4,78 fois ; un IBAN de 23 chiffres et lettres donne 23 tokens pour 6 estimés, soit 3,83 fois. Un tokenizer réel apprend des dizaines de milliers de fusions et se rapproche de 4 caractères par token sur l'anglais courant, d'où la règle empirique ; ce qui reste vrai à toute échelle, c'est que le rapport change d'une langue à l'autre et que les chiffres se découpent mal. Comme le coût d'entrée vaut N × Pᵢₙ (étape 72), l'erreur passe telle quelle dans le budget : au prix illustratif de 3 USD par million de tokens, 100 000 messages arabes comme celui du programme coûtent 12,90 USD au compte réel, contre 2,70 USD estimés.

### 8. Exemple fait à la main (le code reprend ces nombres)

Corpus « 60000 60000 600 ». Le pré-découpage donne trois morceaux, chacun une fois : « 60000 », « ▁60000 », « ▁600 ». La base vaut B = {▁, 0, 6}, donc |B| = 3, et N = 5 + 6 + 4 = 15.

- Paires : (6, 0) apparaît 3 fois, (0, 0) 3 + 3 + 1 = 7 fois, (▁, 6) 2 fois. **Fusion 1 : (0, 0)**, f = 7. Les séries de zéros ont pour longueurs 4, 4 et 2, d'où 2 + 2 + 1 = 5 remplacements et N = 10 : 6|00|00, ▁|6|00|00, ▁|6|00.
- Paires : (6, 00) 3 fois, (00, 00) 2 fois, (▁, 6) 2 fois. **Fusion 2 : (6, 00)**, f = 3 = gain, N = 7 : 600|00, ▁|600|00, ▁|600.
- Paires : (600, 00) 2 fois, (▁, 600) 2 fois. Égalité : la plus petite paire commence par l'espace, qui précède « 6 » dans l'ordre des caractères. **Fusion 3 : (▁, 600)**, N = 5 : 600|00, ▁600|00, ▁600.
- Paires : (600, 00) et (▁600, 00), une fois chacune. Égalité : « ▁600 » précède « 600 ». **Fusion 4 : (▁600, 00)**, N = 4 : 600|00, ▁60000, ▁600.

Le vocabulaire compte 3 + 4 = 7 tokens : ▁, 0, 6, 00, 600, ▁600, ▁60000. On remarque que « 60000 » en tête de texte coûte deux tokens, alors que « ▁60000 » n'en coûte qu'un : l'espace qui précède un mot fait partie du token.

## Effets et comportement

- **Plus de fusions, des textes plus courts, un modèle plus gros.** Chaque fusion raccourcit les textes qui ressemblent au corpus d'entraînement et ajoute une ligne à la matrice d'embeddings et une case à la softmax.
- **La langue du corpus d'entraînement fixe le prix des autres langues.** Une langue peu représentée garde des tokens courts, parfois un par octet : elle coûte plus cher, remplit plus vite le contexte et se génère plus lentement.
- **L'espace et la casse changent les tokens.** « ▁loyer » et « loyer » sont deux tokens différents ; dans le programme, « le » en tête de phrase se découpe en « l » et « e », alors que « ▁le » au milieu du texte forme un seul token.
- **Les nombres se découpent selon le corpus.** « ▁60000 », vu trois fois, devient un seul token ; un montant jamais vu reste en morceaux, et un identifiant de 23 caractères peut coûter 23 tokens.
- **Le flux de tokens n'est pas un flux de caractères.** Avec des tokens d'octets, un client qui affiche la réponse au fil de l'eau doit décoder de façon incrémentale.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| pré-découpage en morceaux w | `pre_decouper(texte)` |
| symboles de base, ensemble B | `symboles_de_base(morceau, niveau)`, `modele.base` |
| n(w) | valeurs du dictionnaire `mots` |
| f(a, b) | `compter_paires(mots)[(a, b)]` |
| (a*, b*) | `meilleure` dans `entrainer_bpe` |
| fusion et m(w) | `fusionner(mot, paire)`, `remplacements_prevus(mot, paire)` |
| N | `nombre_de_tokens(mots)` |
| V, de taille « base + k » | `modele.vocabulaire()` |
| encodage, décodage | `encoder(texte, modele)`, `decoder(tokens, modele)` |
| estimation ⌈L/4⌉ | `math.ceil(len(texte) / 4)` |

### Déroulé, ligne par ligne

**`pre_decouper(texte)`** applique `MOTIF.findall`. Sur `"60000 60000 600"`, le résultat vaut `['60000', ' 60000', ' 600']`. La garde `"".join(morceaux) != texte` lève `ValueError` si un caractère a été perdu (démonstration, point 1).

**`symboles_de_base(morceau, niveau)`** renvoie `tuple(morceau)` au niveau caractères : `' 600'` devient `(' ', '6', '0', '0')`. Au niveau octets, `morceau.encode("utf-8")` puis un objet `bytes` par octet : `'€'` devient `(b'\xe2', b'\x82', b'\xac')`.

**`compter_paires(mots)`** parcourt chaque morceau avec `zip(mot, mot[1:])`, qui donne les couples de voisins, et ajoute `n` (le nombre d'occurrences du morceau) à chaque couple. Sur l'exemple à la main : `(0, 0)` vaut 7, `(6, 0)` vaut 3 et `(' ', 6)` vaut 2.

**`fusionner(mot, paire)`** construit `sortie` de gauche à droite. Si `mot[i]` et `mot[i + 1]` forment la paire, on ajoute `a + b` et l'on avance de 2 (`i += 2`), sinon on recopie `mot[i]` et l'on avance de 1. Sur `('6', '0', '0', '0', '0')` avec `('0', '0')`, la sortie vaut `('6', '00', '00')` et `remplaces` vaut 2. Le saut de 2 est ce qui interdit les chevauchements (point 3, exercice 3).

**`remplacements_prevus(mot, paire)`** calcule m(w) sans fusionner. Si a ≠ b, elle compte les occurrences. Si a = b, elle mesure chaque série dans `serie` et ajoute `serie // 2` quand la série s'arrête ; la sentinelle `None` ajoutée en fin de tuple ferme la dernière série. Pour quatre zéros, 4 // 2 = 2.

**`nombre_de_tokens(mots)`** renvoie `sum(n * len(mot) ...)` : 15 sur l'exemple à la main, 407 sur le corpus avant toute fusion.

**`entrainer_bpe(texte, k, niveau)`**.

- `Counter(pre_decouper(texte))` compte les morceaux : le corpus en contient 89, dont 46 distincts. Chaque morceau distinct devient une clé de `mots`, sous forme de tuple de symboles.
- `base` vaut les 256 octets au niveau octets, et sinon les caractères vus, triés : 48 pour le corpus.
- Dans la boucle, `paires = compter_paires(mots)`. Si `paires` est vide, chaque morceau tient en un token et l'on s'arrête.
- `meilleure = min(paires, key=lambda p: (-paires[p], p))` prend la paire de fréquence maximale (d'où le signe moins) et, à égalité, la plus petite paire. À la fusion 3 de l'exemple, `(' ', '600')` et `('600', '00')` valent toutes deux 2, et l'espace l'emporte. Ce départage rend l'entraînement reproductible : sans lui, l'ordre d'un dictionnaire déciderait.
- `prevus` additionne `n * remplacements_prevus(mot, meilleure)` avant la fusion ; `nouveaux` reçoit les morceaux fusionnés. Deux morceaux différents ne peuvent pas devenir identiques, puisque la fusion conserve la concaténation, mais `nouveaux.get(fusionne, 0) + n` reste prudent.
- `historique` garde `(paire, f, N avant, N après, prévus)` : `(('0', '0'), 7, 15, 10, 5)` pour la première fusion de l'exemple.

**`encoder(texte, modele)`** pré-découpe, remplace tout symbole hors de `modele.base` par `INCONNU`, puis applique `fusionner` pour chaque paire de `modele.fusions`, dans l'ordre d'apprentissage. Sur `"le loyer annuel est de 60000 AED ."`, on obtient 16 tokens, de `'l'`, `'e'`, `' loyer'` jusqu'à `' 60000'` et `' .'`.

**`decoder(tokens, modele)`** recolle les tokens avec `"".join` ; au niveau octets, `b"".join(tokens).decode("utf-8")`.

**`visible(token)`** sert seulement à l'affichage : l'espace devient « ▁ », un token d'octets s'affiche par son `repr`.

**`main()`**, bloc par bloc.

1. L'exemple à la main : la liste `attendu` contient les quatre fusions et les valeurs de N du point 8 ; le vocabulaire compte 3 + 4 = 7 tokens.
2. Le corpus, k = 40 : pour chaque fusion, `avant - apres == prevus` ; si a ≠ b, `prevus == f` (point 2). La fusion (0, 0) donne f = 9 et un gain de 6 (point 3).
3. 48 + 40 = 88 tokens, tous distincts (point 5).
4. Aller-retour exact sur la phrase et sur tout le corpus ; les trois premiers tokens `['l', 'e', ' loyer']` montrent l'effet de l'espace (point 4).
5. « Prix : 500 € » au niveau caractères perd 5 symboles ; au niveau octets, k = 60, le vocabulaire fait 256 + 60 tokens, chaque token produit en fait partie et trois textes difficiles reviennent à l'identique (point 6).
6. Le tableau compare N à ⌈L/4⌉ pour quatre textes, puis le coût de 100 000 messages arabes (point 7).
7. Décoder chaque token seul lève `UnicodeDecodeError` pour 38 tokens sur 43 ; `codecs.getincrementaldecoder("utf-8")()` reconstitue la phrase (point 6).

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`pre_decouper(texte)`** — Cette fonction est le boucher qui débite la pièce en morceaux avant que l'atelier de fusion n'y touche : elle reçoit un texte et lui applique l'expression régulière `MOTIF`, qui isole un mot avec l'espace qui le précède, une suite de chiffres, une suite de ponctuations, une suite de soulignés ou une suite d'espaces. Elle vérifie ensuite que les morceaux recollés redonnent exactement le texte et lève `ValueError` dans le cas contraire, puis renvoie la liste des morceaux : `['60000', ' 60000', ' 600']` pour l'exemple fait à la main. Aucune fusion ne pourra plus traverser la frontière entre deux morceaux, ce qui empêche par exemple un chiffre de se coller à une lettre.

**`symboles_de_base(morceau, niveau)`** — Celle-ci réduit chaque morceau en grains élémentaires, comme un meunier qui choisit la finesse de sa mouture : elle reçoit un morceau de texte et un niveau, et renvoie un tuple d'un caractère par symbole au niveau `"caracteres"`, ou un tuple d'objets `bytes` d'un octet chacun, issus de l'encodage UTF-8, au niveau `"octets"`. Tout autre niveau lève `ValueError` avec le message « niveau inconnu ». C'est elle qui décide du vocabulaire de départ de l'entraînement et de l'encodage : `' 600'` devient quatre caractères, alors que `'€'` devient trois octets, `b'\xe2'`, `b'\x82'` et `b'\xac'`.

**`compter_paires(mots)`** — Cette fonction est le recenseur qui fait la tournée de tous les couples de voisins : elle reçoit un dictionnaire qui associe à chaque morceau, écrit comme un tuple de symboles, son nombre d'occurrences n dans le corpus, parcourt chaque tuple avec `zip(mot, mot[1:])` et ajoute n au compteur de chaque paire adjacente, chevauchements compris. Elle renvoie un `Counter` des fréquences f(a, b) sans lever d'exception ; sur l'exemple fait à la main, la paire (0, 0) vaut 7, (6, 0) vaut 3 et (espace, 6) vaut 2, et c'est dans ce compteur qu'`entrainer_bpe` choisit, à chaque tour, la fusion la plus fréquente.

**`nombre_de_tokens(mots)`** — Celle-ci est le comptable qui fait l'inventaire du stock à chaque étape : elle reçoit le même dictionnaire des morceaux et de leurs occurrences, multiplie la longueur de chaque tuple par son nombre d'occurrences et renvoie la somme, N = Σ n × |w| sur tous les morceaux w, c'est-à-dire le nombre total de tokens nécessaires pour écrire tout le corpus avec le découpage courant. Elle ne lève rien. Elle vaut 15 sur l'exemple fait à la main avant toute fusion, 407 sur le corpus trilingue, et `entrainer_bpe` l'appelle avant et après chaque fusion pour noter, dans l'historique, de combien la fusion a raccourci le texte.

**`ModeleBPE.vocabulaire()`** — Cette méthode du modèle entraîné dresse le catalogue complet de ce que le tokenizer sait écrire, comme un imprimeur qui aligne d'abord ses caractères de plomb puis les ligatures qu'il a fait fondre : elle ne reçoit rien d'autre que le modèle, recopie la liste `base` des symboles de départ et y ajoute, dans l'ordre d'apprentissage, la concaténation a + b de chaque paire fusionnée. Elle renvoie cette liste : 3 + 4 = 7 tokens pour l'exemple à la main, 48 + 40 = 88 tokens tous distincts pour le corpus, et 256 + 60 au niveau des octets, comme le vérifient les `assert` de `main`.

**`entrainer_bpe(texte, k, niveau)`** — C'est l'atelier d'apprentissage lui-même, où un artisan répète k fois le même geste : il reçoit un corpus, un nombre de fusions et un niveau, `"caracteres"` par défaut, pré-découpe le texte, compte les morceaux, les écrit en symboles de base et fixe la base, les 256 octets ou bien les caractères vus, triés. À chaque tour, il compte les paires, s'arrête s'il n'en reste aucune, choisit la plus fréquente en départageant les égalités par la plus petite paire, calcule les remplacements prévus, fusionne tous les morceaux et consigne dans l'historique la paire, sa fréquence, N avant, N après et les remplacements prévus. Il renvoie le `ModeleBPE` obtenu ; sur « 60000 60000 600 » avec k = 4, la première ligne d'historique est la paire (0, 0), de fréquence 7, qui fait passer N de 15 à 10.

**`encoder(texte, modele)`** — Cette fonction rejoue sur un texte neuf la recette apprise, comme un cuisinier qui suit les étapes de son carnet dans l'ordre exact où il les a notées : elle reçoit un texte et un modèle, pré-découpe le texte, réduit chaque morceau en symboles de base au niveau du modèle, remplace tout symbole absent de la base par le marqueur `INCONNU`, puis applique une à une toutes les fusions apprises. Elle renvoie la liste des tokens : 16 pour « le loyer annuel est de 60000 AED . » au niveau caractères, qui commencent par `'l'`, `'e'` et `' loyer'`, alors que « Prix : 500 € » y perd 5 symboles inconnus et tient en 13 tokens au niveau des octets, sans aucune perte.

**`decoder(tokens, modele)`** — Celle-ci est le relieur qui recoud les pages dans l'ordre : elle reçoit une liste de tokens et le modèle qui les a produits, et, au niveau caractères, se contente de les concaténer en une chaîne ; au niveau des octets, elle concatène les objets `bytes` puis décode le tout en UTF-8, ce qui peut lever `UnicodeDecodeError` si la suite d'octets est incomplète. Elle renvoie le texte : sur la phrase et sur tout le corpus, l'aller-retour est exact, mais un texte qui contenait des symboles inconnus revient avec des marqueurs `<inconnu>` à la place des caractères perdus.

**`visible(token)`** — Cette petite fonction ne sert qu'à l'affichage, comme un projecteur qui éclaire les coulisses : elle reçoit un token, renvoie sa représentation `repr` s'il s'agit d'un objet `bytes`, par exemple `b'\xd8'`, et sinon remplace chaque espace par le caractère « ▁ » de `ESPACE_VISIBLE`, pour que l'espace collé devant un mot se voie à l'écran. Elle ne change rien aux tokens eux-mêmes et ne lève pas d'exception ; `main` l'utilise pour imprimer les fusions, le vocabulaire et les tokens d'une phrase, comme « ▁loyer » ou « ▁60000 ».

**`main()`** — C'est le maître de conférences qui fait défiler les sept démonstrations du chapitre et vérifie chacune : il entraîne d'abord le petit modèle sur « 60000 60000 600 » et compare ses quatre fusions à la liste attendue, puis entraîne le modèle du corpus avec k = 40 et contrôle que chaque fusion retire exactement les remplacements prévus, la paire (0, 0) donnant f = 9 pour une baisse de 6 seulement. Il vérifie ensuite les 88 tokens du vocabulaire, l'aller-retour exact de l'encodage, la perte du niveau caractères et le repli par octets avec k = 60, compare le compte réel à l'estimation ⌈L/4⌉ et chiffre 100 000 messages arabes à 12,90 USD contre 2,70 USD estimés, et montre enfin que 38 tokens sur 43 ne se décodent pas seuls alors que le décodeur incrémental reconstitue la phrase. La ligne finale n'apparaît que si tous les `assert` sont passés.

```python
"""Étape 02 bis — tokenisation BPE : entraîner, encoder, décoder, repli par octets. Bibliothèque standard seulement."""
import codecs
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass, field

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ESPACE_VISIBLE = chr(0x2581)  # « ▁ » : rend l'espace visible à l'affichage, rien de plus
INCONNU = "<inconnu>"

# Pré-découpage à la manière de GPT-2 : un mot garde l'espace qui le précède ; chiffres et ponctuation
# forment leurs propres morceaux. Aucune fusion ne traverse la frontière entre deux morceaux.
MOTIF = re.compile(r" ?[^\W\d_]+| ?\d+| ?[^\w\s]+| ?_+|\s+")

CORPUS = (
    "le loyer du studio est payé par virement . le loyer annuel est de 60000 AED . "
    "la banque vérifie le dossier du locataire . le contrat de location est signé . "
    "the rent of the studio is paid by transfer . the annual rent is 60000 AED . "
    "the bank checks the file of the tenant . the lease contract is signed . "
    "عقد إيجار شقة في دبي . الإيجار السنوي 60000 درهم . "
    "le loyer est payé . the rent is paid . عقد إيجار . "
)


def pre_decouper(texte: str) -> list[str]:
    morceaux = MOTIF.findall(texte)
    if "".join(morceaux) != texte:
        raise ValueError("le pré-découpage a perdu des caractères")
    return morceaux


def symboles_de_base(morceau: str, niveau: str) -> tuple:
    """« caracteres » : un symbole par caractère. « octets » : un symbole par octet UTF-8."""
    if niveau == "caracteres":
        return tuple(morceau)
    if niveau == "octets":
        return tuple(bytes([b]) for b in morceau.encode("utf-8"))
    raise ValueError("niveau inconnu : " + niveau)


def compter_paires(mots: dict) -> Counter:
    """f(a, b) = Σ_w n_w × (nombre de positions i où w_i = a et w_(i+1) = b), chevauchements compris."""
    paires = Counter()
    for mot, n in mots.items():
        for a, b in zip(mot, mot[1:]):
            paires[(a, b)] += n
    return paires


def fusionner(mot: tuple, paire: tuple) -> tuple[tuple, int]:
    """Remplace, de gauche à droite et sans chevauchement, chaque (a, b) adjacent par a + b."""
    a, b = paire
    sortie, i, remplaces = [], 0, 0
    while i < len(mot):
        if i + 1 < len(mot) and mot[i] == a and mot[i + 1] == b:
            sortie.append(a + b)
            i += 2
            remplaces += 1
        else:
            sortie.append(mot[i])
            i += 1
    return tuple(sortie), remplaces


def remplacements_prevus(mot: tuple, paire: tuple) -> int:
    """m_w(a, b) calculé sans fusionner : les occurrences si a ≠ b, Σ ⌊L/2⌋ sur les séries de a si a = b."""
    a, b = paire
    if a != b:
        return sum(1 for x, y in zip(mot, mot[1:]) if (x, y) == paire)
    total, serie = 0, 0
    for s in mot + (None,):
        if s == a:
            serie += 1
        else:
            total += serie // 2
            serie = 0
    return total


def nombre_de_tokens(mots: dict) -> int:
    """N = Σ_w n_w × |w|."""
    return sum(n * len(mot) for mot, n in mots.items())


@dataclass
class ModeleBPE:
    niveau: str
    base: list
    fusions: list = field(default_factory=list)      # paires, dans l'ordre d'apprentissage (le rang)
    historique: list = field(default_factory=list)   # (paire, f, N avant, N après, remplacements prévus)

    def vocabulaire(self) -> list:
        return list(self.base) + [a + b for a, b in self.fusions]


def entrainer_bpe(texte: str, k: int, niveau: str = "caracteres") -> ModeleBPE:
    """k fois : compter les paires adjacentes, fusionner la plus fréquente (égalité : la plus petite paire)."""
    mots: dict = {}
    for morceau, n in Counter(pre_decouper(texte)).items():
        mots[symboles_de_base(morceau, niveau)] = n
    base = [bytes([b]) for b in range(256)] if niveau == "octets" else sorted({s for mot in mots for s in mot})
    modele = ModeleBPE(niveau, base)
    for _ in range(k):
        paires = compter_paires(mots)
        if not paires:                       # chaque morceau tient déjà en un seul token
            break
        meilleure = min(paires, key=lambda p: (-paires[p], p))
        avant = nombre_de_tokens(mots)
        prevus = sum(n * remplacements_prevus(mot, meilleure) for mot, n in mots.items())
        nouveaux: dict = {}
        for mot, n in mots.items():
            fusionne, _ = fusionner(mot, meilleure)
            nouveaux[fusionne] = nouveaux.get(fusionne, 0) + n
        mots = nouveaux
        modele.fusions.append(meilleure)
        modele.historique.append((meilleure, paires[meilleure], avant, nombre_de_tokens(mots), prevus))
    return modele


def encoder(texte: str, modele: ModeleBPE) -> list:
    """Pré-découper, passer en symboles de base, puis appliquer les fusions dans leur ordre d'apprentissage."""
    connus = set(modele.base)
    tokens = []
    for morceau in pre_decouper(texte):
        mot = tuple(s if s in connus else INCONNU for s in symboles_de_base(morceau, modele.niveau))
        for paire in modele.fusions:
            mot, _ = fusionner(mot, paire)
        tokens.extend(mot)
    return tokens


def decoder(tokens: list, modele: ModeleBPE) -> str:
    """Concaténation ; au niveau des octets, on décode ensuite l'UTF-8."""
    if modele.niveau == "octets":
        return b"".join(tokens).decode("utf-8")
    return "".join(tokens)


def visible(token) -> str:
    if isinstance(token, bytes):
        return repr(token)
    return token.replace(" ", ESPACE_VISIBLE)


def main() -> None:
    print("=== 1. Exemple fait à la main : « 60000 60000 600 », k = 4 ===")
    petit = entrainer_bpe("60000 60000 600", k=4)
    for i, (paire, f, avant, apres, prevus) in enumerate(petit.historique, start=1):
        print(f"  fusion {i} : {visible(paire[0])} + {visible(paire[1])}   f = {f}   N : {avant} -> {apres}")
    attendu = [(("0", "0"), 7, 15, 10), (("6", "00"), 3, 10, 7), ((" ", "600"), 2, 7, 5), ((" 600", "00"), 1, 5, 4)]
    assert [h[:4] for h in petit.historique] == attendu
    print(f"  vocabulaire = {[visible(t) for t in petit.vocabulaire()]}")
    assert len(petit.vocabulaire()) == 3 + 4

    print("=== 2. Corpus FR / EN / AR, k = 40 : chaque fusion retire m tokens ===")
    modele = entrainer_bpe(CORPUS, k=40)
    for i, (paire, f, avant, apres, prevus) in enumerate(modele.historique[:5], start=1):
        print(f"  fusion {i} : {visible(paire[0])} + {visible(paire[1])}   f = {f:2d}   N : {avant} -> {apres}")
    for paire, f, avant, apres, prevus in modele.historique:
        assert avant - apres == prevus                    # la réduction vaut le nombre de remplacements
        if paire[0] != paire[1]:
            assert prevus == f                            # a ≠ b : les occurrences ne se chevauchent pas
    zeros = next(h for h in modele.historique if h[0] == ("0", "0"))
    print(f"  paire (0, 0) : f = {zeros[1]} mais N ne baisse que de {zeros[2] - zeros[3]} (3 × ⌊4/2⌋)")
    assert (zeros[1], zeros[2] - zeros[3]) == (9, 6)

    print("=== 3. Taille du vocabulaire = base + fusions ===")
    vocab = modele.vocabulaire()
    print(f"  {len(modele.base)} caractères de base + {len(modele.fusions)} fusions = {len(vocab)} tokens")
    assert len(vocab) == len(modele.base) + len(modele.fusions) == 88 and len(set(vocab)) == len(vocab)

    print("=== 4. Encoder puis décoder rend le texte exact ===")
    phrase = "le loyer annuel est de 60000 AED ."
    tokens = encoder(phrase, modele)
    print(f"  {len(phrase)} caractères -> {len(tokens)} tokens : {[visible(t) for t in tokens]}")
    assert decoder(tokens, modele) == phrase and decoder(encoder(CORPUS, modele), modele) == CORPUS
    assert tokens[:3] == ["l", "e", " loyer"]             # en tête de texte, « le » n'a pas d'espace devant

    print("=== 5. Caractère inconnu : le niveau caractères perd, le niveau octets non ===")
    prix = "Prix : 500 €"
    perdus = encoder(prix, modele)
    print(f"  caractères : {perdus.count(INCONNU)} tokens {INCONNU} ; texte rendu = {decoder(perdus, modele)!r}")
    assert INCONNU in perdus and decoder(perdus, modele) != prix
    octets = entrainer_bpe(CORPUS, k=60, niveau="octets")
    assert len(octets.vocabulaire()) == 256 + 60
    connus = set(octets.vocabulaire())
    for texte in (prix, "迪拜 " + chr(0x1F642), "AED ٦٠٠٠٠"):
        toks = encoder(texte, octets)
        assert all(t in connus for t in toks) and decoder(toks, octets) == texte
    print(f"  octets : {len(encoder(prix, octets))} tokens, texte rendu à l'identique ; € = {len('€'.encode('utf-8'))} octets")

    print("=== 6. L'estimation ⌈L/4⌉ contre le compte réel (niveau octets, k = 60) ===")
    print("  texte     L  octets  N  ⌈L/4⌉  N / ⌈L/4⌉")
    textes = {
        "FR": "Le loyer annuel du studio est de 60000 AED.",
        "EN": "The annual rent of the studio is 60000 AED.",
        "AR": "الإيجار السنوي للاستوديو 60000 درهم",
        "IBAN": "AE070331234567890123456",
    }
    rapports = {}
    for nom, texte in textes.items():
        n = len(encoder(texte, octets))
        estime = math.ceil(len(texte) / 4)
        rapports[nom] = n / estime
        print(f"  {nom:5s} {len(texte):4d} {len(texte.encode('utf-8')):6d} {n:3d} {estime:5d} {n / estime:9.2f}")
    assert [len(encoder(t, octets)) for t in textes.values()] == [16, 17, 43, 23]
    assert rapports["AR"] > 4 > rapports["FR"] > 1
    prix_in = 3.00 / 1_000_000                            # USD par token d'entrée, illustratif (étape 72)
    reel, estime = 100_000 * 43 * prix_in, 100_000 * 9 * prix_in
    print(f"  100 000 messages arabes : {reel:.2f} USD au compte réel, {estime:.2f} USD estimés par ⌈L/4⌉")
    assert (round(reel, 2), round(estime, 2)) == (12.9, 2.7)

    print("=== 7. Flux de tokens : décoder token par token casse l'UTF-8 ===")
    toks = encoder(textes["AR"], octets)
    casses = []
    for t in toks:
        try:
            t.decode("utf-8")
        except UnicodeDecodeError:
            casses.append(t)
    decodeur = codecs.getincrementaldecoder("utf-8")()
    morceaux = [decodeur.decode(t) for t in toks] + [decodeur.decode(b"", final=True)]
    print(f"  {len(casses)} tokens sur {len(toks)} ne sont pas de l'UTF-8 complet, par exemple {casses[0]!r}")
    print(f"  décodeur incrémental : texte reconstitué identique = {''.join(morceaux) == textes['AR']}")
    assert casses and "".join(morceaux) == textes["AR"]

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
=== 1. Exemple fait à la main : « 60000 60000 600 », k = 4 ===
  fusion 1 : 0 + 0   f = 7   N : 15 -> 10
  fusion 2 : 6 + 00   f = 3   N : 10 -> 7
…
  fusion 4 : 0 + 0   f =  9   N : 373 -> 367
  fusion 5 : h + e   f =  9   N : 367 -> 358
  paire (0, 0) : f = 9 mais N ne baisse que de 6 (3 × ⌊4/2⌋)
…
  48 caractères de base + 40 fusions = 88 tokens
…
  caractères : 5 tokens <inconnu> ; texte rendu = '<inconnu>ri<inconnu> <inconnu> <inconnu>00 <inconnu>'
  octets : 13 tokens, texte rendu à l'identique ; € = 3 octets
…
  AR      35     61  43     9      4.78
  100 000 messages arabes : 12.90 USD au compte réel, 2.70 USD estimés par ⌈L/4⌉
…
  38 tokens sur 43 ne sont pas de l'UTF-8 complet, par exemple b'\xd8'
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un tokenizer n'a rien de mystérieux. C'est une liste ordonnée de fusions apprises en comptant des paires, qu'on rejoue pour encoder et qu'on défait en recollant. Sa seule faiblesse de principe, le symbole inconnu, disparaît avec les octets, au prix de tokens plus nombreux pour les langues et les symboles qu'il a peu vus.

### Le comptage chez un fournisseur (extrait)

Le tokenizer d'un modèle d'API n'est pas toujours publié, et il change d'un modèle à l'autre. Le compte exact se demande alors au fournisseur. L'adaptateur ci-dessous branche le point de terminaison de comptage de l'API Claude sur le port `compter_tokens(texte)` ; l'agent ne dépend que du port. Le compte renvoyé porte sur un message entier : il peut inclure quelques tokens de mise en forme en plus du texte.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`CompteurClaude.__init__(model)`** — Le constructeur de l'adaptateur installe le guichet par lequel on posera la question au fournisseur, comme un clerc qui ouvre un compte auprès d'une étude avant d'y envoyer ses dossiers : il reçoit le nom du modèle, `"claude-opus-5-5"` par défaut, crée un client `anthropic.Anthropic()`, qui lit la clé `ANTHROPIC_API_KEY` ou le profil créé par `ant auth login`, et garde le nom du modèle, parce que le compte de tokens dépend du modèle utilisé à l'inférence. Il ne renvoie rien ; sans clé ni profil valides, c'est la bibliothèque `anthropic` qui signale l'erreur.

**`CompteurClaude.compter_tokens(texte)`** — Cette méthode est l'implémentation du port `compter_tokens` : elle reçoit un texte, l'emballe dans un unique message de rôle `user` et le soumet au point de terminaison `messages.count_tokens` de l'API pour le modèle retenu, comme un expéditeur qui fait peser son colis au guichet avant de l'envoyer. Elle renvoie l'entier `input_tokens` de la réponse, c'est-à-dire le compte du message entier, qui peut inclure quelques tokens de mise en forme en plus du texte ; cet extrait n'est pas exécuté par le harnais, et une erreur réseau ou d'authentification remonterait telle quelle depuis le client.

```python
# [extrait] — adaptateur de comptage pour l'API Claude, non exécuté par le harnais (pip install anthropic)
import anthropic


class CompteurClaude:
    """Port compter_tokens(texte) -> int ; d'autres adaptateurs : tokenizer local, estimation calibrée par langue."""

    def __init__(self, model: str = "claude-opus-5-5"):
        self.client = anthropic.Anthropic()   # lit ANTHROPIC_API_KEY ou le profil créé par `ant auth login`
        self.model = model                    # le compte dépend du modèle : on passe celui de l'inférence

    def compter_tokens(self, texte: str) -> int:
        reponse = self.client.messages.count_tokens(
            model=self.model,
            messages=[{"role": "user", "content": texte}],
        )
        return reponse.input_tokens
```

On n'utilise pas, pour un modèle Claude, le tokenizer public d'un autre fournisseur : il donne un autre découpage, donc un autre compte, surtout sur le code et sur les langues autres que l'anglais.

## Squelette algorithmique

L'entraînement prend un texte et un nombre de fusions k, et rend la base et la liste ordonnée des fusions. L'encodage rejoue ces fusions sur chaque morceau ; le décodage recolle.

```text
ALGORITHME EntraînerBPE
ENTRÉES : texte d'entraînement, nombre de fusions k, niveau ∈ {caractères, octets}
SORTIE  : base B, liste ordonnée des fusions

  morceaux ← PréDécouper(texte)                     (l'espace reste collé au mot qui suit)
  POUR CHAQUE morceau distinct w FAIRE
      n(w) ← nombre d'occurrences de w
      w ← suite de ses symboles de base (caractères, ou octets UTF-8)
  FIN POUR
  SI niveau = octets ALORS B ← les 256 octets SINON B ← caractères vus, triés FIN SI
  fusions ← liste vide
  POUR t DE 1 À k FAIRE
      f ← pour chaque paire adjacente (a, b) : Σ n(w) × occurrences de (a, b) dans w
      SI f est vide ALORS SORTIR DE LA BOUCLE FIN SI       (chaque morceau tient en un token)
      (a*, b*) ← paire de f maximale ; à égalité, la plus petite
      POUR CHAQUE w FAIRE
          remplacer de gauche à droite, sans chevauchement, chaque (a*, b*) par a* + b*
      FIN POUR
      ajouter (a*, b*) à fusions
  FIN POUR
  RETOURNER B, fusions

ALGORITHME Encoder(texte)
  tokens ← liste vide
  POUR CHAQUE morceau de PréDécouper(texte) FAIRE
      w ← symboles de base du morceau ; un symbole hors de B devient <inconnu>
      POUR CHAQUE (a, b) DE fusions, dans l'ordre FAIRE  w ← Fusionner(w, (a, b))  FIN POUR
      ajouter les tokens de w à tokens
  FIN POUR
  RETOURNER tokens

ALGORITHME Décoder(tokens)
  s ← concaténation des tokens
  SI niveau = octets ALORS RETOURNER DécoderUTF8(s) SINON RETOURNER s FIN SI
```

**Complexité :** notons S la somme des longueurs des morceaux distincts. Chaque tour d'entraînement recompte les paires en O(S) et réécrit les morceaux en O(S), d'où O(k × S) en temps et O(S) en mémoire pour les morceaux et leurs paires. Les implémentations de production ne mettent à jour que les morceaux qui contiennent la paire fusionnée, avec une file de priorité sur les fréquences, ce qui rend chaque fusion proportionnelle au nombre d'occurrences touchées. L'encodage naïf coûte O(k × |w|) par morceau. La variante par rangs, qui fusionne à chaque pas la paire présente de plus petit rang, donne le même résultat : une paire créée par la fusion de rang r contient le nouveau token, donc a un rang supérieur à r, si bien que les rangs sont traités dans l'ordre croissant. Elle coûte O(|w|²) par morceau en version simple, O(|w| log |w|) avec un tas, et l'on met en cache l'encodage des morceaux fréquents. Le décodage est en O(N). Le modèle lui-même tient en O(|B| + k).

**Du squelette au code :** `PréDécouper` est `pre_decouper` ; les symboles de base viennent de `symboles_de_base` ; le comptage f est `compter_paires` ; le choix de (a*, b*) est la ligne `meilleure = min(...)` de `entrainer_bpe` ; le remplacement sans chevauchement est `fusionner`, dont le gain est prévu par `remplacements_prevus` ; `Encoder` et `Décoder` sont `encoder` et `decoder`. La ligne « un symbole hors de B devient <inconnu> » est la compréhension avec `INCONNU` dans `encoder`, qui ne sert jamais au niveau octets.

## Cas d'usage réels aux Émirats

Les rapports entre compte réel et estimation cités ci-dessous viennent du tokenizer jouet du programme : ils sont illustratifs. En production, on les mesure sur le trafic réel, avec le tokenizer du modèle déployé.

### Banque — le budget d'un assistant bilingue

Une banque de détail de Dubaï déploie un assistant qui répond aux clients en arabe et en anglais sur les cartes, les prêts personnels et les financements Murabaha. L'équipe a d'abord chiffré le budget mensuel avec l'estimation ⌈L/4⌉ de l'étape 4, appliquée à toutes les conversations. Le calcul de ce fichier montre le défaut : le rapport entre compte réel et estimation vaut 4/ρ, et il change avec la langue ; sur le tokenizer jouet, il vaut 1,45 pour une phrase française et 4,78 pour une phrase arabe, si bien que 100 000 messages arabes coûtent 12,90 USD au lieu des 2,70 USD prévus (prix illustratif). La banque remplace donc l'estimation unique par un ρ mesuré par langue : chaque semaine, un échantillon de messages anonymisés passe par le compteur exact (le point de terminaison de comptage du fournisseur, ou le tokenizer du modèle hébergé en interne), et le ρ de chaque langue alimente le garde-fou de budget et le réglage de `max_tokens`. Sans ce calibrage, le budget dérive en silence, et les réponses arabes atteignent plus souvent la limite de sortie, ce qui renvoie un `stop_reason` « max_tokens » et une réponse coupée au client. L'échantillon envoyé au comptage externe ne contient aucune donnée client identifiable, conformément à la politique de la banque sur les données transmises à des tiers. Les indicateurs suivis sont l'écart relatif entre tokens estimés et tokens facturés, par langue, et le taux de réponses tronquées.

### Secteur public — une fenêtre de contexte qui se remplit plus vite en arabe

Une entité de services publics en ligne, accessible par UAE Pass, accompagne les usagers dans des démarches de plusieurs dizaines d'échanges, en arabe ou en anglais. Le service résume l'historique quand la conversation dépasse un seuil (étape 13 ter). La première version exprimait ce seuil en nombre de messages, ce qui supposait qu'un message coûte le même nombre de tokens dans les deux langues. Le point 7 de la démonstration montre que c'est faux : à texte de même longueur, une conversation arabe peut compter plusieurs fois plus de tokens, si le tokenizer du modèle couvre mal l'arabe. L'équipe exprime donc le seuil en tokens, mesurés à chaque tour par le port `compter_tokens`, et non en messages ni en caractères. Sans cette correction, les sessions arabes atteignent la limite du contexte avant d'avoir été résumées, et les plus longues échouent au moment précis où l'usager termine sa démarche. Résumer tôt sert aussi la minimisation des données personnelles qu'exige la PDPL, puisque les pièces citées en début de démarche ne sont plus renvoyées au modèle. Les indicateurs suivis sont le nombre de tokens par session, par langue, et le taux de sessions interrompues par la limite de contexte.

### Immobilier — des montants et des références que le modèle ne doit pas recopier

Une agence et un promoteur actifs à Dubaï et Abu Dhabi font rédiger par un agent des fiches de biens : prix en AED, surface en sqft, référence de contrat Ejari, frais de transfert DLD de 4 %. Les chiffres se découpent mal : dans le programme, « ▁60000 », vu trois fois à l'entraînement, forme un seul token, mais un identifiant de 23 caractères en coûte 23, et chaque token de chiffres est une occasion pour le modèle d'en tirer un autre (étape 2). L'agent ne recopie donc jamais un montant ni une référence : il écrit un repère comme `{prix_aed}` ou `{ref_ejari}`, et le code le remplace par la valeur de la base du projet avant publication. Sans cette séparation, une fiche sur plusieurs centaines peut afficher 2 200 000 AED au lieu de 2 020 000 AED, ou une référence Ejari fausse, ce qui expose l'agence à une réclamation de l'acheteur. Les annonces doivent par ailleurs reprendre exactement les données du projet enregistré, à confirmer avec les règles en vigueur du régulateur. L'indicateur suivi est le nombre de fiches dont un chiffre diffère de la base, avec un objectif de zéro.

### RH — des noms translittérés et des Emirates ID au caractère près

Un cabinet RH présent dans plusieurs émirats rapproche les dossiers des salariés entre ses fichiers de paie WPS, les contrats enregistrés auprès du MOHRE et les copies d'Emirates ID. Le même nom s'écrit « Mohammed », « Muhammad » ou « Mohamed » en lettres latines, et de plusieurs façons en arabe selon les diacritiques et la forme de l'alef. Pour le modèle, ces variantes sont des suites de tokens différentes, découpées à des endroits différents : lui demander « est-ce la même personne ? » donne une réponse plausible, pas un rapprochement fiable. L'agent appelle donc des outils déterministes : une normalisation de l'arabe (alef, ta marbuta, diacritiques) et des variantes latines connues, puis une comparaison exacte, et la fonction canonique `emirates_id_format_valide` pour le format à 15 chiffres commençant par 784, au lieu de « relire » le numéro, que la tokenisation découpe en morceaux arbitraires. Sans ces outils, un doublon passe inaperçu et un salaire peut être versé deux fois, ou deux homonymes sont fusionnés. Les indicateurs suivis sont le nombre de doublons détectés avant envoi du fichier WPS et le taux de rapprochements corrigés par un gestionnaire.

### Crypto — des adresses de portefeuille hors de portée du modèle

Une plateforme d'actifs virtuels agréée par la VARA fait rédiger par un agent les alertes de surveillance de liquidité et les réponses aux questions des clients sur leurs retraits. Une adresse de portefeuille ou une empreinte de transaction est une longue suite de caractères hexadécimaux sans régularité : comme l'IBAN du programme, elle coûte à peu près un token par caractère avec un tokenizer qui ne l'a jamais vue, soit plusieurs fois l'estimation ⌈L/4⌉, et chaque token est une occasion d'erreur de recopie. Une adresse fausse d'un seul caractère envoie des fonds vers un portefeuille que personne ne contrôle. La règle de la plateforme est donc qu'aucune adresse ne transite par le texte généré : l'agent manipule un identifiant interne (« portefeuille n° 18 du client »), et l'outil d'exécution résout l'adresse et vérifie sa somme de contrôle dans le code. Cette règle réduit aussi les tokens de chaque alerte. Les indicateurs suivis sont le nombre d'adresses apparues dans une sortie du modèle, avec un objectif de zéro, et le coût moyen en tokens par alerte.

### BTP — des symboles et des réponses affichées en flux

Un groupe de construction qui mène de grands chantiers à Dubaï fait produire par un agent des comptes rendus et des devis bilingues, avec des symboles comme « Ø12 » pour un diamètre d'acier, « m² » et des montants HT et TTC avec une TVA de 5 %. Le tokenizer à octets garantit qu'aucun de ces symboles ne devient un token inconnu (point 6) : rien ne se perd, mais chaque symbole rare coûte deux ou trois tokens. Le vrai incident est venu de l'affichage : l'application de chantier affichait la réponse en flux et décodait chaque token séparément, si bien que des caractères arabes et des symboles apparaissaient brisés à l'écran. Le programme en donne la mesure : sur la phrase arabe, 38 tokens sur 43 ne sont pas, seuls, de l'UTF-8 valide. Le client utilise désormais un décodeur incrémental, qui garde en attente les octets d'un caractère commencé (étape 33 bis), et les montants restent insérés par le code, jamais générés. L'indicateur suivi est le nombre de caractères mal affichés signalés par les équipes de chantier, avec un objectif de zéro.

## Pièges et limites

- **Budgéter en caractères ou en mots.** Tout se compte en tokens : coût, contexte, `max_tokens`, limites de débit. ⌈L/4⌉ ne donne qu'un ordre de grandeur, et seulement pour un texte proche de ce que le tokenizer a vu.
- **Changer de modèle sans recompter.** Le découpage dépend du modèle, y compris chez un même fournisseur quand il change de tokenizer d'une génération à l'autre ; on recompte un échantillon à chaque changement de modèle.
- **Décoder token par token un flux d'octets.** Un token peut s'arrêter ou commencer au milieu d'un caractère ; on décode de façon incrémentale.
- **Confier au modèle une tâche au caractère près.** Compter des lettres, recopier un IBAN, comparer deux translittérations : le modèle voit des tokens, pas des caractères. On passe par un outil.
- **Prendre la fréquence pour le gain.** Pour une paire de deux symboles identiques, f compte des paires qui se chevauchent ; le gain réel vaut Σ ⌊ℓ/2⌋ (point 3).

### Exercice feuille blanche

1. Sans regarder le code, écrire `compter_paires`, `fusionner` et `entrainer_bpe`, puis retrouver les quatre fusions de « 60000 60000 600 » et la suite N = 15, 10, 7, 5, 4.
2. Prédire, puis vérifier : sur « 6000 6000 », quelle est la première fusion, sa fréquence et le nouveau N ? (Réponse : (0, 0), f = 4, mais chaque série de trois zéros ne permet qu'un remplacement, donc N passe de 9 à 7.)
3. Trouver le bug : dans une variante de `fusionner`, la ligne `i += 2` est remplacée par `i += 1`. Que devient `('0', '0', '0')` avec la paire `('0', '0')`, et quelle propriété de la démonstration est violée ? (Réponse : `('00', '00', '0')`, qui se recolle en « 00000 » : la concaténation n'est plus conservée (point 4), le décodage invente deux zéros.)

## Pour aller plus loin

Le BPE vient de la compression de données (Gage, 1994) ; Sennrich et al. (2016) l'ont appliqué à la traduction automatique, et GPT-2 (Radford et al., 2019) l'a fait travailler sur les octets. WordPiece (BERT) choisit les fusions par un critère de vraisemblance plutôt que par la fréquence ; l'algorithme Unigram de SentencePiece (Kudo, 2018) part d'un grand vocabulaire et l'élague. Le BPE-dropout (Provilkov et al., 2020) saute des fusions au hasard pendant l'entraînement du modèle pour le rendre robuste aux découpages. Plusieurs tokenizers découpent les nombres chiffre par chiffre, ou par groupes de trois, pour faciliter l'arithmétique. Les modèles arabes comme Jais utilisent, selon leurs auteurs, un vocabulaire construit à la fois sur l'arabe et sur l'anglais, ce qui rapproche le coût des deux langues.

> Étape 02 bis du parcours · Prérequis : [Softmax et température](<02-Softmax-Temperature-Prochain-Token.md>) · Suite : [Fondements : softmax et Bellman](<03-Fondements-Softmax-et-LLM.md>)
