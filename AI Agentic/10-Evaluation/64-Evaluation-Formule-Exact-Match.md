# Étape 64 — Évaluation — Exact Match

> Étape 64 du parcours · Prérequis : [Answer Correctness](<63-Evaluation-Formule-Answer-Correctness.md>) · Suite : [Théorèmes de fidélité, pertinence et F1](<64b-Theoremes-Fidelite-Pertinence-et-F1.md>)

**Dossier :** 10-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Product Engineers  
**Nom du fichier :** 64-Evaluation-Formule-Exact-Match.md

## Définition

L'Exact Match (EM) est la métrique la plus stricte de l'évaluation : pour chaque exemple, elle vaut 1 si la réponse de l'agent est identique à la réponse attendue **après normalisation**, et 0 sinon. Le score d'un jeu d'évaluation est la part des exemples qui valent 1. La normalisation fait partie de la définition de la métrique : deux équipes qui normalisent différemment ne mesurent pas la même chose, et doivent publier leur normalisation avec le chiffre. Pour une sortie structurée (un montant, un IBAN, une date, une adresse de portefeuille), la normalisation se choisit **champ par champ** : on ne traite pas un montant comme une adresse crypto. L'EM est sévère par construction : une réponse juste mais formulée autrement échoue, c'est pourquoi on la complète par la F1 des mots ou par Answer Correctness (étape 63). Un jeu vide n'a pas d'EM (`None`), et des listes de longueurs différentes sont une erreur, pas un cas à tronquer.

## Rôle dans un agent

L'EM est le correcteur « code » de l'étape 13 bis dans sa forme la plus simple : déterministe, gratuit, exact. Il intervient en fin de boucle, quand l'agent produit une sortie qu'on peut comparer à une valeur attendue : les champs d'un objet JSON validé par un schéma (étape 8), un code de produit, une référence de dossier, un montant. Hors ligne, il sert de barrière sur les tâches d'extraction : chaque champ a son taux d'EM et son seuil. En production, on compare la valeur extraite par l'agent à celle qu'un humain a finalement validée, ce qui donne un EM en ligne sans juge. La même normalisation par champ sert à comparer les arguments d'un appel d'outil dans Tool Call F1 (étape 59) : deux appels identiques à un espace insécable près ne doivent pas compter comme différents.

## Équation complète

EM d'un exemple, ν étant la fonction de normalisation déclarée :

$$
\text{EM}_i = \mathbf{1}\big[\, \nu(\hat y_i) = \nu(y_i) \,\big]
$$

EM d'un jeu de N exemples (N ≥ 1, autant de prédictions que de références) :

$$
\text{EM} = \frac{1}{N} \sum_{i=1}^{N} \text{EM}_i
$$

Plusieurs réponses acceptables Yᵢ pour un même exemple :

$$
\text{EM}_i = \max_{y \in Y_i} \mathbf{1}\big[\, \nu(\hat y_i) = \nu(y) \,\big]
$$

Sortie structurée : un score par champ c, chacun avec sa normalisation :

$$
\text{EM}_c = \frac{1}{N} \sum_{i=1}^{N} \mathbf{1}\big[\, \nu_c(\hat y_{i,c}) = \nu_c(y_{i,c}) \,\big]
$$

F1 des mots, pour comparaison (multi-ensembles de mots après normalisation) :

$$
F_1^{\text{mots}} = \frac{2PR}{P + R}, \qquad P = \frac{|\hat T \cap T|}{|\hat T|}, \qquad R = \frac{|\hat T \cap T|}{|T|}
$$

## Décryptage des symboles

$$
N
$$

**Sens :** nombre d'exemples du jeu d'évaluation · **Type / plage :** entier ≥ 0 ; l'EM n'est définie que pour N ≥ 1 · **Variable Python :** `len(references)`

$$
\hat y_i,\; y_i
$$

**Sens :** réponse produite par l'agent pour l'exemple i, et réponse attendue · **Type / plage :** chaînes de caractères · **Variable Python :** `predictions[i]`, `references[i]`

$$
\nu
$$

**Sens :** fonction de normalisation déclarée, appliquée des deux côtés avant la comparaison · **Type / plage :** fonction de chaîne vers chaîne (ou vers nombre pour un montant) · **Variable Python :** paramètre `normaliser` : `normaliser_texte`, `normaliser_squad`, `normaliser_arabe`…

$$
\mathbf{1}[\cdot]
$$

**Sens :** indicatrice : 1 si la condition est vraie, 0 sinon · **Type / plage :** 0 ou 1 · **Variable Python :** `int(a == b)`, ou le booléen additionné directement

$$
\text{EM}_i,\; \text{EM}
$$

**Sens :** succès d'un exemple, et part des succès sur le jeu · **Type / plage :** 0 ou 1 ; réel dans [0, 1], ou indéfini si N = 0 · **Variable Python :** `exact_match(predictions, references, normaliser)`

$$
Y_i
$$

**Sens :** ensemble des réponses acceptables pour l'exemple i (sigle et nom complet, arabe et anglais) · **Type / plage :** liste non vide de chaînes · **Variable Python :** `references` dans `em_multi(prediction, references)`

$$
c,\; \nu_c
$$

**Sens :** un champ d'une sortie structurée, et sa normalisation propre · **Type / plage :** nom de champ ; fonction · **Variable Python :** clés de `normaliseurs`, par exemple `normaliseurs["iban"] = normaliser_iban`

$$
\hat T,\; T
$$

**Sens :** multi-ensembles des mots de la réponse et de la référence, après normalisation · **Type / plage :** compteurs de mots · **Variable Python :** `Counter(p)`, `Counter(r)` dans `f1_tokens`

## Démonstration

### 1. L'EM est une proportion : elle a un intervalle de confiance

Chaque EMᵢ vaut 0 ou 1, donc leur moyenne est dans [0, 1] et c'est une proportion de succès sur N essais. On lui applique l'intervalle de Wilson de l'étape 7. Avec 46 réponses exactes sur 50, l'EM vaut 0,92, mais l'intervalle à 95 % va de 0,8116 à 0,9685 : 50 exemples ne permettent pas d'affirmer que le vrai taux dépasse 0,90. Une barrière de déploiement compare la **borne basse** au seuil, pas l'estimation (étape 13 bis).

### 2. Une normalisation plus grossière donne toujours un EM plus haut

Supposons que la normalisation ν₂ s'obtienne en appliquant une transformation g après ν₁, c'est-à-dire ν₂ = g ∘ ν₁. Si ν₁(a) = ν₁(b), on applique g des deux côtés et l'on obtient ν₂(a) = ν₂(b). Tout exemple réussi avec ν₁ est donc réussi avec ν₂ :

$$
\nu_2 = g \circ \nu_1 \quad\Longrightarrow\quad \text{EM}_i^{(\nu_1)} \le \text{EM}_i^{(\nu_2)} \quad\Longrightarrow\quad \text{EM}^{(\nu_1)} \le \text{EM}^{(\nu_2)}
$$

Dans le code, `normaliser_squad` commence par appeler `normaliser_texte`, et l'identité est la normalisation la plus fine : sur cinq couples, on obtient 0,0 sans normalisation, 0,4 avec `normaliser_texte` et 0,6 avec `normaliser_squad`. Ce gain n'est pas un gain de qualité de l'agent : c'est la mesure qui devient plus indulgente. À l'extrême, une normalisation qui renvoie toujours la même chaîne donne un EM de 1 à n'importe quel agent. Le risque concret est le **faux positif** : passer en minuscules une adresse en Base58, alphabet sensible à la casse, fusionne « 4kR9vTqW2mZp8sLx » et « 4kr9vTqW2mZp8sLx », qui sont deux portefeuilles différents.

### 3. L'EM est toujours inférieure ou égale à la F1 des mots

Prenons la même normalisation pour les deux métriques. Si EMᵢ = 1, les deux chaînes normalisées sont identiques, donc leurs multi-ensembles de mots aussi : P = R = 1 et F1 = 1. Si EMᵢ = 0, la F1 est au moins 0. Dans les deux cas EMᵢ ≤ F1ᵢ, et l'inégalité passe à la moyenne. La F1 des mots est plus indulgente, et ce n'est pas toujours une qualité : « Retenue de 10 % » contre « retenue de 5 % » donne EM = 0 mais F1 = 2/3, parce que deux mots sur trois coïncident. Pour un montant ou un taux, le seul mot qui compte est celui qui diffère : c'est l'EM qui dit la vérité métier.

### 4. Le bug des longueurs : `zip` tronque en silence

La fonction `zip` de Python s'arrête à la plus courte des deux listes. L'ancienne version divisait ensuite par le nombre de prédictions. Avec 3 prédictions pour 5 références, toutes justes sur les 3 premières, elle renvoyait 3/3 = 1,0, comme si les deux exemples sans réponse n'existaient pas. Si l'agent n'a rien répondu à deux exemples, ce sont deux échecs : on complète par des réponses vides et l'on obtient 3/5 = 0,6. La nouvelle version vérifie les longueurs et lève `ValueError` avec un message clair ; en plus, `zip(…, strict=True)`, disponible depuis Python 3.10, lèverait lui-même une erreur si la vérification était retirée.

### 5. Les espaces insécables

Les caractères U+00A0 (espace insécable) et U+202F (espace fine insécable, séparateur de milliers de la typographie française) ne sont pas l'espace ordinaire U+0020. Un montant saisi « 1 500 AED » dans un traitement de texte français contient souvent U+202F. La méthode `strip()` ne retire que les espaces aux deux bouts, et `lower()` ne touche pas aux espaces : l'ancienne version donnait donc 0 pour trois écritures du même montant. La normalisation NFKC remplace U+00A0 et U+202F par U+0020, parce que ces caractères ont une décomposition de compatibilité vers l'espace ordinaire. Ensuite, `" ".join(s.split())` fusionne toute suite d'espaces en un seul, puisque `split()` sans argument coupe sur tous les blancs Unicode. Les trois écritures deviennent identiques.

### 6. L'arabe : ce que NFKC ne fait pas

En écriture courante, les voyelles brèves (le *tashkil*, de U+064B à U+0652) sont facultatives, l'alef portant une hamza (أ, إ, آ) est souvent écrit comme un alef nu (ا), et le ta marbuta final (ة) se confond avec le ha (ه), comme l'alef maqsura (ى) avec le ya (ي). NFKC ne rapproche pas ces formes, parce que ce sont des lettres distinctes et non des variantes de compatibilité : sans normalisation arabe, les trois paires du programme donnent un EM de 0, et 1 après. En revanche, aucune normalisation de caractères ne rapproche deux translittérations latines d'un même prénom, comme Mohammed et Muhammad : c'est un problème de résolution d'entités, qui demande une table d'alias ou une comparaison approchée, hors de portée de l'EM.

### 7. Les montants : chiffres arabes-indiens et séparateur déclaré

NFKC ne transforme pas non plus les chiffres arabes-indiens (U+0660 à U+0669, comme dans ١٥٠٠) en chiffres ASCII ; la fonction `unicodedata.digit` donne leur valeur. Reste le séparateur décimal. En anglais, « 1,500 » vaut mille cinq cents ; en français, « 1,500 » vaut un et demi. Deviner le format est donc dangereux : le séparateur décimal est un **paramètre du champ**, fixé par le modèle de document, et la normalisation renvoie un `Decimal`, comparé par sa valeur et non par son écriture.

### 8. Exemple fait à la main (le code reprend ces valeurs)

Un ordre de virement dont l'agent a extrait cinq champs :

| Champ | Prédiction | Référence | Normalisation | EM |
|---|---|---|---|---|
| montant | 1 500 AED (séparateur U+202F) | AED 1,500.00 | nombre décimal, séparateur « . » | 1 |
| iban | ae07 0331 2345 6789 0123 456 | AE070331234567890123456 | sans espaces, majuscules | 1 |
| bénéficiaire | Fatima  Al Mansoori (deux espaces) | fatima al mansoori | NFKC, espaces, casse | 1 |
| date | 2026-03-05 | 05/03/2026 | format AAAA-MM-JJ | 1 |
| portefeuille | 4kr9vTqW2mZp8sLx | 4kR9vTqW2mZp8sLx | aucune (Base58) | 0 |

L'EM par champ vaut 4/5 = 0,8, et son seul échec est réel : l'adresse extraite désigne un autre portefeuille. L'ancienne version, qui ne faisait que `strip().lower()`, échoue sur le montant, l'IBAN, le bénéficiaire et la date, et réussit sur le portefeuille : 1/5 = 0,2, avec pour seul « succès » un faux positif dangereux.

## Effets et comportement

- **L'EM ne pardonne rien de ce que la normalisation ne couvre pas.** Une virgule, un article, un ordre de mots différent suffisent à faire échouer une réponse juste. C'est voulu pour un montant, gênant pour une phrase.
- **L'EM monte quand on relâche la normalisation, sans que l'agent change** (point 2). Une hausse d'EM après une modification de la normalisation n'est pas une amélioration de l'agent.
- **L'EM par champ révèle où l'extraction casse.** Un EM global de 0,8 peut cacher un champ à 0,4.
- **L'EM se calcule sans juge**, de façon exacte et rejouable ; c'est son principal avantage sur Answer Correctness.

## Du symbole au code Python

$$
\nu
$$

**Variable ou fonction :** `normaliser_texte`, `normaliser_squad`, `normaliser_arabe`, `normaliser_montant`, `normaliser_iban`, `normaliser_date`, `normaliser_base58`

$$
\frac{1}{N} \sum_{i} \mathbf{1}[\nu(\hat y_i) = \nu(y_i)]
$$

**Variable ou fonction :** `exact_match(predictions, references, normaliser)`

$$
\max_{y \in Y_i} \mathbf{1}[\nu(\hat y_i) = \nu(y)]
$$

**Variable ou fonction :** `em_multi(prediction, references)`

$$
\text{EM}_c
$$

**Variable ou fonction :** `em_par_champ(prediction, reference, normaliseurs)`

$$
F_1^{\text{mots}}
$$

**Variable ou fonction :** `f1_tokens(prediction, reference)`

### Déroulé, ligne par ligne

**`normaliser_texte(s)`** enchaîne trois opérations. `unicodedata.normalize("NFKC", s)` remplace les caractères de compatibilité par leur forme canonique : les espaces insécables U+00A0 et U+202F deviennent des espaces ordinaires, les chiffres pleine chasse deviennent des chiffres ASCII. `" ".join(….split())` découpe la chaîne sur toute suite de blancs et la recolle avec un seul espace, ce qui retire aussi les espaces de début et de fin. `casefold()` est une mise en minuscules plus complète que `lower()`, prévue pour comparer des chaînes.

**`normaliser_squad(s, articles)`** applique d'abord `normaliser_texte`, ce qui garantit la propriété de monotonie du point 2. Elle retire ensuite chaque caractère de `string.punctuation` (le point de « Department. », le signe « % »), puis les mots de la liste `articles`. La liste par défaut est celle de SQuAD, en anglais ; pour des réponses en français, on peut passer sa propre liste, à déclarer avec le score.

**`normaliser_arabe(s)`** applique NFKC, retire les caractères de l'ensemble `DIACRITIQUES_AR` (les voyelles brèves de U+064B à U+0652, construites par `range`, et le tatweel U+0640), puis remplace les lettres de la table `LETTRES_AR` : les trois alefs à hamza par l'alef nu, le ta marbuta par le ha, l'alef maqsura par le ya. La table est construite avec `chr(…)` pour que chaque point de code soit lisible dans le source.

**`normaliser_montant(s, separateur_decimal)`** passe en majuscules et retire « AED », convertit chaque chiffre par `unicodedata.digit` (ce qui traite ١٥٠٠), supprime les blancs et le séparateur de milliers, remplace le séparateur décimal par un point, puis vérifie par `re.fullmatch` qu'il ne reste qu'un nombre. Pour « AED 1,500.00 », on obtient la chaîne `1500.00`, puis `Decimal("1500.00").normalize()`, égal à `Decimal("1500")`. Une valeur illisible lève `ValueError` au lieu d'être comparée de travers.

**`normaliser_iban`**, **`normaliser_date`** et **`normaliser_base58`** sont les normalisations des trois autres champs : l'IBAN perd ses espaces et passe en majuscules, la date est réécrite en AAAA-MM-JJ, et l'adresse Base58 ne perd que les espaces autour, sans aucun changement de casse.

**`exact_match(predictions, references, normaliser)`**, le cœur du fichier.

- `if len(predictions) != len(references)` lève `ValueError` : « 3 prédictions pour 5 références ». C'est la correction du bug du point 4.
- `if not references: return None` : sans exemple, pas de score.
- La somme `sum(normaliser(p) == normaliser(r) for p, r in zip(predictions, references, strict=True))` additionne des booléens, que Python compte comme 0 et 1, puis on divise par `len(references)`.

**`ancienne_version`** recopie l'ancien code : `zip` sans `strict`, `strip().lower()`, et une division par `len(predictions)`.

**`em_multi(prediction, references)`** prend le maximum des comparaisons : « Dubai Land Department » est accepté si l'une des références, ici « the Dubai Land Department », lui est égale après normalisation SQuAD.

**`f1_tokens(prediction, reference)`** coupe les deux chaînes normalisées en mots, calcule l'intersection de multi-ensembles `Counter(p) & Counter(r)`, qui garde pour chaque mot le plus petit des deux comptes, puis la précision, le rappel et leur moyenne harmonique. Pour « retenue de 10 » contre « retenue de 5 », deux mots sont communs sur trois de chaque côté : P = R = 2/3 et F1 = 2/3.

**`em_par_champ(prediction, reference, normaliseurs)`** parcourt les champs de la **référence** : un champ absent de la prédiction vaut 0, et une valeur que la normalisation ne sait pas lire vaut aussi 0, au lieu de faire planter toute l'évaluation.

**`main()`**, bloc par bloc.

1. Trois écritures de « 1 500 AED » (séparateur U+202F, U+00A0, puis espace ordinaire avec un double espace) : 0 pour l'ancienne version, 1 après normalisation.
2. « The Dubai Land Department. » contre « dubai land department » : 0 avec `normaliser_texte`, 1 avec `normaliser_squad`.
3. Trois paires de noms arabes : EM 0 sans normalisation arabe, 1 avec ; et « Mohammed » contre « Muhammad » reste à 0.
4. Quatre écritures du même montant donnent toutes `Decimal("1500")`, et « 1 500,50 » en convention française donne 1500,5. Le programme vérifie aussi que NFKC seul ne convertit pas ١٥٠٠.
5. L'exemple du tableau : `{'montant': 1, 'iban': 1, 'beneficiaire': 1, 'date': 1, 'portefeuille': 0}`, EM par champ 0,8, ancienne version 0,2.
6. Trois prédictions pour cinq références : 1,0 pour l'ancienne version, 0,6 en comptant les réponses manquantes comme fausses, et `ValueError` pour la nouvelle.
7. Sur cinq couples : 0,0, puis 0,4, puis 0,6 selon la normalisation, et EM ≤ F1 des mots pour chaque couple.
8. Wilson sur 46/50 : [0,8116 ; 0,9685]. Enfin, une liste vide donne `None`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`normaliser_iban(s)`** — Cette fonction est le guichetier de banque qui recopie un numéro de compte d'une seule traite, sans les blancs que le client a mis pour se relire : elle reçoit une chaîne, la découpe sur toute suite de blancs, recolle les morceaux sans séparateur et passe le tout en majuscules, sans aucune vérification de format ni de clé de contrôle. Elle renvoie l'IBAN ainsi compacté : « ae07 0331 2345 6789 0123 456 », écrit par l'agent, devient `AE070331234567890123456`, exactement la référence, si bien que le champ `iban` de l'ordre de virement obtient 1 dans `em_par_champ`.

**`normaliser_date(s)`** — Celle-ci est l'archiviste qui range toutes les dates dans le même format avant de les comparer : elle reçoit une chaîne, retire les blancs autour, la renvoie telle quelle si elle a déjà la forme AAAA-MM-JJ, et sinon cherche la forme JJ/MM/AAAA pour la réécrire en AAAA-MM-JJ. Toute autre écriture lève une `ValueError`, que `em_par_champ` transforme en 0 pour ce champ ; la fonction ne vérifie pas qu'une date existe vraiment au calendrier. Ainsi « 05/03/2026 » de la référence devient « 2026-03-05 », comme la prédiction, et le champ `date` compte pour 1.

**`normaliser_base58(s)`** — Cette fonction est le gardien scrupuleux d'une adresse de portefeuille crypto, où chaque majuscule compte : elle reçoit une chaîne et se contente d'en retirer les blancs autour, sans toucher à la casse, puisqu'en Base58 un « R » et un « r » ne désignent pas le même caractère. Elle renvoie l'adresse ainsi nettoyée ; dans l'exemple du virement, « 4kr9vTqW2mZp8sLx » ne vaut pas « 4kR9vTqW2mZp8sLx », et le champ `portefeuille` obtient 0, alors que l'ancienne version, qui passait tout en minuscules, y voyait à tort son seul succès.

**`exact_match(predictions, references, normaliser)`** — Celle-ci est le correcteur intransigeant qui pose chaque copie sur le corrigé et ne compte que les réponses identiques, une fois l'une et l'autre récrites par la même normalisation : elle reçoit la liste des prédictions, celle des références et une fonction de normalisation, `normaliser_texte` par défaut, lève une `ValueError` du type « 3 prédictions pour 5 références » si les deux listes n'ont pas la même longueur, et renvoie `None` si elles sont vides. Sinon, elle compte les paires égales après normalisation, avec un `zip` strict, et divise par le nombre de références : 1 pour les trois écritures de « 1 500 AED », 0,0, 0,4 et 0,6 sur les cinq couples selon que la normalisation est stricte, textuelle ou SQuAD, et 0,6 quand les deux réponses manquantes sont comptées comme fausses.

**`ancienne_version(predictions, references)`** — Cette fonction est l'ancien correcteur, conservé pour montrer ses deux défauts : elle reçoit les deux listes, renvoie 0 s'il n'y a aucune prédiction, compare chaque paire après un simple `strip().lower()` grâce à un `zip` qui s'arrête en silence à la liste la plus courte, puis divise par le nombre de prédictions. Elle renvoie donc 0 pour les trois écritures de « 1 500 AED » aux espaces insécables, 0,2 pour l'ordre de virement, où son seul succès est le portefeuille, à tort, et 1 pour trois prédictions justes face à cinq références, comme si les deux réponses manquantes n'existaient pas.

**`em_multi(prediction, references, normaliser)`** — Celle-ci est l'examinateur bienveillant qui accepte plusieurs bonnes réponses au même énoncé : elle reçoit une prédiction, une liste de références acceptables et une normalisation, `normaliser_squad` par défaut, lève une `ValueError` si la liste est vide, et renvoie le maximum, 0 ou 1, des comparaisons de la prédiction normalisée avec chaque référence normalisée. « Dubai Land Department » est ainsi accepté parce que l'une des références, « the Dubai Land Department », lui devient égale une fois l'article retiré ; `main` vérifie aussi que cette note ne dépasse jamais la F1 des mots sur les cinq couples.

**`em_par_champ(prediction, reference, normaliseurs)`** — Cette fonction est le contrôleur d'un formulaire, qui vérifie chaque case avec la règle qui lui est propre : elle reçoit la prédiction et la référence sous forme de dictionnaires, et un dictionnaire qui associe à chaque champ sa normalisation, puis parcourt les champs de la référence, en donnant 0 à un champ absent de la prédiction et 0 aussi à une valeur que la normalisation ne sait pas lire, au lieu de faire planter l'évaluation. Elle renvoie un dictionnaire de 1 et de 0 : pour l'ordre de virement, montant, IBAN, bénéficiaire et date valent 1 et le portefeuille 0, d'où un Exact Match par champ de 0,8.

**`wilson(succes, n, z)`** — Cette fonction est la fonction canonique du parcours, recopiée sans changement, l'arpenteur qui entoure chaque taux de sa marge d'incertitude : elle reçoit un nombre de succès, un nombre d'essais et z, 1,96 par défaut, renvoie `None` si n = 0, lève `ValueError` si les succès sortent de [0, n], puis calcule le centre et la demi-largeur de l'intervalle de Wilson à 95 %. Elle renvoie les deux bornes ; pour 46 réponses exactes sur 50, un Exact Match de 0,92, l'intervalle va de 0,8116 à 0,9685, ce qui rappelle qu'un score mesuré sur 50 exemples reste incertain de plusieurs points.

**`main()`** — C'est le chef d'orchestre des huit démonstrations : il montre que les trois écritures de « 1 500 AED » échouent avec l'ancienne version et réussissent après normalisation, que la normalisation SQuAD retire ponctuation et articles, que la normalisation arabe rapproche trois paires de noms sans rapprocher deux translittérations latines, et que quatre écritures d'un montant donnent toutes 1500. Il évalue ensuite l'ordre de virement champ par champ, 0,8 contre 0,2 pour l'ancienne version, montre la troncature silencieuse de l'ancien `zip`, vérifie l'ordre 0,0, 0,4, 0,6 des normalisations, l'inégalité EM ≤ F1 et la F1 de 2/3 sur « retenue de 10 % », puis l'intervalle de Wilson sur 46 sur 50, avant d'afficher « OK ».

```python
"""Étape 64 — Exact Match : normalisation déclarée, par champ, longueurs vérifiées, vide → None."""
import math
import re
import string
import sys
import unicodedata
from collections import Counter
from decimal import Decimal

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

NBSP = chr(0x00A0)          # espace insécable
NNBSP = chr(0x202F)         # espace fine insécable, séparateur de milliers en français


# ---------------------------------------------------------------- normalisations
def normaliser_texte(s: str) -> str:
    """NFKC (U+00A0 et U+202F deviennent des espaces), espaces fusionnés, casse ignorée."""
    return " ".join(unicodedata.normalize("NFKC", s).split()).casefold()


def normaliser_squad(s: str, articles: tuple[str, ...] = ("a", "an", "the")) -> str:
    """Normalisation SQuAD, appliquée APRÈS normaliser_texte : ponctuation et articles retirés."""
    s = normaliser_texte(s)
    s = "".join(c for c in s if c not in string.punctuation)
    return " ".join(m for m in s.split() if m not in articles)


DIACRITIQUES_AR = {chr(c) for c in range(0x064B, 0x0653)} | {chr(0x0640)}   # tashkil (U+064B à U+0652) et tatweel
LETTRES_AR = str.maketrans({chr(0x0623): chr(0x0627), chr(0x0625): chr(0x0627), chr(0x0622): chr(0x0627),  # alef hamza → alef
                            chr(0x0629): chr(0x0647),                                                   # ta marbuta → ha
                            chr(0x0649): chr(0x064A)})                                                  # alef maqsura → ya


def normaliser_arabe(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = "".join(c for c in s if c not in DIACRITIQUES_AR).translate(LETTRES_AR)
    return " ".join(s.split())


def normaliser_montant(s: str, separateur_decimal: str = ".") -> Decimal:
    """« AED 1,500.00 », « 1 500 AED », « ١٥٠٠ AED » → Decimal('1500'). Le séparateur décimal est déclaré."""
    s = unicodedata.normalize("NFKC", s).upper().replace("AED", "")
    chiffres = "".join(str(unicodedata.digit(c)) if c.isdigit() else c for c in s)   # chiffres arabes-indiens
    milliers = "," if separateur_decimal == "." else "."
    nettoye = "".join(chiffres.split()).replace(milliers, "").replace(separateur_decimal, ".")
    if not re.fullmatch(r"\d+(\.\d+)?", nettoye):
        raise ValueError(f"montant illisible : {s!r}")
    return Decimal(nettoye).normalize()


def normaliser_iban(s: str) -> str:
    return "".join(s.split()).upper()


def normaliser_date(s: str) -> str:
    """Accepte AAAA-MM-JJ et JJ/MM/AAAA ; renvoie AAAA-MM-JJ."""
    s = s.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return s
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s)
    if not m:
        raise ValueError(f"date illisible : {s!r}")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"


def normaliser_base58(s: str) -> str:
    """Adresse crypto en Base58 : sensible à la casse. On retire seulement les espaces autour."""
    return s.strip()


# ---------------------------------------------------------------- métriques
def exact_match(predictions: list[str], references: list[str], normaliser=normaliser_texte) -> float | None:
    """EM = part des paires égales après normalisation ; None si la liste est vide."""
    if len(predictions) != len(references):
        raise ValueError(f"{len(predictions)} prédictions pour {len(references)} références")
    if not references:
        return None
    return sum(normaliser(p) == normaliser(r) for p, r in zip(predictions, references, strict=True)) / len(references)


def ancienne_version(predictions: list[str], references: list[str]) -> float:
    """Version d'origine : zip tronque en silence, casse et espaces seulement."""
    if not predictions:
        return 0.0
    matches = sum(p.strip().lower() == r.strip().lower() for p, r in zip(predictions, references))
    return matches / len(predictions)


def em_multi(prediction: str, references: list[str], normaliser=normaliser_squad) -> int:
    """Plusieurs réponses acceptables : EM = max sur les références."""
    if not references:
        raise ValueError("au moins une référence")
    return max(int(normaliser(prediction) == normaliser(r)) for r in references)


def f1_tokens(prediction: str, reference: str) -> float | None:
    """F1 au niveau des mots (SQuAD), sur des multi-ensembles ; None si les deux sont vides."""
    p, r = normaliser_squad(prediction).split(), normaliser_squad(reference).split()
    if not p and not r:
        return None
    commun = sum((Counter(p) & Counter(r)).values())
    if commun == 0:
        return 0.0
    precision, rappel = commun / len(p), commun / len(r)
    return 2 * precision * rappel / (precision + rappel)


def em_par_champ(prediction: dict[str, str], reference: dict[str, str], normaliseurs: dict) -> dict[str, int]:
    """1 ou 0 par champ de la référence ; un champ absent de la prédiction vaut 0."""
    resultat = {}
    for champ, attendu in reference.items():
        if champ not in prediction:
            resultat[champ] = 0
            continue
        norm = normaliseurs[champ]
        try:
            resultat[champ] = int(norm(prediction[champ]) == norm(attendu))
        except ValueError:
            resultat[champ] = 0                        # valeur illisible : fausse, pas d'exception en évaluation
    return resultat


def wilson(succes: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    """Intervalle de Wilson à 95 % pour une proportion ; None si n = 0."""
    if n == 0:
        return None
    if not 0 <= succes <= n:
        raise ValueError("il faut 0 <= succes <= n")
    p = succes / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    demi = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (centre - demi, centre + demi)


def main() -> None:
    print("1. Espaces insécables : « 1 500 AED » écrit de trois façons")
    variantes = ["1" + NNBSP + "500 AED", "1" + NBSP + "500 AED", "1 500  AED"]
    for v in variantes:
        code = f"U+{ord(v[1]):04X}" + (" et double espace" if "  " in v else "")
        print(f"  séparateur {code:<22} ancien = {ancienne_version([v], ['1 500 AED']):.0f}   normalisé = {exact_match([v], ['1 500 AED']):.0f}")
    assert ancienne_version(variantes, ["1 500 AED"] * 3) == 0.0 and exact_match(variantes, ["1 500 AED"] * 3) == 1.0

    print("2. Normalisation SQuAD : ponctuation et articles")
    pred, ref = "The Dubai Land Department.", "dubai land department"
    print(f"  texte = {exact_match([pred], [ref]):.0f}   squad = {exact_match([pred], [ref], normaliser_squad):.0f}")
    assert exact_match([pred], [ref]) == 0.0 and exact_match([pred], [ref], normaliser_squad) == 1.0

    print("3. Arabe : diacritiques, alef, ta marbuta")
    paires = [("مُحَمَّد", "محمد"), ("أحمد", "احمد"), ("فاطمة", "فاطمه")]
    brut = exact_match([a for a, _ in paires], [b for _, b in paires], normaliser_texte)
    ar = exact_match([a for a, _ in paires], [b for _, b in paires], normaliser_arabe)
    print(f"  3 paires : EM texte = {brut:.4f}   EM arabe normalisé = {ar:.4f}")
    assert brut == 0.0 and ar == 1.0
    assert exact_match(["Mohammed"], ["Muhammad"], normaliser_squad) == 0.0   # translittérations : hors de portée

    print("4. Montants : NFKC ne convertit pas les chiffres arabes-indiens, unicodedata.digit oui")
    assert unicodedata.normalize("NFKC", "١٥٠٠") != "1500"
    montants = ["AED 1,500.00", "1" + NNBSP + "500 AED", "١٥٠٠ AED", "1500"]
    valeurs = [normaliser_montant(m) for m in montants]
    print(f"  {[format(v, 'f') for v in valeurs]}   « 1 500,50 » en convention française → {normaliser_montant('1 500,50', ','):f}")
    assert len(set(valeurs)) == 1 and valeurs[0] == Decimal("1500")
    assert normaliser_montant("1 500,50", ",") == Decimal("1500.5")

    print("5. Exemple fait à la main : un ordre de virement, cinq champs")
    reference = {"montant": "AED 1,500.00", "iban": "AE070331234567890123456", "beneficiaire": "fatima al mansoori",
                 "date": "05/03/2026", "portefeuille": "4kR9vTqW2mZp8sLx"}
    prediction = {"montant": "1" + NNBSP + "500 AED", "iban": "ae07 0331 2345 6789 0123 456",
                  "beneficiaire": "Fatima  Al Mansoori", "date": "2026-03-05", "portefeuille": "4kr9vTqW2mZp8sLx"}
    normaliseurs = {"montant": normaliser_montant, "iban": normaliser_iban, "beneficiaire": normaliser_texte,
                    "date": normaliser_date, "portefeuille": normaliser_base58}
    par_champ = em_par_champ(prediction, reference, normaliseurs)
    em_champs = sum(par_champ.values()) / len(par_champ)
    em_vieux = ancienne_version(list(prediction.values()), list(reference.values()))
    print(f"  par champ : {par_champ}")
    print(f"  EM par champ = {em_champs:.2f}   ancienne version = {em_vieux:.2f} (son seul « succès » est le portefeuille, à tort)")
    assert par_champ == {"montant": 1, "iban": 1, "beneficiaire": 1, "date": 1, "portefeuille": 0}
    assert em_champs == 0.8 and em_vieux == 0.2
    assert "4kR9vTqW2mZp8sLx".lower() == "4kr9vTqW2mZp8sLx".lower()      # minuscules globales : faux positif

    print("6. Longueurs différentes : l'ancien zip tronque en silence")
    preds, refs = ["a", "b", "c"], ["a", "b", "c", "d", "e"]
    print(f"  ancienne version = {ancienne_version(preds, refs):.2f}   réponses manquantes comptées fausses = {exact_match(preds + ['', ''], refs):.2f}")
    assert ancienne_version(preds, refs) == 1.0 and exact_match(preds + ["", ""], refs) == 0.6
    try:
        exact_match(preds, refs)
    except ValueError as e:
        print(f"  exact_match → ValueError ({e})")
    else:
        raise AssertionError("des longueurs différentes auraient dû être refusées")

    print("7. Propriétés : normalisation plus grossière ⇒ EM plus haut ; EM <= F1 des mots")
    couples = [("The Dubai Land Department.", "dubai land department"), ("1" + NBSP + "500 AED", "1 500 AED"),
               ("Ejari", "ejari"), ("Retenue de 10 %", "retenue de 5 %"), ("Sharjah", "Ajman")]
    p_l, r_l = [p for p, _ in couples], [r for _, r in couples]
    stricte = exact_match(p_l, r_l, normaliser=lambda s: s)
    em_t = exact_match(p_l, r_l, normaliser_texte)
    em_s = exact_match(p_l, r_l, normaliser_squad)
    print(f"  stricte = {stricte:.1f} <= texte = {em_t:.1f} <= squad = {em_s:.1f}")
    assert stricte <= em_t <= em_s and (stricte, em_t, em_s) == (0.0, 0.4, 0.6)
    for p, r in couples:
        assert em_multi(p, [r]) <= f1_tokens(p, r)
    print(f"  « Retenue de 10 % » / « retenue de 5 % » : EM = 0, F1 des mots = {f1_tokens('Retenue de 10 %', 'retenue de 5 %'):.4f}")
    assert math.isclose(f1_tokens("Retenue de 10 %", "retenue de 5 %"), 2 / 3)
    assert em_multi("Dubai Land Department", ["DLD", "the Dubai Land Department"]) == 1

    print("8. Intervalle de Wilson sur 46 réponses exactes sur 50")
    lo, hi = wilson(46, 50)
    print(f"  EM = 0.92   IC 95 % = [{lo:.4f} ; {hi:.4f}]")
    assert (round(lo, 4), round(hi, 4)) == (0.8116, 0.9685)
    assert exact_match([], []) is None and f1_tokens("", "") is None
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Espaces insécables : « 1 500 AED » écrit de trois façons
  séparateur U+202F                 ancien = 0   normalisé = 1
  séparateur U+00A0                 ancien = 0   normalisé = 1
…
2. Normalisation SQuAD : ponctuation et articles
  texte = 0   squad = 1
…
4. Montants : NFKC ne convertit pas les chiffres arabes-indiens, unicodedata.digit oui
  ['1500', '1500', '1500', '1500']   « 1 500,50 » en convention française → 1500.5
5. Exemple fait à la main : un ordre de virement, cinq champs
  par champ : {'montant': 1, 'iban': 1, 'beneficiaire': 1, 'date': 1, 'portefeuille': 0}
  EM par champ = 0.80   ancienne version = 0.20 (son seul « succès » est le portefeuille, à tort)
6. Longueurs différentes : l'ancien zip tronque en silence
  ancienne version = 1.00   réponses manquantes comptées fausses = 0.60
7. Propriétés : normalisation plus grossière ⇒ EM plus haut ; EM <= F1 des mots
  stricte = 0.0 <= texte = 0.4 <= squad = 0.6
  « Retenue de 10 % » / « retenue de 5 % » : EM = 0, F1 des mots = 0.6667
8. Intervalle de Wilson sur 46 réponses exactes sur 50
  EM = 0.92   IC 95 % = [0.8116 ; 0.9685]
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : « exactement égal » n'a de sens qu'avec une normalisation écrite, testée et déclarée, choisie champ par champ. Trop faible, elle fait échouer des réponses justes ; trop forte, elle fait réussir des réponses fausses.

## Squelette algorithmique

Les entrées sont deux listes de même longueur, les prédictions de l'agent et les réponses attendues, et une fonction de normalisation ν (ou une normalisation par champ pour une sortie structurée). La sortie est une proportion dans [0, 1], ou INDÉFINI si le jeu est vide. L'idée tient en une ligne : normaliser les deux côtés de la même façon, compter les égalités, diviser par le nombre d'exemples ; tout le soin porte sur ν.

```text
ALGORITHME NormaliserTexte
ENTRÉES : une chaîne s
SORTIE  : la chaîne normalisée
    s ← NFKC(s)                                  ▹ U+00A0 et U+202F deviennent U+0020
    mots ← découper s sur tout blanc
    s ← joindre mots avec un seul espace
    RETOURNER minuscules(s)

ALGORITHME ExactMatch
ENTRÉES : prédictions ŷ₁ … ŷ_N, références y₁ … y_M, normalisation ν
SORTIE  : EM ∈ [0, 1], ou INDÉFINI
    SI N ≠ M ALORS
        ÉCHOUER « N prédictions pour M références »     ▹ jamais de troncature
    FIN SI
    SI N = 0 ALORS
        RETOURNER INDÉFINI
    FIN SI
    égaux ← 0
    POUR i DE 1 À N FAIRE
        SI ν(ŷᵢ) = ν(yᵢ) ALORS
            égaux ← égaux + 1
        FIN SI
    FIN POUR
    RETOURNER égaux / N                          ▹ = (Σ EMᵢ) / N, et 0 ≤ EM ≤ 1

ALGORITHME ExactMatchParChamp
ENTRÉES : prédiction p, référence r (dictionnaires), normalisations ν_c
SORTIE  : un 0 ou un 1 par champ de r
    POUR chaque champ c de r FAIRE
        SI c absent de p ALORS
            résultat[c] ← 0
        SINON SI ν_c(p[c]) ou ν_c(r[c]) est illisible ALORS
            résultat[c] ← 0
        SINON
            résultat[c] ← 1 si ν_c(p[c]) = ν_c(r[c]), 0 sinon
        FIN SI
    FIN POUR
    RETOURNER résultat

ALGORITHME F1DesMots
ENTRÉES : prédiction ŷ, référence y
    T̂ ← multi-ensemble des mots de ν(ŷ) ; T ← multi-ensemble des mots de ν(y)
    SI T̂ et T sont vides ALORS RETOURNER INDÉFINI FIN SI
    commun ← Σ sur les mots m de min(T̂[m], T[m])
    SI commun = 0 ALORS RETOURNER 0 FIN SI
    P ← commun / |T̂| ; R ← commun / |T|
    RETOURNER 2PR / (P + R)
```

**Complexité :** chaque normalisation parcourt sa chaîne un nombre fixe de fois (NFKC, découpage, recollage, minuscules), donc elle coûte O(L) pour une chaîne de L caractères, et la comparaison de deux chaînes normalisées coûte aussi O(L). Sur un jeu de N exemples de longueur moyenne L, ExactMatch coûte O(N·L) en temps : un passage par exemple, rien de quadratique. La mémoire supplémentaire est O(L), le temps de garder les deux chaînes normalisées de l'exemple en cours, plus O(1) pour le compteur `égaux` : on n'a pas besoin de stocker toutes les versions normalisées. ExactMatchParChamp coûte O(C·L) pour C champs. F1DesMots coûte O(L) en temps et en mémoire, parce que construire les deux compteurs et calculer leur intersection passe une fois sur chaque mot, avec des accès en temps constant moyen dans une table de hachage.

**Du squelette au code :** NormaliserTexte est `normaliser_texte` ; ses variantes `normaliser_squad`, `normaliser_arabe`, `normaliser_montant`, `normaliser_iban`, `normaliser_date` et `normaliser_base58` jouent le rôle de ν ou de ν_c. Dans ExactMatch, le test « SI N ≠ M » est la première ligne de `exact_match`, le cas « N = 0 » est `if not references: return None`, et la boucle POUR avec son compteur est la somme de booléens `sum(normaliser(p) == normaliser(r) for p, r in zip(…, strict=True))`, divisée par `len(references)`. ExactMatchParChamp est `em_par_champ`, où la branche « illisible » est le `except ValueError`. F1DesMots est `f1_tokens`, où le minimum des comptes est l'opération `Counter(p) & Counter(r)`. La version à plusieurs références, `em_multi`, ajoute un maximum autour de la comparaison.

## Cas d'usage réels aux Émirats

Les volumes et seuils ci-dessous sont illustratifs ; les formats sont ceux du guide du parcours.

### Banque — l'extraction d'un ordre de virement, champ par champ

Une banque de détail de Dubaï fait extraire par un agent les champs des ordres de virement reçus en PDF ou en photo : montant, IBAN, nom du bénéficiaire, date d'exécution. Son jeu d'évaluation contient 500 ordres dont un opérateur a saisi les valeurs justes. Un EM global de 0,8 ne dirait pas quoi corriger ; l'EM par champ montre par exemple que le montant échoue à cause des séparateurs de milliers et des chiffres arabes-indiens, alors que l'IBAN passe. L'IBAN est d'abord validé par le contrôle mod 97 du guide (un IBAN émirien a 23 caractères et commence par AE), puis comparé sans espaces et en majuscules. La banque fixe un seuil de 0,99 sur la borne basse de Wilson pour le montant et l'IBAN, parce qu'une erreur y est un virement mal dirigé ; avec 500 ordres, il faut alors au plus un ou deux échecs. L'indicateur suivi en production est l'EM par champ entre l'extraction de l'agent et la valeur validée par l'opérateur.

### Crypto — une adresse de portefeuille ne se met jamais en minuscules

Une plateforme d'actifs virtuels agréée par la VARA fait vérifier par un agent que l'adresse de destination saisie dans une demande de retrait est bien celle du portefeuille enregistré par le client. Une première version de l'évaluation passait toutes les chaînes en minuscules, et affichait un EM de 1 sur une adresse qui ne différait de la bonne que par la casse de deux caractères. En Base58, ces deux chaînes désignent deux portefeuilles différents : le contrôle aurait laissé partir des fonds vers une adresse inconnue. La plateforme utilise désormais une normalisation par champ : rien d'autre que le retrait des espaces autour de l'adresse. Toute différence bloque le retrait et le renvoie à la conformité. L'indicateur suivi est le nombre de faux positifs trouvés par un audit mensuel, avec un objectif de zéro.

### RH — Emirates ID et noms arabes dans les dossiers de visa

Un cabinet RH présent dans plusieurs émirats extrait des formulaires scannés l'Emirates ID et le nom de chaque employé pour préparer les dossiers MOHRE. L'Emirates ID s'affiche sous la forme 784-AAAA-NNNNNNN-C ; la normalisation retire tirets et espaces et vérifie le format (15 chiffres commençant par 784) avant la comparaison. Pour le nom en arabe, la normalisation retire les voyelles brèves et unifie alef, ta marbuta et alef maqsura : sans elle, un nom écrit avec ses diacritiques sur le passeport et sans eux dans le système compterait comme une erreur d'extraction. Le cabinet sait aussi ce que l'EM ne fait pas : Mohammed, Muhammad et Mohamed restent trois chaînes différentes, et le rapprochement des translittérations passe par une table d'alias validée par un humain. L'indicateur suivi est l'EM du numéro d'identité, qui doit être de 1, et le taux de noms renvoyés en vérification manuelle.

### Immobilier — numéros Ejari et surfaces en sqft

Une agence de Dubaï et d'Abu Dhabi fait extraire des contrats de location le numéro d'enregistrement Ejari, le loyer annuel en AED et la surface en sqft. Le numéro Ejari se compare en EM strict après retrait des espaces : c'est une clé, pas un texte. Le loyer passe par la normalisation des montants, avec un séparateur décimal déclaré par modèle de contrat, parce que certains modèles anglais écrivent « 85,000 » et certains documents français « 85 000 ». La surface est normalisée en nombre suivi de l'unité, pour que « 1,250 sqft » et « 1250 sq ft » coïncident. Sans ces règles, l'agence aurait mesuré un EM bas et cherché un défaut dans l'agent alors qu'il était dans la mesure. L'indicateur suivi est l'EM par champ et, pour le loyer, le nombre de contrats où l'agent et le système de gestion divergent.

### BTP — des factures de sous-traitance, et la taille du jeu

Un groupe de construction qui mène de grands chantiers à Dubaï contrôle les montants des factures de ses sous-traitants : hors taxe, TVA de 5 % et toutes taxes comprises, par exemple 240 000, 12 000 et 252 000 AED. Certaines factures écrivent les montants en chiffres arabes-indiens, d'autres avec des espaces fines : la normalisation par `unicodedata.digit` et NFKC les ramène au même `Decimal`. Le groupe a d'abord évalué son agent sur 50 factures et obtenu 46 montants exacts, soit 0,92. L'intervalle de Wilson, de 0,81 à 0,97, montre que ce jeu ne prouve même pas un taux de 0,90 : il faut beaucoup plus de factures pour valider une barrière à 0,95. Le jeu a été porté à plusieurs centaines de factures tirées de plusieurs sous-traitants. L'indicateur suivi est la borne basse de Wilson de l'EM sur les montants TTC.

### Secteur public — une même réponse en arabe ou en anglais

Une entité de services publics en ligne, accessible par UAE Pass, fait répondre un agent à des questions dont la réponse est un nom de procédure ou de document, en arabe ou en anglais selon l'usager. Chaque question du jeu d'évaluation a plusieurs références acceptables : le nom arabe, le nom anglais, un sigle officiel. L'EM retenu est le maximum sur ces références, avec la normalisation arabe pour la version arabe et la normalisation SQuAD pour la version anglaise. Sans les références multiples, une réponse juste en arabe à une question posée en anglais compterait comme une erreur. L'entité publie l'EM par langue et vérifie qu'aucune langue ne décroche de plus de 5 points par rapport à l'autre.

## Pièges et limites

- **Tronquer avec `zip`.** Des longueurs différentes sont une erreur ; une réponse manquante est un échec, à compter comme tel.
- **Normaliser trop fort.** Les minuscules globales, la suppression de toute ponctuation ou de tous les chiffres créent des faux positifs. On normalise champ par champ, et jamais une adresse crypto.
- **Oublier les espaces insécables et les chiffres arabes-indiens.** NFKC traite les premiers, pas les seconds.
- **Deviner le séparateur décimal.** « 1,500 » vaut 1 500 en anglais et 1,5 en français ; le format est un paramètre du champ.
- **Publier un EM sans sa normalisation ni son intervalle.** Le chiffre ne se compare à rien sans les deux.

### Exercice feuille blanche

1. Sans regarder le code, écrire `normaliser_texte` et `exact_match`, avec la vérification des longueurs et la convention `None`, puis vérifier que « 1 500 AED » écrit avec U+202F est égal à « 1 500 AED ».
2. Prédire, puis vérifier : quel EM donne `normaliser_squad` pour « An Ejari certificate » contre « ejari certificate » ? Et `normaliser_texte` ? (Réponses : 1, puis 0.)
3. Trouver le bug : `return sum(p.lower() == r.lower() for p, r in zip(preds, refs)) / len(refs)`. Trouver deux entrées où il donne un résultat faux. (Une piste : des listes de longueurs différentes ; une autre : deux adresses Base58 qui ne diffèrent que par la casse.)

## Pour aller plus loin

En question-réponse, la F1 des mots de SQuAD complète l'EM et accorde un crédit partiel. Pour les dates, montants et unités, on compare souvent des valeurs typées après analyse plutôt que des chaînes, ce qui revient à faire de la normalisation une conversion. Pour les noms translittérés, on mesure la similarité par une distance d'édition ou une table d'alias, et l'on rapporte ce score à part de l'EM.

> Suite : [Théorèmes de fidélité, pertinence et F1](<64b-Theoremes-Fidelite-Pertinence-et-F1.md>) — étape 64 bis.
