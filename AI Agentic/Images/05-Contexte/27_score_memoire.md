# Fiche 27 — Score de mémoire

> Image : `27_score_memoire.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 16 — Décroissance d'un souvenir](<../../04-Contexte-Similarite-et-Memoire/16-Memoire-Formule-Decroissance-Temporelle.md>)

**Quoi réinjecter dans le contexte**

## Formule

$$
\operatorname{score}(m) = \alpha \times \operatorname{récence}(m) + \beta \times \operatorname{importance}(m) + \gamma \times \operatorname{pertinence}(m, q)
$$

## Éléments

$$
m
$$

**m** : un souvenir.

$$
q
$$

**q** : la question ou la tâche en cours.

$$
\operatorname{récence}(m) \in [0, 1]
$$

**récence(m)** : la fraîcheur, qui décroît avec le temps (étape 16).

$$
\operatorname{importance}(m) \in [0, 1]
$$

**importance(m)** : le poids du souvenir.

$$
\operatorname{pertinence}(m, q)
$$

**pertinence(m, q)** : la proximité avec la tâche, souvent un cosinus (fiche 03).

$$
\alpha,\ \beta,\ \gamma
$$

**α, β, γ (alpha, bêta, gamma)** : les poids des trois composantes.

## Ce que c'est

La mémoire longue ne se relit pas en entier. On classe les souvenirs et on n'injecte que les mieux scorés.

## Effets et impacts

- Si une composante n'est pas à la même échelle, elle écrase les autres.
- Une importance notée par le modèle n'est pas calibrée.
- Oublier dans le classement n'efface pas la donnée : un droit à l'effacement exige une vraie suppression.

## Exemple chiffré

Poids α = 0,3, β = 0,3, γ = 0,4. Souvenir A récent mais peu utile, souvenir B ancien mais important et pertinent :

$$
\operatorname{score}(A) = 0{,}3 \times 0{,}9 + 0{,}3 \times 0{,}3 + 0{,}4 \times 0{,}5 = 0{,}56
$$

$$
\operatorname{score}(B) = 0{,}3 \times 0{,}2 + 0{,}3 \times 0{,}9 + 0{,}4 \times 0{,}85 = 0{,}67
$$

B passe devant. Si l'importance était notée de 1 à 10 au lieu de 0 à 1, elle écraserait les deux autres termes.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`score(recence, importance, pertinence, poids)`** — Cette fonction est la bibliothécaire qui décide quels carnets de souvenirs remonter de la réserve jusqu'au bureau de l'agent : elle reçoit la récence, l'importance et la pertinence d'un souvenir, plus un triplet de poids qui vaut par défaut 0,3, 0,3 et 0,4, et commence par vérifier que les trois composantes sont toutes comprises entre 0 et 1. Si l'une d'elles sort de cette échelle, elle lève une `ValueError` qui demande de normaliser d'abord, car une note sur 10 écraserait les deux autres ; sinon elle déballe les poids α, β et γ et renvoie la somme pondérée α × récence + β × importance + γ × pertinence, le score qui sert à classer les souvenirs avant de les réinjecter dans le contexte.

**`main()`** — C'est l'examinateur qui met deux souvenirs face à face : il calcule le score du souvenir A, très récent (0,9) mais peu important (0,3) et moyennement pertinent (0,5), puis celui du souvenir B, ancien (0,2) mais important (0,9) et pertinent (0,85), imprime les deux valeurs et vérifie par un `assert` qu'elles valent 0,56 et 0,67 et que B passe bien devant. Il tente ensuite d'appeler `score` avec une importance de 9, notée comme sur une échelle de 1 à 10, et exige que la fonction la refuse ; ce n'est qu'après ce refus qu'il imprime la ligne de succès.

```python
"""Fiche 27 — score de mémoire : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def score(recence: float, importance: float, pertinence: float, poids=(0.3, 0.3, 0.4)) -> float:
    """score(m) = α récence(m) + β importance(m) + γ pertinence(m, q), composantes dans [0, 1]."""
    if not all(0 <= x <= 1 for x in (recence, importance, pertinence)):
        raise ValueError("chaque composante doit être dans [0, 1] : normaliser d'abord")
    a, b, g = poids
    return a * recence + b * importance + g * pertinence


def main() -> None:
    sa, sb = score(0.9, 0.3, 0.5), score(0.2, 0.9, 0.85)
    print(f"souvenir A : {sa:.2f}   souvenir B : {sb:.2f}   B passe devant : {sb > sa}")
    assert math.isclose(sa, 0.56) and math.isclose(sb, 0.67) and sb > sa
    try:
        score(0.2, 9, 0.85)                       # importance notée de 1 à 10 : refusée
        raise AssertionError("une composante hors échelle aurait dû être refusée")
    except ValueError:
        pass
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
souvenir A : 0.56   souvenir B : 0.67   B passe devant : True
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`score` vérifie d'abord que les trois composantes sont toutes entre 0 et 1, puis calcule la somme pondérée de la fiche avec les poids α = 0,3, β = 0,3 et γ = 0,4. La vérification n'est pas un détail : si l'importance était notée de 1 à 10 alors que la récence et la pertinence restent entre 0 et 1, elle écraserait les deux autres termes, et le classement ne dépendrait presque plus que d'elle. La fonction refuse donc une composante hors échelle, ce qui oblige à normaliser les signaux avant de les mélanger.

`main` vérifie l'exemple de la fiche : le souvenir A, très récent mais peu important et peu pertinent, obtient 0,56, et le souvenir B, ancien mais important et pertinent pour la question, obtient 0,67 et passe devant. Le programme vérifie aussi qu'une importance notée 9 sur une échelle de 1 à 10 est bien refusée. L'étape 17 du cours ajoute la normalisation min-max qui ramène automatiquement chaque signal dans [0, 1].

## Squelette algorithmique

```text
ALGORITHME RappelerLesSouvenirs
ENTRÉES : souvenirs (âge, importance, vecteur), question q, poids α, β, γ, demi-vie h, k
SORTIE  : les k souvenirs à réinjecter dans le contexte

  POUR CHAQUE souvenir m FAIRE
      récence ← 0,5^(âge / h)
      pertinence ← cos(q, m.vecteur)
      ramener importance, récence et pertinence dans [0 ; 1]      (min-max sur les candidats)
      score(m) ← α × récence + β × importance + γ × pertinence
  FIN POUR
  RETOURNER les k meilleurs scores
```

**Complexité.** O(n × d) pour les cosinus de n souvenirs de dimension d, O(n) pour les autres composantes et les normalisations, et O(n log k) pour garder les k meilleurs.

**Du squelette au code.** La ligne du score est la fonction `score`, avec sa garde sur l'échelle des composantes ; le calcul de la récence et de la pertinence est fait aux étapes 16 et 17.

## Dans le cours

- [Étape 16 — Décroissance d'un souvenir](<../../04-Contexte-Similarite-et-Memoire/16-Memoire-Formule-Decroissance-Temporelle.md>)
- [Étape 17 — Score de pertinence d'un souvenir](<../../04-Contexte-Similarite-et-Memoire/17-Memoire-Formule-Score-de-Pertinence.md>)
- [Étape 15 — Fondements du RAG et de la mémoire](<../../04-Contexte-Similarite-et-Memoire/15-Fondements-RAG-et-Memoire.md>)
