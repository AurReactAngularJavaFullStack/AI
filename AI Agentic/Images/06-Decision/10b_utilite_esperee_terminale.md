# Fiche 10b_utilite_esperee_terminale — Utilité espérée, niveau terminale

> Image : `10b_utilite_esperee_terminale.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**Même espérance d'utilité, avec l'argmax**

## Ce que montre l'image

Fiche de niveau terminale, avec la même formule que 10a, l'ensemble Ω des résultats possibles et la règle de décision a\* = argmax EU(a). Un schéma « résultats possibles → balance → valeur moyenne pondérée », et une suite d'actions pour illustrer la planification.

**Ce que l'image ajoute :** la notation argmax. On ne garde pas la valeur maximale, mais l'action qui l'atteint.

## Formule

$$
\mathrm{EU}(a) = \sum_{o} P(o \mid a)\, U(o)
$$

$$
a^{*} = \arg\max_a \mathrm{EU}(a)
$$

## Éléments

$$
a
$$

**a** : l'action choisie.

$$
o
$$

**o** : un résultat possible.

$$
P(o \mid a)
$$

**P(o | a)** : la chance de o si l'on fait a.

$$
U(o)
$$

**U(o)** : l'utilité de ce résultat (gain ou coût déjà mis sur une échelle).

$$
\operatorname{EU}(a), \qquad a^{*} = \arg\max_{a} \operatorname{EU}(a)
$$

**EU(a)** : la moyenne pondérée. L'agent joue l'action a\* qui la rend la plus grande.

## Ce que c'est

Version terminale de `10a`. Le second cran, a\*, est l'action qui maximise la moyenne. Ce n'est pas l'action au meilleur cas, ni celle au pire cas.

## Effets et impacts

- Planifier, c'est comparer des EU sur une séquence, pas seulement sur le prochain clic.
- Si les probabilités P(o | a) sont inventées par le modèle et non mesurées, EU hérite de cette erreur.

## Exemple chiffré

Appeler l'outil : 70 % de chance d'un gain U = 10, 30 % d'un coût U = −5.

$$
\mathrm{EU}(\text{outil}) = 0{,}7 \times 10 + 0{,}3 \times (-5) = 7 - 1{,}5 = 5{,}5
$$

Ne rien faire : U = 0. L'agent appelle l'outil.

La fiche 10 écrit la même idée avec un bénéfice, un coût, un délai et un risque déjà séparés. Cette affiche les replie dans U(o).

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`utilite(benefice, cout, delai, risque, l_c, l_t, l_r)`** — Cette fonction est la feuille de calcul d'un trésorier qui ne connaît qu'une opération, la soustraction pondérée : elle reçoit un bénéfice moyen attendu, puis le coût, le délai et le risque d'un outil, avec trois coefficients λ_c, λ_t et λ_r fixés par défaut à 1, 2 et 50, et elle renvoie le bénéfice dont on a retranché chaque pénalité multipliée par son coefficient. C'est la forme de la fiche 10, et non celle de cette fiche, mais `main` l'utilise pour vérifier que l'outil A vaut 59 points et l'outil B exactement 0.

**`utilite_esperee(issues)`** — Celle-ci est le calcul d'espérance qu'un élève de terminale fait sur une loi de probabilité, posée comme un tableau à deux lignes, les valeurs en haut, les probabilités en bas : elle reçoit la liste des issues de l'action sous forme de couples (probabilité, utilité), vérifie que la somme des probabilités vaut 1, comme pour toute loi, et lève une `ValueError` dans le cas contraire. Elle renvoie ensuite la somme des produits probabilité × utilité, l'espérance EU(a) de la balance dessinée sur l'image : 0,7 × 10 + 0,3 × (−5) = 5,5 pour l'outil de l'exemple.

**`choisir(utilites)`** — Cette fonction est l'argmax de l'image mis en code, l'arbitre qui ne lève pas le score le plus haut mais le bras de celui qui l'a obtenu : elle reçoit un dictionnaire qui associe chaque action à son utilité, cherche la clé dont la valeur est la plus grande, ce qui donne le nom de l'action a\* et non le maximum lui-même, puis renvoie ce nom si l'utilité correspondante est strictement positive, sinon la chaîne « ne rien faire ». Entre l'outil à 5,5 et l'inaction à 0, elle renvoie donc le mot « outil ».

**`main()`** — C'est la copie corrigée qui reprend les deux exemples de la famille, l'un après l'autre : il calcule les utilités 59 et 0 des outils A et B de la fiche 10 et vérifie que `choisir` retient A, puis il calcule l'espérance de l'outil de cette fiche à partir des issues (0,7, 10) et (0,3, −5), imprime 5,5 et le choix qui en découle. Un `assert` contrôle que l'espérance vaut bien 5,5 et que l'argmax désigne l'outil plutôt que l'inaction, après quoi la ligne de succès s'affiche.

```python
"""Fiches 10, 10a, 10b — utilité espérée d'une action : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def utilite(benefice: float, cout: float, delai: float, risque: float,
            l_c: float = 1.0, l_t: float = 2.0, l_r: float = 50.0) -> float:
    """U(a) = E[B(a)] − λ_c C(a) − λ_t T(a) − λ_r R(a)  (fiche 10)."""
    return benefice - l_c * cout - l_t * delai - l_r * risque


def utilite_esperee(issues: list[tuple[float, float]]) -> float:
    """EU(a) = Σ_o P(o | a) U(o)  (fiches 10a et 10b)."""
    if not math.isclose(sum(p for p, _ in issues), 1.0):
        raise ValueError("les probabilités des issues doivent sommer à 1")
    return sum(p * u for p, u in issues)


def choisir(utilites: dict[str, float]) -> str:
    """L'action de plus grande utilité ; n'agir que si elle est positive."""
    meilleure = max(utilites, key=utilites.get)
    return meilleure if utilites[meilleure] > 0 else "ne rien faire"


def main() -> None:
    u_a, u_b = utilite(90, 20, 3, 0.1), utilite(95, 60, 10, 0.3)
    print(f"fiche 10 : U(A) = {u_a:.0f}   U(B) = {u_b:.0f}   choix : {choisir({'A': u_a, 'B': u_b})}")
    assert math.isclose(u_a, 59) and math.isclose(u_b, 0) and choisir({"A": u_a, "B": u_b}) == "A"
    eu = utilite_esperee([(0.7, 10), (0.3, -5)])
    print(f"fiches 10a/10b : EU(outil) = {eu}   choix : {choisir({'outil': eu, 'rien': 0.0})}")
    assert math.isclose(eu, 5.5) and choisir({"outil": eu, "rien": 0.0}) == "outil"
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
fiche 10 : U(A) = 59   U(B) = 0   choix : A
fiches 10a/10b : EU(outil) = 5.5   choix : outil
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

Le programme écrit les deux formes de l'utilité présentes dans la famille de fiches. `utilite` suit la fiche 10 : elle part du bénéfice moyen attendu et en retranche trois pénalités, le coût, le délai et le risque, chacune multipliée par un poids λ qui la convertit dans l'unité du bénéfice ; les poids par défaut sont ceux de l'exemple (1 par unité de coût, 2 par seconde, 50 par unité de risque). `utilite_esperee` suit les fiches 10a et 10b, qui replient tout dans l'utilité de chaque issue : elle vérifie que les probabilités des issues somment à 1, puis fait la moyenne des utilités pondérée par ces probabilités. `choisir` garde l'action de plus grande utilité, mais renvoie « ne rien faire » si cette utilité n'est pas positive : un outil n'est pas appelé parce qu'il existe.

`main` vérifie les deux exemples : l'outil A vaut 59 points et l'outil B 0, malgré un bénéfice plus élevé, parce qu'il coûte, tarde et risque trop, donc l'agent appelle A ; et l'outil des fiches 10a et 10b, qui rapporte 10 avec 70 % de chances et coûte 5 avec 30 % de chances, a une utilité espérée de 5,5, supérieure à celle de l'inaction.

## Squelette algorithmique

```text
ALGORITHME ChoisirUneAction
ENTRÉES : actions possibles, et pour chacune ses issues (probabilité, utilité) ou ses bénéfice, coût, délai, risque
SORTIE  : l'action à jouer, ou « ne rien faire »

  POUR CHAQUE action a FAIRE
      U(a) ← Σ_o P(o | a) × U(o)            (ou E[B(a)] − λ_c C(a) − λ_t T(a) − λ_r R(a))
  FIN POUR
  a* ← l'action de plus grande utilité
  SI U(a*) ≤ 0 ALORS RETOURNER « ne rien faire »
  RETOURNER a*
```

**Complexité.** O(Σ_a |issues(a)|) pour toutes les utilités, puis O(|A|) pour trouver le maximum. Le coût réel est ailleurs : estimer les probabilités et les utilités demande des mesures sur l'historique des outils.

**Du squelette au code.** La boucle correspond à `utilite_esperee` (ou à `utilite`), et les deux dernières lignes à `choisir`.

## Dans le cours

- [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)
- [Fiche 10 — Utilité espérée d'une action](<10_utilite_esperee.md>)
