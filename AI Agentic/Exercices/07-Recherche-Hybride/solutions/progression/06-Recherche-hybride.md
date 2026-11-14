# Étape 6 — La recherche hybride

> Palier 07 · Étape 6 sur 8 · Précédent : [Étape 5 — Classement et RRF](<05-Classement-et-RRF.md>) · Suivant : [Étape 7 — L'outil et les citations](<07-Outil-et-citations.md>) · Retour à l'énoncé : [README du palier 07](<../../README.md>)

## Comment raisonner

Toutes les pièces existent : `indexer`, `tokeniser`, `plonger`, `bm25_score`, `classement`, `rrf`, et `cosinus` au palier 06. `rechercher_hybride` ne calcule rien de nouveau ; elle **orchestre**. Pour l'écrire sans se tromper, on énumère ce qu'elle doit produire, puis on remonte :

1. la sortie : un dictionnaire avec les scores BM25, les scores cosinus et les k premiers de la fusion, pour que l'appelant (l'outil, la démo, les tests) puisse tout inspecter ;
2. la fusion a besoin de deux classements, donc de deux dictionnaires de scores ;
3. chaque dictionnaire a besoin de la question sous deux formes (mots et vecteur) et de chaque document sous deux formes ;
4. et avant tout cela, les cas impossibles : `k < 1`, un corpus vide.

Une question de déterminisme se pose aussi : dans quel ordre parcourir les documents ? On trie les identifiants, pour que deux corpus identiques écrits dans un ordre différent donnent exactement le même résultat.

## Le cosinus, rappel du palier 06

On ne le récrit pas, on l'importe. Voici ce qu'il fait, tel qu'il est dans `agent/memoire.py` :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cosinus(a, b)`** — C'est la fonction du palier 06, le navigateur qui compare deux caps sans tenir compte de la longueur des trajets : elle reçoit deux vecteurs, lève `ValueError` si leurs dimensions diffèrent ou si l'un d'eux est nul, puis renvoie le produit scalaire divisé par le produit des normes, borné à [−1, 1]. Ce palier l'importe sans la réécrire ; ce qui compte ici, c'est qu'elle refuse le vecteur nul, si bien que la recherche devra l'épargner aux documents sans concept mais laisser l'erreur sortir pour une question sans concept, comme « bonjour madame ».

```python
# [extrait] agent/memoire.py
def cosinus(a: list[float], b: list[float]) -> float:
    """cos(a, b) = a · b / (‖a‖ ‖b‖), borné à [−1, 1] ; un vecteur nul lève `ValueError` (pas d'epsilon).

    Exemple : `cosinus([1, 1, 2, 1, 0, 1, 0, 0], [0, 1, 1, 0, 0, 0, 0, 0])` = 3 / (√8 × √2) = 3 / 4 = 0.75.
    """
    if len(a) != len(b):
        raise ValueError("dimensions différentes")
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        raise ValueError("vecteur nul : le cosinus n'est pas défini")
    return max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b)) / (na * nb)))
```

Le point qui compte pour ce palier : un vecteur nul lève `ValueError`. La recherche devra donc éviter d'appeler `cosinus` sur un **document** sans concept (ce n'est pas une erreur, juste un document hors sujet), mais laisser l'erreur sortir pour une **question** sans concept (là, on ne sait pas chercher par le sens, et le dire vaut mieux que rendre un résultat arbitraire). `min_max`, l'autre fonction du palier 06 que l'étape 77 rangeait à côté, ne sert pas ici : RRF fusionne des rangs et n'a rien à normaliser.

## La fonction

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`rechercher_hybride(question, k, k_rrf, corpus)`** — Cette fonction est la bibliothécaire en chef qui ne calcule rien elle-même mais fait travailler deux experts, l'un attaché aux mots, l'autre au sens, puis confronte leurs palmarès : elle reçoit la question, le nombre k de documents à rendre, 3 par défaut, la constante `k_rrf`, 60 par défaut, et le corpus, lève `ValueError` si k est inférieur à 1 ou si l'index est vide, puis tokenise et plonge la question une fois et parcourt les identifiants triés. Elle calcule le score BM25 de chaque document, le cosinus des seuls documents au vecteur non nul, et renvoie un dictionnaire aux clés `bm25`, `cos` et `fusion`, cette dernière gardant les k premiers couples de `rrf` appliqué aux deux classements ; la requête de référence donne REG-1 à 0,032522, REG-2 à 0,032266 et FORUM-9 à 0,032002.

```python
# [extrait] agent/recherche.py
def rechercher_hybride(question: str, k: int = 3, k_rrf: int = 60, corpus: dict[str, str] | None = None) -> dict:
    """Rend {"bm25": scores, "cos": scores, "fusion": k premiers (id, score RRF)} ; `corpus` par défaut : CORPUS.

    Le cosinus n'est calculé que pour les documents de vecteur non nul ; une question sans aucun
    concept connu lève `ValueError` (vecteur nul) au lieu de masquer le problème.
    Exemple : « plafond d'endettement d'un retraité et durée maximale d'un prêt personnel » donne la
    fusion [("REG-1", 0.032522), ("REG-2", 0.032266), ("FORUM-9", 0.032002)].
    """
    if k < 1:
        raise ValueError("k doit valoir au moins 1")
    index = indexer(corpus)
    if not index:
        raise ValueError("corpus vide")
    q, ids = tokeniser(question), sorted(index)
    textes = [index[d] for d in ids]
    vq = plonger(q)
    s_bm25 = {d: bm25_score(q, index[d], textes) for d in ids}
    s_cos = {d: cosinus(vq, plonger(index[d])) for d in ids if any(plonger(index[d]))}
    return {"bm25": s_bm25, "cos": s_cos, "fusion": rrf([classement(s_bm25), classement(s_cos)], k_rrf)[:k]}
```

Groupe par groupe :

- **Les gardes.** `k < 1` : demander zéro document n'a pas de sens, et `[:0]` rendrait une liste vide sans rien signaler. `indexer(corpus)` transmet `None` tel quel, ce qui choisit `CORPUS` ; un corpus `{}` donne un index vide, refusé par `if not index`.
- **`q, ids = tokeniser(question), sorted(index)`** : une affectation multiple, qui construit puis déballe un tuple. `sorted(index)` trie les **clés** du dictionnaire : `["FORUM-9", "REG-1", …, "REG-6"]`, car « F » vient avant « R ».
- **`textes`** est le corpus sous la forme qu'attend `bm25_score` : une liste de listes de mots. L'ordre n'a pas d'importance pour BM25 (une somme et un comptage), mais on garde celui des identifiants.
- **`vq = plonger(q)`** : le vecteur de la question, calculé une fois. Il n'est pas testé ici : s'il est nul, c'est `cosinus` qui lèvera l'erreur au premier document, avec son propre message.
- **`s_bm25`** : une compréhension de dictionnaire, un score BM25 par document, y compris les scores nuls ; c'est `classement` qui les écartera.
- **`s_cos`** : la clause `if any(plonger(index[d]))` saute les documents dont le vecteur est nul. `any` sur une liste de flottants est vrai dès qu'une composante est non nulle, comme `stream().anyMatch(x -> x != 0)`. Dans le corpus fourni, les 7 documents ont au moins un concept ; la garde protège les corpus personnalisés.
- **Le retour.** Les deux classements sont fusionnés par `rrf`, et `[:k]` garde les k premiers. On rend aussi les deux dictionnaires bruts : ils servent à la démo, aux tests et au débogage.

**Exemple fait à la main, le cosinus de REG-1.** Ses mots donnent v = [2, 3, 1, 0, 0, 0, 0, 0] (dette : `endettement`, `mensualites` ; revenu : `salaire`, `revenu`, `retraite` ; crédit : `credit`). Avec vq = [1, 1, 1, 1, 0, 0, 0, 0] :

$$
\cos = \frac{1 \times 2 + 1 \times 3 + 1 \times 1}{\sqrt{4} \times \sqrt{14}} = \frac{6}{2 \times 3{,}7417} = 0{,}8018
$$

Le dictionnaire `cos` complet vaut, arrondi : FORUM-9 0,7071, REG-1 0,8018, REG-2 0,6708, REG-3 0,0, REG-4 0,5330, REG-5 0,0, REG-6 0,0. REG-3, REG-5 et REG-6 ont un vecteur non nul (taxe, change, immobilier) mais orthogonal à celui de la question : ils sont dans le dictionnaire, avec 0,0, et `classement` les écarte. Les deux classements valent `["REG-2", "REG-1", "FORUM-9", "REG-4"]` et `["REG-1", "FORUM-9", "REG-2", "REG-4"]`, et la fusion rend `[("REG-1", 0.032522), ("REG-2", 0.032266), ("FORUM-9", 0.032002)]`.

- **Analogie Java :** un service de façade (`@Service`) qui appelle des composants sans logique propre ; tout le calcul est délégué.
- **Piège classique :** filtrer avec `if any(vq)` au lieu de laisser `cosinus` lever l'erreur. On rendrait alors une fusion fondée sur BM25 seul, sans prévenir que le signal sémantique a disparu : exactement le genre d'epsilon qui masque un problème. Le test `rechercher_hybride("bonjour madame")` exige la `ValueError`.
- **Piège classique bis :** plonger les textes bruts du corpus au lieu de leurs mots indexés. `plonger` attend une liste de mots ; lui passer une chaîne ferait parcourir ses **caractères**, et aucun caractère seul n'est dans un concept : tous les vecteurs seraient nuls.

**Pourquoi RRF ne dépend que des rangs.** Le test `test_rrf_ne_depend_que_des_rangs` remplace les scores BM25 par ln(1 + x) et les cosinus par x³, deux fonctions strictement croissantes qui envoient 0 sur 0 : les classements, donc la fusion, sont identiques. Avec le score hybride de l'étape 23, la même transformation changerait les valeurs normalisées et pourrait changer l'ordre.

**Tests qui passent maintenant :**

```powershell
python -m unittest -v tests.test_07_recherche.TestBM25 tests.test_07_recherche.TestFusion
```

Sept tests verts : les trois de `TestBM25`, dont les quatre scores du scénario (5,0951 ; 3,1771 ; 1,9524 ; 0,6775), et les quatre de `TestFusion`, dont la fusion à 12 décimales, l'invariance par transformation croissante et les trois `ValueError` (`k_rrf=-1`, `k=0`, question sans concept).
