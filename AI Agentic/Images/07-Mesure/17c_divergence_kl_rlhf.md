# Fiche 17c_divergence_kl_rlhf — KL pour ne pas s'éloigner de la référence

> Image : `17c_divergence_kl_rlhf.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 50 — Précision, rappel, F1 et KL](<../../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>)

**La KL entre la politique apprise et la politique de départ**

## Ce que montre l'image

Affiche « Divergence KL pour la régularisation dans le RLHF ». La formule compare πθ, la politique en cours d'apprentissage, à la politique de référence (le modèle pré-entraîné), action par action. Conséquence : l'agent ne s'éloigne pas trop de la référence. Effets : la KL sert dans PPO et DPO à stabiliser l'entraînement. Impact : un alignement plus sûr des agents LLM.

**À lire avec prudence :** l'encadré de gauche dit que la KL « mesure la distance ». Ce n'est pas une distance : elle n'est pas symétrique (fiche 17).

**Lien :** l'exemple chiffré « récompense − β × KL » est dans `Demonstrations/07-Mesure/17_divergence_kl.md`.

## Formule

$$
\mathrm{KL}(\pi_{\theta} \,\|\, \pi_{\mathrm{ref}}) = \sum_a \pi_{\theta}(a)\, \log \frac{\pi_{\theta}(a)}{\pi_{\mathrm{ref}}(a)}
$$

## Éléments

$$
\pi_{\theta}
$$

**πθ** : la politique en cours d'apprentissage.

$$
\pi_{\text{ref}}
$$

**πref** : la politique de référence, souvent le modèle avant alignement.

$$
a
$$

**a** : une action, ou un token.

C'est la fiche 17, avec P = πθ et Q = πref. L'affiche somme sur les actions.

## Ce que c'est

On pénalise un agent qui s'éloigne trop du modèle de départ. PPO et DPO utilisent ce frein pour que l'alignement ne détruise pas le modèle.

## Effets et impacts

- Une KL forte : l'agent a changé de comportement. Ce n'est pas automatiquement un progrès.
- Une KL nulle : il n'a pas bougé. L'alignement n'a rien fait.
- Le frein ne remplace pas un garde-fou. Une politique proche de la référence peut encore être nuisible si la référence l'était.

## Exemple chiffré

P = (0,5, 0,5) et Q = (0,9, 0,1), logarithme naturel.

$$
D_{\mathrm{KL}} = 0{,}5 \ln \frac{0{,}5}{0{,}9} + 0{,}5 \ln \frac{0{,}5}{0{,}1} \approx 0{,}5(-0{,}588) + 0{,}5(1{,}609) \approx 0{,}511
$$

Dans l'autre sens, KL(Q ‖ P) ≈ 0,368. Même paire, deux nombres.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`kl(p, q)`** — Cette fonction mesure la tension de la laisse qui relie un chien en apprentissage, la politique πθ, à son maître, la politique de référence πref : elle reçoit les deux distributions sur les actions, vérifie que chacune a une somme égale à 1 et lève une `ValueError` sinon, puis parcourt les actions une à une. Elle ignore celles que πθ ne joue jamais, renvoie l'infini dès que la référence interdit une action que πθ joue, la laisse cassant alors net, et ajoute pour les autres πθ(a) × ln(πθ(a) / πref(a)) au total qu'elle renvoie : 0,0851 pour une politique (0,7 ; 0,2 ; 0,1) qui s'est un peu écartée d'une référence (0,5 ; 0,3 ; 0,2), et 0 si elle n'a pas bougé du tout.

**`main()`** — C'est le dresseur qui vérifie la laisse avant chaque séance : il commence par l'exemple des fiches 17 à 17b, imprime 0,511 dans un sens et 0,368 dans l'autre, ainsi que 0,0 pour une distribution comparée à elle-même, et contrôle ces nombres par un `assert`. Il calcule ensuite la divergence de la politique apprise par rapport à sa référence, propre à cette fiche, imprime 0,0851 et vérifie qu'elle est strictement positive, qu'une politique devenue certaine diverge elle aussi d'une référence uniforme, et qu'une référence qui interdit une action possible donne une pénalité infinie, avant d'imprimer la ligne de succès.

```python
"""Fiches 17, 17a à 17c — divergence KL : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def kl(p: list[float], q: list[float]) -> float:
    """D_KL(P ‖ Q) = Σ P(x) ln(P(x) / Q(x)) ; infini si Q(x) = 0 là où P(x) > 0."""
    if not (math.isclose(sum(p), 1) and math.isclose(sum(q), 1)):
        raise ValueError("P et Q doivent être des distributions")
    total = 0.0
    for px, qx in zip(p, q):
        if px == 0:
            continue                       # convention 0 ln 0 = 0
        if qx == 0:
            return math.inf
        total += px * math.log(px / qx)
    return total


def main() -> None:
    P, Q = [0.5, 0.5], [0.9, 0.1]
    pq, qp = kl(P, Q), kl(Q, P)
    print(f"KL(P ‖ Q) = {pq:.3f}   KL(Q ‖ P) = {qp:.3f}   KL(P ‖ P) = {kl(P, P)}")
    assert round(pq, 3) == 0.511 and round(qp, 3) == 0.368 and kl(P, P) == 0
    pi_theta, pi_ref = [0.7, 0.2, 0.1], [0.5, 0.3, 0.2]      # fiche 17c : politique et référence
    print(f"fiche 17c : KL(πθ ‖ πref) = {kl(pi_theta, pi_ref):.4f}")
    assert kl(pi_theta, pi_ref) > 0 and kl([1.0, 0.0], [0.5, 0.5]) > 0 and kl([0.5, 0.5], [1.0, 0.0]) == math.inf
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
KL(P ‖ Q) = 0.511   KL(Q ‖ P) = 0.368   KL(P ‖ P) = 0.0
fiche 17c : KL(πθ ‖ πref) = 0.0851
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`kl` vérifie d'abord que P et Q sont bien des distributions, puis parcourt les événements un par un. Un événement de probabilité nulle sous P ne compte pas, selon la convention 0 ln 0 = 0 ; un événement possible sous P mais impossible sous Q rend la divergence infinie, parce que Q affirme impossible ce que la référence considère possible, et la fonction le renvoie immédiatement. Pour les autres événements, elle ajoute P(x) multiplié par le logarithme du rapport P(x) / Q(x), l'écart local de la fiche.

`main` vérifie l'exemple des fiches 17, 17a et 17b : avec P = (0,5 ; 0,5) et Q = (0,9 ; 0,1), KL(P ‖ Q) vaut 0,511 et KL(Q ‖ P) vaut 0,368, deux nombres différents pour la même paire, ce qui montre que la KL n'est pas symétrique ; et la divergence d'une distribution avec elle-même est nulle. Le programme applique enfin la formule à la situation de la fiche 17c, une politique en cours d'apprentissage comparée à sa politique de référence, et vérifie qu'une référence qui interdit une action possible donne une pénalité infinie.

## Squelette algorithmique

```text
ALGORITHME DivergenceKL
ENTRÉES : distributions P et Q sur les mêmes événements
SORTIE  : D_KL(P ‖ Q) ≥ 0, éventuellement +∞

  total ← 0
  POUR CHAQUE événement x FAIRE
      SI P(x) = 0 ALORS passer
      SI Q(x) = 0 ALORS RETOURNER +∞
      total ← total + P(x) × ln(P(x) / Q(x))
  FIN POUR
  RETOURNER total

USAGE EN ALIGNEMENT (fiche 17c) : objectif ← récompense − β × KL(πθ ‖ πref), pour ne pas trop s'éloigner de la référence.
```

**Complexité.** Une passe sur les événements : O(n). Pour un modèle de langage, n est la taille du vocabulaire, et la KL se calcule à chaque position de la séquence.

**Du squelette au code.** Les deux tests et l'accumulation sont, dans l'ordre, le `continue`, le `return math.inf` et la ligne `total += …` de `kl`.

## Dans le cours

- [Étape 50 — Précision, rappel, F1 et KL](<../../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>)
- [Fiche 17 — Divergence KL](<17_divergence_kl.md>)
- [Fiche 19 — REINFORCE](<../06-Decision/19_reinforce.md>)
