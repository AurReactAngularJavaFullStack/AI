# Étape 7 — Prompts — Taux de conformité aux consignes

> Étape 7 du parcours · Prérequis : [Applications des prompts par domaine](<06-Prompts-Applications-Domaines.md>) · Suite : [Schémas : définitions](<../03-Schemas-Outils-et-Premiere-Evaluation/08-Schemas-Definitions-Fondamentaux.md>)

**Dossier :** 02-LLM-Softmax-et-Prompts  
**Métiers :** Product Engineers, AI Engineers, Forward-Deployed Engineers, AI Agent Ops

Un prompt ne se juge pas à sa lecture : il se juge aux réponses qu'il produit. Ce fichier remplace l'ancienne note de relecture (une somme pondérée de critères notés à l'œil) par une **mesure** : la proportion de réponses qui respectent toutes les consignes vérifiables, avec son intervalle de confiance. Il montre aussi pourquoi un taux de violation, même très faible, finit toujours par produire des violations en production.

## Définition

On fait tourner l'agent sur un jeu de n demandes représentatives. Pour chaque réponse, un programme vérifie chaque consigne vérifiable du prompt : format JSON valide, source citée, absence de formule interdite, escalade quand la règle l'exige. Une réponse est **conforme** si elle passe toutes les vérifications. Le taux de conformité est :

$$
\hat c = \frac{s}{n}
$$

où s est le nombre de réponses conformes. On publie toujours ĉ avec son intervalle de Wilson à 95 %, parce que 47 réponses conformes sur 50 et 940 sur 1 000 donnent le même ĉ = 0,94 mais pas du tout la même certitude.

## Rôle dans la boucle de l'agent

Le prompt est réglé à l'étape « décider » de la boucle : il oriente chaque token tiré par la softmax (étape 2). Le taux de conformité dit si ce réglage tient. Il sert de **barrière de déploiement** : une nouvelle version du prompt ne part en production que si la borne basse de son intervalle dépasse le seuil fixé, et il sert de **sonde** en production, sur un échantillon de réponses réelles.

## Équations

Intervalle de Wilson, pour un niveau de confiance donné par z (z = 1,96 à 95 %) :

$$
\frac{\hat c + \dfrac{z^2}{2n} \pm z\sqrt{\dfrac{\hat c(1-\hat c)}{n} + \dfrac{z^2}{4n^2}}}{1 + \dfrac{z^2}{n}}
$$

Violations inévitables : si chaque réponse viole une consigne avec la probabilité q > 0, indépendamment des autres, alors sur N réponses :

$$
P(\text{au moins une violation}) = 1 - (1-q)^N, \qquad \mathbb{E}[\text{violations}] = Nq
$$

Zéro violation observée : si aucune des n réponses ne viole la consigne, la borne haute à 95 % du taux de violation vaut

$$
q_{\max} = 1 - 0{,}05^{1/n} \approx \frac{3}{n}
$$

(la « règle de trois »).

### Décryptage des symboles

$$
n
$$

**Sens :** nombre de réponses évaluées · **Type / plage :** entier ≥ 1 · **Variable Python :** `n`

$$
s
$$

**Sens :** réponses conformes à toutes les consignes · **Type / plage :** entier, 0 ≤ s ≤ n · **Variable Python :** `s`

$$
\hat c
$$

**Sens :** taux de conformité observé · **Type / plage :** réel dans [0, 1] · **Variable Python :** `s / n`

$$
z
$$

**Sens :** quantile de la loi normale ; 1,96 à 95 % · **Type / plage :** réel > 0 · **Variable Python :** `z`

$$
q
$$

**Sens :** probabilité qu'une réponse viole la consigne · **Type / plage :** réel dans [0, 1] · **Variable Python :** `q`

$$
N
$$

**Sens :** nombre de réponses servies en production · **Type / plage :** entier · **Variable Python :** `N`

$$
q_{\max}
$$

**Sens :** plus grand taux de violation compatible avec 0 violation observée · **Type / plage :** réel · **Variable Python :** `borne_zero_violation(n)`

## Démonstration

### 1. D'où vient l'intervalle de Wilson

Si le vrai taux est c, le nombre de réponses conformes suit une loi binomiale : ĉ a pour moyenne c et pour écart-type √(c(1−c)/n). Pour n assez grand, ĉ tombe à moins de z écarts-types de c avec une probabilité de 95 % quand z = 1,96 :

$$
|\hat c - c| \le z\sqrt{\frac{c(1-c)}{n}}
$$

L'intervalle « naïf » remplace le c inconnu sous la racine par ĉ. Wilson ne fait pas cette approximation : il cherche **toutes** les valeurs de c qui vérifient l'inégalité. On élève au carré (les deux membres sont positifs) :

$$
(\hat c - c)^2 \le \frac{z^2}{n}\,c(1-c)
$$

On développe et on regroupe en c :

$$
\left(1 + \frac{z^2}{n}\right)c^2 - \left(2\hat c + \frac{z^2}{n}\right)c + \hat c^2 \le 0
$$

C'est un trinôme en c de coefficient dominant positif : il est négatif entre ses deux racines. La formule des racines d'un trinôme ac² + bc + d,

$$
c = (-b \pm \sqrt{b^2 - 4ad})/(2a) ,
$$

donne après division du numérateur et du dénominateur par 2 exactement la formule de Wilson. Les deux bornes restent dans [0, 1], ce que l'intervalle naïf ne garantit pas : avec 50 réponses conformes sur 50, l'intervalle naïf vaut [1 ; 1], comme si la conformité était certaine, alors que Wilson donne [0,929 ; 1].

### 2. Calcul à la main

200 réponses, 188 conformes : ĉ = 0,94, z² = 3,8416.

- z²/(2n) = 0,009604, donc le centre du numérateur vaut 0,949604.
- Sous la racine : 0,94 × 0,06 / 200 = 0,000282, plus 3,8416/160 000 = 0,000024, soit 0,000306 ; racine 0,017493 ; fois z : 0,034287.
- Dénominateur : 1 + 3,8416/200 = 1,019208.
- Bornes :

$$
(0{,}949604 - 0{,}034287)/1{,}019208 = 0{,}8981
$$

et

$$
(0{,}949604 + 0{,}034287)/1{,}019208 = 0{,}9653 .
$$

Le prompt est conforme entre 89,8 % et 96,5 % du temps. Si le seuil de déploiement est 90 %, la borne basse (89,8 %) ne le franchit pas : il faut soit améliorer le prompt, soit évaluer davantage de cas.

### 3. Pourquoi une violation finit toujours par arriver

La softmax de l'étape 2 donne une probabilité **strictement positive** à chaque token tant que la température n'est pas nulle :

$$
e^{z/T} > 0
$$

pour tout score z. Une réponse qui viole une consigne n'est donc jamais impossible, seulement improbable. Si chaque réponse viole la consigne avec la probabilité q, indépendamment, la probabilité qu'aucune des N réponses ne la viole est (1−q)ᴺ (produit de N facteurs, comme la fiabilité composée de l'étape 1). Avec q = 0,001 et N = 10 000 réponses par jour :

$$
(0{,}999)^{10\,000} = e^{10\,000 \ln 0{,}999} = e^{-10{,}005} \approx 0{,}000045 .
$$

La probabilité d'au moins une violation dans la journée vaut 0,99995, et l'on en attend Nq = 10. Une consigne critique ne doit donc **jamais** reposer sur le prompt seul : on la double d'une vérification dans le code (schéma à l'étape 8, garde-fou à l'étape 66).

### 4. La règle de trois

Si l'on observe 0 violation sur n réponses, les taux q compatibles avec cette observation à 95 % sont ceux pour lesquels (1−q)ⁿ ≥ 0,05, soit

$$
q \le 1 - 0{,}05^{1/n} .
$$

Comme ln 0,05 ≈ −3 et 1 − e⁻ˣ ≈ x pour x petit, qₘₐₓ ≈ 3/n. Avec 300 réponses sans violation : qₘₐₓ = 0,00994, environ 1 %. « Zéro violation » ne veut jamais dire « taux nul ».

## Du symbole au code Python

Le programme vérifie quatre consignes sur un jeu de réponses simulées, calcule le taux et l'intervalle, puis les deux formules de violation.

### Déroulé, ligne par ligne

**Les vérificateurs** sont des fonctions `reponse -> bool`, une par consigne : `json_valide` essaie `json.loads` ; `cite_source` cherche un numéro de facture `FAC-\d+` ; `sans_formule_interdite` refuse « je garantis » ; `escalade_si_ecart` exige `"verdict": "escalade"` quand la réponse mentionne un écart de TVA.

**`conforme(reponse)`** fait `all(v(reponse) for v in VERIFICATEURS)` : une seule consigne violée rend la réponse non conforme.

**`wilson(s, n, z)`** traduit la formule terme à terme ; le programme vérifie qu'elle redonne [0,8981 ; 0,9653] pour 188/200 et que 50/50 donne une borne haute de 1 et une borne basse de 0,929.

**`jeu_simule()`** fabrique 200 réponses, dont 12 fautives, réparties sur les quatre consignes. Le comptage des échecs consigne par consigne se fait directement dans `main`, dans le dictionnaire `echecs` (il n'y a pas de fonction à part pour cela) : c'est ce tableau qui dit **quoi** corriger dans le prompt.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`json_valide(r)`** — Ce premier vérificateur est le portier qui ne laisse entrer que les documents correctement scellés : il reçoit le texte d'une réponse, tente de le décoder avec `json.loads` et renvoie `True` si le décodage réussit, `False` s'il lève `json.JSONDecodeError`, sans laisser l'exception sortir. Il incarne la consigne « réponds par un JSON » ; dans le jeu simulé, il ne rejette que les 4 réponses écrites en texte libre, « verdict : conforme FAC-900 », et c'est son nom court `json` qui apparaît dans le tableau des échecs par consigne.

**`cite_source(r)`** — Celui-ci est l'archiviste qui exige une cote sur chaque pièce : il reçoit une réponse et renvoie `True` si l'expression régulière `FAC-\d+` y trouve un numéro de facture, c'est-à-dire les lettres FAC, un tiret et au moins un chiffre, `False` sinon. Il ne décode pas le JSON et cherche donc le numéro n'importe où dans le texte, ce qui explique que la réponse en texte libre « FAC-900 » le satisfasse. Il incarne la consigne « cite tes sources » et rejette, dans le jeu simulé, les 4 réponses qui donnent un verdict sans aucune facture.

**`sans_formule_interdite(r)`** — Ce vérificateur joue le juriste qui raye toute promesse que l'entreprise ne pourrait pas tenir : il reçoit une réponse, la passe en minuscules et renvoie `True` seulement si l'expression « je garantis » n'y figure pas, de sorte que « Je garantis » avec une majuscule est attrapé aussi. Il ne lève jamais d'exception. Dans le jeu simulé, il rejette les 2 réponses dont la note dit « Je garantis le paiement », et ce sont les seules qu'il fait échouer, ce que vérifie l'`assert` du tableau des échecs.

**`escalade_si_ecart(r)`** — Celui-ci est l'aiguilleur qui veille à ce qu'un incident parte vers la bonne voie : il reçoit une réponse et renvoie `True` si elle ne mentionne pas d'« écart de TVA », ou si, la mentionnant, elle contient aussi `"verdict": "escalade"`. Une réponse qui signale l'écart tout en concluant « conforme » viole donc la consigne et le fait renvoyer `False`. Dans le jeu simulé, ce sont les 2 réponses sur la facture FAC-902, qui notent un écart de TVA avec un verdict « conforme », et elles seules.

**`conforme(r)`** — Cette fonction est le jury qui ne délivre son visa qu'à l'unanimité : elle reçoit une réponse, la soumet tour à tour aux quatre vérificateurs du dictionnaire `VERIFICATEURS` et renvoie `True` seulement si tous l'acceptent, grâce à `all`, qui s'arrête au premier refus. Une seule consigne violée rend donc la réponse non conforme. Elle ne lève pas d'exception, puisque chaque vérificateur renvoie un booléen ; `main` additionne ses résultats sur les 200 réponses du jeu simulé et obtient s = 188, le numérateur du taux de conformité.

**`wilson(s, n, z)`** — C'est le statisticien prudent qui refuse d'annoncer un taux sans sa marge d'erreur : il reçoit le nombre de succès, le nombre d'essais et le quantile z, 1,96 par défaut pour 95 %, lève `ValueError` si n est inférieur à 1 ou si s sort de [0, n], puis calcule p = s/n, le centre décalé p + z²/2n, la marge et le dénominateur 1 + z²/n de l'intervalle de Wilson. Il renvoie le couple des bornes, ramenées dans [0, 1] : (0,8981 ; 0,9653) pour 188 sur 200, si bien que la barrière de 90 % n'est pas franchie, et (0,929 ; 1) pour 50 sur 50, là où l'intervalle naïf se réduirait à un point.

**`p_au_moins_une(q, N)`** — Celle-ci est l'oracle pessimiste qui rappelle qu'un événement rare finit toujours par arriver : elle reçoit la probabilité q qu'une réponse viole une consigne et le nombre N de réponses, puis renvoie 1 − (1 − q)ᴺ, la probabilité d'au moins une violation quand les réponses sont indépendantes. Elle ne contrôle pas ses entrées. Avec q = 0,001 et N = 10 000 réponses par jour, elle renvoie 0,99995 : une violation dans la journée est quasi certaine, et `main` imprime aussi l'espérance, 10 violations.

**`borne_zero_violation(n, alpha)`** — Cette fonction est le contrôleur qui, même devant un relevé parfait, refuse de conclure à la perfection : elle reçoit le nombre n de réponses observées sans aucune violation et le risque α, 0,05 par défaut, et renvoie 1 − α puissance 1/n, le plus grand taux de violation encore compatible avec cette observation au niveau de confiance de 95 %. Elle ne lève rien pour n ≥ 1. Pour 300 réponses sans faute, elle renvoie 0,00994, à moins de 0,0002 de la règle de trois, 3/n = 0,01, ce que vérifie le dernier `assert` de `main`.

**`jeu_simule()`** — C'est le metteur en scène qui fabrique une salle de test avec des comédiens dont on connaît d'avance les fautes : la fonction ne reçoit rien et construit 188 réponses JSON conformes qui citent chacune une facture `FAC-0` à `FAC-187`, puis 4 réponses en texte libre, 4 réponses sans numéro de facture, 2 réponses qui « garantissent le paiement » et 2 réponses qui signalent un écart de TVA en concluant « conforme ». Elle renvoie la liste de ces 200 réponses, dont exactement 12 fautives, une seule consigne violée chacune, ce qui permet à `main` de vérifier le tableau 4, 4, 2, 2.

**`main()`** — C'est l'auditeur qui rédige le rapport en cinq rubriques : il calcule le taux de conformité du jeu simulé, 188 sur 200, soit 94 %, et son intervalle de Wilson, constate que la borne basse de 89,81 % reste sous la barrière de 90 %, puis compte les échecs consigne par consigne et exige le tableau 4, 4, 2, 2. Il compare ensuite l'intervalle naïf et l'intervalle de Wilson sur 50 succès sur 50, calcule la probabilité 0,99995 d'au moins une violation sur 10 000 réponses et la borne 0,00994 de la règle de trois pour 300 réponses sans faute. Chaque nombre est vérifié par un `assert` avant la ligne finale.

```python
"""Étape 7 — taux de conformité aux consignes : vérificateurs, Wilson, violations inévitables, règle de trois."""
import json
import math
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def json_valide(r: str) -> bool:
    try:
        json.loads(r)
        return True
    except json.JSONDecodeError:
        return False


def cite_source(r: str) -> bool:
    return re.search(r"FAC-\d+", r) is not None


def sans_formule_interdite(r: str) -> bool:
    return "je garantis" not in r.lower()


def escalade_si_ecart(r: str) -> bool:
    return "écart de TVA" not in r or '"verdict": "escalade"' in r


VERIFICATEURS = {"json": json_valide, "source": cite_source,
                 "interdit": sans_formule_interdite, "escalade": escalade_si_ecart}


def conforme(r: str) -> bool:
    return all(v(r) for v in VERIFICATEURS.values())


def wilson(s: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n < 1 or not 0 <= s <= n:
        raise ValueError("il faut n >= 1 et 0 <= s <= n")
    p = s / n
    centre = p + z * z / (2 * n)
    marge = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    denom = 1 + z * z / n
    return max(0.0, (centre - marge) / denom), min(1.0, (centre + marge) / denom)


def p_au_moins_une(q: float, N: int) -> float:
    return 1 - (1 - q) ** N


def borne_zero_violation(n: int, alpha: float = 0.05) -> float:
    return 1 - alpha ** (1 / n)


def jeu_simule() -> list[str]:
    ok = '{"verdict": "conforme", "facture": "FAC-%d"}'
    reponses = [ok % i for i in range(188)]
    reponses += ["verdict : conforme FAC-900"] * 4                                  # JSON cassé
    reponses += ['{"verdict": "conforme"}'] * 4                                     # source manquante
    reponses += ['{"verdict": "conforme", "facture": "FAC-901", "note": "Je garantis le paiement"}'] * 2
    reponses += ['{"verdict": "conforme", "facture": "FAC-902", "note": "écart de TVA"}'] * 2
    return reponses


def main() -> None:
    reponses = jeu_simule()
    n, s = len(reponses), sum(conforme(r) for r in reponses)
    bas, haut = wilson(s, n)
    print(f"1. Conformité : {s}/{n} = {s / n:.2%}, Wilson 95 % [{bas:.4f} ; {haut:.4f}]")
    assert (s, n) == (188, 200)
    assert (round(bas, 4), round(haut, 4)) == (0.8981, 0.9653)
    seuil = 0.90
    print(f"   barrière à {seuil:.0%} : {'franchie' if bas >= seuil else 'NON franchie'} (borne basse {bas:.2%})")
    assert bas < seuil

    print("2. Échecs par consigne")
    echecs = {nom: sum(not v(r) for r in reponses) for nom, v in VERIFICATEURS.items()}
    for nom, k in echecs.items():
        print(f"   {nom:<9} {k:>2} échec(s)")
    assert echecs == {"json": 4, "source": 4, "interdit": 2, "escalade": 2}

    print("3. Intervalle naïf contre Wilson, 50/50")
    b50, h50 = wilson(50, 50)
    print(f"   naïf [1 ; 1], Wilson [{b50:.3f} ; {h50:.3f}]")
    assert h50 == 1.0 and round(b50, 3) == 0.929

    print("4. Violations inévitables")
    p = p_au_moins_une(0.001, 10_000)
    print(f"   q = 0,001, N = 10 000 : P(au moins une) = {p:.5f}, espérance = {10_000 * 0.001:.0f}")
    assert round(p, 5) == 0.99995

    print("5. Règle de trois")
    qmax = borne_zero_violation(300)
    print(f"   0 violation sur 300 : q_max = {qmax:.5f} (3/n = {3 / 300:.5f})")
    assert round(qmax, 5) == 0.00994 and abs(qmax - 3 / 300) < 0.0002
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Conformité : 188/200 = 94.00%, Wilson 95 % [0.8981 ; 0.9653]
   barrière à 90% : NON franchie (borne basse 89.81%)
2. Échecs par consigne
   json       4 échec(s)
   source     4 échec(s)
   interdit   2 échec(s)
   escalade   2 échec(s)
3. Intervalle naïf contre Wilson, 50/50
   naïf [1 ; 1], Wilson [0.929 ; 1.000]
4. Violations inévitables
   q = 0,001, N = 10 000 : P(au moins une) = 0.99995, espérance = 10
5. Règle de trois
   0 violation sur 300 : q_max = 0.00994 (3/n = 0.01000)
OK — toutes les vérifications sont passées.
```

### Mécanisme du programme, en détail

Le programme traite chaque consigne du prompt comme une petite fonction qui reçoit le texte d'une réponse et renvoie vrai ou faux. `json_valide` tente un `json.loads` et attrape l'exception `JSONDecodeError` : une réponse qui n'est pas du JSON échoue sans arrêter le programme. `cite_source` cherche avec une expression régulière un numéro de facture de la forme `FAC-` suivi de chiffres. `sans_formule_interdite` met le texte en minuscules avant de chercher « je garantis », pour qu'une majuscule ne suffise pas à contourner la règle. `escalade_si_ecart` exprime une implication logique : si la réponse parle d'un écart de TVA, alors elle doit contenir le verdict « escalade » ; sinon la consigne est respectée d'office.

Le dictionnaire `VERIFICATEURS` rassemble ces quatre fonctions, ce qui permet à `conforme` de les appeler toutes avec `all(...)`. `all` s'arrête au premier échec, et c'est exactement la définition d'une réponse conforme : toutes les consignes, sans exception. Le taux observé est ensuite le nombre de réponses conformes divisé par le nombre de réponses.

`wilson` traduit la formule terme à terme : le centre `p + z²/(2n)`, la marge `z × √(p(1−p)/n + z²/(4n²))` et le dénominateur `1 + z²/n`. Les deux `max` et `min` ramènent les bornes dans [0, 1] pour absorber les erreurs d'arrondi des flottants. `p_au_moins_une` calcule le complément de « aucune violation » sur N réponses, et `borne_zero_violation` la règle de trois exacte, 1 − 0,05^(1/n). `jeu_simule` construit 200 réponses dont 12 fautives, réparties de façon à ce que chaque vérificateur en attrape un nombre connu : le programme peut ainsi vérifier à la fois le taux global (188/200) et le tableau des échecs par consigne.

## Squelette algorithmique

L'algorithme mesure un prompt sur un jeu de réponses, puis décide s'il peut partir en production. Il sert de barrière d'intégration continue : le déploiement n'a lieu que si la borne basse de l'intervalle dépasse le seuil.

```text
ALGORITHME BarrièreDeConformité
ENTRÉES : réponses r₁ … rₙ, vérificateurs v₁ … vₘ, seuil, z (1,96 à 95 %)
SORTIE  : (taux, intervalle, échecs par consigne, décision)

  s ← 0
  échecs ← tableau de m compteurs à 0
  POUR CHAQUE réponse r FAIRE
      conforme ← vrai
      POUR CHAQUE vérificateur vⱼ FAIRE
          SI vⱼ(r) = faux ALORS échecs[j] ← échecs[j] + 1 ; conforme ← faux
      FIN POUR
      SI conforme ALORS s ← s + 1
  FIN POUR
  ĉ ← s / n
  (bas, haut) ← Wilson(s, n, z)
  SI bas ≥ seuil ALORS décision ← « déployer » SINON décision ← « refuser »
  RETOURNER ĉ, (bas, haut), échecs, décision
```

**Complexité.** Chaque réponse passe par les m vérificateurs : O(n × m × L), où L est la longueur d'une réponse, parce que chaque vérificateur relit le texte. L'intervalle de Wilson coûte O(1). La mémoire est O(m) pour les compteurs si l'on traite les réponses en flux, sans les garder toutes.

**Du squelette au code.** La boucle intérieure correspond à `VERIFICATEURS` et à `conforme`, le comptage des échecs par consigne au tableau `echecs` de `main`, l'intervalle à `wilson`, et la décision à la comparaison `bas >= seuil` du premier bloc de `main`.

## Cas d'usage réels aux Émirats

Les volumes et seuils sont illustratifs.

### Banque — barrière avant chaque nouvelle version de prompt

Une banque de détail impose qu'un prompt d'agent client ne parte en production que si la borne basse de Wilson dépasse 95 % sur 400 demandes de test. La version 12 obtient 387/400 : ĉ = 96,75 %, mais l'intervalle commence vers 94,5 %. Elle est refusée ; le tableau par consigne montre que 9 des 13 échecs viennent de l'oubli de la mention réglementaire sur les frais, que l'équipe déplace dans un champ obligatoire du schéma de sortie plutôt que dans une phrase du prompt.

### Assurance — sonde quotidienne en production

Un assureur santé tire chaque nuit 200 conversations réelles de son agent et applique les mêmes vérificateurs. Le taux est tracé avec son intervalle ; une alerte part quand la borne haute de la journée passe sous la borne basse de la semaine de référence. C'est ainsi qu'il détecte une baisse après une mise à jour du modèle, sans qu'aucune ligne du prompt ait changé.

### Crypto — consigne qui ne doit jamais céder

Une plateforme agréée par la VARA interdit à son agent toute formulation de conseil en investissement. Avec q = 0,001 et 10 000 conversations par jour, la démonstration montre qu'environ 10 violations quotidiennes sont attendues. La plateforme ajoute donc un filtre de sortie déterministe qui bloque les formules interdites : le prompt réduit q, le filtre rend la consigne effective.

## Pièges et limites

- **Mesurer sur cinquante cas faciles.** L'intervalle sera large, et un jeu non représentatif donne un taux faux avec une belle précision. Le jeu doit couvrir les demandes rares et les demandes piégées.
- **Ne compter que les consignes faciles à vérifier.** Le ton ou la pertinence demandent un juge (humain ou LLM, étape 13 bis) ; le taux de ce fichier ne couvre que les consignes vérifiables par programme.
- **Croire qu'une consigne est respectée parce qu'elle l'a été 300 fois.** La règle de trois laisse jusqu'à 1 % de violations possibles.
- **Supposer l'indépendance.** Une même demande piégée fait échouer la consigne à chaque fois ; on mesure aussi la constance sur des demandes rejouées (pass^k, étape 60).

### Exercice feuille blanche

1. Calculer à la main l'intervalle de Wilson de 45 réponses conformes sur 50. (Réponse : environ [0,786 ; 0,957].)
2. Combien de réponses sans violation faut-il observer pour affirmer, à 95 %, que q < 0,5 % ? (Réponse : n ≥ 598, car

$$
1 - 0{,}05^{1/598} < 0{,}005
$$

.)
3. Ajouter un vérificateur `longueur_max` (moins de 1 200 caractères) et observer comment une seule consigne de plus fait baisser ĉ.

## Pour aller plus loin

- La forme exacte de la réponse se garantit par un schéma, ce qui retire la consigne « JSON valide » du prompt : [étape 8](<../03-Schemas-Outils-et-Premiere-Evaluation/08-Schemas-Definitions-Fondamentaux.md>).
- Le protocole d'évaluation complet (jeu de test, juges, barrière en intégration continue) est à l'[étape 13 bis](<../03-Schemas-Outils-et-Premiere-Evaluation/13b-Evaluation-Definitions-Fondamentaux.md>).

> Suite : [Schémas : définitions](<../03-Schemas-Outils-et-Premiere-Evaluation/08-Schemas-Definitions-Fondamentaux.md>) — étape 8.
