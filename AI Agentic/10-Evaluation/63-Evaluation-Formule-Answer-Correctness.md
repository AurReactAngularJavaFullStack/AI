# Étape 63 — Évaluation — Answer Correctness (simplifiée)

> Étape 63 du parcours · Prérequis : [Perplexité en évaluation](<62-Evaluation-Formule-Perplexite.md>) · Suite : [Exact Match](<64-Evaluation-Formule-Exact-Match.md>)

**Dossier :** 10-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Product Engineers  
**Nom du fichier :** 63-Evaluation-Formule-Answer-Correctness.md

## Définition

Answer Correctness mesure si la réponse de l'agent est **juste** par rapport à une réponse de référence écrite par un expert (la *ground truth*). Elle combine deux signaux. Le premier, qui domine, est une **F1 des faits** : on découpe la réponse et la référence en affirmations élémentaires, puis on compte les affirmations justes (présentes des deux côtés), inventées (seulement dans la réponse) et oubliées (seulement dans la référence). Le second est une **similarité sémantique** entre les embeddings de la réponse et de la référence, qui récompense une formulation proche. Dans l'implémentation de référence RAGAS, la F1 des faits pèse 0,75 et la similarité 0,25 : l'ancienne version de ce fichier faisait l'inverse, ou mettait 0,5 partout, ce qui laisse passer une réponse bien écrite mais fausse. La similarité est bornée à 0, parce qu'un cosinus peut être négatif et qu'un score de justesse ne doit pas l'être.

## Rôle dans un agent

Answer Correctness sert au moment où l'on **évalue** l'agent, hors ligne, sur un jeu de questions dont la réponse attendue est connue (étape 13 bis). Elle complète les deux métriques qui la précèdent dans le parcours. La fidélité (étape 54) vérifie que la réponse s'appuie sur le contexte récupéré, mais un contexte faux donne une réponse fidèle et fausse. Answer Relevancy (étape 55) vérifie que la réponse parle de la question, mais une réponse hors sujet bien tournée y échappe mal, et une réponse dans le sujet avec un chiffre faux y échappe complètement. Answer Correctness compare directement le contenu à la référence. Le composant concerné est le **juge** : un LLM extrait et classe les affirmations, un modèle d'embedding calcule la similarité, et la barrière de déploiement compare la moyenne à un seuil. En production, elle ne peut se calculer que sur l'échantillon de conversations pour lesquelles un expert a écrit une référence.

## Équation complète

Score de justesse, avec des poids positifs de somme 1 (RAGAS : 0,75 et 0,25) :

$$
\text{AC} = w_{\text{fait}} \cdot F_1^{\text{faits}} + w_{\text{sim}} \cdot \max(0,\, \text{sim}), \qquad w_{\text{fait}} = 0{,}75, \quad w_{\text{sim}} = 0{,}25
$$

Classement des affirmations, A étant l'ensemble des affirmations de la réponse et G celui de la référence :

$$
TP = |A \cap G|, \qquad FP = |A \setminus G|, \qquad FN = |G \setminus A|
$$

F1 des faits, sous la forme qu'utilise RAGAS :

$$
F_1^{\text{faits}} = \frac{TP}{TP + \tfrac{1}{2}(FP + FN)}
$$

Similarité sémantique entre les embeddings de la réponse et de la référence (étape 14) :

$$
\text{sim} = \cos(E_{\text{réponse}},\, E_{\text{réf}}) \in [-1,\, 1]
$$

F1 minimale qu'il faut atteindre pour franchir un seuil τ, à similarité donnée :

$$
\text{AC} \ge \tau \iff F_1^{\text{faits}} \ge \frac{\tau - w_{\text{sim}} \max(0, \text{sim})}{w_{\text{fait}}}
$$

## Décryptage des symboles

$$
A,\; G
$$

**Sens :** ensemble des affirmations élémentaires de la réponse, et de la référence (*ground truth*) · **Type / plage :** ensembles finis de faits normalisés · **Variable Python :** `reponse`, `reference` (des `set[str]`)

$$
TP,\; FP,\; FN
$$

**Sens :** affirmations justes (dans les deux), inventées (dans la réponse seulement), oubliées (dans la référence seulement) · **Type / plage :** entiers ≥ 0 · **Variable Python :** `tp, fp, fn = classer_affirmations(reponse, reference)`

$$
F_1^{\text{faits}}
$$

**Sens :** F1 des faits ; vaut 1 si la réponse dit tout ce que dit la référence et rien d'autre · **Type / plage :** réel dans [0, 1], indéfinie si TP + FP + FN = 0 · **Variable Python :** `f1_factuelle(tp, fp, fn)`

$$
E_{\text{réponse}},\; E_{\text{réf}}
$$

**Sens :** embeddings de la réponse et de la référence, produits par le même modèle · **Type / plage :** vecteurs réels de même dimension · **Variable Python :** remplacés ici par un sac de mots jouet dans `similarite_jouet`

$$
\text{sim}
$$

**Sens :** cosinus entre les deux embeddings · **Type / plage :** réel dans [−1, 1], ramené à [0, 1] par max(0, sim) · **Variable Python :** `sim`

$$
w_{\text{fait}},\; w_{\text{sim}}
$$

**Sens :** poids de la F1 des faits et de la similarité · **Type / plage :** réels ≥ 0 de somme 1 ; 0,75 et 0,25 par défaut · **Variable Python :** `w_fact`, `w_sim`

$$
\text{AC}
$$

**Sens :** score de justesse de la réponse · **Type / plage :** réel dans [0, 1], ou indéfini si la F1 l'est · **Variable Python :** `answer_correctness(f1, sim)`

$$
\tau
$$

**Sens :** seuil de la barrière de déploiement sur la moyenne des AC · **Type / plage :** réel dans [0, 1], à fixer par métier · **Variable Python :** `seuil`

## Démonstration

### 1. Les deux formes de la F1 sont la même formule

On multiplie numérateur et dénominateur par 2 :

$$
\frac{TP}{TP + \tfrac{1}{2}(FP+FN)} = \frac{2\,TP}{2\,TP + FP + FN}
$$

C'est la forme par les comptes de la F1, démontrée à l'étape 50 (et à l'étape 64 bis) à partir de la précision P = TP/(TP + FP) et du rappel R = TP/(TP + FN) : la moyenne harmonique 2PR/(P + R) se simplifie exactement en 2TP/(2TP + FP + FN). Ici, la précision demande « parmi ce que l'agent affirme, quelle part est juste ? » et le rappel « parmi ce qu'il fallait dire, quelle part est dite ? ». Une réponse qui invente est punie par FP, une réponse qui oublie est punie par FN.

### 2. Le score est entre 0 et 1, à condition de borner la similarité

La F1 est dans [0, 1], parce que TP ≤ TP + ½(FP + FN). La similarité bornée max(0, sim) est dans [0, 1], parce qu'un cosinus vaut au plus 1. Avec des poids positifs de somme 1, AC est une moyenne pondérée de deux nombres de [0, 1] :

$$
0 \;\le\; w_{\text{fait}} F_1 + w_{\text{sim}} \max(0,\text{sim}) \;\le\; w_{\text{fait}} \cdot 1 + w_{\text{sim}} \cdot 1 = 1
$$

Sans la borne, un cosinus de −0,2 avec une F1 nulle et un poids de 0,25 sur la similarité donne 0,25 × (−0,2) = −0,05 : un score de justesse négatif, que l'on ne sait pas interpréter et qui fait baisser une moyenne sans raison.

### 3. La pondération inversée, sur un contre-exemple chiffré

Prenons une réponse fluide mais fausse : elle ressemble beaucoup à la référence (sim = 0,95) mais ne contient qu'une partie des bons faits (F1 = 0,40).

- Avec les poids RAGAS : 0,75 × 0,40 + 0,25 × 0,95 = 0,30 + 0,2375 = **0,5375**.
- Avec l'ancienne version et son poids par défaut de 0,5 : 0,5 × 0,95 + 0,5 × 0,40 = **0,675**.
- Avec les poids inversés, 0,75 sur la similarité : 0,75 × 0,95 + 0,25 × 0,40 = 0,7125 + 0,1 = **0,8125**.

Avec un seuil de 0,7, la réponse est refusée par la première formule, frôle le seuil avec la deuxième et passe largement avec la troisième. La formule décide donc, à elle seule, si une réponse fausse part en production.

### 4. Ce que la similarité peut acheter à elle seule

Une réponse dont aucun fait n'est juste (F1 = 0) obtient au plus w_sim × 1. Avec les poids RAGAS, c'est 0,25 : elle ne franchit jamais un seuil de 0,7. Avec les poids inversés, c'est 0,75 : elle le franchit. Plus précisément, la condition de seuil s'écrit

$$
F_1 \ge \frac{\tau - w_{\text{sim}} \max(0,\text{sim})}{w_{\text{fait}}}
$$

parce qu'il suffit d'isoler F1 dans l'inégalité AC ≥ τ, en divisant par w_fait > 0. Avec τ = 0,7 et sim = 0,95, les poids RAGAS exigent F1 ≥ (0,7 − 0,2375)/0,75 ≈ 0,6167, et F1 ≥ 0,6 même avec une similarité parfaite. Les poids inversés exigent F1 ≥ (0,7 − 0,7125)/0,25 = −0,05 : n'importe quelle réponse passe, quel que soit son contenu factuel.

### 5. Pourquoi la similarité ne voit pas un chiffre faux

Prenons, à la place d'un vrai modèle d'embedding, un embedding jouet par sac de mots, dont le cosinus se calcule à la main. La référence est « ratio maximal 50 % du salaire » (6 mots). La réponse fausse, « ratio maximal 60 % du salaire », partage 5 mots sur 6 : son cosinus vaut 5/(√6 × √6) = 5/6 ≈ 0,8333. La paraphrase juste, « le plafond est la moitié du salaire » (7 mots), n'en partage que 2 : son cosinus vaut 2/(√6 × √7) = 2/√42 ≈ 0,3086. La réponse fausse est **plus** similaire que la réponse juste. Côté faits, la réponse fausse affirme « plafond = 60 % » (FP = 1, FN = 1, F1 = 0) et la paraphrase affirme « plafond = 50 % » (F1 = 1). Avec les poids RAGAS, la paraphrase obtient 0,75 + 0,25 × 0,3086 ≈ 0,8272 et la réponse fausse 0,25 × 0,8333 ≈ 0,2083 : le classement est juste. Avec les poids inversés, la réponse fausse obtient 0,625 et la paraphrase 0,4815 : la fausse passe devant. Un vrai modèle d'embedding rapproche bien mieux les paraphrases qu'un sac de mots, mais il reste peu sensible à un seul chiffre changé dans une phrase : c'est pour cela que la partie factuelle doit dominer.

### 6. Sans affirmation, pas de F1

Si ni la réponse ni la référence ne contiennent d'affirmation (une référence « aucune information disponible » et une réponse qui refuse poliment), TP + FP + FN = 0 et la F1 vaut 0/0. Le code renvoie `None`, et la question sort de la moyenne, comme toute métrique sans dénominateur dans ce parcours. Ces cas se mesurent à part, par le taux de refus corrects (étape 60).

### 7. Exemple fait à la main (le code reprend ces nombres)

Question de conformité bancaire : « quel est le plafond d'endettement d'un salarié, celui d'un retraité, et la durée maximale d'un prêt personnel ? ». La référence contient trois faits : 50 % pour un salarié, 30 % pour un retraité, 48 mois. La réponse B affirme deux choses : 50 % pour un salarié (juste) et 60 mois (faux). Donc TP = 1, FP = 1 (les 60 mois), FN = 2 (les 30 % et les 48 mois), et

$$
F_1 = \frac{1}{1 + \tfrac{1}{2}(1 + 2)} = \frac{1}{2{,}5} = 0{,}40
$$

Avec une similarité de 0,95 donnée par le modèle d'embedding, AC = 0,5375 < 0,7 : la réponse échoue. La réponse A cite les trois faits : F1 = 1, et avec une similarité de 0,80, AC = 0,75 + 0,20 = 0,95.

## Effets et comportement

- **La F1 pèse trois fois plus que la similarité.** Un fait juste de plus compte beaucoup plus qu'une formulation plus proche : la dérivée de AC vaut 0,75 par rapport à la F1 et 0,25 par rapport à la similarité.
- **Inventer et oublier coûtent pareil.** FP et FN ont le même poids ½ dans la F1. Si l'invention est plus grave dans un métier (un montant faux), on ajoute un contrôle dur sur les faits critiques, par exemple un Exact Match sur le montant (étape 64).
- **Le score dépend du juge.** L'extraction et le classement des affirmations sont faits par un LLM : on fixe sa version et sa température, on répète le calcul et on publie la dispersion (étape 53).
- **Le score dépend de la référence.** Une référence incomplète transforme des affirmations justes en FP. Les références se relisent et se versionnent comme du code.

## Du symbole au code Python

$$
TP,\; FP,\; FN
$$

**Variable ou fonction :** `classer_affirmations(reponse, reference)`

$$
F_1^{\text{faits}}
$$

**Variable ou fonction :** `f1_factuelle(tp, fp, fn)`

$$
\cos(E_{\text{réponse}}, E_{\text{réf}})
$$

**Variable ou fonction :** `cosinus(a, b)` (canonique), appelé par `similarite_jouet(texte_a, texte_b)`

$$
w_{\text{fait}} F_1 + w_{\text{sim}} \max(0, \text{sim})
$$

**Variable ou fonction :** `answer_correctness(f1, sim, w_fact=0.75, w_sim=0.25)`

$$
\frac{\tau - w_{\text{sim}} \max(0,\text{sim})}{w_{\text{fait}}}
$$

**Variable ou fonction :** `f1_minimal(seuil, sim, w_fact=0.75)`

### Déroulé, ligne par ligne

**`cosinus(a, b)`** est la fonction canonique du parcours : elle refuse deux dimensions différentes et un vecteur nul, puis borne le résultat à [−1, 1] pour absorber les erreurs d'arrondi.

**`similarite_jouet(texte_a, texte_b)`** met les deux textes en minuscules, les coupe en mots, construit le vocabulaire commun trié, puis compte chaque mot. Pour la référence et la réponse fausse, le vocabulaire a 7 mots (`%`, `50`, `60`, `du`, `maximal`, `ratio`, `salaire`) ; les vecteurs valent `[1, 1, 0, 1, 1, 1, 1]` et `[1, 0, 1, 1, 1, 1, 1]`, leur produit scalaire 5 et leurs normes √6 : le cosinus vaut 5/6.

**`classer_affirmations(reponse, reference)`** utilise trois opérations d'ensembles : `reponse & reference` (intersection, les TP), `reponse - reference` (les FP), `reference - reponse` (les FN). Pour la réponse B, l'intersection contient `endettement_salarie=50%`, la réponse a en plus `duree_max=60 mois`, et la référence a en plus le plafond retraité et les 48 mois : `(1, 1, 2)`.

**`f1_factuelle(tp, fp, fn)`** refuse un compte négatif, renvoie `None` si les trois comptes sont nuls, puis calcule `tp / (tp + 0.5 * (fp + fn))` : 1 / (1 + 1,5) = 0,4.

**`answer_correctness(f1, sim, w_fact, w_sim)`**, le cœur du fichier.

- La première garde refuse des poids négatifs ou dont la somme n'est pas 1 : sans elle, la preuve des bornes (point 2) ne tient plus.
- La deuxième refuse une similarité hors de [−1, 1], qui ne peut pas être un cosinus.
- `if f1 is None: return None` propage l'indéfini au lieu de le transformer en 0.
- `return w_fact * f1 + w_sim * max(0.0, sim)` : pour F1 = 0,4 et sim = 0,95, cela donne 0,75 × 0,4 + 0,25 × 0,95 = 0,5375.

**`ancienne_version(semantic_sim, fact_f1, alpha)`** recopie l'ancien code : `alpha * semantic_sim + (1 - alpha) * fact_f1`, avec `alpha = 0.5` par défaut et sans borne. Elle sert de contraste.

**`f1_minimal(seuil, sim, w_fact)`** isole la F1 dans la condition AC ≥ τ (point 4).

**`main()`**, bloc par bloc.

1. Le contre-exemple de la démonstration : 0,5375 avec les poids RAGAS, 0,675 avec l'ancienne version, 0,8125 avec les poids inversés.
2. La F1 de 0,40 retrouvée à partir des affirmations de la réponse B ; la réponse A complète obtient F1 = 1 et AC = 0,95.
3. Les trois formes de la F1 donnent le même nombre sur quatre triplets (TP, FP, FN).
4. L'embedding jouet : la réponse fausse a une similarité de 0,8333, la paraphrase de 0,3086. Le programme vérifie les valeurs exactes 5/6 et 2/√42, puis que les poids RAGAS classent la paraphrase devant (0,8272 contre 0,2083) alors que les poids inversés classent la fausse devant (0,625 contre 0,4815).
5. Seuil 0,7 : F1 ≥ 0,6167 avec les poids RAGAS, F1 ≥ −0,05 avec les poids inversés, et F1 ≥ 0,6 quand la similarité vaut 1.
6. Un cosinus de −0,2 donne AC = 0 avec la borne, −0,05 sans. Une double boucle vérifie que AC reste dans [0, 1] sur une grille de valeurs, et que la similarité seule plafonne à 0,25.
7. Les comptes nuls donnent `None` ; des poids de somme 1,1, une similarité de 1,3 et une F1 de 1,2 lèvent `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cosinus(a, b)`** — Cette fonction est le rapporteur du géomètre, qui mesure l'angle entre deux flèches sans se soucier de leur longueur : elle reçoit deux vecteurs, lève `ValueError` s'ils n'ont pas la même dimension ou si l'un est nul, puis divise leur produit scalaire par le produit de leurs normes et borne le résultat à [−1, 1] pour absorber un arrondi. Elle renvoie ce cosinus, la fonction canonique du parcours, que `similarite_jouet` applique aux vecteurs de comptes de mots : 5/6, soit 0,8333, entre la référence et la réponse au chiffre faux, et 2/√42, soit 0,3086, avec la paraphrase.

**`f1_factuelle(tp, fp, fn)`** — Celle-ci est le correcteur qui compare, fait par fait, la copie à la référence : elle reçoit le nombre d'affirmations justes, inventées et oubliées, lève une `ValueError` si l'un des comptes est négatif, renvoie `None` si les trois sont nuls, faute de la moindre affirmation à juger, et sinon renvoie TP ÷ (TP + 0,5 × (FP + FN)). Pour la réponse B, avec un fait juste, un inventé et deux oubliés, elle donne 1 ÷ 2,5 = 0,4 ; la réponse A complète obtient 1, et `main` vérifie sur quatre triplets que cette forme égale les deux autres écritures de la F1.

**`answer_correctness(f1, sim, w_fact, w_sim)`** — Cette fonction est le président du jury qui combine deux notes en donnant le dernier mot aux faits : elle reçoit la F1 factuelle, la similarité sémantique et deux poids, 0,75 et 0,25 par défaut comme dans RAGAS, lève `ValueError` si les poids sont négatifs ou ne somment pas à 1, si la similarité sort de [−1, 1] ou si la F1 sort de [0, 1], et renvoie `None` quand la F1 est indéfinie. Sinon, elle renvoie w_fact × F1 + w_sim × max(0, sim), toujours dans [0, 1] : 0,5375 pour la réponse fluide mais fausse, 0,95 pour la réponse complète, 0,2083 pour le chiffre faux contre 0,8272 pour la paraphrase, et 0 quand un cosinus négatif est rabattu à zéro.

**`ancienne_version(semantic_sim, fact_f1, alpha)`** — Celle-ci est l'ancienne formule du fichier, gardée comme témoin à charge : elle reçoit la similarité, la F1 factuelle et un poids alpha de 0,5 par défaut, placé sur la similarité, et renvoie alpha × sim + (1 − alpha) × F1, sans contrôler ni les poids ni le signe de la similarité. Elle donne 0,675 à la réponse fluide mais fausse, plus que les 0,5375 de RAGAS, et descend jusqu'à −0,05 avec un cosinus de −0,2 et alpha = 0,25, un score négatif qui n'a aucun sens pour une justesse.

**`f1_minimal(seuil, sim, w_fact)`** — Cette fonction répond à la question du candidat qui veut savoir quelle note de fond il lui faut pour être reçu, à note de forme donnée : elle reçoit le seuil d'acceptation, la similarité et le poids des faits, 0,75 par défaut, et renvoie (seuil − (1 − w_fact) × max(0, sim)) ÷ w_fact, la F1 minimale pour que le score atteigne le seuil. Au seuil 0,7 avec une similarité de 0,95, il faut une F1 d'au moins 0,6167 avec les poids RAGAS, mais seulement −0,05 avec les poids inversés, si bien que toute réponse passerait ; avec une similarité de 1, le minimum vaut 0,6.

**`main()`** — C'est le chef d'orchestre des sept démonstrations : il oppose d'abord, pour une réponse fluide mais fausse, les 0,5375 de RAGAS, les 0,675 de l'ancienne version et les 0,8125 des poids inversés, puis retrouve la F1 de 0,4 à partir des affirmations et vérifie les trois écritures de la F1. Il montre ensuite, avec l'embedding jouet, que la similarité préfère le chiffre faux à la paraphrase et que seuls les poids RAGAS remettent les deux réponses dans le bon ordre, calcule les F1 minimales au seuil 0,7, vérifie que le score reste dans [0, 1] et que la similarité seule plafonne à 0,25, et termine par les cas limites avant le « OK ».

```python
"""Étape 63 — Answer Correctness : 0,75 × F1 des faits + 0,25 × similarité, bornée à [0, 1]."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def cosinus(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("dimensions différentes")
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        raise ValueError("vecteur nul : le cosinus n'est pas défini")
    return max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b)) / (na * nb)))


def similarite_jouet(texte_a: str, texte_b: str) -> float:
    """Embedding JOUET par sac de mots (comptes), à la place d'un vrai modèle d'embedding."""
    mots_a, mots_b = texte_a.lower().split(), texte_b.lower().split()
    vocab = sorted(set(mots_a) | set(mots_b))
    return cosinus([float(mots_a.count(m)) for m in vocab], [float(mots_b.count(m)) for m in vocab])


def classer_affirmations(reponse: set[str], reference: set[str]) -> tuple[int, int, int]:
    """TP : dans la réponse ET dans la référence ; FP : inventé ; FN : oublié.
    Dans RAGAS, un LLM extrait et classe les affirmations ; ici, ce sont des clés déjà normalisées."""
    return len(reponse & reference), len(reponse - reference), len(reference - reponse)


def f1_factuelle(tp: int, fp: int, fn: int) -> float | None:
    """F1 = TP / (TP + 0,5 (FP + FN)) ; None si aucune affirmation d'aucun côté."""
    if min(tp, fp, fn) < 0:
        raise ValueError("comptes négatifs")
    if tp + fp + fn == 0:
        return None
    return tp / (tp + 0.5 * (fp + fn))


def answer_correctness(f1: float | None, sim: float, w_fact: float = 0.75, w_sim: float = 0.25) -> float | None:
    """AC = w_fact · F1 + w_sim · max(0, sim), avec des poids >= 0 de somme 1 (RAGAS : 0,75 et 0,25)."""
    if w_fact < 0 or w_sim < 0 or not math.isclose(w_fact + w_sim, 1.0):
        raise ValueError("poids >= 0 et de somme 1")
    if not -1.0 <= sim <= 1.0:
        raise ValueError("un cosinus est dans [-1, 1]")
    if f1 is None:
        return None
    if not 0.0 <= f1 <= 1.0:
        raise ValueError("F1 dans [0, 1]")
    return w_fact * f1 + w_sim * max(0.0, sim)


def ancienne_version(semantic_sim: float, fact_f1: float, alpha: float = 0.5) -> float:
    """Version d'origine du fichier : poids alpha sur la SIMILARITÉ, non bornée."""
    return alpha * semantic_sim + (1 - alpha) * fact_f1


def f1_minimal(seuil: float, sim: float, w_fact: float = 0.75) -> float:
    """F1 qu'il faut au moins atteindre pour que AC >= seuil, à similarité donnée."""
    return (seuil - (1 - w_fact) * max(0.0, sim)) / w_fact


def main() -> None:
    print("1. Réponse fluide mais fausse : sim = 0.95, F1 = 0.40")
    juste = answer_correctness(0.40, 0.95)
    vieux = ancienne_version(0.95, 0.40)
    inverse = answer_correctness(0.40, 0.95, w_fact=0.25, w_sim=0.75)
    print(f"  RAGAS (0.75 F1 + 0.25 sim) = {juste:.4f}   ancienne version (alpha 0.5) = {vieux:.4f}   poids inversés = {inverse:.4f}")
    assert math.isclose(juste, 0.5375) and math.isclose(vieux, 0.675) and math.isclose(inverse, 0.8125)

    print("2. D'où vient F1 = 0.40 : trois faits attendus, deux affirmés dont un faux")
    reference = {"endettement_salarie=50%", "endettement_retraite=30%", "duree_max=48 mois"}
    reponse_b = {"endettement_salarie=50%", "duree_max=60 mois"}
    tp, fp, fn = classer_affirmations(reponse_b, reference)
    f1_b = f1_factuelle(tp, fp, fn)
    print(f"  TP = {tp}, FP = {fp}, FN = {fn}   F1 = {tp} / ({tp} + 0.5 × {fp + fn}) = {f1_b:.4f}")
    assert (tp, fp, fn) == (1, 1, 2) and math.isclose(f1_b, 0.4)
    reponse_a = {"endettement_salarie=50%", "endettement_retraite=30%", "duree_max=48 mois"}
    f1_a = f1_factuelle(*classer_affirmations(reponse_a, reference))
    print(f"  réponse A, complète : F1 = {f1_a:.4f}   AC avec sim = 0.80 : {answer_correctness(f1_a, 0.80):.4f}")
    assert f1_a == 1.0 and math.isclose(answer_correctness(f1_a, 0.80), 0.95)

    print("3. Les deux formes de la F1 sont égales")
    for t, p, n in ((1, 1, 2), (2, 1, 0), (3, 0, 4), (5, 2, 2)):
        a = f1_factuelle(t, p, n)
        precision, rappel = t / (t + p), t / (t + n)
        assert math.isclose(a, 2 * t / (2 * t + p + n)) and math.isclose(a, 2 * precision * rappel / (precision + rappel))
    print("  TP / (TP + 0.5(FP + FN)) = 2TP / (2TP + FP + FN) = 2PR / (P + R) sur 4 triplets")

    print("4. La similarité ne voit pas un chiffre faux (embedding jouet)")
    ref_txt = "ratio maximal 50 % du salaire"
    faux_txt = "ratio maximal 60 % du salaire"
    para_txt = "le plafond est la moitié du salaire"
    s_faux, s_para = similarite_jouet(ref_txt, faux_txt), similarite_jouet(ref_txt, para_txt)
    f1_faux = f1_factuelle(*classer_affirmations({"plafond=60%"}, {"plafond=50%"}))
    f1_para = f1_factuelle(*classer_affirmations({"plafond=50%"}, {"plafond=50%"}))
    ac_faux, ac_para = answer_correctness(f1_faux, s_faux), answer_correctness(f1_para, s_para)
    inv_faux = answer_correctness(f1_faux, s_faux, w_fact=0.25, w_sim=0.75)
    inv_para = answer_correctness(f1_para, s_para, w_fact=0.25, w_sim=0.75)
    print(f"  chiffre faux : sim = {s_faux:.4f}, F1 = {f1_faux:.1f}, AC = {ac_faux:.4f}   (poids inversés : {inv_faux:.4f})")
    print(f"  paraphrase   : sim = {s_para:.4f}, F1 = {f1_para:.1f}, AC = {ac_para:.4f}   (poids inversés : {inv_para:.4f})")
    assert math.isclose(s_faux, 5 / 6) and math.isclose(s_para, 2 / math.sqrt(42))
    assert round(ac_faux, 4) == 0.2083 and round(ac_para, 4) == 0.8272
    assert round(inv_faux, 4) == 0.625 and round(inv_para, 4) == 0.4815
    assert ac_para > ac_faux and inv_faux > inv_para          # les poids inversés classent la fausse devant

    print("5. Seuil 0.7 : F1 minimale exigée selon les poids")
    m_ragas = f1_minimal(0.7, 0.95)
    m_inv = f1_minimal(0.7, 0.95, w_fact=0.25)
    print(f"  RAGAS : F1 >= {m_ragas:.4f}   poids inversés : F1 >= {m_inv:.4f} (toute réponse passe)")
    assert round(m_ragas, 4) == 0.6167 and m_inv < 0 and math.isclose(f1_minimal(0.7, 1.0), 0.6)

    print("6. Bornes : un cosinus négatif ne rend pas le score négatif")
    print(f"  sim = -0.2, F1 = 0 : AC = {answer_correctness(0.0, -0.2):.4f}   sans borne : {ancienne_version(-0.2, 0.0, alpha=0.25):.4f}")
    assert answer_correctness(0.0, -0.2) == 0.0 and math.isclose(ancienne_version(-0.2, 0.0, alpha=0.25), -0.05)
    for f1 in (0.0, 0.4, 1.0):
        for sim in (-1.0, 0.0, 0.5, 1.0):
            assert 0.0 <= answer_correctness(f1, sim) <= 1.0
    assert answer_correctness(0.0, 1.0) == 0.25                # la similarité seule plafonne à 0,25

    print("7. Cas limites")
    assert f1_factuelle(0, 0, 0) is None and answer_correctness(None, 0.9) is None
    for args in ((0.5, 0.9, 0.8, 0.3), (0.5, 1.3), (1.2, 0.5)):
        try:
            answer_correctness(*args)
        except ValueError as e:
            print(f"  {args} → ValueError ({e})")
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Réponse fluide mais fausse : sim = 0.95, F1 = 0.40
  RAGAS (0.75 F1 + 0.25 sim) = 0.5375   ancienne version (alpha 0.5) = 0.6750   poids inversés = 0.8125
2. D'où vient F1 = 0.40 : trois faits attendus, deux affirmés dont un faux
  TP = 1, FP = 1, FN = 2   F1 = 1 / (1 + 0.5 × 3) = 0.4000
  réponse A, complète : F1 = 1.0000   AC avec sim = 0.80 : 0.9500
3. Les deux formes de la F1 sont égales
  TP / (TP + 0.5(FP + FN)) = 2TP / (2TP + FP + FN) = 2PR / (P + R) sur 4 triplets
4. La similarité ne voit pas un chiffre faux (embedding jouet)
  chiffre faux : sim = 0.8333, F1 = 0.0, AC = 0.2083   (poids inversés : 0.6250)
  paraphrase   : sim = 0.3086, F1 = 1.0, AC = 0.8272   (poids inversés : 0.4815)
5. Seuil 0.7 : F1 minimale exigée selon les poids
  RAGAS : F1 >= 0.6167   poids inversés : F1 >= -0.0500 (toute réponse passe)
6. Bornes : un cosinus négatif ne rend pas le score négatif
  sim = -0.2, F1 = 0 : AC = 0.0000   sans borne : -0.0500
7. Cas limites
  (0.5, 0.9, 0.8, 0.3) → ValueError (poids >= 0 et de somme 1)
  (0.5, 1.3) → ValueError (un cosinus est dans [-1, 1])
  (1.2, 0.5) → ValueError (F1 dans [0, 1])
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : la justesse d'une réponse se juge d'abord sur ses faits. La similarité n'est qu'un bonus de formulation, plafonné à 0,25 : elle ne doit jamais pouvoir faire passer une réponse fausse.

## Squelette algorithmique

Les entrées sont les affirmations élémentaires de la réponse et de la référence (extraites par un LLM juge dans RAGAS, déjà normalisées ici), les deux embeddings, et les deux poids. La sortie est un score dans [0, 1], ou INDÉFINI s'il n'y a aucune affirmation. L'idée : classer les affirmations en justes, inventées et oubliées, en tirer une F1, calculer un cosinus borné à 0, puis faire une moyenne pondérée où les faits pèsent trois fois plus que la formulation.

```text
ALGORITHME AnswerCorrectness
ENTRÉES : affirmations A de la réponse, affirmations G de la référence (ensembles),
          embeddings e_rep et e_ref, poids w_fait = 0,75 et w_sim = 0,25
SORTIE  : AC ∈ [0, 1], ou INDÉFINI
    SI w_fait < 0 OU w_sim < 0 OU w_fait + w_sim ≠ 1 ALORS
        ÉCHOUER « poids invalides »
    FIN SI
    TP ← 0 ; FP ← 0
    POUR chaque affirmation a de A FAIRE
        SI a ∈ G ALORS
            TP ← TP + 1                          ▹ affirmée et attendue
        SINON
            FP ← FP + 1                          ▹ inventée
        FIN SI
    FIN POUR
    FN ← |G| − TP                                ▹ attendue mais oubliée
    SI TP + FP + FN = 0 ALORS
        RETOURNER INDÉFINI
    FIN SI
    F1 ← TP / (TP + (FP + FN) / 2)
    SI ‖e_rep‖ = 0 OU ‖e_ref‖ = 0 ALORS
        ÉCHOUER « vecteur nul »
    FIN SI
    sim ← (Σ e_rep[j] × e_ref[j]) / (‖e_rep‖ × ‖e_ref‖)
    sim ← max(0, sim)                            ▹ un cosinus peut être négatif
    RETOURNER w_fait × F1 + w_sim × sim          ▹ 0 ≤ AC ≤ 1

ALGORITHME F1Minimale
ENTRÉES : seuil τ, similarité sim, poids w_fait
SORTIE  : la F1 qu'il faut au moins atteindre pour que AC ≥ τ
    RETOURNER (τ − (1 − w_fait) × max(0, sim)) / w_fait
```

**Complexité :** le classement des affirmations fait un passage sur A avec un test d'appartenance à G en temps constant moyen (table de hachage), donc O(|A| + |G|) en temps en comptant la construction de G ; le cosinus de deux embeddings de dimension d coûte O(d) (un produit scalaire et deux normes). Le score d'une question coûte donc O(|A| + |G| + d) en temps et O(|A| + |G|) en mémoire pour les deux ensembles. Sur un jeu de N questions, on multiplie par N. En pratique, ce coût de calcul est négligeable devant celui des appels au juge : RAGAS fait quelques appels LLM par question pour extraire et classer les affirmations, et un appel au modèle d'embedding par texte, ce qui donne O(N) appels facturés. Dans le programme, `similarite_jouet` est moins efficace que nécessaire : `mots.count(m)` relit toute la liste pour chaque mot du vocabulaire, soit O(V × L) pour V mots distincts et L mots ; un `Counter` le ferait en O(L), ce qui est sans importance sur des phrases de six mots.

**Du squelette au code :** la vérification des poids est la première garde de `answer_correctness`. La boucle POUR qui compte TP et FP, puis FN ← |G| − TP, est faite en une ligne par `classer_affirmations`, avec les opérations d'ensembles `reponse & reference`, `reponse - reference` et `reference - reponse`. Le test « TP + FP + FN = 0 » et le calcul de la F1 sont dans `f1_factuelle`, qui renvoie `None` pour l'indéfini. Le cosinus et sa garde « vecteur nul » sont la fonction canonique `cosinus`, appelée par `similarite_jouet` à la place d'un vrai modèle d'embedding. La borne max(0, sim) et la moyenne pondérée sont la dernière ligne de `answer_correctness` : `w_fact * f1 + w_sim * max(0.0, sim)`. F1Minimale est `f1_minimal`.

## Cas d'usage réels aux Émirats

Les similarités, F1, seuils et volumes ci-dessous sont illustratifs ; les règles métier sont celles du guide du parcours, à confirmer avec le texte en vigueur.

### Banque — une réponse de conformité bien écrite mais incomplète

Une banque de détail de Dubaï évalue son assistant de crédit sur 200 questions dont les réponses de référence ont été écrites et signées par l'équipe conformité. À la question sur les plafonds d'endettement et la durée des prêts personnels, la référence contient trois faits issus des règles de la CBUAE : 50 % du revenu pour un salarié, 30 % pour un retraité, 48 mois au plus. Une nouvelle version du prompt produit une réponse très proche dans la forme (similarité 0,95) mais qui annonce 60 mois et oublie le cas du retraité : F1 = 0,40 et AC = 0,5375. Avec le seuil de 0,7 fixé par la banque, la réponse échoue ; l'ancienne formule lui aurait donné 0,675, à trois centièmes du seuil, et la formule aux poids inversés 0,8125, un succès net. Un conseiller qui aurait relayé cette réponse aurait proposé un prêt hors des règles. La banque suit la moyenne d'AC par famille de produits et, à part, le nombre de FP sur les faits réglementaires, qu'elle veut à zéro.

### Immobilier — le bon taux, le mauvais montant

Une agence qui opère à Dubaï et à Abu Dhabi évalue l'agent qui répond aux acheteurs sur les frais d'acquisition. Pour un bien de 2 000 000 AED à Dubaï, la référence contient deux faits : frais de transfert DLD de 4 % et montant de 80 000 AED. L'agent répond « 4 %, soit 8 000 AED » : le taux est juste, le montant faux d'un facteur 10, donc TP = 1, FP = 1, FN = 1 et F1 = 1/(1 + 1) = 0,5. La similarité est très haute, 0,97, parce que les deux phrases ne diffèrent que par un zéro. Avec les poids RAGAS, AC = 0,375 + 0,2425 = 0,6175, sous le seuil de 0,7 ; l'ancienne formule donnait 0,735 et laissait passer l'erreur. L'agence ajoute en plus un Exact Match sur le montant (étape 64), parce qu'un acheteur qui prévoit 8 000 AED au lieu de 80 000 découvre l'écart au moment du transfert. L'indicateur suivi est le taux de réponses chiffrées qui passent les deux contrôles.

### RH — une moyenne qui cache le seul fait qui compte

Un cabinet RH présent dans plusieurs émirats évalue son assistant de fin de service. Pour un salarié du secteur privé avec 7 ans d'ancienneté et un salaire de base de 10 000 AED, la référence contient trois faits : 21 jours par an les cinq premières années, 30 jours au-delà, total de 55 000 AED. L'agent cite correctement les deux règles mais annonce 70 000 AED, en appliquant 30 jours à toutes les années : TP = 2, FP = 1, FN = 1, F1 = 2/3 ≈ 0,667. Avec une similarité de 0,93, AC = 0,5 + 0,2325 ≈ 0,7325 : la réponse **passe** le seuil de 0,7, alors que le seul nombre qui intéresse le salarié est faux. Answer Correctness traite tous les faits comme égaux ; le cabinet ajoute donc un veto : tout montant d'indemnité faux fait échouer le cas, quel que soit le score. Il suit le taux d'échec par veto à part de la moyenne d'AC, parce que les deux ne racontent pas la même chose.

### Assurance — une réponse juste en arabe, une référence en anglais

Un assureur auto et santé a écrit ses réponses de référence en anglais, mais son agent répond en arabe aux assurés arabophones. La similarité entre une réponse arabe et une référence anglaise dépend du modèle d'embedding : avec un modèle peu multilingue, elle tombe à 0,40 même pour une réponse parfaitement juste. Si le juge qui extrait les affirmations sait lire les deux langues, la F1 vaut 1, et AC = 0,75 + 0,25 × 0,40 = 0,85 avec les poids RAGAS ; l'ancienne formule à 0,5 donnait 0,70, au bord du seuil, et aurait fait croire que l'agent répondait moins bien en arabe. L'assureur vérifie d'abord la qualité de son juge sur un échantillon arabe noté par des humains, puis choisit un modèle d'embedding multilingue. Il suit l'écart de moyenne d'AC entre les conversations en arabe et en anglais, et le considère comme un défaut de mesure tant qu'il n'est pas confirmé par la revue humaine.

### Crypto — un juge qui ne donne pas deux fois la même note

Une plateforme d'actifs virtuels agréée par la VARA évalue l'agent qui répond aux questions sur les procédures de retrait. Le classement des affirmations est fait par un LLM juge, et trois passages du même juge sur la même réponse donnent des F1 de 0,6, 0,6 et 0,8, selon que le juge considère ou non « vérification renforcée » et « contrôle d'identité approfondi » comme la même affirmation. La plateforme fixe la version du juge et sa température, répète le calcul trois fois, publie la moyenne (0,667 sur cet exemple) et l'écart, et ne compare deux versions de l'agent que si leur différence dépasse cette dispersion. Sans cette discipline, un changement de prompt serait jugé meilleur ou pire selon le tirage du juge, pas selon la qualité. On suit l'écart type de la F1 entre passages du juge, et l'accord entre le juge et un relecteur humain sur un échantillon mensuel.

### BTP — séparer le récit et les montants

Un groupe de construction qui mène de grands chantiers à Dubaï fait expliquer par un agent les factures de sous-traitance contestées. Une réponse type contient un récit (« la retenue de garantie s'applique jusqu'à la réception ») et des montants (240 000 AED hors taxe, TVA de 5 % soit 12 000 AED, 252 000 AED toutes taxes comprises). Le groupe utilise Answer Correctness pour le récit, où les paraphrases sont nombreuses et légitimes, et un Exact Match normalisé (étape 64) pour chaque montant, où aucune approximation n'est acceptable. Une réponse dont le récit obtient 0,85 mais dont un seul montant est faux échoue au cas. Mélanger les deux dans un seul score aurait permis à un récit bien écrit de compenser un montant faux, exactement le défaut que la pondération 0,75 / 0,25 limite sans l'éliminer. L'indicateur suivi est le taux de cas réussis sur les deux critères, par type de litige.

## Pièges et limites

- **Mettre le gros poids sur la similarité.** C'est l'erreur corrigée ici : une réponse fluide mais fausse passe le seuil.
- **Oublier de borner le cosinus.** Un cosinus négatif rend le score négatif et fausse la moyenne.
- **Croire que la F1 traite les faits critiques à part.** Tous les faits pèsent pareil ; un montant faux peut être noyé dans deux faits justes. On ajoute un veto ou un Exact Match sur les faits critiques.
- **Oublier que le juge est un LLM.** Version, température, répétitions et dispersion font partie du protocole de mesure.
- **Comparer des scores obtenus avec des modèles d'embedding différents.** La partie similarité change d'échelle d'un modèle à l'autre ; on fixe le modèle pour toute la série de mesures.

### Exercice feuille blanche

1. Sans regarder le code, écrire `f1_factuelle` et `answer_correctness`, avec la borne sur le cosinus et la convention `None`, puis vérifier 0,5375 pour F1 = 0,40 et sim = 0,95.
2. Prédire, puis vérifier : une réponse a TP = 2, FP = 0, FN = 2 et une similarité de 0,9. Que vaut AC ? Passe-t-elle un seuil de 0,7 ? (Réponse : F1 = 2/(2 + 1) ≈ 0,667, AC = 0,5 + 0,225 = 0,725 : elle passe de justesse, alors qu'elle oublie la moitié des faits.)
3. Trouver le bug : `return alpha * sim + (1 - alpha) * f1` avec `alpha = 0.75`. Quelle note obtient une réponse sans aucun fait juste mais de similarité 0,95 ? (Réponse : 0,7125, au-dessus d'un seuil de 0,7.)

## Pour aller plus loin

RAGAS propose aussi une option qui transforme la similarité en 0 ou 1 au-delà d'un seuil, et une métrique séparée de *factual correctness* qui ne garde que la partie factuelle, avec un choix entre précision, rappel et F1. Quand l'invention est plus grave que l'oubli, on remplace la F1 par une F-bêta avec β < 1, qui favorise la précision (étape 50). Pour les réponses longues, on pondère parfois les affirmations par leur importance métier, ce qui revient à introduire explicitement les faits critiques.

> Suite : [Exact Match](<64-Evaluation-Formule-Exact-Match.md>) — étape 64.
