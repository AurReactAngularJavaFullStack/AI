# Fiche 07c_bayes_theorem — Bayes' theorem

> Image : `07c_bayes_theorem.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 51 — Spécificité, NPV, AUC](<../../10-Evaluation/51-Specificite-NPV-AUC.md>)

**La même mise à jour, en anglais**

## Ce que montre l'image

Affiche en anglais, sur fond sombre. Les mêmes quatre termes (posterior, likelihood, prior, marginal) et cinq usages, dont « foundation for many learning and inference systems » (filtrage, lissage). En bas, une boucle : observer une preuve → mettre à jour la croyance → décider et agir → nouvelle preuve.

**Ce que l'image ajoute à la fiche 07 :** la boucle de mise à jour. La croyance a posteriori d'aujourd'hui devient l'a priori de demain : c'est ce qui permet d'enchaîner deux détecteurs dans `Demonstrations/07-Mesure/07_theoreme_bayes.md`.

**Défaut de l'image :** le numérateur est entouré de crochets inutiles.

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

**`bayes(p_h, p_e_si_h, p_e_si_non_h)`** — Cette fonction est le pilote d'un navire qui corrige sa position chaque fois qu'un phare apparaît, et dont la position corrigée sert de point de départ au phare suivant, exactement la boucle dessinée au bas de l'affiche : elle reçoit le prior P(H), la likelihood P(E | H) et la chance de voir la même preuve quand l'hypothèse est fausse, P(E | non H), vérifie que ces trois nombres sont des probabilités et lève une `ValueError` si l'un sort de [0, 1]. Elle calcule la probabilité marginale P(E), lève une autre `ValueError` si elle est nulle, puis renvoie un couple formé du posterior P(H | E) et de P(E), environ 0,154 et 0,0585 dans l'exemple de cette fiche ; le programme ne fait qu'un tour de boucle, mais on pourrait rappeler la fonction en lui donnant ce posterior comme nouveau prior pour enchaîner un second détecteur.

**`main()`** — C'est le journal de bord qui note deux corrections de cap successives, chacune indépendante de l'autre : il calcule d'abord l'exemple de la fiche 07, imprime P(E) = 0,117 et un posterior de 0,162, et les vérifie par un `assert`. Il calcule ensuite l'exemple commun aux fiches 07a à 07d, 1 % d'erreurs, 90 % de détection et 5 % de fausses alarmes, imprime le posterior en pourcentage, 15,4 %, le contrôle à une décimale près, puis termine par la ligne qui annonce que toutes les vérifications sont passées.

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
