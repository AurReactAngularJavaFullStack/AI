# Étape 6 — Calendrier et chemin critique

> Palier 08 · Étape 6 sur 7 · Précédent : [Étape 5 — Les vagues parallèles](<05-Vagues-paralleles.md>) · Suivant : [Étape 7 — Assemblage et vérification](<07-Assemblage-et-verification.md>) · Retour à l'énoncé : [README du palier 08](<../../README.md>)

## Comment raisonner

Trois questions de chef de projet, dans cet ordre :

1. **Quand chaque tâche peut-elle commencer et finir, au plus tôt ?** Une tâche démarre dès que **tous** ses prérequis sont finis, donc à la plus grande de leurs dates de fin : c'est le calendrier.
2. **Combien de temps dure le dossier, au minimum ?** La plus grande date de fin du calendrier. La chaîne de tâches qui la produit est le **chemin critique** : retarder l'une de ses tâches retarde tout le dossier.
3. **Que coûte une exécution synchronisée par vagues ?** La somme des maxima des vagues, une borne supérieure du chemin critique.

On code dans cet ordre, parce que chaque réponse s'appuie sur la précédente.

## Le calendrier au plus tôt

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`calendrier(taches)`** — Cette fonction est l'agenda d'un atelier qui aurait autant d'ouvriers qu'il le faut, si bien que chaque poste démarre dès que le dernier de ses prérequis est fini : elle reçoit les tâches, les indexe par nom, parcourt l'ordre de `tri_topologique` et donne à chaque tâche un début égal à la plus grande date de fin de ses prérequis, 0,0 s'il n'en a pas, puis une fin égale à ce début plus sa durée. Elle renvoie le dictionnaire nom → (début, fin) ; sur le dossier de crédit, `evaluer_risque` démarre à 2,0 et finit à 3,2, et `rediger_reponse` occupe le créneau de 3,2 à 5,7.

```python
# [extrait] agent/planification.py
def calendrier(taches: list[Tache]) -> dict[str, tuple[float, float]]:
    """Dates au plus tôt {nom: (début, fin)} : une tâche démarre dès que TOUS ses prérequis sont finis.

    Exemple (dossier de crédit) : "evaluer_risque" démarre à max(1.5, 1.9, 2.0) = 2.0 et finit à 3.2.
    """
    par_nom = {t.nom: t for t in taches}
    dates: dict[str, tuple[float, float]] = {}
    for n in tri_topologique(taches):
        debut = max((dates[p][1] for p in par_nom[n].prerequis), default=0.0)
        dates[n] = (debut, debut + par_nom[n].duree)
    return dates
```

- **Même structure que `vagues`** : on parcourt l'ordre topologique, donc les dates des prérequis sont toujours calculées avant celles de la tâche. C'est de la programmation dynamique, la même idée que l'équation de Bellman de l'étape 38 : la valeur d'un nœud se déduit de celle de ses prédécesseurs déjà calculés.
- **`dates[p][1]`** est la date de **fin** du prérequis p (l'indice 0 est le début).
- **`default=0.0`** : une tâche sans prérequis démarre à l'instant 0.
- **`(debut, debut + par_nom[n].duree)`** : un tuple immuable de deux flottants. En Java, on écrirait un petit `record Creneau(double debut, double fin)`.
- On suppose des exécutants **en nombre illimité** : deux tâches prêtes au même instant démarrent ensemble. Avec deux exécutants seulement, il faudrait un ordonnanceur de liste, plus complexe.

**Exemple fait à la main.** `lire_memoire` occupe (0,0 ; 0,5), donc `calculer_mensualite` (0,5 ; 1,3), puis `calculer_ratio` (1,3 ; 1,9) et `convertir_usd` (1,3 ; 1,7). `rechercher_regles` occupe (0,0 ; 2,0) et `verifier_identite` (0,0 ; 1,5). `evaluer_risque` attend trois fins, 1,5, 1,9 et 2,0, et démarre à leur maximum :

$$
\text{début}(\text{evaluer\_risque}) = \max(1{,}5 ;\ 1{,}9 ;\ 2{,}0) = 2{,}0 \qquad \text{fin} = 2{,}0 + 1{,}2 = 3{,}2
$$

Enfin `rediger_reponse` attend 3,2 et 1,7, démarre à 3,2 et finit à 5,7.

**Test qui passe maintenant :** `python -m unittest -v tests.test_08_planification.TestCheminCritique.test_calendrier_au_plus_tot`

## Le chemin critique

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`chemin_critique(taches)`** — Cette fonction est l'enquêteur qui, chantier terminé, remonte le fil des attentes pour désigner la chaîne qui a fixé la date de livraison : elle reçoit les tâches, renvoie `(0.0, [])` pour un plan vide, sinon calcule le calendrier, choisit la tâche qui finit le plus tard, les égalités étant départagées par le plus petit nom, puis remonte à chaque pas vers le prérequis qui finit le plus tard, celui qui a fait attendre, jusqu'à une tâche sans prérequis. Elle renvoie la fin de la dernière tâche et le chemin remis dans l'ordre d'exécution : 5,7 s par `rechercher_regles`, `evaluer_risque` et `rediger_reponse` sur le dossier de crédit.

```python
# [extrait] agent/planification.py
def chemin_critique(taches: list[Tache]) -> tuple[float, list[str]]:
    """(durée minimale du plan, chemin critique) : la plus longue chaîne de durées, de la source à la fin.

    On part de la tâche qui finit le plus tard et l'on remonte, à chaque pas, le prérequis qui finit le
    plus tard (égalité : le plus petit nom). Retarder une tâche du chemin retarde tout le plan.
    Exemple (dossier de crédit) : (5.7, ["rechercher_regles", "evaluer_risque", "rediger_reponse"]),
    soit 2.0 + 1.2 + 2.5 secondes, contre 9.5 s en séquentiel.
    """
    if not taches:
        return 0.0, []
    dates = calendrier(taches)
    par_nom = {t.nom: t for t in taches}
    n = min(dates, key=lambda m: (-dates[m][1], m))
    chemin = [n]
    while par_nom[n].prerequis:
        n = min(par_nom[n].prerequis, key=lambda p: (-dates[p][1], p))
        chemin.append(n)
    return dates[chemin[0]][1], chemin[::-1]
```

Groupe par groupe :

- **`if not taches: return 0.0, []`** : un plan vide dure 0 et n'a pas de chemin. Sans cette garde, `min(dates, …)` sur un dictionnaire vide lèverait `ValueError`.
- **`n = min(dates, key=lambda m: (-dates[m][1], m))`** : la tâche de plus grande fin, départagée par le plus petit nom. C'est la même astuce de clé que `classement` au palier 07 : la fin négative pour « la plus grande d'abord », le nom pour le départage. En Java : `Collections.min(noms, Comparator.comparing((String m) -> -fin(m)).thenComparing(m -> m))`.
- **La boucle `while par_nom[n].prerequis`** remonte, à chaque pas, vers le prérequis qui finit le plus tard. Pourquoi lui ? Parce que la tâche courante a démarré exactement à sa date de fin : c'est lui qui l'a fait attendre. Les autres prérequis avaient de la marge.
- **`return dates[chemin[0]][1], chemin[::-1]`** : la durée est la fin de la première tâche trouvée (la dernière à finir), et le chemin, construit de la fin vers le début, est retourné pour se lire dans l'ordre d'exécution.

**Exemple fait à la main.** `rediger_reponse` finit le plus tard, à 5,7. Ses prérequis finissent à 3,2 (`evaluer_risque`) et 1,7 (`convertir_usd`) : on suit `evaluer_risque`. Les siens finissent à 1,5, 1,9 et 2,0 : on suit `rechercher_regles`, qui n'a pas de prérequis. Le chemin est `rechercher_regles` → `evaluer_risque` → `rediger_reponse` :

$$
T_{\mathrm{CP}} = 2{,}0 + 1{,}2 + 2{,}5 = 5{,}7 \text{ s}
$$

- **Piège classique :** remonter vers le prérequis de plus **grande durée** au lieu du prérequis qui **finit** le plus tard. Pour `evaluer_risque`, le prérequis le plus long est `rechercher_regles` (2,0) et c'est aussi celui qui finit le plus tard, mais ce n'est pas vrai en général : `calculer_ratio` ne dure que 0,6 s et finit pourtant à 1,9, après `verifier_identite` (1,5 s, fin à 1,5). Seule la date de fin dit qui fait attendre.
- **Piège classique bis :** comparer les flottants avec `==` dans un test. 2,0 + 1,2 + 2,5 ne tombe pas toujours exactement sur la représentation binaire de 5,7 ; les tests utilisent `assertAlmostEqual(…, places=9)`.

## La durée par vagues

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`duree_par_vagues(taches)`** — Cette fonction chronomètre un atelier trop discipliné, où personne ne commence la vague suivante avant que le plus lent de la vague en cours ait fini : elle reçoit les tâches, les indexe par nom, puis renvoie la somme, sur les vagues que rend `vagues`, de la plus grande durée de chaque vague ; un plan vide n'a pas de vague et donne 0. Sur le dossier de crédit, elle donne 2,0 + 0,8 + 0,6 + 1,2 + 2,5 = 7,1 s, entre les 9,5 s du séquentiel et les 5,7 s du chemin critique, ce qui chiffre à 1,4 s le coût de la synchronisation par vagues.

```python
# [extrait] agent/planification.py
def duree_par_vagues(taches: list[Tache]) -> float:
    """Calendrier SYNCHRONISÉ : chaque vague attend la plus lente de la précédente. Borne >= chemin critique.

    Exemple (dossier de crédit) : 2.0 + 0.8 + 0.6 + 1.2 + 2.5 = 7.1 s.
    """
    par_nom = {t.nom: t for t in taches}
    return sum(max(par_nom[n].duree for n in v) for v in vagues(taches))
```

- Une ligne : pour chaque vague, la durée de sa tâche la plus lente, et la somme sur les vagues. Une vague n'est jamais vide, donc `max` n'a pas besoin de `default` ; un plan vide n'a pas de vague, et la somme vaut 0.
- Elle sert de **point de comparaison** : c'est ce qu'on obtient avec un orchestrateur naïf qui attend la fin de toute une vague avant de lancer la suivante.

**Exemple fait à la main.** Les maxima valent 2,0 (vague 1), 0,8, 0,6, 1,2 et 2,5 :

$$
T_{\mathrm{seq}} = 9{,}5 \;\ge\; T_{\mathrm{vagues}} = 2{,}0 + 0{,}8 + 0{,}6 + 1{,}2 + 2{,}5 = 7{,}1 \;\ge\; T_{\mathrm{CP}} = 5{,}7
$$

La synchronisation coûte 1,4 s ici : `calculer_mensualite` attend la fin de `rechercher_regles` (2,0 s) au lieu de celle de `lire_memoire` (0,5 s). L'inégalité T_vagues ≥ T_CP est toujours vraie : les tâches du chemin critique sont dans des vagues toutes différentes, et chacune de ces vagues dure au moins autant que la tâche du chemin qu'elle contient.

**Où optimiser.** Seules les tâches du chemin critique font gagner du temps. Si `rechercher_regles` passe de 2,0 s à 0,8 s, `evaluer_risque` attend désormais `calculer_ratio` (1,9 s) et le dossier finit à 1,9 + 1,2 + 2,5 = 5,6 s : on ne gagne que 0,1 s, parce que la branche `lire_memoire` → `calculer_mensualite` → `calculer_ratio` n'avait que 0,1 s de marge. La démo le montre à sa ligne 5.

**Tests qui passent maintenant :**

```powershell
python -m unittest -v tests.test_08_planification
```

Les 12 tests du palier sont verts. Les derniers à passer sont `test_chemin_et_duree`, `test_plan_vide_et_tache_seule`, `test_entrees_invalides` (qui commence par `chemin_critique([Tache("a", 0)])`) et `test_sequentiel_vagues_critique` (9,5 ; 7,1 ; et la borne).
