# Fiche 10a_utilite_esperee_eu — Utilité espérée

> Image : `10a_utilite_esperee_eu.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**La moyenne des résultats, pondérée par leur chance**

## Ce que montre l'image

Affiche « L'utilité espérée (EU) ». La formule EU(a) = Σ sur o de P(o | a) U(o), où o est un résultat possible et a l'action choisie. P(o | a) est la probabilité du résultat si l'on choisit a ; U(o) son utilité, bénéfice ou coût. Trois usages : décider sous incertitude, planifier, choisir l'action a\* qui maximise EU.

**Différence avec la fiche 10 :** l'image donne la forme générale, par résultats possibles. La fiche 10 en tire une version d'ingénieur : bénéfice attendu moins coût, temps et risque pondérés. Le passage de l'une à l'autre est démontré dans `Demonstrations/06-Decision/10_utilite_esperee.md` (démonstration 1).

## Formule

$$
\mathrm{EU}(a) = \sum_{o} P(o \mid a)\, U(o)
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

L'utilité espérée d'une action est la valeur moyenne de ses résultats possibles. L'agent ne connaît pas l'avenir. Il choisit l'action dont cette moyenne est la plus haute.

## Effets et impacts

- Elle compare des actions dont les conséquences sont incertaines.
- Elle ne voit que ce qui est dans U. Un risque non noté est un risque ignoré.
- La fiche 10 est la version « coût, délai, risque » utilisée pour décider d'un outil.

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

**`utilite(benefice, cout, delai, risque, l_c, l_t, l_r)`** — Cette fonction est la version d'ingénieur de la fiche 10, celle d'un chef de chantier qui calcule le solde d'une intervention avant de l'autoriser : elle reçoit un bénéfice moyen, un coût, un délai et un risque déjà séparés, ainsi que trois poids λ_c, λ_t et λ_r, qui valent par défaut 1, 2 et 50, et elle renvoie le bénéfice diminué du coût, du délai et du risque, chacun multiplié par son poids. Cette affiche replie tout cela dans U(o), mais `main` s'en sert pour vérifier l'exemple voisin, où l'outil A vaut 59 points et l'outil B exactement 0.

**`utilite_esperee(issues)`** — Voici la formule de cette affiche, racontée comme le calcul d'un capitaine qui hésite à prendre la mer en lisant le bulletin météo : elle reçoit la liste des issues possibles de l'action, chacune donnée par un couple (probabilité, utilité), contrôle que les probabilités forment bien un tout égal à 1 et lève une `ValueError` si ce n'est pas le cas, puis additionne chaque utilité multipliée par sa chance de se produire. Elle renvoie EU(a), la moyenne pondérée des résultats : pour l'outil de l'exemple, 70 % de chances d'un gain de 10 et 30 % d'un coût de 5 donnent 7 − 1,5 = 5,5.

**`choisir(utilites)`** — Cette fonction est le capitaine qui, une fois les bulletins lus, donne l'ordre de partir ou de rester au port : elle reçoit un dictionnaire qui associe un nom d'action à son utilité, retient l'action dont l'utilité est la plus grande, c'est-à-dire l'action a\* de l'affiche, et renvoie son nom si cette utilité est strictement positive, sinon la chaîne « ne rien faire ». Face à l'outil à 5,5 et à l'inaction à 0, elle renvoie l'outil, et elle refuserait d'agir si toutes les options avaient une utilité nulle ou négative.

**`main()`** — C'est le tableau de bord qui fait tourner les deux exemples de la famille : il évalue d'abord les outils A et B de la fiche 10 avec `utilite`, imprime 59 et 0 et vérifie que `choisir` désigne A, puis il calcule l'utilité espérée de l'outil de cette affiche avec les issues (0,7, 10) et (0,3, −5). Il imprime 5,5, vérifie par un `assert` que cette valeur est la bonne et que l'outil l'emporte sur l'inaction, puis termine par la ligne qui annonce que toutes les vérifications sont passées.

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
