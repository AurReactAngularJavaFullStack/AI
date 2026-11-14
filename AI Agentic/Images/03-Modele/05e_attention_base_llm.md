# Fiche 05e_attention_base_llm — Attention, base des LLM

> Image : `05e_attention_base_llm.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 31 — Attention par produit scalaire normalisé](<../../06-Attention-et-Transformer/31-Attention-Formule-Produit-Scalaire-Normalise.md>)

**Pourquoi un agent moderne lit un long contexte**

## Ce que montre l'image

Affiche « Mécanisme d'attention, base des agents LLM modernes ». La formule au centre ; Q, K et V à gauche, reliés à elle par des flèches ; deux encadrés à droite, l'un pour la division par √dₖ (stabiliser les gradients, éviter la saturation), l'autre pour la softmax (des poids qui somment à 1). En bas : conséquences (pondérer les tokens), effets (dépendances longues, au-delà des RNN), impacts (raisonnement et planification), et une légende des symboles.

**Ce que l'image ajoute à la fiche 05 :** une légende compacte des symboles, à recopier en tête de feuille avant de refaire la démonstration.

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

**`softmax(z)`** — Cette fonction est le pupitre de mixage d'un chef d'orchestre qui règle le volume de chaque instrument pour que la somme des volumes reste fixe. Elle reçoit les scores, retranche le plus grand, calcule l'exponentielle de chaque écart, puis divise par leur total ; elle rend une liste de poids positifs qui somment à 1. C'est la softmax de la fiche 04, sans température, et dans un LLM c'est elle qui décide, à chaque couche, quelle part d'écoute chaque token accorde aux autres.

**`attention(Q, K, V)`** — Celle-ci décrit le chef d'orchestre lui-même : pour chaque mesure à jouer, la requête, il écoute les pupitres dont la partition, la clé, s'accorde avec elle, et fait entendre un mélange de leurs sons, les valeurs. Elle reçoit Q, K et V, prend d_k égal à la dimension des clés, divise chaque produit scalaire requête-clé par √d_k, passe les scores dans `softmax`, puis additionne les valeurs pondérées coordonnée par coordonnée. Elle rend les sorties et les poids ; la mise à l'échelle par √d_k ramène un score brut de 8, avec d_k = 4, à 4, pour qu'un seul pupitre ne couvre pas tous les autres.

**`main()`** — C'est la répétition où le chef vérifie l'accord de l'orchestre. Il ne reçoit rien ; il appelle `attention` sur l'exemple de la fiche 05, une requête [1 ; 0] et trois clés employées aussi comme valeurs, et contrôle par `assert` les poids [0,431 ; 0,245 ; 0,325] et la sortie [0,574 ; 0,426]. Il vérifie ensuite que 8 / √4 vaut 4, l'exemple de cette fiche, puis que la matrice QKᵀ compte 1 000 000 de cases pour 1000 tokens et quatre fois plus pour 2000 ; il ne rend rien.

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
