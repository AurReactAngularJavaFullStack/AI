# Fiche 05b_attention_ia_agentique — Attention, affiche

> Image : `05b_attention_ia_agentique.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 31 — Attention par produit scalaire normalisé](<../../06-Attention-et-Transformer/31-Attention-Formule-Produit-Scalaire-Normalise.md>)

**La formule de la fiche 05, sur une affiche**

## Ce que montre l'image

Affiche « Attention scaled dot-product en IA agentique ». La formule, puis les quatre ingrédients posés comme des questions : Q, « que cherche l'agent maintenant ? » ; K, « à quoi correspondent les informations disponibles ? » ; V, « quelle information récupérer ? » ; dₖ, la dimension, dont la racine stabilise l'échelle des produits scalaires. En bas, cinq usages : base des Transformers, dépendances à longue distance, focus sur l'information utile, raisonnement en plusieurs étapes, mémoire des agents.

**Ce que l'image ajoute à la fiche 05 :** la lecture « question, étiquette, contenu » de Q, K et V, qui aide à retenir la formule.

**À lire avec prudence :** l'affiche écrit softmax(Q Kᵀ/√dₖ) ; la division porte bien sur tout le produit Q Kᵀ.

## Formule

$$
\mathrm{Attention}(Q, K, V) = \mathrm{softmax}\!\left(\frac{Q K^{\top}}{\sqrt{d_k}}\right) V
$$

## Éléments

$$
Q
$$

**Q** : requêtes, ce que la position courante cherche.

$$
K
$$

**K** : clés, ce que chaque position propose.

$$
V
$$

**V** : valeurs, l'information transportée.

$$
d_k,\ \sqrt{d_k}
$$

**dₖ** : la dimension des clés. √dₖ empêche les scores de saturer la softmax.

$$
\operatorname{softmax}
$$

**softmax** : transforme chaque ligne de scores en poids qui somment à 1.

## Ce que c'est

Chaque position calcule une moyenne pondérée des valeurs. Le poids dépend de l'alignement entre sa requête et les clés.

## Effets et impacts

- C'est le cœur du Transformer, donc de l'agent qui lit un RAG.
- Un poids d'attention élevé n'est pas une preuve de raisonnement correct.
- Le coût croît comme n².

## Exemple chiffré

Deux tokens, dₖ = 4, un score brut q·k = 8. Sans échelle, 8 part dans l'exponentielle et écrase les autres. Divisé par √4 = 2, le score devient 4. L'écart reste, la softmax ne s'effondre pas sur un seul token.

Doubler la longueur de la séquence multiplie par quatre le nombre de cases de QKᵀ.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(z)`** — Dans la tête d'un agent qui lit un dossier RAG, cette fonction est le budget d'attention : une enveloppe fixe de 1 qu'il faut répartir entre les passages, et ce qu'un passage reçoit, un autre le perd. Elle reçoit la liste des scores, soustrait le plus grand, prend l'exponentielle de chaque écart et divise par la somme ; elle rend les parts, positives et de total 1. C'est la même softmax que celle de la fiche 04, à température 1, utilisée ici pour transformer les scores d'alignement en poids de lecture.

**`attention(Q, K, V)`** — Celle-ci décrit un enquêteur qui interroge plusieurs témoins : sa question est la requête, ce que chaque témoin prétend savoir est sa clé, et son témoignage complet est sa valeur. Elle reçoit Q, K et V, prend d_k comme la dimension des clés, calcule pour chaque requête le produit scalaire avec chaque clé divisé par √d_k, transforme ces scores en poids par `softmax`, puis compose la synthèse en additionnant les valeurs pondérées. Elle rend le couple (sorties, poids) ; la division par √d_k empêche qu'un score brut de 8, avec d_k = 4, n'écrase tous les autres témoins : il ne vaut plus que 4.

**`main()`** — C'est le commissaire qui relit le rapport d'enquête. Il ne reçoit rien ; il fait tourner `attention` sur l'exemple de la fiche 05, une requête [1 ; 0] et trois clés qui servent aussi de valeurs, et vérifie par `assert` les poids [0,431 ; 0,245 ; 0,325] et la synthèse [0,574 ; 0,426]. Il vérifie ensuite le cas de cette fiche, 8 / √4 = 4, et le coût de lecture d'un long contexte, 1 000 000 cases de QKᵀ pour 1000 tokens et quatre fois plus pour 2000 ; il ne rend rien.

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
- [Fiche 05 — Attention](<05_attention_scaled_dot_product.md>)
