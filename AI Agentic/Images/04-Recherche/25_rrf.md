# Fiche 25 — Reciprocal Rank Fusion

> Image : `25_rrf.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 24 — Reciprocal Rank Fusion](<../../05-RAG/24-RAG-Formule-RRF.md>)

**Fusionner des classements sans mêler leurs scores**

## Formule

$$
\operatorname{RRF}(d) = \sum_{j \,:\, d \in R_j} \frac{1}{k + \operatorname{rang}_j(d)}
$$

**Correction par rapport à l'image.** Le classement fusionné de l'image est inexact. Avec k = 60, α et β sont à égalité, ζ (rang 4 du moteur B) passe devant ε (rang 5 du moteur A), et « Doc η » n'existe dans aucune des deux listes. Le calcul juste est dans l'exemple.

## Éléments

$$
d
$$

**d** : un document candidat.

$$
R_j
$$

**Rⱼ** : le classement du moteur j (par exemple BM25 ou cosinus).

$$
\operatorname{rang}_j(d)
$$

**rangⱼ(d)** : la position de d dans ce classement, en partant de 1.

$$
k
$$

**k** : la constante d'amortissement, souvent 60.

$$
\sum_{j \,:\, d \in R_j}
$$

**La somme** : un bonus pour chaque liste où d apparaît.

## Ce que c'est

RRF additionne l'inverse du rang. Un document bien classé par plusieurs moteurs monte, sans jamais comparer un score BM25 à un cosinus, qui n'ont pas la même échelle.

## Effets et impacts

- k n'est pas le nombre de résultats à renvoyer.
- k = 60 amortit l'écart entre la 1ʳᵉ et la 10ᵉ place.
- Deux moteurs trop semblables renforcent les mêmes erreurs.
- La fusion ne remplace pas le contrôle d'accès aux documents.

## Exemple chiffré

Moteur A : α, β, γ, δ, ε. Moteur B : β, α, δ, ζ, γ. Avec k = 60 :

$$
\alpha = \beta = \frac{1}{61} + \frac{1}{62} \approx 0{,}03252
$$

$$
\delta = \frac{1}{64} + \frac{1}{63} \approx 0{,}03150, \qquad \gamma = \frac{1}{63} + \frac{1}{65} \approx 0{,}03126
$$

$$
\zeta = \frac{1}{64} = 0{,}015625, \qquad \varepsilon = \frac{1}{65} \approx 0{,}01538
$$

Classement fusionné : α et β ex aequo, puis δ, γ, ζ, ε.

Le programme affiche `0.01562` pour ζ : la valeur exacte 0,015625 tombe pile entre 0,01562 et 0,01563, et dans ce cas `round` de Python arrondit vers le chiffre pair.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`rrf(classements, k)`** — Cette fonction se comporte comme le président d'un festival qui reçoit les palmarès de plusieurs jurys, notés chacun à sa manière, et refuse de comparer leurs notes : il ne retient que les places, et donne à chaque film un bonus d'autant plus grand qu'il est bien classé. Elle reçoit la liste des classements et la constante k, 60 par défaut, parcourt chaque classement en numérotant les rangs à partir de 1, ajoute 1 / (k + rang) au score de chaque document rencontré, puis trie les scores par ordre décroissant en départageant les égalités par le nom. Elle rend la liste des couples (document, score) : pour les deux moteurs de la fiche, α et β arrivent ex aequo avec environ 0,03252, devant δ, γ, ζ et ε.

**`main()`** — C'est le secrétaire du festival qui proclame le palmarès fusionné et vérifie qu'il est juste. Il ne reçoit rien ; il fusionne le classement A, α, β, γ, δ, ε, et le classement B, β, α, δ, ζ, γ, imprime les six couples arrondis à cinq décimales et vérifie par `assert` l'ordre α, β, δ, γ, ζ, ε. Il contrôle encore que α et β ont le même score, que ζ, cité une fois au rang 4, devance ε, cité une fois au rang 5, et qu'aucun document jamais classé n'apparaît dans le résultat ; il ne rend rien.

```python
"""Fiche 25 — Reciprocal Rank Fusion : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def rrf(classements: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """RRF(d) = Σ_j 1 / (k + rang_j(d)), sur les classements où d apparaît ; égalités départagées par le nom."""
    scores: dict[str, float] = {}
    for classement in classements:
        for rang, doc in enumerate(classement, start=1):
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (k + rang)
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))


def main() -> None:
    A = ["α", "β", "γ", "δ", "ε"]
    B = ["β", "α", "δ", "ζ", "γ"]
    fusion = rrf([A, B])
    print("classement fusionné :", [(d, round(s, 5)) for d, s in fusion])
    assert [d for d, _ in fusion] == ["α", "β", "δ", "γ", "ζ", "ε"]
    s = dict(fusion)
    assert math.isclose(s["α"], s["β"]) and s["ζ"] > s["ε"] and "η" not in s
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
classement fusionné : [('α', 0.03252), ('β', 0.03252), ('δ', 0.0315), ('γ', 0.03126), ('ζ', 0.01562), ('ε', 0.01538)]
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`rrf` parcourt chaque classement du premier au dernier document, en numérotant les rangs à partir de 1, et ajoute au score de chaque document la quantité 1 / (k + rang). Un document absent d'un classement n'y reçoit rien, ce qui n'est pas une pénalité mais simplement l'absence d'un bonus. Les scores sont gardés dans un dictionnaire, puis triés par ordre décroissant ; deux scores égaux sont départagés par le nom du document, pour que le résultat soit toujours le même d'une exécution à l'autre. La constante k, ici 60, amortit l'écart entre les premiers rangs : 1/61 et 1/62 sont presque égaux, ce qui évite qu'un seul moteur impose son premier résultat.

`main` rejoue les deux listes de l'image et vérifie le classement exact, qui corrige celui de l'affiche : α et β sont à égalité (1/61 + 1/62 chacun), δ passe devant γ, ζ, cinquième avec un seul rang 4, passe devant ε, qui n'a qu'un rang 5, et aucun « Doc η » n'apparaît, puisqu'il n'est dans aucune des deux listes.

## Squelette algorithmique

```text
ALGORITHME RRF
ENTRÉES : classements L₁ … L_m (listes ordonnées), constante k
SORTIE  : un classement fusionné

  score ← dictionnaire vide
  POUR CHAQUE classement L FAIRE
      POUR rang DE 1 À longueur(L) FAIRE
          d ← L[rang] ; score[d] ← score[d] + 1 / (k + rang)
      FIN POUR
  FIN POUR
  RETOURNER les documents triés par score décroissant (égalités par nom)
```

**Complexité.** O(Σ longueurs des classements) pour les scores, puis O(U log U) pour trier les U documents distincts. Aucune normalisation n'est nécessaire : seuls les rangs comptent.

**Du squelette au code.** La double boucle est la double boucle `for` de `rrf`, et le tri final est son `sorted(..., key=...)`.

## Dans le cours

- [Étape 24 — Reciprocal Rank Fusion](<../../05-RAG/24-RAG-Formule-RRF.md>)
- [Étape 23 — Score hybride](<../../05-RAG/23-RAG-Formule-Score-Hybride.md>)
