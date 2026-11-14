# Étape 13 bis — Évaluation — Définitions fondamentales : mesurer avant d'améliorer

> Étape 13 bis du parcours · Prérequis : [Exemples d'agents](<13-Agent-Exemples-Cas-Usage.md>) · Suite : [Ingénierie du contexte](<../04-Contexte-Similarite-et-Memoire/13c-Contexte-Definitions-Fondamentaux.md>)

**Dossier :** 03-Schemas-Outils-et-Premiere-Evaluation  
**Métiers :** AI Engineers, AI Agent Ops, Product Engineers, Forward-Deployed Engineers

Ce fichier arrive tôt dans le parcours, juste après le premier agent outillé : on évalue un agent dès qu'il existe, pas à la fin. Sans jeu d'évaluation, chaque changement de prompt, de modèle ou d'outil est un pari : on ne sait pas s'il améliore, s'il dégrade ou s'il déplace seulement les erreurs. Les métriques spécialisées (fidélité, Tool Call F1, Context Precision) viendront aux étapes 50 à 65. Ici, on pose le protocole et on construit le banc d'essai qui servira à toutes.

## Définitions

### Développement guidé par l'évaluation

Le développement guidé par l'évaluation applique à un agent ce que le TDD applique au code : on écrit d'abord les cas et leurs critères de réussite, on mesure la version actuelle, puis on change **une** chose et on remesure. Un changement n'est gardé que si la mesure progresse au-delà du bruit.

### Cas d'évaluation

Un cas contient une entrée (la demande, les données du contexte), un **critère de réussite vérifiable** et des métadonnées (catégorie, difficulté, origine). « La réponse est bonne » n'est pas un critère. « Le verdict vaut `escalade` et le motif cite la TVA » en est un. Les meilleurs cas viennent de la production : demandes réelles anonymisées, incidents passés, réclamations.

### Jeu d'évaluation et séparation

Le jeu d'évaluation rassemble les cas. On le sépare en un jeu de **développement**, sur lequel on règle prompts et outils, et un jeu de **test**, qu'on ne regarde qu'avant une décision. Régler un prompt en regardant le jeu de test le transforme en jeu de développement : la mesure devient optimiste. La séparation se fait par famille de demandes ou par client, pas au hasard, sinon deux variantes presque identiques d'une même demande se retrouvent des deux côtés.

### Correcteur

Le correcteur (*grader*) décide si un essai réussit. Trois familles, du plus fiable au plus coûteux à fiabiliser :

| Correcteur | Exemple | Quand l'utiliser |
|---|---|---|
| **Code** | égalité d'un champ, validation de schéma, test unitaire exécuté, état final de la base | dès que le critère est vérifiable par programme |
| **LLM juge** | « la réponse cite-t-elle une source qui soutient chaque affirmation ? » | critères de sens ; à valider contre des humains (kappa, Genspark §29b) |
| **Humain** | revue d'un échantillon par un expert métier | référence pour calibrer les deux autres ; trop lent pour tout |

### Essai et trace

Un essai est une exécution complète de l'agent sur un cas. Comme l'agent est stochastique, on lance **plusieurs essais** par cas. Chaque essai produit une trace : appels d'outils, arguments, résultats, réponse finale, tokens, durée. On évalue le **résultat** (la tâche est-elle accomplie ?) et, si besoin, le **processus** (les bons outils ont-ils été appelés, sans action interdite ?).

### Évaluation hors ligne et en ligne

L'évaluation hors ligne tourne sur le jeu d'évaluation, avant le déploiement. L'évaluation en ligne observe la production : échantillon de conversations notées, taux d'escalade, réclamations. Les deux se complètent : le hors ligne protège contre les régressions connues, le en ligne découvre les cas que le jeu ne couvrait pas, et ces cas rejoignent le jeu.

### Barrière d'intégration continue

La barrière d'intégration continue bloque un déploiement si la nouvelle version ne tient pas le niveau. Deux conditions, toutes deux statistiques :

1. la **borne basse** de l'intervalle de Wilson du taux de réussite dépasse le seuil métier (étape 7) ;
2. la nouvelle version n'est pas **significativement moins bonne** que la version en production sur les mêmes cas (test de McNemar sur les paires discordantes).

## Équations

Les trois mesures du banc, démontrées ailleurs dans le parcours :

$$
\hat p = \frac{s}{n} \quad\text{avec son intervalle de Wilson (étape 7)}
$$

$$
\operatorname{pass@}k = 1 - \frac{\binom{n-c}{k}}{\binom{n}{k}}, \qquad \operatorname{pass}^k = \frac{\binom{c}{k}}{\binom{n}{k}} \quad\text{par cas, puis moyennés (étape 60)}
$$

$$
\chi^2_{\text{McNemar}} = \frac{(|b - c| - 1)^2}{b + c}, \quad\text{significatif à 5 % si } \chi^2 > 3{,}84
$$

où, pour chaque cas, c est le nombre d'essais réussis sur n ; et pour la comparaison, b compte les cas réussis par l'ancienne version et ratés par la nouvelle, c l'inverse (deux usages de la lettre c, que le code nomme `reussis` et `gagnes`).

## Architecture hexagonale : le banc d'essai ne dépend que du port

Le banc d'essai appelle l'agent par le même port que la production (étape 1). On évalue donc le vrai assemblage : prompt, outils, garde-fous, contexte. Seul le modèle peut être remplacé par un faux pour tester le banc lui-même. En Java, c'est un test d'intégration paramétré (`@ParameterizedTest` sur les cas), avec un rapport qui agrège les résultats au lieu d'échouer au premier cas raté.

## Construire depuis une feuille blanche

On construit le banc d'essai d'un agent de back-office qui traite trois catégories de demandes : factures, crédits, sinistres. L'agent est simulé : chaque cas a une difficulté, et l'agent réussit un essai avec une probabilité qui en dépend, tirée avec une graine fixe pour que la sortie soit reproductible. Le banc lance 5 essais par cas pour l'ancienne et la nouvelle version, calcule le taux global avec Wilson, le détail par catégorie, pass@1, pass@3 et pass^3, compare les deux versions avec McNemar et applique la barrière.

### Déroulé, ligne par ligne

**`Cas`** est une `dataclass` : identifiant, catégorie, probabilité de réussite de l'ancienne version (`p_a`) et de la nouvelle (`p_b`). Dans un vrai banc, il n'y a pas de probabilité : il y a une entrée et un critère, et c'est l'agent réel qui réussit ou échoue.

**`executer(cas, version, essai, rng)`** joue le rôle de « lancer l'agent puis appliquer le correcteur » : il renvoie `True` si l'essai réussit. Chaque tirage utilise le générateur `rng` partagé, initialisé une fois.

**`jeu()`** fabrique 60 cas : 20 par catégorie, de difficultés variées. La nouvelle version améliore les sinistres (+0,15) et dégrade légèrement les factures (−0,05) : c'est le cas typique d'un changement de prompt qui aide une catégorie et en abîme une autre.

**`evaluer(cas_list, version, n, rng)`** renvoie, pour chaque cas, la liste de ses `n` résultats. Tout le reste se calcule à partir de ce tableau.

**`rapport(resultats, cas_list, k)`** calcule :

- le taux global `s / total` et son intervalle de Wilson, sur tous les essais ;
- le taux par catégorie : une moyenne globale stable peut cacher une catégorie qui s'effondre ;
- pass@1, pass@k et pass^k par cas, puis la moyenne. Le programme vérifie l'inégalité passᵏ ≤ pass@1 ≤ pass@k sur chaque cas.

**`mcnemar(res_a, res_b)`** compare le **premier** essai de chaque cas pour les deux versions : les paires sont appariées par cas, c'est ce qui rend le test plus sensible qu'une comparaison de deux taux.

**`barriere(rap, chi2, perdus, gagnes, seuil)`** applique les deux conditions ; `perdus` et `gagnes` sont les paires discordantes b et c du test de McNemar. La nouvelle version est refusée si la borne basse est sous le seuil, ou si elle perd significativement (χ² > 3,84 avec plus de paires perdues que gagnées).

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer(cas, version, essai, rng)`** — Cette fonction tient la place de l'agent et de son correcteur réunis, comme un dé truqué dont on connaît exactement le biais : elle reçoit un cas, le nom de la version, `"A"` ou autre, le numéro de l'essai et le générateur partagé, choisit la probabilité `p_a` pour la version A et `p_b` sinon, puis renvoie `True` si le tirage `rng.random()` tombe sous cette probabilité. Le numéro d'essai n'intervient pas dans le calcul : il est là pour garder la forme d'un vrai banc. C'est le seul endroit qu'il faudrait remplacer pour évaluer un agent réel avec un vrai critère de réussite.

**`jeu()`** — Celle-ci est l'examinateur qui prépare le sujet d'épreuve : elle ne reçoit rien et fabrique 60 cas, 20 pour chacune des catégories facture, crédit et sinistre, identifiés de « facture-00 » à « sinistre-19 ». La probabilité de réussite de l'ancienne version parcourt cycliquement 0,55, 0,65, 0,75, 0,85 et 0,95 ; celle de la nouvelle y ajoute l'effet de la catégorie, −0,05 pour les factures, 0 pour les crédits et +0,15 pour les sinistres, en la maintenant entre 0 et 0,99. Elle renvoie la liste de ces cas figés, qui simule un changement de prompt qui aide une catégorie et en abîme une autre.

**`evaluer(cas_list, version, n, rng)`** — C'est le surveillant de salle qui fait passer l'épreuve à chaque candidat plusieurs fois : la fonction reçoit la liste des cas, la version évaluée, le nombre n d'essais et le générateur, appelle `executer` n fois sur chaque cas et renvoie un dictionnaire qui associe à l'identifiant de chaque cas la liste de ses n résultats booléens. Elle ne résume rien, parce que les mesures de constance ont besoin de tous les essais et pas seulement de leur somme. Dans `main`, elle tourne avec 5 essais pour la version A puis pour la version B, sur le même générateur.

**`wilson(s, n, z)`** — Cette fonction est le statisticien qui encadre chaque taux mesuré : elle reçoit le nombre de succès, le nombre d'essais et le quantile z, 1,96 par défaut, calcule le centre décalé et la marge de l'intervalle de Wilson, puis renvoie les deux bornes divisées par 1 + z²/n. Cette version ne contrôle pas ses entrées et ne ramène pas les bornes dans [0, 1]. Elle donne 0,8981 pour la borne basse de 188 succès sur 200, la même valeur qu'à l'étape 7, et [0,716 ; 0,811] pour les 300 essais de la version A.

**`pass_at_k(n, reussis, k)`** — Celle-ci répond à la question du client indulgent, qui se contente qu'au moins une réponse sur k soit bonne : elle reçoit le nombre n d'essais d'un cas, le nombre de réussites et k, puis renvoie 1 − C(n − c, k) / C(n, k), le complément de la probabilité que k essais tirés sans remise parmi les n soient tous des échecs. Elle ne lève pas d'exception pour des entrées cohérentes. Pour 7 réussites sur 10 et k = 3, elle vaut 1 − 1/120, puisqu'un seul trio sur les 120 possibles ne contient que des échecs.

**`pass_puissance_k(n, reussis, k)`** — Cette fonction répond à la question du client exigeant, qui redemande k fois et veut k bonnes réponses : elle reçoit les mêmes n, c et k, et renvoie C(c, k) / C(n, k), la probabilité que k essais tirés sans remise soient tous des réussites. Pour 7 réussites sur 10 et k = 3, elle vaut 35/120, bien moins que pass@1, qui vaut 0,7. C'est elle qui mesure la constance de l'agent : la version A n'obtient que 0,477 en pass^3, alors que son pass@1 atteint 0,767.

**`rapport(resultats, cas_list, k)`** — C'est le rédacteur du bulletin de notes, qui ne se contente pas de la moyenne : il reçoit le tableau des résultats d'une version, la liste des cas et k, calcule le taux global sur tous les essais et son intervalle de Wilson, le taux de chaque catégorie, puis, pour chaque cas, pass@1, pass@k et pass^k, en vérifiant par un `assert` que pass^k ≤ pass@1 ≤ pass@k. Il renvoie un dictionnaire avec le taux, l'intervalle, les taux par catégorie et les trois moyennes : pour la version B, 76,0 %, des factures à 63 % et des sinistres à 93 %, avec un pass^3 de 0,517.

**`mcnemar(res_a, res_b)`** — Cette fonction est l'arbitre d'un match retour joué sur le même terrain : elle reçoit les résultats des deux versions, ne regarde que le premier essai de chaque cas, compte les cas perdus, réussis par A et ratés par B, et les cas gagnés, ratés par A et réussis par B, puis renvoie le triplet formé de la statistique (|perdus − gagnés| − 1)² / (perdus + gagnés), du nombre de perdus et du nombre de gagnés, ou (0, 0, 0) s'il n'y a aucune paire discordante. Sur l'exemple vérifié à la main, 12 perdus et 28 gagnés donnent 5,625 ; sur le banc simulé, 13 perdus et 9 gagnés ne donnent que 0,41.

**`barriere(rap, chi2, perdus, gagnes, seuil)`** — C'est le garde-barrière de l'intégration continue, qui ne lève le bras que si deux conditions sont remplies : il reçoit le rapport de la version candidate, la statistique de McNemar, les nombres de cas perdus et gagnés et le seuil, puis renvoie `(False, motif)` si la borne basse de Wilson est sous le seuil, `(False, "régression significative (McNemar)")` si le χ² dépasse 3,84 avec plus de perdus que de gagnés, et `(True, "déploiement autorisé")` sinon. Avec le seuil de 70 %, la version B passe, alors que ses factures chutent de 82 % à 63 % : la barrière ne regarde pas les catégories.

**`main()`** — C'est le président du jury qui fait passer les deux versions devant la même épreuve : il fixe la graine 2026, fabrique les 60 cas, évalue la version A puis la version B avec 5 essais par cas, et imprime pour chacune le taux, l'intervalle, les taux par catégorie et les trois mesures pass, en vérifiant que l'intervalle contient le taux et que pass^3 < pass@1 < pass@3. Il calcule ensuite McNemar sur le premier essai, applique la barrière à 70 %, qui autorise le déploiement, puis contrôle à la main Wilson sur 188/200, pass@3 et pass^3 de 7 sur 10, McNemar 12 contre 28 et deux refus de la barrière.

```python
"""Étape 13 bis — banc d'évaluation : essais répétés, Wilson, catégories, pass@k / pass^k, McNemar, barrière CI."""
import math
import random
import sys
from dataclasses import dataclass
from math import comb

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


@dataclass(frozen=True)
class Cas:
    id: str
    categorie: str
    p_a: float          # ancienne version
    p_b: float          # nouvelle version


def executer(cas: Cas, version: str, essai: int, rng: random.Random) -> bool:
    """Simule « lancer l'agent sur le cas, puis appliquer le correcteur »."""
    p = cas.p_a if version == "A" else cas.p_b
    return rng.random() < p


def jeu() -> list[Cas]:
    cas = []
    effets = {"facture": -0.05, "credit": 0.0, "sinistre": 0.15}
    for categorie, effet in effets.items():
        for i in range(20):
            p_a = 0.55 + 0.4 * (i % 5) / 4                       # 0,55 ; 0,65 ; 0,75 ; 0,85 ; 0,95
            cas.append(Cas(f"{categorie}-{i:02d}", categorie, p_a, min(0.99, max(0.0, p_a + effet))))
    return cas


def evaluer(cas_list: list[Cas], version: str, n: int, rng: random.Random) -> dict[str, list[bool]]:
    return {c.id: [executer(c, version, e, rng) for e in range(n)] for c in cas_list}


def wilson(s: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = s / n
    centre, marge = p + z * z / (2 * n), z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (centre - marge) / (1 + z * z / n), (centre + marge) / (1 + z * z / n)


def pass_at_k(n: int, reussis: int, k: int) -> float:
    return 1 - comb(n - reussis, k) / comb(n, k)


def pass_puissance_k(n: int, reussis: int, k: int) -> float:
    return comb(reussis, k) / comb(n, k)


def rapport(resultats: dict[str, list[bool]], cas_list: list[Cas], k: int) -> dict:
    total = sum(len(r) for r in resultats.values())
    s = sum(sum(r) for r in resultats.values())
    par_cat = {}
    for c in cas_list:
        ok, nb = par_cat.get(c.categorie, (0, 0))
        par_cat[c.categorie] = (ok + sum(resultats[c.id]), nb + len(resultats[c.id]))
    p1, pk, ppk = [], [], []
    for r in resultats.values():
        n, reussis = len(r), sum(r)
        a, b, d = pass_at_k(n, reussis, 1), pass_at_k(n, reussis, k), pass_puissance_k(n, reussis, k)
        assert d <= a + 1e-12 and a <= b + 1e-12                # pass^k <= pass@1 <= pass@k
        p1.append(a), pk.append(b), ppk.append(d)
    m = len(resultats)
    return {"taux": s / total, "wilson": wilson(s, total), "categories": {c: ok / nb for c, (ok, nb) in par_cat.items()},
            "pass@1": sum(p1) / m, f"pass@{k}": sum(pk) / m, f"pass^{k}": sum(ppk) / m}


def mcnemar(res_a: dict, res_b: dict) -> tuple[float, int, int]:
    perdus = sum(1 for i in res_a if res_a[i][0] and not res_b[i][0])
    gagnes = sum(1 for i in res_a if not res_a[i][0] and res_b[i][0])
    if perdus + gagnes == 0:
        return 0.0, 0, 0
    return (abs(perdus - gagnes) - 1) ** 2 / (perdus + gagnes), perdus, gagnes


def barriere(rap: dict, chi2: float, perdus: int, gagnes: int, seuil: float) -> tuple[bool, str]:
    if rap["wilson"][0] < seuil:
        return False, f"borne basse {rap['wilson'][0]:.3f} < seuil {seuil}"
    if chi2 > 3.84 and perdus > gagnes:
        return False, "régression significative (McNemar)"
    return True, "déploiement autorisé"


def main() -> None:
    rng = random.Random(2026)
    cas_list = jeu()
    res_a = evaluer(cas_list, "A", 5, rng)
    res_b = evaluer(cas_list, "B", 5, rng)
    k = 3
    for nom, res in (("A (production)", res_a), ("B (candidate)", res_b)):
        r = rapport(res, cas_list, k)
        bas, haut = r["wilson"]
        cats = ", ".join(f"{c} {v:.0%}" for c, v in r["categories"].items())
        print(f"{nom} : {r['taux']:.1%} [{bas:.3f} ; {haut:.3f}] — {cats}")
        print(f"   pass@1 {r['pass@1']:.3f}   pass@3 {r['pass@3']:.3f}   pass^3 {r['pass^3']:.3f}")
        assert bas <= r["taux"] <= haut
        assert r["pass^3"] < r["pass@1"] < r["pass@3"]
    rap_b = rapport(res_b, cas_list, k)
    chi2, perdus, gagnes = mcnemar(res_a, res_b)
    print(f"McNemar (1er essai) : {perdus} cas perdus, {gagnes} gagnés, χ² = {chi2:.2f}")
    ok, motif = barriere(rap_b, chi2, perdus, gagnes, seuil=0.70)
    print(f"Barrière à 70 % : {motif}")

    print("Contrôles à la main")
    assert round(wilson(188, 200)[0], 4) == 0.8981                     # même valeur qu'à l'étape 7
    assert pass_at_k(10, 7, 3) == 1 - 1 / 120 and pass_puissance_k(10, 7, 3) == 35 / 120
    assert mcnemar({"x": [True]} | {f"p{i}": [True] for i in range(12)} | {f"g{i}": [False] for i in range(28)},
                   {"x": [True]} | {f"p{i}": [False] for i in range(12)} | {f"g{i}": [True] for i in range(28)}) \
        == (5.625, 12, 28)
    assert barriere({"wilson": (0.65, 0.80)}, 0.0, 0, 0, 0.70)[0] is False
    assert barriere({"wilson": (0.75, 0.85)}, 5.0, 20, 8, 0.70) == (False, "régression significative (McNemar)")
    print("  Wilson 188/200, pass@3 et pass^3 de 7/10, McNemar 12/28 = 5,625 : conformes")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
A (production) : 76.7% [0.716 ; 0.811] — facture 82%, credit 75%, sinistre 73%
   pass@1 0.767   pass@3 0.982   pass^3 0.477
B (candidate) : 76.0% [0.709 ; 0.805] — facture 63%, credit 72%, sinistre 93%
   pass@1 0.760   pass@3 0.952   pass^3 0.517
McNemar (1er essai) : 13 cas perdus, 9 gagnés, χ² = 0.41
Barrière à 70 % : déploiement autorisé
Contrôles à la main
  Wilson 188/200, pass@3 et pass^3 de 7/10, McNemar 12/28 = 5,625 : conformes
OK — toutes les vérifications sont passées.
```

Lisez la sortie de près : B laisse le taux global presque inchangé (76,7 % contre 76,0 %, intervalles qui se recouvrent), McNemar ne voit pas de régression significative, et la barrière autorise le déploiement. Pourtant les factures passent de 82 % à 63 %. La barrière à deux conditions est aveugle à une catégorie qui s'effondre quand une autre progresse : c'est l'objet de l'exercice 2, qui ajoute la règle par catégorie.

Ce que le programme montre : un agent s'évalue comme un système stochastique. On répète les essais, on publie un intervalle et non un chiffre, on découpe par catégorie pour voir ce que la moyenne cache, on compare deux versions sur les **mêmes** cas, et une règle écrite décide du déploiement.

### Mécanisme du programme, en détail

Le programme simule un banc d'évaluation complet sans appeler de modèle. Chaque `Cas` porte deux probabilités de réussite, `p_a` pour la version en production et `p_b` pour la version candidate, et `executer` tire un nombre au hasard pour décider si l'agent réussit ce cas à cet essai : c'est le seul endroit qu'il faudrait remplacer pour brancher un vrai agent et un vrai correcteur. `jeu` fabrique 60 cas répartis en trois catégories de 20, avec des difficultés qui vont de 0,55 à 0,95 ; la catégorie « facture » perd 5 points dans la version candidate, « crédit » ne change pas et « sinistre » en gagne 15, ce qui permet de vérifier qu'une moyenne globale peut masquer une régression locale.

`evaluer` lance chaque cas n fois et garde la liste des réussites, parce que les mesures de constance ont besoin de tous les essais, pas seulement de leur somme. `rapport` calcule le taux global et son intervalle de Wilson, le taux par catégorie, puis, pour chaque cas, pass@1, pass@k et pass^k par les formules combinatoires : `pass_at_k` est la probabilité qu'au moins un des k essais tirés sans remise réussisse, `pass_puissance_k` celle que les k réussissent tous. La ligne `assert d <= a and a <= b` vérifie à chaque cas l'ordre pass^k ≤ pass@1 ≤ pass@k, qui découle du fait qu'exiger k succès est plus dur qu'en exiger un, et qu'en avoir un parmi k est plus facile qu'en avoir un du premier coup.

`mcnemar` compare les deux versions sur les mêmes cas, en ne regardant que les paires discordantes : les cas réussis par A et ratés par B (« perdus ») et l'inverse (« gagnés ») ; les cas réussis ou ratés par les deux n'apportent aucune information sur la différence. La statistique (|perdus − gagnés| − 1)² / (perdus + gagnés), avec la correction de continuité, se compare à 3,84, le seuil du χ² à un degré de liberté au niveau 5 %. `barriere` enchaîne enfin les deux conditions de déploiement : la borne basse de Wilson doit atteindre le seuil, et il ne doit pas y avoir de régression significative.

## Squelette algorithmique

L'algorithme est une barrière d'intégration continue : à chaque version candidate, on rejoue le jeu d'évaluation, on mesure, on compare à la version en production, et on autorise ou on bloque.

```text
ALGORITHME BarrièreDÉvaluation
ENTRÉES : cas c₁ … c_m, version A (production), version B (candidate), n essais par cas, k, seuil
SORTIE  : (déployer : vrai ou faux, motif)

  POUR CHAQUE version V DANS {A, B} FAIRE
      POUR CHAQUE cas c FAIRE
          résultats[V][c] ← [Exécuter(c, V) pour e de 1 à n]
      FIN POUR
  FIN POUR
  s ← nombre total de réussites de B          total ← m × n
  (bas, haut) ← Wilson(s, total)
  POUR CHAQUE cas c FAIRE  calculer pass@1, pass@k, pass^k de B sur c  FIN POUR
  perdus ← #{c : A réussit le 1er essai, B l'échoue}
  gagnés ← #{c : A échoue le 1er essai, B le réussit}
  χ² ← (|perdus − gagnés| − 1)² / (perdus + gagnés)
  SI bas < seuil ALORS RETOURNER (faux, « borne basse sous le seuil »)
  SI χ² > 3,84 ET perdus > gagnés ALORS RETOURNER (faux, « régression significative »)
  RETOURNER (vrai, « déploiement autorisé »)
```

**Complexité.** L'évaluation coûte 2 × m × n exécutions de l'agent : c'est elle qui domine, en temps comme en argent, puisque chaque exécution réelle appelle le modèle. Les statistiques sont ensuite légères : O(m × n) pour les comptes, O(1) pour Wilson et McNemar, et O(m) calculs de coefficients binomiaux de petite taille pour pass@k et pass^k. La mémoire est O(m × n) pour garder tous les résultats.

**Du squelette au code.** `Exécuter` correspond à `executer`, la double boucle à `evaluer`, les mesures à `rapport` (avec `wilson`, `pass_at_k` et `pass_puissance_k`), le comptage des paires discordantes et le χ² à `mcnemar`, et les deux conditions finales à `barriere`.

## Cas d'usage réels aux Émirats

Les volumes et seuils sont illustratifs.

### Banque — jeu d'évaluation construit à partir des réclamations

Une banque de Dubaï construit le jeu d'évaluation de son agent client à partir de 18 mois de réclamations anonymisées : 400 cas, dont 60 demandes piégées (tentatives d'obtenir des informations sur un autre compte). Les critères sont vérifiés par code (« aucun appel à `lire_compte` avec un identifiant différent de celui du client authentifié »), ce qui rend la mesure exacte et rejouable. Chaque nouvelle version de prompt passe la barrière avant d'arriver en recette.

### Assurance — une moyenne qui cache une catégorie

Un assureur santé voit son taux global passer de 88 % à 89 % après un changement de prompt, mais le détail par catégorie montre que les demandes de remboursement en arabe passent de 85 % à 76 %. Le changement est retiré. Le banc découpe désormais par catégorie **et** par langue, et la barrière exige qu'aucune catégorie ne perde plus de 5 points.

### Immobilier — constance mesurée par pass^k

Une agence évalue son agent d'estimation sur 50 biens, avec 5 essais chacun. pass@1 vaut 0,82 mais pass^3 seulement 0,58 : le même bien reçoit des fourchettes différentes selon l'essai. L'équipe fixe la température basse, déplace le calcul des quartiles dans un outil déterministe (étape 1), et pass^3 remonte à 0,79 : un client qui redemande une estimation obtient la même réponse.

## Pièges et limites

- **Évaluer à la fin.** Un agent construit sans jeu d'évaluation a accumulé des choix qu'on ne peut plus départager.
- **Un seul essai par cas.** On mesure le hasard autant que l'agent ; pass^k reste invisible.
- **Régler sur le jeu de test.** Après dix itérations guidées par le test, son taux ne prédit plus la production.
- **Faire confiance au LLM juge sans le mesurer.** Un juge non calibré peut récompenser les réponses longues ou celles de son propre modèle.
- **Comparer deux versions sur des cas différents.** Les écarts de difficulté dominent l'écart de qualité ; on compare sur les mêmes cas, avec un test apparié.

### Exercice feuille blanche

1. Réécrire `rapport` sans regarder : taux, Wilson, détail par catégorie.
2. Ajouter à la barrière la règle « aucune catégorie ne perd plus de 5 points par rapport à A » et vérifier qu'elle refuse B si les factures baissent trop.
3. Prédire : avec 60 cas et 5 essais, combien d'essais au total ? Quelle largeur approximative a l'intervalle de Wilson autour de 75 % ? (Réponse : 300 essais ; environ ±5 points, car

$$
1{,}96\sqrt{0{,}75 \times 0{,}25 / 300} \approx 0{,}049
$$

.)

## Pour aller plus loin

- La démonstration de pass@k et pass^k, et la mesure de la réussite de la tâche : [étape 60](<../10-Evaluation/60-Evaluation-Formule-Agent-Goal-Accuracy.md>).
- Les métriques spécialisées du RAG et des outils (fidélité, Context Precision, Tool Call F1) : étapes 50 à 65.
- Le support Genspark (sections 27b, 28 et 29b) résume pass^k, McNemar et le kappa d'un LLM juge.

> Suite : [Ingénierie du contexte](<../04-Contexte-Similarite-et-Memoire/13c-Contexte-Definitions-Fondamentaux.md>) — étape 13 ter.
