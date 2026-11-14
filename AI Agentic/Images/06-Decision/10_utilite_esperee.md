# Fiche 10 — Utilité espérée d'une action

> Image : `10_utilite_esperee.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

**Appeler un outil seulement s'il vaut le coup**

## Formule

$$
U(a) = \mathbb{E}[B(a)] - \lambda_c\, C(a) - \lambda_t\, T(a) - \lambda_r\, R(a)
$$

**Correction par rapport à l'image.** L'image écrit « λt T(a) » et « λ_r^r R(a) ». Les trois poids s'écrivent simplement λ_c, λ_t et λ_r.

## Éléments

$$
a
$$

**a** : l'action ou l'outil candidat.

$$
\mathbb{E}[B(a)]
$$

**𝔼[B(a)]** : le bénéfice moyen attendu (fiche 22 pour l'espérance).

$$
C(a)
$$

**C(a)** : le coût (tokens, appel payant).

$$
T(a)
$$

**T(a)** : le délai.

$$
R(a)
$$

**R(a)** : le risque (probabilité ou gravité d'un effet indésirable).

$$
\lambda_c,\ \lambda_t,\ \lambda_r
$$

**λ (lambda)** : les poids de ces pénalités. Ils convertissent coût, délai et risque dans l'unité du bénéfice.

## Ce que c'est

L'utilité compare le gain attendu aux pénalités. L'agent choisit l'action dont U est la plus haute, ou n'agit pas si toutes les U sont négatives.

## Effets et impacts

- Un outil n'est pas appelé parce qu'il existe.
- Cette règle limite les appels inutiles, la latence et les actions risquées.
- De mauvais poids font soit un agent trop timide, soit un agent qui agit trop souvent.

## Exemple chiffré

Poids : λ_c = 1, λ_t = 2 par seconde, λ_r = 50. Deux outils, en points :

$$
U(\text{A}) = 90 - 1 \times 20 - 2 \times 3 - 50 \times 0{,}1 = 90 - 20 - 6 - 5 = 59
$$

$$
U(\text{B}) = 95 - 1 \times 60 - 2 \times 10 - 50 \times 0{,}3 = 95 - 60 - 20 - 15 = 0
$$

B rapporte un peu plus, mais coûte, traîne et risque trop : l'agent appelle A.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`utilite(benefice, cout, delai, risque, l_c, l_t, l_r)`** — Cette fonction est le contrôleur de gestion qui examine un devis avant de signer : elle reçoit le bénéfice moyen attendu d'un outil, son coût, son délai en secondes et son risque, ainsi que trois poids λ qui valent par défaut 1, 2 et 50 et qui convertissent chaque pénalité dans l'unité du bénéfice. Elle retranche du bénéfice le coût fois λ_c, le délai fois λ_t et le risque fois λ_r, puis renvoie le solde, l'utilité U(a) : 90 − 20 − 6 − 5 = 59 points pour l'outil A, et 95 − 60 − 20 − 15 = 0 pour l'outil B, qui rapporte davantage mais coûte, traîne et risque trop.

**`utilite_esperee(issues)`** — Celle-ci est l'assureur qui raisonne sur les scénarios plutôt que sur une seule estimation : elle reçoit la liste des issues possibles d'une action, chacune sous la forme d'un couple (probabilité, utilité), vérifie d'abord que les probabilités font bien 1 au total et lève une `ValueError` dans le cas contraire, puis multiplie chaque utilité par sa probabilité et additionne le tout. Elle renvoie l'utilité espérée, la moyenne pondérée qu'utilisent les fiches 10a et 10b : 0,7 × 10 + 0,3 × (−5) = 5,5 pour un outil qui réussit sept fois sur dix et coûte 5 points quand il échoue.

**`choisir(utilites)`** — Cette fonction joue l'huissier qui ouvre ou non la porte à l'action : elle reçoit un dictionnaire qui associe à chaque nom d'action son utilité, repère celle dont l'utilité est la plus grande, puis renvoie son nom seulement si cette utilité est strictement positive, et sinon la chaîne « ne rien faire ». C'est la règle de la fiche, un outil n'est pas appelé parce qu'il existe : entre A à 59 et B à 0, elle renvoie A, et si toutes les utilités étaient nulles ou négatives, l'agent s'abstiendrait.

**`main()`** — C'est la réunion de décision où l'on passe en revue les deux exemples de la famille : il calcule l'utilité des outils A et B de cette fiche avec les poids par défaut, imprime 59 et 0 et le choix A, et vérifie le tout par un `assert`. Il calcule ensuite l'utilité espérée 5,5 de l'outil des fiches 10a et 10b, la compare à l'inaction, notée 0, contrôle que `choisir` retient bien l'outil, puis imprime la ligne de succès.

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
- [Étape 78 — Synthèse : les mathématiques de l'IA agentique](<../../14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md>)
