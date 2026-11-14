# Étape 58 — Évaluation — Context Recall

> Étape 58 du parcours · Prérequis : [Context Precision](<57-Evaluation-Formule-Context-Precision.md>) · Suite : [Tool Call F1](<59-Evaluation-Formule-Tool-Call-F1.md>)

**Dossier :** 10-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  
**Nom du fichier :** 58-Evaluation-Formule-Context-Recall.md

## Définition

Le Context Recall mesure si le contexte récupéré contient toutes les informations nécessaires pour produire la réponse de référence (la vérité terrain, écrite par un expert). On découpe la réponse de référence en affirmations atomiques, qu'on ne peut pas couper en deux affirmations vérifiables séparément, puis un juge décide, pour chacune, si un passage du contexte la soutient ; le score est la part d'affirmations soutenues. Le mécanisme est celui de la Faithfulness de l'étape 54, mais la source des affirmations change : la Faithfulness découpe la réponse **générée** et demande « l'agent a-t-il inventé ? », le Context Recall découpe la réponse **de référence** et demande « le retriever a-t-il apporté tout ce qu'il fallait ? ». Quand on connaît les passages de référence, une variante sans LLM compte simplement la part de ces passages présents dans le contexte : c'est le Recall@K de l'étape 25. Si la référence ne contient aucune affirmation, le score n'est pas défini et la fonction renvoie `None`.

## Rôle dans un agent

Le Context Recall se calcule à l'étape **observer**, hors ligne, sur un jeu de questions accompagnées d'une réponse de référence. Il évalue tout ce qui décide de ce qui entre dans le prompt : le retriever, le découpage des documents, la réécriture de la requête, le nombre K de passages et la troncature imposée par le budget de contexte (étape 13 ter). C'est la métrique qui sépare un échec de **retrieval** d'un échec de **génération** : si l'information n'est pas dans le contexte, aucun prompt ne fera répondre juste sans inventer. On le lit avec la Context Precision de l'étape 57, qui mesure l'ordre ; le croisement des deux dit quoi réparer (démonstration, point 6). Dans la barrière d'intégration continue, une baisse du Context Recall moyen bloque un changement d'index, de découpage ou de modèle d'embedding.

## Équation complète

Version par affirmations (celle de RAGAS, avec un juge LLM) :

$$
\text{CR} = \frac{\lvert \{\, a \in A \;:\; \exists\, c \in C,\ \text{juge}(a, c) = 1 \,\} \rvert}{\lvert A \rvert}
$$

Variante par identifiants, sans LLM, quand on connaît les passages de référence :

$$
\text{CR}_{id} = \frac{\lvert \text{Top}_K \cap \text{Ref} \rvert}{\lvert \text{Ref} \rvert}
$$

Conventions :

$$
\lvert A \rvert = 0 \;\Longrightarrow\; \text{CR indéfini} \qquad\qquad C = \varnothing,\ \lvert A \rvert > 0 \;\Longrightarrow\; \text{CR} = 0
$$

Quand chaque affirmation a exactement un passage source, la version par affirmations est un rappel de passages pondéré :

$$
\text{CR} = \frac{\sum_{d \in \text{Ref}} n_d \, [\, d \in \text{Top}_K \,]}{\sum_{d \in \text{Ref}} n_d}
$$

## Décryptage des symboles

$$
A
$$

**Sens :** ensemble des affirmations atomiques extraites de la réponse de référence · **Type / plage :** ensemble fini, éventuellement vide · **Variable Python :** `affirmations`, une `list[Affirmation]`

$$
a
$$

**Sens :** une affirmation de la référence, par exemple « la durée est limitée à 48 mois » · **Type / plage :** élément de A · **Variable Python :** `a`, avec `a.texte` et `a.termes`

$$
C
$$

**Sens :** contexte récupéré, la liste des passages réellement injectés dans le prompt · **Type / plage :** liste de textes · **Variable Python :** `contexte`

$$
c
$$

**Sens :** un passage du contexte · **Type / plage :** texte · **Variable Python :** `c` ou `chunk`

$$
\text{juge}(a, c)
$$

**Sens :** verdict : 1 si le passage c permet de déduire l'affirmation a, 0 sinon ; rendu par un LLM juge, un humain, ou ici un juge par termes clés · **Type / plage :** 0 ou 1 · **Variable Python :** `juge_par_termes(a, chunk)`

$$
\text{CR}
$$

**Sens :** Context Recall, part des affirmations de la référence soutenues par au moins un passage · **Type / plage :** réel dans [0, 1], ou indéfini si A est vide · **Variable Python :** `context_recall(affirmations, contexte)`

$$
\text{Ref}
$$

**Sens :** ensemble des identifiants des passages de référence, ceux qu'un expert a marqués comme nécessaires · **Type / plage :** ensemble fini · **Variable Python :** `references`, ou `PASSAGES_REFERENCE`

$$
\text{Top}_K
$$

**Sens :** ensemble des identifiants des K passages récupérés · **Type / plage :** ensemble d'au plus K éléments · **Variable Python :** `set(retrouves)`

$$
\text{CR}_{id}
$$

**Sens :** variante par identifiants : part des passages de référence présents dans le contexte · **Type / plage :** réel dans [0, 1], ou indéfini si Ref est vide · **Variable Python :** `context_recall_ids(retrouves, references)`

$$
n_d
$$

**Sens :** nombre d'affirmations de la référence que le passage d soutient · **Type / plage :** entier ≥ 0 · **Variable Python :** `poids[d]`

$$
[\, d \in \text{Top}_K \,]
$$

**Sens :** crochet d'Iverson : vaut 1 si le passage d a été récupéré, 0 sinon · **Type / plage :** 0 ou 1 · **Variable Python :** `d in retrouves`

## Démonstration

### 1. Le score est compris entre 0 et 1

Le numérateur compte des affirmations de A, chacune au plus une fois : c'est le cardinal d'un sous-ensemble de A, donc un entier compris entre 0 et |A|. Pour |A| ≥ 1, on divise par |A| > 0 et l'on obtient un nombre de [0, 1]. Le score vaut 1 si et seulement si chaque affirmation a au moins un passage qui la soutient, et 0 si et seulement si aucune n'en a.

### 2. Ajouter des passages ne fait jamais baisser le rappel

Soit deux contextes C ⊆ C′. Si une affirmation est soutenue par un passage c de C, ce même passage est dans C′, donc elle est aussi soutenue dans C′. L'ensemble des affirmations soutenues ne peut que grandir, et le dénominateur |A| ne dépend pas du contexte : CR(C) ≤ CR(C′). En particulier, quand on augmente K sur un même classement, le Context Recall ne baisse jamais, comme le Recall@k de l'étape 25. Le programme le vérifie sur les 729 paires « sous-ensemble, sur-ensemble » d'un corpus de six passages.

Cette propriété est celle d'un juge **idéal**, qui juge chaque affirmation passage par passage. Un juge LLM qui lit tout le contexte d'un coup peut se laisser distraire par des passages ajoutés et changer d'avis. Si le score mesuré baisse quand K augmente, c'est donc le juge qui bruite, pas le retriever : on fixe la version du modèle juge et sa température, on répète la mesure et l'on publie la dispersion (étape 13 bis).

### 3. La variante par identifiants est le Recall@K de l'étape 25

Si Ref est l'ensemble des passages pertinents et Top_K l'ensemble des passages récupérés, la formule de la variante est exactement celle du Recall@k. Elle en hérite toutes les propriétés démontrées à l'étape 25 : elle est dans [0, 1], elle ne baisse jamais quand K augmente, elle est plafonnée par min(1, K/|Ref|), et une question sans passage de référence est indéfinie et sort de la moyenne. Elle ne demande ni LLM ni extraction d'affirmations, ce qui la rend déterministe et bon marché ; en contrepartie, elle exige qu'un expert ait marqué les passages de référence.

### 4. Affirmations et identifiants ne donnent pas le même nombre

On suppose que chaque affirmation de la référence a exactement un passage source, et l'on note n_d le nombre d'affirmations soutenues par le passage d. Les affirmations soutenues par le contexte sont alors exactement celles dont le passage source a été récupéré. On les compte passage par passage :

$$
\text{CR} = \frac{\sum_{d \in \text{Ref}} n_d \, [\, d \in \text{Top}_K \,]}{\sum_{d \in \text{Ref}} n_d}
$$

Le dénominateur vaut |A| parce que chaque affirmation est comptée une fois, chez son unique source. La version par affirmations est donc un rappel de passages **pondéré** par la quantité d'information que porte chaque passage. Sur l'exemple du point 7, le passage pol-12 porte deux affirmations et les deux autres une seule : récupérer pol-12 et pol-14 donne 3/4 = 0,75 en affirmations, mais 2/3 ≈ 0,667 en identifiants. Aucune des deux n'est fausse ; on annonce celle qu'on publie, et l'on ne compare jamais une version à l'autre.

### 5. Référence vide : indéfini ; contexte vide : 0

Une référence sans affirmation, par exemple « cette question ne relève pas de nos politiques », donne 0/0. L'ancien code de ce fichier renvoyait 0,0 et comptait donc la question comme un échec du retriever, alors qu'il n'y avait rien à trouver. On renvoie `None`, on exclut la question de la moyenne et l'on publie le nombre de questions exclues ; ces questions servent ailleurs, à vérifier que l'agent sait répondre « je ne sais pas ». Le cas inverse est bien défini : une référence qui contient des affirmations face à un contexte vide donne 0, parce que rien n'est soutenu, et ce 0 est mérité.

### 6. Croiser précision et rappel : les quatre cas du retrieval

L'ancienne version de ce fichier disait que la Context Precision mesure la « pureté ». C'est inexact : la pureté, c'est-à-dire la part de passages utiles parmi les K récupérés, est la Precision@K de l'étape 26 ; la Context Precision est une précision **pondérée par le rang** (étape 57), qui ignore le bruit placé après le dernier passage utile. Croisée avec le Context Recall, elle sépare quatre situations. Trois sont des échecs du retrieval ; la quatrième dit que l'échec, s'il y en a un, est ailleurs.

| Situation | Context Precision | Context Recall | Ce qui casse | Remède |
|---|---|---|---|---|
| Sain | haute | haut | rien côté retrieval ; si la réponse est fausse, l'erreur vient de la génération (Faithfulness, étape 54) | travailler le prompt ou le modèle |
| Incomplet | haute | bas | des preuves manquent : K trop petit, découpage qui coupe une règle en deux, requête trop étroite | augmenter K, revoir le découpage, réécrire ou multiplier les requêtes, score hybride (étape 23) |
| Noyé | basse | haut | les preuves sont là, mais derrière du bruit, et la troncature peut les couper | reranker, réduire K, filtrer par métadonnées |
| À côté | basse | bas | le retriever cherche ailleurs : embedding inadapté, langue mal normalisée, index périmé | changer ou affiner l'embedding, normaliser l'arabe (étape 22), reconstruire l'index |

Le programme produit un exemple de chaque cas avec les mêmes passages, seulement récupérés différemment : A donne CP = 1 et CR = 1 ; B donne CP = 1 et CR = 0,5 ; C donne CP ≈ 0,383 et CR = 1 ; D donne CP = 0,25 et CR = 0,25. Les seuils utilisés pour classer, 0,7 et 0,8, sont illustratifs.

### 7. Exemple fait à la main (le code reprend ces nombres)

Question d'un conseiller bancaire : « quelles limites s'appliquent à un prêt personnel ? ». La réponse de référence donne quatre affirmations, qui reprennent les règles de la CBUAE : ratio d'endettement total plafonné à 50 % du salaire ; 30 % pour un retraité ; montant limité à 20 fois le salaire ; durée limitée à 48 mois. Les deux premières viennent du passage pol-12, la troisième de pol-13, la quatrième de pol-14. Le retriever renvoie pol-12, faq-3, pol-14 et blog-7 : pol-13 manque.

| Affirmation de la référence | Passage qui la soutient |
|---|---|
| ratio d'endettement total ≤ 50 % du salaire | pol-12 |
| 30 % pour un retraité | pol-12 |
| montant ≤ 20 fois le salaire | aucun |
| durée ≤ 48 mois | pol-14 |

$$
\text{CR} = \frac{3}{4} = 0{,}75 \qquad \text{CR}_{id} = \frac{\lvert \{\text{pol-12}, \text{pol-14}\} \rvert}{\lvert \{\text{pol-12}, \text{pol-13}, \text{pol-14}\} \rvert} = \frac{2}{3} \approx 0{,}667
$$

Avec les poids du point 4, n = 2 pour pol-12 et 1 pour pol-13 et pol-14 :

$$
\frac{2 \times 1 + 1 \times 0 + 1 \times 1}{2 + 1 + 1} = \frac{3}{4} = 0{,}75
$$

L'agent, avec ce contexte, peut valider un prêt de 30 fois le salaire sans avoir vu la règle qui l'interdit : un Context Recall de 0,75 sur une question réglementaire est un échec, pas une note honorable.

## Effets et comportement

- **Augmenter K ne fait jamais baisser le Context Recall** (point 2), mais ajoute du bruit, des tokens et, souvent, fait baisser la Context Precision : on règle K sur les deux.
- **Le score dépend du découpage de la référence en affirmations.** La même référence, découpée en trois ou en cinq affirmations, donne des scores différents ; on garde le même extracteur d'affirmations pour comparer deux versions.
- **Le score ne peut pas dépasser la qualité de la référence.** Une information absente de la référence n'est jamais réclamée ; une référence incomplète fait paraître complet un contexte qui ne l'est pas.
- **Le score ignore l'ordre et le bruit** : un passage utile au rang 10 compte autant qu'au rang 1, tant qu'il est dans le contexte injecté. L'ordre est le rôle de la Context Precision.

## Du symbole au code Python

| Notion | Variable ou fonction |
|---|---|
| A, les affirmations de la référence | `REFERENCE`, une `list[Affirmation]` |
| C, le contexte injecté | `contexte`, une `list[str]` |
| juge(a, c) | `juge_par_termes(a, chunk)`, après `normaliser` |
| CR | `context_recall(affirmations, contexte, juge)` |
| Ref et Top_K | `PASSAGES_REFERENCE` et `retrouves` |
| CR par identifiants | `context_recall_ids(retrouves, references)` |
| n_d | `poids[d]` |
| CP@K de l'étape 57 | `context_precision(v)` |
| les quatre cas | `diagnostic(cp, cr, seuil_cp, seuil_cr)` |

### Déroulé, ligne par ligne

**`normaliser(texte)`** applique `unicodedata.normalize("NFKC", texte)`, qui remplace notamment l'espace insécable U+00A0 et l'espace fine U+202F par une espace ordinaire, puis `casefold()`, une mise en minuscules plus complète que `lower()`, et enfin `" ".join(texte.split())`, qui réduit toute suite d'espaces à une seule. Le passage pol-12 écrit « 50 % » avec une espace insécable : sans cette normalisation, le terme « 50 % » ne serait pas trouvé, et l'affirmation serait déclarée non soutenue à tort.

**`Affirmation`** est une `dataclass` figée : le texte de l'affirmation et le tuple des termes clés que le juge simplifié doit trouver.

**`juge_par_termes(aff, chunk)`** remplace le juge LLM par une règle déterministe : l'affirmation est soutenue si **tous** ses termes clés figurent dans le **même** passage, après normalisation. Pour « la durée est limitée à 48 mois », le seul terme est « 48 mois », présent dans pol-14. En production, cette fonction appelle un LLM juge à qui l'on donne l'affirmation et le passage.

**`context_recall(affirmations, contexte, juge)`** est la formule.

- `if not affirmations: return None` : référence vide, le score n'est pas défini (point 5). L'ancien code renvoyait `0.0` ici.
- `any(juge(a, c) for c in contexte)` vaut `True` dès qu'un passage soutient l'affirmation a : c'est le « il existe » de la formule. Pour un contexte vide, `any` d'une suite vide vaut `False`, et le score vaut 0.
- `soutenues / len(affirmations)` : sur l'exemple, 3 / 4 = 0,75.

**`context_recall_ids(retrouves, references)`** renvoie `None` si `references` est vide, sinon `len(set(retrouves) & references) / len(references)` : `{'pol-12', 'pol-14'}` sur trois références, soit 0,6667. Le `set` retire un éventuel doublon dans la liste récupérée.

**`context_precision(v)`** est recopiée de l'étape 57 pour le diagnostic croisé : un seul bloc exécutable doit tout contenir.

**`diagnostic(cp, cr, seuil_cp, seuil_cr)`** applique le tableau du point 6 : quatre branches, dans l'ordre sain, incomplet, noyé, à côté.

**`CORPUS`, `REFERENCE` et `PASSAGES_REFERENCE`** décrivent le cas bancaire : six passages, dont trois réglementaires, et quatre affirmations de référence.

**`main()`**, bloc par bloc.

1. L'exemple à la main : pour chaque affirmation, `next(...)` cherche le premier passage récupéré qui la soutient, ou « aucun ». Puis CR = 0,75 et CR par identifiants = 0,6667. Le dictionnaire `poids` compte, pour chaque passage de référence, les affirmations qu'il soutient : `{'pol-12': 2, 'pol-13': 1, 'pol-14': 1}`, et le rappel pondéré redonne exactement 0,75 (point 4).
2. La monotonie du point 2 : `itertools.combinations` produit les 64 sous-ensembles des six passages ; pour chaque paire « petit ⊆ grand », 729 au total, le rappel du petit ne dépasse pas celui du grand. Puis la courbe pour K = 1 à 5 sur un classement fixe : 0 ; 0,5 ; 0,5 ; 0,75 ; 1, qui ne baisse jamais.
3. Les conventions : référence vide et références vides → `None`, contexte vide → 0,0 ; puis la preuve que la normalisation est nécessaire : le texte brut de pol-12, mis en minuscules, ne contient pas « 50 % » avec une espace ordinaire.
4. Les quatre scénarios du point 6, avec leur CP, leur CR et leur diagnostic, chacun vérifié par `assert`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`context_recall(affirmations, contexte, juge)`** — Cette fonction est l'avocate qui, avant l'audience, coche une à une les affirmations de la référence en cherchant pour chacune une pièce du dossier qui la soutienne : elle reçoit la liste des affirmations, la liste des passages injectés dans le contexte et un juge, par défaut `juge_par_termes`, renvoie `None` si la référence ne contient aucune affirmation, puis compte celles pour lesquelles au moins un passage est jugé favorable. Elle renvoie ce compte divisé par le nombre d'affirmations : 3 sur 4, soit 0,75, pour le contexte de l'exemple, où le montant limité à 20 fois le salaire ne trouve aucune source, et 0 pour un contexte vide, puisqu'aucune pièce ne peut alors soutenir quoi que ce soit.

**`context_recall_ids(retrouves, references)`** — Celle-ci est la variante du greffier pressé, qui ne lit pas les pièces mais vérifie seulement leurs cotes : elle reçoit la liste des identifiants récupérés et l'ensemble des identifiants de référence, renvoie `None` si cet ensemble est vide, et sinon la part des références présentes parmi les récupérés, après passage par `set` pour qu'un doublon ne compte qu'une fois. Avec pol-12 et pol-14 retrouvés sur trois passages de référence, elle donne 0,6667, un peu moins que les 0,75 du rappel par affirmations, parce que pol-12 soutient à lui seul deux affirmations ; `main` montre que le rappel pondéré par ce nombre d'affirmations redonne exactement 0,75.

**`context_precision(v)`** — Cette fonction est la même que dans le programme de l'étape 57, recopiée ici pour que le bloc se suffise à lui-même : elle reçoit la liste des verdicts 0 ou 1 dans l'ordre des rangs, renvoie `None` si elle est vide, 0 si aucun passage n'est pertinent, et sinon la moyenne des Precision@k prises aux rangs pertinents. Cette copie n'a pas la garde qui refusait un verdict autre que 0 ou 1. Elle fournit la moitié du diagnostic croisé : 1 pour le scénario A, 0,3833 pour le scénario C, où les trois bons passages arrivent en fin de liste, et 0,25 pour le scénario D.

**`diagnostic(cp, cr, seuil_cp, seuil_cr)`** — Celle-ci est le médecin qui lit deux analyses côte à côte avant de rendre son avis : elle reçoit la Context Precision, le Context Recall et deux seuils illustratifs, 0,7 pour la précision et 0,8 pour le rappel, puis parcourt quatre branches dans l'ordre. Elle renvoie « retrieval sain » quand les deux mesures passent leur seuil, « incomplet » quand le rappel seul est trop bas, « noyé » quand le rappel passe mais pas la précision, et « à côté » quand les deux échouent ; les scénarios A, B, C et D de `main` tombent chacun dans l'une de ces quatre cases.

**`main()`** — C'est le chef d'orchestre des quatre démonstrations : il cherche, pour chaque affirmation de la référence, le premier passage récupéré qui la soutient, calcule le rappel 0,75 et sa variante par identifiants 0,6667, puis le rappel pondéré qui redonne 0,75. Il vérifie ensuite la monotonie sur les 64 sous-ensembles des six passages, soit 729 paires « petit inclus dans grand », et la courbe 0, 0,5, 0,5, 0,75, 1 pour K = 1 à 5, contrôle les conventions et la nécessité de la normalisation des espaces insécables, enfin passe les quatre scénarios au diagnostic croisé ; « OK » n'apparaît que si tout concorde.

```python
"""Étape 58 — Context Recall : affirmations de la référence couvertes par le contexte, variante par identifiants, diagnostic."""
import itertools
import math
import sys
import unicodedata
from dataclasses import dataclass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def normaliser(texte: str) -> str:
    """NFKC (espaces insécables → espace), minuscules sans casse, espaces multiples réduits."""
    return " ".join(unicodedata.normalize("NFKC", texte).casefold().split())


@dataclass(frozen=True)
class Affirmation:
    texte: str
    termes: tuple[str, ...]          # ce que le juge simplifié doit trouver dans un même chunk


def juge_par_termes(aff: Affirmation, chunk: str) -> bool:
    """Juge déterministe qui remplace le juge LLM : tous les termes clés figurent dans le chunk."""
    c = normaliser(chunk)
    return all(normaliser(t) in c for t in aff.termes)


def context_recall(affirmations: list[Affirmation], contexte: list[str], juge=juge_par_termes) -> float | None:
    """|affirmations de la référence soutenues par le contexte| / |affirmations de la référence| ; None si aucune."""
    if not affirmations:
        return None
    soutenues = sum(1 for a in affirmations if any(juge(a, c) for c in contexte))
    return soutenues / len(affirmations)


def context_recall_ids(retrouves: list[str], references: set[str]) -> float | None:
    """Variante sans LLM : |retrouvés ∩ références| / |références| ; None si aucune référence."""
    if not references:
        return None
    return len(set(retrouves) & references) / len(references)


def context_precision(v: list[int]) -> float | None:
    """Étape 57, recopiée pour le diagnostic croisé."""
    if not v:
        return None
    r = sum(v)
    if r == 0:
        return 0.0
    total, vus = 0.0, 0
    for k, vk in enumerate(v, start=1):
        if vk:
            vus += 1
            total += vus / k
    return total / r


def diagnostic(cp: float, cr: float, seuil_cp: float = 0.7, seuil_cr: float = 0.8) -> str:
    """Croise précision pondérée par le rang et rappel ; les seuils sont illustratifs."""
    if cr >= seuil_cr and cp >= seuil_cp:
        return "retrieval sain : chercher l'erreur dans la génération"
    if cr < seuil_cr and cp >= seuil_cp:
        return "incomplet : il manque des preuves"
    if cr >= seuil_cr:
        return "noyé : les preuves sont là mais mal classées"
    return "à côté : ni les bonnes preuves ni le bon ordre"


CORPUS = {
    "pol-12": "Ratio d'endettement total : au plus 50 % du salaire, toutes mensualités comprises ; 30 % pour un retraité.",
    "pol-13": "Montant maximal d'un prêt personnel : 20 fois le salaire mensuel.",
    "pol-14": "Durée maximale d'un prêt personnel : 48 mois.",
    "faq-3": "Les cartes de crédit sont soumises à des frais annuels.",
    "faq-9": "Le virement international se fait en AED ou en USD.",
    "blog-7": "Cinq conseils pour épargner chaque mois.",
}
REFERENCE = [
    Affirmation("le ratio d'endettement total est plafonné à 50 % du salaire", ("endettement", "50 %")),
    Affirmation("le plafond est de 30 % pour un retraité", ("30 %", "retraité")),
    Affirmation("le montant est limité à 20 fois le salaire", ("20 fois", "salaire")),
    Affirmation("la durée est limitée à 48 mois", ("48 mois",)),
]
PASSAGES_REFERENCE = {"pol-12", "pol-13", "pol-14"}


def main() -> None:
    print("1. Exemple à la main : quatre affirmations, quatre passages récupérés")
    retrouves = ["pol-12", "faq-3", "pol-14", "blog-7"]
    contexte = [CORPUS[i] for i in retrouves]
    for a in REFERENCE:
        source = next((i for i in retrouves if juge_par_termes(a, CORPUS[i])), "aucun")
        print(f"   {a.texte:<62} → {source}")
    cr, cr_ids = context_recall(REFERENCE, contexte), context_recall_ids(retrouves, PASSAGES_REFERENCE)
    print(f"   Context Recall (affirmations) = {cr:.4f}   variante par identifiants = {cr_ids:.4f}")
    assert cr == 0.75 and math.isclose(cr_ids, 2 / 3)

    # Chaque affirmation n'a qu'une source : le rappel par affirmations est un rappel de passages pondéré
    poids = {d: sum(1 for a in REFERENCE if juge_par_termes(a, CORPUS[d])) for d in sorted(PASSAGES_REFERENCE)}
    pondere = sum(w for d, w in poids.items() if d in retrouves) / sum(poids.values())
    print(f"   affirmations par passage : {poids} → rappel pondéré = {pondere:.4f}")
    assert poids == {"pol-12": 2, "pol-13": 1, "pol-14": 1} and pondere == cr

    print("2. Ajouter des passages ne fait jamais baisser le rappel (64 sous-ensembles × leurs sur-ensembles)")
    ids = sorted(CORPUS)
    sous_ensembles = [set(s) for n in range(len(ids) + 1) for s in itertools.combinations(ids, n)]
    paires = 0
    for petit in sous_ensembles:
        for grand in sous_ensembles:
            if petit <= grand:
                assert context_recall(REFERENCE, [CORPUS[i] for i in sorted(petit)]) <= \
                    context_recall(REFERENCE, [CORPUS[i] for i in sorted(grand)])
                paires += 1
    courbe = [context_recall(REFERENCE, [CORPUS[i] for i in ["faq-3", "pol-12", "blog-7", "pol-14", "pol-13"][:k]])
              for k in range(1, 6)]
    print(f"   {paires} paires vérifiées ; courbe K = 1..5 : {courbe}")
    assert courbe == [0.0, 0.5, 0.5, 0.75, 1.0]

    print("3. Conventions")
    print(f"   référence sans affirmation : {context_recall([], contexte)}   aucune référence : {context_recall_ids(retrouves, set())}")
    print(f"   contexte vide : {context_recall(REFERENCE, [])}")
    assert context_recall([], contexte) is None and context_recall_ids(retrouves, set()) is None
    assert context_recall(REFERENCE, []) == 0.0
    assert juge_par_termes(REFERENCE[0], CORPUS["pol-12"])                  # « 50 % » normalisé en « 50 % »
    assert "50 %" not in CORPUS["pol-12"].casefold()                        # sans NFKC, le juge raterait l'affirmation

    print("4. Les quatre façons dont un retrieval peut se présenter")
    scenarios = {
        "A": ["pol-12", "pol-13", "pol-14", "faq-3"],
        "B": ["pol-12", "faq-3", "blog-7", "faq-9"],
        "C": ["faq-3", "blog-7", "faq-9", "pol-12", "pol-13", "pol-14"],
        "D": ["faq-3", "blog-7", "faq-9", "pol-14"],
    }
    attendus = {"A": (1.0, 1.0), "B": (1.0, 0.5), "C": ((1 / 4 + 2 / 5 + 3 / 6) / 3, 1.0), "D": (0.25, 0.25)}
    for nom, liste in scenarios.items():
        v = [1 if i in PASSAGES_REFERENCE else 0 for i in liste]
        cp, cr = context_precision(v), context_recall(REFERENCE, [CORPUS[i] for i in liste])
        print(f"   {nom} v = {v!s:<19} CP = {cp:.4f}  CR = {cr:.2f}  → {diagnostic(cp, cr)}")
        assert math.isclose(cp, attendus[nom][0]) and math.isclose(cr, attendus[nom][1])
    assert diagnostic(0.38, 1.0).startswith("noyé") and diagnostic(1.0, 0.5).startswith("incomplet")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Exemple à la main : quatre affirmations, quatre passages récupérés
   le ratio d'endettement total est plafonné à 50 % du salaire    → pol-12
   le plafond est de 30 % pour un retraité                        → pol-12
   le montant est limité à 20 fois le salaire                     → aucun
   la durée est limitée à 48 mois                                 → pol-14
   Context Recall (affirmations) = 0.7500   variante par identifiants = 0.6667
   affirmations par passage : {'pol-12': 2, 'pol-13': 1, 'pol-14': 1} → rappel pondéré = 0.7500
2. Ajouter des passages ne fait jamais baisser le rappel (64 sous-ensembles × leurs sur-ensembles)
   729 paires vérifiées ; courbe K = 1..5 : [0.0, 0.5, 0.5, 0.75, 1.0]
3. Conventions
   référence sans affirmation : None   aucune référence : None
   contexte vide : 0.0
4. Les quatre façons dont un retrieval peut se présenter
   A v = [1, 1, 1, 0]        CP = 1.0000  CR = 1.00  → retrieval sain : chercher l'erreur dans la génération
   B v = [1, 0, 0, 0]        CP = 1.0000  CR = 0.50  → incomplet : il manque des preuves
   C v = [0, 0, 0, 1, 1, 1]  CP = 0.3833  CR = 1.00  → noyé : les preuves sont là mais mal classées
   D v = [0, 0, 0, 1]        CP = 0.2500  CR = 0.25  → à côté : ni les bonnes preuves ni le bon ordre
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : le Context Recall est un rappel d'affirmations, qui ne baisse jamais quand le contexte grandit, et qui se lit avec la Context Precision. À eux deux, ils disent si l'information manque, si elle est noyée, si le retriever cherche ailleurs, ou si l'erreur est dans la génération.

## Squelette algorithmique

Quatre algorithmes, dont deux principaux. CONTEXT_RECALL_PAR_AFFIRMATIONS prend les affirmations de la référence, les passages du contexte et un juge, et rend la part d'affirmations soutenues : pour chaque affirmation, on cherche **un** passage qui la soutient, et l'on s'arrête dès qu'on l'a trouvé. JUGE_PAR_TERMES est le juge simplifié du programme, qui remplace le juge LLM. CONTEXT_RECALL_PAR_IDENTIFIANTS prend les identifiants récupérés et les identifiants de référence, et rend la part de références présentes. DIAGNOSTIC croise ensuite le rappel avec la Context Precision de l'étape 57.

```text
ALGORITHME CONTEXT_RECALL_PAR_AFFIRMATIONS
ENTRÉES : A[1..n], affirmations de la référence ; C[1..K], passages du contexte injecté ;
          JUGE(a, c), qui répond VRAI si le passage c soutient l'affirmation a
SORTIE  : CR, ou INDÉFINI si n = 0

  SI n = 0 ALORS RETOURNER INDÉFINI FIN SI
  soutenues ← 0
  POUR i de 1 à n FAIRE
      k ← 1 ; trouvée ← FAUX
      TANT QUE k ≤ K ET NON trouvée FAIRE          ▷ « il existe un passage qui soutient A[i] »
          SI JUGE(A[i], C[k]) ALORS trouvée ← VRAI FIN SI
          k ← k + 1
      FIN TANT QUE
      SI trouvée ALORS soutenues ← soutenues + 1 FIN SI
  FIN POUR
  RETOURNER soutenues / n
```

```text
ALGORITHME JUGE_PAR_TERMES
ENTRÉES : a, avec ses termes clés t[1..T] ; c, un passage
SORTIE  : VRAI si tous les termes figurent dans c, après normalisation

  texte ← NORMALISER(c)                            ▷ NFKC, minuscules sans casse, espaces réduits
  POUR j de 1 à T FAIRE
      SI NORMALISER(t[j]) n'apparaît pas dans texte ALORS RETOURNER FAUX FIN SI
  FIN POUR
  RETOURNER VRAI
```

```text
ALGORITHME CONTEXT_RECALL_PAR_IDENTIFIANTS
ENTRÉES : TopK[1..K], identifiants récupérés ; Ref, ensemble des identifiants de référence
SORTIE  : CR_id, ou INDÉFINI si Ref est vide

  SI Ref est vide ALORS RETOURNER INDÉFINI FIN SI
  RETOURNER |ensemble(TopK) ∩ Ref| / |Ref|
```

```text
ALGORITHME DIAGNOSTIC
ENTRÉES : CP, CR ; seuils s_cp et s_cr (illustratifs : 0,7 et 0,8)
SORTIE  : l'une des quatre situations du point 6

  SI CR ≥ s_cr ET CP ≥ s_cp ALORS RETOURNER « sain »
  SINON SI CR < s_cr ET CP ≥ s_cp ALORS RETOURNER « incomplet »
  SINON SI CR ≥ s_cr ALORS RETOURNER « noyé »
  SINON RETOURNER « à côté »
  FIN SI
```

**Complexité :** on note n le nombre d'affirmations, K le nombre de passages, T le nombre maximal de termes par affirmation, L la longueur maximale d'un passage et ℓ celle d'un terme, en caractères. JUGE_PAR_TERMES normalise le passage en O(L), puis fait au plus T recherches de sous-chaîne, chacune en O(L × ℓ) dans le pire cas et souvent proche de O(L) en pratique : O(L + T × L × ℓ) en temps et O(L) en mémoire pour la copie normalisée. CONTEXT_RECALL_PAR_AFFIRMATIONS appelle le juge au plus n × K fois, d'où O(n × K × (L + T × L × ℓ)) dans le pire cas ; la boucle TANT QUE s'arrête au premier passage qui soutient l'affirmation, ce qui réduit le coût moyen sans changer le pire cas. Le code renormalise le passage à chaque appel du juge, ce qui multiplie par n le coût des normalisations : les normaliser une fois au départ coûterait O(K × L) de mémoire et ramènerait ce terme à O(K × L). Avec un juge LLM, la mesure qui compte est le nombre d'appels : jusqu'à n × K si l'on juge affirmation par affirmation et passage par passage, comme le recommande le point 2, ou n si le juge lit tout le contexte d'un coup. CONTEXT_RECALL_PAR_IDENTIFIANTS construit un ensemble de K éléments puis teste |Ref| appartenances en O(1) en moyenne chacune : O(K + |Ref|) en temps, O(K) en mémoire. DIAGNOSTIC fait au plus trois comparaisons doubles : O(1). La vérification de monotonie du programme, sur les 729 paires de sous-ensembles d'un corpus de six passages, est une preuve par énumération, exponentielle en la taille du corpus.

**Du squelette au code :** CONTEXT_RECALL_PAR_AFFIRMATIONS est `context_recall(affirmations, contexte, juge)`. Sa première ligne est `if not affirmations: return None` ; la boucle TANT QUE avec son arrêt anticipé est `any(juge(a, c) for c in contexte)`, parce que `any` s'arrête au premier `True` ; le compteur `soutenues` est `sum(1 for a in affirmations if …)` ; le RETOURNER est `soutenues / len(affirmations)`. JUGE_PAR_TERMES est `juge_par_termes(aff, chunk)` : NORMALISER est `normaliser(texte)`, et la boucle POUR avec son RETOURNER FAUX anticipé est `all(normaliser(t) in c for t in aff.termes)`, parce que `all` s'arrête au premier `False`. CONTEXT_RECALL_PAR_IDENTIFIANTS est `context_recall_ids(retrouves, references)`, avec `set(retrouves) & references` pour l'intersection. DIAGNOSTIC est `diagnostic(cp, cr, seuil_cp, seuil_cr)`, dont les quatre `return` suivent les quatre branches dans le même ordre. Le calcul de CP qu'il consomme vient de `context_precision(v)`, recopiée de l'étape 57.

## Cas d'usage réels aux Émirats

Les volumes, les scores et les seuils ci-dessous sont illustratifs ; seules les règles réglementaires citées sont réelles.

### Banque — la règle coupée par le découpage

L'assistant de conformité d'une banque de détail de Dubaï répond aux conseillers sur les prêts personnels. Pour la question des limites, la réponse de référence contient quatre affirmations issues des règles de la CBUAE (ratio d'endettement total d'au plus 50 % du salaire, 30 % pour un retraité, montant d'au plus 20 fois le salaire, durée d'au plus 48 mois), et le Context Recall mesuré vaut 0,75 : la règle des 20 fois le salaire manque au contexte. L'analyse montre que le découpage par blocs de taille fixe avait coupé le tableau des plafonds en deux, et que la moitié qui contenait le montant maximal ne ressemblait plus à la question. L'équipe passe à un découpage qui respecte les sections du document, et le rappel remonte à 1 sur cette question. Sans la métrique, l'erreur aurait été attribuée au modèle, et l'équipe aurait réécrit le prompt pour un défaut qui venait de l'index. La barrière de mise en production exige un Context Recall moyen d'au moins 0,95 sur les questions réglementaires, publié avec le nombre de questions exclues faute de référence. L'indicateur suivi est le Context Recall moyen par famille de produits, recalculé à chaque réindexation.

### Immobilier — tous les frais d'un achat

L'agent d'une agence immobilière de Dubaï répond aux acheteurs sur les frais d'une acquisition. Pour « quels frais paie l'acheteur d'un appartement neuf ? », la référence contient plusieurs affirmations, dont deux qui reposent sur des règles réelles : les frais de transfert du DLD valent 4 % de la valeur du bien, et la première livraison d'un bien résidentiel neuf est au taux zéro de TVA. Le contexte récupéré contient bien la page du DLD mais pas la note fiscale : le Context Recall vaut 0,5 sur ces deux affirmations, et l'agent risque d'appliquer 5 % de TVA à un prix qui n'en supporte pas. La variante par identifiants, qui demande seulement si la note fiscale fait partie des passages récupérés, suffit ici : elle est déterministe et ne coûte aucun appel de juge. L'agence la calcule à chaque mise à jour de sa base documentaire et garde la version par affirmations pour un échantillon mensuel. L'indicateur suivi est la part des questions sur les frais dont tous les passages de référence sont récupérés.

### Assurance — la même métrique que la fidélité, retournée

L'assistant des gestionnaires de sinistres d'un assureur auto et santé est évalué avec deux métriques construites de la même façon. La Faithfulness (étape 54) découpe la réponse générée et vérifie qu'elle n'invente rien ; le Context Recall découpe la décision de référence rédigée par un gestionnaire expérimenté et vérifie que le contexte contenait de quoi la prendre. Sur un sinistre de test, la réponse est parfaitement fidèle, Faithfulness = 1, mais le Context Recall vaut 0,67 : l'exclusion « conduite sans permis valide » n'a pas été récupérée, et la réponse fidèle à un contexte incomplet conclut à une prise en charge. Le diagnostic croisé de la démonstration, point 6, classe ce cas en « incomplet » ; l'équipe ajoute une deuxième requête dédiée aux exclusions. L'assureur est supervisé par la CBUAE et la décision reste humaine. Les indicateurs suivis sont le Context Recall des exclusions, publié à part, et le taux de décisions révisées après contestation.

### RH — l'exception qui vit dans un autre document

Un cabinet RH présent dans plusieurs émirats répond aux salariés sur l'indemnité de fin de service. La référence d'une question type contient les règles du décret-loi fédéral 33/2021 pour le secteur privé (au moins un an de service, 21 jours de salaire de base par an pendant les cinq premières années, 30 jours au-delà, plafond de 24 mois de salaire de base) et deux exceptions : les ressortissants émiriens relèvent de la GPSSA, et les salariés du DIFC ont leur propre régime. Les règles générales sont dans un même guide, les exceptions dans deux documents distincts, rarement récupérés. Quand seul le guide général est récupéré, le Context Recall par affirmations, qui pèse chaque passage par son nombre d'affirmations (point 4), donne 4/6 ≈ 0,67, alors que la variante par identifiants, qui ne trouve qu'un des trois passages de référence, donne 1/3 ≈ 0,33 : les deux nombres racontent la même panne avec des poids différents. Le cabinet publie la variante par affirmations, qui reflète ce que le salarié lira, mais bloque toute version qui rate une exception, parce qu'une indemnité promise à tort engage l'employeur. L'indicateur suivi est le rappel des affirmations d'exception, question par question.

### BTP — les règles fiscales d'une facture de sous-traitant

Un groupe de construction qui travaille sur de grands chantiers à Dubaï fait vérifier les factures de ses sous-traitants par un agent. Pour « quelles règles s'appliquent à cette facture ? », la référence contient la TVA standard de 5 %, la retenue de garantie prévue au contrat du sous-traitant et les conditions de paiement du contrat. Le retriever trouve sans difficulté la règle de TVA, commune à toutes les factures, mais rate souvent l'avenant au contrat qui modifie la retenue de garantie, parce que l'avenant est un document court et peu ressemblant à la question. Le Context Recall par affirmations tombe alors à 2/3 et l'agent applique la retenue d'origine, ce qui bloque à tort une partie du paiement dû. L'équipe ajoute un filtre par métadonnées qui récupère d'office tous les documents du contrat concerné avant la recherche sémantique, et le rappel remonte. L'indicateur suivi est le Context Recall moyen sur les factures de test qui ont un avenant.

### Secteur public — un juge bilingue qui doit rester stable

Un service public en ligne accessible par UAE Pass évalue son retrieval avec un juge LLM qui décide, affirmation par affirmation, si un passage la soutient ; les questions et les passages sont en arabe ou en anglais. Lors d'une première campagne, le Context Recall de certaines questions baissait quand on augmentait K, ce que le point 2 interdit pour un juge idéal : le juge, qui lisait tout le contexte d'un coup, se laissait distraire par les passages ajoutés. L'équipe fait désormais juger chaque affirmation passage par passage, fixe la version du modèle juge et sa température, et rejoue chaque mesure trois fois pour publier la dispersion. Les questions hors périmètre, sans affirmation de référence, renvoient `None`, sortent de la moyenne et servent de tests d'abstention. Les données des usagers sont soumises à la PDPL : les références sont rédigées sur des questions anonymisées. Les indicateurs suivis sont le Context Recall par langue et l'écart entre trois répétitions d'une même mesure.

## Pièges et limites

- **Confondre Context Recall et Faithfulness.** Les deux comptent des affirmations soutenues par le contexte, mais pas les mêmes : celles de la référence pour le premier, celles de la réponse générée pour la seconde.
- **Renvoyer 0 pour une référence vide.** La question n'avait rien à trouver ; on renvoie `None`, on l'exclut et l'on publie le nombre d'exclues.
- **Changer d'extracteur d'affirmations ou de juge entre deux versions.** Le score dépend du découpage et du juge ; on les fige pour comparer.
- **Mélanger la version par affirmations et la version par identifiants.** Elles pondèrent différemment les passages (point 4) et ne se comparent pas entre elles.
- **Lire un Context Recall élevé comme un retrieval réussi.** Il ne dit rien de l'ordre ni du bruit : on le croise toujours avec la Context Precision.

### Exercice feuille blanche

1. Sans regarder le code, écrire `context_recall` et `context_recall_ids`, avec `None` pour une référence vide, puis vérifier 0,75 et 0,667 sur l'exemple du point 7.
2. Prédire, puis vérifier : si le retriever renvoie seulement pol-13 et pol-14, que valent les deux versions ? (Réponse : 2/4 = 0,5 en affirmations, 2/3 ≈ 0,667 en identifiants ; cette fois, c'est la version par identifiants qui est la plus haute, parce que le passage manquant, pol-12, porte deux affirmations.)
3. Trouver le bug : `soutenues = sum(1 for c in contexte if any(juge(a, c) for a in affirmations))`. Que compte cette ligne, combien vaut le score sur l'exemple (réponse : 2/4 = 0,5), et pourquoi ce numérateur est-il celui de la Precision@K de l'étape 26 plutôt que celui d'un rappel ?

## Pour aller plus loin

RAGAS propose aussi un Context Recall sans LLM qui compare les passages récupérés à des passages de référence par une distance entre chaînes de caractères, et un rappel d'entités (Context Entity Recall) qui compte les entités nommées de la référence (montants, dates, noms d'autorités) présentes dans le contexte. Quand certaines affirmations comptent plus que d'autres, par exemple une exclusion de garantie face à une formule de politesse, on peut pondérer chaque affirmation par son importance ; la formule reste un rappel, avec des poids au numérateur et au dénominateur, comme au point 4.

> Suite : [Tool Call F1](<59-Evaluation-Formule-Tool-Call-F1.md>) — étape 59.
