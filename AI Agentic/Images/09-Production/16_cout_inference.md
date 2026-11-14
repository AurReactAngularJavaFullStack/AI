# Fiche 16 — Coût d'inférence

> Image : `16_cout_inference.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 72 — Coûts et gestion des tokens](<../../12-Production-Couts-Optimisation/72-Couts-et-Gestion-des-Tokens.md>)

**Ce que coûte vraiment une tâche d'agent**

## Formule

$$
C_{\text{total}} \approx N_{\text{in}} \times c_{\text{in}} + N_{\text{out}} \times c_{\text{out}} + C_{\text{outils}}
$$

## Éléments

$$
N_{\text{in}}
$$

**N in** : le nombre de tokens en entrée (lus par le modèle).

$$
c_{\text{in}}
$$

**c in** : le prix d'un token d'entrée.

$$
N_{\text{out}}
$$

**N out** : le nombre de tokens générés.

$$
c_{\text{out}}
$$

**c out** : le prix d'un token de sortie, souvent plusieurs fois plus cher.

$$
C_{\text{outils}}
$$

**C outils** : le coût des appels d'outils et des recherches.

## Ce que c'est

Le coût d'une étape est la somme du contexte lu, du texte écrit et des outils. Dans une boucle d'agent, le contexte est relu à chaque tour.

## Effets et impacts

- Une boucle d'agent coûte plus que le dernier message : l'historique est refacturé à chaque tour.
- Les tokens de sortie sont souvent plus chers.
- Couper le contexte inutile baisse la facture sans baisser la qualité, si la preuve utile reste.

## Exemple chiffré

Prix illustratifs : 3 \$ par million de tokens d'entrée, 15 \$ par million en sortie. Un appel lit 12 000 tokens, en écrit 800, et un outil coûte 0,005 \$ :

$$
C = 12\,000 \times 3 \times 10^{-6} + 800 \times 15 \times 10^{-6} + 0{,}005 = 0{,}036 + 0{,}012 + 0{,}005 = 0{,}053\ \$
$$

Sur 5 tours, si chaque tour ajoute 2 000 tokens à l'historique relu :

$$
N_{\text{in}} = 5 \times 12\,000 + 2\,000 \times (0 + 1 + 2 + 3 + 4) = 80\,000 \quad\Longrightarrow\quad 0{,}24\ \$\ \text{rien qu'en entrée}
$$

La part due à l'historique croît comme le carré du nombre de tours.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cout_appel(n_in, n_out, prix_in, prix_out, c_outils)`** — Cette fonction est la caissière d'un restaurant qui facture séparément ce que le client a lu sur la carte, ce qu'il a commandé en cuisine et les extras : elle reçoit le nombre de tokens lus, le nombre de tokens écrits, le prix d'un token d'entrée et celui d'un token de sortie, exprimés en dollars par token, et le coût des outils, nul par défaut. Elle multiplie chaque nombre de tokens par son prix, ajoute le coût des outils et renvoie le total de l'appel : pour 12 000 tokens lus à 3 dollars le million, 800 tokens écrits à 15 dollars le million et un outil à 0,005 dollar, cela fait 0,036 + 0,012 + 0,005 = 0,053 dollar.

**`tokens_entree_boucle(tours, base, ajout_par_tour)`** — Celle-ci raconte le client qui, à chaque nouveau plat, se fait relire depuis le début toute la conversation de la soirée, de plus en plus longue : elle reçoit le nombre de tours de la boucle d'agent, le nombre de tokens fixes relus à chaque tour et le nombre de tokens que l'historique gagne d'un tour à l'autre, puis additionne, pour chaque tour i de 0 à tours − 1, la quantité base + i × ajout. Elle renvoie le nombre total de tokens d'entrée facturés, 80 000 pour cinq tours de 12 000 tokens qui grossissent de 2 000 à chaque tour, une somme dont la part due à l'historique croît comme le carré du nombre de tours.

**`main()`** — C'est le contrôleur financier qui épluche la note de la soirée : il convertit les prix illustratifs de 3 et 15 dollars par million de tokens en prix par token, calcule le coût d'un appel avec `cout_appel` et le nombre de tokens relus en cinq tours avec `tokens_entree_boucle`, puis imprime 0,053 dollar, 80 000 tokens et 0,24 dollar rien qu'en entrée. Des `assert` vérifient ces trois nombres, puis que dix tours relisent plus du double des tokens de cinq tours, 210 000 contre 80 000, avant que la ligne de succès ne s'affiche.

```python
"""Fiche 16 — coût d'inférence : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def cout_appel(n_in: int, n_out: int, prix_in: float, prix_out: float, c_outils: float = 0.0) -> float:
    """C ≈ N_in × c_in + N_out × c_out + C_outils (prix en dollars par token)."""
    return n_in * prix_in + n_out * prix_out + c_outils


def tokens_entree_boucle(tours: int, base: int, ajout_par_tour: int) -> int:
    """Chaque tour relit tout l'historique : Σ_{i=0}^{tours−1} (base + i × ajout)."""
    return sum(base + i * ajout_par_tour for i in range(tours))


def main() -> None:
    prix_in, prix_out = 3 / 1_000_000, 15 / 1_000_000                 # prix illustratifs
    c = cout_appel(12_000, 800, prix_in, prix_out, 0.005)
    n = tokens_entree_boucle(5, 12_000, 2_000)
    print(f"un appel : {c:.3f} $   5 tours : {n:,} tokens relus, {n * prix_in:.2f} $ en entrée")
    assert math.isclose(c, 0.053) and n == 80_000 and math.isclose(n * prix_in, 0.24)
    assert tokens_entree_boucle(10, 12_000, 2_000) > 2 * tokens_entree_boucle(5, 12_000, 2_000)
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
un appel : 0.053 $   5 tours : 80,000 tokens relus, 0.24 $ en entrée
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`cout_appel` applique la formule de la fiche : le nombre de tokens lus multiplié par le prix d'un token d'entrée, plus le nombre de tokens écrits multiplié par le prix d'un token de sortie, souvent plusieurs fois plus cher, plus le coût des outils appelés pendant la tâche. Les prix sont passés en dollars par token, d'où la division par un million des prix catalogue, qui sont exprimés par million de tokens.

`tokens_entree_boucle` montre pourquoi une boucle d'agent coûte plus que son dernier message : à chaque tour, le modèle relit tout l'historique, qui a grossi de `ajout_par_tour` tokens depuis le tour précédent. La fonction additionne donc base, base + ajout, base + 2 × ajout, et ainsi de suite, une somme dont la partie due à l'historique croît comme le carré du nombre de tours.

`main` vérifie les deux nombres de la fiche : un appel qui lit 12 000 tokens, en écrit 800 et utilise un outil à 0,005 \$ coûte 0,053 \$ ; et cinq tours dont l'historique grossit de 2 000 tokens à chaque tour relisent 80 000 tokens, soit 0,24 \$ rien qu'en entrée. Le dernier `assert` vérifie que doubler le nombre de tours fait plus que doubler les tokens relus.

## Squelette algorithmique

```text
ALGORITHME CoûtDUneTâcheDAgent
ENTRÉES : nombre de tours T, tokens fixes n₀ par appel, ajout Δ par tour, tokens écrits par tour, prix, coûts d'outils
SORTIE  : coût total

  coût ← 0
  POUR t DE 0 À T − 1 FAIRE
      N_in ← n₀ + t × Δ                      (l'historique est relu à chaque tour)
      coût ← coût + N_in × c_in + N_out × c_out + C_outils(t)
  FIN POUR
  RETOURNER coût                              (≈ T n₀ c_in + Δ c_in T (T − 1) / 2 + …)
```

**Complexité.** O(T) pour additionner les tours. Le coût lui-même croît en O(T²) à cause du terme Δ T (T − 1) / 2 : c'est ce qui pousse à résumer l'historique ou à le couper par une fenêtre glissante.

**Du squelette au code.** Le calcul de N_in est le terme `base + i * ajout_par_tour` de `tokens_entree_boucle`, et la ligne du coût est `cout_appel`.

## Dans le cours

- [Étape 72 — Coûts et gestion des tokens](<../../12-Production-Couts-Optimisation/72-Couts-et-Gestion-des-Tokens.md>)
- [Étape 13 ter — Ingénierie du contexte](<../../04-Contexte-Similarite-et-Memoire/13c-Contexte-Definitions-Fondamentaux.md>)
