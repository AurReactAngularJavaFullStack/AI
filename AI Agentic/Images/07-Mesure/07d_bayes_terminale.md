# Fiche 07d_bayes_terminale — Bayes, niveau terminale

> Image : `07d_bayes_terminale.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 51 — Spécificité, NPV, AUC](<../../10-Evaluation/51-Specificite-NPV-AUC.md>)

**Prior, vraisemblance, évidence, posterior**

## Ce que montre l'image

Fiche de niveau terminale, la plus propre de la série : la formule en notation A et B, les quatre termes définis dans quatre cases, une explication et trois usages. Une ligne de notation rappelle que P(X | Y) se lit « probabilité de X sachant Y ».

**Ce que l'image ajoute :** rien de nouveau sur le fond. C'est la version à recopier telle quelle en tête de feuille avant les exercices de `Demonstrations/07-Mesure/07_theoreme_bayes.md`.

## Formule

$$
P(H \mid E) = \frac{P(E \mid H)\, P(H)}{P(E)}
$$

## Éléments

$$
H
$$

**H** : l'hypothèse.

$$
E
$$

**E** : l'observation.

$$
P(H)
$$

**P(H)** : la croyance avant E, le taux de base.

$$
P(E \mid H)
$$

**P(E | H)** : la chance de voir E si H est vraie.

$$
P(E)
$$

**P(E)** : la chance de voir E dans tous les cas.

$$
P(H \mid E)
$$

**P(H | E)** : la croyance après l'observation.

## Ce que c'est

Même théorème que la fiche 07. On met à jour P(H) après avoir vu E.

## Effets et impacts

- Un détecteur sensible produit surtout des faux positifs quand l'erreur est rare.
- La formule ne dit rien si P(E) vaut 0.

## Exemple chiffré

1 % des réponses sont fausses. Le détecteur voit 90 % des erreurs et 5 % des réponses justes.

$$
P(\text{erreur} \mid \text{alerte}) = \frac{0{,}90 \times 0{,}01}{0{,}90 \times 0{,}01 + 0{,}05 \times 0{,}99} \approx 15{,}4\ \%
$$

L'alerte a l'air forte. Le taux de base la ramène à une chance sur six environ.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`bayes(p_h, p_e_si_h, p_e_si_non_h)`** — Cette fonction dessine, sans le montrer, l'arbre pondéré qu'un élève de terminale trace en marge de sa copie : elle reçoit la probabilité de la première branche, P(H), puis celles des deux branches qui mènent à E, P(E | H) sous H et P(E | non H) sous non H, et vérifie d'abord que ces trois nombres sont des probabilités, en levant une `ValueError` sinon. Elle parcourt ensuite les deux chemins qui aboutissent à E et additionne leurs produits, ce qui est la formule des probabilités totales, 0,90 × 0,01 + 0,05 × 0,99 = 0,0585 dans l'exemple de cette fiche, refuse par une seconde `ValueError` une évidence P(E) nulle, puis renvoie le posterior, le poids du chemin passant par H divisé par P(E), soit environ 15,4 %, accompagné de P(E).

**`main()`** — C'est le corrigé type qui traite les deux exercices de la série dans l'ordre : il résout d'abord celui de la fiche 07, 2 % d'erreurs, 95 % de détection et 10 % de fausses alarmes, imprime P(E) = 0,117 et P(H | E) = 0,162, et les vérifie par un `assert`. Il résout ensuite celui des fiches 07a à 07d, imprime la probabilité 15,4 % qu'une alerte corresponde à une vraie erreur, contrôle ce résultat arrondi à une décimale, puis inscrit au bas de la copie que toutes les vérifications sont passées.

```python
"""Fiches 07, 07a à 07d — théorème de Bayes : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def bayes(p_h: float, p_e_si_h: float, p_e_si_non_h: float) -> tuple[float, float]:
    """P(H | E) = P(E | H) P(H) / P(E), avec P(E) = P(E | H) P(H) + P(E | non H) P(non H)."""
    for p in (p_h, p_e_si_h, p_e_si_non_h):
        if not 0 <= p <= 1:
            raise ValueError("une probabilité est dans [0, 1]")
    p_e = p_e_si_h * p_h + p_e_si_non_h * (1 - p_h)
    if p_e == 0:
        raise ValueError("l'observation E est impossible")
    return p_e_si_h * p_h / p_e, p_e


def main() -> None:
    post, p_e = bayes(0.02, 0.95, 0.10)                      # fiche 07
    print(f"fiche 07 : P(E) = {p_e:.3f}   P(H | E) = {post:.3f}")
    assert math.isclose(p_e, 0.117) and round(post, 3) == 0.162
    post2, _ = bayes(0.01, 0.90, 0.05)                       # fiches 07a à 07d
    print(f"fiches 07a à 07d : P(erreur | alerte) = {100 * post2:.1f} %")
    assert round(100 * post2, 1) == 15.4
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
fiche 07 : P(E) = 0.117   P(H | E) = 0.162
fiches 07a à 07d : P(erreur | alerte) = 15.4 %
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`bayes` reçoit le taux de base P(H), la sensibilité P(E | H) (la chance de voir l'alerte quand l'hypothèse est vraie) et le taux de fausses alarmes P(E | non H). Elle vérifie que ces trois nombres sont bien des probabilités, puis calcule P(E) par la formule des probabilités totales : on voit l'alerte soit parce que H est vraie et que le détecteur la repère, soit parce que H est fausse et que le détecteur se trompe. Elle refuse le cas où P(E) vaut zéro, car on ne peut pas conditionner sur un événement impossible, et renvoie enfin le quotient de Bayes, avec P(E) pour qu'on puisse le relire.

`main` vérifie les deux exemples de la famille. Avec 2 % de réponses fausses, un détecteur qui en repère 95 % et 10 % de fausses alarmes, P(E) vaut 0,117 et une alerte ne signale une vraie erreur que dans 16,2 % des cas. Avec 1 % d'erreurs, 90 % de détection et 5 % de fausses alarmes, l'exemple des fiches 07a à 07d, la probabilité tombe à 15,4 %, environ une chance sur six : un détecteur qui paraît fiable produit surtout de fausses alarmes quand l'erreur est rare.

## Squelette algorithmique

```text
ALGORITHME MettreÀJourUneCroyance
ENTRÉES : taux de base P(H), sensibilité P(E | H), taux de fausses alarmes P(E | ¬H)
SORTIE  : P(H | E), la croyance après avoir vu E

  P(E) ← P(E | H) × P(H) + P(E | ¬H) × (1 − P(H))
  SI P(E) = 0 ALORS ERREUR « observation impossible »
  RETOURNER P(E | H) × P(H) / P(E)

USAGE : décider si une alerte justifie une escalade, en comparant P(H | E) à un seuil.
```

**Complexité.** O(1) : deux multiplications, une addition et une division. Avec plusieurs observations indépendantes, on répète la mise à jour en prenant la croyance obtenue comme nouveau taux de base : O(k) pour k observations.

**Du squelette au code.** La première ligne est le calcul de `p_e`, la garde est le test `if p_e == 0`, et le quotient est la valeur renvoyée par `bayes`.

## Dans le cours

- [Étape 51 — Spécificité, NPV, AUC](<../../10-Evaluation/51-Specificite-NPV-AUC.md>)
- [Fiche 07 — Théorème de Bayes](<07_theoreme_bayes.md>)
