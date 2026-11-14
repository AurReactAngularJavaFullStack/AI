# Fiche 05c_attention_agentic_ai — Scaled dot-product attention

> Image : `05c_attention_agentic_ai.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 31 — Attention par produit scalaire normalisé](<../../06-Attention-et-Transformer/31-Attention-Formule-Produit-Scalaire-Normalise.md>)

**La même attention, légendes en anglais**

Même formule que la fiche 05. Le nom de fichier d'origine orthographiait mal « scaled ». La formule, elle, est le produit scalaire mis à l'échelle.

## Ce que montre l'image

Affiche en anglais, la plus complète de la série. Le calcul en quatre étapes : similarité Q Kᵀ, mise à l'échelle par √dₖ, softmax en poids, somme pondérée des valeurs V. Un encadré « Why scaled? » : sans la division, de grands produits scalaires poussent la softmax dans des zones où le gradient est presque nul. Une matrice de poids d'attention en couleurs sur la phrase « The agent plans ahead to achieve the goal » : le token « plans » regarde surtout « ahead » et « goal ». Six usages en bas.

**Ce que l'image ajoute à la fiche 05 :** la matrice de poids, à lire ligne par ligne (chaque ligne somme à 1), et la raison de la division par √dₖ, démontrée dans `Demonstrations/03-Modele/05_attention_scaled_dot_product.md`.

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

**`softmax(z)`** — Cette fonction joue l'oreille d'un invité dans une réception bruyante : elle ne peut pas tout écouter, et répartit son écoute entre les conversations en donnant beaucoup à la plus intéressante et presque rien aux autres. Elle reçoit une liste de scores, retranche le maximum, calcule l'exponentielle de chaque écart, puis divise par la somme de ces exponentielles ; elle rend des poids positifs qui totalisent 1. C'est la softmax de la fiche 04 à température 1, appliquée ici aux scores d'alignement entre une requête et des clés.

**`attention(Q, K, V)`** — Celle-ci est la soirée tout entière : chaque invité, la requête, tend l'oreille vers les groupes dont le sujet, la clé, ressemble à ce qu'il cherche, et repart avec un mélange de ce qu'il a entendu, les valeurs. Elle reçoit les requêtes, les clés et les valeurs, prend d_k égal à la dimension des clés, divise chaque produit scalaire par √d_k, confie les scores à `softmax`, puis additionne les valeurs pondérées coordonnée par coordonnée. Elle rend les sorties et les poids ; sans la division par √d_k, un score brut de 8 dominerait toute la salle, alors qu'avec d_k = 4 il ne vaut plus que 4.

**`main()`** — C'est l'hôte qui vérifie, à la fin de la soirée, que chacun a bien entendu. Il ne reçoit rien ; il exécute `attention` sur l'exemple de la fiche 05, une requête [1 ; 0] et trois clés réutilisées comme valeurs, et contrôle par `assert` les poids [0,431 ; 0,245 ; 0,325] et la sortie [0,574 ; 0,426]. Il vérifie ensuite que 8 / √4 vaut 4, le cas de cette fiche, puis que la matrice QKᵀ passe de 1 000 000 de cases pour 1000 tokens à 4 000 000 pour 2000 ; il ne rend rien.

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
