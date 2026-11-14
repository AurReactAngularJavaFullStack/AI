# Étape 18 — RAG — Formules, Théorèmes et Algorithmes

> Étape 18 du parcours · Prérequis : [Score de pertinence d'un souvenir](<../04-Contexte-Similarite-et-Memoire/17-Memoire-Formule-Score-de-Pertinence.md>) · Suite : [Similarité cosinus, seuils et calibrage](<19-RAG-Formule-Similarite-Cosinus.md>)

**Leçon longue pour AI Software Engineer — Aurélien Hamzaoui**

## Introduction narrative : pourquoi ces formules changent la donne dans un vrai projet

Imagine que tu travailles, comme dans le projet d'assurance automobile de ton CV, pour un assureur auto et santé de Dubaï. Un assuré décrit un sinistre en quelques phrases : « J'ai percuté un poteau en reculant dans un parking souterrain de Dubai Marina, mon pare-chocs est enfoncé et la caméra de recul ne fonctionne plus. » L'agent IA doit retrouver, parmi des milliers de clauses de contrat, de procédures internes et de notes de gestion, les éléments exacts qui permettent de décider si le sinistre est couvert, quelle franchise s'applique et quelles pièces justificatives demander. Sans une bonne recherche, l'agent va soit rater la clause pertinente, soit noyer la réponse dans du bruit. C'est précisément ici que la similarité cosinus et les métriques de retrieval deviennent des outils quotidiens, pas des abstractions académiques.

Dans un cabinet RH présent dans plusieurs émirats, le même problème se pose pour les règles d'onboarding : un recruteur demande « quelles démarches pour un salarié transféré de Dubaï vers Abu Dhabi, déjà titulaire d'un visa de travail ? ». L'agent doit récupérer les bons fragments de documentation de conformité avant de proposer la suite. Les formules que nous allons détailler sont le socle de cette capacité. Ce fichier est le point d'entrée du dossier RAG : il raconte la chaîne complète, la code en Python standard de bout en bout, et renvoie aux fichiers qui démontrent chaque formule.

## Définition

Le Retrieval-Augmented Generation (RAG) repose sur trois étapes : l'**indexation** (découper les documents en morceaux, ou *chunks*, et transformer chaque morceau en vecteur), la **récupération** (trouver les vecteurs les plus proches de celui de la question) et la **génération** (le LLM rédige sa réponse à partir des passages récupérés, en les citant). L'ancienne version de ce fichier affirmait que la qualité de la récupération « dépend quasi entièrement de la fonction de similarité choisie » : c'est faux. Elle dépend surtout du modèle d'embedding, qui décide quels textes reçoivent des vecteurs proches, du découpage, car un morceau trop long dilue l'information et un morceau coupé au mauvais endroit la perd, et du reranking, un second modèle qui reclasse les meilleurs candidats. Pour des vecteurs normalisés, cosinus, produit scalaire et distance euclidienne donnent exactement le même classement (démonstration, point 1, et étape 14) : changer de fonction de similarité ne change alors rien. La similarité cosinus s'est imposée parce qu'elle ignore la norme des vecteurs et ne regarde que leur direction ; en sac de mots, cela neutralise la longueur des morceaux, et beaucoup de modèles d'embedding neuronaux renvoient de toute façon des vecteurs de norme 1.

## Rôle dans un agent

Le RAG est l'outil de *perception* documentaire de l'agent. Avant de *décider*, l'agent appelle le **retriever**, souvent exposé comme un outil (« chercher dans les conditions générales »), qui renvoie les k passages les plus proches avec leur source. L'agent assemble ces passages dans son prompt et génère une réponse qui les cite ; un **juge** peut ensuite *observer* la réponse et mesurer sa fidélité au contexte (la Faithfulness) avant l'envoi. Les métriques de retrieval (Recall@k, Precision@k, MRR) ne servent pas pendant la boucle : elles se calculent hors ligne, sur un jeu de questions étiquetées, pour régler le découpage, le modèle et k. Dans une architecture hexagonale, le retriever est un port (`RetrievalPort`) et l'index vectoriel un adaptateur : le domaine, par exemple les règles de couverture, ne dépend ni du modèle d'embedding ni de la base.

## Équation complète

### Formule centrale : similarité cosinus

Soit deux vecteurs d'embeddings 𝐚, 𝐛 ∈ ℝⁿ. La similarité cosinus est définie par :

$$
\cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\lVert \mathbf{a} \rVert \, \lVert \mathbf{b} \rVert} = \frac{\sum_{i=1}^{n} a_i b_i}{\sqrt{\sum_{i=1}^{n} a_i^2} \cdot \sqrt{\sum_{i=1}^{n} b_i^2}}
$$

où θ est l'angle entre les deux vecteurs, · désigne le produit scalaire et ‖ · ‖ la norme euclidienne. Le résultat appartient toujours à l'intervalle [−1, 1], ce que l'inégalité de Cauchy-Schwarz garantit (démontrée à l'étape 14) :

- **1** : même direction. Les deux vecteurs sont proportionnels ; cela ne veut pas dire que les textes sont identiques.
- **0** : vecteurs orthogonaux, aucune relation pour le modèle.
- **−1** : directions opposées, rare en pratique avec les embeddings de texte, qui donnent plutôt des scores entre 0 et 1.

### Métriques de retrieval (démontrées aux étapes 25, 26 et 27)

$$
\text{Recall@}k = \frac{\lvert \text{Pertinents} \cap \text{Top}_k \rvert}{\lvert \text{Pertinents} \rvert}
$$

$$
\text{Precision@}k = \frac{\lvert \text{Pertinents} \cap \text{Top}_k \rvert}{k}
$$

$$
\text{MRR} = \frac{1}{\lvert Q \rvert} \sum_{i=1}^{\lvert Q \rvert} \frac{1}{\text{rang}_i}
$$

Conventions du parcours : Recall@k n'est pas défini (`None`) quand la question n'a aucun passage pertinent, et cette question n'entre pas dans la moyenne ; le rang réciproque vaut 0 quand aucun pertinent n'apparaît dans le classement ; Precision@k divise toujours par k, même si moins de k passages sont renvoyés ; un k < 1 est refusé par `ValueError`.

### Fidélité de la réponse : Faithfulness (démontrée à l'étape 54)

L'ancienne version utilisait la Faithfulness dans un cas d'usage sans la définir. C'est la part des affirmations de la réponse que le contexte récupéré soutient, la mesure qu'utilisent RAGAS et les principaux cadres d'évaluation :

$$
\text{Faithfulness} = \frac{\text{nombre d'affirmations de la réponse soutenues par le contexte}}{\text{nombre total d'affirmations de la réponse}}
$$

Elle n'est pas définie (`None`) pour une réponse qui ne contient aucune affirmation.

### Score hybride (étape 23) et coût de la recherche exhaustive

$$
\text{score}_{\text{hybride}} = \alpha \, \widetilde{s}_{\cos} + (1 - \alpha) \, \widetilde{s}_{\text{BM25}}
$$

$$
C(N, n) = N \times (2n - 1) = O(N \cdot n)
$$

## Décryptage des symboles

$$
\mathbf{a},\quad \mathbf{b}
$$

**Sens :** les deux vecteurs comparés : la question et un morceau · **Type / plage :** listes de n réels · **Variable Python :** `q1`, `v`

**Symbole :** n (noté d à l'étape 15) · **Sens :** dimension des vecteurs · **Type / plage :** entier ≥ 1 · **Variable Python :** `len(VOCABULAIRE)`, ici 12

$$
\theta
$$

**Sens :** angle entre les deux vecteurs · **Type / plage :** de 0° à 180° · **Variable Python :** —

$$
\lVert \mathbf{a} \rVert
$$

**Sens :** norme L2, racine de la somme des carrés · **Type / plage :** réel ≥ 0 · **Variable Python :** calculée dans `cosinus`

$$
N
$$

**Sens :** nombre de morceaux comparables dans l'index · **Type / plage :** entier · **Variable Python :** `len(index)`

$$
k
$$

**Sens :** nombre de passages gardés (top-k) · **Type / plage :** entier ≥ 1 · **Variable Python :** `k`

$$
\text{Pertinents}
$$

**Sens :** morceaux jugés pertinents par un humain pour une question · **Type / plage :** ensemble · **Variable Python :** `pertinents`

$$
\text{Top}_k
$$

**Sens :** les k premiers morceaux du classement · **Type / plage :** ensemble · **Variable Python :** `classement[:k]`

$$
\text{rang}_i
$$

**Sens :** rang du premier morceau pertinent pour la question i · **Type / plage :** entier ≥ 1 · **Variable Python :** dans `rang_reciproque`

$$
Q
$$

**Sens :** jeu de questions de test ; | Q | est leur nombre · **Type / plage :** ensemble · **Variable Python :** `questions`

$$
\alpha
$$

**Sens :** poids du score hybride · **Type / plage :** réel dans [0, 1] · **Variable Python :** — (étape 23)

$$
\widetilde{s}
$$

**Sens :** score ramené dans [0, 1] par min-max (étape 17) · **Type / plage :** réel dans [0, 1] · **Variable Python :** `min_max`

$$
C(N, n)
$$

**Sens :** nombre d'opérations d'une recherche exhaustive · **Type / plage :** entier · **Variable Python :** `compteur.mult + compteur.add`

## Démonstration

### 1. Pour des vecteurs normalisés, produit scalaire, cosinus et distance donnent le même classement

Si ‖ 𝐚 ‖ = ‖ 𝐛 ‖ = 1, le dénominateur du cosinus vaut 1 × 1, donc cosθ = 𝐚 · 𝐛 : le produit scalaire est le cosinus. On peut aller plus loin. Pour une question 𝐪 quelconque et des morceaux normalisés 𝐝̂ⱼ, on a cos(𝐪, 𝐝̂ⱼ) = (𝐪 · 𝐝̂ⱼ) / ‖ 𝐪 ‖, et ‖ 𝐪 ‖ > 0 est le même pour tous les morceaux : classer par cosinus ou par 𝐪 · 𝐝̂ⱼ donne le même ordre, parce que diviser tous les scores par un même nombre positif ne change pas leur ordre. Normaliser les morceaux à l'ingestion suffit donc pour le classement ; normaliser la question ne compte que si l'on applique un seuil absolu. Enfin, l'étape 14 a démontré ‖ 𝐪̂ − 𝐝̂ ‖² = 2 − 2cosθ, fonction décroissante du cosinus : la distance euclidienne donne aussi le même ordre. C'est pour cela que la fonction de similarité n'est pas le levier principal d'un RAG.

Sans normalisation, en revanche, le produit scalaire favorise les vecteurs longs. Contre-exemple tiré du mini-corpus du code : la question « reculé dans un parking, pare-chocs enfoncé, caméra de recul cassée » a pour vecteur 1 sur « parking », « recul », « pare-chocs » et « caméra », donc

$$
\lVert \mathbf{q} \rVert = \sqrt{4} = 2 .
$$

Le morceau publicitaire « Parking partenaire : parking gratuit, parking surveillé, parking couvert… » compte 4 fois « parking » : produit scalaire 4, norme 4, cosinus 4 / (2 × 4) = 0,5. Le morceau de clause « la caméra de recul font partie des éléments couverts » compte une fois « caméra » et une fois « recul » : produit scalaire 2, norme √2, cosinus

$$
2 / (2\sqrt{2}) = 0{,}7071 .
$$

Le produit scalaire brut classe la publicité en tête (4 > 2) ; le cosinus classe la clause en tête (0,7071 > 0,5).

### 2. Le coût de la recherche exhaustive est en O(N · n)

Un produit scalaire en dimension n demande n multiplications, une par coordonnée, et n − 1 additions pour les cumuler, soit 2n − 1 opérations. Parce que les morceaux ont été normalisés à l'ingestion, il n'y a rien d'autre à calculer par morceau : ni norme, ni racine, ni division. Pour N morceaux, on fait donc N(2n − 1) opérations. Il reste à choisir les k meilleurs : trier les N scores coûte de l'ordre de N log N comparaisons, et un tas de taille k (`heapq.nlargest`) de l'ordre de N log k. Le total est en O(N · n + N log k), soit O(N · n) dès que n ≥ log k, ce qui est toujours le cas en pratique (n vaut au moins quelques centaines, log₂ k moins de 10). Sur le mini-corpus, N = 13 morceaux comparables et n = 12 donnent 13 × 12 = 156 multiplications et 13 × 11 = 143 additions, soit 299 = 13 × 23 opérations. À l'échelle d'une vraie base, N = 10⁶ et n = 1024 donnent 10⁶ × 2047 = 2 047 000 000 opérations par question.

Les index approximatifs réduisent N, le nombre de vecteurs comparés. L'ancienne version disait que HNSW et IVF ramènent le coût « à du quasi-logarithmique » : seul HNSW s'en approche, avec de l'ordre de log N étapes de navigation dans son graphe en pratique (un comportement observé, pas une garantie). IVF découpe l'espace en C groupes et ne visite que les p groupes les plus proches de la question : il compare la question aux C centres, puis à environ pN/C vecteurs. Avec

$$
C \approx \sqrt{N} ,
$$

cela fait de l'ordre de √N comparaisons : un coût sous-linéaire, nettement inférieur à N, mais pas logarithmique.

### 3. Exemple fait à la main : les deux calculs du cours

Le calcul en trois dimensions vient de l'ancienne version ; celui en quatre dimensions est repris du doublon « Formules Theoremes », dont les nombres étaient justes mais le LaTeX cassé.

| Calcul | Vecteurs 3D | Vecteurs 4D |
|---|---|---|
| 𝐪 | (0,8 ; 0,3 ; 0,5) | (0,6 ; 0,2 ; 0,8 ; 0,1) |
| 𝐝 | (0,7 ; 0,4 ; 0,6) | (0,5 ; 0,3 ; 0,7 ; 0,2) |
| 𝐪 · 𝐝 | 0,56 + 0,12 + 0,30 = 0,98 | 0,30 + 0,06 + 0,56 + 0,02 = 0,94 |
| ‖ 𝐪 ‖ | √(0,64 + 0,09 + 0,25) = √0,98 ≈ 0,990 | √(0,36 + 0,04 + 0,64 + 0,01) = √1,05 ≈ 1,025 |
| ‖ 𝐝 ‖ | √(0,49 + 0,16 + 0,36) = √1,01 ≈ 1,005 | √(0,25 + 0,09 + 0,49 + 0,04) = √0,87 ≈ 0,933 |
| cosθ | 0,98 / 0,995 ≈ 0,985 | 0,94 / 0,956 ≈ 0,983 |

Un score de 0,985 indique une très forte proximité. Dans un vrai système d'assurance, cela pourrait correspondre à une clause « dommages matériels en stationnement » parfaitement alignée avec la description du sinistre ; mais ce qui compte comme « élevé » dépend du modèle d'embedding, et l'étape 19 montre comment calibrer le seuil.

### 4. Les métriques sur le mini-corpus (calculées, pas démontrées)

Le code pose quatre questions à l'index et compare le top-3 du cosinus à un jugement humain des morceaux pertinents. Les étapes 25, 26 et 27 démontrent les propriétés de ces métriques ; ici, on les calcule seulement.

| Question (termes reconnus) | Top-3 du cosinus | Pertinents | Recall@3 | Precision@3 | RR |
|---|---|---|---|---|---|
| parking, recul, pare-chocs, caméra | §4 #3 (0,7071), §4 #1 (0,5774), §4 #2 (0,5774) | §4 #1, #2, #3 | 1 | 1 | 1 |
| vol, police | §7 #0 (0,7071), §7 #1 (0,7071), procédure #0 (0,5) | §7 #0, #1 | 1 | 0,6667 | 1 |
| inondation, pluies, franchise | météo #0 (0,8165), #1 (0,5774), #2 (0,5774) | météo #0, #2 | 1 | 0,6667 | 1 |
| sinistre, parking | §4 #0 (0,7071), partenaire (0,7071), procédure #0 (0,5) | procédure #0, #1, #2 | 0,3333 | 0,3333 | 0,3333 |
| **Moyenne** | | | 0,8333 | 0,6667 | MRR 0,8333 |

La quatrième question, « Quels documents envoyer pour déclarer un sinistre de parking ? », échoue en partie : « documents » et « envoyer » ne sont pas dans le vocabulaire, si bien que la question ne retient que « sinistre » et « parking », et deux morceaux qui parlent de parking passent devant la procédure de déclaration. C'est la limite d'un sac de mots, qu'un modèle d'embedding neuronal ou une recherche hybride corrige. L'exemple du doublon se vérifie de la même façon : pour le classement docA, docB, docC, docD et les pertinents docB et docE, Recall@3 = 1/2 = 0,5 et Precision@3 = 1/3 ≈ 0,333 ; des rangs 2, 1 et 5 donnent MRR = (1/2 + 1 + 1/5)/3 ≈ 0,5667. Enfin, une réponse dont 3 affirmations sur 4 sont soutenues par le contexte a une Faithfulness de 0,75.

## Effets et comportement

- **Augmenter k** ne peut pas faire baisser Recall@k, parce que le top-k est contenu dans le top-(k+1) ; Precision@k a tendance à baisser, et le prompt s'allonge, donc coûte plus de tokens.
- **Ajouter du recouvrement** multiplie les morceaux (15 au lieu de 11 sur le mini-corpus) mais coupe moins souvent une règle en deux.
- **Changer de modèle d'embedding** change tous les scores : les seuils et les métriques se recalculent (étape 19).
- **Normaliser à l'ingestion** rend produit scalaire, cosinus et distance interchangeables, et retire la norme et la division du calcul par morceau.
- **Augmenter N** fait croître linéairement le coût de la recherche exhaustive ; au-delà de quelques centaines de milliers de morceaux (ordre de grandeur illustratif), on passe à un index approximatif.

## Algorithmes de retrieval détaillés

### Algorithme 1 : recherche par similarité cosinus (naïve)

1. Encoder la question de l'utilisateur en vecteur 𝐪.
2. Pour chaque morceau de la base, encoder un vecteur 𝐝ᵢ (une fois, à l'ingestion, et le normaliser).
3. Calculer cos(𝐪, 𝐝ᵢ) pour tous les i.
4. Trier les morceaux par score décroissant.
5. Retourner les top-k (souvent k = 3 à 10).

Complexité : O(N · n), où N est le nombre de morceaux et n la dimension (démonstration, point 2). En production, on utilise des index approximatifs : HNSW, dont le coût est proche de log N étapes en pratique, ou IVF, dont le coût est sous-linéaire en N.

### Algorithme 2 : recherche hybride (BM25 + cosinus)

Beaucoup de systèmes réels combinent recherche lexicale et sémantique :

1. Calculer un score BM25 pour chaque morceau (étape 22).
2. Calculer le score cosinus.
3. Normaliser les deux scores, souvent par min-max (étape 17) ou par z-score.
4. Combiner les deux scores **normalisés** avec un poids α, selon la formule ci-dessous. L'ancienne version écrivait les scores non normalisés juste après l'étape « normaliser », ce qui annulait l'étape 3.
5. Reclasser éventuellement les 50 premiers avec un reranker (cross-encoder).

$$
\text{score}_{\text{final}} = \alpha \, \widetilde{s}_{\cos} + (1 - \alpha) \, \widetilde{s}_{\text{BM25}}
$$

Dans un contexte BTP, BM25 est excellent pour les termes techniques précis (« retenue de garantie », numéro d'enregistrement à la TVA, intitulé exact d'un poste), tandis que le cosinus capte les reformulations.

## Implémentation Java (extrait réaliste)

```java
public final class CosineSimilarity {
    public static double compute(double[] a, double[] b) {
        if (a.length != b.length) {
            throw new IllegalArgumentException("Dimensions must match");
        }
        double dot = 0.0;
        double normA = 0.0;
        double normB = 0.0;
        for (int i = 0; i < a.length; i++) {
            dot += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }
        double denom = Math.sqrt(normA) * Math.sqrt(normB);
        return denom == 0.0 ? 0.0 : dot / denom;
    }
}
```

Dans une architecture hexagonale, cette classe vit dans un adapter d'infrastructure ; le domaine ne connaît que le port `RetrievalPort`. Une différence avec le Python ci-dessous : pour un vecteur nul, cette classe renvoie 0.0, ce qui fait passer une panne d'embedding (texte vide, appel au modèle échoué) pour un document « sans rapport ». La convention du parcours est de refuser l'entrée ; en Java, on écrirait `throw new IllegalArgumentException("vecteur nul")` à la place du `0.0`.

## Du symbole au code Python

| Java | Python (fonction `cosinus` ci-dessous) |
|---|---|
| `if (a.length != b.length) throw …` | `if len(a) != len(b): raise ValueError(…)` |
| boucle `for` qui cumule `dot`, `normA`, `normB` | trois `sum(…)` sur `zip(a, b)` |
| `Math.sqrt(normA) * Math.sqrt(normB)` | `na * nb` |
| `denom == 0.0 ? 0.0 : dot / denom` | `raise ValueError` si une norme est nulle |
| — | `max(-1.0, min(1.0, …))` contre les arrondis |

$$
\cos(\mathbf{q}, \mathbf{d})
$$

**Variable ou fonction :** `cosinus(q, d)`

$$
\hat{\mathbf{d}} = \mathbf{d} / \lVert \mathbf{d} \rVert
$$

**Variable ou fonction :** `normaliser(d)`

$$
\text{Top}_k
$$

**Variable ou fonction :** `top_k(question, index, k)`

**Symbole :** Recall@k, Precision@k, 1/rang · **Variable ou fonction :** `recall_at_k`, `precision_at_k`, `rang_reciproque`

**Symbole :** MRR · **Variable ou fonction :** `moyenne(rrs)`

**Symbole :** Faithfulness · **Variable ou fonction :** `faithfulness(soutenues, total)`

$$
C(N, n)
$$

**Variable ou fonction :** `Compteur`

### Déroulé, ligne par ligne

**`cosinus(a, b)`** est l'équivalent Python de la classe Java, dans sa version canonique du parcours : même test de dimension, trois sommes au lieu d'une boucle, `ValueError` au lieu de `0.0` pour un vecteur nul, puis `max(-1.0, min(1.0, …))` pour rabattre un arrondi dans [−1, 1]. **`normaliser(v)`** divise chaque coordonnée par la norme et refuse le vecteur nul.

**`mots(texte)`** met en minuscules, remplace les apostrophes par des espaces (« l'expert » donne « l » et « expert »), puis garde les suites de lettres accentuées, de chiffres, de « § » et de tirets, si bien que « pare-chocs » reste un seul mot.

**`decouper(texte, taille, recouvrement)`**, le découpage à taille fixe avec recouvrement.

- `if not 0 <= recouvrement < taille` : un recouvrement égal à la taille donnerait un pas nul et une boucle infinie.
- `pas = taille - recouvrement` : avec 12 mots et 4 de recouvrement, chaque morceau commence 8 mots après le précédent, et reprend donc ses 4 derniers mots.
- `for debut in range(0, len(m), pas)` : pour la clause §7 (31 mots), les débuts valent 0, 8, 16 et 24, donc 4 morceaux ; `break` s'arrête dès qu'un morceau atteint la fin du texte.
- Sans recouvrement (`recouvrement = 0`), la même clause donne 3 morceaux, et la règle « une plainte est déposée auprès de la police dans les 24 heures » est coupée entre le premier et le deuxième.

**`contient(morceau, phrase)`** cherche une suite de mots consécutifs : c'est le test qui vérifie que la règle tient entière dans un morceau.

**`vectoriser(liste_mots)`** compte, pour chacun des 12 termes de `VOCABULAIRE`, ses occurrences dans le morceau : c'est un vecteur jouet de dimension 12, un « sac de mots ». Le morceau publicitaire donne 4 sur la coordonnée « parking » et 0 ailleurs ; la question du parking donne 1 sur « parking », « recul », « pare-chocs » et « caméra » (« reculé » n'est pas « recul » : le sac de mots compare des mots exacts).

**`top_k(question, index, k)`** calcule le cosinus avec chaque morceau, trie par score décroissant et départage les égalités par identifiant ; l'arrondi à 12 décimales dans la clé de tri évite qu'un écart d'arrondi de 10⁻¹⁶ décide entre deux scores égaux, comme les deux 0,7071 de la question sur le vol.

**`Compteur`** refait le produit scalaire en comptant les opérations : une multiplication pour la première coordonnée, puis une multiplication et une addition pour chacune des n − 1 suivantes, soit n multiplications et n − 1 additions.

**`assembler_prompt(question, passages)`** écrit le contexte, un passage par ligne précédé de sa source entre crochets, puis la question et la consigne de citer les sources et de dire quand le contexte ne suffit pas.

**`recall_at_k`, `precision_at_k`, `rang_reciproque`, `moyenne`, `faithfulness`** appliquent les formules et leurs conventions : `None` quand le dénominateur n'existe pas, `ValueError` pour un k < 1 ou une Faithfulness impossible, et `moyenne` ignore les `None`.

**`main()`**, bloc par bloc.

1. Les deux exemples du cours : 0,985 en 3D et 0,983 en 4D, avec les normes 0,990 ; 1,005 ; 1,025 et 0,933 et les produits de normes 0,995 et 0,956. Le vecteur nul lève `ValueError`.
2. Les 5 documents donnent 15 morceaux avec recouvrement (11 sans). La règle du vol tient entière dans un morceau avec recouvrement, pas sans.
3. Deux morceaux ne contiennent aucun terme du vocabulaire, « valeur du véhicule fixée par l expert » et « une copie de son permis de conduire » : leur vecteur est nul, ils sont écartés au lieu de recevoir un score inventé. Il reste N = 13 morceaux comparables.
4. Les quatre questions donnent le tableau de la démonstration, point 4, vérifié par `assert`, puis les moyennes 0,8333 ; 0,6667 et 0,8333.
5. Après normalisation, le produit scalaire de chaque morceau avec la question normalisée égale son cosinus à 10⁻¹² près. Le produit scalaire brut met la publicité en tête (4) ; le cosinus y met la clause (0,7071). Classer par 𝐪 · 𝐝̂, sans normaliser la question, donne le même ordre que le cosinus.
6. Le compteur trouve 156 multiplications et 143 additions, soit 13 × (2 × 12 − 1) = 299 opérations, puis l'ordre de grandeur pour 10⁶ morceaux de dimension 1024.
7. Le prompt contient les trois passages du top-3, chacun avec sa source entre crochets, et rien d'autre entre crochets.
8. La Faithfulness vaut 0,75 pour 3 affirmations soutenues sur 4, et `None` pour une réponse sans affirmation.
9. L'exemple docA à docD du doublon : 0,5 ; 0,333 et 0,5667, et `None` pour une question sans pertinent.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`normaliser(v)`** — On peut l'imaginer comme un tailleur qui raccourcit ou rallonge chaque flèche pour qu'elles aient toutes exactement la même longueur, sans jamais changer la direction où elles pointent : la fonction reçoit un vecteur, calcule sa norme comme la racine de la somme des carrés de ses coordonnées, lève `ValueError` si cette norme est nulle, puisqu'une flèche de longueur zéro n'a pas de direction, puis renvoie la liste des coordonnées divisées par la norme. Le programme s'en sert au point 5 pour montrer qu'après cette mise à longueur 1, un simple produit scalaire redonne le cosinus à 10⁻¹² près.

**`decouper(texte, taille, recouvrement)`** — Cette fonction travaille comme un copiste qui recopie un long contrat sur des fiches de taille fixe, en reprenant en haut de chaque nouvelle fiche les derniers mots de la précédente pour qu'aucune phrase ne soit tranchée net : elle reçoit le texte, le nombre de mots par fiche et le nombre de mots repris, lève `ValueError` si le recouvrement n'est pas compris entre 0 et la taille exclue, découpe le texte en mots avec `mots`, avance d'un pas égal à taille − recouvrement, et s'arrête dès qu'une fiche atteint la fin du texte. Elle renvoie la liste des morceaux, chacun étant une liste de mots ; avec 12 mots et 4 de recouvrement, la clause §7 donne 4 morceaux, 3 sans recouvrement, et les cinq documents en donnent 15 contre 11.

**`contient(morceau, phrase)`** — C'est le relecteur qui vérifie, doigt sur la ligne, qu'une règle importante figure bien d'un seul tenant sur une fiche : la fonction reçoit un morceau et une phrase, tous deux sous forme de listes de mots, fait glisser une fenêtre de la longueur de la phrase sur toutes les positions possibles du morceau, et renvoie `True` dès qu'une fenêtre coïncide mot pour mot avec la phrase, `False` sinon, y compris quand la phrase est plus longue que le morceau. Le programme l'utilise pour prouver que la règle « une plainte est déposée auprès de la police dans les 24 heures » tient entière dans un morceau avec recouvrement, mais pas sans.

**`Compteur.__init__()`** — Le constructeur prépare le carnet d'un contrôleur chargé de compter chaque geste d'un calculateur : il ne reçoit rien d'autre que l'objet à initialiser, crée les deux compteurs `mult` et `add` et les met tous deux à zéro, sans rien renvoyer. Ces deux nombres s'accumulent ensuite au fil des appels à `produit_scalaire`, si bien qu'un seul `Compteur` suffit pour mesurer le coût total d'une recherche exhaustive sur tout l'index, morceau après morceau.

**`Compteur.produit_scalaire(a, b)`** — Cette méthode refait le produit scalaire à la main, comme un employé de bureau qui pointe chaque opération sur sa feuille : elle reçoit deux vecteurs de même longueur, multiplie leurs premières coordonnées en comptant une multiplication, puis, pour chacune des coordonnées suivantes, ajoute le produit au total en comptant une multiplication et une addition. Elle renvoie la somme obtenue, et laisse dans `mult` et `add` la trace de n multiplications et n − 1 additions par appel ; sur les 13 morceaux comparables, en dimension 12, le compteur arrive à 156 multiplications et 143 additions, soit 299 opérations pour une seule question.

**`assembler_prompt(question, passages)`** — Voici le greffier qui prépare le dossier remis au juge : la fonction reçoit la question de l'utilisateur et la liste des passages retrouvés, chacun sous la forme d'un couple (source, texte), écrit une ligne « Contexte : », puis une ligne par passage précédée de sa source entre crochets, puis la question, et enfin la consigne de ne répondre qu'avec le contexte, de citer chaque source et de dire quand le contexte ne suffit pas. Elle renvoie ce texte unique, lignes jointes par des retours à la ligne ; `main` vérifie que les trois sources du top 3 y figurent entre crochets et qu'aucun autre crochet ne s'y est glissé.

**`recall_at_k(classement, pertinents, k)`** — Elle se pose la question d'un chercheur d'or qui tamise les k premières pelletées : quelle part des pépites connues a-t-il récupérée ? Elle reçoit le classement des identifiants, l'ensemble des pertinents et la profondeur k, lève `ValueError` si k est inférieur à 1, renvoie `None` quand il n'y a aucun pertinent, car le rapport n'aurait pas de dénominateur, et sinon renvoie le nombre de pertinents présents dans les k premiers, divisé par le nombre total de pertinents. Sur l'exemple docA à docD avec les pertinents docB et docE, elle donne 0,5 à k = 3, et la moyenne des quatre questions d'assurance vaut 0,8333.

**`precision_at_k(classement, pertinents, k)`** — Cette fonction regarde la même pelletée par l'autre bout : sur les k objets ramenés, combien sont vraiment de l'or ? Elle reçoit le classement, l'ensemble des pertinents et k, lève `ValueError` si k est inférieur à 1, puis renvoie le nombre de pertinents trouvés parmi les k premiers divisé par k lui-même, de sorte qu'un ensemble de pertinents vide donne simplement 0. Sur l'exemple docA à docD, elle donne 0,333 à k = 3, et la moyenne des quatre questions d'assurance vaut 0,6667.

**`rang_reciproque(classement, pertinents)`** — Elle note la patience demandée à un lecteur qui descend la liste jusqu'au premier résultat utile : elle reçoit le classement et l'ensemble des pertinents, renvoie `None` s'il n'existe aucun pertinent, parcourt ensuite la liste en numérotant les rangs à partir de 1 et renvoie 1 divisé par le rang du premier pertinent rencontré, ou 0,0 si aucun n'apparaît. Une réponse utile en tête vaut donc 1, en troisième position 0,3333, et c'est exactement ce que reçoit la quatrième question d'assurance.

**`moyenne(valeurs)`** — C'est un comptable qui refuse de compter les cases restées vides : la fonction reçoit une liste de nombres où certaines entrées valent `None`, écarte ces entrées, puis renvoie la moyenne arithmétique des valeurs restantes, ou `None` si plus rien ne reste. Le programme l'utilise pour les trois moyennes des quatre questions, 0,8333, 0,6667 et 0,8333, et pour le MRR 0,5667 des rangs 2, 1 et 5 au point 9 ; ignorer les `None` évite qu'une question sans pertinent ne fasse baisser la moyenne par un zéro inventé.

**`faithfulness(affirmations_soutenues, affirmations_total)`** — Elle joue le vérificateur de faits qui, après la réponse de l'agent, coche chaque affirmation trouvée dans le contexte : elle reçoit le nombre d'affirmations soutenues et le nombre total d'affirmations, renvoie `None` pour une réponse qui n'affirme rien, lève `ValueError` si le nombre soutenu est négatif ou dépasse le total, et renvoie sinon le rapport des deux. Trois affirmations soutenues sur quatre donnent 0,75, et une réponse sans affirmation donne `None`, ce que `main` vérifie au point 8.

**`main()`** — Le chef d'orchestre fait traverser au lecteur tout un RAG en neuf étapes : il recalcule les deux cosinus du cours, 0,985 et 0,983, et vérifie que le vecteur nul est refusé, puis découpe les cinq documents en 15 morceaux et prouve l'utilité du recouvrement, écarte les deux morceaux de vecteur nul pour n'en garder que 13, et interroge l'index avec quatre questions dont il compare le top 3 au jugement humain. Il montre ensuite que normaliser transforme le produit scalaire en cosinus, alors que le produit brut met la publicité en tête, compte les 299 opérations d'une recherche exhaustive, assemble le prompt cité, mesure la Faithfulness de 0,75 et rejoue l'exemple docA à docD. Chaque résultat est confronté par un `assert` à la valeur attendue, et la dernière ligne n'annonce le succès que si tous ont tenu.

```python
"""Étape 18 — un RAG de bout en bout en Python standard : découpage, vecteurs, cosinus top-k, prompt cité, métriques."""
import math
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- l'équivalent Python de la classe Java
def cosinus(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("dimensions différentes")
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        raise ValueError("vecteur nul : le cosinus n'est pas défini")
    return max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b)) / (na * nb)))


def normaliser(v: list[float]) -> list[float]:
    n = math.sqrt(sum(x * x for x in v))
    if n == 0.0:
        raise ValueError("impossible de normaliser le vecteur nul")
    return [x / n for x in v]


# ---------------------------------------------------------------- 1. découpage
def mots(texte: str) -> list[str]:
    """Minuscules, apostrophes remplacées par des espaces, puis suites de lettres, chiffres, § et tirets."""
    texte = texte.lower().replace("'", " ").replace("’", " ")
    return re.findall(r"[a-zàâçéèêëîïôûùüÿœ0-9§-]+", texte)


def decouper(texte: str, taille: int, recouvrement: int) -> list[list[str]]:
    """Fenêtres de `taille` mots ; chaque fenêtre reprend les `recouvrement` derniers mots de la précédente."""
    if not 0 <= recouvrement < taille:
        raise ValueError("il faut 0 <= recouvrement < taille")
    m = mots(texte)
    pas = taille - recouvrement
    morceaux = []
    for debut in range(0, len(m), pas):
        morceaux.append(m[debut:debut + taille])
        if debut + taille >= len(m):
            break
    return morceaux


def contient(morceau: list[str], phrase: list[str]) -> bool:
    n = len(phrase)
    return any(morceau[i:i + n] == phrase for i in range(len(morceau) - n + 1))


# ---------------------------------------------------------------- 2. vecteurs jouets
VOCABULAIRE = ["parking", "recul", "pare-chocs", "caméra", "franchise", "vol",
               "police", "plafond", "inondation", "pluies", "sinistre", "photos"]


def vectoriser(liste_mots: list[str]) -> list[float]:
    """Sac de mots : la coordonnée i compte les occurrences du i-ème mot du vocabulaire."""
    return [float(liste_mots.count(terme)) for terme in VOCABULAIRE]


# ---------------------------------------------------------------- 3. recherche exhaustive
def top_k(question: list[float], index: dict[str, list[float]], k: int) -> list[tuple[str, float]]:
    """Cosinus avec chaque morceau, tri décroissant (égalités départagées par l'identifiant), k premiers."""
    scores = [(ident, cosinus(question, v)) for ident, v in index.items()]
    scores.sort(key=lambda s: (-round(s[1], 12), s[0]))
    return scores[:k]


class Compteur:
    def __init__(self) -> None:
        self.mult = 0
        self.add = 0

    def produit_scalaire(self, a: list[float], b: list[float]) -> float:
        total = a[0] * b[0]
        self.mult += 1
        for x, y in zip(a[1:], b[1:]):
            total += x * y
            self.mult += 1
            self.add += 1
        return total


# ---------------------------------------------------------------- 4. prompt avec citations
def assembler_prompt(question: str, passages: list[tuple[str, str]]) -> str:
    lignes = ["Contexte :"]
    lignes += [f"[{source}] {texte}" for source, texte in passages]
    lignes += [f"Question : {question}",
               "Consigne : réponds seulement avec le contexte, cite chaque source entre crochets ; "
               "si le contexte ne suffit pas, dis-le."]
    return "\n".join(lignes)


# ---------------------------------------------------------------- 5. métriques (démontrées aux étapes 25 à 27 et 54)
def recall_at_k(classement: list[str], pertinents: set[str], k: int) -> float | None:
    if k < 1:
        raise ValueError("k >= 1")
    if not pertinents:
        return None
    return len(set(classement[:k]) & pertinents) / len(pertinents)


def precision_at_k(classement: list[str], pertinents: set[str], k: int) -> float:
    if k < 1:
        raise ValueError("k >= 1")
    return len(set(classement[:k]) & pertinents) / k


def rang_reciproque(classement: list[str], pertinents: set[str]) -> float | None:
    if not pertinents:
        return None
    for rang, ident in enumerate(classement, start=1):
        if ident in pertinents:
            return 1.0 / rang
    return 0.0


def moyenne(valeurs: list[float | None]) -> float | None:
    definies = [v for v in valeurs if v is not None]
    return sum(definies) / len(definies) if definies else None


def faithfulness(affirmations_soutenues: int, affirmations_total: int) -> float | None:
    if affirmations_total == 0:
        return None
    if not 0 <= affirmations_soutenues <= affirmations_total:
        raise ValueError("il faut 0 <= soutenues <= total")
    return affirmations_soutenues / affirmations_total


DOCUMENTS = {
    "contrat-auto §4": "Dommages en stationnement. Les dommages subis dans un parking pendant une manœuvre de recul "
                       "sont couverts après la franchise de 500 AED. Le pare-chocs et la caméra de recul font partie "
                       "des éléments couverts.",
    "contrat-auto §7": "Vol du véhicule. Le vol est couvert si une plainte est déposée auprès de la police dans les "
                       "24 heures. Le plafond est la valeur du véhicule fixée par l'expert.",
    "procedure-sinistre": "Pour déclarer un sinistre, l'assuré envoie le rapport de police, des photos des dommages "
                          "et une copie de son permis de conduire.",
    "option-meteo": "Les dégâts causés par une inondation ou de fortes pluies sont couverts seulement avec l'option "
                    "tous risques, et la franchise est alors doublée.",
    "partenaire-parking": "Parking partenaire : parking gratuit, parking surveillé, parking couvert près de la Marina.",
}


def main() -> None:
    print("1. Les deux exemples chiffrés du cours")
    c3 = cosinus([0.8, 0.3, 0.5], [0.7, 0.4, 0.6])
    c4 = cosinus([0.6, 0.2, 0.8, 0.1], [0.5, 0.3, 0.7, 0.2])
    print(f"  3D : 0.98 / ({math.sqrt(0.98):.3f} × {math.sqrt(1.01):.3f}) = {c3:.3f}   4D : 0.94 / ({math.sqrt(1.05):.3f} × {math.sqrt(0.87):.3f}) = {c4:.3f}")
    assert round(c3, 3) == 0.985 and round(c4, 3) == 0.983
    assert round(math.sqrt(0.98), 3) == 0.990 and round(math.sqrt(1.01), 3) == 1.005
    assert round(math.sqrt(1.05), 3) == 1.025 and round(math.sqrt(0.87), 3) == 0.933
    assert round(math.sqrt(0.98 * 1.01), 3) == 0.995 and round(math.sqrt(1.05 * 0.87), 3) == 0.956
    try:
        cosinus([0.0, 0.0], [1.0, 0.0])
    except ValueError:
        print("  vecteur nul → ValueError (la classe Java renvoyait 0.0)")
    else:
        raise AssertionError("le vecteur nul aurait dû être refusé")

    print("2. Découpage : 12 mots par morceau, 4 mots de recouvrement")
    index_textes: dict[str, list[str]] = {}
    for source, texte in DOCUMENTS.items():
        for i, morceau in enumerate(decouper(texte, 12, 4)):
            index_textes[f"{source} #{i}"] = morceau
    print(f"  {len(DOCUMENTS)} documents → {len(index_textes)} morceaux")
    assert len(index_textes) == 15
    regle = mots("une plainte est déposée auprès de la police dans les 24 heures")
    avec = any(contient(m, regle) for m in decouper(DOCUMENTS["contrat-auto §7"], 12, 4))
    sans = any(contient(m, regle) for m in decouper(DOCUMENTS["contrat-auto §7"], 12, 0))
    print(f"  règle « plainte … police … 24 heures » entière dans un morceau : avec recouvrement {avec}, sans {sans}")
    assert avec and not sans
    assert len(decouper(DOCUMENTS["contrat-auto §7"], 12, 0)) == 3
    assert sum(len(decouper(t, 12, 0)) for t in DOCUMENTS.values()) == 11

    print("3. Vecteurs : sac de mots sur 12 termes ; un morceau sans aucun terme n'est pas comparable")
    index: dict[str, list[float]] = {}
    for ident, morceau in index_textes.items():
        v = vectoriser(morceau)
        if any(v):
            index[ident] = v
        else:
            print(f"  écarté (vecteur nul) : {ident}")
    assert sorted(set(index_textes) - set(index)) == ["contrat-auto §7 #3", "procedure-sinistre #2"]

    print("4. Recherche : cosinus top-3 pour quatre questions, comparé à un jugement humain")
    questions = {
        "J'ai reculé dans un parking : pare-chocs enfoncé et caméra de recul cassée.":
            {"contrat-auto §4 #1", "contrat-auto §4 #2", "contrat-auto §4 #3"},
        "Vol de ma voiture cette nuit : dois-je aller à la police ?":
            {"contrat-auto §7 #0", "contrat-auto §7 #1"},
        "Inondation après de fortes pluies : quelle franchise ?":
            {"option-meteo #0", "option-meteo #2"},
        "Quels documents envoyer pour déclarer un sinistre de parking ?":
            {"procedure-sinistre #0", "procedure-sinistre #1", "procedure-sinistre #2"},
    }
    rappels, precisions, rrs = [], [], []
    for texte_q, pertinents in questions.items():
        q = vectoriser(mots(texte_q))
        classement = top_k(q, index, k=len(index))
        ids = [ident for ident, _ in classement]
        r, p, rr = recall_at_k(ids, pertinents, 3), precision_at_k(ids, pertinents, 3), rang_reciproque(ids, pertinents)
        rappels.append(r)
        precisions.append(p)
        rrs.append(rr)
        tete = ", ".join(f"{ident} {s:.4f}" for ident, s in classement[:3])
        print(f"  {texte_q[:24]}… → {tete}")
        print(f"      Recall@3 = {r:.4f}   Precision@3 = {p:.4f}   RR = {rr:.4f}")
    assert [round(x, 4) for x in rappels] == [1.0, 1.0, 1.0, 0.3333]
    assert [round(x, 4) for x in precisions] == [1.0, 0.6667, 0.6667, 0.3333]
    assert [round(x, 4) for x in rrs] == [1.0, 1.0, 1.0, 0.3333]
    print(f"  moyennes : Recall@3 = {moyenne(rappels):.4f}   Precision@3 = {moyenne(precisions):.4f}   MRR = {moyenne(rrs):.4f}")
    assert round(moyenne(rappels), 4) == 0.8333 and round(moyenne(precisions), 4) == 0.6667 and round(moyenne(rrs), 4) == 0.8333

    q1 = vectoriser(mots("J'ai reculé dans un parking : pare-chocs enfoncé et caméra de recul cassée."))
    scores_q1 = dict(top_k(q1, index, k=len(index)))
    assert round(scores_q1["contrat-auto §4 #3"], 4) == 0.7071 and round(scores_q1["contrat-auto §4 #1"], 4) == 0.5774
    assert scores_q1["partenaire-parking #0"] == 0.5

    print("5. Normaliser : produit scalaire = cosinus ; sans normaliser, la publicité gagne")
    q1_n = normaliser(q1)
    index_n = {ident: normaliser(v) for ident, v in index.items()}
    assert all(abs(sum(a * b for a, b in zip(q1_n, v)) - scores_q1[i]) < 1e-12 for i, v in index_n.items())
    brut = sorted(index, key=lambda i: (-sum(a * b for a, b in zip(q1, index[i])), i))
    print(f"  produit scalaire brut : 1er = {brut[0]} ({sum(a * b for a, b in zip(q1, index[brut[0]])):.0f})"
          f" ; cosinus : 1er = contrat-auto §4 #3 ({scores_q1['contrat-auto §4 #3']:.4f})")
    assert brut[0] == "partenaire-parking #0"
    par_q_brut = sorted(index_n, key=lambda i: (-round(sum(a * b for a, b in zip(q1, index_n[i])), 12), i))
    assert par_q_brut == [i for i, _ in top_k(q1, index, k=len(index))]   # ||q|| constant : même ordre

    print("6. Coût de la recherche exhaustive : N × d multiplications, N × (d − 1) additions")
    compteur = Compteur()
    for v in index_n.values():
        compteur.produit_scalaire(q1_n, v)
    n_morceaux, d = len(index_n), len(VOCABULAIRE)
    print(f"  N = {n_morceaux}, d = {d} : {compteur.mult} multiplications + {compteur.add} additions = {compteur.mult + compteur.add}")
    assert (compteur.mult, compteur.add) == (n_morceaux * d, n_morceaux * (d - 1)) == (156, 143)
    print(f"  à l'échelle : N = 1 000 000, d = 1024 → {1_000_000 * (2 * 1024 - 1):,} opérations par question")
    assert 1_000_000 * (2 * 1024 - 1) == 2_047_000_000

    print("7. Prompt assemblé pour la première question")
    meilleurs = top_k(q1, index, k=3)
    passages = [(ident, " ".join(index_textes[ident])) for ident, _ in meilleurs]
    prompt = assembler_prompt("Mon pare-chocs et ma caméra de recul sont-ils couverts ?", passages)
    print("\n".join("  " + ligne for ligne in prompt.split("\n")))
    assert all(f"[{ident}]" in prompt for ident, _ in meilleurs) and prompt.count("[") == 3

    print("8. Faithfulness de la réponse générée")
    f = faithfulness(3, 4)
    print(f"  3 affirmations soutenues par le contexte sur 4 → {f:.2f} ; réponse sans affirmation → {faithfulness(0, 0)}")
    assert f == 0.75 and faithfulness(0, 0) is None

    print("9. L'exemple du cours : docA à docD, pertinents docB et docE")
    ids = ["docA", "docB", "docC", "docD"]
    pert = {"docB", "docE"}
    mrr = moyenne([1 / 2, 1 / 1, 1 / 5])
    print(f"  Recall@3 = {recall_at_k(ids, pert, 3):.4f}   Precision@3 = {precision_at_k(ids, pert, 3):.4f}"
          f"   MRR des rangs (2, 1, 5) = {mrr:.4f}")
    assert recall_at_k(ids, pert, 3) == 0.5 and round(precision_at_k(ids, pert, 3), 3) == 0.333
    assert round(mrr, 4) == 0.5667 and recall_at_k(ids, set(), 3) is None
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Les deux exemples chiffrés du cours
  3D : 0.98 / (0.990 × 1.005) = 0.985   4D : 0.94 / (1.025 × 0.933) = 0.983
…
  règle « plainte … police … 24 heures » entière dans un morceau : avec recouvrement True, sans False
…
  J'ai reculé dans un park… → contrat-auto §4 #3 0.7071, contrat-auto §4 #1 0.5774, contrat-auto §4 #2 0.5774
…
  Quels documents envoyer … → contrat-auto §4 #0 0.7071, partenaire-parking #0 0.7071, procedure-sinistre #0 0.5000
      Recall@3 = 0.3333   Precision@3 = 0.3333   RR = 0.3333
  moyennes : Recall@3 = 0.8333   Precision@3 = 0.6667   MRR = 0.8333
…
  produit scalaire brut : 1er = partenaire-parking #0 (4) ; cosinus : 1er = contrat-auto §4 #3 (0.7071)
…
  N = 13, d = 12 : 156 multiplications + 143 additions = 299
…
  [contrat-auto §4 #3] et la caméra de recul font partie des éléments couverts
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un RAG n'est pas une boîte noire. C'est un découpage, un vecteur par morceau, un produit scalaire par morceau, un tri, puis un prompt qui cite ses sources ; et sa qualité se mesure hors ligne, question par question, avant de faire confiance à l'agent.

## Squelette algorithmique

Le programme de ce fichier construit un RAG complet en miniature, de l'ingestion des documents à l'évaluation de la réponse. Les deux algorithmes détaillés plus haut (recherche naïve et recherche hybride) y deviennent un pipeline en deux phases : l'indexation, faite une fois, et la requête, faite à chaque question.

```text
ALGORITHME IndexerUnCorpus
ENTRÉES : documents (identifiant, texte), taille t des morceaux, recouvrement r (0 ≤ r < t)
SORTIE  : index (identifiant du morceau → vecteur normalisé)

  POUR CHAQUE document FAIRE
      mots ← découper le texte en mots
      POUR début DE 0 À longueur(mots) PAR PAS DE (t − r) FAIRE
          morceau ← mots[début … début + t − 1]          (chaque morceau reprend les r derniers mots du précédent)
          index[document#n] ← Normaliser(Vectoriser(morceau))
          SI début + t ≥ longueur(mots) ALORS sortir
      FIN POUR
  FIN POUR
  RETOURNER index

ALGORITHME RépondreEtÉvaluer
ENTRÉES : question, index, k, pertinents (pour l'évaluation)
SORTIE  : prompt assemblé, Recall@k, Precision@k, rang réciproque

  q ← Normaliser(Vectoriser(question))
  POUR CHAQUE morceau m de l'index FAIRE  score(m) ← cos(q, m)  FIN POUR
  top ← les k morceaux de plus grand score (égalités départagées par l'identifiant)
  prompt ← « Contexte : » + top avec leurs sources + « Question : » + question + consigne de citation
  Recall@k ← |pertinents ∩ top| / |pertinents|      Precision@k ← |pertinents ∩ top| / k
  RR ← 1 / rang du premier pertinent dans top (0 s'il n'y en a pas)
  APRÈS LA RÉPONSE : Faithfulness ← affirmations soutenues / affirmations (indéfinie si aucune)
  RETOURNER prompt, Recall@k, Precision@k, RR
```

**Complexité.** L'indexation coûte O(L) pour découper un texte de L mots, plus le coût de vectorisation de chaque morceau ; avec un recouvrement r, il y a environ L / (t − r) morceaux, donc un recouvrement plus grand multiplie les morceaux à stocker. La requête coûte O(N × n) pour comparer la question aux N morceaux de dimension n (démonstration, point 2), puis O(N log N) pour le tri ; les métriques coûtent O(k). Au-delà de quelques centaines de milliers de morceaux, un index approximatif remplace la boucle exhaustive.

**Du squelette au code.** `IndexerUnCorpus` correspond à `decouper` (avec sa garde 0 ≤ recouvrement < taille), `mots`, `vectoriser` et `normaliser`. `RépondreEtÉvaluer` correspond à `top_k` (avec `cosinus`), `assembler_prompt`, puis `recall_at_k`, `precision_at_k`, `rang_reciproque` et `moyenne` pour les métriques, et `faithfulness` pour la fidélité, qui renvoie `None` quand la réponse ne contient aucune affirmation.

## Cas d'usage réels aux Émirats

Les seuils, les tailles de corpus et les volumes ci-dessous sont illustratifs : en production, on les mesure sur ses propres documents et avec son propre modèle d'embedding.

### Assurance — le sinistre de parking, de la question à la réponse citée

Un assureur auto et santé de Dubaï reçoit chaque jour des déclarations de sinistre écrites en quelques phrases, en anglais ou en arabe, comme celle de l'introduction : un choc en marche arrière dans un parking souterrain, un pare-chocs enfoncé, une caméra de recul hors service. L'agent découpe et vectorise à l'avance les conditions générales, les procédures de déclaration et les options, puis, pour chaque déclaration, récupère les trois passages les plus proches : dans le mini-corpus du code, la clause « caméra de recul … couverts » arrive en tête avec 0,7071, devant deux autres morceaux de la même clause. Il assemble un prompt qui cite chaque passage par sa source, et ne propose une indemnisation automatique que si le meilleur passage dépasse un seuil calibré pour son modèle (par exemple 0,85, étape 19) et si la Faithfulness de la réponse générée dépasse 0,9 ; sinon, il demande des précisions ou passe la main à un gestionnaire. Sans normalisation des vecteurs, un passage publicitaire qui répète « parking » quatre fois passerait devant la clause, exactement comme le produit scalaire brut du bloc 5. La contrainte est que la décision de couverture reste dans les règles du domaine (franchise, plafond, exclusions), jamais dans le texte généré : le RAG apporte la clause, le code métier calcule. L'indicateur suivi est la part des déclarations traitées automatiquement que le gestionnaire ne corrige pas, à côté de la Faithfulness moyenne des réponses.

### RH — l'onboarding multi-émirats et les synonymes

Un cabinet RH présent dans plusieurs émirats indexe ses procédures internes : enregistrement du contrat auprès du MOHRE, versement des salaires par le WPS, demande d'Emirates ID, objectifs d'Émiratisation. Un recruteur demande « annual leave for a new hire in Abu Dhabi? » alors que la procédure est rédigée en français sous le titre « congés annuels » : un sac de mots ne trouverait rien, faute de mot commun, alors qu'un modèle d'embedding multilingue donne aux deux formulations des vecteurs proches. C'est la limite que montre la quatrième question du code : « documents » et « envoyer » ne sont pas dans le vocabulaire, si bien que deux morceaux sur le parking passent devant la procédure de déclaration (rang réciproque 0,3333), et que le morceau « une copie de son permis de conduire », sans aucun terme connu, est même écarté. Le cabinet mesure donc Recall@5 et MRR sur un jeu d'une centaine de questions réelles de recruteurs, réparties par émirat et par langue, avant chaque changement de modèle ou de découpage. Sans cette mesure, une baisse de qualité sur les questions en anglais passerait inaperçue jusqu'à la première erreur de procédure. La contrainte est la traçabilité : chaque réponse cite la procédure et sa version, pour qu'un auditeur puisse vérifier la règle appliquée. L'indicateur suivi est le MRR par langue, avec une alerte s'il baisse d'une version à l'autre.

### BTP — la facture conforme et ce que dit vraiment un Recall@5

Un groupe de construction de Dubaï fait répondre ses équipes de chantier par un agent qui cherche dans les guides internes de facturation : TVA de 5 %, mentions obligatoires d'une facture fiscale, retenues de garantie, factures de sous-traitants. Un conducteur de travaux demande comment émettre une facture de situation pour un lot de gros œuvre, et l'agent présente au LLM les cinq passages les plus proches. L'ancienne version disait qu'un bon Recall@5 « garantit » que le bon modèle de facture est parmi les cinq premiers : un Recall@5 de 1 sur cette requête dit seulement que, pour cette question-là, tous les passages jugés pertinents étaient dans les cinq premiers ; la moyenne sur un jeu de questions dit ce qu'on peut attendre en général, sans rien garantir pour la question suivante. Pour les termes exacts (« retenue de garantie », numéro d'enregistrement à la TVA, intitulés de postes), l'équipe ajoute BM25 et combine les deux scores normalisés (algorithme 2, étape 23), parce qu'un modèle d'embedding confond facilement deux numéros ou deux montants proches. Sans cette double recherche, l'agent citerait un modèle de facture voisin mais faux, et la facture serait rejetée par le client ou lors d'un contrôle fiscal. L'indicateur suivi est le Recall@5 moyen sur un jeu de questions mis à jour chaque trimestre, à côté du taux de factures rejetées.

### Secteur public — filtrer les droits avant de calculer la similarité

Une entité de services publics en ligne, accessible par UAE Pass, indexe à la fois des fiches publiques et des notes internes réservées à ses agents. La similarité seule ne suffit pas : l'agent filtre d'abord les morceaux que le profil de l'utilisateur a le droit de voir, puis calcule le cosinus sur ce seul sous-ensemble, si bien qu'une note interne ne peut jamais apparaître dans une réponse à un usager, même si elle est la plus proche de la question. Filtrer après coup serait plus fragile, car il suffirait d'un oubli dans le code d'assemblage du prompt pour que la note fuie. Ce filtrage réduit aussi N, donc le coût N × (2n − 1) de la recherche exhaustive (démonstration, point 2). Les fiches sont rédigées en arabe et en anglais : l'équipe normalise l'arabe (alef, ta marbuta, diacritiques) avant l'indexation et mesure Recall@k séparément dans chaque langue. L'indicateur suivi est double : le nombre de passages hors droits présentés, avec un objectif de zéro vérifié par des tests automatiques, et le MRR sur les questions des usagers.

### Banque — les règles de crédit et le ratio d'endettement

Une banque de détail de Dubaï donne à ses conseillers un agent qui cherche dans sa politique de crédit interne et dans les règles de la CBUAE applicables aux particuliers. Un conseiller demande si un client qui rembourse déjà une carte et un prêt auto peut obtenir un prêt personnel : le RAG doit ramener le passage sur le ratio d'endettement, qui compte toutes les mensualités, y compris la nouvelle, et le plafonne à 50 % du revenu (30 % pour un retraité). L'agent cite ce passage, mais le calcul du ratio se fait dans un outil déterministe, jamais dans le texte généré. Si le retriever ramenait seulement la règle du prêt personnel limité à 20 fois le salaire et à 48 mois, la réponse serait vraie mais incomplète : c'est ce que le Recall@k mesure, et l'équipe vérifie que les deux règles sont récupérées quand la question touche les deux. La politique interne change régulièrement, si bien que chaque passage indexé porte sa date de version et que l'ancienne version est retirée de l'index le jour où la nouvelle entre en vigueur. L'indicateur suivi est la Faithfulness des réponses relues par la conformité sur un échantillon hebdomadaire.

### Immobilier — frais de transfert et fiches de quartier trop bavardes

Une agence immobilière de Dubaï et d'Abu Dhabi indexe ses modèles de contrats de location enregistrés auprès d'Ejari, ses procédures de transfert de propriété auprès du DLD et ses fiches de quartiers. Un client demande ce qu'il paiera en plus du prix pour un appartement de 1,5 million d'AED : le RAG doit ramener le passage sur les frais de transfert du DLD, 4 % de la valeur du bien, soit 60 000 AED, et l'agent le cite. Les fiches de quartiers sont longues et répètent des mots comme « appartement » ou « Marina » ; avec un produit scalaire non normalisé, elles écraseraient les passages courts et précis, comme la publicité du mini-corpus écrase la clause, alors que le cosinus sur des vecteurs normalisés ne regarde que la direction (démonstration, point 1). Le découpage avec recouvrement évite qu'une règle de frais soit coupée entre deux morceaux, comme la règle « plainte … police … 24 heures » du bloc 2. Sans ces précautions, l'agent répondrait avec un montant faux ou sans source, ce qui est inacceptable pour une décision d'achat. L'indicateur suivi est le taux de réponses chiffrées dont la source citée contient bien le chiffre donné.

## Pièges et limites

- **Croire que la fonction de similarité est le levier principal.** Sur des vecteurs normalisés, cosinus, produit scalaire et distance classent de la même façon ; les vrais leviers sont le modèle d'embedding, le découpage et le reranking.
- **Découper sans recouvrement.** Une règle coupée entre deux morceaux n'est entière nulle part (bloc 2) ; un recouvrement de 10 à 20 % de la taille est un point de départ courant, à mesurer.
- **Oublier qu'un sac de mots ne connaît pas les synonymes.** « Reculé » n'est pas « recul », « documents » n'est pas « rapport » : la quatrième question échoue en partie, et un morceau sans terme connu a un vecteur nul.
- **Juger un retriever sur une seule question.** Un Recall@5 de 1 sur une requête n'est pas une garantie : on mesure sur un jeu de questions étiquetées, par langue et par type de demande.
- **Comparer des scores d'un modèle à l'autre.** Un seuil de 0,85 n'a de sens que pour le modèle sur lequel il a été calibré (étape 19).

### Exercice feuille blanche

1. Sans regarder le code, réécrire `cosinus` à partir de la classe Java, avec `ValueError` au lieu de `0.0` pour un vecteur nul, puis vérifier le 0,985 de l'exemple en 3D.
2. Prédire, puis vérifier : avec `decouper(texte, 12, 0)`, combien de morceaux donne la clause §7, et la règle « plainte … police … 24 heures » tient-elle entière dans l'un d'eux ? (Réponse : 3 morceaux au lieu de 4, et non : elle est coupée après « déposée ».)
3. Trouver le bug : `return len(set(classement[:k]) & pertinents) / len(pertinents)` dans `precision_at_k`. Que renvoie-t-elle pour la question sur le vol ? (Réponse : 1 au lieu de 0,6667 ; c'est le Recall@3, pas la Precision@3, parce que le dénominateur doit être k.)

## Pour aller plus loin

La similarité cosinus est le cœur mathématique du RAG pratique : maîtriser sa formule, ses propriétés (invariance à la norme, équivalence avec la distance pour des vecteurs normalisés) et les métriques d'évaluation (Recall@k, MRR, Faithfulness) permet de diagnostiquer rapidement pourquoi un agent « ne trouve pas » la bonne information. Les suites naturelles sont le calibrage des seuils (étape 19), la distance euclidienne et la distance cosinus (étapes 20 et 21), BM25 et la recherche hybride (étapes 22 à 24), les métriques démontrées (étapes 25 à 28), puis les métriques RAGAS du dossier Évaluation (étapes 53 et suivantes). Côté découpage, on peut couper par phrases ou par titres plutôt qu'à taille fixe, et garder dans chaque morceau le titre de la section dont il vient.

> Suite : [Similarité cosinus, seuils et calibrage](<19-RAG-Formule-Similarite-Cosinus.md>) — étape 19.
