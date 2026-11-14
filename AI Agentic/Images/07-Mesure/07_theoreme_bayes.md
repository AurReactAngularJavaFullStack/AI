# Fiche 07 — Théorème de Bayes

> Image : `07_theoreme_bayes.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 51 — Spécificité, NPV, AUC](<../../10-Evaluation/51-Specificite-NPV-AUC.md>)

**Mettre à jour une croyance**

## Formule

$$
P(H \mid E) = \frac{P(E \mid H) \times P(H)}{P(E)}
$$

## Éléments

$$
H
$$

**H** : l'hypothèse, par exemple « la réponse est fausse ».

$$
E
$$

**E** : l'observation, par exemple une alerte d'un détecteur.

$$
P(H)
$$

**P(H)** : la probabilité avant l'observation, le taux de base.

$$
P(E \mid H)
$$

**P(E | H)** : la chance de voir E si H est vraie (la sensibilité du détecteur).

$$
P(E) = P(E \mid H)\,P(H) + P(E \mid \lnot H)\,P(\lnot H)
$$

**P(E)** : la chance de voir E dans tous les cas. **¬H** se lit « non H ». La formule des probabilités totales la calcule.

$$
P(H \mid E)
$$

**P(H | E)** : la croyance après l'observation.

## Ce que c'est

Bayes combine une fréquence initiale (le taux de base) et la valeur informative d'une preuve (le rapport entre la chance de la voir quand H est vraie et quand H est fausse).

## Effets et impacts

- Un détecteur sensible peut surtout produire des faux positifs si l'erreur est rare.
- Ignorer le taux de base surestime l'alerte.
- « Je suis sûr à 95 % » dit par un LLM n'est pas une probabilité calibrée (voir le score de Brier, fiche 20).

## Exemple chiffré

2 % des réponses d'un agent sont fausses. Un détecteur d'hallucination signale 95 % des réponses fausses, et 10 % des réponses justes (faux positifs).

$$
P(E) = 0{,}95 \times 0{,}02 + 0{,}10 \times 0{,}98 = 0{,}019 + 0{,}098 = 0{,}117
$$

$$
P(H \mid E) = \frac{0{,}95 \times 0{,}02}{0{,}117} = \frac{0{,}019}{0{,}117} \approx 0{,}162
$$

Quand l'alerte sonne, la réponse n'est fausse que dans 16 % des cas. 84 % des alertes sont de fausses alarmes, parce que les erreurs sont rares.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`bayes(p_h, p_e_si_h, p_e_si_non_h)`** — Cette fonction est le veilleur de nuit qui entend l'alarme sonner et se demande, avant de réveiller tout le monde, quelle est la vraie chance qu'il y ait un cambrioleur : elle reçoit le taux de base P(H), la sensibilité P(E | H) du détecteur et son taux de fausses alarmes P(E | non H), vérifie que ces trois nombres sont bien compris entre 0 et 1 et lève une `ValueError` sinon. Elle calcule ensuite P(E), la chance d'entendre l'alarme dans tous les cas, en ajoutant les alertes justifiées et les fausses alarmes, refuse par une seconde `ValueError` le cas où cette chance est nulle, puis renvoie un couple formé de la croyance mise à jour P(H | E) et de P(E) : 0,162 et 0,117 pour un détecteur qui repère 95 % des 2 % de réponses fausses et se trompe sur 10 % des justes.

**`main()`** — C'est le rapport de garde qui consigne les deux alertes de la famille Bayes : il appelle d'abord `bayes` avec l'exemple de cette fiche, 2 % d'erreurs, 95 % de détection et 10 % de fausses alarmes, imprime P(E) = 0,117 et P(H | E) = 0,162, et vérifie ces deux valeurs par un `assert`. Il passe ensuite à l'exemple des fiches 07a à 07d, 1 % d'erreurs, 90 % de détection et 5 % de fausses alarmes, imprime la probabilité qu'une alerte signale vraiment une erreur, 15,4 %, la contrôle à une décimale près, puis annonce que toutes les vérifications sont passées.

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
- [Étape 67 — Score de risque](<../../11-GardeFous/67-GardeFous-Formule-Score-de-Risque.md>)
- [Étape 78 — Synthèse : les mathématiques de l'IA agentique](<../../14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md>)
