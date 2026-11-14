# Fiche 15 — Budget de contexte

> Image : `15_budget_contexte.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 13 ter — Ingénierie du contexte](<../../04-Contexte-Similarite-et-Memoire/13c-Contexte-Definitions-Fondamentaux.md>)

**Réserver la place de la réponse**

## Formule

$$
B_{\text{disponible}} = B_{\text{total}} - B_{\text{instructions}} - B_{\text{historique}} - B_{\text{sortie}}
$$

## Éléments

$$
B_{\text{total}}
$$

**B total** : la fenêtre de contexte du modèle, en tokens.

$$
B_{\text{instructions}}
$$

**B instructions** : le prompt système, la description des outils, les règles.

$$
B_{\text{historique}}
$$

**B historique** : les tours de conversation déjà accumulés.

$$
B_{\text{sortie}}
$$

**B sortie** : la place réservée à la réponse.

$$
B_{\text{disponible}}
$$

**B disponible** : ce qui reste pour les passages récupérés et la mémoire.

## Ce que c'est

Le budget découpe la fenêtre avant d'y empiler des documents. La réponse a besoin d'une réserve, sinon elle est coupée.

## Effets et impacts

- Il pilote le chunking, le résumé et la mémoire.
- Dépasser le budget tronque les instructions ou les preuves.
- Un historique trop long évince le passage utile.
- Réserver la sortie évite une réponse interrompue.

## Exemple chiffré

Fenêtre de 200 000 tokens, prompt et outils 6 000, historique 40 000, réserve de sortie 8 000 :

$$
B_{\text{disponible}} = 200\,000 - 6\,000 - 40\,000 - 8\,000 = 146\,000
$$

Avec des passages de 800 tokens, on peut en injecter au plus 182. En pratique on en met bien moins : le coût croît avec chaque token lu (fiche 16), et l'attention se dilue (fiche 05).

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`budget_disponible(total, instructions, historique, sortie)`** — Cette fonction tient le rôle d'un régisseur de théâtre qui, avant de laisser entrer le public, retire de la salle les sièges déjà réservés : elle reçoit la taille de la fenêtre de contexte en tokens, puis les trois parts non négociables, les instructions, l'historique de la conversation et la réserve laissée à la réponse, et les soustrait l'une après l'autre du total. Si le reste devient négatif, elle ne rend pas un nombre absurde : elle lève une `ValueError` qui annonce de combien de tokens on dépasse et conseille de réduire l'historique ou les instructions ; sinon elle renvoie les places libres, 146 000 tokens pour une fenêtre de 200 000 dont on a ôté 6 000, 40 000 et 8 000.

**`remplir(passages, place)`** — Celle-ci est le déménageur qui charge un camion en commençant toujours par le carton le plus précieux : elle reçoit une liste de passages décrits chacun par un couple (score, taille) et la place disponible, numérote les passages pour se souvenir de leur position d'origine, les trie par score décroissant, puis prend chaque passage qui tient encore dans l'espace restant et décompte aussitôt sa taille, en laissant sur le trottoir ceux qui sont trop gros. Elle renvoie la liste des indices retenus, dans l'ordre où ils ont été chargés : avec 2 600 tokens, le passage 0 de 1 000 tokens entre, le passage 1 de 3 000 tokens ne passe plus, et le passage 2 de 1 500 tokens se glisse dans les 1 600 qui restaient, d'où `[0, 2]`.

**`main()`** — C'est le chef de plateau qui fait la répétition générale de la fiche : il demande à `budget_disponible` la place libre pour l'exemple chiffré, imprime 146 000 tokens et le nombre maximal de passages de 800 tokens, puis vérifie par un `assert` que ces deux nombres valent bien 146 000 et 182. Il teste ensuite `remplir` sur trois passages et exige le résultat `[0, 2]`, puis provoque volontairement un dépassement, une fenêtre de 8 000 tokens pour 3 000, 4 000 et 2 000 de charges, et considère comme une faute que l'exception attendue ne soit pas levée, avant d'imprimer la ligne de succès.

```python
"""Fiche 15 — budget de contexte : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def budget_disponible(total: int, instructions: int, historique: int, sortie: int) -> int:
    """B_disponible = B_total − B_instructions − B_historique − B_sortie."""
    reste = total - instructions - historique - sortie
    if reste < 0:
        raise ValueError(f"dépassement de {-reste} tokens : réduire l'historique ou les instructions")
    return reste


def remplir(passages: list[tuple[float, int]], place: int) -> list[int]:
    """Ajoute les passages par score décroissant tant qu'ils tiennent (remplissage glouton)."""
    retenus = []
    for i, (score, taille) in sorted(enumerate(passages), key=lambda x: -x[1][0]):
        if taille <= place:
            retenus.append(i)
            place -= taille
    return retenus


def main() -> None:
    dispo = budget_disponible(200_000, 6_000, 40_000, 8_000)
    print(f"disponible : {dispo:,} tokens   passages de 800 tokens au plus : {dispo // 800}")
    assert dispo == 146_000 and dispo // 800 == 182
    retenus = remplir([(0.9, 1_000), (0.8, 3_000), (0.7, 1_500)], 2_600)
    print("passages retenus dans 2 600 tokens :", retenus)
    assert retenus == [0, 2]
    try:
        budget_disponible(8_000, 3_000, 4_000, 2_000)
        raise AssertionError("le dépassement aurait dû être signalé")
    except ValueError:
        pass
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
disponible : 146,000 tokens   passages de 800 tokens au plus : 182
passages retenus dans 2 600 tokens : [0, 2]
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`budget_disponible` retranche de la fenêtre totale du modèle les trois parts qui ne sont pas négociables : les instructions (prompt système et description des outils), l'historique déjà accumulé et la réserve de sortie, sans laquelle la réponse serait coupée. Si le résultat est négatif, la fonction ne renvoie pas un nombre absurde : elle lève une erreur qui dit de combien de tokens on dépasse, pour qu'on réduise l'historique (résumé, fenêtre glissante) avant d'appeler le modèle.

`remplir` utilise la place disponible : elle trie les passages par score décroissant et ajoute chaque passage s'il tient encore dans la place qui reste, en décomptant sa taille. C'est un remplissage glouton, simple et prévisible, qui privilégie toujours le passage le mieux classé.

`main` vérifie l'exemple de la fiche : une fenêtre de 200 000 tokens, 6 000 tokens d'instructions, 40 000 d'historique et 8 000 de réserve laissent 146 000 tokens, soit au plus 182 passages de 800 tokens. Il vérifie aussi le remplissage sur trois passages : avec 2 600 tokens de place, le premier passage (1 000 tokens) est retenu, le deuxième (3 000) ne tient plus, et le troisième (1 500) tient encore.

## Squelette algorithmique

```text
ALGORITHME RemplirLeContexte
ENTRÉES : B_total, B_instructions, B_historique, B_sortie, passages (score, taille)
SORTIE  : les passages injectés

  place ← B_total − B_instructions − B_historique − B_sortie
  SI place < 0 ALORS ERREUR « réduire l'historique » (résumé, fenêtre glissante)
  trier les passages par score décroissant
  POUR CHAQUE passage p FAIRE
      SI taille(p) ≤ place ALORS injecter p ; place ← place − taille(p)
  FIN POUR
```

**Complexité.** O(1) pour le budget, O(n log n) pour trier n passages et O(n) pour les ajouter. Mesurer la taille d'un passage en tokens coûte O(longueur du passage) avec un tokenizer.

**Du squelette au code.** La première ligne et sa garde sont `budget_disponible`, la suite est `remplir`.

## Dans le cours

- [Étape 13 ter — Ingénierie du contexte](<../../04-Contexte-Similarite-et-Memoire/13c-Contexte-Definitions-Fondamentaux.md>)
- [Étape 72 — Coûts et gestion des tokens](<../../12-Production-Couts-Optimisation/72-Couts-et-Gestion-des-Tokens.md>)
