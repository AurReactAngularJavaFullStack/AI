# Fiche 07b_theoreme_bayes_affiche — Théorème de Bayes, affiche

> Image : `07b_theoreme_bayes_affiche.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 51 — Spécificité, NPV, AUC](<../../10-Evaluation/51-Specificite-NPV-AUC.md>)

**L'affiche de la fiche 07**

## Ce que montre l'image

Affiche « Théorème de Bayes en IA agentique », avec les lettres A et B au lieu de H et E. Les quatre termes sont nommés autour de la formule : a posteriori (croyance mise à jour), vraisemblance, a priori (croyance initiale), probabilité marginale. Un schéma « croyance actuelle → nouvelle preuve → croyance mise à jour », et quatre usages : raisonnement probabiliste, révision des croyances, planification sous incertitude, décisions avec une information incomplète.

**Défaut de l'image :** un crochet « ] » parasite termine le numérateur.

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

**`bayes(p_h, p_e_si_h, p_e_si_non_h)`** — Cette fonction est le juré d'un procès qui entre au tribunal avec une opinion de départ et la révise à mesure que les pièces arrivent : elle reçoit l'a priori P(H), la vraisemblance P(E | H) et la chance de voir la même pièce si l'accusé est innocent, P(E | non H), contrôle que chacune est une probabilité entre 0 et 1 et lève une `ValueError` sinon. Elle reconstitue ensuite la probabilité marginale de l'affiche, P(E), en additionnant les deux façons de voir apparaître la pièce, et, comme la formule ne dit rien quand P(E) vaut 0, elle lève dans ce cas une seconde `ValueError` ; autrement, elle renvoie l'a posteriori P(H | E) et P(E), soit environ 0,154 et 0,0585 pour 1 % d'erreurs, 90 % de détection et 5 % de fausses alarmes.

**`main()`** — C'est le greffier qui relit les deux verdicts de la famille Bayes devant la cour : il fait calculer à `bayes` l'exemple de la fiche 07, imprime P(E) = 0,117 et l'a posteriori 0,162, puis les vérifie par un `assert`. Il passe à l'exemple de cette affiche, imprime la probabilité qu'une alerte corresponde à une vraie erreur, 15,4 %, et vérifie ce pourcentage arrondi à une décimale, ce qui montre qu'un a priori de 1 % suffit à ramener une alerte d'apparence sûre à une chance sur six environ, avant d'imprimer la ligne de succès.

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
