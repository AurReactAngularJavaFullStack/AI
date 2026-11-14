# Fiche 23 — Vraisemblance autorégressive

> Image : `23_vraisemblance_autoregressive.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 3 — Fondements de la softmax](<../../02-LLM-Softmax-et-Prompts/03-Fondements-Softmax-et-LLM.md>)

**Chaque token dépend de ceux d'avant**

## Formule

$$
P(x_{1:n} \mid c) = \prod_{t=1}^{n} P(x_t \mid x_{<t}, c)
$$

## Éléments

$$
c
$$

**c** : le contexte donné au modèle (prompt, documents).

$$
x_t
$$

**xₜ** : le token généré à l'étape t.

$$
x_{<t}
$$

**x<ₜ** : tous les tokens déjà produits avant t.

$$
\prod_{t=1}^{n}
$$

**Π (pi majuscule)** : le produit. On multiplie les probabilités conditionnelles.

$$
n
$$

**n** : la longueur de la séquence.

## Ce que c'est

La probabilité d'une phrase est le produit des probabilités de ses tokens, chacun conditionné par le passé. Une erreur tôt change tout le futur, puisque chaque token suivant est conditionné par elle.

## Effets et impacts

- Dix tokens à 0,5 donnent une probabilité de séquence proche de 0,001.
- La suite la plus probable n'est ni forcément vraie, ni utile, ni autorisée.
- La longueur fait chuter la probabilité brute : comparer des textes exige la même tokenisation, et en pratique une moyenne par token (la perplexité, fiche 32).

## Exemple chiffré

$$
0{,}5^{10} \approx 0{,}000977
$$

En logarithme, le produit devient une somme, plus stable en machine :

$$
\ln P = \sum_{t=1}^{10} \ln 0{,}5 = 10 \times (-0{,}693) \approx -6{,}93
$$

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`log_vraisemblance(probas)`** — Cette fonction raconte un funambule qui traverse une suite de cordes : la chance d'arriver au bout est le produit des chances de franchir chaque corde, et ce produit fond si vite qu'on préfère compter en logarithmes, où il devient une simple addition. Elle reçoit la liste des probabilités conditionnelles des tokens, lève `ValueError` si l'une d'elles n'est pas dans ]0, 1], puis rend la somme de leurs logarithmes népériens. Pour dix tokens à 0,5, elle rend 10 × ln 0,5 ≈ −6,931, dont l'exponentielle redonne 0,5¹⁰ ≈ 0,000977, la probabilité de la phrase entière.

**`perplexite(probas)`** — Celle-ci traduit la même traversée en un nombre plus parlant : le nombre de cordes entre lesquelles le funambule aurait hésité, en moyenne, à chaque pas. Elle reçoit la même liste, appelle `log_vraisemblance`, divise par le nombre de tokens, change le signe et prend l'exponentielle, ce qui rend exp(−(1/n) Σ ln pₜ). Pour les probabilités 1/2, 1/4 et 1/8, elle rend 4, et pour dix tokens à 0,5 elle rend 2 : le modèle hésite comme entre deux choix équiprobables à chaque token.

**`main()`** — C'est le juge de piste qui vérifie les deux scores. Il ne reçoit rien ; il calcule la log-vraisemblance de dix tokens à 0,5, imprime P ≈ 0,000977 et ln P ≈ −6,931 et vérifie par `assert` que l'exponentielle retrouve 0,5¹⁰ et que le logarithme arrondi vaut −6,931. Il calcule ensuite les perplexités 4,0000 et 2,0000, les contrôle, puis vérifie que cinq tokens à 1/8 donnent une perplexité de 8, comme huit branches équiprobables ; il ne rend rien.

```python
"""Fiches 23 et 32 — vraisemblance autorégressive et perplexité : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def log_vraisemblance(probas: list[float]) -> float:
    """ln P(x₁:n | c) = Σ ln P(xₜ | x<ₜ, c) : le produit devient une somme de logarithmes."""
    if any(not 0 < p <= 1 for p in probas):
        raise ValueError("chaque probabilité doit être dans ]0, 1]")
    return sum(math.log(p) for p in probas)


def perplexite(probas: list[float]) -> float:
    """PPL = exp(−(1/n) Σ ln P(xₜ | x<ₜ, c))."""
    return math.exp(-log_vraisemblance(probas) / len(probas))


def main() -> None:
    dix = [0.5] * 10
    print(f"dix tokens à 0,5 : P = {math.exp(log_vraisemblance(dix)):.6f}   ln P = {log_vraisemblance(dix):.3f}")
    assert math.isclose(math.exp(log_vraisemblance(dix)), 0.5 ** 10) and round(log_vraisemblance(dix), 3) == -6.931
    print(f"perplexité de (1/2, 1/4, 1/8) = {perplexite([1 / 2, 1 / 4, 1 / 8]):.4f}   de dix tokens à 0,5 = {perplexite(dix):.4f}")
    assert math.isclose(perplexite([1 / 2, 1 / 4, 1 / 8]), 4) and math.isclose(perplexite(dix), 2)
    assert math.isclose(perplexite([1 / 8] * 5), 8)          # huit branches équiprobables
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
dix tokens à 0,5 : P = 0.000977   ln P = -6.931
perplexité de (1/2, 1/4, 1/8) = 4.0000   de dix tokens à 0,5 = 2.0000
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`log_vraisemblance` reçoit les probabilités que le modèle a données à chaque token réellement présent dans la séquence, chacune conditionnée par les tokens d'avant et par le contexte, et renvoie la somme de leurs logarithmes. Passer au logarithme transforme le produit de la formule en somme, ce qui évite un problème pratique : le produit de quelques centaines de probabilités devient si petit qu'un nombre flottant l'arrondit à zéro, alors que la somme des logarithmes reste un nombre ordinaire. La fonction refuse une probabilité nulle, dont le logarithme serait −∞.

`perplexite` divise cette somme par le nombre de tokens pour obtenir la perte moyenne par token, change le signe, puis prend l'exponentielle : le résultat se lit comme un nombre de choix équiprobables entre lesquels le modèle hésite en moyenne.

`main` vérifie les deux fiches. Dix tokens à 0,5 donnent une probabilité de séquence d'environ 0,000977 et une log-vraisemblance de −6,931, la fiche 23. Trois tokens vus avec les probabilités 1/2, 1/4 et 1/8 donnent une perplexité de 4, la moyenne géométrique de 2, 4 et 8, et cinq tokens à 1/8 donnent 8, les « huit branches équiprobables » de l'image de la fiche 32.

## Squelette algorithmique

```text
ALGORITHME Perplexité
ENTRÉES : modèle, contexte c, séquence x₁ … x_n
SORTIE  : log-vraisemblance et perplexité

  somme ← 0
  POUR t DE 1 À n FAIRE
      p ← probabilité que le modèle donne à xₜ sachant c et x₁ … xₜ₋₁       (une softmax)
      somme ← somme + ln p
  FIN POUR
  RETOURNER somme, exp(−somme / n)
```

**Complexité.** Un passage du modèle par token, mais tous les tokens d'une séquence connue peuvent être évalués en une seule passe parallèle grâce au masque causal ; la somme et l'exponentielle coûtent O(n). Comparer deux modèles n'a de sens qu'avec le même tokenizer, parce que n change avec le découpage.

**Du squelette au code.** La boucle est la somme de `log_vraisemblance`, et la dernière ligne est `perplexite`.

## Dans le cours

- [Étape 3 — Fondements de la softmax](<../../02-LLM-Softmax-et-Prompts/03-Fondements-Softmax-et-LLM.md>)
- [Étape 52 — Perplexité](<../../10-Evaluation/52-Perplexite-LLM.md>)
- [Étape 78 — Synthèse : les mathématiques de l'IA agentique](<../../14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md>)
