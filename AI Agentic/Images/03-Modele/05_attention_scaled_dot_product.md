# Fiche 05 — Attention par produit scalaire normalisé

> Image : `05_attention_scaled_dot_product.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 31 — Attention par produit scalaire normalisé](<../../06-Attention-et-Transformer/31-Attention-Formule-Produit-Scalaire-Normalise.md>)

**Chaque token choisit ce qu'il lit**

## Formule

$$
\operatorname{Attention}(Q, K, V) = \operatorname{softmax}\left( \frac{Q K^\top}{\sqrt{d_k}} \right) V
$$

## Éléments

$$
Q
$$

**Q** : les requêtes, ce que chaque position cherche.

$$
K
$$

**K** : les clés, ce que chaque position propose.

$$
V
$$

**V** : les valeurs, l'information transportée.

$$
K^\top
$$

**Kᵀ** : la transposée de K. Le produit QKᵀ calcule tous les produits scalaires requête–clé d'un coup.

$$
d_k
$$

**dₖ** : la dimension des clés (et des requêtes).

$$
\sqrt{d_k}
$$

**√dₖ** : le facteur qui stabilise les scores. Il ramène leur variance à 1 (démontré à l'étape 32 bis).

$$
\operatorname{softmax}
$$

**softmax** : transforme les scores en poids de lecture qui somment à 1 (fiche 04).

## Ce que c'est

Chaque position calcule une moyenne pondérée des valeurs. Le poids de chaque valeur dépend de l'alignement entre la requête de la position et la clé de cette valeur.

## Effets et impacts

- C'est le cœur du Transformer.
- Le contexte, les passages inutiles et leur place changent la réponse : les poids se partagent un total de 1.
- La matrice d'interactions croît comme n² : doubler la longueur du contexte quadruple les interactions.
- Un poids d'attention élevé n'est pas une preuve de raisonnement correct.

## Exemple chiffré

Une requête et trois clés en dimension 2 (les valeurs sont égales aux clés) :

$$
q = [1\ ;\ 0], \quad k_1 = [0{,}9\ ;\ 0{,}1], \quad k_2 = [0{,}1\ ;\ 0{,}9], \quad k_3 = [0{,}5\ ;\ 0{,}5]
$$

Scores divisés par √2, puis softmax :

$$
\left(\frac{0{,}9}{\sqrt{2}},\ \frac{0{,}1}{\sqrt{2}},\ \frac{0{,}5}{\sqrt{2}}\right) \approx (0{,}636\ ;\ 0{,}071\ ;\ 0{,}354) \ \xrightarrow{\ \operatorname{softmax}\ }\ (0{,}431\ ;\ 0{,}245\ ;\ 0{,}325)
$$

$$
\text{sortie} = 0{,}431\,k_1 + 0{,}245\,k_2 + 0{,}325\,k_3 \approx [0{,}574\ ;\ 0{,}426]
$$

Pour le coût : 1 000 tokens donnent 10⁶ interactions, 2 000 tokens en donnent 4 × 10⁶.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(z)`** — Cette petite fonction est la balance du programme : elle reçoit une liste de scores et la transforme en poids qui se partagent exactement un total de 1, comme on répartit une heure de lecture entre plusieurs dossiers selon leur intérêt. Elle retranche d'abord le plus grand score pour que les exponentielles ne débordent pas, élève e à chaque écart, puis divise chaque exponentielle par leur somme. Elle rend la liste des poids, tous positifs ; ici sans température, c'est la softmax de la fiche 04 avec T = 1, et pour les scores (0,636 ; 0,071 ; 0,354) elle rend (0,431 ; 0,245 ; 0,325).

**`attention(Q, K, V)`** — Celle-ci raconte un archiviste qui arrive avec une question, la requête, et parcourt des fiches dont chacune porte une étiquette, la clé, et un contenu, la valeur. Elle reçoit les listes de requêtes Q, de clés K et de valeurs V, prend d_k égal à la dimension des clés, et pour chaque requête calcule le produit scalaire avec chaque clé divisé par √d_k, passe ces scores dans `softmax`, puis forme, coordonnée par coordonnée, la somme des valeurs pondérées par ces poids. Elle rend le couple (sorties, poids) : pour q = [1 ; 0] et les trois clés de la fiche, prises aussi comme valeurs, la sortie vaut environ [0,574 ; 0,426].

**`main()`** — C'est le contrôleur qui vérifie la lecture de l'archiviste et la facture qu'elle implique. Il ne reçoit rien ; il appelle `attention` sur l'exemple de la fiche et contrôle par `assert` les poids [0,431 ; 0,245 ; 0,325] et la sortie [0,574 ; 0,426], puis vérifie qu'un score brut de 8 divisé par √4 donne 4, le cas des fiches 05a à 05e. Il compte enfin les cases de la matrice QKᵀ, 1 000 000 pour 1000 tokens et 4 000 000 pour 2000, vérifie que doubler la longueur quadruple ce nombre, et ne rend rien.

```python
"""Fiches 05, 05a à 05e — attention par produit scalaire normalisé : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def softmax(z: list[float]) -> list[float]:
    m = max(z)
    e = [math.exp(x - m) for x in z]
    return [x / sum(e) for x in e]


def attention(Q: list[list[float]], K: list[list[float]], V: list[list[float]]):
    """Pour chaque requête : poids = softmax(q · kⱼ / √d_k), sortie = Σⱼ poidsⱼ × vⱼ."""
    d_k = len(K[0])
    sorties, tous_les_poids = [], []
    for q in Q:
        scores = [sum(a * b for a, b in zip(q, k)) / math.sqrt(d_k) for k in K]
        poids = softmax(scores)
        sortie = [sum(p * v[c] for p, v in zip(poids, V)) for c in range(len(V[0]))]
        sorties.append(sortie)
        tous_les_poids.append(poids)
    return sorties, tous_les_poids


def main() -> None:
    K = [[0.9, 0.1], [0.1, 0.9], [0.5, 0.5]]
    sorties, poids = attention([[1.0, 0.0]], K, K)          # fiche 05 : valeurs = clés
    print("poids :", [round(p, 3) for p in poids[0]], "  sortie :", [round(v, 3) for v in sorties[0]])
    assert [round(p, 3) for p in poids[0]] == [0.431, 0.245, 0.325]
    assert [round(v, 3) for v in sorties[0]] == [0.574, 0.426]
    print(f"fiches 05a à 05e : score brut 8, d_k = 4  ->  {8 / math.sqrt(4):.0f} après division par √d_k")
    assert 8 / math.sqrt(4) == 4
    n = 1000
    print(f"cases de QKᵀ : {n * n:,} pour {n} tokens, {(2 * n) ** 2:,} pour {2 * n}")
    assert (2 * n) ** 2 == 4 * n * n
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
poids : [0.431, 0.245, 0.325]   sortie : [0.574, 0.426]
fiches 05a à 05e : score brut 8, d_k = 4  ->  4 après division par √d_k
cases de QKᵀ : 1,000,000 pour 1000 tokens, 4,000,000 pour 2000
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`attention` traite les requêtes une par une. Pour chaque requête q, elle calcule le produit scalaire de q avec chaque clé, le divise par √d_k, puis passe ces scores dans la softmax pour obtenir des poids positifs qui somment à 1 : ce sont les « poids de lecture » de la fiche, qui disent quelle part de chaque position la requête va lire. Elle construit ensuite la sortie coordonnée par coordonnée, comme la somme des valeurs pondérées par ces poids : la sortie est donc toujours une moyenne des valeurs, jamais une information qui n'y était pas. La softmax utilisée retranche le maximum avant l'exponentielle pour ne jamais déborder.

`main` reprend l'exemple de la fiche 05 : une requête [1 ; 0] et trois clés, dont les valeurs sont égales aux clés. Les poids valent 0,431, 0,245 et 0,325, la première clé, la plus alignée avec la requête, recevant la plus grande part, et la sortie vaut [0,574 ; 0,426]. Le programme vérifie aussi l'exemple des fiches 05a à 05e, où un score brut de 8 avec d_k = 4 devient 4 après la division par √4, puis le coût quadratique : doubler le nombre de tokens multiplie par quatre le nombre de cases de la matrice QKᵀ.

## Squelette algorithmique

```text
ALGORITHME Attention
ENTRÉES : requêtes Q (n × d_k), clés K (n × d_k), valeurs V (n × d_v)
SORTIE  : sorties O (n × d_v)

  POUR CHAQUE requête qᵢ FAIRE
      POUR CHAQUE clé kⱼ FAIRE  sⱼ ← (qᵢ · kⱼ) / √d_k  FIN POUR
      a ← Softmax(s)                                   (poids de lecture, somme 1)
      POUR c DE 1 À d_v FAIRE  Oᵢ,c ← Σⱼ aⱼ × Vⱼ,c  FIN POUR
  FIN POUR
  RETOURNER O
```

**Complexité.** Pour n positions : O(n² × d_k) pour les scores et O(n² × d_v) pour les sorties, avec n² poids à garder en mémoire. C'est ce carré qui rend les longs contextes coûteux.

**Du squelette au code.** La boucle sur les requêtes est le `for q in Q` de `attention`, la boucle des scores est la compréhension de liste `scores = [...]`, la ligne de softmax est l'appel à `softmax`, et la dernière boucle est le calcul de `sortie`.

## Dans le cours

- [Étape 31 — Attention par produit scalaire normalisé](<../../06-Attention-et-Transformer/31-Attention-Formule-Produit-Scalaire-Normalise.md>)
- [Étape 32 bis — Théorèmes de l'attention et de la softmax](<../../06-Attention-et-Transformer/32b-Theoremes-Attention-et-Softmax.md>)
- [Étape 33 — Déroulé numérique de l'attention](<../../06-Attention-et-Transformer/33-Transformer-et-Attention-Deroule-Numerique.md>)
