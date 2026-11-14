# Fiche 21 — Entropie

> Image : `21_entropie.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 52 — Perplexité](<../../10-Evaluation/52-Perplexite-LLM.md>)

**Mesurer l'incertitude d'une distribution**

## Formule

$$
H(P) = -\sum_{i} p_i \times \ln(p_i)
$$

## Éléments

$$
P
$$

**P** : une distribution discrète.

$$
p_i
$$

**pᵢ** : la probabilité du cas i.

$$
\ln
$$

**ln** : le logarithme naturel ; l'unité est le nat.

$$
-
$$

**Le signe moins** : ln p ≤ 0, donc l'entropie reste positive.

$$
0 \ln 0 = 0
$$

**Par convention**, un cas de probabilité nulle ne compte pas.

## Ce que c'est

Une distribution concentrée sur un seul choix a une entropie faible. Une distribution étalée a une entropie haute. Deux choix équiprobables valent ln 2. Sur n choix, l'entropie maximale est ln n, atteinte pour la distribution uniforme.

## Effets et impacts

- Elle décrit la dispersion d'un routeur ou du prochain token.
- L'entropie des tokens n'est pas l'incertitude factuelle : un modèle peut être sûr d'une réponse fausse, ou hésiter entre deux formulations justes.

## Exemple chiffré

$$
H(0{,}5\ ;\ 0{,}5) = \ln 2 \approx 0{,}693
$$

$$
H(0{,}9\ ;\ 0{,}1) = -(0{,}9 \ln 0{,}9 + 0{,}1 \ln 0{,}1) \approx 0{,}095 + 0{,}230 = 0{,}325
$$

$$
H(\text{uniforme sur 4}) = \ln 4 \approx 1{,}386
$$

Plus la distribution est piquée, plus l'entropie baisse.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`entropie(p)`** — Cette fonction est le sismographe de l'hésitation : elle reçoit une distribution sous forme de liste de probabilités, vérifie qu'elle est bien positive et que sa somme vaut 1, et lève une `ValueError` dans le cas contraire, puis additionne pᵢ × ln pᵢ sur les seules probabilités non nulles, appliquant ainsi la convention 0 ln 0 = 0 qui évite à `math.log(0)` de lever une erreur. Elle change enfin le signe du total, chaque logarithme étant négatif ou nul, et renvoie une entropie positive ou nulle exprimée en nats : ln 2 ≈ 0,693 pour deux cas équiprobables, 0,325 pour la distribution piquée (0,9 ; 0,1), ln 4 ≈ 1,386 pour quatre cas équiprobables.

**`main()`** — C'est la tournée d'inspection qui fait passer le sismographe sur toutes les distributions de la famille : il mesure d'abord les trois cas de cette fiche et vérifie par un `assert` qu'ils valent ln 2, 0,325 et ln 4, puis le dé équitable des fiches 21a à 21c, 1,792 nat, et le dé pipé qui tombe toujours sur 6, dont l'entropie nulle s'imprime `-0.0` parce que le signe moins s'applique à un total nul. Il termine par la politique de la fiche 21d, qui joue sa première action neuf fois sur dix, vérifie que son entropie de 0,325 reste inférieure aux 0,693 d'une politique qui hésite, et imprime la ligne de succès.

```python
"""Fiches 21, 21a à 21d — entropie : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def entropie(p: list[float]) -> float:
    """H(P) = −Σ pᵢ ln pᵢ, en nats ; convention 0 ln 0 = 0."""
    if not math.isclose(sum(p), 1) or any(x < 0 for x in p):
        raise ValueError("P doit être une distribution")
    return -sum(x * math.log(x) for x in p if x > 0)


def main() -> None:
    h2, h91, h4 = entropie([0.5, 0.5]), entropie([0.9, 0.1]), entropie([0.25] * 4)
    print(f"(½, ½) : {h2:.3f}   (0,9 ; 0,1) : {h91:.3f}   uniforme sur 4 : {h4:.3f}")
    assert math.isclose(h2, math.log(2)) and round(h91, 3) == 0.325 and math.isclose(h4, math.log(4))
    de, pipe = entropie([1 / 6] * 6), entropie([0, 0, 0, 0, 0, 1])          # fiches 21a à 21c
    print(f"dé équitable : {de:.3f} nat   dé pipé : {pipe}")
    assert round(de, 3) == 1.792 and pipe == 0
    print(f"fiche 21d : politique (0,9 ; 0,1) : {entropie([0.9, 0.1]):.3f} < ln 2 = {math.log(2):.3f}")
    assert entropie([0.9, 0.1]) < entropie([0.5, 0.5])
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
(½, ½) : 0.693   (0,9 ; 0,1) : 0.325   uniforme sur 4 : 1.386
dé équitable : 1.792 nat   dé pipé : -0.0
fiche 21d : politique (0,9 ; 0,1) : 0.325 < ln 2 = 0.693
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`entropie` vérifie que la liste reçue est une distribution (positive, de somme 1), puis additionne pᵢ × ln pᵢ sur les cas de probabilité non nulle et change le signe du total. Ignorer les cas de probabilité nulle applique la convention 0 ln 0 = 0, qui est la limite de p ln p quand p tend vers 0 ; sans elle, `math.log(0)` lèverait une erreur. Comme chaque ln pᵢ est négatif ou nul, le signe moins rend l'entropie positive ou nulle, et l'unité est le nat parce qu'on utilise le logarithme naturel.

`main` vérifie les exemples de toute la famille : deux cas équiprobables valent ln 2 ≈ 0,693, la distribution (0,9 ; 0,1) seulement 0,325, et quatre cas équiprobables ln 4 ≈ 1,386. Les fiches 21a à 21c comparent deux dés : le dé équitable vaut ln 6 ≈ 1,792 nat, le dé pipé qui tombe toujours sur 6 vaut 0, aucune surprise. La fiche 21d applique la même formule à une politique : jouer la première action 9 fois sur 10 donne 0,325, moins que les 0,693 d'une politique qui hésite, ce qui sert de bonus d'exploration dans l'objectif d'apprentissage.

## Squelette algorithmique

```text
ALGORITHME Entropie
ENTRÉE  : distribution p₁ … p_n
SORTIE  : H ≥ 0, au plus ln n

  H ← 0
  POUR i DE 1 À n FAIRE
      SI pᵢ > 0 ALORS H ← H − pᵢ × ln pᵢ
  FIN POUR
  RETOURNER H

USAGE (fiche 21d) : objectif d'une politique ← retour moyen + λ × H(π(· | s)), pour ne pas s'enfermer trop tôt dans une action.
```

**Complexité.** Une passe sur les n cas : O(n). Pour un modèle de langage, l'entropie du prochain token se calcule à partir de la softmax, donc en O(|V|) par position.

**Du squelette au code.** La boucle et son test sont la somme `sum(x * math.log(x) for x in p if x > 0)` de `entropie`, précédée de la vérification que P est une distribution.

## Dans le cours

- [Étape 52 — Perplexité](<../../10-Evaluation/52-Perplexite-LLM.md>)
- [Étape 78 — Synthèse : les mathématiques de l'IA agentique](<../../14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md>)
