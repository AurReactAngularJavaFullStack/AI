# Fiche 32 — Perplexité

> Image : `32_perplexite.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 52 — Perplexité](<../../10-Evaluation/52-Perplexite-LLM.md>)

**Entre combien de tokens le modèle hésite**

## Formule

$$
PPL = \exp\left( -\frac{1}{n} \times \sum_{t=1}^{n} \ln P(x_t \mid x_{<t}, c) \right)
$$

## Éléments

$$
n
$$

**n** : le nombre de tokens.

$$
P(x_t \mid x_{<t}, c)
$$

**P(xₜ | x<ₜ, c)** : la probabilité du token vu, sachant le passé et le contexte (fiche 23).

$$
\ln
$$

**ln** : le logarithme naturel.

$$
\exp
$$

**exp** : remet la moyenne des logarithmes à l'échelle d'un « nombre de choix ».

$$
PPL
$$

**PPL** : la perplexité. Plus basse est meilleure ; 1 est le minimum.

## Ce que c'est

La perplexité est l'exponentielle de la perte moyenne (l'entropie croisée, fiche 06). PPL = 2 veut dire que le modèle hésite autant qu'entre deux tokens équiprobables. PPL = 8 : autant qu'entre huit.

## Effets et impacts

- Elle compare des modèles seulement avec le même tokenizer et le même texte.
- Une perplexité basse n'est pas une réponse vraie.
- Elle ne mesure ni la fidélité aux sources, ni le succès d'une tâche d'agent.

## Exemple chiffré

Trois tokens vus avec les probabilités 1/2, 1/4 et 1/8 :

$$
-\frac{1}{3}\left(\ln\frac{1}{2} + \ln\frac{1}{4} + \ln\frac{1}{8}\right) = \frac{0{,}693 + 1{,}386 + 2{,}079}{3} \approx 1{,}386
$$

$$
PPL = e^{1{,}386} = 4
$$

C'est la moyenne géométrique de 2, 4 et 8 : le modèle hésite en moyenne comme entre quatre tokens.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`log_vraisemblance(probas)`** — Cette fonction tient le carnet d'un randonneur qui note, à chaque carrefour, la probabilité d'avoir choisi le bon sentier ; au lieu de multiplier ces fractions de plus en plus minuscules, elle additionne leurs logarithmes. Elle reçoit la liste des probabilités conditionnelles des tokens, lève `ValueError` si l'une n'appartient pas à ]0, 1], et rend la somme des logarithmes népériens, une valeur négative ou nulle. Pour les trois tokens de cette fiche, 1/2, 1/4 et 1/8, cette somme vaut −(0,693 + 1,386 + 2,079), soit environ −4,159.

**`perplexite(probas)`** — Celle-ci répond à la question que se pose le randonneur au bout du chemin : entre combien de sentiers ai-je hésité, en moyenne, à chaque carrefour ? Elle reçoit la même liste, divise la log-vraisemblance rendue par `log_vraisemblance` par le nombre de tokens, change le signe et prend l'exponentielle. Elle rend la perplexité, la moyenne géométrique des inverses des probabilités : 4 pour 1/2, 1/4 et 1/8, l'exemple de cette fiche, 2 pour dix tokens à 0,5 et 8 pour cinq tokens à 1/8.

**`main()`** — C'est le guide qui relit le carnet et vérifie les moyennes. Il ne reçoit rien ; il calcule d'abord la log-vraisemblance de dix tokens à 0,5, de la fiche 23, imprime P ≈ 0,000977 et ln P ≈ −6,931 et les contrôle par `assert`. Il imprime ensuite les perplexités 4,0000 pour (1/2, 1/4, 1/8) et 2,0000 pour dix tokens à 0,5, les vérifie avec `math.isclose`, puis contrôle qu'une perplexité de 8 correspond bien à huit branches équiprobables ; il ne rend rien.

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

- [Étape 52 — Perplexité](<../../10-Evaluation/52-Perplexite-LLM.md>)
- [Étape 62 — Perplexité, version métier](<../../10-Evaluation/62-Evaluation-Formule-Perplexite.md>)
- [Étape 23 — Score hybride](<../../05-RAG/23-RAG-Formule-Score-Hybride.md>)
