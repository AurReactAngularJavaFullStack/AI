# Étape 55 — Évaluation — Answer Relevancy

> Étape 55 du parcours · Prérequis : [Faithfulness](<54-Evaluation-Formule-Faithfulness.md>) · Suite : [Precision, Recall et F1 en évaluation](<56-Evaluation-Formule-Precision-Recall-F1.md>)

**Dossier :** 10-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Product Engineers  

**Nom du fichier :** 55-Evaluation-Formule-Answer-Relevancy.md

## Définition

Answer Relevancy (pertinence de la réponse) mesure si la réponse générée répond vraiment à la question posée, et non à une question voisine ou hors sujet. L'idée est indirecte : on demande à un LLM de reconstruire, à partir de la réponse seule, n questions auxquelles elle pourrait répondre ; si la réponse est dans le sujet, ces questions ressemblent à la question d'origine. On encode toutes les questions avec le même modèle d'embedding, puis on fait la moyenne des similarités cosinus entre chaque question reconstruite et la question d'origine. Le score ne juge ni la vérité ni la fidélité aux documents (c'est le rôle de l'étape 54) : une réponse fausse mais dans le sujet peut obtenir un score élevé. Une réponse évasive (« je ne peux pas répondre, contactez votre conseiller ») reçoit 0 dans RAGAS, quelle que soit la similarité calculée.

## Rôle dans un agent

Answer Relevancy juge la fin de l'étape **agir** de la boucle percevoir → décider → agir → observer : la réponse est-elle à la hauteur de la question **perçue** au début du tour ? Elle sert hors ligne, sur le jeu de référence, pour repérer les versions de prompt qui font dériver l'agent vers un sujet voisin ; en ligne, sur un échantillon de conversations, pour détecter les dérapages (une question sur les congés à laquelle l'agent répond par la paie). Elle complète la Faithfulness dans le tableau de diagnostic de l'étape 53 : une réponse fidèle aux documents mais peu pertinente signale un problème de compréhension de la question ou de retrieval hors sujet, pas une hallucination. Elle coûte un appel au LLM pour reconstruire les questions et n + 1 calculs d'embedding.

## Équation complète

$$
\text{Answer Relevancy} = \frac{1}{n} \sum_{i=1}^{n} \cos(E_{g_i}, E_o) = \frac{1}{n} \sum_{i=1}^{n} \frac{E_{g_i} \cdot E_o}{\lVert E_{g_i}\rVert \, \lVert E_o\rVert}
$$

Avec les vecteurs normalisés, la même quantité s'écrit comme un produit scalaire avec un centroïde :

$$
\hat e = \frac{E}{\lVert E \rVert}, \qquad \bar c = \frac{1}{n}\sum_{i=1}^{n} \hat e_{g_i}, \qquad \text{Answer Relevancy} = \hat e_o \cdot \bar c \le \lVert \bar c \rVert \le 1
$$

Convention de RAGAS pour une réponse évasive, et convention du parcours pour une entrée vide :

$$
\text{AR} = 0 \text{ si la réponse est jugée évasive}, \qquad \text{AR indéfinie si } n = 0
$$

## Décryptage des symboles

$$
n
$$

**Sens :** nombre de questions reconstruites à partir de la réponse (souvent 3 à 5) ; plus n est grand, plus l'estimation est stable, mais plus le coût augmente · **Type / plage :** entier ≥ 1 · **Variable Python :** `len(generees)`.

$$
E_{g_i}
$$

**Sens :** embedding de la i-ème question reconstruite à partir de la réponse · **Type / plage :** vecteur réel non nul, de la même dimension que Eₒ · **Variable Python :** les éléments de `generees`.

$$
E_o
$$

**Sens :** embedding de la question d'origine de l'utilisateur, calculé par le même modèle · **Type / plage :** vecteur réel non nul · **Variable Python :** `e_o`.

$$
\cos(E_{g_i}, E_o)
$$

**Sens :** similarité cosinus des deux embeddings ; proche de 1 quand les deux questions ont le même sens · **Type / plage :** réel dans [−1, 1] · **Variable Python :** `cosinus(g, e_o)`, la fonction canonique du parcours.

$$
\hat e_o,\; \bar c
$$

**Sens :** question d'origine normalisée, et centroïde des questions reconstruites normalisées · **Type / plage :** vecteur unitaire, et vecteur de norme au plus 1 · **Variable Python :** `normaliser(e_o)`, `centroide(generees)`.

$$
\tau
$$

**Sens :** seuil de décision, « en dessous, la réponse est jugée hors sujet » ; 0,7 est une valeur de départ, à calibrer pour chaque modèle d'embedding · **Type / plage :** réel dans ]0, 1[ · **Variable Python :** `tau`, renvoyé par `calibrer_seuil`.

## Démonstration

### 1. Le score est entre −1 et 1

Chaque terme de la moyenne est un cosinus. L'inégalité de Cauchy-Schwarz, démontrée à l'étape 14, dit que |E_gᵢ · Eₒ| ≤ ‖E_gᵢ‖ ‖Eₒ‖, donc chaque cosinus est entre −1 et 1. Une moyenne de nombres compris entre −1 et 1 reste entre −1 et 1, parce que

$$
-1 = \frac{1}{n}\sum_{i=1}^{n}(-1) \le \frac{1}{n}\sum_{i=1}^{n}\cos_i \le \frac{1}{n}\sum_{i=1}^{n} 1 = 1
$$

En pratique, les embeddings de textes donnent presque toujours des cosinus positifs, d'où un score observé entre 0 et 1 ; ce n'est pas une garantie mathématique. Le cosinus n'existe pas pour un vecteur nul : l'ancien code divisait par une norme sans la vérifier. La fonction canonique lève `ValueError`, sans epsilon qui masquerait l'erreur. Et le cosinus est invariant d'échelle (étape 14) : multiplier un embedding par un nombre positif ne change pas le score.

### 2. Le score est un produit scalaire avec un centroïde

Le cosinus de deux vecteurs est le produit scalaire de leurs versions normalisées. Le produit scalaire étant linéaire, on peut sortir la somme :

$$
\frac{1}{n}\sum_{i=1}^{n} \cos(E_{g_i}, E_o) = \frac{1}{n}\sum_{i=1}^{n} \hat e_{g_i}\cdot \hat e_o = \hat e_o \cdot \left(\frac{1}{n}\sum_{i=1}^{n} \hat e_{g_i}\right) = \hat e_o \cdot \bar c
$$

Deux conséquences. D'abord, par Cauchy-Schwarz, ê_o · c̄ ≤ ‖ê_o‖ ‖c̄‖ = ‖c̄‖. Ensuite, par l'inégalité triangulaire, ‖c̄‖ ≤ (1/n) ∑ ‖ê_gᵢ‖ = 1. Le score atteint 1 si et seulement si toutes les questions reconstruites ont exactement la direction de la question d'origine.

**Une réponse qui traite deux sujets est plafonnée.** Si la moitié des questions reconstruites porte sur un sujet et l'autre moitié sur un sujet orthogonal, par exemple (1 ; 0) et (0 ; 1), le centroïde vaut (0,5 ; 0,5) et sa norme 1/√2 = 0,7071. Quelle que soit la question d'origine, le score ne dépassera jamais 0,7071 ; avec Eₒ = (1 ; 0), il vaut 0,5. Une réponse qui mélange la franchise et le réseau de garages agréés perd des points même si chaque moitié est excellente.

### 3. Exemple fait à la main (le code reprend ces nombres)

L'ancienne version de ce fichier annonçait « ≈ 0,74 » sans calcul. Avec les vecteurs du chapitre (étape 53) : Eₒ = (0,9 ; 0,1), g₁ = (0,85 ; 0,15), g₂ = (0,7 ; 0,4), g₃ = (0,2 ; 0,8). Les normes valent 0,90554, 0,86313, 0,80623 et 0,82462.

$$
\cos_1 = \frac{0{,}78}{0{,}90554 \times 0{,}86313} = 0{,}998
\qquad
\cos_2 = \frac{0{,}67}{0{,}90554 \times 0{,}80623} = 0{,}918
\qquad
\cos_3 = \frac{0{,}26}{0{,}90554 \times 0{,}82462} = 0{,}348
$$

La moyenne vaut (0,998 + 0,918 + 0,348)/3 = 0,755. Par le centroïde : les questions normalisées sont (0,98478 ; 0,17378), (0,86824 ; 0,49614) et (0,24254 ; 0,97014), leur moyenne c̄ = (0,69852 ; 0,54669), et ê_o = (0,99388 ; 0,11043). Le produit scalaire vaut 0,69424 + 0,06037 = 0,75461 : le même nombre. La norme de c̄ vaut 0,8870 : le score ne pouvait pas dépasser cette valeur, parce que la troisième question est partie dans une autre direction.

### 4. Pourquoi une réponse évasive doit valoir 0

Question : « quel est le montant maximal d'un prêt personnel ? ». Réponse évasive : « je ne peux pas vous répondre, contactez votre conseiller pour votre prêt personnel ». La question reconstruite, « qui contacter pour un prêt personnel ? », parle du même produit que la question d'origine : avec des embeddings simplifiés (0,9 ; 0,3 ; 0,1) et (0,8 ; 0,4 ; 0,3), le cosinus vaut 0,87 / (0,95394 × 0,94340) = 0,967. La formule seule récompense donc une non-réponse. RAGAS corrige ce défaut en demandant aussi au LLM si la réponse est évasive (*noncommittal*) ; si c'est le cas, le score est mis à 0. Le programme reproduit cette convention avec le paramètre `evasive`.

### 5. Le seuil de 0,7 dépend du modèle d'embedding

Beaucoup de modèles d'embedding sont **anisotropes** : tous leurs vecteurs partagent une composante commune, et deux textes sans rapport ont quand même un cosinus élevé. On le démontre sur deux vecteurs unitaires orthogonaux a et b, auxquels on ajoute une même composante w, orthogonale aux deux et de norme t. Le produit scalaire vaut a·b + a·w + w·b + w·w = 0 + 0 + 0 + t², et par Pythagore ‖a + w‖² = ‖b + w‖² = 1 + t² :

$$
\cos(a + w,\; b + w) = \frac{t^2}{1 + t^2}
$$

Avec t = 2, deux textes sans rapport ont un cosinus de 4/5 = 0,8, au-dessus du seuil de 0,7. Le programme compare deux modèles sur les mêmes réponses : avec le modèle A (isotrope), les réponses pertinentes obtiennent 0,989 et 0,972, les réponses hors sujet 0,000 et 0,292, et 0,7 sépare bien les deux. Avec le modèle B (la même géométrie plus une composante commune t = 2), les réponses hors sujet obtiennent 0,799 et 0,857 : le seuil de 0,7 les laisse passer. On calibre donc τ pour chaque modèle, sur des réponses étiquetées pertinentes et hors sujet : ici, le milieu de l'écart donne 0,632 pour A et 0,926 pour B. Sur un vrai jeu, les deux nuages se chevauchent, et l'on choisit τ sur la courbe ROC de l'étape 51.

### 6. Les entrées vides

Si le LLM ne renvoie aucune question reconstruite, la moyenne n'a pas de dénominateur : le score est indéfini, `None`, et il n'entre pas dans les moyennes du jeu. L'ancien code renvoyait 0,0 dans ce cas, ce qui confondait une panne du générateur de questions avec une réponse hors sujet. Si un embedding est nul, la fonction lève `ValueError` : c'est un défaut en amont (texte vide, erreur du modèle d'embedding), pas une réponse à noter.

## Effets et comportement

- **Plus les questions reconstruites sont proches de la question d'origine**, plus le score augmente : la réponse est dans le sujet.
- **Si la réponse parle d'autre chose**, les questions reconstruites s'éloignent et le score baisse.
- **Si la réponse traite plusieurs sujets**, le centroïde raccourcit et plafonne le score, même si chaque partie est juste.
- **Un score sous le seuil** signale souvent une réponse hors sujet ou trop vague, mais le seuil n'a de sens que pour le modèle d'embedding sur lequel il a été calibré.

## Du symbole au code Python

| Symbole | Variable ou fonction Python |
|---|---|
| Eₒ, E_gᵢ | `e_o`, éléments de `generees` |
| cos(E_gᵢ, Eₒ) | `cosinus(g, e_o)` (code canonique) |
| ê = E / ‖E‖ | `normaliser(v)` |
| Answer Relevancy | `answer_relevancy(e_o, generees, evasive)` |
| c̄ | `centroide(generees)` |
| τ | `calibrer_seuil(pertinentes, hors_sujet)` |

### Déroulé, ligne par ligne

**`cosinus(a, b)`** est recopiée du code canonique du parcours. Elle refuse deux dimensions différentes, parce que `zip` tronquerait le vecteur le plus long en silence. Elle calcule les deux normes, lève `ValueError` si l'une est nulle, puis divise le produit scalaire par le produit des normes ; le `max(-1.0, min(1.0, …))` final absorbe un arrondi qui donnerait 1,0000000002 pour deux vecteurs identiques.

**`normaliser(v)`** divise chaque coordonnée par la norme ; un vecteur nul n'a pas de direction et lève `ValueError`.

**`answer_relevancy(e_o, generees, evasive)`**.

- `if not generees: return None` : aucune question reconstruite, le score n'existe pas.
- `if evasive: return 0.0` : la convention de RAGAS ; le drapeau vient du même appel au LLM qui reconstruit les questions.
- Sinon, la moyenne des cosinus. Sur l'exemple, `cosinus` renvoie 0,998, 0,9177 et 0,3482, et la moyenne vaut 0,7546.

**`centroide(generees)`** normalise chaque question, puis fait la moyenne coordonnée par coordonnée grâce à `zip(*unitaires)`, qui regroupe les premières coordonnées ensemble, puis les secondes. Sur l'exemple, il renvoie (0,6985 ; 0,5467).

**`calibrer_seuil(pertinentes, hors_sujet)`** prend le meilleur score hors sujet et le pire score pertinent. Si le premier est strictement inférieur au second, les deux nuages sont séparés et le milieu de l'écart est un seuil qui ne se trompe sur aucun exemple ; sinon, elle renvoie `None` pour dire qu'un seuil parfait n'existe pas, et qu'il faut choisir un compromis sur la courbe ROC.

**`main()`**, bloc par bloc.

1. Les trois cosinus et leur moyenne, comparés à 0,998, 0,918, 0,348 et 0,755.
2. Le centroïde : ê_o · c̄ redonne 0,7546 à 10⁻¹² près, et 0,7546 ≤ ‖c̄‖ = 0,8870 ≤ 1. Puis la réponse à deux sujets orthogonaux : score 0,5, plafond 0,7071. Enfin, multiplier Eₒ par 3 et chaque question par 5 ne change pas le score.
3. La réponse évasive : cosinus brut 0,9667, ramené à 0 par le drapeau.
4. Quatre réponses, trois questions reconstruites chacune, notées par le modèle A puis par le modèle B. La fonction `decale` ajoute 2 à la troisième coordonnée de chaque vecteur, question d'origine comprise : c'est la composante commune w de la démonstration. Les `assert` vérifient que 0,7 sépare les réponses avec A et ne les sépare plus avec B, que le seuil calibré sépare dans les deux cas, et que deux vecteurs orthogonaux décalés ont un cosinus de 0,8.
5. Les cas limites : aucune question, deux nuages qui se chevauchent, un vecteur nul.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`normaliser(v)`** — Cette fonction est le cartographe qui ne garde d'une flèche que sa direction, en effaçant sa longueur : elle reçoit un vecteur, calcule sa norme euclidienne, lève `ValueError` si cette norme est nulle, parce qu'un vecteur nul ne pointe nulle part, et sinon renvoie la liste des coordonnées divisées par la norme, un vecteur de longueur 1. Elle sert à `centroide`, qui ne doit moyenner que des directions, et à `main`, qui normalise la question d'origine pour vérifier que l'Answer Relevancy n'est rien d'autre que le produit scalaire de cette direction avec le centroïde.

**`answer_relevancy(e_o, generees, evasive)`** — Celle-ci est l'examinatrice qui fait deviner la question à partir de la seule réponse, puis mesure à quel point les devinettes ressemblent à l'original : elle reçoit le vecteur de la question d'origine, la liste des vecteurs des questions régénérées et un drapeau `evasive`, faux par défaut. Elle renvoie `None` s'il n'y a aucune question régénérée, 0 si le drapeau signale une réponse évasive, selon la convention de RAGAS, et sinon la moyenne des cosinus entre chaque question régénérée et l'originale : 0,7546 pour les cosinus 0,998, 0,9177 et 0,3482 de l'exemple, 0,5 pour une réponse à deux sujets orthogonaux, et 0 pour la réponse évasive dont le cosinus brut atteignait 0,9667.

**`centroide(generees)`** — Cette fonction cherche le centre de gravité d'un nuage de questions, comme on plante un drapeau au milieu d'un groupe de randonneurs dispersés : elle reçoit les vecteurs des questions régénérées, normalise chacun avec `normaliser`, puis regroupe les coordonnées de même rang grâce à `zip(*unitaires)` et renvoie la liste de leurs moyennes. Sur l'exemple, elle renvoie (0,6985 ; 0,5467), dont la norme 0,8870 est le plafond que l'Answer Relevancy ne peut pas dépasser ; pour les deux sujets orthogonaux, ce plafond tombe à 0,7071, soit 1/√2.

**`main()`** — C'est le chef d'orchestre des cinq démonstrations : il calcule les trois cosinus de l'exemple et leur moyenne 0,7546, vérifie avec `centroide` que ce score égale le produit scalaire de la question normalisée et du centroïde, et qu'il reste sous la norme 0,8870 de ce dernier, puis montre la réponse à deux sujets et l'invariance du score quand on multiplie les vecteurs par 3 et par 5. Il traite ensuite la réponse évasive, ramenée à 0, compare les modèles d'embedding A et B, où le seuil fixe 0,7 sépare les réponses avec A mais plus avec B, tandis que le seuil calibré, 0,632 puis 0,926, sépare dans les deux cas, et termine par les cas limites avant d'afficher « OK ».

```python
"""Étape 55 — Answer Relevancy : moyenne de cosinus, centroïde, réponse évasive, seuil à calibrer."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def cosinus(a: list[float], b: list[float]) -> float:
    """Code canonique du parcours : refuse les dimensions différentes et les vecteurs nuls."""
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
        raise ValueError("vecteur nul : pas de direction")
    return [x / n for x in v]


def answer_relevancy(e_o: list[float], generees: list[list[float]], evasive: bool = False) -> float | None:
    """(1/n) Σ cos(E_gi, E_o). None si aucune question régénérée ; 0 si la réponse est évasive (convention RAGAS)."""
    if not generees:
        return None
    if evasive:
        return 0.0
    return sum(cosinus(g, e_o) for g in generees) / len(generees)


def centroide(generees: list[list[float]]) -> list[float]:
    """c̄ = (1/n) Σ ê_gi, moyenne des questions normalisées."""
    unitaires = [normaliser(g) for g in generees]
    return [sum(col) / len(unitaires) for col in zip(*unitaires)]


def calibrer_seuil(pertinentes: list[float], hors_sujet: list[float]) -> float | None:
    """Milieu entre le pire score pertinent et le meilleur hors sujet ; None si les deux nuages se chevauchent."""
    if not pertinentes or not hors_sujet:
        return None
    bas, haut = max(hors_sujet), min(pertinentes)
    return (bas + haut) / 2 if bas < haut else None


def main() -> None:
    print("1. Trois questions régénérées, la question d'origine Eo = (0.9, 0.1)")
    e_o = [0.9, 0.1]
    generees = [[0.85, 0.15], [0.7, 0.4], [0.2, 0.8]]
    cos = [cosinus(g, e_o) for g in generees]
    ar = answer_relevancy(e_o, generees)
    print(f"  cosinus = {[round(c, 4) for c in cos]}   Answer Relevancy = {ar:.4f}")
    assert [round(c, 3) for c in cos] == [0.998, 0.918, 0.348] and round(ar, 3) == 0.755

    print("2. AR = ê_o · c̄, donc AR ≤ ‖c̄‖ ≤ 1")
    c = centroide(generees)
    produit = sum(x * y for x, y in zip(normaliser(e_o), c))
    norme_c = math.sqrt(sum(x * x for x in c))
    print(f"  c̄ = {[round(x, 4) for x in c]}   ê_o · c̄ = {produit:.4f}   ‖c̄‖ = {norme_c:.4f}")
    assert abs(produit - ar) < 1e-12 and ar <= norme_c <= 1
    deux_sujets = [[1.0, 0.0], [0.0, 1.0]]                     # la réponse traite deux sujets orthogonaux
    plafond = math.sqrt(sum(x * x for x in centroide(deux_sujets)))
    print(f"  réponse à deux sujets : AR = {answer_relevancy([1.0, 0.0], deux_sujets):.4f}   plafond ‖c̄‖ = {plafond:.4f}")
    assert answer_relevancy([1.0, 0.0], deux_sujets) == 0.5 and abs(plafond - 1 / math.sqrt(2)) < 1e-12
    assert abs(answer_relevancy([3 * x for x in e_o], [[5 * x for x in g] for g in generees]) - ar) < 1e-12

    print("3. Réponse évasive : la question régénérée ressemble à l'originale")
    question = [0.9, 0.3, 0.1]                                  # « plafond d'un prêt personnel ? »
    regeneree = [[0.8, 0.4, 0.3]]                               # « qui contacter pour un prêt personnel ? »
    brut = answer_relevancy(question, regeneree)
    print(f"  cosinus brut = {brut:.4f}   avec le drapeau « évasive » de RAGAS = {answer_relevancy(question, regeneree, evasive=True)}")
    assert brut > 0.9 and answer_relevancy(question, regeneree, evasive=True) == 0.0

    print("4. Le seuil 0.7 dépend du modèle d'embedding")
    q = [1.0, 0.0, 0.0]
    reponses = {"pertinente 1": [[1.0, 0.1, 0.0], [0.9, 0.2, 0.0], [1.0, -0.1, 0.0]],
                "pertinente 2": [[0.8, 0.3, 0.0], [1.0, 0.2, 0.0], [0.9, 0.0, 0.0]],
                "hors sujet 1": [[0.0, 1.0, 0.0], [0.1, 1.0, 0.0], [-0.1, 1.0, 0.0]],
                "hors sujet 2": [[0.3, 1.0, 0.0], [0.2, 0.9, 0.0], [0.4, 1.0, 0.0]]}
    decale = lambda v: [v[0], v[1], v[2] + 2.0]                # modèle B : une direction commune à tous les textes
    for nom_modele, f in (("A", lambda v: v), ("B", decale)):
        scores = {nom: answer_relevancy(f(q), [f(g) for g in gs]) for nom, gs in reponses.items()}
        pert = [s for nom, s in scores.items() if nom.startswith("pertinente")]
        hors = [s for nom, s in scores.items() if nom.startswith("hors")]
        tau = calibrer_seuil(pert, hors)
        print(f"  modèle {nom_modele} : " + "  ".join(f"{nom} = {s:.3f}" for nom, s in scores.items()))
        print(f"           0.7 sépare : {min(pert) >= 0.7 > max(hors)}   seuil calibré = {tau:.3f}")
        assert min(pert) > tau > max(hors)
        if nom_modele == "A":
            assert min(pert) >= 0.7 > max(hors)
        else:
            assert max(hors) >= 0.7                            # avec B, le seuil 0.7 laisse passer du hors sujet
    assert abs(cosinus(decale([1.0, 0.0, 0.0]), decale([0.0, 1.0, 0.0])) - 0.8) < 1e-12   # t²/(1 + t²) avec t = 2

    print("5. Cas limites")
    assert answer_relevancy(e_o, []) is None and calibrer_seuil([0.6], [0.7]) is None
    try:
        answer_relevancy(e_o, [[0.0, 0.0]])
    except ValueError:
        print("  aucune question → None ; vecteur nul → ValueError ; nuages qui se chevauchent → None")
    else:
        raise AssertionError("un vecteur nul aurait dû être refusé")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Trois questions régénérées, la question d'origine Eo = (0.9, 0.1)
  cosinus = [0.998, 0.9177, 0.3482]   Answer Relevancy = 0.7546
2. AR = ê_o · c̄, donc AR ≤ ‖c̄‖ ≤ 1
  c̄ = [0.6985, 0.5467]   ê_o · c̄ = 0.7546   ‖c̄‖ = 0.8870
  réponse à deux sujets : AR = 0.5000   plafond ‖c̄‖ = 0.7071
3. Réponse évasive : la question régénérée ressemble à l'originale
  cosinus brut = 0.9667   avec le drapeau « évasive » de RAGAS = 0.0
4. Le seuil 0.7 dépend du modèle d'embedding
  modèle A : pertinente 1 = 0.989  pertinente 2 = 0.972  hors sujet 1 = 0.000  hors sujet 2 = 0.292
           0.7 sépare : True   seuil calibré = 0.632
  modèle B : pertinente 1 = 0.998  pertinente 2 = 0.994  hors sujet 1 = 0.799  hors sujet 2 = 0.857
           0.7 sépare : False   seuil calibré = 0.926
5. Cas limites
  aucune question → None ; vecteur nul → ValueError ; nuages qui se chevauchent → None
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

Deux algorithmes : le calcul du score d'une réponse, puis la calibration du seuil qui décide « pertinente » ou « hors sujet ».

### Answer Relevancy d'une réponse

Entrées : la question d'origine, la réponse, le nombre n de questions à reconstruire, un LLM et un modèle d'embedding. Sortie : un score dans [−1, 1], 0 pour une réponse évasive, ou indéfini. L'idée : reconstruire des questions à partir de la réponse, les encoder avec le même modèle que la question d'origine, et moyenner les cosinus.

```text
ALGORITHME AnswerRelevancy
ENTRÉES : question, réponse, n, LLM, embedding
SORTIE : score ∈ [−1, 1], ou INDÉFINI
  (questions, évasive) ← LLM.reconstruire_questions(réponse, n)
  SI questions est vide ALORS
    RETOURNER INDÉFINI
  FIN SI
  SI évasive ALORS
    RETOURNER 0                                      (convention RAGAS)
  FIN SI
  e_o ← embedding(question)
  somme ← 0
  POUR chaque question q de questions FAIRE
    e_g ← embedding(q)                               (le même modèle que pour e_o)
    SI ‖e_g‖ = 0 OU ‖e_o‖ = 0 ALORS
      SIGNALER UNE ERREUR « vecteur nul : cosinus non défini »
    FIN SI
    somme ← somme + (e_g · e_o) / (‖e_g‖ · ‖e_o‖)
  FIN POUR
  RETOURNER somme / |questions|
```

**Complexité :** le coût réel est d'un appel au LLM et de n + 1 appels au modèle d'embedding (un seul s'ils sont envoyés en lot). Le calcul Python est en O(n·d) en temps pour des embeddings de dimension d, parce que chaque cosinus parcourt les d coordonnées trois fois (produit scalaire et deux normes) ; la mémoire supplémentaire est en O(d) si l'on traite les questions une par une, O(n·d) si on les garde toutes.

**Du squelette au code :** la reconstruction et les embeddings sont faits avant l'appel ; le programme reçoit `e_o`, `generees` et le drapeau `evasive`. Les deux premiers `SI` sont les deux premiers `return` de `answer_relevancy` ; la garde de norme nulle et la division sont dans `cosinus` ; la boucle et la division finale sont la ligne `sum(cosinus(g, e_o) for g in generees) / len(generees)`.

### Calibrer le seuil pour un modèle d'embedding

Entrées : les scores d'un échantillon de réponses étiquetées pertinentes et d'un échantillon étiqueté hors sujet, tous calculés avec le même modèle d'embedding. Sortie : un seuil τ, ou « pas de seuil parfait ». L'idée : placer τ au milieu de l'écart entre les deux nuages de scores quand ils sont séparés.

```text
ALGORITHME CalibrerSeuil
ENTRÉES : pertinentes[1..a], hors_sujet[1..b]
SORTIE : τ, ou AUCUN SEUIL PARFAIT
  SI a = 0 OU b = 0 ALORS
    RETOURNER AUCUN SEUIL PARFAIT
  FIN SI
  bas ← max(hors_sujet)                              (le meilleur score d'une réponse hors sujet)
  haut ← min(pertinentes)                            (le pire score d'une réponse pertinente)
  SI bas < haut ALORS
    RETOURNER (bas + haut) / 2
  SINON
    RETOURNER AUCUN SEUIL PARFAIT                    (choisir un compromis sur la courbe ROC, étape 51)
  FIN SI
```

**Complexité :** O(a + b) en temps, parce que le maximum et le minimum se trouvent chacun en un passage ; O(1) en mémoire supplémentaire. Le vrai coût est en amont : calculer a + b scores, donc a + b appels au LLM et autant de lots d'embeddings, et surtout faire étiqueter ces réponses par des humains.

**Du squelette au code :** le test des listes vides et le calcul de `bas` et `haut` sont les trois premières lignes de `calibrer_seuil` ; le `SI bas < haut` est l'expression conditionnelle `(bas + haut) / 2 if bas < haut else None`. Le bloc 4 de `main()` appelle cette fonction pour les modèles A et B et vérifie que le seuil obtenu sépare les deux nuages.

## Cas d'usage réels aux Émirats

Les scores et les seuils ci-dessous sont illustratifs ; les règles citées sont à confirmer avec le texte en vigueur.

### Banque — une question sur le prêt personnel, une réponse sur l'hypothèque

L'assistant d'une banque de détail de Dubaï reçoit : « combien puis-je emprunter au maximum en prêt personnel, et sur combien de temps ? ». Les règles de la CBUAE pour les particuliers limitent le prêt personnel à 20 fois le salaire mensuel et à 48 mois. Une version de prompt fait répondre l'agent par une explication détaillée des prêts hypothécaires, parce que les morceaux récupérés parlaient aussi de crédit immobilier. La réponse est fidèle à ses documents, mais les questions reconstruites (« quel apport pour un prêt immobilier ? », « quelle durée pour une hypothèque ? ») s'éloignent de la question d'origine, et le score tombe sous le seuil calibré. C'est la troisième ligne du tableau de diagnostic de l'étape 53 : Faithfulness haute, Answer Relevancy basse. Sans cette mesure, l'équipe aurait vu une réponse « fidèle » et l'aurait laissée en production. On suit l'Answer Relevancy par catégorie de produit et le taux de reformulation de la même question par le client dans la conversation.

### Secteur public — une question en arabe, des questions reconstruites en anglais

Une entité de services publics en ligne, accessible par UAE Pass, reçoit les demandes en arabe et en anglais. Quand un usager écrit en arabe et que l'agent répond en anglais, les questions reconstruites sont en anglais, et un modèle d'embedding monolingue les juge éloignées de la question arabe même quand le sens est identique. L'équipe impose un modèle d'embedding multilingue pour l'évaluation, normalise l'arabe avant l'encodage (alef, ta marbuta, diacritiques), et calibre un seuil par langue sur 200 demandes étiquetées dans chacune. Sans ces précautions, la métrique aurait puni toutes les réponses en anglais à des questions en arabe et poussé l'équipe à corriger un problème qui n'existait pas. Les demandes servant à l'évaluation sont anonymisées, conformément à la PDPL. On suit l'Answer Relevancy séparément par langue de la question et par langue de la réponse.

### RH — la réponse évasive qui avait un bon score

Un cabinet RH multi-émirats mesure la pertinence des réponses de son agent sur les questions d'indemnité de fin de service. Une version de l'agent répond à beaucoup de questions par « je vous invite à contacter votre service RH pour le calcul de votre indemnité ». Sans le drapeau de réponse évasive, ces réponses obtenaient un score élevé : la question reconstruite, « comment obtenir le calcul de mon indemnité de fin de service ? », est très proche de la question d'origine, comme le cosinus de 0,967 de la démonstration. Avec la convention de RAGAS, ces réponses reçoivent 0, et la moyenne de la version chute. L'équipe branche alors l'outil de calcul canonique (21 jours de salaire de base par an pour les cinq premières années, 30 jours au-delà, plafond de 24 mois), et l'agent répond avec un montant. On suit la part de réponses évasives et l'Answer Relevancy hors réponses évasives, pour ne pas confondre les deux causes de baisse.

### Immobilier — Ejari ou transfert de propriété ?

Une agence de Dubaï reçoit la question « comment enregistrer mon bail dans Ejari, et qui paie les frais ? ». Une version de l'agent répond par le détail des frais de transfert de propriété du DLD (4 % de la valeur du bien), un sujet voisin mais différent : l'acheteur d'un bien, pas le locataire. La réponse est exacte et fidèle aux documents récupérés, mais les questions reconstruites portent sur l'achat, et le score tombe de 0,9 à 0,5 environ. L'équipe en déduit que le retriever confond les deux familles de documents, et sépare les index « location » et « vente ». Sans cette mesure, l'agence aurait reçu des plaintes de locataires à qui l'on parle d'un achat qu'ils ne font pas. On suit l'Answer Relevancy par type de démarche et la part de conversations transférées à un agent humain.

### Assurance — une réponse en deux parties plafonnée

Un assureur auto remarque que les réponses de son agent aux questions sur la franchise obtiennent rarement plus de 0,75, alors qu'elles sont justes. L'analyse montre que l'agent ajoute systématiquement un paragraphe sur le réseau de garages agréés : la moitié des questions reconstruites parle de franchise, l'autre moitié de garages. Comme le montre la démonstration (point 2), le centroïde raccourcit et plafonne le score, à 0,7071 dans le cas extrême de deux sujets sans rapport. L'équipe ne baisse pas le seuil : elle modifie le prompt pour que l'agent réponde d'abord à la question posée et ne propose l'information sur les garages qu'en une ligne, ou sur demande. Le score remonte au-dessus de 0,9, et les assurés lisent moins de texte inutile. On suit l'Answer Relevancy et la longueur moyenne des réponses, en tokens.

### Crypto — changer de modèle d'embedding sans recalibrer

Une plateforme d'actifs virtuels agréée par la VARA remplace son modèle d'embedding par un modèle plus récent, et garde le seuil de 0,7 hérité de l'ancien. Du jour au lendemain, presque toutes les réponses de son agent de support passent le seuil, y compris des réponses manifestement hors sujet sur les frais de retrait. Le nouveau modèle est anisotrope : deux textes sans rapport y ont un cosinus de 0,8, exactement le cas t = 2 de la démonstration (point 5). L'équipe recalibre sur 200 réponses étiquetées : le nouveau seuil est autour de 0,93, et les deux nuages se chevauchent un peu, ce qui l'oblige à choisir un compromis sur la courbe ROC. Sans cette recalibration, la métrique aurait cessé de détecter quoi que ce soit, tout en affichant de meilleurs chiffres. On suit l'AUC de la métrique sur le jeu étiqueté à chaque changement de modèle d'embedding.

## Pièges et limites

- **Garder le seuil de 0,7 sans le calibrer.** Il dépend du modèle d'embedding ; un modèle anisotrope donne 0,8 à des textes sans rapport.
- **Oublier les réponses évasives.** Sans le drapeau, une non-réponse qui reprend les mots de la question obtient un score élevé.
- **Diviser par une norme nulle, ou renvoyer 0 pour une liste vide.** Un vecteur nul lève `ValueError` ; aucune question reconstruite donne `None`, pas 0.
- **Lire la pertinence comme une preuve de justesse.** Une réponse fausse mais dans le sujet a un bon score : il faut la Faithfulness (étape 54) et la justesse (étape 63) à côté.
- **Mélanger les modèles d'embedding.** La question d'origine et les questions reconstruites doivent être encodées par le même modèle, sinon les cosinus ne veulent rien dire.

### Exercice feuille blanche

1. Sans regarder le code, écrire `answer_relevancy` avec ses deux conventions, puis calculer à la main le score de Eₒ = (1 ; 0) avec les questions (1 ; 1) et (1 ; 0). (Réponse : (0,7071 + 1)/2 = 0,854.)
2. Prédire, puis vérifier : si l'on ajoute à tous les vecteurs une composante commune de norme t = 3, quel cosinus obtiennent deux textes dont les vecteurs d'origine étaient orthogonaux et unitaires ? (Réponse : 9/10 = 0,9.)
3. Trouver le bug : `return float(np.mean(sims))` précédé de `if not generated: return 0.0`. Quel problème pose ce 0,0 dans la moyenne d'un jeu d'évaluation ? (Réponse : une panne du générateur de questions est comptée comme une réponse hors sujet et fait baisser la moyenne ; il faut `None`, exclu de la moyenne et compté à part.)

## Pour aller plus loin

- Une correction courante de l'anisotropie consiste à soustraire à chaque embedding la moyenne des embeddings d'un grand corpus avant de calculer les cosinus ; le seuil reste à recalibrer après.
- RAGAS appelle aujourd'hui cette métrique « Response Relevancy » ; la formule et la convention des réponses évasives sont les mêmes.
- La preuve que l'Answer Relevancy est un produit avec un centroïde est reprise, avec ses corollaires, à l'étape 64 bis.

> Suite : [Precision, Recall et F1 en évaluation](<56-Evaluation-Formule-Precision-Recall-F1.md>) — étape 56.
